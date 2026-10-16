# Seal and blind window

A forecast test is only as good as the guarantee that the forecast did not see the earthquakes it is scored
on. This document gives the fixed data split, the gates in the code that enforce it, and the design for
opening the blind window once.

## 1. Fixed rules

- **Calibration ≤ 2015.** Models that will face the blind window are fitted on data up to 2015-12-31.
- **2016–2020 is the Italian blind window.** It is opened once, by decision of the maintainer, after the
  preregistration is frozen and published.
- **2021-01-01 and later is sealed.** No earthquake record dated on or after 2021-01-01 is downloaded, opened,
  printed or committed, and nothing derived from such records is used (a fault plane or slip model of a 2023
  earthquake, for example). Files that contain no events (fault databases, strain maps, hazard models,
  forecast grids) may be downloaded, but not in a version built from 2021+ earthquakes.
- **Current rows** are fitted on data up to 2010 (2005 for the ten-year California row) and scored on later
  years: 2011–2015 in Italy, 2011–2020 on the southern California and New Zealand development bench. Those two
  regions are development data, so their 2016–2020 years are not blind.

## 2. Gates in the code

**Catalogue readers** (`knotenlinie/etas/katalog.py`) apply three gates before anything is computed:

1. **File-year gate.** The yearly Italian instrumental files are opened by year; a file whose year is 2016 or
   later is not opened at all, so a broad file pattern cannot reach them.
2. **Seal gate.** If a parsed row is dated on or after 2021-01-01T00:00:00Z, the reader raises `MuhurIhlali`
   and stops. It does not drop the row: the seal is not a filter. The error message carries only a count,
   never the sealed record.
3. **Cutoff gate.** Rows after 2015-12-31T23:59:59.999999Z are dropped and counted; the last microsecond of
   2015 is kept.

The cutoff and the seal are checked again at every computing entry point. The comparison runner refuses a
window that ends after 2016-01-01 and any catalogue row from 2016 on; the common-ground history reader refuses
2016 and later.

**Downloaders** ask each server for events before 2021-01-01 and drop any later row while streaming, before
anything reaches disk. One source (the HORUS zip archive) has no server-side date filter: the archive is
opened in memory and every post-2020 row is dropped before a file is written. The ≤2015 working copy that
the Italian models read is cut from these files by `scripts/kesik_2015.py`.

**Seal check.** `scripts/muhur.py <root>` scans every catalogue file under `<root>/deprem/` (it is run on the
data root and on the California and bench roots, [DATA.md](DATA.md) §2) and fails if any record is dated on or
after 2021-01-01, if a file's format is not recognised, or if a date cannot be parsed. It prints counts only.
It also fails if a dataset listed as sealed is present, matching it by path without opening it. Exit 0 = clean,
1 = sealed or unreadable data found, 2 = usage error.

## 3. Literature quarantine

Published papers can leak the blind window or the sealed years as surely as data can. Before a paper's results
are read, its evaluation window is checked:

- a paper whose evaluation reaches 2021 or later, or that reports Italian results for 2016–2020, is
  quarantined: only its method may be used, its numbers are not read or quoted;
- examples kept closed: the ten-year results of the Italian operational forecasting system and its ensemble
  weights, the Italian EEPAS test (Biondini et al. 2023), the prospective GEAR1 test (Strader et al. 2018),
  and the RECAST neural model (window not verified, treated as suspect);
- examples checked and used: Bayona et al. (2026), California only, August 2007 – August 2018; Taroni et al.
  (2018), evaluation window about 2009–2014, used qualitatively; the EarthquakeNPP benchmark, whose test
  windows all end by 2021-01-01 00:00 UTC (one dataset ends exactly there and may only be used with a copy cut
  at 2020-12-31).

None of the quarantined results changes the order of work in [SOTA-LANDSCAPE.md](SOTA-LANDSCAPE.md).

## 4. Opening the blind window once

**Gates before opening.** The window stays closed until all of these hold:

- the scoring code, the frozen common baseline and every candidate's code have passed independent review;
- the final candidates, their parameters and their history filters are frozen and identified by SHA-256;
- the common baseline is rebuilt with data up to 2015 only, without re-selecting any weight;
- the base forecasts' versions and units are confirmed;
- the preregistration (candidates per horizon, the "we passed" rule of [TEST-RULES.md](TEST-RULES.md) §8, the
  reading order) is complete and has passed its own independent review;
- a separate opening script and its data access have been reviewed.

**Preregistration and fingerprints.**

- The frozen preregistration is committed to the repository and published, dated, on the project page
  before the window is opened. The maintainer reads the page before it is published.
- The frozen rule and the SHA-256 fingerprints of every frozen model's forecast files are deposited on Zenodo.
  Zenodo registers a DOI and keeps the files fixed (after the first 30 days only for legal reasons), but
  descriptive fields can be edited, so the record's DOI and registration date are what count. The fingerprints
  are also registered with an independent timestamping service.
- **One register per window.** A single versioned Zenodo record lists every model frozen for the window. All of
  them are scored and published, not only the best; a freeze that is not in the register does not count.
- A fingerprint proves that the files existed on that date; it does not by itself prove that the window was
  unseen. The record therefore also states when the window was first read.

**Single run.** All candidates are scored in one command, no intermediate score is read, the result file is
written atomically and opened once, and an existing result file is refused. If a technical error occurs, the
first output is kept and the error and its effect are recorded; there is no new tuning, no change of
candidates or window, and no second scientific chance.

**Publication.** The result is published on the project page whether the models win or lose. The expected power
is low: about a 25 % chance of a pass for the Italian primary comparison.

**After scoring,** the forecast files themselves are published, so that anyone can score them again with pyCSEP
and compare them with the fingerprints. Scoring needs only the forecast numbers, not our code; knowing that the
numbers were made without sight of the window rests on the record, which is why the level is pseudo-
prospective, and why only forecasts deposited before the earthquakes count as prospective.

**In this release.** The blind-window opening code is held back. It will be published with the frozen
preregistration. The `gectik` helper in `knotenlinie/karsilastir/puan.py` already carries the
three-member Italian Holm family that the draft uses.

## 5. The 2021+ vault

The sealed years are kept for the final test of a frozen model. Only the maintainer can open the seal.

## References

- Bayona, J. A. et al. (2026). Nat. Commun. 17, 9444. https://doi.org/10.1038/s41467-026-76243-7
- Biondini, E., Rhoades, D. A., Gasperini, P. (2023). Geophys. J. Int. 234. https://doi.org/10.1093/gji/ggad123
  (quarantined, method only)
- Dascher-Cousineau, K., Shchur, O., Brodsky, E. E., Günnemann, S. (2023). Geophys. Res. Lett. 50.
  https://doi.org/10.1029/2023GL103909 (quarantined)
- Stockman, S., Lawson, D. J., Werner, M. J. (2026). EarthquakeNPP. Trans. Mach. Learn. Res.;
  arXiv:2410.08226
- Strader, A. et al. (2018). Seismol. Res. Lett. 89. https://doi.org/10.1785/0220180051 (quarantined)
- Taroni, M. et al. (2018). Seismol. Res. Lett. 89, 1251. https://doi.org/10.1785/0220180031
