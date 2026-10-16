"""Ledger reader: dispatch on the schema version, compute Delta-CFS, never store it.

The reader opens one channel/version parquet file, reads its schema version from the
metadata and validates the required columns of that version, requires and validates
the sibling provenance sidecar, and then *computes* Delta-CFS from the stored tau,
sigma_n and p with :func:`coulomb_taramasi`.  No stored Coulomb column exists because
none is ever written.  Unknown extra columns are returned untouched, never
dropped or reinterpreted.

B is required exactly when the file carries a non-null open pore pressure, so no
hidden friction parameter can change a channel's number.  The reader never
sums channels: a consumer that wants a total builds it explicitly and owns its summing rules.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq

from . import kunye, sema, zaman
from .coulomb import coulomb_taramasi
from .geometri import gerilmeyi_coz


@dataclass
class Defter:
    """One read ledger file: rows, the Delta-CFS scan, its record, metadata, version."""
    satirlar: pd.DataFrame
    cfs: Dict[float, np.ndarray]
    kunye: Dict[str, object]
    meta: Dict[str, object]
    sema_surum: int


def _meta_coz(ham: Dict[str, str], surum: int) -> Dict[str, object]:
    meta: Dict[str, object] = dict(ham)
    meta[sema.SEMA_META_ANAHTARI] = surum
    meta["satir"] = int(ham["satir"])
    meta["isaret"] = json.loads(ham["isaret"])
    rd = ham.get("referans_donem")
    meta["referans_donem"] = json.loads(rd) if rd else None
    return meta


def oku(yol, *, mu_prime=(0.2, 0.4, 0.6), B=None, kunye_dogrula: bool = True,
        hash_dogrula: bool = False) -> Defter:
    """Read a ledger file and compute its Delta-CFS scan (Pa)."""
    yol = os.fspath(yol)
    tablo = pq.read_table(yol)
    ham = sema.meta_oku(tablo.schema.metadata)
    surum = sema.surum_oku(ham)
    bilgi = sema.surum_bilgisi(surum)
    eksik = [c for c in bilgi["zorunlu"] if c not in tablo.column_names]
    if eksik:
        raise sema.SemaHatasi(f"v{surum} dosyasında zorunlu sütun eksik: {eksik}")
    if ham.get("birim") != sema.BIRIM:
        raise sema.SemaHatasi(
            f"defter birimi {ham.get('birim')!r}; yalnız {sema.BIRIM} kabul edilir"
        )

    # the distinct kinds from the Arrow column, not a per-row Python loop over the pandas column: on
    # pandas 3's Arrow-backed strings that loop was ~76 % of the read of a 25.7M-row ledger part
    turler = sorted({str(t) for t in pc.unique(tablo.column("kind")).to_pylist()})
    df = tablo.to_pandas()
    if len(turler) != 1:
        raise ValueError(f"defter dosyasında karışık tür var: {turler}")
    tur = zaman.tur_dogrula(turler[0])
    if ham.get("tur") != tur:
        raise ValueError(
            f"künye meta verisi türü {ham.get('tur')!r} ile satır türü {tur!r} uyuşmuyor"
        )
    df["time_utc"] = zaman.utc_yap(df["time_utc"])

    kunye_yolu = os.path.join(os.path.dirname(os.path.abspath(yol)), str(ham.get("kunye", "")))
    if not os.path.exists(kunye_yolu):
        raise kunye.KunyeHatasi(f"defter künyesi bulunamadı: {kunye_yolu}")
    if kunye_dogrula:
        rec = kunye.kunye_oku(kunye_yolu)
    else:
        with open(kunye_yolu, encoding="utf-8") as akis:
            rec = json.load(akis)
    if rec["sema_surum"] != surum:
        raise kunye.KunyeHatasi(f"künye şema sürümü {rec['sema_surum']} ile dosya sürümü {surum} uyuşmuyor")
    if rec["tur"] != tur:
        raise kunye.KunyeHatasi(f"künye türü {rec['tur']!r} ile dosya türü {tur!r} uyuşmuyor")
    if int(rec["satir"]) != len(df):
        raise kunye.KunyeHatasi(f"künye satır sayısı {rec['satir']} ile dosya {len(df)} uyuşmuyor")
    if rec["kanal"] != ham.get("kanal") or rec["kanal_surum"] != ham.get("kanal_surum"):
        raise kunye.KunyeHatasi("künye kanal/sürüm bilgisi dosya meta verisiyle uyuşmuyor")
    if hash_dogrula and kunye.girdi_ozeti(yol) != rec["defter_sha256"]:
        raise kunye.KunyeHatasi("defter sha256 kaydı dosyayla uyuşmuyor")

    p = df["p_Pa"].to_numpy(dtype=np.float64) if "p_Pa" in df.columns else None
    p_dolu = p is not None and bool(np.any(~np.isnan(p)))
    if p_dolu and B is None:
        raise ValueError(
            "defterde dolu p_Pa var ama B verilmedi; gizli bir B kullanılmaz"
        )
    cfs = coulomb_taramasi(
        df["tau_Pa"].to_numpy(dtype=np.float64),
        df["sigma_n_Pa"].to_numpy(dtype=np.float64),
        p=p, mu_primes=mu_prime, B=B,
    )
    return Defter(df, cfs, rec, _meta_coz(ham, surum), surum)


def tensorden_coz(satirlar: pd.DataFrame, normal, slip):
    """Re-resolve tau and sigma_n on a sampled geometry from the stored tensor.

    Serves the geometry-uncertainty sampling of the ledger: the six Voigt components are
    rebuilt into a 3x3 NED tensor and projected on the supplied unit vectors.
    """
    eksik = [c for c in sema.TENSOR_SUTUNLARI if c not in satirlar.columns]
    if eksik:
        raise ValueError(f"satırlarda tensör sütunları yok: {eksik}")
    n = len(satirlar)
    sigma = np.full((n, 3, 3), np.nan, dtype=np.float64)
    sigma[:, 0, 0] = satirlar["s_xx_Pa"].to_numpy(dtype=np.float64)
    sigma[:, 1, 1] = satirlar["s_yy_Pa"].to_numpy(dtype=np.float64)
    sigma[:, 2, 2] = satirlar["s_zz_Pa"].to_numpy(dtype=np.float64)
    xy = satirlar["s_xy_Pa"].to_numpy(dtype=np.float64)
    xz = satirlar["s_xz_Pa"].to_numpy(dtype=np.float64)
    yz = satirlar["s_yz_Pa"].to_numpy(dtype=np.float64)
    sigma[:, 0, 1] = sigma[:, 1, 0] = xy
    sigma[:, 0, 2] = sigma[:, 2, 0] = xz
    sigma[:, 1, 2] = sigma[:, 2, 1] = yz
    return gerilmeyi_coz(sigma, normal, slip)
