#!/usr/bin/env python3
"""Seal check for the earthquake side: no earthquake record dated 2021-01-01 or later.

Scans every file under <data>/deprem/ and fails if any earthquake record is dated on or after
2021-01-01, if a file's format is not recognised, or if a record's date cannot be parsed. It prints
counts only, never a record, so a sealed row never reaches a terminal or a transcript.

Formats (detected from the extension and the header line):
  .ndk               Global CMT NDK, 5 lines per event, date in line 1 columns 6-15 (YYYY/MM/DD)
  FDSN text          '|'-separated, header starts with '#EventID', column 'Time' (ISO)
  CSV with 'time'    ISO timestamp column (USGS ComCat export)
  CSV with 'Year'    year / month / day columns (CPTI15)
  TSV with 'Year'    tab-separated, first column 'Year' as a float string (HORUS, one file per year)

It also fails if a dataset placed under the seal is present anywhere in the data directory
(SEALED_DATASETS). Those are matched by path only and never opened.

usage: muhur.py <data-dir>        exit 0 = clean, 1 = sealed or unreadable data found, 2 = usage
"""
import csv
import sys
from pathlib import Path

SEAL_YEAR = 2021  # records dated >= 2021-01-01 are sealed
SIDE = "deprem"
# Datasets placed under the seal: GNSS velocity fields that
# cover the years after 2015 and may carry post-2021 observations. Present = fail; never opened.
SEALED_DATASETS = ("zenodo-10417518", "zenodo-17120300", "NASA4SHA")


def _year(text: str) -> int:
    return int(text.strip()[:4])


def check_ndk(path: Path) -> tuple[int, int, int]:
    rows = sealed = bad = 0
    with path.open(encoding="ascii", errors="replace") as f:
        for i, line in enumerate(f):
            if i % 5:
                continue
            rows += 1
            try:
                if _year(line[5:15]) >= SEAL_YEAR:
                    sealed += 1
            except ValueError:
                bad += 1
    return rows, sealed, bad


def check_fdsn_text(path: Path) -> tuple[int, int, int]:
    rows = sealed = bad = 0
    with path.open(encoding="utf-8", errors="replace") as f:
        col = f.readline().lstrip("#").strip().split("|").index("Time")
        for line in f:
            if not line.strip():
                continue
            rows += 1
            try:
                if _year(line.split("|")[col]) >= SEAL_YEAR:
                    sealed += 1
            except (ValueError, IndexError):
                bad += 1
    return rows, sealed, bad


def check_csv(path: Path, field: str) -> tuple[int, int, int]:
    rows = sealed = bad = 0
    with path.open(encoding="utf-8", errors="replace", newline="") as f:
        for rec in csv.DictReader(f):
            rows += 1
            try:
                if _year(rec[field]) >= SEAL_YEAR:
                    sealed += 1
            except (ValueError, KeyError, TypeError):
                bad += 1
    return rows, sealed, bad


def check_tsv_year(path: Path) -> tuple[int, int, int]:
    rows = sealed = bad = 0
    with path.open(encoding="utf-8", errors="replace") as f:
        col = [c.strip() for c in f.readline().split("\t")].index("Year")
        for line in f:
            if not line.strip():
                continue
            rows += 1
            try:
                if int(float(line.split("\t")[col])) >= SEAL_YEAR:
                    sealed += 1
            except (ValueError, IndexError):
                bad += 1
    return rows, sealed, bad


def check_file(path: Path) -> tuple[str, int, int, int]:
    if path.suffix == ".ndk":
        return ("ndk", *check_ndk(path))
    if path.suffix not in (".txt", ".csv"):
        return ("unknown", 0, 0, 1)
    with path.open(encoding="utf-8", errors="replace") as f:
        head = f.readline()
    if head.startswith("#EventID") and "|Time|" in head:
        return ("fdsn-text", *check_fdsn_text(path))
    if "\t" in head and "Year" in [c.strip() for c in head.split("\t")]:
        return ("tsv-year", *check_tsv_year(path))
    fields = next(csv.reader([head]), [])
    if "time" in fields:
        return ("csv-time", *check_csv(path, "time"))
    if "Year" in fields:
        return ("csv-year", *check_csv(path, "Year"))
    return ("unknown", 0, 0, 1)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    root = Path(sys.argv[1]) / SIDE
    files = sorted(p for p in root.rglob("*") if p.is_file() and not p.name.startswith("."))
    failed = False
    total = 0
    for p in files:
        fmt, rows, sealed, bad = check_file(p)
        total += rows
        status = "ok" if not (sealed or bad) else "FAIL"
        failed |= status == "FAIL"
        print(f"{status:4} {fmt:9} rows={rows:>8} sealed={sealed:>6} unreadable={bad:>4}  {p.relative_to(root)}")
    for p in sorted(Path(sys.argv[1]).rglob("*")):
        if any(s.lower() in p.name.lower() for s in SEALED_DATASETS):
            failed = True
            print(f"FAIL sealed-dataset present (not opened)  {p.relative_to(sys.argv[1])}")
    verdict = "FAIL" if failed else "clean"
    print(f"seal {verdict}: {len(files)} files, {total} records, cut {SEAL_YEAR}-01-01, under {root}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
