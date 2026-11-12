import sys, json
sys.path.insert(0, "/home/user/knotenlinie/kayit/turetme/tr10b")
import numpy as np
import tr10b_sayim as K
out = {}
rng = np.random.default_rng(4242)
dT = 1/365.25
for Y in (2003, 2013):
    P, n, i0, iH, iT = K.gunler(Y)
    m = np.ones(n, bool); v = []
    for _ in range(100000):
        x = np.cumsum(rng.standard_normal(n)) * dT**0.5
        v.append(K.dv_uc(x, m, i0, iH, iT, np)["dv"])
    v = np.abs(np.array(v))
    q50, q95, q99 = np.quantile(v, [.5, .95, .99])
    out[f"c1_{Y}"] = dict(q50=q50, q95=q95, q99=q99, kappa=q95/q50, sd=float(np.sqrt(np.mean(v**2))))
c1 = out["c1_2003"]["q95"]
# etiket davranışı: kesim yapısı B_R2 (21,10,4,4,2) ve B_U (21,19,8,6,4,4); Gauss |dv|, site bağımsız
def etiket_sim(yapi, b, tekrar=400, B=2000):
    sonuc = {"buyuk": 0, "bant": 0, "kucuk": 0}; bL=[]; bU=[]; kap=[]
    blok = np.repeat(np.arange(len(yapi)), yapi)
    for _ in range(tekrar):
        dv = np.abs(rng.standard_normal(len(blok))) * b * c1 / 1.959964
        reps = []
        for _ in range(B):
            sec = rng.integers(0, len(yapi), len(yapi))
            vals = np.concatenate([dv[blok == k] for k in sec])
            reps.append(np.quantile(vals, .95) / c1)
        L, U = np.quantile(reps, [.05, .95]); bL.append(L); bU.append(U)
        kap.append(np.quantile(dv,.95)/np.quantile(dv,.5))
        if L > 4.6: sonuc["buyuk"] += 1
        elif U < 2.2: sonuc["kucuk"] += 1
        else: sonuc["bant"] += 1
    return dict(etiket={k: v/tekrar for k, v in sonuc.items()}, bL_medyan=float(np.median(bL)), bU_medyan=float(np.median(bU)),
                kappa_q05_q95=[float(np.quantile(kap,.05)), float(np.quantile(kap,.95))])
for ad, yapi in (("B_R2", [21,10,4,4,2]), ("B_U", [21,19,8,6,4,4])):
    for b in (1.5, 3.0, 6.0, 9.0):
        out[f"etiket_{ad}_b{b}"] = etiket_sim(yapi, b, tekrar=200, B=1000)
print(json.dumps(out, indent=1, default=float))
