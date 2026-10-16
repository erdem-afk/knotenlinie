"""Bilinen gün-integrali, eski Mc ve dış ebeveyn; IG/Holm zinciri."""
import unittest
import numpy as np
import pandas as pd
from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.arayuz import UzunETAS, TamGecmis, ebeveynler
from knotenlinie.ortak_zemin.arayuz import omori_kutle
from knotenlinie.ortak_zemin.veri import IZGARA
from knotenlinie.karsilastir.puan import eslestirilmis, holm
from knotenlinie.karsilastir.kosucu import Model, kos, karsilastir


class TestUzunArayuz(unittest.TestCase):
    def setUp(self):
        self.grid=pd.DataFrame([[12.,12.1,40.,40.1]],columns=IZGARA)
        self.box=(40.,40.1,12.,12.2)
        self.th=dict(mu=.25,K=.012,c=.03,alpha=.45,p=1.3,D=1.4,q=1.8,gamma=.2)
        self.p=dict(parametreler=self.th,mc=2.5,b={'deger':1.},kutu=self.box,
                    normalizasyon=M.NORMALIZASYON,metrik=M.yerel_metrik(self.box).kayit(),
                    baslangic_yili=1985,ayar_baslangic='1985-01-01T00:00:00Z',ayar_bitis='2011-01-01T00:00:00Z',
                    arka_plan=dict(x_kenar=[12.,12.1,12.2],y_kenar=[40.,40.1],yogunluk=[[100.],[0.]]))
        self.a=pd.Timestamp('2011-01-01',tz='UTC');self.z=self.a+pd.Timedelta(days=1)
        self.cat=pd.DataFrame(dict(zaman=pd.to_datetime(['2004-01-01','2004-01-02','2010-12-31','2010-12-31T12:00:00','2011-01-01T12:00:00'],utc=True,format='mixed'),
                                  boylam=[12.05,12.05,12.15,12.05,12.05],enlem=[40.05]*5,derinlik=[10.,10.,10.,30.,10.],mw=[2.9,3.2,3.,6.,4.]))

    def test_old_mc_depth_outside_mask(self):
        h=ebeveynler(self.cat,self.box,self.a)
        self.assertEqual(len(h),2);self.assertEqual(h.iloc[-1].boylam,12.15)
        model=UzunETAS(self.p,self.grid,nesil=0)
        value=TamGecmis(model,self.cat).beklenen(self.a,self.z,self.cat.iloc[:0],self.grid,[3.95,np.inf])
        age=((self.a-h.zaman)/pd.Timedelta(days=1)).to_numpy()
        weights=self.th['K']*10**(self.th['alpha']*(h.mw.to_numpy()-2.5))*omori_kutle(age,age+1,self.th['c'],self.th['p'])
        truth=(self.th['mu']+np.dot(weights,model.taban._mekan(h,self.grid.to_numpy(float))[:,0]))*10**(-1.45)
        self.assertAlmostEqual(value[0,0],truth,places=12)
        model.model.nesil=10
        self.assertGreater(model.beklenen(self.a,self.z,h,self.grid,[3.95,np.inf]).sum(),value.sum())

    def test_poisson_cascade_and_ig(self):
        p=dict(self.p,parametreler=dict(self.th,K=0.))
        model=UzunETAS(p,self.grid)
        val=model.beklenen(self.a,self.z,self.cat.iloc[:0],self.grid,[3.95,np.inf])
        self.assertAlmostEqual(val.sum(),self.th['mu']*10**(-1.45),places=12)
        settings=dict(sinir=(12.,12.2,40.,40.1),baslangic_yil=1985,derinlik_max=30)
        direct=UzunETAS(self.p,self.grid,nesil=0);cascade=UzunETAS(self.p,self.grid)
        runs=kos([Model('d',TamGecmis(direct,self.cat).beklenen,True,settings),Model('k',TamGecmis(cascade,self.cat).beklenen,True,settings)],self.a,self.z,self.cat,self.grid,[3.95,np.inf],bolge='italya',derinlik=(0,30))
        pair=karsilastir(runs['k'],runs['d'])
        self.assertEqual(pair['N'],1)
        self.assertAlmostEqual(pair['IG'],runs['k'].logL-runs['d'].logL,places=12)
        answer=eslestirilmis(np.array([2.,4.,8.]),np.array([1.,2.,4.]),14.,7.)
        self.assertAlmostEqual(answer['IG'],np.log(2)-7/3)
        np.testing.assert_allclose(holm([.01,.04]),[.02,.04])

    def test_future_and_in_day_rejected(self):
        model=UzunETAS(self.p,self.grid)
        with self.assertRaisesRegex(ValueError,'gün başından'):model.beklenen(self.a,self.z,self.cat,self.grid,[3.95,np.inf])
        bad=self.cat.copy();bad.loc[0,'zaman']=pd.Timestamp('2016-01-01',tz='UTC')
        with self.assertRaisesRegex(ValueError,'2015'):TamGecmis(model,bad)

if __name__=='__main__':unittest.main()
