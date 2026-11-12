#!/usr/bin/env python3
"""TR-4 / TR-5: gerçek veri doluluğu (fdsnws/availability ÜSTVERİSİ; dalga formu indirilmez).

Metadata epoğu verinin arşivde olduğunu göstermez (TR-1/TR-11 dersi: kaba sayımlar ayrıntıda küçülür). Bu betik
merkezin availability servisinden birleştirilmiş zaman aralıklarını alır ve yıl başına dolu gün oranını hesaplar.
EarthScope availability servisi 12 Kasım 2026'da "This service has been retired" (404) döndürdü; IRISDMC
istasyonları için doluluk ölçülemez ve "bilinmiyor" yazılır. Erişim hatası atlatılmaz.

Kullanım:
  python3 -I -B kullanilabilirlik.py <liste.tsv> <çıktı.json>
liste.tsv satırı: ag<TAB>istasyon<TAB>merkez<TAB>başlangıç(YYYY-MM-DD)<TAB>bitiş(YYYY-MM-DD)
Bitiş en geç 2025-12-31'e kırpılır (2026 verisi kör).
"""
import datetime as dt, json, sys, time, urllib.request, urllib.error

AV = {
    'KOERI': 'https://eida.koeri.boun.edu.tr/fdsnws/availability/1/query',
    'GEOFON': 'https://geofon.gfz.de/fdsnws/availability/1/query',
    'ORFEUS': 'https://www.orfeus-eu.org/fdsnws/availability/1/query',
    'NOA': 'https://eida.gein.noa.gr/fdsnws/availability/1/query',
    'INGV': 'https://webservices.ingv.it/fdsnws/availability/1/query',
    'EPOSFR': 'https://seisdata.epos-france.fr/fdsnws/availability/1/query',
    'UIB-NORSAR': 'https://eida.geo.uib.no/fdsnws/availability/1/query',
    'BGR': 'https://eida.bgr.de/fdsnws/availability/1/query',
    'SED': 'https://eida.ethz.ch/fdsnws/availability/1/query',
    'NCEDC': 'https://service.ncedc.org/fdsnws/availability/1/query',
}
SON = dt.date(2025, 12, 31)

def zaman(s):
    s = s.rstrip('Z')
    return dt.datetime.fromisoformat(s[:19])

def al(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'knotenlinie-ustveri/1.0'})
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, r.read().decode('utf-8', 'replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        return type(e).__name__, ''

sonuc = {}
for l in open(sys.argv[1]):
    if not l.strip() or l.startswith('#'): continue
    net, sta, mk, b, e = l.split('\t')[:5]
    b = dt.date.fromisoformat(b.strip()); e = min(dt.date.fromisoformat(e.strip()), SON)
    key = f'{net}.{sta}|{b}|{e}'
    if mk not in AV:
        sonuc[key] = dict(durum='bilinmiyor (availability servisi yok: ' + mk + ')'); continue
    en_iyi = None
    for cha in ('HHZ', 'BHZ'):
        url = (AV[mk] + f'?net={net}&sta={sta}&cha={cha}&start={b}T00:00:00&end={e}T23:59:59'
               '&mergegaps=86400&merge=quality,samplerate,overlap&format=text')
        kod, metin = al(url)
        time.sleep(0.5)
        if kod not in (200, 204):
            sonuc.setdefault(key, {})['hata_' + cha] = kod; continue
        gun = set()
        for s in metin.splitlines():
            if s.startswith('#') or not s.strip(): continue
            p = s.split()
            try: t0, t1 = zaman(p[-2]), zaman(p[-1])
            except Exception:
                try: t0, t1 = zaman(p[6]), zaman(p[7])
                except Exception: continue
            d = max(t0.date(), b)
            while d <= min(t1.date(), e):
                if (t1 - dt.datetime.combine(d, dt.time())).total_seconds() > 0: gun.add(d)
                d += dt.timedelta(days=1)
        yillar = {}
        y = b.year
        while y <= e.year:
            y0, y1 = max(dt.date(y, 1, 1), b), min(dt.date(y, 12, 31), e)
            n = (y1 - y0).days + 1
            yillar[y] = round(sum(1 for g in gun if y0 <= g <= y1) / n, 3)
            y += 1
        oran = round(len(gun) / ((e - b).days + 1), 3)
        if en_iyi is None or oran > en_iyi['oran']:
            en_iyi = dict(kanal=cha, oran=oran, yil=yillar)
    if en_iyi: sonuc.setdefault(key, {}).update(en_iyi)
    print(key, json.dumps(sonuc.get(key), ensure_ascii=False)[:300], flush=True)
json.dump(sonuc, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
