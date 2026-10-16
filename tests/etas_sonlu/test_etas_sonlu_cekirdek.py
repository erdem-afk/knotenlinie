"""Sonlu kaynak çekirdeği: bilinen doğrultulu sentetik dünya, kütle, R eşitliği."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.etas import model as M
from knotenlinie.etas_sonlu.model import (SonluKaskad, dugum_sayisi, serit_noktalari)
from knotenlinie.etas_sonlu.wc94 import kirik_boyu_km
from knotenlinie.kaskad.arayuz import KaskadETAS
from knotenlinie.ortak_zemin.arayuz import DuzETAS
from knotenlinie.ortak_zemin.veri import IZGARA


def _ayar(kutu, grid):
    la0, la1, lo0, lo1 = kutu
    return dict(parametreler=dict(mu=.05, K=.02, c=.03, alpha=.45, p=1.3, D=2.0, q=1.8, gamma=.2),
                mc=2.5, b={'deger': 1.0}, kutu=kutu,
                normalizasyon=M.NORMALIZASYON, metrik=M.yerel_metrik(kutu).kayit(),
                baslangic_yili=1985, ayar_baslangic='1985-01-01T00:00:00Z',
                ayar_bitis='2011-01-01T00:00:00Z',
                arka_plan=dict(x_kenar=[lo0, (lo0 + lo1) / 2, lo1],
                               y_kenar=[la0, (la0 + la1) / 2, la1],
                               yogunluk=[[0.25, 0.25], [0.25, 0.25]]))


class TestCekirdek(unittest.TestCase):
    def setUp(self):
        la0, la1, lo0, lo1 = 39.5, 41.5, 11.5, 13.5
        self.kutu = (la0, la1, lo0, lo1)
        n = 20
        rows = []
        for i in range(n):
            for j in range(n):
                rows.append([lo0 + j * .1, lo0 + (j + 1) * .1, la0 + i * .1, la0 + (i + 1) * .1])
        self.grid = pd.DataFrame(np.round(rows, 12), columns=IZGARA)
        self.p = _ayar(self.kutu, self.grid)

    def test_wc94_sabitler(self):
        self.assertAlmostEqual(float(kirik_boyu_km(5.0)), 3.235936569296281, places=9)
        self.assertAlmostEqual(float(kirik_boyu_km(6.3)), 18.92343618644974, places=9)
        self.assertAlmostEqual(float(kirik_boyu_km(5.5)), 6.3826348619054825, places=9)
        with self.assertRaises(ValueError):
            kirik_boyu_km(np.nan)

    def test_dugum_sayisi_tek_ve_sinirli(self):
        for L, D in ((19., 4.8), (6.4, 3.9), (3.2, 3.0), (100., .5)):
            k = dugum_sayisi(L, D)
            self.assertEqual(k % 2, 1)
            self.assertGreaterEqual(k, 3)
            self.assertLessEqual(k, 15)

    def test_kutle_korunumu(self):
        met = M.yerel_metrik(self.kutu)
        mw = 6.3
        L = float(kirik_boyu_km(mw))
        D_i = float(M.mekan_olcegi(self.p['parametreler']['D'], self.p['parametreler']['gamma'], [mw], 2.5)[0])
        lon, lat, K = serit_noktalari(12.5, 40.5, 35.0, L, met, D_i)
        full = M.mekan_hucre_integralleri(lon, lat, np.full(K, D_i), self.p['parametreler']['q'],
                                          self.kutu, metrik=met, blok=K)
        izo = M.mekan_hucre_integralleri([12.5], [40.5], [D_i], self.p['parametreler']['q'],
                                         self.kutu, metrik=met, blok=1)[0]
        # Şerit kütlesi düğüm kütlelerinin ortalamasıdır: yapay kütle yok.
        self.assertAlmostEqual(float(full.mean(axis=0).sum()), float(full.sum(axis=(1, 2)).mean()), places=12)
        # İç şeritte toplam, izotrop toplama göre %0,1'den az sapar (sonlu kutu kenarı).
        self.assertLess(abs(float(full.mean(axis=0).sum()) - float(izo.sum())) / float(izo.sum()), 1e-3)

    def test_toplu_gecis_fftconvolve_ile_ayni(self):
        from scipy.signal import fftconvolve
        taban = DuzETAS(self.p, self.grid)
        s = SonluKaskad(taban, yon=None, adim=32, nesil=10)
        rng = np.random.default_rng(3)
        blok = rng.normal(0, 1e-3, (4, len(self.grid)))
        refs = []
        for v in range(4):
            f = np.zeros(s.shape)
            f[s.iy, s.ix] = blok[v]
            refs.append(fftconvolve(f, s.kernel, mode='same')[s.iy, s.ix])
        np.testing.assert_allclose(s._gecis_blok(blok), np.stack(refs), rtol=0, atol=1e-12)
        np.testing.assert_allclose(s._gecis_isaretli(blok[0]), refs[0], rtol=0, atol=1e-12)

    def test_temel_kaskad_ile_ayni(self):
        taban = DuzETAS(self.p, self.grid)
        base = KaskadETAS(taban, adim=32, nesil=10)
        sonlu = SonluKaskad(taban, yon=None, adim=32, nesil=10)
        a = pd.Timestamp('2011-01-01', tz='UTC')
        z = a + pd.Timedelta(days=1)
        h = pd.DataFrame(dict(
            zaman=pd.to_datetime(['2010-12-31', '2010-12-31T12:00:00', '2010-12-30'],
                                 utc=True, format='mixed'),
            boylam=[12.05, 12.45, 12.15], enlem=[40.05, 40.45, 40.15],
            derinlik=[10., 10., 10.], mw=[3.2, 3.0, 5.8]))
        edges = np.r_[np.round(np.arange(2.95, 9., .1), 2), np.inf]
        ob = base.beklenen(a, z, h, self.grid, edges)
        os, ctx = sonlu.temel(a, z, h, self.grid, edges)
        np.testing.assert_allclose(ob, os, rtol=0, atol=0)
        d = sonlu.duzeltme(ctx, 'b', 5.0)
        self.assertIsNone(d, 'yon işaretçisi yokken düzeltme sıfır olmalı')

    def test_sifir_boylu_serit_izotropa_esit(self):
        """L -> 0 ise şerit satırı R'nin izotrop satırına eşit (indeks/hizalama denetimi)."""
        taban = DuzETAS(self.p, self.grid)
        sonlu = SonluKaskad(taban, yon=None, adim=32, nesil=10)
        a = pd.Timestamp('2011-01-01', tz='UTC')
        z = a + pd.Timedelta(days=1)
        h = pd.DataFrame(dict(
            zaman=pd.to_datetime(['2010-12-30', '2010-12-31'], utc=True, format='mixed'),
            boylam=[12.15, 12.45], enlem=[40.15, 40.45], derinlik=[10., 10.], mw=[5.8, 3.0]))
        edges = np.r_[np.round(np.arange(2.95, 9., .1), 2), np.inf]
        _, ctx = sonlu.temel(a, z, h, self.grid, edges)
        j = int(np.argmax(ctx['h'].mw.to_numpy(float)))
        yon = dict(merkez_lon=12.15, merkez_lat=40.15, dogrultu=33.0)
        satir = sonlu._serpme(5.8, yon, 1e-9, ('t', 0))
        np.testing.assert_allclose(satir, ctx['spatial'][j], rtol=1e-9, atol=1e-15)
        # Gerçek boylu şerit aynı kütleyi başka hücrelere dağıtır: toplam ~ korunur.
        uzun = sonlu._serpme(5.8, yon, float(kirik_boyu_km(5.8)), ('t', 1))
        self.assertGreater(float(np.abs(uzun - satir).max()), 0.0)
        self.assertLess(abs(float(uzun.sum()) - float(satir.sum())) / float(satir.sum()), 2e-2)

    def test_sonlu_logL_izotroptan_yuksek(self):
        rng = np.random.default_rng(7)
        mw = 6.2
        L = float(kirik_boyu_km(mw))
        D_i = float(M.mekan_olcegi(2.0, 0.2, [mw], 2.5)[0])
        met = M.yerel_metrik(self.kutu)
        dogrultu = 35.0
        lon, lat, K = serit_noktalari(12.5, 40.5, dogrultu, L, met, D_i)
        # Şeritten çocuk üret: düğüm seç, Ogata radyal çekirdeğinden yarıçap örnekle.
        sec = rng.integers(0, K, 3000)
        q = 1.8
        # Ters CDF: F(r)=1-(1+r^2/D^2)^(1-q); u ile r^2 = D^2((1-u)^(1/(1-q))-1)
        u = rng.random(3000)
        r = D_i * np.sqrt(np.maximum((1 - u) ** (1.0 / (1.0 - q)) - 1.0, 0.0))
        aci = rng.random(3000) * 2 * np.pi
        x = met.km(lon[sec], lat[sec])[0] + r * np.cos(aci)
        y = met.km(lon[sec], lat[sec])[1] + r * np.sin(aci)
        # km -> derece
        elon = 12.5 + (x - met.km(12.5, 40.5)[0]) / met.kx
        elat = 40.5 + (y - met.km(12.5, 40.5)[1]) / met.ky
        g_iso = M.mekan_cekirdegi((met.km(elon, elat)[0] - met.km(12.5, 40.5)[0]) ** 2
                                  + (met.km(elon, elat)[1] - met.km(12.5, 40.5)[1]) ** 2,
                                  D_i, q, 0.0, np.array([2.5]), 2.5)
        g_fin = np.zeros(len(elon))
        for k in range(K):
            xk, yk = met.km(lon[k], lat[k])
            g_fin += M.mekan_cekirdegi((met.km(elon, elat)[0] - xk) ** 2
                                       + (met.km(elon, elat)[1] - yk) ** 2,
                                       D_i, q, 0.0, np.array([2.5]), 2.5)
        g_fin /= K
        self.assertGreater(float(np.log(g_fin).sum()), float(np.log(g_iso).sum()))


if __name__ == '__main__':
    unittest.main()
