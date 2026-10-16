"""q̄ (hedef i): büyük olay yokken 1, sızıntı yok, bağımsız sayısal integrale eşit."""
import unittest

import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.special import ndtr

from knotenlinie.etas_stai.arayuz import ALT_KENAR, q_gunluk
from knotenlinie.etas_stai.tamlik import MC0, SIGMA, Z95, sonra_a

EDGES = np.r_[np.round(np.arange(2.95, 9.0, 0.1), 2), np.inf]
KUTU = (40., 41., 12., 13.)
EPOCH = pd.Timestamp('1985-01-01', tz='UTC')


def kat(satirlar):
    return pd.DataFrame(satirlar, columns=['zaman', 'enlem', 'boylam', 'derinlik', 'mw'])


def fit_a():
    return dict(stai=dict(tur='a'), stai_theta=None, b=dict(deger=1.0), kutu=list(KUTU),
                parametreler=dict(mu=0.5, K=0.02, c=0.02, alpha=0.7, p=1.2, D=1.0, q=1.8, gamma=0.1))


class TestQGunluk(unittest.TestCase):
    def setUp(self):
        self.ana = '2010-03-10T23:50:00Z'
        self.raw = kat([
            ['2010-01-05T00:00:00Z', 40.5, 12.5, 5.0, 3.0],
            [self.ana, 40.5, 12.5, 5.0, 6.3],
            ['2010-03-10T23:55:00Z', 40.5, 12.5, 5.0, 4.4],
            ['2010-03-11T09:00:00Z', 40.5, 12.5, 5.0, 3.5],
        ])

    def test_buyuk_olay_yoksa_bir_ve_aralik(self):
        q = q_gunluk(fit_a(), self.raw, EDGES, '2010-02-01T00:00:00Z', '2010-03-10T00:00:00Z')
        self.assertTrue(np.all(q == 1.0))
        q = q_gunluk(fit_a(), self.raw, EDGES, '2010-03-10T00:00:00Z', '2010-03-14T00:00:00Z')
        self.assertTrue(np.all(q[0] == 1.0))                 # gün içi olay sızdırılmaz
        self.assertTrue(((q > 0) & (q <= 1)).all())
        self.assertTrue((q[1] < 1).any())                    # ertesi gün ilk saatlerde eksik
        self.assertTrue((np.diff(q[1]) >= -1e-12).all())     # büyüklükle artar

    def test_sizinti_yok(self):
        a, z = '2010-03-09T00:00:00Z', '2010-03-12T00:00:00Z'
        q0 = q_gunluk(fit_a(), self.raw, EDGES, a, z)
        fazla = pd.concat([self.raw, kat([['2010-03-10T20:00:00Z', 40.4, 12.4, 5.0, 6.8]])], ignore_index=True)
        q1 = q_gunluk(fit_a(), fazla, EDGES, a, z)
        np.testing.assert_array_equal(q0[:2], q1[:2])        # 9 ve 10 Mart değişmez
        self.assertFalse(np.array_equal(q0[2], q1[2]))       # 11 Mart'ta yeni olay etkili

    def test_bagimsiz_sayisal_integral(self):
        f = fit_a()
        q = q_gunluk(f, self.raw, EDGES, '2010-03-11T00:00:00Z', '2010-03-12T00:00:00Z')[0]
        th, beta = f['parametreler'], 1.0 * np.log(10)
        t0 = float((pd.Timestamp('2010-03-11', tz='UTC') - EPOCH) / pd.Timedelta(days=1))
        tm = float((pd.Timestamp(self.ana) - EPOCH) / pd.Timedelta(days=1))
        ti = float((pd.Timestamp('2010-03-10T23:55:00Z') - EPOCH) / pd.Timedelta(days=1))

        def rate(t):
            r = th['mu'] + th['K'] * 10 ** (th['alpha'] * (6.3 - MC0)) * (t - tm + th['c']) ** (-th['p'])
            return r + th['K'] * 10 ** (th['alpha'] * (4.4 - MC0)) * (t - ti + th['c']) ** (-th['p'])

        def mu(t):
            return float(sonra_a(np.array([t]), np.array([tm]), np.array([6.3]))[0]) - Z95 * SIGMA

        for j in (0, 3, 10, 30):
            m1, m2 = EDGES[j], EDGES[j + 1]
            qm = lambda t: quad(lambda m: np.exp(-beta * m) * ndtr((m - mu(t)) / SIGMA), m1, m2)[0] / \
                quad(lambda m: np.exp(-beta * m), m1, m2)[0]
            pay = quad(lambda s: rate(t0 + s) * qm(t0 + s), 0, 1, points=[1e-3, 1e-2, .1], limit=200)[0]
            payda = quad(lambda s: rate(t0 + s), 0, 1, points=[1e-3, 1e-2, .1], limit=200)[0]
            self.assertAlmostEqual(q[j], pay / payda, delta=2e-3)


if __name__ == '__main__':
    unittest.main()
