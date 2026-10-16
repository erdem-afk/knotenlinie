"""Cezalı İtalya R-tipi MLE: log θ'nın çekirdeğe doğru ampirik-Bayes büzülmesi.

Amaç (en küçüklenen): -logL_R(v) + Σ_k (g_k(v) - çekirdek_k)^2 / (2 τ²), g = `cekirdek.tema`
(7 bileşen). τ = ∞ cezasız R'dir (özdeş nesne). μ cezasız. Olabilirlik nesnesi
`knotenlinie/etas_uzun/mle.py::Olabilirlik`'tir (dokunulmaz); ceza yalnızca amaç fonksiyonunu sarar.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logit

from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.mle import coz
from knotenlinie.ortak_zemin.ayar import dallanma
from . import cekirdek as C

MC0_ITALYA = 2.5
TAU = (0.05, 0.1, 0.2, 0.4, 0.8, float('inf'))
SINIRLAR = [(-11.5, 6.9), (-9.2, float(logit(1 - 1e-6))), (-6.9, 3.4), (-9.2, 9.2), (-6.9, 1.386),
            (np.log(1e-5 * M.KM_DERECE), np.log(10 * M.KM_DERECE)), (-6.9, 2.3), (0., 2.)]


class Cezali:
    """L'nin sarmalayıcısı: `objectif(v, 'ortak')` = (-logL + ceza)/n ve gradyanı."""

    def __init__(self, L, cekirdek_tema, tau, mc0=MC0_ITALYA, maske=None):
        self.L = L
        self.cek = np.array([np.nan if x is None else x for x in cekirdek_tema], float)
        self.tau = float(tau)
        self.mc0 = float(mc0)
        if self.cek.shape != (7,):
            raise ValueError('çekirdek 7 bileşenli olmalı')
        self.maske = np.isfinite(self.cek) if maske is None else (np.asarray(maske, bool) & np.isfinite(self.cek))

    def ceza(self, v):
        """(ceza, d ceza / d v); toplam (n'ye bölünmemiş) ölçekte."""
        if not np.isfinite(self.tau):
            return 0.0, np.zeros(len(v))
        g = C.tema_v(v, self.L.b, self.mc0)
        J = C.tema_jakobi(v, self.L.b, self.mc0)
        d = np.where(self.maske, g - np.where(self.maske, self.cek, 0.0), 0.0)
        return float(d @ d) / (2 * self.tau ** 2), (J.T @ d) / self.tau ** 2

    def objectif(self, v, tur='ortak'):
        f, g = self.L.objectif(v, tur)
        n = len(self.L.t)
        c, gc = self.ceza(np.asarray(v, float))
        return f + c / n, g + gc / n


def ayarla_ceza(L, cekirdek_tema, tau, x0, *, maksiter=300, mc0=MC0_ITALYA, maske=None):
    """x0'dan başlayan tek L-BFGS-B (sıcak başlangıç); R'nin sınırları ve toleransları."""
    P = Cezali(L, cekirdek_tema, tau, mc0, maske)
    r = minimize(P.objectif, np.asarray(x0, float), args=('ortak',), jac=True, method='L-BFGS-B',
                 bounds=SINIRLAR, options=dict(maxiter=maksiter, ftol=1e-11, gtol=2e-7, maxls=40))
    th = coz(r.x, L.b, 'ortak')
    f, g = P.objectif(r.x)
    ll = float(-L.objectif(r.x, 'ortak')[0] * len(L.t))
    c, _ = P.ceza(r.x)
    return dict(parametreler=th, logL=ll, ceza=c, logL_cezali=ll - c, basari=bool(r.success), nit=int(r.nit),
                tur='ortak', tau=float(tau), dallanma=dallanma(th, L.b), x=r.x.tolist(),
                gradyan_sonsuz_norm=float(np.max(np.abs(g))), mesaj=str(r.message),
                tema=C.tema_v(r.x, L.b, mc0).tolist(),
                optimizer='L-BFGS-B; analitik gradyan + sayısal ceza Jakobiyeni; sıcak başlangıç')


# --------------------------------------------------------------------------- #
# İtalya olabilirliği (≤2005 ve ≤2010) — S/R kurulumlarının aynısı
# --------------------------------------------------------------------------- #
def italya_L(raw, grid, son):
    """R-ortak MLE'sinin olabilirlik nesnesi. son: '2006-01-01' (≤2005) ya da '2011-01-01' (≤2010)."""
    from knotenlinie.etas_uzun.arayuz import ebeveynler
    from knotenlinie.etas_uzun.maske import arka_plan_sec
    from knotenlinie.etas_uzun.mle import Olabilirlik, b_ayarla
    from knotenlinie.etas_uzun.olcek import kde_sec
    from knotenlinie.ortak_zemin.arayuz import utc
    from knotenlinie.ortak_zemin.veri import hucre_indeks
    epoch, end = utc('1985-01-01T00:00:00Z'), utc(son + 'T00:00:00Z')
    if son not in ('2006-01-01', '2011-01-01'):
        raise ValueError('son 2006-01-01 ya da 2011-01-01')
    raw = raw[raw.zaman < end]
    box = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    d = ebeveynler(raw, box, end)
    target = d[hucre_indeks(d, grid) >= 0].reset_index(drop=True)
    mc = np.where(target.zaman < utc('2005-01-01T00:00:00Z'), 3.1, 2.5)
    bmeta = b_ayarla(target.mw.to_numpy(), mc)
    hist = kde_sec(target, grid, box) if son == '2006-01-01' else arka_plan_sec(target, grid, box, end)
    t = ((d.zaman - epoch) / pd.Timedelta(days=1)).to_numpy(float)
    T = float((end - epoch) / pd.Timedelta(days=1))
    change = float((utc('2005-01-01T00:00:00Z') - epoch) / pd.Timedelta(days=1))
    u = M.arka_plan_degeri(d.boylam.to_numpy(), d.enlem.to_numpy(), hist)
    L = Olabilirlik(t, d.mw.to_numpy(), d.boylam.to_numpy(), d.enlem.to_numpy(), bmeta['deger'], T, change,
                    grid, box, u)
    return L, dict(b=bmeta, arka_plan=hist, kutu=box, ayar_n=len(d), hedef_n=len(target))


def model_p(r_json, ceza_fit):
    """UzunETAS için parametre sözlüğü: R dosyasının üstüne cezalı parametreler yazılır."""
    p = dict(r_json)
    p['parametreler'] = {k: float(v) for k, v in ceza_fit['parametreler'].items()}
    p['dallanma'] = float(ceza_fit['dallanma'])
    p['x'] = list(ceza_fit['x'])
    p['logL'] = float(ceza_fit['logL'])
    p['hiyerarsi'] = {k: ceza_fit[k] for k in ('tau', 'ceza', 'logL_cezali', 'tema', 'basari', 'nit')}
    return p


# --------------------------------------------------------------------------- #
# Zaman-havuzu çekirdeği: İtalya'nın kendi 1985–2004 (Mc 3,1) ayarı
# --------------------------------------------------------------------------- #
def italya_havuz_kur(cat, grid, *, maksiter=300):
    """N'nin Mc-sabit kurulumunun 1985–2004 kesiti (sınırlı: CSEP maskesi yok, dış dikdörtgen)."""
    from knotenlinie.etas_mc25.mle import Olabilirlik as SabitL, ayarla as sabit_ayarla
    from knotenlinie.ortak_zemin.arayuz import utc
    from knotenlinie.ortak_zemin.arka_plan import BANTLAR_KM, ZEMIN_PAYLARI, kde_histogram
    from knotenlinie.ortak_zemin.ayar import b_ayarla
    MC = 3.1
    epoch, end = utc('1985-01-01T00:00:00Z'), utc('2005-01-01T00:00:00Z')
    d = cat[(cat.zaman >= epoch) & (cat.zaman < end) & (cat.derinlik < 30) & (cat.mw >= MC)].reset_index(drop=True)
    kutu = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    b = b_ayarla(d.mw.to_numpy(), MC)
    met = M.yerel_metrik(kutu)
    split = epoch + (end - epoch) / 2
    tr, ho = d[d.zaman < split], d[d.zaman >= split]
    best = None
    for h in BANTLAR_KM:
        for eps in ZEMIN_PAYLARI:
            hist = kde_histogram(tr.boylam, tr.enlem, kutu, h, eps)
            u = M.arka_plan_degeri(ho.boylam.to_numpy(), ho.enlem.to_numpy(), hist)
            s = float(np.log(u / met.jakobiyen).sum())
            if best is None or s > best[0]:
                best = (s, h, eps)
    hist = kde_histogram(d.boylam, d.enlem, kutu, best[1], best[2])
    T = float((end - epoch) / pd.Timedelta(days=1))
    t = ((d.zaman - epoch) / pd.Timedelta(days=1)).to_numpy(float)
    L = SabitL(t, d.mw.to_numpy(float), d.boylam.to_numpy(float), d.enlem.to_numpy(float), MC, b['deger'], T,
               kutu, M.arka_plan_degeri(d.boylam, d.enlem, hist))
    fit = sabit_ayarla(L, 'ortak', maksiter=maksiter)
    kayit = dict(ad='italya-1985-2004-Mc3.1', mc0=MC, b=float(b['deger']),
                 parametreler={k: float(v) for k, v in fit['parametreler'].items()},
                 tema=C.tema(fit['parametreler'], MC).tolist(), dallanma=float(fit['dallanma']),
                 basari=bool(fit['basari']), logL=float(fit['logL']), n_olay=int(len(d)), x=list(map(float, fit['x'])),
                 kde=dict(bant_km=best[1], zemin_payi=best[2]), ayar_baslangic=epoch.isoformat(),
                 ayar_bitis_haric=end.isoformat())
    cov, tani = C.tema_kovaryans(L, fit['x'], MC)
    kayit.update(tema_var=np.diag(cov).tolist(), tema_std=np.sqrt(np.diag(cov)).tolist(), kovaryans_tani=tani)
    return kayit
