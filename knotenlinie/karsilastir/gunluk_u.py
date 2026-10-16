"""Deney U: skor defteri ve topluluk (İtalya günlük, ETAS-LM çıtası).

Aşamalar:
  ayar      ≤2005 kurulumları (R-lm, N, ETAS-LM arka planı)
  defter    her dönem için 5 modelin olay/gün defterleri
  olcum     2006–2010 ağırlıkları donar; 2011–2015 ölçümü yazılır
  hepsi     tamamı

Ölçüm yalnız defterlerden hesaplanır (model yeniden koşmaz). Ağırlıklar
2006–2010 M≥2,95 logL'inde seçilir ve 2011–2015'te değişmez.
"""
from __future__ import annotations

import os
for _k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_k, '1')

import argparse
import gc
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np
import pandas as pd

from knotenlinie.karsilastir.gunluk_r import gecmis_ayari, kaynak_oku, rss_byte
from knotenlinie.karsilastir.kosucu import KESIM, Model, geometri, katalog_kontrol, utc
from knotenlinie.karsilastir.ortak4 import AyriGecmis
from knotenlinie.karsilastir.puan import holm, tutarlilik
from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.etas_lm.cekirdek import B as LM_B, MC as LM_MC, zaman_katsayilari
from knotenlinie.etas_mc25.arayuz import SigGecmis, yukle as n_yukle
from knotenlinie.etas_uzun.arayuz import TamGecmis, UzunETAS
from knotenlinie.etas_uzun.olcek import AYAR_SON
from knotenlinie.kaskad.arayuz import KaskadETAS
from knotenlinie.ortak_zemin.arayuz import DuzETAS, ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla
from knotenlinie.skor_defteri.defter import KOK as DEFTER_KOK
from knotenlinie.skor_defteri.defter import alt_indeks, alt_sutun, defter_oku, defter_yaz, kos_defter
from knotenlinie.skor_defteri.karisim import agirlik_sec, iki_yonlu, log_olabilirlik, ozet

OUT = KOSU / 'U'   # frozen inputs are seeded from records/U/ by kayit_hazirla
KURAL = KAYIT / 'U' / 'KURAL.md'   # frozen rule, read only
DEFTER = DEFTER_KOK / 'U'
AYAR = DEFTER / 'ayar'
BAS6, SON6 = '2006-01-01T00:00:00Z', '2011-01-01T00:00:00Z'
BAS11, SON11 = '2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z'
TOHUM = 20261005
ESIKLER = (2.95, 3.95, 4.95)
DERINLIK = (0, 30)
IZGARA_SHA = 'ortak/italya_izgara.csv'
KATALOG_SHA = 'ortak/italya_katalog_le2015.csv'

R_ORTAK = 'R-ortak-kaskad'
R_LM = 'R-lm-kaskad'
ETAS_LM = 'ETAS-LM'
ORTAK = 'ortak-ETAS'
N_KASKAD = 'N-ortak-kaskad'
MODEL_LIST = [R_ORTAK, R_LM, ETAS_LM, ORTAK, N_KASKAD]
TOPLULUKLAR = {
    'T1': [R_ORTAK, ETAS_LM],
    'T2': [R_ORTAK, ORTAK, N_KASKAD],
    'T3': [R_ORTAK, R_LM, ETAS_LM, ORTAK, N_KASKAD],
}


# --------------------------------------------------------------------------- #
# Yardımcı modeller
# --------------------------------------------------------------------------- #
class GrUzat:
    """Mc=3,1 düz ortak tabanı kendi b'siyle M≥2,95 yüzeyine GR ile uzatır.

    Hücre oranı tabanın [Mc,+∞) integralidir; her kutu aynı GR payını alır:
    10^(-b(alt-Mc)) − 10^(-b(üst-Mc)). Mc'nin üstündeki kutularda bu, tabanın
    kendi formülüyle birebir aynıdır (testle gösterilir); altındaki kutular GR
    ile uzatılır. Ortak-ETAS topluluk üyesidir, referans değildir; uzatma
    raporda açıkça yazılır.
    """

    def __init__(self, taban):
        self.taban = taban
        self.mc = taban.mc
        self.b = taban.b
        self.kutu = taban.kutu
        self.p = taban.p

    @property
    def metadata(self):
        d = dict(getattr(self.taban, 'metadata', {}) or {})
        d.update(gr_uzatma=True, taban_mc=self.taban.mc,
                 notu='M<Mc, GR ve tabanın kendi b değeriyle uzatıldı')
        return d

    def beklenen(self, a, z, h, izgara, m_kenarlar):
        edges = np.asarray(m_kenarlar, float)
        if edges[0] >= self.taban.mc - 1e-12:
            return self.taban.beklenen(a, z, h, izgara, m_kenarlar)
        cell = self.taban.beklenen(a, z, h, izgara, np.array([self.taban.mc, np.inf]))[:, 0]
        mag = 10 ** (-self.b * (edges[:-1] - self.mc)) - 10 ** (-self.b * (edges[1:] - self.mc))
        out = cell[:, None] * mag[None, :]
        if not np.isfinite(out).all() or (out < 0).any():
            raise ValueError('GR uzatması sonlu/negatif değil')
        return out


def arka_plan_mct(katalog, izgara, *, bas, son, kirilma, mc0, mc1,
                  komsu=10, alt_bant=1.1, maksiter=200, tolerans=1e-6):
    """J'nin Eq.3 iteratif Gaussian ayıklaması; Mc(t) ile 1985–2005 tabanı."""
    from scipy.spatial import cKDTree
    from scipy.special import ndtr
    from knotenlinie.etas.model import yerel_metrik
    from knotenlinie.etas_lm.arka_plan import km_izgara
    from knotenlinie.etas_lm.cekirdek import C, D, P, YIL, uretkenlik
    from knotenlinie.ortak_zemin.veri import IZGARA
    start, end, kir = utc(bas), utc(son), utc(kirilma)
    raw = katalog[['zaman', 'enlem', 'boylam', 'derinlik', 'mw']].copy()
    raw['zaman'] = pd.to_datetime(raw['zaman'], utc=True)
    if (raw.zaman >= end).any() or not start < kir < end:
        raise ValueError('Arka-plan Mc(t) penceresi geçersiz')
    mc = np.where((raw.zaman < kir).to_numpy(), mc0, mc1)
    use = ((raw.zaman >= start) & (raw.derinlik >= 0) & (raw.derinlik < 30) &
           (raw.mw.to_numpy(float) >= mc)).to_numpy()
    k = raw[use].reset_index(drop=True)
    mc = mc[use]
    if len(k) <= komsu:
        raise ValueError('Mc(t) KDE için yeterli kaynak yok')
    g = izgara[IZGARA].to_numpy(float)
    met = yerel_metrik((g[:, 2].min(), g[:, 3].max(), g[:, 0].min(), g[:, 1].max()))
    x, y = met.km(k.boylam.to_numpy(float), k.enlem.to_numpy(float))
    xy = np.column_stack([x, y])
    bandwidth = np.maximum(cKDTree(xy).query(xy, k=komsu + 1)[0][:, -1], alt_bant)
    duration = float((end - start) / pd.Timedelta(days=1))
    time = ((k.zaman - start) / pd.Timedelta(days=1)).to_numpy(float)
    # Mc(t) tamlık kompansatörü: her Mc=3,1 dönemi olayı, Mc=2,5 kataloğunda
    # 10^{b(Mc(t)-2.5)} olayı temsil eder (J b=1). Şekil bozulmaz, ölçek düzelir.
    b_ref = 1.0
    w_comp = 10.0 ** (b_ref * (mc - 2.5))
    r2 = (x[:, None] - x[None, :]) ** 2 + (y[:, None] - y[None, :]) ** 2
    gaussian = np.exp(-r2 / (2 * bandwidth[None, :] ** 2)) / (2 * np.pi * bandwidth[None, :] ** 2)
    age = time[:, None] - time[None, :]
    trigger = np.where(age > 0, (np.maximum(age, 0) + C) ** (-P), 0)
    trigger *= D / (2 * np.pi * (r2 + D * D) ** 1.5) * uretkenlik(k.mw.to_numpy(float))[None, :] * w_comp[None, :]
    trig = trigger.sum(axis=1)
    weights = np.ones(len(k))
    delta = None
    for iteration in range(1, maksiter + 1):
        bg = np.einsum('ij,j->i', gaussian, weights * w_comp, optimize=False) / duration
        new = bg / (bg + trig)
        delta = float(np.max(np.abs(new - weights)))
        weights = new
        if delta < tolerans:
            break
    if delta >= tolerans:
        raise ValueError('Mc(t) arka-plan iterasyonu yakınsamadı')
    grid_km = km_izgara(izgara, met)
    cell = np.zeros(len(grid_km))
    for j in range(len(k)):
        sx = ndtr((grid_km[:, 1] - x[j]) / bandwidth[j]) - ndtr((grid_km[:, 0] - x[j]) / bandwidth[j])
        sy = ndtr((grid_km[:, 3] - y[j]) / bandwidth[j]) - ndtr((grid_km[:, 2] - y[j]) / bandwidth[j])
        cell += weights[j] * w_comp[j] * sx * sy / duration
    mu = weights * w_comp
    meta = dict(ayar_baslangic=start.isoformat(), ayar_bitis=end.isoformat(),
                ayar_max_zaman=k.zaman.max().isoformat(), N=len(k), komsu=komsu,
                alt_bant_km=alt_bant, bant_km_min=float(bandwidth.min()),
                bant_km_medyan=float(np.median(bandwidth)), iterasyon=iteration, son_fark=delta,
                arka_plan_payi=float(weights.mean()), mu_yil=float(mu.sum() / duration * YIL),
                maske_mu_yil=float(cell.sum() * YIL), metrik=met.kayit(),
                tamlik_kompansator=dict(b_ref=b_ref,
                                       agirlik='10^(b_ref*(Mc(t)-2.5)); eksik alt-M temsili'),
                Mc_tanimi=[dict(bas=bas, son=kirilma, Mc=mc0), dict(bas=kirilma, son=son, Mc=mc1)],
                normalizasyon='Gaussian düzlemde bir; maskenin dışına taşan kütle kayıp, floor yok')
    return cell, met, meta


class ETASLMGecmis(ETASLM):
    """ETAS-LM 2006–2010 sürümü: arka plan ≤2005 Mc(t) yüzeyi, geçmiş 2005-01-01'den.

    ETASLM.beklenen 2011 öncesini ve 2005-04-16 öncesi geçmişi reddeder;
    kapılar burada ayar sonuna (2006-01-01) ve Mc=2,5 tamlığının başladığı
    2005-01-01'e çekilir, kalan hesap ETASLM ile aynıdır (Eq.1, Tablo 1).
    """
    AYAR_SON = pd.Timestamp('2006-01-01', tz='UTC')
    GECMIS_BAS = pd.Timestamp('2005-01-01', tz='UTC')

    def __init__(self, katalog_ayar, izgara, *, arka_plan, **kwargs):
        super().__init__(katalog_ayar, izgara, **kwargs)
        self.background = np.asarray(arka_plan['bg'], float)
        if self.background.shape != (len(self.izgara),):
            raise ValueError('Arka plan yüzeyi ızgarayla uyuşmuyor')
        self.metadata['arka_plan'] = arka_plan['meta']
        self.metadata['arka_plan_kaynagi'] = 'arka_plan_mct: 1985–2004 Mc 3,1 + 2005 Mc 2,5'
        self.metadata['gecmis_baslangic'] = self.GECMIS_BAS.isoformat()

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        a, z = utc(baslangic), utc(bitis)
        if not self.AYAR_SON <= a < z <= KESIM or z - a > pd.Timedelta(days=1):
            raise ValueError('ETAS-LM 2006 sürümü: ayar sonu ≤ a, ≤2016, en fazla bir gün')
        h = katalog_kontrol(gecmis)
        if (h.zaman >= a).any():
            raise ValueError('Geçmiş gün başından önce olmalı')
        g, edges = geometri(izgara, m_kenarlar)
        if not np.array_equal(g, np.round(self.izgara.to_numpy(float), 12)) or edges[0] < LM_MC:
            raise ValueError('Kurulum ızgarası/Mc uyuşmuyor')
        h = h[(h.zaman >= self.GECMIS_BAS) & (h.mw >= LM_MC) & (h.derinlik >= 0)
              & (h.derinlik < 30)].reset_index(drop=True)
        age = ((a - h.zaman) / pd.Timedelta(days=1)).to_numpy(float)
        duration = float((z - a) / pd.Timedelta(days=1))
        coeff = zaman_katsayilari(age, h.mw.to_numpy(float), duration, self.adim, self.nesil)
        spatial = self._mekan(h)
        raw = coeff[:, :-1] @ spatial + coeff[:, -1, None] * self.background[None, :]
        cell = raw[-1].copy()
        for generation in range(len(raw) - 2, -1, -1):
            cell = raw[generation] + self.gecis(cell)
        if cell.sum():
            self.max_last_ratio = max(self.max_last_ratio, float(raw[-1].sum()) / float(cell.sum()))
        mag = 10 ** (-LM_B * (edges[:-1] - LM_MC)) - 10 ** (-LM_B * (edges[1:] - LM_MC))
        return cell[:, None] * mag[None, :]


# --------------------------------------------------------------------------- #
# ≤2005 kurulumları
# --------------------------------------------------------------------------- #
def r_ml_kur(raw, grid, tur, *, maksiter=300):
    """S'nin ≤2005 R-ortak kurulumunun kardeşi: aynı KDE/Mc/b, istenen çekirdek."""
    from knotenlinie.etas import model as M
    from knotenlinie.etas_uzun.arayuz import ebeveynler
    from knotenlinie.etas_uzun.mle import Olabilirlik, ayarla, b_ayarla
    from knotenlinie.etas_uzun.olcek import kde_sec
    from knotenlinie.ortak_zemin.veri import hucre_indeks
    epoch, end = utc('1985-01-01T00:00:00Z'), utc(AYAR_SON)
    if (raw.zaman >= end).any():
        raise ValueError('MLE girdisi <2006 olmalı')
    box = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    d = ebeveynler(raw, box, end)
    target = d[hucre_indeks(d, grid) >= 0].reset_index(drop=True)
    mc = np.where(target.zaman < utc('2005-01-01T00:00:00Z'), 3.1, 2.5)
    bmeta = b_ayarla(target.mw.to_numpy(), mc)
    hist = kde_sec(target, grid, box)
    t = ((d.zaman - epoch) / pd.Timedelta(days=1)).to_numpy(float)
    T = float((end - epoch) / pd.Timedelta(days=1))
    change = float((utc('2005-01-01T00:00:00Z') - epoch) / pd.Timedelta(days=1))
    u = M.arka_plan_degeri(d.boylam.to_numpy(), d.enlem.to_numpy(), hist)
    L = Olabilirlik(t, d.mw.to_numpy(), d.boylam.to_numpy(), d.enlem.to_numpy(),
                    bmeta['deger'], T, change, grid, box, u)
    fit = ayarla(L, tur, maksiter=maksiter)
    fit.update(mc=2.5, b=bmeta, baslangic_yili=1985, ayar_baslangic=epoch.isoformat(),
               ayar_bitis=end.isoformat(), ayar_max_zaman=d.zaman.max().isoformat(),
               ayar_n=len(d), hedef_n=len(target), dis_ebeveyn_n=len(d) - len(target), kutu=box,
               arka_plan=hist, metrik=M.yerel_metrik(box).kayit(), normalizasyon=M.NORMALIZASYON,
               uzay_ayar_destegi='CSEP İtalya maskesi; dış dikdörtgen yalnız ebeveyn erişim sınırı',
               maske_kenar=L.mask.kenar,
               tamlik=dict(donemler=[dict(bas='1985-01-01', son='2005-01-01', Mc=3.1),
                                     dict(bas='2005-01-01', son='2006-01-01', Mc=2.5)],
                           referans_Mc=2.5, eksik_ebeveyn='impute edilmez; gözlenen-ebeveyn koşullu ETAS'),
               katalog_sha256=sha256(VERI / KATALOG_SHA), izgara_sha256=sha256(VERI / IZGARA_SHA),
               kaynak='knotenlinie/etas_uzun/olcek.py::kur ile aynı akış; tur=' + tur)
    return fit


def _tamlik_mct(train, yil_bas=1985):
    """tani ile aynı yıllık MAXC+GR kuralı; katalog bittiği yılda durur.

    `knotenlinie/etas_mc25/tamlik.tani` sabit 1985–2010 yıllarını tarar; ≤2005
    katalogda boş 2006–2010 yıllarını 'kabul değil' sayıp başlangıcı 2011'e
    taşırdı. Burada boş yıllar taranmaz.
    """
    from knotenlinie.ortak_zemin.ayar import b_ayarla
    if train.empty or (train.zaman >= pd.Timestamp('2011-01-01', tz='UTC')).any():
        raise ValueError('Tamlık yalnız ≤2010')
    son = int(train.zaman.max().year)
    rows = []
    for year in range(yil_bas, son + 1):
        d = train[train.zaman.dt.year == year]
        m = d.mw.to_numpy(float)
        positive = m[m > 0]
        h, e = np.histogram(positive, np.arange(.05, 9.06, .1))
        maxc = float(e[h.argmax()] + .05) if len(positive) else None
        s = m[m >= 2.5]
        b = b_ayarla(s, 2.5) if len(s) >= 100 else None
        if b:
            thresholds = np.round(np.arange(2.5, 9.01, .1), 2)
            obs = np.array([(s >= z - 1e-10).sum() for z in thresholds])
            pred = len(s) * 10 ** (-b['deger'] * (thresholds - 2.5))
            R = float(100 * (1 - np.abs(obs - pred).sum() / obs.sum()))
        else:
            R = None
        rows.append(dict(yil=year, N=len(s), sifir_buyukluk=int((m == 0).sum()),
                         MAXC=maxc, Mc_MAXC_artı_02=maxc + .2 if maxc is not None else None,
                         b=b, GR_uyum_yuzde=R,
                         oran_25_31=float(len(s) / max(1, (m >= 3.1).sum())),
                         kabul=bool(b and maxc + .2 <= 2.5 + 1e-10 and R >= 90)))
    bad = [r['yil'] for r in rows if not r['kabul']]
    start = max(bad) + 1 if bad else yil_bas
    if start > son:
        raise ValueError('Mc2.5 kabul edilen eğitim penceresine erişmiyor')
    return dict(yillik=rows, baslangic_yili=start, mc=2.5,
                kural='N≥100; MAXC+0.2≤2.5; kümülatif GR R≥90%; kabul edilen en uzun son blok',
                notu='≤2005 kesiti; knotenlinie/etas_mc25/tamlik.tani ile aynı kural.')


def n_mc25_kur(cat, grid, *, maksiter=300):
    """N'nin ≤2005 Mc=2,5 ortak çekirdek kurulumu (yalnız 2005 bloğu).

    `knotenlinie/karsilastir/gunluk_n.py` ≤2010 akışının 2006 kesiti; N'nin Mc=2,5
    tamlık bloğu 2005'te başladığı için KDE zaman bölmesi 2005 içinde yarı-yarıya
    yapılır (hiçbir 2006+ olay görülmez).
    """
    from knotenlinie.etas import model as M
    from knotenlinie.etas_mc25.mle import Olabilirlik, ayarla
    from knotenlinie.ortak_zemin.arka_plan import BANTLAR_KM, ZEMIN_PAYLARI, kde_histogram
    from knotenlinie.ortak_zemin.ayar import b_ayarla, gr_ayar_paylari
    end = utc('2006-01-01T00:00:00Z')
    train = cat[(cat.zaman < end) & (cat.derinlik < 30)].reset_index(drop=True)
    completeness = _tamlik_mct(train)
    year = int(completeness['baslangic_yili'])
    epoch = pd.Timestamp(f'{year}-01-01', tz='UTC')
    d = train[(train.zaman >= epoch) & (train.mw >= 2.5)].reset_index(drop=True)
    if len(d) < 200:
        raise ValueError(f'N ≤2005 bloğu çok küçük: {len(d)} olay')
    kutu = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    b = b_ayarla(d.mw.to_numpy(), 2.5)
    met = M.yerel_metrik(kutu)
    split = epoch + (end - epoch) / 2
    tr, ho = d[d.zaman < split], d[d.zaman >= split]
    trials = []
    for h in BANTLAR_KM:
        for eps in ZEMIN_PAYLARI:
            hist = kde_histogram(tr.boylam, tr.enlem, kutu, h, eps)
            u = M.arka_plan_degeri(ho.boylam.to_numpy(), ho.enlem.to_numpy(), hist)
            trials.append(dict(bant_km=h, zemin_payi=eps,
                               logL_konum=float(np.log(u / met.jakobiyen).sum())))
    best = max(trials, key=lambda r: r['logL_konum'])
    hist = kde_histogram(d.boylam, d.enlem, kutu, best['bant_km'], best['zemin_payi'])
    hist['secim'] = dict(kurulum=split.isoformat(), kurulum_n=len(tr), secim_n=len(ho),
                         yeniden_kurulum_n=len(d), en_iyi=best, adaylar=trials,
                         notu='2005 içi yarı bölme; 2006+ görülmedi')
    T = float((end - epoch) / pd.Timedelta(days=1))
    t = ((d.zaman - epoch) / pd.Timedelta(days=1)).to_numpy(float)
    L = Olabilirlik(t, d.mw.to_numpy(float), d.boylam.to_numpy(float), d.enlem.to_numpy(float),
                    2.5, b['deger'], T, kutu, M.arka_plan_degeri(d.boylam, d.enlem, hist))
    fit = ayarla(L, 'ortak', maksiter=maksiter)
    fit.update(mc=2.5, b=b, baslangic_yili=year, ayar_baslangic=epoch.isoformat(),
               ayar_bitis=end.isoformat(), ayar_max_zaman=d.zaman.max().isoformat(),
               ayar_n=len(d), kutu=kutu, arka_plan=hist, metrik=met.kayit(),
               normalizasyon=M.NORMALIZASYON, tamlik=completeness,
               gr_ayar_paylari=gr_ayar_paylari(d.mw, 2.5, b['deger']),
               katalog_sha256=sha256(VERI / KATALOG_SHA), izgara_sha256=sha256(VERI / IZGARA_SHA),
               kaynak='knotenlinie/karsilastir/gunluk_n.py::kur akışı; kesim 2006-01-01, KDE 2005 içi')
    return fit


def ayarlari_uret(raw, cat, grid, *, maksiter=300):
    AYAR.mkdir(parents=True, exist_ok=True)
    paths = {}
    raw2006 = raw[raw.zaman < utc('2006-01-01T00:00:00Z')].reset_index(drop=True)
    if not (AYAR / f'{R_LM}_le2005.json').exists():
        fit = r_ml_kur(raw2006, grid, 'lm', maksiter=maksiter)
        _yaz(AYAR / f'{R_LM}_le2005.json', fit)
        print('R-lm ≤2005 MLE', fit['parametreler'], 'n=', fit['dallanma'], flush=True)
    paths[R_LM] = AYAR / f'{R_LM}_le2005.json'
    if not (AYAR / f'{N_KASKAD}_le2005.json').exists():
        fit = n_mc25_kur(cat, grid, maksiter=maksiter)
        _yaz(AYAR / f'{N_KASKAD}_le2005.json', fit)
        print('N ≤2005 MLE', fit['parametreler'], 'n=', fit['dallanma'], flush=True)
    paths[N_KASKAD] = AYAR / f'{N_KASKAD}_le2005.json'
    if not (AYAR / 'ETAS-LM_arka_plan_le2005.json').exists():
        start, end, kir = '1985-01-01T00:00:00Z', '2006-01-01T00:00:00Z', '2005-01-01T00:00:00Z'
        bg, met, meta = arka_plan_mct(cat[cat.zaman < utc('2006-01-01T00:00:00Z')].reset_index(drop=True),
                                      grid, bas=start, son=end, kirilma=kir, mc0=3.1, mc1=2.5)
        _yaz(AYAR / 'ETAS-LM_arka_plan_le2005.json', dict(bg=bg.tolist(), meta=meta))
        print('ETAS-LM ≤2005 arka plan N=', meta['N'], 'μ/yıl=', meta['mu_yil'], flush=True)
    paths[ETAS_LM] = AYAR / 'ETAS-LM_arka_plan_le2005.json'
    return paths


def _yaz(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)

    def cevir(v):
        if isinstance(v, dict):
            return {str(k): cevir(x) for k, x in v.items()}
        if isinstance(v, (list, tuple, np.ndarray)):
            return [cevir(x) for x in list(v)]
        if isinstance(v, (float, np.floating)):
            return float(v) if np.isfinite(v) else None
        if isinstance(v, np.integer):
            return int(v)
        if isinstance(v, (bool, np.bool_)):
            return bool(v)
        return v

    path.write_text(json.dumps(cevir(obj), ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def _oku_json(path):
    return json.loads(Path(path).read_text())



# --------------------------------------------------------------------------- #
# Modeller (her biri koşmadan hemen önce kurulur; bellek için)
# --------------------------------------------------------------------------- #
def fabrikalar(donem, cat, raw, grid, ayar_paths):
    """ad -> Model üreten çağrı. '2006-2010': ≤2005 kurulumları; '2011-2015': ≤2010."""
    f = {}
    if donem == '2006-2010':
        def ortak():
            base = ayar_tabani('italya', son='2006-01-01')
            ayar = gecmis_ayari(base, 'italya')
            return Model(ORTAK, AyriGecmis(GrUzat(base), cat, ayar).beklenen, True, ayar)

        def lm():
            s_lm = _oku_json(ayar_paths[ETAS_LM])
            bg = {'bg': np.asarray(s_lm['bg'], float), 'meta': s_lm['meta']}
            m = ETASLMGecmis(cat[cat.zaman < utc(BAS6)], grid, arka_plan=bg, adim=32, nesil=10)
            box = m.met.kutu
            s = dict(sinir=(box[2], box[3], box[0], box[1]), baslangic_yil=2005, derinlik_max=30)
            return Model(ETAS_LM, m.beklenen, True, s)

        def nk():
            n = KaskadETAS(DuzETAS(_oku_json(ayar_paths[N_KASKAD]), grid), adim=32, nesil=10)
            s = gecmis_ayari(n.taban, 'italya')
            s['derinlik_max'] = 30
            return Model(N_KASKAD, SigGecmis(n, cat, s).beklenen, True, s)

        def r(ad):
            def kur():
                m = UzunETAS(_oku_json(ayar_paths[ad]), grid, adim=32, nesil=10)
                s = gecmis_ayari(m, 'italya')
                s['derinlik_max'] = 30
                return Model(ad, TamGecmis(m, raw).beklenen, True, s)
            return kur
    else:
        def ortak():
            base = ayar_tabani('italya', son='2011-01-01')
            ayar = gecmis_ayari(base, 'italya')
            return Model(ORTAK, AyriGecmis(GrUzat(base), cat, ayar).beklenen, True, ayar)

        def lm():
            m = ETASLM(cat[cat.zaman < utc(BAS11)], grid, adim=32, nesil=10)
            box = m.met.kutu
            s = dict(sinir=(box[2], box[3], box[0], box[1]), baslangic_yil=2005, derinlik_max=30)
            return Model(ETAS_LM, m.beklenen, True, s)

        def nk():
            n = n_yukle('ortak', grid, kaskad=True, adim=32, nesil=10)
            s = gecmis_ayari(n.taban, 'italya')
            s['derinlik_max'] = 30
            return Model(N_KASKAD, SigGecmis(n, cat, s).beklenen, True, s)

        def r(ad):
            dosya = {R_ORTAK: 'etas_ortak.json', R_LM: 'etas_lm.json'}[ad]

            def kur():
                m = UzunETAS(_oku_json(VERI / 'ortak/uzun' / dosya), grid, adim=32, nesil=10)
                s = gecmis_ayari(m, 'italya')
                s['derinlik_max'] = 30
                return Model(ad, TamGecmis(m, raw).beklenen, True, s)
            return kur
    f[ORTAK], f[ETAS_LM], f[N_KASKAD] = ortak, lm, nk
    f[R_ORTAK], f[R_LM] = r(R_ORTAK), r(R_LM)
    if set(f) != set(MODEL_LIST):
        raise ValueError('Model kümesi eksik')
    return f


# --------------------------------------------------------------------------- #
# Defter üretimi
# --------------------------------------------------------------------------- #
def _kenarlar():
    return np.r_[np.round(2.95 + 0.1 * np.arange(61), 2), np.inf]


def _marjinal_yol(ad, donem):
    return DEFTER / f'{ad}__{donem}__marjinal.npz'


def _donem_pencere(donem):
    return (BAS6, SON6) if donem == '2006-2010' else (BAS11, SON11)


def def_uret(donem, cat, raw, grid, ayar_paths, *, gun_siniri=None, adlar=None, zorla=False):
    """Her modeli sırayla kurar, koşar, yazar ve belleği boşaltır; mevcut defter atlanır."""
    bas, son = _donem_pencere(donem)
    if gun_siniri:
        son = (utc(bas) + pd.Timedelta(days=gun_siniri)).isoformat()
    fab = fabrikalar(donem, cat, raw, grid, ayar_paths)
    out = {}
    for ad in (adlar or MODEL_LIST):
        olay_yol = DEFTER / f'{ad}__{donem}__olay.csv.gz'
        if not gun_siniri and not zorla and olay_yol.exists() and _marjinal_yol(ad, donem).exists():
            print(donem, ad, 'var, atlandı', flush=True)
            continue
        t0 = time.monotonic()
        model = fab[ad]()
        d = kos_defter([model], bas, son, cat, grid, _kenarlar(), derinlik=DERINLIK, bolge='italya',
                       ilerleme=150)[ad]
        d.ek['sure_s'] = time.monotonic() - t0
        print(donem, ad, 'N=%d logL=%.4f Lam295=%.2f Lam395=%.2f s=%.0f RSS=%.2fGB' % (
            d.N, d.logL, d.gun['Lam295'].sum(), d.gun['Lam395'].sum(), d.ek['sure_s'], rss_byte() / 1e9),
            flush=True)
        if gun_siniri:
            out[ad] = d
        else:
            defter_yaz(d, DEFTER, donem)
            np.savez_compressed(_marjinal_yol(ad, donem), beklenen=d.beklenen, gozlem=d.gozlem,
                                logL=np.array([d.logL]))
        del model, d
        gc.collect()
    return out


def defterleri_yukle(donem):
    out = {}
    for ad in MODEL_LIST:
        d = defter_oku(ad, DEFTER, donem)
        with np.load(_marjinal_yol(ad, donem)) as z:
            d.beklenen, d.gozlem, d.logL = z['beklenen'], z['gozlem'], float(z['logL'][0])
        out[ad] = d
    return out


# --------------------------------------------------------------------------- #
# Seçim (yalnız 2006–2010) ve ölçüm (2011–2015)
# --------------------------------------------------------------------------- #
def kural_sha():
    yol = KURAL
    if not yol.exists():
        raise SystemExit('Önce U/KURAL.md yazılmalı (2011–2015 puanlamasından önce)')
    return sha256(yol)


def _defter_hash(donem):
    return {p.name: sha256(p) for p in sorted(DEFTER.glob(f'*__{donem}__*'))}


def agirlik_belirle(d2006):
    """Üç sabit topluluk için 2006–2010 M≥2,95 logL'ini en büyükleyen simplex ağırlığı."""
    out = {}
    for ad, uyeler in TOPLULUKLAR.items():
        defs = [d2006[a] for a in uyeler]
        sec = agirlik_sec(defs, 2.95)
        esit = [1.0 / len(uyeler)] * len(uyeler)
        tek = {a: log_olabilirlik([d2006[a]], [1.0], 2.95) for a in uyeler}
        out[ad] = dict(uyeler=uyeler, eniyi=sec['agirliklar'], esit=esit,
                       logL_eniyi=log_olabilirlik(defs, sec['agirliklar'], 2.95),
                       logL_esit=log_olabilirlik(defs, esit, 2.95),
                       logL_uyeler_tek=tek, secim='2006-2010, M>=2.95, simplex')
    return out


def agirlik_yaz(d2006, kural):
    res = dict(agirliklar=agirlik_belirle(d2006), kural_SHA256=kural,
               defter2006_sha256=_defter_hash('2006-2010'),
               tablo_2006=_tekil_2006(d2006),
               not_='2011-2015 açılmadan yazıldı; bu kayıt ölçümden sonra yeniden ayarlanmaz')
    _yaz(OUT / 'AGIRLIK.json', res)
    return res


def _tekil_2006(d2006):
    return {a: dict(N295=int((d.olay.mw >= 2.95 - 1e-9).sum()), N395=int((d.olay.mw >= 3.95 - 1e-9).sum()),
                    Lam295=float(d.gun['Lam295'].sum()), Lam395=float(d.gun['Lam395'].sum()),
                    logL295=log_olabilirlik([d], [1.0], 2.95), logL395=log_olabilirlik([d], [1.0], 3.95))
            for a, d in d2006.items()}


def nsm_mixture(defterler, adlar, w, alt, olcek=None):
    j = alt_indeks(alt)
    c = np.ones(len(adlar)) if olcek is None else np.asarray(olcek, float)
    lam = sum(wi * ci * defterler[a].beklenen[:, j:] for wi, ci, a in zip(w, c, adlar))
    goz = defterler[adlar[0]].gozlem[:, j:]
    r = tutarlilik(lam, goz, tekrar=10000, tohum=TOHUM)
    return dict(N_ust=r['N']['ust_kuyruk'], N_alt=r['N']['alt_kuyruk'], N_gecti=r['N']['gecti'],
                S_p=r['S']['p'], S_gecti=r['S']['gecti'], M_p=r['M']['p'], M_gecti=r['M']['gecti'],
                gecti=r['gecti'])


def _satir(d, aday_adlar, taban_ad, alt, w, kural, donem='2011-2015', olcek=None):
    aday = [d[a] for a in aday_adlar]
    s = ozet(aday, d[taban_ad], alt, agirliklar=w, olcekler=olcek)
    iki = iki_yonlu(aday, d[taban_ad], alt, w, olcek)
    return dict(aday='+'.join(aday_adlar), agirlik_kurali=kural,
                agirliklar=[float(x) for x in w], taban=taban_ad, donem=donem, esik=alt,
                N=s['N'], Lambda_aday=s['Lambda_aday'], Lambda_taban=s['Lambda_taban'],
                IG=s['IG'], IG_olay=s['IG_olay'], integral=s['integral'],
                SE_blok=s['SE_blok'], z=s['z'], p_tek=s['p_tek'], GA95=s['GA95'],
                blok_sayisi=s['blok_sayisi'], p_T_iki_yonlu=iki['p_T'], p_W_iki_yonlu=iki['p_W'],
                NSM=nsm_mixture(d, aday_adlar, w, alt, olcek))


def olcum(agirliklar, d2011):
    """Ağırlıklar donmuş; 2011–2015 tek sefer ölçülür. Holm: her (eşik, taban, kural) için 3 topluluk."""
    satirlar = []
    for alt in ESIKLER:
        for taban_ad in (ETAS_LM, R_ORTAK):
            for kural in ('eniyi', 'esit'):
                grup = []
                for ad, uyeler in TOPLULUKLAR.items():
                    s = _satir(d2011, uyeler, taban_ad, alt, agirliklar[ad][kural], kural)
                    s['topluluk'] = ad
                    grup.append(s)
                for s, ph in zip(grup, holm([x['p_tek'] for x in grup])):
                    s['p_tek_holm3'] = ph
                satirlar.extend(grup)
            for ad in MODEL_LIST:
                if ad == taban_ad:
                    continue
                s = _satir(d2011, [ad], taban_ad, alt, [1.0], 'tekil')
                s['topluluk'] = None
                satirlar.append(s)
    return satirlar


def tani_satiri(d2006, d2011):
    """R'nin toplamı LM'ye eşitlense (c=Λ_LM/Λ_R, 2006–2010'dan); yalnız tanı, seçimde kullanılmaz."""
    out = {}
    for alt in ESIKLER:
        kol = alt_sutun(alt)
        c = float(d2006[ETAS_LM].gun[kol].sum() / d2006[R_ORTAK].gun[kol].sum())
        s = ozet([d2011[R_ORTAK]], d2011[ETAS_LM], alt, agirliklar=[1.0], olcekler=[c])
        out[str(alt)] = dict(c=c, N=s['N'], Lambda_aday=s['Lambda_aday'], Lambda_taban=s['Lambda_taban'],
                             IG=s['IG'], IG_olay=s['IG_olay'], integral=s['integral'],
                             SE_blok=s['SE_blok'], z=s['z'], p_tek=s['p_tek'])
    return dict(not_='R-ortak-kaskad yüzeyi c=Λ_LM/Λ_R (2006–2010, eşik başına) ile çarpıldı; seçimde kullanılmaz',
                satirlar=out)


def main():
    kayit_hazirla('U')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('ayar', 'defter', 'sec', 'olcum', 'hepsi'), default='hepsi')
    ap.add_argument('--donem', choices=('2006-2010', '2011-2015', 'hepsi'), default='hepsi')
    ap.add_argument('--maksiter', type=int, default=300)
    ap.add_argument('--gun-siniri', type=int, default=None, help='yalnız duman testi; hiçbir şey yazmaz')
    ap.add_argument('--modeller', nargs='*', default=None)
    ap.add_argument('--cikti', default='OLCUM.json', help='ölçüm çıktı dosya adı (U/ altında)')
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    DEFTER.mkdir(parents=True, exist_ok=True)
    basla = time.monotonic()
    cat = katalog_oku(VERI / KATALOG_SHA)
    raw, paths, report = kaynak_oku()
    grid = ayar_tabani('italya', son='2006-01-01').izgara
    ayar_paths = {R_ORTAK: VERI / 'ortak/uzun/etas_s_le2005.json'}
    if args.asama in ('ayar', 'hepsi'):
        ayar_paths.update(ayarlari_uret(raw, cat, grid, maksiter=args.maksiter))
    else:
        for ad, ad_dosya in ((R_LM, f'{R_LM}_le2005.json'), (N_KASKAD, f'{N_KASKAD}_le2005.json'),
                             (ETAS_LM, 'ETAS-LM_arka_plan_le2005.json')):
            yol = AYAR / ad_dosya
            if not yol.exists():
                raise SystemExit(f'Önce ayar aşaması: eksik {yol}')
            ayar_paths[ad] = yol
    if args.asama == 'ayar':
        return
    donemler = ['2006-2010', '2011-2015'] if args.donem == 'hepsi' else [args.donem]
    if args.asama in ('defter', 'hepsi'):
        for dn in donemler:
            if dn == '2011-2015':
                kural_sha()
                if not (OUT / 'AGIRLIK.json').exists() and not args.gun_siniri:
                    raise SystemExit('Önce 2006–2010 defteri ve AGIRLIK.json (sec aşaması)')
            def_uret(dn, cat, raw, grid, ayar_paths, gun_siniri=args.gun_siniri, adlar=args.modeller)
            print(dn, 'defterleri hazır', time.monotonic() - basla, flush=True)
            if args.gun_siniri:
                return
            if dn == '2006-2010' and args.asama == 'hepsi':
                agirlik_yaz(defterleri_yukle('2006-2010'), kural_sha())
                print('AGIRLIK.json yazıldı', flush=True)
    if args.asama == 'sec':
        agirlik_yaz(defterleri_yukle('2006-2010'), kural_sha())
        return
    if args.asama == 'defter':
        return
    # ölçüm
    kural = kural_sha()
    ag = json.loads((OUT / 'AGIRLIK.json').read_text())
    if ag['kural_SHA256'] != kural:
        raise SystemExit('AGIRLIK.json KURAL.md ile uyuşmuyor (kural ağırlıktan sonra değişmiş)')
    if ag['defter2006_sha256'] != _defter_hash('2006-2010'):
        raise SystemExit('2006–2010 defterleri AGIRLIK.json yazıldıktan sonra değişmiş')
    d2006 = defterleri_yukle('2006-2010')
    d2011 = defterleri_yukle('2011-2015')
    satirlar = olcum(ag['agirliklar'], d2011)
    res = dict(satirlar=satirlar, agirliklar=ag['agirliklar'], tablo_2006=ag['tablo_2006'],
               tani_olcek=tani_satiri(d2006, d2011))
    res.update(durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler; kör hüküm değil',
               baslangic2006=BAS6, bitis2006=SON6, baslangic2011=BAS11, bitis2011=SON11,
               derinlik=list(DERINLIK), hucre=len(grid), modeller=MODEL_LIST,
               topluluklar={k: v for k, v in TOPLULUKLAR.items()},
               agirlik_kaynagi='2006-2010 M>=2.95 logL, simplex; 2011-2015 değişmez',
               IG_tanimi='ortalama log(λ_aday/λ_taban) − (Λ_aday−Λ_taban)/N; gün kazancı üstünde haftalık blok SE, tek yönlü z',
               NSM_notu='N iki Poisson kuyruğu; S/M sabit N multinomial 10000, tohum 20261005/20261006; eşik başına alt yüzey; operasyonel tanı',
               p_notu='p_tek: tek yönlü blok z; p_T/p_W_iki_yonlu: eşleştirilmiş iki yönlü (bağımsızlık varsayar). Holm: her (eşik,taban,kural) için üç topluluk',
               ortak_ETAS_notu='Mc=3,1 taban; M<3,1 kutuları kendi b’siyle GR ile uzatıldı (GrUzat); topluluk üyesi, referans değil',
               kural_SHA256=kural, defter2006_sha256=ag['defter2006_sha256'],
               defter2011_sha256=_defter_hash('2011-2015'),
               ayar_SHA256={str(p): sha256(p) for p in ayar_paths.values()},
               kaynak_SHA256={str(p): sha256(p) for p in paths},
               kod_SHA256={str(p): sha256(p) for p in (Path(__file__), Path('knotenlinie/skor_defteri/defter.py'),
                                                        Path('knotenlinie/skor_defteri/karisim.py'))},
               duvar_saniye=time.monotonic() - basla, rss_tepe_byte=rss_byte(),
               python=sys.version, numpy=np.__version__, pandas=pd.__version__)
    _yaz(OUT / args.cikti, res)
    print(OUT / args.cikti, 's=', res['duvar_saniye'], 'RSS=', rss_byte() / 1e9, flush=True)


if __name__ == '__main__':
    main()
