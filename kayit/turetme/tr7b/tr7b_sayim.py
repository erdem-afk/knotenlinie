"""TR-7b veri varlığı kapısı (0 €; yalnız üstveri + availability + R içinde birkaç 10 sn'lik yoklama).

Çalıştırma:  python3 -I -B tr7b_sayim.py <chao2012_TableS1.txt> <günlük_dizini/> <çıktı.json>

Ne yapar:
  1. Chao vd. 2012 (BSSA, 10.1785/0120110151) Ek Tablo S1'i okur: 2001–2010 arası 42 Mw ≥ 7,5 olay ve
     Orta Kaliforniya (CC, Parkfield–Cholame) için "tetikledi (1) / tetiklemedi (0)" işareti. 2001-06-23 ile
     2008-05-12 arasındaki 31 olay Peng vd. 2009 (10.1029/2008jb006049) ile aynı kümedir; tetikleyen 10 olay o
     makalenin tam metninden doğrulandı (betikte LIT sözlüğü). Tohoku 2011 (geliştirme verisi) ayrıca eklenir.
  2. Her olay için TR-7 §5 pencereleri (iz köşe ortalamasına Δ ile): W = [T0 + Δ/5,0, T0 + Δ/2,8 + 600],
     R = [T0 − 3600, T0).
  3. NCEDC ve EarthScope fdsnws/station (kanal düzeyi, TR-7 §3.2 kutusu, W ile kesişen epoklar). Seçim: düşey
     (|dip| ≥ 60° ya da kanal kodu Z ile biter), alet kodu H ya da P, örnekleme ≥ 20 Hz, birim M/S, ize ≤ 50 km.
  4. fdsnws/availability (NCEDC; NCEDC'de yoksa EarthScope): kanal başına W ve R örtüsü (kayıtlı süre payı).
     İstasyon "var" = en az bir seçili düşey kanalında W örtüsü ≥ 0,90 ve R örtüsü ≥ 0,90.
  5. Sınıflar: "liste" = TR-7 `tr7_parkfield_liste.csv`'deki 56 yüzey istasyonu; "kuyu" = BP (HRSN) ve PB;
     "yuzey_diger" = öteki yüzey istasyonları (bilgi).
  6. Yoklama: olay başına sınıf başına en çok 1 dataselect isteği, 10 sn, R ortasında (T0 − 1800 s; olaydan
     ÖNCE). Yalnız HTTP kodu ve bayt; içerik çözülmez, diske yazılmaz. W içinde hiçbir dalga formu istenmez.

Körlük: W içindeki hiçbir dalga formu istenmez; availability yalnız zaman aralığı döner.
Bütün sorgular ≤ 2025-12-31. Marmara kutusuna hiçbir sorgu yapılmaz.
"""
import csv, datetime as dt, hashlib, json, math, os, sys, time, urllib.error, urllib.parse, urllib.request

UA = "Mozilla/5.0 (compatible; research-client)"
NCEDC = "https://service.ncedc.org/fdsnws"
ESC = "https://service.iris.edu/fdsnws"
KUTU = dict(minlat=35.3, maxlat=36.6, minlon=-121.3, maxlon=-119.6)
IZ = [(-120.80, 36.20), (-120.50, 35.97), (-120.35, 35.83), (-120.20, 35.65)]
IZ_ORTA = (sum(p[1] for p in IZ) / 4, sum(p[0] for p in IZ) / 4)  # (enlem, boylam)
SINIR = dt.datetime(2025, 12, 31, 23, 59, 59)
BURADA = os.path.dirname(os.path.abspath(__file__))
LISTE = os.path.join(BURADA, '..', 'tr7', 'tr7_parkfield_liste.csv')

# Literatür (doğrulama düzeyi elle yazıldı; kaynak: tam metin ya da özet, TR-7b_SAYIM.md §1)
LIT = {
    '200106232033': ('Peru 2001', ['10.1029/2008jb006049 (tam metin §5.5)']),
    '200111140926': ('Kunlun 2001', ['10.1029/2008jb006049 (tam metin §5.9; zayıf, yalnız kaynağa yakın istasyonlarda)']),
    '200211032212': ('Denali 2002', ['10.1029/2008gl036080 (özet)', '10.1029/2008jb006049 (tam metin §5.1)']),
    '200301220206': ('Colima 2003', ['10.1029/2008jb006049 (tam metin §5.4)']),
    '200309251950': ('Tokachi-oki 2003', ['10.1029/2008jb006049 (tam metin §5.8)']),
    '200412260058': ('Sumatra 2004', ['10.1029/2008jb006062 (özet)', '10.1029/2008jb006049 (tam metin §5.3)']),
    '200605031526': ('Tonga 2006', ['10.1029/2008jb006049 (tam metin §5.10; zayıf)']),
    '200611151114': ('Kuril 2006', ['10.1029/2008jb006049 (tam metin §5.6; artçı P dalgalarıyla karışık, konumlanamadı)']),
    '200701130423': ('Kuril 2007', ['10.1029/2008jb006049 (tam metin §5.2)']),
    '200805120628': ('Wenchuan 2008', ['10.1029/2008jb006049 (tam metin §5.7)']),
    '200909291748': ('Samoa 2009', ['10.1785/0120110151 Tablo S1 (yalnız Q işareti)']),
    '201002270634': ('Maule 2010', ['10.1029/2010gl045462 (özet)', '10.1785/0120110151 Tablo S1']),
    '200704012039': ('Solomon 2007', ['10.1029/2008jb006049 (tam metin, Gomberg vd. 2008b atfıyla: tetiklemedi)']),
    '200708152340': ('Peru 2007', ['10.1029/2008jb006049 (tam metin, Gomberg vd. 2008b atfıyla: tetiklemedi)']),
    '200709121110': ('G. Sumatra 2007', ['10.1029/2008jb006049 (tam metin, Gomberg vd. 2008b atfıyla: tetiklemedi)']),
}
TOHOKU = dict(evid='201103110546', t0='2011-03-11T05:46:24.120', lon=142.373, lat=38.297, dep=29.0, mag=9.1,
              Q=1, ad='Tohoku 2011 (GELİŞTİRME VERİSİ, kör değil)', kaynak=['10.1785/0120120114 (özet)'])


def buyuk_daire(la1, lo1, la2, lo2):
    p1, p2, dl = math.radians(la1), math.radians(la2), math.radians(lo2 - lo1)
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(dl)
    return 6371.0 * math.acos(max(-1.0, min(1.0, c)))


def nokta_cizgi(la, lo, iz):  # tr7_onkayit_sayilar.py ile aynı
    k = math.cos(math.radians(la)) * 111.195
    px, py = lo * k, la * 111.195
    en = 1e9
    for (x1, y1), (x2, y2) in zip(iz[:-1], iz[1:]):
        ax, ay, bx, by = x1 * k, y1 * 111.195, x2 * k, y2 * 111.195
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        en = min(en, math.hypot(px - (ax + t * dx), py - (ay + t * dy)))
    return en


def iso(t):
    return t.strftime('%Y-%m-%dT%H:%M:%S')


def zt(s):
    s = s.strip().rstrip('Z')
    for f in ('%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            return dt.datetime.strptime(s, f)
        except ValueError:
            pass
    raise ValueError(s)


GUNLUK = []
SON = [0.0]


def iste(url, veri=None, gunluk_ad=None, kaydet=None):
    """HTTP isteği; 429/503'te bekle ve yeniden dene. (kod, gövde) döner."""
    for deneme in range(4):
        bekle = 0.5 - (time.time() - SON[0])
        if bekle > 0:
            time.sleep(bekle)
        req = urllib.request.Request(url, data=veri, headers={'User-Agent': UA})
        SON[0] = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                kod, govde = r.status, r.read()
        except urllib.error.HTTPError as e:
            kod, govde = e.code, b''
            if kod in (429, 503) and deneme < 3:
                ra = e.headers.get('Retry-After')
                time.sleep(float(ra) if ra and ra.isdigit() else 30 * (deneme + 1))
                continue
        except Exception as e:  # ağ hatası
            kod, govde = -1, str(e).encode()
            if deneme < 3:
                time.sleep(10 * (deneme + 1))
                continue
        GUNLUK.append(dict(ad=gunluk_ad, url=url.split('?')[0], sorgu=url.split('?')[1] if '?' in url else None,
                           post=veri.decode()[:20000] if veri else None, http=kod, bayt=len(govde),
                           sha256=hashlib.sha256(govde).hexdigest() if kaydet else None,
                           zaman=dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')))
        if kaydet and govde:
            with open(kaydet, 'wb') as f:
                f.write(govde)
        return kod, govde
    return kod, govde


def kanallar(servis, W0, W1, dizin, evid):
    q = dict(KUTU, starttime=iso(W0), endtime=iso(W1), level='channel', format='text')
    ad = f'{evid}_station_{"ncedc" if servis == NCEDC else "esc"}.txt'
    kod, g = iste(f'{servis}/station/1/query?' + urllib.parse.urlencode(q), gunluk_ad=ad,
                  kaydet=os.path.join(dizin, ad))
    out = []
    if kod != 200:
        return out
    for sat in g.decode('utf-8', 'replace').splitlines():
        if sat.startswith('#') or not sat.strip():
            continue
        p = sat.split('|')
        if len(p) < 17:
            continue
        net, sta, loc, cha = p[0], p[1], p[2], p[3]
        try:
            la, lo, dip, sr = float(p[4]), float(p[5]), float(p[9] or 0), float(p[14] or 0)
            derin = float(p[7] or 0)
        except ValueError:
            continue
        birim = p[13].upper()
        if len(cha) != 3 or cha[1] not in 'HP' or sr < 20 or birim != 'M/S':
            continue
        if not (abs(dip) >= 60 or cha[2] == 'Z'):
            continue
        izk = nokta_cizgi(la, lo, IZ)
        if izk > 50:
            continue
        out.append(dict(net=net, sta=sta, loc=loc, cha=cha, la=la, lo=lo, derin=derin, sr=sr, iz_km=round(izk, 1),
                        bas=p[15], son=p[16]))
    return out


def ortu(araliklar, a, b):
    """[a, b) içinde araliklar (birleşimi) ile kaplanan pay."""
    k = sorted((max(a, x), min(b, y)) for x, y in araliklar if y > a and x < b)
    top, uc = 0.0, a
    for x, y in k:
        x = max(x, uc)
        if y > x:
            top += (y - x).total_seconds()
            uc = y
    return top / (b - a).total_seconds()


def uygunluk(servis, kan, R0, W1, dizin, evid):
    if not kan:
        return {}
    satirlar = ['format=text']
    for c in kan:
        bos = '*' if servis == NCEDC else '--'   # NCEDC POST '--' ile 204 döner (yoklandı); '*' bütün konumlar
        satirlar.append(f"{c['net']} {c['sta']} {c['loc'] or bos} {c['cha']} {iso(R0)} {iso(W1)}")
    ad = f'{evid}_availability_{"ncedc" if servis == NCEDC else "esc"}.txt'
    kod, g = iste(f'{servis}/availability/1/query', veri='\n'.join(satirlar).encode(), gunluk_ad=ad,
                  kaydet=os.path.join(dizin, ad))
    sp = {}
    if kod != 200:
        return sp
    for sat in g.decode('utf-8', 'replace').splitlines():
        if sat.startswith('#') or not sat.strip():
            continue
        p = sat.split()
        if len(p) < 8:
            continue
        loc = '' if p[2] == '--' else p[2]
        sp.setdefault((p[0], p[1], loc, p[3]), []).append((zt(p[6]), zt(p[7])))
    return sp


def main():
    tablo, dizin, cikti = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(dizin, exist_ok=True)
    liste = {(r['ag'], r['istasyon']) for r in csv.DictReader(open(LISTE))}
    olaylar = []
    for sat in open(tablo):
        if sat.startswith('#') or not sat.strip():
            continue
        p = sat.split()
        t0 = dt.datetime(int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5])) + dt.timedelta(seconds=float(p[6]))
        ad, kay = LIT.get(p[0], (None, []))
        olaylar.append(dict(evid=p[0], t0=t0, lon=float(p[7]), lat=float(p[8]), dep=float(p[9]), mag=float(p[10]),
                            Q=int(p[16]), cc_ist=p[11], pgv_z=float(p[14]), pgv_t=float(p[15]),
                            ad=ad or f'{p[0][:4]} M{p[10]} ({float(p[8]):.1f}, {float(p[7]):.1f})',
                            kaynak=['10.1785/0120110151 Tablo S1'] + kay))
    th = dict(TOHOKU)
    th['t0'] = zt(th['t0'])
    th.update(cc_ist='—', pgv_z=None, pgv_t=None)
    olaylar.append(th)
    sonuc = []
    for o in olaylar:
        assert o['t0'] < SINIR
        D = buyuk_daire(o['lat'], o['lon'], *IZ_ORTA)
        W0 = o['t0'] + dt.timedelta(seconds=round(D / 5.0))
        W1 = o['t0'] + dt.timedelta(seconds=round(D / 2.8 + 600))
        R0, R1 = o['t0'] - dt.timedelta(seconds=3600), o['t0']
        assert W1 < SINIR
        kn = kanallar(NCEDC, W0, W1, dizin, o['evid'])
        ke = kanallar(ESC, W0, W1, dizin, o['evid'])
        anahtar = lambda c: (c['net'], c['sta'], c['loc'], c['cha'])
        nset = {anahtar(c) for c in kn}
        kan = {anahtar(c): dict(c, servis='ncedc') for c in kn}
        for c in ke:
            if anahtar(c) not in kan:
                kan[anahtar(c)] = dict(c, servis='esc')
        spn = uygunluk(NCEDC, [c for c in kan.values() if c['servis'] == 'ncedc'], R0, W1, dizin, o['evid'])
        # NCEDC'de aralık dönmeyen (ya da yalnız EarthScope'ta bulunan) kanallar EarthScope'a sorulur
        eks = [c for k, c in kan.items() if k not in spn]
        spe = uygunluk(ESC, eks, R0, W1, dizin, o['evid'])
        ist = {}
        for k, c in kan.items():
            ar = spn.get(k) or spe.get(k) or []
            ow, orr = ortu(ar, W0, W1), ortu(ar, R0, R1)
            sinif = 'kuyu' if c['net'] in ('BP', 'PB') else ('liste' if (c['net'], c['sta']) in liste else 'yuzey_diger')
            s = ist.setdefault((c['net'], c['sta']), dict(sinif=sinif, iz_km=c['iz_km'], kanallar=[], var=False))
            s['kanallar'].append(dict(loc=c['loc'], cha=c['cha'], sr=c['sr'], ortu_W=round(ow, 3), ortu_R=round(orr, 3),
                                      kaynak='ncedc' if k in spn else ('esc' if k in spe else 'yok')))
            if ow >= 0.9 and orr >= 0.9:
                s['var'] = True
        # yoklama: sınıf başına 1 istek, R ortasında, 10 sn; yalnız kod ve bayt
        yok = {}
        tm = o['t0'] - dt.timedelta(seconds=1800)
        for sinif in ('liste', 'kuyu'):
            aday = sorted([(v['iz_km'], k) for k, v in ist.items() if v['sinif'] == sinif and v['var']])
            if not aday:
                yok[sinif] = None
                continue
            net, sta = aday[0][1]
            ch = sorted(ist[(net, sta)]['kanallar'], key=lambda x: -x['sr'])[0]
            servis = NCEDC if ch['kaynak'] != 'esc' else ESC
            q = dict(net=net, sta=sta, loc=ch['loc'] or '--', cha=ch['cha'], starttime=iso(tm),
                     endtime=iso(tm + dt.timedelta(seconds=10)))
            kod, g = iste(f'{servis}/dataselect/1/query?' + urllib.parse.urlencode(q), gunluk_ad=f'{o["evid"]}_yoklama_{sinif}')
            yok[sinif] = dict(istasyon=f'{net}.{sta}', kanal=ch['cha'], http=kod, bayt=len(g))
            del g
        say = {s: sum(1 for v in ist.values() if v['sinif'] == s and v['var']) for s in ('liste', 'kuyu', 'yuzey_diger')}
        say_meta = {s: sum(1 for v in ist.values() if v['sinif'] == s) for s in ('liste', 'kuyu', 'yuzey_diger')}
        sonuc.append(dict(evid=o['evid'], ad=o['ad'], t0=o['t0'].isoformat(), M=o['mag'], lat=o['lat'], lon=o['lon'],
                          Q_CC=o['Q'], pgv_z_cms=o['pgv_z'], pgv_t_cms=o['pgv_t'], cc_istasyon=o['cc_ist'],
                          kaynak=o['kaynak'], delta_km=round(D, 1), W=[iso(W0), iso(W1)], R=[iso(R0), iso(R1)],
                          sayi_var=say, sayi_ustveri=say_meta, yoklama=yok,
                          istasyonlar={f'{k[0]}.{k[1]}': v for k, v in sorted(ist.items())}))
        print(o['evid'], o['ad'], 'Q', o['Q'], 'var', say, 'üstveri', say_meta, 'yoklama',
              {k: (v['http'], v['bayt']) if v else None for k, v in yok.items()}, flush=True)
    # kapı
    gelis = '201103110546'
    poz = [r for r in sonuc if r['Q_CC'] == 1 and r['evid'] != gelis]
    neg = [r for r in sonuc if r['Q_CC'] == 0]
    kapi = {}
    for s in ('liste', 'kuyu'):
        p3 = [r['evid'] for r in poz if r['sayi_var'][s] >= 3]
        n3 = [r['evid'] for r in neg if r['sayi_var'][s] >= 3]
        kapi[s] = dict(pozitif=p3, negatif=n3, gecti=len(p3) >= 2 and len(n3) >= 1)
    p3 = [r['evid'] for r in poz if r['sayi_var']['liste'] >= 3 or r['sayi_var']['kuyu'] >= 3]
    n3 = [r['evid'] for r in neg if r['sayi_var']['liste'] >= 3 or r['sayi_var']['kuyu'] >= 3]
    kapi['herhangi_sinif'] = dict(pozitif=p3, negatif=n3, gecti=len(p3) >= 2 and len(n3) >= 1)
    out = dict(tarih=dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds'),
               tablo_sha256=hashlib.sha256(open(tablo, 'rb').read()).hexdigest(),
               liste_sha256=hashlib.sha256(open(LISTE, 'rb').read()).hexdigest(),
               iz_orta=IZ_ORTA, kural='var: seçili düşey kanalda W ve R örtüsü ≥ 0,90; kapı: ≥2 pozitif (Q_CC=1, '
                                     'Tohoku hariç) ve ≥1 negatif (Q_CC=0), her biri aynı sınıfta ≥3 "var" istasyon',
               kapi=kapi, http_istek=len(GUNLUK),
               http_dagilim={str(k): sum(1 for g in GUNLUK if g['http'] == k) for k in sorted({g['http'] for g in GUNLUK})},
               olaylar=sonuc)
    json.dump(out, open(cikti, 'w'), ensure_ascii=False, indent=1)
    with open(os.path.join(dizin, 'tr7b_sayim_gunluk.jsonl'), 'w') as f:
        for g in GUNLUK:
            f.write(json.dumps(g, ensure_ascii=False) + '\n')
    print(json.dumps(kapi, ensure_ascii=False))


if __name__ == '__main__':
    main()
