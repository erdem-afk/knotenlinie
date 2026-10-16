"""Elastik sabitler ve standart yerçekimi değeri.

clean-room implementation from the equations published in Okada 1992 (BSSA 82(2),
1018-1040, DOI 10.1785/bssa0820021018); no code copied from cutde (MIT) or any other
Okada implementation.

The Lamé constants are λ = μ = 30 GPa, i.e. a Poisson solid with ν = 0.25.  E is
derived from them and is never a free number; ``G`` (9.80665 m/s²) is standard gravity.
No number in this module is fitted to earthquake data.
"""
from __future__ import annotations

LAM = 30.0e9   # Pa
MU = 30.0e9    # Pa
NU = 0.25      # Poisson solid
E = MU * (3.0 * LAM + 2.0 * MU) / (LAM + MU)   # derived, never a free number
G = 9.80665    # standard gravity (m/s²)

__all__ = ["LAM", "MU", "NU", "E", "G", "poisson_lam_mu", "young_lam_mu"]


def poisson_lam_mu(lam=LAM, mu=MU):
    """ν = λ / (2(λ+μ)): the derived check that the declared constants make a Poisson solid."""
    return lam / (2.0 * (lam + mu))


def young_lam_mu(lam=LAM, mu=MU):
    """E = μ(3λ+2μ)/(λ+μ): the same derivation as the module constant."""
    return mu * (3.0 * lam + 2.0 * mu) / (lam + mu)
