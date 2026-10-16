"""The handover: the single place the cumulative replay stops.

The cumulative replay stops on 2015-12-31; in a blind-test window K9 adds only
the events after the replay and before that window, and the 1349-2015 events are never added again.
The 1349-2015 events live inside the cumulative initial state, so a window that starts
at ``t0`` may add only events **strictly after** the handover and **strictly before** ``t0``; an
event exactly on the handover instant belongs to the initial state, and an event inside
``[t0, t1)`` is not used to start its own window.

This module holds the only occurrence of the handover date; the K9 source list
(:func:`knotenlinie.kanal.tektonik_kaynak.kaynak_listesi`) calls :func:`pencere_kaynaklari`.
"""
from __future__ import annotations

import pandas as pd

DEVIR = "2015-12-31T23:59:59.999999Z"  # the handover instant


def _an(x) -> pd.Timestamp:
    t = pd.Timestamp(x)
    if t.tzinfo is None:
        raise ValueError(f"zaman dilimsiz: {x!r}; tz-aware UTC gerekir")
    return t.tz_convert("UTC")


def pencere_kaynaklari(kaynaklar, pencere_basi, *, devir: str = DEVIR):
    """Events strictly after the handover and strictly before the window start.

    ``kaynaklar`` is either a DataFrame carrying ``time_utc`` (a filtered copy is returned) or an
    iterable of records each carrying ``time_utc`` (a new list is returned; the input is never
    mutated).  The 1349-2015 list therefore passes through unchanged.
    """
    d = _an(devir)
    t0 = _an(pencere_basi)
    if isinstance(kaynaklar, pd.DataFrame):
        if len(kaynaklar) == 0:
            return kaynaklar.copy()
        zaman = pd.to_datetime(kaynaklar["time_utc"], utc=True)
        m = (zaman > d) & (zaman < t0)
        return kaynaklar.loc[m].reset_index(drop=True)
    return [k for k in kaynaklar if d < _an(k["time_utc"]) < t0]


def devir_sonrasi(kaynaklar, *, devir: str = DEVIR):
    """Events strictly after the handover, without an upper window (incremental list)."""
    d = _an(devir)
    if isinstance(kaynaklar, pd.DataFrame):
        if len(kaynaklar) == 0:
            return kaynaklar.copy()
        zaman = pd.to_datetime(kaynaklar["time_utc"], utc=True)
        return kaynaklar.loc[zaman > d].reset_index(drop=True)
    return [k for k in kaynaklar if _an(k["time_utc"]) > d]
