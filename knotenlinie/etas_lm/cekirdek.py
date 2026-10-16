"""Lombardi–Marzocchi (2010), denklem 1 ve Tablo 1; gün/km birimleri."""
from __future__ import annotations

import numpy as np
from knotenlinie.ortak_zemin.arayuz import omori_kutle

YIL = 365.25
MC, B, ALPHA, P, D = 2.5, 1.0, 1.3, 1.16, 1.10
K, C = .011 * YIL ** (P - 1), .00004 * YIL


def uretkenlik(m):
    """Makalenin alpha'sı doğal üstel; 10 tabanına karıştırılmaz."""
    return K * np.exp(ALPHA * (np.asarray(m, float) - MC))


def ortalama_uretkenlik(mmax=9.0):
    beta = B * np.log(10)
    width = mmax - MC
    return K * beta / (beta - ALPHA) * (-np.expm1(-(beta - ALPHA) * width)) / (-np.expm1(-beta * width))


def hucre_kutlesi(x, y, grid_km, d=D):
    """q=1.5 için analitik dikdörtgen solid-angle integrali, floor/renorm yok."""
    if not np.isfinite(d) or d <= 0:
        raise ValueError('d pozitif olmalı')
    g = np.asarray(grid_km, float)
    if g.ndim != 2 or g.shape[1] != 4 or not np.isfinite(g).all() or (g[:, 1] <= g[:, 0]).any() or (g[:, 3] <= g[:, 2]).any():
        raise ValueError('Geçersiz km hücresi')
    def f(a, b):
        return np.arctan2(a * b, d * np.sqrt(a*a + b*b + d*d)) / (2*np.pi)
    x0, x1, y0, y1 = g.T
    mass = f(x1-x, y1-y) - f(x0-x, y1-y) - f(x1-x, y0-y) + f(x0-x, y0-y)
    if (mass < -1e-13).any():
        raise ValueError('Negatif analitik kütle')
    return np.maximum(mass, 0)


def radyal_kutle(r):
    return 1 - D / np.sqrt(np.asarray(r, float)**2 + D**2)


def zaman_operatoru(duration, adim):
    """Uniform kaynak zaman-kutusu → hedef kutusu, Omori çift integrali.

    Alt üçgensel Toeplitz. Köşegen aynı zaman kutusu içindeki nedensel
    kızları içerir; gelecekteki gözlemlere erişmeden beklenen kızlar eklenir.
    """
    if duration <= 0 or adim < 1 or int(adim) != adim:
        raise ValueError('Geçersiz süre/adım')
    dt = duration / adim
    t = np.arange(adim + 1) * dt
    primitive = ((t+C)**(2-P) - C**(2-P)) / ((1-P)*(2-P)) - t*C**(1-P)/(1-P)
    h = np.empty(adim)
    h[0] = primitive[1] / dt
    if adim > 1:
        h[1:] = np.diff(primitive, n=2) / dt
    h *= ortalama_uretkenlik()
    i, j = np.indices((adim, adim))
    return np.where(i >= j, h[np.maximum(i-j, 0)], 0)


def zaman_katsayilari(age, mags, duration, adim=32, nesil=10):
    """Nesil başına gerçek ebeveyn katsayıları + birim arka-plan katsayısı."""
    age, mags = np.asarray(age, float), np.asarray(mags, float)
    if age.shape != mags.shape or (age < 0).any() or not np.isfinite(age).all() or not np.isfinite(mags).all() or nesil < 0:
        raise ValueError('Geçersiz geçmiş/nesil')
    t = np.linspace(0, duration, adim+1)
    f = omori_kutle(age[None, :]+t[:-1, None], age[None, :]+t[1:, None], C, P) * uretkenlik(mags)[None, :]
    f = np.column_stack([f, np.full(adim, duration/adim)])
    op = zaman_operatoru(duration, adim)
    out = [f.sum(axis=0)]
    for _ in range(nesil):
        f = op @ f
        out.append(f.sum(axis=0))
    return np.asarray(out)
