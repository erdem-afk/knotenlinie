"""Tam dikdörtgen limiti, delik ve değişken Mc'nin elle çift toplamı."""
import unittest
import numpy as np
from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.maske import MaskeIntegrali
from knotenlinie.etas_uzun.mle import Olabilirlik, b_ayarla
from tests.etas_uzun.test_etas_uzun_mle import izgara
from knotenlinie.ortak_zemin.arayuz import omori_kutle


class TestMaskeLimit(unittest.TestCase):
    def test_gr_gercek_cozunurluk_ve_degisen_mc(self):
        # HORUS 0.01: sessiz 0.1 düzeltmesi b'yi düşürmemeli.
        mc=np.tile([3.1,3.1,2.5,2.5],3)
        excess=np.tile([.01,.12,.23,.45],3)
        fit=b_ayarla(mc+excess,mc)
        self.assertEqual(fit['dm'],.01)
        self.assertAlmostEqual(fit['deger'],np.log10(np.e)/(excess.mean()+.005),places=12)
        with self.assertRaisesRegex(ValueError,'Mc'):b_ayarla([2.9],[3.1])

    def test_delik_dis_ve_kenardaki_ebeveyn(self):
        box=(40.,40.3,12.,12.3);grid=izgara(box)
        grid=grid.drop(4).reset_index(drop=True)
        met=M.yerel_metrik(box)
        x=np.array([12.15,12.35,12.,12.05]);y=np.array([40.15,40.15,40.,40.05]);D=np.array([1.4]*4)
        mask=MaskeIntegrali(x,y,grid,met)
        all_cells=M.mekan_hucre_integralleri(x,y,D,1.8,box,metrik=met,blok=1)
        truth=all_cells.sum(axis=(1,2))-all_cells[:,1,1]
        np.testing.assert_allclose(mask.deger(D,1.8),truth,atol=3e-12)
        full=MaskeIntegrali(x,y,izgara(box),met)
        rect=M.mekan_kutu_integrali(x,y,D,1.8,box,metrik=met)
        np.testing.assert_allclose(full.deger(D,1.8),rect,atol=3e-12)

    def test_elle_mc_hedef_ve_ebeveyn_sum(self):
        box=(40.,40.2,12.,12.2);grid=izgara(box)
        t=np.array([.2,.3,1.1]);m=np.array([3.1,3.5,2.5]);x=np.array([12.05,12.06,12.07]);y=np.full(3,40.05)
        th=dict(mu=.3,K=.02,c=.04,alpha=.5,p=1.3,D=1.2,q=1.6,gamma=.1)
        L=Olabilirlik(t,m,x,y,1.,2.,1.,grid,box)
        xk,yk=L.met.km(x,y);D=M.mekan_olcegi(th['D'],th['gamma'],m,2.5)
        area=.04*L.met.jakobiyen
        ll=0.
        for i in range(3):
            intensity=th['mu']/area
            for j in range(i):
                r2=(xk[i]-xk[j])**2+(yk[i]-yk[j])**2
                intensity+=th['K']*10**(th['alpha']*(m[j]-2.5))*(t[i]-t[j]+th['c'])**(-th['p'])*(th['q']-1)/(np.pi*D[j]**2)*(1+r2/D[j]**2)**(-th['q'])
            ll+=np.log(intensity*10**(-(.6 if t[i]<1 else 0.)))
        ll-=th['mu']*(1+10**(-.6))
        G=M.mekan_kutu_integrali(x,y,D,th['q'],box,metrik=L.met)
        for j in range(3):
            I=omori_kutle(max(1-t[j],0),2-t[j],th['c'],th['p'])
            if t[j]<1:I+=10**(-.6)*omori_kutle(0,1-t[j],th['c'],th['p'])
            ll-=th['K']*10**(th['alpha']*(m[j]-2.5))*I*G[j]
        self.assertAlmostEqual(L.deger(th),ll,places=11)

if __name__=='__main__':unittest.main()
