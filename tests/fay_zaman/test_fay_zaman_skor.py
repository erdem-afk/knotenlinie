"""Skor kodu bilinen cevaplı sentetik dünyada (uzun_ah.satir)."""
from __future__ import annotations

import numpy as np
import pytest

from knotenlinie.karsilastir import uzun_ah


def test_bilinen_ig_ve_poisson_kimligi():
    n = 3
    lam_r = np.array([1.0, 1.0, 1.0])
    lam_a = np.array([2.0, 2.0, 2.0])
    ci, mi = np.array([0, 1]), np.array([1, 1])
    r = uzun_ah.satir(lam_a, lam_r, ci, mi, 0, n, bootstrap=200, ad_a='a', ad_r='r',
                      bolge='x', donem='d', tur='t')
    # IG = log2 − (6−3)/2; olay terimi log2; integral (toplam fark, N'ye bölünmeden) −3; şekil satırı 0
    assert r['IG'] == pytest.approx(np.log(2) - 1.5, abs=1e-12)
    assert r['IG_olay'] == pytest.approx(np.log(2), abs=1e-12)
    assert r['integral'] == pytest.approx(-3.0, abs=1e-12)
    assert r['IG_olay'] + r['integral'] / r['N'] == pytest.approx(r['IG'], abs=1e-12)
    assert r['IG_sekil'] == pytest.approx(0.0, abs=1e-12)
    assert (r['logL_aday'] - r['logL_taban']) / r['N'] == pytest.approx(r['IG'], rel=1e-12)


def test_sekil_satiri_toplam_esitler():
    # aday 3× toplam, ama yerinde: şekil satırı yalnız olay yerlerindeki oran farkını ölçer
    lam_r = np.array([1.0, 2.0, 1.0])
    lam_a = 3.0 * np.array([2.0, 1.0, 1.0])
    ci, mi = np.array([0, 0]), np.array([0, 0])
    r = uzun_ah.satir(lam_a, lam_r, ci, mi, 0, 3, bootstrap=100, ad_a='a', ad_r='r',
                      bolge='x', donem='d', tur='t')
    c = lam_r.sum() / lam_a.sum()
    assert r['IG_sekil'] == pytest.approx(np.log(lam_a[0] * c / lam_r[0]), abs=1e-12)
