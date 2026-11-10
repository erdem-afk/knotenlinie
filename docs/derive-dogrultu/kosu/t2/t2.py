# T2 koşusu, T2-KURAL.md (dondurulmuş cda6638) birebir.
import numpy as np, json, glob, csv, sys, datetime as dt, xml.etree.ElementTree as ET
import numba, shapefile
from sklearn.mixture import GaussianMixture
from scipy.stats import spearmanr, norm
V=sys.argv[1]; EDSF=sys.argv[2]; OUT=sys.argv[3]
rng=np.random.default_rng(20261110)
MTH=2.2
def yil(s):
    s=s.replace('Z','')
    d=dt.datetime.fromisoformat(s[:26]); return d.year+(d-dt.datetime(d.year,1,1)).total_seconds()/(365.25*86400)
# --- kataloglar
ca=[]
for f in sorted(glob.glob(V+'/ca/*.csv')):
    for r in csv.DictReader(open(f)):
        if r['mag'] and round(float(r['mag'])+1e-9,1)>=MTH: ca.append((yil(r['time']),float(r['latitude']),float(r['longitude']),round(float(r['mag'])+1e-9,1)))
mar=[]
for l in open(V+'/emsc_mar.txt'):
    if l.startswith('#'): continue
    x=l.split('|')
    if x[10] and round(float(x[10]),1)>=MTH: mar.append((yil(x[1]),float(x[2]),float(x[3]),round(float(x[10]),1)))
ca=np.array(sorted(ca)); mar=np.array(sorted(mar))
@numba.njit(parallel=True)
def nn(t,la,lo,m):
    n=len(t); eta=np.full(n,np.inf); R=6371.0
    for j in numba.prange(1,n):
        best=np.inf
        for i in range(j):
            dtt=t[j]-t[i]
            if dtt<=0: dtt=1e-9
            p1=np.radians(la[i]);p2=np.radians(la[j]);dl=np.radians(lo[j]-lo[i])
            a=np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
            r=2*R*np.arcsin(min(1.0,np.sqrt(a)))
            if r<0.1: r=0.1
            e=dtt*r**1.6*10**(-1.0*m[i])
            if e<best: best=e
        eta[j]=best
    return eta
def esik(eta):
    x=np.log10(eta[np.isfinite(eta)]).reshape(-1,1)
    try:
        g=GaussianMixture(2,random_state=0,n_init=5).fit(x)
        mu=g.means_.ravel(); sd=np.sqrt(g.covariances_.ravel()); w=g.weights_
        o=np.argsort(mu); grid=np.linspace(mu[o[0]],mu[o[1]],20001)
        d=w[o[0]]*norm.pdf(grid,mu[o[0]],sd[o[0]])-w[o[1]]*norm.pdf(grid,mu[o[1]],sd[o[1]])
        k=np.where(np.diff(np.sign(d))!=0)[0]
        if len(k)==0: raise ValueError
        return 10**grid[k[0]],dict(mu=mu.tolist(),sd=sd.tolist(),w=w.tolist())
    except Exception as e:
        return 1e-5,{'hata':str(e)}
res={'M_th':MTH,'N_ca':len(ca),'N_mar':len(mar)}
eca=nn(*[ca[:,k].copy() for k in range(4)]); emar=nn(*[mar[:,k].copy() for k in range(4)])
e0ca,gca=esik(eca); e0mar,gmar=esik(emar)
res.update(eta0_ca=e0ca,gmm_ca=gca,eta0_mar=e0mar,gmm_mar=gmar,fbg_ca_tum=float(np.mean(eca>e0ca)),fbg_mar_tum=float(np.mean(emar>e0mar)))
np.save(OUT+'/eta_ca.npy',eca); np.save(OUT+'/eta_mar.npy',emar)
# --- uzaklık
def iz_uzak(la,lo,tr):  # tr: (k,2) lat,lon ; nokta-çoklu çizgi km
    la0=np.radians(la); kx=111.195*np.cos(la0); ky=111.195
    X=(tr[:,1][None,:]-lo[:,None])*kx[:,None]; Y=(tr[:,0][None,:]-la[:,None])*ky
    ax,ay,bx,by=X[:,:-1],Y[:,:-1],X[:,1:],Y[:,1:]
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy; L2[L2==0]=1e-12
    u=np.clip(-(ax*dx+ay*dy)/L2,0,1); px,py=ax+u*dx,ay+u*dy
    return np.sqrt(px*px+py*py).min(1)
def rk(a):
    a=a%360; return min(abs(a-0),abs(a-360),abs(a-180))<=30
fm=ET.parse(V+'/FM3_1.xml').getroot()[0]
def bolumler(kor,eta,e0,cat):
    out=[]
    for s in fm:
        A=s.attrib
        if not(rk(float(A['aveRake'])) and float(A['aveDip'])>=70): continue
        tr=np.array([[float(l.attrib['Latitude']),float(l.attrib['Longitude'])] for l in s.find('FaultTrace').iter('Location')])
        bb=(cat[:,1]>tr[:,0].min()-0.2)&(cat[:,1]<tr[:,0].max()+0.2)&(cat[:,2]>tr[:,1].min()-0.25)&(cat[:,2]<tr[:,1].max()+0.25)
        idx=np.where(bb)[0]
        if len(idx)==0: continue
        d=iz_uzak(cat[idx,1],cat[idx,2],tr); ii=idx[d<=kor]
        if len(ii)<30: continue
        out.append(dict(ad=A['sectionName'],id=A['sectionId'],asf=float(A['aseismicSlipFactor']),n=len(ii),fbg=float(np.mean(eta[ii]>e0))))
    return out
def degerlendir(B):
    kal=[b for b in B if b['ad'].startswith('San Andreas')]; dog=[b for b in B if not b['ad'].startswith('San Andreas')]
    r={'N_kal':len(kal),'N_dog':len(dog)}
    if len(kal)<3: r['A']=False; return r,None
    x=np.array([b['fbg'] for b in kal]); y=np.array([b['asf'] for b in kal])
    beta,alpha=np.polyfit(x,y,1); rho=spearmanr(x,y).correlation
    r.update(alpha=alpha,beta=beta,rho_kal=rho,A=bool(rho>=0.5 and beta>0),asf_kal_ort=float(y.mean()))
    f=lambda fb: np.clip(alpha+beta*np.asarray(fb),0,1)
    if len(dog)>=2:
        xv=np.array([b['fbg'] for b in dog]); yv=np.array([b['asf'] for b in dog]); pv=f(xv)
        rv=spearmanr(xv,yv).correlation
        perm=np.array([spearmanr(xv,rng.permutation(yv)).correlation for _ in range(10000)])
        p=float((np.sum(perm>=rv)+1)/10001)
        mm=np.mean(abs(pv-yv)); ms=np.mean(abs(y.mean()-yv)); m0=np.mean(abs(yv))
        bs=[]
        for _ in range(2000):
            k=rng.integers(0,len(dog),len(dog)); 
            c=spearmanr(xv[k],yv[k]).correlation
            bs.append((c,np.mean(abs(pv[k]-yv[k]))-min(np.mean(abs(y.mean()-yv[k])),np.mean(abs(yv[k])))))
        bs=np.array(bs)
        r.update(rho_v=rv,p_v=p,MAE_model=mm,MAE_sabit=ms,MAE_sifir=m0,rho_v_90=np.nanpercentile(bs[:,0],[5,95]).tolist(),dMAE_90=np.nanpercentile(bs[:,1],[5,95]).tolist(),
                 n_asf_pozitif_dog=int(np.sum(yv>0)))
        r['B']=bool(len(dog)>=8 and rv>=0.4 and p<=0.05 and mm<min(ms,m0))
    else: r['B']=False
    return r,f
# --- Marmara kutuları
sh=shapefile.Reader(EDSF+'/DB-CFS/DB-CFS-ESRI-shapefile/Crustal_fault_sources_TOP.shp',encoding='latin1')
iz={}
for sr in sh.shapeRecords():
    if sr.record[0] in('TRCS996','TRCS013','TRCS014'):
        iz[sr.record[0]]=[np.array([[p[1],p[0]] for p in sr.shape.points[a:b]]) for a,b in zip(sr.shape.parts,list(sr.shape.parts[1:])+[len(sr.shape.points)])]
PEN={'Ganos':(26.95,27.50),'Tekirdag_bilgi':(27.50,27.75),'CMF-B':(27.75,28.40),'CMF-D':(28.40,28.75),'PIF':(28.75,29.20)}
def mar_kutu(kor,maske):
    d=np.min([iz_uzak(mar[:,1],mar[:,2],t) for k in('TRCS996','TRCS013') for t in iz[k]],axis=0)
    d14=np.min([iz_uzak(mar[:,1],mar[:,2],t) for t in iz['TRCS014']],axis=0)
    K={a:np.where((d<=kor)&(mar[:,2]>=lo)&(mar[:,2]<hi)&maske)[0] for a,(lo,hi) in PEN.items()}
    K['Cinarcik_TRCS014_bilgi']=np.where((d14<=kor)&maske)[0]
    return K
def mar_deg(K,f,e0):
    o={}
    for a,ii in K.items(): o[a]=dict(n=int(len(ii)),fbg=float(np.mean(emar[ii]>e0)) if len(ii) else None,uygun=len(ii)>=30)
    if f is None: return o,None
    for a in o:
        if o[a]['fbg'] is not None: o[a]['asf_tahmin']=float(f(o[a]['fbg']))
    bs={a:[] for a in K}
    for _ in range(5000):
        for a,ii in K.items():
            if len(ii): bs[a].append(float(f(np.mean(emar[rng.choice(ii,len(ii))]>e0))))
    bs={a:np.array(v) for a,v in bs.items()}
    C={}
    ok=all(o[a]['uygun'] for a in('CMF-B','CMF-D','Ganos'))
    for b in('CMF-D','Ganos'):
        if len(bs[b]) and len(bs['CMF-B']):
            dd=bs['CMF-B']-bs[b]; C['CMF-B_eksi_'+b]=dict(nokta=o['CMF-B']['asf_tahmin']-o[b]['asf_tahmin'],ci90=np.percentile(dd,[5,95]).tolist())
    C['C']=bool(ok and all(C[k]['nokta']>0 and C[k]['ci90'][0]>0 for k in C))
    for a in o:
        if len(bs[a]): o[a]['asf_ci90']=np.percentile(bs[a],[5,95]).tolist()
    return o,C
def kos(kor,e0ca,e0mar,maske):
    B=bolumler(kor,eca,e0ca,ca); r,f=degerlendir(B)
    K=mar_kutu(kor,maske); o,C=mar_deg(K,f,e0mar)
    return dict(bolumler=B,deg=r,marmara=o,C=C)
tum=np.ones(len(mar),bool)
res['ana']=kos(5,e0ca,e0mar,tum)
a=res['ana']; H1=bool(a['deg'].get('A') and a['deg'].get('B') and a['C'] and a['C']['C'])
res['hukum']='H1' if H1 else 'H0'
# bilgi satırları
big=mar[mar[:,3]>=5.5]
ms=tum.copy()
for b in big:
    r=6371*2*np.arcsin(np.sqrt(np.sin(np.radians(mar[:,1]-b[1])/2)**2+np.cos(np.radians(b[1]))*np.cos(np.radians(mar[:,1]))*np.sin(np.radians(mar[:,2]-b[2])/2)**2))
    ms&=~((r<=30)&(mar[:,0]>=b[0])&(mar[:,0]<b[0]+1))
res['bilgi_i_artci_dislama']=kos(5,e0ca,e0mar,ms)
res['bilgi_ii_3km']=kos(3,e0ca,e0mar,tum); res['bilgi_ii_10km']=kos(10,e0ca,e0mar,tum)
res['bilgi_iii_eta0_1e-5']=kos(5,1e-5,1e-5,tum)
json.dump(res,open(OUT+'/t2_sonuc.json','w'),indent=1,default=float)
print(json.dumps({k:v for k,v in res.items() if not isinstance(v,dict) or k.startswith('gmm')},default=float))
for k in ['ana','bilgi_i_artci_dislama','bilgi_ii_3km','bilgi_ii_10km','bilgi_iii_eta0_1e-5']:
    print(k, json.dumps(res[k]['deg'],default=float)); print('  MAR',json.dumps(res[k]['marmara'],default=float)); print('  C',json.dumps(res[k]['C'],default=float))
