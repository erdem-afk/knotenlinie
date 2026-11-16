#!/usr/bin/env python3
"""TR-13b INCELEME-1: T1'in (ETAS-kalibre ortalama z, K = 14) yanlış alarmı ETAS dışı gerçekçi bozulmalar altında.
YALNIZ YAPAY VERİ. Gerçek katalogda hiçbir ölçü hesaplanmaz.

ETAS üreteci, GK74 ve V(0,5)/z ölçüsü kayit/turetme/tr13/tr13_guc.py'den çağrılır (yazarın ölçüsünü sınamak için);
sınama düzeni, bozulmalar ve özet bu betikte bağımsız yazıldı.
Kalibrasyon: sinyalsiz ETAS (dallanma 0,6, pay_fay 0,6), N3bg ≈ 50 (ve doyma denetimi için 200).
Bozulmalar (veri tarafı; kalibrasyon bunları bilmez):
  D0  aynı ayar (bağımsız havuz)
  D1  durağan sürüler: bölgede yılda λ sürü (Poisson, 15 y boyunca); sürü = 15 olay, M 2,5–3,2, 3 km Gauss, 180 gün
  D2  yalnız önce-pencerede tek sürü (bölgelerin %30'unda), aynı sürü
  D7  ETAS verim üssü farklı: α = 0,8 ln10 (kalibrasyon 1,0 ln10)
  D3  ağ yerel iyileşmesi: referans döneminde rastgele 20 km'lik bir dairede m < 3,0 olayları 0,4 olasılıkla görülür;
      önce-pencerede tam (geçici/yeni istasyon kümesi)
  D4  ağ yerel kaybı: önce-pencerede bölgenin bir kenar yarım düzleminde (x > 30 km) m < 3,0 olayları 0,3 olasılıkla
  D5  arka plan yapısı farklı: pay_fay 0,9 (kalibrasyon 0,6)
  D6  doyma: kalibrasyon ve veri aynı N3bg hedefi 200 (eşleşik kalibrasyon) — "≤ 100" kuralının α gerekçesi sınanır
Kullanım: python3 -I -B tr13b_inc1.py <cikti.json> [hizli|tam|buyuk|mde]  (tam: tohum 20261118; buyuk: 20261119)
"""
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tr13"))
import tr13_guc as G  # noqa: E402

YIL = G.YIL
R = 80.0
K = 14


def surular(rng, n_suru, T0, T1, F, R_sim, boy=15, sure=180.0):
    t, x, y, m = [], [], [], []
    for _ in range(n_suru):
        t0 = T0 + rng.random() * (T1 - T0 - sure)
        if rng.random() < 0.6:
            cx, cy = G.fay_noktasi(rng, F[rng.integers(len(F))], 1)
            cx, cy = cx[0], cy[0]
        else:
            rr, th = R * math.sqrt(rng.random()), rng.random() * 2 * math.pi
            cx, cy = rr * math.cos(th), rr * math.sin(th)
        t.append(t0 + rng.random(boy) * sure)
        x.append(cx + rng.normal(0, 3, boy))
        y.append(cy + rng.normal(0, 3, boy))
        u = rng.random(boy)
        beta = math.log(10)
        m.append(2.5 - np.log(1 - u * (1 - math.exp(-beta * 0.7))) / beta)
    if not t:
        return [np.empty(0)] * 4
    return [np.concatenate(a) for a in (t, x, y, m)]


def bolge(rng, Nh, sen, f=0.0):
    pay = 0.9 if sen == "D5" else 0.6
    F = G.faylar(rng, R)
    R_sim = R + 30
    mu = Nh / (3 * YIL) * (R_sim / R) ** 2
    t, x, y, m, _ = G.etas(rng, R_sim, mu, -5 * YIL, 10 * YIL, F, f_lok=f, lok_t0=7 * YIL, pay_fay=pay)
    if sen == "D1":
        ns = rng.poisson(LAM * 15)
        st, sx, sy, sm = surular(rng, ns, -5 * YIL, 10 * YIL, F, R_sim)
    elif sen == "D2":
        ns = int(rng.random() < 0.3)
        st, sx, sy, sm = surular(rng, ns, 7 * YIL, 10 * YIL - 2, F, R_sim)
    else:
        st = np.empty(0)
    if len(st):
        t, x, y, m = (np.concatenate(a) for a in ((t, st), (x, sx), (y, sy), (m, sm)))
        o = np.argsort(t)
        t, x, y, m = t[o], x[o], y[o], m[o]
    keep = np.ones(len(t), bool)
    if sen == "D3":
        rr, th = 60 * math.sqrt(rng.random()), rng.random() * 2 * math.pi
        cx, cy = rr * math.cos(th), rr * math.sin(th)
        ic = (np.hypot(x - cx, y - cy) <= 20) & (t < 7 * YIL) & (m < 3.0)
        keep[ic] = rng.random(int(ic.sum())) < 0.4
    if sen == "D4":
        ic = (x > 30) & (t >= 7 * YIL) & (m < 3.0)
        keep[ic] = rng.random(int(ic.sum())) < 0.3
    t, x, y, m = t[keep], x[keep], y[keep], m[keep]
    bg = G.gk74_xy(t, x, y, m)
    g, ic = G.izgara(R)
    z, n = G.z_olcu(rng, x[bg], y[bg], t[bg], R, 7 * YIL, 10 * YIL, 0.0, 0.5, g, ic, 100)
    return z, n


def kalibre(rng, N, sen="D0", deneme=25):
    ns = [bolge(rng, N, sen)[1] for _ in range(deneme)]
    return N * N / max(float(np.mean(ns)), 1.0)


def havuz(rng, Nh, sen, n, f=0.0):
    a = np.array([bolge(rng, Nh, sen, f) for _ in range(n)], float)
    return a[np.isfinite(a[:, 0])]


def T1_red(rng, z0, za, nb=40000):
    e = float(np.quantile(rng.choice(z0, (nb, K)).mean(1), 0.05))
    return float((rng.choice(za, (nb, K)).mean(1) < e).mean()), e


LAM = 0.4


def main(cikti, kip="tam"):
    rng = np.random.default_rng({"hizli": 1, "tam": 20261118, "buyuk": 20261119}[kip])
    n0, nd = {"hizli": (120, 60), "tam": (800, 300), "buyuk": (3000, 1500)}[kip]
    t0 = time.time()
    out = dict(K=K, n0=n0, nd=nd, lam_suru_yil=LAM, sen={})
    Nh = kalibre(rng, 50)
    z0 = havuz(rng, Nh, "D0", n0)
    out["kal_N50"] = dict(N3bg=float(z0[:, 1].mean()), z_ort=float(z0[:, 0].mean()), z_sd=float(z0[:, 0].std(ddof=1)))
    print("kal", out["kal_N50"], round(time.time() - t0), flush=True)
    for sen in ("D0", "D1", "D2", "D3", "D4", "D5", "D7"):
        if sen == "D7":
            G.ALFA = 0.8 * math.log(10)
            G.K_VERIM = G.verim_sabiti()
        za = havuz(rng, Nh, sen, nd)
        G.ALFA = 1.0 * math.log(10)
        G.K_VERIM = G.verim_sabiti()
        a, e = T1_red(rng, z0[:, 0], za[:, 0])
        out["sen"][sen] = dict(alfa_T1=round(a, 3), esik=round(e, 3), z_ort=round(float(za[:, 0].mean()), 3),
                               z_sd=round(float(za[:, 0].std(ddof=1)), 3), N3bg=round(float(za[:, 1].mean()), 1),
                               tek_pencere_5=round(float((za[:, 0] < np.quantile(z0[:, 0], 0.05)).mean()), 3))
        print(sen, out["sen"][sen], round(time.time() - t0), flush=True)
    # D6: doyma, eşleşik kalibrasyon (N3bg hedef 200)
    Nh2 = kalibre(rng, 200, deneme=12)
    z02 = havuz(rng, Nh2, "D0", n0 // 2)
    za2 = havuz(rng, Nh2, "D0", nd // 2)
    a, e = T1_red(rng, z02[:, 0], za2[:, 0])
    zf2 = havuz(rng, Nh2, "D0", nd // 2, f=0.3)
    gu, _ = T1_red(rng, z02[:, 0], zf2[:, 0])
    out["D6_doyma_eslesik"] = dict(N3bg=round(float(z02[:, 1].mean()), 1), z_sd=round(float(z02[:, 0].std(ddof=1)), 3),
                                   alfa_T1=round(a, 3), guc_f0_3=round(gu, 3))
    print("D6", out["D6_doyma_eslesik"], round(time.time() - t0), flush=True)
    out["sure_s"] = round(time.time() - t0)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)


def mde_kos(cikti):
    """T1 MDE'sinin bağımsız yeniden hesabı (K = 14; N3bg 50 ve 100; sinyal tr13_guc.arka_plan f_lok ile)."""
    rng = np.random.default_rng(20261120)
    fl = [0.0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4]
    out = {}
    for N in (50, 100):
        Nh = kalibre(rng, N)
        z0 = havuz(rng, Nh, "D0", 2000)[:, 0]
        gs = []
        for f in fl:
            za = havuz(rng, Nh, "D0", 600, f=f)[:, 0]
            gs.append(T1_red(rng, z0, za)[0])
            print(N, f, round(gs[-1], 3), flush=True)
        m = None
        for i in range(1, len(fl)):
            if gs[i] >= 0.8:
                m = round(fl[i - 1] + (0.8 - gs[i - 1]) * (fl[i] - fl[i - 1]) / max(gs[i] - gs[i - 1], 1e-9), 3)
                break
        out[str(N)] = dict(guc=dict(zip(map(str, fl), [round(g, 3) for g in gs])), MDE_f=m)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "mde":
        mde_kos(sys.argv[1])
    else:
        main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "tam")
