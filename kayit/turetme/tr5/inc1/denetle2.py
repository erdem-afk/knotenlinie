import json, csv, collections, datetime as dt, sys
import numpy as np
L = json.load(open(sys.argv[1]))['olaylar']; M6 = sys.argv[2]
D = dt.date.fromisoformat
def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))
H = [(r['id'], D(r['time'][:10]), float(r['latitude']), float(r['longitude']), float(r['depth'] or 0), float(r['mag']))
     for r in csv.DictReader(open(M6)) if r['type'] == 'earthquake' and r['time'][:4] < '2026']
ana = [r for r in L if not r['volkanik']]
def kirli(s, a, b, haric, R=75, Mmin=6.0):
    out = []
    for (i, t, la, lo, z, M) in H:
        if i in haric or M < Mmin or z > 40: continue
        if a <= t <= b and hav(s['la'], s['lo'], la, lo) <= R: out.append((i, str(t), M, round(float(hav(s['la'], s['lo'], la, lo)))))
    return out
for R in (50, 75):
    ne = nc = 0; te = tc = 0; ex = []
    for r in ana:
        T = D(r['t']); a = T - dt.timedelta(days=1095 + 730); b = T - dt.timedelta(days=8)
        kume_id = {x['id'] for x in L if x['kume'] == r['kume']}
        for s in r['istasyon']:
            te += 1; k = kirli(s, a, b, kume_id, R)
            if k: ne += 1; ex.append(('olay', r['id'], s['ist'], k))
        for c in r['kontrol'][:5]:
            for s in c['istasyon']:
                tc += 1; k = kirli(s, a, b, (), R)
                if k: nc += 1; ex.append(('kontrol', r['id'], s['ist'], k))
    print(f'R={R} km, [pencere başı-2y, T-8]: olay ist {ne}/{te} = {ne/te:.2f}; kontrol ist {nc}/{tc} = {nc/tc:.2f}')
    for x in ex[:40]: print('   ', x)
# aynı olayın ilk 5 kontrolü arasında ortak istasyon
n = 0
for r in L:
    seen = collections.Counter(s['ist'] for c in r['kontrol'][:5] for s in c['istasyon'])
    d = [k for k, v in seen.items() if v > 1]
    if d: n += 1; print('aynı olayda ortak kontrol istasyonu', r['id'], d)
print('olay sayısı (ortak ist.)', n)
# plasebo eşleşik kümesi usb000r2hc tek olay mı
print([x['id'] for x in L if x['kume'] == 'usb000r2hc'])
