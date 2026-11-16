#!/usr/bin/env python3
"""TR-6c sürüm 2, Z2 (kapı seçim yanlılığı): yol seçimi için yapay kanıt. Yalnız yapay veri ve olay öncesi önsayım.

İki aşama:
  kayit <i|ii> <tohum> <deneme> <çıktı.json>
      Tek birimli yapay dünyada (TR-6c §C3, kural (d)) gerçek oran λ ızgarasında denemeler. Her deneme için: gözlenen kapı
      N0'ı, veri yok, gerçek düşüş oyu D, geçerli sahte oyların (D′, sahte kapı N0′) listesi. Sahte kapı N0′ (a1) için
      gerekir (sahte kapı 40'ta yeniden uygulanır). Tohum bağlayıcı olamaz.
  secim <kayit_i.json> <kayit_ii.json> <tekrar> <tohum> <çıktı.json>
      Küme düzeyi benzetim. Her senaryoda her kümeye kendi λ'sından rastgele bir deneme kaydı atanır (gerçek ve sahte
      oyun aynı gerçekleşmedeki ilişkisi korunur). Tasarımlar:
        v1  sürüm 1: kapı N0 ≥ 31,36; p̂₀ yalnız kapıyı geçen (kenar dışı) kümelerin sahtelerinden;
        a1  kapı N0 ≥ 40 (gerçek ve sahte kapı); p̂₀ kapıyı geçenlerden;
        a2  kapı N0 ≥ 31,36; p̂₀ kapıdan ÖNCE bütün aday kümelerin (kenar dışı) sahtelerinden (her sahte kendi
            sahte kapısıyla);
        b   v1 + kapıyı geçen kenar dışı kümelerin yarısından fazlasının kapı N0'ı < 40 ise p₀ tabanı 0,52 (İNCELEME-1).
      Her tasarımda p₀ = KO.p0_kestir, p₀ > 0,60 → "güç yok (ölçü yanlı)", K < 23 → "güç yok", testere dişi KO.testere
      (en zayıf = en küçük gözlenen kapı N0), H1 ⟺ X ≥ c(K_h; p₀). Yanlış H1 (H0 dünyası) ve güç (tasarım H1 dünyası:
      kapıyı geçen her kümede f = 0,549 olasılıkla D ~ Bern(0,987), yoksa H0 kaydının D'si).
      Kenar kümeleri (kapı N0 > 500): her zaman kapıdan geçer, sahteleri havuza girmez, H0 D'si prova hattından
      (§C6: (i) 0,4283 / 0,3214, (ii) 0,4253 / 0,3267; N0 583,7 için log ara değer).

Kullanım (deponun kökünde):
  python3 -I -B kayit/turetme/tr6/tr6c_z2.py kayit i 7331 4000 <dizin>/z2_kayit_i.json
  python3 -I -B kayit/turetme/tr6/tr6c_z2.py secim <dizin>/z2_kayit_i.json <dizin>/z2_kayit_ii.json 20000 7332 \
      kayit/turetme/tr6/tr6c_z2_secim.json
"""
import json
import math
import os
import sys
import time

import numpy as np

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr6a_onkayit_sayilar as S     # noqa: E402
import tr6a_kosu as KO               # noqa: E402
import tr6a_yapay as Y               # noqa: E402

LAM = (6.0, 10.0, 14.0, 17.08, 20.0, 23.0, 26.0, 28.5, 30.0, 31.36, 33.0, 34.5, 36.0, 38.0, 40.0, 42.5, 45.0, 48.0,
       52.0, 57.0, 63.0, 70.0, 78.0, 87.0, 97.0, 110.0, 135.0, 170.0, 220.0, 320.0)
KAPI, KAPI_A1, N0_YAKIN = 31.36, 40.0, 40.0
F_DOGRU, PD_ADIM = 0.549, 0.987
KENAR_HAT = {"i": {583.7: None, 1500.0: 0.4283, 4500.0: 0.3214, 500.0: 0.4730},
             "ii": {583.7: None, 1500.0: 0.4253, 4500.0: 0.3267, 500.0: 0.4658}}


def kenar_pD(N0, dunya):
    t = KENAR_HAT[dunya]
    x = np.log([500.0, 1500.0, 4500.0])
    y = [t[500.0], t[1500.0], t[4500.0]]
    return float(np.interp(math.log(min(max(N0, 500.0), 4500.0)), x, y))


# ------------------------------------------------------------------------------------------------ kayıt aşaması
def kayit(dunya, tohum, n, cikti):
    Y.tohum_denetle_c(tohum, False)
    T = Y.tek_birim_c()
    an = T.an
    ozgun = an.sahte_oylari
    yakala = {}

    def sarmal(B, k):
        x = ozgun(B, k)
        yakala["so"] = x
        return x
    an.sahte_oylari = sarmal
    out = dict(dunya=dunya, tohum=tohum, deneme=n, lam=list(LAM), kayit={})
    t0 = time.time()
    for li, lam in enumerate(LAM):
        sp = dict(N0=lam, dtau="sifir", ikincil_bolge=True)
        if dunya == "ii":
            sp["ikincil_lob"] = True
        rng = np.random.default_rng([tohum, 1 if dunya == "i" else 2, li])
        sat = []
        for _ in range(n):
            yakala.clear()
            r = T.deneme(rng, sp, sahte=True, ham=False)
            sh = [(int(x["D"]), round(x["n_on_kapi"] / KO.N0_YIL, 3)) for x in yakala["so"] if x["gecerli"]]
            vy = r.get("veri_yok", False) or r.get("D") is None
            sat.append([round(r["N0_kapi"], 3), int(vy), -1 if vy else int(r["D"]), sh])
        out["kayit"][f"{lam:g}"] = sat
        print(f"{time.strftime('%H:%M:%S')} {dunya} λ {lam:g} bitti ({time.time() - t0:.0f} s)", flush=True)
    an.sahte_oylari = ozgun
    with open(cikti, "w", encoding="utf-8") as f:
        json.dump(out, f)


# ------------------------------------------------------------------------------------------------ seçim aşaması
class Kayitlar:
    def __init__(self, yol):
        d = json.load(open(yol, encoding="utf-8"))
        self.dunya = d["dunya"]
        self.lam = np.array(d["lam"])
        self.k = {}
        for li, lam in enumerate(d["lam"]):
            sat = d["kayit"][f"{lam:g}"]
            N0k = np.array([s[0] for s in sat])
            vy = np.array([s[1] for s in sat], bool)
            D = np.array([s[2] for s in sat])
            # sahteler: (31,36 kapısıyla geçerli sayısı, D′ toplamı), (40 kapısıyla geçerli, D′ toplamı)
            J31 = np.array([len(s[3]) for s in sat])
            S31 = np.array([sum(x[0] for x in s[3]) for s in sat])
            J40 = np.array([sum(1 for x in s[3] if x[1] >= KAPI_A1) for s in sat])
            S40 = np.array([sum(x[0] for x in s[3] if x[1] >= KAPI_A1) for s in sat])
            self.k[li] = dict(N0k=N0k, vy=vy, D=D, J31=J31, S31=S31, J40=J40, S40=S40)

    def li(self, lam):
        return int(np.argmin(np.abs(np.log(self.lam) - math.log(lam))))


def benzetim(kay, lamlar, tasarim, n, rng, h1=False, kaydir_gercek=0.0, kaydir_sahte=0.0):
    """lamlar: küme gerçek oranları (kenar > 500 dahil). Dönüş: yanlış H1 (ya da güç), ölçü yanlı, güç yok payları,
    K ve J ortalaması, p₀ dağılımı."""
    lamlar = np.asarray(lamlar, float)
    kenar = lamlar > 500.0
    nk = int((~kenar).sum())
    idx = [kay.li(x) for x in lamlar[~kenar]]
    kapi = KAPI_A1 if tasarim == "a1" else KAPI
    # her tekrar, her kenar dışı küme için rastgele kayıt
    N0k = np.zeros((n, nk))
    vy = np.zeros((n, nk), bool)
    D = np.zeros((n, nk))
    J = np.zeros((n, nk))
    Ss = np.zeros((n, nk))
    for j, li in enumerate(idx):
        r = kay.k[li]
        s = rng.integers(0, len(r["D"]), n)
        N0k[:, j], vy[:, j], D[:, j] = r["N0k"][s], r["vy"][s], r["D"][s]
        if tasarim == "a1":
            J[:, j], Ss[:, j] = r["J40"][s], r["S40"][s]
        else:
            J[:, j], Ss[:, j] = r["J31"][s], r["S31"][s]
    # kaydırmalar (aşırı saçılım ya da uyuşmazlık): D = 0 olan oy, δ / (1 − 0,5) olasılıkla 1 olur
    if kaydir_gercek:
        D = np.where((D == 0) & (rng.random(D.shape) < 2 * kaydir_gercek), 1, D)
    if kaydir_sahte:
        ek = rng.binomial((J - Ss).astype(int), min(1.0, 2 * kaydir_sahte))
        Ss = Ss + ek
    gecen = (N0k >= kapi) & ~vy
    if h1:
        dogru = rng.random(D.shape) < F_DOGRU
        D = np.where(dogru, (rng.random(D.shape) < PD_ADIM).astype(float), D)
    # havuz
    if tasarim == "a2":
        Jh, Sh = J.sum(1), Ss.sum(1)
    else:
        Jh, Sh = (J * gecen).sum(1), (Ss * gecen).sum(1)
    # kenar kümeleri
    ke_lam = lamlar[kenar]
    nkenar = len(ke_lam)
    if nkenar:
        pk = np.array([kenar_pD(x, kay.dunya) for x in ke_lam])
        if h1:
            pk = F_DOGRU * PD_ADIM + (1 - F_DOGRU) * pk
        Dk = (rng.random((n, nkenar)) < pk[None, :]).astype(float)
    sonuc = dict(H1=0, olcu=0, gucyok=0)
    Ks, p0s = [], {}
    for t in range(n):
        g = np.where(gecen[t])[0]
        K = len(g) + nkenar
        Ks.append(K)
        p0, _ = KO.p0_kestir(int(Sh[t]), int(Jh[t]))
        if tasarim == "b":
            yakin = int((N0k[t, g] < N0_YAKIN).sum())
            if 2 * yakin > len(g):
                p0 = max(p0, 0.52)
        p0s[p0] = p0s.get(p0, 0) + 1
        if K < S.K_ALT:
            sonuc["gucyok"] += 1
            continue
        if p0 > S.P0_UST:
            sonuc["olcu"] += 1
            continue
        tz = KO.testere(K, p0)
        # en zayıf = en küçük kapı N0 (kenar kümeleri en güçlü)
        sira = g[np.argsort(N0k[t, g], kind="stable")]
        ana = sira[tz["atilan"]:]
        X = D[t, ana].sum() + (Dk[t].sum() if nkenar else 0)
        if X >= S.kritik(K - tz["atilan"], p0):
            sonuc["H1"] += 1
    return dict(oran=round(sonuc["H1"] / n, 4), se=round(math.sqrt(max(sonuc["H1"], 1)) / n, 4),
                olcu_yanli=round(sonuc["olcu"] / n, 4), guc_yok=round(sonuc["gucyok"] / n, 4),
                K_ort=round(float(np.mean(Ks)), 2), J_ort=round(float(Jh.mean()), 1),
                p0_050=round(p0s.get(0.5, 0) / n, 3), p0_dagilim={f"{k:.2f}": round(v / n, 4) for k, v in sorted(p0s.items())})


def onsayim():
    """Olay öncesi önsayım (tr6a_onkayit_sayilar.json onsayim.19): K_kaba 28 kümenin kaba N0'ı (Sumatra (d) ile çıkar);
    kapı altı aday kümeler yalnız sayı olarak bilinir: 17,08–31,36 arasında 6 küme (K 35 − 29), 17,08 altında
    81 − 49 = 32 birim. Bunlara ızgaradan oran verilir (6 küme 17,5–30 arasında log eşit; 32'nin yerine 25 küme
    6–14 arasında)."""
    ON = json.load(open(os.path.join(BURA, "tr6a_onkayit_sayilar.json"), encoding="utf-8"))
    kum = [c[0]["N0"] for c in ON["onsayim"]["19"]["kumeler"] if c[0]["id"] != "official20041226005853450_30"]
    assert len(kum) == 28
    bant = list(np.exp(np.linspace(math.log(17.5), math.log(30.0), 6)))
    alt = list(np.exp(np.linspace(math.log(6.0), math.log(14.0), 25)))
    return sorted(kum), bant, alt


def senaryolar():
    kum, bant, alt = onsayim()
    kum = np.array(kum)
    ke = kum > 500
    kd = np.sort(kum[~ke])                         # 26 kenar dışı
    s = []
    s.append(("önsayım (28 küme + kapı altı adaylar)", list(kum) + bant + alt, {}))
    s.append(("önsayım, en büyük 23 küme (+ kapı altı)", list(np.sort(kum)[-23:]) + bant + alt, {}))
    for g in (4, 10, 16, 26):
        y = np.r_[np.full(g, 31.36), kd[g:], kum[ke]]
        s.append((f"en küçük {g} küme λ 31,36 (kapı sınırında)", list(y) + bant + alt, {}))
    for lam_ in (34.0, 40.0, 45.0):
        y = np.r_[np.full(26, lam_), kum[ke]]
        s.append((f"kenar dışı 26 kümenin hepsi λ {lam_:g}", list(y) + bant + alt, {}))
    y = np.r_[np.full(16, 31.36), kd[16:], kum[ke]]
    s.append(("K 23 civarı: en küçük 16 küme λ 31,36, en büyük 23 + kapı altı",
              list(np.r_[np.full(16, 31.36), np.sort(kum)[-7:]]) + bant + alt, {}))
    s.append(("önsayım, aşırı saçılım (gerçek ve sahte +0,03)", list(kum) + bant + alt,
              dict(kaydir_gercek=0.03, kaydir_sahte=0.03)))
    s.append(("hepsi λ 31,36 + aşırı saçılım +0,03", list(np.r_[np.full(26, 31.36), kum[ke]]) + bant + alt,
              dict(kaydir_gercek=0.03, kaydir_sahte=0.03)))
    s.append(("önsayım, uyuşmazlık: gerçek +0,02 (sahte değil)", list(kum) + bant + alt, dict(kaydir_gercek=0.02)))
    s.append(("kapı altı aday yok (yalnız 28 küme)", list(kum), {}))
    s.append(("kapı altı adaylar 3 kat (18 bant, 75 alt)", list(kum) + bant * 3 + alt * 3, {}))
    return s


def secim(yol_i, yol_ii, n, tohum, cikti):
    Y.tohum_denetle_c(tohum, False)
    kays = {"i": Kayitlar(yol_i), "ii": Kayitlar(yol_ii)}
    rng = np.random.default_rng(tohum)
    out = dict(tekrar=n, tohum=tohum, tasarimlar=["v1", "a1", "a2", "b"], alfa=[], guc=[], kapi_onsayim={})
    kum, bant, alt = onsayim()
    out["kapi_onsayim"] = dict(K_31=int(sum(x >= KAPI for x in kum)), K_40=int(sum(x >= KAPI_A1 for x in kum)),
                               N0_lt_40=[round(x, 1) for x in kum if x < KAPI_A1])
    for ad, lam, kw in senaryolar():
        for dunya in ("i", "ii"):
            sat = dict(senaryo=ad, dunya=dunya)
            for t in out["tasarimlar"]:
                sat[t] = benzetim(kays[dunya], lam, t, n, rng, **kw)
            out["alfa"].append(sat)
            print(ad, dunya, {t: (sat[t]["oran"], sat[t]["K_ort"]) for t in out["tasarimlar"]}, flush=True)
    ss = senaryolar()
    for ad, lam, kw in [ss[0], ss[1], ss[6], ss[7]]:
        for dunya in ("i", "ii"):
            sat = dict(senaryo=ad, dunya=dunya)
            for t in out["tasarimlar"]:
                sat[t] = benzetim(kays[dunya], lam, t, n, rng, h1=True, **kw)
            out["guc"].append(sat)
            print("güç", ad, dunya, {t: (sat[t]["oran"], sat[t]["K_ort"]) for t in out["tasarimlar"]}, flush=True)
    with open(cikti, "w", encoding="utf-8") as f:
        f.write(KO.json_metni(out))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "kayit":
        kayit(a[1], int(a[2]), int(a[3]), a[4])
    elif a[0] == "secim":
        secim(a[1], a[2], int(a[3]), int(a[4]), a[5])
    else:
        raise SystemExit(__doc__)
