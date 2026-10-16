"""Mevcut olabilirliğin alt-kritik kısıtlı ayarı; knotenlinie.etas'a yazmaz.

Serbest MLE süperkritikse aynı 8 parametre SLSQP ile alpha<b ve n<1
kısıtlarında yeniden optimize edilir. K sonuçta kırpılmaz. Serbest
Hessian tanısı aktif sınırdaki örnekleme belirsizliği değildir.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize
from knotenlinie.etas import model as M

DALLANMA_UST = 1 - 1e-6
ALFA_PAY = 1e-6


def kisitlar(x, beta, b):
    th = M._x_den_theta(x, beta, M.UZAY_ADLARI)
    _, K, c, alpha, p = th[:5]
    gap = b - alpha
    return np.array([gap - ALFA_PAY,
                     np.log(DALLANMA_UST) - np.log(K) + (p - 1) * np.log(c) +
                     np.log(p - 1) + np.log(max(gap, 1e-12)) - np.log(b)])


def alt_kritik_mle(t, mags, x, y, mc, beta, b, T, kutu, u_olay, serbest,
                   *, chunk=128, maksiter=400):
    starts = [serbest['parametreler'], *M.BASLANGICLAR_UZAY]
    results = []
    for start in starts:
        th0 = M._dizi(start, M.UZAY_ADLARI)
        th0[3] = min(th0[3], b * 0.8)
        cap = th0[2] ** (th0[4] - 1) * (th0[4] - 1) * (b - th0[3]) / b
        th0[1] = min(th0[1], 0.8 * cap)  # Yalnız başlangıcı fizibil yapar.
        x0 = M._theta_dan_x(th0, beta)
        res = optimize.minimize(
            M._nll_uzay_x, x0,
            args=(t, mags, x, y, mc, beta, 0., T, kutu, u_olay, 0.1, chunk),
            method='SLSQP', bounds=optimize.Bounds(*M.UZAY_SINIRLAR),
            constraints=[{'type': 'ineq', 'fun': kisitlar, 'args': (beta, b)}],
            options={'maxiter': maksiter, 'ftol': 1e-7})
        results.append(res)
    feasible = [r for r in results if r.success and np.min(kisitlar(r.x, beta, b)) >= -1e-8]
    if not feasible:
        raise ValueError('Alt-kritik MLE yakınsamadı: ' + '; '.join(r.message for r in results))
    best = min(feasible, key=lambda r: r.fun)
    th = M._x_den_theta(best.x, beta, M.UZAY_ADLARI)
    H = M.hessian_nll_uzay(th, t, mags, x, y, mc, beta, 0., T, kutu, u_olay, 0.1, chunk)
    std, R, condition, _ = M._std_korelasyon(H)
    return {**serbest, 'parametreler': M._sozluk(th, M.UZAY_ADLARI),
            'std': M._sozluk(std, M.UZAY_ADLARI), 'korelasyon': R.tolist(),
            'hessian_kosul': condition, 'logL': float(-best.fun), 'nit': int(best.nit),
            'basari': bool(best.success), 'optimizer': 'SLSQP; aynı logL, kısıtlı MLE',
            'kisit': {'alpha_ust': b - ALFA_PAY, 'dallanma_ust': DALLANMA_UST,
                      'deger': kisitlar(best.x, beta, b).tolist()},
            'belirsizlik_notu': 'Serbest doğal Hessian; aktif sınırda std/korelasyon güven aralığı değildir',
            'baslangic_sonuclari': [{'basari': bool(r.success), 'mesaj': str(r.message),
                                     'logL': float(-r.fun), 'nit': int(r.nit)} for r in results],
            'serbest_MLE': {'parametreler': serbest['parametreler'], 'logL': serbest['logL']}}
