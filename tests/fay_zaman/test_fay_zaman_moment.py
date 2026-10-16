"""Moment dengesi ve MFD: bilinen girdi, kapalı biçim, bağımsız sayısal integral."""
from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import quad

from knotenlinie.fay_zaman import moment as mom


def test_moment_hizi_bilinen():
    # 100 km² × 1 mm/yıl × 3e10 Pa = 3e10 · 1e8 m² · 1e-3 m/yıl = 3e15 N m/yıl
    assert mom.moment_hizi(100.0, 1.0) == pytest.approx(3e15, rel=1e-12)
    assert mom.moment_hizi(100.0, 1.0, baglasim=0.5) == pytest.approx(1.5e15, rel=1e-12)


@pytest.mark.parametrize('tur', ['gr', 'kar'])
@pytest.mark.parametrize('mmax', [6.2, 7.3])
def test_moment_dengesi_bagimsiz_integral(tur, mmax):
    pr = mom.parcalar(tur, 5.45, mmax, 0.9)
    mdot = 4.2e16
    S = mom.olcek(pr, mdot)

    def f(m):
        for lo, hi, c, beta in pr:
            if lo <= m <= hi:
                return c * np.exp(-beta * m)
        return 0.0
    # parça sınırları noktalar olarak verilir (süreksizlik yok ama kırılma var)
    pts = sorted({p[0] for p in pr} | {p[1] for p in pr})
    tum = sum(quad(lambda m: S * f(m) * 10 ** (1.5 * m + 9.05), a, b, epsabs=0, epsrel=1e-12)[0]
              for a, b in zip(pts[:-1], pts[1:]))
    assert tum == pytest.approx(mdot, rel=1e-9)


def test_gr_kapali_bicim_sayi():
    # kesik GR b=1: N = Ṁ₀ (10^{-a b}−10^{-c b})/(b ln10) / [10^{9.05} (10^{(1.5-b)c}−10^{(1.5-b)a})/((1.5-b) ln10)]
    b, a, c, mdot = 1.0, 5.45, 7.0, 1e17
    pr = mom.parcalar('gr', a, c, b)
    S = mom.olcek(pr, mdot)
    kenar = np.r_[np.round(np.arange(5.45, 7.0 + 1e-9, 0.1), 2), np.inf]
    sayi = mom.kutu_sayilari(pr, S, kenar, lo=a, hi=c).sum()
    pay = (10 ** (-a * b) - 10 ** (-c * b)) / (b * np.log(10))
    payda = 10 ** 9.05 * (10 ** ((1.5 - b) * c) - 10 ** ((1.5 - b) * a)) / ((1.5 - b) * np.log(10))
    assert sayi == pytest.approx(mdot * pay / payda, rel=1e-9)


def test_dar_aralik_limiti():
    # Mmax ≈ Mmin: tüm olaylar Mmax'ta → oran = Ṁ₀ / M₀(Mmax)
    mdot = 2e17
    pr = mom.parcalar('gr', 6.0, 6.0 + 1e-6, 1.0)
    S = mom.olcek(pr, mdot)
    n = S * float(sum(mom.parca_integral(p, 6.0, 6.0 + 1e-6) for p in pr))
    assert n == pytest.approx(mdot / mom.m0(6.0), rel=1e-5)


def test_karakteristik_duz_kisim_ve_sureklilik():
    pr = mom.parcalar('kar', 5.45, 7.2, 1.0)
    assert len(pr) == 2 and pr[0][1] == pytest.approx(5.7) and pr[1][3] == 0.0
    f_sol = pr[0][2] * np.exp(-pr[0][3] * pr[0][1])
    assert pr[1][2] == pytest.approx(f_sol, rel=1e-12)  # süreklilik
    # Mmax−1,5 ≤ 5,45: tamamen düz
    assert len(mom.parcalar('kar', 5.45, 6.5, 1.0)) == 1 and mom.parcalar('kar', 5.45, 6.5, 1.0)[0][3] == 0.0


def test_kutu_toplami_ust_sinir_disi_sifir():
    pr = mom.parcalar('gr', 5.45, 6.5, 0.9)
    S = mom.olcek(pr, 1e17)
    kenar = np.r_[np.round(np.arange(5.45, 9.0, 0.1), 2), np.inf]
    kutu = mom.kutu_sayilari(pr, S, kenar, lo=5.45, hi=6.5)
    assert kutu[kenar[:-1] >= 6.5 - 1e-9].sum() == 0.0
    assert kutu.sum() > 0
