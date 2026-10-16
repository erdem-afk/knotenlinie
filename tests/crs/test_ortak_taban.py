"""T protokolü için toplu/ortak-imza eşitliği; sahte veri, ETAS yeniden ayarı yok."""
import numpy as np
import pandas as pd
import pytest

from knotenlinie.crs.arayuz import Model
from knotenlinie.crs.dalga2 import alici_paylari, melez
from knotenlinie.crs.italya import crs_gunluk
from knotenlinie.crs.ortak_taban import TopluOrtak, OrtakCRS
from tests.crs.test_crs import fixture
from knotenlinie.crs.girdi import k9_basamaklari


class SahteT:
    def __init__(self, base, g):
        self.base = base
        self.th = base.parametre
        self.mc, self.b = base.m0, base.b
        self.p = {'ayar_bitis': '2011-01-01T00:00:00Z'}
        self.izgara = g
        self.baslangic = pd.Timestamp('2009-01-01T00:00:00Z')
        self.spatial_calls = 0

    def _arka_plan(self, grid):
        return self.base.uzay(self.izgara, self.base.ayar)[0]

    def _mekan(self, h, grid):
        self.spatial_calls += 1
        return self.base.uzay(self.izgara, h)[2]

    def beklenen(self, *args):
        return self.base.beklenen(*args)


def omori(a, z, c, p):
    return (a+c)**(1-p)*(-np.expm1((1-p)*np.log1p((z-a)/(a+c))))/(p-1)


def test_baglayici_ortak_imza_ve_toplu_ayni():
    f, h, g, p = fixture()
    t = SahteT(Model(p, h, f), g)
    batch = TopluOrtak(t, h, omori)
    days = pd.date_range('2009-01-01T00:00:00Z', periods=5, freq='D')
    e = batch.gunluk(days)
    ts, ds = k9_basamaklari(h, f)
    ratios = crs_gunluk(days, ts, ds, 100000., f.tau_dot_pa_gun.to_numpy())
    mix = melez(e, batch.arka_plan, ratios, alici_paylari(g, f), .25)
    arayuz = OrtakCRS(t, f, asigma_pa=100000., agirlik=.25)
    null = OrtakCRS(t, f, asigma_pa=100000., agirlik=0.)
    for i, a in enumerate(days):
        history = h[h.zaman < a]
        base = t.beklenen(a, a+pd.Timedelta(days=1), history, g, [4., np.inf])
        np.testing.assert_array_equal(null.beklenen(a, a+pd.Timedelta(days=1), history, g, [4., np.inf]), base)
        got = arayuz.beklenen(a, a+pd.Timedelta(days=1), history, g, [4., np.inf])
        np.testing.assert_allclose(got[:, 0], mix[i], rtol=2e-12, atol=1e-15)
    assert t.spatial_calls == 1
    batch.gunluk(days[2:])
    assert t.spatial_calls == 1
    with pytest.raises(ValueError):
        batch.uzay(g.iloc[:1], h)
    with pytest.raises(ValueError):
        batch.uzay(g, h.iloc[:1])
    with pytest.raises(ValueError):
        arayuz.beklenen(days[0], days[1], h, g, [4., np.inf])


def test_csep_bati_kenari_eski_kutuya_kesilmez():
    f, _, _, _ = fixture()
    g = pd.DataFrame({'boylam_min': [5.5], 'boylam_max': [5.6],
                      'enlem_min': [40.], 'enlem_max': [40.1]})
    pay = alici_paylari(g, f)
    assert pay.shape == (1, 2)
    np.testing.assert_allclose(pay.sum(), 1.)


def test_2010_taban_kapisi():
    f, h, g, p = fixture()
    t = SahteT(Model(p, h, f), g)
    t.p['ayar_bitis'] = '2012-01-01T00:00:00Z'
    with pytest.raises(ValueError):
        TopluOrtak(t, h, omori)
    with pytest.raises(ValueError):
        OrtakCRS(t, f, asigma_pa=100000., agirlik=.25)
