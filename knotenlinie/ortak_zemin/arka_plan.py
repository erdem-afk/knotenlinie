"""Zamansal dış örneklemle seçilen Gauss KDE + açık düzgün kütle.

KDE km metriğinde izotropiktir. Her annenin Gauss'u kutuya koşullanır;
analitik CDF hücre integralleri 0.1° parça-sabit yoğunluğa çevrilir.
MLE'ye verilen u_olay ve tahmin integrali böylece aynı yüzeyi kullanır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.special import ndtr

from knotenlinie.etas import model as M
from .veri import AYAR_SON

BANTLAR_KM = (5., 10., 20., 40., 80.)
ZEMIN_PAYLARI = (0.001, 0.005, 0.01, 0.02, 0.05, 0.1)


def kde_histogram(x, y, kutu, bant_km, zemin_payi, dx=0.1, blok=128):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if (x.ndim != 1 or y.shape != x.shape or not len(x) or
            not np.isfinite(x).all() or not np.isfinite(y).all() or
            not np.isfinite(bant_km) or bant_km <= 0 or not 0 < zemin_payi < 1):
        raise ValueError('KDE girdisi/bant/zemin geçersiz')
    la0, la1, lo0, lo1 = kutu
    if ((x < lo0) | (x > lo1) | (y < la0) | (y > la1)).any():
        raise ValueError('KDE annesi kutu dışında')
    met = M.yerel_metrik(kutu)
    xe, ye = M.hucre_kenarlari(kutu, dx)
    mass = np.zeros((len(xe) - 1, len(ye) - 1))
    for a in range(0, len(x), blok):
        b = a + blok
        wx = np.diff(ndtr((xe[:, None] - x[None, a:b]) * met.kx / bant_km), axis=0)
        wy = np.diff(ndtr((ye[:, None] - y[None, a:b]) * met.ky / bant_km), axis=0)
        # Her annenin kutudaki kütlesi ayrı ayrı bir yapılır (sınır düzeltmesi).
        wx /= wx.sum(axis=0)
        wy /= wy.sum(axis=0)
        mass += wx @ wy.T
    mass /= len(x)
    area = np.diff(xe)[:, None] * np.diff(ye)[None, :]
    box_area = (lo1 - lo0) * (la1 - la0)
    density = (1 - zemin_payi) * mass / area + zemin_payi / box_area
    return {'x_kenar': xe, 'y_kenar': ye, 'yogunluk': density, 'dx': dx,
            'kutu': list(kutu), 'tur': 'Gauss-KDE + düzgün zemin',
            'bant_km': float(bant_km), 'zemin_payi': float(zemin_payi),
            'kde_n': len(x), 'kde_sinir': 'her Gauss kutuya koşullu',
            'yogunluk_birimi': 'derece^-2; analitik KDE kütlesinin parça-sabit temsili'}


def arka_plan_sec(d, kutu, son, *, bantlar=BANTLAR_KM, zeminler=ZEMIN_PAYLARI):
    """d zaten Mc üstü olmalı; son hariç, hiçbir ileri satır kabul edilmez.

    Son=2011: ≤2005 kurulum / 2006–2010 seçim / ≤2010 yeniden kurulum.
    Son=2006: aynı tasarımın iç katı ≤2000 / 2001–2005 / ≤2005;
    bileşenlerin 2006–2010 ağırlık ayarına hiperparametre sızdırmaz.
    """
    end = pd.Timestamp(son)
    if end.tzinfo is None:
        end = end.tz_localize('UTC')
    if end not in (pd.Timestamp('2006-01-01', tz='UTC'), AYAR_SON):
        raise ValueError('Yalnız 2006/2011 ayar sonu desteklenir')
    if d.empty or (d.zaman >= end).any():
        raise ValueError('KDE ayar verisi boş veya son sınırını aşıyor')
    split = end - pd.DateOffset(years=5)
    train, hold = d[d.zaman < split], d[d.zaman >= split]
    if train.empty or hold.empty:
        raise ValueError('KDE zamansal bölmelerinde olay yok')
    trials = []
    for h in bantlar:
        for eps in zeminler:
            hist = kde_histogram(train.boylam, train.enlem, kutu, h, eps)
            u = M.arka_plan_degeri(hold.boylam.to_numpy(), hold.enlem.to_numpy(), hist)
            trials.append({'bant_km': h, 'zemin_payi': eps,
                           'logL_konum': float(np.log(u / M.yerel_metrik(kutu).jakobiyen).sum())})
    # Sadece tutulmuş olay konumu olabilirliği; toplam kütle her adayda aynı.
    best = max(trials, key=lambda r: r['logL_konum'])
    hist = kde_histogram(d.boylam, d.enlem, kutu, best['bant_km'], best['zemin_payi'])
    hist['secim'] = {'kurulum_bitis_haric': split.isoformat(),
                     'secim_baslangic': split.isoformat(), 'secim_bitis_haric': end.isoformat(),
                     'kurulum_n': len(train), 'secim_n': len(hold), 'yeniden_kurulum_n': len(d),
                     'yeniden_kurulum_max_zaman': d.zaman.max().isoformat(),
                     'olcut': 'tutulmuş konumların sum log u_km; M≥Mc, zamanla ayrık',
                     'en_iyi': best, 'adaylar': trials}
    return hist
