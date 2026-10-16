"""Yan bölge kataloğu okuyucusu ve tamlık (dönem Mc + HKJ kısa süreli terim).

Yalnız `knotenlinie/yan_tezgah/indir.py`'nin yazdığı normalleştirilmiş dosyaları okur.
Mühür kapıları: dosya adı yılı < 2021 (açmadan), başlık birebir, satır yılı < 2021
(sonda bir kez daha). Bölge/derinlik süzgeci burada; KESIM = 2021-01-01.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.etas.tamlik import mc_maximum_egrilik, mc_wiemer_wyss
from .indir import BASLIK, BOLGELER, MuhurIhlali

KESIM = pd.Timestamp('2021-01-01', tz='UTC')
KUTU_DERINLIK = {b: (v['kutu'], v['maxdepth']) for b, v in BOLGELER.items()}


def _zaman_coz(s: str) -> pd.Timestamp:
    s = s.strip()
    if 'T' in s:
        return pd.Timestamp(s, tz='UTC')
    return pd.Timestamp(s.replace('/', '-'), tz='UTC')


def dosyalar(kok: Path, bolge: str, *, ilk_yil: int | None = None,
             son_yil: int | None = None) -> list[Path]:
    b = BOLGELER[bolge]
    ilk = b['ilk_yil'] if ilk_yil is None else ilk_yil
    son = b['son_yil'] if son_yil is None else son_yil
    yol = Path(kok) / 'deprem' / 'yan-bolge' / bolge
    out = []
    for y in range(ilk, son + 1):
        if y >= 2021:
            raise MuhurIhlali(f'{bolge}: yıl {y} mühürlü')
        p = yol / f"{b['onek']}_{y}.txt"
        if p.exists():
            out.append(p)
    return out


def _oku_dosya(path: Path, yil: int) -> list[dict]:
    if int(path.stem.split('_')[-1]) >= 2021:
        raise MuhurIhlali(f'{path.name}: dosya adı yılı mühürlü')
    satirlar = path.read_text(encoding='utf-8').splitlines()
    if not satirlar or satirlar[0] != BASLIK:
        raise MuhurIhlali(f'{path.name}: başlık birebir değil')
    kayit = []
    for satir in satirlar[1:]:
        if not satir.strip():
            continue
        hucre = satir.split('|')
        if len(hucre) != 14:
            continue
        if hucre[1].strip()[:4] == '':
            continue
        if int(hucre[1].strip()[:4]) >= 2021:
            raise MuhurIhlali(f'{path.name}: 2021+ satır görüldü')
        kayit.append(dict(event_id=hucre[0], zaman=_zaman_coz(hucre[1]),
                          enlem=float(hucre[2]), boylam=float(hucre[3]),
                          derinlik=float(hucre[4]), mag_type=hucre[9].strip() or '(bos)',
                          mw=float(hucre[10]), source=hucre[7] or hucre[5],
                          catalog_file=path.name))
    return kayit


def oku(kok, bolge: str, *, ilk_yil: int | None = None, son_yil: int | None = None,
        kutu_uygula: bool = True) -> pd.DataFrame:
    """Normalleştirilmiş yıllık dosyaları okur; kutu/derinlik süzgeci uygular."""
    kayit = []
    for p in dosyalar(Path(kok), bolge, ilk_yil=ilk_yil, son_yil=son_yil):
        kayit.extend(_oku_dosya(p, int(p.stem.split('_')[-1])))
    if not kayit:
        raise MuhurIhlali(f'{bolge}: dosya yok')
    df = pd.DataFrame(kayit).sort_values('zaman', kind='stable').reset_index(drop=True)
    if (df.zaman >= KESIM).any():
        raise MuhurIhlali(f'{bolge}: çerçevede 2021+ var')
    if kutu_uygula:
        (la0, la1, lo0, lo1), dmax = KUTU_DERINLIK[bolge]
        df = df[(df.boylam >= lo0) & (df.boylam < lo1) & (df.enlem >= la0) &
                (df.enlem < la1) & (df.derinlik >= 0) & (df.derinlik <= dmax)].reset_index(drop=True)
    return df


def cerceve_dogrula(df: pd.DataFrame) -> pd.DataFrame:
    s = ['zaman', 'enlem', 'boylam', 'derinlik', 'mw']
    c = df[s].copy()
    c['zaman'] = pd.to_datetime(c['zaman'], utc=True)
    if c.zaman.isna().any() or (c.zaman >= KESIM).any():
        raise MuhurIhlali('geçersiz/2021+ zaman')
    if not np.isfinite(c[['enlem', 'boylam', 'derinlik', 'mw']].to_numpy(float)).all():
        raise MuhurIhlali('eksik koordinat/derinlik/mw')
    return c.sort_values('zaman', kind='stable').reset_index(drop=True)


def izgara(bolge: str, dx: float = 0.1) -> pd.DataFrame:
    la0, la1, lo0, lo1 = BOLGELER[bolge]['kutu']
    boylam = np.round(np.arange(lo0, lo1, dx), 6)
    enlem = np.round(np.arange(la0, la1, dx), 6)
    grid = pd.DataFrame([(lo, lo + dx, la, la + dx) for la in enlem for lo in boylam],
                        columns=['boylam_min', 'boylam_max', 'enlem_min', 'enlem_max'])
    return grid


def _hk_j(t, mw, m_buyuk: float = 5.0, gun: float = 30.0):
    """Helmstetter-Kagan-Jackson 2006 kısa süreli Mc artışı (vektörel, O(N log M))."""
    t = np.asarray(t, float)
    mw = np.asarray(mw, float)
    buyuk = np.flatnonzero(mw >= m_buyuk)
    if buyuk.size == 0:
        return np.full(len(t), -np.inf)
    bt, bm = t[buyuk], mw[buyuk]
    out = np.full(len(t), -np.inf)
    for i in range(len(t)):
        # t_j < t_i ve 0 < dt <= gun
        lo = np.searchsorted(bt, t[i] - gun, side='right')
        hi = np.searchsorted(bt, t[i], side='left')
        if hi <= lo:
            continue
        dt = t[i] - bt[lo:hi]
        gecerli = dt > 0
        if not gecerli.any():
            continue
        dt = dt[gecerli]
        out[i] = float(np.max(bm[lo:hi][gecerli] - 4.5 - 0.75 * np.log10(dt)))
    return out


def donem_mc(df: pd.DataFrame, bas_yil: int, son_yil: int, yil: int = 5,
             n_min: int = 200, baslangic_mc: float | None = None) -> list[dict]:
    """5 yıllık pencerelerde MBS Mc; kararsız/az veride maksimum eğrilik + 0.2."""
    y = df['zaman'].dt.year.to_numpy()
    m = df['mw'].to_numpy(float)
    baslangiclar = list(range(bas_yil, son_yil + 1, yil))
    pencereler = []
    for i, a in enumerate(baslangiclar):
        bit = baslangiclar[i + 1] if i + 1 < len(baslangiclar) else son_yil + 1
        sec = (y >= a) & (y < bit)
        mm = m[sec]
        if mm.size < n_min:
            pencereler.append(dict(ad=f'{a}-{min(bit - 1, son_yil)}', bas_yil=a, bit_yil=bit,
                                   n=int(mm.size), mc=float(np.round(mc_maximum_egrilik(mm) + 0.2, 6)),
                                   yontem='MAXC+0.2 (n<n_min)', kararli=False))
            continue
        ww = mc_wiemer_wyss(mm, baslangic=baslangic_mc)
        if ww['kararli'] and ww['mc'] is not None:
            pencereler.append(dict(ad=f'{a}-{min(bit - 1, son_yil)}', bas_yil=a, bit_yil=bit,
                                   n=int(mm.size), mc=float(ww['mc']), yontem='MBS',
                                   kararli=True, mc_max_egrilik=ww['mc_maximum_egrilik']))
        else:
            mc = float(np.round(mc_maximum_egrilik(mm) + 0.2, 6))
            pencereler.append(dict(ad=f'{a}-{min(bit - 1, son_yil)}', bas_yil=a, bit_yil=bit,
                                   n=int(mm.size), mc=mc, yontem='MAXC+0.2 (kararsız)',
                                   kararli=False, mc_max_egrilik=ww['mc_maximum_egrilik']))
    return pencereler


def mc_t_serisi(df: pd.DataFrame, pencereler: list[dict]) -> np.ndarray:
    """Her olay için dönem Mc(t)."""
    y = df['zaman'].dt.year.to_numpy()
    mc = np.full(len(y), np.nan)
    for p in pencereler:
        sec = (y >= p['bas_yil']) & (y < p['bit_yil'])
        mc[sec] = p['mc']
    if np.isnan(mc).any():
        raise MuhurIhlali('dönem Mc(t) kapsamı dışı olay')
    return mc


def hkj_mc(df: pd.DataFrame, m_buyuk: float = 5.0, gun: float = 30.0) -> np.ndarray:
    t = ((df['zaman'] - pd.Timestamp('1970-01-01', tz='UTC')) / pd.Timedelta(days=1)).to_numpy(float)
    return _hk_j(t, df['mw'].to_numpy(float), m_buyuk=m_buyuk, gun=gun)


def tamlik(df: pd.DataFrame, bas_yil: int, son_yil: int, *, hkj: bool = True,
           m_buyuk: float = 5.0, gun: float = 30.0) -> dict:
    """Dönem Mc tablosu, olay başına Mc95 ve hedef eşiği (yukarı yuvarlı)."""
    pencereler = donem_mc(df, bas_yil, son_yil)
    dnm = mc_t_serisi(df, pencereler)
    mc_after = hkj_mc(df, m_buyuk=m_buyuk, gun=gun) if hkj else np.full(len(df), -np.inf)
    mc95 = np.maximum(dnm, mc_after)
    en_buyuk = max(p['mc'] for p in pencereler)
    hedef = float(np.ceil(np.round(en_buyuk + 0.2, 6) * 10) / 10)
    return dict(pencereler=pencereler, donem_mc=dnm, mc_after=mc_after, mc95=mc95,
                en_buyuk=en_buyuk, hedef=hedef,
                mc_min=float(min(p['mc'] for p in pencereler)))


def sayim(df: pd.DataFrame) -> dict:
    mt = df['mag_type'].value_counts().to_dict()
    return dict(N=int(len(df)), yil_ilk=int(df.zaman.dt.year.min()), yil_son=int(df.zaman.dt.year.max()),
                mag_turu={str(k): int(v) for k, v in mt.items()},
                kutle_basi_agirlikli=float(df.mw.mean()))
