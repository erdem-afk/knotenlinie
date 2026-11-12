#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 2, E1: teleseismik cisim dalgası maskesinin tetikleyici ve Parkfield pencerelerindeki önhesabı.

Yalnız katalog ve seyahat süresi; dalga formu yok. Kural (ön kayıt §6.5 madde 1a): her pencere için ComCat'ten
[R başı − 3 sa, W sonu] aralığındaki bütün M ≥ 6,0 olaylar; tetikleyici olayın kendisi dışarıda (Wharton biriminde
öteki olay dahil). Her olay için segment orta noktasına (köşe ortalaması; Parkfield'da iz köşe ortalaması) Δ ile
obspy.taup iasp91, olay derinliğinde: t_P = adı 'P' ile başlayan fazların en erkeni, t_S = adı 'S' ile başlayan
fazların en erkeni. Maske [t0 + t_P − 10, t0 + t_P + k] ∪ [t0 + t_S − 10, t0 + t_S + k] (sn); k değişkeye göre.
Bu önhesap segment orta noktasıyla ve listedeki W'lerin birleşimiyle yapılır; koşuda pencere başına aynı kural.

ComCat yanıtları depo dışı önbelleğe (<onbellek>/e1_<olay>.csv) yazılır, varsa yeniden çekilmez; sha256 çıktıya girer.
Sorgu bitişleri ≤ 2025-12-31T23:59:59 ile kırpılır.
Değişkeler (aynı olay listesinden; özet json'da ayrı): 'E1-lit' = İNCELEME-1 metni (M ≥ 6,0, P ve S, +240 sn);
'E1-C' = sürüm 2'nin İŞLEYEN kuralı (M ≥ 7,0: P ve S +240 sn; 6,0 ≤ M < 7,0: yalnız P, +60 sn);
'E1-B' = seçenek (M ≥ 7,0 +240; 6,0 ≤ M < 7,0 P ve S +60); 'E1-A' = seçenek (yalnız M ≥ 7,0, +240).
Gerekçe (ön kayıt §6.5 1a, §17): E1-lit Tohoku pencerelerini (Marmara ve Parkfield K1) %100 maskeler.
Kullanım: python3 -I -B tr7_e1_maske.py <onbellek_dizini> [--yaz]
Çıktı: tr7_e1_maske.csv (olay × pencere × faz), tr7_e1_maske_ozet.json.
"""
import csv, datetime as dt, hashlib, json, os, sys, time, urllib.request, urllib.parse
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees

BURADA = os.path.dirname(os.path.abspath(__file__))
ONB = sys.argv[1]
UA = 'fdsn-event-client/1.0 (python-urllib)'
SON = dt.datetime(2025, 12, 31, 23, 59, 59)
WHARTON = ('official20120411083836720_20', 'usp000jhjb')
SEGMENT = {
    'S1': [(26.20, 40.55), (26.90, 40.62), (27.50, 40.80)],
    'S2': [(27.50, 40.80), (28.00, 40.82), (28.60, 40.85), (29.00, 40.83)],
    'S3': [(29.00, 40.83), (29.30, 40.72), (29.90, 40.72)],
    'S4': [(29.90, 40.72), (30.30, 40.70), (30.80, 40.75), (31.20, 40.80)],
    'S5': [(31.20, 40.80), (31.60, 40.73), (32.20, 40.80), (32.60, 40.87)],
    'S6': [(32.60, 40.87), (33.30, 40.90), (34.00, 41.02)],
    'S7': [(30.30, 40.50), (29.50, 40.43), (29.10, 40.42), (28.30, 40.33), (27.50, 40.25), (27.00, 40.10),
           (26.60, 39.70)],
    'PK': [(-120.80, 36.20), (-120.50, 35.97), (-120.35, 35.83), (-120.20, 35.65)],
}
ORTA = {s: (sum(p[1] for p in iz) / len(iz), sum(p[0] for p in iz) / len(iz)) for s, iz in SEGMENT.items()}
ONCE = 10.0
K1_ARALIK = (dt.datetime(2011, 3, 11, 6, 16, 0), dt.datetime(2011, 3, 11, 6, 31, 48))
MODEL = TauPyModel('iasp91')


def zaman(s):
    s = s.replace('Z', '')
    for f in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
        try:
            return dt.datetime.strptime(s, f)
        except ValueError:
            pass
    raise ValueError(s)


def comcat(ad, t0, t1):
    yol = os.path.join(ONB, f'e1_{ad}.csv')
    if not os.path.exists(yol):
        q = urllib.parse.urlencode(dict(format='csv', starttime=t0.isoformat(timespec='seconds'),
                                        endtime=min(t1, SON).isoformat(timespec='seconds'), minmagnitude='6.0',
                                        orderby='time-asc'))
        req = urllib.request.Request('https://earthquake.usgs.gov/fdsnws/event/1/query?' + q,
                                     headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            veri = r.read()
        with open(yol, 'wb') as f:
            f.write(veri)
        time.sleep(1.0)
    veri = open(yol, 'rb').read()
    return list(csv.DictReader(veri.decode('utf-8').splitlines())), hashlib.sha256(veri).hexdigest()


def fazlar(dep, deg):
    tt = MODEL.get_travel_times(source_depth_in_km=max(0.0, dep), distance_in_degree=deg, phase_list=['ttall'])
    tp = min((a.time for a in tt if a.name.startswith('P')), default=None)
    ts = min((a.time for a in tt if a.name.startswith('S')), default=None)
    return tp, ts


def birlesim(ar):
    ar = sorted(ar)
    out = []
    for a, b in ar:
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


DEGISKE = {'E1-lit': (6.0, lambda M, f: 240.0),
           'E1-B': (6.0, lambda M, f: 240.0 if M >= 7.0 else 60.0),
           'E1-C': (6.0, lambda M, f: 240.0 if M >= 7.0 else (60.0 if f == 'P' else None)),
           'E1-A': (7.0, lambda M, f: 240.0)}


def bosluklar(maske, a, b):
    out, cur = [], a
    for x, y in sorted(maske):
        if x > cur:
            out.append((min(x, b) - cur).total_seconds())
        cur = max(cur, y)
        if cur >= b:
            break
    if cur < b:
        out.append((b - cur).total_seconds())
    return [g for g in out if g > 0]


def kesisim_s(maske, a, b):
    return sum(max(0.0, (min(y, b) - max(x, a)).total_seconds()) for x, y in maske)


def main():
    liste = list(csv.DictReader(open(os.path.join(BURADA, 'tr7_dondurulan_liste.csv'), encoding='utf-8')))
    pen = {}
    for r in liste:
        k = (r['birim'], r['tetikleyici'], r['segment'])
        p = pen.setdefault(k, dict(t0=zaman(r['t0']), R0=zaman(r['R_bas']), R1=zaman(r['R_son']),
                                   W0=zaman(r['W_bas']), W1=zaman(r['W_son'])))
        p['W0'] = min(p['W0'], zaman(r['W_bas']))
        p['W1'] = max(p['W1'], zaman(r['W_son']))
    pk = list(csv.DictReader(open(os.path.join(BURADA, 'tr7_parkfield_liste.csv'), encoding='utf-8')))
    tohoku = 'official20110311054624120_30'
    t0_th = next(zaman(r['t0']) for r in liste if r['tetikleyici'] == tohoku)
    pen[('PARKFIELD', tohoku, 'PK')] = dict(t0=t0_th, R0=t0_th - dt.timedelta(seconds=3600), R1=t0_th,
                                            W0=min(zaman(x['W_bas']) for x in pk),
                                            W1=max(zaman(x['W_son']) for x in pk))
    # olay başına tek sorgu: o olayın bütün pencerelerinin birleşim aralığı
    sorgu = {}
    for (b, o, s), p in pen.items():
        a, z = sorgu.get(o, (p['R0'], p['W1']))
        sorgu[o] = (min(a, p['R0']), max(z, p['W1']))
    kat, shas = {}, {}
    for o, (a, z) in sorted(sorgu.items(), key=lambda kv: kv[1][0]):
        kat[o], shas[o] = comcat(o, a - dt.timedelta(hours=3), z)
    satir, ozet = [], {}
    for (b, o, s), p in sorted(pen.items(), key=lambda kv: (kv[1]['t0'], kv[0][2])):
        la, lo = ORTA[s]
        varis = []                                   # (M, varış anı)
        for e in kat[o]:
            te = zaman(e['time'])
            if not (p['R0'] - dt.timedelta(hours=3) <= te <= p['W1']):
                continue
            if e['id'] == o:
                continue
            # tetikleyicinin kendisi başka kimlikle: ±5 sn ve M ≥ 7
            if abs((te - p['t0']).total_seconds()) < 5 and float(e['mag']) >= 7.0:
                continue
            deg = locations2degrees(float(e['latitude']), float(e['longitude']), la, lo)
            dep = float(e['depth'] or 0)
            tp, ts = fazlar(dep, deg)
            for faz, tt in (('P', tp), ('S', ts)):
                if tt is None:
                    continue
                tv = te + dt.timedelta(seconds=tt)
                varis.append((float(e['mag']), tv, faz))
                satir.append(dict(birim=b, tetikleyici=o, segment=s, olay=e['id'], olay_t=te.isoformat(),
                                  M=e['mag'], derinlik_km=dep, delta_derece=round(deg, 2), faz=faz,
                                  seyahat_s=round(tt, 1), varis=tv.isoformat(timespec='seconds'),
                                  W_icinde=int(p['W0'] <= tv <= p['W1'])))
        wl = (p['W1'] - p['W0']).total_seconds()
        rl = (p['R1'] - p['R0']).total_seconds()
        anahtar = 'PARKFIELD|PK' if s == 'PK' else f'{o}|{s}'
        ozet[anahtar] = dict(W=[p['W0'].isoformat(timespec='seconds'), p['W1'].isoformat(timespec='seconds')],
                             W_icinde_varis_M6_6p9=sum(1 for M, tv, f in varis if M < 7 and p['W0'] <= tv <= p['W1']),
                             W_icinde_varis_M7=sum(1 for M, tv, f in varis if M >= 7 and p['W0'] <= tv <= p['W1']))
        for ad, (mmin, kuyruk) in DEGISKE.items():
            mb = birlesim([(tv - dt.timedelta(seconds=ONCE), tv + dt.timedelta(seconds=kuyruk(M, f)))
                           for M, tv, f in varis if M >= mmin and kuyruk(M, f) is not None])
            mb = [(x, y) for x, y in mb if kesisim_s([(x, y)], p['R0'], p['W1']) > 0]
            acik = bosluklar(mb, p['W0'], p['W1'])
            d = dict(W_maskeli_pay=round(kesisim_s(mb, p['W0'], p['W1']) / wl, 3),
                     R_maskeli_pay=round(kesisim_s(mb, p['R0'], p['R1']) / rl, 3),
                     W_en_uzun_acik_s=round(max(acik, default=0)),
                     maske=[[x.isoformat(timespec='seconds'), y.isoformat(timespec='seconds')] for x, y in mb])
            if s == 'PK' or o == tohoku:
                ka, kz = K1_ARALIK
                d['K1_araligi_maskeli_pay'] = round(kesisim_s(mb, ka, kz) / (kz - ka).total_seconds(), 3)
                d['K1_araligi_en_uzun_acik_s'] = round(max(bosluklar(mb, ka, kz), default=0))
            ozet[anahtar][ad] = d
    sonuc = dict(kural=dict(M_min=6.0, once_s=ONCE, model='iasp91', obspy=__import__('obspy').__version__,
                            sorgu='[R başı − 3 sa, W sonu], ≤ 2025-12-31',
                            degiskeler={'E1-lit': 'İNCELEME-1 metni: M ≥ 6,0, [t−10, t+240]',
                                        'E1-B': 'seçenek: M ≥ 7,0 [t−10, t+240]; 6,0 ≤ M < 7,0 P ve S [t−10, t+60]',
                                        'E1-C': 'sürüm 2 işleyen kural: M ≥ 7,0 P ve S [t−10, t+240]; 6,0 ≤ M < 7,0 yalnız P [t−10, t+60]',
                                        'E1-A': 'seçenek: yalnız M ≥ 7,0, [t−10, t+240]'}),
                 comcat_sha256=shas, olay_sayisi={o: len(v) for o, v in kat.items()},
                 pencere_segment=len(ozet))
    for ad in DEGISKE:
        sonuc[ad + '_ozet'] = dict(
            maskeli_pencere=sum(1 for v in ozet.values() if v[ad]['W_maskeli_pay'] > 0),
            W_yarisindan_cogu_maskeli=sorted(k for k, v in ozet.items() if v[ad]['W_maskeli_pay'] > 0.5),
            S1_S3_PK=dict((k, [v[ad]['W_maskeli_pay'], v[ad].get('K1_araligi_maskeli_pay'),
                               v[ad]['W_en_uzun_acik_s'], v[ad].get('K1_araligi_en_uzun_acik_s')])
                          for k, v in ozet.items() if k.split('|')[1] in ('S1', 'S2', 'S3', 'PK')
                          and v[ad]['W_maskeli_pay'] > 0))
    sonuc['pencere'] = ozet
    js = json.dumps(sonuc, ensure_ascii=False, indent=1)
    print(js)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, 'tr7_e1_maske.csv'), 'x', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
            w.writeheader()
            w.writerows(satir)
        with open(os.path.join(BURADA, 'tr7_e1_maske_ozet.json'), 'x', encoding='utf-8') as f:
            f.write(js + '\n')


if __name__ == '__main__':
    main()
