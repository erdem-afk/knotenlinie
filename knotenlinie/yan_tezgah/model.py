"""D0/D1/D2/D3 modelleri: ayar (MLE) ve ortak `beklenen` arayüzü.

D0 düz ETAS (tek Mc = hedef eşiği), D1 dönem Mc(t)'li R-tipi MLE,
D2 = D1 + HKJ kısa süreli tamlık, D3 = D0/D1/D2'nin ağırlıklı doğrusal
karışımı (ağırlıklar 2006–2010'da seçilir). Zaman gün, uzunluk km.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import pandas as pd

from knotenlinie.etas import model as M
from . import kesme as K
from . import mle as ML
from .okuyucu import KESIM, cerceve_dogrula, izgara as izgara_yap, tamlik as tamlik_hesap

GUN = pd.Timedelta(days=1)


def _utc(x):
    t = pd.Timestamp(x)
    return t.tz_convert('UTC') if t.tzinfo is not None else t.tz_localize('UTC')


def _yil_gun(yil, epoch):
    return float((_utc(f'{int(yil)}-01-01T00:00:00Z') - epoch) / GUN)


def _birlestir(araliklar, T):
    araliklar = sorted(tuple(x) for x in araliklar)
    out = []
    for a, b, s in araliklar:
        if b <= a:
            continue
        if out and abs(out[-1][1] - a) < 1e-9 and abs(out[-1][2] - s) < 1e-15:
            out[-1][1] = b
        else:
            out.append([a, b, s])
    if out[0][0] > 1e-9:
        out.insert(0, [0.0, out[0][0], out[0][2]])
    if out[-1][1] < T - 1e-9:
        out.append([out[-1][1], T, out[-1][2]])
    return [(float(a), float(b), float(s)) for a, b, s in out]


def _araliklar_donem(tm, mc0, b, epoch, T):
    out = []
    for p in tm['pencereler']:
        a = max(_yil_gun(p['bas_yil'], epoch), 0.0)
        b_ = min(_yil_gun(p['bit_yil'], epoch), T)
        if b_ > a:
            out.append((a, b_, 10 ** (-b * (p['mc'] - mc0))))
    return _birlestir(out, T)


def _mcd_nokta(tm, t_gun, buyuk_t, buyuk_m, m_buyuk, hkj_gun, epoch, hedef=None):
    y = (_utc(epoch) + pd.Timedelta(days=float(t_gun))).year
    mc = float(tm['en_buyuk'])
    for p in tm['pencereler']:
        if p['bas_yil'] <= y < p['bit_yil']:
            mc = float(p['mc'])
            break
    if hedef is not None:
        mc = max(mc, float(hedef))
    if buyuk_t.size:
        sec = (buyuk_t < t_gun) & (buyuk_t > t_gun - hkj_gun)
        if sec.any():
            dtj = t_gun - buyuk_t[sec]
            hkj = float(np.max(buyuk_m[sec] - 4.5 - 0.75 * np.log10(np.maximum(dtj, 1e-6))))
            mc = max(mc, hkj)
    return mc


def _araliklar_hkj(tm, fit, mc0, b, epoch, T, m_buyuk, hkj_gun, kaba, hedef):
    kes = [0.0, float(T)]
    for p in tm['pencereler']:
        kes += [_yil_gun(p['bas_yil'], epoch), _yil_gun(p['bit_yil'], epoch)]
    buyuk = fit[fit.mw >= m_buyuk]
    buyuk_t = ((buyuk.zaman - epoch) / GUN).to_numpy(float)
    buyuk_m = buyuk.mw.to_numpy(float)
    for tb in buyuk_t:
        kes += [float(tb), float(tb + hkj_gun)]
    kes = np.unique(np.clip(np.round(np.sort(np.array(kes, float)) / kaba) * kaba, 0, T))
    out = []
    for a, bb in zip(kes[:-1], kes[1:]):
        mid = 0.5 * (a + bb)
        # KURAL.md: s(t)=10^{-b(max(Mc_dönem, Mc_sonra)-Mc0)}; hedef tabanı YOK (olay terimi
        # mc95 kullanır, kompansatör aynı tespit eşiğini görmeli). 2026-10-12 Y2 düzeltmesi.
        mcd = _mcd_nokta(tm, mid, buyuk_t, buyuk_m, m_buyuk, hkj_gun, epoch, None)
        out.append((float(a), float(bb), 10 ** (-b * (mcd - mc0))))
    return _birlestir(out, T)


def _taban_kirp(tm, taban):
    """Küçük ölçek denemesi için Mc tabanını yükseltir; hepsi tutarlı kırpılır."""
    tm = dict(tm)
    tm['pencereler'] = [dict(p, mc=max(float(p['mc']), taban)) for p in tm['pencereler']]
    tm['donem_mc'] = np.maximum(tm['donem_mc'], taban)
    tm['mc95'] = np.maximum(tm['mc95'], taban)
    tm['mc_min'] = max(float(tm['mc_min']), taban)
    tm['en_buyuk'] = max(float(tm['en_buyuk']), taban)
    tm['hedef'] = max(float(tm['hedef']), taban)
    return tm


_BOLGE_KUTU = None


def kutu(bolge):
    from .indir import BOLGELER
    return BOLGELER[bolge]['kutu']


def kur(df, bolge, *, ayar_son='2011-01-01T00:00:00Z', hedef=None, varyant='D1',
        hkj=True, m_buyuk=5.0, hkj_gun=30.0, bas_yil=None, maks_cift=20_000_000,
        maksiter=400, aralik_kaba=1.0, taban_mc=None, rmax_km=None, tmax_gun=None):
    """Bir varyantı ≤ayar_son verisiyle ayarlar; `YanModel` döndürür."""
    kes = K.parametreler(bolge, rmax_km=rmax_km, tmax_gun=tmax_gun)
    df = cerceve_dogrula(df)
    son = _utc(ayar_son)
    fit = df[df.zaman < son].reset_index(drop=True)
    if not len(fit):
        raise ValueError('ayar penceresinde olay yok')
    if bas_yil is None:
        bas_yil = int(fit.zaman.dt.year.min())
    tm = tamlik_hesap(fit, bas_yil, int(fit.zaman.dt.year.max()), hkj=hkj,
                      m_buyuk=m_buyuk, gun=hkj_gun)
    if taban_mc is not None:
        tm = _taban_kirp(tm, float(taban_mc))
    if hedef is None:
        hedef = float(tm['hedef'])
    epoch = _utc(fit.zaman.min())
    T = float((son - epoch) / GUN)
    t = ((fit.zaman - epoch) / GUN).to_numpy(float)
    m_all = fit.mw.to_numpy(float)
    if varyant == 'D0':
        mc0 = float(tm['mc_min']) if taban_mc is not None else float(hedef)
        hedef = max(float(hedef), float(tm['en_buyuk']))
        mc_olay = np.full(len(fit), hedef)
        kullan = m_all >= hedef - 1e-9
    elif varyant in ('D1', 'D2'):
        mc0 = float(tm['mc_min'])
        mc_olay = tm['donem_mc'] if varyant == 'D1' else tm['mc95']
        kullan = m_all >= mc_olay - 1e-9
    else:
        raise ValueError('varyant D0/D1/D2 olmalı')
    b = ML.b_ayarla(m_all[kullan], mc_olay[kullan])
    bd = float(b['deger'])
    if varyant == 'D0':
        araliklar = [(0.0, T, 1.0)]
    elif varyant == 'D1':
        araliklar = _araliklar_donem(tm, mc0, bd, epoch, T)
    else:
        araliklar = _araliklar_hkj(tm, fit, mc0, bd, epoch, T, m_buyuk, hkj_gun,
                                   aralik_kaba, hedef)
    grid = izgara_yap(bolge)
    L = ML.Olabilirlik(t[kullan], m_all[kullan], fit.boylam.to_numpy(float)[kullan],
                       fit.enlem.to_numpy(float)[kullan], bd, T, mc0, mc_olay[kullan],
                       araliklar, grid, kutu(bolge), maks_cift=int(maks_cift),
                       rmax_km=kes['rmax_km'], tmax_gun=kes['tmax_gun'])
    fitmeta = ML.ayarla(L, 'ortak', maksiter=int(maksiter))
    fitmeta['kesme'] = kes
    return YanModel(ad=varyant, p=fitmeta, mc0=mc0, b=bd, hedef=float(hedef), bolge=bolge,
                    donem_mc=tm['pencereler'], hkj=(varyant == 'D2'), m_buyuk=m_buyuk,
                    hkj_gun=hkj_gun, epoch=epoch, rmax_km=kes['rmax_km'], tmax_gun=kes['tmax_gun'],
                    bilgi=dict(pencereler=tm['pencereler'], b=b, ayar_son=son.isoformat(),
                               n_fit=int(kullan.sum()), kutu=list(kutu(bolge)), mc0=mc0,
                               hedef=float(hedef), mc_min=float(tm['mc_min']),
                               en_buyuk=float(tm['en_buyuk']), bas_yil=int(bas_yil),
                               aralik_sayisi=len(araliklar), kesme=kes))


def _hizli_dogrula(df):
    """`cerceve_dogrula` ile aynı kapılar; sıralı, UTC ve temizse kopyasız geçer."""
    s = ['zaman', 'enlem', 'boylam', 'derinlik', 'mw']
    z = df['zaman']
    if (str(z.dtype).startswith('datetime64') and getattr(z.dt, 'tz', None) is not None and
            z.is_monotonic_increasing and not z.isna().any() and z.iloc[-1] < KESIM and
            np.isfinite(df[['enlem', 'boylam', 'derinlik', 'mw']].to_numpy(float)).all()):
        return df[s].reset_index(drop=True)
    return cerceve_dogrula(df)


class YanModel:
    """Ayarı dondurulmuş bir varyant; ortak `beklenen` imzası."""

    def __init__(self, ad, p, mc0, b, hedef, bolge, donem_mc, hkj, m_buyuk, hkj_gun,
                 epoch, bilgi=None, dx=0.1, rmax_km=None, tmax_gun=None):
        self.ad = ad
        self.p = dict(p)
        self.th = dict(p['parametreler'])
        self.mc0, self.b, self.hedef = float(mc0), float(b), float(hedef)
        self.bolge = bolge
        self.kutu = tuple(kutu(bolge))
        self.donem_mc = donem_mc
        self.hkj, self.m_buyuk, self.hkj_gun = bool(hkj), float(m_buyuk), float(hkj_gun)
        self.epoch = _utc(epoch)
        self.dx = float(dx)
        self.rmax_km = None if rmax_km is None else float(rmax_km)
        self.tmax_gun = None if tmax_gun is None else float(tmax_gun)
        self.metadata = dict(bilgi or {})
        self._grid_key = None
        self._pk = np.empty((0, 4))
        self._sifirla_onbellek()
        self._mekan_met = M.yerel_metrik(self.kutu)

    def mc_det(self, zaman, gecmis):
        y = pd.Timestamp(zaman).year
        mc = float(self.hedef)
        for p in self.donem_mc:
            if p['bas_yil'] <= y < p['bit_yil']:
                mc = max(mc, float(p['mc']))
                break
        if self.hkj and gecmis is not None and len(gecmis):
            z0 = pd.Timestamp(zaman)
            i0 = int(gecmis.zaman.searchsorted(z0 - pd.Timedelta(days=self.hkj_gun) - pd.Timedelta(seconds=1)))
            gecmis = gecmis.iloc[i0:]  # yalnız son hkj_gun günü (zamana göre sıralı)
            t = ((gecmis.zaman - z0) / GUN).to_numpy(float)
            m = gecmis.mw.to_numpy(float)
            sec = (m >= self.m_buyuk) & (t < 0) & (t > -self.hkj_gun)
            if sec.any():
                dtj = -t[sec]
                mc = max(mc, float(np.max(m[sec] - 4.5 - 0.75 * np.log10(np.maximum(dtj, 1e-6)))))
        return mc

    def _sifirla_onbellek(self):
        self._pk = np.empty((0, 4))
        self._ip = np.zeros(1024, np.int64)   # indptr (kapasiteli)
        self._fi = np.empty(1 << 20, np.int32)  # düz hücre indeksleri
        self._fv = np.empty(1 << 20)           # düz integral değerleri
        self._nnz = 0

    def _ekle(self, k, rows, vals):
        m = len(rows)
        if self._nnz + m > len(self._fi):
            cap = max(int(1.3 * len(self._fi)), self._nnz + m)
            self._fi = np.resize(self._fi, cap)
            self._fv = np.resize(self._fv, cap)
        if k + 2 > len(self._ip):
            self._ip = np.resize(self._ip, 2 * len(self._ip))
        self._fi[self._nnz:self._nnz + m] = rows
        self._fv[self._nnz:self._nnz + m] = vals
        self._nnz += m
        self._ip[k + 1] = self._nnz

    def _kutu_ara(self, lon, lat, lo_k, la_k):
        """Ebeveynin rmax disklerini kapsayan hücre-indeks kutusu (tam kutu: rmax yok)."""
        nla, nlo = len(la_k) - 1, len(lo_k) - 1
        if self.rmax_km is None:
            return 0, nla, 0, nlo
        dla = self.rmax_km / 100.0 + self.dx
        dlo = self.rmax_km / (100.0 * np.cos(np.radians(min(89.0, abs(lat) + dla)))) + self.dx
        ix0 = int(np.searchsorted(lo_k, lon - dlo, side='right')) - 1
        ix1 = int(np.searchsorted(lo_k, lon + dlo, side='left'))
        iy0 = int(np.searchsorted(la_k, lat - dla, side='right')) - 1
        iy1 = int(np.searchsorted(la_k, lat + dla, side='left'))
        return max(iy0, 0), min(iy1, nla), max(ix0, 0), min(ix1, nlo)

    def _mekan(self, history, grid):
        """Ebeveyn × hücre seyrek integral matrisi (CSR, satır = history sırası).

        Disk dışı hücreler tam sıfırdır, yalnız rmax kutusu hesaplanır ve saklanır.
        Önbellek ebeveyn dizisinin öneki olduğu sürece yeniden kullanılır (D3 aynı
        modelleri yeniden koşarken yeniden hesaplamaz).
        """
        key = grid[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float).tobytes()
        pk = np.column_stack([history.zaman.astype('int64').to_numpy(), history.boylam.to_numpy(float),
                              history.enlem.to_numpy(float), history.mw.to_numpy(float)])
        n_c = len(self._pk)
        if key != self._grid_key or n_c > len(pk) and not np.array_equal(pk, self._pk[:len(pk)]) \
                or n_c <= len(pk) and not np.array_equal(pk[:n_c], self._pk):
            self._grid_key = key
            self._sifirla_onbellek()
            n_c = 0
        n = len(pk)
        if n > n_c:
            xe, ye = M.hucre_kenarlari(self.kutu, self.dx)
            ix = np.rint((grid.boylam_min.to_numpy(float) - xe[0]) / self.dx).astype(int)
            iy = np.rint((grid.enlem_min.to_numpy(float) - ye[0]) / self.dx).astype(int)
            if (ix < 0).any() or (iy < 0).any() or (ix >= len(xe) - 1).any() or (iy >= len(ye) - 1).any():
                raise ValueError('hedef hücre kutu ızgarasına hizalı değil')
            hid = np.full((len(ye) - 1, len(xe) - 1), -1, np.int64)
            hid[iy, ix] = np.arange(len(grid))
            for k in range(n_c, n):
                lon, lat, mw = pk[k, 1], pk[k, 2], pk[k, 3]
                iy0, iy1, ix0, ix1 = self._kutu_ara(lon, lat, xe, ye)
                Di = M.mekan_olcegi(self.th['D'], self.th['gamma'], [mw], self.mc0)
                alt = (ye[iy0], ye[iy1], xe[ix0], xe[ix1])
                if iy1 > iy0 and ix1 > ix0:
                    full = K.kesik_hucre_integralleri([lon], [lat], Di, self.th['q'], alt, self.dx,
                                                      metrik=self._mekan_met, blok=1,
                                                      rmax_km=self.rmax_km)[0]
                    rows = hid[iy0:iy1, ix0:ix1]
                    tut = (rows >= 0) & (full > 1e-12)  # disk dışı sayısal gürültü saklanmaz
                    self._ekle(k, rows[tut], full[tut])
                else:
                    self._ekle(k, np.empty(0, np.int32), np.empty(0))
            self._pk = pk
        return n

    def _matris(self, lo, n, ncell):
        """CSR alt matrisi: satırlar [lo, n)."""
        ip = self._ip
        a, z = ip[lo], ip[n]
        return sp.csr_matrix((self._fv[a:z], self._fi[a:z], ip[lo:n + 1] - a), shape=(n - lo, ncell))

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = _utc(baslangic), _utc(bitis)
        if not a < z:
            raise ValueError('boş tahmin aralığı')
        grid = izgara[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].reset_index(drop=True)
        edges = np.asarray(m_kenarlar, float)
        if len(gecmis):
            history = _hizli_dogrula(gecmis)
        else:
            history = pd.DataFrame(dict(zaman=pd.Series([], dtype='datetime64[ns, UTC]'),
                                        enlem=[], boylam=[], derinlik=[], mw=[]))
        history = history[(history.zaman < a) & (history.mw >= self.mc0)].reset_index(drop=True)
        duration = float((z - a) / GUN)
        la0, la1, lo0, lo1 = self.kutu
        alan = (la1 - la0) * (lo1 - lo0)
        hucre = ((grid.boylam_max - grid.boylam_min) * (grid.enlem_max - grid.enlem_min)).to_numpy(float)
        cell = self.th['mu'] * duration * hucre / alan
        if len(history) and self.th['K'] > 0:
            age = ((a - history.zaman) / GUN).to_numpy(float)
            if self.tmax_gun is None:
                om = (M._omori_ilke(age + duration, self.th['c'], self.th['p'])[0] -
                      M._omori_ilke(age, self.th['c'], self.th['p'])[0])
            else:
                ust = np.minimum(age + duration, self.tmax_gun)
                om = np.where(age < self.tmax_gun,
                              M._omori_ilke(ust, self.th['c'], self.th['p'])[0] -
                              M._omori_ilke(age, self.th['c'], self.th['p'])[0], 0.0)
            w = (self.th['K'] * 10 ** (self.th['alpha'] * (history.mw.to_numpy(float) - self.mc0)) * om)
            n_h = self._mekan(history, grid)
            lo = 0 if self.tmax_gun is None else int(np.searchsorted(age[::-1], self.tmax_gun, side='left'))
            lo = 0 if self.tmax_gun is None else n_h - lo
            cell = cell + self._matris(lo, n_h, len(grid)).T @ w[lo:]
        mcd = self.mc_det(a, history)
        m1 = np.maximum(edges[:-1], mcd)
        m2 = np.maximum(edges[1:], mcd)
        alt = 10 ** (-self.b * (m1 - self.mc0))
        ust = np.where(np.isinf(m2), 0.0, 10 ** (-self.b * (m2 - self.mc0)))
        wmag = alt - ust
        out = cell[:, None] * wmag[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise ValueError('beklenen sonlu/negatif değil')
        return out


class Karisim:
    """D3: ağırlıklı doğrusal karışım; `beklenen` ağırlıklı toplamı verir."""

    def __init__(self, ad, modeller, agirliklar):
        if len(modeller) != len(agirliklar) or abs(sum(agirliklar) - 1) > 1e-9:
            raise ValueError('karışım ağırlıkları olasılık olmalı')
        if any(w < 0 for w in agirliklar):
            raise ValueError('negatif ağırlık yok')
        self.ad = ad
        self.modeller = list(modeller)
        self.agirliklar = [float(w) for w in agirliklar]
        self.metadata = dict(karisim=[m.ad for m in modeller], agirliklar=self.agirliklar)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        return sum(w * m.beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
                   for w, m in zip(self.agirliklar, self.modeller))
