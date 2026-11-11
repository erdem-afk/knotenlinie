#!/usr/bin/env python3
"""TR-2 koşu kodunun yapay sınavı: işareti bilinen uydurma olaylar. Gerçek veriye dokunmaz.

Sınananlar: isabet fonksiyonu (çeşitli köken, doğrultu, yarıküre, tarih çizgisi), §3 eşikleri ve kesin binom,
zaman ters çevrimi (K_ters, X_ters, kuyruklar, yorum kuralları), bootstrap (belirlenimcilik, E2'deki X 26 / 30
davranışı), bilgi satırı alt grupları, manifest tarafındaki zaman aralığı sınırları ve ortak sonraki olay kuralı,
yapay ham dizinle uçtan uca koşu (sha doğrulama, manifest tutarlılık denetimi).

Kullanım: python3 -I -B kayit/turetme/tr2/tr2_test_yapay.py
"""
import csv
import math
import os
import random
import sys
import tempfile

sys.dont_write_bytecode = True
BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
import tr2_sayim as S  # noqa: E402
import tr2_manifest as MF  # noqa: E402
import tr2_kosu as KO  # noqa: E402

GECEN = []


def sina(f):
    f()
    GECEN.append(f.__name__)
    print("GEÇTİ", f.__name__)
    return f


def yerlestir(lat, lon, stk, s, d):
    """Kökene göre (s, d) km konumundaki nokta: eksen_bilesen'in tersi."""
    return MF.hedef_nokta(lat, lon, math.hypot(s, d), stk + math.degrees(math.atan2(d, s)))


def iso(ms):
    return S.time.strftime("%Y-%m-%dT%H:%M:%S", S.time.gmtime(ms / 1000)) + f".{ms % 1000:03d}Z"


# ---------------------------------------------------------------- yapay manifest üretici
def yapay(K=40, X=26, Kters=30, Xters=15, tohum=1, flag_fn=None):
    """K küme; ilk X'i isabet. İlk Kters kümede önceki olay var; bunların ilk Xters'i isabet_ters.
    Dönüş: manifest, manifest_ag, olaylar, etas, beklenen (küme -> (isabet, isabet_ters))."""
    rng = random.Random(tohum)
    man, olaylar, bek = [], {}, {}
    t_ms = S._ms("2000-01-01T00:00:00")
    for i in range(K):
        lat, lon = rng.uniform(-65, 65), rng.uniform(-180, 180)
        if i % 7 == 0:
            lon = 179.9 if i % 2 else -179.9           # tarih çizgisi
        mw = round(rng.uniform(6.0, 7.2), 1)
        L = S.L_km(mw)
        D = max(L, 30.0)
        stk = rng.uniform(0, 360)
        sessiz = rng.choice((1, -1))
        h = int(i < X)
        sg = sessiz if h else -sessiz
        s_son, d_son = sg * rng.uniform(0.5 * L + 0.5, 5 * L - 0.5), rng.uniform(-D + 0.5, D - 0.5)
        sl, so = yerlestir(lat, lon, stk, s_son, d_son)
        sid = f"yson{i:02d}"
        olaylar[sid] = (sl, so)
        aS, aD = S.mutlak_eksen({"lat": lat, "lon": lon}, sl, so, stk)
        r = {a: "" for a in MF.ALANLAR}
        fl = flag_fn(i) if flag_fn else {}
        r.update({"kume": f"K{i + 1:02d}", "birincil_id": f"yb{i:02d}", "t0": iso(t_ms + i * 10 ** 9),
                  "t0_ms": t_ms + i * 10 ** 9, "mw": mw, "L_km": repr(L), "stk": repr(stk),
                  "dis_merkez_lat": lat, "dis_merkez_lon": lon, "koken": "dis_merkez",
                  "koken_lat": repr(lat), "koken_lon": repr(lon), "sessiz_isaret": sessiz,
                  "n_taraf": 12, "absA": "0.5000", "sonraki_id": sid, "sonraki_t": "", "sonraki_m": 6.3,
                  "sonraki_tur": "earthquake", "sonraki_abs_s_L": f"{aS / L:.4f}", "sonraki_abs_d_km": f"{aD:.3f}",
                  "aday_sayisi": fl.get("aday_sayisi", 1), "u_L": f"{fl.get('u_L', i / 100):.4f}",
                  "duzlem_pca_fark": "5.00", "zayif_duzlem": fl.get("zayif_duzlem", 0),
                  "aday_ge3": fl.get("aday_ge3", 0), "golge": fl.get("golge", 0), "cift_oncu": fl.get("cift_oncu", 0),
                  "sonraki_s_le_L": int(aS / L <= 1), "sonraki_m_ge_mw": fl.get("sonraki_m_ge_mw", 0),
                  "sonraki_ss_birincil": fl.get("sonraki_ss_birincil", 0), "tr": int(i == 3),
                  "kume_birincil_sayisi": 1})
        ht = None
        if i < Kters:
            ht = int(i < Xters)
            sg = sessiz if ht else -sessiz
            s_o, d_o = sg * rng.uniform(0.5 * L + 0.5, 5 * L - 0.5), rng.uniform(-D + 0.5, D - 0.5)
            ol, oo = yerlestir(lat, lon, stk, s_o, d_o)
            oid = f"yonc{i:02d}"
            olaylar[oid] = (ol, oo)
            aS, aD = S.mutlak_eksen({"lat": lat, "lon": lon}, ol, oo, stk)
            r.update({"onceki_id": oid, "onceki_abs_s_L": f"{aS / L:.4f}", "onceki_abs_d_km": f"{aD:.3f}"})
        man.append(r)
        bek[r["kume"]] = (h, ht)
    etas = {r["kume"]: 0.3 + 0.4 * (j % 5) / 4 for j, r in enumerate(man)}
    return man, [dict(r, koken="agirlik") for r in man[:10]], olaylar, etas, bek


# ---------------------------------------------------------------- sınavlar
@sina
def isabet_fonksiyonu():
    rng = random.Random(7)
    n = 0
    for _ in range(2000):
        lat, lon = rng.uniform(-80, 80), rng.uniform(-180, 180)
        stk = rng.uniform(0, 360)
        L = S.L_km(rng.uniform(6, 7.2))
        sessiz = rng.choice((1, -1))
        taraf = rng.choice((1, -1))
        s = taraf * rng.uniform(0.5 * L, 5 * L)
        d = rng.uniform(-max(L, 30), max(L, 30))
        la, lo = yerlestir(lat, lon, stk, s, d)
        s2, d2 = S.eksen_bilesen({"lat": lat, "lon": lon}, la, lo, stk)
        assert abs(s2 - s) < 1e-6 and abs(d2 - d) < 1e-6
        assert KO.isabet(lat, lon, stk, sessiz, la, lo) == int(taraf == sessiz)
        n += 1
    # elle: köken (0,0), doğrultu 90 (doğu). Doğudaki olay s>0.
    assert KO.isabet(0, 0, 90, 1, 0, 0.5) == 1 and KO.isabet(0, 0, 90, -1, 0, 0.5) == 0
    assert KO.isabet(0, 0, 90, 1, 0, -0.5) == 0 and KO.isabet(0, 0, 270, 1, 0, -0.5) == 1
    # doğrultu 0 (kuzey): kuzeydeki olay s>0; doğrultuyu 180° çevirmek işareti çevirir
    assert KO.isabet(10, 20, 0, 1, 10.4, 20) == 1 and KO.isabet(10, 20, 180, 1, 10.4, 20) == 0
    # tarih çizgisi: köken 179.9 D, doğrultu 90; 180'i aşan olay (−179.8) doğuda
    assert KO.isabet(0, 179.9, 90, 1, 0, -179.8) == 1
    try:
        KO.isabet(0, 0, 90, 0, 0, 0.5)
        raise AssertionError("sessiz 0 kabul edildi")
    except ValueError:
        pass


@sina
def binom_ve_esikler():
    assert abs(KO.binom_ust(26, 40) - 0.0403) < 5e-5            # ön kayıt §3: 0,040
    assert abs(KO.binom_alt(22, 40, 0.7) - 0.0320) < 5e-5       # 0,032
    assert abs(KO.binom_ust(0, 40) - 1) < 1e-12 and abs(KO.binom_alt(40, 40) - 1) < 1e-12
    # §3 tablosu: p 0,5 / 0,6 / 0,65 / 0,7 altında hüküm olasılıkları
    for p, (h1, h0) in {0.5: (0.04, 0.78), 0.6: (0.32, 0.31), 0.65: (0.57, 0.12), 0.7: (0.81, 0.03)}.items():
        assert abs(KO.binom_ust(26, 40, p) - h1) < 0.006 and abs(KO.binom_alt(22, 40, p) - h0) < 0.006
    bek = {X: ("H1" if X >= 26 else "H0" if X <= 22 else "ayirt_edilemez") for X in range(41)}
    for X in range(41):
        assert KO.hukum(X, 40) == bek[X]
    assert [KO.hukum(X, 40) for X in (22, 23, 25, 26)] == ["H0", "ayirt_edilemez", "ayirt_edilemez", "H1"]
    try:
        KO.hukum(20, 39)
        raise AssertionError("K 39 kabul edildi")
    except ValueError:
        pass


@sina
def hesapla_X_ve_hukum():
    for X in (0, 14, 22, 23, 24, 25, 26, 30, 40):
        man, ag, ol, et, bek = yapay(X=X, tohum=100 + X)
        r = KO.hesapla(man, ag, ol, et)
        assert r["K"] == 40 and r["X"] == X, (X, r["X"])
        for s in r["kume_satirlari"]:
            assert s["isabet"] == bek[s["kume"]][0]
        assert r["hukum"] == KO.hukum(X, 40)
        assert r["bilgi_satirlari"]["6_ters_yon_notu"] == (X <= 14)


@sina
def zaman_ters_cevrimi():
    # K_ters 30, X_ters 21: üst kuyruk P(X≥21 | 30) = 0,0214 → red; hüküm H1 → kural 2
    man, ag, ol, et, bek = yapay(X=27, Kters=30, Xters=21, tohum=5)
    r = KO.hesapla(man, ag, ol, et)
    z = r["bilgi_satirlari"]["8_zaman_ters_cevrimi"]
    assert (z["K"], z["X"]) == (30, 21)
    assert abs(z["ust_kuyruk_p"] - sum(math.comb(30, i) for i in range(21, 31)) / 2 ** 30) < 1e-12
    assert abs(z["alt_kuyruk_p"] - sum(math.comb(30, i) for i in range(0, 22)) / 2 ** 30) < 1e-12
    assert r["yorum_kurallari"]["kural2_H1_ve_ters_ust_red"]["uygulanir"] is True
    assert r["yorum_kurallari"]["s8_aktarim_adayi"] is False
    for s in r["kume_satirlari"]:
        assert s["isabet_ters"] == bek[s["kume"]][1]
    # H0 ve ters alt red: K_ters 30, X_ters 9 (P(X≤9|30) = 0,0214) → kural 3
    man, ag, ol, et, bek = yapay(X=18, Kters=30, Xters=9, tohum=6)
    r = KO.hesapla(man, ag, ol, et)
    assert r["hukum"] == "H0" and r["yorum_kurallari"]["kural3_H0_ya_da_ters_yon_ve_ters_alt_red"]["uygulanir"]
    assert r["yorum_kurallari"]["kural2_H1_ve_ters_ust_red"]["uygulanir"] is False
    # Ayırt edilemez, X > 14, alt red → kural 3 uygulanmaz
    man, ag, ol, et, bek = yapay(X=24, Kters=30, Xters=9, tohum=8)
    r = KO.hesapla(man, ag, ol, et)
    assert not r["yorum_kurallari"]["kural3_H0_ya_da_ters_yon_ve_ters_alt_red"]["uygulanir"]
    # Ters yön notu (X ≤ 14) ile alt red → kural 3 uygulanır
    man, ag, ol, et, bek = yapay(X=13, Kters=30, Xters=9, tohum=9)
    r = KO.hesapla(man, ag, ol, et)
    assert r["yorum_kurallari"]["kural3_H0_ya_da_ters_yon_ve_ters_alt_red"]["uygulanir"]
    # önceki olayı olmayan kümeler K_ters'e girmez
    man, ag, ol, et, bek = yapay(X=26, Kters=0, Xters=0, tohum=10)
    r = KO.hesapla(man, ag, ol, et)
    z = r["bilgi_satirlari"]["8_zaman_ters_cevrimi"]
    assert z["K"] == 0 and z["ust_kuyruk_p"] is None


@sina
def bootstrap_davranisi():
    a = KO.bootstrap({"x": [0.1 * i for i in range(40)]})
    b = KO.bootstrap({"x": [0.1 * i for i in range(40)]})
    assert a == b                                                 # tohumla belirlenimci
    for X, icerir in ((26, True), (29, True), (30, False)):       # inceleme E2: yalnız X ≥ 30'da sıfırı dışlar
        man, ag, ol, et, _ = yapay(X=X, tohum=200 + X)
        r = KO.hesapla(man, ag, ol, et)
        bt = r["log_skor"]["bosluk_eksi_taban"]
        assert abs(bt["fark_nat"] - (X * math.log(1.3) + (40 - X) * math.log(0.7))) < 1e-9
        assert bt["sifiri_icerir"] == icerir, (X, bt)
        lo, hi = bt["aralik_95"]
        assert lo < bt["fark_nat"] < hi
        # boşluk − ETAS = (boşluk − taban) − (ETAS − taban)
        ls = r["log_skor"]
        assert abs(ls["bosluk_eksi_etas"]["fark_nat"]
                   - (ls["bosluk_eksi_taban"]["fark_nat"] - ls["etas_eksi_taban"]["fark_nat"])) < 1e-9
        if X == 26:
            assert abs(bt["fark_nat"] - 1.828) < 1e-3 and lo < -1.0 and hi > 4.5   # inceleme: [−1,89, +5,54]
            assert r["yorum_kurallari"]["s4_oncelik"]["metin"] == "H1, log skor aralığı sıfırı içeriyor"
    # ETAS log skoru: p_i doğrudan kullanılır
    man, ag, ol, et, bek = yapay(X=20, tohum=3)
    r = KO.hesapla(man, ag, ol, et)
    bek_etas = sum(math.log(et[k]) if bek[k][0] else math.log(1 - et[k]) for k in et)
    assert abs(r["log_skor"]["toplamlar_nat"]["etas"] - bek_etas) < 1e-9


@sina
def bilgi_satirlari_alt_gruplar():
    fl = lambda i: {"zayif_duzlem": int(i % 3 == 0), "aday_ge3": int(i % 4 == 0), "golge": int(i % 5 == 0),
                    "cift_oncu": int(i % 6 == 0), "sonraki_m_ge_mw": int(i % 2 == 0),
                    "sonraki_ss_birincil": int(i % 7 == 0), "u_L": (i * 37 % 40) / 40}
    man, ag, ol, et, bek = yapay(X=25, tohum=11, flag_fn=fl)
    r = KO.hesapla(man, ag, ol, et)
    b = r["bilgi_satirlari"]
    h = [bek[f"K{i + 1:02d}"][0] for i in range(40)]

    def xk(f):
        idx = [i for i in range(40) if f(i)]
        return sum(h[i] for i in idx), len(idx)
    assert (b["3_zayif_duzlem"]["var"]["X"], b["3_zayif_duzlem"]["var"]["K"]) == xk(lambda i: i % 3 == 0)
    assert (b["4_aday_ge3"]["yok"]["X"], b["4_aday_ge3"]["yok"]["K"]) == xk(lambda i: i % 4 != 0)
    assert (b["5_golge_disli"]["X"], b["5_golge_disli"]["K"]) == xk(lambda i: i % 5 != 0)
    assert (b["9_cift_oncu_disli"]["X"], b["9_cift_oncu_disli"]["K"]) == xk(lambda i: i % 6 != 0)
    g = b["10_alt_gruplar"]
    assert (g["sonraki_m_ge_mw"]["grup"]["X"], g["sonraki_m_ge_mw"]["grup"]["K"]) == xk(lambda i: i % 2 == 0)
    assert (g["sonraki_ss_birincil"]["grup"]["X"], g["sonraki_ss_birincil"]["grup"]["K"]) == xk(lambda i: i % 7 == 0)
    u = [(i * 37 % 40) / 40 for i in range(40)]
    med = sorted(u)[19] / 2 + sorted(u)[20] / 2
    assert b["1_u_L"]["medyan"] == med
    assert (b["1_u_L"]["alt"]["X"], b["1_u_L"]["alt"]["K"]) == xk(lambda i: u[i] < med)
    assert b["1_u_L"]["alt"]["K"] + b["1_u_L"]["ust"]["K"] == 40
    assert b["7_turkiye"] == [{"kume": "K04", "birincil_id": "yb03", "isabet": h[3]}]
    ag_h = [bek[f"K{i + 1:02d}"][0] for i in range(10)]
    assert b["2_agirlik_merkezi"]["X"] == sum(ag_h) and b["2_agirlik_merkezi"]["K"] == 10


@sina
def manifest_tutarlilik_denetimi():
    man, ag, ol, et, _ = yapay(X=26, tohum=12)
    man[5] = dict(man[5], sonraki_abs_s_L=f"{float(man[5]['sonraki_abs_s_L']) + 0.05:.4f}")
    try:
        KO.hesapla(man, ag, ol, et)
        raise AssertionError("yanlış |s|/L yakalanmadı")
    except ValueError:
        pass


@sina
def zaman_araliklari_ve_ortak_kural():
    """Manifest tarafı: (t0+30 g, ...] ve [..., t0−30 g) sınırları; ortak sonraki olay kuralı."""
    t0 = S._ms("2005-06-01T00:00:00")
    mw, stk = 7.0, 90.0
    L = S.L_km(mw)
    A = {"id": "A", "t": t0, "lat": 0.0, "lon": 0.0, "mw": mw, "dz": [(90, 90, 0), (0, 90, 180)]}
    Bb = {"id": "B", "t": t0 + 5 * S.GUN_MS, "lat": 0.0, "lon": 0.0, "mw": mw, "dz": [(90, 90, 0), (0, 90, 180)]}
    Bb["lat"], Bb["lon"] = yerlestir(0, 0, stk, 400.0, 0.0)

    def ev(eid, t, lat, lon, m=6.2):
        return {"id": eid, "t": t, "time": iso(t), "lat": lat, "lon": lon, "m": m, "tur": "earthquake"}
    orta = yerlestir(0, 0, stk, 200.0, 0.0)           # iki kutuda da (|s| = 200 km)
    yalniz_B = yerlestir(Bb["lat"], Bb["lon"], stk, 2 * L, 0.0)
    havuz = [ev("tam30", t0 + 30 * S.GUN_MS, *yerlestir(0, 0, stk, -2 * L, 0)),        # sonraki dışı (30. gün)
             ev("o_tam30", t0 - 30 * S.GUN_MS, *yerlestir(0, 0, stk, -2 * L, 0)),      # önceki dışı
             ev("o_ic", t0 - 31 * S.GUN_MS, *yerlestir(0, 0, stk, -2 * L, 0)),         # önceki
             ev("o_eski", t0 - 400 * S.GUN_MS, *yerlestir(0, 0, stk, 2 * L, 0)),       # daha eski önceki
             ev("ortak", t0 + 100 * S.GUN_MS, *orta),
             ev("B2", t0 + 200 * S.GUN_MS, *yalniz_B)]
    havuz.sort(key=lambda h: h["t"])
    son = MF.kutu_adaylari(A, A, stk, L, havuz, "sonraki")
    assert [c["id"] for c in son] == ["ortak"], son
    once = MF.kutu_adaylari(A, A, stk, L, havuz, "onceki")
    assert [c["id"] for c in once] == ["o_eski", "o_ic"]
    assert "s" not in son[0] and set(son[0]) >= {"abs_s", "abs_d"}       # işaret tutulmaz

    def bulut(b):
        art = [yerlestir(b["lat"], b["lon"], stk, 20.0 + k, 1.0) + (4.5,) for k in range(10)]
        art += [yerlestir(b["lat"], b["lon"], stk, -20.0 - k, 1.0) + (4.5,) for k in range(3)]
        return art
    analiz = []
    for k, b in enumerate((A, Bb)):
        art = bulut(b)
        analiz.append({"b": b, "L": L, "art": art, "buyuk": [], "stk": stk, "pfark": 1.0, "kok": k,
                       "cen": {"lat": b["lat"], "lon": b["lon"]}, "u": 0.0})
    sat, ist = MF.manifest_kur(analiz, havuz, {"A", "B"}, "dis_merkez")
    assert [(s["birincil_id"], s["sonraki_id"]) for s in sat] == [("A", "ortak"), ("B", "B2")], sat
    assert len(ist["ortak_sonraki_olay"]) == 1 and ist["ortak_sonraki_olay"][0]["olay"] == "ortak"
    assert sat[0]["onceki_id"] == "o_ic" and sat[0]["sessiz_isaret"] == -1   # 10 artçı + yanda, 3 − yanda
    assert not {"sonraki_s", "onceki_s", "sonraki_isaret", "onceki_isaret"} & set(MF.ALANLAR)
    # B2 olmasa B nitelikten düşer
    sat2, _ = MF.manifest_kur(analiz, [h for h in havuz if h["id"] != "B2"], {"A", "B"}, "dis_merkez")
    assert [s["birincil_id"] for s in sat2] == ["A"]
    # |A| = 1/3 tam eşitliği: metin içeri alır, sayım yuvarlaması dışarıda bırakır
    assert MF.asim_olculur(15, 5 / 15, False) and not MF.asim_olculur(15, 5 / 15, True)
    assert not MF.asim_olculur(9, 1.0, False)


@sina
def uctan_uca_dosyalarla():
    man, ag, ol, et, bek = yapay(X=27, Kters=25, Xters=12, tohum=21)
    with tempfile.TemporaryDirectory() as td:
        ham = os.path.join(td, "ham")
        os.makedirs(os.path.join(ham, "artci"))
        bas = ["time", "latitude", "longitude", "depth", "mag", "magType", "id", "type"]
        with open(os.path.join(ham, "birincil_aday.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(bas)
            for r in man:
                w.writerow([iso(int(r["t0_ms"])), r["dis_merkez_lat"], r["dis_merkez_lon"], 10, r["mw"], "mww",
                            r["birincil_id"], "earthquake"])
        with open(os.path.join(ham, "birincil_aday_fm.csv"), "w", newline="") as f:
            csv.writer(f).writerow(bas)
        with open(os.path.join(ham, "m6_havuz.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(bas)
            for i, (eid, (la, lo)) in enumerate(sorted(ol.items())):
                w.writerow(["2010-01-01T00:00:00.000Z", la, lo, 10, 6.1, "mww", eid, "earthquake"])
        open(os.path.join(ham, "artci", "yb00.csv"), "w").write(",".join(bas) + "\n")
        for ad, sat in (("m.csv", man), ("a.csv", ag)):
            MF.yaz_csv(os.path.join(td, ad), sat)
        with open(os.path.join(td, "e.csv"), "w") as f:
            f.write("kume,birincil_id,p_i\n" + "".join(f"{r['kume']},{r['birincil_id']},{et[r['kume']]:.6f}\n"
                                                       for r in man))
        with open(os.path.join(td, "sha.txt"), "w") as f:
            f.write("\n".join(MF.sha_listesi(ham)) + "\n")
        cik = os.path.join(td, "cikti")
        arg = ["--ham", ham, "--manifest", os.path.join(td, "m.csv"), "--manifest-agirlik", os.path.join(td, "a.csv"),
               "--sha", os.path.join(td, "sha.txt"), "--etas", os.path.join(td, "e.csv"), "--cikti", cik]
        KO.main(KO.argumanlar(arg))
        import json
        r = json.load(open(os.path.join(cik, "tr2_sonuc.json")))
        assert r["X"] == 27 and r["hukum"] == "H1" and r["girdi"]["sha_dogrulanan_dosya"] == 4
        z = r["bilgi_satirlari"]["8_zaman_ters_cevrimi"]
        assert (z["K"], z["X"]) == (25, 12)
        md = open(os.path.join(cik, "tr2_sonuc.md")).read()
        assert "X = 27" in md and "| K40 |" in md
        # tek koşu: ikinci çağrı durur
        try:
            KO.main(KO.argumanlar(arg))
            raise AssertionError("ikinci koşu durmadı")
        except SystemExit:
            pass
        # bozulmuş dosya: sha doğrulaması durur
        open(os.path.join(ham, "artci", "yb00.csv"), "a").write("x\n")
        try:
            KO.main(KO.argumanlar(arg + ["--uzerine-yaz"]))
            raise AssertionError("sha bozulması yakalanmadı")
        except SystemExit as e:
            assert "sha256" in str(e)


@sina
def ek1_k42():
    for X, deg in ((22, True), (23, True), (24, False), (25, True), (26, True), (27, False), (30, False)):
        man, ag, ol, et, _ = yapay(X=X, tohum=300 + X)
        r = KO.hesapla(man, ag, ol, et)
        assert r["ek1_K42"]["hukum_degisebilir"] is deg, (X, r["ek1_K42"])
        assert "Ek 1 (K = 42" in KO.md_yaz(r)


if __name__ == "__main__":
    print(f"{len(GECEN)} sınav geçti.")
