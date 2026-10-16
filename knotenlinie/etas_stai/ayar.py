"""Deney W: R kurulumunun (maske, KDE, b, Mc basamağı) üstüne ETAS+STAI birlikte MLE."""
from __future__ import annotations

import time

import numpy as np
import pandas as pd

from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.arayuz import ebeveynler
from knotenlinie.ortak_zemin.arayuz import utc
from knotenlinie.ortak_zemin.veri import hucre_indeks
from .mle import Olabilirlik, ayarla
from .tamlik import KisaTamlik, HKJ_M_ESIK

EPOCH = '1985-01-01T00:00:00Z'
KIRILMA_TARIH = '2005-01-01T00:00:00Z'


def _hist(r_fit):
    h = dict(r_fit['arka_plan'])
    for k in ('x_kenar', 'y_kenar', 'yogunluk'):
        h[k] = np.asarray(h[k], float)
    return h


def hazirla(r_fit, raw, grid, son, tur):
    """R kurulumunun aynı veri/ağırlık yapısını kurar; (L, d, stai) döner."""
    end, epoch = utc(son), utc(EPOCH)
    box = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    if not np.allclose(box, r_fit['kutu']):
        raise ValueError('R kurulumunun kutusu ızgarayla uyuşmuyor')
    d = ebeveynler(raw, box, end)
    if len(d) != r_fit['ayar_n']:
        raise ValueError(f"ebeveyn sayısı R kurulumundan farklı: {len(d)} != {r_fit['ayar_n']}")
    t = ((d.zaman - epoch) / pd.Timedelta(days=1)).to_numpy(float)
    T = float((end - epoch) / pd.Timedelta(days=1))
    kirilma = float((utc(KIRILMA_TARIH) - epoch) / pd.Timedelta(days=1))
    b = float(r_fit['b']['deger'])
    u = M.arka_plan_degeri(d.boylam.to_numpy(), d.enlem.to_numpy(), _hist(r_fit))
    big = d[d.mw >= HKJ_M_ESIK]
    bt = ((big.zaman - epoch) / pd.Timedelta(days=1)).to_numpy(float)
    stai = KisaTamlik(tur, kirilma, b, bt, big.mw.to_numpy(float), T)
    L = Olabilirlik(t, d.mw.to_numpy(), d.boylam.to_numpy(), d.enlem.to_numpy(), b, T, kirilma,
                    grid, box, u, stai)
    return L, d, stai


def kur(r_fit, raw, grid, son, tur, *, maksiter=200, theta0=None):
    """``r_fit``: R'nin aynı ayar penceresindeki JSON'u (başlangıç ve b/KDE kaynağı)."""
    basla = time.monotonic()
    L, d, stai = hazirla(r_fit, raw, grid, son, tur)
    th_r = {k: float(r_fit['parametreler'][k]) for k in M.UZAY_ADLARI}
    ll_r_w = L.deger(th_r, False, None)  # W olabilirliğinin R parametresindeki değeri
    fit = ayarla(L, th_r, theta0=theta0, maksiter=maksiter)
    out = {k: v for k, v in r_fit.items()}
    for eski in ('x', 'sinirlar'):
        out.pop(eski, None)
    out.update(fit)
    out.update(
        R_logL=float(r_fit['logL']), W_logL_R_parametresinde=float(ll_r_w),
        stai=stai.kayit(fit['stai_theta']),
        W_kurulum=dict(son=son, hedef_n=int(L.nhedef), ebeveyn_n=int(len(d)),
                       duvar_saniye=time.monotonic() - basla,
                       not_='ETAS+STAI birlikte; başlangıç R çözümü; R\'nin b, KDE, maske ve Mc basamağı aynen'))
    return out, L
