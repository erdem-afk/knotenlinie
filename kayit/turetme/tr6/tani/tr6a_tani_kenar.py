"""TR-6a sınama tanısı: kümesizleştirmenin "gelecek kesmesi" kenar etkisi (yalnız yapay veri; bağlayıcı tohum yok).
Aynı Δτ = 0 dünyasında (lob saf Poisson), olay öncesi dönemin içinde 335 g'lük bir pencere W = [t0 − 1100, t0 − 765)
alınır; önünde 730 g tampon vardır. Katalog W'nin sonundan sonra g_son gün (0, 35, 100, 335) daha uzatılıp gölge lobu
kümesizleştirilir; W'de silinen pay ölçülür. Karşılaştırma: 1796 g'lük ön pencere [t0 − 1826, t0 − 30) (sonrası 0 g).
Kullanım: python3 -I -B tr6a_tani_kenar.py TOHUM N N0"""
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


def main():
    tohum, n, N0 = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
    assert tohum not in (20261114, 20261115)
    T = Y.TekBirimSinama(M=7.8)
    B, an, u = T.B, T.an, T.u
    t0 = B["t0"]
    rng = np.random.default_rng([tohum, int(N0)])
    W = (t0 - 1100.0, t0 - 765.0)
    ekler = (0.0, 35.0, 100.0, 335.0)
    ham, kal = [], {g: [] for g in ekler}
    on_ham, on_kal = [], []
    for _ in range(n):
        d, k, P, mk, o, kp = deneme(T, rng, N0)
        F, _ = an._olaylari_yerlestir(B, d.olaylar(u, k), B["kat"][k]["taban"])
        ev = KO.ev_maske(F, B["M"]["golge"]) & KAT.ust(F["m"], mk)
        ham.append(int((ev & (F["t"] >= W[0]) & (F["t"] < W[1])).sum()))
        for g in ekler:
            kk = ev & (F["t"] >= W[0] - KAT.TAMPON_G) & (F["t"] < W[1] + g)
            kal[g].append(KAT._say(F, kk, W[0], W[1], True))
        a, b = P["on"]
        kk = ev & (F["t"] >= a - KAT.TAMPON_G) & (F["t"] < b)
        on_ham.append(int((kk & (F["t"] >= a)).sum()))
        on_kal.append(KAT._say(F, kk, a, b, True))
    h = np.array(ham, float)
    out = dict(tohum=tohum, n=n, N0=N0, pencere_W=[-1100, -765], ham_ort=round(h.mean(), 2),
               on_pencere_silinen_pay=round(1 - np.mean(on_kal) / np.mean(on_ham), 5), W={})
    for g in ekler:
        x = np.array(kal[g], float)
        s = h - x
        out["W"][f"sonra_{g:g}g"] = dict(silinen_pay=round(s.sum() / h.sum(), 5),
                                        silinen_ort=round(s.mean(), 3), se=round(s.std(ddof=1) / math.sqrt(n), 3))
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
