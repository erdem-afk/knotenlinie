"""Mevcut knotenlinie.etas yordamlarıyla ≤2010 uzay-zaman tabanı; ayar koduna dokunmaz."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.etas import katalog as K, model as M, tamlik
from .veri import AYAR_SON, katalog_oku, json_yaz, sha256
from knotenlinie.yollar import kod_ozeti
from .arka_plan import arka_plan_sec
from .mle import alt_kritik_mle


def buyukluk_cozunurlugu(mags):
    """En kaba tam ondalık ızgara; hiçbiri uymuyorsa fiilen sürekli (dm=0).

    Kısmi ızgara uyumu, dönüştürülmüş/sürekli katalogda yuvarlama kanıtı
    değildir. Yalnız float okuma toleransı kullanılır; bütün olaylar uymalı.
    """
    m = np.asarray(mags, float)
    if m.ndim != 1 or not len(m) or not np.isfinite(m).all():
        raise ValueError('Çözünürlük için dolu, sonlu büyüklük dizisi gerekli')
    unique = np.unique(m)
    if len(unique) < 2:
        raise ValueError('Tek büyüklükten çözünürlük ölçülemez')
    candidates = [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001]
    fractions = {f'{dm:g}': float(np.mean(np.isclose(
        m / dm, np.rint(m / dm), atol=1e-7, rtol=0))) for dm in candidates}
    dm = next((v for v in candidates if fractions[f'{v:g}'] == 1.0), 0.0)
    return {'dm': dm, 'n': len(m), 'tekil_n': len(unique),
            'en_kucuk_pozitif_fark': float(np.diff(unique).min()),
            'izgara_uyum_paylari': fractions, 'izgara_birimi_tolerans': 1e-7,
            'yontem': 'en kaba tam ondalık ızgara (1..1e-6); yoksa dm=0, fiilen sürekli'}


def b_ayarla(mags, mc):
    """Yalnız Mc üstü ayar olaylarının gerçek çözünürlüğüyle b/beta."""
    selected = np.asarray(mags, float)
    selected = selected[selected >= mc]
    resolution = buyukluk_cozunurlugu(selected)
    b = K.b_degeri(selected, mc, dm=resolution['dm'])
    b['cozunurluk'] = resolution
    if resolution['dm'] == 0:
        b['yontem'] = 'sürekli GR MLE (dm=0)'
    return b


def gr_ayar_paylari(mags, mc, b):
    """Büyük-M GR ekstrapolasyonunu yalnız ayar dönemindeki payla karşılaştır."""
    m = np.asarray(mags, float)
    m = m[m >= mc]
    rows = []
    for threshold in (3.95, 4.95):
        if threshold < mc:
            continue
        n = int(np.sum(m >= threshold))
        observed = n / len(m)
        gr = float(10 ** (-b * (threshold - mc)))
        rows.append({'m_alt': threshold, 'ayar_n': len(m), 'N': n,
                     'gozlenen_pay': observed, 'gr_pay': gr,
                     'gr_gozlenen_orani': gr / observed if n else None})
    return rows


def dallanma(parametreler, b):
    """Sonsuz düzlem/zaman ve kesilmemiş GR: K c^(1-p)/(p-1) b/(b-alpha)."""
    th = parametreler
    if not (b > th['alpha'] >= 0 and th['p'] > 1):
        return float('inf')
    return float(th['K'] * th['c'] ** (1 - th['p']) / (th['p'] - 1) * b / (b - th['alpha']))


def tamlik_sec(d, baslangic, floor):
    """Komut tamlik'in genel ve beş-yıllık MBS maksimumu; yalnız ayar olayları."""
    if d.empty or (d['zaman'] >= AYAR_SON).any():
        raise ValueError('Tamlık yalnız dolu ≤2010 ayar verisiyle')
    old = d.rename(columns={'zaman': 'time_utc', 'mw': 'mag'})
    overall = tamlik.mc_wiemer_wyss(d['mw'].to_numpy(float), baslangic=floor)
    windows = tamlik.pencere_araliklari(old, floor, bas_yil=baslangic)
    if not overall['kararli'] or any(w['mc'] is None and not w['yargilanmadi'] for w in windows):
        raise ValueError('MBS: b-kararlı tamlık yok')
    mc = max([overall['mc']] + [w['mc'] for w in windows if w['mc'] is not None])
    return {'mc': float(mc), 'genel': overall, 'pencereler': windows,
            'baslangic_yili': baslangic, 'arama_alt': floor,
            'yontem': 'knotenlinie.etas.tamlik: genel ve 5 yıllık MBS maksimumu'}


def ayarla(bolge, ortak, *, son='2011-01-01', maks_cift=None, maksiter=400, mc_alt=None):
    """Dışarıdan KDE yoğunluğu verilen mevcut MLE; knotenlinie.etas değişmez.

    Son sınırı hem Mc/b hem arka plan hem ETAS için geçerlidir. Mc eski
    teslimdeki 3.1/4.4 olarak korunur; bütçe aşımı Mc yükseltmez, reddeder.
    """
    end = pd.Timestamp(son)
    if end.tzinfo is None:
        end = end.tz_localize('UTC')
    if end not in (pd.Timestamp('2006-01-01', tz='UTC'), AYAR_SON):
        raise ValueError('Yalnız 2006/2011 ayar sonu desteklenir')
    suffix = f'le{end.year - 1}'
    start, floor = {'italya': (1985, 2.0)}[bolge]
    if maks_cift is None:
        maks_cift = {'italya': 30_000_000}[bolge]
    ortak = Path(ortak)
    catalog_path = ortak / f'{bolge}_katalog_le2015.csv'
    grid_path = ortak / f'{bolge}_izgara.csv'
    cat = katalog_oku(catalog_path)
    d = cat[(cat['zaman'] >= pd.Timestamp(f'{start}-01-01', tz='UTC')) & (cat['zaman'] < end)]
    completeness = tamlik_sec(d, start, floor)
    grid = pd.read_csv(grid_path)
    kutu = (grid['enlem_min'].min(), grid['enlem_max'].max(),
            grid['boylam_min'].min(), grid['boylam_max'].max())
    t = ((d['zaman'] - pd.Timestamp(f'{start}-01-01', tz='UTC')) / pd.Timedelta(days=1)).to_numpy(float)
    mags = d['mw'].to_numpy(float)
    T = float((end - pd.Timestamp(f'{start}-01-01', tz='UTC')) / pd.Timedelta(days=1))
    mc = float(mc_alt if mc_alt is not None else {'italya': 3.1}[bolge])
    if mc < completeness['mc']:
        raise ValueError('Mc tamlık sınırının altında')
    pairs = M.yaklasik_cift_sayisi(t[mags >= mc], pencere=T + 1)
    budget = {'mc': mc, 'n': int(np.sum(mags >= mc)), 'cift': pairs, 'yukseltildi': False}
    if pairs > maks_cift:
        raise ValueError('Çift bütçesi aşıldı; Mc korunur, bütçeyi açıkça artır')
    selected = mags >= mc
    ds = d.loc[selected]
    x, y = ds['boylam'].to_numpy(float), ds['enlem'].to_numpy(float)
    b = b_ayarla(mags, mc)
    hist = arka_plan_sec(ds, kutu, end)
    before = time.monotonic()
    print(f'{bolge}/{suffix}: Mc={mc}, N={len(ds)}, çift={budget["cift"]}, '
          f'KDE={hist["bant_km"]}km, zemin={hist["zemin_payi"]}', flush=True)
    fit = M.mle_uzay_zaman(t[selected], mags[selected], x, y, mc, b['beta'], 0.0, T,
                          kutu, M.arka_plan_degeri(x, y, hist), chunk=128, maksiter=maksiter)
    fit['optimizer'] = 'knotenlinie.etas MLE; L-BFGS-B'
    if fit['basari'] and not dallanma(fit['parametreler'], b['deger']) < 1:
        json_yaz(ortak / f'etas_{bolge}_{suffix}_serbest.json', fit)
        fit = alt_kritik_mle(t[selected], mags[selected], x, y, mc, b['beta'], b['deger'],
                            T, kutu, M.arka_plan_degeri(x, y, hist), fit,
                            maksiter=maksiter)
    seconds = time.monotonic() - before
    ratio = dallanma(fit['parametreler'], b['deger'])
    fit.update(bolge=bolge, mc=mc, b=b, baslangic_yili=start,
               ayar_baslangic=f'{start}-01-01T00:00:00Z', ayar_bitis=end.isoformat(),
               tamlik=completeness, mc_bilgi=budget, maks_cift=maks_cift,
               maksiter=maksiter, duvar_saniye=seconds, dallanma=ratio,
               dallanma_sonlu=bool(np.isfinite(ratio)), alt_kritik=bool(ratio < 1),
               dallanma_tanimi='sonsuz düzlem/zaman, kesilmemiş GR; alpha log10 katsayısı, alpha<b gerekli',
               kutu=list(kutu), arka_plan={k: v for k, v in hist.items()},
               katalog_sha256=sha256(catalog_path), izgara_sha256=sha256(grid_path),
               ayar_n=len(ds), ayar_max_zaman=ds['zaman'].max().isoformat(),
               gr_ayar_paylari=gr_ayar_paylari(mags, mc, b['deger']),
               kod_sha256=kod_ozeti([
                   'knotenlinie/etas/model.py', 'knotenlinie/etas/katalog.py', 'knotenlinie/etas/tamlik.py',
                   'knotenlinie/ortak_zemin/ayar.py', 'knotenlinie/ortak_zemin/arka_plan.py',
                   'knotenlinie/ortak_zemin/mle.py']),
               durum='PROVISIONAL; bağımsız skor-kodu incelemesi ve maskeli MLE kapısı açık',
               uzay_ayar_destegi='olaylar hedef maskede; MLE kompansatörü dış dikdörtgende (mevcut kod)',
               tahmin='günlük sabit geçmişli doğrudan tetikleme; pencere içi yeni kızlar eklenmez')
    attempt = ortak / f'etas_{bolge}_{suffix}_deneme_mc{mc:g}.json'
    json_yaz(attempt, fit)
    print(f'{bolge}: {seconds:.1f}s, basari={fit["basari"]}, dallanma={ratio}, param={fit["parametreler"]}', flush=True)
    if not fit['basari']:
        raise ValueError(f'MLE yakınsamadı; tanı {attempt}')
    if not ratio < 1:
        raise ValueError(f'Süperkritik MLE; kesme/parametre kırpma yapılmadı; tanı {attempt}')
    json_yaz(ortak / f'etas_{bolge}_{suffix}.json', fit)
    return fit
