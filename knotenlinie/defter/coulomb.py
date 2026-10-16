"""Coulomb stress change: the only place mu' enters a channel number.

With an open pore pressure p the change is

    Delta-CFS = tau + mu' * sigma_n + mu * p,   mu = mu' / (1 - B)

(Cocco and Rice 2002).  Tension is positive and a positive value brings the fault
closer to failure.  The single free friction input is the effective friction
mu' (centre 0.4; 0.2 and 0.6 carried for sensitivity); B and mu are derived,
never tuned independently.  If p carries a value and B is not given the call raises
instead of using a hidden B.
"""
from __future__ import annotations

from typing import Dict, Iterable

import numpy as np

MU_PRIMES = (0.2, 0.4, 0.6)


def mu_den_B(mu_prime, mu):
    """B = 1 - mu'/mu (Skempton B is derived, not chosen)."""
    mu = np.asarray(mu, dtype=np.float64)
    if np.any(mu == 0.0):
        raise ValueError("mu sıfır olamaz")
    return 1.0 - np.asarray(mu_prime, dtype=np.float64) / mu


def B_den_mu(mu_prime, B):
    """mu = mu'/(1 - B)."""
    B = np.asarray(B, dtype=np.float64)
    if np.any(B == 1.0):
        raise ValueError("B = 1 olamaz; mu tanımsız olur")
    return np.asarray(mu_prime, dtype=np.float64) / (1.0 - B)


def coulomb(tau, sigma_n, p=None, mu_prime=0.4, B=None):
    """Delta-CFS in Pa; p is required to come with its B."""
    tau = np.asarray(tau, dtype=np.float64)
    sigma_n = np.asarray(sigma_n, dtype=np.float64)
    if p is None:
        return tau + mu_prime * sigma_n
    parc = np.asarray(p, dtype=np.float64)
    if not np.any(~np.isnan(parc)):
        return tau + mu_prime * sigma_n
    if B is None:
        raise ValueError(
            "p dolu ama B verilmedi; gizli bir B kullanılmaz. "
            "B'yi mu' ile birlikte açıkça verin ya da p'yi boş bırakın."
        )
    return tau + mu_prime * sigma_n + B_den_mu(mu_prime, B) * parc


def coulomb_taramasi(tau, sigma_n, p=None, mu_primes: Iterable[float] = MU_PRIMES,
                     B=None) -> Dict[float, np.ndarray]:
    """Delta-CFS on the friction scan (mu' = 0.2, 0.4, 0.6); keys are the mu' values."""
    return {
        float(mp): coulomb(tau, sigma_n, p=p, mu_prime=float(mp), B=B)
        for mp in mu_primes
    }
