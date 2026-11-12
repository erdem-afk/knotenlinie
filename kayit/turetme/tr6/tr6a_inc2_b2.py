# H0 altında gerçek oy ile sahte oyların ortak veri yüzünden ilişkisi ve tam kalibrasyon yordamının α'sı (yapay).
import math, numpy as np
from scipy.stats import binom
rng=np.random.default_rng(7)
pi=335/2131
NMAX=40000
k_b=np.full(NMAX+1,-1)
# b_dus(n): en büyük b, F(b;n,pi)<=0.5
for n in range(1,NMAX+1):
    m=int(n*pi); 
    b=int(binom.ppf(0.5,n,pi))  # en küçük b: F>=0.5
    while b>=0 and binom.cdf(b,n,pi)>0.5+1e-12: b-=1
    while binom.cdf(b+1,n,pi)<=0.5+1e-12: b+=1
    k_b[n]=b
B=[-2891,-2556,-2221,-1826,-1095,-1035,-760,-700,-425,-365,-30,30,365]
seg=list(zip(B[:-1],B[1:]))
def idx(a,b): return [i for i,(x,y) in enumerate(seg) if x>=a and y<=b]
W={'on':idx(-1826,-30),'son':idx(30,365),
   's1o':idx(-2221,-425),'s1s':idx(-365,-30),
   's2o':idx(-2556,-760),'s2s':idx(-700,-365),
   's3o':idx(-2891,-1095),'s3s':idx(-1035,-700)}
def kume(M,N0,phi):
    L=np.array([(y-x)/365.25 for x,y in seg])
    if phi==1: g=np.ones((M,len(seg)))
    else:
        kk=N0/(phi-1); g=rng.gamma(kk*L,1/(kk*L),(M,len(seg)))
    c=rng.poisson(N0*L*g)
    if seg[10]==(-30,30): pass
    def oy(o,s):
        a=c[:,W[o]].sum(1); b=c[:,W[s]].sum(1); n=a+b
        return ((n>0)&(b<=k_b[np.minimum(n,NMAX)])).astype(int)
    return oy('on','son'), np.stack([oy('s1o','s1s'),oy('s2o','s2s'),oy('s3o','s3s')],1)
C={}
def ckp(K,p): 
    key=(K,p)
    if key not in C:
        C[key]=next(x for x in range(K+2) if binom.sf(x-1,K,p)<=0.05+1e-12)
    return C[key]
def yordam(D,Ds,valid,K,floor=0.50,Jmin=30,label_rule=False):
    X=D.sum(1); S=(Ds*valid).sum(1); J=valid.sum(1)
    res=np.zeros(len(X),bool)
    for r in range(len(X)):
        if J[r]>=Jmin: p0=max(int(round(floor*100)), -(-100*S[r]//J[r]))
        else: p0=int(round(floor*100)) if not label_rule else int(round(floor*100))
        if p0>60: continue
        res[r]= X[r]>=ckp(K,p0/100)
    return res.mean()
R=20000
for N0,phi in ((31.36,1),(31.36,3),(31.36,5),(100,3),(100,5),(500,5)):
    for K in (23,28):
        D,Ds=kume(R*K,N0,phi); D=D.reshape(R,K); Ds=Ds.reshape(R,K,3)
        valid=np.ones((R,K,3),int)
        # korelasyon: gerçek D ile sahte j=1 D'
        cor=np.corrcoef(D.ravel(),Ds[:,:,0].ravel())[0,1]
        pD=D.mean(); pDs=Ds.mean()
        a_full=yordam(D,Ds.reshape(R,K*3),valid.reshape(R,K*3),K)
        # bağımsızlık varsayımıyla (karıştırılmış sahte)
        perm=rng.permutation(R)
        a_ind=yordam(D,Ds[perm].reshape(R,K*3),valid.reshape(R,K*3),K)
        a_p05=(D.sum(1)>=ckp(K,0.5)).mean()
        print(f"N0 {N0} phi {phi} K {K}: P(D) {pD:.4f} P(D') {pDs:.4f} kor(D,D'1) {cor:+.3f} | alfa p0=.50 {a_p05:.4f} kalibre-ortak {a_full:.4f} kalibre-bagimsiz {a_ind:.4f}")
