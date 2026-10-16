"""Temporal recovery, Fisher-information tolerance, kernel normalisation.

The parameter vector is a declared pre-2015 Italian-regime ETAS literal (Falcone,
Console & Murru 2010, 10.4401/ag-4760; Zhuang's example values).  It is written
here as a literal and is never tuned to make a run pass.

Small local tier: sigma_theta is the observed information per event at the truth, pooled from a
declared reference set of catalogs (seeds 101..105) and scaled to each run's N;
pooling is needed because the c/K direction is near-degenerate and a single
catalog's observed information at the truth is not guaranteed positive definite.

Heavy tier (``-m agir``, compute server), rebuilt after review.  The old test scaled a pooled unit information by
``N_HEDEF = 2000`` while the mean event count is 1126 (SD 110), so its sigma was 0.75 of the right
value and a correct Gaussian estimator was predicted to cover 0.867, not 0.954; its loop also stopped
at the first failing parameter.  Now each replicate's sigma is its **own** observed information at
its estimate (``r["std"]``; the information varies strongly between runs, Efron & Hinkley 1978,
Biometrika 65:457, 10.1093/biomet/65.3.457), coverage and bias are evaluated in the fit's transformed
coordinates ``(log mu, log K, log c, logit(alpha/(beta - 1e-3)), log(p - 1))``, where the estimator is
close to normal (``sigma_x = sigma_theta / (d theta/d x)`` at the estimate, exact for this diagonal
map), and the thresholds are unchanged: 2-sigma coverage >= 0.90 and ``|mean bias| <= 0.5`` x the
median own sigma.  The 1 % binomial floor of the nominal 0.954 at R = 200 is 0.915, so 0.90 leaves
room.  All five parameters are computed first and asserted together; the natural-coordinate numbers
are reported (the heavy right tails of c and p make them look biased there).  The heavy tier uses its
own fresh seeds.
"""
from __future__ import annotations

import numpy as np
import pytest

from knotenlinie.etas import benzetim as B
from knotenlinie.etas import model as M

BETA = float(np.log(10.0))
T0, T1 = 0.0, 365.0
MC = 2.0
BV = 1.0
#: mu(1/d), K, c(d), alpha, p, b=1.0, mc=2.0 — declared Italian-regime literals.
GERCEK = {"mu": 2.0, "K": 0.01, "c": 0.015, "alpha": 0.75, "p": 1.15}
KUTU = (41.5, 44.0, 12.0, 14.5)
REF_TOHUMLARI = (101, 102, 103, 104, 105)
KUCUK_TOHUMLARI = (1, 2, 3, 4, 5)
ESIK_3SIGMA = 3.0
GEREKEN_GECEN = 4  # of 5
# heavy tier: the original design numbers, unchanged, and fresh seeds
KAPSAM_ESIK = 0.90
SAPMA_ORANI = 0.5
#: A replicate within this distance of a transformed bound counts as not covered.
SINIR_TOL = 1e-6
TOHUM_KUTU = tuple(range(2026093101, 2026093301))   # R = 200


def _uret(seed, bbox=None, theta=None):
    return B.uretim(theta or GERCEK, T0, T1, mc=MC, b=BV, m_max=6.5, seed=seed, bbox=bbox)


def _bilgi_birim(theta_true, tohumlar=REF_TOHUMLARI):
    """Observed information per event at the truth, pooled over the reference set."""
    th = M._dizi(theta_true, M.ZAMAN_ADLARI)
    H = None
    for seed in tohumlar:
        d = _uret(seed)
        t, mags, x, y = B.diziler(d)
        Hi = M.hessian_nll(th, t, mags, MC, BETA, T0, T1) / len(d)
        H = Hi if H is None else H + Hi
    return H / len(tohumlar)


def test_temporal_recovery_3sigma_kucuk():
    """Small local tier (reduced): each parameter within 3 sigma in at least 4 of 5 runs."""
    birim_bilgi = _bilgi_birim(GERCEK)
    assert np.all(np.linalg.eigvalsh(birim_bilgi) > 0), "pooled truth information is not positive definite"
    gecen = {k: 0 for k in M.ZAMAN_ADLARI}
    for seed in KUCUK_TOHUMLARI:
        d = _uret(seed)
        t, mags, x, y = B.diziler(d)
        r = M.mle_temporal(t, mags, MC, BETA, T0, T1)
        sigma = np.sqrt(np.diag(np.linalg.inv(birim_bilgi)) / len(d))
        for i, k in enumerate(M.ZAMAN_ADLARI):
            z = (r["parametreler"][k] - GERCEK[k]) / sigma[i]
            if abs(z) <= ESIK_3SIGMA:
                gecen[k] += 1
        assert r["basari"], "L-BFGS-B reported failure"
    # report, never hide, a parameter that misses (a finding)
    for k, n in gecen.items():
        assert n >= GEREKEN_GECEN, f"parameter {k}: only {n}/5 runs within 3 sigma (a finding, do not widen)"


@pytest.mark.agir
def test_temporal_recovery_fisher_agir():
    """Heavy tier: R = 200, each run's own sigma at its estimate, in the fit's transformed coordinates:
    2-sigma coverage >= 0.90 and |mean bias| <= 0.5 x median own sigma, all five asserted together.

    a replicate within 1e-6 of a bound counts as **not covered** for that
    parameter.  At a bound ``sigma_x = sigma_theta / |d theta/d x|`` blows up (at ``p - 1 = 0.001``
    it is ``1000 sigma_p``), so the old rule counted bound-stuck replicates as covered; on the
    investigator's R = 200 results 11 replicates sat at ``p = 1.001`` and all 11 counted.  The count
    of bound-stuck replicates per parameter goes into ``RAPOR``.
    """
    th_gercek = M._dizi(GERCEK, M.ZAMAN_ADLARI)
    x_gercek = M._theta_dan_x(th_gercek, BETA)
    alt, ust = M.ZAMAN_SINIRLAR
    X, SX, TH, STH, NN, basari = [], [], [], [], [], 0
    for seed in TOHUM_KUTU:
        t, mags, _, _ = B.diziler(_uret(seed))
        r = M.mle_temporal(t, mags, MC, BETA, T0, T1)
        th = M._dizi(r["parametreler"], M.ZAMAN_ADLARI)
        sd = M._dizi(r["std"], M.ZAMAN_ADLARI)
        x = M._theta_dan_x(th, BETA)
        X.append(x); SX.append(sd / np.abs(M._zincir_carpani(x, BETA)))
        TH.append(th); STH.append(sd); NN.append(t.size); basari += int(r["basari"])
    X, SX, TH, STH = (np.asarray(v, float) for v in (X, SX, TH, STH))
    ok = np.isfinite(SX) & (SX > 0)
    # at a bound the transformed sigma is not the estimator's spread
    sinirda = (np.abs(X - np.asarray(alt, float)) <= SINIR_TOL) | (np.abs(X - np.asarray(ust, float)) <= SINIR_TOL)
    kapsam = np.mean(ok & (np.abs(X - x_gercek) <= 2.0 * np.where(ok, SX, 0.0)) & ~sinirda, axis=0)
    sapma = np.abs(np.mean(X - x_gercek, axis=0))
    olcek = np.nanmedian(np.where(ok, SX, np.nan), axis=0)
    dogal_sapma = (TH.mean(0) - th_gercek) / np.nanmedian(np.where(STH > 0, STH, np.nan), axis=0)
    dogal_kapsam = np.mean(np.abs(TH - th_gercek) <= 2.0 * STH, axis=0)
    rapor = {k: {"kapsam_x": float(kapsam[i]), "sapma_x": float(sapma[i]), "medyan_sigma_x": float(olcek[i]),
                 "sapma_orani_x": float(sapma[i] / olcek[i]), "dogal_sapma_orani": float(dogal_sapma[i]),
                 "dogal_kapsam": float(dogal_kapsam[i]), "gecersiz_sigma": int((~ok[:, i]).sum()),
                 "sinir_sayisi": int(sinirda[:, i].sum())}
             for i, k in enumerate(M.ZAMAN_ADLARI)}
    rapor["_"] = {"R": len(TOHUM_KUTU), "N_ort": float(np.mean(NN)), "N_sd": float(np.std(NN, ddof=1)),
                  "basari": basari,
                  "toplam_sinir_sayisi": int(sinirda.sum())}
    print(f"RAPOR test_temporal_recovery_fisher_agir {rapor}")
    kotu = [f"{k}: coverage {kapsam[i]:.3f} < {KAPSAM_ESIK}" for i, k in enumerate(M.ZAMAN_ADLARI)
            if not kapsam[i] >= KAPSAM_ESIK]
    kotu += [f"{k}: |mean bias| {sapma[i]:.4g} > {SAPMA_ORANI} x median sigma {olcek[i]:.4g}"
             for i, k in enumerate(M.ZAMAN_ADLARI) if not sapma[i] <= SAPMA_ORANI * olcek[i]]
    assert not kotu, f"findings (do not widen): {kotu}; {rapor}"


def test_omori_ilke_matches_numeric_integral():
    """The analytic Omori integral and its c and p derivatives against quad."""
    from scipy import integrate
    for c, p, tau in ((0.05, 1.2, 0.1), (0.015, 1.15, 1.0), (0.05, 1.5, 50.0)):
        I, dIdc, dIdp = M._omori_ilke(np.array([tau]), c, p)
        say = integrate.quad(lambda u: (u + c) ** (-p), 0, tau, limit=200)[0]
        sdc = integrate.quad(lambda u: -p * (u + c) ** (-p - 1), 0, tau, limit=200)[0]
        sdp = integrate.quad(lambda u: -np.log(u + c) * (u + c) ** (-p), 0, tau, limit=200)[0]
        assert float(I[0]) == pytest.approx(say, rel=1e-9)
        assert float(dIdc[0]) == pytest.approx(sdc, rel=1e-9)
        assert float(dIdp[0]) == pytest.approx(sdp, rel=1e-8)


def test_mekan_cekirdegi_normalises_to_one():
    """int g dA = 1 on the plane, with the pi written out."""
    from scipy import integrate
    D, q, gama = 0.05, 1.6, 1.0
    for D, q in ((0.05, 1.6), (0.2, 2.0), (0.01, 1.2)):
        mast = integrate.quad(
            lambda r: 2 * np.pi * r * float(M.mekan_cekirdegi(np.array([r ** 2]), D, q, gama,
                                                             np.array([3.0]), MC)[0]),
            0, np.inf, limit=400)[0]
        assert mast == pytest.approx(1.0, rel=1e-6)


def test_uzay_zaman_likelihood_path_runs():
    """A small space-time catalog fits through the transformed-parameter path (D in km)."""
    kucuk = {"mu": 0.3, "K": 0.004, "c": 0.02, "alpha": 0.7, "p": 1.1, "D": 5.0, "q": 1.6, "gamma": 1.0}
    d = B.uretim(kucuk, T0, T1, mc=MC, b=BV, m_max=6.0, seed=11, bbox=KUTU, metrik="km")
    t, mags, x, y = B.diziler(d)
    assert len(d) > 30
    th = M._dizi(kucuk, M.UZAY_ADLARI)
    hist = M.arka_plan_histogram(x, y, KUTU, dx=0.25)
    u = M.arka_plan_degeri(x, y, hist)
    ell = M.logL_uzay_zaman(th, t, mags, x, y, MC, BETA, T0, T1, KUTU, u, dx=0.25)
    assert np.isfinite(ell)
    r = M.mle_uzay_zaman(t, mags, x, y, MC, BETA, T0, T1, KUTU, u, dx=0.25,
                         baslangiclar=[kucuk], maksiter=3)
    assert np.isfinite(r["logL"]) and r["model"] == "uzay-zaman"
    assert r["normalizasyon"] == M.NORMALIZASYON and r["metrik"]["D_birim"] == "km"
    assert r["metrik"]["phi0"] == 0.5 * (KUTU[0] + KUTU[1])
