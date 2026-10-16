"""Known-answer tests for the Coulomb function."""
import numpy as np
import pytest

from knotenlinie.defter.coulomb import B_den_mu, coulomb, coulomb_taramasi, mu_den_B

# Hand-computed once, on paper, and written here as literals:
# sigma = diag(10, 20, 30) Pa, n = (1,0,1)/sqrt(2), s = (1,0,-1)/sqrt(2)
#   sigma.n = (10, 0, 30)/sqrt(2)
#   tau = -10 Pa, sigma_n = +20 Pa
#   Delta-CFS = tau + mu'*sigma_n = -6 / -2 / +2 Pa for mu' = 0.2 / 0.4 / 0.6
TAU = -10.0
SIGMA_N = 20.0


def test_elle_hesaplanan_coulomb():
    assert coulomb(TAU, SIGMA_N, mu_prime=0.2) == pytest.approx(-6.0)
    assert coulomb(TAU, SIGMA_N, mu_prime=0.4) == pytest.approx(-2.0)
    assert coulomb(TAU, SIGMA_N, mu_prime=0.6) == pytest.approx(2.0)


def test_gozenek_basinci_terimi():
    # p = 5 Pa, B = 0.5 -> mu = 0.4/0.5 = 0.8 -> -10 + 0.4*20 + 0.8*5 = +2 Pa
    assert coulomb(TAU, SIGMA_N, p=5.0, mu_prime=0.4, B=0.5) == pytest.approx(2.0)


def test_p_varken_B_zorunlu():
    p = np.array([5.0, np.nan])
    with pytest.raises(ValueError):
        coulomb(np.array([TAU, TAU]), np.array([SIGMA_N, SIGMA_N]), p=p, mu_prime=0.4)


def test_tamamen_bos_p_B_istemez():
    p = np.array([np.nan, np.nan])
    out = coulomb(np.array([TAU, TAU]), np.array([SIGMA_N, SIGMA_N]), p=p, mu_prime=0.4)
    assert out == pytest.approx([-2.0, -2.0])


def test_tarama_uclu():
    tarama = coulomb_taramasi(np.array([TAU]), np.array([SIGMA_N]))
    assert set(tarama) == {0.2, 0.4, 0.6}
    assert tarama[0.2][0] == pytest.approx(-6.0)
    assert tarama[0.4][0] == pytest.approx(-2.0)
    assert tarama[0.6][0] == pytest.approx(2.0)


def test_mu_ve_B_donusumu():
    assert mu_den_B(0.4, 0.8) == pytest.approx(0.5)
    assert B_den_mu(0.4, 0.5) == pytest.approx(0.8)
