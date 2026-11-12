#!/usr/bin/env python3
"""TR-5b sürüm 2: dondurulacak olay / istasyon / kontrol / plasebo listesi, pilot listesi ve hacim (yalnız üstveri
ve katalog). Hiçbir dalga formu okunmaz, indirilmez ya da yoklanmaz.

Sürüm 1 (`tr5b_liste.py`) değiştirilmedi; bu betik onun kurallarını alır ve İNCELEME-1 düzeltmelerini ekler
(ön kayıt `kayit/onkayit/TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 2, §2):
  Ö3  (f) volkanik kural: bir istasyonu Smithsonian GVP Holosen volkanına <= 25 km olan olay ana hükümden çıkar;
      kontrol ve plasebo kontrolü merkezi atlanır (sıradaki gelir). Liste `tr5b_gvp_holosen.csv` (sha256 donduruldu).
      Sürüm 1'in ad kuralı (Hawaii, Akutan, Jan Mayen) kaldırıldı; yerini bu kural aldı.
  Ö4  kota İSTASYON düzeyinde ve koşuda KULLANILAN kontrollere (yedekler dahil) göre işler: aşama 0'da olaylar
      (T, kimlik) sırasıyla işlenir, kotası dolmuş istasyonu içeren aday atlanır (`tr5b_asama0.kota_ata`). Listede
      kota uygulanmaz; liste 10 adayı (a)-(f) ile seçer ve kotanın "hepsi dolu" önizlemesini yazar.
      (e) merkezler arası >= 200 km ve aynı olayın adayları ortak istasyon içermez.
  Ö5  plasebo istasyonları = olay istasyonları ∩ (plasebo kapsamı ve ay doluluğu). Kesişim boşsa plasebo yok.
  E3c aygıt önizlemesi olay istasyonlarında [T-1095, T+30]: `aygit_degisimi_Z` (pencere [T-1095, T-8]) ve
      `aygit_degisimi_PK` (yalnız (T-8, T+30]; istasyon PK'den düşer, hüküm ölçüsünde kalır).
  E1  pilot P2 aday olayları (listede olmayan M>=6 olaylar) ve P1 / P2 / 1b hacimleri.

Girdi (depo dışında): <ham> (FDSN üstverisi), <ngl> (ev*.csv), <tr2> (m6_havuz.csv, mekanizma.jsonl),
<m5> (ComCat M>=5,0, z<=70 km, 1990-2025, m5_*.csv). Depoda: tr5_doluluk.csv, tr5b_gvp_holosen.csv.
Çıktı (bu dizine): tr5b_liste_s2.json (bağlayıcı), tr5b_olaylar_s2.csv, tr5b_kontroller_s2.csv,
tr5b_pilot_s2.csv, tr5b_ozet_s2.json.

Kullanım: python3 -I -B tr5b_liste_s2.py <ham> <ngl> <tr2> <m5_dizini>
"""
import collections, csv, datetime as dt, glob, hashlib, importlib.util, json, math, os, re, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
HAM, NGL, TR2, M5 = sys.argv[1:5]
TD = dt.timedelta

_spec = importlib.util.spec_from_file_location('doluluk_yokla', os.path.join(BURASI, 'doluluk_yokla.py'))
DY = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(DY)
ns = DY.betik_yukle('sayim_ustveri.py', [HAM, NGL, TR2], DY.KOSU)
np = ns['np']; hav = ns['hav']; yil = ns['yil']; ANAHTAR = ns['ANAHTAR']
IDX = {k: i for i, k in enumerate(ANAHTAR)}

# ------------------------------------------------------------------ önceden sabit sayılar (ön kayıt sürüm 2, §2-§5)
TABAN = 3                   # yıl; pencere [T - 1095 g, T - 8 g]
KORUMA = 7                  # T-7 g ... T-1 g okunmaz
N_KONTROL = 5               # bağlayıcı kontrol sayısı (aşama 0 ve 1b'den geçen ilk 5)
N_YEDEK = 10                # aday listesi uzunluğu (1-10)
PK_SONRA = 30               # pozitif kontrol: [T+1, T+30] (yalnız olay istasyonları)
M5_R, M5_GUN = 50.0, 60     # maske: istasyona <= 50 km, M>=5,0, z<=70 km depremden sonra 60 gün
SAAT = 4                    # gün başına saat (yerel güneş saati 00-04)
B_ORNEK = 1.3               # bayt/örnek (TR-5 sayımı §5.1)
VOLKAN_KM = 25.0            # Ö3 (f): istasyon-volkan uzaklığı
KONTROL_ARA = 200.0         # Ö4 (e): aynı olayın kontrol merkezleri arası en az uzaklık
P2_N, P2_ONCE, P2_SONRA = 20, 400, 30          # pilot P2: 20 olay, [T-400, T+30]
P2_T = (dt.date(2005, 1, 1), dt.date(2023, 12, 31))
P1_N = 24
TR4_KUTU = (40.0, 41.6, 26.5, 30.5)            # enlem, enlem, boylam, boylam
TR1_KUTU = (39.5, 42.0, 26.0, 31.5)
HARIC_MERKEZ, HARIC_AG = {'KOERI'}, {'6G'}      # kontrollerde ve P2'de kullanılmaz (sürüm 1 §2.3)

# ------------------------------------------------------------------ GVP Holosen volkan listesi (Ö3)
GVP_YOL = os.path.join(BURASI, 'tr5b_gvp_holosen.csv')
GVP = list(csv.DictReader(open(GVP_YOL, encoding='utf-8')))
GLA = np.array([float(r['enlem']) for r in GVP]); GLO = np.array([float(r['boylam']) for r in GVP])
def volkan(la, lo):
    """En yakın Holosen volkanı (ad, km) ya da None (> 25 km)."""
    d = hav(la, lo, GLA, GLO); j = int(np.argmin(d))
    return (GVP[j]['ad'], round(float(d[j]), 1)) if d[j] <= VOLKAN_KM else None

# ------------------------------------------------------------------ doluluk süzgeci (tr5_doluluk.csv, ana)
dolu = {}
for r in csv.DictReader(open(os.path.join(BURASI, 'tr5_doluluk.csv'))):
    dolu[(r['ag'], r['ist'], dt.date.fromisoformat(r['bas']), dt.date.fromisoformat(r['son']))] = r['dolu_ana'] == 'True'
ozg_uygun, ozg_kontrol = ns['uygun'], ns['kontrol_sec']
durum = dict(kontrol=False)
def kontrol_sec(e, R, n_min):
    durum['kontrol'] = True
    try: return ozg_kontrol(e, R, n_min)
    finally: durum['kontrol'] = False
def uygun(la, lo, R, a, b, acik_sart=True):
    if durum['kontrol']: return ozg_uygun(la, lo, R, a, b, acik_sart)
    key = (la, lo, R)
    if key not in ns['_yakin']:
        d = hav(la, lo, ns['SLA'], ns['SLO']); ns['_yakin'][key] = np.nonzero(d <= R)[0]; ns['_uzak'][key] = d
    idx = [i for i in ns['_yakin'][key] if (ns['ACIK'][i] or not acik_sart) and ns['kapsar'](ANAHTAR[i], a, b)
           and dolu.get((ANAHTAR[i][0], ANAHTAR[i][1], a, b), False)]
    y = sorted(ns['yerler'](idx), key=lambda i: (ns['_uzak'][key][i], ANAHTAR[i]))
    return y[:ns['N_MAX']], None
ns['uygun'], ns['kontrol_sec'] = uygun, kontrol_sec

ns['TABAN_YIL'], ns['ONCE_TEMIZ'] = TABAN, TABAN + 2
EV60 = [e for e in ns['H6'] if e['t'] >= dt.date(2000, 1, 1) and e['z'] <= 30.0]
sat, gecen = ns['olay_say'](EV60, 100.0, 1)
kg = [g for g in gecen if g.get('kgecer')]
K, kok = ns['kumele'](kg)
pl = ns['plasebo_say'](kg, 100.0, 1)
Kp = ns['kumele'](pl)[0] if pl else 0
print(f'olay {len(kg)}, K {K}; plasebo olay {len(pl)}, K_plasebo {Kp}')
assert (K, Kp) == (37, 20), 'TR-5 Ek 1 sayımı yeniden üretilemedi'

kume_of = {g['e']['id']: kok[i] for i, g in enumerate(kg)}
kume_ad = {}
for r_ in set(kok):
    ilk = min((g for i, g in enumerate(kg) if kok[i] == r_), key=lambda g: (g['e']['t'], g['e']['id']))
    kume_ad[r_] = ilk['e']['id']

# ------------------------------------------------------------------ M>=5 katalog (maske)
M5L = []
for f in sorted(glob.glob(os.path.join(M5, 'm5_*.csv'))):
    for r in csv.DictReader(open(f)):
        if r['type'] != 'earthquake': continue
        t = dt.date.fromisoformat(r['time'][:10])
        if t >= dt.date(2026, 1, 1): continue
        M5L.append((t, float(r['latitude']), float(r['longitude']), float(r['depth'] or 0), float(r['mag']), r['id']))
M5T = np.array([x[0].toordinal() for x in M5L]); M5LA = np.array([x[1] for x in M5L]); M5LO = np.array([x[2] for x in M5L])
M5ID = [x[5] for x in M5L]
def maske_gun(k, a, b, haric=()):
    la, lo = ns['konum'][k]
    sec = (M5T >= (a - TD(days=M5_GUN)).toordinal()) & (M5T <= b.toordinal())
    if not sec.any(): return 0, []
    d = hav(la, lo, M5LA[sec], M5LO[sec]); ids = np.nonzero(sec)[0][d <= M5_R]
    gun = set()
    for j in ids:
        if M5ID[j] in haric: continue
        for x in range(M5T[j], M5T[j] + M5_GUN):
            if a.toordinal() <= x <= b.toordinal(): gun.add(x)
    return len(gun), sorted(M5ID[j] for j in ids if M5ID[j] not in haric)

# ------------------------------------------------------------------ aygıt önizlemesi (yalnız Z üstverisi)
EPOK = collections.defaultdict(lambda: collections.defaultdict(list))
for f in [os.path.join(HAM, 'fedcatalog_kanal.txt')] + sorted(glob.glob(os.path.join(HAM, 'ek_*_kanal.txt'))):
    for l in open(f, encoding='utf-8', errors='replace'):
        if l.startswith('#') or '|' not in l: continue
        q = l.rstrip('\n').split('|')
        if len(q) < 17 or q[3] not in ('BHZ', 'HHZ'): continue
        try: b_ = dt.date.fromisoformat(q[15][:10])
        except ValueError: continue
        sens = re.sub(r'S/N[:#\s]*\S+', '', q[10]).strip().lower()
        EPOK[(q[0], q[1])][(q[2].strip(), q[3])].append((b_, sens, q[8].strip(), q[9].strip()))
def aygit_degisimi(k, a, b):
    """(a, b] içinde başlayan bir Z epoğunda, aynı konum ve kanalın önceki epoğuna göre sensör tanımı (seri numarası
    atılarak) ya da yönelim değişiyorsa True (ön kayıt §2.5)."""
    for L in EPOK.get(k, {}).values():
        L = sorted(set(L))
        for x, y in zip(L, L[1:]):
            if a < y[0] <= b and x[1:] != y[1:]: return True
    return False

def ist_kayit(i, la, lo, a, b, haric=(), T=None):
    k = ANAHTAR[i]; mg, mo = maske_gun(k, a, b, haric)
    v = volkan(float(ns['SLA'][i]), float(ns['SLO'][i]))
    out = dict(ist='.'.join(k), merkez=ns['merkez_of'][k], la=round(float(ns['SLA'][i]), 4), lo=round(float(ns['SLO'][i]), 4),
               uzaklik_km=round(float(hav(la, lo, ns['SLA'][i], ns['SLO'][i])), 1), sps_min=ns['oran_min'][k],
               maske_gun=mg, maske_olay=mo, aygit_degisimi_Z=aygit_degisimi(k, a, b),
               volkan=(dict(ad=v[0], km=v[1]) if v else None))
    if T is not None:   # olay istasyonu: E3c, (T-8, T+30] yalnız PK
        out['aygit_degisimi_PK'] = aygit_degisimi(k, T - TD(days=KORUMA + 1), T + TD(days=PK_SONRA))
    return out

def pencere(T):
    return T - yil(TABAN), T - TD(days=KORUMA + 1)

# ------------------------------------------------------------------ kontrol seçimi (Ö3, Ö4)
_s0 = importlib.util.spec_from_file_location('tr5b_asama0', os.path.join(BURASI, 'tr5b_asama0.py'))
A0 = importlib.util.module_from_spec(_s0); _s0.loader.exec_module(A0)
KOTA = A0.KOTA
atla_say = collections.Counter()
def kontrol_istasyon(la, lo, a, b):
    key = (la, lo, 100.0)
    if key not in ns['_yakin']:
        d = hav(la, lo, ns['SLA'], ns['SLO']); ns['_yakin'][key] = np.nonzero(d <= 100.0)[0]; ns['_uzak'][key] = d
    idx = [i for i in ns['_yakin'][key] if ns['ACIK'][i] and ns['kapsar'](ANAHTAR[i], a, b)
           and ns['merkez_of'][ANAHTAR[i]] not in HARIC_MERKEZ and ANAHTAR[i][0] not in HARIC_AG]
    return sorted(ns['yerler'](idx), key=lambda i: (ns['_uzak'][key][i], ANAHTAR[i]))[:ns['N_MAX']]

def kontrol_kota(e, T, anahtar_id, tur, kume):
    """SHA-256(anahtar|merkez) sırası; (a)-(d) sürüm 1 ile aynı; (e) 200 km ve ortak istasyon yok; (f) volkanik
    merkez atlanır. Kota burada uygulanmaz (aşama 0, kullanılan adaylara göre)."""
    a, b = T - yil(TABAN), T - TD(days=1)
    sira = sorted(ns['MERKEZ'], key=lambda c: hashlib.sha256((anahtar_id + '|' + c['id']).encode()).hexdigest())
    sec = []
    for c in sira:
        if hav(e['la'], e['lo'], c['la'], c['lo']) < ns['KONTROL_UZAK']: continue
        if any(hav(c['la'], c['lo'], s['la'], s['lo']) < KONTROL_ARA for s, _ in sec): continue
        st = kontrol_istasyon(c['la'], c['lo'], a, b)
        if len(st) < 1: continue
        if any(hav(ns['SLA'][i], ns['SLO'][i], e['la'], e['lo']) < ns['KONTROL_UZAK'] for i in st): continue
        if not ns['sakin'](c['la'], c['lo'], T - yil(TABAN + 2), T + yil(2)): continue
        if any(i in st_ for _, st_ in sec for i in st): atla_say['ortak_istasyon'] += 1; continue
        if any(volkan(float(ns['SLA'][i]), float(ns['SLO'][i])) for i in st): atla_say[f'volkan_{tur}'] += 1; continue
        sec.append((c, st))
        if len(sec) >= N_YEDEK: break
    return sec

def kontrol_kayit(sira, c, cst, e, a, b):
    return dict(sira=sira, merkez_id=c['id'], la=c['la'], lo=c['lo'], M=c['M'],
                uzaklik_olaya_km=round(float(hav(e['la'], e['lo'], c['la'], c['lo'])), 0),
                istasyon=[ist_kayit(i, c['la'], c['lo'], a, b) for i in cst])

# ------------------------------------------------------------------ liste
olaylar = []
kg_s = sorted(kg, key=lambda g: (g['e']['t'], g['e']['id']))
for g in kg_s:
    e = g['e']; T = e['t']; a, b = pencere(T)
    st = [IDX[k] for k in g['st']]
    ist = [ist_kayit(i, e['la'], e['lo'], a, b, haric={e['id']}, T=T) for i in st]
    vk = [dict(ist=s['ist'], **s['volkan']) for s in ist if s['volkan']]
    kume = kume_ad[kume_of[e['id']]]
    ks = kontrol_kota(e, T, e['id'], 'olay', kume)
    rec = dict(id=e['id'], t=str(T), M=e['M'], z=e['z'], la=e['la'], lo=e['lo'], yer=e['yer'], bolge=ns['bolge'](e),
               mek=ns['mek'].get(e['id'], '?'), kume=kume, volkanik=bool(vk), volkan=vk,
               pencere=[str(a), str(b)], pk_pencere=[str(T + TD(days=1)), str(T + TD(days=PK_SONRA))],
               istasyon=ist, kontrol=[kontrol_kayit(s + 1, c, cst, e, a, b) for s, (c, cst) in enumerate(ks)],
               plasebo=None, plasebo_dusme=None)
    olaylar.append(rec)

# plasebo (Ö5): olay istasyonları ∩ ([T-2191 g, T-1 g] kesintisiz ve ay doluluğu); dış merkez [T-8 yıl, T) sakin
pl_id = {g['e']['id'] for g in pl}
for rec, g in zip(olaylar, kg_s):
    assert rec['id'] == g['e']['id']
    if rec['id'] not in pl_id: continue
    e = g['e']; T = e['t']; Tp = T - yil(TABAN); a, b = pencere(Tp)
    pa, pb = T - yil(2 * TABAN), T - TD(days=1)
    st = [IDX[k] for k in g['st'] if ns['kapsar'](k, pa, pb) and dolu.get((k[0], k[1], pa, pb), False)]
    if not st:
        rec['plasebo_dusme'] = 'olay istasyonlarıyla kesişim boş (Ö5)'; continue
    ks = kontrol_kota(e, Tp, e['id'] + '|plasebo', 'plasebo', rec['kume'])
    rec['plasebo'] = dict(T=str(Tp), pencere=[str(a), str(b)],
                          istasyon=[ist_kayit(i, e['la'], e['lo'], a, b) for i in st],
                          kontrol=[kontrol_kayit(s + 1, c, cst, e, a, b) for s, (c, cst) in enumerate(ks)])

# ------------------------------------------------------------------ pozitif kontrol kümeleri
def L_km(M): return 10 ** (-2.44 + 0.59 * M)
ana = [r for r in olaylar if not r['volkanik']]
yakin_pk = [r for r in ana if min(s['uzaklik_km'] for s in r['istasyon']) <= max(30.0, 2 * L_km(r['M']))]
PK_KUME = sorted({r['kume'] for r in yakin_pk})

# ------------------------------------------------------------------ pilot P2 aday olayları (E1; listede olmayan)
def kutuda(la, lo, k): return k[0] <= la <= k[1] and k[2] <= lo <= k[3]
rol_pen = collections.defaultdict(list)   # istasyon -> [(a, b)] TR-5b'nin bütün rolleri
for r in olaylar:
    for s in r['istasyon']: rol_pen[s['ist']].append((dt.date.fromisoformat(r['pencere'][0]), dt.date.fromisoformat(r['pk_pencere'][1])))
    for c in r['kontrol']:
        for s in c['istasyon']: rol_pen[s['ist']].append(tuple(dt.date.fromisoformat(x) for x in r['pencere']))
    if r['plasebo']:
        p = r['plasebo']
        for s in p['istasyon']: rol_pen[s['ist']].append(tuple(dt.date.fromisoformat(x) for x in p['pencere']))
        for c in p['kontrol']:
            for s in c['istasyon']: rol_pen[s['ist']].append(tuple(dt.date.fromisoformat(x) for x in p['pencere']))
liste_id = {r['id'] for r in olaylar}
p2_aday = []
for e in sorted([e for e in ns['H6'] if P2_T[0] <= e['t'] <= P2_T[1] and e['z'] <= 30.0 and e['M'] >= 6.0
                 and e['id'] not in liste_id],
                key=lambda e: hashlib.sha256(('pilot|' + e['id']).encode()).hexdigest()):
    if kutuda(e['la'], e['lo'], TR4_KUTU) or kutuda(e['la'], e['lo'], TR1_KUTU): continue
    T = e['t']; a, b = T - TD(days=P2_ONCE), T + TD(days=P2_SONRA); esik = max(30.0, 2 * L_km(e['M']))
    d = hav(e['la'], e['lo'], ns['SLA'], ns['SLO'])
    adaylar = sorted(np.nonzero(d <= esik)[0], key=lambda i: (d[i], ANAHTAR[i]))
    sec = None
    for i in adaylar:
        k = ANAHTAR[i]; nm = '.'.join(k)
        if not ns['ACIK'][i] or not ns['kapsar'](k, a, b): continue
        if ns['merkez_of'][k] in HARIC_MERKEZ or k[0] in HARIC_AG: continue
        if kutuda(float(ns['SLA'][i]), float(ns['SLO'][i]), TR1_KUTU): continue
        if aygit_degisimi(k, a, b): continue
        if volkan(float(ns['SLA'][i]), float(ns['SLO'][i])): continue          # Ö3 simetrisi: PK volkaniksiz
        if any(x <= b and a <= y for x, y in rol_pen.get(nm, [])): continue
        sec = i; break
    if sec is None: continue
    if any(hav(e['la'], e['lo'], q['la'], q['lo']) <= 300.0 and abs((T - dt.date.fromisoformat(q['t'])).days) <= 365
           for q in p2_aday): continue
    v = volkan(float(ns['SLA'][sec]), float(ns['SLO'][sec]))
    p2_aday.append(dict(sira=len(p2_aday) + 1, id=e['id'], t=str(T), M=e['M'], z=e['z'], la=e['la'], lo=e['lo'],
                        yer=e['yer'], ist='.'.join(ANAHTAR[sec]), merkez=ns['merkez_of'][ANAHTAR[sec]],
                        sps_min=ns['oran_min'][ANAHTAR[sec]], uzaklik_km=round(float(d[sec]), 1), esik_km=round(esik, 1),
                        pencere=[str(a), str(b)], volkan=(f'{v[0]} {v[1]} km' if v else '')))
    if len(p2_aday) >= P2_N: break

# ------------------------------------------------------------------ hacim
def birlesim(iv):
    m = []
    for b_, e_ in sorted(iv):
        if m and b_ <= m[-1][1] + TD(days=1): m[-1][1] = max(m[-1][1], e_)
        else: m.append([b_, e_])
    return m
def gun_say(m): return sum((e_ - b_).days + 1 for b_, e_ in m)
def D(x): return dt.date.fromisoformat(x) if isinstance(x, str) else x
def hacim_hesap(kalemler, cikar=None):
    """kalemler: [(ist, merkez, sps, a, b)]. cikar: aynı biçimde, önceden indirilmiş günler (düşülür)."""
    pen = collections.defaultdict(list); sps = {}; mk = {}
    for s, m_, r_, a, b in kalemler: pen[s].append((D(a), D(b))); sps[s] = r_; mk[s] = m_
    cik = collections.defaultdict(list)
    for s, _, _, a, b in (cikar or []): cik[s].append((D(a), D(b)))
    tb = collections.Counter(); ig = 0; istek = collections.Counter()
    for s, iv in pen.items():
        m = birlesim(iv); n = gun_say(m)
        if s in cik:
            n = gun_say(birlesim(iv + cik[s])) - gun_say(birlesim(cik[s]))
        ig += n; tb[mk[s]] += n * SAAT * 3600 * sps[s] * B_ORNEK * 3 / 1e12; istek[mk[s]] += n
    return dict(istasyon=len(pen), istasyon_gunu=ig, TB=round(sum(tb.values()), 4),
                merkez_TB={m: round(v, 4) for m, v in tb.most_common()},
                istek_30g_paket=sum(math.ceil(v / 30) for v in istek.values()), merkez_istasyon_gunu=dict(istek.most_common()))
def kal(s, a, b): return (s['ist'], s['merkez'], s['sps_min'], a, b)
olay_pl, kon5, kon10, plk5, plk10 = [], [], [], [], []
for r in olaylar:
    for s in r['istasyon']:
        olay_pl.append(kal(s, *r['pencere'])); olay_pl.append(kal(s, *r['pk_pencere']))
    for c in r['kontrol'][:N_KONTROL]: kon5 += [kal(s, *r['pencere']) for s in c['istasyon']]
    for c in r['kontrol']: kon10 += [kal(s, *r['pencere']) for s in c['istasyon']]
    if r['plasebo']:
        p = r['plasebo']
        olay_pl += [kal(s, *p['pencere']) for s in p['istasyon']]
        for c in p['kontrol'][:N_KONTROL]: plk5 += [kal(s, *p['pencere']) for s in c['istasyon']]
        for c in p['kontrol']: plk10 += [kal(s, *p['pencere']) for s in c['istasyon']]
# P1: volkaniksiz olayların (T, kimlik) sırasıyla ilk 24'ü; 1. aday kontrolün en yakın istasyonu (vekil; gerçek seçim aşama 0'da)
p1 = []
for r in [r for r in olaylar if not r['volkanik']][:P1_N]:
    if r['kontrol']:
        s = min(r['kontrol'][0]['istasyon'], key=lambda s: s['uzaklik_km']); p1.append(kal(s, *r['pencere']))
p2 = [(q['ist'], q['merkez'], q['sps_min'], q['pencere'][0], q['pencere'][1]) for q in p2_aday]
HACIM = {
    '1b_olay_plasebo (olay [T-1095,T-8] + PK [T+1,T+30] + plasebo)': hacim_hesap(olay_pl),
    '1b_kontrol_5_plasebo_kontrol_5 (olay tarafına ek)': hacim_hesap(kon5 + plk5, cikar=olay_pl),
    'A_toplam (olay + plasebo + kontrol 5 + plasebo kontrolü 5)': hacim_hesap(olay_pl + kon5 + plk5),
    'B_toplam (kontrol 10, plasebo kontrolü 10)': hacim_hesap(olay_pl + kon10 + plk10),
    'pilot_P1 (24 sahte olay istasyon-penceresi; vekil: 1. aday, en yakın istasyon)': hacim_hesap(p1),
    'pilot_P2 (20 olay, [T-400, T+30], en yakın istasyon)': hacim_hesap(p2),
    'A_toplam_pilot_P1_dusulmus (P1 verisi yeniden kullanılır)': hacim_hesap(olay_pl + kon5 + plk5, cikar=p1),
}

# ------------------------------------------------------------------ özet sayılar
def kume_say(L): return len({r['kume'] for r in L})
def gecerli_ist(L, alan='aygit_degisimi_Z'): return [s for s in L if not s[alan]]
pl_ana = [r for r in ana if r['plasebo']]
ozet = dict(surum='TR-5b liste sürüm 2', olay=len(olaylar), K=kume_say(olaylar), K_ana_volkaniksiz=kume_say(ana),
            volkanik_olay=[dict(id=r['id'], kume=r['kume'], volkan=r['volkan']) for r in olaylar if r['volkanik']],
            plasebo_olay=len([r for r in olaylar if r['plasebo']]), K_plasebo=kume_say([r for r in olaylar if r['plasebo']]),
            K_plasebo_eslesik_volkaniksiz=kume_say(pl_ana),
            plasebo_dusen=[dict(id=r['id'], neden=r['plasebo_dusme']) for r in olaylar if r['plasebo_dusme']])
ozet['gvp'] = dict(dosya='tr5b_gvp_holosen.csv', volkan=len(GVP), km=VOLKAN_KM,
                   sha256=hashlib.sha256(open(GVP_YOL, 'rb').read()).hexdigest())
ozet['kontrol_aday_sayisi'] = dict(sorted(collections.Counter(len(r['kontrol']) for r in olaylar).items()))
ozet['plasebo_kontrol_aday_sayisi'] = dict(sorted(collections.Counter(len(r['plasebo']['kontrol']) for r in olaylar if r['plasebo']).items()))
ozet['kontrol_atlama_nedeni'] = dict(atla_say)
ozet['K_ana_aday_ge5'] = kume_say([r for r in ana if len(r['kontrol']) >= N_KONTROL])
ozet['K_ana_aday_ge4'] = kume_say([r for r in ana if len(r['kontrol']) >= 4])
ozet['K_plasebo_aday_ge4'] = kume_say([r for r in pl_ana if len(r['plasebo']['kontrol']) >= 4])
# Z aygıt önizlemesi sonrası (bağlayıcı denetim aşama 0'da üç bileşenle)
def ok_olay(r): return bool(gecerli_ist(r['istasyon'])) and sum(1 for c in r['kontrol'] if gecerli_ist(c['istasyon'])) >= 4
def ok_pl(r): return r['plasebo'] and bool(gecerli_ist(r['plasebo']['istasyon'])) and \
    sum(1 for c in r['plasebo']['kontrol'] if gecerli_ist(c['istasyon'])) >= 4
ana_ok = [r for r in ana if ok_olay(r)]
ozet['Z_onizleme'] = dict(K=kume_say(ana_ok), K_p=len({r['kume'] for r in ana if ok_pl(r)} & {r['kume'] for r in ana_ok}),
                          olay_ist_Z=sum(1 for r in olaylar for s in r['istasyon'] if s['aygit_degisimi_Z']),
                          olay_ist_yalniz_PK=[(r['id'], s['ist']) for r in olaylar for s in r['istasyon']
                                              if s['aygit_degisimi_PK'] and not s['aygit_degisimi_Z']],
                          tum_istasyonu_dusen_olay=[r['id'] for r in olaylar if not gecerli_ist(r['istasyon'])],
                          kontrol_ist_Z=sum(1 for r in olaylar for c in r['kontrol'] for s in c['istasyon'] if s['aygit_degisimi_Z']))
ozet['olay_istasyon_sayisi'] = dict(sorted(collections.Counter(len(r['istasyon']) for r in ana).items()))
uz = sorted(s['uzaklik_km'] for r in ana for s in r['istasyon'])
ozet['olay_istasyon_uzaklik_km_volkaniksiz'] = dict(n=len(uz), medyan=uz[len(uz) // 2], q25=uz[len(uz) // 4], q75=uz[3 * len(uz) // 4])
uzy = sorted(min(s['uzaklik_km'] for s in r['istasyon']) for r in ana)
ozet['en_yakin_istasyon_medyan_km'] = uzy[len(uzy) // 2]
ozet['bolge_kume_volkaniksiz'] = dict(collections.Counter(next(r['bolge'] for r in ana if r['kume'] == k) for k in sorted({r["kume"] for r in ana})))
ozet['mekanizma_olay_volkaniksiz'] = dict(collections.Counter(r['mek'] for r in ana))
ozet['M_dagilimi_volkaniksiz'] = dict(collections.Counter('6.0-6.4' if r['M'] < 6.5 else ('6.5-6.9' if r['M'] < 7 else '>=7') for r in ana))
ozet['pk'] = dict(olay=len(yakin_pk), kume=len(PK_KUME), kumeler=PK_KUME,
                  aygit_PK_dusen=[(r['id'], s['ist']) for r in yakin_pk for s in r['istasyon'] if s['aygit_degisimi_PK'] or s['aygit_degisimi_Z']],
                  en_yakin=[dict(kume=r['kume'], id=r['id'], M=r['M'], ist=min(r['istasyon'], key=lambda s: s['uzaklik_km'])['ist'],
                                 km=min(s['uzaklik_km'] for s in r['istasyon'])) for r in yakin_pk])
# istasyon kotası önizlemesi (Ö4; dinamik kota aşama 0'da, tr5b_asama0.kota_ata ile aynı kod)
K0_h, Kp0_h, ayr_h = A0.K_say(dict(olaylar=olaylar), lambda rol, r, s: True)
K0_z, Kp0_z, ayr_z = A0.K_say(dict(olaylar=olaylar), lambda rol, r, s: not s['aygit_degisimi_Z'])
ozet['kota_onizleme'] = dict(
    hepsi_dolu=dict(K0=K0_h, K_p0=Kp0_h, kontrol_4ten_az=[i for i, v in ayr_h.items() if len(v['kontrol']) < 4],
                    plasebo_kontrol_4ten_az=[i for i, v in ayr_h.items() if olaylar[[r['id'] for r in olaylar].index(i)]['plasebo']
                                             and len(v['plasebo_kontrol']) < 4]),
    hepsi_dolu_Z_aygit=dict(K0=K0_z, K_p0=Kp0_z))
# varsayımsal doluluk benzetimi (bilgi; aşama 0'ın G0 olasılığı için kaba ön bilgi, karar vermez)
_rng = np.random.default_rng(20261112)
mc = {}
for q_e in (1.0, 0.85):
    for p_c in (0.4, 0.6, 0.8):
        ks = []
        for _ in range(300):
            cek = {}
            def f(rol, r, s):
                key = (rol, r['id'] if rol in ('olay', 'plasebo') else r['t'], s['ist'])
                if key not in cek:
                    p_ = q_e if rol in ('olay', 'plasebo') else p_c
                    cek[key] = (not s['aygit_degisimi_Z']) and _rng.random() < p_
                return cek[key]
            k0, kp0, _ = A0.K_say(dict(olaylar=olaylar), f); ks.append((k0, kp0))
        ks = np.array(ks)
        mc[f'olay_ist_tutar={q_e}_kontrol_ist_dolu={p_c}'] = dict(
            K0_medyan=float(np.median(ks[:, 0])), K_p0_medyan=float(np.median(ks[:, 1])),
            P_G0_gecer=round(float(np.mean((ks[:, 0] >= A0.KAPI_K) & (ks[:, 1] >= A0.KAPI_KP))), 3))
ozet['G0_benzetim_varsayimsal'] = mc
ozet['p2'] = dict(aday=len(p2_aday), en_yakin_km_medyan=sorted(q['uzaklik_km'] for q in p2_aday)[len(p2_aday) // 2] if p2_aday else None)
ozet['hacim'] = HACIM

# ------------------------------------------------------------------ yaz
liste = dict(surum='TR-5b liste 2', tarih='2026-11-12',
             kural=dict(M_min=6.0, z_max=30.0, T=['2000-01-01', '2023-12-31'], R_km=100.0, n_min=1, taban_yil=TABAN,
                        koruma_gun=KORUMA, n_kontrol=N_KONTROL, n_aday=N_YEDEK, pk_sonra_gun=PK_SONRA,
                        maske=dict(M_min=5.0, z_max=70.0, R_km=M5_R, gun=M5_GUN), saat_gun=SAAT,
                        volkan=dict(liste='tr5b_gvp_holosen.csv', km=VOLKAN_KM, olay='ana hükümden çıkar (bilgi satırı 1)',
                                    kontrol='merkez atlanır'),
                        kontrol_kota=dict(birim='istasyon', kume=KOTA, isler='aşama 0 ve 1b, kullanılan adaylar (yedekler dahil), (T, kimlik) sırası'),
                        kontrol_ara_km=KONTROL_ARA, kontrol_ortak_istasyon=False,
                        kontrol_haric_merkez=sorted(HARIC_MERKEZ), kontrol_haric_ag=sorted(HARIC_AG),
                        plasebo_istasyon='olay istasyonları ∩ plasebo kapsamı ve ay doluluğu',
                        aygit_olay=['T-1095', 'T+30'], aygit_yalniz_PK=['T-7', 'T+30'],
                        pk_kume=PK_KUME, pk_olay_dko='en yakın geçerli istasyon',
                        p2=dict(n=P2_N, pencere=[-P2_ONCE, P2_SONRA], T=[str(x) for x in P2_T], tr4_kutu=TR4_KUTU,
                                tr1_kutu=TR1_KUTU, sira='SHA-256(pilot|kimlik)', kume='300 km ve 365 g içinde sırada ilk'),
                        p1=dict(n=P1_N),
                        doluluk_suzgeci='tr5_doluluk.csv dolu_ana (olay ve plasebo istasyonları)'),
             girdi_sha256={os.path.basename(f): hashlib.sha256(open(f, 'rb').read()).hexdigest()
                           for f in [os.path.join(BURASI, 'tr5_doluluk.csv'), GVP_YOL, os.path.join(NGL, 'ev.csv'),
                                     os.path.join(TR2, 'm6_havuz.csv'), os.path.join(HAM, 'fedcatalog_kanal.txt')] +
                           sorted(glob.glob(os.path.join(M5, 'm5_*.csv')))},
             olaylar=olaylar, pilot_p2=p2_aday)
yol = os.path.join(BURASI, 'tr5b_liste_s2.json')
with open(yol, 'w', encoding='utf-8') as f:
    json.dump(liste, f, ensure_ascii=False, indent=1, sort_keys=True, default=str); f.write('\n')
with open(os.path.join(BURASI, 'tr5b_olaylar_s2.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id', 't', 'M', 'z', 'la', 'lo', 'bolge', 'mek', 'kume', 'volkanik', 'volkan', 'istasyonlar', 'uzaklik_km',
                'aygit_Z', 'aygit_PK', 'kontrol_aday', 'plasebo_T', 'plasebo_istasyonlar', 'plasebo_kontrol_aday', 'pk', 'yer'])
    for r in olaylar:
        p = r['plasebo']
        w.writerow([r['id'], r['t'], r['M'], r['z'], r['la'], r['lo'], r['bolge'], r['mek'], r['kume'], r['volkanik'],
                    '; '.join(f"{v['ist']}:{v['ad']} {v['km']} km" for v in r['volkan']),
                    ' '.join(s['ist'] for s in r['istasyon']), ' '.join(str(s['uzaklik_km']) for s in r['istasyon']),
                    ' '.join(str(int(s['aygit_degisimi_Z'])) for s in r['istasyon']),
                    ' '.join(str(int(s['aygit_degisimi_PK'])) for s in r['istasyon']),
                    len(r['kontrol']), p['T'] if p else '', ' '.join(s['ist'] for s in p['istasyon']) if p else '',
                    len(p['kontrol']) if p else '', r['kume'] in PK_KUME and not r['volkanik'], r['yer']])
with open(os.path.join(BURASI, 'tr5b_kontroller_s2.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['olay', 'epok', 'sira', 'merkez_id', 'la', 'lo', 'uzaklik_olaya_km', 'istasyonlar'])
    for r in olaylar:
        for c in r['kontrol']:
            w.writerow([r['id'], 'olay', c['sira'], c['merkez_id'], c['la'], c['lo'], c['uzaklik_olaya_km'],
                        ' '.join(s['ist'] for s in c['istasyon'])])
        if r['plasebo']:
            for c in r['plasebo']['kontrol']:
                w.writerow([r['id'], 'plasebo', c['sira'], c['merkez_id'], c['la'], c['lo'], c['uzaklik_olaya_km'],
                            ' '.join(s['ist'] for s in c['istasyon'])])
with open(os.path.join(BURASI, 'tr5b_pilot_s2.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); alan = ['sira', 'id', 't', 'M', 'z', 'la', 'lo', 'ist', 'merkez', 'sps_min', 'uzaklik_km', 'esik_km', 'volkan', 'yer']
    w.writerow(alan)
    for q in p2_aday: w.writerow([q[a] for a in alan])
ozet['sha256'] = {os.path.basename(p): hashlib.sha256(open(p, 'rb').read()).hexdigest()
                  for p in [yol] + [os.path.join(BURASI, x) for x in ('tr5b_olaylar_s2.csv', 'tr5b_kontroller_s2.csv', 'tr5b_pilot_s2.csv')]}
json.dump(ozet, open(os.path.join(BURASI, 'tr5b_ozet_s2.json'), 'w'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))
