"""İNCELEME-2 b2 (bağımsız denetim), numpy + standart kitaplıkla yeniden yazım (özgün betik scipy kullanıyordu).

Yapay: H0 altında gerçek oy ile sahte oyların ortak veri yüzünden ilişkisi ve §4.6 tam kalibrasyon yordamının α'sı.
Ortak zaman ekseni 12 bölüt; her bölütün oranı bağımsız Gamma çarpanıyla saçılır (φ = var/ortalama, yıllık). Gerçek oy:
ön [t0 − 1826, t0 − 30), son [t0 + 30, t0 + 365); sahte j = 1, 2, 3 §4.6'daki gibi (kesilmemiş, tek olaylı birim).
Gerçek veri okumaz. Tohum 7 (özgün betikteki gibi); eşikler scipy'siz kesin binomla.
Kullanım: python3 -I -B tr6a_inc2_b2.py
"""
import math
import numpy as np

PI = 335 / 2131
NMAX = 60000
rng = np.random.default_rng(7)
_LF = np.concatenate([[0.0], np.cumsum(np.log(np.arange(1, NMAX + 2)))])
_KB = {}


def k_b(n):
    """b_dus(n): F(b; n, π) <= 0,5 olan en büyük b (yoksa −1); pencereli kesin binom."""
    if n not in _KB:
        s = math.sqrt(n * PI * (1 - PI)) + 1
        lo, hi = max(0, int(n * PI - 16 * s - 5)), min(n, int(n * PI + 16 * s + 5))
        k = np.arange(lo, hi + 1)
        lp = _LF[n] - _LF[k] - _LF[n - k] + k * math.log(PI) + (n - k) * math.log1p(-PI)
        F = np.cumsum(np.exp(lp))
        ok = np.nonzero(F <= 0.5 + 1e-12)[0]
        _KB[n] = int(lo + ok.max()) if len(ok) else lo - 1
    return _KB[n]


B = [-2891, -2556, -2221, -1826, -1095, -1035, -760, -700, -425, -365, -30, 30, 365]
SEG = list(zip(B[:-1], B[1:]))


def _idx(a, b):
    return [i for i, (x, y) in enumerate(SEG) if x >= a and y <= b]


W = {"on": _idx(-1826, -30), "son": _idx(30, 365), "s1o": _idx(-2221, -425), "s1s": _idx(-365, -30),
     "s2o": _idx(-2556, -760), "s2s": _idx(-700, -365), "s3o": _idx(-2891, -1095), "s3s": _idx(-1035, -700)}


def kume(M, N0, phi):
    L = np.array([(y - x) / 365.25 for x, y in SEG])
    if phi == 1:
        g = np.ones((M, len(SEG)))
    else:
        kk = N0 / (phi - 1)
        g = rng.gamma(kk * L, 1 / (kk * L), (M, len(SEG)))
    c = rng.poisson(N0 * L * g)

    def oy(o, s):
        a = c[:, W[o]].sum(1)
        b = c[:, W[s]].sum(1)
        n = a + b
        kb = np.array([k_b(int(x)) if x > 0 else -1 for x in n])
        return ((n > 0) & (b <= kb)).astype(int)
    return oy("on", "son"), np.stack([oy("s1o", "s1s"), oy("s2o", "s2s"), oy("s3o", "s3s")], 1)


def _sf(x, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(max(x, 0), n + 1))


_C = {}


def ckp(K, p):
    if (K, p) not in _C:
        _C[(K, p)] = next(x for x in range(K + 2) if _sf(x, K, p) <= 0.05 + 1e-12)
    return _C[(K, p)]


def yordam(D, Ds, valid, K, taban=50, j_alt=30, taban_j30=52):
    """§4.6 yordamı (sürüm 3): p0 = max(0,50; ⌈100 S/J⌉/100); J < 30 ise max(0,52; ⌈100 S/J⌉/100) (A1);
    p0 > 0,60 ise H1 verilmez. Döndürür: H1 oranı (H0 altında gerçek α)."""
    X = D.sum(1)
    S = (Ds * valid).sum(1)
    J = valid.sum(1)
    res = np.zeros(len(X), bool)
    for r in range(len(X)):
        yuz = -(-100 * int(S[r]) // int(J[r])) if J[r] > 0 else 0
        p0 = max(taban, yuz) if J[r] >= j_alt else max(taban_j30, yuz)
        if p0 > 60:
            continue
        res[r] = X[r] >= ckp(K, p0 / 100)
    return res.mean()


def main(R=20000):
    for N0, phi in ((31.36, 1), (31.36, 3), (31.36, 5), (100, 3), (100, 5), (500, 5)):
        for K in (23, 28):
            D, Ds = kume(R * K, N0, phi)
            D = D.reshape(R, K)
            Ds = Ds.reshape(R, K, 3)
            valid = np.ones((R, K * 3), int)
            cor = np.corrcoef(D.ravel(), Ds[:, :, 0].ravel())[0, 1]
            a_full = yordam(D, Ds.reshape(R, K * 3), valid, K)
            perm = rng.permutation(R)
            a_ind = yordam(D, Ds[perm].reshape(R, K * 3), valid, K)
            a_p05 = (D.sum(1) >= ckp(K, 0.5)).mean()
            print(f"N0 {N0} φ {phi} K {K}: P(D) {D.mean():.4f} P(D') {Ds.mean():.4f} kor(D, D'1) {cor:+.3f} | "
                  f"α p0 0,50 {a_p05:.4f}  kalibre-ortak {a_full:.4f}  kalibre-bağımsız {a_ind:.4f}")


if __name__ == "__main__":
    main()
