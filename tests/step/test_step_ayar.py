"""STEP ayarı: bilinen RJ parametreli diziden geri kazanım, dizi ağırlıkları, atama kuralı."""
import unittest

import numpy as np

from knotenlinie.step import ayar
from knotenlinie.step.cekirdek import omori_integral
from knotenlinie.step.dizi import Dizi, DiziIsleyici

MC = 3.1


def sentetik_dizi(rng, mm, a, b, p, c, T, t0=0.0, i=0):
    s = Dizi(i, t0, 12.0, 43.0, mm)
    s.tgk = T
    G = 10.0 ** (b * (mm - MC)) - 1.0
    lam = 10.0 ** a * G * float(omori_integral(0.0, T, c, p))
    n = rng.poisson(lam)
    u = rng.random(n)
    q = 1.0 - p
    if abs(q) < 1e-9:
        t = c * np.exp(u * np.log((T + c) / c)) - c
    else:
        t = (u * ((T + c) ** q - c ** q) + c ** q) ** (1 / q) - c
    v = rng.random(n)                              # kesik üstel M ∈ [Mc, Mm]
    m = -np.log10(10.0 ** (-b * MC) - v * (10.0 ** (-b * MC) - 10.0 ** (-b * mm))) / b
    s.uye_t, s.uye_m = list(t), list(m)
    return s


class GenelRJ(unittest.TestCase):
    def test_geri_kazanim(self):
        rng = np.random.default_rng(7)
        gercek = dict(a=-1.6, b=0.95, p=1.1, c=0.03)
        diz = [sentetik_dizi(rng, rng.uniform(4.0, 6.5), T=200.0, i=i, **gercek) for i in range(500)]
        self.assertGreater(sum(len(s.uye_t) for s in diz), 2000)
        jen = ayar.jenerik_kur(diz, t_son=1e9, mc=MC)
        self.assertAlmostEqual(jen['a'], gercek['a'], delta=0.1)
        self.assertAlmostEqual(jen['b'], gercek['b'], delta=0.05)
        self.assertAlmostEqual(jen['p'], gercek['p'], delta=0.06)
        self.assertAlmostEqual(jen['c'], gercek['c'], delta=0.02)
        # gerçek parametrede olabilirlik, kestirimden büyük olamaz
        veri = ayar._veri(diz, 1e9)
        self.assertLessEqual(ayar.log_olabilirlik((gercek['a'], gercek['b'], gercek['p'], gercek['c']), veri, MC),
                             jen['logL'] + 1e-6)


class DiziAgirliklari(unittest.TestCase):
    JEN = dict(a=-1.6, b=0.95, p=1.1, c=0.03)

    def test_genel_dizide_genel_agirlik_baskin_degil_ama_toplam_bir(self):
        rng = np.random.default_rng(11)
        agirlik = []
        for i in range(40):
            s = sentetik_dizi(rng, 5.5, T=300.0, i=i, **self.JEN)
            if len(s.uye_t) >= 8:
                w = ayar.dizi_agirliklari(s, 100.0 if max(s.uye_t) < 100 else max(s.uye_t) + 1, self.JEN, MC, 8)
                self.assertAlmostEqual(sum(x[0] for x in w), 1.0, places=12)
                agirlik.append(w[0][0])
        self.assertGreater(len(agirlik), 5)
        self.assertGreater(np.mean(agirlik), 0.4)      # genel doğruysa genel model kaybetmez

    def test_uretken_dizi_a_guncellenir(self):
        rng = np.random.default_rng(3)
        gercek = dict(self.JEN, a=self.JEN['a'] + 0.7)          # 5 kat üretken
        s = sentetik_dizi(rng, 6.0, T=300.0, **gercek)
        self.assertGreater(len(s.uye_t), 60)
        w = ayar.dizi_agirliklari(s, 300.0, self.JEN, MC, 8)
        self.assertLess(w[0][0], 1e-6)                          # genel reddedilir
        a_guncel = sum(x[0] * x[1] for x in w[1:]) / sum(x[0] for x in w[1:])
        self.assertAlmostEqual(a_guncel, gercek['a'], delta=0.15)

    def test_az_uyede_yalniz_genel(self):
        s = Dizi(0, 0.0, 12.0, 43.0, 5.0)
        s.uye_t, s.uye_m = [0.1, 0.5], [3.2, 3.3]
        self.assertEqual(ayar.dizi_agirliklari(s, 10.0, self.JEN, MC, 8), [(1.0, self.JEN['a'], self.JEN['p'])])


class Atama(unittest.TestCase):
    def test_kurallar(self):
        isl = DiziIsleyici(4.0)
        ana = isl.ekle(0.0, 12.0, 43.0, 5.0)
        self.assertIsNotNone(ana)
        # pencere içi, küçük → artçı
        self.assertIs(isl.ekle(1.0, 12.1, 43.0, 3.5), ana)
        # çok uzak → arka plan (M<Mseq)
        self.assertIsNone(isl.ekle(2.0, 16.0, 40.0, 3.4))
        # daha büyük olay ana şoka atanmaz, yeni dizi açar
        yeni = isl.ekle(3.0, 12.0, 43.0, 5.5)
        self.assertIsNot(yeni, ana)
        # sonraki küçük olay: iki aday da var, en büyük ana şok (5.5) alır
        self.assertIs(isl.ekle(4.0, 12.0, 43.0, 3.3), yeni)
        # pencere dışı (çok sonra) → arka plan
        self.assertIsNone(isl.ekle(5000.0, 12.0, 43.0, 3.3))
        # ana şoklar da arka plan listesinde
        self.assertEqual(len(isl.arka), 4)

    def test_gelecek_bilgisi_kullanilmaz(self):
        a = DiziIsleyici(4.0)
        b = DiziIsleyici(4.0)
        olaylar = [(0.0, 12.0, 43.0, 4.6), (1.0, 12.0, 43.0, 3.5), (2.0, 12.1, 43.0, 3.9)]
        for o in olaylar:
            a.ekle(*o)
        for o in olaylar[:2]:
            b.ekle(*o)
        self.assertEqual(a.tum[0].uye_t[:1], b.tum[0].uye_t[:1])


class Hiyerarsi(unittest.TestCase):
    def test_en_yakin_ebeveyn_ve_ozel_dizi(self):
        isl = DiziIsleyici(3.0, 3.1, hiyerarsi=True)
        ana = isl.ekle(0.0, 12.0, 43.0, 6.0)
        ara = isl.ekle(1.0, 12.0, 43.0, 5.0)        # 6.0'ın artçısı + kendi dizisi
        self.assertIsNot(ara, ana)
        self.assertEqual(ana.uye_m, [5.0])
        kucuk = isl.ekle(2.0, 12.0, 43.0, 4.0)       # en yakın ebeveyn 5.0'lık dizi
        self.assertIs(kucuk, isl.tum[2])             # M>=Mseq: kendi dizisi de açılır
        self.assertEqual(ara.uye_m, [4.0])
        self.assertEqual(ana.uye_m, [5.0])
        # arka plan: yalnız atanmamış olay (ana şok)
        self.assertEqual(len(isl.arka), 1)

    def test_varsayilan_en_buyuk_ana_sok(self):
        isl = DiziIsleyici(3.0, 3.1)
        ana = isl.ekle(0.0, 12.0, 43.0, 6.0)
        isl.ekle(1.0, 12.0, 43.0, 5.0)
        isl.ekle(2.0, 12.0, 43.0, 4.0)
        self.assertEqual(ana.uye_m, [5.0, 4.0])

    def test_mc_arka_kucuk_olaylari_arka_plana_almaz(self):
        isl = DiziIsleyici(2.5, 3.1)
        isl.ekle(0.0, 12.0, 43.0, 2.7)
        isl.ekle(5000.0, 16.0, 40.0, 3.3)
        self.assertEqual([x[3] for x in isl.arka], [3.3])

    def test_mc_alti_uyeler_ayara_girmez(self):
        s = Dizi(0, 0.0, 12.0, 43.0, 5.0)
        s.uye_t, s.uye_m = [0.1, 0.2, 0.3], [2.7, 3.2, 3.4]
        v = ayar._veri([s], 100.0, 3.1)
        self.assertEqual(len(v[0]), 2)
        s2 = Dizi(1, 0.0, 12.0, 43.0, 3.0)           # Mm<=Mc: olasılığa girmez
        self.assertEqual(len(ayar._veri([s2], 100.0, 3.1)[4]), 0)


if __name__ == '__main__':
    unittest.main()
