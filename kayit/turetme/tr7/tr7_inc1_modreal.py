# TR-7 İNCELEME-1 inceleme betiği (modreal.py), sürüm 2 için depoya kopyalandı; yalnız yapay veri. Ölçümler: İNCELEME-1 §E.
# Kullanım için İNCELEME-1 §E'deki tohumlara bakın; python3 -I -B ile koşulur.
import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import importlib; Y=importlib.import_module('tr7_onkayit_yapay'); import numpy as np
TUR=sys.argv[1]; A=float(sys.argv[2]); rng=np.random.default_rng(int(sys.argv[3])); NP=int(sys.argv[4]); W=Y.W_S; t=np.arange(W)
def paket():
    t0=600; f=np.interp(t,[t0-450,t0+450],[1/40,1/15]); ph=2*np.pi*np.cumsum(f)+rng.uniform(0,2*np.pi)
    return np.exp(-0.5*((t-t0)/250)**2)*np.cos(ph)
def faz(v):
    V=np.fft.fft(v); n=len(v); h=np.zeros(n); h[0]=1; h[1:(n+1)//2]=2
    if n%2==0: h[n//2]=1
    return np.cos(np.angle(np.fft.ifft(V*h)))
def stat(L,v,a,b):
    v=faz(v); best=-1
    for s in (1,-1):
        for lag in range(0,11):
            x=np.maximum(0,s*np.roll(v,lag))[a:b]; y=L[a:b]
            if x.std()>0: best=max(best,np.corrcoef(x,y)[0,1])
    return best
ok=0; det=0
for k in range(NP):
    v=paket(); bas=int(rng.integers(450,750)); a=max(0,bas-60); b=min(W,bas+360)
    m=np.zeros(W); e=np.arange(W)-bas; on=(e>=0)&(e<300); tap=np.minimum(1,np.minimum(e,300-e)/10)
    if TUR=='kilitli': m[on]=(np.maximum(0,np.roll(v,3))/np.abs(v).max())[on]*tap[on]
    elif TUR=='bagimsiz': m[on]=np.maximum(0,np.sin(2*np.pi*e[on]/20+rng.uniform(0,6.3)))*tap[on]
    else: m[on]=tap[on]
    env=np.zeros(Y.N); env[Y.R_S*int(Y.FS):(Y.R_S+W)*int(Y.FS)]=np.repeat(m,int(Y.FS))
    Ls=[]; ist=[]
    for i in range(3):
        cs=[]
        for c in range(3):
            ad=Y.bant_analitik(rng.standard_normal(Y.N)); ad/=np.sqrt(np.mean(ad.real**2))
            as_=Y.bant_analitik(rng.standard_normal(Y.N)*env); onn=env>0; as_/=np.sqrt(np.mean(as_.real[onn]**2))
            cs.append(Y.zarf1hz(np.abs(ad+A*as_))[:Y.R_S+W])
        C=np.sqrt(np.mean(np.array(cs)**2,0)); L,mm,s=Y.isle(C); Ls.append(L[Y.R_S:]); ist.append((L,Y.asimlar(L,mm,s)))
    det+=Y.tutarli(ist)
    Lk=np.median(np.array(Ls),0); o=stat(Lk,v,a,b)
    nul=[stat(Lk,np.roll(v,int(rng.integers(120,W-120))),a,b) for _ in range(200)]
    ok+=(1+sum(x>=o for x in nul))/201<=0.01
print(TUR,A,'p<=0.01 orani',ok/NP,'algilama',det/NP)
