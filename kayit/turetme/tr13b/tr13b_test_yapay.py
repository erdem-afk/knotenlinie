#!/usr/bin/env python3
"""TR-13b koşu betiğinin (tr13b_kosu.py) yapay sınaması. GERÇEK KATALOGDA HİÇBİR ÖLÇÜ HESAPLANMAZ.

Gerçek dosyalara tek dokunuş: `tr13_ham_sha256.txt`'nin ayrıştırılması (biçim). Bütün kataloglar yapay ETAS'tan
(tr13_guc.py) üretilip gerçek arşivlerle aynı üye adlarıyla SAHTE tar.gz'lere yazılır; sahte sha256 listesi ve sahte
tr13_tamsayim.json ile koşu uçtan uca çalıştırılır.

  birim     hızlı birim sınamaları (U1–U14)
  uctan     uçtan uca: E1 sinyalsiz -> "ayırt edilemez"; E2 f = 0,5 -> "VAR"; E3 bozuk girdi -> "veri yok" /
            "geçersiz" (sha, eksik parça, kalibrasyon bozulması, D-3 bozulması) ve tek koşu kilidi
  mutasyon  her mutasyon betiğin bir kopyasına uygulanır; birim + ilgili uçtan uca sınamalardan en az biri düşmeli

Kullanım: python3 -I -B tr13b_test_yapay.py <karalama_dizini> birim|uctan|mutasyon [--modul <tr13b_kosu.py yolu>]
Çıktı: <karalama_dizini>/test_<kip>.json (özet).
"""
import importlib.util
import io
import json
import math
import os
import shutil
import subprocess
import sys
import tarfile
import time

import numpy as np

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
TR13 = os.path.abspath(os.path.join(BURA, "..", "tr13"))
sys.path.insert(0, TR13)
import tr13_guc as G  # noqa: E402
import tr13_sayim as T  # noqa: E402

K = None   # sınanan koşu modülü
YIL = G.YIL
TOHUM_TEST = 20261131


def yukle(yol):
    global K
    spec = importlib.util.spec_from_file_location("tr13b_kosu_sinanan", yol)
    K = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = K          # süreç havuzu işleri adla aktarır (fork)
    spec.loader.exec_module(K)
    return K


# ------------------------------------------------------------------ sahte veri
def ters_izdusum(la0, lo0, x, y):
    r, th = np.hypot(x, y) / 6371.0, np.arctan2(x, y)
    p1, l1 = math.radians(la0), math.radians(lo0)
    p2 = np.arcsin(math.sin(p1) * np.cos(r) + math.cos(p1) * np.sin(r) * np.cos(th))
    l2 = l1 + np.arctan2(np.sin(th) * np.sin(r) * math.cos(p1), np.cos(r) - math.sin(p1) * np.sin(p2))
    lo = (np.degrees(l2) + 180.0) % 360.0 - 180.0
    return np.degrees(p2), lo


def yapay_katalog(rng, R, Nh, f, t_ana, la0, lo0):
    """[t-10y, t) yapay katalog (lat/lon, ms); dallanma 0,6; sinyal [t-3y, t) arka planının f kesri kırık bandında."""
    K.dallanma(0.6)
    F = G.faylar(rng, R)
    R_sim = R + 30
    mu = Nh / (3 * YIL) * (R_sim / R) ** 2
    t, x, y, m, _ = G.etas(rng, R_sim, mu, -5 * YIL, 10 * YIL, F, f_lok=f, lok_t0=7 * YIL)
    k = t >= 0
    la, lo = ters_izdusum(la0, lo0, x[k], y[k])
    tms = t_ana - (10 * YIL - t[k]) * T.GUN_MS
    return dict(t=np.floor(tms), la=la, lo=lo, de=np.full(int(k.sum()), 10.0), m=np.round(m[k], 2))


def npz_bayt(d):
    b = io.BytesIO()
    np.savez_compressed(b, **d)
    return b.getvalue()


def tar_yaz(yol, uyeler):
    with tarfile.open(yol, "w:gz") as tf:
        for ad, b in uyeler.items():
            ti = tarfile.TarInfo(ad)
            ti.size = len(b)
            tf.addfile(ti, io.BytesIO(b))


OLAYLAR = [  # (id, küme, R, N hedefi, katalog) — keşif kümeleri 397, 979, 395; iki çok üyeli küme
    ("ya01", 397, 62, 80, "ComCat"), ("ya02", 397, 75, 70, "ComCat"), ("ya03", 979, 70, 85, "ComCat"),
    ("ya04", 395, 90, 75, "ISC"), ("ya05", 1139, 65, 80, "ISC"), ("ya06", 1139, 58, 70, "ISC"),
    ("ya07", 11, 80, 90, "ISC"), ("ya08", 12, 60, 75, "GeoNet"), ("ya09", 13, 85, 80, "ComCat"),
    ("ya10", 14, 70, 70, "ISC"), ("ya11", 15, 66, 85, "ISC"), ("ya12", 16, 95, 75, "ComCat"),
    ("ya13", 17, 60, 80, "GeoNet"), ("ya14", 18, 72, 90, "ISC"), ("ya15", 19, 64, 70, "ComCat"),
    ("ya16", 20, 78, 80, "ISC"),
]


def sahte_veri(dizin, f=0.0, eksik=(), tohum=TOHUM_TEST):
    """Sahte arşivler + sha listesi + tamsayim.json. eksik: parça üyesi silinecek olay kimlikleri."""
    os.makedirs(dizin, exist_ok=True)
    rng = np.random.default_rng(tohum)
    t_ana0 = float(T.ms_of("2012-06-01T00:00:00"))
    u1, u2, sat, s4 = {}, {}, [], []
    for j, (oid, kume, R, N, kat) in enumerate(OLAYLAR):
        la0, lo0 = 35.0 + 0.7 * j, (170.0 + 1.3 * j + 180) % 360 - 180    # antimeridyen dahil
        t_ana = t_ana0 + j * 37 * T.GUN_MS
        d = yapay_katalog(rng, R, N * 0.93, f, t_ana, la0, lo0)
        if kat == "ComCat":
            u1[f"ham/kat_ComCat_{oid}.npz"] = npz_bayt(d)
        else:
            w = d["t"] >= t_ana - 3 * T.YIL_MS
            u1[f"ham/tam3_{kat}_{oid}.npz"] = npz_bayt({k: v[w] for k, v in d.items()})
            for jj in range(3, 10):
                if oid in eksik and jj == 5:
                    continue
                w = (d["t"] >= t_ana - (jj + 1) * T.YIL_MS) & (d["t"] < t_ana - jj * T.YIL_MS)
                u2[f"ham_tam/parca_{kat}_{oid}_{jj:02d}.npz"] = npz_bayt({k: v[w] for k, v in d.items()})
        s4.append(dict(id=oid, t=t_ana, enlem=la0, boylam=lo0, R=float(R), R_ind=float(R) + 30))
        sat.append(dict(id=oid, zaman=T.iso(int(t_ana))[:10], M=7.0, yer=f"yapay {oid}", kume=kume, R_km=float(R),
                        katalog=kat, mc_once=2.5, N3bg_mc=N, ref_tam=dict(mc=2.5), ref_gecer={"0.1": True, "0.3": True}))
    # listeye girmemesi gerekenler: M < 6,5 ve referans geçmeyen
    sat.append(dict(sat[0], id="yaX1", M=6.3))
    sat.append(dict(sat[0], id="yaX2", ref_gecer={"0.1": False, "0.3": False}))
    u1["ham/sayim_tam_satirlar.json"] = json.dumps(dict(satir=s4)).encode()
    tar_yaz(os.path.join(dizin, "tr13_ham_2026-11-12.tar.gz"), u1)
    tar_yaz(os.path.join(dizin, "tr13_tamsayim_ham_2026-11-12.tar.gz"), u2)
    satirlar = ["sahte liste"]
    for ad in ("tr13_ham_2026-11-12.tar.gz", "tr13_tamsayim_ham_2026-11-12.tar.gz"):
        satirlar += [f"Arşiv: {os.path.join(dizin, ad)} (0 B)", f"  sha256 {K.sha256(os.path.join(dizin, ad))}"]
    open(os.path.join(dizin, "sha.txt"), "w").write("\n".join(satirlar) + "\n")
    json.dump(dict(satir=sat), open(os.path.join(dizin, "tamsayim.json"), "w"))
    return K.Yollar(arsiv_dizin=dizin.rstrip("/") + "/", sha_liste=os.path.join(dizin, "sha.txt"),
                    tamsayim=os.path.join(dizin, "tamsayim.json"), cikti=os.path.join(dizin, "kosu"))


def ayar_test(**kw):
    a = dict(havuz=150, parca=2, kal_deneme=40, b_ref=50, ns_t1=40000, d3_n0=60, d3_nf=50, d3_nb=8000, cekirdek=4)
    a.update(kw)
    return K.Ayar(**a)


# ------------------------------------------------------------------ birim sınamaları
def U1_sabitler():
    assert K.HAVUZ == 2000 and K.PARCA >= 1 and K.KAL_DENEME >= 40 and K.TOL_KAL == 0.05
    assert K.NS_T1 == 200000 and K.DALLANMA == (0.4, 0.6, 0.8) and set(K.KESIF) == {397, 979, 395}
    assert K.ALFA == 0.05 and K.B_REF == 200 and K.Q_V == 0.5 and (K.N_ALT, K.N_UST) == (50, 100)
    assert K.KD_MIN == 8 and (K.D3_FA_UST, K.D3_GUC_ALT, K.D3_F) == (0.05, 0.65, 0.4)
    assert K.tohum_havuz(3, 2) == 20261201 + 3002 and K.tohum_havuz(0, 0) == 20261201
    assert K.tohum_havuz(3, 2, 1) == 20261201 + 3022 and K.tohum_olcu(0) == 20261251
    assert K.TOHUM_T1 == 20260900 and K.TOHUM_D3 == 20260999
    a = K.Ayar()
    assert (a.havuz, a.kal_deneme, a.b_ref, a.ns_t1, a.test_nh_carpan, a.test_d3_sinyal0) == \
        (2000, K.KAL_DENEME, 200, 200000, 1.0, 0.0)
    assert sum(K.parca_boylari(2000, 4)) == 2000 and sum(K.parca_boylari(151, 2)) == 151
    # aynı tohumdan iki parça birbirinden farklı, aynı parça tekrarlanabilir
    a1 = np.random.default_rng(np.random.SeedSequence(5, spawn_key=(0,))).random(3)
    a2 = np.random.default_rng(np.random.SeedSequence(5, spawn_key=(1,))).random(3)
    assert not np.allclose(a1, a2)


def U2_izdusum():
    rng = np.random.default_rng(1)
    for la0, lo0 in ((40.0, 178.5), (-41.0, 174.0), (71.0, -8.0), (18.0, -78.0)):
        x = rng.uniform(-400, 400, 200)
        y = rng.uniform(-400, 400, 200)
        la, lo = ters_izdusum(la0, lo0, x, y)
        x2, y2 = K.izdusum(la0, lo0, la, lo)
        assert np.allclose(np.hypot(x2, y2), T.uzak(la0, lo0, la, lo), atol=1e-6)
        assert np.allclose(x2, x, atol=1e-3) and np.allclose(y2, y, atol=1e-3)
    xe, ye = K.izdusum(0.0, 0.0, np.array([0.0]), np.array([1.0]))
    assert xe[0] > 100 and abs(ye[0]) < 1e-6


def U3_sha(dizin):
    L = K.sha_listesi(os.path.join(TR13, "tr13_ham_sha256.txt"))       # gerçek dosya: yalnız biçim
    assert [a for a, _ in L] == ["tr13_ham_2026-11-12.tar.gz", "tr13_tamsayim_ham_2026-11-12.tar.gz"]
    assert L[0][1].startswith("2e11e7d2") and L[1][1].startswith("7f40414b")
    d = os.path.join(dizin, "u3")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for ad in ("tr13_ham_2026-11-12.tar.gz", "tr13_tamsayim_ham_2026-11-12.tar.gz"):
        tar_yaz(os.path.join(d, ad), {"ham/a.json": b"{}"})
    s = ["x"]
    for ad in ("tr13_ham_2026-11-12.tar.gz", "tr13_tamsayim_ham_2026-11-12.tar.gz"):
        s += [f"Arşiv: {os.path.join(d, ad)} (1 B)", f"  sha256 {K.sha256(os.path.join(d, ad))}"]
    open(os.path.join(d, "sha.txt"), "w").write("\n".join(s))
    y = K.Yollar(arsiv_dizin=d + "/", sha_liste=os.path.join(d, "sha.txt"))
    assert K.sha_denetimi(y)[0] is True
    b = bytearray(open(os.path.join(d, "tr13_ham_2026-11-12.tar.gz"), "rb").read())
    b[-5] ^= 1
    open(os.path.join(d, "tr13_ham_2026-11-12.tar.gz"), "wb").write(bytes(b))
    assert K.sha_denetimi(y)[0] is False
    os.remove(os.path.join(d, "tr13_ham_2026-11-12.tar.gz"))
    assert K.sha_denetimi(y)[0] is False


def _el_katalog(t_ana, la0, lo0, n_once, n_ref, ekstra=True):
    """El yapımı seyrek katalog: olaylar 10 gün arayla (GK74 pencereleri örtüşmez), M 2,5."""
    rng = np.random.default_rng(3)
    T0 = t_ana - 10 * T.YIL_MS
    tt = list(t_ana - (np.arange(n_once) * 10 + 15) * T.GUN_MS)                     # [t-3y, t)
    tt += list(t_ana - 3 * T.YIL_MS - (np.arange(n_ref) * 10 + 15) * T.GUN_MS)       # [t-10y, t-3y)
    tt = [x for x in tt if x >= T0]
    n = len(tt)
    x, y = rng.uniform(-50, 50, n), rng.uniform(-50, 50, n)
    la, lo = ters_izdusum(la0, lo0, x, y)
    d = dict(t=np.array(tt, float), la=la, lo=lo, de=np.full(n, 10.0), m=np.full(n, 2.5))
    if ekstra:   # sınır ve körlük olayları: t-3y'den 1 g önce (referans), ana şokta ve sonrasında, derin, R dışı
        ek_t = [t_ana - 3 * T.YIL_MS - 1 * T.GUN_MS, t_ana, t_ana + 20 * T.GUN_MS, t_ana - 400 * T.GUN_MS - 7e5,
                t_ana - 401 * T.GUN_MS - 9e5]
        ek_la, ek_lo = ters_izdusum(la0, lo0, np.array([0, 0, 0, 0, 300.0]), np.array([0, 0, 0, 0, 0.0]))
        d = {k: np.concatenate([d[k], v]) for k, v in
             dict(t=np.array(ek_t), la=ek_la, lo=ek_lo, de=np.array([10, 10, 10, 60, 10.0]),
                  m=np.full(5, 2.5)).items()}
    return d


def U4_hazirla():
    t_ana = float(T.ms_of("2015-03-01T00:00:00"))
    o = dict(t=t_ana, enlem=40.0, boylam=178.0)
    s = dict(id="u4", yer="u4", kume=1, R_km=80.0, katalog="ComCat", mc_once=2.5, ref_tam=dict(mc=2.4))
    # (d) pencere sınırları ve körlük: 60 önce, 200 referans; +1 referans sınır olayı; derin, ana şok anı/sonrası, R dışı
    oz, bg = K.hazirla(s, o, _el_katalog(t_ana, 40.0, 178.0, 60, 200))
    assert oz["durum"] == "tamam", oz
    assert oz["N3bg"] == 60 and oz["N_ref"] == 201 and oz["mc_ortak"] == 2.5, oz
    assert bg[2].max() < 10 * YIL and bg[2].min() >= 0
    # (b) ortak Mc = max(Mc_önce, Mc_ref)
    oz, _ = K.hazirla(dict(s, ref_tam=dict(mc=2.7)), o, _el_katalog(t_ana, 40.0, 178.0, 60, 200))
    assert oz["mc_ortak"] == 2.7 and oz["N3bg"] == 0 and oz["durum"].startswith("düşer"), oz
    # (c) N < 50 düşer
    oz, bg = K.hazirla(s, o, _el_katalog(t_ana, 40.0, 178.0, 45, 200))
    assert oz["N3bg"] == 45 and oz["durum"].startswith("düşer: N3bg") and bg is None, oz
    # referans yetersiz düşer
    oz, bg = K.hazirla(s, o, _el_katalog(t_ana, 40.0, 178.0, 60, 50, ekstra=False))
    assert oz["durum"].startswith("düşer: referans") and bg is None, oz
    # eksik parça
    oz, bg = K.hazirla(s, o, None)
    assert "veri yok" in oz["durum"] and bg is None
    # (a) doyma: yoğun ETAS kataloğu; son Mc'de N <= 100, bir adım aşağıda (GK74 bağımsız yeniden) N > 100
    rng = np.random.default_rng(11)
    d = yapay_katalog(rng, 80.0, 260.0, 0.0, t_ana, 40.0, 178.0)
    oz, bg = K.hazirla(s, o, d)
    assert oz["mc_son"] > oz["mc_ortak"] and 50 <= oz["N3bg"] <= 100, oz

    def say(mc):
        u = (d["m"] >= mc - 1e-6) & (d["t"] < t_ana)
        b = T.gk74(d["t"][u], d["la"][u], d["lo"][u], d["m"][u])
        r = T.uzak(40.0, 178.0, d["la"][u], d["lo"][u])
        return int(((r <= 80) & b & (d["t"][u] >= t_ana - 3 * T.YIL_MS)).sum())
    assert say(oz["mc_son"]) == oz["N3bg"] and say(round(oz["mc_son"] - 0.1, 2)) > 100


def U5_kalibrasyon_kendi_R():
    gorulen = []
    asil = K.yapay_bolge

    def sarmal(rng, Nh, R, f=0.0, b_ref=K.B_REF, olc=True):
        gorulen.append(R)
        return asil(rng, Nh, R, f, b_ref, olc)
    K.yapay_bolge = sarmal
    try:
        K.dallanma(0.6)
        k = K.kalibre(np.random.default_rng(2), 80.0, 250.0, 3)
    finally:
        K.yapay_bolge = asil
    assert gorulen and all(r == 250.0 for r in gorulen) and k["Nh"] > 0, gorulen
    # istatistik: R = 200'de kalibre μ ile 60 bölgenin ortalama N'si hedefin ±%8'i içinde
    rng = np.random.default_rng(4)
    k = K.kalibre(rng, 80.0, 200.0, 40)
    n = np.mean([K.yapay_bolge(rng, k["Nh"], 200.0, olc=False)[2] for _ in range(60)])
    assert abs(n / 80.0 - 1) < 0.08, (n, k)


def U6_p_ve_R0():
    assert K.p_deger(np.array([0.0, 1, 2, 3]), 1.0) == 0.5
    assert K.p_deger(np.arange(100.0), -1.0) == 0.0 and K.p_deger(np.arange(100.0), 1000.0) == 1.0
    D = K.DALLANMA
    hep = {d: 0.01 for d in D}
    assert K.karar(hep, hep) is True
    assert K.karar({d: 0.05 for d in D}, {d: 0.05 for d in D}) is True
    assert K.karar({**hep, 0.8: 0.06}, hep) is False
    assert K.karar(hep, {**hep, 0.4: 0.06}) is False
    assert K.karar({**hep, 0.4: 0.06}, {**hep, 0.4: 0.06}) is False
    # r0_oran = karar'ın vektör biçimi
    rng = np.random.default_rng(5)
    Sa = {d: np.sort(rng.normal(0, 1, 5000)) for d in D}
    Sk = {d: np.sort(rng.normal(0.1 * i, 1, 5000)) for i, d in enumerate(D)}
    Va, Vk = rng.normal(-1.5, 1, 400), rng.normal(-1.5, 1, 400)
    beklenen = np.mean([K.karar({d: K.p_deger(Sa[d], a) for d in D}, {d: K.p_deger(Sk[d], b) for d in D})
                        for a, b in zip(Va, Vk)])
    assert abs(K.r0_oran(Sa, Sk, Va, Vk) - beklenen) < 1e-12
    assert K.mde([0, 0.2, 0.4], [0.02, 0.4, 0.9]) == 0.36 and K.mde([0, 0.2], [0.02, 0.5]) is None


def U7_plasebo_baglamaz():
    D = K.DALLANMA
    hep = {d: 0.01 for d in D}
    a = K.hukum_kur(hep, hep, 0.01, 10, "f ≈ 0,40")
    b = K.hukum_kur(hep, hep, 0.90, 10, "f ≈ 0,40")
    assert a[:2] == b[:2] == (3, "VAR")
    assert "Aynı bölgelerin 3 yıl önceki penceresi de ETAS'a göre yerelleşmiş" in a[2]
    assert "Aynı bölgelerin" not in b[2]
    assert a[2].startswith("BZ20'nin keşif olayları dışındaki K = 10 bölgede")
    c = K.hukum_kur({**hep, 0.6: 0.2}, hep, 0.9, 10, "f ≈ 0,40")
    assert c[:2] == (5, "ayırt edilemez") and "f ≈ 0,40" in c[2] and "H0" not in c[2]
    assert "Daha küçük yerelleşme hakkında bilgi yok" in c[2]
    assert K.mde_metni(None).startswith("f > 0,6") and K.mde_metni(0.4) == "f ≈ 0,40"


def U8_kume_ortalamasi():
    assert K.kume_ort({0: 0.0, 1: 0.0, 2: 3.0}, [[0, 1], [2]]) == 1.5
    hv = {0: np.zeros((10, 3)), 1: np.zeros((10, 3)), 2: np.full((10, 3), 3.0)}
    hv[1][:, 0] = 2.0
    S = K.sifir_cekilis(np.random.default_rng(1), hv, [[0, 1], [2]], 1000)
    assert S.shape == (1000, 2, 2) and np.allclose(S[:, 0, 0], 1.0) and np.allclose(S[:, :, 0].mean(1), 2.0)
    assert np.allclose(S[:, 1, 1], 3.0)


def U9_kume_yapisi():
    kum, kids, kd = K.kume_yapisi([(0, 397), (1, 397), (2, 5), (3, 979), (4, 6), (5, 395), (6, 6)])
    assert kids == [5, 6, 395, 397, 979] and kum == [[2], [4, 6], [5], [0, 1], [3]] and kd == [0, 1]
    # üye düşerse küme kalan üyeyle sürer; küme boşalırsa düşer
    kum, kids, kd = K.kume_yapisi([(1, 397), (2, 5)])
    assert kum == [[2], [1]] and kids == [5, 397] and kd == [0]


def U10_kilit(dizin):
    d = os.path.join(dizin, "u10")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    K._yaz_hukum(d, dict(hukum="ilk"))
    try:
        K._yaz_hukum(d, dict(hukum="ikinci"))
        raise AssertionError("hüküm iki kez yazıldı")
    except FileExistsError:
        pass
    assert json.load(open(os.path.join(d, "tr13b_hukum.json")))["hukum"] == "ilk"
    y = K.Yollar(arsiv_dizin="/yok/", sha_liste="/yok/sha.txt", tamsayim="/yok/t.json", cikti=d)
    h = K.kos(K.Ayar(), y, gunluk=lambda *a: None)
    assert h["hukum"] == "ilk" and not os.path.exists(os.path.join(d, "durum.json"))


def U14_kal_tol():
    assert K.kal_tamam(104.0, 100) and K.kal_tamam(95.5, 100)
    assert not K.kal_tamam(106.0, 100) and not K.kal_tamam(94.0, 100)
    assert K.d3_gecer(0.04, 0.70) and K.d3_gecer(0.05, 0.65)
    assert not K.d3_gecer(0.06, 0.9) and not K.d3_gecer(0.02, 0.6)


def birim(dizin):
    out = {}
    for ad, fn in (("U1", U1_sabitler), ("U2", U2_izdusum), ("U3", lambda: U3_sha(dizin)), ("U4", U4_hazirla),
                   ("U5", U5_kalibrasyon_kendi_R), ("U6", U6_p_ve_R0), ("U7", U7_plasebo_baglamaz),
                   ("U8", U8_kume_ortalamasi), ("U9", U9_kume_yapisi), ("U10", lambda: U10_kilit(dizin)),
                   ("U14", U14_kal_tol)):
        t0 = time.time()
        try:
            fn()
            out[ad] = dict(gecti=True)
        except Exception as e:  # noqa
            out[ad] = dict(gecti=False, hata=f"{type(e).__name__}: {str(e)[:300]}")
        out[ad]["s"] = round(time.time() - t0, 1)
    return out


# ------------------------------------------------------------------ uçtan uca
def E_kos(dizin, ad, f=0.0, eksik=(), bozuk_sha=False, **ayar):
    d = os.path.join(dizin, ad)
    shutil.rmtree(d, ignore_errors=True)
    y = sahte_veri(d, f=f, eksik=eksik)
    if bozuk_sha:
        p = os.path.join(d, "tr13_tamsayim_ham_2026-11-12.tar.gz")
        b = bytearray(open(p, "rb").read())
        b[len(b) // 2] ^= 0xFF
        open(p, "wb").write(bytes(b))
    t0 = time.time()
    h = K.kos(ayar_test(**ayar), y, gunluk=lambda *a: None)
    z_var = os.path.exists(os.path.join(y.cikti, "gercek_z.json"))
    return h, z_var, round(time.time() - t0, 1), y


def uctan(dizin, sec=None):
    out = {}

    def kayit(ad, kosul, h, z_var, s, **ek):
        out[ad] = dict(gecti=bool(kosul), hukum=h.get("hukum"), dal=h.get("dal"), neden=h.get("neden"),
                       gercek_z_hesaplandi=z_var, s=s, p_butun=h.get("p_butun"), p_kesif_disi=h.get("p_kesif_disi"),
                       D3=h.get("D3"), K_kd=h.get("K_kesif_disi"), cumle=h.get("cumle"), **ek)

    if sec is None or "E1" in sec:
        h, z, s, _ = E_kos(dizin, "E1_sinyalsiz")
        kayit("E1_sinyalsiz", h["hukum"] == "ayırt edilemez" and h["dal"] == 5 and z
              and "en küçük etki f" in h["cumle"] and "H0" not in json.dumps(h, ensure_ascii=False), h, z, s)
    if sec is None or "E2" in sec:
        h, z, s, _ = E_kos(dizin, "E2_f05", f=0.5)
        kayit("E2_f05", h["hukum"] == "VAR" and h["dal"] == 3 and z, h, z, s)
    if sec is None or "E3a" in sec:
        h, z, s, y = E_kos(dizin, "E3a_sha", bozuk_sha=True)
        bos = not os.listdir(os.path.join(y.cikti, "havuz"))
        kayit("E3a_sha", h["hukum"] == "veri yok" and h["dal"] == 1 and not z and bos, h, z, s)
    if sec is None or "E3b" in sec:
        # 5 ISC/GeoNet keşif dışı olayın referans parçası eksik -> keşif dışı K = 11 - 5 = 6 < 8
        ek = ("ya07", "ya08", "ya10", "ya11", "ya13")
        h, z, s, y = E_kos(dizin, "E3b_eksik", eksik=ek)
        bos = not os.listdir(os.path.join(y.cikti, "havuz"))
        kayit("E3b_eksik_parca", h["hukum"] == "veri yok" and h["dal"] == 1 and not z and bos, h, z, s)
    if sec is None or "E3c" in sec:
        h, z, s, _ = E_kos(dizin, "E3c_kal", test_nh_carpan=1.4)
        kayit("E3c_kalibrasyon_bozuk", h["hukum"] == "geçersiz" and h["dal"] == 2 and not z, h, z, s)
    if sec is None or "E3d" in sec:
        h, z, s, y = E_kos(dizin, "E3d_d3", test_d3_sinyal0=0.4)
        kayit("E3d_D3_bozuk", h["hukum"] == "geçersiz" and h["dal"] == 2 and not z, h, z, s)
        # kilit: aynı dizinde ikinci koşu hiçbir şey hesaplamaz, hüküm dosyası değişmez
        hp = os.path.join(y.cikti, "tr13b_hukum.json")
        m0, b0 = os.path.getmtime(hp), open(hp, "rb").read()
        t0 = time.time()
        h2 = K.kos(ayar_test(), y, gunluk=lambda *a: None)
        kayit("E3e_kilit", h2 == json.loads(b0) and open(hp, "rb").read() == b0 and os.path.getmtime(hp) == m0
              and time.time() - t0 < 2, h2, z, round(time.time() - t0, 2))
    return out


# ------------------------------------------------------------------ mutasyonlar
MUTASYON = [  # (ad, eski, yeni, ek uçtan uca sınamalar)
    ("M01 R0 've' -> 'veya' (iki liste)", ") and all(p_k[d] <= ALFA", ") or all(p_k[d] <= ALFA", ()),
    ("M02 bütün liste eşiği 0,10", "all(p_a[d] <= ALFA", "all(p_a[d] <= 2 * ALFA", ()),
    ("M03 kalibrasyon R = 80 (K1)", "yapay_bolge(rng, Nh, R, 0.0, olc=False)",
     "yapay_bolge(rng, Nh, 80.0, 0.0, olc=False)", ()),
    ("M04 plasebo hükmü bağlar", "    if karar(p_a, p_k):\n        return 3",
     "    if karar(p_a, p_k) and (p_pl is None or p_pl > ALFA):\n        return 3", ()),
    ("M05 keşif kümeleri dışlanmaz", "if kk not in KESIF]", "if True]", ()),
    ("M06 sha256 denetimi atlanır", "tamam = tamam and g == h", "tamam = tamam", ()),
    ("M07 hüküm üzerine yazılabilir", 'h, kip="x")', 'h, kip="w")', ()),
    ("M08 kilit denetimi yok", "    if os.path.exists(hyol):\n        gunluk(",
     "    if False:\n        gunluk(", ()),
    ("M09 kuyruk yönü ters", "return float(np.mean(sifir <= gozlenen))",
     "return float(np.mean(sifir >= gozlenen))", ()),
    ("M10 küme yerine üye ortalaması", "return float(np.mean([np.mean([z_uye[u] for u in k]) for k in kumeler]))",
     "return float(np.mean([z_uye[u] for k in kumeler for u in k]))", ()),
    ("M11 düşme eşiği 30", "    if N < N_ALT:", "    if N < 30:", ()),
    ("M12 D-3 kapısı yok (gerçek z D-3 başarısızken)", "    if not d3[\"gecer\"]:", "    if False:", ("E3d",)),
    ("M13 tohum formülü", "return TOHUM0 + 1000 * i + di + 20 * deneme",
     "return TOHUM0 + 100 * i + di + 20 * deneme", ()),
    ("M14 kalibrasyon toleransı ±%10", "return abs(ort_n / N - 1.0) <= TOL_KAL",
     "return abs(ort_n / N - 1.0) <= 2 * TOL_KAL", ()),
    ("M15 önce-pencere 2 yıl", "N = int((ic & bg & (tt >= t_ana - 3 * YIL_MS)).sum())",
     "N = int((ic & bg & (tt >= t_ana - 2 * YIL_MS)).sum())", ()),
    ("M16 veri yok eşiği keşif dışı K < 5", "    if len(kd) < KD_MIN:", "    if len(kd) < 5:", ("E3b",)),
    ("M17 ortak Mc = min", "mc = max(mc0, mcr)", "mc = min(mc0, mcr)", ()),
    ("M18 D-3 güç eşiği 0,55", "guc_f04 >= D3_GUC_ALT)", "guc_f04 >= D3_GUC_ALT - 0.1)", ()),
    ("M19 doyma eşiği 150", "        if N > N_UST:", "        if N > 1.5 * N_UST:", ()),
    ("M20 körlük süzgeci yok (ana şok anı ve sonrası)", "(d[\"t\"] < t_ana) & (d[\"t\"] < T.KOR_MS)",
     "(d[\"t\"] <= t_ana + 30 * GUN_MS)", ()),
]


def mutasyon(dizin, kaynak):
    metin = open(kaynak).read()
    out = []
    for ad, eski, yeni, ek in MUTASYON:
        assert metin.count(eski) == 1, ("mutasyon dizgisi bir kez geçmeli", ad, metin.count(eski))
        md = os.path.join(dizin, "mut", ad[:3])
        shutil.rmtree(md, ignore_errors=True)
        os.makedirs(md)
        yol = os.path.join(md, "tr13b_kosu.py")
        open(yol, "w").write(metin.replace(eski, yeni))
        t0 = time.time()
        kipler = ["birim"] + (["uctan:" + ",".join(ek)] if ek else [])
        dusen = []
        for kip in kipler:
            r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__), md, kip, "--modul", yol],
                               capture_output=True, text=True, timeout=1800)
            ozet = json.load(open(os.path.join(md, f"test_{kip.split(':')[0]}.json")))
            dusen += [k for k, v in ozet["sonuc"].items() if not v["gecti"]]
            assert r.returncode in (0, 1), r.stderr[-2000:]
        out.append(dict(mutasyon=ad, yakalandi=bool(dusen), dusen_sinamalar=dusen, s=round(time.time() - t0, 1)))
        print(ad, "YAKALANDI" if dusen else "KAÇTI", dusen, flush=True)
        shutil.rmtree(md, ignore_errors=True)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    dizin, kip = os.path.abspath(a[0]), a[1]
    modul = a[a.index("--modul") + 1] if "--modul" in a else os.path.join(BURA, "tr13b_kosu.py")
    yukle(modul)
    os.makedirs(dizin, exist_ok=True)
    t0 = time.time()
    if kip == "birim":
        sonuc = birim(dizin)
    elif kip.startswith("uctan"):
        sonuc = uctan(dizin, kip.split(":")[1].split(",") if ":" in kip else None)
    elif kip == "mutasyon":
        sonuc = mutasyon(dizin, modul)
    else:
        sys.exit(__doc__)
    ozet = dict(kip=kip, modul_sha256=K.sha256(modul), sure_s=round(time.time() - t0, 1), sonuc=sonuc)
    json.dump(ozet, open(os.path.join(dizin, f"test_{kip.split(':')[0]}.json"), "w"), indent=1, ensure_ascii=False,
              default=float)
    print(json.dumps(ozet, indent=1, ensure_ascii=False, default=float))
    if kip != "mutasyon":
        sys.exit(0 if all(v["gecti"] for v in sonuc.values()) else 1)
