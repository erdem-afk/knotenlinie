"""Transformed-time residual analysis.

Ogata 1988, 10.1080/01621459.1988.10478560.  Event times are mapped to

    tau_i = int_{t0}^{t_i} lambda_obs(u) du

(and in the space-time case to the analogous cumulative integral).  If the model
is correct the ``tau_i`` are a unit-rate Poisson process, so the increments are
iid Exp(1); the KS statistic and its p-value are reported against that null, with
the cumulative-count plot data.  Schoenberg's (2003, 10.1198/016214503000000710)
thinning-based residuals are reported by magnitude bin.

Space-time fits: the transformed time is the fit's own
compensator up to ``t_j``, integrated over the box,

    tau_j = mu (t_j - t0) + sum_{t_i < t_j} K A_i J(t_j - t_i) G_i,

with ``J`` the Omori integral and ``G_i`` the exact box integral of parent ``i``'s kernel
(:func:`knotenlinie.etas.model.mekan_kutu_integrali`) — the normalisation the likelihood
uses, not ``G = 1``.  An earlier full run's KS test (p = 0.0027) took ``G = 1``.

``ks_poisson`` reports ``oran = N / tau_N`` (observed count over the model's expected
count at the last event) and ``beklenen_bolu_gozlenen = tau_N / N``, its inverse: that run's
``oran = 0.968`` means ``tau_N = 1.033 N``, the model expected 3.3 % more events than it saw.

Two uses: the acceptance test of the ETAS fit and a trigger diagnostic for comparison with neural
rivals on the <= 2015 fit.  The test never tunes the fit: a rejection is a finding.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

from . import model as M


def donusmus_zaman(theta, t, mags, m0, beta, t0, G=None) -> np.ndarray:
    """tau_i = int_{t0}^{t_i} lambda(u) du for the temporal ETAS model.

    ``G`` (default 1) is a per-parent factor on the productivity: the space-time fit's
    ``G_i`` gives its box-integrated compensator (:func:`donusmus_zaman_uzay`).
    """
    t = np.asarray(t, float)
    mags = np.asarray(mags, float)
    mu, Kk, c, alpha, p = (float(v) for v in list(theta)[:5])
    A = 10.0 ** (alpha * (mags - m0))
    if G is not None:
        A = A * np.asarray(G, float)
    N = t.size
    tau = mu * (t - t0)
    for j in range(N):
        gecmis = t[:j] < t[j]
        if np.any(gecmis):
            J, _, _ = M._omori_ilke(t[j] - t[:j][gecmis], c, p)
            tau[j] += Kk * float(np.sum(A[:j][gecmis] * J))
    return tau


def donusmus_zaman_uzay(theta, t, mags, x, y, m0, beta, t0, kutu, u_olay=None,
                        dx: float = 0.1, metrik=None, G=None) -> np.ndarray:
    """Space-time transformed time with the fit's own ``G_i``.

    ``theta`` is the space-time vector ``(mu, K, c, alpha, p, D, q, gamma)`` with ``D`` in km;
    ``x, y`` are longitudes and latitudes in degrees; ``G`` defaults to
    :func:`knotenlinie.etas.model.uzay_normalizasyonu`.  The background integrates to ``mu`` over
    the box whatever ``u`` is (unit integral), so ``u_olay`` and ``dx`` do not enter.
    """
    th = np.asarray(theta, float)
    if G is None:
        G = M.uzay_normalizasyonu(th, x, y, mags, m0, kutu, metrik=metrik)
    return donusmus_zaman(th[:5], t, mags, m0, beta, t0, G=G)


def ks_poisson(tau) -> dict:
    """KS test of the transformed-time increments against Exp(1) (unit-rate Poisson).

    ``oran = N / tau_N`` (observed over expected); ``beklenen_bolu_gozlenen = tau_N / N``.
    """
    tau = np.sort(np.asarray(tau, float))
    if tau.size < 5:
        return {"D": float("nan"), "p": float("nan"), "n": int(tau.size)}
    art = np.diff(np.concatenate([[0.0], tau]))
    D, p = stats.kstest(art, "expon")
    return {"D": float(D), "p": float(p), "n": int(tau.size),
            "oran": float(tau.size / tau[-1]) if tau[-1] > 0 else float("nan"),
            "beklenen_bolu_gozlenen": float(tau[-1] / tau.size),
            "oran_tanimi": "oran = N / tau_N (observed / expected); beklenen_bolu_gozlenen = tau_N / N"}


def schoenberg_kalinti(theta, t, mags, m0, beta, t0, mag_binleri=None, tau=None) -> dict:
    """Schoenberg (2003) thinning residuals by magnitude bin (``tau`` given or temporal)."""
    t = np.asarray(t, float)
    mags = np.asarray(mags, float)
    if tau is None:
        tau = donusmus_zaman(theta, t, mags, m0, beta, t0)
    lam_toplam = float(tau[-1])
    beta_v = beta
    if mag_binleri is None:
        mag_binleri = np.arange(np.floor(mags.min() * 2) / 2, mags.max() + 0.5, 0.5)
    cikti = []
    for a, b in zip(mag_binleri[:-1], mag_binleri[1:]):
        # model-expected number in the bin: the GR share of the total intensity
        beklenen = lam_toplam * (np.exp(-beta_v * (a - m0)) - np.exp(-beta_v * (b - m0)))
        gozlenen = float(((mags >= a) & (mags < b)).sum())
        sapma = (gozlenen - beklenen) / np.sqrt(beklenen) if beklenen > 0 else np.nan
        cikti.append({"bin": [float(a), float(b)], "gozlenen": gozlenen,
                      "beklenen": float(beklenen), "z": float(sapma)})
    return {"tau": tau, "toplam": lam_toplam, "bins": cikti}


def kalinti_ozet(theta, t, mags, m0, beta, t0, x=None, y=None, kutu=None, metrik=None) -> dict:
    """Everything the CLI prints for the residual analysis.

    With a space-time ``theta`` (eight entries) and ``x, y, kutu`` the transformed time is
    :func:`donusmus_zaman_uzay` (``G_i`` of the fit); otherwise the temporal one.
    """
    uzay = np.size(theta) >= 8 and kutu is not None
    if uzay:
        if x is None or y is None:
            raise ValueError("a space-time residual needs the event longitudes and latitudes")
        tau = donusmus_zaman_uzay(theta, t, mags, x, y, m0, beta, t0, kutu, metrik=metrik)
    else:
        tau = donusmus_zaman(theta, t, mags, m0, beta, t0)
    ks = ks_poisson(tau)
    sch = schoenberg_kalinti(theta, t, mags, m0, beta, t0, tau=tau)
    birikim = (np.arange(1, tau.size + 1) / tau.size, tau / tau[-1] if tau[-1] > 0 else tau)
    return {"ks": ks, "donusmus_zaman": tau.tolist(),
            "birikim": {"gozlenen": birikim[0].tolist(), "beklenen": birikim[1].tolist()},
            "schoenberg": sch["bins"], "model": "uzay-zaman" if uzay else "zaman",
            "normalizasyon": M.NORMALIZASYON if uzay else None}
