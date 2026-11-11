import csv, math, sys, json, datetime as dt
rows=list(csv.DictReader(open(sys.argv[1])))
ev=[]
for r in rows:
    t=dt.datetime.fromisoformat(r['time'].replace('Z',''))
    ev.append((t,float(r['latitude']),float(r['longitude']),float(r['mag']),r['id'],r['place']))
def dist(a,b):
    la1,lo1,la2,lo2=map(math.radians,(a[1],a[2],b[1],b[2]))
    h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 6371*2*math.asin(math.sqrt(h))
def L(m): return 10**(-2.57+0.62*m)  # WC94 RLD tüm tipler, km
mmin1=float(sys.argv[2]); mmin2=float(sys.argv[3]); tmax=float(sys.argv[4]); band=float(sys.argv[5])
prim=[e for e in ev if e[3]>=mmin1]
pairs=[]
for p in prim:
    for s in ev:
        if s[0]<=p[0] or s[3]<mmin2: continue
        dy=(s[0]-p[0]).days/365.25
        if dy>tmax: break
        d=dist(p,s); r=L(p[3])/2
        if d>r+L(s[3])/2*0.0 and d<=r+band and dy>=float(sys.argv[6]):
            pairs.append((p,s,dy,d))
print("birincil",len(prim),"çift",len(pairs))
dl=sorted(x[2] for x in pairs)
if dl:
    import statistics
    print("gecikme medyan %.2f yıl; çeyrekler"%statistics.median(dl), [round(dl[int(len(dl)*q)],2) for q in (0.1,0.25,0.75,0.9)])
    for lo,hi in [(0,1),(1,3),(3,10),(10,30),(30,100)]:
        n=sum(lo<=x<hi for x in dl); print(f"  {lo}-{hi} yıl: {n}  yoğunluk/yıl {n/(hi-lo):.2f}")
json.dump([[str(p[0]),p[4],p[3],p[5],str(s[0]),s[4],s[3],s[5],round(dy,2),round(d)] for p,s,dy,d in pairs],open(sys.argv[7],'w'),ensure_ascii=False,indent=0)
