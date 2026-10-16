"""Time handling: UTC is mandatory, kind is closed, consumers resample.

Every channel produces on its own natural step and declares its kind: ``series``
(Pa on a time grid), ``rate`` (Pa/year) or ``step`` (a jump in Pa at one instant).
Resampling to a consumer's step belongs to the consumer; this module
only parses, normalises to UTC and validates the kind.  A tz-naive or local-time
input is refused outright rather than assumed to be UTC.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TURLER = ("series", "rate", "step")


#: The one resolution every result carries: pandas 3's native unit, and under pandas 2 the unit
#: that holds instants before 1677 (catalogue events from 1349, as in CPTI15).  One unit for
#: every result, so two results always concatenate and subtract.
BIRIM = "us"


def utc_yap(x) -> pd.Series:
    """Return a tz-aware UTC datetime Series at microsecond resolution; refuse tz-naive or local input.

    The result is always ``datetime64[us, UTC]``, under pandas 2 as under pandas 3 on the compute server,
    whatever the input's range: before, an in-range input came back in nanoseconds and an older
    one in microseconds, so concatenating or subtracting two results raised
    ``OutOfBoundsDatetime``.  A finer input is floored to the microsecond (the ledger carries no finer
    instant).
    """
    seri = x if isinstance(x, pd.Series) else pd.Series(x)
    if pd.api.types.is_datetime64_any_dtype(seri.dtype):
        dt = seri
    else:
        try:
            dt = pd.to_datetime(seri, errors="raise")
        except (pd.errors.OutOfBoundsDatetime, OverflowError):
            # pandas 2 holds nanoseconds (1677-2262); an older instant (a catalogue event from 1349,
            # as in CPTI15) goes through microseconds, as pandas 3 does natively
            damgalar = []
            for v in seri:
                d = pd.Timestamp(v) if v is not None else pd.NaT
                if d is pd.NaT or pd.isna(d):
                    raise ValueError(
                        "time_utc boş (NaT); her satır bir UTC anı taşımalı"
                    )
                damgalar.append(d)
            if any(d.tz is None for d in damgalar):
                raise ValueError(
                    "time_utc zaman dilimsiz ya da yerel; tz-aware UTC gerekir"
                )
            yerel = [d.tz_convert("UTC").to_pydatetime().replace(tzinfo=None) for d in damgalar]
            dt = pd.Series(np.array(yerel, dtype="datetime64[us]"), index=seri.index).dt.tz_localize("UTC")
    # Every path refuses a NaT with its own message: pandas 3 parses 1349 natively at microseconds,
    # so the pre-1677 fallback above no longer runs for it and the check cannot live there
    # alone (every ledger row carries a UTC instant).
    if dt.isna().any():
        raise ValueError(
            "time_utc boş (NaT); her satır bir UTC anı taşımalı"
        )
    if getattr(dt.dtype, "tz", None) is None:
        raise ValueError(
            "time_utc zaman dilimsiz ya da yerel; tz-aware UTC gerekir"
        )
    return dt.dt.tz_convert("UTC").dt.as_unit(BIRIM)


def tur_dogrula(tur: str) -> str:
    """Accept only ``series``, ``rate`` or ``step``."""
    if tur not in TURLER:
        raise ValueError(f"geçersiz defter türü {tur!r}; beklenen: {list(TURLER)}")
    return tur
