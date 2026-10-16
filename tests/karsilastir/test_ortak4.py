"""H4 ince komutu: hedef/geçmiş ayrımı, grup ve GR tanısı bilinen cevapları."""
from types import SimpleNamespace
import unittest

import numpy as np
import pandas as pd

from knotenlinie.karsilastir import Model, kos, karsilastir, PuanHatasi
from knotenlinie.karsilastir.ortak4 import (AyriGecmis, gecmis_ayari, gecmis_filtrele,
                                     kumelenme, uzaklik_km, ayristir, olcekle)


def catalog(rows):
    return pd.DataFrame(rows, columns=['zaman', 'enlem', 'boylam', 'derinlik', 'mw'])


class Ortak4Test(unittest.TestCase):
    def setUp(self):
        self.grid = pd.DataFrame([[10, 11, 40, 41]],
                                 columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])
        self.ayar = dict(sinir=(10, 11, 40, 41), baslangic_yil=1985, derinlik_max=70)

    def test_own_box_year_and_depth(self):
        model = SimpleNamespace(kutu=(40, 41, 10, 11), p={'baslangic_yili': 1985})
        self.assertEqual(gecmis_ayari(model, 'italya'), self.ayar)
        with self.assertRaises(PuanHatasi):
            gecmis_ayari(model, 'baska')
        rows = [['1985-01-01T00:00:00Z', 40.5, 10.5, 70, 3.1],
                ['1984-12-31T23:59:59Z', 40.5, 10.5, 10, 4],
                ['2010-01-01T00:00:00Z', 40.5, 11, 10, 4],
                ['2010-01-01T00:00:00Z', 41, 10.5, 10, 4],
                ['2010-01-01T00:00:00Z', 40.5, 10.5, 70.01, 4],
                ['2010-01-01T00:00:00Z', 40.5, 10.5, -0.01, 4]]
        self.assertEqual(len(gecmis_filtrele(catalog(rows), self.ayar)), 1)

    def test_full_catalog_gate_before_filters(self):
        bad = catalog([['2016-01-01T00:00:00Z', 0, 0, 100, 1]])
        with self.assertRaisesRegex(PuanHatasi, '2016'):
            gecmis_filtrele(bad, self.ayar)

    def test_independent_history_strict_day_cut_and_mc(self):
        seen = []
        def expected(a, b, h, g, m):
            seen.append(h.copy())
            return np.full((1, 1), len(h) + 1.)
        model = SimpleNamespace(mc=3.1, beklenen=expected)
        history = catalog([
            ['2010-12-31T23:59:59Z', 40.5, 10.5, 70, 3.1],
            ['2010-12-31T23:59:59Z', 40.5, 10.5, 10, 3.0],
            ['2011-01-01T00:00:00Z', 40.5, 10.5, 10, 3.2],
            ['2011-01-01T13:00:00Z', 40.5, 10.5, 10, 3.3]])
        targets = catalog([['2011-01-01T12:00:00Z', 40.5, 10.5, 10, 5.]])
        wrapper = AyriGecmis(model, history, self.ayar)
        run = kos([Model('base', wrapper.beklenen, True, self.ayar)],
                  '2011-01-01T00:00:00Z', '2011-01-03T00:00:00Z', targets,
                  self.grid, [4.95, 8.6])['base']
        self.assertEqual([len(x) for x in seen], [1, 3])
        self.assertEqual(run.olay_oranlari.tolist(), [2.])
        self.assertEqual(run.beklenen.sum(), 6.)
        self.assertFalse(any((x.mw == 5).any() for x in seen))
        with self.assertRaisesRegex(PuanHatasi, 'kör'):
            wrapper.beklenen('2016-01-01T00:00:00Z', '2016-01-02T00:00:00Z',
                             targets, self.grid, [4.95, 8.6])

    def test_previous_event_not_any_event_and_no_self_parent(self):
        parents = catalog([
            ['2011-01-01T00:00:00Z', 40, 10, 10, 4.5],
            ['2011-01-02T00:00:00Z', 40, 15, 10, 4.5],
            ['2011-01-03T00:00:00Z', 40, 10, 10, 5.]])
        targets = parents.iloc[[2]]
        flags, any_flags, details = kumelenme(targets, parents)
        self.assertEqual(flags.tolist(), [False])
        self.assertEqual(any_flags.tolist(), [True])
        self.assertEqual(details[0]['onceki_zaman'], '2011-01-02T00:00:00+00:00')

    def test_cluster_time_boundary_and_m_threshold(self):
        parents = catalog([['2011-01-01T00:00:00Z', 40, 10, 10, 4.5],
                           ['2011-01-30T00:00:00Z', 40, 15, 10, 4.49]])
        targets = catalog([['2011-01-31T00:00:00Z', 40, 10, 10, 5],
                           ['2011-01-31T00:00:01Z', 40, 10, 10, 5]])
        self.assertEqual(kumelenme(targets, parents)[0].tolist(), [True, False])
        self.assertAlmostEqual(float(uzaklik_km(0, 0, 0, 1)), 111.1950802335, places=7)

    def runs(self):
        targets = catalog([['2011-01-01T12:00:00Z', 40.5, 10.5, 10, 5],
                           ['2011-01-02T12:00:00Z', 40.5, 10.5, 10, 5]])
        return kos([Model('a', lambda *args: np.array([[8.]])),
                    Model('b', lambda *args: np.array([[4.]]))],
                   '2011-01-01T00:00:00Z', '2011-01-03T00:00:00Z',
                   targets, self.grid, [4.95, 8.6])

    def test_gr_scale_event_and_integral_identity(self):
        r = self.runs()
        scaled = olcekle(r['a'], .5)
        pair = karsilastir(scaled, r['b'])
        self.assertEqual(pair['IG'], 0.)
        self.assertEqual(pair['p_T'], 1.)
        delta = pair['IG'] - karsilastir(r['a'], r['b'])['IG']
        self.assertAlmostEqual(delta, np.log(.5) + (.5 * 8) / 2)
        with self.assertRaises(PuanHatasi):
            olcekle(r['a'], 0)

    def test_event_group_decomposition(self):
        r = self.runs()
        d = ayristir(r['a'], r['b'], r['a'].olaylar)
        self.assertEqual(d['gruplar']['kumelenme']['N'], 1)
        self.assertEqual(d['gruplar']['geri_kalan']['N'], 1)
        weighted = sum(x['log_oran_toplami'] for x in d['gruplar'].values()) / 2
        pair = karsilastir(r['a'], r['b'])
        self.assertAlmostEqual(weighted + pair['integral_terimi'], pair['IG'])
        self.assertEqual(len(d['olaylar']), 2)

    def test_empty_cluster_group_not_zero_mean(self):
        r = self.runs()
        empty = catalog([])
        d = ayristir(r['a'], r['b'], empty)
        self.assertEqual(d['gruplar']['kumelenme']['N'], 0)
        self.assertIsNone(d['gruplar']['kumelenme']['ortalama_log_oran'])


if __name__ == '__main__':
    unittest.main()
