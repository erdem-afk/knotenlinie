"""S1 geçit envanteri ve puanlama (kural docs/arastirma-sorulari/S1-S6-KURAL.md, sha 167ef5b4…; Ek 1).
Kullanım: python3 s1_gecit.py VERI_DIZINI CIKTI.json [--puanla]
"""
import json, math, sys, glob, os
import numpy as np, shapefile, openpyxl
from pyproj import Transformer
from shapely.geometry import LineString, MultiLineString, Point, shape
from shapely.ops import unary_union, linemerge

V = sys.argv[1]

def utm(lon, lat):
    z = int((lon + 180) // 6) + 1
    return Transformer.from_crs("EPSG:4326", f"EPSG:{32600 + z if lat >= 0 else 32700 + z}", always_xy=True)

def proj_lines(lines, T):
    out = []
    for l in lines:
        x, y = T.transform([p[0] for p in l], [p[1] for p in l])
        if len(x) >= 2:
            out.append(LineString(np.c_[np.array(x) / 1000, np.array(y) / 1000]))  # km
    return out

def az(p, q):
    return math.degrees(math.atan2(q[0] - p[0], q[1] - p[1])) % 180  # doğrultu, 0-180

def azfark(a, b):
    d = abs(a - b) % 180
    return min(d, 180 - d)

GEM = None
def gem_lines(lon0, lat0, r=1.5):
    global GEM
    if GEM is None:
        GEM = json.load(open(os.path.join(V, "gem.geojson")))["features"]
    out = []
    for f in GEM:
        g = f["geometry"]
        cs = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for c in cs:
            if any(abs(p[0] - lon0) < r * 1.5 and abs(p[1] - lat0) < r for p in c):
                out.append(c)
    return out

EDSF = None
def edsf_lines(lon0, lat0, r=3.0):
    """Ek 1: Türkiye olayları için EDSF13 (2013, olay öncesi) bileşik kaynak üst izleri GEM'e eklenir."""
    global EDSF
    if EDSF is None:
        f = glob.glob(os.path.join(V, "edsf", "DB-CFS", "**", "Crustal_fault_sources_TOP.shp"), recursive=True)[0]
        rr = shapefile.Reader(f); EDSF = []
        for sh in rr.shapes():
            pts = sh.points; parts = list(sh.parts) + [len(pts)]
            for i in range(len(parts) - 1):
                EDSF.append(pts[parts[i]:parts[i + 1]])
    return [c for c in EDSF if any(abs(p[0] - lon0) < r * 1.5 and abs(p[1] - lat0) < r for p in c)]

def kapsama(L, G):
    """Kırık noktalarının fay haritasına ≤3 km olan payı (0,5 km aralıkla)."""
    from shapely.strtree import STRtree
    if not G:
        return 0.0
    agac = STRtree(G); n = k = 0
    for l in L:
        for x in np.arange(0, l.length + 1e-9, 0.5):
            p = l.interpolate(x); n += 1
            k += len(agac.query(p, predicate="dwithin", distance=3.0)) > 0
    return k / max(1, n)

def kollar(lines):
    """0,2 km'den yakın parçaları birleştir (STRtree + birleşim-bul), ≥1 km kolları döndür."""
    from shapely.strtree import STRtree
    tree = STRtree(lines); par = list(range(len(lines)))
    def bul(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    for i, l in enumerate(lines):
        for j in tree.query(l, predicate="dwithin", distance=0.2):
            a, b = bul(i), bul(int(j))
            if a != b:
                par[a] = b
    grup = {}
    for i in range(len(lines)):
        grup.setdefault(bul(i), []).append(lines[i])
    out = []
    for ls in grup.values():
        m = MultiLineString(ls) if len(ls) > 1 else ls[0]
        if m.length >= 1.0:
            out.append(m)
    return out

def ana_hat(m, u):
    """Ek 1: kolun merkez çizgisi. Parçalar birleşip kol uzunluğunun ≥%70'ini tek çizgide veriyorsa o çizgi;
    yoksa kolun kendi ana ekseni boyunca 1 km kutularda dik uzaklık ortalaması (yoğun saha haritaları için)."""
    mm = linemerge(m) if m.geom_type != "LineString" else m
    en = mm if mm.geom_type == "LineString" else max(mm.geoms, key=lambda g: g.length)
    if en.length >= 0.7 * m.length:
        return en
    P = np.vstack([np.array(g.coords) for g in getattr(m, "geoms", [m])])
    c = P.mean(0); u = np.linalg.svd(P[::max(1, len(P) // 5000)] - c, full_matrices=False)[2][0]
    s_ = (P - c) @ u; n = np.array([-u[1], u[0]]); t_ = (P - c) @ n
    kut = np.floor(s_).astype(int); xs = []
    for k in range(kut.min(), kut.max() + 1):
        w = kut == k
        if w.any():
            xs.append(c + (k + 0.5) * u + t_[w].mean() * n)
    return LineString(xs) if len(xs) >= 2 else None

def bukumler(m, eksen):
    """5 km kiriş doğrultularında ≥10° değişim; 5 km içinde tek sayılır."""
    h = ana_hat(m, eksen)
    if h is None or h.length < 10:
        return []
    s = np.arange(0, h.length + 1e-9, 1.0)
    pts = [h.interpolate(x) for x in s]
    out, son = [], -99
    for i in range(5, len(s) - 5):
        a1 = az((pts[i - 5].x, pts[i - 5].y), (pts[i].x, pts[i].y))
        a2 = az((pts[i].x, pts[i].y), (pts[i + 5].x, pts[i + 5].y))
        th = azfark(a1, a2)
        if th >= 10 and s[i] - son > 5:
            out.append({"tur": "bukum", "aci": round(th, 1), "gecti": True, "km": round(float(s[i]), 1)})
            son = s[i]
    return out

def envanter(ad, lines_ll, gem_ll):
    lon0 = np.mean([p[0] for l in lines_ll for p in l]); lat0 = np.mean([p[1] for l in lines_ll for p in l])
    T = utm(lon0, lat0)
    L = [l.simplify(0.02) for l in proj_lines(lines_ll, T)]
    G = proj_lines(gem_ll, T)
    kap = kapsama([k for k in L], G)
    P = np.vstack([np.array(l.coords) for l in L])
    c = P.mean(0); u = np.linalg.svd(P[::max(1, len(P) // 5000)] - c, full_matrices=False)[2][0]  # ana eksen
    sx = lambda p: float(np.dot(np.array(p) - c, u))
    K = kollar(L)
    K = sorted(K, key=lambda m: min(sx(q) for g in getattr(m, "geoms", [m]) for q in g.coords))
    gates = []
    # içerideki basamaklar: eksen boyunca ardışık kollar
    # Ek 1: yalnız kırılma cephesini ilerleten kol bir geçit sayılır; paralel kollar (cephe içinde) atlanır
    smax = lambda m: max(sx(q) for g in getattr(m, "geoms", [m]) for q in g.coords)
    zincir = K[0]; cephe = smax(K[0])
    for b in K[1:]:
        if smax(b) > cephe + 1.0:
            d = b.distance(zincir)
            if d >= 1.0:
                gates.append({"tur": "basamak", "d_km": round(d, 2), "gecti": True})
            cephe = smax(b)
        zincir = MultiLineString([g for k in (zincir, b) for g in getattr(k, 'geoms', [k])])
    for m in K:
        gates += bukumler(m, u)
    # uçlar
    tum = MultiLineString([g for k in K for g in getattr(k, 'geoms', [k])])
    from shapely.strtree import STRtree
    agac = STRtree(list(tum.geoms))
    G2 = []
    for g in G:
        n = max(2, int(g.length / 0.5) + 1)
        q = [g.interpolate(x) for x in np.linspace(0, g.length, n)]
        uzak = [len(agac.query(p, predicate="dwithin", distance=1.0)) == 0 for p in q]
        run = []
        for p, f in zip(q, uzak):
            if f:
                run.append((p.x, p.y))
            else:
                if len(run) >= 3: G2.append(LineString(run))
                run = []
        if len(run) >= 3: G2.append(LineString(run))
    for yon in (-1, 1):
        pts = [q for l in L for q in l.coords]
        E = max(pts, key=lambda q: yon * sx(q))
        Ep = Point(E)
        # uçtaki 5 km'lik doğrultu
        geri = [q for q in pts if 0 < yon * (sx(E) - sx(q)) <= 5]
        a_uc = az(min(geri, key=lambda q: -yon * sx(q)) if geri else E, E) if geri else None
        ileri = []
        for parca in G2:
            if parca.length < 1:
                continue
            q = [p for p in parca.coords if yon * (sx(p) - sx(E)) > 0 and Point(p).distance(Ep) <= 10]
            if q:
                ileri.append(parca)
        if not ileri:
            gates.append({"tur": "uc_fay_yok", "gecti": False, "puan": False})
            continue
        P2 = min(ileri, key=lambda g: g.distance(Ep))
        # uç doğrultusu üzerindeki doğruya dik uzaklık
        if a_uc is None:
            continue
        th = math.radians(a_uc); dvec = np.array([math.sin(th), math.cos(th)])
        nvec = np.array([-dvec[1], dvec[0]])
        dperp = min(abs(float(np.dot(np.array(p) - np.array(E), nvec))) for p in P2.coords
                    if Point(p).distance(Ep) <= 10)
        if dperp >= 1.0:
            gates.append({"tur": "basamak", "d_km": round(dperp, 2), "gecti": False})
        else:
            cc = [p for p in P2.coords if Point(p).distance(Ep) <= 6]
            if len(cc) >= 2:
                a2 = az(cc[0], cc[-1]) if yon * (sx(cc[-1]) - sx(cc[0])) > 0 else az(cc[-1], cc[0])
                tht = azfark(a_uc, a2)
            else:
                tht = 0
            if tht >= 10:
                gates.append({"tur": "bukum", "aci": round(tht, 1), "gecti": False})
            else:
                gates.append({"tur": "uc_geometrisiz", "aci": round(tht, 1), "gecti": False, "puan": False})
    if kap < 0.5:  # Ek 1: fay haritası kırılan fayı göstermiyorsa uç geçitleri puanlanmaz
        for g in gates:
            if not g["gecti"]:
                g["puan"] = False; g["not"] = "fay haritası kapsaması < 0,5"
    return {"olay": ad, "kapsama": round(kap, 2), "uzunluk_km": round(sum(m.length for m in K), 1), "kol": len(K), "gecitler": gates}

def sure(fn_glob):
    r = shapefile.Reader(glob.glob(os.path.join(V, "SURE2.0_Ruptures", fn_glob))[0])
    out = []
    for sh, rec in zip(r.shapes(), r.records()):
        if rec["Comp_rank"] == 1:
            pts = sh.points; parts = list(sh.parts) + [len(pts)]
            for i in range(len(parts) - 1):
                out.append(pts[parts[i]:parts[i + 1]])
    return out

def myanmar():
    p = [tuple(map(float, l.split()[:2])) for l in open(os.path.join(V, "myanmar_trace.txt")) if l.strip()]
    return [p]

def maras():
    """Ek 1: Pucci 2023 noktaları yalnız kırılan GEM parçalarını seçer; iz = noktalara 2 km yakın GEM parçaları."""
    ws = openpyxl.load_workbook(os.path.join(V, "pucci.xlsx"), read_only=True).worksheets[0]
    pts = [(r[4], r[3]) for i, r in enumerate(ws.iter_rows(values_only=True)) if i and r[3] and r[13] == "Coseismic rupture"]
    lon0 = np.mean([p[0] for p in pts]); lat0 = np.mean([p[1] for p in pts])
    T = utm(lon0, lat0)
    x, y = T.transform([p[0] for p in pts], [p[1] for p in pts]); X = np.c_[np.array(x) / 1000, np.array(y) / 1000]
    G = gem_lines(lon0, lat0, 2.5)
    Ti = Transformer.from_crs(T.target_crs, "EPSG:4326", always_xy=True)
    out = []
    cloud = unary_union([Point(p).buffer(2.0) for p in X])
    for g in proj_lines(G, T):
        part = g.intersection(cloud)
        for pp in getattr(part, "geoms", [part]):
            if not pp.is_empty and pp.geom_type == "LineString" and pp.length >= 0.5:
                lo, la = Ti.transform([q[0] * 1000 for q in pp.coords], [q[1] * 1000 for q in pp.coords])
                out.append(list(zip(lo, la)))
    return out, pts

def maras_insar(olay):
    """Ek 1: Tsironi & Ganas 2023 InSAR kırık izleri (Zenodo 8050940). Atama: en güney noktası 37,75°K'nin
    kuzeyindeki çizgiler Mw 7,6 (Çardak–Sürgü); 36,2°D'nin doğusundaki diğerleri Mw 7,8 (DAF + Narlı + Adıyaman
    kolu); 36,2°D batısındaki (≈36,9°K) zincir hiçbir olaya atanamadı, dışarıda."""
    import re
    s_ = open(os.path.join(V, "maras_insar.kml")).read()
    out = []
    for c in re.findall(r"<coordinates>(.*?)</coordinates>", s_, re.S):
        pts = [tuple(map(float, x.split(",")[:2])) for x in c.split()]
        if min(p[1] for p in pts) > 37.75:
            o = "7.6"
        elif min(p[0] for p in pts) >= 36.2:
            o = "7.8"
        else:
            o = None
        if o == olay:
            out.append(pts)
    return out

OLAYLAR = {
    "Kumamoto 2016 Mw7,0": lambda: sure("20160415*ruptures.shp"),
    "Ridgecrest 2019 Mw6,4": lambda: sure("20190704*ruptures.shp"),
    "Ridgecrest 2019 Mw7,1": lambda: sure("20190705*ruptures.shp"),
    "Myanmar 2025 Mw7,7": myanmar,
    "Kahramanmaras 2023 Mw7,8": lambda: maras_insar("7.8"),
    "Elbistan 2023 Mw7,6": lambda: maras_insar("7.6"),
}

if __name__ == "__main__":
    res = []
    for ad, f in OLAYLAR.items():
        lines = f()
        lon0 = np.mean([p[0] for l in lines for p in l]); lat0 = np.mean([p[1] for l in lines for p in l])
        harita = gem_lines(lon0, lat0, 3.0) + (edsf_lines(lon0, lat0) if ad.startswith(("Kahraman", "Elbistan")) else [])
        e = envanter(ad, lines, harita)
        res.append(e)
        print(ad, e["uzunluk_km"], "km,", e["kol"], "kol, kapsama", e["kapsama"])
        for g in e["gecitler"]:
            print("   ", g)
    json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
