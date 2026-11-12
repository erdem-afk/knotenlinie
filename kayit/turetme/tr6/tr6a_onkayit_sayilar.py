"""TR-6a ön kaydı sürüm 2: bütün sayılar (yalnız olay öncesi üstveri; hiçbir olay sonrası sorgu, ağ erişimi yok).

Girdi : tr6_a_sayim.json (155 olaylık havuz), tr6_a_kapi.json (Ek 1 kapı sayımı),
        tr6a_sifir_buyukluk.json (K3: Ek 1 önbelleğinde "0 büyüklük" denetimi; tr6a_sifir_buyukluk.py üretir).
Çıktı : tr6a_olay_listesi.json   -> dondurulan aday listesi: olaylar (155) + olay grupları (birimler); sha256 ön kayıtta
        tr6a_onkayit_sayilar.json -> ön kayıt metnindeki sayılar: kaba kapı önsayımı (sürüm 2 kurallarıyla), binom
                                     tabloları, p0 ızgarasında testere dişi çözümü, güç ve "doğru lob payı" tabloları,
                                     H0 altında N0'a bağlı oy olasılığı, yapay Dieterich sınaması.
Kullanım: python3 -I -B tr6a_onkayit_sayilar.py            (≈ 1 dk; numpy + standart kitaplık)
          python3 -I -B tr6a_onkayit_sayilar.py --md       (ön kayıttaki tabloları Markdown olarak basar)

Bu betik hiçbir oran değişimi hesaplamaz; yapay bölümler yalnız uydurma Poisson sayılarıyla çalışır.
"""
import datetime as dt, hashlib, json, math, os, sys
import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6_a_kapi as KAPI   # noqa: E402  (kumele, gereken_n0, binom_ust, uzaklik_km; ağ kodu çağrılmaz)

# ------------------------------------------------------------------ ön kayıt sabitleri (metinle aynı)
ASIGMA = 19.0
DTAU_ESIK = 10.0
VERI_SONU = dt.datetime(2025, 12, 31, 23, 59, 59)
ISC_GOZDEN = dt.datetime(2023, 12, 31, 23, 59, 59)
ON_G0, ON_G1 = 1826, 30
SON_G0, SON_G1 = 30, 365
T_ON_G, T_SON_G = ON_G0 - ON_G1, SON_G1 - SON_G0          # 1796, 335
NK_G0, NK_G1 = 365, 30
T_NK_ON_G, T_NK_SON_G = ON_G0 - NK_G0, NK_G0 - NK_G1     # 1461, 335
TAMPON_G = 730                                            # B9: ön kümesizleştirme tamponu
SAHTE_J = 3
SAHTE_ILK_G, SAHTE_ADIM_G = 395, 335                      # t'_j = t0 - 395 - 335 (j - 1)
KISA_SON_G = 60                                           # B4: T_son < 60 g -> küme ana hükümden çıkar
P1, ALFA, GUC = 0.75, 0.05, 0.80
GRUP_G, GRUP_KM = 30, 300.0
K_ALT = 23
P0_IZGARA = [round(0.50 + 0.01 * i, 2) for i in range(11)]  # 0,50 .. 0,60
P0_UST = 0.60                                             # p0 > 0,60: hüküm satırı koşulmaz
BILINEN_CIKAN = ("us20005iis", "ci38457511")             # A3: Kumamoto 2016, Ridgecrest 2019
BILINEN_KALAN = ("official20110311054624120_30",)         # Tohoku 2011
TOHUM = 20261112
GUN = dt.timedelta(days=1)


def sha256_dosya(yol):
    return hashlib.sha256(open(yol, "rb").read()).hexdigest()


def T(x):
    return dt.datetime.fromisoformat(x)


def km(a, b):
    return float(KAPI.uzaklik_km(a["enlem"], a["boylam"], np.array([b["enlem"]]), np.array([b["boylam"]]))[0])


# ------------------------------------------------------------------ 1. dondurulan liste: olaylar ve olay grupları
def aday_listesi():
    havuz = json.load(open(os.path.join(BURAYA, "tr6_a_sayim.json")))["olaylar"]
    kapi = json.load(open(os.path.join(BURAYA, "tr6_a_kapi.json")))
    sifir = json.load(open(os.path.join(BURAYA, "tr6a_sifir_buyukluk.json"), encoding="utf-8"))
    gecersiz = {(r["sahip"], r["katalog"]): r for r in sifir["mc_yeniden"]
                if r["ek1_mc"] is not None and r["mc_dar_kural_maskeli"] != r["mc_suzgecsiz_maskeli"]}
    ek1 = {o["id"]: o for o in kapi["olaylar"]}
    assert len(havuz) == 155 and set(ek1) == {o["id"] for o in havuz}
    kume_no = {}
    for i, c in enumerate(kapi["kapilar"]["en_iyi_acik (<=40 km)"]["19"]["kumeler"]):
        for x in c:
            kume_no[x] = i
    liste = []
    for o in sorted(havuz, key=lambda x: x["zaman"]):
        e = ek1[o["id"]]
        kat = {}
        for k, v in sorted(e["kataloglar"].items()):
            if v.get("mc") is None:
                continue
            g = gecersiz.get((o["id"], k))
            kat[k] = dict(mc=v["mc"], N0_halka=v["N0"], N0_halka_mc05=v.get("N0_mc05"), tur=v["tur"],
                          gecersiz_sifir_buyukluk=bool(g),
                          mc_dar_kural=(g or {}).get("mc_dar_kural_maskeli"))
        en = e["en_iyi"]
        liste.append(dict(
            id=o["id"], zaman=o["zaman"], M=o["M"], enlem=o["enlem"], boylam=o["boylam"], L_km=o["L_km"],
            halka_km=o["halka_km"], ek1_kataloglar=kat,
            ek1_en_iyi=None if en is None else dict(katalog=en["katalog"], mc=en["mc"], N0=en["N0"], tur=en["tur"]),
            ek1_kume_19=kume_no.get(o["id"]),
            mekanizma_sinif=e.get("mekanizma", {}).get("sinif", "bilinmiyor"),
            mekanizma_rake=e.get("mekanizma", {}).get("rake"), mekanizma_dip=e.get("mekanizma", {}).get("dip")))
    # olay grubu (§3.2): 30 gün ve 300 km içinde zincir
    grup = {x["id"]: x["id"] for x in liste}
    for i, a in enumerate(liste):
        for b in liste[i + 1:]:
            if (T(b["zaman"]) - T(a["zaman"])).total_seconds() / 86400 <= GRUP_G and km(a, b) <= GRUP_KM:
                eski, yeni = grup[b["id"]], grup[a["id"]]
                for k in grup:
                    if grup[k] == eski:
                        grup[k] = yeni
    for x in liste:
        x["grup"] = grup[x["id"]]
    birimler = []
    for gid in sorted(set(grup.values()), key=lambda g: next(x["zaman"] for x in liste if x["id"] == g)):
        uy = [x for x in liste if x["grup"] == gid]
        buyuk = max(uy, key=lambda x: (x["M"], x["zaman"]))
        t0, ts = T(uy[0]["zaman"]), T(uy[-1]["zaman"])
        son_bitis = t0 + dt.timedelta(days=SON_G1)
        birimler.append(dict(
            id=gid, uyeler=[x["id"] for x in uy], buyuk_uye=buyuk["id"], M=buyuk["M"], enlem=buyuk["enlem"],
            boylam=buyuk["boylam"], L_km=buyuk["L_km"], halka_km=buyuk["halka_km"],
            zaman=uy[0]["zaman"], t_s=uy[-1]["zaman"],
            son_baslangic=(ts + dt.timedelta(days=SON_G0)).isoformat(timespec="seconds"),
            son_bitis_kesilmemis=son_bitis.isoformat(timespec="seconds"),
            tarih_kurali_gecer=son_bitis <= VERI_SONU,
            isc_gozden_gecmis=son_bitis <= ISC_GOZDEN,
            kataloglar=buyuk["ek1_kataloglar"], mekanizma_sinif=buyuk["mekanizma_sinif"],
            bilinen_sonuclu=("cikan" if set(BILINEN_CIKAN) & {x["id"] for x in uy} else
                             "kalan" if set(BILINEN_KALAN) & {x["id"] for x in uy} else None),
            on_indirme_baslangic=(t0 - dt.timedelta(days=ON_G0 + TAMPON_G)).isoformat(timespec="seconds"),
            sahte_on_indirme_baslangic=(t0 - dt.timedelta(days=SAHTE_ILK_G + SAHTE_ADIM_G * (SAHTE_J - 1) + ON_G0
                                                          + TAMPON_G)).isoformat(timespec="seconds"),
        ))
    # katalog seçimi (§3.5, A4 ISC kuralı ve K3 sıfır büyüklük); kaba N0 = Ek 1 halka N0'ı (lob payı 0,25)
    for b in birimler:
        izin = {k: v for k, v in b["kataloglar"].items() if not v["gecersiz_sifir_buyukluk"]
                and not (k == "ISC" and not b["isc_gozden_gecmis"])}
        b["secilebilir_kataloglar"] = sorted(izin)
        b["isc_kurali_ile_dusen"] = ("ISC" in b["kataloglar"] and not b["isc_gozden_gecmis"])
        sira = ("ISC", "ComCat", "GeoNet", "EMSC", "KOERI", "INGV")
        b["kaba_secim"] = (max(izin, key=lambda k: (izin[k]["N0_halka"], -sira.index(k))) if izin else None)
        b["kaba_N0"] = izin[b["kaba_secim"]]["N0_halka"] if izin else 0.0
        b["kaba_N0_mc05"] = max([v["N0_halka_mc05"] or 0 for v in izin.values()] or [0])
        b["kosu_adayi"] = bool(b["tarih_kurali_gecer"] and b["kataloglar"])
    # B4 son pencere kesmesi ve A1 sahte zamanların geçerliliği (yalnız havuz üstverisi)
    for b in birimler:
        t0, ts = T(b["zaman"]), T(b["t_s"])
        bas, bit = ts + dt.timedelta(days=SON_G0), t0 + dt.timedelta(days=SON_G1)
        kes2, kes3 = [], []
        for x in liste:
            if x["grup"] == b["id"]:
                continue
            tx = T(x["zaman"])
            if bas <= tx < bit:
                d = km(b, x)
                if d <= 2 * b["L_km"]:
                    kes2.append((tx, x["id"], round(d)))
                if d <= 3 * b["L_km"]:
                    kes3.append((tx, x["id"], round(d)))

        def kesme(lst):
            if not lst:
                return dict(olay=None, son_bitis=bit.isoformat(timespec="seconds"),
                            T_son_g=round((bit - bas).total_seconds() / 86400, 3))
            tx, xid, d = min(lst)
            sb = tx - GUN
            return dict(olay=xid, uzaklik_km=d, son_bitis=sb.isoformat(timespec="seconds"),
                        T_son_g=round((sb - bas).total_seconds() / 86400, 3))
        b["kesme_2L_dis_merkez"] = kesme(kes2)      # önsayım (bağlayıcı kural r_k <= 2L ile manifestte)
        b["kesme_3L_dis_merkez"] = kesme(kes3)      # üst sınır duyarlılığı
        Ts = b["kesme_2L_dis_merkez"]["T_son_g"]
        b["pi_onsayim"] = round(Ts / (T_ON_G + Ts), 5)
        sahte = []
        kay = (ts - t0)
        for j in range(1, SAHTE_J + 1):
            tj = t0 - dt.timedelta(days=SAHTE_ILK_G + SAHTE_ADIM_G * (j - 1))
            s0, s1 = tj + kay + dt.timedelta(days=SON_G0), tj + dt.timedelta(days=SON_G1)
            ortusen = []
            for x in liste:
                if x["grup"] == b["id"]:
                    continue
                tx = T(x["zaman"])
                if tx < s1 and tx + dt.timedelta(days=365) > s0 and km(b, x) < 3 * x["L_km"] + 3 * b["L_km"]:
                    ortusen.append(x["id"])
            sahte.append(dict(j=j, t=tj.isoformat(timespec="seconds"), son=[s0.isoformat(timespec="seconds"),
                              s1.isoformat(timespec="seconds")], gecerli=not ortusen, ortusen=ortusen))
        b["sahte"] = sahte
    return liste, birimler, kapi, sifir


# ------------------------------------------------------------------ 2. kaba kapı önsayımı (sürüm 2 kuralları)
def onsayim(birimler, esik, kurallar=True, kesme="kesme_2L_dis_merkez", n0_alan="kaba_N0", carpan=1.0):
    adim = {}
    ad = [b for b in birimler if b["kosu_adayi"]]
    adim["kosu_adayi_birim"] = len(ad)
    if kurallar:
        gec = [b for b in ad if b[n0_alan] * carpan >= esik]
    else:   # sürüm 1 yeniden üretimi: olay başına, Ek 1 en iyi katalog, ISC ve sıfır kuralı yok
        gec = [b for b in ad if max([v["N0_halka"] for v in b["kataloglar"].values()] or [0]) * carpan >= esik]
    adim["kapi_birim"] = len(gec)
    kl = KAPI.kumele(gec)
    adim["kume"] = len(kl)
    if not kurallar:
        return adim, kl, []
    cikan = []
    kalan = []
    for c in kl:
        tem = c[0]
        uy = {u for x in c for u in x["uyeler"]}
        if set(BILINEN_CIKAN) & uy:
            cikan.append(dict(temsilci=tem["id"], neden="A3 bilinen sonuçlu"))
        elif tem[kesme]["T_son_g"] < KISA_SON_G:
            cikan.append(dict(temsilci=tem["id"], neden=f"B4 kısa son pencere ({tem[kesme]['T_son_g']:.1f} g, "
                                                          f"{tem[kesme]['olay']})"))
        else:
            kalan.append(c)
    adim["cikan_A3"] = sum(1 for x in cikan if x["neden"].startswith("A3"))
    adim["cikan_B4"] = sum(1 for x in cikan if x["neden"].startswith("B4"))
    adim["K_kaba"] = len(kalan)
    return adim, kalan, cikan


def onsayim_ozet(birimler):
    esik = {a: KAPI.gereken_n0(math.exp(-DTAU_ESIK / a)) for a in (13.0, 19.0, 39.0)}
    out = dict(esik={f"{a:g}": round(e, 2) for a, e in esik.items()})
    # sürüm 1 yeniden üretimi (olay başına, kural yok): 37 küme beklenir
    for a, e in esik.items():
        ad, kl, cik = onsayim(birimler, e)
        sat = dict(adimlar=ad, cikan=cik)
        if a == 19.0:
            sat["kumeler"] = [[dict(id=x["id"], uyeler=x["uyeler"], zaman=x["zaman"][:10], M=x["M"],
                                    enlem=x["enlem"], boylam=x["boylam"], katalog=x["kaba_secim"],
                                    mc=x["kataloglar"][x["kaba_secim"]]["mc"], N0=x["kaba_N0"],
                                    mekanizma=x["mekanizma_sinif"], T_son_g=x["kesme_2L_dis_merkez"]["T_son_g"],
                                    kesme_olayi=x["kesme_2L_dis_merkez"]["olay"],
                                    sahte_gecerli=sum(s["gecerli"] for s in x["sahte"]),
                                    isc_kurali=x["isc_kurali_ile_dusen"])
                               for x in c] for c in kl]
            dok = {}
            for c in kl:
                m = max(c, key=lambda x: x["M"])["mekanizma_sinif"]
                dok[m] = dok.get(m, 0) + 1
            sat["mekanizma_dokumu"] = dok
            sat["sahte_gecerli_toplam"] = sum(sum(s["gecerli"] for s in c[0]["sahte"]) for c in kl)
            sat["sahte_toplam"] = SAHTE_J * len(kl)
            # ISC kuralıyla kapıdan düşen (D6) birimler
            sat["D6_isc_kurali_dusen"] = [b["id"] for b in birimler if b["kosu_adayi"] and b["isc_kurali_ile_dusen"]
                                          and b["kaba_N0"] < e and
                                          (b["kataloglar"].get("ISC", {}).get("N0_halka", 0) >= e)]
            sat["isc_kurali_katalog_degisen"] = [dict(id=b["id"], yeni=b["kaba_secim"], N0=b["kaba_N0"])
                                                 for b in birimler if b["kosu_adayi"] and b["isc_kurali_ile_dusen"]
                                                 and b["kaba_N0"] >= e and
                                                 b["kataloglar"].get("ISC", {}).get("N0_halka", 0) > b["kaba_N0"]]
            # duyarlılıklar (bilgi): kesme 3L, kaba N0 x 0,5 ve x 0,25, Mc + 0,5
            sat["duyarlilik"] = {
                "kesme_3L": onsayim(birimler, e, kesme="kesme_3L_dis_merkez")[0]["K_kaba"],
                "N0_x0.5": onsayim(birimler, e, carpan=0.5)[0]["K_kaba"],
                "N0_x0.25": onsayim(birimler, e, carpan=0.25)[0]["K_kaba"],
                "Mc_arti_0.5": onsayim(birimler, e, n0_alan="kaba_N0_mc05")[0]["K_kaba"],
                "Mc_arti_0.5_ve_N0_x0.5": onsayim(birimler, e, n0_alan="kaba_N0_mc05", carpan=0.5)[0]["K_kaba"],
            }
        out[f"{a:g}"] = sat
    return out


def surum1_yeniden(liste):
    """Sürüm 1 kaba kapısı (olay başına, Ek 1 en iyi katalog, yalnız tarih kuralı): 46 olay / 37 küme."""
    e = KAPI.gereken_n0(math.exp(-DTAU_ESIK / ASIGMA))
    sec = [x for x in liste if T(x["zaman"]) + dt.timedelta(days=SON_G1) <= VERI_SONU
           and (x["ek1_en_iyi"] or {}).get("N0", 0) >= e]
    return dict(olay=len(sec), kume=len(KAPI.kumele(sec)))


def b3_ciftleri(liste, birimler):
    """B3: bir koşu adayının ön indirmesi [t_B - 1826 - 730 g, t_B - 30 g) başka bir adayın son penceresini
    [t_A, t_A + 365 g) kapsıyor ve kaba bölgeleri (dış merkez < 2 L_A + 2 L_B) örtüşüyor."""
    ad = [b for b in birimler if b["kosu_adayi"]]
    out = {}
    for tampon, ad_ in ((0, "tamponsuz (İNCELEME-1 ölçütü)"), (TAMPON_G, "730 g tamponla")):
        m = set()
        for a in ad:
            for b in ad:
                if a is b:
                    continue
                ta, tb = T(a["zaman"]), T(b["zaman"])
                if tb - dt.timedelta(days=ON_G0 + tampon) < ta + dt.timedelta(days=365) and \
                        ta < tb - dt.timedelta(days=ON_G1) and km(a, b) < 2 * a["L_km"] + 2 * b["L_km"]:
                    m.add((a["id"], b["id"]))
        out[ad_] = dict(cift=len(m), etkilenen_A=len({p[0] for p in m}))
    return out


# ------------------------------------------------------------------ 3. binom tabloları ve p0 ızgarası
def binom_alt(k, n, p):
    if k < 0:
        return 0.0
    return float(sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1)))


def kritik(K, p0):
    return next(c for c in range(K + 2) if KAPI.binom_ust(c, K, p0) <= ALFA + 1e-15)


def esik_H0(K):
    return max([h for h in range(-1, K + 1) if h < 0 or binom_alt(h, K, P1) <= ALFA])


def guc(K, p0, p1=P1):
    return KAPI.binom_ust(kritik(K, p0), K, p1)


def binom_tablosu(Ks=range(15, 61)):
    tab = []
    for K in Ks:
        c, h = kritik(K, 0.5), esik_H0(K)
        sat = dict(K=K, kritik_H1=c, alfa_gercek=round(KAPI.binom_ust(c, K, 0.5), 4),
                   guc_p075=round(KAPI.binom_ust(c, K, P1), 4), esik_H0=h,
                   P_H0_p075=round(binom_alt(h, K, P1), 4) if h >= 0 else 0.0)
        sat["hukum_olasiliklari"] = {
            f"{p:.2f}": dict(H1=round(KAPI.binom_ust(c, K, p), 3), H0=round(binom_alt(h, K, p), 3),
                             ayirt=round(1 - KAPI.binom_ust(c, K, p) - binom_alt(h, K, p), 3))
            for p in (0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80)}
        tab.append(sat)
    return tab


def p0_izgarasi(Kmax=80):
    """A1/§4.6: p0 = max(0,50; ⌈100 p̂0⌉/100) için c(K), gerçek α (p0'da), güç (p1 0,75) ve testere dişi çözümü."""
    out = {}
    for p0 in P0_IZGARA:
        satir = {}
        for K in range(K_ALT, Kmax + 1):
            c = kritik(K, p0)
            satir[K] = dict(c=c, alfa=round(KAPI.binom_ust(c, K, p0), 4), guc=round(KAPI.binom_ust(c, K, P1), 4),
                            h=esik_H0(K))
        cozum = {}
        for Kk in range(K_ALT, Kmax + 1):
            uygun = [k for k in range(K_ALT, Kk + 1) if satir[k]["guc"] >= GUC]
            if uygun:
                kh = max(uygun)
                cozum[Kk] = dict(K_hukum=kh, atilan=Kk - kh, guc=satir[kh]["guc"], c=satir[kh]["c"])
            else:
                cozum[Kk] = dict(K_hukum=Kk, atilan=0, guc=satir[Kk]["guc"], c=satir[Kk]["c"], tasarim_alti=True)
        kalici = next((K for K in range(K_ALT, Kmax + 1) if all(satir[k]["guc"] >= GUC
                                                                 for k in range(K, Kmax + 1))), None)
        ilk = next((K for K in range(K_ALT, Kmax + 1) if satir[K]["guc"] >= GUC), None)
        out[f"{p0:.2f}"] = dict(tablo={str(k): v for k, v in satir.items()},
                                testere={str(k): v for k, v in cozum.items()}, ilk_K_guc08=ilk, kalici_K_guc08=kalici)
    # p0 = 0,50 için K = 28..200 denetimi (sürüm 1 savı)
    for K in range(28, 201):
        assert guc(K, 0.5) >= GUC, K
    return out


def gereken_p1(K, p0):
    """p0 ile c(K) sabitken güç 0,80 için gereken en küçük küme başına oy olasılığı (ikiye bölme)."""
    c = kritik(K, p0)
    lo, hi = 0.5, 0.999
    for _ in range(60):
        m = (lo + hi) / 2
        if KAPI.binom_ust(c, K, m) >= GUC:
            hi = m
        else:
            lo = m
    return hi


def p0_kestirim_dagilimi(Ks=(23, 28, 33, 39), p_sahte=(0.46, 0.48, 0.50, 0.52)):
    """p̂0 = S/J, S ~ Binom(J, p_sahte) (bağımsızlık varsayımı; gerçek ilişki saçılımı büyütür), J = 3K.
    Çıktı: P(p0 > 0,50), P(p0 > 0,60) ve beklenen güç (p1 0,75; K sabit, atma yok)."""
    out = {}
    for K in Ks:
        J = SAHTE_J * K
        for ps in p_sahte:
            pmf = [math.comb(J, s) * ps ** s * (1 - ps) ** (J - s) for s in range(J + 1)]
            p_ust50 = p_ust60 = eg = 0.0
            for s, w in enumerate(pmf):
                yuz = max(50, -(-100 * s // J))
                if yuz > 50:
                    p_ust50 += w
                if yuz > 60:
                    p_ust60 += w
                    continue
                eg += w * guc(K, yuz / 100)
            out[f"K{K}_p{ps:.2f}"] = dict(J=J, P_p0_ust_050=round(p_ust50, 3), P_p0_ust_060=round(p_ust60, 4),
                                          beklenen_guc=round(eg, 3), guc_p0_050=round(guc(K, 0.5), 3))
    return out


# ------------------------------------------------------------------ 4. oy olasılığı (büyük N0 için pencereli kesin hesap)
class Oy:
    """Koşullu binom oyu (§4.3) eşikleri ve kesin Poisson olasılıkları; büyük n için pencereli binom."""

    def __init__(self, nmax, T_on=T_ON_G, T_son=T_SON_G):
        self.pi = T_son / (T_on + T_son)
        self.LF = np.concatenate([[0.0], np.cumsum(np.log(np.arange(1, nmax + 2)))])
        self.nmax = nmax
        self.b_dus = np.full(nmax + 1, -1)
        self.b_art = np.full(nmax + 1, 10 ** 9)
        for n in range(1, nmax + 1):
            lo, F = self._cdf_pencere(n, self.pi)
            ok = np.nonzero(F <= 0.5 + 1e-12)[0]
            self.b_dus[n] = lo + ok.max() if len(ok) else (lo - 1)
            ust = 1 - np.concatenate([[0.0], F[:-1]])
            ok2 = np.nonzero(ust <= 0.5 + 1e-12)[0]
            self.b_art[n] = lo + ok2.min() if len(ok2) else 10 ** 9

    def _cdf_pencere(self, n, p):
        s = math.sqrt(n * p * (1 - p)) + 1
        lo = max(0, int(n * p - 16 * s - 5))
        hi = min(n, int(n * p + 16 * s + 5))
        k = np.arange(lo, hi + 1)
        lp = self.LF[n] - self.LF[k] - self.LF[n - k] + k * math.log(p) + (n - k) * math.log1p(-p)
        return lo, np.cumsum(np.exp(lp))

    def F(self, b, n, p):
        if b < 0:
            return 0.0
        lo, F = self._cdf_pencere(n, p)
        if b < lo:
            return 0.0
        return float(F[min(b - lo, len(F) - 1)])

    def olasilik(self, lam_on, lam_son, yon=-1):
        L = lam_on + lam_son
        th = lam_son / L
        s = math.sqrt(L)
        n = np.arange(max(1, int(L - 12 * s - 10)), int(L + 12 * s + 20) + 1)
        assert n[-1] <= self.nmax
        lw = -L + n * math.log(L) - self.LF[n]
        top = 0.0
        for ni, w in zip(n, np.exp(lw)):
            if yon < 0:
                top += w * self.F(int(self.b_dus[ni]), int(ni), th)
            else:
                top += w * (1 - self.F(int(self.b_art[ni]) - 1, int(ni), th))
        return float(top)


def dieterich_N(r, t1, t2, dtau, asig, ta):
    q = math.exp(-dtau / asig)
    if math.isinf(ta):
        return r * (t2 - t1) / q
    f = lambda t: ta * math.log(math.exp(t / ta) + q - 1)
    return r * (f(t2) - f(t1))


def yapay_dieterich(oy):
    rng = np.random.default_rng(TOHUM)
    T_on, t1, t2 = T_ON_G / 365.25, SON_G0 / 365.25, SON_G1 / 365.25
    out = dict(H0={}, golge={}, pozitif={}, olcer={}, gerekli_dogru_lob_payi={})
    for N0 in (17.08, 31.36, 50.0, 111.2, 300.0, 1000.0, 4500.0):
        out["H0"][f"{N0:g}"] = dict(dusus_oyu=round(oy.olasilik(N0 * T_on, N0 * (t2 - t1), -1), 4),
                                    artis_oyu=round(oy.olasilik(N0 * T_on, N0 * (t2 - t1), +1), 4))
    for tdot in (2.0, 10.0, 50.0, 0.0):
        ta = math.inf if tdot == 0 else ASIGMA / tdot
        an = "kalici" if tdot == 0 else f"tau0_{tdot:g}_kPa_yil (t_a {ta:.2f} y)"
        out["golge"][an], out["pozitif"][an], out["olcer"][an] = {}, {}, {}
        for N0 in (31.36, 50.0, 111.2):
            for dtau, kap in ((-DTAU_ESIK, "golge"), (+DTAU_ESIK, "pozitif")):
                lam_son = dieterich_N(N0, t1, t2, dtau, ASIGMA, ta)
                out[kap][an][f"{N0:g}"] = round(oy.olasilik(N0 * T_on, lam_son, -1 if dtau < 0 else +1), 4)
            lam_son = dieterich_N(N0, t1, t2, -DTAU_ESIK, ASIGMA, ta)
            n_on, n_son = rng.poisson(N0 * T_on, 20000), rng.poisson(lam_son, 20000)
            with np.errstate(divide="ignore"):
                est = ASIGMA * np.log((n_son / (t2 - t1)) / (n_on / T_on))
            out["olcer"][an][f"{N0:g}"] = dict(
                beklenen_dtau_est=round(ASIGMA * math.log(lam_son / (t2 - t1) / N0), 2),
                medyan=round(float(np.median(est)), 2), q10=round(float(np.quantile(est, 0.10)), 2),
                q90=round(float(np.quantile(est, 0.90)), 2))
    a = rng.poisson(31.36 * T_on, 200000)
    b = rng.poisson(31.36 * (t2 - t1), 200000)
    n = a + b
    out["monte_carlo_denetim_H0_31.36"] = round(float(((b <= oy.b_dus[n]) & (n > 0)).mean()), 4)
    # Mc_kul - Mc_lob farkının oya etkisi (kapı sınırı N0 31,36 Mc_lob'da, b = 1, kalıcı -10 kPa)
    q = math.exp(-DTAU_ESIK / ASIGMA)          # gölge: oran q kat (kalıcı adım)
    out["mc_farki"] = {}
    for dM in (0.0, 0.3, 0.5, 1.0):
        N = 31.36 * 10 ** (-dM)
        out["mc_farki"][f"{dM:g}"] = dict(N0_etkin=round(N, 2), P_D_kalici=round(oy.olasilik(N * T_on, N * (t2 - t1) * q, -1), 3),
                                          P_D_H0=round(oy.olasilik(N * T_on, N * (t2 - t1), -1), 4))
    return out


def dogru_lob_payi(yd, p0_grid=(0.50, 0.52, 0.55), Ks=(23, 28, 33, 39, 45)):
    """B5: güç 0,80 için gereken küme başına oy olasılığı p1* (p0 ile c(K) verilmişken) ve buna karşılık gelen doğru lob
    payı f = (p1* - w) / (P_D - w); w yanlış lobların oy olasılığı, P_D doğru lobunki."""
    PD = {"kalıcı, ΔMc 0": yd["golge"]["kalici"]["31.36"], "10 kPa/yıl, ΔMc 0":
          yd["golge"]["tau0_10_kPa_yil (t_a 1.90 y)"]["31.36"], "kalıcı, ΔMc 0,5": yd["mc_farki"]["0.5"]["P_D_kalici"],
          "kalıcı, ΔMc 1,0": yd["mc_farki"]["1"]["P_D_kalici"]}
    out = {}
    for p0 in p0_grid:
        for K in Ks:
            ps = gereken_p1(K, p0)
            sat = dict(p1_gereken=round(ps, 3), f={})
            for w in (p0 if p0 > 0.5 else yd["H0"]["31.36"]["dusus_oyu"], 0.40, 0.30, 0.20):
                for ad, pD in PD.items():
                    sat["f"][f"w={w:.4g} | {ad}"] = round((ps - w) / (pD - w), 3) if (ps - w) / (pD - w) <= 1 else None
            out[f"p0={p0:.2f} K={K}"] = sat
    return out, PD


# ------------------------------------------------------------------ ana
def main():
    liste, birimler, kapi, sifir = aday_listesi()
    yol = os.path.join(BURAYA, "tr6a_olay_listesi.json")
    with open(yol, "w", encoding="utf-8") as f:
        json.dump(dict(aciklama="TR-6a sürüm 2 dondurulan aday listesi: ComCat finite-fault havuzu (155 olay) ve olay "
                                "grupları (birimler): Ek 1 katalog ve Mc değerleri (K3 sıfır büyüklük işaretiyle), tarih "
                                "kuralı, ISC kuralı, B4 kesmesi (önsayım: dış merkez ≤ 2L), sahte zamanlar ve "
                                "geçerlilikleri, ön indirme başlangıçları. Olay sonrası katalog bilgisi içermez.",
                       uretici="tr6a_onkayit_sayilar.py (sürüm 2)",
                       girdi_sha256={k: sha256_dosya(os.path.join(BURAYA, k))
                                     for k in ("tr6_a_sayim.json", "tr6_a_kapi.json", "tr6a_sifir_buyukluk.json")},
                       olaylar=liste, birimler=birimler), f, indent=1, ensure_ascii=False)
        f.write("\n")
    tab = binom_tablosu()
    oy = Oy(30000)
    yd = yapay_dieterich(oy)
    f_tab, PD = dogru_lob_payi(yd)
    ad = [b for b in birimler if b["kosu_adayi"]]
    sayi = dict(
        olay_listesi_sha256=sha256_dosya(yol),
        esik_N0={f"{a:g}": round(KAPI.gereken_n0(math.exp(-DTAU_ESIK / a)), 2) for a in (13.0, 19.0, 39.0)},
        surum1_yeniden=surum1_yeniden(liste),
        havuz=dict(olay=len(liste), birim=len(birimler),
                   tarih_disi_birim=[b["id"] for b in birimler if not b["tarih_kurali_gecer"]],
                   katalogsuz_birim=sum(1 for b in birimler if not b["kataloglar"]),
                   kosu_adayi_birim=len(ad), kosu_adayi_olay=sum(len(b["uyeler"]) for b in ad),
                   kosu_adayi_isc_sinir_otesi=sum(1 for b in ad if not b["isc_gozden_gecmis"]),
                   kosu_adayi_isc_sinir_otesi_isc_li=sum(1 for b in ad if not b["isc_gozden_gecmis"]
                                                         and "ISC" in b["kataloglar"]),
                   cok_uyeli=[b["uyeler"] for b in birimler if len(b["uyeler"]) > 1],
                   ts_kaymasi_g={b["id"]: round((T(b["t_s"]) - T(b["zaman"])).total_seconds() / 86400, 2)
                                 for b in birimler if len(b["uyeler"]) > 1},
                   sifir_buyukluk_gecersiz=[(x["id"], k) for x in liste for k, v in x["ek1_kataloglar"].items()
                                            if v["gecersiz_sifir_buyukluk"]],
                   en_erken_sahte_on_indirme=min(b["sahte_on_indirme_baslangic"] for b in ad),
                   en_gec_sorgu_bitisi=max(b["son_bitis_kesilmemis"] for b in ad)),
        onsayim=onsayim_ozet(birimler),
        b3=b3_ciftleri(liste, birimler),
        binom=[r for r in tab if 18 <= r["K"] <= 60],
        p0_izgarasi=p0_izgarasi(),
        p0_kestirim=p0_kestirim_dagilimi(),
        yapay_dieterich=yd,
        dogru_lob_payi=f_tab, P_D_senaryolari=PD,
        gercek_alfa_poisson={f"{N0}": {K: round(KAPI.binom_ust(kritik(K, 0.5), K, yd["H0"][N0]["dusus_oyu"]), 4)
                                       for K in (23, 28, 33, 39)} for N0 in yd["H0"]},
    )
    with open(os.path.join(BURAYA, "tr6a_onkayit_sayilar.json"), "w", encoding="utf-8") as f:
        json.dump(sayi, f, indent=1, ensure_ascii=False)
        f.write("\n")
    o = sayi["onsayim"]
    print(json.dumps(dict(sha=sayi["olay_listesi_sha256"], s1=sayi["surum1_yeniden"], havuz=sayi["havuz"],
                          onsayim={a: {k: v for k, v in o[a].items() if k != "kumeler"} for a in ("13", "19", "39")},
                          b3=sayi["b3"], p0_kestirim=sayi["p0_kestirim"], H0=yd["H0"], mc_farki=yd["mc_farki"],
                          mc=yd["monte_carlo_denetim_H0_31.36"]), ensure_ascii=False, indent=1))


# ------------------------------------------------------------------ Markdown tabloları
def v(x, b=3):
    return f"{x:.{b}f}".replace(".", ",")


def md_tablolar():
    d = json.load(open(os.path.join(BURAYA, "tr6a_onkayit_sayilar.json"), encoding="utf-8"))
    print("### §6.1 eşik tablosu (p0 = 0,50)\n")
    L = ["| K | H1: X ≥ c | P(X ≥ c \\| 0,5) | güç P(X ≥ c \\| 0,75) | H0: X ≤ h | P(X ≤ h \\| 0,75) |",
         "|---|---|---|---|---|---|"]
    for r in d["binom"]:
        if 23 <= r["K"] <= 45:
            L.append(f"| {r['K']} | {r['kritik_H1']} | {v(r['alfa_gercek'], 4)} | {v(r['guc_p075'])} | "
                     f"{r['esik_H0']} | {v(r['P_H0_p075'], 4)} |")
    print("\n".join(L) + "\n")
    ps = ("0.45", "0.50", "0.55", "0.60", "0.65", "0.70", "0.75")
    L = ["| K | " + " | ".join(f"p = {v(float(p), 2)}" for p in ps) + " |", "|---" * (len(ps) + 1) + "|"]
    for r in d["binom"]:
        if r["K"] in (23, 26, 28, 30, 33, 37):
            h = r["hukum_olasiliklari"]
            L.append(f"| {r['K']} | " + " | ".join(
                f"{v(h[p]['H1'], 2)} / {v(h[p]['ayirt'], 2)} / {v(h[p]['H0'], 2)}" for p in ps) + " |")
    print("\n".join(L) + "\n")
    print("### p0 ızgarası: c(K) / güç (p1 0,75)\n")
    g = d["p0_izgarasi"]
    p0s = list(g)
    L = ["| K | " + " | ".join(f"p₀ {v(float(p), 2)}" for p in p0s) + " |", "|---" * (len(p0s) + 1) + "|"]
    for K in range(23, 46):
        L.append(f"| {K} | " + " | ".join(f"{g[p]['tablo'][str(K)]['c']} / {v(g[p]['tablo'][str(K)]['guc'], 2)}"
                                          for p in p0s) + " |")
    print("\n".join(L) + "\n")
    print("### testere dişi: hükmün K'si (atılan) ; * = tasarım gücünün altında, atma yok\n")
    L = ["| K_kapı | " + " | ".join(f"p₀ {v(float(p), 2)}" for p in p0s) + " |", "|---" * (len(p0s) + 1) + "|"]
    for K in range(23, 46):
        cells = []
        for p in p0s:
            t = g[p]["testere"][str(K)]
            cells.append(f"{t['K_hukum']}*" if t.get("tasarim_alti") else
                         (f"{t['K_hukum']} (−{t['atilan']})" if t["atilan"] else f"{t['K_hukum']}"))
        L.append(f"| {K} | " + " | ".join(cells) + " |")
    print("\n".join(L) + "\n")
    print("ilk / kalıcı K (güç ≥ 0,80):", {p: (g[p]["ilk_K_guc08"], g[p]["kalici_K_guc08"]) for p in p0s}, "\n")
    print("### güç (p1 0,75) p0 = 0,50 / 0,52 / 0,55, K = 23..45\n")
    L = ["| K | c / α / güç (p₀ 0,50) | c / α / güç (p₀ 0,52) | c / α / güç (p₀ 0,55) |", "|---|---|---|---|"]
    for K in range(23, 46):
        L.append(f"| {K} | " + " | ".join(
            f"{g[p]['tablo'][str(K)]['c']} / {v(g[p]['tablo'][str(K)]['alfa'], 4)} / {v(g[p]['tablo'][str(K)]['guc'])}"
            for p in ("0.50", "0.52", "0.55")) + " |")
    print("\n".join(L) + "\n")
    print("### doğru lob payı\n")
    for k, s in d["dogru_lob_payi"].items():
        print(k, s["p1_gereken"], s["f"])
    print("\n### p0 kestirim dağılımı\n")
    for k, s in d["p0_kestirim"].items():
        print(k, s)
    print("\n### Ek A (sürüm 2 önsayımı, Aσ 19)\n")
    L = ["| Küme | Birim (üyeler) | Tarih | M | Enlem, boylam | Katalog (Mc) | Kaba N0 (/yıl) | Mekanizma | "
         "Kesilmiş T_son (g) | Geçerli sahte j |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(d["onsayim"]["19"]["kumeler"], 1):
        for x in c:
            uy = x["id"] if len(x["uyeler"]) == 1 else x["id"] + " (+" + ", ".join(u for u in x["uyeler"] if u != x["id"]) + ")"
            L.append(f"| {i} | {uy} | {x['zaman']} | {str(float(x['M'])).replace('.', ',')} | {v(x['enlem'], 2)}, "
                     f"{v(x['boylam'], 2)} | {x['katalog']} ({v(x['mc'], 1)}){' ‡' if x['isc_kurali'] else ''} | "
                     f"{v(x['N0'], 1)} | {x['mekanizma']} | {v(x['T_son_g'], 1)}"
                     f"{' (' + x['kesme_olayi'] + ')' if x['kesme_olayi'] else ''} | {x['sahte_gecerli']} |")
    print("\n".join(L))
    print("\nçıkan:", d["onsayim"]["19"]["cikan"])


if __name__ == "__main__":
    if "--md" in sys.argv:
        md_tablolar()
    else:
        main()
