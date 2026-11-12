"""TR-7 ön kayıt §7.1: yapay durağan Gauss gürültüsünde algılayıcının beklenen davranışı.

Yalnız numpy; gerçek dalga formu yok. Süzgeç FFT ile, 4 kutuplu Butterworth bant geçirenin ileri-geri genlik
yanıtı (|H|^2) olarak; 20 Hz örnekleme (2-8 Hz bandı için yeterli). Zarf, 1 sn ortalama, 3 bileşen karesel ortalama,
5 sn kayan ortalama, log10; başvuru 3600 sn, W 1900 sn; aşım m + KSIG*sigma, boşluk köprüleme BOSLUK sn, en kısa
açıklık KMIN sn, en az NUST aşım örneği; >=3 istasyon +-20 sn örtüşme ve >=3 çiftte zarf ilişkisi >=0,5 (gecikme
<=10 sn). Genlik A: tremorun etkin (zarf>0) örneklerinde bileşen başına 2-8 Hz RMS / gürültünün bileşen başına
2-8 Hz RMS'i. Tremor: 300 sn, 20 sn periyotlu yarım sinüs modülasyonu (MOD=yarim) ya da sabit (MOD=sabit), 10 sn
kenar yumuşatma; her istasyon ve bileşende bağımsız gürültü gerçekleşmesi, ortak zarf.

Kullanım: [KSIG=4 BOSLUK=20 KMIN=30 NUST=15 MOD=yarim] python3 -I -B tr7_onkayit_yapay.py <n_ist> <n_pencere> <tohum>
"""
import numpy as np, sys
FS=20.0; R_S=3600; W_S=1900; N=int((R_S+W_S)*FS)
f=np.fft.rfftfreq(N,1/FS)
def bw2(f,lo,hi,n=4):
    with np.errstate(divide='ignore'):
        hp=1/(1+(lo/np.maximum(f,1e-9))**(2*n)); lp=1/(1+(f/hi)**(2*n))
    return hp*lp            # |H|^2 -> sıfır fazlı (ileri-geri) 4 kutuplu
H28=bw2(f,2,8)
def analitik(x_fft_filtered):
    X=x_fft_filtered.copy(); X[1:]*=2; 
    full=np.zeros(N,complex); full[:len(X)]=X
    if N%2==0: full[len(X)-1]/=2
    return np.fft.ifft(full)
def bant_analitik(x): return analitik(np.fft.rfft(x)*H28)
def zarf1hz(env): return env[:int(len(env)//FS*FS)].reshape(-1,int(FS)).mean(1)
def isle(c):  # c: 1 Hz birleşik zarf
    k=np.ones(5)/5; L=np.log10(np.convolve(c,k,'same'))
    r=L[5:R_S-5]; m=np.median(r); s=1.4826*np.median(np.abs(r-m))
    return L,m,s
BOSLUK=int(__import__('os').environ.get('BOSLUK','20')); KMIN=int(__import__('os').environ.get('KMIN','30')); NUST=int(__import__('os').environ.get('NUST','15'))
KSIG=float(__import__('os').environ.get('KSIG','4'))
def asimlar(L,m,s,k=None):
    k=KSIG if k is None else k
    w=np.flatnonzero(L[R_S:]>m+k*s); out=[]
    if len(w)==0: return out
    a=w[0]; b=w[0]; n=1
    for x in w[1:]:
        if x-b-1<=BOSLUK: b=x; n+=1
        else:
            if b-a+1>=KMIN and n>=NUST: out.append((a,b+1))
            a=b=x; n=1
    if b-a+1>=KMIN and n>=NUST: out.append((a,b+1))
    return out
def tutarli(ist):  # ist: [(L, asimlar)]
    ivs=[(k,a,b) for k,(L,ax) in enumerate(ist) for a,b in ax]
    for k,a,b in ivs:
        grp={k2 for k2,a2,b2 in ivs if a2<=b+20 and b2>=a-20}
        if len(grp)<3: continue
        aa=[x for x in ivs if x[0] in grp]
        lo=max(0,min(x[1] for x in aa)-60); hi=min(W_S,max(x[2] for x in aa)+60)
        g=sorted(grp); n_ok=0
        for i1 in range(len(g)):
            for i2 in range(i1+1,len(g)):
                x=ist[g[i1]][0][R_S+lo:R_S+hi]; y=ist[g[i2]][0][R_S+lo:R_S+hi]
                best=-1
                for lag in range(-10,11):
                    if lag>=0: xx,yy=x[lag:],y[:len(y)-lag]
                    else: xx,yy=x[:lag],y[-lag:]
                    if len(xx)>10 and xx.std()>0 and yy.std()>0: best=max(best,np.corrcoef(xx,yy)[0,1])
                if best>=0.5: n_ok+=1
        if n_ok>=3: return True
    return False
MOD=__import__('os').environ.get('MOD','yarim')
def tremor_zarf(rng,bas,sure=300,per=20.0):
    t=np.arange(N)/FS; e=np.zeros(N)
    tt=t-(R_S+bas); msk=(tt>=0)&(tt<sure)
    e[msk]=(np.maximum(0,np.sin(2*np.pi*tt[msk]/per)) if MOD=='yarim' else np.ones(msk.sum()))*np.minimum(1,np.minimum(tt[msk],sure-tt[msk])/10)
    return e
def kos(n_ist,A_list,n_pen,seed,tremor=True):
    rng=np.random.default_rng(seed); sonuc={A:0 for A in A_list}
    for p in range(n_pen):
        bas=rng.integers(60,W_S-360)
        env=tremor_zarf(rng,bas)
        # birim gerçek RMS: zarf ölçeği; gürültü bant RMS'i 1'e normalize
        a_d=[];a_s=[]
        for i in range(n_ist):
            dd=[];ss=[]
            for c in range(3):
                x=rng.standard_normal(N); ad=bant_analitik(x)
                ad/=np.sqrt(np.mean(ad.real**2))
                y=rng.standard_normal(N)*env; as_=bant_analitik(y)
                on=env>0.0
                # tremor 'genlik' tanımı: bölüm boyunca bant RMS (zarf>0 iken)
                as_/=np.sqrt(np.mean(as_.real[on]**2)) if on.any() else 1
                dd.append(ad);ss.append(as_)
            a_d.append(dd);a_s.append(ss)
        for A in A_list:
            ist=[]
            for i in range(n_ist):
                cs=[zarf1hz(np.abs(a_d[i][c]+A*a_s[i][c]))[:R_S+W_S] for c in range(3)]
                cc=np.sqrt(np.mean(np.array(cs)**2,0))
                L,m,s=isle(cc); ist.append((L,asimlar(L,m,s)))
            sonuc[A]+=tutarli(ist)
    return {A:v/n_pen for A,v in sonuc.items()}
if __name__=='__main__':
    n_ist=int(sys.argv[1]); n_pen=int(sys.argv[2]); seed=int(sys.argv[3])
    A=[0.0]+[round(10**(j/40),3) for j in range(-16,1)]
    print(n_ist,n_pen,kos(n_ist,A,n_pen,seed))
