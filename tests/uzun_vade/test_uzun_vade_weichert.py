"""Weichert (1980) ve Stepp (1972) sentetik testleri.

Weichert kestiricisi bilinen bir sentetik katalogda b'yi ve M>=4.95 oranını geri
kazanmalıdır. Katalog, farklı tamlık dönemlerinden (eşit olmayan süre ve Mc)
üretilir; olaylar kesik GR'den çekilip 0,1 ızgarasına yuvarlanır. Etkin süre,
dönem ataması ve tablo sıkılaştırma da sınanır.
"""
from __future__ import annotations

import numpy as np
import pytest

from knotenlinie.uzun_vade.weichert import (CPTI_TAMLIK, WeichertHatasi, etkin_sure,
                                      gk74_mask, mc_ata, sikilastir, stepp_tamlik,
                                      weichert_mle)


def _sentetik(tohum=20261005, b=1.0, A0=40.0, m1=4.0, n=40000):
    tablo = [(0, 100, 5.0), (100, 200, 4.5), (200, 300, 4.0)]
    rng = np.random.default_rng(tohum)
    kenar = np.r_[np.round(np.arange(4.0, 8.0, 0.1), 2), np.inf]
    yil, mw = [], []
    for a, bnd, mc in tablo:
        T = bnd - a
        lam = A0 * 10.0 ** (-b * (mc - m1)) * T
        nn = rng.poisson(lam)
        # Kesik GR: m = mc + Exp(beta) ; beta = b ln10
        e = rng.exponential(1.0 / (b * np.log(10.0)), size=nn)
        m = mc + e
        m = np.round(np.floor(m / 0.1) * 0.1, 2)
        yil.append(rng.uniform(a, bnd, size=nn))
        mw.append(m)
    return tablo, kenar, np.concatenate(yil), np.concatenate(mw)


def _oran_mref(A, b, m1, mref=4.95):
    return A * 10.0 ** (-b * (mref - m1))


def test_weichert_b_ve_oran_geri_kazanir():
    tablo, kenar, yil, mw = _sentetik()
    r = weichert_mle(mw, yil, tablo, kenarlar=kenar, bas=0, son=299)
    assert abs(r['b'] - 1.0) < 0.05
    dogru = _oran_mref(40.0, 1.0, 4.0)
    assert abs(r['oran_mref'] - dogru) / dogru < 0.05


def test_weichert_farkli_siddet_egrisi():
    tablo, kenar, yil, mw = _sentetik(tohum=7, b=0.8, A0=60.0)
    r = weichert_mle(mw, yil, tablo, kenarlar=kenar, bas=0, son=299)
    assert abs(r['b'] - 0.8) < 0.05
    dogru = _oran_mref(60.0, 0.8, 4.0)
    assert abs(r['oran_mref'] - dogru) / dogru < 0.07


def test_tablo_sikilastirma_ve_etkin_sure():
    t = sikilastir(CPTI_TAMLIK)
    assert all(m == pytest.approx(w + 0.5) for (_, _, m), (_, _, w) in zip(t, CPTI_TAMLIK))
    k = np.array([4.0, 4.5, 5.0, 5.5, np.inf], float)
    T = etkin_sure([(0, 10, 5.0), (10, 20, 4.5)], k, bas=0, son=19)
    # 5.0 kutusu (alt kenar 5.0): iki dönem de Mc<=5.0, 10+10 yıl.
    assert T[2] == pytest.approx(20.0)
    # 4.5 kutusu: yalnız Mc=4.5 dönemi (10 yıl); Mc=5.0 dönemi dışarıda.
    assert T[1] == pytest.approx(10.0)
    # 4.0 kutusu: hiçbir dönem Mc<=4.0 yok.
    assert T[0] == pytest.approx(0.0)


def test_mc_ata_donem_disi_nan():
    tablo = [(1900, 1950, 6.0), (1950, 2000, 5.0)]
    mc = mc_ata(tablo, np.array([1899.0, 1925.0, 1975.0, 2001.0]))
    assert np.isnan(mc[0]) and np.isnan(mc[3])
    assert mc[1] == 6.0 and mc[2] == 5.0


def test_stepp_sabit_hizli_katalog():
    rng = np.random.default_rng(11)
    yil = rng.uniform(1900, 2005, size=500)
    yil = np.concatenate([yil, rng.uniform(1600, 1900, size=40)])
    mw = np.full(yil.shape, 5.0)
    tab = stepp_tamlik(yil, mw, 2005, m_esikler=(5.0,))
    assert tab and tab[-1][1] == pytest.approx(2006.0)


def test_gk74_ile_gercek_ardisik_kume_tek_ana_sok():
    # Aynı gün, aynı yer, büyüklükçe azalan dizi: yalnız bir ana şok kalmalı.
    yil = np.array([2000.0, 2000.0 + 1 / 365.25, 2000.0 + 2 / 365.25])
    mw = np.array([6.5, 5.5, 5.0])
    la = np.array([38.0, 38.0, 38.0])
    lo = np.array([22.0, 22.0, 22.0])
    z = np.zeros(3)
    mask = gk74_mask(yil, la, lo, z, mw)
    assert mask.sum() == 1 and bool(mask[0])


def test_weichert_gecersiz_girdi():
    with pytest.raises(WeichertHatasi):
        weichert_mle(np.array([5.0]), np.array([2000.0]), [(1900, 2000, 5.0)],
                     kenarlar=np.array([4.0, 8.0, np.inf]), bas=1900, son=1999)
