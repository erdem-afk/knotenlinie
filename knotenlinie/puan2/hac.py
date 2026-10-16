"""Newey–West / Diebold–Mariano SE: günlük kazanç serisi üstünde, oran-kestirici (ΣD/N) için."""
from __future__ import annotations

import numpy as np
from scipy import stats

from knotenlinie.karsilastir.puan import PuanHatasi


def gecikme_kurali(T):
    """KURAL.md §3: floor(4 (T/100)^(2/9))."""
    return int(np.floor(4.0 * (T / 100.0) ** (2.0 / 9.0)))


def hac_ozeti(gun_kazanci, gun_n, *, gecikme=None, n=None):
    """IG=ΣD/N, u_t=D_t−IG n_t; Bartlett çekirdeği; T/(T−1) küçük örnek çarpanı.

    gecikme=0 → günlük bloklu sandwich (i.i.d. SE). Dönüş: IG, SE_HAC, z (tek yönlü), p_tek, gecikme.
    """
    D, N = np.asarray(gun_kazanci, float), np.asarray(gun_n, float)
    if D.shape != N.shape or D.ndim != 1 or not np.isfinite(D).all():
        raise PuanHatasi('HAC girdisi geçersiz')
    T = len(D)
    n = float(N.sum()) if n is None else float(n)
    L = gecikme_kurali(T) if gecikme is None else int(gecikme)
    if L < 0 or L >= T:
        raise PuanHatasi('Gecikme [0, T) olmalı')
    if n == 0 or T < 2:
        return dict(N=int(n), IG=None, SE_HAC=None, z=None, p_tek=None, gecikme=L, T=T)
    ig = float(D.sum() / n)
    u = D - ig * N
    s = float(np.dot(u, u))
    for l in range(1, L + 1):
        s += 2.0 * (1.0 - l / (L + 1.0)) * float(np.dot(u[l:], u[:-l]))
    s = max(s, 0.0)
    se = float(np.sqrt(T / (T - 1.0) * s) / n)
    z = ig / se if se > 0 else (0.0 if ig == 0 else float(np.copysign(np.inf, ig)))
    return dict(N=int(n), IG=ig, SE_HAC=se, z=float(z), p_tek=float(stats.norm.sf(z)), gecikme=L, T=T)
