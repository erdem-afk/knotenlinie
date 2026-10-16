"""Brownian passage time (Matthews, Ellsworth ve Reasenberg 2002) koşullu olasılığı.

BPT(μ, α) ters Gauss dağılımıdır; ortalama μ, aperiyodiklik α = σ/μ. Koşullu
pencere olasılığı P = [F(e+Δ) − F(e)]/[1 − F(e)], e = son olaydan geçen süre.
Poisson karşılığı P₀ = 1 − exp(−Δ/μ); çarpan g = P/P₀.
"""
from __future__ import annotations

import numpy as np
from scipy.stats import invgauss, norm


class BPTHatasi(ValueError):
    """BPT girdisi geçersiz."""


def _dogrula(mu, alpha):
    if not (np.isfinite(mu) and mu > 0 and np.isfinite(alpha) and alpha > 0):
        raise BPTHatasi('mu ve alpha pozitif sonlu olmalı')


def bpt_cdf_analitik(t, mu, alpha):
    """Kapalı biçim: Φ((√(t/μ) − √(μ/t))/α) + e^{2/α²} Φ(−(√(t/μ)+√(μ/t))/α)."""
    _dogrula(mu, alpha)
    t = np.asarray(t, float)
    u1 = (np.sqrt(t / mu) - np.sqrt(mu / t)) / alpha
    u2 = (np.sqrt(t / mu) + np.sqrt(mu / t)) / alpha
    return norm.cdf(u1) + np.exp(2.0 / alpha ** 2) * norm.cdf(-u2)


def bpt_pdf(t, mu, alpha):
    _dogrula(mu, alpha)
    t = np.asarray(t, float)
    return np.sqrt(mu / (2 * np.pi * alpha ** 2 * t ** 3)) * np.exp(
        -(t - mu) ** 2 / (2 * alpha ** 2 * mu * t))


def _dagilim(mu, alpha):
    lam = mu / alpha ** 2
    return invgauss(mu=alpha ** 2, scale=lam)


def kosullu_olasilik(mu, alpha, gecen, sure):
    """[gecen, gecen+sure) pencere olasılığı; sf farklarının logundan kararlı."""
    _dogrula(mu, alpha)
    if gecen < 0 or sure <= 0:
        raise BPTHatasi('geçen süre ≥ 0, pencere > 0 olmalı')
    d = _dagilim(mu, alpha)
    if gecen == 0:
        return float(d.cdf(sure))
    ls0, ls1 = d.logsf(gecen), d.logsf(gecen + sure)
    if not np.isfinite(ls0):  # yüzey sıfıra gitti: tehlike oranı sınırı
        h = float(d.pdf(gecen + sure / 2) / max(d.sf(gecen + sure / 2), 1e-300))
        return float(-np.expm1(-h * sure))
    return float(max(0.0, -np.expm1(ls1 - ls0)))


def poisson_olasilik(mu, sure):
    return float(-np.expm1(-sure / mu))


def carpan(mu, alpha, gecen, sure):
    """g = P_BPT / P_Poisson; son olay bilinmiyorsa çağıran 1 kullanır."""
    p0 = poisson_olasilik(mu, sure)
    if p0 <= 0:
        return 1.0
    return kosullu_olasilik(mu, alpha, gecen, sure) / p0
