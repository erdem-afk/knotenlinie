"""Kaliforniya verisi: HKJ07 tahmin dosyaları, RELM ızgarası ve ComCat kataloğu.

HKJ07 dosya biçimi (pyCSEP `*-fromXML.dat`): her satır bir hücre×kutu; sütunlar
boylam_min, boylam_max, enlem_min, enlem_max, derinlik_min, derinlik_max, m_min, m_max,
beklenen_sayi (5 yıllık), maske. Satırlar hücre-büyük, kutu-küçük sıralıdır (41 kutu).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.yollar import VERI as _KOK  # noqa: E402

VERI = _KOK / 'kaliforniya'
HKJ_ANA = VERI / 'hkj07/helmstetter_et_al.hkj-fromXML.dat'
HKJ_ARTCI = VERI / 'hkj07/helmstetter_et_al.hkj.aftershock-fromXML.dat'
HKJ_YIL = 5.0
M_KENAR = np.r_[np.round(np.arange(4.95, 9.0, 0.1), 2), np.inf]   # 40 kutu + [8.95, +inf)
IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']
DERINLIK = (0.0, 30.0)
SON_YIL = 2020


class VeriHatasi(ValueError):
    """Girdi dosyası beklenen biçimde değil."""


def hkj_oku(yol):
    """(izgara DataFrame, beklenen [hücre, 41 kutu]) döner; 5 yıllık sayılar."""
    a = np.loadtxt(yol)
    if a.ndim != 2 or a.shape[1] != 10 or len(a) % 41:
        raise VeriHatasi('HKJ07 dosyası 10 sütun ve 41 kutu katı satır olmalı')
    n = len(a) // 41
    b = a.reshape(n, 41, 10)
    if not (np.allclose(b[:, :, 6], b[0, :, 6]) and np.allclose(b[:, :, 0], b[:, :1, 0])
            and np.allclose(b[:, :, 2], b[:, :1, 2])):
        raise VeriHatasi('satır sırası hücre-büyük/kutu-küçük değil')
    if not np.allclose(b[0, :, 6], np.round(np.arange(4.95, 9.0, 0.1), 2)[:40].tolist() + [8.95], atol=1e-6) and \
            not np.allclose(b[0, :40, 6], np.round(np.arange(4.95, 8.95, 0.1), 2), atol=1e-6):
        raise VeriHatasi('kutu kenarları 4.95 + 0.1 k değil')
    izgara = pd.DataFrame({'boylam_min': b[:, 0, 0], 'boylam_max': b[:, 0, 1],
                           'enlem_min': b[:, 0, 2], 'enlem_max': b[:, 0, 3]})
    if (b[:, :, 4] != 0).any() or (b[:, :, 5] != 30).any():
        raise VeriHatasi('derinlik katmanı [0,30) değil')
    if not (b[:, :, 9] == 1).all():
        raise VeriHatasi('maske 1 olmayan hücre var')
    return izgara.round(6), b[:, :, 8].astype(float)


def katalog_oku(klasor=VERI / 'deprem', *, ilk=1981, son=SON_YIL):
    """ComCat yıllık CSV'leri; sütunlar zaman, enlem, boylam, derinlik, mw. 2021+ reddedilir."""
    parcalar = []
    for yil in range(ilk, son + 1):
        yol = Path(klasor) / f'comcat_{yil}.csv'
        if not yol.exists():
            raise VeriHatasi(f'eksik yıl dosyası: {yol.name}')
        d = pd.read_csv(yol, usecols=['time', 'latitude', 'longitude', 'depth', 'mag', 'type'])
        parcalar.append(d)
    d = pd.concat(parcalar, ignore_index=True)
    d = d[d['type'] == 'earthquake'].dropna(subset=['mag', 'depth', 'latitude', 'longitude'])
    d['zaman'] = pd.to_datetime(d['time'], utc=True, format='ISO8601')
    if (d['zaman'] >= pd.Timestamp('2021-01-01', tz='UTC')).any():
        raise VeriHatasi('2021+ satır: mühür ihlali, dosya reddedildi')
    d = d.rename(columns={'latitude': 'enlem', 'longitude': 'boylam', 'depth': 'derinlik', 'mag': 'mw'})
    d = d[['zaman', 'enlem', 'boylam', 'derinlik', 'mw']].sort_values('zaman', kind='stable')
    return d.reset_index(drop=True)


def yil_ondalik(zaman):
    """UTC zamanlarından ondalık yıl (yıl + yıl içi kesir)."""
    z = pd.to_datetime(pd.Series(zaman), utc=True).dt.tz_localize(None)
    y0 = z.dt.year.astype(str).radd('') + '-01-01'
    bas = pd.to_datetime(y0)
    son = pd.to_datetime((z.dt.year + 1).astype(str) + '-01-01')
    return (z.dt.year + (z - bas).dt.total_seconds() / (son - bas).dt.total_seconds()).to_numpy(float)
