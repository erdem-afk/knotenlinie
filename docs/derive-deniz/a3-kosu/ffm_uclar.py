"""A3 kural 2.1 §3: USGS FFM -> dogrultu ekseni, %5/%95 moment uclari."""
import sys, re, json, math
import numpy as np
R=6371.0
def oku(p):
    rows=[];strk=None;seg_str=None;seg=0;segs=[]
    for ln in open(p):
        m=re.search(r'STRK\s*=\s*([-\d.]+)',ln)
        if m and strk is None: strk=float(m.group(1))
        m=re.search(r'SEGMENT\s*#\s*(\d+):\s*STRIKE\s*=\s*([-\d.]+)',ln)
        if m: seg=int(m.group(1)); seg_str=float(m.group(2))
        if ln.lstrip().startswith('%') or not ln.strip(): continue
        v=ln.split()
        if len(v)>=10:
            rows.append([float(x) for x in v[:10]]+[seg_str if seg_str is not None else strk, seg])
    return np.array(rows), strk
def ll2xyz(lat,lon):
    la,lo=np.radians(lat),np.radians(lon)
    return np.stack([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)],-1)
def eksen(lat0,lon0,az):
    p=ll2xyz(lat0,lon0); la,lo=math.radians(lat0),math.radians(lon0)
    e=np.array([-math.sin(lo),math.cos(lo),0]); n=np.array([-math.sin(la)*math.cos(lo),-math.sin(la)*math.sin(lo),math.cos(la)])
    a=math.radians(az); t=math.sin(a)*e+math.cos(a)*n
    return p,t,np.cross(p,t)  # nokta, teget, kutup
def izdus(lat,lon,ax):
    p,t,pole=ax; x=ll2xyz(lat,lon)
    xp=x-np.outer(x@pole,pole); xp/=np.linalg.norm(xp,axis=-1,keepdims=True)
    return R*np.arctan2(xp@t, xp@p)   # dogrultu boyunca km (merkez=0)
def eksen_nokta(s,ax):
    p,t,_=ax; th=s/R; v=math.cos(th)*p+math.sin(th)*t
    return math.degrees(math.asin(v[2])), math.degrees(math.atan2(v[1],v[0]))
def ortalama_az(az,w):
    # dogrultu 180 belirsizligi yok (sag el kurali); dairesel ortalama
    a=np.radians(az); return math.degrees(math.atan2((w*np.sin(a)).sum(),(w*np.cos(a)).sum()))%360
def isle(p,dx):
    d,strk=oku(p); lat,lon,slip,mo,az=d[:,0],d[:,1],d[:,5],d[:,9],d[:,10]
    w=slip
    c=(ll2xyz(lat,lon)*w[:,None]).sum(0); c/=np.linalg.norm(c)
    clat,clon=math.degrees(math.asin(c[2])),math.degrees(math.atan2(c[1],c[0]))
    A=ortalama_az(az,w); ax=eksen(clat,clon,A)
    s=izdus(lat,lon,ax)
    o=np.argsort(s); cm=np.cumsum(mo[o])/mo.sum()
    x1=float(np.interp(0.05,cm,s[o])); x2=float(np.interp(0.95,cm,s[o]))
    smin,smax=float(s.min()),float(s.max())
    return dict(dosya=p.split('/')[-1],n_altfay=len(d),merkez=[clat,clon],dogrultu=A,
        x1=x1,x2=x2,L=x2-x1,alan=[smin,smax],dx=dx,
        x1_kesik=bool(x1<smin+dx/2), x2_kesik=bool(x2>smax-dx/2),
        uc1=eksen_nokta(x1,ax),uc2=eksen_nokta(x2,ax))
if __name__=='__main__':
    out={}
    for p in sys.argv[1:]:
        dx=float(re.search(r'Dx\s*=\s*([\d.]+)',open(p).read()).group(1))
        out[p.split('/')[-1]]=isle(p,dx)
    print(json.dumps(out,indent=1,ensure_ascii=False))
