#!/usr/bin/env python3
"""TR-5: büyük depremlerden önceki dv/v sınavı için yalnız ÜSTVERİYLE olay ve kontrol sayımı.

Hiçbir dalga formu okunmaz. Tanımlar `kayit/onkayit/TR-5_TR-4_SAYIM.md` bölüm 2'dedir; bu betik onları kodlar.

Girdi (ham dosyalar depo dışında):
  <ham>/fedcatalog_kanal.txt, <ham>/ek_*_kanal.txt     BHZ/HHZ kanal epokları (ustveri_indir.py)
  <ham>/acik_*.txt, <ham>/durum.json                   includerestricted=false istasyon listeleri
  <ngl>/ev.csv          ComCat M>=6,5, derinlik<=30 km, 2000-2025 (TR-1 indirmesi)
  <ngl>/ev70.csv, ev70_pre.csv   ComCat M>=6,5, derinlik<=70 km, 2000-2025 ve 1985-1999
  <tr2>/m6_havuz.csv    ComCat M>=6,0, derinlik<=40 km, 1976-2025 (TR-2 indirmesi)
  <tr2>/mekanizma.jsonl ComCat mekanizmaları (M6,0-7,2, derinlik<=25 km)
2026 ve sonrası tarihli satırlar atılır. Katalog sorgusu yapılmaz.

Kullanım: python3 -I -B sayim_ustveri.py <ham> <ngl> <tr2> [--json çıktı.json]
"""
import csv, collections, datetime as dt, glob, hashlib, json, math, os, sys
import numpy as np

HAM, NGL, TR2 = sys.argv[1], sys.argv[2], sys.argv[3]
JSON = sys.argv[sys.argv.index('--json') + 1] if '--json' in sys.argv else None
Y = 365.25
TD = dt.timedelta
def yil(n): return TD(days=int(math.floor(n * Y)))
SON = dt.date(2025, 12, 31)
KOR = dt.date(2026, 1, 1)

# ------------------------------------------------------------------ önceden sabit tanımlar (bölüm 2)
TABAN_YIL = 5            # istasyon [T-5y, T-1g] boyunca metadata epoğu kesintisiz (<= 30 g boşluk)
BOSLUK = 30
ONCE_TEMIZ = 7           # sakinlik [T-7y, T) (taban + 2 yıl iyileşme payı)
S1 = (6.0, 40.0, 150.0)  # M, derinlik, yarıçap
S2 = (7.0, 70.0, 500.0)
S3 = (8.0, 70.0, 1000.0)
KONTROL_SONRA = 2        # kontrol yerinde [T-7y, T+2y] sakin
KONTROL_UZAK, KONTROL_ARA, KONTROL_N, KONTROL_MIN = 600.0, 150.0, 10, 5
KUME_R, KUME_T = 300.0, 1.0
AYNI_YER_KM = 1.0
T_SON_ANA = dt.date(2023, 12, 31)

def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

def tarih(s):
    s = s.strip()
    if not s: return SON
    d = dt.date.fromisoformat(s[:10])
    return min(d, SON)

# ------------------------------------------------------------------ istasyonlar
durum = json.load(open(os.path.join(HAM, 'durum.json')))
kanal = collections.defaultdict(list)   # (net, sta) -> [(b, e)]
konum, merkez_of, oran, oran_min = {}, {}, {}, {}
def kanal_oku(dosya, merkez0):
    mk = merkez0
    for l in open(dosya, encoding='utf-8', errors='replace'):
        if l.startswith('#DATACENTER='):
            mk = l.split('=', 1)[1].split(',')[0].strip(); continue
        if l.startswith('#') or '|' not in l: continue
        p = l.rstrip('\n').split('|')
        if len(p) < 17 or p[3] not in ('BHZ', 'HHZ'): continue
        try:
            sr = float(p[14]); b = tarih(p[15]); e = tarih(p[16]) if p[16].strip() else SON
            la, lo = float(p[4]), float(p[5])
        except ValueError:
            continue
        if sr < 10 or b > SON: continue
        k = (p[0], p[1])
        if k in merkez_of and merkez_of[k] != mk and merkez0 is not None:
            continue              # fedcatalog'daki kayıt öncelikli (ek merkez kopyası atlanır)
        merkez_of.setdefault(k, mk)
        kanal[k].append((b, e)); konum[k] = (la, lo); oran[k] = max(oran.get(k, 0), sr)
        oran_min[k] = min(oran_min.get(k, 1e9), sr)
kanal_oku(os.path.join(HAM, 'fedcatalog_kanal.txt'), None)
fed_anahtar = set(kanal)
for f in sorted(glob.glob(os.path.join(HAM, 'ek_*_kanal.txt'))):
    mk = os.path.basename(f)[3:-10]
    once = set(kanal)
    kanal_oku(f, mk)

# açık / kısıtlı
acik, acik_bilinmiyor = set(), set()
ad_esle = {'IRISDMC': 'IRISDMC', 'GEONET': 'GEONET'}
for mk in set(merkez_of.values()):
    d = durum.get('acik_' + mk.upper().replace('EARTHSCOPE', 'IRISDMC'))
    f = os.path.join(HAM, f'acik_{mk.upper()}.txt')
    if d and d['kod'] == 200 and os.path.exists(f):
        for l in open(f, encoding='utf-8', errors='replace'):
            if l.startswith('#') or '|' not in l: continue
            p = l.split('|'); acik.add((p[0], p[1]))
    else:
        acik_bilinmiyor.add(mk)
def acik_mi(k):
    return k in acik or merkez_of[k] in acik_bilinmiyor

def birlestir(iv):
    iv = sorted(iv); out = []
    for b, e in iv:
        if out and (b - out[-1][1]).days <= BOSLUK: out[-1][1] = max(out[-1][1], e)
        else: out.append([b, e])
    return out
araliklar = {k: birlestir(v) for k, v in kanal.items()}
ANAHTAR = sorted(kanal)
SLA = np.array([konum[k][0] for k in ANAHTAR]); SLO = np.array([konum[k][1] for k in ANAHTAR])
ACIK = np.array([acik_mi(k) for k in ANAHTAR])
def kapsar(k, a, b):
    return any(x <= a and y >= b for x, y in araliklar[k])

def yerler(idx):
    """1 km içindeki istasyonları tek yer say (açgözlü, ada göre)."""
    sec = []
    for i in sorted(idx, key=lambda i: ANAHTAR[i]):
        if all(hav(SLA[i], SLO[i], SLA[j], SLO[j]) > AYNI_YER_KM for j in sec): sec.append(i)
    return sec

_yakin, _uzak = {}, {}
N_MAX = 3          # olay ve kontrolde en yakın en çok 3 yer (eşit sayı; hacim sınırı)
def uygun(la, lo, R, a, b, acik_sart=True):
    key = (la, lo, R)
    if key not in _yakin:
        d = hav(la, lo, SLA, SLO); _yakin[key] = np.nonzero(d <= R)[0]; _uzak[key] = d
    idx = [i for i in _yakin[key] if (ACIK[i] or not acik_sart) and kapsar(ANAHTAR[i], a, b)]
    y = sorted(yerler(idx), key=lambda i: (_uzak[key][i], ANAHTAR[i]))
    return y[:N_MAX], None

# ------------------------------------------------------------------ kataloglar
def oku(f):
    out = []
    for r in csv.DictReader(open(f)):
        if r['type'] != 'earthquake': continue
        t = dt.datetime.fromisoformat(r['time'].replace('Z', '')).date()
        if t >= KOR: continue
        out.append(dict(id=r['id'], t=t, la=float(r['latitude']), lo=float(r['longitude']),
                        z=float(r['depth'] or 0), M=float(r['mag']), yer=r['place']))
    return out
H6 = oku(os.path.join(TR2, 'm6_havuz.csv'))                       # M>=6, z<=40, 1976-2025
H70 = oku(os.path.join(NGL, 'ev70.csv')) + oku(os.path.join(NGL, 'ev70_pre.csv'))  # M>=6,5 z<=70 1985-2025
def kat_dizi(L):
    return (np.array([e['la'] for e in L]), np.array([e['lo'] for e in L]), np.array([e['M'] for e in L]),
            np.array([e['z'] for e in L]), np.array([e['t'].toordinal() for e in L]), [e['id'] for e in L])
K6, K70 = kat_dizi(H6), kat_dizi(H70)

def sakin(la, lo, a, b, haric=(), kurallar=('S1', 'S2', 'S3'), s1=S1):
    """[a, b) aralığında kural depremi yoksa True."""
    for ad, (M, z, R), kat in (('S1', s1, K6), ('S2', S2, K70), ('S3', S3, K70)):
        if ad not in kurallar: continue
        la_, lo_, m_, z_, t_, id_ = kat
        sec = (m_ >= M) & (z_ <= z) & (t_ >= a.toordinal()) & (t_ < b.toordinal())
        if not sec.any(): continue
        d = hav(la, lo, la_[sec], lo_[sec])
        ids = np.array(id_)[sec][d <= R]
        if any(i not in haric for i in ids): return False
    return True

mek = {}
for l in open(os.path.join(TR2, 'mekanizma.jsonl')):
    r = json.loads(l)
    pl = (r.get('mt') or []) + (r.get('fm') or [])
    if not pl: continue
    try:
        rk = float(pl[0]['nodal-plane-1-rake']); rk = (rk + 180) % 360 - 180
        mek[r['id']] = 'SS' if (abs(rk) <= 30 or abs(rk) >= 150) else 'diğer'
    except Exception:
        pass

def bolge(e):
    la, lo = e['la'], e['lo']
    if 30 <= la <= 46 and 128 <= lo <= 146: return 'Japonya'
    if 30 <= la <= 42 and -126 <= lo <= -114: return 'Kaliforniya-Nevada'
    if 50 <= la <= 72 and (lo <= -130 or lo >= 170): return 'Alaska-Aleut'
    if -48 <= la <= -34 and 165 <= lo <= 180: return 'Yeni Zelanda'
    if 20 <= la <= 26 and 119 <= lo <= 123: return 'Tayvan'
    if -56 <= la <= 13 and -82 <= lo <= -66: return 'And'
    if 7 <= la <= 33 and -118 <= lo <= -77: return 'Meksika-Orta Amerika-Karayip'
    if 34 <= la <= 48 and 5 <= lo <= 30: return 'İtalya-Balkan-Ege'
    if 34 <= la <= 43 and 26 <= lo <= 45: return 'Anadolu'
    if 25 <= la <= 40 and 45 <= lo <= 75: return 'İran-Orta Asya'
    if 20 <= la <= 45 and 75 <= lo <= 120: return 'Çin-Himalaya'
    if -12 <= la <= 20 and 92 <= lo <= 140: return 'Endonezya-Filipinler'
    if -25 <= la <= 0 and 140 <= lo <= 180: return 'PNG-Solomon-Vanuatu-Fiji'
    return 'öteki'

# ------------------------------------------------------------------ olay sayımı
def olay_say(olaylar, R, n_min, kurallar=('S1', 'S2', 'S3'), s1=S1, son=T_SON_ANA, foreshock_gun=0, kontrol=True):
    sat = dict(toplam=0, istasyonlu=0, temiz=0, kontrollu=0)
    gecen = []
    for e in olaylar:
        if e['t'] > son: continue
        sat['toplam'] += 1
        a, b = e['t'] - yil(TABAN_YIL), e['t'] - TD(days=1)
        st, _ = uygun(e['la'], e['lo'], R, a, b)
        if len(st) < n_min: continue
        sat['istasyonlu'] += 1
        if not sakin(e['la'], e['lo'], e['t'] - yil(ONCE_TEMIZ), e['t'] - TD(days=foreshock_gun), haric={e['id']},
                     kurallar=kurallar, s1=s1):
            continue
        sat['temiz'] += 1
        g = dict(e=e, st=[ANAHTAR[i] for i in st])
        if kontrol:
            g['kontrol'] = kontrol_sec(e, R, n_min)
            if len(g['kontrol']) < KONTROL_MIN: g['kgecer'] = False
            else: g['kgecer'] = True; sat['kontrollu'] += 1
        gecen.append(g)
    return sat, gecen

# kontrol merkezleri: M>=6,5, z<=40 ComCat dış merkezleri (deprem üreten yerler), 25 km içinde tekilleştirilmiş
MERKEZ = []
for e in sorted([e for e in H6 if e['M'] >= 6.5], key=lambda e: e['id']):
    if all(hav(e['la'], e['lo'], c['la'], c['lo']) > 25 for c in MERKEZ): MERKEZ.append(e)
_kontrol_onbellek = {}
def kontrol_sec(e, R, n_min):
    key = (e['id'], R, n_min, TABAN_YIL)
    if key in _kontrol_onbellek: return _kontrol_onbellek[key]
    T = e['t']; a, b = T - yil(TABAN_YIL), T - TD(days=1)
    sira = sorted(MERKEZ, key=lambda c: hashlib.sha256((e['id'] + '|' + c['id']).encode()).hexdigest())
    sec = []
    for c in sira:
        if hav(e['la'], e['lo'], c['la'], c['lo']) < KONTROL_UZAK: continue
        if any(hav(c['la'], c['lo'], s['la'], s['lo']) < KONTROL_ARA for s, _ in sec): continue
        st, _ = uygun(c['la'], c['lo'], R, a, b)
        if len(st) < n_min: continue
        if any(hav(SLA[i], SLO[i], e['la'], e['lo']) < KONTROL_UZAK for i in st): continue
        if not sakin(c['la'], c['lo'], T - yil(ONCE_TEMIZ), T + yil(KONTROL_SONRA)): continue
        sec.append((c, st))
        if len(sec) >= KONTROL_N: break
    _kontrol_onbellek[key] = sec
    return sec

def kumele(gecen):
    n = len(gecen); par = list(range(n))
    def bul(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            ei, ej = gecen[i]['e'], gecen[j]['e']
            dtj = abs((ei['t'] - ej['t']).days) / Y
            bag = (hav(ei['la'], ei['lo'], ej['la'], ej['lo']) < KUME_R and dtj < KUME_T) or \
                  (set(gecen[i]['st']) & set(gecen[j]['st']) and dtj < TABAN_YIL)
            if bag: par[bul(i)] = bul(j)
    return len({bul(i) for i in range(n)}), [bul(i) for i in range(n)]

def plasebo_say(gecen, R, n_min):
    """Yerinde plasebo: aynı istasyonlar [T-10y, T-1g] kesintisiz ve [T-12y, T) sakin."""
    ok = []
    for g in gecen:
        e = g['e']
        st, _ = uygun(e['la'], e['lo'], R, e['t'] - yil(2 * TABAN_YIL), e['t'] - TD(days=1))
        if len(st) >= n_min and sakin(e['la'], e['lo'], e['t'] - yil(TABAN_YIL + ONCE_TEMIZ), e['t'], haric={e['id']}):
            ok.append(g)
    return ok

# ------------------------------------------------------------------ koşu
EV30 = oku(os.path.join(NGL, 'ev.csv'))
EV40 = [e for e in H6 if e['M'] >= 6.5 and e['t'] >= dt.date(2000, 1, 1)]
sonuc = dict(girdi=dict(istasyon=len(ANAHTAR), acik=int(ACIK.sum()), acik_bilinmiyor=sorted(acik_bilinmiyor),
                        ev30=len(EV30), ev40=len(EV40), kontrol_merkezi=len(MERKEZ)), satirlar=[], ayrinti={})
print(f"istasyon (BHZ/HHZ, >=10 sps, epok 1995-2020 kesişimli) {len(ANAHTAR)}; açık {int(ACIK.sum())}; "
      f"açıklığı denetlenemeyen merkez {sorted(acik_bilinmiyor)}; olay z<=30: {len(EV30)}, z<=40: {len(EV40)}; "
      f"kontrol merkezi {len(MERKEZ)}")

B_ORNEK = 1.3   # bayt/örnek (miniSEED Steim; 12 Kasım 2026 denemeleri: KO.ISK HHZ 1,30, IU.ANMO BHZ 1,13)
def hacim_hesap(gecen, taban):
    """Olay + kontrol pencerelerinin istasyon başına birleşimi; 3 bileşen, en düşük >=10 sps kanal."""
    pen = collections.defaultdict(list)
    for g in gecen:
        if not g.get('kgecer'): continue
        T = g['e']['t']; a = T - yil(taban)
        for k in g['st']: pen[k].append((a, T))
        for _, st in g['kontrol']:
            for i in st: pen[ANAHTAR[i]].append((a, T))
    gun = 0; bayt = 0.0; gun_olay = 0
    for k, iv in pen.items():
        iv = sorted(iv); m = []
        for b, e in iv:
            if m and b <= m[-1][1]: m[-1][1] = max(m[-1][1], e)
            else: m.append([b, e])
        n = sum((e - b).days for b, e in m); gun += n
        bayt += n * 86400 * oran_min[k] * B_ORNEK * 3
    for g in gecen:
        if g.get('kgecer'): gun_olay += len(g['st']) * yil(taban).days
    return dict(istasyon_gunu=gun, olay_istasyon_gunu=gun_olay, hacim_GB=round(bayt / 1e9, 1), n_istasyon=len(pen))

def satir(ad, olaylar, R, n_min, taban=5, **kw):
    global TABAN_YIL, ONCE_TEMIZ
    TABAN_YIL, ONCE_TEMIZ = taban, taban + 2
    sat, gecen = olay_say(olaylar, R, n_min, **kw)
    K, _ = kumele(gecen)
    kg = [g for g in gecen if g.get('kgecer')]
    Kk, _ = kumele(kg)
    pl = plasebo_say(kg, R, n_min)
    Kp, _ = kumele(pl) if pl else (0, [])
    r = dict(ad=ad, R=R, n_min=n_min, **sat, K_temiz=K, K_kontrollu=Kk, plasebo_olay=len(pl), K_plasebo=Kp,
             SS_kontrollu=sum(1 for g in kg if mek.get(g['e']['id']) == 'SS'))
    r['taban'] = taban
    r.update(hacim_hesap(gecen, taban))
    r['olaylar'] = [dict(id=g['e']['id'], t=str(g['e']['t']), M=g['e']['M'], yer=g['e']['yer'], bolge=bolge(g['e']),
                         istasyon=[[k[0], k[1], merkez_of[k]] for k in g['st']],
                         kontrol_istasyon=[[ANAHTAR[i][0], ANAHTAR[i][1], merkez_of[ANAHTAR[i]]] for _, st in g['kontrol'] for i in st])
                    for g in gecen if g.get('kgecer')]
    TABAN_YIL, ONCE_TEMIZ = 5, 7
    sonuc['satirlar'].append(r)
    print(f"{ad:44s} t{taban} R={R:>3.0f} n>={n_min} | toplam {sat['toplam']:3d} istasyonlu {sat['istasyonlu']:3d} "
          f"temiz {sat['temiz']:3d} (K {K:3d}) kontrollu {sat['kontrollu']:3d} (K {Kk:3d}) "
          f"plasebo {len(pl):3d} (K {Kp:3d}) SS {r['SS_kontrollu']} | ist-gün {r['istasyon_gunu']} "
          f"(olay {r['olay_istasyon_gunu']}) {r['hacim_GB']} GB", flush=True)
    return gecen

ANA = None
for R in (50.0, 100.0):
    for n in (1, 2, 3):
        g = satir('ana (z<=30, T<=2023)', EV30, R, n)
        if R == 100.0 and n == 2: ANA = g
for R in (50.0, 100.0):
    satir('z<=40, T<=2023', EV40, R, 2)
satir('T<=2025 (kontrol T+2y kısalır; bilgi)', EV30, 100.0, 2, son=SON)
satir('tanı: S1-S3 kapalı', EV30, 100.0, 2, kurallar=())
satir('tanı: yalnız S1', EV30, 100.0, 2, kurallar=('S1',))
satir('tanı: S1 yarıçapı 100 km', EV30, 100.0, 2, s1=(6.0, 40.0, 100.0))
satir('tanı: S1 M>=6,5', EV30, 100.0, 2, s1=(6.5, 40.0, 150.0))
satir('tanı: son 30 gün öncüleri serbest', EV30, 100.0, 2, foreshock_gun=30)
# bilgi değişkeleri (ön kayıt kuralı değil): kısa taban ve M>=6,0 hedefler
EV60 = [e for e in H6 if e['t'] >= dt.date(2000, 1, 1) and e['z'] <= 30.0]
sonuc['girdi']['ev60_z30'] = len(EV60)
for n in (1, 2):
    satir('bilgi: taban 3 yıl', EV30, 100.0, n, taban=3)
    satir('bilgi: M>=6,0 (z<=30)', EV60, 100.0, n)
    satir('bilgi: M>=6,0, taban 3 yıl', EV60, 100.0, n, taban=3)
satir('bilgi: M>=6,0, R=50', EV60, 50.0, 1)

# eleme nedenleri (ana, R=100): istasyon yok / var ama kısa / kısıtlı
neden = collections.Counter(); bolge_yok = collections.Counter()
for e in EV30:
    if e['t'] > T_SON_ANA: continue
    a, b = e['t'] - yil(5), e['t'] - TD(days=1)
    st_any, _ = uygun(e['la'], e['lo'], 100.0, dt.date(1900, 1, 1), dt.date(1900, 1, 1), acik_sart=False)
    hepsi = [i for i in _yakin[(e['la'], e['lo'], 100.0)]]
    calisan = [i for i in hepsi if any(x <= b and y >= e['t'] - TD(days=30) for x, y in araliklar[ANAHTAR[i]])]
    tam = [i for i in hepsi if kapsar(ANAHTAR[i], a, b)]
    tam_acik = [i for i in tam if ACIK[i]]
    if not hepsi: nd = 'a: 100 km içinde hiç BHZ/HHZ epoğu yok'
    elif not calisan: nd = 'b: olay anında çalışan istasyon yok'
    elif not tam: nd = 'c: çalışan var, 5 yıl kesintisiz yok'
    elif not tam_acik: nd = 'd: 5 yıl var ama kısıtlı'
    else: nd = 'e: >=1 açık 5 yıllık istasyon'
    neden[nd] += 1
    if nd[0] in 'ab': bolge_yok[bolge(e)] += 1
sonuc['eleme_nedeni'] = dict(sorted(neden.items())); sonuc['istasyonsuz_bolge'] = dict(bolge_yok.most_common())
print('eleme nedeni (z<=30, T<=2023, R=100):', dict(sorted(neden.items())))
print('istasyonsuz (a+b) olayların bölgesi:', dict(bolge_yok.most_common()))

# ana satırın ayrıntısı
kg = [g for g in ANA if g.get('kgecer')]
K, kok = kumele(kg)
blg = collections.Counter(bolge(g['e']) for g in kg)
blgK = collections.Counter()
for r_ in set(kok):
    blgK[bolge(kg[kok.index(r_)]['e'])] += 1
ist = collections.Counter(len(g['st']) for g in kg)
ncont = collections.Counter(len(g['kontrol']) for g in ANA)
sonuc['ayrinti']['ana_R100_n2'] = dict(
    olay=[dict(id=g['e']['id'], t=str(g['e']['t']), M=g['e']['M'], z=g['e']['z'], la=g['e']['la'], lo=g['e']['lo'],
               yer=g['e']['yer'], bolge=bolge(g['e']), mek=mek.get(g['e']['id'], '?'), n_yer=len(g['st']),
               istasyon=['.'.join(k) for k in g['st']], n_kontrol=len(g['kontrol']), kume=kok[i])
          for i, g in enumerate(kg)],
    bolge_olay=dict(blg), bolge_kume=dict(blgK), yer_sayisi=dict(sorted(ist.items())),
    kontrol_sayisi_dagilimi=dict(sorted(ncont.items())))
print('\nANA (R=100, n>=2) kontrollü olaylar bölgeye göre:', dict(blg.most_common()))
print('kümeler bölgeye göre:', dict(blgK.most_common()))
print('olay başına yer sayısı:', dict(sorted(ist.items())))
print('olay başına kontrol sayısı (temiz olaylar):', dict(sorted(ncont.items())))

# kontrol havuzu: epok başına, dünyada sakin ve 5 yıl kesintisiz açık istasyonlu M6,5 merkezleri ve istasyon sayısı
havuz = {}
for T in (dt.date(2005, 1, 1), dt.date(2010, 1, 1), dt.date(2015, 1, 1), dt.date(2020, 1, 1), dt.date(2023, 1, 1)):
    a, b = T - yil(TABAN_YIL), T - TD(days=1)
    kap = [i for i, k in enumerate(ANAHTAR) if ACIK[i] and kapsar(k, a, b)]
    nm = 0
    for c in MERKEZ:
        st, _ = uygun(c['la'], c['lo'], 100.0, a, b)
        if len(st) >= 2 and sakin(c['la'], c['lo'], T - yil(ONCE_TEMIZ), T + yil(KONTROL_SONRA)): nm += 1
    havuz[str(T)] = dict(acik_5y_istasyon=len(kap), sakin_merkez_n2=nm)
    print(f"havuz T={T}: 5 yıl kesintisiz açık istasyon {len(kap)}; sakin kontrol merkezi (>=2 yer, 100 km) {nm}")
sonuc['havuz'] = havuz

# hacim: ana satırdaki istasyon-yılı (olay + 10 kontrol), 3 bileşen
oy = sum(len(g['st']) for g in kg) * TABAN_YIL
ky = sum(sum(len(st) for _, st in g['kontrol']) for g in kg) * TABAN_YIL
ky_tekil = len({(ANAHTAR[i], g['e']['t'].year) for g in kg for _, st in g['kontrol'] for i in st})
sr = collections.Counter('HH' if oran[k] >= 80 else 'BH' for g in kg for k in g['st'])
sonuc['hacim'] = dict(olay_istasyon_yili=oy, kontrol_istasyon_yili=ky, kontrol_tekil_istasyon_olayyili=ky_tekil,
                      olay_ist_ornekleme=dict(sr))
print(f"\nhacim: olay istasyon-yılı {oy}, kontrol istasyon-yılı {ky} (tekrar sayılı); olay istasyonu örnekleme {dict(sr)}")
if JSON:
    json.dump(sonuc, open(JSON, 'w'), indent=1, ensure_ascii=False, default=str)
