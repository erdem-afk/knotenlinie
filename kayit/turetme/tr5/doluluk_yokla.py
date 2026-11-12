#!/usr/bin/env python3
"""TR-5 (M>=6,0 değişkesi) ve TR-4 (KO ağı): gerçek veri DOLULUĞU yoklaması (yalnız varlık sayımı).

Dalga formu okunmaz ve saklanmaz. Her (istasyon, ay) için ayın 15'i 12:00:00-12:01:00 UTC aralığında tek
düşey kanal isteği (cha=BHZ,HHZ, loc=*) fdsnws/dataselect'e atılır; yalnız HTTP kodu ve bayt sayısı önbelleğe
yazılır. Kanal listesi iki kodu birlikte ister, çünkü üstveride BHZ görünüp arşivde yalnız HHZ olan istasyonlar
var (12 Kasım denemesi: AC.PHP BHZ 204, BHZ,HHZ 200).
Availability servisleri kapalı (EarthScope, 404 "retired") ya da eksik raporluyor (KOERI); bu yüzden doğrudan
dataselect ile yoklanır. Tanımlar ve kurallar: `kayit/onkayit/TR-5_TR-4_SAYIM.md` (bölüm 2-4 ve Ek 1).

Kurallar (önceden sabit):
  - Bir ay "veri var": HTTP 200 ve bayt > 0. 204/404: yok. 401/403: "kısıtlı" (veri yok sayılır, atlatılmaz).
    Öteki kodlar ve ağ hataları: "hata" (ana kuralda veri yok sayılır; ayrıca sayılır).
  - İstasyon-penceresi "dolu" (ana): pencere aylarının >= %80'inde veri var VE en uzun ardışık boş ay <= 3.
    Duyarlılık: gevşek (>= %60, <= 6 ay), sıkı (>= %90, <= 2 ay).
  - TR-5 aday çiftleri: sayim_ustveri.py'nin M>=6,0 (z<=30, 2000-2023, R=100 km) değişkesinde temiz ve >=5
    kontrollü olayların, 100 km içindeki açık ve metadata ile kesintisiz kapsanan BÜTÜN istasyonları; pencere
    [T-taban, T-1g], taban 3 ve 5 yıl. Yerinde plasebo için [T-2*taban, T-1g]. Kontrol havuzu yoklanmaz.
    Toplam istek 15 000'i aşarsa olay başına en yakın 3 yer ile sınırlanır (çıktıda yazılır).
  - TR-4: tr4_sayim.py ana kuralında pencereli 24 KO istasyonu, 2012-01 ... 2023-12 her ay.
  - Bütün istek zamanları <= 2023-12-15 (2026 verisi yok).

Nezaket: servis (sunucu) başına tek akış; EarthScope/GEOFON/ORFEUS istekler arası >= 0,3 sn, KOERI >= 2 sn,
öteki merkezler >= 0,5 sn; 429/503'te bekle, en çok 2 yeniden deneme; genel User-Agent; TLS doğrulaması açık.

Kullanım (python3 -I -B):
  doluluk_yokla.py aday  <ham> <ngl> <tr2> <onbellek_dizini>     istek listesini kurar (istekler.json)
  doluluk_yokla.py yokla <onbellek_dizini> [sure_sn]              istekleri atar (yeniden başlatılabilir)
  doluluk_yokla.py say   <ham> <ngl> <tr2> <onbellek_dizini>     tr5_doluluk.csv, tr4_doluluk.csv,
                                                                  doluluk_ozet.json (bu betiğin dizinine)
"""
import collections, contextlib, csv, datetime as dt, io, json, math, os, sys, threading, time
import urllib.request, urllib.error

BURASI = os.path.dirname(os.path.abspath(__file__))
TD = dt.timedelta
SON_ISTEK = dt.date(2025, 12, 31)
UA = 'fdsn-availability-probe/0.1 (python-urllib)'
MAKS_ISTEK = 15000
KURAL = {'ana': (0.80, 3), 'gevsek': (0.60, 6), 'siki': (0.90, 2)}

DS = {
    'IRISDMC': 'https://service.earthscope.org/fdsnws/dataselect/1/query',
    'AUSPASS': 'https://auspass.edu.au/fdsnws/dataselect/1/query',
    'BGR': 'https://eida.bgr.de/fdsnws/dataselect/1/query',
    'EPOSFR': 'https://seisdata.epos-france.fr/fdsnws/dataselect/1/query',
    'GEOFON': 'https://geofon.gfz.de/fdsnws/dataselect/1/query',
    'ICGC': 'https://ws.icgc.cat/fdsnws/dataselect/1/query',
    'IGN': 'http://fdsnws.sismologia.ign.es/fdsnws/dataselect/1/query',
    'INGV': 'https://webservices.ingv.it/fdsnws/dataselect/1/query',
    'IPGP': 'http://ws.ipgp.fr/fdsnws/dataselect/1/query',
    'KOERI': 'https://eida.koeri.boun.edu.tr/fdsnws/dataselect/1/query',
    'LMU': 'https://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/query',
    'NCEDC': 'https://service.ncedc.org/fdsnws/dataselect/1/query',
    'NIEP': 'https://eida-sc3.infp.ro/fdsnws/dataselect/1/query',
    'NOA': 'https://eida.gein.noa.gr/fdsnws/dataselect/1/query',
    'ORFEUS': 'https://www.orfeus-eu.org/fdsnws/dataselect/1/query',
    'SCEDC': 'https://service.scedc.caltech.edu/fdsnws/dataselect/1/query',
    'SED': 'https://eida.ethz.ch/fdsnws/dataselect/1/query',
    'UIB-NORSAR': 'https://eida.geo.uib.no/fdsnws/dataselect/1/query',
    'USPSC': 'http://seisrequest.iag.usp.br/fdsnws/dataselect/1/query',
    'GEONET': 'https://service.geonet.org.nz/fdsnws/dataselect/1/query',
    'NRCAN': 'https://earthquakescanada.nrcan.gc.ca/fdsnws/dataselect/1/query',
    'BGS': 'https://eida.bgs.ac.uk/fdsnws/dataselect/1/query',
    'KIT': 'http://ws.gpi.kit.edu/fdsnws/dataselect/1/query',
}
ARA = {'IRISDMC': 0.3, 'GEOFON': 0.3, 'ORFEUS': 0.3, 'KOERI': 2.0}


def ay_listesi(a, b):
    """[a, b] içinde 15'i kalan aylar (YYYY-MM)."""
    out = []; y, m = a.year, a.month
    while (y, m) <= (b.year, b.month):
        g = dt.date(y, m, 15)
        if a <= g <= b and g <= SON_ISTEK: out.append(f'{y:04d}-{m:02d}')
        m += 1
        if m == 13: y, m = y + 1, 1
    return out


def betik_yukle(dosya, argv, kes=None):
    """sayim_ustveri.py / tr4_sayim.py tanımlarını aynı kurallarla yükle (çıktısı yutulur)."""
    src = open(os.path.join(BURASI, dosya), encoding='utf-8').read()
    if kes: src = src.split(kes)[0]
    ns = {'__name__': 'yuklenen', '__file__': os.path.join(BURASI, dosya)}
    eski = sys.argv; sys.argv = [dosya] + list(argv)
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            exec(compile(src, dosya, 'exec'), ns)
    finally:
        sys.argv = eski
    return ns


KOSU = '\nANA = None\n'   # tanımlar + hacim_hesap; satır koşuları yüklenmez


def kanal_satirlari(ham):
    """(ag, ist) -> [(loc, cha, b, e)] (>= 10 sps BHZ/HHZ)."""
    import glob
    sat = collections.defaultdict(list)
    for f in [os.path.join(ham, 'fedcatalog_kanal.txt')] + sorted(glob.glob(os.path.join(ham, 'ek_*_kanal.txt'))) + \
             [os.path.join(ham, 'marmara_fed_kanal.txt')]:
        for l in open(f, encoding='utf-8', errors='replace'):
            if l.startswith('#') or '|' not in l: continue
            p = l.rstrip('\n').split('|')
            if len(p) < 17 or p[3] not in ('BHZ', 'HHZ'): continue
            try:
                if float(p[14]) < 10: continue
                b = dt.date.fromisoformat(p[15][:10]); e = dt.date.fromisoformat(p[16][:10]) if p[16].strip() else SON_ISTEK
            except ValueError:
                continue
            r = (p[2].strip(), p[3], b, e)
            if r not in sat[(p[0], p[1])]: sat[(p[0], p[1])].append(r)
    return sat


def kanal_sec(rows, ay):
    g = dt.date.fromisoformat(ay + '-15')
    kap = [r for r in rows if r[2] <= g <= r[3]]
    if not kap:
        kap = sorted(rows, key=lambda r: min(abs((r[2] - g).days), abs((r[3] - g).days)))[:1]
    kap.sort(key=lambda r: (r[1] != 'BHZ', r[0] not in ('', '00'), r[0]))
    return kap[0][0], kap[0][1]


# ====================================================================== aday
def aday(ham, ngl, tr2, ob):
    os.makedirs(ob, exist_ok=True)
    ns = betik_yukle('sayim_ustveri.py', [ham, ngl, tr2], KOSU)
    H6, ANAHTAR, ACIK, hav, SLA, SLO = ns['H6'], ns['ANAHTAR'], ns['ACIK'], ns['hav'], ns['SLA'], ns['SLO']
    kapsar, sakin, yil, yerler = ns['kapsar'], ns['sakin'], ns['yil'], ns['yerler']
    EV60 = [e for e in H6 if e['t'] >= dt.date(2000, 1, 1) and e['z'] <= 30.0 and e['t'] <= ns['T_SON_ANA']]
    ciftler = []      # (olay, taban, rol, istasyon idx, a, b, uzaklık)
    for taban in (3, 5):
        ns['TABAN_YIL'], ns['ONCE_TEMIZ'] = taban, taban + 2
        for e in EV60:
            T = e['t']; a, b = T - yil(taban), T - TD(days=1)
            d = hav(e['la'], e['lo'], SLA, SLO)
            yakin = [i for i in range(len(ANAHTAR)) if d[i] <= 100.0 and ACIK[i]]
            st = [i for i in yakin if kapsar(ANAHTAR[i], a, b)]
            if not st: continue
            if not sakin(e['la'], e['lo'], T - yil(taban + 2), T, haric={e['id']}): continue
            if len(ns['kontrol_sec'](e, 100.0, 1)) < ns['KONTROL_MIN']: continue
            for i in st: ciftler.append((e['id'], taban, 'olay', i, a, b, float(d[i])))
            ap = T - yil(2 * taban)
            if sakin(e['la'], e['lo'], T - yil(taban + taban + 2), T, haric={e['id']}):
                for i in yakin:
                    if kapsar(ANAHTAR[i], ap, b): ciftler.append((e['id'], taban, 'plasebo', i, ap, b, float(d[i])))
    def istek_kur(cf):
        ist = collections.defaultdict(set)
        for _, _, _, i, a, b, _ in cf: ist[i].update(ay_listesi(a, b))
        return ist
    ist = istek_kur(ciftler); n = sum(len(v) for v in ist.values()); sinir = None
    print(f'TR-5 aday çift {len(ciftler)}, istasyon {len(ist)}, istek {n}')
    if n > MAKS_ISTEK:
        sinir = 'olay başına en yakın 3 yer'
        kes = []
        for key in sorted({(c[0], c[1], c[2]) for c in ciftler}):
            g = [c for c in ciftler if (c[0], c[1], c[2]) == key]
            sec = sorted(yerler([c[3] for c in g]), key=lambda i: [c[6] for c in g if c[3] == i][0])[:3]
            kes += [c for c in g if c[3] in sec]
        ciftler = kes; ist = istek_kur(ciftler); n = sum(len(v) for v in ist.values())
        print(f'  sınırlandı ({sinir}): çift {len(ciftler)}, istasyon {len(ist)}, istek {n}')
    kanal = kanal_satirlari(ham)
    istekler = []
    for i, aylar in sorted(ist.items()):
        k = ANAHTAR[i]; mk = ns['merkez_of'][k]
        for ay in sorted(aylar):
            loc, cha = kanal_sec(kanal[k], ay)
            istekler.append(dict(is_='tr5', ag=k[0], ist=k[1], loc=loc, cha=cha, merkez=mk, ay=ay))
    # TR-4: 24 KO istasyonu (tr4_sayim.py ana kural), 2012-01 ... 2023-12
    ns4 = betik_yukle('tr4_sayim.py', [ham, ngl, tr2])
    ko = sorted(k for k in ns4['ist_T'] if k.startswith('KO.'))
    print(f'TR-4 KO istasyonu {len(ko)}')
    var = {(r['ag'], r['ist'], r['ay']) for r in istekler}
    tr4 = []
    for k in ko:
        ag, s = k.split('.')
        for ay in ay_listesi(dt.date(2012, 1, 1), dt.date(2023, 12, 31)):
            loc, cha = kanal_sec(kanal[(ag, s)], ay)
            r = dict(is_='tr4', ag=ag, ist=s, loc=loc, cha=cha, merkez='KOERI', ay=ay)
            tr4.append(r)
    istekler += [r for r in tr4 if (r['ag'], r['ist'], r['ay']) not in var]
    print(f'TR-4 istek {len(tr4)} (TR-5 ile ortak olanlar bir kez atılır); toplam benzersiz istek {len(istekler)}')
    json.dump(dict(istekler=istekler, sinir=sinir, tr4_istasyon=ko,
                   ciftler=[[c[0], c[1], c[2], ANAHTAR[c[3]][0], ANAHTAR[c[3]][1], str(c[4]), str(c[5]), round(c[6], 1)]
                            for c in ciftler]),
              open(os.path.join(ob, 'istekler.json'), 'w'), ensure_ascii=False)
    print(collections.Counter(r['merkez'] for r in istekler).most_common())


# ====================================================================== yokla
def anahtar(r): return f"{r['ag']}.{r['ist']}.{r['ay']}"


def yokla(ob, sure=None):
    L = json.load(open(os.path.join(ob, 'istekler.json')))['istekler']
    oyol = os.path.join(ob, 'onbellek.jsonl')
    yapilan = set()
    if os.path.exists(oyol):
        for l in open(oyol):
            try: yapilan.add(json.loads(l)['k'])
            except Exception: pass
    kuyruk = collections.defaultdict(list)
    for r in L:
        if anahtar(r) not in yapilan: kuyruk[r['merkez']].append(r)
    print(f'kalan {sum(len(v) for v in kuyruk.values())} / {len(L)}', {m: len(v) for m, v in kuyruk.items()}, flush=True)
    kilit = threading.Lock(); f = open(oyol, 'a'); bitis = time.time() + sure if sure else None

    def akis(mk, rs):
        ara = ARA.get(mk, 0.5); son = 0.0
        for r in rs:
            if bitis and time.time() > bitis: return
            q = (f"?net={r['ag']}&sta={r['ist']}&loc=*&cha=BHZ,HHZ"
                 f"&start={r['ay']}-15T12:00:00&end={r['ay']}-15T12:01:00")
            url = DS[mk] + q
            for deneme in range(3):
                bekle = ara - (time.time() - son)
                if bekle > 0: time.sleep(bekle)
                t0 = time.time(); son = t0; kod, n = None, 0
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': UA})
                    with urllib.request.urlopen(req, timeout=120) as y:
                        kod = y.status; n = len(y.read())
                except urllib.error.HTTPError as e:
                    kod = e.code; ra = e.headers.get('Retry-After') if e.headers else None
                    if kod in (429, 503) and deneme < 2:
                        try: w = min(float(ra), 120.0)
                        except Exception: w = 30.0 * (deneme + 1)
                        time.sleep(w); continue
                except Exception as e:
                    kod = type(e).__name__
                    if deneme < 2: time.sleep(10.0 * (deneme + 1)); continue
                break
            with kilit:
                f.write(json.dumps(dict(k=anahtar(r), m=mk, kod=kod, bayt=n, sn=round(time.time() - t0, 2),
                                        deneme=deneme)) + '\n'); f.flush()
    th = [threading.Thread(target=akis, args=(m, v), daemon=True) for m, v in kuyruk.items()]
    for t in th: t.start()
    while any(t.is_alive() for t in th):
        time.sleep(60)
        n = sum(1 for _ in open(oyol))
        print(time.strftime('%H:%M:%S'), f'önbellek {n} / {len(L)}', [t.name for t in th if t.is_alive()].__len__(),
              'akış sürüyor', flush=True)
    f.close()


# ====================================================================== say
def oku_onbellek(ob):
    d = {}
    for l in open(os.path.join(ob, 'onbellek.jsonl')):
        r = json.loads(l); d[r['k']] = r
    return d


def ay_durum(r):
    if r is None: return 'yok_istek'
    if r['kod'] == 200 and r['bayt'] > 0: return 'var'
    if r['kod'] in (204, 404) or (r['kod'] == 200 and r['bayt'] == 0): return 'bos'
    if r['kod'] in (401, 403): return 'kisitli'
    return 'hata'


def degerlendir(durumlar):
    n = len(durumlar); v = sum(1 for s in durumlar if s == 'var')
    en, cur = 0, 0
    for s in durumlar:
        cur = 0 if s == 'var' else cur + 1; en = max(en, cur)
    out = dict(ay_n=n, ay_var=v, oran=round(v / n, 3) if n else 0.0, en_uzun_bosluk=en,
               bos=durumlar.count('bos'), kisitli=durumlar.count('kisitli'), hata=durumlar.count('hata'),
               yoklanmadi=durumlar.count('yok_istek'))
    for ad, (o, g) in KURAL.items():
        out['dolu_' + ad] = bool(n and v / n >= o and en <= g)
    return out


def merkez_hacim(ns, gecen, taban):
    """hacim_hesap ile aynı birleşim; merkez başına GB (3 bileşen, tam gün)."""
    pen = collections.defaultdict(list)
    for g in gecen:
        if not g.get('kgecer'): continue
        T = g['e']['t']; a = T - ns['yil'](taban)
        for k in g['st']: pen[k].append((a, T))
        for _, st in g['kontrol']:
            for i in st: pen[ns['ANAHTAR'][i]].append((a, T))
    out = collections.Counter()
    for k, iv in pen.items():
        m = []
        for b_, e_ in sorted(iv):
            if m and b_ <= m[-1][1]: m[-1][1] = max(m[-1][1], e_)
            else: m.append([b_, e_])
        n = sum((e_ - b_).days for b_, e_ in m)
        out[ns['merkez_of'][k]] += n * 86400 * ns['oran_min'][k] * ns['B_ORNEK'] * 3 / 1e9
    return {m: round(v, 1) for m, v in out.most_common()}


def say(ham, ngl, tr2, ob):
    IST = json.load(open(os.path.join(ob, 'istekler.json')))
    kayit = oku_onbellek(ob)
    idx = {}
    for r in IST['istekler']: idx[(r['ag'], r['ist'], r['ay'])] = anahtar(r)
    def durumlar(ag, s, a, b):
        return [ay_durum(kayit.get(idx.get((ag, s, ay)))) for ay in ay_listesi(a, b)]
    ozet = dict(tarih='2026-11-12', sinir=IST['sinir'], kural=KURAL)
    # --- istek/kod dağılımı
    kd = collections.defaultdict(collections.Counter); sn = collections.defaultdict(list)
    for r in IST['istekler']:
        x = kayit.get(anahtar(r))
        kd[r['merkez']][str(x['kod']) if x else 'atılmadı'] += 1
        if x: sn[r['merkez']].append(x['sn'])
    ozet['istek'] = dict(toplam=len(IST['istekler']), atilan=sum(1 for r in IST['istekler'] if anahtar(r) in kayit),
                         merkez={m: dict(c) for m, c in sorted(kd.items())},
                         medyan_sn={m: round(sorted(v)[len(v) // 2], 2) for m, v in sn.items() if v})
    # --- TR-5 çift tablosu
    yaz = []; dolu = {a: {} for a in KURAL}
    for oid, taban, rol, ag, s, a, b, d in IST['ciftler']:
        a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
        ds = durumlar(ag, s, a, b); ev = degerlendir(ds)
        yaz.append(dict(olay=oid, taban=taban, rol=rol, ag=ag, ist=s, uzaklik_km=d, bas=str(a), son=str(b), **ev))
        for ad in KURAL: dolu[ad][(ag, s, a, b)] = ev['dolu_' + ad]
    with open(os.path.join(BURASI, 'tr5_doluluk.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(yaz[0])); w.writeheader(); w.writerows(yaz)
    ozet['tr5_cift'] = dict(n=len(yaz), **{f'dolu_{ad}': sum(1 for r in yaz if r['dolu_' + ad]) for ad in KURAL},
                            tam_kapsanan=sum(1 for r in yaz if r['yoklanmadi'] == 0))
    # --- TR-5 yeniden sayım (sayim_ustveri.py kuralları, olay/plasebo istasyonlarına doluluk süzgeci)
    ns = betik_yukle('sayim_ustveri.py', [ham, ngl, tr2], KOSU)
    EV60 = [e for e in ns['H6'] if e['t'] >= dt.date(2000, 1, 1) and e['z'] <= 30.0]
    ozg_uygun, ozg_kontrol = ns['uygun'], ns['kontrol_sec']
    durum = dict(suzgec=None, kontrol=False)
    def kontrol_sec(e, R, n_min):
        durum['kontrol'] = True
        try: return ozg_kontrol(e, R, n_min)
        finally: durum['kontrol'] = False
    def uygun(la, lo, R, a, b, acik_sart=True):
        if durum['suzgec'] is None or durum['kontrol']: return ozg_uygun(la, lo, R, a, b, acik_sart)
        key = (la, lo, R)
        if key not in ns['_yakin']:
            d = ns['hav'](la, lo, ns['SLA'], ns['SLO']); ns['_yakin'][key] = ns['np'].nonzero(d <= R)[0]; ns['_uzak'][key] = d
        D = dolu[durum['suzgec']]
        idx_ = [i for i in ns['_yakin'][key] if (ns['ACIK'][i] or not acik_sart) and ns['kapsar'](ns['ANAHTAR'][i], a, b)
                and D.get((ns['ANAHTAR'][i][0], ns['ANAHTAR'][i][1], a, b), False)]
        y = sorted(ns['yerler'](idx_), key=lambda i: (ns['_uzak'][key][i], ns['ANAHTAR'][i]))
        return y[:ns['N_MAX']], None
    ns['uygun'], ns['kontrol_sec'] = uygun, kontrol_sec
    tablo = []
    for suz in (None, 'ana', 'gevsek', 'siki'):
        durum['suzgec'] = suz
        for taban in (5, 3):
            for n in (1, 2):
                ns['TABAN_YIL'], ns['ONCE_TEMIZ'] = taban, taban + 2
                sat, gecen = ns['olay_say'](EV60, 100.0, n)
                kg = [g for g in gecen if g.get('kgecer')]
                K, _ = ns['kumele'](kg)
                pl = ns['plasebo_say'](kg, 100.0, n)
                Kp = ns['kumele'](pl)[0] if pl else 0
                ss = sum(1 for g in kg if ns['mek'].get(g['e']['id']) == 'SS')
                hac = ns['hacim_hesap'](gecen, taban)
                mk_gb = merkez_hacim(ns, gecen, taban)
                tablo.append(dict(suzgec=suz or 'üstveri', taban=taban, n_min=n, istasyonlu=sat['istasyonlu'],
                                  temiz=sat['temiz'], kontrollu=sat['kontrollu'], K=K, plasebo_olay=len(pl),
                                  K_plasebo=Kp, SS=ss, G1=K >= 20, G2=Kp >= 10, hacim_3b_tamgun_GB=hac['hacim_GB'],
                                  istasyon_gunu=hac['istasyon_gunu'], olay_istasyon_gunu=hac['olay_istasyon_gunu'],
                                  n_istasyon=hac['n_istasyon'], merkez_hacim_3b_tamgun_GB=mk_gb,
                                  olaylar=sorted({g['e']['id'] for g in kg})))
                ns['TABAN_YIL'], ns['ONCE_TEMIZ'] = 5, 7
                print(f"{suz or 'üstveri':8s} t{taban} n>={n} istasyonlu {sat['istasyonlu']:3d} temiz {sat['temiz']:3d} "
                      f"kontrollü {sat['kontrollu']:3d} K {K:3d} plasebo {len(pl):3d} (K {Kp:3d}) SS {ss} "
                      f"hacim {hac['hacim_GB']} GB", flush=True)
    ozet['tr5_sayim'] = tablo
    # --- TR-4
    ns4 = betik_yukle('tr4_sayim.py', [ham, ngl, tr2])
    y4 = []
    ko = IST['tr4_istasyon']
    for k in ko:
        ag, s = k.split('.')
        for Ty in ns4['ist_T'][k]:
            T = dt.date(Ty, 1, 1); a, b = T - ns4['yil'](5), T - TD(days=1)
            ds = durumlar(ag, s, a, b)
            ds_kap = [x for x, ay in zip(ds, ay_listesi(a, b)) if ay >= '2012-01']
            ev = degerlendir(ds_kap)
            son_yil = degerlendir(ds[-12:])
            y4.append(dict(ist=k, T=Ty, bas=str(a), son=str(b), tam_kapsam=ay_listesi(a, b)[0] >= '2012-01',
                           son_yil_oran=son_yil['oran'], **ev))
    with open(os.path.join(BURASI, 'tr4_doluluk.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(y4[0])); w.writeheader(); w.writerows(y4)
    tr4 = {}
    for ad in KURAL:
        ep = {}
        for Ty in range(2012, 2024):
            rs = [r for r in y4 if r['T'] == Ty and r['tam_kapsam']]
            ep[Ty] = sum(1 for r in rs if r['dolu_' + ad]) if rs else None
        ist_dolu = sorted({r['ist'] for r in y4 if r['tam_kapsam'] and r['dolu_' + ad]})
        # örtüşmeyen epok çiftleri (>= 5 yıl arayla) içinde ikisinde de >= 10 dolu istasyon
        iyi = [T for T, v in ep.items() if v is not None and v >= 10]
        cift = [(x, y) for x in iyi for y in iyi if y - x >= 5]
        tr4[ad] = dict(epok_dolu=ep, dolu_istasyon=len(ist_dolu), istasyonlar=ist_dolu, ortusmeyen_iyi_epok=cift,
                       kapi=bool(cift))
    ay_ist = {}
    for k in ko:
        ag, s = k.split('.')
        ds = durumlar(ag, s, dt.date(2012, 1, 1), dt.date(2023, 12, 31))
        ay_ist[k] = round(sum(1 for x in ds if x == 'var') / len(ds), 3)
    yil_oran = {}
    for y in range(2012, 2024):
        ds = [x for k in ko for x in durumlar(*k.split('.'), dt.date(y, 1, 1), dt.date(y, 12, 31))]
        yil_oran[y] = round(sum(1 for x in ds if x == 'var') / len(ds), 3)
    ozet['tr4'] = dict(kural=tr4, istasyon_ay_orani=ay_ist, yil_ay_orani=yil_oran,
                       not_='T < 2017 pencereleri 2012 öncesine taştığı için yoklama kapsamı dışında (tam_kapsam=False)')
    json.dump(ozet, open(os.path.join(BURASI, 'doluluk_ozet.json'), 'w'), indent=1, ensure_ascii=False, default=str)
    for ad in KURAL: print('TR-4', ad, tr4[ad]['epok_dolu'], 'dolu istasyon', tr4[ad]['dolu_istasyon'], 'kapı', tr4[ad]['kapi'])
    print(json.dumps(ozet['istek'], ensure_ascii=False))


if __name__ == '__main__':
    k = sys.argv[1]
    if k == 'aday': aday(*sys.argv[2:6])
    elif k == 'yokla': yokla(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else None)
    elif k == 'say': say(*sys.argv[2:6])
