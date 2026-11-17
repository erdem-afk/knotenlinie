#!/usr/bin/env python3
"""TR-13c 0 € SAYIM: M 6,0–6,49 adaylarının TR-13b §3.1–3.3 kurallarıyla yalnız SAYISI.

Kural: kayit/onkayit/TR-13c_SAYIM-KURALI.md (sayımdan önce commit edildi).
Gerçek katalogda hiçbir yerelleşme ölçüsü (V(q), Gini, z) HESAPLANMAZ. tr13b_kosu.kos() ÇAĞRILMAZ; yalnız hazırlık
işlevleri (sha_denetimi, arsiv_oku, uye_adlari, katalog, hazirla) değiştirilmeden içe aktarılır. hazirla'nın döndürdüğü
arka plan konumları hemen atılır; yalnız sayılar yazılır.

Kullanım: python3 -I -B tr13c_sayim.py ana <cikti.json>
          python3 -I -B tr13c_sayim.py ek  <ham_dizin/> <cikti_ek.json>     (ek tarama; ISC indirir)
"""
import json
import math
import os
import sys
import urllib.parse

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BURA, "..", "tr13b"))
sys.path.insert(0, os.path.join(BURA, "..", "tr13"))
import tr13b_kosu as K  # noqa: E402
import tr13_sayim as T  # noqa: E402

TR13B_KUME = {397, 160, 303, 395, 1141, 689, 727, 802, 901, 942, 979, 1139, 1035, 1144}
YOGUN_MC = 2.5
BILGI_I = ("ak995cti1ypa", "usb000m8ch", "us7000g8n3")
EK_ID = ("us7000irp8", "usp000jmcv", "usp000jqf3")


def ana_liste(S):
    return [s for s in S if 6.0 <= s["M"] < 6.5 and s["ref_gecer"]["0.3"]]


def cakisma(o, s4, tr13b):
    """Doğrudan çakışma: uzaklık <= R_i + R_j ve |dt| <= 10 y (TR-13 küme kuralının tek adımı)."""
    out = []
    for b in tr13b:
        ob = s4[b["id"]]
        d = float(T.uzak(o["enlem"], o["boylam"], np.array([ob["enlem"]]), np.array([ob["boylam"]]))[0])
        dt = abs(float(o["t"]) - float(ob["t"])) / T.YIL_MS
        if d <= float(o["R"]) + float(ob["R"]) and dt <= 10.0:
            out.append(dict(id=b["id"], yer=b["yer"], kume=b["kume"], uzaklik_km=round(d, 1), dt_y=round(dt, 2)))
    return out


def say_satirlar(L, s4, A, tr13b):
    sat = []
    for s in L:
        o = s4[s["id"]]
        assert abs(float(o["R"]) - float(s["R_km"])) < 0.05
        oz, bg = K.hazirla(s, o, K.katalog(s, A))
        del bg                                   # konumlar kullanılmaz; ölçü yok
        oz.update(M=s["M"], zaman=s["zaman"], bolge=s["bolge"], yeni_kume=s["kume"] not in TR13B_KUME,
                  yogun=(oz.get("mc_ortak") is not None and oz["mc_ortak"] <= YOGUN_MC + 1e-9),
                  dogrudan_cakisma_tr13b=cakisma(o, s4, tr13b))
        sat.append(oz)
    return sat


def ana(cikti):
    tam, sha = K.sha_denetimi(K.Yollar())
    assert tam, f"sha256 uyuşmuyor: {sha}"
    S = json.load(open(K.TAMSAYIM))["satir"]
    L = ana_liste(S)
    L_i = [s for s in S if s["id"] in BILGI_I]
    tr13b = K.ana_liste(K.TAMSAYIM)
    adlar = [a for a, _ in K.sha_listesi(K.SHA_LISTE)]
    g1, g2 = {"ham/sayim_tam_satirlar.json"}, set()
    for s in L + L_i:
        a, b = K.uye_adlari(s)
        g1.update(a); g2.update(b)
    A = {}
    A.update(K.arsiv_oku(K.ARSIV_DIZIN + adlar[0], g1))
    A.update(K.arsiv_oku(K.ARSIV_DIZIN + adlar[1], g2))
    s4 = {z["id"]: z for z in A["ham/sayim_tam_satirlar.json"]["satir"]}
    sat = say_satirlar(L, s4, A, tr13b)
    sat_i = say_satirlar(L_i, s4, A, tr13b)
    gecen = [z for z in sat if z["durum"] == "tamam"]
    yeni = [z for z in gecen if z["yeni_kume"]]
    Ka = sorted({z["kume"] for z in yeni})
    Kb = sorted({z["kume"] for z in yeni if z["yogun"]})
    out = dict(kural="kayit/onkayit/TR-13c_SAYIM-KURALI.md", sha256=sha, kod_sha256=K.kod_sha(),
               aday_sayisi=len(L), gecen_olay=len(gecen), gecen_tr13b_kumesinde=len(gecen) - len(yeni),
               yeni_gecen_olay=len(yeni), K_a=len(Ka), kumeler_a=Ka, K_b=len(Kb), kumeler_b=Kb,
               satir=sat, bilgi_i=sat_i,
               not_="Yalnız sayı. V(q), Gini, z hesaplanmadı; tr13b_kosu.kos() çağrılmadı.")
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False, default=float)
    for z in sat + sat_i:
        print(z["id"], z["yer"][:30], z["kume"], "yeni" if z["yeni_kume"] else "TR13b", z.get("mc_once"),
              z.get("mc_ref"), z.get("mc_ortak"), z.get("mc_son"), z.get("N3bg"), z.get("N_ref"), z["durum"],
              "yoğun" if z["yogun"] else "", [c["id"] for c in z["dogrudan_cakisma_tr13b"]])
    print("K_a", len(Ka), Ka, "K_b", len(Kb), Kb)


# ------------------------------------------------------------------ ek tarama (bilgi satırı ii)
def isc_daire(o, t0, t1, mmin, onb):
    assert t1 <= o["t"] and t1 <= T.BITIS_MS + 1000, "KÖRLÜK"
    q = dict(format="text", latitude=f"{o['enlem']:.4f}", longitude=f"{o['boylam']:.4f}",
             maxradius=f"{o['R'] / 111.195:.4f}", starttime=T.iso(t0), endtime=T.iso(t1 - 1000),
             minmagnitude=f"{mmin:.1f}", limit=20000)
    d = T.fdsn_text(T.getir(T.SERVIS["ISC"] + "?" + urllib.parse.urlencode(q), onb, zaman_asimi=900))
    if len(d["t"]) >= 20000:
        orta = (t0 + t1) // 2
        return T.birlestir([isc_daire(o, t0, orta, mmin, onb), isc_daire(o, orta, t1, mmin, onb)])
    return d


def mc_kural(m):
    if m.size >= 50:
        return round(T.maxc(m) + 0.2, 2)
    if m.size >= 20:
        return round(T.maxc(m) + 0.3, 2)
    return None


def ek(ham, cikti):
    ham = ham if ham.endswith("/") else ham + "/"
    A = K.arsiv_oku(K.ARSIV_DIZIN + K.sha_listesi(K.SHA_LISTE)[0][0], {"ham/sayim_tam_satirlar.json"})
    s4 = {z["id"]: z for z in A["ham/sayim_tam_satirlar.json"]["satir"]}
    tr13b = K.ana_liste(K.TAMSAYIM)
    sat = []
    for i in EK_ID:
        o = s4[i]
        assert 6.0 <= o["M"] < 6.5 and not o["oncu_M6_kirli"] and o["en_iyi"] == "ISC_ornek"
        fn = ham + f"ek_ISC_{i}.npz"
        try:
            if os.path.exists(fn):
                with np.load(fn, allow_pickle=False) as z:
                    d = {k: np.asarray(z[k]) for k in z.files}
            else:
                mmin = max(-1.0, o["kataloglar"]["ISC_ornek"]["mc"] - 0.3)
                parca = []
                for j in range(9, -1, -1):
                    t1 = int(o["t"] - j * T.YIL_MS)
                    t0 = int(o["t"] - (j + 1) * T.YIL_MS)
                    parca.append(isc_daire(o, t0, t1, mmin, ham + "onbellek_ISC"))
                d = T.birlestir(parca)
                np.savez_compressed(fn, **d)
        except RuntimeError as e:
            sat.append(dict(id=i, yer=o["yer"], kume=o["kume"], durum=f"doğrulanamadı: {e}"[:300]))
            continue
        t = o["t"]
        r = T.uzak(o["enlem"], o["boylam"], d["la"], d["lo"])
        ic = (r <= o["R"]) & (d["de"] <= T.DERIN_MAX + 10) & (d["t"] < t)
        w3 = ic & (d["t"] >= t - 3 * T.YIL_MS)
        wr = ic & (d["t"] < t - 3 * T.YIL_MS) & (d["t"] >= t - 10 * T.YIL_MS)
        mc0, mcr = mc_kural(d["m"][w3]), mc_kural(d["m"][wr])
        oz = dict(id=i, yer=o["yer"], kume=o["kume"], M=o["M"], R=o["R"], n_indirilen=int(len(d["t"])),
                  mc_once=mc0, mc_ref=mcr, yeni_kume=o["kume"] not in TR13B_KUME)
        if mc0 is None or mcr is None:
            oz["durum"] = "düşer: Mc kestirilemedi (< 20 olay)"
            sat.append(oz)
            continue
        # TR-13 Ek 1 referans şartı (GK74 referans penceresinde, R dairesi)
        sec = (d["t"] < t - 3 * T.YIL_MS) & (d["t"] >= t - 10 * T.YIL_MS)
        dd = {k: v[sec] for k, v in d.items()}
        bgr = T.gk74(dd["t"], dd["la"], dd["lo"], dd["m"])
        icr = (T.uzak(o["enlem"], o["boylam"], dd["la"], dd["lo"]) <= o["R"]) & (dd["de"] <= T.DERIN_MAX + 10)
        nref0 = int((icr & bgr & (dd["m"] >= mc0 - 1e-6)).sum())
        oz["N_ref_bg_mc_once"] = nref0
        gec03 = mcr <= mc0 + 0.3 and nref0 >= 100
        oz["ref_gecer_0.3"] = bool(gec03)
        # §3.1–3.3 (tr13b_kosu.hazirla ile aynı adımlar; s satırı tamsayım biçiminde kurulur)
        s = dict(id=i, yer=o["yer"], kume=o["kume"], R_km=o["R"], katalog="ISC", mc_once=mc0, ref_tam=dict(mc=mcr))
        oz2, bg = K.hazirla(s, o, {k: np.asarray(v, float) for k, v in d.items()})
        del bg
        oz.update({k: v for k, v in oz2.items() if k not in oz})
        if not gec03:
            oz["durum"] = "ana listeye girmez: referans şartı (tol 0,3) sağlanmıyor; §3 sayısı: " + oz2["durum"]
        oz["yogun"] = oz2.get("mc_ortak") is not None and oz2["mc_ortak"] <= YOGUN_MC + 1e-9
        oz["dogrudan_cakisma_tr13b"] = cakisma(o, s4, tr13b)
        sat.append(oz)
    json.dump(dict(kural="TR-13c_SAYIM-KURALI.md §4 (ii)", satir=sat), open(cikti, "w"), indent=1,
              ensure_ascii=False, default=float)
    for z in sat:
        print(json.dumps(z, ensure_ascii=False, default=float))


if __name__ == "__main__":
    if sys.argv[1] == "ana":
        ana(sys.argv[2])
    elif sys.argv[1] == "ek":
        ek(sys.argv[2], sys.argv[3])
