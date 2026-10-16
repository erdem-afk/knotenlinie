# Data: layout, preparation and run order

Licences and citations of every source are in [DATA-SOURCES.md](../DATA-SOURCES.md). This page says where the
files go, how the working copies are made, which checksums pin them, and in which order the pipeline runs.

## 1. Roots

Inside the package, `knotenlinie/yollar.py` is the only module that reads the three root variables (the scripts
in `scripts/` read `KNOTENLINIE_DATA` and `KNOTENLINIE_RECORDS` for their defaults):

| Variable | Default | Content |
|---|---|---|
| `KNOTENLINIE_DATA` | `<repo>/data` (git-ignored) | downloaded catalogues, fault sources, base forecasts, common-ground files |
| `KNOTENLINIE_RECORDS` | `<repo>/records` (tracked) | frozen rule files and selections of each experiment |
| `KNOTENLINIE_RUNS` | `<repo>/runs` (git-ignored) | new outputs and score ledgers |

Frozen records are never overwritten: before its first stage a driver copies `records/<ID>/` into `runs/<ID>/`
and writes only there. One more variable, `KNOTENLINIE_FAY_AYAR`, names the setup JSON of the fault-budget
background when the comparison runner loads `knotenlinie/fay_butce/arayuz.py` as a model.

## 2. Layout under `KNOTENLINIE_DATA`

| Path | Written by | Read by |
|---|---|---|
| `deprem/horus/horus_YYYY.txt` (to 2020) | `scripts/indir.py --only horus` | `scripts/kesik_2015.py` |
| `deprem/cpti15/CPTI15_v4.0_le2015.csv` (to 2015) | `scripts/indir.py --only cpti15` | `scripts/kesik_2015.py` |
| `deprem/iside/iside_YYYY.txt` (1985–2020) | `scripts/indir.py --only iside` | EEPAS experiment (files from 2016 on are never opened) |
| `deprem/gcmt/jan76_dec20.ndk` | `scripts/indir.py --only gcmt` | `scripts/kesik_2015.py` |
| `kuvvet/fay/diss320/*.geojson` | `scripts/indir.py --only diss320` | `scripts/kesik_2015.py` |
| `kesik-2015/horus/horus_YYYY.txt` (1960–2015) | `scripts/kesik_2015.py` | common ground, R lineage |
| `kesik-2015/CPTI15_v4.0_le2015.csv` | `scripts/kesik_2015.py` | long-term Italy, fault budget, CRS |
| `kesik-2015/gcmt_le2015.ndk` | `scripts/kesik_2015.py` | finite-source experiment |
| `diss320/{iss320,csspln320,csstop320}.geojson` | `scripts/kesik_2015.py` | fault-based long term, fault budget, CRS |
| `tabanlar/*.italy.10yr.2010-01-01.xml` | `scripts/tabanlar_indir.py` | long-term Italy baselines |
| `kaliforniya/hkj07/*`, RELM polygons | `scripts/tabanlar_indir.py` | ten-year California row |
| `kaliforniya/deprem/comcat_YYYY.csv` (to 2020) | `knotenlinie/kaliforniya/indir.py` | ten-year California row |
| `yan/deprem/yan-bolge/{scsn,geonet}/` (to 2020) | `knotenlinie/yan_tezgah/indir.py` | daily development bench |
| `ortak/` | `python -m knotenlinie.ortak_zemin.komut` | almost every daily driver |

`scripts/muhur.py <root>` checks every catalogue file under `<root>/deprem/` (exit 0 = clean). There are three
catalogue roots, so after the downloads run it three times: `python scripts/muhur.py "$KNOTENLINIE_DATA"`
(Italian and global catalogues; `scripts/indir.py` also runs this check itself), then with
`"$KNOTENLINIE_DATA/kaliforniya"` and with `"$KNOTENLINIE_DATA/yan"`.

## 3. Base forecasts and their checksums

The CSEP-Italy forecasts come from commit `ecb696c3ee06f2bb6a38c7c275d8486fcb6e505b` of
`github.com/cseptesting/italy2010_experiment` (`models/`), unit ten years:

| Forecast | File | SHA-256 |
|---|---|---|
| HAZFX-BPT | `akinci.HAZFX_BPT.italy.10yr.2010-01-01.xml` | `c0235baa6c9b579b45accd2e0ec9f25758ca43364cd724a1cd10999ebc74effe` |
| TripleS-CPTI | `zechar.TripleS-CPTI.italy.10yr.2010-01-01.xml` | `5dda2a757ed1aa2871ecfe9677973c5ecb82b39f418c4d7f29a583b59c783e24` |
| MPS04 | `meletti.MPS04.italy.10yr.2010-01-01.xml` | `2ea8c3902cb00eb551777ab87da1deebf53cb44f2e0db225ba045ccf7dbf0de4` |

The ten-year unit is confirmed by `src/total/models.yml` of the same commit (SHA-256
`15ba20b96ed9baf0690e539652dbc0b283052541defebc5eb36c7964cbc01040`); the five-year dates written inside the
MPS04 file are not its rate unit. HAZFX-BPT is used as its delivered ten-year average rate, not as a re-run
renewal model. The URLs and hashes are recorded in `records/H/TABANLAR.json`.

The California baseline comes from the pyCSEP artifacts (`csep/artifacts/` of `SCECcode/pycsep`):

| File | SHA-256 |
|---|---|
| `helmstetter_et_al.hkj-fromXML.dat` (mainshock) | `85fc89102218f0f4183faacc7428f846e792874c1822090bddb76e35b3c1ccff` |
| `helmstetter_et_al.hkj.aftershock-fromXML.dat` (aftershock) | `7b3cf1ffc13633be661a391c5e12415b5bc60d3ccd36d26ec26633ab3d285c14` |
| `RELMTestingPolygon.txt` | `44d7fa59e3bfe98309e1d8eb1678a299d758e685db7abc1bd4210b9278e5fda5` |
| `RELMCollectionPolygon.txt` | `03346a49b7b5899a536b2083e8b0debc5964e485f3f021e1083bf2e12e118a77` |
| `RELMTestArea.dat` | `d4133608f70a52d2faed002483a492231b5f2dcd2ff805d7fe68b2d1fd3117a7` |

HKJ07 is a five-year forecast (7682 cells × 41 magnitude bins, depth [0, 30) km); its rates are doubled for the
2011–2020 test. Its file totals are about 4 % below the totals given in the paper (cause not verified); the file
is used as it is.

## 4. Pinned hashes and a fresh setup

Some drivers pin the SHA-256 of the files they were run with (the DISS 3.2.0 download in
`knotenlinie/fay_butce/veri.py`, the delivered common-ground files in `fay_butce/komut3.py`, the EEPAS input
package `records/C/zemin2.json` and the code hash of `knotenlinie/etas/model.py` checked by `eepas/c2.py` and
`eepas/c3.py`). These pins refer to the maintainer's files. A fresh download or a refitted common ground can differ
byte for byte, so these gates refuse to run until they are re-anchored. They are kept on purpose, because they
protect the frozen inputs. A fresh setup therefore builds every shared input itself and re-anchors the pins:

1. **Download CPTI15 again** with `python scripts/indir.py "$KNOTENLINIE_DATA" --only cpti15`, even if you have
   a copy from elsewhere: the downloader writes the ≤2015 split together with a sidecar JSON
   (`yan-kayit/cpti15/`) that binds it to the SHA-256 of the source spreadsheet, and the sealed CPTI15 reader
   (`knotenlinie/kanal/tektonik_kaynak.py`) refuses a split without a matching sidecar of this repository's
   kind. Fetch the other sources of step 1 below the same way.
2. **Rebuild the common ground** with `python -m knotenlinie.ortak_zemin.komut` and the steps `katalog`, `ayar`,
   `dogrulama` and `readme`. The last step writes `ortak/README.md` with the SHA-256 of every common-ground file;
   the EEPAS drivers check the files against it, and the fitted ETAS files carry the code hash of
   `knotenlinie/etas/model.py`.
3. **Re-anchor the remaining pins:** `python -m knotenlinie.eepas.c2 --hazirla` writes a new input package to
   `runs/C/zemin2.json` (pass it to C2 with `--paket runs/C/zemin2.json`); for the fault-budget experiment, replace
   the four values of `TESLIM` in `knotenlinie/fay_butce/komut3.py` with the SHA-256 of your rebuilt
   `ortak/` files. The DISS 3.2.0 pin in `fay_butce/veri.py` is enforced only for a blind-window run.
4. Frozen selections that pin a ledger (`records/U/AGIRLIK.json`) are re-written in `runs/<ID>/` when that
   experiment's selection stage runs again (`--asama hepsi`); the frozen copy in `records/` is never changed.

Rebuilt inputs reproduce the recorded numbers only within the tolerance of the refit, not byte for byte.

## 5. Run order

Run every command from the repository root: the drivers record the SHA-256 of their own code by repo-relative
path (`knotenlinie/...`), so a run started in another directory fails or records an incomplete code list. The
commands assume `KNOTENLINIE_DATA` is set; outputs go to `KNOTENLINIE_RUNS` (default `runs/`). Single-threaded
BLAS is recommended (`OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1`).

1. **Download and cut.**
   `python scripts/indir.py "$KNOTENLINIE_DATA" --only horus,cpti15,diss320` (add `gcmt,iside` for the
   finite-source and EEPAS experiments), then `python scripts/kesik_2015.py`, then
   `python scripts/tabanlar_indir.py` (base forecasts; the common-ground grid is read from the HAZFX-BPT file).
2. **Common ground.** `python -m knotenlinie.ortak_zemin.komut katalog`, then `ayar`, `dogrulama` and `readme`:
   the common catalogue, the CSEP-Italy grid, the ≤2005 and ≤2010 plain ETAS baselines and the checksum list.
3. **R lineage.** `python -m knotenlinie.karsilastir.gunluk_n --asama hepsi` (Mc 2.5 refit), then `gunluk_r
   --asama hepsi` (R fits), then `gunluk_s --asama hepsi` (≤2005 R-type fit).
4. **Ensembles.** `python -m knotenlinie.karsilastir.gunluk_u --asama hepsi`: R, ETAS-LM and the equal-weight
   ledgers for 2006–2010 and 2011–2015.
5. **Branching-constrained R.** `python -m knotenlinie.karsilastir.gunluk_aj --asama sec`, then `son`, then
   `olcum`: AJ and E7 ledgers.
6. **Development bench.** `python -m knotenlinie.yan_tezgah.indir --bolge scsn --bolge geonet`, then
   `python scripts/muhur.py "$KNOTENLINIE_DATA/yan"`, then for each region (`scsn`, `geonet`)
   `python -m knotenlinie.karsilastir.gunluk_y --bolge scsn --d3 --defter-yaz --donem-adi 2011-2020
   --maks-cift 200000000 --cikti runs/Y/OLCUM-scsn.json` (fit on data before 2011, scored on 2011–2020; the
   ledgers go to `runs/defter/Y/`).
7. **Long term.** Italy: `uzun_z` (shape selection; the frozen record is shipped), `uzun_z2`, `uzun_ah sec`,
   `uzun_ah puan`. California: `python -m knotenlinie.kaliforniya.indir "$KNOTENLINIE_DATA/kaliforniya"` and
   `python scripts/muhur.py "$KNOTENLINIE_DATA/kaliforniya"`, then `uzun_ad sec`, `uzun_ad puan` (all under
   `python -m knotenlinie.karsilastir.`).
8. **Scoring re-read.** `python -m knotenlinie.puan2.komut --parca hepsi` re-reads the ledgers and writes the
   table of [TEST-RULES.md](TEST-RULES.md) §7.

Steps 3–5 took about 80 minutes on a compute server, with peaks of a few GB of memory; the tests need none of
them.
