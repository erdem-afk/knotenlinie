#!/usr/bin/env python3
"""TR-10 hedef sayımı (kör): sünme serisi olan fay kesimlerinin yakınındaki M>=5,5 ve M>=6 olaylar,
olaydan önce >= 5 yıl kayıt şartıyla.

SINAV KOŞULMAZ. Hiçbir sünme serisinin İÇERİĞİ okunmaz (USGS arşivinden yalnız istasyon listesi sayfası alınır).
Yalnız şunlar yazılır: (seri, olay) çiftinin uzaklık, zaman ve kayıt uzunluğu şartlarını sağlayıp sağlamadığı,
bağımsız küme sayısı K.

KÖRLÜK: bütün ComCat sorgularının bitişi 2025-12-31T23:59:59 (tr2_sayim.sorgu assert eder). Marmara GNSS
2017+ hiçbir yerde indirilmez (VE-1 için kör); Marmara serisi tabloda yalnız akustik/InSAR üstverisi olarak durur.

Kullanım (depo kökünden):
  python3 -I -B kayit/turetme/tr10/tr10_sayim.py say <tr10_ham_dizin> <cikti.json> [<tr2_ham_dizin>]
  python3 -I -B kayit/turetme/tr10/tr10_sayim.py guc
"""
import csv
import html
import json
import math
import os
import re
import sys
import time
import urllib.request

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "tr2"))
sys.path.insert(0, os.path.join(KOK, "tr9"))
import tr2_sayim as T2  # noqa: E402
import tr9_sayim as T9  # noqa: E402  (KESIMLER, iz_izdusum)

USGS_SAYFA = "https://earthquake.usgs.gov/monitoring/deformation/data/download.php"
ONCE_YIL = 5.0                 # olaydan önce en az 5 yıl kayıt
UZAK_KM = (30.0, 50.0)
M_ESIK = (5.5, 6.0)
DERIN_MAX = 30.0
KUME_KM, KUME_GUN = 300.0, 365.25

# Literatürden sünme serileri (USGS K. Kaliforniya sünme ölçerleri ayrıca sayfadan okunur).
# kesim: tr9_sayim.KESIMLER anahtarı (seri kesim izi boyunca sayılır). bas/bit: serinin kapsadığı yıllar
# (özetten; "~" işaretli olanlar özetten doğrulanamadı). acik: sayısal seri açık veri mi.
# surekli: yıl ölçekli hız değişimini ölçebilecek kadar sık/sürekli mi (False: seyrek ya da boşluklu).
SERILER = [
    dict(ad="Ismetpasa_duvar+surunme_olcer", kesim="KAF_Ismetpasa", tur="sünme ölçer/duvar", bas=1957.0, bit=2016.9,
         doi="10.1002/2016jb013394", acik="hayir", surekli=False, nokta=(40.87, 32.60)),
    dict(ad="Ismetpasa_InSAR_ERS-Envisat-ALOS", kesim="KAF_Ismetpasa", tur="InSAR", bas=1992.5, bit=2010.9,
         doi="10.1016/j.epsl.2005.06.044; 10.1002/2014gc005307; 10.1029/2012jb009661", acik="hayir", surekli=False),
    dict(ad="Chihshang_surunme_olcer", kesim="Longitudinal_Valley", tur="sünme ölçer", bas=1998.0, bit=2025.99,
         doi="10.1016/j.crte.2005.04.018", acik="bilinmiyor", surekli=True, not_="bitiş doğrulanamadı",
         nokta=(23.12, 121.22)),
    dict(ad="Xianshuihe_InSAR_S1", kesim="Xianshuihe", tur="InSAR", bas=2014.8, bit=2021.99,
         doi="10.1093/gji/ggae310", acik="hayir", surekli=True),
    # Aceh: iki ayrı dönem (2007-2010 ALOS, 2017-2023 S1; özetten), arası boşluk; her dönem ayrı seri sayılır.
    dict(ad="Aceh_InSAR_ALOS", kesim="Sumatra_Aceh", tur="InSAR", bas=2007.0, bit=2010.99,
         doi="10.1038/s43247-026-03951-9", acik="bilinmiyor", surekli=True),
    dict(ad="Aceh_InSAR_S1", kesim="Sumatra_Aceh", tur="InSAR", bas=2017.0, bit=2023.99,
         doi="10.1038/s43247-026-03951-9", acik="bilinmiyor", surekli=True),
    dict(ad="Leyte_InSAR_ALOS", kesim="Filipin_Leyte", tur="InSAR", bas=2006.8, bit=2011.1,
         doi="10.1186/s40623-019-1096-5", acik="bilinmiyor", surekli=True),
    dict(ad="El_Pilar_InSAR_ALOS", kesim="El_Pilar", tur="InSAR", bas=2007.0, bit=2011.99,
         doi="10.1002/2016jb013121", acik="bilinmiyor", surekli=True),
    dict(ad="Chaman_InSAR_S1", kesim="Chaman", tur="InSAR", bas=2014.0, bit=2019.99,
         doi="10.1029/2021jb021935", acik="evet (Zenodo 10.5281/zenodo.5221208)", surekli=True),
    dict(ad="Izmit_InSAR_FLATSIM", kesim="KAF_Izmit_postsismik", tur="InSAR", bas=2016.0, bit=2021.99,
         doi="10.1016/j.epsl.2024.119104", acik="bilinmiyor", surekli=True),
    dict(ad="Marmara_Kumburgaz_akustik", kesim="KAF_Marmara_CMF", tur="akustik", bas=2017.4, bit=2019.3,
         doi="10.1029/2018gl080984", acik="kismen", surekli=True),
    # Küresel Sentinel-1 (LiCSAR açık ürünleri, 2014 sonu/2015+) her sünen kesim için olası seri: üst sınır sayımı.
] + [dict(ad=f"LiCSAR_S1_{k}", kesim=k, tur="InSAR (LiCSAR, işlenmemiş)", bas=2015.0, bit=2025.99,
          doi="(COMET LiCSAR açık ürün)", acik="evet (ham interferogram; sünme serisi türetilmeli)", surekli=True,
          licsar=True) for k in T9.KESIMLER if k != "KAF_Marmara_CMF"]  # Marmara izi deniz altında: InSAR görmez


def yil(ms):
    return 1970 + ms / T2.YIL_MS


def _ctx():
    return T2.CTX


# ---------------------------------------------------------------- USGS sünme ölçer listesi
def usgs_istasyonlar(ham):
    fn = os.path.join(ham, "usgs_download.html")
    if not os.path.exists(fn):
        with urllib.request.urlopen(USGS_SAYFA, context=_ctx(), timeout=60) as r:
            open(fn, "wb").write(r.read())
    t = open(fn, encoding="utf-8", errors="replace").read()
    txt = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
    i, j = txt.find("Name Code Latitude Longitude Initial obs."), txt.find("Dilatometer")
    blok = txt[i:j]
    ay = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.?"
    pat = re.compile(r"([A-Z0-9]{3,4}) (-?\d+\.\d+) (-?\d+\.\d+) ((?:" + ay + r"[- ]?\d{2,4})|\d{4})")
    fay = None
    out = []
    for m in pat.finditer(blok):
        onceki = blok[:m.start()]
        fay =max(("Calaveras Fault", "Hayward Fault", "San Andreas Fault"), key=lambda f: onceki.rfind(f))
        kod, la, lo, ilk = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
        y = re.findall(r"\d{2,4}", ilk)[-1]
        y = int(y) if len(y) == 4 else (1900 + int(y) if int(y) > 30 else 2000 + int(y))
        out.append(dict(kod=kod, lat=la, lon=lo, bas=float(y), fay=fay))
    # SJN1 boylamı sayfada 0.0000; aynı yerdeki XSJ2 boylamı kullanılır (yalnız uzaklık için).
    for s in out:
        if s["lon"] == 0.0:
            s["lon"] = next(x["lon"] for x in out if x["kod"] == "XSJ2")
            s["not"] = "boylam sayfada 0; XSJ2'den"
    return out


# ---------------------------------------------------------------- ComCat
def olaylar(ham):
    fn = os.path.join(ham, "olay_m55.json")
    if os.path.exists(fn):
        return json.load(open(fn))
    kutular = {}
    for k, v in T9.KESIMLER.items():
        la = [p[0] for p in v["iz"]]; lo = [p[1] for p in v["iz"]]
        kutular[k] = (min(la) - 0.6, max(la) + 0.6, min(lo) - 0.7, max(lo) + 0.7)
    gor, out = set(), []
    for k, (a0, a1, o0, o1) in kutular.items():
        t = T2.sorgu({"format": "csv", "starttime": "1957-01-01", "endtime": T2.BITIS, "minmagnitude": 5.5,
                      "maxdepth": DERIN_MAX, "minlatitude": a0, "maxlatitude": a1, "minlongitude": o0,
                      "maxlongitude": o1, "orderby": "time-asc", "limit": 20000})
        for r in csv.DictReader(t.splitlines()):
            if r["id"] in gor or r["type"] != "earthquake":
                continue
            gor.add(r["id"])
            ms = T2._ms(r["time"])
            assert ms <= T2.BITIS_MS
            out.append(dict(id=r["id"], t=ms, lat=float(r["latitude"]), lon=float(r["longitude"]),
                            m=float(r["mag"]), mt=r["magType"], yer=r["place"]))
    json.dump(out, open(fn, "w"))
    return out


# ---------------------------------------------------------------- sayım
def say(ham, cikti, ham2=None):
    """ham2 verilirse (TR-2 anlık görüntüsü) M>=6 olaylar için doğrultu atımlı alt küme de sayılır."""
    os.makedirs(ham, exist_ok=True)
    SS = {b["id"] for b in T2.birincil_sec(ham2)} if ham2 else None
    ist = usgs_istasyonlar(ham)
    E = olaylar(ham)
    cift = []
    # (a) USGS sünme ölçerleri: istasyon noktasına uzaklık; seri sonu 2025 kabul (içerik bakılmadı).
    for e in E:
        for s in ist:
            d = T2.mesafe_az(s["lat"], s["lon"], e["lat"], e["lon"])[0]
            if d <= max(UZAK_KM) and yil(e["t"]) - s["bas"] >= ONCE_YIL:
                cift.append(dict(seri="USGS_" + s["kod"], kaynak="USGS", e=e, d=d, licsar=False))
    # (b) literatür serileri ve LiCSAR üst sınırı: kesim izine uzaklık; olay seri içinde ve öncesinde >= 5 yıl
    for e in E:
        ey = yil(e["t"])
        for s in SERILER:
            if "nokta" in s:   # nokta ölçer: istasyona uzaklık
                d = T2.mesafe_az(s["nokta"][0], s["nokta"][1], e["lat"], e["lon"])[0]
            else:              # alan serisi (InSAR): kesim izine uzaklık
                d = T9.iz_izdusum(T9.KESIMLER[s["kesim"]]["iz"], e["lat"], e["lon"])[0]
            if d <= max(UZAK_KM) and ey - s["bas"] >= ONCE_YIL and ey <= s["bit"] + 0.01:
                cift.append(dict(seri=s["ad"], kaynak="LiCSAR" if s.get("licsar") else "literatur", e=e, d=d,
                                 licsar=bool(s.get("licsar")), surekli=s["surekli"]))
    # olay düzeyinde topla
    def topla(filtre):
        ol = {}
        for c in cift:
            if filtre(c):
                ol.setdefault(c["e"]["id"], c["e"])
        return list(ol.values())

    def kume(evs):
        evs = sorted(evs, key=lambda e: e["t"])
        ana = list(range(len(evs)))

        def bul(i):
            while ana[i] != i:
                ana[i] = ana[ana[i]]; i = ana[i]
            return i
        for i in range(len(evs)):
            for j in range(i + 1, len(evs)):
                if evs[j]["t"] - evs[i]["t"] > KUME_GUN * T2.GUN_MS:
                    break
                if T2.mesafe_az(evs[i]["lat"], evs[i]["lon"], evs[j]["lat"], evs[j]["lon"])[0] <= KUME_KM:
                    ana[bul(i)] = bul(j)
        return len({bul(i) for i in range(len(evs))})

    tablo = {}
    for kay, f0 in (("USGS_surunme_olcer", lambda c: c["kaynak"] == "USGS"),
                    ("literatur_serileri", lambda c: c["kaynak"] == "literatur"),
                    ("literatur_surekli", lambda c: c["kaynak"] == "literatur" and c["surekli"]),
                    ("USGS+literatur", lambda c: c["kaynak"] in ("USGS", "literatur")),
                    ("LiCSAR_ust_sinir", lambda c: c["kaynak"] == "LiCSAR"),
                    ("hepsi", lambda c: True)):
        for R in UZAK_KM:
            for M in M_ESIK:
                evs = topla(lambda c, f0=f0, R=R, M=M: f0(c) and c["d"] <= R and c["e"]["m"] >= M)
                tablo[f"{kay}|R{int(R)}|M{M}"] = {"N": len(evs), "K": kume(evs)}
                if SS is not None and M >= 6.0:
                    ss = [e for e in evs if e["id"] in SS]
                    tablo[f"{kay}|R{int(R)}|M{M}|dogrultu_atimli_Mw"] = {"N": len(ss), "K": kume(ss)}
    # ayrıntı: USGS+literatür, 50 km, M>=5,5 olay listesi
    ayr = {}
    for c in cift:
        if c["kaynak"] in ("USGS", "literatur") and c["e"]["m"] >= 5.5:
            z = ayr.setdefault(c["e"]["id"], {"tarih": time.strftime("%Y-%m-%d", time.gmtime(c["e"]["t"] / 1000)),
                                              "m": c["e"]["m"], "mt": c["e"]["mt"], "yer": c["e"]["yer"],
                                              "seriler": {}})
            z["seriler"][c["seri"]] = round(min(c["d"], z["seriler"].get(c["seri"], 1e9)), 1)
    lic = {}
    for c in cift:
        if c["kaynak"] == "LiCSAR" and c["e"]["m"] >= 5.5 and c["d"] <= 50:
            lic[c["e"]["id"]] = {"tarih": time.strftime("%Y-%m-%d", time.gmtime(c["e"]["t"] / 1000)),
                                 "m": c["e"]["m"], "yer": c["e"]["yer"], "seri": c["seri"], "d": round(c["d"], 1)}
    ozet = {"usgs_istasyon_N": len(ist), "usgs_istasyon_ilk_yil_aralik": [min(s["bas"] for s in ist),
                                                                          max(s["bas"] for s in ist)],
            "olay_havuzu_M55_N": len(E), "sayim": tablo}
    json.dump({"ozet": ozet, "usgs_istasyonlar": ist, "usgs_lit_olaylar": ayr, "licsar_olaylar": lic},
              open(cikti, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    for k, z in sorted(ayr.items(), key=lambda kv: kv[1]["tarih"]):
        print(z["tarih"], k, z["m"], z["mt"], z["yer"], sorted(z["seriler"].items(), key=lambda kv: kv[1])[:3])
    print("LiCSAR üst sınır olayları (50 km, M>=5,5):")
    for k, z in sorted(lic.items(), key=lambda kv: kv[1]["tarih"]):
        print(z["tarih"], k, z["m"], z["yer"], z["seri"], z["d"])


def guc():
    """Olay başına sıra ölçüsü r = (olay öncesi sünme hızı değişiminin olaysız pencereler içindeki sırası).
    H0: r ~ U(0,1). H1: r ~ Beta(a,1). Ortalama r için tek yanlı test, α 0,05; ayrıca ikili 'üst %10'da mı'."""
    print("K | güç a=0,4 / 0,5 / 0,7 (sıra ölçüsü) | ikili (p0 0,10): kritik, güç p1=0,3 / 0,4")
    for K in (3, 5, 8, 10, 12, 15, 20, 30):
        row = []
        for a in (0.4, 0.5, 0.7):
            m1 = a / (a + 1); v1 = a / ((a + 1) ** 2 * (a + 2)); s0 = math.sqrt(1 / 12)
            z = (0.5 - m1) / math.sqrt(v1 / K) - 1.645 * s0 / math.sqrt(v1)
            row.append(round(0.5 * (1 + math.erf(z / math.sqrt(2))), 2))
        c = next(c for c in range(K + 2) if T9.binom_kuyruk(K, c, 0.10) <= 0.05)
        print(K, row, c, round(T9.binom_kuyruk(K, c, 0.3), 2), round(T9.binom_kuyruk(K, c, 0.4), 2))


if __name__ == "__main__":
    if sys.argv[1] == "say":
        say(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif sys.argv[1] == "guc":
        guc()
