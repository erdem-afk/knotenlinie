#!/usr/bin/env python3
"""TR-6c İNCELEME-1: küme düzeyinde (binom) benzetim. Yalnız yapay veri; gerçek katalog açılmaz.

Ne yapar:
  1. Yanlış "H1" oranı (H0 dünyaları): K_kapı kümesi, her kümenin H0 düşüş oyu olasılığı p_i (N0'a ve dünyaya bağlı;
     TR-6c §C5 kesin değerleri + §C6 prova kenar kaymaları), sahte oy olasılığı q_i, sahte sayısı J_i (önsayım
     `sahte_gecerli`). p₀ = KO.p0_kestir (kenar kümeleri hariç havuz: TR-6c; dahil: TR-6a biçimi), p₀ > 0,60 →
     "güç yok (ölçü yanlı)", testere dişi KO.testere, en zayıf = en küçük N0, H1 ⟺ X ≥ c(K_h; p₀).
  2. Yanlış "H0" oranı (tasarım H1 dünyası p₁ 0,75 = f P_D + (1 − f) w): kenar kümelerinde w kenar kaymasıyla düşer.
  3. Görülebilir en küçük etki (MDE): K'ye göre, p₀ 0,50 / 0,52; ×0,5 ve ×2 duyarlılığı.

Kullanım: python3 -I -B kayit/turetme/tr6/inc_c/inc_c_alfa.py [tekrar] > çıktı.json
"""
import json
import math
import os
import sys

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(BURA))
import tr6a_onkayit_sayilar as S     # noqa: E402
import tr6a_kosu as KO               # noqa: E402

N_TEKRAR = int(sys.argv[1]) if len(sys.argv) > 1 else 200000
rng = np.random.default_rng(91011)   # inceleme tohumu (bağlayıcı değil)

# önsayım (olay öncesi, kaba N0; tr6a_onkayit_sayilar.json onsayim.19; Sumatra (d) ile çıkar → 28 küme)
ON = json.load(open(os.path.join(os.path.dirname(BURA), "tr6a_onkayit_sayilar.json"), encoding="utf-8"))
KUM = [(c[0]["id"], c[0]["N0"], c[0]["sahte_gecerli"]) for c in ON["onsayim"]["19"]["kumeler"]
       if c[0]["id"] != "official20041226005853450_30"]
assert len(KUM) == 28

# N0 → H0 düşüş/artış oyu olasılığı. Kesin (kümesizleştirmesiz, 275 g; TR-6c §C5) ve prova hat − kesin kaymaları (§C6).
N0_IZ = np.array([31.36, 100.0, 500.0, 1500.0, 4500.0])
KESIN = np.array([0.4426, 0.4682, 0.4862, 0.4920, 0.4954])          # N0_kul ile (prova tablosu "kesin")
HAT_I = np.array([0.4464, 0.4622, 0.4730, 0.4283, 0.3214])          # (i) koşulsuz hat P(D)
HAT_II = np.array([0.4428, 0.4671, 0.4658, 0.4253, 0.3267])         # (ii)


def pD(N0, dunya):
    x = np.log(np.clip(N0, 31.36, 4500.0))
    return float(np.interp(x, np.log(N0_IZ), HAT_I if dunya == "i" else HAT_II))


def c_K(K, p0):
    return S.kritik(K, p0)


def senaryo(ad, p, q, J, N0, kenar, kural_c=True, n=N_TEKRAR):
    """p: gerçek oy olasılıkları, q: sahte oy olasılıkları, J: sahte sayıları; kenar: bool dizi."""
    K = len(p)
    p, q, J, kenar = map(np.asarray, (p, q, J, kenar))
    havuz = ~kenar if kural_c else np.ones(K, bool)
    Jh = int(J[havuz].sum())
    # sahte S ~ Σ Binom(J_i, q_i) (havuzdaki kümeler)
    Ssim = np.zeros(n, int)
    for i in np.where(havuz)[0]:
        if J[i]:
            Ssim += rng.binomial(J[i], q[i], n)
    Xb = rng.random((n, K)) < p[None, :]
    sira = np.argsort(N0, kind="stable")              # en zayıf önce (eşitlik yok)
    h1 = olcu = 0
    p0_say = {}
    for S_ in np.unique(Ssim):
        sel = Ssim == S_
        p0, _ = KO.p0_kestir(int(S_), Jh)
        p0_say[p0] = p0_say.get(p0, 0) + int(sel.sum())
        if p0 > S.P0_UST:
            olcu += int(sel.sum())
            continue
        tz = KO.testere(K, p0)
        at = set(sira[:tz["atilan"]].tolist())
        ana = [i for i in range(K) if i not in at]
        X = Xb[sel][:, ana].sum(1)
        h1 += int((X >= c_K(len(ana), p0)).sum())
    return dict(ad=ad, K=K, J=Jh, yanlis_H1=round(h1 / n, 4), se=round(math.sqrt(max(h1, 1) / n) / math.sqrt(n), 4),
                olcu_yanli=round(olcu / n, 4), p0_dagilim={f"{k:.2f}": round(v / n, 4) for k, v in sorted(p0_say.items())})


def alfa_bolumu():
    out = []
    N0 = np.array([x[1] for x in KUM])
    J = np.array([x[2] for x in KUM])
    kenar = N0 > 500.0
    for dunya in ("i", "ii"):
        p = np.array([pD(x, dunya) for x in N0])
        out.append(senaryo(f"önsayım K=28, ({dunya}) Poisson hat, sahte = gerçek", p, p, J, N0, kenar))
        out.append(senaryo(f"önsayım K=28, ({dunya}), TR-6a havuzu (kenar sahteleri dahil)", p, p, J, N0, kenar,
                           kural_c=False))
    # aşırı saçılım: kenar dışı kümeler TR-6a §4.3 en kötü hücresi 0,5151 (φ 5); kenar kümeleri (ii) hat değeri
    p = np.where(kenar, [pD(x, "ii") for x in N0], 0.5151)
    out.append(senaryo("önsayım K=28, φ 5 (0,5151), sahte = gerçek", p, p, J, N0, kenar))
    # kalibrasyon uyuşmazlığı: sahteler gerçekten 0,02 düşük (gerçek 0,5151 + 0,02)
    p2 = np.where(kenar, p, 0.5351)
    out.append(senaryo("önsayım K=28, gerçek 0,535, sahte 0,515 (uyuşmazlık −0,02)", p2, p, J, N0, kenar))
    # kenar kümeleri de H0'da 0,50'ye çıksın (gerçek kümelenme kenar kaymasını yensin), öteki 0,5151
    p3 = np.where(kenar, 0.50, 0.5151)
    out.append(senaryo("önsayım K=28, kenar kümeleri 0,50, öteki 0,5151", p3, p3, J, N0, kenar))
    # K = 23 (kapı sınırı): en büyük 23 N0 (iki kenar dahil), J önsayımdaki gibi
    o = np.argsort(-N0)[:23]
    for dunya in ("i", "ii"):
        pp = np.array([pD(x, dunya) for x in N0[o]])
        out.append(senaryo(f"K=23, ({dunya}) Poisson hat", pp, pp, J[o], N0[o], kenar[o]))
    pp = np.where(kenar[o], [pD(x, "ii") for x in N0[o]], 0.5151)
    out.append(senaryo("K=23, φ 5 (0,5151)", pp, pp, J[o], N0[o], kenar[o]))
    pp2 = np.where(kenar[o], pp, 0.5351)
    out.append(senaryo("K=23, gerçek 0,535, sahte 0,515", pp2, pp, J[o], N0[o], kenar[o]))
    # J < 30 dalı: J'lerin yarısı geçersiz (sahte kapı), φ 5
    Jy = J // 2
    out.append(senaryo("önsayım K=28, J yarıya (J<30 dalı), φ 5", p, p, Jy, N0, kenar))
    # kapı seçim yanlılığı (prova: i:31,36'da P(D | kapı) 0,540, koşulsuz 0,446): kapıya yakın (N0 < 40) kümeler 0,54
    yak = N0 < 40.0
    for dunya in ("i", "ii"):
        pb = np.array([pD(x, dunya) for x in N0])
        pk = np.where(yak, 0.54, pb)
        out.append(senaryo(f"önsayım K=28, ({dunya}), kapı yakını {int(yak.sum())} küme 0,54, sahte de 0,54", pk, pk, J,
                           N0, kenar))
        out.append(senaryo(f"önsayım K=28, ({dunya}), kapı yakını 0,54, sahte koşulsuz (soğurmaz)", pk, pb, J, N0,
                           kenar))
    # en kötü: bütün kenar dışı kümeler kapı sınırında (0,54) ve sahteler aynı
    pz = np.where(kenar, [pD(x, "ii") for x in N0], 0.54)
    out.append(senaryo("önsayım K=28, bütün kenar dışı 0,54, sahte 0,54", pz, pz, J, N0, kenar))
    # inc_c_kapi bulgusu: kapıyı geçen kümelerin sahteleri gerçek oydan ≈ 0,05 düşük (N0 31,36: gerçek 0,538, sahte
    # 0,487). g küme kapı sınırında, ötekiler (ii) hattı.
    sira = np.argsort(N0)
    for g in (4, 10, 16, 26):
        at = np.zeros(len(N0), bool)
        at[sira[:g]] = True
        pr = np.where(at, 0.538, [pD(x, "ii") for x in N0])
        qs = np.where(at, 0.487, pr)
        out.append(senaryo(f"önsayım K=28, en küçük N0'lı {g} küme kapı sınırında (gerçek 0,538, sahte 0,487)", pr, qs,
                           J, N0, kenar))
        if g <= 23:
            o23 = sira[len(N0) - 23:] if g == 0 else np.r_[sira[:g], sira[len(N0) - (23 - g):]]
            out.append(senaryo(f"K=23, {g} küme kapı sınırında (0,538 / 0,487)", pr[o23], qs[o23], J[o23], N0[o23],
                               kenar[o23]))
    return out


def uyusmazlik_bolumu(n=100000):
    """Gerçek pencere sahte pencereden δ kadar 'düşüşçü' (kalibrasyonun soğurmadığı yanlılık; ör. Risk 6): önsayım
    K = 28, kenar kümeleri (ii) hat değeri, öteki kümelerde sahte q, gerçek q + δ. Yanlış H1 oranı."""
    N0 = np.array([x[1] for x in KUM])
    J = np.array([x[2] for x in KUM])
    ke = N0 > 500.0
    out = []
    for q in (0.46, 0.50, 0.5151):
        for d in (0.0, 0.02, 0.03, 0.04, 0.05, 0.07):
            p = np.where(ke, [pD(x, "ii") for x in N0], q + d)
            qq = np.where(ke, p, q)
            r = senaryo(f"q {q}, δ {d}", p, qq, J, N0, ke, n=n)
            out.append(dict(q=q, delta=d, yanlis_H1=r["yanlis_H1"], olcu_yanli=r["olcu_yanli"]))
    return out


def h0_bolumu():
    """Tasarım H1 dünyası: p₁ = f·P_D + (1 − f)·w; f 0,549, P_D 0,987, w = H0 düzeyi (N0'a göre (i) hattı).
    Kenarsız (w = 0,4574 her kümede) ile kenarlı (önsayım N0'larıyla) yanlış H0 (X ≤ h) ve güç."""
    f, PD = 0.549, 0.987
    out = []
    for K in (23, 28):
        c, h = S.kritik(K, 0.5), S.esik_H0(K)
        p_kenarsiz = f * PD + (1 - f) * 0.4574
        for ad, wl in (("kenarsız (w 0,4574)", [0.4574] * K),
                       ("1 küme N0 4500 (w 0,321)", [0.4574] * (K - 1) + [0.3214]),
                       ("2 küme (N0 584 → 0,470; 4500 → 0,321)", [0.4574] * (K - 2) + [0.470, 0.3214]),
                       ("5 küme N0 4500", [0.4574] * (K - 5) + [0.3214] * 5)):
            ps = [f * PD + (1 - f) * w for w in wl]
            out.append(dict(K=K, c=c, h=h, durum=ad, p1_ort=round(float(np.mean(ps)), 4),
                            guc=round(_pb_ust(c, ps), 4), yanlis_H0=round(1 - _pb_ust(h + 1, ps), 4)))
        out.append(dict(K=K, not_="p1 tam 0,75 başvuru", yanlis_H0=round(1 - _pb_ust(h + 1, [0.75] * K), 4),
                        p1_kenarsiz=round(p_kenarsiz, 4)))
    return out


def _pb_ust(c, ps):
    f = np.zeros(len(ps) + 1)
    f[0] = 1.0
    for p in ps:
        f[1:] = f[1:] * (1 - p) + f[:-1] * p
        f[0] *= (1 - p)
    return float(f[c:].sum())


def guc(K, p, p0=0.5):
    c = S.kritik(K, p0)
    return _pb_ust(c, [p] * K)


def mde_bolumu():
    out = {}
    for p0 in (0.50, 0.52):
        r = {}
        for K in (23, 25, 28, 30, 35, 40):
            lo, hi = p0, 1.0
            for _ in range(60):
                mid = (lo + hi) / 2
                (lo, hi) = (mid, hi) if guc(K, mid, p0) < 0.8 else (lo, mid)
            r[str(K)] = dict(c=S.kritik(K, p0), p1_min=round(hi, 4))
        out[f"p0_{p0:.2f}"] = r
    # gereken K (ilk K ≥ 5 ki güç ≥ 0,8 kalıcı olarak; kaba: ilk K)
    gk = {}
    for p1 in (0.625, 0.65, 0.70, 0.75, 0.80, 0.875, 0.95):
        ilk = next(K for K in range(3, 400) if guc(K, p1) >= 0.8)
        kal = next(K for K in range(3, 400) if all(guc(k, p1) >= 0.8 for k in range(K, K + 40)))
        gk[f"{p1:g}"] = dict(ilk_K=ilk, kalici_K=kal)
    out["gereken_K_p0_0.50"] = gk
    # f (doğru lob payı) cinsinden: p1 = f·0,987 + (1 − f)·0,4574
    out["f_cinsinden"] = {f"{f:g}": round(f * 0.987 + (1 - f) * 0.4574, 4) for f in (0.2745, 0.549, 1.0)}
    return out


if __name__ == "__main__":
    print(json.dumps(dict(tekrar=N_TEKRAR, kumeler=KUM, alfa=alfa_bolumu(), uyusmazlik=uyusmazlik_bolumu(), yanlis_H0=h0_bolumu(), mde=mde_bolumu()),
                     ensure_ascii=False, indent=1))
