#!/usr/bin/env python3
"""TR-4 İNCELEME-1: σ̂_Δ ve q95 kesinliğinin bağımsız küçük benzetimi (yer düzeyi; tr4_guc.py içe aktarılmaz).

Model (ön kayıt §6.2 ile aynı nesne, bağımsız yazım): yıllık düzey L(yer, yıl) = √ρ·C(yıl) + √(1-ρ)·U(yer, yıl), C, U
bağımsız N(0,1) (φ = 0); Δ(yer, T) = [L(T-1) - (L(T-2) + L(T-3))/2]·σ/√1,5 + N(0, s_olc). Hücreler gerçek yer-pencere
deseni (102; ISK temsilci). Her hücre 1 - 0,91·0,9 olasılıkla düşer (ön kayıttaki kademe C, CC10 ≈ 0,5 varsayımı).
İki yönlü önyükleme: yer ve T yılı ayrı ayrı yerine koyarak, hücre ağırlığı çoklukların çarpımı.
Sonuç: kapsama ve (c) olasılıkları; σ için %90 (5-95) ve %80 (10-90) aralıkları; q95 için %90 ve %95 aralıkları;
eşikler: karşılandı U < %0,20; karşılanmadı L > %0,20 (taslak) ya da L > %0,245 (kontrol düzeyi düzeltmesi, İNC1-Ö2).
Desenler: tam (102), T 2017-2020 (60), aşama 0'da %40 yer kaybı (sabit tohumlu bir desen; kapı altı bilgi satırı).
Kullanım: python3 -I -B inc1_kesinlik.py <tr4_pencereler.csv> [R] [D]   Çıktı: inc1_kesinlik.json ya da (D ile, yalnız
T 2017-2021 deseni) inc1_kesinlik_D.json (bu dizine). Tek süreç.
"""
import csv, hashlib, json, math, os, sys, time
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
R_SIM = int(sys.argv[2]) if len(sys.argv) > 2 else 200
B = 300
S_OLC = 0.026e-2
P_GEC = 0.91 * 0.9


def desen_oku(yol):
    h = []
    for r in csv.DictReader(open(yol)):
        if r['ana_T'] != 'True' or r['DOLU_ana'] != 'True': continue
        if r['yer'] == 'KO.ISK' and r['ist'] != 'KO.ISK': continue
        h.append((r['yer'], int(r['T'][:4])))
    return h


def kestir(v):
    return 1.4826 * np.median(np.abs(v - np.median(v))), np.quantile(np.abs(v), 0.95)


def boot(si, ti, v, rng):
    nS, nT = si.max() + 1, ti.max() + 1
    ms = rng.multinomial(nS, np.ones(nS) / nS, size=B); mt = rng.multinomial(nT, np.ones(nT) / nT, size=B)
    w = ms[:, si] * mt[:, ti]
    s = np.full(B, np.nan); q = np.full(B, np.nan)
    for b in range(B):
        x = np.repeat(v, w[b])
        if len(x) >= 5: s[b], q[b] = kestir(x)
    return s, q


def tek(hucre, sigma, rho, rng):
    yerler = sorted({y for y, _ in hucre}); yil = np.arange(2012, 2025)
    C = rng.standard_normal(len(yil)); U = rng.standard_normal((len(yerler), len(yil)))
    L = math.sqrt(rho) * C[None, :] + math.sqrt(1 - rho) * U
    yi = {y: i for i, y in enumerate(yerler)}
    kal = [(y, t) for y, t in hucre if rng.random() < P_GEC]
    i = np.array([yi[y] for y, _ in kal]); j = np.array([t - 1 - 2012 for _, t in kal])
    v = (L[i, j] - 0.5 * (L[i, j - 1] + L[i, j - 2])) * sigma / math.sqrt(1.5) + S_OLC * rng.standard_normal(len(kal))
    si = np.unique(i, return_inverse=True)[1]; ti = np.unique(j, return_inverse=True)[1]
    sh, qh = kestir(v)
    s, q = boot(si, ti, v, rng)
    return len(v), sh, qh, np.nanquantile(s, [0.05, 0.10, 0.90, 0.95]), np.nanquantile(q, [0.025, 0.05, 0.95, 0.975])


def main():
    t0 = time.time()
    H = desen_oku(sys.argv[1])
    rng0 = np.random.default_rng(777)
    yerler = sorted({y for y, _ in H})
    kayip = set(np.array(yerler)[rng0.random(len(yerler)) < 0.40])
    DES = {'tam (102)': H, 'T 2017-2020 (60)': [x for x in H if x[1] <= 2020],
           'aşama 0 %40 yer kaybı': [x for x in H if x[0] not in kayip]}
    if len(sys.argv) > 3 and sys.argv[3] == 'D':                 # kademe D (kesik koşu) en küçük kümesi
        DES = {'T 2017-2021 (74)': [x for x in H if x[1] <= 2021]}
    out = dict(R=R_SIM, B=B, s_olc_yuzde=S_OLC * 100, p_gec=P_GEC, kayip_yerler=sorted(kayip), sonuc={})
    for dad, h in DES.items():
        for rho in (0.3, 0.6):
            for sg in (0.0010, 0.0015, 0.0020, 0.00245, 0.0030):
                rng = np.random.default_rng(int(hashlib.sha256(f'inc1|{dad}|{rho}|{sg}'.encode()).hexdigest()[:8], 16))
                st = math.sqrt(sg ** 2 + S_OLC ** 2); qt = 1.959964 * st      # nüfus değerleri (normal)
                r = [tek(h, sg, rho, rng) for _ in range(R_SIM)]
                n = np.array([x[0] for x in r]); sh = np.array([x[1] for x in r]); qh = np.array([x[2] for x in r])
                sQ = np.array([x[3] for x in r]); qQ = np.array([x[4] for x in r])
                L90, U90, L80, U80 = sQ[:, 0], sQ[:, 3], sQ[:, 1], sQ[:, 2]
                k = f'{dad}|rho={rho}|sigma={sg * 100:.3f}%'
                out['sonuc'][k] = dict(
                    n_ort=round(float(n.mean()), 1), sigma_hat_oran_q05_q50_q95=[round(float(x), 3) for x in np.quantile(sh / st, [.05, .5, .95])],
                    q95_hat_oran_q05_q50_q95=[round(float(x), 3) for x in np.quantile(qh / qt, [.05, .5, .95])],
                    kapsama_sigma_90=round(float(np.mean((L90 <= st) & (U90 >= st))), 3),
                    kapsama_sigma_80=round(float(np.mean((L80 <= st) & (U80 >= st))), 3),
                    kapsama_q95_90=round(float(np.mean((qQ[:, 1] <= qt) & (qQ[:, 2] >= qt))), 3),
                    kapsama_q95_95=round(float(np.mean((qQ[:, 0] <= qt) & (qQ[:, 3] >= qt))), 3),
                    sigma_genislik_90=round(float(np.median((U90 - L90) / st)), 3),
                    karsilandi_90=round(float(np.mean(U90 < 0.002)), 3), karsilandi_80=round(float(np.mean(U80 < 0.002)), 3),
                    karsilanmadi_90_020=round(float(np.mean(L90 > 0.002)), 3), karsilanmadi_90_0245=round(float(np.mean(L90 > 0.00245)), 3),
                    karsilanmadi_80_020=round(float(np.mean(L80 > 0.002)), 3), karsilanmadi_80_0245=round(float(np.mean(L80 > 0.00245)), 3))
                print(k, out['sonuc'][k], flush=True)
    out['sure_sn'] = round(time.time() - t0)
    ad = 'inc1_kesinlik_D.json' if len(sys.argv) > 3 and sys.argv[3] == 'D' else 'inc1_kesinlik.json'
    json.dump(out, open(os.path.join(BURASI, ad), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
