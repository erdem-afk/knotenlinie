"""Analitik dallanma, çekirdek ve günlük skor/sızıntı testleri."""
import unittest

import numpy as np
import pandas as pd
from scipy.integrate import quad, dblquad
from scipy.linalg import solve_triangular

from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin.arayuz import DuzETAS, omori_kutle
from knotenlinie.ortak_zemin.veri import IZGARA
from knotenlinie.kaskad.cekirdek import ortalama_uretkenlik, zaman_operatoru, zaman_katsayilari, mekan_kernel
from knotenlinie.kaskad.arayuz import KaskadETAS
from knotenlinie.karsilastir.kosucu import Model, kos, karsilastir
from knotenlinie.karsilastir.gunluk_j import esik_kosu


def sentetik():
    grid = pd.DataFrame([[12,12.1,42,42.1], [12.1,12.2,42,42.1]], columns=IZGARA)
    th = dict(mu=1., K=.02, c=.1, p=1.8, alpha=.4, D=2., q=1.5, gamma=.15)
    p = dict(parametreler=th, mc=3., b=dict(deger=1.), kutu=[42,42.1,12,12.2],
             ayar_baslangic='2000-01-01T00:00Z', ayar_bitis='2011-01-01T00:00Z',
             normalizasyon=M.NORMALIZASYON, metrik=M.yerel_metrik((42,42.1,12,12.2)).kayit(),
             arka_plan=dict(x_kenar=[12,12.2], y_kenar=[42,42.1], yogunluk=[[50.]]))
    return DuzETAS(p, grid)


class CekirdekTest(unittest.TestCase):
    def setUp(self):
        self.th = dict(K=.02, c=.1, p=1.8, alpha=.4, D=2., q=1.5, gamma=.15)

    def test_GR_uretkenlik_sonsuz(self):
        known = quad(lambda x: self.th['K']*np.log(10)*10**(-.6*x), 0, np.inf)[0]
        self.assertAlmostEqual(ortalama_uretkenlik(self.th, 1), known, places=12)

    def test_tek_ebeveyn_analitik_birinci_nesil(self):
        coeff = zaman_katsayilari([2], [4], 1, self.th, 1, 3, 32, 0)
        known = .02*10**.4*quad(lambda t:(t+.1)**(-1.8), 2,3)[0]
        self.assertAlmostEqual(coeff[0,0],known,places=13)
        self.assertAlmostEqual(coeff[0,1],1,places=13)

    def test_zaman_causal_ayni_kutu_ve_lag(self):
        op = zaman_operatoru(1,4,self.th,1)
        self.assertTrue((op[np.triu_indices(4,1)] == 0).all())
        k = ortalama_uretkenlik(self.th,1)
        diag = k/.25*quad(lambda u:(.25-u)*(u+.1)**(-1.8),0,.25)[0]
        lag = k/.25*dblquad(lambda t,s:(t-s+.1)**(-1.8),0,.25,lambda _: .25,lambda _: .5)[0]
        self.assertAlmostEqual(op[0,0],diag,places=12)
        self.assertAlmostEqual(op[1,0],lag,places=12)

    def test_p_iki(self):
        th = dict(self.th,p=2.)
        op = zaman_operatoru(1,4,th,1)
        known = ortalama_uretkenlik(th,1)/.25*quad(lambda u:(.25-u)*(u+.1)**(-2),0,.25)[0]
        self.assertAlmostEqual(op[0,0],known,places=12)

    def test_dallanma_volterra_ve_nesil_yakinsama(self):
        op = zaman_operatoru(1,32,self.th,1)
        answer = solve_triangular(np.eye(32)-op,np.ones(32)/32,lower=True).sum()
        coeff = zaman_katsayilari([],[],1,self.th,1,3,32,40)
        self.assertAlmostEqual(float(coeff.sum()),answer,places=12)

    def test_bilinen_1_bolu_1_eksi_n_siniri(self):
        # Tek bir Mc ebeveyn; alpha=0, p=3: sonsuz düzlem, uzun pencere.
        # Uniform background değil, t=0 impulsunun kızları. Direkt nesil n.
        n=.3
        th=dict(self.th,alpha=0,p=3.,c=1.,K=2*n)
        T=1000.
        coeff=zaman_katsayilari([0],[3],T,th,1,3,128,40)
        total=1+coeff[:,0].sum()
        self.assertLessEqual(total,1/(1-n)+1e-12)
        self.assertAlmostEqual(total,1/(1-n),places=5)

    def test_uzay_gamma_sifir_LM_analitik(self):
        from knotenlinie.etas_lm.cekirdek import hucre_kutlesi
        th=dict(self.th,gamma=0)
        kernel=mekan_kernel(3,2,8,10,th,1,uzay_dugum=6)
        nodes,w=np.polynomial.legendre.leggauss(6)
        xx,yy=np.meshgrid(np.arange(-2,3)*8,np.arange(-1,2)*10)
        rect=np.column_stack([(xx-4).ravel(),(xx+4).ravel(),(yy-5).ravel(),(yy+5).ravel()])
        known=np.zeros(len(rect))
        for i,x in enumerate(nodes):
            for j,y in enumerate(nodes):
                known+=w[i]*w[j]/4*hucre_kutlesi(x*4,y*5,rect,d=th['D'])
        np.testing.assert_allclose(kernel,known.reshape(kernel.shape),rtol=1e-10,atol=1e-12)
        self.assertLess(kernel.sum(),1)

    def test_gamma_karisimi_sayisal_integral(self):
        # Merkezi hedef, uniform kaynak: tek konumdaki dikdörtgen integrali
        # magnitude ile değişir. GR karışımını bağımsız quad ile kıyasla.
        th=dict(self.th,q=1.5)
        kernel=mekan_kernel(1,1,8,10,th,1,uzay_dugum=1,gr_dugum=64)
        from knotenlinie.etas_lm.cekirdek import hucre_kutlesi
        rect=np.array([[-4,4,-5,5]])
        known=quad(lambda x: np.exp(-x)*hucre_kutlesi(0,0,rect,d=2*np.exp(.15/.6*x))[0],0,50,epsabs=1e-11)[0]
        self.assertAlmostEqual(kernel[0,0],known,places=9)


class ArayuzTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=sentetik()
        cls.model=KaskadETAS(cls.base,adim=32,nesil=10)
        cls.g=cls.base.izgara
        cls.a=pd.Timestamp('2011-01-01',tz='UTC')
        cls.z=cls.a+pd.Timedelta(days=1)
        cls.edges=np.array([3.,4.,np.inf])
        cls.h=pd.DataFrame(dict(zaman=pd.to_datetime(['2010-12-31T00:00Z'],utc=True),
                               enlem=[42.05],boylam=[12.05],derinlik=[5.],mw=[4.]))

    def test_nesil_sifir_tabanla_ozdes(self):
        model=KaskadETAS(self.base,nesil=0)
        f=model.beklenen(self.a,self.z,self.h,self.g,self.edges)
        known=self.base.beklenen(self.a,self.z,self.h,self.g,self.edges)
        np.testing.assert_allclose(f,known,rtol=1e-13,atol=1e-14)

    def test_kaskad_artar_ve_bos_gecmis(self):
        h=self.h.iloc[:0]
        f=self.model.beklenen(self.a,self.z,h,self.g,self.edges)
        base=self.base.beklenen(self.a,self.z,h,self.g,self.edges)
        self.assertTrue((f>=base).all())
        coeff=zaman_katsayilari([],[],1,self.base.th,1,3,32,10)[:,0]
        power=self.base._arka_plan(self.g.to_numpy(float))*self.base.th['mu']
        known=coeff[0]*power
        for c in coeff[1:]:
            power=self.model.gecis(power)
            known+=c*power
        np.testing.assert_allclose(f.sum(axis=1),known,rtol=1e-12)

    def test_alt_izgara_ayni_tam_kaskad(self):
        full=self.model.beklenen(self.a,self.z,self.h,self.g,self.edges)
        small=self.model.beklenen(self.a,self.z,self.h,self.g.iloc[:1],self.edges)
        np.testing.assert_array_equal(full[:1],small)

    def test_kenar_kaybi(self):
        for unit in np.eye(2):
            self.assertLess(self.model.gecis(unit).sum(),1)

    def test_gecmis_kuculmesi(self):
        f=self.model.beklenen(self.a,self.z,self.h,self.g,self.edges)
        self.model.beklenen(self.a,self.z,self.h.iloc[:0],self.g,self.edges)
        np.testing.assert_array_equal(f,self.model.beklenen(self.a,self.z,self.h,self.g,self.edges))

    def test_muhur_ve_gecmis_reddi(self):
        h=self.h.copy()
        h.loc[0,'zaman']=self.a
        with self.assertRaises(ValueError):
            self.model.beklenen(self.a,self.z,h,self.g,self.edges)
        with self.assertRaises(ValueError):
            self.model.beklenen(pd.Timestamp('2015-12-31',tz='UTC'),pd.Timestamp('2016-01-02',tz='UTC'),self.h,self.g,self.edges)
        with self.assertRaises(ValueError):
            self.model.beklenen(self.a,self.z,self.h,self.g,np.array([2.,np.inf]))


class SkorTest(unittest.TestCase):
    def test_bilinen_IG_integral_ve_alt_esik(self):
        grid=pd.DataFrame([[12,12.1,42,42.1]],columns=IZGARA)
        edges=np.array([3.95,4.95,np.inf])
        cat=pd.DataFrame(dict(zaman=pd.to_datetime(['2011-01-01T01:00Z','2011-01-01T02:00Z','2011-01-02T02:00Z'],utc=True),
                              enlem=[42.05]*3,boylam=[12.05]*3,derinlik=[5]*3,mw=[5,5,4]))
        def base(a,z,h,g,m):
            return np.array([[1.,2.]])*float((z-a)/pd.Timedelta(days=1))
        def doubled(a,z,h,g,m):
            return 2*base(a,z,h,g,m)
        runs=kos([Model('b',base),Model('c',doubled)],'2011-01-01T00:00Z','2011-01-03T00:00Z',cat,grid,edges)
        pair=karsilastir(runs['c'],runs['b'])
        self.assertAlmostEqual(pair['IG'],np.log(2)-2,places=12)
        self.assertAlmostEqual(pair['integral_terimi'],-2,places=12)
        b=esik_kosu(runs['b'],grid,edges,4.95)
        c=esik_kosu(runs['c'],grid,edges,4.95)
        self.assertEqual(len(b.olaylar),2)
        self.assertAlmostEqual(b.logL,2*np.log(2)-4-np.log(2),places=12)
        self.assertAlmostEqual(karsilastir(c,b)['IG'],np.log(2)-2,places=12)


if __name__ == '__main__':
    unittest.main()
