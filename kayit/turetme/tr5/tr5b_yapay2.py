#!/usr/bin/env python3
"""TR-5b sürüm 2: yapay veri, iki iş (gerçek dalga formu yok). `tr5b_yapay.py` (sürüm 1) değiştirilmedi; zincirin
başvuru fonksiyonları (`seri`, `zincir`, `ay_esle`, `ger`, `bant_gurultu`, `wilcoxon_tek_yan`) oradan alınır.

  donder  (Ö9) E1/E2'nin yapay günlük ÇİF dizileri dosyaya dondurulur: 3 SNR düzeyi × 20 tekrar × (özgün, son yılı
          −%0,1 gerilmiş) × 1095 gün × 2401 örnek, float16; geçerli gün maskesi ve takvim ayı ile. Başvuru Δ ve oranı,
          dosyadan geri okunan (float16 -> float64) dizilerle `tr5b_yapay.zincir/ay_esle` ile hesaplanır ve
          `tr5b_yapay_ccf_ref.json`'a yazılır. Koşu kodu 1. adımda her dizide Δ'yı %0,0005, oranı 0,005 içinde üretmelidir.
  e3      (E3d) pozitif kontrolün geçme olasılığı, sürüm 2 PK tanımıyla: germe ızgarası ±%2,0 (E3b; adım %0,001,
          kaba-ince arama: önce %0,01 adım, sonra kaba en iyilerin ±%0,015'inin birleşiminde %0,001 adım; tam ızgarayla eşdeğerlik
          `--denetle` ile sınanır), 15 küme (16 PK kümesinden us7000irfb'nin tek istasyonu aygıt önizlemesinde düşer),
          5 bağımsız havuz × 1000 yapay istasyon, A = 0 / 0,02 / 0,05 / 0,08 / 0,15 %; mevsim genliği %0,05 (iki SNR)
          ve %0,10 (CC10 ≈ 0,5). Havuz başına 2000 çekiliş. Enerji reddi (E3a) yapay veride yoktur.

Gürültü doğrusal ve Gauss olduğu için e3 yalnız gereken günleri üretir: yığınlar için [T-69, T-8] ve [T+1, T+30];
başvurunun kalan günlerinin gürültü toplamı tek bir bant sınırlı satırın √n katıdır (dağılımca aynı); başvurunun
sinyal toplamı ε'ları 1e-5'e yuvarlanarak hesaplanır (gecikmede ≤ 0,2 ms kayma).

Kullanım: python3 -I -B tr5b_yapay2.py donder <çıktı.npz>
          python3 -I -B tr5b_yapay2.py e3 [--denetle] [--hizli]
"""
import hashlib, importlib.util, json, math, os, sys, time
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location('tr5b_yapay', os.path.join(BURASI, 'tr5b_yapay.py'))
YP = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(YP)
tau, koda = YP.tau, YP.koda
SNR = {'CC10~0,5': 0.577 / math.sqrt(10), 'CC10~0,7': 0.98 / math.sqrt(10), 'CC10~0,9': 2.06 / math.sqrt(10)}


# ====================================================================== Ö9: dondurulmuş yapay ÇİF'ler
def donder(yol, n_tekrar=20, tohum=20261114):
    rng = np.random.default_rng(tohum)
    gunler = np.arange(-YP.TABAN_GUN, 0)
    C16, C16b, GEC, AY, ref = [], [], [], [], []
    for ad, s in SNR.items():
        for k in range(n_tekrar):
            T_ord = 737000 + int(rng.integers(0, 365)); ay = YP.gun_ay(T_ord, gunler)
            faz = rng.uniform(0, 2 * np.pi)
            ccf, gec = YP.seri(rng, s, 5e-4 * np.sin(2 * np.pi * gunler / 365.25 + faz))
            ccf2 = ccf.copy()
            for i in np.nonzero(gunler >= -365)[0]: ccf2[i] = YP.ger(ccf[i], -1e-3)
            a16, b16 = ccf.astype(np.float16), ccf2.astype(np.float16)
            D0 = YP.ay_esle(YP.zincir(a16.astype(np.float64), gec, gunler, 0), gunler, ay)
            D2 = YP.ay_esle(YP.zincir(b16.astype(np.float64), gec, gunler, 0), gunler, ay)
            C16.append(a16); C16b.append(b16); GEC.append(gec); AY.append(ay)
            ref.append(dict(snr=ad, tekrar=k, T_ord=T_ord, delta_yuzde=round(D0 * 100, 6), delta_eklenmis_yuzde=round(D2 * 100, 6),
                            oran=round((D2 - D0) / -1e-3, 5)))
        print(ad, 'tamam', flush=True)
    np.savez(yol, ccf=np.stack(C16), ccf_eklenmis=np.stack(C16b), gecerli=np.stack(GEC), ay=np.stack(AY).astype(np.int8),
             gunler=gunler.astype(np.int16), tau=tau)
    sha = hashlib.sha256()
    with open(yol, 'rb') as f:
        for blok in iter(lambda: f.read(1 << 24), b''): sha.update(blok)
    out = dict(dosya=os.path.basename(yol), sha256=sha.hexdigest(), bayt=os.path.getsize(yol), tohum=tohum,
               bicim='ccf, ccf_eklenmis: (60, 1095, 2401) float16; gecerli: (60, 1095) bool; ay: (60, 1095) int8; '
                     'gunler: T\'ye göre gün (−1095 … −1); tau: gecikme (s); sıra: SNR (0,5 / 0,7 / 0,9) × 20 tekrar',
               tolerans=dict(delta_yuzde=0.0005, oran=0.005), seriler=ref)
    for ad in SNR:
        o = [r['oran'] for r in ref if r['snr'] == ad]
        out[f'ozet_{ad}'] = dict(oran_medyan=round(float(np.median(o)), 4), oran_min=round(min(o), 4), oran_max=round(max(o), 4))
    json.dump(out, open(os.path.join(BURASI, 'tr5b_yapay_ccf_ref.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != 'seriler'}, ensure_ascii=False, indent=1))


# ====================================================================== E3 (sürüm 2 PK)
PK_EPS_MAX, PK_ADIM = 0.02, 1e-5
EPS_TAM = np.arange(-PK_EPS_MAX, PK_EPS_MAX + PK_ADIM / 2, PK_ADIM)
EPS_KABA = np.arange(-PK_EPS_MAX, PK_EPS_MAX + 1e-4 / 2, 1e-4)
TK = tau[koda]


def _R(ref, eps):
    R = np.interp((TK[None, :] * (1 + eps[:, None])).ravel(), tau, ref).reshape(len(eps), -1)
    R = R - R.mean(1, keepdims=True); return R / np.linalg.norm(R, axis=1, keepdims=True)


def germe_pk(Y, ref, tam=False):
    """±%2 ızgara, adım %0,001, parabol inceltme; geçerli: CC >= 0,40 ve ızgara kenarında değil."""
    Y = Y[:, koda]; Y = Y - Y.mean(1, keepdims=True); Y = Y / np.linalg.norm(Y, axis=1, keepdims=True)
    if tam:
        C = Y @ _R(ref, EPS_TAM).T; k = C.argmax(1)
    else:
        kb = (Y @ _R(ref, EPS_KABA).T).argmax(1)
        idx = sorted({j for kk in kb for j in range(max(0, kk * 10 - 15), min(len(EPS_TAM), kk * 10 + 16))})
        C = np.full((len(Y), len(EPS_TAM)), -2.0)
        C[:, idx] = Y @ _R(ref, EPS_TAM[idx]).T       # ince arama: bütün satırların pencerelerinin birleşimi
        k = C.argmax(1)
    cc = C[np.arange(len(k)), k]; eps = EPS_TAM[k].copy()
    ic = (k > 0) & (k < len(EPS_TAM) - 1)
    a, b, c = C[ic, k[ic] - 1], C[ic, k[ic]], C[ic, k[ic] + 1]
    den = a - 2 * b + c
    ok_ = (a > -1.5) & (c > -1.5) & (den != 0)
    off = np.where(ok_, 0.5 * (a - c) / np.where(den != 0, den, 1), 0.0)
    eps[ic] += np.clip(off, -1, 1) * PK_ADIM
    eps[~((cc >= YP.CC_MIN) & ic)] = np.nan
    return eps


def pk_istasyon(rng, snr, A, a_mev, tam=False):
    """Bir yapay istasyonun δ_ko'su (sürüm 2 tanımı). Gün indisi T'ye göre."""
    gun_all = np.arange(-YP.TABAN_GUN, 31)
    faz = rng.uniform(0, 2 * np.pi)
    e = a_mev * np.sin(2 * np.pi * gun_all / 365.25 + faz)
    t = gun_all[gun_all >= 1]; Ak = A * rng.uniform(0.5, 1.5)
    e[gun_all >= 1] += -Ak * (1 - 0.5 * np.log1p(t) / np.log1p(50))
    n = len(gun_all)
    gec = rng.random(n) > 0.15
    b0 = rng.integers(0, n - 30); gec[b0:b0 + 30] = False
    zarf = np.exp(-np.abs(tau) / 20.0)
    G = YP.bant_gurultu(rng, 1)[0] * zarf; G /= np.sqrt(np.mean(G[koda] ** 2))
    pen = (gun_all >= -YP.TABAN_GUN) & (gun_all <= -(YP.KORUMA + 1))
    gerek = ((gun_all >= -69) & (gun_all <= -8)) | (gun_all >= 1)
    gi = np.nonzero(gerek)[0]
    sig = np.interp((tau[None, :] * (1 + e[gi, None])).ravel(), tau, G, left=0.0, right=0.0).reshape(len(gi), -1)
    gur = YP.bant_gurultu(rng, len(gi)) / snr
    ccf = {int(gun_all[g]): sig[j] + gur[j] for j, g in enumerate(gi)}
    # başvuru: pen ∩ geçerli günler; sinyal kısmı tam, gürültünün gerekmeyen günleri tek satırda toplanır
    rm = pen & gec
    ri = np.nonzero(rm)[0]
    eb, say = np.unique(np.round(e[ri], 5), return_counts=True)     # 1e-5 bölmeli (kayma ≤ 0,2 ms, örnek 50 ms)
    sig_all = (np.interp((tau[None, :] * (1 + eb[:, None])).ravel(), tau, G, left=0.0, right=0.0).reshape(len(eb), -1)
               * say[:, None]).sum(0)
    ic_ = [i for i in ri if gerek[i]]; dis = len(ri) - len(ic_)
    gur_sum = sum(gur[np.searchsorted(gi, i)] for i in ic_) + (YP.bant_gurultu(rng, 1)[0] * math.sqrt(dis) / snr if dis else 0)
    ref = (sig_all + gur_sum) / len(ri)
    def yigin(d):
        rows = [ccf[x] for x in range(d - 9, d + 1) if x in ccf and gec[x + YP.TABAN_GUN]]
        return np.mean(rows, axis=0) if len(rows) >= YP.YIGIN_MIN else None
    pre_d = list(range(-60, -7)); post_d = list(range(10, 31))
    Y, etik = [], []
    for d in pre_d + post_d:
        y = yigin(d)
        if y is not None: Y.append(y); etik.append(d)
    if not Y: return np.nan
    eps = germe_pk(np.array(Y), ref, tam)
    etik = np.array(etik)
    pre = eps[etik <= -8]; post = eps[etik >= 10]
    if np.sum(~np.isnan(pre)) < 10 or np.sum(~np.isnan(post)) < 5: return np.nan
    return float(np.nanmean(post) - np.nanmean(pre))


def _havuz(arg):
    snr, A, a_mev, n, tohum = arg
    rng = np.random.default_rng(tohum)
    return [pk_istasyon(rng, snr, A, a_mev) for _ in range(n)]


def e3(hizli=False, denetle=False):
    t0 = time.time()
    if denetle:
        rng1, rng2 = np.random.default_rng(5), np.random.default_rng(5)
        a = [pk_istasyon(rng1, SNR['CC10~0,5'], 8e-4, 5e-4, tam=True) for _ in range(60)]
        b = [pk_istasyon(rng2, SNR['CC10~0,5'], 8e-4, 5e-4, tam=False) for _ in range(60)]
        fark = np.nanmax(np.abs(np.array(a) - np.array(b)))
        print('kaba-ince ile tam ızgara: en büyük δ_ko farkı', fark, 'NaN eşleşmesi', np.array_equal(np.isnan(a), np.isnan(b)), flush=True)
        return dict(n=60, en_buyuk_fark=float(fark), nan_esit=bool(np.array_equal(np.isnan(a), np.isnan(b))))
    N_HAVUZ, N_IST, N_CEK, N_KUME = (2, 100, 500, 15) if hizli else (5, 1000, 2000, 15)
    A_L = (0.0, 2e-4, 5e-4, 8e-4, 1.5e-3); MEV = (5e-4, 1e-3); SN = ('CC10~0,5', 'CC10~0,7')
    isler = []
    for sn in SN:
        for mv in MEV:
            if mv == 1e-3 and sn != 'CC10~0,5': continue      # %0,10 mevsim satırı yalnız düşük SNR'de (en kötü durum)
            for A in A_L:
                for h in range(N_HAVUZ):
                    tohum = int(hashlib.sha256(f'e3v2|{sn}|{mv}|{A}|{h}'.encode()).hexdigest()[:8], 16)
                    isler.append(((SNR[sn], A, mv, N_IST, tohum), (sn, mv, A, h)))
    import multiprocessing as mp
    with mp.get_context('fork').Pool(4) as p:
        sonuc = p.map(_havuz, [x[0] for x in isler], chunksize=1)
    out = {}
    for (arg, (sn, mv, A, h)), dko in zip(isler, sonuc):
        dko = np.array(dko); rng = np.random.default_rng(arg[4] + 1)
        g = 0
        for _ in range(N_CEK):
            x = dko[rng.integers(0, len(dko), N_KUME)]; x = x[~np.isnan(x)]
            g += (len(x) >= 8) and YP.wilcoxon_tek_yan(x) <= 0.05
        key = f'{sn}|mevsim={mv * 100:.2f}%|A={A * 100:.2f}%'
        r = out.setdefault(key, dict(P=[], gecerli=[], dko_medyan_yuzde=[]))
        r['P'].append(round(g / N_CEK, 4)); r['gecerli'].append(round(float(np.mean(~np.isnan(dko))), 3))
        r['dko_medyan_yuzde'].append(round(float(np.nanmedian(dko)) * 100, 4))
    for k, r in out.items():
        r['P_ort'] = round(float(np.mean(r['P'])), 3); r['P_min'] = min(r['P']); r['P_max'] = max(r['P'])
    res = dict(n_havuz=N_HAVUZ, n_istasyon=N_IST, n_cekilis=N_CEK, n_kume=N_KUME, izgara='±2%, adım 0,001%',
               sonuc=out, sure_sn=round(time.time() - t0))
    json.dump(res, open(os.path.join(BURASI, 'tr5b_yapay2_e3_sonuc.json' if not hizli else '/dev/null'), 'w'), ensure_ascii=False, indent=1)
    for k, r in out.items(): print(k, r['P_ort'], r['P_min'], r['P_max'], r['dko_medyan_yuzde'][0], flush=True)
    return res


if __name__ == '__main__':
    if sys.argv[1] == 'donder': donder(sys.argv[2])
    elif sys.argv[1] == 'e3': e3(hizli='--hizli' in sys.argv, denetle='--denetle' in sys.argv)
