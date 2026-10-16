"""Kesme testleri (Y2): büyük kesme = kesmesiz, kırpılmış MLE geri kazanım,
kompansatör–olay terimi sayısal integral tutarlılığı."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.integrate import quad

from knotenlinie.etas import model as MM
from knotenlinie.yan_tezgah import mle as ML
from knotenlinie.yan_tezgah import model as YM


def _izgara(kutu, dx=0.1):
    la0, la1, lo0, lo1 = kutu
    enlem = np.round(np.arange(la0, la1, dx), 6)
    boylam = np.round(np.arange(lo0, lo1, dx), 6)
    return pd.DataFrame([(lo, lo + dx, la, la + dx) for la in enlem for lo in boylam],
                        columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])


KUTU = (34.0, 35.5, -119.0, -117.5)


def _katalog(n=60, tohum=3, T=300.0):
    rng = np.random.default_rng(tohum)
    t = np.sort(rng.uniform(0, T, n))
    m = 2.5 + rng.exponential(0.5, n)
    x = rng.uniform(KUTU[2], KUTU[3], n)
    y = rng.uniform(KUTU[0], KUTU[1], n)
    return t, m, x, y


def _olabilirlik(rmax_km=None, tmax_gun=None, T=365.0):
    t, m, x, y = _katalog()
    return ML.Olabilirlik(t, m, x, y, 1.05, T, 2.5, np.full(len(t), 2.5),
                          [(0.0, 150.0, 1.0), (150.0, T, 0.5)], _izgara(KUTU), KUTU,
                          rmax_km=rmax_km, tmax_gun=tmax_gun)


def test_buyuk_kesme_kesmesizle_ayni():
    """Kimsenin erişemeyeceği kadar büyük kesme, kesmesiz olabilirlikle aynı olmalı."""
    L0 = _olabilirlik(rmax_km=None, tmax_gun=None)
    L1 = _olabilirlik(rmax_km=1e6, tmax_gun=1e9)
    assert L0.cift == L1.cift
    th = dict(mu=.05, K=.01, c=.02, alpha=.6, p=1.2, D=2.0, q=1.5, gamma=.2)
    l0, g0 = L0.deger(th, True)
    l1, g1 = L1.deger(th, True)
    assert np.isclose(l0, l1, rtol=1e-12, atol=1e-12)
    assert np.allclose(g0, g1, rtol=1e-9, atol=1e-9)
    I0, _, _ = L0.zaman(.02, 1.2)
    I1, _, _ = L1.zaman(.02, 1.2)
    assert np.allclose(I0, I1, rtol=1e-12, atol=1e-12)


def _simule_kesik(th, mc0, b, T, kutu, rng, *, n_bg=500, rmax=30.0, tmax=150.0):
    """Kırpılmış ETAS'tan ebeveyn-çocuk örneklemesi: tau<=tmax ve R<=rmax koşullu."""
    met = MM.yerel_metrik(kutu)
    la0, la1, lo0, lo1 = kutu
    c, p, D, q, alpha, gamma = (th['c'], th['p'], th['D'], th['q'], th['alpha'], th['gamma'])
    tf = (c ** (1 - p) - (c + tmax) ** (1 - p)) / (p - 1)
    t0 = rng.uniform(0, T, n_bg)
    m0 = mc0 - np.log10(rng.random(n_bg)) / b
    x0 = rng.uniform(met.kx * (lo0 - met.lam0), met.kx * (lo1 - met.lam0), n_bg)
    y0 = rng.uniform(met.ky * (la0 - met.phi0), met.ky * (la1 - met.phi0), n_bg)
    hepsi = list(zip(t0, m0, x0, y0))
    yeni = hepsi
    while yeni:
        nxt = []
        for tj, mj, xj, yj in yeni:
            Di = D * 10 ** (gamma * (mj - mc0))
            fsp = 1 - (1 + rmax ** 2 / Di ** 2) ** (1 - q)
            bek = th['K'] * 10 ** (alpha * (mj - mc0)) * tf * fsp
            for _ in range(int(rng.poisson(min(bek, 50)))):
                while True:
                    tau = c * (rng.random() ** (-1 / (p - 1)) - 1)
                    if tau <= tmax:
                        break
                while True:
                    R = Di * np.sqrt((1 - rng.random()) ** (-1 / (q - 1)) - 1)
                    if R <= rmax:
                        break
                ang = rng.uniform(0, 2 * np.pi)
                t = tj + tau
                if 0 <= t < T:
                    nxt.append((t, mc0 - np.log10(rng.random()) / b,
                                xj + R * np.cos(ang), yj + R * np.sin(ang)))
        hepsi += nxt
        yeni = nxt
    arr = np.array(hepsi)
    keep = ((arr[:, 2] >= met.kx * (lo0 - met.lam0)) & (arr[:, 2] < met.kx * (lo1 - met.lam0)) &
            (arr[:, 3] >= met.ky * (la0 - met.phi0)) & (arr[:, 3] < met.ky * (la1 - met.phi0)))
    arr = arr[keep]
    arr = arr[np.argsort(arr[:, 0], kind='stable')]
    return arr[:, 0], arr[:, 1], arr[:, 2] / met.kx + met.lam0, arr[:, 3] / met.ky + met.phi0


def test_kesmeli_sentetik_geri_kazanim():
    """Kırpılmış çekirdekten üretilen katalogda kırpılmış MLE parametreyi geri kazanır."""
    rng = np.random.default_rng(20261011)
    mc0, b, T = 2.5, 1.05, 1000.0
    rmax, tmax, n_bg = 30.0, 150.0, 500
    gercek = dict(K=.015, c=.05, alpha=.6, p=1.2, D=2.0, q=1.5, gamma=0.0)
    t, m, x, y = _simule_kesik(gercek, mc0, b, T, KUTU, rng, n_bg=n_bg, rmax=rmax, tmax=tmax)
    assert 200 < len(t) < 6000
    L = ML.Olabilirlik(t, m, x, y, b, T, mc0, np.full(len(t), mc0), [(0.0, T, 1.0)],
                       _izgara(KUTU), KUTU, rmax_km=rmax, tmax_gun=tmax)
    son = ML.ayarla(L, 'lm', maksiter=300)
    th = son['parametreler']
    mu_gercek = n_bg / T
    assert abs(th['mu'] - mu_gercek) < 0.30 * mu_gercek
    assert 0.4 < th['K'] / gercek['K'] < 2.5
    assert abs(th['alpha'] - gercek['alpha']) < 0.25
    assert abs(th['p'] - gercek['p']) < 0.3
    assert son['dallanma'] < 1.0
    # MLE, gerçek parametrelerin birkaç nat yakınında olmalı (yüzey düz olabilir).
    assert abs(son['logL'] - L.deger(dict(gercek, mu=mu_gercek))) < 5.0


def test_kompansator_olay_sayisal_integral():
    """Zaman (quad) ve uzay (ızgara) integralleri, tahminin kırpılmış normalizasyonuyla tutarlı."""
    t, m, x, y = _katalog()
    T, c, p, rmax, tmax = 365.0, 0.02, 1.2, 40.0, 120.0
    th = dict(mu=0.0, K=.02, c=c, alpha=.6, p=p, D=5.0, q=1.5, gamma=0.0)
    araliklar = [(0.0, 150.0, 1.0), (150.0, T, 0.5)]
    L = ML.Olabilirlik(t, m, x, y, 1.05, T, 2.5, np.full(len(t), 2.5), araliklar,
                       _izgara(KUTU), KUTU, rmax_km=rmax, tmax_gun=tmax)
    I, _, _ = L.zaman(c, p)

    def s_of(tt):
        for lo, hi, s in araliklar:
            if lo <= tt < hi or (hi == T and tt == T):
                return s
        return 0.0

    for i in (0, len(t) // 2, len(t) - 1):
        ti = t[i]
        hi = min(T, ti + tmax)
        bnd = sorted({ti, hi} | {b for lo, _, _ in araliklar for b in (lo, hi) if ti < b < hi})
        num = 0.0
        for a, bb in zip(bnd[:-1], bnd[1:]):
            if bb <= a:
                continue
            s = s_of(0.5 * (a + bb))
            if s:
                num += s * quad(lambda tau: (tau + c) ** (-p), a - ti, bb - ti, epsabs=1e-13)[0]
        assert np.isclose(I[i], num, rtol=1e-9, atol=1e-9)

    # Uzay: YanModel._mekan (tahmin) brüt kuvvet ızgara integraline eşit olmalı; kesme de.
    grid = _izgara(KUTU)
    parent = pd.DataFrame(dict(zaman=[pd.Timestamp('2000-01-01', tz='UTC')], enlem=[34.6],
                               boylam=[-118.4], derinlik=[5.0], mw=[3.2]))
    m2 = YM.YanModel(ad='T', p=dict(parametreler=th), mc0=2.5, b=1.05, hedef=2.5,
                     bolge='scsn', donem_mc=[], hkj=False, m_buyuk=5.0, hkj_gun=30.0,
                     epoch=parent.zaman.iloc[0], rmax_km=rmax, tmax_gun=tmax)
    a = parent.zaman.iloc[0] + pd.Timedelta(days=1)
    edges = np.array([2.5, 2.6, np.inf])
    bek = m2.beklenen(a, a + pd.Timedelta(days=1), parent, grid, edges)
    wmag = 10 ** 0 - 10 ** (-1.05 * 0.1)
    G_bek = float(bek[:, 0].sum()) / wmag
    om = (MM._omori_ilke(np.array([2.0]), c, p)[0] - MM._omori_ilke(np.array([1.0]), c, p)[0])[0]
    K_A_om = th['K'] * 10 ** (th['alpha'] * (3.2 - 2.5)) * om
    # Brute-force disk integrali, modelin kendi metriğiyle, disk ızgaranın içinde.
    met = m2._mekan_met
    xk, yk = met.km(-118.4, 34.6)
    adim = 0.2
    eksen = np.arange(-rmax + adim / 2, rmax, adim)
    X, Y = np.meshgrid(xk + eksen, yk + eksen)
    r2 = (X - xk) ** 2 + (Y - yk) ** 2
    g = MM.mekan_cekirdegi(r2, 5.0, th['q'], 0.0, np.array([0.0]), 0.0)
    G_brute = float(g[r2 <= rmax ** 2].sum() * adim ** 2)
    assert np.isclose(G_bek, K_A_om * G_brute, rtol=5e-3)


def test_kesmeli_gradyan_finite_difference():
    """Kırpılmış çekirdekte analitik gradyan sonlu farkla uyumlu (D ve q dahil)."""
    L = _olabilirlik(rmax_km=15.0, tmax_gun=100.0)
    th = dict(mu=.05, K=.02, c=.02, alpha=.6, p=1.2, D=0.3, q=1.5, gamma=.2)
    x0 = ML.donustur(th, 1.05, 'ortak')
    _, ga = L.objectif(x0, 'ortak')
    fd = np.zeros(len(x0))
    for i in range(len(x0)):
        h = 1e-6
        xp, xm = x0.copy(), x0.copy()
        xp[i] += h
        xm[i] -= h
        fd[i] = (L.objectif(xp, 'ortak')[0] - L.objectif(xm, 'ortak')[0]) / (2 * h)
    assert np.allclose(ga, fd, rtol=1e-4, atol=1e-6), (ga, fd)


def test_d2_kompansator_hedef_tabani_yok():
    """D2 tespit parçaları KURAL'a uyar: max(Mc_dönem, Mc_sonra); hedef eşiği tabanı yok."""
    epoch = pd.Timestamp('2000-01-01', tz='UTC')
    tm = dict(pencereler=[dict(bas_yil=2000, bit_yil=2003, mc=2.6)], en_buyuk=2.6)
    fit = pd.DataFrame(dict(zaman=[epoch + pd.Timedelta(days=500)], mw=[9.0]))
    b, T = 1.0, 1000.0
    ar = YM._araliklar_hkj(tm, fit, 2.6, b, epoch, T, 5.0, 30.0, 1.0, 3.8)
    # büyük olaydan 400 gün önce: yalnız dönem Mc'si -> s = 1 (hedef 3.8 olsaydı 10^-1.2)
    s_once = [s for a, bb, s in ar if a <= 100.0 < bb][0]
    assert np.isclose(s_once, 1.0)
    # olaydan hemen sonra HKJ: Mc_sonra = 9-4.5-0.75 log10(dt) > 2.6 -> s < 1
    s_sonra = [s for a, bb, s in ar if a <= 500.5 < bb][0]
    assert s_sonra < 1.0
