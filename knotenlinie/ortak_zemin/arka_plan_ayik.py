"""φ ağırlıklı, k-komşulu Gauss KDE; aynı kutuya koşullu kütle."""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree
from scipy.special import ndtr
from knotenlinie.etas import model as M


def uyarlamali_bant(x, y, kutu, k, alt_km):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.ndim != 1 or y.shape != x.shape or len(x) < 2 or not np.isfinite([x, y]).all():
        raise ValueError('Komşuluk için en az iki sonlu konum gerekli')
    if int(k) != k or k < 1 or not np.isfinite(alt_km) or alt_km <= 0:
        raise ValueError('k/alt bant geçersiz')
    met = M.yerel_metrik(kutu)
    xy = np.column_stack(met.km(x, y))
    # Öz-komşu hariç; çakışan ayrı olaylar komşudur. Küçük sentetikte k küçülür.
    return np.maximum(cKDTree(xy).query(xy, k=min(int(k), len(x)-1)+1)[0][:, -1], alt_km)


def kde_ayik(x, y, kutu, bantlar, phi, zemin_payi, dx=0.1, blok=128):
    x, y, h, w = [np.asarray(v, float) for v in (x, y, bantlar, phi)]
    if (x.ndim != 1 or not len(x) or any(v.shape != x.shape for v in (y,h,w)) or
            not all(np.isfinite(v).all() for v in (x,y,h,w)) or (h <= 0).any() or
            (w < 0).any() or (w > 1).any() or w.sum() <= 0 or not 0 < zemin_payi < 1):
        raise ValueError('Ayıklanmış KDE girdisi geçersiz')
    la0, la1, lo0, lo1 = kutu
    if ((x < lo0) | (x > lo1) | (y < la0) | (y > la1)).any():
        raise ValueError('KDE annesi kutu dışında')
    met = M.yerel_metrik(kutu)
    xe, ye = M.hucre_kenarlari(kutu, dx)
    mass = np.zeros((len(xe)-1, len(ye)-1))
    for a in range(0, len(x), blok):
        b = a + blok
        wx = np.diff(ndtr((xe[:,None]-x[None,a:b])*met.kx/h[None,a:b]), axis=0)
        wy = np.diff(ndtr((ye[:,None]-y[None,a:b])*met.ky/h[None,a:b]), axis=0)
        wx /= wx.sum(axis=0)
        wy /= wy.sum(axis=0)
        mass += (wx * w[None,a:b]) @ wy.T
    area = np.diff(xe)[:,None]*np.diff(ye)[None,:]
    density = (1-zemin_payi)*mass/w.sum()/area + zemin_payi/((lo1-lo0)*(la1-la0))
    return dict(x_kenar=xe, y_kenar=ye, yogunluk=density, kutu=list(kutu), dx=dx,
                tur='φ ağırlıklı uyarlamalı Gauss KDE + düzgün zemin',
                zemin_payi=float(zemin_payi), kde_n=len(x), phi_toplam=float(w.sum()),
                bant_min_km=float(h.min()), bant_medyan_km=float(np.median(h)),
                bant_max_km=float(h.max()), kde_sinir='her Gauss kutuya koşullu')
