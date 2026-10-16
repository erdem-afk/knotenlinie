"""Tests for scripts/kesik_2015.py on synthetic files (no real catalogue rows, no network)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import kesik_2015 as K  # noqa: E402

NDK = (
    "PDE  {date} 01:20:05.4  13.78  -88.78 193.1 5.0 0.0 SYNTHETIC EVENT         \n"
    "C000000000000A B:  0    0  40 S:  0    0   0 M:  0    0   0 CMT: 1 TRIHD:  0.6\n"
    "CENTROID:     -0.3 0.9  13.76 0.06  -89.08 0.09 162.8 12.5 FREE S-20050322125201\n"
    "23  0.838 0.201 -0.005 0.231 -0.833 0.270  1.050 0.121 -0.369 0.161  0.044 0.240\n"
    "V10   1.581 56  12  -0.537 23 140  -1.044 24 241   1.312   9 29  142 133 72   66\n"
)


def test_gcmt_kes_drops_2016_2020_and_keeps_le2015(tmp_path):
    k = tmp_path / "in.ndk"
    k.write_text(NDK.format(date="2014/03/01") + NDK.format(date="2015/12/31") + NDK.format(date="2018/06/01"))
    h = tmp_path / "out.ndk"
    r = K.gcmt_kes(k, h, yeniden=False)
    assert r["kayit"] == 2 and r["atilan_2016_2020"] == 1
    assert "2018/06/01" not in h.read_text() and h.read_text().count("PDE") == 2


def test_gcmt_kes_stops_at_the_seal(tmp_path):
    k = tmp_path / "in.ndk"
    k.write_text(NDK.format(date="2014/03/01") + NDK.format(date="2021/01/01"))
    h = tmp_path / "out.ndk"
    with pytest.raises(K.MuhurIhlali):
        K.gcmt_kes(k, h, yeniden=False)
    assert not h.exists()


def test_kopyala_keeps_bytes_and_refuses_missing(tmp_path):
    k = tmp_path / "a.csv"; k.write_text("Year\n2015\n")
    h = tmp_path / "kesik" / "a.csv"
    assert K._kopyala(k, h, yeniden=False) == "kopyalandı"
    assert h.read_bytes() == k.read_bytes()
    assert K._kopyala(k, h, yeniden=False) == "var"
    with pytest.raises(FileNotFoundError):
        K._kopyala(tmp_path / "yok.csv", tmp_path / "b.csv", yeniden=False)
