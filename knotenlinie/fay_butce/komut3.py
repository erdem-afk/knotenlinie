"""D3: kronolojik ağırlık ayarı, sabit düzgün-zemin kontrolü, iki İtalya eşiği."""
from __future__ import annotations

import argparse
import gc
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import hucre_indeks
from .butce import izgara_dogrula
from .etas import OrtakTaban, ETASFay, gunluk, ayarla, olcum
from .komut import _yaz
from .komut2 import katalog_oku
from .veri import fay_oku, sha256, DISS_SHA256

# Deney T Düzeltme 2 teslimi; eski-b veya koşuda değişmiş girdi kabul edilmez.
TESLIM = {
    'italya_katalog_le2015.csv': 'c3293da8f128920f0132736928218567d3ac516845a5651d19a92819a69925b9',
    'italya_izgara.csv': 'b503fd1c85721a5d225045e57c4ff3f0366d0887f9ebb1f893718c3c94cc0b41',
    'etas_italya_le2005.json': '5b5266fa0b01a297dc37d97cd723f85b61ac553329d57bb2a34901735098c72c',
    'etas_italya_le2010.json': 'a23c52366ffa90bb199819ebb99b256acd3b26391ac2341ff228246f5aa77510',
}
SIGMALAR = (5., 10., 20., 40.)
AYAR_BAS = pd.Timestamp('2006-01-01', tz='UTC')
AYAR_SON = pd.Timestamp('2011-01-01', tz='UTC')
SON = pd.Timestamp('2016-01-01', tz='UTC')


def zemin_sekli(izgara):
    """Ortak sabit metrikte alan payı; yalnız hedef maskenin toplamı korunur."""
    g = izgara_dogrula(izgara)
    area = (g[:, 1]-g[:, 0])*(g[:, 3]-g[:, 2])
    return area/area.sum()


def sec(tuning, keys):
    """Seçim yalnız [2006,2011) skorunu görür; düzgün zemin de aynı optimizer."""
    return ayarla(tuning['olay_taban'], {s: tuning['olay_fay'][k] for s, k in keys.items()},
                  tuning['toplam_taban'], {s: tuning['toplam_fay'][k] for s, k in keys.items()},
                  baslangic=AYAR_BAS, bitis=AYAR_SON)


def karisim_skoru(sample, key, w, *, esik, secim_esigi, b):
    """Ortak GR ile üst eşik: olay süzme + tüm λ'ya aynı GR çarpanı.

    Fay şekli seçim eşiğinde dondurulur. Ek M>=4.95 satırında ne sigma ne w
    yeniden seçilir. Bu, aynı uzaysal bileşenin büyüklükten bağımsızlık deneyidir.
    """
    if esik < secim_esigi or b <= 0:
        raise ValueError('üst eşik ve pozitif b gerekli')
    keep = sample['olay_mw'] >= esik
    factor = 10.**(-b*(esik-secim_esigi))
    a, f = sample['olay_taban'][keep], sample['olay_fay'][key][keep]
    nt, nf = sample['toplam_taban'], sample['toplam_fay'][key]
    # w=0 tam kimliği; w>0 için doğrusal günlük λ karışımı.
    event = a.copy() if w == 0 else (1-w)*a+w*f
    total = nt if w == 0 else (1-w)*nt+w*nf
    return event*factor, total*factor, a*factor, nt*factor


def puanla(sample, key, fit, control_fit, *, esik, secim_esigi, b):
    a, nm, base, nt = karisim_skoru(sample, key, fit['agirlik'], esik=esik,
                                    secim_esigi=secim_esigi, b=b)
    c, nc, _, _ = karisim_skoru(sample, 'zemin', control_fit['agirlik'], esik=esik,
                                secim_esigi=secim_esigi, b=b)
    return dict(**olcum(a, base, nm, nt),
                ortak_taban_karsi=olcum(a, base, nm, nt),
                kontrol_karsi=olcum(a, c, nm, nc),
                kontrol=dict(aday='ortak-ETAS+duzgun-zemin',
                             agirlik=control_fit['agirlik'], ayar=control_fit,
                             **olcum(c, base, nc, nt)))


def _girdi_kontrol(paths, expected):
    hashes = {k: sha256(v) for k, v in paths.items()}
    if hashes != expected:
        raise ValueError('D3 teslim SHA256 uyuşmuyor / koşu sırasında girdi değişti')
    return hashes


def _model(bolge, ortak, son, hashes):
    m = ayar_tabani(bolge, ortak, son=son)
    if (m.p['katalog_sha256'] != hashes['katalog'] or m.p['izgara_sha256'] != hashes['izgara']
            or m.ayar_son != pd.Timestamp(son, tz='UTC')):
        raise ValueError('D3 ortak ayar/katalog/ızgara kapısı')
    return m


def bolge_kos(bolge, ortak, fay_yolu, cikti):
    start = time.monotonic()
    if bolge != 'italya':
        raise ValueError(f'D3: yalnız italya tanımlı, {bolge!r} değil')
    esik = 3.95
    surum = 'DISS3.2.0'
    names = dict(katalog=f'{bolge}_katalog_le2015.csv', izgara=f'{bolge}_izgara.csv',
                 etas_ayar=f'etas_{bolge}_le2005.json', etas_dogrulama=f'etas_{bolge}_le2010.json')
    paths = {k: ortak/v for k, v in names.items()}
    paths['fay'] = fay_yolu
    expected = {k: TESLIM[v] for k, v in names.items()}
    expected['fay'] = DISS_SHA256
    hashes = _girdi_kontrol(paths, expected)
    cat = katalog_oku(paths['katalog'])
    grid = pd.read_csv(paths['izgara'])
    variants = {'tam': fay_oku(fay_yolu, surum=surum, en_gec=SON,
                               beklenen_sha256=expected['fay'])}
    variants['kaynak-le2010'] = fay_oku(fay_yolu, surum=surum, en_gec=AYAR_SON,
                                       beklenen_sha256=expected['fay'])
    train = _model(bolge, ortak, '2006-01-01', hashes)
    # Filtre yalnız ebeveyn üretkenliği sıfır satırları çıkarır, hedefleri değil.
    parents = cat[(cat.zaman >= train.baslangic) & (cat.mw >= train.mc)].copy()
    shapes = {'zemin': zemin_sekli(grid)}
    for variant, faults in variants.items():
        for s in SIGMALAR:
            shapes[(variant, s)] = ETASFay(OrtakTaban(train), faults, agirlik=1.,
                                           sigma_km=s, b=1., sekil_esik=esik).sekil(grid)
    tuning = gunluk(OrtakTaban(train), shapes, parents, grid, [esik, np.inf], AYAR_BAS, AYAR_SON,
                    hucre_esleyici=hucre_indeks)
    if tuning['dis']:
        raise ValueError('D3 ayar hedefi ızgara dışında')
    control_fit = sec(tuning, {0.: 'zemin'})  # 0 yalnız kontrolün tek şekil kimliği; sigma değil.
    control_fit.pop('sigma_km')
    for item in control_fit['adaylar']:
        item.pop('sigma_km')
    fits = {v: sec(tuning, {s: (v, s) for s in SIGMALAR}) for v in variants}
    train_start = train.baslangic
    train_meta = dict(mc=train.mc, b=train.b, dallanma=train.p['dallanma'],
                      arka_plan_bant_km=train.p['arka_plan']['bant_km'],
                      arka_plan_zemin_payi=train.p['arka_plan']['zemin_payi'])
    del train  # İki büyük anne×hücre cache'i aynı anda tutulmaz.
    gc.collect()
    validation_model = _model(bolge, ortak, '2011-01-01', hashes)
    if validation_model.mc != train_meta['mc'] or validation_model.baslangic != train_start:
        # İki teslimin ebeveyn penceresi farklıysa sessiz ortak filtre kullanma.
        raise ValueError('D3 iki tabanın ebeveyn filtresi farklı')
    selected_shapes = {'zemin': shapes['zemin']}
    selected_shapes.update({(v, f['sigma_km']): shapes[(v, f['sigma_km'])] for v, f in fits.items()})
    validation = gunluk(OrtakTaban(validation_model), selected_shapes, parents, grid, [esik, np.inf],
                        AYAR_SON, SON, hucre_esleyici=hucre_indeks)
    if validation['dis']:
        raise ValueError('D3 doğrulama hedefi ızgara dışında')
    _girdi_kontrol(paths, expected)
    rows = []
    for variant, fit in fits.items():
        key = (variant, fit['sigma_km'])
        # Kullanıma hazır arayüz ayarı: seçilen şekil, son=2011 tabanıyla.
        config_path = cikti/f'd3-{bolge}-{variant}'/'ayar.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)
        _yaz(config_path, dict(taban='ortak_etas', etas_fabrika='knotenlinie.fay_butce.etas:ortak_yukle',
                              etas_yolu=str(paths['etas_dogrulama'].resolve()),
                              fay_yolu=str(fay_yolu.resolve()), surum=surum, fay_sha256=expected['fay'],
                              kaynak_en_gec=(AYAR_SON if variant == 'kaynak-le2010' else SON).isoformat(),
                              agirlik=fit['agirlik'], sigma_km=fit['sigma_km'], b=1., sekil_esik=esik))
        for threshold in (3.95, 4.95):
            row = dict(aday=f'ETAS+{surum}-{variant}', bolge=bolge, esik=threshold,
                       m_kenarlar=[threshold, '+inf'], secim_esigi=esik,
                       agirlik=fit['agirlik'], sigma_km=fit['sigma_km'],
                       sigma_tanimli=fit['agirlik'] > 0, ayar=fit,
                       ayar_N=len(tuning['olay_taban']), ayar_baslangic=AYAR_BAS.isoformat(),
                       ayar_bitis=AYAR_SON.isoformat(), ayar_dis=tuning['dis'],
                       dogrulama_dis=validation['dis'], pencere=['2011-01-01', '2016-01-01'],
                       fay_sayisi=len(variants[variant]), izgara_hucre=len(grid),
                       kaynak_en_gec=(AYAR_SON if variant == 'kaynak-le2010' else SON).isoformat(),
                       ayar_dosyasi=str(config_path), kaynak_sha256=hashes,
                       etas_ayar=train_meta,
                       etas_dogrulama=dict(mc=validation_model.mc, b=validation_model.b,
                                          dallanma=validation_model.p['dallanma']),
                       durum='PROVISIONAL', birim='nat/olay', taban='ortak-duz-ETAS',
                       bagimsiz_inceleme='D3 skor kodu bekliyor',
                       notlar=['Fay şekli b=1 ve seçim eşiğinde sabit; yalnız arka plan karışır.',
                               'Ek İtalya satırı aynı w/sigma/şekille; yeniden seçim yok.',
                               'Kontrol aynı ayar bölmesinde seçilen, toplam-eşit düzgün alan arka planı.',
                               'p iki yönlü eşleştirilmiş T-test; kümelenme nedeniyle tanısal.',
                               'Taban: maskesiz MLE, aktif dallanma sınırı.',
                               'Tam DISS 2012 bilgisini içerebilir; le2010 geçmiş sürüm rekonstrüksiyonu değil.'])
            row.update(puanla(validation, key, fit, control_fit, esik=threshold,
                              secim_esigi=esik, b=validation_model.b))
            rows.append(row)
    elapsed = time.monotonic()-start
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform == 'darwin' else 1024)
    for row in rows:
        row['kosu'] = dict(duvar_saniye=elapsed, rss_tepe_byte=rss,
                           kucultme=False, gun_ayar=1826, gun_dogrulama=1826)
    print(f'{bolge}: {elapsed:.1f} saniye, RSS tepe {rss/1e9:.3f} GB', flush=True)
    return rows


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ortak', type=Path, required=True)
    p.add_argument('--diss', type=Path, required=True)
    p.add_argument('--cikti', type=Path, required=True)
    args = p.parse_args(argv)
    rows = []
    for bolge, source in [('italya', args.diss)]:
        rows.extend(bolge_kos(bolge, args.ortak, source, args.cikti))
        gc.collect()
    code = {str(f): sha256(f) for folder in ('knotenlinie/fay_butce', 'knotenlinie/ortak_zemin')
            for f in sorted(Path(folder).glob('*.py'))}
    for row in rows:
        row['kod_sha256'] = code
    _yaz(args.cikti/'OLCUM3.json', rows)
    print(args.cikti/'OLCUM3.json', flush=True)


if __name__ == '__main__':
    main()
