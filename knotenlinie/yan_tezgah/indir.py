"""SCEDC ve GeoNet FDSN'den yan bölge kataloglarını indirir (<=2020-12-31, mühür 2021).

Yıllık dosyalar `deprem/yan-bolge/<bolge>/<onek>_<yil>.txt`, normalleştirilmiş
14 sütunlu ISIDe biçimi (boşluksuz `|`), böylece `scripts/muhur.py` değişmeden tarar.
Yan kayıt (`yan-kayit/`) yalnız sayı taşır. 2021+ satır ne istenir ne yazılır;
görülürse sayılır, dosyaya girmez ve çağıran uyarılır.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from knotenlinie.yollar import VERI

UA = 'knotenlinie (+https://github.com/erdem-afk/knotenlinie)'
BASLIK = ("#EventID|Time|Latitude|Longitude|Depth/km|Author|Catalog|Contributor|"
          "ContributorID|MagType|Magnitude|MagAuthor|EventLocationName|EventType")

BOLGELER = {
    'scsn': dict(
        url='https://service.scedc.caltech.edu/fdsnws/event/1/query',
        onek='ca-scsn', ilk_yil=1996, son_yil=2020, minmag=1.0, maxdepth=30,
        kutu=(32.5, 36.5, -121.0, -114.5), satir_siniri=None, kaynak='SCEDC/SCSN'),
    'geonet': dict(
        url='https://service.geonet.org.nz/fdsnws/event/1/query',
        onek='nz-geonet', ilk_yil=2002, son_yil=2020, minmag=2.0, maxdepth=40,
        kutu=(-43.8, -37.0, 171.5, 178.5), satir_siniri=10000, kaynak='GeoNet'),
}

# Ham başlık adı -> normalleştirilmiş ad. SCEDC'nin 'Longtitude' yazımı ve
# eksik Contributor/ContributorID/EventType sütunları burada kapanır.
ESLEME = {
    'eventid': 'EventID', 'time': 'Time', 'latitude': 'Latitude',
    'longitude': 'Longitude', 'longtitude': 'Longitude', 'depth/km': 'Depth/km',
    'author': 'Author', 'catalog': 'Catalog', 'contributor': 'Contributor',
    'contributorid': 'ContributorID', 'magtype': 'MagType', 'magnitude': 'Magnitude',
    'magauthor': 'MagAuthor', 'eventlocationname': 'EventLocationName',
    'eventtype': 'EventType',
}


class MuhurIhlali(ValueError):
    """2021-01-01 ve sonrası satır görüldü."""


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blok in iter(lambda: f.read(1 << 20), b''):
            h.update(blok)
    return h.hexdigest()


def _pencere(bas: datetime, bit: datetime) -> dict:
    """FDSN parametreleri; bit her zaman 2021-01-01'den önce biter."""
    if bit > datetime(2021, 1, 1, tzinfo=timezone.utc):
        raise MuhurIhlali('pencere 2021 sınırını aşıyor')
    return dict(starttime=bas.strftime('%Y-%m-%dT%H:%M:%S'),
                endtime=(bit - timedelta(microseconds=1)).strftime('%Y-%m-%dT%H:%M:%S.%f'))


def _sorgu(url: str, params: dict, zaman_asimi: float = 300.0) -> str:
    tam = f'{url}?{urlencode(params)}'
    try:
        with urlopen(Request(tam, headers={'User-Agent': UA}), timeout=zaman_asimi) as y:
            return y.read().decode('utf-8', 'replace')
    except HTTPError as e:
        raise


def _satirlari_coz(metin: str) -> list[list[str]]:
    """Ham FDSN metnini başlık-adlı 14 sütuna çevirir; boş satırları atar."""
    satirlar = [s for s in metin.splitlines() if s.strip()]
    if not satirlar:
        return []
    ham_baslik = satirlar[0].lstrip('#').split('|')
    adlar = [ESLEME.get(h.strip().lower(), h.strip()) for h in ham_baslik]
    if 'Time' not in adlar:
        raise MuhurIhlali(f'FDSN başlığında Time yok: {ham_baslik[:4]}')
    cikti = []
    for satir in satirlar[1:]:
        hucre = [x.strip() for x in satir.split('|')]
        if len(hucre) != len(adlar):
            continue
        kayit = dict(zip(adlar, hucre))
        if not kayit.get('EventID') or not kayit.get('Time'):
            continue
        cikti.append([kayit.get(s, '') for s in
                      ('EventID', 'Time', 'Latitude', 'Longitude', 'Depth/km', 'Author',
                       'Catalog', 'Contributor', 'ContributorID', 'MagType', 'Magnitude',
                       'MagAuthor', 'EventLocationName', 'EventType')])
    return cikti


def _yil(satir: list[str]) -> int:
    return int(satir[1].strip()[:4])


def _bolge_indir(bolge: str, kok: Path, *, bekle: float = 0.2, sinir_ay: int | None = None,
                 yil_araligi=None, devam: bool = False) -> dict:
    """Bir bölgeyi ay ay indirir; pencere taşarsa ikiye böler; yıllık dosya yazar."""
    b = BOLGELER[bolge]
    la0, la1, lo0, lo1 = b['kutu']
    veri = kok / 'deprem' / 'yan-bolge' / bolge
    kayit = kok / 'yan-kayit' / 'yan-bolge' / bolge
    veri.mkdir(parents=True, exist_ok=True)
    kayit.mkdir(parents=True, exist_ok=True)
    ilk, son = (b['ilk_yil'], b['son_yil']) if yil_araligi is None else yil_araligi
    yillar = {y: [] for y in range(ilk, son + 1)}
    atlanan = set()
    atilan, pencereler, ornek_url = 0, 0, None
    t0 = time.monotonic()

    def cek(bas: datetime, bit: datetime) -> list[list[str]]:
        nonlocal atilan, pencereler, ornek_url
        p = _pencere(bas, bit)
        tam = dict(p, minlatitude=la0, maxlatitude=la1, minlongitude=lo0,
                   maxlongitude=lo1, minmagnitude=b['minmag'], maxdepth=b['maxdepth'],
                   orderby='time-asc', format='text')
        if ornek_url is None:
            ornek_url = f"{b['url']}?{urlencode(tam)}"
        try:
            metin = _sorgu(b['url'], tam)
        except HTTPError as e:
            if e.code in (413, 400, 500, 503) and (bit - bas) > timedelta(minutes=10):
                orta = bas + (bit - bas) / 2
                return cek(bas, orta) + cek(orta, bit)
            raise
        rows = _satirlari_coz(metin)
        if b['satir_siniri'] and len(rows) >= b['satir_siniri'] and (bit - bas) > timedelta(minutes=10):
            orta = bas + (bit - bas) / 2
            return cek(bas, orta) + cek(orta, bit)
        pencereler += 1
        temiz = []
        for r in rows:
            if _yil(r) >= 2021:
                atilan += 1
                continue
            temiz.append(r)
        return temiz

    for y in range(ilk, son + 1):
        hedef0 = veri / f"{b['onek']}_{y}.txt"
        if devam and hedef0.exists():
            atlanan.add(y)
            print(f'{bolge} {y}: atlandı (var)', flush=True)
            continue
        if sinir_ay is not None:
            aylar = range(1, sinir_ay + 1)
        else:
            aylar = range(1, 13)
        for ay in aylar:
            bas = datetime(y, ay, 1, tzinfo=timezone.utc)
            bit = datetime(y + 1, 1, 1, tzinfo=timezone.utc) if ay == 12 else datetime(y, ay + 1, 1, tzinfo=timezone.utc)
            for satir in cek(bas, bit):
                yy = _yil(satir)
                if yy < y or yy > y:
                    raise MuhurIhlali(f'{bolge} {y} dosyasına {yy} satırı geldi')
                yillar[y].append(satir)
            if bekle:
                time.sleep(bekle)
        print(f'{bolge} {y}: {len(yillar[y])} satır, {time.monotonic()-t0:.0f}s', flush=True)
        if sinir_ay is not None:
            break

    dosyalar = []
    for y, satirlar in yillar.items():
        if y in atlanan:
            continue
        hedef = veri / f"{b['onek']}_{y}.txt"
        gecici = hedef.with_suffix('.txt.tmp')
        with open(gecici, 'w', encoding='utf-8') as f:
            f.write(BASLIK + '\n')
            for s in satirlar:
                f.write('|'.join(s) + '\n')
        gecici.replace(hedef)
        mag_tur = {}
        for s in satirlar:
            mt = s[9].strip() or '(bos)'
            mag_tur[mt] = mag_tur.get(mt, 0) + 1
        side = dict(tur='knotenlinie-yan-bolge', bolge=bolge, kaynak=b['kaynak'],
                    kaynak_url=b['url'], sorgu_ornegi=ornek_url, cikti=str(hedef),
                    cikti_sha256=sha256(hedef), kesim_yili=2020, yil=y, satir=len(satirlar),
                    atilan_2021_sonrasi=atilan, mag_turu_sayimi=mag_tur,
                    kutu=list(b['kutu']), derinlik_max_km=b['maxdepth'], minmag=b['minmag'],
                    pencere_sayisi=pencereler, utc=datetime.now(timezone.utc).isoformat())
        (kayit / f'{b["onek"]}_{y}.json').write_text(
            json.dumps(side, indent=1, sort_keys=True) + '\n', encoding='utf-8')
        dosyalar.append(hedef)

    rapor = dict(bolge=bolge, dosya=len(dosyalar), satir=sum(len(v) for v in yillar.values()),
                 atilan_2021_sonrasi=atilan, pencere=pencereler, urls=ornek_url,
                 duvar_saniye=time.monotonic() - t0, dosyalar=[str(p) for p in dosyalar])
    return rapor


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kok', type=Path, default=VERI / 'yan')
    ap.add_argument('--bolge', choices=sorted(BOLGELER), action='append')
    ap.add_argument('--bekle', type=float, default=0.2)
    ap.add_argument('--sinir-ay', type=int, default=None, help='yalnız ilk N ay (deneme)')
    ap.add_argument('--ilk-yil', type=int, default=None)
    ap.add_argument('--son-yil', type=int, default=None)
    ap.add_argument('--devam', action='store_true', help='var olan yıl dosyalarını atla')
    args = ap.parse_args(argv)
    bolgeler = args.bolge or ['scsn', 'geonet']
    raporlar = []
    for bolge in bolgeler:
        b = BOLGELER[bolge]
        aralik = None
        if args.ilk_yil is not None or args.son_yil is not None:
            aralik = (args.ilk_yil or b['ilk_yil'], args.son_yil or b['son_yil'])
        r = _bolge_indir(bolge, args.kok, bekle=args.bekle, sinir_ay=args.sinir_ay, yil_araligi=aralik, devam=args.devam)
        print(json.dumps(r, ensure_ascii=False))
        raporlar.append(r)
    args.kok.mkdir(parents=True, exist_ok=True)
    (args.kok / 'indirme-raporu.json').write_text(
        json.dumps(raporlar, indent=1, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
