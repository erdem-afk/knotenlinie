"""S1 Marmara geçitleri: EDSF13 (TRCS012 İzmit, TRCS013 Doğu Marmara = PIF+CMF, TRCS996 Marmara–Saros)
üzerinde aynı algoritma (5 km kiriş, ≥10° büküm; kaynaklar arası ≥1 km basamak). Kural Ek 1."""
import sys, glob, json, math, numpy as np, shapefile
sys.argv = [sys.argv[0], sys.argv[1], "x.json"]
sys.path.insert(0, "/home/user/knotenlinie/tools/arastirma")
import s1_gecit as s, s1_puan_fn as pf
from shapely.geometry import LineString
r = shapefile.Reader(glob.glob(sys.argv[1] + "/edsf/DB-CFS/**/Crustal_fault_sources_TOP.shp", recursive=True)[0], encoding="latin-1")
src = {rec["IDSOURCE"]: sh.points for sh, rec in zip(r.shapes(), r.records())}
T = s.utm(28.7, 40.8)
def P(ids):
    return s.proj_lines([src[i] for i in ids], T)
izm, dm, ms = P(["TRCS012", "TRCS013", "TRCS996"])
# batıdan doğuya uzunluk boyunca
def bukum_listesi(l, ad):
    out = []
    s_ = np.arange(0, l.length + 1e-9, 1.0); pts = [l.interpolate(x) for x in s_]; son = -99
    for i in range(5, len(s_) - 5):
        a1 = s.az((pts[i-5].x, pts[i-5].y), (pts[i].x, pts[i].y)); a2 = s.az((pts[i].x, pts[i].y), (pts[i+5].x, pts[i+5].y))
        th = s.azfark(a1, a2)
        if th >= 10 and s_[i] - son > 5:
            x, y = pts[i].x, pts[i].y
            out.append({"kaynak": ad, "tur": "bukum", "aci": round(th, 1), "km_dogudan": round(float(s_[i]), 1)}); son = s_[i]
    return out
G = []
G.append({"kaynak": "İzmit (TRCS012) → Doğu Marmara (TRCS013)", "tur": "basamak", "d_km": round(izm.distance(dm), 2)})
G += bukum_listesi(dm, "Doğu Marmara (PIF+CMF, TRCS013)")
G.append({"kaynak": "Doğu Marmara → Marmara–Saros (TRCS996)", "tur": "basamak", "d_km": round(dm.distance(ms), 2)})
G += bukum_listesi(ms, "Marmara–Saros (Ganos, TRCS996)")
for g in G:
    if g["tur"] == "basamak" and g["d_km"] < 1:
        g["not"] = "< 1 km, geçit değil"; continue
    g["P_BW"] = round(pf.p_bw(g), 3); g["P_R0"] = 0.46
    print(g)
json.dump(G, open("s1_marmara.json", "w"), ensure_ascii=False, indent=1)
