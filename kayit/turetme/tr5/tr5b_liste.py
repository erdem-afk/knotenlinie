#!/usr/bin/env python3
"""TR-5b: dondurulacak olay / istasyon / kontrol / plasebo listesi ve hacim tahmini (yalnız üstveri ve katalog).

Hiçbir dalga formu okunmaz ya da indirilmez. Tanımlar `kayit/onkayit/TR-5b_sismik-hiz-oncul_ONKAYIT.md` §2-§4.
Kurallar `sayim_ustveri.py` ile aynıdır (M>=6,0, z<=30 km, 2000-2023, R=100 km, taban 3 yıl, n>=1, temiz pencere
[T-5y, T), kontroller SHA-256(olay|aday) sırasıyla); olay ve plasebo istasyonlarına `tr5_doluluk.csv` içindeki
ana doluluk süzgeci (ay doluluğu >= %80, en uzun boşluk <= 3 ay) uygulanır. Kontrol istasyonlarına süzgeç
uygulanmaz (yoklanmadı); koşunun 1. aşaması bunu gün düzeyinde ölçer (ön kayıt §5).

Girdi (depo dışında): <ham> (FDSN üstverisi), <ngl> (ev*.csv), <tr2> (m6_havuz.csv, mekanizma.jsonl),
<m5> (ComCat M>=5,0, z<=70 km, 1990-2025, dört parça: m5_*.csv).
Çıktı (bu dizine): tr5b_liste.json (bağlayıcı liste), tr5b_olaylar.csv, tr5b_kontroller.csv, tr5b_ozet.json.

Kullanım: python3 -I -B tr5b_liste.py <ham> <ngl> <tr2> <m5_dizini>
"""
import collections, csv, datetime as dt, glob, hashlib, importlib.util, json, math, os, re, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
HAM, NGL, TR2, M5 = sys.argv[1:5]
TD = dt.timedelta

_spec = importlib.util.spec_from_file_location('doluluk_yokla', os.path.join(BURASI, 'doluluk_yokla.py'))
DY = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(DY)
ns = DY.betik_yukle('sayim_ustveri.py', [HAM, NGL, TR2], DY.KOSU)
np = ns['np']; hav = ns['hav']; yil = ns['yil']; ANAHTAR = ns['ANAHTAR']

# ------------------------------------------------------------------ önceden sabit sayılar (ön kayıt §2-§4)
TABAN = 3                   # yıl; pencere [T - 1095 g, T - 8 g]
KORUMA = 7                  # T-7 g ... T-1 g okunmaz
N_KONTROL = 5               # bağlayıcı kontrol sayısı (SHA sırasında ilk 5 geçerli)
N_YEDEK = 10                # sırada 10'a kadar yedek (1. aşamada doluluğu tutmayan kontrolün yerine)
PK_SONRA = 30               # pozitif kontrol: [T+1, T+30] (yalnız olay istasyonları)
M5_R, M5_GUN = 50.0, 60     # maske: istasyona <= 50 km, M>=5,0, z<=70 km depremden sonra 60 gün
SAAT = 4                    # gün başına saat (yerel güneş saati 00-04)
B_ORNEK = 1.3               # bayt/örnek (TR-5 sayımı §5.1: KO.ISK HHZ 1,30; IU.ANMO BHZ 1,13)
VOLKANIK = {'hv70116556', 'hv6000471'}   # ön kayıt §2.7: Hawaii adası (Kīlauea / Mauna Loa); ana hükümden çıkar, ayrı satır
VOLKAN_YAPI = {'usp000br01', 'usp000jr55'}  # bilgi satırı: olay istasyonu volkan yapısı üstünde (AV.AKT Akutan, NO.JMIC Jan Mayen)

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

# küme etiketi: kümenin zamanca ilk olayının kimliği
kume_of = {}
for i, g in enumerate(kg):
    kume_of[g['e']['id']] = kok[i]
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
    """[a, b] içinde maskelenen gün sayısı ve maskeyi tetikleyen olaylar."""
    la, lo = ns['konum'][k]
    sec = (M5T >= (a - TD(days=M5_GUN)).toordinal()) & (M5T <= b.toordinal())
    if not sec.any(): return 0, []
    d = hav(la, lo, M5LA[sec], M5LO[sec]); ids = np.nonzero(sec)[0][d <= M5_R]
    gun = set()
    for j in ids:
        if M5ID[j] in haric: continue
        t0 = M5T[j]
        for x in range(t0, t0 + M5_GUN):
            if a.toordinal() <= x <= b.toordinal(): gun.add(x)
    return len(gun), sorted(M5ID[j] for j in ids if M5ID[j] not in haric)

# aygıt değişimi önizlemesi (yalnız Z kanalı üstverisi; bağlayıcı denetim 1. aşamada 3 bileşenle yapılır, ön kayıt §5)
EPOK = collections.defaultdict(lambda: collections.defaultdict(list))   # (ag, ist) -> (loc, cha) -> [(b, sensör, sps, azimut, eğim)]
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
    """Pencere içinde başlayan bir Z epoğunda, aynı konum kodu ve kanalın önceki epoğuna göre sensör tanımı (seri
    numarası atılarak) ya da yönelim değişiyorsa True. Örnekleme hızı ve ölçek değişimi sayılmaz (ön kayıt §2.5)."""
    for L in EPOK.get(k, {}).values():
        L = sorted(set(L))
        for x, y in zip(L, L[1:]):
            if a < y[0] <= b and x[1:] != y[1:]: return True
    return False

def ist_kayit(i, la, lo, a, b, haric=()):
    k = ANAHTAR[i]; mg, mo = maske_gun(k, a, b, haric)
    return dict(ist='.'.join(k), merkez=ns['merkez_of'][k], la=round(float(ns['SLA'][i]), 4), lo=round(float(ns['SLO'][i]), 4),
                uzaklik_km=round(float(hav(la, lo, ns['SLA'][i], ns['SLO'][i])), 1), sps_min=ns['oran_min'][k],
                maske_gun=mg, maske_olay=mo, aygit_degisimi_Z=aygit_degisimi(k, a, b))

def pencere(T):
    return T - yil(TABAN), T - TD(days=KORUMA + 1)

# ------------------------------------------------------------------ kontrol seçimi (kotalı)
# sayim_ustveri.kontrol_sec ile aynı (a)-(e) şartları ve aynı SHA-256(olay kimliği|aday kimliği) sırası; ek olarak
# KOTA: bir kontrol merkezi aynı epok türünde (olay / plasebo) en çok 3 bağımsızlık kümesinde kullanılır
# (TR-1 inceleme 2, bulgu 4). Olaylar (T, kimlik) sırasıyla işlenir; kotası dolmuş merkez atlanır. N_YEDEK'e kadar alınır.
KOTA = 3
kota_say = {'olay': collections.defaultdict(set), 'plasebo': collections.defaultdict(set)}
HARIC_MERKEZ, HARIC_AG = {'KOERI'}, {'6G'}   # kontrollerde kullanılmaz: KOERI tek akış ≈ 40 KB/s (TR-5 §5.2);
                                            # 6G deneme isteği 204 (veri yok). Olay istasyonlarına uygulanmaz.
def kontrol_istasyon(la, lo, a, b):
    """sayim_ustveri.uygun ile aynı (açık, metadata ile kesintisiz, 1 km tek yer, en yakın 3), HARIC'ler atılarak."""
    key = (la, lo, 100.0)
    if key not in ns['_yakin']:
        d = hav(la, lo, ns['SLA'], ns['SLO']); ns['_yakin'][key] = np.nonzero(d <= 100.0)[0]; ns['_uzak'][key] = d
    idx = [i for i in ns['_yakin'][key] if ns['ACIK'][i] and ns['kapsar'](ANAHTAR[i], a, b)
           and ns['merkez_of'][ANAHTAR[i]] not in HARIC_MERKEZ and ANAHTAR[i][0] not in HARIC_AG]
    return sorted(ns['yerler'](idx), key=lambda i: (ns['_uzak'][key][i], ANAHTAR[i]))[:ns['N_MAX']]

def kontrol_kota(e, T, anahtar_id, tur, kume):
    a, b = T - yil(TABAN), T - TD(days=1)
    sira = sorted(ns['MERKEZ'], key=lambda c: hashlib.sha256((anahtar_id + '|' + c['id']).encode()).hexdigest())
    sec = []
    for c in sira:
        if hav(e['la'], e['lo'], c['la'], c['lo']) < ns['KONTROL_UZAK']: continue
        if any(hav(c['la'], c['lo'], s['la'], s['lo']) < ns['KONTROL_ARA'] for s, _ in sec): continue
        u = kota_say[tur][c['id']]
        if kume not in u and len(u) >= KOTA: continue
        st = kontrol_istasyon(c['la'], c['lo'], a, b)
        if len(st) < 1: continue
        if any(hav(ns['SLA'][i], ns['SLO'][i], e['la'], e['lo']) < ns['KONTROL_UZAK'] for i in st): continue
        if not ns['sakin'](c['la'], c['lo'], T - yil(TABAN + 2), T + yil(2)): continue
        sec.append((c, st))
        if len(sec) >= N_YEDEK: break
    for c, _ in sec[:N_KONTROL]: kota_say[tur][c['id']].add(kume)
    return sec

# ------------------------------------------------------------------ liste
olaylar = []
for g in sorted(kg, key=lambda g: (g['e']['t'], g['e']['id'])):
    e = g['e']; T = e['t']; a, b = pencere(T)
    st = [ns['ANAHTAR'].index(k) for k in g['st']]
    kon = []
    g['kontrol_kota'] = kontrol_kota(e, T, e['id'], 'olay', kume_ad[kume_of[e['id']]])
    for sira, (c, cst) in enumerate(g['kontrol_kota']):
        kon.append(dict(sira=sira + 1, merkez_id=c['id'], la=c['la'], lo=c['lo'], M=c['M'],
                        uzaklik_olaya_km=round(float(hav(e['la'], e['lo'], c['la'], c['lo'])), 0),
                        istasyon=[ist_kayit(i, c['la'], c['lo'], a, b) for i in cst]))
    rec = dict(id=e['id'], t=str(T), M=e['M'], z=e['z'], la=e['la'], lo=e['lo'], yer=e['yer'], bolge=ns['bolge'](e),
               mek=ns['mek'].get(e['id'], '?'), kume=kume_ad[kume_of[e['id']]], volkanik=e['id'] in VOLKANIK,
               volkan_yapi=e['id'] in VOLKAN_YAPI,
               pencere=[str(a), str(b)], pk_pencere=[str(T + TD(days=1)), str(T + TD(days=PK_SONRA))],
               istasyon=[ist_kayit(i, e['la'], e['lo'], a, b, haric={e['id']}) for i in st], kontrol=kon,
               plasebo=None)
    olaylar.append(rec)

# plasebo: aynı yer, epok T' = T - 1095 g; istasyonlar [T-2190 g, T-1 g] kesintisiz ve dolu (sayim_ustveri kuralı)
pl_id = {g['e']['id'] for g in pl}
kg_s = sorted(kg, key=lambda g: (g['e']['t'], g['e']['id']))
for rec, g in zip(olaylar, kg_s):
    assert rec['id'] == g['e']['id']
    if rec['id'] not in pl_id: continue
    e = g['e']; T = e['t']; Tp = T - yil(TABAN); a, b = pencere(Tp)
    st, _ = ns['uygun'](e['la'], e['lo'], 100.0, T - yil(2 * TABAN), T - TD(days=1))
    ks = kontrol_kota(e, Tp, e['id'] + '|plasebo', 'plasebo', rec['kume'])
    rec['plasebo'] = dict(T=str(Tp), pencere=[str(a), str(b)],
                          istasyon=[ist_kayit(i, e['la'], e['lo'], a, b) for i in st],
                          kontrol=[dict(sira=s + 1, merkez_id=c['id'], la=c['la'], lo=c['lo'], M=c['M'],
                                        uzaklik_olaya_km=round(float(hav(e['la'], e['lo'], c['la'], c['lo'])), 0),
                                        istasyon=[ist_kayit(i, c['la'], c['lo'], a, b) for i in cst])
                                   for s, (c, cst) in enumerate(ks)])

# ------------------------------------------------------------------ özet sayılar
def kume_say(L):
    return len({r['kume'] for r in L})
ana = [r for r in olaylar if not r['volkanik']]
pl_ok = [r for r in olaylar if r['plasebo'] and len(r['plasebo']['kontrol']) >= N_KONTROL]
ozet = dict(olay=len(olaylar), K=kume_say(olaylar), K_ana_volkaniksiz=kume_say(ana), volkanik=[r['id'] for r in olaylar if r['volkanik']],
            plasebo_olay=len([r for r in olaylar if r['plasebo']]), K_plasebo=kume_say([r for r in olaylar if r['plasebo']]),
            plasebo_kontrollu_olay=len(pl_ok), K_plasebo_kontrollu=kume_say(pl_ok),
            K_plasebo_kontrollu_volkaniksiz=kume_say([r for r in pl_ok if not r['volkanik']]))
ozet['olay_istasyon_sayisi'] = dict(collections.Counter(len(r['istasyon']) for r in olaylar))
uz = sorted(s['uzaklik_km'] for r in olaylar for s in r['istasyon'])
ozet['olay_istasyon_uzaklik_km'] = dict(n=len(uz), medyan=uz[len(uz) // 2], q25=uz[len(uz) // 4], q75=uz[3 * len(uz) // 4])
ozet['bolge_kume'] = dict(collections.Counter(next(r['bolge'] for r in olaylar if r['kume'] == k) for k in {r['kume'] for r in olaylar}))
ozet['mekanizma_olay'] = dict(collections.Counter(r['mek'] for r in olaylar))
ozet['M_dagilimi'] = dict(collections.Counter('6.0-6.4' if r['M'] < 6.5 else ('6.5-6.9' if r['M'] < 7 else '>=7') for r in olaylar))
# pozitif kontrol alt kümesi: en yakın olay istasyonu <= 30 km, ya da <= 2 kırık boyu (Wells-Coppersmith 1994, tüm türler)
def L_km(M): return 10 ** (-2.44 + 0.59 * M)
yakin_pk = [r for r in olaylar if not r['volkanik'] and min(s['uzaklik_km'] for s in r['istasyon']) <= max(30.0, 2 * L_km(r['M']))]
ozet['pk_yakin_olay'] = len(yakin_pk); ozet['pk_yakin_kume'] = kume_say(yakin_pk)
# kontrol merkezlerinin tekrarı (ilk 5)
say5 = collections.Counter(); kume5 = collections.defaultdict(set)
for r in olaylar:
    for c in r['kontrol'][:N_KONTROL]:
        say5[c['merkez_id']] += 1; kume5[c['merkez_id']].add(r['kume'])
ozet['kontrol_ilk5'] = dict(yuva=sum(say5.values()), tekil_merkez=len(say5), en_cok_kume=max(len(v) for v in kume5.values()),
                           uc_kumeden_fazla_merkez=sum(1 for v in kume5.values() if len(v) > 3))
ozet['kontrol_sayisi'] = dict(collections.Counter(len(r['kontrol']) for r in olaylar))
ozet['plasebo_kontrol_sayisi'] = dict(collections.Counter(len(r['plasebo']['kontrol']) for r in olaylar if r['plasebo']))
ozet['kontrol_5ten_az_olay'] = [r['id'] for r in olaylar if len(r['kontrol']) < N_KONTROL]
ozet['K_ana_kontrollu'] = kume_say([r for r in ana if len(r['kontrol']) >= N_KONTROL])
pk_say = collections.Counter(); pk_kume = collections.defaultdict(set)
for r in olaylar:
    if r['plasebo']:
        for c in r['plasebo']['kontrol'][:N_KONTROL]: pk_kume[c['merkez_id']].add(r['kume'])
ozet['plasebo_kontrol_ilk5'] = dict(tekil_merkez=len(pk_kume), en_cok_kume=max((len(v) for v in pk_kume.values()), default=0))
ozet['volkan_yapi_bilgi'] = sorted(VOLKAN_YAPI)
ozet['aygit_degisimi_Z'] = dict(
    olay_ist=sum(1 for r in olaylar for s_ in r['istasyon'] if s_['aygit_degisimi_Z']),
    olay_tum_istasyonu_degisen_olay=[r['id'] for r in olaylar if all(s_['aygit_degisimi_Z'] for s_ in r['istasyon'])],
    plasebo_ist=sum(1 for r in olaylar if r['plasebo'] for s_ in r['plasebo']['istasyon'] if s_['aygit_degisimi_Z']),
    kontrol5_ist=sum(1 for r in olaylar for c in r['kontrol'][:5] for s_ in c['istasyon'] if s_['aygit_degisimi_Z']))
ozet['maske'] = dict(olay_ist_maskeli=sum(1 for r in olaylar for s in r['istasyon'] if s['maske_gun'] > 0),
                     olay_ist=sum(len(r['istasyon']) for r in olaylar),
                     olay_ist_maske_gun_ort=round(sum(s['maske_gun'] for r in olaylar for s in r['istasyon']) / max(1, sum(len(r['istasyon']) for r in olaylar)), 1),
                     kontrol5_ist_maskeli=sum(1 for r in olaylar for c in r['kontrol'][:5] for s in c['istasyon'] if s['maske_gun'] > 0),
                     kontrol5_ist=sum(len(c['istasyon']) for r in olaylar for c in r['kontrol'][:5]))

# ------------------------------------------------------------------ hacim (istasyon başına gün birleşimi)
def birlesim(iv):
    m = []
    for b_, e_ in sorted(iv):
        if m and b_ <= m[-1][1] + TD(days=1): m[-1][1] = max(m[-1][1], e_)
        else: m.append([b_, e_])
    return sum((e_ - b_).days + 1 for b_, e_ in m)
def hacim(bicim):
    pen = collections.defaultdict(list); sps = {}; mk = {}
    def ekle(s, a, b):
        pen[s['ist']].append((dt.date.fromisoformat(a) if isinstance(a, str) else a, dt.date.fromisoformat(b) if isinstance(b, str) else b))
        sps[s['ist']] = s['sps_min']; mk[s['ist']] = s['merkez']
    nk = bicim['n_kontrol']
    for r in olaylar:
        for s in r['istasyon']:
            ekle(s, *r['pencere']); ekle(s, *r['pk_pencere'])
        for c in r['kontrol'][:nk]:
            for s in c['istasyon']: ekle(s, *r['pencere'])
        if r['plasebo'] and bicim['plasebo']:
            for s in r['plasebo']['istasyon']: ekle(s, *r['plasebo']['pencere'])
            for c in r['plasebo']['kontrol'][:bicim['n_plasebo_kontrol']]:
                for s in c['istasyon']: ekle(s, *r['plasebo']['pencere'])
    gun = {k: birlesim(v) for k, v in pen.items()}
    out = dict(istasyon=len(gun), istasyon_gunu=sum(gun.values()))
    for ad, saat in (('4saat_3bilesen', SAAT), ('tamgun_3bilesen', 24)):
        tb = collections.Counter()
        for k, n in gun.items(): tb[mk[k]] += n * saat * 3600 * sps[k] * B_ORNEK * 3 / 1e12
        out[ad + '_TB'] = round(sum(tb.values()), 3); out[ad + '_merkez_TB'] = {m: round(v, 3) for m, v in tb.most_common()}
    return out
BICIM = {'A (bağlayıcı): olay + plasebo, kontrol 5, plasebo kontrol 5': dict(n_kontrol=5, plasebo=True, n_plasebo_kontrol=5),
         'A0: olay + plasebo, kontrol 5, plasebo kontrolsüz': dict(n_kontrol=5, plasebo=True, n_plasebo_kontrol=0),
         'A3: olay + plasebo, kontrol 3, plasebo kontrol 3': dict(n_kontrol=3, plasebo=True, n_plasebo_kontrol=3),
         'B (tam): kontrol 10, plasebo kontrol 10': dict(n_kontrol=10, plasebo=True, n_plasebo_kontrol=10)}
ozet['hacim'] = {ad: hacim(b) for ad, b in BICIM.items()}
# yedek payı: 1. aşamada kontrol istasyonlarının %40'ı doluluğu tutmazsa (TR-5 Ek 1'de olay istasyonlarında ≈ %60 tutmadı)
# yerine sıradaki kontrol gelir; kaba üst sınır olarak A'nın kontrol payı 1/0,4 = 2,5 kat yoklanır. Hesap ön kayıtta.

# ------------------------------------------------------------------ yaz
liste = dict(surum='TR-5b liste 1', tarih='2026-11-12',
             kural=dict(M_min=6.0, z_max=30.0, T=['2000-01-01', '2023-12-31'], R_km=100.0, n_min=1, taban_yil=TABAN,
                        koruma_gun=KORUMA, n_kontrol=N_KONTROL, n_yedek=N_YEDEK, pk_sonra_gun=PK_SONRA,
                        maske=dict(M_min=5.0, z_max=70.0, R_km=M5_R, gun=M5_GUN), saat_gun=SAAT, volkanik=sorted(VOLKANIK),
                        volkan_yapi=sorted(VOLKAN_YAPI), kontrol_kota_kume=KOTA,
                        kontrol_haric_merkez=sorted(HARIC_MERKEZ), kontrol_haric_ag=sorted(HARIC_AG),
                        doluluk_suzgeci='tr5_doluluk.csv dolu_ana (olay ve plasebo istasyonları)'),
             girdi_sha256={os.path.basename(f): hashlib.sha256(open(f, 'rb').read()).hexdigest()
                           for f in [os.path.join(BURASI, 'tr5_doluluk.csv'), os.path.join(NGL, 'ev.csv'),
                                     os.path.join(TR2, 'm6_havuz.csv'), os.path.join(HAM, 'fedcatalog_kanal.txt')] +
                           sorted(glob.glob(os.path.join(M5, 'm5_*.csv')))},
             olaylar=olaylar)
yol = os.path.join(BURASI, 'tr5b_liste.json')
with open(yol, 'w', encoding='utf-8') as f:
    json.dump(liste, f, ensure_ascii=False, indent=1, sort_keys=True, default=str); f.write('\n')
with open(os.path.join(BURASI, 'tr5b_olaylar.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['id', 't', 'M', 'z', 'la', 'lo', 'bolge', 'mek', 'kume', 'volkanik', 'istasyonlar', 'uzaklik_km',
                'kontrol_sayisi', 'plasebo_T', 'plasebo_istasyonlar', 'plasebo_kontrol_sayisi', 'yer'])
    for r in olaylar:
        p = r['plasebo']
        w.writerow([r['id'], r['t'], r['M'], r['z'], r['la'], r['lo'], r['bolge'], r['mek'], r['kume'], r['volkanik'],
                    ' '.join(s['ist'] for s in r['istasyon']), ' '.join(str(s['uzaklik_km']) for s in r['istasyon']),
                    len(r['kontrol']), p['T'] if p else '', ' '.join(s['ist'] for s in p['istasyon']) if p else '',
                    len(p['kontrol']) if p else '', r['yer']])
with open(os.path.join(BURASI, 'tr5b_kontroller.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(['olay', 'epok', 'sira', 'merkez_id', 'la', 'lo', 'uzaklik_olaya_km', 'istasyonlar'])
    for r in olaylar:
        for c in r['kontrol']:
            w.writerow([r['id'], 'olay', c['sira'], c['merkez_id'], c['la'], c['lo'], c['uzaklik_olaya_km'],
                        ' '.join(s['ist'] for s in c['istasyon'])])
        if r['plasebo']:
            for c in r['plasebo']['kontrol']:
                w.writerow([r['id'], 'plasebo', c['sira'], c['merkez_id'], c['la'], c['lo'], c['uzaklik_olaya_km'],
                            ' '.join(s['ist'] for s in c['istasyon'])])
ozet['sha256'] = {os.path.basename(p): hashlib.sha256(open(p, 'rb').read()).hexdigest()
                  for p in [yol, os.path.join(BURASI, 'tr5b_olaylar.csv'), os.path.join(BURASI, 'tr5b_kontroller.csv')]}
json.dump(ozet, open(os.path.join(BURASI, 'tr5b_ozet.json'), 'w'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(ozet, ensure_ascii=False, indent=1, default=str))
