"""Source list, WC94 scaling and the declared constants of the serial chain.

Every number this module uses is declared **in code** here, before any run, and none of them is
fitted to earthquake data.  The loading scale is the constant-stress-drop elastic
scaling of Console, Murru, Falcone & Catalli 2008, Appendix A (DOI 10.1029/2007JB005418): the
per-fault stressing rate is ``tau_dot = C mu v_s / sqrt(W L)`` with ``C`` an order-of-magnitude
constant -- **never** strain rate times a stiffness.  The source dimensions
of an event that has no finite-fault slip model come from the Wells & Coppersmith 1994 all-types
area-from-magnitude regression (Table 2A, ``log(RA) = a + b*M``) and the Hanks & Kanamori 1979
moment-magnitude relation:

    log10(A_km2) = -3.49 + 0.91 Mw  (Wells & Coppersmith 1994, all types, Table 2A)
    M0 = 10**(1.5 Mw + 9.1) N m     (Hanks & Kanamori 1979)
    D  = M0 / (mu A)                (uniform-slip rectangle)

Two gates live inside the reader, not in a comment: a file whose **name** carries a year
>= 2016 is refused unopened, and a row on or after 2021-01-01 raises instead of being dropped
(the seal); rows past the 2015-12-31 cutoff are dropped and counted.
Nothing here reads a file on its own except through the catalog adapters of ``knotenlinie.etas`` or the
SRCMOD adapter, both of which apply the same gates.

Clean room: the equations are transcribed from the published papers named above; no code is copied
from a package with an unknown licence.
"""
from __future__ import annotations

import datetime as _dt
import decimal as _decimal
import fractions as _fractions
import warnings as _warnings
import glob as _glob
import hashlib
import json
import os
import re
import threading as _threading
import unicodedata as _unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

#: One lock for every suppressed time parse (re-entrant).  ``warnings.catch_warnings()`` swaps one process-wide filter
#: list, so two overlapping suppressed parses can drop each other's "ignore" and print a sealed
#: cell; the lock makes the swap serial.  The same object is imported by ``knotenlinie.etas.katalog`` so
#: both copies share one lock, and the readers take it around their whole bodies.  It is an
#: ``RLock`` because a locked reader calls other locked helpers (``_cerceve``, ``_yil_onek``) in
#: the same thread.  The guarantee holds for a gate run in one thread: pandas itself
#: (``pandas_dtype``, ``read_csv``) and a caller's own code can still swap the process-wide filter
#: list from another thread.
_ZAMAN_KILIDI = _threading.RLock()

#: The phrases pandas 2 uses when it does not resolve a timezone abbreviation to a UTC offset:
#: an unrecognised one (which it silently drops) and one it matches to the machine's own
#: ``time.tzname`` (the "as tzlocal" branch).  The warning text quotes the cell, so it is only
#: inspected for these phrases and never kept or shown (the tzlocal branch included).
_TANINMAYAN_DILIM_IFADELERI = (
    "un-recognized timezone", "unrecognized timezone", "un-recognised timezone",
    "unrecognised timezone", "as tzlocal",
)


def _taninmayan_zaman_dilimi(kayitlar) -> bool:
    """True when a recorded warning says a time string's timezone was not resolved to an offset.

    Pandas 2 reads an unrecognised abbreviation's wall time as UTC
    and only warns; pandas 3 refuses it.  The "as tzlocal" branch
    (an abbreviation in the machine's ``time.tzname``) is treated the same way.  The recorded
    message quotes the cell, so this reads the phrase only and never keeps or shows the text.
    """
    for kayit in kayitlar:
        metin = str(kayit.message).lower()
        if any(ifade in metin for ifade in _TANINMAYAN_DILIM_IFADELERI):
            return True
    return False

# --- declared constants (pre-registered; not fitted to earthquake data) ------------------

MU_PA = 30e9                     # lambda = mu = 30 GPa
MU_PRIME = (0.2, 0.4, 0.6)       # effective friction mu'; the reader's scan, not a fitted value
C_YUKLEME = 1.0                  # loading-scale order-of-magnitude constant, declared
KAYNAK_ESIK_MW = 5.0             # K9 source threshold, declared, NOT fitted
MESAFE_KESIMI_KM = 300.0         # K9 distance cutoff, declared, NOT fitted
KESIM = "2015-12-31T23:59:59.999999Z"
#: Wells & Coppersmith 1994 Table 2A, row ``log(RA) = a + b*M``, "All": a = -3.49 +- 0.16,
#: b = 0.91 +- 0.03, 148 events, s = 0.24, M 4.8-7.9.  This is the table's own area-from-
#: magnitude regression, not the inverse of its M-on-area row ``M = 4.07 + 0.98 log(RA)``
#: (the inverse drops the slope and is not a row of the table).
WC94_ALAN_EGIM, WC94_ALAN_KESISIM = 0.91, -3.49
#: The same table's "Normal" row (a = -2.87 +- 0.50, b = 0.82 +- 0.08, 22 events): a declared
#: sensitivity row only, never silently substituted for the all-types row above.
WC94_ALAN_N_EGIM, WC94_ALAN_N_KESISIM = 0.82, -2.87
EN_BOY_ORANI = 2.0               # L/W for Central Apennine normal faults, declared

MUHUR_BASI = "2021-01-01T00:00:00Z"      # first instant of the seal
MUHUR_YIL = 2021                         # the seal's calendar year; a raw year >= it is sealed
ACILMAYAN_YIL = 2016                     # a file name carrying this year or later is not opened

YIL_SANIYE = 365.25 * 24 * 3600.0
PI2_32 = np.pi ** 2 / 32.0

_KATALOG_SUTUNLARI = ("time_utc", "lat", "lon", "mag")
#: Every maximal four-digit run in a file name, bounded so an embedded five-digit run is not
#: split.  The year gate reads all of them, not only the first.
_YIL_DESENI = re.compile(r"(?<!\d)(\d{4})(?!\d)")

#: The basename the non-ISIDe catalogue branch may route to ``cpti15_oku``.  It is the
#: <=2015 split written by ``scripts/indir.py``; the full file is never kept on disk, so no other name -- not even a ``_``-suffixed variant -- is
#: accepted.  Exact match only.
CPTI15_ADLARI = ("CPTI15_v4.0_le2015.csv",)

#: Sidecars never live under ``deprem/``: the data root holds
#: ``yan-kayit/<kaynak>/<csv basename>.json``.  ``scripts/muhur.py`` stays strictly fail-closed,
#: so a ``<csv>.json`` beside the CSV would make the seal scan fail and is itself refused.
YAN_KAYIT_DIZINI = "yan-kayit"
CPTI15_KAYNAK = "cpti15"


class MuhurIhlali(RuntimeError):
    """A record on or after 2021-01-01 was seen; the seal forbids reading it (do not drop)."""


class KesimIhlali(ValueError):
    """An event past the 2015-12-31 cutoff was offered where only calibration events may enter."""


class VeriYok(RuntimeError):
    """A declared input product is not on this machine (SRCMOD, DISS); it is not fabricated."""


class KatalogYok(RuntimeError):
    """The catalog adapters of ``knotenlinie.etas`` are not importable on this machine."""


class BicimHatasi(ValueError):
    """A raw file does not carry the header the adapter declares."""


REPO_KOKU = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def muhur_bloku_uret(kok, *, python=None, zaman_asimi_s: float = 600.0) -> dict:
    """Run ``scripts/muhur.py`` on ``kok`` and return the seal block, or raise.

    The block is machine-produced: the attestation tool's own exit code decides, so a channel
    cannot publish an earthquake-fed ledger by describing a clean seal in a comment.
    """
    import datetime
    import subprocess
    import sys

    python = python or sys.executable
    arac = os.path.join(REPO_KOKU, "tools", "muhur.py")
    komut = [python, arac, os.fspath(kok)]
    sonuc = subprocess.run(komut, capture_output=True, text=True, timeout=zaman_asimi_s)
    if sonuc.returncode != 0:
        raise MuhurIhlali(
            f"scripts/muhur.py çıkış kodu {sonuc.returncode} ({kok}): "
            f"{sonuc.stdout.strip()[-300:]}"
        )
    return {
        "durum": "clean",
        "komut": " ".join(komut),
        "kok": os.fspath(kok),
        "tarih": datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds").replace("+00:00", "Z"),
    }


# --- time helpers -------------------------------------------------------------------------

def _an(x) -> pd.Timestamp:
    """One instant as a tz-aware UTC Timestamp; a naive input is refused.

    No cell text enters a message here.  ``pd.Timestamp``'s own
    ``DateParseError`` carries the string it was handed, so it is caught and re-raised with no
    value and ``from None``; a naive instant is refused without quoting it either.  A pandas warning that quotes the string (an unrecognised timezone
    abbreviation) is recorded and never shown.  That suppression
    shares ``_ZAMAN_KILIDI`` with every other suppressed parse.  The
    no-warning guarantee holds for a gate run in one thread; another thread's pandas work can still
    swap the process-wide filter list.  An unrecognised timezone abbreviation is
    refused (never read as a wall time), exactly as pandas 3 does.
    """
    try:
        with _ZAMAN_KILIDI:
            with _warnings.catch_warnings(record=True) as kayit:
                _warnings.simplefilter("always")
                t = pd.Timestamp(x)
    except (ValueError, TypeError, OverflowError, AttributeError):
        raise ValueError("zaman okunamadı; tz-aware UTC bir an gerekir") from None
    if _taninmayan_zaman_dilimi(kayit):
        raise ValueError("tanınmayan zaman dilimi; tz-aware UTC bir an gerekir") from None
    if t.tzinfo is None:
        raise ValueError("zaman dilimsiz; tz-aware UTC gerekir")
    return t.tz_convert("UTC")


def kesim_ani(kesim) -> pd.Timestamp:
    """A cutoff argument as a tz-aware UTC instant.

    A bare date (a command-line ``--kesim 2015-12-31``) means the last microsecond of that day,
    which is what the calibration cutoff keeps; a full timestamp is taken as written from UTC.
    """
    t = pd.Timestamp(kesim)
    if t.tzinfo is None:
        t = t.tz_localize("UTC")
        if len(str(kesim)) <= 10:
            t = t + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    return t.tz_convert("UTC")


def kesim_kapisi(kesim) -> None:
    """Refuse a cutoff later than the declared :data:`KESIM` by name.

    The calibration window cannot be widened: a later ``kesim`` is harmless only because
    ``katalog_oku`` already truncates to :data:`KESIM` first, and that makes the argument a lie.
    An earlier cutoff is allowed and recorded as narrower (see :func:`kaynak_listesi`).  ``None``
    keeps its existing ``kaynak_listesi`` meaning (no upper cutoff in a blind-window path).
    """
    if kesim is None:
        return
    if kesim_ani(kesim) > _an(KESIM):
        raise KesimIhlali(
            f"kesim={kesim!r} declared KESIM {KESIM} sonrasında; kalibrasyon kesimi "
            "genişletilemez"
        )


def dosya_yillari(ad: str) -> List[int]:
    """Every maximal four-digit run in 1000-2999 in the basename, in order.

    The reader's file-name gate works on this list, not on a first match, so
    ``iside_2015_2020.txt`` cannot hide its later year.
    """
    return [int(y) for y in _YIL_DESENI.findall(str(ad)) if 1000 <= int(y) <= 2999]


def dosya_yili(ad: str) -> Optional[int]:
    """The **largest** four-digit year (1000-2999) the file name declares, or None.

    Returning the largest keeps the old single-year callers unchanged while making a range
    name's later year visible; :func:`yil_kapisi` reads the full list through
    :func:`dosya_yillari`.
    """
    yillar = dosya_yillari(ad)
    return max(yillar) if yillar else None


def _cpti15_adi(ad: str) -> bool:
    """True when ``ad`` is exactly one of the declared CPTI15 basenames."""
    return str(ad) in CPTI15_ADLARI


def _sha256_dosya(yol) -> str:
    """Streamed sha256 of one file (the sidecar's binding digest)."""
    h = hashlib.sha256()
    with open(yol, "rb") as akis:
        for parca in iter(lambda: akis.read(1 << 20), b""):
            h.update(parca)
    return h.hexdigest()


def _cpti15_yan_kapisi(yol, yan_koku):
    """Refuse a CPTI15 split whose ``yan-kayit`` sidecar does not bind it; return the sidecar.

    ``scripts/indir.py`` writes the binding sidecar at
    ``<data>/yan-kayit/cpti15/<csv basename>.json``, **never** beside the CSV.  The
    CSV is not opened for rows until the sidecar is present and matches; a missing, malformed,
    wrong-kind, or wrong-cutoff sidecar is refused by name.  ``kesim_yili`` must
    be a real ``int`` (``2015.0`` and ``True`` are not accepted).
    """
    ad = os.path.basename(os.fspath(yol))
    eski = os.fspath(yol) + ".json"
    if os.path.isfile(eski):
        raise MuhurIhlali(
            f"{ad}: kardeş {os.path.basename(eski)} CSV'nin yanında; yan kayıtlar "
            f"<data>/{YAN_KAYIT_DIZINI}/{CPTI15_KAYNAK}/ altında olmalı ve mühür taramasını "
            "bozar; dosya açılmadı"
        )
    if yan_koku is None:
        raise MuhurIhlali(
            f"{ad}: yan-kayıt kökü (mühür kökü) verilmedi; dosya açılmadı")
    yan = os.path.join(os.fspath(yan_koku), YAN_KAYIT_DIZINI, CPTI15_KAYNAK, ad + ".json")
    if not os.path.isfile(yan):
        raise MuhurIhlali(
            f"{ad}: yan-kayıt {os.path.join(YAN_KAYIT_DIZINI, CPTI15_KAYNAK, ad + '.json')} "
            "yok; dosya açılmadı"
        )
    try:
        with open(yan, encoding="utf-8") as akis:
            kayit = json.load(akis)
    except (OSError, ValueError):
        raise MuhurIhlali(
            f"{ad}: yan-kayıt {os.path.basename(yan)} okunamadı; dosya açılmadı") from None
    if not isinstance(kayit, dict) or kayit.get("tur") != "knotenlinie-cpti15-bolme":
        raise MuhurIhlali(
            f"{ad}: yan-kayıt {os.path.basename(yan)} cpti15-bolme künyesi değil; dosya açılmadı")
    kesim_yili = kayit.get("kesim_yili")
    if type(kesim_yili) is not int or kesim_yili != 2015:
        raise MuhurIhlali(
            f"{ad}: yan-kayıt {os.path.basename(yan)} kesim_yili 2015 değil; dosya açılmadı")
    if kayit.get("cikti_sha256") != _sha256_dosya(os.fspath(yol)):
        raise MuhurIhlali(
            f"{ad}: yan-kayıt {os.path.basename(yan)} cikti_sha256 ile eşleşmiyor; dosya açılmadı")
    return kayit


def _cpti15_rapor_kapisi(ad: str, rapor: dict, yan: dict) -> None:
    """Refuse a split the reader had to cut or seal, or whose row count the sidecar miscounts.

    A checksum only proves the bytes, not that the bytes are the <=2015 window.
    ``cpti15_oku`` must report zero rows cut at :data:`KESIM` and zero sealed rows for the split,
    and its ``okunan`` row count must equal the sidecar's ``satir_le2015``.
    """
    kesim = int(rapor.get("atilan_kesim", 0) or 0)
    muhur = int(rapor.get("atilan_muhur", 0) or 0)
    if kesim or muhur:
        raise MuhurIhlali(
            f"{ad}: okuma {kesim + muhur} satırı kesti ya da mühürledi; <=2015 bölmesi temiz "
            "değil, dosya reddedildi"
        )
    okunan = rapor.get("okunan")
    beklenen = yan.get("satir_le2015")
    if okunan is not None and okunan != beklenen:
        raise MuhurIhlali(
            f"{ad}: okunan {okunan} satır, kardeş künye satir_le2015 {beklenen}; "
            "dosya reddedildi"
        )


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
                with _warnings.catch_warnings():
                    _warnings.simplefilter("ignore")
                    t = pd.Timestamp(u)
        except (ValueError, TypeError, OverflowError):
            continue
        if t.tzinfo is not None:
            t = t.tz_convert("UTC")
        yillar.append(int(t.year))
    return max(yillar) if yillar else None


#: The default-ignorable leading characters stripped by :func:`_onek_temizle` in addition to
#: whitespace and category ``Cf``.  Each entry is an inclusive
#: ``(first, last)`` code-point range.
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
    """
    i = 0
    n = len(metin)
    while i < n and _onemsenmez_karakter(metin[i]):
        i += 1
    return metin[i:]


def _yil_onek(deger) -> Optional[int]:
    r"""The leading four digits of a raw time cell as a year, or ``None``.

    Used to tell a sealed time that cannot be parsed (``2021-02-30T...``) from an ordinary
    defect, without ever quoting the cell.  The rule is narrow: optional leading whitespace, then
    four digits, anchored (``re.match(r"\s*(\d{4})")``), so ``zq9-2222``, ``ID-2500`` and ``-2021``
    stay defects; a bytes cell is decoded as UTF-8 and read by the same rule (one that does not
    decode counts as nothing); a numeric cell (int, float, Decimal, a numpy number, negatives
    included) is excluded here and refused by position; a Period or Interval cell is read by its
    endpoints (the later one's year, so a straddling period counts); every other value (complex,
    list, tuple, dict, ...) counts as nothing.  A date-typed cell (``datetime.date``/
    ``datetime.datetime``, ``np.datetime64`` or ``pd.Timestamp``) has its UTC year read directly,
    naive as UTC.  ``bytearray``/``memoryview`` are treated as bytes.  Leading whitespace,
    Unicode format characters (category ``Cf``) and the named default-ignorable ranges are
    stripped in one linear scan before the text rule, and UTF-16 bytes carrying a BOM are decoded
    as such; both choices seal more, never less.
    ``knotenlinie.etas.katalog._yil_onek`` is the same rule; one literal case list in
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


#: A time of day, with an optional fraction and an attached zone offset.  Removed before the four-digit test, so a four-digit fraction (``.000000``) or offset
#: (``+0100``) can no longer stand in for a year.
_SAAT_DESENI = re.compile(
    r"(?<!\d)\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d+)?(?:\s*(?:Z|[+-]\d{2}(?::?\d{2})?))?")
#: Any digit run; its length decides the date shape.
_RAKAM_KOSUSU = re.compile(r"\d+")
#: A three-part short date (``21/01/01``, ``1.1.21``; separators ``/ - .``), not adjacent to another
#: digit.  With no four-digit run before it, it is a two-digit-year
#: date even when a four-digit run (the colon-less ``HHMM`` time, ``21/01/01 0713``) follows.
_UC_PARCA_KISA_TARIH = re.compile(r"(?<!\d)\d{1,2}[/\-.]\d{1,2}[/\-.]\d{1,2}(?!\d)")
#: Any four-digit run; used only to tell a preceding year from a following time.
_DORT_RAKAM_DESENI = re.compile(r"\d{4}")
#: An English month name (what pandas reads); with two short runs before a four-digit run, that run
#: is a time rather than a year.
_AY_ADI = re.compile(r"(?i)(?<![a-z])(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)")


def _iki_hane_yil_maskesi(seri) -> np.ndarray:
    """True where a string date cell carries no placeable four-digit year.

    A ``str`` cell (``np.str_`` included) whose date part -- the text with its time of day, fraction
    and attached offset removed -- has no run of exactly four (``YYYY``) or eight (``YYYYMMDD``)
    digits but looks like a date (two or more runs of at most two digits, or a six-digit ``YYMMDD``
    run) is refused by position before any parse.  A three-part short date (``21/01/01``) with no
    four-digit run before it is refused too, even when a four-digit run follows (the colon-less
    ``HHMM`` time).  In general, the first four- or eight-digit
    run is the year only if no complete short date precedes it (three short runs, two short runs
    with a month name, or a six-digit ``YYMMDD`` run); a month name with a single short run and no
    four-digit run (``Jun '99``, ``Jun 1``) is refused as well.  A datetime object is unaffected.
    The cell's text never enters a message.  This is the safe side: a refused cell is never kept.
    """
    dizi = seri.to_numpy() if isinstance(seri, pd.Series) else np.asarray(seri)

    def _iki(v) -> bool:
        if not isinstance(v, str):
            return False
        # a short three-part date with no four-digit run before it
        # is a two-digit-year date, even when a colon-less ``HHMM`` four-digit run follows it.
        for m in _UC_PARCA_KISA_TARIH.finditer(v):
            if _DORT_RAKAM_DESENI.search(v[:m.start()]) is None:
                return True
        tarih = _SAAT_DESENI.sub(" ", v)
        eslesen = list(_RAKAM_KOSUSU.finditer(tarih))
        kosular = [len(k.group()) for k in eslesen]
        ilk = next((j for j, n in enumerate(kosular) if n in (4, 8)), None)
        if ilk is not None and int(eslesen[ilk].group()[:4]) < 1000:
            return True   # a first year run below 1000 has no placeable instant
        if (kosular == [4, 6] and tarih[eslesen[1].start() - 1] not in ".,"
                and _AY_ADI.search(tarih[:eslesen[0].start()]) is None):
            # one four-digit run, then one six-digit run (``1713 202106``, ``1713 062021``,
            # ``1713 Jun 012021``): pandas takes the four-digit run as the year and the six-digit run as a time
            return True
        if any(kosular[i] == 4 and kosular[i + 1] >= 5 and tarih[eslesen[i + 1].start() - 1] in ".,"
               for i in range(len(kosular) - 1)):
            # anywhere in the cell, a four-digit run and then a run of five or more digits right after
            # a dot or a comma (a further short run or month name after it, or a day run before it, included);
            # for example a four-digit run, then a run of five or more digits right after a dot or a comma
            # (``1713.202106``, ``1713,01062021``, the decimal year ``2015.416667``): pandas reads the four-digit
            # run as the year and the rest as a time or a fraction, never as the date it may hold
            return True
        if ilk is not None:
            # The first four- or eight-digit run is the year only if
            # no complete short date precedes it -- three short runs, two short runs with a month
            # name, or a six-digit ``YYMMDD`` run.  After one it is a colon-less time
            # (``21 Jan 01 0713``, ``210101 0713``) or an offset (``Jun 1 21 07:13:47 AM +0100``).
            once = kosular[:ilk]
            kisa = sum(1 for n in once if n <= 2)
            return bool(6 in once or kisa >= 3
                        or (kisa >= 2 and _AY_ADI.search(tarih[:eslesen[ilk].start()]) is not None))
        # a month name with a single short run and no four-digit run
        # (``Jun '99``, ``Jun 1``) is a date without a placeable instant; refuse it too.  The
        # short runs are counted, so a longer run beside them (``021 Jun 01``) does not cancel the rule.
        kisa = sum(1 for n in kosular if n <= 2)
        if _AY_ADI.search(tarih) is not None and kisa == 1:
            return True
        # date-like: two or more short runs (21/01/01, 1/1/21, Jan 21 01, 21 01 01, 021-06-01) or YYMMDD
        return kisa >= 2 or 6 in kosular

    return np.array([_iki(v) for v in dizi], dtype=bool)


#: A text cell parsed before this instant has no placeable four-digit year (pandas' default year 1
#: for a year-less cell, a three-digit or zero-padded year, a colon-less time read as the year).  pandas 2
#: cannot hold such an instant (NaT); pandas 3 can, so the floor makes both versions refuse it.
_METIN_YIL_TABANI = pd.Timestamp("1000-01-01", tz="UTC")


def _taban_alti_nat(ham_dizi, zaman):
    """``zaman`` with every ``str`` cell parsed before ``_METIN_YIL_TABANI`` set to ``NaT`` (refused by
    position as unparsed by the caller; its text never enters a message)."""
    if not isinstance(zaman, pd.Series) or not isinstance(zaman.dtype, pd.DatetimeTZDtype):
        return zaman
    metin = np.array([isinstance(v, str) for v in ham_dizi], dtype=bool)
    if len(metin) != len(zaman) or not metin.any():
        return zaman
    alt = (zaman < _METIN_YIL_TABANI).to_numpy() & metin
    return zaman.mask(pd.Series(alt, index=zaman.index)) if alt.any() else zaman


#: A four-digit run, or the first four digits of a run of eight or more digits, in a text cell's
#: date part (time of day, fraction and attached offset removed; a run right after "+" is not a year).  A
#: run right after "." or "," may be the year (``Jun 1,2021``, ``01-Jun.2021``).
_YIL_ADAYI = re.compile(r"(?<![\d+])(\d{4})(?:\d{4,})?(?!\d)")
#: A six-digit run (its first or last four digits may be the year: ``YYYYMM``, ``MMYYYY``, ``DDYYYY``) or an
#: eight-digit run (its last four: ``DDMMYYYY``, ``MMDDYYYY``), not right after a digit or "+" (a run
#: right after "." or "," is counted too, in a flagged cell only).
_ALTI_SEKIZ = re.compile(r"(?<![\d+])(\d{6}|\d{8})(?!\d)")


def _metin_muhur_yili(v) -> Optional[int]:
    """The largest year run >= MUHUR_YIL in a ``str`` cell's date part, or None."""
    if not isinstance(v, str):
        return None
    tarih = _SAAT_DESENI.sub(" ", _onek_temizle(v))
    yillar = [int(m.group(1)) for m in _YIL_ADAYI.finditer(tarih)]
    yillar = [y for y in yillar if y >= MUHUR_YIL]
    return max(yillar) if yillar else None


def _yanlis_okunan_muhur(ham_dizi, anlar) -> np.ndarray:
    """True where a ``str`` cell PARSED to an instant whose UTC year is more than one year below a sealed year run
    in its own text (pandas took another run as the year: ``1713 01 Jun 2021`` -> 1713).  A cell that did not parse
    is left to the leading-year rule; a cell whose instant is within a year of its sealed
    run (an offset shift, ``2021-01-01T00:30+01:00`` -> 2020-12-31) is decided by its instant."""
    out = np.zeros(len(ham_dizi), dtype=bool)
    for k, v in enumerate(ham_dizi):
        y = _metin_muhur_yili(v)
        if y is None or k >= len(anlar):
            continue
        a = anlar[k]
        if a is None or pd.isna(a):
            continue
        try:
            t = pd.Timestamp(a).tz_convert("UTC")
        except (TypeError, ValueError):
            t = pd.Timestamp(a)
        # within one year of the sealed run only an instant on 31 December of the year before (an offset
        # that moves the instant across the new year) keeps its instant
        out[k] = t.year < y - 1 or (t.year == y - 1 and (t.month, t.day) < (12, 31))
    return out


def _metin_muhur_sayilir(v, isaretli: bool) -> bool:
    """Before a text date cell with no four-digit year is refused, a cell is counted when its leading year is sealed, and a flagged cell
    also when a year run in its date part is sealed."""
    y = _yil_onek(v)
    return ((y is not None and y >= MUHUR_YIL) or _metin_muhur_yili(v) is not None   # every cell
            or (isaretli and _uzun_kosu_muhur(v)))


def _uzun_kosu_muhur(v) -> bool:
    """A six-digit run whose first or last four digits, or an eight-digit run whose last four digits, read
    2021 or later in a ``str`` cell's date part (time of day, fraction and attached offset removed)."""
    if not isinstance(v, str):
        return False
    tarih = _SAAT_DESENI.sub(" ", _onek_temizle(v))
    for m in _ALTI_SEKIZ.finditer(tarih):
        k = m.group(1)
        if int(k[-4:]) >= MUHUR_YIL or (len(k) == 6 and int(k[:4]) >= MUHUR_YIL):
            return True
    return False


def _ad_kapisi(ad: str, *, yilsiz_izin_listesi: bool = False) -> None:
    """Refuse one basename: any 4-digit run >= 2016; with ``yilsiz_izin_listesi`` (the K9
    catalogue path only) also a year-less name that is not on :data:`CPTI15_ADLARI`."""
    yillar = dosya_yillari(ad)
    yasak = [y for y in yillar if y >= ACILMAYAN_YIL]
    if yasak:
        raise MuhurIhlali(
            f"{ad}: dosya adı {yasak} yıl(lar)ını taşıyor; "
            f"{ACILMAYAN_YIL} ve sonrası mühür/kesim dışıdır, dosya açılmadı"
        )
    if yilsiz_izin_listesi and not yillar and not _cpti15_adi(ad):
        raise BicimHatasi(
            f"{ad}: dosya adı dört haneli bir yıl taşımıyor ve izinli CPTI15 adlarından "
            f"biri değil ({CPTI15_ADLARI}); açılmadı"
        )


def _kapali_bileseni(yol) -> bool:
    """True when a path component starts ``kapali`` (the closed 2016-2020 window)."""
    return any(p.startswith("kapali") for p in os.fspath(yol).split(os.sep) if p)


def yil_kapisi(yol, *, _yilsiz_izin_listesi: bool = False) -> None:
    """Refuse a file whose name carries any year >= 2016, without opening it.

    Every maximal four-digit run is read.  The gate runs on the given basename **and** on
    the realpath's basename, and a path component starting ``kapali`` is refused, so a symlink or a
    rename cannot hide the target's year or the closed window.

    This is the shared gate other readers call: a year-less name passes here.  The K9
    catalogue path adds the CPTI15 allow-list through :func:`katalog_yil_kapisi`.
    """
    yol = os.fspath(yol)
    if _kapali_bileseni(yol):
        raise MuhurIhlali(
            f"{os.path.basename(yol)}: yol 'kapali' bileşeni taşıyor; kapalı 2016-2020 penceresi, "
            "dosya açılmadı"
        )
    gercek = os.path.realpath(yol)
    if _kapali_bileseni(gercek):
        raise MuhurIhlali(
            f"{os.path.basename(yol)}: gerçek yol 'kapali' bileşeni taşıyor; kapalı 2016-2020 "
            "penceresi, dosya açılmadı"
        )
    for ad in sorted({os.path.basename(yol), os.path.basename(gercek)}):
        _ad_kapisi(ad, yilsiz_izin_listesi=_yilsiz_izin_listesi)


def katalog_yil_kapisi(yol) -> None:
    """The K9 catalogue gate: :func:`yil_kapisi` plus the year-less allow-list.

    A year-less name is accepted only when it is on :data:`CPTI15_ADLARI`; any other year-less
    name is refused unopened.  Only the K9 importer's own paths use it."""
    yil_kapisi(yol, _yilsiz_izin_listesi=True)


def kaynaklari_coz(yollar) -> List[str]:
    """Expand ``--kaynaklar`` globs to concrete paths without opening any of them."""
    acilacak: List[str] = []
    for y in yollar:
        if any(c in str(y) for c in "*?["):
            acilacak.extend(sorted(_glob.glob(str(y))))
        else:
            acilacak.append(str(y))
    return acilacak


def muhur_kok_kapisi(kaynaklar, muhur_koku, *, srcmod=None) -> dict:
    """Run the seal attestation and gate every input path under ``<muhur>/deprem``.

    Must run before any catalogue is opened.  ``muhur_bloku_uret`` runs first and raises (its
    own ``MuhurIhlali``) when the seal root is not clean; then every concrete ``--kaynaklar``
    path (after glob expansion) and the optional ``--srcmod`` directory must resolve (realpath)
    under the seal root's ``deprem`` subtree and carry no ``kapali`` component, or they are
    refused by name.  Returns the clean seal block.
    """
    blok = muhur_bloku_uret(muhur_koku)
    deprem = os.path.realpath(os.path.join(os.fspath(muhur_koku), "deprem"))
    hedefler = [(y, "--kaynaklar") for y in kaynaklari_coz(kaynaklar)]
    if srcmod is not None:
        hedefler.append((os.fspath(srcmod), "--srcmod"))
    for yol, rol in hedefler:
        hedef = os.path.realpath(os.fspath(yol))
        if _kapali_bileseni(hedef):
            raise MuhurIhlali(
                f"{os.path.basename(hedef)}: {rol} gerçek yolu 'kapali' bileşeni taşıyor; "
                "dosya açılmadı"
            )
        if not (hedef == deprem or hedef.startswith(deprem + os.sep)):
            raise MuhurIhlali(
                f"{os.path.basename(hedef)}: {rol} yolu {deprem} altında değil; "
                "dosya açılmadı"
            )
    return blok


# --- scaling (fault loading, K9 sources) ---------------------------------------------------

def kaynak_geometri(Mw, *, kayma_turu: str = "hepsi") -> Tuple[float, float, float, float, float]:
    """``(A_km2, L_km, W_km, M0_Nm, D_m)`` from the WC94 Table 2A area and L/W = 2.

    ``A = 10**(a + b Mw)`` for the declared all-types row (Wells & Coppersmith 1994 Table 2A,
    ``log(RA) = a + b*M``, "All", 148 events: ``a = -3.49``, ``b = 0.91``), ``L = sqrt(2 A)``,
    ``W = A / L`` with the declared aspect ratio, ``M0 = 10**(1.5 Mw + 9.1)`` (Hanks & Kanamori
    1979) and the uniform-slip displacement ``D = M0 / (mu A)``.  ``kayma_turu="normal"`` selects
    the table's normal-fault row (``-2.87 + 0.82 Mw``, 22 events) as a sensitivity row only; the
    default ``"hepsi"`` keeps every caller on the declared all-types relation.  An unknown
    ``kayma_turu`` is refused rather than silently defaulted.
    """
    mw = float(Mw)
    if kayma_turu == "hepsi":
        egim, kesisim = WC94_ALAN_EGIM, WC94_ALAN_KESISIM
    elif kayma_turu == "normal":
        egim, kesisim = WC94_ALAN_N_EGIM, WC94_ALAN_N_KESISIM
    else:
        raise ValueError(
            f"bilinmeyen kayma_turu {kayma_turu!r}; beklenen 'hepsi' ya da 'normal'")
    A_km2 = 10.0 ** (egim * mw + kesisim)
    L_km = float(np.sqrt(EN_BOY_ORANI * A_km2))
    W_km = float(A_km2 / L_km)
    M0_Nm = 10.0 ** (1.5 * mw + 9.1)
    D_m = float(M0_Nm / (MU_PA * A_km2 * 1e6))
    return float(A_km2), L_km, W_km, float(M0_Nm), D_m


def kayma_gerilme_hizi(v_s_mm_yr, W_km, L_km, *, C: float = C_YUKLEME,
                        mu: float = MU_PA) -> np.ndarray:
    """Per-fault stressing rate ``C mu v_s / sqrt(W L)`` in Pa/year (Console et al. 2008, eq. A9).

    The constant-stress-drop elastic scaling; strain rate times stiffness is deliberately **not**
    implemented anywhere.  ``W`` and ``L`` in km, ``v_s`` in mm/year.
    """
    v_s = np.asarray(v_s_mm_yr, dtype=np.float64) * 1e-3 / YIL_SANIYE
    kok = np.sqrt(np.asarray(W_km, dtype=np.float64) * 1e3
                  * np.asarray(L_km, dtype=np.float64) * 1e3)
    return C * mu * v_s / kok * YIL_SANIYE


def console_a9_gerinme_hizi(eps_dot_per_yr, *, mu: float = MU_PA) -> np.ndarray:
    """Regional path of Console et al. 2008 A9: ``(pi**2 / 32) mu eps_dot`` in Pa/year.

    With ``eps_dot = 6 mm/yr / 60 km`` this gives 925 Pa/yr; with the per-fault slip rate it is
    equivalent to :func:`kayma_gerilme_hizi` through ``v_s = (pi**2/32) eps_dot sqrt(WL)``.
    """
    return PI2_32 * mu * np.asarray(eps_dot_per_yr, dtype=np.float64)


# --- catalog reading (gates inside the read) ----------------------------------------------

def _bos_cerceve() -> pd.DataFrame:
    df = pd.DataFrame({c: pd.Series(dtype="float64") for c in _KATALOG_SUTUNLARI})
    df["time_utc"] = pd.Series(dtype="datetime64[ns, UTC]")
    return df[list(_KATALOG_SUTUNLARI)]


def _yil_kapisi_dosyalari(yollar):
    """Expand globs, apply :func:`yil_kapisi` before opening anything, and split the list.

    Returns ``(acilacak, reddedilen)``.  A concrete path the caller named is refused by
    :func:`yil_kapisi` (which raises); a path only a glob produced is skipped and its basename
    returned in ``reddedilen``, because a glob asks for "whatever is there" and the report must
    name what was left unopened.
    """
    acilacak: List[str] = []
    reddedilen: List[str] = []
    for y in yollar:
        desen = any(c in str(y) for c in "*?[")
        adaylar = sorted(_glob.glob(str(y))) if desen else [str(y)]
        for yol in adaylar:
            try:
                katalog_yil_kapisi(yol)
            except MuhurIhlali:
                if not desen:
                    raise
                reddedilen.append(os.path.basename(yol))
            else:
                acilacak.append(yol)
    return acilacak, reddedilen


def katalog_oku(yollar, *, yan_koku=None) -> Tuple[pd.DataFrame, dict]:
    """Read seal-clean, cutoff-respecting catalogs through the ``knotenlinie.etas`` adapters.

    ISIDe FDSN text files are handed to ``knotenlinie.etas.katalog.iside_oku`` (its file-year gate
    refuses ``iside_2016..2020`` before opening) and CPTI15 CSVs to ``cpti15_oku``.  K9's own
    multi-year name gate runs first, before the adapter's first-match ``yollari_coz``, so an
    ``iside_2015_2020.txt`` cannot hide its later year.  The non-ISIDe branch routes only the
    exact basename on :data:`CPTI15_ADLARI` to ``cpti15_oku``; every other ``.csv``/``.txt`` is
    refused, and the refusal happens before the file is opened.  For the CPTI15 split,
    :func:`_cpti15_yan_kapisi` first checks the sibling ``<file>.json`` sidecar and refuses unless
    it binds the CSV.  The concatenated frame is gated again here (defence in depth).  The adapters are imported lazily so code that never reads a catalogue needs no catalogue file at all.
    """
    try:
        from knotenlinie.etas import katalog as _K
    except ImportError as exc:  # pragma: no cover - exercised only when knotenlinie/etas is absent
        raise KatalogYok("knotenlinie.etas.katalog içe aktarılamadı; katalog yolları okunamaz") from exc

    yollar = [yollar] if isinstance(yollar, (str, bytes, os.PathLike)) else list(yollar)
    iside, diger = [], []
    for y in yollar:
        (iside if "iside" in os.path.basename(str(y)).lower() else diger).append(y)

    cerceveler: List[pd.DataFrame] = []
    raporlar: List[dict] = []
    if iside:
        # K9's own multi-year gate first, before ``knotenlinie.etas``' first-match ``yollari_coz``.
        guvenli, onceden = _yil_kapisi_dosyalari(iside)
        try:
            df, r = _K.iside_oku(guvenli)
        except _K.MuhurIhlali as exc:
            raise MuhurIhlali(str(exc)) from exc
        # an explicitly named file the year gate refused is an error; a glob skips it by design
        if r.get("acilmayan"):
            adli = [y for y in iside if not any(c in str(y) for c in "*?[")]
            if adli:
                raise MuhurIhlali(
                    f"dosya adı {ACILMAYAN_YIL} ya da sonrası bir yıl taşıyor, açılmadı: "
                    f"{r['acilmayan']}"
                )
        if onceden:
            r["acilmayan"] = list(r.get("acilmayan") or []) + onceden
        cerceveler.append(df)
        raporlar.append(r)

    # The non-ISIDe branch: every concrete path first passes the year gate, then the CPTI15
    # allow-list.  A refused glob is named in a synthetic report part, never opened.
    diger_acilacak: List[str] = []
    diger_reddedilen: List[str] = []
    for y in diger:
        a, red = _yil_kapisi_dosyalari([y])
        diger_acilacak += a
        diger_reddedilen += red
    for yol in diger_acilacak:
        ad = os.path.basename(yol)
        if not ad.lower().endswith(".csv"):
            raise BicimHatasi(
                f"tanınmayan katalog biçimi (yalnız iside .txt ve CPTI15 .csv): {ad}")
        if not _cpti15_adi(ad):
            raise BicimHatasi(
                f"{ad}: izinli CPTI15 adlarından biri değil ({CPTI15_ADLARI}); açılmadı")
        yan = _cpti15_yan_kapisi(yol, yan_koku)
        try:
            df, r = _K.cpti15_oku(yol)
        except _K.MuhurIhlali as exc:
            raise MuhurIhlali(str(exc)) from exc
        _cpti15_rapor_kapisi(ad, r, yan)
        cerceveler.append(df)
        raporlar.append(r)
    if diger_reddedilen:
        raporlar.append({
            "kaynak": "cpti15-dosyaadi", "okunan": 0, "tutulan": 0, "atilan_kesim": 0,
            "atilan_muhur": 0, "acilan": [], "acilmayan": diger_reddedilen, "kesim": KESIM,
        })

    df = pd.concat(cerceveler, ignore_index=True) if cerceveler else _bos_cerceve()
    df = muhur_kapisi(df)
    kesim = _an(KESIM)
    df = df.loc[df["time_utc"] <= kesim].reset_index(drop=True)
    return df, {"parcalar": raporlar, "tutulan": int(len(df))}


def _sayisal_zaman_maskesi(seri) -> np.ndarray:
    """True where a raw time cell is a real number rather than a datetime.

    A numeric cell is ambiguous (epoch seconds, nanoseconds since 1970, ...), so it is refused by
    position instead of being read as a pandas nanosecond count.  A ``datetime64`` cell is not a
    number, ``bool`` is not a time, and a float ``NaN`` is a *missing* cell like ``None``/``NaT``,
    not a number; ``inf`` and ``1e20`` stay numeric.  ``Decimal`` and ``Fraction`` are numeric here too, so they are refused
    under the numeric message, not the unparsed one.
    """
    dizi = seri.to_numpy() if isinstance(seri, pd.Series) else np.asarray(seri)

    def _sayi_mi(v) -> bool:
        if isinstance(v, (_decimal.Decimal, _fractions.Fraction)):
            return True
        if isinstance(v, (bool, np.bool_)) or not isinstance(
                v, (int, float, np.integer, np.floating)):
            return False
        return not (isinstance(v, (float, np.floating)) and bool(np.isnan(v)))

    return np.array([_sayi_mi(v) for v in dizi], dtype=bool)


def _coerce_konumlari(ham_dizi) -> Tuple[List[int], List[Optional[pd.Timestamp]], List[bool]]:
    """For each cell, its parsed UTC instant (or ``None``), the positions its parse raises on, and
    whether its parse reported an unrecognised timezone.

    Used only when the whole-column coerce parse raises (a wrong-shaped input).  The fallback reads each cell's own parsed UTC instant, so a cell that parses is
    judged by it rather than by its leading text; this returns the instants alongside the failing
    positions.  The parse runs one cell at a time under the shared lock with warnings recorded and
    never shown, so a pandas
    ``FutureWarning`` for an unrecognised timezone never quotes a sealed cell.  An empty position
    list means no single cell reproduces the failure, and the caller's message says the positions
    are unknown.

    A cell whose own parse recorded an
    unrecognised timezone or the "as tzlocal" branch is returned with ``None``, listed among the
    failing positions, and flagged in the third list.  The caller does not exclude the flag from
    the leading-year count: such a cell's leading year decides the seal (a sealed leading year is
    counted, an earlier one is refused by position).  A ``str`` cell whose own parsed instant is before 1000-01-01 is
    returned as ``None`` too, so the year floor applies on this path as well; its own text never
    enters a message.
    """
    konumlar: List[int] = []
    anlar: List[Optional[pd.Timestamp]] = []
    taninmadi: List[bool] = []
    for k in range(len(ham_dizi)):
        try:
            with _ZAMAN_KILIDI:
                with _warnings.catch_warnings(record=True) as kayit:
                    _warnings.simplefilter("always")
                    tek = pd.to_datetime(pd.Series([ham_dizi[k]]), utc=True, errors="coerce")
        except (ValueError, TypeError, OverflowError, AttributeError):
            if len(konumlar) < 5:
                konumlar.append(k)
            anlar.append(None)
            taninmadi.append(False)
            continue
        if _taninmayan_zaman_dilimi(kayit):
            if len(konumlar) < 5:
                konumlar.append(k)
            anlar.append(None)
            taninmadi.append(True)
            continue
        if not isinstance(tek, pd.Series):
            tek = pd.Series(tek)
        if len(tek) and not bool(pd.isna(tek.iloc[0])):
            # a text cell whose own instant is below the year floor
            # has no placeable four-digit year either; hand it back as none so the leading-year rule
            # decides it (defence in depth on the fallback path).
            if isinstance(ham_dizi[k], str) and tek.iloc[0] < _METIN_YIL_TABANI:
                anlar.append(None)
            else:
                anlar.append(tek.iloc[0])
        else:
            anlar.append(None)
        taninmadi.append(False)
    return konumlar, anlar, taninmadi


def _zaman_sutunu_canli(seri) -> Tuple[pd.Series, np.ndarray]:
    """Parse a whole time column, then ``NaT`` every cell whose parse reported an unrecognised tz.

    Returns ``(zaman, taninmadi)``.  The whole-column parse runs with warnings recorded and never
    shown; if any recorded warning names an unrecognised timezone
    or the "as tzlocal" branch, each cell is parsed alone (through
    :func:`_coerce_konumlari`, positionally, under the shared lock) and the ones that report it
    become ``NaT`` and are flagged in ``taninmadi``.  They are not excluded from the
    leading-year count: a sealed leading year is counted, an earlier
    one is refused by position.  The recorded message quotes the cell and is inspected only for
    the phrase; it is never kept or shown.  The re-parse is handed
    ``dizi.to_numpy()`` so a caller's label index can never be read as a position.  Pandas 2 guesses the whole column's format from its first cell, so a
    column whose first cell carries an abbreviation holds every later cell of another shape as
    ``NaT``; the column is rebuilt from the per-cell instants ``_coerce_konumlari`` returns, so the
    first cell no longer decides the column.
    """
    with _ZAMAN_KILIDI:
        with _warnings.catch_warnings(record=True) as kayit:
            _warnings.simplefilter("always")
            zaman = pd.to_datetime(seri, utc=True, errors="coerce")
    if not isinstance(zaman, pd.Series):
        zaman = pd.Series(zaman)
    taninmadi = np.zeros(len(zaman), dtype=bool)
    if _taninmayan_zaman_dilimi(kayit):
        dizi = seri if isinstance(seri, pd.Series) else pd.Series(seri)
        _konumlar, anlar, taninmadi_list = _coerce_konumlari(dizi.to_numpy())
        taninmadi = np.asarray(taninmadi_list, dtype=bool)[:len(zaman)]
        # Pandas 2 guessed the column's format from its first cell;
        # with an abbreviation there the format held it literally and later cells of another shape
        # were NaT.  pandas 3 cannot guess that format and parses each cell alone, so rebuild the
        # column from the per-cell instants (the row-for-row answer).
        yeni = [pd.NaT if (a is None or t) else a for a, t in zip(anlar, taninmadi_list)]
        zaman = pd.Series(yeni, index=zaman.index, dtype="datetime64[ns, UTC]")
    return zaman, taninmadi


def _zaman_maskeleri(ham) -> Tuple[pd.Series, np.ndarray, np.ndarray]:
    r"""Parse raw time cells and return ``(time, sealed, numeric)`` masks, never a cell's text.

    Times are parsed with ``errors="coerce"``; a parsed time at
    or after the seal, or an unparsed cell whose leading four digits are a sealed year, is sealed;
    a numeric cell is flagged for refusal by position.  A parse that still raises becomes a
    ``BicimHatasi`` reporting the failing positions it can name (or an explicit "unknown") and no
    chained traceback.

    A bool/timedelta/period column coerces to a tz-naive column; such a dtype
    is refused by dtype name instead of reaching the seal comparison (which would otherwise raise
    a bare ``TypeError``).  The leading-year count runs **before** that refusal,
    so a period column, an interval or a bytes cell whose text carries a sealed year is counted
    (never quoted) and handed back in the sealed mask; only a dtype with no sealed year in its
    text is refused by name.  ``muhur_tara`` therefore still returns the count.  Only text/bytes
    cells (``re.match(r"\s*(\d{4})")``) and a Period/Interval cell's endpoints are scanned; a numeric
    cell is excluded (refused by position) and every other value, including a ``timedelta``, counts
    as nothing, so a non-time dtype with no sealed date in it is still refused by name.  A Period's
    year is read from its daily frequency inside a try; a date-typed cell counts by its UTC year
    (naive as UTC); the leading years are counted even when the whole-column parse raises, before
    the refusal by position; leading whitespace, category-``Cf`` characters and the named
    default-ignorables are stripped before the text rule, BOM-carrying UTF-16 bytes are decoded, and
    ``bytearray``/``memoryview`` are treated as bytes; pandas warnings around the parse are
    suppressed under one shared lock.  In the whole-column fallback each cell's own parsed UTC
    instant decides (the leading-year rule applies only to a cell that does not parse, and the
    count may exceed one).  A cell whose parse reported an unrecognised timezone or the "as tzlocal"
    branch is ``NaT`` and goes through the leading-year rule -- a sealed leading year is counted, an
    earlier one is refused by position (never read as a wall time).  A string date cell with no
    four-digit year is refused by position before any parse.  After the parse, a
    ``str`` cell whose parsed UTC instant is before 1000-01-01 (pandas' default year 1 for a
    year-less cell, a three-digit or zero-padded year, a colon-less time read as the year) becomes
    ``NaT`` before the leading-year rule and the NaT refusal; pandas 3 can hold such an instant, so
    a sealed one is now counted instead of returned, and every other one is refused by position.
    """
    if isinstance(ham, pd.DataFrame):
        raise BicimHatasi(
            "time_utc sütunu birden çok kez var; hangi zaman sütununun okunacağı belirsiz")
    ham_dizi = ham.to_numpy() if isinstance(ham, pd.Series) else np.asarray(ham)
    sayisal = _sayisal_zaman_maskesi(ham)
    iki_hane = _iki_hane_yil_maskesi(ham_dizi)
    if bool(iki_hane.any()):
        # Seal first, counted.  A flagged cell whose leading-year
        # prefix is at or after the seal is counted (the count is the seal's witness) and handed
        # back in the sealed mask, so ``muhur_tara`` still returns the count and the one gate
        # raises ``MuhurIhlali``; the refusal of a text date cell with no four-digit year fires only
        # when no flagged cell is sealed.
        muhur_ek = np.array([_metin_muhur_sayilir(v, bool(i)) for v, i in zip(ham_dizi, iki_hane)],
                            dtype=bool) & ~np.asarray(sayisal, dtype=bool)
        if bool(muhur_ek.any()):
            return (pd.Series(pd.NaT, index=range(len(ham_dizi)), dtype="datetime64[ns, UTC]"),
                    muhur_ek, sayisal)
        raise BicimHatasi(
            f"{int(iki_hane.sum())} sat\u0131rda d\u00f6rt haneli y\u0131l ta\u015f\u0131mayan metin tarih h\u00fccresi "
            f"(sat\u0131r konumlar\u0131): {np.flatnonzero(iki_hane)[:5].tolist()} "
            "(year-floor rule)")
    try:
        zaman, taninmadi = _zaman_sutunu_canli(ham)
    except (ValueError, TypeError, OverflowError, AttributeError):
        # The whole-column parse failed, so read each cell alone
        # (under the shared lock, with warnings recorded, in :func:`_coerce_konumlari`) and let its
        # own parsed UTC instant decide; the leading-year text rule applies only to a cell that
        # does not parse.  The leading-year count is kept for a text/date cell pandas cannot
        # parse; the count may exceed one.  A cell with an unrecognised timezone or the "as tzlocal" branch
        # (NaT, flagged) goes through the leading-year rule -- a sealed leading year is counted, an
        # earlier one is refused by position; it is never read as a wall time.
        hucreler = ham.tolist() if isinstance(ham, pd.Series) else list(ham_dizi)
        konumlar, anlar, _taninmadi_list = _coerce_konumlari(ham_dizi)
        muhur_ek = _yanlis_okunan_muhur(ham_dizi, anlar) & ~np.asarray(sayisal, dtype=bool)
        say = np.asarray(sayisal)
        muhur_ani = _an(MUHUR_BASI)
        for k in range(len(hucreler)):
            if say.ndim == 1 and k < len(say) and bool(say[k]):
                continue   # a numeric cell is refused by position, not sealed
            an = anlar[k] if k < len(anlar) else None
            if an is not None:
                if an >= muhur_ani:
                    muhur_ek[k] = True
            else:
                yil = _yil_onek(hucreler[k])
                if yil is not None and yil >= MUHUR_YIL:
                    muhur_ek[k] = True
        if bool(muhur_ek.any()):
            return (pd.Series(pd.NaT, index=range(len(hucreler)), dtype="datetime64[ns, UTC]"),
                    muhur_ek, sayisal)
        if konumlar:
            raise BicimHatasi(
                f"{len(konumlar)} satırda zaman çözülemedi (satır konumları): "
                f"{konumlar}") from None
        raise BicimHatasi(
            "zaman çözülemedi (satır konumları bilinmiyor)") from None
    if not isinstance(zaman, pd.Series):
        zaman = pd.Series(zaman)
    zaman = _taban_alti_nat(ham_dizi, zaman)   # the text-cell year floor
    yanlis = _yanlis_okunan_muhur(ham_dizi, list(zaman)) & ~np.asarray(sayisal, dtype=bool)
    nat = zaman.isna().to_numpy()
    # Count the leading years **before** the dtype refusal.  A period column
    # (and a bytes or interval-of-datetimes cell whose text carries a sealed year) coerces to a
    # tz-naive or all-NaT column; the old order refused it by dtype before its text could be
    # counted.  Only text/bytes and a
    # Period/Interval cell's endpoints, so the count never quotes a cell and a ``timedelta`` or a
    # numeric cell is not sealed; the dtype refusal below runs only when no sealed date was found.
    # A cell whose parse reported an unrecognised timezone or the
    # "as tzlocal" branch is NaT and goes through the leading-year rule -- a sealed leading year
    # is counted, an earlier one is refused by position.
    muhur_ek = np.zeros(len(nat), dtype=bool)
    if len(nat) and nat.any():  # only an unparsed cell can carry a sealed leading year
        hucreler = ham.tolist() if isinstance(ham, pd.Series) else ham_dizi
        muhur_ek = np.array(
            [(lambda y: y is not None and y >= MUHUR_YIL)(_yil_onek(hucreler[k]))
             for k in range(len(hucreler))], dtype=bool) & nat
    if not isinstance(zaman.dtype, pd.DatetimeTZDtype):
        if bool(muhur_ek.any()):
            # the leading-year count already sealed the column; hand the count to the caller
            return zaman, muhur_ek, sayisal
        tur = getattr(ham, "dtype", type(ham).__name__)
        raise BicimHatasi(
            f"zaman sütunu UTC farkında bir zaman türü değil: {tur}")
    muhur_parsed = (zaman >= _an(MUHUR_BASI)).to_numpy() & ~sayisal
    return zaman, (muhur_parsed | muhur_ek | yanlis), sayisal


def zaman_kapisi(ham) -> pd.Series:
    """The one time gate for every path.

    ``_cercevele``'s order becomes this single function: parse with ``errors="coerce"``, count the
    seal first, then refuse numeric cells by position, then refuse unparsed or missing cells by
    position.  It never quotes a cell, and the message carries a count or real row positions only.
    ``_cercevele`` and :func:`muhur_kapisi` both reach this one order; :func:`muhur_tara` (count only)
    no longer stands in for it anywhere.
    Returns the parsed times so a caller does not parse again.

    It accepts only a :class:`pandas.Series`.  ``df["time_utc"]`` on a frame
    with duplicate ``time_utc`` columns is a ``DataFrame``, and a list or array is not a column at
    all; both are refused by name instead of parsing an ambiguous shape.  The
    leading-year count inside :func:`_zaman_maskeleri` runs before the dtype refusal, so a period
    column (or any date-carrying dtype whose text carries a sealed year) raises ``MuhurIhlali``,
    counted.  Only text/bytes and a Period/Interval cell's
    endpoints are counted, so a non-date dtype (bool, timedelta, ...) is still refused by name and
    a numeric cell by position.  A date-typed
    cell (including one pandas 2 cannot represent, like ``datetime(9999, ...)``) counts by its UTC
    year, a leading U+FEFF/U+200B and the named default-ignorables are stripped, and
    ``bytearray``/``memoryview`` are bytes; a ``Decimal``/``Fraction`` is refused under the numeric
    message.  Every suppressed parse here and in the readers shares one lock.  The no-warning
    guarantee holds for a gate that runs in one thread, because pandas (``pandas_dtype``,
    ``read_csv``) and caller code can swap the process-wide filter list from another thread.  A cell
    with an unrecognised timezone or the "as tzlocal" branch is read as ``NaT`` and its leading year
    is counted (a sealed year is the seal, an earlier one is refused by position; never read as a
    wall time); in the whole-column fallback each cell's own parsed instant decides.  A string date
    cell with no four-digit year is refused by position, before any parse.  Every ``str`` cell has
    a year floor: one parsed before 1000-01-01 UTC is ``NaT`` (a sealed one is counted, every other
    is refused by position), so pandas 3 cannot return a year-less or sub-1000-year text cell.
    """
    if isinstance(ham, pd.DataFrame):
        raise BicimHatasi(
            "time_utc sütunu birden çok kez var; hangi zaman sütununun okunacağı belirsiz")
    if not isinstance(ham, pd.Series):
        raise BicimHatasi(
            f"zaman kapısı bir Seri bekler; gelen tür {type(ham).__name__}")
    zaman, muhurlu, sayisal = _zaman_maskeleri(ham)
    if bool(muhurlu.any()):
        raise MuhurIhlali(
            f"{int(muhurlu.sum())} satır {MUHUR_BASI} ve sonrasında; mühür okumayı yasaklar; "
            "satır düşürülmez, okuma durur")
    if bool(sayisal.any()):
        raise BicimHatasi(
            f"{int(sayisal.sum())} satırda sayısal zaman hücresi (satır konumları): "
            f"{np.flatnonzero(sayisal)[:5].tolist()}")
    nat = zaman.isna().to_numpy()
    if bool(nat.any()):
        raise BicimHatasi(
            f"{int(nat.sum())} satırda zaman çözülemedi (satır konumları): "
            f"{np.flatnonzero(nat)[:5].tolist()}")
    return zaman


def muhur_kapisi(df: pd.DataFrame) -> pd.DataFrame:
    """Raise (never drop) if any row is on or after 2021-01-01 (the seal).

    The seal, a numeric time cell and an unparsed or missing time are all refused through the one
    gate :func:`zaman_kapisi`, so this is the same order as ``_cercevele``.  Messages carry a count
    or real row positions, never an index label, id, time or value.  Returns the frame with the
    parsed times so a caller does not parse again.  The gate's suppressed parses share one lock.
    The no-warning guarantee holds for a gate that runs in one thread; another thread's pandas work
    can still swap the process-wide filter list.  A cell with an unrecognised timezone is counted by
    its leading year (refused by position when that year is earlier), and a string date cell with
    no four-digit year is refused by position.
    """
    if len(df):
        df = df.copy()
        df["time_utc"] = zaman_kapisi(df["time_utc"])
    return df


def muhur_tara(df: pd.DataFrame) -> int:
    """The number of sealed rows in a raw frame, on coerced times only.

    A count-only helper for time cells: it returns the seal count and never quotes or drops a row.
    It does refuse a wrong shape: a duplicate ``time_utc`` column is named, a
    non-time dtype with no sealed date in its text is refused by name, and a numeric or unparsed
    time is refused through the same masks :func:`zaman_kapisi` uses — except that a sealed year in
    a text/bytes cell, or a Period/Interval cell's sealed endpoint, is counted here rather than
    refused (narrowed by a numeric cell and
    every non-date value, a ``timedelta`` included, are not counted).  The one gate
    :func:`zaman_kapisi` is what refuses a numeric or unparsed time, and this function no longer
    stands in for it anywhere; a caller that needs the gate's
    parse and refusals calls the gate, not this.  No id, time or value enters the number.  A frame
    with no ``time_utc`` column returns 0 (the caller's own column check names it).
    """
    if not len(df) or "time_utc" not in df.columns:
        return 0
    _zaman, muhurlu, _sayisal = _zaman_maskeleri(df["time_utc"])
    return int(muhurlu.sum())


def _cercevele(katalog, *, atilan: Optional[dict] = None,
               rapor: Optional[dict] = None, yan_koku=None) -> pd.DataFrame:
    """A normalised catalog as a DataFrame; magnitude-less rows dropped and named.

    Rows without a magnitude are left out of the source list and named through ``atilan`` (a
    caller-supplied dict): ``parametresiz`` are the rows with no location either and
    ``buyukluksuz`` the located rows.  CPTI15 v4.0 carries 112 + 45 = 157 such rows up to its
    2015 cutoff (the numbers measured on the full catalogue, 2026-09-30); neither group can be
    placed against the declared Mw threshold, so both are dropped and named, never silently lost.
    A row whose magnitude is present but not a number is a defect, not a missing parameter, and
    raises by name (event id and value); a row with a magnitude but no location cannot be a source
    plane and raises.  An ``event_id`` column is required (a frame
    without one raises), time cells are parsed with ``errors="coerce"``, a sealed (>= 2021) but
    unparseable time raises ``MuhurIhlali`` with a count only, every other unparsed or missing time
    raises ``BicimHatasi`` with positions only, and NaT rows are refused.  those positions are real row positions (``np.flatnonzero``), never index labels,
    and a numeric time cell (int/float) is refused by position instead of being read as
    nanoseconds since 1970.
    """
    if isinstance(katalog, pd.DataFrame):
        df = katalog.copy()
    else:
        df, katalog_raporu = katalog_oku(katalog, yan_koku=yan_koku)
        # carry the reader's per-catalogue report (acilan/acilmayan/atilan_kesim/
        # atilan_muhur) up to the caller instead of dropping it here; nothing is recomputed.
        if rapor is not None:
            rapor["katalog"] = katalog_raporu
    eksik = [c for c in _KATALOG_SUTUNLARI if c not in df.columns]
    if eksik:
        raise BicimHatasi(f"normalize katalogda eksik sütun: {eksik}")
    # a frame without ``event_id`` can no longer be named and used to
    # crash on the bad-magnitude path; it is a format error by name.
    if "event_id" not in df.columns:
        raise BicimHatasi(
            "normalize katalogda event_id sütunu yok; satırlar adlandırılamaz")
    ham_zaman = df["time_utc"]
    # the one gate
    # (count the seal, refuse numeric cells by position, then refuse unparsed or missing times by
    # position, never quoting a cell) parses the times and returns them, so the frame path and
    # ``muhur_kapisi`` share one order.
    df["time_utc"] = zaman_kapisi(ham_zaman)
    df = muhur_kapisi(df)
    ham = df["mag"]
    adlar = df["event_id"].astype(str)
    sayi = pd.to_numeric(ham, errors="coerce")
    # an empty magnitude is a missing parameter; a non-empty non-number is a defect
    bos = ham.isna() | (ham.astype(str).str.strip() == "")
    # Only finite magnitudes pass; ``inf``/``-inf``/``Infinity`` are
    # defects like any unparseable non-empty cell.
    kotu = ~bos & ~np.isfinite(sayi)
    if bool(kotu.any()):
        ornek = [(str(adlar.loc[i]), str(ham.loc[i])) for i in df.index[kotu]][:5]
        raise BicimHatasi(f"katalogda sayıya çevrilemeyen büyüklük (id, değer): {ornek}")
    df["mag"] = sayi
    mag_yok = df["mag"].isna()
    yer_yok = df["lat"].isna() | df["lon"].isna()
    konumsuz = ~mag_yok & yer_yok
    if bool(konumsuz.any()):
        kimlik = adlar.loc[konumsuz].tolist()
        raise BicimHatasi(
            f"{int(konumsuz.sum())} katalog satırında büyüklük var ama konum yok: {kimlik[:5]}")
    if bool(mag_yok.any()):
        parametresiz = adlar.loc[mag_yok & yer_yok].tolist()
        buyukluksuz = adlar.loc[mag_yok & ~yer_yok].tolist()
    else:
        parametresiz, buyukluksuz = [], []
    if atilan is not None:
        atilan["parametresiz"] = parametresiz
        atilan["buyukluksuz"] = buyukluksuz
    temiz = df.loc[~mag_yok].reset_index(drop=True)
    # the ids ride along for a caller that only sees the returned frame
    temiz.attrs["parametresiz"] = parametresiz
    temiz.attrs["buyukluksuz"] = buyukluksuz
    return temiz


def kaynak_listesi(katalog, *, kesim=KESIM, devir=None, pencere=None,
                   atilan: Optional[dict] = None,
                   rapor: Optional[dict] = None, yan_koku=None) -> pd.DataFrame:
    """The K9 source list: seal-clean, threshold-respecting, cutoff/handover-aware.

    Without ``pencere`` this is the **calibration** list: every event at or below ``kesim``
    (default the 2015-12-31 cutoff; ``kesim=None`` drops the upper cutoff and leaves only the seal
    and the optional ``devir``).  With ``pencere`` this is a **blind-window** list: the upper bound is
    the window start, not the 2015 cutoff, because the cumulative replay stops at the handover and
    a window must be able to add 2016-2020 events; only ``devir < t < pencere`` enters,
    through :func:`knotenlinie.kanal.tektonik_devir.pencere_kaynaklari`.  The seal gate re-runs before
    the frame is returned.

    Rows without a magnitude cannot be placed against the declared threshold; they are dropped by
    :func:`_cercevele` and named in the optional ``atilan`` dict (``parametresiz``/
    ``buyukluksuz``), so every user of this list applies one drop rule.
    """
    from knotenlinie.kanal.tektonik_devir import DEVIR, pencere_kaynaklari

    df = _cercevele(katalog, atilan=atilan, rapor=rapor, yan_koku=yan_koku)
    df = muhur_kapisi(df)
    # the rows the narrower cutoff removes on top of what the reader already cut at the
    # declared KESIM.  ``katalog_oku`` truncates to KESIM, so this counts only the additional
    # (kesim, KESIM] band; a caller-built frame with no reader report counts every row past kesim.
    kesim_ustu = 0
    if pencere is not None:
        df = pencere_kaynaklari(df.reset_index(drop=True), pencere,
                                devir=devir if devir is not None else DEVIR)
    else:
        if kesim is not None:
            esik = kesim_ani(kesim)
            onceki = len(df)
            df = df.loc[df["time_utc"] <= esik]
            kesim_ustu = onceki - len(df)
        if devir is not None:
            esik = _an(devir)
            df = df.loc[df["time_utc"] > esik]
    df = df.loc[df["mag"] >= float(KAYNAK_ESIK_MW)]
    df = muhur_kapisi(df)
    if rapor is not None:
        rapor["kesim_ustu"] = int(kesim_ustu)
        rapor["kesim_kullanilan"] = (
            None if kesim is None else kesim_ani(kesim).isoformat())
        rapor["kesim_dar"] = bool(kesim is not None and kesim_ani(kesim) < _an(KESIM))
    return df.sort_values("time_utc", kind="mergesort").reset_index(drop=True)


# --- one source plane per event (K9) ------------------------------------------------------

def mesafe_km(lat1, lon1, lat2, lon2) -> np.ndarray:
    """Great-circle distance in km (spherical Earth, R = 6371.0 km)."""
    R = 6371.0
    p1 = np.deg2rad(np.asarray(lat1, dtype=np.float64))
    p2 = np.deg2rad(np.asarray(lat2, dtype=np.float64))
    dp = p2 - p1
    dl = np.deg2rad(np.asarray(lon2, dtype=np.float64) - np.asarray(lon1, dtype=np.float64))
    a = np.sin(dp / 2.0) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2.0) ** 2
    return 2.0 * R * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def _aci_sutunu(fay_tablosu: pd.DataFrame, adaylar: Sequence[str]) -> Optional[str]:
    for ad in adaylar:
        if ad in fay_tablosu.columns:
            return ad
    return None


def kaynak_plani(olay, fay_tablosu: pd.DataFrame) -> Optional[Dict[str, object]]:
    """The v0 **declared** source plane for one event (K9), or None past the distance cutoff.

    The nearest DISS fault within :data:`MESAFE_KESIMI_KM` carries the event's own magnitude and the
    WC94 dimensions; its own central strike/dip/rake and vectors are used, which removes the GCMT
    nodal-plane ambiguity.  The rectangle is placed at the fault centroid and its upper edge is
    lifted up-dip by ``(W/2) sin(dip)`` from the central depth.  No file is read here; the seal and
    the cutoff are re-checked on the event itself.
    """
    # Neither the event's time nor any cell text enters a message;
    # the boundary is the declared constant, and the count is the only number.  ``_an`` refuses a
    # naive or unparseable instant without quoting it.
    zaman = _an(olay["time_utc"])
    if zaman >= _an(MUHUR_BASI):
        raise MuhurIhlali(
            f"1 olay {MUHUR_BASI} ve sonrasında; mühür kaynak düzlemi kurmaz")
    if zaman > _an(KESIM):
        raise KesimIhlali("1 olay 2015 kesiminden sonra; kalibrasyon kaynağı olamaz")

    A_km2, L_km, W_km, M0_Nm, D_m = kaynak_geometri(float(olay["mag"]))
    d = mesafe_km(float(olay["lat"]), float(olay["lon"]),
                  fay_tablosu["centroid_lat"].to_numpy(), fay_tablosu["centroid_lon"].to_numpy())
    i = int(np.argmin(d))
    if float(d[i]) > MESAFE_KESIMI_KM:
        return None

    fay = fay_tablosu.iloc[i]
    c_strike = _aci_sutunu(fay_tablosu, ("strike_central_deg", "strike_min_stated_deg"))
    c_dip = _aci_sutunu(fay_tablosu, ("dip_central_deg", "dip_min_deg"))
    c_rake = _aci_sutunu(fay_tablosu, ("rake_central_deg", "rake_min_stated_deg"))
    if not (c_strike and c_dip and c_rake):
        raise BicimHatasi("fay tablosunda merkez doğrultu/eğim/atım açı sütunları yok")
    strike = float(fay[c_strike])
    dip = float(fay[c_dip])
    rake = float(fay[c_rake])
    derinlik_km = float(fay["depth_central_km"]) if "depth_central_km" in fay_tablosu.columns else 8.0
    W_m = W_km * 1e3
    ust_m = max(0.0, derinlik_km * 1e3 - 0.5 * W_m * np.sin(np.deg2rad(dip)))
    return {
        "kaynak_id": str(olay.get("event_id", "bilinmeyen")),
        "fault_id": str(fay["id"]),
        "model_id": "wc94",
        "mesafe_km": float(d[i]),
        "A_km2": A_km2,
        "M0_Nm": M0_Nm,
        "kayma_m": D_m,
        "dogrultu_deg": strike,
        "egim_deg": dip,
        "kayma_deg": rake,
        "uzunluk_m": L_km * 1e3,
        "genislik_m": W_m,
        "ust_derinlik_m": ust_m,
        "kaynak_lat": float(fay["centroid_lat"]),
        "kaynak_lon": float(fay["centroid_lon"]),
        "olay_lat": float(olay["lat"]),
        "olay_lon": float(olay["lon"]),
        "olay_zaman": zaman,
    }


def wc94_saglayici(fay_tablosu: pd.DataFrame):
    """A slip-model provider yielding the single WC94 model per event (no SRCMOD mixing)."""
    def saglayici(olay) -> List[Dict[str, object]]:
        plan = kaynak_plani(olay, fay_tablosu)
        return [] if plan is None else [plan]
    return saglayici


# --- SRCMOD adapter (DETERMINED-PENDING until the browser download lands) ------------------

def srcmod_oku(dizin) -> Dict[str, object]:
    """SRCMOD finite-fault slip models keyed by event; raises until the product is downloaded.

    The adapter interface exists so K9 routes per event when the data lands.  Today it
    refuses to open any file whose name carries a year >= 2016 and then raises :class:`VeriYok`
    naming the directory; parsing is DETERMINED-PENDING and no format is
    guessed.  No fallback silently mixes a SRCMOD model with the WC94 model for the same event.

    Requirement: a SRCMOD file name carrying any year >= 2016 (for example
    ``s2016AMATRI01.fsp``) must be refused **unopened** through :func:`yil_kapisi` before any
    parser runs.  This adapter never opens a sealed name and has no parser to reach.
    """
    dizin = os.fspath(dizin)
    if not os.path.isdir(dizin):
        raise VeriYok(
            f"SRCMOD dizini yok: {dizin} (tarayıcıyla elle indirilir)"
        )
    for ad in sorted(os.listdir(dizin)):
        katalog_yil_kapisi(os.path.join(dizin, ad))
    raise VeriYok(
        f"SRCMOD dizini var ama ayrıştırıcı henüz yok: {dizin}; biçim henüz "
        "sabitlenmedi (DETERMINED-PENDING)"
    )


def kaynak_slip_saglayici(kaynaklar, fay_tablosu: pd.DataFrame, *, mod: str = "wc94",
                          srcmod_dizin=None):
    """Route one event to exactly one kind of slip model.

    ``mod='wc94'`` is the only variant until SRCMOD lands; ``mod='srcmod'`` requires the directory
    and raises :class:`VeriYok` otherwise.  The event allow-list is the already cutoff-filtered
    source list, so a slip model whose event is not in that list can never enter calibration
    (the model's event date, not its magnitude, decides).
    """
    if mod == "wc94":
        return wc94_saglayici(fay_tablosu)
    if mod == "srcmod":
        modeller = srcmod_oku(srcmod_dizin if srcmod_dizin is not None else "")
        izin = {str(k.get("event_id", "")) for k in _kaynak_kayitlari(kaynaklar)}

        def saglayici(olay):
            eid = str(olay.get("event_id", ""))
            if eid not in izin:
                return []
            return list(modeller.get(eid) or [])

        return saglayici
    raise ValueError(f"bilinmeyen kaynak modu {mod!r}; beklenen 'wc94' ya da 'srcmod'")


def _kaynak_kayitlari(kaynaklar) -> List[dict]:
    """The source list as plain records, from a DataFrame or an iterable of mappings."""
    if kaynaklar is None:
        return []
    if isinstance(kaynaklar, pd.DataFrame):
        return kaynaklar.to_dict("records")
    return [dict(k) for k in kaynaklar]
