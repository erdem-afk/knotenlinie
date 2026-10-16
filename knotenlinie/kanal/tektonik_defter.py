"""The single ledger writer seam of the K9 transfer.

Every K9 ledger file is published through :func:`yaz_kanal`, which wraps
``knotenlinie.defter.yaz`` and adds only the rules of the serial chain:

* the producer string ``uretici`` is required and non-empty;
* the declared time kind ``tur`` must be the channel's own -- ``step`` for K9;
* K9 is earthquake-fed (``deprem_girdisi=True``) and can only publish with a clean seal block;
* no column named like a Coulomb quantity may exist -- Delta-CFS is computed by the reader and
  never stored.

The module also carries the compute/publish split used by the CLIs: :func:`is_yaz` / :func:`is_oku`
write an intermediate row table (parquet, with the acceptance record and the input list in its
key-value metadata) so a heavy ``onar``/``aktar``/``psgrn`` run does not have to be repeated by
``yaz``.  Summing channels is not offered anywhere here.
"""
from __future__ import annotations

import json
import os
from typing import Dict, Iterable, Optional

import pandas as pd

from knotenlinie.defter import yaz as _yaz

KANAL_TURLERI: Dict[str, str] = {"K9": "step"}
DEPREM_KANALLARI = ("K9",)
_YASAK_ONEK = ("cfs", "dcfs", "delta_cfs", "delta_coulomb", "coulomb")


def _yasak_sutunlar(satirlar: pd.DataFrame) -> None:
    for c in satirlar.columns:
        lc = str(c).strip().lower()
        if any(lc == y or lc.startswith(y + "_") for y in _YASAK_ONEK):
            raise ValueError(f"defterde '{c}' sütunu olamaz; Delta-CFS hesaplanır, saklanmaz")


def yaz_kanal(yol, *, kanal: str, surum: str, satirlar, tur: str, isaret, girdiler: Iterable = (),
              kabul, uretici: str, deprem_girdisi: bool = False, muhur=None,
              referans_donem=None) -> str:
    """Publish one channel/version ledger file plus its provenance sidecar.

    ``yol`` is a file or a directory (the writer names a directory's file
    ``<kanal>_<surum>.parquet``).  ``kabul`` is the channel's acceptance record and must have
    passed; nothing is written before it does.
    """
    if kanal not in KANAL_TURLERI:
        raise ValueError(f"bu zincirin kanalı değil: {kanal!r}; beklenen {sorted(KANAL_TURLERI)}")
    if not isinstance(uretici, str) or not uretici.strip():
        raise ValueError("üretici (uretici) zorunlu ve boş olamaz")
    beklenen = KANAL_TURLERI[kanal]
    if str(tur) != beklenen:
        raise ValueError(f"{kanal} türü {beklenen!r} olmalı; verilen {tur!r}")
    if kanal in DEPREM_KANALLARI and not deprem_girdisi:
        raise ValueError(
            f"{kanal} deprem beslemeli bir kanaldır; deprem_girdisi=True ve temiz mühür olmadan "
            "yayımlanamaz"
        )
    if kanal not in DEPREM_KANALLARI and deprem_girdisi:
        raise ValueError(f"{kanal} deprem beslemeli değil; deprem_girdisi=True olamaz")
    df = satirlar if isinstance(satirlar, pd.DataFrame) else pd.DataFrame(satirlar)
    if df.empty:
        raise ValueError(f"{kanal}/{surum}: boş satır tablosu yazılmaz")
    _yasak_sutunlar(df)
    if not os.fspath(yol).endswith(".parquet"):
        os.makedirs(os.fspath(yol), exist_ok=True)      # a directory target is created here
    return _yaz(
        yol, kanal=kanal, kanal_surum=str(surum), satirlar=df, isaret=dict(isaret),
        referans_donem=referans_donem, girdiler=girdiler, kabul=kabul,
        deprem_girdisi=deprem_girdisi, muhur=muhur, uretici=uretici,
    )


# --- intermediate row table for the compute/publish split ----------------------------------


def is_yaz(yol, satirlar, *, kabul: dict, girdiler: Iterable = (), ek: Optional[dict] = None) -> str:
    """Write an intermediate row table (parquet) with its acceptance and input list.

    The acceptance record, the input list and the run report travel in a sibling ``<yol>.json``
    sidecar, so the row table itself stays a plain dataframe any reader can open.
    """
    df = satirlar if isinstance(satirlar, pd.DataFrame) else pd.DataFrame(satirlar)
    if "time_utc" in df.columns:
        df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    yol = os.fspath(yol)
    kok = os.path.dirname(os.path.abspath(yol))
    os.makedirs(kok, exist_ok=True)
    gecici = yol + ".tmp"
    df.to_parquet(gecici, index=False)
    os.replace(gecici, yol)
    yan, gecici_yan = yol + ".json", yol + ".json.tmp"
    with open(gecici_yan, "w", encoding="utf-8") as akis:
        json.dump({"kabul": kabul, "girdiler": list(girdiler), "ek": ek or {}}, akis,
                  ensure_ascii=False, default=str, indent=1)
    os.replace(gecici_yan, yan)
    return yol


def is_oku(yol):
    """Read an intermediate row table plus its acceptance record and input list."""
    yol = os.fspath(yol)
    df = pd.read_parquet(yol)
    with open(yol + ".json", encoding="utf-8") as akis:
        yan = json.load(akis)
    return df, yan
