#!/usr/bin/env python3
"""TR-5b inceleme: liste ve kataloglar üstünden bağımsız denetimler (dalga formu yok)."""
import json, csv, glob, collections, datetime as dt, math, sys
import numpy as np

LISTE, M6, M5DIR = sys.argv[1:4]
L = json.load(open(LISTE))
O = L['olaylar']
D = dt.date.fromisoformat
def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

# kataloglar
H6 = []
for r in csv.DictReader(open(M6)):
    if r['type'] != 'earthquake': continue
    t = D(r['time'][:10])
    if t >= dt.date(2026, 1, 1): continue
    H6.append((r['id'], t, float(r['latitude']), float(r['longitude']), float(r['depth'] or 0), float(r['mag'])))
H6id = {x[0]: x for x in H6}
M5 = {}
for f in sorted(glob.glob(M5DIR + '/m5_*.csv')):
    for r in csv.DictReader(open(f)):
        M5[r['id']] = (D(r['time'][:10]), float(r['mag']))

ana = [r for r in O if not r['volkanik']]
print('olay', len(O), 'ana', len(ana))

# 1. kontrol istasyon sayısı / olay istasyon sayısı
ce = collections.Counter(len(r['istasyon']) for r in ana)
cc = collections.Counter(len(c['istasyon']) for r in ana for c in r['kontrol'][:5])
cc10 = collections.Counter(len(c['istasyon']) for r in ana for c in r['kontrol'])
print('olay istasyon sayısı', dict(ce), 'kontrol(ilk5) istasyon sayısı', dict(cc), 'kontrol(10)', dict(cc10))
ud_e = [s['uzaklik_km'] for r in ana for s in r['istasyon']]
ud_c = [s['uzaklik_km'] for r in ana for c in r['kontrol'][:5] for s in c['istasyon']]
print('uzaklık medyan olay %.1f kontrol %.1f' % (np.median(ud_e), np.median(ud_c)))
# en yakın istasyon uzaklığı
print('en yakın: olay medyan %.1f, kontrol medyan %.1f' % (np.median([min(s['uzaklik_km'] for s in r['istasyon']) for r in ana]),
      np.median([min(s['uzaklik_km'] for s in c['istasyon']) for r in ana for c in r['kontrol'][:5]])))

# 2. plasebo istasyonları olay istasyonlarıyla aynı mı
ayni = farkli = kismen = 0
for r in ana:
    if not r['plasebo']: continue
    a = {s['ist'] for s in r['istasyon']}; b = {s['ist'] for s in r['plasebo']['istasyon']}
    if a == b: ayni += 1
    elif a & b: kismen += 1
    else: farkli += 1; print('  plasebo farklı istasyon', r['id'], sorted(a), sorted(b))
print('plasebo istasyon kümesi: aynı', ayni, 'kısmen', kismen, 'farklı', farkli)

# 3. kontrol merkezlerinin ve olay yerlerinin [T-10y, T-5y) içinde 150 km'de M>=6 (z<=40) geçmişi: iyileşme kuyruğu asimetrisi
def gecmis(la, lo, T, haric=(), a_y=10, b_y=5, Mmin=6.0, R=150):
    a = T - dt.timedelta(days=int(a_y * 365.25)); b = T - dt.timedelta(days=int(b_y * 365.25))
    for (i, t, la_, lo_, z, M) in H6:
        if i in haric or M < Mmin or z > 40 or not (a <= t < b): continue
        if hav(la, lo, la_, lo_) <= R: return True
    return False
ge = np.mean([gecmis(r['la'], r['lo'], D(r['t']), haric={r['id']}) for r in ana])
gc = np.mean([gecmis(c['la'], c['lo'], D(r['t'])) for r in ana for c in r['kontrol'][:5]])
print('[T-10y,T-5y) 150 km M>=6 oranı: olay %.2f, kontrol(ilk5) %.2f' % (ge, gc))
ge2 = np.mean([gecmis(r['la'], r['lo'], D(r['t']), haric={r['id']}, a_y=15, Mmin=6.5) for r in ana])
gc2 = np.mean([gecmis(c['la'], c['lo'], D(r['t']), a_y=15, Mmin=6.5) for r in ana for c in r['kontrol'][:5]])
print('[T-15y,T-5y) 150 km M>=6,5 oranı: olay %.2f, kontrol %.2f' % (ge2, gc2))
# kontrol merkezinin kendi olayının zamanı
dts = []
for r in ana:
    for c in r['kontrol'][:5]:
        x = H6id.get(c['merkez_id'])
        if x: dts.append((x[1] - D(r['t'])).days / 365.25)
dts = np.array(dts)
print('kontrol merkezi kendi olayı - T (yıl): n %d; <-5: %.2f; -10..-5: %.2f; >+2: %.2f' % (len(dts), np.mean(dts < -5), np.mean((dts >= -10) & (dts < -5)), np.mean(dts > 2)))

# 4. maske günleri dilim başına: olay vs kontrol
def dilim_maske(s, T):
    gun = {'A': set(), 'B': set(), 'C': set()}
    for q in s['maske_olay']:
        if q not in M5: continue
        t0 = M5[q][0]
        for k in range(60):
            d = (t0 + dt.timedelta(days=k) - T).days
            if -1095 <= d <= -731: gun['A'].add(d)
            elif -730 <= d <= -366: gun['B'].add(d)
            elif -365 <= d <= -8: gun['C'].add(d)
    return {k: len(v) for k, v in gun.items()}
def ozet(lst):
    a = np.array([[x['A'], x['B'], x['C']] for x in lst])
    return 'n %d; ort gün A %.1f B %.1f C %.1f; C>0 oranı %.2f; (A∪B)>0 oranı %.2f' % (len(a), *a.mean(0), np.mean(a[:, 2] > 0), np.mean(a[:, :2].sum(1) > 0))
me = [dilim_maske(s, D(r['t'])) for r in ana for s in r['istasyon']]
mc = [dilim_maske(s, D(r['t'])) for r in ana for c in r['kontrol'][:5] for s in c['istasyon']]
print('maske olay:', ozet(me)); print('maske kontrol:', ozet(mc))
# C'de maskesi olan olay istasyonları
for r in ana:
    for s in r['istasyon']:
        x = dilim_maske(s, D(r['t']))
        if x['C'] > 0: print('   C maskeli', r['id'], r['M'], s['ist'], x, [(q, str(M5[q][0]), M5[q][1]) for q in s['maske_olay'] if q in M5][:6])

# 5. PK kümeleri: istasyon uzaklıkları, M
def L_km(M): return 10 ** (-2.44 + 0.59 * M)
pk = [r for r in ana if min(s['uzaklik_km'] for s in r['istasyon']) <= max(30.0, 2 * L_km(r['M']))]
print('PK olay', len(pk), 'küme', len({r['kume'] for r in pk}))
for r in pk:
    print('   PK', r['kume'], r['id'], r['t'], r['M'], [(s['ist'], s['uzaklik_km'], s['aygit_degisimi_Z']) for s in r['istasyon']], 'max(30,2L)=%.0f' % max(30, 2 * L_km(r['M'])))
# PK penceresinde başka M>=6 (aynı küme dışı ya da büyük artçı / ana şok)
for r in pk:
    T = D(r['t'])
    for (i, t, la, lo, z, M) in H6:
        if i != r['id'] and T <= t <= T + dt.timedelta(days=30) and M >= 6 and hav(r['la'], r['lo'], la, lo) <= 150:
            print('   PK penceresinde M>=6:', r['id'], '->', i, t, M)

# 6. volkanik kontrol merkezleri (kaba kutular: Hawaii, İzlanda, Kamçatka, Aleut yayı, Vanuatu...)
kut = {'Hawaii': (18, 23, -161, -154), 'İzlanda': (63, 67, -25, -13), 'Jan Mayen': (70, 72, -10, -7)}
for ad, (a, b, c_, d_) in kut.items():
    n = sum(1 for r in ana for c in r['kontrol'][:5] if a <= c['la'] <= b and c_ <= c['lo'] <= d_)
    n2 = sum(1 for r in ana if r['plasebo'] for c in r['plasebo']['kontrol'][:5] if a <= c['la'] <= b and c_ <= c['lo'] <= d_)
    print('kontrol merkezi', ad, 'olay ilk5:', n, 'plasebo ilk5:', n2)

# 7. kota: ilk 10 ile merkez başına küme sayısı (yedek kullanılırsa)
k10 = collections.defaultdict(set); k5 = collections.defaultdict(set)
for r in O:
    for c in r['kontrol']: k10[c['merkez_id']].add(r['kume'])
    for c in r['kontrol'][:5]: k5[c['merkez_id']].add(r['kume'])
print('ilk10 ile merkez başına en çok küme', max(len(v) for v in k10.values()), '; >3 kümeli merkez', sum(len(v) > 3 for v in k10.values()))
# kontrol istasyonu bazında tekrar (aynı istasyon farklı merkezlerin kontrolünde)
ist_kume = collections.defaultdict(set)
for r in O:
    for c in r['kontrol'][:5]:
        for s in c['istasyon']: ist_kume[s['ist']].add(r['kume'])
print('ilk5 kontrol istasyonu: tekil', len(ist_kume), '; en çok küme', max(len(v) for v in ist_kume.values()), '; >3 kümede', sum(len(v) > 3 for v in ist_kume.values()))
# olay ve plasebo kontrolleri arası ortak istasyon
pi = set(s['ist'] for r in O if r['plasebo'] for c in r['plasebo']['kontrol'][:5] for s in c['istasyon'])
print('olay-kontrol ve plasebo-kontrol ortak istasyon', len(set(ist_kume) & pi))
# kontrol istasyonu aynı zamanda olay istasyonu mu
ev = set(s['ist'] for r in O for s in r['istasyon'])
print('kontrol (ilk5) istasyonu olan olay istasyonu', sorted(set(ist_kume) & ev))

# 8. 1a istek sayısı: ilk 10 kontrol + 10 plasebo kontrol istasyon-pencereleri, ay sayısı
nw = 0; nreq = 0; seen = set()
for r in O:
    for c in r['kontrol']:
        for s in c['istasyon']:
            key = (s['ist'], r['pencere'][0]);
            if key in seen: continue
            seen.add(key); nw += 1; nreq += 36
    if r['plasebo']:
        for c in r['plasebo']['kontrol']:
            for s in c['istasyon']:
                key = (s['ist'], r['plasebo']['pencere'][0])
                if key in seen: continue
                seen.add(key); nw += 1; nreq += 36
print('1a istasyon-pencere', nw, 'istek (36 ay)', nreq)
merk = collections.Counter()
for r in O:
    for c in r['kontrol']:
        for s in c['istasyon']: merk[s['merkez']] += 36
    if r['plasebo']:
        for c in r['plasebo']['kontrol']:
            for s in c['istasyon']: merk[s['merkez']] += 36
print('merkez başına istek (tekrarlı)', dict(merk.most_common()))
# olay + plasebo istasyon-pencereleri
ne = sum(len(r['istasyon']) for r in O); npl = sum(len(r['plasebo']['istasyon']) for r in O if r['plasebo'])
print('olay ist-pencere', ne, 'plasebo ist-pencere', npl)
