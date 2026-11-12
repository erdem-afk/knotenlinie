"""TR-6 (b) Marmara çözünürlük sayımı: Mc, kümesizleştirilmiş arka plan oranı, %80 güçle algılanabilir en küçük
gerilme hızı değişimi ve gerilme adımı (Dieterich 1994 hız-durum sismisite modeli, Poisson sayım istatistiği).

Girdi: tr6_indir_koeri.py çıktıları (koeri_YYYY.txt, 2006..2025). KÖR KURAL: zaman >= 2026-01-01 olan her satır
okunurken sayılmadan atılır; atılan satır sayısı yazdırılmaz. Hüküm satırı yoktur; bu bir güç sayımıdır.

Kullanım: python3 -I -B tr6_sayim.py <ham_dizin> <cikti.json>
"""
import glob, json, math, os, sys
import numpy as np

KOR = np.datetime64("2026-01-01T00:00:00")

# Segment kutuları (enlem_min, enlem_max, boylam_min, boylam_max). Kaba, önceden beyan; fay izine göre değil kutuya göre.
SEGMENT = {
    "Ganos":         (40.45, 40.90, 26.50, 27.35),
    "Orta Marmara":  (40.70, 41.00, 27.35, 28.60),
    "Prens Adaları": (40.78, 40.98, 28.60, 29.10),
    "Çınarcık":      (40.50, 40.78, 28.60, 29.35),
    "İzmit":         (40.62, 40.85, 29.35, 30.10),
    # En iyi durum satırı: beş kutunun zarfı. Tek bir gerilme hızı değişiminin bütün kuşağa eşit düştüğünü varsayar.
    "Kuşak (zarf)":  (40.45, 41.00, 26.50, 30.10),
}
DONEMLER = {"2006-2025": (2006, 2025), "2011-2025": (2011, 2025), "2016-2025": (2016, 2025)}
# Mc kuralı: "max" = dönemdeki yıllık Mc'lerin en büyüğü (tutucu, ana satır); "medyan" = yıllık Mc medyanı
# (duyarlılık; eksik yıllarda oranı düşük gösterir ve aşırı saçılımı büyütür).
MC_KURAL = ("max", "medyan")
ASIGMA_KPA = [10.0, 20.0, 30.0, 50.0]          # Aσ = 0,01-0,05 MPa
TAUDOT0 = [1.0, 5.0, 10.0]                      # arka plan gerilme hızı, kPa/yıl (beyan, ölçülmedi)
ZA, ZB = 1.6449, 0.8416                         # tek yanlı alfa 0,05; güç 0,80


# ---------------------------------------------------------------- okuma
def oku(dizin):
    t, la, lo, de, m = [], [], [], [], []
    for yol in sorted(glob.glob(os.path.join(dizin, "koeri_*.txt"))):
        for s in open(yol, encoding="utf-8"):
            a = s.rstrip("\n").split("\t")
            if len(a) < 8:
                continue
            zaman = np.datetime64(a[2].replace(".", "-") + "T" + a[3][:8])
            if zaman >= KOR:          # kör veri: sayılmadan at
                continue
            t.append(zaman); la.append(float(a[4])); lo.append(float(a[5])); de.append(float(a[6]))
            m.append(float(a[7]))
    t = np.array(t, dtype="datetime64[s]")
    o = np.argsort(t)
    return dict(t=t[o], lat=np.array(la)[o], lon=np.array(lo)[o], dep=np.array(de)[o], m=np.array(m)[o])


def yil(t):
    return t.astype("datetime64[Y]").astype(int) + 1970


def ondalik_yil(t):
    s = (t - np.datetime64("1970-01-01T00:00:00")).astype("timedelta64[s]").astype(float)
    return 1970.0 + s / (365.2425 * 86400)


# ---------------------------------------------------------------- Mc
def mc_maxc(m):
    if len(m) < 20:
        return float("nan")
    b = np.round(m, 1)
    v, c = np.unique(b, return_counts=True)
    return float(v[np.argmax(c)])


def b_aki(m, mc, dm=0.1):
    x = m[m >= mc - 1e-9]
    if len(x) < 20:
        return float("nan")
    return math.log10(math.e) / (x.mean() - (mc - dm / 2))


def mc_gft(m, esik=90.0, dm=0.1):
    """Wiemer & Wyss 2000 iyilik-uyum: R >= esik veren en küçük Mc. Yoksa nan."""
    b = np.round(m, 1)
    for mc in np.arange(np.round(b.min(), 1), np.round(b.max(), 1) - 1.0, dm):
        x = b[b >= mc - 1e-9]
        if len(x) < 30:
            break
        bv = b_aki(x, mc)
        a = math.log10(len(x)) + bv * mc
        kenar = np.arange(mc, x.max() + dm / 2, dm)
        gozl = np.array([np.sum(x >= k - 1e-9) for k in kenar], dtype=float)
        mod = 10 ** (a - bv * kenar)
        r = 100 - 100 * np.sum(np.abs(gozl - mod)) / np.sum(gozl)
        if r >= esik:
            return float(round(mc, 1))
    return float("nan")


def mc_birlesik(m):
    a = mc_maxc(m) + 0.2
    g = mc_gft(m, 90.0)
    return float(round(max(a, g) if not math.isnan(g) else a, 1)), dict(maxc_02=a, gft90=g, gft95=mc_gft(m, 95.0))


# ---------------------------------------------------------------- kümesizleştirme
def pencere(M, tur):
    if tur == "GK74":
        d = 10 ** (0.1238 * M + 0.983)
        g = 10 ** (0.032 * M + 2.7389) if M >= 6.5 else 10 ** (0.5409 * M - 0.547)
    else:  # Uhrhammer 1986
        d = math.exp(-1.024 + 0.804 * M)
        g = math.exp(-2.87 + 1.235 * M)
    return d, g


def kumesizlestir(k, tur):
    """Pencere yöntemi: büyükten küçüğe her ana şokun penceresindeki (önce ve sonra) küçük olaylar bağımlı."""
    n = len(k["m"])
    td = ondalik_yil(k["t"]) * 365.2425
    bagimli = np.zeros(n, bool)
    lat, lon = np.radians(k["lat"]), np.radians(k["lon"])
    for i in np.argsort(-k["m"], kind="stable"):
        if bagimli[i]:
            continue
        d, g = pencere(k["m"][i], tur)
        j = np.where((np.abs(td - td[i]) <= g) & (k["m"] <= k["m"][i]))[0]
        j = j[j != i]
        if len(j) == 0:
            continue
        x = np.sin(lat[i]) * np.sin(lat[j]) + np.cos(lat[i]) * np.cos(lat[j]) * np.cos(lon[j] - lon[i])
        r = 6371.0 * np.arccos(np.clip(x, -1, 1))
        bagimli[j[r <= d]] = True
    return ~bagimli


# ---------------------------------------------------------------- Dieterich 1994 ileri model
def n_hiz(r, T, q, ta1):
    """Gerilme hızı tau0 -> q*tau0 değişiminden sonra [0,T]'de beklenen olay sayısı. ta1 = Aσ/(q tau0)."""
    x = T / ta1
    if x > 50:
        lg = x + math.log1p((q - 1) * math.exp(-x))
    else:
        lg = math.log(math.exp(x) + q - 1)
    return r * q * ta1 * (lg - math.log(q))


def n_adim(r, T, dtau, asig, tau0):
    """Gerilme adımı dtau (kPa) sonrası [0,T]'de beklenen olay sayısı; ta = Aσ/tau0."""
    ta = asig / tau0
    lc1 = -dtau / asig                   # log(1 + c)
    c1 = math.exp(lc1)
    x = T / ta
    if x > 50:
        lg = x + math.log1p((c1 - 1) * math.exp(-x))
    else:
        lg = math.log(math.exp(x) + c1 - 1)
    return r * ta * (lg - lc1)


def gerekli_fark(N0, N1, phi, T, Tb):
    """Algılama için gereken |N1-N0| (normal yaklaşım; taban oranı Tb yılda kestirildi; aşırı saçılım phi)."""
    s0 = math.sqrt(phi * N0 * (1 + T / Tb))
    s1 = math.sqrt(phi * (N1 + N0 * T / Tb))
    return ZA * s0 + ZB * s1


def kok(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        c = 0.5 * (a + b)
        fc = f(c)
        if (fc > 0) == (fa > 0):
            a, fa = c, fc
        else:
            b = c
    return 0.5 * (a + b)


def mde_hiz(r, asig, tau0, T, Tb, phi, yon=+1):
    """%80 güçle algılanabilir en küçük gerilme hızı değişimi (kPa/yıl). yon=-1 düşüş."""
    N0 = r * T
    def f(dd):
        q = 1 + yon * dd / tau0
        N1 = n_hiz(r, T, q, asig / (q * tau0))
        return abs(N1 - N0) - gerekli_fark(N0, N1, phi, T, Tb)
    ust = 1e6 if yon > 0 else tau0 * (1 - 1e-9)
    if f(ust) < 0:
        return float("inf")
    return kok(f, 1e-9, ust)


def mde_adim(r, asig, tau0, T, Tb, phi, yon=+1):
    N0 = r * T
    def f(dt):
        N1 = n_adim(r, T, yon * dt, asig, tau0)
        return abs(N1 - N0) - gerekli_fark(N0, N1, phi, T, Tb)
    ust = 30 * asig
    if f(ust) < 0:
        return float("inf")
    return kok(f, 1e-9, ust)


def mde_kisa_zaman(r, asig, T, Tb, phi):
    """T << ta sınırı: N1-N0 ≈ r T^2 Δτ̇ / (2 Aσ). Açık formül (N1≈N0 alınarak)."""
    N0 = r * T
    d = (ZA + ZB) * math.sqrt(phi * N0 * (1 + T / Tb))
    return 2 * asig * d / (r * T * T)


def mde_poisson_kesin(N0, alfa=0.05, guc=0.8):
    """phi=1, taban biliniyor: kesin Poisson. Kritik c: P(X>=c|N0)<=alfa. Gerekli N1: P(X>=c|N1)>=guc."""
    from math import exp, lgamma, log
    def kuyruk(mu, c):
        if c <= 0:
            return 1.0
        s, terim = 0.0, exp(-mu)
        for k in range(c):
            s += terim
            terim *= mu / (k + 1)
        return 1 - s
    c = 0
    while kuyruk(N0, c) > alfa:
        c += 1
    lo, hi = N0, N0 * 10 + 50
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if kuyruk(mid, c) >= guc:
            hi = mid
        else:
            lo = mid
    return c, hi


# ---------------------------------------------------------------- ana
def main():
    dizin, cikti = sys.argv[1], sys.argv[2]
    k = oku(dizin)
    Y = yil(k["t"])
    sonuc = dict(kaynak="KOERI zeqdb, 40,20-41,30 K, 26,30-30,30 D, 2006-2025 (2026 satırları okurken atıldı)",
                 toplam_olay=int(len(k["m"])), segment_kutu=SEGMENT, yillik_mc={}, donemler={})
    for y in range(2006, 2026):
        mm = k["m"][Y == y]
        mc, ayr = mc_birlesik(mm)
        sonuc["yillik_mc"][y] = dict(n=int(len(mm)), mc=mc, **{a: (None if math.isnan(b) else b) for a, b in ayr.items()},
                                     m_min=float(mm.min()))
    print("Yıllık Mc (kutu):", {y: v["mc"] for y, v in sonuc["yillik_mc"].items()})

    for (dad0, (y0, y1)), kural in [(d, k_) for d in DONEMLER.items() for k_ in MC_KURAL]:
        dad = f"{dad0} | Mc {kural}"
        sec = (Y >= y0) & (Y <= y1)
        Tb = y1 - y0 + 1
        ymc = [sonuc["yillik_mc"][y]["mc"] for y in range(y0, y1 + 1)]
        mc_don = float(max(ymc)) if kural == "max" else float(np.round(np.median(ymc), 1))
        kd = {a: v[sec] for a, v in k.items()}
        ust = kd["m"] >= mc_don - 1e-9
        ku = {a: v[ust] for a, v in kd.items()}
        bv = b_aki(ku["m"], mc_don)
        don = dict(Tb_yil=Tb, mc_kutu=mc_don, b_kutu=round(bv, 3), n_kutu_mc_ustu=int(ust.sum()), segment={})
        maske = {tur: kumesizlestir(ku, tur) for tur in ("GK74", "Uhrhammer86")}
        don["arka_plan_payi_kutu"] = {tur: round(float(v.mean()), 3) for tur, v in maske.items()}
        Yu = yil(ku["t"])
        saat = (ku["t"].astype("datetime64[h]").astype(int)) % 24
        for sad, (a0, a1, b0, b1) in SEGMENT.items():
            sm = (ku["lat"] >= a0) & (ku["lat"] < a1) & (ku["lon"] >= b0) & (ku["lon"] < b1)
            small = (kd["lat"] >= a0) & (kd["lat"] < a1) & (kd["lon"] >= b0) & (kd["lon"] < b1)
            mc_seg, mc_ayr = mc_birlesik(kd["m"][small]) if small.sum() >= 50 else (float("nan"), {})
            sd = dict(n_ham_hepsi=int(small.sum()), mc_segment_havuz=mc_seg, mc_kullanilan=mc_don,
                      n_ham_mc_ustu=int(sm.sum()), ham_oran_yil=round(sm.sum() / Tb, 2))
            for tur, bag in maske.items():
                s = sm & bag
                yc = np.array([np.sum(s & (Yu == y)) for y in range(y0, y1 + 1)], float)
                r = float(yc.mean())
                phi = float(yc.var(ddof=1) / r) if r > 0 else float("nan")
                gun = float(np.mean((saat[s] >= 5) & (saat[s] < 15))) if s.sum() else float("nan")
                ent = dict(n=int(s.sum()), r_yil=round(r, 2), yillik=[int(v) for v in yc], phi=round(phi, 2),
                           gunduz_payi_05_15UTC=round(gun, 3), mde={})
                for phi_k, phi_v in (("phi1", 1.0), ("phi_olculen", max(1.0, phi))):
                    tab = {}
                    for asg in ASIGMA_KPA:
                        row = dict(kisa_zaman_hiz=round(mde_kisa_zaman(r, asg, 1.0, Tb, phi_v), 2))
                        for t0 in TAUDOT0:
                            row[f"hiz_artis_tau0_{t0:g}"] = round(mde_hiz(r, asg, t0, 1.0, Tb, phi_v, +1), 2)
                            row[f"hiz_dusus_tau0_{t0:g}"] = round(mde_hiz(r, asg, t0, 1.0, Tb, phi_v, -1), 2)
                            row[f"adim_artis_1yil_tau0_{t0:g}"] = round(mde_adim(r, asg, t0, 1.0, Tb, phi_v, +1), 2)
                            row[f"adim_artis_3ay_tau0_{t0:g}"] = round(mde_adim(r, asg, t0, 0.25, Tb, phi_v, +1), 2)
                            row[f"adim_dusus_1yil_tau0_{t0:g}"] = round(mde_adim(r, asg, t0, 1.0, Tb, phi_v, -1), 2)
                        tab[f"Asigma_{asg:g}kPa"] = row
                    ent["mde"][phi_k] = tab
                c, n1 = mde_poisson_kesin(r) if r > 0 else (None, None)
                ent["kesin_poisson_1yil"] = dict(kritik_sayi=c, gerekli_N1=round(n1, 2) if n1 else None,
                                                 gerekli_kat=round(n1 / r, 3) if r > 0 else None)
                sd[tur] = ent
            don["segment"][sad] = sd
        sonuc["donemler"][dad] = don
    json.dump(sonuc, open(cikti, "w"), indent=1, ensure_ascii=False)

    # kısa tablo
    for dad, don in sonuc["donemler"].items():
        print(f"\n== {dad}  Mc(kutu)={don['mc_kutu']}  b={don['b_kutu']}  arka plan payı={don['arka_plan_payi_kutu']}")
        for sad, sd in don["segment"].items():
            g = sd["GK74"]; u = sd["Uhrhammer86"]
            m1 = g["mde"]["phi_olculen"]
            print(f"  {sad:14s} Mc_seg={sd['mc_segment_havuz']}  ham/yıl={sd['ham_oran_yil']:6.1f}  "
                  f"GK r={g['r_yil']:6.2f} φ={g['phi']:5.2f}  Uh r={u['r_yil']:6.2f} φ={u['phi']:5.2f}  "
                  f"MDE hız (kPa/yıl, GK, φ, Aσ10/50, τ̇0=5): {m1['Asigma_10kPa']['hiz_artis_tau0_5']} / "
                  f"{m1['Asigma_50kPa']['hiz_artis_tau0_5']}  adım1y: {m1['Asigma_10kPa']['adim_artis_1yil_tau0_5']} / "
                  f"{m1['Asigma_50kPa']['adim_artis_1yil_tau0_5']}")


if __name__ == "__main__":
    main()
