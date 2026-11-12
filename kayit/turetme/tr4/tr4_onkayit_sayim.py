#!/usr/bin/env python3
"""TR-4 ön kayıt taslağı (sürüm 1): olaysız pencere tanımı, istasyon-pencere sayımı, kapı ve indirme hacmi.

Dalga formu OKUNMAZ ve İNDİRİLMEZ. Yalnız mevcut sayım dosyaları kullanılır:
  <ham>  TR-5 üstveri dizini: marmara_fed_kanal.txt (fedcatalog, kutu 40,0-41,6 K / 26,5-30,5 D, BHZ/HHZ)
         [arşiv: /mnt/project-files/turetme/tr5b-ham/tr5_ham_ustveri_2026-11-12.tar.gz, ham/]
  <dol>  TR-5 Ek 1-2 doluluk önbelleği onbellek.jsonl (ayın 15'i 12:00-12:01 UTC, cha=BHZ,HHZ, loc=*; 2012-01..2023-12)
         [aynı arşiv, doluluk/onbellek.jsonl; sha256 ce4fe524...]
  <m5>   ComCat M>=5,0, z<=70 km, 1990-2025 dizini (m5_*.csv; TR-5b §2.6 kataloğu)
         [arşiv: /mnt/project-files/turetme/tr5b-ham/tr5b_kat_2026-11-12.tar.gz]

Tanımlar `kayit/onkayit/TR-4_marmara-hiz-tabani_ONKAYIT.md` §2-§3'tedir. Kısaca:
  - Pencere TR-5b §3.5'in aynısıdır: [T-1095, T-8], dilimler A/B/C; T yıllık 1 Ocak.
  - Kanal kodu pencere içinde değişmez (TR-5b §3.1); KO'da 2013-11-08'de BH -> HH geçişi olduğu için T >= 2017.
  - Aygıt kuralı (TR-5b §2.5) burada yalnız Z üstverisiyle önizlenir (yatay üstveri aşama 0'da).
  - Olaysızlık (istasyon koordinatına göre; ana): [T - 5 yıl, T + 1 yıl) içinde 150 km'de M>=6 (z<=40), 300 km'de
    M>=7 (z<=70), 1000 km'de M>=8 (z<=70) yok. Değişkeler bilgi satırıdır.
  - M>=5 maskesi (TR-5b §2.6, zincirin parçası): istasyona <= 50 km M>=5,0 (z<=70) olaydan sonra [t, t+59] günleri.
  - Z ay doluluğu `dolu_ana` (TR-5b): ayların >= %80'i var ve en uzun ardışık boş ay <= 3.

Kullanım: python3 -I -B tr4_onkayit_sayim.py <ham> <dol> <m5>
Çıktı (bu dizine): tr4_onkayit_sayim.json, tr4_pencereler.csv
"""
import collections, csv, datetime as dt, glob, hashlib, json, math, os, re, sys
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
TD = dt.timedelta
HAM, DOL, M5 = sys.argv[1:4]
SON = dt.date(2025, 12, 31)                 # veri sınırı; 2026 hiçbir amaçla kullanılmaz
KUTU = (40.0, 41.6, 26.5, 30.5)
TABAN, KORUMA = 1095, 8                     # TR-5b §3.5: [T-1095, T-8]
TLER = [dt.date(y, 1, 1) for y in range(2015, 2026)]
ANA_T = [dt.date(y, 1, 1) for y in range(2017, 2025)]
BOSLUK_GUN = 30
DOLU = {'ana': (0.80, 3), 'gevsek': (0.60, 6), 'siki': (0.90, 2)}
M5_R, M5_GUN = 50.0, 60
KAPI_IST, KAPI_ARA_YIL = 10, 3              # >= 10 dolu istasyon, >= 2 örtüşmeyen epokta (T farkı >= 3 yıl)
BAYT_ORNEK, SPS, BILESEN = 1.3, 100.0, 3     # TR-5 §5.1 ölçümü (KO HHZ 1,30 bayt/örnek); KO >= 2013-11-08 yalnız HH 100 sps
HIZLAR_KiBs = {'TR-7 §4 (1 saat, 2026-11-11)': 23.0, 'TR-5 §4.1 (1 gün, 2026-11-12)': 40.0,
               'TR-7 varlık (1 saat, tek akış)': 341.3, 'TR-7 varlık (2 paralel akış, toplam)': 632.5}
ISTEK_EK_SN = 3.0                           # KOERI'de istekler arası >= 2 sn + ≈ 1 sn gecikme (Ek 1 medyanı 0,98 sn)


def yil(n): return TD(days=int(math.floor(n * 365.25)))


def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(np.radians, (la1, lo1, la2, lo2))
    a = np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def sha(y):
    h = hashlib.sha256()
    with open(y, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def ay_listesi(a, b):                       # tr5b_asama0.ay_listesi ile aynı (ayın 15'i pencerede)
    out = []; y, m = a.year, a.month
    while (y, m) <= (b.year, b.month):
        g = dt.date(y, m, 15)
        if a <= g <= b: out.append(f'{y:04d}-{m:02d}')
        m += 1
        if m == 13: y, m = y + 1, 1
    return out


# ---------------------------------------------------------------- üstveri (yalnız Z; KO, kutu)
EP = collections.defaultdict(list); KONUM = {}
fed = os.path.join(HAM, 'marmara_fed_kanal.txt')
for l in open(fed, encoding='utf-8', errors='replace'):
    if l.startswith('#') or '|' not in l: continue
    p = l.rstrip('\n').split('|')
    if len(p) < 17 or p[0] != 'KO' or p[3] not in ('BHZ', 'HHZ'): continue
    la, lo = float(p[4]), float(p[5])
    if not (KUTU[0] <= la <= KUTU[1] and KUTU[2] <= lo <= KUTU[3]): continue
    b = dt.date.fromisoformat(p[15][:10]); e = min(dt.date.fromisoformat(p[16][:10]) if p[16].strip() else SON, SON)
    sens = re.sub(r'S/N[:#\s]*\S+', '', p[10]).strip().lower()
    EP[('KO.' + p[1], p[2].strip(), p[3])].append((b, e, sens, p[8].strip(), p[9].strip(), float(p[14])))
    KONUM['KO.' + p[1]] = (la, lo)
ISTASYONLAR = sorted(KONUM)
YER_KM = 1.0                                # TR-5b §2.2: 1 km içindeki istasyonlar tek yer


def _yerler():
    ana = {s: s for s in ISTASYONLAR}
    def bul(x):
        while ana[x] != x: x = ana[x]
        return x
    for i, s in enumerate(ISTASYONLAR):
        for t in ISTASYONLAR[i + 1:]:
            if float(hav(*KONUM[s], *KONUM[t])) <= YER_KM: ana[bul(t)] = bul(s)
    return {s: bul(s) for s in ISTASYONLAR}


def kapsar(ep, a, b):                       # tr5b_asama0.kapsar ile aynı
    iv = sorted((x[0], x[1]) for x in ep); m = []
    for x, y in iv:
        if m and (x - m[-1][1]).days <= BOSLUK_GUN: m[-1][1] = max(m[-1][1], y)
        else: m.append([x, y])
    return any(x <= a and y >= b for x, y in m)


def aygit(ep, a, b):                        # tr5b_asama0.aygit ile aynı
    L = sorted(set((x[0], x[2], x[3], x[4]) for x in ep))
    return any(a < y[0] <= b and x[1:] != y[1:] for x, y in zip(L, L[1:]))


def kanal_sec_Z(s, a, b):
    """TR-5b §3.1 sırası (BH, sonra HH; konum '', 00, 10), yalnız Z ile: (konum, bant, aygıt_bozuk) ya da None."""
    locs = sorted({k[1] for k in EP if k[0] == s}, key=lambda l: ({'': 0, '00': 1, '10': 2}.get(l, 3), l))
    for bant in ('BH', 'HH'):
        for loc in locs:
            ep = EP.get((s, loc, bant + 'Z'))
            if ep and kapsar(ep, a, b): return loc, bant, aygit(ep, a, b), ep[0][5]
    return None


# ---------------------------------------------------------------- katalog (M>=5, z<=70, 1990-2025)
KAT = []
for f in sorted(glob.glob(os.path.join(M5, 'm5_*.csv'))):
    for r in csv.DictReader(open(f)):
        if r['type'] != 'earthquake': continue
        t = dt.datetime.fromisoformat(r['time'].replace('Z', '')).date()
        if t > SON: continue
        KAT.append((t, float(r['latitude']), float(r['longitude']), float(r['depth'] or 0), float(r['mag']), r['id'], r['place']))
KT = np.array([x[0].toordinal() for x in KAT]); KLA = np.array([x[1] for x in KAT]); KLO = np.array([x[2] for x in KAT])
KZ = np.array([x[3] for x in KAT]); KM = np.array([x[4] for x in KAT])
KAT_SHA = {os.path.basename(f): sha(f) for f in sorted(glob.glob(os.path.join(M5, 'm5_*.csv')))}

KURAL = {   # ad: ([(M_min, z_max, R_km)], önce, sonra, ek)
    'ana': ([(6.0, 40, 150), (7.0, 70, 300), (8.0, 70, 1000)], yil(5), yil(1), None),
    'ileri_2y': ([(6.0, 40, 150), (7.0, 70, 300), (8.0, 70, 1000)], yil(5), yil(2), None),
    'M7_500': ([(6.0, 40, 150), (7.0, 70, 500), (8.0, 70, 1000)], yil(5), yil(1), None),
    'M5_50_pencere': ([(6.0, 40, 150), (7.0, 70, 300), (8.0, 70, 1000)], yil(5), yil(1), ('M5', 5.0, 70, 50, 0, 0)),
    'M55_100_genis': ([(6.0, 40, 150), (7.0, 70, 300), (8.0, 70, 1000)], yil(5), yil(1), ('M55', 5.5, 70, 100, 365, 365)),
}


def olaylar_yakin(la, lo, a, b, M, z, R):
    sec = (KT >= a.toordinal()) & (KT < b.toordinal()) & (KM >= M) & (KZ <= z)
    if not sec.any(): return []
    d = hav(la, lo, KLA[sec], KLO[sec]); ix = np.nonzero(sec)[0][d <= R]
    return [KAT[j][5] for j in ix]


def sakin(s, T, kural):
    la, lo = KONUM[s]; esik, once, sonra, ek = KURAL[kural]
    neden = []
    for M, z, R in esik:
        neden += olaylar_yakin(la, lo, T - once, T + sonra, M, z, R)
    if ek:
        _, M, z, R, gon, gsn = ek
        a, b = T - TD(days=TABAN) - TD(days=gon), T - TD(days=KORUMA) + TD(days=1 + gsn)
        neden += olaylar_yakin(la, lo, a, b, M, z, R)
    return sorted(set(neden))


def maske(s, a, b):
    """TR-5b §2.6: istasyona <= 50 km M>=5 (z<=70) olaydan sonra [t, t+59] günleri; pencere [a, b] içinde."""
    la, lo = KONUM[s]
    sec = (KT >= (a - TD(days=M5_GUN)).toordinal()) & (KT <= b.toordinal()) & (KM >= 5.0) & (KZ <= 70)
    gun = set(); ids = []
    if sec.any():
        d = hav(la, lo, KLA[sec], KLO[sec])
        for j in np.nonzero(sec)[0][d <= M5_R]:
            ids.append(KAT[j][5])
            for x in range(KT[j], KT[j] + M5_GUN):
                if a.toordinal() <= x <= b.toordinal(): gun.add(x)
    return gun, sorted(ids)


YER = None   # aşağıda (hav tanımından sonra) kurulur

# ---------------------------------------------------------------- doluluk (Z ay yoklaması)
AY = {}
for l in open(DOL):
    try: r = json.loads(l)
    except ValueError: continue
    if not r['k'].startswith('KO.'): continue
    s, ay = r['k'].rsplit('.', 1)
    var = r['kod'] == 200 and r['bayt'] > 0
    AY[(s, ay)] = 'var' if var else ('bos' if r['kod'] in (200, 204, 404) else ('kisitli' if r['kod'] in (401, 403) else 'hata'))
YOKLANAN = sorted({s for s, _ in AY} & set(ISTASYONLAR))
YER = _yerler()
COK_ISTASYONLU_YER = {y: sorted(s for s in ISTASYONLAR if YER[s] == y) for y in set(YER.values())
                      if sum(1 for s in ISTASYONLAR if YER[s] == y) > 1}


def doluluk(s, a, b):
    ays = ay_listesi(a, b); d = [AY.get((s, m)) for m in ays]
    if any(x is None for x in d): return dict(durum='yoklanmadi', n=len(ays), yoklanan=sum(x is not None for x in d))
    var = [x == 'var' for x in d]; en = cur = 0
    for v in var:
        cur = 0 if v else cur + 1; en = max(en, cur)
    oran = sum(var) / len(var)
    return dict(durum='yoklandi', n=len(ays), oran=round(oran, 3), en_uzun_bosluk=en,
                **{k: (oran >= o and en <= g) for k, (o, g) in DOLU.items()})


# ---------------------------------------------------------------- istasyon-pencereler
satir = []
for s in ISTASYONLAR:
    for T in TLER:
        a, b = T - TD(days=TABAN), T - TD(days=KORUMA)
        r = dict(ist=s, T=T.isoformat(), a=a.isoformat(), b=b.isoformat())
        k = kanal_sec_Z(s, a, b)
        r['kanal'] = None if k is None else f'{k[0] or "--"}.{k[1]}Z'
        r['sps'] = None if k is None else k[3]
        r['aygit_Z_bozuk'] = None if k is None else k[2]
        for kural in KURAL: r['sakin_' + kural] = not sakin(s, T, kural)
        r['sakin_ana_neden'] = ';'.join(sakin(s, T, 'ana'))
        g, ids = maske(s, a, b); r['maske_gun'] = len(g); r['maske_olay'] = ';'.join(ids)
        dl = doluluk(s, a, b); r['doluluk'] = dl['durum']; r['ay_oran'] = dl.get('oran'); r['en_uzun_bosluk'] = dl.get('en_uzun_bosluk')
        for kk in DOLU: r['dolu_' + kk] = dl.get(kk)
        r['uygun_ustveri'] = k is not None and not k[2] and r['sakin_ana']
        r['aday_yoklanmamis'] = r['uygun_ustveri'] and dl['durum'] == 'yoklanmadi'
        for kk in DOLU: r['DOLU_' + kk] = bool(r['uygun_ustveri'] and dl.get(kk))
        r['ana_T'] = T in ANA_T
        r['yer'] = YER[s]
        satir.append(r)


def temsilci(anahtar, kural_sakin='ana'):
    """Her yer için SABİT tek temsilci (bütün T'lerde aynı istasyon): ölçütü sağlayan ana-T pencere sayısı en çok olan,
    eşitlikte ay oranı ortalaması yüksek olan, sonra kod sırası. Temsilcinin ölçütü sağladığı (yer, T)'ler sayılır."""
    ok = [r for r in satir if r['ana_T'] and r[anahtar] and r['sakin_' + kural_sakin]]
    puan = collections.defaultdict(lambda: [0, 0.0])
    for r in ok:
        puan[r['ist']][0] += 1; puan[r['ist']][1] += (r['ay_oran'] or 0)
    tems = {}
    for st, (n, so) in puan.items():
        y = YER[st]; o = (-n, -so / n, st)
        if y not in tems or o < tems[y][0]: tems[y] = (o, st)
    return {(YER[r['ist']], r['T']): r['ist'] for r in ok if tems[YER[r['ist']]][1] == r['ist']}


def kapi(sayi):
    """sayi: {T(yıl): dolu istasyon}. >= KAPI_IST istasyonlu ve aralarında >= KAPI_ARA_YIL yıl olan iki T var mı."""
    iyi = sorted(y for y, n in sayi.items() if n >= KAPI_IST)
    ciftler = [(x, y) for i, x in enumerate(iyi) for y in iyi[i + 1:] if y - x >= KAPI_ARA_YIL]
    return dict(iyi_epok=iyi, ortusmeyen_cift=ciftler, gecti=bool(ciftler))


def ozet(anahtar, kural_sakin='ana', Tset=ANA_T):
    """Sayım YER düzeyindedir (1 km içindeki istasyonlar tek yer; temsilci tek)."""
    tm = temsilci(anahtar, kural_sakin)
    sayi = {}; ist = set(); n = 0; ham = {}
    for T in Tset:
        x = [v for (y, t), v in tm.items() if t == T.isoformat()]   # yalnız ana_T içinde
        sayi[T.year] = len(x); n += len(x); ist |= set(x)
        ham[T.year] = sum(1 for r in satir if r['T'] == T.isoformat() and r[anahtar] and r['sakin_' + kural_sakin])
    return dict(epok=sayi, yer_pencere=n, yer=len({YER[s] for s in ist}), istasyonlar=sorted(ist),
                istasyon_duzeyi_epok=ham, kapi=kapi(sayi))


O = {}
for kk in DOLU: O['Z_dolu_' + kk] = ozet('DOLU_' + kk)
O['ustveri_uygun'] = ozet('uygun_ustveri')
for kural in KURAL:
    if kural != 'ana': O['Z_dolu_ana__' + kural] = ozet('DOLU_ana', kural)
O['Z_dolu_ana__ortusmeyen_2018_2021_2024'] = ozet('DOLU_ana', 'ana', [dt.date(2018, 1, 1), dt.date(2021, 1, 1), dt.date(2024, 1, 1)])
O['Z_dolu_ana__ortusmeyen_2017_2020_2023'] = ozet('DOLU_ana', 'ana', [dt.date(2017, 1, 1), dt.date(2020, 1, 1), dt.date(2023, 1, 1)])

# eleme nedenleri (ana T, istasyon-pencere)
neden = collections.Counter()
for r in satir:
    if not r['ana_T']: continue
    if r['kanal'] is None: neden['kanal kapsamı yok (üstveri)'] += 1
    elif r['aygit_Z_bozuk']: neden['aygıt değişimi (Z önizleme)'] += 1
    elif not r['sakin_ana']: neden['olaysızlık (ana)'] += 1
    elif r['doluluk'] == 'yoklanmadi': neden['Z ay yoklaması yok (aday)'] += 1
    elif not r['dolu_ana']: neden['Z ay doluluğu (dolu_ana değil)'] += 1
    else: neden['dolu'] += 1
olay_neden = collections.Counter()
for r in satir:
    if r['ana_T'] and r['kanal'] is not None and not r['aygit_Z_bozuk'] and not r['sakin_ana']:
        for e in r['sakin_ana_neden'].split(';'): olay_neden[e] += 1

# ---------------------------------------------------------------- olaylar: uzaklıklar
OLAY = {x[5]: x for x in KAT}
ANILAN = ['usb000r2hc', 'us20009ly0', 'us70005lkl', 'us7000c7y0', 'us7000irp8', 'us7000lg2l', 'us7000pufs', 'us6000qznb']
uz = {}
for e in ANILAN:
    if e not in OLAY: continue
    t, la, lo, z, M, _, yer = OLAY[e]
    uz[e] = dict(t=t.isoformat(), M=M, z=z, yer=yer, L_km=round(10 ** (-2.44 + 0.59 * M), 1),
                 istasyon_km={s: round(float(hav(la, lo, *KONUM[s])), 1) for s in ISTASYONLAR})

# ---------------------------------------------------------------- hacim ve süre (örnekleme tasarımları)
TASARIM = {   # ad: (ayda gün bloğu: 1..d; None = her gün, saat/gün) — tr4_guc.py ile aynı adlar
    'A_her_gun_4s': (None, 4), 'H_her_gun_3s': (None, 3), 'B_her_gun_2s': (None, 2),
    'C_20g_4s': (20, 4), 'G_20g_3s': (20, 3), 'D_20g_2s': (20, 2), 'F_16g_4s': (16, 4), 'E_16g_2s': (16, 2),
}
GUN_BAYT = lambda h: h * 3600 * SPS * BILESEN * BAYT_ORNEK


def gunler_kumesi(pencereler):
    g = set()
    for a, b in pencereler:
        x = a
        while x <= b: g.add(x); x += TD(days=1)
    return g


def hacim(anahtar='DOLU_ana', kural='ana', Tset=ANA_T, ist_sec=None):
    out = {}
    pen = collections.defaultdict(list)
    tm = temsilci(anahtar, kural)
    for r in satir:
        if r['T'] in {T.isoformat() for T in Tset} and tm.get((YER[r['ist']], r['T'])) == r['ist']:
            if ist_sec and r['ist'] not in ist_sec: continue
            pen[r['ist']].append((dt.date.fromisoformat(r['a']), dt.date.fromisoformat(r['b'])))
    G = {s: gunler_kumesi(v) for s, v in pen.items()}
    for ad, (d, h) in TASARIM.items():
        n_gun = sum(sum(1 for x in g if d is None or x.day <= d) for g in G.values())
        n_ay = sum(len({(x.year, x.month) for x in g}) for g in G.values())
        bayt = n_gun * GUN_BAYT(h)
        sure = {k: round((bayt / (v * 1024) + n_ay * ISTEK_EK_SN) / 86400, 2) for k, v in HIZLAR_KiBs.items()}
        out[ad] = dict(istasyon=len(G), istasyon_gun=n_gun, istek_ay=n_ay, GB=round(bayt / 1e9, 1), gun_sure=sure)
    return out


H = {'ana (Z dolu, T 2017-2024)': hacim(),
     'ana, örtüşmeyen T 2018/2021/2024': hacim(Tset=[dt.date(2018, 1, 1), dt.date(2021, 1, 1), dt.date(2024, 1, 1)]),
     'ana, yalnız T 2021-2024': hacim(Tset=[dt.date(y, 1, 1) for y in range(2021, 2025)])}
# hedef: 1 hafta indirme için gereken hız (KiB/s)
for ad, v in H['ana (Z dolu, T 2017-2024)'].items():
    v['bir_hafta_icin_KiBs'] = round(v['GB'] * 1e9 / 1024 / (7 * 86400 - v['istek_ay'] * ISTEK_EK_SN), 0)

# PK 2025 (bilgi): 50 km içindeki istasyonlar; [T-69, T+30] her gün + [T-400, T-70] örnekli
PK = {}
if 'us7000pufs' in OLAY:
    t0 = OLAY['us7000pufs'][0]; la, lo = OLAY['us7000pufs'][1:3]
    for s in ISTASYONLAR:
        dkm = float(hav(la, lo, *KONUM[s]))
        if dkm > 50: continue
        k = kanal_sec_Z(s, t0 - TD(days=400), t0 + TD(days=30))
        PK[s] = dict(km=round(dkm, 1), kanal_kapsar=k is not None, aygit_Z_bozuk=None if k is None else k[2],
                     ilk_epok=min(x[0] for kk, v in EP.items() if kk[0] == s for x in v).isoformat())
    n_s = sum(1 for v in PK.values() if v['kanal_kapsar'] and not v['aygit_Z_bozuk'])
    PK_hacim = {ad: round(n_s * (100 + (331 if d is None else 331 * d / 30.44)) * GUN_BAYT(h) / 1e9, 2)
                for ad, (d, h) in TASARIM.items()}
else:
    PK_hacim = {}

# ---------------------------------------------------------------- aşama 0 istek kestirimi
dolu_ana = [r for r in satir if r['ana_T'] and r['DOLU_ana']]
aday = [r for r in satir if r['ana_T'] and r['aday_yoklanmamis']]
yatay = set()
for r in dolu_ana + aday:
    T = dt.date.fromisoformat(r['T'])
    for a_, b_ in ((T - TD(days=1095), T - TD(days=731)), (T - TD(days=730), T - TD(days=366)), (T - TD(days=365), T - TD(days=8))):
        g = a_ + (b_ - a_) / 2; yatay.add((r['ist'], f'{g.year:04d}-{g.month:02d}'))
z_aday = {(r['ist'], m) for r in aday for m in ay_listesi(dt.date.fromisoformat(r['a']), dt.date.fromisoformat(r['b']))}
pk_ay = {(s, f'{y:04d}-{m:02d}') for s in PK for y in (2024, 2025) for m in range(1, 13) if dt.date(y, m, 15) <= dt.date(2025, 5, 31)
         and dt.date(y, m, 15) >= dt.date(2024, 3, 1)}
asama0 = dict(ustveri_istasyon=len({r['ist'] for r in dolu_ana + aday} | set(PK)),
              yatay_istek=2 * len(yatay), z_aday_istek=len(z_aday), pk_z_istek=len(pk_ay), pk_yatay_istek=2 * len(pk_ay),
              hiz_denemesi_istek=24)
asama0['toplam_istek'] = sum(v for k, v in asama0.items())
asama0['sure_saat_3sn'] = round(asama0['toplam_istek'] * ISTEK_EK_SN / 3600, 2)

# ---------------------------------------------------------------- yaz
with open(os.path.join(BURASI, 'tr4_pencereler.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(satir[0].keys())); w.writeheader(); w.writerows(satir)
out = dict(tarih='2026-11-12', girdi_sha256=dict(marmara_fed_kanal=sha(fed), doluluk_onbellek=sha(DOL), **KAT_SHA),
           tanim=dict(pencere='[T-1095, T-8]', T='yıllık 1 Ocak', ana_T=[T.isoformat() for T in ANA_T],
                      olaysizlik={k: dict(esik=v[0], once_gun=v[1].days, sonra_gun=v[2].days, ek=v[3]) for k, v in KURAL.items()},
                      maske=dict(M=5.0, z=70, R_km=M5_R, gun=M5_GUN), dolu=DOLU, kapi=dict(istasyon=KAPI_IST, epok_arasi_yil=KAPI_ARA_YIL, epok=2)),
           istasyon_sayisi_kutu=len(ISTASYONLAR), yoklanan_istasyon=len(YOKLANAN), cok_istasyonlu_yer=COK_ISTASYONLU_YER,
           ozet=O, eleme_nedeni_ana_T=dict(neden), olaysizlik_neden_olay=dict(olay_neden.most_common()),
           olay_uzaklik=uz, pk2025_istasyon=PK, pk2025_hacim_GB=PK_hacim, hacim=H, asama0_istek=asama0,
           hiz_KiBs=HIZLAR_KiBs, bayt_ornek=BAYT_ORNEK)
json.dump(out, open(os.path.join(BURASI, 'tr4_onkayit_sayim.json'), 'w'), ensure_ascii=False, indent=1)

print('istasyon (kutu, KO):', len(ISTASYONLAR), 'yoklanan:', len(YOKLANAN), 'çok istasyonlu yer:', COK_ISTASYONLU_YER)
for k, v in O.items():
    print(f"{k:45s} yer/epok={v['epok']} N={v['yer_pencere']} yer={v['yer']} kapı={v['kapi']['gecti']} {v['kapi']['ortusmeyen_cift'][:4]} (ist düzeyi {v['istasyon_duzeyi_epok']})")
print('eleme:', dict(neden)); print('olay:', dict(olay_neden.most_common(10)))
for k, v in H.items():
    print(k)
    for ad, x in v.items(): print('  ', ad, x)
print('PK2025:', PK, PK_hacim); print('aşama 0:', asama0)
