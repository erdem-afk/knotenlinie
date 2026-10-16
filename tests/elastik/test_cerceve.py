"""Çerçeve testleri: izdüşüm, fay düzlemi çerçevesi, Voigt dönüşümleri, Hooke.

Known answers are fixed literals.
"""
import numpy as np
import pytest

from knotenlinie.elastik.cerceve import (
    dud_gerilme, fay_gerilmesi, ned_metre, nede_yerel, yerel_cerceve, yerelden_nede,
)
from knotenlinie.elastik.sabitler import E, LAM, MU, NU

def test_poisson_katisi():
    assert E == 75.0e9
    assert E == MU * (3.0 * LAM + 2.0 * MU) / (LAM + MU)
    assert NU == pytest.approx(LAM / (2.0 * (LAM + MU)))


def test_ned_metre_bilinen():
    kuzey, dogu = ned_metre(43.0, 14.0, lat0_deg=42.0, lon0_deg=13.0)
    assert kuzey == pytest.approx(6371000.0 * np.deg2rad(1.0), rel=1e-15)
    assert dogu == pytest.approx(6371000.0 * np.deg2rad(1.0) * np.cos(np.deg2rad(42.0)), rel=1e-15)
    # the documented bound: below 0.5 % of the horizontal distance for |Δ| <= 1°
    kuzey_b, dogu_b = ned_metre(42.0, 14.0, lat0_deg=42.0, lon0_deg=13.0)
    p1, p2 = np.deg2rad(42.0), np.deg2rad(42.0)
    l2 = np.deg2rad(14.0)
    gc = 6371000.0 * np.arccos(np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(l2 - np.deg2rad(13.0)))
    assert abs(np.hypot(kuzey_b, dogu_b) - gc) / gc < 0.005


def test_yerel_cerceve_doksan_derece():
    R = yerel_cerceve(0.0, 90.0)
    assert R @ np.array([1.0, 0.0, 0.0]) == pytest.approx([1.0, 0.0, 0.0], abs=1e-15)
    assert R @ np.array([0.0, 0.0, 1.0]) == pytest.approx([0.0, 1.0, 0.0], abs=1e-15)
    assert np.abs(R @ R.T - np.eye(3)).max() < 1e-15
    assert np.linalg.det(R) == pytest.approx(1.0, abs=1e-15)


def test_yerel_cerceve_fay_vektorleri_ile_ayni():
    from knotenlinie.defter.geometri import fay_vektorleri

    for dogrultu, egim in ((0.0, 45.0), (155.0, 30.0), (300.0, 70.0), (42.0, 90.0), (200.0, 10.0)):
        R = yerel_cerceve(dogrultu, egim)
        n, s0 = fay_vektorleri(dogrultu, egim, 0.0)
        _, s90 = fay_vektorleri(dogrultu, egim, 90.0)
        assert R[0] == pytest.approx(s0, abs=1e-14)          # x is the strike, rake 0
        assert R[1] == pytest.approx(-s90, abs=1e-14)        # y is down-dip, -rake 90
        assert R[2] == pytest.approx(-n, abs=1e-14)          # z is the fault normal
        assert np.abs(R @ R.T - np.eye(3)).max() < 1e-15


def test_voigt_donusum_elle():
    sigma_yerel = np.array([1.0, 4.0, 6.0, 2.0, 3.0, 5.0])
    dogrultu, egim = 30.0, 40.0
    R = yerel_cerceve(dogrultu, egim)
    m = np.array([[1.0, 2.0, 3.0], [2.0, 4.0, 5.0], [3.0, 5.0, 6.0]])
    beklenen = np.array([
        (R.T @ m @ R)[0, 0], (R.T @ m @ R)[1, 1], (R.T @ m @ R)[2, 2],
        (R.T @ m @ R)[0, 1], (R.T @ m @ R)[0, 2], (R.T @ m @ R)[1, 2],
    ])
    assert yerelden_nede(sigma_yerel, dogrultu, egim) == pytest.approx(beklenen, abs=1e-12)
    geri = nede_yerel(yerelden_nede(sigma_yerel, dogrultu, egim), dogrultu, egim)
    assert geri == pytest.approx(sigma_yerel, abs=1e-12)


def test_dud_gerilme_elle():
    dud = np.diag([1.0e-3, 2.0e-3, 3.0e-3])
    s = dud_gerilme(dud)
    tr = 6.0e-3
    assert s == pytest.approx([LAM * tr + 2 * MU * 1e-3, LAM * tr + 2 * MU * 2e-3,
                               LAM * tr + 2 * MU * 3e-3, 0.0, 0.0, 0.0], rel=1e-15)
    # an antisymmetric gradient is a rigid rotation: no strain, no stress
    omega = 1e-3
    dud = np.array([[0.0, -omega, 0.0], [omega, 0.0, 0.0], [0.0, 0.0, 0.0]])
    assert dud_gerilme(dud) == pytest.approx(np.zeros(6), abs=1e-9)


def test_fay_gerilmesi_defterin_aynen():
    from knotenlinie.defter.geometri import gerilmeyi_coz

    sigma = np.array([[10.0, 1.0, 2.0], [1.0, 20.0, 3.0], [2.0, 3.0, 30.0]])
    voigt = np.array([10.0, 20.0, 30.0, 1.0, 2.0, 3.0])
    n = np.array([0.3, -0.5, 0.81])
    n = n / np.linalg.norm(n)
    s = np.array([-0.6, 0.7, 0.39])
    s = s / np.linalg.norm(s)
    tau_a, sn_a = fay_gerilmesi(sigma, n, s)
    tau_b, sn_b = gerilmeyi_coz(sigma, n, s)
    assert tau_a == tau_b
    assert sn_a == sn_b
    tau_c, sn_c = fay_gerilmesi(voigt, n, s)
    assert tau_c == pytest.approx(tau_b, rel=1e-15)
    assert sn_c == pytest.approx(sn_b, rel=1e-15)
