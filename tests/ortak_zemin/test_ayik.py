"""K: bilinen ETAS dünyası, φ/KDE ve tam olabilirlik/gradyan."""
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from knotenlinie.etas import model as M, benzetim as B
from knotenlinie.ortak_zemin.arka_plan import kde_histogram
from knotenlinie.ortak_zemin.arka_plan_ayik import kde_ayik, uyarlamali_bant
from knotenlinie.ortak_zemin.ayar_ayik import Olabilirlik, yinele, arka_plan_sec_ayik


class AyikTest(unittest.TestCase):
    def setUp(self):
        self.kutu = (40,42,10,12)
        self.th = dict(mu=.2,K=.03,c=.03,alpha=.5,p=1.3,D=10,q=1.5,gamma=.2)
        rng = np.random.default_rng(42)
        self.lik = Olabilirlik(np.sort(rng.uniform(0,100,30)),3+rng.exponential(.4,30),
                              rng.uniform(10,12,30),rng.uniform(40,42,30),3,1,100,self.kutu)
        self.u = rng.uniform(.1,.4,30)
        self.lik.set_u(self.u)
        self.xx = M._theta_dan_x(M._dizi(self.th,M.UZAY_ADLARI),self.lik.beta)

    def test_equal_weight_fixed_band_reproduces_T(self):
        x,y = self.lik.x,self.lik.y
        a = kde_histogram(x,y,self.kutu,15,.05)
        b = kde_ayik(x,y,self.kutu,np.full(len(x),15.),np.ones(len(x)),.05)
        np.testing.assert_allclose(a['yogunluk'],b['yogunluk'],atol=1e-14)

    def test_weighted_mass_and_zero_weight_parent(self):
        x,y = np.array([10.4,11.6]),np.array([40.5,41.5])
        h = np.array([5.,25.])
        b = kde_ayik(x,y,self.kutu,h,[.2,.8],.05)
        left = kde_ayik(x[:1],y[:1],self.kutu,h[:1],[1],.05)
        right = kde_ayik(x[1:],y[1:],self.kutu,h[1:],[1],.05)
        np.testing.assert_allclose(b['yogunluk'],.2*left['yogunluk']+.8*right['yogunluk'])
        area = np.diff(b['x_kenar'])[:,None]*np.diff(b['y_kenar'])[None,:]
        self.assertAlmostEqual(float((b['yogunluk']*area).sum()),1.)
        np.testing.assert_allclose(kde_ayik(x,y,self.kutu,h,[0,1],.05)['yogunluk'],right['yogunluk'])
        self.assertGreaterEqual(b['yogunluk'].min(),.05/4)

    def test_knn_excludes_self_lower_floor_and_duplicates(self):
        met=M.yerel_metrik(self.kutu)
        x=np.array([10.5,10.5,10.5+10/met.kx]); y=np.full(3,41.)
        np.testing.assert_allclose(uyarlamali_bant(x,y,self.kutu,1,5),[5,5,10])
        np.testing.assert_allclose(uyarlamali_bant(x,y,self.kutu,2,5),[10,10,10])

    def test_likelihood_and_gradient_same_as_independent_T(self):
        value,grad = self.lik.hesapla(self.xx)
        ref = M.logL_uzay_zaman(M._dizi(self.th,M.UZAY_ADLARI),self.lik.t,self.lik.m,
            self.lik.x,self.lik.y,3,self.lik.beta,0,100,self.kutu,self.u)
        self.assertAlmostEqual(value,-ref,places=11)
        numerical = approx_derivative(lambda x:self.lik.hesapla(x)[0],self.xx).ravel()
        np.testing.assert_allclose(grad,numerical,rtol=2e-6,atol=2e-7)

    def test_default_uniform_density_uses_km_units(self):
        lik=Olabilirlik(self.lik.t,self.lik.m,self.lik.x,self.lik.y,3,1,100,self.kutu)
        value,_=lik.hesapla(self.xx)
        ref=M.logL_uzay_zaman(M._dizi(self.th,M.UZAY_ADLARI),lik.t,lik.m,
                              lik.x,lik.y,3,lik.beta,0,100,self.kutu)
        self.assertAlmostEqual(value,-ref,places=11)

    def test_phi_exact_hand_sum_and_equal_time_not_parent(self):
        lik=Olabilirlik([0,0,1],[3,3.4,3.2],[11,11.1,11.2],[41,41,41],3,1,5,self.kutu)
        u=np.array([.2,.3,.4]); lik.set_u(u)
        _,phi=lik.hesapla(self.xx,gradyan=False)
        met=M.yerel_metrik(self.kutu)
        x,y=met.km(lik.x,lik.y)
        r2=(x[2]-x[:2])**2+(y[2]-y[:2])**2
        trigger=(self.th['K']*10**(self.th['alpha']*(lik.m[:2]-3))*(1+self.th['c'])**(-self.th['p'])*
            M.mekan_cekirdegi(r2,self.th['D'],self.th['q'],self.th['gamma'],lik.m[:2],3)).sum()
        bg=self.th['mu']*u[2]/met.jakobiyen
        np.testing.assert_allclose(phi,[1,1,bg/(bg+trigger)])

    def test_gate_future_and_temporal_split_both_freezes(self):
        for end,trainyear,holdyear in [('2011-01-01',2005,2006),('2006-01-01',2000,2001)]:
            d=pd.DataFrame(dict(zaman=pd.to_datetime([f'{trainyear}-01-01',f'{trainyear}-02-01',
                f'{holdyear}-01-01',f'{holdyear}-02-01'],utc=True),mw=[3.1,3.4,3.3,3.5],
                boylam=[10.5,11.5,10.8,11.2],enlem=[40.5,41.5,40.8,41.2]))
            fake = dict(arka_plan=kde_ayik([10.5,11.5],[40.5,41.5],self.kutu,[20,20],[1,1],.05))
            seen=[]
            def fit(lik,hp,**kwargs):
                seen.append((lik.t.copy(),lik.T,lik.b))
                return dict(arka_plan=dict(fake['arka_plan'],ayiklama={'turlar':[]}))
            with patch('knotenlinie.ortak_zemin.ayar_ayik.yinele',side_effect=fit), \
                 patch('knotenlinie.ortak_zemin.ayar_ayik.b_ayarla',return_value={'deger':1.}):
                out=arka_plan_sec_ayik(d,self.kutu,end,3,pd.Timestamp('1985-01-01',tz='UTC'),
                    adaylar=[dict(k=10,alt_km=5,zemin_payi=.05)])
            sec=out['arka_plan']['secim']
            self.assertEqual(sec['kurulum_n'],2);self.assertEqual(sec['secim_n'],2)
            self.assertEqual(len(seen[0][0]),2);self.assertEqual(len(seen[1][0]),4)
            d.loc[3,'zaman']=pd.Timestamp(end,tz='UTC')
            with self.assertRaises(ValueError):
                arka_plan_sec_ayik(d,self.kutu,end,3,pd.Timestamp('1985-01-01',tz='UTC'))

    def test_known_nonuniform_background_and_triggering_reconstruction(self):
        # Gerçek şekil analitik: [10,12]×[40,42]'de integral=4.
        def shape(x,y):
            return (1+.8*np.cos(np.pi*(x-10)))*(1+.5*np.cos(np.pi*(y-40)))
        th=dict(mu=.8,K=.06,c=.1,alpha=.3,p=1.4,D=1.5,q=2,gamma=0)
        cat=B.uretim(th,0,1000,3,1,seed=20261005,bbox=self.kutu,metrik='km',arka_plan=shape)
        cat=cat[(cat.lon>=10)&(cat.lon<12)&(cat.lat>=40)&(cat.lat<42)].reset_index(drop=True)
        lik=Olabilirlik(cat.gun,cat.mag,cat.lon,cat.lat,3,1,1000,self.kutu)
        fit=yinele(lik,dict(k=20,alt_km=8.,zemin_payi=.05),maks_tur=30,tolerans=.005)
        diag=fit['arka_plan']['ayiklama'];phi=np.array(diag['phi']);true=cat.arka_plan.to_numpy()
        self.assertTrue(diag['yakinsadi'])
        self.assertLess(abs(fit['parametreler']['mu']/.8-1),.25)
        self.assertLess(abs(phi.sum()/true.sum()-1),.25)
        self.assertGreater(phi[true].mean(),.7);self.assertLess(phi[~true].mean(),.35)
        h=fit['arka_plan']; xe,ye=h['x_kenar'],h['y_kenar']
        # Hücre integralinin analitik cos ortalaması; merkez yaklaşımı yok.
        fx=1+.8*np.diff(np.sin(np.pi*(xe-10)))/(np.pi*np.diff(xe))
        fy=1+.5*np.diff(np.sin(np.pi*(ye-40)))/(np.pi*np.diff(ye))
        truth=fx[:,None]*fy[None,:]/4
        l1=float(np.sum(np.abs(h['yogunluk']-truth)*np.diff(xe)[:,None]*np.diff(ye)[None,:]))
        self.assertLess(l1,.28)
        print('KNOWN:',dict(N=len(cat),true_background=int(true.sum()),estimated_background=phi.sum(),
                             mu=fit['parametreler']['mu'],shape_L1=l1),flush=True)


if __name__ == '__main__':
    unittest.main()
