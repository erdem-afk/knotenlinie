#!/usr/bin/env python3
"""TR-5b İNCELEME-2: yatay yoklama kuralının (altı isteğin hepsi "var") beklenen kaybı, TR-5 Ek 1'in Z ay
yoklamasından (onbellek.jsonl; loc=*, BHZ,HHZ). Yeni ağ isteği yok; dalga formu yok.

Yaklaşım: Ek 1'de `dolu_ana` geçen olay istasyon-pencerelerinde (taban 3 yıl), A, B, C dilimlerinin orta ayında Z'nin
"var" olup olmadığına bakılır. Yatay bileşenlerin Z ile aynı aylarda var olduğu (en iyi durum) varsayılırsa, "altısı
da var" kuralının pencere kaybı en az P(üç orta aydan biri Z'de var değil | dolu_ana) kadardır. Ayrıca önerilen koşullu
kural (Z'si "var" olmayan dilimin yatay isteği sayılmaz) ile kayıp.
Kullanım: python3 -I -B inc2_yatay_kayip.py <Ek1 onbellek dizini (onbellek.jsonl)>
"""
import collections, csv, datetime as dt, json, os, sys

BURASI = os.path.dirname(os.path.abspath(__file__))
TR5 = os.path.dirname(BURASI)
ob = sys.argv[1]
kayit = {}
for l in open(os.path.join(ob, 'onbellek.jsonl')):
    x = json.loads(l); kayit[x['k']] = x
kod = collections.Counter(str(x['kod']) for x in kayit.values())


def durum(x):
    if x is None: return 'yok_istek'
    if x['kod'] == 200 and x['bayt'] > 0: return 'var'
    if x['kod'] in (204, 404) or (x['kod'] == 200 and x['bayt'] == 0): return 'bos'
    if x['kod'] in (401, 403): return 'kisitli'
    return 'hata'


def orta_ay(a, b):
    g = a + (b - a) / 2
    return f'{g.year:04d}-{g.month:02d}'


TD = dt.timedelta
n = kayip_sert = kayip_kosul = 0; ay_var = []
for r in csv.DictReader(open(os.path.join(TR5, 'tr5_doluluk.csv'))):
    if r['taban'] != '3' or r['rol'] != 'olay' or r['dolu_ana'] != 'True': continue
    a, b = dt.date.fromisoformat(r['bas']), dt.date.fromisoformat(r['son'])
    T = b + TD(days=1)                       # Ek 1 penceresi [T - 3 yıl, T - 1 g]
    dil = [(a, T - TD(days=731)), (T - TD(days=730), T - TD(days=366)), (T - TD(days=365), b)]
    d = [durum(kayit.get(f"{r['ag']}.{r['ist']}.{orta_ay(x, y)}")) for x, y in dil]
    n += 1; ay_var += [s == 'var' for s in d]
    kayip_sert += any(s != 'var' for s in d)
    kayip_kosul += all(s != 'var' for s in d)  # koşullu kural: yalnız hiçbir dilim bilgi vermiyorsa düşer
out = dict(ek1_kod_dagilimi=dict(kod), dolu_ana_olay_penceresi=n,
           orta_ay_Z_var_orani=round(sum(ay_var) / len(ay_var), 3),
           sert_kural_en_az_kayip=round(kayip_sert / n, 3), kosullu_kural_kayip=round(kayip_kosul / n, 3))
json.dump(out, open(os.path.join(BURASI, 'inc2_yatay_kayip.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
