"""Deney W: hedef (i) gözlenecek oran için günlük kutu bazlı tespit olasılığı q̄.

Hedef (ii) gerçek orandır: W parametreleriyle R'nin kaskad tahmini (``UzunETAS``).
Hedef (i) = (ii) × q̄(gün, kutu); q̄ yalnız gün başından önceki olaylardan hesaplanır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.etas_uzun.arayuz import ebeveynler
from knotenlinie.ortak_zemin.arayuz import utc
from .tamlik import (MC0, SIGMA, Z95, HKJ_M_ESIK, HKJ_PENCERE, HAINZL_PENCERE, kutu_q, sonra_a, sonra_b)

EPOCH = pd.Timestamp('1985-01-01', tz='UTC')
#: gün içi alt adım kenarları (günün kesri); ilk saatlerdeki hızlı değişimi çözer
ALT_KENAR = np.array([0.0, 1e-3, 2e-3, 4e-3, 8e-3, 0.016, 0.032, 0.064, 0.128, 0.256, 0.512, 1.0])
OMORI_PROXY_M = 4.0
GERI_PENCERE = 60.0


def _gun(zaman):
    return ((pd.DatetimeIndex(pd.to_datetime(zaman, utc=True)) - EPOCH) / pd.Timedelta(days=1)).to_numpy(float)


def oran_vekili(t, tp, mp, th):
    """Gün içi ağırlık: μ + Σ K 10^{α(M−2,5)} (t−t_i+c)^{−p}; t (s,), tp/mp ebeveynler."""
    r = np.full(t.shape, th['mu'], float)
    if len(tp):
        dt = t[:, None] - tp[None, :] + th['c']
        r = r + ((th['K'] * 10 ** (th['alpha'] * (mp - MC0)))[None, :] * dt ** (-th['p'])).sum(1)
    return r


def q_gunluk(fit, raw, edges, bas, son):
    """(ngun, nkutu) günlük kutu-ortalama tespit olasılığı; ``fit``: W kurulum JSON'u.

    Kural: günün alt adımlarında Mc_sonra, YALNIZ gün başından önceki M≥5 olaylardan hesaplanır
    (gün içi olaylar sızdırılmaz). Ağırlık oran vekilidir (geçmiş M≥4 olaylar).
    """
    tur = fit['stai']['tur']
    theta = fit.get('stai_theta')
    b = float(fit['b']['deger'])
    beta = b * np.log(10.0)
    th = {k: float(v) for k, v in fit['parametreler'].items()}
    kutu = tuple(fit['kutu'])
    k = ebeveynler(raw, kutu)
    tk, mk = _gun(k.zaman), k.mw.to_numpy(float)
    ib = mk >= HKJ_M_ESIK
    bt, bm = tk[ib], mk[ib]
    ip = mk >= OMORI_PROXY_M
    pt, pm = tk[ip], mk[ip]
    e = np.asarray(edges, float)
    m1, m2 = e[:-1], e[1:]
    t0s = _gun(pd.date_range(bas, son, freq='D', inclusive='left'))
    pencere = HKJ_PENCERE if tur == 'a' else HAINZL_PENCERE
    out = np.ones((len(t0s), len(m1)))
    mid = 0.5 * (ALT_KENAR[:-1] + ALT_KENAR[1:])
    gen = np.diff(ALT_KENAR)
    for d, t0 in enumerate(t0s):
        lo, hi = np.searchsorted(bt, t0 - pencere, side='left'), np.searchsorted(bt, t0, side='left')
        if hi == lo:
            continue
        ts = t0 + mid
        if tur == 'a':
            sonra = sonra_a(ts, bt[lo:hi], bm[lo:hi])
        else:
            sonra = sonra_b(ts, bt[lo:hi], theta)
        mus = sonra - Z95 * SIGMA
        if not np.isfinite(mus).any():
            continue
        plo, phi = np.searchsorted(pt, t0 - GERI_PENCERE, side='left'), np.searchsorted(pt, t0, side='left')
        w = gen * oran_vekili(ts, pt[plo:phi], pm[plo:phi], th)
        q = np.stack([kutu_q(mu, m1, m2, beta) for mu in mus])
        out[d] = np.clip((w[:, None] * q).sum(0) / w.sum(), 0.0, 1.0)
    return out
