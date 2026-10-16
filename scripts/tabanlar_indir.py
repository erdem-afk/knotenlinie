#!/usr/bin/env python3
"""Download the published base-model forecasts the comparisons score against, and check each file's
recorded SHA-256 and size.  No earthquake catalogue is involved.

    python scripts/tabanlar_indir.py [<data>] [--only italya|kaliforniya]

* Italy (CSEP Italy 2010 experiment, pinned commit): the files listed in ``records/H/TABANLAR.json``
  (``indirmeler``: url, sha256, byte, data-root-relative ``dosya``) -> ``<data>/tabanlar/``.
* California (HKJ07 and the RELM polygons, pyCSEP artifacts) -> ``<data>/kaliforniya/hkj07/``.

A file that already exists with the recorded SHA-256 is kept; a mismatch (existing or downloaded) is an
error and the bad download is removed.  The default data root is ``$KNOTENLINIE_DATA``, else ``<repo>/data``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
UA = "knotenlinie (+https://github.com/erdem-afk/knotenlinie)"
PYCSEP = "https://raw.githubusercontent.com/SCECcode/pycsep/main/csep/artifacts"

#: HKJ07 (Helmstetter, Kagan & Jackson 2007) and RELM polygons as distributed with pyCSEP (BSD-3-Clause).
#: Sizes and SHA-256 from the project record of the 2026-10-12 download (default branch, now ``main``;
#: a changed upstream file is refused by the SHA-256 check).
KALIFORNIYA = [
    ("Regions/Polygons/California/RELMTestingPolygon.txt", 192,
     "44d7fa59e3bfe98309e1d8eb1678a299d758e685db7abc1bd4210b9278e5fda5"),
    ("Regions/Polygons/California/RELMCollectionPolygon.txt", 228,
     "03346a49b7b5899a536b2083e8b0debc5964e485f3f021e1083bf2e12e118a77"),
    ("Regions/RELMTestArea.dat", 407146,
     "d4133608f70a52d2faed002483a492231b5f2dcd2ff805d7fe68b2d1fd3117a7"),
    ("ExampleForecasts/GriddedForecasts/helmstetter_et_al.hkj-fromXML.dat", 21417416,
     "85fc89102218f0f4183faacc7428f846e792874c1822090bddb76e35b3c1ccff"),
    ("ExampleForecasts/GriddedForecasts/helmstetter_et_al.hkj.aftershock-fromXML.dat", 21417416,
     "7b3cf1ffc13633be661a391c5e12415b5bc60d3ccd36d26ec26633ab3d285c14"),
]


class SHAUyusmazligi(ValueError):
    """A file does not match its recorded SHA-256 or size."""


def _sha256(yol: Path) -> str:
    h = hashlib.sha256()
    with yol.open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


def indir(url: str, hedef: Path, sha256: str, byte=None, tries: int = 4) -> str:
    """Fetch ``url`` to ``hedef`` atomically and check its SHA-256 (and size when given)."""
    if hedef.exists():
        if _sha256(hedef) != sha256:
            raise SHAUyusmazligi(f"{hedef}: var olan dosyanın sha256'sı kayıtla uyuşmuyor")
        return "var"
    hedef.parent.mkdir(parents=True, exist_ok=True)
    gecici = hedef.with_name(hedef.name + ".part")
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}),
                                        timeout=300) as r, gecici.open("wb") as f:
                while blok := r.read(1 << 20):
                    f.write(blok)
            break
        except (urllib.error.URLError, TimeoutError):
            gecici.unlink(missing_ok=True)
            if i == tries - 1:
                raise
            time.sleep(5 * 2 ** i)
    if (byte is not None and gecici.stat().st_size != byte) or _sha256(gecici) != sha256:
        gecici.unlink(missing_ok=True)
        raise SHAUyusmazligi(f"{url}: indirilen dosya kayıtlı sha256/boyutla uyuşmuyor")
    os.replace(gecici, hedef)
    return "indirildi"


def italya(veri: Path, kayit: Path) -> dict:
    d = json.loads(kayit.read_text(encoding="utf-8"))
    sonuc = {}
    for x in d["indirmeler"]:
        sonuc[x["ad"]] = indir(x["url"], veri / x["dosya"], x["sha256"], x.get("byte"))
    return sonuc


def kaliforniya(veri: Path) -> dict:
    sonuc = {}
    for yol, byte, sha in KALIFORNIYA:
        ad = yol.rsplit("/", 1)[1]
        sonuc[ad] = indir(f"{PYCSEP}/{yol}", veri / "kaliforniya" / "hkj07" / ad, sha, byte)
    return sonuc


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?", default=os.environ.get("KNOTENLINIE_DATA", str(KOK / "data")))
    ap.add_argument("--only", choices=["italya", "kaliforniya"])
    ap.add_argument("--kayit", type=Path,
                    default=Path(os.environ.get("KNOTENLINIE_RECORDS", KOK / "records")) / "H" / "TABANLAR.json")
    a = ap.parse_args(argv)
    veri = Path(a.data)
    if a.only in (None, "italya"):
        for k, v in italya(veri, a.kayit).items():
            print(f"italya {k}: {v}")
    if a.only in (None, "kaliforniya"):
        for k, v in kaliforniya(veri).items():
            print(f"kaliforniya {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
