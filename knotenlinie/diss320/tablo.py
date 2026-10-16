"""DISS 3.2.0 GeoJSON readers and the seal (the subset used by the CRS layer).

The model's fault set is DISS 3.2.0's 293 sources: 167 composite (CSS, ``csspln320``) and
126 individual (ISS, ``iss320``).  This module reads those WFS GeoJSON layers into one dict
per feature (:func:`css_oku`, :func:`iss_oku`) and applies the seal (:func:`muhurle`).  The
builder of the full fault-geometry table (which used an external tide engine's geometry code)
is not part of this release.

Seal: any source whose ``created`` or ``updated`` is on or after 2021-01-01 is dropped.
DISS 3.2.0's latest record dates from 2015, so none is expected; the check is still enforced.

Clean room: DISS 3.2.0 is a published data product (INGV, CC BY 4.0).  No earthquake catalogue
is opened anywhere.
"""
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import pandas as pd
from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry

__all__ = [
    "CSS_SAYISAL", "CSS_SECMELI", "ISS_SAYISAL", "ISS_SECMELI",
    "MUHUR", "BicimHatasi", "css_oku", "iss_oku", "muhurle", "sha256_dosya",
]

#: DISS 3.2.0 CSS properties that must be numeric; quality flags are optional.
CSS_SAYISAL: Tuple[str, ...] = (
    "mindepth", "maxdepth", "strikemin", "strikemax", "dipmin", "dipmax", "rakemin",
    "rakemax", "srmin", "srmax", "maxmag",
)
CSS_SECMELI: Tuple[str, ...] = (
    "mindepthq", "maxdepthq", "strikeq", "dipq", "rakeq", "sliprateq", "maxmagq",
)

#: DISS 3.2.0 ISS properties: the four mapped-surface corners, the single central angles and
#: the recurrence interval are all required; the quality flags are optional.
ISS_SAYISAL: Tuple[str, ...] = (
    "length", "width", "mindepth", "maxdepth", "strike", "dip", "rake", "avgdispl", "srmin",
    "srmax", "recintmin", "recintmax", "maxmag",
    "latul", "lonul", "latur", "lonur", "latll", "lonll", "latlr", "lonlr",
)
ISS_SECMELI: Tuple[str, ...] = (
    "lengthq", "widthq", "mindepthq", "maxdepthq", "strikeq", "dipq", "rakeq", "avgdisplq",
    "sliprateq", "recintq", "maxmagq", "locationq",
)

#: Properties that must be present non-empty strings (the fault-table schema reads them directly).
METIN_ZORUNLU: Tuple[str, ...] = ("idsource", "sourcename", "linktoinfo")

#: The seal date: on or after this, a source is dropped.
MUHUR = pd.Timestamp("2021-01-01", tz="UTC")


class BicimHatasi(ValueError):
    """A GeoJSON feature or file that does not carry the declared DISS 3.2.0 fields."""


def _sayi(ham: Mapping[str, Any], alan: str, kimlik: str) -> float:
    """One required numeric property, or :class:`BicimHatasi` naming the source and the field."""
    if alan not in ham or ham[alan] is None:
        raise BicimHatasi(f"{kimlik}: {alan} alanı yok (D1)")
    deger = ham[alan]
    if isinstance(deger, bool):
        raise BicimHatasi(f"{kimlik}: {alan} alanı sayı değil: {deger!r} (D1)")
    try:
        return float(deger)
    except (TypeError, ValueError):
        raise BicimHatasi(f"{kimlik}: {alan} alanı sayı değil: {deger!r} (D1)") from None


def _sayisal_secmeli(ham: Mapping[str, Any], alan: str, kimlik: str) -> float:
    """An optional numeric property: missing/empty becomes NaN, a malformed value still raises."""
    if alan not in ham or ham[alan] is None or ham[alan] == "":
        return float("nan")
    return _sayi(ham, alan, kimlik)


def _metin(ham: Mapping[str, Any], alan: str, kimlik: str) -> str:
    if alan not in ham or ham[alan] is None or not str(ham[alan]).strip():
        raise BicimHatasi(f"{kimlik}: {alan} alanı yok ya da boş (D1)")
    return str(ham[alan])


def _tarih_coz(metin: str, alan: str, kimlik: str) -> Tuple[str, pd.Timestamp]:
    """A ``YYYYMMDD`` date string, both as DISS stores it and as a UTC timestamp."""
    try:
        an = datetime.datetime.strptime(str(metin).strip(), "%Y%m%d")
    except ValueError:
        raise BicimHatasi(f"{kimlik}: {alan} alanı YYYYMMDD değil: {metin!r} (D1)") from None
    return str(metin), pd.Timestamp(an, tz="UTC")


def _tarih(ham: Mapping[str, Any], alan: str, kimlik: str) -> Tuple[str, pd.Timestamp]:
    return _tarih_coz(_metin(ham, alan, kimlik), alan, kimlik)


def _geometri(ozellik: Mapping[str, Any], kimlik: str) -> Tuple[BaseGeometry, Mapping[str, Any]]:
    """Parse the WFS geometry.  Validity is deliberately not judged here: DISS 3.2.0's ISS
    MultiPolygons carry self-intersecting kinematic-symbol helpers ; the fault-table
    builder replaces every ISS geometry with the corner rectangle anyway."""
    ham = ozellik.get("geometry")
    if not isinstance(ham, Mapping):
        raise BicimHatasi(f"{kimlik}: geometri yok (D1)")
    try:
        geom = shape(ham)
    except Exception as hata:  # shapely names the coordinate error; keep the source id too
        raise BicimHatasi(f"{kimlik}: geometri okunamadı: {hata} (D1)") from None
    if geom.is_empty:
        raise BicimHatasi(f"{kimlik}: geometri boş (D1)")
    return geom, ham


def _oku(yol, katman: str, sayisal: Sequence[str], secmeli: Sequence[str]) -> List[Dict[str, Any]]:
    """One dict per GeoJSON feature: converted properties, a shapely geometry and the raw geometry.

    ``created``/``updated`` stay ``YYYYMMDD`` strings exactly as DISS stores them, with the parses
    available as ``created_utc``/``updated_utc`` for the seal (D4).
    """
    yol = str(yol)
    try:
        kayit = json.loads(Path(yol).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise BicimHatasi(f"{yol}: dosya yok (D1)") from None
    except json.JSONDecodeError as hata:
        raise BicimHatasi(f"{yol}: JSON okunamadı: {hata} (D1)") from None
    ozellikler = kayit.get("features")
    if not isinstance(ozellikler, list):
        raise BicimHatasi(f"{yol}: 'features' listesi yok (D1)")
    kayitlar: List[Dict[str, Any]] = []
    for sira, ozellik in enumerate(ozellikler):
        ham = ozellik.get("properties") if isinstance(ozellik, Mapping) else None
        if not isinstance(ham, Mapping):
            raise BicimHatasi(f"{yol}: {katman} #{sira}: 'properties' yok (D1)")
        kimlik = str(ham.get("idsource") or f"{katman}#{sira}")
        satir: Dict[str, Any] = dict(ham)
        for alan in METIN_ZORUNLU:
            satir[alan] = _metin(ham, alan, kimlik)
        for alan in sayisal:
            satir[alan] = _sayi(ham, alan, kimlik)
        for alan in secmeli:
            satir[alan] = _sayisal_secmeli(ham, alan, kimlik)
        olusma, olusma_utc = _tarih(ham, "created", kimlik)
        guncelleme, guncelleme_utc = _tarih(ham, "updated", kimlik)
        satir["created"], satir["updated"] = olusma, guncelleme
        satir["created_utc"], satir["updated_utc"] = olusma_utc, guncelleme_utc
        geom, ham_geom = _geometri(ozellik, kimlik)
        satir["geometry"], satir["geometry_json"] = geom, ham_geom
        kayitlar.append(satir)
    return kayitlar


def css_oku(yol) -> List[Dict[str, Any]]:
    """Read ``csspln320`` (DISS 3.2.0 composite sources) into one dict per feature (D1)."""
    return _oku(yol, "CSS", CSS_SAYISAL, CSS_SECMELI)


def iss_oku(yol) -> List[Dict[str, Any]]:
    """Read ``iss320`` (DISS 3.2.0 individual sources) into one dict per feature (D1)."""
    return _oku(yol, "ISS", ISS_SAYISAL, ISS_SECMELI)


def muhurle(kayitlar: Sequence[Mapping[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Drop sources created or updated on or after 2021-01-01; return kept and dropped ids (D4)."""
    kalan: List[Dict[str, Any]] = []
    atilan: List[str] = []
    for kayit in kayitlar:
        if kayit["created_utc"] >= MUHUR or kayit["updated_utc"] >= MUHUR:
            atilan.append(str(kayit["idsource"]))
        else:
            kalan.append(dict(kayit))
    return kalan, sorted(atilan)


def sha256_dosya(yol) -> str:
    """SHA256 of a file, read in chunks (the manifest's input digests)."""
    ozet = hashlib.sha256()
    with open(yol, "rb") as akis:
        for parca in iter(lambda: akis.read(1024 * 1024), b""):
            ozet.update(parca)
    return ozet.hexdigest()
