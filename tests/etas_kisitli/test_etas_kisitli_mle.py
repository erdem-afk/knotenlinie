"""Dallanma kısıtlı MLE: sentetik alt-kritik katalogda geri kazanım, kısıt bağlar, serbest = R."""
import unittest
import numpy as np
from knotenlinie.etas_kisitli import mle as K
from knotenlinie.etas_uzun.mle import Olabilirlik, ayarla
from tests.etas_uzun.test_etas_uzun_mle import benzet, izgara

NGERCEK = .5


class TestKisitli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        box = (40., 40.4, 12., 12.4)
        cls.grid = izgara(box, eksik=True)
        th = dict(mu=.38, c=.03, alpha=.45, p=1.35, D=1.2, q=1.8, gamma=.2)
        th['K'] = NGERCEK*(th['p']-1)*th['c']**(th['p']-1)*(1-th['alpha'])
        cls.th = th
        t, m, x, y = benzet(th, 1., 6000., 3000., cls.grid, box, 20261012)
        cls.L = Olabilirlik(t, m, x, y, 1., 6000., 3000., cls.grid, box)
        cls.R = ayarla(cls.L, 'ortak', maksiter=300)

    def test_sinirlar(self):
        self.assertEqual(K.sinirlar(K.SERBEST), K.SINIRLAR)
        b = K.sinirlar(.7)
        self.assertAlmostEqual(1/(1+np.exp(-b[1][1])), .7, places=12)
        self.assertEqual(b[0], K.SINIRLAR[0])
        with self.assertRaises(ValueError):
            K.sinirlar(1.)
        for x0 in K.baslangiclar(self.R['x'], .3):
            lo, hi = zip(*K.sinirlar(.3))
            self.assertTrue(np.all(x0 >= lo) and np.all(x0 <= hi))

    def test_serbest_R_ile_ozdes(self):
        fit = K.ayarla_kisitli(self.L, K.SERBEST, self.R['x'], maksiter=300)
        self.assertAlmostEqual(fit['logL'], self.R['logL'], delta=1e-9*abs(self.R['logL']))
        self.assertAlmostEqual(fit['dallanma'], self.R['dallanma'], places=5)
        for k, v in self.R['parametreler'].items():
            self.assertAlmostEqual(fit['parametreler'][k]/v, 1., places=3)

    def test_altkritik_geri_kazanim_ve_bagli_olmayan_kisit(self):
        fit = K.ayarla_kisitli(self.L, .8, self.R['x'], maksiter=300)
        print('AJ SENTETIK gercek n', NGERCEK, 'serbest n', self.R['dallanma'], 'kisitli(.8) n', fit['dallanma'], flush=True)
        self.assertLess(abs(fit['dallanma']-NGERCEK), .18)
        self.assertLess(fit['dallanma'], .8-1e-3)
        self.assertFalse(fit['sinirda'])
        self.assertAlmostEqual(fit['logL'], self.R['logL'], delta=1e-6*abs(self.R['logL']))
        hat = fit['parametreler']
        self.assertLess(abs(hat['alpha']-.45), .2)
        self.assertLess(abs(hat['p']-1.35), .2)
        self.assertGreaterEqual(fit['logL']+1e-6, self.L.deger(self.th))

    def test_bagli_kisit_sinirda_ve_logL_dusmez_artmaz(self):
        fit = K.ayarla_kisitli(self.L, .3, self.R['x'], maksiter=300)
        self.assertTrue(fit['sinirda'])
        self.assertLessEqual(fit['dallanma'], .3+1e-9)
        self.assertAlmostEqual(fit['dallanma'], .3, places=6)
        self.assertLessEqual(fit['logL'], self.R['logL']+1e-9)
        self.assertGreater(fit['logL'], self.R['logL']-60.)   # makul: kısıt çok yıkmaz

    def test_model_p(self):
        fit = K.ayarla_kisitli(self.L, .3, self.R['x'], maksiter=50)
        p = K.model_p(dict(parametreler={}, dallanma=1., x=[0.], logL=0., baska=7), fit)
        self.assertEqual(p['baska'], 7)
        self.assertEqual(p['kisitli']['n_max'], .3)
        self.assertEqual(p['x'], fit['x'])


if __name__ == '__main__':
    unittest.main()
