"""Denklem 3: sabit tetikleme altında iteratif Gaussian declustering."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.special import ndtr

from knotenlinie.karsilastir.kosucu import katalog_kontrol, utc
from knotenlinie.ortak_zemin.veri import IZGARA
from knotenlinie.etas.model import yerel_metrik
from .cekirdek import MC, P, C, D, uretkenlik, YIL

BAS = pd.Timestamp('2005-04-16', tz='UTC')
SON = pd.Timestamp('2011-01-01', tz='UTC')


def km_izgara(izgara, metrik):
    g = izgara[IZGARA].to_numpy(float)
    return np.column_stack([metrik.km(g[:, 0], g[:, 2])[0], metrik.km(g[:, 1], g[:, 3])[0],
                            metrik.km(g[:, 0], g[:, 2])[1], metrik.km(g[:, 1], g[:, 3])[1]])


def kur(katalog, izgara, *, son=SON, komsu=10, alt_bant=1.1, maksiter=200, tolerans=1e-6):
    """Yalnız ≤2010 kaynak; mu dahil arka-plan Eq3 ile yeniden kurulur.

    LM bant komşu sayısını/minimumunu yayımlamaz. 10/1.1km açık varsayım,
    doğrulama olaylarından seçilmez. Tetikleme parametreleri asla optimize edilmez.
    """
    end = utc(son)
    if not BAS < end <= SON or komsu < 1 or int(komsu) != komsu or alt_bant <= 0:
        raise ValueError('Arka-plan ayarı ≤2010 olmalı; bant geçersiz')
    raw = katalog_kontrol(katalog)
    if (raw.zaman >= end).any():
        raise ValueError('Arka-plan çağrısında ayar sonrası veri var')
    k = raw[(raw.zaman >= BAS) & (raw.mw >= MC) & (raw.derinlik >= 0) & (raw.derinlik < 30)].reset_index(drop=True)
    if len(k) <= komsu:
        raise ValueError('KDE için yeterli kaynak yok')
    g = izgara[IZGARA].to_numpy(float)
    met = yerel_metrik((g[:, 2].min(), g[:, 3].max(), g[:, 0].min(), g[:, 1].max()))
    x, y = met.km(k.boylam.to_numpy(float), k.enlem.to_numpy(float))
    xy = np.column_stack([x, y])
    bandwidth = np.maximum(cKDTree(xy).query(xy, k=komsu+1)[0][:, -1], alt_bant)
    duration = float((end-BAS) / pd.Timedelta(days=1))
    time = ((k.zaman-BAS) / pd.Timedelta(days=1)).to_numpy(float)
    # n<=3000; iki n×n matris <160MB. Aynı zamanlı olaylar tetiklemez.
    r2 = (x[:, None]-x[None, :])**2 + (y[:, None]-y[None, :])**2
    gaussian = np.exp(-r2 / (2*bandwidth[None, :]**2)) / (2*np.pi*bandwidth[None, :]**2)
    age = time[:, None]-time[None, :]
    trigger = np.where(age > 0, (np.maximum(age, 0)+C)**(-P), 0)
    trigger *= D/(2*np.pi*(r2+D*D)**1.5) * uretkenlik(k.mw.to_numpy(float))[None, :]
    trig = trigger.sum(axis=1)
    weights = np.ones(len(k))
    delta = None
    for iteration in range(1, maksiter+1):
        bg = np.einsum('ij,j->i', gaussian, weights, optimize=False) / duration
        new = bg / (bg+trig)
        delta = float(np.max(np.abs(new-weights)))
        weights = new
        if delta < tolerans:
            break
    if delta >= tolerans:
        raise ValueError('Arka-plan iterasyonu yakınsamadı')
    grid_km = km_izgara(izgara, met)
    cell = np.zeros(len(grid_km))
    for j in range(len(k)):
        sx = ndtr((grid_km[:, 1]-x[j])/bandwidth[j])-ndtr((grid_km[:, 0]-x[j])/bandwidth[j])
        sy = ndtr((grid_km[:, 3]-y[j])/bandwidth[j])-ndtr((grid_km[:, 2]-y[j])/bandwidth[j])
        cell += weights[j] * sx*sy / duration
    metadata = dict(ayar_baslangic=BAS.isoformat(), ayar_bitis=end.isoformat(), ayar_max_zaman=k.zaman.max().isoformat(),
                    N=len(k), komsu=komsu, alt_bant_km=alt_bant, bant_km_min=float(bandwidth.min()),
                    bant_km_medyan=float(np.median(bandwidth)), iterasyon=iteration, son_fark=delta,
                    arka_plan_payi=float(weights.mean()), mu_yil=float(weights.sum()/duration*YIL),
                    maske_mu_yil=float(cell.sum()*YIL), metrik=met.kayit(),
                    normalizasyon='Gaussian düzlemde bir; maskenin dışına taşan kütle kayıp, floor yok')
    return cell, met, metadata
