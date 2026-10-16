"""Bilinen cevaplı olabilirlik/IG/kaskad ve sentetik MLE geri kazanımı."""
import unittest
import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.mle import Olabilirlik,ayarla,donustur,coz
from knotenlinie.etas_mc25.tamlik import tani
from knotenlinie.ortak_zemin.ayar import dallanma
from knotenlinie.karsilastir.puan import eslestirilmis,holm
from knotenlinie.kaskad.cekirdek import zaman_katsayilari


def benzet(th,b,T,kutu,seed=20261005):
    """Dışarıda doğan kız ölür; maskelenmiş eski simülatör kullanılmaz."""
    rng=np.random.default_rng(seed); met=M.yerel_metrik(kutu)
    x0,x1,y0,y1=met.kutu_km()
    nb=rng.poisson(th['mu']*T)
    t=list(rng.uniform(0,T,nb));m=list(2.5+rng.exponential(1/(b*M.LN10),nb))
    x=list(rng.uniform(x0,x1,nb));y=list(rng.uniform(y0,y1,nb))
    for i in range(20000):
        if i>=len(t):break
        ni=th['K']*10**(th['alpha']*(m[i]-2.5))*th['c']**(1-th['p'])/(th['p']-1)
        k=rng.poisson(ni)
        tt=t[i]+th['c']*(rng.random(k)**(-1/(th['p']-1))-1)
        mm=2.5+rng.exponential(1/(b*M.LN10),k)
        Di=th['D']*10**(th['gamma']*(m[i]-2.5))
        r=Di*np.sqrt((1-rng.random(k))**(-1/(th['q']-1))-1)
        a=rng.uniform(0,2*np.pi,k);xx=x[i]+r*np.cos(a);yy=y[i]+r*np.sin(a)
        keep=(tt<T)&(xx>=x0)&(xx<x1)&(yy>=y0)&(yy<y1)
        t.extend(tt[keep]);m.extend(mm[keep]);x.extend(xx[keep]);y.extend(yy[keep])
    else:raise ValueError('Sentetik katalog bütçesi')
    order=np.argsort(t);lon,lat=met.derece(np.array(x)[order],np.array(y)[order])
    return np.array(t)[order],np.array(m)[order],lon,lat


class TestMc25(unittest.TestCase):
    def setUp(self):
        self.th=dict(mu=.25,K=.012,c=.03,alpha=.45,p=1.3,D=1.4,q=1.8,gamma=.2)
        self.box=(40.,42.,12.,14.)
        self.t=np.array([.2,.2,.3,1.,2.])
        self.m=np.array([2.5,3.,3.4,2.7,3.1])
        self.x=np.array([13.,13.02,13.01,12.99,13.04]);self.y=np.array([41.,41.,41.01,41.02,41.])
        self.L=Olabilirlik(self.t,self.m,self.x,self.y,2.5,1.,3.,self.box)

    def test_mevcut_olabilirlik_ve_es_zaman(self):
        ref=M.logL_uzay_zaman(np.array([self.th[k] for k in M.UZAY_ADLARI]),self.t,self.m,self.x,self.y,2.5,M.LN10,0,3.,self.box)
        self.assertAlmostEqual(self.L.deger(self.th),ref,places=10)
        self.assertEqual(len(self.L.i),9)

    def test_natural_gradient(self):
        v=np.array([self.th[k] for k in M.UZAY_ADLARI])
        numeric=approx_derivative(lambda z:self.L.deger(dict(zip(M.UZAY_ADLARI,z))),v,method='3-point')
        _,g=self.L.deger(self.th,True)
        np.testing.assert_allclose(g,numeric.ravel(),rtol=2e-5,atol=1e-5)

    def test_transformed_gradient_iki_cekirdek(self):
        for tur in ('ortak','lm'):
            v=donustur(self.th,1.,tur)
            f,g=self.L.objectif(v,tur)
            numeric=approx_derivative(lambda z:self.L.objectif(z,tur)[0],v,method='3-point')
            np.testing.assert_allclose(g,numeric.ravel(),rtol=2e-5,atol=1e-6)
            self.assertLess(dallanma(coz(v,1.,tur),1.),1.)

    def test_poisson_integral(self):
        th=dict(self.th,K=0.)
        area=(self.box[1]-self.box[0])*(self.box[3]-self.box[2])*self.L.met.jakobiyen
        expected=len(self.t)*np.log(th['mu']/area)-th['mu']*3
        self.assertAlmostEqual(self.L.deger(th),expected,places=12)

    def test_ig_integral_ve_holm(self):
        p=eslestirilmis(np.array([2.,4.,8.]),np.array([1.,2.,4.]),14.,7.)
        self.assertAlmostEqual(p['IG'],np.log(2)-7/3)
        self.assertAlmostEqual(p['SE'],0.,places=14)
        np.testing.assert_allclose(holm([.01,.04,.03,.8]),[.04,.09,.09,.8])

    def test_kaskadsiz_tek_ebeveyn(self):
        from knotenlinie.ortak_zemin.arayuz import omori_kutle
        th=self.th
        z=zaman_katsayilari(np.array([.1]),np.array([3.]),1.,th,1.,2.5,32,0)
        self.assertAlmostEqual(z[0,0],th['K']*10**(th['alpha']*.5)*float(omori_kutle(.1,1.1,th['c'],th['p'])),places=12)
        self.assertAlmostEqual(z[0,1],1.)
        many=zaman_katsayilari(np.array([.1]),np.array([3.]),1.,th,1.,2.5,32,10)
        self.assertGreater(many.sum(),z.sum())

    def test_skor_arayuzu_ve_sig_gecmis(self):
        from knotenlinie.etas_mc25.arayuz import SigGecmis
        from knotenlinie.ortak_zemin.arayuz import DuzETAS,omori_kutle
        from knotenlinie.kaskad.arayuz import KaskadETAS
        from knotenlinie.karsilastir.kosucu import Model,kos,karsilastir
        box=(40.,40.1,12.,12.2)
        grid=pd.DataFrame([[12.,12.1,40.,40.1],[12.1,12.2,40.,40.1]],
                          columns=['boylam_min','boylam_max','enlem_min','enlem_max'])
        p=dict(parametreler=self.th,mc=2.5,b={'deger':1.},kutu=box,
               normalizasyon=M.NORMALIZASYON,metrik=M.yerel_metrik(box).kayit(),
               baslangic_yili=2005,ayar_baslangic='2005-01-01T00:00:00Z',ayar_bitis='2011-01-01T00:00:00Z',
               arka_plan=dict(x_kenar=[12.,12.2],y_kenar=[40.,40.1],yogunluk=[[50.]]))
        base=DuzETAS(p,grid)
        a=pd.Timestamp('2011-01-01',tz='UTC');z=a+pd.Timedelta(days=1)
        cat=pd.DataFrame(dict(zaman=[a-pd.Timedelta(days=1),a-pd.Timedelta(days=.5),a+pd.Timedelta(hours=12)],
                             boylam=[12.05]*3,enlem=[40.05]*3,derinlik=[29.9,30.,10.],mw=[3.,6.,4.]))
        settings=dict(sinir=(12.,12.2,40.,40.1),baslangic_yil=2005,derinlik_max=30)
        wrap=SigGecmis(base,cat,settings)
        edges=np.array([3.95,np.inf])
        val=wrap.beklenen(a,z,cat.iloc[:0],grid,edges)
        h=cat.iloc[:1]
        weight=self.th['K']*10**(self.th['alpha']*.5)*float(omori_kutle(1.,2.,self.th['c'],self.th['p']))
        spatial=base._mekan(h,grid.to_numpy(float))[0]
        truth=(self.th['mu']*np.array([.5,.5])+weight*spatial)*10**(-1.45)
        np.testing.assert_allclose(val[:,0],truth,rtol=1e-9,atol=1e-12)
        cascade=KaskadETAS(base,adim=32,nesil=10)
        runs=kos([Model('direct',wrap.beklenen,True,settings),
                  Model('cascade',SigGecmis(cascade,cat,settings).beklenen,True,settings)],
                 a,z,cat,grid,edges,bolge='italya',derinlik=(0,30))
        pair=karsilastir(runs['cascade'],runs['direct'])
        self.assertEqual(pair['N'],1)
        self.assertAlmostEqual(pair['IG'],runs['cascade'].logL-runs['direct'].logL,places=12)
        self.assertGreater(runs['cascade'].beklenen.sum(),runs['direct'].beklenen.sum())
        with self.assertRaisesRegex(ValueError,'geleceği'):base.beklenen(a,z,cat,grid,edges)
        illegal=cat.copy();illegal.loc[0,'zaman']=pd.Timestamp('2016-01-01',tz='UTC')
        with self.assertRaisesRegex(ValueError,'2016'):SigGecmis(base,illegal,settings)

    def test_future_completeness_rejected(self):
        c=pd.DataFrame(dict(zaman=pd.to_datetime(['2011-01-01'],utc=True),mw=[3.]))
        with self.assertRaisesRegex(ValueError,'≤2010'):tani(c)

    def test_synthetic_recovery(self):
        b=1.; T=4500.
        for tur,gamma in [('ortak',.25),('lm',0.)]:
            truth=dict(mu=.28,c=.03,alpha=.5,p=1.35,D=1.5,q=1.8,gamma=gamma)
            truth['K']=.65*(truth['p']-1)*truth['c']**(truth['p']-1)*(b-truth['alpha'])/b
            t,m,x,y=benzet(truth,b,T,self.box)
            L=Olabilirlik(t,m,x,y,2.5,b,T,self.box)
            fit=ayarla(L,tur)
            th=fit['parametreler']
            print('SENTETIK',tur,'N',len(t),'gercek',truth,'mle',th,'n',fit['dallanma'],flush=True)
            self.assertLess(abs(th['mu']/truth['mu']-1),.3)
            self.assertLess(abs(fit['dallanma']-.65),.15)
            self.assertLess(abs(th['alpha']-.5),.2)
            self.assertLess(abs(th['p']-1.35),.2)
            self.assertLess(abs(th['q']-1.8),.65)
            self.assertLess(abs(th['gamma']-gamma),.2)
            for key in ('K','c','D'):
                self.assertLess(abs(np.log(th[key]/truth[key])),np.log(3))
            self.assertGreaterEqual(fit['logL']+1e-7,L.deger(truth))

if __name__=='__main__':unittest.main()
