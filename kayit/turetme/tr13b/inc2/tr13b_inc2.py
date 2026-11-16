#!/usr/bin/env python3
"""TR-13b INCELEME-2: §9.4 kararı için plasebo denetimi seçeneklerinin yanlış alarmı ve MDE'si. YALNIZ YAPAY VERİ.

Gerçek katalogda hiçbir ölçü (V(q), z) hesaplanmaz; katalog indirilmez. Tek gerçek girdi, taslak sürüm 2'nin kullandığı
üstveri satırlarıdır (tr13_tamsayim.json: olay, küme, R, Mc, N3bg sayısı; liste() tr13b_v2_mde.py'den aynen).
ETAS üreteci, GK74 ve V(0,5)/z ölçüsü tr13_guc.py'den; sınama düzeni ve özet bu betikte bağımsız yazıldı.

Bileşim: listenin gerçek (R, N_son) değerleri, 15 üye / 13 küme / keşif dışı 10 küme (sürüm 2 ile aynı).
Kalibrasyon (sürüm 2'den farkı): mu her üyenin KENDİ R'sinde kalibre edilir (sürüm 2'nin M.kalibre'si R = 80'de
kalibre ediyor; bölüm K bunun büyük R'de N'yi ne kadar kaçırdığını ölçer). Sıfır havuzları dallanma 0,4/0,6/0,8;
veri dallanma 0,6, ayrı kalibrasyonla (gerçekteki kalibrasyon gürültüsünden biraz kötümser).
Veri senaryoları: D0 sinyalsiz; D1 durağan sürüler (INCELEME-1 tanımı: yılda 0,4 sürü, 15 olay, M 2,5–3,2, 3 km,
180 gün); D4 kenar ağ kaybı yalnız önce-pencerede (x > 0,375 R, R = 80'de INCELEME-1'in 30 km'si; m < 3 olaylar 0,3
olasılıkla görülür); sinyal f = 0,2 ... 0,6.
Kurallar (hepsi tek yanlı, yerelleşme = z küçük):
  R0  üç dallanmanın üçünde de, hem bütün liste (K 13) hem keşif dışı (K 10) T1 p <= 0,05      (Z5'siz "VAR")
  R1  R0 ve plasebo T1 p > 0,20 (dallanma 0,6 sıfırı; sürüm 2'nin tam kuralı)
  R1b R0 ve plasebo T1 p > 0,05
  R3  R0'ın eşikleri ortak bir a nicelinde; a, max(D1, D4) yanlış alarmı <= 0,05 olacak en büyük değer
  R4  fark d = z - z_p ile T1 (üç dallanma, iki liste; bilgi için)
Kullanım: python3 -I -B tr13b_inc2.py <cikti.json> [hizli]
"""
import json
import math
import multiprocessing as mp
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BURA, ".."))
sys.path.insert(0, os.path.join(BURA, "..", "..", "tr13"))
import tr13_guc as G  # noqa: E402
import tr13b_mde as M  # noqa: E402
import tr13b_v2_mde as V  # noqa: E402

TOHUM = 20261122
YIL = G.YIL
KESIF = {397, 979, 395}
DAL = (0.4, 0.6, 0.8)
F_LIST = (0.2, 0.3, 0.4, 0.5, 0.6)
HIZLI = False


def bolge(rng, Nh, sen, f, R):
    """V.bolge_B ile aynı; yalnız D4 kenarı 0,375 R (R = 80'de 30 km)."""
    F = G.faylar(rng, R)
    R_sim = R + 30
    mu = Nh / (3 * YIL) * (R_sim / R) ** 2
    t, x, y, m, _ = G.etas(rng, R_sim, mu, -5 * YIL, 10 * YIL, F, f_lok=f, lok_t0=7 * YIL)
    if sen == "D1":
        ns = rng.poisson(0.4 * 15)
        st, sx, sy, sm = [], [], [], []
        for _ in range(ns):
            t0 = -5 * YIL + rng.random() * (15 * YIL - 180)
            if rng.random() < 0.6:
                cx, cy = G.fay_noktasi(rng, F[rng.integers(len(F))], 1)
                cx, cy = cx[0], cy[0]
            else:
                rr, th = R * math.sqrt(rng.random()), rng.random() * 2 * math.pi
                cx, cy = rr * math.cos(th), rr * math.sin(th)
            st.append(t0 + rng.random(15) * 180)
            sx.append(cx + rng.normal(0, 3, 15))
            sy.append(cy + rng.normal(0, 3, 15))
            u = rng.random(15)
            sm.append(2.5 - np.log(1 - u * (1 - 10 ** -0.7)) / math.log(10))
        if ns:
            t, x, y, m = (np.concatenate([a] + b) for a, b in ((t, st), (x, sx), (y, sy), (m, sm)))
            o = np.argsort(t)
            t, x, y, m = t[o], x[o], y[o], m[o]
    keep = np.ones(len(t), bool)
    if sen == "D4":
        ic = (x > 0.375 * R) & (t >= 7 * YIL) & (m < 3.0)
        keep[ic] = rng.random(int(ic.sum())) < 0.3
    t, x, y, m = t[keep], x[keep], y[keep], m[keep]
    bg = G.gk74_xy(t, x, y, m)
    g, ic = G.izgara(R)
    ze, n = G.z_olcu(rng, x[bg], y[bg], t[bg], R, 7 * YIL, 10 * YIL, 0.0, 0.5, g, ic, 100)
    zp, _ = G.z_olcu(rng, x[bg], y[bg], t[bg], R, 4 * YIL, 7 * YIL, 0.0, 0.5, g, ic, 100)
    return ze, zp, n


def _kal(arg):
    """(tohum, R, N, dal, deneme) -> (Nh kendi R'de, ns_R ort., ns_80 ort.)"""
    tohum, R, N, dal, den = arg
    rng = np.random.default_rng(tohum)
    M.dallanma(dal)
    nsR = [bolge(rng, N, "D0", 0.0, R)[2] for _ in range(den)]
    ns80 = [bolge(rng, N, "D0", 0.0, 80.0)[2] for _ in range(den)] if dal == 0.6 else [np.nan]
    return N * N / max(float(np.mean(nsR)), 1.0), float(np.mean(nsR)), float(np.mean(ns80))


def _hv(arg):
    tohum, R, Nh, dal, sen, f, n = arg
    rng = np.random.default_rng(tohum)
    M.dallanma(dal)
    a = np.array([bolge(rng, Nh, sen, f, R) for _ in range(n)], float)
    return a[np.isfinite(a[:, 0]) & np.isfinite(a[:, 1])]


def main(cikti):
    t0 = time.time()
    rng = np.random.default_rng(TOHUM)
    L, dusen = V.liste(os.path.join(BURA, "..", "..", "tr13", "tr13_tamsayim.json"))
    kids = sorted({r["kume"] for r in L})
    kum = [[i for i, r in enumerate(L) if r["kume"] == k] for k in kids]
    kd = [j for j, k in enumerate(kids) if k not in KESIF]
    print("üye", len(L), "küme", len(kum), "keşif dışı", len(kd), flush=True)
    den, n0, nd, nf = (8, 40, 30, 20) if HIZLI else (40, 400, 250, 150)
    nb = 4000 if HIZLI else 20000
    pool = mp.Pool(4)
    # ---- K: kalibrasyon (kendi R'de), sıfır dallanmaları + veri için ayrı 0,6
    kj, kk = [], []
    for i, r in enumerate(L):
        for di, d in enumerate(DAL):
            kj.append((TOHUM + 1000 * i + di, r["R"], r["N_son"], d, den)); kk.append((i, d))
        kj.append((TOHUM + 1000 * i + 9, r["R"], r["N_son"], 0.6, den)); kk.append((i, "veri"))
    ks = pool.map(_kal, kj, chunksize=1)
    NH = {k: v[0] for k, v in zip(kk, ks)}
    kal = [dict(yer=L[i]["yer"], R=L[i]["R"], N_son=L[i]["N_son"],
                ns_kendiR=round(ks[kk.index((i, 0.6))][1], 1), ns_R80kal=round(ks[kk.index((i, 0.6))][2], 1),
                oran_R80_kendiR=round(ks[kk.index((i, 0.6))][2] / ks[kk.index((i, 0.6))][1], 3))
           for i in range(len(L))]
    print("kalibrasyon", round(time.time() - t0), "s", json.dumps(kal, ensure_ascii=False), flush=True)
    # ---- havuzlar
    jobs, key = [], []
    for i, r in enumerate(L):
        for di, d in enumerate(DAL):
            for p in range(2):
                jobs.append((TOHUM + 1000 * i + 100 + 10 * di + p, r["R"], NH[(i, d)], d, "D0", 0.0, n0 // 2))
                key.append((i, "s", d))
        for si, sen in enumerate(("D0", "D1", "D4")):
            for p in range(2):
                jobs.append((TOHUM + 1000 * i + 200 + 10 * si + p, r["R"], NH[(i, "veri")], 0.6, sen, 0.0, nd // 2))
                key.append((i, sen, 0))
        for fi, f in enumerate(F_LIST):
            jobs.append((TOHUM + 1000 * i + 300 + fi, r["R"], NH[(i, "veri")], 0.6, "D0", f, nf))
            key.append((i, "f", f))
    # büyük R'li işleri öne al (yük dengesi)
    order = sorted(range(len(jobs)), key=lambda j: -jobs[j][1])
    res = pool.map(_hv, [jobs[j] for j in order], chunksize=1)
    pool.close()
    P = {}
    for j, a in zip(order, res):
        P.setdefault(key[j], []).append(a)
    P = {k: np.concatenate(v) for k, v in P.items()}
    print("havuzlar", round(time.time() - t0), "s", flush=True)

    def kume_cek(r, havuz, nbb):
        """Küme yapılı çekiliş: (nbb, küme sayısı) ze, zp."""
        ze = np.zeros((nbb, len(kum))); zp = np.zeros((nbb, len(kum)))
        for j, uy in enumerate(kum):
            for u in uy:
                h = havuz[u]
                ix = r.integers(0, len(h), nbb)
                ze[:, j] += h[ix, 0]; zp[:, j] += h[ix, 1]
            ze[:, j] /= len(uy); zp[:, j] /= len(uy)
        return ze, zp

    def ist(ze, zp):
        return dict(a=ze.mean(1), k=ze[:, kd].mean(1), p=zp.mean(1),
                    da=(ze - zp).mean(1), dk=(ze - zp)[:, kd].mean(1))

    NS = 200000
    S = {d: ist(*kume_cek(np.random.default_rng(TOHUM + 7 + int(10 * d)), {i: P[(i, "s", d)] for i in range(len(L))},
                          NS)) for d in DAL}

    def esik(q):
        return {d: {s: float(np.quantile(S[d][s], q)) for s in ("a", "k", "da", "dk")} for d in DAL}

    E05 = esik(0.05)
    EP = {q: float(np.quantile(S[0.6]["p"], q)) for q in (0.05, 0.20)}

    veri = {"D0": "D0", "D1": "D1", "D4": "D4"}
    T = {}
    rr = np.random.default_rng(TOHUM + 99)
    for ad in list(veri) + [f"f{f}" for f in F_LIST]:
        if ad.startswith("f"):
            hv = {i: P[(i, "f", float(ad[1:]))] for i in range(len(L))}
        else:
            hv = {i: P[(i, ad, 0)] for i in range(len(L))}
        T[ad] = ist(*kume_cek(rr, hv, nb))

    def r0(t, E):
        return np.all([(t["a"] < E[d]["a"]) & (t["k"] < E[d]["k"]) for d in DAL], axis=0)

    def r4(t, E):
        return np.all([(t["da"] < E[d]["da"]) & (t["dk"] < E[d]["dk"]) for d in DAL], axis=0)

    fs = [0.0] + list(F_LIST)
    sat = ["D0", "D1", "D4"] + [f"f{f}" for f in F_LIST]
    kur = {}
    for ad, fn in (("T1_06_ana", lambda t: t["a"] < E05[0.6]["a"]),
                   ("R0", lambda t: r0(t, E05)),
                   ("R1_plasebo_q20", lambda t: r0(t, E05) & (t["p"] > EP[0.20])),
                   ("R1b_plasebo_q05", lambda t: r0(t, E05) & (t["p"] > EP[0.05])),
                   ("R4_fark", lambda t: r4(t, E05))):
        kur[ad] = {s: float(fn(T[s]).mean()) for s in sat}
    # R3: en kötü bozulmaya göre ortak nicel
    a_sec = None
    for a in np.arange(0.050, 0.0, -0.0025):
        E = esik(a)
        if max(float(r0(T["D1"], E).mean()), float(r0(T["D4"], E).mean())) <= 0.05:
            a_sec = float(a)
            break
    E3 = esik(a_sec)
    kur["R3_enkotu_kalibre"] = {s: float(r0(T[s], E3).mean()) for s in sat}
    kur["R3_enkotu_kalibre"]["a"] = a_sec
    mde = {}
    for ad, v in kur.items():
        gs = [v["D0"]] + [v[f"f{f}"] for f in F_LIST]
        mde[ad] = M.mde(fs, gs)
    # plasebo seçiciliği: R0 reddi içinde plasebonun düşürdüğü pay, ve ortalama kaymalar
    sec = {}
    for s in sat:
        m0 = r0(T[s], E05)
        sec[s] = dict(R0=float(m0.mean()),
                      plasebo_q20_duser_R0_icinde=float((T[s]["p"][m0] <= EP[0.20]).mean()) if m0.any() else None,
                      plasebo_q05_duser_R0_icinde=float((T[s]["p"][m0] <= EP[0.05]).mean()) if m0.any() else None,
                      plasebo_q20_red_kosulsuz=float((T[s]["p"] <= EP[0.20]).mean()))
    kay = {}
    for s in ("D1", "D4", "f0.4"):
        kay[s] = {}
        for sutun, c in (("z", 0), ("z_p", 1)):
            k0 = np.mean([P[(i, "D0", 0)][:, c].mean() for i in range(len(L))])
            k1 = np.mean([P[(i, s, 0) if not s.startswith("f") else (i, "f", 0.4)][:, c].mean()
                          for i in range(len(L))])
            kay[s][sutun] = round(float(k1 - k0), 3)
    out = dict(tohum=TOHUM, hizli=HIZLI, den=den, n0=n0, nd=nd, nf=nf, nb=nb, K_ana=len(kum), K_kesifsiz=len(kd),
               kalibrasyon=kal, esik05=E05, esik_plasebo=EP, kurallar=kur, MDE=mde, plasebo_seciciligi=sec,
               ortalama_kayma_D0a_gore=kay,
               havuz_boyu={f"{k[0]}_{k[1]}_{k[2]}": int(len(v)) for k, v in P.items() if k[0] == 0},
               sure_s=round(time.time() - t0))
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(dict(kurallar=kur, MDE=mde, secicilik=sec, kayma=kay), indent=1, ensure_ascii=False))
    print("bitti", out["sure_s"], "s")


if __name__ == "__main__":
    HIZLI = len(sys.argv) > 2 and sys.argv[2] == "hizli"
    main(sys.argv[1])
