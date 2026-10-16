"""Yüzey izdüşümü: kütle korunumu ve bilinen paylar."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from shapely.geometry import box

from knotenlinie.fay_zaman.izdusum import Izgara


def _izgara(n=4):
    r = []
    for i in range(n):
        for j in range(n):
            r.append((10 + 0.1 * i, 10.1 + 0.1 * i, 40 + 0.1 * j, 40.1 + 0.1 * j))
    return pd.DataFrame(r, columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])


def test_icerde_toplam_bir():
    g = Izgara(_izgara())
    idx, pay, disari = g.paylar(box(10.12, 40.12, 10.27, 40.18))
    assert pay.sum() == pytest.approx(1.0, rel=1e-12) and disari == pytest.approx(0.0, abs=1e-12)


def test_iki_hucre_yari_yariya():
    g = Izgara(_izgara())
    idx, pay, disari = g.paylar(box(10.05, 40.02, 10.15, 40.08))
    assert sorted(np.round(pay, 9)) == [0.5, 0.5]


def test_izgara_disina_tasan():
    g = Izgara(_izgara())
    idx, pay, disari = g.paylar(box(10.3, 40.1, 10.5, 40.2))  # yarısı (x>10.4) dışarıda
    assert pay.sum() == pytest.approx(0.5, rel=1e-9)
    assert disari == pytest.approx(0.5, rel=1e-9)
    assert pay.sum() + disari == pytest.approx(1.0, rel=1e-12)


def test_tamamen_disarida():
    g = Izgara(_izgara())
    idx, pay, disari = g.paylar(box(20, 20, 20.1, 20.1))
    assert len(idx) == 0 and disari == 1.0


def test_bos_poligon_hata():
    g = Izgara(_izgara())
    with pytest.raises(ValueError):
        g.paylar(box(10, 40, 10, 40))
