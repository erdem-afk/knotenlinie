"""Structured log lines: one JSON object per line on stderr (journald picks them up)."""

from __future__ import annotations

import json
import os
import sys
import time

_stream = sys.stderr
_records: list[dict] | None = None  # tests can capture


def capture(on: bool = True) -> list[dict]:
    global _records
    _records = [] if on else None
    return _records if _records is not None else []


def log(event: str, level: str = "info", **fields) -> None:
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "level": level, "event": event}
    rec.update(fields)
    if _records is not None:
        _records.append(rec)
        if not os.environ.get("AJAN_TEST_LOG"):
            return
    try:
        _stream.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
        _stream.flush()
    except Exception:
        pass


def excerpt(text: str | None, n: int = 160) -> str:
    t = (text or "").replace("\n", " ")
    return t if len(t) <= n else t[: n - 1] + "…"
