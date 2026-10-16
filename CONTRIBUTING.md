# Contributing

Issues and pull requests are welcome: bug reports, checks of our numbers, new tests, and models that follow the
rules below.

## Before you open a pull request

- Run the tests: `python -m pip install -e ".[dev]"` and `python -m pytest -q`. Tests that need downloaded data
  must skip cleanly when `KNOTENLINIE_DATA` is unset or a file is missing.
- Score-producing code (log-likelihoods, information gains, rate densities) needs a test in a synthetic world
  with a known answer, and should give the same numbers under Python 3.9 and a current Python 3.
- Keep to the standard library plus numpy, scipy and pandas where you can; a new dependency needs a reason in the
  pull request.
- Module names and identifiers may stay in the existing Turkish style; documentation and pull request text are in
  English.

## Rules that are not negotiable

- **The seal.** Do not add, download, open or print earthquake data dated 2021-01-01 or later, and do not add
  anything derived from it. Downloaders filter on the server or while streaming;
  `python scripts/muhur.py "$KNOTENLINIE_DATA"` must report a clean data root.
- **The blind window.** Do not score or tune anything on Italian earthquakes of 2016–2020. That window is opened
  once, after the preregistration is frozen ([docs/SEAL-AND-BLIND-WINDOW.md](docs/SEAL-AND-BLIND-WINDOW.md)).
- **No third-party data in the repository.** Add a download script and an entry in
  [DATA-SOURCES.md](DATA-SOURCES.md) instead, with the licence and the citation the provider asks for.
- **No copied code** from packages whose licence is not compatible with Apache-2.0.
- **Frozen records stay frozen.** Files under `records/` are not edited after the period they rule has been
  scored. A correction is a dated addendum, and every changed hash is listed in `records/HASHES.md`.

## Proposing a new layer or model

State in one line which score it moves and against which baseline. Write the rule file before the period it
rules is scored. Report the result with its evidence level, whatever it is: a layer that does not clear the bar is
a result too ([docs/HOW-WE-WORK.md](docs/HOW-WE-WORK.md), [docs/TEST-RULES.md](docs/TEST-RULES.md)).

## Licence

By contributing you agree that your contribution is licensed under the Apache License 2.0, the licence of this
repository.
