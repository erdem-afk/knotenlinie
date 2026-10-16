"""STAI tespit eğrisi: kapalı biçimler sayısal integrale, düğüm azalması ince kuadratüre karşı."""
import unittest

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr

from knotenlinie.etas import model as M
from knotenlinie.etas_stai.mle import _omori_fark
from knotenlinie.etas_stai.tamlik import (MC0, SIGMA, Z95, KisaTamlik, donem, kutu_q, s_w, sonra_a, sonra_b)


class TestTamlik(unittest.TestCase):
    def test_hkj_degerleri(self):
        bt, bm = np.array([10.0]), np.array([6.3])
        v = sonra_a(np.array([10.0, 10.0 + 1.0, 10.0 + 0.1, 10.0 + 30.0, 10.0 + 30.1, 9.0]), bt, bm)
        self.assertTrue(np.isneginf(v[0]) and np.isneginf(v[4]) and np.isneginf(v[5]))
        self.assertAlmostEqual(v[1], 6.3 - 4.5, places=12)
        self.assertAlmostEqual(v[2], 6.3 - 4.5 - 0.75 * np.log10(0.1), places=12)
        self.assertAlmostEqual(v[3], 6.3 - 4.5 - 0.75 * np.log10(30.0), places=12)

    def test_hainzl_son_olay_kurali(self):
        bt = np.array([10.0, 11.0])
        v = sonra_b(np.array([10.5, 12.0, 80.0]), bt, (0.8, 2.0))
        self.assertAlmostEqual(v[0], MC0 + 0.8 * np.exp(-0.5 / 2.0), places=12)
        self.assertAlmostEqual(v[1], MC0 + 0.8 * np.exp(-1.0 / 2.0), places=12)  # en son olay
        self.assertTrue(np.isneginf(v[2]))

    def test_etkin_agirlik_kapali_cozum_sayisal_integral(self):
        beta = 1.0 * np.log(10.0)
        for a in (2.5, 3.1):
            for mu in (1.0, 2.7, 3.4, 5.0):
                f = lambda m: beta * np.exp(-beta * (m - MC0)) * ndtr((m - mu) / SIGMA)
                num = quad(f, a, 40.0, points=[mu], limit=300)[0]
                S, dS = s_w(np.array(mu), np.array(a), beta)
                self.assertAlmostEqual(float(S), num, places=9)
                h = 1e-5
                Sp, _ = s_w(np.array(mu + h), np.array(a), beta)
                Sm, _ = s_w(np.array(mu - h), np.array(a), beta)
                self.assertAlmostEqual(float(dS), float((Sp - Sm) / (2 * h)), places=7)
        S, dS = s_w(np.array(-np.inf), np.array(3.1), beta)
        self.assertAlmostEqual(float(S), 10 ** (-(3.1 - MC0)), places=14)
        self.assertEqual(float(dS), 0.0)

    def test_kutu_ortalama_tespit_sayisal(self):
        beta = 1.0 * np.log(10.0)
        mu = 3.2
        m1, m2 = np.array([2.95, 3.05, 3.95, 8.95]), np.array([3.05, 3.15, 4.05, np.inf])
        q = kutu_q(mu, m1, m2, beta)
        for i in range(4):
            hi = m2[i] if np.isfinite(m2[i]) else 60.0
            pay = quad(lambda m: np.exp(-beta * m) * ndtr((m - mu) / SIGMA), m1[i], hi, limit=200)[0]
            pay0 = quad(lambda m: np.exp(-beta * m), m1[i], hi, limit=200)[0]
            self.assertAlmostEqual(q[i], pay / pay0, places=8)
        self.assertTrue(np.allclose(kutu_q(-np.inf, m1, m2, beta), 1.0))
        self.assertTrue(((q > 0) & (q <= 1)).all() and q[0] < q[2] < q[3] + 1e-12)

    def test_dugum_azalmasi_ince_kuadratura(self):
        b = 1.0
        beta = b * np.log(10)
        bt, bm, T = np.array([100.0, 100.5, 300.0]), np.array([6.3, 5.4, 5.1]), 400.0
        for tur, theta in (('a', None), ('b', (0.8, 2.0))):
            st = KisaTamlik(tur, 50.0, b, bt, bm, T)
            r, dr = st.azalma(theta)
            self.assertTrue((r >= -1e-12).all())
            f = lambda t: float(np.exp(-beta * (donem(t, 50.0) - MC0)) - st.agirlik(np.array([t]), theta)[0][0])
            pts = sorted(tb + x for tb in bt for x in (1e-4, 1e-3, 1e-2, .1, 1, 10))
            num = quad(f, 0, T, points=pts, limit=800)[0]
            self.assertLess(abs(float(np.dot(r, st.genislik)) - num) / num, 0.02)
            c, p = 0.02, 1.2
            for tj in (100.0, 100.5, 99.9):
                g = lambda t: f(t) * (t - tj + c) ** (-p) if t > tj else 0.0
                ptj = sorted([tj + x for x in (1e-3, .01, .1, 1, 10)] + pts)
                numj = quad(g, tj, T, points=ptj, limit=1500)[0]
                hi = st.hi[None, :] - tj
                ok = hi > 0
                hi = np.where(ok, hi, 0.0)
                lo = np.minimum(np.maximum(st.lo[None, :] - tj, 0.0), hi)
                Om, _, _ = _omori_fark(lo, hi, c, p)
                self.assertLess(abs(float(((Om * ok) @ r)[0]) - numj) / numj, 0.005)

    def test_omori_fark_ilke_ile_ayni(self):
        lo, hi = np.array([[0.0, 0.3, 2.0]]), np.array([[0.5, 1.0, 9.0]])
        for c, p in ((0.02, 1.2), (0.1, 0.9)):
            I, Ic, Ip = _omori_fark(lo, hi, c, p)
            v, vc, vp = M._omori_ilke(hi, c, p)
            w, wc, wp = M._omori_ilke(lo, c, p)
            np.testing.assert_allclose(I, v - w, rtol=1e-12)
            np.testing.assert_allclose(Ic, vc - wc, rtol=1e-12)
            np.testing.assert_allclose(Ip, vp - wp, rtol=1e-9, atol=1e-13)

    def test_dugumler_kirilmayi_asmaz_ve_guc_yok_ise_bos(self):
        st = KisaTamlik('a', 50.0, 1.0, np.array([49.99, 60.0]), np.array([6.0, 5.5]), 100.0)
        self.assertFalse(((st.lo < 50.0) & (st.hi > 50.0)).any())
        self.assertEqual(len(KisaTamlik('b', 50.0, 1.0, np.empty(0), np.empty(0), 100.0).mid), 0)
        with self.assertRaises(ValueError):
            KisaTamlik('c', 50.0, 1.0, np.empty(0), np.empty(0), 100.0)


if __name__ == '__main__':
    unittest.main()
