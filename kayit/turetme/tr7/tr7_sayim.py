#!/usr/bin/env python3
"""TR-7: tetiklenmiş tremor taramasının 0 € güç kapısı sayımı (yalnız üstveri; dalga formu okunmaz).

Tanımlar `kayit/onkayit/TR-7_SAYIM.md` bölüm 2'dedir; bu betik onları kodlar.

Girdi (ağdan çekilir, ham yanıtlar depo dışında <onbellek> dizinine yazılır, varsa yeniden çekilmez):
  ComCat fdsnws/event   M>=7,5, 2005-01-01 .. 2025-12-31T23:59:59 (2026 kör)
  KOERI, EIDA federator (ORFEUS), EarthScope fdsnws/station   26-34° D, 39,5-41,5° K, kanal düzeyi, metin
  KOERI fdsnws/availability   her tetikleyicinin yüzey dalgası penceresi için (KO, TL, IJ, 6G)
  EIDA federator fdsnws/availability   KOERI dışındaki EIDA ağları için (denenir; yanıt yoksa "doğrulanamadı")
Reddedilen ya da yanıt vermeyen servis atlatılmaz; durum kodu çıktıya yazılır.

Kullanım: python3 -I -B tr7_sayim.py <onbellek_dizini> [--json çıktı.json] [--csv-dir dizin]
"""
import csv, datetime as dt, io, json, math, os, sys, time, urllib.request, urllib.error, urllib.parse

ONB = sys.argv[1]
ARG = sys.argv[2:]
def arg(ad, vars=None):
    return ARG[ARG.index(ad) + 1] if ad in ARG else vars
os.makedirs(ONB, exist_ok=True)

# ------------------------------------------------------------------ önceden sabit tanımlar (bölüm 2)
BAS, SON = '2005-01-01T00:00:00', '2025-12-31T23:59:59'
M_MIN = 7.5
DERIN_MAX = 100.0                 # km; daha derin olaylar yüzey dalgası üretmez, ayrı sayılır
KUTU = (39.5, 41.5, 26.0, 34.0)   # minlat, maxlat, minlon, maxlon
G_PA, C_MS = 30e9, 3500.0         # dinamik gerilme = G * PGV / c  (1 cm/s ~ 85,7 kPa)
ESIK_ANA = 2.0                    # kPa; Parkfield 2-3 kPa'nın alt ucu (Peng vd. 2009)
ESIKLER = [1.0, 2.0, 3.0, 5.0, 7.5]
PGV_CARPAN = [1/3, 1.0, 3.0]      # kaba PGV tahmininin belirsizliği (duyarlılık)
D_FAY = 50.0                      # km; istasyon fay izine en çok bu kadar
N_IST = 3                         # taranabilir çift için en az istasyon
ORT = 0.9                         # pencerenin en az bu kesri kayıtta olmalı
SR_MIN = 20.0                     # Hz; 2-8 Hz bandı için
BANT_KOD = set('HBES')            # HH?, BH?, EH?, SH?
ALET_KOD = set('HP')              # yüksek kazançlı sismometre (H) ya da geofon (P: EP?, DP?)
V_ON, V_ARKA, KUYRUK = 5.0, 2.8, 600.0   # pencere: [T0 + D/5 km/s, T0 + D/2,8 km/s + 600 s]
KOERI_AG = {'KO', 'TL', 'IJ', '6G'}
DISLA_AG = {'ZQ', 'SY'}           # ZQ: İstanbul DAS ayı (gerinim hızı), SY: sentetik

# Fay izi: KAF ve güney kolu, elle sayısallaştırılmış kaba iz (±5-10 km; 50 km ölçütü için yeterli).
SEGMENT = {
    'S1 Ganos-Saros':           [(26.20, 40.55), (26.90, 40.62), (27.50, 40.80)],
    'S2 Orta Marmara-Adalar':   [(27.50, 40.80), (28.00, 40.82), (28.60, 40.85), (29.00, 40.83)],
    'S3 Cinarcik-Izmit':        [(29.00, 40.83), (29.30, 40.72), (29.90, 40.72)],
    'S4 Sapanca-Duzce':         [(29.90, 40.72), (30.30, 40.70), (30.80, 40.75), (31.20, 40.80)],
    'S5 Bolu-Gerede-Ismetpasa': [(31.20, 40.80), (31.60, 40.73), (32.20, 40.80), (32.60, 40.87)],
    'S6 Cerkes-Tosya':          [(32.60, 40.87), (33.30, 40.90), (34.00, 41.02)],
    'S7 Guney kol (Geyve-Biga)':[(30.30, 40.50), (29.50, 40.43), (29.10, 40.42), (28.30, 40.33),
                                 (27.50, 40.25), (27.00, 40.10), (26.60, 39.70)],
}

LOG = []
def getir(url, ad, zorunlu=True):
    yol = os.path.join(ONB, ad)
    if os.path.exists(yol):
        LOG.append(dict(url=url, durum='onbellek', bayt=os.path.getsize(yol)))
        return open(yol, encoding='utf-8', errors='replace').read()
    for dene in range(3):
        try:
            with urllib.request.urlopen(url, timeout=180) as r:
                b = r.read()
                LOG.append(dict(url=url, durum=r.status, bayt=len(b)))
                open(yol, 'wb').write(b)
                return b.decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 204:
                LOG.append(dict(url=url, durum=204, bayt=0)); open(yol, 'w').close(); return ''
            LOG.append(dict(url=url, durum=e.code, bayt=0))
            if e.code in (400, 401, 403, 404, 405, 407): break
        except Exception as e:
            LOG.append(dict(url=url, durum=f'hata:{type(e).__name__}', bayt=0))
        time.sleep(2 * (dene + 1))
    if zorunlu:
        raise SystemExit(f'erişilemedi (atlatılmadı): {url}')
    return None

def zaman(s):
    s = s.strip()
    if not s: return None
    s = s.replace('Z', '')
    for f in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try: return dt.datetime.strptime(s, f)
        except ValueError: pass
    raise ValueError(s)

R = 6371.0
def hav(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    a = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(math.radians(lo2-lo1)/2)**2
    return 2*R*math.asin(min(1, math.sqrt(a)))

def nokta_cizgi(la, lo, iz):
    """Yerel düzlem (eşdikdörtgen) yaklaşımıyla noktanın çoklu çizgiye en kısa uzaklığı, km."""
    k = math.cos(math.radians(la)) * 111.195
    px, py = lo * k, la * 111.195
    en = 1e9
    for (x1, y1), (x2, y2) in zip(iz[:-1], iz[1:]):
        ax, ay, bx, by = x1*k, y1*111.195, x2*k, y2*111.195
        dx, dy = bx-ax, by-ay
        t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
        en = min(en, math.hypot(px-(ax+t*dx), py-(ay+t*dy)))
    return en

def orta(iz):
    la = sum(p[1] for p in iz)/len(iz); lo = sum(p[0] for p in iz)/len(iz)
    return la, lo

def pgv_cms(M, d_km):
    """Kaba yüzey dalgası tepe yer hızı: Prag Ms bağıntısı tersten (A/T, T=20 s), V = 2*pi*A/T.
    20°-160° için geçerli; daha yakında 'bölgesel' işaretlenir, Mw>8'de Ms doygunluğu yok sayılır."""
    D = max(d_km / 111.195, 1.0)
    a_t = 10 ** (M - 1.66 * math.log10(D) - 3.3)      # mikrometre / s
    return 2 * math.pi * a_t * 1e-4                    # cm/s

def kpa(pgv):
    return G_PA * pgv * 1e-2 / C_MS / 1e3

# ------------------------------------------------------------------ 1. tetikleyiciler
q = urllib.parse.urlencode(dict(starttime=BAS, endtime=SON, minmagnitude=M_MIN, orderby='time-asc', format='csv'))
ev_txt = getir('https://earthquake.usgs.gov/fdsnws/event/1/query?' + q, 'comcat_m75.csv')
olaylar = []
for r in csv.DictReader(io.StringIO(ev_txt)):
    t = zaman(r['time'])
    if t.year >= 2026: continue
    if r['type'] != 'earthquake': continue
    olaylar.append(dict(id=r['id'], t=t, la=float(r['latitude']), lo=float(r['longitude']),
                        z=float(r['depth'] or 0), M=float(r['mag']), yer=r['place']))
SEG_ORTA = {s: orta(iz) for s, iz in SEGMENT.items()}
for e in olaylar:
    e['d_seg'] = {s: hav(e['la'], e['lo'], *SEG_ORTA[s]) for s in SEGMENT}
    e['d_ref'] = hav(e['la'], e['lo'], 40.85, 29.0)          # İstanbul açığı başvuru
    e['pgv'] = pgv_cms(e['M'], e['d_ref'])
    e['kpa'] = kpa(e['pgv'])
    e['kpa_seg'] = {s: kpa(pgv_cms(e['M'], d)) for s, d in e['d_seg'].items()}
    e['bolgesel'] = e['d_ref'] < 20 * 111.195
    e['derin'] = e['z'] > DERIN_MAX

# ------------------------------------------------------------------ 2. istasyonlar
B = urllib.parse.urlencode(dict(minlat=KUTU[0], maxlat=KUTU[1], minlon=KUTU[2], maxlon=KUTU[3],
                                level='channel', format='text'))
KAYNAK = {'koeri': 'https://eida.koeri.boun.edu.tr/fdsnws/station/1/query?',
          'eida_federator': 'https://federator.orfeus-eu.org/fdsnws/station/1/query?',
          'earthscope': 'https://service.earthscope.org/fdsnws/station/1/query?'}
kanal = {}
kaynak_ozet = {}
for k, u in KAYNAK.items():
    txt = getir(u + B, f'st_{k}.txt', zorunlu=False)
    if txt is None:
        kaynak_ozet[k] = 'erişilemedi'; continue
    n = 0
    for sat in txt.splitlines():
        if not sat.strip() or sat.startswith('#'): continue
        f = [x.strip() for x in sat.split('|')]
        net, sta, loc, cha = f[0], f[1], f[2], f[3]
        la, lo, sr = float(f[4]), float(f[5]), float(f[14] or 0)
        if not (KUTU[0] <= la <= KUTU[1] and KUTU[2] <= lo <= KUTU[3]): continue
        if net in DISLA_AG: continue
        if len(cha) != 3 or cha[2] != 'Z' or cha[0] not in BANT_KOD or cha[1] not in ALET_KOD: continue
        if sr < SR_MIN: continue
        anahtar = (net, sta)
        d = kanal.setdefault(anahtar, dict(net=net, sta=sta, la=la, lo=lo, ep=set(), kanal=set(), kaynak=set()))
        d['ep'].add((zaman(f[15]), zaman(f[16]) if f[16] else None))
        d['kanal'].add(cha); d['kaynak'].add(k); n += 1
    kaynak_ozet[k] = n
for d in kanal.values():
    d['fay'] = {s: nokta_cizgi(d['la'], d['lo'], iz) for s, iz in SEGMENT.items()}
    d['yakin'] = [s for s, x in d['fay'].items() if x <= D_FAY]

def epokta(d, t0, t1):
    return any(a <= t0 and (b is None or b >= t1) for a, b in d['ep'])

def pencere(e, s):
    D = e['d_seg'][s]
    return e['t'] + dt.timedelta(seconds=D / V_ON), e['t'] + dt.timedelta(seconds=D / V_ARKA + KUYRUK)

# ------------------------------------------------------------------ 3. veri varlığı (yalnız üstveri)
def kullanilabilirlik(e, taban, aglar, ad):
    t0 = min(pencere(e, s)[0] for s in SEGMENT); t1 = max(pencere(e, s)[1] for s in SEGMENT)
    q = urllib.parse.urlencode(dict(network=','.join(sorted(aglar)), station='*', channel='?HZ,?PZ',
                                    starttime=t0.strftime('%Y-%m-%dT%H:%M:%S'),
                                    endtime=t1.strftime('%Y-%m-%dT%H:%M:%S'),
                                    format='text', merge='samplerate,quality,overlap'), safe='*,?')
    txt = getir(taban + q, ad, zorunlu=False)
    if txt is None: return None
    sp = {}
    for sat in txt.splitlines():
        if not sat.strip() or sat.startswith('#'): continue
        f = sat.split()
        if len(f) < 6: continue
        sp.setdefault((f[0], f[1]), []).append((zaman(f[-2]), zaman(f[-1])))
    return sp

def ortu(spans, a, b, gece=False):
    """Pencerenin kayıtta olan kesri. gece=True: tam 00:00:00'da biten aralık ertesi güne uzatılır
    (KOERI kullanılabilirlik dizininin gün sınırında kesildiği görüldü; üst sınır değişkesi)."""
    if not spans: return 0.0
    tot = 0.0
    if gece:
        spans = [(x, y + dt.timedelta(days=1)) if (y.hour, y.minute, y.second, y.microsecond) == (0, 0, 0, 0)
                 else (x, y) for x, y in spans]
    for x, y in spans:
        lo, hi = max(x, a), min(y, b)
        if hi > lo: tot += (hi - lo).total_seconds()
    return tot / (b - a).total_seconds()

aday_ister = arg('--esik')
esik_ana = float(aday_ister) if aday_ister else ESIK_ANA
gecen = [e for e in olaylar if not e['derin'] and max(e['kpa_seg'].values()) >= min(ESIKLER) / 3]
diger_ag = sorted({d['net'] for d in kanal.values() if d['yakin'] and d['net'] not in KOERI_AG})
for e in gecen:
    e['av_koeri'] = kullanilabilirlik(e, 'https://eida.koeri.boun.edu.tr/fdsnws/availability/1/query?',
                                      KOERI_AG, f'av_koeri_{e["id"]}.txt')
    e['av_fed'] = (kullanilabilirlik(e, 'https://federator.orfeus-eu.org/fdsnws/availability/1/query?',
                                     set(diger_ag), f'av_fed_{e["id"]}.txt') if diger_ag else {})

# ------------------------------------------------------------------ 4. sayım
def cift_say(esik, carpan):
    sat = []
    for e in gecen:
        for s in SEGMENT:
            k = kpa(pgv_cms(e['M'], e['d_seg'][s]) * carpan)
            if k < esik: continue
            a, b = pencere(e, s)
            ep = [d for d in kanal.values() if s in d['yakin'] and epokta(d, a, b)]
            dog, dogrulanamaz, gece = [], [], []
            for d in ep:
                av = e['av_koeri'] if d['net'] in KOERI_AG else e['av_fed']
                if av is None:
                    dogrulanamaz.append(d); continue
                if ortu(av.get((d['net'], d['sta'])), a, b) >= ORT: dog.append(d)
                if ortu(av.get((d['net'], d['sta'])), a, b, gece=True) >= ORT: gece.append(d)
            sat.append(dict(olay=e['id'], t=e['t'].isoformat(), M=e['M'], segment=s, kpa=round(k, 2),
                            bolgesel=e['bolgesel'], n_epok=len(ep), n_veri=len(dog),
                            n_dogrulanamaz=len(dogrulanamaz), n_veri_gece=len(gece),
                            veri_ist=' '.join(sorted(f"{d['net']}.{d['sta']}" for d in dog))))
    return sat

ozet = dict(log_ozet={}, kaynak_kanal_satiri=kaynak_ozet)
ana = cift_say(esik_ana, 1.0)
def topla(sat, alan='n_veri'):
    cift = [x for x in sat if x[alan] >= N_IST]
    return dict(cift_esik_ustu=len(sat), taranabilir_cift=len(cift),
                taranabilir_olay=len({x['olay'] for x in cift}),
                taranabilir_segment=sorted({x['segment'] for x in cift}),
                bolgesel_haric_cift=len([x for x in cift if not x['bolgesel']]),
                bolgesel_haric_olay=len({x['olay'] for x in cift if not x['bolgesel']}))
ozet['ana'] = dict(esik_kpa=esik_ana, **topla(ana))
ozet['ana_epok_ile'] = topla(ana, 'n_epok')
ozet['ana_gece_uzatma'] = topla(ana, 'n_veri_gece')
ozet['duyarlilik'] = []
for es in ESIKLER:
    for c in PGV_CARPAN:
        sat = cift_say(es, c)
        ozet['duyarlilik'].append(dict(esik_kpa=es, pgv_carpan=round(c, 3), **topla(sat)))
# segment başına
ozet['segment'] = {}
for s in SEGMENT:
    x = [r for r in ana if r['segment'] == s]
    ozet['segment'][s] = dict(cift_esik_ustu=len(x), taranabilir=len([r for r in x if r['n_veri'] >= N_IST]),
                              ist_yakin_toplam=len([d for d in kanal.values() if s in d['yakin']]))
ozet['olay_sayisi'] = dict(toplam=len(olaylar), derin=len([e for e in olaylar if e['derin']]),
                           sig=len([e for e in olaylar if not e['derin']]),
                           **{f'ref_kpa>={es}': len([e for e in olaylar if not e['derin'] and e['kpa'] >= es])
                              for es in ESIKLER})
ozet['istasyon'] = dict(toplam_kutu=len(kanal), fay_50km=len([d for d in kanal.values() if d['yakin']]),
                        ag=sorted({d['net'] for d in kanal.values() if d['yakin']}))
ozet['diger_ag_availability'] = {e['id']: ('yok/erişilemedi' if e['av_fed'] is None else len(e['av_fed']))
                                 for e in gecen} if diger_ag else 'diger ag yok'
ozet['log'] = LOG

cikti = arg('--json')
if cikti:
    json.dump(ozet, open(cikti, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
cd = arg('--csv-dir')
if cd:
    with open(os.path.join(cd, 'tr7_tetikleyici.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['id', 'zaman', 'M', 'derinlik_km', 'yer', 'uzaklik_km', 'pgv_cms_kaba', 'kpa_kaba',
                    'bolgesel', 'derin'])
        for e in sorted(olaylar, key=lambda e: -e['kpa']):
            w.writerow([e['id'], e['t'].isoformat(), e['M'], e['z'], e['yer'], round(e['d_ref']),
                        f"{e['pgv']:.4f}", f"{e['kpa']:.2f}", int(e['bolgesel']), int(e['derin'])])
    with open(os.path.join(cd, 'tr7_cift.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(ana[0].keys()) if ana else ['bos'])
        w.writeheader(); [w.writerow(r) for r in ana]
    with open(os.path.join(cd, 'tr7_istasyon.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['ag', 'istasyon', 'enlem', 'boylam', 'kanallar', 'ilk_epok', 'son_epok', 'kaynak',
                    'yakin_segmentler', 'en_yakin_fay_km'])
        for d in sorted(kanal.values(), key=lambda d: (d['net'], d['sta'])):
            if not d['yakin']: continue
            a = min(x for x, _ in d['ep']); b = None if any(y is None for _, y in d['ep']) else max(y for _, y in d['ep'])
            w.writerow([d['net'], d['sta'], d['la'], d['lo'], ' '.join(sorted(d['kanal'])), a.date(),
                        b.date() if b else 'açık', ' '.join(sorted(d['kaynak'])), '; '.join(d['yakin']),
                        round(min(d['fay'].values()), 1)])
print(json.dumps({k: v for k, v in ozet.items() if k not in ('log', 'duyarlilik')}, ensure_ascii=False,
                 indent=1, default=str))
for r in ozet['duyarlilik']:
    print(r['esik_kpa'], r['pgv_carpan'], r['cift_esik_ustu'], r['taranabilir_cift'], r['taranabilir_olay'],
          r['bolgesel_haric_cift'], r['bolgesel_haric_olay'])
print('servis durumları:', sorted({(str(x['durum'])) for x in LOG}))
