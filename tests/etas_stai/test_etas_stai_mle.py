"""W olabilirliği: R'ye özdeşlik, analitik gradyan, bilinen cevaplı sentetik geri kazanım."""
import unittest

import numpy as np
import pandas as pd
from scipy.optimize._numdiff import approx_derivative
from scipy.special import ndtr

from knotenlinie.etas import model as M
from knotenlinie.etas_stai.mle import Olabilirlik as W, ayarla
from knotenlinie.etas_stai.tamlik import KisaTamlik, SIGMA, Z95, MC0, sonra_a, sonra_b
from knotenlinie.etas_uzun.mle import Olabilirlik as R, ayarla as r_ayarla, tamlik
from tests.etas_uzun.test_etas_uzun_mle import izgara
from knotenlinie.ortak_zemin.veri import hucre_indeks

KUTU = (40., 40.4, 12., 12.4)


def benzet_ek(th, b, T, change, grid, box, seed, ana):
    """Gözlenen-ebeveyn öncesi TAM süreç: arka plan + eklenen ana şoklar + kaskad."""
    rng = np.random.default_rng(seed)
    met = M.yerel_metrik(box)
    tt, mm, xx, yy = [], [], [], []
    cells = grid.to_numpy(float)
    for lo, hi, mc in ((0, change, 3.1), (change, T, 2.5)):
        n = rng.poisson(th['mu'] * (hi - lo) * 10 ** (-b * (mc - 2.5)))
        cell = cells[rng.integers(0, len(cells), n)]
        lon = rng.uniform(cell[:, 0], cell[:, 1])
        lat = rng.uniform(cell[:, 2], cell[:, 3])
        x, y = met.km(lon, lat)
        tt.extend(rng.uniform(lo, hi, n)); mm.extend(mc + rng.exponential(1 / (b * M.LN10), n))
        xx.extend(x); yy.extend(y)
    for ta, ma in ana:
        cell = cells[rng.integers(0, len(cells))]
        x, y = met.km(np.array([rng.uniform(cell[0], cell[1])]), np.array([rng.uniform(cell[2], cell[3])]))
        tt.append(ta); mm.append(ma); xx.append(x[0]); yy.append(y[0])
    for i in range(60000):
        if i >= len(tt):
            break
        n = rng.poisson(th['K'] * 10 ** (th['alpha'] * (mm[i] - 2.5)) * th['c'] ** (1 - th['p']) / (th['p'] - 1))
        t = tt[i] + th['c'] * (rng.random(n) ** (-1 / (th['p'] - 1)) - 1)
        m = 2.5 + rng.exponential(1 / (b * M.LN10), n)
        Di = th['D'] * 10 ** (th['gamma'] * (mm[i] - 2.5))
        r = Di * np.sqrt((1 - rng.random(n)) ** (-1 / (th['q'] - 1)) - 1)
        a = rng.uniform(0, 2 * np.pi, n)
        x = xx[i] + r * np.cos(a); y = yy[i] + r * np.sin(a)
        lon, lat = met.derece(x, y)
        inside = hucre_indeks(pd.DataFrame(dict(boylam=lon, enlem=lat)), grid) >= 0
        keep = (t < T) & (m >= tamlik(t, change)) & inside
        tt.extend(t[keep]); mm.extend(m[keep]); xx.extend(x[keep]); yy.extend(y[keep])
    else:
        raise ValueError('Sentetik bütçe')
    o = np.argsort(tt)
    lon, lat = met.derece(np.asarray(xx)[o], np.asarray(yy)[o])
    return np.asarray(tt)[o], np.asarray(mm)[o], lon, lat


def dunya(seed=11):
    b, p, c, al = 1.0, 1.2, .02, .8
    K = .5 * (p - 1) * c ** (p - 1) * (b - al) / b
    th = dict(mu=.25, K=K, c=c, alpha=al, p=p, D=1.2, q=1.8, gamma=.2)
    ana = [(300, 6.4), (700, 6.7), (1100, 6.3), (1700, 6.6), (2100, 6.5), (2500, 6.4), (1300, 6.2), (2800, 6.8)]
    T, change = 3000., 1500.
    grid = izgara(KUTU, eksik=True)
    t, m, x, y = benzet_ek(th, b, T, change, grid, KUTU, seed, ana)
    return th, b, T, change, grid, (t, m, x, y)


class TestWOzdeslik(unittest.TestCase):
    def setUp(self):
        self.box, self.b, self.T, self.change = KUTU, 1.0, 1500., 750.
        self.grid = izgara(self.box, eksik=True)
        self.th = dict(mu=.38, c=.03, alpha=.45, p=1.35, D=1.2, q=1.8, gamma=.2)
        self.th['K'] = .6 * (self.th['p'] - 1) * self.th['c'] ** (self.th['p'] - 1) * (1 - self.th['alpha'])
        t, m, x, y = benzet_ek(self.th, self.b, self.T, self.change, self.grid, self.box, 5, [])
        m = m.copy()
        self.idx = [i for i in (50, 200, 400) if i < len(m)]
        m[self.idx] = [5.6, 6.1, 5.2][:len(self.idx)]
        self.veri = (t, m, x, y)

    def _L(self, tur, buyuk=True):
        t, m, x, y = self.veri
        bm = m >= 5.0 if buyuk else np.zeros(len(m), bool)
        st = KisaTamlik(tur, self.change, self.b, t[bm], m[bm], self.T)
        return W(t, m, x, y, self.b, self.T, self.change, self.grid, self.box, None, st)

    def test_buyuk_olay_yoksa_R_ile_ozdes(self):
        t, m, x, y = self.veri
        Lr = R(t, m, x, y, self.b, self.T, self.change, self.grid, self.box, None)
        for tur in ('a', 'b'):
            L = self._L(tur, buyuk=False)
            th = self.th
            llr, gr = Lr.deger(th, True)
            ll, g = L.deger(th, True, (0.6, 1.5) if tur == 'b' else None)
            self.assertAlmostEqual(ll, llr, places=9)
            np.testing.assert_allclose(g[:8], gr, rtol=1e-10, atol=1e-10)
            if tur == 'b':
                np.testing.assert_allclose(g[8:], 0.0, atol=1e-12)

    def test_azalma_olabilirligi_arttirir_ve_sayisal_gradyan(self):
        v = np.array([self.th[k] for k in M.UZAY_ADLARI])
        for tur, theta in (('a', None), ('b', (0.6, 1.5))):
            L = self._L(tur)
            self.assertGreater(len(L.stai.mid), 0)
            ll, g = L.deger(self.th, True, theta)
            f = lambda z: L.deger(dict(zip(M.UZAY_ADLARI, z[:8])), False, tuple(z[8:]) if theta else None)
            z0 = np.r_[v, theta] if theta else v
            num = approx_derivative(f, z0, method='3-point', rel_step=1e-6)
            np.testing.assert_allclose(g, num.ravel(), rtol=2e-5, atol=2e-6)

    def test_donusturulmus_gradyan(self):
        from knotenlinie.etas_stai.mle import objektif
        from knotenlinie.etas_mc25.mle import donustur
        L = self._L('b')
        v = np.r_[donustur(self.th, self.b, 'ortak'), np.log([0.6, 1.5])]
        num = approx_derivative(lambda z: objektif(L, z)[0], v, method='3-point', rel_step=1e-6)
        np.testing.assert_allclose(objektif(L, v)[1], num.ravel(), rtol=2e-5, atol=2e-6)


class TestWGeriKazanim(unittest.TestCase):
    """Bilinen cevap: büyük olaylardan sonra gözlemin eksik kaldığı sentetik dünya."""

    @classmethod
    def setUpClass(cls):
        cls.th, cls.b, cls.T, cls.change, cls.grid, cls.tam = dunya()

    def _fit(self, t, m, x, y, tur='a', theta0=None):
        Lr = R(t, m, x, y, self.b, self.T, self.change, self.grid, KUTU, None)
        fr = r_ayarla(Lr, 'ortak', maksiter=150)
        bm = m >= 5.0
        st = KisaTamlik(tur, self.change, self.b, t[bm], m[bm], self.T)
        Lw = W(t, m, x, y, self.b, self.T, self.change, self.grid, KUTU, None, st)
        fw = ayarla(Lw, fr['parametreler'], theta0=theta0, maksiter=150)
        return fr, fw

    def _hata(self, par):
        # c ve K'nın log hatası: kısa süreli eksiklikten en çok bozulanlar
        return np.log(par['c'] / self.th['c']) ** 2 + np.log(par['K'] / self.th['K']) ** 2

    def _gozlenen(self, mod):
        t, m, x, y = [a.copy() for a in self.tam]
        rng = np.random.default_rng(3)
        bm = m >= 5.0
        ms = sonra_a(t, t[bm], m[bm])
        if mod == 'sert':          # tasarım: HKJ kuralıyla olay sil
            keep = m >= ms
        else:                      # tam model: yumuşak tespit
            mu = ms - Z95 * SIGMA
            q = np.where(np.isfinite(mu), ndtr((m - np.where(np.isfinite(mu), mu, 0)) / SIGMA), 1.)
            keep = rng.random(len(t)) < q
        self.assertGreater((~keep).sum(), 50)
        return t[keep], m[keep], x[keep], y[keep]

    def test_hkj_sert_silme_W_R_den_yakin(self):
        fr, fw = self._fit(*self._gozlenen('sert'))
        print('SENTETIK sert  R:', {k: round(v, 4) for k, v in fr['parametreler'].items()},
              ' W:', {k: round(v, 4) for k, v in fw['parametreler'].items()}, ' gercek c,K', self.th['c'], round(self.th['K'], 4))
        self.assertLess(self._hata(fw['parametreler']), self._hata(fr['parametreler']))
        self.assertGreater(fr['parametreler']['c'], 2 * self.th['c'])  # R'nin sapması gerçek
        self.assertLess(fw['parametreler']['c'], fr['parametreler']['c'])
        self.assertGreater(fw['logL'], fr['logL'])

    def test_yumusak_tespit_tam_model_yakin_geri_kazanim(self):
        fr, fw = self._fit(*self._gozlenen('rampa'))
        pw, pr = fw['parametreler'], fr['parametreler']
        print('SENTETIK rampa R:', {k: round(v, 4) for k, v in pr.items()},
              ' W:', {k: round(v, 4) for k, v in pw.items()})
        self.assertLess(self._hata(pw), 0.5 * self._hata(pr))
        self.assertLess(abs(np.log(pw['c'] / self.th['c'])), 0.25)
        self.assertLess(abs(pw['alpha'] - self.th['alpha']), 0.1)

    def test_hainzl_biçimi_theta_yonu(self):
        # gerçek mekanizma (b): dMc=1.0, tau=2 gün; W-b theta'yı aynı büyüklük mertebesinde bulur
        t, m, x, y = [a.copy() for a in self.tam]
        bt = m >= 5.0
        dMc, tau = 1.0, 2.0
        ms = sonra_b(t, t[bt], (dMc, tau))
        mu = ms - Z95 * SIGMA
        q = np.where(np.isfinite(mu), ndtr((m - np.where(np.isfinite(mu), mu, 0)) / SIGMA), 1.)
        keep = np.random.default_rng(4).random(len(t)) < q
        fr, fw = self._fit(t[keep], m[keep], x[keep], y[keep], tur='b')
        th_hat = fw['stai_theta']
        print('SENTETIK b theta', th_hat, 'gercek', (dMc, tau), 'R c', round(fr['parametreler']['c'], 4),
              'W c', round(fw['parametreler']['c'], 4))
        self.assertLess(abs(np.log(th_hat[0] / dMc)), np.log(2.0))
        self.assertLess(abs(np.log(th_hat[1] / tau)), np.log(3.0))
        self.assertLess(self._hata(fw['parametreler']), self._hata(fr['parametreler']))


if __name__ == '__main__':
    unittest.main()
