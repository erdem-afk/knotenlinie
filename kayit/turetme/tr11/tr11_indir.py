#!/usr/bin/env python3
"""TR-11: küme listesindeki istasyonların NGL IGS20 tenv3 dosyalarını indirir (depo dışına).

  https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{STA}.tenv3

- Liste `tr11_kume_listesi.json`; sha256 denetlenir (79f6cf0f…27cbbd), uyuşmazsa durur.
- Marmara kutusu (39,5–42,0° K, 26,0–31,5° D): listedeki her istasyon DataHoldings koordinatlarıyla denetlenir; kutu
  içinde ya da DataHoldings'te olmayan bir istasyon varsa HİÇBİR şey indirilmeden durur. Listede olmayan istasyon
  indirilmez.
- 4 eşzamanlı bağlantı, istasyon başına 3 deneme, üstel bekleme (5, 10, 20 sn). Dosya önce `.part` adıyla yazılır,
  bitince yeniden adlandırılır. Yeniden başlatılabilir: hedefte dosya varsa ve manifestteki sha256 ile uyuşuyorsa
  yeniden indirilmez.
- Manifest (`<hedef>/tr11_indirme_manifest.json`): istasyon başına durum (tamam/hata), sha256, bayt, zaman, hata.
  Başarısız istasyonların payı %5'i aşarsa (K6) bir kez, yalnız başarısızlar için yeniden deneme turu yapılır;
  sonra pay yine yazılır (koşu kodu %5'i aşan payda durur).
- Ö4: Marmara kutusuna 150 km'den yakın istasyonlar yazdırılır; dosyaları koşu kodu yalnız w1'e kadar okur ve
  koşudan sonra siler.
- İçerik doğrulaması yalnız ilk satırdadır (başlık "site ..." ya da istasyon adı); seri okunmaz.

Kullanım:
  python3 -I -B tr11_indir.py --hedef <dizin> [--ustveri /mnt/project-files/turetme/tr11-ustveri] [--kuru]
  --kuru: hiçbir ağ isteği yapmaz; yalnız denetimleri koşar ve istasyon sayısını yazar.
"""
import argparse, concurrent.futures as cf, datetime as dt, hashlib, json, math, os, ssl, sys, threading, time
import urllib.request, urllib.error

BURADA = os.path.dirname(os.path.abspath(__file__))
LISTE_SHA256 = '79f6cf0f9a1a11d932617b20c7b866bb5125a3acea62d35325af9364f027cbbd'
DH_SHA16 = '4a98b65ad74c425b'
URL = 'https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{}.tenv3'
MARMARA = (39.5, 42.0, 26.0, 31.5)
ESZAMAN, DENEME, BEKLE0 = 4, 3, 5.0
HATA_PAY = 0.05
MANIFEST = 'tr11_indirme_manifest.json'


def sha256_dosya(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def sar(lo): return (lo + 180) % 360 - 180


def hav(la1, lo1, la2, lo2):
    la1, lo1, la2, lo2 = map(math.radians, (la1, lo1, la2, lo2))
    a = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(min(1.0, max(0.0, a))))


def kutuda(la, lo): return MARMARA[0] <= la <= MARMARA[1] and MARMARA[2] <= lo <= MARMARA[3]


def kutu_uzaklik(la, lo):
    if kutuda(la, lo):
        return 0.0
    a, b, c, d = MARMARA
    pts = [(a + (b - a) * i / 500, x) for i in range(501) for x in (c, d)]
    pts += [(y, c + (d - c) * i / 1100) for i in range(1101) for y in (a, b)]
    return min(hav(la, lo, p, q) for p, q in pts)


def dataholdings(yol):
    out = {}
    with open(yol) as f:
        next(f)
        for l in f:
            p = l.split()
            try:
                out[p[0]] = (float(p[1]), sar(float(p[2])))
            except Exception:
                continue
    return out


def denetle(liste_yol, ustveri):
    if sha256_dosya(liste_yol) != LISTE_SHA256:
        sys.exit('DUR: küme listesi sha256 uyuşmuyor')
    dh_yol = os.path.join(ustveri, 'DataHoldings.txt')
    if sha256_dosya(dh_yol)[:16] != DH_SHA16:
        sys.exit('DUR: DataHoldings.txt sha256 uyuşmuyor')
    liste = json.load(open(liste_yol))
    ist = sorted({s for k in liste for s in k['y'] + k['r']})
    ko = dataholdings(dh_yol)
    yok = [s for s in ist if s not in ko]
    if yok:
        sys.exit(f'DUR: DataHoldings\'te olmayan istasyon: {yok[:10]}')
    kutu = [s for s in ist if kutuda(*ko[s])]
    if kutu:
        sys.exit(f'DUR: listede Marmara kutusu istasyonu var, hiçbir şey indirilmedi: {kutu}')
    o4 = sorted((s, round(kutu_uzaklik(*ko[s]), 1)) for s in ist if kutu_uzaklik(*ko[s]) < 150.0)
    return ist, o4


def ssl_baglam():
    ca = os.environ.get('SSL_CERT_FILE') or os.environ.get('REQUESTS_CA_BUNDLE') or os.environ.get('CURL_CA_BUNDLE')
    return ssl.create_default_context(cafile=ca) if ca and os.path.exists(ca) else ssl.create_default_context()


def indir_bir(sta, hedef, baglam, izinli):
    if sta not in izinli:                                  # savunma: listede olmayan istasyon indirilmez
        raise RuntimeError(f'izinsiz istasyon {sta}')
    yol = os.path.join(hedef, f'{sta}.tenv3')
    son_hata = None
    for d in range(DENEME):
        try:
            req = urllib.request.Request(URL.format(sta), headers={'User-Agent': 'tr11-indir/1.0'})
            with urllib.request.urlopen(req, timeout=120, context=baglam) as r, open(yol + '.part', 'wb') as f:
                while True:
                    b = r.read(1 << 20)
                    if not b:
                        break
                    f.write(b)
            with open(yol + '.part', 'rb') as f:
                ilk = f.readline().decode('ascii', 'replace').split()
            if not ilk or ilk[0] not in ('site', sta):
                raise ValueError(f'tenv3 gibi görünmüyor (ilk sözcük {ilk[:1]})')
            os.replace(yol + '.part', yol)
            return dict(durum='tamam', sha256=sha256_dosya(yol), bayt=os.path.getsize(yol),
                        zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), deneme=d + 1)
        except Exception as e:                             # noqa: BLE001
            son_hata = f'{type(e).__name__}: {e}'
            if os.path.exists(yol + '.part'):
                os.remove(yol + '.part')
            if isinstance(e, urllib.error.HTTPError) and e.code == 404:
                break
            if d < DENEME - 1:
                time.sleep(BEKLE0 * 2 ** d)
    return dict(durum='hata', hata=son_hata, zaman=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'))


def manifest_yaz(yol, man):
    tmp = yol + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(man, f, indent=1, sort_keys=True)
    os.replace(tmp, yol)


def tur(isler, hedef, man, kilit, man_yol, izinli):
    baglam = ssl_baglam()
    n = [0]
    with cf.ThreadPoolExecutor(ESZAMAN) as ex:
        fut = {ex.submit(indir_bir, s, hedef, baglam, izinli): s for s in isler}
        for f in cf.as_completed(fut):
            s = fut[f]
            with kilit:
                man['istasyonlar'][s] = f.result()
                n[0] += 1
                if n[0] % 100 == 0:
                    manifest_yaz(man_yol, man)
                    print(f'  {n[0]}/{len(isler)}', flush=True)
    manifest_yaz(man_yol, man)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--hedef', required=True)
    p.add_argument('--ustveri', default='/mnt/project-files/turetme/tr11-ustveri')
    p.add_argument('--liste', default=os.path.join(BURADA, 'tr11_kume_listesi.json'))
    p.add_argument('--kuru', action='store_true')
    a = p.parse_args(argv)
    ist, o4 = denetle(a.liste, a.ustveri)
    print(f'listede {len(ist)} istasyon; Marmara kutusunda 0 (DataHoldings koordinatlarıyla denetlendi)')
    print(f'Ö4 (kutuya < 150 km): {o4}')
    if a.kuru:
        print('kuru kip: ağ isteği yapılmadı')
        return 0
    os.makedirs(a.hedef, exist_ok=True)
    man_yol = os.path.join(a.hedef, MANIFEST)
    man = json.load(open(man_yol)) if os.path.exists(man_yol) else {}
    man.setdefault('istasyonlar', {})
    man.update(liste_sha256=LISTE_SHA256, url=URL, baslangic=man.get('baslangic') or
               dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'))
    izinli = set(ist)
    kalan = []
    for s in ist:
        v = man['istasyonlar'].get(s)
        yol = os.path.join(a.hedef, f'{s}.tenv3')
        if v and v.get('durum') == 'tamam' and os.path.exists(yol) and sha256_dosya(yol) == v.get('sha256'):
            continue
        kalan.append(s)
    print(f'indirilecek {len(kalan)} (önceden tamam {len(ist) - len(kalan)})')
    kilit = threading.Lock()
    tur(kalan, a.hedef, man, kilit, man_yol, izinli)
    hata = [s for s in ist if man['istasyonlar'].get(s, {}).get('durum') != 'tamam']
    pay = len(hata) / len(ist)
    print(f'başarısız {len(hata)} (%{100 * pay:.2f})')
    if pay > HATA_PAY and not man.get('yeniden_deneme_turu'):
        print('pay %5\'i aşıyor: tek yeniden deneme turu (K6)')
        time.sleep(60)
        man['yeniden_deneme_turu'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
        tur(hata, a.hedef, man, kilit, man_yol, izinli)
        hata = [s for s in ist if man['istasyonlar'].get(s, {}).get('durum') != 'tamam']
        pay = len(hata) / len(ist)
        print(f'yeniden deneme sonrası başarısız {len(hata)} (%{100 * pay:.2f})')
    man['bitis'] = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
    man['basarisiz'] = hata
    man['basarisiz_pay'] = pay
    manifest_yaz(man_yol, man)
    print(f'manifest: {man_yol}')
    return 0 if pay <= HATA_PAY else 3


if __name__ == '__main__':
    sys.exit(main())
