"""Doğrusal topluluk ve sabit ölçek; defterden logL, gün kazancı, blok SE.

Bütün büyüklükler yalnız defterlerden hesaplanır; model yeniden koşmaz. λ_k
olay başına, Lam_k gün başına toplamdır. Karışım λ = Σ w_k c_k λ_k ve
Λ = Σ w_k c_k Λ_k; logL farkında log(n!) terimi (gözlemden gelir) düşer.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln

from knotenlinie.karsilastir.puan import PuanHatasi
from .defter import Defter, alt_sutun


def _esik_mask(defter, alt):
    return defter.olay['mw'].to_numpy(float) >= float(alt) - 1e-9


def _dogrula(defterler):
    if not defterler:
        raise PuanHatasi('Boş defter listesi')
    ref = defterler[0]
    for d in defterler[1:]:
        if not (np.array_equal(ref.olay['zaman'].to_numpy(), d.olay['zaman'].to_numpy()) and
                np.array_equal(ref.olay['hucre'].to_numpy(), d.olay['hucre'].to_numpy()) and
                np.array_equal(ref.olay['kutu'].to_numpy(), d.olay['kutu'].to_numpy()) and
                np.allclose(ref.olay['mw'].to_numpy(float), d.olay['mw'].to_numpy(float), atol=1e-9)):
            raise PuanHatasi('Defterler aynı hedef dizisini taşımıyor')
        if not np.array_equal(ref.gun['gun'].to_numpy(), d.gun['gun'].to_numpy()):
            raise PuanHatasi('Defterler aynı takvim günlerini taşımıyor')
    return ref


def _lam_matris(defterler):
    return np.vstack([d.lam() for d in defterler])


def _gun_vektoru(defter, alt):
    kol = alt_sutun(alt)
    return defter.gun[kol].to_numpy(float)


def _gunler(defter):
    return [pd.Timestamp(x) for x in defter.gun['gun'].astype(str)]


def bilesen(defterler, agirliklar, alt, olcekler=None):
    """Karışımın olay-başı λ'sı ve gün-başı Λ'sı."""
    defterler = list(defterler)
    ref = _dogrula(defterler)
    W = np.asarray(agirliklar, float)
    if W.shape != (len(defterler),) or (W < 0).any() or not np.isfinite(W).all():
        raise PuanHatasi('Ağırlıklar negatif olmayan ve model sayısı kadar olmalı')
    C = np.ones(len(defterler)) if olcekler is None else np.asarray(olcekler, float)
    if C.shape != W.shape or (C <= 0).any() or not np.isfinite(C).all():
        raise PuanHatasi('Ölçekler pozitif ve model sayısı kadar olmalı')
    lam_olay = (W * C) @ _lam_matris(defterler)
    Lam_gun = sum(w * c * _gun_vektoru(d, alt) for w, c, d in zip(W, C, defterler))
    return lam_olay, np.asarray(Lam_gun, float), _esik_mask(ref, alt)


def log_olabilirlik(defterler, agirliklar, alt, olcekler=None):
    """Karışımın Poisson logL'si (log(n!) dahil), yalnız defterden."""
    lam_olay, Lam_gun, mask = bilesen(defterler, agirliklar, alt, olcekler)
    ref = defterler[0]
    key = (ref.olay.loc[mask, 'gun'].astype(str) + '|' + ref.olay.loc[mask, 'hucre'].astype(str)
           + '|' + ref.olay.loc[mask, 'kutu'].astype(str))
    _, say = np.unique(key.to_numpy(), return_counts=True)
    if (lam_olay[mask] <= 0).any():
        return -np.inf
    return float(np.log(lam_olay[mask]).sum() - Lam_gun.sum() - gammaln(say + 1).sum())


def gun_kazanci(defterler, taban, alt, agirliklar=None, olcekler=None):
    """Aday karışım − taban: gün başına kazanç D_i, olay sayısı n_i, IG.

    D_i = Σ_{olay∈gün i, M≥alt} log(λ_aday/λ_taban) − (Λ_aday,i − Λ_taban,i).
    ``blok_ozeti`` bu (D, n) ve bütün takvim günleriyle haftalık sandwich SE verir.
    """
    if agirliklar is None:
        agirliklar = [1.0 / len(defterler)] * len(defterler)
    lam_olay, Lam_gun, mask = bilesen(defterler, agirliklar, alt, olcekler)
    _dogrula(list(defterler) + [taban])
    ref_olay = taban.lam()
    ref_gun = _gun_vektoru(taban, alt)
    if mask.any() and (lam_olay[mask].min() <= 0 or ref_olay[mask].min() <= 0):
        raise PuanHatasi('Gözlemli sıfır oran: IG tanımsız')
    oran = np.log(lam_olay[mask]) - np.log(ref_olay[mask])
    gunler = _gunler(taban)
    gun_idx = {g: i for i, g in enumerate(gunler)}
    idx = taban.olay.loc[mask, 'gun'].astype(str).map(gun_idx).to_numpy(int)
    D = np.bincount(idx, weights=oran, minlength=len(gunler)) - (Lam_gun - ref_gun)
    n = np.bincount(idx, minlength=len(gunler))
    N = int(n.sum())
    ig_olay = float(oran.mean()) if N else None
    integral = float(-(Lam_gun.sum() - ref_gun.sum()) / N) if N else None
    ig = float(D.sum() / N) if N else None
    return dict(D=D, n=n.astype(int), gunler=gunler, N=N,
                Lambda_aday=float(Lam_gun.sum()), Lambda_taban=float(ref_gun.sum()),
                IG=ig, IG_olay=ig_olay, integral=integral)


def ozet(defterler, taban, alt, agirliklar=None, olcekler=None):
    """Kazanç satırı + haftalık blok SE (tek yönlü z, p_tek)."""
    from knotenlinie.karsilastir.blok import blok_ozeti
    k = gun_kazanci(defterler, taban, alt, agirliklar, olcekler)
    blok = blok_ozeti(k['D'], k['n'], k['gunler'], n=k['N'])
    k.update(SE_blok=blok['SE_blok'], z=blok['z'], p_tek=blok['p_tek'],
             blok_sayisi=blok.get('blok_sayisi'), GA95=blok.get('GA95'))
    return k


def iki_yonlu(defterler, taban, alt, agirliklar=None, olcekler=None):
    """Eşleştirilmiş iki yönlü T ve Wilcoxon p-değerleri (olay bağımsızlığı varsayar; ek tanı)."""
    from knotenlinie.karsilastir.puan import eslestirilmis
    if agirliklar is None:
        agirliklar = [1.0 / len(defterler)] * len(defterler)
    lam_olay, Lam_gun, mask = bilesen(defterler, agirliklar, alt, olcekler)
    r = eslestirilmis(lam_olay[mask], taban.lam()[mask], float(Lam_gun.sum()),
                      float(_gun_vektoru(taban, alt).sum()))
    return dict(p_T=r['p_T'], p_W=r['p_W'], IG=r['IG'])


def agirlik_sec(defterler, alt, *, baslangic=None):
    """Simplex üstünde 2006–2010 M≥alt logL'ini en büyükleyen ağırlık."""
    defterler = list(defterler)
    ref = _dogrula(defterler)
    L = _lam_matris(defterler)
    mask = _esik_mask(ref, alt)
    Lm = L[:, mask]
    Lam = np.array([_gun_vektoru(d, alt).sum() for d in defterler], float)
    K = len(defterler)
    if not mask.any():
        raise PuanHatasi('Seçim penceresinde M≥eşik olay yok')

    def f(w):
        s = w @ Lm
        if (s <= 0).any():
            return 1e12
        return float(-(np.log(s).sum() - w @ Lam))

    def g(w):
        s = w @ Lm
        return -(Lm @ (1.0 / s) - Lam)

    w0 = np.full(K, 1.0 / K) if baslangic is None else np.asarray(baslangic, float)
    sonuc = minimize(f, w0, jac=g, method='SLSQP', bounds=[(0.0, 1.0)] * K,
                     constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1,
                                   'jac': lambda w: np.ones(K)}],
                     options=dict(maxiter=1000, ftol=1e-13))
    if not sonuc.success or not np.isfinite(sonuc.fun):
        raise PuanHatasi(f'Ağırlık optimizasyonu başarısız: {sonuc.message}')
    w = np.clip(sonuc.x, 0.0, None)
    w = w / w.sum()
    return dict(agirliklar=w.tolist(), logL=float(-sonuc.fun),
                olcekler=[1.0] * K, modeller=[d.ad for d in defterler])
