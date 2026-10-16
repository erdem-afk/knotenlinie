"""Roots of the data, record and run trees (the only package module that reads the root variables).

``KNOTENLINIE_DATA``     data root (catalogues, fault sources, base models); default ``<repo>/data``, git-ignored.
``KNOTENLINIE_RECORDS``  frozen rule and selection records; default ``<repo>/records``, tracked.
``KNOTENLINIE_RUNS``     new outputs and score ledgers; default ``<repo>/runs``, git-ignored.

Frozen records are never overwritten in place: a driver copies ``KAYIT/<ID>/*`` into ``KOSU/<ID>/``
before its first stage and writes only there.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]                                   # repo root
VERI = Path(os.environ.get('KNOTENLINIE_DATA', KOK / 'data'))              # data root, git-ignored
KAYIT = Path(os.environ.get('KNOTENLINIE_RECORDS', KOK / 'records'))       # frozen records, tracked
KOSU = Path(os.environ.get('KNOTENLINIE_RUNS', KOK / 'runs'))              # outputs and ledgers, git-ignored


def kayit_hazirla(kimlik: str) -> Path:
    """Return ``KOSU/<kimlik>``, seeding it once with the frozen files of ``KAYIT/<kimlik>``.

    Files already present in the run folder are kept (a stage's own outputs are never replaced by the
    frozen copy); the frozen record itself is only read.
    """
    hedef = KOSU / kimlik
    hedef.mkdir(parents=True, exist_ok=True)
    kaynak = KAYIT / kimlik
    if kaynak.is_dir():
        for p in sorted(kaynak.iterdir()):
            if p.is_file() and not (hedef / p.name).exists():
                shutil.copyfile(p, hedef / p.name)
    return hedef


def veri_var(*parcalar: str) -> bool:
    """True when ``VERI/<parcalar...>`` exists (used by data-dependent tests to skip)."""
    return VERI.joinpath(*parcalar).exists()


def kod_ozeti(yollar) -> dict:
    """``{repo-relative path: sha256}`` for code files named relative to the repo root (provenance)."""
    import hashlib
    out = {}
    for rel in yollar:
        rel = str(rel)
        h = hashlib.sha256()
        with open(KOK / rel, 'rb') as f:
            for blok in iter(lambda: f.read(1 << 20), b''):
                h.update(blok)
        out[rel] = h.hexdigest()
    return out
