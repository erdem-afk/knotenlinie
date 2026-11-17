#!/usr/bin/env python3
"""TR-13d 0 € KATALOG VARLIĞI SAYIMI: TR-13'te düşen adaylar açık bölgesel kataloglarla §3.1–3.3'ü geçer mi (yalnız SAYI).

Kural: kayit/onkayit/TR-13d_SAYIM-KURALI.md (sayımdan önce commit edildi, 8a99970).
Gerçek katalogda hiçbir yerelleşme ölçüsü (V(q), Gini, z) HESAPLANMAZ. tr13b_kosu.kos() ÇAĞRILMAZ; yalnız
tr13b_kosu.hazirla (değiştirilmeden) içe aktarılır; döndürdüğü arka plan konumları hemen atılır.

KÖRLÜK (kod uygular): her indirme parçasının bitişi < ana şok t ve <= 2025-12-31T23:59:59; zamanı >= 2026-01-01 ya da
>= t olan satır okunurken atılır. Ana şok sonrası pencere istenmez.

Kullanım:
  python3 -I -B tr13d_sayim.py say <aday.json> <sayim4.json> <ham_dizin/> <cikti.json> [katalog ...]
Kataloglar: JMA NRCan KOERI AUTH INGV IMO GeoNet NNSN CSN
"""
import calendar
import collections
import hashlib
import html
import io
import json
import math
import os
import re
import sys
import time
import urllib.parse
import zipfile

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BURA, "..", "tr13b"))
sys.path.insert(0, os.path.join(BURA, "..", "tr13"))
import tr13b_kosu as K  # noqa: E402
import tr13_sayim as T  # noqa: E402

YIL = T.YIL_MS
GUN = T.GUN_MS
BITIS_MS = T.BITIS_MS
TR13B_KUME = {397, 160, 303, 395, 1141, 689, 727, 802, 901, 942, 979, 1139, 1035, 1144}
TR13C_KUME = {847, 854, 910, 911, 1137}
BEKLE = 0.4                      # istekler arası (s); 429'da T.getir üstel bekler

# bölge -> denenecek katalog sırası (kural §2)
BOLGE_KATALOG = {
    "Japonya": ["JMA"],
    "Tayvan": ["CWA", "JMA"],
    "Kanada (BC)": ["NRCan"],
    "Türkiye": ["AFAD", "KOERI"],
    "Yunanistan-Ege": ["NOA", "AUTH"],
    "İtalya-Adriyatik": ["INGV"],
    "İzlanda": ["IMO"],
    "İran-Kafkas": ["IRSC"],
    "Yeni Zelanda": ["GeoNet"],
    "Svalbard-Jan Mayen": ["NNSN"],
    "Şili-Arjantin": ["CSN"],
    "Kuzey And": ["SGC"],
    "Meksika": ["SSN"],
}
COMCAT_ZATEN = {"Kaliforniya", "ABD iç batı", "Alaska"}
# Erişim denemesinin sonucu (sayımdan sonra, 17 Kasım 2026; ayrıntı rapor ve erisim.json):
ERISILEMEZ = {
    "CWA": "GDMS katalog indirme oturum açma ister (kayıt); www.cwa.gov.tw bağlantı sıfırlandı. Başvurulmadı.",
    "AFAD": "apiv2/event/filter her sorguya (2015, 2019, 2023-02-06, 2025) boş liste [] dönüyor: makine erişimi işlevsiz.",
    "IRSC": "irsc.ut.ac.ir: https bağlantı sıfırlandı, http 503 (upstream connect timeout).",
    "SGC": "sismo.sgc.gov.co:8080 bağlanamadı (port kapalı/erişilemez); https:443 fdsnws yolu 404.",
    "SSN": "www.ssn.unam.mx bağlantı sıfırlandı; www2.ssn.unam.mx:8080 bağlanamadı.",
}
# Kapsam başlangıcı (katalog bu tarihten önce boş): NOA FDSN 2011-06'dan önce boş (2010-01..2011-01 sorguları 0 satır).
KAPSAM_BASI = {"NOA": calendar.timegm((2011, 6, 1, 0, 0, 0)) * 1000,
               "AUTH": calendar.timegm((1995, 1, 1, 0, 0, 0)) * 1000,
               "IMO": calendar.timegm((1991, 1, 7, 0, 0, 0)) * 1000}


class Yok(Exception):
    """Bu parça için veri alınamadı (403/404 sayfa, erişim yok)."""


def iso(ms):
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000))


def bos():
    return dict(t=np.zeros(0), la=np.zeros(0), lo=np.zeros(0), de=np.zeros(0), m=np.zeros(0))


def diz(t, la, lo, de, m):
    return dict(t=np.array(t, float), la=np.array(la, float), lo=np.array(lo, float), de=np.array(de, float),
                m=np.array(m, float))


def kor(d, t_ust):
    """Körlük: t >= min(t_ana, 2026) satırları at."""
    k = (d["t"] < min(t_ust, T.KOR_MS))
    return {a: v[k] for a, v in d.items()}


def getir(url, onb):
    time.sleep(BEKLE)
    return T.getir(url, onb, zaman_asimi=300)


def bitis_denetle(t1):
    assert t1 <= BITIS_MS + 1000, "KÖRLÜK: bitiş 2025-12-31 sonrası"


# ------------------------------------------------------------------ FDSN text (başlık adlarıyla)
def fdsn_oku(metin, mag_say):
    t, la, lo, de, m = [], [], [], [], []
    bas = None
    for s in metin.splitlines():
        if s.startswith("#"):
            bas = [x.strip().lower() for x in s[1:].split("|")]
            continue
        if not s.strip() or bas is None:
            continue
        a = [x.strip() for x in s.split("|")]
        r = dict(zip(bas, a))
        try:
            tt = T.ms_of(r["time"])
            mm = float(r["magnitude"])
            y, x = float(r["latitude"]), float(r["longitude"])
        except (KeyError, ValueError):
            continue
        if r.get("eventtype", "earthquake") not in ("", "earthquake"):
            continue
        dd = r.get("depth/km") or r.get("depth") or ""
        try:
            dd = float(dd)
        except ValueError:
            dd = 0.0
        t.append(tt); la.append(y); lo.append(x); de.append(dd); m.append(mm)
        mag_say[r.get("magtype", "?")] += 1
    return diz(t, la, lo, de, m)


FDSN = {
    "NRCan": "https://earthquakescanada.nrcan.gc.ca/fdsnws/event/1/query",
    "GeoNet": "https://service.geonet.org.nz/fdsnws/event/1/query",
    "INGV": "https://webservices.ingv.it/fdsnws/event/1/query",
    "NNSN": "https://nnsn.geo.uib.no/nnsn_eqcat/fdsnws/event/1/query",
}


def fdsn_parca(srv, o, t0, t1, onb, mag_say, derin=0):
    bitis_denetle(t1)
    R = o["R"]
    if srv == "NNSN":                    # NNSN daire parametresini yok sayıyor: kutu + yerel daire süzgeci
        dla = R / 111.195 * 1.05
        dlo = min(179.0, dla / max(0.05, math.cos(math.radians(o["enlem"]))))
        q = dict(starttime=iso(t0), endtime=iso(t1 - 1000), minlatitude=f"{max(-90, o['enlem'] - dla):.4f}",
                 maxlatitude=f"{min(90, o['enlem'] + dla):.4f}", minlongitude=f"{o['boylam'] - dlo:.4f}",
                 maxlongitude=f"{o['boylam'] + dlo:.4f}", format="text", limit=20000)
    else:
        q = dict(starttime=iso(t0), endtime=iso(t1 - 1000), latitude=f"{o['enlem']:.4f}",
                 longitude=f"{o['boylam']:.4f}", maxradius=f"{R / 111.195:.4f}", format="text")
        if srv != "GeoNet":
            q["limit"] = 20000
    yerel = collections.Counter()
    d = fdsn_oku(getir(FDSN[srv] + "?" + urllib.parse.urlencode(q), onb), yerel)
    if len(d["t"]) >= 9000 and derin < 8:          # olası üst sınır: zamanı böl
        orta = (t0 + t1) // 2
        return T.birlestir([fdsn_parca(srv, o, t0, orta, onb, mag_say, derin + 1),
                            fdsn_parca(srv, o, orta, t1, onb, mag_say, derin + 1)])
    mag_say.update(yerel)
    return d


# ------------------------------------------------------------------ KOERI (zeqdb, daire sorgusu, HTML satırları)
KOERI = "http://www.koeri.boun.edu.tr/sismo/zeqdb/submitCrcSearchT.asp"


def koeri_parca(o, t0, t1, onb, mag_say):
    bitis_denetle(t1)
    a, b = time.gmtime(t0 / 1000), time.gmtime((t1 - 1000) / 1000)
    q = dict(bYear=a.tm_year, bMont=f"{a.tm_mon:02d}", bDay=f"{a.tm_mday:02d}", eYear=b.tm_year,
             eMont=f"{b.tm_mon:02d}", eDay=f"{b.tm_mday:02d}", Enlem=f"{o['enlem']:.2f}",
             Boylam=f"{o['boylam']:.2f}", Yaricap=f"{o['R']:.1f}", MAGMin="0.0", MAGMax="9.9", DerMin="0",
             DerMax="40", Tip="Deprem", ofName="liste.txt")
    metin = getir(KOERI + "?" + urllib.parse.urlencode(q), onb)
    t, la, lo, de, m = [], [], [], [], []
    for s in re.split(r"<br>", metin):
        s = re.sub(r"<[^>]*>", "", s).strip()
        a_ = s.split("\t")
        if len(a_) < 9 or not re.fullmatch(r"\d{6}", a_[0].strip()):
            continue
        try:
            tt = calendar.timegm(time.strptime(a_[2].strip() + " " + a_[3].strip()[:8], "%Y.%m.%d %H:%M:%S")) * 1000
            t.append(tt); la.append(float(a_[4])); lo.append(float(a_[5])); de.append(float(a_[6]))
            m.append(float(a_[7]))                      # xM: KOERI'nin tercih edilen büyüklüğü
        except ValueError:
            continue
    mag_say["xM (KOERI)"] += len(t)
    if len(t) >= 9000:
        raise Yok(f"KOERI parça {len(t)} satır: olası üst sınır")
    return diz(t, la, lo, de, m)


# ------------------------------------------------------------------ IMO (api.vedur.is quakes, SIL)
IMO = "https://api.vedur.is/quakes/events"


def imo_parca(o, t0, t1, onb, mag_say):
    bitis_denetle(t1)
    t0 = max(t0, KAPSAM_BASI["IMO"])
    if t0 >= t1:
        return bos()
    dla = o["R"] / 111.195 * 1.05
    dlo = dla / math.cos(math.radians(o["enlem"]))
    a, b, c, d_ = o["boylam"] - dlo, o["boylam"] + dlo, o["enlem"] - dla, o["enlem"] + dla
    poly = f"POLYGON(({a:.4f} {c:.4f}, {b:.4f} {c:.4f}, {b:.4f} {d_:.4f}, {a:.4f} {d_:.4f}, {a:.4f} {c:.4f}))"
    q = dict(start_time=iso(t0), end_time=iso(t1 - 1000), polygon=poly, system="sil", depth_max=40)
    n = int(getir(IMO + "/count?" + urllib.parse.urlencode(q), onb).strip())
    metin = getir(IMO + "?" + urllib.parse.urlencode(dict(q, format="csv")), onb)
    t, la, lo, de, m = [], [], [], [], []
    for r in __import__("csv").DictReader(io.StringIO(metin)):
        if r.get("type", "earthquake") != "earthquake":
            continue
        try:
            t.append(T.ms_of(r["time"])); la.append(float(r["latitude"])); lo.append(float(r["longitude"]))
            de.append(float(r["depth"] or 0)); m.append(float(r["magnitude"]))
        except (ValueError, KeyError):
            continue
    satir = metin.count("\n") - 1 if metin else 0
    if satir < n:
        raise Yok(f"IMO parça eksik: {satir} < sayım {n}")
    mag_say["IMO SIL (Mw ölçekli boyut)"] += len(t)
    return diz(t, la, lo, de, m)


# ------------------------------------------------------------------ CSN (günlük HTML sayfaları)
CSN = "https://www.sismologia.cl/sismicidad/catalogo/{y:04d}/{mo:02d}/{y:04d}{mo:02d}{d:02d}.html"


def csn_gun(gun_ms, onb):
    g = time.gmtime(gun_ms / 1000)
    url = CSN.format(y=g.tm_year, mo=g.tm_mon, d=g.tm_mday)
    try:
        return getir(url, onb)
    except RuntimeError as e:
        raise Yok(str(e)[:120])


def csn_parca(o, t0, t1, onb, mag_say):
    bitis_denetle(t1)
    t, la, lo, de, m = [], [], [], [], []
    g = t0 - t0 % GUN
    while g < t1:
        metin = csn_gun(g, onb)
        for blok in re.findall(r"<tr>.*?</tr>", metin, flags=re.S):
            h = [" ".join(html.unescape(re.sub(r"<[^>]*>", " ", x)).split())
                 for x in re.findall(r"<td.*?</td>", blok, re.S)]
            if len(h) < 5:
                continue
            try:
                tt = calendar.timegm(time.strptime(h[1][:19], "%Y-%m-%d %H:%M:%S")) * 1000   # UTC sütunu
                y, x = (float(v) for v in h[2].split()[:2])
                dd = float(h[3].split()[0])
                mm = float(h[4].split()[0])
            except (ValueError, IndexError):
                continue
            t.append(tt); la.append(y); lo.append(x); de.append(dd); m.append(mm)
            mag_say["CSN " + (h[4].split()[1] if len(h[4].split()) > 1 else "?")] += 1
        g += GUN
    d = diz(t, la, lo, de, m)
    k = (d["t"] >= t0) & (d["t"] < t1)
    return {a: v[k] for a, v in d.items()}


# ------------------------------------------------------------------ JMA (yıllık sabit biçim dosyaları)
JMA = "https://www.data.jma.go.jp/eqev/data/bulletin/data/hypo/{ad}.zip"
JMA_DOSYA = ["h1967"] + [f"h{y}" for y in range(1983, 1997)] + ["h199701", "h199710"] + \
    [f"h{y}" for y in range(1998, 2025)]
_JMA = {}


def jma_mag(s):
    s = s.strip()
    if not s:
        return None
    if s[0] == "-":
        return -int(s[1]) / 10.0
    if s[0] in "ABC":
        return -(1 + "ABC".index(s[0])) - int(s[1]) / 10.0
    return int(s) / 10.0


def jma_ondalik(f):
    """JMA sabit biçim: iki ondalık hane örtük; eski kayıtlarda düşük haneler boş (boş = 0). '548 ' -> 54,80."""
    return int(f.replace(" ", "0")) / 100.0


def jma_dosya(ad, ham, mag_say):
    if ad in _JMA:
        return _JMA[ad]
    npz = os.path.join(ham, "JMA", ad + ".npz")
    if os.path.exists(npz):
        with np.load(npz, allow_pickle=False) as z:
            _JMA[ad] = {k: np.asarray(z[k]) for k in z.files}
            return _JMA[ad]
    os.makedirs(os.path.join(ham, "JMA"), exist_ok=True)
    zp = os.path.join(ham, "JMA", ad + ".zip")
    if not os.path.exists(zp):
        import urllib.request
        time.sleep(BEKLE)
        req = urllib.request.Request(JMA.format(ad=ad), headers={"User-Agent": T.UA})
        with urllib.request.urlopen(req, timeout=600, context=T.CTX) as r:
            b = r.read()
        open(zp + ".tmp", "wb").write(b)
        os.replace(zp + ".tmp", zp)
    t, la, lo, de, m, tp = [], [], [], [], [], []
    with zipfile.ZipFile(zp) as z:
        for nm in z.namelist():
            for s in z.open(nm).read().decode("ascii", "replace").splitlines():
                if len(s) < 58 or s[0] != "J":
                    continue
                try:
                    sec = jma_ondalik(s[13:17])
                    tt = calendar.timegm((int(s[1:5]), int(s[5:7]), int(s[7:9]), int(s[9:11]), int(s[11:13]), 0)) \
                        * 1000 + int(round(sec * 1000))
                    y = int(s[21:24]) + jma_ondalik(s[24:28]) / 60
                    x = int(s[32:36]) + jma_ondalik(s[36:40]) / 60
                    dd = jma_ondalik(s[44:49])
                    mm = jma_mag(s[52:54])
                    tip = s[54]
                    if mm is None:
                        mm = jma_mag(s[55:57]); tip = s[57]
                    if mm is None:
                        continue
                except ValueError:
                    continue
                t.append(tt); la.append(y); lo.append(x); de.append(dd); m.append(mm); tp.append(ord(tip))
    d = diz(t, la, lo, de, m)
    d["tip"] = np.array(tp, np.int16)
    np.savez_compressed(npz, **d)
    _JMA[ad] = d
    return d


def jma_yillar(t0, t1):
    a, b = time.gmtime(t0 / 1000).tm_year, time.gmtime((t1 - 1) / 1000).tm_year
    out = []
    for ad in JMA_DOSYA:
        if ad == "h1967":
            if a <= 1982:
                out.append(ad)
        elif ad in ("h199701", "h199710"):
            if a <= 1997 <= b:
                out.append(ad)
        elif a <= int(ad[1:]) <= b:
            out.append(ad)
    return out


def jma_parca(o, t0, t1, ham, mag_say):
    bitis_denetle(t1)
    if time.gmtime((t1 - 1) / 1000).tm_year > 2024:
        raise Yok("JMA 2025 dosyası yayımlanmamış")
    ds = []
    for ad in jma_yillar(t0, t1):
        d = jma_dosya(ad, ham, mag_say)
        r = T.uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
        k = (d["t"] >= t0) & (d["t"] < t1) & (r <= o["R"])
        for c, n in zip(*np.unique(d["tip"][k], return_counts=True)):
            mag_say["JMA tür " + chr(int(c))] += int(n)
        ds.append({a: v[k] for a, v in d.items() if a != "tip"})
    return T.birlestir(ds)


# ------------------------------------------------------------------ AUTH (tek dosya, 1995+)
AUTH = "https://seismo.auth.gr/wp-content/uploads/CATALOGS/preliminary/finalcat.cat"
_AUTH = {}


def auth_tum(ham, onb):
    if "d" in _AUTH:
        return _AUTH["d"]
    metin = getir(AUTH, onb)
    t, la, lo, de, m = [], [], [], [], []
    for s in metin.splitlines():
        a = s.split()
        if len(a) < 6 or not re.fullmatch(r"\d{4}-\d\d-\d\d", a[0]):
            continue
        try:
            tt = calendar.timegm(time.strptime(a[0] + " " + a[1][:8], "%Y-%m-%d %H:%M:%S")) * 1000
            if tt >= T.KOR_MS:
                continue                 # 2026+ satır sayılmadan atılır
            t.append(tt); la.append(float(a[2])); lo.append(float(a[3])); de.append(float(a[4])); m.append(float(a[5]))
        except ValueError:
            continue
    _AUTH["d"] = diz(t, la, lo, de, m)
    return _AUTH["d"]


def auth_parca(o, t0, t1, ham, onb, mag_say):
    bitis_denetle(t1)
    d = auth_tum(ham, onb)
    r = T.uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
    k = (d["t"] >= t0) & (d["t"] < t1) & (r <= o["R"])
    mag_say["AUTH M (ML ağırlıklı)"] += int(k.sum())
    return {a: v[k] for a, v in d.items()}


# ------------------------------------------------------------------ ortak indirme
def indir(kat, o, t0, t1, ham, mag_say):
    """[t0, t1) yıllık parçalar halinde. Dönüş: (d, eksik parça sayısı)."""
    onb = os.path.join(ham, "onbellek_" + kat)
    ds, eksik = [], []
    if kat == "AUTH":
        return auth_parca(o, t0, t1, ham, onb, mag_say), eksik
    if kat == "JMA":
        try:
            return jma_parca(o, t0, t1, ham, mag_say), eksik
        except Yok as e:
            return bos(), [str(e)]
    a = t0
    while a < t1:
        b = min(t1, a + YIL)
        try:
            if kat in FDSN:
                ds.append(fdsn_parca(kat, o, a, b, onb, mag_say))
            elif kat == "KOERI":
                ds.append(koeri_parca(o, a, b, onb, mag_say))
            elif kat == "IMO":
                ds.append(imo_parca(o, a, b, onb, mag_say))
            elif kat == "CSN":
                ds.append(csn_parca(o, a, b, onb, mag_say))
            else:
                raise AssertionError(kat)
        except (Yok, RuntimeError) as e:
            eksik.append(f"{iso(a)[:10]}–{iso(b)[:10]}: {str(e)[:160]}")
            if kat == "CSN" and "403" in str(e):
                break                    # 403 aşılmaz; bu dönem için yeniden denenmez
        a = b
    return T.birlestir(ds), eksik


def mc_kural(m):
    if m.size >= 50:
        return round(T.maxc(m) + 0.2, 2)
    if m.size >= 20:
        return round(T.maxc(m) + 0.3, 2)
    return None


def say_olay(a, kat, ham, s4tr13b):
    o = dict(t=int(a["t"]), enlem=a["enlem"], boylam=a["boylam"], R=a["R"])
    t = o["t"]
    oz = dict(id=a["id"], yer=a["yer"], zaman=a["zaman"], M=a["M"], bolge=a["bolge"], kume=a["kume"], R=a["R"],
              katalog=kat, neden_tr13=a["neden"], N3bg_kuresel=a["N3bg_kuresel"], marmara=a["marmara"],
              tr13c_kumesi=a["tr13c_kumesi"])
    mag_say = collections.Counter()
    bas = KAPSAM_BASI.get(kat)
    if bas is not None and bas >= t:
        oz.update(durum=f"düşer: katalog {iso(bas)[:10]}'dan başlıyor, önce-pencere kapsanmıyor", mag=dict(mag_say))
        return oz
    t1 = min(t, BITIS_MS + 1000)
    d3, eks3 = indir(kat, o, t - 3 * YIL, t1, ham, mag_say)
    d3 = kor(d3, t)
    r3 = T.uzak(o["enlem"], o["boylam"], d3["la"], d3["lo"])
    ic3 = (r3 <= o["R"]) & (d3["de"] <= T.DERIN_MAX + 10)
    oz.update(n3_toplam=int(ic3.sum()), eksik_once=eks3)
    if eks3:
        oz.update(durum="düşer: önce-pencerede parça alınamadı (veri yok)", mag=dict(mag_say))
        return oz
    if ic3.sum() < 50:
        oz.update(durum=f"düşer: ön eleme, önce-pencerede toplam {int(ic3.sum())} < 50 olay", mag=dict(mag_say))
        return oz
    dr, eksr = indir(kat, o, t - 10 * YIL, t - 3 * YIL, ham, mag_say)
    dr = kor(dr, t)
    oz["eksik_ref"] = eksr
    d = T.birlestir([dr, d3])
    r = T.uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
    ic = (r <= o["R"]) & (d["de"] <= T.DERIN_MAX + 10)
    w3 = ic & (d["t"] >= t - 3 * YIL)
    wr = ic & (d["t"] < t - 3 * YIL)
    mc0, mcr = mc_kural(d["m"][w3]), mc_kural(d["m"][wr])
    oz.update(n_indirilen=int(len(d["t"])), n_ref_toplam=int(wr.sum()), mc_once=mc0, mc_ref=mcr,
              mag=dict(mag_say))
    if mc0 is None or mcr is None:
        oz["durum"] = "düşer: Mc kestirilemedi (< 20 olay)"
        return oz
    # bilgi: TR-13b §2 / TR-13 Ek 1 referans süzgeci (geçti tanımına girmez)
    sec = d["t"] < t - 3 * YIL
    dd = {k: v[sec] for k, v in d.items()}
    bgr = T.gk74(dd["t"], dd["la"], dd["lo"], dd["m"])
    icr = (T.uzak(o["enlem"], o["boylam"], dd["la"], dd["lo"]) <= o["R"]) & (dd["de"] <= T.DERIN_MAX + 10)
    nref0 = int((icr & bgr & (dd["m"] >= mc0 - 1e-6)).sum())
    oz.update(N_ref_bg_mc_once=nref0, s2_suzgeci=bool(mcr <= mc0 + 0.3 + 1e-9 and nref0 >= 100))
    # §3.1–3.3: tr13b_kosu.hazirla, değiştirilmeden
    s = dict(id=a["id"], yer=a["yer"], kume=a["kume"], R_km=a["R"], katalog=kat, mc_once=mc0, ref_tam=dict(mc=mcr))
    oz2, bg = K.hazirla(s, o, {k: np.asarray(v, float) for k, v in d.items()})
    del bg                                   # konumlar kullanılmaz; ölçü yok
    for k in ("mc_ortak", "mc_son", "mc_artis", "N3bg", "N_ref", "N_plasebo", "N_plasebo_ref", "ref_en_buyuk",
              "durum"):
        if k in oz2:
            oz[k] = oz2[k]
    oz["cakisma_tr13b"] = cakisma(o, s4tr13b)
    return oz


def cakisma(o, tr13b):
    out = []
    for b in tr13b:
        dkm = float(T.uzak(o["enlem"], o["boylam"], np.array([b["enlem"]]), np.array([b["boylam"]]))[0])
        dt = abs(float(o["t"]) - float(b["t"])) / YIL
        if dkm <= float(o["R"]) + float(b["R"]) and dt <= 10.0:
            out.append(dict(id=b["id"], kume=b["kume"], uzaklik_km=round(dkm, 1), dt_y=round(dt, 2)))
    return out


def say(aday_yol, s4yol, ham, cikti, kataloglar):
    ham = ham if ham.endswith("/") else ham + "/"
    os.makedirs(ham, exist_ok=True)
    A = json.load(open(aday_yol))["aday"]
    s4 = {z["id"]: z for z in json.load(open(s4yol))["satir"]}
    tr13b = [s4[s["id"]] for s in K.ana_liste(K.TAMSAYIM)]
    eski = {}
    if os.path.exists(cikti):
        eski = {(z["id"], z["katalog"]): z for z in json.load(open(cikti))["satir"]}
    sat = list(eski.values())
    for a in A:
        sira = BOLGE_KATALOG.get(a["bolge"])
        if not sira:
            continue
        kat = next((k for k in sira if k not in ERISILEMEZ and
                    not (k in KAPSAM_BASI and k == "NOA" and KAPSAM_BASI[k] > a["t"] - 10 * YIL)), None)
        if kat is None or kat not in kataloglar or (a["id"], kat) in eski:
            continue
        t0 = time.time()
        oz = say_olay(a, kat, ham, tr13b)
        oz["sure_s"] = round(time.time() - t0, 1)
        sat.append(oz)
        print(oz["id"], oz["bolge"], kat, oz["M"], oz.get("n3_toplam"), oz.get("mc_once"), oz.get("mc_ref"),
              oz.get("mc_son"), oz.get("N3bg"), oz.get("N_ref"), oz["durum"], flush=True)
        json.dump(dict(kural="kayit/onkayit/TR-13d_SAYIM-KURALI.md", satir=sat), open(cikti, "w"), indent=1,
                  ensure_ascii=False, default=float)


if __name__ == "__main__":
    if sys.argv[1] == "say":
        say(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], set(sys.argv[6:]))
