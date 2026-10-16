"""MLE: gradyan tutarlılığı ve sentetik geri kazanım (bilinen cevaplı dünya)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from knotenlinie.etas import model as MM
from knotenlinie.yan_tezgah import mle as ML


def _izgara(kutu, dx=0.1):
    la0, la1, lo0, lo1 = kutu
    enlem = np.round(np.arange(la0, la1, dx), 6)
    boylam = np.round(np.arange(lo0, lo1, dx), 6)
    return pd.DataFrame([(lo, lo + dx, la, la + dx) for la in enlem for lo in boylam],
                        columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])


def _simule(th, mc0, b, T, kutu, rng, n_bg=80):
    """Düz ETAS'tan Ogata inceltmesi olmadan ebeveyn-çocuk örneklemesi."""
    met = MM.yerel_metrik(kutu)
    la0, la1, lo0, lo1 = kutu
    c, p, D, q, alpha, gamma = (th['c'], th['p'], th['D'], th['q'], th['alpha'], th['gamma'])
    t0 = rng.uniform(0, T, n_bg)
    m0 = mc0 - np.log10(rng.random(n_bg)) / b
    x0 = rng.uniform(met.kx * (lo0 - met.lam0), met.kx * (lo1 - met.lam0), n_bg)
    y0 = rng.uniform(met.ky * (la0 - met.phi0), met.ky * (la1 - met.phi0), n_bg)
    hepsi = list(zip(t0, m0, x0, y0))
    yeni = hepsi
    while yeni:
        nxt = []
        for tj, mj, xj, yj in yeni:
            beklenen = th['K'] * 10 ** (alpha * (mj - mc0)) * c ** (1 - p) / (p - 1)
            for _ in range(int(rng.poisson(min(beklenen, 50)))):
                tau = c * (rng.random() ** (-1 / (p - 1)) - 1)
                m = mc0 - np.log10(rng.random()) / b
                Di = D * 10 ** (gamma * (mj - mc0))
                R = Di * np.sqrt((1 - rng.random()) ** (-1 / (q - 1)) - 1)
                ang = rng.uniform(0, 2 * np.pi)
                t = tj + tau
                if 0 <= t < T:
                    nxt.append((t, m, xj + R * np.cos(ang), yj + R * np.sin(ang)))
        hepsi += nxt
        yeni = nxt
    arr = np.array(hepsi)
    keep = ((arr[:, 2] >= met.kx * (lo0 - met.lam0)) & (arr[:, 2] < met.kx * (lo1 - met.lam0)) &
            (arr[:, 3] >= met.ky * (la0 - met.phi0)) & (arr[:, 3] < met.ky * (la1 - met.phi0)))
    arr = arr[keep]
    arr = arr[np.argsort(arr[:, 0], kind='stable')]
    x = arr[:, 2] / met.kx + met.lam0
    y = arr[:, 3] / met.ky + met.phi0
    return arr[:, 0], arr[:, 1], x, y


def test_gradyan_finite_difference():
    rng = np.random.default_rng(7)
    kutu = (34.0, 35.5, -119.0, -117.5)
    grid = _izgara(kutu)
    n = 150
    t = np.sort(rng.uniform(0, 300, n))
    m = 2.5 + rng.exponential(0.5, n)
    x = rng.uniform(-119, -117.5, n)
    y = rng.uniform(34, 35.5, n)
    L = ML.Olabilirlik(t, m, x, y, 1.0, 365.0, 2.5, np.full(n, 2.5), [(0.0, 365.0, 1.0)],
                       grid, kutu)
    th = dict(mu=.05, K=.02, c=.02, alpha=.6, p=1.2, D=1.5, q=1.5, gamma=.2)
    x0 = ML.donustur(th, 1.0, 'ortak')
    _, ga = L.objectif(x0, 'ortak')
    fd = np.zeros(len(x0))
    for i in range(len(x0)):
        h = 1e-6
        xp, xm = x0.copy(), x0.copy()
        xp[i] += h
        xm[i] -= h
        fd[i] = (L.objectif(xp, 'ortak')[0] - L.objectif(xm, 'ortak')[0]) / (2 * h)
    assert np.allclose(ga, fd, rtol=1e-4, atol=1e-6), (ga, fd)


def test_sentetik_geri_kazanim():
    rng = np.random.default_rng(20261011)
    kutu = (34.0, 35.5, -119.0, -117.5)
    grid = _izgara(kutu)
    T, mc0, b = 500.0, 2.5, 1.05
    gercek = dict(mu=.03, K=.02, c=.02, alpha=.6, p=1.2, D=1.5, q=1.5, gamma=0.0)
    t, m, x, y = _simule(gercek, mc0, b, T, kutu, rng, n_bg=120)
    assert 80 < len(t) < 4000
    L = ML.Olabilirlik(t, m, x, y, b, T, mc0, np.full(len(t), mc0), [(0.0, T, 1.0)], grid, kutu)
    sonuc = ML.ayarla(L, 'lm', maksiter=250)
    # MLE, gerçek parametreden daha kötü olabilirlik veremez.
    assert sonuc['logL'] >= L.deger(gercek) - 1e-6
    assert sonuc['dallanma'] < 1
    # b veriyle sabit; Mc altı olay yok.
    assert (m >= mc0 - 1e-12).all()
