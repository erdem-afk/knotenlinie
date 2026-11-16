#!/usr/bin/env python3
"""TR-13b sınırlı koşu: ETAS'tan kalibre edilmiş kesin sınama, K = 14 ile MDE (f cinsinden). YALNIZ YAPAY VERİ.

Gerçek katalogda hiçbir yerelleşme ölçüsü hesaplanmaz. ETAS üreteci, GK74 ve V(0,5)/z ölçüsü TR-13 güç betiğinden
(kayit/turetme/tr13/tr13_guc.py) aynen alınır; bu betik yalnız sınama düzenlerini ekler.

Her yapay bölge (R = 80 km, 5 y ısınma + 10 y; ana şok t = 10 y):
  z_olay   : önce [7, 10) y, referans [0, 7) y        (TR-13 tanımı)
  z_plasebo: önce [4, 7) y,  referans [0, 4) y        (bölgenin kendi geçmişi; olayın referansıyla örtüşür)
  sinyal   : [7, 10) y arka plan olaylarının f kesri gelecek kırık çizgisine (2 km) taşınır.
Sınamalar (K bölge, tek yanlı α = 0,05, yerelleşme = z küçük):
  T1 ETAS-kalibre ortalama z: eşik, sinyalsiz ETAS z'lerinden K'lık ortalamaların %5 niceliği.
  T2 kendi geçmişiyle eşli fark d = z_olay − z_plasebo, kesin işaret çevirme (2^K desen).
  T3 bölge başına ETAS-kalibre tek pencere eşiği (sinyalsiz z'nin %5 niceliği) aşım sayısı, kesin binom p0 = 0,05.
Gerçek α: eşik dallanma n = 0,6 ile kalibre edilip n = 0,4 / 0,8 ETAS'ında ve N3bg kaymasında ölçülür.
Kullanım: python3 -I -B tr13b_mde.py <cikti.json> [hizli]
"""
import itertools
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tr13"))
import tr13_guc as G  # noqa: E402

TOHUM = 20261116
YIL = G.YIL
ALFA, GUC = 0.05, 0.80
K_ANA = 14


def dallanma(n):
    G.DAL = n
    G.K_VERIM = G.verim_sabiti()


def bolge(rng, Nh, f, R=80.0, B_ref=100):
    F = G.faylar(rng, R)
    R_sim = R + 30
    mu = Nh / (3 * YIL) * (R_sim / R) ** 2
    t, x, y, m, _ = G.etas(rng, R_sim, mu, -5 * YIL, 10 * YIL, F, f_lok=f, lok_t0=7 * YIL)
    bg = G.gk74_xy(t, x, y, m)
    tt, xx, yy = t[bg], x[bg], y[bg]
    g, ic = G.izgara(R)
    ze, n = G.z_olcu(rng, xx, yy, tt, R, 7 * YIL, 10 * YIL, 0.0, 0.5, g, ic, B_ref)
    zp, _ = G.z_olcu(rng, xx, yy, tt, R, 4 * YIL, 7 * YIL, 0.0, 0.5, g, ic, B_ref)
    # kırık bandı payı (|uzaklık| <= 2 km, ilk fay) önce-pencerede: etki büyüklüğünü 'kat' olarak okumak için
    x0, y0, az, Lf = F[0]
    pre = (tt >= 7 * YIL) & (np.hypot(xx, yy) <= R)
    ux, uy = math.cos(az), math.sin(az)
    s = xx[pre] * ux + yy[pre] * uy
    w = -xx[pre] * uy + yy[pre] * ux
    band = float(((np.abs(w) <= 2.0) & (np.abs(s) <= Lf / 2)).mean()) if pre.any() else np.nan
    return ze, zp, n, band


def kalibre(rng, N, deneme=30):
    ns = [bolge(rng, N, 0.0, B_ref=2)[2] for _ in range(deneme)]
    return N * N / max(float(np.mean(ns)), 1.0)


def havuz(rng, Nh, f, n):
    r = [bolge(rng, Nh, f) for _ in range(n)]
    a = np.array(r, float)
    a = a[np.isfinite(a[:, 0]) & np.isfinite(a[:, 1])]
    return a


ISARETLER = None


def isaret_p(d):
    """Kesin tek yanlı işaret çevirme p'si (ortalama d küçükse yerelleşme)."""
    s = (ISARETLER[:, : len(d)] * d).sum(1)
    return float((s <= d.sum() + 1e-12).mean())


def binom_esik(K, p0=0.05):
    pmf = [math.comb(K, i) * p0 ** i * (1 - p0) ** (K - i) for i in range(K + 1)]
    kuyruk = np.cumsum(pmf[::-1])[::-1]
    for c in range(K + 1):
        if kuyruk[c] <= ALFA:
            return c, float(kuyruk[c])
    return K + 1, 0.0


def sinamalar(rng, z0e, z0d, havuz_f, K, nb):
    """havuz_f: (n, 4) [ze, zp, n, band]. z0e, z0d: kalibrasyon havuzu (sinyalsiz, n = 0,6)."""
    e1 = float(np.quantile(rng.choice(z0e, (40000, K)).mean(1), ALFA))
    e3 = float(np.quantile(z0e, ALFA))
    c3, a3 = binom_esik(K)
    i = rng.integers(0, len(havuz_f), (nb, K))
    ze, zp = havuz_f[i, 0], havuz_f[i, 1]
    r1 = float((ze.mean(1) < e1).mean())
    r2 = float(np.mean([isaret_p(ze[j] - zp[j]) <= ALFA for j in range(nb)]))
    r3 = float(((ze < e3).sum(1) >= c3).mean())
    return dict(T1=round(r1, 3), T2=round(r2, 3), T3=round(r3, 3)), dict(e1=e1, e3=e3, c3=c3, a3=a3)


def mde(fs, gs):
    for i in range(1, len(fs)):
        if gs[i] >= GUC:
            return round(fs[i - 1] + (GUC - gs[i - 1]) * (fs[i] - fs[i - 1]) / max(gs[i] - gs[i - 1], 1e-9), 3)
    return None


def main(cikti, hizli=False):
    global ISARETLER
    rng = np.random.default_rng(TOHUM)
    ISARETLER = np.array(list(itertools.product([-1.0, 1.0], repeat=K_ANA)))
    t0 = time.time()
    n0, nf, nb = (150, 80, 300) if hizli else (1500, 500, 2000)
    f_list = [0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
    out = dict(ayar=dict(tohum=TOHUM, K=K_ANA, n0=n0, nf=nf, nb=nb, f_list=f_list, B_ref=100,
                         plasebo="önce [t-6y, t-3y), referans [t-10y, t-6y)",
                         etas=dict(Mc=G.MC, b=G.B, Mmax=G.MMAX, dallanma_kalibrasyon=0.6)), N={})
    for N in (50, 100):
        dallanma(0.6)
        Nh = kalibre(rng, N)
        cal = havuz(rng, Nh, 0.0, n0)                       # kalibrasyon havuzu
        z0e, z0d = cal[:, 0], cal[:, 0] - cal[:, 1]
        d = dict(N3bg_hedef=N, N3bg_gercek=float(cal[:, 2].mean()), z0_ort=float(z0e.mean()),
                 z0_sd=float(z0e.std(ddof=1)), d0_ort=float(z0d.mean()), d0_sd=float(z0d.std(ddof=1)),
                 tek_pencere_anma_yanlis_alarm=float((z0e < -1.645).mean()),
                 bant_payi_f0=float(np.nanmean(cal[:, 3])), guc={}, gercek_alfa={})
        # sinyal havuzları (n = 0,6) — güç
        bant = {}
        for f in f_list:
            hv = havuz(rng, Nh, f, nf) if f > 0 else havuz(rng, Nh, 0.0, nf)
            g, esik = sinamalar(rng, z0e, z0d, hv, K_ANA, nb)
            d["guc"][str(f)] = g
            bant[str(f)] = float(np.nanmean(hv[:, 3]))
            print(N, "f", f, g, round(time.time() - t0), "s", flush=True)
        d["esikler"] = esik
        d["bant_payi"] = bant
        d["MDE_f"] = {k: mde(f_list, [d["guc"][str(f)][k] for f in f_list]) for k in ("T1", "T2", "T3")}
        # gerçek α: kalibrasyon n = 0,6 / N; veri n = 0,4 ve 0,8, ayrıca N kayması (×0,5, ×2)
        for ad, (n_dal, Nv) in {"n0.4": (0.4, N), "n0.8": (0.8, N), "N_x0.5": (0.6, N // 2),
                                "N_x2": (0.6, 2 * N)}.items():
            dallanma(n_dal)
            Nh2 = kalibre(rng, Nv)
            hv = havuz(rng, Nh2, 0.0, nf)
            g, _ = sinamalar(rng, z0e, z0d, hv, K_ANA, nb)
            d["gercek_alfa"][ad] = dict(g, N3bg_gercek=float(hv[:, 2].mean()))
            print(N, "alfa", ad, g, round(time.time() - t0), "s", flush=True)
        dallanma(0.6)
        out["N"][str(N)] = d
    # ×0,5 / ×2 ve gereken K (T1 ve T2, N = 50 ve 100 havuzları yeniden kullanılmaz; aynı ayarla yeni havuz)
    duy = {}
    for N in (50, 100):
        dallanma(0.6)
        Nh = kalibre(rng, N)
        cal = havuz(rng, Nh, 0.0, n0)
        z0e, z0d = cal[:, 0], cal[:, 0] - cal[:, 1]
        for test in ("T1", "T2"):
            m = out["N"][str(N)]["MDE_f"][test]
            if m is None:
                continue
            r = dict(MDE_f=m)
            for ad, f in (("yari", m / 2), ("iki_kat", min(2 * m, 0.95))):
                hv = havuz(rng, Nh, f, nf)
                rr = dict(f=round(f, 3))
                gk = None
                for K in (14, 20, 30, 40, 60, 80, 120):
                    if test == "T1":
                        e1 = float(np.quantile(rng.choice(z0e, (20000, K)).mean(1), ALFA))
                        gu = float((rng.choice(hv[:, 0], (4000, K)).mean(1) < e1).mean())
                    else:   # büyük K'de işaret çevirmenin normal yaklaşımı (yalnız gereken K için)
                        dd = hv[:, 0] - hv[:, 1]
                        sd0 = z0d.std(ddof=1)
                        mm = rng.choice(dd, (4000, K)).mean(1)
                        gu = float((mm < -1.645 * sd0 / math.sqrt(K)).mean())
                    if K == 14:
                        rr["guc_K14"] = round(gu, 3)
                    if gu >= GUC and gk is None:
                        gk = K
                rr["gereken_K"] = gk if gk is not None else "> 120"
                r[ad] = rr
            duy[f"N{N}_{test}"] = r
            print("duy", N, test, r, round(time.time() - t0), "s", flush=True)
    out["duyarlilik"] = duy
    out["sure_s"] = round(time.time() - t0)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)
    for N, d in out["N"].items():
        print(N, {k: v for k, v in d.items() if k not in ("guc", "gercek_alfa")})
        print("   gercek_alfa", d["gercek_alfa"])


if __name__ == "__main__":
    main(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "hizli")
