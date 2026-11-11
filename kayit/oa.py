"""OpenAlex yardımcı aracı (köprü sorusu yöntemi). Yalnız standart kitaplık.

Anahtar: OPENALEX_API_KEY ortamdaysa oradan, yoksa Doppler'dan (DOPPLER_TOKEN, knotenlinie/prd) okunur.
Anahtar hiçbir yere yazılmaz, loglanmaz. 429 ve ağ hatalarında bekleyip yeniden dener (2, 4, 8 ... 64 sn).

  python3 kayit/oa.py ara "<sorgu>" [adet=15] [yil>=YYYY]   başlık/özet araması: yıl, atıf, başlık, DOI
  python3 kayit/oa.py ozet <doi> [...]                      künye + özet + açık erişim bağlantısı
  python3 kayit/oa.py kopru <tohumlar.json> <cikti_dizini>  köprü ölçümü (ortak atıf kesişimi, Jaccard)

tohumlar.json biçimi:
  {"kumeler": {"A": ["10.x/..", ...], "B": [...], "KONTROL": [...]},
   "kopruler": {"A x B": ["A", "B"], "pozitif kontrol": ["A", "KONTROL"]}}
Köprü ölçüsü: iki (ya da üç) tohum kümesinin HEPSİNE atıf yapan iş sayısı (k) ve Jaccard (J).
Her ölçümde bir pozitif kontrol köprüsü bulunmalı; boşluk iddiası kontrolle kıyaslanır.
"""
import json, os, sys, time, urllib.request, urllib.parse, urllib.error

_KEY = None


def key():
    global _KEY
    if _KEY:
        return _KEY
    _KEY = os.environ.get("OPENALEX_API_KEY")
    if not _KEY:
        req = urllib.request.Request(
            "https://api.doppler.com/v3/configs/config/secret?project=knotenlinie&config=prd&name=OPENALEX_API_KEY",
            headers={"Authorization": "Bearer " + os.environ["DOPPLER_TOKEN"]})
        with urllib.request.urlopen(req, timeout=60) as r:
            _KEY = json.load(r)["value"]["raw"]
    return _KEY


def get(path, **q):
    q["api_key"] = key()
    url = "https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(q)
    for i in range(7):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if i == 6:
                raise RuntimeError(f"OpenAlex hata {e.code}: {path}")
        except Exception as e:
            if i == 6:
                raise RuntimeError(f"OpenAlex hata: {path} {type(e).__name__}")
        time.sleep(2 ** (i + 1))


def ozet_metni(inv):
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


def ara(sorgu, adet=15, yil=None):
    q = {"search": sorgu, "per-page": adet,
         "select": "id,doi,title,publication_year,cited_by_count"}
    if yil:
        q["filter"] = f"publication_year:>{int(yil) - 1}"
    d = get("works", **q)
    print(f"== {sorgu} | n={d['meta']['count']}")
    for r in d["results"]:
        print(f"  {r['publication_year']} atıf {r['cited_by_count']:5d} | {(r['title'] or '')[:130]} | {r['doi']}")


def ozet(doi):
    doi = doi.lower().replace("https://doi.org/", "")
    w = get("works/doi:" + doi)
    if not w:
        print(f"== {doi}: OpenAlex'te yok")
        return
    oa = (w.get("best_oa_location") or {})
    print(f"== {w['title']} ({w['publication_year']}), atıf {w['cited_by_count']}, {w['id']}")
    print("   yazarlar:", "; ".join(a["author"]["display_name"] for a in w.get("authorships", [])[:6]))
    print("   kaynak:", ((w.get("primary_location") or {}).get("source") or {}).get("display_name"))
    print("   açık erişim:", oa.get("pdf_url") or oa.get("landing_page_url") or "yok")
    print("   özet:", ozet_metni(w.get("abstract_inverted_index")) or "(özet yok)")


def citers(wid, cache):
    p = os.path.join(cache, wid + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    out, cur = {}, "*"
    while cur:
        d = get("works", filter="cites:" + wid, select="id,doi,title,publication_year",
                **{"per-page": 200, "cursor": cur})
        for r in d["results"]:
            out[r["id"].split("/")[-1]] = [r.get("title"), r.get("publication_year"), r.get("doi")]
        cur = d["meta"].get("next_cursor") if d["results"] else None
    json.dump(out, open(p, "w"))
    return out


def kopru(tohum_yolu, od):
    cfg = json.load(open(tohum_yolu))
    cache = os.path.join(od, "oa_onbellek")
    os.makedirs(cache, exist_ok=True)
    S, meta, tek = {}, {}, {}
    for ad, dois in cfg["kumeler"].items():
        u = set()
        for d in dois:
            w = get("works/doi:" + d.lower(), select="id,title,publication_year,cited_by_count")
            if not w:
                print(f"UYARI: tohum bulunamadı {d}")
                continue
            c = citers(w["id"].split("/")[-1], cache)
            tek[d] = [w["title"], w["publication_year"], len(c)]
            u |= set(c)
            meta.update(c)
        S[ad] = u
    rap = {"tarih": time.strftime("%Y-%m-%d"), "kaynak": "OpenAlex (anahtarlı)", "tohum_atif": tek,
           "kume_boyu": {k: len(v) for k, v in S.items()}, "kopruler": {}}
    for ad, ks_ad in cfg["kopruler"].items():
        ks = [S[x] for x in ks_ad]
        inter, uni = set.intersection(*ks), set.union(*ks)
        rap["kopruler"][ad] = {
            "kumeler": ks_ad, "boylar": [len(x) for x in ks], "kesisim": len(inter),
            "jaccard": len(inter) / max(1, len(uni)),
            "kesisim_isleri": sorted(([i] + meta[i] for i in inter), key=lambda x: -(x[2] or 0))[:80]}
        r = rap["kopruler"][ad]
        print(f"{ad:40} boy={r['boylar']} k={r['kesisim']:4d} J={r['jaccard']:.4f}")
    for d, v in tek.items():
        print(f"  tohum {d}: {v[2]} atıf | {v[1]} | {(v[0] or '')[:90]}")
    yol = os.path.join(od, "kopru_rapor.json")
    json.dump(rap, open(yol, "w"), ensure_ascii=False, indent=1)
    print("rapor:", yol)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "ara":
        ara(a[1], int(a[2]) if len(a) > 2 else 15, a[3] if len(a) > 3 else None)
    elif a[0] == "ozet":
        for d in a[1:]:
            ozet(d)
    elif a[0] == "kopru":
        kopru(a[1], a[2])
    else:
        print(__doc__)
