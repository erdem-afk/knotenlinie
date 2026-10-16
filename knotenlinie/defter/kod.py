"""Code-version block and hashing: prove which code wrote a ledger file.

The provenance record's ``kod`` block carries the git commit, a dirty flag taken from
``git status --porcelain`` and a streamed sha256 per package module, so a reviewer can
tie a ledger file back to the exact code.  ``girdi_ozeti`` is the single sha256 helper
used both here and for the provenance record's input references.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import os
import subprocess
from typing import Dict

KOD_DIZINI = os.path.dirname(os.path.abspath(__file__))
REPO_KOKU = os.path.dirname(os.path.dirname(KOD_DIZINI))


def girdi_ozeti(yol) -> str:
    """Streamed sha256 of one input file; never loads the file into memory."""
    h = hashlib.sha256()
    with open(yol, "rb") as akis:
        for parca in iter(lambda: akis.read(1024 * 1024), b""):
            h.update(parca)
    return h.hexdigest()


def simdi_utc() -> str:
    """Current instant as an ISO-8601 Z string."""
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _git(*argumanlar: str) -> str:
    try:
        sonuc = subprocess.run(
            ["git", "-C", REPO_KOKU, *argumanlar],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return sonuc.stdout.strip() if sonuc.returncode == 0 else ""


def kod_bloku() -> Dict[str, object]:
    """Code version: git commit, dirty flag, and a sha256 per package module."""
    paket = {
        ad: girdi_ozeti(os.path.join(KOD_DIZINI, ad))
        for ad in sorted(os.listdir(KOD_DIZINI))
        if ad.endswith(".py")
    }
    return {
        "git_commit": _git("rev-parse", "HEAD"),
        "git_kirli": bool(_git("status", "--porcelain")),
        "paket_sha256": paket,
    }
