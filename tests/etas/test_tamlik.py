"""Completeness tables, the Schuster test, small-N guard and the census cross-check."""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from knotenlinie.etas import katalog as K
from knotenlinie.etas import tamlik

N_MIN = 500


def _df(saat, mags):
    taban = pd.Timestamp("2000-01-01T00:00:00Z")
    t = [taban + pd.Timedelta(hours=float(h)) for h in saat]
    return pd.DataFrame({"time_utc": pd.to_datetime(t, utc=True), "mag": np.asarray(mags, float),
                         "lat": 42.0, "lon": 13.0, "depth_km": 8.0, "mag_type": "ML",
                         "source": "iside", "event_id": [str(i) for i in range(len(saat))],
                         "catalog_file": "syn.txt", "gun": np.asarray(saat, float) / 24.0})


def test_schuster_finds_injected_diurnal_deficit():
    rng = np.random.default_rng(4)
    # 900 events over 60 days, deficit in hours 0-5 (a diurnal detection hole)
    gunler = rng.integers(0, 60, 900)
    saat = rng.choice(np.arange(6, 24, 0.5), 900) + 0.25
    saat = saat % 24.0
    saat = saat + gunler * 24.0
    taban = pd.Timestamp("2000-01-01T00:00:00Z")
    df = _df(saat, 2.5 + rng.random(900))
    cikti = tamlik.saat_dilimi(df, mc=2.0, n_min=N_MIN)
    assert cikti["2.5"]["N"] >= N_MIN
    assert cikti["2.5"]["p"] < 0.05


def test_schuster_false_positive_control():
    rng = np.random.default_rng(5)
    saat = rng.random(1200) * 24.0
    taban = pd.Timestamp("2000-01-01T00:00:00Z")
    gunler = np.repeat(np.arange(50), 24)
    saat = (np.tile(np.arange(24), 50) + rng.random(1200) * 0.5) % 24.0
    df = _df(saat, 2.5 + rng.random(1200))
    cikti = tamlik.saat_dilimi(df, mc=2.0, n_min=N_MIN)
    assert cikti["2.5"]["p"] >= 0.05


def test_small_bin_returns_yetersiz():
    saat = np.random.default_rng(6).random(30) * 24.0
    df = _df(saat, np.full(30, 2.5))
    cikti = tamlik.saat_dilimi(df, mc=2.0, n_min=N_MIN)
    assert cikti["2.5"]["sonuc"] == tamlik.YETERSIZ_VERI


def _gr(n, b=1.0, m0=2.0, seed=8):
    """Gutenberg-Richter magnitudes above m0, rounded to 0.1 (complete from m0)."""
    return np.round(m0 - 0.05 + np.random.default_rng(seed).exponential(1.0 / (b * np.log(10)), n), 1)


def test_mc_two_methods_disagree_is_reported():
    df = _df(np.random.default_rng(7).random(3000) * 24.0, _gr(3000))
    ozet = tamlik.tamlik_ozet(df, mc_baslangic=2.0, m_buyuk=4.0, etasd_mc=3.0)
    assert ozet["ozet"]["uyusmuyor"] is True and ozet["ozet"]["uyum_farki"] > tamlik.UYUM_ESIGI
    ozet2 = tamlik.tamlik_ozet(df, mc_baslangic=2.0, m_buyuk=4.0, etasd_mc=ozet["ozet"]["mc"] + 0.05)
    assert ozet2["ozet"]["uyusmuyor"] is False


def test_mbs_gr_katalogunda_mc_tamlik_esigi():
    """MBS on a GR catalogue (b = 1, complete from 2.0, a detection taper below) finds Mc near 2.0."""
    rng = np.random.default_rng(21)
    m = np.round(0.95 + rng.exponential(1.0 / np.log(10), 200000), 1)
    tut = rng.random(m.size) < np.clip((m - 1.0) / 1.0, 0.0, 1.0)      # detection ramps to 1 at 2.0
    ww = tamlik.mc_wiemer_wyss(m[tut], baslangic=1.0)
    assert ww["kararli"] and 1.9 <= ww["mc"] <= 2.3, ww["mc"]
    assert abs(ww["b"] - 1.0) < 0.1


def test_mbs_kararsizsa_tavan_degil_yok_der():
    """No b-stable cutoff: mc is None (it once returned the search span's end, 3.75 on the compute server)."""
    m = np.round(2.0 + np.random.default_rng(8).random(600), 1)       # uniform, not GR
    ww = tamlik.mc_wiemer_wyss(m, baslangic=2.0)
    assert ww["mc"] is None and ww["kararli"] is False
    with pytest.raises(ValueError, match="no b-stable Mc"):
        tamlik.tamlik_ozet(_df(np.random.default_rng(7).random(600) * 24.0, m), 2.0, 4.0)
    boot = tamlik.mc_bootstrap(m, n_bootstrap=20, baslangic=2.0)
    assert boot["mc"] is None and boot["kararsiz"] == 20


def test_tur_kuyrugu_kapisi_buyuk_olaylar_baska_turdeyse_durur():
    """ML-only with the large events typed Mw (ISIDe 2005-2015) cuts the tail: the gate stops."""
    mags = _gr(4000, seed=3)
    df = _df(np.arange(mags.size, dtype=float), mags)
    df.loc[df["mag"] >= 3.5, "mag_type"] = np.where(np.arange(int((df["mag"] >= 3.5).sum())) % 3 == 0, "ML", "Mw")
    with pytest.raises(K.TurKuyruguHatasi, match="3.5"):
        K.tur_kuyrugu_kapisi(df, "ML", 2.0)
    temiz = _df(np.arange(mags.size, dtype=float), mags)
    paylar = K.tur_kuyrugu_kapisi(temiz, "ML", 2.0)
    assert paylar["[2.0, 2.5)"]["pay"] == 1.0
    assert all(v["pay"] is None for v in paylar.values() if v["n"] < K.KUYRUK_N_MIN)


def test_maksimum_egrilik_izgara_buyuklugu_dondurur():
    """The mode is a grid magnitude (2.0), not half a bin above it (2.05)."""
    assert tamlik.mc_maximum_egrilik(_gr(5000), baslangic=1.0) == 2.0
    assert tamlik.mc_maximum_egrilik(_gr(5000, m0=3.0), baslangic=2.0) == 3.0


def test_tamlik_mc_her_pencerede_gecerli():
    """Mc holds over the span: an early window complete from 3.0 lifts the pooled Mc to 3.0."""
    rng = np.random.default_rng(31)

    def pencere(n, mc, gun0):
        m = np.round(0.95 + rng.exponential(1.0 / np.log(10), n), 1)
        tut = rng.random(n) < np.clip((m - (mc - 1.0)) / 1.0, 0.0, 1.0)
        return m[tut], gun0 + rng.uniform(0, 5 * 365.0, int(tut.sum()))

    m1, g1 = pencere(400000, 3.0, 0.0)            # 2000-2004: complete from 3.0
    m2, g2 = pencere(400000, 2.0, 5 * 365.25)     # 2005-2009: complete from 2.0
    m, g = np.concatenate([m1, m2]), np.concatenate([g1, g2])
    df = _df(g * 24.0, m)
    ozet = tamlik.tamlik_ozet(df, mc_baslangic=1.0, m_buyuk=5.0)
    assert 2.9 <= ozet["ozet"]["mc"] <= 3.3 and ozet["ozet"]["mc"] >= ozet["ozet"]["mc_genel"]
    assert set(ozet["pencereler"]) == {"2000-2004", "2005-2009"}
    assert ozet["pencereler"]["2005-2009"]["mc"] <= 2.3
