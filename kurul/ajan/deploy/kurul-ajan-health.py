#!/usr/bin/env python3
"""kurul-ajan-health: one health line for the agent worker (stdlib only).

Run by kurul-ajan-health.service (as the kurul-ajan user, every 10 minutes). Checks:
  unit       systemctl is-active kurul-ajan
  site       GET <KURUL_BASE_URL>/healthz answers 200 with {"ok": true}
  poll       age of KURUL_STATE_DIR/heartbeat (written by the worker after every successful
             long-poll). While the worker is processing an event (busy.json) no poll happens, so a
             stale heartbeat is fine until the busy marker itself is older than the busy limit.
Writes one journal line, `KURUL-HEALTH OK ...` or `KURUL-HEALTH FAIL <reasons>` (FAIL at syslog
priority err), and KURUL_STATE_DIR/health.json. Exit status 1 on FAIL, so the unit shows as failed.

Tunables (environment): KURUL_HEALTH_MAX_POLL_AGE (seconds, default 300),
KURUL_HEALTH_BUSY_MAX (seconds; default 4 x KURUL_LLM_TIMEOUT, or KURUL_RUN_TIMEOUT + 1800 with
KURUL_AUTORUN=1), KURUL_UNIT (default kurul-ajan).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def num(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name) or default)
    except ValueError:
        return default


def unit_state(unit: str) -> str:
    try:
        p = subprocess.run(["systemctl", "is-active", unit], capture_output=True, text=True, timeout=20)
        return p.stdout.strip() or f"exit {p.returncode}"
    except (OSError, subprocess.TimeoutExpired) as e:
        return f"unknown ({e.__class__.__name__})"


def site_check(base: str) -> tuple[bool, str]:
    if not base:
        return False, "KURUL_BASE_URL not set"
    url = base.rstrip("/") + "/healthz"
    req = urllib.request.Request(url, headers={"User-Agent": "kurul-ajan-health"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read(2000)
            ok = r.status == 200 and json.loads(body or b"{}").get("ok") is True
            return ok, f"http {r.status}" + ("" if ok else " (unexpected body)")
    except urllib.error.HTTPError as e:
        return False, f"http {e.code}"
    except (urllib.error.URLError, OSError, ValueError) as e:
        reason = getattr(e, "reason", e)
        return False, f"unreachable ({str(reason)[:120]})"


def read_busy(state: Path) -> dict | None:
    try:
        b = json.loads((state / "busy.json").read_text())
        return b if isinstance(b, dict) else None
    except (OSError, ValueError):
        return None


def main() -> int:
    now = time.time()
    state = Path(os.environ.get("KURUL_STATE_DIR") or "/var/lib/kurul-ajan")
    unit = os.environ.get("KURUL_UNIT") or "kurul-ajan"
    max_age = num("KURUL_HEALTH_MAX_POLL_AGE", 300)
    autorun = (os.environ.get("KURUL_AUTORUN") or "0").strip().lower() in ("1", "true", "yes", "on")
    busy_max = num("KURUL_HEALTH_BUSY_MAX",
                   num("KURUL_RUN_TIMEOUT", 21600) + 1800 if autorun else 4 * num("KURUL_LLM_TIMEOUT", 900))

    fails: list[str] = []
    info: dict = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))}

    u = unit_state(unit)
    info["unit"] = u
    if u != "active":
        fails.append(f"unit {unit} is {u}")

    ok, detail = site_check(os.environ.get("KURUL_BASE_URL", ""))
    info["site"] = detail
    if not ok:
        fails.append(f"site {detail}")

    try:
        hb = float((state / "heartbeat").read_text().strip())
        age = int(now - hb)
    except (OSError, ValueError):
        age = None
    info["poll_age_s"] = age
    busy = read_busy(state) if u == "active" else None
    if busy:
        info["busy"] = {"event_id": busy.get("event_id"), "type": busy.get("type"),
                        "for_s": int(now - float(busy.get("since") or now))}
    if age is None:
        fails.append("no heartbeat file (worker has not polled successfully yet)")
    elif age > max_age:
        if busy and info["busy"]["for_s"] <= busy_max:
            pass  # processing a long event; polling resumes afterwards
        elif busy:
            fails.append(f"busy on event {busy.get('event_id')} for {info['busy']['for_s']}s (limit {int(busy_max)}s)")
        else:
            fails.append(f"last successful poll {age}s ago (limit {int(max_age)}s)")

    info["ok"] = not fails
    info["reasons"] = fails
    try:
        tmp = state / ".health.json.tmp"
        tmp.write_text(json.dumps(info, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, state / "health.json")
    except OSError as e:
        fails.append(f"cannot write health.json ({e.__class__.__name__})")

    # Syslog priority prefix only when stdout is the journal (systemd sets JOURNAL_STREAM).
    err, inf = ("<3>", "<6>") if os.environ.get("JOURNAL_STREAM") else ("", "")
    if fails:
        print(err + "KURUL-HEALTH FAIL " + "; ".join(fails), flush=True)
        return 1
    extra = f" busy=event {info['busy']['event_id']} {info['busy']['for_s']}s" if busy else ""
    print(f"{inf}KURUL-HEALTH OK unit={u} site={detail} poll_age={age}s{extra}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
