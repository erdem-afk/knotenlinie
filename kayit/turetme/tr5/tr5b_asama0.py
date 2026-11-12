#!/usr/bin/env python3
"""TR-5b AŞAMA 0: sunucu kiralanmadan, dalga formu okunmadan doluluk ve üstveri sayımı; kapı G0.

Ön kayıt: `kayit/onkayit/TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 2, §5.1. Örnek alınan betik `doluluk_yokla.py`
(değiştirilmedi). Bu betik HİÇBİR dalga formunu açmaz ya da saklamaz: dataselect isteklerinden yalnız HTTP kodu ve
bayt sayısı kaydedilir; istasyon servisinden yalnız `level=channel` metin üstverisi alınır.

Adımlar (önceden sabit):
  1. ustveri  Listedeki bütün istasyonlar (olay, plasebo, kontrol adayı 1-10, plasebo kontrol adayı 1-10) için
              merkezin fdsnws-station servisinden `level=channel&format=text&channel=BH?,HH?` (istasyon başına bir istek).
  2. kur      Her istasyon-penceresi için kanal seçimi (§3.1, K4): pencereyi (olayda [T-1095, T+30], ötekilerde
              [a, T-8]) üç bileşenle (Z + N/E ya da 1/2; 30 günden kısa epok boşlukları birleştirilerek) tümüyle
              kapsayan (bant, konum) çiftleri arasından önce bant (BH, sonra HH; >= 10 sps), sonra konum kodu sırası
              '', '00', '10', sonra alfabetik. Seçilen üç kanala aygıt kuralı (§2.5; olayda [T-1095, T+30], yalnız
              (T-8, T+30] içinde bozan istasyon PK'den düşer). Sonra yoklama istekleri kurulur:
              (a) Z ay yoklaması: penceredeki her ayın 15'i 12:00:00-12:01:00 UTC, seçilen konum kodu ve Z kanalı;
              (b) yatay yoklama: A, B, C dilimlerinin orta günlerinin ayında (15'i, 12:00-12:01), iki yatay kanal ayrı.
  3. yokla    İstekleri atar; önbellekli ve yeniden başlatılabilir (`sure_sn` ile kendini durdurur).
  4. say      Doluluk, istasyon kotası (dinamik), K0, K_p0, kapı G0, pilot P1 istasyonları -> asama0_sonuc.json.

Kurallar (ön kayıt §5.1): ay "var": HTTP 200 ve bayt > 0; 204/404 ya da 200+0 bayt: yok; 401/403: kısıtlı (yok sayılır,
atlatılmaz); öteki: hata (yok sayılır, ayrıca sayılır). Z ay doluluğu `dolu_ana`: ayların >= %80'i var VE en uzun
ardışık boş ay <= 3. İstasyon-penceresi dolu: kanal seçildi, aygıt kuralı geçti, Z `dolu_ana` ve altı yatay isteğin
hepsi "var". Kontrol dolu: >= 1 dolu istasyonu var. İstasyon kotası (Ö4): olaylar (T, kimlik) sırasıyla işlenir; her
olay için aday sırasıyla dolu olan ve hiçbir istasyonu başka 3 kümede KULLANILMIŞ olmayan ilk 5 aday atanır; atanan
adayların istasyonları kotaya yazılır. Olay geçer: >= 1 dolu istasyon ve >= 4 atanmış kontrol. K0: geçen olayı olan
volkaniksiz küme sayısı. K_p0: K0 kümelerinden, aynı olayın plasebo tarafı da geçen (>= 1 dolu plasebo istasyonu ve
>= 4 atanmış plasebo kontrolü) kümelerin sayısı. G0: K0 < 20 ya da K_p0 < 10 ise "güç yok (aşama 0)".

Nezaket (TR-5 Ek 1 ile aynı): merkez başına tek akış; EarthScope/GEOFON/ORFEUS istekler arası >= 0,3 sn, KOERI >= 2 sn,
öteki merkezler >= 0,5 sn; 429/503'te Retry-After (en çok 120 sn) ya da 30/60 sn bekle, en çok 2 yeniden deneme; genel
User-Agent; TLS doğrulaması açık. Bütün istek zamanları <= 2023-12-31 (assert).

Ağ kullanan kipler yalnız `--ag-onay` bayrağıyla çalışır; bayraksız çağrı hiçbir istek atmadan durur.

Kullanım (python3 -I -B):
  tr5b_asama0.py kuru    <liste.json> <ham> [ozet.json]     ağsız: istek sayısı ve süre tahmini (Z üstverisiyle;
                                                            konum kodu vekili); çıktı tr5b_asama0_kuru.json
  tr5b_asama0.py ustveri <liste.json> <ob> [sure_sn] --ag-onay
  tr5b_asama0.py kur     <liste.json> <ob>
  tr5b_asama0.py yokla   <ob> [sure_sn] --ag-onay
  tr5b_asama0.py say     <liste.json> <ob>
"""
import collections, datetime as dt, hashlib, json, math, os, re, sys, threading, time
import urllib.request, urllib.error, urllib.parse

BURASI = os.path.dirname(os.path.abspath(__file__))
TD = dt.timedelta
SON_ISTEK = dt.date(2023, 12, 31)
UA = 'fdsn-availability-probe/0.1 (python-urllib)'
N_KONTROL, KONTROL_MIN, KOTA = 5, 4, 3
KAPI_K, KAPI_KP = 20, 10
DOLU_ORAN, DOLU_BOSLUK = 0.80, 3
BOSLUK_GUN = 30
LISTE_SHA = None   # sürüm 2 dondurulunca: tr5b_liste_s2.json sha256 (ön kayıt §2.8); None ise yalnız yazdırılır

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
ST = {m: u.replace('/dataselect/1/', '/station/1/') for m, u in DS.items()}
ARA = {'IRISDMC': 0.3, 'GEOFON': 0.3, 'ORFEUS': 0.3, 'KOERI': 2.0}
ARA_VARSAYILAN = 0.5


def D(x): return dt.date.fromisoformat(x) if isinstance(x, str) else x


def ay_listesi(a, b):
    out = []; y, m = a.year, a.month
    while (y, m) <= (b.year, b.month):
        g = dt.date(y, m, 15)
        if a <= g <= b: out.append(f'{y:04d}-{m:02d}')
        m += 1
        if m == 13: y, m = y + 1, 1
    return out


def orta_ay(a, b):
    g = a + (b - a) / 2
    return f'{g.year:04d}-{g.month:02d}'


# ====================================================================== listedeki istasyon-pencereleri
def pencereler(L):
    """Dönen: [dict(rol, olay, kume, sira, ist, merkez, a, b, b_ayg, T)]. a-b: Z yoklama ve dilim penceresi
    ([T-1095, T-8] ya da plasebo karşılığı); b_ayg: kanal kapsamı ve aygıt kuralının bitişi (olayda T+30)."""
    out = []
    for r in L['olaylar']:
        T = D(r['t']); a, b = D(r['pencere'][0]), D(r['pencere'][1])
        for s in r['istasyon']:
            out.append(dict(rol='olay', olay=r['id'], kume=r['kume'], sira=0, ist=s['ist'], merkez=s['merkez'], a=a, b=b,
                            b_ayg=T + TD(days=30), T=T))
        for c in r['kontrol']:
            for s in c['istasyon']:
                out.append(dict(rol='kontrol', olay=r['id'], kume=r['kume'], sira=c['sira'], merkez_id=c['merkez_id'],
                                ist=s['ist'], merkez=s['merkez'], a=a, b=b, b_ayg=b, T=T))
        p = r.get('plasebo')
        if p:
            Tp = D(p['T']); a, b = D(p['pencere'][0]), D(p['pencere'][1])
            for s in p['istasyon']:
                out.append(dict(rol='plasebo', olay=r['id'], kume=r['kume'], sira=0, ist=s['ist'], merkez=s['merkez'],
                                a=a, b=b, b_ayg=b, T=Tp))
            for c in p['kontrol']:
                for s in c['istasyon']:
                    out.append(dict(rol='plasebo_kontrol', olay=r['id'], kume=r['kume'], sira=c['sira'],
                                    merkez_id=c['merkez_id'], ist=s['ist'], merkez=s['merkez'], a=a, b=b, b_ayg=b, T=Tp))
    for w in out: assert w['b_ayg'] <= SON_ISTEK
    return out


def pkey(w): return f"{w['ist']}|{w['a']}|{w['b_ayg']}"


# ====================================================================== istasyon kotası ve K0 (dinamik; Ö4)
def kota_ata(olaylar, ist_dolu, rol_kontrol='kontrol'):
    """olaylar: liste kayıtları; ist_dolu(rol, olay_kaydı, istasyon_kaydı) -> bool.
    (T, kimlik) sırasıyla; aday sırasıyla dolu ve kotası uygun ilk N_KONTROL aday atanır. Kota yalnız ATANAN
    adayların istasyonlarına yazılır (koşuda kullanılan; yedekler dahil). Dönen: olay kimliği -> atanan aday sıraları."""
    kota = collections.defaultdict(set); atanan = {}
    for r in sorted(olaylar, key=lambda r: (r['t'], r['id'])):
        if rol_kontrol == 'kontrol': adaylar = r['kontrol']
        else: adaylar = r['plasebo']['kontrol'] if r.get('plasebo') else []
        sec = []
        for c in adaylar:
            dl = [s['ist'] for s in c['istasyon'] if ist_dolu(rol_kontrol, r, s)]
            if not dl: continue
            if any(r['kume'] not in kota[x] and len(kota[x]) >= KOTA for x in dl): continue
            sec.append(c['sira'])
            for x in dl: kota[x].add(r['kume'])
            if len(sec) >= N_KONTROL: break
        atanan[r['id']] = sec
    return atanan


def K_say(L, ist_dolu):
    """ist_dolu(rol, olay, istasyon) -> bool. Dönen: K0, K_p0, olay ayrıntısı."""
    ol = L['olaylar']
    at_k = kota_ata(ol, ist_dolu, 'kontrol'); at_p = kota_ata(ol, ist_dolu, 'plasebo_kontrol')
    ayr = {}
    for r in ol:
        e_ok = any(ist_dolu('olay', r, s) for s in r['istasyon']) and len(at_k[r['id']]) >= KONTROL_MIN
        p = r.get('plasebo')
        p_ok = bool(p) and any(ist_dolu('plasebo', r, s) for s in p['istasyon']) and len(at_p[r['id']]) >= KONTROL_MIN
        ayr[r['id']] = dict(kume=r['kume'], volkanik=r['volkanik'], olay=e_ok, plasebo=e_ok and p_ok,
                            kontrol=at_k[r['id']], plasebo_kontrol=at_p[r['id']])
    K0 = len({v['kume'] for v in ayr.values() if v['olay'] and not v['volkanik']})
    Kp0 = len({v['kume'] for v in ayr.values() if v['plasebo'] and not v['volkanik']})
    return K0, Kp0, ayr


# ====================================================================== kuru (ağsız)
def kanal_satirlari_ham(ham):
    """Z üstverisi (yerel): (ag, ist) -> [(loc, cha, b, e)]. Yalnız kuru kipte konum kodu vekili için."""
    import glob
    sat = collections.defaultdict(list)
    for f in [os.path.join(ham, 'fedcatalog_kanal.txt')] + sorted(glob.glob(os.path.join(ham, 'ek_*_kanal.txt'))):
        for l in open(f, encoding='utf-8', errors='replace'):
            if l.startswith('#') or '|' not in l: continue
            p = l.rstrip('\n').split('|')
            if len(p) < 17 or p[3] not in ('BHZ', 'HHZ'): continue
            try:
                if float(p[14]) < 10: continue
                b = dt.date.fromisoformat(p[15][:10]); e = dt.date.fromisoformat(p[16][:10]) if p[16].strip() else SON_ISTEK
            except ValueError:
                continue
            sat[(p[0], p[1])].append((p[2].strip(), p[3], b, e))
    return sat


def istek_kur_vekil(W, kanal_sec_fn):
    """W: istasyon-pencereleri. kanal_sec_fn(w) -> (loc, bant, (yatay1, yatay2)) ya da None.
    Dönen: (istekler, ustveri_istasyonlari, secim)."""
    ist = {}
    secim = {}
    istek = {}
    for w in W:
        ist[w['ist']] = w['merkez']
        k = pkey(w)
        if k in secim: continue
        s = kanal_sec_fn(w); secim[k] = s
        if s is None: continue
        loc, bant, (h1, h2) = s; ag, st = w['ist'].split('.')
        for ay in ay_listesi(w['a'], w['b']):
            r = dict(tur='Z', ag=ag, ist=st, loc=loc, cha=bant + 'Z', ay=ay, merkez=w['merkez'])
            istek[(ag, st, loc, r['cha'], ay)] = r
        a, b = w['a'], w['b']; T = w['T']
        dil = [(a, T - TD(days=731)), (T - TD(days=730), T - TD(days=366)), (T - TD(days=365), b)]
        for x, y in dil:
            ay = orta_ay(x, y)
            for h in (h1, h2):
                r = dict(tur='H', ag=ag, ist=st, loc=loc, cha=bant + h, ay=ay, merkez=w['merkez'])
                istek[(ag, st, loc, r['cha'], ay)] = r
    for r in istek.values(): assert dt.date.fromisoformat(r['ay'] + '-15') <= SON_ISTEK
    return list(istek.values()), ist, secim


def kuru(liste, ham, ozet_yol=None):
    L = json.load(open(liste))
    sha = hashlib.sha256(open(liste, 'rb').read()).hexdigest()
    print('liste', os.path.basename(liste), sha)
    W = pencereler(L)
    kanal = kanal_satirlari_ham(ham)
    def vekil(w):
        rows = kanal.get(tuple(w['ist'].split('.')), [])
        kap = [r for r in rows if r[2] <= w['a'] and r[3] >= w['b']] or rows
        if not kap: return ('', 'BH', ('N', 'E'))
        kap.sort(key=lambda r: (r[1] != 'BHZ', {'': 0, '00': 1, '10': 2}.get(r[0], 3), r[0]))
        return (kap[0][0], kap[0][1][:2], ('N', 'E'))
    istekler, ist, _ = istek_kur_vekil(W, vekil)
    n_pen = len({pkey(w) for w in W})
    rol = collections.Counter(w['rol'] for w in W)
    tur = collections.Counter(r['tur'] for r in istekler)
    mk = collections.Counter(r['merkez'] for r in istekler)
    mk_ust = collections.Counter(ist.values())
    # süre: merkez başına tek akış; istek başına (medyan gecikme + bekleme); üstveri isteği 2 sn varsayımı
    gec = {}
    oz = ozet_yol or os.path.join(BURASI, 'doluluk_ozet.json')
    if os.path.exists(oz): gec = json.load(open(oz)).get('istek', {}).get('medyan_sn', {})
    sure, sure_iyi = {}, {}
    for m in set(mk) | set(mk_ust):
        g = gec.get(m, 1.0); ara = ARA.get(m, ARA_VARSAYILAN)
        sure[m] = round((mk[m] * (g + ara) + mk_ust[m] * (2.0 + ara)) / 3600, 2)        # tutucu: gecikme + bekleme
        sure_iyi[m] = round((mk[m] * max(g, ara) + mk_ust[m] * max(2.0, ara)) / 3600, 2)  # betiğin gerçek akışı
    duvar = max(sure.values()); duvar_iyi = max(sure_iyi.values())
    sonuc = dict(liste_sha256=sha, istasyon_penceresi=n_pen, pencere_rol=dict(rol), ustveri_istasyon=len(ist),
                 istek_toplam=len(istekler) + len(ist), istek_Z_ay=tur['Z'], istek_yatay=tur['H'], istek_ustveri=len(ist),
                 merkez_istek={m: mk[m] + mk_ust[m] for m in sorted(set(mk) | set(mk_ust), key=lambda m: -(mk[m] + mk_ust[m]))},
                 merkez_saat_tutucu=dict(sorted(sure.items(), key=lambda x: -x[1])), duvar_saati_tutucu=duvar,
                 duvar_saati_iyimser=duvar_iyi,
                 is_2saat=math.ceil(duvar / 1.9), gecikme_kaynagi='doluluk_ozet.json medyan_sn (TR-5 Ek 1); bilinmeyen 1,0 sn')
    # kuru kipte K0 üst sınırı: bütün istasyon-pencereleri dolu sayılırsa
    K0, Kp0, _ = K_say(L, lambda rol, r, s: not s.get('aygit_degisimi_Z', False))
    sonuc['K0_ust_sinir_hepsi_dolu_Z_aygit'] = dict(K0=K0, K_p0=Kp0)
    sonuc['ag_istegi'] = 0
    json.dump(sonuc, open(os.path.join(BURASI, 'tr5b_asama0_kuru.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(sonuc, ensure_ascii=False, indent=1))
    print('AĞ İSTEĞİ ATILMADI (kuru kip). Çıktı: tr5b_asama0_kuru.json')
    return sonuc


# ====================================================================== ağ kipleri
def ag_onayi():
    if '--ag-onay' not in sys.argv:
        print('Ağ kipi --ag-onay bayrağı olmadan çalışmaz; hiçbir istek atılmadı.'); sys.exit(2)


def _getir(url, ara, son):
    """Tek istek; (kod, bayt, govde_metin|None, son_zaman)."""
    kod, n, govde = None, 0, None
    for deneme in range(3):
        bekle = ara - (time.time() - son)
        if bekle > 0: time.sleep(bekle)
        son = time.time()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=120) as y:
                kod = y.status; veri = y.read(); n = len(veri)
                return kod, n, veri, son, deneme
        except urllib.error.HTTPError as e:
            kod = e.code; ra = e.headers.get('Retry-After') if e.headers else None
            if kod in (429, 503) and deneme < 2:
                try: w = min(float(ra), 120.0)
                except Exception: w = 30.0 * (deneme + 1)
                time.sleep(w); continue
            return kod, 0, None, son, deneme
        except Exception as e:
            kod = type(e).__name__
            if deneme < 2: time.sleep(10.0 * (deneme + 1)); continue
            return kod, 0, None, son, deneme
    return kod, n, None, son, 2


def ustveri(liste, ob, sure=None):
    ag_onayi()
    L = json.load(open(liste)); W = pencereler(L)
    os.makedirs(os.path.join(ob, 'ustveri'), exist_ok=True)
    ist = {}
    for w in W:
        ist.setdefault(w['ist'], [w['a'], w['b_ayg'], w['merkez']])
        ist[w['ist']][0] = min(ist[w['ist']][0], w['a']); ist[w['ist']][1] = max(ist[w['ist']][1], w['b_ayg'])
    kuyruk = collections.defaultdict(list)
    for s, (a, b, m) in sorted(ist.items()):
        if not os.path.exists(os.path.join(ob, 'ustveri', s + '.txt')): kuyruk[m].append((s, a, b))
    print('üstveri kalan', sum(len(v) for v in kuyruk.values()), '/', len(ist), flush=True)
    bitis = time.time() + sure if sure else None
    gunluk = open(os.path.join(ob, 'ustveri_gunluk.jsonl'), 'a'); kilit = threading.Lock()
    def akis(m, rs):
        son = 0.0
        for s, a, b in rs:
            if bitis and time.time() > bitis: return
            assert b <= SON_ISTEK
            ag, st = s.split('.')
            q = urllib.parse.urlencode(dict(net=ag, sta=st, channel='BH?,HH?', level='channel', format='text',
                                            starttime=f'{a}T00:00:00', endtime=f'{b}T23:59:59'))
            kod, n, veri, son, den = _getir(ST[m] + '?' + q, ARA.get(m, ARA_VARSAYILAN), son)
            if kod in (200, 204, 404):
                with open(os.path.join(ob, 'ustveri', s + '.txt'), 'wb') as f: f.write(veri or b'')
            with kilit:
                gunluk.write(json.dumps(dict(ist=s, m=m, kod=kod, bayt=n, deneme=den)) + '\n'); gunluk.flush()
    th = [threading.Thread(target=akis, args=(m, v), daemon=True) for m, v in kuyruk.items()]
    for t in th: t.start()
    for t in th: t.join()


def kanal_epoklari(ob, s):
    """(loc, cha) -> [(b, e, sensör (S/N atılmış), azimut, eğim, sps)] (istasyon servisi metni)."""
    out = collections.defaultdict(list)
    yol = os.path.join(ob, 'ustveri', s + '.txt')
    if not os.path.exists(yol): return None
    for l in open(yol, encoding='utf-8', errors='replace'):
        if l.startswith('#') or '|' not in l: continue
        p = l.rstrip('\n').split('|')
        if len(p) < 17: continue
        try:
            sps = float(p[14]); b = dt.date.fromisoformat(p[15][:10])
            e = dt.date.fromisoformat(p[16][:10]) if p[16].strip() else SON_ISTEK
        except ValueError:
            continue
        if sps < 10: continue
        sens = re.sub(r'S/N[:#\s]*\S+', '', p[10]).strip().lower()
        out[(p[2].strip(), p[3])].append((b, e, sens, p[8].strip(), p[9].strip(), sps))
    return out


def kapsar(ep, a, b):
    iv = sorted((x[0], x[1]) for x in ep); m = []
    for x, y in iv:
        if m and (x - m[-1][1]).days <= BOSLUK_GUN: m[-1][1] = max(m[-1][1], y)
        else: m.append([x, y])
    return any(x <= a and y >= b for x, y in m)


def aygit(ep, a, b):
    L = sorted(set((x[0], x[2], x[3], x[4]) for x in ep))
    return any(a < y[0] <= b and x[1:] != y[1:] for x, y in zip(L, L[1:]))


def kanal_sec(E, w):
    """(loc, bant, (h1, h2), aygit_hukum, aygit_PK) ya da None."""
    if not E: return None
    locs = sorted({l for l, _ in E}, key=lambda l: ({'': 0, '00': 1, '10': 2}.get(l, 3), l))
    for bant in ('BH', 'HH'):
        for loc in locs:
            if (loc, bant + 'Z') not in E: continue
            for h in (('N', 'E'), ('1', '2')):
                ks = [bant + 'Z', bant + h[0], bant + h[1]]
                if all((loc, c) in E and kapsar(E[(loc, c)], w['a'], w['b_ayg']) for c in ks):
                    T = w['T']
                    if w['rol'] == 'olay':
                        hk = any(aygit(E[(loc, c)], w['a'], w['b']) for c in ks)
                        pk = any(aygit(E[(loc, c)], T - TD(days=8), w['b_ayg']) for c in ks)
                    else:
                        hk = any(aygit(E[(loc, c)], w['a'], w['b']) for c in ks); pk = False
                    return loc, bant, h, hk, pk
    return None


def kur(liste, ob):
    L = json.load(open(liste)); W = pencereler(L)
    cache = {}
    def sec(w):
        if w['ist'] not in cache: cache[w['ist']] = kanal_epoklari(ob, w['ist'])
        s = kanal_sec(cache[w['ist']], w)
        return None if s is None else s[:3]
    istekler, ist, secim = istek_kur_vekil(W, sec)
    tam = {pkey(w): (lambda s: None if s is None else dict(loc=s[0], bant=s[1], yatay=list(s[2]), aygit_hukum=s[3], aygit_PK=s[4]))
           (kanal_sec(cache.get(w['ist']), w)) for w in W}
    eksik = sorted({w['ist'] for w in W if cache.get(w['ist']) is None})
    json.dump(dict(istekler=istekler, secim=tam, ustveri_eksik=eksik), open(os.path.join(ob, 'istekler.json'), 'w'),
              ensure_ascii=False)
    print('istek', len(istekler), 'kanal seçilemeyen pencere', sum(1 for v in tam.values() if v is None),
          'üstverisi eksik istasyon', len(eksik))


def anahtar(r): return f"{r['ag']}.{r['ist']}.{r['loc']}.{r['cha']}.{r['ay']}"


def yokla(ob, sure=None):
    ag_onayi()
    L = json.load(open(os.path.join(ob, 'istekler.json')))['istekler']
    oyol = os.path.join(ob, 'onbellek.jsonl'); yapilan = set()
    if os.path.exists(oyol):
        for l in open(oyol):
            try: yapilan.add(json.loads(l)['k'])
            except Exception: pass
    kuyruk = collections.defaultdict(list)
    for r in L:
        if anahtar(r) not in yapilan: kuyruk[r['merkez']].append(r)
    print(f'kalan {sum(len(v) for v in kuyruk.values())} / {len(L)}', flush=True)
    kilit = threading.Lock(); f = open(oyol, 'a'); bitis = time.time() + sure if sure else None
    def akis(mk, rs):
        son = 0.0; ara = ARA.get(mk, ARA_VARSAYILAN)
        for r in rs:
            if bitis and time.time() > bitis: return
            assert dt.date.fromisoformat(r['ay'] + '-15') <= SON_ISTEK
            q = (f"?net={r['ag']}&sta={r['ist']}&loc={r['loc'] or '--'}&cha={r['cha']}"
                 f"&start={r['ay']}-15T12:00:00&end={r['ay']}-15T12:01:00")
            t0 = time.time()
            kod, n, _, son, den = _getir(DS[mk] + q, ara, son)   # gövde okunur, saklanmaz, çözülmez
            with kilit:
                f.write(json.dumps(dict(k=anahtar(r), m=mk, kod=kod, bayt=n, sn=round(time.time() - t0, 2), deneme=den)) + '\n')
                f.flush()
    th = [threading.Thread(target=akis, args=(m, v), daemon=True) for m, v in kuyruk.items()]
    for t in th: t.start()
    for t in th: t.join()
    f.close()


def ay_durum(x):
    if x is None: return 'yok_istek'
    if x['kod'] == 200 and x['bayt'] > 0: return 'var'
    if x['kod'] in (204, 404) or (x['kod'] == 200 and x['bayt'] == 0): return 'bos'
    if x['kod'] in (401, 403): return 'kisitli'
    return 'hata'


def say(liste, ob):
    L = json.load(open(liste)); W = pencereler(L)
    sha = hashlib.sha256(open(liste, 'rb').read()).hexdigest()
    if LISTE_SHA and sha != LISTE_SHA: sys.exit('liste sha256 uyuşmuyor; durdu')
    IST = json.load(open(os.path.join(ob, 'istekler.json')))
    kayit = {}
    for l in open(os.path.join(ob, 'onbellek.jsonl')):
        x = json.loads(l); kayit[x['k']] = x
    durum = {}
    neden = collections.Counter()
    for w in W:
        k = pkey(w)
        if k in durum: continue
        s = IST['secim'].get(k)
        if s is None: durum[k] = dict(dolu=False, pk=False, neden='uc_bilesen_yok'); neden['uc_bilesen_yok'] += 1; continue
        if s['aygit_hukum']: durum[k] = dict(dolu=False, pk=False, neden='aygit'); neden['aygit'] += 1; continue
        ag, st = w['ist'].split('.')
        ds = [ay_durum(kayit.get(f"{ag}.{st}.{s['loc']}.{s['bant']}Z.{ay}")) for ay in ay_listesi(w['a'], w['b'])]
        v = sum(1 for x in ds if x == 'var'); en = cur = 0
        for x in ds: cur = 0 if x == 'var' else cur + 1; en = max(en, cur)
        z_ok = bool(ds) and v / len(ds) >= DOLU_ORAN and en <= DOLU_BOSLUK
        T = w['T']; a, b = w['a'], w['b']
        dil = [(a, T - TD(days=731)), (T - TD(days=730), T - TD(days=366)), (T - TD(days=365), b)]
        h_ok = all(ay_durum(kayit.get(f"{ag}.{st}.{s['loc']}.{s['bant']}{h}.{orta_ay(x, y)}")) == 'var'
                   for x, y in dil for h in s['yatay'])
        ok = z_ok and h_ok
        nd = 'dolu' if ok else ('z_ay' if not z_ok else 'yatay')
        neden[nd] += 1
        durum[k] = dict(dolu=ok, pk=ok and not s['aygit_PK'], neden=nd, z_oran=round(v / len(ds), 3) if ds else 0, z_bosluk=en)
    def ist_dolu(rol, r, s):
        if rol in ('olay', 'kontrol'):
            a, b = D(r['pencere'][0]), D(r['pencere'][1]); b_ayg = D(r['t']) + TD(days=30) if rol == 'olay' else b
        else:
            a, b = D(r['plasebo']['pencere'][0]), D(r['plasebo']['pencere'][1]); b_ayg = b
        return durum[f"{s['ist']}|{a}|{b_ayg}"]['dolu']
    K0, Kp0, ayr = K_say(L, ist_dolu)
    hukum = 'güç yok (aşama 0)' if (K0 < KAPI_K or Kp0 < KAPI_KP) else 'G0 geçti'
    # P1 istasyonları: volkaniksiz olayların (T, kimlik) sırasıyla ilk 24'ü; ilk atanmış kontrolün en yakın dolu istasyonu
    p1 = []
    for r in sorted([r for r in L['olaylar'] if not r['volkanik']], key=lambda r: (r['t'], r['id'])):
        at = ayr[r['id']]['kontrol']
        if not at: continue
        c = next(c for c in r['kontrol'] if c['sira'] == at[0])
        ds = sorted([s for s in c['istasyon'] if ist_dolu('kontrol', r, s)], key=lambda s: s['uzaklik_km'])
        p1.append(dict(olay=r['id'], kontrol_sira=c['sira'], merkez_id=c['merkez_id'], ist=ds[0]['ist'], pencere=r['pencere']))
        if len(p1) >= 24: break
    out = dict(liste_sha256=sha, K0=K0, K_p0=Kp0, kapi=dict(K=KAPI_K, K_p=KAPI_KP), hukum=hukum,
               pencere_neden=dict(neden), olay=ayr, p1=p1,
               istek=dict(toplam=len(IST['istekler']), atilan=sum(1 for r in IST['istekler'] if anahtar(r) in kayit)))
    json.dump(out, open(os.path.join(ob, 'asama0_sonuc.json'), 'w'), ensure_ascii=False, indent=1, default=str)
    print(json.dumps({k: out[k] for k in ('K0', 'K_p0', 'hukum', 'pencere_neden', 'istek')}, ensure_ascii=False))


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    arg = [a for a in sys.argv[2:] if not a.startswith('--')]
    if k == 'kuru': kuru(*arg[:3])
    elif k == 'ustveri': ustveri(arg[0], arg[1], float(arg[2]) if len(arg) > 2 else None)
    elif k == 'kur': kur(arg[0], arg[1])
    elif k == 'yokla': yokla(arg[0], float(arg[1]) if len(arg) > 1 else None)
    elif k == 'say': say(arg[0], arg[1])
    else: print(__doc__)
