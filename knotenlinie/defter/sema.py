"""Ledger schema registry: one version per stored column set.

The ledger format is fixed: one parquet file per channel and
version, rows carrying fault id, UTC time, kind, tau and sigma_n in Pa, an optional
open pore pressure and an optional six-component stress tensor.  Delta-CFS is not a
stored column; the reader computes it.

The shared ledger code is written once, by one hand, before
any channel is built.  The mechanical form of the schema rule is here: adding a
field (for example the producer field ``uretici``) means
registering a new version with its own required and optional columns.  Stored files
are never rewritten, the reader understands every registered version, and an
unregistered version raises with its number instead of being guessed.
"""
from __future__ import annotations

from typing import Dict, Sequence, Tuple

SEMA_META_ANAHTARI = "defter_sema_surum"
BIRIM = "Pa"

# The six Voigt components of the NED tension tensor; all six or none.
TENSOR_SUTUNLARI: Tuple[str, ...] = (
    "s_xx_Pa", "s_yy_Pa", "s_zz_Pa", "s_xy_Pa", "s_xz_Pa", "s_yz_Pa",
)

ZORUNLU_V1: Tuple[str, ...] = ("fault_id", "time_utc", "kind", "tau_Pa", "sigma_n_Pa")
SECMELI_V1: Tuple[str, ...] = ("p_Pa",) + TENSOR_SUTUNLARI

# Version -> {"zorunlu": required columns, "secmeli": optional columns}.
# v2 adds the producer field ``uretici``: every new ledger
# file names the layer, model and version that produced it. v1 files stay readable as they are.
ZORUNLU_V2: Tuple[str, ...] = ZORUNLU_V1 + ("uretici",)
SEMA_SURUMLARI: Dict[int, Dict[str, Sequence[str]]] = {
    1: {"zorunlu": ZORUNLU_V1, "secmeli": SECMELI_V1},
    2: {"zorunlu": ZORUNLU_V2, "secmeli": SECMELI_V1},
}

META_ANAHTARLARI: Tuple[str, ...] = (
    "kanal", "kanal_surum", "tur", "isaret", "referans_donem",
    "birim", "kunye", "satir", "olusturma_utc",
)


class SemaHatasi(ValueError):
    """Malformed or missing ledger schema metadata."""


class SemaSurumHatasi(SemaHatasi):
    """A ledger file declares a schema version that is not registered."""


def guncel_surum() -> int:
    """Newest registered schema version; the writer always stores this one."""
    return max(SEMA_SURUMLARI)


def surum_ekle(surum: int, zorunlu: Sequence[str], secmeli: Sequence[str] = ()) -> None:
    """Register a new schema version (for example the producer field ``uretici``).

    Existing versions and files are untouched; the reader dispatches on the file's
    own version number.
    """
    if surum in SEMA_SURUMLARI:
        raise SemaHatasi(f"şema sürümü zaten kayıtlı: {surum}")
    SEMA_SURUMLARI[surum] = {"zorunlu": tuple(zorunlu), "secmeli": tuple(secmeli)}


def surum_bilgisi(surum: int) -> Dict[str, Sequence[str]]:
    """Required and optional columns of one registered version."""
    if surum not in SEMA_SURUMLARI:
        raise SemaSurumHatasi(
            f"defter şema sürümü {surum} kayıtlı değil; "
            f"kayıtlı sürümler: {sorted(SEMA_SURUMLARI)}"
        )
    return SEMA_SURUMLARI[surum]


def meta_oku(meta) -> Dict[str, str]:
    """Decode parquet key-value metadata into a text dictionary."""
    if not meta:
        raise SemaHatasi("parquet dosyasında künye meta verisi yok")
    out: Dict[str, str] = {}
    for anahtar, deger in meta.items():
        k = anahtar.decode("utf-8") if isinstance(anahtar, bytes) else str(anahtar)
        v = deger.decode("utf-8") if isinstance(deger, bytes) else str(deger)
        out[k] = v
    return out


def surum_oku(meta: Dict[str, str]) -> int:
    """Schema version declared by a ledger file, with a clear error when unknown."""
    ham = meta.get(SEMA_META_ANAHTARI)
    if ham is None:
        raise SemaHatasi(f"parquet meta verisinde '{SEMA_META_ANAHTARI}' yok")
    try:
        surum = int(ham)
    except (TypeError, ValueError):
        raise SemaHatasi(f"'{SEMA_META_ANAHTARI}' sayı değil: {ham!r}") from None
    surum_bilgisi(surum)
    return surum
