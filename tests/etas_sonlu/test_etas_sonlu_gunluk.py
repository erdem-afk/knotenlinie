"""Deney X ölçüm yardımcıları: seçim kuralı, büyük-ebeveyn alt kümesi, defter doğrulaması."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from knotenlinie.etas import model as M
from knotenlinie.etas_sonlu import defter as DF
from knotenlinie.karsilastir import gunluk_x as GX

KUTU = (39.5, 41.5, 11.5, 13.5)


class TestSecim(unittest.TestCase):
    def _s(self, **ll):
        return dict(runs={n: SimpleNamespace(logL=v) for n, v in ll.items()})

    def test_en_yuksek_logL(self):
        tablo, sec = GX.secim_yap(self._s(**{'R-le2005': -10.0, 'X-a-5.0': -9.0, 'X-b-5.5': -9.5}))
        self.assertEqual(sec, 'X-a-5.0')

    def test_beraberlik_sirasi(self):
        _, sec = GX.secim_yap(self._s(**{'R-le2005': -9.0, 'X-a-5.0': -9.0, 'X-b-5.0': -9.0}))
        self.assertEqual(sec, 'R-le2005')
        _, sec = GX.secim_yap(self._s(**{'R-le2005': -10.0, 'X-a-5.5': -9.0, 'X-a-5.0': -9.0,
                                         'X-b-5.0': -9.0, 'X-b-5.5': -9.0}))
        self.assertEqual(sec, 'X-a-5.0')
        _, sec = GX.secim_yap(self._s(**{'R-le2005': -10.0, 'X-b-5.0': -9.0, 'X-a-5.5': -9.0}))
        self.assertEqual(sec, 'X-b-5.0')  # küçük M_s, yoldan önce gelir


class TestAltKume(unittest.TestCase):
    def test_buyuk_ebeveyn_maskesi(self):
        met = M.yerel_metrik(KUTU)
        t = pd.Timestamp('2010-06-01', tz='UTC')
        k = pd.DataFrame(dict(zaman=[t], boylam=[12.5], enlem=[40.5], derinlik=10.0, mw=[5.2]))
        # Hedefler: yakın/zamanında (dahil), 40 gün sonra (hariç), 200 km uzak (hariç), ebeveynden önce (hariç)
        hedef = pd.DataFrame(dict(
            zaman=[t + pd.Timedelta(days=5), t + pd.Timedelta(days=40), t + pd.Timedelta(days=5),
                   t - pd.Timedelta(days=1)],
            boylam=[12.6, 12.6, 12.5, 12.6], enlem=[40.6, 40.6, 42.5, 40.6], mw=3.0))
        m = GX.buyuk_ebeveyn_maske(hedef, k, met)
        self.assertEqual(m.tolist(), [True, False, False, False])
        k2 = k.assign(mw=4.9)
        self.assertFalse(GX.buyuk_ebeveyn_maske(hedef, k2, met).any())


class TestDefter(unittest.TestCase):
    def test_defter_logL_farki_koşucuyla_eslesir(self):
        hedef = pd.DataFrame(dict(zaman=pd.to_datetime(['2011-01-01T03:00:00Z', '2011-01-02T05:00:00Z']),
                                  enlem=[40.1, 40.2], boylam=[12.1, 12.2], mw=[3.0, 3.5]))
        gunler = pd.date_range('2011-01-01', periods=3, freq='D', tz='UTC')
        ci, mi = np.array([1, 2]), np.array([0, 5])
        gs = hedef.zaman.dt.strftime('%Y-%m-%d').to_numpy()
        lam = {'R': np.array([0.02, 0.01]), 'X': np.array([0.03, 0.008])}
        gun = {'R': np.array([1.0, 2.0, 0.5]), 'X': np.array([1.1, 1.9, 0.55])}
        runs = {}
        with tempfile.TemporaryDirectory() as d:
            eski = GX.DEFTER
            GX.DEFTER = Path(d)
            try:
                for n in lam:
                    o = DF.olay_cercevesi(hedef, ci, mi, lam[n], gs)
                    g = DF.gun_cercevesi(gunler, gun[n], 0.1 * gun[n])
                    DF.yaz(Path(d), n, '2011-2015', o, g)
                    runs[n] = SimpleNamespace(logL=float(np.log(lam[n]).sum() - gun[n].sum() - 1.234))
                sonuc = GX.defter_dogrula('2011-2015', runs, 'R')
                self.assertTrue(sonuc['X']['tamam'])
                runs['X'].logL += 1e-3
                with self.assertRaises(ValueError):
                    GX.defter_dogrula('2011-2015', runs, 'R')
            finally:
                GX.DEFTER = eski


class TestSatir(unittest.TestCase):
    def _kur(self):
        from scipy.special import gammaln
        from knotenlinie.karsilastir.kosucu import Kosu, geometri, olay_kutulari
        grid = pd.DataFrame(dict(boylam_min=[12.0, 12.1], boylam_max=[12.1, 12.2],
                                 enlem_min=[40.0, 40.0], enlem_max=[40.1, 40.1]))
        edges = np.array([2.95, 3.95, 4.95, np.inf])
        hedef = pd.DataFrame(dict(
            zaman=pd.to_datetime(['2011-01-01T03:00:00Z', '2011-01-01T09:00:00Z',
                                  '2011-01-02T05:00:00Z', '2011-01-02T06:00:00Z']),
            enlem=40.05, boylam=[12.05, 12.15, 12.05, 12.15], derinlik=10.0, mw=[3.0, 4.0, 3.2, 5.0]))
        g, m = geometri(grid, edges)
        hd, ci, mi = olay_kutulari(hedef, grid, m)
        gun_idx = np.array([0, 0, 1, 1])
        ndays = 3
        rng = np.random.default_rng(5)
        runs, bins = {}, {}
        for ad, carp in (('A', 1.3), ('B', 1.0)):
            gb = carp * rng.uniform(0.05, 0.2, (ndays, 3))
            lam = carp * np.array([0.1, 0.05, 0.12, 0.02])
            toplam = np.zeros((2, 3))
            for d in range(ndays):          # günlük bütünü hücrelere eşit dağıt
                toplam += gb[d][None, :] / 2.0
            gozlem = np.zeros((2, 3), int)
            np.add.at(gozlem, (ci, mi), 1)
            ll = float(np.log(lam).sum() - toplam.sum())  # log(n!) = 0: hepsi tekil
            runs[ad] = Kosu(ad, toplam, gozlem, lam, ll, hd, ('a', 'b', (0.0, 30.0), 'h', 'italya'))
            bins[ad] = gb
        return grid, edges, hd, ci, mi, gun_idx, ndays, runs, bins

    def test_satir_ig_ve_alt_kume(self):
        grid, edges, hd, ci, mi, gun_idx, ndays, runs, bins = self._kur()
        for esik, n_beklenen in ((2.95, 4), (3.95, 2), (4.95, 1)):
            r = GX.satir_yap('A', 'B', '2011-2015', esik, runs, bins, hd, gun_idx, ndays, grid, edges)
            self.assertEqual(r['N'], n_beklenen)
            j = int(np.flatnonzero(np.isclose(edges[:-1], esik))[0])
            x = np.log(runs['A'].olay_oranlari / runs['B'].olay_oranlari)[hd.mw.to_numpy() >= esik - 1e-9]
            delta = (bins['A'][:, j:].sum() - bins['B'][:, j:].sum())
            self.assertAlmostEqual(r['IG'], float(x.sum() - delta) / n_beklenen, places=10)
            self.assertAlmostEqual(r['IG_olay'], float(x.mean()), places=12)
            self.assertAlmostEqual(r['integral'], float(-delta / n_beklenen), places=12)
        # Alt küme: M>=5 ebeveyn yok -> N=0; 3.0 olayından 4.0 olayına kadar M>=5 ebeveyn varsa o olaylar girer.
        met = M.yerel_metrik((39.5, 41.5, 11.5, 13.5))
        k = pd.DataFrame(dict(zaman=[pd.Timestamp('2010-12-25', tz='UTC')], boylam=[12.1],
                              enlem=[40.05], derinlik=10.0, mw=[5.4]))
        a = GX.alt_kume_satiri('A', 'B', 3.95, runs, bins, hd, grid, edges, k, met)
        self.assertEqual(a['N'], 2)
        j = 1
        x = np.log(runs['A'].olay_oranlari / runs['B'].olay_oranlari)[hd.mw.to_numpy() >= 3.95 - 1e-9]
        delta = bins['A'][:, j:].sum() - bins['B'][:, j:].sum()
        self.assertAlmostEqual(a['IG'], float(x.mean() - delta / 2), places=12)
        k2 = k.assign(zaman=pd.Timestamp('2010-10-01', tz='UTC'))  # >30 gün önce
        self.assertEqual(GX.alt_kume_satiri('A', 'B', 3.95, runs, bins, hd, grid, edges, k2, met)['N'], 0)


if __name__ == '__main__':
    unittest.main()
