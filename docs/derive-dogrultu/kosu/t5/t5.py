# T5 koşusu, T5-KURAL.md (dondurulmuş cda6638) birebir.
import json,glob,numpy as np,shapefile,xml.etree.ElementTree as ET,sys
from scipy.stats import binom
B=sys.argv[1]; EDSF=sys.argv[2]; FM=sys.argv[3]; JS=sys.argv[4]
O={o['id']:o for o in json.load(open(B+'/veri/olaylar_ozet.json'))}
def parcalar(s): 
    pp=list(s.parts)+[len(s.points)]; return [np.array([[p[1],p[0]] for p in s.points[a:b]]) for a,b in zip(pp[:-1],pp[1:])]
M={}
# ESHM13: DB-CFS izleri, HM-CFS MAXMW
mx={r[0]:r[35] for r in shapefile.Reader(EDSF+'/HM-CFS/CSSMwMax5_polyline.shp',encoding='latin1').records()}
M['ESHM13']=[(sr.record[0],mx.get(sr.record[0]),t) for sr in shapefile.Reader(EDSF+'/DB-CFS/DB-CFS-ESRI-shapefile/Crustal_fault_sources_TOP.shp',encoding='latin1').shapeRecords() for t in parcalar(sr.shape)]
fm=ET.parse(FM).getroot()[0]
M['UCERF3']=[(s.attrib['sectionName'],None,np.array([[float(l.attrib['Latitude']),float(l.attrib['Longitude'])] for l in s.find('FaultTrace').iter('Location')])) for s in fm]
js=[]
for f in sorted(glob.glob(JS+'/x/*_LND_*.shp')):
    for sr in shapefile.Reader(f,encoding='cp932').shapeRecords():
        d=sr.record.as_dict(); 
        mg=abs(d['MAG']) if 'MAG' in d else max(abs(float(x)) for x in __import__('re').findall(r'-?\d+\.\d+',d['MAGRANGE']))
        for t in parcalar(sr.shape): js.append((d['LTECODE'],mg,t))
M['JSHIS_Y2014']=js
OLAY={'ci38457511':'UCERF3','us60007ewc':'ESHM13','us6000jllz':'ESHM13','us6000jlqa':'ESHM13','us20005iis':'JSHIS_Y2014'}
DISARI={'nn00725272':'UCERF3 alanı, USGS FFM yok','usb000r2hc':'ESHM13 alanı, USGS FFM yok','us10003ywp':'ESHM13 alanı, USGS FFM yok'}
def km(la0): return 111.195*np.cos(np.radians(la0)),111.195
def uzak(P,tr):
    kx,ky=km(P[:,0].mean()); X=(tr[:,1][None,:]-P[:,1][:,None])*kx; Y=(tr[:,0][None,:]-P[:,0][:,None])*ky
    if tr.shape[0]==1: return np.hypot(X[:,0],Y[:,0])
    ax,ay,bx,by=X[:,:-1],Y[:,:-1],X[:,1:],Y[:,1:]; dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy; L2[L2==0]=1e-12
    u=np.clip(-(ax*dx+ay*dy)/L2,0,1); return np.hypot(ax+u*dx,ay+u*dy).min(1)
def gozlenen(i,esik_oran=0.0):
    g=json.load(open(f'{B}/ffm/{i}_FFM.geojson')); smax=max(f['properties']['slip'] for f in g['features'])
    pts=[];L=0
    for f in g['features']:
        if f['properties']['slip']<=esik_oran*smax or f['properties']['slip']<=0: continue
        c=np.array(f['geometry']['coordinates'][0][:4]); z=c[:,2]; o=np.argsort(z)[:2]; a,b=c[o[0]],c[o[1]]
        kx,ky=km(a[1]); l=np.hypot((b[0]-a[0])*kx,(b[1]-a[1])*ky); n=max(2,int(l/0.25)+1)
        for s in np.linspace(0,1,n): pts.append((a[1]+s*(b[1]-a[1]),a[0]+s*(b[0]-a[0]),l/n))
        L+=l
    return np.array(pts),L
def puan(i,esik_oran=0.0):
    P,L=gozlenen(i,esik_oran); mod=M[OLAY[i]]
    bb=(P[:,0].min()-0.5,P[:,0].max()+0.5,P[:,1].min()-0.6,P[:,1].max()+0.6)
    dmin=np.full(len(P),np.inf); kes={}
    for ad,mm,t in mod:
        if t[:,0].max()<bb[0] or t[:,0].min()>bb[1] or t[:,1].max()<bb[2] or t[:,1].min()>bb[3]: continue
        d=uzak(P[:,:2],t); dmin=np.minimum(dmin,d)
        if (d<=5).any(): kes[ad]=mm
    pay=float(np.sum(P[:,2]*(dmin<=5))/np.sum(P[:,2])); K1=pay>=0.5
    mw=O[i]['mag']; mmx=[v for v in kes.values() if v is not None]
    if OLAY[i]=='UCERF3': K2=None
    else: K2=bool(len(mmx) and max(mmx)>=mw-0.2)
    kac=(not K1) or (K2 is False)
    return dict(id=i,yer=O[i]['place'],Mw=mw,model=OLAY[i],K1_pay=round(pay,3),K1=K1,kesisen=sorted(kes)[:12],n_kesisen=len(kes),Mmax_kesisen=max(mmx) if mmx else None,K2=K2,kacirildi=kac,iz_uzunluk_toplam_km=round(L,1))
R={'ana':[puan(i) for i in OLAY],'bilgi_kayma_ge_0.1max':[puan(i,0.1) for i in OLAY],'disarida':DISARI}
for k in ['ana','bilgi_kayma_ge_0.1max']:
    n=len(R[k]); x=sum(r['kacirildi'] for r in R[k]); p=float(binom.sf(x-1,n,0.2))
    R[k+'_ozet']=dict(N=n,kacirma=x,pay=x/n,p_binom=p,ates=n>=5,hukum=('veri yetersiz' if n<5 else ('H1' if p<=0.05 else 'H0')))
json.dump(R,open(B+'/t5_sonuc.json','w'),indent=1,ensure_ascii=False,default=float)
for k in ['ana','bilgi_kayma_ge_0.1max']:
    for r in R[k]: print(k,{x:r[x] for x in ['id','Mw','model','K1_pay','K1','n_kesisen','Mmax_kesisen','K2','kacirildi']})
    print(R[k+'_ozet'])
