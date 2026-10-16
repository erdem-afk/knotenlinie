"""CSEP hücre birleşiminin yönlü sınırı ve birim maskeli KDE."""
import numpy as np
import pandas as pd
from knotenlinie.etas import model as M
from knotenlinie.ortak_zemin.veri import izgara_dogrula, hucre_indeks
from knotenlinie.ortak_zemin.arka_plan import kde_histogram, BANTLAR_KM, ZEMIN_PAYLARI


def sinir(izgara, met):
    """İç kenarlar iptal; aynı doğru üzerindeki ardışık sınırlar birleşir."""
    g, origin, size, lookup = izgara_dogrula(izgara)
    segments = []
    for i, j in lookup:
        if (i, j-1) not in lookup: segments.append((0, j, i, i+1, 1))
        if (i+1, j) not in lookup: segments.append((1, i+1, j, j+1, 1))
        if (i, j+1) not in lookup: segments.append((0, j+1, i, i+1, -1))
        if (i-1, j) not in lookup: segments.append((1, i, j, j+1, -1))
    groups = {}
    for axis, line, a, b, sign in segments:
        groups.setdefault((axis, line, sign), []).append((a, b))
    edges = []
    for (axis, line, sign), intervals in sorted(groups.items()):
        merged = []
        for a, b in sorted(intervals):
            if merged and merged[-1][1] == a: merged[-1][1] = b
            else: merged.append([a, b])
        for a, b in merged:
            p, q = ((a, line), (b, line)) if axis == 0 else ((line, a), (line, b))
            if sign < 0: p, q = q, p
            edges.append([origin+size*np.array(p), origin+size*np.array(q)])
    edges = np.asarray(edges)
    ax, ay = met.km(edges[:, 0, 0], edges[:, 0, 1])
    bx, by = met.km(edges[:, 1, 0], edges[:, 1, 1])
    return ax, ay, bx, by


class MaskeIntegrali:
    """Radyal CDF sınır integrali; delikler/maske dışı anneler desteklenir."""
    def __init__(self, x, y, izgara, met, blok=32):
        ax, ay, bx, by = sinir(izgara, met)
        xk, yk = met.km(x, y)
        self.n = len(xk); self.parcalar = []; self.kenar = len(ax)
        for a in range(0, self.n, blok):
            z = min(self.n, a+blok)
            R, w, pair, _ = M._ucgen_dugumleri(xk[a:z, None], yk[a:z, None], ax, ay, bx, by)
            self.parcalar.append((a, z, R, w, (pair//len(ax)).astype(np.int32)))

    def deger(self, Di, q, grad=False):
        G = np.zeros(self.n); dD = G.copy(); dq = G.copy()
        for a, z, R, w, j in self.parcalar:
            U = R/Di[a:z][j]**2; L = np.log1p(U); E = np.exp((1-q)*L)
            G[a:z] = np.bincount(j, w*(-np.expm1((1-q)*L)), minlength=z-a)
            if grad:
                dD[a:z] = np.bincount(j, w*2*(1-q)*U/(1+U)*E, minlength=z-a)
                dq[a:z] = np.bincount(j, w*L*E, minlength=z-a)
        if (G < -1e-10).any() or (G > 1+1e-10).any(): raise ValueError('Maske integrali [0,1] dışında')
        return (G, dD, dq) if grad else G


def maskeli_hist(d, grid, kutu, h, eps):
    """KDE maskeye koşullu; düzgün bileşen yalnız maskenin alanında."""
    hist = kde_histogram(d.boylam, d.enlem, kutu, h, .001)
    xe, ye = np.asarray(hist['x_kenar']), np.asarray(hist['y_kenar'])
    area = np.diff(xe)[:, None]*np.diff(ye)[None, :]
    density = (np.asarray(hist['yogunluk'])-.001/area.sum())/.999
    g = grid.to_numpy(float)
    ix = np.rint((g[:, 0]-xe[0])/.1).astype(int); iy = np.rint((g[:, 2]-ye[0])/.1).astype(int)
    mask = np.zeros_like(density, bool); mask[ix, iy] = True
    density *= mask
    density /= np.sum(density*area)
    density = (1-eps)*density+eps*mask/area[mask].sum()
    hist.update(yogunluk=density, zemin_payi=eps, tur='CSEP-maskeye koşullu KDE + maskede düzgün zemin',
                maskeli=True, maske_kutlesi=float(np.sum(density*area)))
    return hist


def arka_plan_sec(d, grid, kutu, son):
    if (d.zaman >= son).any() or (hucre_indeks(d, grid) < 0).any(): raise ValueError('KDE hedef kapısı')
    split = pd.Timestamp('2006-01-01', tz='UTC')
    train, hold = d[d.zaman < split], d[d.zaman >= split]
    trials = []
    for h in BANTLAR_KM:
        for eps in ZEMIN_PAYLARI:
            hist = maskeli_hist(train, grid, kutu, h, eps)
            u = M.arka_plan_degeri(hold.boylam.to_numpy(), hold.enlem.to_numpy(), hist)
            trials.append(dict(bant_km=h, zemin_payi=eps, logL_konum=float(np.log(u).sum())))
    best = max(trials, key=lambda r:r['logL_konum'])
    hist = maskeli_hist(d, grid, kutu, best['bant_km'], best['zemin_payi'])
    hist['secim'] = dict(kurulum_bitis_haric=split.isoformat(), secim_bitis_haric=son.isoformat(),
                        kurulum_n=len(train), secim_n=len(hold), yeniden_kurulum_n=len(d),
                        yeniden_kurulum_max_zaman=d.zaman.max().isoformat(), en_iyi=best, adaylar=trials)
    return hist
