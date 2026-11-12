#!/usr/bin/env python3
"""TR-7 kapı K0: dalga formu VARLIK yoklaması (yalnız HTTP kodu ve bayt; içerik çözülmez, diske yazılmaz).

Tanımlar `kayit/onkayit/TR-7_SAYIM.md` bölüm 2 ve Ek 1'dedir. Aday kümesi `tr7_sayim.py` ile aynı kurallarla
(aynı önbellekteki ComCat ve istasyon yanıtlarından) yeniden üretilir: kaba τ ≥ 2 kPa (×1) olan her
(tetikleyici × segment) çiftinde, segment izine ≤50 km ve epoku pencereyi örten istasyonlar; çiftte epokla ≥3
istasyon yoksa çift zaten taranamaz, yoklanmaz. Her (istasyon × tetikleyici) için bir istek:
  - pencere: istasyonun kendi uzaklığına göre W = [T0 + Δ/5 km/s, T0 + Δ/2,8 km/s + 600 s], W'nin ortasından 10 sn;
  - kanal: o anda epokta olan ilk Z kanalı, HHZ > BHZ > EHZ > SHZ > öteki (HPZ, EPZ ...) sırasıyla;
  - servis: KO/TL/IJ/6G -> KOERI; istasyon üstverisi EIDA federatörden gelmişse federatör; yoksa EarthScope.
Sınıflama: 200 ve >0 bayt = var; 204/404 (ya da 200 ve 0 bayt) = yok; 401/403 = kısıtlı (atlatılmaz);
öteki = belirsiz (bir kez yeniden denenir). 429/503: bekle, en çok 2 kez yeniden dene.
Nezaket: tek akış, istekler arası ≥0,5 sn, genel User-Agent.

Yanıt özeti (url -> kod, bayt) <onbellek>/varlik_onb.jsonl'e eklenir; yeniden koşuda ağa çıkılmaz.

Kullanım: python3 -I -B tr7_varlik.py <onbellek_dizini> [--csv-dir dizin] [--json ozet.json] [--hiz hiz.json] [--yalniz-plan]
"""
import csv, datetime as dt, io, json, math, os, sys, time, urllib.request, urllib.error, urllib.parse

ONB = sys.argv[1]
ARG = sys.argv[2:]
def arg(ad, vars=None):
    return ARG[ARG.index(ad) + 1] if ad in ARG else vars

# ------------------------------------------------------------------ tr7_sayim.py ile aynı sabitler
KUTU = (39.5, 41.5, 26.0, 34.0)
G_PA, C_MS = 30e9, 3500.0
ESIK = 2.0
CARPAN = {'x1/3': 1/3, 'x1': 1.0, 'x3': 3.0}
DERIN_MAX, D_FAY, N_IST, SR_MIN = 100.0, 50.0, 3, 20.0
BANT_KOD, ALET_KOD = set('HBES'), set('HP')
V_ON, V_ARKA, KUYRUK = 5.0, 2.8, 600.0
KOERI_AG = {'KO', 'TL', 'IJ', '6G'}
DISLA_AG = {'ZQ', 'SY'}
SON_GUN = dt.datetime(2026, 1, 1)          # 2026 ve sonrası kör: bu andan sonra veri istenmez
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
DS = {'koeri': 'https://eida.koeri.boun.edu.tr/fdsnws/dataselect/1/query?',
      'eida_federator': 'https://federator.orfeus-eu.org/fdsnws/dataselect/1/query?',
      'earthscope': 'https://service.earthscope.org/fdsnws/dataselect/1/query?'}
UA = 'fdsn-availability-probe/1.0 (python-urllib)'
KANAL_SIRA = ['HHZ', 'BHZ', 'EHZ', 'SHZ']
# hacim varsayımları (TR-7_SAYIM.md bölüm 5): 100 Hz, ≈0,55 MB/saat/kanal, 3 bileşen, başvuru 1 saat, 10 negatif kontrol
MB_SAAT_KANAL, BILESEN, BASVURU_S, N_NEG = 0.55, 3, 3600.0, 10

def zaman(s):
    s = s.strip().replace('Z', '')
    if not s: return None
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
    return sum(p[1] for p in iz)/len(iz), sum(p[0] for p in iz)/len(iz)

def pgv_cms(M, d_km):
    D = max(d_km / 111.195, 1.0)
    return 2 * math.pi * 10 ** (M - 1.66 * math.log10(D) - 3.3) * 1e-4

def kpa(pgv):
    return G_PA * pgv * 1e-2 / C_MS / 1e3

def pencere_d(e, d_km):
    return e['t'] + dt.timedelta(seconds=d_km / V_ON), e['t'] + dt.timedelta(seconds=d_km / V_ARKA + KUYRUK)

# ------------------------------------------------------------------ 1. tetikleyiciler (önbellekten)
olaylar = []
for r in csv.DictReader(io.StringIO(open(os.path.join(ONB, 'comcat_m75.csv'), encoding='utf-8').read())):
    t = zaman(r['time'])
    if t.year >= 2026 or r['type'] != 'earthquake': continue
    e = dict(id=r['id'], t=t, la=float(r['latitude']), lo=float(r['longitude']), z=float(r['depth'] or 0),
             M=float(r['mag']), yer=r['place'])
    if e['z'] > DERIN_MAX: continue
    e['d_seg'] = {s: hav(e['la'], e['lo'], *orta(iz)) for s, iz in SEGMENT.items()}
    e['kpa_seg'] = {s: kpa(pgv_cms(e['M'], d)) for s, d in e['d_seg'].items()}
    e['bolgesel'] = hav(e['la'], e['lo'], 40.85, 29.0) < 20 * 111.195
    olaylar.append(e)

# ------------------------------------------------------------------ 2. istasyonlar (kanal epoklarıyla)
ist = {}
for kay in ('koeri', 'eida_federator', 'earthscope'):
    yol = os.path.join(ONB, f'st_{kay}.txt')
    if not os.path.exists(yol): continue
    for sat in open(yol, encoding='utf-8', errors='replace').read().splitlines():
        if not sat.strip() or sat.startswith('#'): continue
        f = [x.strip() for x in sat.split('|')]
        net, sta, loc, cha = f[0], f[1], f[2], f[3]
        la, lo, sr = float(f[4]), float(f[5]), float(f[14] or 0)
        if not (KUTU[0] <= la <= KUTU[1] and KUTU[2] <= lo <= KUTU[3]): continue
        if net in DISLA_AG: continue
        if len(cha) != 3 or cha[2] != 'Z' or cha[0] not in BANT_KOD or cha[1] not in ALET_KOD: continue
        if sr < SR_MIN: continue
        d = ist.setdefault((net, sta), dict(net=net, sta=sta, la=la, lo=lo, kanal=[], kaynak=set()))
        d['kanal'].append(dict(loc=loc, cha=cha, a=zaman(f[15]), b=zaman(f[16]) if f[16] else None, kay=kay))
        d['kaynak'].add(kay)
for d in ist.values():
    d['yakin'] = [s for s, iz in SEGMENT.items() if nokta_cizgi(d['la'], d['lo'], iz) <= D_FAY]

def epokta(d, t0, t1):
    return any(k['a'] <= t0 and (k['b'] is None or k['b'] >= t1) for k in d['kanal'])

def servis(d):
    if d['net'] in KOERI_AG: return 'koeri'
    if 'eida_federator' in d['kaynak']: return 'eida_federator'
    return 'earthscope'

def kanal_sec(d, t0, t1):
    uy = [k for k in d['kanal'] if k['a'] <= t0 and (k['b'] is None or k['b'] >= t1)]
    if not uy: return None
    sira = lambda k: (KANAL_SIRA.index(k['cha']) if k['cha'] in KANAL_SIRA else 9, k['loc'] not in ('', '00'), k['loc'])
    return sorted(uy, key=sira)[0]

# ------------------------------------------------------------------ 3. aday (tetikleyici × segment) çiftleri
def ciftler(carpan, esik=ESIK):
    out = []
    for e in olaylar:
        for s in SEGMENT:
            k = e['kpa_seg'][s] * carpan
            if k < esik: continue
            a, b = pencere_d(e, e['d_seg'][s])
            ep = [d for d in ist.values() if s in d['yakin'] and epokta(d, a, b)]
            out.append(dict(e=e, s=s, kpa=k, ep=ep))
    return out

cift_x1 = ciftler(1.0)
aday = {}            # (net, sta, olay) -> istek
for c in cift_x1:
    if len(c['ep']) < N_IST: continue
    for d in c['ep']:
        anahtar = (d['net'], d['sta'], c['e']['id'])
        if anahtar in aday: aday[anahtar]['segment'].add(c['s']); continue
        e = c['e']
        a, b = pencere_d(e, hav(e['la'], e['lo'], d['la'], d['lo']))
        orta_t = a + (b - a) / 2
        t0, t1 = orta_t.replace(microsecond=0), orta_t.replace(microsecond=0) + dt.timedelta(seconds=10)
        assert t1 < SON_GUN, 'kör dönem'
        k = kanal_sec(d, a, b) or kanal_sec(d, t0, t1)
        if k is None: continue
        srv = servis(d)
        q = urllib.parse.urlencode(dict(network=d['net'], station=d['sta'], location=k['loc'] or '--',
                                        channel=k['cha'], starttime=t0.strftime('%Y-%m-%dT%H:%M:%S'),
                                        endtime=t1.strftime('%Y-%m-%dT%H:%M:%S'), nodata='404'))
        aday[anahtar] = dict(net=d['net'], sta=d['sta'], cha=k['cha'], loc=k['loc'], olay=e['id'], srv=srv,
                             url=DS[srv] + q, segment={c['s']}, W_s=(b - a).total_seconds())

if '--yalniz-plan' in ARG:
    from collections import Counter
    print('istek:', len(aday), Counter(x['srv'] for x in aday.values()), Counter(x['net'] for x in aday.values()))
    sys.exit(0)

# ------------------------------------------------------------------ 4. yoklama (önbellekli)
ONB_DOSYA = os.path.join(ONB, 'varlik_onb.jsonl')
onb = {}
if os.path.exists(ONB_DOSYA):
    for sat in open(ONB_DOSYA, encoding='utf-8'):
        if sat.strip():
            x = json.loads(sat); onb[x['url']] = x
son_istek = [0.0]
def tek(url):
    bekle = 0.5 - (time.time() - son_istek[0])
    if bekle > 0: time.sleep(bekle)
    son_istek[0] = time.time()
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            n = 0
            while True:
                b = r.read(65536)
                if not b: break
                n += len(b)                     # içerik çözülmez, saklanmaz
            return r.status, n, time.time() - t, None
    except urllib.error.HTTPError as e:
        return e.code, 0, time.time() - t, e.headers.get('Retry-After')
    except Exception as e:
        return f'hata:{type(e).__name__}', 0, time.time() - t, None

def sinif(kod, n):
    if kod == 200 and n > 0: return 'var'
    if kod in (204, 404) or (kod == 200 and n == 0): return 'yok'
    if kod in (401, 403): return 'kisitli'
    return 'belirsiz'

def yokla(url):
    if url in onb: return onb[url]
    deneme, mesgul = [], 0
    while True:
        kod, n, sure, ra = tek(url)
        deneme.append(kod)
        if kod in (429, 503) and mesgul < 2:
            mesgul += 1
            try: w = min(float(ra), 120.0)
            except (TypeError, ValueError): w = 30.0 * mesgul
            time.sleep(w); continue
        if sinif(kod, n) == 'belirsiz' and len(deneme) - mesgul < 2 and kod not in (429, 503):
            time.sleep(5); continue
        break
    x = dict(url=url, http=kod, bayt=n, sure=round(sure, 3), denemeler=deneme,
             zaman=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S'))
    with open(ONB_DOSYA, 'a', encoding='utf-8') as f:
        f.write(json.dumps(x) + '\n')
    onb[url] = x
    return x

sirali = sorted(aday.values(), key=lambda x: (x['srv'], x['olay'], x['net'], x['sta']))
for i, x in enumerate(sirali):
    y = yokla(x['url'])
    x.update(http=y['http'], bayt=y['bayt'], sure=y['sure'], var=sinif(y['http'], y['bayt']))
    if (i + 1) % 50 == 0:
        print(f'{i+1}/{len(sirali)}', flush=True)

# ------------------------------------------------------------------ 5. segment sayımı
var_kume = {(x['net'], x['sta'], x['olay']) for x in sirali if x['var'] == 'var'}
belirsiz_kume = {(x['net'], x['sta'], x['olay']) for x in sirali if x['var'] in ('belirsiz', 'kisitli')}

def segment_say(carpan):
    sonuc = {}
    for s in SEGMENT:
        sat = []
        for c in ciftler(carpan):
            if c['s'] != s: continue
            e = c['e']
            n_var = sum((d['net'], d['sta'], e['id']) in var_kume for d in c['ep'])
            n_bel = sum((d['net'], d['sta'], e['id']) in belirsiz_kume for d in c['ep'])
            n_yoklanmadi = sum((d['net'], d['sta'], e['id']) not in aday for d in c['ep'])
            sat.append(dict(olay=e['id'], kpa=c['kpa'], bolgesel=e['bolgesel'], n_epok=len(c['ep']),
                            n_var=n_var, n_bel=n_bel, n_yoklanmadi=n_yoklanmadi))
        ok = sorted([r for r in sat if r['n_var'] >= N_IST], key=lambda r: -r['kpa'])
        okb = [r for r in ok if not r['bolgesel']]
        # yoklanmamış (yalnız ×3'te ortaya çıkan) istasyonlar varsa en iyi durum üst sınırı
        ust = [r for r in sat if r['n_var'] + r['n_bel'] + r['n_yoklanmadi'] >= N_IST]
        sonuc[s] = dict(esik_ustu=len(sat), n=len(ok), n_bolgesel_haric=len(okb),
                        tau8=round(ok[7]['kpa'], 2) if len(ok) >= 8 else None,
                        tau5=round(ok[4]['kpa'], 2) if len(ok) >= 5 else None,
                        tau8_bolgesel_haric=round(okb[7]['kpa'], 2) if len(okb) >= 8 else None,
                        ust_sinir_yoklanmamis_dahil=len(ust),
                        olaylar=[(r['olay'], round(r['kpa'], 2), r['n_var']) for r in ok])
    return sonuc

def hukum(n):
    return 'GECTI' if n >= 8 else ('ZAYIF' if n >= 5 else 'GECMEDI')

ozet = dict(tarih=dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d'), istek=len(sirali), esik_kpa=ESIK,
            yeniden_deneme=sum(1 for x in sirali if len(onb[x['url']]['denemeler']) > 1))
from collections import Counter, defaultdict
ag = defaultdict(Counter)
for x in sirali: ag[f"{x['net']} ({x['srv']})"][x['var']] += 1
ozet['ag_dagilim'] = {k: dict(v) for k, v in sorted(ag.items())}
ozet['http_dagilim'] = dict(Counter(str(x['http']) for x in sirali))
ozet['toplam_bayt'] = sum(x['bayt'] for x in sirali)
ozet['ortalama_sure_s'] = round(sum(x['sure'] for x in sirali) / max(1, len(sirali)), 3)
ozet['segment'] = {k: segment_say(c) for k, c in CARPAN.items()}
k0 = {s: ozet['segment']['x1'][s] for s in list(SEGMENT)[:3]}
ozet['K0'] = dict(
    x1={s: (v['n'], hukum(v['n']), v['tau8']) for s, v in k0.items()},
    x1_bolgesel_haric={s: (v['n_bolgesel_haric'], hukum(v['n_bolgesel_haric']), v['tau8_bolgesel_haric'])
                       for s, v in k0.items()},
    x1_3={s: (ozet['segment']['x1/3'][s]['n'], hukum(ozet['segment']['x1/3'][s]['n'])) for s in k0},
    x3={s: (ozet['segment']['x3'][s]['n'], hukum(ozet['segment']['x3'][s]['n'])) for s in k0})
ozet['K0']['hukum'] = min((v[1] for v in ozet['K0']['x1'].values()), key=['GECMEDI', 'ZAYIF', 'GECTI'].index)

# ------------------------------------------------------------------ 6. doğrulanmış tam tarama hacmi
dog_ciftler = [c for c in cift_x1 if sum((d['net'], d['sta'], c['e']['id']) in var_kume for d in c['ep']) >= N_IST]
ist_olay = {}
for c in dog_ciftler:
    for d in c['ep']:
        if (d['net'], d['sta'], c['e']['id']) in var_kume:
            ist_olay[(d['net'], d['sta'], c['e']['id'])] = aday[(d['net'], d['sta'], c['e']['id'])]['W_s']
saat = sum((w + BASVURU_S) / 3600 for w in ist_olay.values())
mb_tetik = saat * MB_SAAT_KANAL * BILESEN
ozet['hacim'] = dict(dogrulanmis_cift=len(dog_ciftler), dogrulanmis_olay=len({c['e']['id'] for c in dog_ciftler}),
                     istasyon_tetikleyici=len(ist_olay),
                     koeri_payi=sum(1 for k in ist_olay if aday[k]['srv'] == 'koeri'),
                     tetikleyici_mb=round(mb_tetik), negatif_kontrol_mb=round(mb_tetik * N_NEG),
                     toplam_gb=round(mb_tetik * (1 + N_NEG) / 1024, 1))
# hız: --hiz <json> (KOERI tek akış / 2 paralel akış denemesi; betik dışında bir kez yapıldı, Ek 1)
hz = arg('--hiz')
if hz and os.path.exists(hz):
    h = json.load(open(hz, encoding='utf-8'))
    toplam_kb = mb_tetik * (1 + N_NEG) * 1024
    hizlar = {'onceki_tek_akis_23kbs': 23.0, 'tek_akis_olculen': h['tek'][0]['kbs'],
              'iki_akis_olculen_toplam': h['paralel_toplam_kbs']}
    ozet['hiz_deneme'] = dict(tek=[{k: v for k, v in o.items() if k in ('q', 'http', 'bayt', 'sure', 'kbs')} for o in h['tek']],
                              paralel=[{k: v for k, v in o.items() if k in ('q', 'http', 'bayt', 'sure', 'kbs')} for o in h['paralel']],
                              oran=h['oran'])
    ozet['hacim']['sure_saat'] = {k: round(toplam_kb / v / 3600, 1) for k, v in hizlar.items()}

cd = arg('--csv-dir')
if cd:
    with open(os.path.join(cd, 'tr7_varlik.csv'), 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['istasyon', 'ag', 'kanal', 'tetikleyici', 'segment', 'http', 'bayt', 'var'])
        for x in sorted(sirali, key=lambda x: (x['olay'], x['net'], x['sta'])):
            w.writerow([x['sta'], x['net'], f"{x['loc']}.{x['cha']}" if x['loc'] else x['cha'], x['olay'],
                        '; '.join(sorted(s.split()[0] for s in x['segment'])), x['http'], x['bayt'], x['var']])
cj = arg('--json')
if cj:
    json.dump(ozet, open(cj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps({k: v for k, v in ozet.items() if k != 'segment'}, ensure_ascii=False, indent=1, default=str))
for k in CARPAN:
    print(k, {s.split()[0]: (v['esik_ustu'], v['n'], v['n_bolgesel_haric'], v['tau8'], v['ust_sinir_yoklanmamis_dahil'])
              for s, v in ozet['segment'][k].items()})
