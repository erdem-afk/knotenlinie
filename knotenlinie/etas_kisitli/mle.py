"""Dallanma kısıtlı R-ortak MLE: n(θ) ≤ n_max, kutu sınırı olarak (v₁ = logit n).

`knotenlinie/etas_uzun/mle.py::Olabilirlik` ve `knotenlinie/etas_mc25/mle.py` değişmez; yalnız L-BFGS-B sınırı daraltılır.
n_max = SERBEST, R'nin kendi sınırıdır (n ≤ 0,999999).
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
from scipy.special import logit
from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.mle import coz
from knotenlinie.ortak_zemin.ayar import dallanma

SERBEST = 1 - 1e-6
ADAYLAR = (0.6, 0.7, 0.8, 0.9, SERBEST)
SINIRLAR = [(-11.5, 6.9), (-9.2, float(logit(SERBEST))), (-6.9, 3.4), (-9.2, 9.2), (-6.9, 1.386),
            (np.log(1e-5 * M.KM_DERECE), np.log(10 * M.KM_DERECE)), (-6.9, 2.3), (0., 2.)]


def ad(n_max):
    return 'serbest' if n_max >= SERBEST else f'{n_max:g}'


def sinirlar(n_max):
    if not 0 < n_max <= SERBEST:
        raise ValueError('n_max (0, 0,999999] içinde olmalı')
    b = list(SINIRLAR)
    b[1] = (b[1][0], min(b[1][1], float(logit(n_max))))
    return b


def kirp(x, n_max):
    """x'i kısıt kutusuna kırp (yalnız v₁ değişebilir)."""
    lo, hi = zip(*sinirlar(n_max))
    return np.clip(np.asarray(x, float), lo, hi)


def baslangiclar(x_r, n_max):
    """İki sabit başlangıç: R'nin x'i sınıra kırpılmış; n'si 0,9·n_max'a çekilmiş."""
    a = kirp(x_r, n_max)
    b = np.array(a)
    b[1] = min(a[1], float(logit(0.9 * min(n_max, SERBEST))))
    return [a, kirp(b, n_max)]


def ayarla_kisitli(L, n_max, x_r, *, maksiter=300):
    """L: etas_uzun Olabilirlik. Dönüş: ceza.ayarla_ceza ile uyumlu kayıt (+ kisit alanları)."""
    bnd = sinirlar(n_max)
    sonuc = []
    for x0 in baslangiclar(x_r, n_max):
        r = minimize(L.objectif, x0, args=('ortak',), jac=True, method='L-BFGS-B', bounds=bnd,
                     options=dict(maxiter=maksiter, ftol=1e-11, gtol=2e-7, maxls=40))
        sonuc.append(r)
    iyi = [r for r in sonuc if r.success] or sonuc
    r = min(iyi, key=lambda r: r.fun)
    th = coz(r.x, L.b, 'ortak')
    val, g = L.objectif(r.x, 'ortak')
    n = dallanma(th, L.b)
    sinirda = bool(r.x[1] >= bnd[1][1] - 1e-6)
    return dict(parametreler=th, logL=float(-val * len(L.t)), basari=bool(r.success), nit=int(r.nit), tur='ortak',
                n_max=float(n_max), dallanma=n, sinirda=sinirda, x=r.x.tolist(),
                gradyan_sonsuz_norm=float(np.max(np.abs(g))), tam_cift=int(L.cift),
                baslangic_sonuclari=[dict(basari=bool(q.success), logL=float(-q.fun * len(L.t)), nit=int(q.nit),
                                          mesaj=str(q.message)) for q in sonuc],
                optimizer='L-BFGS-B; R ile aynı dönüşüm ve sınırlar, v1=logit(n) ≤ logit(n_max)')


def model_p(r_json, fit):
    """UzunETAS için parametre sözlüğü: R dosyasının üstüne kısıtlı parametreler."""
    p = dict(r_json)
    p['parametreler'] = {k: float(v) for k, v in fit['parametreler'].items()}
    p['dallanma'] = float(fit['dallanma'])
    p['x'] = list(fit['x'])
    p['logL'] = float(fit['logL'])
    p['kisitli'] = {k: fit[k] for k in ('n_max', 'sinirda', 'basari', 'nit')}
    return p
