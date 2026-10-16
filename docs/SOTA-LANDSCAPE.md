# State of the art in earthquake forecasting, by evidence level

A literature survey made on 2026-10-15 to answer one question: what has been shown to work, at which horizon,
and at what level of evidence? It decided the order of work in [HOW-WE-WORK.md](HOW-WE-WORK.md). Five search
arms covered short-term ETAS and operational systems, machine learning, physics-based and hybrid models and
ensembles, long-term forecasts, and reviews and scoring; a sixth arm audited the time windows of the key
papers against our seal.

**Reading level.** Full-text access failed for most papers, so most numbers come from abstracts. Where a number
could not be checked it is marked "not verified".

**Evidence levels.** **P**: prospective, the forecast was frozen before the earthquakes. **SP**: pseudo-
prospective, parameters were frozen before a past test window. **G**: retrospective or in-sample. Our own
2011–2015 internal validation is SP (more precisely SP-ic, see [TEST-RULES.md](TEST-RULES.md)).

## 1. Short answer

- Once tied to evidence, "state of the art" is not one model. It is a significant information gain against a
  named, frozen baseline, in a prospective window, while also passing the consistency tests.
- Three classes win consistently in prospective tests:
  - **days ahead:** the ETAS class (and related triggering models such as STEP);
  - **years ahead:** smoothed seismicity adapted to small earthquakes (the HKJ family), at least in
    California and New Zealand; in Italy the best five-year models also used faults and the historical
    catalogue;
  - **months to a few years:** EEPAS, so far mainly in New Zealand.
- Beyond these, no method has been shown to beat an established baseline in a prospective test. Some have shown
  gains in pseudo-prospective tests, on one sequence or one region.
- Our standing (internal, SP): we cannot tell our daily Italian models apart from the published Italian ETAS,
  and our ten-year California model apart from HKJ07; the best five-year Italian model (HAZFX-BPT) is ahead of
  ours on 7 earthquakes. We have no medium-term product.
- **No contradiction.** The literature says that our long list of layers with no gain is the general finding of
  the field, not a build error.

## 2. Horizon by horizon

| Horizon | What wins with prospective evidence | Evidence | Where we stand (SP-ic) | Open |
|---|---|---|---|---|
| Days | ETAS class. Probability gain over time-independent models of two to three orders of magnitude. Differences among ETAS variants are small and their ranking changes from period to period; variants calibrated with small earthquakes and with finer smoothing are slightly ahead. Bayesian ensembles did not beat their components. STEP led in 2007–2012. | California CSEP, Aug 2007 – Aug 2018, 597 events M≥3.95, 21 models (Bayona et al. 2026, P); New Zealand testing centre (Rhoades et al. 2018); Japan, Tohoku sequence (Schorlemmer et al. 2018) | R vs ETAS-LM, Italy M≥3.95: +0.025 ± 0.112, undecided. California: our period-Mc ETAS beat our plain ETAS by +0.280 ± 0.134 | No prospective anchor yet |
| Months to a few years | EEPAS and double-branching models beat smoothed seismicity for three-month forecasts in New Zealand. Global EEPAS, M≥7.45, 2014–2019, N = 19: +0.81 nat/eq against PPE, +0.37 to +0.43 against a strain-rate baseline | Rhoades et al. 2018 (P and G mixed); Geosciences 16:267, 2026 (SP, parameters frozen on 1994–2013; authors not verified) | No product at this horizon. On a daily grid an EEPAS weight near zero is expected | Horizon missing |
| Five years and more | Adaptive smoothed seismicity (HKJ) was the most informative model in RELM 2006–2010 and 2011–2020; none of 16 multiplicative hybrids built on it beat it prospectively. In Italy 2009–2014 the best five-year models combined faults and historical seismicity (qualitative) | Zechar et al. 2013, Bayona et al. 2022 (P); Taroni et al. 2018 (P, window inferred as 2009–2014) | California: +0.35 ± 0.18 against HKJ07 (N = 22), not significant. Italy: HAZFX-BPT ahead, −0.35 ± 0.45 (N = 7) | Our Italian long-term shape does not use the historical catalogue |

## 3. Without evidence, or below our resolution

| Method | Best evidence | Ours | Verdict |
|---|---|---|---|
| ETAS variants: completeness-tolerant ETAS, magnitude-dependent Omori, spatially varying parameters, anisotropic or finite-source kernels | SP, about 0.03–0.1 nat/eq; the gain falls as the target threshold rises and is not significant at M≥3.5 and above (Mizrahi et al. 2021) | R already uses events down to the time-varying Mc as triggers; finite source +0.004 | Not built further; gain below resolution |
| Multiplicative hybrids (strain rate, faults, GEAR1 background) | Won in G, collapsed in P, because the hybrid fit is unstable in time (Bayona et al. 2022) | GEAR1 background and fault budget gave no gain | Not built |
| Coulomb rate-and-state (CRS) | Only in individual aftershock sequences, over days to months; needs secondary triggering, finite slip and heterogeneous receiver faults | +0.026 at M≥4.95 on an earlier baseline, no secondary triggering; −0.005 at M≥3.95 on the corrected one | Not built alone; sequence-based physics is a later topic |
| BPT, renewal, seismic gap | No prospective support (Rong et al. 2003; Kagan et al. 2012) | Italy +0.010 | Not built |
| Neural networks and ML | A fair SP gain only when small earthquakes are inputs (Zlydenko et al. 2023, Japan: +0.12 to +0.41 bit/eq, i.e. +0.08 to +0.28 nat/eq); in EarthquakeNPP five neural point processes did not beat ETAS | Gradient boosting −0.29 | Not built |
| Ensembles with selected weights | Italy, one day, P: the ensemble was as good as the best model, not better (Taroni et al. 2018). California: Bayesian ensembles did not beat their components (Bayona et al. 2026). In econometrics, the "forecast combination puzzle": equal weights beat estimated weights (Smith and Wallis 2009) | Selected weights < equal weights | Equal or shrunk weights only |

## 4. Order of work this implies

Every step must say in one line which score it moves, against which baseline. Score-producing code is reviewed
independently once.

1. **Bring the scoring to the pyCSEP standard.** Negative-binomial number test; binary likelihood for
   clustering-aware S and L tests; HAC/Diebold–Mariano errors next to the weekly blocks; the W test for small N;
   gains reported at M≥2.95 and M≥3.95 side by side. Basis: Werner et al. 2011, Nandan et al. 2019, Savran et
   al. 2020, Bayona et al. 2022 and 2026, Brehmer et al. 2024 (method only), Mizrahi et al. 2021. **Done** on
   2026-10-15 ([TEST-RULES.md](TEST-RULES.md) §7).
2. **A prospective anchor: the CSEP California next-day archive.** Fit R on data up to July 2007, produce daily
   M≥3.95 forecasts for 1 August 2007 – 30 August 2018 on the archive's grid (7,682 cells × 51 magnitude bins =
   391,782 rows, 0–30 km) and score them with the same tests against the archived models, which include
   ETAS-PPE, ETAS-HW-KERNEL and STEP. Archive: Zenodo record 15076187 (HDF5); reproduction code:
   `github.com/bayonato89/reproducibility_next_day_california`. Report in nats per earthquake and in the
   archive's own unit (IGPA, per active cell). Honesty note: the archived models are truly P; our side is SP,
   because R's design was chosen while looking at southern California 2011–2020. It still gives the best
   available answer to "where are we against operational models", with 4.6 times the Italian N = 130.
   The archive is a 56.5 GB zip (about 120 GB unpacked), so this runs on cloud compute.
3. **Medium term: Janus (R + EEPAS) at three-month and one-year horizons**, built with PyEEPAS
   (`github.com/phonchi/EEPAS`, MIT), target M≥5 (M≥4.95 in Italy). Scored as Janus − R and Janus − smoothed
   seismicity, in California (fit ≤2010, test 2011–2020) and Italy (fit ≤2010, test 2011–2015). Basis: New
   Zealand three-month forecasts (P, Rhoades et al. 2018), global EEPAS (SP), Janus over ETAS +0.2 to +0.5
   (G, Rhoades 2013, 2022). Expected: positive sign, size uncertain (±0.3); the power comes from California.
4. **Italian long term: historical catalogue plus faults with a sharp spatial kernel**, to capture the spatial
   concentration of HAZFX-BPT (its top 10 % of cells carry 69 % of its rate). Basis: Taroni et al. 2018
   (qualitative); Werner et al. 2010 (an over-sharp model is rejected). Scored as X − HAZFX-BPT, Italy, five
   years, declustered M≥4.95; because N = 7, the same recipe also runs in California against HKJ07.

Deferred: simulation-based forecasts with parameter uncertainty (full Bayesian ETAS); it is a large task and
waits for the result of step 2.

## 5. Effect on the "we passed" rule

- The rule already follows the standard: a paired comparison against a baseline, N/S/M consistency and Holm.
- Four changes were made with step 1, before any preregistration freeze: NBD for consistency, HAC errors, W for
  small N, and the evidence level on every row (internal validation SP-ic; the blind window SP-blind; against
  the CSEP archive "P vs SP").
- **Mizrahi et al. (2021) warning:** selecting at M≥2.95 and reporting at M≥3.95 can inflate a gain. Selection
  stays at M≥2.95, but every selection reports the M≥3.95 row beside it, and a component must show the same sign
  in California at M≥3.95.

## 6. Quarantine

Papers whose evaluation reaches the sealed years, or reports Italian results for the blind window, are read for
method only ([SEAL-AND-BLIND-WINDOW.md](SEAL-AND-BLIND-WINDOW.md) §3). The most important results we could not
see: the ten-year results and ensemble weights of the Italian operational forecasting system, the Italian EEPAS
test, the prospective GEAR1 test, and the data-size threshold of RECAST. None of them changes the order of work.

## 7. Not verified, or in conflict

- Most numbers come from abstracts.
- Zlydenko et al. (2023), FERN+ gain: one arm read "about 0.1 bit/eq", another 0.12–0.41 bit/eq from the
  paper's Table 1.
- Serafini et al. (2025: August 2008 – August 2018, 571 events) and Bayona et al. (2026: August 2007 –
  August 2018, 597 events) differ in period; step 2 resolves this when the archive is downloaded.
- The sign of the monthly CRS gain for Ridgecrest: one reading says CRS below ETAS, the text of Mancini et al.
  (2020) shows the best CRS above ETAS over the first month.
- The context of the "≈6.0 gain" in Werner et al. (2011) was not verified.

## References

Short term and operational systems

- Bayona, J. A. et al. (2026). Nat. Commun. 17, 9444. https://doi.org/10.1038/s41467-026-76243-7
- Cattania, C. et al. (2018). Seismol. Res. Lett. 89(4), 1238–1250.
- Lombardi, A. M., Marzocchi, W. (2010). Ann. Geophys. 53(3). https://doi.org/10.4401/ag-4848
- Mancini, S., Segou, M., Werner, M. J., Parsons, T. (2020). Bull. Seismol. Soc. Am. 110(4), 1736.
  https://doi.org/10.1785/0120200028
- Mizrahi, L., Nandan, S., Wiemer, S. (2021). J. Geophys. Res. 126. https://doi.org/10.1029/2021JB022379
- Mizrahi, L. et al. (2024). Rev. Geophys. 62. https://doi.org/10.1029/2023RG000823
- Nandan, S., Ouillon, G., Sornette, D., Wiemer, S. (2019). Seismol. Res. Lett. https://doi.org/10.1785/0220180374
- Savran, W. H. et al. (2020). Bull. Seismol. Soc. Am. https://doi.org/10.1785/0120200026
- Schorlemmer, D. et al. (2018). Seismol. Res. Lett. 89. https://doi.org/10.1785/0220180053
- Serafini, F. et al. (2025). Sci. Data 12, 1501. https://doi.org/10.1038/s41597-025-05766-3
- Zlydenko, O. et al. (2023). Sci. Rep. 13. https://doi.org/10.1038/s41598-023-38033-9

Machine learning

- Mignan, A., Broccardo, M. (2020). Seismol. Res. Lett. https://doi.org/10.1785/0220200021
- Stockman, S., Lawson, D. J., Werner, M. J. (2026). EarthquakeNPP. Trans. Mach. Learn. Res.; arXiv:2410.08226

Physics-based models, hybrids and ensembles

- Bayona, J. A., Savran, W. H., Rhoades, D. A., Werner, M. J. (2022). Geophys. J. Int. 229, 1736.
  https://doi.org/10.1093/gji/ggac018
- Rhoades, D. A. (2013). Bull. Seismol. Soc. Am. 103(4), 2203. https://doi.org/10.1785/0120120233
- Rhoades, D. A. et al. (2018). Seismol. Res. Lett. 89(4), 1229–1237. https://doi.org/10.1785/0220180032
- Rhoades, D. A. (2022). Geosciences 12(9), 349. https://doi.org/10.3390/geosciences12090349
- Smith, J., Wallis, K. F. (2009). Oxf. Bull. Econ. Stat. 71, 331. https://doi.org/10.1111/j.1468-0084.2008.00541.x
- Taroni, M. et al. (2018). Seismol. Res. Lett. 89(4), 1251. https://doi.org/10.1785/0220180031

Long term

- Bird, P. et al. (2015). GEAR1. Bull. Seismol. Soc. Am. 105, 2538–2554. https://doi.org/10.1785/0120150058
- Helmstetter, A., Kagan, Y. Y., Jackson, D. D. (2007). Seismol. Res. Lett. 78, 78–86.
  https://doi.org/10.1785/gssrl.78.1.78
- Kagan, Y. Y., Jackson, D. D., Geller, R. J. (2012). Seismol. Res. Lett. 83. https://doi.org/10.1785/0220120107
- Rong, Y., Jackson, D. D., Kagan, Y. Y. (2003). J. Geophys. Res. 108, 2471. https://doi.org/10.1029/2002JB002334
- Werner, M. J., Zechar, J. D., Marzocchi, W., Wiemer, S. (2010). Ann. Geophys. 53(3). https://doi.org/10.4401/ag-4840
- Zechar, J. D. et al. (2013). Bull. Seismol. Soc. Am. 103(2A). https://doi.org/10.1785/0120120186

Reviews and scoring

- Brehmer, J. R., Kraus, K., Gneiting, T., Herrmann, M., Marzocchi, W. (2024). Seismol. Res. Lett.
  https://doi.org/10.1785/0220240209 (method sections only)
- Graham et al. (2024). Seismol. Res. Lett. https://doi.org/10.1785/0220240197
- Khawaja et al. (2023). Geophys. J. Int. 233. https://doi.org/10.1093/gji/ggad030
- Savran, W. H. et al. (2022). pyCSEP. J. Open Source Softw. https://doi.org/10.21105/joss.03658
- Werner, M. J., Helmstetter, A., Jackson, D. D., Kagan, Y. Y. (2011). Bull. Seismol. Soc. Am. 101, 1630–1648.
  https://doi.org/10.1785/0120090340
- Werner, M. J., Sornette, D. (2008). J. Geophys. Res. 113. https://doi.org/10.1029/2007JB005427
