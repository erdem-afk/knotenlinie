"""Reader, gates, regions, magnitude handling.

Every fixture is synthetic; no real catalog row is written or read.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

import json

from knotenlinie.etas import katalog as K
from knotenlinie.kanal import tektonik_kaynak as TK

BASLIK = K.ISIDE_HEADER


def _satir(t: str, lat=42.5, lon=13.0, m=2.0, tur="ML", eid="1") -> str:
    return f"{eid}|{t}|{lat}|{lon}|10.0|SYN|SYN|SYN|1|{tur}|{m}|SYN|SYNTHETIC|earthquake"


def _yaz(tmp_path, ad: str, satirlar):
    p = tmp_path / ad
    p.write_text(BASLIK + "\n" + "\n".join(satirlar) + "\n", encoding="utf-8")
    return str(p)


def _zincir(e):
    """Every message Python's default traceback would print, ``__cause__``/``__context__`` included."""
    out, x, gorulen = [], e, set()
    while x is not None and id(x) not in gorulen:
        gorulen.add(id(x))
        out.append(f"{type(x).__name__}: {x}")
        x = x.__cause__ if x.__cause__ is not None else (
            None if x.__suppress_context__ else x.__context__)
    return out


def test_a_synthetic_iside_parses_with_dtypes(tmp_path):
    yol = _yaz(tmp_path, "iside_2010.txt", [_satir("2010-03-01T04:05:06.000000", m=2.4, tur="ML")])
    df, rep = K.iside_oku(yol)
    assert list(df.columns) == ["time_utc", "lat", "lon", "depth_km", "mag", "mag_type", "source",
                                "event_id", "catalog_file"]
    # UTC at any resolution: pandas 3 (compute server) uses microseconds, which also holds CPTI15's pre-1677 events.
    assert str(df["time_utc"].dtype) in ("datetime64[ns, UTC]", "datetime64[us, UTC]")
    assert df["lat"].dtype == "float64" and df["mag"].dtype == "float64"
    assert df["mag_type"].iloc[0] == "ML" and df["source"].iloc[0] == "iside"
    assert df["catalog_file"].iloc[0] == "iside_2010.txt"
    assert rep["okunan"] == 1 and rep["tutulan"] == 1 and rep["atilan_kesim"] == 0
    assert K.kesim_temiz_mi(df) and K.muhur_temiz_mi(df)


def test_b_2021_row_raises_muhur(tmp_path):
    yol = _yaz(tmp_path, "iside_2015.txt",
               [_satir("2021-06-01T07:13:47.000000", eid="SEALID", m=7.7)])
    with pytest.raises(K.MuhurIhlali) as hata:
        K.iside_oku(yol)
    metin = " ".join(_zincir(hata.value))
    assert "SEALID" not in metin and "07:13:47" not in metin and "7.7" not in metin


def test_c_2016_to_2020_dropped_and_counted(tmp_path):
    yol = _yaz(tmp_path, "iside_2015.txt", [
        _satir("2015-12-31T23:59:59.999999", eid="a"),
        _satir("2016-01-01T00:00:00.000000", eid="b"),
        _satir("2018-06-01T00:00:00.000000", eid="c"),
        _satir("2020-12-31T23:59:59.000000", eid="d"),
    ])
    df, rep = K.iside_oku(yol)
    assert rep["okunan"] == 4 and rep["tutulan"] == 1 and rep["atilan_kesim"] == 3
    assert df["time_utc"].max() == K.KESIM
    assert df["event_id"].tolist() == ["a"]


def test_d_iside_2016_refused_unopened(tmp_path):
    # the file's content is invalid; if the adapter opened it, it would raise BicimHatasi
    p = tmp_path / "iside_2016.txt"
    p.write_text("not a catalog at all\n", encoding="utf-8")
    iyi = _yaz(tmp_path, "iside_2015.txt", [_satir("2015-01-01T00:00:00.000000")])
    df, rep = K.iside_oku([iyi, str(p)])
    assert "iside_2016.txt" in rep["acilmayan"]
    assert rep["acilan"] == ["iside_2015.txt"]
    assert rep["tutulan"] == 1
    # a broad glob over the same directory cannot open it either
    df2, rep2 = K.iside_oku(str(tmp_path / "iside_*.txt"))
    assert "iside_2016.txt" in rep2["acilmayan"] and len(df2) == 1


def test_e_cpti15_bad_header_raises_bicim(tmp_path):
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("foo,bar,baz\n1,2,3\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi):
        K.cpti15_oku(str(p))


def test_e3_cpti15_headerless_names_no_value(tmp_path):
    """A file with no header line names only the file and the missing column
    candidates, never its first data row (the old message quoted the header it saw)."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("2021,6,1,7,13,47,42.0,13.0,7.77,SEALEDID\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.cpti15_oku(str(p))
    metin = " ".join(_zincir(hata.value))
    assert "CPTI15_v4.0.csv" in str(hata.value) and "Year" in str(hata.value)
    assert str(tmp_path) not in str(hata.value)          # basename only, never the directory path
    assert all(t not in metin for t in ("SEALEDID", "7.77", "2021", "42.0", "13.0"))


def test_e4_iside_headerless_names_no_value(tmp_path):
    """A headerless ISIDe file quotes no value from its first row."""
    p = tmp_path / "iside_2015.txt"
    p.write_text("SEALEDID|2021-06-01T07:13:47.000000|42.8|13.2|10.0|a|c|c|c|ML|7.77|a|loc|earthquake\n",
                 encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.iside_oku(str(p))
    metin = " ".join(_zincir(hata.value))
    assert "iside_2015.txt" in str(hata.value)
    assert str(tmp_path) not in str(hata.value)          # basename only, never the directory path
    assert all(t not in metin for t in ("SEALEDID", "7.77", "2021-06", "42.8", "13.2"))


def test_e2_cpti15_good_candidate_header_parses(tmp_path):
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("Year,Mo,Dy,Hour,Lat,Lon,Depth,Mw,CPTI15_ID\n"
                 "1900,1,2,3,42.0,13.0,8.0,5.0,id1\n"
                 "2021,1,1,0,42.0,13.0,8.0,5.0,id2\n", encoding="utf-8")
    with pytest.raises(K.MuhurIhlali):
        K.cpti15_oku(str(p))
    p2 = tmp_path / "ok.csv"
    p2.write_text("Year,Mo,Dy,Hour,Lat,Lon,Depth,Mw,CPTI15_ID\n"
                  "1900,1,2,3,42.0,13.0,8.0,5.0,id1\n", encoding="utf-8")
    df, rep = K.cpti15_oku(str(p2))
    assert df["mag_type"].iloc[0] == "Mw" and df["source"].iloc[0] == "cpti15"
    assert df["time_utc"].iloc[0] == pd.Timestamp("1900-01-02T03:00:00Z")
    assert rep["tutulan"] == 1


def test_yil_dort_haneden_az_reddedilir(tmp_path):
    """a two-digit numeric year cannot be placed against the seal,
    so the CPTI15 and HORUS readers refuse it by row number, quoting no cell; 1005 (CPTI15's
    first year) is accepted."""
    p = tmp_path / "CPTI15_v4.0.csv"
    for y in ("21", "99"):
        p.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                     f"{y},1,1,42.0,13.0,5.0,id1\n", encoding="utf-8")
        with pytest.raises(K.BicimHatasi) as hata:
            K.cpti15_oku(str(p))
        metin = " ".join(_zincir(hata.value))
        assert "row 0" in str(hata.value) and "fewer than four digits" in metin
        assert f"{y},1,1" not in metin and "id1" not in metin
    p.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "1005,1,1,42.0,13.0,5.0,id1\n", encoding="utf-8")
    df, _ = K.cpti15_oku(str(p))
    assert int(df["time_utc"].iloc[0].year) == 1005
    for y in (21, 99):
        (tmp_path / "horus_1990.txt").write_text(_HORUS_BAS + _horus_satir(y), encoding="utf-8")
        with pytest.raises(K.BicimHatasi) as hata2:
            K.horus_oku(str(tmp_path / "horus_1990.txt"))
        metin2 = " ".join(_zincir(hata2.value))
        assert "[0]" in str(hata2.value) and "fewer than four digits" in metin2
        assert f"{y}.0000000000" not in metin2


def test_yil_tabani_muhur_sayimini_gizlemez(tmp_path):
    """the year floor never hides a
    sealed row's count -- a file with a two-digit year and a sealed row raises ``MuhurIhlali`` in
    both readers, whichever row comes first.  Three-digit years are refused too."""
    p = tmp_path / "CPTI15_v4.0.csv"
    for y in ("999", "100"):
        p.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                     f"{y},6,1,42.0,13.0,5.0,id1\n", encoding="utf-8")
        with pytest.raises(K.BicimHatasi, match="fewer than four digits"):
            K.cpti15_oku(str(p))
        (tmp_path / "horus_1990.txt").write_text(_HORUS_BAS + _horus_satir(y), encoding="utf-8")
        with pytest.raises(K.BicimHatasi, match="fewer than four digits"):
            K.horus_oku(str(tmp_path / "horus_1990.txt"))
    for yillar in (("21", "2021"), ("2021", "21")):
        p.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                     + "".join(f"{y},6,1,42.0,13.0,5.0,id{k}\n" for k, y in enumerate(yillar)),
                     encoding="utf-8")
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.cpti15_oku(str(p))
        (tmp_path / "horus_1990.txt").write_text(
            _HORUS_BAS + "".join(_horus_satir(y) for y in yillar), encoding="utf-8")
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.horus_oku(str(tmp_path / "horus_1990.txt"))


def test_yil_tabani_saat_muhur_sayimini_gizlemez(tmp_path):
    """a two-digit year beside a 2020-12-31 ``Ho = 24``
    row (whose parsed time rolls into 2021) still gives ``MuhurIhlali`` with count 1 in both
    readers, in both row orders -- the CPTI15 floor and the HORUS floor both wait for the
    parsed-time seal."""
    for sira in (("kisa", "saat"), ("saat", "kisa")):
        cpti = []
        horus = []
        for ad in sira:
            if ad == "kisa":
                cpti.append("21,6,1,,42.0,13.0,5.0,id2")
                horus.append(_horus_satir(21))
            else:
                cpti.append("2020,12,31,24,42.0,13.0,5.0,id1")
                horus.append(_horus_satir(2020, mo=12, da=31).replace(
                    "\t 12.0\t 30.0\t", "\t 24.0\t 30.0\t"))
        p = tmp_path / "CPTI15_v4.0.csv"
        p.write_text("Year,Mo,Da,Ho,LatDef,LonDef,MwDef,CPTI15_ID\n" + "\n".join(cpti) + "\n",
                     encoding="utf-8")
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.cpti15_oku(str(p))
        (tmp_path / "horus_1990.txt").write_text(_HORUS_BAS + "".join(horus), encoding="utf-8")
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.horus_oku(str(tmp_path / "horus_1990.txt"))


def test_f_region_filter_counts_exact(tmp_path):
    satirlar = [
        _satir("2010-01-01T00:00:00", lat=41.5, lon=12.0, m=3.0, eid="in1"),
        _satir("2010-01-02T00:00:00", lat=44.0, lon=14.5, m=2.5, eid="in2"),
        _satir("2010-01-03T00:00:00", lat=41.4, lon=13.0, m=9.0, eid="out1"),
        _satir("2010-01-04T00:00:00", lat=42.0, lon=14.6, m=9.0, eid="out2"),
    ]
    yol = _yaz(tmp_path, "iside_2010.txt", satirlar)
    df, _ = K.iside_oku(yol)
    ap = K.bolge_sec(df, "apennine")
    assert ap["event_id"].tolist() == ["in1", "in2"]
    assert K.sayim(df, "apennine", 3.0) == 1
    assert K.sayim(df, "italy", 2.0) == 4
    assert K.BOLGELER["apennine"] == (41.5, 44.0, 12.0, 14.5)


def test_g_tek_tur_sec_rule(tmp_path):
    satirlar = [_satir("2010-01-01T00:00:00", tur="ML", eid=str(i)) for i in range(96)]
    satirlar += [_satir("2010-01-02T00:00:00", tur="Mw", eid=f"w{i}") for i in range(4)]
    yol = _yaz(tmp_path, "iside_2010.txt", satirlar)
    df, _ = K.iside_oku(yol)
    assert K.tek_tur_sec(df, "apennine") == "ML"
    assert K.mag_turu_sayimi(df, "apennine")["pay"]["ML"] == pytest.approx(0.96)
    # a different dominant type at >= 0.95 wins
    s2 = [_satir("2010-01-01T00:00:00", tur="Mw", eid=str(i)) for i in range(99)]
    s2 += [_satir("2010-01-02T00:00:00", tur="ML", eid="x")]
    y2 = _yaz(tmp_path, "iside_2011.txt", s2)
    d2, _ = K.iside_oku(y2)
    assert K.tek_tur_sec(d2, "apennine") == "Mw"


def test_no_forbidden_third_party_imports():
    """The package must not pull AGPL/GPL/Fortran ETAS code or sklearn."""
    import sys
    import knotenlinie.etas  # noqa: F401
    from knotenlinie.etas import (ayristirma, benzetim, kalinti,  # noqa: F401
                            model, tamlik)
    yasak = [m for m in sys.modules if m.split(".")[0] in ("pyetas", "openquake", "rpy2", "sklearn")]
    assert yasak == [], f"forbidden modules imported: {yasak}"


def test_h_b_degeri_and_bootstrap():
    rng = np.random.default_rng(7)
    # continuous magnitudes: the binning correction is switched off (dm=0)
    beta = np.log(10.0)
    m = 2.0 + rng.exponential(1.0 / beta, 4000)
    r = K.b_degeri(m, mc=2.0, dm=0.0, n_bootstrap=200, seed=3)
    assert abs(r["deger"] - 1.0) < 0.05
    assert r["aralik95"][0] < r["deger"] < r["aralik95"][1]
    assert r["beta"] == pytest.approx(r["deger"] * np.log(10))
    # the declared binning correction shifts the effective threshold to mc - dm/2
    r2 = K.b_degeri(m, mc=2.0, dm=0.1, n_bootstrap=50, seed=3)
    assert r2["deger"] < r["deger"]


def test_i_gun_is_resolution_independent():
    """pandas 3 stores microseconds, pandas 2 nanoseconds; days must agree."""
    t = pd.Timestamp("2015-01-02T12:00:00Z")
    for birim in ("ns", "us", "s"):
        s = pd.Series([t]).astype(f"datetime64[{birim}, UTC]")
        assert K.gun(s)[0] == pytest.approx(16437.5, abs=1e-9)


def test_j_cpti15_real_header_names_parse(tmp_path):
    """The CPTI15 v4.0 header in the downloaded file uses LatDef / LonDef / MwDef / DepDef."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("N,Year,Mo,Da,Ho,Mi,Se,EpicentralArea,LatDef,LonDef,DepDef,MwDef\n"
                 "1,1703,2,2,11,5,,Aquilano,42.43,13.29,,6.7\n", encoding="utf-8")
    df, rep = K.cpti15_oku(str(p))
    assert float(df["lat"].iloc[0]) == pytest.approx(42.43) and float(df["mag"].iloc[0]) == pytest.approx(6.7)
    assert df["time_utc"].iloc[0] == pd.Timestamp("1703-02-02T11:05:00Z")


def test_k_cpti15_julian_dates_before_the_reform():
    """Known conversions: Julian 1582-10-04 is Gregorian 1582-10-14; Julian 1400-02-29 is 1400-03-09."""
    assert K.julyen_gregoryen(1582, 10, 4) == __import__("datetime").date(1582, 10, 14)
    assert K.julyen_gregoryen(1400, 2, 29) == __import__("datetime").date(1400, 3, 9)
    assert K.julyen_gregoryen(1400, 3, 1) == __import__("datetime").date(1400, 3, 10)
    assert K.julyen_gregoryen(1349, 9, 9) == __import__("datetime").date(1349, 9, 17)


def test_l_cpti15_hour_24_is_next_midnight(tmp_path):
    """CPTI15 has one 'Ho = 24' (1522-07-05); it is the next day's 00:00, not a parse error."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("N,Year,Mo,Da,Ho,Mi,Se,LatDef,LonDef,MwDef\n1,1703,7,5,24,,,42.4,13.3,5.0\n", encoding="utf-8")
    df, _ = K.cpti15_oku(str(p))
    assert df["time_utc"].iloc[0] == pd.Timestamp("1703-07-06T00:00:00Z")


def test_n_cpti15_non_numeric_magnitude_raises(tmp_path):
    """An empty MwDef is a missing parameter (NaN, handled upstream) but a
    non-empty cell that is not a number raises, naming the event id and the value."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text('Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n'
                 '1600,1,1,42.0,13.0,"6,1",virgul\n', encoding="utf-8")
    with pytest.raises(K.BicimHatasi, match="virgul"):
        K.cpti15_oku(str(p))
    q = tmp_path / "bos.csv"
    q.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "1600,1,1,42.0,13.0,,bos\n", encoding="utf-8")
    df, rep = K.cpti15_oku(str(q))
    assert rep["tutulan"] == 1 and bool(df["mag"].isna().all())


def test_o_cpti15_seal_before_magnitude(tmp_path):
    """The seal is checked on the parsed times before the magnitude check,
    so a sealed 2021 row with a malformed magnitude raises MuhurIhlali with a count only and the
    sealed row's id and value never appear in the message."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "1600,1,1,42.0,13.0,6.0,ok\n"
                 '2021,6,1,42.0,13.0,"6,1",MUHURLU-ID\n', encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata:
        K.cpti15_oku(str(p))
    assert "MUHURLU-ID" not in str(hata.value) and "6,1" not in str(hata.value)
    assert "2021-06" not in str(hata.value)
    assert "1 record(s)" in str(hata.value)


def test_o2_cpti15_seal_before_date_parse(tmp_path):
    """The year is parsed first and a year >= 2021 is sealed before the rest of
    the row, so a sealed row with a malformed hour (or an invalid calendar date) names neither its
    cell nor its id."""
    p = tmp_path / "CPTI15_v4.0_muhur_saat.csv"
    p.write_text("Year,Mo,Da,Ho,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "1600,1,1,,42.0,13.0,6.0,ok\n"
                 "2021,6,1,1a,42.0,13.0,6.1,MUHURLU-ID\n", encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata:
        K.cpti15_oku(str(p))
    metin_o2 = str(hata.value)
    assert "MUHURLU-ID" not in metin_o2 and "1a" not in metin_o2
    assert "2021-06" not in metin_o2 and "6.1" not in metin_o2
    assert "1 record(s)" in metin_o2
    q = tmp_path / "CPTI15_v4.0_muhur_gun.csv"
    q.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "1600,1,1,42.0,13.0,6.0,ok\n"
                 "2021,2,30,42.0,13.0,6.1,MUHURLU-ID\n", encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata2:
        K.cpti15_oku(str(q))
    assert "MUHURLU-ID" not in str(hata2.value)
    assert "2021-02" not in str(hata2.value) and "6.1" not in str(hata2.value)


def test_p_cpti15_infinite_magnitude_raises(tmp_path):
    """Inf/-inf/Infinity are not finite magnitudes and raise like any other
    unparseable non-empty cell; an empty cell is still a missing parameter."""
    for v in ("inf", "-inf", "Infinity"):
        p = tmp_path / "CPTI15_v4.0.csv"
        p.write_text("Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"
                     f'1600,1,1,42.0,13.0,"{v}",x\n', encoding="utf-8")
        with pytest.raises(K.BicimHatasi, match="x"):
            K.cpti15_oku(str(p))


def test_q_iside_non_numeric_magnitude_raises(tmp_path):
    """A non-numeric ISIDe magnitude raises by name (the shared ``_cerceve``
    stops the read where it used to coerce silently)."""
    for v in ("--", "nan"):
        yol = _yaz(tmp_path, "iside_2010.txt", [_satir("2010-01-01T00:00:00", m=v, eid="e1")])
        with pytest.raises(K.BicimHatasi, match="e1"):
            K.iside_oku(yol)


def test_mc_araligi_raporlanan_tahminciden():
    """The Mc interval brackets the Mc that is reported (b-value stability), not another estimator."""
    from knotenlinie.etas import tamlik as T
    rng = np.random.default_rng(3)
    tam = 2.0 + rng.exponential(1.0 / (1.0 * np.log(10)), 20000)          # complete above 2.0, b = 1
    eksik = rng.normal(1.8, 0.25, 4000)                                    # a soft roll-off below
    mags = np.round(np.concatenate([tam, eksik[eksik < 2.0]]), 1)
    ww = T.mc_wiemer_wyss(mags)
    boot = T.mc_bootstrap(mags, n_bootstrap=100)
    assert boot["aralik95"][0] <= ww["mc"] <= boot["aralik95"][1]


def test_tur_donemi_iside_md_den_ml_ye_gecis():
    """Md before 2005 and ML after it: the ML era starts 2005-01-01 even with stray ML earlier and
    a few Md later (the central-Apennine ISIDe pattern, compute server 2026-09-29)."""
    satir = []
    for y in range(1995, 2016):
        ml = 0 if y < 2005 else 100
        md = 100 if y < 2005 else 8
        if y == 1997:
            ml = 5
        satir += [(f"{y}-06-01T00:00:00Z", "ML")] * ml + [(f"{y}-06-01T00:00:00Z", "Md")] * md
    df = pd.DataFrame(satir, columns=["time_utc", "mag_type"])
    df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    assert K.tur_donemi_baslangic(df, "ML") == pd.Timestamp("2005-01-01", tz="UTC")
    with pytest.raises(K.BicimHatasi):
        K.tur_donemi_baslangic(df, "Md")


_HORUS_BAS = ("Year\tMo\tDa\tHo\tMi\tSe\tLat\tLon\tDepth\tMw\tsigMw\tGeo-Ita\tGeo-CPTI15\tEv. type\tIside n.\t\n")


def _horus_satir(y, mo=6, da=15, mw=2.5, tur=" ", iside=" "):
    return (f"     {y}.0000000000\t {mo}.0\t {da}.0\t 12.0\t 30.0\t 15.5\t 42.8\t 13.2\t 10.0\t {mw}\t 0.2"
            f"\t*\t*\t{tur}\t{iside}\t\n")


def test_horus_hour_minute_second_and_overflow_strict(tmp_path):
    """A non-numeric ``Mi`` or ``Se`` is refused by position (never read as 0),
    and a non-finite hour is a ``BicimHatasi`` with the traceback chain suppressed, so no cell text
    rides it."""
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("\t 30.0\t", "\t xx\t"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi, match="Mi") as h1:
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert "xx" not in " ".join(_zincir(h1.value))
    # the position is a plain Python int (``[0]``), not ``np.int64(0)`` under numpy 2
    assert "[0]" in str(h1.value) and "np.int64" not in " ".join(_zincir(h1.value))
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("\t 15.5\t", "\t yy\t"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi, match="Se") as h2:
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert "yy" not in " ".join(_zincir(h2.value))
    assert "[0]" in str(h2.value) and "np.int64" not in " ".join(_zincir(h2.value))
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("\t 12.0\t", "\t inf\t"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as h3:
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert "inf" not in " ".join(_zincir(h3.value))


def test_horus_year_with_letter_is_sealed(tmp_path):
    """A HORUS year whose leading four digits are >= 2021 is sealed like CPTI15;
    the id, the year cell and the row's time and value never appear."""
    (tmp_path / "horus_2015.txt").write_text(
        _HORUS_BAS + _horus_satir("2021a", iside="SEALEDID"), encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata:
        K.horus_oku(str(tmp_path / "horus_2015.txt"))
    metin = " ".join(_zincir(hata.value))
    assert "SEALEDID" not in metin and "2021a" not in metin and "06-15" not in metin and "2.5" not in metin


def test_horus_infinite_magnitude_raises(tmp_path):
    """The shared frame refuses an infinite HORUS magnitude by name."""
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("\t 2.5\t", "\t inf\t"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi, match="inf"):
        K.horus_oku(str(tmp_path / "horus_2014.txt"))


def test_horus_magnitude_strict(tmp_path):
    """HORUS magnitudes are strict (a manual count of non-numeric `Mw`
    cells is 0): a non-empty non-numeric or non-finite `Mw` on a kept, non-sealed row raises
    `BicimHatasi` naming the row, exactly as ISIDe does; an empty cell stays a missing parameter."""
    for v in ("--", "nan", "6,1", "1e999", "inf", "-inf", "Infinity"):
        (tmp_path / "horus_2014.txt").write_text(
            _HORUS_BAS + _horus_satir(2014, mw=v), encoding="utf-8")
        with pytest.raises(K.BicimHatasi):
            K.horus_oku(str(tmp_path / "horus_2014.txt"))
    # the row is named (as ISIDe names its own), and a non-earthquake row is not kept, so its
    # magnitude is never read
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014, mw="--", iside="rowid"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi, match="rowid"):
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014, mw="--", tur="x"), encoding="utf-8")
    df, rep = K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert rep["atilan_deprem_disi"] == 1 and len(df) == 0
    # an empty Mw stays a missing parameter (the ISIDe rule)
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("\t 2.5\t", "\t \t"), encoding="utf-8")
    df, rep = K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert rep["okunan"] == 1 and bool(df["mag"].isna().all())


def test_horus_non_numeric_hour_refused_and_seal_first(tmp_path):
    """A non-numeric HORUS hour/minute/second is refused, never read as 0; a
    2021 row with a malformed hour raises the seal first, and neither the id nor the cell text
    appears in the message."""
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("\t 12.0\t", "\t xx\t"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi, match="Ho") as ho:
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert "[0]" in str(ho.value) and "np.int64" not in " ".join(_zincir(ho.value))
    (tmp_path / "horus_2015.txt").write_text(
        _HORUS_BAS + _horus_satir(2021, iside="SEALID").replace("\t 12.0\t", "\t xx\t"),
        encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata:
        K.horus_oku(str(tmp_path / "horus_2015.txt"))
    assert "SEALID" not in str(hata.value) and "xx" not in str(hata.value)
    assert "06-15" not in str(hata.value) and "2.5" not in str(hata.value)
    # a 2020-12-31 row whose hour would roll into 2021 is sealed by the parsed time
    (tmp_path / "horus_2013.txt").write_text(
        _HORUS_BAS + _horus_satir(2020, mo=12, da=31).replace("\t 12.0\t 30.0\t", "\t 24.0\t 30.0\t"),
        encoding="utf-8")
    with pytest.raises(K.MuhurIhlali):
        K.horus_oku(str(tmp_path / "horus_2013.txt"))


def test_horus_calendar_message_no_year_cell(tmp_path):
    """The HORUS "no full calendar date" message gives the row position only,
    never the ``Year`` cell."""
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(1970).replace("\t 6.0\t 15.0\t", "\t \t \t"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    metin = " ".join(_zincir(hata.value))
    assert "no full calendar date" in metin and "1970" not in metin
    # the HORUS positions are plain Python ints under numpy 2 as well
    assert "[0]" in str(hata.value) and "np.int64" not in metin


def test_horus_oku_kapilar(tmp_path):
    """HORUS: Mw throughout, non-earthquakes dropped, 2016+ files unopened, a sealed time raises."""
    (tmp_path / "horus_2014.txt").write_text(_HORUS_BAS + _horus_satir(2014) + _horus_satir(2014, mw=3.1, iside="123"))
    (tmp_path / "horus_2015.txt").write_text(_HORUS_BAS + _horus_satir(2015) + _horus_satir(2015, tur="x"))
    (tmp_path / "horus_2016.txt").write_text(_HORUS_BAS + _horus_satir(2016))
    df, rep = K.horus_oku(str(tmp_path / "horus_*.txt"))
    assert len(df) == 3 and set(df["mag_type"]) == {"Mw"} and set(df["source"]) == {"horus"}
    assert rep["acilmayan"] == ["horus_2016.txt"] and rep["atilan_deprem_disi"] == 1
    assert str(df["time_utc"].iloc[0]) == "2014-06-15 12:30:15.500000+00:00"
    assert "123" in set(df["event_id"])
    (tmp_path / "horus_2013.txt").write_text(_HORUS_BAS + _horus_satir(2021))
    with pytest.raises(K.MuhurIhlali):
        K.horus_oku(str(tmp_path / "horus_2013.txt"))


def test_horus_cpti15_ile_birlesir(tmp_path):
    """HORUS times are microseconds, so they concatenate with a year-1005 row (the compute-server census fell here)."""
    (tmp_path / "horus_2014.txt").write_text(_HORUS_BAS + _horus_satir(2014))
    df, _ = K.horus_oku(str(tmp_path / "horus_*.txt"))
    eski = pd.DataFrame({"time_utc": pd.Series(np.array(["1005-01-07"], dtype="datetime64[us]")).dt.tz_localize("UTC")})
    birlesik = pd.concat([df[["time_utc"]], eski], ignore_index=True)
    assert birlesik["time_utc"].min().year == 1005


def test_l_cpti15_1349_in_microseconds(tmp_path):
    """CPTI15's 1349 rows read under pandas 2 too (microseconds), time of day kept, seal intact."""
    p = tmp_path / "cpti15.csv"
    p.write_text("Year,Mo,Da,Ho,Mi,Se,Lat,Lon,MwDef,DepDef\n"
                 "1349,9,9,,,,41.5,13.9,6.8,\n"
                 "1915,1,13,6,52,,42.0,13.5,7.0,\n", encoding="utf-8")
    df, rep = K.cpti15_oku(str(p))
    assert str(df["time_utc"].dtype) == "datetime64[us, UTC]"
    assert df["time_utc"].iloc[0].year == 1349
    assert (df["time_utc"].iloc[1].hour, df["time_utc"].iloc[1].minute) == (6, 52)
    q = tmp_path / "cpti15_muhur.csv"
    q.write_text("Year,Mo,Da,Ho,Mi,Se,Lat,Lon,MwDef,DepDef\n"
                 "1349,9,9,,,,41.5,13.9,6.8,\n"
                 "2020,12,31,24,0,0,42.0,13.5,5.0,\n", encoding="utf-8")
    with pytest.raises(K.MuhurIhlali):
        K.cpti15_oku(str(q))


def test_iside_malformed_time_refused(tmp_path):
    """An unparsed or blank ISIDe Time raises ``BicimHatasi`` with positions only;
    a sealed but unparseable time raises ``MuhurIhlali`` (count only).  Neither message carries the
    sealed row's id, time or value."""
    yol = _yaz(tmp_path, "iside_2015.txt", [
        _satir("2015-06-01T01:01:01.000000", eid="ok"),
        _satir("", eid="NOTIME", m=4.4)])
    with pytest.raises(K.BicimHatasi) as hata:
        K.iside_oku(yol)
    assert "NOTIME" not in str(hata.value) and "4.4" not in str(hata.value)
    yol2 = _yaz(tmp_path, "iside_2015.txt", [
        _satir("2015-06-01T01:01:01.000000", eid="ok"),
        _satir("2021-06-01T25:13:47.000000", eid="SEALID", m=7.7)])
    with pytest.raises(K.MuhurIhlali) as hata2:
        K.iside_oku(yol2)
    assert "SEALID" not in str(hata2.value) and "25:13" not in str(hata2.value)
    assert "7.7" not in str(hata2.value)


def test_iside_format_message_positions_no_cell(tmp_path):
    """An ISIDe format error gives real row positions and no cell text,
    and the traceback chain is suppressed."""
    yol = _yaz(tmp_path, "iside_2015.txt", [
        _satir("2015-06-01T01:01:01.000000", eid="ok"),
        _satir("zq9-leak", eid="BADID", m=4.4)])
    with pytest.raises(K.BicimHatasi) as hata:
        K.iside_oku(yol)
    metin = " ".join(_zincir(hata.value))
    assert "zq9-leak" not in metin and "BADID" not in metin and "4.4" not in metin
    assert "rows [1]" in str(hata.value)


def test_cpti15_2019_2020_read_then_cut(tmp_path):
    """A year gate that also sealed 2020 would refuse this file.  Rows 2019 and
    2020-12-31T23:59:59 are read and then cut at the 2015 cutoff."""
    p = tmp_path / "cpti15.csv"
    p.write_text("Year,Mo,Da,Ho,Mi,Se,Lat,Lon,MwDef,CPTI15_ID\n"
                 "2015,1,1,,,,42.0,13.0,5.0,a\n"
                 "2019,6,1,,,,42.0,13.0,5.0,b\n"
                 "2020,12,31,23,59,59,42.0,13.0,5.0,c\n", encoding="utf-8")
    df, rep = K.cpti15_oku(str(p))
    assert rep["okunan"] == 3 and rep["tutulan"] == 1 and rep["atilan_kesim"] == 2
    assert df["event_id"].tolist() == ["a"]


def test_cpti15_malformed_time_names_no_cell(tmp_path):
    """A malformed year/hour/minute raises a format or seal error with the row
    position only, never the id or the cell (also year ``inf``/``1e999``, ``OverflowError``)."""
    cases = [
        ("2021a,6,1,7,13,47,42.0,13.0,6.1,SEALID\n", K.MuhurIhlali),
        ("1600,1,1,1a,13,47,42.0,13.0,6.1,SEALID\n", K.BicimHatasi),
        ("inf,6,1,7,13,47,42.0,13.0,6.1,SEALID\n", K.BicimHatasi),
        ("1600,1,1,1e20,13,47,42.0,13.0,6.1,SEALID\n", K.BicimHatasi),
    ]
    for satir, hata_tipi in cases:
        p = tmp_path / "CPTI15_v4.0.csv"
        p.write_text("Year,Mo,Da,Ho,Mi,Se,LatDef,LonDef,MwDef,CPTI15_ID\n" + satir,
                     encoding="utf-8")
        with pytest.raises(hata_tipi) as hata:
            K.cpti15_oku(str(p))
        metin = " ".join(_zincir(hata.value))
        assert all(t not in metin for t in ("SEALID", "2021a", "1a", "1e20", "6.1"))


def test_okuyucu_yil_onek_yalniz_onek(tmp_path):
    """The readers' own leading-year rule is a prefix rule (``re.match``).  A
    year cell whose first four digits are not at the start but which contains a sealed year later is
    *not* sealed; the prefix rule refuses it as a format error, while ``re.search`` would seal it
    (only the frame copy was pinned before)."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("Year,Mo,Da,Ho,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "zq9-2222,1,1,0,42.0,13.0,5.0,BADID\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.cpti15_oku(str(p))
    metin = " ".join(_zincir(hata.value))
    assert "BADID" not in metin and "zq9-2222" not in metin
    (tmp_path / "horus_2014.txt").write_text(
        _HORUS_BAS + _horus_satir(2014).replace("2014.0000000000", "zq9-2222"), encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata2:
        K.horus_oku(str(tmp_path / "horus_2014.txt"))
    assert "zq9-2222" not in " ".join(_zincir(hata2.value))


def test_cpti15_year_message_no_cell_and_blank_refused(tmp_path):
    """A non-numeric year is refused with the row position only (no
    cell, no id, no chained traceback), and a blank year is a ``BicimHatasi``,
    not a ``TypeError`` escaping the reader."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text("Year,Mo,Da,Ho,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 "zq9,1,1,0,42.0,13.0,5.0,BADID\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.cpti15_oku(str(p))
    metin = " ".join(_zincir(hata.value))
    assert "zq9" not in metin and "BADID" not in metin and "5.0" not in metin
    assert "row 0" in str(hata.value)
    q = tmp_path / "CPTI15_v4.0_bos.csv"
    q.write_text("Year,Mo,Da,Ho,LatDef,LonDef,MwDef,CPTI15_ID\n"
                 ",1,1,0,42.0,13.0,5.0,BADID\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata2:
        K.cpti15_oku(str(q))
    assert "BADID" not in str(hata2.value)


def test_yil_onek_ortak_durum_listesi():
    """The shared literal case list of the narrowed leading-year rule, checked against both copies of
    ``_yil_onek`` (``knotenlinie.etas.katalog`` and ``knotenlinie.kanal.tektonik_kaynak``).  Text is
    optional whitespace then four digits; bytes are decoded as UTF-8 first; a numeric cell is
    excluded; a Period/Interval is read by its endpoints; every other value counts nothing.  Both
    copies must give identical results on this list, which includes the big-endian BOM and the listed
    default-ignorables."""
    durumlar = [
        ("2021-06-01T07:13:47Z", 2021), (" 2021-03", 2021), ("1999-01-01", 1999),
        ("2020-12-31T23:59:59Z", 2020), ("+2021-06-01", None), ("-2021", None),
        ("ID-2500", None), ("zq9-2222", None), ("T2021-06-01 07:13:47", None),
        (b"2021-02", 2021), (b"1991-11-11", 1991), (b"\xff\xfe2021", None),
        (2021, None), (2021.0, None), (-2021, None), (np.float64(2021.0), None),
        (pd.Period("2021-06", "M"), 2021), (pd.Period("2020-12-28", "W"), 2021),
        (pd.Period("1990-01", "M"), 1990),
        (pd.Interval(pd.Timestamp("2020-12-31"), pd.Timestamp("2021-01-05")), 2021),
        (pd.Interval(pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")), 2020),
        (pd.Interval(2021, 2022), None),
        (complex(2021, 0), None), ([2021], None), ((2500, 1), None), ({"y": 2021}, None),
        (pd.Timedelta(2021, "D"), None), (pd.Timedelta(25000, "D"), None),
        # a leading BOM/ZWSP is stripped; bytearray/memoryview are bytes
        ("\ufeff2021-02-30T07:13:47Z", 2021), ("\u200b2021-02-30T07:13:47Z", 2021),
        (bytearray(b"2021-06-01T07:13:47Z"), 2021),
        (memoryview(b"2021-06-01T07:13:47Z"), 2021),
        # date objects by their UTC year, naive as UTC
        (dt.date(2021, 6, 1), 2021), (dt.date(2500, 6, 1), 2500),
        (dt.datetime(2021, 6, 1, 7, 13, 47), 2021),
        (dt.datetime(2021, 6, 1, 7, 13, 47, tzinfo=dt.timezone.utc), 2021),
        (dt.datetime(1000, 1, 1), 1000), (np.datetime64("2021-06-01T07:13:47"), 2021),
        (np.datetime64("2500-01-01"), 2500), (pd.Timestamp("2021-06-01T07:13:47Z"), 2021),
        (pd.Timestamp("2021-01-01 01:00", tz="Asia/Kolkata"), 2020),
        # a leading category-Cf character is stripped in a loop; a space
        # before a BOM is stripped too; UTF-16 bytes carrying a BOM are decoded as UTF-16
        ("\u20602021-02-30T07:13:47Z", 2021), ("\u200c2021-02-30T07:13:47Z", 2021),
        ("\u00ad2021-02-30T07:13:47Z", 2021), (" \ufeff2021-02-30T07:13:47Z", 2021),
        ("2021-06-01T07:13:47Z".encode("utf-16"), 2021),
        # the big-endian BOM decodes too
        (b"\xfe\xff" + "2021-06-01".encode("utf-16-be"), 2021),
        # the listed default-ignorables are stripped as well
        ("\u034f2021-02-30T07:13:47Z", 2021), ("\ufe0f2021-02-30T07:13:47Z", 2021),
        ("\u115f2021-02-30T07:13:47Z", 2021), ("\u3164\u200b2021-02-30T07:13:47Z", 2021),
        # one case for each remaining range (U+E0000-E0FFF, U+FFA0, U+17B4-U+17B5)
        ("\U000E01002021-02-30T07:13:47Z", 2021), ("\uffa02021-02-30T07:13:47Z", 2021),
        ("\u17b42021-02-30T07:13:47Z", 2021),
        # the astimezone overflow keeps the value's own year (9999), not None
        (dt.datetime(9999, 12, 31, 23, tzinfo=dt.timezone(dt.timedelta(hours=-2))), 9999),
    ]
    assert [K._yil_onek(v) for v, _ in durumlar] == [b for _, b in durumlar]
    assert [TK._yil_onek(v) for v, _ in durumlar] == [b for _, b in durumlar]


def test_uc_yili_utc_kaymasi_okuyucu():
    """The readers' ``_uc_yili`` converts an aware interval endpoint
    to UTC before reading the year.  US/Eastern 20:00-22:00 on 2020-12-31 is 2021 in UTC (sealed);
    Asia/Kolkata 01:00-02:00 on 2021-01-01 is still 2020 in UTC.  Dropping the conversion survives
    the old suite and is a real difference."""
    dogu = pd.Interval(pd.Timestamp("2020-12-31 20:00", tz="America/New_York"),
                       pd.Timestamp("2020-12-31 22:00", tz="America/New_York"))
    kolkata = pd.Interval(pd.Timestamp("2021-01-01 01:00", tz="Asia/Kolkata"),
                          pd.Timestamp("2021-01-01 02:00", tz="Asia/Kolkata"))
    assert K._uc_yili(dogu) == 2021 and K._uc_yili(kolkata) == 2020
    assert K._yil_onek(dogu) == 2021 and K._yil_onek(kolkata) == 2020


def test_okuyucu_period_ns_araligi_disinda_guvenli():
    """In the readers' copy: a Period beyond pandas 2's nanosecond
    range reads its daily-frequency year instead of raising ``OutOfBoundsDatetime`` with the sealed
    date in the message."""
    for deger, yil in ((pd.Period("3000-01", "M"), 3000), (pd.Period("2500-06-01", "D"), 2500),
                       (pd.Period("1000-01", "M"), 1000)):
        assert K._uc_yili(deger) == yil and K._yil_onek(deger) == yil


def test_iside_tam_muhur_ani(tmp_path):
    """An ISIDe row at exactly 2021-01-01T00:00:00Z raises the seal,
    so the reader's own ``>=`` comparison cannot become ``>``.  The id and value never appear."""
    yol = _yaz(tmp_path, "iside_2015.txt",
               [_satir("2021-01-01T00:00:00.000000", eid="BOUNDARY", m=6.17)])
    with pytest.raises(K.MuhurIhlali) as hata:
        K.iside_oku(yol)
    metin = " ".join(_zincir(hata.value))
    assert "BOUNDARY" not in metin and "6.17" not in metin


def test_horus_tam_muhur_ani(tmp_path):
    """a HORUS row whose parsed time is exactly 2021-01-01T00:00:00Z
    (year 2020, 24:00) raises the seal.  With ``>`` it would be dropped by the 2015 cutoff instead,
    so this kills the readers' ``horus_oku`` comparison mutant."""
    (tmp_path / "horus_2013.txt").write_text(
        _HORUS_BAS + _horus_satir(2020, mo=12, da=31, iside="SEALEDID").replace(
            "\t 12.0\t 30.0\t 15.5\t", "\t 24.0\t 0.0\t 0.0\t"), encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata:
        K.horus_oku(str(tmp_path / "horus_2013.txt"))
    metin = " ".join(_zincir(hata.value))
    assert "SEALEDID" not in metin and "24.0" not in metin


def test_muhur_temiz_mi_tam_muhur_ani():
    """``muhur_temiz_mi`` asserts on a row at exactly
    2021-01-01T00:00:00Z; with ``>`` the assert would not fire."""
    df = pd.DataFrame({"time_utc": pd.to_datetime(["2021-01-01T00:00:00Z"], utc=True)})
    with pytest.raises(AssertionError):
        K.muhur_temiz_mi(df)
    temiz = pd.DataFrame({"time_utc": pd.to_datetime(["2020-12-31T23:59:59.999999Z"], utc=True)})
    assert K.muhur_temiz_mi(temiz)


def test_iside_taninmayan_zaman_dilimi_reddedilir(tmp_path):
    """On pandas 2 the ISIDe reader would
    read a "2020-12-31T20:00:00 EST" row's wall time as UTC (2020, then dropped by the cutoff)
    instead of refusing it; the shared column parse now refuses it by position, as pandas 3 does.
    The real instant is 2021-01-01T01:00Z.  A 2021-leading CET cell is NaT and counted by the
    leading-year rule (count 1) on both pandas versions.  No id, time or value is quoted."""
    for i, hucre in enumerate(("2020-12-31T20:00:00 EST", "2020-12-31T22:30:00 PST")):
        yol = _yaz(tmp_path, f"iside_{2014 - i}.txt", [_satir(hucre, eid="SEALEDID", m=6.17)])
        with pytest.raises(K.BicimHatasi) as hata:
            K.iside_oku(yol)
        metin = " ".join(_zincir(hata.value))
        assert "SEALEDID" not in metin and "6.17" not in metin and "20:00" not in metin
    yol = _yaz(tmp_path, "iside_2012.txt",
               [_satir("2021-01-01T00:30:00 CET", eid="SEALEDID", m=6.17)])
    with pytest.raises(K.MuhurIhlali) as hata2:
        K.iside_oku(yol)
    metin2 = " ".join(_zincir(hata2.value))
    assert "1 record(s)" in metin2
    assert "SEALEDID" not in metin2 and "6.17" not in metin2 and "00:30" not in metin2


def test_iside_iki_hane_yil_reddedilir(tmp_path):
    """The ISIDe reader refuses a text date cell with no four-digit
    year by position, before any parse, quoting nothing (the id, value and cell never appear)."""
    yol = _yaz(tmp_path, "iside_2015.txt", [_satir("21/01/01 07:13", eid="SEALEDID", m=6.17)])
    with pytest.raises(K.BicimHatasi) as hata:
        K.iside_oku(yol)
    metin = " ".join(_zincir(hata.value))
    assert "[0]" in str(hata.value)
    assert "SEALEDID" not in metin and "6.17" not in metin and "21/01" not in metin


def test_iside_uyari_zaman_cozumlemesinden_sizmaz(tmp_path):
    """The
    ISIDe reader's time parse runs with pandas warnings recorded and never shown, so an unrecognised
    timezone abbreviation never prints the sealed string; the cell becomes ``NaT`` and is then
    counted by its leading year (a 2021-leading cell gives ``MuhurIhlali`` with count 1), with no
    id, time or value in the message."""
    yol = _yaz(tmp_path, "iside_2015.txt",
               [_satir("2021-06-01T07:13:47 CET", eid="SEALEDID", m=6.17)])
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with pytest.raises(K.MuhurIhlali) as hata:
            K.iside_oku(yol)
    metin = " ".join(_zincir(hata.value)) + " " + " ".join(str(x.message) for x in w)
    assert "2021-06" not in metin and "07:13" not in metin and "13:47" not in metin
    assert "SEALEDID" not in metin and "6.17" not in metin


def test_zaman_parsisi_kilidi_paylasilir():
    """The reader's suppressed parses use the one lock defined in
    ``knotenlinie.kanal.tektonik_kaynak``, not a per-copy lock (kills the per-copy-lock mutant)."""
    from knotenlinie.kanal import tektonik_kaynak as TK

    assert K._ZAMAN_KILIDI is TK._ZAMAN_KILIDI


def test_astimezone_tasmasi_yili_sayar_okuyucu():
    """In the readers' copy: converting ``9999-12-31T23:00-02:00`` to
    UTC overflows the year range, so the fallback keeps the value's own year (9999); returning
    ``None`` would leave the sealed value uncounted."""
    deger = dt.datetime(9999, 12, 31, 23, tzinfo=dt.timezone(dt.timedelta(hours=-2)))
    assert K._yil_onek(deger) == 9999


def test_yil_onek_naive_utc_kolkata_okuyucu():
    """In the readers' copy: a naive date object is read as UTC.  Under
    ``TZ=Asia/Kolkata`` a naive ``datetime(2021,1,1,3)`` is still 2021 (kills the naive-as-local
    mutant, which a UTC host cannot see)."""
    import subprocess

    kod = ("import os, time\n"
           "os.environ['TZ'] = 'Asia/Kolkata'\n"
           "time.tzset()\n"
           "import datetime as dt\n"
           "from knotenlinie.etas import katalog as K\n"
           "print(K._yil_onek(dt.datetime(2021, 1, 1, 3)), "
           "K._yil_onek(dt.datetime(2020, 12, 31, 23)), time.strftime('%z'))\n")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    kok = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sonuc = subprocess.run([sys.executable, "-c", kod], cwd=kok,
                           capture_output=True, text=True, env=env)
    assert sonuc.returncode == 0, sonuc.stderr
    # the zone must have taken effect, or the test is vacuous
    assert sonuc.stdout.strip() == "2021 2020 +0530"


def test_iside_metin_yil_tabani(tmp_path, monkeypatch):
    """``iside_oku``'s text year floor is pinned on both
    pandas versions without the emulation -- a one-row file with the sealed EXIF cell (parse
    monkeypatched to year 1) counts the record, and a file whose second row parses to year 1 is
    refused by position naming row ``[1]``, with no cell text."""
    Y = "20" + "21"
    exs = f"{Y}:06:01 07:13:47"
    yil1 = pd.Timestamp("0001-06-01", tz="UTC")

    def _tabanli(seri):
        degerler = []
        for v in (seri.to_numpy() if isinstance(seri, pd.Series) else list(seri)):
            if str(v) in ("June", exs):
                degerler.append(yil1)
            else:
                degerler.append(pd.Timestamp("1990-01-01T00:00:00Z"))
        return (pd.Series(degerler, index=seri.index, dtype="datetime64[us, UTC]"),
                np.zeros(len(degerler), dtype=bool))

    monkeypatch.setattr(K, "_zaman_sutunu_canli", _tabanli)
    yol = tmp_path / "iside_1990.txt"
    yol.write_text(BASLIK + "\n"
                   f"SEALED|{exs}|42.0|13.0|5.0|X||||ML|6.0|--|loc|earthquake\n",
                   encoding="utf-8")
    with pytest.raises(K.MuhurIhlali) as hata:
        K.iside_oku(str(yol))
    assert "1 record" in str(hata.value)
    assert exs not in " ".join(_zincir(hata.value))
    yol2 = tmp_path / "iside_1991.txt"
    yol2.write_text(BASLIK + "\n"
                    "A|1990-01-01T00:00:00Z|42.0|13.0|5.0|X||||ML|3.0|--|loc|earthquake\n"
                    "B|June|42.0|13.0|5.0|X||||ML|3.1|--|loc|earthquake\n",
                    encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata2:
        K.iside_oku(str(yol2))
    assert "rows [1]" in str(hata2.value) and "June" not in " ".join(_zincir(hata2.value))


def test_horus_taban_satiri_muhru_gizlemez(tmp_path):
    """The year-floor rows are outside the calendar and
    time parse, so a malformed floor row -- a bad calendar, a missing hour or
    an overflowing hour -- cannot hide a sealed ``Ho = 24`` row; both row orders give
    ``MuhurIhlali`` with count 1."""
    def _taban_bozuk(y, tur):
        s = _horus_satir(y)
        if tur == "takvim":
            return s.replace("\t 6.0\t 15.0\t 12.0\t", "\t xx\t \t yy\t")
        return s.replace("\t 12.0\t 30.0\t", "\t 1e30\t 30.0\t")

    saat = _horus_satir(2020, mo=12, da=31).replace("\t 12.0\t 30.0\t", "\t 24.0\t 30.0\t")
    for sira in (("kisa", "saat"), ("saat", "kisa")):
        for tur in ("takvim", "saat"):
            parcalar = [_taban_bozuk(21, tur) if ad == "kisa" else saat for ad in sira]
            p = tmp_path / "horus_1990.txt"
            p.write_text(_HORUS_BAS + "".join(parcalar), encoding="utf-8")
            with pytest.raises(K.MuhurIhlali, match="1 record") as hata:
                K.horus_oku(str(p))
            assert _horus_satir(21)[:20] not in " ".join(_zincir(hata.value))


# --- reader checks G, E' and H ------------------------------------------------------------

_MUHUR_Y_A = "20" + "21"
_CPTI_BASLIK = "Year,Mo,Da,LatDef,LonDef,MwDef,CPTI15_ID\n"


def test_iside_g1_g2_muhurlu_metin_sayilir(tmp_path):
    """Through ``iside_oku``: a sealed year right after
    a comma or a dot is seen, and the one-year margin counts a ``2020`` time before a sealed date;
    every cell gives ``MuhurIhlali`` "1 record" and no cell text appears in the chain."""
    Y = _MUHUR_Y_A
    hucreler = [f"1713 Jun 1,{Y}", f"1713 1 Jun,{Y}", f"1713 June 1,{Y}", f"1713 01-Jun.{Y}",
                f"1713 Jun. 1,{Y}", f"1713 Mon,1 Jun,{Y}", f"2013 Jun 1,{Y}", f"1713,{Y} Jun 01",
                f"1713,{Y}0601", f"2020 01 Jun {Y}", f"2020 Jun 1, {Y}", f"T2020 01 Jun {Y}",
                f"01 Jun 2020 {Y}"]
    for h in hucreler:
        yol = _yaz(tmp_path, "iside_1990.txt", [_satir(h)])
        with pytest.raises(K.MuhurIhlali) as hata:
            K.iside_oku(yol)
        assert "1 record" in str(hata.value)
        assert h not in " ".join(_zincir(hata.value))


def test_iside_e_ust_b_once_muhur(tmp_path):
    """Through ``iside_oku``: a flagged
    ``HHMM``-first sealed cell is counted before the four-digit-year refusal."""
    Y = _MUHUR_Y_A
    for h in (f"0713 01 Jun {Y}", f"0000 01 Jun {Y}", f"0013 Jun 1, {Y}", f"0713 {Y}-06-01",
              f"071347 01 Jun {Y}"):
        yol = _yaz(tmp_path, "iside_1990.txt", [_satir(h)])
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.iside_oku(yol)
        ikiz = h.replace(Y, "2015")
        yol2 = _yaz(tmp_path, "iside_1991.txt", [_satir(ikiz)])
        with pytest.raises(K.BicimHatasi, match="year-floor rule"):
            K.iside_oku(yol2)


def test_iside_e_ust_karisik_sutun_tam_sayim(tmp_path):
    """Through ``iside_oku``: every cell of a column is
    counted by its leading year before the refusal."""
    Y = _MUHUR_Y_A
    hucreler = [Y + "060107 13 47", Y + "-06-01T00:00:00", Y + "-07-01T00:00:00"]
    yol = _yaz(tmp_path, "iside_1990.txt", [_satir(h) for h in hucreler])
    with pytest.raises(K.MuhurIhlali, match="3 record"):
        K.iside_oku(yol)
    yol2 = _yaz(tmp_path, "iside_1992.txt", [_satir("21/01/01"), _satir(Y + "-06-01T00:00:00")])
    with pytest.raises(K.MuhurIhlali, match="1 record"):
        K.iside_oku(yol2)


def test_h_cpti15_bozuk_satir_muhru_gizlemez(tmp_path):
    """``cpti15_oku`` collects rows whose year or date
    does not parse and raises the seal count first, so a sealed row elsewhere in the file is
    counted; the sealed row is counted from its year alone, its other cells unread."""
    Y = _MUHUR_Y_A
    for satirlar in ([f"{Y},6,1,42.0,13.0,5.0,SEALID",
                      "1990,xx,1,42.0,13.0,5.0,BADID"],
                     ["1990,xx,1,42.0,13.0,5.0,BADID",
                      f"{Y},6,1,42.0,13.0,5.0,SEALID"],
                     [f"{Y},6,1,42.0,13.0,5.0,SEALID",
                      "abc,6,1,42.0,13.0,5.0,BADID"]):
        p = tmp_path / "CPTI15_v4.0.csv"
        p.write_text(_CPTI_BASLIK + "\n".join(satirlar) + "\n", encoding="utf-8")
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.cpti15_oku(str(p))


def test_h_cpti15_bozuk_satir_reddi(tmp_path):
    """a file with only the malformed row keeps its ``BicimHatasi``
    and row number, and a seven-row file names the first row and at most five positions, never a
    cell."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text(_CPTI_BASLIK + "1990,xx,1,42.0,13.0,5.0,BADID\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.cpti15_oku(str(p))
    metin = " ".join(_zincir(hata.value))
    assert "row 0" in str(hata.value)
    assert "xx" not in metin and "BADID" not in metin
    q = tmp_path / "CPTI15_v4.0_uzun.csv"
    q.write_text(_CPTI_BASLIK + "".join(
        f"abc{i},6,1,42.0,13.0,5.0,BAD{i}\n" for i in range(7)), encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata2:
        K.cpti15_oku(str(q))
    metin2 = " ".join(_zincir(hata2.value))
    assert "rows [0, 1, 2, 3, 4]" in str(hata2.value)
    assert "5]" not in str(hata2.value).split("rows")[-1]
    assert all(f"BAD{i}" not in metin2 for i in range(7))


# --- checks J, E'', the pins and docs -------------------------------------------------------

_MUHUR_Y = "20" + "21"


def _iside_hucreleri(tmp_path, hucreler, ad="iside_1990"):
    """A one-file ISIDe catalogue of the cells (synthetic; never a real row)."""
    return _yaz(tmp_path, ad + ".txt", [_satir(h) for h in hucreler])


@pytest.mark.parametrize("hucre", ["1713 01 Jun " + _MUHUR_Y, "2013 Jun 1," + _MUHUR_Y,
                                    "2020 01 Jun " + _MUHUR_Y], ids=["E2-0", "E2-1", "E2-2"])
def test_e2_karisik_sutunda_a_hucresi_sayilir(hucre, tmp_path):
    """A sealed cell in a column that
    also holds a cell flagged by the four-digit-year rule is counted, not refused uncounted."""
    with pytest.raises(TK.MuhurIhlali, match="1 sat\u0131r"):
        TK.zaman_kapisi(pd.Series(["21/01/01", hucre], dtype=object))
    assert TK.muhur_tara(pd.DataFrame({"time_utc": ["21/01/01", hucre]})) == 1
    with pytest.raises(K.MuhurIhlali, match="1 record"):
        K.iside_oku(_iside_hucreleri(tmp_path, ["21/01/01", hucre]))


# J: a sealed year inside a six-digit run, or the last four digits of an eight-digit run
_J_SEALED = ["1713 " + _MUHUR_Y + "06", "1713 06" + _MUHUR_Y, "1713 Jun 01" + _MUHUR_Y,
             "06" + _MUHUR_Y, "0106" + _MUHUR_Y, "0601" + _MUHUR_Y, "0713 0106" + _MUHUR_Y,
             "Jun 01" + _MUHUR_Y, "1713 " + _MUHUR_Y + "06 Jun", "2013 06" + _MUHUR_Y]


@pytest.mark.parametrize("hucre", _J_SEALED, ids=[f"J-{i}" for i in range(len(_J_SEALED))])
def test_j_alti_hane_muhur_sayilir(hucre, tmp_path):
    """a cell whose digit runs, time of day removed, are one
    four-digit run and then one six-digit run is refused by the four-digit-year rule, and a flagged cell is
    counted; the 2015 twin stays a format refusal."""
    with pytest.raises(TK.MuhurIhlali, match="1 sat\u0131r"):
        TK.zaman_kapisi(pd.Series([hucre], dtype=object))
    assert TK.muhur_tara(pd.DataFrame({"time_utc": [hucre]})) == 1
    with pytest.raises(K.MuhurIhlali, match="1 record"):
        K.iside_oku(_iside_hucreleri(tmp_path, [hucre]))
    ikiz = hucre.replace(_MUHUR_Y, "2015")
    with pytest.raises(TK.BicimHatasi):
        TK.zaman_kapisi(pd.Series([ikiz], dtype=object))


# The decimal year ``2015.416667`` is checked in ``test_j4_kontroller``, where it is counted.
@pytest.mark.parametrize("hucre", ["Jun 2015 071347", "2015-06-01 071347",
                                   "20150601T071347Z", "2015-06-01T07:13:47.213045"],
                         ids=["Jk-0", "Jk-2", "Jk-3", "Jk-4"])
def test_j_kontroller(hucre):
    """Controls: a 2015 cell with a six- or eight-digit run is left
    as it was (the decimal year ``2015.416667`` is checked in ``test_j4_kontroller``)."""
    try:
        r = TK.zaman_kapisi(pd.Series([hucre], dtype=object))
        assert int(r.iloc[0].year) == 2015
    except TK.BicimHatasi as e:
        assert hucre == "2015.416667" and "year-floor rule" not in str(e)


# A four-digit run, then a run of five or more
# digits right after a dot or a comma
_J4_SEALED = ["1713." + _MUHUR_Y + "06", "1713," + "06" + _MUHUR_Y, "1713." + "01" + _MUHUR_Y,
              "1713," + "0106" + _MUHUR_Y, "1713." + "0601" + _MUHUR_Y, "2013." + _MUHUR_Y + "06",
              "1713," + _MUHUR_Y + "06"]


@pytest.mark.parametrize("hucre", _J4_SEALED, ids=[f"J4-{i}" for i in range(len(_J4_SEALED))])
def test_j4_nokta_virgul_muhur_sayilir(hucre, tmp_path):
    """a four-digit run and then a five-or-more-digit
    run right after a dot or a comma is refused by the four-digit-year rule and its flagged six- or eight-digit
    run is counted; the 2015 twin stays a format refusal."""
    with pytest.raises(TK.MuhurIhlali, match="1 sat\u0131r"):
        TK.zaman_kapisi(pd.Series([hucre], dtype=object))
    assert TK.muhur_tara(pd.DataFrame({"time_utc": [hucre]})) == 1
    with pytest.raises(K.MuhurIhlali, match="1 record"):
        K.iside_oku(_iside_hucreleri(tmp_path, [hucre]))
    ikiz = hucre.replace(_MUHUR_Y, "2015")
    with pytest.raises(TK.BicimHatasi):
        TK.zaman_kapisi(pd.Series([ikiz], dtype=object))


@pytest.mark.parametrize("hucre", ["1713." + _MUHUR_Y + "6", "1713," + _MUHUR_Y + "152"],
                         ids=["J4r-0", "J4r-1"])
def test_j4_bes_yedi_hane_reddedilir(hucre):
    """a five- or seven-digit run holding the sealed
    year is refused (never kept) and is not counted as a sealed year."""
    with pytest.raises(TK.BicimHatasi):
        TK.zaman_kapisi(pd.Series([hucre], dtype=object))


@pytest.mark.parametrize("hucre,sinif", [("2015.416667", TK.MuhurIhlali), ("2015.123456", TK.MuhurIhlali),
                                         ("2015,071347", TK.BicimHatasi)], ids=["J4k-0", "J4k-1", "J4k-2"])
def test_j4_kontroller(hucre, sinif):
    """Controls: the accepted cost, counted or refused
    by the four-digit-year rule; the decimal year left out of ``test_j_kontroller`` is counted here."""
    with pytest.raises(sinif) as hata:
        TK.zaman_kapisi(pd.Series([hucre], dtype=object))
    assert sinif is TK.MuhurIhlali or "year-floor rule" in str(hata.value)


# A four-digit run and then a five-or-more-digit
# run right after a dot or a comma, anywhere in the cell, not only as the second of exactly two runs
_J4C_SEALED = ["1713." + _MUHUR_Y + "06 01", "1713," + "06" + _MUHUR_Y + " Jun 01",
               "1713." + "0106" + _MUHUR_Y + " 01 Jun", "01 1713." + _MUHUR_Y + "06",
               "01 Jun 1713," + "0601" + _MUHUR_Y, "Jun 01 1713." + "01" + _MUHUR_Y]


@pytest.mark.parametrize("hucre", _J4C_SEALED, ids=[f"J4c-{i}" for i in range(len(_J4C_SEALED))])
def test_j4c_ek_kosulu_nokta_virgul_muhur_sayilir(hucre, tmp_path):
    """a four-digit run and then a five-or-more-digit
    run right after a dot or a comma is refused by the four-digit-year rule and its flagged six- or eight-digit
    run is counted, wherever the pair stands in the cell; the 2015 twin stays a format refusal."""
    with pytest.raises(TK.MuhurIhlali, match="1 sat\u0131r"):
        TK.zaman_kapisi(pd.Series([hucre], dtype=object))
    assert TK.muhur_tara(pd.DataFrame({"time_utc": [hucre]})) == 1
    with pytest.raises(K.MuhurIhlali, match="1 record"):
        K.iside_oku(_iside_hucreleri(tmp_path, [hucre]))
    ikiz = hucre.replace(_MUHUR_Y, "2015")
    with pytest.raises(TK.BicimHatasi, match="year-floor rule"):
        TK.zaman_kapisi(pd.Series([ikiz], dtype=object))


# P1: the fraction on a time of day is stripped before the year search
@pytest.mark.parametrize("hucre", ["2015-06-01T07:13:47.5000", "2015-06-01T07:13:47.213045678",
                                    "2015-06-01 07:13,2130"], ids=["P1-0", "P1-1", "P1-2"])
def test_p1_saat_kesri_yil_sayilmaz(hucre):
    """Pin: a fraction on a time of day is stripped before the year
    search, so a nanosecond fraction is not counted as a sealed year."""
    assert TK.muhur_tara(pd.DataFrame({"time_utc": [hucre]})) == 0
    assert int(TK.zaman_kapisi(pd.Series([hucre], dtype=object)).iloc[0].year) == 2015


# P2: the 31-December boundary of the margin before a sealed run
@pytest.mark.parametrize("hucre", ["2020 30 Dec " + _MUHUR_Y, "2020 15 Dec " + _MUHUR_Y],
                         ids=["P2-0", "P2-1"])
def test_p2_g2_aralik_siniri(hucre, tmp_path):
    """Pin: the margin is exactly 31 December of the year before a
    sealed run; an earlier December date is returned."""
    with pytest.raises(TK.MuhurIhlali) as hata:
        TK.zaman_kapisi(pd.Series([hucre], dtype=object))
    assert "1 sat\u0131r" in str(hata.value) and hucre not in " ".join(_zincir(hata.value))
    assert TK.muhur_tara(pd.DataFrame({"time_utc": [hucre]})) == 1
    with pytest.raises(K.MuhurIhlali, match="1 record"):
        K.iside_oku(_iside_hucreleri(tmp_path, [hucre]))


# P3: the CPTI15 reader's missing-year branch, with a row that has as many fields as the header
def test_p3_h_bos_yil(tmp_path):
    """Pin: a 7-field blank-year row is collected with the
    unparseable rows, so ``cpti15_oku`` names "year missing" and raises the seal count first."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text(_CPTI_BASLIK + ",1,1,42.0,13.0,5.0,BADID\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.cpti15_oku(str(p))
    assert "row 0: year missing" in str(hata.value) and "BADID" not in " ".join(_zincir(hata.value))
    for satirlar in ([f"{_MUHUR_Y},6,1,42.0,13.0,5.0,SEALID", ",1,1,42.0,13.0,5.0,BADID"],
                     [",1,1,42.0,13.0,5.0,BADID", f"{_MUHUR_Y},6,1,42.0,13.0,5.0,SEALID"]):
        p.write_text(_CPTI_BASLIK + "\n".join(satirlar) + "\n", encoding="utf-8")
        with pytest.raises(K.MuhurIhlali, match="1 record"):
            K.cpti15_oku(str(p))


# P4: the CPTI15 reader names the first malformed row with its reason
def test_p4_h_ilk_satir_ve_sebep(tmp_path):
    """Pin: a multi-row CPTI15 refusal names the first unparseable row
    with its own reason and at most five positions, never a cell."""
    p = tmp_path / "CPTI15_v4.0.csv"
    p.write_text(_CPTI_BASLIK + "1990,6,1,42.0,13.0,5.0,G0\n" + "1990,xx,1,42.0,13.0,5.0,B1\n"
                 + "abc,6,1,42.0,13.0,5.0,B2\n" + ",6,1,42.0,13.0,5.0,B3\n"
                 + "1990,6,32,42.0,13.0,5.0,B4\n" + "1990,6,1,42.0,13.0,5.0,G5\n"
                 + "abc,6,1,42.0,13.0,5.0,B6\n" + "abc,6,1,42.0,13.0,5.0,B7\n", encoding="utf-8")
    with pytest.raises(K.BicimHatasi) as hata:
        K.cpti15_oku(str(p))
    assert "row 1: date not parseable (rows [1, 2, 3, 4, 6])" in str(hata.value)
    for i, s in ((2, "year not parseable"), (3, "year missing")):
        p.write_text(_CPTI_BASLIK + "1990,6,1,42.0,13.0,5.0,G0\n" * i
                     + ("abc" if i == 2 else "") + ",6,1,42.0,13.0,5.0,B\n", encoding="utf-8")
        with pytest.raises(K.BicimHatasi, match=f"row {i}: {s}"):
            K.cpti15_oku(str(p))


# P5: the sealed-year count reaches an np.str_ cell as it reaches a str cell
@pytest.mark.parametrize("hucre", ["06" + _MUHUR_Y, "0106" + _MUHUR_Y, "1713 " + _MUHUR_Y + "06"],
                         ids=["P5-0", "P5-1", "P5-2"])
def test_p5_j3_np_str(hucre):
    """Pin: an ``np.str_`` flagged cell is counted as a
    ``str`` one, in ``zaman_kapisi`` and ``muhur_tara``."""
    with pytest.raises(TK.MuhurIhlali, match="1 sat\u0131r"):
        TK.zaman_kapisi(pd.Series([np.str_(hucre)], dtype=object))
    assert TK.muhur_tara(pd.DataFrame({"time_utc": pd.Series([np.str_(hucre)], dtype=object)})) == 1


# P6: only flagged cells are counted, in both readers
@pytest.mark.parametrize("hucre", ["2015-06-01 213045", "1990-06-01 235959"], ids=["P6-0", "P6-1"])
def test_p6_j3_yalniz_isaretli(hucre, tmp_path):
    """Pin: in a flagged column a 2015 cell whose colon-less
    ``HHMMSS`` reads 20:21 or later is refused by the four-digit-year rule, never counted, in both readers."""
    kolon = ["21/01/01", hucre]
    with pytest.raises(TK.BicimHatasi, match="year-floor rule"):
        TK.zaman_kapisi(pd.Series(kolon, dtype=object))
    with pytest.raises(K.BicimHatasi, match="year-floor rule"):
        K.iside_oku(_iside_hucreleri(tmp_path, kolon))
