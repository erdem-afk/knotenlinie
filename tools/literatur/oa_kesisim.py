"""OpenAlex ile köprü kesişimlerini yeniden ölçer (v3 OpenCitations ölçümünün doğrulaması, 10 Kasım 2026).
Anahtar OPENALEX_API_KEY ortam değişkeninden okunur; hiçbir yere yazılmaz/loglanmaz.
Kullanım: OPENALEX_API_KEY=... python3 -I oa_kesisim.py tohumlar_v3.json kopruler_v3.json cikti_dizini
"""
import json, os, sys, time, urllib.request, urllib.parse
KEY = os.environ["OPENALEX_API_KEY"]
def get(path, **q):
    q["api_key"] = KEY
    url = "https://api.openalex.org/" + path + "?" + urllib.parse.urlencode(q)
    for i in range(5):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)
        except Exception as e:
            if i == 4: raise RuntimeError(f"OpenAlex hata: {path} {type(e).__name__}")
            time.sleep(2 ** i)
def wid(doi):
    return get("works/doi:" + doi, select="id,title,publication_year,cited_by_count")
def citers(w, cache):
    p = os.path.join(cache, w.split("/")[-1] + ".json")
    if os.path.exists(p): return json.load(open(p))
    out, cur = {}, "*"
    while cur:
        d = get("works", filter="cites:" + w.split("/")[-1], select="id,doi,title,publication_year",
                **{"per-page": 200, "cursor": cur})
        for r in d["results"]: out[r["id"].split("/")[-1]] = [r.get("title"), r.get("publication_year"), r.get("doi")]
        cur = d["meta"].get("next_cursor") if d["results"] else None
    json.dump(out, open(p, "w")); return out
def main():
    cfg = json.load(open(sys.argv[1])); kop = json.load(open(sys.argv[2])); od = sys.argv[3]
    cache = os.path.join(od, "oa_onbellek"); os.makedirs(cache, exist_ok=True)
    S, meta, tek = {}, {}, {}
    for ad, dois in cfg["kumeler"].items():
        u = set()
        for d in dois:
            w = wid(d.lower()); c = citers(w["id"], cache); tek[d] = [w["title"], len(c)]
            u |= set(c); meta.update(c)
        S[ad] = u
    rap = {"tarih": time.strftime("%Y-%m-%d"), "kaynak": "OpenAlex (anahtarlı)", "tohum_atif": tek,
           "kume_boyu": {k: len(v) for k, v in S.items()}, "kopruler": {}}
    for ad, k in kop.items():
        ks = [S[x] for x in k["kumeler"]]; inter = set.intersection(*ks); uni = set.union(*ks)
        r = {"kumeler": k["kumeler"], "boylar": [len(x) for x in ks], "kesisim": len(inter),
             "jaccard": len(inter) / max(1, len(uni)),
             "kesisim_isleri": sorted(([i] + meta[i] for i in inter), key=lambda x: -(x[2] or 0))[:80]}
        rap["kopruler"][ad] = r
        print(f"{ad:28} {r['boylar']} k={r['kesisim']:4d} J={r['jaccard']:.4f}")
    json.dump(rap, open(os.path.join(od, "oa_kesisim_rapor.json"), "w"), ensure_ascii=False, indent=1)
if __name__ == "__main__": main()
