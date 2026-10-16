"""Geometrik ölçek, dönem kapıları ve analitik kaskadsız gün integrali."""
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.olcek import (geometrik_olcek, dis_maskeleri, olcek_hesapla, kde_sec,
                                  kur, model_kur, Olcekli, AYAR_SON, OLCEK_SON)
from knotenlinie.etas_uzun.arayuz import TamGecmis, ebeveynler
from knotenlinie.ortak_zemin.arayuz import omori_kutle
from knotenlinie.ortak_zemin.veri import IZGARA
from knotenlinie.karsilastir.kosucu import Kosu


class TestOlcek(unittest.TestCase):
    def test_geometrik_bilinen(self):
        result = geometrik_olcek(100,200.,20,10.)
        self.assertEqual(result['tum']['c'],.5)
        self.assertEqual(result['LAquila_dis']['c'],2.)
        self.assertEqual(result['c'],1.)
        for args in ((0,10,1,2),(5,0,2,1),(5,10,0,2),(5,10,2,np.inf),(5,10,6,2),(5,10,2,11)):
            with self.assertRaises(ValueError): geometrik_olcek(*args)

    def test_dis_kapali_uc_ve_hizalama(self):
        grid = pd.DataFrame([[12.9,13.,42.,42.1],[13.,13.1,42.,42.1],[13.7,13.8,42.5,42.6],[13.8,13.9,42.,42.1]],columns=IZGARA)
        events = pd.DataFrame(dict(boylam=[12.99,13.,13.8,13.81,13.5],enlem=[42.,42.,42.6,42.,42.61]))
        ev, cells = dis_maskeleri(events,grid)
        np.testing.assert_array_equal(ev,[True,False,False,True,True])
        np.testing.assert_array_equal(cells,[True,False,False,True])
        bad = grid.copy(); bad.loc[1,'boylam_min'] = 12.95
        with self.assertRaisesRegex(ValueError,'hizalı'): dis_maskeleri(events,bad)

    def test_olcek_yalniz_gecmiste(self):
        grid = pd.DataFrame([[13.,13.1,42.,42.1],[14.,14.1,42.,42.1]],columns=IZGARA)
        ev = pd.DataFrame(dict(zaman=pd.to_datetime(['2009-04-06','2010-01-01'],utc=True),
                               boylam=[13.05,14.05],enlem=[42.05]*2,mw=[4.,4.]))
        run = Kosu('s',np.array([[3.],[1.]]),np.ones((2,1),int),np.ones(2),-4.,ev,(AYAR_SON,OLCEK_SON,(0,30),'grid','italya'))
        self.assertAlmostEqual(olcek_hesapla(run,grid)['c'],np.sqrt(.5))
        run.cerceve = ('2011-01-01T00:00:00Z','2016-01-01T00:00:00Z',(0,30),'grid','italya')
        with self.assertRaisesRegex(ValueError,'2006'): olcek_hesapla(run,grid)

    def test_kde_ic_bolme(self):
        grid = pd.DataFrame([[12.,12.1,40.,40.1]],columns=IZGARA)
        d = pd.DataFrame(dict(zaman=pd.to_datetime(['2000-12-31','2001-01-01','2005-12-31'],utc=True),boylam=[12.05]*3,enlem=[40.05]*3))
        seen = []
        def fake(data,g,box,h,eps):
            seen.append(list(data.zaman.dt.year))
            return dict(value=h+eps)
        with patch('knotenlinie.etas_uzun.olcek.maskeli_hist',side_effect=fake), \
             patch('knotenlinie.etas_uzun.olcek.M.arka_plan_degeri',side_effect=lambda x,y,h:np.full(len(x),h['value'])):
            hist = kde_sec(d,grid,(40.,40.1,12.,12.1))
        self.assertTrue(all(v == [2000] for v in seen[:-1]))
        self.assertEqual(seen[-1],[2000,2001,2005])
        self.assertEqual(hist['secim']['secim_n'],2)
        bad = d.copy(); bad.loc[0,'zaman'] = pd.Timestamp('2006-01-01',tz='UTC')
        with self.assertRaisesRegex(ValueError,'2006'): kde_sec(bad,grid,(40.,40.1,12.,12.1))
        with self.assertRaisesRegex(ValueError,'2006'): kur(bad,grid)

    def test_dogrudan_integral_ve_yuzey_olcegi(self):
        grid = pd.DataFrame([[12.,12.1,40.,40.1]],columns=IZGARA)
        box = (40.,40.1,12.,12.2)
        th = dict(mu=.25,K=.012,c=.03,alpha=.45,p=1.3,D=1.4,q=1.8,gamma=.2)
        p = dict(parametreler=th,mc=2.5,b={'deger':1.},kutu=box,normalizasyon=M.NORMALIZASYON,
                 metrik=M.yerel_metrik(box).kayit(),baslangic_yili=1985,ayar_baslangic='1985-01-01T00:00:00Z',
                 ayar_bitis=AYAR_SON,arka_plan=dict(x_kenar=[12.,12.1,12.2],y_kenar=[40.,40.1],yogunluk=[[100.],[0.]]))
        cat = pd.DataFrame(dict(zaman=pd.to_datetime(['2004-01-01','2004-01-02','2005-12-31','2006-01-01T12:00:00'],utc=True,format='mixed'),
                                boylam=[12.05,12.05,12.15,12.05],enlem=[40.05]*4,derinlik=[10.]*4,mw=[2.9,3.2,3.,4.]))
        a = pd.Timestamp(AYAR_SON); z = a+pd.Timedelta(days=1)
        direct = model_kur(p,grid,False); cascade = model_kur(p,grid,True)
        wrapper = TamGecmis(direct,cat)
        edges = [3.95,4.95,np.inf]
        h = ebeveynler(cat,box,a)
        self.assertEqual(len(h),2)  # Mc(t); dış anne dahil, gün içi hariç
        age = ((a-h.zaman)/pd.Timedelta(days=1)).to_numpy()
        weight = th['K']*10**(th['alpha']*(h.mw.to_numpy()-2.5))*omori_kutle(age,age+1,th['c'],th['p'])
        mag = 10**(-(np.array(edges[:-1])-2.5))-10**(-(np.array(edges[1:])-2.5))
        truth = (th['mu']+np.dot(weight,direct.taban._mekan(h,grid.to_numpy(float))[:,0]))*mag
        value = wrapper.beklenen(a,z,cat.iloc[:0],grid,edges)
        np.testing.assert_allclose(value[0],truth,rtol=1e-12)
        np.testing.assert_allclose(Olcekli(wrapper,.7).beklenen(a,z,cat.iloc[:0],grid,edges),.7*value,rtol=1e-12)
        self.assertGreater(cascade.beklenen(a,z,h,grid,edges).sum(),value.sum())
        self.assertEqual(direct.taban.th,th)
        with self.assertRaises(ValueError): Olcekli(wrapper,0)
        with self.assertRaisesRegex(ValueError,'gün başından'): direct.beklenen(a,z,cat,grid,edges)


if __name__ == '__main__': unittest.main()
