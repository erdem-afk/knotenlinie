"""Kaliforniya SCSN 2011–2020: D1 − D0 (deney Y defteri); gün sütunları Lam_hedef (M≥2,8), Lam_hedef1 (M≥2,9)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.puan import PuanHatasi
from knotenlinie.skor_defteri.defter import KOK

from .satir import kazanc_satiri, n_testleri

Y = KOK / 'Y'
ESIK = {2.8: 'Lam_hedef', 2.9: 'Lam_hedef1'}


def oku(ad, bolge='scsn', donem='2011-2020', dizin=Y):
    o = pd.read_csv(dizin / f'{ad}__{bolge}__{donem}__olay.csv.gz')
    g = pd.read_csv(dizin / f'{ad}__{bolge}__{donem}__gun.csv.gz')
    o['zaman'] = pd.to_datetime(o['zaman'], utc=True, format='mixed')
    if (o['zaman'] >= pd.Timestamp('2021-01-01', tz='UTC')).any():
        raise PuanHatasi('Mühür: 2021+ olay')
    if not (o['lam'] > 0).all():
        raise PuanHatasi('Gözlemli sıfır oran')
    return o, g


def kazanc(oa, ga, ot, gt, alt):
    kol = ESIK[alt]
    if not (oa[['zaman', 'hucre', 'kutu']].equals(ot[['zaman', 'hucre', 'kutu']]) and ga['gun'].equals(gt['gun'])):
        raise PuanHatasi('Defterler aynı hedef dizisini taşımıyor')
    mask = (oa['mw'].to_numpy(float) >= alt - 1e-9)
    gunler = [pd.Timestamp(x) for x in ga['gun'].astype(str)]
    idx = oa.loc[mask, 'gun'].astype(str).map({g: i for i, g in enumerate(ga['gun'].astype(str))}).to_numpy(int)
    la, lt = oa['lam'].to_numpy(float)[mask], ot['lam'].to_numpy(float)[mask]
    oran = np.log(la) - np.log(lt)
    La, Lt = ga[kol].to_numpy(float), gt[kol].to_numpy(float)
    D = np.bincount(idx, weights=oran, minlength=len(gunler)) - (La - Lt)
    n = np.bincount(idx, minlength=len(gunler))
    N = int(mask.sum())
    k = dict(D=D, n=n.astype(int), gunler=gunler, N=N, Lambda_aday=float(La.sum()), Lambda_taban=float(Lt.sum()),
             IG=float(D.sum() / N), IG_olay=float(oran.mean()), integral=float(-(La.sum() - Lt.sum()) / N))
    return k, la, lt


def olc():
    oa, ga = oku('D1')
    ot, gt = oku('D0')
    satirlar = []
    for alt in ESIK:
        k, la, lt = kazanc(oa, ga, ot, gt, alt)
        r = kazanc_satiri(k, la, lt, None, None)
        r.update(satir='D1 - D0', aday='D1', taban='D0', esik=alt, bolge='scsn', donem='2011-2020')
        r['tutarlilik_aday'] = n_testleri(k['Lambda_aday'], k['N'], None)
        r['tutarlilik_taban'] = n_testleri(k['Lambda_taban'], k['N'], None)
        r['not_'] = 'NBD yok (SCSN ≤2010 dönem Mc sabit değil); S/M/ikili S-L yok (defterde marjinal yok)'
        satirlar.append(r)
    return dict(satirlar=satirlar)
