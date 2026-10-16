"""Eğitim kümesi (ağırlıklı alt örnekleme) ve HistGradientBoosting uyumu."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .ozellik import EPOCH, MC_ALT, gun_no


def hedef_olaylari(hesap, cat, d0, d1):
    """[d0,d1) gün aralığında M>=3,1, derinlik [0,30), ızgara içi olaylar → (gun, hucre)."""
    z = pd.to_datetime(cat['zaman'], utc=True)
    t = gun_no(z)
    s = ((cat['mw'].to_numpy(float) >= MC_ALT - 1e-6) & (cat['derinlik'].to_numpy(float) >= 0) &
         (cat['derinlik'].to_numpy(float) < 30) & (t >= d0) & (t < d1))
    d = cat[s]
    h = hesap.hucre_kutu(d['enlem'].to_numpy(float), d['boylam'].to_numpy(float))
    g = np.floor(t[s]).astype(int)
    k = h >= 0
    return g[k], h[k]


def egitim_gunleri(poz_gun, d0, d1, p_gun, tohum):
    """Olay günleri ∪ rastgele p_gun payı; (günler, örnekleme_bayrağı)."""
    rng = np.random.default_rng(tohum)
    orn = rng.random(d1 - d0) < p_gun
    gunler = np.union1d(np.unique(poz_gun), d0 + np.flatnonzero(orn))
    bay = np.zeros(len(gunler), bool)
    bay[np.isin(gunler, d0 + np.flatnonzero(orn))] = True
    return gunler.astype(int), bay


def yil_mod(gun, mod=4):
    return (EPOCH + pd.to_timedelta(gun, unit='D')).year % mod


def egitim_kumesi(hesap, ol, poz_gun, poz_hucre, gunler, bayrak, kde_kat, r_orani,
                  p_gun, q_hucre, tohum, mod=4):
    """Pozitifler (ağırlık 1) + örnek günlerde sıfır hücrelerin q payı (ağırlık 1/(p q)).

    kde_kat : {kat: KDE vektörü}; satırın yıl%mod katı için o katın dışlamalı KDE'si.
    r_orani : (len(gunler), n) R oranı ya da None.
    """
    rng = np.random.default_rng(tohum + 1)
    gsira = {int(g): i for i, g in enumerate(gunler)}
    say = {}
    for g, h in zip(poz_gun, poz_hucre):
        say.setdefault(int(g), {}).setdefault(int(h), 0)
        say[int(g)][int(h)] += 1
    Xs, ys, ws, gs, hs = [], [], [], [], []
    for i, g in enumerate(gunler):
        kat = int(yil_mod(np.array([g]), mod)[0])
        rlog = None if r_orani is None else np.log(np.maximum(r_orani[i].astype(float), 1e-12))
        X = hesap.hesapla(ol, float(g), kde_kat[kat], rlog)
        pos = say.get(int(g), {})
        ph = np.array(sorted(pos), int)
        yy = np.array([pos[h] for h in ph], float)
        sel_h, sel_y, sel_w = [ph], [yy], [np.ones(len(ph))]
        if bayrak[i]:
            sifir = np.ones(hesap.n, bool)
            sifir[ph] = False
            zi = np.flatnonzero(sifir & (rng.random(hesap.n) < q_hucre))
            sel_h.append(zi)
            sel_y.append(np.zeros(len(zi)))
            sel_w.append(np.full(len(zi), 1.0 / (p_gun * q_hucre)))
        h = np.concatenate(sel_h)
        if len(h):
            Xs.append(X[h])
            ys.append(np.concatenate(sel_y))
            ws.append(np.concatenate(sel_w))
            gs.append(np.full(len(h), g))
            hs.append(h)
    return (np.vstack(Xs).astype(np.float32), np.concatenate(ys).astype(np.float32),
            np.concatenate(ws), np.concatenate(gs), np.concatenate(hs))


def egit(X, y, w, kolonlar, cfg, tohum=20261012):
    from sklearn.ensemble import HistGradientBoostingRegressor
    m = HistGradientBoostingRegressor(
        loss='poisson', learning_rate=cfg['lr'], max_iter=cfg['iter'], max_leaf_nodes=cfg['yaprak'],
        min_samples_leaf=cfg['min_yaprak'], l2_regularization=cfg.get('l2', 1.0),
        early_stopping=False, random_state=tohum)
    # Ağırlıklar ortalama 1'e ölçeklenir: ham 1/(p q) ağırlıklarıyla Poisson Newton adımı
    # (küçük hessian) salınıp kalibrasyonu bozdu (ön deneme: Σw·μ/Σw·y = 5x); ölçekli
    # halde 0,98-1,00. Sabit nokta değişmez, yalnız l2'nin göreli ağırlığı.
    m.fit(X[:, list(kolonlar)], y, sample_weight=w / w.mean())
    return m
