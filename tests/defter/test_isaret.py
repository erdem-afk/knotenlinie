"""Sign-convention round trip: four flag combinations, converted once."""
import numpy as np
import pandas as pd
import pytest

from knotenlinie.defter import oku, yaz
from knotenlinie.defter.isaret import isaret_dogrula, isaret_uygula


def test_dort_kombinasyon_S3_e_cevrilir():
    for normal in ("tension_positive", "compression_positive"):
        for kayma in ("rake_positive", "rake_negative"):
            # channel-convention inputs chosen so the stored values are tau=-10, sigma_n=+20
            sn_gir = 20.0 if normal == "tension_positive" else -20.0
            tau_gir = -10.0 if kayma == "rake_positive" else 10.0
            tau3, sn3 = isaret_uygula(
                np.array([tau_gir]), np.array([sn_gir]), {"normal": normal, "kayma": kayma}
            )
            assert float(tau3[0]) == pytest.approx(-10.0)
            assert float(sn3[0]) == pytest.approx(20.0)


def test_beyan_eksikse_S3_varsayilan():
    assert isaret_dogrula({}) == {"normal": "tension_positive", "kayma": "rake_positive"}
    assert isaret_dogrula(None) == {"normal": "tension_positive", "kayma": "rake_positive"}


def test_bilinmeyen_eksen_ve_deger_hata():
    with pytest.raises(ValueError):
        isaret_dogrula({"ters": "tension_positive"})
    with pytest.raises(ValueError):
        isaret_dogrula({"normal": "pulling_positive"})
    with pytest.raises(ValueError):
        isaret_dogrula({"kayma": "rake_sideways"})


def test_yazici_okuyucu_isaret(tmp_path, kabul):
    df = pd.DataFrame({
        "fault_id": ["F1"],
        "time_utc": pd.to_datetime(["2024-01-01T00:00:00Z"]),
        "kind": ["series"],
        "tau_Pa": [10.0],        # rake_negative channel: writer flips to -10
        "sigma_n_Pa": [-20.0],   # compression_positive channel: writer flips to +20
    })
    hedef = tmp_path / "k9_v1.parquet"
    yaz(
        hedef, kanal="K9", kanal_surum="v1", satirlar=df,
        isaret={"normal": "compression_positive", "kayma": "rake_negative"}, kabul=kabul,
        uretici="test@v0",
    )
    d = oku(hedef)
    assert float(d.satirlar["tau_Pa"][0]) == pytest.approx(-10.0)
    assert float(d.satirlar["sigma_n_Pa"][0]) == pytest.approx(20.0)
    assert d.cfs[0.4][0] == pytest.approx(-2.0)
    assert d.kunye["isaret"] == {"normal": "compression_positive", "kayma": "rake_negative"}
    # the reader never converts again: stored values are already in the stored convention
    assert d.meta["isaret"] == {"normal": "compression_positive", "kayma": "rake_negative"}
