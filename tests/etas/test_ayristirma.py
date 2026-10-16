"""Stochastic declustering on labelled synthetic data."""
from __future__ import annotations

import numpy as np
import pytest

from knotenlinie.etas import ayristirma as A
from knotenlinie.etas import benzetim as B
from knotenlinie.etas import model as M

BETA = float(np.log(10.0))
THETA = {"mu": 0.2, "K": 0.006, "c": 0.02, "alpha": 0.9, "p": 1.1}
T0, T1 = 0.0, 500.0
AUC_ESIK = 0.80
EBEVEYN_ESIK = 0.60
TOHUM = 3


def _katalog(seed=TOHUM):
    return B.uretim(THETA, T0, T1, mc=2.0, b=1.0, m_max=6.0, seed=seed, en_cok=200000)


def test_declustering_background_sum_auc_parent_kucuk():
    df = _katalog()
    t, mags, x, y = B.diziler(df)
    theta = M._dizi(THETA, M.ZAMAN_ADLARI)
    phi, (ii, jj, rr) = A.arka_plan_olasiliklari(theta, t, mags, 2.0)
    b_gercek = int(df["arka_plan"].sum())
    n = len(df)
    sigma = np.sqrt(b_gercek * (1.0 - b_gercek / n))
    assert abs(float(phi.sum()) - b_gercek) <= 2.0 * sigma, \
        f"sum(phi)={phi.sum():.1f} vs true background {b_gercek} +- 2*{sigma:.1f}"
    auc = A.auc(phi, df["arka_plan"].to_numpy())
    assert auc >= AUC_ESIK, f"AUC={auc:.3f} < {AUC_ESIK}"
    geri = A.ebeveyn_geri_kazanim(ii, jj, rr, df["ebeveyn"].to_numpy())
    assert geri["oran"] >= EBEVEYN_ESIK, f"parent recovery {geri['oran']:.3f} < {EBEVEYN_ESIK}"


def test_declustering_iteration_runs_and_keeps_mu_separate():
    df = _katalog()
    t, mags, x, y = B.diziler(df)
    theta = M._dizi(THETA, M.ZAMAN_ADLARI)
    res = A.ayristir(theta, t, mags, 2.0, BETA, T0, T1, azami=5)
    assert res["iterasyon"] >= 1 and len(res["logL_gecmisi"]) == res["iterasyon"]
    assert res["mu"] > 0.0
    assert len(res["probs"]) == len(df)
    assert set(res["rates"].keys()) == {"t", "arka_plan", "toplam"}
