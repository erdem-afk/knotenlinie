"""Bilinen cevaplı skor, sızıntı ve kaynak birimi testleri (unittest)."""
import math
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd
from scipy import stats

from knotenlinie.karsilastir import (
    Model, kos, karsilastir, PuanHatasi, log_olabilirlik, eslestirilmis,
    tutarlilik, holm, gectik, csep_xml,
)
from knotenlinie.karsilastir.kosucu import IZGARA, SUTUNLAR, olay_kutulari, geometri
from knotenlinie.karsilastir.puan import n_testi, kosullu_test
from knotenlinie.karsilastir.komut import sentetik, json_temiz


def izgara():
    return pd.DataFrame([[10, 11, 40, 41], [11, 12, 40, 41]], columns=IZGARA, dtype=float)


def katalog(rows=()):
    k = pd.DataFrame(rows, columns=SUTUNLAR)
    k['zaman'] = pd.to_datetime(k.zaman, utc=True)
    return k


def statik(ad, daily):
    return Model(ad, lambda a, b, past, g, m: np.asarray(daily, float) * ((b - a) / pd.Timedelta(days=1)))


class PuanTest(unittest.TestCase):
    def test_poisson_known(self):
        lam = [2, 0, 3]
        n = [3, 0, 1]
        expected = 3 * math.log(2) - 2 - math.lgamma(4) + math.log(3) - 3
        self.assertAlmostEqual(log_olabilirlik(lam, n), expected)
        self.assertEqual(log_olabilirlik([0], [1]), -np.inf)
        self.assertEqual(log_olabilirlik([0], [0]), 0)

    def test_bad_inputs(self):
        for lam, n in [([-1], [0]), ([np.nan], [0]), ([np.inf], [0]), ([1], [.5]), ([1], [-1]), ([1], [np.nan]), ([1, 2], [1])]:
            with self.assertRaises(PuanHatasi):
                log_olabilirlik(lam, n)

    def test_compensator_and_t(self):
        a, b = np.array([2., 3., 4.]), np.ones(3)
        s = eslestirilmis(a, b, 10, 6)
        y = np.log(a) - 4 / 3
        self.assertAlmostEqual(s['IG'], y.mean())
        self.assertAlmostEqual(s['T'], stats.ttest_1samp(y, 0).statistic)
        self.assertAlmostEqual(s['p_T'], stats.ttest_1samp(y, 0).pvalue)
        self.assertAlmostEqual(s['GA'][0], y.mean() - stats.t.ppf(.975, 2)*y.std(ddof=1)/np.sqrt(3))
        w = stats.wilcoxon(y, method='approx')
        self.assertAlmostEqual(s['p_W'], w.pvalue)

    def test_equal_models(self):
        s = eslestirilmis([1, 2, 4], [1, 2, 4], 9, 9)
        self.assertEqual((s['IG'], s['p_T'], s['p_W'], s['GA']), (0, 1, 1, [0, 0]))

    def test_empty_singleton_zero(self):
        self.assertIsNone(eslestirilmis([], [], 1, 1)['IG'])
        self.assertIsNone(eslestirilmis([1], [2], 1, 2)['p_T'])
        with self.assertRaises(PuanHatasi):
            eslestirilmis([0, 1], [1, 1], 1, 2)
        s = eslestirilmis([1, 1], [1, 1], 10, 2)
        self.assertEqual(s['IG'], -4)
        self.assertEqual(s['p_T'], 0)
        self.assertLess(s['T'], 0)

    def test_synthetic_better_wins(self):
        s = sentetik()
        self.assertGreater(s['daha_iyi']['IG'], .2)
        self.assertLess(s['daha_iyi']['p_T'], .001)
        self.assertLess(s['daha_iyi']['p_W'], .001)
        self.assertTrue(s['tutarlilik']['gecti'])
        self.assertAlmostEqual((s['dogru_logL'] - s['taban_logL']) / s['daha_iyi']['N'], s['daha_iyi']['IG'])

    def test_n_analytic(self):
        s = n_testi(3, 2)
        self.assertAlmostEqual(s['ust_kuyruk'], 1 - 4 * math.exp(-3))
        self.assertAlmostEqual(s['alt_kuyruk'], 8.5 * math.exp(-3))
        self.assertTrue(n_testi(0, 0)['gecti'])
        self.assertFalse(n_testi(0, 1)['gecti'])
        self.assertFalse(n_testi(100, 1)['gecti'])

    def test_s_m_wrong_shape(self):
        n = np.array([[500, 0], [0, 0]])
        wrong = np.array([[.1, .9], [.9, 8.1]])
        s = tutarlilik(wrong, n, tekrar=999)
        self.assertFalse(s['S']['gecti'])
        self.assertFalse(s['M']['gecti'])
        self.assertFalse(s['N']['gecti'])

    def test_conditional_fixed_count_and_scale(self):
        a = kosullu_test([1, 1], [5, 5], tekrar=50, tohum=4)
        b = kosullu_test([10, 10], [5, 5], tekrar=50, tohum=4)
        self.assertEqual(a, b)
        self.assertEqual(a['p'], 1)
        self.assertFalse(kosullu_test([0, 1], [1, 0])['gecti'])
        self.assertFalse(kosullu_test([1, 1], [0, 0])['gecti'])
        # Tek hücre: bütün simülasyonlar gözlemle eşit, p=1.
        self.assertEqual(kosullu_test([3], [8], tekrar=10)['p'], 1)

    def test_holm_family(self):
        np.testing.assert_allclose(holm([.02, .001, .04]), [.04, .003, .04])
        self.assertEqual(holm([None, .1]), [1., .2])
        with self.assertRaises(PuanHatasi):
            holm([np.nan])

    def test_full_verdict(self):
        c = {k: {'IG': .2, 'p_T': .001} for k in ['italya_hazfx', 'italya_triples', 'italya_etas']}
        t = {'italya': {'gecti': True}}
        self.assertTrue(gectik(c, t)['gectik'])
        c['italya_triples']['IG'] = -.1
        self.assertFalse(gectik(c, t)['gectik'])
        with self.assertRaises(PuanHatasi):
            gectik({}, t)

    def test_json(self):
        self.assertEqual(json_temiz(dict(x=np.inf, a=np.int64(2))), dict(x=None, a=2))


class KosucuTest(unittest.TestCase):
    def setUp(self):
        self.g = izgara(); self.m = [4.95, 5.05, np.inf]
        self.k = katalog([
            ['2010-12-31T23:59:59Z', 40.5, 10.5, 10, 4],
            ['2011-01-01T12:00:00Z', 40.5, 10.5, 10, 5],
            ['2011-01-01T13:00:00Z', 40.5, 10.5, 10, 5],
            ['2011-01-02T00:00:00Z', 40.5, 11.5, 10, 5.1],
            ['2011-01-03T00:00:00Z', 40.5, 11.5, 10, 5],
        ])

    def run_models(self, models, k=None):
        return kos(models, '2011-01-01T00:00:00Z', '2011-01-03T00:00:00Z',
                   self.k if k is None else k, self.g, self.m)

    def test_static_calls_once_and_factorial(self):
        calls = []
        def expected(a, b, past, g, m):
            calls.append(len(past)); return np.ones((2, 2)) * 2
        s = self.run_models([Model('m', expected)])['m']
        self.assertEqual(calls, [1])
        self.assertEqual(s.gozlem.sum(), 3)
        self.assertAlmostEqual(s.logL, -8 - math.log(2))
        np.testing.assert_equal(s.olay_oranlari, [1, 1, 1])

    def test_dynamic_history_and_static_same_bins(self):
        calls = []
        def expected(a, b, past, g, m):
            self.assertTrue((past.zaman < a).all())
            calls.append((a, len(past)))
            return np.ones((2, 2))
        s = self.run_models([Model('dyn', expected, True, gecmis_ayarlari={'sinir': (10,12,40,41), 'baslangic_yil': 2010, 'derinlik_max': 70}), statik('ti', np.ones((2, 2)))])
        self.assertEqual([n for _, n in calls], [1, 3])
        self.assertEqual(s['dyn'].logL, s['ti'].logL)
        self.assertEqual(karsilastir(s['dyn'], s['ti'])['IG'], 0)

    def test_ig_logl_identity(self):
        s = self.run_models([statik('a', [[2, 1], [1, 1]]), statik('b', [[1, 1], [1, 1]])])
        r = karsilastir(s['a'], s['b'])
        self.assertAlmostEqual(r['IG'], (2 * math.log(2) - 2)/3)

    def test_not_day_future_information(self):
        seen = []
        def expected(a, b, past, g, m):
            seen.append(past.mw.tolist()); return np.ones((2, 2)) * (1 + len(past))
        model = Model('a', expected, True, gecmis_ayarlari={
            'sinir': (10,12,40,41), 'baslangic_yil': 2010, 'derinlik_max': 70})
        a = self.run_models([model])['a']
        changed = self.k.copy(); changed.loc[4, 'mw'] = 9
        b = self.run_models([model], changed)['a']
        np.testing.assert_equal(a.beklenen, b.beklenen)
        self.assertEqual(a.logL, b.logL)
        self.assertEqual(seen[0], [4])

    def test_mutating_model_cannot_mutate_other_models(self):
        def mutate(a, b, past, g, m):
            past.loc[:, 'mw'] = 100; g.loc[:, 'boylam_min'] = 0; m[:] = 0
            return np.ones((2, 2)) * ((b - a) / pd.Timedelta(days=1))
        s = self.run_models([Model('a', mutate), statik('b', np.ones((2, 2)))])
        self.assertEqual(karsilastir(s['a'], s['b'])['IG'], 0)
        self.assertEqual(self.k.mw.iloc[0], 4)
        self.assertEqual(self.g.boylam_min.iloc[0], 10)

    def test_zero_rate_is_not_floored(self):
        s = self.run_models([statik('a', np.zeros((2, 2))), statik('b', np.ones((2, 2)))])
        self.assertEqual(s['a'].logL, -np.inf)
        r = karsilastir(s['a'], s['b'])
        self.assertEqual(r['durum'], 'tanımsız')
        self.assertIsNone(r['IG'])
        self.assertFalse(s['a'].tutarlilik(tekrar=10)['gecti'])

    def test_temporal_gates(self):
        for a, b in [('2016-01-01T00:00:00Z', '2017-01-01T00:00:00Z'),
                     ('2011-01-01', '2011-01-03'), ('2011-01-01T01:00:00Z', '2011-01-03T00:00:00Z')]:
            with self.assertRaises(PuanHatasi):
                kos([statik('x', np.ones((2, 2)))], a, b, self.k, self.g, self.m)
        k = self.k.copy(); k.loc[4, 'zaman'] = pd.Timestamp('2016-01-01', tz='UTC')
        with self.assertRaises(PuanHatasi):
            self.run_models([statik('x', np.ones((2, 2)))], k)

    def test_shape_and_negative_models(self):
        for daily in [np.ones((2, 1)), -np.ones((2, 2)), np.full((2, 2), np.nan)]:
            with self.assertRaises(PuanHatasi):
                self.run_models([statik('x', daily)])

    def test_edges_exclusive(self):
        k = katalog([
            ['2011-01-01T00:00:00Z', 40, 11, 0, 5.05],
            ['2011-01-01T00:00:00Z', 41, 11, 0, 5.05],
            ['2011-01-01T00:00:00Z', 40, 12, 0, 5.05],
            ['2011-01-01T00:00:00Z', 40, 10, 30, 5],
            ['2011-01-01T00:00:00Z', 40, 10, 29, 4.949],
        ])
        k, c, m = olay_kutulari(k, self.g, self.m)
        self.assertEqual(len(k), 1); self.assertEqual(c.tolist(), [1]); self.assertEqual(m.tolist(), [1])

    def test_bad_grid(self):
        bad = pd.concat([self.g, self.g.iloc[:1]], ignore_index=True)
        with self.assertRaises(PuanHatasi):
            geometri(bad, self.m)
        for edges in [[4.95, 4.9], [np.nan, 5], [4.9, np.inf, np.inf]]:
            with self.assertRaises(PuanHatasi):
                geometri(self.g, edges)

    def test_different_domain_cannot_be_compared(self):
        a = self.run_models([statik('a', np.ones((2, 2)))])['a']
        # Aynı olaylar ve aynı hücre sayımı, ama boş alanın integrali farklı.
        grid = self.g.copy(); grid.loc[1, 'boylam_max'] = 13
        b = kos([statik('b', np.ones((2, 2)))], '2011-01-01T00:00:00Z',
                '2011-01-03T00:00:00Z', self.k, grid, self.m)['b']
        self.assertTrue(a.olaylar.equals(b.olaylar))
        with self.assertRaises(PuanHatasi):
            karsilastir(a, b)

    def test_different_window_cannot_be_compared(self):
        a = self.run_models([statik('a', np.ones((2, 2)))], katalog())['a']
        b = kos([statik('b', np.ones((2, 2)))], '2011-01-01T00:00:00Z',
                '2011-01-04T00:00:00Z', katalog(), self.g, self.m)['b']
        with self.assertRaises(PuanHatasi):
            karsilastir(a, b)

    def test_no_events_not_a_victory(self):
        s = self.run_models([statik('a', np.ones((2, 2))), statik('b', np.ones((2, 2)))], katalog())
        self.assertIsNone(karsilastir(s['a'], s['b'])['p_T'])
        self.assertFalse(s['a'].tutarlilik(tekrar=10)['gecti'])


XML = '''<CSEPForecast xmlns="http://www.scec.org/xml-ns/csep/forecast/0.1"><forecastData>
<modelName>test</modelName><issueDate>2009-01-01T00:00:00Z</issueDate>
<forecastStartDate>2008-01-01T00:00:00Z</forecastStartDate><forecastEndDate>2013-01-01T00:00:00Z</forecastEndDate>
<defaultMagBinDimension>0.1</defaultMagBinDimension><lastMagBinOpen>1</lastMagBinOpen>
<defaultCellDimension latRange="1" lonRange="1"/><depthLayer min="0" max="30">
<cell lat="40.5" lon="10.5"><bin m="5.0">10</bin><bin m="5.1">20</bin></cell>
<cell lat="40.5" lon="11.5"><bin m="5.0">30</bin><bin m="5.1">40</bin></cell>
</depthLayer></forecastData></CSEPForecast>'''


class KaynakTest(unittest.TestCase):
    def xml_model(self, text=XML):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'forecast.xml'; p.write_text(text)
            return csep_xml(p, sure_yil=10)

    def test_xml_explicit_units_and_open_tail(self):
        m = self.xml_model()
        np.testing.assert_equal(m.yillik, [[1, 2], [3, 4]])
        self.assertEqual(m.m_kenarlar.tolist(), [4.95, 5.05, np.inf])
        k = m.beklenen(pd.Timestamp('2011-01-01', tz='UTC'), pd.Timestamp('2012-01-01', tz='UTC'), None, izgara(), [4.95, np.inf])
        np.testing.assert_allclose(k, np.array([[3], [7]]) * 365 / 365.25)
        self.assertEqual(m.metadata['forecast_unit_yil'], 10)

    def test_reordered_subset(self):
        m = self.xml_model()
        g = izgara().iloc[[1, 0]]
        s = m.beklenen(pd.Timestamp('2011-01-01', tz='UTC'), pd.Timestamp('2011-01-02', tz='UTC'), None, g, [5.05, np.inf])
        np.testing.assert_allclose(s[:, 0], np.array([4, 2])/365.25)

    def test_no_silent_interpolation(self):
        m = self.xml_model()
        with self.assertRaises(PuanHatasi):
            m.beklenen(pd.Timestamp('2011-01-01', tz='UTC'), pd.Timestamp('2011-01-02', tz='UTC'), None, izgara(), [4.9, np.inf])
        g = izgara().copy(); g.loc[0, 'boylam_min'] = 9.9
        with self.assertRaises(PuanHatasi):
            m.beklenen(pd.Timestamp('2011-01-01', tz='UTC'), pd.Timestamp('2011-01-02', tz='UTC'), None, g, [4.95, np.inf])

    def test_magnitude_rebin_conserves_mass_and_names_assumptions(self):
        from knotenlinie.karsilastir import IzgaraTabani
        src = IzgaraTabani('test', izgara(), np.array([4.9, 5.0, 5.1, 5.2]),
                           np.array([[2., 4., 6.], [1., 2., 3.]]), {})
        with self.assertRaises(PuanHatasi):
            src.buyukluk_kutula([4.95, 5.05, np.inf])
        with self.assertRaises(PuanHatasi):
            src.buyukluk_kutula([4.95, 5.05, np.inf], kutu_ici_duzgun=True)
        dst = src.buyukluk_kutula([4.95, 5.05, np.inf], kutu_ici_duzgun=True, sifir_ust_kuyruk=True)
        np.testing.assert_allclose(dst.yillik, [[3, 8], [1.5, 4]])
        same = src.buyukluk_kutula([4.9, 5.2], kutu_ici_duzgun=True)
        np.testing.assert_allclose(same.yillik[:, 0], src.yillik.sum(axis=1))
        with self.assertRaises(PuanHatasi):
            self.xml_model().buyukluk_kutula([4.95, 5.05, np.inf], kutu_ici_duzgun=True)

    def test_late_publication_rejected(self):
        with self.assertRaises(PuanHatasi):
            self.xml_model(XML.replace('2009-01-01T00:00:00Z', '2016-01-01T00:00:00Z'))



if __name__ == '__main__':
    unittest.main()
