"""Skip guards for tests that need private or downloaded data (KNOTENLINIE_DATA, KNOTENLINIE_RUNS).

Without the data root (or with the named file missing) such a test is skipped, so the plain
``python -m pytest`` gives 0 failures on a machine without data.
"""
import pytest

from knotenlinie.yollar import KOSU, VERI


def _eksik(kok, yollar):
    return [str(y) for y in yollar if not (kok / y).exists()]


def veri_gerek(*yollar):
    """Skip unless every path exists under the data root ``KNOTENLINIE_DATA``."""
    eksik = _eksik(VERI, yollar)
    return pytest.mark.skipif(bool(eksik), reason=(
        f"needs data: $KNOTENLINIE_DATA/{eksik[0]}" if eksik else ""))


def kosu_gerek(*yollar):
    """Skip unless every path exists under the runs root ``KNOTENLINIE_RUNS`` (pipeline outputs)."""
    eksik = _eksik(KOSU, yollar)
    return pytest.mark.skipif(bool(eksik), reason=(
        f"needs pipeline output: $KNOTENLINIE_RUNS/{eksik[0]}" if eksik else ""))
