"""Dondurulmuş düz ETAS'ın ortak beklenen(...) arayüzü; gerçek hücre integralleri."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.etas import model as M
from .ayar import dallanma
from .veri import VERI, IZGARA, izgara_dogrula, katalog_dogrula, sha256


def utc(zaman):
    t = pd.Timestamp(zaman)
    if t.tzinfo is None or pd.isna(t):
        raise ValueError('UTC/tz-aware zaman gerekli')
    return t.tz_convert('UTC')


def omori_kutle(alt, ust, c, p):
    """∫alt^ust (t+c)^-p dt; eski anne/çok kısa pencere için kararlı fark."""
    a, b = np.asarray(alt, float), np.asarray(ust, float)
    if (a < 0).any() or (b < a).any() or not (c > 0 and p > 1):
        raise ValueError('Omori aralığı/parametresi geçersiz')
    return (a + c) ** (1 - p) * (-np.expm1((1 - p) * np.log1p((b - a) / (a + c)))) / (p - 1)


class DuzETAS:
    """Bir bölgenin donmuş ETAS'ı; KDE'nin parça-sabit hücre integralleri.

    Dış tetikleme kütlesi kayıptır; tekrar normalize edilmez. Düzgün zemin
    kayıttaki açık karışımdır, gizli floor değildir. Geçmiş kapısı ≤2015.
    """
    def __init__(self, parametreler, izgara):
        self.p = dict(parametreler)
        self.th = dict(self.p['parametreler'])
        self.mc, self.b = float(self.p['mc']), float(self.p['b']['deger'])
        self.kutu = tuple(self.p['kutu'])
        self.met = M.uzay_parametre_kontrol(self.p, self.kutu)
        self.izgara = izgara[IZGARA].copy().reset_index(drop=True)
        g, _, _, _ = izgara_dogrula(self.izgara)
        la0, la1, lo0, lo1 = self.kutu
        if ((g[:, 0] < lo0 - 1e-9) | (g[:, 1] > lo1 + 1e-9) |
            (g[:, 2] < la0 - 1e-9) | (g[:, 3] > la1 + 1e-9)).any():
            raise ValueError('Hedef hücre ayar kutusu dışında')
        vals = np.array([self.th[k] for k in M.UZAY_ADLARI], float)
        if not np.isfinite(vals).all() or self.th['mu'] < 0 or self.th['K'] < 0 or not (
            self.th['c'] > 0 and self.th['p'] > 1 and self.th['D'] > 0 and self.th['q'] > 1):
            raise ValueError('ETAS parametre kapısı')
        if not np.isfinite(self.mc) or not dallanma(self.th, self.b) < 1:
            raise ValueError('ETAS alt-kritik değil (alpha<b, kesilmemiş GR)')
        self.baslangic = utc(self.p['ayar_baslangic'])
        self.ayar_son = utc(self.p.get('ayar_bitis', self.p['ayar_baslangic']))
        self.hist = {k: np.asarray(self.p['arka_plan'][k], float)
                     for k in ('x_kenar', 'y_kenar', 'yogunluk')}
        xe, ye, density = self.hist['x_kenar'], self.hist['y_kenar'], self.hist['yogunluk']
        if density.shape != (len(xe) - 1, len(ye) - 1) or not np.isfinite(density).all() or (density < 0).any():
            raise ValueError('Arka plan histogramı geçersiz')
        if (np.diff(xe) <= 0).any() or (np.diff(ye) <= 0).any():
            raise ValueError('Histogram kenarları artan değil')
        mass = np.sum(density * np.diff(xe)[:, None] * np.diff(ye)[None, :])
        if not np.isclose(mass, 1, atol=1e-8, rtol=0):
            raise ValueError('Arka plan histogramı birim kütle değil')
        self._support = set(map(tuple, np.round(g, 9)))
        self._grid_key = None
        self._background_key = None
        self._background = None
        self._keys = []
        self._spatial = np.empty((0, 0))

    def _arka_plan(self, grid):
        key = grid.tobytes()
        if self._background_key == key:
            return self._background
        xe, ye, density = self.hist['x_kenar'], self.hist['y_kenar'], self.hist['yogunluk']
        wx = np.maximum(0, np.minimum(grid[:, 1, None], xe[None, 1:]) -
                        np.maximum(grid[:, 0, None], xe[None, :-1]))
        wy = np.maximum(0, np.minimum(grid[:, 3, None], ye[None, 1:]) -
                        np.maximum(grid[:, 2, None], ye[None, :-1]))
        self._background = np.einsum('ij,ij->i', wx @ density, wy)
        self._background_key = key
        return self._background

    def _mekan(self, history, grid):
        key = grid.tobytes()
        keys = list(map(tuple, history[['zaman', 'boylam', 'enlem', 'mw']].to_numpy()))
        if key != self._grid_key or keys[:len(self._keys)] != self._keys:
            self._keys = []
            self._spatial = np.empty((0, len(grid)))
            self._grid_key = key
        new = history.iloc[len(self._keys):]
        if len(new):
            # Her yeni anne için vstack eski 300+ MB matrisi kopyalıyordu;
            # allocator/BLAS çalışma alanları yerel makinede 15.6 GB RSS'ye çıktı.
            # İki katlı kapasite ve doğrudan satıra yazma: O(N*hücre) kalıcı alan.
            if len(keys) > self._spatial.shape[0]:
                capacity = max(16, 1 << (len(keys) - 1).bit_length())
                grown = np.empty((capacity, len(grid)))
                grown[:len(self._keys)] = self._spatial[:len(self._keys)]
                self._spatial = grown
            # Tam kutuda paylaşılan kenarlar, blok=1: varsayılan blok=64 yerel makinede GB'lar tutar.
            _, _, size, _ = izgara_dogrula(pd.DataFrame(grid, columns=IZGARA))
            dx = size[0]
            if not np.isclose(dx, size[1], atol=1e-9, rtol=0):
                raise ValueError('ETAS hücre integrali kare derece hücre ister')
            xe, ye = M.hucre_kenarlari(self.kutu, dx)
            ix = np.rint((grid[:, 0] - xe[0]) / dx).astype(int)
            iy = np.rint((grid[:, 2] - ye[0]) / dx).astype(int)
            if (ix < 0).any() or (iy < 0).any() or (ix >= len(xe) - 1).any() or (iy >= len(ye) - 1).any():
                raise ValueError('Hedef ayar kutusunda hizalı değil')
            if not np.allclose(grid, np.column_stack([xe[ix], xe[ix + 1], ye[iy], ye[iy + 1]]), atol=1e-8, rtol=0):
                raise ValueError('Hedef ayar kutusunda hizalı değil')
            first = len(self._keys)
            for j, (_, row) in enumerate(new.iterrows()):
                Di = M.mekan_olcegi(self.th['D'], self.th['gamma'], [row['mw']], self.mc)
                full = M.mekan_hucre_integralleri([row['boylam']], [row['enlem']], Di, self.th['q'],
                                                 self.kutu, dx, metrik=self.met, blok=1)
                self._spatial[first + j] = full[0, iy, ix]
            self._keys = keys
        return self._spatial[:len(keys)]

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        """Sabit H_bas ile doğrudan ETAS oran integrali, hücre × büyüklük."""
        a, z = utc(baslangic), utc(bitis)
        if z <= a or a < self.ayar_son:
            raise ValueError('Tahmin aralığı ayar bitişinden sonra ve artan olmalı')
        history = katalog_dogrula(gecmis)
        if (history['zaman'] >= a).any():
            raise ValueError('Geçmiş geleceği/başlangıç anını içeriyor')
        grid, _, _, _ = izgara_dogrula(izgara)
        if not all(tuple(row) in self._support for row in np.round(grid, 9)):
            raise ValueError('Hedef hücre ayar desteğinde yok')
        edges = np.asarray(m_kenarlar, float)
        if edges.ndim != 1 or len(edges) < 2 or not np.isfinite(edges[:-1]).all() or np.isnan(edges[-1]) or (
            np.diff(edges) <= 0).any() or edges[0] < self.mc:
            raise ValueError('Büyüklük kutuları artan ve Mc üstünde olmalı (son kenar +inf olabilir)')
        duration = float((z - a) / pd.Timedelta(days=1))
        cell = self.th['mu'] * duration * self._arka_plan(grid)
        h = history[(history['mw'] >= self.mc) & (history['zaman'] >= self.baslangic)].reset_index(drop=True)
        if len(h) and self.th['K'] > 0:
            age = ((a - h['zaman']) / pd.Timedelta(days=1)).to_numpy(float)
            weights = (self.th['K'] * 10 ** (self.th['alpha'] * (h['mw'].to_numpy(float) - self.mc)) *
                       omori_kutle(age, age + duration, self.th['c'], self.th['p']))
            # BLAS'ın değişen N için büyük geçici paketlerini tutma;
            # optimize=False einsum doğrudan C-satırlarını biriktirir.
            cell = cell + np.einsum('i,ij->j', weights, self._mekan(h, grid), optimize=False)
        mag = 10 ** (-self.b * (edges[:-1] - self.mc)) - 10 ** (-self.b * (edges[1:] - self.mc))
        out = cell[:, None] * mag[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise ValueError('Beklenen sonlu/negatif olmayan değil')
        return out


def model_yukle(bolge, ortak=VERI / 'ortak', *, son='2011-01-01'):
    ortak = Path(ortak)
    end = pd.Timestamp(son)
    end = end.tz_localize('UTC') if end.tzinfo is None else utc(end)
    if end not in (pd.Timestamp('2006-01-01', tz='UTC'), pd.Timestamp('2011-01-01', tz='UTC')):
        raise ValueError('Yalnız 2006/2011 ayar sonu desteklenir')
    p = json.loads((ortak / f'etas_{bolge}_le{end.year - 1}.json').read_text())
    if utc(p['ayar_bitis']) != end or utc(p['ayar_max_zaman']) >= end:
        raise ValueError('Parametre ayar sonu uyuşmuyor')
    path = ortak / f'{bolge}_izgara.csv'
    if sha256(path) != p['izgara_sha256']:
        raise ValueError('Izgara SHA256 parametre kaydıyla uyuşmuyor')
    return DuzETAS(p, pd.read_csv(path))


class AyarTabani:
    """Sonu açıkça seçilen, ızgaradan bölge bulan ortak arayüz."""
    def __init__(self, son, ortak):
        self.son, self.ortak = son, ortak
        self.modeller = {}

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        target = set(map(tuple, np.round(izgara[IZGARA].to_numpy(float), 9)))
        candidates = []
        for name in ('italya',):
            if name not in self.modeller:
                self.modeller[name] = model_yukle(name, self.ortak, son=self.son)
            model = self.modeller[name]
            if target and target <= model._support:
                candidates.append(model)
        if len(candidates) != 1:
            raise ValueError('Hedef ızgaranın tek bir ortak ETAS bölgesi olmalı')
        return candidates[0].beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)


def ayar_tabani(bolge=None, ortak=VERI / 'ortak', *, son='2006-01-01'):
    """2006–2010 ağırlık ayarı için son=2006; doğrulama için son=2011.

    Bölge verilmezse aynı beklenen imzalı bölge-seçici döner.
    """
    return (AyarTabani(son, ortak) if bolge is None else model_yukle(bolge, ortak, son=son))


_MODELLER = {}


def beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar):
    """Ortak imza; tam/alt ızgaradan bölgeyi bulur, belirsizliği reddeder.

    Tekrarlı çağrıda nesne ve anne-hücre integralleri tutulur. Açık bölge seçimi
    isteyen koşucu model_yukle('italya').beklenen kullanabilir.
    """
    target = set(map(tuple, np.round(izgara[IZGARA].to_numpy(float), 9)))
    candidates = []
    for name in ('italya',):
        if name not in _MODELLER:
            _MODELLER[name] = model_yukle(name)
        model = _MODELLER[name]
        support = set(map(tuple, np.round(model.izgara.to_numpy(float), 9)))
        if target and target <= support:
            candidates.append(model)
    if len(candidates) != 1:
        raise ValueError('Hedef ızgaranın tek bir ortak ETAS bölgesi olmalı')
    return candidates[0].beklenen(baslangic, bitis, gecmis, izgara, m_kenarlar)
