"""Paket testleri: temiz oda taraması, birim sonekleri, sabitler, sürüm."""
import importlib
import sys

from knotenlinie.elastik import __version__


def test_temiz_oda_sys_modules():
    """After importing knotenlinie.elastik nothing named LoadDef/cutde/spotl/nloadf is loaded."""
    importlib.import_module("knotenlinie.elastik")
    yasak = ("loaddef", "cutde", "spotl", "nloadf")
    yuklu = {str(ad).split(".")[0].lower() for ad in sys.modules if isinstance(ad, str) and ad}
    bulunan = sorted(set(yasak) & yuklu)
    assert bulunan == [], f"temiz oda ihlali: {bulunan} yüklü"


def test_surum():
    assert isinstance(__version__, str) and __version__


def _kaynak_metni():
    from knotenlinie.yollar import KOK

    kok = KOK / "knotenlinie" / "elastik"
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(kok.glob("*.py")))


def test_temiz_oda_atfi_modul_docstringlerinde():
    metin = _kaynak_metni()
    assert "10.1785/bssa0820021018" in metin
    assert "clean-room" in metin
    assert "cutde (MIT)" in metin


def test_imza_birimleri():
    import inspect

    from knotenlinie.elastik import cerceve, okada

    beklenen = {
        cerceve.ned_metre: {"lat_deg", "lon_deg", "lat0_deg", "lon0_deg"},
        cerceve.yerel_cerceve: {"dogrultu_deg", "egim_deg"},
        okada.okada_ned: {"alici_lat", "alici_lon", "alici_derinlik_m"},
    }
    for fonksiyon, adlar in beklenen.items():
        parametreler = set(inspect.signature(fonksiyon).parameters)
        assert adlar <= parametreler, f"{fonksiyon.__name__}: {sorted(adlar - parametreler)} eksik"


def test_hicbir_imzada_deprem_girdisi_yok():
    """No kernel signature can carry a magnitude, a date or a catalog path."""
    import inspect

    from knotenlinie.elastik import cerceve, okada

    yasak = ("magnitude", "buyukluk", "tarih", "date", "katalog", "catalog")
    for modul in (cerceve, okada):
        for ad, nesne in vars(modul).items():
            if not inspect.isfunction(nesne) or nesne.__module__ != modul.__name__:
                continue
            parametreler = [p.lower() for p in inspect.signature(nesne).parameters]
            for p in parametreler:
                assert not any(y in p for y in yasak), f"{modul.__name__}.{ad}: {p}"
