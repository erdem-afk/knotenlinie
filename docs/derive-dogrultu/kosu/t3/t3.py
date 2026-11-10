# T3 puanlama, T3-KURAL.md birebir; tablo T3-TABLO.json (sha d44303ed…)
import json,numpy as np,hashlib,sys
from scipy.stats import norm
assert hashlib.sha256(open('T3-TABLO.json','rb').read()).hexdigest().startswith('d44303ed')
T=json.load(open('T3-TABLO.json'))['tabla' if 0 else 'tablo']
rng=np.random.default_rng(20261110)
def skor(sig,T=T):
    o=[]
    for t in T:
        Da=t['v']*1e-3*(t['t_olay']-t['t_last']); Ds=10**(-1.70+1.04*np.log10(t['SRL']))
        y=np.log10(t['D_obs'])
        o.append(dict(seg=t['segment'],olay=t['olay'],blok=t['blok'],D_obs=t['D_obs'],D_acik=round(Da,3),D_olcek=round(Ds,3),R=t['D_obs']/Da,
                      lLa=norm.logpdf(y,np.log10(Da),sig),lLs=norm.logpdf(y,np.log10(Ds),sig)))
    return o
def boot(o,anahtar,n=10000):
    B=sorted(set(x[anahtar] for x in o)); d={b:sum(x['lLa']-x['lLs'] for x in o if x[anahtar]==b) for b in B}
    v=np.array([d[b] for b in B]); s=[v[rng.integers(0,len(v),len(v))].sum() for _ in range(n)]
    return dict(n_blok=len(B),bloklar={b:round(d[b],2) for b in B},ci90=np.percentile(s,[5,95]).tolist())
R={}
for sig in [0.25,0.15,0.35]:
    o=skor(sig); dL=sum(x['lLa']-x['lLs'] for x in o)
    R[f'sigma_{sig}']=dict(dL=dL,segmentler=o,boot_ikiz_tek_olay=boot(o,'blok'),boot_ikiz_iki_olay=boot(o,'olay'))
o=R['sigma_0.25']['segmentler']; Rr=np.array([x['R'] for x in o])
n_seg=len(o); n_olay_tek=len(set(x['blok'] for x in o)); n_olay_iki=len(set(x['olay'] for x in o))
R['kapi']=dict(n_segment=n_seg,n_bagimsiz_olay_ikiz_tek=n_olay_tek,n_olay_ikiz_iki=n_olay_iki,
              ates_ana=bool(n_seg>=6 and n_olay_tek>=3),ates_ikiz_iki=bool(n_seg>=6 and n_olay_iki>=3))
a=R['sigma_0.25']
R['hukum_ana']='veri yetersiz' if not R['kapi']['ates_ana'] else ('H1' if a['dL']>0 and a['boot_ikiz_tek_olay']['ci90'][0]>0 else 'H0')
R['hukum_ikiz_iki_olay_bilgi']=('H1' if a['dL']>0 and a['boot_ikiz_iki_olay']['ci90'][0]>0 else 'H0') if R['kapi']['ates_ikiz_iki'] else 'veri yetersiz'
R['R_medyan']=float(np.median(Rr)); R['R_aralik']=[float(Rr.min()),float(Rr.max())]; R['R_ge1_pay']=float(np.mean(Rr>=1))
json.dump(R,open('t3_sonuc.json','w'),ensure_ascii=False,indent=1,default=float)
for x in o: print(f"{x['seg'][:22]:22s} Dobs {x['D_obs']:.2f} Dacik {x['D_acik']:.2f} Dolcek {x['D_olcek']:.2f} R {x['R']:.2f}")
for s in [0.25,0.15,0.35]: print(s,round(R[f'sigma_{s}']['dL'],2),R[f'sigma_{s}']['boot_ikiz_tek_olay'],R[f'sigma_{s}']['boot_ikiz_iki_olay']['ci90'])
print(R['kapi'],R['hukum_ana'],R['hukum_ikiz_iki_olay_bilgi'],R['R_medyan'],R['R_aralik'],R['R_ge1_pay'])
