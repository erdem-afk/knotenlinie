"""TR-6a sınama tanısı (yalnız yapay veri; bağlayıcı tohum KULLANILMAZ).
(i) Δτ = 0, lobda saf Poisson: aynı katalog gerçekleşmesinde gölge düşüş oyu birkaç sayım biçimiyle (eşli):
  V0 hat (tr6a_kosu.Analiz, §3.6 pencereleri; tr6a_yapay.TekBirimSinama.deneme ile aynı yol, sahte yok)
  V1 kümesizleştirme yok (D4 biçimi)
  V2 son katalog t0 − 730 g'de başlar (son pencerenin önüne ön pencereyle aynı 730 g tampon), bitiş aynı
  V3 tek sürekli katalog [t0 − 3621, t0 + 400) bir kez kümesizleştirilir; iki pencere ondan sayılır (kenar yok)
  V4 V2 + iki pencerenin sonuna 35 g veri (ön: t0 − 30 → t0 + 5; son: t0 + 365 → t0 + 400) -- yalnız son kenar
Kullanım: python3 -I -B tr6a_tani_kumesiz.py TOHUM N N0 [N0 ...] > çıktı.json
"""
import json
import math
import os
import sys
import time

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6a_yapay as Y            # noqa: E402
import tr6a_kosu as KO            # noqa: E402
import tr6a_katalog as KAT        # noqa: E402
import tr6a_onkayit_sayilar as S  # noqa: E402

YASAK = (20261114, 20261115)


def deneme(T, rng, N0):
    """TekBirimSinama.deneme ile aynı adımlar (sahte=False), dünya nesnesini de döndürür."""
    d = Y.YapayDunya.__new__(Y.YapayDunya)
    sp = dict(N0=N0, dtau="sifir", ikincil_bolge=True)
    d.liste, d.rng, d.spec = T.liste, rng, {T.u: dict(sp, mekanizma=T.mek)}
    d.birim, d.olay, d.ffm, d.tensor = T.d0.birim, T.d0.olay, T.d0.ffm, T.d0.tensor
    d.geo, d.cache = T.d0.geo, {}
    an, B = T.an, T.B
    B["kat"] = {}
    B["durum"] = "hazır"
    an.kaynak = Y.YapayKaynak(d, "on")
    an.son_eklendi = False
    an.on_katalog()
    an.katalog_secimi()
    k = B["secim"]
    kp = B["kapi"][k]["golge"]
    plan = [dict(birim=T.u, katalog=k, t_bas=KAT.zaman(B["t0"]).isoformat(timespec="milliseconds"),
                 t_bit=KAT.zaman(B["son_bit"]).isoformat(timespec="milliseconds"), taban=B["kat"][k]["taban"],
                 R_km=B["R_sorgu"], merkez=[B["la"], B["lo"]])]
    an.son_ekle(plan, Y.YapayKaynak(d, "son"))
    P = an.pencere(B, "gercek")
    ms, _ = an.mc_son(B, k, P, kp["mc_lob"])
    mk = KO.mc_kul(kp["mc_lob"], ms)
    o = an.lob_oyu(B, k, "golge", P, mk)
    return d, k, P, mk, o, kp


def say_tek(E, ev, mk, kat_a, kat_b, a, b):
    k = ev & KAT.ust(E["m"], mk) & (E["t"] >= kat_a) & (E["t"] < kat_b)
    return KAT._say(E, k, a, b, True)


def main():
    tohum, n = int(sys.argv[1]), int(sys.argv[2])
    N0lar = [float(x) for x in sys.argv[3:]]
    assert tohum not in YASAK and tohum + 1 not in YASAK
    T = Y.TekBirimSinama(M=7.8)
    B, an, u = T.B, T.an, T.u
    pi = B["pi"]
    oy = S.Oy(40000)
    t0 = B["t0"]
    out = dict(tohum=tohum, n=n, pi=pi, lob_hucre=int(B["M"]["golge"].sum()), sonuc={})
    for N0 in N0lar:
        rng = np.random.default_rng([tohum, int(round(N0 * 100))])
        kay = {v: dict(D=[], n_on=[], n_son=[]) for v in ("V0", "V1", "V2", "V3", "V4")}
        mcs, bas = [], time.time()
        for i in range(n):
            d, k, P, mk, o, kp = deneme(T, rng, N0)
            mcs.append(mk)
            E = B["kat"][k]["E"]
            ev = KO.ev_maske(E, B["M"]["golge"])
            (a, b), (s, e) = P["on"], P["son"]
            # tam (kesintisiz) katalog, aynı gerçekleşme
            dd = d.olaylar(u, k)
            F, _ = an._olaylari_yerlestir(B, dd, B["kat"][k]["taban"])
            evF = KO.ev_maske(F, B["M"]["golge"])
            v = {}
            v["V0"] = (o["n_on"], o["n_son"])
            v["V1"] = KAT.pencere_sayisi(E, ev, dict(on=P["on"], son=P["son"], son_katalog=P["son_katalog"]), mk,
                                         kumesiz=False)
            v["V2"] = (o["n_on"], say_tek(F, evF, mk, t0 - 730.0, e, s, e))
            # V3: tek sürekli katalog
            kF = evF & KAT.ust(F["m"], mk)
            idx = np.nonzero(kF)[0]
            bag = KAT.kumesizlestir(F["t"][idx], F["la"][idx], F["lo"][idx], F["m"][idx])
            tt = F["t"][idx][bag]
            v["V3"] = (int(((tt >= a) & (tt < b)).sum()), int(((tt >= s) & (tt < e)).sum()))
            v["V4"] = (say_tek(F, evF, mk, a - KAT.TAMPON_G, b + 35.0, a, b),
                       say_tek(F, evF, mk, t0 - 730.0, e + 35.0, s, e))
            for kk, (x, y) in v.items():
                kay[kk]["n_on"].append(x)
                kay[kk]["n_son"].append(y)
                kay[kk]["D"].append(KAT.oy(x, y, pi)[0])
        bek = oy.olasilik(N0 * S.T_ON_G / 365.25, N0 * S.T_SON_G / 365.25, -1)
        r = dict(beklenen_poisson=round(bek, 5), sure_s=round(time.time() - bas, 1),
                 mc_kul=sorted(set(float(x) for x in mcs)))
        D0 = np.array(kay["V0"]["D"], float)
        for kk, x in kay.items():
            D = np.array(x["D"], float)
            no, ns = np.array(x["n_on"], float), np.array(x["n_son"], float)
            nn = no + ns
            res = ns - pi * nn                       # H0'da beklenen 0
            Neff = no.mean() / (S.T_ON_G / 365.25)
            bek_eff = oy.olasilik(Neff * S.T_ON_G / 365.25, Neff * S.T_SON_G / 365.25, -1)
            fark = D - D0
            r[kk] = dict(P_D=round(D.mean(), 5), se=round(D.std(ddof=1) / math.sqrt(n), 5),
                         z_poisson=round((D.mean() - bek) / math.sqrt(bek * (1 - bek) / n), 2),
                         esli_fark_V0dan=round(fark.mean(), 5),
                         esli_fark_se=round(fark.std(ddof=1) / math.sqrt(n), 5),
                         ort_n_on=round(no.mean(), 2), ort_n_son=round(ns.mean(), 3),
                         oran_son_on_bolu_T=round((ns.mean() / S.T_SON_G) / (no.mean() / S.T_ON_G), 5),
                         artik_ort=round(res.mean(), 3), artik_se=round(res.std(ddof=1) / math.sqrt(n), 3),
                         N_etkin=round(Neff, 2), beklenen_poisson_N_etkin=round(bek_eff, 5),
                         silinen_pay_on=round(1 - no.mean() / np.mean(kay["V1"]["n_on"]), 4),
                         silinen_pay_son=round(1 - ns.mean() / np.mean(kay["V1"]["n_son"]), 4))
        out["sonuc"][f"{N0:g}"] = r
        print(f"N0 {N0:g}: " + json.dumps(r, ensure_ascii=False), file=sys.stderr, flush=True)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
