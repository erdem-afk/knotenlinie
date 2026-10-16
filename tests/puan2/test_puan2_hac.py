import unittest

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.blok import blok_ozeti
from knotenlinie.puan2 import italya
from knotenlinie.puan2.hac import gecikme_kurali, hac_ozeti
from knotenlinie.skor_defteri import karisim as K
from tests._veri import kosu_gerek


class HacTest(unittest.TestCase):
    def test_gecikme_kurali(self):
        self.assertEqual(gecikme_kurali(1826), 7)
        self.assertEqual(gecikme_kurali(3653), 8)
        self.assertEqual(gecikme_kurali(100), 4)

    def test_el_hesabi(self):
        r = hac_ozeti([1.0, 2.0, 3.0], [1, 1, 1], gecikme=1)
        # u=[-1,0,1]; s = 2 + 2·0.5·(u1u0+u2u1)=2; SE = sqrt(3/2·2)/3
        self.assertAlmostEqual(r['SE_HAC'], np.sqrt(3.0) / 3.0, places=14)
        self.assertAlmostEqual(r['IG'], 2.0)

    def test_gecikme_sifir_iid_ve_gun_bloklu_sandwich(self):
        rng = np.random.default_rng(0)
        T = 300
        D = rng.normal(0.1, 1.0, T)
        n = rng.poisson(0.4, T)
        r = hac_ozeti(D, n, gecikme=0)
        # her gün ayrı blok (7 gün aralıklı tarihler) = blok_ozeti'nin gün-bloklu hali
        gunler = [pd.Timestamp('2011-01-03') + pd.Timedelta(days=7 * i) for i in range(T)]
        b = blok_ozeti(D, n, gunler)
        self.assertAlmostEqual(r['SE_HAC'], b['SE_blok'], places=14)
        # n≡1 ve L=0: klasik ortalama standart hatası s/√T
        r1 = hac_ozeti(D, np.ones(T), gecikme=0)
        self.assertAlmostEqual(r1['SE_HAC'], D.std(ddof=1) / np.sqrt(T), places=12)

    def test_pozitif_otokorelasyon_se_buyutur(self):
        rng = np.random.default_rng(2)
        e = rng.normal(size=2000)
        x = np.zeros(2000)
        for i in range(1, 2000):
            x[i] = 0.7 * x[i - 1] + e[i]
        s0 = hac_ozeti(x, np.ones(2000), gecikme=0)['SE_HAC']
        s7 = hac_ozeti(x, np.ones(2000), gecikme=7)['SE_HAC']
        # AR(1) ρ=0,7; Bartlett L=7 kesik: teorik oran sqrt(1+2Σ(1−l/8)ρ^l) (≈1,8; tam 2,38 değil)
        teorik = np.sqrt(1 + 2 * sum((1 - l / 8) * 0.7 ** l for l in range(1, 8)))
        self.assertLess(abs(s7 / s0 / teorik - 1), 0.15)
        self.assertGreater(s7 / s0, 1.5)

    @kosu_gerek('defter/U/R-ortak-kaskad__2011-2015__olay.csv.gz', 'defter/U/R-ortak-kaskad__2011-2015__marjinal.npz',
                    'defter/U/ETAS-LM__2011-2015__olay.csv.gz', 'defter/U/ETAS-LM__2011-2015__marjinal.npz',
                    'defter/AJ/AJ__2011-2015__olay.csv.gz', 'defter/AJ/AJ__2011-2015__marjinal.npz')
    def test_gercek_defter_hac_blokla_uyumlu(self):
        d, m = italya.yukle()
        k = K.gun_kazanci([d['AJ']], d['ETAS-LM'], 2.95, [1.0])
        b = blok_ozeti(k['D'], k['n'], k['gunler'], n=k['N'])
        h = hac_ozeti(k['D'], k['n'], n=k['N'])
        h7 = hac_ozeti(k['D'], k['n'], gecikme=7, n=k['N'])
        self.assertEqual(h['gecikme'], 7)
        self.assertEqual(h['T'], 1826)
        self.assertAlmostEqual(h['IG'], b['IG'], places=12)
        self.assertLess(abs(h['SE_HAC'] / b['SE_blok'] - 1), 0.25)
        self.assertEqual(h['SE_HAC'], h7['SE_HAC'])   # kural 7 = yan satır 7 (1826 gün)


if __name__ == '__main__':
    unittest.main()
