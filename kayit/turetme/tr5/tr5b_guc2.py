#!/usr/bin/env python3
"""TR-5b sürüm 2: hüküm kuralının gücü, 4. adımın yeni ölçütü (E2), pilot P1 kapısı ve geçme olasılıkları.

Yalnız istatistik benzetimi; veri okunmaz. `tr5b_guc.py` (sürüm 1) değiştirilmedi; t dağılımı, puan ve hüküm kuralı
oradan aynen kopyalandı. Değişenler (ön kayıt sürüm 2):
  - küme yapısı `tr5b_liste_s2.json`dan (GVP volkanik kuralı sonrası volkaniksiz kümeler, Ö3);
  - eşleşik plasebo kümesi Ö5 kuralıyla (olay istasyonlarıyla kesişim);
  - 4. adım: −%0,1 eklenmiş sahte olayların r̄_sahte'sinin iki yanlı %95 t üst sınırı < 0,5 (E2); eski ölçüt
    (r̄_sahte <= 0,25, S4) bilgi;
  - pilot P1: σ̂ = 1,4826·MAD(24 istasyon Δ'sı); P̂4 < 0,50 ise "güç yok (pilot P1)". Eşdeğer eşik σ*(K);
  - K2: H0 sınırı ±0,10 ile H0 olasılığı; Ö7: olay Δ'sı 1,5 kat gürültülü.
Δ'lar σ_Δ birimindedir (σ_Δ: kontrol Δ_c'lerinin sd'si, Ö7): kontrol Δ_c ~ N(0, 1), olay Δ_e ~ N(δ, s_e²).

Kullanım: python3 -I -B tr5b_guc2.py   (çıktı: tr5b_guc2_sonuc.json; ≈ 2-4 dk)
"""
import json, math, os, time
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(BURASI, 'tr5b_liste_s2.json')))['olaylar']
TOHUM = 20261113
rng = np.random.default_rng(TOHUM)
NC, B = 5, 20000
ESIK_H0 = 0.15
SIGMA = (0.05, 0.075, 0.1, 0.15, 0.2, 0.3)          # gerçek σ_Δ, %


def t_cdf(x, df):   # tr5b_guc.py ile aynı
    def betacf(a, b, x):
        qab, qap, qam = a + b, a + 1, a - 1; c, d = 1.0, 1 - qab * x / qap
        d = 1 / d if abs(d) > 1e-30 else 1e30; h = d
        for m in range(1, 300):
            m2 = 2 * m; aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d; d = 1 / d if abs(d) > 1e-30 else 1e30; c = 1 + aa / c; h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d; d = 1 / d if abs(d) > 1e-30 else 1e30; c = 1 + aa / c; de = d * c; h *= de
            if abs(de - 1) < 1e-12: break
        return h
    if x == 0: return 0.5
    xx = df / (df + x * x); a, b = df / 2, 0.5
    lb = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(xx) + b * math.log(1 - xx)
    ib = math.exp(lb) * betacf(a, b, xx) / a if xx < (a + 1) / (a + b + 2) else 1 - math.exp(lb) * betacf(b, a, 1 - xx) / b
    return 1 - 0.5 * ib if x > 0 else 0.5 * ib
_tq = {}
def t_q(p, df):
    if (p, df) in _tq: return _tq[(p, df)]
    lo, hi = -50.0, 50.0
    for _ in range(200):
        m = (lo + hi) / 2
        if t_cdf(m, df) < p: lo = m
        else: hi = m
    _tq[(p, df)] = (lo + hi) / 2
    return _tq[(p, df)]


ana = [r for r in L if not r['volkanik']]
kumeler = {}
for r in ana: kumeler.setdefault(r['kume'], []).append(r)
OLAY_SAYISI = [len(v) for v in kumeler.values()]
PL_KUME = [k for k, v in kumeler.items() if any(r['plasebo'] for r in v)]
K0, KP0 = len(OLAY_SAYISI), len(PL_KUME)
K_Z, KP_Z = 28, 15     # Z aygıt önizlemesi sonrası (tr5b_ozet_s2.json Z_onizleme); aşama 0'ın üst sınırı
assert json.load(open(os.path.join(BURASI, 'tr5b_ozet_s2.json')))['Z_onizleme']['K'] == K_Z


def r_puan(De, Dc):
    return ((Dc < De[..., None]).sum(-1) + 0.5 * (Dc == De[..., None]).sum(-1)) / Dc.shape[-1]


def kume_sec(K):
    return np.array(OLAY_SAYISI)[rng.choice(len(OLAY_SAYISI), K, replace=False) if K <= len(OLAY_SAYISI)
                                 else rng.choice(len(OLAY_SAYISI), K)]


def benzet(delta, K=K0, Kp=KP0, s_e=1.0, mutlak=False, nb=B, esik_h0=ESIK_H0):
    """tr5b_guc.benzet ile aynı kural (plasebo eşleşik fark Ö5: küme r_e − r_p, df = K_p − 1)."""
    ne = kume_sec(K)
    kume_r = np.zeros((nb, K))
    De_k = delta + s_e * rng.standard_normal((nb, K))
    for j in range(K):
        Dc = rng.standard_normal((nb, ne[j], NC))
        De = np.repeat(De_k[:, j:j + 1], ne[j], axis=1)
        kume_r[:, j] = (r_puan(np.abs(De), np.abs(Dc)) if mutlak else r_puan(De, Dc)).mean(axis=1)
    m = kume_r.mean(1); se = kume_r.std(1, ddof=1) / math.sqrt(K)
    t95, t90 = t_q(0.975, K - 1), t_q(0.95, K - 1)
    if mutlak:
        return dict(H1_ana=float((m - t90 * se > 0.5).mean()))
    h1_ana = (m - t95 * se > 0.5) | (m + t95 * se < 0.5)
    Kp_ = min(Kp, K)
    Dp = s_e * rng.standard_normal((nb, Kp_)); rp = np.zeros((nb, Kp_))
    for j in range(Kp_):
        rp[:, j] = r_puan(Dp[:, j], rng.standard_normal((nb, NC)))
    d = kume_r[:, :Kp_] - rp
    dm = d.mean(1); dse = d.std(1, ddof=1) / math.sqrt(Kp_); tp = t_q(0.95, Kp_ - 1)
    yon = np.sign(m - 0.5)
    d_ok = np.where(yon > 0, dm - tp * dse > 0, dm + tp * dse < 0)
    pm = rp.mean(1); pse = rp.std(1, ddof=1) / math.sqrt(Kp_); tpb = t_q(0.975, Kp_ - 1)
    p_blok = np.where(yon > 0, pm - tpb * pse > 0.5, pm + tpb * pse < 0.5)
    H1 = h1_ana & d_ok & ~p_blok
    H0 = (m - t90 * se > 0.5 - esik_h0) & (m + t90 * se < 0.5 + esik_h0) & ~H1
    return dict(H1=round(float(H1.mean()), 3), H0=round(float(H0.mean()), 3),
                ayirt_edilemez=round(float(1 - H1.mean() - H0.mean()), 3), H1_ana_yalniz=round(float(h1_ana.mean()), 3))


def auc(delta): return 0.5 * (1 + math.erf(delta / 2))


def adim4(sigma, K=K0, nb=B, kayma=-0.1):
    """Sahte olay = her olayın ilk geçerli kontrolü, kalan 4 kontrole karşı; −%0,1 eklenmiş.
    Dönen: P(üst sınır < 0,5) [E2 ölçütü], P(r̄ <= 0,25) [S4, bilgi], ort r̄."""
    ne = kume_sec(K); kr = np.zeros((nb, K))
    for j in range(K):
        Dc = rng.standard_normal((nb, ne[j], NC))
        kr[:, j] = r_puan(Dc[..., 0] + kayma / sigma, Dc[..., 1:]).mean(1)
    m = kr.mean(1); se = kr.std(1, ddof=1) / math.sqrt(K)
    return dict(P_gecer=round(float((m + t_q(0.975, K - 1) * se < 0.5).mean()), 3),
                P_S4=round(float((m <= 0.25).mean()), 3), r_ort=round(float(m.mean()), 3))


def sigma_yildiz(K, nb=8000):
    """P̂4(σ) = 0,5 olan σ (%). P̂4 σ'da azalan."""
    lo, hi = 0.05, 1.0
    for _ in range(14):
        mid = (lo + hi) / 2
        if adim4(mid, K, nb)['P_gecer'] >= 0.5: lo = mid
        else: hi = mid
    return round((lo + hi) / 2, 4)


def p1_gecer(sigma, s_yildiz, n=24, nb=200000):
    x = sigma * rng.standard_normal((nb, n))
    med = np.median(x, axis=1, keepdims=True)
    s_hat = 1.4826 * np.median(np.abs(x - med), axis=1)
    return round(float((s_hat <= s_yildiz).mean()), 3), round(float(np.quantile(s_hat / sigma, 0.1)), 3), round(float(np.quantile(s_hat / sigma, 0.9)), 3)


t0 = time.time()
out = dict(tohum=TOHUM, B=B, K_ana=K0, K_plasebo_eslesik=KP0, K_Z_onizleme=K_Z, K_p_Z_onizleme=KP_Z,
           olay_sayisi_kume=sorted(OLAY_SAYISI, reverse=True), n_kontrol=NC)
# 1. hüküm olasılıkları (K = K0)
out['tablo_K0'] = {f'{dl:.2f}': dict(AUC=round(auc(dl), 3), **benzet(dl)) for dl in (0.0, 0.25, 0.5, 0.75, 1.0)}
print('tablo_K0', out['tablo_K0'], f'{time.time() - t0:.0f} sn', flush=True)
# 2. K'ye göre
out['tablo_K'] = {}
for K, Kp in ((K_Z, KP_Z), (25, 13), (20, 10)):
    for dl in (0.0, 0.5, 0.75):
        out['tablo_K'][f'K{K}_Kp{Kp}_d{dl:.2f}'] = benzet(dl, K=K, Kp=Kp)
print('tablo_K', out['tablo_K'], flush=True)
# 3. en küçük ölçülebilir δ (güç 0,8)
def en_kucuk(anahtar, K=K0, Kp=KP0):
    lo, hi = 0.0, 2.0
    for _ in range(12):
        m = (lo + hi) / 2
        if benzet(m, K=K, Kp=Kp, nb=4000)[anahtar] >= 0.8: hi = m
        else: lo = m
    return round(hi, 3)
ek = dict(ana_aralik=en_kucuk('H1_ana_yalniz'), tam_H1=en_kucuk('H1'))
ek['ana_aralik_AUC'] = round(auc(ek['ana_aralik']), 3); ek['tam_H1_AUC'] = round(auc(ek['tam_H1']), 3)
ek['yuzde_sigma_0.05_0.1_0.2'] = {k: [round(ek[k] * s, 4) for s in (0.05, 0.1, 0.2)] for k in ('ana_aralik', 'tam_H1')}
out['en_kucuk_delta_guc80'] = ek
print(ek, flush=True)
# 4. ölçek farkı (işaretli / mutlak), Ö7 olay gürültüsü, K2 H0 sınırı
out['olcu_kiyas'] = dict(H0_olcek_farki_isaretli=benzet(0.0, s_e=1.5)['H1_ana_yalniz'],
                         H0_olcek_farki_mutlak=round(benzet(0.0, s_e=1.5, mutlak=True)['H1_ana'], 3))
out['O7_olay_gurultusu_1.5'] = {f'{dl:.2f}': benzet(dl, s_e=1.5)['H1'] for dl in (0.5, 0.75, 1.0)}
out['K2_H0_siniri'] = {'0.15': benzet(0.0)['H0'], '0.10': benzet(0.0, esik_h0=0.10)['H0']}
print(out['olcu_kiyas'], out['O7_olay_gurultusu_1.5'], out['K2_H0_siniri'], flush=True)
# 5. N1
ne = np.array(OLAY_SAYISI); kr = np.zeros((B, K0))
for j in range(K0):
    Dc = rng.standard_normal((B, ne[j], NC)); kr[:, j] = r_puan(Dc[..., 0], Dc[..., 1:]).mean(1)
m = kr.mean(1); se = kr.std(1, ddof=1) / math.sqrt(K0); t95 = t_q(0.975, K0 - 1)
out['N1_yanlis_gecersiz'] = round(float(((m - t95 * se > 0.5) | (m + t95 * se < 0.5)).mean()), 4)
# 6. 4. adım (E2) ve S4, σ_Δ ve K'ye göre
out['adim4'] = {f'K{K}': {f'{s}%': adim4(s, K) for s in SIGMA} for K in (K0, K_Z, 25, 20)}
print('adim4', out['adim4'], f'{time.time() - t0:.0f} sn', flush=True)
# 7. pilot P1: σ*(K) ve P(P1 geçer | gerçek σ)
out['P1_sigma_yildiz'] = {f'K{K}': sigma_yildiz(K) for K in (K0, K_Z, 25, 20)}
out['P1_gecer'] = {}
for K in (K0, K_Z, 20):
    sy = out['P1_sigma_yildiz'][f'K{K}']
    out['P1_gecer'][f'K{K}'] = {f'{s}%': dict(zip(('P', 'shat_oran_q10', 'shat_oran_q90'), p1_gecer(s, sy))) for s in SIGMA}
# 8. birleşik: P1 ve 4. adım (bağımsız varsayımıyla çarpım; K = K_Z)
out['birlesik_P1_x_adim4_KZ'] = {f'{s}%': round(out['P1_gecer'][f'K{K_Z}'][f'{s}%']['P'] * out['adim4'][f'K{K_Z}'][f'{s}%']['P_gecer'], 3)
                                 for s in SIGMA}
print('P1', out['P1_sigma_yildiz'], out['P1_gecer'], out['birlesik_P1_x_adim4_KZ'], flush=True)
out['sure_sn'] = round(time.time() - t0)
json.dump(out, open(os.path.join(BURASI, 'tr5b_guc2_sonuc.json'), 'w'), ensure_ascii=False, indent=1)
