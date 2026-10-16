# Test rules: scoring, uncertainty, verdicts and evidence levels

This document states how a forecast is scored, how its uncertainty is measured, which consistency tests are
run, and when a row counts as a pass. The rules follow the CSEP practice (Schorlemmer et al. 2007; Zechar et
al. 2010; Rhoades et al. 2011) with corrections for clustered seismicity. They were re-read and tightened on
2026-10-15; the frozen rule of that re-read is `records/MC2/KURAL.md` and its code is `knotenlinie/puan2/`.

## 1. Score

- **Likelihood:** Poisson log-likelihood per day, cell and magnitude bin, including log(n!). Static forecasts
  are called once and split over days in proportion to time; time-dependent forecasts are called every day.
- **Information gain:** IG = (logL_candidate − logL_baseline) / N, in nats per earthquake. It contains both the
  event term (the log ratio of rates at the observed earthquakes) and the integral term (the difference in
  expected totals over all cells, empty ones included). The log(n!) term is model-independent and cancels.
- **No floors:** zero rates are not raised and no event is dropped. An observed earthquake in a cell with zero
  rate gives logL = −∞; the comparison is then recorded as undefined, with the reason, and the model cannot
  win it.
- **Reading IG:** exp(IG) is the geometric-mean probability ratio; +0.1 nat ≈ 1.11 times, +0.35 nat ≈ 1.42
  times.

## 2. Uncertainty

- **Weekly block standard error.** UTC Monday weeks, partial and zero-event weeks included. With D_w the
  week's log-likelihood difference, N_w its target count and B the number of blocks:
  SE_block² = B/(B−1) · Σ_w (D_w − IG·N_w)² / N². This is the cluster-robust sandwich error of a ratio
  estimator; it does not claim to remove all time dependence.
- **HAC (Newey–West) standard error.** Daily gains D_t with u_t = D_t − IG·n_t, Bartlett kernel,
  SE_HAC = sqrt(T/(T−1) · [Σu_t² + 2 Σ_{l=1..L} (1 − l/(L+1)) Σ_t u_t u_{t−l}]) / N, lag
  L = floor(4 (T/100)^(2/9)) (7 for 1826 days, 8 for 3653 days), the Diebold–Mariano form of the error.
- **z and p.** z = IG/SE, one-sided. One-sided z > 1.645 is the same as a two-sided 90 % level (two-sided
  p < 0.10), and the tables say so.
- **Paired T and W tests.** Two-sided paired T test and Wilcoxon signed-rank test on per-event log ratios with
  the total terms. W is used when N < 30, T otherwise. Both assume independent events, so under clustering
  they are optimistic: in Italy at M≥2.95 the W-test p-values of the four daily rows are 1e−9 to 1e−15, while
  their HAC z-values are at most about 1.1 (two-sided p ≈ 0.28). T/W never decide a row alone.
- **Long-term rows** have one time window, so HAC is undefined; their SE is an event bootstrap (2000
  replicates), which does not account for clustering.

## 3. Consistency tests

Reported beside every row; they do not enter the verdict.

- **N test, Poisson:** two tails, each ≥ 0.025.
- **N test, negative binomial (NBD):** δ1 = P(X ≥ N), δ2 = P(X ≤ N) with X ~ NBD(mean Λ, variance V),
  V = Λ + aΛ²; pass ⇔ min(δ1, δ2) ≥ 0.025 (Zechar 2010; pyCSEP `negative_binomial_number_test`). The single
  parameter a is estimated only from calibration data: windows of the test-window length (1826 days) starting
  in 1985, sliding by 30 days, ending before 2011; a = max(0, (v − m)/m²). For Italy a = 0.13, 0.11 and 0.14 at
  M≥2.95, 3.95 and 4.95. Overlapping windows make the estimate loose (about 5 independent windows) and the
  resulting distribution very wide (standard deviation about 44 instead of 11 at N = 130): the NBD test
  relaxes the Poisson test but rejects almost nothing. Sensitivity rows with a × 0.5 and a × 2 are stored and
  change nothing.
- **S and M tests:** spatial and magnitude marginals normalised to the observed N, 10,000 fixed-N multinomial
  simulations, lower tail (1 + k)/(1 + R), seeds 20261005 (S) and 20261006 (M).
- **Binary likelihood:** p = 1 − exp(−λ) per day, cell and bin; the exact joint binary log-likelihood is
  computed from the ledger, lnL = Σ_{distinct occupied day-cell-bins} [ln(1 − e^{−λ}) + λ] − Λ_total. Binary S
  and L tests run on the time-aggregated cell × bin marginal with the pyCSEP protocol (R = 10,000; seeds
  20261007 and 20261008), because the ledgers do not hold daily rates for every cell.

These tests are operational, conditional diagnostics for a daily, history-dependent model; they are not an
unconditional calibration test of ETAS under its own generator.

## 4. Verdict rule

For every row (candidate − baseline):

- **pass** ⇔ IG > 0 and z_block > 1.645 and z_HAC > 1.645 and (N < 30 ? p_W < 0.10 : p_T < 0.10);
- **fail** ⇔ IG ≤ 0;
- **undecided** otherwise.

Long-term rows drop the z_HAC condition (HAC is undefined for a single window) and use the asymptotic W p-value
of the rule; exact W, a tie-corrected permutation W and a tie flag are side columns only. The earlier rule was
pass ⇔ IG > 0 and z_block > 1.645.

**Component acceptance (daily).** A new component enters the finalist model only if, on 2011–2015 against R,
it gives IG > 0 and z > 1.645 at M≥2.95 and IG > 0 at M≥3.95. The verdict row is then against ETAS-LM.
Selecting at M≥2.95 and reporting at M≥3.95 can inflate a gain (Mizrahi et al. 2021), so every selection
reports the M≥3.95 row beside it.

**Multiple comparisons.** Holm's step-down correction within a family fixed in advance; an undefined p counts
as 1 and stays in the family.

## 5. Rules are written before scoring

Every experiment writes its rule file `KURAL.md` before the period it rules is scored: models and build ends,
the fixed candidate list, the selection rule, the rows to report and the tests. Its SHA-256 is stored in the
experiment's measurement or selection record, and the drivers refuse to run if the rule file and the stored
hash disagree. Addenda written later carry a date and say whether they change any verdict; the first hash is
kept next to the new one. In this release the frozen rule files are kept verbatim in Turkish apart from
required edits, and every re-anchored hash is listed in `records/HASHES.md`.

Example (`records/U/KURAL.md`, the ensemble experiment): three fixed ensembles; simplex weights that maximise
the 2006–2010 M≥2.95 log-likelihood; equal weights written in advance as a second row; no member removed when
its weight goes to zero; the weights stored before the 2011–2015 ledgers are produced; Holm over the three
ensembles at each threshold. The equal-weight row is the one that did best, and it was written down before
any ensemble was scored.

## 6. Evidence levels

Every row carries its level:

| Level | Meaning |
|---|---|
| **P** | Prospective: the forecast was frozen before the earthquakes happened. |
| **SP** | Pseudo-prospective: parameters were frozen before a past test window. |
| **G** | Retrospective or in-sample. |
| **SP-ic** | Internal validation: our 2011–2015 Italian rows and the 2011–2020 development bench. The windows were looked at by many experiments, so this is weaker than a once-only test. |
| **SP-blind** | The once-only 2016–2020 Italian blind window, after the preregistration is frozen. |
| **P vs SP** | Our pseudo-prospective forecast scored against forecasts that were truly prospective (the CSEP California archive). |

All current rows are **SP-ic**. A result found after the scored period was seen (a post-hoc variant) is
labelled **G** and never replaces the registered row.

## 7. What the CSEP-standard re-read changed

The 2026-10-15 re-read applied the rules above to the existing ledgers; no model was re-run.

- **One verdict changed.** AH − TripleS-CPTI, all events, M≥4.95, N = 14, Italy: pass (z 1.83) under the old
  rule, undecided under the new one (asymptotic p_W 0.124, p_T 0.104; exact 0.135, permutation 0.131).
  AH − MPS04 on the same row stays a pass but is borderline: p_W 0.096 asymptotic, 0.100 tie-corrected
  permutation, 0.104 exact (14 events in 12 cells, so ties exist and the exact test is invalid).
- **All other Italy and California rows kept their verdicts.** In Italy, 2011–2015, neither R, AJ, the
  equal-weight R+ETAS-LM nor E7 beats ETAS-LM at any threshold. In southern California D1 − D0 stays a pass
  (z_block 2.09, z_HAC 2.04).
- **HAC confirmed the weekly blocks:** SE_HAC / SE_block = 0.97–1.04 over 14 rows.
- **Thresholds side by side:** no Italian verdict flips between M≥2.95 and M≥3.95; only the sign of R − LM
  changes (−0.027 → +0.025), both not significant.
- **Binary likelihood** departs from the Poisson IG by ≤ 1e−3 at M≥4.95; at M≥2.95 several events in one
  day-cell lower the binary score (R − LM −0.050 against −0.027) without changing the sign or verdict. S tests
  give p ≈ 1 everywhere: the S test does not discriminate here.
- **Open:** the southern California ledger has no daily Λ above M≥3.95, so NBD, S/M and binary S/L are missing
  there; the New Zealand row and the ten-year California row were not re-read.

**Cross-check against pyCSEP 0.8.0** on shared inputs: NBD N test 1e−14, Poisson N test 6e−16, binary
log-likelihood identical, binary S/L identical with the same seed, T/W 1e−15, HAC against statsmodels 2e−15.
The scoring code does not depend on pyCSEP (the cross-check script is optional).

**Independent review** of the re-read code found two errors before acceptance: the code used an exact W test
where the rule names the asymptotic one (this had flipped AH − MPS04 to undecided), and the long-term verdict
did not follow the rule's form. Both were fixed, an addendum to the rule says that no verdict changes, and the
same reviewer accepted the fixed version.

## 8. The "we passed" rule for the blind window

The rule that will decide the 2016–2020 blind window is a draft and is not frozen. Its elements:

- named, frozen candidates per horizon; IG > 0 against the named baseline; significance with the weekly
  block and HAC errors; W for small N; NBD-based consistency; Holm families fixed in advance; the evidence
  level on every row;
- in the draft, a primary comparison (R − ETAS-LM, daily, M≥3.95) and secondary comparisons against the
  frozen CSEP-Italy forecasts at M≥4.95; a row passes with IG > 0, z > 1.645 and Holm p < 0.05; a secondary
  result cannot rescue the primary;
- the code helper `karsilastir.puan.gectik` holds one Holm family of three Italian comparisons (against
  HAZFX-BPT, TripleS-CPTI and our plain ETAS).

The final family, the reading order and the opening procedure are fixed only when the preregistration is
frozen ([SEAL-AND-BLIND-WINDOW.md](SEAL-AND-BLIND-WINDOW.md)). The expected power is low:
for the Italian primary comparison the chance of a pass is about 25 %.

## References

- Brehmer, J. R., Kraus, K., Gneiting, T., Herrmann, M., Marzocchi, W. (2024). Seismol. Res. Lett.,
  https://doi.org/10.1785/0220240209 (method sections only).
- Diebold, F. X., Mariano, R. S. (1995). J. Bus. Econ. Stat. 13, 253–263.
- Mizrahi, L., Nandan, S., Wiemer, S. (2021). J. Geophys. Res. 126, https://doi.org/10.1029/2021JB022379
- Newey, W. K., West, K. D. (1987). Econometrica 55, 703–708.
- Rhoades, D. A., Schorlemmer, D., Gerstenberger, M. C., Christophersen, A., Zechar, J. D., Imoto, M. (2011).
  Acta Geophys. 59, 728–747. https://doi.org/10.2478/s11600-011-0013-5
- Savran, W. H. et al. (2022). pyCSEP. J. Open Source Softw. https://doi.org/10.21105/joss.03658
- Schorlemmer, D., Gerstenberger, M. C., Wiemer, S., Jackson, D. D., Rhoades, D. A. (2007). Seismol. Res.
  Lett. 78, 17–29. https://doi.org/10.1785/gssrl.78.1.17
- Werner, M. J., Helmstetter, A., Jackson, D. D., Kagan, Y. Y. (2011). Bull. Seismol. Soc. Am. 101, 1630–1648.
  https://doi.org/10.1785/0120090340
- Zechar, J. D., Gerstenberger, M. C., Rhoades, D. A. (2010). Bull. Seismol. Soc. Am. 100, 1184–1195.
  https://doi.org/10.1785/0120090192
