#!/usr/bin/env python3
"""TR-13d 0 € KATALOG VARLIĞI SAYIMI — aday çıkarımı (yalnız TR-13'ün yayımlı satırlarından; yeni sorgu yok).

Aday = TR-13 ana şoku (sayim4 = ham/sayim_tam_satirlar.json, 1175 satır), M >= 6,0, temiz önce-pencere
(oncu_M6_kirli yanlış), TR-13b'nin 14 ön kayıt kümesinde DEĞİL ve TR-13 sayımında düşmüş:
  (A) "arka plan yetersiz": N3bg_en_iyi[mc] < 50 ya da yok (Mc kestirilemedi), ya da
  (B) "referans geçmiyor": N3bg >= 50 ama tr13_tamsayim.json ref_gecer["0.3"] yanlış.
TR-13c'nin geçen 5 kümesi (847, 854, 910, 911, 1137) ayrıca işaretlenir.
Bölge: dış merkez koordinatından sabit kutu sırasıyla (ilk eşleşen). Yerelleşme ölçüsü YOK.

Kullanım: python3 -I -B tr13d_aday.py <sayim4.json> <cikti.json>
"""
import collections
import json
import os
import sys

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
TAMSAYIM = os.path.join(BURA, "..", "tr13", "tr13_tamsayim.json")
TR13B_KUME = {397, 160, 303, 395, 1141, 689, 727, 802, 901, 942, 979, 1139, 1035, 1144}
TR13C_KUME = {847, 854, 910, 911, 1137}
MARMARA = (39.5, 42.0, 26.0, 31.5)

# (ad, [(enlem_min, enlem_max, boylam_min, boylam_max), ...]) — sırayla, ilk eşleşen
BOLGE = [
    ("Tayvan", [(21.0, 26.0, 119.0, 122.5)]),
    ("Japonya", [(24.0, 46.0, 122.5, 150.0), (20.0, 24.0, 122.5, 126.0)]),
    ("Kanada (BC)", [(46.0, 55.0, -135.0, -122.0)]),
    ("Alaska", [(50.0, 72.0, -180.0, -129.0), (50.0, 60.0, 165.0, 180.0)]),
    ("Kaliforniya", [(32.0, 42.0, -127.0, -114.0)]),
    ("ABD iç batı", [(36.0, 49.0, -122.0, -104.0)]),
    ("Meksika", [(14.0, 32.0, -118.0, -86.0)]),
    ("Karayip", [(16.5, 23.0, -88.0, -57.0), (10.0, 16.5, -62.0, -57.0)]),
    ("Orta Amerika", [(7.0, 16.5, -93.0, -77.0)]),
    ("Kuzey And", [(-5.0, 13.0, -82.0, -59.0)]),
    ("Peru-Bolivya", [(-18.0, -5.0, -82.0, -60.0)]),
    ("Şili-Arjantin", [(-56.0, -18.0, -76.0, -62.0)]),
    ("İzlanda", [(62.5, 67.5, -25.0, -12.0)]),
    ("Svalbard-Jan Mayen", [(70.0, 82.0, -15.0, 35.0)]),
    ("İtalya-Adriyatik", [(36.0, 47.5, 6.0, 19.0)]),
    ("Yunanistan-Ege", [(34.0, 42.0, 19.0, 26.0)]),
    ("Türkiye", [(36.0, 42.5, 26.0, 45.0)]),
    ("İran-Kafkas", [(25.0, 44.0, 44.0, 63.5)]),
    ("Orta Asya", [(35.0, 46.0, 63.5, 80.0)]),
    ("Myanmar", [(9.0, 28.0, 92.0, 98.5)]),
    ("Çin-Tibet-Moğolistan", [(20.0, 50.0, 80.0, 125.0), (46.0, 52.0, 85.0, 120.0)]),
    ("Altay-Sayan-Baykal", [(48.0, 58.0, 80.0, 120.0)]),
    ("Yeni Zelanda", [(-52.0, -34.0, 160.0, 180.0), (-52.0, -34.0, -180.0, -175.0)]),
    ("Filipinler", [(4.5, 21.0, 116.0, 128.0)]),
    ("Endonezya-Timor", [(-12.0, 6.0, 94.0, 142.0)]),
    ("PNG-Solomon", [(-13.0, 0.0, 142.0, 163.0)]),
    ("GB Pasifik adaları (Vanuatu-Fiji-Tonga-Kermadec)", [(-35.0, -10.0, 163.0, 180.0), (-35.0, -10.0, -180.0, -170.0)]),
    ("Mariana-Mikronezya", [(0.0, 24.0, 142.0, 150.0)]),
    ("Kamçatka-Kuril", [(44.0, 62.0, 150.0, 165.0)]),
    ("Avustralya", [(-45.0, -10.0, 112.0, 155.0)]),
    ("Afrika-Arabistan", [(-35.0, 37.0, -18.0, 60.0)]),
]


def bolge(la, lo):
    for ad, kutular in BOLGE:
        for a, b, c, d in kutular:
            if a <= la <= b and c <= lo <= d:
                return ad
    return "okyanus/diğer"


def marmara(la, lo):
    a, b, c, d = MARMARA
    return a <= la <= b and c <= lo <= d


def main(s4yol, cikti):
    S = json.load(open(s4yol))["satir"]
    tam = {s["id"]: s for s in json.load(open(TAMSAYIM))["satir"]}
    out = []
    for s in S:
        if s["M"] < 6.0 or s["oncu_M6_kirli"] or s["kume"] in TR13B_KUME:
            continue
        n = s["N3bg_en_iyi"]["mc"]
        if n is None or n < 50:
            neden = "A: arka plan yetersiz (N3bg < 50 ya da Mc yok)"
        elif s["id"] in tam and not tam[s["id"]]["ref_gecer"]["0.3"]:
            neden = "B: referans geçmiyor (tol 0,3)"
        elif s["id"] in tam and tam[s["id"]]["ref_gecer"]["0.3"]:
            continue                         # TR-13 (küresel) ile zaten geçen: TR-13c'nin konusu
        else:
            raise AssertionError(s["id"])
        out.append(dict(id=s["id"], zaman=s["zaman"], t=s["t"], M=s["M"], enlem=s["enlem"], boylam=s["boylam"],
                        derinlik=s["derinlik"], R=s["R"], R_ind=s["R_ind"], yer=s["yer"], kume=s["kume"],
                        en_iyi=s["en_iyi"], N3bg_kuresel=n, mc_kuresel=s["mc_en_iyi"], neden=neden,
                        bolge=bolge(s["enlem"], s["boylam"]), marmara=marmara(s["enlem"], s["boylam"]),
                        tr13c_kumesi=s["kume"] in TR13C_KUME, M65=s["M"] >= 6.5))
    tab = collections.defaultdict(lambda: [0, 0, set(), set()])
    for a in out:
        t = tab[a["bolge"]]
        t[0 if a["M65"] else 1] += 1
        (t[2] if a["M65"] else t[3]).add(a["kume"])
    ozet = {b: dict(olay_M65=v[0], olay_M60_65=v[1], kume_M65=len(v[2]), kume_M60=len(v[2] | v[3]))
            for b, v in sorted(tab.items(), key=lambda kv: -(kv[1][0] + kv[1][1]))}
    d = dict(kaynak="sayim4 (ham/sayim_tam_satirlar.json) + tr13_tamsayim.json", n_aday=len(out),
             n_M65=sum(a["M65"] for a in out), n_kume_M65=len({a["kume"] for a in out if a["M65"]}),
             n_kume_M60=len({a["kume"] for a in out}), bolge_ozet=ozet, aday=out)
    json.dump(d, open(cikti, "w"), indent=1, ensure_ascii=False)
    print(len(out), d["n_M65"], d["n_kume_M65"], d["n_kume_M60"])
    for b, v in ozet.items():
        print(f"{b:50s} {v}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
