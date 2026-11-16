#!/usr/bin/env python3
"""TR-1b sınırlı koşu: güç ve en küçük görülebilir etki (MDE) hesabı. YALNIZ YAPAY VERİ.

Hiçbir GNSS serisi, hiçbir olay penceresi okunmaz. Tek dış girdi: TR-11'in commit edilmiş sonuç nicelikleri
(kayit/turetme/tr11/tr11_sonuc.json; depremsiz 665 küme-pencere): q50, q90, q95, q99 ve n_y katmanları.

Yapay sıfır modeli (varsayım, belge §4.1):
  küme başına n_y yakın istasyon (TR-11 katman sayılarına göre 3–8); istasyon artık hız-değişim vektörü
  w_i ~ N2(0, σ_c² I); σ_c küme başına log-normal(μ, τ); S = median_i |w_i|.
  μ, τ, TR-11'in dört niceliğine ızgara aramasıyla uydurulur; katman q95'leri doğrulama olarak yazılır.
Sinyal (H1): bütün yakın istasyonlara aynı g vektörü (mm/yıl) eklenir, referansa eklenmez:
  S = median_i |w_i + g|  (en elverişli durum: uyumlu sinyal). Bilgi: istasyon başına a_i ~ U(0, 1) ile dağınık.
Sınamalar (K bağımsız olay kümesi, tek yanlı α = 0,05):
  A  ortalama yüzdelik ū = ort F0(S_k) (AUC karşılığı); sıfır dağılımı H0' altında yapaydan kesin (Monte Carlo).
  B  q95 aşım sayısı X ~ Binom(K, p0'); kesin binom eşiği.
  H0' : olay S'i c0 × S_sıfır dağılır (c0 = 1: saf TR-11 tabanı; c0 > 1: aktif bölge yanlılığı payı).
Kullanım: python3 -I -B tr1b_mde.py <tr11_sonuc.json> <cikti.json>
"""
import json
import math
import sys

import numpy as np

sys.dont_write_bytecode = True
TOHUM = 20261116
ALFA, GUC = 0.05, 0.80
NY_KATMAN = [((3, 4), 213), ((5, 7), 253), ((8, 8), 199)]   # TR-11 tr11_sonuc.md kırılım tablosu


def ny_cek(rng, n):
    w = np.array([c for _, c in NY_KATMAN], float)
    k = rng.choice(len(NY_KATMAN), n, p=w / w.sum())
    lo = np.array([NY_KATMAN[i][0][0] for i in k])
    hi = np.array([NY_KATMAN[i][0][1] for i in k])
    return lo + (rng.random(n) * (hi - lo + 1)).astype(int)


def S_uret(rng, n, mu, tau, g=0.0, dagin=False, ny=None, c0=1.0):
    ny = ny_cek(rng, n) if ny is None else ny
    sig = np.exp(mu + tau * rng.standard_normal(n))
    out = np.empty(n)
    for k in range(3, 9):
        sec = ny == k
        m = int(sec.sum())
        if m == 0:
            continue
        w = rng.standard_normal((m, k, 2)) * sig[sec, None, None]
        if g:
            a = rng.random((m, k)) if dagin else np.ones((m, k))
            w[:, :, 0] += g * a
        out[sec] = np.median(np.hypot(w[:, :, 0], w[:, :, 1]), axis=1)
    return c0 * out, ny


def uydur(rng, hedef):
    qs = np.array([0.5, 0.9, 0.95, 0.99])
    h = np.array([hedef[k] for k in ("q50", "q90", "q95", "q99")])
    en = None
    ny = ny_cek(rng, 40000)
    z = rng.standard_normal(40000)
    wb = rng.standard_normal((40000, 8, 2))
    M = np.empty(40000)
    for k in range(3, 9):   # sıfır altında S = σ_c × median|w| (ölçek doğrusal)
        sec = ny == k
        M[sec] = np.median(np.hypot(wb[sec, :k, 0], wb[sec, :k, 1]), axis=1)
    for tau in np.arange(0.0, 1.01, 0.025):
        for mu in np.arange(-1.0, 1.0, 0.02):
            S = M * np.exp(mu + tau * z)
            q = np.quantile(S, qs)
            e = float(np.sum(np.log(q / h) ** 2))
            if en is None or e < en[0]:
                en = (e, float(mu), float(tau), q.tolist())
    return en


def ihall_esik(rng, K, n=400000):
    """K tane U(0,1) ortalamasının üst %5 niceliği (c0 = 1 için ū'nun kesin sıfır eşiği)."""
    return float(np.quantile(rng.random((n, K)).mean(1), 1 - ALFA))


def binom_esik(K, p0):
    """P(X >= c) <= α olan en küçük c ve gerçek α."""
    pmf = [math.comb(K, i) * p0 ** i * (1 - p0) ** (K - i) for i in range(K + 1)]
    kuyruk = np.cumsum(pmf[::-1])[::-1]
    for c in range(K + 1):
        if kuyruk[c] <= ALFA:
            return c, float(kuyruk[c])
    return K + 1, 0.0


def binom_guc(K, p1, c):
    return float(sum(math.comb(K, i) * p1 ** i * (1 - p1) ** (K - i) for i in range(c, K + 1)))


def main(tr11, cikti):
    rng = np.random.default_rng(TOHUM)
    d = json.load(open(tr11))["ana"]
    hedef = {k: d[k]["nokta"] for k in ("q50", "q90", "q95", "q99")}
    e, mu, tau, qfit = uydur(rng, hedef)
    out = dict(girdi=dict(tr11_nicelik=hedef), model=dict(mu=mu, tau=tau, uyum_hata=e, q_model=qfit))
    # büyük sıfır örneklemi: F0 ve katman doğrulaması
    S0, ny0 = S_uret(rng, 400000, mu, tau)
    S0s = np.sort(S0)
    F0 = lambda s: np.searchsorted(S0s, s, side="right") / len(S0s)
    q95_0 = float(np.quantile(S0, 0.95))
    out["model"]["katman_q95_model"] = {f"{lo}-{hi}": float(np.quantile(S0[(ny0 >= lo) & (ny0 <= hi)], 0.95))
                                        for (lo, hi), _ in NY_KATMAN}
    out["model"]["katman_q95_TR11"] = {"3-4": 2.759, "5-7": 2.24, "8-8": 1.94}
    # TR-11 kod denetimi (ii-b) karşılaştırması: 3 mm/yıl eklenince S'in medyan artışı (TR-11 MC beklentisi 2,17)
    ny = ny_cek(rng, 50000)
    st = rng.bit_generator.state
    a, _ = S_uret(rng, 50000, mu, tau, ny=ny)
    rng.bit_generator.state = st
    b, _ = S_uret(rng, 50000, mu, tau, g=3.0, ny=ny)
    out["model"]["g3_medyan_artis"] = float(np.median(b - a))
    out["model"]["g3_medyan_artis_TR11_mstar"] = 2.174

    g_list = [round(0.1 * i, 1) for i in range(0, 41)] + [4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 10.0]
    K_list = [5, 6, 8, 10, 11, 12, 15, 20, 27, 40]
    c0_list = [1.0, 1.3, 1.64]
    n_g = 30000
    tablo = {}
    for dagin in (False, True):
        u_g, x_g = {}, {}
        for g in g_list:
            S, _ = S_uret(rng, n_g, mu, tau, g=g, dagin=dagin)
            u_g[g] = F0(S)
            x_g[g] = S > q95_0
        tablo_d = {}
        for c0 in c0_list:
            S0c = c0 * S_uret(rng, n_g, mu, tau)[0]
            u0 = F0(S0c)
            p0 = float((S0c > q95_0).mean())
            tablo_c = dict(p0_q95=p0, AUC_H0=float(u0.mean()), K={})
            for K in K_list:
                nb = 20000
                esikA = float(np.quantile(rng.choice(u0, (nb, K)).mean(1), 1 - ALFA)) if c0 > 1 else \
                    ihall_esik(rng, K)
                cB, aB = binom_esik(K, p0)
                gA, gB = {}, {}
                for g in g_list:
                    gA[g] = float((rng.choice(u_g[g], (nb, K)).mean(1) > esikA).mean())
                    gB[g] = binom_guc(K, float(x_g[g].mean()), cB)

                def mde(gg):
                    for i in range(1, len(g_list)):
                        if gg[g_list[i]] >= GUC:
                            g0, g1 = g_list[i - 1], g_list[i]
                            p_0, p_1 = gg[g0], gg[g1]
                            return round(g0 + (GUC - p_0) * (g1 - g0) / max(p_1 - p_0, 1e-9), 2)
                    return None
                mA, mB = mde(gA), mde(gB)
                aucA = None
                if mA is not None:
                    S, _ = S_uret(rng, n_g, mu, tau, g=mA, dagin=dagin)
                    aucA = round(float(F0(S).mean()), 3)
                tablo_c["K"][str(K)] = dict(esik_ubar=round(esikA, 4), binom_c=cB, binom_alfa=round(aB, 4),
                                            MDE_g_A=mA, AUC_MDE_A=aucA, MDE_g_B=mB,
                                            guc_A={str(g): round(v, 3) for g, v in gA.items()},
                                            guc_B={str(g): round(v, 3) for g, v in gB.items()})
            tablo_d[str(c0)] = tablo_c
        tablo["daginik" if dagin else "uyumlu"] = tablo_d
        tablo["AUC_g_" + ("daginik" if dagin else "uyumlu")] = {str(g): round(float(u_g[g].mean()), 3)
                                                                for g in g_list}
        tablo["p_asim_g_" + ("daginik" if dagin else "uyumlu")] = {str(g): round(float(x_g[g].mean()), 3)
                                                                   for g in g_list}
    out["guc"] = tablo
    # ×0,5 / ×2 duyarlılığı (A sınaması, K = 12): MDE'nin yarısı ve iki katında güç; yarısı için gereken K
    duy = {}
    for kip, dagin in (("uyumlu", False), ("daginik", True)):
        for c0 in c0_list:
            m = tablo[kip][str(c0)]["K"]["12"]["MDE_g_A"]
            if m is None:
                continue
            S0c = c0 * S_uret(rng, n_g, mu, tau)[0]
            u0 = F0(S0c)
            r = dict(MDE_g=m)
            for ad, g in (("yari", m / 2), ("iki_kat", 2 * m)):
                ug = F0(S_uret(rng, n_g, mu, tau, g=g, dagin=dagin)[0])
                r[ad] = dict(g=round(g, 2), AUC=round(float(ug.mean()), 3))
                gk = None
                for K in [12, 16, 20, 25, 30, 40, 50, 60, 80, 100, 130, 160, 200, 300]:
                    e = float(np.quantile(rng.choice(u0, (8000, K)).mean(1), 1 - ALFA))
                    gu = float((rng.choice(ug, (8000, K)).mean(1) > e).mean())
                    if K == 12:
                        r[ad]["guc_K12"] = round(gu, 3)
                    if gu >= GUC and gk is None:
                        gk = K
                r[ad]["gereken_K"] = gk if gk is not None else "> 300"
            duy[f"{kip}_c0_{c0}"] = r
    out["duyarlilik_K12"] = duy
    out["ayar"] = dict(tohum=TOHUM, alfa=ALFA, guc=GUC, g_list=g_list, K_list=K_list, c0_list=c0_list,
                       q95_model=q95_0)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(out["model"], ensure_ascii=False))
    for kip in ("uyumlu", "daginik"):
        for c0 in c0_list:
            t = tablo[kip][str(c0)]
            print(kip, "c0", c0, "p0", round(t["p0_q95"], 3), "AUC_H0", round(t["AUC_H0"], 3))
            for K in K_list:
                r = t["K"][str(K)]
                print("   K", K, "A: esik", r["esik_ubar"], "MDE_g", r["MDE_g_A"], "AUC", r["AUC_MDE_A"],
                      "| B: c", r["binom_c"], "α", r["binom_alfa"], "MDE_g", r["MDE_g_B"])
    print("duyarlilik", json.dumps(duy, ensure_ascii=False))
    print("AUC(g) uyumlu", tablo["AUC_g_uyumlu"])
    print("p_asim(g) uyumlu", tablo["p_asim_g_uyumlu"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
