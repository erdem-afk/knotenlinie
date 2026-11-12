"""İNCELEME-2 b1 (bağımsız denetim), numpy + standart kitaplıkla yeniden yazım (özgün betik scipy kullanıyordu).

tr6a_onkayit_sayilar.json'daki binom tablosunu, p0 ızgarasını (c, gerçek α, güç), testere dişi çözümünü ve ilk/kalıcı
K değerlerini, tr6a_onkayit_sayilar.py'den bağımsız yazılmış kesin binomla (math.comb, Fraction yok; çift duyarlık)
denetler; Poisson H0 altında P(D) ve P(A)'yı ayrıca hesaplar. Gerçek veri okumaz.
Kullanım: python3 -I -B tr6a_inc2_b1.py
"""
import json, math, os
import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))


def sf(x, n, p):                      # P(X >= x)
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(max(x, 0), n + 1))


def cdf(x, n, p):                     # P(X <= x)
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, x + 1)) if x >= 0 else 0.0


def c(K, p0):
    return next(x for x in range(K + 2) if sf(x, K, p0) <= 0.05 + 1e-12)


def h(K):
    hs = [x for x in range(K + 1) if cdf(x, K, 0.75) <= 0.05]
    return max(hs) if hs else -1


def poisson_pd(N0, pi=335 / 2131, Ton=1796 / 365.25, Ts=335 / 365.25):
    lam = N0 * (Ton + Ts)
    s = math.sqrt(lam)
    tot = tota = 0.0
    for n in range(max(1, int(lam - 15 * s - 10)), int(lam + 15 * s + 20)):
        k = np.arange(0, n + 1)
        lp = (math.lgamma(n + 1) - np.array([math.lgamma(x + 1) + math.lgamma(n - x + 1) for x in k])
              + k * math.log(pi) + (n - k) * math.log1p(-pi))
        pmf = np.exp(lp)
        F = np.cumsum(pmf)
        S = 1 - np.concatenate([[0.0], F[:-1]])
        w = math.exp(-lam + n * math.log(lam) - math.lgamma(n + 1))
        b = k[F <= 0.5 + 1e-12]
        if len(b):
            tot += w * F[b.max()]
        a = k[S <= 0.5 + 1e-12]
        if len(a):
            tota += w * S[a.min()]
    return tot, tota


def main():
    d = json.load(open(os.path.join(BURAYA, "tr6a_onkayit_sayilar.json"), encoding="utf-8"))
    bad = 0
    for r in d["binom"]:
        K = r["K"]
        cc = c(K, 0.5)
        if cc != r["kritik_H1"] or h(K) != r["esik_H0"] or abs(sf(cc, K, 0.75) - r["guc_p075"]) > 6e-5:
            bad += 1
            print("binom", K)
    g = d["p0_izgarasi"]
    for p0 in g:
        P = float(p0)
        tab = {}
        for K in range(23, 81):
            cc = c(K, P)
            pw = sf(cc, K, 0.75)
            tab[K] = pw
            t = g[p0]["tablo"][str(K)]
            if cc != t["c"] or abs(pw - t["guc"]) > 6e-5 or abs(sf(cc, K, P) - t["alfa"]) > 6e-5:
                bad += 1
                print("ızgara", p0, K)
        for Kk in range(23, 81):
            u = [k for k in range(23, Kk + 1) if tab[k] >= 0.8]
            kh = max(u) if u else Kk
            if g[p0]["testere"][str(Kk)]["K_hukum"] != kh:
                bad += 1
                print("testere", p0, Kk)
        ilk = next((K for K in range(23, 81) if tab[K] >= 0.8), None)
        kal = next((K for K in range(23, 81) if all(tab[k] >= 0.8 for k in range(K, 81))), None)
        if (ilk, kal) != (g[p0]["ilk_K_guc08"], g[p0]["kalici_K_guc08"]):
            bad += 1
            print("ilk/kalıcı", p0, ilk, kal)
        nb = [(K, round(tab[K], 4)) for K in range(23, 81) if abs(tab[K] - 0.8) < 0.005]
        if nb:
            print("0,80'e yakın güç", p0, nb)
    # sürüm 3 anahtarları: c <= h (K1) ve J < 30 dalı (A1)
    for p0, Ks in d["c_le_h"].items():
        if Ks != [K for K in range(23, 81) if c(K, float(p0)) <= h(K)]:
            bad += 1
            print("c<=h", p0)
    j = d["j30_dali"]
    for pd in (j["P_D_en_kotu"], 0.53):
        for p0 in (0.50, 0.52):
            a = max(sf(c(K, p0), K, pd) for K in range(23, 46))
            if abs(a - j[f"alfa_max P_D={pd:g} p0={p0:.2f}"]["alfa"]) > 6e-5:
                bad += 1
                print("j30", pd, p0, a)
    print("uyuşmayan:", bad)
    for N0 in (17.08, 31.36, 50, 111.2, 300):
        pd, pa = poisson_pd(N0)
        print(f"N0 {N0}: P(D) {pd:.4f}  P(A) {pa:.4f}  α K=23 (p0 0,50) {sf(16, 23, pd):.4f}")


if __name__ == "__main__":
    main()
