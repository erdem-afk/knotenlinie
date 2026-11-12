import numpy as np, math
from scipy.stats import binom
exec(open('b2.py').read().split("R=20000")[0])
R=20000
print("Sabit yıllık CV modeli: phi = 1 + CV^2 N0")
PDt={}
for cv in (0.1,0.2,0.3):
    for N0 in (31.36,100,500,1000):
        phi=1+cv*cv*N0
        D,Ds=kume(R,N0,phi)
        PDt[(cv,N0)]=D.mean()
        print(f"CV {cv} N0 {N0} phi {phi:.1f} P(D) {D.mean():.4f}")
# Karışım: K=23; 5 küme yüksek N0 (sahte yok), 18 küme orta N0 (3 sahte geçerli) -> J=54
for cv in (0.1,0.2,0.3):
  for Nh,nh in ((1000,5),(500,5),(1000,8)):
    K=23; nm=K-nh
    Dh,_=kume(R*nh,Nh,1+cv*cv*Nh); Dm,Dsm=kume(R*nm,50,1+cv*cv*50)
    D=np.concatenate([Dh.reshape(R,nh),Dm.reshape(R,nm)],1)
    Ds=Dsm.reshape(R,nm*3); valid=np.ones_like(Ds)
    a=yordam(D,Ds,valid,K); a5=(D.sum(1)>=ckp(K,.5)).mean()
    # J<30 kuralları karşılaştırması: J=nm*3
    print(f"CV {cv} yüksek N0 {Nh} x{nh}, orta N0 50 x{nm} (J={3*nm}): alfa p0=.50 {a5:.4f}  kalibre {a:.4f}")
