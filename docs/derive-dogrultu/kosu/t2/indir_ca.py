import urllib.request,time,sys,os
B="https://earthquake.usgs.gov/fdsnws/event/1/query?minlatitude=32&maxlatitude=42&minlongitude=-125&maxlongitude=-114&maxdepth=20&minmagnitude=2.15&format=csv&orderby=time-asc"
os.makedirs('ca',exist_ok=True)
for y in range(1990,2026):
  for a,b in [("01-01","04-01"),("04-01","07-01"),("07-01","10-01"),("10-01","01-01")]:
    e=f"{y+1 if b=='01-01' else y}-{b}"; f=f"ca/{y}-{a}.csv"
    if os.path.exists(f): continue
    for k in range(6):
      try:
        d=urllib.request.urlopen(B+f"&starttime={y}-{a}&endtime={e}",timeout=120).read()
        open(f,'wb').write(d); print(f,d.count(b'\n'),flush=True); break
      except Exception as x:
        print('hata',f,x,flush=True); time.sleep(2**k)
