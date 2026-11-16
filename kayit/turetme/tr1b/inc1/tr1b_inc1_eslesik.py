#!/usr/bin/env python3
"""TR-1b INCELEME-1 ek: yerinde kaydırılmış plasebo ile eşli işaret çevirme sınamasının MDE'si. YALNIZ YAPAY VERİ.

Öneri: plasebo penceresi olay penceresinin 730 g geriye kaydırılmışı (w1_p = H). Aynı yer, aynı istasyonlar.
Model: küme başına σ_c (katman log-normal; tr1b_inc1.json'daki katman uyumu), olay ve plasebo aynı σ_c'yi paylaşır
(bölge şişmesi c her ikisinde aynı, bu yüzden sınamada sadeleşir). Ortak segment bağımlılığı modellenmez (bilgi).
İstatistik: d_k = log(S_olay,k / S_plasebo,k), ortalama d; tek yanlı kesin işaret çevirme (2^K desen), α = 0,05.
Kullanım: python3 -I -B tr1b_inc1_eslesik.py <tr1b_inc1.json> <cikti.json>
"""
import itertools
import json
import sys

import numpy as np

sys.dont_write_bytecode = True
KAT = [(3, 4), (5, 7), (8, 8)]
PK = np.array([213, 253, 199]) / 665


def S_iki(rng, n, prm, g, dagin):
    kat = rng.choice(3, n, p=PK)
    mu = np.array([prm[k][0] for k in kat])
    tau = np.array([prm[k][1] for k in kat])
    lo = np.array([KAT[k][0] for k in kat])
    hi = np.array([KAT[k][1] for k in kat])
    ny = lo + (rng.random(n) * (hi - lo + 1)).astype(int)
    sig = np.exp(mu + tau * rng.standard_normal(n))
    out = []
    for gg in (g, 0.0):
        w = rng.standard_normal((n, 8, 2)) * sig[:, None, None]
        if gg:
            a = rng.random((n, 8)) if dagin else np.ones((n, 8))
            w[:, :, 0] += gg * a
        r = np.hypot(w[:, :, 0], w[:, :, 1])
        v = np.empty(n)
        for k in range(3, 9):
            s = ny == k
            v[s] = np.median(r[s, :k], axis=1)
        out.append(v)
    return np.log(out[0] / out[1])


def main(prm_yol, cikti):
    prm = [(d["mu"], d["tau"]) for d in json.load(open(prm_yol))["katman_model"]]
    rng = np.random.default_rng(1117)
    gl = np.round(np.arange(0, 5.01, 0.25), 2)
    out = {}
    for dagin in (False, True):
        for Kp in (6, 8, 10, 12):
            I = np.array(list(itertools.product([-1.0, 1.0], repeat=Kp)))
            gs = []
            for g in gl:
                d = S_iki(rng, 3000 * Kp, prm, g, dagin).reshape(3000, Kp)
                T = d @ I.T                      # (3000, 2^K)
                p = (T >= d.sum(1)[:, None] - 1e-12).mean(1)
                gs.append(float((p <= 0.05).mean()))
            m = None
            for i in range(1, len(gl)):
                if gs[i] >= 0.8:
                    m = round(float(gl[i - 1] + (0.8 - gs[i - 1]) * (gl[i] - gl[i - 1]) / max(gs[i] - gs[i - 1], 1e-9)), 2)
                    break
            key = f"{'daginik' if dagin else 'uyumlu'}_Kp{Kp}"
            out[key] = dict(MDE=m, alfa_g0=round(gs[0], 3), guc={str(g): round(v, 3) for g, v in zip(gl, gs)})
            print(key, m, round(gs[0], 3), flush=True)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
