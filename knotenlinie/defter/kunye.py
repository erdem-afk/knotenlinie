"""Provenance record: the sidecar that travels with every ledger file.

Next to each ledger file stand the input references and sha256 values,
the code version, the sign declaration, the reference period and the acceptance
result.  The record is written by code, never by hand: the writer builds it here and
the reader validates it here.  The acceptance condition and the seal live in
:mod:`knotenlinie.defter.kabul`; the code-version block in :mod:`knotenlinie.defter.kod`.

No cross-channel total and no ``topla`` field exists anywhere; summing
channels is a consumer's explicit decision.
"""
from __future__ import annotations

import json
import re
from typing import Dict, Iterable, List, Optional, Sequence

from . import sema
from .isaret import isaret_dogrula
from .kabul import KabulHatasi, kabul_dogrula, muhur_blogu
from .kod import girdi_ozeti, kod_bloku, simdi_utc
from .zaman import TURLER

RECORD_TYPE = "defter-kunye"
RECORD_VERSION = 1
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

__all__ = [
    "KunyeHatasi", "KabulHatasi", "girdi_ozeti", "girdileri_kaydet",
    "kunye_olustur", "kunye_dogrula", "kunye_yaz", "kunye_oku", "RECORD_TYPE",
    "RECORD_VERSION",
]


class KunyeHatasi(ValueError):
    """Malformed or incomplete provenance record."""


def _girdi_kaydi(girdi) -> Dict[str, str]:
    if isinstance(girdi, dict):
        yol = girdi["yol"]
        rol = girdi.get("rol", "")
        ozet = girdi.get("sha256") or girdi_ozeti(yol)
    elif isinstance(girdi, (tuple, list)):
        yol, rol = girdi[0], (girdi[1] if len(girdi) > 1 else "")
        ozet = girdi_ozeti(yol)
    else:
        yol, rol, ozet = str(girdi), "", girdi_ozeti(girdi)
    if not _SHA256.match(ozet):
        raise KunyeHatasi(f"girdi sha256 geçersiz: {yol}")
    return {"yol": str(yol), "sha256": ozet, "rol": str(rol)}


def girdileri_kaydet(girdiler: Iterable) -> List[Dict[str, str]]:
    """Normalise an input list into provenance input records with sha256 values."""
    return [_girdi_kaydi(g) for g in girdiler]


def kunye_olustur(*, kanal: str, kanal_surum: str, sema_surum: int, defter_dosya: str,
                  defter_sha256: str, satir: int, tur: str, isaret=None,
                  referans_donem=None, girdiler: Iterable = (), kabul,
                  deprem_girdisi: bool = False, muhur=None, uretici: Optional[str] = None,
                  olusturma_utc: Optional[str] = None, kod=None) -> Dict[str, object]:
    """Build the provenance record; every field is produced by code, not typed by hand."""
    if not str(kanal).strip() or not str(kanal_surum).strip():
        raise KunyeHatasi("kanal ve kanal_surum boş olamaz")
    if tur not in TURLER:
        raise KunyeHatasi(f"geçersiz tür {tur!r}; beklenen: {list(TURLER)}")
    if not _SHA256.match(defter_sha256):
        raise KunyeHatasi("defter_sha256 geçersiz")
    if not isinstance(satir, int) or satir < 0:
        raise KunyeHatasi("satir negatif olmayan bir tam sayı olmalı")
    return {
        "record_type": RECORD_TYPE,
        "record_version": RECORD_VERSION,
        "kanal": str(kanal),
        "kanal_surum": str(kanal_surum),
        "sema_surum": int(sema_surum),
        "defter_dosya": str(defter_dosya),
        "defter_sha256": str(defter_sha256),
        "satir": int(satir),
        "tur": tur,
        "olusturma_utc": olusturma_utc or simdi_utc(),
        "kod": kod if kod is not None else kod_bloku(),
        "isaret": isaret_dogrula(isaret),
        "referans_donem": referans_donem if referans_donem is not None else None,
        "birim": sema.BIRIM,
        "girdiler": girdileri_kaydet(girdiler),
        "kabul": kabul_dogrula(kabul),
        "muhur": muhur_blogu(deprem_girdisi, muhur),
        "uretici": uretici,
    }


def _zorunlu(rec: Dict[str, object], alanlar: Sequence[str], yer: str) -> None:
    eksik = [a for a in alanlar if a not in rec]
    if eksik:
        raise KunyeHatasi(f"{yer} eksik alan: {eksik}")


def kunye_dogrula(rec) -> Dict[str, object]:
    """Check every provenance field, the closed enums and the acceptance condition."""
    if not isinstance(rec, dict):
        raise KunyeHatasi("künye bir JSON nesnesi olmalı")
    _zorunlu(rec, ("record_type", "record_version", "kanal", "kanal_surum", "sema_surum",
                   "defter_dosya", "defter_sha256", "satir", "tur", "olusturma_utc",
                   "kod", "isaret", "referans_donem", "birim", "girdiler", "kabul",
                   "muhur", "uretici"), "künye")
    if rec["record_type"] != RECORD_TYPE or rec["record_version"] != RECORD_VERSION:
        raise KunyeHatasi(f"künye türü/sürümü tanınmıyor: {rec['record_type']!r}/{rec['record_version']!r}")
    if not str(rec["kanal"]).strip():
        raise KunyeHatasi("künyede kanal boş")
    if not isinstance(rec["sema_surum"], int):
        raise KunyeHatasi("künyede sema_surum tam sayı değil")
    if not _SHA256.match(str(rec["defter_sha256"])):
        raise KunyeHatasi("künyede defter_sha256 geçersiz")
    if not isinstance(rec["satir"], int) or rec["satir"] < 0:
        raise KunyeHatasi("künyede satir geçersiz")
    if rec["tur"] not in TURLER:
        raise KunyeHatasi(f"künyede geçersiz tür: {rec['tur']!r}")
    if not str(rec["olusturma_utc"]).endswith("Z"):
        raise KunyeHatasi("künyede olusturma_utc ISO-8601 Z değil")
    kod = rec["kod"]
    if not isinstance(kod, dict):
        raise KunyeHatasi("künyede kod bloğu sözlük değil")
    _zorunlu(kod, ("git_commit", "git_kirli", "paket_sha256"), "kod bloğu")
    if not isinstance(kod["git_kirli"], bool):
        raise KunyeHatasi("kod.git_kirli mantıksal değil")
    if not isinstance(kod["paket_sha256"], dict) or not kod["paket_sha256"]:
        raise KunyeHatasi("kod.paket_sha256 boş")
    isaret_dogrula(rec["isaret"])
    rd = rec["referans_donem"]
    if rd is not None:
        if not isinstance(rd, dict) or set(rd) != {"from", "to"}:
            raise KunyeHatasi("referans_donem null ya da {'from','to'} olmalı")
        if not str(rd["from"]).strip() or not str(rd["to"]).strip():
            raise KunyeHatasi("referans_donem.from/to boş")
    if rec["birim"] != sema.BIRIM:
        raise KunyeHatasi(f"künyede birim {rec['birim']!r}; yalnız {sema.BIRIM} kabul edilir")
    girdiler = rec["girdiler"]
    if not isinstance(girdiler, list):
        raise KunyeHatasi("künyede girdiler liste değil")
    for g in girdiler:
        if not isinstance(g, dict):
            raise KunyeHatasi("girdi kaydı sözlük değil")
        _zorunlu(g, ("yol", "sha256", "rol"), "girdi kaydı")
        if not _SHA256.match(str(g["sha256"])):
            raise KunyeHatasi(f"girdi sha256 geçersiz: {g.get('yol')}")
    kabul_dogrula(rec["kabul"])
    muhur = rec["muhur"]
    if not isinstance(muhur, dict) or "gerekli" not in muhur:
        raise KunyeHatasi("künyede mühür bloğu geçersiz")
    if muhur["gerekli"] and muhur.get("durum") != "clean":
        raise KabulHatasi("mühür gerekli ama durum 'clean' değil")
    if rec["uretici"] is not None and not str(rec["uretici"]).strip():
        raise KunyeHatasi("künyede uretici boş")
    return rec


def kunye_yaz(yol: str, rec: Dict[str, object]) -> str:
    """Write a validated record as JSON; the only writer of a sidecar."""
    kunye_dogrula(rec)
    with open(yol, "w", encoding="utf-8") as akis:
        json.dump(rec, akis, indent=2, ensure_ascii=False, sort_keys=False)
        akis.write("\n")
    return yol


def kunye_oku(yol: str) -> Dict[str, object]:
    """Read and validate a sidecar record."""
    with open(yol, encoding="utf-8") as akis:
        rec = json.load(akis)
    return kunye_dogrula(rec)
