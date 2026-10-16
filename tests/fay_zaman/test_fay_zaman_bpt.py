"""BPT olasılığı: analitik değer, sayısal integral, yenileme zinciri."""
from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import quad

from knotenlinie.fay_zaman import bpt


@pytest.mark.parametrize('alpha', [0.3, 0.5, 0.7])
def test_cdf_sayisal_integrale_esit(alpha):
    mu = 120.0
    for t in (20.0, 80.0, 150.0, 400.0):
        sayisal = quad(lambda x: bpt.bpt_pdf(x, mu, alpha), 0, t, epsabs=0, epsrel=1e-11)[0]
        assert bpt.bpt_cdf_analitik(t, mu, alpha) == pytest.approx(sayisal, rel=1e-8)
        # kosullu_olasilik (scipy invgauss) ile, geçen=0
        assert bpt.kosullu_olasilik(mu, alpha, 0.0, t) == pytest.approx(sayisal, rel=1e-8)


def test_ortalama_mu():
    mu, alpha = 250.0, 0.5
    ort = quad(lambda x: x * bpt.bpt_pdf(x, mu, alpha), 0, np.inf, epsabs=0, epsrel=1e-9)[0]
    assert ort == pytest.approx(mu, rel=1e-6)


def test_kosullu_analitik_deger():
    mu, alpha, e, d = 100.0, 0.5, 80.0, 30.0
    F = bpt.bpt_cdf_analitik
    beklenen = (F(e + d, mu, alpha) - F(e, mu, alpha)) / (1 - F(e, mu, alpha))
    assert bpt.kosullu_olasilik(mu, alpha, e, d) == pytest.approx(beklenen, rel=1e-9)


def test_yenileme_zinciri():
    mu, alpha = 100.0, 0.5
    e, d1, d2 = 40.0, 25.0, 35.0
    p12 = bpt.kosullu_olasilik(mu, alpha, e, d1 + d2)
    p1 = bpt.kosullu_olasilik(mu, alpha, e, d1)
    p2 = bpt.kosullu_olasilik(mu, alpha, e + d1, d2)
    assert p12 == pytest.approx(p1 + (1 - p1) * p2, rel=1e-10)


def test_carpan_yonu_ve_poisson_sinir():
    mu, alpha = 100.0, 0.5
    assert bpt.carpan(mu, alpha, 1.0, 5.0) < 0.01          # yeni kırılma: neredeyse sıfır
    assert bpt.carpan(mu, alpha, 120.0, 5.0) > 1.5          # gecikmiş: Poisson'dan büyük
    # Poisson kimliği: P₀ = 1−exp(−Δ/μ)
    assert bpt.poisson_olasilik(mu, 5.0) == pytest.approx(1 - np.exp(-0.05), rel=1e-12)
    # çok büyük μ, kısa geçen süre: BPT yoğunluğu ~e^{-6666}; g sonlu ve negatif olmayan (alttan taşar)
    g = bpt.carpan(1e6, 0.5, 300.0, 5.0)
    assert np.isfinite(g) and g >= 0


def test_hatalar():
    with pytest.raises(bpt.BPTHatasi):
        bpt.kosullu_olasilik(-1.0, 0.5, 1.0, 1.0)
    with pytest.raises(bpt.BPTHatasi):
        bpt.kosullu_olasilik(10.0, 0.5, -1.0, 1.0)
