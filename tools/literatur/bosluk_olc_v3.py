"""Literatür boşluğu ölçümü v3 (10 Kasım 2026).
v2 ile aynı yöntem (köprü sorusu: iki tohum kümesinin ikisine de atıf yapan iş sayısı; Jaccard),
ama kaynak OpenCitations Index (anahtarsız, kotasız); atıf listeleri indirilip kesişim yerelde alınır.
Bu sayede üçlü kesişim (A ∩ B ∩ C) de ölçülür. OpenAlex'e göre kapsama daha düşük (~%65–70);
bu yüzden v2 sayıları (OpenAlex) ile karşılaştırma için 8 Kasım köprüsü ve ETAS pozitif kontrolü yeniden ölçülür.
Kullanım: python3 -I bosluk_olc_v3.py tohumlar_v3.json kopruler_v3.json cikti_dizini
"""
import json, os, sys, time, urllib.request
API = "https://api.opencitations.net/index/v2/citations/doi:"

def citers(doi, cache):
    p = os.path.join(cache, doi.replace("/", "_") + ".json")
    if os.path.exists(p):
        return json.load(open(p))
    for i in range(5):
        try:
            with urllib.request.urlopen(API + doi, timeout=120) as r:
                d = json.load(r)
            break
        except Exception:
            if i == 4: raise
            time.sleep(2 ** i)
    out = []
    for c in d:
        ids = dict(x.split(":", 1) for x in c["citing"].split() if ":" in x)
        out.append(ids.get("doi") or ids.get("omid"))
    out = sorted(set(out))
    json.dump(out, open(p, "w"))
    return out

def main():
    cfg = json.load(open(sys.argv[1])); kop = json.load(open(sys.argv[2])); od = sys.argv[3]
    cache = os.path.join(od, "atif_onbellek"); os.makedirs(cache, exist_ok=True)
    S, tek = {}, {}
    for ad, dois in cfg["kumeler"].items():
        u = set()
        for d in dois:
            c = citers(d.lower(), cache); tek[d] = len(c); u |= set(c)
        S[ad] = u
    rap = {"tarih": time.strftime("%Y-%m-%d"), "kaynak": "OpenCitations Index v2", "tohum_atif": tek,
           "kume_boyu": {k: len(v) for k, v in S.items()}, "kopruler": {}}
    for ad, k in kop.items():
        ks = [S[x] for x in k["kumeler"]]
        inter = set.intersection(*ks); uni = set.union(*ks)
        r = {"kumeler": k["kumeler"], "boylar": [len(x) for x in ks], "kesisim": len(inter),
             "jaccard": len(inter) / max(1, len(uni)), "kesisim_isleri": sorted(inter)[:60]}
        rap["kopruler"][ad] = r
        print(f"{ad:28} {r['boylar']} k={r['kesisim']:4d} J={r['jaccard']:.4f}")
    json.dump(rap, open(os.path.join(od, "bosluk_rapor_v3.json"), "w"), ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
