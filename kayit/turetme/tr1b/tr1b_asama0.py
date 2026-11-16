#!/usr/bin/env python3
"""TR-1b sürüm 2, aşama 0: YALNIZ ÜSTVERİYLE sayım (hiçbir tenv3 ya da başka konum zaman serisi okunmaz).

Kurallar: kayit/onkayit/TR-1b_sinirli-kosu_ONKAYIT.md sürüm 2, §2 ve §7. Okuyucular ve istasyon uygunluğu
kayit/turetme/tr11/sayim_ustveri.py'den uyarlandı (o betik modül düzeyinde koştuğu için içe aktarılamıyor).

Girdi (depo dışı, önbellek; sha256 denetlenir):
  <ngl>/DataHoldings.txt, <ngl>/steps.txt            NGL üstverisi (11 Kasım 2026 indirmesi; TR-1/TR-11 ile aynı dosya)
  <ngl>/ev30.csv                                     ComCat 2000-01-01..2026-01-01T00:00:00, M>=6,5, derinlik<=30 (olaylar)
  <ngl>/ev70.csv, <ngl>/ev70_pre.csv                 ComCat M>=6,5, derinlik<=70, 2000-2025 ve 1985-1999 (Ş2, Ş3)
  <tr2>/m6_havuz.csv                                 ComCat M>=6,0, derinlik<=40, 1976-2025 (Ş1; TR-2 indirmesi)
  <tr2>/mekanizma.jsonl, birincil_aday*.csv          mekanizma (yalnız bileşim satırı; M6,0-7,2, z<=25)
Çıktı: <cikti_dizini>/tr1b_asama0_liste.json (dondurulan olay/küme listesi), tr1b_asama0_ozet.json (sayılar, sha256).
Kullanım: python3 -I -B tr1b_asama0.py <ngl> <tr2> <cikti_dizini>
"""
import csv, collections, datetime as dt, hashlib, json, math, os, sys
import numpy as np

sys.dont_write_bytecode = True
NGL, TR2, CIK = sys.argv[1], sys.argv[2], sys.argv[3]
Y = 365.25
def gun(y): return int(math.floor(y * Y))
TD = dt.timedelta
SON = dt.date(2026, 1, 1)
MARMARA = (39.5, 42.0, 26.0, 31.5)
R_YAKIN, HALKA, N_MAX, N_MIN = 100.0, (200.0, 500.0), 8, 3
N_PEN, N_YAK = gun(5), gun(2)                 # 1826, 730
KAYDIR = gun(2)                               # plasebo 730 g geriye
SICRAMA_KENAR = 30
W0_ALT = dt.date(2008, 1, 1)                  # Z5 bilgi alt kümesi
SHA16 = {'DataHoldings.txt': '4a98b65ad74c425b', 'steps.txt': '887501a438c41c34', 'm6_havuz.csv': '969c5c54851ee353'}
# Ö3: TR-12 tablosundaki yıl ölçekli öncül iddialarının olayları (tarih, yalnız eşleme için)
LITERATUR = {'Tohoku 2011': dt.date(2011, 3, 11), 'Maule 2010': dt.date(2010, 2, 27), 'Illapel 2015': dt.date(2015, 9, 16),
             'Iquique 2014': dt.date(2014, 4, 1), 'Nicoya 2012': dt.date(2012, 9, 5), 'Papanoa 2014': dt.date(2014, 4, 18)}


def sha(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


GIRDI = {fn: sha(os.path.join(d, fn)) for d, fns in ((NGL, ('DataHoldings.txt', 'steps.txt', 'ev30.csv', 'ev70.csv',
                                                            'ev70_pre.csv')),
                                                    (TR2, ('m6_havuz.csv', 'mekanizma.jsonl')))
         for fn in fns}
for fn, s16 in SHA16.items():
    assert GIRDI[fn].startswith(s16), f'{fn} sha256 uyuşmuyor'


def hav_vec(la, lo, LA_, LO_):
    la, lo = math.radians(la), math.radians(lo)
    a = np.sin((LA_ - la) / 2) ** 2 + np.cos(la) * np.cos(LA_) * np.sin((LO_ - lo) / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def sar(lo): return (lo + 180) % 360 - 180
def marmara(la, lo): return MARMARA[0] <= la <= MARMARA[1] and MARMARA[2] <= lo <= MARMARA[3]


st_ad, st_la, st_lo, st_b, st_e, st_n = [], [], [], [], [], []
with open(os.path.join(NGL, 'DataHoldings.txt')) as f:
    next(f)
    for l in f:
        p = l.split()
        try:
            la, lo = float(p[1]), sar(float(p[2]))
            b, e, n = dt.date.fromisoformat(p[7]), dt.date.fromisoformat(p[8]), int(p[10])
        except Exception:
            continue
        st_ad.append(p[0]); st_la.append(la); st_lo.append(lo); st_b.append(b)
        st_e.append(min(e, SON - TD(days=1))); st_n.append(n)
NS = len(st_ad)
AD = np.array(st_ad)
LA, LO = np.radians(st_la), np.radians(st_lo)
MAR = np.array([marmara(a, o) for a, o in zip(st_la, st_lo)])
DOL = np.array([n / max((e - b).days + 1, 1) for n, b, e in zip(st_n, st_b, st_e)])


def tarih(s):
    yy = int(s[:2]); yyyy = 2000 + yy if yy <= 79 else 1900 + yy
    return dt.datetime.strptime(f'{yyyy}{s[2:]}', '%Y%b%d').date()


k1 = collections.defaultdict(set); k2 = collections.defaultdict(list)
with open(os.path.join(NGL, 'steps.txt')) as f:
    for l in f:
        p = l.split()
        if len(p) < 3: continue
        try: t = tarih(p[1])
        except Exception: continue
        if t >= SON: continue
        if p[2] == '1': k1[p[0]].add(t)
        elif p[2] == '2': k2[p[0]].append(t)


def katalog(fn, sadece_deprem=True):
    out = []
    with open(fn) as f:
        for r in csv.DictReader(f):
            t = dt.date.fromisoformat(r['time'][:10])
            if t >= SON: continue
            if sadece_deprem and r.get('type', 'earthquake') != 'earthquake': continue
            out.append(dict(id=r['id'], T=t, la=float(r['latitude']), lo=sar(float(r['longitude'])),
                            M=float(r['mag']), z=float(r['depth'] or 0), yer=r.get('place', '')))
    return out


EV = katalog(os.path.join(NGL, 'ev30.csv'))
assert all(e['T'] < SON for e in EV)
E6 = katalog(os.path.join(TR2, 'm6_havuz.csv'))
E70 = list({e['id']: e for e in katalog(os.path.join(NGL, 'ev70_pre.csv')) + katalog(os.path.join(NGL, 'ev70.csv'))}.values())
def dizi(E):
    return (np.radians([e['la'] for e in E]), np.radians([e['lo'] for e in E]),
            np.array([e['T'].toordinal() for e in E]), np.array([e['M'] for e in E]))
E6a, E70a = dizi(E6), dizi(E70)


def deprem_var(la, lo, arr, Mmin, R, t0, t1):
    ELA, ELO, ET, EM = arr
    m = (EM >= Mmin) & (ET >= t0.toordinal()) & (ET <= t1.toordinal())
    if not m.any(): return False
    return bool((hav_vec(la, lo, ELA[m], ELO[m]) <= R).any())


# mekanizma (bileşim satırı için)
konum = {}
for fn in ('birincil_aday.csv', 'birincil_aday_fm.csv'):
    for e in katalog(os.path.join(TR2, fn)):
        konum[e['id']] = e
MEK = {}
with open(os.path.join(TR2, 'mekanizma.jsonl')) as f:
    for s in f:
        if not s.strip(): continue
        r = json.loads(s)
        if r.get('hata'): continue
        for k in ('mt', 'fm'):
            L = [x for x in r.get(k, []) if 'nodal-plane-1-rake' in x or 'nodal-plane-1-slip' in x]
            if L:
                x = max(L, key=lambda q: q.get('_w', 0))
                rk = sar(float(x.get('nodal-plane-1-rake', x.get('nodal-plane-1-slip'))))
                MEK[r['id']] = 'doğrultu atımlı' if abs(rk) <= 30 or abs(rk) >= 150 else ('bindirme' if rk > 0 else 'normal')
                break


def bolge(la, lo):
    if 30 <= la <= 50 and -126 <= lo <= -112: return 'ABD batı'
    if 50 < la <= 72 and -170 <= lo <= -128 or (la > 50 and lo > 170): return 'Alaska/Kanada batı'
    if 24 <= la <= 46 and 122 <= lo <= 150: return 'Japonya'
    if -48 <= la <= -33 and 165 <= lo <= 180: return 'Yeni Zelanda'
    if -56 <= la <= 13 and -82 <= lo <= -60: return 'And/G. Amerika batı'
    if 34 <= la <= 48 and 12 <= lo <= 30: return 'Alp-İtalya-Balkan-Ege'
    if 34 <= la <= 44 and 26 <= lo <= 45: return 'Anadolu (Marmara dışı)'
    if 20 <= la <= 50 and 70 <= lo <= 122: return 'Çin/Tibet/Tayvan/Himalaya'
    if 14 <= la <= 33 and -118 <= lo <= -86: return 'Meksika/Orta Amerika'
    if -12 <= la <= 20 and 90 <= lo <= 160: return 'Endonezya/Filipinler/PNG'
    if 24 <= la <= 50 and -112 < lo <= -60: return 'K. Amerika (öteki)'
    return 'öteki'


def uygun(w0, w1, H, doluluk, aday):
    """TR-11 §2.3 istasyon kuralları, pencere [w0, w1], menteşe H; yalnız aday indisler değerlendirilir."""
    e0 = w0 - TD(days=N_YAK)
    ok = np.zeros(NS, bool)
    for i in aday:
        if MAR[i] or st_b[i] > w0 or st_e[i] < w1: continue
        if doluluk and DOL[i] < 0.60: continue
        s = st_ad[i]
        if any(e0 <= t <= w1 for t in k2[s]): continue
        bad = False
        for t in k1[s]:
            if w0 <= t <= w1 and (abs((t - H).days) < SICRAMA_KENAR or (t - w0).days < SICRAMA_KENAR
                                  or (w1 - t).days < SICRAMA_KENAR):
                bad = True; break
        if bad: continue
        ok[i] = True
    return ok


def pencere(T_eff):
    """T_eff = olay günü − 6 g; w1 = T_eff − 1 = T − 7 g (TR-1b §2)."""
    w1 = T_eff - TD(days=1); w0 = T_eff - TD(days=N_PEN); H = T_eff - TD(days=N_YAK)
    return w0, w1, H


def sakin(la, lo, w0, w1):
    if deprem_var(la, lo, E6a, 6.0, 200.0, w0 - TD(days=gun(5)), w1): return 'Ş1'
    if deprem_var(la, lo, E70a, 7.0, 500.0, w0 - TD(days=gun(10)), w1): return 'Ş2'
    if deprem_var(la, lo, E70a, 8.0, 1000.0, w0 - TD(days=gun(10)), w1): return 'Ş3'
    return None


def kume_kur(la, lo, ok):
    d = hav_vec(la, lo, LA, LO)
    yk = np.where((d <= R_YAKIN) & ok)[0]; hk = np.where((d >= HALKA[0]) & (d <= HALKA[1]) & ok)[0]
    yk = yk[np.lexsort((AD[yk], d[yk]))][:N_MAX]; hk = hk[np.lexsort((AD[hk], d[hk]))][:N_MAX]
    return (list(yk), list(hk)) if len(yk) >= N_MIN and len(hk) >= N_MIN else None


def degerlendir(e, doluluk):
    r = dict(id=e['id'], T=e['T'].isoformat(), M=e['M'], la=e['la'], lo=e['lo'], z=e['z'], yer=e['yer'],
             bolge=bolge(e['la'], e['lo']), mekanizma=MEK.get(e['id'], 'bilinmiyor'))
    if marmara(e['la'], e['lo']):
        r['neden'] = 'Marmara kutusu'; return r
    Te = e['T'] - TD(days=6)
    w0, w1, H = pencere(Te)
    r.update(w0=w0.isoformat(), w1=w1.isoformat())
    s = sakin(e['la'], e['lo'], w0, w1)
    if s:
        r['neden'] = s; return r
    aday = np.where(hav_vec(e['la'], e['lo'], LA, LO) <= HALKA[1])[0]
    k = kume_kur(e['la'], e['lo'], uygun(w0, w1, H, doluluk, aday))
    if not k:
        r['neden'] = 'istasyon<3'; return r
    r['olay'] = dict(yakin=[str(AD[i]) for i in k[0]], ref=[str(AD[i]) for i in k[1]], n_y=len(k[0]), n_r=len(k[1]))
    # eşli plasebo: 730 g geriye; iki pencerede de uygun istasyonlar; sakinlik birleşik aralıkta
    w0p, w1p, Hp = pencere(Te - TD(days=KAYDIR))
    sp = sakin(e['la'], e['lo'], w0p, w1)
    if sp:
        r['esli_neden'] = 'plasebo ' + sp; return r
    ok2 = uygun(w0, w1, H, doluluk, aday) & uygun(w0p, w1p, Hp, doluluk, aday)
    k2_ = kume_kur(e['la'], e['lo'], ok2)
    if not k2_:
        r['esli_neden'] = 'ortak istasyon<3'; return r
    r['esli'] = dict(yakin=[str(AD[i]) for i in k2_[0]], ref=[str(AD[i]) for i in k2_[1]], n_y=len(k2_[0]),
                     n_r=len(k2_[1]), w0_p=w0p.isoformat())
    return r


def kumele(rs, anahtar, bas):
    """TR-1b §2: (i) < 300 km ve < 1 yıl; (ii) ortak istasyon ve pencere çakışması; (iii) aynı 10° blok ve çakışma."""
    n = len(rs); ana = list(range(n))
    def bul(i):
        while ana[i] != i:
            ana[i] = ana[ana[i]]; i = ana[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            a, b = rs[i], rs[j]
            Ti, Tj = dt.date.fromisoformat(a['T']), dt.date.fromisoformat(b['T'])
            dkm = float(hav_vec(a['la'], a['lo'], np.radians([b['la']]), np.radians([b['lo']]))[0])
            ai0, ai1 = dt.date.fromisoformat(a[bas]), dt.date.fromisoformat(a['w1'])
            bj0, bj1 = dt.date.fromisoformat(b[bas]), dt.date.fromisoformat(b['w1'])
            cak = ai0 <= bj1 and bj0 <= ai1
            sti = set(a[anahtar]['yakin'] + a[anahtar]['ref']); stj = set(b[anahtar]['yakin'] + b[anahtar]['ref'])
            blk = (math.floor(a['la'] / 10), math.floor(a['lo'] / 10)) == (math.floor(b['la'] / 10), math.floor(b['lo'] / 10))
            if (dkm < 300 and abs((Ti - Tj).days) < 365) or (cak and (sti & stj)) or (cak and blk):
                ana[bul(i)] = bul(j)
    g = collections.defaultdict(list)
    for i in range(n):
        g[bul(i)].append(i)
    return sorted(g.values(), key=lambda v: rs[v[0]]['T'])


def katman(n): return '3-4' if n <= 4 else ('5-7' if n <= 7 else '8')


def say(doluluk):
    R = [degerlendir(e, doluluk) for e in sorted(EV, key=lambda e: (e['T'], e['id']))]
    gecen = [r for r in R if 'olay' in r]
    esli = [r for r in R if 'esli' in r]
    K_k = kumele(gecen, 'olay', 'w0')
    Kp_k = kumele(esli, 'esli', 'w0_p')
    alt = [r for r in gecen if dt.date.fromisoformat(r['w0']) >= W0_ALT]
    K08 = kumele(alt, 'olay', 'w0')
    neden = collections.Counter(r.get('neden', 'geçti') for r in R)
    eneden = collections.Counter(r.get('esli_neden', 'geçti') for r in R if 'olay' in r)
    def bil(rs, kk):
        return dict(bolge=dict(collections.Counter(rs[v[0]]['bolge'] for v in kk)),
                    mekanizma_olay=dict(collections.Counter(r['mekanizma'] for r in rs)),
                    katman_olay=dict(collections.Counter(katman(r['olay' if 'olay' in r else 'esli']['n_y']) for r in rs)))
    lit = {ad: [r['id'] for r in R if abs((dt.date.fromisoformat(r['T']) - t).days) <= 1 and r['M'] >= 7.0]
           for ad, t in LITERATUR.items()}
    lit_esli = {ad: [i for i in v if any(r['id'] == i and 'esli' in r for r in R)] for ad, v in lit.items()}
    return dict(R=R, olay_aday=len(R), olay_gecen=len(gecen), K=len(K_k), olay_esli=len(esli), K_p=len(Kp_k),
                olay_w0_2008=len(alt), K_w0_2008=len(K08), eleme=dict(neden), esli_eleme=dict(eneden),
                bilesim_K=bil(gecen, K_k), bilesim_Kp=bil(esli, Kp_k),
                kumeler_K=[[gecen[i]['id'] for i in v] for v in K_k],
                kumeler_Kp=[[esli[i]['id'] for i in v] for v in Kp_k],
                literatur_olaylari_katalogda=lit, literatur_olaylari_eslide=lit_esli)


def main():
    os.makedirs(CIK, exist_ok=True)
    ozet = dict(tarih=dt.date.today().isoformat(), girdi_sha256=GIRDI, kural='TR-1b sürüm 2 §2, §7; doluluk "yok" = üst '
                'sınır (dal kuralı bunu kullanır), "oran" = NumSol / gün aralığı >= 0,60 (yaklaşık, bilgi)', sonuc={})
    liste = None
    for dol in (False, True):
        s = say(dol)
        ad = 'oran' if dol else 'yok'
        if not dol:
            # dondurulan liste: doluluk 'yok' (üst sınır) ile eşli plasebosu kurulan olaylar ve kümeleri
            idx = {r['id']: r for r in s['R']}
            liste = dict(kural='TR-1b sürüm 2, aşama 0, doluluk yok (üst sınır)',
                         esli_kumeler=[dict(kume=k + 1, olaylar=[dict(id=i, T=idx[i]['T'], M=idx[i]['M'],
                                                                    la=idx[i]['la'], lo=idx[i]['lo'],
                                                                    n_y_ust=idx[i]['esli']['n_y'],
                                                                    katman_ust=katman(idx[i]['esli']['n_y']),
                                                                    yakin=idx[i]['esli']['yakin'],
                                                                    ref=idx[i]['esli']['ref']) for i in v])
                                       for k, v in enumerate(s['kumeler_Kp'])],
                         olay_kumeler=[dict(kume=k + 1, olaylar=v) for k, v in enumerate(s['kumeler_K'])])
        ozet['sonuc'][ad] = {k: v for k, v in s.items() if k != 'R'}
        print(ad, json.dumps({k: v for k, v in s.items() if k not in ('R', 'kumeler_K', 'kumeler_Kp')},
                             ensure_ascii=False), flush=True)
    yol = os.path.join(CIK, 'tr1b_asama0_liste.json')
    with open(yol, 'w') as f:
        json.dump(liste, f, indent=1, ensure_ascii=False, sort_keys=True)
    ozet['liste_sha256'] = sha(yol)
    Kp = ozet['sonuc']['yok']['K_p']
    ozet['dal'] = 'K_p >= 6: eşli sınama koşulabilir' if Kp >= 6 else 'K_p < 6: veri yok (eşli küme); koşu yapılmaz'
    with open(os.path.join(CIK, 'tr1b_asama0_ozet.json'), 'w') as f:
        json.dump(ozet, f, indent=1, ensure_ascii=False)
    print('liste sha256', ozet['liste_sha256'], '|', ozet['dal'])


main()
