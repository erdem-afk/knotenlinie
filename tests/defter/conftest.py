"""Fixtures of the ledger tests."""
import pytest


@pytest.fixture
def kabul():
    """A passing acceptance record (published number)."""
    return {
        "gecti": True,
        "tur": "yayimlanmis",
        "olcu": "genlik",
        "deger": 1.0,
        "kaynak": "test",
        "kanit": "sentetik test kaydı",
    }
