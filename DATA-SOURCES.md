# Data sources and third-party software

Knotenlinie reads third-party datasets but ships none of them. The repository contains download scripts and
readers; the data are fetched from their providers into a local data root and are never committed. This file
lists every source the code in this release reads, its licence, the attribution it asks for, and how the
repository obtains it. If you use a source, its terms bind you, not the repository's Apache-2.0 licence.

## How data reach your machine

- **Data root.** Set `KNOTENLINIE_DATA` to an empty directory. Every downloader writes below it (for example
  `deprem/` for the Italian and global catalogues, `kuvvet/` for fault geometry). The directory layout the models
  read, and the steps that produce it, are in [docs/DATA.md](docs/DATA.md).
- **Main downloader.** `python scripts/indir.py --list` prints the source ids;
  `python scripts/indir.py "$KNOTENLINIE_DATA" --only <id>[,<id>...]` fetches the named sources and then runs
  the seal check. Each written file gets a line in `$KNOTENLINIE_DATA/MANIFEST.jsonl` (source, URLs, bytes,
  SHA-256, rows kept and dropped).
- **Other downloaders.** `knotenlinie/kaliforniya/indir.py` (California, USGS ComCat),
  `knotenlinie/yan_tezgah/indir.py` (southern California SCSN and New Zealand GeoNet) and
  `scripts/tabanlar_indir.py` (base forecasts, fetched from pinned URLs and checked against recorded SHA-256
  values; [docs/DATA.md](docs/DATA.md) §3).
- **Earthquake date limit.** Every earthquake downloader asks its server only for events dated before
  2021-01-01; `scripts/indir.py` and `knotenlinie/yan_tezgah/indir.py` also drop any later row while streaming,
  before anything reaches disk. HORUS has no server-side filter: its zip archive is opened in memory and later
  rows are dropped before a file is written. `scripts/muhur.py`
  checks the downloaded catalogues afterwards (one call per catalogue root, [docs/DATA.md](docs/DATA.md) §2).
  No tracked file may contain an earthquake record dated 2021-01-01 or later.
- **User-Agent.** The downloaders identify themselves as
  `knotenlinie (+https://github.com/erdem-afk/knotenlinie)`; no e-mail address is sent.

## Sources with use restrictions

| Source | Restriction |
|---|---|
| SCSN catalogue | SCEDC grants a non-transferable licence; each user obtains it from SCEDC |
| Global CMT catalogue | No licence stated; the project asks users to cite two papers |
| SRCMOD finite-fault models (optional) | No licence found; each model belongs to its original authors |

## Earthquake catalogues

### HORUS: Homogenized instrumental seismic catalogue of Italy

- **Provider:** INGV Bologna.
- **Licence:** CC BY 4.0.
- **Cite:** Lolli B., Randazzo D., Vannucci G., Gasperini P. (2020). The Homogenized Instrumental Seismic
  Catalog (HORUS) of Italy from 1960 to Present. Seismol. Res. Lett. 91, 3208–3222,
  https://doi.org/10.1785/0220200148 ; dataset https://doi.org/10.13127/HORUS
- **Obtained by:** `scripts/indir.py`, source `horus` (one file per year).
- **Used by:** the common ground and every daily Italian model.

### CPTI15 v4.0: Italian parametric earthquake catalogue

- **Provider:** Istituto Nazionale di Geofisica e Vulcanologia (INGV).
- **Licence:** CC BY 4.0.
- **Cite:** Rovida A., Locati M., Camassi R., Lolli B., Gasperini P., Antonucci A. (2022). Catalogo Parametrico dei
  Terremoti Italiani (CPTI15), versione 4.0. INGV. https://doi.org/10.13127/cpti/cpti15.4 , and Rovida et al.
  (2020), Bull. Earthq. Eng. 18, 2953–2984, https://doi.org/10.1007/s10518-020-00818-y
- **Obtained by:** `scripts/indir.py`, source `cpti15`. Only rows up to 2015 are written; a sidecar JSON
  binds the file to the SHA-256 of the source spreadsheet. Needs `openpyxl`.
- **Used by:** the long-term Italian models (Weichert rate), the fault-budget, CRS and EEPAS experiments.

### ISIDe: Italian Seismological Instrumental and Parametric Database

- **Provider:** INGV, FDSN event web service.
- **Licence:** CC BY 4.0.
- **Cite:** ISIDe Working Group (2007). Italian Seismological Instrumental and Parametric Database (ISIDe).
  INGV. https://doi.org/10.13127/ISIDe
- **Obtained by:** `scripts/indir.py`, source `iside` (one file per year, 1985–2020; queries end at
  2020-12-31).
- **Used by:** the EEPAS experiment.

### Global CMT catalogue

- **Provider:** Global Centroid-Moment-Tensor Project (Lamont-Doherty Earth Observatory).
- **Licence:** none stated; the project asks users to cite two papers.
- **Cite:** Dziewonski A. M., Chou T.-A., Woodhouse J. H. (1981), J. Geophys. Res. 86, 2825–2852,
  https://doi.org/10.1029/JB086iB04p02825 ; Ekström G., Nettles M., Dziewonski A. M. (2012), Phys. Earth Planet.
  Inter. 200–201, 1–9, https://doi.org/10.1016/j.pepi.2012.04.002
- **Obtained by:** `scripts/indir.py`, source `gcmt` (file `jan76_dec20.ndk`).
- **Used by:** the finite-source experiment (rupture orientation).

### ANSS Comprehensive Earthquake Catalog (ComCat): California

- **Provider:** U.S. Geological Survey, FDSN event service (RELM region plus a 1-degree buffer).
- **Licence:** USGS-authored data are in the U.S. public domain; USGS asks for credit.
- **Cite:** U.S. Geological Survey, Earthquake Hazards Program (2017). Advanced National Seismic System (ANSS)
  Comprehensive Catalog. https://doi.org/10.5066/F7MS3QZH
- **Obtained by:** `knotenlinie/kaliforniya/indir.py` (M≥2.5, 1981–2020, `endtime` ≤ 2020-12-31T23:59:59).
- **Used by:** the ten-year California model.

### SCSN catalogue: southern California

- **Provider:** Southern California Earthquake Data Center (SCEDC), FDSN event service.
- **Licence:** SCEDC grants a non-exclusive, royalty-free, non-transferable, worldwide right to use, reproduce and
  publicly display public SCSN data, and asks for both DOIs below in publications.
- **Cite:** SCEDC (2013): Southern California Earthquake Center. Caltech. Dataset. https://doi.org/10.7909/C3WD3xH1 ;
  California Institute of Technology (Caltech) (1926): Southern California Seismic Network.
  https://doi.org/10.7914/SN/CI
- **Obtained by:** `knotenlinie/yan_tezgah/indir.py`, region `scsn`.
- **Used by:** the daily development bench.

### GeoNet earthquake catalogue: New Zealand

- **Provider:** GeoNet (New Zealand), FDSN event service.
- **Licence:** CC BY 3.0 New Zealand.
- **Acknowledge:** "We acknowledge the New Zealand GeoNet programme and its sponsors NHC, Earth Sciences NZ, LINZ,
  NEMA and MBIE for providing data used in this study."
- **Obtained by:** `knotenlinie/yan_tezgah/indir.py`, region `geonet`.
- **Used by:** the daily development bench.

## Fault sources and baseline forecasts

### DISS 3.2.0: Database of Individual Seismogenic Sources

- **Provider:** INGV, OGC WFS service.
- **Licence:** CC BY 4.0; downloading implies crediting the database.
- **Cite:** DISS Working Group (2015). Database of Individual Seismogenic Sources (DISS), version 3.2.0. INGV.
  https://doi.org/10.6092/ingv.it-diss3.2.0
- **Obtained by:** `scripts/indir.py`, source `diss320` (six layers as GeoJSON).
- **Used by:** the fault-based long-term model, the fault-budget and CRS experiments.

### CSEP Italy 2010 experiment forecasts

- **Provider:** Collaboratory for the Study of Earthquake Predictability, repository
  `cseptesting/italy2010_experiment`, pinned commit `ecb696c3ee06f2bb6a38c7c275d8486fcb6e505b`.
- **Licence:** The Unlicense (repository licence). The model files are authored by the modelling groups; they
  are downloaded, not redistributed.
- **Cite:** Schorlemmer D. et al. (2010), Ann. Geophys. 53(3), 1–9, https://doi.org/10.4401/ag-4844 , and the
  authors of each model used (HAZFX-BPT, TripleS-CPTI, MPS04).
- **Obtained by:** download from the pinned commit; URLs and SHA-256 values are in `records/H/TABANLAR.json`;
  read by `knotenlinie/karsilastir/tabanlar.py`.
- **Used by:** the long-term Italian rows (baselines).

### pyCSEP artifacts

- **Provider:** pyCSEP, repository `SCECcode/pycsep` (`csep/artifacts/`): the CSEP Italy forecast region, the
  Helmstetter et al. (2007) California forecasts (HKJ07, mainshock and aftershock versions) and the RELM
  polygons.
- **Licence:** BSD-3-Clause (repository-wide).
- **Cite:** Savran W. H. et al. (2022), pyCSEP, J. Open Source Softw., https://doi.org/10.21105/joss.03658 ;
  Helmstetter A., Kagan Y. Y., Jackson D. D. (2007), Seismol. Res. Lett. 78, 78–86,
  https://doi.org/10.1785/gssrl.78.1.78
- **Obtained by:** download from the pyCSEP repository; checksums in [docs/DATA.md](docs/DATA.md); read by
  `knotenlinie/kaliforniya/veri.py`.
- **Used by:** the ten-year California row (baseline and grid); the Italy forecast region can serve as the grid
  of the fault-budget experiment.

### SRCMOD finite-fault rupture models (optional)

- **Provider:** SRCMOD online database.
- **Licence:** none found; each model belongs to its original authors.
- **Cite:** Mai P. M., Thingbaijam K. K. S. (2014), Seismol. Res. Lett. 85, 1348–1357,
  https://doi.org/10.1785/0220140077 , and the source paper of every model used.
- **Obtained by:** manual download. The Coulomb-transfer code (`knotenlinie/kanal/k9.py`) uses scaled
  rectangular ruptures (Wells and Coppersmith 1994) when no SRCMOD model is supplied.

## Values inside test files

These tests carry reference numbers, not datasets:

| File | Content | Source |
|---|---|---|
| `tests/elastik/okada1985_tablo2.py` | check values for the Okada surface-deformation formulas | Okada Y. (1985), Bull. Seismol. Soc. Am. 75(4), 1135–1154 |
| `tests/elastik/pscmp_ka2_anlik.json` | output values of one PSGRN/PSCMP 2020 run (one Okada source in central Italy, 44 receivers), used as a cross-check of `okada_ned` on the sphere; no PSGRN/PSCMP code is included | Wang R. et al. (2006), Comput. Geosci. 32, 527–541, https://doi.org/10.1016/j.cageo.2005.08.006 |

No other third-party file, and no file derived from third-party earthquake data, is tracked in the repository.

## Third-party software

The repository contains no third-party source code. The ETAS core and the elastic kernels are clean-room
implementations from the published equations (Ogata 1988, 1998; Zhuang et al. 2002; Okada 1985, 1992).

Python dependencies are installed with `pip` and never vendored: numpy, scipy, pandas, shapely (BSD-3-Clause);
openpyxl and pytest (MIT); pyarrow (Apache-2.0); optional scikit-learn, statsmodels and pycsep (BSD-3-Clause).
pycsep is used only by an optional cross-check of the scoring code; the scoring code does not depend on it.
