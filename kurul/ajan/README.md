# kurul/ajan: Knotenlinie Board agent worker

The AI participant of the Knotenlinie Board chat. It long-polls the site's agent API
(`../SPEC.md`, section 5), decides per event what to do (section 7), answers from the ledger in a
checkout of this repository, and posts cards (section 6). Outbound HTTPS only; Python 3.12+
standard library only. Model calls go through the Claude Code CLI in headless mode.

## Run

```sh
cd kurul
export KURUL_BASE_URL=https://board.example.org KURUL_AGENT_TOKEN=... KURUL_REPO=/path/to/checkout
python3 -m ajan check   # validates config, prints the CLI command it will use
python3 -m ajan         # the loop; JSON log lines on stderr
```

Production: `deploy/kurul-ajan.service` (unprivileged user, `EnvironmentFile=/etc/kurul-ajan.env`,
`Restart=always`) and `deploy/kurul-ajan.env.example`. Log in to the Claude Code CLI once as the
service user.

## Environment

| Variable | Default | Meaning |
|---|---|---|
| `KURUL_BASE_URL`, `KURUL_AGENT_TOKEN` | required | site and bearer token |
| `KURUL_REPO` | `.` | checkout holding `kayit/adaylar.jsonl`; any branch, never checked out or pulled by the worker |
| `KURUL_REPO_URL`, `KURUL_REPO_REF` | empty, `main` | public GitHub base and branch for links in cards; without a base, refs carry no `url` |
| `KURUL_LLM` | `claude` | `fake` = deterministic stand-in (tests) |
| `KURUL_MODEL_FAST`, `KURUL_MODEL_MAIN` | `haiku`, `opus` | classify/restate use fast; the rest use main |
| `KURUL_AUTORUN` | `0` | `1` = review, freeze, run, ledger line by the agent (see below) |
| `KURUL_SUGGEST_THRESHOLD` | `0.85` | minimum classifier confidence for a suggestion card |
| `KURUL_MENTION_THRESHOLD` | `0.6` | same, for `@knotenlinie` messages (an explicit request) |
| `KURUL_BLOCKED_NAMES`, `KURUL_BLOCKED_TERMS` | empty | comma lists never allowed in posts (e.g. the coordinator's personal name) |
| `KURUL_STATE_DIR` | `~/.local/state/kurul-ajan` | SQLite state, `kuyruk/`, `coordinator.jsonl`, worktrees |
| `KURUL_LLM_TIMEOUT`, `KURUL_RUN_TIMEOUT` | `900`, `21600` | seconds per model call / per run |
| `KURUL_CLAUDE_BIN`, `KURUL_POLL_WAIT`, `KURUL_LEDGER_PATH` | `claude`, `25`, `kayit/adaylar.jsonl` | |

## Tests

```sh
cd kurul && python3 -m unittest discover -s ajan/tests -t .
# or, with pytest in a venv:  ajan/.venv/bin/pytest ajan/tests
```

Tests use an in-process fake site (`tests/fakesite.py`) and `KURUL_LLM=fake`; they make no model
calls and run no git commands. `AJAN_TEST_LOG=1` prints log lines during tests.

## What it does

- Suggests a question (card visible only to the author) when the classifier is at or above the
  threshold; at most one offer per message, ever. Opinions, greetings, logistics: silent.
- `@knotenlinie` question: registers it directly; otherwise a brief reply.
- Forward: restates (note first) and posts a confirm card to the forwarder, or one line saying
  nothing testable was found.
- Confirmed question: acknowledgement, then a read-only ledger search (Read, Grep, Glob; no shell,
  network or edits). Either an `answer_record` card whose every point cites closed ledger entries
  (checked in code; links built by code from the entry's files), or a `plan` card plus a
  feasibility report (cost and detail only in the private part). Out-of-domain: asks the member.
- Plan changes (card button or a message in the thread): next draft.
- Approved plan with `KURUL_AUTORUN=0`: status `frozen`, a notice that the run is queued, and a
  request file `KURUL_STATE_DIR/kuyruk/Q-nnn.json` (plan + sha256) for the team.
- `KURUL_AUTORUN=1` (`run_job.py`): independent review, freeze (plan + sha256 in
  `kayit/kurul/Q-nnn/` of a git worktree on branch `kurul/q-nnn`, committed, not pushed), one run in
  that worktree, `answer_test` card, ledger line, statuses through `in_ledger`. A run is never
  started twice, even after a crash.

## What it will not do

- Post anything that fails the code post-checks: absolute probabilities for Istanbul, Marmara or a
  segment; the word "prediction"; money; infrastructure names or server paths; blocked names. The
  model gets one retry with the rule named; then nothing (or a neutral notice) is posted and the
  violation is logged.
- Treat member text as instructions. Member text is always inside a marked data block. Text that
  tries to instruct the agent gets no post; it is logged and appended to
  `KURUL_STATE_DIR/coordinator.jsonl`.
- Read hidden messages (the site does not serve them), open blind data, rent machines, push to git,
  or start a run without an approved plan.
