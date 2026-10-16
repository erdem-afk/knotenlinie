"""Kümesizleştirme pencereleri: Gardner–Knopoff 1974, Uhrhammer 1986, Reasenberg 1985.

Pencere katsayıları van Stiphout, Zhuang ve Marsan (2012) derlemesindeki ve
`bruces` (keurfonluu) kodundaki standart biçimlerdir:

- Gardner–Knopoff (1974), Uhrhammer (1986) tarafından uydurulmuş sürekli pencere:
  dr = 10**(0.1238 m + 0.983) km; dt = 10**(0.032 m + 2.7389) gün (m >= 6.5),
  yoksa 10**(0.5409 m - 0.547) gün.
- Uhrhammer (1986): dr = exp(-1.024 + 0.804 m) km; dt = exp(-2.87 + 1.235 m) gün.
- Reasenberg (1985): örnek standart parametreler rfact=10, xk=0.5,
  tau_min=1 gün, tau_max=10 gün, p=0.95; xmeff verilmezse katalog en küçük Mw.

Pencere yöntemleri büyüklükçe azalan sırada işlenir ve zaman penceresi simetriktir
(öncü + artçı). Böylece en büyük olay ana şok olur, kendinden küçük komşuları
siler. Reasenberg küme büyütmesi ileriye bakışlıdır; `bruces` portu korunur.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

SUTUNLAR = ['zaman', 'enlem', 'boylam', 'derinlik', 'mw']
KM_ENLEM = 110.57
KM_BOYLAM = 111.32


class KumesizHatasi(ValueError):
    """Kümesizleştirme girdisi geçersiz."""


def yerel_km(enlem, boylam, *, merkez=None):
    """Bölge merkezine göre yerel düzlem; enlem/boylam derece, çıktı km."""
    la, lo = np.asarray(enlem, float), np.asarray(boylam, float)
    if merkez is None:
        la0, lo0 = float(np.mean(la)), float(np.mean(lo))
    else:
        la0, lo0 = float(merkez[0]), float(merkez[1])
    x = (lo - lo0) * KM_BOYLAM * np.cos(np.deg2rad(la0))
    y = (la - la0) * KM_ENLEM
    return x, y


def pencere(yontem, m):
    """(dt_gün, dr_km) dizileri; yalnız üç adlandırılmış yöntem."""
    m = np.asarray(m, float)
    if yontem in ('gk', 'gk74', 'gardner_knopoff'):
        dr = 10.0 ** (0.1238 * m + 0.983)
        dt = np.where(m >= 6.5, 10.0 ** (0.032 * m + 2.7389),
                      10.0 ** (0.5409 * m - 0.547))
        return dt, dr
    if yontem in ('uhr', 'uhrhammer', 'uhrhammer1986'):
        return np.exp(-2.87 + 1.235 * m), np.exp(-1.024 + 0.804 * m)
    raise KumesizHatasi(f'bilinmeyen pencere yöntemi: {yontem}')


def dogrula(katalog):
    k = katalog[SUTUNLAR].copy()
    k['zaman'] = pd.to_datetime(k['zaman'], utc=True)
    if k['zaman'].isna().any():
        raise KumesizHatasi('zaman eksik/geçersiz')
    x = k[['enlem', 'boylam', 'derinlik', 'mw']].to_numpy(float)
    if not np.isfinite(x).all():
        raise KumesizHatasi('koordinat/derinlik/mw sonlu olmalı')
    return k.sort_values('zaman', kind='stable').reset_index(drop=True)


def _mainshock_penceresi(k, yontem, simetrik):
    """Büyüklükçe azalan ana şok seçimi; arka plan maskesi döner."""
    t = (k['zaman'] - k['zaman'].iloc[0]).dt.total_seconds().to_numpy() / 86400.0
    la, lo, z, m = (k['enlem'].to_numpy(float), k['boylam'].to_numpy(float),
                    k['derinlik'].to_numpy(float), k['mw'].to_numpy(float))
    x, y = yerel_km(la, lo)
    n = len(k)
    if n == 0:
        return np.zeros(0, bool)
    dt, dr = pencere(yontem, m)
    agac = cKDTree(np.column_stack([x, y]))
    silindi = np.zeros(n, bool)
    for i in np.argsort(-m, kind='stable'):
        if silindi[i]:
            continue
        idx = np.asarray(agac.query_ball_point([x[i], y[i]], float(dr[i])), int)
        if idx.size == 0:
            continue
        idx = idx[idx != i]
        if idx.size == 0:
            continue
        fark = t[idx] - t[i]
        if simetrik:
            zaman_ok = np.abs(fark) < dt[i]
        else:
            zaman_ok = (fark > 0) & (fark < dt[i])
        dx = x[idx] - x[i]
        dy = y[idx] - y[i]
        dz = z[idx] - z[i]
        uzak_ok = np.sqrt(dx * dx + dy * dy + dz * dz) < dr[i]
        sec = zaman_ok & uzak_ok & (m[idx] < m[i]) & (~silindi[idx])
        silindi[idx[sec]] = True
    return ~silindi


def reasenberg(katalog, *, rfact=10, xmeff=None, xk=0.5, tau_min=1.0,
               tau_max=10.0, p=0.95):
    """Reasenberg (1985) ileriye bakışlı küme büyütmesi; arka plan maskesi."""
    k = dogrula(katalog)
    if not (tau_min > 0 and tau_min <= tau_max and 0 < p < 1 and rfact > 0):
        raise KumesizHatasi('Reasenberg parametreleri geçersiz')
    t = (k['zaman'] - k['zaman'].iloc[0]).dt.total_seconds().to_numpy() / 86400.0
    la, lo, z, m = (k['enlem'].to_numpy(float), k['boylam'].to_numpy(float),
                    k['derinlik'].to_numpy(float), k['mw'].to_numpy(float))
    x, y = yerel_km(la, lo)
    n = len(k)
    if n == 0:
        return np.zeros(0, bool)
    xmeff = float(np.min(m)) if xmeff is None else float(xmeff)
    rmain = 0.011 * 10.0 ** (0.4 * m)
    kume = np.full(n, -1, np.int64)
    kume_ana = np.full(n, -1, np.int64)
    n_kume = 0

    def uzaklik(i, j):
        return np.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2 + (z[i] - z[j]) ** 2)

    for i in range(n - 1):
        if kume[i] < 0:
            tau = tau_min
            ana = i
        else:
            ana = int(kume_ana[kume[i]])
            cmag = m[ana]
            if m[i] > cmag:
                ana = i
                kume_ana[kume[i]] = i
                tau = tau_min
            else:
                tdif = t[i] - t[ana]
                deltam = (1.0 - xk) * cmag - xmeff
                denom = 10.0 ** ((max(deltam, 0.0) - 1.0) * 2.0 / 3.0)
                tau = -np.log(1.0 - p) * tdif / denom
                tau = min(max(tau, tau_min), tau_max)
        # İleri penceredeki adayları önce topla; pahalı uzaklık dış döngüde.
        j0 = i + 1
        j1 = j0
        while j1 < n and t[j1] - t[i] < tau:
            j1 += 1
        if j1 <= j0:
            continue
        idx = np.arange(j0, j1)
        d1 = np.sqrt((x[idx] - x[i]) ** 2 + (y[idx] - y[i]) ** 2 + (z[idx] - z[i]) ** 2)
        r1 = rfact * rmain[i]
        cond1 = d1 < r1
        if tau > tau_min:
            d2 = np.sqrt((x[idx] - x[ana]) ** 2 + (y[idx] - y[ana]) ** 2
                         + (z[idx] - z[ana]) ** 2)
            cond2 = d2 < rmain[ana]
        else:
            cond2 = np.zeros(len(idx), bool)
        for kpos, j in enumerate(idx):
            if kume[i] >= 0 and kume[j] == kume[i]:
                continue
            if not (cond1[kpos] or cond2[kpos]):
                continue
            id1, id2 = kume[i], kume[j]
            if id1 >= 0 and id2 >= 0:
                if t[i] < t[j]:
                    c1, c2 = id1, id2
                else:
                    c1, c2 = id2, id1
                kume[kume == c2] = c1
                if m[kume_ana[c1]] > m[kume_ana[c2]]:
                    kume_ana[c1] = kume_ana[c2]
                else:
                    kume_ana[c2] = kume_ana[c1]
            elif id1 >= 0:
                kume[j] = id1
                if m[j] > m[kume_ana[id1]]:
                    kume_ana[id1] = j
            elif id2 >= 0:
                kume[i] = id2
                if m[i] > m[kume_ana[id2]]:
                    kume_ana[id2] = i
            else:
                kume[i] = n_kume
                kume[j] = n_kume
                kume_ana[n_kume] = i if m[i] > m[j] else j
                n_kume += 1
    arka = np.ones(n, bool)
    for i in range(n):
        if kume[i] >= 0 and int(kume_ana[kume[i]]) != i:
            arka[i] = False
    return arka


def arka_plan_maskesi(katalog, yontem='gk74', *, simetrik=True):
    """Arka plan (kümesiz) maskesi; katalog zamana göre sıralı döner."""
    k = dogrula(katalog)
    y = yontem.lower()
    if y in ('reasenberg', 'reasenberg1985'):
        return k, reasenberg(k)
    return k, _mainshock_penceresi(k, yontem, simetrik)


def kumesizlestir(katalog, yontem='gk74', *, simetrik=True):
    """Kümesizleştirilmiş katalog (yalnız bağımsız olaylar)."""
    k, maske = arka_plan_maskesi(katalog, yontem, simetrik=simetrik)
    return k[maske].reset_index(drop=True)
