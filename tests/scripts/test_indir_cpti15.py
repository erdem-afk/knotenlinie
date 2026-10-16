#!/usr/bin/env python3
"""Tests for the CPTI15 <=2015 split writer of ``scripts/indir.py``.

Synthetic xlsx/csv only, no network.  ``fetch_cpti`` is exercised with ``get`` stubbed and the
pure write step ``_cpti15_bol_yaz`` directly; both must write only the <=2015 split and never the
full ``CPTI15_v4.0.csv``.  The binding sidecar goes to ``<data>/yan-kayit/cpti15/``,
never beside the CSV under ``deprem/``, and main's fail-closed ``scripts/muhur.py`` must scan the
resulting ``<data>`` clean.

run: python -m pytest tests/scripts/test_indir_cpti15.py -q
"""
import hashlib
import io
import json
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest

TOOLS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(TOOLS))
import indir  # noqa: E402  (no network at import)

CPTI = "CPTI15_v4.0_le2015.csv"
TAM = "CPTI15_v4.0.csv"
HEADER = ["Year", "Mo", "Da", "Ho", "Mi", "Se", "Lat", "Lon", "Mw", "CPTI15_ID"]
SATIRLAR = [
    (2015, 1, 1, 0, 0, 0, 42.0, 13.0, 6.0, "k2015"),
    (2016, 1, 1, 0, 0, 0, 42.0, 13.0, 6.0, "a2016"),
    (2020, 1, 1, 0, 0, 0, 42.0, 13.0, 6.0, "a2020"),
    (2021, 1, 1, 0, 0, 0, 42.0, 13.0, 6.0, "d2021"),
]


def _xlsx(satirlar, header=HEADER):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "catalogue"
    ws.append(list(header))
    for r in satirlar:
        ws.append(list(r))
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


class _Yanit:
    """The one attribute ``fetch_cpti`` uses from ``get(...)``: ``read()``."""

    def __init__(self, govde):
        self.govde = govde

    def read(self):
        return self.govde


def _yan_yolu(data):
    """The sidecar's home, ``<data>/yan-kayit/cpti15/<csv basename>.json``."""
    return data / "yan-kayit" / "cpti15" / (CPTI + ".json")


# ---------------------------------------------------------------- the pure write step
def test_cpti15_bol_yaz_yillari_ayirir(tmp_path):
    """2015 kept; 2016-2020 and 2021+ dropped and counted separately."""
    dest = tmp_path / "deprem" / "cpti15" / CPTI
    yan = _yan_yolu(tmp_path)
    info, kept, atilan, dropped = indir._cpti15_bol_yaz(
        dest, yan, HEADER, iter(SATIRLAR), 0,
        kaynak="http://x/CPTI15_v4.0.xlsx", kaynak_sha256="ab" * 32)
    assert (kept, atilan, dropped) == (1, 2, 1)
    metin = dest.read_text(encoding="utf-8")
    assert "k2015" in metin
    assert "a2016" not in metin and "a2020" not in metin and "d2021" not in metin
    assert info["sha256"] == hashlib.sha256(dest.read_bytes()).hexdigest()
    kayit = json.loads(yan.read_text(encoding="utf-8"))
    assert kayit["tur"] == "knotenlinie-cpti15-bolme"
    assert kayit["kesim_yili"] == 2015
    assert kayit["satir_le2015"] == 1 and kayit["atilan_2016_2020"] == 2
    assert kayit["kaynak"] == "http://x/CPTI15_v4.0.xlsx"
    assert kayit["kaynak_sha256"] == "ab" * 32
    assert kayit["cikti_sha256"] == info["sha256"]
    assert not (tmp_path / "deprem" / "cpti15" / TAM).exists()
    # no .json anywhere under deprem/
    assert not list((tmp_path / "deprem").rglob("*.json"))


def test_cpti15_bol_yaz_bicim_indent1_sirali(tmp_path):
    """The sidecar is exactly ``json.dumps(..., indent=1, sort_keys=True)`` plus a newline."""
    dest = tmp_path / "deprem" / "cpti15" / CPTI
    yan = _yan_yolu(tmp_path)
    indir._cpti15_bol_yaz(dest, yan, HEADER, iter(SATIRLAR), 0,
                          kaynak="http://x", kaynak_sha256="ab" * 32)
    ham = yan.read_text(encoding="utf-8")
    assert ham == json.dumps(json.loads(ham), indent=1, sort_keys=True) + "\n"


def test_fetch_cpti_ayri_yazar_tam_dosya_birakmaz(tmp_path, monkeypatch):
    monkeypatch.setattr(indir, "get", lambda url: _Yanit(_xlsx(SATIRLAR)))
    s = {"urls": ["http://x/CPTI15_v4.0.xlsx"], "dest": "cpti15/" + CPTI, "side": "deprem"}
    indir.fetch_cpti(tmp_path, "cpti15", s)

    cikti = tmp_path / "deprem" / "cpti15" / CPTI
    yan = _yan_yolu(tmp_path)
    assert cikti.exists() and yan.exists()
    assert not (tmp_path / "deprem" / "cpti15" / TAM).exists()
    assert not list((tmp_path / "deprem").rglob("*.json"))
    assert "k2015" in cikti.read_text(encoding="utf-8")

    satirlar = [json.loads(x) for x in
                (tmp_path / "MANIFEST.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    kayit = satirlar[-1]
    assert kayit["path"] == "deprem/cpti15/" + CPTI
    assert kayit["rows_kept"] == 1
    assert kayit["rows_2016_2020"] == 2
    assert kayit["rows_dropped"] == 1
    assert kayit["raw_sha256"] == hashlib.sha256(_xlsx(SATIRLAR)).hexdigest()

    # a second call is a no-op while both halves exist (no duplicate MANIFEST row)
    indir.fetch_cpti(tmp_path, "cpti15", s)
    assert len([x for x in (tmp_path / "MANIFEST.jsonl").read_text(encoding="utf-8").splitlines()
                if x.strip()]) == len(satirlar)


def test_fetch_cpti_yan_eksikse_yeniden_yazar(tmp_path, monkeypatch):
    """A CSV without its binding sidecar is not a finished product; fetch rewrites both."""
    monkeypatch.setattr(indir, "get", lambda url: _Yanit(_xlsx(SATIRLAR)))
    s = {"urls": ["http://x/CPTI15_v4.0.xlsx"], "dest": "cpti15/" + CPTI, "side": "deprem"}
    indir.fetch_cpti(tmp_path, "cpti15", s)
    _yan_yolu(tmp_path).unlink()
    indir.fetch_cpti(tmp_path, "cpti15", s)
    assert _yan_yolu(tmp_path).exists()


def test_fetch_cpti_muhur_temiz(tmp_path, monkeypatch):
    """Main's fail-closed ``scripts/muhur.py`` scans the produced ``<data>`` clean."""
    monkeypatch.setattr(indir, "get", lambda url: _Yanit(_xlsx(SATIRLAR)))
    s = {"urls": ["http://x/CPTI15_v4.0.xlsx"], "dest": "cpti15/" + CPTI, "side": "deprem"}
    indir.fetch_cpti(tmp_path, "cpti15", s)
    r = subprocess.run([sys.executable, str(TOOLS / "muhur.py"), str(tmp_path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "seal clean" in r.stdout
