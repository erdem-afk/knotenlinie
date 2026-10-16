"""≤2015 ortak İtalya kataloğu ve CSEP hücre desteği."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

from knotenlinie.etas import katalog as K

KOLONLAR = ['zaman', 'enlem', 'boylam', 'derinlik', 'mw']
IZGARA = ['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max']
SON = pd.Timestamp('2016-01-01', tz='UTC')
AYAR_SON = pd.Timestamp('2011-01-01', tz='UTC')
from knotenlinie.yollar import VERI  # noqa: E402  (data root: KNOTENLINIE_DATA)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for blok in iter(lambda: f.read(1024 * 1024), b''):
            h.update(blok)
    return h.hexdigest()


def json_yaz(path, obj):
    """Hessian'ın tanı NaN'larını null yaz; model sayıları ayrıca denetlenir."""
    def temiz(v):
        if isinstance(v, dict):
            return {str(k): temiz(x) for k, x in v.items()}
        if isinstance(v, (list, tuple, np.ndarray)):
            return [temiz(x) for x in v]
        if isinstance(v, (float, np.floating)):
            return float(v) if np.isfinite(v) else None
        if isinstance(v, np.integer):
            return int(v)
        return v
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(temiz(obj), ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def izgara_dogrula(izgara):
    g = izgara[IZGARA].to_numpy(float)
    if not len(g) or not np.isfinite(g).all():
        raise ValueError('Izgara boş/sonlu değil')
    w = g[:, 1] - g[:, 0]
    h = g[:, 3] - g[:, 2]
    if (w <= 0).any() or (h <= 0).any():
        raise ValueError('Izgara hücresi artan değil')
    if not np.allclose(w, w[0], atol=1e-9, rtol=0) or not np.allclose(h, h[0], atol=1e-9, rtol=0):
        raise ValueError('Bu okuyucu eş boyutlu düzenli hücreler ister')
    origin = np.array([g[:, 0].min(), g[:, 2].min()])
    size = np.array([w[0], h[0]])
    keys = (g[:, [0, 2]] - origin) / size
    if not np.allclose(keys, np.rint(keys), atol=1e-7, rtol=0):
        raise ValueError('Izgara hücreleri hizalı değil')
    keys = np.rint(keys).astype(int)
    if len(set(map(tuple, keys))) != len(g):
        raise ValueError('Izgara hücreleri tekrarlı')
    return g, origin, size, {tuple(k): i for i, k in enumerate(keys)}


def hucre_indeks(katalog, izgara):
    """Yarı açık [alt,üst) hücre; yalnız float yuvarlama için 1e-10 hücre toleransı."""
    _, origin, size, lookup = izgara_dogrula(izgara)
    xy = katalog[['boylam', 'enlem']].to_numpy(float)
    if not np.isfinite(xy).all():
        raise ValueError('Olay konumu sonlu değil')
    keys = np.floor((xy - origin) / size + 1e-10).astype(int)
    return np.array([lookup.get(tuple(k), -1) for k in keys], int)


def katalog_dogrula(df):
    d = df[KOLONLAR].copy()
    d['zaman'] = pd.to_datetime(d['zaman'], utc=True, format='mixed')
    if d['zaman'].isna().any() or (d['zaman'] >= SON).any():
        raise ValueError('Katalog zaman kapısı: eksik veya ≤2015 dışı satır')
    for k in KOLONLAR[1:]:
        d[k] = pd.to_numeric(d[k], errors='raise').astype(float)
    if not np.isfinite(d[KOLONLAR[1:]].to_numpy()).all():
        raise ValueError('Katalogda sonlu olmayan sayı')
    return d.sort_values('zaman', kind='stable').reset_index(drop=True)


def katalog_oku(path):
    return katalog_dogrula(pd.read_csv(path))


def csep_izgara(path):
    """Olay içermeyen tahmin XML'sinden mask=1 merkezlerin 0.1° hücreleri."""
    root = ET.parse(path).getroot()
    ns = {'c': root.tag.split('}')[0].lstrip('{')}
    data = root.find('c:forecastData', ns)
    dim = data.find('c:defaultCellDimension', ns)
    dx, dy = float(dim.attrib['lonRange']), float(dim.attrib['latRange'])
    layers = data.findall('c:depthLayer', ns)
    if len(layers) != 1:
        raise ValueError('CSEP tek derinlik katmanı gerekli')
    rows = []
    for cell in layers[0]:
        if cell.attrib.get('mask', '1') == '0':
            continue
        x, y = float(cell.attrib['lon']), float(cell.attrib['lat'])
        rows.append([x - dx / 2, x + dx / 2, y - dy / 2, y + dy / 2])
    grid = pd.DataFrame(np.round(rows, 12), columns=IZGARA)
    izgara_dogrula(grid)
    return grid


def kataloglari_yaz(horus, csep, cikti):
    """Önce ortak İtalya kataloğu teslim edilir; ham girdiler değişmez."""
    out = Path(cikti)
    out.mkdir(parents=True, exist_ok=True)
    grids = {'italya': csep_izgara(csep)}
    # Dosya-yıl kapısını glob yerine açık ≤2015 listeyle de koru.
    paths = [str(Path(horus) / f'horus_{y}.txt') for y in range(1960, 2016)]
    raw, report = K.horus_oku(paths)
    if report['atilan_kesim']:
        raise ValueError('HORUS kesim girdisi beklenmedik 2016+ satır içeriyor')
    italy = katalog_dogrula(raw.rename(columns={
        'time_utc': 'zaman', 'lat': 'enlem', 'lon': 'boylam', 'depth_km': 'derinlik', 'mag': 'mw'}))
    reports = {}
    for name, cat in [('italya', italy)]:
        grid = grids[name]
        idx = hucre_indeks(cat, grid)
        depth = 70
        take = (idx >= 0) & (cat['derinlik'] >= 0) & (cat['derinlik'] <= depth)
        selected = cat.loc[take].reset_index(drop=True)
        selected.to_csv(out / f'{name}_katalog_le2015.csv', index=False,
                        date_format='%Y-%m-%dT%H:%M:%S.%fZ')
        grid.to_csv(out / f'{name}_izgara.csv', index=False)
        reports[name] = {'n_girdi': len(cat), 'n': len(selected), 'hucre': len(grid),
                         'derinlik_ust_km': depth, 'ilk_zaman': selected['zaman'].min().isoformat(),
                         'son_zaman': selected['zaman'].max().isoformat(),
                         'katalog_sha256': sha256(out / f'{name}_katalog_le2015.csv'),
                         'izgara_sha256': sha256(out / f'{name}_izgara.csv')}
    reports['girdiler'] = {'horus': report, 'horus_sha256': {Path(p).name: sha256(p) for p in paths},
                           'csep': {'dosya': str(csep), 'sha256': sha256(csep)}}
    json_yaz(out / 'kataloglar.json', reports)
    return reports
