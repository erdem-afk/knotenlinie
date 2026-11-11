#!/usr/bin/env python3
"""TR-1 sürüm 2: yalnız üstveriyle uygunluk sayımı (hiçbir tenv3 serisi okunmaz).

Girdi dizini (ham dosyalar, depoya konmaz):
  DataHoldings.txt  https://geodesy.unr.edu/NGLStationPages/DataHoldings.txt
  steps.txt         https://geodesy.unr.edu/NGLStationPages/steps.txt
  ev30.csv          ComCat 2000-01-01..2026-01-01T00:00:00, M>=6.5, derinlik<=30
  ev70.csv          aynı aralık, derinlik<=70
  ev70_pre.csv      1985-01-01..2000-01-01, M>=6.5, derinlik<=70 (geçmiş şartları için; --katalog-2000 ile kapatılır)
  mt.json           (isteğe bağlı) {comcat_id: [rake1, rake2]} doğrultu atımlı sayımı için

Kullanım: python3 -I sayim_ustveri.py <girdi_dizini> [--doluluk yok|oran] [--katalog-2000] [--json çıktı.json]
Tanı bayrakları (ön kayıt kuralı DEĞİL, yalnız hangi kuralın ne kadar elediğini görmek için):
  --tani-kural2-yok, --tani-sicrama-yok, --tani-k2-sicrama-yok, --tani-b-gelecek, --tani-c-enaz, --yalniz-olay
İnceleme 2'deki sayılar (11 Kasım 2026 üstverisi, ~3 dk/koşu):
  ön kayıt kuralları, doluluk yok: geçerli olay kümesi 27, >=5 kontrol 15, K 11-12, plasebo 3
  ön kayıt kuralları, doluluk oran: 23 / 11 / K 9 / plasebo 1

Doluluk: 'yok' = şart atlanır (üst sınır); 'oran' = NumSol / (Dtend - Dtbeg + 1) >= 0,60 (yaklaşık).
Ön kayıttaki yıl uzunlukları tam güne aşağı yuvarlanır (5 yıl = 1826 g, 2 yıl = 730 g, 8 yıl = 2922 g, 13 yıl = 4748 g).
Hiçbir S, Δv ya da r hesaplanmaz.
"""
import csv, collections, datetime as dt, hashlib, itertools, json, math, os, sys
import numpy as np

D = sys.argv[1]
DOLULUK = 'oran' if '--doluluk' in sys.argv and sys.argv[sys.argv.index('--doluluk') + 1] == 'oran' else 'yok'
KAT2000 = '--katalog-2000' in sys.argv
TANI_K2 = '--tani-kural2-yok' in sys.argv      # tanı: 2. uygunluk kuralı kapalı
TANI_SC = '--tani-sicrama-yok' in sys.argv     # tanı: sıçrama yakınlık kuralı kapalı
TANI_K2SC = '--tani-k2-sicrama-yok' in sys.argv  # tanı: kod 2 kayıtları sıçrama yakınlık kuralına girmez
YALNIZ_OLAY = '--yalniz-olay' in sys.argv      # kontrolleri sayma (hızlı)
TANI_B = '--tani-b-gelecek' in sys.argv        # tanı: (b) yalnız [T, T+2 yıl]
TANI_C = '--tani-c-enaz' in sys.argv           # tanı: (c) en az n_y / n_r (eşitleme yok, en çok 8)
Y = 365.25
def gun(y): return int(math.floor(y * Y))
TD = dt.timedelta

# --- istasyonlar
st_ad, st_la, st_lo, st_b, st_e, st_n = [], [], [], [], [], []
with open(os.path.join(D, 'DataHoldings.txt')) as f:
    next(f)
    for l in f:
        p = l.split()
        try:
            la, lo = float(p[1]), (float(p[2]) + 180) % 360 - 180
            b, e, n = dt.date.fromisoformat(p[7]), dt.date.fromisoformat(p[8]), int(p[10])
        except Exception:
            continue
        st_ad.append(p[0]); st_la.append(la); st_lo.append(lo); st_b.append(b); st_e.append(e); st_n.append(n)
NS = len(st_ad)
LA, LO = np.radians(st_la), np.radians(st_lo)
MARMARA = np.array([39.5 <= a <= 42.0 and 26.0 <= o <= 31.5 for a, o in zip(st_la, st_lo)])

def hav(la, lo, LA_, LO_):
    la, lo = math.radians(la), math.radians(lo)
    a = np.sin((LA_ - la) / 2) ** 2 + np.cos(la) * np.cos(LA_) * np.sin((LO_ - lo) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

# --- basamaklar
def tarih(s):
    yy = int(s[:2]); yyyy = 2000 + yy if yy <= 79 else 1900 + yy
    return dt.datetime.strptime(f'{yyyy}{s[2:]}', '%Y%b%d').date()
k1 = collections.defaultdict(list); k2 = collections.defaultdict(list)
with open(os.path.join(D, 'steps.txt')) as f:
    for l in f:
        p = l.split()
        if len(p) < 4: continue
        try: t = tarih(p[1])
        except Exception: continue
        if t >= dt.date(2026, 1, 1): continue
        if p[2] == '1': k1[p[0]].append(t)
        elif p[2] == '2' and len(p) >= 7: k2[p[0]].append((t, float(p[3]), float(p[4])))

# --- kataloglar
def oku(fn):
    out = []
    with open(os.path.join(D, fn)) as f:
        for r in csv.DictReader(f):
            t = dt.date.fromisoformat(r['time'][:10])
            if t >= dt.date(2026, 1, 1): continue
            out.append(dict(id=r['id'], T=t, la=float(r['latitude']), lo=(float(r['longitude']) + 180) % 360 - 180,
                            M=float(r['mag']), z=float(r['depth']), yer=r['place']))
    return out
EV = oku('ev30.csv')
E70 = oku('ev70.csv') + ([] if KAT2000 else oku('ev70_pre.csv'))
E70la, E70lo = np.radians([e['la'] for e in E70]), np.radians([e['lo'] for e in E70])
E70T = np.array([e['T'].toordinal() for e in E70])

def deprem_var(la, lo, t0, t1, haric=None):
    d = hav(la, lo, E70la, E70lo)
    m = (d <= 100) & (E70T >= t0.toordinal()) & (E70T <= t1.toordinal())
    if haric is not None:
        m &= np.array([e['id'] != haric for e in E70])
    return bool(m.any())

# --- istasyon uygunluğu (T'ye göre önbellekli)
_cache = {}
def uygun(i, T):
    key = (i, T)
    if key in _cache: return _cache[key]
    w0, w1 = T - TD(days=gun(5) + 7), T - TD(days=7)
    H = T - TD(days=gun(2) + 7)
    ok = not MARMARA[i] and st_b[i] <= w0 and st_e[i] >= w1
    if ok and DOLULUK == 'oran':
        span = (st_e[i] - st_b[i]).days + 1
        ok = st_n[i] / span >= 0.60
    if ok:
        s = st_ad[i]; e8 = T - TD(days=gun(8) + 7)
        sicr = set(t for t in k1[s] if w0 <= t <= w1)
        for (t, thr, dd) in k2[s]:
            if not TANI_K2 and e8 <= t <= w1 and dd < thr / 4: ok = False; break
            if w0 <= t <= w1 and not TANI_K2SC: sicr.add(t)
        if ok and not TANI_SC:
            for t in sicr:
                if abs((t - H).days) < 30 or (t - w0).days < 30 or (w1 - t).days < 30: ok = False; break
    _cache[key] = ok
    return ok

def halka(M): return (500, 1000) if M >= 7.5 else (200, 500)

def kume(la, lo, T, M, ny=None, nr=None):
    d = hav(la, lo, LA, LO)
    r0, r1 = halka(M)
    ny_c = [i for i in np.lexsort((np.array(st_ad), d)) if d[i] <= 100]
    nr_c = [i for i in np.lexsort((np.array(st_ad), d)) if r0 <= d[i] <= r1]
    want_y, want_r = (8, 8) if TANI_C else ((ny or 8), (nr or 8))
    y = [];
    for i in ny_c:
        if uygun(i, T): y.append(i)
        if len(y) == want_y: break
    r = []
    for i in nr_c:
        if uygun(i, T): r.append(i)
        if len(r) == want_r: break
    if ny is None:
        return (y, r) if len(y) >= 3 and len(r) >= 3 else None
    if TANI_C: return (y, r) if len(y) >= ny and len(r) >= nr else None
    return (y, r) if len(y) == ny and len(r) == nr else None

def kontroller(ev, T, ny, nr):
    elat, elon = ev['la'], ev['lo']
    adaylar = [c for c in EV if c['id'] != ev['id']]
    adaylar.sort(key=lambda c: hashlib.sha256(f"{ev['id']}|{c['id']}".encode()).hexdigest())
    secilen = []
    for c in adaylar:
        if hav(elat, elon, np.radians([c['la']]), np.radians([c['lo']]))[0] < 600: continue  # (a)
        if any(hav(c['la'], c['lo'], np.radians([s['la']]), np.radians([s['lo']]))[0] < 150 for s, _ in secilen): continue  # (e)
        if deprem_var(c['la'], c['lo'], T if TANI_B else T - TD(days=gun(8)), T + TD(days=gun(2))): continue  # (b)
        k = kume(c['la'], c['lo'], T, ev['M'], ny, nr)  # (c)
        if k is None: continue
        ids = k[0] + k[1]
        if (hav(elat, elon, LA[ids], LO[ids]) < 600).any(): continue  # (d)
        secilen.append((c, k))
        if len(secilen) == 10: break
    return secilen

def bolge(p):
    s = p.lower()
    if 'japan' in s or 'tokachi' in s or 'tohoku' in s or 'kumamoto' in s or 'noto' in s: return 'Japonya'
    if 'chile' in s: return 'Şili'
    return 'öteki'

def bilesen(n, pairs):
    par = list(range(n))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for a, b in pairs: par[f(a)] = f(b)
    return len({f(i) for i in range(n)})

def dd(a, b): return hav(a['la'], a['lo'], np.radians([b['la']]), np.radians([b['lo']]))[0]

MT = {}
if os.path.exists(os.path.join(D, 'mt.json')):
    MT = json.load(open(os.path.join(D, 'mt.json')))
def dogrultu(i):
    r = MT.get(i)
    if not r: return None
    return any(abs(x) <= 30 or abs(x) >= 150 for x in r)

# --- olaylar
sonuc = []
for ev in EV:
    if ev['T'] > dt.date(2023, 12, 31): continue
    k = kume(ev['la'], ev['lo'], ev['T'], ev['M'])
    if k is None: continue
    ny, nr = len(k[0]), len(k[1])
    if YALNIZ_OLAY:
        sonuc.append(dict(ev=ev, ny=ny, nr=nr, st=set(k[0] + k[1]), nk=10, pl=None)); continue
    ks = kontroller(ev, ev['T'], ny, nr)
    # plasebo
    Tp = ev['T'] - TD(days=gun(5))
    pl = None
    if not deprem_var(ev['la'], ev['lo'], ev['T'] - TD(days=gun(13)), ev['T'] - TD(days=7), haric=ev['id']):
        kp = kume(ev['la'], ev['lo'], Tp, ev['M'])
        if kp is not None:
            kps = kontroller(ev, Tp, len(kp[0]), len(kp[1]))
            pl = len(kps)
    sonuc.append(dict(ev=ev, ny=ny, nr=nr, st=set(k[0] + k[1]), nk=len(ks), pl=pl, kid=[(c['id'], bolge(c['yer']), c['yer']) for c, _ in ks]))

gecerli = [s for s in sonuc if s['nk'] >= 5]
print(f'istasyon {NS}; olay (M>=6,5, z<=30, 2000-2025) {len(EV)}; T<=2023: {sum(e["T"]<=dt.date(2023,12,31) for e in EV)}')
print(f'doluluk={DOLULUK} katalog_2000={KAT2000}')
print(f'olay kümesi geçerli: {len(sonuc)}; >=5 kontrol: {len(gecerli)}')
print('kontrol sayısı dağılımı:', collections.Counter(s['nk'] for s in sonuc))
n = len(gecerli)
p_i = [(a, b) for a, b in itertools.combinations(range(n), 2)
       if abs((gecerli[a]['ev']['T'] - gecerli[b]['ev']['T']).days) < Y and dd(gecerli[a]['ev'], gecerli[b]['ev']) < 300]
p_ii = [(a, b) for a, b in itertools.combinations(range(n), 2)
        if abs((gecerli[a]['ev']['T'] - gecerli[b]['ev']['T']).days) < gun(5) and gecerli[a]['st'] & gecerli[b]['st']]
print(f'K yalnız (i) [üst]: {bilesen(n, p_i)}; K (i)+(ii) [alt]: {bilesen(n, p_i + p_ii)}')
plk = [i for i, s in enumerate(gecerli) if s['pl'] is not None and s['pl'] >= 5]
pp = [(a, b) for a, b in p_i + p_ii if a in plk and b in plk]
idx = {v: j for j, v in enumerate(plk)}
print(f'plasebosu hesaplanabilen olay: {len(plk)}; küme (alt tahmin, ana kümelemeyle): {bilesen(len(plk), [(idx[a], idx[b]) for a, b in pp])}')
print('bölge:', collections.Counter(bolge(s['ev']['yer']) for s in gecerli))
kk = collections.Counter(x[0] for s in gecerli for x in s.get('kid', []))
print('kontrol merkezi kullanımı: benzersiz', len(kk), '/ toplam', sum(kk.values()), '; en çok:', kk.most_common(5))
print('kontrol bölgeleri:', collections.Counter(x[2].split(', ')[-1] for s in gecerli for x in s.get('kid', [])).most_common(8))
print('M>=7,5:', sum(s['ev']['M'] >= 7.5 for s in gecerli))
if MT:
    print('doğrultu atımlı:', sum(dogrultu(s['ev']['id']) is True for s in gecerli),
          '/ MT yok:', sum(dogrultu(s['ev']['id']) is None for s in gecerli))
print('olaylar:')
for s in gecerli:
    e = s['ev']
    print(f"  {e['T']} {e['id']} M{e['M']} {e['yer'][:45]:45s} ny={s['ny']} nr={s['nr']} kontrol={s['nk']} plasebo_kontrol={s['pl']} SS={dogrultu(e['id'])}")
if '--json' in sys.argv:
    json.dump([s['ev']['id'] for s in gecerli], open(sys.argv[sys.argv.index('--json') + 1], 'w'))
