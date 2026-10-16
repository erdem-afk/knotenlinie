#!/usr/bin/env python3
"""Build the <=2015 calibration layout under <data>/ from the files scripts/indir.py wrote.

    python scripts/kesik_2015.py <data>          (default: $KNOTENLINIE_DATA, else <repo>/data)

What it writes (copies, never links; existing targets are kept unless --yeniden):

  <data>/kesik-2015/horus/horus_YYYY.txt        HORUS 1960-2015, copied from deprem/horus/
  <data>/kesik-2015/CPTI15_v4.0_le2015.csv     the CPTI15 <=2015 split, copied from deprem/cpti15/
                                               (its binding sidecar stays in yan-kayit/cpti15/; the copy
                                               has the same sha256, so the sidecar still binds it)
  <data>/kesik-2015/gcmt_le2015.ndk             GCMT records dated 2015-12-31 or earlier, cut from
                                               deprem/gcmt/jan76_dec20.ndk (5-line NDK records)
  <data>/kesik-2015/iside/iside_YYYY.txt        ISIDe 1985-2015 (EEPAS only), copied from deprem/iside/
                                               when that source was downloaded
  <data>/diss320/{iss320,csspln320,csstop320}.geojson   copied from kuvvet/fay/diss320/

The seal holds throughout: a record dated 2021-01-01 or later stops the script (it is never written
or printed); rows dated 2016-2020 are dropped and only counted.  Nothing is downloaded.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
KESIM_YILI = 2015
MUHUR_YILI = 2021
HORUS_YILLARI = range(1960, KESIM_YILI + 1)
DISS_KATMANLARI = ("iss320", "csspln320", "csstop320")


class MuhurIhlali(RuntimeError):
    """A record dated on or after 2021-01-01 was found; nothing more is written."""


def _sha256(yol: Path) -> str:
    h = hashlib.sha256()
    with yol.open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def _kopyala(kaynak: Path, hedef: Path, yeniden: bool) -> str:
    if not kaynak.is_file():
        raise FileNotFoundError(f"girdi yok: {kaynak} (önce scripts/indir.py)")
    if hedef.exists() and not yeniden:
        return "var"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_name(hedef.name + ".part")
    shutil.copyfile(kaynak, gecici)
    if _sha256(gecici) != _sha256(kaynak):
        gecici.unlink()
        raise OSError(f"kopya sha256 tutmadı: {hedef}")
    os.replace(gecici, hedef)
    return "kopyalandı"


def gcmt_kes(kaynak: Path, hedef: Path, yeniden: bool) -> dict:
    """Keep the 5-line NDK records whose line-1 year is <= 2015; count the rest (2016-2020)."""
    if hedef.exists() and not yeniden:
        return dict(durum="var")
    if not kaynak.is_file():
        raise FileNotFoundError(f"girdi yok: {kaynak} (önce scripts/indir.py --only gcmt)")
    satirlar = kaynak.read_bytes().splitlines(keepends=True)
    if len(satirlar) % 5:
        raise ValueError(f"{kaynak.name}: satır sayısı 5'in katı değil")
    tutulan, atilan = [], 0
    for i in range(0, len(satirlar), 5):
        blok = satirlar[i:i + 5]
        yil = int(blok[0][5:9].decode("ascii"))
        if yil >= MUHUR_YILI:
            raise MuhurIhlali(f"{kaynak.name}: {MUHUR_YILI}+ kayıt var; dosya yazılmadı")
        if yil <= KESIM_YILI:
            tutulan.append(b"".join(blok))
        else:
            atilan += 1
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_name(hedef.name + ".part")
    gecici.write_bytes(b"".join(tutulan))
    os.replace(gecici, hedef)
    return dict(durum="kesildi", kayit=len(tutulan), atilan_2016_2020=atilan)


def horus_kopyala(veri: Path, yeniden: bool) -> dict:
    for y in HORUS_YILLARI:
        k = veri / "deprem" / "horus" / f"horus_{y}.txt"
        if not k.is_file():
            continue          # a year with no event in the zip has no file
        _kopyala(k, veri / "kesik-2015" / "horus" / k.name, yeniden)
    yazilan = sorted(p.name for p in (veri / "kesik-2015" / "horus").glob("horus_*.txt"))
    if not yazilan:
        raise FileNotFoundError("HORUS yıl dosyası yok (önce scripts/indir.py --only horus)")
    return dict(dosya=len(yazilan), ilk=yazilan[0], son=yazilan[-1])


def iside_kopyala(veri: Path, yeniden: bool) -> dict:
    kaynak = veri / "deprem" / "iside"
    if not kaynak.is_dir():
        return dict(durum="atlandı (deprem/iside yok; yalnız EEPAS kullanır)")
    n = 0
    for y in range(1985, KESIM_YILI + 1):
        k = kaynak / f"iside_{y}.txt"
        if k.is_file():
            _kopyala(k, veri / "kesik-2015" / "iside" / k.name, yeniden)
            n += 1
    return dict(dosya=n)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?", default=os.environ.get("KNOTENLINIE_DATA", str(KOK / "data")))
    ap.add_argument("--yeniden", action="store_true", help="var olan hedefleri yeniden yaz")
    a = ap.parse_args(argv)
    veri = Path(a.data)
    rapor = {}
    rapor["horus"] = horus_kopyala(veri, a.yeniden)
    rapor["cpti15"] = _kopyala(veri / "deprem" / "cpti15" / "CPTI15_v4.0_le2015.csv",
                               veri / "kesik-2015" / "CPTI15_v4.0_le2015.csv", a.yeniden)
    rapor["gcmt"] = gcmt_kes(veri / "deprem" / "gcmt" / "jan76_dec20.ndk",
                             veri / "kesik-2015" / "gcmt_le2015.ndk", a.yeniden)
    rapor["iside"] = iside_kopyala(veri, a.yeniden)
    for katman in DISS_KATMANLARI:
        rapor[katman] = _kopyala(veri / "kuvvet" / "fay" / "diss320" / f"{katman}.geojson",
                                 veri / "diss320" / f"{katman}.geojson", a.yeniden)
    for k, v in rapor.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
