# What did not work

Every layer below was added on its own, scored against the same baseline as everything else, and measured
against a bar fixed in advance (the component acceptance rule in [TEST-RULES.md](TEST-RULES.md) §4: on
2011–2015 against R, IG > 0 and z > 1.645 at M≥2.95 and IG > 0 at M≥3.95). None cleared it. Several showed a
small positive gain that did not clear the bar; a small gain is reported as what it is, not as zero.

Unless stated otherwise: Italy, daily frame of [METHOD.md](METHOD.md) §1, 2011–2015, IG in nats per earthquake
± weekly-block SE, level **SP-ic** (internal validation). "Common baseline" is the plain ETAS of the common
ground (Mc 3.1); its target counts differ slightly from the J/R frame (N = 136 against 130 at M≥3.95). A
variant built after the 2011–2015 result was seen is marked **G** (post hoc).

The literature says the same for most of these classes; see [SOTA-LANDSCAPE.md](SOTA-LANDSCAPE.md) §3.

## Summary

| Layer | Measured | Level | Code in this release |
|---|---|---|---|
| Tides and loads (six physical channels) | ≤ about 1e−4 nat/eq per channel | SP-ic | no (to come) |
| Mantle flow (long-memory loading) | −0.061 mm/yr velocity change, below the 0.5 mm/yr step | model check, no score | no |
| Coulomb rate-and-state (CRS) | −0.005 ± 0.006 at M≥3.95 | SP-ic | yes |
| BPT renewal on faults | +0.010 | SP-ic | yes |
| Machine-learning member | −0.285 ± 0.267 at M≥3.95 | SP-ic | yes |
| STEP-type model | −0.612 ± 0.184 at M≥3.95 | SP-ic | yes |
| Short-term incompleteness (STAI, HKJ correction) | selection chose R; bench −0.016 and −0.297 | SP-ic | yes |
| Finite-source kernel | +0.0040 ± 0.0030 against R at M≥3.95 (z 1.32) | SP-ic | yes |
| Hierarchical shrinkage | not reproducible from this release's data | – | yes |
| Fault slip-rate budget (daily background) | +0.023 ± 0.019 at M≥3.95 (p 0.235) | SP-ic | yes |
| EEPAS / Janus on the daily grid | −0.008 ± 0.011 at M≥3.95 | SP-ic | yes |
| Ensembles with selected weights | best +0.041 ± 0.070 | SP-ic | yes |
| GEAR1 background | weight 0 selected | SP-ic | no |
| Total-rate rescaling | +0.025 → −0.024 | SP-ic | yes |
| Period-Mc ETAS in New Zealand | −0.139 ± 0.130 | SP-ic, development bench | yes |

## Physical forcing

### Tides and loads

Six physical channels were measured on the Italian fault set: the solid Earth tide, ocean-tide loading, the pole
tide, changes in the length of day, continental water load, and ice and sea level. Each was added alone, all
were added together, and each was left out in turn: 16 models and 5,503,680 rows, scored on 2011–2015
earthquakes that the models had not seen. Over 2011–2015 no channel added more than about **1e−4 nat per
earthquake**; the largest, from the solid Earth tide, did not survive the correction for multiple tests. Air
pressure and rain were not measured.

This does not prove that the effects are zero. In the region and magnitude range tested they are far too small
to help a forecast; published work reports tidal effects on the size distribution of large earthquakes that
this test could not see.

**Code:** not in this release. The channel code calls an external tide engine that cannot be redistributed. A
clean-room body-tide module following the IERS Conventions (2010) is planned for a later release.

### Mantle flow

A simple mantle-convection model was tested as a source of long-memory loading. Its contribution to Italian
surface velocity was **−0.061 mm/yr** (numerical uncertainty 0.004 mm/yr), well below the 0.5 mm/yr step at
which it could change the loading input of the fault model. Italy-specific follow-up work was stopped. The layer
never reached a forecast score; this is a model check, not a forecast measurement, and it does not close other
regions or other physics.

**Code:** not in this release (it depends on external solver runs).

### Coulomb rate-and-state (CRS)

Dieterich (1994) rate-and-state seismicity response to Coulomb stress steps from M≥5 sources (Okada
dislocations, Wells–Coppersmith scaling), applied to the background of the common ETAS on 126 DISS 3.2.0
receiver sources.

- Corrected common baseline, weights chosen on 2006–2010 (Aσ = 300 kPa, w = 0.25): M≥3.95, N = 136:
  **−0.0046 ± 0.0063** (paired T p 0.47). M≥4.95, N = 14: +0.033, but the event term is negative (−0.014)
  and the gain comes from suppressing the expected count (+0.046), not from higher rates where earthquakes
  happened.
- Earlier common baseline: +0.026 at M≥4.95 (N = 14), again from count suppression (event term −0.001).
- No secondary triggering, no finite slip, single receiver point per source. The literature gain for CRS is in
  individual sequences over days to months, with exactly those ingredients.

**Code:** `knotenlinie/crs/`, with the ledger code `defter/`, the elastic kernels `elastik/`, the source
scaling and transfer `kanal/` and the DISS reader `diss320/`.

### BPT renewal on faults

Inside the fault-based long-term model (AH), turning BPT on for the sources with a known last event changed the
2011–2015 declustered M≥4.95 score by **+0.010** nat/eq (characteristic variant +0.011). In Italy 98
individual sources have a known last event; BPT moves their total by about 15 %. Fault *location* (moment-weighted space) carries information; time dependence does not, at this
resolution. **Code:** `knotenlinie/fay_zaman/bpt.py`.

## Daily statistical members

### Machine-learning member (gradient boosting)

Cell-day Poisson gradient boosting on past counts, the last large event, the background and R's log rate; trained
on ≤2005, selected on 2006–2010. ML − ETAS-LM: M≥2.95 **−0.421 ± 0.147**, M≥3.95 **−0.285 ± 0.267**, M≥4.95
−0.220 ± 0.522. Its per-event log rate correlates 0.93–0.95 with R's, because R's rate dominates its feature
importance: it is neither different enough from R nor good enough on its own. **Code:** `knotenlinie/ml_uye/`
(needs scikit-learn).

### STEP-type model

A daily model in the STEP family (generic and sequence-specific Reasenberg–Jones, kernel background), written
from the papers' descriptions; the original code and tables were not available, so it is STEP-type, not a
copy of STEP. STEP − ETAS-LM: M≥3.95 **−0.612 ± 0.184**,
M≥2.95 −0.739 ± 0.121; equal {R, ETAS-LM, STEP} − ETAS-LM −0.011 ± 0.076. Its log rates correlate 0.91 with R and
ETAS-LM, so it is a genuinely different member, but it adds no gain and its total is mis-calibrated (Λ 156
against 130 observed). A post-hoc hierarchical variant (**G**) scored −0.297 ± 0.075 at M≥2.95. The published
STEP model itself did well in the CSEP California tests; our STEP-type addition did not raise our score.
**Code:** `knotenlinie/step/`.

### Short-term incompleteness

- **On R in Italy (STAI):** the pre-registered 2006–2010 selection chose R itself, so the layer is R
  (W − R = 0). Exploratory rows: W-a − R at M≥2.95 −0.0028 ± 0.0012; no measurable post-event deficit at the
  M≥2.5 level with day-start forecasts.
- **HKJ correction on the bench:** D2 − D1 −0.016 ± 0.005 (southern California, M≥2.8) and −0.297 ± 0.047 (New
  Zealand, M≥3.8).
- Falsified in Italy, southern California and New Zealand. **Code:** `knotenlinie/etas_stai/`,
  `knotenlinie/yan_tezgah/`.

### Finite-source kernel

For M≥5 parents, R's spatial kernel spread along a rupture of Wells–Coppersmith length, oriented by the Global CMT
nodal plane or by the principal axis of the early aftershocks. Against R: M≥2.95 **+0.0036 ± 0.0024** (z 1.49), M≥3.95
+0.0040 ± 0.0030 (z 1.32); not enough for the bar. The gain sits in the large sequences (+0.011 to +0.014 for
targets near an M≥5 parent) but is diluted over five years. Carried unchanged to the southern California bench:
**+0.00026 ± 0.00057** (z 0.47, N = 3407). **Code:** `knotenlinie/etas_sonlu/`, `yan_tezgah/sonlu.py`.

### Hierarchical shrinkage

R's parameters are shrunk toward a core estimated from other fits of the same R-type model (empirical-Bayes
penalty on the log parameters, τ chosen on 2006–2010 from a fixed list, τ = ∞ being R itself). The code builds the
core from the southern California and New Zealand bench fits and from Italy's own 1985–2004 fit. The selection
and its scores are not reproducible from this release's data, so no number is quoted here. One observation does
not depend on the selection: the bench fits and Italy's 1985–2004 fit all end at the branching-ratio ceiling
(see [Development bench](#development-bench)), so a core built from them cannot pull R below the ceiling. R's
defect is its productivity level, not parameter noise. **Code:** `knotenlinie/etas_hiyerarsi/`,
`karsilastir/gunluk_ae.py`.

### Total-rate rescaling

Scaling R's rate by the 2006–2010 ratio of observed to expected counts lowered the score: cascade
+0.025 → **−0.024**, without cascade −0.025 → −0.069. **Code:** `knotenlinie/etas_uzun/olcek.py`.

## Background layers

### Fault slip-rate budget

A moment-conserving fault component (DISS 3.2.0 slip rates, μ = 30 GPa, truncated GR) mixed into the ETAS
background, weight and kernel width chosen on 2006–2010 on the corrected common baseline:

- full DISS 3.2.0: M≥3.95 **+0.023 ± 0.019** (p 0.235), M≥4.95 −0.007;
- only sources updated by 2010: weight 0.

An earlier measurement against a plain kernel-density base gave +0.799 with the full database but +0.078 with
sources updated by 2010: the large number is sensitive to fault information added after the fit period. **Code:**
`knotenlinie/fay_butce/`.

In the long-term model AH, the fault layer improves on the smoothed-seismicity model Z2 by +0.293 ± 0.297
(z 0.98, N = 7), not significant; AH is the current long-term row and keeps it.

### GEAR1 background

A background shaped by the global GEAR1 forecast: the 2006–2010 selection chose weight 0 in Italy (common
baseline, M≥3.95: −0.0013 ± 0.0020). Only a coarse 2° GEAR1 sample was available, not the 0.1° model, so this is
not a verdict on GEAR1 itself. The long-term shape candidate that used GEAR1 (U3 of experiment Z) also received
weight 0. **Code:** not in this release.

### EEPAS and Janus on the daily grid

EEPAS (precursory scale increase) and Janus (ETAS + EEPAS mixture), with the Janus weight chosen on 2006–2010
(w = 0.088): M≥3.95, N = 136: **−0.0078 ± 0.0106** (p 0.46); M≥4.95 −0.067 ± 0.018. A weight near zero on a
daily grid is what the literature leads one to expect: EEPAS's evidence is at horizons of months to years.
**Status:** the medium-term horizon where EEPAS has prospective support is not built yet; a Janus at three-month
and one-year horizons is on the roadmap. **Code:** `knotenlinie/eepas/`.

## Ensembles

### Selected weights

Simplex weights chosen on 2006–2010 M≥2.95:

- {R, ETAS-LM}: all weight went to ETAS-LM, so the ensemble *is* ETAS-LM (difference 0);
- {R, common ETAS, Mc 2.5 refit}: +0.041 ± 0.070 at M≥3.95;
- all five models: +0.004 ± 0.012.

The equal-weight {R, ETAS-LM} did better, +0.071 ± 0.072, and is carried forward as a candidate, not dropped.
Equal-weight mixtures with the new STEP-type and ML members (E1–E5, rule written before the members were scored):
best {R, ETAS-LM, ML} +0.097 ± 0.105 (Holm 0.89), worst {R, STEP, ML} −0.020 ± 0.125. The 2006–2010 selection
leans on one sequence (L'Aquila 2009), which is one reason selected weights are noisy. **Code:**
`knotenlinie/skor_defteri/`, `karsilastir/gunluk_u.py`, `karsilastir/topluluk2.py`.

## Development bench

### Period-Mc ETAS in New Zealand

The R-type ETAS (D1) that beats plain ETAS in southern California (+0.280 ± 0.134) does not in New Zealand:
D1 − D0 **−0.139 ± 0.130** at M≥3.8 (N = 2125); a small-scale trial on one year had shown +0.104. All New
Zealand forecasts under-predicted 2011–2020 (the Canterbury and Kaikōura sequences), and the fits end at the
branching ceiling. Level: SP-ic, development bench.

## Not a negative result

Layers that are part of a current row are not listed above as drops: the intraday cascade (part of R), the Mc 2.5
refit (part of R's lineage), the branching constraint (AJ, in the E7 row) and the fault layer of AH.

## References

- Dieterich, J. (1994). J. Geophys. Res. 99, 2601–2618.
- Gerstenberger, M. C., Wiemer, S., Jones, L. M., Reasenberg, P. A. (2005). Nature 435, 328–331.
- Helmstetter, A., Kagan, Y. Y., Jackson, D. D. (2006). Bull. Seismol. Soc. Am. 96, 90–106.
- Okada, Y. (1992). Bull. Seismol. Soc. Am. 82, 1018–1040. https://doi.org/10.1785/bssa0820021018
- Rhoades, D. A., Evison, F. F. (2004). Pure Appl. Geophys. 161, 47–72 (EEPAS).
- Wells, D. L., Coppersmith, K. J. (1994). Bull. Seismol. Soc. Am. 84, 974–1002.
