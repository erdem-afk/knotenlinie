"""2011–2015 günlük ileri ETAS hücre-Poisson logL; ayar/aday seçimi yapmaz."""
from __future__ import annotations

from pathlib import Path
import json
import resource
import sys
import time

import numpy as np
import pandas as pd
from scipy.special import gammaln, xlogy

from .arayuz import DuzETAS, model_yukle
from .veri import AYAR_SON, SON, VERI, hucre_indeks, json_yaz, katalog_oku, sha256


def poisson_logl(beklenen, sayim):
    """Bilinen cevap: sıfır oran+sıfır olay 0; pozitif olay+sıfır oran -inf."""
    r, n = np.asarray(beklenen, float), np.asarray(sayim, float)
    if r.shape != n.shape or not np.isfinite(r).all() or (r < 0).any() or not np.isfinite(n).all() or (
        n < 0).any() or not np.equal(n, np.floor(n)).all():
        raise ValueError('Poisson oran/sayım şekli, sonluluğu veya işareti geçersiz')
    return float(np.sum(xlogy(n, r) - r - gammaln(n + 1)))


def dogrula(bolge, ortak=VERI / 'ortak', *, m_kenarlar=(4.95, np.inf), ilerleme=True):
    """Her gün H_gün-başı kullanılır; gün içi ve ileri olaylar geçmişe girmez.

    Varsayılan tek [4.95,inf) kutusu; İtalya bileşen seçimi [3.95,inf).
    Çoklu kutular da aynı kodla çalışır; rapor kutu kenarlarını saklar.
    """
    started = time.monotonic()
    ortak = Path(ortak)
    model = model_yukle(bolge, ortak)
    grid = model.izgara
    cat_path = ortak / f'{bolge}_katalog_le2015.csv'
    if sha256(cat_path) != model.p['katalog_sha256']:
        raise ValueError('Katalog SHA256 ayar kaydıyla uyuşmuyor')
    cat = katalog_oku(cat_path)
    edges = np.asarray(m_kenarlar, float)
    parents = cat[(cat['zaman'] >= model.baslangic) & (cat['mw'] >= model.mc)].reset_index(drop=True)
    target = cat[(cat['zaman'] >= AYAR_SON) & (cat['zaman'] < SON) &
                 (cat['mw'] >= edges[0]) & (cat['mw'] < edges[-1])].reset_index(drop=True)
    cells = hucre_indeks(target, grid)
    if (cells < 0).any():
        raise ValueError('Doğrulama hedefi ızgara dışında')
    # Eski ham histogram boşluğu, yeni KDE boşluğundan ayrı raporlanır.
    train = parents[parents.zaman < AYAR_SON]
    train_cells = hucre_indeks(train, grid)
    if (train_cells < 0).any():
        raise ValueError('Ayar olayı hedef ızgara dışında')
    raw_counts = np.bincount(train_cells, minlength=len(grid))
    raw_empty_target = raw_counts[cells] == 0
    bg_mass = model._arka_plan(grid.to_numpy(float))
    bg_empty_target = bg_mass[cells] == 0
    archive = ortak / 'eski-b' / f'etas_{bolge}_le2010.json'
    old_bg = (DuzETAS(json.loads(archive.read_text()), grid)._arka_plan(grid.to_numpy(float))
              if archive.exists() else None)
    min_all, min_target, min_raw_empty_target = float('inf'), float('inf'), float('inf')
    magbins = np.searchsorted(edges, target['mw'].to_numpy(float), side='right') - 1
    days = np.floor(((target['zaman'] - AYAR_SON) / pd.Timedelta(days=1)).to_numpy(float)).astype(int)
    daycount = int((SON - AYAR_SON) / pd.Timedelta(days=1))
    logs, sums, rows = [], [], []
    for day in range(daycount):
        a = AYAR_SON + pd.Timedelta(days=day)
        z = a + pd.Timedelta(days=1)
        # Timestamp searchsorted, pandas 2/3 biriminden bağımsız.
        stop = int(parents['zaman'].searchsorted(a, side='left'))
        history = parents.iloc[:stop]
        rates = model.beklenen(a, z, history, grid, edges)
        counts = np.zeros(rates.shape, int)
        obs = days == day
        np.add.at(counts, (cells[obs], magbins[obs]), 1)
        target_rates = rates[cells[obs], magbins[obs]]
        former_empty_rates = target_rates[raw_empty_target[obs]]
        min_all = min(min_all, float(rates.min()))
        if len(target_rates):
            min_target = min(min_target, float(target_rates.min()))
        if len(former_empty_rates):
            min_raw_empty_target = min(min_raw_empty_target, float(former_empty_rates.min()))
        logl = poisson_logl(rates, counts)
        expectation = float(rates.sum())
        logs.append(logl); sums.append(expectation)
        rows.append({'baslangic': a.isoformat(), 'N': int(obs.sum()), 'beklenen_toplam': expectation,
                     'logL': logl, 'sifir_oran_hedef': int(((counts > 0) & (rates == 0)).sum()),
                     'lambda_min': float(rates.min()),
                     'lambda_min_hedef': float(target_rates.min()) if len(target_rates) else None,
                     'ham_histogram_bos_hedef': int(raw_empty_target[obs].sum())})
        if ilerleme and (day % 365 == 0 or day == daycount - 1):
            rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)
            print(f'{bolge}: gün={day+1}/{daycount}, logL={sum(logs):.6f}, Lambda={sum(sums):.6f}, '
                  f'RSS_tepe_MB={rss / 1e6:.1f}, cache_anne={len(model._keys)}', flush=True)
    total = float(np.sum(logs))
    result = {'aday': 'ortak-duz-ETAS', 'bolge': bolge, 'N': len(target),
              'logL': total, 'logL_sonlu': bool(np.isfinite(total)),
              'beklenen_toplam': float(np.sum(sums)), 'IG': None, 'SE': None, 'p': None,
              'IG_notu': 'taban satırı; kendine karşı kazanç hesaplanmaz',
              'baslangic': AYAR_SON.isoformat(), 'bitis_haric': SON.isoformat(),
              'gun': daycount, 'hucre': len(grid),
              'm_kenarlar': [float(v) if np.isfinite(v) else '+inf' for v in edges],
              'skor': 'günlük bağımsız hücre×büyüklük Poisson; log(n!) dahil, koşullu toplam değil',
              'zaman_adimi': 'gün başında sabit geçmiş; gün içi kızlar eklenmez',
              'dallanma': model.p['dallanma'], 'mc': model.mc, 'b': model.b,
              'b_dm': model.p['b']['dm'],
              'bilesen_dogrulama': bool(np.array_equal(edges, [
                  3.95 if bolge == 'italya' else 4.95, np.inf])),
              'baslangic_yili': model.p['baslangic_yili'],
              'parametre_sha256': sha256(ortak / f'etas_{bolge}_le2010.json'),
              'katalog_sha256': sha256(cat_path), 'izgara_sha256': model.p['izgara_sha256'],
              'durum': model.p['durum'],
              'duvar_saniye': time.monotonic() - started,
              'rss_tepe_byte': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss *
                               (1 if sys.platform == 'darwin' else 1024),
              'kod_sha256': {str(p): sha256(p) for p in map(Path, [
                  'knotenlinie/ortak_zemin/arayuz.py', 'knotenlinie/ortak_zemin/dogrulama.py'])},
              'arka_plan_bant_km': model.p['arka_plan']['bant_km'],
              'arka_plan_zemin_payi': model.p['arka_plan']['zemin_payi'],
              'arka_plan_bos_hucre': int(np.sum(bg_mass == 0)),
              'arka_plan_bos_hedef': int(bg_empty_target.sum()),
              'ham_histogram_bos_hucre': int(np.sum(raw_counts == 0)),
              'ham_histogram_bos_hedef': int(raw_empty_target.sum()),
              'eski_b_histogram_sifir_hedef': int(np.sum(old_bg[cells] == 0)) if old_bg is not None else None,
              'eski_b_histogram_ihmal_edilebilir_hedef': int(np.sum(old_bg[cells] < 1e-12)) if old_bg is not None else None,
              'eski_b_parametre_sha256': sha256(archive) if old_bg is not None else None,
              'bosluk_notu': 'ham: hizalı hücrede ayar olayı yok; eski-b: eski float histogram integrali tam 0. '
                             'Eski kenar sliver kütleleri ~1e-16 olduğundan iki sayı farklı olabilir',
              'lambda_min': min_all,
              'lambda_min_hedef': min_target if len(target) else None,
              'lambda_min_ham_bos_hedef': min_raw_empty_target if raw_empty_target.any() else None,
              'lambda_birimi': 'günlük hücre×büyüklük beklenen sayısı (Poisson lambda)',
              'sifir_oran_hedef': sum(r['sifir_oran_hedef'] for r in rows)}
    # Farklı büyüklük kutularının günlük ölçümleri birbirini ezmez.
    suffix = '' if np.array_equal(edges, [4.95, np.inf]) else '_m' + '_'.join(
        f'{v:g}' if np.isfinite(v) else 'inf' for v in edges)
    json_yaz(ortak / f'dogrulama_{bolge}_2011_2015{suffix}.json', {'ozet': result, 'gunluk': rows})
    return result
