# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/c1.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
import sys
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.dirname(__import__("os").path.abspath(__file__)))))
import numpy as np, tr10b_sayim as K
rng = np.random.default_rng(8128)
for Y in (2003, 2013, 1978):
    P, n, i0, iH, iT = K.gunler(Y); t2, t3 = (iT-iH)/365.25, (iH-i0)/365.25
    v = []
    for _ in range(20):
        x = np.cumsum(rng.standard_normal((5000, n)), axis=1) * (1/365.25)**0.5
        u = [np.median(x[:, i-15:i+16], axis=1) for i in (i0, iH, iT)]
        v.append(np.abs((u[2]-u[1])/t2 - (u[1]-u[0])/t3))
    v = np.concatenate(v); q50, q95 = np.quantile(v, [.5, .95])
    # nicelik MC hatası: 200 alt örneklem bootstrap
    bs = [np.quantile(rng.choice(v, v.size), .95) for _ in range(200)]
    print(Y, v.size, "q95 %.4f ± %.4f" % (q95, np.std(bs)), "q50 %.4f" % q50, "kappa %.3f" % (q95/q50), "sd %.4f" % np.sqrt(np.mean(v**2)))
# dv_uc ile aynı mı (tutarlılık)
P, n, i0, iH, iT = K.gunler(2013); x = np.cumsum(rng.standard_normal(n))*(1/365.25)**0.5
u = [np.median(x[i-15:i+16]) for i in (i0, iH, iT)]; t2, t3 = (iT-iH)/365.25, (iH-i0)/365.25
print("dv_uc fark", abs(K.dv_uc(x, np.ones(n, bool), i0, iH, iT, np)["dv"] - ((u[2]-u[1])/t2-(u[1]-u[0])/t3)))
print("Gauss kappa", 1.959964/0.6744898)
