# TR-7 İNCELEME-1 inceleme betiği (modv.py), sürüm 2 için depoya kopyalandı; yalnız yapay veri. Ölçümler: İNCELEME-1 §E.
# Kullanım için İNCELEME-1 §E'deki tohumlara bakın; python3 -I -B ile koşulur.
"""TR-7 ön kayıt §6.4: modülasyon ölçüsünün yapay sınaması (1 Hz düzeyinde; yalnız numpy, gerçek veri yok).

Yapay yüzey dalgası: 1900 sn W içinde t0 = 600 sn merkezli, Gauss zarflı (sd 250 sn), periyodu 40 sn'den 15 sn'ye
kayan (dispersiyonlu) paket. Tremor 300 sn: 'kilitli' (max(0, v) ile 3 sn gecikmeli), 'bagimsiz' (20 sn sabit
periyotlu yarım sinüs, rastgele faz), 'sabit', 'rastgele' (Poisson patlamaları, 5-15 sn). c = sqrt(1 + (A m)^2) (1 +
0,1 e), L = log10(5 sn kayan ortalama). Ölçü: küme aralığında [bas-60, bas+360] L ile max(0, s cos(faz(v)(t-lag)))
arasındaki Pearson ilişkisinin s in {+,-}, lag 0..10 sn üzerinden en büyüğü; boş dağılım v'nin [120, W-120] sn
dairesel kaydırmaları (burada 200; koşuda 1000). Çıktı: p <= 0,01 oranı.
Kullanım: python3 -I -B tr7_onkayit_modulasyon.py <tur> <tohum> <A> <n_pencere>
"""
import numpy as np, sys, os
SIGNS=tuple(int(x) for x in os.environ.get('SIGNS','1,-1').split(','))
LAGMAX=int(os.environ.get('LAGMAX','10'))
W=1900; rng=np.random.default_rng(int(sys.argv[2])); TUR=sys.argv[1]; A=float(sys.argv[3]); NP=int(sys.argv[4])
t=np.arange(W)
def paket(rng):
    t0=600; f=np.interp(t,[t0-450,t0+450],[1/40,1/15]); ph=2*np.pi*np.cumsum(f)+rng.uniform(0,2*np.pi)
    return np.exp(-0.5*((t-t0)/250)**2)*np.cos(ph)
def faz(v):
    V=np.fft.fft(v); n=len(v); h=np.zeros(n); h[0]=1; h[1:(n+1)//2]=2
    if n%2==0: h[n//2]=1
    return np.cos(np.angle(np.fft.ifft(V*h)))
def stat(L,v,a,b):
    v=faz(v)
    best=-1
    for s in SIGNS:
        for lag in range(0,LAGMAX+1):
            x=np.maximum(0,s*np.roll(v,lag))[a:b]; y=L[a:b]
            if x.std()>0: best=max(best,np.corrcoef(x,y)[0,1])
    return best
ok=0
for k in range(NP):
    v=paket(rng); bas=int(rng.integers(450,750)); a=max(0,bas-60); b=min(W,bas+360)
    m=np.zeros(W); e=np.arange(W)-bas; on=(e>=0)&(e<300); tap=np.minimum(1,np.minimum(e,300-e)/10)
    if TUR=='kilitli': m[on]=(np.maximum(0,np.roll(v,3))/np.abs(v).max())[on]*tap[on]; m/=np.sqrt(np.mean(m[on]**2))
    elif TUR=='bagimsiz': m[on]=np.maximum(0,np.sin(2*np.pi*e[on]/20+rng.uniform(0,6.3)))*tap[on]; m/=np.sqrt(np.mean(m[on]**2))
    elif TUR=='rastgele':
        for b0 in np.flatnonzero(rng.random(300)<1/15): m[bas+b0:bas+b0+int(rng.integers(5,15))]=1
        m[~on]=0; m[on]*=tap[on]
    else: m[on]=tap[on]
    c=np.sqrt(1+(A*m)**2)*(1+0.1*rng.standard_normal(W))
    L=np.log10(np.convolve(c,np.ones(5)/5,'same'))
    o=stat(L,v,a,b)
    nul=[stat(L,np.roll(v,int(rng.integers(120,W-120))),a,b) for _ in range(200)]
    p=(1+sum(x>=o for x in nul))/201
    ok+=p<=0.01
print(TUR,A,ok/NP)
