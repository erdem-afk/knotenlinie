"""Fault geometry: fault normal/slip vectors and the stress resolution onto a fault.

The fault set and the frame are fixed: DISS sources, north-east-down, normal and
slip unit vectors from strike, dip and rake.

The two functions follow the standard fault-vector convention of an external tide engine the
project used earlier (``fault_vectors`` / ``resolve_stress``, written by the project itself,
2026-09-29).  The formulas are the textbook strike/dip/rake vectors and the traction
resolution; the code here is self-contained and does not import that engine.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd

FAY_SUTUNLARI = ("id", "normal_n", "normal_e", "normal_d", "slip_n", "slip_e", "slip_d")
ACI_SUTUNLARI = ("strike_central_deg", "dip_central_deg", "rake_central_deg")


def fay_vektorleri(strike_deg, dip_deg, rake_deg) -> Tuple[np.ndarray, np.ndarray]:
    """Unit normal and slip vectors in NED for strike/dip/rake in degrees.

    Same arithmetic order as the external engine's ``fault_vectors``; broadcasting over a
    leading axis is added so a whole fault table resolves at once.
    """
    strike = np.deg2rad(np.asarray(strike_deg, dtype=np.float64))
    dip = np.deg2rad(np.asarray(dip_deg, dtype=np.float64))
    rake = np.deg2rad(np.asarray(rake_deg, dtype=np.float64))
    normal = np.stack([
        -np.sin(dip) * np.sin(strike),
        np.sin(dip) * np.cos(strike),
        -np.cos(dip),
    ], axis=-1)
    slip = np.stack([
        np.cos(rake) * np.cos(strike) + np.sin(rake) * np.cos(dip) * np.sin(strike),
        np.cos(rake) * np.sin(strike) - np.sin(rake) * np.cos(dip) * np.cos(strike),
        -np.sin(rake) * np.sin(dip),
    ], axis=-1)
    return normal.astype(np.float64), slip.astype(np.float64)


def gerilmeyi_coz(sigma, normal, slip) -> Tuple[np.ndarray, np.ndarray]:
    """Shear along rake and normal stress from a tensor (the ``resolve_stress`` convention).

    ``sigma`` may carry a leading time axis; ``normal`` and ``slip`` are the three
    NED components.
    """
    tensor = np.asarray(sigma, dtype=np.float64)
    n = np.asarray(normal, dtype=np.float64)
    s = np.asarray(slip, dtype=np.float64)
    traction = np.einsum("...ij,j->...i", tensor, n)
    tau = np.einsum("i,...i->...", s, traction)
    sigma_n = np.einsum("i,...i->...", n, traction)
    return tau.astype(np.float64, copy=False), sigma_n.astype(np.float64, copy=False)


def fay_tablosu_oku(yol) -> pd.DataFrame:
    """Load a DISS fault table (parquet or csv) and validate it."""
    yol = str(yol)
    df = pd.read_csv(yol) if yol.lower().endswith(".csv") else pd.read_parquet(yol)
    return fay_tablosu_dogrula(df)


def fay_tablosu_dogrula(df: pd.DataFrame) -> pd.DataFrame:
    """Validate id uniqueness, unit vectors, and angle/vector agreement.

    Where the central angle columns exist the vectors are recomputed with
    ``fay_vektorleri`` and compared against the stored ones, so a convention
    mismatch between the geometry artifact's angles and its stored vectors cannot
    pass silently.  No DISS version and no fault count is hard-coded here; the
    caller supplies the table and the writer hashes it into the provenance.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("fay tablosu bir pandas DataFrame olmalı")
    eksik = [c for c in FAY_SUTUNLARI if c not in df.columns]
    if eksik:
        raise ValueError(f"fay tablosunda eksik sütun: {eksik}")
    if df["id"].isna().any():
        raise ValueError("fay tablosunda boş id var")
    if df["id"].duplicated().any():
        kotu = sorted(df.loc[df["id"].duplicated(), "id"].astype(str).unique())
        raise ValueError(f"fay tablosunda id tekil değil: {kotu[:5]}")
    N = df[["normal_n", "normal_e", "normal_d"]].to_numpy(dtype=np.float64)
    S = df[["slip_n", "slip_e", "slip_d"]].to_numpy(dtype=np.float64)
    for ad, V in (("normal", N), ("slip", S)):
        sapma = np.abs(np.linalg.norm(V, axis=1) - 1.0)
        if np.any(sapma > 1e-9):
            raise ValueError(f"{ad} vektörleri birim değil (en büyük sapma {sapma.max():.3e})")
    if all(c in df.columns for c in ACI_SUTUNLARI):
        n2, s2 = fay_vektorleri(df[ACI_SUTUNLARI[0]].to_numpy(),
                                df[ACI_SUTUNLARI[1]].to_numpy(),
                                df[ACI_SUTUNLARI[2]].to_numpy())
        sapma = max(float(np.abs(N - n2).max()), float(np.abs(S - s2).max()))
        if sapma > 1e-9:
            raise ValueError(
                f"açılar ve saklanan vektörler uyuşmuyor (en büyük sapma {sapma:.3e}); "
                "geometri yapıtı ile fay_vektorleri aynı kuralı kullanmıyor"
            )
    return df
