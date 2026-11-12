#!/usr/bin/env python3
"""TR-9 hedef sayımı (kör): kilitlenme/sünme haritası yayımlanmış doğrultu atımlı fay kesimlerinin
<= 50 km yakınındaki Mw 6,0-7,2 doğrultu atımlı olaylar ve artçı ucunun ölçülebilirliği.

SINAV KOŞULMAZ. Artçı ucunun KONUMU hesaplanmaz; uçtan sınıra uzaklık hiçbir yerde hesaplanmaz.
Yalnız şunlar yazılır: olay kesime yakın mı, kesimin hangi sınırı dış merkeze doğrultu boyunca en yakın
(olay öncesi bilgi), sınıra bakan yanda en az N artçı var mı (var/yok), bağımsız küme sayısı K.

KÖRLÜK: bütün ComCat sorgularının bitişi 2025-12-31T23:59:59 (tr2_sayim.sorgu assert eder).

Kullanım (depo kökünden; __pycache__ bırakmamak için -B):
  python3 -I -B kayit/turetme/tr9/tr9_sayim.py say <tr2_ham_dizin> <tr9_ham_dizin> <cikti.json>
  python3 -I -B kayit/turetme/tr9/tr9_sayim.py guc
<tr2_ham_dizin>: TR-2 ComCat anlık görüntüsü (birincil_aday*.csv, mekanizma.jsonl, artci/). Yeniden kullanılır.
<tr9_ham_dizin>: aday olaylar için M>=2,5 artçı sorguları (yeni, küçük) buraya önbelleklenir.
"""
import csv
import json
import math
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(KOK, "tr2"))
import tr2_sayim as T2  # noqa: E402  (BITIS, sorgu, birincil_sec, L_km, mesafe_az)

# --- Sayım parametreleri (TR-9_SAYIM.md §1) ---
YAKIN_KM = 50.0          # olay dış merkezi kesim izine <= 50 km
ARTCI_GUN = 30
ARTCI_R_L = 3.0
ARTCI_DIK_KM = 15.0      # artçı kesim izine dik uzaklık <= max(15 km, 0,5 L)
UC_N_TOPLAM = 10         # uç ölçülebilir: toplam >= 10 artçı ...
UC_N_YAN = 5             # ... ve sınıra bakan yanda >= 5 artçı
SINIR_ERISIM_L = 3.0     # en yakın sınır dış merkezden doğrultu boyunca <= 3 L değilse "erişim dışı" (bilgi)
KUME_KM, KUME_GUN = 300.0, 365.25
IZDE_KM = 15.0           # "iz üstünde" (bilgi): dış merkez kesim izine <= 15 km

# --- Kesim tablosu ---
# iz: yaklaşık fay izi (enlem, boylam), kuzey/batı ucundan; köşeler literatürdeki yer adlarından elle yazıldı,
#     SAYISALLAŞTIRILMADI, konum belirsizliği kabaca ±10 km. 50 km tampon için yeterli, sınav için değil.
# sinir: izin üzerindeki kilitli<->sünen geçiş noktaları (yaklaşık). Sınav için yayımlanmış sayısal haritadan
#        yeniden okunmalı (TR-9_SAYIM.md §1.2).
# kaynak: kilitlenme/sünme haritasının DOI'si (OpenAlex ile doğrulandı, TR-9_SAYIM.md §2.1).
# acik_veri: sayısal harita açık veri olarak bulundu mu ("evet", "hayir", "bilinmiyor").
KESIMLER = {
    "SAF_sunen": dict(iz=[(36.85, -121.54), (36.60, -121.20), (36.20, -120.80), (35.90, -120.43), (35.73, -120.29)],
                      sinir=[(36.85, -121.54), (35.82, -120.35)], kaynak="10.1002/2013jb010741", acik_veri="bilinmiyor"),
    "Hayward": dict(iz=[(38.00, -122.36), (37.84, -122.23), (37.67, -122.08), (37.53, -121.95), (37.43, -121.85)],
                    sinir=[(38.00, -122.36), (37.43, -121.85)], kaynak="10.1002/2015jb012230", acik_veri="bilinmiyor"),
    "Rodgers_Creek": dict(iz=[(38.06, -122.33), (38.30, -122.55), (38.55, -122.80)],
                          sinir=[(38.06, -122.33), (38.55, -122.80)], kaynak="10.3133/ofr20131165", acik_veri="evet"),
    "Calaveras": dict(iz=[(36.80, -121.37), (36.97, -121.47), (37.10, -121.52), (37.30, -121.68), (37.45, -121.80),
                          (37.75, -121.95)],
                      sinir=[(37.45, -121.80)], kaynak="10.1002/2015jb012230", acik_veri="bilinmiyor"),
    "Concord_GV": dict(iz=[(37.92, -122.03), (38.10, -122.10), (38.40, -122.20)],
                       sinir=[(37.92, -122.03), (38.40, -122.20)], kaynak="10.3133/ofr20131165", acik_veri="evet"),
    "Maacama": dict(iz=[(38.70, -122.75), (39.15, -123.20), (39.45, -123.35)],
                    sinir=[(38.70, -122.75), (39.45, -123.35)], kaynak="10.3133/ofr20131165", acik_veri="evet"),
    "Imperial": dict(iz=[(32.97, -115.52), (32.80, -115.42), (32.67, -115.33)],
                     sinir=[(32.80, -115.42)], kaynak="10.1002/2015jb012516", acik_veri="bilinmiyor"),
    "Superstition_Hills": dict(iz=[(33.08, -115.83), (32.97, -115.72), (32.92, -115.68)],
                               sinir=[(33.08, -115.83), (32.92, -115.68)], kaynak="10.1029/2008jb006135",
                               acik_veri="bilinmiyor"),
    "SSAF_Coachella": dict(iz=[(33.95, -116.40), (33.70, -116.10), (33.35, -115.70)],
                           sinir=[(33.95, -116.40)], kaynak="10.1029/2026jb034392", acik_veri="bilinmiyor"),
    "KAF_Ismetpasa": dict(iz=[(40.80, 32.10), (40.87, 32.60), (40.93, 33.10)],
                          sinir=[(40.80, 32.10), (40.93, 33.10)], kaynak="10.1029/2012jb009661", acik_veri="bilinmiyor"),
    "KAF_Izmit_postsismik": dict(iz=[(40.73, 29.70), (40.72, 30.00), (40.70, 30.30)],
                                 sinir=[(40.73, 29.70), (40.70, 30.30)], kaynak="10.1002/2015jb012737",
                                 acik_veri="bilinmiyor"),
    "KAF_Marmara_CMF": dict(iz=[(40.80, 27.70), (40.85, 28.00), (40.87, 28.30), (40.85, 28.60)],
                            sinir=[(40.87, 28.30), (40.85, 28.60)], kaynak="10.1029/2018gl080984",
                            acik_veri="kismen (akustik ham veri SEANOE/PANGAEA)"),
    "DAF_Puturge": dict(iz=[(38.70, 39.90), (38.48, 39.45), (38.40, 39.20), (38.20, 38.80), (38.02, 38.40)],
                        sinir=[(38.48, 39.45), (38.20, 38.80)], kaynak="10.1029/2020gl087775", acik_veri="bilinmiyor"),
    "Haiyuan_Laohushan": dict(iz=[(37.30, 102.90), (37.10, 103.50), (36.85, 104.30), (36.55, 105.30)],
                              sinir=[(37.10, 103.50), (36.85, 104.30)], kaynak="10.1029/2020jb021576",
                              acik_veri="bilinmiyor"),
    "Xianshuihe": dict(iz=[(31.40, 100.60), (31.00, 101.10), (30.50, 101.60), (30.05, 101.95), (29.60, 102.10),
                           (29.20, 102.30)],
                       sinir=[(31.00, 101.10), (30.05, 101.95)], kaynak="10.1029/2020jb021406", acik_veri="bilinmiyor"),
    "Longitudinal_Valley": dict(iz=[(23.95, 121.55), (23.50, 121.40), (23.10, 121.25), (22.75, 121.15)],
                                sinir=[(23.50, 121.40)], kaynak="10.1029/2023jb026843", acik_veri="bilinmiyor"),
    "Filipin_Leyte": dict(iz=[(11.60, 124.40), (11.10, 124.65), (10.60, 124.95), (10.20, 125.20)],
                          sinir=[(11.20, 124.60), (11.08, 124.66)], kaynak="10.1186/s40623-019-1096-5",
                          acik_veri="bilinmiyor"),
    "Filipin_Masbate": dict(iz=[(12.60, 123.15), (12.30, 123.55), (12.00, 123.90)],
                            sinir=[(12.30, 123.55)], kaynak="10.1186/bf03351877", acik_veri="bilinmiyor"),
    "Sumatra_Aceh": dict(iz=[(5.55, 95.25), (5.20, 95.60), (4.85, 96.10), (4.60, 96.60)],
                         sinir=[(5.20, 95.60), (4.85, 96.10)], kaynak="10.1038/s43247-026-03951-9", acik_veri="bilinmiyor"),
    "Chaman": dict(iz=[(29.30, 65.95), (30.00, 66.25), (30.90, 66.45), (31.60, 66.70), (32.40, 67.30)],
                   sinir=[(29.30, 65.95), (30.90, 66.45), (31.60, 66.70)], kaynak="10.1029/2021jb021935",
                   acik_veri="bilinmiyor"),
    "El_Pilar": dict(iz=[(10.47, -64.20), (10.50, -63.70), (10.55, -63.10), (10.60, -62.40)],
                     sinir=[(10.55, -63.10)], kaynak="10.1002/2016jb013121", acik_veri="bilinmiyor"),
    "Olu_Deniz_havza": dict(iz=[(31.80, 35.55), (31.30, 35.45), (30.90, 35.35)],
                            sinir=[(31.80, 35.55), (30.90, 35.35)], kaynak="10.1029/2024jb030191",
                            acik_veri="bilinmiyor"),
}


# ---------------------------------------------------------------- geometri
def _xy(la0, lo0, la, lo):
    k = math.cos(math.radians(la0))
    return (lo - lo0) * 111.195 * k, (la - la0) * 111.195


def iz_izdusum(iz, la, lo):
    """Noktanın ize en kısa uzaklığı (km), izdüşümün iz boyunca konumu (km, ilk köşeden) ve yerel doğrultu."""
    best = (1e9, 0.0, 0.0)
    birikim = 0.0
    for (a1, o1), (a2, o2) in zip(iz[:-1], iz[1:]):
        x1, y1 = _xy(la, lo, a1, o1)
        x2, y2 = _xy(la, lo, a2, o2)
        dx, dy = x2 - x1, y2 - y1
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, -(x1 * dx + y1 * dy) / L2))
        px, py = x1 + t * dx, y1 + t * dy
        d = math.hypot(px, py)
        if d < best[0]:
            best = (d, birikim + t * math.sqrt(L2), math.degrees(math.atan2(dx, dy)) % 180)
        birikim += math.sqrt(L2)
    return best


def iz_boyu(iz):
    return sum(T2.mesafe_az(a1, o1, a2, o2)[0] for (a1, o1), (a2, o2) in zip(iz[:-1], iz[1:]))


# ---------------------------------------------------------------- ek artçı sorgusu (aday olaylar için)
def artci_indir_25(ham9, b):
    os.makedirs(ham9, exist_ok=True)
    fn = os.path.join(ham9, b["id"] + "_m25.csv")
    if os.path.exists(fn):
        return fn
    t0 = b["t"]
    t1 = min(t0 + ARTCI_GUN * T2.GUN_MS, T2.BITIS_MS)
    iso = lambda ms: time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(ms / 1000))
    t = T2.sorgu({"format": "csv", "starttime": iso(t0 + 1000), "endtime": iso(t1),
                  "latitude": b["lat"], "longitude": b["lon"],
                  "maxradiuskm": round(ARTCI_R_L * T2.L_km(b["mw"]), 1),
                  "minmagnitude": 2.5, "orderby": "time-asc", "limit": 20000})
    open(fn, "w").write(t)
    return fn


def artcilar(fn, b, mmin):
    out = []
    for r in csv.DictReader(open(fn)):
        if r["id"] == b["id"] or not r["mag"]:
            continue
        m = float(r["mag"])
        if m < mmin or m >= b["mw"]:
            continue
        assert T2._ms(r["time"]) <= T2.BITIS_MS
        out.append((float(r["latitude"]), float(r["longitude"]), m))
    return out


def uc_olculur(b, kes, s_dis, s_sinir, art):
    """Sınıra bakan yanda yeterli artçı var mı. Yalnız SAYI; uç konumu hesaplanmaz."""
    iz = KESIMLER[kes]["iz"]
    L = T2.L_km(b["mw"])
    dik_max = max(ARTCI_DIK_KM, 0.5 * L)
    yon = 1 if s_sinir >= s_dis else -1   # sınır dış merkezin hangi yanında (olay öncesi bilgi)
    n_top = n_yan = 0
    for la, lo, _ in art:
        d, s, _ = iz_izdusum(iz, la, lo)
        if d > dik_max:
            continue
        n_top += 1
        if (s - s_dis) * yon >= T2.S_ICERI_KM:
            n_yan += 1
    return n_top, n_top >= UC_N_TOPLAM and n_yan >= UC_N_YAN


# ---------------------------------------------------------------- sayım
def say(ham2, ham9, cikti):
    istat = {}
    B = T2.birincil_sec(ham2, istat)
    satir = []
    for b in B:
        en = None
        for ad, k in KESIMLER.items():
            d, s, _ = iz_izdusum(k["iz"], b["lat"], b["lon"])
            if d <= YAKIN_KM and (en is None or d < en[1]):
                en = (ad, d, s)
        if en is None:
            continue
        ad, d, s = en
        L = T2.L_km(b["mw"])
        # en yakın sınır (doğrultu boyunca; olay öncesi bilgi)
        ss = [iz_izdusum(KESIMLER[ad]["iz"], la, lo)[1] for la, lo in KESIMLER[ad]["sinir"]]
        s_sinir = min(ss, key=lambda x: abs(x - s))
        z = {"id": b["id"], "tarih": time.strftime("%Y-%m-%d", time.gmtime(b["t"] / 1000)), "mw": b["mw"],
             "yer": b["yer"], "kesim": ad, "ize_km": round(d, 1), "L_km": round(L, 1),
             "sinira_dogrultu_km": round(abs(s_sinir - s), 1),
             "sinir_erisimde": abs(s_sinir - s) <= SINIR_ERISIM_L * L,
             "_lat": b["lat"], "_lon": b["lon"], "_t": b["t"]}
        f4 = os.path.join(ham2, "artci", b["id"] + ".csv")
        a4 = artcilar(f4, b, 4.0) if os.path.exists(f4) else []
        z["n_artci_M4_izde"], z["uc_olculur_M4"] = uc_olculur(b, ad, s, s_sinir, a4)
        f25 = artci_indir_25(ham9, b)
        for mmin, ek in ((3.0, "M3"), (2.5, "M25")):
            a = artcilar(f25, b, mmin)
            z[f"n_artci_{ek}_izde"], z[f"uc_olculur_{ek}"] = uc_olculur(b, ad, s, s_sinir, a)
        satir.append(z)

    # bağımsızlık: TR-2 ile aynı tek bağlantı (300 km, 1 yıl) ve ayrıca kesim-sınır birimi
    n = len(satir)
    ana = list(range(n))

    def bul(i):
        while ana[i] != i:
            ana[i] = ana[ana[i]]; i = ana[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if abs(satir[j]["_t"] - satir[i]["_t"]) > KUME_GUN * T2.GUN_MS:
                continue
            if T2.mesafe_az(satir[i]["_lat"], satir[i]["_lon"], satir[j]["_lat"], satir[j]["_lon"])[0] <= KUME_KM:
                ana[bul(i)] = bul(j)
    for i, z in enumerate(satir):
        z["kume"] = bul(i)

    def K(f):
        return len({z["kume"] for z in satir if f(z)})

    ozet = {"istat_tr2_birincil": istat, "birincil_ss_N": len(B), "kesim_yakin_N": n,
            "kesim_basina": {}, "esik": {}}
    for z in satir:
        ozet["kesim_basina"][z["kesim"]] = ozet["kesim_basina"].get(z["kesim"], 0) + 1
    for ek in ("M4", "M3", "M25"):
        f = lambda z, ek=ek: z[f"uc_olculur_{ek}"]
        g = lambda z, ek=ek: z[f"uc_olculur_{ek}"] and z["sinir_erisimde"]
        ozet["esik"][ek] = {"uc_olculur_N": sum(map(f, satir)), "K": K(f),
                            "uc_olculur_ve_sinir_erisimde_N": sum(map(g, satir)), "K_erisimde": K(g),
                            "K_kesim_birimi": len({z["kesim"] for z in satir if f(z)})}
    ozet["K_tum_yakin"] = K(lambda z: True)
    # Üst sınır (bölgesel düşük Mc'li katalogla uç her olayda ölçülebilse): iz üstünde (<= 15 km) ve sınır erişimde
    ust = lambda z: z["ize_km"] <= IZDE_KM and z["sinir_erisimde"]
    ozet["ust_sinir_izde_erisimde"] = {"N": sum(map(ust, satir)), "K": K(ust),
                                       "K_kesim_birimi": len({z["kesim"] for z in satir if ust(z)})}
    for z in satir:
        for k in ("_lat", "_lon", "_t"):
            z.pop(k)
    ozet["kesim_iz_boyu_km"] = {a: round(iz_boyu(k["iz"])) for a, k in KESIMLER.items()}
    json.dump({"ozet": ozet, "satirlar": satir}, open(cikti, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(ozet, ensure_ascii=False, indent=1))
    for z in satir:
        print(z["tarih"], z["id"], z["mw"], z["kesim"], z["ize_km"], "L", z["L_km"], "sınıra", z["sinira_dogrultu_km"],
              "erişim", z["sinir_erisimde"], "M4", z["n_artci_M4_izde"], z["uc_olculur_M4"],
              "M3", z["n_artci_M3_izde"], z["uc_olculur_M3"], "M2.5", z["n_artci_M25_izde"], z["uc_olculur_M25"],
              "küme", z["kume"])


# ---------------------------------------------------------------- güç
def binom_kuyruk(K, c, p):
    return sum(math.comb(K, i) * p ** i * (1 - p) ** (K - i) for i in range(c, K + 1))


def guc_tablosu():
    """İkili isabet: uç sınırın ±tolerans içinde. H0 isabet olasılığı p0 (yer değiştirme kontrolünden),
    H1 p1. Tek yanlı kesin binom, α 0,05."""
    print("K | p0 | kritik | güç p1=0,4 | 0,5 | 0,6")
    for K in (5, 8, 10, 12, 15, 20, 25, 30):
        for p0 in (0.15, 0.2, 0.3):
            c = next(c for c in range(K + 2) if binom_kuyruk(K, c, p0) <= 0.05)
            print(K, p0, c, *[round(binom_kuyruk(K, c, p1), 2) for p1 in (0.4, 0.5, 0.6)])
    # sıra (rank) ölçüsü: r_i ~ U(0,1) H0'da; H1'de r ~ Beta(a,1) (a<1 uca yakınlık). Ortalama r için tek yanlı
    # normal yaklaşım: güç = Φ((0,5 - E[r]) / (σ1/√K) - 1,645 σ0/σ1)
    print("sıra ölçüsü, H1 r~Beta(a,1)")
    for K in (5, 8, 10, 12, 15, 20, 30):
        row = []
        for a in (0.5, 0.6, 0.7):
            m1 = a / (a + 1); v1 = a / ((a + 1) ** 2 * (a + 2)); s0 = math.sqrt(1 / 12)
            z = (0.5 - m1) / math.sqrt(v1 / K) - 1.645 * s0 / math.sqrt(v1)
            row.append(round(0.5 * (1 + math.erf(z / math.sqrt(2))), 2))
        print(K, row)


def ek58(ham9):
    """Duyarlılık: TR-2 anlık görüntüsünde olmayan 5,8 <= M < 6,0 (her büyüklük türü) ve M>=6 Mw-dışı olaylardan
    kesim izine <= 15 km olanlar. Yalnız liste; mekanizma için olay ayrıntısı çekilir (küçük istek)."""
    f = os.path.join(ham9, "m58_aday.csv")
    if not os.path.exists(f):
        open(f, "w").write(T2.sorgu({"format": "csv", "starttime": T2.BASLA, "endtime": T2.BITIS,
                                     "minmagnitude": 5.8, "maxmagnitude": 5.99, "maxdepth": 25,
                                     "orderby": "time-asc", "limit": 20000}))
    for r in csv.DictReader(open(f)):
        if r["type"] != "earthquake":
            continue
        la, lo = float(r["latitude"]), float(r["longitude"])
        for ad, k in KESIMLER.items():
            d, s, _ = iz_izdusum(k["iz"], la, lo)
            if d <= IZDE_KM:
                rec = T2.detay(r["id"])
                dz, _ = T2.duzlemler(rec)
                print(r["time"][:10], r["id"], r["mag"], r["magType"], ad, round(d, 1),
                      "ss" if dz and T2.ss_mi(dz) else ("mekanizma yok" if not dz else "ss değil"))
                break


if __name__ == "__main__":
    if sys.argv[1] == "say":
        say(sys.argv[2], sys.argv[3], sys.argv[4])
    elif sys.argv[1] == "ek58":
        ek58(sys.argv[2])
    elif sys.argv[1] == "guc":
        guc_tablosu()
