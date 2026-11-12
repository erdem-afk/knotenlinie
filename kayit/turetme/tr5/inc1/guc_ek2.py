import json, math, sys
import numpy as np
L = json.load(open(sys.argv[1]))['olaylar']
rng = np.random.default_rng(99001)
ana = [r for r in L if not r['volkanik']]
km = {}
for r in ana: km.setdefault(r['kume'], []).append(r)
NE = np.array([len(v) for v in km.values()]); B = 20000
T975 = {34: 2.0322, 19: 2.0930, 24: 2.0639}
def r_puan(De, Dc): return ((Dc < De[..., None]).sum(-1) + 0.5 * (Dc == De[..., None]).sum(-1)) / Dc.shape[-1]
def p(shift, sig, K=35, nk=4):
    ne = NE[:K]; kr = np.zeros((B, K))
    for j in range(K):
        Dc = rng.standard_normal((B, ne[j], nk + 1)); kr[:, j] = r_puan(Dc[..., 0] + shift / sig, Dc[..., 1:]).mean(1)
    m = kr.mean(1); se = kr.std(1, ddof=1) / math.sqrt(K)
    return round(float((m + T975[K - 1] * se < 0.5).mean()), 3), round(float((m <= 0.25).mean()), 3)
for K in (35, 20):
    print('K', K, '(-0,1: P[üst sınır<0,5], P[r<=0,25])', {s: p(-0.1, s, K) for s in (0.075, 0.1, 0.15, 0.2, 0.3)})
    print('K', K, '(-0,2)', {s: p(-0.2, s, K) for s in (0.1, 0.15, 0.2, 0.3, 0.4)})
