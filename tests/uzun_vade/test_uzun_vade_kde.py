"""GR oranları ve KDE şekli: kütle korunumu ve sıfır hücre kaçınması."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.uzun_vade.duzgunlestir import (_gauss_kutle, gr_oranlari,
                                          hucre_merkez_km, sekil_kde)


def kare_izgara(n, dx=0.1, lo=10.0, la=40.0):
    hucreler = []
    for i in range(n):
        for j in range(n):
            hucreler.append(dict(boylam_min=lo + i * dx, boylam_max=lo + (i + 1) * dx,
                                 enlem_min=la + j * dx, enlem_max=la + (j + 1) * dx))
    return pd.DataFrame(hucreler)


class GrTesti(unittest.TestCase):
    def test_mmin_ustu_korunum(self):
        kenar = np.r_[np.arange(4.0, 9.0, 0.1), np.inf]
        oran = gr_oranlari(100.0, 1.0, 4.0, kenar)
        self.assertAlmostEqual(float(oran.sum()), 100.0, places=6)

    def test_esik_alti_sifir(self):
        kenar = np.array([3.0, 3.5, 4.0, 5.0, np.inf])
        oran = gr_oranlari(50.0, 1.0, 4.0, kenar)
        self.assertEqual(oran[0], 0.0)
        self.assertEqual(oran[1], 0.0)
        self.assertGreater(oran[2], 0.0)

    def test_b_arttikca_yuksek_kutu_azalir(self):
        kenar = np.array([4.0, 5.0, 6.0, np.inf])
        oran = gr_oranlari(100.0, 1.0, 4.0, kenar)
        self.assertGreater(oran[0], oran[1])
        self.assertGreater(oran[1], oran[2])


class KdeTesti(unittest.TestCase):
    def test_sekil_toplam_bir(self):
        g = kare_izgara(9)
        p = np.array([[10.45, 40.45]])
        s = sekil_kde(p, g, sigma_km=10.0)
        self.assertAlmostEqual(float(s.sum()), 1.0, places=12)
        self.assertEqual(float(s[s.argmax()]), float(s.max()))

    def test_zemin_katkisi(self):
        g = kare_izgara(9)
        p = np.array([[10.45, 40.45]])
        s0 = sekil_kde(p, g, sigma_km=20.0, zemin_payi=0.0)
        s1 = sekil_kde(p, g, sigma_km=20.0, zemin_payi=0.5)
        beklenen = 0.5 * s0 + 0.5 / len(g)
        np.testing.assert_allclose(s1, beklenen, rtol=1e-12, atol=1e-15)
        self.assertTrue((s1 > 0).all())

    def test_gauss_kutle_yaklasik_bir(self):
        # 6°x6° ızgara sigma=15 km kuyruğu büyük ölçüde taşır; kütle ~1.
        g = kare_izgara(60)
        a = g[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float)
        cx, cy, alan = hucre_merkez_km(a)
        kütle = _gauss_kutle(np.array([[cx.mean(), cy.mean()]]), np.array([15.0]),
                             (cx, cy), alan)
        self.assertGreater(float(kütle.sum()), 0.95)
        self.assertLessEqual(float(kütle.sum()), 1.01)

    def test_uyarlamali_bant_pozitif(self):
        g = kare_izgara(20)
        rng = np.random.default_rng(7)
        p = np.column_stack([10.1 + 1.8 * rng.random(50), 40.1 + 1.8 * rng.random(50)])
        s = sekil_kde(p, g, k_komsu=5, zemin_payi=0.001)
        self.assertAlmostEqual(float(s.sum()), 1.0, places=12)
        self.assertGreaterEqual(float(s.min()), 0.001 / len(g) - 1e-18)


if __name__ == '__main__':
    unittest.main()
