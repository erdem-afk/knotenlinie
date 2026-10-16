"""Poisson logL ve olay-başı IG bilinen cevaplı; puan.eslestirilmis ile eşleşme."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.puan import eslestirilmis, log_olabilirlik
from knotenlinie.karsilastir.uzun_z import (_poisson_kimlik, katalog_oku, olay_ig,
                                     poisson_logl)


class LogLTesti(unittest.TestCase):
    def test_bilinen_poisson(self):
        bek = np.array([[2.0, 3.0]])
        goz = np.array([[1.0, 4.0]])
        elle = 1 * np.log(2.0) - 2.0 + 4 * np.log(3.0) - 3.0 - np.log(24.0)
        self.assertAlmostEqual(poisson_logl(bek, goz), float(elle), places=12)
        self.assertAlmostEqual(log_olabilirlik(bek, goz), float(elle), places=12)

    def test_sifir_oranda_eksi_sonsuz(self):
        self.assertEqual(poisson_logl(np.array([[0.0, 1.0]]), np.array([[1.0, 0.0]])),
                         -np.inf)


class IgTesti(unittest.TestCase):
    def test_bilinen_ig(self):
        lam_t = np.array([1.0, 2.0, 0.5, 4.0])
        c = 2.0
        lam_a = c * lam_t
        n = len(lam_t)
        ig_elle = np.log(c) - (lam_a.sum() - lam_t.sum()) / n
        r = olay_ig(lam_a, lam_t, lam_a.sum(), lam_t.sum(), tekrar=50)
        self.assertAlmostEqual(r['IG'], float(ig_elle), places=12)
        self.assertAlmostEqual(r['IG_olay'], float(np.log(c)), places=12)
        self.assertAlmostEqual(r['integral'], float(-(lam_a.sum() - lam_t.sum())), places=12)

    def test_puan_ile_eslesme(self):
        rng = np.random.default_rng(11)
        lam_t = 0.5 + rng.random(200)
        lam_a = lam_t * np.exp(0.3 + 0.2 * rng.standard_normal(200))
        p = eslestirilmis(lam_a, lam_t, lam_a.sum(), lam_t.sum())
        r = olay_ig(lam_a, lam_t, lam_a.sum(), lam_t.sum(), tekrar=50)
        self.assertAlmostEqual(r['IG'], p['IG'], places=10)
        self.assertAlmostEqual(r['IG_olay'], p['IG_olay'], places=10)
        self.assertAlmostEqual(r['integral'], p['integral_terimi'] * len(lam_t), places=8)

    def test_sifir_oran_tanimsiz(self):
        r = olay_ig(np.array([0.0, 1.0]), np.array([1.0, 1.0]), 1.0, 2.0)
        self.assertIsNone(r['IG'])
        self.assertEqual(r['durum'], 'tanımsız')

    def test_bootstrap_se_sifir_ayni_oran(self):
        lam = np.array([1.0, 2.0, 3.0, 4.0])
        r = olay_ig(lam, lam, lam.sum(), lam.sum(), tekrar=50)
        self.assertEqual(r['SE_blok'], 0.0)
        self.assertEqual(r['IG'], 0.0)

    def test_esik_alti_olay_ig_ye_karismaz(self):
        # Yalnız eşik üstü olaylar (mi>=0) IG'ye girer; logL kimliği birebir tutar.
        exp_a = np.array([[2.0], [1.0], [0.5]])
        exp_t = np.array([[1.0], [0.8], [0.6]])
        ci = np.array([0, 1, 2, 0, 1])
        mi = np.array([0, 0, 0, -1, -1])
        sec = mi >= 0
        obs = np.zeros((3, 1), int)
        np.add.at(obs, (ci[sec], mi[sec]), 1)
        r = olay_ig(exp_a.ravel()[ci[sec]], exp_t.ravel()[ci[sec]],
                    exp_a.sum(), exp_t.sum(), tekrar=50)
        r.update(logL_aday=poisson_logl(exp_a, obs), logL_taban=poisson_logl(exp_t, obs))
        self.assertEqual(r['N'], 3)
        self.assertAlmostEqual((r['logL_aday'] - r['logL_taban']) / r['N'], r['IG'], places=9)


class PoissonKimlikTesti(unittest.TestCase):
    def test_tutar(self):
        _poisson_kimlik(dict(durum='tanımlı', N=5, logL_aday=1.0, logL_taban=-4.0, IG=1.0))

    def test_tutmazsa_hata(self):
        with self.assertRaises(ValueError):
            _poisson_kimlik(dict(durum='tanımlı', N=5, logL_aday=1.0, logL_taban=-4.0, IG=2.0))


class KatalogKapisiTesti(unittest.TestCase):
    def test_2016_reddedilir(self, ):
        import tempfile, os
        d = pd.DataFrame(dict(zaman=['2016-01-01T00:00:00Z'], enlem=[38.0], boylam=[22.0],
                              derinlik=[5.0], mw=[5.0]))
        yol = os.path.join(tempfile.mkdtemp(), 'k.csv')
        d.to_csv(yol, index=False)
        with self.assertRaises(ValueError):
            katalog_oku(yol, (0.0, 40.0))


if __name__ == '__main__':
    unittest.main()
