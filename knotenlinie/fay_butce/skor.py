"""Hücre×büyüklük Poisson skoru ve yalnız ≤2010 karışım ayarı."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from .butce import izgara_dogrula, kenarlar_dogrula, karisim

AYAR_SON = pd.Timestamp('2011-01-01', tz='UTC')
ACIK_SON = pd.Timestamp('2016-01-01', tz='UTC')


def sayim(olaylar, izgara, kenarlar):
    """Yarı açık hücre/kutular; dışarıdaki olaylar açıkça sayılır."""
    a = izgara_dogrula(izgara)
    k = kenarlar_dogrula(kenarlar)
    h = np.zeros((len(a), len(k)-1), dtype=int)
    dis = 0
    for r in olaylar.itertuples(index=False):
        if not np.isfinite([r.boylam,r.enlem,r.mw]).all():
            raise ValueError('olay koordinatı/büyüklüğü geçersiz')
        i = np.flatnonzero((a[:,0] <= r.boylam) & (r.boylam < a[:,1])
                          & (a[:,2] <= r.enlem) & (r.enlem < a[:,3]))
        j = int(np.searchsorted(k, r.mw, side='right')-1)
        if len(i)==1 and 0 <= j < len(k)-1:
            h[i[0],j] += 1
        else:
            dis += 1
    return h, dis


def log_olabilirlik(beklenen, gozlenen):
    """Σ[n log λ − λ]; log(n!) modeller arası farkta düşer."""
    a, n = np.asarray(beklenen, float), np.asarray(gozlenen, float)
    if a.shape != n.shape or not np.isfinite(a).all() or not np.isfinite(n).all() or np.any(a<0) or np.any(n<0) or np.any(n != np.floor(n)):
        raise ValueError('Poisson girdi şekli/değeri geçersiz')
    sec = n > 0
    if np.any(a[sec] == 0):
        return -np.inf
    return float(np.sum(n[sec]*np.log(a[sec])) - a.sum())


def bilgi_kazanci(model, taban, gozlenen):
    """Tam Poisson farkı/olay; integral ve olay-log payları ayrı raporlanır."""
    lm, lt = log_olabilirlik(model, gozlenen), log_olabilirlik(taban, gozlenen)
    n = int(np.sum(gozlenen))
    if n == 0 or not np.isfinite(lt):
        raise ValueError('IG için olay ve sonlu taban skoru gerekir')
    fark = lm-lt
    integral = float(np.sum(taban)-np.sum(model))
    return dict(n=n, delta_logL=float(fark), ig_nat_olay=float(fark/n),
                integral_farki=integral, olay_log_farki=float(fark-integral),
                beklenen_model=float(np.sum(model)), beklenen_taban=float(np.sum(taban)))


def ayarla(taban, fay_adaylari, gozlenen, *, baslangic, bitis, toplam_esitle=False):
    """Sigma adayları ve konveks ağırlık, Poisson olabilirliğini en büyük yapar."""
    bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
    if bas.tzinfo is None or son.tzinfo is None or not bas < son <= AYAR_SON:
        raise ValueError('ayar aralığı UTC ve ≤2010 olmalı')
    if np.sum(gozlenen) <= 0:
        raise ValueError('ayar olayı yok')
    # Tabanın biçimi/değerleri, w=0 kimliğinde dahi denetlenir.
    log_olabilirlik(taban, gozlenen)
    sonuclar = []
    for sigma, fay in fay_adaylari.items():
        def L(w):
            return log_olabilirlik(karisim(taban, fay, w, toplam_esitle=toplam_esitle), gozlenen)
        fit = minimize_scalar(lambda w: -L(w), bounds=(0,1), method='bounded',
                              options={'xatol':1e-10})
        w = max([0.0, 1.0, float(fit.x)], key=L)
        # Yuvarlama düzeyindeki iyileşme w=0 kimliğini bozmamalı.
        if np.isfinite(L(0)) and L(w)-L(0) <= 1e-10:
            w = 0.0
        elif np.isfinite(L(1)) and L(w)-L(1) <= 1e-10:
            w = 1.0
        sonuclar.append(dict(sigma_km=float(sigma), agirlik=w, logL=L(w),
                            delta_logL=L(w)-L(0)))
    if not sonuclar or not any(np.isfinite(s['logL']) for s in sonuclar):
        raise ValueError('sonlu ayar adayı yok')
    en_iyi = max(sonuclar, key=lambda s:s['logL'])
    return dict(**en_iyi, adaylar=sonuclar, toplam_esitle=bool(toplam_esitle),
                baslangic=bas.isoformat(), bitis=son.isoformat())
