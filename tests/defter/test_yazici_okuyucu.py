"""Writer/reader round trip: columns, units, UTC, computed Delta-CFS."""
import numpy as np
import pandas as pd
import pytest

from knotenlinie.defter import coulomb, oku, yaz


def _satirlar():
    return pd.DataFrame({
        "fault_id": ["F1", "F1", "F2"],
        "time_utc": pd.to_datetime(
            ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z", "2024-01-01T02:00:00Z"]
        ),
        "kind": ["series", "series", "series"],
        "tau_Pa": [-10.0, 5.0, 0.0],
        "sigma_n_Pa": [20.0, -3.0, 1.0],
    })


def test_yaz_oku(tmp_path, kabul):
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=_satirlar(), kabul=kabul, uretici="test@v0")
    assert hedef.exists()
    assert (tmp_path / "k9_v1.provenance.json").exists()

    d = oku(hedef)
    assert d.sema_surum == 2 and d.satirlar["uretici"].iloc[0] == "test@v0"   # schema v2 default
    assert list(d.satirlar.columns) == ["fault_id", "time_utc", "kind", "tau_Pa", "sigma_n_Pa", "uretici"]
    assert str(d.satirlar["time_utc"].dt.tz) == "UTC"
    assert set(d.satirlar["kind"]) == {"series"}
    assert d.meta["birim"] == "Pa"
    assert d.satirlar["tau_Pa"].dtype == np.float64
    # Delta-CFS is computed by the reader, never read from a stored column
    assert "cfs" not in d.satirlar.columns
    okunan = coulomb(
        d.satirlar["tau_Pa"].to_numpy(), d.satirlar["sigma_n_Pa"].to_numpy(), mu_prime=0.4
    )
    assert d.cfs[0.4] == pytest.approx(okunan)
    assert d.cfs[0.4][0] == pytest.approx(-2.0)


def test_gezegen_olcegi_kucuk_kanal_aynen(tmp_path, kabul):
    # ~1e-2 Pa is a planet-sized Delta-CFS; it must survive byte-for-byte
    df = _satirlar()
    df["tau_Pa"] = [1.248e-2, 9.8765e-4, 3.0e-3]
    df["sigma_n_Pa"] = [-1.0e-2, 2.5e-4, 0.0]
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")
    d = oku(hedef)
    assert list(d.satirlar["tau_Pa"]) == list(df["tau_Pa"])
    assert list(d.satirlar["sigma_n_Pa"]) == list(df["sigma_n_Pa"])
    assert d.cfs[0.4][0] == pytest.approx(1.248e-2 - 0.4 * 1.0e-2, abs=0.0)


def test_tensor_satirlari_korunur(tmp_path, kabul):
    df = _satirlar()
    df["s_xx_Pa"] = [1.0, np.nan, 2.0]
    df["s_yy_Pa"] = [2.0, np.nan, 3.0]
    df["s_zz_Pa"] = [3.0, np.nan, 4.0]
    df["s_xy_Pa"] = [0.1, np.nan, 0.2]
    df["s_xz_Pa"] = [0.2, np.nan, 0.3]
    df["s_yz_Pa"] = [0.3, np.nan, 0.4]
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")
    d = oku(hedef)
    from knotenlinie.defter.okuyucu import tensorden_coz
    tau, sigma_n = tensorden_coz(d.satirlar, np.array([0.0, 1.0, 0.0]), np.array([1.0, 0.0, 0.0]))
    assert np.isnan(tau[1])
    assert tau[0] == pytest.approx(0.1)
    assert sigma_n[0] == pytest.approx(2.0)


def test_birim_kPa_reddedilir(tmp_path, kabul):
    import pyarrow.parquet as pq
    from knotenlinie.defter import sema
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=_satirlar(), kabul=kabul, uretici="test@v0")
    tablo = pq.read_table(hedef)
    meta = dict(tablo.schema.metadata)
    meta[b"birim"] = b"kPa"                      # silent unit drift must not pass
    pq.write_table(tablo.replace_schema_metadata(meta), hedef)
    with pytest.raises(sema.SemaHatasi):
        oku(hedef)


def test_p_varsa_B_zorunlu(tmp_path, kabul):
    df = pd.DataFrame({
        "fault_id": ["F1"],
        "time_utc": pd.to_datetime(["2024-01-01T00:00:00Z"]),
        "kind": ["series"],
        "tau_Pa": [-10.0],
        "sigma_n_Pa": [20.0],
        "p_Pa": [5.0],
    })
    hedef = tmp_path / "k6_v1.parquet"
    yaz(hedef, kanal="K6", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")
    with pytest.raises(ValueError):
        oku(hedef)                                 # p is present, B is not
    d = oku(hedef, B=0.5)
    assert d.cfs[0.4][0] == pytest.approx(2.0)     # -10 + 0.4*20 + 0.8*5


def test_p_yalniz_k6_ve_k13(tmp_path, kabul):
    """K6 and K13 may carry open pore pressure; K9 may not."""
    df = pd.DataFrame({
        "fault_id": ["F1"],
        "time_utc": pd.to_datetime(["2024-01-01T00:00:00Z"]),
        "kind": ["series"],
        "tau_Pa": [-10.0],
        "sigma_n_Pa": [20.0],
        "p_Pa": [5.0],
    })
    yaz(tmp_path / "k13_v1.parquet", kanal="K13", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")
    assert oku(tmp_path / "k13_v1.parquet", B=0.5).cfs[0.4][0] == pytest.approx(2.0)
    with pytest.raises(ValueError):
        yaz(tmp_path / "k9_v1.parquet", kanal="K9", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")


def test_1677_oncesi_an_yazilir_okunur(tmp_path, kabul):
    """A step row dated 1349 (CPTI15 starts there) is written and read back
    at microsecond resolution under pandas 2, whose nanosecond range starts in 1677."""
    import datetime as dt
    zaman = [dt.datetime(1349, 9, 9, 12, 0, tzinfo=dt.timezone.utc),
             dt.datetime(2015, 12, 31, 23, 59, 59, 999999, tzinfo=dt.timezone.utc)]
    satirlar = pd.DataFrame({"fault_id": ["F1", "F1"], "time_utc": zaman, "kind": ["step", "step"],
                             "tau_Pa": [150.0, -20.0], "sigma_n_Pa": [10.0, 0.0]})
    hedef = tmp_path / "K9_eski.parquet"
    yaz(hedef, kanal="K9", kanal_surum="eski", satirlar=satirlar, kabul=kabul, uretici="test@v0",
        referans_donem={"from": "1349-09-09", "to": "2015-12-31"})
    d = oku(hedef)
    geri = pd.to_datetime(d.satirlar["time_utc"], utc=True).tolist()
    assert [g.year for g in geri] == [1349, 2015]
    assert geri[1].microsecond == 999999
    assert d.satirlar["tau_Pa"].tolist() == [150.0, -20.0]


def test_utc_yap_hep_mikrosaniye():
    """utc_yap returns microseconds whatever the input's range: an
    in-range and a pre-1677 result share one unit, so they concatenate and subtract."""
    import datetime as dt
    from knotenlinie.defter.zaman import utc_yap
    yeni = utc_yap(["2000-01-01T00:00:00Z"])
    eski = utc_yap(["1349-01-01T00:00:00Z"])
    hazir = utc_yap(pd.Series(pd.to_datetime(["2015-12-31T23:59:59.999999Z"])))
    for s in (yeni, eski, hazir):
        assert str(s.dtype) == "datetime64[us, UTC]"
    birlesik = pd.concat([yeni, eski, hazir], ignore_index=True)
    assert str(birlesik.dtype) == "datetime64[us, UTC]"
    assert (yeni.iloc[0] - eski.iloc[0]) == pd.Timestamp("2000-01-01", tz="UTC") - pd.Timestamp(
        dt.datetime(1349, 1, 1, tzinfo=dt.timezone.utc))
    assert hazir.iloc[0].microsecond == 999999


def test_utc_yap_eski_yolda_nat_kendi_mesaji():
    """A NaT on the pre-1677 path gets its own message, not the tz-naive one."""
    from knotenlinie.defter.zaman import utc_yap
    with pytest.raises(ValueError) as h:
        utc_yap(pd.Series(["1349-09-09T12:00:00Z", None], dtype=object))
    assert "NaT" in str(h.value) and "dilimsiz" not in str(h.value)
    with pytest.raises(ValueError) as h2:
        utc_yap(pd.Series(["1349-09-09T12:00:00"], dtype=object))
    assert "dilimsiz" in str(h2.value)


@pytest.mark.parametrize("girdi", [
    pd.Series(["2015-01-01T00:00:00Z", None], dtype=object),
    pd.Series(["2015-01-01T00:00:00Z", float("nan")], dtype=object),
    pd.Series(["2015-01-01T00:00:00Z", "NaT"], dtype=object),
    pd.Series([pd.Timestamp("2015-01-01", tz="UTC"), pd.NaT]),
    pd.Series(pd.to_datetime(["2015-01-01", None], utc=True)),
    pd.Series(["1349-09-09T12:00:00Z", None], dtype=object),
    pd.Series([None, None], dtype=object),
], ids=["none", "nan", "NaT-text", "timestamp-NaT", "datetime-utc-NaT", "pre1677-none", "all-none"])
def test_utc_yap_nat_her_yolda_kendi_mesaji(girdi):
    """A NaT is refused with its own message on every path and under every pandas version:
    in-range text, a ready tz-aware column, a pre-1677 text.  Pandas 3 parses all of
    these natively, pandas 2 holds the in-range ones in nanoseconds; neither may pass a NaT."""
    from knotenlinie.defter.zaman import utc_yap
    with pytest.raises(ValueError) as h:
        utc_yap(girdi)
    assert "NaT" in str(h.value) and "dilimsiz" not in str(h.value)


@pytest.mark.parametrize("girdi", [
    pd.Series(["2015-01-01T00:00:00", "2016-01-01T00:00:00"], dtype=object),
    pd.Series(pd.to_datetime(["2015-01-01", "2016-01-01"])),
], ids=["in-range-text", "naive-datetime"])
def test_utc_yap_dilimsiz_her_yolda_kendi_mesaji(girdi):
    """A tz-naive input keeps its own message on the in-range path (not only the pre-1677 one)."""
    from knotenlinie.defter.zaman import utc_yap
    with pytest.raises(ValueError) as h:
        utc_yap(girdi)
    assert "dilimsiz" in str(h.value) and "NaT" not in str(h.value)
