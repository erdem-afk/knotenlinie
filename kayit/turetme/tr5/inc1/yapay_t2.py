#!/usr/bin/env python3
"""TR-5b: dv/v ölçü zincirinin YAPAY veriyle doğrulanması (gerçek dalga formu yok).

Bu betik ön kayıttaki (§3) dv/v zincirinin başvuru uygulamasıdır: günlük ÇİF -> başvuru (pencere ortalaması) ->
10 günlük geriye dönük yığın -> germe (stretching) -> ay eşlemeli Δ. Yapay günlük ÇİF'ler bant sınırlı (0,5-2 Hz)
bir "Green fonksiyonu"nun bilinen dv/v ile gerilmesi ve üstüne bağımsız bant sınırlı gürültü eklenmesiyle kurulur.

Deneyler (ön kayıt §6):
  E1  H0: yalnız mevsimsel dv/v (genlik %0,05, rastgele evre) ve ölçüm gürültüsü -> Δ'nın yanlılığı ve σ_ölçüm.
  E2  Kod denetimi (ii-a): son yılın günlük ÇİF'lerine -%0,1 germe eklenir; oran = (Δ_eklenmiş - Δ_özgün) / (-%0,1).
      35 'sahte olay' istasyonunun medyan oranının [0,8; 1,2] içinde kalma olasılığı.
  E3  Pozitif kontrol (kosismik): T'de A kadar düşüş, 50 günde yarıya logaritmik toparlanma; δ_ko ölçülür;
      16 yakın kümede tek yanlı Wilcoxon işaretli sıra p <= 0,05 olasılığı (A ve SNR'ye göre).

Kullanım: python3 -I -B tr5b_yapay.py [--hizli]   (çıktı: tr5b_yapay_sonuc.json bu dizine)
"""
import json, math, os, sys, time
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
HIZLI = '--hizli' in sys.argv

# ------------------------------------------------------------------ önceden sabit parametreler (ön kayıt §3)
FS = 20.0                       # Hz (indirgeme sonrası)
TAU_MAX = 60.0                  # s, ÇİF gecikme aralığı ±60 s
BANT = (0.5, 2.0)               # Hz, ana bant
KODA = (10.0, 40.0)             # s, |gecikme| koda penceresi (iki yan)
YIGIN = 10                      # gün, geriye dönük yığın [d-9, d]
YIGIN_MIN = 5                   # yığında en az geçerli gün
EPS_MAX, EPS_ADIM = 0.005, 1e-5 # germe ızgarası ±%0,5, adım %0,001
CC_MIN = 0.40                   # germe ilişki katsayısı alt sınırı
AY_MIN_GUN, AY_MIN = 10, 9      # ay eşlemesi: ay başına >= 10 geçerli gün, >= 9 eşleşen ay
TABAN_GUN, KORUMA = 1095, 7     # pencere [T-1095, T-8]

tau = np.arange(-TAU_MAX, TAU_MAX + 0.5 / FS, 1 / FS)
koda = (np.abs(tau) >= KODA[0]) & (np.abs(tau) <= KODA[1])
EPS = np.arange(-EPS_MAX, EPS_MAX + EPS_ADIM / 2, EPS_ADIM)


def bant_gurultu(rng, n_satir):
    """Bant sınırlı (0,5-2 Hz, 0,1 Hz kosinüs kenarlı) beyaz gürültü, satır başına birim RMS."""
    n = len(tau); nf = 1 << (n - 1).bit_length()
    f = np.fft.rfftfreq(nf, 1 / FS)
    w = np.zeros_like(f)
    w[(f >= BANT[0]) & (f <= BANT[1])] = 1
    for lo, hi in ((BANT[0] - 0.1, BANT[0]), (BANT[1], BANT[1] + 0.1)):
        m = (f > lo) & (f < hi)
        x = (f[m] - lo) / (hi - lo)
        w[m] = 0.5 - 0.5 * np.cos(np.pi * (x if lo < BANT[0] else 1 - x))
    z = rng.standard_normal((n_satir, nf))
    y = np.fft.irfft(np.fft.rfft(z, axis=1) * w, nf, axis=1)[:, :n]
    return y / y.std(axis=1, keepdims=True)


def ger(sig, eps):
    """sig(τ) -> sig(τ(1+eps)) (dv/v = eps: hız artarsa varışlar erkene kayar)."""
    return np.interp(tau * (1 + eps), tau, sig, left=0.0, right=0.0)


def germe_olc(yiginlar, ref):
    """Her yığın için (ε, CC). Izgara + parabolik incelik. Yığın satırları NaN ise NaN döner."""
    R = np.stack([np.interp(tau[koda] * (1 + e), tau, ref) for e in EPS])
    R = R - R.mean(axis=1, keepdims=True); R /= np.linalg.norm(R, axis=1, keepdims=True)
    Y = yiginlar[:, koda]; Y = Y - Y.mean(axis=1, keepdims=True)
    nrm = np.linalg.norm(Y, axis=1, keepdims=True); nrm[nrm == 0] = np.nan
    C = (Y / nrm) @ R.T
    k = np.nanargmax(np.nan_to_num(C, nan=-2), axis=1)
    cc = C[np.arange(len(k)), k]
    eps = EPS[k].copy()
    ic = (k > 0) & (k < len(EPS) - 1)
    a, b, c = C[ic, k[ic] - 1], C[ic, k[ic]], C[ic, k[ic] + 1]
    den = a - 2 * b + c
    off = np.where(den != 0, 0.5 * (a - c) / den, 0.0)
    eps[ic] += np.clip(off, -1, 1) * EPS_ADIM
    gecerli = (cc >= CC_MIN) & ic
    eps[~gecerli] = np.nan
    return eps, cc


def zincir(ccf, gecerli_gun, gunler, T, ref_gun=None):
    """ccf: (gün, örnek); gunler: gün indisleri (T'ye göre, negatif = önce). Dönen: yığın-sonu günü -> ε."""
    pen = (gunler >= -TABAN_GUN) & (gunler <= -(KORUMA + 1))
    rm = pen & gecerli_gun if ref_gun is None else ref_gun
    ref = ccf[rm].mean(axis=0)
    n = len(gunler); Ys = np.full((n, ccf.shape[1]), np.nan)
    cs = np.cumsum(np.where(gecerli_gun[:, None], ccf, 0), axis=0); cn = np.cumsum(gecerli_gun)
    for i in range(n):
        j0 = i - YIGIN
        s = cs[i] - (cs[j0] if j0 >= 0 else 0); c = cn[i] - (cn[j0] if j0 >= 0 else 0)
        if c >= YIGIN_MIN: Ys[i] = s / c
    ok = ~np.isnan(Ys[:, 0])
    eps = np.full(n, np.nan)
    if ok.any():
        e, _ = germe_olc(Ys[ok], ref); eps[ok] = e
    return eps


def ay_esle(eps, gunler, ay):
    """Δ = ortalama_m [ ort(ε | C, ay m) - ort(ε | A∪B, ay m) ]; C = [T-365, T-8], A∪B = [T-1095, T-366]."""
    C = (gunler >= -365) & (gunler <= -(KORUMA + 1)); AB = (gunler >= -TABAN_GUN) & (gunler <= -366)
    fark = []
    for m in range(1, 13):
        c = C & (ay == m) & ~np.isnan(eps); ab = AB & (ay == m) & ~np.isnan(eps)
        if c.sum() >= AY_MIN_GUN and ab.sum() >= AY_MIN_GUN: fark.append(eps[c].mean() - eps[ab].mean())
    return float(np.mean(fark)) if len(fark) >= AY_MIN else float('nan')


def seri(rng, snr_gun, eps_gercek, eksik=0.15):
    """Yapay günlük ÇİF dizisi: G gerilmiş + gürültü / snr. Döner (ccf, gecerli_gun)."""
    zarf = np.exp(-np.abs(tau) / 20.0)
    G = bant_gurultu(rng, 1)[0] * zarf
    G /= np.sqrt(np.mean(G[koda] ** 2))
    n = len(eps_gercek)
    ccf = np.stack([ger(G, e) for e in eps_gercek]) + bant_gurultu(rng, n) / snr_gun
    gec = rng.random(n) > eksik
    b = rng.integers(0, n - 30); gec[b:b + 30] = False       # bir 30 günlük boşluk
    return ccf, gec


def gun_ay(T_ord, gunler):
    import datetime as dt
    return np.array([dt.date.fromordinal(T_ord + int(g)).month for g in gunler])


def E1_E2(snr_gun, n_tekrar, rng):
    gunler = np.arange(-TABAN_GUN, 0)
    T_ord = 737000 + int(rng.integers(0, 365))
    ay = gun_ay(T_ord, gunler)
    d0, oran, ccs = [], [], []
    for _ in range(n_tekrar):
        faz = rng.uniform(0, 2 * np.pi)
        e_true = 5e-4 * np.sin(2 * np.pi * gunler / 365.25 + faz)
        ccf, gec = seri(rng, snr_gun, e_true)
        eps = zincir(ccf, gec, gunler, 0)
        D = ay_esle(eps, gunler, ay)
        # E2: son yılın günlük ÇİF'lerine -%0,1 germe (yığın ve başvuru yeniden hesaplanır)
        ccf2 = ccf.copy(); m = gunler >= -365
        for i in np.nonzero(m)[0]: ccf2[i] = ger(ccf[i], -1e-3)
        eps2 = zincir(ccf2, gec, gunler, 0)
        D2 = ay_esle(eps2, gunler, ay)
        d0.append(D); oran.append((D2 - D) / -1e-3)
        ccs.append(np.nanmean(np.isnan(eps[(gunler <= -8)])))
    d0, oran = np.array(d0), np.array(oran)
    return dict(snr_gun=snr_gun, n=n_tekrar, gecersiz_delta=int(np.isnan(d0).sum()),
                delta_ort_yuzde=round(float(np.nanmean(d0)) * 100, 4), sigma_olcum_yuzde=round(float(np.nanstd(d0)) * 100, 4),
                oran_medyan=round(float(np.nanmedian(oran)), 3), oran_q05=round(float(np.nanquantile(oran, 0.05)), 3),
                oran_q95=round(float(np.nanquantile(oran, 0.95)), 3), oran_sd=round(float(np.nanstd(oran)), 3),
                gecersiz_gun_orani=round(float(np.mean(ccs)), 3), _oran=oran[~np.isnan(oran)].tolist(),
                _delta=d0[~np.isnan(d0)].tolist())


def wilcoxon_tek_yan(x):
    """H1: medyan < 0. Kesin dağılım (n <= 30): P(W+ <= gözlenen)."""
    x = np.asarray([v for v in x if v != 0 and not np.isnan(v)])
    n = len(x)
    if n == 0: return 1.0
    r = np.argsort(np.argsort(np.abs(x))) + 1
    wplus = int(r[x > 0].sum())
    dp = np.zeros(n * (n + 1) // 2 + 1); dp[0] = 1
    for k in range(1, n + 1):
        yeni = dp.copy(); yeni[k:] += dp[:-k]; dp = yeni
    dp /= dp.sum()
    return float(dp[:wplus + 1].sum())


def E3(snr_gun, A_list, n_havuz, n_kume, n_tekrar, rng):
    """Her A için n_havuz yapay istasyon (bir istasyon = bir küme) üretilir.
    δ_ko (ana)  = ort ε[yığın sonu T+10..T+30] - ort ε[T-60..T-8]; başvuru olay öncesi pencere.
    δ_ko (mev)  = δ_ko(ana) - (aynı iki takvim penceresinin bir yıl önceki farkı): mevsimden arındırılmış değişke.
    Sonra havuzdan n_kume'lik kümeler çekilip tek yanlı kesin Wilcoxon (p <= 0,05, geçerli küme >= 8)."""
    gunler = np.arange(-TABAN_GUN, 31)
    pen = (gunler >= -TABAN_GUN) & (gunler <= -(KORUMA + 1))
    pre = (gunler >= -60) & (gunler <= -8); post = (gunler >= 10) & (gunler <= 30)
    pre1 = (gunler >= -60 - 365) & (gunler <= -8 - 365); post1 = (gunler >= 10 - 365) & (gunler <= 30 - 365)
    sonuc = {}
    for A in A_list:
        dko, dmev = [], []
        for _ in range(n_havuz):
            faz = rng.uniform(0, 2 * np.pi)
            e = 5e-4 * np.sin(2 * np.pi * gunler / 365.25 + faz)
            t = gunler[gunler >= 1]
            Ak = A * rng.uniform(0.5, 1.5)                        # kümeden kümeye genlik saçılımı
            e[gunler >= 1] += -Ak * (1 - 0.5 * np.log1p(t) / np.log1p(50))
            ccf, gec = seri(rng, snr_gun, e)
            eps = zincir(ccf, gec, gunler, 0, ref_gun=pen & gec)
            ok = lambda m, k: np.sum(~np.isnan(eps[m])) >= k
            d = np.nanmean(eps[post]) - np.nanmean(eps[pre]) if ok(pre, 10) and ok(post, 5) else np.nan
            d1 = np.nanmean(eps[post1]) - np.nanmean(eps[pre1]) if ok(pre1, 10) and ok(post1, 5) else np.nan
            dko.append(d); dmev.append(d - d1)
        dko, dmev = np.array(dko), np.array(dmev)
        gecti = np.zeros(2)
        for _ in range(n_tekrar):
            ix = rng.integers(0, n_havuz, n_kume)
            for j, v in enumerate((dko, dmev)):
                x = v[ix]; x = x[~np.isnan(x)]
                gecti[j] += (len(x) >= 8) and wilcoxon_tek_yan(x) <= 0.05
        r = {}
        for j, (ad, v) in enumerate((('ana', dko), ('mevsimden_arindirilmis', dmev))):
            g = v[~np.isnan(v)]
            r[ad] = dict(gecme_olasiligi=round(gecti[j] / n_tekrar, 3), gecerli_oran=round(len(g) / n_havuz, 3),
                         dko_medyan_yuzde=round(float(np.median(g)) * 100, 4), dko_sd_yuzde=round(float(np.std(g)) * 100, 4))
        sonuc[f'A={A * 100:.3f}%'] = dict(n_havuz=n_havuz, **r)
    return sonuc


if __name__ == '__main__':
    t0 = time.time()
    rng = np.random.default_rng(777123)
    SNR = {'CC10~0,5': 0.577 / math.sqrt(10), 'CC10~0,7': 0.98 / math.sqrt(10), 'CC10~0,9': 2.06 / math.sqrt(10)}
    out = dict(parametre=dict(FS=FS, BANT=BANT, KODA=KODA, YIGIN=YIGIN, YIGIN_MIN=YIGIN_MIN, EPS_MAX=EPS_MAX,
                              EPS_ADIM=EPS_ADIM, CC_MIN=CC_MIN, AY_MIN_GUN=AY_MIN_GUN, AY_MIN=AY_MIN, tohum=777123),
               E1_E2={}, E2_35_sahte={}, E3={})
    n12 = 40 if HIZLI else 120
    for ad, s in SNR.items():
        r = E1_E2(s, n12, rng)
        o = np.array(r.pop('_oran')); r.pop('_delta')
        # 35 sahte olayın medyan oranı [0,8; 1,2] içinde mi: önyükleme (10 000)
        b = np.median(o[rng.integers(0, len(o), (10000, 35))], axis=1)
        out['E2_35_sahte'][ad] = dict(medyan_oran_q01=round(float(np.quantile(b, 0.01)), 3),
                                      medyan_oran_q99=round(float(np.quantile(b, 0.99)), 3),
                                      P_aralik_disi=round(float(np.mean((b < 0.8) | (b > 1.2))), 4))
        out['E1_E2'][ad] = r
        print(ad, r, out['E2_35_sahte'][ad], f'{time.time() - t0:.0f} sn', flush=True)
    n3 = 40 if HIZLI else 200
    for ad in ('CC10~0,5', 'CC10~0,7'):
        out['E3'][ad] = E3(SNR[ad], [2e-4, 5e-4, 8e-4, 1.5e-3], n3, 16, 2000, rng)
        print('E3', ad, out['E3'][ad], f'{time.time() - t0:.0f} sn', flush=True)
    out['sure_sn'] = round(time.time() - t0)
    json.dump(out, open(os.path.join(BURASI, 'tr5b_yapay_sonuc.json'), 'w'), ensure_ascii=False, indent=1)
