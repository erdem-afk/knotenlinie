import itertools
import unittest

import numpy as np
from scipy.special import gammaln

from knotenlinie.karsilastir.puan import log_olabilirlik
from knotenlinie.puan2 import italya
from knotenlinie.puan2.ikili import ikili_kosullu_test, ikili_logL, ikili_logL_defter
from knotenlinie.puan2.satir import ikili_ig
from tests._veri import kosu_gerek

ITALYA_DEFTERLERI = kosu_gerek('defter/U/R-ortak-kaskad__2011-2015__olay.csv.gz', 'defter/U/R-ortak-kaskad__2011-2015__marjinal.npz',
                'defter/U/ETAS-LM__2011-2015__olay.csv.gz', 'defter/U/ETAS-LM__2011-2015__marjinal.npz',
                'defter/AJ/AJ__2011-2015__olay.csv.gz', 'defter/AJ/AJ__2011-2015__marjinal.npz')


class IkiliTest(unittest.TestCase):
    def test_bilinen_cevap_tek_hucre(self):
        lam = np.array([np.log(2.0), 0.3])
        self.assertAlmostEqual(ikili_logL(lam, [1, 0]), np.log(0.5) - 0.3, places=14)
        self.assertEqual(ikili_logL([0.0, 0.3], [1, 0]), float('-inf'))

    def test_lambda_sifira_poisson_olay_terimi(self):
        rng = np.random.default_rng(1)
        taban = rng.uniform(0.5, 2.0, size=200)
        n = (rng.uniform(size=200) < 0.05).astype(int)
        for s in (1e-4, 1e-6, 1e-8):
            lam = taban * s
            # Poisson (n! = 1 çünkü n ∈ {0,1}) ile fark O(λ)·N
            fark = abs(ikili_logL(lam, n) - log_olabilirlik(lam, n))
            self.assertLessEqual(fark, 2 * s * 2.0 * max(1, n.sum()))
        self.assertLess(abs(ikili_logL(taban * 1e-9, n) - log_olabilirlik(taban * 1e-9, n)), 1e-6)

    def test_defter_formulu_tam_kup_ile_ayni(self):
        rng = np.random.default_rng(5)
        kup = rng.gamma(0.3, 0.05, size=(30, 12, 4))       # gün×hücre×kutu
        gz = np.zeros(kup.shape, int)
        kes = rng.uniform(size=kup.shape) < kup            # Bernoulli(≈λ) gözlem
        gz[kes] = 1
        gz[0, 0, 0] = 2                                      # aynı kutuda iki olay: ikili için tek 1
        tam = ikili_logL(kup, gz)
        d = ikili_logL_defter(kup[gz > 0], kup.sum())
        self.assertAlmostEqual(tam, d, places=10)

    def test_kosullu_test_analitik_dagilim(self):
        # 4 kutu, k=2 farklı kutu, ağırlık ∝ λ: sıralı örnekleme olasılıkları elle
        lam = np.array([0.1, 0.4, 0.9, 1.6])
        n = np.array([0, 0, 1, 1])
        obs = ikili_logL(lam, n)
        w = lam / lam.sum()
        c = np.log(-np.expm1(-lam)) + lam
        P = 0.0
        for i, j in itertools.permutations(range(4), 2):
            pr = w[i] * w[j] / (1 - w[i])
            if c[i] + c[j] - lam.sum() <= obs + 1e-12:
                P += pr
        r = ikili_kosullu_test(lam, n, tekrar=40000, tohum=11)
        self.assertLess(abs(r['p'] - P), 4 * np.sqrt(P * (1 - P) / 40000) + 1e-3)
        r2 = ikili_kosullu_test(lam, n, tekrar=40000, tohum=11, uretec='pycsep')
        self.assertLess(abs(r2['p'] - P), 4 * np.sqrt(P * (1 - P) / 40000) + 1e-3)

    @ITALYA_DEFTERLERI
    def test_gercek_defter_ikili_fark_poisson_yakin(self):
        d, m = italya.yukle()
        M = italya.model_tablo(d, m)
        # M≥4,95: λ'lar çok küçük, N=14 farklı hücre-gün → ikili IG ≈ Poisson IG
        r = ikili_ig(M['AJ'].defterler, M['AJ'].agirlik, d['ETAS-LM'], 4.95)
        from knotenlinie.skor_defteri import karisim as K
        k = K.gun_kazanci(M['AJ'].defterler, d['ETAS-LM'], 4.95, [1.0])
        self.assertLess(abs(r['IG_ikili'] - k['IG']), 1e-3)
        self.assertLess(r['max_lam_olay'], 0.5)
        # M≥2,95: ikili ≠ Poisson (aynı hücre-gün-kutuda çoklu olay) ama sonlu
        r2 = ikili_ig(M['AJ'].defterler, M['AJ'].agirlik, d['ETAS-LM'], 2.95)
        self.assertTrue(np.isfinite(r2['IG_ikili']))

    @ITALYA_DEFTERLERI
    def test_gercek_marjinal_ikili_testler_calisir(self):
        d, m = italya.yukle()
        M = italya.model_tablo(d, m)
        lam, gz = M['LM'].beklenen(3.95), M['LM'].gozlem(3.95)
        r = ikili_kosullu_test(lam.sum(axis=1), gz.sum(axis=1), tekrar=300, tohum=1)
        self.assertEqual(r['dolu_kutu'], int((gz.sum(axis=1) > 0).sum()))
        self.assertTrue(0 <= r['p'] <= 1)


if __name__ == '__main__':
    unittest.main()
