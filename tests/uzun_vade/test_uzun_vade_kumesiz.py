"""Kümesizleştirme bilinen girdide: pencere değerleri ve arka plan maskesi."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.uzun_vade.kumesiz import (KumesizHatasi, arka_plan_maskesi, pencere,
                                     reasenberg)


def katalog(zamanlar, enlemler, boylamlar, mw, derinlik=5.0):
    return pd.DataFrame(dict(zaman=zamanlar, enlem=enlemler, boylam=boylamlar,
                             derinlik=derinlik, mw=mw))


class PencereTesti(unittest.TestCase):
    def test_gk_bilinen_deger(self):
        dt, dr = pencere('gk74', np.array([5.0, 6.5]))
        self.assertAlmostEqual(float(dr[0]), 10 ** (0.1238 * 5 + 0.983), places=10)
        self.assertAlmostEqual(float(dt[0]), 10 ** (0.5409 * 5 - 0.547), places=10)
        self.assertAlmostEqual(float(dt[1]), 10 ** (0.032 * 6.5 + 2.7389), places=10)

    def test_uhrhammer_bilinen_deger(self):
        dt, dr = pencere('uhrhammer', np.array([5.0, 7.0]))
        self.assertAlmostEqual(float(dr[0]), np.exp(-1.024 + 0.804 * 5), places=10)
        self.assertAlmostEqual(float(dt[1]), np.exp(-2.87 + 1.235 * 7), places=10)

    def test_bilinmeyen(self):
        with self.assertRaises(KumesizHatasi):
            pencere('yok', np.array([5.0]))


class MainshockTesti(unittest.TestCase):
    def setUp(self):
        self.t0 = pd.Timestamp('2000-01-01', tz='UTC')

    def test_artci_ve_oncu_silinir(self):
        # M6 ana şok iki küçük olayı (öncü + artçı) siler; uzaktaki bağımsız kalır.
        k = katalog(
            [self.t0 + pd.Timedelta(days=1), self.t0, self.t0 + pd.Timedelta(days=3),
             self.t0 + pd.Timedelta(days=1)],
            [38.05, 38.0, 38.0, 41.0], [22.05, 22.0, 22.0, 26.0], [4.5, 6.0, 4.0, 4.5])
        _, maske = arka_plan_maskesi(k, 'gk74')
        self.assertEqual(maske.tolist(), [True, False, True, False])

    def test_es_buyukluk_silmez(self):
        k = katalog([self.t0, self.t0 + pd.Timedelta(days=2)], [38.0, 38.0],
                    [22.0, 22.0], [5.0, 5.0])
        _, maske = arka_plan_maskesi(k, 'gk74')
        self.assertEqual(maske.tolist(), [True, True])

    def test_pencere_disinda_artci_kalir(self):
        # M5 pencere süresi ~144 gün; 400 gün sonraki olay bağımsız kalır.
        k = katalog([self.t0, self.t0 + pd.Timedelta(days=400)], [38.0, 38.0],
                    [22.0, 22.0], [5.0, 3.0])
        _, maske = arka_plan_maskesi(k, 'gk74')
        self.assertEqual(maske.tolist(), [True, True])


class ReasenbergTesti(unittest.TestCase):
    def test_kume_ana_sok_tek_arka_plan(self):
        t0 = pd.Timestamp('2000-01-01', tz='UTC')
        k = katalog([t0, t0 + pd.Timedelta(hours=2), t0 + pd.Timedelta(days=1)],
                    [38.0, 38.01, 38.0], [22.0, 22.01, 22.0], [5.0, 4.0, 3.5])
        _, maske = arka_plan_maskesi(k, 'reasenberg')
        self.assertEqual(int(maske.sum()), 1)
        self.assertTrue(maske[0])


if __name__ == '__main__':
    unittest.main()
