#!/usr/bin/env python3
"""TR-11: sakin küme-pencerelerinin yalnız üstveriyle sayımı (hiçbir tenv3 ya da başka zaman serisi okunmaz).

Tanımlar `kayit/onkayit/TR-11_SAYIM.md` bölüm 2'dedir; bu betik onları kodlar. Okuyucular TR-1
`kayit/turetme/tr1/sayim_ustveri.py`'den uyarlandı (o betik içe aktarılamıyor: modül düzeyinde koşuyor).

Girdi (ham dosyalar depo dışında):
  <ngl>/DataHoldings.txt, <ngl>/steps.txt               NGL üstverisi (11 Kasım 2026 indirmesi)
  <ngl>/ev70.csv, <ngl>/ev70_pre.csv                     ComCat M>=6,5, derinlik<=70 km, 2000-2025 ve 1985-1999
  <tr2>/m6_havuz.csv                                     ComCat M>=6,0, derinlik<=40 km, 1976-2025 (TR-2 indirmesi)
  <tr2>/birincil_aday.csv, birincil_aday_fm.csv, mekanizma.jsonl
                                                         ComCat M6,0-7,2, derinlik<=25 km, mekanizmalı olaylar (TR-2)
Hiçbir dosyada 2026 ve sonrası tarih kullanılmaz (satır düzeyinde atılır).

Kullanım: python3 -I -B sayim_ustveri.py <ngl_dizini> <tr2_ham_dizini> [--json çıktı.json]
Ana sayım ve tanı/bilgi değişkeleri (ön kayıt kuralı değil) aynı koşuda yazılır.
"""
import csv, collections, datetime as dt, json, math, os, sys
import numpy as np

NGL, TR2 = sys.argv[1], sys.argv[2]
Y = 365.25
def gun(y): return int(math.floor(y * Y))
TD = dt.timedelta
SON = dt.date(2026, 1, 1)

# ------------------------------------------------------------------ önceden sabit tanımlar (bölüm 2)
EPOKLAR = [dt.date(y, 1, 1) for y in (2003, 2008, 2013, 2018, 2023)]   # T; W = [T - 5 yıl, T - 1 gün]
R_YAKIN, HALKA = 100.0, (200.0, 500.0)
N_MAX, N_MIN = 8, 3
IZGARA = 2.0                     # derece; satırlar 2° (≈222 km) aralıklı, satır içinde ≈222 km
MARMARA = (39.5, 42.0, 26.0, 31.5)
# sakinlik
S1 = dict(M=6.0, R=200.0, once=5, sonra=2)      # M>=6,0 (z<=40) merkez 200 km, [w0-5y, T+2y]
S2 = dict(M=7.0, R=500.0, once=10, sonra=2)     # M>=7,0 (z<=70) merkez 500 km, [w0-10y, T+2y]
S3 = dict(M=8.0, R=1000.0, once=10, sonra=0)    # M>=8,0 (z<=70) merkez 1000 km, [w0-10y, T]
K2_ONCE = 2                                      # istasyon: [w0-2y, w1] içinde kod 2 kaydı yok
SICRAMA_KENAR = 30                               # kod 1: H±30 g ya da pencere kenarından 30 g içinde -> uygun değil
# ortam sınıfı
SINIF_R, SINIF_MIN_MEK = 150.0, 2

# ------------------------------------------------------------------ okuyucular
def hav_vec(la, lo, LA_, LO_):
    la, lo = math.radians(la), math.radians(lo)
    a = np.sin((LA_ - la) / 2) ** 2 + np.cos(la) * np.cos(LA_) * np.sin((LO_ - lo) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

def sar(lo): return (lo + 180) % 360 - 180

st_ad, st_la, st_lo, st_b, st_e, st_n = [], [], [], [], [], []
with open(os.path.join(NGL, 'DataHoldings.txt')) as f:
    next(f)
    for l in f:
        p = l.split()
        try:
            la, lo = float(p[1]), sar(float(p[2]))
            b, e, n = dt.date.fromisoformat(p[7]), dt.date.fromisoformat(p[8]), int(p[10])
        except Exception:
            continue
        st_ad.append(p[0]); st_la.append(la); st_lo.append(lo); st_b.append(b); st_e.append(min(e, SON - TD(days=1))); st_n.append(n)
NS = len(st_ad)
AD = np.array(st_ad)
LA, LO = np.radians(st_la), np.radians(st_lo)
def marmara(la, lo): return MARMARA[0] <= la <= MARMARA[1] and MARMARA[2] <= lo <= MARMARA[3]
MAR = np.array([marmara(a, o) for a, o in zip(st_la, st_lo)])

def tarih(s):
    yy = int(s[:2]); yyyy = 2000 + yy if yy <= 79 else 1900 + yy
    return dt.datetime.strptime(f'{yyyy}{s[2:]}', '%Y%b%d').date()
k1 = collections.defaultdict(set); k2 = collections.defaultdict(list)
with open(os.path.join(NGL, 'steps.txt')) as f:
    for l in f:
        p = l.split()
        if len(p) < 3: continue
        try: t = tarih(p[1])
        except Exception: continue
        if t >= SON: continue
        if p[2] == '1': k1[p[0]].add(t)
        elif p[2] == '2': k2[p[0]].append(t)

def katalog(fn, sadece_deprem=True):
    out = []
    with open(fn) as f:
        for r in csv.DictReader(f):
            t = dt.date.fromisoformat(r['time'][:10])
            if t >= SON: continue
            if sadece_deprem and r.get('type', 'earthquake') != 'earthquake': continue
            out.append(dict(id=r['id'], T=t, la=float(r['latitude']), lo=sar(float(r['longitude'])),
                            M=float(r['mag']), z=float(r['depth'] or 0)))
    return out
E6 = katalog(os.path.join(TR2, 'm6_havuz.csv'))
E70 = {e['id']: e for e in katalog(os.path.join(NGL, 'ev70_pre.csv')) + katalog(os.path.join(NGL, 'ev70.csv'))}
E70 = list(E70.values())
def dizi(E):
    return (np.radians([e['la'] for e in E]), np.radians([e['lo'] for e in E]),
            np.array([e['T'].toordinal() for e in E]), np.array([e['M'] for e in E]))
E6a, E70a = dizi(E6), dizi(E70)

def deprem_var(la, lo, arr, Mmin, R, t0, t1):
    ELA, ELO, ET, EM = arr
    m = (EM >= Mmin) & (ET >= t0.toordinal()) & (ET <= t1.toordinal())
    if not m.any(): return False
    return bool((hav_vec(la, lo, ELA[m], ELO[m]) <= R).any())

# mekanizma (TR-2: M6,0-7,2, z<=25, 1976-2025)
konum = {}
for fn in ('birincil_aday.csv', 'birincil_aday_fm.csv'):
    for e in katalog(os.path.join(TR2, fn)):
        konum[e['id']] = e
def rake_sec(rec):
    for k in ('mt', 'fm'):
        L = [x for x in rec.get(k, []) if 'nodal-plane-1-rake' in x or 'nodal-plane-1-slip' in x]
        if L:
            x = max(L, key=lambda q: q.get('_w', 0))
            return float(x.get('nodal-plane-1-rake', x.get('nodal-plane-1-slip')))
    return None
MEK = []
with open(os.path.join(TR2, 'mekanizma.jsonl')) as f:
    for s in f:
        if not s.strip(): continue
        r = json.loads(s)
        if r.get('hata') or r['id'] not in konum: continue
        rk = rake_sec(r)
        if rk is None: continue
        rk = sar(rk)
        e = konum[r['id']]
        MEK.append((e['la'], e['lo'], abs(rk) <= 30 or abs(rk) >= 150))
MEKla, MEKlo = np.radians([m[0] for m in MEK]), np.radians([m[1] for m in MEK])
MEKss = np.array([m[2] for m in MEK])

def sinif(la, lo):
    """A: doğrultu atımlı kuşak, B: öteki aktif, D: düşük sismisite (place property, 1976-2025)."""
    n6 = int((hav_vec(la, lo, E6a[0], E6a[1]) <= SINIF_R).sum())
    if n6 == 0: return 'D'
    m = hav_vec(la, lo, MEKla, MEKlo) <= SINIF_R
    nm, nss = int(m.sum()), int(MEKss[m].sum())
    if nm >= SINIF_MIN_MEK and nss / nm >= 0.5: return 'A'
    return 'B'

def bolge(la, lo):
    if 30 <= la <= 50 and -126 <= lo <= -112: return 'ABD batı/Kaliforniya-Nevada'
    if 50 < la <= 72 and -170 <= lo <= -128 or (la > 50 and lo > 170): return 'Alaska/Kanada batı'
    if 24 <= la <= 46 and 122 <= lo <= 150: return 'Japonya'
    if -48 <= la <= -33 and 165 <= lo <= 180: return 'Yeni Zelanda'
    if -56 <= la <= 13 and -82 <= lo <= -60: return 'And/G. Amerika batı'
    if 34 <= la <= 48 and 12 <= lo <= 30: return 'Alp-İtalya-Balkan-Ege'
    if 34 <= la <= 44 and 26 <= lo <= 45: return 'Anadolu (Marmara dışı)'
    if 20 <= la <= 50 and 70 <= lo <= 122: return 'Çin/Tibet/Tayvan/Himalaya'
    if 63 <= la <= 67 and -25 <= lo <= -13: return 'İzlanda'
    if 14 <= la <= 33 and -118 <= lo <= -86: return 'Meksika/Orta Amerika'
    if 35 <= la <= 72 and -12 <= lo <= 40: return 'Avrupa (öteki)'
    if 24 <= la <= 50 and -112 < lo <= -60: return 'K. Amerika (öteki)'
    if -45 <= la <= -10 and 110 <= lo <= 155: return 'Avustralya'
    return 'öteki'

# ------------------------------------------------------------------ istasyon uygunluğu (epok başına)
def uygunluk(T, doluluk=False, k2_kural=True, sicrama=True):
    w0, w1 = T - TD(days=gun(5)), T - TD(days=1)
    H = T - TD(days=gun(2))
    e0 = w0 - TD(days=gun(K2_ONCE))
    ok = np.zeros(NS, bool)
    for i in range(NS):
        if MAR[i] or st_b[i] > w0 or st_e[i] < w1: continue
        if doluluk and st_n[i] / ((st_e[i] - st_b[i]).days + 1) < 0.60: continue
        s = st_ad[i]
        if k2_kural and any(e0 <= t <= w1 for t in k2[s]): continue
        if sicrama:
            bad = False
            for t in k1[s]:
                if w0 <= t <= w1 and (abs((t - H).days) < SICRAMA_KENAR or (t - w0).days < SICRAMA_KENAR or (w1 - t).days < SICRAMA_KENAR):
                    bad = True; break
            if bad: continue
        ok[i] = True
    return ok

def sakin(la, lo, T, s1=True, s2=True, s3=True):
    w0 = T - TD(days=gun(5))
    if s1 and deprem_var(la, lo, E6a, S1['M'], S1['R'], w0 - TD(days=gun(S1['once'])), T + TD(days=gun(S1['sonra'])) - TD(days=1)): return False
    if s2 and deprem_var(la, lo, E70a, S2['M'], S2['R'], w0 - TD(days=gun(S2['once'])), T + TD(days=gun(S2['sonra'])) - TD(days=1)): return False
    if s3 and deprem_var(la, lo, E70a, S3['M'], S3['R'], w0 - TD(days=gun(S3['once'])), T - TD(days=1)): return False
    return True

# ------------------------------------------------------------------ ızgara merkezleri
def izgara():
    out = []
    lat = -89.0
    while lat < 90:
        n = max(1, int(math.floor(360 * math.cos(math.radians(lat)) / IZGARA)))
        for k in range(n):
            out.append((lat, sar(-180 + k * 360.0 / n)))
        lat += IZGARA
    return out
MERKEZ = [(la, lo) for la, lo in izgara() if not marmara(la, lo)]
# yalnız 100 km içinde (zamandan bağımsız) >=3 istasyonu olan merkezler; uzaklık ve sıra önbellekte
ON = []
for la, lo in MERKEZ:
    d = hav_vec(la, lo, LA, LO)
    yk = np.where(d <= R_YAKIN)[0]
    if (~MAR[yk]).sum() < N_MIN: continue
    hk = np.where((d >= HALKA[0]) & (d <= HALKA[1]))[0]
    yk = yk[np.lexsort((AD[yk], d[yk]))]; hk = hk[np.lexsort((AD[hk], d[hk]))]
    ON.append(dict(la=la, lo=lo, yk=yk, hk=hk, d=d))

def kume(c, ok):
    y = [i for i in c['yk'] if ok[i]][:N_MAX]
    r = [i for i in c['hk'] if ok[i]][:N_MAX]
    return (y, r) if len(y) >= N_MIN and len(r) >= N_MIN else None

def say(ad, doluluk=False, k2_kural=True, sicrama=True, s1=True, s2=True, s3=True, ayrinti=False):
    satir = []
    for T in EPOKLAR:
        ok = uygunluk(T, doluluk, k2_kural, sicrama)
        for j, c in enumerate(ON):
            k = kume(c, ok)
            if k is None: continue
            if not sakin(c['la'], c['lo'], T, s1, s2, s3): continue
            satir.append(dict(T=T, j=j, y=k[0], r=k[1]))
    yer = sorted({s['j'] for s in satir})
    blok = {(int(math.floor(ON[j]['la'] / 10)), int(math.floor(ON[j]['lo'] / 10))) for j in yer}
    print(f'\n== {ad}: küme-pencere {len(satir)}; bağımsız yer {len(yer)}; 10°x10° blok {len(blok)}')
    if not ayrinti: return satir
    print('  epok başına küme-pencere:', {str(T.year): sum(s['T'] == T for s in satir) for T in EPOKLAR})
    cls = {j: sinif(ON[j]['la'], ON[j]['lo']) for j in yer}
    reg = {j: bolge(ON[j]['la'], ON[j]['lo']) for j in yer}
    for etiket, fn in (('sınıf', cls), ('bölge', reg)):
        kp = collections.Counter(fn[s['j']] for s in satir)
        yr = collections.Counter(fn[j] for j in yer)
        bl = collections.defaultdict(set)
        for j in yer: bl[fn[j]].add((int(math.floor(ON[j]['la'] / 10)), int(math.floor(ON[j]['lo'] / 10))))
        print(f'  {etiket}: (küme-pencere / yer / blok)')
        for k, v in sorted(kp.items(), key=lambda x: -x[1]):
            print(f'    {k:32s} {v:5d} {yr[k]:5d} {len(bl[k]):4d}')
    # A sınıfı: bölge kırılımı
    print('  A sınıfı bölgeler (küme-pencere / yer):',
          dict(collections.Counter(reg[s['j']] for s in satir if cls[s['j']] == 'A')),
          dict(collections.Counter(reg[j] for j in yer if cls[j] == 'A')))
    print('  n_y dağılımı:', dict(sorted(collections.Counter(len(s['y']) for s in satir).items())))
    print('  n_r dağılımı:', dict(sorted(collections.Counter(len(s['r']) for s in satir).items())))
    yk = np.array([np.median(ON[s['j']]['d'][s['y']]) for s in satir])
    print('  yakın istasyon uzaklığı medyanı (km), küme-pencereler üzerinde çeyrekler:', np.round(np.percentile(yk, [25, 50, 75]), 1))
    # yer başına epok sayısı
    print('  yer başına epok sayısı:', dict(sorted(collections.Counter(collections.Counter(s['j'] for s in satir).values()).items())))
    # indirme
    ist = sorted({i for s in satir for i in s['y'] + s['r']})
    nsol = sum(st_n[i] for i in ist)
    print(f'  indirilecek istasyon {len(ist)}; toplam çözüm günü {nsol:,}; kaba hacim ≈ {nsol*170/1e9:.2f} GB (170 B/satır)')
    ist_y = sorted({i for s in satir for i in s['y']})
    print(f'  bunların yakın rolündeki {len(ist_y)}; yalnız referans {len(ist) - len(ist_y)}')
    # en kalabalık 15 yer hücresi (blok) payı
    bc = collections.Counter((int(math.floor(ON[s["j"]]['la'] / 10)), int(math.floor(ON[s["j"]]['lo'] / 10))) for s in satir)
    print('  en büyük 5 blok payı (küme-pencere):', [(k, v) for k, v in bc.most_common(5)], f'toplamın %{100*sum(v for _, v in bc.most_common(5))/len(satir):.0f}')
    return satir

if __name__ == '__main__':
    print(f'istasyon {NS} (Marmara kutusu {int(MAR.sum())}); M>=6 havuz {len(E6)}; M>=6,5 z<=70 {len(E70)}; mekanizma {len(MEK)} (DA {int(MEKss.sum())})')
    print(f'ızgara merkezi {len(MERKEZ)}; 100 km içinde >=3 (Marmara dışı) istasyonlu {len(ON)}')
    ana = say('ANA (doluluk atlandı, üst sınır)', ayrinti=True)
    say('doluluk ≈ NumSol/gün aralığı >= 0,60', doluluk=True, ayrinti=True)
    print('\n-- tanı (ön kayıt kuralı değil): sakinlik şartlarının etkisi')
    say('Ş1-Ş3 kapalı (yalnız istasyon kuralları)', s1=False, s2=False, s3=False, ayrinti=True)
    say('yalnız Ş1 kapalı', s1=False)
    say('yalnız Ş2 kapalı', s2=False)
    say('yalnız Ş3 kapalı', s3=False)
    say('kod 2 istasyon kuralı kapalı', k2_kural=False)
    say('kod 1 sıçrama kuralı kapalı', sicrama=False)
    # Marmara bilgi satırı: kutu içi istasyonlar 2016 ve öncesi pencerelerde (yalnız sayım; seri indirilmez)
    print('\n-- bilgi: Marmara kutusu, 2016 sonu öncesi biten pencereler (kullanılmaz)')
    for T in EPOKLAR:
        if T > dt.date(2017, 1, 1): continue
        w0, w1 = T - TD(days=gun(5)), T - TD(days=1)
        n = sum(1 for i in range(NS) if MAR[i] and st_b[i] <= w0 and st_e[i] >= w1
                and not any(w0 - TD(days=gun(K2_ONCE)) <= t <= w1 for t in k2[st_ad[i]]))
        print(f'  T={T}: pencereyi kapsayan, kod 2 kaydı olmayan Marmara istasyonu {n}')
    if '--json' in sys.argv:
        json.dump([dict(T=str(s['T']), la=ON[s['j']]['la'], lo=ON[s['j']]['lo'], y=[st_ad[i] for i in s['y']],
                        r=[st_ad[i] for i in s['r']]) for s in ana], open(sys.argv[sys.argv.index('--json') + 1], 'w'))
