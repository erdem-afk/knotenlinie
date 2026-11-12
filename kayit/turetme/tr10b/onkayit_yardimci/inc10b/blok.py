# İNCELEME-1 (TR-10b_INCELEME-1.md §D) betiğinin kopyası; özgün yer: scratchpad/inc10b/blok.py.
# Değişiklik yalnız yol düzeltmesi (depo içinden çalışsın diye); hesap aynen.
# Bloklu yüzdelik bootstrap'ın kapsama oranı: kesimler arası heterojenlik altında, az blokla.
import numpy as np, json
rng = np.random.default_rng(31)
c1 = 1.78
def kos(yapi, sdlog, tekrar=300, B=1000):
    K = len(yapi); blok = np.repeat(np.arange(K), yapi)
    kac_alt = kac_ust = 0; genislik = []; tek_blok = 0
    for _ in range(tekrar):
        bk = 3.0*np.exp(sdlog*rng.standard_normal(K))         # kesim genlikleri
        # hedef: aynı kesim ağırlıklarıyla (pencere sayısı) evren karışımının q95'i / c1  (kesimler sabit)
        big = np.concatenate([np.abs(rng.standard_normal(20000*w))*bk[k]*c1/1.959964 for k, w in enumerate(yapi)])
        hedef = np.quantile(big, .95)/c1
        dv = np.abs(rng.standard_normal(len(blok)))*bk[blok]*c1/1.959964
        reps = np.empty(B)
        for j in range(B):
            sec = rng.integers(0, K, K)
            reps[j] = np.quantile(np.concatenate([dv[blok == k] for k in sec]), .95)/c1
        L, U = np.quantile(reps, [.05, .95])
        kac_alt += hedef < L; kac_ust += hedef > U; genislik.append(U/L)
    return dict(hedef_L_alti=kac_alt/tekrar, hedef_U_ustu=kac_ust/tekrar, U_bolu_L_medyan=float(np.median(genislik)))
out = {}
for ad, yapi in (("K5_R2", [21,10,4,4,2]), ("K6_U", [21,19,8,6,4,4]), ("K3", [21,12,8])):
    for sd in (0.0, 0.3, 0.6):
        out[f"{ad}_sdlog{sd}"] = kos(yapi, sd)
        print(ad, sd, out[f"{ad}_sdlog{sd}"], flush=True)
