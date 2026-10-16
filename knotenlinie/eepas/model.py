"""EEPAS_0F: eşit öncü ağırlıkları, günlük zaman ve km düzleminde yoğunluk."""
from __future__ import annotations

from dataclasses import dataclass, replace, asdict

import numpy as np
import pandas as pd
from scipy import optimize, special

from knotenlinie.etas import model as ETAS

LN10 = np.log(10.0)
GUN = pd.Timedelta(days=1)
EPOCH = pd.Timestamp('1970-01-01', tz='UTC')


def zaman_gun(zaman):
    """Datetime çözünürlüğünden bağımsız UTC günleri."""
    return np.asarray((pd.to_datetime(zaman, utc=True) - EPOCH) / GUN, float)


def katalog_dizileri(df):
    a = (zaman_gun(df['zaman']), df['mw'].to_numpy(float),
         df['boylam'].to_numpy(float), df['enlem'].to_numpy(float))
    if any(not np.all(np.isfinite(v)) for v in a):
        raise ValueError('Katalogda eksik/sonsuz değer')
    return a


@dataclass(frozen=True)
class Parametreler:
    """NZ 1987–2006 EEPAS_0F başlangıcı; bölgesel ayar yerine geçmez."""
    m0: float = 2.95
    b: float = 1.0
    r0: float = 1.0                  # M >= m0 olay/gün; yalnız ayar dönemi
    mu: float = 0.1                  # PPE payı
    olcek: float = 1.0               # toplam hızı ayar döneminde normalleştirir
    aM: float = 1.10
    bM: float = 1.0
    sigmaM: float = 0.39
    aT: float = 1.71
    bT: float = 0.39
    sigmaT: float = 0.60
    sigmaA: float = 1.63             # km; sigma_i = sigmaA * 10^(bA mi / 2)
    bA: float = 0.36
    gecikme: float = 50.0           # kesme; çekirdek kaydırılmaz/yeniden normalize edilmez
    telafi: bool = True              # eksik M<m0 öncüler için denklem (11)

    def __post_init__(self):
        vals = [v for k, v in asdict(self).items() if k != 'telafi']
        if not np.all(np.isfinite(vals)):
            raise ValueError('Sonlu parametreler gerekli')
        if min(self.b, self.r0, self.olcek, self.bM, self.sigmaM,
               self.sigmaT, self.sigmaA) <= 0 or not 0 <= self.mu <= 1 or self.gecikme < 0:
            raise ValueError('EEPAS parametre alanı ihlali')


def normal_aralik(lo, hi):
    """Normal CDF farkı: sağ kuyrukta çıkarma kaybı yok."""
    lo, hi = np.broadcast_arrays(lo, hi)
    return np.maximum(np.where(lo > 0, special.ndtr(-lo) - special.ndtr(-hi),
                               special.ndtr(hi) - special.ndtr(lo)), 0.0)


def zaman_kutlesi(lo, hi, m, p):
    lo, hi, m = np.broadcast_arrays(lo, hi, m)
    l = np.maximum(lo, p.gecikme)
    with np.errstate(divide='ignore', invalid='ignore'):
        zl = (np.log10(np.maximum(l, 0)) - p.aT - p.bT*m) / p.sigmaT
        zh = (np.log10(np.maximum(hi, 0)) - p.aT - p.bT*m) / p.sigmaT
    return np.where(hi > l, normal_aralik(zl, zh), 0.0)


def zaman_yogunlugu(dt, m, p):
    dt, m = np.broadcast_arrays(dt, m)
    d = np.maximum(dt, np.finfo(float).tiny)
    z = (np.log10(d) - p.aT - p.bT*m) / p.sigmaT
    with np.errstate(over='ignore', under='ignore'):
        f = np.exp(-z*z/2) / (d*p.sigmaT*LN10*np.sqrt(2*np.pi))
    return np.where((dt > 0) & (dt >= p.gecikme), f, 0.0)


def eta(m, p):
    """Denklem (7), E(w)=1; (1-mu) karışımda ayrıca uygulanır."""
    beta = p.b*LN10
    return p.bM*np.exp(-beta*(p.aM + (p.bM-1)*np.asarray(m) + p.sigmaM**2*beta/2))


def buyukluk_yogunlugu(m, oncu_m, p):
    z = (np.asarray(m) - p.aM - p.bM*np.asarray(oncu_m)) / p.sigmaM
    logg = -z*z/2 - np.log(p.sigmaM*np.sqrt(2*np.pi))
    if p.telafi:
        zd = (np.asarray(m) - p.aM - p.bM*p.m0 - p.sigmaM**2*p.b*LN10)/p.sigmaM
        logg = logg - special.log_ndtr(zd)
    return np.exp(logg)


_GL_X, _GL_W = np.polynomial.legendre.leggauss(24)


def buyukluk_kutlesi(kenarlar, oncu_m, p):
    """g/Delta integrali; paneller <=0.1 M, 24 düğüm, sonsuz kenar kabul edilmez."""
    e = np.asarray(kenarlar, float)
    if e.ndim != 1 or e.size < 2 or not np.all(np.isfinite(e)) or np.any(np.diff(e) <= 0):
        raise ValueError('Artan sonlu büyüklük kenarları gerekli')
    m = np.atleast_1d(oncu_m)
    if not p.telafi:
        return normal_aralik((e[:-1,None]-p.aM-p.bM*m)/p.sigmaM,
                             (e[1:,None]-p.aM-p.bM*m)/p.sigmaM)
    sonuc = np.zeros((len(e)-1, len(m)))
    for j, (lo, hi) in enumerate(zip(e[:-1], e[1:])):
        pan = np.linspace(lo, hi, max(1, int(np.ceil((hi-lo)/0.1)))+1)
        h = np.diff(pan)/2
        x = (pan[:-1,None]+pan[1:,None])/2+h[:,None]*_GL_X
        w = h[:,None]*_GL_W
        sonuc[j] = np.sum(buyukluk_yogunlugu(x.reshape(-1,1), m, p)*w.reshape(-1,1), axis=0)
    return sonuc


def hucreler(izgara, met):
    a = izgara[['boylam_min','boylam_max','enlem_min','enlem_max']].to_numpy(float)
    if not np.all(np.isfinite(a)) or np.any(a[:,1] <= a[:,0]) or np.any(a[:,3] <= a[:,2]):
        raise ValueError('Geçerli hücre kenarları gerekli')
    return (met.kx*(a[:,0]-met.lam0), met.kx*(a[:,1]-met.lam0),
            met.ky*(a[:,2]-met.phi0), met.ky*(a[:,3]-met.phi0))


def gaussian_hucre(x, y, sigma, izgara, met):
    x0,x1,y0,y1 = hucreler(izgara, met)
    return (normal_aralik((x0[:,None]-x)/sigma, (x1[:,None]-x)/sigma)*
            normal_aralik((y0[:,None]-y)/sigma, (y1[:,None]-y)/sigma))


def kutu_izgara(kutu):
    a,b,c,d = kutu
    return pd.DataFrame([[c,d,a,b]], columns=['boylam_min','boylam_max','enlem_min','enlem_max'])


class ArkaPlan:
    """PPE: sabit bantlı Gaussian KDE, kutuya normalize; boş merkezler düzgün alan."""
    def __init__(self, kutu, merkezler=None, bant=25.0, duzgun_pay=0.05):
        self.kutu = tuple(kutu)
        self.met = ETAS.yerel_metrik(kutu)
        self.bant = float(bant)
        self.duzgun_pay = float(duzgun_pay)
        if not np.isfinite(bant) or bant <= 0 or not 0<=self.duzgun_pay<=1:
            raise ValueError('Pozitif PPE bant genişliği ve [0,1] düzgün pay gerekli')
        self.merkezler = (merkezler[['boylam','enlem']].copy() if merkezler is not None
                          else pd.DataFrame(columns=['boylam','enlem']))
        self.x,self.y = self.met.km(self.merkezler.boylam, self.merkezler.enlem)
        self.x,self.y = np.asarray(self.x), np.asarray(self.y)
        x0,x1,y0,y1 = self.met.kutu_km()
        self.alan = (x1-x0)*(y1-y0)
        self.norm = (gaussian_hucre(self.x,self.y,bant,kutu_izgara(kutu),self.met).mean()
                     if len(self.x) else 1.0)
        if self.norm <= 0:
            raise ValueError('PPE kutu kütlesi sıfır')

    def yogunluk(self, lon, lat):
        x,y = self.met.km(lon, lat)
        x,y = np.atleast_1d(x),np.atleast_1d(y)
        x0,x1,y0,y1 = self.met.kutu_km()
        inside = (x>=x0)&(x<x1)&(y>=y0)&(y<y1)
        out = np.full(len(x),1/self.alan)
        if len(self.x):
            for a in range(0,len(x),256):
                r2 = (x[a:a+256,None]-self.x)**2+(y[a:a+256,None]-self.y)**2
                out[a:a+256] = np.exp(-r2/(2*self.bant**2)).mean(axis=1)/(2*np.pi*self.bant**2*self.norm)
        if len(self.x):
            out = (1-self.duzgun_pay)*out+self.duzgun_pay/self.alan
        return out*inside

    def kutle(self, izgara):
        # Model alanı dışında PPE sıfırdır; hücreleri alanla kes.
        g = izgara.copy()
        a,b,c,d = self.kutu
        g['boylam_min'] = np.maximum(g.boylam_min,c)
        g['boylam_max'] = np.minimum(g.boylam_max,d)
        g['enlem_min'] = np.maximum(g.enlem_min,a)
        g['enlem_max'] = np.minimum(g.enlem_max,b)
        ok = (g.boylam_max>g.boylam_min)&(g.enlem_max>g.enlem_min)
        out = np.zeros(len(g))
        x0,x1,y0,y1 = hucreler(g.loc[ok],self.met)
        uniform = (x1-x0)*(y1-y0)/self.alan
        if len(self.x):
            out[ok] = ((1-self.duzgun_pay)*gaussian_hucre(self.x,self.y,self.bant,g.loc[ok],self.met).mean(axis=1)/self.norm
                       +self.duzgun_pay*uniform)
        else:
            out[ok] = uniform
        return out


class EEPAS:
    """Sürekli yoğunluk ve analitik zaman/uzay hücre integralleri."""
    def __init__(self, p, kutu, arka_plan=None):
        self.p = p
        self.kutu = tuple(kutu)
        self.met = ETAS.yerel_metrik(kutu)
        self.arka_plan = arka_plan or ArkaPlan(kutu)
        if self.arka_plan.kutu != self.kutu:
            raise ValueError('PPE ve model kutusu farklı')

    def yogunluk(self, hedefler, gecmis, blok=256):
        t,m,lo,la = katalog_dizileri(hedefler)
        pt,pm,pl,pa = katalog_dizileri(gecmis.loc[gecmis.mw>=self.p.m0])
        px,py = self.met.km(pl,pa)
        x,y = self.met.km(lo,la)
        p = self.p
        bg = p.r0*p.b*LN10*np.exp(-p.b*LN10*(m-p.m0))*self.arka_plan.yogunluk(lo,la)
        out = p.mu*bg
        sig = p.sigmaA*10**(p.bA*pm/2)
        for a in range(0,len(t),blok):
            sl = slice(a,a+blok)
            r2 = (x[sl,None]-px)**2+(y[sl,None]-py)**2
            h = np.exp(-r2/(2*sig**2))/(2*np.pi*sig**2)
            f = zaman_yogunlugu(t[sl,None]-pt,pm,p)
            g = buyukluk_yogunlugu(m[sl,None],pm,p)
            out[sl] += (1-p.mu)*np.sum(eta(pm,p)*f*g*h,axis=1)
        return p.olcek*out

    def beklenen_sayisal(self, t0, t1, gecmis, izgara, m_kenarlar, blok=256):
        if not np.isfinite(t0+t1) or t1 <= t0:
            raise ValueError('Pozitif sonlu zaman penceresi gerekli')
        p = self.p
        e = np.asarray(m_kenarlar,float)
        # Kenar doğrulaması, boş geçmişte de geçerli.
        buyukluk_kutlesi(e, np.array([]), p)
        bgm = np.exp(-p.b*LN10*(e[:-1]-p.m0))*(-np.expm1(-p.b*LN10*np.diff(e)))
        out = p.mu*p.r0*(t1-t0)*self.arka_plan.kutle(izgara)[:,None]*bgm
        pt,pm,pl,pa = katalog_dizileri(gecmis.loc[gecmis.mw>=p.m0])
        sig = p.sigmaA*10**(p.bA*pm/2)
        for a in range(0,len(pt),blok):
            s = slice(a,a+blok)
            x,y = self.met.km(pl[s],pa[s])
            h = gaussian_hucre(x,y,sig[s],izgara,self.met)
            tm = zaman_kutlesi(t0-pt[s],t1-pt[s],pm[s],p)*eta(pm[s],p)
            mg = buyukluk_kutlesi(e,pm[s],p)
            out += (1-p.mu)*(h*tm)@mg.T
        return p.olcek*np.maximum(out,0)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        t0,t1 = zaman_gun([baslangic,bitis])
        pt = zaman_gun(gecmis.zaman)
        if np.any(pt >= t0):
            raise ValueError('Geçmiş başlangıçtan önce olmalı')
        return self.beklenen_sayisal(t0,t1,gecmis,izgara,m_kenarlar)


def log_olabilirlik(model, hedefler, gecmis, t0, t1, m_aralik):
    """Tam noktasal Poisson olabilirliği: olay log yoğunluğu EKSİ integral."""
    t,m,lo,la = katalog_dizileri(hedefler)
    a,b,c,d = model.kutu
    if np.any((t<t0)|(t>=t1)|(m<m_aralik[0])|(m>=m_aralik[1])|
              (lo<c)|(lo>=d)|(la<a)|(la>=b)):
        raise ValueError('Hedefler ayar alanı dışında')
    if m_aralik[0] < (model.p.m0 if isinstance(model,EEPAS) else getattr(model,'m0',-np.inf)):
        raise ValueError('Hedef eşiği öncü eşiğinden düşük olamaz')
    lam = model.yogunluk(hedefler,gecmis)
    integ = model.beklenen_sayisal(t0,t1,gecmis,kutu_izgara(model.kutu),m_aralik).sum()
    if np.any(lam<=0) or not np.all(np.isfinite(lam)) or not np.isfinite(integ):
        return -np.inf
    return float(np.log(lam).sum()-integ)


SINIRLAR = {'mu':(0,1), 'aM':(0.1,2.5), 'bM':(0.5,1.5), 'sigmaM':(0.15,1.2),
            'aT':(-1,4), 'bT':(0.05,1.2), 'sigmaT':(0.15,1.2),
            'sigmaA':(0.1,30), 'bA':(0.05,1.2)}


def ayarla(hedefler, gecmis, t0, t1, m_aralik, p, kutu, arka_plan=None,
           serbest=('mu','aT','sigmaA'), maksiter=200, baslangiclar=None):
    """Profil MLE: toplam hız N/integral; bölgesel varsayılan üç biçim parametresi."""
    if len(hedefler)==0 or not serbest or any(k not in SINIRLAR for k in serbest):
        raise ValueError('Hedefler ve bilinen serbest parametreler gerekli')
    p = replace(p,olcek=1.0)
    def cozum(x):
        q = replace(p,**dict(zip(serbest,x)))
        model = EEPAS(q,kutu,arka_plan)
        integ = model.beklenen_sayisal(t0,t1,gecmis,kutu_izgara(kutu),m_aralik).sum()
        if not np.isfinite(integ) or integ<=0:
            return model,1.0
        return EEPAS(replace(q,olcek=len(hedefler)/integ),kutu,arka_plan),integ
    def f(x):
        model,_ = cozum(x)
        ell = log_olabilirlik(model,hedefler,gecmis,t0,t1,m_aralik)
        return -ell if np.isfinite(ell) else 1e100
    starts = baslangiclar or [p,replace(p,mu=0.5,aT=p.aT-0.5),replace(p,mu=0.8,aT=p.aT+0.5)]
    runs = [optimize.minimize(f,[getattr(s,k) for k in serbest], method='L-BFGS-B',
                            bounds=[SINIRLAR[k] for k in serbest],
                            options={'maxiter':maksiter,'ftol':1e-11}) for s in starts]
    best = min(runs,key=lambda r:r.fun)
    model,_ = cozum(best.x)
    return model, {'parametreler':asdict(model.p),'serbest':list(serbest),
                   'logL':float(-best.fun),'basari':bool(best.success and best.fun<1e100),
                   'mesaj':str(best.message),'nit':int(best.nit),
                   'baslangic_logL':[float(-r.fun) for r in runs],
                   'sinirda':[k for k,v in zip(serbest,best.x)
                              if min(abs(v-SINIRLAR[k][0]),abs(v-SINIRLAR[k][1]))<1e-5]}
