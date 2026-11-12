"""TR-6a ön kaydının bütün sayıları (yalnız olay öncesi üstveri; hiçbir olay sonrası sorgu, ağ erişimi yok).

Girdi : tr6_a_sayim.json (155 olaylık havuz), tr6_a_kapi.json (Ek 1 kapı sayımı).
Çıktı : tr6a_olay_listesi.json  -> dondurulan aday listesi (sha256 ön kayıtta yazılır)
        tr6a_onkayit_sayilar.json -> ön kayıt metnindeki bütün sayılar (binom tabloları, testere dişi çözümü,
                                     tarih kuralının etkisi, H0 altında oy olasılığı, yapay Dieterich sınaması)
Kullanım: python3 -I -B tr6a_onkayit_sayilar.py            (≈ 5 sn; numpy + standart kitaplık)
          python3 -I -B tr6a_onkayit_sayilar.py --md       (ayrıca ön kayıttaki tabloları Markdown olarak basar)

Bu betik hiçbir oran değişimi hesaplamaz; yapay Dieterich bölümü yalnız uydurma Poisson sayılarıyla çalışır.
"""
import datetime as dt, hashlib, json, math, os, sys
import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6_a_kapi as KAPI   # noqa: E402  (kumele, gereken_n0, binom_ust; yan etkisi yok)

# ------------------------------------------------------------------ ön kayıt sabitleri (metinle aynı)
ASIGMA, ASIGMA_DUY = 19.0, (13.0, 39.0)
DTAU_ESIK = 10.0                       # kPa; lob eşiği ve kapı adımı
VERI_SONU = dt.datetime(2025, 12, 31, 23, 59, 59)
ISC_GOZDEN = dt.datetime(2023, 12, 31, 23, 59, 59)   # duyarlılık D6: gözden geçirilmiş bülten varsayılan sınırı
ON_G0, ON_G1 = 1826, 30                # ön pencere [t-1826 g, t-30 g)
SON_G0, SON_G1 = 30, 365               # son pencere [t+30 g, t+365 g)
T_ON_G, T_SON_G = ON_G0 - ON_G1, SON_G1 - SON_G0   # 1796 g, 335 g
NK_G0, NK_G1 = 365, 30                 # negatif kontrol "son" penceresi [t-365, t-30); "ön" [t-1826, t-365)
T_NK_ON_G, T_NK_SON_G = ON_G0 - NK_G0, NK_G0 - NK_G1   # 1461 g, 335 g
P1, ALFA, GUC = 0.75, 0.05, 0.80
GRUP_G, GRUP_KM = 30, 300.0            # çift/öncü grubu: 30 gün, 300 km (zincir)
K_ALT, K_KALICI = 23, 28
TOHUM = 20261112


def sha256_dosya(yol):
    return hashlib.sha256(open(yol, "rb").read()).hexdigest()


# ------------------------------------------------------------------ 1. dondurulan aday listesi
def aday_listesi():
    havuz = json.load(open(os.path.join(BURAYA, "tr6_a_sayim.json")))["olaylar"]
    kapi = json.load(open(os.path.join(BURAYA, "tr6_a_kapi.json")))
    ek1 = {o["id"]: o for o in kapi["olaylar"]}
    assert len(havuz) == 155 and set(ek1) == {o["id"] for o in havuz}
    kume_no = {}
    for a in ("13", "19", "39"):
        for i, c in enumerate(kapi["kapilar"]["en_iyi_acik (<=40 km)"][a]["kumeler"]):
            for x in c:
                kume_no.setdefault(x, {})[a] = i
    liste = []
    for o in sorted(havuz, key=lambda x: x["zaman"]):
        e = ek1[o["id"]]
        t = dt.datetime.fromisoformat(o["zaman"])
        son_bitis = t + dt.timedelta(days=SON_G1)
        kat = {k: dict(mc=v["mc"], N0_halka=v["N0"], tur=v["tur"]) for k, v in sorted(e["kataloglar"].items())
               if v.get("mc") is not None}
        tarih_ok = son_bitis <= VERI_SONU
        en = e["en_iyi"]
        liste.append(dict(
            id=o["id"], zaman=o["zaman"], M=o["M"], enlem=o["enlem"], boylam=o["boylam"], L_km=o["L_km"],
            halka_km=o["halka_km"],
            son_pencere_bitis=son_bitis.isoformat(timespec="seconds"),
            tarih_kurali_gecer=tarih_ok,
            isc_gozden_gecmis_son_pencere=son_bitis <= ISC_GOZDEN,
            ek1_kataloglar=kat,
            ek1_en_iyi=None if en is None else dict(katalog=en["katalog"], mc=en["mc"], N0=en["N0"], tur=en["tur"]),
            ek1_kume_19=kume_no.get(o["id"], {}).get("19"),
            mekanizma_sinif=e.get("mekanizma", {}).get("sinif", "bilinmiyor"),
            mekanizma_rake=e.get("mekanizma", {}).get("rake"),
            mekanizma_dip=e.get("mekanizma", {}).get("dip"),
            kosu_adayi=bool(tarih_ok and kat),
        ))
    # olay grubu (ön kayıt §3.5): havuzdan 30 gün ve 300 km içindeki olaylar zincirle tek grup; t0 en erken üye
    def km(a, b):
        return float(KAPI.uzaklik_km(a["enlem"], a["boylam"], np.array([b["enlem"]]), np.array([b["boylam"]]))[0])
    grup = {x["id"]: x["id"] for x in liste}
    for i, a in enumerate(liste):
        for b in liste[i + 1:]:
            dtg = (dt.datetime.fromisoformat(b["zaman"]) - dt.datetime.fromisoformat(a["zaman"])).total_seconds() / 86400
            if dtg <= GRUP_G and km(a, b) <= GRUP_KM:
                eski, yeni = grup[b["id"]], grup[a["id"]]
                for k in grup:
                    if grup[k] == eski:
                        grup[k] = yeni
    for x in liste:
        x["grup"] = grup[x["id"]]
        x["grup_uyeleri"] = [y["id"] for y in liste if grup[y["id"]] == grup[x["id"]]]
    return liste, kapi


def tarih_kurali_etkisi(liste, kapi):
    esik = {a: KAPI.gereken_n0(math.exp(-DTAU_ESIK / a)) for a in (13.0, 19.0, 39.0)}
    ek1 = {o["id"]: o for o in kapi["olaylar"]}
    out = dict(havuz=len(liste),
               tarih_disi=[x["id"] for x in liste if not x["tarih_kurali_gecer"]],
               katalogsuz=sum(1 for x in liste if not x["ek1_kataloglar"]),
               katalogsuz_ve_tarih_disi=sum(1 for x in liste if not x["ek1_kataloglar"] and not x["tarih_kurali_gecer"]),
               katalogu_olan=sum(1 for x in liste if x["ek1_kataloglar"]),
               kosu_adayi=sum(1 for x in liste if x["kosu_adayi"]),
               kosu_adayi_isc_gozden=sum(1 for x in liste if x["kosu_adayi"] and x["isc_gozden_gecmis_son_pencere"]),
               cok_uyeli_gruplar=sorted({tuple(x["grup_uyeleri"]) for x in liste if len(x["grup_uyeleri"]) > 1}),
               ek1_kaba_kapi={})
    for a, e in esik.items():
        sec_once = [ek1[x["id"]] for x in liste if (x["ek1_en_iyi"] or {}).get("N0", 0) >= e]
        sec_sonra = [s for s in sec_once if next(y for y in liste if y["id"] == s["id"])["tarih_kurali_gecer"]]
        out["ek1_kaba_kapi"][f"{a:g}"] = dict(
            esik_N0=round(e, 2), olay_once=len(sec_once), kume_once=len(KAPI.kumele(sec_once)),
            olay_sonra=len(sec_sonra), kume_sonra=len(KAPI.kumele(sec_sonra)),
            dusen=[s["id"] for s in sec_once if s not in sec_sonra])
    # ComCat Mc < 1,0 olup Ek 1'de en iyi seçilen ABD dışı satırlar (büyüklük sıfır şüphesi)
    out["supheli_dusuk_mc"] = [dict(id=x["id"], katalog=x["ek1_en_iyi"]["katalog"], mc=x["ek1_en_iyi"]["mc"])
                               for x in liste if x["ek1_en_iyi"] and x["ek1_en_iyi"]["mc"] < 0.3]
    return out


# ------------------------------------------------------------------ 2. binom tabloları
def binom_alt(k, n, p):
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1)))


def esikler(K):
    c = next(c for c in range(K + 2) if KAPI.binom_ust(c, K, 0.5) <= ALFA)          # H1: X >= c
    h = max([h for h in range(-1, K + 1) if h < 0 or binom_alt(h, K, P1) <= ALFA])     # H0: X <= h
    t = max([t for t in range(-1, K + 1) if t < 0 or binom_alt(t, K, 0.5) <= ALFA])  # ters yön: X <= t
    return c, h, t


def binom_tablosu(Ks=range(15, 61)):
    tab = []
    for K in Ks:
        c, h, t = esikler(K)
        sat = dict(K=K, kritik_H1=c, alfa_gercek=round(KAPI.binom_ust(c, K, 0.5), 4),
                   guc_p075=round(KAPI.binom_ust(c, K, P1), 4), esik_H0=h,
                   P_H0_p075=round(binom_alt(h, K, P1), 4) if h >= 0 else 0.0,
                   esik_ters=t, P_ters_p05=round(binom_alt(t, K, 0.5), 4) if t >= 0 else 0.0)
        sat["hukum_olasiliklari"] = {
            f"{p:.2f}": dict(H1=round(KAPI.binom_ust(c, K, p), 3),
                             H0=round(binom_alt(h, K, p), 3) if h >= 0 else 0.0,
                             ayirt=round(1 - KAPI.binom_ust(c, K, p) - (binom_alt(h, K, p) if h >= 0 else 0), 3),
                             ters=round(binom_alt(t, K, p), 3) if t >= 0 else 0.0)
            for p in (0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80)}
        tab.append(sat)
    return tab


def testere_disi(tab):
    g = {r["K"]: r["guc_p075"] for r in tab}
    kalici = next(K for K in sorted(g) if K >= K_ALT and all(g[k] >= GUC for k in range(K, max(g) + 1)))
    # tablo 60'ta biter; 61..200 için ayrıca denetle
    for K in range(61, 201):
        c = next(c for c in range(K + 2) if KAPI.binom_ust(c, K, 0.5) <= ALFA)
        assert KAPI.binom_ust(c, K, P1) >= GUC, K
    eslem = {}
    for K in range(K_ALT, kalici):
        hedef = max(k for k in range(K_ALT, K + 1) if g[k] >= GUC)
        eslem[K] = dict(hedef_K=hedef, atilan_kume=K - hedef, guc_once=g[K], guc_sonra=g[hedef])
    return dict(kalici_K=kalici, eslem=eslem, guc_23_30={k: g[k] for k in range(23, 31)})


# ------------------------------------------------------------------ 3. oy olasılığı: H0 ve yapay Dieterich
def poisson_cdf_tablo(lam, nmax):
    k = np.arange(nmax + 1)
    lp = -lam + k * math.log(lam) - np.array([math.lgamma(i + 1) for i in k]) if lam > 0 else None
    if lam == 0:
        p = np.zeros(nmax + 1); p[0] = 1.0
    else:
        p = np.exp(lp)
    return p, np.cumsum(p)


def oy_olasiligi_saf(lam_on, lam_son, T_on=T_ON_G, T_son=T_SON_G, yon=-1):
    """REDDEDİLEN saf oy (bilgi): yon=-1: P(n_son*T_on < n_on*T_son); yon=+1: P(n_son*T_on > n_on*T_son).
    Poisson çarpıklığı yüzünden H0 altında düşüş oyu 0,5'in üstüne çıkar (ön kayıt §4.3)."""
    nmax = int(max(lam_on, lam_son) * 3 + 60)
    p_on, _ = poisson_cdf_tablo(lam_on, nmax)
    p_son, F_son = poisson_cdf_tablo(lam_son, nmax * 3)
    top = 0.0
    for a in range(nmax + 1):
        if yon < 0:
            bmax = -(-a * T_son // T_on) - 1
            top += p_on[a] * (F_son[min(bmax, len(F_son) - 1)] if bmax >= 0 else 0.0)
        else:
            bmin = a * T_son // T_on + 1
            top += p_on[a] * (1 - (F_son[bmin - 1] if bmin >= 1 else 0.0))
    return float(top)


def binom_cdf_vec(n, pi):
    k = np.arange(n + 1)
    lg = np.array([math.lgamma(i + 1) for i in range(n + 1)])
    lp = math.lgamma(n + 1) - lg - lg[::-1] + k * math.log(pi) + (n - k) * math.log1p(-pi)
    return np.cumsum(np.exp(lp))


def oy_esikleri(nmax, T_on=T_ON_G, T_son=T_SON_G):
    """Koşullu binom oyu (ön kayıt §4.3). n = n_on + n_son, π = T_son/(T_on + T_son).
    Düşüş oyu: F(n_son; n, π) <= 0,5  <=>  n_son <= b_dus[n].   Artış oyu: 1 - F(n_son - 1; n, π) <= 0,5
    <=>  n_son >= b_art[n]. n = 0'da iki oy da 0. H0 altında her n için P(oy) <= 0,5 (tanım gereği)."""
    pi = T_son / (T_on + T_son)
    b_dus = np.full(nmax + 1, -1)
    b_art = np.full(nmax + 1, 10 ** 9)
    for n in range(1, nmax + 1):
        F = binom_cdf_vec(n, pi)
        ok = np.nonzero(F <= 0.5 + 1e-12)[0]
        b_dus[n] = ok.max() if len(ok) else -1
        ust = 1 - np.concatenate([[0.0], F[:-1]])          # P(X >= b)
        ok2 = np.nonzero(ust <= 0.5 + 1e-12)[0]
        b_art[n] = ok2.min() if len(ok2) else 10 ** 9
    return b_dus, b_art


_ESIK_ONBELLEK = {}


def oy_olasiligi(lam_on, lam_son, T_on=T_ON_G, T_son=T_SON_G, yon=-1):
    """Koşullu binom oyunun kesin olasılığı; n_on ~ Poisson(lam_on), n_son ~ Poisson(lam_son) bağımsız."""
    na = int(lam_on + 8 * math.sqrt(lam_on + 1) + 20)
    nb = int(lam_son + 8 * math.sqrt(lam_son + 1) + 20)
    anahtar = (na + nb, T_on, T_son)
    if anahtar not in _ESIK_ONBELLEK:
        _ESIK_ONBELLEK[anahtar] = oy_esikleri(na + nb, T_on, T_son)
    b_dus, b_art = _ESIK_ONBELLEK[anahtar]
    p_on, _ = poisson_cdf_tablo(lam_on, na)
    p_son, _ = poisson_cdf_tablo(lam_son, nb)
    A, B = np.meshgrid(np.arange(na + 1), np.arange(nb + 1), indexing="ij")
    N = A + B
    oy = (B <= b_dus[N]) if yon < 0 else (B >= b_art[N])
    oy &= N > 0
    return float((np.outer(p_on, p_son) * oy).sum())


def dieterich_N(r, t1, t2, dtau, asig, ta):
    """Dieterich (1994) gerilme adımı: [t1, t2] yıl aralığında beklenen sayı; r yıllık arka plan oranı."""
    q = math.exp(-dtau / asig)
    if math.isinf(ta):
        return r * (t2 - t1) / q
    f = lambda t: ta * math.log(math.exp(t / ta) + q - 1)
    return r * (f(t2) - f(t1))


def yapay_dieterich():
    rng = np.random.default_rng(TOHUM)
    T_on, t1, t2 = T_ON_G / 365.25, SON_G0 / 365.25, SON_G1 / 365.25
    out = dict(H0={}, golge={}, pozitif={}, olcer={}, gerekli_dogru_lob_payi={})
    for N0 in (17.08, 31.36, 50.0, 111.2, 300.0):
        lam_on = N0 * T_on
        lam_son = N0 * (t2 - t1)
        lam_nk_on, lam_nk_son = N0 * T_NK_ON_G / 365.25, N0 * T_NK_SON_G / 365.25
        out["H0"][f"{N0:g}"] = dict(
            dusus_oyu=round(oy_olasiligi(lam_on, lam_son, yon=-1), 4),
            artis_oyu=round(oy_olasiligi(lam_on, lam_son, yon=+1), 4),
            negatif_kontrol_dusus_oyu=round(oy_olasiligi(lam_nk_on, lam_nk_son, T_NK_ON_G, T_NK_SON_G, -1), 4),
            reddedilen_saf_dusus_oyu=round(oy_olasiligi_saf(lam_on, lam_son, yon=-1), 4))
    for tdot in (2.0, 10.0, 50.0, 0.0):             # kPa/yıl; 0 -> t_a sonsuz (kalıcı adım)
        ta = math.inf if tdot == 0 else ASIGMA / tdot
        anahtar = "kalici" if tdot == 0 else f"tau0_{tdot:g}_kPa_yil (t_a {ta:.2f} y)"
        out["golge"][anahtar], out["pozitif"][anahtar], out["olcer"][anahtar] = {}, {}, {}
        for N0 in (31.36, 50.0, 111.2):
            lam_on = N0 * T_on
            for dtau, kap in ((-DTAU_ESIK, "golge"), (+DTAU_ESIK, "pozitif")):
                lam_son = dieterich_N(N0, t1, t2, dtau, ASIGMA, ta)
                p = oy_olasiligi(lam_on, lam_son, yon=-1 if dtau < 0 else +1)
                out[kap][anahtar][f"{N0:g}"] = round(p, 4)
            # ölçer: Δτ_est = Aσ ln((n_son/T_son)/(n_on/T_on)); yapay Poisson, 20 000 deneme
            lam_son = dieterich_N(N0, t1, t2, -DTAU_ESIK, ASIGMA, ta)
            n_on = rng.poisson(lam_on, 20000)
            n_son = rng.poisson(lam_son, 20000)
            with np.errstate(divide="ignore"):
                est = ASIGMA * np.log((n_son / (t2 - t1)) / (n_on / T_on))
            beklenen = ASIGMA * math.log(lam_son / (t2 - t1) / N0)
            out["olcer"][anahtar][f"{N0:g}"] = dict(
                beklenen_dtau_est=round(beklenen, 2), medyan=round(float(np.median(est)), 2),
                q10=round(float(np.quantile(est, 0.10)), 2), q90=round(float(np.quantile(est, 0.90)), 2))
    # kesin hesabın Monte Carlo denetimi (H0 ve kalıcı adım, N0 = 31,36; 200 000 deneme)
    b_dus, b_art = oy_esikleri(2000)
    for anahtar, lam_s in (("H0", 31.36 * (t2 - t1)), ("kalici_golge", dieterich_N(31.36, t1, t2, -DTAU_ESIK, ASIGMA, math.inf))):
        a = rng.poisson(31.36 * T_on, 200000)
        b = rng.poisson(lam_s, 200000)
        n = a + b
        out.setdefault("monte_carlo_denetim", {})[anahtar] = dict(
            mc=round(float(((b <= b_dus[n]) & (n > 0)).mean()), 4))
    # p1 = 0,75 için gereken "doğru lob" payı f: f*p_D + (1-f)*p_0 = 0,75 (N0 = 31,36)
    p0 = out["H0"]["31.36"]["dusus_oyu"]
    for anahtar, d in out["golge"].items():
        pD = d["31.36"]
        out["gerekli_dogru_lob_payi"][anahtar] = round((P1 - p0) / (pD - p0), 3) if pD > p0 else None
    return out


def gercek_alfa(tab, p0):
    return {r["K"]: round(KAPI.binom_ust(r["kritik_H1"], r["K"], p0), 4) for r in tab if r["K"] in (23, 26, 28, 30, 35, 39)}


def main():
    liste, kapi = aday_listesi()
    yol_liste = os.path.join(BURAYA, "tr6a_olay_listesi.json")
    with open(yol_liste, "w", encoding="utf-8") as f:
        json.dump(dict(aciklama="TR-6a dondurulan aday listesi: ComCat finite-fault havuzu (155), Ek 1 katalog ve Mc "
                                "değerleri, tarih kuralı (t + 365 g <= 2025-12-31) ve koşu adaylığı. Olay sonrası bilgi "
                                "içermez.", uretici="tr6a_onkayit_sayilar.py",
                       girdi_sha256={k: sha256_dosya(os.path.join(BURAYA, k))
                                     for k in ("tr6_a_sayim.json", "tr6_a_kapi.json")},
                       olaylar=liste), f, indent=1, ensure_ascii=False)
        f.write("\n")
    tab = binom_tablosu()
    yd = yapay_dieterich()
    sayi = dict(
        olay_listesi_sha256=sha256_dosya(yol_liste),
        esik_N0={f"{a:g}": round(KAPI.gereken_n0(math.exp(-DTAU_ESIK / a)), 2) for a in (13.0, 19.0, 39.0)},
        pencereler_gun=dict(on=[-ON_G0, -ON_G1], son=[SON_G0, SON_G1], T_on=T_ON_G, T_son=T_SON_G,
                            negatif_kontrol_on=[-ON_G0, -NK_G0], negatif_kontrol_son=[-NK_G0, -NK_G1]),
        tarih_kurali=tarih_kurali_etkisi(liste, kapi),
        testere_disi=testere_disi(tab),
        binom=[r for r in tab if 18 <= r["K"] <= 45],
        yapay_dieterich=yd,
        gercek_alfa_H0_oy=gercek_alfa(tab, yd["H0"]["31.36"]["dusus_oyu"]),
        gercek_alfa_reddedilen_saf_oy=gercek_alfa(tab, yd["H0"]["31.36"]["reddedilen_saf_dusus_oyu"]),
    )
    with open(os.path.join(BURAYA, "tr6a_onkayit_sayilar.json"), "w", encoding="utf-8") as f:
        json.dump(sayi, f, indent=1, ensure_ascii=False)
        f.write("\n")
    kisa = {k: v for k, v in sayi.items() if k not in ("binom",)}
    print(json.dumps(kisa, ensure_ascii=False, indent=1))
    for r in sayi["binom"]:
        if r["K"] <= 40:
            print(r["K"], r["kritik_H1"], r["alfa_gercek"], r["guc_p075"], r["esik_H0"], r["P_H0_p075"],
                  r["esik_ters"], {p: (v["H1"], v["ayirt"], v["H0"]) for p, v in r["hukum_olasiliklari"].items()
                                   if p in ("0.50", "0.60", "0.65", "0.70", "0.75")})


def virgul(x, b=3):
    return f"{x:.{b}f}".replace(".", ",")


def md_tablolar():
    d = json.load(open(os.path.join(BURAYA, "tr6a_onkayit_sayilar.json")))
    L = ["| K | H1: X ≥ c | P(X ≥ c \\| 0,5) | güç P(X ≥ c \\| 0,75) | H0: X ≤ h | P(X ≤ h \\| 0,75) | ters yön: X ≤ t | "
         "P(X ≤ t \\| 0,5) |", "|---|---|---|---|---|---|---|---|"]
    for r in d["binom"]:
        if 23 <= r["K"] <= 45:
            L.append(f"| {r['K']} | {r['kritik_H1']} | {virgul(r['alfa_gercek'], 4)} | {virgul(r['guc_p075'], 3)} | "
                     f"{r['esik_H0']} | {virgul(r['P_H0_p075'], 4)} | {r['esik_ters']} | {virgul(r['P_ters_p05'], 4)} |")
    print("\n".join(L) + "\n")
    ps = ("0.45", "0.50", "0.55", "0.60", "0.65", "0.70", "0.75")
    L = ["| K | " + " | ".join(f"p = {virgul(float(p), 2)}" for p in ps) + " |", "|---" * (len(ps) + 1) + "|"]
    for r in d["binom"]:
        if r["K"] in (23, 26, 28, 30, 33, 37):
            h = r["hukum_olasiliklari"]
            L.append(f"| {r['K']} | " + " | ".join(
                f"{virgul(h[p]['H1'], 2)} / {virgul(h[p]['ayirt'], 2)} / {virgul(h[p]['H0'], 2)}" for p in ps) + " |")
    print("\n".join(L) + "\n")
    ol = json.load(open(os.path.join(BURAYA, "tr6a_olay_listesi.json")))["olaylar"]
    kapi = json.load(open(os.path.join(BURAYA, "tr6_a_kapi.json")))
    e = KAPI.gereken_n0(math.exp(-DTAU_ESIK / ASIGMA))
    sec = [x for x in ol if x["tarih_kurali_gecer"] and (x["ek1_en_iyi"] or {}).get("N0", 0) >= e]
    kl = KAPI.kumele(sec)
    L = ["| Küme | Olay | Tarih | M | Enlem, boylam | Ek 1 katalog (Mc) | Ek 1 kaba N0 (/yıl) | Mekanizma (ComCat) |",
         "|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(kl, 1):
        for x in c:
            en = x["ek1_en_iyi"]
            L.append(f"| {i} | {x['id']} | {x['zaman'][:10]} | {str(float(x['M'])).replace('.', ',')} | "
                     f"{virgul(x['enlem'], 2)}, {virgul(x['boylam'], 2)} | {en['katalog']} ({virgul(en['mc'], 1)}) | "
                     f"{virgul(en['N0'], 1)} | {x['mekanizma_sinif']} |")
    print("\n".join(L))
    print(f"\n{len(sec)} olay, {len(kl)} küme")


if __name__ == "__main__":
    if "--md" in sys.argv:
        md_tablolar()
    else:
        main()
