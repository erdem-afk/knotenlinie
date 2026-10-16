"""Bilinen cevaplı çekirdek, dallanma, skor ve sızıntı testleri."""
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
from scipy.integrate import quad, dblquad

from knotenlinie.etas_lm import cekirdek as c
from knotenlinie.etas_lm.arka_plan import kur
from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.karsilastir.kosucu import Model, kos, karsilastir
from knotenlinie.karsilastir.gunluk_j import esik_kosu
from knotenlinie.ortak_zemin.veri import IZGARA


class CekirdekTest(unittest.TestCase):
    def test_yil_gun_ve_alpha(self):
        # Aynı saat için yıl yoğunluğu /365.25, gün yoğunluğuna eşit.
        year_rate = .011 * np.exp(1.3*(5-2.5)) / ((2/365.25+.00004)**1.16) / 365.25
        self.assertAlmostEqual(float(c.uretkenlik(5)/(2+c.C)**c.P), year_rate, places=12)

    def test_analitik_hucre(self):
        g = np.array([[-2, 3, -1, 4]])
        exact = dblquad(lambda y, x: c.D/(2*np.pi*(x*x+y*y+c.D*c.D)**1.5), -2, 3, lambda _: -1, lambda _: 4)[0]
        self.assertAlmostEqual(float(c.hucre_kutlesi(0, 0, g)[0]), exact, places=10)

    def test_kenar_kose(self):
        # Sonsuz düzlemin dört çeyreği simetrik.
        g = np.array([[0, 1e8, 0, 1e8], [-1e8, 0, 0, 1e8], [0, 1e8, -1e8, 0], [-1e8, 0, -1e8, 0]])
        np.testing.assert_allclose(c.hucre_kutlesi(0, 0, g), .25, atol=1e-8)

    def test_fig4_yari_kutle(self):
        self.assertAlmostEqual(float(c.radyal_kutle(c.D*np.sqrt(3))), .5, places=14)
        self.assertAlmostEqual(float(c.radyal_kutle(2)), .5180812502278441, places=12)

    def test_omori_integrali(self):
        self.assertAlmostEqual(float(c.omori_kutle(0, 1, c.C, c.P)), quad(lambda t:(t+c.C)**(-c.P), 0, 1)[0], places=10)

    def test_GR_ortalama(self):
        beta = np.log(10)
        known = quad(lambda m: c.uretkenlik(m)*beta*np.exp(-beta*(m-c.MC)), c.MC, 9)[0]/(1-np.exp(-beta*(9-c.MC)))
        self.assertAlmostEqual(c.ortalama_uretkenlik(), known, places=12)

    def test_zaman_operatoru_causal(self):
        op = c.zaman_operatoru(1, 4)
        self.assertTrue((op[np.triu_indices(4, 1)] == 0).all())
        dt = .25
        diagonal = c.ortalama_uretkenlik()/dt * quad(lambda u:(dt-u)*(u+c.C)**(-c.P), 0, dt)[0]
        self.assertAlmostEqual(op[0,0], diagonal, places=12)
        one_lag = c.ortalama_uretkenlik()/dt * dblquad(lambda t,s:(t-s+c.C)**(-c.P), 0, dt, lambda _: dt, lambda _:2*dt)[0]
        self.assertAlmostEqual(op[1,0], one_lag, places=10)

    def test_bilinen_dallanma(self):
        # Tek hücre P=1: Volterra (I-H)^-1 çözümüyle aynı cevap.
        op = c.zaman_operatoru(1, 32)
        answer = np.linalg.solve(np.eye(32)-op, np.ones(32)/32).sum()
        coeff = c.zaman_katsayilari([], [], 1, 32, 50)
        self.assertAlmostEqual(float(coeff.sum()), float(answer), places=12)
        self.assertGreater(answer, 1)

    def test_dogrudan_sabit_gecmis(self):
        coeff = c.zaman_katsayilari([2], [5], 1, 16, 0)
        self.assertAlmostEqual(coeff[0,0], float(c.uretkenlik(5)*c.omori_kutle(2,3,c.C,c.P)), places=12)
        self.assertEqual(coeff[0,1], 1)

    def test_gecersiz_cekirdek(self):
        with self.assertRaises(ValueError):
            c.hucre_kutlesi(0,0,np.array([[1,0,0,1]]))
        with self.assertRaises(ValueError):
            c.zaman_katsayilari([-1],[4],1)


class ArayuzTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = pd.DataFrame([[12,12.1,42,42.1], [12.1,12.2,42,42.1]], columns=IZGARA)
        cls.cat = pd.DataFrame(dict(zaman=pd.date_range('2006-01-01', periods=12, freq='90D', tz='UTC'),
                                    enlem=np.linspace(42.02,42.08,12), boylam=np.linspace(12.02,12.18,12),
                                    derinlik=np.full(12,5), mw=np.full(12,2.5)))
        cls.lm = ETASLM(cls.cat, cls.grid, adim=16, nesil=10)
        cls.a = pd.Timestamp('2011-01-01', tz='UTC')
        cls.z = cls.a+pd.Timedelta(days=1)
        cls.edges = np.array([3.95,4.95,np.inf])

    def test_arka_plan_yakinsadi(self):
        bg = self.lm.metadata['arka_plan']
        self.assertLess(bg['son_fark'],1e-6)
        self.assertLessEqual(bg['maske_mu_yil'],bg['mu_yil'])

    def test_arka_plan_gelecek_reddi(self):
        k = self.cat.copy()
        k.loc[0,'zaman'] = self.a
        with self.assertRaises(ValueError):
            kur(k,self.grid)

    def test_bilinen_bos_gecmis(self):
        f = self.lm.beklenen(self.a,self.z,self.cat.iloc[:0],self.grid,self.edges)
        coeff = c.zaman_katsayilari([],[],1,16,10)[:,0]
        power = self.lm.background.copy()
        exact = coeff[0]*power
        for i in range(1,len(coeff)):
            power = self.lm.gecis(power)
            exact += coeff[i]*power
        mag = 10**(-(self.edges[:-1]-c.MC))-10**(-(self.edges[1:]-c.MC))
        np.testing.assert_allclose(f,exact[:,None]*mag,rtol=1e-12)
        self.assertGreater(f.sum(),self.lm.background.sum()*mag.sum())

    def test_mekan_altstokastik(self):
        for i in range(2):
            unit=np.eye(2)[i]
            self.assertLessEqual(self.lm.gecis(unit).sum(),1+1e-12)

    def test_gelecek_gecmis_ve_kesim(self):
        for date in ['2011-01-01','2016-01-01','2021-01-01']:
            fake = self.cat.copy()
            fake.loc[0,'zaman']=pd.Timestamp(date,tz='UTC')
            with self.assertRaises(ValueError):
                self.lm.beklenen(self.a,self.z,fake,self.grid,self.edges)
        with self.assertRaises(ValueError):
            self.lm.beklenen(pd.Timestamp('2015-12-31',tz='UTC'),pd.Timestamp('2016-01-02',tz='UTC'),self.cat,self.grid,self.edges)

    def test_grid_ve_esik(self):
        with self.assertRaises(ValueError):
            self.lm.beklenen(self.a,self.z,self.cat,self.grid.iloc[:1],self.edges)
        with self.assertRaises(ValueError):
            self.lm.beklenen(self.a,self.z,self.cat,self.grid,np.array([2.,np.inf]))

    def test_onbellek_kuculme(self):
        a=self.lm.beklenen(self.a,self.z,self.cat.iloc[:2],self.grid,self.edges)
        self.lm.beklenen(self.a,self.z,self.cat,self.grid,self.edges)
        b=self.lm.beklenen(self.a,self.z,self.cat.iloc[:2],self.grid,self.edges)
        np.testing.assert_array_equal(a,b)


class SkorTest(unittest.TestCase):
    def test_bilinen_IG_ve_alt_esik(self):
        grid = pd.DataFrame([[12,12.1,42,42.1]],columns=IZGARA)
        edges=np.array([3.95,4.95,np.inf])
        cat=pd.DataFrame(dict(zaman=pd.to_datetime(['2011-01-01T01:00Z','2011-01-01T02:00Z','2011-01-02T02:00Z'],utc=True),
                              enlem=[42.05]*3,boylam=[12.05]*3,derinlik=[5]*3,mw=[5,5,4]))
        def f(a,z,h,g,m):
            return np.array([[1.,2.]])*float((z-a)/pd.Timedelta(days=1))
        def twice(a,z,h,g,m):
            return 2*f(a,z,h,g,m)
        runs=kos([Model('base',f),Model('twice',twice)],'2011-01-01T00:00Z','2011-01-03T00:00Z',cat,grid,edges)
        p=karsilastir(runs['twice'],runs['base'])
        self.assertAlmostEqual(p['IG'],np.log(2)-2,places=12)
        b=esik_kosu(runs['base'],grid,edges,4.95)
        t=esik_kosu(runs['twice'],grid,edges,4.95)
        self.assertEqual(len(b.olaylar),2)
        self.assertAlmostEqual(b.logL,2*np.log(2)-4-np.log(2),places=12)
        self.assertAlmostEqual(karsilastir(t,b)['IG'],np.log(2)-2,places=12)
        self.assertEqual(b.tutarlilik(tekrar=10)['N']['N'],2)


if __name__ == '__main__':
    unittest.main()
