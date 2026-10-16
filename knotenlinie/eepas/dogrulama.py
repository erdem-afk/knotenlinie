"""Günlük geçmiş dondurma, aynı dikdörtgen ızgarada iç doğrulama."""
from __future__ import annotations

import numpy as np
import pandas as pd

from knotenlinie.etas import model as ETAS
from .model import (EEPAS, zaman_gun, katalog_dizileri, gaussian_hucre,
                    kutu_izgara, zaman_kutlesi, buyukluk_kutlesi, eta, LN10, GUN, EPOCH)
from .janus import ETASModel, Janus, bilgi_kazanci


def gunluk_integraller(model, gecmis, t0, t1, m_aralik):
    """Her günün başındaki tarihçeden kutu integrali; çekirdek uzayı bir kez hesaplanır."""
    if isinstance(model,Janus):
        return (model.agirlik*gunluk_integraller(model.eepas,gecmis,t0,t1,m_aralik)+
                (1-model.agirlik)*gunluk_integraller(model.etas,gecmis,t0,t1,m_aralik))
    days = np.arange(t0,t1,1.)
    end = np.minimum(days+1,t1)
    m0 = model.p.m0 if isinstance(model,EEPAS) else model.m0
    pt,pm,pl,pa = katalog_dizileri(gecmis.loc[gecmis.mw>=m0])
    eligible = pt[None,:] < days[:,None]
    if isinstance(model,EEPAS):
        p = model.p
        sig = p.sigmaA*10**(p.bA*pm/2)
        x,y = model.met.km(pl,pa)
        sp = gaussian_hucre(x,y,sig,kutu_izgara(model.kutu),model.met)[0]
        mg = buyukluk_kutlesi(m_aralik,pm,p)[0]
        tm = zaman_kutlesi(days[:,None]-pt,end[:,None]-pt,pm,p)*eligible
        lo,hi = m_aralik
        bgm = np.exp(-p.b*LN10*(lo-p.m0))*(-np.expm1(-p.b*LN10*(hi-lo)))
        return p.olcek*(p.mu*p.r0*(end-days)*bgm+(1-p.mu)*(tm@(sp*mg*eta(pm,p))))
    mu,K,c,alpha,p,D,q,gamma = model.theta
    di = ETAS.mekan_olcegi(D,gamma,pm,model.m0)
    sp = ETAS.mekan_kutu_integrali(pl,pa,di,q,model.kutu,metrik=model.met)
    low,high = np.maximum(days[:,None]-pt,0),np.maximum(end[:,None]-pt,0)
    tm = (ETAS._omori_ilke(high,c,p)[0]-ETAS._omori_ilke(low,c,p)[0])*eligible
    lo,hi = m_aralik
    bgm = np.exp(-model.b*LN10*(lo-model.m0))*(-np.expm1(-model.b*LN10*(hi-lo)))
    return (mu*(end-days)+tm@(K*10**(alpha*(pm-model.m0))*sp))*bgm


def olay_hucreleri(hedefler, kutu, dx=.2, dm=.1, m_alt=4.95, m_ust=9.05):
    """Izgara sol-alt köşeden sabit dx; son hücre kutu kenarında kesilir."""
    la0,la1,lo0,lo1 = kutu
    x = lo0+np.floor((hedefler.boylam.to_numpy()-lo0)/dx+1e-10)*dx
    y = la0+np.floor((hedefler.enlem.to_numpy()-la0)/dx+1e-10)*dx
    m = m_alt+np.floor((hedefler.mw.to_numpy()-m_alt)/dm+1e-10)*dm
    g = pd.DataFrame({'boylam_min':x,'boylam_max':np.minimum(x+dx,lo1),
                      'enlem_min':y,'enlem_max':np.minimum(y+dx,la1)})
    return g,np.column_stack([m,np.minimum(m+dm,m_ust)])


def ic_dogrulama(modeller, katalog, baslangic, bitis, m_aralik=(4.95,9.05), dx=.2):
    """2011–2015 günlük binned-Poisson IG; öncesinde gelen yeni öncüler kullanılabilir."""
    t0,t1 = zaman_gun([baslangic,bitis])
    if pd.Timestamp(baslangic)<pd.Timestamp('2011-01-01',tz='UTC') or pd.Timestamp(bitis)>pd.Timestamp('2016-01-01',tz='UTC'):
        raise ValueError('Yalnız 2011–2015 iç doğrulaması')
    history = katalog.loc[katalog.zaman<pd.Timestamp(bitis)].copy()
    target = history.loc[(history.zaman>=pd.Timestamp(baslangic))&
                         (history.mw>=m_aralik[0])&(history.mw<m_aralik[1])].reset_index(drop=True)
    cells,bins = olay_hucreleri(target,next(iter(modeller.values())).kutu,dx=dx,
                              m_alt=m_aralik[0],m_ust=m_aralik[1])
    totals = {ad:float(gunluk_integraller(mod,history,t0,t1,m_aralik).sum())
              for ad,mod in modeller.items()}
    lambdas = {ad:np.zeros(len(target)) for ad in modeller}
    for i,row in target.iterrows():
        day = row.zaman.floor('D')
        past = history.loc[history.zaman<day]
        for ad,mod in modeller.items():
            lambdas[ad][i] = mod.beklenen(day,day+GUN,past,cells.iloc[[i]],bins[i])[0,0]
    table = {}
    for ad in modeller:
        table[ad] = {'beklenen':totals[ad],'logL':float(np.log(lambdas[ad]).sum()-totals[ad]),
                     'etas_karsisinda':bilgi_kazanci(lambdas[ad],lambdas['ETAS'],totals[ad],totals['ETAS'])}
    return {'n':len(target),'baslangic':str(baslangic),'bitis_haric':str(bitis),
            'dx':dx,'dm':.1,'m_aralik':list(m_aralik),'kutu':list(next(iter(modeller.values())).kutu),
            'tablo':table,'GEAR1':'GEAR1 kıyası bu sürümde yok',
            'olay_beklenen':{k:v.tolist() for k,v in lambdas.items()}}
