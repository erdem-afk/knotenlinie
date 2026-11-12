#!/usr/bin/env python3
"""TR-5b İNCELEME-2: E3'ün (pozitif kontrol geçme olasılığı) bağımsız, küçük örnekli yeniden yazımı ve uzaklık
senaryoları. Gerçek veri yok. `tr5b_yapay*.py` içe aktarılmaz; model ön kayıt §6.1 metninden yeniden yazıldı.

Model (ön kayıt §6.1 E3, §3.4, §4.2 adım 8): 20 sn^-1, τ ∈ [-60, 60] sn; 0,5-2 Hz bant sınırlı Green fonksiyonu ×
exp(-|τ|/20), koda RMS'i 1; günlük ÇİF = G(τ(1+ε_d)) + gürültü/snr (snr = 0,577/√10, CC10 ≈ 0,5; 0,98/√10, CC10 ≈ 0,7);
günlerin %15'i eksik + bir 30 günlük boşluk; ε_d = mevsim·sin(2πd/365,25 + φ) − A_k(1 − 0,5 ln(1+t)/ln 51) (t >= 1),
A_k = A·U(0,5; 1,5). Başvuru [T-1095, T-8] geçerli günlerinin ortalaması (bütün günler AYRI üretilir; kısaltma yok).
Yığın [d-9, d] (>= 5 geçerli gün). Germe ±%2, adım %0,001, TAM ızgara, parabol; geçerli CC >= 0,40 ve kenar değil.
δ_ko = ort ε(yığın sonu T+10..T+30) − ort ε(T-60..T-8); öncesi >= 10, sonrası >= 5 geçerli. Wilcoxon tek yanlı kesin
(kendi yazımı), p <= 0,05, geçerli küme >= 8.

Senaryolar (havuz başına N_IST istasyon, 2000 çekiliş):
  E3 tablosu satırları: A = 0 ve %0,08 (Napa ölçeği), üç gürültü koşulu.
  PK_uzaklik: 15 PK kümesinin en yakın geçerli istasyonu > 50 km olan 3'ü (NZ.KNZ 53 km M6,6; HT.LKD2 67 km M6,1;
     AK.CHN 69 km) A = 0, kalan 12'si A = %0,08 (Boschelli 2021: 50 km ötesinde düşüş yok).
  P2_uzaklik: 20 P2 olayından > 90 km olan 4'ü (IU.HNR 337, PS.PSI 213, NZ.MXZ 102, CN.LGNH 93 km) A = 0, 16'sı
     A = %0,08; kötümser: > 50 km olan 6'sı (C.ROC1 51, GE.MALT 57 de) A = 0.
Kullanım: python3 -I -B inc2_e3_bagimsiz.py [N_IST]   (varsayılan 300; 4 süreç; ≈ 10 dk)
"""
import json, math, os, sys, time
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
FS = 20.0
TAU = np.arange(-1200, 1201) / FS
KODA = (np.abs(TAU) >= 10) & (np.abs(TAU) <= 40)
NF = 4096
FRQ = np.fft.rfftfreq(NF, 1 / FS)
W = np.clip(np.minimum((FRQ - 0.4) / 0.1, (2.1 - FRQ) / 0.1), 0, 1)
W = np.where((FRQ >= 0.5) & (FRQ <= 2.0), 1.0, np.sin(0.5 * np.pi * W) ** 2)
GRID = np.round(np.arange(-2000, 2001) * 1e-5, 8)
GUN = np.arange(-1095, 31)


def bg(rng, n):
    z = np.fft.irfft(np.fft.rfft(rng.standard_normal((n, NF)), axis=1) * W, NF, axis=1)[:, :TAU.size]
    return z / z.std(1, keepdims=True)


def istasyon(rng, snr, A, mev):
    G = bg(rng, 1)[0] * np.exp(-np.abs(TAU) / 20); G /= np.sqrt((G[KODA] ** 2).mean())
    eps = mev * np.sin(2 * np.pi * GUN / 365.25 + rng.uniform(0, 2 * np.pi))
    t = GUN[GUN >= 1].astype(float)
    eps[GUN >= 1] -= A * rng.uniform(0.5, 1.5) * (1 - 0.5 * np.log1p(t) / np.log(51))
    ccf = np.empty((GUN.size, TAU.size))
    for i, e in enumerate(eps): ccf[i] = np.interp(TAU * (1 + e), TAU, G, left=0, right=0)
    ccf += bg(rng, GUN.size) / snr
    ok = rng.random(GUN.size) > 0.15
    b = rng.integers(0, GUN.size - 30); ok[b:b + 30] = False
    ref = ccf[(GUN <= -8) & ok].mean(0)
    Rk = np.stack([np.interp(TAU[KODA] * (1 + g), TAU, ref) for g in GRID])
    Rk -= Rk.mean(1, keepdims=True); Rk /= np.linalg.norm(Rk, axis=1, keepdims=True)
    son = [d for d in range(-60, -7)] + [d for d in range(10, 31)]
    Y, et = [], []
    for d in son:
        m = (GUN >= d - 9) & (GUN <= d) & ok
        if m.sum() >= 5: Y.append(ccf[m].mean(0)[KODA]); et.append(d)
    if not Y: return float('nan')
    Y = np.array(Y); Y -= Y.mean(1, keepdims=True); Y /= np.linalg.norm(Y, axis=1, keepdims=True)
    C = Y @ Rk.T; k = C.argmax(1); cc = C[np.arange(len(k)), k]
    e = GRID[k].astype(float)
    ic = (k > 0) & (k < GRID.size - 1)
    for j in np.nonzero(ic)[0]:
        a_, b_, c_ = C[j, k[j] - 1], C[j, k[j]], C[j, k[j] + 1]
        dn = a_ - 2 * b_ + c_
        if dn != 0: e[j] += np.clip(0.5 * (a_ - c_) / dn, -1, 1) * 1e-5
    e[~((cc >= 0.40) & ic)] = np.nan
    et = np.array(et); pre, post = e[et <= -8], e[et >= 10]
    if np.isfinite(pre).sum() < 10 or np.isfinite(post).sum() < 5: return float('nan')
    return float(np.nanmean(post) - np.nanmean(pre))


def wilcoxon_p(x):
    """H1: medyan < 0. P(W+ <= gözlenen) kesin; sıfırlar atılır; bağ yok varsayımı (sürekli)."""
    x = x[x != 0]; n = x.size
    if n == 0: return 1.0
    r = np.empty(n); r[np.argsort(np.abs(x))] = np.arange(1, n + 1)
    w = int(r[x > 0].sum())
    say = np.zeros(n * (n + 1) // 2 + 1); say[0] = 1
    for k in range(1, n + 1): say[k:] = say[k:] + say[:-k].copy()
    return float(say[:w + 1].sum() / 2 ** n)


def havuz(arg):
    snr, A, mev, n, tohum = arg
    rng = np.random.default_rng(tohum)
    return [istasyon(rng, snr, A, mev) for _ in range(n)]


def gecme(havuzlar, sayilar, rng, ncek=2000):
    g = 0
    for _ in range(ncek):
        x = np.concatenate([h[rng.integers(0, h.size, s)] for h, s in zip(havuzlar, sayilar)])
        x = x[np.isfinite(x)]
        g += x.size >= 8 and wilcoxon_p(x) <= 0.05
    return round(g / ncek, 3)


if __name__ == '__main__':
    t0 = time.time()
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    KOS = {'CC0,5_mev0,05': (0.577 / math.sqrt(10), 5e-4), 'CC0,5_mev0,10': (0.577 / math.sqrt(10), 1e-3),
           'CC0,7_mev0,05': (0.98 / math.sqrt(10), 5e-4)}
    isler = [(ad, A, (s, A, m, N, 9000 + 10 * i + j)) for i, (ad, (s, m)) in enumerate(KOS.items())
             for j, A in enumerate((0.0, 8e-4))]
    import multiprocessing as mp
    with mp.get_context('fork').Pool(4) as p:
        res = p.map(havuz, [x[2] for x in isler], chunksize=1)
    H = {(ad, A): np.array(r) for (ad, A, _), r in zip(isler, res)}
    rng = np.random.default_rng(31337)
    # Wilcoxon kesin testin ulaşılabilir en büyük boyutu (n = 8..15), p <= 0,05
    boy = {}
    for n in range(8, 16):
        say = np.zeros(n * (n + 1) // 2 + 1); say[0] = 1
        for k in range(1, n + 1): say[k:] = say[k:] + say[:-k].copy()
        cdf = np.cumsum(say) / 2 ** n; boy[n] = round(float(cdf[cdf <= 0.05].max()), 4)
    out = dict(N_ist=N, cekilis=2000, wilcoxon_ulasilabilir_boyut=boy, kosul={})
    for ad in KOS:
        h0, h8 = H[(ad, 0.0)], H[(ad, 8e-4)]
        out['kosul'][ad] = dict(
            gecerli_oran=[round(float(np.isfinite(h).mean()), 3) for h in (h0, h8)],
            dko_medyan_yuzde=[round(float(np.nanmedian(h)) * 100, 4) for h in (h0, h8)],
            P_A0_15kume=gecme([h0], [15], rng), P_A008_15kume=gecme([h8], [15], rng),
            P_PK_uzaklik_12sinyal_3sifir=gecme([h8, h0], [12, 3], rng),
            P_P2_16sinyal_4sifir=gecme([h8, h0], [16, 4], rng),
            P_P2_14sinyal_6sifir=gecme([h8, h0], [14, 6], rng))
    out['sure_sn'] = round(time.time() - t0)
    json.dump(out, open(os.path.join(BURASI, 'inc2_e3_bagimsiz.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))
