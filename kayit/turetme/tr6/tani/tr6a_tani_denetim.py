"""TR-6a sınama tanısı, yan denetimler (yalnız yapay veri; bağlayıcı tohum yok).
1) §4.3 kesin Poisson P(D) değerinin bağımsız hesabı (math.lgamma; tr6a_onkayit_sayilar.Oy kullanılmaz).
2) tr6a_katalog.kumesizlestir'in tr6_sayim.kumesizlestir (başvuru) ile eşliği: N0 500 dünyasının gölge lobu katalogları.
Kullanım: python3 -I -B tr6a_tani_denetim.py TOHUM N_ESLIK"""
import json
import math
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
sys.path.insert(0, BURA)
import tr6a_katalog as KAT        # noqa: E402
import tr6a_kosu as KO            # noqa: E402
import tr6a_yapay as Y            # noqa: E402
from tr6a_tani_kumesiz import deneme   # noqa: E402


def binom_cdf_tum(n, p):
    k = np.arange(n + 1)
    lg = np.array([math.lgamma(x + 1) for x in range(n + 1)])
    lp = lg[n] - lg - lg[::-1] + k * math.log(p) + (n - k) * math.log1p(-p)
    return np.cumsum(np.exp(lp - lp.max())) / np.exp(lp - lp.max()).sum()


def kesin_PD(N0, T_on=1796.0, T_son=335.0):
    lam = N0 * (T_on + T_son) / 365.25
    pi = T_son / (T_on + T_son)
    s = math.sqrt(lam)
    top = 0.0
    for n in range(max(1, int(lam - 10 * s)), int(lam + 10 * s) + 1):
        F = binom_cdf_tum(n, pi)
        ok = np.nonzero(F <= 0.5 + 1e-12)[0]
        if len(ok):
            top += math.exp(-lam + n * math.log(lam) - math.lgamma(n + 1)) * F[ok.max()]
    return top


def main():
    tohum, n_es = int(sys.argv[1]), int(sys.argv[2])
    assert tohum not in (20261114, 20261115)
    out = dict(kesin_PD={f"{N0:g}": round(kesin_PD(N0), 5) for N0 in (31.36, 100.0, 300.0, 500.0, 1000.0)})
    T = Y.TekBirimSinama(M=7.8)
    rng = np.random.default_rng(tohum)
    es, top = 0, 0
    for _ in range(n_es):
        d, k, P, mk, o, kp = deneme(T, rng, 500.0)
        E = T.B["kat"][k]["E"]
        ev = KO.ev_maske(E, T.B["M"]["golge"]) & KAT.ust(E["m"], mk)
        for (a, b) in ((P["on"][0] - KAT.TAMPON_G, P["on"][1]), (P["son_katalog"], P["son"][1])):
            i = np.nonzero(ev & (E["t"] >= a) & (E["t"] < b))[0]
            x = KAT.kumesizlestir(E["t"][i], E["la"][i], E["lo"][i], E["m"][i])
            y = KAT.kumesizlestir_basvuru(E["t"][i], E["la"][i], E["lo"][i], E["m"][i])
            es += int(np.array_equal(np.asarray(x, bool), np.asarray(y, bool)))
            top += 1
    out["kumesizlestir_eslik"] = dict(esit=es, toplam=top)
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
