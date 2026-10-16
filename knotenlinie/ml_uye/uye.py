"""ML üyesi: eğitilmiş Poisson gradyan artırma → ortak model arayüzü (``beklenen``).

Model hücre-gün başına M>=3,1 olay oranı μ (olay/gün) verir. Büyüklük kutularına
dağılım GR ile: kutu payı 10^(-b(alt-Mc)) - 10^(-b(üst-Mc)), Mc=3,1, b R'nin
ayarından (GrUzat ile aynı biçim; M<3,1 kutuları da aynı yasayla uzar).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .ozellik import MC_ALT, OzellikHesap, gun_no

IZGARA_KUTU = (5.5, 19.5, 35.8, 47.9)   # lon0, lon1, lat0, lat1 (R kutusu); geçmiş süzgeci için


def kutu_payi(m_kenarlar, b, mc=MC_ALT):
    """GR kutu payı (Mc'den büyük olay başına); son kenar +inf olabilir."""
    e = np.asarray(m_kenarlar, float)
    ust = np.where(np.isinf(e[1:]), 0.0, 10.0 ** (-b * (e[1:] - mc)))
    return 10.0 ** (-b * (e[:-1] - mc)) - ust


def _utc(x):
    t = pd.Timestamp(x)
    if t.tzinfo is None:
        raise ValueError('Zaman UTC taşımalı')
    return t.tz_convert('UTC')


class MLUye:
    """Eğitilmiş HGB + sabit özellik kümesi; ``beklenen`` arayüzü.

    model     : predict(X) → μ (olay/gün) veren nesne
    kolonlar  : X sütun indeksleri (ML-saf: R'siz; ML-artık: R dahil)
    kde       : hücre başına arka plan log oranı (≤ayar verisinden, sabit)
    r_fn      : ML-artık için ``r_fn(a_timestamp)`` → (n,) R'nin M>=3,1 hücre-gün oranı (> 0)
    """

    def __init__(self, ad, model, kolonlar, hesap, kde, b, r_fn=None):
        self.ad, self.model, self.kolonlar = ad, model, list(kolonlar)
        self.hesap, self.kde, self.b, self.r_fn = hesap, np.asarray(kde, np.float32), float(b), r_fn
        self._pay = {}
        self.metadata = {}

    def mu(self, a, gecmis):
        """Gün başı a için hücre başına olay/gün; yalnız zaman < a olaylar kullanılır."""
        g = gecmis[pd.to_datetime(gecmis['zaman'], utc=True) < a]
        ol = self.hesap.olaylar(g)
        rlog = None
        if self.r_fn is not None:
            rlog = np.log(np.maximum(np.asarray(self.r_fn(a), float), 1e-12))
        X = self.hesap.hesapla(ol, gun_no(a), self.kde, rlog)
        return np.maximum(self.model.predict(X[:, self.kolonlar]), 1e-12)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = _utc(baslangic), _utc(bitis)
        sure = float((z - a) / pd.Timedelta(days=1))
        if sure <= 0 or sure > 1.0 + 1e-9:
            raise ValueError('ML üyesi günlük adım ister')
        key = tuple(np.round(np.asarray(m_kenarlar, float), 9))
        if key not in self._pay:
            self._pay[key] = kutu_payi(m_kenarlar, self.b)
        return (self.mu(a, gecmis) * sure)[:, None] * self._pay[key][None, :]
