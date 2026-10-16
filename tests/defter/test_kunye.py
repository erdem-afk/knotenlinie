"""Provenance tests: completeness, acceptance refusal, seal, hash."""
import json
import os

import pandas as pd
import pytest

from knotenlinie.defter import oku, yaz
from knotenlinie.defter.kunye import KabulHatasi, KunyeHatasi, kunye_dogrula


def _satirlar():
    return pd.DataFrame({
        "fault_id": ["F1"],
        "time_utc": pd.to_datetime(["2024-01-01T00:00:00Z"]),
        "kind": ["series"],
        "tau_Pa": [-10.0],
        "sigma_n_Pa": [20.0],
    })


def _yaz(tmp_path, kabul, **ek):
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=_satirlar(), kabul=kabul, **{"uretici": "test@v0", **ek})
    return hedef


def test_kunye_tam_ve_dogrulanir(tmp_path, kabul):
    hedef = _yaz(tmp_path, kabul)
    kunye_yolu = tmp_path / "k9_v1.provenance.json"
    rec = json.load(open(kunye_yolu, encoding="utf-8"))
    zorunlu = {
        "record_type", "record_version", "kanal", "kanal_surum", "sema_surum", "defter_dosya",
        "defter_sha256", "satir", "tur", "olusturma_utc", "kod", "isaret", "referans_donem",
        "birim", "girdiler", "kabul", "muhur", "uretici",
    }
    assert zorunlu <= set(rec)
    assert rec["defter_dosya"] == "k9_v1.parquet"
    assert kunye_dogrula(rec) is rec
    assert oku(hedef, hash_dogrula=True).kunye == rec


def test_kunye_yoksa_okuma_reddedilir(tmp_path, kabul):
    hedef = _yaz(tmp_path, kabul)
    os.remove(tmp_path / "k9_v1.provenance.json")
    with pytest.raises(KunyeHatasi):
        oku(hedef)


def test_defter_sha256_uyusmazligi(tmp_path, kabul):
    hedef = _yaz(tmp_path, kabul)
    kunye_yolu = tmp_path / "k9_v1.provenance.json"
    rec = json.load(open(kunye_yolu, encoding="utf-8"))
    rec["defter_sha256"] = "0" * 64
    json.dump(rec, open(kunye_yolu, "w", encoding="utf-8"))
    assert oku(hedef, hash_dogrula=False) is not None      # record is only format-valid here
    with pytest.raises(KunyeHatasi):
        oku(hedef, hash_dogrula=True)


def test_S11_gecti_false_dosya_birakmaz(tmp_path, kabul):
    kotu = dict(kabul, gecti=False)
    with pytest.raises(KabulHatasi):
        _yaz(tmp_path, kotu)
    assert list(tmp_path.iterdir()) == []


def test_S11_kabul_yoksa_dosya_birakmaz(tmp_path):
    with pytest.raises(KabulHatasi):
        _yaz(tmp_path, None)
    assert list(tmp_path.iterdir()) == []


def test_S11_kanit_bossa_reddedilir(tmp_path, kabul):
    with pytest.raises(KabulHatasi):
        _yaz(tmp_path, dict(kabul, kanit=""))
    assert list(tmp_path.iterdir()) == []


def test_S11_tur_kapali(tmp_path, kabul):
    with pytest.raises(KabulHatasi):
        _yaz(tmp_path, dict(kabul, tur="tahmin"))
    assert list(tmp_path.iterdir()) == []


def test_deprem_girdisi_muhur_ister(tmp_path, kabul):
    with pytest.raises(KabulHatasi):
        _yaz(tmp_path, kabul, deprem_girdisi=True)
    assert list(tmp_path.iterdir()) == []
    with pytest.raises(KabulHatasi):
        _yaz(tmp_path, kabul, deprem_girdisi=True, muhur={"durum": "kirli"})


def test_deprem_girdisi_temiz_muhurle_yazilir(tmp_path, kabul):
    muhur = {"durum": "clean", "komut": "python3 scripts/muhur.py data",
             "kok": "data", "tarih": "2026-09-29T00:00:00Z"}
    hedef = _yaz(tmp_path, kabul, deprem_girdisi=True, muhur=muhur)
    rec = oku(hedef).kunye
    assert rec["muhur"] == {"gerekli": True, "durum": "clean", "komut": muhur["komut"],
                            "kok": muhur["kok"], "tarih": muhur["tarih"]}


def test_girdi_ozetleri_kunyede(tmp_path, kabul):
    girdi = tmp_path / "girdi.txt"
    girdi.write_text("veri", encoding="utf-8")
    hedef = _yaz(tmp_path, kabul, girdiler=[(str(girdi), "fay tablosu")])
    rec = oku(hedef).kunye
    assert rec["girdiler"][0]["rol"] == "fay tablosu"
    assert len(rec["girdiler"][0]["sha256"]) == 64


def test_karisik_tur_reddedilir(tmp_path, kabul):
    """A ledger whose rows carry two kinds is refused by name; the kinds come from the Arrow
    column, so a null and a second kind are both seen."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    satirlar = pd.concat([_satirlar(), _satirlar().assign(fault_id="F2")], ignore_index=True)
    hedef = tmp_path / "k9_v1.parquet"
    yaz(hedef, kanal="K9", kanal_surum="v1", satirlar=satirlar, kabul=kabul, uretici="test@v0")
    tablo = pq.read_table(hedef)
    i = tablo.column_names.index("kind")
    for yeni in (["series", "step"], ["series", None]):
        bozuk = tablo.set_column(i, "kind", pa.array(yeni, type=tablo.schema.field("kind").type))
        pq.write_table(bozuk.replace_schema_metadata(tablo.schema.metadata), hedef)
        with pytest.raises(ValueError, match="karışık tür"):
            oku(hedef)
