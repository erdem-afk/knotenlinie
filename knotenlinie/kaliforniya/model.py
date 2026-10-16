"""Kaliforniya uzun vadeli model: uyarlamalı Gauss KDE (hücre entegrasyonlu) × Weichert oranı × bükülü GR.

Z'nin `knotenlinie/uzun_vade` paketini import eder (kümesizleştirme, Weichert, UzunVade sınıf mantığı);
değiştirmez. Farkı: KDE kütlesi hücre merkezinde örneklenmez, hücre üzerinde entegre edilir
(HKJ07: "integrate over each cell"); 0,1 derece hücrede küçük bantlarda merkez örneklemesi yanlıdır.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.special import ndtr

from knotenlinie.uzun_vade.kumesiz import arka_plan_maskesi, dogrula, reasenberg, yerel_km
from knotenlinie.uzun_vade.weichert import weichert_mle
from knotenlinie.kaliforniya.veri import M_KENAR, yil_ondalik

KM_ENLEM = 110.57
KM_BOYLAM = 111.32
GUN_YIL = 365.25
GEYSERS = dict(boylam=(-122.95, -122.65), enlem=(38.7, 38.9))
WEI_KENAR = np.round(np.arange(2.95, 8.1, 0.1), 2)      # Mc=3,0 için 3,0 merkezli kutular
WEI_TABLO = ((1981.0, 2400.0, 3.0),)


class ModelHatasi(ValueError):
    """Model girdisi geçersiz."""


class Kafes:
    """İzgara hücrelerinin düzenli 0,1 derece kafesi (boylam, enlem indeksi)."""

    def __init__(self, izgara, adim=0.1):
        a = izgara[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float)
        self.adim = adim
        self.lon0 = float(a[:, 0].min())
        self.lat0 = float(a[:, 2].min())
        self.ix = np.rint((a[:, 0] - self.lon0) / adim).astype(int)
        self.iy = np.rint((a[:, 2] - self.lat0) / adim).astype(int)
        if (np.abs(self.lon0 + self.ix * adim - a[:, 0]) > 1e-6).any() or (
                np.abs(self.lat0 + self.iy * adim - a[:, 2]) > 1e-6).any() or (
                np.abs(a[:, 1] - a[:, 0] - adim) > 1e-6).any():
            raise ModelHatasi('ızgara düzenli 0,1 derece kafese oturmuyor')
        self.nx, self.ny = int(self.ix.max()) + 1, int(self.iy.max()) + 1
        self.lon_kenar = self.lon0 + adim * np.arange(self.nx + 1)
        self.lat_kenar = self.lat0 + adim * np.arange(self.ny + 1)
        if len(set(zip(self.ix.tolist(), self.iy.tolist()))) != len(a):
            raise ModelHatasi('çakışan hücreler')

    def hucreye(self, arr):
        return arr[self.ix, self.iy]


def kde_sekli(kafes, boylam, enlem, sigma_km, *, dayanak=4.5):
    """Her olayın Gauss çekirdeğini hücre üzerinde entegre edip toplar; (nx, ny) kütle."""
    lo, la = np.asarray(boylam, float), np.asarray(enlem, float)
    sg = np.asarray(sigma_km, float)
    kut = np.zeros((kafes.nx, kafes.ny))
    sx = sg / (KM_BOYLAM * np.cos(np.deg2rad(la)))
    sy = sg / KM_ENLEM
    for i in range(len(lo)):
        x0 = np.searchsorted(kafes.lon_kenar, lo[i] - dayanak * sx[i], side='right') - 1
        x1 = np.searchsorted(kafes.lon_kenar, lo[i] + dayanak * sx[i], side='left')
        y0 = np.searchsorted(kafes.lat_kenar, la[i] - dayanak * sy[i], side='right') - 1
        y1 = np.searchsorted(kafes.lat_kenar, la[i] + dayanak * sy[i], side='left')
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, kafes.nx), min(y1, kafes.ny)
        if x1 <= x0 or y1 <= y0:
            continue
        px = np.diff(ndtr((kafes.lon_kenar[x0:x1 + 1] - lo[i]) / sx[i]))
        py = np.diff(ndtr((kafes.lat_kenar[y0:y1 + 1] - la[i]) / sy[i]))
        kut[x0:x1, y0:y1] += np.outer(px, py)
    return kut


def bant_km(boylam, enlem, k_komsu, *, alt=0.5, ust=300.0):
    """k'inci en yakın komşu uzaklığı (km) uyarlamalı bant; HKJ07 d_i > 0,5 km."""
    lo, la = np.asarray(boylam, float), np.asarray(enlem, float)
    x, y = yerel_km(la, lo)
    agac = cKDTree(np.column_stack([x, y]))
    d, _ = agac.query(np.column_stack([x, y]), k=int(k_komsu) + 1)
    return np.clip(d[:, -1], alt, ust)


def geysers_mi(boylam, enlem):
    lo, la = np.asarray(boylam, float), np.asarray(enlem, float)
    return ((lo >= GEYSERS['boylam'][0]) & (lo < GEYSERS['boylam'][1])
            & (la >= GEYSERS['enlem'][0]) & (la < GEYSERS['enlem'][1]))


def bukulu_gr(rate_ust, b, m_ust, kenarlar, *, mc_koseli=8.0):
    """M>=m_ust toplam oranından kutu başına oran. mc_koseli None ise saf GR.

    Bükülü GR (Kagan; HKJ07 eşitlik 10): S(m) = 10^(-b(m-m0)) exp(10^(1.5(m0-mc)) - 10^(1.5(m-mc))).
    """
    k = np.asarray(kenarlar, float)
    if not np.isfinite([rate_ust, b, m_ust]).all() or b <= 0 or rate_ust < 0:
        raise ModelHatasi('oran/b/m geçersiz')
    alt = np.maximum(k[:-1], m_ust)

    def surv(m):
        m = np.asarray(m, float)
        out = np.zeros(m.shape)
        s = np.isfinite(m)
        out[s] = 10.0 ** (-b * (m[s] - m_ust))
        if mc_koseli is not None:
            out[s] *= np.exp(10.0 ** (1.5 * (m_ust - mc_koseli)) - 10.0 ** (1.5 * (m[s] - mc_koseli)))
        return out

    return np.where(k[1:] <= m_ust, 0.0, rate_ust * np.maximum(surv(alt) - surv(k[1:]), 0.0))


class Kaliforniya:
    """Zamandan bağımsız hücre×kutu beklenen sayısı (UzunVade ile aynı `beklenen` imzası)."""

    def __init__(self, sekil, izgara, *, b, rate_ust, m_ust=4.95, mc_koseli=8.0, ad='K', metadata=None):
        self.sekil = np.asarray(sekil, float)
        self.izgara = izgara[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].reset_index(drop=True).copy()
        self.b, self.rate_ust, self.m_ust, self.mc_koseli = float(b), float(rate_ust), float(m_ust), mc_koseli
        self.ad = ad
        self.metadata = dict(metadata or {}, b=self.b, rate_ust=self.rate_ust, m_ust=self.m_ust,
                             mc_koseli=mc_koseli)
        if self.sekil.shape != (len(self.izgara),) or not np.isfinite(self.sekil).all() or self.sekil.sum() <= 0:
            raise ModelHatasi('şekil/ızgara uyuşmuyor')

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        g = np.round(izgara[['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']].to_numpy(float), 9)
        if g.shape != self.izgara.shape or not np.array_equal(g, np.round(self.izgara.to_numpy(float), 9)):
            raise ModelHatasi('ızgara modelin eğitim ızgarasıyla aynı olmalı')
        bas, son = pd.Timestamp(baslangic), pd.Timestamp(bitis)
        if bas.tzinfo is None or son.tzinfo is None or son <= bas:
            raise ModelHatasi('zaman aralığı UTC ve artan olmalı')
        return self.beklenen_yil((son - bas).total_seconds() / (86400.0 * GUN_YIL), m_kenarlar)

    def beklenen_yil(self, yil, m_kenarlar):
        """Verilen süre (yıl) için hücre×kutu beklenen sayısı."""
        oran = bukulu_gr(self.rate_ust, self.b, self.m_ust, m_kenarlar, mc_koseli=self.mc_koseli)
        return self.sekil[:, None] * oran[None, :] * float(yil)


def kumesiz_maske(katalog, yontem='gk74'):
    """Zamana göre sıralı katalog ve arka plan maskesi (yalnız verilen katalogla).

    gk74: Gardner–Knopoff (1974), simetrik pencere. reasenberg: HKJ07 parametreleri
    (rfact=8, xk=0.5, p=0.95, tau 1–5 gün, xmeff=2.5); yarıçap Z'nin Reasenberg yarıçapı
    (HKJ07'nin r=0,01·10^(0,5m) değişikliği yok) ve en az küme boyu kuralı yok.
    """
    if yontem == 'reasenberg':
        k = dogrula(katalog)
        return k, reasenberg(k, rfact=8, xmeff=2.5, xk=0.5, tau_min=1.0, tau_max=5.0, p=0.95)
    return arka_plan_maskesi(katalog, yontem)


def oran_kestir(kat, kafes_sinir, bas_yil, son_yil, *, mc=3.0):
    """Weichert (tek tamlık dönemi, Mc) b ve M>=4,95 yıllık oranı; bölge olayları.

    kat: sütunlar zaman, boylam, enlem, derinlik, mw; zaten kümesiz ya da bütün.
    """
    k = kat[(kat['derinlik'] < 30.0) & (kat['mw'] >= mc)]
    lo0, lo1, la0, la1 = kafes_sinir
    k = k[(k['boylam'] >= lo0) & (k['boylam'] < lo1) & (k['enlem'] >= la0) & (k['enlem'] < la1)]
    yil = yil_ondalik(k['zaman'])
    kenar = np.round(np.arange(mc, 8.15, 0.1), 2)
    tablo = ((bas_yil, son_yil + 1.0, mc),)
    w = weichert_mle(k['mw'].to_numpy(float), yil, tablo, kenarlar=kenar, bas=bas_yil, son=son_yil)
    w['oran_4_95'] = w['A'] * 10.0 ** (-w['b'] * (4.95 - kenar[0]))
    w['n_olay'] = int(len(k))
    return w


def kur(izgara, kafes, kumesiz_k, kumesiz_m, *, bitis, k_komsu, kde_mmin, geysers,
        bas_yil=1981.0, mc_oran_ana=3.0, mc_oran_tum=3.0, mc_koseli=8.0, zemin=0.002, ad='K'):
    """Modeli [1981, bitis) verisiyle kur. kumesiz_k/m: aynı kesime kadar kümesizleştirme çıktısı.

    Döner: (ana şok modeli, artçı modeli); aynı şekil, farklı oran/b.
    """
    bitis = pd.Timestamp(bitis)
    bitis = bitis.tz_localize('UTC') if bitis.tzinfo is None else bitis.tz_convert('UTC')
    son_yil = bitis.year - 1
    eg = kumesiz_k
    if len(eg) != len(kumesiz_m) or (eg['zaman'] >= bitis).any():
        raise ModelHatasi('kümesiz maske kesimle uyuşmuyor ya da kesim sonrası olay var')
    ana = kumesiz_k[kumesiz_m].reset_index(drop=True)
    sin = (kafes.lon0, float(kafes.lon_kenar[-1]), kafes.lat0, float(kafes.lat_kenar[-1]))
    # KDE: kümesiz, derinlik<30, M>=kde_mmin; tampon dahil (bölge dışı olaylar çekirdek taşır).
    nok = ana[(ana['mw'] >= kde_mmin) & (ana['derinlik'] < 30.0)]
    if geysers:
        g = geysers_mi(nok['boylam'], nok['enlem']) & (nok['mw'] < 4.0)
        nok = nok[~g.to_numpy()]
    sg = bant_km(nok['boylam'].to_numpy(), nok['enlem'].to_numpy(), k_komsu)
    kut = kde_sekli(kafes, nok['boylam'].to_numpy(), nok['enlem'].to_numpy(), sg)
    sek = kafes.hucreye(kut)
    if sek.sum() <= 0:
        raise ModelHatasi('KDE kütlesi bölgede sıfır')
    sek = sek / sek.sum()
    sek = (1.0 - zemin) * sek + zemin / len(sek)
    wa = oran_kestir(ana, sin, bas_yil, son_yil, mc=mc_oran_ana)
    wt = oran_kestir(eg, sin, bas_yil, son_yil, mc=mc_oran_tum)
    meta = dict(k_komsu=k_komsu, kde_mmin=kde_mmin, geysers=bool(geysers), zemin=zemin,
                bitis=bitis.isoformat(), kde_n=int(len(nok)), mc_oran_ana=mc_oran_ana, mc_oran_tum=mc_oran_tum)
    m_ana = Kaliforniya(sek, izgara, b=wa['b'], rate_ust=wa['oran_4_95'], mc_koseli=mc_koseli,
                        ad=f'{ad}-ana', metadata=dict(meta, hedef='kumesiz', weichert_n=wa['n_olay']))
    m_art = Kaliforniya(sek, izgara, b=wt['b'], rate_ust=wt['oran_4_95'], mc_koseli=mc_koseli,
                        ad=f'{ad}-artci', metadata=dict(meta, hedef='tum', weichert_n=wt['n_olay']))
    return m_ana, m_art
