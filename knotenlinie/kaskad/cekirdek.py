"""Ortak ETAS için nedensel zaman ve GR-ağırlıklı mekân operatörleri."""
from __future__ import annotations

import numpy as np
from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin.arayuz import omori_kutle


def ortalama_uretkenlik(th, b):
    """Kesilmemiş GR altında E[K 10**(alpha (M-Mc))]."""
    if not b > th['alpha'] or th['K'] < 0:
        raise ValueError('Sonlu/negatif olmayan GR üretkenliği gerekli')
    return th['K'] * b / (b - th['alpha'])


def zaman_operatoru(duration, adim, th, b):
    """Uniform kaynak zaman kutusunun kızları: aynı kutu da nedenseldir."""
    if duration <= 0 or adim < 1 or int(adim) != adim:
        raise ValueError('Geçersiz süre/adım')
    dt = duration / adim
    t = np.arange(adim + 1) * dt
    c, p = th['c'], th['p']
    I = omori_kutle(0, t, c, p)
    if abs(p - 2) < 1e-12:
        first = np.log1p(t / c)
    else:
        first = c**(2-p) * np.expm1((2-p)*np.log1p(t/c)) / (2-p)
    primitive = (t+c)*I - first
    h = np.r_[primitive[1], np.diff(primitive, n=2)] / dt
    if (h < -1e-11).any():
        raise ValueError('Negatif zaman geçişi')
    h = np.maximum(h, 0) * ortalama_uretkenlik(th, b)
    i, j = np.indices((adim, adim))
    return np.where(i >= j, h[np.maximum(i-j, 0)], 0)


def zaman_katsayilari(age, mags, duration, th, b, mc, adim=32, nesil=10):
    """Nesil katsayıları; son sütun birim arka-plan oranıdır."""
    age, mags = np.asarray(age, float), np.asarray(mags, float)
    if age.shape != mags.shape or (age < 0).any() or not np.isfinite(age).all() or not np.isfinite(mags).all():
        raise ValueError('Geçersiz geçmiş')
    if nesil < 0 or int(nesil) != nesil:
        raise ValueError('Geçersiz nesil')
    t = np.linspace(0, duration, adim+1)
    f = omori_kutle(age[None, :]+t[:-1, None], age[None, :]+t[1:, None], th['c'], th['p'])
    f *= th['K'] * 10**(th['alpha']*(mags-mc))[None, :]
    f = np.column_stack([f, np.full(adim, duration/adim)])
    op = zaman_operatoru(duration, adim, th, b)
    out = [f.sum(axis=0)]
    for _ in range(nesil):
        f = op @ f
        out.append(f.sum(axis=0))
    return np.asarray(out)


def mekan_kernel(nx, ny, dx, dy, th, b, *, uzay_dugum=4, gr_dugum=32):
    """Uniform kaynak hücre → tam hedef integrali; GR sonsuza gider.

    K'nın ortalaması zaman operatöründedir. Mekân, üretkenlikle ağırlıklı
    GR karışımıdır: x=(b-alpha) ln(10) (M-Mc) ~ Exp(1). Böylece gamma
    ile büyüyen çekirdek ortalama büyüklüğe indirgenmez. Hedef integrali
    tabanın radyal-CDF/üçgen kuadratürü, kaynak GL, GR Gauss-Laguerre.
    """
    if min(nx, ny, uzay_dugum, gr_dugum) < 1 or min(dx, dy) <= 0:
        raise ValueError('Geçersiz mekân kuadratürü')
    ortalama_uretkenlik(th, b)
    sx, sw = np.polynomial.legendre.leggauss(uzay_dugum)
    rx, rw = np.polynomial.laguerre.laggauss(gr_dugum)
    scales = th['D'] * np.exp(th['gamma'] / (b-th['alpha']) * rx)
    # Pozitif ofset çeyreği yeterli: uniform kaynak ve radyal çekirdek simetrik.
    X, Y = (np.arange(nx+1)-.5)*dx, (np.arange(ny+1)-.5)*dy
    hax, hay = np.meshgrid(X[:-1], Y)
    hbx, hby = np.meshgrid(X[1:], Y)
    vax, vay = np.meshgrid(X, Y[:-1])
    vbx, vby = np.meshgrid(X, Y[1:])
    ax, ay = np.r_[hax.ravel(), vax.ravel()], np.r_[hay.ravel(), vay.ravel()]
    bx, by = np.r_[hbx.ravel(), vbx.ravel()], np.r_[hby.ravel(), vby.ravel()]
    nh = (ny+1)*nx
    quadrant = np.zeros((ny, nx))
    for i, x in enumerate(sx):
        for j, y in enumerate(sx):
            R2, w, pair, count = M._ucgen_dugumleri(x*dx/2, y*dy/2, ax, ay, bx, by)
            cdf = np.zeros_like(R2)
            for scale, weight in zip(scales, rw):
                cdf += weight * M.radyal_cdf(R2, scale, th['q'])
            S = np.bincount(pair, w*cdf, minlength=count)
            H, V = S[:nh].reshape(ny+1, nx), S[nh:].reshape(ny, nx+1)
            cells = H[:-1] + V[:, 1:] - H[1:] - V[:, :-1]
            if cells.min() < -1e-12:
                raise ValueError('Negatif mekân kütlesi')
            quadrant += sw[i]*sw[j]/4 * np.maximum(cells, 0)
    out = quadrant[np.abs(np.arange(-ny+1, ny))[:, None], np.abs(np.arange(-nx+1, nx))[None, :]]
    if out.sum() > 1+1e-10:
        raise ValueError('Mekân operatörü birim kütleyi aşıyor')
    return out
