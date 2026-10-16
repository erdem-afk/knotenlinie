"""KDE hücre entegrasyonu, bükülü GR ve kafes: bilinen cevaplı."""
import unittest

import numpy as np
import pandas as pd
from scipy import integrate, stats

from knotenlinie.kaliforniya.model import (Kafes, ModelHatasi, bant_km, bukulu_gr, kde_sekli,
                                     geysers_mi)


def kafes_kur(nx=40, ny=40, lon0=-120.0, lat0=34.0):
    s = [(lon0 + 0.1 * i, lon0 + 0.1 * (i + 1), lat0 + 0.1 * j, lat0 + 0.1 * (j + 1))
         for i in range(nx) for j in range(ny)]
    return Kafes(pd.DataFrame(s, columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']))


class KdeTesti(unittest.TestCase):
    def test_kutle_bir_ve_hucre_entegrali(self):
        kf = kafes_kur()
        lo, la, sg = -118.0, 36.0, 12.0
        kut = kde_sekli(kf, [lo], [la], [sg])
        self.assertAlmostEqual(kut.sum(), 1.0, places=4)          # tam içeride kütle korunur
        sx = sg / (111.32 * np.cos(np.deg2rad(la)))
        sy = sg / 110.57
        i = int(np.floor((lo - kf.lon0) / 0.1))
        j = int(np.floor((la - kf.lat0) / 0.1))
        elle, _ = integrate.dblquad(
            lambda y, x: stats.norm.pdf(x, lo, sx) * stats.norm.pdf(y, la, sy),
            kf.lon0 + 0.1 * i, kf.lon0 + 0.1 * (i + 1), lambda x: kf.lat0 + 0.1 * j,
            lambda x: kf.lat0 + 0.1 * (j + 1))
        self.assertAlmostEqual(kut[i, j], elle, places=7)

    def test_kucuk_bant_tek_hucrede(self):
        kf = kafes_kur()
        kut = kde_sekli(kf, [-118.05], [36.05], [0.5])               # 0,5 km << 10 km hücre
        self.assertGreater(kut.max(), 0.99)

    def test_kenar_disi_kutle_kaybi(self):
        kf = kafes_kur()
        kut = kde_sekli(kf, [-120.0], [34.0 + 2.0], [20.0])         # sol kenarda: yarı kütle dışarıda
        self.assertTrue(0.4 < kut.sum() < 0.6)

    def test_bant_komsu_uzakligi(self):
        lon = np.array([-118.0, -118.0, -118.0]) + np.array([0.0, 0.1, 0.3])
        d = bant_km(lon, np.full(3, 36.0), 1)
        self.assertAlmostEqual(d[0], 0.1 * 111.32 * np.cos(np.deg2rad(36.0)), places=1)
        self.assertTrue((bant_km(lon, np.full(3, 36.0), 1, alt=50.0) == 50.0).all())

    def test_geysers_kutusu(self):
        self.assertTrue(geysers_mi([-122.8], [38.8])[0])
        self.assertFalse(geysers_mi([-122.0], [38.8])[0])

    def test_kafes_duzensiz_reddedilir(self):
        dd = pd.DataFrame([(-120.0, -119.9, 34.0, 34.1), (-119.85, -119.75, 34.0, 34.1)],
                          columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])
        with self.assertRaises(ModelHatasi):
            Kafes(dd)


class GrTesti(unittest.TestCase):
    K = np.r_[np.round(np.arange(4.95, 9.0, 0.1), 2), np.inf]

    def test_saf_gr_toplam_ve_oran(self):
        o = bukulu_gr(2.0, 1.0, 4.95, self.K, mc_koseli=None)
        self.assertAlmostEqual(o.sum(), 2.0, places=9)               # son kutu açık: toplam = oran
        self.assertAlmostEqual(o[1] / o[0], 10 ** -0.1, places=9)

    def test_bukulu_kuyruk_daha_ince_toplam_korunur(self):
        saf = bukulu_gr(2.0, 0.9, 4.95, self.K, mc_koseli=None)
        buk = bukulu_gr(2.0, 0.9, 4.95, self.K, mc_koseli=8.0)
        self.assertAlmostEqual(buk.sum(), 2.0 * 1.0, delta=2e-3)
        self.assertLess(buk[-10:].sum(), saf[-10:].sum())
        self.assertGreaterEqual(buk.min(), 0.0)

    def test_gecersiz(self):
        with self.assertRaises(ModelHatasi):
            bukulu_gr(1.0, -1.0, 4.95, self.K)


if __name__ == '__main__':
    unittest.main()
