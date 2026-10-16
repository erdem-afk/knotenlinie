"""GCMT NDK record parser (the five-line record and its line-1 date/time), shared by the GCMT reader.

These helpers parse one NDK record only; they carry no region, window or forecast logic. The reader
that applies the <=2015 cutoff and the 2021 seal is :mod:`knotenlinie.etas_sonlu.gcmt`.
"""
from __future__ import annotations

import datetime as _dt
import math
import re
from typing import Dict, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

#: Lines per NDK record.
SATIR_SAYISI = 5

#: The output column order.
KOLONLAR: Tuple[str, ...] = (
    "olay_adi", "zaman_utc", "merkez_zaman_utc", "lat", "lon", "derinlik_km",
    "us", "M0_Nm", "Mw",
    "dogrultu1", "egim1", "kayma1", "dogrultu2", "egim2", "kayma2",
    "mrr_Nm", "mtt_Nm", "mpp_Nm", "mrt_Nm", "mrp_Nm", "mtp_Nm",
)

#: Line 1's time (columns 17-26, stripped); the seconds may be 60 (rolled into the next minute).
_SAAT_DESENI = re.compile(r"\A(\d{1,2}):(\d{1,2}):(\d{1,2})(?:\.(\d{1,6}))?\Z")

#: Tensor element names in NDK order (line 4): Mrr, Mtt, Mpp, Mrt, Mrp, Mtp.
_TENSOR_ADLARI = ("mrr_Nm", "mtt_Nm", "mpp_Nm", "mrt_Nm", "mrp_Nm", "mtp_Nm")


class BicimHatasi(ValueError):
    """A raw NDK record or field does not carry the declared format (line number only)."""


# --- date/time helpers -----------------------------------------------------

def _yil_onek(satir1: str) -> Optional[int]:
    """Line 1's columns 6-9 as a year when they are four ASCII digits (the seal's first look)."""
    t = satir1[5:9]
    return int(t) if len(t) == 4 and t.isascii() and t.isdigit() else None


def _tarih_coz(satir1: str) -> Optional[_dt.date]:
    """Line 1's date (columns 6-15, ``yyyy/mm/dd``), or ``None``; the text never leaves here."""
    try:
        return _dt.datetime.strptime(satir1[5:15].strip(), "%Y/%m/%d").date()
    except ValueError:
        return None


def _saat_coz(satir1: str, tarih: _dt.date) -> Optional[pd.Timestamp]:
    """Line 1's time (columns 17-26) on ``tarih`` as a UTC instant, or ``None``.

    ``ss`` may be 60: GCMT writes it for a rounded 59.95 s and for leap seconds, and it rolls
    into the next minute (ObsPy's NDK reader does the same).
    """
    m = _SAAT_DESENI.match(satir1[16:26].strip())
    if m is None:
        return None
    sa, dk, sn = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if sa > 23 or dk > 59 or sn > 60:
        return None
    mikro = int((m.group(4) or "").ljust(6, "0"))
    return (pd.Timestamp(tarih.isoformat(), tz="UTC")
            + pd.Timedelta(hours=sa, minutes=dk, seconds=sn, microseconds=mikro))


def _yer(satir_no: int, gizli: bool) -> str:
    """A message's locator: the line number, or nothing when ``gizli`` withholds it."""
    if gizli:
        return "NDK satırı (numara verilmez)"
    return f"NDK satır {satir_no}"


def _sayi(metin: str, yer: str) -> float:
    """A numeric field, or :class:`BicimHatasi` at ``yer`` (the text is never quoted)."""
    try:
        deger = float(metin)
    except (TypeError, ValueError):
        deger = None
    if deger is None or not math.isfinite(deger):   # 'nan'/'inf' parse but are no field 
        raise BicimHatasi(f"{yer}: sayısal alan çözülemedi")
    return deger


def _tam(metin: str, yer: str) -> int:
    """An integer field, or :class:`BicimHatasi` at ``yer``."""
    try:
        deger = int(metin)
    except (TypeError, ValueError):
        deger = None
    if deger is None:
        raise BicimHatasi(f"{yer}: tamsayı alan çözülemedi")
    return deger


# --- the record parser (after the line-1 gate) -----------------------------

def _kayit_ayristir(satirlar: Sequence[str], baslangic: int, zaman: pd.Timestamp,
                    gizli: bool = False) -> Dict[str, object]:
    """Convert one 5-line record whose line-1 instant is already classified.

    ``baslangic`` is the 1-based line number of line 1; ``gizli`` withholds it (the line number
    is not reported).  Every failure names the line it happened on, or withholds it, and never
    quotes the record's text.
    """
    _, satir2, satir3, satir4, satir5 = satirlar
    y3, y4, y5 = (_yer(baslangic + k, gizli) for k in (2, 3, 4))

    # line 2: CMT event name, fixed columns 1-16.
    olay_adi = satir2[0:16].strip()

    # line 3: "CENTROID:" fixed 1-9; the eight numbers from the fixed columns: shift
    # [10:18], its error [18:22], lat [22:29], its error [29:34], lon [34:42], its error [42:47],
    # depth [47:53], its error [53:58].  When columns 10-58 also split into exactly eight
    # whitespace tokens the two readings are cross-checked number by number; a touching field
    # drops below eight tokens, and then the fixed columns alone decide.
    if satir3[0:9] != "CENTROID:":
        raise BicimHatasi(f"{y3}: centroid satırı beklenen biçimde değil")
    sabit = (
        _sayi(satir3[10:18], y3), _sayi(satir3[18:22], y3),
        _sayi(satir3[22:29], y3), _sayi(satir3[29:34], y3),
        _sayi(satir3[34:42], y3), _sayi(satir3[42:47], y3),
        _sayi(satir3[47:53], y3), _sayi(satir3[53:58], y3),
    )
    p3 = satir3[9:58].split()
    if len(p3) == 8:
        for a, b in zip(sabit, (_sayi(belirtec, y3) for belirtec in p3)):
            if abs(a - b) > 1e-9:
                raise BicimHatasi(
                    f"{y3}: centroid satırı sütun okuması belirteç okumasıyla uyuşmuyor")
    elif len(p3) > 8:
        raise BicimHatasi(f"{y3}: centroid satırı beklenen biçimde değil")
    kayma, _, lat, _, lon, _, derinlik, _ = sabit

    # line 4: exponent (fixed 1-2), then exactly twelve numbers (value, error) in columns 3-80.
    us = _tam(satir4[0:2], y4)
    p4 = satir4[2:].split()
    if len(p4) != 12:
        raise BicimHatasi(f"{y4}: moment-tensör satırı 12 sayı taşımıyor")
    degerler = [_sayi(p4[2 * k], y4) for k in range(6)]

    # line 5: axes in 4-48 (nine numbers, not stored), scalar moment fixed 50-56, planes 58-80 (six).
    if len(satir5[3:48].split()) != 9:
        raise BicimHatasi(f"{y5}: asal eksen bölümü (sütun 4-48) 9 sayı taşımıyor")
    skaler = _sayi(satir5[49:56], y5)
    p5 = satir5[57:].split()
    if len(p5) != 6:
        raise BicimHatasi(f"{y5}: düğüm düzlemleri (sütun 58-80) 6 sayı taşımıyor")
    dogrultu1, egim1, kayma1, dogrultu2, egim2, kayma2 = (_sayi(v, y5) for v in p5)

    olcek = 10.0 ** us * 1e-7           # 10^us dyne.cm -> N.m
    m0 = skaler * olcek
    if not np.isfinite(m0) or m0 <= 0.0:
        raise BicimHatasi(f"{y5}: skaler moment pozitif değil")
    mw = (2.0 / 3.0) * (np.log10(m0) - 9.1)

    return {
        "olay_adi": olay_adi,
        "zaman_utc": zaman,
        "merkez_zaman_utc": zaman + pd.Timedelta(seconds=kayma),
        "lat": lat,
        "lon": lon,
        "derinlik_km": derinlik,
        "us": us,
        "M0_Nm": float(m0),
        "Mw": float(mw),
        "dogrultu1": dogrultu1,
        "egim1": egim1,
        "kayma1": kayma1,
        "dogrultu2": dogrultu2,
        "egim2": egim2,
        "kayma2": kayma2,
        **{ad: float(v) * olcek for ad, v in zip(_TENSOR_ADLARI, degerler)},
    }
