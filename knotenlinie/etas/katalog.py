"""Catalog reader, cutoff gate, seal gate, regions, magnitude handling.

The reader is the only place where a raw catalog file is opened, and it enforces
three gates *inside* the read, before anything is returned or computed:

1. **File-year gate.** The ISIDe adapter parses the four-digit year out of
   the file name and refuses to open a file whose year is >= 2016.  A broad glob
   over a data directory therefore cannot reach ``iside_2016..2020``.
2. **Seal gate.** If a parsed row carries ``time_utc >= 2021-01-01T00:00:00Z``
   the reader raises :class:`MuhurIhlali` naming the file and the count.  It stops,
   it does not drop: the seal is not a filter.
3. **Cutoff gate.** Rows after ``2015-12-31T23:59:59.999999Z`` are dropped
   and counted.  ``2015-12-31T23:59:59.999999Z`` is kept, ``2016-01-01T00:00:00Z``
   is dropped.

Columns are resolved by *header name*, never by byte offset.  The
Apennines box of :data:`BOLGELER` is exact; the Italy-wide bounds are a declared
coarse rectangle, not a national border — a polygon is a later refinement and is
deliberately not built here.

Clean-room implementation from the equations published in Ogata 1988/1998,
Zhuang et al. 2002, Omi et al. 2014 and Hainzl 2016; no code copied from the pyetas package
(AGPL), the CRAN ETAS package (GPL) or Zhuang's Fortran sd package.
"""
from __future__ import annotations

import datetime as _dt
import functools
import glob as _glob
import os
import re
import unicodedata as _unicodedata
import warnings
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

# The one suppressed-time-parse lock, the same object as in
# ``knotenlinie.kanal.tektonik_kaynak``; a per-copy lock would let the two copies' ``catch_warnings()``
# blocks overlap and drop each other's "ignore".  It is an ``RLock`` taken around the whole body of
# every reader, and it also covers the shared unrecognised-timezone column parse.
from knotenlinie.kanal.tektonik_kaynak import (_ZAMAN_KILIDI, _iki_hane_yil_maskesi, _taban_alti_nat,
                                        _yanlis_okunan_muhur, _zaman_sutunu_canli, _metin_muhur_yili,
                                        _metin_muhur_sayilir)


def _kilitli(fn):
    """Run ``fn`` while the one shared time-parse lock is held.

    ``warnings.catch_warnings()`` swaps one process-wide filter list.  Holding ``_ZAMAN_KILIDI``
    around a whole reader serialises the reader's own suppressed parses, including pandas'
    (``pandas_dtype``, ``read_csv``), so a reader call cannot drop another parse's "ignore".
    The guarantee is only for a gate run in one thread: a caller's own pandas or warnings work in
    another thread can still swap the process-wide list.  The lock is re-entrant, so a locked
    reader may call helpers (``_cerceve``, ``_yil_onek``) that also take it.
    """
    @functools.wraps(fn)
    def sarmal(*args, **kwargs):
        with _ZAMAN_KILIDI:
            return fn(*args, **kwargs)
    return sarmal

# --- fixed constants -------------------------------------------------------

#: Last instant kept.  Inclusive: the microsecond below 2016 is kept.
KESIM = pd.Timestamp("2015-12-31T23:59:59.999999Z")
#: First calendar year the loader refuses to open.  The cutoff ends 2015.
ACILMAYAN_YIL = 2016
#: First instant of the seal.  At or after -> stop.
MUHUR = pd.Timestamp("2021-01-01T00:00:00Z")
#: The 2015 cutoff as a plain UTC datetime, for reports.
KESIM_ISO = "2015-12-31T23:59:59.999999Z"

#: Region boxes ``(lat_min, lat_max, lon_min, lon_max)``.  ``apennine`` is the
#: effect-scale run's box and is exact.  ``italy`` is a coarse declared rectangle
#: around the peninsula, not a border; a polygon is a later refinement.
BOLGELER: Dict[str, Tuple[float, float, float, float]] = {
    "apennine": (41.5, 44.0, 12.0, 14.5),
    "italy": (35.0, 48.0, 6.0, 20.0),
}

#: The exact first line of an ISIDe FDSN export (scripts/indir.py).
ISIDE_HEADER = (
    "#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|"
    "MagType|Magnitude|MagAuthor|EventLocationName|EventType"
)

_TABLO_KOLONLARI = ("time_utc", "lat", "lon", "depth_km", "mag", "mag_type", "source",
                    "event_id", "catalog_file")


class MuhurIhlali(RuntimeError):
    """A record on or after 2021-01-01 was parsed; the seal forbids reading it."""


class BicimHatasi(ValueError):
    """A raw file does not carry the header the adapter declares."""


# --- helpers ---------------------------------------------------------------

def _kolon(df: pd.DataFrame, adaylar: Sequence[str], dosya: str, zorunlu: bool = True) -> Optional[str]:
    """Resolve a column by a declared candidate list, case-insensitively."""
    alt = {str(c).strip().lstrip("#").lower(): c for c in df.columns}
    for ad in adaylar:
        if ad.strip().lower() in alt:
            return alt[ad.strip().lower()]
    if zorunlu:
        # Name only the file and the missing column candidates,
        # never a header or row value (a headerless file's first data row is the header here).
        raise BicimHatasi(
            f"{os.path.basename(str(dosya))}: missing a required column "
            f"(none of {list(adaylar)})")
    return None


def _sayi(seri: pd.Series) -> pd.Series:
    return pd.to_numeric(seri, errors="coerce")


#: The default-ignorable leading characters stripped by :func:`_onek_temizle` in addition to
#: whitespace and category ``Cf``; the same set as in
#: ``knotenlinie.kanal.tektonik_kaynak``.
_DEFAULT_IGNORABLE_ARALIKLAR = (
    (0x034F, 0x034F), (0x115F, 0x1160), (0x17B4, 0x17B5), (0x180B, 0x180F),
    (0x3164, 0x3164), (0xFE00, 0xFE0F), (0xFFA0, 0xFFA0), (0xE0000, 0xE0FFF),
)


def _onemsenmez_karakter(karakter: str) -> bool:
    """True when ``karakter`` is stripped before the leading-year rule.

    Whitespace, category ``Cf`` and the listed Default_Ignorable_Code_Point ranges (they include
    U+034F and U+FE0F, both category ``Mn``).
    """
    if karakter.isspace() or _unicodedata.category(karakter) == "Cf":
        return True
    nokta = ord(karakter)
    return any(alt <= nokta <= ust for alt, ust in _DEFAULT_IGNORABLE_ARALIKLAR)


def _onek_temizle(metin: str) -> str:
    """Strip leading whitespace, category ``Cf`` and the listed default-ignorables.

    A leading NBSP, ZWSP, BOM, word joiner, soft hyphen, ... must
    not hide a sealed year; whitespace and format characters alternate, so a space before a BOM is
    stripped too.  The set includes the named
    Default_Ignorable_Code_Point ranges (U+034F, U+FE0F, ...).  This is on the safe side -- it
    seals more, never less.  The scan is linear (an index walk, not one-character slicing).
    ``knotenlinie.kanal.tektonik_kaynak._onek_temizle`` is the same rule.
    """
    i = 0
    n = len(metin)
    while i < n and _onemsenmez_karakter(metin[i]):
        i += 1
    return metin[i:]


def _uc_yili(deger) -> Optional[int]:
    """The later endpoint's calendar year of a Period or Interval cell, or ``None``.

    a Period/Interval cell is sealed when either endpoint is at or
    after 2021-01-01T00:00:00Z, which the later endpoint's (UTC) year decides.  A numeric or
    missing endpoint is not a date and contributes nothing (the cell is refused by position
    upstream); the cell text is never quoted.  a Period's year is
    read from its daily frequency inside a try, because ``start_time``/``end_time`` raise
    ``OutOfBoundsDatetime`` (and quote the sealed instant) beyond pandas 2's nanosecond range.
    """
    if isinstance(deger, pd.Period):
        try:
            return max(deger.asfreq("D", how="start").year, deger.asfreq("D", how="end").year)
        except (ValueError, TypeError, OverflowError):
            return None
    uclar = [deger.left, deger.right]
    yillar: List[int] = []
    for u in uclar:
        if u is None:
            continue
        try:
            if bool(pd.isna(u)):
                continue
        except (TypeError, ValueError):
            continue
        if not isinstance(u, (pd.Timestamp, _dt.datetime, _dt.date, np.datetime64)):
            # a numeric or otherwise non-date endpoint: not sealed, refused by position upstream
            continue
        try:
            with _ZAMAN_KILIDI:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    t = pd.Timestamp(u)
        except (ValueError, TypeError, OverflowError):
            continue
        if t.tzinfo is not None:
            t = t.tz_convert("UTC")
        yillar.append(int(t.year))
    return max(yillar) if yillar else None


def _yil_onek(deger) -> Optional[int]:
    r"""The leading four digits of a raw date/time cell as a year, or ``None``.

    a cell that does not parse but starts with a sealed year counts as
    sealed, and the cell's text never enters a message.  The rule is narrow: optional leading whitespace, then four digits, anchored
    (``re.match(r"\s*(\d{4})")``); a bytes cell is decoded as UTF-8 and read by the same rule; a
    numeric cell is excluded (refused by position upstream); a Period or Interval cell is read by
    its endpoints (the later one's year, so a straddling period counts); every other value counts
    as nothing.  A date-typed cell (``datetime.date``/
    ``datetime.datetime``, ``np.datetime64`` or ``pd.Timestamp``) has its UTC year read directly,
    naive as UTC.  ``bytearray``/``memoryview`` are treated as bytes.  A leading whitespace or Unicode
    format character (category ``Cf``) is stripped in a loop before the text rule, and UTF-16 bytes
    carrying a BOM are decoded as such; both choices seal more, never less.
    ``knotenlinie.kanal.tektonik_kaynak._yil_onek`` is the same rule; one literal case list in
    ``tests/etas/test_katalog.py`` pins both copies.
    """
    if isinstance(deger, (pd.Period, pd.Interval)):
        return _uc_yili(deger)
    if isinstance(deger, (pd.Timestamp, _dt.datetime, _dt.date, np.datetime64)):
        try:
            if isinstance(deger, np.datetime64):
                if np.isnat(deger):
                    return None
                return int(np.datetime_as_string(deger, unit="Y"))
            if isinstance(deger, (pd.Timestamp, _dt.datetime)) and deger.tzinfo is not None:
                try:
                    deger = deger.astimezone(_dt.timezone.utc)
                except (ValueError, OverflowError):
                    pass
            return int(deger.year)
        except (ValueError, TypeError, OverflowError):
            return None
    if isinstance(deger, (bytes, bytearray, memoryview)):
        try:
            ham_bayt = bytes(deger)
            if ham_bayt.startswith(b"\xff\xfe") or ham_bayt.startswith(b"\xfe\xff"):
                deger = ham_bayt.decode("utf-16")
            else:
                deger = ham_bayt.decode("utf-8")
        except (UnicodeDecodeError, TypeError, ValueError):
            return None
    if not isinstance(deger, str):
        return None
    deger = _onek_temizle(deger)
    m = re.match(r"(\d{4})", deger)
    return int(m.group(1)) if m else None


def _hucre_sayi(deger):
    """A CPTI15 date/time cell as an int, or ``None`` when it is empty.

    A non-empty cell that is not a finite number raises ``ValueError``/``OverflowError``; the
    caller turns that into a ``BicimHatasi`` that names neither the cell nor the row id
.
    """
    if deger is None:
        return None
    s = str(deger).strip()
    if s == "" or s.lower() in ("nan", "none"):
        return None
    return int(float(s))


def yollari_coz(paths: Union[str, Sequence[str]], onek: str = "iside") -> Tuple[List[str], List[str], List[str]]:
    """Expand globs, split per-year catalogue paths (``<onek>_<year>``) into (to open, refused by year,
    unknown names)."""
    acilacak, acilmayan, adsiz = [], [], []
    for p in ([paths] if isinstance(paths, str) else list(paths)):
        for yol in sorted(_glob.glob(p)) if any(ch in p for ch in "*?[") else [p]:
            ad = os.path.basename(yol)
            m = re.search(rf"{onek}_(\d{{4}})", ad)
            if not m:
                adsiz.append(yol)
                continue
            if int(m.group(1)) >= ACILMAYAN_YIL:
                acilmayan.append(yol)
            else:
                acilacak.append(yol)
    return acilacak, acilmayan, adsiz


def _cerceve(satirlar: List[dict], birim: str = None) -> pd.DataFrame:
    """The common table.  ``birim="us"`` stores ``time_utc`` as ``datetime64[us, UTC]``.

    CPTI15 starts in 1349, before the nanosecond range (1677–2262) that pandas 2 uses by
    default; microseconds hold it under pandas 2 and are pandas 3's default.  The other
    catalogues keep the default path.
    """
    if not satirlar:
        df = pd.DataFrame({c: pd.Series(dtype="object") for c in _TABLO_KOLONLARI})
        df["time_utc"] = pd.Series(dtype=f"datetime64[{birim or 'ns'}, UTC]")
        return df[list(_TABLO_KOLONLARI)]
    df = pd.DataFrame(satirlar)
    if birim == "us":
        # through numpy so no step converts to nanoseconds; the time of day is kept
        with _ZAMAN_KILIDI:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                yerel = [pd.Timestamp(t).tz_convert("UTC").to_pydatetime().replace(tzinfo=None)
                         for t in df["time_utc"]]
        df["time_utc"] = pd.Series(np.array(yerel, dtype="datetime64[us]"),
                                   index=df.index).dt.tz_localize("UTC")
    else:
        with _ZAMAN_KILIDI:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    # a magnitude cell is numeric or empty; an empty cell becomes NaN and is handled upstream as a
    # missing parameter, but a non-empty cell that does not parse is a defect and raises by name
    # (row id and value).  This is the point where the CSV/frame paths would otherwise coerce it to
    # NaN and let it slip into the magnitude split.
    ham = df["mag"]
    sayi = pd.to_numeric(ham, errors="coerce")
    bos = ham.isna() | (ham.astype(str).str.strip() == "")
    # Only finite magnitudes pass; ``inf``/``-inf``/``Infinity`` are
    # defects like any unparseable non-empty cell (an empty cell stays a missing parameter).
    kotu = ~bos & ~np.isfinite(sayi)
    if bool(kotu.any()):
        adlar = (df["event_id"].astype(str) if "event_id" in df.columns
                 else df.index.astype(str))
        ornek = [(str(adlar.loc[i]), str(ham.loc[i])) for i in df.index[kotu]][:5]
        raise BicimHatasi(f"magnitude is not a number (event_id, value): {ornek}")
    df["mag"] = sayi.astype("float64")
    for c in ("lat", "lon", "depth_km"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")
    for c in ("mag_type", "source", "event_id", "catalog_file"):
        df[c] = df[c].astype("string")
    return df[list(_TABLO_KOLONLARI)]


# --- ISIDe -----------------------------------------------------------------

@_kilitli
def iside_oku(paths: Union[str, Sequence[str]]) -> Tuple[pd.DataFrame, dict]:
    """Read ISIDe FDSN text files with the file-year, seal and cutoff gates.

    Returns ``(table, report)``.  ``report['acilmayan']`` lists files the
    file-year gate refused to open; ``report['atilan_kesim']`` counts the rows
    dropped by the cutoff; ``report['atilan_muhur']`` is always 0 because a
    sealed row raises instead of being counted.  
    a ``str`` ``Time`` cell parsed before 1000-01-01 UTC (pandas' default year 1
    for a year-less cell, a three-digit or zero-padded year) is ``NaT`` before the
    leading-year rule, so a sealed one is counted and every other one is refused by
    position (never returned) on pandas 3 as well.
    """
    acilacak, acilmayan, adsiz = yollari_coz(paths)
    if adsiz:
        raise BicimHatasi(f"ISIDe file name carries no year: {adsiz}")
    satirlar: List[dict] = []
    okunan = 0
    for yol in acilacak:
        with open(yol, "r", encoding="utf-8", errors="replace") as f:
            ilk = f.readline().rstrip("\n")
        if not ilk.lstrip("#") == ISIDE_HEADER.lstrip("#"):
            # a headerless file must not quote its first row; name
            # only the file and the header the adapter requires.
            raise BicimHatasi(
                f"{os.path.basename(yol)}: the first line is not the ISIDe header; "
                "the exact declared column names are required, refusing to read")
        df = pd.read_csv(yol, sep="|", dtype=str, keep_default_na=False, comment=None)
        cid = _kolon(df, ["EventID"], yol)
        ctime = _kolon(df, ["Time"], yol)
        clat = _kolon(df, ["Latitude"], yol)
        clon = _kolon(df, ["Longitude"], yol)
        cdepth = _kolon(df, ["Depth/Km", "Depth"], yol, zorunlu=False)
        ctype = _kolon(df, ["MagType"], yol, zorunlu=False)
        cmag = _kolon(df, ["Magnitude"], yol)
        okunan += len(df)
        # a string date cell with no four-digit year (``21/01/01``)
        # is refused by position before any parse; the cell text never enters the message.
        iki_hane = _iki_hane_yil_maskesi(df[ctime])
        if bool(iki_hane.any()):
            # Seal first, counted.  A flagged cell whose leading-year
            # prefix is at or after the seal is counted before a text date cell with no four-digit
            # year is refused.
            muhur_ek = np.array(
                [_metin_muhur_sayilir(v, bool(i))
                 for v, i in zip(df[ctime].to_numpy(), iki_hane)], dtype=bool)
            if bool(muhur_ek.any()):
                raise MuhurIhlali(
                    f"{os.path.basename(yol)}: {int(muhur_ek.sum())} record(s) at or after "
                    f"{MUHUR.isoformat()} — seal, refusing to read")
            raise BicimHatasi(
                f"{os.path.basename(yol)}: {int(iki_hane.sum())} record(s) with a text date cell "
                f"carrying no four-digit year (rows {np.flatnonzero(iki_hane)[:5].tolist()}) "
                "(year-floor rule)")
        # Parse with ``errors="coerce"`` so a cell that does not parse
        # never enters a message; a cell whose leading four digits are a sealed year is counted as
        # sealed (count only); every other unparsed or missing Time is a format error naming
        # positions only.  The seal is checked before any other cell of the row.  A cell whose parse reported an unrecognised
        # timezone or the "as tzlocal" branch is ``NaT`` and goes through the leading-year rule
        # (a sealed leading year is counted, an earlier one is refused by position; never read as a
        # wall time).
        try:
            zaman, taninmadi = _zaman_sutunu_canli(df[ctime])
        except (ValueError, TypeError, OverflowError, AttributeError):
            raise BicimHatasi(
                f"{os.path.basename(yol)}: {len(df)} record(s) with an unparseable Time") from None
        # The text-cell year floor (pandas 3 parses these cells;
        # a sealed one is then counted before the leading-year rule and the NaT refusal).
        zaman = _taban_alti_nat(df[ctime].to_numpy(), zaman)
        nat = zaman.isna()
        ham = df[ctime].to_numpy()
        muhur_ek = np.array(
            [(lambda y: y is not None and y >= MUHUR.year)(_yil_onek(ham[k]))
             for k in range(len(df))], dtype=bool) if len(df) else np.zeros(0, dtype=bool)
        # seal gate before the cutoff, on the parsed times (independent of muhur.py).  a NaT cell with an unrecognised timezone or the "as tzlocal"
        # branch is no longer excluded from the leading-year count (the pre-fix `& ~taninmadi` is
        # dropped), so a 2021 CET cell is counted and an earlier one is refused by position.
        kotu = ((zaman >= MUHUR).to_numpy() | (muhur_ek & nat.to_numpy())
                | _yanlis_okunan_muhur(ham, list(zaman)))   # a misread sealed year
        if bool(kotu.any()):
            raise MuhurIhlali(
                f"{os.path.basename(yol)}: {int(kotu.sum())} record(s) at or after "
                f"{MUHUR.isoformat()} — seal, refusing to read")
        if bool(nat.any()):
            raise BicimHatasi(
                f"{os.path.basename(yol)}: {int(nat.sum())} record(s) with no parseable Time "
                f"(rows {np.flatnonzero(nat.to_numpy())[:5].tolist()})")
        for i in range(len(df)):
            satirlar.append({
                "time_utc": zaman.iat[i], "lat": df[clat].iat[i], "lon": df[clon].iat[i],
                "depth_km": df[cdepth].iat[i] if cdepth else np.nan,
                "mag": df[cmag].iat[i], "mag_type": df[ctype].iat[i] if ctype else "ML",
                "source": "iside", "event_id": str(df[cid].iat[i]), "catalog_file": os.path.basename(yol)})
    df = _cerceve(satirlar)
    # cutoff gate inside the reader
    if len(df):
        kesilecek = df["time_utc"] > KESIM
        atilan = int(kesilecek.sum())
        df = df.loc[~kesilecek].reset_index(drop=True)
    else:
        atilan = 0
    if len(df):
        assert df["time_utc"].max() <= KESIM, "cutoff gate leaked a row past 2015"
    report = {"kaynak": "iside", "okunan": okunan, "tutulan": int(len(df)),
              "atilan_kesim": atilan, "atilan_muhur": 0,
              "acilan": [os.path.basename(p) for p in acilacak],
              "acilmayan": [os.path.basename(p) for p in acilmayan], "kesim": KESIM_ISO}
    return df, report


# --- HORUS -------------------------------------------------------------------

HORUS_KOLONLARI = ("Year", "Mo", "Da", "Ho", "Mi", "Se", "Lat", "Lon", "Depth", "Mw", "sigMw",
                   "Geo-Ita", "Geo-CPTI15", "Ev. type", "Iside n.")


@_kilitli
def horus_oku(paths: Union[str, Sequence[str]]) -> Tuple[pd.DataFrame, dict]:
    """Read HORUS per-year files (``horus_<year>.txt``, scripts/indir.py) with the ISIDe gates.

    HORUS (Lolli et al. 2020, 10.1785/0220200148) gives every event one
    homogenized Mw, so ``mag_type`` is ``Mw`` throughout. The file-year gate leaves 2016 and later
    unopened, a parsed time on or after 2021-01-01 raises, rows after the 2015 cutoff are dropped and
    counted, and events HORUS marks as not earthquakes (``Ev. type`` = x) are dropped and counted.
    """
    acilacak, acilmayan, adsiz = yollari_coz(paths, "horus")
    if adsiz:
        raise BicimHatasi(f"HORUS file name carries no year: {adsiz}")
    parcalar, okunan, deprem_disi = [], 0, 0
    for yol in acilacak:
        df = pd.read_csv(yol, sep="\t", dtype=str, keep_default_na=False)
        df.columns = [str(c).strip() for c in df.columns]
        eksik = [c for c in HORUS_KOLONLARI if c not in df.columns]
        if eksik:
            raise BicimHatasi(f"{os.path.basename(yol)}: HORUS columns missing {eksik}")
        okunan += len(df)
        sayi = {c: pd.to_numeric(df[c].str.strip(), errors="coerce") for c in HORUS_KOLONLARI[:11]}
        # The seal is checked first, on the year
        # alone.  A row in a sealed calendar year (>= 2021) never has any other cell read, so a
        # malformed hour or a malformed magnitude cannot name its cell (or the sealed id).  A
        # non-numeric year whose leading four digits are a sealed year seals too, as in CPTI15.
        ham_yil = df["Year"].str.strip()
        muhurlu_yil = (sayi["Year"] >= MUHUR.year).to_numpy().copy()
        y_na = sayi["Year"].isna().to_numpy()
        if y_na.any():  # only an unparsed year can carry a sealed leading year (as in CPTI15)
            for k in np.flatnonzero(y_na):
                yil = _yil_onek(ham_yil.iat[k])
                if yil is not None and yil >= MUHUR.year:
                    muhurlu_yil[k] = True
        if bool(muhurlu_yil.any()):
            raise MuhurIhlali(
                f"{os.path.basename(yol)}: {int(muhurlu_yil.sum())} record(s) at or after "
                f"{MUHUR.isoformat()} — seal, refusing to read")
        # a year of fewer than four digits ("21") cannot be placed
        # against the seal; such a row is refused by position, never read as a first-century year.
        # The refusal waits for the seal count below.
        # the floor rows are excluded from the calendar
        # and time parse, the parsed-time (Ho = 24) seal count runs first, and only then is the
        # floor reported -- the floor used to hide a sealed row's parsed time.
        eksik_yil = (sayi["Year"] < 1000).to_numpy() & ~y_na
        gecerli = ~eksik_yil
        takvim = pd.DataFrame({"year": sayi["Year"], "month": sayi["Mo"], "day": sayi["Da"]})
        eksik_takvim = ((takvim.isna().any(axis=1)
                         | (takvim["month"] < 1) | (takvim["day"] < 1)).to_numpy() & gecerli)
        if bool(eksik_takvim.any()):
            raise BicimHatasi(
                f"{os.path.basename(yol)}: a HORUS row has no full calendar date "
                f"(rows {np.flatnonzero(eksik_takvim)[:5].tolist()})")
        # a non-numeric hour/minute/second is refused, never read as 0
        # (the old ``fillna(0)`` silently moved the event to midnight).
        for c in ("Ho", "Mi", "Se"):
            eksik_saat = sayi[c].isna().to_numpy() & gecerli
            if bool(eksik_saat.any()):
                raise BicimHatasi(
                    f"{os.path.basename(yol)}: a HORUS row has a non-numeric {c} "
                    f"(rows {np.flatnonzero(eksik_saat)[:5].tolist()})")
        try:
            with _ZAMAN_KILIDI:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    zaman = (pd.to_datetime(takvim[gecerli].astype(int), utc=True)
                             + pd.to_timedelta((sayi["Ho"] * 3600 + sayi["Mi"] * 60
                                                + sayi["Se"])[gecerli], unit="s"))
        except (ValueError, TypeError, OverflowError):
            # ``OverflowError`` joins the caught
            # exceptions and the traceback is suppressed so no cell text rides the chain; only real
            # row positions enter the message.  The floor rows are
            # not parsed, so only their positions can appear here.
            kotu_zaman = []
            for k in np.flatnonzero(gecerli):
                try:
                    with _ZAMAN_KILIDI:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            (pd.to_datetime(takvim.iloc[[k]].astype(int), utc=True)
                             + pd.to_timedelta(sayi["Ho"].iloc[[k]] * 3600 + sayi["Mi"].iloc[[k]] * 60
                                               + sayi["Se"].iloc[[k]], unit="s"))
                except (ValueError, TypeError, OverflowError):
                    kotu_zaman.append(int(k))
                    if len(kotu_zaman) >= 5:
                        break
            raise BicimHatasi(
                f"{os.path.basename(yol)}: a HORUS row has an unparseable time "
                f"(rows {kotu_zaman})") from None
        kotu = zaman >= MUHUR
        if bool(kotu.any()):
            raise MuhurIhlali(
                f"{os.path.basename(yol)}: {int(kotu.sum())} record(s) at or after "
                f"{MUHUR.isoformat()} — seal, refusing to read")
        if bool(eksik_yil.any()):
            raise BicimHatasi(
                f"{os.path.basename(yol)}: a HORUS row has a year of fewer than four digits "
                f"(rows {np.flatnonzero(eksik_yil)[:5].tolist()})")
        deprem = df["Ev. type"].str.strip().str.lower() != "x"
        deprem_disi += int((~deprem).sum())
        iside = df["Iside n."].str.strip()
        parcalar.append(pd.DataFrame({
            "time_utc": zaman[deprem].to_numpy(), "lat": sayi["Lat"][deprem].to_numpy(float),
            "lon": sayi["Lon"][deprem].to_numpy(float), "depth_km": sayi["Depth"][deprem].to_numpy(float),
            # HORUS magnitudes are strict now (the compute-server count of
            # non-numeric Mw cells was 0): the raw cell reaches the shared frame, which raises by
            # name for a non-empty non-numeric or non-finite value, exactly as ISIDe does.
            "mag": df["Mw"].str.strip().to_numpy()[deprem.to_numpy()],
            "mag_type": "Mw", "source": "horus",
            "event_id": [i if i else f"horus-{os.path.basename(yol)}-{k}"
                         for k, i in zip(np.flatnonzero(deprem.to_numpy()), iside[deprem])],
            "catalog_file": os.path.basename(yol)}))
    df = _cerceve(pd.concat(parcalar, ignore_index=True).to_dict("records")) if parcalar else _cerceve([])
    # microseconds, like the compute server's ISIDe/CPTI15 tables: a nanosecond column cannot join CPTI15's year 1005
    df["time_utc"] = df["time_utc"].dt.as_unit("us")
    kesilecek = df["time_utc"] > KESIM if len(df) else pd.Series(dtype=bool)
    atilan = int(kesilecek.sum()) if len(df) else 0
    if atilan:
        df = df.loc[~kesilecek].reset_index(drop=True)
    if len(df):
        assert df["time_utc"].max() <= KESIM, "cutoff gate leaked a row past 2015"
    report = {"kaynak": "horus", "okunan": okunan, "tutulan": int(len(df)), "atilan_kesim": atilan,
              "atilan_muhur": 0, "atilan_deprem_disi": deprem_disi,
              "acilan": [os.path.basename(p) for p in acilacak],
              "acilmayan": [os.path.basename(p) for p in acilmayan], "kesim": KESIM_ISO}
    return df, report


# --- CPTI15 ------------------------------------------------------------------

_CPTI_TAKVIM = (["Year"], ["Mo", "Month"], ["Dy", "Da", "Day"])


def gun(zaman: pd.Series) -> np.ndarray:
    """UTC times as float days since 1970-01-01, independent of the datetime resolution.

    pandas 2 stores these columns in nanoseconds and pandas 3 (compute server) in microseconds, so an
    ``astype("int64")`` conversion is off by 1000 on one of them.
    """
    return ((zaman - pd.Timestamp("1970-01-01", tz="UTC")) / pd.Timedelta(days=1)).to_numpy(float)


def julyen_gregoryen(y: int, mo: int, d: int) -> _dt.date:
    """A Julian-calendar date as a proleptic Gregorian date (via the Julian day number).

    CPTI15 gives pre-reform dates as the historical sources do, in the Julian calendar (its only date
    invalid in the Gregorian calendar is 1400-02-29, a Julian leap day). pandas times are proleptic
    Gregorian, so dates before 1582-10-15 are converted: 8 to 10 days in 1349-1582.
    """
    a = (14 - mo) // 12
    yy, mm = y + 4800 - a, mo + 12 * a - 3
    jdn = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4 - 32083
    return _dt.date.fromordinal(jdn - 1721425)


@_kilitli
def cpti15_oku(path: str) -> Tuple[pd.DataFrame, dict]:
    """Read a CPTI15 ``catalogue`` CSV written by ``scripts/indir.py``.

    The exact column names are not fixed by the provider: the adapter resolves a
    declared candidate list and raises :class:`BicimHatasi` naming only the file and the missing
    candidate columns when none matches; it never prints the header
    it saw.  It never reads positionally.
    """
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    cy = _kolon(df, _CPTI_TAKVIM[0], path)
    cmo = _kolon(df, _CPTI_TAKVIM[1], path)
    cd = _kolon(df, _CPTI_TAKVIM[2], path)
    clat = _kolon(df, ["Lat", "Latitude", "LatDef"], path)
    clon = _kolon(df, ["Lon", "Longitude", "LonDef"], path)
    cmag = _kolon(df, ["Mw", "MwDef", "Magnitude", "MW"], path)
    cdepth = _kolon(df, ["Depth", "Depth/Km", "DepDef"], path, zorunlu=False)
    cid = _kolon(df, ["CPTI15_ID", "ID", "EventID"], path, zorunlu=False)
    ch = _kolon(df, ["Hour", "Ho"], path, zorunlu=False)
    cmin = _kolon(df, ["Min", "Mi"], path, zorunlu=False)
    csec = _kolon(df, ["Sec", "Se"], path, zorunlu=False)
    satirlar: List[dict] = []
    okunan = len(df)
    muhurlu_yil = 0
    # Rows whose year has fewer than four digits are collected and
    # refused by position after the seal count, so a sealed row elsewhere in the file is still
    # counted and reported first (HORUS checks the seal before its floor too).
    kisa_yil: List[int] = []
    # Rows whose year or date does not parse are collected too
    # instead of raising inside the loop, so a sealed row elsewhere in the file is still counted and
    # reported first; the refusal names the first row and at most five positions, never a cell.
    bozuk: List[int] = []
    bozuk_sebep: dict = {}
    for i in range(len(df)):
        # seal safety, catalogue date parse: parse
        # the year first; a year at or after the seal year is sealed **before** the rest of the row
        # is read, so a malformed hour/minute/second in a sealed row cannot name its cell or the
        # sealed id.  A non-numeric year whose leading four digits are a sealed year is sealed too;
        # any other non-numeric or missing year is a format error with the row position only.
        ham_y = df[cy].iat[i]
        try:
            y = _hucre_sayi(ham_y)
        except (ValueError, TypeError, OverflowError):
            yil = _yil_onek(ham_y)
            if yil is not None and yil >= MUHUR.year:
                muhurlu_yil += 1
                continue
            bozuk.append(i)
            bozuk_sebep[i] = "year not parseable"
            continue
        if y is None:
            bozuk.append(i)
            bozuk_sebep[i] = "year missing"
            continue
        if y < 1000:
            # a year of fewer than four digits ("21") cannot be placed
            # against the seal; CPTI15 starts in 1005, so such a row is refused by position.  Only
            # the row number enters the message.  The refusal waits
            # for the seal count below, so a sealed row in the same file is still counted first.
            kisa_yil.append(i)
            continue
        if y >= MUHUR.year:
            muhurlu_yil += 1
            continue
        try:
            mo = _hucre_sayi(df[cmo].iat[i])
            d = _hucre_sayi(df[cd].iat[i])
            hh = _hucre_sayi(df[ch].iat[i]) if ch else None
            mi = _hucre_sayi(df[cmin].iat[i]) if cmin else None
            ss = _hucre_sayi(df[csec].iat[i]) if csec else None
            mo, d = 1 if mo is None else max(1, mo), 1 if d is None else max(1, d)
            hh = 0 if hh is None else hh
            mi = 0 if mi is None else mi
            ss = 0 if ss is None else ss
            gun_ = julyen_gregoryen(y, mo, d) if (y, mo, d) < (1582, 10, 5) else _dt.date(y, mo, d)
            # Time of day as a duration, so CPTI15's one "Ho = 24" (end of the day) becomes the next 00:00.
            zaman = pd.Timestamp(_dt.datetime(gun_.year, gun_.month, gun_.day, tzinfo=_dt.timezone.utc)
                                 + _dt.timedelta(hours=hh, minutes=mi, seconds=ss))
        except (ValueError, TypeError, OverflowError):
            # nothing from the row enters the message: not the id, not the cell, not the value
            bozuk.append(i)
            bozuk_sebep[i] = "date not parseable"
            continue
        satirlar.append({
            "time_utc": zaman, "lat": df[clat].iat[i], "lon": df[clon].iat[i],
            "depth_km": df[cdepth].iat[i] if cdepth else np.nan,
            "mag": df[cmag].iat[i], "mag_type": "Mw", "source": "cpti15",
            "event_id": str(df[cid].iat[i]) if cid else f"cpti15-{i}", "catalog_file": os.path.basename(path)})
    # The seal is checked on the parsed times
    # before the shared frame's magnitude check, so a sealed row with a malformed magnitude raises
    # MuhurIhlali with a count only; the sealed row's id and value never enter a message.  The year
    # gate above is not enough on its own: CPTI15's one "Ho = 24" carries 2020-12-31 into 2021.
    muhurlu = muhurlu_yil + sum(1 for s in satirlar if s["time_utc"] >= MUHUR)
    if muhurlu:
        raise MuhurIhlali(
            f"{os.path.basename(path)}: {muhurlu} record(s) at or after {MUHUR.isoformat()}")
    if kisa_yil:
        # Only after the seal count; only the first row and a short
        # list of positions enter the message, never a cell's text.
        raise BicimHatasi(f"{os.path.basename(path)}: row {kisa_yil[0]}: year has fewer than four "
                          f"digits (rows {kisa_yil[:5]})")
    if bozuk:
        # The first row with its reason and at most five positions,
        # after the seal count above, never a cell's text.
        raise BicimHatasi(
            f"{os.path.basename(path)}: row {bozuk[0]}: {bozuk_sebep[bozuk[0]]} "
            f"(rows {bozuk[:5]})")
    df = _cerceve(satirlar, birim="us")
    if len(df):
        atilan = int((df["time_utc"] > KESIM).sum())
        df = df.loc[df["time_utc"] <= KESIM].reset_index(drop=True)
    else:
        atilan = 0
    report = {"kaynak": "cpti15", "okunan": okunan, "tutulan": int(len(df)),
              "atilan_kesim": atilan, "atilan_muhur": 0, "acilan": [os.path.basename(path)],
              "acilmayan": [], "kesim": KESIM_ISO}
    return df, report


# --- gates as assertions -----------------------------------------------------

def kesim_temiz_mi(df: pd.DataFrame) -> bool:
    """Defence in depth: no row past the 2015 cutoff."""
    if len(df):
        kotu = df["time_utc"] > KESIM
        assert not bool(kotu.any()), f"cutoff leak: {int(kotu.sum())} row(s) past {KESIM_ISO}"
    return True


def muhur_temiz_mi(df: pd.DataFrame) -> bool:
    """Defence in depth: no row on or after 2021-01-01."""
    if len(df):
        kotu = df["time_utc"] >= MUHUR
        assert not bool(kotu.any()), f"seal leak: {int(kotu.sum())} row(s) at or after 2021-01-01"
    return True


def giris_kapilari(df: pd.DataFrame) -> pd.DataFrame:
    """Both gates as one call; every computing entry point uses this."""
    kesim_temiz_mi(df)
    muhur_temiz_mi(df)
    return df


# --- regions and counts ------------------------------------------------------

def bolge_sec(df: pd.DataFrame, bolge: Union[str, Tuple[float, float, float, float]]) -> pd.DataFrame:
    """Filter to a declared region box. Returns a copy with a fresh index."""
    b = BOLGELER[bolge] if isinstance(bolge, str) else tuple(bolge)
    la0, la1, lo0, lo1 = b
    m = (df["lat"] >= la0) & (df["lat"] <= la1) & (df["lon"] >= lo0) & (df["lon"] <= lo1)
    return df.loc[m].reset_index(drop=True)


def sayim(df: pd.DataFrame, bolge: Optional[str] = None, mag_esik: float = 0.0) -> int:
    d = bolge_sec(df, bolge) if bolge else df
    return int((d["mag"] >= mag_esik).sum())


def mag_turu_sayimi(df: pd.DataFrame, bolge: Optional[str] = None) -> dict:
    """Counts and shares per ``mag_type`` (never silently normalised)."""
    d = bolge_sec(df, bolge) if bolge else df
    n = len(d)
    if n == 0:
        return {"toplam": 0, "sayi": {}, "pay": {}}
    sayi = {str(k): int(v) for k, v in d["mag_type"].value_counts().items()}
    return {"toplam": n, "sayi": sayi, "pay": {k: v / n for k, v in sayi.items()}}


def tek_tur_sec(df: pd.DataFrame, bolge: Optional[str] = None, esik: float = 0.95) -> str:
    """Choose one ``mag_type`` by the pre-declared rule.

    Most common type if its share >= ``esik``; otherwise ``ML`` if present;
    otherwise raise.  Mixing ML/Mw/Md in the productivity term biases alpha and
    K; no magnitude-conversion relation is used in v0.
    """
    c = mag_turu_sayimi(df, bolge)
    if c["toplam"] == 0:
        raise BicimHatasi("mag_turu_sec: empty catalog")
    en_sik = max(c["sayi"], key=lambda k: c["sayi"][k])
    if c["pay"][en_sik] >= esik:
        return en_sik
    if "ML" in c["sayi"]:
        return "ML"
    raise BicimHatasi(
        f"no mag_type reaches the declared rule ({esik}); counts={c['sayi']} — this needs a review")


# --- magnitude of completeness input: the b value ----------------------------


def tur_donemi_baslangic(df: pd.DataFrame, tur: str) -> pd.Timestamp:
    """First 1 January from which ``tur`` is the majority magnitude type in every year to the end.

    ISIDe reports Md before 2005 and ML after it in the central Apennines: an ML-only catalogue over
    the whole span is nearly empty for fifteen years, and the fit read that as a near-zero background
    (compute server, 2026-09-29). With no magnitude conversion in v0, the catalogue a model sees is the
    years in which its one type is the majority, every year, through the end of the data.
    """
    if df.empty:
        raise BicimHatasi("tur_donemi_baslangic: empty catalog")
    yil = df["time_utc"].dt.year
    sayim = df.assign(_yil=yil).groupby(["_yil", "mag_type"]).size().unstack(fill_value=0)
    if tur not in sayim.columns:
        raise BicimHatasi(f"tur_donemi_baslangic: no {tur!r} events")
    cogunluk = sayim[tur] * 2 > sayim.sum(axis=1)
    yillar = list(sayim.index)
    bas = None
    for y in reversed(yillar):
        if not bool(cogunluk.loc[y]):
            break
        bas = y
    if bas is None:
        raise BicimHatasi(f"tur_donemi_baslangic: {tur!r} is not the majority type in the last year")
    return pd.Timestamp(f"{int(bas)}-01-01", tz="UTC")


#: Magnitude bins with fewer events than this are not judged by the tail gate.
KUYRUK_N_MIN = 10
#: Width of the tail gate's magnitude bins.
KUYRUK_GENISLIK = 0.5


class TurKuyruguHatasi(BicimHatasi):
    """The one magnitude type is a minority in a magnitude bin: selecting it cuts the FMD's tail."""


def tur_kuyruk_paylari(df: pd.DataFrame, tur: str, m_alt: float, genislik: float = KUYRUK_GENISLIK,
                       n_min: int = KUYRUK_N_MIN) -> dict:
    """Share of ``tur`` among all typed events in each magnitude bin from ``m_alt`` up (counts only).

    ``df`` is the catalogue before the type filter (region and era already cut). Bins with fewer
    than ``n_min`` events are listed with ``pay`` None.
    """
    m = df["mag"].to_numpy(float)
    secili = df["mag_type"].to_numpy(object) == tur
    ust = float(np.nanmax(m)) if m.size else m_alt
    out = {}
    lo = float(m_alt)
    while lo <= ust:
        hi = lo + genislik
        kutu = (m >= lo - 1e-9) & (m < hi - 1e-9)
        n = int(kutu.sum())
        out[f"[{lo:.1f}, {hi:.1f})"] = {"n": n, "n_tur": int((kutu & secili).sum()),
                                        "pay": (float((kutu & secili).sum()) / n) if n >= n_min else None}
        lo = hi
    return out


def tur_kuyrugu_kapisi(df: pd.DataFrame, tur: str, m_alt: float, esik: float = 0.95) -> dict:
    """Stop when ``tur`` falls below ``esik`` (the declared share rule) in any judged bin at or above ``m_alt``.

    A single magnitude type is only a clean catalogue when it is the type of the large events
    too. ISIDe gives most larger events of 2005-2015 as Mw (central Apennines, compute server 2026-09-29: at
    M 3.5-4 40 ML against 63 Mw, at M >= 4 9 ML against 32 Mw); the ML-only catalogue then loses
    its tail, Aki's b climbs from 1.23 at M 2 to 1.98 at M 3.4, and the completeness estimate and
    the productivity term read a truncation as physics.
    """
    paylar = tur_kuyruk_paylari(df, tur, m_alt)
    kotu = {k: v for k, v in paylar.items() if v["pay"] is not None and v["pay"] < esik}
    if kotu:
        raise TurKuyruguHatasi(
            f"{tur!r} is below the {esik} share in magnitude bins {kotu}; a {tur}-only catalogue cuts "
            f"the frequency-magnitude tail. A magnitude-homogeneous catalogue is a maintainer decision.")
    return paylar


def b_degeri(mags: Iterable[float], mc: float, dm: float = 0.1,
             n_bootstrap: int = 1000, seed: int = 20260929) -> dict:
    """Aki–Utsu b with the binning correction, plus a seeded bootstrap interval.

    ``b = log10(e) / (mean(mag) - (mc - dm/2))``.  Classic estimator, no DOI, not
    verified in this work; the Mc method it is paired with is Wiemer & Wyss 2000
    (10.1785/0119990114).  ``b`` is estimated separately and stored as a fit
    input, never absorbed into alpha.
    """
    m = np.asarray([x for x in mags if x == x], dtype=float)
    m = m[m >= mc]
    if m.size < 10:
        raise BicimHatasi(f"b_degeri: only {m.size} events at or above Mc={mc}")
    b = float(np.log10(np.e) / (m.mean() - (mc - dm / 2.0)))
    rng = np.random.default_rng(seed)
    n = m.size
    bs = np.empty(n_bootstrap)
    for k in range(n_bootstrap):
        s = m[rng.integers(0, n, n)]
        bs[k] = np.log10(np.e) / (s.mean() - (mc - dm / 2.0))
    return {"deger": b, "aralik95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "yontem": "aki-utsu+dm/2", "n": int(n), "dm": dm, "mc": float(mc),
            "beta": b * float(np.log(10.0)), "n_bootstrap": n_bootstrap, "seed": seed}
