# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/etiket.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
# Bant içindeki gerçek değerlerde yanlış "küçük"/"büyük" etiketi olasılığı; %90 ve %95 yüzdelik aralık, ve
# önerilen ek şart (birini-dışarıda-bırak kesim jackknife'ının bütün nokta değerleri aynı yanda).
import numpy as np
rng = np.random.default_rng(57)
c1 = 1.78
def kos(yapi, b, sdlog, tekrar=300, B=1000):
    K = len(yapi); blok = np.repeat(np.arange(K), yapi)
    r = dict(kucuk90=0, buyuk90=0, kucuk95=0, buyuk95=0, kucuk90_jk=0, buyuk90_jk=0)
    for _ in range(tekrar):
        bk = b*np.exp(sdlog*rng.standard_normal(K)); bk *= b/np.exp(np.mean(np.log(bk)))  # geometrik ortalama b
        dv = np.abs(rng.standard_normal(len(blok)))*bk[blok]*c1/1.959964
        reps = np.empty(B)
        for j in range(B):
            sec = rng.integers(0, K, K)
            reps[j] = np.quantile(np.concatenate([dv[blok == k] for k in sec]), .95)/c1
        L90, U90 = np.quantile(reps, [.05, .95]); L95, U95 = np.quantile(reps, [.025, .975])
        jk = [np.quantile(dv[blok != k], .95)/c1 for k in range(K)]
        r["kucuk90"] += U90 < 2.2; r["buyuk90"] += L90 > 4.6
        r["kucuk95"] += U95 < 2.2; r["buyuk95"] += L95 > 4.6
        r["kucuk90_jk"] += (U90 < 2.2) and max(jk) < 2.2; r["buyuk90_jk"] += (L90 > 4.6) and min(jk) > 4.6
    return {k: round(v/tekrar, 3) for k, v in r.items()}
for ad, yapi in (("K5", [21,10,4,4,2]), ("K6", [21,19,8,6,4,4])):
    for b in (1.5, 2.5, 4.0, 6.0):
        for sd in (0.0, 0.3):
            print(ad, "b", b, "sdlog", sd, kos(yapi, b, sd), flush=True)
