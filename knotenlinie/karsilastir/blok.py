"""Haftalık blok sandwich SE (``blok_ozeti``): günlük skor kazancının olay başına IG'si ve SE'si.

Kör pencere açma kodundan ayrılmış tek yardımcıdır; kör açma kodu ön kayıt dondurulana kadar
bu sürümde yoktur. Yalnız numpy, pandas ve scipy.stats kullanır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def blok_ozeti(gun_kazanci, gun_n, gunler, *, n=None):
    """Haftalık oran-kestirici sandwich SE; sıfır olaylı haftalar da dahil."""
    D, N = np.asarray(gun_kazanci, float), np.asarray(gun_n, int)
    n = int(N.sum()) if n is None else n
    if n == 0 or not np.isfinite(D).all():
        return dict(N=n, IG=None, SE_blok=None, z=None, p_tek=None, durum='belirsiz')
    ig = float(D.sum()/n)
    keys = [t.normalize()-pd.Timedelta(days=t.weekday()) for t in gunler]
    uniq = sorted(set(keys)); lookup = {k:i for i,k in enumerate(uniq)}
    di = np.zeros(len(uniq)); ni = np.zeros(len(uniq))
    for i, key in enumerate(keys):
        di[lookup[key]] += D[i]; ni[lookup[key]] += N[i]
    b = len(uniq)
    if n < 2 or b < 2:
        return dict(N=n, IG=ig, SE_blok=None, z=None, p_tek=None, blok_sayisi=b, durum='belirsiz')
    se = float(np.sqrt(b/(b-1)*np.sum((di-ig*ni)**2))/n)
    z = ig/se if se > 0 else (0. if ig == 0 else np.copysign(np.inf, ig))
    p = float(stats.norm.sf(z))
    return dict(N=n, IG=ig, SE_blok=se, z=float(z), p_tek=p, blok_sayisi=b,
                GA95=[ig-1.96*se, ig+1.96*se],
                durum='başarısızlık' if ig <= 0 else ('başarı' if z > 1.645 else 'belirsiz'))
