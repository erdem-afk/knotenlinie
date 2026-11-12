import json, math, numpy as np
from scipy.stats import binom, poisson
d=json.load(open('../kopya/tr6a_onkayit_sayilar.json'))
def c(K,p0): 
    for x in range(K+2):
        if binom.sf(x-1,K,p0)<=0.05+1e-12: return x
def h(K):
    hs=[x for x in range(K+1) if binom.cdf(x,K,0.75)<=0.05]; return max(hs) if hs else -1
bad=0
for r in d['binom']:
    K=r['K']; cc=c(K,.5)
    if cc!=r['kritik_H1'] or h(K)!=r['esik_H0'] or abs(binom.sf(cc-1,K,.75)-r['guc_p075'])>6e-5: bad+=1;print('binom',K)
g=d['p0_izgarasi']
for p0 in g:
    P=float(p0); tab={}
    for K in range(23,81):
        cc=c(K,P); pw=binom.sf(cc-1,K,.75); tab[K]=pw
        t=g[p0]['tablo'][str(K)]
        if cc!=t['c'] or abs(pw-t['guc'])>6e-5 or abs(binom.sf(cc-1,K,P)-t['alfa'])>6e-5: bad+=1; print('grid',p0,K)
    for Kk in range(23,81):
        u=[k for k in range(23,Kk+1) if tab[k]>=0.8]
        kh=max(u) if u else Kk
        if g[p0]['testere'][str(Kk)]['K_hukum']!=kh: bad+=1; print('testere',p0,Kk)
    ilk=next((K for K in range(23,81) if tab[K]>=.8),None)
    kal=next((K for K in range(23,81) if all(tab[k]>=.8 for k in range(K,81))),None)
    if (ilk,kal)!=(g[p0]['ilk_K_guc08'],g[p0]['kalici_K_guc08']): bad+=1; print('ilk',p0,ilk,kal)
    # near-boundary powers
    nb=[(K,round(tab[K],4)) for K in range(23,81) if abs(tab[K]-0.8)<0.005]
    if nb: print('sinira yakin guc',p0,nb)
print('bad',bad)
# kalici beyond 80? check K up to 200 for p0 0.59,0.60
for P in (0.59,0.60):
    print(P,[K for K in range(23,201) if binom.sf(c(K,P)-1,K,.75)<0.8][-3:])
# Poisson P(D)
pi=335/2131
def PD(N0,pi=pi,Ton=1796/365.25,Ts=335/365.25):
    lam=N0*(Ton+Ts); ns=np.arange(max(1,int(lam-15*math.sqrt(lam)-10)),int(lam+15*math.sqrt(lam)+20))
    tot=0;tota=0
    for n in ns:
        k=np.arange(0,n+1); F=binom.cdf(k,n,pi); b=k[F<=0.5+1e-12]
        w=poisson.pmf(n,lam)
        if len(b): tot+=w*binom.cdf(b.max(),n,pi)
        S=binom.sf(k-1,n,pi); a=k[S<=0.5+1e-12]
        if len(a): tota+=w*binom.sf(a.min()-1,n,pi)
    return tot,tota
for N0 in (17.08,31.36,50,111.2,300):
    pd,pa=PD(N0); print(N0,round(pd,4),round(pa,4), 'alfaK23',round(binom.sf(15,23,pd),4))
