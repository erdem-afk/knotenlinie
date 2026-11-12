#!/usr/bin/env python3
"""TR-10b veri adımı (ön kayıt sürüm 2 §2.4 madde 2–5): aday listesindeki 35 istasyonun sayfadaki DAY (16), 10MIN
(21) ve MIC (29) bağlantılarını (66 dosya) depo DIŞINA indirir ve sha256 manifestini yazar.

BU BETİK KOD İNCELEMESİNDEN ÖNCE ÇALIŞTIRILMAZ (§14 madde 4–5).

- Dosya listesi yalnız `tr10b_listeler.json`'dan gelir; liste ön kaydın kanonik sha256'larıyla denetlenir
  (tr10b_listeler.listeleri_yukle) ve listeler JSON'unun sha256'sı sabitle karşılaştırılır. Listede olmayan URL
  indirilmez.
- Dosyaların İÇERİĞİ açılmaz, ayrıştırılmaz: yalnız bayt olarak yazılır ve sha256'sı alınır.
- Sırayla, istekler arasında 2 sn; genel User-Agent; dosya başına en çok 3 deneme (üstel bekleme). HTTP 401/403/404
  yeniden denenmez ve atlatılmaz; dosya "hata" olarak kayda geçer.
- §2.4 madde 3: başarısız dosyaların payı %5'i aşarsa yalnız başarısızlar için TEK bir yeniden deneme turu yapılır;
  yine aşarsa manifest yazılır ve çıkış kodu 3'tür (koşu kodu %5'i aşan payda durur).
- Manifest (varsayılan kayit/turetme/tr10b/tr10b_manifest_veri.json): URL, yerel ad, boy, Last-Modified, sha256,
  indirme zamanı, deneme; bellekte kurulur ve "x" kipinde bir kez yazılır (varsa durur: tek indirme anı, §2.4
  madde 5). Hedef dizin depo içindeyse durur. Hedef dizin boş olmalıdır.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr10b/tr10b_indir.py --hedef <depo_disi_dizin> [--manifest ...] [--kuru]
  --kuru: ağ isteği yapmaz; yalnız listeyi denetler ve dosya sayısını yazar.
  --url-onek ESKI=YENI: yalnız sınama içindir (yerel yapay sunucu); manifestte özgün URL yazılır.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr10b_listeler as TL  # noqa: E402

LISTELER_JSON_SHA = "d0c2246007c25f11027cc3325ff3cfa53b3984296d0cf6c82f30e8dacffdcba5"
MANIFEST = os.path.join(BURA, "tr10b_manifest_veri.json")
TURLER = ("DAY", "10MIN", "MIC")
UA = "Mozilla/5.0 (compatible; data-fetch)"
DENEME = 3
HATA_PAY = 0.05


def zaman():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def dosya_listesi(json_yol=TL.JSON_YOL):
    T = TL.listeleri_yukle(json_yol=json_yol)
    if T["json_sha256"] != LISTELER_JSON_SHA:
        raise SystemExit("DUR: tr10b_listeler.json sha256 uyuşmuyor")
    out = []
    for k in sorted(T["istasyon"]):
        for t in TURLER:
            for u in T["istasyon"][k]["dosya"][t]:
                out.append(dict(url=u, tur=t, istasyon=k, yerel=f"{t}/{u.rsplit('/', 1)[1]}"))
    if len(out) != 66 or len({x["yerel"] for x in out}) != 66:
        raise SystemExit(f"DUR: dosya listesi 66 değil ya da yerel adlar çakışıyor ({len(out)})")
    return out


def ssl_baglam():
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return ssl.create_default_context(cafile=ca) if ca and os.path.exists(ca) else ssl.create_default_context()


def indir_bir(x, hedef, baglam, url_onek=None, bekle=2.0):
    url = x["url"]
    if url_onek:
        eski, yeni = url_onek
        assert url.startswith(eski)
        url = yeni + url[len(eski):]
    yol = os.path.join(hedef, x["yerel"])
    son = None
    for d in range(DENEME):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            kw = dict(context=baglam) if url.startswith("https:") else {}
            with urllib.request.urlopen(req, timeout=120, **kw) as r:
                lm = r.headers.get("Last-Modified", "")
                h = hashlib.sha256()
                n = 0
                with open(yol + ".part", "wb") as f:
                    for b in iter(lambda: r.read(1 << 20), b""):
                        f.write(b)
                        h.update(b)
                        n += len(b)
            os.replace(yol + ".part", yol)
            return dict(x, durum="tamam", boy=n, last_modified=lm, sha256=h.hexdigest(), zaman=zaman(),
                        deneme=d + 1)
        except urllib.error.HTTPError as e:
            son = f"HTTP {e.code}"
            if e.code in (401, 403, 404):
                break
        except Exception as e:                       # noqa: BLE001
            son = f"{type(e).__name__}: {e}"
        finally:
            if os.path.exists(yol + ".part"):
                os.remove(yol + ".part")
        if d < DENEME - 1:
            time.sleep(bekle * 2 ** d)
    return dict(x, durum="hata", hata=son, zaman=zaman())


def tur(isler, hedef, kayit, url_onek, bekle):
    baglam = ssl_baglam()
    for x in isler:
        kayit[x["url"]] = indir_bir(x, hedef, baglam, url_onek, bekle)
        r = kayit[x["url"]]
        print(r["durum"], r.get("boy", r.get("hata")), x["yerel"], flush=True)
        time.sleep(bekle)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--hedef", required=True)
    p.add_argument("--manifest", default=MANIFEST)
    p.add_argument("--listeler", default=TL.JSON_YOL)
    p.add_argument("--kuru", action="store_true")
    p.add_argument("--url-onek", default=None)
    p.add_argument("--bekle", type=float, default=2.0)
    a = p.parse_args(argv)
    ls = dosya_listesi(a.listeler)
    print(f"listede {len(ls)} dosya: " + ", ".join(f"{t} {sum(x['tur'] == t for x in ls)}" for t in TURLER))
    if a.kuru:
        print("kuru kip: ağ isteği yapılmadı")
        return 0
    hedef = os.path.abspath(a.hedef)
    if os.path.commonpath([hedef, TL.DEPO]) == TL.DEPO:
        raise SystemExit("DUR: hedef depo içinde (ham veri depoya konmaz)")
    if os.path.exists(a.manifest):
        raise SystemExit("DUR: manifest zaten var (tek indirme anı)")
    if os.path.exists(hedef) and os.listdir(hedef):
        raise SystemExit("DUR: hedef dizin boş değil")
    for t in TURLER:
        os.makedirs(os.path.join(hedef, t), exist_ok=True)
    url_onek = tuple(a.url_onek.split("=", 1)) if a.url_onek else None
    baslangic = zaman()
    kayit = {}
    tur(ls, hedef, kayit, url_onek, a.bekle)
    hata = [x for x in ls if kayit[x["url"]]["durum"] != "tamam"]
    pay = len(hata) / len(ls)
    yeniden = None
    if pay > HATA_PAY:
        print(f"başarısız pay %{100 * pay:.1f} > %5: tek yeniden deneme turu")
        yeniden = zaman()
        time.sleep(30 * a.bekle)
        tur(hata, hedef, kayit, url_onek, a.bekle)
        hata = [x for x in ls if kayit[x["url"]]["durum"] != "tamam"]
        pay = len(hata) / len(ls)
    man = dict(aciklama="TR-10b veri adımı (§2.4 madde 2): 66 veri dosyası, depo dışında; içerik açılmadı.",
               listeler_json_sha256=LISTELER_JSON_SHA, user_agent=UA, baslangic=baslangic, bitis=zaman(),
               yeniden_deneme_turu=yeniden, basarisiz=[x["url"] for x in hata], basarisiz_pay=pay,
               dosyalar=[kayit[x["url"]] for x in ls])
    with open(a.manifest, "x", encoding="utf-8") as f:
        f.write(json.dumps(man, ensure_ascii=False, indent=1) + "\n")
    print(f"manifest: {a.manifest}; başarısız {len(hata)} (pay {pay:.3f})")
    return 0 if pay <= HATA_PAY else 3


if __name__ == "__main__":
    sys.exit(main())
