#!/usr/bin/env python3
"""TR-13 güç kapısı (yapay veri; gerçek katalogda yerelleşme ölçüsü HESAPLANMAZ).

Basit uzay-zaman ETAS üreteci + GK74 kümesizleştirme + yerelleşme ölçüsü (kesirsel alan V(q), BZ20 tanımına en
yakın okunabilen biçim; §2 TR-13_SAYIM.md). Üç iş:
  (1) yanlış alarm: sinyalsiz ETAS'ta tek pencere için P(z < -1,645);
  (2) güç: önce-pencerede arka plan olaylarının f kesri gelecekteki kırık çizgisine (genişlik 2 km) taşınırsa,
      K bağımsız bölgenin ortalama z'si ile tek yanlı α = 0,05 sınamada güç; güç 0,8 için en küçük f ve
      standartlaştırılmış etki d = (E[z|f] - E[z|0]) / sd(z|0);
  (3) ETAS'ın kendi "ana şok öncesi" etkisi: uzun ETAS kataloğunda M >= 5,5 olaylardan önceki pencerelerin z'si,
      rastgele pencerelerinkine karşı (sinyal eklenmeden).

Kullanım: python3 -I -B tr13_guc.py <cikti.json> <hizli|tam> <gk|kahin> <N1,N2,...> <oncesi|-->
Tohum sabit (20261112). Yalnız numpy.
"""
import json
import math
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
TOHUM = 20261112

# ---- ETAS (yaygın Kaliforniya değerleri; bkz. belge §3.1) ----
MC, B, MMAX = 2.5, 1.0, 7.5
ALFA = 1.0 * math.log(10)        # verim ∝ exp(ALFA (m - MC)), yani 10^(1,0 (m-Mc))
P_OMORI, C_GUN = 1.1, 0.01
Q_UZ, D0_KM, GAMMA = 1.5, 0.5, 0.5   # f(r) ∝ (r² + d²)^-q, d = D0 10^(GAMMA (m - MC))
DAL = 0.6                        # dallanma oranı n
T_UST_GUN = 3650.0 * 5           # tetikleme zamanı kesmesi (50 y), kütle düzeltmesiyle
HUCRE_KM = 5.0
W_KM = 2.0                       # kırık çizgisi Gauss yarı genişliği
YIL = 365.25


def gr(rng, n):
    beta = B * math.log(10)
    u = rng.random(n)
    return MC - np.log(1 - u * (1 - math.exp(-beta * (MMAX - MC)))) / beta


def omori_t(rng, n):
    # p > 1, [0, T_UST] kesik Omori örneklemi
    a = 1 - P_OMORI
    lo, hi = C_GUN ** a, (T_UST_GUN + C_GUN) ** a
    return (lo + rng.random(n) * (hi - lo)) ** (1 / a) - C_GUN


def verim_sabiti():
    # E[10^(α'(m-Mc))] GR altında; n = K * E[...]
    beta = B * math.log(10)
    mm = np.linspace(MC, MMAX, 20001)
    pdf = beta * np.exp(-beta * (mm - MC)) / (1 - math.exp(-beta * (MMAX - MC)))
    e = np.trapezoid(pdf * np.exp(ALFA * (mm - MC)), mm) if hasattr(np, "trapezoid") else \
        np.trapz(pdf * np.exp(ALFA * (mm - MC)), mm)
    return DAL / e


K_VERIM = verim_sabiti()


def uzaysal(rng, m):
    d = D0_KM * 10 ** (GAMMA * (m - MC))
    u = rng.random(len(m))
    r = d * np.sqrt((1 - u) ** (-1 / (Q_UZ - 1)) - 1)
    th = rng.random(len(m)) * 2 * math.pi
    return r * np.cos(th), r * np.sin(th)


def faylar(rng, R, n_fay=5):
    """Arka plan yapısı: n_fay doğru parçası (20–60 km), ilki 'gelecek kırık' (uzunluk L = R/2, merkezde)."""
    F = [(0.0, 0.0, rng.random() * math.pi, R / 2)]
    for _ in range(n_fay - 1):
        r0, th0 = R * math.sqrt(rng.random()), rng.random() * 2 * math.pi
        F.append((r0 * math.cos(th0), r0 * math.sin(th0), rng.random() * math.pi, 20 + 40 * rng.random()))
    return F


def fay_noktasi(rng, f, n):
    x0, y0, az, Lf = f
    s = (rng.random(n) - 0.5) * Lf
    w = rng.normal(0, W_KM, n)
    return x0 + s * math.cos(az) - w * math.sin(az), y0 + s * math.sin(az) + w * math.cos(az)


def arka_plan(rng, R_sim, mu_gun, T0, T1, F, f_lok=0.0, lok_t0=None, pay_fay=0.6):
    n = rng.poisson(mu_gun * (T1 - T0))
    t = T0 + rng.random(n) * (T1 - T0)
    x, y = np.empty(n), np.empty(n)
    tur = rng.random(n)
    k_fay = rng.integers(0, len(F), n)
    for i in range(n):
        if tur[i] < pay_fay:
            xi, yi = fay_noktasi(rng, F[k_fay[i]], 1)
            x[i], y[i] = xi[0], yi[0]
        else:
            rr, th = R_sim * math.sqrt(rng.random()), rng.random() * 2 * math.pi
            x[i], y[i] = rr * math.cos(th), rr * math.sin(th)
    if f_lok > 0 and lok_t0 is not None:
        sec = (t >= lok_t0) & (rng.random(n) < f_lok)
        if sec.any():
            xs, ys = fay_noktasi(rng, F[0], int(sec.sum()))
            x[sec], y[sec] = xs, ys
    return t, x, y


def etas(rng, R_sim, mu_gun, T0, T1, F, **kw):
    t, x, y = arka_plan(rng, R_sim, mu_gun, T0, T1, F, **kw)
    m = gr(rng, len(t))
    T, X, Y, M, BG = [t], [x], [y], [m], [np.ones(len(t), bool)]
    gt, gx, gy, gm = t, x, y, m
    while len(gt):
        nk = rng.poisson(K_VERIM * np.exp(ALFA * (gm - MC)))
        if nk.sum() == 0:
            break
        pt, px, py, pm = np.repeat(gt, nk), np.repeat(gx, nk), np.repeat(gy, nk), np.repeat(gm, nk)
        ct = pt + omori_t(rng, len(pt))
        dx, dy = uzaysal(rng, pm)
        cm = gr(rng, len(pt))
        ok = ct < T1
        gt, gx, gy, gm = ct[ok], px[ok] + dx[ok], py[ok] + dy[ok], cm[ok]
        T.append(gt); X.append(gx); Y.append(gy); M.append(gm); BG.append(np.zeros(len(gt), bool))
    T, X, Y, M, BG = (np.concatenate(a) for a in (T, X, Y, M, BG))
    s = np.argsort(T)
    return T[s], X[s], Y[s], M[s], BG[s]


def gk74_xy(t_gun, x, y, m):
    n = len(m)
    bg = np.ones(n, bool)
    d_km = 10 ** (0.1238 * m + 0.983)
    d_gun = np.where(m >= 6.5, 10 ** (0.032 * m + 2.7389), 10 ** (0.5409 * m - 0.547))
    for i in np.argsort(-m, kind="stable"):
        if not bg[i]:
            continue
        k0 = np.searchsorted(t_gun, t_gun[i] - d_gun[i])
        j1 = np.searchsorted(t_gun, t_gun[i] + d_gun[i], side="right")
        idx = np.arange(k0, j1)
        idx = idx[(idx != i) & (m[idx] <= m[i])]
        if len(idx) == 0:
            continue
        r = np.hypot(x[idx] - x[i], y[idx] - y[i])
        bg[idx[r <= d_km[i]]] = False
    return bg


def izgara(R):
    g = np.arange(-R, R, HUCRE_KM) + HUCRE_KM / 2
    gx, gy = np.meshgrid(g, g)
    ic = np.hypot(gx, gy) <= R
    return g, ic


def V_q(x, y, R, q, g, ic):
    """Kesirsel alan: penceredeki olayların q kesrini içeren en az hücre sayısı / bölgedeki hücre sayısı."""
    n = len(x)
    if n == 0:
        return np.nan
    ix = np.clip(((x + R) // HUCRE_KM).astype(int), 0, len(g) - 1)
    iy = np.clip(((y + R) // HUCRE_KM).astype(int), 0, len(g) - 1)
    c = np.bincount(iy * len(g) + ix, minlength=len(g) ** 2)
    c = np.sort(c[ic.ravel()])[::-1]
    cs = np.cumsum(c)
    hedef = q * n
    k = int(np.searchsorted(cs, hedef))
    onceki = cs[k - 1] if k > 0 else 0
    kesir = (hedef - onceki) / c[k] if c[k] > 0 else 0
    return (k + kesir) / ic.sum()


def z_olcu(rng, x, y, t, R, t_pre0, t_pre1, t_ref0, q, g, ic, B_ref=200):
    """Önce-penceredeki V(q), referans pencereden aynı boyda çekilen alt örneklerin V(q) dağılımına göre z."""
    r = np.hypot(x, y) <= R
    pre = r & (t >= t_pre0) & (t < t_pre1)
    ref = r & (t >= t_ref0) & (t < t_pre0)
    n = int(pre.sum())
    if n < 5 or ref.sum() < n + 5:
        return np.nan, n
    v = V_q(x[pre], y[pre], R, q, g, ic)
    xr, yr = x[ref], y[ref]
    vs = np.empty(B_ref)
    for b in range(B_ref):
        s = rng.choice(len(xr), n, replace=False)
        vs[b] = V_q(xr[s], yr[s], R, q, g, ic)
    sd = vs.std(ddof=1)
    return ((v - vs.mean()) / sd if sd > 0 else np.nan), n


KUMESIZ = "gk"   # "gk": GK74 pencereleri; "kahin": ETAS'ın gerçek arka plan etiketi (ideal kümesizleştirme)


def bir_bolge(rng, N3hedef, f_lok, R=80.0, q=0.5, B_ref=200):
    """Bir yapay bölge: 5 y ısınma + 10 y (ref 7 y, önce 3 y). Önce-penceredeki GK74 arka plan sayısı ≈ N3hedef."""
    F = faylar(rng, R)
    R_sim = R + 30
    mu_gun = N3hedef / (3 * YIL) * (R_sim / R) ** 2   # ilk tahmin; kalibre() ölçekler
    T0, T1 = -5 * YIL, 10 * YIL
    t, x, y, m, gercek_bg = etas(rng, R_sim, mu_gun, T0, T1, F, f_lok=f_lok, lok_t0=7 * YIL)
    keep = t >= T0
    bg = gk74_xy(t[keep], x[keep], y[keep], m[keep]) if KUMESIZ == "gk" else gercek_bg[keep]
    tt, xx, yy = t[keep][bg], x[keep][bg], y[keep][bg]
    g, ic = izgara(R)
    return z_olcu(rng, xx, yy, tt, R, 7 * YIL, 10 * YIL, 0.0, q, g, ic, B_ref)


def kalibre(rng, N3hedef, deneme=20):
    """mu'yu önce-pencere GK74 arka plan sayısı N3hedef olacak biçimde ölçekle (tek düzeltme)."""
    ns = [bir_bolge(rng, N3hedef, 0.0, B_ref=2)[1] for _ in range(deneme)]
    return float(np.mean(ns))


def guc(z0, zf, K, rng, nb=20000):
    """Tek yanlı (yerelleşme = z küçük) ortalama-z sınaması; eşik sinyalsiz dağılımın K'lık ortalamalarından."""
    z0, zf = z0[np.isfinite(z0)], zf[np.isfinite(zf)]
    m0 = rng.choice(z0, (nb, K)).mean(1)
    esik = np.quantile(m0, 0.05)
    mf = rng.choice(zf, (nb, K)).mean(1)
    return float((mf < esik).mean()), float(esik)


def main(cikti, hizli=False, N_list=None, oncesi=True):
    rng = np.random.default_rng(TOHUM + (N_list[0] if N_list else 0) + (7 if KUMESIZ != "gk" else 0))
    t_bas = time.time()
    N_list = N_list or ([25, 50, 100, 200] if hizli else [25, 50, 100, 200, 400])
    f_list = [0.05, 0.1, 0.15, 0.2, 0.3, 0.5]
    n0, nf = (60, 40) if hizli else (400, 200)
    K_list = [10, 15, 20, 30]
    out = dict(parametre=dict(MC=MC, B=B, MMAX=MMAX, alfa_log10=ALFA / math.log(10), p=P_OMORI, c_gun=C_GUN,
                              q_uz=Q_UZ, d0_km=D0_KM, gamma=GAMMA, dallanma=DAL, hucre_km=HUCRE_KM,
                              w_km=W_KM, R_km=80.0, pencere="ref [t-10y, t-3y), önce [t-3y, t)", q_V=0.5,
                              tohum=TOHUM, n0=n0, nf=nf, kumesizlestirme=KUMESIZ), duzeyler={})
    # ölçek: mu -> N3 (bir kez, N=100'de) ve doğrusal ölçekleme
    for N in N_list:
        # basit kalibrasyon: hedef N için gerçekleşen ortalama n, sonra ölçek düzeltmesi
        ger = kalibre(rng, N)
        olcek = N / ger if ger > 0 else 1.0
        Nhedef = N * olcek
        r0 = [bir_bolge(rng, Nhedef, 0.0) for _ in range(n0)]
        z0 = np.array([a[0] for a in r0])
        d = dict(N3bg_hedef=N, N3bg_gerceklesen_ort=float(np.mean([a[1] for a in r0])),
                 kalibrasyon_gercek_ilk=round(ger, 1), z0_ort=float(np.nanmean(z0)),
                 z0_sd=float(np.nanstd(z0, ddof=1)), yanlis_alarm_z_1645=float(np.nanmean(z0 < -1.645)),
                 yanlis_alarm_z_2326=float(np.nanmean(z0 < -2.326)), z0_q05=float(np.nanquantile(z0, 0.05)),
                 sinyal={})
        for f in f_list:
            zf = np.array([bir_bolge(rng, Nhedef, f)[0] for _ in range(nf)])
            dd = (np.nanmean(zf) - np.nanmean(z0)) / np.nanstd(z0, ddof=1)
            d["sinyal"][str(f)] = dict(z_ort=float(np.nanmean(zf)), d_std=float(dd),
                                       tek_pencere_algilama_z1645=float(np.nanmean(zf < -1.645)),
                                       guc_K={str(K): guc(z0, zf, K, rng)[0] for K in K_list})
        for K in K_list:  # güç 0,8 için en küçük f (doğrusal ara değer; tekdüze değilse ilk geçiş)
            fs, gs = [0.0] + f_list, [0.05] + [d["sinyal"][str(f)]["guc_K"][str(K)] for f in f_list]
            fmin = None
            for i in range(1, len(fs)):
                if gs[i] >= 0.8:
                    fmin = fs[i - 1] + (0.8 - gs[i - 1]) * (fs[i] - fs[i - 1]) / max(gs[i] - gs[i - 1], 1e-9)
                    break
            d.setdefault("f_min_guc08", {})[str(K)] = None if fmin is None else round(fmin, 3)
        out["duzeyler"][str(N)] = d
        print(N, json.dumps({k: v for k, v in d.items() if k != "sinyal"}),
              {f: (round(v["d_std"], 2), v["guc_K"]["20"]) for f, v in d["sinyal"].items()},
              round(time.time() - t_bas), "s", flush=True)
    if oncesi:
        out["etas_ana_sok_oncesi"] = etas_oncesi(rng, 2000 if hizli else 6000)
        print("etas öncesi", out["etas_ana_sok_oncesi"], round(time.time() - t_bas), "s", flush=True)
    json.dump(out, open(cikti, "w"), indent=1)


def etas_oncesi(rng, yil, R=80.0, N3=100, M_hedef=5.5, r_hedef=40.0, n_rast=400):
    """Sinyalsiz uzun ETAS: merkeze <= r_hedef km'deki M >= M_hedef olaylardan önceki z, rastgele zamanlardakine
    karşı. Önce-pencere ve referans: [t-3y, t), [t-10y, t-3y). Bölge merkezde, R = 80 km."""
    F = faylar(rng, R)
    R_sim = R + 30
    mu_gun = N3 / (3 * YIL) * (R_sim / R) ** 2 * 1.0
    T0, T1 = -10 * YIL, yil * YIL
    t, x, y, m, _ = etas(rng, R_sim, mu_gun, T0, T1, F)
    bg = gk74_xy(t, x, y, m)
    tt, xx, yy = t[bg], x[bg], y[bg]
    g, ic = izgara(R)
    hedef = t[(m >= M_hedef) & (np.hypot(x, y) <= r_hedef) & (t >= 0)]
    # aynı dizinin olayları: önceki hedeften 1 yıl içinde olan hedefler atılır (ilk olay kalır)
    h2 = [h for i, h in enumerate(hedef) if i == 0 or h - hedef[i - 1] > YIL]
    zh = np.array([z_olcu(rng, xx, yy, tt, R, h - 3 * YIL, h, h - 10 * YIL, 0.5, g, ic)[0] for h in h2])
    rast = rng.random(n_rast) * yil * YIL
    zr = np.array([z_olcu(rng, xx, yy, tt, R, h - 3 * YIL, h, h - 10 * YIL, 0.5, g, ic)[0] for h in rast])
    zh, zr = zh[np.isfinite(zh)], zr[np.isfinite(zr)]
    return dict(yil=yil, M_hedef=M_hedef, n_hedef=int(len(zh)), n_rastgele=int(len(zr)),
                z_hedef_ort=float(zh.mean()) if len(zh) else None, z_rast_ort=float(zr.mean()),
                z_rast_sd=float(zr.std(ddof=1)),
                fark_std=float((zh.mean() - zr.mean()) / zr.std(ddof=1)) if len(zh) else None,
                fark_se=float(zr.std(ddof=1) / math.sqrt(max(len(zh), 1))),
                yanlis_alarm_hedef_z1645=float((zh < -1.645).mean()) if len(zh) else None,
                yanlis_alarm_rast_z1645=float((zr < -1.645).mean()), n_olay=int(len(t)))


if __name__ == "__main__":
    a = sys.argv[1:]
    KUMESIZ = a[2]
    main(a[0], a[1] == "hizli", [int(v) for v in a[3].split(",")], a[4] == "oncesi")
