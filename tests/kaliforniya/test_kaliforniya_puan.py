"""Skor zinciri (satir/IG/Holm/yıl bloğu) bilinen cevaplı sentetik dünyada."""
import types
import unittest

import numpy as np
import pandas as pd

from knotenlinie.kaliforniya import veri
from knotenlinie.karsilastir import uzun_ad as U


def sahte_baglam(nx=6, ny=5):
    s = [(-120.0 + 0.1 * i, -119.9 + 0.1 * i, 34.0 + 0.1 * j, 34.1 + 0.1 * j)
         for i in range(nx) for j in range(ny)]
    izg = pd.DataFrame(s, columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])
    return types.SimpleNamespace(izgara=izg)


def dunya(b, lam_gercek, tohum):
    """lam_gercek (hücre×41 kutu) beklenenli Poisson dünyası: olay tablosu."""
    rng = np.random.default_rng(tohum)
    n = rng.poisson(lam_gercek)
    ci, mi = np.nonzero(n)
    rep = n[ci, mi]
    ci, mi = np.repeat(ci, rep), np.repeat(mi, rep)
    g = b.izgara.to_numpy()
    lo = (g[ci, 0] + g[ci, 1]) / 2
    la = (g[ci, 2] + g[ci, 3]) / 2
    m = np.where(mi < 40, 5.0 + 0.1 * mi, 9.2)                    # kutu ortası: 4.95+0.1k+0.05
    t = pd.Timestamp('2011-01-01', tz='UTC') + pd.to_timedelta(rng.random(len(ci)) * 3650, unit='D')
    return pd.DataFrame({'zaman': t, 'enlem': la, 'boylam': lo, 'derinlik': 5.0, 'mw': m})


class SatirTesti(unittest.TestCase):
    def test_bilinen_ig(self):
        b = sahte_baglam()
        rng = np.random.default_rng(3)
        mag = 10 ** (-0.9 * 0.1 * np.arange(41))
        gercek = rng.random((30, 1)) * 40.0 * mag[None, :]
        aday = gercek * rng.uniform(0.8, 1.25, size=gercek.shape)       # biraz bozulmuş
        taban = np.full_like(gercek, gercek.sum() / gercek.size)        # düzgün
        fr = dunya(b, gercek, 11)
        r = U.satir(b, aday, taban, fr, '2011-01-01', '2021-01-01', aday='a', taban='t', hat='h',
                    donem='d', hedef='x', bootstrap=800)
        n = r['N']
        beklenen_ig = float((gercek * (np.log(aday) - np.log(taban))).sum() / gercek.sum()
                            - (aday.sum() - taban.sum()) / gercek.sum())
        self.assertGreater(n, 1000)
        self.assertAlmostEqual(r['IG'], beklenen_ig, delta=4 * r['SE_blok'])
        self.assertAlmostEqual((r['logL_aday'] - r['logL_taban']) / n, r['IG'], places=9)
        self.assertEqual(r['durum'], 'tanımlı')
        self.assertGreater(r['z'], 1.645)

    def test_ayni_model_sifir(self):
        b = sahte_baglam()
        gercek = np.full((30, 41), 0.3)
        fr = dunya(b, gercek, 5)
        r = U.satir(b, gercek, gercek.copy(), fr, '2011-01-01', '2021-01-01', aday='a', taban='t',
                    hat='h', donem='d', hedef='x', bootstrap=200)
        self.assertEqual(r['IG'], 0.0)
        self.assertEqual(r['integral'], 0.0)

    def test_donem_disi_olay_sayilmaz(self):
        b = sahte_baglam()
        gercek = np.full((30, 41), 0.2)
        fr = dunya(b, gercek, 9)
        r = U.satir(b, gercek, gercek * 1.1, fr, '2011-01-01', '2016-01-01', aday='a', taban='t',
                    hat='h', donem='d', hedef='x', bootstrap=100)
        self.assertEqual(r['N'], int(((fr.zaman >= pd.Timestamp('2011-01-01', tz='UTC'))
                                     & (fr.zaman < pd.Timestamp('2016-01-01', tz='UTC'))).sum()))

    def test_gozlemli_sifir_oran_tanimsiz(self):
        b = sahte_baglam()
        gercek = np.full((30, 41), 0.2)
        fr = dunya(b, gercek, 2)
        _, ci, mi = U.hucre_bin(b, fr, '2011-01-01', '2021-01-01', 4.95, veri.M_KENAR)
        sifir = gercek.copy()
        sifir[ci[0], mi[0]] = 0.0
        r = U.satir(b, gercek, sifir, fr, '2011-01-01', '2021-01-01', aday='a', taban='t',
                    hat='h', donem='d', hedef='x', bootstrap=50)
        self.assertEqual(r['durum'], 'tanımsız')
        self.assertIsNone(r['IG'])


class YardimciTesti(unittest.TestCase):
    def test_holm(self):
        h = U.holm([0.01, 0.04, 0.03])
        self.assertAlmostEqual(h[0], 0.03)
        self.assertAlmostEqual(h[2], 0.06)
        self.assertAlmostEqual(h[1], 0.06)

    def test_yil_blogu_se_pozitif(self):
        rng = np.random.default_rng(1)
        x = rng.normal(0.2, 0.5, 200)
        yil = np.repeat(np.arange(2011, 2021), 20)
        se = U.olay_ig_yil(x, yil, 0.0, tekrar=500)
        self.assertTrue(0.005 < se < 0.2)
        self.assertIsNone(U.olay_ig_yil(x[:5], np.full(5, 2011), 0.0))


if __name__ == '__main__':
    unittest.main()
