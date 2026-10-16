"""Maskeli Mc(t) MLE: analitik cevap, gradyan, sentetik geri kazanım."""
import unittest
import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from knotenlinie.etas import model as M
from knotenlinie.etas_uzun.maske import MaskeIntegrali, maskeli_hist
from knotenlinie.etas_uzun.mle import Olabilirlik, ayarla, donustur, tamlik
from knotenlinie.ortak_zemin.arayuz import omori_kutle
from knotenlinie.ortak_zemin.veri import IZGARA, hucre_indeks
from knotenlinie.ortak_zemin.ayar import dallanma


def izgara(box, eksik=False):
    la0,la1,lo0,lo1=box
    rows=[]
    for x in np.arange(lo0,lo1-1e-8,.1):
        for y in np.arange(la0,la1-1e-8,.1):
            if eksik and x>lo0+.149 and y>la0+.149: continue
            rows.append([x,x+.1,y,y+.1])
    return pd.DataFrame(rows,columns=IZGARA)


def benzet(th,b,T,change,grid,box,seed):
    """Gözlenen-ebeveyn süreci; dönem GR thinning ve maskede kızlar."""
    rng=np.random.default_rng(seed);met=M.yerel_metrik(box)
    tt=[];mm=[];xx=[];yy=[];cells=grid.to_numpy(float)
    for lo,hi,mc in ((0,change,3.1),(change,T,2.5)):
        n=rng.poisson(th['mu']*(hi-lo)*10**(-b*(mc-2.5)))
        cell=cells[rng.integers(0,len(cells),n)]
        lon=rng.uniform(cell[:,0],cell[:,1]);lat=rng.uniform(cell[:,2],cell[:,3]);x,y=met.km(lon,lat)
        tt.extend(rng.uniform(lo,hi,n));mm.extend(mc+rng.exponential(1/(b*M.LN10),n));xx.extend(x);yy.extend(y)
    for i in range(30000):
        if i>=len(tt):break
        n=rng.poisson(th['K']*10**(th['alpha']*(mm[i]-2.5))*th['c']**(1-th['p'])/(th['p']-1))
        t=tt[i]+th['c']*(rng.random(n)**(-1/(th['p']-1))-1)
        m=2.5+rng.exponential(1/(b*M.LN10),n)
        Di=th['D']*10**(th['gamma']*(mm[i]-2.5))
        r=Di*np.sqrt((1-rng.random(n))**(-1/(th['q']-1))-1);a=rng.uniform(0,2*np.pi,n)
        x=xx[i]+r*np.cos(a);y=yy[i]+r*np.sin(a);lon,lat=met.derece(x,y)
        inside=hucre_indeks(pd.DataFrame(dict(boylam=lon,enlem=lat)),grid)>=0
        keep=(t<T)&(m>=tamlik(t,change))&inside
        tt.extend(t[keep]);mm.extend(m[keep]);xx.extend(x[keep]);yy.extend(y[keep])
    else:raise ValueError('Sentetik bütçe')
    order=np.argsort(tt);lon,lat=met.derece(np.asarray(xx)[order],np.asarray(yy)[order])
    return np.asarray(tt)[order],np.asarray(mm)[order],lon,lat


class TestUzunMLE(unittest.TestCase):
    def setUp(self):
        self.box=(40.,40.2,12.,12.2)
        self.grid=izgara(self.box).iloc[:3].reset_index(drop=True)
        self.th=dict(mu=.25,K=.012,c=.03,alpha=.45,p=1.3,D=1.4,q=1.8,gamma=.2)
        self.t=np.array([.2,.2,.3,1.2,2.]);self.m=np.array([3.1,3.3,3.4,2.7,3.1])
        self.x=np.array([12.05,12.3,12.06,12.04,12.05]);self.y=np.full(5,40.05)
        self.L=Olabilirlik(self.t,self.m,self.x,self.y,1.,3.,1.,self.grid,self.box)

    def test_poisson_mask_and_mc(self):
        th=dict(self.th,K=0.)
        area=.03*self.L.met.jakobiyen
        truth=np.log(th['mu']/area*self.L.s).sum()-th['mu']*(10**(-.6)+2.)
        self.assertAlmostEqual(self.L.deger(th),truth,places=11)
        self.assertEqual(self.L.nhedef,4)
        self.assertEqual(self.L.cift,9)  # dış anne hedef değil; eş zaman nedensel değil

    def test_mask_matches_sum_cells_external_parent(self):
        mask=self.L.mask
        Di=M.mekan_olcegi(self.th['D'],self.th['gamma'],self.m,2.5)
        full=M.mekan_hucre_integralleri(self.x,self.y,Di,self.th['q'],self.box,metrik=self.L.met,blok=1)
        g=self.grid.to_numpy();ix=np.rint((g[:,0]-12)/.1).astype(int);iy=np.rint((g[:,2]-40)/.1).astype(int)
        np.testing.assert_allclose(mask.deger(Di,self.th['q']),full[:,iy,ix].sum(1),atol=2e-12)
        self.assertGreater(mask.deger(Di,self.th['q'])[1],0.)

    def test_integral_crosses_mc_boundary(self):
        I,_,_=self.L.zaman(self.th['c'],self.th['p'])
        t=self.t[0];c=self.th['c'];p=self.th['p']
        truth=10**(-.6)*omori_kutle(0,1-t,c,p)+omori_kutle(1-t,3-t,c,p)
        self.assertAlmostEqual(I[0],truth,places=12)

    def test_natural_and_transformed_gradient(self):
        v=np.array([self.th[k] for k in M.UZAY_ADLARI])
        num=approx_derivative(lambda z:self.L.deger(dict(zip(M.UZAY_ADLARI,z))),v,method='3-point')
        np.testing.assert_allclose(self.L.deger(self.th,True)[1],num.ravel(),rtol=2e-5,atol=2e-6)
        for tur in ('ortak','lm'):
            v=donustur(self.th,1.,tur)
            num=approx_derivative(lambda z:self.L.objectif(z,tur)[0],v,method='3-point')
            np.testing.assert_allclose(self.L.objectif(v,tur)[1],num.ravel(),rtol=2e-5,atol=2e-6)

    def test_masked_background_unit_mass(self):
        d=pd.DataFrame(dict(boylam=[12.05,12.05,12.15],enlem=[40.05,40.15,40.05]))
        h=maskeli_hist(d,self.grid,self.box,10.,.02)
        density=np.asarray(h['yogunluk']);area=np.diff(h['x_kenar'])[:,None]*np.diff(h['y_kenar'])[None,:]
        self.assertAlmostEqual(float((density*area).sum()),1.,places=12)
        self.assertEqual(density[1,1],0.)

    def test_mc_gate(self):
        with self.assertRaisesRegex(ValueError,'Mc'):
            Olabilirlik(self.t,np.full(5,2.5),self.x,self.y,1.,3.,1.,self.grid,self.box)

    def test_synthetic_recovery_two_variants(self):
        box=(40.,40.4,12.,12.4);grid=izgara(box,eksik=True)
        for tur,gamma in [('ortak',.2),('lm',0.)]:
            th=dict(mu=.38,c=.03,alpha=.45,p=1.35,D=1.2,q=1.8,gamma=gamma)
            th['K']=.6*(th['p']-1)*th['c']**(th['p']-1)*(1-th['alpha'])
            t,m,x,y=benzet(th,1.,6000.,3000.,grid,box,20261005)
            L=Olabilirlik(t,m,x,y,1.,6000.,3000.,grid,box)
            fit=ayarla(L,tur,maksiter=300);hat=fit['parametreler']
            print('R SENTETIK',tur,'N',len(t),'gercek',th,'mle',hat,'n',fit['dallanma'],flush=True)
            self.assertLess(abs(hat['mu']/th['mu']-1),.25)
            self.assertLess(abs(fit['dallanma']-.6),.18)
            self.assertLess(abs(hat['alpha']-.45),.2)
            self.assertLess(abs(hat['p']-1.35),.2)
            self.assertLess(abs(hat['q']-1.8),.65)
            self.assertLess(abs(hat['gamma']-gamma),.2)
            for k in ('K','c','D'):self.assertLess(abs(np.log(hat[k]/th[k])),np.log(3))
            self.assertGreaterEqual(fit['logL']+1e-6,L.deger(th))

if __name__=='__main__':unittest.main()
