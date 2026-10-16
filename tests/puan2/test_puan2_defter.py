import unittest

import numpy as np

from knotenlinie.puan2 import italya, kaliforniya
from knotenlinie.puan2.satir import hukum_eski, hukum_yeni, kazanc_satiri
from knotenlinie.skor_defteri import karisim as K
from tests._veri import kosu_gerek, veri_gerek

ITALYA_DEFTERLERI = kosu_gerek('defter/U/R-ortak-kaskad__2011-2015__olay.csv.gz', 'defter/U/R-ortak-kaskad__2011-2015__marjinal.npz',
                'defter/U/ETAS-LM__2011-2015__olay.csv.gz', 'defter/U/ETAS-LM__2011-2015__marjinal.npz',
                'defter/AJ/AJ__2011-2015__olay.csv.gz', 'defter/AJ/AJ__2011-2015__marjinal.npz')


@ITALYA_DEFTERLERI
class DefterTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d, cls.m = italya.yukle()

    def test_defter_logL_koşucu_logL(self):
        # npz logL = kos_defter'in koşucu logL'i (n! dahil); defterden hesap 1e-9 göreli
        for ad in (italya.R_AD, italya.LM_AD, italya.AJ_AD):
            ll = K.log_olabilirlik([self.d[ad]], [1.0], 2.95)
            self.assertLess(abs(ll - self.m[ad]['logL']) / abs(self.m[ad]['logL']), 1e-9)
        fark_defter = K.log_olabilirlik([self.d[italya.AJ_AD]], [1.0], 2.95) - \
            K.log_olabilirlik([self.d[italya.LM_AD]], [1.0], 2.95)
        fark_kosucu = self.m[italya.AJ_AD]['logL'] - self.m[italya.LM_AD]['logL']
        self.assertLess(abs(fark_defter - fark_kosucu) / abs(fark_kosucu), 1e-9)

    def test_satir_ig_logL_farki(self):
        M = italya.model_tablo(self.d, self.m)
        k = K.gun_kazanci(M['AJ'].defterler, self.d[italya.LM_AD], 2.95, [1.0])
        lam_o, _, mask = K.bilesen(M['AJ'].defterler, [1.0], 2.95)
        r = kazanc_satiri(k, lam_o[mask], self.d[italya.LM_AD].lam()[mask], None, None)
        fark = self.m[italya.AJ_AD]['logL'] - self.m[italya.LM_AD]['logL']
        self.assertLess(abs(r['IG'] * r['N'] - fark) / abs(fark), 1e-9)
        for kolon in ('SE_blok', 'SE_HAC', 'SE_HAC7', 'p_T', 'p_W', 'eski_hukum', 'yeni_hukum'):
            self.assertIsNotNone(r[kolon])
        self.assertEqual(r['kanit_duzeyi'], 'SP-ic')

    def test_karisim_marjinal_ve_olay_toplami_tutarli(self):
        M = italya.model_tablo(self.d, self.m)
        e7 = M['E7']
        for alt in (2.95, 3.95, 4.95):
            lam_marj = e7.beklenen(alt).sum()
            _, Lam_gun, _ = K.bilesen(e7.defterler, e7.agirlik, alt)
            self.assertLess(abs(lam_marj - Lam_gun.sum()) / lam_marj, 1e-9)

    def test_hukum_kurallari(self):
        self.assertEqual(hukum_eski(0.1, 2.0), 'başarı')
        self.assertEqual(hukum_eski(-0.1, 2.0), 'başarısızlık')
        self.assertEqual(hukum_yeni(0.1, 2.0, 2.0, 0.01, 0.01, 100), 'başarı')
        self.assertEqual(hukum_yeni(0.1, 2.0, 1.5, 0.01, 0.01, 100), 'belirsiz')   # HAC tutmaz
        self.assertEqual(hukum_yeni(0.1, 2.0, 2.0, 0.01, 0.2, 7), 'belirsiz')      # N küçük → W
        self.assertEqual(hukum_yeni(0.1, 2.0, 2.0, 0.2, 0.01, 7), 'başarı')

    @kosu_gerek('defter/Y/D1__scsn__2011-2020__olay.csv.gz', 'defter/Y/D0__scsn__2011-2020__olay.csv.gz')
    def test_kaliforniya_gercek_defter(self):
        oa, ga = kaliforniya.oku('D1')
        ot, gt = kaliforniya.oku('D0')
        k, la, lt = kaliforniya.kazanc(oa, ga, ot, gt, 2.8)
        self.assertEqual(k['N'], 3407)
        self.assertAlmostEqual(k['IG'], 0.2798, delta=5e-4)       # README.md table: +0.280
        ig_olay = np.log(la).mean() - np.log(lt).mean()
        self.assertAlmostEqual(k['IG_olay'], ig_olay, places=12)


if __name__ == '__main__':
    unittest.main()
