# TR-7 İNCELEME-1 inceleme betiği (d10b.py), sürüm 2 için depoya kopyalandı; yalnız yapay veri. Ölçümler: İNCELEME-1 §E.
# Kullanım için İNCELEME-1 §E'deki tohumlara bakın; python3 -I -B ile koşulur.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
mod=os.environ.get('MOD','sabit')
import importlib; Y=importlib.import_module('tr7_onkayit_yapay')
import numpy as np
A=float(sys.argv[1]); rng=np.random.default_rng(int(sys.argv[2])); ests=[]; Ilen=[]
for p in range(int(sys.argv[3])):
    bas=rng.integers(60,Y.W_S-360); env=Y.tremor_zarf(rng,bas)
    Cs=[];Ls=[];axs=[]
    for i in range(3):
        cs=[]
        for c in range(3):
            ad=Y.bant_analitik(rng.standard_normal(Y.N)); ad/=np.sqrt(np.mean(ad.real**2))
            as_=Y.bant_analitik(rng.standard_normal(Y.N)*env); on=env>0; as_/=np.sqrt(np.mean(as_.real[on]**2))
            cs.append(Y.zarf1hz(np.abs(ad+A*as_))[:Y.R_S+Y.W_S])
        C=np.sqrt(np.mean(np.array(cs)**2,0)); L,m,s=Y.isle(C); ax=Y.asimlar(L,m,s); Cs.append(C); axs.append(ax)
    allax=[x for ax in axs for x in ax]
    if not allax: continue
    lo=max(0,min(a for a,b in allax)); hi=min(Y.W_S,max(b for a,b in allax)); Ilen.append(hi-lo)
    a=[np.sqrt(max(0,np.mean(C[Y.R_S+lo:Y.R_S+hi]**2)-np.mean(C[:Y.R_S]**2))*2/np.pi) for C in Cs]
    ests.append(np.median(a)/A)
print(mod,A,len(ests),'median est/A',round(float(np.median(ests)),3),'q05-q95',np.round(np.quantile(ests,[.05,.95]),3),'|I| med',np.median(Ilen))
