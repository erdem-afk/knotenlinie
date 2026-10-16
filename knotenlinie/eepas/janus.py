"""Mevcut ETAS çekirdeklerini kullanan adaptör ve konveks Janus karışımı."""
from __future__ import annotations

import numpy as np
from scipy import optimize, stats

from knotenlinie.etas import model as ETAS
from .model import (ArkaPlan, katalog_dizileri, zaman_gun, hucreler, LN10,
                    kutu_izgara, log_olabilirlik)


class ETASModel:
    """Ogata uzay-zaman ETAS; gün/km birimleri ve kesin hücre integralleri."""
    def __init__(self, parametreler, m0, b, kutu, arka_plan=None):
        self.theta = np.array([parametreler[k] for k in ETAS.UZAY_ADLARI],float)
        mu,K,c,alpha,p,D,q,gamma = self.theta
        if (not np.all(np.isfinite(self.theta)) or min(mu,K,c,D)<=0 or
                p<=1 or q<=1 or not 0<=alpha<b or b<=0):
            raise ValueError('ETAS parametre alanı ihlali')
        self.m0,self.b = float(m0),float(b)
        self.kutu = tuple(kutu)
        self.met = ETAS.yerel_metrik(kutu)
        self.arka_plan = arka_plan or ArkaPlan(kutu)
        if self.arka_plan.kutu != self.kutu:
            raise ValueError('PPE ve ETAS kutusu farklı')

    def yogunluk(self, hedefler, gecmis, blok=256):
        t,m,lo,la = katalog_dizileri(hedefler)
        pt,pm,pl,pa = katalog_dizileri(gecmis.loc[gecmis.mw>=self.m0])
        x,y = self.met.km(lo,la)
        px,py = self.met.km(pl,pa)
        mu,K,c,alpha,p,D,q,gamma = self.theta
        out = mu*self.arka_plan.yogunluk(lo,la)
        A = K*10**(alpha*(pm-self.m0))
        for a in range(0,len(t),blok):
            s = slice(a,a+blok)
            dt = t[s,None]-pt
            f = np.where(dt>0,(np.maximum(dt,0)+c)**(-p),0)
            r2 = (x[s,None]-px)**2+(y[s,None]-py)**2
            h = ETAS.mekan_cekirdegi(r2,D,q,gamma,pm,self.m0)
            out[s] += np.sum(A*f*h,axis=1)
        return out*self.b*LN10*np.exp(-self.b*LN10*(m-self.m0))

    def beklenen_sayisal(self, t0, t1, gecmis, izgara, m_kenarlar, blok=256):
        if not np.isfinite(t0+t1) or t1<=t0:
            raise ValueError('Pozitif sonlu zaman penceresi gerekli')
        e = np.asarray(m_kenarlar,float)
        if e.ndim!=1 or len(e)<2 or not np.all(np.isfinite(e)) or np.any(np.diff(e)<=0):
            raise ValueError('Artan sonlu büyüklük kenarları gerekli')
        hucreler(izgara,self.met)
        pt,pm,pl,pa = katalog_dizileri(gecmis.loc[gecmis.mw>=self.m0])
        mu,K,c,alpha,p,D,q,gamma = self.theta
        out = mu*(t1-t0)*self.arka_plan.kutle(izgara)
        low,high = np.maximum(t0-pt,0),np.maximum(t1-pt,0)
        Ihi = ETAS._omori_ilke(high,c,p)[0]
        Ilo = ETAS._omori_ilke(low,c,p)[0]
        A = K*10**(alpha*(pm-self.m0))*(Ihi-Ilo)
        Di = ETAS.mekan_olcegi(D,gamma,pm,self.m0)
        # Her hücre aynı bölge metriği ile, ortanokta yaklaşımı olmadan.
        for j,cell in enumerate(izgara.itertuples(index=False)):
            box = (cell.enlem_min,cell.enlem_max,cell.boylam_min,cell.boylam_max)
            for a in range(0,len(pm),blok):
                s = slice(a,a+blok)
                out[j] += np.sum(A[s]*ETAS.mekan_kutu_integrali(pl[s],pa[s],Di[s],q,box,metrik=self.met))
        mg = np.exp(-self.b*LN10*(e[:-1]-self.m0))*(-np.expm1(-self.b*LN10*np.diff(e)))
        return np.maximum(out[:,None]*mg,0)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        t0,t1 = zaman_gun([baslangic,bitis])
        if np.any(zaman_gun(gecmis.zaman)>=t0):
            raise ValueError('Geçmiş başlangıçtan önce olmalı')
        return self.beklenen_sayisal(t0,t1,gecmis,izgara,m_kenarlar)


class Janus:
    """w EEPAS + (1-w) ETAS; w yalnız ayar penceresinde belirlenir."""
    def __init__(self, eepas, etas, agirlik):
        if not np.isfinite(agirlik) or not 0<=agirlik<=1:
            raise ValueError('Janus ağırlığı [0,1] içinde olmalı')
        if eepas.kutu != etas.kutu:
            raise ValueError('Janus bileşen kutuları farklı')
        self.eepas,self.etas,self.agirlik = eepas,etas,float(agirlik)
        self.kutu = eepas.kutu

    def yogunluk(self, hedefler, gecmis):
        return (self.agirlik*self.eepas.yogunluk(hedefler,gecmis)+
                (1-self.agirlik)*self.etas.yogunluk(hedefler,gecmis))

    def beklenen_sayisal(self, *args, **kwargs):
        return (self.agirlik*self.eepas.beklenen_sayisal(*args,**kwargs)+
                (1-self.agirlik)*self.etas.beklenen_sayisal(*args,**kwargs))

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        args = (baslangic,bitis,gecmis,izgara,m_kenarlar)
        return self.agirlik*self.eepas.beklenen(*args)+(1-self.agirlik)*self.etas.beklenen(*args)


def agirlik_ayarla(eepas_lam, etas_lam, eepas_integral, etas_integral):
    """Noktasal olabilirlikten tek w MLE; iki uç da açıkça değerlendirilir."""
    e,t = np.asarray(eepas_lam,float),np.asarray(etas_lam,float)
    if (e.shape!=t.shape or e.ndim!=1 or len(e)==0 or np.any(e<0) or np.any(t<0) or
            not np.all(np.isfinite(e+t)) or min(eepas_integral,etas_integral)<0 or
            not np.isfinite(eepas_integral+etas_integral)):
        raise ValueError('Geçerli olay yoğunlukları ve integraller gerekli')
    def nll(w):
        lam = w*e+(1-w)*t
        if np.any(lam<=0):
            return np.inf
        return float(-np.log(lam).sum()+w*eepas_integral+(1-w)*etas_integral)
    r = optimize.minimize_scalar(nll,bounds=(0,1),method='bounded',options={'xatol':1e-12})
    w = min((0.0,1.0,float(r.x)),key=nll)
    curv = float(np.sum(((e-t)/(w*e+(1-w)*t))**2))
    return {'agirlik':w,'logL':-nll(w),'std':1/np.sqrt(curv) if curv>0 else None,
            'sinirda':w in (0.0,1.0),'tanimlanabilir':curv>0}


def janus_ayarla(eepas, etas, hedefler, gecmis, t0, t1, m_aralik):
    args = (t0,t1,gecmis,kutu_izgara(eepas.kutu),m_aralik)
    sonuc = agirlik_ayarla(eepas.yogunluk(hedefler,gecmis),etas.yogunluk(hedefler,gecmis),
                          eepas.beklenen_sayisal(*args).sum(),etas.beklenen_sayisal(*args).sum())
    return Janus(eepas,etas,sonuc['agirlik']),sonuc


def bilgi_kazanci(lam, taban_lam, integral, taban_integral):
    """Poisson IG/olay ve eşleştirilmiş iki yönlü T, %95 aralık."""
    a,b = np.asarray(lam,float),np.asarray(taban_lam,float)
    if (a.shape!=b.shape or a.ndim!=1 or np.any(a<=0) or np.any(b<=0) or
            not np.all(np.isfinite(a+b)) or min(integral,taban_integral)<0 or
            not np.isfinite(integral+taban_integral)):
        raise ValueError('Pozitif sonlu olay yoğunlukları gerekli; epsilon eklenmez')
    n = len(a)
    if n==0:
        return {'n':0,'ig':None,'se':None,'aralik95':None,'p':None}
    x = np.log(a/b) - (integral-taban_integral)/n
    ort = float(x.mean())
    if n<2:
        return {'n':n,'ig':ort,'se':None,'aralik95':None,'p':None}
    se = float(x.std(ddof=1)/np.sqrt(n))
    if se==0:
        p = 1.0 if ort==0 else 0.0
        ara = [ort,ort]
    else:
        p = float(2*stats.t.sf(abs(ort/se),n-1))
        d = float(stats.t.ppf(0.975,n-1)*se)
        ara = [ort-d,ort+d]
    return {'n':n,'ig':ort,'se':se,'aralik95':ara,'p':p}


def etas_ayarla(hedefler, gecmis, t0, t1, m_aralik, m0, b, kutu,
                arka_plan=None, maksiter=120):
    """ETAS bölgesel MLE; çekirdekler mevcut paketten, sıcak geçmiş integrali doğru."""
    # Eski mle_uzay_zaman bütün satırları hedef sayıyor; sıcak geçmiş için adaptör.
    starts = ETAS.BASLANGICLAR_UZAY
    def build(x):
        th = ETAS._x_den_theta(x,b,ETAS.UZAY_ADLARI)
        return ETASModel(dict(zip(ETAS.UZAY_ADLARI,th)),m0,b,kutu,arka_plan)
    def f(x):
        # Aşırı D/gamma tekliflerinde mevcut çekirdeğin kuvvetleri taşabilir.
        # Teklif reddi, son yoğunlukta epsilon/NaN temizleme değildir.
        with np.errstate(over='ignore',under='ignore',divide='ignore',invalid='ignore'):
            ell = log_olabilirlik(build(x),hedefler,gecmis,t0,t1,m_aralik)
        return -ell if np.isfinite(ell) else 1e12
    # Sayısal finite-difference + dev ceza L-BFGS'nin başlangıçta yanlış
    # yakınsamasına yol açıyor. Powell çekirdeği/alanı değiştirmeden arar.
    runs = [optimize.minimize(f,np.clip(ETAS._theta_dan_x(ETAS._dizi(s,ETAS.UZAY_ADLARI),b),
                                        *ETAS.UZAY_SINIRLAR),
                             method='Powell',bounds=optimize.Bounds(*ETAS.UZAY_SINIRLAR),
                             options={'maxiter':maksiter,'ftol':1e-8,'xtol':1e-5}) for s in starts]
    r = min(runs,key=lambda z:z.fun)
    model = build(r.x)
    return model, {'parametreler':dict(zip(ETAS.UZAY_ADLARI,map(float,model.theta))),
                   'm0':m0,'b':b,'logL':float(-r.fun),'basari':bool(r.success and r.fun<1e12),
                   'nit':int(r.nit),'mesaj':str(r.message),'yontem':'Powell',
                   'baslangic_logL':[float(-f(np.clip(ETAS._theta_dan_x(ETAS._dizi(s,ETAS.UZAY_ADLARI),b),
                                                     *ETAS.UZAY_SINIRLAR))) for s in starts],
                   'son_logL':[float(-z.fun) for z in runs],
                   'sinirda':[name for name,v,lo,hi in zip(ETAS.UZAY_ADLARI,r.x,*ETAS.UZAY_SINIRLAR)
                              if min(abs(v-lo),abs(v-hi))<1e-3]}
