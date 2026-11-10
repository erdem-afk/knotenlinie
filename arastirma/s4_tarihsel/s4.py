#!/usr/bin/env python3
"""S4: tarihsel Marmara depremlerinin segment ataması (ön kayıt ONKAYIT.md sürüm 2).

Kullanım: python3 -I s4.py <edsf_zip> <cikti_dizini>
Girdiler bu klasörden okunur (veri/, TURBIDIT.csv, TSUNAMI.csv). Ağ kullanmaz.
"""
import csv, json, math, sys, zipfile, tempfile, os, hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

BURASI = Path(__file__).resolve().parent
H_KM = 10.0
LAT0, LON0 = 40.7, 29.0
KX = 111.32 * math.cos(math.radians(LAT0)); KY = 110.57


def xy(lon, lat):
    return (np.asarray(lon) - LON0) * KX, (np.asarray(lat) - LAT0) * KY


# ---------------- geometri ----------------
def edsf_izleri(zip_yolu):
    import shapefile
    d = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_yolu) as z:
        z.extractall(d)
    shp = next(Path(d).rglob("Crustal_fault_sources_TOP.shp"))
    r = shapefile.Reader(str(shp), encoding="latin1")
    return {rec["IDSOURCE"]: [(p[0], p[1]) for p in s.points] for s, rec in zip(r.shapes(), r.records())}


def kes(poly, lo, hi):
    """lon'a göre sıralı çoklu çizgiyi [lo, hi] aralığında kes (uçlar enterpolasyonlu)."""
    out = []
    for (x1, y1), (x2, y2) in zip(poly[:-1], poly[1:]):
        for x in (lo, hi):
            if (x1 - x) * (x2 - x) < 0:
                out.append((x, y1 + (y2 - y1) * (x - x1) / (x2 - x1)))
    out += [p for p in poly if lo <= p[0] <= hi]
    return sorted(set(out))


def segmentler(izler):
    # SAPMA/hata düzeltmesi: ön kayıttaki "TRCS290" başka bir kaynak (38° K); TRCS996 zaten 26,60'a uzanıyor.
    # IZG için ön kayıttaki düz bağlantı yerine EDSF'nin TRCS012 izi (29,33–29,79) kullanılır.
    kuzey = izler["TRCS996"] + izler["TRCS013"] + izler["TRCS012"]
    kuzey = sorted(kuzey)
    sinir = [("GAN", 26.60, 27.25), ("TEK", 27.25, 27.75), ("CEN", 27.75, 28.30), ("KUM", 28.30, 28.75),
             ("PIF", 28.75, 29.23), ("IZG", 29.23, 29.79), ("IZE", 29.79, 30.40), ("SAK", 30.40, 30.97)]
    seg = {ad: kes(kuzey, lo, hi) for ad, lo, hi in sinir}
    seg["SCI"] = sorted(izler["TRCS014"])
    seg["GEM"] = sorted(izler["TRCS023"])
    seg["GEY"] = sorted(izler["TRCS022"])
    return seg, [s[0] for s in sinir]


DENIZ = {"TEK", "CEN", "KUM", "PIF", "IZG", "SCI", "GEM"}


def adaylar(kuzey_sira):
    c = []
    for n in range(1, 5):
        for i in range(len(kuzey_sira) - n + 1):
            c.append(tuple(kuzey_sira[i:i + n]))
    c += [("SCI",), ("SCI", "IZG"), ("SCI", "IZG", "IZE"), ("GEM",), ("GEY",), ("GEM", "GEY")]
    c.append(("DIS",))
    return c


def uzunluk(pts):
    x, y = xy([p[0] for p in pts], [p[1] for p in pts])
    return float(np.sum(np.hypot(np.diff(x), np.diff(y))))


def nokta_cizgi(px, py, pts):
    """noktalardan çoklu çizgiye en kısa uzaklık (km), vektörel."""
    x, y = xy([p[0] for p in pts], [p[1] for p in pts])
    px = np.asarray(px)[:, None]; py = np.asarray(py)[:, None]
    ax, ay, bx, by = x[:-1], y[:-1], x[1:], y[1:]
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = np.clip(((px - ax) * dx + (py - ay) * dy) / np.where(L2 > 0, L2, 1), 0, 1)
    return np.min(np.hypot(px - (ax + t * dx), py - (ay + t * dy)), axis=1)


def jb_uzaklik(px, py, poligonlar):
    """Joyner–Boore: yüzey izdüşümü poligonlarına uzaklık, içerideyse 0."""
    best = np.full(len(px), np.inf)
    for poly in poligonlar:
        pts = [(p[0], p[1]) for p in poly]
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        d = nokta_cizgi(px, py, pts)
        X, Y = xy([p[0] for p in pts], [p[1] for p in pts])
        ic = np.zeros(len(px), bool)
        for i in range(len(pts) - 1):
            x1, y1, x2, y2 = X[i], Y[i], X[i + 1], Y[i + 1]
            kos = ((y1 > py) != (y2 > py)) & (px < (x2 - x1) * (py - y1) / np.where(y2 != y1, y2 - y1, 1e-12) + x1)
            ic ^= kos
        best = np.minimum(best, np.where(ic, 0.0, d))
    return best


# ---------------- veri ----------------
NS = {"ms": "http://quakeml.org/xmlns/macroseismic/0.9", "q": "http://quakeml.org/xmlns/bed/1.3"}


def ahead_mdp(yol, veri_kumesi="UNITH003"):
    root = ET.parse(yol).getroot()
    yer = {}
    for pl in root.iter("{%s}place" % NS["ms"]):
        la = pl.find("ms:referenceLatitude/q:value", NS); lo = pl.find("ms:referenceLongitude/q:value", NS)
        if la is None:
            la = pl.find("ms:referenceLatitude/{*}value", NS); lo = pl.find("ms:referenceLongitude/{*}value", NS)
        yer[pl.get("publicID")] = (float(lo.text), float(la.text))
    out = []
    for m in root.iter("{%s}mdp" % NS["ms"]):
        if f"/{veri_kumesi}/" not in m.get("publicID"):
            continue
        cl = m.find("ms:intensity/ms:expectedIntensity/ms:class", NS)
        if cl is None or not (cl.text or "").strip():
            continue
        try:
            I = float(cl.text)
        except ValueError:
            continue
        lo, la = yer[m.find("ms:placeReference", NS).text]
        out.append((lo, la, I))
    ev = root.find(".//q:origin", NS)
    lat = float(ev.find("q:latitude/q:value", NS).text); lon = float(ev.find("q:longitude/q:value", NS).text)
    return np.array(out), (lon, lat)


def shakemap(kimlik):
    d = BURASI / "veri" / "shakemap"
    s = json.load(open(d / f"{kimlik}_stations.json"))
    pts = []
    for f in s["features"]:
        p = f["properties"]
        if p.get("station_type") != "macroseismic" or p.get("intensity") in (None, "null"):
            continue
        pts.append((f["geometry"]["coordinates"][0], f["geometry"]["coordinates"][1], float(p["intensity"])))
    r = json.load(open(d / f"{kimlik}_rupture.json"))
    polys = []
    for feat in r["features"]:
        g = feat["geometry"]
        if g["type"] == "MultiPolygon":
            for pg in g["coordinates"]:
                polys.append([(c[0], c[1]) for c in pg[0]])
        elif g["type"] == "Polygon":
            polys.append([(c[0], c[1]) for c in g["coordinates"][0]])
    e = json.load(open(d / f"{kimlik}_event.json"))
    return np.array(pts), polys, e


KALIB = ["usp0009d4z", "usp0009hev", "usp000547c", "usp0000kf0", "usp0000cqe", "usp0003pmm", "usp000axp7"]
IZMIT = "usp0009d4z"


# ---------------- IPE ve olabilirlik ----------------
def ipe(th, M, R, h=H_KM):
    a, b, c = th[:3]
    return a + b * M - c * np.log10(np.sqrt(R * R + h * h))


def mvn_ll(r, s2, t2):
    """r: (..., n) artıklar; kovaryans s2 I + t2 11ᵀ için log yoğunluk."""
    n = r.shape[-1]
    S = r.sum(-1); Q = (r * r).sum(-1)
    logdet = (n - 1) * np.log(s2) + np.log(s2 + n * t2)
    quad = Q / s2 - t2 * S * S / (s2 * (s2 + n * t2))
    return -0.5 * (n * np.log(2 * np.pi) + logdet + quad)


def kalibre(olaylar, h=H_KM):
    nbar = np.mean([len(o[0]) for o in olaylar])

    def nll(th):
        s2, t2 = np.exp(2 * th[3]), np.exp(2 * th[4])
        tot = 0.0
        for I, M, R in olaylar:
            tot += (nbar / len(I)) * mvn_ll(I - ipe(th, M, R, h), s2, t2)
        tot += -0.5 * ((th[1] - 1.5) / 0.5) ** 2
        return -tot
    best = None
    for x0 in ([1.0, 1.5, 3.0, 0.0, -0.5], [3.0, 1.2, 2.5, -0.3, -1.0], [0.0, 1.8, 3.5, 0.2, 0.0]):
        r = minimize(nll, x0, method="Nelder-Mead", options={"maxiter": 20000, "xatol": 1e-6, "fatol": 1e-8})
        if best is None or r.fun < best.fun:
            best = r
    return best.x


M_SIG = 0.25
GZ = np.linspace(-2, 2, 9); GW = np.exp(-0.5 * GZ ** 2); GW /= GW.sum()


def L_siddet(th, I, px, py, aday, seg, merkez, h=H_KM):
    s2, t2 = np.exp(2 * th[3]), np.exp(2 * th[4])
    if aday == ("DIS",):
        cx, cy = xy(merkez[0], merkez[1])
        R = np.hypot(px - cx, py - cy)
        Ms = np.linspace(6.5, 7.6, 12); w = np.full(12, 1 / 12)
    else:
        R = np.min([nokta_cizgi(px, py, seg[s]) for s in aday], axis=0)
        L = sum(uzunluk(seg[s]) for s in aday)
        M0 = 5.16 + 1.12 * math.log10(L)
        Ms = M0 + M_SIG * GZ; w = GW
    ll = np.array([mvn_ll(I - ipe(th, M, R, h), s2, t2) for M in Ms])
    return float(logsumexp(ll, b=w))


HAVZA = {"TB": (27.55, 40.82), "CB": (28.00, 40.83), "KB": (28.55, 40.87), "CiB": (29.05, 40.72), "IGB": (29.55, 40.70)}


def havza_p(aday, seg, merkez):
    out = {}
    for hv, (lo, la) in HAVZA.items():
        bx, by = xy(lo, la)
        if aday == ("DIS",):
            cx, cy = xy(merkez[0], merkez[1])
            out[hv] = 0.2 if float(np.hypot(bx - cx, by - cy)) <= 50 else 0.05
            continue
        else:
            d = [float(nokta_cizgi(np.array([bx]), np.array([by]), seg[s])[0]) for s in aday]
        out[hv] = 0.7 if min(d) <= 10 else (0.2 if min(d) <= 50 else 0.05)
    return out


def deniz_alti(aday, seg, merkez):
    if aday == ("DIS",):
        cx, cy = xy(merkez[0], merkez[1])
        return any(float(nokta_cizgi(np.array([cx]), np.array([cy]), seg[s])[0]) <= 10 for s in DENIZ)
    return any(s in DENIZ for s in aday)


def L_turbidit_tek(gozlemler, p):
    ll = 0.0
    for hv, g, w in gozlemler:
        pv = w * p[hv] + (1 - w) * 0.3
        ll += math.log(pv if g == "var" else 1 - pv)
    return ll


def L_tsunami(g, deniz):
    P = 0.6 if deniz else 0.15
    if g == "var":
        return math.log(P)
    if g == "bildirilmemis":
        return math.log(1 - 0.7 * P)
    return 0.0


def turbidit_oku():
    d = {}
    for r in csv.DictReader(open(BURASI / "TURBIDIT.csv")):
        if r["gozlem"] in ("var", "yok"):
            d.setdefault(r["olay"], []).append((r["havza"], r["gozlem"], float(r["w"])))
    return d


def tsunami_oku():
    return {r["olay"]: r["gozlem"] for r in csv.DictReader(open(BURASI / "TSUNAMI.csv"))}


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b)


def normal(ll):
    ll = np.asarray(ll, float)
    return np.exp(ll - logsumexp(ll))


def segment_marj(post, cands, segs):
    return {s: float(sum(p for p, c in zip(post, cands) if s in c)) for s in segs}


# ---------------- ana akış ----------------
def main(zip_yolu, cikti):
    cikti = Path(cikti); cikti.mkdir(parents=True, exist_ok=True)
    izler = edsf_izleri(zip_yolu)
    seg, kuzey = segmentler(izler)
    cands = adaylar(kuzey)
    tum_seg = kuzey + ["SCI", "GEM", "GEY"]
    sonuc = {"segment_uzunluk_km": {s: round(uzunluk(seg[s]), 1) for s in tum_seg}, "aday_sayisi": len(cands)}
    TU, TS = turbidit_oku(), tsunami_oku()

    # kalibrasyon verisi
    kal = {}
    for k in KALIB:
        pts, polys, e = shakemap(k)
        px, py = xy(pts[:, 0], pts[:, 1])
        kal[k] = (pts[:, 2], e["mag"], jb_uzaklik(px, py, polys), e)
    sonuc["kalibrasyon_nokta"] = {k: int(len(v[0])) for k, v in kal.items()}

    def th_icin(haric, h=H_KM):
        return kalibre([(v[0], v[1], v[2]) for k, v in kal.items() if k not in haric], h)
    th_tum = th_icin([]); th_loo = th_icin([IZMIT])
    sonuc["ipe_tum"] = dict(zip(["a", "b", "c", "sigma", "tau"], [*map(float, th_tum[:3]), float(np.exp(th_tum[3])), float(np.exp(th_tum[4]))]))
    sonuc["ipe_izmit_haric"] = dict(zip(["a", "b", "c", "sigma", "tau"], [*map(float, th_loo[:3]), float(np.exp(th_loo[3])), float(np.exp(th_loo[4]))]))

    # ---- pozitif kontroller ----
    D99 = ("IZG", "IZE", "SAK")
    dogru99 = np.array([c != ("DIS",) and jaccard(c, D99) >= 2 / 3 for c in cands])
    batiya = np.array([(not d) and c != ("DIS",) and any(s in c for s in ("GAN", "TEK", "CEN", "KUM", "PIF", "SCI", "GEM")) for c, d in zip(cands, dogru99)])
    I99, _, _, e99 = kal[IZMIT]
    pts99, _, _ = shakemap(IZMIT)
    px99, py99 = xy(pts99[:, 0], pts99[:, 1])
    m99 = (e99["lon"], e99["lat"])
    ll_s99 = np.array([L_siddet(th_loo, I99, px99, py99, c, seg, m99) for c in cands])
    ll_t99 = np.array([L_turbidit_tek(TU.get("1999", []), havza_p(c, seg, m99)) + L_tsunami(TS["1999"], deniz_alti(c, seg, m99)) for c in cands])
    p_s = normal(ll_s99); p_o = normal(ll_s99 + ll_t99)
    K1 = float(p_s[dogru99].sum())
    K4 = float(np.log(p_o[dogru99].sum()) - np.log(p_s[dogru99].sum()))
    sonuc["K1_1999_dogru_kutle"] = K1
    sonuc["K1_en_olasi"] = [(list(cands[i]), float(p_s[i])) for i in np.argsort(-p_s)[:5]]
    sonuc["K4_log_fark"] = K4

    # K2: tarihsel geometride alt örnek
    rng = np.random.default_rng(20261110)
    hedefler = {"1509": "15090910_0000_000", "1719": "17190525_0000_000", "1754": "17540902_0000_000",
                "1766-05": "17660522_0000_000", "1766-08": "17660805_0000_000", "1894": "18940710_1833_000"}
    mdp = {k: ahead_mdp(BURASI / "veri" / "ahead" / f"{v}.xml") for k, v in hedefler.items()}
    k2 = {}
    for ad, (P, _) in mdp.items():
        hx, hy = xy(P[:, 0], P[:, 1])
        d = np.hypot(hx[:, None] - px99[None, :], hy[:, None] - py99[None, :])
        yakin = np.argsort(d, axis=1)[:, :3]
        dk, bk = [], []
        for _ in range(200):
            secilen = []
            for k, row in enumerate(yakin):
                aday_i = [j for j in row if j not in secilen]
                if not aday_i:
                    aday_i = [int(j) for j in np.argsort(d[k]) if j not in secilen][:1]
                secilen.append(int(rng.choice(aday_i)))
            s = np.array(secilen)
            ll = np.array([L_siddet(th_loo, I99[s], px99[s], py99[s], c, seg, m99) for c in cands])
            p = normal(ll); dk.append(p[dogru99].sum()); bk.append(p[batiya].sum())
        k2[ad] = {"n": int(len(P)), "dogru": float(np.mean(dk)), "batiya_yanlis": float(np.mean(bk))}
    K2d = float(np.mean([v["dogru"] for v in k2.values()])); K2b = float(np.mean([v["batiya_yanlis"] for v in k2.values()]))
    sonuc["K2"] = {"olay_bazinda": k2, "dogru_ort": K2d, "batiya_yanlis_ort": K2b}

    # K3: 1912 yalnız türbidit + tsunami
    m12 = (27.2, 40.75)
    ll12 = np.array([L_turbidit_tek(TU.get("1912", []), havza_p(c, seg, m12)) + L_tsunami(TS["1912"], deniz_alti(c, seg, m12)) for c in cands])
    p12 = normal(ll12)
    d12 = np.array([c != ("DIS",) and jaccard(c, ("GAN", "TEK")) >= 2 / 3 for c in cands])
    d12a = np.array([c != ("DIS",) and jaccard(c, ("GAN", "TEK", "CEN")) >= 2 / 3 for c in cands])
    K3 = float(p12[d12].sum())
    sonuc["K3_1912_dogru_kutle"] = K3; sonuc["K3_armijo_bilgi"] = float(p12[d12a].sum())
    sonuc["K3_onsel_dogru"] = float(d12.mean())

    gec = {"K1": K1 >= 0.5, "K2": K2d >= 0.35 and K2b <= 0.25, "K3": K3 >= 0.4, "K4": K4 >= -0.1}
    sonuc["kapilar"] = gec
    siddet_kullan = gec["K1"] and gec["K2"]
    tt_kullan = gec["K3"]
    sonuc["hukum"] = ("KAPANDI (K1)" if not gec["K1"] else
                      f"siddet {'kullanilir' if siddet_kullan else 'kullanilmaz'}; turbidit+tsunami {'kullanilir' if tt_kullan else 'kullanilmaz'}; "
                      f"{'ortak' if gec['K4'] else 'yalniz siddet'} yayilim")

    # ---- tarihsel olaylar ----
    def bilesenler(ad, P, merkez, turb_anahtar):
        px, py = xy(P[:, 0], P[:, 1])
        s = np.array([L_siddet(th_tum, P[:, 2], px, py, c, seg, merkez) for c in cands])
        t = np.array([L_turbidit_tek(TU.get(turb_anahtar, []), havza_p(c, seg, merkez)) if turb_anahtar else 0.0 for c in cands])
        u = np.array([L_tsunami(TS.get(ad, "belirsiz"), deniz_alti(c, seg, merkez)) for c in cands])
        return s, t, u

    onsel_marj = segment_marj(np.full(len(cands), 1 / len(cands)), cands, tum_seg)
    sonuc["segment_onsel_marjinal"] = onsel_marj
    olay_out = {}
    B = {}
    for ad in ["1509", "1719", "1754", "1894"]:
        P, mz = mdp[ad]
        B[ad] = bilesenler(ad, P, mz, ad)
    for ad in ["1766-05", "1766-08"]:
        P, mz = mdp[ad]
        B[ad] = bilesenler(ad, P, mz, None)

    def olay_rapor(ad, satirlar):
        r = {}
        for ad_s, ll in satirlar.items():
            p = normal(ll)
            r[ad_s] = {"segment": segment_marj(p, cands, tum_seg), "en_olasi": [(list(cands[i]), round(float(p[i]), 4)) for i in np.argsort(-p)[:3]],
                       "kume_disi": float(p[-1])}
        return r

    for ad in ["1509", "1719", "1754", "1894"]:
        s, t, u = B[ad]
        sat = {"yalniz_siddet": s, "yalniz_turbidit": t, "yalniz_tsunami": u, "turbidit+tsunami": t + u, "ortak": s + t + u}
        olay_out[ad] = olay_rapor(ad, sat)
    # 1766 çifti
    obs = TU.get("1766", [])
    P1 = [havza_p(c, seg, mdp["1766-05"][1]) for c in cands]
    P2 = [havza_p(c, seg, mdp["1766-08"][1]) for c in cands]
    n = len(cands)
    T = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ll = 0.0
            for hv, g, w in obs:
                pv = w * (1 - (1 - P1[i][hv]) * (1 - P2[j][hv])) + (1 - w) * 0.3
                ll += math.log(pv if g == "var" else 1 - pv)
            T[i, j] = ll
    s1, _, u1 = B["1766-05"]; s2, _, u2 = B["1766-08"]

    def cift(S1, S2, TT):
        J = S1[:, None] + S2[None, :] + TT
        J = J - logsumexp(J)
        return np.log(np.exp(J).sum(1) + 1e-300), np.log(np.exp(J).sum(0) + 1e-300)
    z = np.zeros(n)
    for ad, idx in (("1766-05", 0), ("1766-08", 1)):
        sat = {"yalniz_siddet": cift(s1, z, 0 * T)[idx] if idx == 0 else cift(z, s2, 0 * T)[idx],
               "yalniz_turbidit": cift(z, z, T)[idx],
               "yalniz_tsunami": cift(u1, z, 0 * T)[idx] if idx == 0 else cift(z, u2, 0 * T)[idx],
               "turbidit+tsunami": cift(u1, u2, T)[idx],
               "ortak": cift(s1 + u1, s2 + u2, T)[idx]}
        olay_out[ad] = olay_rapor(ad, sat)
    sonuc["olaylar"] = olay_out

    # yayılıma giden satır
    satir = ("ortak" if (siddet_kullan and tt_kullan and gec["K4"]) else
             "yalniz_siddet" if siddet_kullan else
             "turbidit+tsunami" if tt_kullan else None)
    sonuc["yayilim_satiri"] = satir
    if satir:
        ist = {}
        for s in ("CEN", "KUM", "PIF"):
            pm = {ad: olay_out[ad][satir]["segment"][s] for ad in olay_out}
            ist[s] = {"olay_basina_p": pm, "beklenen_kirilma_1500_1900": float(sum(pm.values())),
                      "sonsal_onsel_orani": {ad: (pm[ad] / onsel_marj[s] if onsel_marj[s] else None) for ad in pm}}
            # son kırılma yılı dağılımı (olaylar bağımsız varsayımıyla; 1766 çifti marjinal)
            yillar = sorted(pm, key=lambda a: -int(a[:4]))
            kalan = 1.0; dag = {}
            for a in yillar:
                dag[a] = kalan * pm[a]; kalan *= 1 - pm[a]
            dag["1500_oncesi_ya_da_yok"] = kalan
            ist[s]["son_kirilma"] = dag
        sonuc["istanbul_onu"] = ist

    # h duyarlılığı (hükme girmez): K1
    duy = {}
    for h in (5.0, 15.0):
        th = th_icin([IZMIT], h)
        ll = np.array([L_siddet(th, I99, px99, py99, c, seg, m99, h) for c in cands])
        duy[f"h{int(h)}_K1"] = float(normal(ll)[dogru99].sum())
    sonuc["duyarlilik"] = duy
    sonuc["kod_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    json.dump(sonuc, open(cikti / "sonuc.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: sonuc[k] for k in ("K1_1999_dogru_kutle", "K3_1912_dogru_kutle", "K4_log_fark", "kapilar", "hukum", "yayilim_satiri")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
