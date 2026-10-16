"""The single ``knotenlinie.elastik`` seam of K9.

K9 never imports the elastic kernel anywhere else.  This module is the one place that knows the
frozen public API of ``knotenlinie.elastik`` (``okada_ned(*, kaynak, alici_lat, alici_lon,
alici_derinlik_m, R=6371000.0) -> (N, 6)``, NED Voigt, Pa, tension positive), turns its Voigt
vector into the ``(3, 3)`` NED tension tensor the ledger's tensor columns expect, and raises
:class:`ElastikYok` when the package cannot be imported -- the channel's tests can then run against a
stub kernel, and full runs use the real Okada 1992 kernel.

``kelvin=True`` means the half-space (free-surface image) solution, which is what the frozen
kernel returns.  The full-space Kelvin point source is **not** part of the frozen API; asking for
``kelvin=False`` raises :class:`NotImplementedError` naming it DETERMINED-PENDING rather than
silently returning the half-space answer.
"""
from __future__ import annotations

from typing import Dict

import numpy as np

from knotenlinie.defter.geometri import fay_vektorleri

KAYNAK_ANAHTARLARI = (
    "dogrultu_deg", "egim_deg", "kayma_deg", "uzunluk_m", "genislik_m",
    "ust_derinlik_m", "kayma_m", "kaynak_lat", "kaynak_lon",
)


class ElastikYok(RuntimeError):
    """``knotenlinie.elastik`` is not importable on this machine (it is installed with the package)."""


def elastik_yukle():
    """Import ``knotenlinie.elastik`` lazily; raise :class:`ElastikYok` when it is absent."""
    try:
        import knotenlinie.elastik as elastik
    except ImportError as exc:  # pragma: no cover - knotenlinie/elastik ships with the package
        raise ElastikYok(
            "knotenlinie.elastik içe aktarılamadı; Okada 1992 elastik çekirdeği olmadan gerçek transfer "
            "hesaplanamaz (çekirdek paketle birlikte kurulur)"
        ) from exc
    return elastik


def voigt_den_tensor(voigt) -> np.ndarray:
    """``(6,)`` or ``(N, 6)`` NED Voigt vector(s) to ``(3, 3)`` or ``(N, 3, 3)`` tensors.

    Order is ``s_xx, s_yy, s_zz, s_xy, s_xz, s_yz`` (``knotenlinie.defter.sema.TENSOR_SUTUNLARI``).
    """
    v = np.asarray(voigt, dtype=np.float64)
    tek = v.ndim == 1
    if tek:
        v = v[None, :]
    if v.ndim != 2 or v.shape[1] != 6:
        raise ValueError(f"Voigt dizisi (N, 6) olmalı; alınan biçim {np.asarray(voigt).shape}")
    t = np.zeros(v.shape[:1] + (3, 3), dtype=np.float64)
    t[:, 0, 0], t[:, 1, 1], t[:, 2, 2] = v[:, 0], v[:, 1], v[:, 2]
    t[:, 0, 1] = t[:, 1, 0] = v[:, 3]
    t[:, 0, 2] = t[:, 2, 0] = v[:, 4]
    t[:, 1, 2] = t[:, 2, 1] = v[:, 5]
    return t[0] if tek else t


def alici_noktasi(satir) -> Dict[str, object]:
    """One receiver record from a fault-table row or a mapping.

    A fault-table row carries ``centroid_lat``, ``centroid_lon`` and ``depth_central_km`` (the
    DISS centre depth); a mapping may already carry ``alici_lat``, ``alici_lon``,
    ``alici_derinlik_m``.
    """
    def _al(satir, ad, varsayilan=None):
        try:
            v = satir[ad]
        except (KeyError, IndexError, TypeError):
            v = varsayilan
        return v

    lat = _al(satir, "alici_lat", _al(satir, "centroid_lat"))
    lon = _al(satir, "alici_lon", _al(satir, "centroid_lon"))
    derinlik = _al(satir, "alici_derinlik_m")
    if derinlik is None:
        derinlik = float(_al(satir, "depth_central_km", 8.0)) * 1e3
    fid = _al(satir, "fault_id", _al(satir, "id"))
    if lat is None or lon is None:
        raise ValueError("alıcıda ne alici_lat/lon ne de centroid_lat/lon var")
    return {
        "alici_lat": float(lat),
        "alici_lon": float(lon),
        "alici_derinlik_m": float(derinlik),
        "fault_id": fid,
    }


def _kaynak_sozlugu(kaynak) -> dict:
    eksik = [k for k in KAYNAK_ANAHTARLARI if k not in kaynak]
    if eksik:
        raise ValueError(f"kaynakta eksik anahtar: {eksik} (knotenlinie.elastik API'si)")
    return {k: kaynak[k] for k in KAYNAK_ANAHTARLARI}


def gerilme_tensoru(kaynak, alici, *, kelvin: bool = True) -> np.ndarray:
    """The ``(3, 3)`` NED tension tensor (Pa) at one receiver from one source rectangle.

    Calls the frozen ``knotenlinie.elastik.okada_ned`` (Okada 1992, half-space) and reshapes its Voigt
    output.  ``kaynak`` must carry the nine frozen keys; ``alici`` is a fault row or a mapping
    (:func:`alici_noktasi`).
    """
    if not kelvin:
        raise NotImplementedError(
            "tam uzay (Kelvin nokta kaynağı) çekirdeği knotenlinie.elastik donmuş API'sinde yok; "
            "kelvin=False DETERMINED-PENDING, yarım uzay sonucu sessizce döndürülmez"
        )
    elastik = elastik_yukle()
    nokta = alici_noktasi(alici)
    voigt = elastik.okada_ned(
        kaynak=_kaynak_sozlugu(kaynak),
        alici_lat=nokta["alici_lat"],
        alici_lon=nokta["alici_lon"],
        alici_derinlik_m=nokta["alici_derinlik_m"],
    )
    return voigt_den_tensor(voigt)


def fay_normal_kayma(fay_tablosu):
    """``(normal, slip)`` unit-vector arrays of a receiver table.

    The stored fault-table vectors are used when present (``fay_tablosu_dogrula`` has already checked
    them against the central angles); a table carrying only the angles is converted with
    ``knotenlinie.defter.geometri.fay_vektorleri``.
    """
    vektor = ("normal_n", "normal_e", "normal_d", "slip_n", "slip_e", "slip_d")
    if all(c in fay_tablosu.columns for c in vektor):
        n = fay_tablosu[["normal_n", "normal_e", "normal_d"]].to_numpy(dtype=np.float64)
        s = fay_tablosu[["slip_n", "slip_e", "slip_d"]].to_numpy(dtype=np.float64)
        return n, s
    n, s = fay_vektorleri(
        fay_tablosu["strike_central_deg"].to_numpy(),
        fay_tablosu["dip_central_deg"].to_numpy(),
        fay_tablosu["rake_central_deg"].to_numpy(),
    )
    return n, s
