"""Zhuang dönüşümlü ayar; eski T giriş noktaları/dosyaları değişmez."""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy import optimize
from knotenlinie.etas import model as M
from .ayar import b_ayarla, dallanma, gr_ayar_paylari
from .arayuz import DuzETAS
from .arka_plan_ayik import uyarlamali_bant, kde_ayik
from .mle import kisitlar
from .veri import VERI, AYAR_SON, katalog_oku, json_yaz, sha256
from knotenlinie.yollar import kod_ozeti

AYIK = VERI / 'ortak/ayik'
ADAYLAR = tuple(dict(k=k, alt_km=h, zemin_payi=z)
                 for k,h,z in itertools.product((10,30), (5.,15.), (.01,.05)))


class Olabilirlik:
    """Tam çiftler önbellekte; doğal analitik gradyan, G türevi merkez farkı.

    Yakın/uzak anne kesimi yok. Kutudaki kompansatör mevcut T ile aynıdır;
    hedef maskesi yerine dış dikdörtgen kullanması T'den kalan sınırlamadır.
    """
    def __init__(self, t, mags, x, y, mc, b, T, kutu, maks_cift=12_000_000):
        self.t, self.m, self.x, self.y = [np.asarray(v,float) for v in (t,mags,x,y)]
        self.mc, self.b, self.beta, self.T, self.kutu = mc,b,b*np.log(10),T,kutu
        n = len(t)
        if n < 2 or n*(n-1)//2 > maks_cift:
            raise ValueError('Dolu katalog/tam çift bütçesi kapısı')
        if (not all(np.isfinite(v).all() for v in (self.t,self.m,self.x,self.y)) or
                (np.diff(self.t) < 0).any() or (self.t < 0).any() or (self.t >= T).any()):
            raise ValueError('Ayar zamanı/sırası geçersiz')
        met = M.yerel_metrik(kutu)
        self.jacobian = met.jakobiyen
        xx, yy = met.km(self.x,self.y)
        # Bellek: en çok 12m çift × 24 bayt + O(blok×N) çalışma alanı.
        ii, jj, dt, r2 = [], [], [], []
        for a in range(0,n,64):
            z = min(a+64,n)
            diff = self.t[a:z,None]-self.t[None,:z]
            i,j = np.nonzero(diff > 0)
            ii.append((i+a).astype(np.int32)); jj.append(j.astype(np.int32))
            dt.append(diff[i,j]); r2.append((xx[i+a]-xx[j])**2+(yy[i+a]-yy[j])**2)
        self.i, self.j, self.dt, self.r2 = [np.concatenate(v) for v in (ii,jj,dt,r2)]
        self.u = np.ones(n)/((kutu[1]-kutu[0])*(kutu[3]-kutu[2]))/self.jacobian
        self._last = None

    def set_u(self, u):
        self.u = np.asarray(u,float)/self.jacobian
        self._last = None

    def hesapla(self, xx, gradyan=True):
        th = M._x_den_theta(xx,self.beta,M.UZAY_ADLARI)
        mu,K,c,alpha,p,D,q,gamma = th
        dm = self.m-self.mc
        A = 10**(alpha*dm)
        Di = M.mekan_olcegi(D,gamma,self.m,self.mc)
        trigger = np.zeros(len(dm))
        sums = np.zeros((len(dm),6)) if gradyan else None
        for a in range(0,len(self.i),200_000):
            z = a+200_000
            i,j = self.i[a:z], self.j[a:z]
            dc = self.dt[a:z]+c
            rr = self.r2[a:z]/Di[j]**2
            v = K*A[j]*dc**(-p)*(q-1)/(np.pi*Di[j]**2)*(1+rr)**(-q)
            trigger += np.bincount(i,weights=v,minlength=len(dm))
            if gradyan:
                ds = -2+2*q*rr/(1+rr)
                derivatives = (-p/dc, np.log(10)*dm[j], -np.log(dc),
                               ds/D, 1/(q-1)-np.log1p(rr), ds*np.log(10)*dm[j])
                for k,dv in enumerate(derivatives):
                    sums[:,k] += np.bincount(i,weights=v*dv,minlength=len(dm))
        lam = mu*self.u+trigger
        G = M.mekan_kutu_integrali(self.x,self.y,Di,q,self.kutu)
        I,dIc,dIp = M._omori_ilke(self.T-self.t,c,p)
        value = np.log(lam).sum()-mu*self.T-K*np.sum(A*I*G)
        if not gradyan:
            return float(value), mu*self.u/lam
        grad = np.zeros(8)
        grad[0] = np.sum(self.u/lam)-self.T
        grad[1] = np.sum(trigger/lam)/K-np.sum(A*I*G)
        for k,jj in enumerate((2,3,4,5,6,7)):
            grad[jj] = np.sum(sums[:,k]/lam)
        grad[2] -= K*np.sum(A*dIc*G)
        grad[3] -= K*np.sum(A*np.log(10)*dm*I*G)
        grad[4] -= K*np.sum(A*dIp*G)
        # G'nin uzay türevleri ucuz O(N); çift türevleri analitik.
        step = 1e-5
        for jj in (5,6,7):
            plus,minus = th.copy(),th.copy()
            plus[jj] += step; minus[jj] -= step
            gp = M.mekan_kutu_integrali(self.x,self.y,
                M.mekan_olcegi(plus[5],plus[7],self.m,self.mc),plus[6],self.kutu)
            gm = M.mekan_kutu_integrali(self.x,self.y,
                M.mekan_olcegi(minus[5],minus[7],self.m,self.mc),minus[6],self.kutu)
            grad[jj] -= K*np.sum(A*I*(gp-gm)/(2*step))
        return -float(value), -grad*M._zincir_carpani(xx,self.beta)

    def nll(self, xx):
        if self._last is None or not np.array_equal(xx,self._last[0]):
            self._last = (xx.copy(), self.hesapla(xx))
        return self._last[1]

    def mle(self, start, maksiter=180):
        th = M._dizi(start,M.UZAY_ADLARI)
        th[3] = min(th[3],self.b*.95)
        cap = th[2]**(th[4]-1)*(th[4]-1)*(self.b-th[3])/self.b
        th[1] = min(th[1],.95*cap)
        res = optimize.minimize(self.nll,M._theta_dan_x(th,self.beta),jac=True,
            method='SLSQP',bounds=optimize.Bounds(*M.UZAY_SINIRLAR),
            constraints=[dict(type='ineq',fun=kisitlar,args=(self.beta,self.b))],
            options=dict(maxiter=maksiter,ftol=1e-6))
        # Aktif n≈1 sınırında SLSQP'nin varsayılan durması kısıt ihlaliyle
        # başarı diyebiliyor. Parametreyi kırpmadan aynı olabilirliği hassaslaştır.
        if not res.success or np.min(kisitlar(res.x,self.beta,self.b)) < -1e-7:
            res = optimize.minimize(self.nll,res.x,jac=True,method='SLSQP',
                bounds=optimize.Bounds(*M.UZAY_SINIRLAR),
                constraints=[dict(type='ineq',fun=kisitlar,args=(self.beta,self.b))],
                options=dict(maxiter=maksiter,ftol=1e-10))
        param = M._sozluk(M._x_den_theta(res.x,self.beta,M.UZAY_ADLARI),M.UZAY_ADLARI)
        if not res.success or np.min(kisitlar(res.x,self.beta,self.b)) < -1e-7:
            raise ValueError(f'MLE yakınsamadı/kısıt: {res.message}, nit={res.nit}, '
                             f'kısıt_min={np.min(kisitlar(res.x,self.beta,self.b))}')
        return dict(parametreler=param,logL=float(-res.fun),nit=int(res.nit),basari=True,
                    optimizer='SLSQP; tam çiftler, analitik gradyan/G merkez farkı; alpha<b,n<1')


def yinele(lik, hp, *, start=None, maks_tur=25, tolerans=.005, maksiter=180):
    h = uyarlamali_bant(lik.x,lik.y,lik.kutu,hp['k'],hp['alt_km'])
    phi = np.ones(len(lik.t))
    start = start or dict(M.BASLANGICLAR_UZAY[0],mu=len(phi)/lik.T,
                         alpha=lik.b*.5,gamma=.3)
    trace = []
    for turn in range(maks_tur):
        hist = kde_ayik(lik.x,lik.y,lik.kutu,h,phi,hp['zemin_payi'])
        u = M.arka_plan_degeri(lik.x,lik.y,hist)
        lik.set_u(u)
        fit = lik.mle(start,maksiter=maksiter)
        xx = M._theta_dan_x(M._dizi(fit['parametreler'],M.UZAY_ADLARI),lik.beta)
        _,newphi = lik.hesapla(xx,gradyan=False)
        nexthist = kde_ayik(lik.x,lik.y,lik.kutu,h,newphi,hp['zemin_payi'])
        area = np.diff(hist['x_kenar'])[:,None]*np.diff(hist['y_kenar'])[None,:]
        delta = float(np.sum(np.abs(hist['yogunluk']-nexthist['yogunluk'])*area))
        dp = float(np.mean(np.abs(phi-newphi)))
        trace.append(dict(tur=turn+1,phi_toplam=float(newphi.sum()),
                          phi_degisim=dp,harita_L1_degisim=delta,logL=fit['logL'],nit=fit['nit']))
        print(f'  {hp} tur={turn+1} φ={newphi.sum():.1f} Δ={delta:.4g} MLE={fit["nit"]}',flush=True)
        phi,start = newphi,fit['parametreler']
        if delta < tolerans and dp < tolerans and turn >= 2:
            # Hist, MLE ve φ aynı son olabilirlikten; φ ile bir sonraki harita
            # arasındaki L1 hata yukarıdaki ölçülmüş toleransın altındadır.
            hist.update(hp,ayiklama=dict(yakinsadi=True,tolerans=tolerans,
                        maks_tur=maks_tur,turlar=trace,phi=phi.tolist(),
                        arka_plan_n=float(phi.sum()),arka_plan_oran=float(phi.mean()),
                        bant_yontemi='öz hariç k-komşu; bütün ayar konumları, km metriği'))
            fit['arka_plan'] = hist
            return fit
    raise ValueError(f'Ayıklama {maks_tur} turda yakınsamadı: {trace[-1]}')


def arka_plan_sec_ayik(d, kutu, son, mc, baslangic, *, adaylar=ADAYLAR, maks_tur=25):
    end = pd.Timestamp(son)
    end = end.tz_localize('UTC') if end.tzinfo is None else end.tz_convert('UTC')
    if end not in (pd.Timestamp('2006-01-01',tz='UTC'),AYAR_SON):
        raise ValueError('Yalnız 2006/2011 ayar sonu')
    if d.empty or (d.zaman >= end).any() or (d.mw < mc).any():
        raise ValueError('Ayar verisi boş/son sınırını aşıyor/Mc altında')
    split = end-pd.DateOffset(years=5)
    train,hold = d[d.zaman < split],d[d.zaman >= split]
    if train.empty or hold.empty:
        raise ValueError('Zamansal bölmeler boş')
    def lik_for(rows, stop):
        t = ((rows.zaman-baslangic)/pd.Timedelta(days=1)).to_numpy(float)
        b = b_ayarla(rows.mw,mc)['deger']
        return Olabilirlik(t,rows.mw,rows.boylam,rows.enlem,mc,b,
                           (stop-baslangic)/pd.Timedelta(days=1),kutu)
    lik = lik_for(train,split)
    trials = []
    for hp in adaylar:
        before = time.monotonic()
        try:
            fit = yinele(lik,hp,maks_tur=maks_tur)
            u = M.arka_plan_degeri(hold.boylam.to_numpy(),hold.enlem.to_numpy(),fit['arka_plan'])
            score = float(np.log(u/M.yerel_metrik(kutu).jakobiyen).sum())
            trials.append(dict(**hp,logL_konum=score,yakinsadi=True,
                               turlar=fit['arka_plan']['ayiklama']['turlar']))
        except ValueError as e:
            trials.append(dict(**hp,yakinsadi=False,hata=str(e)))
        trials[-1]['saniye'] = time.monotonic()-before
    good = [x for x in trials if x['yakinsadi']]
    if not good:
        raise ValueError('Hiçbir ayıklama adayı yakınsamadı: '+str(trials))
    best = max(good,key=lambda x:x['logL_konum'])
    del lik
    fit = yinele(lik_for(d,end),{k:best[k] for k in ('k','alt_km','zemin_payi')},maks_tur=maks_tur)
    fit['arka_plan']['secim'] = dict(kurulum_bitis_haric=split.isoformat(),
        secim_baslangic=split.isoformat(),secim_bitis_haric=end.isoformat(),
        kurulum_n=len(train),secim_n=len(hold),yeniden_kurulum_n=len(d),
        yeniden_kurulum_max_zaman=d.zaman.max().isoformat(),en_iyi=best,adaylar=trials,
        olcut='tutulmuş bütün M≥Mc konumlarının sum log u_km; tam ETAS olabilirliği değil')
    return fit


def ayarla_ayik(bolge, *, son='2011-01-01', ortak=VERI/'ortak', cikti=AYIK,
                adaylar=ADAYLAR, maks_tur=25):
    started = time.monotonic()
    ortak,cikti = Path(ortak),Path(cikti)
    end = pd.Timestamp(son)
    end = end.tz_localize('UTC') if end.tzinfo is None else end.tz_convert('UTC')
    # Eski Mc/b/tamlık/GR arayüz metadata'sını koru; ileri ayardan başlatma yok.
    p = json.loads((ortak/f'etas_{bolge}_le{end.year-1}.json').read_text())
    if end not in (pd.Timestamp('2006-01-01',tz='UTC'),AYAR_SON) or pd.Timestamp(p['ayar_max_zaman']) >= end:
        raise ValueError('Ayar sonu kapısı')
    path = ortak/f'{bolge}_katalog_le2015.csv'
    if sha256(path) != p['katalog_sha256']:
        raise ValueError('Ayar katalog SHA uyuşmuyor')
    cat = katalog_oku(path)
    start = pd.Timestamp(p['ayar_baslangic'])
    d = cat[(cat.zaman >= start)&(cat.zaman < end)&(cat.mw >= p['mc'])].reset_index(drop=True)
    if len(d) != p['ayar_n']:
        raise ValueError('Ayar olay sayısı uyuşmuyor')
    fit = arka_plan_sec_ayik(d,p['kutu'],end,p['mc'],start,adaylar=adaylar,maks_tur=maks_tur)
    # Eski fit Hessian/serbest-MLE tanıları yeni fit'e taşınmaz.
    keep = ('bolge','mc','b','baslangic_yili','ayar_baslangic','ayar_bitis','tamlik',
            'mc_bilgi','kutu','katalog_sha256','izgara_sha256','ayar_n','ayar_max_zaman',
            'gr_ayar_paylari','metrik','normalizasyon','uzay_ayar_destegi','tahmin')
    fit.update({k:p[k] for k in keep})
    fit.update(dallanma=dallanma(fit['parametreler'],p['b']['deger']),
               duvar_saniye=time.monotonic()-started,
               durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler',
               kod_sha256=kod_ozeti(
                   ['knotenlinie/ortak_zemin/arka_plan_ayik.py','knotenlinie/ortak_zemin/ayar_ayik.py']))
    json_yaz(cikti/f'etas_{bolge}_le{end.year-1}_ayik.json',fit)
    return fit


def ayar_tabani_ayik(bolge, *, son='2011-01-01', ortak=VERI/'ortak', ayik=AYIK):
    end = pd.Timestamp(son)
    end = end.tz_localize('UTC') if end.tzinfo is None else end.tz_convert('UTC')
    if end not in (pd.Timestamp('2006-01-01',tz='UTC'),AYAR_SON):
        raise ValueError('Yalnız 2006/2011 ayar sonu')
    p = json.loads((Path(ayik)/f'etas_{bolge}_le{end.year-1}_ayik.json').read_text())
    if pd.Timestamp(p['ayar_bitis']) != end or pd.Timestamp(p['ayar_max_zaman']) >= end:
        raise ValueError('Ayıklanmış ayar sonu uyuşmuyor')
    grid = Path(ortak)/f'{bolge}_izgara.csv'
    if sha256(grid) != p['izgara_sha256']:
        raise ValueError('Izgara SHA uyuşmuyor')
    return DuzETAS(p,pd.read_csv(grid))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bolge',choices=('italya',),required=True)
    ap.add_argument('--son',choices=('2006-01-01','2011-01-01'),default='2011-01-01')
    ap.add_argument('--maks-tur',type=int,default=25)
    args = ap.parse_args()
    ayarla_ayik(args.bolge,son=args.son,maks_tur=args.maks_tur)


if __name__ == '__main__':
    main()
