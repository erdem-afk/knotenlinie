#!/usr/bin/env python3
"""TR-13d özet: sayım satırlarını birleştirir, bölge tablosu ve yeni K'yi kurar (yalnız sayı; ölçü yok).

Kullanım: python3 -I -B tr13d_ozet.py <aday.json> <cikti.json> <sayim_parca.json> [...]
"""
import collections
import json
import sys

sys.dont_write_bytecode = True
TR13B_KUME = {397, 160, 303, 395, 1141, 689, 727, 802, 901, 942, 979, 1139, 1035, 1144}
TR13C_KUME = {847, 854, 910, 911, 1137}
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from tr13d_sayim import BOLGE_KATALOG, COMCAT_ZATEN, ERISILEMEZ  # noqa: E402


def sinif(d):
    for a, b in (("tamam", "geçti"), ("düşer: ön eleme", "düştü: önce-pencerede toplam < 50"),
                 ("düşer: N3bg", "düştü: N3bg < 50"), ("düşer: referans", "düştü: referans < N3bg + 5"),
                 ("düşer: Mc", "düştü: Mc kestirilemedi"), ("düşer: önce-pencerede parça", "düştü: veri yok (403/eksik)"),
                 ("düşer: katalog", "düştü: katalog dönemi kapsamıyor")):
        if d.startswith(a):
            return b
    return d


def main(aday_yol, cikti, parcalar):
    A = json.load(open(aday_yol))["aday"]
    sat = {}
    for p in parcalar:
        for z in json.load(open(p))["satir"]:
            sat[z["id"]] = z
    tab = collections.OrderedDict()
    for a in A:
        b = a["bolge"]
        if b not in tab:
            tab[b] = dict(aday_olay=0, aday_olay_M65=0, aday_kume=set(), aday_kume_M65=set(), sayilan=0,
                          gecen_olay=[], gecen_kume=set(), gecen_kume_M65=set(), gecen_s2_kume=set(),
                          katalog=set(), durum=collections.Counter())
        t = tab[b]
        t["aday_olay"] += 1
        t["aday_kume"].add(a["kume"])
        if a["M65"]:
            t["aday_olay_M65"] += 1
            t["aday_kume_M65"].add(a["kume"])
        z = sat.get(a["id"])
        if z is None:
            if b in COMCAT_ZATEN:
                t["durum"]["ComCat zaten bölgesel ağı içeriyor (TR-13 sonucu aynen)"] += 1
            elif b in BOLGE_KATALOG:
                t["durum"]["erişilemedi: " + "; ".join(k for k in BOLGE_KATALOG[b] if k in ERISILEMEZ)] += 1
            else:
                t["durum"]["açık bölgesel katalog yok / denenmedi"] += 1
            continue
        t["sayilan"] += 1
        t["katalog"].add(z["katalog"])
        t["durum"][sinif(z["durum"])] += 1
        if z["durum"] == "tamam":
            t["gecen_olay"].append(a["id"])
            t["gecen_kume"].add(a["kume"])
            if a["M65"]:
                t["gecen_kume_M65"].add(a["kume"])
            if z.get("s2_suzgeci"):
                t["gecen_s2_kume"].add(a["kume"])
    gecen = [sat[i] for b in tab.values() for i in b["gecen_olay"]]
    kume_M60 = sorted({z["kume"] for z in gecen})
    kume_M65 = sorted({z["kume"] for z in gecen if z["M"] >= 6.5})
    assert not set(kume_M60) & TR13B_KUME
    for z in gecen:
        assert not z.get("cakisma_tr13b"), z["id"]
    yeni_M60_haric_c = sorted(set(kume_M60) - TR13C_KUME)
    out = dict(
        kural="kayit/onkayit/TR-13d_SAYIM-KURALI.md",
        K_birincil_M65=len(kume_M65), kumeler_M65=kume_M65,
        K_ikincil_M60=len(kume_M60), kumeler_M60=kume_M60,
        K_ikincil_M60_TR13c_disi=len(yeni_M60_haric_c),
        K_ikincil_birlesik_TR13c=len(set(kume_M60) | TR13C_KUME),
        K_s2_suzgeciyle_M65=len({z["kume"] for z in gecen if z["M"] >= 6.5 and z.get("s2_suzgeci")}),
        K_s2_suzgeciyle_M60=len({z["kume"] for z in gecen if z.get("s2_suzgeci")}),
        bolge={b: dict(aday_olay=v["aday_olay"], aday_olay_M65=v["aday_olay_M65"], aday_kume=len(v["aday_kume"]),
                       aday_kume_M65=len(v["aday_kume_M65"]), sayilan_olay=v["sayilan"],
                       katalog=sorted(v["katalog"]), gecen_olay=len(v["gecen_olay"]),
                       gecen_kume=len(v["gecen_kume"]), gecen_kume_M65=len(v["gecen_kume_M65"]),
                       durum=dict(v["durum"])) for b, v in tab.items()},
        gecenler=[{k: z.get(k) for k in ("id", "yer", "zaman", "M", "bolge", "kume", "R", "katalog", "mc_once",
                                         "mc_ref", "mc_ortak", "mc_son", "N3bg", "N_ref", "s2_suzgeci",
                                         "N_ref_bg_mc_once", "neden_tr13", "N3bg_kuresel", "tr13c_kumesi",
                                         "marmara", "mag")} for z in gecen],
        satir=list(sat.values()),
        erisilemez=ERISILEMEZ,
        not_="Yalnız sayı. V(q), Gini, z hesaplanmadı; tr13b_kosu.kos() çağrılmadı.")
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False, default=float)
    print("K M>=6,5:", len(kume_M65), kume_M65, " K M>=6,0:", len(kume_M60), kume_M60,
          " TR-13c dışı:", len(yeni_M60_haric_c), " birleşik:", out["K_ikincil_birlesik_TR13c"],
          " §2 ile:", out["K_s2_suzgeciyle_M65"], out["K_s2_suzgeciyle_M60"])
    for b, v in out["bolge"].items():
        print(f"{b:45s} aday {v['aday_olay']:3d}/{v['aday_kume']:3d} (M6,5 {v['aday_olay_M65']}/{v['aday_kume_M65']}) "
              f"sayılan {v['sayilan_olay']:2d} {','.join(v['katalog']):10s} geçen {v['gecen_olay']}/{v['gecen_kume']} "
              f"(M6,5 küme {v['gecen_kume_M65']})  {v['durum']}")
    for z in out["gecenler"]:
        print(z)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
