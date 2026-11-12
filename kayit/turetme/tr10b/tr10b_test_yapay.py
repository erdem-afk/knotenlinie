#!/usr/bin/env python3
"""TR-10b koşu kodu sınamaları: YALNIZ YAPAY VERİ. Hiçbir gerçek sünme ölçer veri dosyası okunmaz.

Kapsam (§14 madde 3 ve §10.2): liste sha256 doğrulaması; okuma (başlık, boş satır, günlük medyan, 10MIN, sırasız
dosya, erken durma yok); biçim hatasında durma ve biçim keşfi maskesi; ⌊gün⌋ = 0; geçersiz tarih; %1 bozuk pay;
aralık dışı bozuk satır; 2024 ve sonrası satırların değer sütununun ayrıştırılmaması; §8 boşluk/doluluk/uç ve elle
katman şartları; kaynak sırası; temsilci; aygıt olayı kuralı (K tamponu, K_SON, HDR aralığı); HDR uyarlaması ve
README sınaması; (a), (a3), (a4), elle katman; ρ ekleme ve deterministik sınır; d_analitik; dolgu tanısı; menteşe
modeli; bootstrap tohumu ve (B, K) çekilişi; seri tohumları; uçtan uca koşular (kapı geçti K ≥ 4 bağlayıcı boyutta,
kapı geçmedi, K ≤ 3, kod hatası, biçim hatası, tek koşu işaretleri, manifest uyuşmazlığı); indirme betiği yerel
yapay sunucuyla.

Kullanım (depo kökünden): python3 -I -B kayit/turetme/tr10b/tr10b_test_yapay.py [-v] [Sinif.test_adi]
Ortam: TR10B_HAM=<SAYIM ham dizini> ve TR10B_HDR=<HDR dosyaları dizini> verilirse README sınaması ve HDR
çıktısının yeniden üretimi de koşar (yoksa atlanır).
"""
import contextlib
import copy
import datetime as dt
import gzip
import hashlib
import http.server
import io
import json
import math
import os
import re
import resource
import shutil
import sys
import tempfile
import threading
import time
import unittest

BURA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURA)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

import tr10b_hdr as H  # noqa: E402
import tr10b_indir as I  # noqa: E402
import tr10b_kosu as K  # noqa: E402
import tr10b_listeler as TL  # noqa: E402

KOK_SABIT = {n: getattr(K, n) for n in ("B_BOOT", "B_M", "N0_M", "B_N_PAY", "B_TAM_N", "KAPI_YER", "KAPI_YP")}


def sabitleri_geri_al():
    for n, v in KOK_SABIT.items():
        setattr(K, n, v)


def gz_yaz(yol, satirlar):
    with gzip.open(yol, "wt", encoding="utf-8") as f:
        f.write("".join(s + "\n" for s in satirlar))


def ord_(y, m, d):
    return dt.date(y, m, d).toordinal()


# ======================================================================== listeler
class Listeler(unittest.TestCase):
    def test_kanonik_ve_sha(self):
        T = TL.listeleri_yukle()
        for ad, v in T["listeler"].items():
            self.assertEqual(TL.kanonik(v), TL.LISTE_SHA[ad])
        B, A, _ = TL.md_listeleri(TL.md_oku())
        self.assertEqual(TL.kanonik(B), TL.LISTE_SHA["B"])
        self.assertEqual(TL.kanonik(A), TL.LISTE_SHA["A"])
        self.assertEqual(T["json_sha256"], K.LISTELER_JSON_SHA)

    def test_md_degisirse_durur(self):
        with tempfile.TemporaryDirectory() as d:
            b = open(TL.MD_YOL, "rb").read()
            y = os.path.join(d, "md.md")
            open(y, "wb").write(b.replace(b"XSH1 2013, 2018 (2018)", b"XSH1 2013, 2018 (2013)"))
            with self.assertRaises(TL.ListeHata):
                TL.listeleri_yukle(md_yol=y)
            # ek eklenmiş metin (dondurulmuş önek aynı) kabul edilir
            open(y, "wb").write(b + "\n## Ek: HDR K/D olayları (koşu öncesi)\n\nmetin\n".encode())
            TL.listeleri_yukle(md_yol=y)

    def test_json_alt_kume_degisirse_durur(self):
        with tempfile.TemporaryDirectory() as d:
            j = json.load(open(TL.JSON_YOL, encoding="utf-8"))
            j["listeler"]["B_R2"] = j["listeler"]["B_R2"][1:]
            y = os.path.join(d, "l.json")
            json.dump(j, open(y, "w", encoding="utf-8"))
            with self.assertRaises(TL.ListeHata):
                TL.listeleri_yukle(json_yol=y)

    def test_md_tablosu_ayristirma(self):
        B, A, kes = TL.md_listeleri(TL.md_oku())
        self.assertIn(("HWP1", 1973), B)
        self.assertIn(("HWP1", 2003), A)
        self.assertNotIn(("HWP1", 2008), A)
        self.assertIn(("XGH1", 1978), A)
        self.assertNotIn(("XDL2", 1998), A)
        self.assertEqual(kes["X461"], "SAF_Parkfield")
        self.assertEqual(len(B), 78)

    def test_readme_tablosu(self):
        self.assertEqual(len(K.README_TAB), 18)
        self.assertEqual(K.README_TAB["XMD1"], (2.57, 6.47))
        self.assertNotIn("XPK2", K.README_TAB)       # ardıl kod öncülün parametrelerini almaz


# ======================================================================== okuma
class Okuma(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.ar = [(ord_(2013, 9, 16), ord_(2018, 10, 16))]

    def tearDown(self):
        shutil.rmtree(self.d)

    def yol(self, ad="f.gz"):
        return os.path.join(self.d, ad)

    def test_temel_baslik_bos_medyan(self):
        gz_yaz(self.yol(), ["# başlık", "station xyz", "2014 1 1.00", "2014 1 3.00", "2014 1 2.00", "",
                            "2014 2 5.25 ekstra sütun"])
        o = K.oku_dosya(self.yol(), self.ar)
        self.assertEqual(o["gunluk"][ord_(2014, 1, 1)], 2.0)
        self.assertEqual(o["gunluk"][ord_(2014, 1, 2)], 5.25)
        self.assertEqual(o["sayac"]["baslik"], 2)
        self.assertEqual(o["sayac"]["bos"], 1)
        self.assertAlmostEqual(o["delta"], 0.01)

    def test_10min_ondalik_gun(self):
        gz_yaz(self.yol(), [f"2015 {32 + q / 144:.5f} {q * 0.001:.4f}" for q in range(144)])
        o = K.oku_dosya(self.yol(), self.ar)
        self.assertEqual(list(o["gunluk"]), [ord_(2015, 2, 1)])
        self.assertAlmostEqual(o["gunluk"][ord_(2015, 2, 1)], np.median(np.arange(144) * 0.001))

    def test_bicim_hatasi_durur_ve_maskeler(self):
        gz_yaz(self.yol(), ["2014 1 1.234", "2014 2 7.777", "metin satiri 9.876 4.5"])
        with self.assertRaises(K.BicimHata) as c:
            K.oku_dosya(self.yol(), self.ar)
        k = c.exception.kesif
        self.assertEqual(k["satir"], 3)
        self.assertEqual(k["sutun1"], "metin")
        self.assertEqual(k["sonrasi"], ["***", "***"])
        metin = json.dumps(k)
        for gizli in ("1.234", "7.777", "9.876", "4.5"):
            self.assertNotIn(gizli, metin)
        self.assertTrue(issubclass(K.BicimHata, K.KosuDur))

    def test_gun_sifir_durur(self):
        gz_yaz(self.yol(), ["1960 0 1.0"])               # aralık dışında bile durdurur
        with self.assertRaises(K.BicimHata):
            K.oku_dosya(self.yol(), self.ar)

    def test_gecersiz_tarih_durur(self):
        for s in ("2015 366 1.0", "1959 10 1.0", "2014.5 10 1.0"):
            gz_yaz(self.yol(), [s])
            with self.assertRaises(K.BicimHata):
                K.oku_dosya(self.yol(), self.ar)
        gz_yaz(self.yol(), ["2016 366 1.0"])                # artık yıl
        self.assertEqual(len(K.oku_dosya(self.yol(), self.ar)["gunluk"]), 1)

    def test_bozuk_pay(self):
        ok = [f"2014 {g} 1.0" for g in range(1, 101)]
        gz_yaz(self.yol(), ok + ["2014 201 abc", "2014 202 1e5"])       # 2/102 > %1
        with self.assertRaises(K.BicimHata):
            K.oku_dosya(self.yol(), self.ar)
        gz_yaz(self.yol(), ok + ["2014 201 abc", "2014 202"])            # 2/102 > %1 (alan eksik)
        with self.assertRaises(K.BicimHata):
            K.oku_dosya(self.yol(), self.ar)
        gz_yaz(self.yol(), ok + ["2014 201 nan"])                        # 1/101 ≤ %1
        o = K.oku_dosya(self.yol(), self.ar)
        self.assertEqual(o["sayac"]["bozuk"], 1)

    def test_aralik_disi_bozuk_durdurmaz(self):
        gz_yaz(self.yol(), ["2010 5 abc", "2010 6", "2014 1 1.0"])
        o = K.oku_dosya(self.yol(), self.ar)
        self.assertEqual(o["sayac"]["aralik_disi"], 2)
        self.assertEqual(o["sayac"]["aralik_disi_bozuk"], 1)
        self.assertEqual(o["sayac"]["bozuk"], 0)

    def test_2024_sonrasi_deger_sutunu_ayristirilmaz(self):
        cagri = []
        eski = K._deger
        K._deger = lambda tok: (cagri.append(tok), eski(tok))[1]
        try:
            gz_yaz(self.yol(), ["2014 1 1.5", "2024 10 99.25", "2025 1 GIZLI", "2026 3 -7.5", "2014 2 2.5"])
            o = K.oku_dosya(self.yol(), self.ar)
        finally:
            K._deger = eski
        self.assertEqual(cagri, ["1.5", "2.5"])
        self.assertEqual(sorted(o["gunluk"].values()), [1.5, 2.5])
        self.assertEqual(o["sayac"]["aralik_disi"], 3)
        self.assertTrue(all(d <= K.SON_GUN.toordinal() for d in o["gunluk"]))

    def test_sirasiz_dosya_veri_kaybetmez(self):
        gz_yaz(self.yol(), ["2014 1 1.0", "2020 1 9.0", "2014 2 2.0", "2012 1 0.0", "2014 3 3.0"])
        o = K.oku_dosya(self.yol(), self.ar)
        self.assertEqual(len(o["gunluk"]), 3)

    def test_gzip_degil(self):
        open(self.yol(), "w").write("2014 1 1.0\n")
        with self.assertRaises(K.BicimHata):
            K.oku_dosya(self.yol(), self.ar)


# ======================================================================== §8 şartları
class Sartlar(unittest.TestCase):
    def setUp(self):
        self.W = K.pencere(2013)

    def test_pencere_gunleri(self):
        for Y, (g3, g2) in {1973: (1095, 731), 1978: (1096, 730), 1998: (1096, 730), 2003: (1096, 730),
                            2008: (1096, 731), 2013: (1095, 731), 2018: (1096, 730)}.items():
            W = K.pencere(Y)
            self.assertEqual((W["iH"] - W["i0"], W["iT"] - W["iH"]), (g3, g2))
            self.assertEqual(W["i0"], 15)
            self.assertEqual(W["n"] - 1 - W["iT"], 15)

    def test_tele_bosluk_doluluk_uc(self):
        W, n = self.W, self.W["n"]
        m = np.ones(n, bool)
        self.assertEqual(K.tele_sart(m, W), (True, None))
        m2 = m.copy(); m2[500:560] = False                  # 60 gün: geçer
        self.assertTrue(K.tele_sart(m2, W)[0])
        m2[560] = False                                     # 61 gün: boşluk
        self.assertEqual(K.tele_sart(m2, W)[1], "boşluk")
        m3 = m.copy(); m3[:61] = False                      # aralık başındaki eksikler de koşu (61)
        self.assertEqual(K.tele_sart(m3, W)[1], "boşluk")
        m4 = m.copy()
        idx = np.arange(W["i0"], W["iH"])
        m4[idx[np.arange(len(idx)) % 5 < 2]] = False        # taban doluluğu 0,60 → geçer
        self.assertTrue(K.tele_sart(m4, W)[0])
        m4[idx[np.arange(len(idx)) % 5 == 2]] = False       # 0,40 → doluluk
        self.assertEqual(K.tele_sart(m4, W)[1], "doluluk")
        m5 = m.copy(); m5[W["iH"] - 15:W["iH"] + 7] = False  # uçta 9 gün
        self.assertEqual(K.tele_sart(m5, W)[1], "uç değeri")
        m5[W["iH"] + 6] = True                                # 10 gün
        self.assertTrue(K.tele_sart(m5, W)[0])

    def test_man_sartlari_ve_dar_okuma(self):
        W, n = self.W, self.W["n"]
        m = np.zeros(n, bool); m[::20] = True                # 0, 20, …: w0 (15) için önceki ölçüm 0
        self.assertEqual(K.man_sart(m, W)[1], "uç değeri")   # T'den sonra okuma aralığında ölçüm yok
        m[n - 1] = True
        self.assertTrue(K.man_sart(m, W)[0])
        m2 = np.zeros(n, bool); m2[5::30] = True; m2[n - 3] = True
        self.assertTrue(K.man_sart(m2, W)[0])
        # okuma aralığı dışındaki ölçüm okunmaz: w0'dan önce aralıkta ölçüm yoksa uç tanımsız (kodlayıcı okuması)
        m3 = np.zeros(n, bool); m3[16::20] = True
        self.assertEqual(K.man_sart(m3, W)[1], "uç değeri")
        m4 = np.zeros(n, bool); m4[0::60] = True             # taban < 12 ölçüm? 1095/60 ≈ 18 → geçer sayı
        m4[W["iH"]:] = False; m4[W["iH"]:W["iT"]:100] = True  # yakın: 8 ölçüm, aralık 100 → geçer
        m4[W["iT"]] = True
        ok, ne = K.man_sart(m4, W)
        self.assertEqual(ok, True, ne)
        m5 = m4.copy(); m5[W["iH"]:W["iT"]] = False; m5[W["iH"]:W["iT"]:120] = True
        self.assertEqual(K.man_sart(m5, W)[1], "doluluk")    # yakın dönem 7 ölçüm
        m6 = np.zeros(n, bool); m6[0:n:15] = True; m6[600:800] = False
        self.assertEqual(K.man_sart(m6, W)[1], "boşluk")     # 181+ gün
        m7 = np.zeros(n, bool); m7[0:n:10] = True; m7[W["iH"] - 95:W["iH"] + 1] = False
        self.assertEqual(K.man_sart(m7, W)[1], "uç değeri")  # H'den önceki ölçüm > 90 g

    def test_olc_tele_ve_elle_dogrusal(self):
        W = self.W
        t = (np.arange(W["n"]) - W["i0"]) / 365.25
        m = np.zeros(W["n"], bool); m[::17] = True; m[W["iH"]] = True
        dv, v5 = K.olc(3 + 7 * t, m, W, "man")
        self.assertLess(abs(dv), 1e-9)
        self.assertAlmostEqual(v5, 7.0, places=9)
        dv, v5 = K.olc(3 + 7 * t, np.ones(W["n"], bool), W, "tele")
        self.assertLess(abs(dv), 1e-9)

    def test_rho_deterministik_sinir_ve_analitik(self):
        rng = np.random.default_rng(5)
        for Y in (1973, 1998, 2013, 2018):
            W = K.pencere(Y)
            for _ in range(20):
                x = K.yapay_rw(W["n"], rng)
                m = rng.random(W["n"]) > 0.3
                m[W["i0"] - 15:W["i0"] + 16] = True; m[W["iH"] - 15:W["iH"] + 16] = True
                m[W["iT"] - 15:W["iT"] + 16] = True
                d = K.olc(x + K.rho_seri(W), m, W, "tele")[0] - K.olc(x, m, W, "tele")[0]
                self.assertTrue(4.726 - 1e-3 <= d <= 5.103 + 1e-3, d)
                mm = np.zeros(W["n"], bool); mm[rng.integers(0, 9)::rng.integers(7, 30)] = True
                if not K.man_sart(mm, W)[0]:
                    continue
                d = K.olc(x + K.rho_seri(W), mm, W, "man")[0] - K.olc(x, mm, W, "man")[0]
                self.assertLess(abs(d - K.d_analitik(mm, W)), 1e-9)
                self.assertTrue(4.49 <= K.d_analitik(mm, W) <= 5.0)


# ======================================================================== aygıt olayları
class Olaylar(unittest.TestCase):
    def test_k_tampon_ve_son_veren(self):
        W = K.pencere(2013)
        w0, T = W["w0"], W["T"]
        f = lambda a, b=None: K.olay_dusurur(a, b or a, W)
        self.assertTrue(f(w0 - dt.timedelta(days=30)))
        self.assertFalse(f(w0 - dt.timedelta(days=31)))
        self.assertTrue(f(T + dt.timedelta(days=15)))
        self.assertFalse(f(T + dt.timedelta(days=16)))
        self.assertTrue(f(dt.date(2000, 1, 1), dt.date(2009, 1, 1)))      # tarihsiz aralık keser
        self.assertFalse(f(dt.date(2000, 1, 1), dt.date(2008, 8, 31)))
        self.assertEqual(K.k_nedeni("XPK1", K.pencere(2013), []), "K")    # K_SON 2004-09-28 sonrası
        self.assertEqual(K.k_nedeni("CWC3", K.pencere(2003), []), "K")
        self.assertIsNone(K.k_nedeni("XPK2", K.pencere(2013), []))
        hdr = [dict(kod="XPK2", tur="K", a=dt.date(2009, 1, 1), b=dt.date(2009, 1, 1), tarihsiz=False)]
        self.assertEqual(K.k_nedeni("XPK2", K.pencere(2013), hdr), "HDR")
        hdr = [dict(kod="XPK2", tur="D", a=dt.date(2009, 1, 1), b=dt.date(2009, 1, 1), tarihsiz=False)]
        self.assertIsNone(K.k_nedeni("XPK2", K.pencere(2013), hdr))
        self.assertTrue(K.d_var("XPK2", K.pencere(2013), hdr))
        self.assertTrue(K.d_var("XMM1", K.pencere(2008), []))             # D_OLAY 2007-05-08

    def test_hdr_csv_sabit(self):
        self.assertEqual(K.sha256_dosya(K.HDR_CSV), K.HDR_CSV_SHA)
        ol = K.hdr_olaylari(K.HDR_CSV)
        self.assertTrue(all(o["a"] <= o["b"] for o in ol))
        self.assertTrue(all(o["tur"] in ("K", "D") for o in ol))


class HDRKurali(unittest.TestCase):
    def test_cekirdek_kod_degismedi(self):
        self.assertEqual(K.sha256_dosya(os.path.join(H.YARDIMCI, "inc1_hdr_kural.py")),
                         "69894531e0a69ae4ad20f8265b52f9c66bed34181613fbae8313aad58cbc74b6")

    def test_uyarlama(self):
        H.uyarlamayi_kur()
        HK = H.HK
        self.assertEqual(HK.tarih("N 201402120040 Wire Reset"), (dt.date(2014, 2, 12), "tam"))
        self.assertEqual(HK.tarih("S N 2016j3431450 x")[0], dt.date(2016, 12, 8))
        self.assertEqual(HK.tarih("N 24j310232000 y")[0], dt.date(2024, 11, 5))
        self.assertEqual(HK.tarih("Sept 28 2004 Parkfield EQ")[0], dt.date(2004, 9, 28))
        self.assertEqual(HK.tarih("removed 20180913 a"), (None, None))   # 8 rakam: damga değil, yalın yıl da değil
        L = ["Times of possible offsets:", "N 201402120040 Wire Reset", "N 201505132000 Ditto", "   devam",
             "Late 2023 offline", "", "Başka paragraf", "ikinci satır"]
        self.assertEqual(HK.notlara_bol(L), [(0, [L[0]]), (1, [L[1]]), (2, [L[2], L[3]]), (4, [L[4]]),
                                             (6, [L[6], L[7]])])
        self.assertEqual(HK.notlara_bol(["a", "b"]), [(0, ["a"]), (1, ["b"])])
        o = HK.isle([(1, "April 2007 DCP swap"), (2, "Times of possible offsets:"),
                     (3, "N 201402120040 Wire Reset"), (4, "N 201505132000 Ditto")], dt.date(1966, 1, 1))
        self.assertEqual([(x["tur"], x["a"], x["b"], x["tarihsiz"]) for x in o],
                         [("D", dt.date(2007, 4, 1), dt.date(2007, 4, 1), False),
                          ("K", dt.date(2007, 4, 1), dt.date(2014, 2, 12), True),
                          ("K", dt.date(2014, 2, 12), dt.date(2014, 2, 12), False)])

    @unittest.skipUnless(os.environ.get("TR10B_HAM"), "TR10B_HAM yok")
    def test_readme_basvuru(self):
        ham = os.environ["TR10B_HAM"]
        lj = os.path.join(os.path.dirname(ham), "..", "tr10b_hdr", "listeler.json")
        lj = os.environ.get("TR10B_INC1", lj)
        r = io.StringIO()
        with contextlib.redirect_stdout(r):
            ok = H.readme_sinama(os.path.join(ham, "README_CREEP.txt"), lj)
        self.assertTrue(ok, r.getvalue())

    @unittest.skipUnless(os.environ.get("TR10B_HDR"), "TR10B_HDR yok")
    def test_hdr_ciktisi_yeniden_uretilir(self):
        T = TL.listeleri_yukle()
        ilk = {k: dt.date.fromisoformat(v["ilk"]) for k, v in T["istasyon"].items()}
        if os.environ.get("TR10B_TR10HAM"):
            for s in H.KS.sayfa_istasyonlar(os.environ["TR10B_TR10HAM"]):
                ilk.setdefault(s["kod"], s["ilk"])
        else:
            self.skipTest("TR10B_TR10HAM yok")
        ol, _, _ = H.uygula(os.environ["TR10B_HDR"], H.MANIFEST, None, ilk)
        self.assertEqual(hashlib.sha256(H.csv_metni(ol).encode()).hexdigest(), K.HDR_CSV_SHA)


# ======================================================================== ölçü yardımcıları
class Olcu(unittest.TestCase):
    def test_dolgu(self):
        W = K.pencere(2013)
        n = W["n"]
        rng = np.random.default_rng(3)
        x = np.round(K.yapay_rw(n, rng), 2)
        m = np.ones(n, bool)
        self.assertEqual(K.dolgu(x, m, W, 0.01), (False, False))
        y = x.copy()
        a, b = W["iH"] - 20, W["iH"] + 20
        y[a:b + 1] = np.round(np.linspace(y[a], y[b], b - a + 1), 2)   # doğrusal ara değer, 0,01 nicemli
        self.assertTrue(K.dolgu(y, m, W, 0.01)[0])
        z = x.copy(); z[a:b + 1] = 4.0
        self.assertEqual(K.dolgu(z, m, W, 0.01), (True, True))          # eğimi sıfır
        mm = m.copy(); mm[W["iH"]] = False
        self.assertFalse(K.dolgu(z, mm, W, 0.01)[0])                      # geçerli günler ardışık değil

    def test_mentese(self):
        W = K.pencere(2008)
        t = (np.arange(W["n"]) - W["i0"]) / 365.25
        tH = (W["iH"] - W["i0"]) / 365.25
        x = 2 + 6 * t + 4 * np.maximum(0, t - tH) + 1.5 * np.sin(2 * np.pi * t) + 2.0 * (np.arange(W["n"]) >= 900)
        x[300] += 50
        m = np.ones(W["n"], bool); m[100:130] = False
        d = W["ilk"] + dt.timedelta(days=900)
        self.assertAlmostEqual(K.mentese(x, m, W, [d]), 4.0, places=8)
        self.assertNotAlmostEqual(K.mentese(x, m, W, []), 4.0, places=3)

    def test_seri_tohumu(self):
        s = K.seri_tohumu("XMM1", 2013, 0)
        self.assertEqual(s, int(hashlib.sha256(b"XMM1|2013|0").hexdigest()[:16], 16) ^ 20261112)

    def test_bootstrap_tohum_ve_cekilis(self):
        yps = [dict(kod=f"S{i:02d}", Y=2013, dv=float(v), v5=10.0, kesim=f"k{i % 5}", site=f"s{i}")
               for i, v in enumerate(np.random.default_rng(1).normal(0, 3, 45))]
        Kb, ar = K.bootstrap(yps, "kesim")
        self.assertEqual(Kb, 5)
        rng = np.random.default_rng(20261112)
        cek = rng.integers(0, 5, size=(K.B_BOOT, 5))
        bl = sorted({r["kesim"] for r in yps})
        dv = np.array([r["dv"] for r in yps])
        q95 = []
        for it in range(K.B_BOOT):
            say = np.zeros(len(yps), int)
            for b in cek[it]:
                say[[i for i, r in enumerate(yps) if r["kesim"] == bl[b]]] += 1
            q95.append(np.quantile(np.abs(np.repeat(dv, say)), .95, method="linear"))
        self.assertAlmostEqual(ar["q95"]["L"], np.quantile(q95, .05, method="linear"), places=12)
        self.assertAlmostEqual(ar["q95"]["U"], np.quantile(q95, .95, method="linear"), places=12)
        self.assertEqual(K.bootstrap(yps, "kesim")[1]["q95"], ar["q95"])         # her satır yeni rng

    def test_tanimsiz_yineleme_guc_yok(self):
        yps = [dict(kod=f"S{i}", Y=2013, dv=1.0 + i, v5=(5.0 if i == 0 else 0.5), kesim=f"k{i % 4}", site=f"s{i}")
               for i in range(40)]
        _, ar = K.bootstrap(yps, "kesim")
        self.assertTrue(ar["r95"]["guc_yok"])          # sünen pencere yalnız bir blokta: >%10 tanımsız
        self.assertFalse(ar["q95"]["guc_yok"])

    def test_etiket_ve_okumalar(self):
        self.assertIn("büyük", K.b_etiketi(4.61 * 1.78, 20))
        self.assertIn("küçük", K.b_etiketi(0.1, 2.19 * 1.78))
        self.assertIn("aralığında", K.b_etiketi(2.0, 9.0))
        self.assertEqual(K.rho_okuma(0.5, 0.99), "küçük")
        self.assertEqual(K.rho_okuma(1.01, 2), "büyük")
        self.assertEqual(K.rho_okuma(0.9, 1.1), "uyumlu")
        self.assertEqual(K.ch_okuma(0.0, 0.04), "tabanın üstünde")
        self.assertEqual(K.ch_okuma(0.06, 0.3), "tabanın içinde")


class Tohumlar(unittest.TestCase):
    def tearDown(self):
        sabitleri_geri_al()

    def test_n0_cekilisleri_pl_seri_ile_ayni(self):
        K.N0_M = 5
        W = K.pencere(2013)
        m = np.ones(W["n"], bool)
        r = dict(kod="XMD1", Y=2013, W=W, maske=m, katman="tele")
        got = K.n0_cekilisleri([r])[("XMD1", 2013)]
        rng = np.random.default_rng(20261112 + 3)
        ust, A = K.README_TAB["XMD1"]
        exp = [abs(K.KS.dv_uc(K.KS.pl_seri(W["n"], ust, A, rng, np), m, W["i0"], W["iH"], W["iT"], np)["dv"])
               for _ in range(5)]
        np.testing.assert_allclose(got, exp, rtol=1e-9, atol=1e-9)

    def test_b_payda_ve_pay_tohumlari(self):
        K.B_M, K.B_N_PAY, K.B_TAM_N = 7, 4, 4
        W = K.pencere(2018)
        m = np.ones(W["n"], bool); m[200:230] = False
        yps = [dict(kod="ZZZ1", Y=2018, W=W, maske=m, katman="tele", kaynak="DAY"),
               dict(kod="AAA1", Y=2018, W=W, maske=m, katman="tele", kaynak="10MIN")]
        with tempfile.TemporaryDirectory() as d:
            b, f, c = K.denetim_b_c(yps, d)
        rng = np.random.default_rng(20261112 + 1)
        pd = []
        for _ in ("AAA1", "ZZZ1"):                      # kanonik sıra
            X = 3.0 * math.sqrt(1 / 365.25) * np.cumsum(rng.standard_normal((7, W["n"])), axis=1) \
                + 0.1 * rng.standard_normal((7, W["n"]))
            pd.append(np.abs(K.olc(X, m, W, "tele")[0]))
        self.assertAlmostEqual(b["q95_payda"], np.quantile(np.concatenate(pd), .95), places=10)
        pay = []
        for kod in ("AAA1", "ZZZ1"):
            for j in range(2):
                g = np.random.default_rng(int(hashlib.sha256(f"{kod}|2018|{j}".encode()).hexdigest()[:16], 16)
                                          ^ 20261112)
                x = 3.0 * math.sqrt(1 / 365.25) * np.cumsum(g.standard_normal(W["n"])) + 0.1 * g.standard_normal(W["n"])
                pay.append(abs(K.olc(np.round(x, 6), m, W, "tele")[0]))
        self.assertAlmostEqual(b["q95_pay"], np.quantile(pay, .95), places=5)
        self.assertEqual(b["R"], 2)
        self.assertEqual(f["yer_pencere"], 1)
        self.assertLessEqual(f["en_buyuk_fark"], 0.005)
        self.assertTrue(c["gecti"])


class KodDenetimiA(unittest.TestCase):
    def test_a_a3_a4_tam_maske(self):
        with tempfile.TemporaryDirectory() as d:
            W = K.pencere(2013)
            m = np.ones(W["n"], bool)
            mm = np.zeros(W["n"], bool); mm[::25] = True
            yps = [dict(kod="X", Y=2013, katman="tele", maske=m, W=W),
                   dict(kod="Y", Y=2013, katman="man", maske=mm, W=W)]
            a = K.denetim_a(yps, d)
        self.assertTrue(all(a["gecti"].values()), a["gecti"])
        self.assertLessEqual(a["tam_en_buyuk"], 0.005)
        self.assertLess(a["a3_en_buyuk"], 1e-9)
        self.assertLess(a["a4_en_buyuk"], 1e-9)

    def test_a3_ortalamayla_yakalanir(self):
        W = K.pencere(2013)
        x = np.full(W["n"], 3.0); x[W["iT"]] = 503.0
        ort = lambda i: x[i - 15:i + 16].mean()
        v = (ort(W["iT"]) - ort(W["iH"])) / W["tau2"] - (ort(W["iH"]) - ort(W["i0"])) / W["tau3"]
        self.assertTrue(8.0 < v < 8.1)


# ======================================================================== uçtan uca (yapay dünya)
def yapay_dunya(kok, kapsam=lambda k, Y: True, bozuk=None, tohum=7, mic_adim=10):
    """66 dosyalık yapay veri dizini ve manifest. kapsam(k, Y): istasyon-pencerenin okuma aralığında veri olsun mu."""
    T = TL.listeleri_yukle()
    veri = os.path.join(kok, "veri")
    os.makedirs(veri)
    rng = np.random.default_rng(tohum)
    pen = {}
    for k, Y in T["listeler"]["B"]:
        pen.setdefault(k, []).append(Y)
    dos = []
    for k in sorted(T["istasyon"]):
        bas = min(K.pencere(Y)["ilk"] for Y in pen[k]) - dt.timedelta(days=40)
        son = max(K.pencere(Y)["son"] for Y in pen[k]) + dt.timedelta(days=40)
        n = (son - bas).days + 1
        x = K.yapay_rw(n, rng) + 0.02 * np.arange(n)
        maske = np.ones(n, bool)
        i = 0
        while i < n:
            if rng.random() < 0.01:
                L = int(rng.integers(1, 21)); maske[i:i + L] = False; i += L
            i += 1
        acik = np.zeros(n, bool)
        for Y in pen[k]:
            if kapsam(k, Y):
                W = K.pencere(Y)
                acik[(W["ilk"] - bas).days:(W["son"] - bas).days + 1] = True
        for t in K.KAYNAK_SIRA:
            for u in T["istasyon"][k]["dosya"][t]:
                yerel = f"{t}/{u.rsplit('/', 1)[1]}"
                os.makedirs(os.path.join(veri, t), exist_ok=True)
                S = ["# yapay " + k]
                for g in range(n):
                    if not acik[g] or not maske[g] or (t == "MIC" and g % mic_adim):
                        continue
                    d = bas + dt.timedelta(days=g)
                    j = d.timetuple().tm_yday
                    S.append(f"{d.year} {j + (0.5 if t == '10MIN' else 0):g} {x[g]:.2f}")
                S += ["1965 100 1.00", "2024 10 GIZLI", "2025 3 77.7", "2025 4"]       # aralık dışı satırlar
                if bozuk and bozuk == yerel:
                    S.insert(5, "BOZUK SATIR 1.0")
                gz_yaz(os.path.join(veri, yerel), S)
                dos.append(dict(url=u, yerel=yerel, durum="tamam", sha256=K.sha256_dosya(os.path.join(veri, yerel)),
                                boy=os.path.getsize(os.path.join(veri, yerel))))
    man = os.path.join(kok, "manifest.json")
    json.dump(dict(dosyalar=dos, basarisiz=[], basarisiz_pay=0.0), open(man, "w", encoding="utf-8"))
    cik = os.path.join(kok, "cikti")
    isd = os.path.join(kok, "isaret")
    os.makedirs(cik); os.makedirs(isd)
    return veri, man, cik, isd


def kosu_arg(veri, man, cik, isd, tur=0):
    return K.argumanlar(["--veri", veri, "--manifest", man, "--cikti-dizin", cik, "--isaret-depo", isd,
                         "--duzeltme-turu", str(tur)])


class UctanUca(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)
        sabitleri_geri_al()

    def kos(self, a):
        log = []
        kod, s = K.kos(a, log=log.append)
        return kod, s, log

    def test_1_kapi_gecti_baglayici_boyut(self):
        """Bağlayıcı boyut (B = 2000, M = 2000, R = ⌈820/n⌉, N0 2000): süre ve bellek kaydedilir."""
        veri, man, cik, isd = yapay_dunya(self.d)
        t0 = time.time()
        kod, s, log = self.kos(kosu_arg(veri, man, cik, isd))
        sure = time.time() - t0
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        print(f"\n[bağlayıcı boyutta yapay prova] süre {sure:.1f} sn, en yüksek RSS {rss:.0f} MB; "
              f"yer-pencere {s['kapi']['yer_pencere']}, yer {s['kapi']['yer']}, K {s['kapi']['kesim_K']}; "
              f"(b) oran {s['denetim']['b']['oran']:.3f}, R {s['denetim']['b']['R']}; "
              f"144 satır {s['denetim']['f144']['yer_pencere']} yp, fark {s['denetim']['f144']['en_buyuk_fark']:.5f}",
              file=sys.stderr)
        self.assertEqual(kod, 0)
        self.assertTrue(s["kapi"]["gecti"])
        self.assertGreaterEqual(s["kapi"]["kesim_K"], 4)
        self.assertEqual(s["kapi"]["dusme_nedenleri"].get("HDR"), 23)
        self.assertTrue(s["denetim"]["b"]["gecti"])
        self.assertTrue(s["denetim"]["c_gercek"]["gecti"])
        self.assertGreaterEqual(s["denetim"]["f144"]["yer_pencere"], 1)
        h = s["hukum"]
        self.assertRegex(h, r"^TR-10b: taban, README'nin n = 2 istasyonlarının genlik aralığı(ndan büyük|nda|ndan "
                            r"küçük); README modeline göre .*Kural seti B: Orta Kaliforniya sünme ölçerlerinde sakin 5 "
                            r"yıllık pencerelerde 2 yıllık sünme hızı değişimi \|Δv\|, yer-pencerelerin yarısında .* "
                            r"mm/yıl'ı, %5'inde .* \[.*\] mm/yıl'ı aşar \(sünen katmanda hızın .*\); yer \d+, "
                            r"yer-pencere \d+, kesim \d+; aralık fay kesimi bloklu bootstrap, yüzdelik, nominal %90 "
                            r"\(5–6 blokla gerçek kapsama daha düşük\)\. Kural seti A: q95 .* mm/yıl \(yer \d+, "
                            r"yer-pencere \d+; kapı (geçer|altı)\)\.")
        self.assertIn("koşulsuz yanlış alarm eşiğinin alt kestirimidir", s["olcu"]["yanlis_alarm_cumlesi"])
        self.assertIn("Chihshang 2003", s["olcu"]["chihshang_cumlesi"])
        md = open(os.path.join(cik, "tr10b_sonuc.md"), encoding="utf-8").read()
        self.assertIn(h, md)
        self.assertIn(s["olcu"]["yanlis_alarm_cumlesi"], md)
        js = json.load(open(os.path.join(cik, "tr10b_sonuc.json"), encoding="utf-8"))
        self.assertEqual(js["girdi"]["hdr_csv_sha256"], K.HDR_CSV_SHA)
        self.assertEqual(len(js["girdi"]["veri_dosyalari_sha256"]), 66)
        for y in (os.path.join(veri, K.ISARET_AD), os.path.join(isd, K.ISARET_AD)):
            self.assertTrue(os.path.exists(y))
        # işaretlerden önceki log satırlarında Δv yok; yasak cümleler yok
        i = next(j for j, x in enumerate(log) if "işaret dosyaları yazıldı" in x)
        self.assertFalse(any("dv" in x.lower() and "Δv" in x and re.search(r"\d", x) for x in log[:i]
                             if "hesaplanmadı" not in x))
        for yasak in ("İstanbul", "Marmara", "öncül bulundu", "öncül yok", "olasılık"):
            self.assertNotIn(yasak, md)
        # tek koşu: ikinci koşu durur
        with self.assertRaises(K.KosuDur):
            K.kos(kosu_arg(veri, man, cik, isd), log=lambda *_: None)
        os.remove(os.path.join(isd, K.ISARET_AD))
        with self.assertRaises(K.KosuDur):                  # veri dizinindeki işaret de durdurur
            K.kos(kosu_arg(veri, man, os.path.join(self.d, "c2"), isd), log=lambda *_: None)

    def kucult(self):
        K.B_BOOT, K.B_M, K.N0_M, K.B_TAM_N = 300, 300, 300, 2000      # (b) payı bağlayıcı boyutta kalır

    def test_2_kapi_gecmedi_bilgi_satiri(self):
        self.kucult()
        veri, man, cik, isd = yapay_dunya(self.d, kapsam=lambda k, Y: Y == 2018)
        kod, s, log = self.kos(kosu_arg(veri, man, cik, isd))
        self.assertEqual(kod, 0)
        self.assertFalse(s["kapi"]["gecti"])
        self.assertRegex(s["hukum"], r"^TR-10b: veri yok \(kural seti B: yer \d+ / yer-pencere \d+; kapı ≥ 20 / ≥ 40\)"
                                     r"\. Bilgi satırı, kapı altı: \|Δv\| q50 \S+, q95 \S+ \[\S+, \S+\] mm/yıl \(sünen "
                                     r"katmanda hızın %\S+'si \[\S+, \S+\]\); bu satır bir hüküm değildir\.$")
        self.assertNotIn("etiket", s["olcu"])
        self.assertNotIn("chihshang_cumlesi", s["olcu"])
        self.assertIn("kapsam yok", s["kapi"]["dusme_nedenleri"])
        md = open(os.path.join(cik, "tr10b_sonuc.md"), encoding="utf-8").read()
        self.assertIn("[kapı altı]", md)

    def test_3_blok_yetersiz(self):
        self.kucult()
        K.KAPI_YER, K.KAPI_YP = 5, 5
        T = TL.listeleri_yukle()
        uc = {"SAF_Parkfield", "HAY", "CAL_Hollister"}
        veri, man, cik, isd = yapay_dunya(self.d, kapsam=lambda k, Y: T["istasyon"][k]["kesim"] in uc)
        kod, s, _ = self.kos(kosu_arg(veri, man, cik, isd))
        self.assertEqual(kod, 0)
        self.assertEqual(s["kapi"]["kesim_K"], 3)
        self.assertRegex(s["hukum"], r"^TR-10b: blok yetersiz \(K = 3\); etiket yok\. Kural seti B: \|Δv\| q50 \S+, "
                                     r"q95 \S+ mm/yıl \(yer bootstrap'ı aralığı \[\S+, \S+\], bilgi; sünen katmanda "
                                     r"hızın %\S+'si\); README modeline göre ρ_R = \S+ \(nokta değer\); yer \d+, "
                                     r"yer-pencere \d+\. Kural seti A: q95 \S+ mm/yıl \(yer \d+, yer-pencere \d+; kapı "
                                     r"(geçer|altı)\)\.")
        self.assertNotIn("chihshang_cumlesi", s["olcu"])

    def test_4_kod_hatasi_turlar(self):
        self.kucult()
        K.KAPI_YER, K.KAPI_YP = 5, 5
        veri, man, cik, isd = yapay_dunya(self.d)
        eski = K.rho_seri
        K.rho_seri = lambda W: 0.8 * eski(W)               # bilinçli kod hatası: (c-yapay) yakalamalı
        try:
            kod, s, _ = self.kos(kosu_arg(veri, man, cik, isd, tur=0))
            self.assertEqual(kod, 3)
            self.assertFalse(os.path.exists(os.path.join(cik, "tr10b_sonuc.json")))
            self.assertFalse(os.path.exists(os.path.join(isd, K.ISARET_AD)))
            dj = open(os.path.join(cik, "tr10b_denetim_tur0.json"), encoding="utf-8").read()
            self.assertNotIn('"dv"', dj)
            self.assertEqual(s["kod_hata"]["denetim"], "(c-yapay)")
            kod, s, _ = self.kos(kosu_arg(veri, man, cik, isd, tur=2))
        finally:
            K.rho_seri = eski
        self.assertEqual(kod, 0)
        self.assertRegex(s["hukum"], r"^TR-10b: geçersiz \(kod\) \(\(c-yapay\), \S+ / §10\.3\); gerçek Δv "
                                     r"hesaplanmadı\.$")
        self.assertNotIn("olcu", s)
        self.assertFalse(os.path.exists(os.path.join(isd, K.ISARET_AD)))

    def test_5_bicim_hatasi_kosuyu_durdurur(self):
        self.kucult()
        T = TL.listeleri_yukle()
        u = T["istasyon"]["XMM1"]["dosya"]["DAY"][0]
        veri, man, cik, isd = yapay_dunya(self.d, bozuk="DAY/" + u.rsplit("/", 1)[1])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            kod = K.main(["--veri", veri, "--manifest", man, "--cikti-dizin", cik, "--isaret-depo", isd])
        self.assertEqual(kod, 2)
        self.assertIn("ilk sayısal satırdan sonra sayısal olmayan satır", out.getvalue())
        self.assertIn('"***"', out.getvalue())
        self.assertEqual(os.listdir(cik), [])
        self.assertEqual(os.listdir(isd), [])

    def test_6_manifest_sha_uyusmazligi(self):
        veri, man, cik, isd = yapay_dunya(self.d)
        y = os.path.join(veri, "MIC", sorted(os.listdir(os.path.join(veri, "MIC")))[0])
        gz_yaz(y, ["2014 1 1.0"])
        with self.assertRaises(K.KosuDur):
            K.kos(kosu_arg(veri, man, cik, isd), log=lambda *_: None)
        j = json.load(open(man))
        j["dosyalar"] = j["dosyalar"][1:]
        json.dump(j, open(man, "w"))
        with self.assertRaisesRegex(K.KosuDur, "66 dosya"):
            K.kos(kosu_arg(veri, man, cik, isd), log=lambda *_: None)

    def test_7_indirme_payi(self):
        veri, man, cik, isd = yapay_dunya(self.d)
        j = json.load(open(man))
        for r in j["dosyalar"][:4]:
            r["durum"] = "hata"
        json.dump(j, open(man, "w"))
        with self.assertRaisesRegex(K.KosuDur, "%5"):
            K.kos(kosu_arg(veri, man, cik, isd), log=lambda *_: None)


# ======================================================================== indirme betiği (yerel yapay sunucu)
class Indirme(unittest.TestCase):
    def test_yerel_sunucu(self):
        ls = I.dosya_listesi()
        self.assertEqual(len(ls), 66)
        with tempfile.TemporaryDirectory() as d:
            kok = os.path.join(d, "sunucu")
            istek = {}
            yasak = ls[3]["url"].split("escweb.wr.usgs.gov", 1)[1]
            for x in ls:
                p = os.path.join(kok, x["url"].split("escweb.wr.usgs.gov/", 1)[1])
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "wb").write(hashlib.sha256(x["url"].encode()).digest() * 10)

            class Isleyici(http.server.SimpleHTTPRequestHandler):
                def __init__(s, *a, **k):
                    super().__init__(*a, directory=kok, **k)

                def do_GET(s):
                    istek[s.path] = istek.get(s.path, 0) + 1
                    istek["ua"] = s.headers.get("User-Agent")
                    if s.path == yasak:
                        s.send_error(403)
                        return
                    super().do_GET()

                def log_message(s, *a):
                    pass
            sv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Isleyici)
            th = threading.Thread(target=sv.serve_forever, daemon=True)
            th.start()
            try:
                hedef, man = os.path.join(d, "hedef"), os.path.join(d, "m.json")
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    kod = I.main(["--hedef", hedef, "--manifest", man, "--bekle", "0",
                                  "--url-onek", f"https://escweb.wr.usgs.gov/=http://127.0.0.1:{sv.server_port}/"])
                self.assertEqual(kod, 0)                     # 1/66 < %5
                m = json.load(open(man))
                self.assertEqual(m["basarisiz"], [ls[3]["url"]])
                self.assertEqual(istek[yasak], 1)            # 403 yeniden denenmez
                self.assertNotIn("python", istek["ua"].lower())
                for r in m["dosyalar"]:
                    if r["durum"] == "tamam":
                        self.assertEqual(r["sha256"], K.sha256_dosya(os.path.join(hedef, r["yerel"])))
                        self.assertTrue(r["url"].startswith("https://escweb.wr.usgs.gov/"))
                with self.assertRaises(SystemExit):          # manifest var: tek indirme
                    I.main(["--hedef", os.path.join(d, "h2"), "--manifest", man, "--bekle", "0"])
                with self.assertRaises(SystemExit):          # hedef depo içinde
                    I.main(["--hedef", os.path.join(BURA, "veri_yok"), "--manifest", os.path.join(d, "m2.json")])
                self.assertFalse(os.path.exists(os.path.join(BURA, "veri_yok")))
            finally:
                sv.shutdown()


if __name__ == "__main__":
    unittest.main()
