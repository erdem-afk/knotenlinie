"""Wells ve Coppersmith (1994) yüzey altı kırık boyu (bütün faylanma türleri).

Yayın: Wells, D. L. ve Coppersmith, K. J. (1994), "New empirical relationships
among magnitude, rupture length, rupture width, rupture area, and surface
displacement", BSSA 84(4), 974-1002, Tablo 2A "All" satırı.  Yüzey altı kırık
boyu (RLD) için log10(L_km) = -2.44 + 0.59 Mw (n=193).  Yalnız M >= 5
ebeveynlere uygulanır; daha alçak M'de bağıntı zaten dış değer olurdu.
"""
from __future__ import annotations

import numpy as np


def kirik_boyu_km(mw):
    """RLD (km); Mw skaler ya da dizi, sonlu olmalı."""
    mw = np.asarray(mw, dtype=float)
    if mw.size and not np.isfinite(mw).all():
        raise ValueError('WC94 kırık boyu: Mw sonlu değil')
    return 10.0 ** (-2.44 + 0.59 * mw)
