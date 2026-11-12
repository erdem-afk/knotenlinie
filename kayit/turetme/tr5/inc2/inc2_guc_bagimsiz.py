#!/usr/bin/env python3
"""TR-5b İNCELEME-2: `tr5b_guc2.py` sayılarının bağımsız yazımla, küçük örnekte denetimi (yalnız benzetim; veri yok).

Bağımsız olan: t niceliği (t yoğunluğunun sayısal tümlevi, betacf değil), puan (sıralama ile değil karşılaştırma
sayımıyla, ama aynı tanım), hüküm kuralı ön kayıt §4.2 adım 9 metninden yeniden yazıldı, tohum 515151, B = 12000.
Model ön kayıt §4.4 ile aynı: σ_Δ birimi; kontrol Δ_c ~ N(0,1); aynı kümenin olayları aynı Δ_e'yi paylaşır
(aynı gün, aynı istasyon); olay başına 5 kontrol; plasebo etkisiz.
Ek: P1'in etkin eşiği (istasyon düzeyi σ̂ ile kontrol düzeyi σ farkı) için 4. adımın σ = 0,817·σ* noktasındaki
geçme olasılığı ve P1'in iki uçtaki geçme olasılığı.
Kullanım: python3 -I -B inc2_guc_bagimsiz.py   (≈ 3-5 dk)
"""
import json, math, os
import numpy as np

BURASI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(os.path.dirname(BURASI), 'tr5b_liste_s2.json')))['olaylar']
rng = np.random.default_rng(515151)
B = 12000
kume = {}
for r in L:
    if not r['volkanik']: kume.setdefault(r['kume'], []).append(r)
NE = np.array([len(v) for v in kume.values()])


def t_nicel(p, df):
    x = np.linspace(-60, 60, 600001)
    f = (1 + x * x / df) ** (-(df + 1) / 2)
    F = np.cumsum(f); F /= F[-1]
    return float(np.interp(p, F, x))


TQ = {}
def tq(p, df):
    if (p, df) not in TQ: TQ[(p, df)] = t_nicel(p, df)
    return TQ[(p, df)]


def puan(De, Dc):          # De: (B,), Dc: (B, n)
    return ((Dc < De[:, None]).mean(1) + 0.5 * (Dc == De[:, None]).mean(1))


def hukum(delta, K=31, Kp=16, se_olay=1.0):
    ne = NE[rng.permutation(len(NE))[:K]]
    kr = np.empty((B, K))
    De = delta + se_olay * rng.standard_normal((B, K))
    for j in range(K):
        kr[:, j] = np.mean([puan(De[:, j], rng.standard_normal((B, 5))) for _ in range(ne[j])], axis=0)
    m = kr.mean(1); s = kr.std(1, ddof=1) / math.sqrt(K)
    ana = (m - tq(.975, K - 1) * s > .5) | (m + tq(.975, K - 1) * s < .5)
    rp = np.stack([puan(se_olay * rng.standard_normal(B), rng.standard_normal((B, 5))) for _ in range(Kp)], 1)
    d = kr[:, :Kp] - rp; dm = d.mean(1); ds = d.std(1, ddof=1) / math.sqrt(Kp)
    yukari = m > .5
    d_ok = np.where(yukari, dm - tq(.95, Kp - 1) * ds > 0, dm + tq(.95, Kp - 1) * ds < 0)
    pm = rp.mean(1); ps = rp.std(1, ddof=1) / math.sqrt(Kp)
    p_ayni = np.where(yukari, pm - tq(.975, Kp - 1) * ps > .5, pm + tq(.975, Kp - 1) * ps < .5)
    H1 = ana & d_ok & ~p_ayni
    H0 = ~H1 & (m - tq(.95, K - 1) * s > .35) & (m + tq(.95, K - 1) * s < .65)
    return dict(H1=round(H1.mean(), 3), H0=round(H0.mean(), 3), ana=round(ana.mean(), 3))


def adim4(sig, K=31, kayma=-0.1):
    ne = NE[rng.permutation(len(NE))[:K]]
    kr = np.empty((B, K))
    for j in range(K):
        kr[:, j] = np.mean([puan(rng.standard_normal(B) + kayma / sig, rng.standard_normal((B, 4)))
                            for _ in range(ne[j])], axis=0)
    m = kr.mean(1); s = kr.std(1, ddof=1) / math.sqrt(K)
    return round(float((m + tq(.975, K - 1) * s < .5).mean()), 3)


def p1(sig, esik, n=24, nb=40000):
    x = sig * rng.standard_normal((nb, n))
    sh = 1.4826 * np.median(np.abs(x - np.median(x, 1, keepdims=True)), 1)
    return round(float((sh <= esik).mean()), 3)


out = dict(tohum=515151, B=B, K=len(NE))
out['hukum_K31_Kp16'] = {f'{d}': hukum(d) for d in (0.0, 0.5, 0.75)}
out['hukum_K20_Kp10_d0'] = hukum(0.0, K=20, Kp=10)
out['O7_olay_1.5_d0.75'] = hukum(0.75, se_olay=1.5)['H1']
out['adim4_K31'] = {f'{s}%': adim4(s) for s in (0.1, 0.15, 0.2, 0.3)}
# σ*(K31): P(4. adım geçer) = 0,5
lo, hi = 0.15, 0.35
for _ in range(10):
    mid = (lo + hi) / 2
    if adim4(mid) >= 0.5: lo = mid
    else: hi = mid
sy = round((lo + hi) / 2, 4); out['sigma_yildiz_K31'] = sy
out['adim4_K31_0.817_sigma_yildiz'] = dict(sigma=round(0.817 * sy, 4), P=adim4(0.817 * sy))
# P1, kontrol düzeyi σ_c verilmişken: tam ilişki (σ_ist = σ_c) ve bağımsızlık (σ_ist = σ_c / 0,817)
out['P1_gecer_K31'] = {f'{s}%': dict(tam_iliski=p1(s, sy), bagimsiz=p1(s / 0.817, sy)) for s in (0.1, 0.15, 0.2, 0.25)}
json.dump(out, open(os.path.join(BURASI, 'inc2_guc_bagimsiz.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
