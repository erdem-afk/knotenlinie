#!/usr/bin/env python3
"""Tests for scripts/muhur.py on synthetic fixtures (no real catalogue rows). run: python -m pytest tests/scripts"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[2] / "scripts" / "muhur.py"

NDK_EVENT = (
    "PDE  {date} 01:20:05.4  13.78  -88.78 193.1 5.0 0.0 SYNTHETIC EVENT         \n"
    "C000000000000A B:  0    0  40 S:  0    0   0 M:  0    0   0 CMT: 1 TRIHD:  0.6\n"
    "CENTROID:     -0.3 0.9  13.76 0.06  -89.08 0.09 162.8 12.5 FREE S-20050322125201\n"
    "23  0.838 0.201 -0.005 0.231 -0.833 0.270  1.050 0.121 -0.369 0.161  0.044 0.240\n"
    "V10   1.581 56  12  -0.537 23 140  -1.044 24 241   1.312   9 29  142 133 72   66\n"
)
FDSN_HEAD = "#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|MagAuthor|EventLocationName|EventType\n"


def fdsn_row(t: str) -> str:
    return f"1|{t}|42.8|13.2|10|SYN|SYN|SYN|1|ML|2.0|SYN|SYNTHETIC|earthquake\n"


HORUS_HEAD = "Year\tMo\tDa\tHo\tMi\tSe\tLat\tLon\tDepth\tMw\tsigMw\tGeo-Ita\tGeo-CPTI15\tEv. type\tIside n.\t\n"


def horus_row(y: int) -> str:
    return f"     {y}.0000000000\t  12.0\t  31.0\t  1.0\t  2.0\t  3.0\t  42.8\t  13.2\t  10.0\t  2.1\t  0.2\t*\t*\t \t \t\n"


class SealCheck(unittest.TestCase):
    def run_on(self, files: dict[str, str]) -> subprocess.CompletedProcess:
        tmp = Path(tempfile.mkdtemp())
        for rel, text in files.items():
            p = tmp / "deprem" / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        return subprocess.run([sys.executable, TOOL, tmp], capture_output=True, text=True)

    def test_clean_formats_pass(self):
        r = self.run_on({
            "gcmt/cat.ndk": NDK_EVENT.format(date="1976/01/01") + NDK_EVENT.format(date="2020/12/31"),
            "iside/2020.txt": FDSN_HEAD + fdsn_row("2020-12-31T23:59:59.000000"),
            "isc-gem/cat.csv": "time,latitude,mag\n1904-04-04T10:02:34.560Z,41.8,7.0\n",
            "cpti15/cat.csv": "Year,Mo,Da,MwDef\n1000,,,5.0\n2020,12,31,4.1\n",
            "horus/horus_2020.txt": HORUS_HEAD + horus_row(2020),
        })
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("seal clean: 5 files, 7 records", r.stdout)

    def test_each_format_catches_2021(self):
        cases = {
            "gcmt/cat.ndk": NDK_EVENT.format(date="2021/01/01"),
            "iside/x.txt": FDSN_HEAD + fdsn_row("2021-01-01T00:00:00.000000"),
            "isc-gem/cat.csv": "time,latitude,mag\n2021-01-01T00:00:00.000Z,41.8,7.0\n",
            "cpti15/cat.csv": "Year,Mo,Da,MwDef\n2021,1,1,4.1\n",
            "horus/horus_2021.txt": HORUS_HEAD + horus_row(2021),
        }
        for rel, text in cases.items():
            with self.subTest(rel):
                r = self.run_on({rel: text})
                self.assertEqual(r.returncode, 1)
                self.assertIn("sealed=     1", r.stdout)

    def test_output_never_contains_a_record(self):
        r = self.run_on({"iside/x.txt": FDSN_HEAD + fdsn_row("2022-05-05T00:00:00.000000")})
        self.assertEqual(r.returncode, 1)
        self.assertNotIn("2022-05-05", r.stdout + r.stderr)
        self.assertNotIn("SYNTHETIC", r.stdout + r.stderr)

    def test_unknown_and_unreadable_fail_closed(self):
        for files in (
            {"x/cat.zip": "PK"},
            {"x/cat.csv": "lat,lon\n1,2\n"},
            {"x/empty.txt": ""},
            {"x/cat.csv": "time,lat\nnot-a-date,1\n"},
        ):
            with self.subTest(files):
                self.assertEqual(self.run_on(files).returncode, 1)

    def test_forces_side_is_not_scanned(self):
        tmp = Path(tempfile.mkdtemp())
        (tmp / "kuvvet").mkdir()
        (tmp / "kuvvet" / "eop.csv").write_text("time,x\n2026-01-01,1\n")
        r = subprocess.run([sys.executable, TOOL, tmp], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
