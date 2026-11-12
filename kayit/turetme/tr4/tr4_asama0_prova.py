#!/usr/bin/env python3
"""TR-4 aşama 0: `tr4_asama0.py`'nin AĞSIZ sürdürme provası (İNCELEME-1 İ1-E4 madde 12).

Ağ kesinlikle kullanılmaz: `urllib.request.urlopen` istisna atan bir işlevle değiştirilir; `_getir` (hafif istekler)
ve `_akit` (aşama H) sahte yanıtlayıcılarla değiştirilir; saat (`simdi`, `uyu`) sahte bir saatle değiştirilir, böylece
istekler arası 2 sn bekleme ve 2 günlük aşama H aralığı gerçek zamanda beklenmez. Sahte üstveri, gerçek
`marmara_fed_kanal.txt`'nin KO Z epoklarından (yatay bileşenler N/E kopyalarıyla) kurulur; Z ayları gerçek TR-5
önbelleğinden okunur. Geçici dizinler <kök> altında açılır ve sonunda silinir.

Sınananlar:
  P0 `--ag-onay` olmadan ağ kipi istek atmadan durur.         P1 girdi sha256 uyuşmazlığında iş durur.
  P2 körlük: 2026 bitişli istek bağlantı kurulmadan reddedilir; hüküm isteği 2023-12-24'ten sonra reddedilir.
  P3 üstveri: kesin olmayan kod ikinci çağrıda yeniden denenir; iki denemeden sonra bırakılır; tamamlanmadan `kur`
     ve `say` koşmaz.
  P4 süre sınırı: `yokla` temiz çıkar, kaldığı yerden sürer; eksikken `say` G0 vermez.
  P5 üç ardışık `yokla` çağrısı: hata satırları ikinci çağrıda yeniden denenir, üçüncüde denenmez; çift kayıt 0.
  P6 yarım satır: `yokla` ve `say` düşmez, yeni satır bozulmaz; `say` belirlenimci (aynı bayt).
  P7 aşama H: kademe A / C, ertelendi -> 2 gün kuralı -> 3 ölçüm medyanı -> "veri yok (aktarım hızı)",
     POST reddinde gün gün GET, süre sınırında temiz çıkış.
Kullanım: python3 -I -B tr4_asama0_prova.py <fed> <dol> <geçici_kök>   Çıktı: bu dizine tr4_asama0_prova.json
"""
import collections, hashlib, importlib.util, json, os, shutil, sys, tempfile, urllib.parse, urllib.request
import datetime as dt

BURASI = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('a0', os.path.join(BURASI, 'tr4_asama0.py'))
A0 = importlib.util.module_from_spec(sp); sp.loader.exec_module(A0)
FED, DOL, KOK = sys.argv[1:4]


def _yasak(*a, **k): raise RuntimeError('AĞ YASAK (prova)')
urllib.request.urlopen = _yasak
A0.urllib.request.urlopen = _yasak

SAAT = [1.8e9]                                   # sahte saat (2027 sonrası bir an; yalnız aralıklar önemli)
A0.simdi = lambda: SAAT[0]
def _uyu(s): SAAT[0] += max(0.0, s)
A0.uyu = _uyu

# ---- sahte üstveri: fed dosyasındaki KO Z epokları + N/E kopyaları
UST = collections.defaultdict(list)
for l in open(FED, encoding='utf-8', errors='replace'):
    if l.startswith('#') or '|' not in l: continue
    p = l.rstrip('\n').split('|')
    if len(p) < 17 or p[0] != 'KO': continue
    UST[p[1]].append(p)
def ustveri_govde(sta):
    sat = ['#Network | Station | Location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | '
           'SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime']
    for p in UST.get(sta, []):
        for c, az, dip in ((p[3], p[8], p[9]), (p[3][:2] + 'N', '0.0', '0.0'), (p[3][:2] + 'E', '90.0', '0.0')):
            q = list(p); q[3], q[8], q[9] = c, az, dip; sat.append('|'.join(q))
    return ('\n'.join(sat) + '\n').encode()

CAGRI = collections.Counter(); DENEME = collections.Counter(); ISTEK_URL = []
def sahte_getir(url):
    """Hafif istek yanıtlayıcısı (ağsız). (kod, bayt, gövde, retry_after)."""
    CAGRI['getir'] += 1; ISTEK_URL.append(url); SAAT[0] += 1.0
    q = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query))
    DENEME[url] += 1
    if '/station/' in url:
        if q['sta'] == 'GEMT' and DENEME[url] == 1: return 503, 0, None, 5.0
        if q['sta'] == 'NMR9': return 'ConnectionResetError', 0, None, None
        b = ustveri_govde(q['sta']); return 200, len(b), b, None
    k = f"{q['sta']}.{q['cha']}.{q['start'][:7]}"
    h = int(hashlib.sha256(k.encode()).hexdigest()[:8], 16)
    if h % 41 == 0: return 'ConnectionResetError', 0, None, None          # hep bağlantı hatası
    if h % 23 == 0 and DENEME[url] == 1: return 500, 0, None, None        # ilk denemede 500, sonra 200
    if h % 29 == 0: return 204, 0, None, None
    if h % 97 == 0: return 403, 0, None, None
    return 200, 4096, None, None
A0._getir = sahte_getir

HIZ = dict(v=600.0, post_ret=False)
def sahte_akit(url, govde, tavan_sn):
    CAGRI['akit'] += 1
    if govde is not None and HIZ['post_ret']: SAAT[0] += 0.5; return 405, 0, '0' * 64, 0.5, False
    n = 28_080_000 if govde is not None else 5_616_000
    sn = n / (HIZ['v'] * 1024); kesik = False
    if sn > tavan_sn: n = int(n * tavan_sn / sn); sn = tavan_sn; kesik = True
    SAAT[0] += sn
    return 200, n, hashlib.sha256(str(n).encode()).hexdigest(), round(sn, 3), kesik
A0._akit = sahte_akit


def cikis(f, *a):
    try: f(*a); return None
    except SystemExit as e: return str(e.code)


def satir_say(yol):
    iyi = bozuk = 0
    for l in open(yol, encoding='utf-8'):
        try: json.loads(l); iyi += 1
        except ValueError: bozuk += 1
    return iyi, bozuk


def cift(yol):
    s = A0.satirlar(yol); c = collections.Counter(x['k'] for x in s)
    kes = collections.Counter(x['k'] for x in s if x['kod'] in A0.KESIN)
    return dict(kesin_kodlu_cift=sum(1 for v in kes.values() if v > 1), ikiden_cok_deneme=sum(1 for v in c.values() if v > 2))


os.makedirs(KOK, exist_ok=True)
tmp = tempfile.mkdtemp(dir=KOK)
out = {}
try:
    AG = list(sys.argv)
    obA = os.path.join(tmp, 'A')
    # P0: bayraksız
    sys.argv = AG[:1]; n0 = CAGRI['getir']
    out['P0_bayraksiz'] = dict(cikis=cikis(A0.ustveri, FED, DOL, obA), istek=CAGRI['getir'] - n0, dizin_acildi=os.path.exists(obA))
    sys.argv = AG + ['--ag-onay']
    # P1: sha uyuşmazlığı
    bozuk = os.path.join(tmp, 'fed_bozuk.txt'); shutil.copy(FED, bozuk); open(bozuk, 'a').write('#\n')
    out['P1_sha'] = dict(cikis=cikis(A0.ustveri, bozuk, DOL, obA)[:40], istek=CAGRI['getir'] - n0)
    # P2: körlük
    ak = A0.Akis(SAAT[0] + 6000, 'yokla')
    out['P2_korluk'] = dict(
        y2026=cikis(A0.istek_at, ak, 'https://x.invalid/', dt.date(2026, 1, 15), A0.SON_ISTEK),
        hukum_2024=cikis(A0.istek_at, ak, 'https://x.invalid/', dt.date(2024, 1, 15), A0.SON_HUKUM),
        b13_2025_06=cikis(A0.istek_at, ak, 'https://x.invalid/', dt.date(2025, 6, 15), A0.SON_B13),
        istek=CAGRI['getir'] - n0)
    # P3: üstveri
    n1 = CAGRI['getir']; A0.ustveri(FED, DOL, obA); u1 = CAGRI['getir'] - n1
    kur_once = cikis(A0.kur, FED, DOL, obA); say_once = cikis(A0.say, FED, DOL, obA)
    n2 = CAGRI['getir']; A0.ustveri(FED, DOL, obA); u2 = CAGRI['getir'] - n2
    n3 = CAGRI['getir']; A0.ustveri(FED, DOL, obA); u3 = CAGRI['getir'] - n3
    kur_sonra = cikis(A0.kur, FED, DOL, obA)
    IST = json.load(open(os.path.join(obA, 'istekler.json')))
    out['P3_ustveri'] = dict(cagri_1=u1, cagri_2=u2, cagri_3=u3, kur_tamamlanmadan=kur_once, say_tamamlanmadan=say_once,
                             kur_sonra=kur_sonra, istek_sayisi=IST['sayi'], istek=len(IST['istekler']),
                             ustveri_alinamayan=IST['ustveri_alinamayan'], onizleme_farki=IST['onizleme_farki'],
                             ustveri_yeniden=cikis(A0.ustveri, FED, DOL, obA))
    obB = os.path.join(tmp, 'B'); shutil.copytree(obA, obB)
    # P4: süre sınırı (B)
    t = A0.yokla(FED, DOL, obB, 600); i1, _ = satir_say(os.path.join(obB, 'onbellek.jsonl'))
    p4_say = cikis(A0.say, FED, DOL, obB)
    t2 = A0.yokla(FED, DOL, obB)
    out['P4_sure'] = dict(ilk_cagri_atilan=t, ilk_cagri_satir=i1, say_eksikken=p4_say, ikinci_cagri_atilan=t2,
                          sonuc_yok=not os.path.exists(os.path.join(obB, 'asama0_sonuc.json')),
                          **cift(os.path.join(obB, 'onbellek.jsonl')))
    # P5 + P6: üç ardışık çağrı (A); 1. ve 2. çağrı arasında yarım satır
    oyA = os.path.join(obA, 'onbellek.jsonl')
    DENEME.clear()                                                             # A'nın yanıtlayıcısı B'den bağımsız
    a1 = A0.yokla(FED, DOL, obA)
    d, n = A0.son_durum(A0.satirlar(oyA)); hata1 = sum(1 for k, x in d.items() if x['kod'] not in A0.KESIN)
    say_hatali = cikis(A0.say, FED, DOL, obA)
    with open(oyA, 'a') as f: f.write('{"k": "KO.ADVT..HHE.20')               # yarım satır
    a2 = A0.yokla(FED, DOL, obA)
    iyi, bz = satir_say(oyA)
    d, n = A0.son_durum(A0.satirlar(oyA)); hata2 = sum(1 for k, x in d.items() if x['kod'] not in A0.KESIN)
    a3 = A0.yokla(FED, DOL, obA)
    S1 = A0.say(FED, DOL, obA); h1 = A0.sha_dosya(os.path.join(obA, 'asama0_sonuc.json'))
    S2 = A0.say(FED, DOL, obA); h2 = A0.sha_dosya(os.path.join(obA, 'asama0_sonuc.json'))
    out['P5_uc_cagri'] = dict(cagri_1_atilan=a1, cagri_1_hata=hata1, say_hata_varken=say_hatali, cagri_2_atilan=a2,
                              cagri_2_kalan_hata=hata2, cagri_3_atilan=a3, **cift(oyA),
                              yokla_say_sonrasi=cikis(A0.yokla, FED, DOL, obA))
    out['P6_yarim_satir'] = dict(gecerli_satir=iyi, bozuk_satir=bz, say_dusmedi=S1 is not None, say_iki_kez_ayni=h1 == h2,
                                 say_sha256=h1)
    out['say_ozet'] = {k: S1[k] for k in ('hukum', 'yer_T', 'dolu_yer_pencere', 'indirme', 'neden', 'istek', 'istek_durum')}
    out['say_ozet']['V_GB'] = S1['V_GB']; out['say_ozet']['bilgi13_dolu'] = S1['bilgi13']['dolu']
    out['say_ozet']['ustveri_alinamayan'] = S1['ustveri_alinamayan']
    # P7: aşama H
    def hiz_kopya(ad):
        ob = os.path.join(tmp, ad); shutil.copytree(obA, ob, ignore=shutil.ignore_patterns('hiz_*')); return ob
    H = {}
    for ad, v in (('hA', 600.0), ('hC', 100.0)):
        ob = hiz_kopya(ad); HIZ.update(v=v, post_ret=False); n0 = CAGRI['akit']
        r = A0.hiz(FED, DOL, ob); H[ad] = dict(v=r['v_medyan_KiBs'], kademe=r['kademe'], akit=CAGRI['akit'] - n0)
    ob = hiz_kopya('hY'); HIZ.update(v=60.0, post_ret=False); seri = []
    for adim in range(5):
        n0 = CAGRI['akit']; r = A0.hiz(FED, DOL, ob)
        seri.append(dict(akit=CAGRI['akit'] - n0, kademe=r['kademe'], gerekce=r['gerekce'], ek=r.get('ek_metin')))
        if adim in (1, 3): pass
        else: SAAT[0] += 2 * 86400 + 60
    H['hY_yavas_seri'] = seri
    ob = hiz_kopya('hP'); HIZ.update(v=600.0, post_ret=True); n0 = CAGRI['akit']
    r = A0.hiz(FED, DOL, ob)
    H['hP_post_ret'] = dict(kademe=r['kademe'], bicim=r['bicim'], akit=CAGRI['akit'] - n0)
    ob = hiz_kopya('hS'); HIZ.update(v=40.0, post_ret=False)
    n0 = CAGRI['akit']; r1 = A0.hiz(FED, DOL, ob, 2500); k1 = CAGRI['akit'] - n0
    n0 = CAGRI['akit']; r2 = A0.hiz(FED, DOL, ob); k2 = CAGRI['akit'] - n0
    H['hS_sure'] = dict(cagri_1_istek=k1, cagri_1_kademe=r1['kademe'], cagri_2_istek=k2, cagri_2_kademe=r2['kademe'],
                        v=r2['v_medyan_KiBs'])
    out['P7_hiz'] = H
    out['ag_cagrisi'] = 0
    out['getir_cagri'] = CAGRI['getir']; out['akit_cagri'] = CAGRI['akit']
finally:
    sys.argv = AG
    shutil.rmtree(tmp)
json.dump(out, open(os.path.join(BURASI, 'tr4_asama0_prova.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1,
          sort_keys=True, default=str)
print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
