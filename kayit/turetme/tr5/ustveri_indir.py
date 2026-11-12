#!/usr/bin/env python3
"""TR-5 / TR-4: FDSN istasyon ÜSTVERİSİNİN indirilmesi (dalga formu indirilmez).

Yalnız istasyon/kanal epokları (metin biçimi) ve kısıtlı/açık ayrımı alınır. Deprem kataloğu SORGULANMAZ
(hazır ComCat dosyaları kullanılır, bitiş 2025-12-31). Erişim hatası (403, zaman aşımı, TLS) atlatılmaz:
durum dosyaya yazılır, o merkez sayımda "bilinmiyor" olur.

Kullanım: python3 -I -B ustveri_indir.py <çıktı_dizini>
Çıktılar:
  fedcatalog_kanal.txt           EarthScope fedcatalog: BHZ,HHZ kanal epokları (bütün federe merkezler)
  ek_<merkez>_kanal.txt          fedcatalog'da olmayan merkezlerin kendi istasyon servisi (GeoNet, IESDMC, ...)
  acik_<merkez>.txt / tum_<merkez>.txt   istasyon düzeyi, includerestricted=false / true
  durum.json                     her isteğin HTTP durumu, bayt, süre
"""
import json, os, sys, time, urllib.request, urllib.error, ssl

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
Q = 'cha=BHZ,HHZ&format=text&endafter=1995-01-01&startbefore=2021-01-01'
FED = 'https://service.earthscope.org/irisws/fedcatalog/1/query?level=channel&' + Q

# FDSN datacenters kaydından (www.fdsn.org/ws/datacenters, 12 Kasım 2026) istasyon servisleri.
MERKEZ = {
    'IRISDMC': 'https://service.earthscope.org/fdsnws/station/1/',
    'AUSPASS': 'https://auspass.edu.au/fdsnws/station/1/',
    'BGR': 'https://eida.bgr.de/fdsnws/station/1/',
    'EPOSFR': 'https://seisdata.epos-france.fr/fdsnws/station/1/',
    'GEOFON': 'https://geofon.gfz.de/fdsnws/station/1/',
    'ICGC': 'https://ws.icgc.cat/fdsnws/station/1/',
    'IGN': 'http://fdsnws.sismologia.ign.es/fdsnws/station/1/',
    'INGV': 'https://webservices.ingv.it/fdsnws/station/1/',
    'IPGP': 'http://ws.ipgp.fr/fdsnws/station/1/',
    'KOERI': 'https://eida.koeri.boun.edu.tr/fdsnws/station/1/',
    'LMU': 'https://erde.geophysik.uni-muenchen.de/fdsnws/station/1/',
    'NCEDC': 'https://service.ncedc.org/fdsnws/station/1/',
    'NIEP': 'https://eida-sc3.infp.ro/fdsnws/station/1/',
    'NOA': 'https://eida.gein.noa.gr/fdsnws/station/1/',
    'ORFEUS': 'https://www.orfeus-eu.org/fdsnws/station/1/',
    'SCEDC': 'https://service.scedc.caltech.edu/fdsnws/station/1/',
    'SED': 'https://eida.ethz.ch/fdsnws/station/1/',
    'UIB-NORSAR': 'https://eida.geo.uib.no/fdsnws/station/1/',
    'USPSC': 'http://seisrequest.iag.usp.br/fdsnws/station/1/',
    # fedcatalog'da görünmeyenler (ek kanal listesi de alınır)
    'GEONET': 'https://service.geonet.org.nz/fdsnws/station/1/',
    'IESDMC': 'http://batsws.earth.sinica.edu.tw/fdsnws/station/1/',
    'NRCAN': 'https://earthquakescanada.nrcan.gc.ca/fdsnws/station/1/',
    'KAGSR': 'http://sdis.emsd.ru/fdsnws/station/1/',
    'BGS': 'https://eida.bgs.ac.uk/fdsnws/station/1/',
    'KIT': 'http://ws.gpi.kit.edu/fdsnws/station/1/',
    'OSDC': 'http://osdc.obslab.cn/fdsnws/station/1/',
}
EK = ['GEONET', 'IESDMC', 'NRCAN', 'KAGSR', 'BGS', 'KIT', 'OSDC']

durum = {}
def al(ad, url, dosya, zaman=300):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'knotenlinie-ustveri/1.0'})
        with urllib.request.urlopen(req, timeout=zaman) as r:
            b = r.read(); kod = r.status
    except urllib.error.HTTPError as e:
        b, kod = b'', e.code
    except Exception as e:
        b, kod = b'', type(e).__name__ + ': ' + str(e)[:120]
    if b:
        with open(os.path.join(OUT, dosya), 'wb') as f: f.write(b)
    durum[ad] = dict(url=url, kod=kod, bayt=len(b), sn=round(time.time() - t0, 1))
    print(ad, kod, len(b), flush=True)

al('fedcatalog', FED, 'fedcatalog_kanal.txt', 590)
for m in EK:
    al('ek_' + m, MERKEZ[m] + 'query?level=channel&' + Q, f'ek_{m}_kanal.txt', 300)
for m, u in MERKEZ.items():
    for r, on in (('false', 'acik'), ('true', 'tum')):
        al(f'{on}_{m}', u + f'query?level=station&includerestricted={r}&' + Q, f'{on}_{m}.txt', 300)
with open(os.path.join(OUT, 'durum.json'), 'w') as f:
    json.dump(durum, f, indent=1, ensure_ascii=False)
