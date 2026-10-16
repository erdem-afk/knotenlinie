"""Test setup: a global seed and the heavy-tier marker.

Tests are deterministic: the session fixture seeds numpy once and every statistical test
either uses that seed or sets a declared literal one.
"""
from __future__ import annotations

import numpy as np
import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "agir: heavy statistical test; run with -m agir on cloud compute")


def pytest_collection_modifyitems(config, items):
    if "agir" in (config.getoption("-m") or ""):
        return
    atla = pytest.mark.skip(reason="heavy statistical test: run with -m agir on cloud compute")
    for it in items:
        if "agir" in it.keywords:
            it.add_marker(atla)


@pytest.fixture(autouse=True, scope="session")
def _kuresel_tohum():
    """One declared seed for everything that samples."""
    np.random.seed(20260929)
    yield
