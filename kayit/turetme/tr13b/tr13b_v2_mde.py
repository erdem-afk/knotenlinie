#!/usr/bin/env python3
"""TR-13b sürüm 2: listenin gerçek (R, N3bg) bileşimiyle yapay MDE ve ETAS uyumsuzluk denetimi. YALNIZ YAPAY VERİ.

Gerçek katalogda hiçbir ölçü hesaplanmaz. Tek gerçek girdi kayit/turetme/tr13/tr13_tamsayim.json'daki üstveri
satırlarıdır (olay, küme, R, Mc_önce, Mc_ref, N3bg sayısı). Üreteç, GK74 ve z ölçüsü tr13_guc.py'den (tr13b_mde.bolge).

Bölüm A (bileşim MDE'si):
  ana liste: M >= 6,5, ref_gecer[0,3]; ortak Mc_b = max(Mc_önce, Mc_ref); N' = N3bg x 10^-(Mc_b - Mc_önce) (b = 1
  varsayımı); N' < 50 -> üye düşer; N' > 100 -> Mc 0,1 adımlarla yükseltilir (N' x 10^-0,1k <= 100).
  Her üye kendi R'si ve N''siyle benzetilir. Küme z = üyelerin z ortalaması; sıfırda her üye kendi havuzundan.
  Sıfır havuzları dallanma 0,4 / 0,6 / 0,8; sinyal ve "veri sıfırı" dallanma 0,6.
  Hüküm kuralı ("VAR"): T1 p <= 0,05 üç dallanmanın üçünde de, hem bütün listede (K_ana) hem keşif kümeleri
  (397, 979, 395) dışarıda; ve plasebo T1'i (z_p, dallanma 0,6 sıfırı) p > 0,20.
Bölüm B (Z5 denetimi, R = 80, N3bg 100, K = 14 türdeş): veri D0 / D1 (durağan sürüler) / D4 (kenar ağ kaybı);
  T1 tek başına ve plasebo denetimiyle yanlış "VAR" oranı; D0'da f = 0,3'te denetimin güç bedeli.
  Sürü ve ağ senaryoları INCELEME-1 (tr13b_inc1.py) ile aynı tanımlıdır.
Sürüm 3 notu (D-2): `_is_A` artık kendi R'de kalibre eder (kalibre_R, 40 deneme). tr13b_v2_mde.json bu düzeltmeden
ÖNCE üretildi (R = 80 kalibrasyonu) ve tarihçe olarak kalır; güncel sayılar INCELEME-2 (inc2/) ve koşu öncesi D-3'tür.
Kullanım: python3 -I -B tr13b_v2_mde.py <cikti.json> [hizli]
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
sys.path.insert(0, BURA)
sys.path.insert(0, os.path.join(BURA, "..", "tr13"))
import tr13_guc as G  # noqa: E402
import tr13b_mde as M  # noqa: E402

TOHUM = 20261121
YIL = G.YIL
KESIF = {397, 979, 395}
DALLANMA = (0.4, 0.6, 0.8)
F_LIST = (0.15, 0.2, 0.25, 0.3, 0.4, 0.5)
HIZLI = False


def liste(yol):
    d = json.load(open(yol))
    out, dusen = [], []
    for s in d["satir"]:
        if s["M"] < 6.5 or not s["ref_gecer"]["0.3"]:
            continue
        mc0, mcr = s["mc_once"], s["ref_tam"]["mc"]
        mcb = max(mc0, mcr)
        N = s["N3bg_mc"] * 10 ** (-(mcb - mc0))
        k = 0
        while N * 10 ** (-0.1 * k) > 100:
            k += 1
        Nf = N * 10 ** (-0.1 * k)
        r = dict(id=s["id"], yer=s["yer"][:40], kume=s["kume"], R=s["R_km"], N3bg=s["N3bg_mc"], mc_once=mc0,
                 mc_ref=mcr, N_ortak=round(N, 1), mc_artis=round(mcb - mc0 + 0.1 * k, 1), N_son=round(Nf, 1))
        (out if N >= 50 else dusen).append(r)
    return out, dusen


# ---------------------------------------------------------------- bölüm B bölgesi (z_olay, z_plasebo)
def bolge_B(rng, Nh, sen, f=0.0, R=80.0):
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
        ic = (x > 30) & (t >= 7 * YIL) & (m < 3.0)
        keep[ic] = rng.random(int(ic.sum())) < 0.3
    t, x, y, m = t[keep], x[keep], y[keep], m[keep]
    bg = G.gk74_xy(t, x, y, m)
    g, ic = G.izgara(R)
    ze, n = G.z_olcu(rng, x[bg], y[bg], t[bg], R, 7 * YIL, 10 * YIL, 0.0, 0.5, g, ic, 100)
    zp, _ = G.z_olcu(rng, x[bg], y[bg], t[bg], R, 4 * YIL, 7 * YIL, 0.0, 0.5, g, ic, 100)
    return ze, zp, n


# ---------------------------------------------------------------- işçiler
def kalibre_R(rng, N, R, deneme):
    """INCELEME-2 K1 / D-2 düzeltmesi: μ üyenin KENDİ R'sinde kalibre edilir (M.kalibre R'yi geçirmiyordu, R = 80)."""
    ns = [M.bolge(rng, N, 0.0, R=R, B_ref=2)[2] for _ in range(deneme)]
    return N * N / max(float(np.mean(ns)), 1.0)


def _is_A(arg):
    tohum, R, N, dal, f, n = arg
    rng = np.random.default_rng(tohum)
    M.dallanma(dal)
    Nh = kalibre_R(rng, N, R, deneme=15 if HIZLI else 40)
    a = [M.bolge(rng, Nh, f, R=R) for _ in range(n)]
    a = np.array([r[:3] for r in a], float)
    return a[np.isfinite(a[:, 0]) & np.isfinite(a[:, 1])]


def _is_B(arg):
    tohum, sen, f, n = arg
    rng = np.random.default_rng(tohum)
    M.dallanma(0.6)
    ns = [bolge_B(rng, 100, "D0")[2] for _ in range(15 if HIZLI else 30)]
    Nh = 100 * 100 / max(float(np.mean(ns)), 1.0)
    a = np.array([bolge_B(rng, Nh, sen, f) for _ in range(n)], float)
    return a[np.isfinite(a[:, 0]) & np.isfinite(a[:, 1])]


def parcali(havuz, fn, isler, parca):
    """Her işi parca parçaya böl (paralellik için), sonra birleştir."""
    gen = []
    for j, a in enumerate(isler):
        n = a[-1]
        for p in range(parca):
            gen.append((j, a[:-1], n // parca + (1 if p < n % parca else 0), p))
    sonuc = havuz.map(fn, [(a[0] * 1000 + p,) + tuple(a[1:]) + (n,) for j, a, n, p in gen], chunksize=1)
    out = [[] for _ in isler]
    for (j, _, _, _), r in zip(gen, sonuc):
        out[j].append(r)
    return [np.concatenate(o) for o in out]


def kume_ort(rng, pools, kumeler, nb, sutun=0):
    """pools: üye -> dizi; kumeler: [[üye,...],...]. Dönüş: (nb,) küme ortalamalarının ortalaması."""
    tot = np.zeros(nb)
    for uy in kumeler:
        s = np.zeros(nb)
        for u in uy:
            p = pools[u][:, sutun]
            s += p[rng.integers(0, len(p), nb)]
        tot += s / len(uy)
    return tot / len(kumeler)


def main(cikti):
    t0 = time.time()
    rng = np.random.default_rng(TOHUM)
    L, dusen = liste(os.path.join(BURA, "..", "tr13", "tr13_tamsayim.json"))
    kume_ids = sorted({r["kume"] for r in L})
    kumeler = [[i for i, r in enumerate(L) if r["kume"] == k] for k in kume_ids]
    kumeler_k = [[i for i, r in enumerate(L) if r["kume"] == k] for k in kume_ids if k not in KESIF]
    print("liste", len(L), "üye,", len(kumeler), "küme; keşif dışı", len(kumeler_k), "; düşen",
          [d["yer"] for d in dusen], flush=True)
    n0, nv, nf = (60, 40, 40) if HIZLI else (400, 300, 150)
    nb = 4000 if HIZLI else 20000
    havuz = mp.Pool(4)
    # ---- A: sıfır havuzları (3 dallanma), veri sıfırı (0,6, bağımsız), sinyal havuzları (0,6)
    isler, anahtar = [], []
    for i, r in enumerate(L):
        for di, d in enumerate(DALLANMA):
            isler.append((TOHUM + 100 * i + di, r["R"], r["N_son"], d, 0.0, n0)); anahtar.append((i, "s", d))
        isler.append((TOHUM + 100 * i + 10, r["R"], r["N_son"], 0.6, 0.0, nv)); anahtar.append((i, "v", 0))
        for fi, f in enumerate(F_LIST):
            isler.append((TOHUM + 100 * i + 20 + fi, r["R"], r["N_son"], 0.6, f, nf)); anahtar.append((i, "f", f))
    sonuc = parcali(havuz, _is_A, isler, 2)
    P = {k: v for k, v in zip(anahtar, sonuc)}
    print("A havuzları", round(time.time() - t0), "s", flush=True)

    def pools(tur, d):
        return {i: P[(i, tur, d)] for i in range(len(L))}

    # eşikler (alt kuyruk): her dallanma, K_ana ve keşif dışı; plasebo %20 (dallanma 0,6, sütun 1)
    esik = {}
    for d in DALLANMA:
        esik[("ana", d)] = float(np.quantile(kume_ort(rng, pools("s", d), kumeler, 200000), 0.05))
        esik[("kesifsiz", d)] = float(np.quantile(kume_ort(rng, pools("s", d), kumeler_k, 200000), 0.05))
    esik_p20 = float(np.quantile(kume_ort(rng, pools("s", 0.6), kumeler, 200000, sutun=1), 0.20))

    def karar(veri):
        """veri: üye -> havuz. Dönüş: bileşen başına red oranları."""
        r = np.random.default_rng(rng.integers(1 << 32))
        tot_k = np.zeros(nb); tot_a = np.zeros(nb); tot_p = np.zeros(nb)
        for k_i, uy in zip(kume_ids, kumeler):
            se, sp = np.zeros(nb), np.zeros(nb)
            for u in uy:
                idx = r.integers(0, len(veri[u]), nb)
                se += veri[u][idx, 0]; sp += veri[u][idx, 1]
            tot_a += se / len(uy); tot_p += sp / len(uy)
            if k_i not in KESIF:
                tot_k += se / len(uy)
        za, zk, zp = tot_a / len(kumeler), tot_k / len(kumeler_k), tot_p / len(kumeler)
        r06 = za < esik[("ana", 0.6)]
        r3a = np.all([za < esik[("ana", d)] for d in DALLANMA], axis=0)
        r3k = np.all([zk < esik[("kesifsiz", d)] for d in DALLANMA], axis=0)
        rp = zp > esik_p20
        return dict(T1_06_ana=float(r06.mean()), T1_uc_ana=float(r3a.mean()), T1_uc_kesifsiz=float(r3k.mean()),
                    uc_ana_ve_kesifsiz=float((r3a & r3k).mean()), tam_kural=float((r3a & r3k & rp).mean()))

    A = dict(liste=L, dusen=dusen, K_ana=len(kumeler), K_kesifsiz=len(kumeler_k),
             esik={f"{a}_{d}": v for (a, d), v in esik.items()}, esik_plasebo_q20=esik_p20,
             yanlis_alarm_veri_sifiri=karar(pools("v", 0)), guc={}, MDE={})
    for f in F_LIST:
        A["guc"][str(f)] = karar(pools("f", f))
        print("f", f, A["guc"][str(f)], flush=True)
    fs = [0.0] + list(F_LIST)
    for k in A["yanlis_alarm_veri_sifiri"]:
        gs = [A["yanlis_alarm_veri_sifiri"][k]] + [A["guc"][str(f)][k] for f in F_LIST]
        A["MDE"][k] = M.mde(fs, gs)
    # ×0,5 / ×2 tam kural için: güç doğrudan (yarısı ve iki katı, en yakın f'ye ara değer)
    print("A", json.dumps({k: v for k, v in A.items() if k in ("K_ana", "K_kesifsiz", "MDE",
                                                                  "yanlis_alarm_veri_sifiri")}), flush=True)

    # ---- B: Z5 denetimi
    isB = [(TOHUM + 9000, "D0", 0.0, 1500), (TOHUM + 9001, "D0", 0.0, 600), (TOHUM + 9002, "D1", 0.0, 600),
           (TOHUM + 9003, "D4", 0.0, 600), (TOHUM + 9004, "D0", 0.3, 600), (TOHUM + 9005, "D0", 0.2, 600)]
    if HIZLI:
        isB = [(a, b, c, n // 10) for a, b, c, n in isB]
    cal, d0, d1, d4, s3, s2 = parcali(havuz, _is_B, isB, 4)
    K = 14
    e1 = float(np.quantile(cal[rng.integers(0, len(cal), (200000, K)), 0].mean(1), 0.05))
    ep = float(np.quantile(cal[rng.integers(0, len(cal), (200000, K)), 1].mean(1), 0.20))
    B = dict(K=K, N3bg=100, R=80, esik_T1=e1, esik_plasebo_q20=ep)
    for ad, v in (("D0", d0), ("D1_suru", d1), ("D4_kenar", d4), ("D0_f0.2", s2), ("D0_f0.3", s3)):
        i = rng.integers(0, len(v), (40000, K))
        ze, zp = v[i, 0].mean(1), v[i, 1].mean(1)
        B[ad] = dict(T1=float((ze < e1).mean()), T1_ve_plasebo=float(((ze < e1) & (zp > ep)).mean()),
                     plasebo_red=float((zp <= ep).mean()), n=int(len(v)))
        print("B", ad, B[ad], flush=True)
    havuz.close()
    out = dict(tohum=TOHUM, hizli=HIZLI, n0=n0, nv=nv, nf=nf, nb=nb, A=A, B=B, sure_s=round(time.time() - t0))
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)
    print("bitti", out["sure_s"], "s")


if __name__ == "__main__":
    HIZLI = len(sys.argv) > 2 and sys.argv[2] == "hizli"
    main(sys.argv[1])
