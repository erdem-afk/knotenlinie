#!/usr/bin/env python3
"""Download the open earthquake catalogues and the DISS 3.2.0 fault sources into <data>/ with the
earthquake seal applied (no record dated 2021-01-01 or later is ever written). Standard library only,
except openpyxl for the CPTI15 spreadsheet.

Layout:  <data>/deprem/...   earthquake side, sealed from 2021-01-01; filtered while streaming, so a
                             sealed record never reaches disk and is never printed (only counted)
         <data>/kuvvet/...   fault geometry (DISS 3.2.0; outside the catalogue seal scan)
         <data>/MANIFEST.jsonl   one line per written file: source, urls, bytes, sha256, rows kept/dropped

usage:  indir.py <data> [--only id,id]   fetch the fixed sources (existing files are kept), then seal check
        indir.py --list

Server-side filters: GCMT is a fixed file ending in December 2020 (jan76_dec20.ndk); ISIDe queries end at
2020-12-31; DISS 3.2.0 features are filtered on ``latesteq``. HORUS has no server-side filter: the zip is
read in memory and its rows from 2021 on are dropped before anything is written (only counted).

The latest MANIFEST.jsonl row for a path is authoritative (a refetch hides an earlier row).
"""
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

SEAL = dt.datetime(2021, 1, 1)
LAST = "2020-12-31T23:59:59"
UA = "knotenlinie (+https://github.com/erdem-afk/knotenlinie)"
TLS = ssl.create_default_context()
DISS_WFS = "https://services.seismofaults.eu/DISS320/ows"
WFS_SAYFA = 1000  # WFS 1.1.0 pages with maxFeatures (count is a WFS 2.0 parameter and is ignored here)
LATESTEQ_BICIMLER = ("%d %b %Y", "%d %B %Y", "%d/%m/%Y", "%d-%b-%Y", "%b %Y", "%B %Y", "%Y")

SOURCES = {
    # --- earthquake side (sealed from 2021-01-01) ---
    "gcmt": dict(side="deprem", kind="ndk", license="GCMT, cite Dziewonski et al. 1981 and Ekström et al. 2012",
                 urls=["https://www.ldeo.columbia.edu/~gcmt/projects/CMT/catalog/jan76_dec20.ndk"],
                 dest="gcmt/jan76_dec20.ndk"),
    "cpti15": dict(side="deprem", kind="cpti", license="CC-BY 4.0",
                   urls=["https://emidius.mi.ingv.it/CPTI15-DBMI15/data/CPTI15_v4.0.xlsx"],
                   dest="cpti15/CPTI15_v4.0_le2015.csv",
                   note="<=2015 split only; rows 2016-2020 and 2021+ are dropped before disk; the sibling "
                        ".json sidecar binds the file to its source sha"),
    "iside": dict(side="deprem", kind="ingv", license="CC-BY 4.0 (INGV)", start=1985, dest="iside"),
    "horus": dict(side="deprem", kind="horus", license="CC BY 4.0 (INGV; Lolli et al. 2020, 10.1785/0220200148)",
                  urls=["http://horus.bo.ingv.it/DataFolder/HORUS_Ita_Catalog.zip"], uye="HORUS_Ita_Catalog.txt",
                  dest="horus",
                  note="homogenized Mw with the random second decimal on ISIDe ML/Md (the authors' version "
                       "for statistics); one zip opened in memory, rows from 2021 dropped before disk and "
                       "only counted, one file per year so the ISIDe year gate applies"),
    # --- fault geometry ---
    "diss320": dict(side="kuvvet", kind="wfs", dest="fay/diss320",
                    license="DISS/INGV terms (CC BY 4.0), citation required",
                    base=DISS_WFS, workspace="DISS320",
                    typelayers=["iss320", "csspln320", "csstop320", "dss320", "subdcnt320", "subdzon320"],
                    note="DISS 3.2.0 fault sources as OGC WFS GeoJSON. Placed under kuvvet/, not "
                         "deprem/: it is fault geometry dated by version, not a catalogue, and "
                         "scripts/muhur.py recognises only catalogue formats, so a .geojson under deprem/ "
                         "would make the seal check fail closed and halt later downloads. The "
                         "latesteq filter in fetch_wfs is the byte-level seal for the one "
                         "earthquake-dated field",
                    beklenen_sayilar={"iss320": 126, "csspln320": 167, "csstop320": 167, "dss320": 35,
                                      "subdcnt320": 156, "subdzon320": 3}),
}


# ---------------------------------------------------------------- plumbing
def get(url: str, tries: int = 5):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=300, context=TLS)
        except urllib.error.HTTPError as e:
            if e.code in (204, 404) or i == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
        time.sleep(5 * 2 ** i)


class Out:
    """Atomic file writer that hashes what it writes."""

    def __init__(self, path: Path):
        self.path, self.part = path, path.with_name(path.name + ".part")
        path.parent.mkdir(parents=True, exist_ok=True)
        self.f, self.h, self.n = self.part.open("wb"), hashlib.sha256(), 0

    def write(self, b: bytes):
        self.f.write(b)
        self.h.update(b)
        self.n += len(b)

    def abort(self):
        """Close and delete the .part file; no final file and no MANIFEST row survive.

        The unlink runs in a finally so a close error never leaves the .part behind (and never masks
        the original error)."""
        try:
            self.f.close()
        finally:
            self.part.unlink(missing_ok=True)

    def close(self) -> dict:
        self.f.close()
        self.part.rename(self.path)
        return {"bytes": self.n, "sha256": self.h.hexdigest()}


def record(data: Path, src_id: str, path: Path, info: dict, **extra):
    s = SOURCES.get(src_id, {})
    row = {"source": src_id, "side": s.get("side", "kuvvet"), "path": str(path.relative_to(data)),
           "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "license": s.get("license"), "note": s.get("note"), **info, **extra}
    with (data / "MANIFEST.jsonl").open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"  {row['path']}  {info['bytes'] / 1e6:.1f} MB" +
          (f"  kept={extra['rows_kept']} dropped={extra['rows_dropped']}" if "rows_kept" in extra else ""))


def manifest_son_satirlar(data: Path) -> dict:
    """The latest MANIFEST.jsonl row per path (the latest row is authoritative)."""
    yol = data / "MANIFEST.jsonl"
    son = {}
    if not yol.exists():
        return son
    for line in yol.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        son[r["path"]] = r
    return son


def _sha256_dosya(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
    return h.hexdigest()


def year_of(text: str) -> int:
    return int(text.strip()[:4])


# ---------------------------------------------------------------- seal helpers (DISS latesteq)
def latesteq_tarih(metin):
    """A DISS `latesteq` string as a date, or None.

    The field is free-form ('21 May 2003', 'Unknown', '530-'), so the whole string must match one of
    the declared formats; a year is never guessed from the first four characters.
    """
    if metin is None:
        return None
    metin = str(metin).strip()
    if not metin:
        return None
    for bicim in LATESTEQ_BICIMLER:
        try:
            return dt.datetime.strptime(metin, bicim).date()
        except ValueError:
            continue
    return None


def latesteq_muhur(ozellikler):
    """Split GeoJSON features on the earthquake seal (no record dated 2021-01-01 or later).

    A feature whose `latesteq` is on or after 2021-01-01 is dropped and only counted; an
    unparseable value is kept, counted and never used as a date; a feature without the field passes
    through untouched. Returns (kept, dropped, unparsed) and never a date.
    """
    tutulan, atilan, cozulemeyen = [], 0, 0
    for ozellik in ozellikler:
        props = ozellik.get("properties", {}) if isinstance(ozellik, dict) else {}
        if "latesteq" not in props:
            tutulan.append(ozellik)
            continue
        tarih = latesteq_tarih(props.get("latesteq"))
        if tarih is None:
            tutulan.append(ozellik)
            cozulemeyen += 1
        elif tarih >= SEAL.date():
            atilan += 1
        else:
            tutulan.append(ozellik)
    return tutulan, atilan, cozulemeyen


# ---------------------------------------------------------------- earthquake side
def fetch_ndk(data, sid, s):
    dest = data / "deprem" / s["dest"]
    if dest.exists():
        return
    out, kept, dropped, block = Out(dest), 0, 0, []
    for line in get(s["urls"][0]):
        block.append(line)
        if len(block) == 5:
            if year_of(block[0][5:15].decode()) < SEAL.year:
                out.write(b"".join(block))
                kept += 1
            else:
                dropped += 1
            block = []
    record(data, sid, dest, out.close(), urls=s["urls"], rows_kept=kept, rows_dropped=dropped)



def _cpti15_bol_yaz(dest: Path, yan: Path, header, satirlar, yi: int, *, kaynak: str,
                    kaynak_sha256: str):
    """Write the <=2015 CPTI15 split and its binding sidecar.

    Rows dated 2016-2020 and rows dated 2021 or later are both left out; the first group is
    counted as ``atilan_2016_2020`` (the sidecar's own name) and the second as ``rows_dropped``
    (the MANIFEST row's name).  The sidecar goes to ``yan`` -- ``<data>/yan-kayit/cpti15/``,
    never beside the CSV under ``deprem/`` (so the strictly fail-closed ``scripts/muhur.py`` scan
    stays clean) -- and is written as ``json.dumps(..., indent=1, sort_keys=True)``;
    ``kaynak`` is the source URL and ``kaynak_sha256`` the raw xlsx sha256, because no local full
    file is kept.  Returns ``(info, kept, atilan, dropped)``.
    """
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(header)
    kept = atilan = dropped = 0
    for r in satirlar:
        if r[yi] is None:  # blank spreadsheet row
            continue
        yil = int(r[yi])
        if yil >= SEAL.year:
            dropped += 1
        elif yil <= 2015:
            w.writerow(["" if v is None else v for v in r])
            kept += 1
        else:
            atilan += 1
    out = Out(dest)
    out.write(buf.getvalue().encode())
    info = out.close()
    yan_kayit = {
        "tur": "knotenlinie-cpti15-bolme",
        "kaynak": kaynak,
        "kaynak_sha256": kaynak_sha256,
        "cikti": os.path.abspath(dest),
        "cikti_sha256": info["sha256"],
        "kesim_yili": 2015,
        "satir_le2015": kept,
        "atilan_2016_2020": atilan,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    yan.parent.mkdir(parents=True, exist_ok=True)
    with open(yan, "w", encoding="utf-8") as f:
        json.dump(yan_kayit, f, indent=1, sort_keys=True)
        f.write("\n")
    return info, kept, atilan, dropped


def fetch_cpti(data, sid, s):
    import openpyxl

    dest = data / "deprem" / s["dest"]
    # the binding sidecar lives under <data>/yan-kayit/cpti15/, never beside the CSV
    yan = data / "yan-kayit" / "cpti15" / (dest.name + ".json")
    # the sidecar is part of the product now: regenerate if either half is missing
    if dest.exists() and yan.exists():
        return
    raw = get(s["urls"][0]).read()
    ws = openpyxl.load_workbook(io.BytesIO(raw), read_only=True)["catalogue"]
    rows = ws.iter_rows(values_only=True)
    header = [str(h) for h in next(rows)]
    yi = header.index("Year")
    info, kept, atilan, dropped = _cpti15_bol_yaz(
        dest, yan, header, rows, yi, kaynak=s["urls"][0],
        kaynak_sha256=hashlib.sha256(raw).hexdigest())
    record(data, sid, dest, info, urls=s["urls"], raw_sha256=hashlib.sha256(raw).hexdigest(),
           rows_kept=kept, rows_dropped=dropped, rows_2016_2020=atilan)


def ingv_query(t0: dt.datetime, t1: dt.datetime) -> list[bytes]:
    """Events in [t0, t1); halves the window when the service limit is reached or refused."""
    q = dict(starttime=t0.isoformat(), endtime=(t1 - dt.timedelta(microseconds=1)).isoformat(),
             format="text", limit=10000, orderby="time-asc")
    url = "https://webservices.ingv.it/fdsnws/event/1/query?" + urllib.parse.urlencode(q)
    try:
        with get(url) as r:
            body = b"" if r.status == 204 else r.read()
        refused = False
    except urllib.error.HTTPError as e:
        if e.code == 204:
            return []
        if e.code not in (400, 413, 500, 503):
            raise
        body, refused = b"", True
    time.sleep(0.3)
    rows = body.splitlines(keepends=True)[1:]
    if refused or len(rows) >= 10000:
        if t1 - t0 < dt.timedelta(minutes=10):
            raise SystemExit(f"ISIDe window {t0.isoformat()} still too large at 10 minutes")
        mid = t0 + (t1 - t0) / 2
        return ingv_query(t0, mid) + ingv_query(mid, t1)
    return rows


INGV_HEADER = (b"#EventID|Time|Latitude|Longitude|Depth/Km|Author|Catalog|Contributor|ContributorID|"
               b"MagType|Magnitude|MagAuthor|EventLocationName|EventType\n")


def fetch_ingv(data, sid, s):
    for y in range(s["start"], SEAL.year):
        dest = data / "deprem" / s["dest"] / f"iside_{y}.txt"
        if dest.exists():
            continue
        out, kept, dropped = Out(dest), 0, 0
        out.write(INGV_HEADER)
        for m in range(1, 13):
            t0 = dt.datetime(y, m, 1)
            t1 = dt.datetime(y + (m == 12), m % 12 + 1, 1)
            for line in ingv_query(t0, min(t1, SEAL)):
                if year_of(line.decode().split("|")[1]) < SEAL.year:
                    out.write(line)
                    kept += 1
                else:
                    dropped += 1
        record(data, sid, dest, out.close(), urls=[f"webservices.ingv.it/fdsnws/event/1 {y} monthly"],
               rows_kept=kept, rows_dropped=dropped)


def fetch_horus(data, sid, s):
    """HORUS: the zip is read into memory and never written; its catalogue
    member is split into one tab-separated file per year before 2021 (header kept), so the readers' file-year
    gate keeps 2016-2020 closed during calibration as it does for ISIDe. Rows from 2021 are only counted
    (the HORUS server has no date filter, so this in-memory drop is the seal)."""
    base = data / "deprem" / s["dest"]
    if base.exists() and any(base.glob("horus_*.txt")):
        return
    raw = get(s["urls"][0]).read()
    metin = zipfile.ZipFile(io.BytesIO(raw)).read(s["uye"]).decode("utf-8")
    satirlar = metin.splitlines(keepends=True)
    del metin
    baslik, yillar, dropped = satirlar[0], {}, 0
    if [c.strip() for c in baslik.split("\t")][:1] != ["Year"]:
        raise SystemExit(f"{sid}: {s['uye']} does not start with the Year column")
    for line in satirlar[1:]:
        if not line.strip():
            continue
        y = int(float(line.split("\t", 1)[0]))
        if y >= SEAL.year:
            dropped += 1
        else:
            yillar.setdefault(y, []).append(line)
    del satirlar
    son = max(yillar)
    for y in sorted(yillar):
        dest = base / f"horus_{y}.txt"
        out = Out(dest)
        out.write(baslik.encode())
        for line in yillar[y]:
            out.write(line.encode())
        record(data, sid, dest, out.close(), urls=s["urls"], raw_sha256=hashlib.sha256(raw).hexdigest(),
               rows_kept=len(yillar[y]), rows_dropped=dropped if y == son else 0,
               **({"rows_dropped_note": "all rows dated 2021 or later in the zip"} if y == son else {}))


# ---------------------------------------------------------------- forces and loads
FETCH = {"ndk": fetch_ndk, "cpti": fetch_cpti, "ingv": fetch_ingv, "horus": fetch_horus}


def fetch_wfs(data, sid, s):
    """Fetch one OGC WFS type layer per GeoJSON file, paged with startIndex/maxFeatures.

    WFS 1.1.0 uses `maxFeatures`; the WFS 2.0 `count` parameter is silently ignored by this server
    (measured 2026-09-29), so paging is done with maxFeatures. The latesteq seal filter runs before
    the file is written, so a sealed feature never reaches disk and is never printed.
    """
    sayfa = s.get("sayfa", WFS_SAYFA)
    for katman in s["typelayers"]:
        dest = data / s["side"] / s["dest"] / f"{katman}.geojson"
        if dest.exists():
            continue
        ozellikler, urls, baslangic = [], [], 0
        while True:
            q = dict(service="WFS", version="1.1.0", request="GetFeature", typeName=f"{s['workspace']}:{katman}",
                     outputFormat="application/json", maxFeatures=sayfa, startIndex=baslangic)
            url = s["base"] + "?" + urllib.parse.urlencode(q)
            urls.append(url)
            with get(url) as r:
                obje = json.loads(r.read())
            yeni = obje.get("features", [])
            ozellikler += yeni
            if len(yeni) < sayfa:
                break
            baslangic += len(yeni)
            time.sleep(0.2)
        tutulan, atilan, cozulemeyen = latesteq_muhur(ozellikler)
        out = Out(dest)
        out.write(json.dumps({"type": "FeatureCollection", "features": tutulan}, ensure_ascii=False).encode())
        record(data, sid, dest, out.close(), urls=urls, rows_kept=len(tutulan), rows_dropped=atilan,
               muhur_2021_atilan=atilan, latesteq_cozulemedi=cozulemeyen, katman_kayit=len(ozellikler))



def fetch_source(data, sid, s):
    """Dispatch one source."""
    if s["side"] == "deprem":
        FETCH[s["kind"]](data, sid, s)
    elif s.get("kind") == "wfs":
        fetch_wfs(data, sid, s)
    else:
        raise ValueError(f"{sid}: unknown source kind")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?")
    ap.add_argument("--only")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    if a.list:
        for k, s in SOURCES.items():
            print(f"{k:18} {s['side']:7} {s.get('note', '')}")
        return 0
    if not a.data:
        ap.error("data directory required")
    data = Path(a.data)
    data.mkdir(parents=True, exist_ok=True)
    acik = a.only.split(",") if a.only else None
    for sid in (acik or SOURCES):
        s = SOURCES[sid]
        print(f"{sid}:")
        fetch_source(data, sid, s)
    seal = subprocess.run([sys.executable, Path(__file__).with_name("muhur.py"), data])
    return seal.returncode


if __name__ == "__main__":
    sys.exit(main())
