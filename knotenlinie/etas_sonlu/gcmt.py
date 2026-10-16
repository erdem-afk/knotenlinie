"""Bölgesel GCMT <=2015 okuyucusu: merkez zamanı, iki düğüm düzlemi.

`knotenlinie/etas_sonlu/ndk.py` NDK ayrıştırıcısını kullanır (tarih/saat kapısı ve
`_kayit_ayristir`); yalnız <=2015 satırları okunur ve 2016+ satır adıyla reddedilir.  Mühür
(2021-01-01) zaten dosyanın kesiminde; yine de yıl öneki denetlenir.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.etas_sonlu.ndk import _kayit_ayristir, _saat_coz, _tarih_coz

#: Okunacak en son an (kesim dosyası 2015 sonuna kadar).
KESIM = pd.Timestamp('2016-01-01', tz='UTC')
#: Mühür başlangıcı; bu okuyucu hiçbir koşulda geçmez.
MUHUR = pd.Timestamp('2021-01-01', tz='UTC')

KOLONLAR = ['olay_adi', 'zaman', 'merkez_zaman', 'enlem', 'boylam', 'derinlik', 'mw',
            'dogrultu1', 'egim1', 'kayma1', 'dogrultu2', 'egim2', 'kayma2']


def oku(yol, *, kesim=KESIM):
    """NDK dosyasını oku; `kesim` sonrası ya da 2016+ satır varsa dur.

    Dönüş: her kayıt için bir satır (`KOLONLAR`).  `enlem`, `boylam`, `derinlik`
    line 1'in hiposantır alanlarıdır (eşleştirme için), düğüm düzlemleri line 5'ten.
    """
    lines = Path(yol).read_text(encoding='latin-1').splitlines()
    if len(lines) % 5:
        raise ValueError('GCMT NDK beş satırlı değil')
    times = []
    for i in range(0, len(lines), 5):
        d = _tarih_coz(lines[i])
        if d is None:
            raise ValueError('GCMT: line-1 tarihi çözülemedi')
        if d.year >= 2016:
            raise ValueError('GCMT: 2016+ satır; kapı kapalı')
        if d.year >= 2021:
            raise ValueError('GCMT: mühür ihlali')
        t = _saat_coz(lines[i], d)
        if t is None or t >= kesim:
            raise ValueError('GCMT: geçersiz ya da kesim sonrası zaman')
        times.append(t)
    rows = []
    for j, t in enumerate(times):
        i = j * 5
        rec = _kayit_ayristir(lines[i:i + 5], i + 1, t, False)
        rows.append([rec['olay_adi'], t, rec['merkez_zaman_utc'],
                     float(lines[i][27:33]), float(lines[i][34:41]), float(lines[i][42:47]),
                     rec['Mw'], rec['dogrultu1'], rec['egim1'], rec['kayma1'],
                     rec['dogrultu2'], rec['egim2'], rec['kayma2']])
    df = pd.DataFrame(rows, columns=KOLONLAR)
    df['zaman'] = pd.to_datetime(df['zaman'], utc=True)
    df['merkez_zaman'] = pd.to_datetime(df['merkez_zaman'], utc=True)
    return df.sort_values('zaman', kind='stable').reset_index(drop=True)


def esles(df, zaman, boylam, enlem, *, zaman_tol_s=60.0, uzaklik_km=50.0,
          merkez_once=None):
    """`zaman +- zaman_tol_s` ve `uzaklik_km` icinde en yakin cozumu dondurur.

    `merkez_once` verilirse yalniz merkez zamanı ondan once olan cozumler kabul
    edilir (nedensellik).  Aday zamana gore en yakini, esitlikte en yakın uzaklik.
    Yoksa `None`.
    """
    if df is None or not len(df):
        return None
    lo = zaman - pd.Timedelta(seconds=float(zaman_tol_s))
    hi = zaman + pd.Timedelta(seconds=float(zaman_tol_s))
    ad = df[(df.zaman >= lo) & (df.zaman <= hi)]
    if merkez_once is not None:
        ad = ad[ad.merkez_zaman < merkez_once]
    if not len(ad):
        return None
    p = np.radians(enlem)
    q = np.radians(ad.enlem.to_numpy(float))
    dlon = np.radians(ad.boylam.to_numpy(float) - boylam)
    h = np.sin((q - p) / 2) ** 2 + np.cos(p) * np.cos(q) * np.sin(dlon / 2) ** 2
    km = 6371.0088 * 2 * np.arcsin(np.sqrt(np.clip(h, 0, 1)))
    ad = ad.assign(km=km)
    ad = ad[ad.km <= float(uzaklik_km)]
    if not len(ad):
        return None
    dt = np.abs((ad.zaman - zaman).dt.total_seconds().to_numpy(float))
    order = np.lexsort((ad.km.to_numpy(float), dt))
    return ad.iloc[int(order[0])]
