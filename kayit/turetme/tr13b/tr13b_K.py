#!/usr/bin/env python3
"""TR-13b ek: T1 (ETAS-kalibre ortalama z) MDE'sinin K'ye bağımlılığı (K = 8, 11, 14, 17, 20). YALNIZ YAPAY VERİ.
Üreteç ve ölçü tr13b_mde.py / tr13_guc.py ile aynı; tohum farklı (20261117).
Kullanım: python3 -I -B tr13b_K.py <cikti.json>
"""
import json
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tr13b_mde as M  # noqa: E402

K_LIST = [8, 11, 14, 17, 20]
F_LIST = [0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]


def main(cikti):
    rng = np.random.default_rng(20261117)
    out = dict(K=K_LIST, f=F_LIST, N={})
    for N in (50, 100):
        M.dallanma(0.6)
        Nh = M.kalibre(rng, N)
        z0 = M.havuz(rng, Nh, 0.0, 1500)[:, 0]
        hv = {f: M.havuz(rng, Nh, f, 500)[:, 0] for f in F_LIST}
        r = {}
        for K in K_LIST:
            e1 = float(np.quantile(rng.choice(z0, (40000, K)).mean(1), M.ALFA))
            g = [float((rng.choice(hv[f], (20000, K)).mean(1) < e1).mean()) for f in F_LIST]
            r[str(K)] = dict(esik=round(e1, 3), guc=[round(v, 3) for v in g], MDE_f=M.mde(F_LIST, g))
            print(N, K, r[str(K)], flush=True)
        out["N"][str(N)] = r
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1])
