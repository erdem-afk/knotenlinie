"""asim.py çıktısının çözümlemesi: R0 red oranı, sıfır/veri süzgeci bileşimleri; havuz önyükleme (paired)."""
import json
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, "/home/user/knotenlinie/kayit/turetme/tr13b")
import tr13b_kosu as K  # noqa: E402

D = K.DALLANMA
ONAR = "zonly"


def yukle(yol):
    z = np.load(yol)
    uye = z["uye"]
    U = [(int(r[0]), int(r[1]), float(r[2]), int(r[3])) for r in uye]
    return z, U


def suz(h, kip):
    ok = np.isfinite(h[:, 0])
    if kip in ("kod", "duz", "sonlu"):
        ok &= np.isfinite(h[:, 1])
    if kip in ("duz", "N50", "duz_zonly"):
        ok &= h[:, 2] >= 50
    return h[ok]


def oranlar(z, U, sifir_kip, veri_kip, rng_boot=None, ns=100000, nb=20000):
    ids = [u[0] for u in U]
    kids = sorted({u[1] for u in U})
    kum = [[u[0] for u in U if u[1] == k] for k in kids]
    kd = [j for j, k in enumerate(kids) if k not in K.KESIF]

    def al(ad, kip):
        h = z[ad]
        if rng_boot is not None:          # ham havuz önce yeniden örneklenir: iki süzgeç aynı örnekle (eşli)
            h = h[rng_boot.integers(0, len(h), len(h))]
        return suz(h, kip)
    Sa, Sk = {}, {}
    for di, d in enumerate(D):
        hv = {i: al(f"s{i}_{di}", sifir_kip) for i in ids}
        S = K.sifir_cekilis(np.random.default_rng(100 + di), hv, kum, ns)
        Sa[d], Sk[d] = np.sort(S[:, :, 0].mean(1)), np.sort(S[:, kd, 0].mean(1))
    out = {}
    for ad in ("0", "f"):
        hv = {i: al(f"v{i}_{ad}", veri_kip) for i in ids}
        c = K.sifir_cekilis(np.random.default_rng(7), hv, kum, nb)
        out[ad] = K.r0_oran(Sa, Sk, c[:, :, 0].mean(1), c[:, kd, 0].mean(1))
    return out


def nitelik(z, U):
    r = {}
    for i, k, R, N in U:
        for di in range(3):
            h = z[f"s{i}_{di}"]
            fin = np.isfinite(h[:, 0])
            alt = h[:, 2] < 50
            r[f"{i}_{di}"] = dict(
                N=N, R=R, n=len(h), z_nan=float(np.mean(~fin)),
                zp_nan_z_var=float(np.mean(fin & ~np.isfinite(h[:, 1]))), N50_alti=float(np.mean(alt)),
                N_ort=float(h[:, 2].mean()), nan_N_ort=float(h[~fin, 2].mean()) if (~fin).any() else None,
                z_ort_N50alti=float(h[fin & alt, 0].mean()) if (fin & alt).any() else None,
                z_ort_N50ustu=float(h[fin & ~alt, 0].mean()),
                z_q05_kod=float(np.quantile(h[fin & np.isfinite(h[:, 1]), 0], 0.05)),
                z_q05_duz=float(np.quantile(h[fin & np.isfinite(h[:, 1]) & ~alt, 0], 0.05)))
    return r


def main(yol, cikti, B):
    z, U = yukle(yol)
    sonuc = dict(nitelik=nitelik(z, U), oran={})
    for sk, vk in (("kod", "sonlu"), ("kod", "kosulsuz"), ("kod", "N50"), ("zonly", "kosulsuz"), ("zonly", "N50"),
                   ("duz", "N50"), ("duz_zonly", "N50"), ("zonly", "sonlu")):
        sonuc["oran"][f"{sk}|{vk}"] = oranlar(z, U, sk, vk)
        print(sk, vk, sonuc["oran"][f"{sk}|{vk}"], flush=True)
    # önyükleme: (kod|N50) - (duz|N50) farkı, aynı önyükleme örneğiyle
    sat = []
    for b in range(B):
        r = [oranlar(z, U, sk, "N50", np.random.default_rng(1000 + b), ns=50000, nb=10000)
             for sk in ("kod", "zonly", "duz_zonly")]
        sat.append([x["0"] for x in r] + [x["f"] for x in r])
    sat = np.array(sat)
    sonuc["onyukleme"] = dict(B=B, sira="fa kod, fa zonly, fa duz_zonly, guc kod, guc zonly, guc duz_zonly",
                              ort=sat.mean(0).tolist(), sd=sat.std(0, ddof=1).tolist(),
                              fark_zp=[float((sat[:, 0] - sat[:, 1]).mean()), float((sat[:, 0] - sat[:, 1]).std(ddof=1))],
                              fark_N50=[float((sat[:, 1] - sat[:, 2]).mean()), float((sat[:, 1] - sat[:, 2]).std(ddof=1))],
                              fark_guc_N50=[float((sat[:, 4] - sat[:, 5]).mean()), float((sat[:, 4] - sat[:, 5]).std(ddof=1))])
    print(sonuc["onyukleme"])
    json.dump(sonuc, open(cikti, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]))
