"""Sabit dış öncülere koşullu EEPAS Poisson kataloğu; gizli ebeveynler ayarda yok."""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import special, stats

from .model import (katalog_dizileri, zaman_kutlesi, buyukluk_kutlesi,
                    buyukluk_yogunlugu, eta, gaussian_hucre, kutu_izgara, EPOCH, GUN, LN10)


def _kesik_normal(rng, ort, sd, lo, hi, n):
    return stats.truncnorm.rvs((lo-ort)/sd,(hi-ort)/sd,loc=ort,scale=sd,
                               size=n,random_state=rng)


def uret(model, gecmis, t0, t1, m_aralik, seed=472):
    """Her kaynaktan bağımsız Poisson sayımı; çocuklar yeni öncü yapılmaz."""
    p,met = model.p,model.met
    if t1<=t0 or m_aralik[1]<=m_aralik[0]:
        raise ValueError('Pozitif pencere gerekli')
    if len(model.arka_plan.x):
        raise ValueError('Sentetik üretici yalnız düzgün PPE destekliyor')
    rng = np.random.default_rng(seed)
    pt,pm,pl,pa = katalog_dizileri(gecmis.loc[gecmis.mw>=p.m0])
    x,y = met.km(pl,pa)
    x0,x1,y0,y1 = met.kutu_km()
    sig = p.sigmaA*10**(p.bA*pm/2)
    tm = zaman_kutlesi(t0-pt,t1-pt,pm,p)
    mg = buyukluk_kutlesi(m_aralik,pm,p)[0]
    sp = gaussian_hucre(x,y,sig,kutu_izgara(model.kutu),met)[0]
    means = p.olcek*(1-p.mu)*eta(pm,p)*tm*mg*sp
    rows = []
    lo,hi = m_aralik
    bgmass = np.exp(-p.b*LN10*(lo-p.m0))*(-np.expm1(-p.b*LN10*(hi-lo)))
    nb = rng.poisson(p.olcek*p.mu*p.r0*(t1-t0)*bgmass)
    mb = lo-np.log1p(-rng.uniform(size=nb)*(-np.expm1(-p.b*LN10*(hi-lo))))/(p.b*LN10)
    xb,yb = rng.uniform(x0,x1,nb),rng.uniform(y0,y1,nb)
    lob,lab = met.derece(xb,yb)
    rows.extend(zip(rng.uniform(t0,t1,nb),mb,lob,lab))
    for i,n in enumerate(rng.poisson(means)):
        if n==0:
            continue
        low = max(t0-pt[i],p.gecikme,np.finfo(float).tiny)
        logdt = _kesik_normal(rng,p.aT+p.bT*pm[i],p.sigmaT,np.log10(low),np.log10(t1-pt[i]),n)
        # Telafili g'nin ters CDF'si: çok ince trapez, serbest parametreden bağımsız RNG.
        grid = np.linspace(lo,hi,8193)
        dens = buyukluk_yogunlugu(grid,pm[i],p)
        cdf = np.r_[0,np.cumsum((dens[:-1]+dens[1:])/2*np.diff(grid))]
        mags = np.interp(rng.uniform(0,cdf[-1],n),cdf,grid)
        xs = _kesik_normal(rng,x[i],sig[i],x0,x1,n)
        ys = _kesik_normal(rng,y[i],sig[i],y0,y1,n)
        lon,lat = met.derece(xs,ys)
        rows.extend(zip(pt[i]+10**logdt,mags,lon,lat))
    df = pd.DataFrame(rows,columns=['gun','mw','boylam','enlem'])
    df['zaman'] = EPOCH+pd.to_timedelta(df.pop('gun'),unit='D')
    df['derinlik'] = 10.0
    return df.sort_values('zaman').reset_index(drop=True)
