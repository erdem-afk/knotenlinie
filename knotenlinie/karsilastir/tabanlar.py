"""CSEP XML oran okuyucusu; olay dosyası okunmaz."""
from __future__ import annotations

from dataclasses import dataclass
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from .kosucu import IZGARA, utc, geometri
from .puan import PuanHatasi, oranlar

YIL_GUN = 365.25


@dataclass
class IzgaraTabani:
    ad: str
    izgara: pd.DataFrame
    m_kenarlar: np.ndarray
    yillik: np.ndarray
    metadata: dict

    def __post_init__(self):
        self.izgara = self.izgara[IZGARA].reset_index(drop=True).copy()
        _, self.m_kenarlar = geometri(self.izgara, self.m_kenarlar)
        self.yillik = oranlar(self.yillik).copy()
        if self.yillik.shape != (len(self.izgara), len(self.m_kenarlar) - 1):
            raise PuanHatasi('Taban oran şekli ızgara/büyüklükle eşleşmiyor')

    def buyukluk_kutula(self, m_kenarlar, *, kutu_ici_duzgun=False, sifir_ust_kuyruk=False):
        """Açık varsayımla korunumlu büyüklük yeniden kutulaması.

        Kapalı kutuda sabit büyüklük yoğunluğu; sonlu kaynak üst sınırı
        üstündeki sıfır oran ayrıca onay ister. Açık kaynak kuyruğu bölünmez.
        Bu işlem yayın modelinin kendisi değil, dondurulacak adaptasyonudur.
        """
        if not kutu_ici_duzgun:
            raise PuanHatasi('Kutu içi düzgün büyüklük yoğunluğu açıkça kabul edilmeli')
        _, m = geometri(self.izgara, m_kenarlar)
        src = self.m_kenarlar
        if not np.isfinite(src).all():
            raise PuanHatasi('Açık kaynak kuyruğu düzgün yoğunlukla bölünemez')
        if m[0] < src[0]:
            raise PuanHatasi('Kaynağın alt eşiğine ekstrapolasyon yok')
        if m[-1] > src[-1] and not sifir_ust_kuyruk:
            raise PuanHatasi('Sonlu kaynak üstündeki sıfır kuyruk açıkça kabul edilmeli')
        overlap = np.maximum(0, np.minimum(m[1:, None], src[None, 1:]) -
                             np.maximum(m[:-1, None], src[None, :-1]))
        w = overlap / np.diff(src)[None, :]
        meta = dict(self.metadata, buyukluk_adaptasyonu='kapalı kaynak kutusunda düzgün yoğunluk',
                    sifir_ust_kuyruk=bool(sifir_ust_kuyruk), kaynak_m_kenarlar=src.tolist())
        yillik = self.yillik @ w.T
        return IzgaraTabani(self.ad + '-M-adapte', self.izgara, m, yillik, meta)

    def beklenen(self, baslangic, bitis, gecmis, izgara, m_kenarlar):
        """Yıllık oran * gün/365.25; yalnız tam hizalı alt ızgara/kutular.

        Mekân veya büyüklük kutularını kaydırmak sessiz interpolasyon değildir:
        ayrı, dondurulmuş ve testli yeniden ızgaralama gerektirir.
        """
        a, b = utc(baslangic), utc(bitis)
        if a >= b:
            raise PuanHatasi('Taban penceresi artan olmalı')
        g, m = geometri(izgara, m_kenarlar)
        kaynak = np.round(self.izgara[IZGARA].to_numpy(float), 12)
        indeks = {tuple(row): i for i, row in enumerate(kaynak)}
        try:
            idx = np.array([indeks[tuple(row)] for row in g], int)
        except KeyError as e:
            raise PuanHatasi('Tabanla aynı hücre sınırları gerekli') from e
        kenarlar = np.round(self.m_kenarlar, 12)
        m = np.round(m, 12)
        jdx = []
        for edge in m:
            match = np.flatnonzero(kenarlar == edge)
            if len(match) != 1:
                raise PuanHatasi(f'Tabanda büyüklük kenarı yok: {edge}')
            jdx.append(match[0])
        out = np.column_stack([self.yillik[idx, j:k].sum(axis=1) for j, k in zip(jdx[:-1], jdx[1:])])
        return out * float((b - a) / pd.Timedelta(days=1)) / YIL_GUN


def csep_xml(path, *, sure_yil):
    """Oranların birimi zorunlu: XML tarihleri/adı otomatik birim sayılmaz."""
    if not np.isfinite(sure_yil) or sure_yil <= 0:
        raise PuanHatasi('Kaynak forecast_unit pozitif olmalı')
    root = ET.parse(path).getroot()
    ns = {'c': root.tag.split('}')[0].lstrip('{')}
    d = root.find('c:forecastData', ns)
    if d is None:
        raise PuanHatasi('CSEP forecastData bulunamadı')
    text = lambda k: d.findtext('c:' + k, namespaces=ns)
    issue = utc(text('issueDate'))
    if issue >= pd.Timestamp('2016-01-01', tz='UTC'):
        raise PuanHatasi('2016+ yayımlı taban kabul edilmez; kalibrasyon kanıtı gerekli')
    dim = d.find('c:defaultCellDimension', ns)
    dx, dy = float(dim.attrib['lonRange']), float(dim.attrib['latRange'])
    dm = float(text('defaultMagBinDimension'))
    layers = d.findall('c:depthLayer', ns)
    if len(layers) != 1:
        raise PuanHatasi('Bir derinlik katmanı gerekli; sessiz toplama yok')
    cells, rates, mags = [], [], None
    for c in layers[0]:
        if c.attrib.get('mask', '1') == '0':
            continue
        lon, lat = float(c.attrib['lon']), float(c.attrib['lat'])
        bins = c.findall('c:bin', ns)
        mm = np.array([float(x.attrib['m']) for x in bins])
        if mags is None:
            mags = mm
        if not np.array_equal(mm, mags):
            raise PuanHatasi('CSEP hücre büyüklük kutuları farklı')
        cells.append([lon - dx / 2, lon + dx / 2, lat - dy / 2, lat + dy / 2])
        rates.append([float(x.text) for x in bins])
    if mags is None or (len(mags) > 1 and not np.allclose(np.diff(mags), dm)):
        raise PuanHatasi('CSEP büyüklük adımı eksik/düzensiz')
    edges = np.round(np.r_[mags - dm / 2, mags[-1] + dm / 2], 12)
    if text('lastMagBinOpen') == '1':
        edges[-1] = np.inf
    grid = pd.DataFrame(np.round(cells, 12), columns=IZGARA)
    geometri(grid, edges)
    yillik = oranlar(rates) / sure_yil
    metadata = dict(issueDate=issue.isoformat(), forecastStartDate=text('forecastStartDate'),
                    forecastEndDate=text('forecastEndDate'), forecast_unit_yil=float(sure_yil),
                    derinlik_min=float(layers[0].attrib['min']), derinlik_max=float(layers[0].attrib['max']),
                    derinlik_tanimi='CSEP XML depthLayer [min,max)',
                    kalibrasyon_ust_sinir=issue.isoformat(),
                    kalibrasyon_notu='Yayın tarihi üst sınırdır; katalog kesimi kaynak fişinde ayrı teyit edilir')
    return IzgaraTabani(text('modelName'), grid, edges, yillik, metadata)

