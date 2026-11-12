"""İNCELEME-2 b4 (bağımsız denetim), depo yollarıyla yeniden yazım (özgün betik scipy kullanmıyordu; yalnız yollar).

Dondurulan listeden (yalnız havuz üstverisi): sahte geçerlilik ölçütünün 3 L_A ve 4 L_A ile J'si, geçersiz sahte
zamanların örtüşen olayları ve gerçek ön pencerenin son yılında [t0 − 365 g, t0) 3 L_A + 3 L_temsilci içinde havuz
olayı olan temsilciler ("öncül komşu", B2). Gerçek veri okumaz.
Kullanım: python3 -I -B tr6a_inc2_b4.py
"""
import datetime as dt, json, math, os

BURAYA = os.path.dirname(os.path.abspath(__file__))
T = dt.datetime.fromisoformat


def km(a, b):
    p1, p2 = math.radians(a["enlem"]), math.radians(b["enlem"])
    c = math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(math.radians(b["boylam"] - a["boylam"]))
    return 6371 * math.acos(max(-1, min(1, c)))


def main():
    L = json.load(open(os.path.join(BURAYA, "tr6a_olay_listesi.json"), encoding="utf-8"))
    d = json.load(open(os.path.join(BURAYA, "tr6a_onkayit_sayilar.json"), encoding="utf-8"))
    bi = {b["id"]: b for b in L["birimler"]}
    kl = d["onsayim"]["19"]["kumeler"]
    for kat in (3, 4):
        J = 0
        out = []
        for c in kl:
            b = bi[c[0]["id"]]
            t0 = T(b["zaman"])
            kay = T(b["t_s"]) - t0
            g = 0
            for j in (1, 2, 3):
                tj = t0 - dt.timedelta(days=395 + 335 * (j - 1))
                s0, s1 = tj + kay + dt.timedelta(days=30), tj + dt.timedelta(days=365)
                ok = True
                for x in L["olaylar"]:
                    if x["grup"] == b["id"]:
                        continue
                    tx = T(x["zaman"])
                    if tx < s1 and tx + dt.timedelta(days=365) > s0 and km(b, x) < kat * x["L_km"] + 3 * b["L_km"]:
                        ok = False
                g += ok
            J += g
            out.append((b["id"], g, round(c[0]["N0"], 1)))
        print(kat, "L_A + 3 L_temsilci: J =", J, [o for o in out if o[1] < 3])
    for c in kl:
        b = bi[c[0]["id"]]
        for s in b["sahte"]:
            if not s["gecerli"]:
                print("geçersiz sahte:", b["id"], s["j"], s["ortusen"])
    print("--- öncül komşu: [t0 − 365 g, t0) içinde, < 3 L_A + 3 L_temsilci")
    for c in kl:
        b = bi[c[0]["id"]]
        t0 = T(b["zaman"])
        nb = [x["id"] for x in L["olaylar"] if x["grup"] != b["id"] and
              t0 - dt.timedelta(days=365) <= T(x["zaman"]) < t0 and km(b, x) < 3 * x["L_km"] + 3 * b["L_km"]]
        if nb:
            print(b["id"], nb)


if __name__ == "__main__":
    main()
