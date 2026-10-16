# How we work

This document describes the working method behind the code and the results: who does the work, which rules
decide what is built, kept and published, and the roadmap.

## 1. Our own harness

We develop our own harness. Many AI agents work at the same time: coordinating agents, one for each line of work
and one that coordinates across the lines, each directing its own parallel AI worker agents, and independent AI
reviewers from a different model family. One human maintainer oversees them all, catches the dialectical errors
(errors in the reasoning) and takes the decisions that cannot be delegated. On the technical side we start from published papers and work across disciplines and where they meet;
here, seismology, geodesy, hydrology and statistics. Compute runs on cloud services, and we manage everything
ourselves, with AI: the experiments, the compute, the reviews and this repository. We develop the harness, and the
harness develops our products, this model among them.

- **Experiments run in parallel.** Each experiment (R, J, AJ, U and so on) is one worker's task. A worker works
  on its own branch, writes only the files it owns, runs small-scale checks, and finishes with a short report:
  what was done, the tests, the numbers, the downloads (URL, date, SHA-256), the assumptions and what is still
  open. Workers do not merge, commit to the main line or open sealed data.
- **Coordinators** write the task descriptions, run the full-scale jobs on cloud compute, check each result,
  merge it after the tests pass and, for score-producing code, after independent review.
- **The maintainer decides** what cannot be delegated: when the blind window is opened, when the seal is
  opened, what is published, and spending.
- **Workers keep going.** A worker infers the intent from context and does not stop to ask; it makes a
  reasonable assumption and writes it down. If a gate is truly closed (data cannot be downloaded, a source does
  not exist), it names the gate, takes the best way around it and continues.

## 2. The score-chain gate

A task is opened only if it can say, in one line, which score it moves and against which baseline (for example
"R − ETAS-LM, Italy, daily, M≥3.95"). If there is no answer, the task is not opened. Work that does not connect
to a score is not invented to keep a worker busy; being idle is legitimate.

## 3. A layer must earn its place

A new layer is added on its own, scored against the same baseline as everything else, and kept only if its gain
clears a bar fixed in advance (the component acceptance rule, [TEST-RULES.md](TEST-RULES.md) §4). A layer whose
expected effect is below what the data can show cannot pass by definition. Several layers showed small positive
gains that did not clear the bar; they were dropped and their numbers published
([WHAT-DID-NOT-WORK.md](WHAT-DID-NOT-WORK.md)). Self-contained code for dropped layers stays in the repository so
the negative results can be checked.

## 4. Freeze before measuring

- **Rule file first.** Every experiment writes `KURAL.md` before the period it rules is scored: models, build
  ends, the fixed list of variants, the selection rule, the rows and tests to report. Its SHA-256 is stored in
  the experiment's records and the drivers check it. Addenda are dated and say whether they change a verdict.
- **Split.** Build on data up to 2005, choose on 2006–2010, rebuild on data up to 2010, score once on
  2011–2015. Nothing chosen changes after the score is seen. A variant built afterwards is reported as post hoc
  (level G) and never replaces the registered row.
- **Results are provisional** until the score-producing code has passed independent review.
- **Positive, null, unresolved.** A positive result must predict withheld data and survive independent
  nuisance and instrument checks. A null is an upper bound below the effect that physics requires. An interval
  too wide to exclude that effect is unresolved, not null; too few cycles is not a null.
- **Smallest observation first.** A claimed mechanism is tested first on the smallest observation of its
  endpoint (for accumulation: the retained change after unloading against an equal-mean static control; for
  transfer: amplitude, sign and phase on a withheld sensor or interval), without earthquake dates guiding the
  first test. A period match with no gain, bandwidth and phase is not a transfer.

## 5. The data split

- **Calibration ≤ 2015** for models that will face the blind window.
- **2016–2020: the Italian blind window**, opened once, after the preregistration is frozen and published.
- **2021 and later: sealed.** No earthquake data from these years is downloaded or opened.

The current rows are fitted on data up to 2010 and scored on 2011–2015 (Italy) or 2011–2020 (the southern
California and New Zealand development bench). Details: [SEAL-AND-BLIND-WINDOW.md](SEAL-AND-BLIND-WINDOW.md).

## 6. Independent review, in three places only

- **What is reviewed:** score-producing code (log-likelihoods, information gains, rate densities), the
  preregistration freeze, and data access that touches the seal. Documentation, metadata, bibliography and code
  custody are not sent to review.
- **How:** once, by an independent AI reviewer from a different model family than the author. A review does
  not trigger another review; the one exception is a real error in score-producing code, which is fixed and then
  checked once more by the same reviewer.
- **Status today:** the CSEP-standard scoring code (`knotenlinie/puan2/`), the R model and the ETAS-LM
  reconstruction have been reviewed and accepted. The other models behind the current rows have not been
  reviewed yet.

## 7. Testing

Score-producing code is tested in a synthetic world with a known answer (analytic Omori integrals, Poisson
identities, parameter recovery on simulated catalogues, mass conservation of kernels), and the score ledger must
reproduce the runner's log-likelihood difference to within 1e−9. Score code is run under two environments
(Python 3.9 with pandas 2 and Python 3.12 with pandas 3) and must give the same numbers. A check that has passed
is not re-run without a new reason.

## 8. Honest results

- A stage can close with "did not pass"; the result is written down by name and the stage closes.
- Ties are reported as ties: "not distinguishable" is not "level", and a small positive gain is not zero.
- Every number carries its evidence level; nothing internal is presented as prospective.
- **No permanent hardening.** A check added after an incident is removed when the root cause is fixed; a
  proposal for a new check comes with the condition under which it ends.

## 9. Roadmap

Every stage has an exit gate.

**Stage 0 (done, 5–15 October 2026).** Seven waves of experiments against established models, then a literature
survey. State (internal, SP): daily, not distinguishable from ETAS-LM; long term, not distinguishable from HKJ07,
with HAZFX-BPT ahead on 7 earthquakes. The literature's verdict: three classes win with prospective evidence:
ETAS for days, smoothed seismicity from small earthquakes for years, EEPAS for months to years
([SOTA-LANDSCAPE.md](SOTA-LANDSCAPE.md)).

**Stage 1: consolidate at the state-of-the-art level.**

| Task | What | Score chain |
|---|---|---|
| Scoring to CSEP standard (done 15 October) | NBD number test, binary likelihood, HAC errors, W test, evidence levels; existing rows re-read; no candidate beats ETAS-LM; one verdict changed | all existing rows |
| California next-day archive | R against the daily models tested prospectively by CSEP California, 2007–2018 | R − ETAS-PPE-M2 / ETAS-HW-KERNEL-M2 / STEP |
| Medium term | Janus (R + EEPAS) at three-month and one-year horizons | Janus − R and − smoothed seismicity, California and Italy |
| Italian long term | historical catalogue plus faults, sharp spatial kernel | X − HAZFX-BPT; the same recipe against HKJ07 in California |

Exit gate: the four rows are scored with the new scoring code, and the score code has passed independent review.
The outcome may be "did not pass"; it is then written down by name and the stage closes.

**Stage 2: preregistration and public announcement.** Frozen: the candidates per horizon, the "we passed" rule
(IG > 0 against the baseline, significance, NBD-based consistency, HAC errors, W for small N, Holm families, the
evidence level on every row) and the reading rule of the blind window. The freeze passes one independent review,
is pushed to the repository and is published, dated, on the project page before the window opens. The rule and
the fingerprints of every frozen forecast are deposited in one versioned Zenodo record per window and with an
independent timestamping service. Exit gate: the preregistration commit, the Zenodo DOI and the page are public.

**Stage 3: the blind window 2016–2020.** Italy. Opened once, by decision of the maintainer. The expected power
is low (about a 25 % chance of a pass for the Italian primary comparison). The result is published whether we
win or lose. Exit gate: the blind result is public.

**Stage 4: research to beat the baselines (unproven ground).** The literature suggests gains may exist here but
has no prospective evidence. Each line enters with a preregistered internal measurement; a line that does not
raise the score is dropped.

- Sequence physics: CRS with secondary triggering, against ETAS in large sequences (M≥6).
- Full-distribution forecasts: simulation with parameter uncertainty (Bayesian ETAS); R's total is too high,
  a general problem of the ETAS family.
- Medium term for large earthquakes: EEPAS with strain rate and faults, for M≥7 earthquakes in the regions of
  this release.
- Multi-resolution grids (Khawaja et al. 2023), which raise test power with few earthquakes.
- A learned residual model on large catalogues (California or Japan scale only, against R); weak evidence,
  last in line.

**Final stage: the 2021+ vault.** The final test of the frozen model. Only the maintainer opens the seal.

**What is published.** The method, the test rules, the seal and blind-window design, the comparison tables with
their evidence levels, the negative results, the roadmap and the code in this repository. Fingerprints of frozen
forecasts are published before a window is scored and the forecast files after. Not published: results inside
the blind window or the seal before they are opened, and copies of purchased papers.
