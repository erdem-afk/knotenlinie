"""TR-6a ön kayıt sürüm 2: İNCELEME-1 denetimlerinin (denetim1-5, scipy) numpy ile yeniden yazımı ve genişletmesi.

Yalnız yapay sayılarla çalışır; hiçbir katalog okunmaz.
 (1) A1 aşırı saçılım: yıllık Gamma çarpanı (φ = yıllık sayının var/ortalama'sı), H0 altında P(D), P(A); p0 = 0,50
     ile gerçek α; §4.6 kalibrasyonuyla (p0 = max(0,50; ⌈100 p̂0⌉/100), p̂0 = S/J, J = 3K bağımsız sahte oy) beklenen α.
 (2) A2 ana şok sonrası tamlık: Mc(t) = M_ana − 4,5 − 0,75 log10(t / 1 g) (keskin kesim, b = 1), gürültüsüz beklenen
     histogram; bölge = arka plan + Omori artçıları (p 1,1, c 0,05 g); lob yalnız arka plan (H0). Kurallar: sürüm 1
     (havuzlanmış MAXC + 0,2), A2 alt pencere kuralı, yedek (a), (b), (c). Ölçüt: P(D | H0) − P_Poisson(D) ≤ 0,02.
 (3) S7 eşleşik McNemar gücü (kesin): gölgede p 0,75, nötrde H0 Poisson değeri, bağımsız.
Kullanım: python3 -I -B tr6a_inc1_denetim.py  -> tr6a_inc1_denetim.json  (≈ 1-2 dk)
"""
import json, math, os, sys
import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6a_onkayit_sayilar as S   # noqa: E402  (Oy, kritik, sabitler)
import tr6_a_kapi as KAPI          # noqa: E402

TON, TSON = S.T_ON_G / 365.25, S.T_SON_G / 365.25
TOHUM = 20261113


def asiri_sacilim(oy):
    rng = np.random.default_rng(TOHUM)
    out = {}
    N = 400000
    for N0 in (31.36, 100.0, 500.0):
        for phi in (1.0, 1.5, 2.0, 3.0, 5.0):
            if phi == 1.0:
                g_on = np.ones(N); g_son = np.ones(N)
            else:
                kk = N0 / (phi - 1)
                g_on = rng.gamma(kk * TON, 1 / (kk * TON), N)     # ortalama 1
                g_son = rng.gamma(kk * TSON, 1 / (kk * TSON), N)
            a = rng.poisson(N0 * TON * g_on)
            b = rng.poisson(N0 * TSON * g_son)
            n = a + b
            pD = float(((b <= oy.b_dus[n]) & (n > 0)).mean())
            pA = float(((b >= oy.b_art[n]) & (n > 0)).mean())
            sat = dict(P_D=round(pD, 4), P_A=round(pA, 4), se=round(math.sqrt(pD * (1 - pD) / N), 4))
            for K in (23, 28, 39):
                c = S.kritik(K, 0.5)
                sat[f"alfa_p05_K{K}"] = round(KAPI.binom_ust(c, K, pD), 4)
                # kalibrasyonla: S ~ Binom(3K, pD), p0 = max(0,50; ⌈100 S/3K⌉/100); p0 > 0,60 -> hüküm yok (H1 yok)
                J = 3 * K
                ea = 0.0
                for s_ in range(J + 1):
                    w = math.comb(J, s_) * pD ** s_ * (1 - pD) ** (J - s_)
                    yuz = max(50, -(-100 * s_ // J))
                    if yuz > 60:
                        continue
                    ea += w * KAPI.binom_ust(S.kritik(K, yuz / 100), K, pD)
                sat[f"alfa_kalibre_K{K}"] = round(ea, 4)
            out[f"N0={N0:g} phi={phi:g}"] = sat
    return out


def bolge_hist_maxc(t, w, Mc_t, taban, b=1.0):
    """Gürültüsüz beklenen histogramın en sık 0,1 kutusu (kutu [m − 0,05, m + 0,05), taban altı kesik)."""
    kut = np.round(np.arange(round(taban + 0.05, 1), 9.0, 0.1), 1)
    h = []
    for m in kut:
        lo = np.maximum(max(m - 0.05, taban), Mc_t)
        hi = m + 0.05
        dens = np.where(hi > lo, 10 ** (-b * lo) - 10 ** (-b * hi), 0.0)
        h.append(float((w * dens).sum()))
    return float(kut[int(np.argmax(h))])


ALT_A2 = ((30, 45), (45, 60), (60, 90), (90, 180), (180, 365))
ALT_YA = ((30, 40), (40, 50), (50, 60), (60, 90), (90, 180), (180, 365))
ALT_YC = ((90, 180), (180, 365))


def tamlik(M_ana, Mc_lob, ap, kural):
    t0_, t1_ = (90, 365) if kural == "yedek_c" else (30, 365)
    t = np.arange(t0_, t1_, 0.01) + 0.005
    Mc_t = M_ana - 4.5 - 0.75 * np.log10(t)
    w_as = (t + 0.05) ** -1.1
    w_as = w_as / w_as.mean()
    w = (1 - ap) + ap * w_as
    taban = Mc_lob - 0.05
    if kural == "surum1":
        ms = bolge_hist_maxc(t, w, Mc_t, taban) + 0.2
    else:
        alt = {"A2": ALT_A2, "yedek_a": ALT_YA, "yedek_b": ALT_YA, "yedek_c": ALT_YC}[kural]
        ek = 0.4 if kural in ("yedek_b", "yedek_c") else 0.2
        ms = max(bolge_hist_maxc(t[(t >= a) & (t < b)], w[(t >= a) & (t < b)], Mc_t[(t >= a) & (t < b)], taban)
                 for a, b in alt) + ek
    mk = max(Mc_lob, ms)
    r = float(np.minimum(1.0, 10 ** (-(Mc_t - mk))).mean())   # lob (yalnız arka plan) algılanan pay
    return round(ms, 2), round(mk, 2), r


def tamlik_izgarasi():
    oy = S.Oy(30000)
    oy_c = S.Oy(30000, S.T_ON_G, 275)
    out = {}
    for kural in ("surum1", "A2", "yedek_a", "yedek_b", "yedek_c"):
        o, ts = (oy_c, 275 / 365.25) if kural == "yedek_c" else (oy, TSON)
        satir = {}
        enkotu = 0.0
        for M_ana in (7.0, 7.5, 8.0, 9.0):
            for Mc_lob in (1.0, 1.8, 3.0):
                for ap in (0.0, 0.9):
                    ms, mk, r = tamlik(M_ana, Mc_lob, ap, kural)
                    for N0 in (31.36, 100.0, 500.0, 4500.0):
                        p = o.olasilik(N0 * TON, N0 * ts * r, -1)
                        p0 = o.olasilik(N0 * TON, N0 * ts, -1)
                        fark = p - p0
                        enkotu = max(enkotu, fark)
                        satir[f"M{M_ana:g} Mc{Mc_lob:g} ap{ap:g} N0={N0:g}"] = dict(
                            Mc_son=ms, Mc_kul_eksi_Mc_lob=round(mk - Mc_lob, 2), algilanan=round(r, 4),
                            P_D=round(p, 4), P_D_poisson=round(p0, 4), fark=round(fark, 4))
        gecmeyen = [k for k, v in satir.items() if v["fark"] > 0.02]
        out[kural] = dict(en_buyuk_fark=round(enkotu, 4), gecmeyen_hucre=len(gecmeyen), hucre=len(satir),
                          gecmeyen=gecmeyen, hucreler=satir)
    return out


def mcnemar_gucu(p_g=0.75, p_n=0.4585, Ks=(23, 28, 33, 37)):
    """a = #(D_g=1, D_n=0), b = #(D_g=0, D_n=1); p = P(Binom(a+b, 0,5) >= a) <= 0,10. Kesin (üç terimli)."""
    pa, pb = p_g * (1 - p_n), (1 - p_g) * p_n
    pc = 1 - pa - pb
    out = {}
    for K in Ks:
        g = 0.0
        for a in range(K + 1):
            for b in range(K - a + 1):
                w = math.factorial(K) / (math.factorial(a) * math.factorial(b) * math.factorial(K - a - b)) \
                    * pa ** a * pb ** b * pc ** (K - a - b)
                m = a + b
                p = KAPI.binom_ust(a, m, 0.5) if m > 0 else 1.0
                if p <= 0.10:
                    g += w
        out[str(K)] = round(g, 3)
    return out


def main():
    oy = S.Oy(30000)
    out = dict(aciklama=__doc__, asiri_sacilim=asiri_sacilim(oy), tamlik=tamlik_izgarasi(),
               mcnemar_gucu=mcnemar_gucu())
    with open(os.path.join(BURAYA, "tr6a_inc1_denetim.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(json.dumps(out["asiri_sacilim"], indent=0))
    for k, v in out["tamlik"].items():
        print(k, v["en_buyuk_fark"], v["gecmeyen_hucre"], "/", v["hucre"])
    print(out["mcnemar_gucu"])


if __name__ == "__main__":
    main()
