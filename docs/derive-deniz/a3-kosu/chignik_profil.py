"""A3 §1 Chignik: TDEFNODE flt.gmt, phi = baslik satirinin 3. sayisal alani (Z degerinden sonra 2.;
dogrulama: 2. alan / phi = 59-66 mm/yil yakinsama hizi). 0-60 km derinlik dugumleri, 10 km kutu ortalamasi."""
import sys, json, numpy as np
sys.path.insert(0, sys.argv[3]); from ffm_uclar import eksen, izdus
f, uc_json = sys.argv[1], sys.argv[2]
lat=[];lon=[];phi=[];dep=[]
for ln in open(f):
    if ln.startswith('>'):
        v=ln.split(); phi.append(float(v[4])); lon.append(float(v[10])-360); lat.append(float(v[11])); dep.append(-float(v[12]))
lat,lon,phi,dep=map(np.array,(lat,lon,phi,dep))
u=json.load(open(uc_json))['ak0219neiszm_2.fsp']
ax=eksen(u['merkez'][0],u['merkez'][1],u['dogrultu'])
m=(dep>=0)&(dep<=60)
s=izdus(lat[m],lon[m],ax); p=phi[m]
lo,hi=np.floor(s.min()/10)*10, np.ceil(s.max()/10)*10
kenar=np.arange(lo,hi+10,10); idx=np.digitize(s,kenar)-1
x=[];c=[]
for i in range(len(kenar)-1):
    k=idx==i
    if k.sum()>0: x.append(kenar[i]+5); c.append(float(p[k].mean()))
json.dump(dict(olay='Chignik',x=x,c=c,a=float(s.min()),b=float(s.max()),n_dugum=int(m.sum()),
  kaynak='Drooff-Freymueller 2021, Zenodo 7644098 flt.gmt, phi sutunu 3'),open(sys.argv[4],'w'),indent=1)
print(len(x), s.min(), s.max(), u['x1'], u['x2'])
