"""Schema-version dispatch tests: v1 read-back, registered v2, unknown version."""
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd
import pytest

from knotenlinie.defter import oku, sema, yaz
from knotenlinie.defter.kunye import girdi_ozeti, kunye_olustur, kunye_yaz
from knotenlinie.defter.zaman import utc_yap


def _satirlar(satir=1):
    df = pd.DataFrame({
        "fault_id": ["F1"] * satir,
        "time_utc": pd.to_datetime(["2024-01-01T00:00:00Z"] * satir),
        "kind": ["series"] * satir,
        "tau_Pa": [-10.0] * satir,
        "sigma_n_Pa": [20.0] * satir,
    })
    return df


def _v1(tmp_path, kabul, satir=1):
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=_satirlar(satir), kabul=kabul, sema_surum=1)
    return hedef


def _v2_yap(v1, v2, uretici="K9-v0", surum=2):
    """Add the producer column and bump the version number, without rewriting v1."""
    tablo = pq.read_table(v1)
    tablo = tablo.append_column("uretici", pa.array([uretici] * tablo.num_rows, type=pa.string()))
    meta = dict(tablo.schema.metadata)
    meta[b"defter_sema_surum"] = str(surum).encode("ascii")
    meta[b"uretici"] = uretici.encode("utf-8")
    meta[b"kunye"] = b"k9_v2.provenance.json"
    pq.write_table(tablo.replace_schema_metadata(meta), v2)
    return v2


def _v2_kunye(v2, kabul, satir, uretici="K9-v0"):
    rec = kunye_olustur(
        kanal="K9", kanal_surum="v1", sema_surum=2, defter_dosya="k9_v2.parquet",
        defter_sha256=girdi_ozeti(v2), satir=satir, tur="series", isaret=None,
        girdiler=(), kabul=kabul, uretici=uretici, olusturma_utc="2026-09-29T00:00:00Z",
    )
    kunye_yaz(str(v2)[: -len(".parquet")] + ".provenance.json", rec)


def test_v1_surum_geri_okunur(tmp_path, kabul):
    hedef = _v1(tmp_path, kabul)
    ham = pq.ParquetFile(hedef).schema_arrow.metadata
    assert int(ham[b"defter_sema_surum"]) == 1
    assert oku(hedef).sema_surum == 1


def test_kayitsiz_surum_numarasiyla_hata(tmp_path, kabul):
    v1 = _v1(tmp_path, kabul)
    v2 = tmp_path / "k9_v2.parquet"
    _v2_yap(v1, v2, surum=3)
    _v2_kunye(v2, kabul, 1)
    assert 3 not in sema.SEMA_SURUMLARI          # only v1 and v2 are registered
    with pytest.raises(sema.SemaSurumHatasi) as yakalanan:
        oku(v2)
    assert "3" in str(yakalanan.value)


def test_kayitli_v2_uretici_ile_okunur(tmp_path, kabul, monkeypatch):
    v1 = _v1(tmp_path, kabul)
    monkeypatch.setitem(
        sema.SEMA_SURUMLARI, 2,
        {"zorunlu": sema.ZORUNLU_V1 + ("uretici",), "secmeli": sema.SECMELI_V1},
    )
    v2 = tmp_path / "k9_v2.parquet"
    _v2_yap(v1, v2, uretici="K9-v0")
    _v2_kunye(v2, kabul, 1, uretici="K9-v0")

    d = oku(v2)
    assert d.sema_surum == 2
    assert "uretici" in d.satirlar.columns
    assert d.satirlar["uretici"].iloc[0] == "K9-v0"
    # v1 is still readable and untouched
    assert oku(v1).sema_surum == 1


def test_tz_naive_zaman_reddedilir(tmp_path, kabul):
    with pytest.raises(ValueError):
        utc_yap(pd.Series(["2024-01-01T00:00:00"]))
    df = _satirlar()
    df["time_utc"] = pd.to_datetime(["2024-01-01T00:00:00"])  # tz-naive
    with pytest.raises(ValueError):
        yaz(tmp_path / "k9_v1.parquet", kanal="K9", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")
    assert list(tmp_path.iterdir()) == []


def test_naive_zamanli_dosya_okunmaz(tmp_path, kabul):
    v1 = _v1(tmp_path, kabul)
    tablo = pq.read_table(v1)
    idx = tablo.schema.get_field_index("time_utc")
    tablo = tablo.set_column(idx, "time_utc", tablo.column(idx).cast(pa.timestamp("us")))
    meta = dict(tablo.schema.metadata)
    meta.pop(b"pandas", None)          # keep the reader from restoring UTC from pandas metadata
    tablo = tablo.replace_schema_metadata(meta)
    naive = tmp_path / "k9_v1.parquet"
    pq.write_table(tablo, naive)
    with pytest.raises(ValueError):
        oku(naive)


def test_karisik_tur_yazici_reddeder(tmp_path, kabul):
    df = _satirlar(2)
    df["kind"] = ["series", "rate"]
    with pytest.raises(ValueError):
        yaz(tmp_path / "k9_v1.parquet", kanal="K9", kanal_surum="v1", satirlar=df, kabul=kabul, uretici="test@v0")
    assert list(tmp_path.iterdir()) == []


def test_karisik_tur_okuyucu_reddeder(tmp_path, kabul):
    v1 = _v1(tmp_path, kabul, satir=2)
    tablo = pq.read_table(v1)
    idx = tablo.schema.get_field_index("kind")
    tablo = tablo.set_column(idx, "kind", pa.array(["series", "rate"], type=pa.string()))
    pq.write_table(tablo, v1)
    with pytest.raises(ValueError):
        oku(v1)
