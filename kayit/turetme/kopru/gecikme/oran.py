import csv, math, sys, datetime as dt, json
rows=list(csv.DictReader(open(sys.argv[1])))
ev=[(dt.datetime.fromisoformat(r['time'].replace('Z','')),float(r['latitude']),float(r['longitude']),float(r['mag']),r['id']) for r in rows]
TEND=dt.datetime(2026,1,1)
def dist(a,b):
    la1,lo1,la2,lo2=map(math.radians,(a[1],a[2],b[1],b[2]))
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 6371*2*math.asin(math.sqrt(h))
L=lambda m:10**(-2.57+0.62*m)
mm1,mm2,band=float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4])
sel=set(json.load(open(sys.argv[5]))) if len(sys.argv)>5 else None
t0=dt.datetime(int(sys.argv[6]),1,1) if len(sys.argv)>6 else dt.datetime(1904,1,1)
prim=[e for e in ev if e[3]>=mm1 and e[0]>=t0 and (sel is None or e[4] in sel)]
bins=[(0,1/12),(1/12,1),(1,3),(3,10),(10,30),(30,60)]
cnt=[0]*len(bins); exp=[0.0]*len(bins)
for p in prim:
    T=(TEND-p[0]).days/365.25
    for i,(a,b) in enumerate(bins): exp[i]+=max(0,min(b,T)-a)
    r=L(p[3])/2
    for s in ev:
        if s[0]<=p[0] or s[3]<mm2: continue
        dy=(s[0]-p[0]).days/365.25
        if dy>=60: break
        d=dist(p,s)
        if r<d<=r+band:
            for i,(a,b) in enumerate(bins):
                if a<=dy<b: cnt[i]+=1
print("birincil",len(prim))
base=cnt[-1]/exp[-1]
for (a,b),n,e in zip(bins,cnt,exp):
    print(f"  {a:6.3f}-{b:5.1f} yıl: n={n:5d} birincil-yıl={e:9.0f} oran={n/e:.4f}/yıl  /taban(30-60y)={n/e/base:.2f}")
