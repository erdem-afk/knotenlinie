"""Weichert oran/b geri kazanımı, kesim sızıntısı koruması ve HKJ07 okuyucusu."""
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.kaliforniya import veri
from knotenlinie.kaliforniya.model import Kafes, ModelHatasi, kumesiz_maske, kur, oran_kestir
from tests.kaliforniya.test_kaliforniya_kde import kafes_kur


def sentetik_katalog(n_yil=20, a3=300.0, b=1.0, seed=7):
    """GR(b), M>=3 yıllık oran a3; zaman 1981'den, konum rastgele; derinlik 8 km."""
    rng = np.random.default_rng(seed)
    n = rng.poisson(a3 * n_yil)
    m = 3.0 - np.log10(1.0 - rng.random(n)) / b
    t0 = pd.Timestamp('1981-01-01', tz='UTC')
    t = t0 + pd.to_timedelta(rng.random(n) * n_yil * 365.25, unit='D')
    return pd.DataFrame({'zaman': t, 'enlem': rng.uniform(34.2, 37.8, n),
                         'boylam': rng.uniform(-119.8, -116.2, n), 'derinlik': 8.0,
                         'mw': np.round(m, 2)}).sort_values('zaman').reset_index(drop=True)


class OranTesti(unittest.TestCase):
    def test_weichert_geri_kazanim(self):
        kat = sentetik_katalog()
        w = oran_kestir(kat, (-121.0, -115.0, 33.0, 39.0), 1981.0, 2000.0, mc=3.0)
        self.assertAlmostEqual(w['b'], 1.0, delta=0.05)
        gercek = 300.0 * 10 ** (-1.95)
        self.assertAlmostEqual(w['oran_4_95'] / gercek, 1.0, delta=0.15)

    def test_kesim_sonrasi_olay_reddedilir(self):
        kat = sentetik_katalog(n_yil=10)
        kf = kafes_kur()
        kk, mm = kumesiz_maske(kat)
        s = [(kf.lon0 + 0.1 * i, kf.lon0 + 0.1 * (i + 1), kf.lat0 + 0.1 * j, kf.lat0 + 0.1 * (j + 1))
             for i in range(kf.nx) for j in range(kf.ny)]
        izg = pd.DataFrame(s, columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])
        with self.assertRaises(ModelHatasi):
            kur(izg, kf, kk, mm, bitis='1985-01-01', k_komsu=5, kde_mmin=3.0, geysers=False)

    def test_model_gelecegi_okumaz(self):
        """Kesimden sonraki olayları eklemek (kesimden önce kümesizleştirme) modeli değiştirmez."""
        kat = sentetik_katalog(n_yil=12)
        kes = pd.Timestamp('1991-01-01', tz='UTC')
        kf = kafes_kur()
        s = [(kf.lon0 + 0.1 * i, kf.lon0 + 0.1 * (i + 1), kf.lat0 + 0.1 * j, kf.lat0 + 0.1 * (j + 1))
             for i in range(kf.nx) for j in range(kf.ny)]
        izg = pd.DataFrame(s, columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])
        onceki = kat[kat['zaman'] < kes]
        a1 = kur(izg, kf, *kumesiz_maske(onceki), bitis=kes, k_komsu=5, kde_mmin=3.0, geysers=False)[0]
        gelecek = pd.concat([onceki, kat[kat['zaman'] >= kes]])
        a2 = kur(izg, kf, *kumesiz_maske(gelecek[gelecek['zaman'] < kes]), bitis=kes, k_komsu=5,
                 kde_mmin=3.0, geysers=False)[0]
        np.testing.assert_allclose(a1.sekil, a2.sekil)
        self.assertEqual(a1.rate_ust, a2.rate_ust)


HKJ = Path(veri.HKJ_ANA)


@unittest.skipUnless(HKJ.exists(), 'HKJ07 dosyası yok')
class HkjTesti(unittest.TestCase):
    def test_hkj_okuma(self):
        izg, bek = veri.hkj_oku(veri.HKJ_ANA)
        self.assertEqual(bek.shape, (7682, 41))
        self.assertAlmostEqual(float(bek.sum()), 21.12892416879642, places=9)
        Kafes(izg)                                  # 0,1° kafese oturur
        self.assertAlmostEqual(float(izg.boylam_min.min()), -125.4)

    def test_yil_ondalik(self):
        y = veri.yil_ondalik(['2001-01-01T00:00:00Z', '2000-07-02T00:00:00Z'])
        self.assertAlmostEqual(y[0], 2001.0, places=9)
        self.assertAlmostEqual(y[1], 2000.5, delta=0.003)


if __name__ == '__main__':
    unittest.main()
