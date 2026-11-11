import csv, math, datetime as dt, sys
D=sys.argv[1]
st=[]
for i,l in enumerate(open(D+'/holdings.txt')):
    if i==0: continue
    p=l.split()
    try:
        lat=float(p[1]); lon=float(p[2]); b=dt.date.fromisoformat(p[7]); e=dt.date.fromisoformat(p[8]); n=int(p[10])
    except Exception: continue
    st.append((p[0],lat,lon,b,e,n))
def hav(a,b,c,d):
    a,b,c,d=map(math.radians,(a,b,c,d))
    return 6371*2*math.asin(math.sqrt(math.sin((c-a)/2)**2+math.cos(a)*math.cos(c)*math.sin((d-b)/2)**2))
ev=list(csv.DictReader(open(D+'/comcat.csv')))
res={}
out=open(D+'/olay_istasyon.csv','w'); out.write('time,lat,lon,depth,mag,place,n100_5y,n100_10y,n50_5y,id\n')
for R,Y in [(100,5),(100,10),(50,5),(200,5)]:
    k3=0
    for e in ev:
        t=dt.date.fromisoformat(e['time'][:10]); la=float(e['latitude']); lo=float(e['longitude'])
        c=0
        for s in st:
            if s[3]<=t-dt.timedelta(days=365*Y) and s[4]>=t-dt.timedelta(days=30):
                span=(min(s[4],t)-s[3]).days
                if s[5]/max((s[4]-s[3]).days,1) < 0.6: continue
                if hav(la,lo,s[1],s[2])<=R: c+=1
        e[(R,Y)]=c
        if c>=3: k3+=1
    print(f"R={R}km, seri>={Y}y: >=3 istasyonlu olay {k3} / {len(ev)}")
for e in ev:
    out.write(f"{e['time'][:10]},{e['latitude']},{e['longitude']},{e['depth']},{e['mag']},\"{e['place']}\",{e[(100,5)]},{e[(100,10)]},{e[(50,5)]},{e['id']}\n")
# yillara gore
import collections
by=collections.Counter(); byall=collections.Counter()
for e in ev:
    y=int(e['time'][:4]); p=(y-2000)//5
    byall[p]+=1
    if e[(100,5)]>=3: by[p]+=1
print({2000+5*k:(by[k],byall[k]) for k in sorted(byall)})
