"""Dönem Mc(t)'li ETAS olabilirliği (R-tipi) ve düz ETAS; bölge bağımsız MLE.

Olay terimi kendi dönem/tamlık Mc'siyle GR ölçeğiyle çarpılır; kompansatör
parça-sabit tespit fonksiyonu s(t)=10^{-b(Mc(t)-Mc0)} ile ölçeklenir. D0 için
tek Mc ve tek parça; D1 için dönemler; D2 için dönemler + HKJ günlük parçalar.
`knotenlinie/etas_uzun/mle.py` mantığının bölge bağımsız yazımıdır; dondurulmuş
paketlere dokunmaz.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, logit

from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin.ayar import b_ayarla as _ortak_b, dallanma
from .kesme import KesikMaske


def b_ayarla(mags, mc):
    """GR MLE (gerçek büyüklük çözünürlüğü); Mc(t) dizi olabilir."""
    m = np.asarray(mags, float)
    mc = np.broadcast_to(np.asarray(mc, float), m.shape)
    sec = m >= mc - 1e-12
    if int(sec.sum()) < 10:
        raise ValueError('b için en az 10 olay gerekli')
    excess = np.maximum(m[sec] - mc[sec], 0.0)
    r = _ortak_b(excess, 0.0)
    r.update(tur='GR MLE, Mc(t)', ortalama_fazla=float(excess.mean()),
             n=int(sec.sum()))
    return r


def coz(v, b, tur='ortak'):
    mu, n, c = np.exp(v[0]), expit(v[1]), np.exp(v[2])
    alpha, p = b * expit(v[3]), 1 + np.exp(v[4])
    K = n * (p - 1) * c ** (p - 1) * (b - alpha) / b
    return dict(mu=mu, K=K, c=c, alpha=alpha, p=p,
                D=np.exp(v[5]), q=1 + np.exp(v[6]),
                gamma=(v[7] if tur == 'ortak' else 0.))


def donustur(th, b, tur='ortak'):
    v = [np.log(th['mu']), logit(dallanma(th, b)), np.log(th['c']),
         logit(th['alpha'] / b), np.log(th['p'] - 1), np.log(th['D']), np.log(th['q'] - 1)]
    return np.r_[v, th['gamma']] if tur == 'ortak' else np.array(v)


class Olabilirlik:
    """λ_obs(t) = s(t) [μ u + Σ K 10^{α(M_j-Mc0)} f g].

    s_i = 10^{-b(Mc_olay_i - Mc0)}; `araliklar` = [(lo, hi, s)] mutlak gün
    kesirleriyle ve hi>lo, [0,T]'yi örter. Eş zamanlı ebeveyn yok. Çekirdek
    ``rmax_km``/``tmax_gun`` ile kırpılır; ikisi de None ise tam çiftler.
    """

    def __init__(self, t, m, x, y, b, T, mc0, mc_olay, araliklar, grid, kutu, u=None,
                 maks_cift: int = 20_000_000, rmax_km=None, tmax_gun=None):
        self.t = np.asarray(t, float)
        self.dm = np.asarray(m, float) - float(mc0)
        self.b, self.T, self.mc0 = float(b), float(T), float(mc0)
        self.kutu = tuple(kutu)
        # Kırpılmış çekirdek: g(r)1[r<=rmax], f(dt)1[dt<=tmax]; olay terimi ve
        # kompansatör aynı kesmeyi görür (KURAL.md).
        self.rmax2 = None if rmax_km is None else float(rmax_km) ** 2
        self.tmax = None if tmax_gun is None else float(tmax_gun)
        if not len(self.t) or (self.t < 0).any() or (self.t >= T).any() or (np.diff(self.t) < 0).any():
            raise ValueError('MLE zaman kapısı')
        # s(t) parçaları: mutlak zaman, (lo, hi, s)
        self.araliklar = [(float(a), float(b_), float(s)) for a, b_, s in araliklar]
        if not self.araliklar or min(a for a, _, _ in self.araliklar) > 0 or \
                max(b_ for _, b_, _ in self.araliklar) < T - 1e-9:
            raise ValueError('aralıklar [0,T] örtmüyor')
        self.arka_T = float(sum((b_ - a) * s for a, b_, s in self.araliklar))
        mc_olay = np.asarray(mc_olay, float)
        if (np.asarray(m, float) < mc_olay - 1e-9).any():
            raise ValueError('olay kendi Mc altında')
        self.met = M.yerel_metrik(self.kutu)
        from knotenlinie.ortak_zemin.veri import hucre_indeks
        inside = hucre_indeks(pd.DataFrame(dict(boylam=x, enlem=y)), grid) >= 0
        self.hedef = np.flatnonzero(inside)
        self.nhedef = len(self.hedef)
        if not self.nhedef:
            raise ValueError('maskede hedef yok')
        xk, yk = self.met.km(np.asarray(x, float), np.asarray(y, float))
        self.parcalar, self.cift = [], 0
        for a in range(0, self.nhedef, 64):
            targets = self.hedef[a:a + 64]
            ii, jj = np.nonzero(self.t[targets, None] > self.t[None, :])
            i = targets[ii]
            j = jj.astype(np.int32)
            ii = ii.astype(np.int32)
            dt = self.t[i] - self.t[j]
            r2 = (xk[i] - xk[j]) ** 2 + (yk[i] - yk[j]) ** 2
            if self.tmax is not None:
                tut = dt <= self.tmax
                i, j, ii, dt, r2 = i[tut], j[tut], ii[tut], dt[tut], r2[tut]
            if self.rmax2 is not None:
                tut = r2 <= self.rmax2
                i, j, ii, dt, r2 = i[tut], j[tut], ii[tut], dt[tut], r2[tut]
            self.parcalar.append((ii, j, dt, r2, a, len(targets)))
            self.cift += len(i)
        if self.cift > maks_cift:
            raise ValueError(f'kırpılmış çift bütçesi aşıldı: {self.cift}')
        area = ((grid.boylam_max - grid.boylam_min) * (grid.enlem_max - grid.enlem_min)).sum()
        all_u = np.full(len(self.t), 1 / area) if u is None else np.asarray(u, float)
        self.u = all_u[self.hedef] / self.met.jakobiyen
        self.s = 10 ** (-self.b * (mc_olay[self.hedef] - self.mc0))
        self.mask = KesikMaske(np.asarray(x, float), np.asarray(y, float), grid, self.met,
                               rmax_km=rmax_km)

    def zaman(self, c, p):
        I = np.zeros(len(self.t))
        Ic = np.zeros(len(self.t))
        Ip = np.zeros(len(self.t))
        for lo, hi, s in self.araliklar:
            active = self.t < hi
            a = np.maximum(lo - self.t[active], 0.0)
            b_ = hi - self.t[active]
            if self.tmax is not None:
                b_ = np.maximum(np.minimum(b_, self.tmax), a)
            v, vc, vp = M._omori_ilke(b_, c, p)
            w, wc, wp = M._omori_ilke(a, c, p)
            I[active] += s * (v - w)
            Ic[active] += s * (vc - wc)
            Ip[active] += s * (vp - wp)
        return I, Ic, Ip

    def deger(self, th, grad=False):
        mu, K, c, alpha, p, D, q, gamma = [th[k] for k in M.UZAY_ADLARI]
        Di = D * np.exp(M.LN10 * gamma * self.dm)
        A = np.exp(M.LN10 * alpha * self.dm)
        ll = 0.
        g = np.zeros(8)
        for i, j, dt, r2, a, n in self.parcalar:
            dc = dt + c
            U = r2 / Di[j] ** 2
            L = np.log1p(U)
            z = K * A[j] * np.exp(-p * np.log(dc)) * (q - 1) / (np.pi * Di[j] ** 2) * np.exp(-q * L)
            ub = self.u[a:a + n]
            lam = mu * ub + np.bincount(i, z, minlength=n)
            if not np.isfinite(lam).all() or (lam <= 0).any():
                raise ValueError('geçersiz oran')
            ll += np.log(lam * self.s[a:a + n]).sum()
            if grad:
                wz = z / lam[i]
                scale = 2 * (-1 + q * U / (1 + U))
                g += np.array([np.dot(1 / lam, ub), wz.sum() / K,
                               np.dot(wz, -p / dc), np.dot(wz, M.LN10 * self.dm[j]),
                               np.dot(wz, -np.log(dc)), np.dot(wz, scale) / D,
                               np.dot(wz, 1 / (q - 1) - L), np.dot(wz, scale * M.LN10 * self.dm[j])])
        G, GD, Gq = self.mask.deger(Di, q, True)
        I, Ic, Ip = self.zaman(c, p)
        comp = K * A * I
        ll -= mu * self.arka_T + np.dot(comp, G)
        if not grad:
            return float(ll)
        g -= np.array([self.arka_T, np.dot(A * I, G), np.dot(K * A * Ic, G),
                       np.dot(comp * M.LN10 * self.dm, G), np.dot(K * A * Ip, G),
                       np.dot(comp, GD) / D, np.dot(comp, Gq),
                       np.dot(comp * M.LN10 * self.dm, GD)])
        return float(ll), g

    def objectif(self, v, tur):
        th = coz(v, self.b, tur)
        ll, g = self.deger(th, True)
        mu, K, c, a, p, D, q, gamma = [th[k] for k in M.UZAY_ADLARI]
        n = expit(v[1])
        f = expit(v[3])
        gx = np.array([g[0] * mu, g[1] * K * (1 - n), g[2] * c + g[1] * K * (p - 1),
                       self.b * f * (1 - f) * (g[3] - g[1] * K / (self.b - a)),
                       (p - 1) * (g[4] + g[1] * K * (1 / (p - 1) + np.log(c))),
                       g[5] * D, g[6] * (q - 1), g[7]])
        if tur == 'lm':
            gx = gx[:-1]
        return -ll / len(self.t), -gx / len(self.t)


def ayarla(L: Olabilirlik, tur='ortak', *, maksiter=400, baslangiclar=None):
    if tur not in ('ortak', 'lm'):
        raise ValueError('iki sabit çekirdek')
    starts = baslangiclar or [
        dict(mu=len(L.t) / L.T * .5, K=.01, c=.02, alpha=L.b * .55, p=1.25,
             D=1.1, q=1.5, gamma=.2),
        dict(mu=len(L.t) / L.T * .7, K=.01, c=.01, alpha=L.b * .7, p=1.15,
             D=2.2, q=1.8, gamma=.4)]
    bounds = [(-11.5, 6.9), (-9.2, float(logit(1 - 1e-6))), (-6.9, 3.4), (-9.2, 9.2),
              (-6.9, 1.386), (np.log(1e-5 * M.KM_DERECE), np.log(10 * M.KM_DERECE)),
              (-6.9, 2.3)]
    if tur == 'ortak':
        bounds.append((0., 2.))
    sonuc = []
    for start in starts:
        th = dict(start)
        cap = (th['p'] - 1) * th['c'] ** (th['p'] - 1) * (L.b - th['alpha']) / L.b
        th['K'] = .5 * cap
        r = minimize(L.objectif, donustur(th, L.b, tur), args=(tur,), jac=True,
                     method='L-BFGS-B', bounds=bounds,
                     options=dict(maxiter=maksiter, ftol=1e-11, gtol=2e-7, maxls=40))
        sonuc.append(r)
    iyi = [r for r in sonuc if r.success]
    if not iyi:
        raise ValueError('MLE yakınsamadı: ' + str([r.message for r in sonuc]))
    en = min(iyi, key=lambda r: r.fun)
    th = coz(en.x, L.b, tur)
    val, grad = L.objectif(en.x, tur)
    return dict(parametreler=th, logL=float(-val * len(L.t)), basari=bool(en.success),
                nit=int(en.nit), tur=tur, dallanma=dallanma(th, L.b), tam_cift=L.cift,
                gradyan_sonsuz_norm=float(np.max(np.abs(grad))),
                optimizer='L-BFGS-B; analitik gradyan',
                x=en.x.tolist(),
                baslangic_sonuclari=[dict(basari=bool(r.success), logL=float(-r.fun * len(L.t)),
                                          nit=int(r.nit), mesaj=str(r.message)) for r in sonuc])
