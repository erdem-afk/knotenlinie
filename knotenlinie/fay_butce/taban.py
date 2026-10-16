"""GEAR1 gelene kadar açıkça adlandırılmış, sabit tarihli sismisite tabanı."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .butce import gauss_kutular, izgara_dogrula, kenarlar_dogrula, YIL_SANIYE
from .skor import AYAR_SON


class Duzlestirilmis:
    """Eğitim olaylarıyla Gauss KDE; küresel kuyruk korunur, b sabittir."""

    def __init__(self, egitim, *, baslangic, bitis, sigma_km=30, b=1, mmin=4.95):
        bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
        if bas.tzinfo is None or son.tzinfo is None or not bas < son <= AYAR_SON:
            raise ValueError('taban eğitimi yalnız ≤2010')
        t = pd.to_datetime(egitim['zaman'], utc=True)
        if ((t < bas) | (t >= son) | t.isna()).any() or len(egitim)==0:
            raise ValueError('taban olayları eğitim aralığı dışında/boş')
        if b <= 0 or not np.isfinite(b) or not np.isfinite(mmin) or (egitim['mw']<mmin).any():
            raise ValueError('b/eşik/eğitim büyüklüğü geçersiz')
        self.noktalar = egitim[['boylam','enlem']].to_numpy(float)
        self.yil = (son-bas).total_seconds()/YIL_SANIYE
        self.sigma_km, self.b, self.mmin = sigma_km, b, mmin
        self._cache = None

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
        if bas.tzinfo is None or son.tzinfo is None or son < bas:
            raise ValueError('zaman aralığı geçersiz')
        a, k = izgara_dogrula(izgara), kenarlar_dogrula(m_kenarlar)
        key = a.tobytes()
        if self._cache is None or self._cache[0] != key:
            uzay = gauss_kutular(self.noktalar, np.ones(len(self.noktalar)), a,
                                self.sigma_km, dogrulanmis=True)/self.yil
            # Bölgeye koşullu değil; 1e-3 olay payı düzgün alan öncülü.
            alan = (np.deg2rad(a[:,1]-a[:,0]) *
                    (np.sin(np.deg2rad(a[:,3]))-np.sin(np.deg2rad(a[:,2]))))
            uzay = (1-1e-3)*uzay + 1e-3*(len(self.noktalar)/self.yil)*alan/alan.sum()
            self._cache = (key, uzay)
        alt, ust = np.maximum(k[:-1],self.mmin), np.maximum(k[1:],self.mmin)
        mag = 10**(-self.b*(alt-self.mmin))-10**(-self.b*(ust-self.mmin))
        return self._cache[1][:,None]*mag[None,:]*((son-bas).total_seconds()/YIL_SANIYE)
