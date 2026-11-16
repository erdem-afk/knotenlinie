#!/usr/bin/env python3
"""TR-4 İNDİRME: KOERI FDSN dataselect istemcisi, ay ay kronolojik indirme, saatlik ÇİF + RMS + tamlık, ham verinin silinmesi.

Ön kayıt: `kayit/onkayit/TR-4_marmara-hiz-tabani_ONKAYIT.md` DONDURULDU sürüm 2 + Ek 1; §3.1–3.3 (TR-5b §3.1–3.3 zinciri),
§5.2–5.6; İNCELEME-1 İ1-E1 (kronolojik sıra, bütçe, kesik koşu), İ1-E3 (saatlik ÇİF saklama), İ1-Ö4 (dondurma);
aşama 0 kod incelemesi K7 (üretim isteklerinin soket zaman aşımı aşama H ile aynı; "kesin kodla tamamlandı" aynı
KESIN kümesiyle). Okumalar: `kayit/onkayit/TR-4_KODLAYICI-OKUMALARI.md`.

BU MODÜL ε YA DA Δ HESAPLAMAZ. Yalnız saatlik ÇİF (iki bant), saat-bileşen RMS'i (0,5–2 Hz) ve örnek tamlığı yazar
(§5.5). ε ve Δ yalnız `tr4_kosu.py`'de, indirme bittikten ya da bütçeyle kesildikten sonra hesaplanır; bu modül zincir
işlevlerini (germe, yığın, ay eşlemesi) içermez ve içe aktarmaz.

Kurallar (özet):
  - Tek akış; istekler arası ≥ 2 sn (aşama H ile aynı); genel User-Agent; TLS doğrulaması açık; 429/503'te Retry-After
    (en çok 120 sn; yoksa 30 sn) beklenir. 401/403 "kısıtlı" sayılır: kesindir, yeniden denenmez, aşılmaz.
  - Kesin kodlar KESIN = (200, 204, 404, 401, 403) (tr4_asama0.py ile aynı küme). Öteki kodlar ve bağlantı hataları
    sonraki çağrıda bir kez yeniden denenir (istek başına en çok iki deneme). İndirme sonunda kesin olmayan son
    durum oranı > %5 ise tek bir yeniden deneme turu yapılır (§5.5 son cümle; TR-5b §5).
  - Soket zaman aşımı 900 sn (aşama H'nin `H_TAVAN_SN`'i; Ek 1 Ö1 ve K7). Üretim isteğinin toplam süresine tavan
    konmaz; yalnız işin süre sınırı (sure_sn) isteği keser; kesilen istek deneme sayılmaz ve sonraki çağrıda yeniden
    atılır.
  - Körlük: her isteğin bitişi ≤ 2025-12-31; hüküm verisinin günü d ≤ 2023-12-24; bilgi satırı 13'ünkü ≤ 2025-05-31.
    Aşılırsa istek BAĞLANTI KURULMADAN reddedilir (SystemExit).
  - İstek birimi istasyon-aydır: bir POST isteği o ayın indirilecek günlerinin 4 saatlik pencerelerini
    "<ağ> <ist> <konum|--> <bant>? <başlangıç> <bitiş>" satırlarıyla ister (aşama H biçimi). Aşama H POST'un
    reddedildiğini yazdıysa (hiz_sonuc.json "bicim" = GET) gün gün GET atılır.
  - Gün d istasyonun yerel ortalama güneş tarihidir; UTC penceresi [d 00:00 − boylam/15 saat (tam saate yuvarlanmış),
    +4 saat] (TR-5b §3.1; tr4_asama0.hiz_secim ile aynı yuvarlama).
  - Kademe C: yalnız d'nin ayın 1–20. günleri (§3.2). Kademe A: her gün.
  - Sıra: 2014-01'den 2023-12'ye ay ay, her ayda istasyonlar kod sırasıyla (§5.3); sonra bilgi satırı 13'ün
    (KO.SLVT, 2024-03…2025-05) ayları.
  - Bütçe: etkin indirme süresi 21 gün (504 iş-saati; işlerin duvar saatleri toplamı) ya da ilk indirme isteğinden
    itibaren 42 takvim günü; hangisi önce dolarsa indirme kalıcı olarak durur (durum "kesildi").
  - Her istasyon-ay: indir (yerel geçici dizine) → saatlik ÇİF/RMS/tamlık → depoya geçici adla yaz, os.replace →
    sha256 → durum satırı → ham dosyayı sil.

Kipler:
  plan   <ob> <depo>                           ağsız; istek planını yazdırır (sayılar, GB tahmini).
  indir  <ob> <depo> <yerel> [sure_sn] --ag-onay
         <ob>: aşama 0 dizini (asama0_sonuc.json, istekler.json, hiz_sonuc.json, girdi/ham/marmara_fed_kanal.txt);
         <depo>: saatlik ÇİF deposu (varsayılan /mnt/project-files/turetme/tr4-cif/); durum dosyaları da oradadır;
         <yerel>: ham miniSEED'in geçici dizini (depo dışı, yerel disk). sure_sn en çok 6000 (varsayılan 6000).
"""
import collections, datetime as dt, hashlib, json, math, os, re, sys, time
import urllib.request, urllib.error, urllib.parse
import csv

import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
TD = dt.timedelta

# ---------------------------------------------------------------- dondurulmuş sabitler
DEPO_VARSAYILAN = '/mnt/project-files/turetme/tr4-cif'
DS = 'https://eida.koeri.boun.edu.tr/fdsnws/dataselect/1/query'      # Ek 1: sunucu adı
UA = 'fdsn-client/0.1 (python-urllib)'                               # genel; kişi ya da proje adı yok
ARA_SN = 2.0                                                         # §5.2: istekler arası ≥ 2 sn
ZAMAN_ASIMI_SN = 900.0                                               # K7: aşama H'nin soket zaman aşımı (H_TAVAN_SN)
KESIN = (200, 204, 404, 401, 403)                                    # K7: tr4_asama0.KESIN ile aynı
RETRY_AFTER_MAX, RETRY_AFTER_YOK = 120.0, 30.0
SURE_MAX = 6000.0
DENEME_MAX = 2                                                       # İ1-E4 madde 6
TUR_ESIK = 0.05                                                      # §5.5: başarısız istek oranı > %5 → tek tur
SON_ISTEK = dt.date(2025, 12, 31)
SON_HUKUM = dt.date(2023, 12, 24)
SON_B13 = dt.date(2025, 5, 31)
ILK_AY, SON_AY = (2014, 1), (2023, 12)                               # §5.3 kronolojik sıra
BUTCE_ETKIN_SN = 21 * 86400.0                                        # 504 iş-saati
BUTCE_TAKVIM_SN = 42 * 86400.0
B13_IST, B13_T = 'KO.SLVT', dt.date(2025, 4, 23)
B13_ILK, B13_SON = dt.date(2024, 3, 1), dt.date(2025, 5, 31)
H_SAAT = 4
C_GUN = 20                                                           # kademe C: ayın 1–20. günleri
BAYT_ORNEK = 1.3

# zincir sabitleri (TR-5b §3.2–3.3; başvuru uygulamasıyla aynı değerler)
FS = 20.0
TAU_MAX = 60.0
NLAG = int(round(TAU_MAX * FS))                                      # 1200 → 2401 gecikme
N20 = int(3600 * FS)                                                 # bir saat, 20 sn^-1
KABUL_TAMLIK = 0.99
BOSLUK_ARADEGER_SN = 1.0
KONIK = 0.05                                                         # %5 Hann konik (her uçta, obspy kuralı)
INDIRGEME_KESIM = (7.5, 8.0)                                         # 8 Hz üstü sıfır, 0,5 Hz kosinüs geçiş
BANTLAR = {'b052': (0.4, 0.5, 2.0, 2.1), 'b24': (1.9, 2.0, 4.0, 4.1)}  # beyazlatma: düz [f1, f2], kenarlar kosinüs
RMS_BANT = (0.5, 2.0)
CIFTLER = ((0, 2), (0, 1), (1, 2))                                   # ZE, ZN, EN (bileşen sırası Z, N|1, E|2)
CIFT_AD = ('ZE', 'ZN', 'EN')
SURUM = 'tr4_indir-1'

simdi = time.time                                                    # sınamalar değiştirebilir (ağsız)
uyu = time.sleep


def sha_dosya(y):
    h = hashlib.sha256()
    with open(y, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def yaz_json(yol, obj):
    with open(yol + '.tmp', 'w', encoding='utf-8') as f:
        f.write(json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True, default=str) + '\n')
    os.replace(yol + '.tmp', yol)


def satirlar(yol):
    """jsonl; yarım ya da bozuk satır atlanır (tr4_asama0.satirlar ile aynı)."""
    out = []
    if os.path.exists(yol):
        for l in open(yol, encoding='utf-8'):
            try: out.append(json.loads(l))
            except ValueError: pass
    return out


def ekle_ac(yol):
    """Ekleme kipi; dosya yarım satırla bitiyorsa önce satır sonu (tr4_asama0.ekle_ac ile aynı)."""
    if os.path.exists(yol) and os.path.getsize(yol) > 0:
        with open(yol, 'rb') as g:
            g.seek(-1, os.SEEK_END); yarim = g.read(1) != b'\n'
        if yarim:
            with open(yol, 'a', encoding='utf-8') as g: g.write('\n')
    return open(yol, 'a', encoding='utf-8')


# ---------------------------------------------------------------- gün ve pencere
def kaydirma_saat(lon):
    """TR-5b §3.1: d 00:00 − boylam/15 saat, tam saate yuvarlanır (tr4_asama0.hiz_secim ile aynı)."""
    return math.floor(-lon / 15.0 + 0.5)


def gun_utc(d, lon):
    t0 = dt.datetime(d.year, d.month, d.day) + TD(hours=kaydirma_saat(lon))
    return t0, t0 + TD(hours=H_SAAT)


def kor_denet(bitis_utc, gun_d, rol):
    """Körlük: bağlantı kurulmadan önce. bitis_utc: isteğin en geç UTC bitişi (datetime); gun_d: en geç gün d."""
    if not isinstance(bitis_utc, dt.datetime) or not isinstance(gun_d, dt.date):
        raise SystemExit('KÖRLÜK: tarih türü geçersiz; bağlantı kurulmadı, durdu')
    sinir = SON_HUKUM if rol == 'ana' else SON_B13
    if bitis_utc.date() > SON_ISTEK or bitis_utc >= dt.datetime(2026, 1, 1) or gun_d > sinir or gun_d > SON_ISTEK:
        raise SystemExit(f'KÖRLÜK: istek bitişi {bitis_utc} / gün {gun_d} sınırı aşıyor ({sinir}, {SON_ISTEK}); '
                         'bağlantı kurulmadı, durdu')


# ---------------------------------------------------------------- girdiler (aşama 0 çıktıları)
def fed_konum(fed):
    kon = {}
    for l in open(fed, encoding='utf-8', errors='replace'):
        if l.startswith('#') or '|' not in l: continue
        p = l.rstrip('\n').split('|')
        if len(p) < 17 or p[0] != 'KO': continue
        kon['KO.' + p[1]] = (float(p[4]), float(p[5]))
    return kon


def csv_oku(yol=None):
    R = list(csv.DictReader(open(yol or os.path.join(BURASI, 'tr4_pencereler.csv'), encoding='utf-8')))
    return {f"{r['ist']}|{r['T']}": r for r in R}


def girdiler(ob, csv_yol=None):
    """Aşama 0'dan sonra dolu kalan yer-pencereleri, kanal seçimi, kademe, biçim, konumlar."""
    S0 = json.load(open(os.path.join(ob, 'asama0_sonuc.json'), encoding='utf-8'))
    IST = json.load(open(os.path.join(ob, 'istekler.json'), encoding='utf-8'))
    H = json.load(open(os.path.join(ob, 'hiz_sonuc.json'), encoding='utf-8'))
    kon = fed_konum(os.path.join(ob, 'girdi', 'ham', 'marmara_fed_kanal.txt'))
    C = csv_oku(csv_yol)
    W = []
    for k, d in sorted(S0['pencere'].items()):
        if not d['dolu']: continue
        r = C[k]; s = IST['secim'][k]
        W.append(dict(k=k, ist=r['ist'], yer=r['yer'], T=dt.date.fromisoformat(r['T']), a=dt.date.fromisoformat(r['a']),
                      b=dt.date.fromisoformat(r['b']), loc=s['loc'], bant=s['bant'], yatay=list(s['yatay'])))
    b13 = None
    s13 = IST['secim'].get(f'{B13_IST}|{B13_T}')
    if S0.get('bilgi13', {}).get('dolu') and s13:
        b13 = dict(k=f'{B13_IST}|{B13_T}', ist=B13_IST, yer=B13_IST, T=B13_T, loc=s13['loc'], bant=s13['bant'],
                   yatay=list(s13['yatay']))
    return dict(W=W, b13=b13, kademe=H.get('kademe'), bicim=H.get('bicim', 'POST'), hiz=H, S0=S0, konum=kon)


# ---------------------------------------------------------------- plan (kronolojik)
def gun_secimi(d, kademe):
    return kademe == 'A' or d.day <= C_GUN


def b13_gunleri(kademe):
    """Bilgi satırı 13 (§8 madde 13, İ1-K5): [T − 69, T + 30] her gün; [T − 400, T − 70] kademeye göre."""
    out = []
    for i in range(-400, 31):
        d = B13_T + TD(days=i)
        if i >= -69 or gun_secimi(d, kademe): out.append(d)
    return [d for d in out if d <= SON_B13]


def plan(G):
    """Dönen: istasyon-ay işleri, kronolojik (ay, istasyon kodu). Ana ayları 2014-01…2023-12, sonra bilgi 13."""
    kademe = G['kademe']
    if kademe not in ('A', 'C'): raise SystemExit(f'kademe seçilmedi ({kademe}); indirme yapılmaz (§5.3)')
    gunler = collections.defaultdict(set); kanal = {}
    for w in G['W']:
        x = w['a']
        while x <= w['b']:
            if gun_secimi(x, kademe): gunler[w['ist']].add(x)
            x += TD(days=1)
        kk = (w['loc'], w['bant'], tuple(w['yatay']))
        if kanal.setdefault(w['ist'], kk) != kk:
            raise SystemExit(f"{w['ist']}: pencereler arasında kanal seçimi farklı; tek istasyon-ay isteği kurulamaz")
    isler = []
    y, m = ILK_AY
    while (y, m) <= SON_AY:
        for s in sorted(gunler):
            g = sorted(d for d in gunler[s] if (d.year, d.month) == (y, m))
            if not g: continue
            loc, bant, yat = kanal[s]
            isler.append(dict(k=f'{s}|{y:04d}-{m:02d}', ist=s, ay=f'{y:04d}-{m:02d}', rol='ana', loc=loc, bant=bant,
                              yatay=list(yat), gunler=[d.isoformat() for d in g]))
        m += 1
        if m == 13: y, m = y + 1, 1
    if G.get('b13'):
        b = G['b13']; g13 = b13_gunleri(kademe)
        for ay in sorted({(d.year, d.month) for d in g13}):
            g = [d.isoformat() for d in g13 if (d.year, d.month) == ay]
            isler.append(dict(k=f"{b['ist']}|{ay[0]:04d}-{ay[1]:02d}|b13", ist=b['ist'], ay=f'{ay[0]:04d}-{ay[1]:02d}',
                              rol='bilgi13', loc=b['loc'], bant=b['bant'], yatay=list(b['yatay']), gunler=g))
    for x in isler:                                    # körlük: plan düzeyinde de
        son = max(dt.date.fromisoformat(g) for g in x['gunler'])
        assert son <= (SON_HUKUM if x['rol'] == 'ana' else SON_B13) and son <= SON_ISTEK, x['k']
    return isler


def pencere_aylari(w, kademe):
    """Bir yer-penceresinin indirilmesi gereken istasyon-ay anahtarları (kesik koşu sayımı için)."""
    out = set(); x = w['a']
    while x <= w['b']:
        if gun_secimi(x, kademe): out.add(f"{w['ist']}|{x.year:04d}-{x.month:02d}")
        x += TD(days=1)
    return out


# ---------------------------------------------------------------- HTTP (tek akış)
class Akis:
    def __init__(self):
        self.son = -1e18; self.bekle = 0.0

    def once(self, bitis):
        w = max(ARA_SN - (simdi() - self.son), self.bekle)
        w = min(w, max(0.0, bitis - simdi()))
        if w > 0: uyu(w)
        self.bekle = 0.0; self.son = simdi()

    def sonra(self, kod, ra):
        if kod in (429, 503): self.bekle = min(ra if ra is not None else RETRY_AFTER_YOK, RETRY_AFTER_MAX)
        elif not isinstance(kod, int): self.bekle = 10.0


def _akit(url, govde, hedef, son_an, zaman_asimi=ZAMAN_ASIMI_SN):
    """Tek istek; gövde parça parça hedef + '.part' dosyasına yazılır, sonra yeniden adlandırılır.
    Dönen: (kod, bayt, sha256, sn, sure_kesti, retry_after). son_an (epoch) geçilirse okuma bırakılır (sure_kesti)."""
    h = hashlib.sha256(); n = 0; t0 = time.monotonic(); kod = None; ra = None; kesti = False
    req = urllib.request.Request(url, data=govde.encode() if govde else None, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=zaman_asimi) as y:
            kod = y.status
            cl = y.headers.get('Content-Length')
            with open(hedef + '.part', 'wb') as f:
                while True:
                    if simdi() > son_an: kesti = True; break
                    b = y.read(1 << 16)
                    if not b: break
                    f.write(b); h.update(b); n += len(b)
            if not kesti and cl is not None and cl.isdigit() and n < int(cl): kod = 'EksikGovde'   # kesik gövde: kesin değil
    except urllib.error.HTTPError as e:
        kod = e.code
        r = e.headers.get('Retry-After') if e.headers else None
        try: ra = float(r) if r is not None else None
        except ValueError: ra = None
    except Exception as e:                                           # bağlantı, zaman aşımı, sıfırlanma
        kod = type(e).__name__
    sn = round(time.monotonic() - t0, 3)
    if kod == 200 and not kesti and n > 0: os.replace(hedef + '.part', hedef)
    elif os.path.exists(hedef + '.part'): os.remove(hedef + '.part')
    return kod, n, h.hexdigest(), sn, kesti, ra


def post_govde(x, kon):
    ag, st = x['ist'].split('.'); lon = kon[x['ist']][1]; out = []
    for g in x['gunler']:
        t0, t1 = gun_utc(dt.date.fromisoformat(g), lon)
        out.append(f"{ag} {st} {x['loc'] or '--'} {x['bant']}? {t0.isoformat()} {t1.isoformat()}\n")
    return ''.join(out)


def get_url(x, kon, g, taban):
    ag, st = x['ist'].split('.'); t0, t1 = gun_utc(dt.date.fromisoformat(g), kon[x['ist']][1])
    return taban + '?' + urllib.parse.urlencode(dict(net=ag, sta=st, loc=x['loc'] or '--', cha=x['bant'] + '?',
                                                     start=t0.isoformat(), end=t1.isoformat()))


def istek_bitisi(x, kon):
    son = max(dt.date.fromisoformat(g) for g in x['gunler'])
    return gun_utc(son, kon[x['ist']][1])[1], son


# ---------------------------------------------------------------- saatlik ön işlem ve ÇİF (TR-5b §3.2–3.3)
def _kosinus_pencere(f, f0, f1, f2, f3):
    a = np.zeros_like(f)
    a[(f >= f1) & (f <= f2)] = 1.0
    m = (f >= f0) & (f < f1); a[m] = 0.5 * (1 - np.cos(np.pi * (f[m] - f0) / (f1 - f0)))
    m = (f > f2) & (f <= f3); a[m] = 0.5 * (1 + np.cos(np.pi * (f[m] - f2) / (f3 - f2)))
    return a


_F20 = np.fft.rfftfreq(N20, 1 / FS)
BEYAZ = {k: _kosinus_pencere(_F20, *v) for k, v in BANTLAR.items()}
RMS_MASKE = (_F20 >= RMS_BANT[0]) & (_F20 <= RMS_BANT[1])


def saat_onisle(x, fs):
    """Bir bileşenin bir saati (NaN = örnek yok) → (20 sn^-1 dizinin spektrumu, 0,5–2 Hz RMS) ya da None.
    §3.2 madde 1 (boşluk: ≤ 1 sn iç boşluk doğrusal aradeğer; daha uzun boşluk ve uçlar, ortalama ve eğilim
    çıkarıldıktan sonra sıfır), 2 (ortalama, eğilim, %5 Hann), 3 (FFT indirgeme), 4'ün RMS'i."""
    n0 = len(x); ok = ~np.isnan(x)
    if ok.sum() < 2: return None
    i = np.arange(n0)
    y = x.copy()
    # ≤ 1 sn iç boşluklar: doğrusal aradeğer
    if not ok.all():
        kenar = np.flatnonzero(np.diff(np.concatenate(([1], ok.astype(np.int8), [1]))))
        for a, b in zip(kenar[::2], kenar[1::2]):                   # [a, b) boş
            if a > 0 and b < n0 and (b - a) <= BOSLUK_ARADEGER_SN * fs:
                y[a:b] = np.interp(i[a:b], [a - 1, b], [y[a - 1], y[b]])
    ok2 = ~np.isnan(y)
    p = np.polyfit(i[ok2].astype(np.float64), y[ok2], 1)            # ortalama + doğrusal eğilim
    y = np.where(ok2, y - np.polyval(p, i), 0.0)
    k = int(round(KONIK * n0))
    if k > 0:
        w = 0.5 * (1 - np.cos(np.pi * np.arange(k) / k))
        y[:k] *= w; y[-k:] *= w[::-1]
    X = np.fft.rfft(y)
    f0 = np.fft.rfftfreq(n0, 1 / fs)
    nb = N20 // 2 + 1
    if len(X) < nb: X = np.concatenate([X, np.zeros(nb - len(X), complex)])
    Y = X[:nb] * _kosinus_pencere(f0[:nb] if len(f0) >= nb else _F20, -1, 0, *INDIRGEME_KESIM)[:nb] * (N20 / n0)
    Y = Y.copy(); Y[-1] = Y[-1].real
    rms = math.sqrt(2.0 * np.sum(np.abs(Y[RMS_MASKE]) ** 2)) / N20  # Parseval: bant içi RMS
    return Y, rms


def beyazlat(Y, bant):
    return np.exp(1j * np.angle(Y)) * BEYAZ[bant]


def cif3(Ys):
    """Üç bileşenin beyazlatılmış spektrumlarından ZE, ZN, EN ÇİF'leri; gecikme ±60 sn (2401), enerji çarpımının
    karekökü ile normalleştirilir. c[τ] = Σ_t a(t) b(t + τ)."""
    xs = [np.fft.irfft(Y, N20) for Y in Ys]
    F = [np.fft.rfft(x, 2 * N20) for x in xs]
    en = [float(np.dot(x, x)) for x in xs]
    out = np.full((3, 2 * NLAG + 1), np.nan)
    for j, (a, b) in enumerate(CIFTLER):
        if en[a] <= 0 or en[b] <= 0: continue
        c = np.fft.irfft(np.conj(F[a]) * F[b], 2 * N20)
        out[j] = np.concatenate([c[-NLAG:], c[:NLAG + 1]]) / math.sqrt(en[a] * en[b])
    return out


def saat_dizisi(parcalar, t0, fs):
    """parcalar: [(başlangıç epoch, fs, veri)] aynı kanal. [t0, t0 + 3600) için NaN'lı dizi."""
    n0 = int(round(3600 * fs)); x = np.full(n0, np.nan)
    for ts, f, d in parcalar:
        if abs(f - fs) > 1e-6: continue
        i0 = int(round((ts - t0) * fs))
        a, b = max(0, i0), min(n0, i0 + len(d))
        if b > a: x[a:b] = d[a - i0:b - i0]
    return x


def isle_istasyon_ay(ham, x, kon):
    """Ham miniSEED (istasyon-ay) → saatlik ÇİF, RMS, tamlık. Dönen dict (numpy dizileri) + meta."""
    from obspy import read
    st = read(ham, format='MSEED')
    lon = kon[x['ist']][1]
    kanal = [x['bant'] + 'Z', x['bant'] + x['yatay'][0], x['bant'] + x['yatay'][1]]
    loc = x['loc'] or ''
    par = {}; fs_k = {}
    for c in kanal:
        s = st.select(location=loc, channel=c)
        L = [(tr.stats.starttime.timestamp, float(tr.stats.sampling_rate), tr.data.astype(np.float64)) for tr in s]
        par[c] = L
        fs_k[c] = sorted({round(f, 6) for _, f, _ in L})
    gun = [dt.date.fromisoformat(g) for g in x['gunler']]
    nd = len(gun); nl = 2 * NLAG + 1
    ccf = {b: np.full((nd, H_SAAT, 3, nl), np.nan, np.float32) for b in BANTLAR}
    rms = np.full((nd, H_SAAT, 3), np.nan, np.float32)
    tam = np.zeros((nd, H_SAAT, 3), np.float32)
    for i, d in enumerate(gun):
        t0 = gun_utc(d, lon)[0].replace(tzinfo=dt.timezone.utc).timestamp()
        for h in range(H_SAAT):
            th = t0 + 3600 * h; Ys = []
            for j, c in enumerate(kanal):
                fs = fs_k[c][0] if len(fs_k[c]) == 1 else None
                if fs is None or fs < 2 * INDIRGEME_KESIM[1]: Ys.append(None); continue
                xs = saat_dizisi(par[c], th, fs)
                tam[i, h, j] = float(np.mean(~np.isnan(xs)))
                if tam[i, h, j] < KABUL_TAMLIK: Ys.append(None); continue
                r = saat_onisle(xs, fs)
                if r is None: Ys.append(None); continue
                Ys.append(r[0]); rms[i, h, j] = r[1]
            if all(Y is not None for Y in Ys):                       # §3.2 madde 1: üç bileşen birlikte
                for b in BANTLAR:
                    ccf[b][i, h] = cif3([beyazlat(Y, b) for Y in Ys]).astype(np.float32)
    meta = dict(ist=x['ist'], ay=x['ay'], rol=x['rol'], loc=x['loc'], kanal=kanal, fs={c: fs_k[c] for c in kanal},
                kaydirma_saat=kaydirma_saat(lon), gunler=x['gunler'], surum=SURUM, ciftler=list(CIFT_AD))
    return dict(gun=np.array([d.toordinal() for d in gun], np.int32), ccf=ccf['b052'], ccf24=ccf['b24'], rms=rms,
                tamlik=tam, meta=meta)


def cif_dosya_adi(x):
    return f"{x['ist']}_{x['ay']}{'_b13' if x['rol'] == 'bilgi13' else ''}.npz"


def cif_yaz(depo, x, d):
    yol = os.path.join(depo, 'cif', cif_dosya_adi(x))
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol + '.tmp', 'wb') as f:
        np.savez(f, gun=d['gun'], ccf=d['ccf'], ccf24=d['ccf24'], rms=d['rms'], tamlik=d['tamlik'],
                 meta=np.array(json.dumps(d['meta'], ensure_ascii=False, sort_keys=True)))
    os.replace(yol + '.tmp', yol)
    return yol, sha_dosya(yol)


def cif_oku(yol, sha=None):
    if sha is not None and sha_dosya(yol) != sha: raise SystemExit(f'ÇİF deposu sha256 uyuşmuyor: {yol}; durdu')
    with np.load(yol, allow_pickle=False) as z:
        d = {k: z[k] for k in z.files}
    d['meta'] = json.loads(str(d['meta']))
    return d


# ---------------------------------------------------------------- durum ve bütçe
def durum_yollari(depo):
    return dict(gunluk=os.path.join(depo, 'istek_gunlugu.jsonl'), butce=os.path.join(depo, 'indirme_durum.json'))


def son_durum(rows):
    """k -> geçerli satır (kesin kodlu son satır, yoksa son satır) ve deneme sayısı (süre kesmesi deneme sayılmaz)."""
    d, n = {}, collections.Counter()
    for x in rows:
        if x.get('sure_kesti'): continue
        n[x['k']] += 1
        if x['k'] not in d or x['kod'] in KESIN or d[x['k']]['kod'] not in KESIN: d[x['k']] = x
    return d, n


def butce_oku(depo):
    y = durum_yollari(depo)['butce']
    if os.path.exists(y): return json.load(open(y, encoding='utf-8'))
    return dict(durum='baslamadi', ilk_istek=None, etkin_sn=0.0, isler=[], tur=False)


def butce_asildi(B, is_bas):
    if B['ilk_istek'] is None: return None
    etkin = B['etkin_sn'] + (simdi() - is_bas)
    takvim = simdi() - B['ilk_istek']
    if etkin >= BUTCE_ETKIN_SN: return f'etkin süre {etkin / 86400:.2f} gün ≥ 21'
    if takvim >= BUTCE_TAKVIM_SN: return f'takvim {takvim / 86400:.2f} gün ≥ 42'
    return None


def kuyruk(isler, d, n, tur):
    """Tamamlanmamış işler: kesin kodsuz ve deneme < 2 (tur açıldıysa < 3)."""
    sinir = DENEME_MAX + (1 if tur else 0)
    return [x for x in isler if not (x['k'] in d and (d[x['k']]['kod'] in KESIN or n[x['k']] >= sinir))]


def ozet(isler, depo):
    d, n = son_durum(satirlar(durum_yollari(depo)['gunluk']))
    kes = sum(1 for x in isler if x['k'] in d and d[x['k']]['kod'] in KESIN)
    bas = sum(1 for x in isler if x['k'] in d and d[x['k']]['kod'] not in KESIN)
    return dict(is_=len(isler), kesin=kes, kesin_olmayan=bas, bekleyen=len(isler) - kes - bas)


# ---------------------------------------------------------------- indir
def ag_onayi():
    if '--ag-onay' not in sys.argv:
        print('Ağ kipi --ag-onay bayrağı olmadan çalışmaz; hiçbir istek atılmadı.'); sys.exit(2)


def indir(ob, depo, yerel, sure=None, taban=DS, G=None):
    """Bir iş (≤ sure_sn). Kaldığı yerden sürer. Dönen: durum özeti."""
    is_bas = simdi()
    s = SURE_MAX if sure is None else float(sure)
    if not 0 < s <= SURE_MAX: raise SystemExit(f'sure_sn en çok {SURE_MAX:.0f}; durdu')
    bitis = is_bas + s
    G = G or girdiler(ob)
    if G['kademe'] == 'veri yok (aktarım hızı)': raise SystemExit('hüküm "veri yok (aktarım hızı)": indirme yapılmaz')
    if G['S0']['dolu_yer_pencere'] < 30: raise SystemExit('dolu yer-penceresi < 30: indirme yapılmaz (§4.3)')
    isler = plan(G)
    os.makedirs(depo, exist_ok=True); os.makedirs(yerel, exist_ok=True)
    if os.path.realpath(yerel) == os.path.realpath(depo): raise SystemExit('yerel ham dizini depoyla aynı olamaz')
    for f in os.listdir(yerel):                                      # önceki işten kalmış ham dosyalar
        if f.endswith('.mseed') or f.endswith('.part'): os.remove(os.path.join(yerel, f))
    Y = durum_yollari(depo); B = butce_oku(depo)
    if B['durum'] in ('bitti', 'kesildi'):
        print(f"indirme {B['durum']}; yeni istek yok"); return B
    B['durum'] = 'suruyor'; B['isler'].append(dict(bas=is_bas, son=None))
    akis = Akis(); atilan = 0; gecen = []
    g = ekle_ac(Y['gunluk'])

    def kapat(neden):
        B['etkin_sn'] += simdi() - is_bas; B['isler'][-1]['son'] = simdi(); B['isler'][-1]['neden'] = neden
        yaz_json(Y['butce'], B)

    try:
        while True:
            d, n = son_durum(satirlar(Y['gunluk']))
            Q = kuyruk(isler, d, n, B['tur'])
            if not Q:
                bas = [x for x in isler if d[x['k']]['kod'] not in KESIN]
                if bas and not B['tur'] and len(bas) / len(isler) > TUR_ESIK:
                    B['tur'] = True; yaz_json(Y['butce'], B); print(f'kesin olmayan oran {len(bas)}/{len(isler)} > %5: tek yeniden deneme turu')
                    continue
                B['durum'] = 'bitti'; B['bitis'] = simdi(); kapat('bitti')
                print('indirme bitti', ozet(isler, depo)); return B
            x = Q[0]
            neden = butce_asildi(B, is_bas)
            if neden:
                B['durum'] = 'kesildi'; B['kesme_nedeni'] = neden; B['bitis'] = simdi(); kapat('bütçe')
                print('BÜTÇE DOLDU:', neden, '— indirme kalıcı olarak durdu (§5.3 kesik koşu)'); return B
            hiz = (sum(r['bayt'] for r in gecen) / max(1e-9, sum(r['sn'] for r in gecen))) if gecen else None
            if hiz is None and G['hiz'].get('v_medyan_KiBs'): hiz = G['hiz']['v_medyan_KiBs'] * 1024
            tahmin = len(x['gunler']) * H_SAAT * 3600 * 100 * 3 * BAYT_ORNEK / (hiz or 40 * 1024) + 60
            if bitis - simdi() < 1.25 * tahmin:
                kapat('süre'); print('süre doldu; temiz çıkış (sürdürülebilir)', ozet(isler, depo)); return B
            son_utc, son_gun = istek_bitisi(x, G['konum'])
            kor_denet(son_utc, son_gun, x['rol'])                     # bağlantıdan ÖNCE
            if B['ilk_istek'] is None: B['ilk_istek'] = simdi(); yaz_json(Y['butce'], B)
            ham = os.path.join(yerel, x['k'].replace('|', '_') + '.mseed')
            if G['bicim'] == 'GET':
                kod, nb, sh, sn, kesti, ra = 200, 0, hashlib.sha256(), 0.0, False, None
                kods = []
                with open(ham + '.birlesik', 'wb') as out:
                    for gg in x['gunler']:
                        akis.once(bitis)
                        kj, nj, shj, snj, kj_k, raj = _akit(get_url(x, G['konum'], gg, taban), None, ham, bitis)
                        akis.sonra(kj, raj); kods.append(kj); nb += nj; sn += snj; sh.update(shj.encode())
                        if kj == 200 and os.path.exists(ham):
                            out.write(open(ham, 'rb').read()); os.remove(ham)
                        if kj_k: kesti = True; break
                kk = [c for c in kods if c not in KESIN]
                kod = kk[0] if kk else (200 if 200 in kods else kods[0])
                sh = sh.hexdigest()
                if kod == 200 and not kesti and os.path.getsize(ham + '.birlesik') > 0: os.replace(ham + '.birlesik', ham)
                else: os.remove(ham + '.birlesik')
            else:
                akis.once(bitis)
                kod, nb, sh, sn, kesti, ra = _akit(taban, post_govde(x, G['konum']), ham, bitis)
                akis.sonra(kod, ra)
            atilan += 1
            satir = dict(k=x['k'], kod=kod, bayt=nb, ham_sha256=sh, sn=sn, sure_kesti=kesti, deneme=n[x['k']] + 1,
                         t=round(simdi(), 1), rol=x['rol'], gun=len(x['gunler']))
            if kod == 200 and not kesti and nb > 0:
                gecen.append(dict(bayt=nb, sn=sn))
                t1 = time.monotonic()
                try:
                    r = isle_istasyon_ay(ham, x, G['konum'])
                    yol, csha = cif_yaz(depo, x, r)
                    satir.update(cif=os.path.basename(yol), cif_sha256=csha, islem_sn=round(time.monotonic() - t1, 2),
                                 kabul_saat=int(np.sum(~np.isnan(r['ccf'][:, :, 0, 0]))))
                except Exception as e:                               # biçim hatası: sunucu yanıtladı, veri kullanılamaz
                    satir.update(cif=None, bicim_hata=f'{type(e).__name__}: {e}'[:300])
                finally:
                    if os.path.exists(ham): os.remove(ham)       # ham veri silinir (§5.5)
            elif os.path.exists(ham): os.remove(ham)
            g.write(json.dumps(satir, sort_keys=True, ensure_ascii=False) + '\n'); g.flush(); os.fsync(g.fileno())
            if kesti:
                kapat('süre (istek kesildi)'); print('süre doldu (istek kesildi; sonraki işte yeniden atılır)'); return B
    finally:
        g.close()


def plan_yazdir(ob, depo):
    G = girdiler(ob); P = plan(G)
    gun = sum(len(x['gunler']) for x in P)
    print(json.dumps(dict(kademe=G['kademe'], bicim=G['bicim'], is_=len(P), istasyon_gun=gun,
                          GB_1_3=round(gun * H_SAAT * 3600 * 100 * 3 * BAYT_ORNEK / 1e9, 1),
                          ilk=P[0]['k'] if P else None, son=P[-1]['k'] if P else None), ensure_ascii=False))
    return P


if __name__ == '__main__':
    k = sys.argv[1] if len(sys.argv) > 1 else ''
    arg = [a for a in sys.argv[2:] if not a.startswith('--')]
    if k == 'plan': plan_yazdir(arg[0], arg[1] if len(arg) > 1 else DEPO_VARSAYILAN)
    elif k == 'indir':
        ag_onayi()
        indir(arg[0], arg[1], arg[2], float(arg[3]) if len(arg) > 3 else None)
    else: print(__doc__)
