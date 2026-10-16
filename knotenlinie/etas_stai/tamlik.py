"""Deney W: kısa süreli tamlık (STAI) — Mc_e(t)=max(Mc_dönem(t), Mc_sonra(t)).

R'nin iki dönemli sabit Mc basamağı (1985–2004: 3,1; 2005+: 2,5) korunur; üstüne
büyük bir olaydan sonraki kısa süreli eksiklik eklenir. İki önceden sabit biçim:

* ``a``: Helmstetter, Kagan ve Jackson (2006) sabitleri,
  ``Mc_sonra(t)=max_j[M_j-4,5-0,75 log10(Δt_gün)]``, ``M_j>=5,0``, ``0<Δt<=30``.
* ``b``: Hainzl (2016) fikrinin zamanın üstel sönümlü sadeleşmesi,
  ``Mc_sonra(t)=Mc0+dMc exp(-Δt/tau)``, son ``M>=5,0`` olaydan ``Δt<=60`` gün;
  ``(dMc, tau)`` ≤ayar verisiyle MLE'de kestirilir.

Tespit olasılığı büyüklüğe göre yumuşaktır (Ogata ve Katsura 1993 biçimi):
``q(m,t)=Phi((m-Mc_sonra(t))/SIGMA+Z95)``; ``Mc_sonra`` %95 tamlık düzeyidir.
Gözlenen oran = gerçek oran × q. Mc_dönem R'deki gibi sert kesimdir. Yumuşak
tespitin kapalı çözümleri (GR yoğunluğu üstünde integral) aşağıda; olabilirliğin
etkin ağırlığı ``s_W(t)=∫_{Mc_dönem}^∞ f(m) q(m,t) dm`` (Mc0=2,5'e göre normalli).
"""
from __future__ import annotations

import numpy as np
from scipy.special import ndtr

MC0 = 2.5
DONEM_MC = (3.1, MC0)
SIGMA = 0.25
Z95 = 1.6448536269514722
HKJ_SABIT, HKJ_EGIM, HKJ_PENCERE, HKJ_M_ESIK = 4.5, 0.75, 30.0, 5.0
HAINZL_PENCERE, HAINZL_M_ESIK = 60.0, 5.0
DMC_ARALIK = (0.05, 1.5)
TAU_ARALIK = (0.3, 10.0)
VARSAYILAN_THETA = (0.5, 1.0)
#: Düğüm kenarları: Δt (gün) cinsinden; sıfıra yakın ince, kuyrukta kaba.
_ILK = [0.0, 1e-4]


def donem(t, kirilma):
    return np.where(np.asarray(t, float) < kirilma, DONEM_MC[0], DONEM_MC[1])


def _buyuk(bt, bm):
    bt, bm = np.asarray(bt, float), np.asarray(bm, float)
    if bt.shape != bm.shape or (np.diff(bt) < 0).any():
        raise ValueError('büyük olaylar zamana göre sıralı ve aynı şekilde olmalı')
    return bt, bm


def sonra_a(t, bt, bm):
    """HKJ Mc_sonra; etkisiz yerde -inf."""
    t = np.asarray(t, float)
    out = np.full(t.shape, -np.inf)
    for tb, mb in zip(bt, bm):
        dt = t - tb
        ok = (dt > 0) & (dt <= HKJ_PENCERE)
        if ok.any():
            v = mb - HKJ_SABIT - HKJ_EGIM * np.log10(np.where(ok, dt, 1.0))
            out = np.where(ok, np.maximum(out, v), out)
    return out


def son_olay(t, bt, pencere):
    """Her t için bt içinde kesin önceki en son olayın Δt'si; yoksa/dışında nan."""
    t = np.asarray(t, float)
    if not len(bt):
        return np.full(t.shape, np.nan)
    idx = np.searchsorted(bt, t, side='left') - 1
    ok = idx >= 0
    dt = np.where(ok, t - bt[np.maximum(idx, 0)], np.nan)
    return np.where((dt > 0) & (dt <= pencere), dt, np.nan)


def sonra_b(t, bt, theta):
    dMc, tau = theta
    dt = son_olay(t, bt, HAINZL_PENCERE)
    return np.where(np.isnan(dt), -np.inf, MC0 + dMc * np.exp(-np.where(np.isnan(dt), 0.0, dt) / tau))


# --- yumuşak tespit: kapalı biçimler -------------------------------------------

def _E(mu, a, beta):
    """E(mu)=∫_a^∞ e^{-β(m-2,5)} φ((m-mu)/σ)/σ dm (mu sonlu)."""
    za = (a - mu) / SIGMA
    return np.exp(-beta * (mu - MC0) + 0.5 * (beta * SIGMA) ** 2) * ndtr(-(za + beta * SIGMA))


def s_w(mu, a, beta):
    """Etkin ağırlık ve türevi dS/dmu; mu=-inf => q=1 (S=s_dönem, türev 0)."""
    mu = np.asarray(mu, float)
    a = np.asarray(a, float)
    sd = np.exp(-beta * (a - MC0))
    fin = np.isfinite(mu)
    m = np.where(fin, mu, 0.0)
    E = _E(m, a, beta)
    S = sd * ndtr((a - m) / SIGMA) + E
    return np.where(fin, S, sd), np.where(fin, -beta * E, 0.0)


def kutu_q(mu, m1, m2, beta):
    """Bin içi GR ağırlıklı ortalama tespit olasılığı; mu skaler (sonlu), m2 +inf olabilir.

    mu=-inf => 1. Bin: [m1, m2).
    """
    m1 = np.asarray(m1, float)
    m2 = np.asarray(m2, float)
    if not np.isfinite(mu):
        return np.ones(np.broadcast(m1, m2).shape)
    z1 = (m1 - mu) / SIGMA
    z2 = np.where(np.isfinite(m2), (m2 - mu) / SIGMA, np.inf)
    e1 = np.exp(-beta * (m1 - MC0))
    e2 = np.where(np.isfinite(m2), np.exp(-beta * (np.where(np.isfinite(m2), m2, 0.0) - MC0)), 0.0)
    E = np.exp(-beta * (mu - MC0) + 0.5 * (beta * SIGMA) ** 2)
    pay = e1 * ndtr(z1) - e2 * ndtr(z2) + E * (ndtr(z2 + beta * SIGMA) - ndtr(z1 + beta * SIGMA))
    return pay / (e1 - e2)


# --- sınıf: tespit eğrisi, düğümler, türevler ------------------------------------

def dugum_kenarlari(pencere):
    """Δt kenarları: geometrik (×1,2) ~1e-4'ten ~0,3 güne; sonra ~0,25–1 gün."""
    e = [0.0, 1e-4]
    while e[-1] < 0.3:
        e.append(e[-1] * 1.2)
    d = e[-1]
    while d < pencere - 1e-12:
        d = min(d + (0.1 if d < 1.0 else (0.25 if d < 4.0 else 1.0)), pencere)
        e.append(d)
    return np.asarray(e, float)


class KisaTamlik:
    """Bir biçim (a/b) için ``mu_det``, etkin ağırlık ve düğüm azalmaları."""

    def __init__(self, tur, kirilma, b, big_t, big_m, T):
        if tur not in ('a', 'b'):
            raise ValueError("tur 'a' ya da 'b' olmalı")
        if not (np.isfinite(b) and b > 0):
            raise ValueError('b pozitif/sonlu olmalı')
        self.tur, self.kirilma, self.b = tur, float(kirilma), float(b)
        self.beta = self.b * np.log(10.0)
        self.T = float(T)
        bt, bm = _buyuk(big_t, big_m)
        keep = bt < self.T
        self.big_t, self.big_m = bt[keep], bm[keep]
        self.pencere = HKJ_PENCERE if tur == 'a' else HAINZL_PENCERE
        self.nstai = 0 if tur == 'a' else 2
        self._dugumler()

    # Mc_sonra ve mu_det
    def sonra(self, t, theta=None):
        if self.tur == 'a':
            return sonra_a(t, self.big_t, self.big_m)
        return sonra_b(t, self.big_t, theta if theta is not None else VARSAYILAN_THETA)

    def mu_det(self, t, theta=None):
        return self.sonra(t, theta) - Z95 * SIGMA

    def agirlik(self, t, theta=None):
        """(s_W(t), dS/dmu, a)."""
        t = np.asarray(t, float)
        a = donem(t, self.kirilma)
        S, dS = s_w(self.mu_det(t, theta), a, self.beta)
        return S, dS, a

    def mu_turev(self, t, theta):
        """∂mu_det/∂θ, şekil (len(t), nstai); (b): son olay kuralı, etkisiz yerde 0."""
        t = np.asarray(t, float)
        if self.nstai == 0:
            return np.zeros((len(t), 0))
        dMc, tau = theta
        dt = son_olay(t, self.big_t, HAINZL_PENCERE)
        ok = ~np.isnan(dt)
        e = np.where(ok, np.exp(-np.where(ok, dt, 0.0) / tau), 0.0)
        return np.column_stack([e, np.where(ok, dMc * e * np.where(ok, dt, 0.0) / tau ** 2, 0.0)])

    # düğümler
    def _dugumler(self):
        if not len(self.big_t):
            self.lo = self.hi = self.mid = np.empty(0)
            return
        E = dugum_kenarlari(self.pencere)
        edges = [(tb + E) for tb in self.big_t]
        edges.append(np.array([self.kirilma, self.T]))
        e = np.unique(np.concatenate(edges))
        e = e[(e >= 0) & (e <= self.T)]
        # çok dar parçaları birleştirme: 1e-9 günden küçük aralıklar atılır
        lo, hi = e[:-1], e[1:]
        keep = (hi - lo) > 1e-9
        lo, hi = lo[keep], hi[keep]
        mid = 0.5 * (lo + hi)
        # kapsama: orta nokta bir büyük olayın penceresinde mi?
        cover = np.zeros(len(mid), bool)
        for tb in self.big_t:
            cover |= (mid > tb) & (mid <= tb + self.pencere)
        self.lo, self.hi, self.mid = lo[cover], hi[cover], mid[cover]
        # kırılma iki parçanın içine düşmesin
        if ((self.lo < self.kirilma) & (self.hi > self.kirilma)).any():
            raise ValueError('düğüm kırılmayı aşıyor')

    @property
    def genislik(self):
        return self.hi - self.lo

    def azalma(self, theta=None):
        """r_k = s_dönem(mid) − s_W(mid) >= 0 (birim zaman başına) ve ∂r/∂θ (K, nstai)."""
        if not len(self.mid):
            return np.empty(0), np.zeros((0, self.nstai))
        S, dS, a = self.agirlik(self.mid, theta)
        r = np.exp(-self.beta * (a - MC0)) - S
        if self.nstai == 0:
            return r, np.zeros((len(r), 0))
        return r, -dS[:, None] * self.mu_turev(self.mid, theta)

    def kayit(self, theta=None):
        return dict(tur=self.tur, b=self.b, sigma=SIGMA, z95=Z95, kirilma=self.kirilma,
                    pencere_gun=self.pencere,
                    sabitler=dict(HKJ=(HKJ_SABIT, HKJ_EGIM, HKJ_M_ESIK)) if self.tur == 'a' else
                    dict(M_esik=HAINZL_M_ESIK, dMc_aralik=DMC_ARALIK, tau_aralik=TAU_ARALIK),
                    theta=(list(map(float, theta)) if theta is not None else None),
                    dugum=int(len(self.mid)), buyuk_olay=int(len(self.big_t)))
