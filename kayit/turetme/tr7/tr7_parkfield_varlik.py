#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 2, E2: Parkfield–Tohoku 2011 dalga formu VARLIK yoklaması (dondurmadan önce, 0 €).

Yalnız HTTP kodu ve bayt sayılır: yanıt gövdesi bellekte okunup uzunluğu alınır, ÇÖZÜLMEZ ve diske YAZILMAZ.
`tr7_parkfield_liste.csv`'deki her istasyon için listedeki Z kanalından (HHZ > BHZ > EHZ > SHZ; konum kodu listedeki
gibi, yoksa "--") iki 10 sn'lik dataselect isteği:
  R örneği: 2011-03-11T05:16:24 – 05:16:34 UTC  (R = [T0 − 3600 s, T0) ortası; T0 = 05:46:24)
  W örneği: 2011-03-11T06:29:20 – 06:29:30 UTC  (iz ortası W = 06:13:38–06:45:02 ortası)
Servis: NCEDC; NCEDC 204/404 (ya da 200 ve 0 bayt) dönerse aynı istek EarthScope'a.
Sınıflama: 200 ve >0 bayt = var; 204/404 = yok; 401/403 = kısıtlı (atlatılmaz); öteki = belirsiz (bir kez yeniden).
Nezaket: tek akış, istekler arası ≥0,3 sn; 429/503'te Retry-After (yoksa 30 sn × deneme), en çok 2 yeniden deneme;
genel User-Agent (kişi/proje adı yok).

Çıktı (bu dizin): tr7_parkfield_varlik.csv (istek başına), tr7_parkfield_varlik_ozet.json.
Kullanım: python3 -I -B tr7_parkfield_varlik.py [--yaz]
"""
import csv, hashlib, json, os, sys, time, urllib.request, urllib.error, urllib.parse

BURADA = os.path.dirname(os.path.abspath(__file__))
LISTE = os.path.join(BURADA, 'tr7_parkfield_liste.csv')
LISTE_SHA_V1 = 'cba4cea81a4b6b231133a99d0f2d19cce956a950885d7789390504c2aa471a77'
ORNEK = {'R': ('2011-03-11T05:16:24', '2011-03-11T05:16:34'),
         'W': ('2011-03-11T06:29:20', '2011-03-11T06:29:30')}
DS = {'ncedc': 'https://service.ncedc.org/fdsnws/dataselect/1/query?',
      'earthscope': 'https://service.earthscope.org/fdsnws/dataselect/1/query?'}
UA = 'fdsn-availability-probe/1.0 (python-urllib)'
ARA = 0.35
KANAL_SIRA = ['HHZ', 'BHZ', 'EHZ', 'SHZ']

_son = [0.0]


def iste(url):
    bekle = ARA - (time.time() - _son[0])
    if bekle > 0:
        time.sleep(bekle)
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            n = len(r.read())          # yalnız uzunluk; içerik çözülmez, yazılmaz
            kod, ra = r.status, None
    except urllib.error.HTTPError as e:
        kod, n, ra = e.code, 0, e.headers.get('Retry-After')
    except Exception as e:      # zaman aşımı, bağlantı
        kod, n, ra = -1, 0, None
    _son[0] = time.time()
    return kod, n, round(time.time() - t, 2), ra


def iste_nazik(url):
    for deneme in range(3):
        kod, n, sure, ra = iste(url)
        if kod in (429, 503) and deneme < 2:
            time.sleep(float(ra) if ra and ra.isdigit() else 30 * (deneme + 1))
            continue
        if kod not in (200, 204, 404, 401, 403, 429, 503) and deneme < 1:
            time.sleep(5)
            continue
        return kod, n, sure
    return kod, n, sure


def sinif(kod, n):
    if kod == 200 and n > 0:
        return 'var'
    if kod in (200, 204, 404):
        return 'yok'
    if kod in (401, 403):
        return 'kisitli'
    return 'belirsiz'


def kanal_sec(kanallar):
    ks = kanallar.split()
    for tip in KANAL_SIRA:
        for k in ks:
            if k.endswith(tip):
                loc, cha = (k.split('.') if '.' in k else ('', k))
                return loc, cha
    loc, cha = (ks[0].split('.') if '.' in ks[0] else ('', ks[0]))
    return loc, cha


def main():
    sha = hashlib.sha256(open(LISTE, 'rb').read()).hexdigest()
    if sha != LISTE_SHA_V1:
        sys.exit('DUR: tr7_parkfield_liste.csv sha256 sürüm 1 ile uyuşmuyor')
    ist = list(csv.DictReader(open(LISTE, encoding='utf-8')))
    satir = []
    for x in ist:
        loc, cha = kanal_sec(x['kanallar'])
        for ad, (t0, t1) in ORNEK.items():
            q = urllib.parse.urlencode(dict(net=x['ag'], sta=x['istasyon'], loc=loc or '--', cha=cha,
                                            start=t0, end=t1, nodata='404'))
            servis = 'ncedc'
            kod, n, sure = iste_nazik(DS['ncedc'] + q)
            if sinif(kod, n) == 'yok':
                servis = 'earthscope'
                kod2, n2, sure2 = iste_nazik(DS['earthscope'] + q)
                kod_nc = kod
                kod, n, sure = kod2, n2, sure2
            else:
                kod_nc = kod
            satir.append(dict(ag=x['ag'], istasyon=x['istasyon'], konum=loc, kanal=cha, ornek=ad, bas=t0, son=t1,
                              ncedc_http=kod_nc, servis=servis, http=kod, bayt=n, sure_s=sure, durum=sinif(kod, n)))
            print(x['ag'], x['istasyon'], cha, ad, servis, kod, n, flush=True)
    durum = {}
    for s in satir:
        durum.setdefault((s['ag'], s['istasyon']), {})[s['ornek']] = s['durum']
    sira = [(x['ag'], x['istasyon']) for x in ist]          # liste ize uzaklık sırasında
    ikisi = [k for k in sira if durum[k].get('R') == 'var' and durum[k].get('W') == 'var']
    ozet = dict(liste_sha256_v1=sha, istek=len(satir),
                http={str(k): sum(1 for s in satir if s['http'] == k) for k in sorted({s['http'] for s in satir})},
                servis={k: sum(1 for s in satir if s['servis'] == k) for k in DS},
                bayt_toplam=sum(s['bayt'] for s in satir),
                var_R=sum(1 for k in sira if durum[k].get('R') == 'var'),
                var_W=sum(1 for k in sira if durum[k].get('W') == 'var'),
                var_R_ve_W=len(ikisi),
                var_R_ve_W_ilk12_listede=sum(1 for k in sira[:12] if k in ikisi),
                var_R_ve_W_istasyonlar=['.'.join(k) for k in ikisi],
                kisitli=sum(1 for s in satir if s['durum'] == 'kisitli'),
                belirsiz=sum(1 for s in satir if s['durum'] == 'belirsiz'),
                hukum=('devam (>=3)' if len(ikisi) >= 3 else 'DONDURULAMAZ (<3)'))
    js = json.dumps(ozet, ensure_ascii=False, indent=1)
    print(js)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, 'tr7_parkfield_varlik.csv'), 'x', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(satir[0].keys()))
            w.writeheader()
            w.writerows(satir)
        with open(os.path.join(BURADA, 'tr7_parkfield_varlik_ozet.json'), 'x', encoding='utf-8') as f:
            f.write(js + '\n')


if __name__ == '__main__':
    main()
