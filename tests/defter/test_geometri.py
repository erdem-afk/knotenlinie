"""Geometry tests: known vectors."""

import numpy as np
import pandas as pd
import pytest

from knotenlinie.defter.geometri import fay_tablosu_dogrula, fay_vektorleri, gerilmeyi_coz

def test_basit_fay_eksenleri():
    n, s = fay_vektorleri(0.0, 90.0, 0.0)
    assert n == pytest.approx([0.0, 1.0, 0.0], abs=1e-12)
    assert s == pytest.approx([1.0, 0.0, 0.0], abs=1e-12)


def test_vettore_benzeri_fay():
    n, s = fay_vektorleri(155.0, 45.0, -90.0)
    assert n == pytest.approx([-0.298836, -0.640856, -0.707107], abs=1e-6)
    assert s == pytest.approx([-0.298836, -0.640856, 0.707107], abs=1e-6)


def test_birim_ve_dik_vektorler():
    n, s = fay_vektorleri(37.0, 23.0, 111.0)
    assert np.linalg.norm(n) == pytest.approx(1.0)
    assert np.linalg.norm(s) == pytest.approx(1.0)
    assert float(np.dot(n, s)) == pytest.approx(0.0, abs=1e-12)


def test_elle_tensor_cozumu():
    sigma = np.diag([10.0, 20.0, 30.0])
    n = np.array([1.0, 0.0, 1.0]) / np.sqrt(2.0)
    s = np.array([1.0, 0.0, -1.0]) / np.sqrt(2.0)
    tau, sigma_n = gerilmeyi_coz(sigma, n, s)
    assert float(tau) == pytest.approx(-10.0)
    assert float(sigma_n) == pytest.approx(20.0)


def _fay_tablosu() -> pd.DataFrame:
    n, s = fay_vektorleri(
        np.array([0.0, 155.0]), np.array([90.0, 45.0]), np.array([0.0, -90.0])
    )
    return pd.DataFrame({
        "id": ["A", "B"],
        "strike_central_deg": [0.0, 155.0],
        "dip_central_deg": [90.0, 45.0],
        "rake_central_deg": [0.0, -90.0],
        "normal_n": n[:, 0], "normal_e": n[:, 1], "normal_d": n[:, 2],
        "slip_n": s[:, 0], "slip_e": s[:, 1], "slip_d": s[:, 2],
    })


def test_fay_tablosu_gecer():
    df = _fay_tablosu()
    assert fay_tablosu_dogrula(df) is df


def test_fay_tablosu_bozuk_vektor_reddedilir():
    df = _fay_tablosu()
    df.loc[0, "slip_e"] = 0.5
    with pytest.raises(ValueError):
        fay_tablosu_dogrula(df)


def test_fay_tablosu_tekrarlanan_id_reddedilir():
    df = _fay_tablosu()
    df.loc[1, "id"] = "A"
    with pytest.raises(ValueError):
        fay_tablosu_dogrula(df)
