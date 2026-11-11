#!/usr/bin/env python3
"""TR-2 isabet öncesi manifest (ön kayıt §6 adım 2). Taraf bilgisi TAŞIMAZ.

Üretir (bu dizine):
  tr2_manifest.csv           ana tanım (köken: dış merkez), K = 40 olmalı; değilse durur, hiçbir şey yazmaz.
  tr2_manifest_agirlik.csv   §5.2: köken artçı ağırlık merkezi; aynı kurallar; K ne çıkarsa.
  tr2_ham_sha256.txt         açılmış anlık görüntüdeki her dosyanın sha256 değeri ("ham/..." yollarıyla).

KÖRLÜK:
  * Sonraki ve önceki olay için yalnız `mutlak_eksen` (|s|, |d|) çağrılır. İşaret hiçbir değişkende tutulmaz.
  * `eksen_bilesen` (işaretli s) yalnız ARTÇILAR için çağrılır: sessiz taraf, ağırlık merkezi, u/L.
  * Ağ sorgusu yok. Tanımlar `tr2_sayim.py`'den içe aktarılır.

Kullanım:
  python3 -I -B tr2_manifest.py <ham_dizin> [<tar.gz>]
    <ham_dizin>: anlık görüntünün açılmış "ham" dizini. <tar.gz> verilirse sha256'sı kayıttaki değerle doğrulanır.
"""
import csv
import hashlib
import math
import os
import sys

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr2_sayim as S  # noqa: E402

TAR_SHA = "07881910d94d8b66c377c9ae42ce8f1e18843b5117a92cec53aaa527f61efd59"
K_BEKLENEN = 40
ZAYIF_DUZLEM_DER = 30.0           # §5.3
ADAY_COK = 3                       # §5.4
GOLGE_YIL, GOLGE_R_L = 1.0, 3.0    # §5.5 = SAYIM §4 varyantı (1 yıl, 3 L_büyük)
BASLA_MS = S._ms("1976-01-01T00:00:00")

ALANLAR = ["kume", "birincil_id", "t0", "t0_ms", "mw", "L_km", "stk", "dis_merkez_lat", "dis_merkez_lon",
           "koken", "koken_lat", "koken_lon", "sessiz_isaret", "n_taraf", "absA",
           "sonraki_id", "sonraki_t", "sonraki_m", "sonraki_tur", "sonraki_abs_s_L", "sonraki_abs_d_km",
           "aday_sayisi", "onceki_id", "onceki_t", "onceki_abs_s_L", "onceki_abs_d_km",
           "u_L", "duzlem_pca_fark", "zayif_duzlem", "aday_ge3", "golge", "cift_oncu",
           "sonraki_s_le_L", "sonraki_m_ge_mw", "sonraki_ss_birincil", "tr", "kume_birincil_sayisi"]


# ---------------------------------------------------------------- okuma
def havuz_oku(ham):
    out = []
    for r in csv.DictReader(open(os.path.join(ham, "m6_havuz.csv"))):
        out.append({"id": r["id"], "t": S._ms(r["time"]), "time": r["time"], "lat": float(r["latitude"]),
                    "lon": float(r["longitude"]), "m": float(r["mag"]), "tur": r.get("type", "")})
    assert all(h["t"] <= S.BITIS_MS for h in out), "KÖRLÜK: havuzda 2025 sonrası olay"
    out.sort(key=lambda h: (h["t"], h["id"]))
    return out


def artci_oku(ham, b):
    """SAYIM §1 artçı bulutu (tr2_sayim.say ile aynı süzgeç) ve bulut dışı M >= Mw olaylar (çift/öncü)."""
    art, buyuk = [], []
    for r in csv.DictReader(open(os.path.join(ham, "artci", b["id"] + ".csv"))):
        if r["id"] == b["id"] or not r["mag"]:
            continue
        m = float(r["mag"])
        if m < S.ARTCI_M:
            continue
        if m >= b["mw"]:
            buyuk.append(r["id"])
            continue
        art.append((float(r["latitude"]), float(r["longitude"]), m))
    return art, buyuk


def sha_listesi(ham):
    """Arşivdeki düzenle aynı yollar: ham/<göreli yol>."""
    sat = []
    for kok, _, dosyalar in os.walk(ham):
        for f in dosyalar:
            p = os.path.join(kok, f)
            rel = "ham/" + os.path.relpath(p, ham).replace(os.sep, "/")
            sat.append((rel, hashlib.sha256(open(p, "rb").read()).hexdigest()))
    sat.sort()
    return [f"{h}  {r}" for r, h in sat]


# ---------------------------------------------------------------- geometri (yeni yardımcı; tanım değil)
def hedef_nokta(lat, lon, d_km, az_der):
    """Büyük çember üzerinde (lat, lon)'dan az yönünde d km gidilen nokta (mesafe_az'ın tersi)."""
    p1, l1 = math.radians(lat), math.radians(lon)
    dd, th = d_km / S.R_E, math.radians(az_der)
    p2 = math.asin(math.sin(p1) * math.cos(dd) + math.cos(p1) * math.sin(dd) * math.cos(th))
    l2 = l1 + math.atan2(math.sin(th) * math.sin(dd) * math.cos(p1), math.cos(dd) - math.sin(p1) * math.sin(p2))
    return math.degrees(p2), (math.degrees(l2) + 540) % 360 - 180


def agirlik_merkezi(b, art):
    """Artçı dış merkezlerinin, PCA'da kullanılan yerel düzlemdeki (azimut eşit uzaklıklı) ortalaması."""
    xy = []
    for la, lo, _ in art:
        d, az = S.mesafe_az(b["lat"], b["lon"], la, lo)
        xy.append((d * math.sin(math.radians(az)), d * math.cos(math.radians(az))))
    e = sum(x for x, _ in xy) / len(xy)
    n = sum(y for _, y in xy) / len(xy)
    return hedef_nokta(b["lat"], b["lon"], math.hypot(e, n), math.degrees(math.atan2(e, n)))


# ---------------------------------------------------------------- birincil analizi
def dogrultu(b, art):
    """tr2_sayim.say ile aynı: PCA ana ekseni, λ1/λ2 ≥ 2, ona yakın düğüm düzlemi."""
    if len(art) < S.PCA_N_MIN:
        return None, None
    xy = []
    for la, lo, _ in art:
        d, az = S.mesafe_az(b["lat"], b["lon"], la, lo)
        xy.append((d * math.sin(math.radians(az)), d * math.cos(math.radians(az))))
    paz, oran = S.pca_azimut(xy)
    if oran < S.PCA_ORAN_MIN:
        return None, None
    (s1, _, _), (s2, _, _) = b["dz"]
    stk = s1 if S.ac_fark(s1, paz) <= S.ac_fark(s2, paz) else s2
    return stk, min(S.ac_fark(s1, paz), S.ac_fark(s2, paz))


def asimetri(koken, art, stk):
    """Köken (dış merkez ya da ağırlık merkezi) etrafında n+ / n−. Dönüş: (n, |A|, sessiz_isaret)."""
    npoz = nneg = 0
    for la, lo, _ in art:
        s, _ = S.eksen_bilesen(koken, la, lo, stk)
        if s >= S.S_ICERI_KM:
            npoz += 1
        elif s <= -S.S_ICERI_KM:
            nneg += 1
    n = npoz + nneg
    if n == 0:
        return 0, None, None
    absA = abs(npoz - nneg) / n
    sessiz = None if npoz == nneg else (1 if npoz < nneg else -1)  # artçısı AZ olan taraf
    return n, absA, sessiz


def kutu_adaylari(koken, b, stk, L, havuz, yon):
    """Kutuya düşen havuz olayları, zaman sırasıyla. Yalnız |s|, |d| (mutlak_eksen)."""
    if yon == "sonraki":
        t_a, t_b = b["t"] + S.SON_T0_GUN * S.GUN_MS, min(b["t"] + S.SON_T1_YIL * S.YIL_MS, S.BITIS_MS)
        zaman = lambda t: t_a < t <= t_b            # (t0 + 30 gün, min(t0 + 15 yıl, 2025-12-31)]
    else:
        t_a, t_b = max(b["t"] - S.SON_T1_YIL * S.YIL_MS, BASLA_MS), b["t"] - S.SON_T0_GUN * S.GUN_MS
        zaman = lambda t: t_a <= t < t_b            # [max(t0 − 15 yıl, 1976-01-01), t0 − 30 gün)
    D = max(S.SON_D_L * L, S.SON_D_KM)
    out = []
    for h in havuz:
        if h["id"] == b["id"] or not zaman(h["t"]):
            continue
        if abs(h["lat"] - b["lat"]) > 8:            # tr2_sayim'deki kaba ön süzgeç (kutudan geniş)
            continue
        aS, aD = S.mutlak_eksen(koken, h["lat"], h["lon"], stk)
        if S.SON_S_MIN_L * L <= aS <= S.SON_S_MAX_L * L and aD <= D:
            out.append({"id": h["id"], "t": h["t"], "time": h["time"], "m": h["m"], "tur": h["tur"],
                        "abs_s": aS, "abs_d": aD})
    return out


def golgede(b, havuz):
    """SAYIM §4 varyantı (tr2_sayim.say içindeki golgede ile aynı ölçüt)."""
    for h in havuz:
        if h["m"] > b["mw"] and 0 < b["t"] - h["t"] <= GOLGE_YIL * S.YIL_MS:
            if S.mesafe_az(h["lat"], h["lon"], b["lat"], b["lon"])[0] <= GOLGE_R_L * S.L_km(h["m"]):
                return True
    return False


def kumele(B):
    """tr2_sayim.say ile aynı tek bağlantılı kümeleme (300 km, 365,25 gün), aynı sıra."""
    n = len(B)
    ana = list(range(n))

    def bul(i):
        while ana[i] != i:
            ana[i] = ana[ana[i]]
            i = ana[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if abs(B[j]["t"] - B[i]["t"]) > S.KUME_GUN * S.GUN_MS:
                continue
            d, _ = S.mesafe_az(B[i]["lat"], B[i]["lon"], B[j]["lat"], B[j]["lon"])
            if d <= S.KUME_KM:
                ana[bul(i)] = bul(j)
    return [bul(i) for i in range(n)]


# ---------------------------------------------------------------- manifest
def hazirla(ham):
    """Bütün birincilleri bir kez analiz eder; iki köken için gereken her şeyi döndürür."""
    B = S.birincil_sec(ham)
    havuz = havuz_oku(ham)
    ss_ids = {b["id"] for b in B}
    kok = kumele(B)
    analiz = []
    for b, k in zip(B, kok):
        L = S.L_km(b["mw"])
        art, buyuk = artci_oku(ham, b)
        stk, pfark = dogrultu(b, art)
        z = {"b": b, "L": L, "art": art, "buyuk": buyuk, "stk": stk, "pfark": pfark, "kok": k}
        if stk is not None:
            cla, clo = agirlik_merkezi(b, art)
            z["cen"] = {"lat": cla, "lon": clo}
            z["u"] = abs(S.eksen_bilesen(b, cla, clo, stk)[0])
        analiz.append(z)
    return B, havuz, ss_ids, analiz


def asim_olculur(n, absA, sayim_yuvarlama):
    """Metin (SAYIM §1): n+ + n− ≥ 10 ve |A| ≥ 1/3.
    sayim_yuvarlama=True: tr2_sayim.say'deki fiilî karşılaştırma, round(|A|, 3) ≥ 1/3; yani |A| = 1/3 tam
    eşitliği DIŞARIDA kalır (0,333 < 0,3333…). Varsayılan metindir; seçim kök oturumundadır."""
    if n < S.ASIM_N_MIN or absA is None:
        return False
    return (round(absA, 3) if sayim_yuvarlama else absA) >= S.ASIM_ESIK


def manifest_kur(analiz, havuz, ss_ids, koken_turu, sayim_yuvarlama=False):
    """koken_turu: 'dis_merkez' (ana) ya da 'agirlik' (§5.2). Dönüş: (satırlar, istatistik)."""
    bilgi = {}
    for i, z in enumerate(analiz):
        if z["stk"] is None:
            continue
        b = z["b"]
        koken = {"lat": b["lat"], "lon": b["lon"]} if koken_turu == "dis_merkez" else z["cen"]
        n, absA, sessiz = asimetri(koken, z["art"], z["stk"])
        olc = asim_olculur(n, absA, sayim_yuvarlama)
        if not olc:
            continue
        assert sessiz is not None
        bilgi[i] = {"koken": koken, "n": n, "absA": absA, "sessiz": sessiz,
                    "son": kutu_adaylari(koken, b, z["stk"], z["L"], havuz, "sonraki"),
                    "once": kutu_adaylari(koken, b, z["stk"], z["L"], havuz, "onceki")}
    kumeler = {}
    for i, z in enumerate(analiz):
        kumeler.setdefault(z["kok"], []).append(i)   # B zaman sırasında; liste de öyle

    # Ortak sonraki olay kuralı (§2): sabit nokta. Dışlanan olay o küme için atlanır, sıradaki aday denenir.
    dislanan = {k: set() for k in kumeler}
    ortak_olay = []
    while True:
        secim = {}
        for k, idx in kumeler.items():
            for i in idx:
                if i in bilgi:
                    kalan = [c for c in bilgi[i]["son"] if c["id"] not in dislanan[k]]
                    if kalan:
                        secim[k] = (i, kalan[0])
                        break
        olaya = {}
        for k, (i, c) in secim.items():
            olaya.setdefault(c["id"], []).append(k)
        degisti = False
        for eid, ks in olaya.items():
            if len(ks) > 1:
                ks = sorted(ks, key=lambda k: (analiz[secim[k][0]]["b"]["t"], analiz[secim[k][0]]["b"]["id"]))
                for k in ks[1:]:
                    dislanan[k].add(eid)
                    ortak_olay.append({"olay": eid, "kazanan": analiz[secim[ks[0]][0]]["b"]["id"],
                                       "dislanan_kume_birincil": analiz[secim[k][0]]["b"]["id"]})
                degisti = True
        if not degisti:
            break

    sat = []
    for k, (i, c) in sorted(secim.items(), key=lambda kv: (analiz[kv[1][0]]["b"]["t"], analiz[kv[1][0]]["b"]["id"])):
        z, bi, b = analiz[i], bilgi[i], analiz[i]["b"]
        L = z["L"]
        once = bi["once"][-1] if bi["once"] else None
        tr = S.TR_KUTU[0] <= b["lat"] <= S.TR_KUTU[1] and S.TR_KUTU[2] <= b["lon"] <= S.TR_KUTU[3]
        sat.append({
            "kume": f"K{len(sat) + 1:02d}", "birincil_id": b["id"],
            "t0": S.time.strftime("%Y-%m-%dT%H:%M:%S", S.time.gmtime(b["t"] / 1000)) + f".{b['t'] % 1000:03d}Z",
            "t0_ms": b["t"], "mw": b["mw"], "L_km": repr(L), "stk": repr(float(z["stk"])),
            "dis_merkez_lat": b["lat"], "dis_merkez_lon": b["lon"], "koken": koken_turu,
            "koken_lat": repr(float(bi["koken"]["lat"])), "koken_lon": repr(float(bi["koken"]["lon"])),
            "sessiz_isaret": bi["sessiz"], "n_taraf": bi["n"], "absA": f"{bi['absA']:.4f}",
            "sonraki_id": c["id"], "sonraki_t": c["time"], "sonraki_m": c["m"], "sonraki_tur": c["tur"],
            "sonraki_abs_s_L": f"{c['abs_s'] / L:.4f}", "sonraki_abs_d_km": f"{c['abs_d']:.3f}",
            "aday_sayisi": len(bi["son"]),
            "onceki_id": once["id"] if once else "", "onceki_t": once["time"] if once else "",
            "onceki_abs_s_L": f"{once['abs_s'] / L:.4f}" if once else "",
            "onceki_abs_d_km": f"{once['abs_d']:.3f}" if once else "",
            "u_L": f"{z['u'] / L:.4f}", "duzlem_pca_fark": f"{z['pfark']:.2f}",
            "zayif_duzlem": int(z["pfark"] > ZAYIF_DUZLEM_DER), "aday_ge3": int(len(bi["son"]) >= ADAY_COK),
            "golge": int(golgede(b, havuz)), "cift_oncu": int(len(z["buyuk"]) > 0),
            "sonraki_s_le_L": int(c["abs_s"] / L <= 1.0), "sonraki_m_ge_mw": int(c["m"] >= b["mw"]),
            "sonraki_ss_birincil": int(c["id"] in ss_ids), "tr": int(tr),
            "kume_birincil_sayisi": sum(1 for j in kumeler[k]),
        })
    ist = {"K": len(sat), "nitelikli_birincil": sum(1 for i in bilgi if bilgi[i]["son"]),
           "ortak_sonraki_olay": ortak_olay, "K_ters_adayi": sum(1 for s in sat if s["onceki_id"])}
    return sat, ist


def yaz_csv(yol, sat):
    with open(yol, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ALANLAR, lineterminator="\n")
        w.writeheader()
        for s in sat:
            w.writerow(s)


def main(ham, tar=None, cikti=BURA, sayim_yuvarlama=False):
    if tar:
        h = hashlib.sha256(open(tar, "rb").read()).hexdigest()
        assert h == TAR_SHA, f"anlık görüntü sha256 uyuşmuyor: {h}"
    B, havuz, ss_ids, analiz = hazirla(ham)
    ana, ist = manifest_kur(analiz, havuz, ss_ids, "dis_merkez", sayim_yuvarlama)
    if ist["K"] != K_BEKLENEN:
        print(f"DUR: manifest K = {ist['K']} (beklenen {K_BEKLENEN}). Hiçbir dosya yazılmadı. "
              "Kayıt 'anlık görüntüden yeniden üretilemedi' diye kapanır.", file=sys.stderr)
        sys.exit(2)
    ag, ist_ag = manifest_kur(analiz, havuz, ss_ids, "agirlik", sayim_yuvarlama)
    os.makedirs(cikti, exist_ok=True)
    yaz_csv(os.path.join(cikti, "tr2_manifest.csv"), ana)
    yaz_csv(os.path.join(cikti, "tr2_manifest_agirlik.csv"), ag)
    with open(os.path.join(cikti, "tr2_ham_sha256.txt"), "w") as f:
        f.write("\n".join(sha_listesi(ham)) + "\n")
    ozet = {
        "K": ist["K"], "nitelikli_birincil": ist["nitelikli_birincil"],
        "ortak_sonraki_olay_sayisi": len(ist["ortak_sonraki_olay"]), "K_ters_adayi": ist["K_ters_adayi"],
        "K_agirlik": ist_ag["K"], "ortak_sonraki_olay_sayisi_agirlik": len(ist_ag["ortak_sonraki_olay"]),
        "K_ters_adayi_agirlik": ist_ag["K_ters_adayi"],
        "bayrak_toplamlari": {a: sum(int(s[a]) for s in ana) for a in
                              ("zayif_duzlem", "aday_ge3", "golge", "cift_oncu", "sonraki_s_le_L",
                               "sonraki_m_ge_mw", "sonraki_ss_birincil", "tr")},
        "deprem_disi_sonraki": sum(1 for s in ana if s["sonraki_tur"] != "earthquake"),
        "u_L_medyan": sorted(float(s["u_L"]) for s in ana)[len(ana) // 2 - 1: len(ana) // 2 + 1],
    }
    print(ozet)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("ham")
    ap.add_argument("tar", nargs="?")
    ap.add_argument("--cikti", default=BURA)
    ap.add_argument("--sayim-yuvarlama", action="store_true",
                    help="|A| ölçütünü tr2_sayim.say'deki gibi round(|A|,3) ≥ 1/3 ile uygula (bkz. asim_olculur)")
    a = ap.parse_args()
    main(a.ham, a.tar, a.cikti, a.sayim_yuvarlama)
