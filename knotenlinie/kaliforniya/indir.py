"""ANSS ComCat FDSN'den Kaliforniya (RELM + 1 derece tampon) kataloğunu indirir; yalnız <=2020.

Yıllık CSV: `<hedef>/deprem/comcat_<yil>.csv` (ComCat 'time' sütunu, `scripts/muhur.py` okur).
Her sorgu `endtime` <= 2020-12-31T23:59:59 ile gider; 20000 satır sınırına çarpan pencere ikiye bölünür.
Yan kayıt `<hedef>/kayit.json`: yıl başına satır sayısı ve sha256.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = 'https://earthquake.usgs.gov/fdsnws/event/1/query'
UA = 'knotenlinie (+https://github.com/erdem-afk/knotenlinie)'
KUTU = dict(minlatitude=30.55, maxlatitude=43.95, minlongitude=-126.35, maxlongitude=-112.15)
SON = datetime(2020, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
SINIR = 20000


def _bicim(t: datetime) -> str:
    return t.strftime('%Y-%m-%dT%H:%M:%S')


def sorgu(bas: datetime, bit: datetime, minmag: float, deneme: int = 4) -> str:
    """[bas, bit] (bit dahil, saniye) pencerenin ham CSV metni."""
    if bit > SON:
        raise ValueError('pencere 2020-12-31T23:59:59 sonrasına uzanıyor')
    p = dict(format='csv', eventtype='earthquake', orderby='time-asc', minmagnitude=minmag,
             starttime=_bicim(bas), endtime=_bicim(bit), limit=SINIR, **KUTU)
    for i in range(deneme):
        try:
            with urlopen(Request(f'{URL}?{urlencode(p)}', headers={'User-Agent': UA}), timeout=300) as y:
                return y.read().decode('utf-8', 'replace')
        except HTTPError as e:
            if e.code == 204:
                return ''
            if i == deneme - 1:
                raise
            time.sleep(5 * (i + 1))
    return ''


def satirlar(metin: str):
    if not metin.strip():
        return None, []
    r = list(csv.reader(io.StringIO(metin)))
    return r[0], r[1:]


def pencere_indir(bas, bit, minmag):
    """Sınıra çarparsa ikiye bölerek (başlık, satırlar) döndürür."""
    bas_, s = satirlar(sorgu(bas, bit, minmag))
    if len(s) < SINIR:
        return bas_, s
    orta = bas + (bit - bas) / 2
    orta = orta.replace(microsecond=0)
    b1, s1 = pencere_indir(bas, orta, minmag)
    b2, s2 = pencere_indir(orta + timedelta(seconds=1), bit, minmag)
    return b1, s1 + s2


def yil_indir(yil: int, minmag: float):
    bas = datetime(yil, 1, 1, tzinfo=timezone.utc)
    bit = min(SON, datetime(yil, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
    baslik, satir = None, []
    ay = bas
    while ay <= bit:
        son = datetime(ay.year + (ay.month == 12), ay.month % 12 + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
        son = min(son, bit)
        b, s = pencere_indir(ay, son, minmag)
        baslik = baslik or b
        satir += s
        ay = son + timedelta(seconds=1)
    gorulen = {r[0] for r in satir}
    tekil, goruldu = [], set()
    for r in satir:                     # pencere sınırında çift olay olmasın (id sütunu)
        k = (r[baslik.index('id')] if baslik and 'id' in baslik else r[0])
        if k in goruldu:
            continue
        goruldu.add(k)
        tekil.append(r)
    return baslik, tekil


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument('hedef', type=Path)
    a.add_argument('--ilk', type=int, default=1981)
    a.add_argument('--son', type=int, default=2020)
    a.add_argument('--minmag', type=float, default=2.5)
    a = a.parse_args(argv)
    if a.son > 2020:
        raise SystemExit('mühür: son yıl en çok 2020')
    d = a.hedef / 'deprem'
    d.mkdir(parents=True, exist_ok=True)
    kf = a.hedef / 'kayit.json'
    kayit = json.loads(kf.read_text()) if kf.exists() else {}
    for yil in range(a.ilk, a.son + 1):
        yol = d / f'comcat_{yil}.csv'
        if yol.exists() and str(yil) in kayit:
            continue
        baslik, s = yil_indir(yil, a.minmag)
        with open(yol, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(baslik)
            w.writerows(s)
        kayit[str(yil)] = dict(satir=len(s), sha256=hashlib.sha256(yol.read_bytes()).hexdigest(),
                               indirildi=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'))
        kf.write_text(json.dumps(kayit, indent=1))
        print(yil, len(s), flush=True)


if __name__ == '__main__':
    main()
