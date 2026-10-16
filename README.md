# Knotenlinie

Knotenlinie is an open research codebase for probabilistic earthquake forecasting. It builds daily
ETAS-class forecasts and long-term smoothed-seismicity and fault-based forecasts for **Italy**, **southern
California** and **New Zealand**, and scores them with CSEP-standard tests against named baseline
forecasts. Every result is written down with its evidence level, including the many layers that did not
raise the score.

The name is Hegel's *Knotenlinie*, the nodal line of measure relations: the points where a steady change in
quantity turns into a change in kind. It names the question, not a finding.

> **Disclaimer.** This is research code. It does not issue earthquake predictions, warnings or official
> hazard assessments, and nothing in this repository says that any place is safe or unsafe. A low
> probability is not a statement of safety and a high one is not a warning. For official information, use
> the seismological agency of your country.

## Where we stand

Information gain (IG) is measured in nats per earthquake: the average log ratio of the probability our model
gave to each observed earthquake against the baseline's, minus the difference in the total number each
expected. +0.1 nat means about 1.11 times the baseline's probability on average (geometric mean).
Uncertainty is the weekly-block standard error. The verdict rule and the tests are in
[docs/TEST-RULES.md](docs/TEST-RULES.md).

| Horizon and region | Comparison | Earthquakes | IG ± SE (nat/eq) | Verdict | Level |
|---|---|---:|---|---|---|
| Daily, Italy 2011–2015, M≥3.95 | R − ETAS-LM | 130 | +0.025 ± 0.112 | undecided | SP-ic |
| Daily, Italy 2011–2015, M≥3.95 | equal-weight {R, ETAS-LM} − ETAS-LM | 130 | +0.071 ± 0.072 | undecided | SP-ic |
| Daily, southern California 2011–2020, M≥2.8 | period-Mc ETAS (D1) − plain ETAS (D0) | 3407 | +0.280 ± 0.134 | pass | SP-ic, development bench |
| Daily, New Zealand 2011–2020, M≥3.8 | D1 − D0 | 2125 | −0.139 ± 0.130 | fail | SP-ic, development bench |
| Five years, Italy 2011–2015, declustered M≥4.95 | fault-based AH − HAZFX-BPT | 7 | −0.35 ± 0.45 | fail | SP-ic |
| Ten years, California 2011–2020, mainshocks M≥4.95 | our model − HKJ07 | 22 | +0.35 ± 0.18 | undecided (Holm p 0.058) | SP-ic |

How to read it:

- **Evidence level.** P = prospective (forecast frozen before the earthquakes happened). SP = pseudo-
  prospective (parameters frozen before a past test window). G = retrospective. **Every row here is SP-ic,
  internal validation; none is prospective.** The test windows were used by many experiments, so these are
  development scores, weaker than a once-only test.
- **ETAS-LM** is our reconstruction of the published Italian daily ETAS model (Lombardi and Marzocchi 2010),
  not the operational forecast itself. **D0** is our own plain ETAS. HAZFX-BPT is a frozen CSEP-Italy forecast;
  HKJ07 is the RELM forecast of Helmstetter, Kagan and Jackson (2007).
- **California and New Zealand rows are a development bench.** The model design was chosen while looking at
  2011–2020; they are not the prospective CSEP California archive. In both regions every forecast expected
  well below the number of earthquakes that happened (about half for D1), so the gain is relative.
- **In short:** with this many earthquakes we cannot tell our daily Italian models apart from the published
  ETAS; the best five-year Italian model (HAZFX-BPT) is ahead of ours on 7 earthquakes, too few to be sure; in
  California our ETAS variant beats our own plain ETAS, in New Zealand it does not. Differences smaller than
  about 0.1 nat (daily, Italy) or 0.3 nat (five years, Italy) cannot be seen with these sample sizes.
- Not every model behind these rows has been reviewed independently yet; see
  [docs/HOW-WE-WORK.md](docs/HOW-WE-WORK.md).

What did not work, with numbers: [docs/WHAT-DID-NOT-WORK.md](docs/WHAT-DID-NOT-WORK.md).

## What is in the repository

| Path | Content |
|---|---|
| `knotenlinie/etas/` | ETAS core: catalogue readers with the seal gates, completeness, likelihood, stochastic declustering, simulation, residuals. Clean-room code from the published equations. |
| `knotenlinie/ortak_zemin/` | Common ground: Italian catalogue on the CSEP grid, plain ETAS baselines fitted on ≤2005 and ≤2010 data. |
| `knotenlinie/etas_uzun/`, `kaskad/`, `etas_mc25/`, `etas_kisitli/`, `etas_lm/` | Daily Italian models: R (long, time-varying completeness ETAS), its intraday cascade, the Mc 2.5 refit, the branching-constrained R (AJ), and the ETAS-LM reconstruction. |
| `knotenlinie/yan_tezgah/`, `kaliforniya/` | Southern California and New Zealand daily bench; California long-term model and data readers. |
| `knotenlinie/uzun_vade/`, `fay_zaman/`, `fay_butce/` | Long-term models: smoothed seismicity, Weichert rates, fault-based moment-balanced rates with optional BPT, fault slip-rate budget. |
| `knotenlinie/karsilastir/` | Comparison runner and experiment drivers (`gunluk_*` daily, `uzun_*` long-term). |
| `knotenlinie/skor_defteri/`, `puan2/` | Score ledgers (per-event rate, per-day total) and the CSEP-standard scoring re-read (NBD, binary likelihood, HAC, T/W). |
| `knotenlinie/step/`, `ml_uye/`, `etas_stai/`, `etas_sonlu/`, `etas_hiyerarsi/`, `eepas/`, `crs/`, `defter/`, `elastik/`, `diss320/` | Layers that were measured and dropped, kept so their negative results can be checked. |
| `knotenlinie/kanal/` | Rupture-size scaling of sources and the Coulomb stress transfer used by the CRS experiment. |
| `knotenlinie/yollar.py` | The single resolver for the data, records and runs roots. |
| `records/<ID>/` | Frozen rule files (`KURAL.md`, written before scoring) and frozen selections of each experiment. Kept verbatim in Turkish apart from required edits; see `records/HASHES.md`. |
| `scripts/` | Data downloaders, the ≤2015 cut, base-model download, and the seal check. |
| `tests/` | Unit and known-answer tests. |
| `docs/` | Method, test rules, seal and blind window, literature landscape, negative results, working method, data layout. |

Module and identifier names are Turkish (`gunluk` daily, `uzun` long, `taban` baseline, `defter` ledger,
`kural` rule, `muhur` seal); the documentation is in English.

## Install and run the tests

Python 3.9 or later.

```sh
python -m pip install -e ".[dev]"
python -m pytest -q
```

Tests that need downloaded data skip when `KNOTENLINIE_DATA` is unset or a file is missing. With data:

```sh
KNOTENLINIE_DATA=/path/to/data python -m pytest -q
python -m pytest -q tests/puan2 tests/karsilastir tests/skor_defteri   # scoring code only
python -m pytest -q -m agir tests/etas                                   # heavy ETAS recovery tests
python -m pip install -e ".[ml,crosscheck]"                              # optional extras and the pyCSEP cross-check
```

## Data

No earthquake catalogue is shipped. Set `KNOTENLINIE_DATA` to an empty directory; the download scripts fetch
each source from its provider into it. Sources, licences and required citations are in
[DATA-SOURCES.md](DATA-SOURCES.md); the directory layout, the run order and the base-model checksums are in
[docs/DATA.md](docs/DATA.md).

Run the pipeline commands from the repository root: the drivers record their code by repo-relative path. Some
drivers pin the SHA-256 of the input files they were run with, and those pins refer to the maintainer's files.
A fresh setup therefore downloads CPTI15 and the other sources itself, rebuilds the shared inputs (the common
ground) and re-anchors the pins, as described in [docs/DATA.md](docs/DATA.md) §4.

## Seal and blind window

No earthquake data dated 2021-01-01 or later is downloaded, opened or committed: the downloaders filter on the
server or while streaming, the readers stop on such a row, and `scripts/muhur.py` checks the downloaded
catalogues. For
Italy, 2016–2020 is a blind window that is opened once, after the rules are frozen and published; models are
calibrated on data up to 2015 ([docs/SEAL-AND-BLIND-WINDOW.md](docs/SEAL-AND-BLIND-WINDOW.md)).

## Documentation

- [docs/METHOD.md](docs/METHOD.md): the models and how each row is produced
- [docs/TEST-RULES.md](docs/TEST-RULES.md): scoring, uncertainty, consistency tests, verdict rule, evidence levels
- [docs/SEAL-AND-BLIND-WINDOW.md](docs/SEAL-AND-BLIND-WINDOW.md): data split, code gates, preregistration design
- [docs/SOTA-LANDSCAPE.md](docs/SOTA-LANDSCAPE.md): what the literature shows, by horizon and evidence level
- [docs/WHAT-DID-NOT-WORK.md](docs/WHAT-DID-NOT-WORK.md): every measured layer that did not raise the score
- [docs/HOW-WE-WORK.md](docs/HOW-WE-WORK.md): the working method and the roadmap
- [docs/DATA.md](docs/DATA.md): data layout and run order

## License and citation

Code and documentation: Apache License 2.0 ([LICENSE](LICENSE), [NOTICE](NOTICE)). Downloaded data keep their
providers' licences ([DATA-SOURCES.md](DATA-SOURCES.md)). To cite this software, use
[CITATION.cff](CITATION.cff); please also cite the data providers and the baseline forecasts you use.

Knotenlinie is not affiliated with or endorsed by CSEP, INGV, SCEDC, GeoNet or the USGS.

Contributions: [CONTRIBUTING.md](CONTRIBUTING.md). Security reports: [SECURITY.md](SECURITY.md).
