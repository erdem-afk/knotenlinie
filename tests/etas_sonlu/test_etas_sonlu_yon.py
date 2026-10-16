"""Doğrultu yolları (a/b), GCMT eşleştirme ve WC94 bağıntısı."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.etas import model as M
from knotenlinie.etas_sonlu import gcmt as G
from knotenlinie.etas_sonlu.yon import Yon, pca_aci
from knotenlinie.yollar import VERI
from tests._veri import veri_gerek

KUTU = (39.5, 41.5, 11.5, 13.5)
MET = M.yerel_metrik(KUTU)
KESIK = VERI / 'kesik-2015/gcmt_le2015.ndk'


def _nokta(merkez, aci_deg, mesafe_km):
    """`merkez`ten `aci_deg` (kuzeyden saat yönü) yönünde `mesafe_km` km noktalar."""
    th = np.radians(aci_deg)
    lon = merkez[0] + mesafe_km * np.sin(th) / MET.kx
    lat = merkez[1] + mesafe_km * np.cos(th) / MET.ky
    return lon, lat


def _cerceve(rows):
    return pd.DataFrame(rows, columns=G.KOLONLAR)


class TestYon(unittest.TestCase):
    def test_pca_aci_geri_kazanim(self):
        rng = np.random.default_rng(11)
        for dogrultu in (0.0, 35.0, 90.0, 140.0):
            r = rng.uniform(-12, 12, 300)
            j = rng.normal(0, 1.2, 300)
            th = np.radians(dogrultu)
            lon = 12.5 + (r * np.sin(th) + j * np.cos(th)) / (M.KM_DERECE * np.cos(np.radians(40.5)))
            lat = 40.5 + (r * np.cos(th) - j * np.sin(th)) / M.KM_DERECE
            aci = pca_aci(lon, lat, MET)
            hata = abs(((np.degrees(aci) - dogrultu + 90) % 180) - 90)
            self.assertLess(hata, 10.0, f'{dogrultu}: hata {hata}')

    def test_yon_b_esik(self):
        t0 = pd.Timestamp('2010-12-20', tz='UTC')
        a = pd.Timestamp('2011-01-01', tz='UTC')
        noktalar = [_nokta((12.5, 40.5), 30.0, r) for r in np.linspace(-5, 5, 20)]
        zaman = [t0 + pd.Timedelta(hours=k) for k in range(20)]
        h = pd.DataFrame(dict(zaman=zaman, boylam=[p[0] for p in noktalar],
                              enlem=[p[1] for p in noktalar], derinlik=10.0, mw=2.8))
        yon = Yon(None)
        yb = yon.yon('b', h, 0, a, MET, 11.0)
        self.assertIsNotNone(yb)
        hata = abs(((yb['dogrultu'] - 30.0 + 90) % 180) - 90)
        self.assertLess(hata, 10.0)
        self.assertEqual(yon.yon('a', h, 0, a, MET, 11.0), None)
        az = h.iloc[:5]
        self.assertIsNone(yon.yon('b', az, 0, a, MET, 11.0))

    def test_yon_a_duzlem_secimi(self):
        t0 = pd.Timestamp('2010-12-31', tz='UTC')
        a = pd.Timestamp('2011-01-01', tz='UTC')
        # Ebeveyn + 20 artçı doğu-batı (dogrultu 90) boyunca ilk gün.
        satirlar = [[t0, 12.5, 40.5, 10.0, 6.0]]
        for k in range(20):
            lon, lat = _nokta((12.5, 40.5), 90.0, (k - 10) * 0.5)
            satirlar.append([t0 + pd.Timedelta(minutes=30 * k + 30), lon, lat, 10.0, 3.0])
        h = pd.DataFrame(satirlar, columns=['zaman', 'boylam', 'enlem', 'derinlik', 'mw'])
        cerceve = _cerceve([['OLAY', t0, t0, 40.5, 12.5, 10.0, 6.0, 0.0, 90.0, 0.0, 90.0, 90.0, 0.0]])
        yon = Yon(cerceve)
        ya = yon.yon('a', h, 0, a, MET, 12.0)
        self.assertIsNotNone(ya)
        hata = abs(((ya['dogrultu'] - 90.0 + 90) % 180) - 90)
        self.assertLess(hata, 5.0)

    def test_gcmt_esles(self):
        t0 = pd.Timestamp('2009-04-06 01:32:39', tz='UTC')
        cerceve = _cerceve([
            ['A', t0, t0, 42.33, 13.33, 8.8, 6.3, 130.0, 55.0, -90.0, 310.0, 35.0, -90.0],
            ['B', t0 + pd.Timedelta(days=5), t0 + pd.Timedelta(days=5), 38.0, 15.0, 10.0, 5.1,
             100.0, 40.0, -80.0, 260.0, 50.0, -100.0],
        ])
        self.assertEqual(G.esles(cerceve, t0 + pd.Timedelta(seconds=20), 13.34, 42.34).olay_adi, 'A')
        # merkez öncesi kapısı: aynı gün başından sonra doğan çözüm kullanılmaz
        self.assertIsNone(G.esles(cerceve, t0, 13.34, 42.34, merkez_once=t0 - pd.Timedelta(days=1)))
        # 50 km'den uzak ve +-60 s dışındaki B eşleşmez
        self.assertIsNone(G.esles(cerceve, t0 + pd.Timedelta(days=5), 12.0, 42.0))

    @veri_gerek('kesik-2015/gcmt_le2015.ndk')
    def test_gcmt_oku_gercek_dosya(self):
        df = G.oku(KESIK)
        self.assertGreater(len(df), 1000)
        self.assertTrue((df.zaman < G.KESIM).all())
        self.assertTrue(df.Mw.notna().all() if 'Mw' in df else True)
        self.assertTrue({'zaman', 'merkez_zaman', 'dogrultu1', 'dogrultu2'}.issubset(df.columns))
        self.assertTrue((df.dogrultu1.between(0, 360)).all())
        self.assertTrue((df.merkez_zaman >= df.zaman - pd.Timedelta(minutes=5)).all())


if __name__ == '__main__':
    unittest.main()
