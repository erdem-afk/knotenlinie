#!/usr/bin/env python3
"""TR-13 özet: sayım tablosu (K) ve güç çıktılarını tek json'a toplar.

Kullanım: python3 -I -B tr13_ozet.py <sayim.json> <guc_gk_a.json> <guc_gk_b.json> <guc_kahin_a.json>
          <guc_gk_oncesi.json> <cikti_ozet.json>
"""
import json
import sys

sys.dont_write_bytecode = True

ESIKLER = [25, 50, 100, 200]
MC_SEC = ["mc", "mc05", "m30", "m40"]


def main(a):
    D = json.load(open(a[0]))
    S = D["satir"]
    tablo = {}
    for Mmin in (6.0, 6.5):
        for et in MC_SEC:
            for thr in ESIKLER:
                ok = [z for z in S if z["M"] >= Mmin and (z["N3bg_en_iyi"][et] or 0) >= thr]
                tem = [z for z in ok if not z["oncu_M6_kirli"]]
                kon = [z for z in tem if z["kontrol_pencere_havuz"] >= 1]
                tam = [z for z in tem if z["en_iyi"] == "ComCat"]
                ek = {"mc": 0.0, "mc05": 0.5, "m30": None, "m40": None}[et]

                def ref_ok(z, tol=0.1):
                    r = z.get("ref")
                    if not r or r.get("mc_ref") is None or z["mc_en_iyi"] is None:
                        return False
                    esik_m = z["mc_en_iyi"] + ek if ek is not None else max(z["mc_en_iyi"], float(et[1:]) / 10)
                    n_ref = r.get("Nrefbg_mc05" if et == "mc05" else "Nrefbg_mc") or 0
                    return r["mc_ref"] <= esik_m + tol and n_ref >= 2 * thr
                ref = [z for z in tem if ref_ok(z)]
                refk = [z for z in ref if z["kontrol_pencere_havuz"] >= 1]
                ref3 = [z for z in tem if ref_ok(z, 0.3)]
                tablo[f"M{Mmin}|{et}|N3bg>={thr}"] = dict(
                    olay=len(ok), K=len({z["kume"] for z in ok}), K_temiz=len({z["kume"] for z in tem}),
                    K_temiz_kontrollu=len({z["kume"] for z in kon}),
                    K_temiz_yalniz_ComCat=len({z["kume"] for z in tam}),
                    K_temiz_ref=len({z["kume"] for z in ref}), K_temiz_ref_kontrollu=len({z["kume"] for z in refk}),
                    K_temiz_ref_tol03=len({z["kume"] for z in ref3}))
    gecen = [dict(id=z["id"], zaman=z["zaman"][:10], M=z["M"], yer=z["yer"], R_km=z["R"], katalog=z["en_iyi"],
                  mc=z["mc_en_iyi"], N3bg_mc=z["N3bg_en_iyi"]["mc"], N3bg_mc05=z["N3bg_en_iyi"]["mc05"],
                  oncu_M6_kirli=z["oncu_M6_kirli"], kontrol_pencere=z["kontrol_pencere_havuz"], kume=z["kume"],
                  marmara_kutusu=z["tr_marmara"], ref=z.get("ref"))
             for z in S if z["N3bg_en_iyi"]["mc"] >= 50]
    marmara = [dict(id=z["id"], zaman=z["zaman"][:10], M=z["M"], katalog=z["en_iyi"], mc=z["mc_en_iyi"],
                    N3bg=z["N3bg_en_iyi"]) for z in S if z["tr_marmara"]]
    guc = {}
    for fn in a[1:4]:
        g = json.load(open(fn))
        k = g["parametre"]["kumesizlestirme"]
        for N, d in g["duzeyler"].items():
            guc.setdefault(k, {})[N] = dict(
                N3bg_gerceklesen=round(d["N3bg_gerceklesen_ort"], 1), z0_sd=round(d["z0_sd"], 2),
                yanlis_alarm_z1645=d["yanlis_alarm_z_1645"], yanlis_alarm_z2326=d["yanlis_alarm_z_2326"],
                f_min_guc08=d["f_min_guc08"],
                d_std={f: round(v["d_std"], 2) for f, v in d["sinyal"].items()},
                guc_K20={f: round(v["guc_K"]["20"], 3) for f, v in d["sinyal"].items()})
        par = g["parametre"]
    oncesi = json.load(open(a[4]))["etas_ana_sok_oncesi"]
    out = dict(istat=D["istat"], f_bg_gk74_comcat=round(D["f_bg"], 3), ana_sok=len(S),
               kume_tum=len({z["kume"] for z in S}), tablo=tablo, gecen_N3bg_mc_50=gecen, marmara_kutusu=marmara,
               guc=guc, guc_parametre=par, etas_ana_sok_oncesi=oncesi)
    json.dump(out, open(a[5], "w"), indent=1, ensure_ascii=False)
    for k, v in tablo.items():
        print(k, v)


if __name__ == "__main__":
    main(sys.argv[1:])
