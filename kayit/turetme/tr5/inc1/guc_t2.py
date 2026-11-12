#!/usr/bin/env python3
"""TR-5b: hüküm kuralının gücü ve hata olasılıkları (yalnız istatistik benzetimi; veri okunmaz).

Küme yapısı `tr5b_liste.json`dan alınır (volkanik olmayan kümeler; küme içindeki olaylar aynı Δ'yı paylaşır, her olayın
kendi 5 kontrolü vardır). Δ'lar σ_Δ birimindedir: kontrol Δ_c ~ N(0, 1), olay Δ_e ~ N(δ, s_e²).

Kural (ön kayıt §4): olay puanı r = [#(Δ_c < Δ_e) + 0,5 #(=)] / n_c; küme puanı kümedeki r'lerin ortalaması;
r̄ küme puanlarının ortalaması. H1: iki yanlı %95 t aralığı 0,5'i dışlar VE plasebo eşleşik fark d = r_e − r_p'nin
tek yanlı %95 t alt (ya da üst) sınırı 0'ı aynı yönde dışlar
ve plasebo r̄_p'nin iki yanlı %95 aralığı 0,5'i aynı yönde dışlamaz. H0 (eşdeğerlik): %90 t aralığı [0,35; 0,65] içinde. Öteki: ayırt edilemez.

Kullanım: python3 -I -B tr5b_guc.py   (çıktı: tr5b_guc_sonuc.json)
"""
import json, math, os
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(BURASI, 'tr5b_liste.json')))['olaylar']
rng = np.random.default_rng(777123)
NC, B = 5, 20000
ESIK_H0 = 0.15

# t nicelikleri (scipy yok): Cornish-Fisher yaklaşımı yerine sayısal ters çevirme
def t_cdf(x, df):
    # düzenli tamamlanmamış beta ile; sürekli kesir (Numerical Recipes betacf)
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
def t_q(p, df):
    lo, hi = -50.0, 50.0
    for _ in range(200):
        m = (lo + hi) / 2
        if t_cdf(m, df) < p: lo = m
        else: hi = m
    return (lo + hi) / 2

ana = [r for r in L if not r['volkanik']]
kumeler = {}
for r in ana: kumeler.setdefault(r['kume'], []).append(r)
OLAY_SAYISI = [len(v) for v in kumeler.values()]
PL_KUME = [k for k, v in kumeler.items() if any(r['plasebo'] for r in v)]
K0, KP0 = len(OLAY_SAYISI), len(PL_KUME)

def r_puan(De, Dc):
    return ((Dc < De[..., None]).sum(-1) + 0.5 * (Dc == De[..., None]).sum(-1)) / Dc.shape[-1]

def benzet(delta, K=K0, Kp=KP0, s_e=1.0, karisik=False, mutlak=False, nb=B):
    """Dönen: hüküm olasılıkları ve ölçü dağılımı."""
    idx = rng.choice(len(OLAY_SAYISI), K, replace=False) if K <= len(OLAY_SAYISI) else rng.choice(len(OLAY_SAYISI), K)
    ne = np.array(OLAY_SAYISI)[idx]
    kume_r = np.zeros((nb, K))
    isaret = np.where(np.arange(K) % 2 == 0, 1.0, -1.0) if karisik else np.ones(K)
    De_k = delta * isaret + s_e * rng.standard_normal((nb, K))           # küme Δ'sı (olaylar paylaşır)
    for j in range(K):
        Dc = rng.standard_normal((nb, ne[j], NC))
        De = np.repeat(De_k[:, j:j + 1], ne[j], axis=1)
        rr = r_puan(np.abs(De), np.abs(Dc)) if mutlak else r_puan(De, Dc)
        kume_r[:, j] = rr.mean(axis=1)
    m = kume_r.mean(1); se = kume_r.std(1, ddof=1) / math.sqrt(K)
    t95, t90 = t_q(0.975, K - 1), t_q(0.95, K - 1)
    if mutlak:   # tek yanlı (yalnız büyük |Δ|)
        h1 = m - t_q(0.95, K - 1) * se > 0.5
        return dict(H1_ana=float(h1.mean()), r_ort=float(m.mean()))
    h1_ana = (m - t95 * se > 0.5) | (m + t95 * se < 0.5)
    # plasebo: aynı yer, epok T-3y, etkisiz: Δ_p ~ N(0, s_e²); eşleşik ilk Kp küme
    Kp_ = min(Kp, K)
    Dp = s_e * rng.standard_normal((nb, Kp_))
    rp = np.zeros((nb, Kp_))
    for j in range(Kp_):
        Dc = rng.standard_normal((nb, NC)); rp[:, j] = r_puan(Dp[:, j], Dc)
    d = kume_r[:, :Kp_] - rp
    dm = d.mean(1); dse = d.std(1, ddof=1) / math.sqrt(Kp_); tp = t_q(0.95, Kp_ - 1)   # tek yanlı %95 (TR-1 İnc-2 b3)
    yon = np.sign(m - 0.5)
    d_ok = np.where(yon > 0, dm - tp * dse > 0, dm + tp * dse < 0)
    pm = rp.mean(1); pse = rp.std(1, ddof=1) / math.sqrt(Kp_); tpb = t_q(0.975, Kp_ - 1)
    p_blok = np.where(yon > 0, pm - tpb * pse > 0.5, pm + tpb * pse < 0.5)
    H1 = h1_ana & d_ok & ~p_blok
    H0 = (m - t90 * se > 0.5 - ESIK_H0) & (m + t90 * se < 0.5 + ESIK_H0) & ~H1
    return dict(H1=round(float(H1.mean()), 3), H0=round(float(H0.mean()), 3),
                ayirt_edilemez=round(float(1 - H1.mean() - H0.mean()), 3), H1_ana_yalniz=round(float(h1_ana.mean()), 3),
                plasebo_blok=round(float(p_blok.mean()), 3), r_ort=round(float(m.mean()), 3),
                se_ort=round(float(se.mean()), 4))

def auc(delta): return 0.5 * (1 + math.erf(delta / 2))   # Φ(δ/√2)

out = dict(K_ana=K0, K_plasebo_eslesik=KP0, olay_sayisi_kume=sorted(OLAY_SAYISI, reverse=True), n_kontrol=NC, B=B,
           sd_r_teorik=round(math.sqrt((NC + 2) / (12 * NC)), 4))
# 1. hüküm olasılıkları (K = K0)
out['tablo_K0'] = {}
for dl in (0.0, 0.25, 0.5, 0.75, 1.0):
    out['tablo_K0'][f'{dl:.2f}'] = dict(AUC=round(auc(dl), 3), **benzet(dl))
    print('K0', dl, out['tablo_K0'][f'{dl:.2f}'], flush=True)
# 2. K'ye göre: K 32 (aygıt kuralı önizlemesi), 25, 20 (kapı); plasebo K'si oranla
out['tablo_K'] = {}
for K in (32, 25, 20):
    Kp = max(10, round(KP0 * K / K0))
    for dl in (0.0, 0.5, 0.75):
        out['tablo_K'][f'K{K}_Kp{Kp}_d{dl:.2f}'] = benzet(dl, K=K, Kp=Kp)
        print('K', K, Kp, dl, out['tablo_K'][f'K{K}_Kp{Kp}_d{dl:.2f}'], flush=True)
# 3. en küçük ölçülebilir δ (güç 0,8): ana aralık yalnız ve tam H1 kuralı
def en_kucuk(anahtar, K=K0, Kp=KP0):
    lo, hi = 0.0, 2.0
    for _ in range(12):
        m = (lo + hi) / 2
        if benzet(m, K=K, Kp=Kp, nb=4000)[anahtar] >= 0.8: hi = m
        else: lo = m
    return round(hi, 3)
out['en_kucuk_delta_guc80'] = dict(ana_aralik=en_kucuk('H1_ana_yalniz'), tam_H1=en_kucuk('H1'))
out['en_kucuk_delta_guc80']['ana_aralik_AUC'] = round(auc(out['en_kucuk_delta_guc80']['ana_aralik']), 3)
out['en_kucuk_delta_guc80']['tam_H1_AUC'] = round(auc(out['en_kucuk_delta_guc80']['tam_H1']), 3)
out['en_kucuk_delta_guc80']['yuzde_sigma_0.05_0.1_0.2'] = [round(out['en_kucuk_delta_guc80'][k] * s, 4)
    for k in ('ana_aralik', 'tam_H1') for s in (0.05, 0.1, 0.2)]
print(out['en_kucuk_delta_guc80'], flush=True)
# 4. işaretli ölçü ile |Δ| ölçüsünün karşılaştırması
out['olcu_kiyas'] = dict(
    H0_olcek_farki_isaretli=benzet(0.0, s_e=1.5)['H1_ana_yalniz'],
    H0_olcek_farki_mutlak=benzet(0.0, s_e=1.5, mutlak=True)['H1_ana'],
    H0_esit_olcek_mutlak=benzet(0.0, mutlak=True)['H1_ana'],
    d050_isaretli=benzet(0.5)['H1_ana_yalniz'], d050_mutlak=benzet(0.5, mutlak=True)['H1_ana'],
    d100_isaretli=benzet(1.0)['H1_ana_yalniz'], d100_mutlak=benzet(1.0, mutlak=True)['H1_ana'],
    karisik_d100_isaretli=benzet(1.0, karisik=True)['H1_ana_yalniz'], karisik_d100_mutlak=benzet(1.0, karisik=True, mutlak=True)['H1_ana'])
print(out['olcu_kiyas'], flush=True)
# 5. negatif kontrol N1 (sahte olay = ilk kontrol, kalan 4'e karşı): H0 altında yanlış "geçersiz" olasılığı
nb = B; K = K0
ne = np.array(OLAY_SAYISI)
kr = np.zeros((nb, K))
for j in range(K):
    Dc = rng.standard_normal((nb, ne[j], NC))
    kr[:, j] = r_puan(Dc[..., 0], Dc[..., 1:]).mean(1)
m = kr.mean(1); se = kr.std(1, ddof=1) / math.sqrt(K); t95 = t_q(0.975, K - 1)
out['N1_yanlis_gecersiz'] = round(float(((m - t95 * se > 0.5) | (m + t95 * se < 0.5)).mean()), 4)
# 6. duyarlılık: sahte olaya -%0,1 eklenince r̄_sahte <= 0,25 olasılığı, σ_Δ'ya göre (4 kontrole karşı)
out['duyarlilik_P_rsahte_le_025'] = {}
for s in (0.05, 0.075, 0.1, 0.15, 0.2):
    dl = -0.1 / s
    kr = np.zeros((nb, K))
    for j in range(K):
        Dc = rng.standard_normal((nb, ne[j], NC))
        kr[:, j] = r_puan(Dc[..., 0] + dl, Dc[..., 1:]).mean(1)
    out['duyarlilik_P_rsahte_le_025'][f'sigma={s}%'] = dict(P=round(float((kr.mean(1) <= 0.25).mean()), 3),
                                                            r_sahte_ort=round(float(kr.mean()), 3))
print(out['N1_yanlis_gecersiz'], out['duyarlilik_P_rsahte_le_025'], flush=True)
json.dump(out, open(os.path.join(BURASI, 'tr5b_guc_sonuc.json'), 'w'), ensure_ascii=False, indent=1)
