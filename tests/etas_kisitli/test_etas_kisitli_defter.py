"""AJ koşucusu: defter logL ↔ koşucu logL (1e-9), E7 karışımı, Lam495."""
import numpy as np
import pandas as pd
import pytest

from tests.etas_hiyerarsi.test_etas_hiyerarsi_defter import _grid, _katalog, _model
from knotenlinie.karsilastir import gunluk_aj as AJ
from knotenlinie.karsilastir import gunluk_ae as AE
from knotenlinie.karsilastir.kosucu import Model, kos
from knotenlinie.skor_defteri.karisim import log_olabilirlik


def test_defter_kosucu_ve_E7():
    grid, cat, edges = _grid(), _katalog(), AE.kenarlar()
    aj, lm = _model('aj', 0.004, 0.002), _model('lm', 0.003, 0.0005)
    bs = ('2011-01-01T00:00:00Z', '2011-01-04T00:00:00Z')
    d = AE.defter_uret(aj, '2011-2015', cat, grid, bas_son=bs, ilerleme=None)
    dl = AE.defter_uret(lm, '2011-2015', cat, grid, bas_son=bs, ilerleme=None)
    kosu = kos([aj, lm], bs[0], bs[1], cat, grid, edges, derinlik=(0, 30))
    assert d.logL == pytest.approx(kosu['aj'].logL, rel=1e-9, abs=1e-9)
    assert dl.logL == pytest.approx(kosu['lm'].logL, rel=1e-9, abs=1e-9)
    assert log_olabilirlik([d], [1.0], 2.95) == pytest.approx(kosu['aj'].logL, rel=1e-9, abs=1e-9)
    mix = Model('e7', lambda *x: 0.5 * aj.beklenen(*x) + 0.5 * lm.beklenen(*x), True, aj.gecmis_ayarlari)
    k7 = kos([mix], bs[0], bs[1], cat, grid, edges, derinlik=(0, 30))['e7']
    assert log_olabilirlik([d, dl], [0.5, 0.5], 2.95) == pytest.approx(k7.logL, rel=1e-9, abs=1e-9)
    assert 'Lam495' in d.gun.columns and d.gun['Lam495'].le(d.gun['Lam395']).all()


def test_aday_adi_ve_kural_kapisi():
    assert AJ.aday_adi(0.6) == 'AJ-n0.6' and AJ.aday_adi(AJ.K.SERBEST) == 'AJ-nserbest'
    assert AJ.kural_kapisi()
