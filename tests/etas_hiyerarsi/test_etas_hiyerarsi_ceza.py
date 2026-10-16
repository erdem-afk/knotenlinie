"""Hiyerarşik büzülme: bilinen cevaplı iki bölgeli sentetik dünya, τ=∞ özdeşliği, gradyan, havuz."""
import unittest

import numpy as np
import pandas as pd
from scipy.optimize import approx_fprime

from knotenlinie.etas import model as M
from knotenlinie.etas_hiyerarsi import cekirdek as C
from knotenlinie.etas_hiyerarsi.ceza import Cezali, ayarla_ceza
from knotenlinie.ortak_zemin.veri import IZGARA
from knotenlinie.yan_tezgah import mle as ML

KUTU = (40.0, 41.6, 10.0, 11.6)   # enlem0, enlem1, boylam0, boylam1
MC0 = 2.5
B = 1.0
CEKIRDEK = dict(mu=0.5, K=0.02, c=0.02, alpha=0.6, p=1.2, D=2.0, q=1.8, gamma=0.1)


def izgara():
    la0, la1, lo0, lo1 = KUTU
    rows = [[x, x + .1, y, y + .1] for x in np.arange(lo0, lo1 - 1e-8, .1) for y in np.arange(la0, la1 - 1e-8, .1)]
    return pd.DataFrame(rows, columns=IZGARA)


def benzet(th, T, seed, ust=4000):
    """Gözlenen-ebeveyn ETAS: tek Mc, düzgün zemin, kapalı dikdörtgen (dışarı düşen kız atılır)."""
    rng = np.random.default_rng(seed)
    met = M.yerel_metrik(KUTU)
    la0, la1, lo0, lo1 = KUTU
    n0 = rng.poisson(th['mu'] * T)
    tt = list(rng.uniform(0, T, n0)); mm = list(MC0 + rng.exponential(1 / (B * M.LN10), n0))
    lon = rng.uniform(lo0, lo1, n0); lat = rng.uniform(la0, la1, n0)
    xx, yy = (list(v) for v in met.km(lon, lat))
    i = 0
    while i < len(tt):
        if len(tt) > ust:
            raise ValueError('sentetik bütçe')
        n = rng.poisson(th['K'] * 10 ** (th['alpha'] * (mm[i] - MC0)) * th['c'] ** (1 - th['p']) / (th['p'] - 1))
        if n:
            t = tt[i] + th['c'] * (rng.random(n) ** (-1 / (th['p'] - 1)) - 1)
            m = MC0 + rng.exponential(1 / (B * M.LN10), n)
            Di = th['D'] * 10 ** (th['gamma'] * (mm[i] - MC0))
            r = Di * np.sqrt((1 - rng.random(n)) ** (-1 / (th['q'] - 1)) - 1)
            a = rng.uniform(0, 2 * np.pi, n)
            x = xx[i] + r * np.cos(a); y = yy[i] + r * np.sin(a)
            lo, la = met.derece(x, y)
            keep = (t < T) & (lo >= lo0) & (lo < lo1) & (la >= la0) & (la < la1)
            tt.extend(t[keep]); mm.extend(m[keep]); xx.extend(x[keep]); yy.extend(y[keep])
        i += 1
    o = np.argsort(tt)
    lon, lat = met.derece(np.asarray(xx)[o], np.asarray(yy)[o])
    return np.asarray(tt)[o], np.asarray(mm)[o], lon, lat


def olabilirlik(t, m, lon, lat, T):
    return ML.Olabilirlik(t, m, lon, lat, B, T, MC0, np.full(len(t), MC0), [(0., T, 1.0)], izgara(), KUTU)


def gercek_v(th):
    return ML.donustur(th, B, 'ortak')


class TestCeza(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t, cls.m, cls.lon, cls.lat = benzet(dict(CEKIRDEK, mu=0.4), 120., 11)
        cls.L = olabilirlik(cls.t, cls.m, cls.lon, cls.lat, 120.)
        cls.v0 = gercek_v(CEKIRDEK)

    def test_tema_referans_kaymasi(self):
        th = dict(CEKIRDEK)
        g = C.tema(th, mc0=C.M_REF)   # Mc0 = M_REF ise K_ref = K, D_ref = D
        self.assertAlmostEqual(g[0], np.log(th['K']), 12)
        self.assertAlmostEqual(g[4], np.log(th['D']), 12)
        g2 = C.tema(th, mc0=MC0)
        self.assertAlmostEqual(g2[0], np.log(th['K']) + M.LN10 * th['alpha'] * (C.M_REF - MC0), 12)
        self.assertAlmostEqual(g2[6], np.log(th['gamma'] + C.GAMMA_OFS), 12)

    def test_tau_sonsuz_R_ozdes(self):
        P = Cezali(self.L, C.tema(CEKIRDEK, MC0), float('inf'), MC0)
        f0, g0 = self.L.objectif(self.v0, 'ortak')
        f1, g1 = P.objectif(self.v0, 'ortak')
        self.assertEqual(f0, f1)
        np.testing.assert_array_equal(g0, g1)
        a = ayarla_ceza(self.L, C.tema(CEKIRDEK, MC0), float('inf'), self.v0, maksiter=60, mc0=MC0)
        self.assertEqual(a['ceza'], 0.0)
        self.assertAlmostEqual(a['logL'], a['logL_cezali'], 12)

    def test_ceza_gradyani_sonlu_farkla(self):
        cek = C.tema(CEKIRDEK, MC0) + 0.3
        P = Cezali(self.L, cek, 0.4, MC0)
        v = self.v0 + 0.05
        f, g = P.objectif(v, 'ortak')
        num = approx_fprime(v, lambda z: P.objectif(z, 'ortak')[0], 1e-6)
        np.testing.assert_allclose(g, num, rtol=2e-4, atol=2e-6)

    def test_havuz_ters_varyans(self):
        k1 = dict(ad='a', tema=[0.] * 7, tema_var=[1.] * 7, dallanma=.5, basari=True)
        k2 = dict(ad='b', tema=[3.] * 7, tema_var=[.25] * 7, dallanma=.5, basari=True)
        k3 = dict(ad='c', tema=[100.] * 7, tema_var=[.01] * 7, dallanma=.999999, basari=True)
        h = C.havuz([k1, k2, k3])
        np.testing.assert_allclose(h['tema'], [2.4] * 7)       # (0*1 + 3*4)/(1+4)
        self.assertEqual(h['uyeler'], ['a', 'b'])
        self.assertEqual(h['dislanan'][0]['ad'], 'c')
        self.assertIsNone(C.havuz([k3]))

    def test_hessian_std_dogru_mertebe(self):
        """MLE'deki delta-yöntemi SE'si, tekrarlar arası yayılımla aynı mertebede (faktör 3)."""
        tema, se = [], []
        for tohum in range(31, 43):
            t, m, lo, la = benzet(dict(CEKIRDEK, mu=0.8), 150., tohum)
            L = olabilirlik(t, m, lo, la, 150.)
            r = ayarla_ceza(L, C.tema(CEKIRDEK, MC0), float('inf'), self.v0, maksiter=200, mc0=MC0)
            if r['dallanma'] > 0.99:
                continue
            cov, tani = C.tema_kovaryans(L, r['x'], MC0)
            self.assertEqual(tani['tekil_yon'], 0)
            tema.append(r['tema']); se.append(np.sqrt(np.diag(cov)))
        tema, se = np.array(tema), np.array(se)
        self.assertGreaterEqual(len(tema), 8)
        for j in (1, 2, 3):      # c, alpha, p
            yayilim = tema[:, j].std(ddof=1)
            tahmin = float(np.sqrt((se[:, j] ** 2).mean()))
            self.assertLess(tahmin / yayilim, 3.0)
            self.assertGreater(tahmin / yayilim, 1 / 3.0)

    def test_buzulme_kisa_pencerede_mse_dusurur(self):
        """İki bölgeli dünya: gerçek çekirdek bilinir; kısa pencerede τ=0,2 MSE'yi düşürür."""
        bolge = dict(CEKIRDEK)                      # bölge parametreleri çekirdek etrafında küçük sapmalı
        bolge.update(K=0.022, p=1.25, D=2.3)
        gercek = C.tema(bolge, MC0)
        cek = C.tema(CEKIRDEK, MC0)                 # uzun bölgeden kestirilmiş çekirdek (burada doğrusu)
        hata = {'sonsuz': [], 'tau': []}
        for tohum in range(21, 29):
            t, m, lo, la = benzet(dict(bolge, mu=0.8), 60., tohum)
            if len(t) < 40:
                continue
            L = olabilirlik(t, m, lo, la, 60.)
            r_inf = ayarla_ceza(L, cek, float('inf'), self.v0, maksiter=200, mc0=MC0)
            r_tau = ayarla_ceza(L, cek, 0.2, self.v0, maksiter=200, mc0=MC0)
            for ad, r in (('sonsuz', r_inf), ('tau', r_tau)):
                # K, c, alpha, p, D, q (gamma ve mu hariç): log tema hatası
                d = np.array(r['tema']) - gercek
                hata[ad].append(float(np.mean(d[:6] ** 2)))
        self.assertGreaterEqual(len(hata['tau']), 5)
        self.assertLess(np.mean(hata['tau']), np.mean(hata['sonsuz']))


if __name__ == '__main__':
    unittest.main()
