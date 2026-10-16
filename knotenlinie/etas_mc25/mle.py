"""Tam ebeveyn çiftleriyle alt-kritik uzay-zaman MLE; analitik gradyan."""
from __future__ import annotations
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logit
from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin.ayar import dallanma

ADLAR = M.UZAY_ADLARI


def coz(v, b, tur):
    mu, n, c = np.exp(v[0]), expit(v[1]), np.exp(v[2])
    alpha, p = b*expit(v[3]), 1+np.exp(v[4])
    K = n*(p-1)*c**(p-1)*(b-alpha)/b
    return dict(mu=mu, K=K, c=c, alpha=alpha, p=p,
                D=np.exp(v[5]), q=1+np.exp(v[6]), gamma=v[7] if tur == 'ortak' else 0.)


def donustur(th, b, tur):
    v = [np.log(th['mu']), logit(dallanma(th,b)), np.log(th['c']),
         logit(th['alpha']/b), np.log(th['p']-1), np.log(th['D']), np.log(th['q']-1)]
    return np.r_[v,th['gamma']] if tur == 'ortak' else np.array(v)


class Olabilirlik:
    """Dikdörtgen kompansatörü; kesme/örneklenmiş çift yok, eş zaman ebeveyn yok."""
    def __init__(self,t,m,x,y,mc,b,T,kutu,u=None):
        self.t,self.dm = np.asarray(t,float),np.asarray(m,float)-mc
        self.x,self.y = np.asarray(x,float),np.asarray(y,float)
        self.mc,self.b,self.T,self.kutu=mc,b,T,tuple(kutu)
        if not len(t) or (self.t<0).any() or (self.t>=T).any() or (self.dm<0).any() or (np.diff(self.t)<0).any():
            raise ValueError('MLE zaman/Mc kapısı')
        n=len(t)
        if n*(n-1)//2 > 15_000_000:
            raise ValueError('yerel tam çift bütçesi 15 milyon; Mc yükseltilmez')
        self.met=M.yerel_metrik(kutu)
        xk,yk=self.met.km(x,y)
        i,j=np.tril_indices(n,-1)
        keep=self.t[i]>self.t[j]
        self.i,self.j=i[keep].astype(np.int32),j[keep].astype(np.int32)
        self.dt=self.t[self.i]-self.t[self.j]
        self.r2=(xk[self.i]-xk[self.j])**2+(yk[self.i]-yk[self.j])**2
        area=(kutu[1]-kutu[0])*(kutu[3]-kutu[2])
        self.u=(np.full(n,1/area) if u is None else np.asarray(u,float))/self.met.jakobiyen
        x0,x1,y0,y1=self.met.kutu_km()
        ax,ay=np.array([x0,x1,x1,x0]),np.array([y0,y0,y1,y1])
        bx,by=np.array([x1,x1,x0,x0]),np.array([y0,y1,y1,y0])
        R,w,pair,count=M._ucgen_dugumleri(xk[:,None],yk[:,None],ax[None,:],ay[None,:],bx[None,:],by[None,:])
        self.R,self.w,self.parent=R,w,pair//4

    def deger(self, th, grad=False):
        mu,K,c,a,p,D,q,gamma=[th[k] for k in ADLAR]
        n=len(self.t)
        Di=D*np.exp(M.LN10*gamma*self.dm)
        A=np.exp(M.LN10*a*self.dm)
        dc=self.dt+c
        u=self.r2/Di[self.j]**2
        logu=np.log1p(u)
        z=K*A[self.j]*np.exp(-p*np.log(dc))*(q-1)/(np.pi*Di[self.j]**2)*np.exp(-q*logu)
        S=np.bincount(self.i,z,minlength=n)
        lam=mu*self.u+S
        if not np.isfinite(lam).all() or (lam<=0).any():
            raise ValueError('Sonlu pozitif olabilirlik oranı gerekli')
        U=self.R/Di[self.parent]**2
        L=np.log1p(U)
        E=np.exp((1-q)*L)
        G=np.bincount(self.parent,self.w*(-np.expm1((1-q)*L)),minlength=n)
        I,Ic,Ip=M._omori_ilke(self.T-self.t,c,p)
        comp=K*A*I
        ll=float(np.log(lam).sum()-mu*self.T-np.dot(comp,G))
        if not grad:
            return ll
        inv=1/lam
        g=np.zeros(8)
        g[0]=np.dot(inv,self.u)-self.T
        # Pair derivatives use event-specific inv(lambda), not inv(sum z).
        wz=z*inv[self.i]
        g[1]=wz.sum()/K-np.dot(A*I,G)
        g[2]=np.dot(wz,-p/dc)-np.dot(K*A*Ic,G)
        g[3]=np.dot(wz,M.LN10*self.dm[self.j])-np.dot(comp*M.LN10*self.dm,G)
        g[4]=np.dot(wz,-np.log(dc))-np.dot(K*A*Ip,G)
        scale=2*(-1+q*u/(1+u))
        dGlogD=np.bincount(self.parent,self.w*2*(1-q)*U/(1+U)*E,minlength=n)
        dGq=np.bincount(self.parent,self.w*L*E,minlength=n)
        g[5]=(np.dot(wz,scale)-np.dot(comp,dGlogD))/D
        g[6]=np.dot(wz,1/(q-1)-logu)-np.dot(comp,dGq)
        g[7]=np.dot(wz,scale*M.LN10*self.dm[self.j])-np.dot(comp,dGlogD*M.LN10*self.dm)
        return ll,g

    def objectif(self,v,tur):
        th=coz(v,self.b,tur)
        ll,g=self.deger(th,True)
        mu,K,c,a,p,D,q,gamma=[th[k] for k in ADLAR]
        n=expit(v[1]); f=expit(v[3])
        gx=np.array([g[0]*mu, g[1]*K*(1-n), g[2]*c+g[1]*K*(p-1),
                     self.b*f*(1-f)*(g[3]-g[1]*K/(self.b-a)),
                     (p-1)*(g[4]+g[1]*K*(1/(p-1)+np.log(c))),
                     g[5]*D, g[6]*(q-1),g[7]])
        if tur=='lm': gx=gx[:-1]
        return -ll/len(self.t),-gx/len(self.t)


def ayarla(L,tur,*,maksiter=300,baslangiclar=None):
    if tur not in ('ortak','lm'): raise ValueError('İki sabit çekirdek')
    starts=baslangiclar or [dict(mu=len(L.t)/L.T*.5,K=.01,c=.02,alpha=L.b*.55,p=1.25,D=1.1,q=1.5,gamma=.2),
                            dict(mu=len(L.t)/L.T*.7,K=.01,c=.01,alpha=L.b*.7,p=1.15,D=2.2,q=1.8,gamma=.4)]
    bounds=[(-11.5,6.9),(-9.2,float(logit(1-1e-6))),(-6.9,3.4),(-9.2,9.2),(-6.9,1.386),
            (np.log(1e-5*M.KM_DERECE),np.log(10*M.KM_DERECE)),(-6.9,2.3)]
    if tur=='ortak':bounds.append((0.,2.))
    results=[]
    for start in starts:
        th=dict(start)
        # Deterministic starts are feasible; K is replaced only at initialization.
        cap=(th['p']-1)*th['c']**(th['p']-1)*(L.b-th['alpha'])/L.b
        th['K']=.5*cap
        res=minimize(L.objectif,donustur(th,L.b,tur),args=(tur,),jac=True,
                     method='L-BFGS-B',bounds=bounds,
                     options=dict(maxiter=maksiter,ftol=1e-11,gtol=2e-7,maxls=40))
        results.append(res)
    good=[r for r in results if r.success]
    if not good: raise ValueError('MLE yakınsamadı: '+str([r.message for r in results]))
    best=min(good,key=lambda r:r.fun)
    th=coz(best.x,L.b,tur)
    val,gradient=L.objectif(best.x,tur)
    return dict(parametreler=th,logL=-val*len(L.t),basari=bool(best.success),nit=int(best.nit),
                tur=tur,dallanma=dallanma(th,L.b),tam_cift=len(L.i),
                gradyan_sonsuz_norm=float(np.max(np.abs(gradient))),
                optimizer='L-BFGS-B; mu,n,c,alpha/b,p-1,D,q-1,(gamma); analytic gradient; n≤0.999999',
                sinirlar=bounds,x=best.x.tolist(),
                baslangic_sonuclari=[dict(basari=bool(r.success),logL=float(-r.fun*len(L.t)),nit=int(r.nit),mesaj=str(r.message)) for r in results],
                uzay_ayar_destegi='T ile aynı: olaylar CSEP maskede, kompansatör dış dikdörtgende; tam maskeli MLE değil',
                cekirdek='D_i=D*10^(gamma*(M-Mc)), q serbest' if tur=='ortak' else '(r²+d²)^(-q), d ve q serbest, gamma=0; LM biçimi, özgün parametreler değil')
