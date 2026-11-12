import json, datetime as dt, math, numpy as np
L=json.load(open('../kopya/tr6a_olay_listesi.json'))
d=json.load(open('../kopya/tr6a_onkayit_sayilar.json'))
ol={o['id']:o for o in L['olaylar']}; bi={b['id']:b for b in L['birimler']}
def km(a,b):
    p1,p2=math.radians(a['enlem']),math.radians(b['enlem'])
    c=math.sin(p1)*math.sin(p2)+math.cos(p1)*math.cos(p2)*math.cos(math.radians(b['boylam']-a['boylam']))
    return 6371*math.acos(max(-1,min(1,c)))
T=dt.datetime.fromisoformat
kl=d['onsayim']['19']['kumeler']
for kat in (3,4):
  J=0; out=[]
  for c in kl:
    b=bi[c[0]['id']]; t0=T(b['zaman']); kay=T(b['t_s'])-t0; g=0
    for j in (1,2,3):
        tj=t0-dt.timedelta(days=395+335*(j-1)); s0=tj+kay+dt.timedelta(days=30); s1=tj+dt.timedelta(days=365)
        ok=True
        for x in L['olaylar']:
            if x['grup']==b['id']: continue
            tx=T(x['zaman'])
            if tx<s1 and tx+dt.timedelta(days=365)>s0 and km(b,x)< kat*x['L_km']+3*b['L_km']: ok=False
        g+=ok
    J+=g; out.append((b['id'],g,round(c[0]['N0'],1)))
  print(kat,'L_A + 3L_B: J =',J, [o for o in out if o[1]<3])
# sahte ozet: gecersiz nedenleri (3L)
for c in kl:
    b=bi[c[0]['id']]
    for s in b['sahte']:
        if not s['gecerli']: print(b['id'], s['j'], s['ortusen'])
# real windows: neighbor A in [t0-365, t0) within 3L_A+3L_B
print('--- gercek: [t0-365,t0) icinde komsu')
for c in kl:
    b=bi[c[0]['id']]; t0=T(b['zaman'])
    nb=[x['id'] for x in L['olaylar'] if x['grup']!=b['id'] and t0-dt.timedelta(days=365)<=T(x['zaman'])<t0 and km(b,x)<3*x['L_km']+3*b['L_km']]
    if nb: print(b['id'],nb)
