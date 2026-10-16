"""Geçmişi gün başında kesen, ortak günlük kutularda karşılaştırma."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Callable

import numpy as np
import pandas as pd
from scipy.special import gammaln

from .puan import PuanHatasi, oranlar, eslestirilmis, tutarlilik

SUTUNLAR = ['zaman', 'enlem', 'boylam', 'derinlik', 'mw']
IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']
KESIM = pd.Timestamp('2016-01-01', tz='UTC')


def utc(x):
    t = pd.Timestamp(x)
    if t.tzinfo is None:
        raise PuanHatasi('Zaman açıkça UTC/ofset taşımalı')
    return t.tz_convert('UTC')


def geometri(izgara, m_kenarlar):
    """Yarı açık hücreler; çakışma yok, son büyüklük kenarı +inf olabilir."""
    g = np.round(izgara[IZGARA].to_numpy(dtype=float), 12)
    m = np.asarray(m_kenarlar, float)
    if not len(g) or not np.isfinite(g).all() or (g[:, 0] >= g[:, 1]).any() or (g[:, 2] >= g[:, 3]).any():
        raise PuanHatasi('Izgara hücreleri geçersiz')
    if ((g[:, :2] < -180) | (g[:, :2] > 180)).any() or ((g[:, 2:] < -90) | (g[:, 2:] > 90)).any():
        raise PuanHatasi('Izgara coğrafi sınırların dışında')
    if m.ndim != 1 or len(m) < 2 or not np.isfinite(m[:-1]).all() or np.isnan(m[-1]) or (np.diff(m) <= 0).any():
        raise PuanHatasi('Büyüklük kenarları artan olmalı')
    # Enlem taraması: ulusal 0.1 derece ızgarasında yalnız aynı şerit aktiftir.
    aktif = []
    for i in np.argsort(g[:, 2]):
        aktif = [j for j in aktif if g[j, 3] > g[i, 2]]
        if any(g[j, 0] < g[i, 1] and g[i, 0] < g[j, 1] for j in aktif):
            raise PuanHatasi('Izgara hücreleri çakışıyor')
        aktif.append(i)
    return g, m


def katalog_kontrol(katalog):
    """Bu sürüm yalnız mühür öncesi/iç doğrulama verisi kabul eder."""
    k = katalog[SUTUNLAR].copy()
    # Hedefin tamamı doğrulanır; ardından filtrelemek sızıntıyı meşrulaştırmaz.
    k['zaman'] = pd.to_datetime(k['zaman'], utc=True)
    if k['zaman'].isna().any() or (k['zaman'] >= KESIM).any():
        raise PuanHatasi('2016+ veya eksik zaman: kör pencere kapalı')
    x = k[['enlem', 'boylam', 'derinlik', 'mw']].to_numpy(dtype=float)
    if not np.isfinite(x).all() or (np.abs(x[:, 0]) > 90).any() or (np.abs(x[:, 1]) > 180).any():
        raise PuanHatasi('Eksik/geçersiz katalog koordinatı, derinlik veya Mw')
    return k.sort_values('zaman', kind='stable').reset_index(drop=True)


def olay_kutulari(olaylar, izgara, m_kenarlar, derinlik=(0.0, 30.0)):
    """Bölge/M/derinlik dışını saymaz; her üst kenar dışarıdadır."""
    g, m = geometri(izgara, m_kenarlar)
    lo, hi = derinlik
    if not np.isfinite([lo, hi]).all() or lo >= hi:
        raise PuanHatasi('Derinlik aralığı geçersiz')
    sec, cidx, midx = [], [], []
    for i, row in enumerate(olaylar.itertuples(index=False)):
        lon, lat = round(float(row.boylam), 12), round(float(row.enlem), 12)
        mw = round(float(row.mw), 12)
        j = np.searchsorted(np.round(m, 12), mw, side='right') - 1
        if not (0 <= j < len(m) - 1 and lo <= row.derinlik < hi):
            continue
        c = np.flatnonzero((g[:, 0] <= lon) & (lon < g[:, 1]) & (g[:, 2] <= lat) & (lat < g[:, 3]))
        if len(c):
            sec.append(i); cidx.append(c[0]); midx.append(j)
    return olaylar.iloc[sec].copy().reset_index(drop=True), np.asarray(cidx, int), np.asarray(midx, int)


@dataclass(frozen=True)
class Model:
    ad: str
    beklenen: Callable
    zamana_bagli: bool = False
    gecmis_ayarlari: dict | None = None
    taban_metadata: dict | None = None

    def __post_init__(self):
        kaynak = getattr(getattr(self.beklenen, '__self__', None), 'metadata', {})
        object.__setattr__(self, 'taban_metadata', dict(kaynak if self.taban_metadata is None else self.taban_metadata))
        if self.gecmis_ayarlari is not None:
            object.__setattr__(self, 'gecmis_ayarlari', dict(self.gecmis_ayarlari))


@dataclass
class Kosu:
    ad: str
    beklenen: np.ndarray
    gozlem: np.ndarray
    olay_oranlari: np.ndarray
    logL: float
    olaylar: pd.DataFrame
    cerceve: tuple
    adim: str = 'gunluk'
    taban_derinlik: dict | None = None

    def tutarlilik(self, **kwargs):
        return tutarlilik(self.beklenen, self.gozlem, **kwargs)


def kos(modeller, baslangic, bitis, katalog, izgara, m_kenarlar, *, derinlik=None, bolge=None):
    """Statik tek çağrı, dinamik günlük; bellekte zaman küpü tutulmaz.

    Statik toplam sayıları ortak günlük kutulara süre orantılı dağıtılır.
    Dinamik model yalnız gün başından önceki geçmişi alır. Aynı günün
    olayları gün bitene dek ebeveyn olmaz. Her dinamik aday kendi donmuş
    sinir/baslangic_yil/derinlik_max (<=70 km) geçmiş filtresini belirtir;
    hedefin M/derinlik filtresi geçmişe uygulanmaz.
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
    cerceve = (t0.isoformat(), t1.isoformat(), tuple(derinlik),
               hashlib.sha256(g.tobytes() + np.round(m, 12).tobytes()).hexdigest(), bolge)
    hedef = katalog[(katalog.zaman >= t0) & (katalog.zaman < t1)]
    hedef, ci, mi = olay_kutulari(hedef, izgara, m, derinlik)
    gozlem = np.zeros(shape, dtype=int)
    np.add.at(gozlem, (ci, mi), 1)
    gun = ((hedef.zaman - t0) / pd.Timedelta(days=1)).to_numpy(dtype=float).astype(int)
    gun_sayisi = int((t1 - t0) / pd.Timedelta(days=1))
    sonuc = {}
    for model in modeller:
        olay_lam = np.empty(len(hedef), float)
        toplam = np.zeros(shape, float)
        ll = 0.0

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

        def tahmin(a, b):
            gecmis = gecmis_katalog[gecmis_katalog.zaman < a].copy(deep=True)
            lam = oranlar(model.beklenen(a, b, gecmis, izgara.copy(deep=True), m.copy()))
            if lam.shape != shape:
                raise PuanHatasi(f'{model.ad}: beklenen şekil {shape}, gelen {lam.shape}')
            return lam

        sabit = None if model.zamana_bagli else tahmin(t0, t1) / gun_sayisi
        for d in range(gun_sayisi):
            a = t0 + pd.Timedelta(days=d)
            lam = tahmin(a, a + pd.Timedelta(days=1)) if sabit is None else sabit
            toplam += lam
            idx = np.flatnonzero(gun == d)
            ll -= float(lam.sum())
            if len(idx):
                rates = lam[ci[idx], mi[idx]]
                olay_lam[idx] = rates
                if (rates == 0).any():
                    ll = -np.inf
                else:
                    ll += float(np.log(rates).sum())
                # Aynı günlük hücrede n>1 ise Poisson n! mutlaka çıkarılır.
                _, n = np.unique(ci[idx] * shape[1] + mi[idx], return_counts=True)
                ll -= float(gammaln(n + 1).sum())
        kaynak_derinlik = {k: model.taban_metadata[k] for k in
                           ('derinlik_min', 'derinlik_max', 'derinlik_tanimi')
                           if k in model.taban_metadata}
        sonuc[model.ad] = Kosu(model.ad, toplam, gozlem.copy(), olay_lam, ll, hedef.copy(), cerceve,
                              taban_derinlik=kaynak_derinlik or None)
    return sonuc


def karsilastir(model: Kosu, taban: Kosu, *, alfa=0.05):
    """Aynı hedef sırası ve günlük skor; Poisson farkı/IG özdeşliği."""
    if model.cerceve != taban.cerceve or model.adim != taban.adim or not model.olaylar.equals(taban.olaylar) or not np.array_equal(model.gozlem, taban.gozlem):
        raise PuanHatasi('Koşuların hedefleri/adımları eşleşmiyor')
    if not 0 < alfa < 1:
        raise PuanHatasi('alfa (0,1) içinde olmalı')
    sifir_model = int(np.count_nonzero(model.olay_oranlari == 0))
    sifir_taban = int(np.count_nonzero(taban.olay_oranlari == 0))
    if sifir_model or sifir_taban:
        s = dict(N=len(model.olaylar), IG=None, IG_olay=None, integral_terimi=None,
                 T=None, p_T=None, p_W=None, W=None, GA=None, durum='tanımsız',
                 sebep='Gözlemli sıfır oran: IG/T/W tanımsız; model kazanamaz',
                 sifir_oran_model=sifir_model, sifir_oran_taban=sifir_taban)
    else:
        s = eslestirilmis(model.olay_oranlari, taban.olay_oranlari,
                         model.beklenen.sum(), taban.beklenen.sum(), alfa)
        s['durum'] = 'tanımlı' if s['IG'] is not None else 'tanımsız'
    if s['IG'] is not None and not np.isclose((model.logL - taban.logL) / s['N'], s['IG'], rtol=1e-9, atol=1e-9):
        raise PuanHatasi('Poisson farkı / N != IG')
    s.update(model=model.ad, taban=taban.ad, logL_model=model.logL, logL_taban=taban.logL,
             beklenen_model=float(model.beklenen.sum()), beklenen_taban=float(taban.beklenen.sum()),
             karsilastirma_kimligi=dict(hedef=model.cerceve, adim=model.adim,
                                       model_derinlik=model.taban_derinlik,
                                       taban_derinlik=taban.taban_derinlik))
    return s
