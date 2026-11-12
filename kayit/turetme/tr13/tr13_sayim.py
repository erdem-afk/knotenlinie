#!/usr/bin/env python3
"""TR-13 örneklem sayımı (0 €, ön kayıt değil): M >= 6,0 sığ doğrultu atımlı ana şoklardan önce, kırık boyu ölçekli
bir dairede, açık kataloglarda kaç kümesizleştirilmiş arka plan olayı var?

KÖRLÜK (kod uygular):
  * Bütün sorguların bitişi <= 2025-12-31T23:59:59 (assert). 2026 sorgulanmaz.
  * Okuyucu zamanı >= 2026-01-01 olan satırı sayılmadan atar.
  * Yalnız ana şok ÖNCESİ pencereler indirilir ([t - 10 y, t)). Ana şok sonrası hiçbir veri istenmez
    (TR-6a / TR-2 olay sonrası pencerelerine dokunulmaz).
  * Yerelleşme ölçüsü (V(q), Gini) GERÇEK veride HESAPLANMAZ; yalnız sayı, Mc ve kümesizleştirilmiş sayı yazılır.

Alt komutlar:
  python3 -I -B tr13_sayim.py anasok  <ham> <tr2_ham>      ana şok adayları + mekanizma (TR-2 anlık görüntüsü
                                                             yeniden kullanılır, eksikler indirilir)
  python3 -I -B tr13_sayim.py katalog <ham> <tr2_ham> [ComCat|ISC|GeoNet|INGV|EMSC] [id_listesi.txt]
                                                             ana şok başına daire kataloğu (ComCat [t-10y, t),
                                                             ötekiler [t-5y, t))
  python3 -I -B tr13_sayim.py say     <ham> <tr2_ham> <cikti.json>    sayım tablosu (depoya yalnız özet)
"""
import calendar
import csv
import hashlib
import io
import json
import math
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BURA, "..", "tr2"))
import tr2_sayim as T2  # noqa: E402  (duzlemler, ss_mi, L_km, mesafe_az, detay)

import numpy as np  # noqa: E402

BASLA = "1980-01-01"
BITIS = "2025-12-31T23:59:59"
BITIS_MS = calendar.timegm((2025, 12, 31, 23, 59, 59)) * 1000
KOR_MS = calendar.timegm((2026, 1, 1, 0, 0, 0)) * 1000
GUN_MS = 86400000
YIL_MS = int(365.25 * GUN_MS)
UA = "Mozilla/5.0 (compatible; research-catalog-client)"

M_MIN, DERIN_MAX = 6.0, 30.0
ONCE_YIL = 10.0                      # indirilen önce-pencere uzunluğu
PRE_YIL = 3.0                        # BZ20: yerelleşme 2–3 yıl önce -> sınama penceresi [t-3y, t)
SAY_YIL = 5.0                        # sayım tablosunun "önceki >= 5 yıl" penceresi
R_KAT, R_MIN = 2.0, 50.0             # ana bölge: daire yarıçapı max(2 L, 50 km)
R_IND_KAT, R_IND_MIN = 3.0, 75.0     # indirilen daire (kenar etkisi için kümesizleştirme payı)
ARTCI_YIL, ARTCI_L = 1.0, 3.0        # ana şok tanımı: 1 yıl içinde 3 L(büyük) içinde >= M olay yoksa
MIN_INDIR_M = 1.0

CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt")
                                 else None)

SERVIS = {
    "ComCat": "https://earthquake.usgs.gov/fdsnws/event/1/query",
    "ISC": "https://www.isc.ac.uk/fdsnws/event/1/query",
    "GeoNet": "https://service.geonet.org.nz/fdsnws/event/1/query",
    "INGV": "https://webservices.ingv.it/fdsnws/event/1/query",
    "EMSC": "https://www.seismicportal.eu/fdsnws/event/1/query",
}
KUTU = {  # (enlem min, max, boylam min, max) — bölgesel servisin kapsamı (kaba)
    "GeoNet": (-52, -25, 160, 190),
    "INGV": (35, 48, 5, 20),
    "EMSC": (28, 50, -15, 50),
}


def iso(ms):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000))


def ms_of(s):
    s = s.strip().replace("Z", "").replace(" ", "T")
    frac = 0
    if "." in s[19:]:
        frac = int(round(float("0" + s[19:]) * 1000))
    return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")) * 1000 + frac


def getir(url, onb, zaman_asimi=300, deneme=6):
    """Önbellekli GET. 204/404 (FDSN 'veri yok') boş metin döner. 401/403 aşılmaz."""
    assert "endtime" not in url or urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)["endtime"][0] <= BITIS, \
        "KÖRLÜK: bitiş 2025-12-31 sonrası olamaz"
    os.makedirs(onb, exist_ok=True)
    yol = os.path.join(onb, hashlib.sha256(url.encode()).hexdigest()[:24] + ".txt")
    if os.path.exists(yol):
        return open(yol, encoding="utf-8", errors="replace").read()
    son = None
    for i in range(deneme):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=zaman_asimi, context=CTX) as r:
                metin = "" if r.status == 204 else r.read().decode("utf-8", errors="replace")
            break
        except urllib.error.HTTPError as e:
            if e.code in (204, 404):
                metin = ""
                break
            son = f"HTTP {e.code}"
            if e.code in (400, 401, 403):
                raise RuntimeError(son + " " + url)
        except Exception as e:  # noqa
            son = type(e).__name__
        time.sleep(min(60, 3 * 2 ** i))
    else:
        raise RuntimeError(f"erişilemedi ({son}) {url}")
    with open(yol, "w") as f:
        f.write(metin)
    return metin


# ------------------------------------------------------------------ ana şoklar
def anasok(ham, tr2ham):
    os.makedirs(ham, exist_ok=True)
    onb = os.path.join(ham, "onbellek")
    for pt, fn in (("moment-tensor", "aday_mt.csv"), ("focal-mechanism", "aday_fm.csv")):
        q = dict(format="csv", starttime=BASLA, endtime=BITIS, minmagnitude=M_MIN, maxdepth=DERIN_MAX,
                 producttype=pt, orderby="time-asc", limit=20000)
        t = getir(T2.API + "?" + urllib.parse.urlencode(q), onb)
        open(os.path.join(ham, fn), "w").write(t)
    # havuz: ana şok / artçı ayrımı ve depremsiz kontrol pencereleri için M >= 5,5, derinlik <= 70 km, 1970+
    parcalar = []
    for y0, y1 in ((1970, 1985), (1985, 1995), (1995, 2005), (2005, 2015), (2015, 2026)):
        q = dict(format="csv", starttime=f"{y0}-01-01", endtime=BITIS if y1 == 2026 else f"{y1 - 1}-12-31T23:59:59",
                 minmagnitude=5.5, maxdepth=70, orderby="time-asc", limit=20000)
        t = getir(T2.API + "?" + urllib.parse.urlencode(q), onb)
        satirlar = t.splitlines()
        assert len(satirlar) - 1 < 20000, "havuz parçası limit doldu"
        parcalar.append(satirlar if not parcalar else satirlar[1:])
    open(os.path.join(ham, "havuz_m55.csv"), "w").write("\n".join(s for p in parcalar for s in p) + "\n")
    # mekanizma: TR-2 anlık görüntüsü + eksikler
    mek = {}
    for s in open(os.path.join(tr2ham, "mekanizma.jsonl")):
        if s.strip():
            r = json.loads(s)
            if not r.get("hata"):
                mek[r["id"]] = r
    f2 = os.path.join(ham, "mekanizma_ek.jsonl")
    if os.path.exists(f2):
        for s in open(f2):
            if s.strip():
                r = json.loads(s)
                mek[r["id"]] = r
    aday = aday_oku(ham)
    eksik = [r["id"] for r in aday if r["id"] not in mek and r["magType"].lower().startswith("mw")]
    print("aday", len(aday), "mekanizma eksik", len(eksik), flush=True)
    with open(f2, "a") as fo:
        for i, eid in enumerate(eksik):
            rec = T2.detay(eid)
            fo.write(json.dumps(rec) + "\n")
            if i % 50 == 0:
                print("mekanizma", i, "/", len(eksik), flush=True)


def aday_oku(ham):
    gor, out = set(), []
    for f in ("aday_mt.csv", "aday_fm.csv"):
        for r in csv.DictReader(open(os.path.join(ham, f))):
            if r["id"] not in gor and ms_of(r["time"]) < KOR_MS:
                gor.add(r["id"])
                out.append(r)
    return sorted(out, key=lambda r: r["time"])


def mekanizmalar(ham, tr2ham):
    mek = {}
    for fn in (os.path.join(tr2ham, "mekanizma.jsonl"), os.path.join(ham, "mekanizma_ek.jsonl")):
        if os.path.exists(fn):
            for s in open(fn):
                if s.strip():
                    r = json.loads(s)
                    if not r.get("hata"):
                        mek[r["id"]] = r
    return mek


def havuz_oku(ham):
    H = []
    for r in csv.DictReader(open(os.path.join(ham, "havuz_m55.csv"))):
        t = ms_of(r["time"])
        if t >= KOR_MS or not r["mag"]:
            continue
        H.append((t, float(r["latitude"]), float(r["longitude"]), float(r["mag"]), r["id"]))
    return H


def ana_soklar(ham, tr2ham):
    """Doğrultu atımlı, Mw, ana şok (1 yıl içinde 3 L(büyük) içinde >= M öncül olay yok)."""
    mek = mekanizmalar(ham, tr2ham)
    H = havuz_oku(ham)
    Ht = np.array([h[0] for h in H])
    st = {"aday": 0, "mw_disi": 0, "mekanizma_yok": 0, "ss_degil": 0, "artci_ya_da_oncu_golgesi": 0}
    out = []
    for r in aday_oku(ham):
        st["aday"] += 1
        if not r["magType"].lower().startswith("mw"):
            st["mw_disi"] += 1
            continue
        dz, _ = T2.duzlemler(mek.get(r["id"], {}))
        if not dz:
            st["mekanizma_yok"] += 1
            continue
        if not T2.ss_mi(dz):
            st["ss_degil"] += 1
            continue
        t, la, lo, m = ms_of(r["time"]), float(r["latitude"]), float(r["longitude"]), float(r["mag"])
        # artçı mı: önceki 1 yılda, büyüklüğü >= m olan ve 3 L(M_büyük) içinde bir olay
        i0, i1 = np.searchsorted(Ht, t - ARTCI_YIL * YIL_MS), np.searchsorted(Ht, t)
        golge = False
        for h in H[i0:i1]:
            if h[4] == r["id"] or h[3] < m:
                continue
            if T2.mesafe_az(la, lo, h[1], h[2])[0] <= ARTCI_L * T2.L_km(h[3]):
                golge = True
                break
        if golge:
            st["artci_ya_da_oncu_golgesi"] += 1
            continue
        L = T2.L_km(m)
        out.append(dict(id=r["id"], t=t, zaman=iso(t), enlem=la, boylam=lo, derinlik=float(r["depth"] or 0),
                        M=m, L=round(L, 1), R=round(max(R_KAT * L, R_MIN), 1),
                        R_ind=round(max(R_IND_KAT * L, R_IND_MIN), 1), yer=r["place"]))
    return out, st


# ------------------------------------------------------------------ katalog
def fdsn_text(metin):
    """FDSN text (| ayraçlı) -> dizi sözlüğü. 2026+ satırlar sayılmadan atılır."""
    t, la, lo, de, m = [], [], [], [], []
    for s in metin.splitlines():
        if not s.strip() or s.startswith("#"):
            continue
        a = s.split("|")
        if len(a) < 11:
            continue
        try:
            tt = ms_of(a[1])
            if tt >= KOR_MS:
                continue
            mm = float(a[10])
        except ValueError:
            continue
        t.append(tt); la.append(float(a[2])); lo.append(float(a[3]))
        de.append(float(a[4]) if a[4].strip() else 0.0); m.append(mm)
    return dict(t=np.array(t, float), la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m))


def comcat_csv(metin):
    t, la, lo, de, m = [], [], [], [], []
    for r in csv.DictReader(io.StringIO(metin)):
        if not r.get("mag"):
            continue
        tt = ms_of(r["time"])
        if tt >= KOR_MS:
            continue
        t.append(tt); la.append(float(r["latitude"])); lo.append(float(r["longitude"]))
        de.append(float(r["depth"] or 0)); m.append(float(r["mag"]))
    return dict(t=np.array(t, float), la=np.array(la), lo=np.array(lo), de=np.array(de), m=np.array(m))


def birlestir(ds):
    return {k: np.concatenate([d[k] for d in ds]) if ds else np.zeros(0) for k in ("t", "la", "lo", "de", "m")}


def daire_indir(servis, o, t0, t1, onb, mmin=MIN_INDIR_M, limit=20000, derinlik=0):
    """[t0, t1) dairesi; limit dolarsa zamanı ikiye böler (en çok 8 kez)."""
    assert t1 <= BITIS_MS + 1000
    if servis == "ComCat":
        q = dict(format="csv", latitude=f"{o['enlem']:.4f}", longitude=f"{o['boylam']:.4f}",
                 maxradiuskm=f"{o['R_ind']:.1f}", starttime=iso(t0), endtime=iso(t1 - 1000),
                 minmagnitude=f"{mmin:.1f}", eventtype="earthquake", orderby="time-asc", limit=limit)
        d = comcat_csv(getir(SERVIS[servis] + "?" + urllib.parse.urlencode(q), onb))
    else:
        q = dict(format="text", latitude=f"{o['enlem']:.4f}", longitude=f"{o['boylam']:.4f}",
                 maxradius=f"{o['R_ind'] / 111.195:.4f}", starttime=iso(t0), endtime=iso(t1 - 1000),
                 minmagnitude=f"{mmin:.1f}")
        if servis != "GeoNet":
            q["limit"] = limit
        d = fdsn_text(getir(SERVIS[servis] + "?" + urllib.parse.urlencode(q), onb, zaman_asimi=900))
    if len(d["t"]) >= limit and derinlik < 8:
        orta = (t0 + t1) // 2
        return birlestir([daire_indir(servis, o, t0, orta, onb, mmin, limit, derinlik + 1),
                          daire_indir(servis, o, orta, t1, onb, mmin, limit, derinlik + 1)])
    return d


def katalog(ham, tr2ham, servis="ComCat", sadece=None):
    A, _ = ana_soklar(ham, tr2ham)
    onb = os.path.join(ham, "onbellek_" + servis)
    if sadece is None:
        hedef = list(A)
    else:  # verilen sırayla (ör. büyükten küçüğe)
        byid = {o["id"]: o for o in A}
        hedef = [byid[i] for i in sadece if i in byid]
    if servis in KUTU:
        a, b, c, e = KUTU[servis]
        hedef = [o for o in hedef if a <= o["enlem"] <= b and (c <= (o["boylam"] % 360) <= e or c <= o["boylam"] <= e)]
    print(servis, "hedef", len(hedef), flush=True)
    for i, o in enumerate(hedef):
        if os.path.exists(os.path.join(ham, f"kat_{servis}_{o['id']}.npz")):
            continue
        # ComCat: [t-10y, t); öteki servisler yavaş: yalnız [t-5y, t) (sayım penceresi)
        t0 = int(o["t"] - (ONCE_YIL if servis == "ComCat" else SAY_YIL) * YIL_MS)
        try:
            d = daire_indir(servis, o, t0, int(o["t"]), onb)
        except RuntimeError as e:
            print("HATA", o["id"], e, flush=True)
            continue
        np.savez_compressed(os.path.join(ham, f"kat_{servis}_{o['id']}.npz"), **d)
        if i % 25 == 0:
            print(servis, i, "/", len(hedef), o["id"], len(d["t"]), flush=True)


ORNEK_G = 90          # örnek pencere (gün), merkezi t - 2 y
ORNEK_MERKEZ_Y = 2.0


def ornek(ham, tr2ham, servis, sadece, is_parcacik=3, merkez_y=None, onek="orn"):
    """Yavaş servisler için örnek pencere: [t-2y-45g, t-2y+45g), daire R (ana bölge), M >= 0.
    Yalnız sayı ve büyüklük dağılımı saklanır; tam sayım değildir (örnekten tahmin)."""
    from concurrent.futures import ThreadPoolExecutor
    A, _ = ana_soklar(ham, tr2ham)
    byid = {o["id"]: o for o in A}
    hedef = [byid[i] for i in sadece if i in byid]
    if servis in KUTU:
        a, b, c, e = KUTU[servis]
        hedef = [o for o in hedef if a <= o["enlem"] <= b and c <= (o["boylam"] % 360 if c > 180 or e > 180
                                                                      else o["boylam"]) <= e]
    onb = os.path.join(ham, "onbellek_" + servis + "_" + onek)

    def bir(o):
        fn = os.path.join(ham, f"{onek}_{servis}_{o['id']}.npz")
        if os.path.exists(fn):
            return
        orta = o["t"] - (merkez_y or ORNEK_MERKEZ_Y) * YIL_MS
        t0, t1 = int(orta - ORNEK_G / 2 * GUN_MS), int(orta + ORNEK_G / 2 * GUN_MS)
        q = dict(format="text", latitude=f"{o['enlem']:.4f}", longitude=f"{o['boylam']:.4f}",
                 maxradius=f"{o['R'] / 111.195:.4f}", starttime=iso(t0), endtime=iso(t1))
        if servis != "GeoNet":
            q["limit"] = 20000
        try:
            d = fdsn_text(getir(SERVIS[servis] + "?" + urllib.parse.urlencode(q), onb, zaman_asimi=900))
        except RuntimeError as e:
            print("HATA", o["id"], e, flush=True)
            return
        np.savez_compressed(fn, **d)

    with ThreadPoolExecutor(is_parcacik) as ex:
        for i, _ in enumerate(ex.map(bir, hedef)):
            if i % 50 == 0:
                print(servis, "örnek", i, "/", len(hedef), flush=True)


def ornek_olc(o, d, f_bg):
    """Örnekten tahmin: Mc (MAXC+0,2 / +0,3), 3 yıllık sayı = örnek sayısı x (3 y / 90 g), arka plan payı f_bg."""
    if len(d["t"]) == 0:
        return dict(n_ornek=0, mc=None)
    r = uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
    ic = (r <= o["R"]) & (d["de"] <= DERIN_MAX + 10)
    m = d["m"][ic]
    if m.size >= 50:
        mc = maxc(m) + 0.2
    elif m.size >= 20:
        mc = maxc(m) + 0.3
    else:
        return dict(n_ornek=int(m.size), mc=None)
    olcek = PRE_YIL * 365.25 / ORNEK_G
    res = dict(n_ornek=int(m.size), mc=round(mc, 2), tur="örnekten tahmin")
    for etik, mcx in (("mc", mc), ("mc05", mc + 0.5), ("m30", max(mc, 3.0)), ("m40", max(mc, 4.0)),
                      ("m45", max(mc, 4.5))):
        n = int((m >= mcx - 1e-6).sum())
        res[f"N3bg_{etik}"] = round(n * olcek * f_bg, 1)
    return res


def tam3(ham, tr2ham, servis, sayim_json, esik=25.0):
    """Örnekten tahminle en iyi katalog `servis`_ornek olan ve N3bg_mc >= esik olaylar için önce-pencerenin
    [t-3y, t) TAM indirmesi; daire R (ana bölge), en küçük büyüklük = örnek Mc - 0,3; yıl yıl istek."""
    D = json.load(open(sayim_json))
    sec = [z for z in D["satir"] if z.get("en_iyi") == servis + "_ornek" and z["N3bg_en_iyi"]["mc"] >= esik]
    sec.sort(key=lambda z: -z["N3bg_en_iyi"]["mc"])
    onb = os.path.join(ham, "onbellek_" + servis + "_tam3")
    print(servis, "tam3 hedef", len(sec), flush=True)
    from concurrent.futures import ThreadPoolExecutor

    def bir(o):
        fn = os.path.join(ham, f"tam3_{servis}_{o['id']}.npz")
        if os.path.exists(fn):
            return
        mmin = max(-1.0, o["kataloglar"][servis + "_ornek"]["mc"] - 0.3)
        parca = []
        t0 = int(o["t"] - PRE_YIL * YIL_MS)
        while t0 < o["t"]:
            t1 = int(min(o["t"], t0 + YIL_MS))
            q = dict(format="text", latitude=f"{o['enlem']:.4f}", longitude=f"{o['boylam']:.4f}",
                     maxradius=f"{o['R'] / 111.195:.4f}", starttime=iso(t0), endtime=iso(t1 - 1000),
                     minmagnitude=f"{mmin:.1f}")
            if servis != "GeoNet":
                q["limit"] = 20000
            d = fdsn_text(getir(SERVIS[servis] + "?" + urllib.parse.urlencode(q), onb, zaman_asimi=900))
            assert len(d["t"]) < 20000, "limit doldu"
            parca.append(d)
            t0 = t1
        np.savez_compressed(fn, **birlestir(parca))
        print(servis, o["id"], o["zaman"][:10], int(sum(len(p["t"]) for p in parca)), flush=True)

    with ThreadPoolExecutor(3) as ex:
        list(ex.map(bir, sec))


def tam3_olc(o, d):
    """[t-3y, t) tam indirme: Mc = MAXC+0,2 (bu pencerede), GK74 bu daire içinde (kenar payı yok)."""
    if len(d["t"]) == 0:
        return dict(n=0, mc=None)
    r = uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
    ic = (r <= o["R"]) & (d["de"] <= DERIN_MAX + 10) & (d["t"] < o["t"])
    m = d["m"][ic]
    if m.size < 50:
        return dict(n=int(m.size), mc=None)
    mc = maxc(m) + 0.2
    bg = gk74(d["t"], d["la"], d["lo"], d["m"])
    res = dict(n=int(m.size), mc=round(mc, 2), tur="tam sayım (3 y, R)")
    for etik, mcx in (("mc", mc), ("mc05", mc + 0.5), ("m30", max(mc, 3.0)), ("m40", max(mc, 4.0)),
                      ("m45", max(mc, 4.5))):
        ust = d["m"] >= mcx - 1e-6
        res[f"N3bg_{etik}"] = int((ic & ust & bg).sum())
        res[f"N3_{etik}"] = int((ic & ust).sum())
    return res


# ------------------------------------------------------------------ Mc, kümesizleştirme, sayım
def uzak(la0, lo0, la, lo):
    p1, p2 = math.radians(la0), np.radians(la)
    dl = np.radians(lo - lo0)
    c = np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(dl)
    return 6371.0 * np.arccos(np.clip(c, -1, 1))


def maxc(m):
    v, c = np.unique(np.round(m, 1), return_counts=True)
    return float(v[np.argmax(c)])


def gk74(t_ms, la, lo, m):
    """Gardner–Knopoff 1974 pencereleriyle kümesizleştirme (Uhrhammer değil, özgün tablo uydurması).
    Dönüş: arka plan maskesi. En büyükten küçüğe; büyük olayın penceresindeki daha küçük olaylar bağımlı."""
    n = len(m)
    bg = np.ones(n, bool)
    if n == 0:
        return bg
    sira = np.argsort(t_ms)
    t = t_ms[sira] / GUN_MS; la, lo, m = la[sira], lo[sira], m[sira]
    d_km = 10 ** (0.1238 * m + 0.983)
    d_gun = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    for i in np.argsort(-m, kind="stable"):
        if not bg[i]:
            continue                      # bağımlı olay küme başı olmaz
        # artçılar (sonraki) ve öncüler: öncüler de aynı pencereyle atılır
        k0 = np.searchsorted(t, t[i] - d_gun[i])
        j1 = np.searchsorted(t, t[i] + d_gun[i], side="right")
        idx = np.arange(k0, j1)
        idx = idx[(idx != i) & (m[idx] <= m[i])]
        if len(idx) == 0:
            continue
        r = uzak(la[i], lo[i], la[idx], lo[idx])
        bg[idx[r <= d_km[i]]] = False
    out = np.empty(n, bool)
    out[sira] = bg
    return out


def olc(o, d):
    """Bir ana şok ve bir katalog için Mc ve sayımlar (yalnız sayı)."""
    if len(d["t"]) == 0:
        return dict(n_ind=0, mc=None)
    t = o["t"]
    r = uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
    sig = d["de"] <= DERIN_MAX + 10       # konum belirsizliği için 40 km
    ic = (r <= o["R"]) & sig
    w5 = (d["t"] >= t - SAY_YIL * YIL_MS) & (d["t"] < t)
    w3 = (d["t"] >= t - PRE_YIL * YIL_MS) & (d["t"] < t)
    w10 = d["t"] < t - PRE_YIL * YIL_MS
    m5 = d["m"][ic & w5]
    res = dict(n_ind=int(len(d["t"])), n_R_5y_tum=int(m5.size))
    if m5.size >= 50:
        mc, kural = maxc(m5) + 0.2, "MAXC+0,2 (5 y, R)"
    elif m5.size >= 20:
        mc, kural = maxc(m5) + 0.3, "MAXC+0,3 (<50)"
    else:
        res.update(mc=None, mc_kural=f"yetersiz ({m5.size})")
        return res
    res.update(mc=round(mc, 2), mc_kural=kural)
    bg = gk74(d["t"], d["la"], d["lo"], d["m"])  # bütün indirilen daire (R_ind) üzerinde
    for etik, mcx in (("mc", mc), ("mc05", mc + 0.5), ("m30", max(mc, 3.0)), ("m40", max(mc, 4.0)),
                      ("m45", max(mc, 4.5))):
        ust = d["m"] >= mcx - 1e-6
        res[f"N5_{etik}"] = int((ic & w5 & ust).sum())
        res[f"N5bg_{etik}"] = int((ic & w5 & ust & bg).sum())
        res[f"N3bg_{etik}"] = int((ic & w3 & ust & bg).sum())
        res[f"N3_{etik}"] = int((ic & w3 & ust).sum())
        res[f"Nrefbg_{etik}"] = int((ic & w10 & ust & bg).sum())
        res[f"mc_gecerli_{etik}"] = bool(mcx >= mc - 1e-6)
    # Mc zamanla değişiyor mu: önceki 5 yılın (t-10..t-5) MAXC'ı
    m_eski = d["m"][ic & (d["t"] < t - SAY_YIL * YIL_MS)]
    res["mc_eski5"] = round(maxc(m_eski) + 0.2, 2) if m_eski.size >= 50 else None
    return res


def say(ham, tr2ham, cikti):
    A, st = ana_soklar(ham, tr2ham)
    H = havuz_oku(ham)
    Ht = np.array([h[0] for h in H], float)
    Hla = np.array([h[1] for h in H])
    Hlo = np.array([h[2] for h in H])
    Hm_all = np.array([h[3] for h in H])
    satir = []
    for o in A:
        z = dict(o)
        z["tr_marmara"] = 39.5 <= o["enlem"] <= 42.0 and 26.0 <= o["boylam"] <= 31.5
        z["kataloglar"] = {}
        for srv in ("ComCat", "ISC", "GeoNet", "INGV", "EMSC"):
            fn = os.path.join(ham, f"kat_{srv}_{o['id']}.npz")
            if os.path.exists(fn):
                d = dict(np.load(fn))
                z["kataloglar"][srv] = olc(o, d)
        satir.append(z)
    # arka plan payı (GK74), ComCat tam sayımlarından: ornek tahminlerinde kullanılır
    oran = [c["N3bg_mc"] / c["N3_mc"] for z in satir for c in [z["kataloglar"].get("ComCat", {})]
            if c.get("N3_mc", 0) >= 30]
    f_bg = float(np.median(oran)) if oran else 0.6
    for z in satir:
        o = z
        for srv in ("ISC", "EMSC", "INGV", "GeoNet"):
            fn = os.path.join(ham, f"orn_{srv}_{o['id']}.npz")
            if os.path.exists(fn):
                z["kataloglar"][srv + "_ornek"] = ornek_olc(o, dict(np.load(fn)), f_bg)
        for srv in ("ISC", "GeoNet", "EMSC", "INGV"):
            fn = os.path.join(ham, f"tam3_{srv}_{o['id']}.npz")
            if os.path.exists(fn):
                z["kataloglar"][srv + "_tam3"] = tam3_olc(o, dict(np.load(fn)))
        # öncelik: tam sayım (ComCat 10 y, *_tam3); tam sayımı olmayan katalog için örnekten tahmin
        tamlar = {k: v for k, v in z["kataloglar"].items() if not k.endswith("_ornek")}
        ornekler = {k: v for k, v in z["kataloglar"].items() if k.endswith("_ornek")
                    and k.replace("_ornek", "_tam3") not in z["kataloglar"]}
        havuz = {**tamlar, **ornekler}
        en = max(havuz.items(), key=lambda kv: kv[1].get("N3bg_mc", 0) or 0, default=(None, {}))
        z["en_iyi"] = en[0]
        z["N3bg_en_iyi"] = {e: (en[1].get(f"N3bg_{e}", 0) or 0) if en[0] else 0
                            for e in ("mc", "mc05", "m30", "m40", "m45")}
        z["N3bg_en_iyi_herhangi"] = {e: max([(c.get(f"N3bg_{e}", 0) or 0) for c in havuz.values()] or [0])
                                     for e in ("mc", "mc05", "m30", "m40", "m45")}
        z["mc_en_iyi"] = en[1].get("mc") if en[0] else None
        # referans dönemi [t-10y, t-3y): ComCat tam (Nrefbg); *_tam3 için örnek pencereden tahmin (merkez t-6,5 y)
        z["ref"] = None
        if en[0] == "ComCat":
            c = en[1]
            z["ref"] = dict(tur="tam", mc_ref=c.get("mc_eski5"), Nrefbg_mc=c.get("Nrefbg_mc"),
                            Nrefbg_mc05=c.get("Nrefbg_mc05"))
        elif en[0] and en[0].endswith("_tam3"):
            srv = en[0][:-5]
            fn = os.path.join(ham, f"ref_{srv}_{o['id']}.npz")
            if os.path.exists(fn):
                d = dict(np.load(fn))
                r = uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
                m = d["m"][(r <= o["R"]) & (d["de"] <= DERIN_MAX + 10)]
                olcek = 7 * 365.25 / ORNEK_G
                mc = en[1]["mc"]
                z["ref"] = dict(tur="örnekten tahmin", n_ornek=int(m.size),
                                mc_ref=round(maxc(m) + 0.2, 2) if m.size >= 50 else
                                (round(maxc(m) + 0.3, 2) if m.size >= 20 else None),
                                Nrefbg_mc=round(float((m >= mc - 1e-6).sum()) * olcek * f_bg, 1),
                                Nrefbg_mc05=round(float((m >= mc + 0.5 - 1e-6).sum()) * olcek * f_bg, 1))
        # depremsiz kontrol pencereleri (havuzdan): bitişi t_c = t - 6k y (k = 1..), [t_c-3y, t_c+3y] içinde
        # dairede M >= 5,5 yok, t_c - 10 y >= 1975
        kontrol = 0
        yakin = Ht[uzak(o["enlem"], o["boylam"], Hla, Hlo) <= o["R"]]
        for k in range(1, 8):
            tc = o["t"] - 6 * k * YIL_MS
            if tc - ONCE_YIL * YIL_MS < calendar.timegm((1975, 1, 1, 0, 0, 0)) * 1000:
                break
            kontrol += not np.any((yakin >= tc - PRE_YIL * YIL_MS) & (yakin <= tc + 3 * YIL_MS))
        z["kontrol_pencere_havuz"] = kontrol
        # önce-pencere kirliliği: [t-4y, t-2g] içinde dairede M >= 6,0 (havuz) — artçı dizisi pencereye taşar
        Hm = Hm_all[uzak(o["enlem"], o["boylam"], Hla, Hlo) <= o["R"]]
        z["oncu_M6_kirli"] = bool(np.any((yakin >= o["t"] - 4 * YIL_MS) & (yakin <= o["t"] - 2 * GUN_MS)
                                         & (Hm >= 6.0)))
    # bağımsız kümeler: daireler örtüşür (uzaklık <= R_i + R_j) ve |Δt| <= 10 y (önce-pencereler örtüşür)
    n = len(satir)
    ana = list(range(n))

    def bul(i):
        while ana[i] != i:
            ana[i] = ana[ana[i]]
            i = ana[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if abs(satir[j]["t"] - satir[i]["t"]) > ONCE_YIL * YIL_MS:
                continue
            dd = T2.mesafe_az(satir[i]["enlem"], satir[i]["boylam"], satir[j]["enlem"], satir[j]["boylam"])[0]
            if dd <= satir[i]["R"] + satir[j]["R"]:
                ana[bul(i)] = bul(j)
    for i, z in enumerate(satir):
        z["kume"] = bul(i)
    json.dump(dict(istat=st, f_bg=f_bg, satir=satir), open(cikti, "w"), indent=0, default=float)
    print("ana şok", len(satir), "küme", len({z['kume'] for z in satir}), st)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "anasok":
        anasok(a[1], a[2])
    elif a[0] == "katalog":
        katalog(a[1], a[2], a[3] if len(a) > 3 else "ComCat",
                open(a[4]).read().split() if len(a) > 4 else None)
    elif a[0] == "ornek":
        ornek(a[1], a[2], a[3], open(a[4]).read().split())
    elif a[0] == "ref_ornek":   # referans dönemi [t-10y, t-3y) için örnek: merkez t - 6,5 y
        ornek(a[1], a[2], a[3], open(a[4]).read().split(), merkez_y=6.5, onek="ref")
    elif a[0] == "tam3":
        tam3(a[1], a[2], a[3], a[4])
    elif a[0] == "say":
        say(a[1], a[2], a[3])
    else:
        print(__doc__)
