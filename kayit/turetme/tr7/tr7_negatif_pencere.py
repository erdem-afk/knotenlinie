#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 2, §7.3 (İNCELEME-1 Ö4): negatif kontrol pencerelerinin seçimi (yalnız katalog; dalga formu yok).

Birim başına 10 pencere. Adaylar d ∈ {−30…−1, +1…+30} gün; yetmezse {−60…−31, +31…+60} gün. Üreteç
numpy.random.default_rng(20261112) (Marmara birimleri, ana şok T0 sırasıyla; Kahramanmaraş bilgi birimleri dahil),
Parkfield için default_rng(20261112 + 1). Her birim için İKİ permütasyon her zaman, sırayla çekilir:
p1 = rng.permutation(±1–30 adayları), p2 = rng.permutation(±31–60 adayları); adaylar p1 sonra p2 sırasıyla denenir,
şartları sağlayan ilk 10 alınır. Şartlar (kaydırılmış zamanlarla):
  (i)   [min R başı − 3 sa, max W sonu] aralığında ComCat M ≥ 6,5 olay yok;
  (ii)  max W sonu < 2026-01-01;
  (iii) kaydırılmış T0'ın yerel gün türü (Pzt–Cum / Cmt–Paz) tetikleyicininkiyle aynı (Marmara: Europe/Istanbul,
        Parkfield: America/Los_Angeles; resmî tatil yok sayılır);
  (iv)  yerel UTC farkı (yaz saati) kaydırılmış min R başında ve max W sonunda tetikleyicininkiyle aynı.
Wharton biriminde iki pencere aynı d ile kayar; aralık iki olayın pencerelerinin birleşimidir.
ComCat yanıtları depo dışı önbelleğe (<onbellek>/neg_<birim>.csv), sha256'ları çıktıya.
Kullanım: python3 -I -B tr7_negatif_pencere.py <onbellek_dizini> [--yaz]
Çıktı: tr7_negatif_pencere.csv, tr7_negatif_pencere_ozet.json.
"""
import csv, datetime as dt, hashlib, json, os, sys, time, urllib.request, urllib.parse
from zoneinfo import ZoneInfo
import numpy as np

BURADA = os.path.dirname(os.path.abspath(__file__))
ONB = sys.argv[1]
UA = 'fdsn-event-client/1.0 (python-urllib)'
SON = dt.datetime(2026, 1, 1)
KAT_SON = dt.datetime(2025, 12, 31, 23, 59, 59)
UTC = dt.timezone.utc


def zaman(s):
    return dt.datetime.fromisoformat(s.replace('Z', ''))


def comcat(ad, t0, t1):
    yol = os.path.join(ONB, f'neg_{ad}.csv')
    if not os.path.exists(yol):
        q = urllib.parse.urlencode(dict(format='csv', starttime=t0.isoformat(timespec='seconds'),
                                        endtime=min(t1, KAT_SON).isoformat(timespec='seconds'),
                                        minmagnitude='6.5', orderby='time-asc'))
        req = urllib.request.Request('https://earthquake.usgs.gov/fdsnws/event/1/query?' + q,
                                     headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            veri = r.read()
        with open(yol, 'wb') as f:
            f.write(veri)
        time.sleep(1.0)
    veri = open(yol, 'rb').read()
    return [zaman(r['time']) for r in csv.DictReader(veri.decode('utf-8').splitlines())], \
        hashlib.sha256(veri).hexdigest()


def yerel(t, tz):
    x = t.replace(tzinfo=UTC).astimezone(tz)
    return ('hafta_sonu' if x.weekday() >= 5 else 'hafta_ici'), x.utcoffset()


def sec(rng, b, tz, kat):
    gt, fark0 = yerel(b['T0'], tz)
    _, fark_r = yerel(b['R0'], tz)
    _, fark_w = yerel(b['W1'], tz)
    p1 = rng.permutation([d for d in range(-30, 31) if d != 0])
    p2 = rng.permutation([d for d in range(-60, 61) if abs(d) > 30])
    out = []
    for d in list(p1) + list(p2):
        k = dt.timedelta(days=int(d))
        r0, w1, t0 = b['R0'] + k, b['W1'] + k, b['T0'] + k
        if any(r0 - dt.timedelta(hours=3) <= e <= w1 for e in kat):
            continue
        if w1 >= SON:
            continue
        if yerel(t0, tz)[0] != gt:
            continue
        if yerel(r0, tz)[1] != fark_r or yerel(w1, tz)[1] != fark_w:
            continue
        out.append(dict(d_gun=int(d), T0_kaydirilmis=t0.isoformat(timespec='seconds'), gun_turu=gt,
                        utc_farki_saat=fark0.total_seconds() / 3600, aday_kumesi='±30' if abs(d) <= 30 else '±31–60'))
        if len(out) == 10:
            break
    return out


def main():
    liste = list(csv.DictReader(open(os.path.join(BURADA, 'tr7_dondurulan_liste.csv'), encoding='utf-8')))
    bir = {}
    for r in liste:
        b = bir.setdefault(r['birim'], dict(T0=None, R0=zaman(r['R_bas']), W1=zaman(r['W_son']),
                                           kahramanmaras=int(r['kahramanmaras'])))
        t0 = zaman(r['t0'])
        b['T0'] = t0 if b['T0'] is None else min(b['T0'], t0)        # Wharton: ana şok
        b['R0'] = min(b['R0'], zaman(r['R_bas']))
        b['W1'] = max(b['W1'], zaman(r['W_son']))
    pk = list(csv.DictReader(open(os.path.join(BURADA, 'tr7_parkfield_liste.csv'), encoding='utf-8')))
    t0 = dt.datetime(2011, 3, 11, 5, 46, 24, 120000)
    pkb = dict(T0=t0, R0=t0 - dt.timedelta(seconds=3600), W1=max(zaman(x['W_son']) for x in pk), kahramanmaras=0)
    satir, ozet, shas = [], {}, {}
    rng = np.random.default_rng(20261112)
    for ad, b in sorted(bir.items(), key=lambda kv: kv[1]['T0']):
        kat, shas[ad] = comcat(ad, b['R0'] - dt.timedelta(days=61, hours=3), b['W1'] + dt.timedelta(days=61))
        s = sec(rng, b, ZoneInfo('Europe/Istanbul'), kat)
        for i, x in enumerate(s, 1):
            satir.append(dict(birim=ad, bolge='Marmara', sira=i, **x))
        ozet[ad] = dict(n=len(s), genisletilmis=sum(1 for x in s if x['aday_kumesi'] != '±30'),
                        kahramanmaras=b['kahramanmaras'])
    rng_pk = np.random.default_rng(20261112 + 1)
    kat, shas['PARKFIELD'] = comcat('PARKFIELD', pkb['R0'] - dt.timedelta(days=61, hours=3),
                                    pkb['W1'] + dt.timedelta(days=61))
    s = sec(rng_pk, pkb, ZoneInfo('America/Los_Angeles'), kat)
    for i, x in enumerate(s, 1):
        satir.append(dict(birim='PARKFIELD_TOHOKU', bolge='Parkfield', sira=i, **x))
    ozet['PARKFIELD_TOHOKU'] = dict(n=len(s), genisletilmis=sum(1 for x in s if x['aday_kumesi'] != '±30'))
    sonuc = dict(comcat_sha256=shas, birim=ozet, toplam=len(satir))
    js = json.dumps(sonuc, ensure_ascii=False, indent=1)
    print(js)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, 'tr7_negatif_pencere.csv'), 'x', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
            w.writeheader()
            w.writerows(satir)
        with open(os.path.join(BURADA, 'tr7_negatif_pencere_ozet.json'), 'x', encoding='utf-8') as f:
            f.write(js + '\n')


if __name__ == '__main__':
    main()
