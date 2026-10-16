import itertools
import unittest

import numpy as np
from scipy import stats

from knotenlinie.puan2.satir import w_perm, w_tam, w_yan


def perm_elle(y):
    """Bilinen cevap: tüm işaret çevirmeleri, ortalama rank, iki yanlı."""
    y = np.asarray(y, float)
    r = stats.rankdata(np.abs(y))
    obs = r[y > 0].sum()
    ort = r.sum() / 2
    t = [sum(ri for ri, s in zip(r, sg) if s) for sg in itertools.product([0, 1], repeat=len(y))]
    return float(np.mean([abs(x - ort) >= abs(obs - ort) - 1e-9 for x in t]))


class WYanTest(unittest.TestCase):
    def test_bagsiz_exact_ve_perm_ayni(self):
        # y = [1,2,3,4,5] (aT=aE=0): W=0 → exact p = 2/32 = 0,0625
        lam_t = np.ones(5)
        lam_a = np.exp(np.array([1., 2., 3., 4., 5.]))
        r = w_yan(lam_a, lam_t, 0.0, 0.0)
        self.assertAlmostEqual(r['p_W_tam'], 0.0625, places=12)
        self.assertFalse(r['bag_var'])
        self.assertIsNone(r['not_'])
        self.assertAlmostEqual(r['p_W_perm'], 0.0625, places=12)

    def test_bagli_exact_gecersiz_perm_dogru(self):
        y = np.array([1., 1., 2., -3., 4., 4., 5.])     # |y| bağlı
        lam_t = np.ones(7)
        lam_a = np.exp(y)
        r = w_yan(lam_a, lam_t, 0.0, 0.0)
        self.assertTrue(r['bag_var'])
        self.assertEqual(r['not_'], 'bağ var, exact geçersiz')
        self.assertAlmostEqual(r['p_W_perm'], perm_elle(y), places=12)
        self.assertAlmostEqual(w_perm(y), perm_elle(y), places=12)
        self.assertIsNotNone(w_tam(lam_a, lam_t, 0.0, 0.0))   # scipy üretir ama geçersiz


if __name__ == '__main__':
    unittest.main()
