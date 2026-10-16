"""Nedensel doğrultu: GCMT düğüm düzlemi (a) ya da artçı temel bileşen ekseni (b).

İki yol da yalnız gün başından önceki olayları kullanır.  (a) yolunda ebeveynle
eşleşen çözümün iki düğüm düzleminden ilk günün artçı dağılımına daha uyanı
seçilir; artçı yoksa ilk düzlem.  (b) yolunda ebeveynin <=L km ve <=3 gün
içindeki artçılarının en az 10 olması şartıyla temel bileşen ekseni doğrultu
olur, aksi hâlde ebeveyn izotrop kalır (None).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import gcmt as G


def pca_aci(lon, lat, met):
    """Temel bileşen büyük ekseninin kuzeyden saat yönü açısı (radyan) ya da None.

    Noktalar yerel km düzlemine taşınır; 2x2 kovaryansın büyük özvektörü
    (doğu, kuzey) olarak okunur, aci = atan2(doğu, kuzey).
    """
    lon = np.asarray(lon, float)
    lat = np.asarray(lat, float)
    if lon.size != lat.size:
        raise ValueError('PCA: lon/lat boyu farklı')
    if lon.size < 2:
        return None
    x, y = met.km(lon, lat)
    x = x - x.mean()
    y = y - y.mean()
    n = x.size
    cxx = float(np.dot(x, x) / n)
    cyy = float(np.dot(y, y) / n)
    cxy = float(np.dot(x, y) / n)
    if not np.isfinite([cxx, cyy, cxy]).all():
        return None
    if cxx + cyy <= 0.0:
        return None
    w, v = np.linalg.eigh(np.array([[cxx, cxy], [cxy, cyy]]))
    if w[-1] <= 1e-12 * max(1.0, float(w[-1])):
        return None
    return float(np.arctan2(float(v[0, -1]), float(v[1, -1])))


def _uzaklik_km(met, lon0, lat0, lon, lat):
    x, y = met.km(np.asarray(lon, float), np.asarray(lat, float))
    x0, y0 = met.km(lon0, lat0)
    return np.hypot(x - x0, y - y0)


class Yon:
    """Doğrultu belirleyici; bütün toleranslar önceden sabittir."""

    def __init__(self, gcmt=None, *, artci_pencere_gun=3.0, artci_min=10,
                 gcmt_zaman_tol_s=60.0, gcmt_uzaklik_km=50.0, ilk_gun_km=100.0,
                 ilk_gun_min=1):
        if artci_pencere_gun <= 0 or artci_min < 2 or ilk_gun_km <= 0:
            raise ValueError('Geçersiz doğrultu ayarı')
        self.g = None if gcmt is None else gcmt.sort_values('zaman', kind='stable').reset_index(drop=True)
        self.artci_pencere_gun = float(artci_pencere_gun)
        self.artci_min = int(artci_min)
        self.gcmt_zaman_tol_s = float(gcmt_zaman_tol_s)
        self.gcmt_uzaklik_km = float(gcmt_uzaklik_km)
        self.ilk_gun_km = float(ilk_gun_km)
        self.ilk_gun_min = int(ilk_gun_min)

    def _pencere(self, h, row, a, gun, yaricap_km, met):
        lo = int(h.zaman.searchsorted(row.zaman, side='right'))
        ust = row.zaman + pd.Timedelta(days=float(gun))
        ust = min(ust, a)
        hi = int(h.zaman.searchsorted(ust, side='right'))
        sub = h.iloc[lo:hi]
        if not len(sub):
            return sub
        km = _uzaklik_km(met, row.boylam, row.enlem, sub.boylam.to_numpy(float),
                         sub.enlem.to_numpy(float))
        return sub[km <= float(yaricap_km)]

    def _yon_a(self, row, h, a, met):
        sol = G.esles(self.g, row.zaman, float(row.boylam), float(row.enlem),
                      zaman_tol_s=self.gcmt_zaman_tol_s, uzaklik_km=self.gcmt_uzaklik_km,
                      merkez_once=a)
        if sol is None:
            return None
        d1, d2 = float(sol.dogrultu1), float(sol.dogrultu2)
        af = self._pencere(h, row, a, 1.0, self.ilk_gun_km, met)
        if len(af) < self.ilk_gun_min:
            duz = d1
        else:
            aci = pca_aci(af.boylam, af.enlem, met)
            if aci is None:
                duz = d1
            else:
                s1 = abs(np.cos(np.radians(d1) - aci))
                s2 = abs(np.cos(np.radians(d2) - aci))
                duz = d1 if s1 >= s2 else d2
        return dict(merkez_lon=float(row.boylam), merkez_lat=float(row.enlem),
                    dogrultu=duz, kaynak='a', gcmt_olay=sol.olay_adi, artci_n=int(len(af)))

    def _yon_b(self, row, h, a, met, L):
        af = self._pencere(h, row, a, self.artci_pencere_gun, L, met)
        if len(af) < self.artci_min:
            return None
        aci = pca_aci(af.boylam, af.enlem, met)
        if aci is None:
            return None
        return dict(merkez_lon=float(af.boylam.mean()), merkez_lat=float(af.enlem.mean()),
                    dogrultu=float(np.degrees(aci)), kaynak='b', artci_n=int(len(af)))

    def yon(self, tip, h, j, a, met, L):
        """`tip` 'a' ya da 'b'; (merkez_lon, merkez_lat, dogrultu) ya da None."""
        if tip not in ('a', 'b'):
            raise ValueError("Doğrultu yolu 'a' ya da 'b' olmalı")
        row = h.iloc[int(j)]
        if tip == 'a':
            return self._yon_a(row, h, a, met)
        return self._yon_b(row, h, a, met, float(L))
