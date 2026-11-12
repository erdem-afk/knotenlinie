import json, math, sys
import numpy as np
L = json.load(open(sys.argv[1]))['olaylar']
rng = np.random.default_rng(424242)
ana = [r for r in L if not r['volkanik']]
km = {}
for r in ana: km.setdefault(r['kume'], []).append(r)
NE = np.array([len(v) for v in km.values()]); K = len(NE); NC = 5; B = 20000
# t quantiles via numpy-free approximation: use table
TQ = {34: (2.0322, 1.6909), 17: (2.1098, 1.7396), 16: (2.1199, 1.7459), 19: (2.093, 1.7291), 24: (2.0639, 1.7109), 9: (2.2622, 1.8331)}
def r_puan(De, Dc): return ((Dc < De[..., None]).sum(-1) + 0.5 * (Dc == De[..., None]).sum(-1)) / Dc.shape[-1]
def sahte(shift_pct, sig, nk=4, Kx=K, nb=B):
    ne = NE[:Kx]; kr = np.zeros((nb, Kx))
    for j in range(Kx):
        Dc = rng.standard_normal((nb, ne[j], nk + 1)); kr[:, j] = r_puan(Dc[..., 0] + shift_pct / sig, Dc[..., 1:]).mean(1)
    return float((kr.mean(1) <= 0.25).mean()), float(kr.mean())
print('Duyarlılık P(r_sahte<=0,25):')
for sh in (-0.1, -0.2):
    print(' ekleme', sh, {s: tuple(round(x, 3) for x in sahte(sh, s)) for s in (0.05, 0.075, 0.1, 0.15, 0.2, 0.3)})
print(' K=20, -0,2:', {s: round(sahte(-0.2, s, Kx=20)[0], 3) for s in (0.1, 0.15, 0.2)})
# H1 gücü: tam kural vs d şartsız (ana + plasebo blok değil) ; olay gürültüsü s_e
def h1(delta, s_e=1.0, Kp=18, nb=B, pl_bias=0.0):
    t95, t90 = TQ[K - 1]; tpb, tp = TQ[Kp - 1]
    kr = np.zeros((nb, K)); Dek = delta + pl_bias + s_e * rng.standard_normal((nb, K))
    for j in range(K):
        Dc = rng.standard_normal((nb, NE[j], NC)); kr[:, j] = r_puan(np.repeat(Dek[:, j:j+1], NE[j], 1), Dc).mean(1)
    m = kr.mean(1); se = kr.std(1, ddof=1) / math.sqrt(K)
    ana_ = (m - t95 * se > 0.5) | (m + t95 * se < 0.5)
    Dp = pl_bias + s_e * rng.standard_normal((nb, Kp)); rp = np.zeros((nb, Kp))
    for j in range(Kp): rp[:, j] = r_puan(Dp[:, j], rng.standard_normal((nb, NC)))
    d = kr[:, :Kp] - rp; dm = d.mean(1); dse = d.std(1, ddof=1) / math.sqrt(Kp)
    yon = np.sign(m - 0.5)
    d_ok = np.where(yon > 0, dm - tp * dse > 0, dm + tp * dse < 0)
    pm = rp.mean(1); pse = rp.std(1, ddof=1) / math.sqrt(Kp)
    blok = np.where(yon > 0, pm - tpb * pse > 0.5, pm + tpb * pse < 0.5)
    return dict(tam=round(float((ana_ & d_ok & ~blok).mean()), 3), d_sartsiz=round(float((ana_ & ~blok).mean()), 3),
                ana=round(float(ana_.mean()), 3))
print('H1 gücü (δ, σ_c birimi):')
for dl in (0.0, 0.5, 0.75, 1.0):
    print(' δ', dl, 'eşit ölçek', h1(dl), '| olay 1,5 kat gürültülü', h1(dl, s_e=1.5))
print('Yer yanlılığı b (olay ve plasebo aynı), δ=0:')
for b in (0.25, 0.5, 0.75):
    print(' b', b, h1(0.0, pl_bias=b))
print('Kp=17:', h1(0.75, Kp=17))
