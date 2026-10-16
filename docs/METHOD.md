# Method: the models and how each row is produced

This document describes what each model in the current results is, what data it sees, and how its score row
is produced. Scoring and the verdict rule are in [TEST-RULES.md](TEST-RULES.md); the data split and the code
gates are in [SEAL-AND-BLIND-WINDOW.md](SEAL-AND-BLIND-WINDOW.md). Each experiment has an identifier (R, J,
AJ, U, Y, Z, Z2, AH, AD and so on); its frozen rule file and selections live in `records/<ID>/`.

All numbers below are internal validation (level **SP-ic**, see [TEST-RULES.md](TEST-RULES.md)); none is
prospective.

## 1. The common daily frame (Italy)

Every daily Italian model is run in the same frame, so that rows can be compared like for like.

- **Grid:** the CSEP-Italy testing region, 8993 cells of 0.1° × 0.1°, depth [0, 30) km.
- **Catalogue:** HORUS, the homogenised instrumental catalogue of Italy, in its own homogeneous Mw (no new
  magnitude conversion is made).
- **Time step:** one UTC day. At the start of each day only earthquakes that happened before the start of the
  day enter the history; earthquakes of the same day are used from the next day on.
- **Magnitude bins:** 0.1 units from the threshold up to 8.95, last bin open (`[8.95, +∞)`).
- **Thresholds:** development M≥2.95, verdict M≥3.95, an extra row at M≥4.95.
- **Split:** models are built on data up to 2005; every choice (weight, hyperparameter, variant) is made with
  the 2006–2010 M≥2.95 log-likelihood; the chosen model is rebuilt on data up to 2010 and scored once on
  2011–2015. No choice changes after the 2011–2015 score is seen. The rule and the list of variants are
  written to `KURAL.md` before 2011–2015 is scored.
- **Event counts:** 956 (M≥2.95) and 101 (M≥3.95) earthquakes in 2006–2010; 1341, 130 and 14 earthquakes at
  M≥2.95, 3.95 and 4.95 in 2011–2015.
- **Score ledger:** for every model and period the ledger holds one row per target earthquake (time, cell,
  magnitude bin, expected count λ for that day, cell and bin) and one row per day (expected totals Λ above each
  threshold). Ensembles and rescalings are computed from the ledgers without re-running the models; the
  ledger log-likelihood difference matches the runner's to within 1e-9 (relative), and a test shows it.

## 2. The ETAS core

`knotenlinie/etas/` is a clean-room implementation written from the published equations: the ETAS model of
Ogata (1988, 1998) and stochastic declustering of Zhuang, Ogata and Vere-Jones (2002). No code was copied
from existing ETAS packages (pyetas, AGPL-3.0; the CRAN ETAS package, GPL; Zhuang's Fortran code, no licence
stated). It contains the catalogue readers (with the cutoff and seal gates), completeness estimation
(maximum curvature and the MBS method), the space-time likelihood and its maximum-likelihood fit,
stochastic declustering, simulation and residual analysis.

## 3. Common ground

`knotenlinie/ortak_zemin/` builds the shared inputs that every daily Italian experiment reads.

- **Catalogue:** HORUS 1960–2015 inside the CSEP-Italy mask, depth 0–70 km (261,276 events, 8993 cells).
- **Plain ETAS baseline:** fitted on 1985–2010 with Mc 3.1. The b-value is estimated with the data's own
  magnitude resolution (b = 0.963 on ≤2010 data). The background is a Gaussian kernel density (each kernel
  conditioned on the outer rectangle) plus an explicit uniform floor; bandwidth and floor are chosen without
  leakage: built on ≤2005, chosen on the 2006–2010 location likelihood, rebuilt on ≤2010 (10 km and 1 %). A
  separate ≤2005 baseline (20 km, 5 %) serves the 2006–2010 selections.
- **Subcriticality:** where the free fit was supercritical, the same likelihood is re-optimised under
  α ≤ b and branching ratio ≤ 1 constraints; the result is not clipped. The ≤2010 Italian branching ratio is
  0.803.
- **Known limitation:** the triggering compensator of the fit is integrated over the outer rectangle while
  target events are in the mask; this is not a fully masked fit.

## 4. Daily Italian models

### ETAS-LM (experiment J): the reference daily model

Our reconstruction of the Italian daily ETAS of Lombardi and Marzocchi (2010). The published triggering
parameters (their Table 1) are held fixed with b = 1. The Gaussian background is built from HORUS events of
2005-04-16 to 2010-12-31 with iterative declustering weights; the paper does not give the bandwidth rule, so a
10th-neighbour bandwidth with a 1.1 km minimum is assumed (not chosen on validation data). Intraday expected
daughters are added as a deterministic branching mean (32 time steps, 10 generations) instead of the original
thinning simulation.

This is **not an exact copy**: our background share is 40.56 % against 54 % in the paper, and the learning
catalogue has 2181 events against the paper's 2100. Only long-term XML forecasts were published for the
CSEP-Italy experiment, no daily forecast files, so a reconstruction was the only like-for-like daily baseline.

### R: long ETAS with time-varying completeness (experiments R, N, S)

- **Completeness:** Mc 3.1 for 1985–2004 and Mc 2.5 from 2005. With a fixed reference Mc₀ = 2.5 the
  observed rate is scaled by the Gutenberg–Richter factor 10^(−b(Mc(t) − 2.5)); the compensator is the sum over
  the two periods. Each parent passes its own Mc; productivity depends on M − Mc₀. Missing small parents are
  not imputed. The idea of letting observability vary in time follows Helmstetter, Kagan and Jackson (2006)
  and Schorlemmer and Woessner (2008); their methods are not reproduced one to one.
- **Geometry:** HORUS-Mw, [0, 30) km. Parents in the outer rectangle (502 outside the mask) trigger events in
  the mask; all 23.7 million causal pairs are used, with no sampling. The compensator is integrated over the
  CSEP mask.
- **Background:** kernel density plus a uniform floor inside the mask (5 km, 10 %), with the same ≤2005 /
  2006–2010 / ≤2010 build-choose-rebuild rule.
- **Intraday cascade** (`knotenlinie/kaskad/`): expected daughters of the day's expected events, 32 time steps
  and 10 generations. The row reported as R is "R-ortak-kaskad": the common triggering kernel with the
  cascade.
- **Fitted values (≤2010):** b 0.985, μ 0.741/day, K 0.0246, c 0.0157 day, α 0.654 (log10), p 1.165,
  branching ratio 0.881.
- **Lineage steps:** experiment N refits the plain ETAS at Mc 2.5 (2005–2010 is the longest recent block that
  passes the completeness test) and writes parameter files R starts from; experiment S provides the ≤2005
  R-type fit used for 2006–2010 selections.

R expects about 23 % more earthquakes than happened at M≥3.95 (Λ/N = 1.234); this excess is the main source of
its N-test failures and a known issue of the ETAS family.

### AJ: branching-constrained R

R with the branching ratio bounded, n ≤ n_max. n_max is chosen on 2006–2010 (candidates 0.6, 0.7, 0.8, 0.9 and
free); 0.7 wins. The constraint fixes the total (Λ/N 1.076 at M≥3.95) but the gain over R comes from the total,
not from the shape.

### Ensembles

Linear mixtures λ = Σ wₖ λₖ, computed from the score ledgers. The current candidate rows are the
**equal-weight** mixtures {R, ETAS-LM} (experiment U, row "T1-esit") and {AJ, ETAS-LM} (row "E7"). Each was
written down before it was scored. Mixtures with weights selected on 2006–2010 did worse
([WHAT-DID-NOT-WORK.md](WHAT-DID-NOT-WORK.md)).

## 5. Southern California and New Zealand bench (experiment Y)

A power bench with many more earthquakes than Italy, used as development data.

- **Data:** SCSN catalogue (SCEDC FDSN service, 1996–2020) and GeoNet catalogue (2002–2020), every row before
  2021-01-01.
- **Frame:** 0.1° grid, daily, 0.1 magnitude bins; targets M≥2.8 (southern California) and M≥3.8 (New
  Zealand); completeness in five-year windows with the MBS method.
- **Models:** D0 plain ETAS; D1 R-type ETAS with a completeness level per period; D2 D1 with the short-term
  incompleteness correction of Helmstetter, Kagan and Jackson (2006); D3 a mixture with weights chosen on
  2006–2010.
- **Fit and score:** fitted on data up to 2010, scored on 2011–2020, with a 100 km spatial cut (plus a one-year
  time cut in southern California) applied the same way to the event term, the compensator and the forecast.
- **Caveats:** all forecasts expected well below the observed number of earthquakes (southern California
  Λ_D1 1717 against N 3407; New Zealand Λ 597–1319 against N 2125), because 2011–2020 was more active than the fitting
  period. The fits end at the branching-ratio ceiling. The design of D1 was chosen while looking at these
  years, so the bench is development data, not a pseudo-prospective test.

## 6. Long-term models

### Italy (experiments Z, Z2, AH)

- **Target:** declustered earthquakes M≥4.95, 2011–2015 (five years), cell × bin Poisson score; the baseline
  forecasts publish nothing below M 4.95, so no comparison is made below it. Declustering: Gardner and
  Knopoff (1974) as primary, Uhrhammer (1986) and Reasenberg (1985) as sensitivity. An "all events" row is
  reported beside it, but the long-term baselines forecast mainshocks, so the verdict is on the declustered
  target.
- **Z (shape):** smoothed seismicity from the declustered catalogue. Variants: U0 fixed-bandwidth kernel, U1
  adaptive bandwidth (Helmstetter, Kagan and Jackson 2007), U2 U1 plus a DISS 3.2.0 moment budget. Selection:
  built on ≤2005, chosen on 2006–2010, rebuilt on ≤2010; U0 with σ = 10 km was selected. A fourth candidate,
  U3, mixed in the shape of the global strain-rate forecast GEAR1; the selection gave it weight 0, and its code
  is not included ([WHAT-DID-NOT-WORK.md](WHAT-DID-NOT-WORK.md)).
- **Z2 (total rate):** a Weichert (1980) estimate on CPTI15 up to 2010, declustered, with a published
  completeness table (M 6.5 from 1000, 5.0 from 1750, 4.5 from 1870, 4.3 from 1900, 3.5 from 1980): b = 0.81, rate
  of M≥4.95 = 1.43 per year. Z2 = Weichert total × Z shape.
- **AH (fault-based):** moment-balanced rates from the DISS 3.2.0 composite and individual sources,
  Ṁ₀ = μAṡ with μ = 3×10¹⁰ Pa and coupling 1; truncated Gutenberg–Richter or characteristic magnitude
  distribution; BPT renewal on sources with a known last event; individual sources are subtracted from their
  parent composite source; the rest of the rate comes from Z2. The fault budget is much larger than the
  catalogue rate (M≥5.45, five years: 15.3 from faults against 2.8 from Weichert), so the fault share is capped
  at 90 % of the Weichert total. Four variants (truncated GR or characteristic, BPT on or off) tied within the
  pre-registered 1 nat band; the tie rule picks the simplest, truncated GR with BPT off (`GR-kapali`).
- **Baselines:** three CSEP-Italy 2010 experiment forecasts, downloaded from a pinned commit of the CSEP
  repository: HAZFX-BPT, TripleS-CPTI and MPS04. Their unit is ten years; rates are scaled to the five-year
  test period. HAZFX-BPT puts 69 % of its rate in the top 10 % of cells and uses a b = 1.05 truncated GR in
  every cell, so its advantage is spatial concentration, not magnitude shape.
- **Caveat:** the fault database is a 2015 version, so the long-term rows are not fully free of later
  geological knowledge.

### California (experiment AD)

- **Model:** adaptive Gaussian kernel density integrated over the cells, a Weichert total rate and a tapered
  Gutenberg–Richter distribution (corner magnitude 8), like HKJ07. Selection on ≤2000 data with 2001–2005
  targets (36 candidates): k = 2, kernel catalogue M≥3.0, rate Mc 3.0.
- **Fair row:** our model sees data up to 2005, as HKJ07 did; scored on 2011–2020 at M≥4.95, mainshocks
  (Gardner–Knopoff declustered, N = 22) and all events (N = 40).
- **Baseline:** HKJ07 mainshock and aftershock forecasts (Helmstetter, Kagan and Jackson 2007) from the pyCSEP
  artifacts; five-year rates, doubled for the ten-year test.
- **Caveats:** most of the gain comes from the total rate (shape-only row +0.138, z 0.75); Reasenberg
  declustering flips the sign (mainshocks −0.161, z −0.78), so the row depends on the declustering choice.

## 7. Components that were tried

STEP-type and machine-learning members, short-term incompleteness, a finite-source kernel, hierarchical
shrinkage, fault slip-rate budgets, a strain-rate background, EEPAS/Janus, Coulomb rate-and-state, BPT
renewal, total-rate rescaling and the physical forcing channels were each added alone and measured against the
same baseline. None cleared the bar. Their code is in the repository where it is self-contained; the numbers
are in [WHAT-DID-NOT-WORK.md](WHAT-DID-NOT-WORK.md).

## 8. Run order

Data download and preparation, then the common ground, the R lineage, the ensembles, the bench and the
long-term rows, then the scoring re-read. The commands are in [DATA.md](DATA.md). The heavy daily steps took
about 80 minutes on cloud compute; the tests do not need them.

## References

- Gardner, J. K., Knopoff, L. (1974). Bull. Seismol. Soc. Am. 64, 1363–1367.
- Helmstetter, A., Kagan, Y. Y., Jackson, D. D. (2006). Comparison of short-term and time-independent
  earthquake forecast models for southern California. Bull. Seismol. Soc. Am. 96, 90–106.
- Helmstetter, A., Kagan, Y. Y., Jackson, D. D. (2007). High-resolution time-independent grid-based forecast
  for M≥5 earthquakes in California. Seismol. Res. Lett. 78, 78–86. https://doi.org/10.1785/gssrl.78.1.78
- Lombardi, A. M., Marzocchi, W. (2010). The ETAS model for daily forecasting of Italian seismicity in the
  CSEP experiment. Ann. Geophys. 53(3). https://doi.org/10.4401/ag-4848
- Ogata, Y. (1988). J. Am. Stat. Assoc. 83, 9–27. Ogata, Y. (1998). Ann. Inst. Stat. Math. 50, 379–402.
- Reasenberg, P. (1985). J. Geophys. Res. 90, 5479–5495.
- Schorlemmer, D., Woessner, J. (2008). Bull. Seismol. Soc. Am. 98, 2103–2117.
- Uhrhammer, R. (1986). Earthquake Notes 57, 21.
- Weichert, D. H. (1980). Bull. Seismol. Soc. Am. 70, 1337–1346.
- Zhuang, J., Ogata, Y., Vere-Jones, D. (2002). J. Am. Stat. Assoc. 97, 369–380.
- Data sources and baseline forecasts: [DATA-SOURCES.md](../DATA-SOURCES.md).
