#!/usr/bin/env python3
"""TR-13b koşu betiğinin bağımsız kod incelemesi: ek sınamalar (yalnız yapay; gerçek katalogda ölçü YOK).

  birim      Y-birim: tohum formülleri, körlük sınırı (2026-01-01, "<"), küme içi bağımsız çekiliş, r0_oran'ın üç
             dallanmayı birden istemesi, gerçek kip kapısı (dondurulmus_mu) ve kos()'un kendi kapısı.
  uctan      Y-uçtan: küçük ayarla bir sahte koşu (f = 0,25); p'ler, z̄'ler, K'ler, havuz boyları, D-3 kapısı, cümle
             havuz dosyalarından BAĞIMSIZ yeniden hesaplanır; sonra kesinti/sürdürme (gercek_z yeniden kullanılır).
             Ayrıca keşif dışı K = 8 sınırı (koşu sürmeli).
  seri       Uçtan uca yanlış alarm / güç serisi: <n> bağımsız sahte liste, f verilen (tohum 20261300 + j).
  mutasyon   Y-mutasyonlar (yazarınkilerden farklı); her biri birim + uçtan uca Y sınamalarıyla.

Kullanım: python3 -I -B tr13b_kodinc.py <karalama> <kip> [--modul <tr13b_kosu.py>] [--n N] [--f F] [--havuz H]
"""
import json
import os
import shutil
import subprocess
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
TR13B = "/home/user/knotenlinie/kayit/turetme/tr13b"
sys.path.insert(0, TR13B)
import tr13b_test_yapay as TY  # noqa: E402  (sahte veri üreteci; yazarın)

K = None
T = TY.T


YASAK = "/mnt/project-files"
TOL_SINAMA = 0.15


def koru():
    """Bu süreçte gerçek arşive (ve ağ bağlamasına) dokunan her açma girişimi hata verir: tarfile, sha256, open."""
    import builtins
    import tarfile as _tf
    ao, to, so = builtins.open, _tf.open, K.sha256

    def _yasak(p):
        return isinstance(p, (str, bytes, os.PathLike)) and os.path.realpath(os.fsdecode(p)).startswith(YASAK)

    def open_(p, *a, **k):
        if _yasak(p):
            raise RuntimeError("KORUMA: gerçek arşiv açılmaya çalışıldı: " + str(p))
        return ao(p, *a, **k)

    def tfo(name=None, *a, **k):
        if _yasak(name):
            raise RuntimeError("KORUMA: gerçek arşiv (tar) açılmaya çalışıldı: " + str(name))
        return to(name, *a, **k)

    def sha_(p):
        if _yasak(p):
            raise RuntimeError("KORUMA: gerçek arşivin sha256'sı istendi: " + str(p))
        return so(p)
    builtins.open, _tf.open, K.sha256 = open_, tfo, sha_


def ayar_kucuk(**kw):
    a = dict(havuz=150, parca=2, kal_deneme=40, b_ref=50, ns_t1=40000, d3_n0=60, d3_nf=50, d3_nb=8000, cekirdek=4)
    a.update(kw)
    return K.Ayar(**a)


def ayar_minik(**kw):
    a = dict(havuz=6, parca=2, kal_deneme=2, b_ref=8, ns_t1=2000, d3_n0=4, d3_nf=4, d3_nb=500, cekirdek=4)
    a.update(kw)
    return K.Ayar(**a)


# ------------------------------------------------------------------ birim
def Y1_tohumlar():
    b = 20261201
    for i in (0, 3, 15):
        for di in (0, 1, 2):
            assert K.tohum_havuz(i, di) == b + 1000 * i + di
            assert K.tohum_havuz(i, di, 1) == b + 1000 * i + 20 + di
            assert K.tohum_kal(i, di) == b + 1000 * i + 10 + di
        assert K.tohum_olcu(i) == b + 1000 * i + 50
        for k in range(6):
            assert K.tohum_veri(i, k) == b + 1000 * i + 60 + k
    # tohumlar çakışmaz (olay 0–15, bütün türler)
    s = [K.tohum_havuz(i, di, r) for i in range(16) for di in range(3) for r in (0, 1)]
    s += [K.tohum_kal(i, di) for i in range(16) for di in range(3)] + [K.tohum_olcu(i) for i in range(16)]
    s += [K.tohum_veri(i, k) for i in range(16) for k in range(6)] + [K.tohum_veri_kal(i) for i in range(16)]
    assert len(s) == len(set(s))
    assert K.TOHUM_T1 == 20260900 and K.NS_T1 == 200000 and K.HAVUZ == 2000 and K.PARCA == 4


def Y2_korluk():
    """Ana şok 2026-03-01 (yalnız sınama): 2026-01-01T00:00:00 ve sonrası sayılmaz; 2025-12-31T23:59:59.999 sayılır."""
    t_ana = float(T.ms_of("2026-03-01T00:00:00"))
    la0, lo0 = 40.0, 20.0
    kor = float(T.KOR_MS)
    tt = [kor - 1.0, kor, kor + 1.0, kor + 10 * T.GUN_MS]          # hepsi önce-pencerede
    tt += list(t_ana - 3 * T.YIL_MS - (np.arange(200) * 10 + 15) * T.GUN_MS)  # referans
    tt += list(kor - (np.arange(55) * 10 + 20) * T.GUN_MS)          # önce-pencere, körlük öncesi
    n = len(tt)
    rng = np.random.default_rng(9)
    la, lo = TY.ters_izdusum(la0, lo0, rng.uniform(-50, 50, n), rng.uniform(-50, 50, n))
    d = dict(t=np.array(tt, float), la=la, lo=lo, de=np.full(n, 10.0), m=np.full(n, 2.5))
    s = dict(id="y2", yer="y2", kume=1, R_km=80.0, katalog="ComCat", mc_once=2.5, ref_tam=dict(mc=2.5))
    oz, bg = K.hazirla(s, dict(t=t_ana, enlem=la0, boylam=lo0), d)
    assert oz["N3bg"] == 56, oz       # 55 + (kor - 1 ms); kor, kor+1, kor+10 g düşer
    assert bg is not None and bg[2].max() < (kor - (t_ana - 10 * T.YIL_MS)) / T.GUN_MS


def Y3_kume_cekilis_bagimsiz():
    rng = np.random.default_rng(3)
    hv = {0: np.c_[rng.normal(0, 1, 4000), np.zeros(4000), np.zeros(4000)],
          1: np.c_[rng.normal(0, 1, 4000), np.zeros(4000), np.zeros(4000)]}
    S = K.sifir_cekilis(np.random.default_rng(1), hv, [[0, 1]], 40000)
    v = S[:, 0, 0].var()
    assert 0.45 < v < 0.55, v        # bağımsız iki üyenin ortalaması: var 0,5 (ortak çekilişte 1'e yakın)
    # z ve z_p aynı bölgeden
    hv2 = {0: np.c_[np.arange(100.0), np.arange(100.0) + 0.5, np.zeros(100)]}
    S2 = K.sifir_cekilis(np.random.default_rng(2), hv2, [[0]], 1000)
    assert np.allclose(S2[:, 0, 1] - S2[:, 0, 0], 0.5)


def Y4_r0_uc_dallanma():
    D = K.DALLANMA
    base = np.sort(np.random.default_rng(1).normal(0, 1, 20000))
    for kotu in D:     # yalnız bir dallanmanın sıfırı çok sola kaymış: o dallanmada p büyük -> red yok
        Sa = {d: base for d in D}
        Sk = {d: base for d in D}
        Sa = {**Sa, kotu: base - 5.0}
        Va, Vk = np.full(50, -3.0), np.full(50, -3.0)
        assert K.r0_oran(Sa, Sk, Va, Vk) == 0.0, kotu
        Sk2 = {**{d: base for d in D}, kotu: base - 5.0}
        assert K.r0_oran({d: base for d in D}, Sk2, Va, Vk) == 0.0, kotu
    assert K.r0_oran({d: base for d in D}, {d: base for d in D}, np.full(5, -3.0), np.full(5, -3.0)) == 1.0
    # p_vektor = p_deger
    z = np.array([-2.0, -1.0, 0.0, 0.3])
    assert np.allclose(K.p_vektor(base, z), [K.p_deger(base, v) for v in z])


def Y5_kapi(dizin):
    ok, neden = K.dondurulmus_mu()
    assert ok is False and "dondurulmamış" in neden, neden
    metin = open(K.ONKAYIT, encoding="utf-8").read()
    d = os.path.join(dizin, "y5")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    asil = K.ONKAYIT
    try:
        # Durum satırı DONDURULDU, sha'lar yazılı -> True
        m1 = metin.replace("Durum: **TASLAK (sürüm 3). Dondurulmadı.", "Durum: **DONDURULDU (sürüm 3).", 1)
        assert m1 != metin
        p = os.path.join(d, "o1.md"); open(p, "w", encoding="utf-8").write(m1)
        K.ONKAYIT = p
        sha = K.kod_sha()
        if all(v in m1 for v in sha.values()):
            assert K.dondurulmus_mu()[0] is True
        # betik sha'sı metinden silinirse -> False
        m2 = m1
        for v in sha.values():
            m2 = m2.replace(v, "0" * 64)
        p = os.path.join(d, "o2.md"); open(p, "w", encoding="utf-8").write(m2)
        K.ONKAYIT = p
        assert K.dondurulmus_mu()[0] is False
        # DONDURULDU yalnız başka bir satırda -> False
        m3 = metin + "\nDONDURULDU\n"
        p = os.path.join(d, "o3.md"); open(p, "w", encoding="utf-8").write(m3)
        K.ONKAYIT = p
        assert K.dondurulmus_mu()[0] is False
    finally:
        K.ONKAYIT = asil
    # kos()'un kendi kapısı. GERÇEK ARŞİVE DOKUNMADAN: modülün "gerçek" sabitleri boş bir sahte dizine çevrilir;
    # kapı yoksa kos sahte dizinde 'veri yok' yazar (gerçek arşiv hiç açılmaz) ve sınama düşer.
    sahte = os.path.join(d, "sahte_gercek") + "/"
    os.makedirs(sahte)
    open(os.path.join(sahte, "sha.txt"), "w").write("yok\n")
    asil_a, asil_s = K.ARSIV_DIZIN, K.SHA_LISTE
    K.ARSIV_DIZIN, K.SHA_LISTE = sahte, os.path.join(sahte, "sha.txt")
    try:
        for ad, y, g in (("k1", K.Yollar(arsiv_dizin="/yok/", sha_liste="/yok/s", tamsayim="/yok/t",
                                         cikti=os.path.join(d, "k1")), True),
                         ("k2", K.Yollar(arsiv_dizin=sahte, sha_liste="/yok/s", tamsayim="/yok/t",
                                         cikti=os.path.join(d, "k2")), False),
                         ("k3", K.Yollar(arsiv_dizin="/yok/", sha_liste=K.SHA_LISTE, tamsayim="/yok/t",
                                         cikti=os.path.join(d, "k3")), False)):
            try:
                K.kos(K.Ayar(), y, gercek=g, gunluk=lambda *a: None)
                raise AssertionError(f"{ad}: kos() dondurulmamış ön kayıtla gerçek kipte reddetmedi")
            except (SystemExit, FileNotFoundError, OSError) as e:
                if not isinstance(e, SystemExit):
                    raise AssertionError(f"{ad}: kapı yok, girdi açılmaya çalışıldı ({type(e).__name__})")
            assert not os.path.exists(os.path.join(d, ad)), ad
    finally:
        K.ARSIV_DIZIN, K.SHA_LISTE = asil_a, asil_s


def Y6_havuz_suzgeci():
    h = np.array([[np.nan, 0, 60], [1.0, np.nan, 60], [2.0, 1, 40], [3.0, 1, 60], [4.0, 1, 50]])
    assert K.sonlu_z(h)[:, 0].tolist() == [1.0, 3.0, 4.0], K.sonlu_z(h)
    assert K.sonlu(h)[:, 0].tolist() == [3.0, 4.0], K.sonlu(h)


def birim(dizin):
    out = {}
    for ad, fn in (("Y1", Y1_tohumlar), ("Y2", Y2_korluk), ("Y3", Y3_kume_cekilis_bagimsiz),
                   ("Y4", Y4_r0_uc_dallanma), ("Y5", lambda: Y5_kapi(dizin)), ("Y6", Y6_havuz_suzgeci)):
        t0 = time.time()
        try:
            fn()
            out[ad] = dict(gecti=True)
        except Exception as e:  # noqa
            out[ad] = dict(gecti=False, hata=f"{type(e).__name__}: {str(e)[:300]}")
        out[ad]["s"] = round(time.time() - t0, 1)
    return out


# ------------------------------------------------------------------ bağımsız yeniden hesap
def yeniden_hesap(h, y, ayar):
    """Hüküm dosyasındaki sayıları havuz dosyalarından ve gercek_z.json'dan bağımsız kurar ve karşılaştırır."""
    hata = []
    sat = {s["id"]: s for s in json.load(open(y.tamsayim))["satir"]}
    L = [s for s in json.load(open(y.tamsayim))["satir"] if s["M"] >= 6.5 and s["ref_gecer"]["0.3"]]
    Z = {int(k): v for k, v in json.load(open(os.path.join(y.cikti, "gercek_z.json"))).items()}
    uye = sorted(i for i in Z if np.isfinite(Z[i]["z"]))
    kume = {i: L[i]["kume"] for i in uye}
    kids = sorted(set(kume.values()))
    kum = [[i for i in uye if kume[i] == k] for k in kids]
    kd = [j for j, k in enumerate(kids) if k not in (397, 979, 395)]
    if h["K_ana"] != len(kum) or h["K_kesif_disi"] != len(kd):
        hata.append(("K", h["K_ana"], len(kum), h["K_kesif_disi"], len(kd)))
    if f"K = {len(kd)}" not in h["cumle"]:
        hata.append(("cumle K", h["cumle"][:80]))
    kal = h["bilgi"]["kalibrasyon"]
    havuz = {}
    for i in sorted(Z):
        for di in range(3):
            r = 0 if kal[f"{i}_{di}"]["tamam0"] else 1
            parc = [np.load(os.path.join(y.cikti, "havuz", f"s{i:02d}_{di}_{r}_p{p}.npy")) for p in range(ayar.parca)]
            a = np.concatenate(parc)
            if len(a) != ayar.havuz:
                hata.append(("havuz boyu", i, di, len(a)))
            if abs(a[:, 2].mean() / [o for o in h["hazirlik"]["olay"] if o["sira"] == i][0]["N3bg"] - 1) > K.TOL_KAL + 1e-9:
                hata.append(("±%5", i, di))
            havuz[(i, di)] = a[np.isfinite(a[:, 0]) & (a[:, 2] >= 50)]   # z tanımlı, N >= 50 (gerçek üye gibi)
    zbar_a = np.mean([np.mean([Z[i]["z"] for i in k]) for k in kum])
    zbar_k = np.mean([np.mean([Z[i]["z"] for i in kum[j]]) for j in kd])
    if not (np.isclose(zbar_a, h["z_bar"]["butun"]) and np.isclose(zbar_k, h["z_bar"]["kesif_disi"])):
        hata.append(("z̄", zbar_a, zbar_k, h["z_bar"]))
    p_a, p_k = {}, {}
    for di, d in enumerate((0.4, 0.6, 0.8)):
        rng = np.random.default_rng(20260900 + di)
        S = np.zeros((ayar.ns_t1, len(kum)))
        for j, k in enumerate(kum):
            for u in k:
                hh = havuz[(u, di)]
                S[:, j] += hh[rng.integers(0, len(hh), ayar.ns_t1)][:, 0]
            S[:, j] /= len(k)
        p_a[d] = float(np.mean(S.mean(1) <= zbar_a))
        p_k[d] = float(np.mean(S[:, kd].mean(1) <= zbar_k))
        if not (np.isclose(p_a[d], h["p_butun"][str(d)]) and np.isclose(p_k[d], h["p_kesif_disi"][str(d)])):
            hata.append(("p", d, p_a[d], h["p_butun"][str(d)], p_k[d], h["p_kesif_disi"][str(d)]))
    var = all(p_a[d] <= 0.05 for d in p_a) and all(p_k[d] <= 0.05 for d in p_k)
    if (h["hukum"] == "VAR") != var or h["dal"] != (3 if var else 5):
        hata.append(("R0", h["hukum"], var))
    d3 = h["D3"]
    if d3["gecer"] != (d3["yanlis_alarm"] <= 0.05 and d3["guc"]["0.4"] >= 0.65):
        hata.append(("D3 kapısı", d3))
    return hata, dict(p_a=p_a, p_k=p_k, zbar=(zbar_a, zbar_k), K=(len(kum), len(kd)))


def uctan(dizin, f=0.25):
    out = {}
    d = os.path.join(dizin, "Yu")
    shutil.rmtree(d, ignore_errors=True)
    y = TY.sahte_veri(d, f=f, tohum=20261317)
    a = ayar_kucuk(d3_n0=40, d3_nf=30)
    K.TOL_KAL = TOL_SINAMA      # yalnız sınama: küçük havuzda ±%5 rastlantıyla tutmaz (bkz. rapor)
    ob = os.environ.get("KODINC_ONBELLEK")       # yalnız havuz dosyaları + kalibrasyon (deterministik tohumlar)
    if ob and os.path.isdir(ob):
        os.makedirs(y.cikti, exist_ok=True)
        shutil.copytree(os.path.join(ob, "havuz"), os.path.join(y.cikti, "havuz"))
        dd = json.load(open(os.path.join(ob, "durum.json")))
        json.dump(dict(asama=[], baslangic=0, kal=dd["kal"]), open(os.path.join(y.cikti, "durum.json"), "w"))
    t0 = time.time()
    cagri = []
    asil_g = K.d3_gecer
    K.d3_gecer = lambda fa, g: (cagri.append((fa, g)), asil_g(fa, g))[1]
    try:
        h = K.kos(a, y, gunluk=lambda *x: None)
        K.d3_gecer = asil_g
        if cagri != [(h["D3"]["yanlis_alarm"], h["D3"]["guc"]["0.4"])]:
            out["Yu4_D3_kapisi_f04"] = dict(gecti=False, hata=str(cagri)[:200])
        else:
            out["Yu4_D3_kapisi_f04"] = dict(gecti=True)
        if h.get("dal") not in (3, 5):
            out["Yu1_yeniden_hesap"] = dict(gecti=False, hata=f"beklenmeyen dal {h.get('dal')} {h.get('neden')}")
        else:
            hata, b = yeniden_hesap(h, y, a)
            out["Yu1_yeniden_hesap"] = dict(gecti=not hata, hata=str(hata)[:600], bagimsiz=str(b)[:400],
                                            hukum=h["hukum"], s=round(time.time() - t0, 1))
            # sürdürme: hüküm silinir (yalnız sınama), aynı komut: gercek_z yeniden kullanılmalı, sonuç aynı
            zy = os.path.join(y.cikti, "gercek_z.json")
            zb, zm = open(zy, "rb").read(), os.path.getmtime(zy)
            os.remove(os.path.join(y.cikti, "tr13b_hukum.json"))
            try:
                h2 = K.kos(a, y, gunluk=lambda *x: None)
                ayni = (h2["p_butun"] == h["p_butun"] and h2["p_kesif_disi"] == h["p_kesif_disi"]
                        and open(zy, "rb").read() == zb and os.path.getmtime(zy) == zm and h2["D3"] == h["D3"])
                out["Yu2_surdurme"] = dict(gecti=bool(ayni))
            except Exception as e:  # noqa
                out["Yu2_surdurme"] = dict(gecti=False, hata=f"{type(e).__name__}: {e}"[:300])
    except Exception as e:  # noqa
        out["Yu1_yeniden_hesap"] = dict(gecti=False, hata=f"{type(e).__name__}: {e}"[:300])
    # keşif dışı K = 8 sınırı: 3 keşif dışı ISC/GeoNet olayında referans parçası eksik -> 11 - 3 = 8, koşu sürmeli
    d = os.path.join(dizin, "Yk8")
    shutil.rmtree(d, ignore_errors=True)
    y = TY.sahte_veri(d, tohum=20261318)
    L, s4, A = K.girdi(y)
    tam = [i for i, s in enumerate(L) if K.hazirla(s, s4[s["id"]], K.katalog(s, A))[1] is not None]
    kids = sorted({L[i]["kume"] for i in tam})
    kd0 = [k for k in kids if k not in K.KESIF]
    tek = [L[i]["id"] for i in tam if L[i]["kume"] in kd0 and L[i]["katalog"] != "ComCat"
           and sum(L[j]["kume"] == L[i]["kume"] for j in tam) == 1]
    assert len(kd0) - 8 <= len(tek) and len(kd0) >= 8, (len(kd0), tek)
    shutil.rmtree(d, ignore_errors=True)
    y = TY.sahte_veri(d, eksik=tuple(tek[:len(kd0) - 8]), tohum=20261318)
    try:
        h = K.kos(ayar_minik(), y, gunluk=lambda *x: None)
        kk = h.get("hazirlik", {}).get("K_kesif_disi")
        out["Yu3_K8_surer"] = dict(gecti=bool(kk == 8 and not (h["dal"] == 1 and "keşif dışı K = 8" in (h.get("neden") or ""))),
                                   dal=h.get("dal"), neden=h.get("neden"), K_kd=kk)
    except Exception as e:  # noqa
        out["Yu3_K8_surer"] = dict(gecti=False, hata=f"{type(e).__name__}: {e}"[:300])
    return out


# ------------------------------------------------------------------ seri (yanlış alarm / güç)
def seri(dizin, n, f, havuz):
    out = []
    bas = int(os.environ.get("KODINC_SERI_BAS", "0"))
    for j in range(bas, n):
        d = os.path.join(dizin, f"seri_f{f}_{j:02d}")
        shutil.rmtree(d, ignore_errors=True)
        y = TY.sahte_veri(d, f=f, tohum=20261300 + j + (0 if f == 0 else 500))
        t0 = time.time()
        K.TOL_KAL = TOL_SINAMA
        h = K.kos(ayar_kucuk(havuz=havuz, d3_n0=40, d3_nf=30), y, gunluk=lambda *x: None)
        r = dict(j=j, dal=h["dal"], hukum=h["hukum"], p_butun=h.get("p_butun"), p_kd=h.get("p_kesif_disi"),
                 K_kd=h.get("K_kesif_disi"), D3_fa=h.get("D3", {}).get("yanlis_alarm"),
                 D3_guc04=h.get("D3", {}).get("guc", {}).get("0.4"), s=round(time.time() - t0))
        if h["dal"] in (3, 5):
            hata, _ = yeniden_hesap(h, y, ayar_kucuk(havuz=havuz, d3_n0=40, d3_nf=30))
            r["yeniden_hesap_hata"] = str(hata)[:300]
        out.append(r)
        print(json.dumps(r, ensure_ascii=False), flush=True)
        with open(os.path.join(dizin, f"seri_f{f}.jsonl"), "a") as fh:      # ara kayıt
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        shutil.rmtree(os.path.join(d, "kosu", "havuz"), ignore_errors=True)
        for x in ("tr13_ham_2026-11-12.tar.gz", "tr13_tamsayim_ham_2026-11-12.tar.gz"):
            os.remove(os.path.join(d, x))
    var = sum(r["hukum"] == "VAR" for r in out)
    return dict(n=len(out), f=f, havuz=havuz, VAR=var, oran=var / max(len(out), 1), kosular=out)


# ------------------------------------------------------------------ mutasyonlar
MUT = [
    ("Y01 p kuyruk: keşif dışı p bütün listenin sıfırına karşı",
     "p_k = {d: p_deger(S[d][:, kd2, 0].mean(1), zk)", "p_k = {d: p_deger(S[d][:, :, 0].mean(1), zk)", "u"),
    ("Y02 p kuyruk: D-3'te p_vektor üst kuyruk",
     'return np.searchsorted(sifir_sirali, z, side="right") / len(sifir_sirali)',
     'return 1.0 - np.searchsorted(sifir_sirali, z, side="left") / len(sifir_sirali)', "b"),
    ("Y03 küme ortalaması: keşif dışı z̄ bütün listeden",
     "zk = kume_ort(zu, kum2), kume_ort(zu, [kum2[j] for j in kd2])", "zk = kume_ort(zu, kum2), kume_ort(zu, kum2)",
     "u"),
    ("Y04 küme: üyeler ortak indeksle çekilir",
     "            out[:, j, :] += h[rng.integers(0, len(h), nb)][:, :2]",
     "            out[:, j, :] += h[np.random.default_rng(j).integers(0, len(h), nb)][:, :2]", "u"),
    ("Y05 dallanma listesi: üç sıfır da 0,6 havuzundan",
     "havuzlar = {d: {i: sonlu_z(P[(i, di)]) for i in BG}", "havuzlar = {d: {i: sonlu_z(P[(i, 1)]) for i in BG}", "u"),
    ("Y20 sıfır havuzu z_p şartıyla (inceleme öncesi davranış)",
     "havuzlar = {d: {i: sonlu_z(P[(i, di)]) for i in BG}", "havuzlar = {d: {i: sonlu(P[(i, di)]) for i in BG}", "u"),
    ("Y06 dallanma listesi: D-3 R0'ı 0,8'i yok sayar",
     "    for d in DALLANMA:\n        red &=", "    for d in DALLANMA[:2]:\n        red &=", "b"),
    ("Y07 K sayımı: cümledeki K bütün liste", "    K_kd = len(kd2)", "    K_kd = len(kum2)", "u"),
    ("Y08 K sayımı: K = 8'de veri yok", "    if len(kd) < KD_MIN:", "    if len(kd) <= KD_MIN:", "u"),
    ("Y09 körlük: 2026-01-01T00:00 dahil", '(d["t"] < T.KOR_MS)', '(d["t"] <= T.KOR_MS)', "b"),
    ("Y10 körlük: 31 gün kayık", '(d["t"] < T.KOR_MS)', '(d["t"] < T.KOR_MS + 31 * GUN_MS)', "b"),
    ("Y11 havuz boyu: son parça okunmaz",
     "np.concatenate([np.load(havuz_yolu(dizin, ad, p)) for p in range(parca)])",
     "np.concatenate([np.load(havuz_yolu(dizin, ad, p)) for p in range(max(parca - 1, 1))])", "U"),
    ("Y12 havuz boyu: %10 eksik havuz",
     "Nh * ayar.test_nh_carpan, d, 0.0, ayar.havuz, ayar.parca", "Nh * ayar.test_nh_carpan, d, 0.0, "
     "ayar.havuz - ayar.havuz // 10, ayar.parca", "U"),
    ("Y13 kilit: DONDURULDU bütün metinde aranır", 'if "DONDURULDU" not in durum:', 'if "DONDURULDU" not in metin:',
     "b"),
    ("Y14 kilit: sha256 denetimi kapıdan kalkar", "    eksik = [k for k, v in kod_sha().items() if v not in metin]",
     "    eksik = []", "b"),
    ("Y15 kilit: sürdürmede gerçek z yeniden hesaplanır", "    if os.path.exists(zyol):", "    if False:", "u"),
    ("Y16 tohum: kalibrasyon tohumu +11", "return TOHUM0 + 1000 * i + 10 + di", "return TOHUM0 + 1000 * i + 11 + di",
     "b"),
    ("Y17 tohum: T1 çekilişi üç dallanmada aynı",
     "S = {d: sifir_cekilis(np.random.default_rng(TOHUM_T1 + di), havuzlar[d], kum, ayar.ns_t1)",
     "S = {d: sifir_cekilis(np.random.default_rng(TOHUM_T1), havuzlar[d], kum, ayar.ns_t1)", "u"),
    ("Y19 kilit: kos()'un kendi gerçek kip kapısı kalkar", "    if gercek or gercek_girdi_mi(yollar):",
     "    if False:", "b"),
    ("Y21 sıfır havuzunda N >= 50 şartı kalkar", "return h[np.isfinite(h[:, 0]) & (h[:, 2] >= N_ALT)]",
     "return h[np.isfinite(h[:, 0])]", "u"),
    ("Y18 D-3 kapısı f = 0,5 gücüyle", "gecer=d3_gecer(oran[0.0], oran[D3_F]),", "gecer=d3_gecer(oran[0.0], oran[0.5]),",
     "u"),
]


def mutasyon(dizin, kaynak):
    metin = open(kaynak).read()
    out = []
    sec = os.environ.get("KODINC_MUT_SEC")
    for ad, eski, yeni, kip in MUT:
        if sec and ad[:3] not in sec.split(","):
            continue
        if metin.count(eski) != 1:
            out.append(dict(mutasyon=ad, yakalandi=None, not_="dizgi bulunamadı/çok: %d" % metin.count(eski)))
            print(ad, "DİZGİ YOK", metin.count(eski), flush=True)
            continue
        md = os.path.join(dizin, "mut", ad[:3])
        shutil.rmtree(md, ignore_errors=True)
        os.makedirs(md)
        yol = os.path.join(md, "tr13b_kosu.py")
        open(yol, "w").write(metin.replace(eski, yeni))
        t0 = time.time()
        dusen = []
        kipler = [("Y", "birim"), ("A", "birim")] + ([("Y", "uctan")] if kip in "uU" else [])
        env = dict(os.environ)
        if kip != "u":
            env.pop("KODINC_ONBELLEK", None)
        for kim, k in kipler:
            betik = os.path.abspath(__file__) if kim == "Y" else os.path.join(TR13B, "tr13b_test_yapay.py")
            r = subprocess.run([sys.executable, "-I", "-B", betik, md, k, "--modul", yol],
                               capture_output=True, text=True, timeout=3600, env=env)
            try:
                ozet = json.load(open(os.path.join(md, f"test_{k}.json")))
                dusen += [f"{kim}:{x}" for x, v in ozet["sonuc"].items() if not v["gecti"]]
            except Exception:  # noqa
                dusen.append(f"{kim}:{k}:çöktü rc={r.returncode} {r.stderr[-200:]}")
            os.path.exists(os.path.join(md, f"test_{k}.json")) and os.remove(os.path.join(md, f"test_{k}.json"))
            if dusen and kim == "Y" and k == "birim":
                break
        out.append(dict(mutasyon=ad, yakalandi=bool(dusen), dusen=dusen, s=round(time.time() - t0, 1)))
        print(ad, "YAKALANDI" if dusen else "KAÇTI", dusen, flush=True)
        shutil.rmtree(md, ignore_errors=True)
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    dizin, kip = os.path.abspath(a[0]), a[1]
    modul = a[a.index("--modul") + 1] if "--modul" in a else os.path.join(TR13B, "tr13b_kosu.py")
    K = TY.yukle(modul)
    # kopya modül (mutasyon) depodan başka yerde: depo yollarını sabitle
    _depo = "/home/user/knotenlinie"
    K.ONKAYIT = os.path.join(_depo, "kayit", "onkayit", "TR-13b_sinirli-kosu_ONKAYIT.md")
    K.SHA_LISTE = os.path.join(_depo, "kayit", "turetme", "tr13", "tr13_ham_sha256.txt")
    K.TAMSAYIM = os.path.join(_depo, "kayit", "turetme", "tr13", "tr13_tamsayim.json")
    K.CIKTI = os.path.join(dizin, "YOK_cikti")
    koru()
    os.makedirs(dizin, exist_ok=True)
    t0 = time.time()
    if kip == "birim":
        sonuc = birim(dizin)
    elif kip == "uctan":
        sonuc = uctan(dizin)
    elif kip == "seri":
        sonuc = seri(dizin, int(a[a.index("--n") + 1]), float(a[a.index("--f") + 1]), int(a[a.index("--havuz") + 1]))
    elif kip == "mutasyon":
        sonuc = mutasyon(dizin, modul)
    else:
        sys.exit(__doc__)
    ozet = dict(kip=kip, modul_sha256=K.sha256(modul), sure_s=round(time.time() - t0, 1), sonuc=sonuc)
    json.dump(ozet, open(os.path.join(dizin, f"test_{kip}.json"), "w"), indent=1, ensure_ascii=False, default=float)
    print(json.dumps(ozet, indent=1, ensure_ascii=False, default=float)[:3000])
    if kip in ("birim", "uctan"):
        sys.exit(0 if all(v["gecti"] for v in sonuc.values()) else 1)
