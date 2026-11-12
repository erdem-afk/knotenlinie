#!/usr/bin/env python3
"""TR-6a sınamaları: yalnız yapay veri (numpy + standart kitaplık; `python3 -I -B`). Ağ kullanılmaz; gerçek önbellek,
gerçek sonlu fay ürünü ya da olay sonrası katalog açılmaz.

Kapsam: Okada (§3.3 1-9, tekil), sonlu fay ayrıştırma/sağlama, katalog katmanı (tarih/körlük, satır sınırı, büyüklük
kuralları, MAXC, Mc_lob, Mc_son, GK + 730 g tampon, oy), p₀ ve testere dişi (JSON ile eşitlik), hüküm adı kapalı
listesi, git aşama denetimi, uçtan uca çok birimli yapay dünya (manifest → olay sonrası → hüküm), yapay Dieterich
sınaması (geliştirme tohumu, küçük boy), tamlık sınaması (geliştirme) ve en az 6 mutasyon.

Kullanım: python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py [-k ad] [--hizli]
"""
import contextlib
import datetime as dt
import io
import itertools
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import urllib.error

import numpy as np

BURAYA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURAYA)
import tr6_a_kapi as KAPI            # noqa: E402
import tr6a_onkayit_sayilar as S     # noqa: E402
import tr6a_okada as OK              # noqa: E402
import tr6a_ffm as FFM               # noqa: E402
import tr6a_katalog as KAT           # noqa: E402
import tr6a_kosu as KO               # noqa: E402
import tr6a_yapay as Y               # noqa: E402

HIZLI = "--hizli" in sys.argv
_DUNYA = {}


def dunya(ad="h1", **kw):
    """Önbellekli uçtan uca yapay dünya: (liste, dunya, analiz, manifest, R, H)."""
    if ad in _DUNYA:
        return _DUNYA[ad]
    liste, spec, d = Y.coklu_dunya(**kw)
    an = KO.Analiz(liste, Y.YapayKaynak(d, "on"), log=lambda *a: None)
    an.hazirla()
    an.on_katalog()
    an.katalog_secimi()
    m = json.loads(KO.json_metni(an.manifest()))
    R = H = None
    if m["durum"] == "devam":
        an.son_ekle(m["son_indirme_plani"], Y.YapayKaynak(d, "son"))
        R = an.oylar(m)
        H = KO.hukum_kur(m, R, an)
    _DUNYA[ad] = (liste, d, an, m, R, H)
    return _DUNYA[ad]


# ================================================================== Okada
class TOkada(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = OK.dogrulama(n_nokta=60 if HIZLI else 200)

    def test_harfiyen_gecenler(self):
        for k in ("1_yuzey_cekme", "2_denge", "4_sayisal_turev", "5_nokta_kaynak_001km", "7_ust_uste_binme",
                  "8a_isaret_uc_pozitif_yan_negatif", "8b_simetri", "8c_dondurme", "9_dcff_izdusumu",
                  "tekil_noktalar_sonlu"):
            self.assertTrue(self.r[k]["gecti"], k)

    def test_harfiyen_tutmayanlar_tani_ile(self):
        """Sınama 3, 6 (±1e−6 W farkı 2ε ∂u/∂n taşır) ve 5 uzak alan (dört kutup terimi): harfiyen ölçüt tutmuyor,
        Richardson tanısı ve 40L normalize tanısı doğru kodu gösteriyor (okuma 3; Ek 1 kararı bekliyor)."""
        self.assertLess(self.r["3_kayma_sureksizligi"]["tani_richardson"], 1e-10)
        self.assertLess(self.r["6_fay_disi_sureklilik"]["tani_richardson"], 1e-10)
        self.assertLess(self.r["bilgi_uzak_alan_nokta_integrali"]["deger"], 1e-4)
        self.assertEqual(self.r["tablo_durumu"], "Okada 1992 tablo değerleri doğrulanamadı")

    def test_dcff_izdusumu_9(self):
        dcff_izdusumu_sinamasi(self)

    def test_izgara_sonlu_ve_tekil(self):
        T = Y.TekBirimSinama(M=7.0)
        H = T.B["H"]
        self.assertTrue(np.all(np.isfinite(H["dA"])) and np.all(np.isfinite(H["dB"])))
        self.assertGreater(T.B["hucre"]["golge"], 0)
        self.assertGreater(T.B["hucre"]["tekil_yakin_alan_toplam"], 0)
        self.assertFalse(np.any(T.B["M"]["golge"] & H["tekil"]))
        self.assertFalse(np.any(T.B["M"]["notr"] & H["tekil"]))


def dcff_izdusumu_sinamasi(tc):
    s = 7.0
    for (ij, (dog, egim, rake), tau, sn) in (
            ((0, 1), (0.0, 90.0, 180.0), -s, 0.0),
            ((0, 0), (0.0, 90.0, 180.0), 0.0, s),
            ((0, 2), (0.0, 30.0, 90.0), -0.5 * s, math.sqrt(3) / 2 * s)):
        sig = np.zeros((3, 3))
        sig[ij] = sig[ij[::-1]] = s
        t_, n_, c_ = OK.dcff(sig, dog, egim, rake)
        tc.assertAlmostEqual(float(t_), tau, delta=1e-12 * s)
        tc.assertAlmostEqual(float(n_), sn, delta=1e-12 * s)
        tc.assertAlmostEqual(float(c_), tau + 0.4 * sn, delta=1e-12 * s)


# ================================================================== sonlu fay
PARAM = """#Total number of fault_segments=     1
#Fault_segment =   1 nx(Along-strike)=   2 Dx= 10.00km ny(downdip)=   1 Dy=  5.00km
#Boundary of Fault_segment     1. EQ in cell (1,1). Lon:  20.0000   Lat:  10.0000
#Lon.  Lat.  Depth
  20.0  10.0  0.0
#Lat. Lon. depth slip rake strike dip t_rup t_ris t_fal mo
  10.0000  20.0000  5.0000  100.0  180.0  0.0  90.0  0.0  1.0  1.0  {mo1}
  10.0900  20.0000  5.0000  200.0  180.0  0.0  90.0  0.0  1.0  1.0  {mo2}
"""


def param_metni(mo_carpan=1.0, baslik=""):
    mo = lambda s: 30e9 * s * 10e3 * 5e3 * 1e7 * mo_carpan       # noqa: E731  (dyn·cm)
    return baslik + PARAM.format(mo1=f"{mo(1.0):.4e}", mo2=f"{mo(2.0):.4e}")


class TFFM(unittest.TestCase):
    def test_param_ayristir_ve_birim(self):
        r = FFM.param_ayristir(param_metni())
        self.assertEqual(len(r["altfaylar"]), 2)
        self.assertAlmostEqual(r["altfaylar"][1]["kayma"], 2.0)
        FFM.birim_denetimi(r["altfaylar"])
        with self.assertRaises(FFM.BicimHata):
            FFM.birim_denetimi(FFM.param_ayristir(param_metni(mo_carpan=1e-3))["altfaylar"])

    def test_koordinat_ve_M0_karari_yoksa_durur(self):
        with self.assertRaises(FFM.BicimHata):
            FFM.coz(param_metni(), "basic_inversion.param")

    def test_baslikla_moment_saglamasi(self):
        M0 = 30e9 * 3.0 * 10e3 * 5e3
        b = f"# Coordinates are the center of each subfault\n# Mo = {M0 * 1e7:.4e} dyne.cm\n"
        r = FFM.coz(param_metni(baslik=b), "basic_inversion.param")
        self.assertEqual(r["koordinat"], "merkez")
        self.assertAlmostEqual(r["moment"]["oran"], 1.0, places=3)
        b2 = f"# Coordinates are the center of each subfault\n# Mo = {M0 * 1.2e7:.4e} dyne.cm\n"
        with self.assertRaises(FFM.VeriYok):
            FFM.coz(param_metni(baslik=b2), "basic_inversion.param")

    def test_indir_ve_arsiv_sha(self):
        M0 = 30e9 * 3.0 * 10e3 * 5e3
        dosya = param_metni(baslik=f"# Coordinates are the center of each subfault\n# Mo = {M0 * 1e7:.4e} dyne.cm\n")
        detay = dict(properties=dict(products={"finite-fault": [
            dict(id="u1", code="c1", source="us", updateTime=1, contents={
                "basic_inversion.param": dict(url="https://x/param")}),
            dict(id="u0", code="c0", source="us", updateTime=0, contents={})]}))

        def getir(u):
            return json.dumps(detay).encode() if "eventid" in u else dosya.encode()
        with tempfile.TemporaryDirectory() as d:
            k = FFM.indir("ev1", d, getir, simdi="2026-11-12T00:00:00+00:00")
            self.assertEqual(k["durum"], "indirildi")
            self.assertEqual(k["urun"]["id"], "u1")
            self.assertEqual([x["id"] for x in k["oteki_urunler"]], ["u0"])
            r = FFM.arsivden_oku(k, d)
            self.assertEqual(r["n_altfay"], 2)
            with open(os.path.join(d, k["dosya"]["yerel"]), "a") as f:
                f.write("#\n")
            with self.assertRaises(FFM.BicimHata):
                FFM.arsivden_oku(k, d)
            with self.assertRaises(FileExistsError):       # "xb": ikinci indirme üzerine yazmaz
                FFM.indir("ev1", d, getir)


# ================================================================== katalog katmanı ve körlük
def fdsn(satirlar):
    b = "#EventID|Time|Latitude|Longitude|Depth/km|Author|Catalog|Contributor|ContributorID|MagType|Magnitude|" \
        "MagAuthor|EventLocationName|EventType\n"
    return b + "".join("|".join(map(str, s)) + "\n" for s in satirlar)


class TKatalog(unittest.TestCase):
    def test_2026_istegi_yapilamaz(self):
        with self.assertRaises(KAT.KorIhlal):
            KAT.tarih_denetle(dt.datetime(2025, 1, 1), dt.datetime(2026, 1, 1))
        with self.assertRaises(KAT.KorIhlal):
            KAT.tarih_denetle(dt.datetime(2026, 1, 2), dt.datetime(2026, 2, 1))
        KAT.tarih_denetle(dt.datetime(2025, 1, 1), dt.datetime(2025, 12, 31, 23, 59, 59))
        cagri = []
        with self.assertRaises(KAT.KorIhlal):
            KAT.parcali_indir(KAT.SERVIS["ComCat"], 0, 0, 100, dt.datetime(2025, 6, 1), dt.datetime(2026, 1, 1, 0, 0, 1),
                              3.0, lambda u: cagri.append(u) or b"")
        self.assertEqual(cagri, [])               # ağa hiç gidilmedi

    def test_gercek_kaynak_asama_siniri_aga_gitmeden(self):
        with tempfile.TemporaryDirectory() as d:
            k = KO.GercekKaynak(d, "on", bekleme=0)
            k.getir._ac = lambda *a, **kw: (_ for _ in ()).throw(AssertionError("ağa gidildi"))
            b = dict(id="x", zaman="2015-06-01T00:00:00")
            with self.assertRaises(KAT.KorIhlal):
                k.katalog(b, "ISC", dt.datetime(2014, 1, 1), dt.datetime(2015, 6, 1), 3.0, 100, (0, 0), "on")
            k2 = KO.GercekKaynak(d, "son", bekleme=0)
            k2.getir._ac = k.getir._ac
            with self.assertRaises(KAT.KorIhlal):
                k2.katalog(b, "ISC", dt.datetime(2025, 6, 1), dt.datetime(2026, 3, 1), 3.0, 100, (0, 0), "son")

    def test_gercek_kaynak_sahte_ag_ve_gunluk(self):
        """Ağ yolu sahte açıcıyla: parçalı istek, kendi indirmesini okuma (sha256), günlükten sürdürme (yeni istek
        yok)."""
        import urllib.parse as up
        cagri = []

        class Yanit(io.BytesIO):
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def ac(req, timeout=None):
            cagri.append(req.full_url)
            q = dict(up.parse_qsl(up.urlsplit(req.full_url).query))
            a = dt.datetime.fromisoformat(q["starttime"])
            s = [(f"e{a:%Y}", f"{a:%Y-%m-%d}T01:00:00", 0.1, 0.1, 10, "", "", "", "", "ML", "3.1", "", "", "earthquake")]
            return Yanit(fdsn(s).encode())
        b = dict(id="x", zaman="2015-06-01T00:00:00")
        with tempfile.TemporaryDirectory() as d:
            k = KO.GercekKaynak(d, "on", bekleme=0)
            k.getir._ac = ac
            r = k.katalog(b, "ISC", dt.datetime(2012, 1, 1), dt.datetime(2015, 5, 2), 3.0, 100, (0, 0), "on")
            n1 = len(cagri)
            self.assertEqual(n1, 4)
            self.assertEqual(len(r["id"]), 4)
            k2 = KO.GercekKaynak(d, "on", bekleme=0)
            k2.getir._ac = ac
            r2 = k2.katalog(b, "ISC", dt.datetime(2012, 1, 1), dt.datetime(2015, 5, 2), 3.0, 100, (0, 0), "on")
            self.assertEqual(len(cagri), n1)                 # günlükten; yeni istek yok
            self.assertEqual(list(r2["id"]), list(r["id"]))
            self.assertEqual(len(k2.kayit["katalog"]), 1)
            ark = KO.ArsivKaynak(d, k2.kayit)
            r3 = ark.katalog(b, "ISC", None, None, 3.0, 100, (0, 0), "on")
            self.assertEqual(list(r3["id"]), list(r["id"]))

    def test_403_atlatilmaz_ve_UA(self):
        gor = []

        def ac(req, timeout=None):
            gor.append(req.get_header("User-agent"))
            raise urllib.error.HTTPError(req.full_url, 403, "yasak", {}, None)
        with tempfile.TemporaryDirectory() as d:
            g = KAT.Getirici(d, bekleme=0, ac=ac)
            with self.assertRaises(RuntimeError):
                g("https://example.invalid/fdsnws/event/1/query?x=1")
        self.assertEqual(len(gor), 1)
        self.assertEqual(gor[0], KAT.UA)
        self.assertNotRegex(KAT.UA, r"@|knotenlinie|tr6")

    def test_satir_siniri_bolme_ve_veri_yok(self):
        def getir_yogun(u):
            import urllib.parse as up
            q = dict(up.parse_qsl(up.urlsplit(u).query))
            a, b = dt.datetime.fromisoformat(q["starttime"]), dt.datetime.fromisoformat(q["endtime"])
            n = int((b - a).total_seconds() / 86400 * 120)
            return ("x\n" * min(n, KAT.LIMIT)).encode()
        r = KAT.parcali_indir(KAT.SERVIS["ISC"], 0, 0, 100, dt.datetime(2010, 1, 1), dt.datetime(2011, 1, 1), 3.0,
                              getir_yogun)
        self.assertGreaterEqual(r["bolunen"], 1)
        self.assertTrue(all(KAT.SERVIS["ISC"].satir_say(m) < KAT.LIMIT_PAY * KAT.LIMIT for _, m in r["metinler"]))
        with self.assertRaises(KAT.VeriYok):
            KAT.parcali_indir(KAT.SERVIS["ISC"], 0, 0, 100, dt.datetime(2010, 1, 1), dt.datetime(2010, 1, 2), 3.0,
                              lambda u: ("x\n" * KAT.LIMIT).encode())

    def test_geonet_yari_esitligi(self):
        import urllib.parse as up
        olay_g = np.sort(np.random.default_rng(1).uniform(0, 366, 500))
        t0 = dt.datetime(2010, 1, 1)

        def getir(u, kes=False):
            q = dict(up.parse_qsl(up.urlsplit(u).query))
            a = (dt.datetime.fromisoformat(q["starttime"]) - t0).total_seconds() / 86400
            b = (dt.datetime.fromisoformat(q["endtime"]) - t0).total_seconds() / 86400
            n = int(((olay_g >= a) & (olay_g <= b)).sum())
            if kes and b - a > 100:
                n = min(n, 100)                 # sunucu kesmesi: bütün eksik döner
            return ("x\n" * n).encode()
        r = KAT.parcali_indir(KAT.SERVIS["GeoNet"], 0, 0, 100, t0, t0 + dt.timedelta(days=366), 3.0, getir)
        self.assertEqual(r["bolunen"], 0)
        r = KAT.parcali_indir(KAT.SERVIS["GeoNet"], 0, 0, 100, t0, t0 + dt.timedelta(days=366), 3.0,
                              lambda u: getir(u, True))
        self.assertGreater(r["bolunen"], 0)
        self.assertEqual(sum(KAT.SERVIS["GeoNet"].satir_say(m) for _, m in r["metinler"]), len(olay_g))

    def test_ayristirma_ve_buyukluk_kurallari(self):
        s = [("a", "2010-01-01T00:00:00", 1, 2, 10, "", "", "", "", "ML", "0.0", "", "", "earthquake"),
             ("b", "2010-01-02T00:00:00", 1, 2, 10, "", "", "", "", "", "0", "", "", "earthquake"),
             ("c", "2010-01-03T00:00:00", 1, 2, 10, "", "", "", "", "", "", "", "", "earthquake"),
             ("d", "2010-01-04T00:00:00", 1, 2, 10, "", "", "", "", "mb", "2.9", "", "", "earthquake"),
             ("e", "2010-01-05T00:00:00", 1, 2, "", "", "", "", "", "mb", "3.0", "", "", "earthquake"),
             ("f", "2026-01-01T00:00:00", 1, 2, 10, "", "", "", "", "mb", "5.0", "", "", "earthquake"),
             ("g", "2010-01-06T00:00:00", 1, 2, 10, "", "", "", "", "mb", "5.0", "", "", "quarry blast")]
        d = KAT.fdsn_ayristir(fdsn(s))
        self.assertEqual(list(d["id"]), ["a", "b", "c", "d", "e"])          # 2026 ve patlama atıldı
        self.assertEqual(d["de"][4], 10.0)
        tut, say = KAT.buyukluk_kurallari(d, -1.0)
        self.assertEqual(say, dict(kural1=1, kural2=1, kural3=0))
        self.assertTrue(tut[0])                                             # türü dolu sıfır tutulur
        tut, say = KAT.buyukluk_kurallari(d, 2.95)
        self.assertEqual(list(np.array(d["id"])[tut]), ["e"])
        with self.assertRaises(KAT.BicimHata):
            KAT.fdsn_ayristir("a|b|c\n")

    def test_maxc_mc_lob(self):
        rng = np.random.default_rng(2)
        m = np.round(rng.exponential(0.43, 400) + 3.0, 1)
        v, c = KAT.hist(m)
        self.assertEqual(KAT.maxc(m), KAT.maxc_sayim(v, c))
        self.assertEqual(KAT.maxc(np.array([3.0, 3.1, 3.1, 3.0])), 3.0)       # eşitlikte küçük
        self.assertEqual(KAT.mc_lob(m[:49], 2.5)[0], 2.8)
        self.assertEqual(KAT.mc_lob(m, 2.5)[0], KAT.r2(max(2.5, KAT.maxc(m) + 0.2)))
        self.assertEqual(KAT.mc_lob(m, 3.6)[0], 3.6)

    def test_mc_son_alt_pencere(self):
        mc_son_sinamasi(self)

    def test_alt_pencereler(self):
        self.assertEqual(KAT.alt_pencereler(0, 365, "A2"), [(30, 45), (45, 60), (60, 90), (90, 180), (180, 365)])
        self.assertEqual(KAT.alt_pencereler(0, 100, "A2"), [(30, 45), (45, 60), (60, 90), (90, 100)])
        self.assertEqual(KAT.alt_pencereler(0, 365, "yedek_c"), [(90, 180), (180, 365)])
        self.assertEqual(KAT.alt_pencereler(10, 375, "yedek_a")[0], (40, 50))

    def test_gk_esdegerlik(self):
        rng = np.random.default_rng(3)
        for _ in range(15):
            n = int(rng.integers(2, 1500))
            t = np.sort(rng.uniform(0, 2000, n))
            la, lo = rng.uniform(-1, 1, n), rng.uniform(-1, 1, n)
            m = np.round(rng.exponential(0.43, n) + 2.0, 1)
            self.assertTrue(np.array_equal(KAT.kumesizlestir(t, la, lo, m), KAT.kumesizlestir_basvuru(t, la, lo, m)))

    def test_tampon_730(self):
        tampon_sinamasi(self)

    def test_oy_tablo_esitligi(self):
        oy = S.Oy(2000)
        for n in range(1, 400, 3):
            for ns in range(0, n + 1, max(1, n // 25)):
                D, A = KAT.oy(n - ns, ns, oy.pi)
                self.assertEqual(D, int(ns <= oy.b_dus[n]))
                self.assertEqual(A, int(ns >= oy.b_art[n]))
            self.assertLessEqual(KAT.p_dusus_kosullu(n, oy.pi), 0.5 + 1e-12)
        self.assertEqual(KAT.oy(0, 0, 0.157), (0, 0))

    def test_kor_maske_ve_onbellek_engeli(self):
        havuz = [dict(id="A", zaman="2010-01-01T00:00:00", enlem=0.0, boylam=0.0, L_km=50.0)]
        d = dict(t=np.array([KAT.gun("2010-02-01T00:00:00"), KAT.gun("2009-12-01T00:00:00"),
                             KAT.gun("2010-02-01T00:00:00")]), la=np.array([0.5, 0.5, 5.0]), lo=np.zeros(3),
                 m=np.ones(3))
        self.assertEqual(list(KAT.kor_maske(d, havuz, sahip="B")), [False, True, True])
        self.assertEqual(list(KAT.kor_maske(d, havuz, sahip="A")), [True, True, True])
        with tempfile.TemporaryDirectory() as dd:
            open(os.path.join(dd, ".tr6a_kor"), "w").close()
            with self.assertRaises(Exception):
                KAPI.getir("https://example.invalid/x", dd)

    def test_open_denetimi(self):
        """§9 adım 3 / İNCELEME-2 K8: önbelleği ya da ön ham dizinleri açabilecek `open(` çağrıları listelenir;
        katalog katmanında yalnız kendi_indirmesini_oku (ve Getirici'nin yazması) açar."""
        izin = {"tr6a_katalog.py": {"Getirici.__init__", "Getirici.__call__",
                                    "kendi_indirmesini_oku"},
                "tr6a_ffm.py": {"indir", "arsivden_oku"}}
        for dosya, izinli in izin.items():
            kaynak = open(os.path.join(BURAYA, dosya), encoding="utf-8").read().splitlines()
            fonk, sinif = None, None
            for s in kaynak:
                mm = re.match(r"^(class|def) (\w+)", s)
                if mm:
                    sinif = mm.group(2) if mm.group(1) == "class" else None
                    fonk = mm.group(2)
                mm = re.match(r"^    def (\w+)", s)
                if mm and sinif:
                    fonk = f"{sinif}.{mm.group(1)}"
                if re.search(r"\bopen\(", s) and not s.strip().startswith("#"):
                    self.assertIn(fonk, izinli, f"{dosya}: {fonk} open( çağırıyor")


def mc_son_sinamasi(tc):
    k = np.round(np.arange(2.0, 6.0, 0.1), 1)

    def h(tepe, n):
        c = np.zeros(len(k))
        c[np.argmin(np.abs(k - tepe))] = n
        return k, c
    ms, d = KAT.mc_son_hist([h(3.5, 60), h(3.0, 60), h(2.5, 60)], 2.7)
    tc.assertEqual(ms, 3.7)                                            # en kötü alt pencere
    ms, d = KAT.mc_son_hist([h(4.0, 20), h(3.0, 40), h(2.5, 60)], 2.7)
    tc.assertEqual(ms, 3.2)                                            # 20+40 birleşti, tepe 3.0 (40 > 20)
    tc.assertEqual([g["n"] for g in d["gruplar"]], [60, 60])
    ms, d = KAT.mc_son_hist([h(3.0, 60), h(4.0, 30)], 2.7)
    tc.assertEqual(ms, 3.2)                                            # sonuncu öncekiyle birleşti: tepe 3.0
    ms, d = KAT.mc_son_hist([h(3.0, 10), h(4.0, 30)], 2.7)
    tc.assertEqual(ms, 3.0)                                            # hiçbir birleşim 50'ye ulaşmadı: Mc_lob + 0,3
    ms, _ = KAT.mc_son_hist([h(3.5, 60)], 2.7, KAT.MC_SON_EK["yedek_b"])
    tc.assertEqual(ms, 3.9)


def tampon_sinamasi(tc):
    """Ön tampon (730 g) içindeki büyük lob olayı, ön pencerenin başındaki bağımlı olayı siler ama sayılmaz."""
    t0 = 10000.0
    E = dict(t=np.array([t0 - 1826 - 100, t0 - 1826 + 20, t0 - 1000]), la=np.zeros(3), lo=np.zeros(3),
             m=np.array([6.0, 3.0, 3.0]), h=np.zeros(3, np.int64), ana_sok=np.zeros(3, bool))
    ev = np.ones(3, bool)
    n_on = KO.Analiz.say(E, ev, (t0 - 1826, t0 - 30), None, None, 3.0)[0]
    tc.assertEqual(n_on, 1)
    n_ham = KO.Analiz.say(E, ev, (t0 - 1826, t0 - 30), None, None, 3.0, kumesiz=False)[0]
    tc.assertEqual(n_ham, 2)


# ================================================================== p₀, testere dişi, tablolar
class TSayilar(unittest.TestCase):
    def test_p0_yuvarlama(self):
        p0_sinamasi(self)

    def test_testere_json_ve_fonksiyon(self):
        js = KO.p0_izgarasi()
        for p0s, x in js.items():
            p0 = float(p0s)
            for K in range(23, 81):
                t = KO.testere(K, p0)
                self.assertEqual(t["K_hukum"], x["testere"][str(K)]["K_hukum"])
                uygun = [k for k in range(23, K + 1) if S.guc(k, p0) >= S.GUC]
                kh = max(uygun) if uygun else K
                self.assertEqual(t["K_hukum"], kh, (p0, K))
        self.assertEqual(KO.testere(24, 0.50)["K_hukum"], 23)
        self.assertEqual(KO.testere(28, 0.51)["K_hukum"], 26)
        self.assertTrue(KO.testere(23, 0.52)["tasarim_alti"])
        self.assertEqual(KO.testere(85, 0.50)["K_hukum"], 85)

    def test_binom_tablolari_json_esitligi(self):
        with open(KO.SAYILAR_JSON, encoding="utf-8") as f:
            js = json.load(f)
        self.assertEqual(KO.sha256_dosya(KO.SAYILAR_JSON), KO.SAYILAR_JSON_SHA)
        yeni = json.loads(json.dumps(S.p0_izgarasi()))
        self.assertEqual(yeni, js["p0_izgarasi"])
        bt = json.loads(json.dumps(S.binom_tablosu(range(18, 61))))
        self.assertEqual(bt, js["binom"])
        self.assertEqual(json.loads(json.dumps(S.c_le_h())), js["c_le_h"])

    def test_en_zayif_sirasi(self):
        k = [dict(temsilci=x) for x in ("a", "b", "c", "d")]
        N0 = dict(a=40.0, b=35.0, c=35.0, d=50.0)
        self.assertEqual([c["temsilci"] for c in KO.en_zayif_sirasi(k, N0)], ["c", "b", "a", "d"])

    def test_taban_c_le_h(self):
        self.assertIn(49, S.c_le_h()["0.50"])
        c, h = S.kritik(49, 0.5), S.esik_H0(49)
        self.assertLessEqual(c, h)
        self.assertEqual(KO.taban_hukum(49, c, 0.5)[0], "H1")
        self.assertEqual(KO.taban_hukum(23, 13, 0.5)[0], "H0")
        self.assertEqual(KO.taban_hukum(23, 15, 0.5)[0], "ayırt edilemez")


def p0_sinamasi(tc):
    tc.assertEqual(KO.p0_kestir(29, 58), (0.50, False))
    tc.assertEqual(KO.p0_kestir(30, 59), (0.51, False))       # ⌈100·30/59⌉ = ⌈50,85⌉ = 51
    tc.assertEqual(KO.p0_kestir(20, 60), (0.50, False))       # taban 0,50
    tc.assertEqual(KO.p0_kestir(37, 60), (0.62, False))       # 61,67 -> 62
    tc.assertEqual(KO.p0_kestir(10, 29), (0.52, True))        # J < 30: taban 0,52
    tc.assertEqual(KO.p0_kestir(16, 29), (0.56, True))        # 55,17 -> 56
    tc.assertEqual(KO.p0_kestir(0, 0), (0.52, True))
    tc.assertEqual(KO.p0_kestir(51, 100), (0.51, False))
    tc.assertEqual(KO.p0_kestir(301, 600), (0.51, False))     # 50,17 -> 51 (tamsayı aritmetiği)


# ================================================================== hüküm adı kapalı listesi (§6.4)
SAYI = r"\d+,\d{2,3}"
NIT = ["pozitif kontrol koşulamadı", "negatif kontrol koşulamadı", "nötr kontrol koşulamadı|nötr kontrolden ayrışmadı",
       "megathrust kümelerine dayanıyor", f"tasarım gücünün altında: güç {SAYI}",
       rf"kalibrasyon zayıf: J = \d+, p₀ = {SAYI}"]
DUS = ["pozitif kontrol tutmadı", "olay öncesi düşüş eğilimi", "nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu"]
EKLER = [r"ters yön notu: gölgede anlamlı artış \(Y = \d+ ≥ c⁺ = \d+\)|ters yön sınanamadı \(p̂₀⁺ = " + SAYI + r"\)",
         "pozitif kontrol de tutmadı: hat ya da model başarısız; ayrılamaz",
         "olay öncesi artış eğilimiyle ayırt edilemez",
         r"oy Mc'si kapı Mc'sinin belirgin üstünde: K kümenin \d+'inde etkin N0_kul < 31,36",
         rf"\(tasarım gücünün altında: güç {SAYI}\)", rf"\(kalibrasyon zayıf: J = \d+, p₀ = {SAYI}\)"]


def kapali_listede(ad):
    """§6.4 dilbilgisi: sabit adlar | H1 (niteleyiciler, sırayla) | ayırt edilemez (düşürücüler, sırayla) |
    H0/ayırt edilemez — ekler (sırayla)."""
    sabit = {"güç yok", "güç yok (ölçü yanlı)"} | {f"koşulmadı (yöntem: {y})" for y in KO.YONTEMLER}
    if ad in sabit or ad == "H1":
        return True

    def sirali(parcalar, desenler):
        i = 0
        for p in parcalar:
            while i < len(desenler) and not re.fullmatch(desenler[i], p):
                i += 1
            if i == len(desenler):
                return False
            i += 1
        return True
    m = re.fullmatch(r"H1 \((.+)\)", ad)
    if m:
        return sirali(m.group(1).split("; "), NIT)
    m = re.fullmatch(r"ayırt edilemez \((.+)\)", ad)
    if m:
        return sirali(m.group(1).split("; "), DUS)
    m = re.fullmatch(r"(H0|ayırt edilemez)( — (.+))?", ad)
    if m:
        if not m.group(3):
            return True
        ekler = re.split(r"; (?=ters yön|pozitif kontrol de|olay öncesi artış|oy Mc'si|\(tasarım|\(kalibrasyon)",
                         m.group(3))
        return sirali(ekler, EKLER)
    return False


class THukum(unittest.TestCase):
    def test_kapali_liste_tum_bilesimler(self):
        n = 0
        for taban in ("H1", "H0", "ayırt edilemez"):
            for S1, S7 in itertools.product(("tuttu", "tutmadı", "koşulamadı"),
                                            ("koşulamadı", "düşüş", "ayrışmadı", "ayrıştı")):
                for s2d, s2a, s2k, s4, tas, kz, ty, et in itertools.product(
                        (0, 1), (0, 1), (0, 1), (0, 1), (None, 0.654), (None, (25, 0.52)),
                        (None, ("not", 18, 17), ("sınanamadı", 0.633)), (None, (14, 23))):
                    f = dict(taban=taban, S1=S1, S2_dusus=bool(s2d), S2_artis=bool(s2a), S2_kosulamadi=bool(s2k),
                             S7=S7, S4_dayanir=bool(s4), tasarim_alti_guc=tas, kalib_zayif=kz, ters_yon=ty,
                             etkin_N0=et)
                    H = KO.hukum_adi(f)
                    self.assertTrue(kapali_listede(H["ad"]), H["ad"])
                    n += 1
        for t in ("guc_yok", "olcu_yanli"):
            self.assertTrue(kapali_listede(KO.hukum_adi(dict(taban=t))["ad"]))
        for y in KO.YONTEMLER:
            self.assertTrue(kapali_listede(KO.hukum_adi(dict(taban="yontem", yontem=y))["ad"]))
        self.assertGreater(n, 10000)
        self.assertFalse(kapali_listede("H1 (zayıf)"))
        self.assertFalse(kapali_listede("H1 (tasarım gücünün altında: güç 0,654; pozitif kontrol koşulamadı)"))

    def test_metindeki_ornekler(self):
        f = dict(taban="H1", S1="tutmadı", S7="düşüş", S2_dusus=False, S2_artis=False, S2_kosulamadi=False)
        self.assertEqual(KO.hukum_adi(f)["ad"],
                         "ayırt edilemez (pozitif kontrol tutmadı; nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu)")
        f = dict(taban="H1", S1="tuttu", S7="ayrışmadı", S2_kosulamadi=False, tasarim_alti_guc=0.654)
        H = KO.hukum_adi(f)
        self.assertEqual(H["ad"], "H1 (nötr kontrolden ayrışmadı; tasarım gücünün altında: güç 0,654)")
        self.assertFalse(H["tasinir"])
        H = KO.hukum_adi(dict(taban="H1", S1="tuttu", S7="ayrıştı", tasarim_alti_guc=0.654))
        self.assertTrue(H["tasinir"])
        self.assertIn("Marmara'ya taşınan tek cümle", KO.marmara_satiri(H))

    def test_marmara_mutlak_olasilik_yok(self):
        for f in (dict(taban="H1", S1="tuttu", S7="ayrıştı"), dict(taban="H1", S1="koşulamadı", S7="ayrıştı"),
                  dict(taban="H0", S1="tuttu", S7="ayrıştı"), dict(taban="guc_yok")):
            s = KO.marmara_satiri(KO.hukum_adi(f)).replace("§13", "")
            self.assertNotRegex(s, r"\d|%|olasılık|yıl içinde")
            self.assertNotIn("İstanbul", s)


# ================================================================== git aşama denetimi
class TGit(unittest.TestCase):
    def test_commit_ve_push_denetimi(self):
        if shutil.which("git") is None:
            self.skipTest("git yok")
        with tempfile.TemporaryDirectory() as d:
            uzak, yerel = os.path.join(d, "uzak.git"), os.path.join(d, "yerel")
            run = lambda *a, cwd=None: subprocess.run(a, cwd=cwd, capture_output=True, text=True, check=True)  # noqa
            run("git", "init", "-q", "--bare", uzak)
            run("git", "init", "-q", yerel)
            run("git", "-C", yerel, "config", "user.email", "t@t")
            run("git", "-C", yerel, "config", "user.name", "t")
            y = os.path.join(yerel, "manifest.json")
            open(y, "w").write("{}")
            eski = KO.DEPO
            KO.DEPO = yerel
            try:
                with self.assertRaises(KO.KosuDur):
                    KO.git_denetle([y], log=lambda *a: None)          # commit yok
                run("git", "-C", yerel, "add", "manifest.json")
                run("git", "-C", yerel, "commit", "-qm", "m")
                with self.assertRaises(KO.KosuDur):
                    KO.git_denetle([y], log=lambda *a: None)          # upstream yok
                run("git", "-C", yerel, "remote", "add", "origin", uzak)
                run("git", "-C", yerel, "push", "-q", "-u", "origin", "HEAD")
                KO.git_denetle([y], log=lambda *a: None)
                open(y, "w").write("{\"x\": 1}")
                with self.assertRaises(KO.KosuDur):
                    KO.git_denetle([y], log=lambda *a: None)          # değişiklik commit edilmemiş
                run("git", "-C", yerel, "commit", "-qam", "m2")
                with self.assertRaises(KO.KosuDur):
                    KO.git_denetle([y], log=lambda *a: None)          # push edilmemiş
            finally:
                KO.DEPO = eski

    def test_okada_ek1_karari_yoksa_manifest_acilmaz(self):
        sin = dict(okada=dict(gecti=False), yapay_katalog=dict(gecti=True), tamlik=dict(secilen="A2"))
        with self.assertRaises(KO.KosuDur):
            KO.sinama_degerlendir(sin)
        sin["okada"]["gecti"] = True
        self.assertEqual(KO.sinama_degerlendir(sin), (None, "A2"))
        sin["tamlik"]["secilen"] = None
        self.assertEqual(KO.sinama_degerlendir(sin)[0]["yontem"], "tamlık sınaması")
        sin["yapay_katalog"]["gecti"] = False
        self.assertEqual(KO.sinama_degerlendir(sin)[0]["yontem"], "yapay katalog sınaması")
        self.assertEqual(KO.erken_hukum("yontem", sinama=dict(yontem="tamlık sınaması", olcut="x"))["hukum"]["ad"],
                         "koşulmadı (yöntem: tamlık sınaması)")

    def test_baglayici_tohum_gelistirmede_reddedilir(self):
        for t in Y.BAGLAYICI_TOHUMLAR:
            with self.assertRaises(ValueError):
                Y.gelistirme_sinamalari(tohum=t, n=1, okada=False, katalog=False, tamlik=False)


# ================================================================== uçtan uca yapay dünya
class TUctanUca(unittest.TestCase):
    def test_manifest_yalniz_olay_oncesi(self):
        liste, d, an, m, R, H = dunya()
        # manifest boyunca hiçbir istek t0 − 30 g'yi aşmadı ve "son" istek yok
        kay = Y.YapayKaynak(d, "on")
        an2 = KO.Analiz(liste, kay, log=lambda *a: None)
        an2.hazirla()
        an2.on_katalog()
        an2.katalog_secimi()
        an2.manifest()
        for (u, k, a, b, asama) in kay.istekler:
            self.assertEqual(asama, "on")
            self.assertLessEqual(b, dt.datetime.fromisoformat(an2.birim[u]["zaman"]) - dt.timedelta(days=30))
        with self.assertRaises(KO.KosuDur):
            an2.oylar(m)                                   # olay sonrası veri eklenmeden oy sayılamaz
        with self.assertRaises(KAT.KorIhlal):              # "on" kaynağından t0 sonrası istenemez
            b = an2.birim["y05"]
            kay.katalog(b, "ISC", dt.datetime.fromisoformat(b["zaman"]),
                        dt.datetime.fromisoformat(b["zaman"]) + dt.timedelta(days=100), 2.0, 100, (0, 0), "on")

    def test_manifest_kurallari(self):
        liste, d, an, m, R, H = dunya()
        cik = {c["temsilci"]: c["neden"] for c in m["cikan"]}
        self.assertTrue(cik[S.BILINEN_CIKAN[0]].startswith("bilinen"))
        self.assertTrue(cik["y03"].startswith("kısa"))                 # havuz olayıyla 29 g'ye kesildi
        self.assertNotIn("y04", cik)                                   # 69 g: kalır
        self.assertAlmostEqual(m["birimler"]["y04"]["T_son_g"], 69.0, places=3)
        self.assertEqual(m["birimler"]["y04"]["kesme"]["olay"], "havuz4")
        self.assertEqual(m["K_kapi"], 24)
        self.assertEqual(m["testere"]["K_hukum"], 23)
        self.assertEqual(len(m["ana_kumeler"]), 23)
        self.assertEqual(m["sahte"]["p0"], KO.p0_kestir(m["sahte"]["S"], m["sahte"]["J"])[0])
        self.assertTrue(all(N >= KO.ESIK[19.0] for u, N in m["kapi_N0"].items() if u in m["kapi_birim"]))
        dusuk = [u for u in m["kapi_N0"] if u not in m["kapi_birim"]]
        self.assertEqual(len(dusuk), 3)
        # grup: iki üye, t_s kayması 2 g
        self.assertEqual(liste["birimler"][2]["uyeler"], ["y02", "y02b"])
        self.assertTrue(set(x["birim"] for x in m["son_indirme_plani"]) >= set(m["ana_kumeler"]))

    def test_hukum_ve_satirlar(self):
        liste, d, an, m, R, H = dunya()
        self.assertTrue(kapali_listede(H["hukum"]["ad"]))
        self.assertEqual(H["hukum"]["taban"], "H1")        # kalıcı −10 kPa dünyası, N0 60
        T = H["satirlar"]
        self.assertEqual(T["ana"]["K"], 23)
        self.assertGreaterEqual(T["ana"]["X"], T["ana"]["c_p0"])
        self.assertGreaterEqual(T["S1"]["X"], S.kritik(T["S1"]["K"], 0.5))
        self.assertIsNotNone(T["B1"])
        self.assertEqual(T["B1"]["K"], 24)
        self.assertTrue(T["S6"]["kosulamadi"])
        for r in R["ana"]:
            self.assertEqual(r["katalog"], an.B[r["temsilci"]]["secim"])
            self.assertGreaterEqual(r["mc_kul"], r["mc_lob"])
        md = KO.sonuc_md(m, H, R, dict(x="y"))
        self.assertIn("| ana | 23 |", md)
        self.assertNotRegex(md, r"İstanbul.*\d+ ?%")

    def test_sifir_dunyasi_ve_guc_yok(self):
        liste, d, an, m, R, H = dunya("sifir", tohum=9, dtau="sifir", n_gecen=24)
        self.assertNotEqual(H["hukum"]["taban"], "H1") if H else None
        liste, d, an, m, R, H = dunya("az", tohum=10, n_gecen=10, n_dusuk=2, ozel=False)
        self.assertEqual(m["durum"], "güç yok")
        self.assertEqual(m["son_indirme_plani"], [])
        self.assertIsNone(m["testere"])
        self.assertEqual(KO.erken_hukum("guc_yok", m=m)["hukum"]["ad"], "güç yok")

    def test_tamlik_kaybi_mc_son(self):
        """Bilinen tamlık kaybı: Mc(t) = M − 4,5 − 0,75 log10 t ve bölge artçıları; alt pencere Mc_son Mc_lob'un
        üstüne çıkar ve oy Mc_kul ile sayılır."""
        T = Y.TekBirimSinama(M=8.0, mc=1.0)
        rng = np.random.default_rng(12)
        r = T.deneme(rng, dict(N0=300.0, dtau="sifir", ikincil_bolge=True, tamlik=dict(ap=0.9)), sahte=False)
        self.assertGreater(r["mc_son"], r["mc_lob"] + 1.0)
        self.assertEqual(r["mc_kul"], r["mc_son"])

    def test_kuru_prova_yapay_son_veri(self):
        liste, d, an, m, R, H = dunya()
        an2 = KO.Analiz(liste, Y.YapayKaynak(d, "on"), log=lambda *a: None)
        an2.hazirla()
        an2.on_katalog()
        an2.katalog_secimi()
        m2 = json.loads(KO.json_metni(an2.manifest()))
        self.assertEqual(KO.cekirdek(m2), KO.cekirdek(m))   # yeniden hesap çekirdeği aynı
        an2.son_ekle(m2["son_indirme_plani"], KO.yapay_son_veri(an2, m2["son_indirme_plani"]))
        R2 = an2.oylar(m2)
        KO.sonuc_md(m2, KO.hukum_kur(m2, R2, an2), R2, {})


# ================================================================== yapay Dieterich ve tamlık (geliştirme boyu)
class TYapaySinama(unittest.TestCase):
    def test_yapay_katalog_gelistirme(self):
        n = 60 if HIZLI else 250
        r = Y.yapay_katalog_sinamasi(tohum=77, n=n, log=lambda *a: None)
        for o in r["olcutler"]:
            self.assertLessEqual(abs(o["z"]), 4.5, o)

    def test_tamlik_hucre_ornegi(self):
        oy = S.Oy(60000, S.T_ON_G, 335)
        rng = np.random.default_rng(5)
        p = Y.tamlik_hucresi(rng, 200, 7.0, 3.0, 100.0, 0.9, "A2", oy)
        p0 = oy.olasilik(100 * S.T_ON_G / 365.25, 100 * 335 / 365.25, -1)
        self.assertLess(p - p0, 0.1)


# ================================================================== mutasyonlar (≥ 6)
@contextlib.contextmanager
def yama(nesne, ad, deger):
    eski = getattr(nesne, ad)
    setattr(nesne, ad, deger)
    try:
        yield
    finally:
        setattr(nesne, ad, eski)


def lob_esigi_sinamasi(tc):
    H = dict(r_k=np.array([30.0, 30, 30, 30, 30, 30, 10]), tekil=np.zeros(7, bool),
             dA=np.array([-9.0, -10.0, -10.5, 10.0, 2.0, -2.5, -50.0]), dB=np.full(7, -20.0))
    M = KO.hucre_maskeleri(H, 50.0)
    tc.assertEqual(list(M["golge"]), [False, True, True, False, False, False, False])
    tc.assertEqual(list(M["pozitif"]), [False, False, False, True, False, False, False])
    tc.assertEqual(list(M["notr"]), [False, False, False, False, True, False, False])


def kesme_sinamasi(tc):
    liste, d, an, m, R, H = dunya()
    B = an.B["y04"]
    tc.assertAlmostEqual(B["son_bit"], KAT.gun(an.olay["havuz4"]["zaman"]) - 1.0, places=9)


MUTASYONLAR = [
    ("ΔCFF işareti", lambda: yama(OK, "dcff", (lambda f: (lambda *a, **k: tuple(-x for x in f(*a, **k))))(OK.dcff)),
     dcff_izdusumu_sinamasi),
    ("sürtünme katsayısı 0,6", lambda: yama(OK, "dcff", (lambda f: (lambda s, d, e, r, mu_s=0.6: f(s, d, e, r, mu_s)))(
        OK.dcff)), dcff_izdusumu_sinamasi),
    ("lob eşiği 8 kPa", lambda: yama(S, "DTAU_ESIK", 8.0), lob_esigi_sinamasi),
    ("Mc_son havuzlanmış (sürüm 1) kuralı", lambda: yama(KAT, "mc_son_hist", lambda hs, mc, ek=0.2: (
        KAT.r2(KAT.maxc_sayim(*KAT.hist(np.concatenate([np.repeat(h[0], h[1].astype(int)) for h in hs]))) + ek),
        {})), mc_son_sinamasi),
    ("Mc_son eki 0", lambda: yama(KAT, "mc_son_hist", (lambda f: (lambda hs, mc, ek=0.2: f(hs, mc, 0.0)))(
        KAT.mc_son_hist)), mc_son_sinamasi),
    ("kümesizleştirme tamponu 0", lambda: yama(KAT, "TAMPON_G", 0), tampon_sinamasi),
    ("p₀ yuvarlama (yukarı değil en yakın)", lambda: yama(KO, "p0_kestir", lambda Ss, J: (
        (max(0.50, round(100 * Ss / J) / 100), False) if J >= 30 else (max(0.52, round(100 * Ss / J) / 100), True))
        if J else (0.52, True)), p0_sinamasi),
    ("§3.7 kesmesi bir gün önce değil aynı gün", None, kesme_sinamasi),
]


class TMutasyon(unittest.TestCase):
    def test_mutasyonlar_yakalanir(self):
        yakalanan = []
        for ad, yap, sinama in MUTASYONLAR:
            if yap is None:
                continue
            with yap():
                try:
                    sinama(self)
                except AssertionError:
                    yakalanan.append(ad)
                    continue
            self.fail(f"mutasyon yakalanmadı: {ad}")
        self.assertGreaterEqual(len(yakalanan), 6)
        # mutasyonsuz hâlde aynı sınamalar geçer
        for _, _, sinama in MUTASYONLAR:
            sinama(self)

    def test_kesme_mutasyonu(self):
        liste, d, an, m, R, H = dunya()
        B = an.B["y04"]
        eski = B["son_bit"]
        B["son_bit"] = eski + 1.0                     # mutasyon: aynı gün
        try:
            with self.assertRaises(AssertionError):
                kesme_sinamasi(self)
        finally:
            B["son_bit"] = eski


if __name__ == "__main__":
    argv = [a for a in sys.argv if a != "--hizli"]
    unittest.main(argv=argv, verbosity=2)
