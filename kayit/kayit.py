#!/usr/bin/env python3
"""Ortak kayıt aracı (aday defteri + kaynakça). Yalnız standart kitaplık.
  python3 kayit/kayit.py ara <kelime> [...]     aday defterinde ara (VE mantığı, büyük/küçük harf duyarsız)
  python3 kayit/kayit.py ozet                    kol × durum sayımı
  python3 kayit/kayit.py dogrula                 kimlik tekilliği, zorunlu alanlar, durum/hüküm sözlüğü, bib tekilliği
  python3 kayit/kayit.py ekle-kaynak <doi> [...] DOI'den BibTeX çek (doi.org), kaynakca.bib'e ekle (varsa atla)
OPENALEX_API_KEY ortamdaysa ekle-kaynak OpenAlex kimliğini de yazar; yoksa alan boş kalır.
"""
import json, os, re, sys, time, urllib.parse, urllib.request

KOK = os.path.dirname(os.path.abspath(__file__))
ADAY = os.path.join(KOK, "adaylar.jsonl")
BIB = os.path.join(KOK, "kaynakca.bib")
ZORUNLU = ["kimlik", "kol", "ad", "tur", "durum", "hukum", "tarih"]
DURUM = {"aday", "kosuyor", "kapandi", "rakip", "kapali-sartli", "birlesti", "elendi"}
HUKUM = {"H0", "H1", "ayirt-edilemez", "veri-yok", "guc-yok", "rakip", "-"}
TUR = {"fizik", "istatistik", "literatur", "veri", "altyapi"}


def oku():
    out = []
    for n, s in enumerate(open(ADAY, encoding="utf-8"), 1):
        s = s.strip()
        if s:
            try:
                out.append(json.loads(s))
            except json.JSONDecodeError as e:
                sys.exit(f"adaylar.jsonl satır {n}: {e}")
    return out


def kucuk(s):
    return s.replace("İ", "i").replace("I", "ı").lower()


def ara(kelimeler):
    ks = [kucuk(k) for k in kelimeler]
    for a in oku():
        metin = kucuk(json.dumps(a, ensure_ascii=False))
        if all(k in metin for k in ks):
            print(f"[{a['kimlik']}] {a['durum']}/{a['hukum']} — {a['ad']}")
            for alan in ("sonuc", "ders", "yeniden_acma_sarti", "kayit"):
                if a.get(alan):
                    print(f"    {alan}: {a[alan]}")


def ozet():
    say = {}
    for a in oku():
        say.setdefault(a["kol"], {}).setdefault(a["durum"], 0)
        say[a["kol"]][a["durum"]] += 1
    for kol in sorted(say):
        print(f"{kol:22}", ", ".join(f"{d} {n}" for d, n in sorted(say[kol].items())))


def bib_doiler():
    if not os.path.exists(BIB):
        return set()
    return {m.lower() for m in re.findall(r"doi\s*=\s*\{([^}]+)\}", open(BIB, encoding="utf-8").read(), flags=re.I)}


def dogrula():
    hata, gor = [], set()
    for a in oku():
        k = a.get("kimlik", "?")
        for z in ZORUNLU:
            if not a.get(z):
                hata.append(f"{k}: '{z}' eksik")
        if k in gor:
            hata.append(f"{k}: kimlik yinelendi")
        gor.add(k)
        if a.get("durum") not in DURUM:
            hata.append(f"{k}: durum '{a.get('durum')}' sözlükte yok")
        if a.get("hukum") not in HUKUM:
            hata.append(f"{k}: hüküm '{a.get('hukum')}' sözlükte yok")
        if a.get("tur") not in TUR:
            hata.append(f"{k}: tür '{a.get('tur')}' sözlükte yok")
        if a.get("durum") == "kapali-sartli" and not a.get("yeniden_acma_sarti"):
            hata.append(f"{k}: kapali-sartli ama şart yazılmamış")
    if os.path.exists(BIB):
        ds = re.findall(r"doi\s*=\s*\{([^}]+)\}", open(BIB, encoding="utf-8").read(), flags=re.I)
        for d in {x.lower() for x in ds}:
            if sum(x.lower() == d for x in ds) > 1:
                hata.append(f"kaynakca.bib: DOI yinelendi {d}")
    for h in hata:
        print("HATA", h)
    print(f"{len(gor)} aday, {len(bib_doiler())} kaynak, {len(hata)} hata")
    sys.exit(1 if hata else 0)


def getir(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": "kayit-araci/1.0", **({"Accept": accept} if accept else {})})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            if i == 3:
                raise
            time.sleep(2 ** i)


def ekle_kaynak(doiler):
    var = bib_doiler()
    key = os.environ.get("OPENALEX_API_KEY", "")
    for d in doiler:
        d = d.strip().lower().replace("https://doi.org/", "")
        if d in var:
            print("zaten var:", d)
            continue
        try:
            b = getir("https://doi.org/" + urllib.parse.quote(d, safe="/"), "application/x-bibtex").strip()
        except Exception as e:
            print("ALINAMADI:", d, e)
            continue
        if not b.startswith("@"):
            print("BibTeX değil:", d)
            continue
        oa = ""
        if key:
            try:
                j = json.loads(getir(f"https://api.openalex.org/works/doi:{d}?select=id&api_key={key}"))
                oa = j["id"].rsplit("/", 1)[-1]
            except Exception:
                pass
        b = re.sub(r"(?i)doi\s*=\s*\{[^}]*\}", "doi={" + d + "}", b, count=1)
        if oa:
            b = b.rstrip().rstrip("}").rstrip() + ", openalex={" + oa + "}}"
        with open(BIB, "a", encoding="utf-8") as f:
            f.write(b + "\n\n")
        var.add(d)
        print("eklendi:", d, oa)
        time.sleep(0.5)


if __name__ == "__main__":
    k = sys.argv[1] if len(sys.argv) > 1 else ""
    if k == "ara" and len(sys.argv) > 2:
        ara(sys.argv[2:])
    elif k == "ozet":
        ozet()
    elif k == "dogrula":
        dogrula()
    elif k == "ekle-kaynak" and len(sys.argv) > 2:
        ekle_kaynak(sys.argv[2:])
    else:
        sys.exit(__doc__)
