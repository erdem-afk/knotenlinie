import sys, json, math
sys.path.insert(0, "/home/user/knotenlinie/kayit/turetme/tr10b")
import numpy as np
import tr10b_sayim as K
rng = np.random.default_rng(777)
out = {}
# deterministik sınır (günlük katman)
for Y in (2003, 2013, 2018, 1978):
    P, n, i0, iH, iT = K.gunler(Y)
    t2, t3 = (iT-iH)/365.25, (iH-i0)/365.25
    r = 5*15/365.25
    out[f"sinir_{Y}"] = dict(tau2=t2, tau3=t3, d_min=5 - 2*r/t2 - r/t3, d_max=5 + r/t2)
P, n, i0, iH, iT = K.gunler(2013)
t = np.arange(n)/365.25
ramp = 5.0*np.maximum(0, t - iH/365.25)

def maske_gercekci(dol_min=0.6):
    """doluluk hedefi U[dol_min,1]; delikler 1-60 gün; uç pencerelerinde >=10 gün (değilse yeniden)."""
    while True:
        hedef = rng.uniform(dol_min, 1.0)
        m = np.ones(n, bool)
        while m.mean() > hedef:
            L = int(rng.integers(1, 61)); a = int(rng.integers(0, n)); m[a:a+L] = False
        # doluluk dönem başına
        if m[i0:iH].mean() < 0.6 or m[iH:iT].mean() < 0.6: continue
        # en uzun boşluk <= 60
        z = np.flatnonzero(m); 
        if len(z) < 2 or np.max(np.diff(z)) - 1 > 60 or z[0] > 60 or n-1-z[-1] > 60: continue
        ok = all(m[max(0,i-15):i+16].sum() >= 10 for i in (i0, iH, iT))
        if ok: return m

def maske_kotu():
    """uçlarda yalnız 10 gün ve tek yanda (en kötü asimetri)."""
    m = np.ones(n, bool)
    for i in (i0, iH, iT):
        m[i-15:i+16] = False
        if rng.random() < 0.5: m[i-15:i-5] = True
        else: m[i+6:i+16] = True
    return m

rejimler = {
 "RW_b3_beyaz0.1": lambda: K.pl_seri(n, 2.0, 3.0, rng, np) + 0.1*rng.standard_normal(n),
 "duz_nicem0.01": lambda: np.round(0.003*rng.standard_normal(n)/0.01)*0.01,
 "dogrusal10_beyaz0.02": lambda: 10*t + 0.02*rng.standard_normal(n),
 "basamakli": lambda: (np.cumsum((rng.random(n) < 4/365.25) * rng.exponential(1.0, n)) + 2*t + 0.02*rng.standard_normal(n)),
 "beyaz1mm": lambda: 1.0*rng.standard_normal(n),
 "RW_b3_mevsim3mm": lambda: K.pl_seri(n, 2.0, 3.0, rng, np) + 3*np.sin(2*np.pi*t) + 0.1*rng.standard_normal(n),
}
for mad, mf in (("tam", lambda: np.ones(n, bool)), ("gercekci", maske_gercekci), ("kotu", maske_kotu)):
    for ad, f in rejimler.items():
        d = []
        for _ in range(400):
            m = mf(); x = f()
            r0 = K.dv_uc(x, m, i0, iH, iT, np); r1 = K.dv_uc(x + ramp, m, i0, iH, iT, np)
            if r0 and r1: d.append(r1["dv"] - r0["dv"])
        d = np.array(d)
        # 20'li alt örneklerin medyanı
        med20 = [np.median(rng.choice(d, 20, replace=False)) for _ in range(2000)]
        out[f"c_{mad}_{ad}"] = dict(N=len(d), medyan=float(np.median(d)), q005=float(np.quantile(d,.005)),
            q995=float(np.quantile(d,.995)), med20_q001=float(np.quantile(med20,.001)), med20_q999=float(np.quantile(med20,.999)))
# (a) gürültüsüz sınama gerçekçi maskeyle
def f_a():
    return (3.0 + 7.0*t + 4.0*np.maximum(0, t - iH/365.25) + 2.0*np.sin(2*np.pi*t + 1) + 0.7*np.cos(4*np.pi*t)
            + 3.0*(np.arange(n) >= iH - 200))
gercek = 4.0 - 3.0/((iH-i0)/365.25)
for mad, mf in (("gercekci", maske_gercekci), ("kotu", maske_kotu)):
    h = []
    for _ in range(500):
        r = K.dv_uc(f_a(), mf(), i0, iH, iT, np)
        if r: h.append(abs(r["dv"] - gercek))
    h = np.array(h); out[f"a_{mad}"] = dict(N=len(h), q99=float(np.quantile(h,.99)), max=float(h.max()))
# (b) maske etkisi: tam maske paydası ile gerçekçi maske q95 oranı
b = 3.0
def q95(mf, N):
    v = []
    while len(v) < N:
        x = K.pl_seri(n, 2.0, b, rng, np) + 0.1*rng.standard_normal(n)
        r = K.dv_uc(x, mf(), i0, iH, iT, np)
        if r: v.append(abs(r["dv"]))
    return float(np.quantile(v, .95))
qt = q95(lambda: np.ones(n, bool), 20000); qg = q95(maske_gercekci, 20000); qk = q95(maske_kotu, 20000)
out["b_q95_tam"] = qt; out["b_q95_gercekci"] = qg; out["b_q95_kotu"] = qk
out["b_oran_gercekci_tam"] = qg/qt; out["b_oran_kotu_tam"] = qk/qt
# b=1 saf RW tam maske
v = []
for _ in range(20000):
    x = K.pl_seri(n, 2.0, 1.0, rng, np); v.append(abs(K.dv_uc(x, np.ones(n,bool), i0, iH, iT, np)["dv"]))
out["c1_q95_b1_tam_2013"] = float(np.quantile(v, .95)); out["c1_q50_b1"] = float(np.quantile(v,.5))
print(json.dumps(out, indent=1))
