"""STEP arayüzü: kütle korunumu, artımlı durum tutarlılığı, defter–koşucu logL eşleşmesi."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.kosucu import Model, kos
from knotenlinie.skor_defteri.defter import kos_defter
from knotenlinie.step.arayuz import EPOCH, MC, STEP
from knotenlinie.step.cekirdek import omori_integral
from tests.step.test_step_ayar import sentetik_dizi

LON0, LAT0, N = 10.0, 41.0, 30
KENAR = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
T0 = pd.Timestamp('2006-01-01', tz='UTC')


def dunya(tohum=5):
    """Sentetik İtalya: 3°x3° kutu, 900 hücre; 1985–2006-02 arası arka plan + RJ dizileri."""
    rng = np.random.default_rng(tohum)
    lo = LON0 + 0.1 * (np.arange(N)[None, :] + np.zeros((N, 1)))
    la = LAT0 + 0.1 * (np.arange(N)[:, None] + np.zeros((1, N)))
    g = pd.DataFrame(dict(boylam_min=lo.ravel(), boylam_max=lo.ravel() + 0.1,
                          enlem_min=la.ravel(), enlem_max=la.ravel() + 0.1))
    gun = float((pd.Timestamp('2006-02-01', tz='UTC') - EPOCH) / pd.Timedelta(days=1))
    n = rng.poisson(0.7 * gun)
    t = np.sort(rng.random(n) * gun)
    m = 2.5 - np.log10(1 - rng.random(n))
    rows = [(x, LON0 + 0.2 + 2.6 * rng.random(), LAT0 + 0.2 + 2.6 * rng.random(), y) for x, y in zip(t, m)]
    ek = []
    for (x, lo_, la_, y) in rows:
        if y >= 4.0:
            s = sentetik_dizi(rng, y, -1.7, 1.0, 1.0, 0.02, 120.0)
            for tt, mm in zip(s.uye_t, s.uye_m):
                if x + tt < gun:
                    ek.append((x + tt, np.clip(lo_ + 0.08 * rng.standard_normal(), LON0 + 0.01, LON0 + 2.99),
                               np.clip(la_ + 0.08 * rng.standard_normal(), LAT0 + 0.01, LAT0 + 2.99), mm))
    rows += ek
    k = pd.DataFrame(rows, columns=['t', 'boylam', 'enlem', 'mw'])
    k['zaman'] = EPOCH + pd.to_timedelta(k.t, unit='D')
    k['derinlik'] = 8.0
    k = k.sort_values('zaman').reset_index(drop=True)
    return k[['zaman', 'enlem', 'boylam', 'derinlik', 'mw']], g


class STEPTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kat, cls.g = dunya()
        cls.ayar = cls.kat[cls.kat.zaman < T0]
        cls.m = STEP(cls.ayar, cls.g, son=T0, mseq=4.0, n_min=8, n0=5.0)

    def test_ayar_makul(self):
        j = self.m.jen
        self.assertTrue(j['yakinsadi'])
        self.assertAlmostEqual(j['b'], 1.0, delta=0.12)
        self.assertAlmostEqual(j['p'], 1.0, delta=0.15)
        self.assertAlmostEqual(j['a'], -1.7, delta=0.25)

    def test_kutle_korunumu(self):
        # Geçmiş yalnız tek M=5 ana şok (merkezde, 2 gün önce): toplam = arka plan + A·10^(-b·2,95)
        a = T0 + pd.Timedelta(days=3)
        ana = pd.DataFrame(dict(zaman=[a - pd.Timedelta(days=2)], enlem=[42.5], boylam=[11.5],
                                derinlik=[8.0], mw=[5.0]))
        out = self.m.beklenen(a, a + pd.Timedelta(days=1), ana, self.g, KENAR)
        j, b = self.m.jen, self.m.jen['b']
        A = 10.0 ** (j['a'] + b * 5.0) * float(omori_integral(2.0, 3.0, j['c'], j['p']))
        bb, mu = self.m.arka['b'], self.m.arka['mu_gun']
        beklenen = A * 10.0 ** (-b * 2.95) + mu * self.m.bg_hucre.sum() * 10.0 ** (-bb * (2.95 - MC))
        self.assertAlmostEqual(float(out.sum()) / beklenen, 1.0, places=9)
        self.assertTrue((out >= 0).all())
        self.assertEqual(out.shape, (len(self.g), len(KENAR) - 1))
        # arka plan hücre kütleleri kutuyu doldurur (toplam 1)
        self.assertAlmostEqual(float(self.m.bg_hucre.sum()), 1.0, places=9)

    def test_artimli_durum_taze_kurulumla_ayni(self):
        gunler = [T0 + pd.Timedelta(days=d) for d in range(0, 20)]
        m1 = STEP(self.ayar, self.g, son=T0, mseq=4.0, n_min=8, n0=5.0)
        # 2006 Ocak'a kadar gerçek ayar verisinin son ayında yeterli dizi bulunsun diye geçmişi 2005 sonuna kaydır
        hepsi = self.kat
        son = None
        for a in gunler:
            son = m1.beklenen(a, a + pd.Timedelta(days=1), hepsi[hepsi.zaman < a], self.g, KENAR)
        a = gunler[-1]
        m2 = STEP(self.ayar, self.g, son=T0, mseq=4.0, n_min=8, n0=5.0)
        taze = m2.beklenen(a, a + pd.Timedelta(days=1), hepsi[hepsi.zaman < a], self.g, KENAR)
        np.testing.assert_allclose(son, taze, rtol=1e-12, atol=0)

    def test_sizinti_ve_kapilar(self):
        from knotenlinie.karsilastir.puan import PuanHatasi
        a = T0 + pd.Timedelta(days=1)
        gelecek = pd.DataFrame(dict(zaman=[a + pd.Timedelta(hours=1)], enlem=[42.0], boylam=[11.0],
                                    derinlik=[8.0], mw=[4.0]))
        with self.assertRaises(PuanHatasi):
            self.m.beklenen(a, a + pd.Timedelta(days=1), gelecek, self.g, KENAR)
        with self.assertRaises(PuanHatasi):
            self.m.beklenen(T0 - pd.Timedelta(days=1), T0, self.ayar.iloc[:0], self.g, KENAR)

    def test_defter_kosucu_logL_esles(self):
        ayar = dict(sinir=(LON0, LON0 + 3.0, LAT0, LAT0 + 3.0), baslangic_yil=1985, derinlik_max=30)
        bas, son = T0, T0 + pd.Timedelta(days=25)
        hedef = self.kat[(self.kat.zaman >= bas) & (self.kat.zaman < son) & (self.kat.mw >= 2.95)]
        self.assertGreater(len(hedef), 5)
        m1 = STEP(self.ayar, self.g, son=T0, mseq=4.0, n_min=8, n0=5.0)
        m2 = STEP(self.ayar, self.g, son=T0, mseq=4.0, n_min=8, n0=5.0)
        r = kos([Model('STEP', m1.beklenen, True, ayar)], bas, son, self.kat, self.g, KENAR,
                derinlik=(0, 30))['STEP']
        d = kos_defter([Model('STEP', m2.beklenen, True, ayar)], bas, son, self.kat, self.g, KENAR,
                       derinlik=(0, 30))['STEP']
        self.assertTrue(np.isfinite(r.logL))
        self.assertAlmostEqual(d.logL / r.logL, 1.0, places=9)
        self.assertLess(abs(d.logL - r.logL), 1e-9 * abs(r.logL))
        # gün dosyası toplamı = koşucunun toplam beklenen sayısı
        self.assertAlmostEqual(float(d.gun['Lam295'].sum()), float(r.beklenen.sum()), places=8)


class Varyantlar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kat, cls.g = dunya()
        cls.ayar = cls.kat[cls.kat.zaman < T0]

    def test_mm_kes_kutle(self):
        m = STEP(self.ayar, self.g, son=T0, mseq=4.0, mm_kes=True)
        a = T0 + pd.Timedelta(days=3)
        ana = pd.DataFrame(dict(zaman=[a - pd.Timedelta(days=2)], enlem=[42.5], boylam=[11.5],
                                derinlik=[8.0], mw=[5.0]))
        out = m.beklenen(a, a + pd.Timedelta(days=1), ana, self.g, KENAR)
        j, b = m.jen, m.jen['b']
        A = 10.0 ** (j['a'] + b * 5.0) * float(omori_integral(2.0, 3.0, j['c'], j['p']))
        bb, mu = m.arka['b'], m.arka['mu_gun']
        bek = (A * (10.0 ** (-b * 2.95) - 10.0 ** (-b * 5.0)) +
               mu * m.bg_hucre.sum() * 10.0 ** (-bb * (2.95 - MC)))
        self.assertAlmostEqual(float(out.sum()) / bek, 1.0, places=9)
        # M>=5 kutuları ana şok büyüklüğünde kesilir: yalnız arka plan kalır
        j5 = int(np.flatnonzero(np.isclose(KENAR, 5.05))[0])
        bg5 = (mu * m.bg_hucre.sum() * 10.0 ** (-bb * (5.05 - MC)))
        self.assertLess(float(out[:, j5:].sum()), bg5 * 1.0001)

    def test_hiyerarsi_mc_kaynak_defter_kosucu(self):
        ay = dict(sinir=(LON0, LON0 + 3.0, LAT0, LAT0 + 3.0), baslangic_yil=1985, derinlik_max=30)
        kw = dict(son=T0, mseq=3.0, hiyerarsi=True, mc_kaynak=2.5, kaynak_bas='2005-01-01')
        m1, m2 = STEP(self.ayar, self.g, **kw), STEP(self.ayar, self.g, **kw)
        bas, son = T0, T0 + pd.Timedelta(days=25)
        r = kos([Model('STEP-h', m1.beklenen, True, ay)], bas, son, self.kat, self.g, KENAR,
                derinlik=(0, 30))['STEP-h']
        d = kos_defter([Model('STEP-h', m2.beklenen, True, ay)], bas, son, self.kat, self.g, KENAR,
                       derinlik=(0, 30))['STEP-h']
        self.assertTrue(np.isfinite(r.logL))
        self.assertLess(abs(d.logL - r.logL), 1e-9 * abs(r.logL))

    def test_mc_kaynak_yalniz_2005_sonrasi(self):
        m = STEP(self.ayar, self.g, son=T0, mseq=4.0, mc_kaynak=2.5)
        k = m._suz(self.kat)
        eski = k[k.zaman < pd.Timestamp('2005-01-01', tz='UTC')]
        yeni = k[k.zaman >= pd.Timestamp('2005-01-01', tz='UTC')]
        self.assertGreaterEqual(float(eski.mw.min()), MC - 1e-9)
        self.assertLess(float(yeni.mw.min()), MC)
        self.assertGreaterEqual(float(yeni.mw.min()), 2.5 - 1e-9)


if __name__ == '__main__':
    unittest.main()
