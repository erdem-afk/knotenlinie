#!/usr/bin/env python3
"""TR-4: Marmara dv/v gürültü tabanı için yalnız ÜSTVERİYLE istasyon-pencere sayımı (dalga formu okunmaz).

Tanımlar `kayit/onkayit/TR-5_TR-4_SAYIM.md` bölüm 3'tedir. Seri 2025-12-31'de kesilir (2026 kataloğu kördür;
2026 dalga formu da kosismik düşüş yoluyla 2026 depremlerini sızdıracağı için kullanılmaz).

Girdi: <ham>/marmara_fed_kanal.txt (fedcatalog, kutu 40,0-41,6 K / 26,5-30,5 D, BHZ/HHZ),
       <tr2>/m6_havuz.csv (M>=6, z<=40), <ngl>/ev70.csv + ev70_pre.csv (M>=6,5, z<=70),
       isteğe bağlı <doluluk.json> dosyaları (kullanilabilirlik.py; KOERI servisi eksik raporluyor, bkz. not)
Kullanım: python3 -I -B tr4_sayim.py <ham> <ngl> <tr2> [doluluk.json ...]
"""
import csv, collections, datetime as dt, json, math, os, sys
import numpy as np

HAM, NGL, TR2 = sys.argv[1:4]
DOL = sys.argv[4:]
SON = dt.date(2025, 12, 31)
Y = 365.25
def yil(n): return dt.timedelta(days=int(math.floor(n * Y)))

def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

ep = collections.defaultdict(list); konum = {}
for l in open(os.path.join(HAM, 'marmara_fed_kanal.txt'), encoding='utf-8', errors='replace'):
    if l.startswith('#') or '|' not in l: continue
    p = l.rstrip('\n').split('|')
    if len(p) < 17 or p[3] not in ('BHZ', 'HHZ'): continue
    b = dt.date.fromisoformat(p[15][:10]); e = min(dt.date.fromisoformat(p[16][:10]) if p[16].strip() else SON, SON)
    if b > SON: continue
    k = p[0] + '.' + p[1]; ep[k].append((b, e)); konum[k] = (float(p[4]), float(p[5]))
def birlestir(iv):
    out = []
    for b, e in sorted(iv):
        if out and (b - out[-1][1]).days <= 30: out[-1][1] = max(out[-1][1], e)
        else: out.append([b, e])
    return out
ara = {k: birlestir(v) for k, v in ep.items()}
def kapsar(k, a, b): return any(x <= a and y >= b for x, y in ara[k])

def oku(f):
    out = []
    for r in csv.DictReader(open(f)):
        if r['type'] != 'earthquake': continue
        t = dt.datetime.fromisoformat(r['time'].replace('Z', '')).date()
        if t > SON: continue
        out.append((t, float(r['latitude']), float(r['longitude']), float(r['depth'] or 0), float(r['mag']), r['place']))
    return out
H6 = oku(os.path.join(TR2, 'm6_havuz.csv'))
H70 = oku(os.path.join(NGL, 'ev70.csv')) + oku(os.path.join(NGL, 'ev70_pre.csv'))

# TR-4 sakinlik (istasyon konumuna göre): M>=6 (z<=40) 150 km, M>=7 (z<=70) 300 km, pencere [T-7y, T)
def sakin(la, lo, a, b, r7=300.0):
    for t, la_, lo_, z, M, _ in H6:
        if a <= t < b and M >= 6.0 and z <= 40 and hav(la, lo, la_, lo_) <= 150: return False
    for t, la_, lo_, z, M, _ in H70:
        if a <= t < b and M >= 7.0 and z <= 70 and hav(la, lo, la_, lo_) <= r7: return False
    return True

print('Marmara çevresi (merkez 40,8 K 28,5 D, 400 km) M>=6, 2000-2025:')
for t, la, lo, z, M, yer in sorted(H6):
    if t.year >= 2000 and hav(40.8, 28.5, la, lo) <= 400:
        print(f'  {t} M{M} z{z:.0f} {hav(40.8, 28.5, la, lo):.0f} km  {yer}')

dol = {}
for f in DOL:
    for k, v in json.load(open(f)).items():
        dol[k.split('|')[0]] = v.get('yil', {})

TLER = [dt.date(y, 1, 1) for y in range(2012, 2024)]   # T + 2 yıl <= 2025-12-31 bilinmeli
sat = collections.Counter(); sat_dol = collections.Counter(); ist_T = collections.defaultdict(list)
for k in sorted(ara):
    la, lo = konum[k]
    for T in TLER:
        a, b = T - yil(5), T - dt.timedelta(days=1)
        if not kapsar(k, a, b): continue
        for kural, r7 in (('ana (M7 300 km)', 300.0), ('sıkı (M7 500 km)', 500.0)):
            if sakin(la, lo, T - yil(7), T, r7) and sakin(la, lo, T, T + yil(2), r7):
                sat[(kural, T.year)] += 1
                sat[(kural + ' ' + k.split('.')[0], T.year)] += 1
                if kural.startswith('ana'): ist_T[k].append(T.year)
                yl = dol.get(k)
                if yl is not None:
                    ok = all(yl.get(str(y), 0) >= 0.6 for y in range(a.year + 1, T.year))
                    if ok: sat_dol[(kural, T.year)] += 1
print('\nistasyon-pencere sayısı (5 yıl kesintisiz metadata; T = 1 Ocak):')
for kural in ('ana (M7 300 km)', 'sıkı (M7 500 km)'):
    print(' ', kural, {y: sat[(kural, y)] for y in range(2012, 2026) if sat[(kural, y)]})
    for ag_ in ('KO', '6G'):
        print('   ', ag_, {y: sat[(kural + ' ' + ag_, y)] for y in range(2012, 2026) if sat[(kural + ' ' + ag_, y)]})
    print('   KOERI availability >=%60 (güvenilmez, alt sınır):', {y: sat_dol[(kural, y)] for y in range(2012, 2026) if sat_dol[(kural, y)]})
# örtüşmeyen pencereler: istasyon başına T'ler arasında >= 5 yıl
bag = 0; ist = 0
for k, Ts in ist_T.items():
    sec = []
    for T in sorted(Ts):
        if not sec or T - sec[-1] >= 5: sec.append(T)
    bag += len(sec); ist += 1
print(f'\nana kural: pencereli istasyon {ist}, örtüşmeyen istasyon-pencere {bag}')
ag = collections.Counter(k.split('.')[0] for k in ist_T)
print('ağlara göre pencereli istasyon:', dict(ag))
bagKO = 0
for k, Ts in ist_T.items():
    if not k.startswith('KO.'): continue
    sec = []
    for T in sorted(Ts):
        if not sec or T - sec[-1] >= 5: sec.append(T)
    bagKO += len(sec)
print('KO örtüşmeyen istasyon-pencere:', bagKO)
