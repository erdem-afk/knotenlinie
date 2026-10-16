"""STEP ayarı: genel Reasenberg–Jones, diziye özgü güncelleme, arka plan.

Genel model (Reasenberg ve Jones 1989): M'den büyük artçıların oranı
λ(t,M) = 10^(a+b(Mm-M)) (t+c)^-p. (a,b,p,c) tüm ayar dizilerinden, ana şok
büyüklüğüne kesilmiş (Mc..Mm) Poisson olabilirliğiyle birlikte kestirilir.
Diziye özgü güncelleme Gerstenberger ve ark. (2005) gibi: genel, yalnız-a,
(a,p) modelleri Akaike ağırlıklarıyla birleştirilir.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize, minimize_scalar

from .cekirdek import omori_integral

LN10 = np.log(10.0)
# Başlangıç ve sınırlar (KURAL.md)
SINIR = dict(a=(-4.0, 1.0), b=(0.6, 1.5), p=(0.6, 1.6), lc=(np.log(1e-4), np.log(1.0)))


def _veri(diziler, t_son, mc=0.0):
    """Dizilerden düz diziler: olay (t, M, Mm, dizi no) ve dizi (Mm, T_gözlem).

    Yalnız Mm > Mc olan diziler ve M >= Mc olan üyeler (Mc altı tamlık dışı)."""
    ev_t, ev_m, ev_mm, ev_i = [], [], [], []
    mm, tobs = [], []
    for s in diziler:
        if s.m <= mc + 1e-9:
            continue
        i = len(mm)
        mm.append(s.m)
        tobs.append(max(0.0, min(s.tgk, t_son - s.t)))
        for t, m in zip(s.uye_t, s.uye_m):
            if m < mc - 1e-9:
                continue
            ev_t.append(t)
            ev_m.append(m)
            ev_mm.append(s.m)
            ev_i.append(i)
    return (np.array(ev_t, float), np.array(ev_m, float), np.array(ev_mm, float),
            np.array(ev_i, int), np.array(mm, float), np.array(tobs, float))


def log_olabilirlik(theta, veri, mc):
    a, b, p, c = theta
    et, em, emm, _, mm, tobs = veri
    G = 10.0 ** (b * (mm - mc)) - 1.0
    I = omori_integral(0.0, tobs, c, p)
    lam_top = (10.0 ** a) * (G * I).sum()
    olay = (np.log(b * LN10) + (a + b * (emm - em)) * LN10 - p * np.log(et + c)).sum()
    return float(olay - lam_top)


def jenerik_kur(diziler, t_son, mc, baslangic=(-1.7, 0.96, 0.96, 0.01)):
    """Genel RJ parametreleri. t_son: ayar sonu (gün), gözlem penceresini keser."""
    veri = _veri(diziler, t_son, mc)
    if len(veri[0]) < 20:
        raise ValueError('Genel RJ için ayar dizilerinde yeterli artçı yok')
    x0 = np.array([baslangic[0], baslangic[1], baslangic[2], np.log(baslangic[3])])
    sinir = [SINIR['a'], SINIR['b'], SINIR['p'], SINIR['lc']]

    def f(x):
        return -log_olabilirlik((x[0], x[1], x[2], np.exp(x[3])), veri, mc)

    en = None
    for s in (x0, x0 + [0.3, -0.1, 0.1, 0.7], x0 + [-0.3, 0.1, -0.1, -0.7]):
        r = minimize(f, np.clip(s, [l for l, _ in sinir], [h for _, h in sinir]),
                     method='L-BFGS-B', bounds=sinir)
        if en is None or r.fun < en.fun:
            en = r
    a, b, p, lc = en.x
    return dict(a=float(a), b=float(b), p=float(p), c=float(np.exp(lc)), logL=float(-en.fun),
                n_dizi=len(veri[4]), n_uye=len(veri[0]), mc=float(mc), yakinsadi=bool(en.success),
                baslangic=list(baslangic))


def dizi_agirliklari(s, yas, jen, mc, n_min):
    """Akaike ağırlıklı [(w, a_k, p_k)]; genel, yalnız-a, (a,p).

    yas: gün başında dizinin yaşı (gözlem uzunluğu). n<n_min ise yalnız genel.
    """
    a0, b, p0, c = jen['a'], jen['b'], jen['p'], jen['c']
    ok = np.array(s.uye_m, float) >= mc - 1e-9
    n = int(ok.sum())
    genel = [(1.0, a0, p0)]
    if n < n_min or yas <= 0 or s.m <= mc + 1e-9:
        return genel
    t = np.array(s.uye_t, float)[ok]
    G = 10.0 ** (b * (s.m - mc)) - 1.0
    st = np.log(t + c).sum()

    def ll(a, p):
        return n * a * LN10 - p * st - (10.0 ** a) * G * float(omori_integral(0.0, yas, c, p))

    def a_en(p):
        return np.log10(n / (G * float(omori_integral(0.0, yas, c, p))))

    ll0 = ll(a0, p0)
    a1 = a_en(p0)
    ll1 = ll(a1, p0)
    r = minimize_scalar(lambda p: -ll(a_en(p), p), bounds=SINIR['p'], method='bounded',
                        options=dict(xatol=1e-4))
    p2 = float(r.x)
    a2 = a_en(p2)
    ll2 = ll(a2, p2)
    aic = np.array([-2 * ll0, 2 - 2 * ll1, 4 - 2 * ll2])
    w = np.exp(-0.5 * (aic - aic.min()))
    w /= w.sum()
    return [(float(w[0]), a0, p0), (float(w[1]), a1, p0), (float(w[2]), a2, p2)]


def arka_plan_kur(arka, epoch, n_gun, mc, kutu, son):
    """Atanamayan olaylardan arka plan: günlük oran, Aki b, KDE (T/R'nin arka_plan_sec'i)."""
    import pandas as pd
    from knotenlinie.ortak_zemin.arka_plan import arka_plan_sec
    if len(arka) < 50:
        raise ValueError('Arka plan için yeterli olay yok')
    d = pd.DataFrame(arka, columns=['t', 'boylam', 'enlem', 'mw'])
    d['zaman'] = epoch + pd.to_timedelta(d['t'], unit='D')
    mu = len(d) / float(n_gun)
    # Aki–Utsu, kutu genişliği 0,1 düzeltmeli
    b = float(np.log10(np.e) / (d['mw'].mean() - (mc - 0.05)))
    hist = arka_plan_sec(d, kutu, son)
    return dict(mu_gun=float(mu), b=b, n=len(d), hist=hist)


def arka_hucre(hist, g):
    """KDE histogramının hücre kütleleri (kutu içi toplam 1)."""
    xe, ye, yog = (np.asarray(hist[k], float) for k in ('x_kenar', 'y_kenar', 'yogunluk'))
    wx = np.maximum(0, np.minimum(g[:, 1, None], xe[None, 1:]) - np.maximum(g[:, 0, None], xe[None, :-1]))
    wy = np.maximum(0, np.minimum(g[:, 3, None], ye[None, 1:]) - np.maximum(g[:, 2, None], ye[None, :-1]))
    return np.einsum('ij,ij->i', wx @ yog, wy)
