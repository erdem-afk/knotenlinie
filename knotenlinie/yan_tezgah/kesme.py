"""Çift kesmesi: uzay silindiri (km) ve zaman penceresi (gün).

Olay terimi, kompansatör ve `YanModel.beklenen`/`_mekan` aynı kırpılmış çekirdeği
kullanır: ``g(r) 1[r <= Rmax]`` ve ``f(dt) 1[dt <= Tmax]``; kırpılmış çekirdek
yeniden normalize edilmez, böylece olabilirlik tutarlı kalır. Kesme parametreleri
bölgeye göre `BOLGE_KESME`'de durur ve puanlamadan önce `Y/KURAL.md`'de dondurulur.

`knotenlinie/etas_uzun/maske.py` dondurulmuş; bu yüzden aynı üçgen/sınır integrali burada
ayrı yazılır, `_ucgen_dugumleri` ve `radyal_cdf` yeniden kullanılır.
"""
from __future__ import annotations

import numpy as np

from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.maske import sinir

#: Bölge varsayılan kesmesi (records/Y/KURAL.md'de gerekçelenir).
BOLGE_KESME = {
    'scsn': dict(rmax_km=100.0, tmax_gun=365.25),
    'geonet': dict(rmax_km=100.0, tmax_gun=None),
}


def parametreler(bolge, rmax_km=None, tmax_gun=None) -> dict:
    """Bölge kesmesi; None bırakılan alan varsayılandan gelir."""
    v = dict(BOLGE_KESME[bolge])
    if rmax_km is not None:
        v['rmax_km'] = float(rmax_km)
    if tmax_gun is not None:
        v['tmax_gun'] = float(tmax_gun)
    return v


class KesikMaske:
    """`MaskeIntegrali`nin ``R <= rmax`` kırpılmış eşi.

    Kırpılan düğümlerde değer CDF(rmax²) olur; D ve q türevi aynı formülle kırpılmış R'de alınır. ``rmax_km=None``
    tam maskeyi verir (`MaskeIntegrali` ile bit düzeyinde aynı sonuç).
    """

    def __init__(self, x, y, izgara, met, rmax_km=None, blok=32):
        self.n = len(x)
        self.rmax2 = None if rmax_km is None else float(rmax_km) ** 2
        ax, ay, bx, by = sinir(izgara, met)
        xk, yk = met.km(x, y)
        self.kenar = len(ax)
        self.parcalar = []
        for a in range(0, self.n, blok):
            z = min(self.n, a + blok)
            R, w, pair, _ = M._ucgen_dugumleri(xk[a:z, None], yk[a:z, None], ax, ay, bx, by)
            j = (pair // len(ax)).astype(np.int32)
            if self.rmax2 is None:
                kesik = np.zeros(R.shape, bool)
            else:
                kesik = R > self.rmax2
                R = np.minimum(R, self.rmax2)
            self.parcalar.append((a, z, R, w, j, kesik))

    def deger(self, Di, q, grad=False):
        G = np.zeros(self.n)
        dD = G.copy()
        dq = G.copy()
        for a, z, R, w, j, kesik in self.parcalar:
            Dij = Di[a:z][j] if np.ndim(Di) else np.full(z - a, float(Di))[j]
            G[a:z] = np.bincount(j, w * M.radyal_cdf(R, Dij, q), minlength=z - a)
            if grad:
                U = R / Dij ** 2
                L = np.log1p(U)
                E = np.exp((1.0 - q) * L)
                tD = w * 2 * (1.0 - q) * U / (1.0 + U) * E
                tq = w * L * E
                # R düğümde rmax²'ye kırpıldıysa CDF(rmax²; D, q) hâlâ D ve q'ya bağlıdır:
                # türev, kırpılmış R ile aynı formülle alınır (sıfırlanmaz).
                dD[a:z] = np.bincount(j, tD, minlength=z - a)
                dq[a:z] = np.bincount(j, tq, minlength=z - a)
        if (G < -1e-10).any() or (G > 1 + 1e-10).any():
            raise ValueError('Maske integrali [0,1] dışında')
        return (G, dD, dq) if grad else G


def kesik_hucre_integralleri(x_i, y_i, D_i, q, kutu, dx=0.1, metrik=None,
                             rmax_km=None, blok=64):
    """`mekan_hucre_integralleri`nin ``R <= rmax`` kırpılmış eşi.

    Hücre başına ``int_cell g_i 1[r <= rmax] dA``; dört işaretli üçgen ayrışımı
    korunur, yalnız radyal CDF ``min(r, rmax)`` ile değerlendirilir.
    """
    met = metrik if metrik is not None else M.yerel_metrik(kutu)
    lo_k, la_k = M.hucre_kenarlari(kutu, dx)
    X = met.kx * (lo_k - met.lam0)
    Y = met.ky * (la_k - met.phi0)
    xk, yk = met.km(x_i, y_i)
    xk = np.atleast_1d(xk)
    yk = np.atleast_1d(yk)
    n = xk.size
    Di = np.broadcast_to(np.asarray(D_i, float), (n,)) if np.ndim(D_i) else np.full(n, float(D_i))
    nla, nlo = Y.size - 1, X.size - 1
    hax, hay = np.meshgrid(X[:-1], Y, indexing='xy')
    hbx, hby = np.meshgrid(X[1:], Y, indexing='xy')
    vax, vay = np.meshgrid(X, Y[:-1], indexing='xy')
    vbx, vby = np.meshgrid(X, Y[1:], indexing='xy')
    ax = np.concatenate([hax.ravel(), vax.ravel()])
    ay = np.concatenate([hay.ravel(), vay.ravel()])
    bx = np.concatenate([hbx.ravel(), vbx.ravel()])
    by = np.concatenate([hby.ravel(), vby.ravel()])
    ns = ax.size
    nh = (nla + 1) * nlo
    rmax2 = None if rmax_km is None else float(rmax_km) ** 2
    cikti = np.empty((n, nla, nlo))
    for a in range(0, n, blok):
        b = min(a + blok, n)
        R2, w, cift, n_cift = M._ucgen_dugumleri(xk[a:b, None], yk[a:b, None], ax[None, :], ay[None, :],
                                                 bx[None, :], by[None, :])
        if rmax2 is not None:
            R2 = np.minimum(R2, rmax2)
        olay = cift // ns
        S = np.bincount(cift, w * M.radyal_cdf(R2, Di[a:b][olay], q), minlength=n_cift).reshape(b - a, ns)
        H = S[:, :nh].reshape(b - a, nla + 1, nlo)
        V = S[:, nh:].reshape(b - a, nla, nlo + 1)
        cikti[a:b] = np.maximum(H[:, :-1, :] + V[:, :, 1:] - H[:, 1:, :] - V[:, :, :-1], 0.0)
    return cikti
