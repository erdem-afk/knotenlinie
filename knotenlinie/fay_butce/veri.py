"""Sürümü sabit DISS 3.2.0 üst kenar GeoJSON ve kesik CPTI15 okuyucuları."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .butce import iz_ornekle


def sha256(yol):
    h = hashlib.sha256()
    with open(yol, 'rb') as f:
        for parca in iter(lambda: f.read(1024*1024), b''):
            h.update(parca)
    return h.hexdigest()


DISS_SHA256 = '93b03567f22121c75ae1eabb2996d1b159a78264f6fdc0d1d2c61c54559d523a'
KOR_BAS = pd.Timestamp('2016-01-01', tz='UTC')


def kaynak_kapisi(faylar, baslangic):
    """Kör tahminde sabit sürüm hash'i ve en geç 2016 kaynak kesimi zorunlu."""
    if pd.Timestamp(baslangic) < KOR_BAS:
        return
    a = faylar.attrs
    kesim = a.get('kaynak_en_gec')
    if kesim is None or pd.Timestamp(kesim) > KOR_BAS:
        raise ValueError('kör koşu: --kaynak-en-gec 2016-01-01 veya daha erken gerekli')
    if a.get('surum') == 'DISS3.2.0' and a.get('sha256') != DISS_SHA256:
        raise ValueError('kör koşu: DISS3.2.0 sha256 uyuşmuyor')
    if a.get('surum') not in ('DISS3.2.0',):
        raise ValueError('kör koşu: kaynak sürümü bilinmiyor')


def fay_oku(yol, *, surum, en_gec=None, beklenen_sha256=None):
    """Yalnız CSS/crustal kaynakları; alan=L×(zmax-zmin)/sin(dip).

    DISS CSS ve ISS birbirine alternatif olduğundan ISS eklenmez. Üst kenar
    zmin derinliğindedir; yüzeye ekstrapolasyon yapılmaz. Bilinmeyen
    hız/Mmax/dip sessiz doldurulmaz; atılan kimlikler attrs'ta taşınır.
    """
    if surum not in ('DISS3.2.0',):
        raise ValueError('yalnız DISS3.2.0 sabit sürümü kabul edilir')
    dosya_hash = sha256(yol)
    if beklenen_sha256 is not None and dosya_hash != beklenen_sha256:
        raise ValueError(f'{surum}: sha256 uyuşmuyor')
    # CLI'deki 2016-01-01 kısa yazımı da UTC'dir; diğer kesimler de UTC'ye alınır.
    kesim = None if en_gec is None else pd.to_datetime(en_gec, utc=True)
    if kesim is not None and (kesim.tzinfo is None or pd.isna(kesim)):
        raise ValueError('kaynak tarih kesimi UTC bilinçli olmalı')
    d = json.loads(Path(yol).read_text(encoding='utf-8'))
    rows, atilan = [], []
    for f in d['features']:
        p = f['properties']
        kimlik = p['idsource']
        tarih = []
        for ad in ('created', 'updated'):
            t = str(p[ad])
            tarih.append(pd.to_datetime(t, format='%Y%m%d' if len(t)==8 else '%Y-%m-%d', utc=True))
        if max(tarih) >= pd.Timestamp('2021-01-01', tz='UTC'):
            raise ValueError(f'{kimlik}: mühürlü fay kaydı')
        if kesim is not None and max(tarih) >= kesim:
            atilan.append({'id': kimlik, 'neden': 'kaynak tarih kesimi'})
            continue
        g = f['geometry']
        if g['type'] not in ('LineString', 'MultiLineString'):
            raise ValueError(f'{kimlik}: üst kenar LineString olmalı')
        iz = g['coordinates'] if g['type']=='MultiLineString' else [g['coordinates']]
        try:
            v0, v1, dip0, dip1, z0, z1, mmax = [float(p[c]) for c in
                ('srmin', 'srmax', 'dipmin', 'dipmax', 'mindepth', 'maxdepth', 'maxmag')]
        except (TypeError, ValueError):
            atilan.append({'id': kimlik, 'neden': 'eksik sayısal alan'})
            continue
        if (not np.isfinite([v0,v1,dip0,dip1,z0,z1,mmax]).all()
                or not 0 <= v0 <= v1 or not 0 < dip0 <= dip1 <= 90
                or not 0 <= z0 < z1 or mmax <= 2.4):
            atilan.append({'id': kimlik, 'neden': 'geçersiz fiziksel alan'})
            continue
        _, _, L = iz_ornekle(iz)
        alan = L * (z1-z0) / np.sin(np.deg2rad((dip0+dip1)/2))
        rows.append(dict(id=kimlik, iz=iz, alan_km2=alan, kayma_mm_yil=(v0+v1)/2,
                         mmax=mmax, katman='CSS', surum=surum))
    sonuc = pd.DataFrame(rows, columns=['id','iz','alan_km2','kayma_mm_yil','mmax','katman','surum'])
    sonuc.attrs.update(atilan=atilan, kaynak_sayisi=len(d['features']), sha256=dosya_hash,
                       surum=surum, kaynak_en_gec=None if kesim is None else kesim.isoformat())
    return sonuc


def cpti_oku(yol, *, ilk_yil=1950):
    """≤2015 kesik CPTI15 kopyası; MwDef ve kesin günlü olaylar."""
    if Path(yol).name != 'CPTI15_v4.0_le2015.csv':
        raise ValueError('yalnız CPTI15_v4.0_le2015.csv kesik kopyası okunur')
    d = pd.read_csv(yol)
    if (d['Year'] >= 2016).any():
        raise ValueError('kesik CPTI dosyasında kör/mühürlü satır: dosyayı kullanmayın')
    d = d.loc[d.Year >= ilk_yil].copy()
    # Gün/ay eksikse uydurma tarih yok.
    d = d.dropna(subset=['Mo','Da','LatDef','LonDef','MwDef'])
    zaman = pd.to_datetime(dict(year=d.Year.astype(int), month=d.Mo.astype(int),
                                day=d.Da.astype(int)), utc=True, errors='coerce')
    sonuc = pd.DataFrame(dict(zaman=zaman, enlem=d.LatDef, boylam=d.LonDef,
                              derinlik=d.DepDef, mw=d.MwDef))
    return sonuc.dropna(subset=['zaman']).reset_index(drop=True)
