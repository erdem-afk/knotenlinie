"""S2: Türkiye için yayımlanmış segment olasılıklarının 2016–2025 karnesi.

Kural: docs/arastirma-sorulari/S2-KURAL.md (sha + OTS ile dondurulmuş). Bu dosyanın sha'sı kurala yazılıdır.

Kullanım:
  python -I s2_karne.py --veri DIZIN --mod kuru   # R1 1976–2005, hedef 2006–2015 (yalnız kod denemesi)
  python -I s2_karne.py --veri DIZIN --mod gercek # R1 1976–2015, hedef 2016–2025 (tek koşu)

DIZIN içinde: comcat_1976_2015_m5.csv, comcat_2016_2025_m6.csv (yalnız gercek), turkiye_ne10m.geojson,
Crustal_fault_sources_TOP.{shp,shx,dbf}, literatur_tablosu.json.
Çıktı: skor özeti stdout'a JSON; hücre oranları yazılmaz (olasılık yayımlanmaz).
"""
import argparse
import csv
import datetime as dt
import json
import math
import os

import numpy as np
import shapefile
from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform as shp_transform

# ---- Sabitler (kuralda aynen yazılı) ----
KUTU = (24.0, 47.0, 33.0, 44.0)  # lon_min, lon_max, lat_min, lat_max (hücre ızgarası)
HUCRE = 0.1  # derece
TAMPON_KM = 25.0  # Türkiye poligonu tamponu
DERINLIK_MAX = 40.0  # km
M_GIRDI = 5.0  # R1 girdi eşiği
M_HEDEF = 6.0  # B1 hedef eşiği
B_DEGERI = 1.0
SIGMA_R1_KM = 30.0
SIGMA_R2_KM = 15.0
TABAN_PAYI = 0.01  # R1 toplamının %1'i test bölgesine düzgün dağıtılır
MU = 3.0e10  # Pa
M_ALT_FAY = 5.0
BOOT = 2000
TOHUM = 20261110
MARMARA_KUTU = (26.5, 30.0, 40.2, 41.2)
M_MARMARA = 7.0

LAEA = Transformer.from_crs("EPSG:4326", "+proj=laea +lat_0=39 +lon_0=35 +units=km", always_xy=True)


def km_xy(lon, lat):
    return LAEA.transform(lon, lat)


def gk_pencere(m):
    d = 10 ** (0.1238 * m + 0.983)
    t = 10 ** (0.032 * m + 2.7389) if m >= 6.5 else 10 ** (0.5409 * m - 0.547)
    return d, t


def oku_katalog(yol, t0, t1, mmin):
    olaylar = []
    with open(yol) as f:
        for r in csv.DictReader(f):
            if r["type"] != "earthquake" or not r["mag"]:
                continue
            t = dt.datetime.fromisoformat(r["time"].replace("Z", "+00:00"))
            if not (t0 <= t < t1):
                continue
            m = float(r["mag"])
            z = float(r["depth"]) if r["depth"] else 0.0
            if m < mmin or z > DERINLIK_MAX:
                continue
            olaylar.append(dict(t=t, lat=float(r["latitude"]), lon=float(r["longitude"]), m=m, id=r["id"], yer=r["place"]))
    olaylar.sort(key=lambda e: e["t"])
    return olaylar


def gk_kumesizlestir(olaylar):
    """Gardner–Knopoff (1974) pencereleri; büyükten küçüğe, her iki yönde (öncü + artçı) bağımlı işaretlenir."""
    n = len(olaylar)
    xy = np.array([km_xy(e["lon"], e["lat"]) for e in olaylar]) if n else np.zeros((0, 2))
    tt = np.array([e["t"].timestamp() / 86400.0 for e in olaylar])
    mm = np.array([e["m"] for e in olaylar])
    bagimli = np.zeros(n, bool)
    for i in np.argsort(-mm, kind="stable"):
        if bagimli[i]:
            continue
        d, t = gk_pencere(mm[i])
        dist = np.hypot(xy[:, 0] - xy[i, 0], xy[:, 1] - xy[i, 1])
        sec = (dist <= d) & (np.abs(tt - tt[i]) <= t) & (mm <= mm[i])
        sec[i] = False
        bagimli |= sec
    return [e for e, b in zip(olaylar, bagimli) if not b]


def izgara():
    lo0, lo1, la0, la1 = KUTU
    nx = int(round((lo1 - lo0) / HUCRE))
    ny = int(round((la1 - la0) / HUCRE))
    lon = lo0 + HUCRE * (np.arange(nx) + 0.5)
    lat = la0 + HUCRE * (np.arange(ny) + 0.5)
    LON, LAT = np.meshgrid(lon, lat)
    X, Y = km_xy(LON, LAT)
    alan = (HUCRE * 111.195) ** 2 * np.cos(np.radians(LAT))
    return LON, LAT, np.asarray(X), np.asarray(Y), alan


def test_bolgesi(LON, LAT, X, Y, veri):
    g = json.load(open(os.path.join(veri, "turkiye_ne10m.geojson")))
    tr = shape(g["features"][0]["geometry"])
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        tr_km = shp_transform(lambda x, y, z=None: LAEA.transform(x, y), tr).buffer(TAMPON_KM)
    from shapely import contains_xy

    return contains_xy(tr_km, X, Y), tr_km


def gauss_ekle(oran, X, Y, alan, x0, y0, sigma, w):
    k = np.exp(-((X - x0) ** 2 + (Y - y0) ** 2) / (2 * sigma**2)) / (2 * math.pi * sigma**2) * alan
    oran += w * k


def r1_izgara(girdi, yil, X, Y, alan):
    """Düzleştirilmiş sismisite: M≥5 kümesizleştirilmiş, σ 30 km; M≥6'ya b=1 ile; yıllık."""
    o = np.zeros_like(X)
    for e in girdi:
        x0, y0 = km_xy(e["lon"], e["lat"])
        gauss_ekle(o, X, Y, alan, x0, y0, SIGMA_R1_KM, 1.0 / yil)
    return o * 10 ** (-B_DEGERI * (M_HEDEF - M_GIRDI))


def mw_m0(m):
    return 10 ** (1.5 * m + 9.1)


def gr_oran_m6(m0dot, mmax):
    """Kesik üstel (b=1) moment dengeli: M≥5 sayısını Ṁ0'dan çöz, M≥6 oranını ver."""
    if mmax <= M_HEDEF:
        return 0.0
    beta = B_DEGERI * math.log(10)
    ms = np.linspace(M_ALT_FAY, mmax, 2001)
    f = beta * np.exp(-beta * (ms - M_ALT_FAY)) / (1 - math.exp(-beta * (mmax - M_ALT_FAY)))
    ort_m0 = np.trapezoid(mw_m0(ms) * f, ms)
    n5 = m0dot / ort_m0
    p6 = (math.exp(-beta * (M_HEDEF - M_ALT_FAY)) - math.exp(-beta * (mmax - M_ALT_FAY))) / (
        1 - math.exp(-beta * (mmax - M_ALT_FAY))
    )
    return n5 * p6


def r2_izgara(veri, X, Y, alan, tr_km):
    """EDSF13 fay kaynakları, moment dengeli Poisson; iz boyunca 1 km adım, σ 15 km."""
    r = shapefile.Reader(os.path.join(veri, "Crustal_fault_sources_TOP"), encoding="latin1")
    o = np.zeros_like(X)
    ozet = []
    for sr in r.iterShapeRecords():
        d = sr.record.as_dict()
        pts = np.array(sr.shape.points)
        xs, ys = km_xy(pts[:, 0], pts[:, 1])
        xs, ys = np.asarray(xs), np.asarray(ys)
        from shapely.geometry import LineString

        hat = LineString(np.c_[xs, ys])
        if hat.distance(tr_km) > 50.0:
            continue
        L = hat.length
        dip = 0.5 * (d["DIPMIN"] + d["DIPMAX"])
        W = (d["MAXDEPTH"] - d["MINDEPTH"]) / max(math.sin(math.radians(dip)), 0.1)
        sr_mm = 0.5 * (d["SRMIN"] + d["SRMAX"])
        m0dot = MU * (L * 1e3) * (W * 1e3) * (sr_mm * 1e-3)
        mmax = d["MAXMAG"] if d["MAXMAG"] and d["MAXMAG"] > 0 else 5.08 + 1.16 * math.log10(max(L, 1.0))
        lam6 = gr_oran_m6(m0dot, mmax)
        ozet.append((d["IDSOURCE"], L, lam6))
        if lam6 <= 0:
            continue
        n = max(int(L), 1)
        for s in np.linspace(0, L, n + 1):
            p = hat.interpolate(s)
            gauss_ekle(o, X, Y, alan, p.x, p.y, SIGMA_R2_KM, lam6 / (n + 1))
    return o, ozet


def hucre_indeksi(e):
    lo0, _, la0, _ = KUTU
    return int((e["lat"] - la0) // HUCRE), int((e["lon"] - lo0) // HUCRE)


def poisson_skor(oran_yil, T, maske, hedefler):
    lam = oran_yil * T
    Lam = lam[maske].sum()
    ln = []
    for e in hedefler:
        i, j = hucre_indeksi(e)
        ln.append(math.log(lam[i, j]))
    return np.array(ln), Lam


def kiyas(adi, A, B, T, maske, hedefler, rng):
    la, LA = poisson_skor(A, T, maske, hedefler)
    lb, LB = poisson_skor(B, T, maske, hedefler)
    N = len(hedefler)
    if N == 0:
        return dict(satir=adi, N=0)
    d = la - lb
    ig = d.mean() - (LA - LB) / N
    boot = np.array([d[rng.integers(0, N, N)].mean() - (LA - LB) / N for _ in range(BOOT)])
    se = boot.std(ddof=1)
    z = ig / se if se > 0 else float("nan")
    hukum = "aday önde" if z > 1.645 else ("rakip önde" if z < -1.645 else "ayırt edilemez")
    return dict(
        satir=adi, N=N, IG=round(ig, 3), SE=round(se, 3), z=round(z, 2), hukum=hukum,
        beklenen_aday=round(LA, 2), beklenen_rakip=round(LB, 2),
        olay_basi=[round(x, 3) for x in d],
    )


def literatur_l1(veri, r1_yil, maske_marmara):
    tab = json.load(open(os.path.join(veri, "literatur_tablosu.json")))
    out = []
    for s in tab["sayisal"]:
        if "P10" in s and s.get("P10") is not None:
            p20 = 1 - (1 - s["P30"]) / (1 - s["P10"])
            pW = 1 - (1 - p20) ** (10 / 20)
        else:
            pW = 1 - (1 - s["P30"]) ** (10 / 30)
        out.append(dict(kimlik=s["kimlik"], aile=s["aile"], pW=round(pW, 4), lnL_olaysiz=round(math.log(1 - pW), 4)))
    # R1 Marmara kutusu, M≥7 (b=1 ile M≥6'dan)
    lam7 = r1_yil[maske_marmara].sum() * 10 ** (-B_DEGERI * (M_MARMARA - M_HEDEF)) * 10
    pR1 = 1 - math.exp(-lam7)
    out.append(dict(kimlik="R1-marmara", aile="duzlestirilmis", pW=round(pR1, 4), lnL_olaysiz=round(math.log(1 - pR1), 4)))
    return out


def ana():
    ap = argparse.ArgumentParser()
    ap.add_argument("--veri", required=True)
    ap.add_argument("--mod", choices=["kuru", "gercek"], required=True)
    a = ap.parse_args()
    utc = dt.timezone.utc
    if a.mod == "kuru":
        g0, g1 = dt.datetime(1976, 1, 1, tzinfo=utc), dt.datetime(2006, 1, 1, tzinfo=utc)
        h0, h1 = dt.datetime(2006, 1, 1, tzinfo=utc), dt.datetime(2016, 1, 1, tzinfo=utc)
        hedef_dosya = "comcat_1976_2015_m5.csv"
    else:
        g0, g1 = dt.datetime(1976, 1, 1, tzinfo=utc), dt.datetime(2016, 1, 1, tzinfo=utc)
        h0, h1 = dt.datetime(2016, 1, 1, tzinfo=utc), dt.datetime(2026, 1, 1, tzinfo=utc)
        hedef_dosya = "comcat_2016_2025_m6.csv"
    yil = (g1 - g0).days / 365.25
    T = (h1 - h0).days / 365.25

    LON, LAT, X, Y, alan = izgara()
    maske, tr_km = test_bolgesi(LON, LAT, X, Y, a.veri)
    girdi = gk_kumesizlestir(oku_katalog(os.path.join(a.veri, "comcat_1976_2015_m5.csv"), g0, g1, M_GIRDI))
    r1 = r1_izgara(girdi, yil, X, Y, alan)
    taban = TABAN_PAYI * r1[maske].sum() / maske.sum()
    r1 = r1 + np.where(maske, taban, 0.0)
    fay, ozet = r2_izgara(a.veri, X, Y, alan, tr_km)
    r2ham = fay + np.where(maske, taban, 0.0)  # kalibrasyon bilgi satırı (moment dengeli toplam)
    olcek = (r1[maske].sum() - taban * maske.sum()) / fay[maske].sum()
    r2 = fay * olcek + np.where(maske, taban, 0.0)  # hüküm: şekil kıyası, toplam R1'e eşit
    r3 = 0.5 * r1 + 0.5 * r2

    tum = oku_katalog(os.path.join(a.veri, hedef_dosya), h0, h1, M_HEDEF)
    ana_sok = gk_kumesizlestir(tum)

    def bolgede(e):
        i, j = hucre_indeksi(e)
        return 0 <= i < maske.shape[0] and 0 <= j < maske.shape[1] and maske[i, j]

    hedef = [e for e in ana_sok if bolgede(e)]
    hedef_tum = [e for e in tum if bolgede(e)]
    rng = np.random.default_rng(TOHUM)
    sonuc = dict(
        mod=a.mod, girdi_yil=round(yil, 2), T=round(T, 2), girdi_N=len(girdi),
        fay_kaynagi=len(ozet), fay_M6_yillik=round(sum(x[2] for x in ozet), 4),
        R1_M6_yillik=round(r1[maske].sum(), 4), R2ham_M6_yillik=round(r2ham[maske].sum(), 4),
        R2_olcek=round(float(olcek), 4),
        hedefler=[dict(t=e["t"].isoformat()[:10], m=e["m"], lat=e["lat"], lon=e["lon"], yer=e["yer"]) for e in hedef],
        hedef_kumeli=[dict(t=e["t"].isoformat()[:10], m=e["m"]) for e in hedef_tum],
        B1=kiyas("B1 R2(fay, şekil)-R1", r2, r1, T, maske, hedef, rng),
        B1k=kiyas("B1k R2ham(moment dengeli)-R1", r2ham, r1, T, maske, hedef, rng),
        B1b=kiyas("B1b R3(0,5/0,5)-R1", r3, r1, T, maske, hedef, rng),
        B1c=kiyas("B1c R2-R1 2023 haric", r2, r1, T, maske, [e for e in hedef if e["t"].year != 2023], rng),
        B1d=kiyas("B1d R2-R1 kumeli", r2, r1, T, maske, hedef_tum, rng),
    )
    mk = (LON >= MARMARA_KUTU[0]) & (LON <= MARMARA_KUTU[1]) & (LAT >= MARMARA_KUTU[2]) & (LAT <= MARMARA_KUTU[3])
    if a.mod == "gercek":
        sonuc["L1"] = literatur_l1(a.veri, r1, mk)
        sonuc["L1_marmara_M7_olay"] = [
            dict(t=e["t"].isoformat()[:10], m=e["m"]) for e in tum
            if e["m"] >= M_MARMARA and MARMARA_KUTU[0] <= e["lon"] <= MARMARA_KUTU[1] and MARMARA_KUTU[2] <= e["lat"] <= MARMARA_KUTU[3]
        ]
        sonuc["L2_marmara_M6_olay"] = [
            dict(t=e["t"].isoformat()[:10], m=e["m"]) for e in tum
            if MARMARA_KUTU[0] <= e["lon"] <= MARMARA_KUTU[1] and MARMARA_KUTU[2] <= e["lat"] <= MARMARA_KUTU[3]
        ]
        sonuc["L2_tau_R1"] = round(float(r1[mk & maske].sum() / r1[maske].sum()), 4)
    print(json.dumps(sonuc, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    ana()
