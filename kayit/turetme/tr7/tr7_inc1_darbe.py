# TR-7 İNCELEME-1 inceleme betiği (darbe.py), sürüm 2 için depoya kopyalandı; yalnız yapay veri. Ölçümler: İNCELEME-1 §E.
# Kullanım için İNCELEME-1 §E'deki tohumlara bakın; python3 -I -B ile koşulur.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import importlib; Y=importlib.import_module('tr7_onkayit_yapay'); import numpy as np
TUR=sys.argv[1]; A=float(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); NP=int(sys.argv[4]); RISE=float(os.environ.get('RISE','0'))
t=np.arange(Y.N)/Y.FS
def zarf(bas):
    tt=t-(Y.R_S+bas); e=np.zeros(Y.N); on=(tt>=0)&(tt<300)
    if TUR=='yarim': e[on]=np.maximum(0,np.sin(2*np.pi*tt[on]/float(os.environ.get('PER','20'))))*np.minimum(1,np.minimum(tt[on],300-tt[on])/10)
    elif TUR=='patlama':
        k=0
        while k<300:
            k+=rng.exponential(15); d=rng.uniform(5,15)
            if k+d>300: break
            m=(tt>=k)&(tt<k+d); r=np.ones(m.sum()) if RISE==0 else np.minimum(1,np.minimum(tt[m]-k,k+d-tt[m])/RISE)
            e[m]=r; k+=d
    elif TUR=='deprem':  # P (c_p/4) then S at SP s, 5 s e-fold decay
        SP=float(os.environ.get('SP','3')); tp=tt; e=np.where(tt>=0,0.25*np.exp(-np.maximum(tt,0)/5),0)+np.where(tt>=SP,np.exp(-np.maximum(tt-SP,0)/5),0)
    return e
dar=0; tot=0; atil=0; alg=0
for p in range(NP):
    bas=int(rng.integers(60,Y.W_S-360)); env=zarf(bas); ist=[]; flags=[]
    for i in range(3):
        cs=[]
        for c in range(3):
            ad=Y.bant_analitik(rng.standard_normal(Y.N)); ad/=np.sqrt(np.mean(ad.real**2))
            as_=Y.bant_analitik(rng.standard_normal(Y.N)*env); on=env>1e-3; as_/=np.sqrt(np.mean(as_.real[on]**2))
            cs.append(Y.zarf1hz(np.abs(ad+A*as_))[:Y.R_S+Y.W_S])
        C=np.sqrt(np.mean(np.array(cs)**2,0)); L,m,s=Y.isle(C); ax=Y.asimlar(L,m,s); ist.append((L,ax))
        fl=[]
        for a,b in ax:
            seg=C[Y.R_S+a:Y.R_S+b]; k=int(np.argmax(seg)); tp=Y.R_S+a+k; cp=C[tp]
            pre=C[tp-2:tp]; post=C[tp+1:tp+21]
            fl.append(bool((pre<=cp/8).any() and (post<=cp/2).any()))
        flags.append(fl)
    if Y.tutarli(ist):
        alg+=1
        # station is darbe if its (largest) exceedance flagged
        st=[any(f) for f in flags if f]
        if st and sum(st)>=len(st)/2: atil+=1
print(TUR,A,os.environ.get('RISE',''),os.environ.get('PER',''),os.environ.get('SP',''),'alg',alg,'/',NP,'darbe_atilan',atil)
