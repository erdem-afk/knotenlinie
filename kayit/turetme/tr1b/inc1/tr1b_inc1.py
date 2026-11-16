#!/usr/bin/env python3
"""TR-1b INCELEME-1: bağımsız yeniden hesap. YALNIZ TR-11'in commit edilmiş depremsiz küme-pencere tablosu ve yapay veri.

Hiçbir olay penceresi, hiçbir tenv3 serisi okunmaz. Girdi: kayit/turetme/tr11/tr11_sonuc.json (kume_pencere_tablosu).
Yazarın betiğinden farkları (bilerek):
  - sıfır dağılımı modelden değil, TR-11'in 665 gerçek S'inden (taslaktaki koşu gibi; katman içi orta-sıra ECDF);
  - sinyal modeli katman başına ayrı uydurulan log-normal σ (yazar tek model kullandı);
  - yanlış alarm, gerçek bölge şişmesi c_gercek ≠ c0 ve karışım kirlenmesi altında; "bir kümeyi dışarıda bırak"
    şartı dahil;
  - TR-11 içi alt kümelerin (epok, sınıf B, Batı ABD) eşdeğer şişme katsayısı;
  - yerinde kaydırılmış plasebo kuralının (c0* = max(1,64, ĉ_üst)) yanlış alarm ve güç bedeli.
Kullanım: python3 -I -B tr1b_inc1.py <tr11_sonuc.json> <cikti.json>
"""
import json
import sys

import numpy as np

sys.dont_write_bytecode = True
TOHUM = 1116
ALFA, GUC = 0.05, 0.80
KAT = [(3, 4), (5, 7), (8, 8)]


def yukle(yol):
    t = json.load(open(yol))["kume_pencere_tablosu"]
    S = np.array([r["S"] for r in t])
    ny = np.array([r["n_y"] for r in t])
    kat = np.array([next(i for i, (a, b) in enumerate(KAT) if a <= n <= b) for n in ny])
    return t, S, ny, kat


class Puan:
    """Katman içi orta-sıra ECDF (taslak §3)."""

    def __init__(self, S, kat):
        self.s = [np.sort(S[kat == k]) for k in range(3)]

    def u(self, s, k):
        out = np.empty(len(s))
        for j in range(3):
            m = k == j
            if m.any():
                a = self.s[j]
                out[m] = (np.searchsorted(a, s[m], "left") + np.searchsorted(a, s[m], "right")) / 2 / len(a)
        return out


def esd_c(P, S_alt, k_alt, hedef_u):
    """Alt kümenin ū'suna eşit ū veren çarpan: ort F(c × S_tum) = hedef (katman korunur)."""
    cs = np.linspace(0.5, 3.0, 501)
    us = [P.u(c * S_alt, k_alt).mean() for c in cs]
    return float(np.interp(hedef_u, us, cs))


def uydur_katman(rng, Sk, n_lo, n_hi):
    """Katman log-normal σ modeli: S = σ × median|N2| (n_y katman içinde düzgün)."""
    M = 60000
    ny = rng.integers(n_lo, n_hi + 1, M)
    w = rng.standard_normal((M, 8, 2))
    med = np.empty(M)
    for n in range(n_lo, n_hi + 1):
        s = ny == n
        med[s] = np.median(np.hypot(w[s, :n, 0], w[s, :n, 1]), axis=1)
    z = rng.standard_normal(M)
    qs = np.array([0.25, 0.5, 0.75, 0.9, 0.95])
    h = np.quantile(Sk, qs)
    en = None
    for tau in np.arange(0.2, 1.0, 0.02):
        for mu in np.arange(-1.2, 0.6, 0.01):
            q = np.quantile(med * np.exp(mu + tau * z), qs)
            e = float(np.sum(np.log(q / h) ** 2))
            if en is None or e < en[0]:
                en = (e, round(float(mu), 3), round(float(tau), 3))
    return en


def S_model(rng, n, kat_i, prm, g=0.0, dagin=False, c=1.0):
    """Model S (sinyalli). c: bölge gürültü şişmesi (σ × c)."""
    out = np.empty(n)
    for j, (lo, hi) in enumerate(KAT):
        m = kat_i == j
        nm = int(m.sum())
        if nm == 0:
            continue
        mu, tau = prm[j]
        sig = c * np.exp(mu + tau * rng.standard_normal(nm))
        ny = rng.integers(lo, hi + 1, nm)
        w = rng.standard_normal((nm, 8, 2)) * sig[:, None, None]
        if g:
            a = rng.random((nm, 8)) if dagin else np.ones((nm, 8))
            w[:, :, 0] += g * a
        r = np.hypot(w[:, :, 0], w[:, :, 1])
        v = np.empty(nm)
        for n in range(lo, hi + 1):
            s = ny == n
            v[s] = np.median(r[s, :n], axis=1)
        out[m] = v
    return out


def main(yol, cikti):
    rng = np.random.default_rng(TOHUM)
    t, S, ny, kat = yukle(yol)
    P = Puan(S, kat)
    pk = np.bincount(kat, minlength=3) / len(kat)
    out = {"n_KP": int(len(S)), "katman_n": np.bincount(kat).tolist()}

    # 1. c0 tek başına AUC (gerçek S ile)
    out["AUC_c0_gercek"] = {str(c): round(float(P.u(c * S, kat).mean()), 3) for c in (1.0, 1.3, 1.64, 2.0, 2.5)}

    # 2. TR-11 içi alt küme şişmeleri (alt küme dışarıda bırakılmış ECDF yerine tüm ECDF; alt küme küçük)
    T = np.array([r["T"][:4] for r in t])
    la = np.array([r["la"] for r in t])
    lo = np.array([r["lo"] for r in t])
    sinif = np.array([r["sinif"] for r in t])
    alt = {f"epok_{e}": T == e for e in ("2003", "2008", "2013", "2018", "2023")}
    alt["sinif_B"] = sinif == "B"
    alt["bati_ABD(lo -125..-110, la 30..50)"] = (lo > -125) & (lo < -110) & (la > 30) & (la < 50)
    alt["epok_2008_disi"] = T != "2008"
    sub = {}
    for ad, m in alt.items():
        u = P.u(S[m], kat[m])
        sub[ad] = dict(n=int(m.sum()), u_ort=round(float(u.mean()), 3),
                       u_se=round(float(u.std(ddof=1) / np.sqrt(m.sum())), 3),
                       medyan_S=round(float(np.median(S[m])), 3),
                       esd_c=round(esd_c(P, S, kat, float(u.mean())), 2))
    out["alt_kume"] = sub

    # 3. katman modeli
    prm = []
    for j, (a, b) in enumerate(KAT):
        e, mu, tau = uydur_katman(rng, S[kat == j], a, b)
        prm.append((mu, tau))
    out["katman_model"] = [dict(mu=m, tau=ta) for m, ta in prm]
    # model g = 0'da gerçek ECDF'e göre ū (≈ 0,5 olmalı) ve 3 mm/yıl medyan artışı
    kk = rng.choice(3, 60000, p=pk)
    s0 = S_model(rng, 60000, kk, prm)
    out["model_g0_u"] = round(float(P.u(s0, kk).mean()), 3)
    out["model_q95_vs_gercek"] = [round(float(np.quantile(s0[kk == j], .95)), 2) for j in range(3)] + \
        [round(float(np.quantile(S[kat == j], .95)), 2) for j in range(3)]
    r1 = np.random.default_rng(5)
    r2 = np.random.default_rng(5)
    a0 = S_model(r1, 60000, kk, prm)
    a3 = S_model(r2, 60000, kk, prm, g=3.0)
    out["model_g3_medyan_artis"] = round(float(np.median(a3 - a0)), 3)

    # sıfır havuzu (katman başına c0 × gerçek S'in u'su)
    def null_u(c0, n):
        k = rng.choice(3, n, p=pk)
        s = np.empty(n)
        for j in range(3):
            m = k == j
            s[m] = rng.choice(S[kat == j], int(m.sum()))
        return P.u(c0 * s, k)

    def esik(c0, K, nb=200000):
        u = null_u(c0, 400000)
        return float(np.quantile(rng.choice(u, (nb, K)).mean(1), 1 - ALFA)), u

    def guc(u_alt, e, K, nb=20000, loo=False, u0=None, c0=None):
        X = rng.choice(u_alt, (nb, K))
        ana = X.mean(1) > e
        if not loo:
            return float(ana.mean())
        # her bir kümeyi dışarıda bırak: p ≤ 0,10 ⇔ ū_(-i) > e10(K-1)
        e10 = float(np.quantile(rng.choice(u0, (200000, K - 1)).mean(1), 0.90))
        loo_ok = ((X.sum(1)[:, None] - X) / (K - 1) > e10).all(1)
        return float((ana & loo_ok).mean())

    # 4. MDE (K = 6, 12, 20), sıfır gerçek S, sinyal katman modeli
    gl = np.round(np.arange(0, 6.01, 0.1), 2)
    mde_t = {}
    for dagin in (False, True):
        ug = {}
        for g in gl:
            k = rng.choice(3, 30000, p=pk)
            ug[g] = P.u(S_model(rng, 30000, k, prm, g=g, dagin=dagin), k)
        for c0 in (1.0, 1.3, 1.64):
            for K in (6, 12, 20):
                e, _ = esik(c0, K)
                gs = [guc(ug[g], e, K) for g in gl]
                m = None
                for i in range(1, len(gl)):
                    if gs[i] >= GUC:
                        m = round(float(gl[i - 1] + (GUC - gs[i - 1]) * (gl[i] - gl[i - 1]) / max(gs[i] - gs[i - 1], 1e-9)), 2)
                        break
                auc = None
                if m is not None:
                    k = rng.choice(3, 30000, p=pk)
                    auc = round(float(P.u(S_model(rng, 30000, k, prm, g=m, dagin=dagin), k).mean()), 3)
                mde_t[f"{'daginik' if dagin else 'uyumlu'}_c0{c0}_K{K}"] = dict(esik=round(e, 4), MDE=m, AUC=auc)
                print(f"{'daginik' if dagin else 'uyumlu'} c0 {c0} K {K}: esik {e:.4f} MDE {m} AUC {auc}", flush=True)
    out["MDE"] = mde_t

    # 4b. Bölge şişmesi gerçekten c0 = 1,64 iken (σ × 1,64) gereken g
    for dagin in (False, True):
        e, _ = esik(1.64, 12)
        gs = []
        for g in gl:
            k = rng.choice(3, 20000, p=pk)
            gs.append(guc(P.u(S_model(rng, 20000, k, prm, g=g, dagin=dagin, c=1.64), k), e, 12))
        m = next((round(float(gl[i]), 1) for i in range(len(gl)) if gs[i] >= GUC), None)
        out[f"MDE_sisme_gercek_1.64_{'daginik' if dagin else 'uyumlu'}_K12"] = m

    # 5. Yanlış alarm: olay S = c_gercek × gerçek S (sinyal yok); "VAR" = ana p ≤ 0,05 ve LOO p ≤ 0,10
    fa = {}
    for K in (6, 12, 20):
        e, u0 = esik(1.64, K)
        for cg in (1.0, 1.3, 1.64, 1.8, 2.0, 2.2, 2.5):
            ua = null_u(cg, 200000)
            fa[f"K{K}_c{cg}"] = dict(ana=round(guc(ua, e, K), 3), ana_ve_LOO=round(guc(ua, e, K, loo=True, u0=u0), 3))
        # karışım: kümelerin π'si 3 kat şişmiş (eşik altı postsismik, volkan), kalanı c = 1
        for pi in (0.1, 0.2, 0.3, 0.4):
            ua = np.where(rng.random(200000) < pi, null_u(3.0, 200000), null_u(1.0, 200000))
            fa[f"K{K}_karisim_pi{pi}_c3"] = dict(ana=round(guc(ua, e, K), 3),
                                                ana_ve_LOO=round(guc(ua, e, K, loo=True, u0=u0), 3))
        # epok yanlılığı: olaylar 2008 epoğu gibi gürültülü (alt küme yeniden örneklenir), bölge c = 1 / 1,3
        m08 = T == "2008"
        for cr in (1.0, 1.3):
            k = kat[m08]
            ua = P.u(cr * S[m08], k)
            fa[f"K{K}_epok2008_c{cr}"] = dict(ana=round(guc(ua, e, K), 3))
    out["yanlis_alarm_c0_1.64"] = fa
    print(json.dumps(fa, ensure_ascii=False), flush=True)

    # 6. Kaydırılmış yerinde plasebo kuralı: K_p küme plasebo; ĉ_üst = AUC→c çevirisiyle ū_p'nin tek yanlı %95 üst
    # sınırı; c0* = max(1,64, ĉ_üst). Bölge şişmesi c_gercek, plasebo ve olayda aynı (bağımsız çekiliş).
    cs = np.linspace(0.5, 4.0, 351)
    auc_c = np.array([P.u(c * S, kat).mean() for c in cs])
    u_by_c = {}

    def u_c(c):
        key = round(c, 2)
        if key not in u_by_c:
            u_by_c[key] = null_u(key, 60000)
        return u_by_c[key]

    yp = {}
    for K, Kp in ((12, 6), (12, 10), (20, 10)):
        for cg in (1.0, 1.64, 2.0, 2.5):
            nrep = 1500
            var = 0
            c0s = []
            for _ in range(nrep):
                up = rng.choice(u_c(cg), Kp)
                ust = up.mean() + 1.645 * up.std(ddof=1) / np.sqrt(Kp)
                ch = float(np.interp(min(ust, auc_c[-1]), auc_c, cs))
                c0 = max(1.64, round(ch, 2))
                c0s.append(c0)
            c0s = np.array(c0s)
            # eşik c0'a bağlı; c0 değerlerini 0,05'lik ızgaraya yuvarla
            c0r = np.round(c0s * 20) / 20
            tot = 0.0
            for cv in np.unique(c0r):
                w = float((c0r == cv).mean())
                e = float(np.quantile(rng.choice(null_u(cv, 100000), (40000, K)).mean(1), 1 - ALFA))
                tot += w * guc(u_c(cg), e, K, nb=8000)
            yp[f"K{K}_Kp{Kp}_c{cg}"] = dict(yanlis_alarm=round(tot, 3), c0_medyan=round(float(np.median(c0s)), 2))
            print("plasebo", K, Kp, cg, yp[f"K{K}_Kp{Kp}_c{cg}"], flush=True)
    out["kaydirilmis_plasebo_kurali"] = yp
    out["ayar"] = dict(tohum=TOHUM, alfa=ALFA, guc=GUC)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k not in ("MDE",)}, ensure_ascii=False, indent=0)[:6000])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
