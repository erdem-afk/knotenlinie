"""Fixtures of the elastic-kernel tests (the heavy-tier marker is registered in pyproject.toml)."""
import numpy as np
import pytest


@pytest.fixture
def rng():
    """The declared sampling seed."""
    return np.random.default_rng(20260929)


@pytest.fixture
def kabul():
    """A passing acceptance record for the ledger round-trip test."""
    return {
        "gecti": True,
        "tur": "bagimsiz_hesap",
        "olcu": "genlik",
        "deger": 1.0,
        "kanit": "sentetik elastik çekirdek testi",
    }
