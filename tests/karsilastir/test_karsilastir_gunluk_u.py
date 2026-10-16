"""Deney U: GR uzatması, ETAS-LM 2006 kapıları, eşik başına N/S/M ve ağırlık tabanı."""
import unittest

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.gunluk_u import ETASLMGecmis, GrUzat
from knotenlinie.ortak_zemin.veri import IZGARA


class TabanSahte:
    """Mc=3,1 ve b=1; kendi GR formülüyle hücre başına sabit oran."""
    mc, b, kutu, p = 3.1, 1.0, (0, 1, 0, 1), {}

    def __init__(self, hucre=(0.5, 0.25)):
        self.hucre = np.asarray(hucre, float)

    def beklenen(self, a, z, h, izgara, e):
        e = np.asarray(e, float)
        if e[0] < self.mc:
            raise ValueError('taban Mc altını bilmez')
        mag = 10 ** (-self.b * (e[:-1] - self.mc)) - 10 ** (-self.b * (e[1:] - self.mc))
        return self.hucre[:, None] * mag[None, :]


class TestGrUzat(unittest.TestCase):
    def test_mc_ustu_tabanla_ayni_alti_gr_ile_uzar(self):
        taban = TabanSahte()
        gr = GrUzat(taban)
        e = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
        out = gr.beklenen(None, None, None, None, e)
        # 3,15 ve üstü kutular tabanın kendi çıktısıyla birebir aynı
        j = int(np.flatnonzero(np.isclose(e, 3.15))[0])
        np.testing.assert_allclose(out[:, j:], taban.beklenen(None, None, None, None, e[j:]), rtol=1e-13)
        # Toplam: M>=2,95 oranı = M>=Mc oranı × 10^(b(Mc-2,95)); M>=3,95 tabanla aynı
        np.testing.assert_allclose(out.sum(axis=1), taban.hucre * 10 ** (taban.b * (taban.mc - 2.95)), rtol=1e-12)
        j395 = int(np.flatnonzero(np.isclose(e, 3.95))[0])
        np.testing.assert_allclose(out[:, j395:].sum(axis=1), taban.hucre * 10 ** (-taban.b * (3.95 - taban.mc)), rtol=1e-12)

    def test_eski_hata_tekrar_etmez(self):
        # Eski formül (2,95 tabanlı) M>=3,95 oranını 10^(-0,15 b) kadar eksik verirdi.
        taban = TabanSahte()
        e = np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]
        out = GrUzat(taban).beklenen(None, None, None, None, e)
        j395 = int(np.flatnonzero(np.isclose(e, 3.95))[0])
        dogru = taban.beklenen(None, None, None, None, np.array([3.95, np.inf]))[:, 0]
        np.testing.assert_allclose(out[:, j395:].sum(axis=1), dogru, rtol=1e-12)


class TestETASLMGecmis(unittest.TestCase):
    def setUp(self):
        r = np.random.default_rng(3)
        n = 40
        self.cat = pd.DataFrame(dict(
            zaman=pd.to_datetime(np.sort(pd.Timestamp('2005-05-01', tz='UTC').value
                                         + r.integers(0, 200 * 86400 * 10**9, n)), utc=True),
            enlem=40.0 + r.random(n) * 0.2, boylam=12.0 + r.random(n) * 0.2,
            derinlik=r.random(n) * 20, mw=2.5 + r.exponential(0.4, n)))
        cell = [(12 + i * 0.1, 12 + (i + 1) * 0.1, 40 + j * 0.1, 40 + (j + 1) * 0.1)
                for j in range(3) for i in range(3)]
        self.grid = pd.DataFrame(cell, columns=IZGARA)
        self.bg = dict(bg=np.full(9, 1e-4), meta={})

    def test_kapilar_ve_guc(self):
        m = ETASLMGecmis(self.cat, self.grid, arka_plan=self.bg, adim=4, nesil=2)
        e = np.r_[np.round(2.95 + 0.1 * np.arange(10), 2), np.inf]
        h = self.cat[self.cat.zaman < pd.Timestamp('2006-01-02', tz='UTC')]
        with self.assertRaises(ValueError):  # ayar sonundan önce
            m.beklenen(pd.Timestamp('2005-12-31', tz='UTC'), pd.Timestamp('2006-01-01', tz='UTC'), h, self.grid, e)
        gun_ici = pd.concat([h, pd.DataFrame(dict(zaman=pd.to_datetime(['2006-01-01T05:00:00Z'], utc=True),
                                                  enlem=[40.1], boylam=[12.1], derinlik=[5.], mw=[4.]))])
        with self.assertRaises(ValueError):  # geçmiş gün içi
            m.beklenen(pd.Timestamp('2006-01-01', tz='UTC'), pd.Timestamp('2006-01-02', tz='UTC'), gun_ici, self.grid, e)
        a = pd.Timestamp('2006-01-02', tz='UTC')
        out = m.beklenen(a, a + pd.Timedelta(days=1), h, self.grid, e)
        self.assertEqual(out.shape, (9, len(e) - 1))
        self.assertTrue((out >= 0).all() and np.isfinite(out).all())
        # Geçmiş olmasa da arka plan kalır; geçmiş oranı artırır (bilinen yön)
        bos = m.beklenen(a, a + pd.Timedelta(days=1), h.iloc[:0], self.grid, e)
        self.assertGreater(out.sum(), bos.sum())
        # Boş geçmiş: arka plan (üstüne kendi kaskadı) — her hücre en az bg×GR payı
        taban = 1e-4 * 10 ** (-1.0 * (2.95 - 2.5))
        self.assertTrue((bos.sum(axis=1) >= taban * (1 - 1e-9)).all())


class TestNSMEsik(unittest.TestCase):
    def test_esik_alt_yuzeyde(self):
        """Düşük M kutularında aşırı tahmin M≥2,95 N testini bozar, M≥3,95 testini bozmaz."""
        from knotenlinie.karsilastir.gunluk_u import nsm_mixture
        from knotenlinie.skor_defteri.defter import Defter, alt_indeks
        nk = 61
        j = alt_indeks(3.95)
        goz = np.zeros((6, nk), int)
        goz[0, j], goz[1, j + 2], goz[2, 3], goz[3, 4] = 2, 3, 5, 5
        # M>=3,95 gözlem: 5; M<3,95 gözlem: 10
        lam = np.full((6, nk), 1e-4)
        lam[:, :j] = 5.0                      # düşük M'de gözlemin çok üstünde
        lam[:, j:] = 5.0 / (6 * (nk - j))     # M>=3,95 toplamı = gözlenen N = 5
        d = {n: Defter(n, pd.DataFrame(), pd.DataFrame(), beklenen=lam.copy(), gozlem=goz) for n in ('a', 'b')}
        r295 = nsm_mixture(d, ['a', 'b'], [0.5, 0.5], 2.95)
        r395 = nsm_mixture(d, ['a', 'b'], [0.5, 0.5], 3.95)
        self.assertFalse(r295['N_gecti'])
        self.assertTrue(r395['N_gecti'])


if __name__ == '__main__':
    unittest.main()
