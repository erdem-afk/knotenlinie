"""Skor defteri: olay ve gün dosyaları + koşucunun günlük döngüsü.

Biçim (bütün günlük deneylerde ortak):

Olay dosyası ``<model>__<donem>__olay.csv.gz``: M>=2,95 hedefi başına bir satır,
sütunlar ``zaman, enlem, boylam, mw, hucre, kutu, gun, lam``. ``lam`` o gün, o
hücre ve o büyüklük kutusu için beklenen sayıdır; aynı gün/hücre/kutuda iki olay
varsa iki satır aynı ``lam``'ı taşır.

Gün dosyası ``<model>__<donem>__gun.csv.gz``: gün başına bir satır, sütunlar
``gun, Lam295, Lam395`` (ve M>=4,95 ek satırı için ``Lam495``). Her sütun bütün
hücreler ve o eşiğin üstündeki kutuların günlük toplamıdır.

``log(n!)`` terimi gözlemden gelir, modelden bağımsız; deftere yazılmaz ve
logL farkını etkilemez.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.karsilastir.kosucu import (KESIM, Model, geometri, katalog_kontrol,
                                      olay_kutulari, utc)
from knotenlinie.karsilastir.puan import PuanHatasi

from knotenlinie.yollar import KOSU

KOK = KOSU / 'defter'
OLAY_SUTUN = ['zaman', 'enlem', 'boylam', 'mw', 'hucre', 'kutu', 'gun', 'lam']
GUN_SUTUN = ['gun', 'Lam295', 'Lam395']
# M>=4,95 ek satırı için türev sütun; ortak biçimin üstüne eklenir.
GUN_EK = 'Lam495'
ESIK_SUB = {'Lam295': 'Lam295', 'Lam395': 'Lam395', 'Lam495': 'Lam495'}
M_KENAR = {'Lam295': 2.95, 'Lam395': 3.95, 'Lam495': 4.95}


def alt_indeks(alt):
    """M>=2,95 tabanlı 0,1 kutu indeksi."""
    j = int(round((float(alt) - 2.95) / 0.1))
    if j < 0 or not np.isclose(2.95 + 0.1 * j, alt, atol=1e-9, rtol=0):
        raise PuanHatasi(f'Eşik 2,95 tabanlı 0,1 ızgarada değil: {alt}')
    return j


def alt_sutun(alt):
    key = {2.95: 'Lam295', 3.95: 'Lam395', 4.95: 'Lam495'}.get(round(float(alt), 2))
    if key is None:
        raise PuanHatasi(f'Bilinmeyen eşik sütunu: {alt}')
    return key


@dataclass
class Defter:
    """Bir model ve dönemin defteri; diskten ya da koşudan gelir."""

    ad: str
    olay: pd.DataFrame
    gun: pd.DataFrame
    beklenen: np.ndarray | None = None
    gozlem: np.ndarray | None = None
    logL: float | None = None
    cerceve: tuple | None = None
    ek: dict = field(default_factory=dict)

    @property
    def N(self):
        return int(len(self.olay))

    def lam(self):
        return self.olay['lam'].to_numpy(float)


def _olay_cerceve(hedef, ci, mi, gun, lam):
    d = hedef[['zaman', 'enlem', 'boylam', 'mw']].copy()
    d['hucre'] = np.asarray(ci, int)
    d['kutu'] = np.asarray(mi, int)
    d['gun'] = np.asarray(gun)
    d['lam'] = np.asarray(lam, float)
    d['zaman'] = pd.to_datetime(d['zaman'], utc=True)
    return d[OLAY_SUTUN]


def _gun_cerceve(t0, gun_sayisi, lam_gun):
    """lam_gun: (gün, kutu) beklenen sayı ızgarası → gün dosyası."""
    kenar = np.array([2.95, 3.95, 4.95])
    idx = {k: alt_indeks(k) for k in kenar}
    gunler = [(t0 + pd.Timedelta(days=d)).strftime('%Y-%m-%d') for d in range(gun_sayisi)]
    out = pd.DataFrame({'gun': gunler})
    out['Lam295'] = lam_gun.sum(axis=1)
    out['Lam395'] = lam_gun[:, idx[3.95]:].sum(axis=1)
    out[GUN_EK] = lam_gun[:, idx[4.95]:].sum(axis=1)
    return out


def kos_defter(modeller, baslangic, bitis, katalog, izgara, m_kenarlar, *,
               derinlik=None, bolge=None, ilerleme=None):
    """``kosucu.kos`` ile birebir aynı günlük döngü; her model için defter döner.

    Fark: toplam yerine gün başına büyüklük-kutu integrali (``lam_gun``) ve olay
    başına λ kaydedilir. Böylece doğrusal karışım ve sabit ölçek model yeniden
    koşmadan hesaplanabilir. Dönen ``logL`` koşucununkiyle eşleşmek zorundadır.
    """
    t0, t1 = utc(baslangic), utc(bitis)
    if not t0 < t1 or t1 > KESIM:
        raise PuanHatasi('Geçersiz pencere veya kör pencereye erişim')
    for t in (t0, t1):
        if t != t.normalize():
            raise PuanHatasi('Günlük koşu UTC gece yarısı sınırları ister')
    modeller = list(modeller)
    if not modeller or len({x.ad for x in modeller}) != len(modeller):
        raise PuanHatasi('Modeller boş veya adları tekrarlı')
    if bolge not in (None, 'italya'):
        raise PuanHatasi('Bölge italya veya None olmalı')
    if derinlik is None:
        if any(x.taban_metadata.get('derinlik_acik_gerekli') for x in modeller):
            raise PuanHatasi('Bu tabanla derinlik açıkça verilmeli')
        derinlik = (0.0, 30.0)
    derinlik = tuple(derinlik)
    for model in modeller:
        meta = model.taban_metadata
        if 'derinlik_min' in meta and 'derinlik_max' in meta:
            if derinlik != (meta['derinlik_min'], meta['derinlik_max']):
                raise PuanHatasi(f'{model.ad}: hedef derinliği tabanın integral tanımıyla eşleşmiyor')
    katalog = katalog_kontrol(katalog)
    g, m = geometri(izgara, m_kenarlar)
    shape = (len(g), len(m) - 1)
    if len(m) - 1 < alt_indeks(4.95) + 1:
        raise PuanHatasi('Defter M>=4,95 sütunu için en az 21 kutu ister')
    cerceve = (t0.isoformat(), t1.isoformat(), tuple(derinlik),
               f'M>=2.95-0.1-{len(m) - 1}kutu', bolge)
    hedef = katalog[(katalog.zaman >= t0) & (katalog.zaman < t1)]
    hedef, ci, mi = olay_kutulari(hedef, izgara, m, derinlik)
    gozlem = np.zeros(shape, dtype=int)
    np.add.at(gozlem, (ci, mi), 1)
    gun = ((hedef.zaman - t0) / pd.Timedelta(days=1)).to_numpy(dtype=float).astype(int)
    gun_sayisi = int((t1 - t0) / pd.Timedelta(days=1))
    sonuc = {}
    for model in modeller:
        gecmis_katalog = katalog
        ayar = model.gecmis_ayarlari
        if model.zamana_bagli and ayar is None:
            raise PuanHatasi(f'{model.ad}: dinamik adayın geçmiş filtreleri dondurulmalı')
        if ayar is not None:
            if set(ayar) != {'sinir', 'baslangic_yil', 'derinlik_max'}:
                raise PuanHatasi(f'{model.ad}: geçmiş ayarı sinir/baslangic_yil/derinlik_max ister')
            lo0, lo1, la0, la1 = ayar['sinir']
            yil, dmax = ayar['baslangic_yil'], ayar['derinlik_max']
            if (not np.isfinite([lo0, lo1, la0, la1, yil, dmax]).all() or
                    not -180 <= lo0 < lo1 <= 180 or not -90 <= la0 < la1 <= 90 or
                    int(yil) != yil or not 1 <= yil < 2016 or not 0 < dmax <= 70):
                raise PuanHatasi(f'{model.ad}: geçmiş filtreleri geçersiz (derinlik en çok 70 km)')
            gecmis_katalog = katalog[
                (katalog.zaman >= pd.Timestamp(f'{int(yil):04d}-01-01', tz='UTC')) &
                (katalog.boylam >= lo0) & (katalog.boylam < lo1) &
                (katalog.enlem >= la0) & (katalog.enlem < la1) &
                (katalog.derinlik >= 0) & (katalog.derinlik <= dmax)]

        def tahmin(a, b, _model=model, _gecmis=gecmis_katalog):
            gecmis = _gecmis[_gecmis.zaman < a].copy(deep=True)
            lam = _model.beklenen(a, b, gecmis, izgara.copy(deep=True), m.copy())
            lam = np.asarray(lam, float)
            if lam.shape != shape:
                raise PuanHatasi(f'{_model.ad}: beklenen şekil {shape}, gelen {lam.shape}')
            if not np.isfinite(lam).all() or (lam < 0).any():
                raise PuanHatasi(f'{_model.ad}: beklenen sonlu/negatif değil')
            return lam

        olay_lam = np.empty(len(hedef), float)
        toplam = np.zeros(shape, float)
        lam_gun = np.zeros((gun_sayisi, shape[1]), float)
        ll = 0.0
        sabit = None if model.zamana_bagli else tahmin(t0, t1) / gun_sayisi
        zaman0 = time.monotonic()
        for d in range(gun_sayisi):
            if ilerleme and d and d % ilerleme == 0:
                print(f'  {model.ad}: gün {d}/{gun_sayisi}, {time.monotonic() - zaman0:.0f} s', flush=True)
            a = t0 + pd.Timedelta(days=d)
            lam = tahmin(a, a + pd.Timedelta(days=1)) if sabit is None else sabit
            toplam += lam
            lam_gun[d] = lam.sum(axis=0)
            idx = np.flatnonzero(gun == d)
            ll -= float(lam.sum())
            if len(idx):
                rates = lam[ci[idx], mi[idx]]
                olay_lam[idx] = rates
                if (rates == 0).any():
                    ll = -np.inf
                else:
                    ll += float(np.log(rates).sum())
                _, n = np.unique(ci[idx] * shape[1] + mi[idx], return_counts=True)
                ll -= float(gammaln(n + 1).sum())
        olay_df = _olay_cerceve(hedef, ci, mi, [f'{t0 + pd.Timedelta(days=int(x)):%Y-%m-%d}' for x in gun], olay_lam)
        gun_df = _gun_cerceve(t0, gun_sayisi, lam_gun)
        sonuc[model.ad] = Defter(model.ad, olay_df, gun_df, beklenen=toplam,
                                 gozlem=gozlem.copy(), logL=float(ll), cerceve=cerceve)
    return sonuc


def defter_yaz(defter, dizin=KOK, donem='2011-2015'):
    """Olay ve gün dosyalarını gzip CSV olarak yazar; yolları döner."""
    dizin = Path(dizin)
    dizin.mkdir(parents=True, exist_ok=True)
    olay_yol = dizin / f'{defter.ad}__{donem}__olay.csv.gz'
    gun_yol = dizin / f'{defter.ad}__{donem}__gun.csv.gz'
    o = defter.olay.copy()
    o['zaman'] = pd.to_datetime(o['zaman'], utc=True).dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    o.to_csv(olay_yol, index=False, compression='gzip')
    defter.gun.to_csv(gun_yol, index=False, compression='gzip')
    return olay_yol, gun_yol


def defter_oku(ad, dizin=KOK, donem='2011-2015'):
    """Diskteki defteri okur; sütun/biçim kapıları burada kapanır."""
    dizin = Path(dizin)
    olay_yol = dizin / f'{ad}__{donem}__olay.csv.gz'
    gun_yol = dizin / f'{ad}__{donem}__gun.csv.gz'
    for yol in (olay_yol, gun_yol):
        if not yol.exists():
            raise PuanHatasi(f'Defter yok: {yol}')
    o = pd.read_csv(olay_yol)
    if list(o.columns) != OLAY_SUTUN:
        raise PuanHatasi(f'Olay sütunları beklenenden farklı: {list(o.columns)}')
    o['zaman'] = pd.to_datetime(o['zaman'], utc=True, format='mixed')
    if o['zaman'].isna().any() or (o['zaman'] >= KESIM).any():
        raise PuanHatasi('Olay defterinde 2016+ veya eksik zaman')
    for k in ('enlem', 'boylam', 'mw', 'lam'):
        o[k] = pd.to_numeric(o[k], errors='raise').astype(float)
    for k in ('hucre', 'kutu'):
        if not np.issubdtype(o[k].dtype, np.integer):
            o[k] = o[k].astype(int)
    o['gun'] = o['gun'].astype(str)
    if not np.isfinite(o[['enlem', 'boylam', 'mw', 'lam']].to_numpy()).all() or (o['lam'] <= 0).any():
        raise PuanHatasi('Olay defteri sonlu/pozitif λ istiyor')
    g = pd.read_csv(gun_yol)
    sayisal = ['Lam295', 'Lam395', GUN_EK]
    for k in sayisal:
        if k not in g.columns:
            raise PuanHatasi(f'Gün dosyasında {k} yok')
        g[k] = pd.to_numeric(g[k], errors='raise').astype(float)
    if not np.isfinite(g[sayisal].to_numpy()).all() or (g[sayisal].to_numpy() < 0).any():
        raise PuanHatasi('Gün defteri sonlu/negatif değil')
    g['gun'] = g['gun'].astype(str)
    return Defter(ad, o, g)


def olcek_uzat(satir, alt):
    """Defter satırının λ değerini verilen M eşiğine indirger (günlük toplam)."""
    if alt == 2.95:
        return satir['Lam295']
    if alt == 3.95:
        return satir['Lam395']
    if alt == 4.95:
        return satir['Lam495']
    raise PuanHatasi(f'Eşik desteklenmiyor: {alt}')
