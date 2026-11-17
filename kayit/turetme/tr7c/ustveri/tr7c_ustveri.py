#!/usr/bin/env python3
"""TR-7c ön kayıt sürüm 2, §8 yoklamaları D4 ve D1 (+ D5, D9 bilgi): yalnız üstveri, katalog ve seyahat süresi.

Kullanım: python3 -I -B tr7c_ustveri.py <ham_dizini> <çıktı.json>

KÖRLÜK: Hiçbir dataselect isteği yapılmaz; hiçbir dalga formu indirilmez ya da açılmaz. İstekler yalnız:
  - USGS ComCat fdsnws/event (katalog; E1 maskesi için M ≥ 6,0),
  - NCEDC ve EarthScope fdsnws/station (level=response / channel; StationXML yanıtı),
  - fdsnws/availability (yalnız zaman aralıkları; CI kanalları için D5).
Bütün sorgu bitişleri ≤ 2025-12-31T23:59:59. Genel User-Agent; kişisel ya da proje bilgisi gönderilmez. 429/503'te
beklenir; 401/403 atlatılmaz (kayda geçer).

KURAL (ön kayıt sürüm 2, commit 41d2ff5; sonuç görülmeden yazıldı):
  D4 (n_P, n_N): olay (N'de birim; D-1: N 27 + N 28 = 'Vanuatu 2009 birimi') sayılır ⇔
     (i) ≥ 3 liste istasyonu "var" (TR-7b_SAYIM'ın availability sayımı: seçili düşey kanalda W ve R örtüsü ≥ 0,90;
         birimde iki olayın en küçüğü) ve
     (ii) K1b aralığı [T0 + Δ/4,6, T0 + Δ/3,0] (iz köşe ortalamasında; birimde [N27 başı, N28 sonu]) E1 maskesinden
         (TR-7 §6.5.1a: ComCat [R başı − 3 sa, W sonu], M ≥ 6,0; tetikleyici hariç; M ≥ 7,0 P ve S [−10, +240] sn,
         6,0 ≤ M < 7,0 yalnız P [−10, +60] sn; iasp91, olay derinliği, iz köşe ortalaması) sonra ≥ %50 açık.
     Tetikleyicinin ComCat kaydı: T0'a ±60 sn içinde M ≥ 7,0 olan en yakın kayıt (sapma yazılır) ve TR-7'nin ikiz kayıt
     kuralı (±5 sn, M ≥ 7,0). Birimde yalnız N 27 tetikleyicidir; N 28 'öteki olay' olarak maskelenir (D-1).
  D1 (k): P olayı başvuru istasyonludur ⇔ liste sınıfında en az bir istasyonun bir düşey kanalı (bant B ya da H,
     alet H; TR-7 §6.6) StationXML yanıtında |H(0,02 Hz)| / |H(1 Hz)| ≥ 0,5 (olay anındaki epok; obspy evalresp, VEL)
     ve W ile R örtüsü ≥ 0,90 (TR-7b_SAYIM availability'si; CI kanalları için D5 yeniden sorgusu). Başvuru istasyonu
     iz köşe ortalamasına en yakın uygun istasyondur. k = başvuru istasyonlu P olayı sayısı (10 P'nin hepsinden).
     Yazarın seçimi: istasyonun herhangi bir uygun düşey kanalı yeterlidir.
  Karar (ön kayıt §8 D1 = D-5 ve D4 satırı): k < 7 ya da kestirilen n_P < 8 ya da n_N < 20 → TR-7c dondurulmaz, kör koşu
     yapılmaz; aksi hâlde "dondurulabilir (üstveri kapısı geçti)".
  Bilgi (karara girmez): k'nin n_P'ye giren olaylarla sınırlı hâli; üç bileşen (yatay kanalların varlığı ve örtüsü) şartlı
     k_3 (uygun istasyonun aynı bant ve alet kodlu iki yatay kanalı da W ve R'de ≥ 0,90; availability, istasyon başına
     olay başına tek GET); D-9'un 4 genliği eşlenmiş N olayında başvuru istasyonu. (yüzey_diger sınıfıyla k
     hesaplanmadı: aday listesi ilk koşudan sonra bu bilgi satırı kapsamdan çıkarıldı; karara girmez.)
"""
import csv, datetime as dt, hashlib, json, math, os, sys, time, urllib.error, urllib.parse, urllib.request

from obspy import read_inventory, UTCDateTime
from obspy.taup import TauPyModel
from obspy.geodetics import locations2degrees

BURADA = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.abspath(os.path.join(BURADA, '..', '..', '..'))
SAYIM = os.path.join(KOK, 'turetme', 'tr7b', 'tr7b_sayim.json')
LISTE = os.path.join(KOK, 'turetme', 'tr7', 'tr7_parkfield_liste.csv')
UA = 'fdsn-client/1.0 (python-urllib)'
NCEDC = 'https://service.ncedc.org/fdsnws'
ESC = 'https://service.iris.edu/fdsnws'
SCEDC = 'https://service.scedc.caltech.edu/fdsnws'
COMCAT = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
SINIR = dt.datetime(2025, 12, 31, 23, 59, 59)
IZ = [(-120.80, 36.20), (-120.50, 35.97), (-120.35, 35.83), (-120.20, 35.65)]
IZ_ORTA = (sum(p[1] for p in IZ) / 4, sum(p[0] for p in IZ) / 4)
MODEL = TauPyModel('iasp91')

P_OLAY = ['200106232033', '200211032212', '200301220206', '200309251950', '200412260058', '200611151114',
          '200701130423', '200805120628', '200909291748', '201002270634']
VANUATU = ('200910072203', '200910072218')
GENLIK4 = ['200412231459', '200503281609', '200704012039', '200708152340']   # Macquarie, Nias, Solomon, Peru 2007

GUNLUK, SON = [], [0.0]


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


def iste(url, ham, ad, veri=None):
    """GET/POST; 429/503'te bekle. Gövde ham dizine yazılır, sha256 günlüğe. (kod, gövde)."""
    assert 'dataselect' not in url
    yol = os.path.join(ham, ad)
    for deneme in range(4):
        bekle = 1.0 - (time.time() - SON[0])
        if bekle > 0:
            time.sleep(bekle)
        req = urllib.request.Request(url, data=veri, headers={'User-Agent': UA})
        SON[0] = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                kod, g = r.status, r.read()
        except urllib.error.HTTPError as e:
            kod, g = e.code, b''
            if kod in (429, 503) and deneme < 3:
                ra = e.headers.get('Retry-After')
                time.sleep(float(ra) if ra and ra.isdigit() else 30 * (deneme + 1))
                continue
        except Exception as e:                                       # noqa: BLE001
            kod, g = -1, str(e).encode()
            if deneme < 3:
                time.sleep(10 * (deneme + 1))
                continue
        GUNLUK.append(dict(ad=ad, url=url.split('?')[0], sorgu=url.split('?')[1] if '?' in url else None,
                           post=veri.decode()[:4000] if veri else None, http=kod, bayt=len(g),
                           sha256=hashlib.sha256(g).hexdigest(),
                           zaman=dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds')))
        if g and kod == 200:
            with open(yol, 'wb') as f:
                f.write(g)
        return kod, g
    return kod, g


def birlesim(ar):
    out = []
    for a, b in sorted(ar):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def kesisim_s(maske, a, b):
    return sum(max(0.0, (min(y, b) - max(x, a)).total_seconds()) for x, y in maske)


def fazlar(dep, deg):
    tt = MODEL.get_travel_times(source_depth_in_km=max(0.0, dep), distance_in_degree=deg, phase_list=['ttall'])
    tp = min((a.time for a in tt if a.name.startswith('P')), default=None)
    ts = min((a.time for a in tt if a.name.startswith('S')), default=None)
    return tp, ts


def pencereler(o):
    D = o['delta_km']
    t0 = zt(o['t0'])
    return dict(t0=t0, R0=t0 - dt.timedelta(seconds=3600), R1=t0, W0=zt(o['W'][0]), W1=zt(o['W'][1]),
                K0=t0 + dt.timedelta(seconds=round(D / 4.6)), K1=t0 + dt.timedelta(seconds=round(D / 3.0)))


def e1(birim, olaylar, ham):
    """birim: dict(ad, tet=olay, ek=[öteki olaylar], p=pencere). E1 maskesi ve K1b açık payı."""
    p = birim['p']
    a, b = p['R0'] - dt.timedelta(hours=3), min(p['W1'], SINIR)
    q = urllib.parse.urlencode(dict(format='csv', starttime=iso(a), endtime=iso(b), minmagnitude='6.0',
                                    orderby='time-asc'))
    kod, g = iste(f'{COMCAT}?{q}', ham, f'comcat_{birim["ad"]}.csv')
    if kod != 200:
        return dict(hata=f'ComCat HTTP {kod}')
    kat = list(csv.DictReader(g.decode('utf-8').splitlines()))
    t0 = p['t0']
    # tetikleyicinin kaydı: ±60 sn içinde M ≥ 7,0 olan en yakın kayıt
    aday = sorted((abs((zt(e['time']) - t0).total_seconds()), e['id']) for e in kat
                  if float(e['mag']) >= 7.0 and abs((zt(e['time']) - t0).total_seconds()) <= 60)
    tet_id = aday[0][1] if aday else None
    tet_sapma = aday[0][0] if aday else None
    la, lo = IZ_ORTA
    varis, satir = [], []
    for e in kat:
        te = zt(e['time'])
        if not (a <= te <= p['W1']):
            continue
        if e['id'] == tet_id:
            continue
        if abs((te - t0).total_seconds()) < 5 and float(e['mag']) >= 7.0:   # ikiz kayıt
            continue
        deg = locations2degrees(float(e['latitude']), float(e['longitude']), la, lo)
        dep = float(e['depth'] or 0)
        tp, ts = fazlar(dep, deg)
        M = float(e['mag'])
        for faz, tt in (('P', tp), ('S', ts)):
            if tt is None:
                continue
            k = 240.0 if M >= 7.0 else (60.0 if faz == 'P' else None)
            if k is None:
                continue
            tv = te + dt.timedelta(seconds=tt)
            varis.append((tv - dt.timedelta(seconds=10), tv + dt.timedelta(seconds=k)))
            satir.append(dict(olay=e['id'], t=iso(te), M=M, faz=faz, varis=iso(tv), kuyruk_s=k))
    mb = birlesim(varis)
    kl = (p['K1'] - p['K0']).total_seconds()
    wl = (p['W1'] - p['W0']).total_seconds()
    km = kesisim_s(mb, p['K0'], p['K1'])
    return dict(comcat_kayit=len(kat), comcat_sha256=hashlib.sha256(g).hexdigest(), tetikleyici_id=tet_id,
                tetikleyici_sapma_s=tet_sapma, maskelenen_varis=satir,
                K1b=[iso(p['K0']), iso(p['K1'])], K1b_maskeli_pay=round(km / kl, 3), K1b_acik_pay=round(1 - km / kl, 3),
                W_maskeli_pay=round(kesisim_s(mb, p['W0'], p['W1']) / wl, 3))


def yanit(net, sta, loc, cha, servis, ham):
    """Kanalın 2001–2010 epoklarının StationXML yanıtı (tek istek)."""
    q = dict(net=net, sta=sta, loc=loc or '--', cha=cha, starttime='2001-01-01T00:00:00',
             endtime='2011-01-01T00:00:00', level='response', format='xml')
    ad = f'resp_{servis_ad(servis)}_{net}.{sta}.{loc or "--"}.{cha}.xml'
    kod, g = iste(f'{servis}/station/1/query?' + urllib.parse.urlencode(q), ham, ad)
    if kod != 200 or not g:
        return None, kod
    return read_inventory(os.path.join(ham, ad), format='STATIONXML'), kod


def servis_ad(s):
    return {NCEDC: 'ncedc', ESC: 'esc', SCEDC: 'scedc'}[s]


def oran(inv, net, sta, loc, cha, t):
    try:
        ch = inv.select(network=net, station=sta, location=loc, channel=cha, time=UTCDateTime(t))
        kan = [c for n in ch for s in n for c in s]
        if not kan or kan[0].response is None or kan[0].response.instrument_sensitivity is None:
            return None, 'yanit yok'
        h = abs(kan[0].response.get_evalresp_response_for_frequencies([0.02, 1.0], output='VEL'))
        return (float(h[0] / h[1]) if h[1] > 0 else None), None
    except Exception as e:                                           # noqa: BLE001
        return None, f'{type(e).__name__}: {e}'


def availability(servis, net, sta, loc, cha, a, b, ham):
    q = dict(net=net, sta=sta, loc=loc or '--', cha=cha, starttime=iso(a), endtime=iso(b), format='text')
    if servis == NCEDC:
        q['loc'] = loc or '*'
    ad = f'avail_{servis_ad(servis)}_{net}.{sta}.{loc or "--"}.{cha}_{a:%Y%m%d%H%M}.txt'
    kod, g = iste(f'{servis}/availability/1/query?' + urllib.parse.urlencode(q), ham, ad)
    ar = []
    if kod == 200:
        for s in g.decode('utf-8', 'replace').splitlines():
            if s.startswith('#') or not s.strip():
                continue
            # Sütun sayısı servise göre değişir (SCEDC'de boş Quality alanı); ilk iki ISO zamanı Earliest, Latest'tir.
            zs = [x for x in s.split() if len(x) >= 19 and x[:4].isdigit() and x[4] == '-' and 'T' in x]
            if len(zs) >= 2:
                ar.append((zt(zs[0]), zt(zs[1])))
    return ar, kod


def ortu(ar, a, b):
    m = birlesim([(max(a, x), min(b, y)) for x, y in ar if y > a and x < b])
    return sum((y - x).total_seconds() for x, y in m) / (b - a).total_seconds()


def main():
    ham, cikti = sys.argv[1], sys.argv[2]
    os.makedirs(ham, exist_ok=True)
    say = json.load(open(SAYIM, encoding='utf-8'))
    olay = {o['evid']: o for o in say['olaylar']}
    P = [olay[e] for e in P_OLAY]
    N = [o for o in say['olaylar'] if o['Q_CC'] == 0]
    assert len(P) == 10 and len(N) == 30 and all(o['Q_CC'] == 1 for o in P)
    for o in say['olaylar']:
        assert zt(o['W'][1]) < SINIR

    # ---------------------------------------------------------------- birimler (D-1)
    birimler = []
    for o in P:
        birimler.append(dict(ad=o['evid'], sinif='P', olaylar=[o], p=pencereler(o)))
    for o in N:
        if o['evid'] == VANUATU[1]:
            continue
        if o['evid'] == VANUATU[0]:
            o2 = olay[VANUATU[1]]
            p1, p2 = pencereler(o), pencereler(o2)
            p = dict(p1, W1=p2['W1'], K1=p2['K1'])
            birimler.append(dict(ad='VANUATU2009', sinif='N', olaylar=[o, o2], p=p))
        else:
            birimler.append(dict(ad=o['evid'], sinif='N', olaylar=[o], p=pencereler(o)))
    assert sum(b['sinif'] == 'N' for b in birimler) == 29

    # ---------------------------------------------------------------- D4: E1 ve K1b açık payı, liste sayısı
    for b in birimler:
        b['e1'] = e1(b, b['olaylar'], ham)
        b['liste_var'] = min(o['sayi_var']['liste'] for o in b['olaylar'])
        b['sayilir'] = bool(b['liste_var'] >= 3 and b['e1'].get('K1b_acik_pay', 0) >= 0.5)
        print(b['ad'], b['sinif'], 'liste', b['liste_var'], 'K1b açık', b['e1'].get('K1b_acik_pay'),
              'tet', b['e1'].get('tetikleyici_id'), b['e1'].get('tetikleyici_sapma_s'), flush=True)

    # ---------------------------------------------------------------- D1: başvuru istasyonu
    liste = {(r['ag'], r['istasyon']) for r in csv.DictReader(open(LISTE, encoding='utf-8'))}
    hedef = P + [olay[e] for e in GENLIK4]
    # aday düşey kanallar: TR-7b_SAYIM'dan bant B/H, alet H
    kanallar = {}
    for o in hedef:
        for k, v in o['istasyonlar'].items():
            if v['sinif'] not in ('liste', 'yuzey_diger'):
                continue
            for c in v['kanallar']:
                if c['cha'][0] in 'BH' and c['cha'][1] == 'H':
                    net, sta = k.split('.')
                    kanallar.setdefault((net, sta, c['loc'], c['cha']), []).append(o['evid'])
    # yanıtlar: liste sınıfı NCEDC (BK, NC) / EarthScope (CI); yuzey_diger yalnız bilgi, EarthScope
    inv, inv_kod = {}, {}
    for (net, sta, loc, cha) in sorted(kanallar):
        sinif = 'liste' if (net, sta) in liste else 'yuzey_diger'
        if sinif != 'liste':
            continue
        servis = NCEDC if net in ('BK', 'NC', 'BP') else ESC
        iv, kod = yanit(net, sta, loc, cha, servis, ham)
        if iv is None and servis == ESC:
            iv, kod = yanit(net, sta, loc, cha, SCEDC, ham)
        inv[(net, sta, loc, cha)], inv_kod[(net, sta, loc, cha)] = iv, kod
    # D5: CI kanallarının W ve R örtüsü (SAYIM'da EarthScope availability 404 vermişti)
    ci_ortu = {}
    for o in hedef:
        p = pencereler(o)
        for (net, sta, loc, cha) in sorted(kanallar):
            if net != 'CI' or o['evid'] not in kanallar[(net, sta, loc, cha)]:
                continue
            ar, kod = availability(ESC, net, sta, loc, cha, p['R0'], p['W1'], ham)
            kaynak = 'esc'
            if kod != 200:
                ar, kod2 = availability(SCEDC, net, sta, loc, cha, p['R0'], p['W1'], ham)
                kaynak = f'scedc ({kod2}; esc {kod})'
            ci_ortu[(o['evid'], net, sta, loc, cha)] = dict(W=round(ortu(ar, p['W0'], p['W1']), 3),
                                                             R=round(ortu(ar, p['R0'], p['R1']), 3), kaynak=kaynak)

    def basvuru(o):
        la0, lo0 = IZ_ORTA
        p = pencereler(o)
        uygun, ayr = [], []
        for k, v in o['istasyonlar'].items():
            net, sta = k.split('.')
            if (net, sta) not in liste:
                continue
            for c in v['kanallar']:
                if not (c['cha'][0] in 'BH' and c['cha'][1] == 'H'):
                    continue
                key = (net, sta, c['loc'], c['cha'])
                ow, orr = c['ortu_W'], c['ortu_R']
                if net == 'CI' and (o['evid'],) + key in ci_ortu:
                    ow, orr = ci_ortu[(o['evid'],) + key]['W'], ci_ortu[(o['evid'],) + key]['R']
                iv = inv.get(key)
                r, hata = (oran(iv, *key, p['t0']) if iv is not None else (None, f'yanıt alınamadı (HTTP {inv_kod.get(key)})'))
                ok = bool(r is not None and r >= 0.5 and ow >= 0.9 and orr >= 0.9)
                ayr.append(dict(kanal='.'.join([net, sta, c['loc'] or '--', c['cha']]), ortu_W=ow, ortu_R=orr,
                                oran_002_1=None if r is None else round(r, 3), hata=hata, uygun=ok))
                if ok:
                    # konum: SAYIM'da yok; yanıt envanterinden
                    ch = iv.select(network=net, station=sta, time=UTCDateTime(p['t0']))
                    s0 = [s for n in ch for s in n][0]
                    uygun.append((round(locations2degrees(la0, lo0, s0.latitude, s0.longitude) * 111.195, 1),
                                  f'{net}.{sta}', c['cha']))
        uygun.sort()
        return dict(basvuru=uygun[0] if uygun else None, uygun_istasyon=sorted({u[1] for u in uygun}),
                    kanallar=ayr)

    d1 = {o['evid']: basvuru(o) for o in hedef}
    for e, v in d1.items():
        print(e, olay[e]['ad'], 'başvuru', v['basvuru'], flush=True)

    # ---------------------------------------------------------------- bilgi: üç bileşen (k_3)
    for o in hedef:
        p = pencereler(o)
        v = d1[o['evid']]
        uc = []
        for ist in v['uygun_istasyon']:
            net, sta = ist.split('.')
            servis = SCEDC if net == 'CI' else NCEDC
            q = dict(net=net, sta=sta, loc='*' if servis == NCEDC else '--', cha='BH?,HH?', starttime=iso(p['R0']),
                     endtime=iso(p['W1']), format='text')
            ad = f'avail3_{servis_ad(servis)}_{net}.{sta}_{p["R0"]:%Y%m%d%H%M}.txt'
            kod, g = iste(f'{servis}/availability/1/query?' + urllib.parse.urlencode(q), ham, ad)
            kan = {}
            if kod == 200:
                for s in g.decode('utf-8', 'replace').splitlines():
                    if s.startswith('#') or not s.strip():
                        continue
                    zs = [x for x in s.split() if len(x) >= 19 and x[:4].isdigit() and x[4] == '-' and 'T' in x]
                    if len(zs) >= 2:
                        kan.setdefault(s.split()[3], []).append((zt(zs[0]), zt(zs[1])))
            ok = {c: (ortu(a, p['W0'], p['W1']) >= 0.9 and ortu(a, p['R0'], p['R1']) >= 0.9) for c, a in kan.items()}
            bant = [b for b in ('BH', 'HH') if ok.get(b + 'Z') and sum(1 for c in ok if c[:2] == b and c[2] != 'Z'
                                                                       and ok[c]) >= 2]
            uc.append(dict(istasyon=ist, http=kod, kanal_ortu_ok={c: bool(x) for c, x in sorted(ok.items())},
                           uc_bilesen_bant=bant))
        v['uc_bilesen'] = uc
        v['uc_bilesen_var'] = any(u['uc_bilesen_bant'] for u in uc)

    # ---------------------------------------------------------------- karar
    nP = sum(1 for b in birimler if b['sinif'] == 'P' and b['sayilir'])
    nN = sum(1 for b in birimler if b['sinif'] == 'N' and b['sayilir'])
    k = sum(1 for e in P_OLAY if d1[e]['basvuru'])
    sayilan_P = {b['ad'] for b in birimler if b['sinif'] == 'P' and b['sayilir']}
    k_nP = sum(1 for e in P_OLAY if d1[e]['basvuru'] and e in sayilan_P)
    nedenler = []
    if k < 7:
        nedenler.append(f'modülasyon şartı için yeterli başvuru istasyonu yok (k = {k})')
    if nP < 8:
        nedenler.append(f'kestirilen n_P = {nP} < 8')
    if nN < 20:
        nedenler.append(f'kestirilen n_N = {nN} < 20')
    karar = ('dondurulmaz; kör koşu yapılmaz: ' + '; '.join(nedenler) + '; kör olaylar harcanmadı') if nedenler \
        else 'dondurulabilir (üstveri kapısı geçti)'
    out = dict(
        tarih=dt.datetime.now(dt.timezone.utc).replace(tzinfo=None).isoformat(timespec='seconds'),
        betik_sha256=hashlib.sha256(open(os.path.abspath(__file__), 'rb').read()).hexdigest(),
        sayim_sha256=hashlib.sha256(open(SAYIM, 'rb').read()).hexdigest(),
        liste_sha256=hashlib.sha256(open(LISTE, 'rb').read()).hexdigest(),
        obspy=__import__('obspy').__version__,
        karar=karar, k=k, k_nP_icinde=k_nP, n_P=nP, n_N=nN,
        k_3_bilgi=sum(1 for e in P_OLAY if d1[e].get('uc_bilesen_var')),
        birimler=[dict(ad=b['ad'], sinif=b['sinif'], olaylar=[o['evid'] for o in b['olaylar']],
                       adlar=[o['ad'] for o in b['olaylar']], liste_var=b['liste_var'], sayilir=b['sayilir'], **b['e1'])
                  for b in birimler],
        d1={e: dict(ad=olay[e]['ad'], grup='P' if e in P_OLAY else 'N_genlik4', **v) for e, v in d1.items()},
        ci_ortu={'|'.join(k_): v for k_, v in ci_ortu.items()},
        yanit_http={'.'.join(x if x else '--' for x in k_): v for k_, v in inv_kod.items()},
        http_istek=len(GUNLUK),
        http_dagilim={str(c): sum(1 for g in GUNLUK if g['http'] == c) for c in sorted({g['http'] for g in GUNLUK})},
        dataselect_istegi=sum(1 for g in GUNLUK if 'dataselect' in g['url']))
    json.dump(out, open(cikti, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    with open(os.path.join(ham, 'tr7c_ustveri_gunluk.jsonl'), 'w', encoding='utf-8') as f:
        for g in GUNLUK:
            f.write(json.dumps(g, ensure_ascii=False) + '\n')
    print(json.dumps(dict(karar=karar, k=k, k_nP=k_nP, n_P=nP, n_N=nN), ensure_ascii=False))


if __name__ == '__main__':
    main()
