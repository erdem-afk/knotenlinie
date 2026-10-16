"""Transformed-time residual KS, correct and misspecified."""
from __future__ import annotations

import numpy as np
import pytest

from knotenlinie.etas import benzetim as B
from knotenlinie.etas import kalinti as KL
from knotenlinie.etas import model as M

BETA = float(np.log(10.0))
THETA = {"mu": 0.5, "K": 0.01, "c": 0.02, "alpha": 0.8, "p": 1.1}
T0, T1 = 0.0, 300.0
R_KUCUK = 30
R_AGIR = 100
ORAN = 0.90


def _bir(seed, yanlis=False):
    df = B.uretim(THETA, T0, T1, mc=2.0, b=1.0, m_max=6.0, seed=seed, en_cok=200000)
    t, mags, x, y = B.diziler(df)
    th = M._dizi(THETA, M.ZAMAN_ADLARI)
    if yanlis:
        th = th.copy()
        th[4] = 1.6  # deliberately wrong p (misspecified model)
    tau = KL.donusmus_zaman(th, t, mags, 2.0, BETA, T0)
    return KL.ks_poisson(tau)["p"]


def _oran(yanlis, r):
    p = [_bir(s, yanlis) for s in range(r)]
    return float(np.mean([x >= 0.01 for x in p]) if not yanlis else np.mean([x < 0.01 for x in p]))


def test_kalinti_ks_correct_and_misspecified_kucuk():
    assert _oran(False, R_KUCUK) >= ORAN, "correctly specified model rejected too often"
    assert _oran(True, R_KUCUK) >= ORAN, "misspecified model not rejected often enough"


@pytest.mark.agir
def test_kalinti_ks_correct_and_misspecified_agir():
    assert _oran(False, R_AGIR) >= ORAN
    assert _oran(True, R_AGIR) >= ORAN


def test_kalinti_schoenberg_runs():
    df = B.uretim(THETA, T0, T1, mc=2.0, b=1.0, m_max=6.0, seed=5, en_cok=200000)
    t, mags, x, y = B.diziler(df)
    res = KL.kalinti_ozet(M._dizi(THETA, M.ZAMAN_ADLARI), t, mags, 2.0, BETA, T0)
    assert "ks" in res and res["ks"]["n"] == len(df)
    assert len(res["schoenberg"]) > 0
