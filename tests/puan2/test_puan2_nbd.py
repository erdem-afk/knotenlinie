import unittest

import numpy as np
from scipy import stats
from scipy.special import gammaln

from knotenlinie.karsilastir.puan import n_testi
from knotenlinie.puan2 import italya
from knotenlinie.puan2.nbd import a_kestir, nbd_n_testi, pencere_sayimlari, varyans
from tests._veri import veri_gerek


def pmf_nbd(k, mean, var):
    """Bağımsız NB pmf: r=μ²/(V−μ), p=r/(r+μ)."""
    r = mean * mean / (var - mean)
    p = r / (r + mean)
    return np.exp(gammaln(k + r) - gammaln(r) - gammaln(k + 1) + r * np.log(p) + k * np.log1p(-p))


class NbdTest(unittest.TestCase):
    def test_bilinen_cevap_toplam_pmf(self):
        mean, var, n = 10.0, 20.0, 12
        k = np.arange(0, 4000)
        pm = pmf_nbd(k, mean, var)
        d2 = pm[:n + 1].sum()
        d1 = pm[n:].sum()
        r = nbd_n_testi(mean, n, varyans_degeri=var)
        self.assertAlmostEqual(r['alt_kuyruk'], d2, places=10)
        self.assertAlmostEqual(r['ust_kuyruk'], d1, places=10)
        self.assertEqual(r['dagilim'], 'nbd')

    def test_varyans_poisson_a_sifir_yakinsar(self):
        for lam, n in [(13.0, 13), (130.0, 99), (1350.0, 1341)]:
            p = n_testi(lam, n)
            r = nbd_n_testi(lam, n, a=1e-9)
            self.assertLess(abs(r['ust_kuyruk'] - p['ust_kuyruk']), 1e-5)
            self.assertLess(abs(r['alt_kuyruk'] - p['alt_kuyruk']), 1e-5)
        # a=0 ve V=Λ tam Poisson
        r = nbd_n_testi(13.0, 13, a=0.0)
        self.assertEqual(r['dagilim'], 'poisson')
        self.assertEqual(r['ust_kuyruk'], n_testi(13.0, 13)['ust_kuyruk'])

    def test_pycsep_formulu(self):
        # pyCSEP _nbd_number_test_ndarray: upsilon=1-(var-mean)/var, tau=mean²/(var-mean), eps=1e-6
        lam, n, var = 7.1, 2, 9.0
        ups, tau = 1.0 - (var - lam) / var, lam ** 2 / (var - lam)
        d1 = 1.0 - stats.nbinom.cdf(n - 1e-6, tau, ups, loc=0)
        d2 = stats.nbinom.cdf(n + 1e-6, tau, ups, loc=0)
        r = nbd_n_testi(lam, n, varyans_degeri=var)
        self.assertAlmostEqual(r['ust_kuyruk'], d1, places=12)
        self.assertAlmostEqual(r['alt_kuyruk'], d2, places=12)

    def test_asiri_yayilma_geciti_genisletir(self):
        # Poisson'da reddedilen sayı NBD'de geçer (Λ=1352, N=1341+400)
        p = n_testi(1352.0, 1800)
        q = nbd_n_testi(1352.0, 1800, a=0.1)
        self.assertFalse(p['gecti'])
        self.assertTrue(q['gecti'])
        self.assertAlmostEqual(varyans(10.0, 0.5), 10 + 50.0)

    def test_pencere_ve_a(self):
        # günler 0..364 her 10 günde bir olay: 365 gün, pencere 100, kayma 100 → 3 pencere
        gun = np.arange(0, 365, 10.0)
        say = pencere_sayimlari(gun, 0, 365, 100, 100)
        self.assertEqual(list(say), [10, 10, 10])
        r = a_kestir([1, 3, 5, 7])
        self.assertAlmostEqual(r['a'], (20 / 3 - 4) / 16)
        self.assertEqual(a_kestir([5, 5, 5])['a'], 0.0)   # v<m → 0

    @veri_gerek('ortak/italya_katalog_le2015.csv', 'ortak/italya_izgara.csv')
    def test_gercek_katalog_a(self):
        r = italya.a_italya(3.95)   # gerçek HORUS ≤2010
        self.assertEqual(r['olay'], 674)
        self.assertEqual(r['pencere'], 256)
        self.assertTrue(0.05 < r['a'] < 0.3)


if __name__ == '__main__':
    unittest.main()
