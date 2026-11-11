#!/usr/bin/env python3
"""TR-2 hedef sayımı (kör): birincil doğrultu atımlı olaylar, artçı asimetrisinin |A| dağılımı,
"sonraki olay" adayı var/yok, bağımsızlık kümeleri ve güç.

KÖRLÜK KURALLARI (kodun kendisi uygular):
  * Bütün ComCat sorgularının bitişi 2025-12-31T23:59:59 (assert). 2026 sorgulanmaz.
  * Artçı asimetrisinin yalnız MUTLAK değeri yazılır.
  * Sonraki olay için yalnız |doğrultu boyunca mesafe| ve |dik mesafe| hesaplanır; işaret
    (hangi tarafta) hiçbir değişkende tutulmaz, hiçbir çıktıya yazılmaz. Çıktı: aday var / yok.

Kullanım:
  python3 -I tr2_sayim.py indir  <ham_dizin>     # ComCat'ten indir (önbellekli)
  python3 -I tr2_sayim.py say    <ham_dizin> <cikti.json>   # tam satır çıktısı scratch'e; depoda yalnız özet
  python3 -I tr2_sayim.py duyarlilik <ham_dizin> <gecici.json>   # tanım varyantlarında yalnız sayılar
  python3 -I tr2_sayim.py guc K1 K2 ...                       # tek yanlı kesin binom gücü, α 0,05
Not: 1976-1989 olaylarının mekanizması ComCat'te "focal-mechanism" ürünündedir; iki sorgu birleştirilir.
"""
import csv
import io
import json
import math
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASLA = "1976-01-01"
BITIS = "2025-12-31T23:59:59"
BITIS_MS = 1767225599000  # 2025-12-31T23:59:59Z
API = "https://earthquake.usgs.gov/fdsnws/event/1/query"
GUN_MS = 86400000
YIL_MS = int(365.25 * GUN_MS)

# --- Dondurulacak parametreler (TR-2_SAYIM.md §2) ---
M_MIN, M_MAX, DERIN_MAX = 6.0, 7.2, 25.0
RAKE_SS = 30.0                 # |rake|<=30 ya da >=150
ARTCI_GUN = 30
ARTCI_M = 4.0
ARTCI_R_L = 3.0                # artçı yarıçapı = 3 L
PCA_N_MIN, PCA_ORAN_MIN = 5, 2.0
S_ICERI_KM = 5.0               # |s| < 5 km olan artçılar tarafsız sayılır
ASIM_N_MIN, ASIM_ESIK = 10, 1.0 / 3.0
SON_M, SON_DERIN = 6.0, 40.0
SON_T0_GUN, SON_T1_YIL = 30, 15
SON_S_MIN_L, SON_S_MAX_L = 0.5, 5.0
SON_D_L, SON_D_KM = 1.0, 30.0  # dik mesafe <= max(1 L, 30 km)
KUME_KM, KUME_GUN = 300.0, 365.25
BUYUK_ONCE_DISLA = False      # duyarlılık: 1 yıl içinde daha büyük bir olayın 3 L'sinde kalan birincili dışla
TR_KUTU = (35.8, 42.2, 25.5, 44.8)  # enlem min/max, boylam min/max (kaba Türkiye kutusu)


def L_km(mw):
    """Wells & Coppersmith 1994, doğrultu atımlı yeraltı kırık boyu: log10 L = 0.62 M - 2.57."""
    return 10 ** (0.62 * mw - 2.57)


# ---------------------------------------------------------------- ağ
def _ctx():
    caf = os.environ.get("SSL_CERT_FILE") or "/root/.ccr/ca-bundle.crt"
    return ssl.create_default_context(cafile=caf if os.path.exists(caf) else None)


CTX = _ctx()


def sorgu(params, deneme=5):
    end = params.get("endtime")
    assert end is not None and end <= BITIS, "KÖRLÜK: bitiş 2025-12-31 sonrası olamaz"
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, context=CTX, timeout=120) as r:
                return r.read().decode()
        except Exception as e:  # noqa
            if i == deneme - 1:
                raise
            time.sleep(2 + 3 * i)


def detay(eid, deneme=5):
    url = API + "?" + urllib.parse.urlencode({"eventid": eid, "format": "geojson"})
    for i in range(deneme):
        try:
            with urllib.request.urlopen(url, context=CTX, timeout=120) as r:
                d = json.loads(r.read().decode())
            break
        except Exception:
            if i == deneme - 1:
                return {"id": eid, "hata": True}
            time.sleep(2 + 3 * i)
    p = d["properties"]
    assert p["time"] <= BITIS_MS
    out = {"id": eid, "mt": [], "fm": []}
    for tur, anah in (("moment-tensor", "mt"), ("focal-mechanism", "fm")):
        for pr in p.get("products", {}).get(tur, []):
            q = pr.get("properties", {})
            out[anah].append({k: q[k] for k in q if k.startswith(("nodal-plane", "tensor-m", "derived-mag"))}
                             | {"_w": pr.get("preferredWeight", 0), "_src": pr.get("source")})
    return out


def indir(ham):
    os.makedirs(ham, exist_ok=True)
    # 1) Birincil adaylar (moment tensörü olan)
    f1 = os.path.join(ham, "birincil_aday.csv")
    if not os.path.exists(f1):
        t = sorgu({"format": "csv", "starttime": BASLA, "endtime": BITIS, "minmagnitude": M_MIN,
                   "maxmagnitude": M_MAX, "maxdepth": DERIN_MAX, "producttype": "moment-tensor",
                   "orderby": "time-asc", "limit": 20000})
        open(f1, "w").write(t)
    f1b = os.path.join(ham, "birincil_aday_fm.csv")  # 1976-1989 olaylarında mekanizma "focal-mechanism" ürünü
    if not os.path.exists(f1b):
        t = sorgu({"format": "csv", "starttime": BASLA, "endtime": BITIS, "minmagnitude": M_MIN,
                   "maxmagnitude": M_MAX, "maxdepth": DERIN_MAX, "producttype": "focal-mechanism",
                   "orderby": "time-asc", "limit": 20000})
        open(f1b, "w").write(t)
    aday = aday_oku(ham)
    # 2) Mekanizma ayrıntıları
    f2 = os.path.join(ham, "mekanizma.jsonl")
    var = set()
    if os.path.exists(f2):
        var = {json.loads(s)["id"] for s in open(f2) if s.strip()}
    eksik = [r["id"] for r in aday if r["id"] not in var]
    with open(f2, "a") as fo, ThreadPoolExecutor(8) as ex:
        for i, rec in enumerate(ex.map(detay, eksik)):
            fo.write(json.dumps(rec) + "\n")
            if i % 200 == 0:
                print("mekanizma", i, "/", len(eksik), flush=True)
    # 3) Sonraki olay havuzu: küresel M>=6, derinlik<=40 km
    f3 = os.path.join(ham, "m6_havuz.csv")
    if not os.path.exists(f3):
        t = sorgu({"format": "csv", "starttime": BASLA, "endtime": BITIS, "minmagnitude": SON_M,
                   "maxdepth": SON_DERIN, "orderby": "time-asc", "limit": 20000})
        open(f3, "w").write(t)
    # 4) Artçılar: her doğrultu atımlı birincil için ayrı sorgu
    birinciller = birincil_sec(ham)
    d4 = os.path.join(ham, "artci")
    os.makedirs(d4, exist_ok=True)

    def artci_indir(b):
        fn = os.path.join(d4, b["id"] + ".csv")
        if os.path.exists(fn):
            return
        t0 = b["t"]
        t1 = min(t0 + ARTCI_GUN * GUN_MS, BITIS_MS)
        iso = lambda ms: time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000))
        t = sorgu({"format": "csv", "starttime": iso(t0 + 1000), "endtime": iso(t1),
                   "latitude": b["lat"], "longitude": b["lon"],
                   "maxradiuskm": round(ARTCI_R_L * L_km(b["mw"]), 1),
                   "minmagnitude": ARTCI_M, "orderby": "time-asc", "limit": 20000})
        open(fn, "w").write(t)

    with ThreadPoolExecutor(6) as ex:
        list(ex.map(artci_indir, birinciller))
    print("indirme tamam:", len(aday), "aday,", len(birinciller), "doğrultu atımlı birincil")


# ---------------------------------------------------------------- mekanizma
def _ms(s):
    import calendar
    ms = int(round(float("0" + s[19:].rstrip("Z")) * 1000)) if len(s) > 19 and s[19] == "." else 0
    return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")) * 1000 + ms


def tensor_duzlemler(q):
    """USE bileşenlerinden iki düğüm düzlemi (doğrultu, eğim, rake)."""
    import numpy as np
    try:
        rr, tt, pp = (float(q["tensor-mrr"]), float(q["tensor-mtt"]), float(q["tensor-mpp"]))
        rt, rp, tp = (float(q["tensor-mrt"]), float(q["tensor-mrp"]), float(q["tensor-mtp"]))
    except (KeyError, ValueError):
        return None
    # NED
    M = np.array([[tt, -tp, rt], [-tp, pp, -rp], [rt, -rp, rr]])
    w, v = np.linalg.eigh(M)
    P, T = v[:, 0], v[:, 2]
    res = []
    for n, u in (((T + P), (T - P)), ((T - P), (T + P))):
        n = n / np.linalg.norm(n); u = u / np.linalg.norm(u)
        if n[2] > 0:
            n, u = -n, -u
        dip = math.degrees(math.acos(max(-1, min(1, -n[2]))))
        stk = math.degrees(math.atan2(-n[0], n[1])) % 360
        sd = math.sin(math.radians(dip)) or 1e-9
        ph = math.radians(stk)
        rake = math.degrees(math.atan2(-u[2] / sd, u[0] * math.cos(ph) + u[1] * math.sin(ph)))
        res.append((stk, dip, rake))
    return res


def duzlemler(rec):
    for anah in ("mt", "fm"):
        for q in sorted(rec.get(anah, []), key=lambda z: -float(z.get("_w") or 0)):
            try:
                return [(float(q[f"nodal-plane-{i}-strike"]), float(q[f"nodal-plane-{i}-dip"]),
                         float(q.get(f"nodal-plane-{i}-rake", q.get(f"nodal-plane-{i}-slip"))))
                        for i in (1, 2)], "duzlem"
            except (KeyError, TypeError, ValueError):
                pass
            if anah == "mt":
                r = tensor_duzlemler(q)
                if r:
                    return r, "tensor"
    return None, None


def ss_mi(dz):
    return any(abs(((r + 180) % 360) - 180) <= RAKE_SS or abs(((r + 180) % 360) - 180) >= 180 - RAKE_SS
               for _, _, r in dz)


def aday_oku(ham):
    gor, out = set(), []
    for f in ("birincil_aday.csv", "birincil_aday_fm.csv"):
        for r in csv.DictReader(open(os.path.join(ham, f))):
            if r["id"] not in gor:
                gor.add(r["id"]); out.append(r)
    return sorted(out, key=lambda r: r["time"])


def birincil_sec(ham, istat=None):
    aday = aday_oku(ham)
    mek = {}
    for s in open(os.path.join(ham, "mekanizma.jsonl")):
        if s.strip():
            r = json.loads(s); mek[r["id"]] = r
    out = []
    st = {"aday": len(aday), "mw_disi": 0, "mekanizma_yok": 0, "ss_degil": 0, "tensor_turetme": 0}
    for r in aday:
        mt = r["magType"].lower()
        if not mt.startswith("mw"):
            st["mw_disi"] += 1; continue
        dz, kay = duzlemler(mek.get(r["id"], {}))
        if not dz:
            st["mekanizma_yok"] += 1; continue
        if not ss_mi(dz):
            st["ss_degil"] += 1; continue
        st["tensor_turetme"] += kay == "tensor"
        out.append({"id": r["id"], "t": _ms(r["time"]), "lat": float(r["latitude"]),
                    "lon": float(r["longitude"]), "dep": float(r["depth"] or 0), "mw": float(r["mag"]),
                    "dz": dz, "yer": r["place"]})
    if istat is not None:
        istat.update(st)
    return out


# ---------------------------------------------------------------- geometri
R_E = 6371.0


def mesafe_az(la1, lo1, la2, lo2):
    p1, p2 = math.radians(la1), math.radians(la2)
    dl = math.radians(lo2 - lo1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    d = 2 * R_E * math.asin(min(1, math.sqrt(a)))
    az = math.degrees(math.atan2(math.sin(dl) * math.cos(p2),
                                 math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)))
    return d, az


def eksen_bilesen(b, la, lo, stk):
    """(s, d): doğrultu boyunca ve dik konum (km). YALNIZ artçı asimetrisi için çağrılır."""
    d, az = mesafe_az(b["lat"], b["lon"], la, lo)
    a = math.radians(az - stk)
    return d * math.cos(a), d * math.sin(a)


def mutlak_eksen(b, la, lo, stk):
    """Sonraki olay için: yalnız |s| ve |d|. İşaret burada atılır, dışarı çıkmaz."""
    d, az = mesafe_az(b["lat"], b["lon"], la, lo)
    a = math.radians(az - stk)
    return abs(d * math.cos(a)), abs(d * math.sin(a))


def pca_azimut(xy):
    import numpy as np
    X = np.array(xy); X = X - X.mean(0)
    C = X.T @ X / len(X)
    w, v = np.linalg.eigh(C)
    e = v[:, 1]  # (doğu, kuzey)
    az = math.degrees(math.atan2(e[0], e[1])) % 180
    oran = w[1] / max(w[0], 1e-9)
    return az, oran


def ac_fark(a, b):
    d = abs((a - b) % 180)
    return min(d, 180 - d)


# ---------------------------------------------------------------- sayım
def say(ham, cikti):
    import numpy as np
    istat = {}
    B = birincil_sec(ham, istat)
    havuz = [r for r in csv.DictReader(open(os.path.join(ham, "m6_havuz.csv")))]
    havuz = [{"id": r["id"], "t": _ms(r["time"]), "lat": float(r["latitude"]), "lon": float(r["longitude"]),
              "m": float(r["mag"])} for r in havuz]
    assert all(h["t"] <= BITIS_MS for h in havuz)
    if BUYUK_ONCE_DISLA:
        def golgede(b):
            for h in havuz:
                if h["m"] > b["mw"] and 0 < b["t"] - h["t"] <= YIL_MS:
                    if mesafe_az(h["lat"], h["lon"], b["lat"], b["lon"])[0] <= ARTCI_R_L * L_km(h["m"]):
                        return True
            return False
        B = [b for b in B if not golgede(b)]
    satir = []
    for b in B:
        L = L_km(b["mw"])
        rows = list(csv.DictReader(open(os.path.join(ham, "artci", b["id"] + ".csv"))))
        art = []
        for r in rows:
            if r["id"] == b["id"] or not r["mag"]:
                continue
            m = float(r["mag"])
            if m < ARTCI_M:
                continue
            if m >= b["mw"]:
                continue  # birincilden büyük/eşit olay artçı sayılmaz
            art.append((float(r["latitude"]), float(r["longitude"]), m))
        z = {"id": b["id"], "yil": time.gmtime(b["t"] / 1000).tm_year, "mw": b["mw"], "L": round(L, 1),
             "tr": TR_KUTU[0] <= b["lat"] <= TR_KUTU[1] and TR_KUTU[2] <= b["lon"] <= TR_KUTU[3],
             "n_artci": len(art), "n_artci_45": sum(1 for a in art if a[2] >= 4.5)}
        # doğrultu seçimi: artçı bulutu ana ekseni
        stk = None
        if len(art) >= PCA_N_MIN:
            xy = []
            for la, lo, _ in art:
                d, az = mesafe_az(b["lat"], b["lon"], la, lo)
                xy.append((d * math.sin(math.radians(az)), d * math.cos(math.radians(az))))
            paz, oran = pca_azimut(xy)
            z["pca_oran"] = round(float(oran), 2)
            if oran >= PCA_ORAN_MIN:
                (s1, _, _), (s2, _, _) = b["dz"]
                stk = s1 if ac_fark(s1, paz) <= ac_fark(s2, paz) else s2
                z["duzlem_pca_fark"] = round(min(ac_fark(s1, paz), ac_fark(s2, paz)), 1)
        z["dogrultu_var"] = stk is not None
        # asimetri: yalnız |A|
        if stk is not None:
            npoz = nneg = 0
            for la, lo, _ in art:
                s, _ = eksen_bilesen(b, la, lo, stk)
                if s >= S_ICERI_KM:
                    npoz += 1
                elif s <= -S_ICERI_KM:
                    nneg += 1
            n = npoz + nneg
            z["n_taraf"] = n
            z["absA"] = round(abs(npoz - nneg) / n, 3) if n else None
            # iki yanlı binom p (simetrik; işaret içermez)
            k = max(npoz, nneg)
            z["binom_p"] = (min(1.0, 2 * sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n) if n else None)
            del npoz, nneg, k
            z["asim_olculur"] = n >= ASIM_N_MIN and z["absA"] >= ASIM_ESIK
        else:
            z["asim_olculur"] = False
        # sonraki olay: yalnız var/yok (mutlak mesafelerle)
        if stk is not None:
            t0 = b["t"] + SON_T0_GUN * GUN_MS
            t1 = min(b["t"] + SON_T1_YIL * YIL_MS, BITIS_MS)
            z["takip_yil"] = round((t1 - b["t"]) / YIL_MS, 2)
            var = 0
            for h in havuz:
                if h["id"] == b["id"] or not (t0 <= h["t"] <= t1):
                    continue
                if abs(h["lat"] - b["lat"]) > 8:
                    continue
                aS, aD = mutlak_eksen(b, h["lat"], h["lon"], stk)
                if SON_S_MIN_L * L <= aS <= SON_S_MAX_L * L and aD <= max(SON_D_L * L, SON_D_KM):
                    var += 1
            z["sonraki_aday_sayisi"] = var
            z["sonraki_var"] = var > 0
        else:
            z["sonraki_var"] = None
        z["_lat"], z["_lon"], z["_t"] = b["lat"], b["lon"], b["t"]
        satir.append(z)

    # bağımsızlık kümeleri (tüm doğrultu atımlı birinciller, tek bağlantı)
    n = len(satir)
    ana = list(range(n))

    def bul(i):
        while ana[i] != i:
            ana[i] = ana[ana[i]]; i = ana[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if abs(satir[j]["_t"] - satir[i]["_t"]) > KUME_GUN * GUN_MS:
                continue
            d, _ = mesafe_az(satir[i]["_lat"], satir[i]["_lon"], satir[j]["_lat"], satir[j]["_lon"])
            if d <= KUME_KM:
                ana[bul(i)] = bul(j)
    for i, z in enumerate(satir):
        z["kume"] = bul(i)

    def kume_say(f):
        return len({z["kume"] for z in satir if f(z)})

    nit = lambda z: z["asim_olculur"] and z["sonraki_var"]
    nit_bp = lambda z: z["dogrultu_var"] and z.get("n_taraf", 0) >= ASIM_N_MIN and z["binom_p"] <= 0.05 and z["sonraki_var"]
    ozet = {
        "istat": istat,
        "birincil_N": len(satir),
        "birincil_TR": sum(z["tr"] for z in satir),
        "dogrultu_secilebilen_N": sum(z["dogrultu_var"] for z in satir),
        "asim_olculur_N": sum(z["asim_olculur"] for z in satir),
        "asim_olculur_TR": sum(z["asim_olculur"] and z["tr"] for z in satir),
        "sonraki_var_N": sum(bool(z["sonraki_var"]) for z in satir),
        "sonraki_var_TR": sum(bool(z["sonraki_var"]) and z["tr"] for z in satir),
        "nitelikli_N": sum(nit(z) for z in satir),
        "nitelikli_TR": sum(nit(z) and z["tr"] for z in satir),
        "kume_tum": kume_say(lambda z: True),
        "K": kume_say(nit),
        "K_TR": kume_say(lambda z: nit(z) and z["tr"]),
        "K_binom_p05": kume_say(nit_bp),
        "K_asim_yok_sonraki_var": kume_say(lambda z: z["dogrultu_var"] and z["sonraki_var"]),
        "absA_ceyrekler_dogrultulu_n10": [round(float(x), 3) for x in np.percentile(
            [z["absA"] for z in satir if z.get("n_taraf", 0) >= ASIM_N_MIN], [10, 25, 50, 75, 90])]
        if any(z.get("n_taraf", 0) >= ASIM_N_MIN for z in satir) else None,
        "absA_dagilim_n10": {},
        "on_yil": {},
        "duzlem_pca_fark_medyan": float(np.median([z["duzlem_pca_fark"] for z in satir if "duzlem_pca_fark" in z])),
    }
    kutu = [(0, .1), (.1, .2), (.2, 1 / 3), (1 / 3, .5), (.5, .75), (.75, 1.01)]
    vals = [z["absA"] for z in satir if z.get("n_taraf", 0) >= ASIM_N_MIN]
    for a, b_ in kutu:
        ozet["absA_dagilim_n10"][f"[{a:.2f},{min(b_,1):.2f})"] = sum(a <= v < b_ for v in vals)
    for z in satir:
        dk = f"{z['yil'] // 10 * 10}s"
        o = ozet["on_yil"].setdefault(dk, {"birincil": 0, "dogrultu": 0, "asim": 0, "sonraki": 0, "nitelikli": 0})
        o["birincil"] += 1; o["dogrultu"] += z["dogrultu_var"]; o["asim"] += z["asim_olculur"]
        o["sonraki"] += bool(z["sonraki_var"]); o["nitelikli"] += nit(z)
    # Duyarlılık: artçı eşiği M>=4,5 ile yeterli sayı (yalnız sayı)
    ozet["n_artci45_ge10"] = sum(z["n_artci_45"] >= 10 for z in satir)
    for z in satir:
        for k in ("_lat", "_lon", "_t"):
            z.pop(k)
    json.dump({"ozet": ozet, "satirlar": satir}, open(cikti, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- güç
def guc(K, p, alfa=0.05):
    c = next(c for c in range(K + 2) if sum(math.comb(K, i) for i in range(c, K + 1)) / 2 ** K <= alfa)
    return c, sum(math.comb(K, i) * p ** i * (1 - p) ** (K - i) for i in range(c, K + 1))


def mde(K, hedef=0.8):
    p = 0.5
    while p < 1:
        if guc(K, p)[1] >= hedef:
            return round(p, 3)
        p += 0.001
    return None


if __name__ == "__main__":
    if sys.argv[1] == "indir":
        indir(sys.argv[2])
    elif sys.argv[1] == "say":
        say(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "duyarlilik":
        g = globals()
        varyant = [("ana", {}), ("pca_oran_1.5", {"PCA_ORAN_MIN": 1.5}), ("asim_esik_0.2", {"ASIM_ESIK": 0.2}),
                   ("asim_n_min_8", {"ASIM_N_MIN": 8}), ("buyuk_once_disla", {"BUYUK_ONCE_DISLA": True}),
                   ("son_dik_1L", {"SON_D_KM": 0.0}), ("artci_M4.5", {"ARTCI_M": 4.5})]
        ilk = {k: g[k] for _, v in varyant for k in v}
        import contextlib
        for ad, v in varyant:
            g.update(ilk); g.update(v)
            with contextlib.redirect_stdout(io.StringIO()):
                say(sys.argv[2], sys.argv[3])
            o = json.load(open(sys.argv[3]))["ozet"]
            print(ad, {k: o[k] for k in ("birincil_N", "dogrultu_secilebilen_N", "asim_olculur_N",
                                         "sonraki_var_N", "nitelikli_N", "K", "K_TR")}, "MDE80", mde(o["K"]))
    elif sys.argv[1] == "guc":
        for K in map(int, sys.argv[2:]):
            print(K, [(p, guc(K, p)[0], round(guc(K, p)[1], 3)) for p in (0.6, 0.65, 0.7)], "MDE80", mde(K))
