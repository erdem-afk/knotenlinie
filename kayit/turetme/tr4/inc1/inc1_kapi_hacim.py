#!/usr/bin/env python3
"""TR-4 İNCELEME-1: kapı, kayıp payı ve kademe D hacmi (bağımsız yazım; yalnız tr4_pencereler.csv okunur, ağ yok).

1. Yer düzeyi hücreler (ana_T, DOLU_ana; ISK+KAVV tek yer, temsilci KO.ISK) yeniden sayılır: 15,16,15,14,14,9,10,9 / 102 / 21.
2. Kapı: >= 10 yer olan iki T, aralarında >= 3 yıl. Alt kümeler (T 2021-2024 vb.) sınanır.
3. Kayıp benzetimi: yer-penceresi düzeyinde bağımsız kayıp p, yer düzeyinde kayıp p, karışık. Kapının kırılma olasılığı.
4. Hacim: istasyon başına, dolu pencerelerinin gün birleşimi; kademe A (her gün) ve C (ayın 1-20'si), 4 saat, 3 bileşen,
   100 sn^-1, 1,3 bayt/örnek. Yer sırası (önceden sabit): dolu hücre sayısı azalan, sonra kod. Kesik koşu: ilk k yer.
Kullanım: python3 -I -B inc1_kapi_hacim.py <tr4_pencereler.csv>   Çıktı: bu dizine inc1_kapi_hacim.json
"""
import csv, collections, datetime as dt, json, os, sys
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
R = [r for r in csv.DictReader(open(sys.argv[1]))]
TEMSILCI = {'KO.ISK': 'KO.ISK'}            # ön kayıt §2.4
hucre = {}                                  # (yer, yıl) -> (istasyon, a, b)
for r in R:
    if r['ana_T'] != 'True' or r['DOLU_ana'] != 'True': continue
    yer = r['yer']
    if yer in TEMSILCI and r['ist'] != TEMSILCI[yer]: continue
    hucre[(yer, int(r['T'][:4]))] = (r['ist'], dt.date.fromisoformat(r['a']), dt.date.fromisoformat(r['b']))
YIL = list(range(2017, 2025))
YER = sorted({y for y, _ in hucre})


def say(h):
    return {t: sum(1 for (_, y) in h if y == t) for t in YIL}


def kapi(c, esik=10, ara=3):
    iyi = [t for t in YIL if c.get(t, 0) >= esik]
    return any(b - a >= ara for i, a in enumerate(iyi) for b in iyi[i + 1:])


out = {}
c0 = say(hucre)
out['yer_T'] = c0; out['yer_pencere'] = len(hucre); out['yer'] = len(YER)
out['kapi_ana'] = kapi(c0)
alt = {'T 2021-2024': range(2021, 2025), 'T 2017-2021': range(2017, 2022), 'T 2017-2020': range(2017, 2021),
       'T 2018/2021/2024': (2018, 2021, 2024), 'T 2017/2020/2023': (2017, 2020, 2023)}
out['alt_kume'] = {}
for ad, ts in alt.items():
    c = {t: (c0[t] if t in ts else 0) for t in YIL}
    out['alt_kume'][ad] = dict(sayi={t: c[t] for t in ts}, n=sum(c.values()), kapi=kapi(c))
# kapının kırılması için en az kaç yer düşmeli (tek tip, her T'de aynı oranda)
out['tek_tip_kayip_kirilma'] = next(round(p, 2) for p in np.arange(0, 1, 0.01)
                                     if not kapi({t: int(np.floor(c0[t] * (1 - p) + 1e-9)) for t in YIL}))

# ---- kayıp benzetimi
rng = np.random.default_rng(404040)
N = 20000
H = list(hucre); yi = {y: i for i, y in enumerate(YER)}
hy = np.array([yi[y] for y, _ in H]); ht = np.array([t for _, t in H])
sim = {}
for p in (0.10, 0.20, 0.30, 0.40, 0.42, 0.50):
    res = {}
    for ad in ('pencere', 'yer', 'karisik'):
        kir = 0; nkal = []
        for _ in range(N):
            if ad == 'pencere': kal = rng.random(len(H)) > p
            elif ad == 'yer': kal = (rng.random(len(YER)) > p)[hy]
            else:
                q = 1 - np.sqrt(1 - p)                              # iki aşamanın birleşik kaybı p
                kal = (rng.random(len(YER)) > q)[hy] & (rng.random(len(H)) > q)
            c = {t: int(np.sum(kal & (ht == t))) for t in YIL}
            kir += not kapi(c); nkal.append(int(kal.sum()))
        res[ad] = dict(P_kapi_kirilir=round(kir / N, 3), n_medyan=int(np.median(nkal)))
    sim[f'p={p:.2f}'] = res
out['kayip_benzetimi'] = dict(N=N, tohum=404040, sonuc=sim)

# ---- hacim
BAYT_GUN = 4 * 3600 * 100 * 3 * 1.3


def gunler(st_hucre, d=None):
    g = set()
    for (_, a, b) in st_hucre:
        x = a
        while x <= b:
            if d is None or x.day <= d: g.add(x)
            x += dt.timedelta(days=1)
    return g


def hacim(h, d):
    per = collections.defaultdict(list)
    for (y, t), v in h.items(): per[y].append(v)
    return sum(len(gunler(v, d)) for v in per.values()) * BAYT_GUN / 1e9


def gun_sure(GB, kibs): return round(GB * 1e9 / (kibs * 1024) / 86400, 1)


out['hacim_GB'] = {'A ana': round(hacim(hucre, None), 1), 'C ana': round(hacim(hucre, 20), 1)}
for ad, ts in alt.items():
    h = {k: v for k, v in hucre.items() if k[1] in ts}
    out['hacim_GB'][f'C {ad}'] = round(hacim(h, 20), 1)
# kesik koşu: yer sırası önceden sabit (dolu hücre sayısı azalan, sonra kod)
nh = collections.Counter(y for y, _ in hucre)
sira = sorted(YER, key=lambda y: (-nh[y], y))
kes = []; kum = 0.0
for k, y in enumerate(sira, 1):
    hy_ = {kk: v for kk, v in hucre.items() if kk[0] == y}
    kum += hacim(hy_, 20)
    hk = {kk: v for kk, v in hucre.items() if kk[0] in sira[:k]}
    c = say(hk)
    kes.append(dict(k=k, yer=y, hucre=nh[y], C_GB_kumulatif=round(kum, 1), n=len(hk), sayi=c, kapi=kapi(c),
                    kapi_12=kapi(c, 12), gun_40=gun_sure(kum, 40), gun_62=gun_sure(kum, 62), gun_106=gun_sure(kum, 106)))
out['kesik_kosu_C'] = kes
for ad, gb in out['hacim_GB'].items():
    out.setdefault('sure_gun', {})[ad] = {f'{v} KiB/s': gun_sure(gb, v) for v in (23, 40, 62, 106, 341)}
json.dump(out, open(os.path.join(BURASI, 'inc1_kapi_hacim.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: out[k] for k in ('yer_T', 'yer_pencere', 'yer', 'kapi_ana', 'alt_kume', 'tek_tip_kayip_kirilma')}, ensure_ascii=False))
print(json.dumps(sim, ensure_ascii=False)); print(json.dumps(out['hacim_GB'], ensure_ascii=False))
for x in kes: print(x['k'], x['yer'], x['hucre'], x['C_GB_kumulatif'], x['n'], list(x['sayi'].values()), x['kapi'], x['kapi_12'], x['gun_40'], x['gun_62'], x['gun_106'])
