#!/usr/bin/env python3
"""TR-2 tek koşu: isabet, hüküm, yorum kuralları, §4 log skorları, §5 bilgi satırları.

Ön kayıt: kayit/onkayit/TR-2_sonraki-M6-yonu_ONKAYIT.md (DONDURULDU). Bu betik yalnız manifestteki id'leri,
stk'yi ve kökeni (ana manifestte dış merkez) kullanır. Ham veriden yalnız havuz koordinatları okunur; birincil
dış merkezleri ve dosya sha256 değerleri doğrulanır.

Kullanım (tek komut):
  python3 -I -B kayit/turetme/tr2/tr2_kosu.py --ham <açılmış anlık görüntü>/ham
Varsayılan girdiler bu dizindedir: tr2_manifest.csv, tr2_manifest_agirlik.csv, tr2_ham_sha256.txt, tr2_etas_p.csv.
Çıktı: tr2_sonuc.json ve tr2_sonuc.md (varsayılan bu dizin). Çıktı zaten varsa durur (tek koşu).

İsabet hesabının çekirdeği `isabet()` ve `hesapla()` dosya açmaz; yapay testten doğrudan çağrılır.
"""
import csv
import hashlib
import json
import math
import os
import statistics
import sys

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr2_sayim as S  # noqa: E402

K_BEKLENEN = 40
H1_ESIK, H0_ESIK = 26, 22          # §3: X ≥ 26 H1, X ≤ 22 H0, 23–25 ayırt edilemez (K = 40)
TERS_YON_ESIK = 14                 # §5.6
ALFA = 0.05
Q_BOSLUK = 0.65                    # §4
BOOT_N, BOOT_TOHUM = 10000, 20261111
KOMSU_AG_ORAN = 0.6                # §3 yorum kuralı (ii)


# ---------------------------------------------------------------- çekirdek (dosya açmaz)
def isabet(koken_lat, koken_lon, stk, sessiz_isaret, olay_lat, olay_lon):
    """§2: s işareti, sessiz tarafın hesaplandığı stk ile, aynı `eksen_bilesen` ile, köken merkezli.
    Dönüş 1 (s işareti = sessiz tarafın işareti) ya da 0."""
    s, _ = S.eksen_bilesen({"lat": koken_lat, "lon": koken_lon}, olay_lat, olay_lon, stk)
    if s == 0:
        raise ValueError("s = 0: tanım gereği olamaz (|s| ≥ 0,5 L)")
    if sessiz_isaret not in (1, -1):
        raise ValueError("sessiz_isaret ±1 olmalı")
    return int((1 if s > 0 else -1) == sessiz_isaret)


def binom_ust(x, n, p=0.5):
    """P(X ≥ x), kesin."""
    return math.fsum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(max(x, 0), n + 1))


def binom_alt(x, n, p=0.5):
    """P(X ≤ x), kesin."""
    return math.fsum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, min(x, n) + 1))


def hukum(X, K):
    if K != K_BEKLENEN:
        raise ValueError(f"eşikler K = {K_BEKLENEN} için donduruldu; K = {K}")
    if X >= H1_ESIK:
        return "H1"
    if X <= H0_ESIK:
        return "H0"
    return "ayirt_edilemez"


def bootstrap(farklar, n=BOOT_N, tohum=BOOT_TOHUM):
    """Küme bootstrap'i. farklar: {ad: küme başına fark listesi}; hepsi aynı yeniden örnekleme indisleriyle
    (eşleştirilmiş). Dönüş: {ad: (alt %2,5, üst %97,5)} toplam log skor farkı (nat) için."""
    import numpy as np
    K = len(next(iter(farklar.values())))
    rng = np.random.default_rng(tohum)
    idx = rng.integers(0, K, size=(n, K))
    out = {}
    for ad, v in farklar.items():
        t = np.asarray(v, dtype=float)[idx].sum(axis=1)
        lo, hi = np.percentile(t, [2.5, 97.5])
        out[ad] = (float(lo), float(hi))
    return out


def _bern(h, p):
    return math.log(p) if h else math.log(1 - p)


def _xk(satirlar, anahtar="isabet"):
    v = [r[anahtar] for r in satirlar if r[anahtar] is not None]
    return {"X": sum(v), "K": len(v), "oran": (sum(v) / len(v)) if v else None}


def _olay_hesap(r, olaylar, alan):
    """Manifestteki olay için isabet; |s|/L ve |d| manifestle tutarlılık denetimi (doğru olay mı)."""
    eid = r[alan + "_id"]
    if not eid:
        return None
    lat, lon = olaylar[eid]
    L, stk = float(r["L_km"]), float(r["stk"])
    kl, ko = float(r["koken_lat"]), float(r["koken_lon"])
    aS, aD = S.mutlak_eksen({"lat": kl, "lon": ko}, lat, lon, stk)
    if abs(aS / L - float(r[alan + "_abs_s_L"])) > 1e-3 or abs(aD - float(r[alan + "_abs_d_km"])) > 1e-2:
        raise ValueError(f"{r['kume']} {alan}: |s|/L ya da |d| manifestle uyuşmuyor")
    return isabet(kl, ko, stk, int(r["sessiz_isaret"]), lat, lon)


def hesapla(manifest, manifest_ag, olaylar, etas):
    """manifest, manifest_ag: satır sözlükleri listesi (CSV alanları). olaylar: {id: (lat, lon)}.
    etas: {kume: p_i}. Dosya açmaz."""
    K = len(manifest)
    sat = []
    for r in manifest:
        sat.append({
            "kume": r["kume"], "birincil_id": r["birincil_id"], "t0": r["t0"], "mw": float(r["mw"]),
            "sessiz_isaret": int(r["sessiz_isaret"]), "sonraki_id": r["sonraki_id"],
            "isabet": _olay_hesap(r, olaylar, "sonraki"),
            "onceki_id": r["onceki_id"] or None, "isabet_ters": _olay_hesap(r, olaylar, "onceki"),
            "p_etas": float(etas[r["kume"]]),
            **{a: int(r[a]) for a in ("zayif_duzlem", "aday_ge3", "golge", "cift_oncu", "sonraki_s_le_L",
                                       "sonraki_m_ge_mw", "sonraki_ss_birincil", "tr")},
            "u_L": float(r["u_L"]), "aday_sayisi": int(r["aday_sayisi"]),
        })
    if any(s["isabet"] is None for s in sat):
        raise ValueError("ana manifestte sonraki olayı olmayan küme var")
    X = sum(s["isabet"] for s in sat)
    hk = hukum(X, K)

    # §4 log skorları
    for s in sat:
        h = s["isabet"]
        s["ls_taban"] = _bern(h, 0.5)
        s["ls_bosluk"] = _bern(h, Q_BOSLUK)
        s["ls_etas"] = _bern(h, s["p_etas"])
    farklar = {
        "bosluk_eksi_taban": [s["ls_bosluk"] - s["ls_taban"] for s in sat],
        "etas_eksi_taban": [s["ls_etas"] - s["ls_taban"] for s in sat],
        "bosluk_eksi_etas": [s["ls_bosluk"] - s["ls_etas"] for s in sat],
    }
    ara = bootstrap(farklar)
    log_skor = {ad: {"fark_nat": math.fsum(v), "aralik_95": list(ara[ad]),
                     "sifiri_icerir": ara[ad][0] <= 0 <= ara[ad][1]} for ad, v in farklar.items()}
    log_skor["toplamlar_nat"] = {m: math.fsum(s["ls_" + m] for s in sat) for m in ("taban", "bosluk", "etas")}

    # §5 bilgi satırları
    b = {}
    med = statistics.median(s["u_L"] for s in sat)
    b["1_u_L"] = {"medyan": med, "alt": _xk([s for s in sat if s["u_L"] < med]),
                  "ust": _xk([s for s in sat if s["u_L"] > med]),
                  "medyana_esit": sum(1 for s in sat if s["u_L"] == med)}
    ag = []
    for r in manifest_ag:
        ag.append({"kume": r["kume"], "birincil_id": r["birincil_id"], "isabet": _olay_hesap(r, olaylar, "sonraki")})
    b["2_agirlik_merkezi"] = _xk(ag)
    b["3_zayif_duzlem"] = {"var": _xk([s for s in sat if s["zayif_duzlem"]]),
                           "yok": _xk([s for s in sat if not s["zayif_duzlem"]])}
    b["4_aday_ge3"] = {"var": _xk([s for s in sat if s["aday_ge3"]]),
                       "yok": _xk([s for s in sat if not s["aday_ge3"]])}
    b["5_golge_disli"] = _xk([s for s in sat if not s["golge"]])
    ters_yon = X <= TERS_YON_ESIK
    b["6_ters_yon_notu"] = ters_yon
    b["7_turkiye"] = [{"kume": s["kume"], "birincil_id": s["birincil_id"], "isabet": s["isabet"]}
                      for s in sat if s["tr"]]
    tr = _xk(sat, "isabet_ters")
    tr["ust_kuyruk_p"] = binom_ust(tr["X"], tr["K"]) if tr["K"] else None
    tr["alt_kuyruk_p"] = binom_alt(tr["X"], tr["K"]) if tr["K"] else None
    b["8_zaman_ters_cevrimi"] = tr
    b["9_cift_oncu_disli"] = _xk([s for s in sat if not s["cift_oncu"]])
    b["10_alt_gruplar"] = {a: {"grup": _xk([s for s in sat if s[a]]), "tumleyen": _xk([s for s in sat if not s[a]])}
                           for a in ("sonraki_s_le_L", "sonraki_m_ge_mw", "sonraki_ss_birincil")}

    # §3 yorum kuralları
    ust_red = tr["K"] > 0 and tr["ust_kuyruk_p"] <= ALFA
    alt_red = tr["K"] > 0 and tr["alt_kuyruk_p"] <= ALFA
    a1, a2 = b["1_u_L"]["alt"]["oran"], b["1_u_L"]["ust"]["oran"]
    kosul_i = a1 is not None and a2 is not None and a1 > 0.5 and a2 > 0.5
    agk = b["2_agirlik_merkezi"]
    kosul_ii = agk["K"] > 0 and agk["X"] / agk["K"] >= KOMSU_AG_ORAN
    y = {}
    y["kural1_arka_plan_kaymasi"] = {"olcum": "§5.8 zaman ters çevrimi", "ust_kuyruk_red": ust_red,
                                     "alt_kuyruk_red": alt_red}
    y["kural2_H1_ve_ters_ust_red"] = {"uygulanir": hk == "H1" and ust_red,
                                      "metin": "H1, sıraya özgü değil, statik geometriyle ayırt edilemez; §8'e "
                                               "hiçbir şey taşınmaz" if hk == "H1" and ust_red else None}
    k3 = (hk == "H0" or ters_yon) and alt_red
    y["kural3_H0_ya_da_ters_yon_ve_ters_alt_red"] = {
        "uygulanir": k3, "metin": "arka plan asimetrisiyle ayırt edilemez; ETAS lehine okunmaz" if k3 else None}
    if hk == "H1":
        komsu = kosul_i and kosul_ii
        ad = ("kırılmamış komşu kesim yorumu yazılabilir" if komsu
              else "dış merkezin arkası; kırılma yönüyle ayırt edilemez")
    else:
        komsu, ad = None, None
    y["kural4_ad"] = {"hukmun_adi": "sessiz taraf", "kosul_i_u_L_iki_yarida_oran_gt_0_5": kosul_i,
                      "kosul_ii_agirlik_X_K_ge_0_6": kosul_ii, "H1_yorumu": ad}
    bt = log_skor["bosluk_eksi_taban"]
    y["s4_oncelik"] = {
        "karar_yalniz_binom": True,
        "H1_ve_bosluk_taban_araligi_sifiri_iceriyor": hk == "H1" and bt["sifiri_icerir"],
        "metin": "H1, log skor aralığı sıfırı içeriyor" if hk == "H1" and bt["sifiri_icerir"] else None,
        "etas_satirlari_sifiri_dislar": {a: not log_skor[a]["sifiri_icerir"]
                                         for a in ("etas_eksi_taban", "bosluk_eksi_etas")},
        "etas_okumasi_arka_plan_kuralina_tabi": k3,
    }
    y["s8_aktarim_adayi"] = bool(hk == "H1" and komsu and not ust_red)
    return {"K": K, "X": X, "oran": X / K, "hukum": hk,
            "binom": {"ust_kuyruk_p_0_5": binom_ust(X, K, 0.5), "alt_kuyruk_p_0_70": binom_alt(X, K, 0.70)},
            "yorum_kurallari": y, "log_skor": log_skor, "bilgi_satirlari": b,
            "kume_satirlari": sat, "agirlik_satirlari": ag}


# ---------------------------------------------------------------- dosyalar
def sha_dogrula(ham, sha_dosya):
    beklenen = {}
    for s in open(sha_dosya):
        if s.strip():
            h, yol = s.rstrip("\n").split("  ", 1)
            assert yol.startswith("ham/")
            beklenen[yol[4:]] = h
    bulunan = set()
    for kok, _, dosyalar in os.walk(ham):
        for f in dosyalar:
            bulunan.add(os.path.relpath(os.path.join(kok, f), ham).replace(os.sep, "/"))
    if bulunan != set(beklenen):
        raise SystemExit(f"sha listesi ile dizin uyuşmuyor: eksik {sorted(set(beklenen) - bulunan)[:5]}, "
                         f"fazla {sorted(bulunan - set(beklenen))[:5]}")
    for yol, h in beklenen.items():
        if hashlib.sha256(open(os.path.join(ham, yol), "rb").read()).hexdigest() != h:
            raise SystemExit(f"sha256 uyuşmuyor: {yol}")
    return len(beklenen)


def dosyalari_oku(ham, manifest_yol, ag_yol, etas_yol):
    man = list(csv.DictReader(open(manifest_yol)))
    ag = list(csv.DictReader(open(ag_yol)))
    if len(man) != K_BEKLENEN:
        raise SystemExit(f"manifest K = {len(man)} ≠ {K_BEKLENEN}: sınav koşulmaz")
    etas_sat = list(csv.DictReader(open(etas_yol)))
    if [(e["kume"], e["birincil_id"]) for e in etas_sat] != [(r["kume"], r["birincil_id"]) for r in man]:
        raise SystemExit("ETAS dosyası manifestle aynı küme/birincil sırasında değil")
    etas = {e["kume"]: float(e["p_i"]) for e in etas_sat}
    # birincil dış merkezleri ham veriyle doğrula
    aday = {r["id"]: r for r in S.aday_oku(ham)}
    for r in man + ag:
        a = aday[r["birincil_id"]]
        if (abs(float(a["latitude"]) - float(r["dis_merkez_lat"])) > 1e-9
                or abs(float(a["longitude"]) - float(r["dis_merkez_lon"])) > 1e-9
                or abs(float(a["mag"]) - float(r["mw"])) > 1e-9 or S._ms(a["time"]) != int(r["t0_ms"])):
            raise SystemExit(f"birincil {r['birincil_id']} ham veriyle uyuşmuyor")
    gerek = {r[k] for r in man + ag for k in ("sonraki_id", "onceki_id") if r.get(k)}
    olaylar = {}
    for h in csv.DictReader(open(os.path.join(ham, "m6_havuz.csv"))):
        if h["id"] in gerek:
            assert S._ms(h["time"]) <= S.BITIS_MS
            olaylar[h["id"]] = (float(h["latitude"]), float(h["longitude"]))
    eksik = gerek - set(olaylar)
    if eksik:
        raise SystemExit(f"havuzda bulunmayan olay: {sorted(eksik)}")
    return man, ag, olaylar, etas


def _f(x, n=3):
    return "—" if x is None else (f"{x:.{n}f}" if isinstance(x, float) else str(x))


def _xks(d):
    return f"X = {d['X']}, K = {d['K']}, oran {_f(d['oran'])}"


def md_yaz(r):
    y, b, ls = r["yorum_kurallari"], r["bilgi_satirlari"], r["log_skor"]
    ad = {"H1": "H1 (sessiz taraf)", "H0": "H0 (büyük etki yok)", "ayirt_edilemez": "ayırt edilemez"}[r["hukum"]]
    L = ["# TR-2 sonucu: sonraki M≥6 sessiz tarafta mı?", "",
         "Ön kayıt: `kayit/onkayit/TR-2_sonraki-M6-yonu_ONKAYIT.md` (DONDURULDU). Kod: `kayit/turetme/tr2/tr2_kosu.py`.",
         "", "## Hüküm (§3)", "",
         f"- K = {r['K']}, X = {r['X']}, oran {r['oran']:.3f}.",
         f"- Hüküm: **{ad}** (eşikler: X ≥ 26 H1, X ≤ 22 H0, 23–25 ayırt edilemez).",
         f"- P(X ≥ {r['X']} | p = 0,5) = {r['binom']['ust_kuyruk_p_0_5']:.4f}; "
         f"P(X ≤ {r['X']} | p = 0,70) = {r['binom']['alt_kuyruk_p_0_70']:.4f}.", "",
         "## Yorum kuralları (§3; hükmü değiştirmez)", "",
         f"1. Arka plan kayması (§5.8 ile ölçülür): ters çevrim üst kuyruk reddi "
         f"{y['kural1_arka_plan_kaymasi']['ust_kuyruk_red']}, alt kuyruk reddi {y['kural1_arka_plan_kaymasi']['alt_kuyruk_red']}.",
         f"2. H1 ve ters çevrim üst kuyrukta red: {y['kural2_H1_ve_ters_ust_red']['uygulanir']}."
         + (f" → \"{y['kural2_H1_ve_ters_ust_red']['metin']}\"" if y['kural2_H1_ve_ters_ust_red']['metin'] else ""),
         f"3. (H0 ya da ters yön notu) ve ters çevrim alt kuyrukta red: "
         f"{y['kural3_H0_ya_da_ters_yon_ve_ters_alt_red']['uygulanir']}."
         + (f" → \"{y['kural3_H0_ya_da_ters_yon_ve_ters_alt_red']['metin']}\""
            if y['kural3_H0_ya_da_ters_yon_ve_ters_alt_red']['metin'] else ""),
         f"4. Hükmün adı \"sessiz taraf\". Koşul (i) u/L iki yarıda oran > 0,5: {y['kural4_ad']['kosul_i_u_L_iki_yarida_oran_gt_0_5']}; "
         f"koşul (ii) ağırlık merkezi X/K ≥ 0,6: {y['kural4_ad']['kosul_ii_agirlik_X_K_ge_0_6']}. "
         f"H1 yorumu: {y['kural4_ad']['H1_yorumu'] or '— (hüküm H1 değil)'}.",
         f"- §4 öncelik: karar yalnız binomla. "
         + (f"\"{y['s4_oncelik']['metin']}\". " if y['s4_oncelik']['metin'] else "")
         + f"ETAS satırları sıfırı dışlıyor mu: {y['s4_oncelik']['etas_satirlari_sifiri_dislar']}; "
           f"arka plan kuralına tabi okuma: {y['s4_oncelik']['etas_okumasi_arka_plan_kuralina_tabi']}.",
         f"- §8 aktarım adayı: {y['s8_aktarim_adayi']}.", "",
         "## Log skorlar (§4; nat, küme bootstrap'i 10 000, tohum 20261111, %95 yüzdelik)", "",
         "| Satır | Fark | %95 aralık | Sıfırı içerir |", "|---|---|---|---|"]
    for a, t in (("bosluk_eksi_taban", "Boşluk − taban"), ("etas_eksi_taban", "ETAS − taban"),
                 ("bosluk_eksi_etas", "Boşluk − ETAS")):
        v = ls[a]
        L.append(f"| {t} | {v['fark_nat']:+.3f} | [{v['aralik_95'][0]:+.3f}, {v['aralik_95'][1]:+.3f}] | "
                 f"{'evet' if v['sifiri_icerir'] else 'hayır'} |")
    t = ls["toplamlar_nat"]
    L += ["", f"Toplam log skor: taban {t['taban']:.3f}, boşluk {t['bosluk']:.3f}, ETAS {t['etas']:.3f}.", "",
          "## Bilgi satırları (§5; hükmü değiştirmez)", ""]
    u = b["1_u_L"]
    L.append(f"1. u/L medyanı {u['medyan']:.3f}. Altı: {_xks(u['alt'])}. Üstü: {_xks(u['ust'])}."
             + (f" Medyana eşit: {u['medyana_esit']}." if u["medyana_esit"] else ""))
    L.append(f"2. Ağırlık merkezi tanımı: {_xks(b['2_agirlik_merkezi'])}.")
    L.append(f"3. Zayıf düzlem (> 30°) var: {_xks(b['3_zayif_duzlem']['var'])}; yok: {_xks(b['3_zayif_duzlem']['yok'])}.")
    L.append(f"4. Aday ≥ 3: {_xks(b['4_aday_ge3']['var'])}; aday < 3: {_xks(b['4_aday_ge3']['yok'])}.")
    L.append(f"5. Büyük olay gölgesindekiler dışlanınca: {_xks(b['5_golge_disli'])}.")
    L.append(f"6. Ters yön notu (X ≤ 14): {'düşülür (§3 arka plan kuralına tabi)' if b['6_ters_yon_notu'] else 'düşülmez'}.")
    L.append("7. Türkiye (yalnız anılır): " + ", ".join(f"{k['kume']} {k['birincil_id']} isabet {k['isabet']}"
                                                   for k in b["7_turkiye"]) + ".")
    z = b["8_zaman_ters_cevrimi"]
    L.append(f"8. Zaman ters çevrimi: K_ters = {z['K']}, X_ters = {z['X']}, oran {_f(z['oran'])}; "
             f"P(X ≥ X_ters | 0,5) = {_f(z['ust_kuyruk_p'], 4)}, P(X ≤ X_ters | 0,5) = {_f(z['alt_kuyruk_p'], 4)}.")
    L.append(f"9. Çift/öncü dışlanınca: {_xks(b['9_cift_oncu_disli'])}.")
    ag10 = b["10_alt_gruplar"]
    L.append(f"10. Sonraki |s|/L ≤ 1: {_xks(ag10['sonraki_s_le_L']['grup'])} (tümleyen {_xks(ag10['sonraki_s_le_L']['tumleyen'])}); "
             f"sonraki M ≥ Mw: {_xks(ag10['sonraki_m_ge_mw']['grup'])} (tümleyen {_xks(ag10['sonraki_m_ge_mw']['tumleyen'])}); "
             f"sonraki doğrultu atımlı birincil: {_xks(ag10['sonraki_ss_birincil']['grup'])} "
             f"(tümleyen {_xks(ag10['sonraki_ss_birincil']['tumleyen'])}).")
    L += ["", "## Küme satırları", "",
          "| Küme | Birincil | t0 | Mw | Sessiz | Sonraki | İsabet | Önceki | İsabet_ters | p_ETAS | u/L | zayıf | aday≥3 | gölge | çift | TR |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in r["kume_satirlari"]:
        L.append(f"| {s['kume']} | {s['birincil_id']} | {s['t0'][:10]} | {s['mw']:.1f} | {s['sessiz_isaret']:+d} | "
                 f"{s['sonraki_id']} | {s['isabet']} | {s['onceki_id'] or '—'} | {_f(s['isabet_ters'])} | "
                 f"{s['p_etas']:.3f} | {s['u_L']:.3f} | {s['zayif_duzlem']} | {s['aday_ge3']} | {s['golge']} | "
                 f"{s['cift_oncu']} | {s['tr']} |")
    L += ["", "Ağırlık merkezi tanımı (§5.2): " + ", ".join(f"{a['kume']} {a['birincil_id']} {a['isabet']}"
                                                         for a in r["agirlik_satirlari"]) + ".", ""]
    return "\n".join(L)


def main(a):
    for f in (os.path.join(a.cikti, "tr2_sonuc.json"), os.path.join(a.cikti, "tr2_sonuc.md")):
        if os.path.exists(f) and not a.uzerine_yaz:
            raise SystemExit(f"{f} zaten var: tek koşu kuralı (bilerek yinelemek için --uzerine-yaz)")
    n = sha_dogrula(a.ham, a.sha)
    man, ag, olaylar, etas = dosyalari_oku(a.ham, a.manifest, a.manifest_agirlik, a.etas)
    r = hesapla(man, ag, olaylar, etas)
    r["girdi"] = {"sha_dogrulanan_dosya": n, "manifest": os.path.basename(a.manifest),
                  "manifest_agirlik": os.path.basename(a.manifest_agirlik), "etas": os.path.basename(a.etas)}
    os.makedirs(a.cikti, exist_ok=True)
    with open(os.path.join(a.cikti, "tr2_sonuc.json"), "w") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    with open(os.path.join(a.cikti, "tr2_sonuc.md"), "w") as f:
        f.write(md_yaz(r))
    print(f"K = {r['K']}, X = {r['X']}, hüküm {r['hukum']}. Yazıldı: {a.cikti}/tr2_sonuc.json, tr2_sonuc.md")


def argumanlar(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--ham", required=True, help="açılmış anlık görüntünün ham/ dizini")
    ap.add_argument("--manifest", default=os.path.join(BURA, "tr2_manifest.csv"))
    ap.add_argument("--manifest-agirlik", default=os.path.join(BURA, "tr2_manifest_agirlik.csv"))
    ap.add_argument("--sha", default=os.path.join(BURA, "tr2_ham_sha256.txt"))
    ap.add_argument("--etas", default=os.path.join(BURA, "tr2_etas_p.csv"))
    ap.add_argument("--cikti", default=BURA)
    ap.add_argument("--uzerine-yaz", action="store_true")
    return ap.parse_args(argv)


if __name__ == "__main__":
    main(argumanlar())
