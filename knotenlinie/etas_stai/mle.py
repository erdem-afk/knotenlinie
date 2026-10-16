"""Deney W: Mc_e(t)'li MLE; R'nin (``knotenlinie/etas_uzun``) olabilirliğini genişletir, değiştirmez.

R'nin hedef maskesi, ebeveyn kümesi, uzay çekirdeği ve tam çift yapısı aynen
alınır. Tek fark hedef ağırlığı ve kompansatör: ``s_W(t)`` (yumuşak tespit,
``tamlik.py``) hedef terimine girer; zaman kompansatörü ``s_dönem − s_W``
azalmasını düğüm aralıklarında analitik Omori integralleriyle düşer.
ETAS parametreleri ve STAI parametreleri birlikte kestirilir.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.mle import coz, donustur
from knotenlinie.etas_uzun.mle import Olabilirlik as ROlabilirlik
from knotenlinie.ortak_zemin.ayar import dallanma
from .tamlik import DMC_ARALIK, TAU_ARALIK, VARSAYILAN_THETA


class _MaskeOnbellek:
    """Ebeveyn deger()'ının hesapladığı G'yi saklar (ikinci hesap yok)."""

    def __init__(self, mask):
        self.mask, self.G = mask, None
        self.kenar = mask.kenar

    def deger(self, Di, q, grad=False):
        out = self.mask.deger(Di, q, grad)
        self.G = out[0] if grad else out
        return out


def _omori_fark(lo, hi, c, p):
    """∫_lo^hi (u+c)^-p du ve c, p türevleri (``M._omori_ilke`` farkıyla aynı, tek log/exp)."""
    ahi, alo = hi + c, lo + c
    lh, ll_ = np.log(ahi), np.log(alo)
    eh, el = np.exp(-p * lh), np.exp(-p * ll_)          # a^-p
    h1, l1 = ahi * eh, alo * el                          # a^(1-p)
    q = 1.0 - p
    I = (h1 - l1) / q
    Ic = eh - el
    Ip = ((-lh * h1 + ll_ * l1) * q + (h1 - l1)) / q ** 2
    return I, Ic, Ip


class Olabilirlik(ROlabilirlik):
    """R olabilirliği + yumuşak tespit ağırlığı + düğümlü kompansatör düzeltmesi."""

    def __init__(self, t, m, x, y, b, T, kirilma, grid, kutu, u=None, stai=None):
        super().__init__(t, m, x, y, b, T, kirilma, grid, kutu, u)
        self.stai = stai
        self.nstai = 0 if stai is None else stai.nstai
        self.mask = _MaskeOnbellek(self.mask)
        self.arka_T_taban = float(self.arka_T)
        self.t_hedef = self.t[self.hedef]
        self._th = None
        self._C = None
        self._dlogs = np.zeros((len(self.hedef), self.nstai))
        self._r = np.empty(0)
        self._dr = np.zeros((0, self.nstai))
        self._hazirla(None)

    def _hazirla(self, theta):
        if self.stai is None:
            return
        if theta is None and self.nstai:
            theta = VARSAYILAN_THETA
        S, dS, _ = self.stai.agirlik(self.t_hedef, theta)
        self.s = S
        if self.nstai:
            self._dlogs = (dS / S)[:, None] * self.stai.mu_turev(self.t_hedef, theta)
        self._r, self._dr = self.stai.azalma(theta)
        self.arka_T = self.arka_T_taban - float(np.dot(self._r, self.stai.genislik)) if len(self._r) else self.arka_T_taban

    def zaman(self, c, p):
        I, Ic, Ip = super().zaman(c, p)
        self._C = None
        if self.stai is None or not len(self._r):
            return I, Ic, Ip
        th = self._th
        A = np.exp(M.LN10 * th['alpha'] * self.dm)
        agirlik = th['K'] * A * self.mask.G
        C = np.zeros(len(self._r))
        B = 256
        hi_all, lo_all = self.stai.hi, self.stai.lo
        for a in range(0, len(self.t), B):
            tj = self.t[a:a + B, None]
            k0 = int(np.searchsorted(hi_all, self.t[a], side='right'))  # t sıralı: önceki düğümler sıfır
            if k0 >= len(hi_all):
                break
            hi = hi_all[None, k0:] - tj
            ok = hi > 0
            hi = np.where(ok, hi, 0.0)
            lo = np.minimum(np.maximum(lo_all[None, k0:] - tj, 0.0), hi)
            Om, Omc, Omp = _omori_fark(lo, hi, c, p)
            Om, Omc, Omp = Om * ok, Omc * ok, Omp * ok
            r = self._r[k0:]
            I[a:a + B] -= Om @ r
            Ic[a:a + B] -= Omc @ r
            Ip[a:a + B] -= Omp @ r
            C[k0:] += agirlik[a:a + B] @ Om
        self._C = C
        return I, Ic, Ip

    def deger(self, th, grad=False, theta=None):
        """ETAS parametreleri ``th`` (8), STAI ``theta`` (nstai); grad=True => (ll, g[8+nstai])."""
        self._th = th
        self._hazirla(theta)
        out = super().deger(th, grad)
        if not grad or not self.nstai:
            return out
        ll, g = out
        C = th['mu'] * self.stai.genislik
        if self._C is not None:
            C = C + self._C
        gt = self._dlogs.sum(0) + self._dr.T @ C
        return ll, np.r_[g, gt]


def _sinirlar(nstai):
    from scipy.special import logit
    b = [(-11.5, 6.9), (-9.2, float(logit(1 - 1e-6))), (-6.9, 3.4), (-9.2, 9.2), (-6.9, 1.386),
         (np.log(1e-5 * M.KM_DERECE), np.log(10 * M.KM_DERECE)), (-6.9, 2.3), (0.0, 2.0)]
    if nstai:
        b += [(np.log(DMC_ARALIK[0]), np.log(DMC_ARALIK[1])), (np.log(TAU_ARALIK[0]), np.log(TAU_ARALIK[1]))]
    return b


def objektif(L, v, tur='ortak'):
    """-ll/N ve doğal-ölçekten dönüşmüş gradyan; v = [8 ETAS dönüşümlü, (ln dMc, ln tau)]."""
    th = coz(v[:8], L.b, tur)
    theta = (float(np.exp(v[8])), float(np.exp(v[9]))) if L.nstai else None
    ll, g = L.deger(th, True, theta)
    mu, K, c, a, p, D, q, gamma = [th[k] for k in M.UZAY_ADLARI]
    n, f = float(expit(v[1])), float(expit(v[3]))
    gx = np.array([g[0] * mu, g[1] * K * (1 - n), g[2] * c + g[1] * K * (p - 1),
                   L.b * f * (1 - f) * (g[3] - g[1] * K / (L.b - a)),
                   (p - 1) * (g[4] + g[1] * K * (1 / (p - 1) + np.log(c))),
                   g[5] * D, g[6] * (q - 1), g[7]])
    if L.nstai:
        gx = np.r_[gx, g[8] * theta[0], g[9] * theta[1]]
    N = len(L.t)
    return -ll / N, -gx / N


def ayarla(L, baslangic_p, *, theta0=None, maksiter=200, tur='ortak'):
    """ETAS+STAI birlikte; başlangıç R çözümü (K, dallanma ``donustur``'dan korunur)."""
    th0 = {k: float(baslangic_p[k]) for k in M.UZAY_ADLARI}
    v0 = donustur(th0, L.b, tur)
    baslar = [v0]
    if L.nstai:
        for t0 in ([theta0] if theta0 is not None else [VARSAYILAN_THETA, (1.0, 3.0), (0.25, 0.5)]):
            baslar_t = np.r_[v0, np.log(np.asarray(t0, float))]
            baslar.append(baslar_t)
        baslar = baslar[1:]
    sonuc = []
    for v in baslar:
        res = minimize(lambda z: objektif(L, z, tur), v, jac=True, method='L-BFGS-B',
                       bounds=_sinirlar(L.nstai),
                       options=dict(maxiter=maksiter, ftol=1e-11, gtol=2e-7, maxls=40))
        sonuc.append(res)
    iyi = [r for r in sonuc if np.isfinite(r.fun)]
    if not iyi:
        raise ValueError('W MLE: sonlu çözüm yok')
    best = min(iyi, key=lambda r: r.fun)
    th = coz(best.x[:8], L.b, tur)
    theta = (float(np.exp(best.x[8])), float(np.exp(best.x[9]))) if L.nstai else None
    _, grad = objektif(L, best.x, tur)
    return dict(parametreler={k: float(v) for k, v in th.items()}, stai_theta=theta,
                logL=-float(best.fun) * len(L.t), basari=bool(best.success), nit=int(best.nit),
                mesaj=str(best.message), gradyan_sonsuz_norm=float(np.max(np.abs(grad))),
                dallanma=dallanma(th, L.b), tam_cift=int(L.cift), tur=tur,
                baslangic_sonuclari=[dict(basari=bool(r.success), logL=float(-r.fun * len(L.t)), nit=int(r.nit))
                                     for r in sonuc],
                optimizer='L-BFGS-B; R ile aynı ETAS dönüşümü + ln(dMc), ln(tau); analitik gradyan')
