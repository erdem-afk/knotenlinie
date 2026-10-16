"""STEP çekirdeği: kütle korunumu ve bilinen cevaplı integraller."""
import unittest

import numpy as np
from scipy.integrate import dblquad, quad

from knotenlinie.step import cekirdek as c


def kare_izgara(lon0, lat0, n, dx=0.1):
    lo = lon0 + dx * np.arange(n)
    la = lat0 + dx * np.arange(n)
    LO, LA = np.meshgrid(lo, la)
    LO, LA = LO.ravel(), LA.ravel()
    return np.column_stack([LO, LO + dx, LA, LA + dx])


class CekirdekTest(unittest.TestCase):
    def test_kutle_korunumu_ic_kaynak(self):
        g = kare_izgara(9.0, 41.0, 60)            # 6x6 derece, kaynak ortada
        for d, r in ((1.0, 40.0), (7.5, 80.0), (30.0, 140.0)):
            k = c.hucre_kutlesi(g, 12.0, 44.0, d, r)
            self.assertAlmostEqual(float(k.sum()), 1.0, places=9)
            self.assertTrue((k >= 0).all())

    def test_hucre_kutlesi_nicel_integralle(self):
        g = kare_izgara(11.9, 43.9, 3)
        lon0, lat0, d, r = 12.0, 44.0, 2.0, 30.0
        kx, ky = c.KM_DERECE * np.cos(np.radians(lat0)), c.KM_DERECE
        Z = dblquad(lambda y, x: 1 / (x * x + y * y + d * d), -r, r, -r, r)[0]
        k = c.hucre_kutlesi(g, lon0, lat0, d, r)
        for i in (0, 4, 8):
            x0, x1 = (g[i, 0] - lon0) * kx, (g[i, 1] - lon0) * kx
            y0, y1 = (g[i, 2] - lat0) * ky, (g[i, 3] - lat0) * ky
            ref = dblquad(lambda y, x: 1 / (x * x + y * y + d * d), x0, x1, y0, y1,
                          epsabs=1e-13, epsrel=1e-12)[0] / Z
            self.assertAlmostEqual(float(k[i]), ref, places=10)

    def test_kutu_disina_tasan_kutle_kaybolur(self):
        g = kare_izgara(9.0, 41.0, 60)
        k = c.hucre_kutlesi(g, 9.02, 41.02, 3.0, 100.0)     # köşeye yakın kaynak
        self.assertLess(float(k.sum()), 0.6)
        self.assertGreater(float(k.sum()), 0.1)

    def test_omori_integrali(self):
        for p in (0.8, 1.0, 1.0 + 1e-12, 1.3):
            ref = quad(lambda t: (t + 0.02) ** -p, 0.5, 7.0, epsabs=1e-13)[0]
            self.assertAlmostEqual(float(c.omori_integral(0.5, 7.0, 0.02, p)), ref, places=10)
        self.assertEqual(float(c.omori_integral(3.0, 3.0, 0.02, 0.9)), 0.0)

    def test_pencereler_artan(self):
        m = np.array([3.5, 4.5, 5.5, 6.4, 6.6, 7.5])
        self.assertTrue((np.diff(c.gk_yaricap(m)) > 0).all())
        self.assertTrue((np.diff(c.gk_sure(m)) > 0).all())
        self.assertAlmostEqual(float(c.gk_sure(5.0)), 10 ** (0.5409 * 5 - 0.547))


if __name__ == '__main__':
    unittest.main()
