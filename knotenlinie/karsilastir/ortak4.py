"""H4: ortak ETAS / yerleşik modeller, yalnız 2011–2015 iç doğrulama."""
from __future__ import annotations

import argparse
from dataclasses import replace
import gc
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np
import pandas as pd

from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from .komut import CSEP_DOSYALAR, KESIK, cpti_prova, json_temiz
from .kosucu import Model, kos, karsilastir, katalog_kontrol, utc, KESIM
from .puan import PuanHatasi
from .tabanlar import csep_xml
from knotenlinie.yollar import KOK, KOSU, VERI as _VERI

TOHUM = 20261005
BAS = '2011-01-01T00:00:00Z'
SON = '2016-01-01T00:00:00Z'


def gecmis_ayari(model, bolge):
    if bolge != 'italya':
        raise PuanHatasi(f'gecmis_ayari: yalnız italya tanımlı, {bolge!r} değil')
    la0, la1, lo0, lo1 = model.kutu
    return dict(sinir=(lo0, lo1, la0, la1),
                baslangic_yil=model.p['baslangic_yili'],
                derinlik_max=70)


def gecmis_filtrele(katalog, ayar):
    k = katalog_kontrol(katalog)
    lo0, lo1, la0, la1 = ayar['sinir']
    return k[(k.zaman >= pd.Timestamp(f"{ayar['baslangic_yil']}-01-01", tz='UTC')) &
             (k.boylam >= lo0) & (k.boylam < lo1) &
             (k.enlem >= la0) & (k.enlem < la1) &
             (k.derinlik >= 0) & (k.derinlik <= ayar['derinlik_max'])].reset_index(drop=True)


class AyriGecmis:
    """Hedef okuyucusu ETAS ebeveynlerini değiştirmez; tam kaynak önce doğrulanır.

    kos'un hedef kataloğundan verdiği geçmiş yerine, donmuş ortak katalogdan
    kesin gün-başı kesimi alınır. Mc yalnız hesap bütçesi için erken uygulanır;
    ETAS zaten aynı Mc filtresini kendi içinde uygular.
    """
    def __init__(self, model, katalog, ayar):
        self.model = model
        k = gecmis_filtrele(katalog, ayar)
        self.k = k[k.mw >= model.mc].reset_index(drop=True)

    def beklenen(self, a, b, gecmis, izgara, m_kenarlar):
        a, b = utc(a), utc(b)
        if not a < b <= KESIM:
            raise PuanHatasi('AyriGecmis: kör pencere kapalı')
        stop = self.k.zaman.searchsorted(a, side='left')
        return self.model.beklenen(a, b, self.k.iloc[:stop].copy(), izgara, m_kenarlar)


def uzaklik_km(lat, lon, lat2, lon2):
    p, q = np.radians(lat), np.radians(np.asarray(lat2, float))
    dlon = np.radians(np.asarray(lon2, float) - lon)
    h = np.sin((q - p) / 2)**2 + np.cos(p) * np.cos(q) * np.sin(dlon / 2)**2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))


def kumelenme(hedef, katalog):
    """Hemen önceki M>=4.5 olay: (0,30] gün ve <=50 km, tam zamanla.

    Her okuyucu kendi bölgesel kaynak olaylarını kullanır: çapraz-katalog
    saniye farkları aynı depremi kendi ebeveyni yapamaz. Ek 'herhangi' maskesi
    son 30 gündeki herhangi bir M>=4.5 ebeveyn duyarlılığıdır, ana grup değildir.
    """
    hedef = katalog_kontrol(hedef)
    parents = katalog_kontrol(katalog)
    parents = parents[parents.mw >= 4.5].reset_index(drop=True)
    flags, any_flags, details = [], [], []
    for row in hedef.itertuples(index=False):
        stop = int(parents.zaman.searchsorted(row.zaman, side='left'))
        cluster, any_cluster, dt, distance, previous = False, False, None, None, None
        if stop:
            p = parents.iloc[stop - 1]
            previous = p.zaman.isoformat()
            dt = float((row.zaman - p.zaman) / pd.Timedelta(days=1))
            distance = float(uzaklik_km(row.enlem, row.boylam, p.enlem, p.boylam))
            cluster = dt <= 30 and distance <= 50
            start = parents.zaman.searchsorted(row.zaman - pd.Timedelta(days=30), side='left')
            window = parents.iloc[start:stop]
            any_cluster = bool((uzaklik_km(row.enlem, row.boylam,
                                           window.enlem, window.boylam) <= 50).any())
        flags.append(cluster)
        any_flags.append(any_cluster)
        details.append(dict(onceki_zaman=previous, gun_farki=dt, km_farki=distance))
    return np.array(flags, bool), np.array(any_flags, bool), details


def ayristir(aday, taban, katalog):
    flags, any_flags, details = kumelenme(aday.olaylar, katalog)
    with np.errstate(divide='ignore', invalid='ignore'):
        x = np.log(aday.olay_oranlari) - np.log(taban.olay_oranlari)
    def groups(mask):
        return {name: dict(N=int(use.sum()),
                           ortalama_log_oran=float(x[use].mean()) if use.any() else None,
                           log_oran_toplami=float(x[use].sum()))
                for name, use in [('kumelenme', mask), ('geri_kalan', ~mask)]}
    rows = []
    for i, (row, detail) in enumerate(zip(aday.olaylar.itertuples(index=False), details)):
        rows.append(dict(zaman=row.zaman.isoformat(), enlem=row.enlem, boylam=row.boylam,
                         derinlik=row.derinlik, mw=row.mw,
                         lambda_taban=float(aday.olay_oranlari[i]),
                         lambda_yerlesik=float(taban.olay_oranlari[i]),
                         log_oran=float(x[i]), kumelenme=bool(flags[i]), **detail))
    return dict(gruplar=groups(flags), herhangi_onceki_duyarliligi=groups(any_flags), olaylar=rows)


def olcekle(kosu, carpan):
    """Tek sabit oran çarpanı: olay ve integral terimleri birlikte değişir."""
    if not np.isfinite(carpan) or carpan <= 0:
        raise PuanHatasi('Tanı ölçeği pozitif/sonlu olmalı')
    N, lam = len(kosu.olaylar), float(kosu.beklenen.sum())
    return replace(kosu, ad=kosu.ad + '-GR-tani', beklenen=kosu.beklenen * carpan,
                   olay_oranlari=kosu.olay_oranlari * carpan,
                   logL=kosu.logL + N * np.log(carpan) + (1 - carpan) * lam)


def cpti_kume_katalog():
    # 2010 başlangıcı ilk hedefin 30 günlük ön-geçmişini fazlasıyla kapsar.
    p = pd.read_csv(KESIK / 'CPTI15_v4.0_le2015.csv')
    if p.Year.isna().any() or (p.Year >= 2016).any():
        raise PuanHatasi('CPTI küme kaynağı zaman kapısını geçmedi')
    p = p[(p.Year >= 2010) & (p.MwDef >= 4.5)].copy()
    z = pd.to_datetime(dict(year=p.Year, month=p.Mo, day=p.Da,
                            hour=p.Ho, minute=p.Mi, second=p.Se), utc=True)
    return katalog_kontrol(pd.DataFrame(dict(zaman=z, enlem=p.LatDef, boylam=p.LonDef,
                                            derinlik=p.DepDef.fillna(p.DepIns), mw=p.MwDef)))


def rss_byte():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)


def olc(bolge, hedef_adi, hedef, katalog, model, yerlesikler, grid, edges,
        *, kume_katalog, tekrar=10000):
    started = time.monotonic()
    ayar = gecmis_ayari(model, bolge)
    wrapper = AyriGecmis(model, katalog, ayar)
    models = [Model('ortak-ETAS', wrapper.beklenen, zamana_bagli=True, gecmis_ayarlari=ayar)]
    models += [Model(ad, x.beklenen) for ad, x in yerlesikler.items()]
    depth = (0, 30)
    runs = kos(models, BAS, SON, hedef, grid, edges, bolge=bolge, derinlik=depth)
    base = runs['ortak-ETAS']
    nsm = base.tutarlilik(tekrar=tekrar, tohum=TOHUM)
    pairs = {}
    for name in yerlesikler:
        pairs[name] = dict(**karsilastir(base, runs[name]),
                           ayristirma=ayristir(base, runs[name], kume_katalog))
    result = dict(bolge=bolge, hedef_katalog=hedef_adi, N=len(base.olaylar),
                  Lambda=float(base.beklenen.sum()), Lambda_bolu_N=float(base.beklenen.sum()) / len(base.olaylar),
                  tutarlilik=nsm, gecmis_ayarlari=ayar, gecmis_kaynak='ortak ' + bolge + ' katalog; <gün başı',
                  hucre=len(grid), m_kenarlar=[float(x) if np.isfinite(x) else '+inf' for x in edges], derinlik=depth,
                  yerlesik_metadata={ad: x.metadata for ad, x in yerlesikler.items()}, ciftler=pairs)
    # Bu oran ≤2010 model ayar kaydından gelir; doğrulama N'si kullanılmaz.
    share = next(x for x in model.p['gr_ayar_paylari'] if x['m_alt'] == 4.95)
    scale = share['gozlenen_pay'] / share['gr_pay']
    diagnostic = olcekle(base, scale)
    dpairs = {}
    for name in yerlesikler:
        d = karsilastir(diagnostic, runs[name])
        d.update(GR_fazlalik_maliyeti_IG=d['IG'] - pairs[name]['IG'],
                 olay_terimi_degisim=float(np.log(scale)),
                 integral_terimi_degisim=float((1 - scale) * base.beklenen.sum() / len(base.olaylar)))
        dpairs[name] = d
    result['GR_tani'] = dict(secimde_kullanilmaz=True, ayar_paylari=share, carpan=scale,
                             Lambda=float(diagnostic.beklenen.sum()),
                             Lambda_bolu_N=float(diagnostic.beklenen.sum()) / len(base.olaylar),
                             maliyet_isareti='pozitif: fazlalık IG maliyeti; negatif: fazlalık bu pencerede avantaj',
                             tutarlilik=diagnostic.tutarlilik(tekrar=tekrar, tohum=TOHUM), ciftler=dpairs)
    result.update(duvar_saniye=time.monotonic() - started, rss_tepe_byte=rss_byte())
    print(f'{bolge}/{hedef_adi}: N={result["N"]}, Lambda={result["Lambda"]:.6f}, '
          f'{result["duvar_saniye"]:.1f}s, RSS={rss_byte()/1e9:.3f}GB', flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--taban-dizin', type=Path, default=_VERI / 'tabanlar')
    ap.add_argument('--cikti', type=Path, default=KOSU / 'H/OLCUM4.json')
    args = ap.parse_args()
    started = time.monotonic()
    ortak = VERI / 'ortak'
    italy = ayar_tabani('italya', son='2011-01-01')
    cat = katalog_oku(ortak / 'italya_katalog_le2015.csv')
    if sha256(ortak / 'italya_katalog_le2015.csv') != italy.p['katalog_sha256']:
        raise PuanHatasi('İtalya katalog SHA uyuşmuyor')
    statics = {ad: csep_xml(args.taban_dizin / f, sure_yil=10) for ad, f in CSEP_DOSYALAR.items()}
    ref = statics['HAZFX-BPT']
    rows = [olc('italya', 'CPTI15-prova (ana)', cpti_prova(KESIK / 'CPTI15_v4.0_le2015.csv'),
                cat, italy, statics, ref.izgara, ref.m_kenarlar, kume_katalog=cpti_kume_katalog())]
    del italy
    gc.collect()
    italy = ayar_tabani('italya', son='2011-01-01')
    rows.append(olc('italya', 'HORUS-ortak (ek)', cat, cat, italy, statics, ref.izgara,
                    ref.m_kenarlar, kume_katalog=gecmis_filtrele(cat, gecmis_ayari(italy, 'italya'))))
    del italy, cat, statics, ref
    gc.collect()
    sources = [KESIK / 'CPTI15_v4.0_le2015.csv']
    sources += [args.taban_dizin / f for f in CSEP_DOSYALAR.values()]
    sources += [ortak / f'italya_{suffix}' for suffix in ('katalog_le2015.csv', 'izgara.csv')]
    sources += [ortak / 'etas_italya_le2010.json']
    codes = ['knotenlinie/karsilastir/ortak4.py', 'knotenlinie/karsilastir/kosucu.py',
             'knotenlinie/karsilastir/puan.py', 'knotenlinie/karsilastir/tabanlar.py',
             'knotenlinie/ortak_zemin/arayuz.py']
    out = dict(durum='PROVISIONAL; 2011–2015 iç doğrulama, kör hüküm/aday seçimi değil',
               baslangic=BAS, bitis_haric=SON, tekrar=10000, tohum=TOHUM,
               M_tohum=TOHUM + 1,
               italya_M_notu='Prova ile birebir: 41 nominal 4.95–9.05 kutu; XML lastMagBinOpen=1 '
                              'nedeniyle son kutu [8.95,+inf). Sonlu 9.05 uyarlaması icat edilmedi.',
               kumelenme_tanimi='Aynı okuyucunun bölgesel M>=4.5 hemen önceki olayı; '
                                'kesin zaman <hedef, <=30 gün ve <=50 km. '
                                'CPTI küme geçmişi >=2010, HORUS kendi taban geçmiş kutu/derinliği. '
                                'Herhangi önceki olay ek duyarlılık olarak saklandı.',
               IG_tanimi='ortalama log-oran - (Lambda_taban-Lambda_yerlesik)/N; '
                         'integral_terimi bu farkın eksi işaretli katkısıdır',
               NSM_notu='N analitik iki Poisson kuyruğu; S/M 10000 sabit-N multinomial. '
                        'Günlük geçmişe bağlı tabanda operasyonel tanı; koşulsuz ETAS testi değil.',
               p_notu='Ham iki yönlü T/W; kümelenme altında bağımsızlık varsayımı. '
                      'Holm/önkayıt kabul hükmü veya GEAR1 üstünlüğü değil.',
               satirlar=rows, kaynak_SHA256={str(p): sha256(p) for p in sources},
               kod_SHA256={p: sha256(KOK / p) for p in codes},
               kaynak_fisi='records/H/TABANLAR.json; ortak/README.md',
               duvar_saniye=time.monotonic() - started, rss_tepe_byte=rss_byte(),
               python=sys.version, numpy=np.__version__, pandas=pd.__version__)
    args.cikti.write_text(json.dumps(json_temiz(out), ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(args.cikti, flush=True)


if __name__ == '__main__':
    main()
