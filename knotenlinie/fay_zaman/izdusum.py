"""Kaynak düzleminin yüzey izdüşümü → ızgara hücrelerine alan payı."""
from __future__ import annotations

import numpy as np
from shapely.geometry import box
from shapely.strtree import STRtree

IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']


class Izgara:
    """Hücre kutuları ve STRtree; çoklu poligon için yeniden kullanılır."""

    def __init__(self, izgara):
        a = izgara[IZGARA].to_numpy(float)
        self.n = len(a)
        self.kutular = [box(r[0], r[2], r[1], r[3]) for r in a]
        self.agac = STRtree(self.kutular)
        self.lat = 0.5 * (a[:, 2] + a[:, 3])

    def paylar(self, poligon):
        """(hücre indeksleri, alan payları, ızgara dışı pay); toplam pay + dışı = 1.

        Alan boylam–enlem derecesinde, hücre merkez enleminin cos'uyla ağırlıklı
        değil düz alan olarak alınır (poligon boyutlarında fark ihmal edilebilir)."""
        if poligon.is_empty or poligon.area <= 0:
            raise ValueError('poligon boş/alansız')
        idx = np.asarray(self.agac.query(poligon, predicate='intersects'), int)
        if idx.size == 0:
            return idx, np.zeros(0), 1.0
        a = np.array([self.kutular[i].intersection(poligon).area for i in idx])
        top = poligon.area
        pay = a / top
        keep = pay > 0
        return idx[keep], pay[keep], float(max(0.0, 1.0 - pay[keep].sum()))
