"""W sürücüsü: tam Poisson skoru, hedef (i)/(ii), skor defteri ve koşucu ile 1e-9 eşleşme."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.karsilastir import gunluk_w as W
from knotenlinie.ortak_zemin.veri import IZGARA


class TestGunlukW(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grid = pd.DataFrame([[12., 12.1, 40., 40.1], [12.1, 12.2, 40., 40.1], [12., 12.1, 40.1, 40.2]],
                                columns=IZGARA)
        nb = len(W.EDGES) - 1
        cls.nb = nb
        cls.taban = np.array([[.5], [.2], [.1]]) * np.exp(-0.9 * np.arange(nb))[None, :]
        cls.bas, cls.son = '2011-01-01T00:00:00Z', '2011-01-05T00:00:00Z'
        z = ['2011-01-01T01:00:00Z', '2011-01-01T02:00:00Z', '2011-01-02T05:00:00Z', '2011-01-03T05:00:00Z',
             '2011-01-03T09:00:00Z', '2011-01-04T05:00:00Z', '2011-01-04T06:00:00Z']
        cls.cat = pd.DataFrame(dict(
            zaman=pd.to_datetime(z, utc=True), boylam=[12.05, 12.05, 12.15, 12.05, 12.05, 12.05, 12.15],
            enlem=[40.05, 40.05, 40.05, 40.15, 40.05, 40.05, 40.05], derinlik=[10.] * 7,
            mw=[3.00, 3.02, 3.50, 4.10, 5.30, 3.01, 4.97]))   # 1-2. olay aynı gün/hücre/kutu (n=2)
        cls.q = np.ones((4, nb))
        cls.q[:, :10] = np.linspace(.2, .9, 10)[None, :] * np.array([1, .8, .6, 1.])[:, None]

        def fn(a, b, h, g, e):
            assert (h.zaman < a).all()
            assert g.shape[0] == 3 and len(e) == nb + 1
            return cls.taban * (1 + 0.5 * (a.day % 2))
        cls.fn = fn
        cls.ayarlar = dict(sinir=(12., 12.2, 40., 40.2), baslangic_yil=1985, derinlik_max=30)
        cls.k = W.kos_et(fn, cls.ayarlar, cls.bas, cls.son, cls.cat, cls.grid, 'sent', cls.q)

    def test_ozet_koşucu_logL_ile_ayni(self):
        o = W.ozet(self.k, 'ii', 2.95)
        self.assertEqual(o['N'], 7)
        self.assertAlmostEqual(o['logL'], self.k.logL_kos, places=9)
        # elle: N=7 olay; iki olay aynı (gün,hücre,kutu) -> log 2!
        lam = self.k.lam_olay('ii')
        top = sum(self.taban.sum() * (1 + .5 * (d % 2)) for d in (1, 2, 3, 4))
        self.assertAlmostEqual(o['logL'], np.log(lam).sum() - top - gammaln(3), places=9)
        self.assertAlmostEqual(o['Lambda'], top, places=9)

    def test_hedef_i_bilinen_cevap(self):
        ii, i = W.ozet(self.k, 'ii', 2.95), W.ozet(self.k, 'i', 2.95)
        lam_i = self.k.lam * self.q[self.k.gun, self.k.kutu]
        top_i = float((self.k.gunluk * self.q).sum())
        n2 = gammaln(3)
        self.assertAlmostEqual(i['logL'], np.log(lam_i).sum() - top_i - n2, places=9)
        self.assertAlmostEqual(i['Lambda'], top_i, places=9)
        # toplam (hücre,kutu) matrisi günlük q ile aynı Λ'yı vermeli
        self.assertAlmostEqual(float(self.k.toplam['i'].sum()), top_i, places=9)
        self.assertLess(i['Lambda'], ii['Lambda'])
        # q sabit c ise logL_i = logL_ii + N ln c + (1−c) Λ
        k2 = W.Kosum('x', self.k.bas, self.k.son, self.k.olaylar, self.k.lam, self.k.gunluk, self.k.gozlem,
                     {'ii': self.k.toplam['ii']}, np.full_like(self.q, .5), 0.)
        o2 = W.ozet(k2, 'i', 2.95)
        self.assertAlmostEqual(o2['logL'], ii['logL'] + 7 * np.log(.5) + .5 * ii['Lambda'], places=9)

    def test_esik_alt_kumesi(self):
        j = W.kutu_no(3.95)
        o = W.ozet(self.k, 'ii', 3.95)
        self.assertEqual(o['N'], int((self.cat.mw >= 3.95).sum()))
        self.assertAlmostEqual(o['Lambda'], float(self.k.gunluk[:, j:].sum()), places=9)

    def test_defter_koşucu_1e9(self):
        with tempfile.TemporaryDirectory() as d:
            for v in ('ii', 'i'):
                olay, gun = W.defter_yaz(self.k, v, f'2011-{v}', d)
                oku = pd.read_csv(Path(d) / f'sent__2011-{v}__olay.csv.gz')
                gu = pd.read_csv(Path(d) / f'sent__2011-{v}__gun.csv.gz')
                self.assertEqual(list(oku.columns), ['zaman', 'enlem', 'boylam', 'mw', 'hucre', 'kutu', 'gun', 'lam'])
                self.assertEqual(list(gu.columns), ['gun', 'Lam295', 'Lam395'])
                self.assertTrue(oku.zaman.str.endswith('Z').all())
                for alt in (2.95, 3.95):
                    ref = W.ozet(self.k, v, alt)['logL']
                    self.assertLess(abs(W.defter_logL(oku, gu, alt) - ref) / abs(ref), 1e-9)
            # (ii) defteri doğrudan koşucunun logL'ine 1e-9 göreli eşit
            olay, gun = W.defter_yaz(self.k, 'ii', '2011-yeni', d)
            self.assertLess(abs(W.defter_logL(olay, gun, 2.95) - self.k.logL_kos) / abs(self.k.logL_kos), 1e-9)

    def test_cift_IG_kimligi_ve_blok(self):
        s = W.cift(self.k, 'i', self.k, 'ii', 2.95, 'a', 'b', tekrar=200)
        a, b = W.ozet(self.k, 'i', 2.95), W.ozet(self.k, 'ii', 2.95)
        self.assertAlmostEqual(s['IG'], (a['logL'] - b['logL']) / 7, places=12)
        self.assertAlmostEqual(s['IG'], s['IG_olay'] + s['integral'], places=12)
        self.assertEqual(s['N'], 7)
        for k in ('NSM_aday', 'NSM_taban'):
            self.assertIn('gecti', s[k])
        self.assertEqual(W.cift(self.k, 'ii', self.k, 'ii', 4.95, 'a', 'b')['IG'], 0.0)

    def test_ham_gidis_donus(self):
        with tempfile.TemporaryDirectory() as d:
            W.ham_yaz(self.k, d)
            r = W.ham_oku('sent', self.k.bas, self.k.son, d)
            np.testing.assert_allclose(r.lam, self.k.lam)
            np.testing.assert_allclose(r.gunluk, self.k.gunluk)
            np.testing.assert_array_equal(r.kutu, self.k.kutu)
            self.assertEqual(r.logL_kos, self.k.logL_kos)
            self.assertAlmostEqual(W.ozet(r, 'i', 2.95)['logL'], W.ozet(self.k, 'i', 2.95)['logL'], places=12)

    def test_dizi_bayragi(self):
        raw = pd.DataFrame(dict(
            zaman=pd.to_datetime(['2011-01-01T00:00:00Z', '2011-01-02T00:00:00Z'], utc=True),
            enlem=[40.05, 41.5], boylam=[12.05, 12.05], derinlik=[10., 10.], mw=[5.2, 5.5]))
        hedef = pd.DataFrame(dict(
            zaman=pd.to_datetime(['2011-01-01T00:00:00Z', '2011-01-03T00:00:00Z', '2011-01-03T00:00:00Z',
                                  '2011-02-15T00:00:00Z'], utc=True),
            enlem=[40.05, 40.10, 40.05, 40.05], boylam=[12.05, 12.05, 12.05, 12.05]))
        bayrak = W.dizi_bayragi(hedef, raw)
        # 1: olayın kendisi önceki değil; 2: ~5.5 km ve 2 gün; 3: aynı konum; 4: 30 günden eski
        np.testing.assert_array_equal(bayrak, [False, True, True, False])


if __name__ == '__main__':
    unittest.main()
