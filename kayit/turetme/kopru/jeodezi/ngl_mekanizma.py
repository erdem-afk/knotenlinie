import csv, json, urllib.request, sys, time
D=sys.argv[1]
rows=list(csv.DictReader(open(D+'/olay_istasyon.csv')))
sel=[r for r in rows if int(r['n100_5y'])>=3]
for r in sel:
    url=f"https://earthquake.usgs.gov/fdsnws/event/1/query?eventid={r['id']}&format=geojson"
    rake='?'
    try:
        j=json.load(urllib.request.urlopen(url,timeout=60))
        for key in ('moment-tensor','focal-mechanism'):
            for p in j['properties']['products'].get(key,[]):
                pr=p['properties']
                if 'nodal-plane-1-rake' in pr:
                    rake=pr['nodal-plane-1-rake']+'/'+pr.get('nodal-plane-2-rake','?'); break
            if rake!='?': break
    except Exception as ex: rake='ERR'
    def tip(rk):
        try:
            a=float(rk.split('/')[0])
        except: return '?'
        a=((a+180)%360)-180
        if abs(a)<=30 or abs(a)>=150: return 'DA'
        return 'T' if a>0 else 'N'
    print(r['time'],r['mag'],r['depth'],r['place'][:40],'n5y=',r['n100_5y'],'n10y=',r['n100_10y'],'rake',rake,tip(rake))
