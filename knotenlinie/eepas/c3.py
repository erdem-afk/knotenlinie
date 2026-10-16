"""C3: 2006–2010 ayar bölmesi, donmuş 2011–2015 doğrulama.

python -m knotenlinie.eepas.c3 (çıktılar yalnız $KNOTENLINIE_RUNS/C/; yeni veri indirmez; yalnız İtalya).
"""
from __future__ import annotations

import argparse
import gc
import json
import re
import resource
import signal
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.ayar import b_ayarla
from .c2 import C, ORTAK, sha256, yaz
from .katalog import kesik_oku
from .model import Parametreler, ArkaPlan, EEPAS
from .ortak import (Alan, GecmisFiltresi, EEPASOnhesap, tamlik_sec,
                    eepas_ayarla_ortak, gunluk_puan, utc, GUN, AYAR_SONU, KESIM)
from .janus import agirlik_ayarla, bilgi_kazanci

BOLME = utc('2006-01-01')


def teslim_dogrula(ortak=ORTAK):
    """README'deki güncel hashlar sabittir; dosyanın kendi hash'i kanıt sayılmaz."""
    ortak = Path(ortak)
    text = (ortak/'README.md').read_text(encoding='utf-8')
    manifest = dict(re.findall(r'\| `([^`]+)` \| `([0-9a-f]{64})` \|', text))
    files = ['kataloglar.json']
    for region in ('italya',):
        files += [f'{region}_katalog_le2015.csv', f'{region}_izgara.csv',
                  f'etas_{region}_le2005.json', f'etas_{region}_le2010.json']
    hashes = {}
    meta = json.loads((ortak/'kataloglar.json').read_text(encoding='utf-8'))
    for name in files:
        actual = sha256(ortak/name)
        if manifest.get(name) != actual:
            raise ValueError(f'Güncel ortak README SHA256 uyuşmuyor: {name}')
        hashes[name] = actual
    from knotenlinie.etas import model as etas_code
    for region in ('italya',):
        for year in (2005, 2010):
            cfg = json.loads((ortak/f'etas_{region}_le{year}.json').read_text(encoding='utf-8'))
            if (utc(cfg['ayar_bitis']) != utc(f'{year+1}-01-01') or
                    utc(cfg['ayar_max_zaman']) >= utc(cfg['ayar_bitis']) or
                    not cfg['basari'] or not 0 <= cfg['dallanma'] < 1):
                raise ValueError('Yakınsamış, doğru sonda alt-kritik T tabanı gerekli')
            if cfg['kod_sha256']['knotenlinie/etas/model.py'] != sha256(etas_code.__file__):
                raise ValueError('T ETAS çekirdeği değişmiş')
            for key, name in [('katalog_sha256', f'{region}_katalog_le2015.csv'),
                              ('izgara_sha256', f'{region}_izgara.csv')]:
                if cfg[key] != hashes[name] or meta[region][key] != hashes[name]:
                    raise ValueError('T model/katalog/ızgara bağı uyuşmuyor')
    return hashes


def alan_yap(grid, region, threshold=None):
    if region != 'italya':
        raise ValueError(f'C3: yalnız italya tanımlı, {region!r} değil')
    lower = 3.95 if threshold is None else threshold
    edges = np.round(np.arange(lower, 9.051, .1), 8)
    return Alan(grid, edges, hedef_alt=lower)


def hedefler(df, alan, baslangic, bitis):
    d = df.loc[(df.zaman >= utc(baslangic)) & (df.zaman < utc(bitis))]
    ci = alan.indeks(d)
    mi = np.searchsorted(alan.m_kenarlar, d.mw.to_numpy(float), side='right')-1
    ok = (ci >= 0) & (mi >= 0) & (mi < len(alan.m_kenarlar)-1)
    return d.loc[ok].reset_index(drop=True), ci[ok], mi[ok]


def onhesap(model, df, alan, a, b):
    # Kalıcı N_hedef × N_öncü ve blok geçicilerini allocation'dan önce sınırla.
    n = len(hedefler(df, alan, a, b)[0])
    parents = int(((df.zaman < utc(b)) & (df.mw >= model.p.m0)).sum())
    estimate = 8*n*parents + 8*parents + 64*parents*8*6 + 128*256*8*4
    if estimate > 1024**3:
        raise MemoryError('EEPAS önhesabı >1 GiB; tam koşu hesap sunucusunda yapılmalı')
    return EEPASOnhesap(model, df, alan, a, b)


def duzgun_puan(df, alan, a, b, m0, b_deger, hiz=None):
    """Sabit düzgün uzay + GR; tek hız ölçeği aynı ayar hedeflerinde profil MLE.

    Kutudaki kütle bir, gerçek maskeye kesilir. Hız ve b doğrulamada değişmez.
    """
    targets, ci, mi = hedefler(df, alan, a, b)
    e = alan.m_kenarlar
    mag = 10**(-b_deger*(e[:-1]-m0))-10**(-b_deger*(e[1:]-m0))
    mass = ArkaPlan(alan.kutu).kutle(alan.izgara)[:, None]*mag
    unit_total = float((utc(b)-utc(a))/GUN)*float(mass.sum())
    if hiz is None:
        if utc(b) > AYAR_SONU or not len(targets):
            raise ValueError('Düzgün hız yalnız <=2010 ve dolu ayardan seçilir')
        hiz = len(targets)/unit_total
    if not np.isfinite(hiz) or hiz <= 0:
        raise ValueError('Pozitif sonlu donmuş düzgün hız gerekli')
    return hiz*mass[ci, mi], hiz*unit_total, float(hiz)


def karistir(e, t, ei, ti, w):
    return w*e+(1-w)*t, float(w*ei+(1-w)*ti)


def sec(e, t, ei, ti, baslangic, bitis):
    if utc(baslangic) != BOLME or utc(bitis) != AYAR_SONU:
        raise ValueError('Ağırlık yalnız 2006–2010 bölmesinde seçilir')
    r = agirlik_ayarla(e, t, ei, ti)
    r.update(baslangic=BOLME.isoformat(), bitis_haric=AYAR_SONU.isoformat(), N=len(t))
    return r


def ayarla(region, ortak, maksiter):
    print(f'{region}: ayar 2006–2010', flush=True)
    et = ayar_tabani(region, ortak, son='2006-01-01')
    alan = alan_yap(et.izgara, region)
    filt = GecmisFiltresi(et.p['ayar_baslangic'], 0., 70.)
    df = filt.uygula(kesik_oku(ortak/f'{region}_katalog_le2015.csv'), alan)
    # Bileşen şeklinin temel girdileri de holdout öncesi; PPE ayar hedeflerini içermez.
    warm = df.loc[df.zaman < BOLME]
    m0, comp = tamlik_sec(warm, filt.baslangic, region, son=BOLME,
                          hedef_alt=alan.m_kenarlar[0])
    shape_start = utc('1995-01-01')
    parents = warm.loc[(warm.zaman >= shape_start) & (warm.mw >= m0)]
    if len(parents) < 100:
        raise ValueError('EEPAS b/r0 için <100 öncü')
    br = b_ayarla(parents.mw.to_numpy(float), m0)
    p = Parametreler(m0=m0, b=br['deger'], r0=len(parents)/float((BOLME-shape_start)/GUN))
    # Sabit 25 km/%5 PPE; yalnız <=2005 hedef merkezleri.
    centers = warm.loc[warm.mw >= alan.m_kenarlar[0]]
    bg = ArkaPlan(alan.kutu, centers, bant=25., duzgun_pay=.05)
    train = df.loc[df.zaman < AYAR_SONU]
    pre = onhesap(EEPAS(p, alan.kutu, bg), train, alan, BOLME, AYAR_SONU)
    q, er = eepas_ayarla_ortak(pre, maksiter=maksiter, ppe_alt=.05)
    if not er['basari']:
        raise RuntimeError(f'EEPAS yakınsamadı: {er}')
    elam, ei = pre.puan(q)
    tlam, ti = gunluk_puan(et.beklenen, train.loc[train.mw >= et.mc], alan, BOLME, AYAR_SONU)
    targets, _, _ = hedefler(train, alan, BOLME, AYAR_SONU)
    if not pre.targets.equals(targets) or len(tlam) != len(targets):
        raise ValueError('EEPAS/ETAS hedef sırası uyuşmuyor')
    ulam, ui, rate = duzgun_puan(train, alan, BOLME, AYAR_SONU, q.m0, q.b)
    janus = sec(elam, tlam, ei, ti, BOLME, AYAR_SONU)
    control = sec(ulam, tlam, ui, ti, BOLME, AYAR_SONU)
    cfg = {'bolge': region, 'hazir': True, 'ayar_baslangic': BOLME.isoformat(),
           'ayar_bitis': AYAR_SONU.isoformat(), 'secim_m_alt': float(alan.m_kenarlar[0]),
           'm_kenarlar': alan.m_kenarlar.tolist(), 'gecmis_filtresi': asdict(filt),
           'tamlik': comp, 'b': br, 'b_r0_baslangic': shape_start.isoformat(),
           'sekil_girdi_bitis_haric': BOLME.isoformat(), 'eepas': er,
           'ppe_merkezler': bg.merkezler.to_numpy().tolist(), 'ppe_bant': bg.bant,
           'ppe_duzgun_pay': bg.duzgun_pay, 'janus': janus,
           'duzgun_kontrol': dict(control, hiz=rate, b=q.b, m0=q.m0),
           'ayar_ozet': {'N': len(tlam), 'EEPAS_toplam': ei, 'ETAS_toplam': ti,
                         'duzgun_toplam': ui, 'oncu_n_b_r0': len(parents),
                         'olay_beklenen': {'EEPAS': elam.tolist(), 'ETAS': tlam.tolist(),
                                          'duzgun': ulam.tolist()}},
           'etas_ayar_dosyasi': str(ortak/f'etas_{region}_le2005.json'),
           'etas_dogrulama_dosyasi': str(ortak/f'etas_{region}_le2010.json')}
    return cfg


def satir(ad, region, threshold, lam, total, tlam, ti, clam, ci, w, uw, factorial):
    r = bilgi_kazanci(lam, tlam, total, ti)
    cr = bilgi_kazanci(lam, clam, total, ci)
    return {'aday': ad, 'bolge': region, 'm_alt': threshold, 'N': r['n'],
            'IG': r['ig'], 'SE': r['se'], 'p': r['p'], 'aralik95': r['aralik95'],
            'beklenen_toplam': total, 'taban_beklenen_toplam': ti,
            'taban': 'ortak ETAS (son=2011)', 'birim': 'nat/olay',
            'agirlik': w, 'kontrol_agirlik': uw, 'kontrol_beklenen_toplam': ci,
            'kontrole_karsi': {'taban': 'ortak taban + düzgün zemin',
                               'IG': cr['ig'], 'SE': cr['se'], 'p': cr['p'],
                               'aralik95': cr['aralik95']},
            'logL': float(np.log(lam).sum()-total-factorial)}


def dogrula(cfg, ortak):
    region = cfg['bolge']
    print(f'{region}: donmuş doğrulama 2011–2015', flush=True)
    et = ayar_tabani(region, ortak, son='2011-01-01')
    alan = alan_yap(et.izgara, region)
    filt = GecmisFiltresi(**cfg['gecmis_filtresi'])
    df = filt.uygula(kesik_oku(ortak/f'{region}_katalog_le2015.csv'), alan)
    q = Parametreler(**cfg['eepas']['parametreler'])
    bg = ArkaPlan(alan.kutu, pd.DataFrame(cfg['ppe_merkezler'], columns=['boylam', 'enlem']),
                  cfg['ppe_bant'], cfg['ppe_duzgun_pay'])
    pre = onhesap(EEPAS(q, alan.kutu, bg), df, alan, AYAR_SONU, KESIM)
    elam, ei = pre.puan(q)
    tlam, ti = gunluk_puan(et.beklenen, df.loc[df.mw >= et.mc], alan, AYAR_SONU, KESIM)
    targets, _, _ = hedefler(df, alan, AYAR_SONU, KESIM)
    if not pre.targets.equals(targets) or len(tlam) != len(targets):
        raise ValueError('Doğrulama hedef sırası uyuşmuyor')
    ulam, ui, _ = duzgun_puan(df, alan, AYAR_SONU, KESIM, q.m0, q.b,
                             cfg['duzgun_kontrol']['hiz'])
    w, uw = cfg['janus']['agirlik'], cfg['duzgun_kontrol']['agirlik']
    jlam, ji = karistir(elam, tlam, ei, ti, w)
    clam, ci = karistir(ulam, tlam, ui, ti, uw)
    rows = []
    totals = {'EEPAS-C3': ei, 'ortak ETAS': ti, 'Janus-C3': ji,
              'ortak taban + düzgün zemin': ci}
    lambdas = {'EEPAS-C3': elam, 'ortak ETAS': tlam, 'Janus-C3': jlam,
               'ortak taban + düzgün zemin': clam}
    for threshold in (3.95, 4.95):
        if threshold == cfg['secim_m_alt']:
            mask = np.ones(len(targets), bool)
            tt = totals
        else:
            # İtalya ek satırı: aynı w/parametre; asla ikinci eşikte yeniden ayar yok.
            high = alan_yap(et.izgara, region, threshold)
            highpre = onhesap(EEPAS(q, alan.kutu, bg), df, high, AYAR_SONU, KESIM)
            helam, hei = highpre.puan(q)
            htlam, hti = gunluk_puan(et.beklenen, df.loc[df.mw >= et.mc], high, AYAR_SONU, KESIM)
            hulam, hui, _ = duzgun_puan(df, high, AYAR_SONU, KESIM, q.m0, q.b,
                                      cfg['duzgun_kontrol']['hiz'])
            mask = targets.mw.to_numpy() >= threshold
            for lo, hi in ((elam, helam), (tlam, htlam), (ulam, hulam)):
                np.testing.assert_allclose(lo[mask], hi, rtol=1e-12)
            tt = {'EEPAS-C3': hei, 'ortak ETAS': hti,
                  'Janus-C3': w*hei+(1-w)*hti,
                  'ortak taban + düzgün zemin': uw*hui+(1-uw)*hti}
        bins = np.column_stack([pre.days[mask], pre.ci[mask], pre.mi[mask]])
        _, counts = np.unique(bins, axis=0, return_counts=True)
        factorial = float(gammaln(counts+1).sum())
        for name, weight in [('Janus-C3', w), ('ortak taban + düzgün zemin', uw),
                             ('EEPAS-C3', 1.), ('ortak ETAS', 0.)]:
            row = satir(name, region, threshold, lambdas[name][mask], tt[name],
                        tlam[mask], tt['ortak ETAS'], clam[mask],
                        tt['ortak taban + düzgün zemin'], weight, uw, factorial)
            row.update(secim_m_alt=cfg['secim_m_alt'], m_ust_haric=float(alan.m_kenarlar[-1]),
                       m_kutu_adim=.1,
                       oncu_m0=q.m0, hedef_oncu_farki=threshold-q.m0,
                       aday_kapisi=threshold-q.m0 >= 1.5 and name == 'Janus-C3')
            rows.append(row)
    return {'bolge': region, 'durum': 'olculdu', 'satirlar': rows,
            'ayar': cfg, 'olay_beklenen': {k: v.tolist() for k, v in lambdas.items()},
            'olaylar': targets.assign(zaman=targets.zaman.astype(str)).to_dict('records')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ortak', type=Path, default=ORTAK)
    parser.add_argument('--maksiter', type=int, default=200)
    args = parser.parse_args()
    start = time.monotonic()
    def deadline(*_):
        raise TimeoutError('55 dakika hesap bütçesi doldu; arka plan süreci yok')
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(55*60)
    hashes = teslim_dogrula(args.ortak)
    fits = []
    for region in ('italya',):
        cfg = ayarla(region, args.ortak, args.maksiter)
        yaz(C/f'ayar3-{region}.json', cfg)
        fits.append(cfg)
        gc.collect()
    # Bütün seçimler doğrulamadan ÖNCE diske donduruldu.
    selection_hashes = {cfg['bolge']: sha256(C/f"ayar3-{cfg['bolge']}.json") for cfg in fits}
    scores = []
    for cfg in fits:
        scores.append(dogrula(cfg, args.ortak))
        gc.collect()
    if teslim_dogrula(args.ortak) != hashes:
        raise ValueError('Ortak teslim koşu sırasında değişti')
    for region, checksum in selection_hashes.items():
        if sha256(C/f'ayar3-{region}.json') != checksum:
            raise ValueError('Doğrulamada ayar değişti')
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_bytes = int(rss if sys.platform == 'darwin' else rss*1024)
    out = {'deney': 'C3', 'durum': 'olculdu', 'baslangic': AYAR_SONU.isoformat(),
           'bitis_haric': KESIM.isoformat(), 'bolgeler': scores,
           'ortak_sha256': hashes, 'secim_sha256': selection_hashes,
           'kosu': {'saniye': time.monotonic()-start, 'tepe_rss_byte': rss_bytes,
                    'python': sys.version, 'pandas': pd.__version__, 'numpy': np.__version__,
                    'kucultme': False},
           'kod_sha256': {str(p): sha256(p) for root in ('knotenlinie/eepas', 'knotenlinie/ortak_zemin')
                          for p in sorted(Path(root).glob('*.py'))},
           'bagimsiz_inceleme': 'C3 değişiklikleri bekliyor; C2 kabulü bunları kapsamaz',
           'sinirlar': ['Ortak taban maskeli MLE değil',
                        'EEPAS NZ şekilleri sabit, yalnız 1 gün ufuk',
                        'Bileşen b/r0/Mc/PPE <=2005; mu/aT/ölçek/w 2006–2010',
                        'İtalya ek M>=4.95 aynı M>=3.95 seçiminin aktarımı',
                        'Bütün skorlar sonlu C2 büyüklük kutularında yeniden hesaplandı']}
    yaz(C/'OLCUM3.json', out)
    signal.alarm(0)
    print(json.dumps({'kosu': out['kosu'], 'satirlar': [r for s in scores for r in s['satirlar']
                     if r['aday'] in ('Janus-C3', 'ortak taban + düzgün zemin')]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
