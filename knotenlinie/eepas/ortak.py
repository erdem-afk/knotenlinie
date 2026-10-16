"""C2: maskeli ortak alan, aynı geçmiş filtresi ve günlük Poisson puanı."""
from __future__ import annotations

from dataclasses import dataclass, replace, asdict

import numpy as np
import pandas as pd
from scipy import optimize

from .model import (zaman_gun, katalog_dizileri, gaussian_hucre,
                    buyukluk_kutlesi, zaman_kutlesi, eta, LN10, GUN)
from .janus import bilgi_kazanci

IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']
AYAR_SONU = pd.Timestamp('2011-01-01', tz='UTC')
KESIM = pd.Timestamp('2016-01-01', tz='UTC')


def utc(t):
    return pd.to_datetime(t, utc=True, format='mixed')


class Alan:
    """Ayrık yarım açık dikdörtgenler; boşluklar skor alanı değildir."""
    def __init__(self, izgara, m_kenarlar, hedef_alt=4.95):
        self.izgara = izgara[IZGARA].reset_index(drop=True).copy()
        g = self.izgara.to_numpy(float)
        e = np.asarray(m_kenarlar, float)
        if (not len(g) or not np.isfinite(g).all() or
                np.any(g[:, 0] >= g[:, 1]) or np.any(g[:, 2] >= g[:, 3])):
            raise ValueError('Geçerli dolu ortak ızgara gerekli')
        if (e.ndim != 1 or len(e) < 2 or not np.isfinite(e).all() or
                np.any(np.diff(e) <= 0) or e[0] != hedef_alt or hedef_alt not in (3.95, 4.95)):
            raise ValueError('M>=3.95/4.95 artan sonlu ortak büyüklük kenarları gerekli')
        size = np.array([g[0, 1]-g[0, 0], g[0, 3]-g[0, 2]])
        origin = np.array([g[:, 0].min(), g[:, 2].min()])
        keys = (g[:, [0, 2]]-origin)/size
        regular = (np.allclose(g[:, 1]-g[:, 0], size[0], atol=1e-9, rtol=0) and
                   np.allclose(g[:, 3]-g[:, 2], size[1], atol=1e-9, rtol=0) and
                   np.allclose(keys, np.rint(keys), atol=1e-7, rtol=0))
        self.lookup = None
        if regular:
            self.origin, self.size = origin, size
            self.lookup = {tuple(k): i for i, k in enumerate(np.rint(keys).astype(int))}
            if len(self.lookup) != len(g):
                raise ValueError('Ortak ızgarada örtüşen hücreler')
        else:
            for a in range(0, len(g), 128):
                h = g[a:a+128]
                overlap = ((np.minimum(h[:, None, 1], g[:, 1]) > np.maximum(h[:, None, 0], g[:, 0])+1e-10) &
                           (np.minimum(h[:, None, 3], g[:, 3]) > np.maximum(h[:, None, 2], g[:, 2])+1e-10))
                overlap[np.arange(len(h)), np.arange(a, a+len(h))] = False
                if overlap.any():
                    raise ValueError('Ortak ızgarada örtüşen hücreler')
        self.g, self.m_kenarlar = g, e.copy()
        self.kutu = (g[:, 2].min(), g[:, 3].max(), g[:, 0].min(), g[:, 1].max())

    def indeks(self, df):
        xy = df[['boylam', 'enlem']].to_numpy(float)
        if not np.isfinite(xy).all():
            raise ValueError('Olay konumu sonlu değil')
        if self.lookup is not None:
            keys = np.floor((xy-self.origin)/self.size+1e-10).astype(int)
            return np.array([self.lookup.get(tuple(k), -1) for k in keys], int)
        out = np.full(len(df), -1, int)
        lon, lat = xy.T
        # Komşu hücrelerde CSV kayan nokta kenarları ortak 12 basamakta buluşur.
        g = np.round(self.g, 12)
        lon, lat = np.round(lon, 12), np.round(lat, 12)
        for a in range(0, len(df), 128):
            x, y = lon[a:a+128, None], lat[a:a+128, None]
            hit = (x >= g[:, 0]) & (x < g[:, 1]) & (y >= g[:, 2]) & (y < g[:, 3])
            if np.any(hit.sum(axis=1) > 1):
                raise ValueError('Olay birden çok ortak hücrede')
            i, j = np.nonzero(hit)
            out[a+i] = j
        return out


@dataclass(frozen=True)
class GecmisFiltresi:
    """T teslimindeki başlangıç/derinlik alanı; hedef ve geçmişe aynı uygulanır."""
    baslangic: str
    derinlik_min: float
    derinlik_max: float
    ust_dahil: bool = True

    def __post_init__(self):
        if (utc(self.baslangic) >= AYAR_SONU or
                not np.isfinite([self.derinlik_min, self.derinlik_max]).all() or
                self.derinlik_max <= self.derinlik_min):
            raise ValueError('Geçerli ayar öncesi geçmiş filtresi gerekli')

    def uygula(self, df, alan):
        d = df[['zaman', 'enlem', 'boylam', 'derinlik', 'mw']].copy()
        d['zaman'] = utc(d.zaman)
        if d.zaman.isna().any() or (d.zaman >= KESIM).any():
            raise ValueError('Yalnız <=2015 açık katalog/geçmiş')
        if not np.isfinite(d[['enlem', 'boylam', 'derinlik', 'mw']].to_numpy(float)).all():
            raise ValueError('Katalogda eksik/sonsuz değer; sessiz derinlik atama yok')
        high = d.derinlik <= self.derinlik_max if self.ust_dahil else d.derinlik < self.derinlik_max
        ok = ((d.zaman >= utc(self.baslangic)) & (d.derinlik >= self.derinlik_min) & high &
              (alan.indeks(d) >= 0))
        return d.loc[ok].sort_values('zaman', kind='stable').reset_index(drop=True)


class FiltreliModel:
    """Kamusal arayüzde de ayardaki alan/derinlik/başlangıç filtresini koru."""
    def __init__(self, callback, alan, filtre):
        self.callback, self.alan, self.filtre = callback, alan, filtre

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, b = utc(baslangic), utc(bitis)
        if a >= b or (utc(gecmis.zaman) >= a).any():
            raise ValueError('Geçmiş başlangıçtan önce; pozitif pencere gerekli')
        d = self.filtre.uygula(gecmis, self.alan)
        return self.callback(a, b, d, izgara, m_kenarlar)


class OrtakJanus:
    """T'nin callable ETAS'ını değiştirmeyen konveks karışım."""
    def __init__(self, eepas, etas, agirlik):
        if not np.isfinite(agirlik) or not 0 <= agirlik <= 1:
            raise ValueError('Janus ağırlığı [0,1] olmalı')
        self.eepas, self.etas, self.agirlik = eepas, etas, float(agirlik)

    def beklenen(self, *args):
        w = self.agirlik
        return w*self.eepas(*args)+(1-w)*self.etas(*args)


def tamlik_sec(katalog, baslangic, bolge, dilim_yil=5, n_min=500,
               son=AYAR_SONU, hedef_alt=4.95):
    """Yalnız belirtilen ayar sonundan önceki MBS; max(Mc)+0.2."""
    from knotenlinie.etas.tamlik import mc_wiemer_wyss
    start, end = utc(baslangic), utc(son)
    hedef_alt = float(hedef_alt)
    if (not start < end <= AYAR_SONU or start.month != 1 or start.day != 1 or
            end.month != 1 or end.day != 1 or hedef_alt not in (3.95, 4.95)):
        raise ValueError('Tamlık başlangıcı/sonu ayar öncesi yıl başı olmalı')
    train = katalog.loc[(utc(katalog.zaman) >= start) & (utc(katalog.zaman) < end)]
    cuts = list(range(start.year, end.year, dilim_yil)) + [end.year]
    # Son kısa dilim bir öncekiyle birleştirilir (tek yıllık Mc tahmini yok).
    if len(cuts) > 2 and cuts[-1]-cuts[-2] < 3:
        cuts.pop(-2)
    floor = {'italya': 2.0}[bolge]
    overall = mc_wiemer_wyss(train.mw.to_numpy(float), baslangic=floor)
    if overall['mc'] is None:
        raise ValueError(f'{bolge}: genel kararlı MBS Mc yok')
    rows = []
    for a, b in zip(cuts[:-1], cuts[1:]):
        d = train.loc[(utc(train.zaman) >= utc(f'{a}-01-01')) &
                      (utc(train.zaman) < utc(f'{b}-01-01'))]
        if len(d) < n_min:
            raise ValueError(f'{bolge} {a}–{b-1}: tamlık için <{n_min} olay')
        r = mc_wiemer_wyss(d.mw.to_numpy(float), baslangic=floor)
        if r['mc'] is None:
            raise ValueError(f'{bolge} {a}–{b-1}: kararlı MBS Mc yok')
        rows.append({'baslangic': a, 'bitis': b-1, 'n': len(d), 'mc': r['mc']})
    m0 = float(np.ceil((max([overall['mc']]+[r['mc'] for r in rows])+.2)*10-1e-9)/10)
    if m0 >= hedef_alt:
        raise ValueError('Öncü tamlık eşiği hedefe ulaştı')
    return m0, {'m0': m0, 'dilimler': rows, 'genel_mc': overall['mc'], 'arama_alt': floor,
                'hedef_oncu_farki': hedef_alt-m0, 'hedef_alt': hedef_alt,
                'fark_1_5_kapisi': hedef_alt-m0 >= 1.5, 'bitis_haric': end.isoformat(),
                'kural': 'max(ayar sonu öncesi MBS dilimleri Mc)+0.2; 0.1 M yukarı yuvarlama'}


def gunluk_puan(callback, katalog, alan, baslangic, bitis):
    """Tam maskede integral, olay hücresinde lambda; UTC gün başında geçmiş donar."""
    a, b = utc(baslangic), utc(bitis)
    if a != a.floor('D') or b != b.floor('D') or a >= b or b > KESIM:
        raise ValueError('<=2015, artan UTC tam günlük puan penceresi gerekli')
    d = katalog.loc[utc(katalog.zaman) < b].copy()
    cell = alan.indeks(d)
    mb = np.searchsorted(alan.m_kenarlar, d.mw.to_numpy(float), side='right')-1
    ok = ((utc(d.zaman) >= a) & (cell >= 0) & (mb >= 0) & (mb < len(alan.m_kenarlar)-1))
    target = d.loc[ok].reset_index(drop=True)
    ti, mi = cell[ok], mb[ok]
    lambdas = np.zeros(len(target))
    total = 0.0
    for day in pd.date_range(a, b, freq='D', inclusive='left'):
        past = d.loc[utc(d.zaman) < day]
        rates = np.asarray(callback(day, day+GUN, past, alan.izgara, alan.m_kenarlar), float)
        if (rates.shape != (len(alan.izgara), len(alan.m_kenarlar)-1) or
                not np.isfinite(rates).all() or (rates < 0).any()):
            raise ValueError('Modelin ortak beklenen çıktısı geçersiz')
        total += float(rates.sum())
        idx = np.flatnonzero(utc(target.zaman).dt.floor('D') == day)
        lambdas[idx] = rates[ti[idx], mi[idx]]
    if (lambdas <= 0).any():
        raise ValueError('Olay hücresinde sıfır oran; epsilon eklenmez')
    return lambdas, total


class EEPASOnhesap:
    """Sabit NZ uzay/büyüklük şekli; günlük maskeli ayarda yalnız mu/aT serbest.

    Mekân bir kez hesaplanır. 50 günlük kesme nedeniyle bütün pencere integrali,
    günlük başlangıç geçmişi integrallerinin toplamına tam eşittir.
    """
    def __init__(self, model, katalog, alan, baslangic, bitis):
        p = model.p
        a, b = utc(baslangic), utc(bitis)
        if p.gecikme < 1 or a != a.floor('D') or b != b.floor('D') or a >= b or b > KESIM:
            raise ValueError('EEPAS önhesabı günlük pencere ve >=1 gün kesme ister')
        self.p, self.alan, self.a, self.b = p, alan, a, b
        d = katalog.loc[utc(katalog.zaman) < b].copy()
        ci = alan.indeks(d)
        mi = np.searchsorted(alan.m_kenarlar, d.mw.to_numpy(float), side='right')-1
        ok = ((utc(d.zaman) >= a) & (ci >= 0) & (mi >= 0) & (mi < len(alan.m_kenarlar)-1))
        targets = d.loc[ok].reset_index(drop=True)
        self.targets = targets
        self.days = zaman_gun(utc(targets.zaman).dt.floor('D'))
        self.ci, self.mi = ci[ok], mi[ok]
        parents = d.loc[d.mw >= p.m0]
        self.pt, self.pm, pl, pa = katalog_dizileri(parents)
        n = len(parents)
        self.coeff = np.empty((len(targets), n))
        self.mass = np.empty(n)
        # N_hedef*N_öncü katsayı; G*N_öncü matris tutulmaz, mekân bloklanır.
        for j in range(0, n, 256):
            sl = slice(j, j+256)
            x, y = model.met.km(pl[sl], pa[sl])
            sig = p.sigmaA*10**(p.bA*self.pm[sl]/2)
            mg = buyukluk_kutlesi(alan.m_kenarlar, self.pm[sl], p)
            source = eta(self.pm[sl], p)
            spatial = np.zeros(len(self.pm[sl]))
            for k in range(0, len(alan.izgara), 128):
                spatial += gaussian_hucre(x, y, sig, alan.izgara.iloc[k:k+128], model.met).sum(axis=0)
            self.mass[sl] = spatial*mg.sum(axis=0)*source
            h = gaussian_hucre(x, y, sig, alan.izgara.iloc[self.ci], model.met)
            self.coeff[:, sl] = h*mg[self.mi]*source
        e = alan.m_kenarlar
        bgm = np.exp(-p.b*LN10*(e[:-1]-p.m0))*(-np.expm1(-p.b*LN10*np.diff(e)))
        bg = model.arka_plan.kutle(alan.izgara)[:, None]*bgm
        self.bg_lam = p.r0*bg[self.ci, self.mi]
        self.bg_total = p.r0*float((b-a)/GUN)*bg.sum()

    def puan(self, p):
        fixed = ('m0', 'b', 'r0', 'aM', 'bM', 'sigmaM', 'bT', 'sigmaT',
                 'sigmaA', 'bA', 'gecikme', 'telafi')
        if any(getattr(p, k) != getattr(self.p, k) for k in fixed):
            raise ValueError('Önhesapta yalnız mu/aT/olcek değişebilir')
        lam = p.mu*self.bg_lam.copy()
        for i in range(0, len(self.targets), 64):
            sl = slice(i, i+64)
            dt = self.days[sl, None]-self.pt
            tm = zaman_kutlesi(dt, dt+1, self.pm, p)*(dt > 0)
            lam[sl] += (1-p.mu)*(tm*self.coeff[sl]).sum(axis=1)
        t0, t1 = zaman_gun([self.a, self.b])
        tm = zaman_kutlesi(t0-self.pt, t1-self.pt, self.pm, p)
        total = p.mu*self.bg_total+(1-p.mu)*float(tm @ self.mass)
        return p.olcek*lam, p.olcek*total


def eepas_ayarla_ortak(onhesap, maksiter=200, ppe_alt=.05):
    """Maskeli binned MLE, profil ölçeği; PPE payı >=%5 ayardan önce sabit kapı."""
    if onhesap.b > AYAR_SONU or not 0 < ppe_alt < 1 or len(onhesap.targets) < 2:
        raise ValueError('<=2010 ayar, >=2 hedef ve pozitif PPE alt sınırı gerekli')
    base = replace(onhesap.p, olcek=1.)
    def build(x):
        q = replace(base, mu=float(x[0]), aT=float(x[1]))
        lam, total = onhesap.puan(q)
        if total <= 0 or not np.isfinite(total):
            return q, -np.inf
        scale = len(lam)/total
        q = replace(q, olcek=scale)
        logl = float(np.log(lam*scale).sum()-len(lam)) if (lam > 0).all() else -np.inf
        return q, logl
    def objective(x):
        _, logl = build(x)
        return -logl if np.isfinite(logl) else 1e100
    starts = ((max(ppe_alt, base.mu), base.aT), (.5, base.aT-.5), (.8, base.aT+.5))
    runs = [optimize.minimize(objective, x, method='L-BFGS-B', bounds=((ppe_alt, 1), (-1, 4)),
                              options={'maxiter': maksiter, 'ftol': 1e-11}) for x in starts]
    best = min(runs, key=lambda r: r.fun)
    q, logl = build(best.x)
    return q, {'parametreler': asdict(q), 'logL': logl, 'basari': bool(best.success and np.isfinite(logl)),
               'serbest': ['mu', 'aT', 'olcek(profil)'], 'ppe_mu_alt': ppe_alt,
               'sinirda': [k for k, v, lo, hi in zip(('mu', 'aT'), best.x, (ppe_alt, -1), (1, 4))
                           if min(abs(v-lo), abs(v-hi)) < 1e-5],
               'mesaj': str(best.message), 'n_ayar': len(onhesap.targets)}


def olcum_satiri(ad, bolge, lam, total, taban_lam, taban_total):
    r = bilgi_kazanci(lam, taban_lam, total, taban_total)
    return {'aday': ad, 'bolge': bolge, 'N': r['n'], 'IG': r['ig'], 'SE': r['se'], 'p': r['p'],
            'beklenen_toplam': total, 'taban_beklenen_toplam': taban_total,
            'aralik95': r['aralik95'], 'taban': 'ortak ETAS', 'birim': 'nat/olay'}
