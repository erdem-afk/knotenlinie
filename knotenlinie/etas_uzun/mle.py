"""Zamanla değişen Mc, hedef maskesi ve dış ebeveynli analitik MLE."""
import numpy as np
from knotenlinie.etas import model as M
from knotenlinie.etas_mc25.mle import coz, donustur, ayarla
from knotenlinie.etas_mc25.mle import Olabilirlik as SabitOlabilirlik
from knotenlinie.ortak_zemin.arayuz import omori_kutle
from .maske import MaskeIntegrali

MC0 = 2.5


def tamlik(t, kirilma):
    return np.where(np.asarray(t) < kirilma, 3.1, MC0)


def b_ayarla(m, mc):
    """Ortak tabanın GR MLE'si; gerçek Mw çözünürlüğü, sabit 0.1 değil."""
    from knotenlinie.ortak_zemin.ayar import b_ayarla as ortak_b
    excess = np.asarray(m, float)-np.asarray(mc, float)
    if (excess < -1e-12).any(): raise ValueError('b için kendi Mc üstü olaylar')
    result = ortak_b(np.maximum(excess, 0.), 0.)
    result.update(tur='GR MLE, Mc(t), gerçek çözünürlük', referans_Mc=MC0,
                  ortalama_fazla=float(excess.mean()))
    return result


class Olabilirlik(SabitOlabilirlik):
    """λ_obs(t)=10^-b(Mc(t)-Mc0)[μu+Σ K10^α(Mj-Mc0)fg].

    Ebeveyn kendi zamanındaki Mc üstünde; yalnız maskede olay hedef.
    Eksik düşük-M ebeveynler impute edilmez. Referans Mc0 sabit, dönemler
    arası üretkenlik yapay yeniden tanımlanmaz. Büyüklük markı sabit b.
    """
    def __init__(self, t, m, x, y, b, T, kirilma, grid, kutu, u=None):
        self.t = np.asarray(t, float); self.dm = np.asarray(m, float)-MC0
        self.b, self.T, self.kirilma = b, T, kirilma
        self.mc, self.kutu = MC0, tuple(kutu)
        if not (0 < kirilma < T) or not len(t) or (self.t < 0).any() or (self.t >= T).any() or (np.diff(self.t) < 0).any():
            raise ValueError('MLE zaman kapısı')
        if (np.asarray(m) < tamlik(self.t, kirilma)).any(): raise ValueError('Olay kendi Mc altında')
        from knotenlinie.ortak_zemin.veri import hucre_indeks
        import pandas as pd
        inside = hucre_indeks(pd.DataFrame(dict(boylam=x, enlem=y)), grid) >= 0
        self.hedef = np.flatnonzero(inside)
        self.nhedef = len(self.hedef)
        if not self.nhedef: raise ValueError('Maskede hedef yok')
        self.met = M.yerel_metrik(kutu)
        xk, yk = self.met.km(x, y)
        self.parcalar = []; self.cift = 0
        # Tam çiftler, 128 hedeflik bloklar; kesme/örnekleme yok.
        for a in range(0, self.nhedef, 128):
            targets = self.hedef[a:a+128]
            ii, jj = np.nonzero(self.t[targets, None] > self.t[None, :])
            i = targets[ii]; j = jj.astype(np.int32)
            self.parcalar.append((ii.astype(np.int32), j, self.t[i]-self.t[j],
                                  (xk[i]-xk[j])**2+(yk[i]-yk[j])**2, a, len(targets)))
            self.cift += len(i)
        self.i = range(self.cift)  # ayarla'nın yalnız len() metadata arayüzü
        area = ((grid.boylam_max-grid.boylam_min)*(grid.enlem_max-grid.enlem_min)).sum()
        all_u = np.full(len(t), 1/area) if u is None else np.asarray(u, float)
        self.u = all_u[self.hedef]/self.met.jakobiyen
        self.s = 10**(-b*(tamlik(self.t[self.hedef], kirilma)-MC0))
        self.arka_T = kirilma*10**(-b*.6)+(T-kirilma)
        self.mask = MaskeIntegrali(x, y, grid, self.met)
        # Zaman kompansatörü iki Mc döneminde ayrı; doğum öncesi integral yok.
        self.araliklar = []
        for lo, hi, mc in ((0., kirilma, 3.1), (kirilma, T, MC0)):
            active = self.t < hi
            self.araliklar.append((active, np.maximum(lo-self.t[active], 0.), hi-self.t[active], 10**(-b*(mc-MC0))))

    def zaman(self, c, p):
        I = np.zeros(len(self.t)); Ic = I.copy(); Ip = I.copy()
        for active, lo, hi, s in self.araliklar:
            v, vc, vp = M._omori_ilke(hi, c, p)
            w, wc, wp = M._omori_ilke(lo, c, p)
            I[active] += s*(v-w); Ic[active] += s*(vc-wc); Ip[active] += s*(vp-wp)
        return I, Ic, Ip

    def deger(self, th, grad=False):
        mu, K, c, alpha, p, D, q, gamma = [th[k] for k in M.UZAY_ADLARI]
        Di = D*np.exp(M.LN10*gamma*self.dm); A = np.exp(M.LN10*alpha*self.dm)
        ll = 0.; g = np.zeros(8)
        for i, j, dt, r2, a, n in self.parcalar:
            dc = dt+c; U = r2/Di[j]**2; L = np.log1p(U)
            z = K*A[j]*np.exp(-p*np.log(dc))*(q-1)/(np.pi*Di[j]**2)*np.exp(-q*L)
            ub = self.u[a:a+n]
            lam = mu*ub+np.bincount(i, z, minlength=n)
            if not np.isfinite(lam).all() or (lam <= 0).any(): raise ValueError('Geçersiz oran')
            ll += np.log(lam*self.s[a:a+n]).sum()
            if grad:
                wz = z/lam[i]; scale = 2*(-1+q*U/(1+U))
                g += np.array([np.dot(1/lam, ub), wz.sum()/K,
                               np.dot(wz, -p/dc), np.dot(wz, M.LN10*self.dm[j]),
                               np.dot(wz, -np.log(dc)), np.dot(wz, scale)/D,
                               np.dot(wz, 1/(q-1)-L), np.dot(wz, scale*M.LN10*self.dm[j])])
        G, GD, Gq = self.mask.deger(Di, q, True)
        I, Ic, Ip = self.zaman(c, p); comp = K*A*I
        ll -= mu*self.arka_T+np.dot(comp, G)
        if not grad: return float(ll)
        g -= np.array([self.arka_T, np.dot(A*I, G), np.dot(K*A*Ic, G),
                       np.dot(comp*M.LN10*self.dm, G), np.dot(K*A*Ip, G),
                       np.dot(comp, GD)/D, np.dot(comp, Gq), np.dot(comp*M.LN10*self.dm, GD)])
        return float(ll), g
