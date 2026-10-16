"""F3: 2006–2010 seçim, 2011–2015 doğrulama; CRS ve düzgün zemin kontrolü."""
from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
import resource
import time

import numpy as np
import pandas as pd
from scipy.special import gammaln

from .arayuz import buyukluk_paylari, gecmis_dogrula, pencere_dogrula
from .dalga2 import (ORTAK_DIZINI, RAPOR_DIZINI, alici_paylari,
                     izgara_dogrula, skor_ozeti)
from .girdi import AYAR_SON, SON, fay_oku, k9_basamaklari
from .italya import crs_gunluk, sayim
from .ortak_taban import TopluOrtak
from knotenlinie.yollar import VERI

AYAR_BAS = pd.Timestamp('2006-01-01', tz='UTC')
ASIGMALAR = (30000., 100000., 300000.)
AGIRLIKLAR = (0., .1, .25, .5, 1.)
ESIKLER = (3.95, 4.95)


def adaylar():
    return ([dict(tur='ortak', agirlik=0.)]
            + [dict(tur='crs', asigma_pa=s, agirlik=w)
               for s in ASIGMALAR for w in AGIRLIKLAR]
            + [dict(tur='duzgun', agirlik=w) for w in AGIRLIKLAR])


def duzgun_arka_plan(izgara, arka_plan):
    """Hedef maskede eşit km² yoğunluğu; tabanın hedef arka plan bütçesi aynı.

    Kontrol λ=ETAS+w(U−B), U=sum(B)*alan/sum(alan). Tetikleme değişmez;
    toplam oranı ayarlayan ek bir μ yoktur. CRS ise bütçeyi değiştirebilir.
    """
    g = izgara_dogrula(izgara)
    b = np.asarray(arka_plan, float)
    if b.shape != (len(g),) or not np.isfinite(b).all() or (b < 0).any():
        raise ValueError('arka plan geçersiz')
    area = (np.deg2rad(g.boylam_max.to_numpy()-g.boylam_min.to_numpy())
            * (np.sin(np.deg2rad(g.enlem_max.to_numpy()))
               - np.sin(np.deg2rad(g.enlem_min.to_numpy()))))
    if (area <= 0).any() or not np.isfinite(area).all():
        raise ValueError('hücre alanı pozitif/sonlu olmalı')
    return b.sum()*area/area.sum()


def bolme_olc(toplu, katalog, faylar, baslangic, bitis, esikler, candidates,
              *, blok_gun=32, kaynak_hesabi=k9_basamaklari):
    """Tek bölmeyi seyrek hedef oranları + tam hücre integraliyle skorla.

    Bu yordam seçim yapmaz. Ayar bölmesinde 2011+ katalog satırı reddedilir;
    ayar tabanı sonu tahmin başlangıcına tam eşit olmalıdır.
    """
    a, z = pencere_dogrula(baslangic, bitis)
    if ((a, z) not in ((AYAR_BAS, AYAR_SON), (AYAR_SON, SON))
            or pd.Timestamp(toplu.taban.p['ayar_bitis']) != a):
        raise ValueError('bölme ile taban ayar sonu uyuşmuyor')
    if blok_gun < 1 or int(blok_gun) != blok_gun:
        raise ValueError('blok gün pozitif tamsayı olmalı')
    d = gecmis_dogrula(katalog, z)
    d = d[(d.zaman >= toplu.taban.baslangic) & (d.mw >= toplu.m0)].copy()
    g = izgara_dogrula(toplu.izgara)
    mag = buyukluk_paylari([*esikler, np.inf], toplu.m0, toplu.b)
    # Eşikler kümülatif M≥ satırlarıdır, ayrık büyüklük kutuları değil.
    mag = np.cumsum(mag[::-1])[::-1]
    background = np.asarray(toplu.arka_plan, float)
    uniform = duzgun_arka_plan(g, background)
    pay = alici_paylari(g, faylar)
    fault_background = background @ pay
    days = pd.date_range(a, z-pd.Timedelta(days=1), freq='D')
    ts, ds = kaynak_hesabi(d, faylar)
    ratios = {s: crs_gunluk(days, ts, ds, s, faylar.tau_dot_pa_gun.to_numpy())
              for s in sorted({c['asigma_pa'] for c in candidates
                               if c['tur'] == 'crs' and c['agirlik'] > 0})}
    for c in candidates:
        if (c['tur'] not in ('ortak', 'crs', 'duzgun')
                or not np.isfinite(c['agirlik']) or not 0 <= c['agirlik'] <= 1):
            raise ValueError('aday türü/ağırlığı geçersiz')
    out = {m: [dict(aday=dict(c), logL=0., beklenen_toplam=0., olay=[], N=0,
                    minimum_olay_orani=None) for c in candidates] for m in esikler}
    for start in range(0, len(days), blok_gun):
        block = days[start:start+blok_gun]
        e = np.asarray(toplu.gunluk(block), float)
        if (e.shape != (len(block), len(g)) or not np.isfinite(e).all()
                or (e < background[None, :]-1e-12).any()):
            raise ValueError('ortak ETAS bloğu geçersiz')
        base_sum = e.sum(axis=1)
        target = {}
        for m in esikler:
            n = sayim(d, g, block, m)
            di, ci = np.nonzero(n)
            target[m] = (di, ci, n[di, ci])
        for i, c in enumerate(candidates):
            w = c['agirlik']
            # Null bit düzeyinde tabanla aynı; eşitlik null lehine kalır.
            if c['tur'] == 'ortak' or w == 0:
                delta_sum = np.zeros(len(block))
            elif c['tur'] == 'crs':
                ri = ratios[c['asigma_pa']][start:start+len(block)]
                delta_sum = w*(ri @ fault_background-background.sum())
            else:
                delta_sum = np.zeros(len(block))  # U ve B'nin bütçesi aynı
            for mi, m in enumerate(esikler):
                di, ci, counts = target[m]
                rates = e[di, ci].copy()
                if w > 0 and c['tur'] == 'crs':
                    local_ratio = (ri[di]*pay[ci]).sum(axis=1)
                    rates += w*background[ci]*(local_ratio-1.)
                elif w > 0 and c['tur'] == 'duzgun':
                    rates += w*(uniform[ci]-background[ci])
                rates *= mag[mi]
                total = float((base_sum+delta_sum).sum()*mag[mi])
                if (rates <= 0).any() or not np.isfinite(rates).all() or total < 0:
                    raise ValueError('aday hedef oranı/toplamı geçersiz')
                r = out[m][i]
                r['logL'] += float((counts*np.log(rates)).sum()-total-gammaln(counts+1).sum())
                r['beklenen_toplam'] += total
                r['N'] += int(counts.sum())
                r['olay'].extend(np.repeat(rates, counts).tolist())
                if len(rates):
                    v = float(rates.min())
                    r['minimum_olay_orani'] = (v if r['minimum_olay_orani'] is None
                                               else min(v, r['minimum_olay_orani']))
    return out, dict(kaynak_zaman_sayisi=len(ts), alici_sayisi=len(faylar),
                     hucre_sayisi=len(g), Mc=toplu.m0, b=toplu.b,
                     taban_arka_plan_toplami=float(background.sum()),
                     duzgun_arka_plan_toplami=float(uniform.sum()))


def sec(ayar):
    """Yalnız M≥3.95 AYAR skorları; eşitlik ilk/null aday lehine."""
    selected = {}
    for kind in ('crs', 'duzgun'):
        rows = [r for r in ayar if r['aday']['tur'] == kind]
        if not rows or not all(np.isfinite(r['logL']) for r in rows):
            raise ValueError('ayar skorları eksik/geçersiz')
        selected[kind] = dict(max(rows, key=lambda r: r['logL'])['aday'])
    return selected


def karsilastir(candidate, baseline):
    r = skor_ozeti(candidate['olay'], baseline['olay'],
                   candidate['beklenen_toplam'], baseline['beklenen_toplam'])
    if r['N']:
        np.testing.assert_allclose(r['IG'], (candidate['logL']-baseline['logL'])/r['N'],
                                   atol=2e-11, rtol=2e-10)
    return r


def satirlar(validation, selected):
    rows = []
    for threshold, scores in validation.items():
        base, crs, control = scores
        against_base = karsilastir(crs, base)
        against_control = karsilastir(crs, control)
        control_ig = karsilastir(control, base)
        row = dict(aday='ETAS+CRS', bolge='italya', esik_mw=threshold,
                   rol='ana' if threshold == 3.95 else 'ek; aynı M≥3.95 seçimi',
                   durum='olculdu', dogrulama=[AYAR_SON.isoformat(), SON.isoformat()],
                   izgara='CSEP İtalya 0.1°', agirlik=selected['crs']['agirlik'],
                   asigma_pa=selected['crs']['asigma_pa'],
                   asigma_tanimlanabilir=selected['crs']['agirlik'] != 0,
                   beklenen_toplam=crs['beklenen_toplam'], beklenen_taban=base['beklenen_toplam'],
                   logL=crs['logL'], logL_taban=base['logL'],
                   ortak_tabana_karsi=against_base, duzgun_kontrole_karsi=against_control,
                   kontrol=dict(aday='ortak taban + düzgün zemin',
                                agirlik=selected['duzgun']['agirlik'],
                                beklenen_toplam=control['beklenen_toplam'], logL=control['logL'],
                                ortak_tabana_karsi=control_ig),
                   minimum_olay_orani=crs['minimum_olay_orani'])
        row.update(against_base)
        rows.append(row)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ortak', type=Path, default=ORTAK_DIZINI)
    parser.add_argument('--fay', type=Path, default=VERI / 'diss320/iss320.geojson')
    parser.add_argument('--blok-gun', type=int, default=32)
    args = parser.parse_args(argv)
    from knotenlinie.ortak_zemin.arayuz import ayar_tabani, omori_kutle
    from knotenlinie.ortak_zemin.veri import katalog_oku, sha256
    before = time.monotonic()
    catalog_path = args.ortak/'italya_katalog_le2015.csv'
    files = [catalog_path, args.ortak/'italya_izgara.csv',
             args.ortak/'etas_italya_le2005.json', args.ortak/'etas_italya_le2010.json', args.fay]
    inputs = [dict(yol=str(p), sha256=sha256(p)) for p in files]
    catalog_hash = inputs[0]['sha256']
    # Tam teslim kataloğu okunur; 2011+ satırları ayar yordamına taşınmaz.
    catalog = katalog_oku(catalog_path)
    training = catalog[catalog.zaman < AYAR_SON].copy()
    del catalog
    faults = fay_oku(args.fay)
    model = ayar_tabani('italya', args.ortak, son='2006-01-01')
    if model.p['katalog_sha256'] != catalog_hash:
        raise ValueError('ayar kataloğu SHA256 uyuşmuyor')
    batch = TopluOrtak(model, training, omori_kutle, ayar_son=AYAR_BAS)
    train, train_meta = bolme_olc(batch, training, faults, AYAR_BAS, AYAR_SON,
                                 (3.95,), adaylar(), blok_gun=args.blok_gun)
    selected = sec(train[3.95])
    scan = [{k: v for k, v in r.items() if k != 'olay'} for r in train[3.95]]
    training_seconds = time.monotonic()-before
    del batch, model, training, train
    gc.collect()
    # İkinci taban yalnız seçim dondurulduktan sonra hazırlanır.
    model = ayar_tabani('italya', args.ortak, son='2011-01-01')
    if model.p['katalog_sha256'] != catalog_hash:
        raise ValueError('doğrulama kataloğu SHA256 uyuşmuyor')
    catalog = katalog_oku(catalog_path)
    batch = TopluOrtak(model, catalog, omori_kutle)
    frozen = [dict(tur='ortak', agirlik=0.), selected['crs'], selected['duzgun']]
    validation, val_meta = bolme_olc(batch, catalog, faults, AYAR_SON, SON,
                                   ESIKLER, frozen, blok_gun=args.blok_gun)
    rows = satirlar(validation, selected)
    references = []
    for row in rows:
        name = ('dogrulama_italya_2011_2015_m3.95_inf.json' if row['esik_mw'] == 3.95
                else 'dogrulama_italya_2011_2015.json')
        path = args.ortak/name
        ref = json.loads(path.read_text())['ozet']
        # T teslim satırıyla ortak taban tam skor zincirini denetle.
        np.testing.assert_allclose(row['beklenen_taban'], ref['beklenen_toplam'], atol=2e-9, rtol=0)
        np.testing.assert_allclose(row['logL_taban'], ref['logL'], atol=2e-9, rtol=0)
        assert row['N'] == ref['N']
        references.append(dict(yol=str(path), sha256=sha256(path), durum='N/Λ/logL eşleşti'))
    # ru_maxrss birimi: macOS'ta bayt, Linux'ta KiB; aşağıda bayta çevrilir.
    import sys
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = int(rss if sys.platform == 'darwin' else rss*1024)
    result = dict(deney='F3', durum='olculdu', sonuclar=rows,
                  ayar=dict(baslangic=AYAR_BAS.isoformat(), son=AYAR_SON.isoformat(),
                            esik_mw=3.95, secili=selected, tarama=scan, **train_meta),
                  dogrulama_meta=val_meta, girdi=inputs, taban_esitlik_kontrolu=references,
                  duvar_saniye=time.monotonic()-before, ayar_saniye=training_seconds,
                  tepe_rss_byte=rss_bytes, blok_gun=args.blok_gun,
                  ortam=dict(python=sys.version.split()[0], pandas=pd.__version__,
                             numpy=np.__version__),
                  kod_sha256={str(p): sha256(p) for p in (
                      Path(__file__), Path(__file__).with_name('ortak_taban.py'),
                      Path(__file__).with_name('dalga2.py'), Path(__file__).with_name('italya.py'),
                      Path(__file__).with_name('girdi.py'),
                      Path('knotenlinie/ortak_zemin/arayuz.py'))},
                  kontrol_tanimi='λ=ETAS+w(U−B); U=sum(B)*hücre_km²/sum(hücre_km²); tetikleme sabit',
                  secim='2006 tabanı; yalnız 2006–2010 M≥3.95 Poisson argmax; iki satırda aynı seçim',
                  taban_durumu=model.p['durum'], ortak_dallanma=model.p['dallanma'],
                  ayar_dallanma=json.loads(files[2].read_text())['dallanma'],
                  bagimsiz_inceleme='F3 skor kodu bağımsız incelemesi bekliyor',
                  sinirlar=['maskeli MLE açık; ortak taban geçici',
                            'DISS 3.2.0 2015 vintage retrospektif',
                            'K9 yakın alan/fay merkezleri ve 1985 CRS dengesi değişmedi',
                            'T p: kümelenme bağımsızlığı ve sabit kompansatör koşullu tanısı',
                            'kör/yerleşik modele karşı geçme hükmü değil'])
    path = RAPOR_DIZINI/'OLCUM3.json'
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(json.dumps(dict(sonuclar=rows, ayar_secili=selected,
                         duvar_saniye=result['duvar_saniye'], tepe_rss_byte=rss_bytes),
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
