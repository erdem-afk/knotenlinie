#!/usr/bin/env python3
"""TR-4 AŞAMA 0 ve AŞAMA H: dalga formu çözülmeden üç bileşen / yatay doluluk, kapı G0, aktarım hızı ve kademe.

Ön kayıt: `kayit/onkayit/TR-4_marmara-hiz-tabani_ONKAYIT.md` sürüm 2, §5.1-5.3 ve §5.6; şartlar İNCELEME-1 İ1-E4
(14 madde). `kayit/turetme/tr5/tr5b_asama0.py`'nin düzeltilmiş hâlinden (sürüm 3) türetildi: `ay_listesi`, `orta_ay`,
`kapsar`, `aygit`, `kanal_sec`, `kanal_epoklari`, `satirlar`, `son_durum`, `ekle_ac`, `ay_durum` aynıdır.
Bu betik HİÇBİR dalga formunu açmaz, çözmez ya da saklamaz: dataselect yanıtlarından yalnız HTTP kodu, bayt sayısı
(aşama H'de ayrıca süre ve sha256) yazılır; istasyon servisinden yalnız `level=channel` metin üstverisi alınır.

Kipler (her kipte dört girdinin sha256'sı denetlenir; uyuşmazlıkta iş durur; İ1-E4 madde 1):
  kuru    <fed> <dol>                    ağsız. §5.1 tablosunu (26 / 468 / 84 / 15 / 30 / 8) yeniden üretir, sapmada
                                         durur; aşama H seçimini yazdırır. Çıktı: bu dizine tr4_asama0_kuru.json.
  ustveri <fed> <dol> <ob> [sure_sn] --ag-onay   26 istasyonun kanal üstverisi (KOERI istasyon servisi).
  kur     <fed> <dol> <ob> --ag-onay              ağ isteği atmaz; kanal seçimi, aygıt kuralı, istek listesi
                                                  (istekler.json). Üstveri tamamlanmadan koşmaz.
  yokla   <fed> <dol> <ob> [sure_sn] --ag-onay   istek listesindeki kısa dataselect yoklamaları (onbellek.jsonl).
  say     <fed> <dol> <ob>                       ağsız. Her istek ve üstveri isteği tamamlanmadıkça hiçbir sayı ve
                                                  hüküm vermez. Çıktı: <ob>/asama0_sonuc.json.
  hiz     <fed> <dol> <ob> [sure_sn] --ag-onay   aşama H (§5.2): 8 üretim biçiminde istek; kademe kararı (§5.3).
                                                  Çıktı: <ob>/hiz_gunluk.jsonl, <ob>/hiz_sonuc.json.
<fed>: marmara_fed_kanal.txt; <dol>: TR-5 doluluk önbelleği onbellek.jsonl (ikisi de
/mnt/project-files/turetme/tr5b-ham/tr5_ham_ustveri_2026-11-12.tar.gz arşivinden, ham/ ve doluluk/).
<ob>: aşama 0 önbellek ve istek günlüğü dizini (ustveri/, ustveri_gunluk.jsonl, istekler.json, onbellek.jsonl,
asama0_sonuc.json, hiz_gunluk.jsonl, hiz_sonuc.json). sure_sn en çok 6000 (varsayılan 6000).

Kurallar (özet; ayrıntı ön kayıt §5.1-5.3):
  - Aday kümesi yalnız tr4_pencereler.csv'den: ana_T ∧ (DOLU_ana ∨ aday_yoklanmamis), temsilci kuralı (ISK yerinde
    yalnız KO.ISK) -> 105 istasyon-penceresi. Temsilci aşama 0'dan sonra yeniden seçilmez.
  - Z durumu: 2012-2023 TR-5 önbelleğinden (KO.<ist>.<YYYY-MM>; loc=*, BHZ,HHZ), üç aday ve SLVT (bilgi satırı 13)
    için yeni yoklama. KO kanal epoklarının hepsinde konum kodu boştur (assert).
  - Kanal seçimi ve aygıt kuralı TR-5b §3.1 (`kanal_sec`): üç bileşen kapsama, BH sonra HH, konum sırası, N/E sonra
    1/2, 30 günlük boşluk birleştirme; aygıt kuralı üç bileşende [a, b].
  - Yoklama: ayın 15'i 12:00-12:01 UTC; tek akış; istekler arası >= 2 sn; genel User-Agent; TLS doğrulaması açık;
    429/503'te Retry-After (en çok 120 sn) beklenir. Gövde okunur, saklanmaz, çözülmez.
  - Kesin kodlar (200, 204, 404, 401, 403); 401/403 kısıtlıdır ve aşılmaz. Öteki kodlar ve bağlantı hataları sonraki
    çağrıda bir kez yeniden denenir: her istek için en çok iki deneme (çağrı başına bir deneme).
  - Yatay kural koşullu (TR-5b İ2-E2): Z'si "var" olan dilim bilgilidir; en az bir bilgili dilim ve her bilgili
    dilimde iki yatay istek "var". Bilgili dilim yoksa neden `yatay_bilgisiz`.
  - Körlük: her isteğin bitişi <= 2025-12-31 (aşılırsa istek bağlantı kurulmadan reddedilir); hüküm
    yer-pencerelerinin yoklamaları <= 2023-12-24; bilgi satırı 13'ünkiler <= 2025-05-31.
  - Süre: kalan süre o kipteki en uzun beklenen istek süresinin iki katından azsa yeni istek başlatılmaz.
  - Tek koşu (§5.6): önbellek silinmez, yeniden yoklama yapılmaz; `kur` yoklama başladıktan sonra istek listesini
    değiştiremez; `say` farklı bir sonuçla yeniden yazılamaz.
"""
import collections, datetime as dt, hashlib, json, math, os, re, sys, time
import urllib.request, urllib.error, urllib.parse
import csv

BURASI = os.path.dirname(os.path.abspath(__file__))
TD = dt.timedelta

# ---------------------------------------------------------------- dondurulmuş sabitler
GIRDI_SHA = {   # İ1-E4 madde 1
    'tr4_pencereler.csv': '166e42ea5b2fbe97ed608daf0f533252c13ef0959d78950c9b3213998915a4ef',
    'tr4_onkayit_sayim.json': '39e91fcecb2b6c9554a7f9d79569b1b81fc20427a72ca207244a85b5151cb2ee',
    'onbellek.jsonl': 'ce4fe524392baa00ea2a8a34aa3effd895d2a7e9b14cdfca211c3b20f4b0b409',
    'marmara_fed_kanal.txt': 'dbcc3ba8ed7564058df2b59381006ee5c342e63206ca5fd4b8991e6797812de9',
}
for _k, _v in GIRDI_SHA.items():
    assert _v is not None and re.fullmatch(r'[0-9a-f]{64}', _v), _k

TABLO = dict(ustveri=26, yatay=468, z_aday=84, b13_z=15, b13_yatay=30, hiz=8)   # §5.1 istek tablosu (sürüm 2)
N_ADAY = 105                                  # 110 + 3 - 8 (KAVV)
SON_ISTEK = dt.date(2025, 12, 31)             # her isteğin bitişi
SON_HUKUM = dt.date(2023, 12, 24)             # hüküm yer-pencerelerinin yoklamaları
SON_B13 = dt.date(2025, 5, 31)                # bilgi satırı 13
B13_IST, B13_T = 'KO.SLVT', dt.date(2025, 4, 23)
B13_AY_ILK, B13_AY_SON = dt.date(2024, 3, 1), dt.date(2025, 5, 31)
TEMSILCI = {'KO.ISK': 'KO.ISK'}               # ön kayıt §2.4
ANA_YIL = list(range(2017, 2025))
KAPI_YER, KAPI_ARA_YIL = 10, 3
DOLU_ORAN, DOLU_BOSLUK = 0.80, 3
BOSLUK_GUN = 30
BILGI0_MIN_N = 30                             # §4.3: dolu yer-penceresi < 30 ise indirme yapılmaz
UA = 'fdsn-availability-probe/0.1 (python-urllib)'
DS = 'https://eida.koeri.boun.edu.tr/fdsnws/dataselect/1/query'
ST = 'https://eida.koeri.boun.edu.tr/fdsnws/station/1/query'
ARA_SN = 2.0
KESIN = (200, 204, 404, 401, 403)             # kesin yanıt kodları; ötekiler bir kez yeniden denenir
RETRY_AFTER_MAX = 120.0
SURE_MAX = 6000.0
BEKLENEN_SN = {'ustveri': 120.0, 'yokla': 120.0, 'hiz': 900.0}   # kipteki en uzun beklenen istek (zaman aşımı/tavan)
# aşama H (§5.2)
H_TOHUM_METIN = 'tr4-asamaH|20261202'
H_N, H_GUN, H_SAAT = 8, 5, 4
H_ILK, H_SON = dt.date(2014, 1, 1), dt.date(2023, 12, 31)
H_TAVAN_SN = 900.0
H_POST_RET = (400, 405, 413, 414, 415, 501)  # POST'un reddi sayılan kodlar (ilk POST isteğinde)
# kademe (§5.3)
BAYT_GUN = 4 * 3600 * 100 * 3 * 1.3           # §5.4: 4 saat, 100 sn^-1, 3 bileşen, 1,3 bayt/örnek
ESIK_A_GUN, ESIK_D_GUN = 7.0, 21.0
H_ARA_GUN, H_ERTELEME_GUN, H_OLCUM_MAX = 2.0, 5.0, 3
D_YIL = (2017, 2021)

simdi = time.time                             # prova bunları değiştirebilir (ağsız)
uyu = time.sleep


def D(x): return dt.date.fromisoformat(x) if isinstance(x, str) else x


def sha_dosya(y):
    h = hashlib.sha256()
    with open(y, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def yaz_json(yol, obj):
    """Atomik ve belirlenimci yazım: geçici ad, sort_keys, os.replace."""
    with open(yol + '.tmp', 'w', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True, default=str) + '\n')
    os.replace(yol + '.tmp', yol)


def girdi_denet(fed, dol):
    yol = {'tr4_pencereler.csv': os.path.join(BURASI, 'tr4_pencereler.csv'),
           'tr4_onkayit_sayim.json': os.path.join(BURASI, 'tr4_onkayit_sayim.json'),
           'onbellek.jsonl': dol, 'marmara_fed_kanal.txt': fed}
    out = {}
    for ad, y in yol.items():
        if not os.path.isfile(y): sys.exit(f'girdi yok: {ad} ({y}); durdu')
        s = sha_dosya(y)
        if s != GIRDI_SHA[ad]: sys.exit(f'girdi sha256 uyuşmuyor: {ad} {s}; durdu')
        out[ad] = s
    return out


def ob_denet(ob, dol):
    if os.path.abspath(os.path.join(ob, 'onbellek.jsonl')) == os.path.abspath(dol):
        sys.exit('<ob>/onbellek.jsonl, TR-5 girdi önbelleğiyle aynı dosya olamaz; durdu')
    os.makedirs(ob, exist_ok=True)


# ---------------------------------------------------------------- tr5b_asama0.py ile aynı işlevler
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
    """(loc, bant, (h1, h2), aygit_hukum, aygit_PK) ya da None. tr5b_asama0.kanal_sec'in aynısı."""
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
        assert p[2].strip() == '', f'KO kanal epokunda konum kodu boş değil: {s} {p[2]!r} {p[3]} (İ1-E4 madde 7)'
        sens = re.sub(r'S/N[:#\s]*\S+', '', p[10]).strip().lower()
        out[(p[2].strip(), p[3])].append((b, e, sens, p[8].strip(), p[9].strip(), sps))
    return out


def satirlar(yol):
    """jsonl; yarım ya da bozuk satır atlanır."""
    out = []
    if os.path.exists(yol):
        for l in open(yol, encoding='utf-8'):
            try: out.append(json.loads(l))
            except ValueError: pass
    return out


def son_durum(kayitlar):
    """anahtar -> geçerli satır (varsa kesin kodlu son satır, yoksa son satır) ve deneme sayısı."""
    d, n = {}, collections.Counter()
    for x in kayitlar:
        n[x['k']] += 1
        if x['k'] not in d or x['kod'] in KESIN or d[x['k']]['kod'] not in KESIN: d[x['k']] = x
    return d, n


def ekle_ac(yol):
    """jsonl'u ekleme kipinde açar; dosya yarım bir satırla bitiyorsa önce satır sonu yazılır, böylece yarım satır
    yalnız kendisi yok sayılır ve yeni satırı bozmaz."""
    if os.path.exists(yol) and os.path.getsize(yol) > 0:
        with open(yol, 'rb') as g:
            g.seek(-1, os.SEEK_END); yarim = g.read(1) != b'\n'
        if yarim:
            with open(yol, 'a', encoding='utf-8') as g: g.write('\n')
    return open(yol, 'a', encoding='utf-8')


def ay_durum(x):
    if x is None: return 'yok_istek'
    if x['kod'] == 200 and x['bayt'] > 0: return 'var'
    if x['kod'] in (204, 404) or (x['kod'] == 200 and x['bayt'] == 0): return 'bos'
    if x['kod'] in (401, 403): return 'kisitli'
    return 'hata'


def tamam(kayit, deneme, k):
    """İstek tamamlandı mı: kesin kodla yanıtlandı ya da iki kez denendi."""
    return k in kayit and (kayit[k]['kod'] in KESIN or deneme[k] >= 2)


# ---------------------------------------------------------------- girdiler (csv, sayım, fed, TR-5 önbelleği)
def csv_oku():
    R = list(csv.DictReader(open(os.path.join(BURASI, 'tr4_pencereler.csv'), encoding='utf-8')))
    for r in R:
        for c in ('ana_T', 'DOLU_ana', 'aday_yoklanmamis', 'aygit_Z_bozuk'):
            r[c] = r[c] == 'True'
    return R


def adaylar(R):
    """İ1-E4 madde 2: ana_T ∧ (DOLU_ana ∨ aday_yoklanmamis), temsilci kuralı. Pencere sözlükleri."""
    out = []
    for r in R:
        if not (r['ana_T'] and (r['DOLU_ana'] or r['aday_yoklanmamis'])): continue
        if r['yer'] in TEMSILCI and r['ist'] != TEMSILCI[r['yer']]: continue
        T = D(r['T']); a, b = D(r['a']), D(r['b'])
        out.append(dict(rol='ana', ist=r['ist'], yer=r['yer'], T=T, a=a, b=b, b_ayg=b, aday=r['aday_yoklanmamis'],
                        csv_kanal=r['kanal'], csv_aygit=r['aygit_Z_bozuk'], sps=float(r['sps'])))
    out.sort(key=lambda w: (w['ist'], w['T']))
    n110 = sum(1 for r in R if r['ana_T'] and r['DOLU_ana'])
    n3 = sum(1 for r in R if r['ana_T'] and r['aday_yoklanmamis'])
    nk = sum(1 for r in R if r['ana_T'] and (r['DOLU_ana'] or r['aday_yoklanmamis'])
             and r['yer'] in TEMSILCI and r['ist'] != TEMSILCI[r['yer']])
    if not (len(out) == N_ADAY == n110 + n3 - nk and (n110, n3, nk) == (110, 3, 8)):
        sys.exit(f'aday kümesi {len(out)} ({n110} + {n3} - {nk}) != {N_ADAY}; durdu')
    for w in out: assert w['b'] <= SON_HUKUM
    return out


def b13_penceresi():
    return dict(rol='bilgi13', ist=B13_IST, yer=B13_IST, T=B13_T, a=B13_T - TD(days=400), b=B13_T + TD(days=30),
                b_ayg=B13_T + TD(days=30), aday=True)


def b13_aylar():
    out = []
    for y in (2024, 2025):
        for m in range(1, 13):
            g = dt.date(y, m, 15)
            if B13_AY_ILK <= g <= B13_AY_SON: out.append(f'{y:04d}-{m:02d}')
    return out


def ustveri_istasyonlari(R):
    """26 istasyon (§5.1 tablosu; tr4_onkayit_sayim.py'nin tanımı): ana_T ∧ (DOLU_ana ∨ aday) istasyonları (KAVV
    dahil) ∪ 2025 PK istasyonları. Aralık [ilk a, son b]; PK istasyonlarında bilgi satırı 13 ayları dahil."""
    S = json.load(open(os.path.join(BURASI, 'tr4_onkayit_sayim.json'), encoding='utf-8'))
    ist = {}
    for r in R:
        if not (r['ana_T'] and (r['DOLU_ana'] or r['aday_yoklanmamis'])): continue
        a, b = D(r['a']), D(r['b'])
        x = ist.setdefault(r['ist'], [a, b]); x[0] = min(x[0], a); x[1] = max(x[1], b)
    for s in S['pk2025_istasyon']:
        x = ist.setdefault(s, [B13_AY_ILK, B13_AY_SON]); x[0] = min(x[0], B13_AY_ILK); x[1] = max(x[1], B13_AY_SON)
    for s, (a, b) in ist.items(): assert b <= SON_ISTEK, s
    return dict(sorted(ist.items()))


def fed_oku(fed):
    """KO istasyon konumları; bütün KO epoklarında konum kodu boş (İ1-E4 madde 7)."""
    kon = {}
    for l in open(fed, encoding='utf-8', errors='replace'):
        if l.startswith('#') or '|' not in l: continue
        p = l.rstrip('\n').split('|')
        if len(p) < 17 or p[0] != 'KO': continue
        assert p[2].strip() == '', f'fed: KO.{p[1]} konum kodu boş değil'
        kon['KO.' + p[1]] = (float(p[4]), float(p[5]))
    return kon


def tr5_onbellek(dol):
    """TR-5 Z ay önbelleği: 'KO.<ist>' , 'YYYY-MM' -> satır (son_durum kuralı)."""
    d, _ = son_durum([x for x in satirlar(dol) if x['k'].startswith('KO.')])
    return {tuple(k.rsplit('.', 1)): x for k, x in d.items()}


# ---------------------------------------------------------------- istek listesi
def dilimler(w):
    T, a, b = w['T'], w['a'], w['b']
    return [(a, T - TD(days=731)), (T - TD(days=730), T - TD(days=366)), (T - TD(days=365), b)]


def anahtar(r): return f"{r['ag']}.{r['ist']}.{r['loc']}.{r['cha']}.{r['ay']}"


def istek_kur(W, b13, sec_fn):
    """sec_fn(w) -> (loc, bant, (h1, h2)) ya da None. Dönen: istekler (anahtar sıralı), seçim."""
    istek, secim = {}, {}
    def ekle(r):
        k = anahtar(r)
        if k in istek: assert istek[k]['rol'] == r['rol'], k
        else: istek[k] = r
    for w in W + [b13]:
        k = f"{w['ist']}|{w['T']}"
        s = sec_fn(w); secim[k] = s
        if s is None: continue
        loc, bant, (h1, h2) = s[:3]; ag, st = w['ist'].split('.')
        if w['rol'] == 'ana':
            if w['aday']:
                for ay in ay_listesi(w['a'], w['b']):
                    ekle(dict(tur='Z', rol='ana', ag=ag, ist=st, loc=loc, cha=bant + 'Z', ay=ay))
            for x, y in dilimler(w):
                for h in (h1, h2):
                    ekle(dict(tur='H', rol='ana', ag=ag, ist=st, loc=loc, cha=bant + h, ay=orta_ay(x, y)))
        else:
            for ay in b13_aylar():
                ekle(dict(tur='Z', rol='bilgi13', ag=ag, ist=st, loc=loc, cha=bant + 'Z', ay=ay))
                for h in (h1, h2):
                    ekle(dict(tur='H', rol='bilgi13', ag=ag, ist=st, loc=loc, cha=bant + h, ay=ay))
    for r in istek.values():                                   # İ1-E4 madde 9
        g = dt.date.fromisoformat(r['ay'] + '-15')
        assert g <= SON_ISTEK
        assert g <= (SON_HUKUM if r['rol'] == 'ana' else SON_B13), anahtar(r)
    return [istek[k] for k in sorted(istek)], secim


def istek_sayilari(L):
    c = collections.Counter((r['rol'], r['tur'], 'aday' if r['tur'] == 'Z' else '') for r in L)
    return dict(yatay=c[('ana', 'H', '')], z_aday=c[('ana', 'Z', 'aday')], b13_z=c[('bilgi13', 'Z', 'aday')],
                b13_yatay=c[('bilgi13', 'H', '')])


# ---------------------------------------------------------------- hacim (§5.3, §5.4)
def hacim_V(W):
    """W: dolu pencereler [(ist, a, b, T yılı)]. İstasyon başına gün birleşimi. GB (1e9)."""
    def gb(sec, d):
        g = collections.defaultdict(set)
        for ist, a, b, y in sec:
            x = a
            while x <= b:
                if d is None or x.day <= d: g[ist].add(x)
                x += TD(days=1)
        return sum(len(v) for v in g.values()) * BAYT_GUN / 1e9
    return dict(A=gb(W, None), C=gb(W, 20), D=gb([w for w in W if D_YIL[0] <= w[3] <= D_YIL[1]], 20))


def kapi(sayi):
    iyi = sorted(y for y, n in sayi.items() if n >= KAPI_YER)
    ciftler = [[x, y] for i, x in enumerate(iyi) for y in iyi[i + 1:] if y - x >= KAPI_ARA_YIL]
    return dict(iyi_epok=iyi, ortusmeyen_cift=ciftler, gecti=bool(ciftler))


def ana_ornek(R):
    """Ön kayıt §2.5 ana örneklemi (102 yer-penceresi): ana_T ∧ DOLU_ana, temsilci kuralı."""
    return sorted([r for r in R if r['ana_T'] and r['DOLU_ana'] and not (r['yer'] in TEMSILCI and r['ist'] != TEMSILCI[r['yer']])],
                  key=lambda r: (r['ist'], r['T']))


# ---------------------------------------------------------------- aşama H seçimi (§5.2)
def hiz_secim(R, kon):
    import numpy as np
    h = hashlib.sha256(H_TOHUM_METIN.encode()).hexdigest()
    rng = np.random.default_rng(int(h[:8], 16))
    A = ana_ornek(R)
    ists = sorted({r['ist'] for r in A})
    out = []
    for j in rng.choice(len(ists), H_N, replace=False):
        s = ists[int(j)]
        G = set()
        for r in A:
            if r['ist'] != s: continue
            x = D(r['a'])
            while x <= D(r['b']): G.add(x); x += TD(days=1)
        aday = sorted(d for d in G if H_ILK <= d and d + TD(days=H_GUN - 1) <= H_SON and d.day <= 20 - H_GUN + 1
                      and all(d + TD(days=i) in G for i in range(H_GUN)))
        d0 = aday[int(rng.integers(len(aday)))]
        lo = kon[s][1]; kay = math.floor(-lo / 15.0 + 0.5)        # TR-5b §3.1: d 00:00 - boylam/15 saat, tam saate
        pen = []
        for i in range(H_GUN):
            d = d0 + TD(days=i)
            t0 = dt.datetime(d.year, d.month, d.day) + TD(hours=kay); t1 = t0 + TD(hours=H_SAAT)
            assert t1.date() <= SON_HUKUM + TD(days=1) and d <= SON_HUKUM and t1.date() <= SON_ISTEK
            pen.append([t0.isoformat(), t1.isoformat()])
        sps = float(next(r['sps'] for r in A if r['ist'] == s))
        out.append(dict(ist=s, gun_ilk=d0.isoformat(), gun=[(d0 + TD(days=i)).isoformat() for i in range(H_GUN)],
                        utc=pen, cha='HH?', loc='--', ornek_beklenen=int(H_GUN * H_SAAT * 3600 * sps * 3)))
    return dict(tohum_metin=H_TOHUM_METIN, tohum=int(h[:8], 16), istek=out)


def hiz_post_govde(x):
    ag, st = x['ist'].split('.')
    return ''.join(f"{ag} {st} {x['loc']} {x['cha']} {a} {b}\n" for a, b in x['utc'])


def hiz_get_url(x, i):
    ag, st = x['ist'].split('.')
    a, b = x['utc'][i]
    return DS + '?' + urllib.parse.urlencode(dict(net=ag, sta=st, loc=x['loc'], cha=x['cha'], start=a, end=b))


# ---------------------------------------------------------------- kuru (ağsız)
def kuru(fed, dol):
    sha = girdi_denet(fed, dol)
    R = csv_oku(); W = adaylar(R); kon = fed_oku(fed); UST = ustveri_istasyonlari(R)
    vekil = lambda w: ('', 'HH', ('N', 'E'))                 # csv: adayların hepsi --.HHZ, 100 sn^-1 (vekil)
    assert all(w['csv_kanal'] == '--.HHZ' for w in W)
    L, _ = istek_kur(W, b13_penceresi(), vekil)
    say_ = dict(ustveri=len(UST), **istek_sayilari(L), hiz=H_N)
    if say_ != TABLO: sys.exit(f'§5.1 tablosundan sapma: {say_} != {TABLO}; durdu')
    # ön kayıt §2.5 / §5.3 sayıları (aşama 0'dan önce, kanıt için)
    A = ana_ornek(R)
    yt = collections.Counter(int(r['T'][:4]) for r in A)
    V = hacim_V([(r['ist'], D(r['a']), D(r['b']), int(r['T'][:4])) for r in A])
    Vr = {k: round(v, 1) for k, v in V.items()}
    if (len(A), [yt[y] for y in ANA_YIL], Vr) != (102, [15, 16, 15, 14, 14, 9, 10, 9], dict(A=298.5, C=196.7, D=153.6)):
        sys.exit(f'ön kayıt sayılarından sapma: {len(A)} {dict(yt)} {Vr}; durdu')
    H = hiz_secim(R, kon)
    hafif = len(UST) + len(L)
    sure_h = {f'{v} KiB/s': round(sum(min(x['ornek_beklenen'] * 1.3 / (v * 1024), H_TAVAN_SN) for x in H['istek']) / 3600, 2)
              for v in (23, 40, 83, 106, 341, 633)}
    out = dict(girdi_sha256=sha, istek_tablosu=say_, aday_penceresi=len(W), ustveri_istasyon=list(UST),
               onkayit_kontrol=dict(yer_pencere=len(A), yer_T={str(y): yt[y] for y in ANA_YIL}, V_GB_on=Vr,
                                    kapi=kapi({y: yt[y] for y in ANA_YIL})),
               hiz_secimi=H,
               sure_tahmini=dict(hafif_istek=hafif, hafif_saat_3sn=round(hafif * 3.0 / 3600, 2),
                                 asamaH_saat=sure_h, sure_sn_tavan=SURE_MAX),
               ag_istegi=0)
    yaz_json(os.path.join(BURASI, 'tr4_asama0_kuru.json'), out)
    print(json.dumps(dict(istek_tablosu=say_, aday=len(W), onkayit_kontrol=out['onkayit_kontrol']), ensure_ascii=False))
    for x in H['istek']: print('H', x['ist'], x['gun_ilk'], x['utc'][0][0], x['ornek_beklenen'])
    print('AĞ İSTEĞİ ATILMADI (kuru kip). Çıktı: tr4_asama0_kuru.json')
    return out


# ---------------------------------------------------------------- ağ
def ag_onayi():
    if '--ag-onay' not in sys.argv:
        print('Ağ kipi --ag-onay bayrağı olmadan çalışmaz; hiçbir istek atılmadı.'); sys.exit(2)


def sure_al(sure):
    s = SURE_MAX if sure is None else float(sure)
    if not 0 < s <= SURE_MAX: sys.exit(f'sure_sn en çok {SURE_MAX:.0f}; durdu')
    return simdi() + s


def kor_denet(bitis, sinir=SON_ISTEK):
    """İ1-E4 madde 9: bitişi sınırı aşan istek bağlantı kurulmadan reddedilir."""
    if not isinstance(bitis, dt.date) or isinstance(bitis, dt.datetime) or bitis > sinir or bitis > SON_ISTEK:
        raise SystemExit(f'KÖRLÜK: istek bitişi {bitis} > {min(sinir, SON_ISTEK)}; bağlantı kurulmadı, durdu')


def _getir(url):
    """Tek deneme, tek istek. (kod, bayt, gövde|None, retry_after_sn|None). Gövde yalnız üstveride kullanılır."""
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=120) as y:
            veri = y.read()
            return y.status, len(veri), veri, None
    except urllib.error.HTTPError as e:
        ra = e.headers.get('Retry-After') if e.headers else None
        try: ra = float(ra) if ra is not None else None
        except ValueError: ra = None
        return e.code, 0, None, ra
    except Exception as e:
        return type(e).__name__, 0, None, None


def _akit(url, govde, tavan_sn):
    """Aşama H: tek istek; gövde parça parça okunur, yalnız bayt ve sha256 tutulur (saklanmaz, çözülmez).
    tavan_sn aşılırsa o ana kadarki bayt ve süre döner. (kod, bayt, sha256, sn, kesik)."""
    h = hashlib.sha256(); n = 0; t0 = time.monotonic(); kesik = False
    req = urllib.request.Request(url, data=govde.encode() if govde else None, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as y:
            kod = y.status
            while True:
                if time.monotonic() - t0 > tavan_sn: kesik = True; break
                b = y.read(1 << 16)
                if not b: break
                h.update(b); n += len(b)
    except urllib.error.HTTPError as e:
        kod = e.code
    except Exception as e:
        kod = type(e).__name__
    return kod, n, h.hexdigest(), round(time.monotonic() - t0, 3), kesik


class Akis:
    """Tek akış: istekler arası >= ARA_SN; 429/503'te sonraki istekten önce Retry-After (<= 120 sn)."""
    def __init__(self, bitis, kip):
        self.son = 0.0; self.bekle = 0.0; self.bitis = bitis; self.kip = kip

    def sure_var(self):
        return self.bitis - simdi() >= 2 * BEKLENEN_SN[self.kip]

    def once(self):
        w = max(ARA_SN - (simdi() - self.son), self.bekle)
        w = min(w, max(0.0, self.bitis - simdi()))
        if w > 0: uyu(w)
        self.bekle = 0.0; self.son = simdi()

    def sonra(self, kod, ra):
        if kod in (429, 503): self.bekle = min(ra if ra is not None else 30.0, RETRY_AFTER_MAX)
        elif not isinstance(kod, int): self.bekle = 10.0


def istek_at(akis, url, bitis, sinir):
    kor_denet(bitis, sinir)
    akis.once()
    kod, n, veri, ra = _getir(url)
    akis.sonra(kod, ra)
    return kod, n, veri


# ---------------------------------------------------------------- ustveri
def ustveri_durum(ob, UST):
    ug = collections.Counter(x['ist'] for x in satirlar(os.path.join(ob, 'ustveri_gunluk.jsonl')) if x['kod'] not in KESIN)
    eksik = [s for s in UST if not os.path.exists(os.path.join(ob, 'ustveri', s + '.txt')) and ug[s] < 2]
    alinamayan = [s for s in UST if not os.path.exists(os.path.join(ob, 'ustveri', s + '.txt'))]
    return eksik, alinamayan


def ustveri(fed, dol, ob, sure=None):
    ag_onayi()
    girdi_denet(fed, dol); ob_denet(ob, dol)
    if os.path.exists(os.path.join(ob, 'istekler.json')): sys.exit('istek listesi kuruldu; üstveri değiştirilemez (§5.6)')
    bitis = sure_al(sure)
    UST = ustveri_istasyonlari(csv_oku())
    os.makedirs(os.path.join(ob, 'ustveri'), exist_ok=True)
    eksik, _ = ustveri_durum(ob, UST)
    print('üstveri kalan', len(eksik), '/', len(UST), flush=True)
    gunluk = ekle_ac(os.path.join(ob, 'ustveri_gunluk.jsonl')); akis = Akis(bitis, 'ustveri'); n = 0
    try:
        for s in eksik:
            if not akis.sure_var(): print('süre doldu; temiz çıkış (sürdürülebilir)'); break
            a, b = UST[s]; ag, st = s.split('.')
            q = urllib.parse.urlencode(dict(net=ag, sta=st, channel='BH?,HH?', level='channel', format='text',
                                            starttime=f'{a}T00:00:00', endtime=f'{b}T23:59:59'))
            kod, nb, veri = istek_at(akis, ST + '?' + q, b, SON_ISTEK); n += 1
            if kod in KESIN:     # kesin kod: tamamlandı (204/404/401/403 boş dosya, yani kanal yok)
                hedef = os.path.join(ob, 'ustveri', s + '.txt')
                with open(hedef + '.tmp', 'wb') as f: f.write(veri if kod == 200 and veri else b'')
                os.replace(hedef + '.tmp', hedef)
            gunluk.write(json.dumps(dict(ist=s, kod=kod, bayt=nb), sort_keys=True) + '\n'); gunluk.flush()
    finally:
        gunluk.close()
    eksik2, _ = ustveri_durum(ob, UST)
    print('üstveri isteği', n, 'kalan', len(eksik2))


# ---------------------------------------------------------------- kur (ağ isteği atmaz)
def kur(fed, dol, ob):
    ag_onayi()
    sha = girdi_denet(fed, dol); ob_denet(ob, dol)
    R = csv_oku(); W = adaylar(R); UST = ustveri_istasyonlari(R)
    eksik, alinamayan = ustveri_durum(ob, UST)
    if eksik: sys.exit(f'üstveri tamamlanmadı: {len(eksik)} istasyon; kur koşmaz')
    cache = {}
    def sec(w):
        if w['ist'] not in cache: cache[w['ist']] = kanal_epoklari(ob, w['ist'])
        return kanal_sec(cache[w['ist']], w)
    for s in UST:                                              # madde 7: bütün KO epoklarında konum kodu boş
        if s not in cache: cache[s] = kanal_epoklari(ob, s)
    b13 = b13_penceresi()
    L, secim = istek_kur(W, b13, sec)
    tam = {k: (None if s is None else dict(loc=s[0], bant=s[1], yatay=list(s[2]), aygit_hukum=bool(s[3])))
           for k, s in secim.items()}
    fark = []                                                  # madde 4: Z önizlemesinden farklı sonuç
    for w in W:
        s = tam[f"{w['ist']}|{w['T']}"]
        if s is None: fark.append(dict(pencere=f"{w['ist']}|{w['T']}", onizleme=w['csv_kanal'], simdi='uc_bilesen_yok'))
        elif s['aygit_hukum'] != w['csv_aygit']:
            fark.append(dict(pencere=f"{w['ist']}|{w['T']}", onizleme=f"aygit={w['csv_aygit']}", simdi=f"aygit={s['aygit_hukum']}"))
        elif f"{s['loc'] or '--'}.{s['bant']}Z" != w['csv_kanal']:
            fark.append(dict(pencere=f"{w['ist']}|{w['T']}", onizleme=w['csv_kanal'], simdi=f"{s['loc'] or '--'}.{s['bant']}Z"))
    out = dict(girdi_sha256=sha, istekler=L, secim=tam, ustveri_alinamayan=alinamayan, onizleme_farki=fark,
               sayi=istek_sayilari(L))
    yol = os.path.join(ob, 'istekler.json')
    if os.path.exists(yol):
        eski = json.load(open(yol, encoding='utf-8'))
        if eski != json.loads(json.dumps(out, default=str)): sys.exit('istekler.json farklı bir içerikle var; değiştirilemez (§5.6)')
        print('istekler.json zaten var ve aynı'); return
    if os.path.exists(os.path.join(ob, 'onbellek.jsonl')) and os.path.getsize(os.path.join(ob, 'onbellek.jsonl')) > 0:
        sys.exit('yoklama başlamış; istek listesi yeniden kurulamaz (§5.6)')
    yaz_json(yol, out)
    print('istek', len(L), out['sayi'], 'kanal seçilemeyen pencere', sum(1 for v in tam.values() if v is None),
          'üstverisi alınamayan', len(alinamayan), 'önizleme farkı', len(fark))


# ---------------------------------------------------------------- yokla
def yokla(fed, dol, ob, sure=None):
    ag_onayi()
    girdi_denet(fed, dol); ob_denet(ob, dol)
    if os.path.exists(os.path.join(ob, 'asama0_sonuc.json')): sys.exit('aşama 0 sayıldı; yeniden yoklama yapılmaz (§5.6)')
    bitis = sure_al(sure)
    L = json.load(open(os.path.join(ob, 'istekler.json'), encoding='utf-8'))['istekler']
    oyol = os.path.join(ob, 'onbellek.jsonl')
    d, n = son_durum(satirlar(oyol))
    kuyruk = [r for r in L if not tamam(d, n, anahtar(r))]
    print(f'kalan {len(kuyruk)} / {len(L)}', flush=True)
    f = ekle_ac(oyol); akis = Akis(bitis, 'yokla'); atilan = 0
    try:
        for r in kuyruk:
            if not akis.sure_var(): print('süre doldu; temiz çıkış (sürdürülebilir)'); break
            g = dt.date.fromisoformat(r['ay'] + '-15')
            q = (f"?net={r['ag']}&sta={r['ist']}&loc={r['loc'] or '--'}&cha={r['cha']}"
                 f"&start={r['ay']}-15T12:00:00&end={r['ay']}-15T12:01:00")
            t0 = simdi()
            kod, nb, _ = istek_at(akis, DS + q, g, SON_HUKUM if r['rol'] == 'ana' else SON_B13)   # gövde saklanmaz
            atilan += 1
            f.write(json.dumps(dict(k=anahtar(r), kod=kod, bayt=nb, sn=round(simdi() - t0, 2), deneme=n[anahtar(r)]),
                               sort_keys=True) + '\n')
            f.flush()
    finally:
        f.close()
    print('atılan', atilan)
    return atilan


# ---------------------------------------------------------------- say
def say(fed, dol, ob):
    sha = girdi_denet(fed, dol); ob_denet(ob, dol)
    R = csv_oku(); W = adaylar(R); UST = ustveri_istasyonlari(R)
    yol_ist = os.path.join(ob, 'istekler.json')
    ust_eksik, alinamayan = ustveri_durum(ob, UST)
    if not os.path.exists(yol_ist):
        sys.exit(f'aşama 0 tamamlanmadı: istek listesi yok, {len(ust_eksik)} üstveri; G0 verilmez')
    IST = json.load(open(yol_ist, encoding='utf-8'))
    oyol = os.path.join(ob, 'onbellek.jsonl')
    kayit, deneme = son_durum(satirlar(oyol))
    eksik = [anahtar(r) for r in IST['istekler'] if not tamam(kayit, deneme, anahtar(r))]
    if eksik or ust_eksik:
        sys.exit(f'aşama 0 tamamlanmadı: {len(eksik)} istek, {len(ust_eksik)} üstveri; G0 verilmez')
    Z5 = tr5_onbellek(dol)
    durum, neden = {}, collections.Counter()
    for w in W:
        k = f"{w['ist']}|{w['T']}"; s = IST['secim'].get(k); ag, st = w['ist'].split('.')
        if s is None: durum[k] = dict(dolu=False, neden='uc_bilesen_yok'); neden['uc_bilesen_yok'] += 1; continue
        if s['aygit_hukum']: durum[k] = dict(dolu=False, neden='aygit'); neden['aygit'] += 1; continue
        if w['aday']: zd = lambda ay: ay_durum(kayit.get(f"{ag}.{st}.{s['loc']}.{s['bant']}Z.{ay}"))
        else: zd = lambda ay: ay_durum(Z5.get((w['ist'], ay)))
        ds = [zd(ay) for ay in ay_listesi(w['a'], w['b'])]
        v = sum(1 for x in ds if x == 'var'); en = cur = 0
        for x in ds: cur = 0 if x == 'var' else cur + 1; en = max(en, cur)
        z_ok = bool(ds) and v / len(ds) >= DOLU_ORAN and en <= DOLU_BOSLUK
        if not w['aday']: assert z_ok, f'{k}: TR-5 önbelleğinden Z, csv DOLU_ana ile uyuşmuyor'
        bilgili = [orta_ay(x, y) for x, y in dilimler(w) if zd(orta_ay(x, y)) == 'var']
        h_ok = bool(bilgili) and all(ay_durum(kayit.get(f"{ag}.{st}.{s['loc']}.{s['bant']}{h}.{ay}")) == 'var'
                                     for ay in bilgili for h in s['yatay'])
        ok = z_ok and h_ok
        nd = 'dolu' if ok else ('z_ay' if not z_ok else ('yatay_bilgisiz' if not bilgili else 'yatay'))
        neden[nd] += 1
        durum[k] = dict(dolu=ok, neden=nd, z_oran=round(v / len(ds), 3) if ds else 0, z_bosluk=en,
                        z_kaynak='yeni_yoklama' if w['aday'] else 'TR-5_onbellek', bilgili_dilim=len(bilgili))
    dolu = [w for w in W if durum[f"{w['ist']}|{w['T']}"]['dolu']]
    yer_T = {y: len({w['yer'] for w in dolu if w['T'].year == y}) for y in ANA_YIL}
    kp = kapi(yer_T)
    hukum = 'G0 geçti' if kp['gecti'] else 'veri yok (aşama 0)'
    V = hacim_V([(w['ist'], w['a'], w['b'], w['T'].year) for w in dolu])
    # bilgi satırı 13 (G0'a girmez)
    s13 = IST['secim'].get(f"{B13_IST}|{B13_T}")
    b13 = dict(kanal=s13)
    if s13 and not s13['aygit_hukum']:
        ag, st = B13_IST.split('.')
        zs = {ay: ay_durum(kayit.get(f"{ag}.{st}.{s13['loc']}.{s13['bant']}Z.{ay}")) for ay in b13_aylar()}
        v = sum(1 for x in zs.values() if x == 'var'); en = cur = 0
        for x in zs.values(): cur = 0 if x == 'var' else cur + 1; en = max(en, cur)
        hs = {ay: [ay_durum(kayit.get(f"{ag}.{st}.{s13['loc']}.{s13['bant']}{h}.{ay}")) for h in s13['yatay']] for ay in b13_aylar()}
        b13.update(z=zs, yatay=hs, z_oran=round(v / len(zs), 3), z_bosluk=en,
                   dolu=v / len(zs) >= DOLU_ORAN and en <= DOLU_BOSLUK and all(hs[a] == ['var', 'var'] for a in zs if zs[a] == 'var'))
    else:
        b13['dolu'] = False
    # istek_durum (rol kırılımıyla)
    sd = {anahtar(r): ay_durum(kayit.get(anahtar(r))) for r in IST['istekler']}
    dz = lambda c: {d: c[d] for d in ('var', 'bos', 'kisitli', 'hata')}
    rol_d = collections.defaultdict(collections.Counter)
    for r in IST['istekler']: rol_d[r['rol']][sd[anahtar(r)]] += 1
    ug = collections.defaultdict(list)
    for x in satirlar(os.path.join(ob, 'ustveri_gunluk.jsonl')): ug[x['ist']].append(x['kod'])
    out = dict(
        girdi_sha256=sha, hukum=hukum, kapi=dict(yer=KAPI_YER, ara_yil=KAPI_ARA_YIL, **kp),
        yer_T={str(y): yer_T[y] for y in ANA_YIL}, dolu_yer_pencere=len(dolu),
        dolu_yer=len({w['yer'] for w in dolu}),
        indirme=('yapılır' if len(dolu) >= BILGI0_MIN_N else f'yapılmaz (dolu yer-penceresi {len(dolu)} < {BILGI0_MIN_N}; §4.3)'),
        neden={k: neden[k] for k in ('dolu', 'uc_bilesen_yok', 'aygit', 'z_ay', 'yatay', 'yatay_bilgisiz')}, pencere=durum, onizleme_farki=IST.get('onizleme_farki', []),
        V_GB={k: round(v, 3) for k, v in V.items()}, bilgi13=b13,
        istek_durum=dict(toplam=dz(collections.Counter(sd.values())), rol={ro: dz(c) for ro, c in sorted(rol_d.items())}),
        istek=dict(toplam=len(IST['istekler']), **IST['sayi']),
        ustveri_alinamayan={s: ug.get(s, []) for s in alinamayan},
        onbellek_sha256=sha_dosya(oyol), istekler_sha256=sha_dosya(yol_ist))
    yol = os.path.join(ob, 'asama0_sonuc.json')
    if os.path.exists(yol):
        if json.load(open(yol, encoding='utf-8')) != json.loads(json.dumps(out, default=str)):
            sys.exit('asama0_sonuc.json farklı bir içerikle var; say bir kez koşulur (§5.6); durdu')
        print('asama0_sonuc.json zaten var ve aynı')
    else:
        yaz_json(yol, out)
    print(json.dumps({k: out[k] for k in ('hukum', 'yer_T', 'dolu_yer_pencere', 'indirme', 'neden', 'V_GB')}, ensure_ascii=False))
    print('istek_durum', json.dumps(out['istek_durum']['toplam'], ensure_ascii=False), 'üstveri alınamayan', len(alinamayan))
    return out


# ---------------------------------------------------------------- hiz (aşama H) ve kademe
def hiz_durum(rows):
    """Ölçüm turları: tur -> {i: son satır}, deneme sayısı; POST reddedildi mi."""
    get = any(x.get('post_ret') for x in rows)
    tur = collections.defaultdict(dict); n = collections.Counter()
    for x in rows:
        if x.get('post_ret'): continue
        k = (x['olcum'], x['i']); n[k] += 1
        d = tur[x['olcum']]
        if x['i'] not in d or x['kod'] in KESIN or d[x['i']]['kod'] not in KESIN: d[x['i']] = x
    return tur, n, get


def tur_tamam(tur, n, k):
    return all(i in tur.get(k, {}) and (tur[k][i]['kod'] in KESIN or n[(k, i)] >= 2) for i in range(H_N))


def olcumler(tur, n):
    """Tamamlanmış turların [(v KiB/s, bitiş zamanı)]: v = Σ bayt / Σ süre (8 isteğin son satırları)."""
    out = []
    for k in sorted(tur):
        if not tur_tamam(tur, n, k): continue
        xs = [tur[k][i] for i in range(H_N)]; sn = sum(x['sn'] for x in xs)
        out.append((sum(x['bayt'] for x in xs) / 1024 / sn if sn > 0 else 0.0, max(x['t_bitis'] for x in xs)))
    return out


def kademe_karar(olc, V, son_an):
    """olc: tamamlanmış turların [(v KiB/s, bitiş zamanı)]. V: GB. son_an: şimdiki zaman.
    Dönen: (kademe|None, gerekçe). §5.3 madde 1-4; ara durum en çok 5 gün."""
    import statistics
    gun = lambda gb, v: (gb * 1e9 / (v * 1024) / 86400) if v > 0 else float('inf')
    def uygula(v):
        if gun(V['A'], v) <= ESIK_A_GUN: return 'A'
        if gun(V['D'], v) <= ESIK_D_GUN: return 'C'
        return None
    if not olc: return None, 'ölçüm yok'
    if len(olc) == 1:
        k = uygula(olc[0][0])
        if k: return k, 'madde 1-2 (ilk ölçüm)'
    if len(olc) >= H_OLCUM_MAX or son_an > olc[0][1] + H_ERTELEME_GUN * 86400:
        v = statistics.median([x[0] for x in olc])
        k = uygula(v)
        return (k, f'madde 3: {len(olc)} ölçümün medyanı') if k else ('veri yok (aktarım hızı)', 'madde 4')
    return None, 'ertelendi (aktarım hızı)'


def hiz(fed, dol, ob, sure=None):
    ag_onayi()
    girdi_denet(fed, dol); ob_denet(ob, dol)
    yol0 = os.path.join(ob, 'asama0_sonuc.json')
    if not os.path.exists(yol0): sys.exit('asama0_sonuc.json yok; aşama H, aşama 0 sayılmadan koşmaz')
    S0 = json.load(open(yol0, encoding='utf-8'))
    if S0['dolu_yer_pencere'] < BILGI0_MIN_N: sys.exit(f"dolu yer-penceresi {S0['dolu_yer_pencere']} < 30: indirme yapılmaz; aşama H koşmaz")
    V = S0['V_GB']
    bitis = sure_al(sure)
    H = hiz_secim(csv_oku(), fed_oku(fed))['istek']
    gyol = os.path.join(ob, 'hiz_gunluk.jsonl')
    akis = Akis(bitis, 'hiz'); atilan = 0
    while True:
        tur, n, get = hiz_durum(satirlar(gyol))
        olc = olcumler(tur, n)
        karar, gerekce = kademe_karar(olc, V, simdi())
        if karar is not None: break                            # §5.3 madde 1, 2 ya da 4
        kmax = max(tur) if tur else 0
        if kmax and not tur_tamam(tur, n, kmax): k = kmax          # süren tur
        elif kmax == 0: k = 1
        elif kmax >= H_OLCUM_MAX: break
        else:
            bas = olc[-1][1] + H_ARA_GUN * 86400
            if simdi() < bas:
                print('ertelendi (aktarım hızı): sonraki ölçüm en erken',
                      dt.datetime.fromtimestamp(bas, dt.timezone.utc).isoformat(timespec='seconds'))
                break
            k = kmax + 1
        kalan = [i for i in range(H_N) if not (i in tur.get(k, {}) and (tur[k][i]['kod'] in KESIN or n[(k, i)] >= 2))]
        if not kalan: continue
        f = ekle_ac(gyol)
        try:
            for i in kalan:
                if not akis.sure_var(): print('süre doldu; temiz çıkış (sürdürülebilir)'); f.close(); return hiz_yaz(ob, gyol, V, H)
                x = H[i]
                son_gun = max(D(g) for g in x['gun'])
                if get:
                    kods, nb, hs, sn, kes = [], 0, hashlib.sha256(), 0.0, False
                    for j in range(H_GUN):
                        kor_denet(son_gun, SON_HUKUM); akis.once()
                        kj, nj, shj, snj, kj_kes = _akit(hiz_get_url(x, j), None, max(1.0, H_TAVAN_SN - sn))
                        akis.sonra(kj, None); kods.append(kj); nb += nj; sn += snj; hs.update(shj.encode())
                        if kj_kes or sn >= H_TAVAN_SN: kes = True; break
                    kod = 200 if 200 in kods else kods[0]; sh = hs.hexdigest(); bicim = 'GET'
                else:
                    kor_denet(son_gun, SON_HUKUM); akis.once()
                    kod, nb, sh, sn, kes = _akit(DS, hiz_post_govde(x), H_TAVAN_SN); akis.sonra(kod, None); bicim = 'POST'
                    if kod in H_POST_RET and k == 1 and not any(r['bicim'] == 'POST' and r['kod'] == 200 for r in satirlar(gyol)):
                        f.write(json.dumps(dict(olcum=k, i=i, kod=kod, bicim='POST', post_ret=True), sort_keys=True) + '\n'); f.flush()
                        print('KOERI POST isteğini reddetti; gün gün GET biçimine geçildi'); get = True; break
                atilan += 1
                f.write(json.dumps(dict(olcum=k, i=i, ist=x['ist'], gun_ilk=x['gun_ilk'], bicim=bicim, kod=kod, bayt=nb, sn=sn,
                                        sha256=sh, kesik=kes, deneme=n[(k, i)], ornek_beklenen=x['ornek_beklenen'],
                                        t_bitis=round(simdi(), 1)), sort_keys=True) + '\n'); f.flush()
        finally:
            if not f.closed: f.close()
    return hiz_yaz(ob, gyol, V, H)


def hiz_yaz(ob, gyol, V, H):
    tur, n, get = hiz_durum(satirlar(gyol))
    olc, ayr = olcumler(tur, n), {}
    for k in sorted(tur):
        if not tur_tamam(tur, n, k): ayr[str(k)] = dict(tamam=False, istek=len(tur[k])); continue
        xs = [tur[k][i] for i in range(H_N)]; sn = sum(x['sn'] for x in xs); nb = sum(x['bayt'] for x in xs)
        v = nb / 1024 / sn if sn > 0 else 0.0
        ayr[str(k)] = dict(tamam=True, v_KiBs=round(v, 2), bayt=nb, sn=round(sn, 1),
                           bayt_ornek={x['ist']: round(x['bayt'] / x['ornek_beklenen'], 3) for x in xs if x['kod'] == 200},
                           kod={str(i): xs[i]['kod'] for i in range(H_N)}, kesik=sum(1 for x in xs if x['kesik']))
    karar, gerekce = kademe_karar(olc, V, simdi())
    import statistics
    vm = statistics.median([x[0] for x in olc]) if olc else None
    gun = lambda gb: round(gb * 1e9 / (vm * 1024) / 86400, 1) if vm else None
    out = dict(V_GB=V, olcum=ayr, v_medyan_KiBs=None if vm is None else round(vm, 2),
               V_A_gun=gun(V['A']), V_C_gun=gun(V['C']), V_D_gun=gun(V['D']), bicim='GET' if get else 'POST',
               kademe=karar or ('ertelendi (aktarım hızı)' if olc else 'ölçüm sürüyor'), gerekce=gerekce)
    hz = ', '.join(f"{ayr[k]['v_KiBs']}" for k in sorted(ayr) if ayr[k]['tamam'])
    if karar == 'veri yok (aktarım hızı)':
        out['ek_metin'] = f"aşama H hızları {hz} KiB/s; medyan {out['v_medyan_KiBs']}; V_D / v = {out['V_D_gun']} gün; bilgi satırı 0: hesaplanmadı (indirme yok)"
    elif karar is None and olc:
        out['ek_metin'] = f"ölçülen hız {hz} KiB/s (ölçüm {len(olc)} adet); V_D / v = {out['V_D_gun']} gün"
    yaz_json(os.path.join(ob, 'hiz_sonuc.json'), out)
    print(json.dumps({k: out[k] for k in ('v_medyan_KiBs', 'V_D_gun', 'kademe', 'gerekce', 'bicim')}, ensure_ascii=False))
    return out


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    arg = [a for a in sys.argv[2:] if not a.startswith('--')]
    if k == 'kuru': kuru(arg[0], arg[1])
    elif k == 'ustveri': ustveri(arg[0], arg[1], arg[2], float(arg[3]) if len(arg) > 3 else None)
    elif k == 'kur': kur(arg[0], arg[1], arg[2])
    elif k == 'yokla': yokla(arg[0], arg[1], arg[2], float(arg[3]) if len(arg) > 3 else None)
    elif k == 'say': say(arg[0], arg[1], arg[2])
    elif k == 'hiz': hiz(arg[0], arg[1], arg[2], float(arg[3]) if len(arg) > 3 else None)
    else: print(__doc__)
