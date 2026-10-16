"""STEP bileşenleri: Gardner–Knopoff pencereleri, Omori integrali, 1/(r²+d²) çekirdeği.

Birim: zaman gün, uzaklık km. Çekirdek yoğunluğu f(r) ∝ 1/(r²+d²), [-R,R]² kutusuna
kesilmiş. Hücre kütlesi kapalı biçimdedir: x = d·sinh(u) dönüşümüyle iç integral
atan farkına iner, dış integral Gauss–Legendre ile alınır (pürüzsüz).
"""
from __future__ import annotations

import numpy as np

KM_DERECE = 111.195
GL_DUGUM = 32
_GLX, _GLW = np.polynomial.legendre.leggauss(GL_DUGUM)


def gk_yaricap(m):
    """Gardner–Knopoff (1974) uzay penceresi, km."""
    return 10.0 ** (0.1238 * np.asarray(m, float) + 0.983)


def gk_sure(m):
    """Gardner–Knopoff (1974) zaman penceresi (Uhrhammer 1986 uydurması), gün."""
    m = np.asarray(m, float)
    return np.where(m >= 6.5, 10.0 ** (0.032 * m + 2.7389), 10.0 ** (0.5409 * m - 0.547))


def kirilma_uzunlugu(m):
    """Wells–Coppersmith (1994) tüm tipler, yüzey altı kırılma uzunluğu, km."""
    return 10.0 ** (-2.44 + 0.59 * np.asarray(m, float))


def cekirdek_olcegi(m, d_min=1.0):
    """Çekirdek yumuşatma uzunluğu d = max(d_min, L/2), km."""
    return np.maximum(d_min, 0.5 * kirilma_uzunlugu(m))


def omori_integral(t1, t2, c, p):
    """∫_{t1}^{t2} (t+c)^-p dt, p=1 dahil kararlı."""
    t1 = np.asarray(t1, float)
    t2 = np.asarray(t2, float)
    q = 1.0 - p
    oran = np.log((t2 + c) / (t1 + c))
    if abs(q) < 1e-9:
        return oran
    return (t1 + c) ** q * np.expm1(q * oran) / q


def uzaklik_km(lat, lon, lat2, lon2):
    p, q = np.radians(lat), np.radians(np.asarray(lat2, float))
    dlon = np.radians(np.asarray(lon2, float) - lon)
    h = np.sin((q - p) / 2) ** 2 + np.cos(p) * np.cos(q) * np.sin(dlon / 2) ** 2
    return 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))


def _kutle(x0, x1, y0, y1, d):
    """∬ dx dy /(x²+y²+d²) dikdörtgen üstünde; x0<x1, y0<y1 (diziler)."""
    u0 = np.arcsinh(x0 / d)
    u1 = np.arcsinh(x1 / d)
    orta = 0.5 * (u0 + u1)[:, None]
    yari = 0.5 * (u1 - u0)[:, None]
    u = orta + yari * _GLX[None, :]
    s = d * np.cosh(u)
    f = np.arctan(y1[:, None] / s) - np.arctan(y0[:, None] / s)
    return (f * _GLW[None, :]).sum(axis=1) * yari[:, 0]


def kutu_toplami(d, r):
    """Çekirdeğin [-r,r]² kutusundaki toplamı (normalleştirici)."""
    z = np.array([-r]), np.array([r])
    return float(_kutle(z[0], z[1], z[0], z[1], d)[0])


def hucre_kutlesi(izgara_dizi, boylam, enlem, d, r):
    """Kaynak (boylam, enlem) için 1/(r²+d²) çekirdeğinin hücre kütleleri.

    izgara_dizi: (N,4) boylam_min, boylam_max, enlem_min, enlem_max. Dönen vektör
    kutu içinde kalan kütleyi verir (toplam ≤ 1; kutu ızgara dışına taşarsa kayıp).
    """
    g = izgara_dizi
    kx = KM_DERECE * np.cos(np.radians(enlem))
    ky = KM_DERECE
    out = np.zeros(len(g))
    x0 = (g[:, 0] - boylam) * kx
    x1 = (g[:, 1] - boylam) * kx
    y0 = (g[:, 2] - enlem) * ky
    y1 = (g[:, 3] - enlem) * ky
    ic = (x1 > -r) & (x0 < r) & (y1 > -r) & (y0 < r)
    idx = np.flatnonzero(ic)
    if not len(idx):
        return out
    a0 = np.maximum(x0[idx], -r)
    a1 = np.minimum(x1[idx], r)
    b0 = np.maximum(y0[idx], -r)
    b1 = np.minimum(y1[idx], r)
    out[idx] = _kutle(a0, a1, b0, b1, d) / kutu_toplami(d, r)
    return out
