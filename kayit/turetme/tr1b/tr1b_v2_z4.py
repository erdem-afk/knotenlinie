#!/usr/bin/env python3
"""TR-1b sürüm 2, Z4: eşli sınamanın (olay penceresi / 730 g geriye kaydırılmış yerinde plasebo, log oran, kesin
işaret çevirme) yapay yanlış alarmı ve MDE'si. YALNIZ YAPAY VERİ; hiçbir tenv3 okunmaz.

Seri: 2556 günlük tam ızgara (önünde 2000 günlük ısınma; kırpışma süreci pencereden önce başlamış) (plasebo w0_p .. olay w1), iki yatay bileşen, beyaz + kırpışma (Williams kesirli fark,
TR-11 tr11_kosu.h_katsayi ile aynı süzgeç) [+ rastgele yürüyüş]. Olay penceresi gün [730, 2556), plasebo [0, 1826):
iki pencere [730, 1826) parçasını (1096 g) PAYLAŞIR ve kırpışma uzun bellekli olduğu için bağımlıdır (Z4'ün konusu).
İstasyon ölçüsü: TR-11 tasarımı (tr11_kosu.tasarim: sabit, eğim, yıllık/altı aylık, menteşe) ile en küçük kareler
menteşe katsayısı; MAD ayıklaması ve kod 1 sıçraması yok (Gauss gürültüde etkisiz sayıldı). Küme ölçüsü
tr11_kosu.S_hesapla. n_y TR-11 katman sayılarına göre 3–8, n_r = 8. Küme başına ölçek exp(0,4 Z) iki pencerede ortak.
Senaryolar (sinyalsiz): N0 (beyaz 1,5 mm, kırpışma 4,6 mm/yıl^0,25 = TR-11 b_f*), N0düşük (kırpışma 3,0),
N1 (N0 + RW 1 mm/yıl^0,5), BOLGE2 (N0, bütün gürültü × 2, iki pencerede), ARTAN (N0, son 730 g'de gürültü × 1,5:
olaydan bağımsız ama T'ye doğru artan gürültü; karıştırıcı gösterimi, Z4 eşiğine girmez).
Sinyal: yakın istasyonlara doğuda g × max(0, t − H) (olay penceresinin son 730 g'ü), uyumlu ya da dağınık (g × U(0,1)).
Hüküm kuralı: eşli p <= 0,05 ve her "bir kümeyi dışarıda bırak" p <= 0,10.
Kullanım: python3 -I -B tr1b_v2_z4.py <cikti.json> [hizli]
"""
import itertools
import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tr11"))
import tr11_kosu as T  # noqa: E402

TOHUM = 20261122
NT = 2556
NW = T.N_PEN            # 1826
BURN = 2000                                     # kırpışma ve RW için ısınma (süreç pencereden önce başlamış)
NTOP = NT + BURN
NFFT = 16384
DT = T.DT
SW = 1.5
KAT = [((3, 4), 213), ((5, 7), 253), ((8, 8), 199)]
NR = 8
NMAX = NR + 8
HF = np.fft.rfft(T.h_katsayi(-1.0, NTOP), NFFT)
HR = np.fft.rfft(T.h_katsayi(-2.0, NTOP), NFFT)
X = T.tasarim(np.arange(NW), 0, NW - T.N_YAK, [])
A = np.linalg.pinv(X)[-1]                       # menteşe katsayısı = A @ y
RAMP = np.maximum(0.0, (np.arange(NT) - (730 + NW - T.N_YAK)) / T.Y)   # olay penceresi menteşesinden sonra


def suz(z, FH):
    return np.fft.irfft(np.fft.rfft(z, NFFT, axis=-1) * FH, NFFT, axis=-1)[..., BURN:NTOP]


def ny_cek(rng, n):
    w = np.array([c for _, c in KAT], float)
    k = rng.choice(3, n, p=w / w.sum())
    lo = np.array([KAT[i][0][0] for i in k]); hi = np.array([KAT[i][0][1] for i in k])
    return lo + (rng.random(n) * (hi - lo + 1)).astype(int)


def kumeler(rng, n, sen="N0", g=0.0, dagin=False, parti=60):
    """Dönüş: d = log(S_olay / S_plasebo), (n,)."""
    out = []
    for b0 in range(0, n, parti):
        m = min(parti, n - b0)
        bf = 3.0 if sen == "N0dusuk" else 4.6
        y = SW * rng.standard_normal((m, NMAX, 2, NT)) + bf * DT ** 0.25 * suz(rng.standard_normal((m, NMAX, 2, NTOP)), HF)
        if sen == "N1":
            y = y + 1.0 * DT ** 0.5 * suz(rng.standard_normal((m, NMAX, 2, NTOP)), HR)
        olc = np.exp(0.4 * rng.standard_normal(m))[:, None, None, None]
        if sen == "BOLGE2":
            olc = olc * 2.0
        y = y * olc
        if sen == "ARTAN":
            y[..., NT - T.N_YAK:] *= 1.5
        ny = ny_cek(rng, m)
        if g:
            a = rng.random((m, 8)) if dagin else np.ones((m, 8))
            y[:, NR:, 0, :] += g * a[:, :, None] * RAMP
        dv_e = y[..., 730:] @ A                       # (m, NMAX, 2)
        dv_p = y[..., :NW] @ A
        S = []
        for dv in (dv_e, dv_p):
            r = dv[:, :NR]
            s = np.empty(m)
            for k in range(3, 9):
                sec = ny == k
                if sec.any():
                    s[sec] = T.S_hesapla(dv[sec, NR:NR + k], r[sec])
            S.append(s)
        out.append(np.log(S[0] / S[1]))
    return np.concatenate(out)


ISARET = {}


def isaret(K):
    if K not in ISARET:
        ISARET[K] = np.array(list(itertools.product([-1.0, 1.0], repeat=K)))
    return ISARET[K]


def p_deg(d):
    """d: (nb, K). Tek yanlı kesin işaret çevirme p'si (büyük d = olay penceresi büyük)."""
    I = isaret(d.shape[1])
    Tt = d @ I.T
    return (Tt >= d.sum(1, keepdims=True) - 1e-12).mean(1)


def karar(rng, havuz, K, nb):
    d = havuz[rng.integers(0, len(havuz), (nb, K))]
    p = p_deg(d)
    loo = np.ones(nb, bool)
    for j in range(K):
        loo &= p_deg(np.delete(d, j, axis=1)) <= 0.10
    return float((p <= 0.05).mean()), float(((p <= 0.05) & loo).mean())


def main(cikti, hizli=False):
    t0 = time.time()
    rng = np.random.default_rng(TOHUM)
    n0, ns, nb = (600, 300, 1000) if hizli else (6000, 2000, 4000)
    KL = [6, 8, 10, 12]
    out = dict(tohum=TOHUM, n0=n0, ns=ns, nb=nb, K=KL, yanlis_alarm={}, guc={}, MDE={})
    sif = {}
    for sen in ("N0", "N0dusuk", "N1", "BOLGE2", "ARTAN"):
        h = kumeler(rng, n0, sen)
        sif[sen] = h
        out["yanlis_alarm"][sen] = {str(K): dict(zip(("p", "p_ve_LOO"), karar(rng, h, K, nb))) for K in KL}
        out["yanlis_alarm"][sen]["d_ort"] = float(h.mean())
        out["yanlis_alarm"][sen]["d_sd"] = float(h.std(ddof=1))
        out["yanlis_alarm"][sen]["d_carpiklik"] = float(((h - h.mean()) ** 3).mean() / h.std() ** 3)
        print(sen, out["yanlis_alarm"][sen], round(time.time() - t0), "s", flush=True)
    gl = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
    for dagin in (False, True):
        kip = "daginik" if dagin else "uyumlu"
        hv = {g: kumeler(rng, ns, "N0", g, dagin) for g in gl}
        out["guc"][kip] = {}
        for K in KL:
            gs = [karar(rng, hv[g], K, nb)[1] for g in gl]
            g0 = out["yanlis_alarm"]["N0"][str(K)]["p_ve_LOO"]
            out["guc"][kip][str(K)] = dict(zip(map(str, gl), [round(v, 3) for v in gs]))
            ga, ka = [0.0] + gl, [g0] + gs
            mde = None
            for i in range(1, len(ga)):
                if ka[i] >= 0.8:
                    mde = round(ga[i - 1] + (0.8 - ka[i - 1]) * (ga[i] - ga[i - 1]) / max(ka[i] - ka[i - 1], 1e-9), 2)
                    break
            out["MDE"][f"{kip}_K{K}"] = mde
            print(kip, K, mde, out["guc"][kip][str(K)], round(time.time() - t0), "s", flush=True)
    # ×0,5 / ×2 (K_p = 8): güç doğrudan
    duy = {}
    for kip, dagin in (("uyumlu", False), ("daginik", True)):
        m = out["MDE"][f"{kip}_K8"]
        if m is None:
            continue
        r = dict(MDE=m)
        for ad, g in (("yari", m / 2), ("iki_kat", 2 * m)):
            hv = kumeler(rng, ns, "N0", g, dagin)
            r[ad] = dict(g=round(g, 2), guc_K8=round(karar(rng, hv, 8, nb)[1], 3),
                         guc_K12=round(karar(rng, hv, 12, nb)[1], 3))
        duy[kip] = r
        print("duy", kip, r, flush=True)
    out["duyarlilik_K8"] = duy
    out["sure_s"] = round(time.time() - t0)
    json.dump(out, open(cikti, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(sys.argv[1], len(sys.argv) > 2 and sys.argv[2] == "hizli")
