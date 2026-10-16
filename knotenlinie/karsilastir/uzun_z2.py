"""Experiment Z2 — uzun katalogdan Weichert toplam oranı × Z'nin şekli (İtalya).

Z2, Z'nin toplam oranını (kısa dönem M>=Mc verisinden kesik GR ile hedefe
taşınan) uzun bir kümesizleştirilmiş katalogdan Weichert (1980) ile kestirilen
M>=4.95 oranıyla değiştirir; uzaysal şekil Z'nin seçtiği şekildir (`UzunVade`
sekil dizisi birebir alınır). Tek önceden sabit model ve iki duyarlılık:

  (i)  b Weichert'ten değil Z'nin b'sinden;
  (ii) tamlık tablosu bir kademe (0,5) sıkı.

İtalya: CPTI15 <=2010 (MwDef, LatDef/LonDef), CSEP İtalya maskesi, GK74
kümesizleştirme; tamlık dönemleri yayımlanmış CPTI/Stucchi tablosundan
(`weichert.CPTI_TAMLIK`).

Ölçüm Z'nin `uzun_z.py` puanlayıcısını import eder: 2011-2015 (birincil ve iki
duyarlılık) ve 2006-2010 (<=2005 ile kurulmuş Weichert oranı) satırları;
kümesiz ve bütün olaylar; M>=4.95; HAZFX/TripleS/MPS04. 2016+ veri yok.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.karsilastir import uzun_z
from knotenlinie.karsilastir.puan import log_olabilirlik
from knotenlinie.uzun_vade.duzgunlestir import UzunVade, izgara_dogrula
from knotenlinie.uzun_vade.kumesiz import arka_plan_maskesi
from knotenlinie.uzun_vade.weichert import (CPTI_TAMLIK, gk74_mask,
                                      sikilastir, stepp_tamlik, weichert_mle)

from knotenlinie.yollar import KAYIT, KOSU, VERI  # noqa: E402

Z2_DIR = KOSU / 'Z2'       # new Z2 outputs
Z_DIR = KAYIT / 'Z'        # frozen Z record (shape selection), read only

#: Weichert büyüklük kutuları (0,1 ızgara); mref=4.95 kenardır.
WEI_KENAR = np.r_[np.round(np.arange(3.4, 8.6, 0.1), 2), np.inf]
#: MLE'yi hedefin altına taşımayan alt sınır (İtalya tablosu en düşük Mc=3.5).
ITA_KENAR = np.r_[np.round(np.arange(3.5, 8.6, 0.1), 2), np.inf]

BOLGELER = dict(uzun_z.BOLGELER)
DONEM_2011 = (uzun_z.utc('2011-01-01'), uzun_z.utc('2016-01-01'))
DONEM_2006 = (uzun_z.utc('2006-01-01'), uzun_z.utc('2011-01-01'))


def _maske_icinde(izgara, boylam, enlem):
    """Hücre alt köşelerine yuvarlanmış eşleşme; CSEP maskesi."""
    a = izgara_dogrula(izgara)
    anahtar = {(round(r[0], 6), round(r[2], 6)) for r in a}
    lo = np.round(np.floor(np.round(np.asarray(boylam, float), 6) * 10) / 10, 6)
    la = np.round(np.floor(np.round(np.asarray(enlem, float), 6) * 10) / 10, 6)
    return np.array([(x, y) in anahtar for x, y in zip(lo, la)])


def _yil_seri(yil, ay=None, gun=None):
    """Kesirli yıl (Weichert dönem ataması için); eksik ay/gün 1 alınır."""
    yil = np.asarray(yil, float)
    ay = np.ones_like(yil) if ay is None else np.nan_to_num(np.asarray(ay, float), nan=1.0)
    gun = np.ones_like(yil) if gun is None else np.nan_to_num(np.asarray(gun, float), nan=1.0)
    return yil + (ay - 1.0) / 12.0 + (gun - 1.0) / 365.25


def italya_katalog(son=2010):
    """CPTI15 <=son, MwDef, CSEP maskesi; GK74 maskesi ayrı döner."""
    p = VERI / 'kesik-2015/CPTI15_v4.0_le2015.csv'
    d = pd.read_csv(p, low_memory=False)
    if (pd.to_numeric(d.Year, errors='coerce') >= 2016).any():
        raise ValueError('CPTI15 dosyasında 2016+ satır var: reddedildi')
    d['mw'] = pd.to_numeric(d.MwDef, errors='coerce')
    d = d[d.mw.notna() & d.LatDef.notna() & d.LonDef.notna()
          & (pd.to_numeric(d.Year, errors='coerce') <= son)].copy()
    d['yil'] = pd.to_numeric(d.Year, errors='coerce')
    d['ay'] = pd.to_numeric(d.Mo, errors='coerce')
    d['gun'] = pd.to_numeric(d.Da, errors='coerce')
    d['enlem'] = d.LatDef.astype(float)
    d['boylam'] = d.LonDef.astype(float)
    d['derinlik'] = 0.0  # derinlik bilgisi eksik: bütün derinlikler
    izgara = pd.read_csv(BOLGELER['italya']['izgara'])
    d = d[_maske_icinde(izgara, d.boylam, d.enlem)].reset_index(drop=True)
    d['zaman_yil'] = _yil_seri(d.yil, d.ay, d.gun)
    return d


def italya_kumesiz(son=2010):
    d = italya_katalog(son)
    maske = gk74_mask(d.zaman_yil.to_numpy(), d.enlem.to_numpy(), d.boylam.to_numpy(),
                      d.derinlik.to_numpy(), d.mw.to_numpy())
    return d[maske].reset_index(drop=True), d


def weichert_kestir(bolge, kk, *, son, tablo=None):
    """Kümesiz katalogdan Weichert b ve M>=4.95 yıllık oranı."""
    if bolge != 'italya':
        raise ValueError(f'weichert_kestir: yalnız italya tanımlı, {bolge!r} değil')
    kenar = ITA_KENAR
    tablo = CPTI_TAMLIK if tablo is None else tablo
    y = kk.zaman_yil.to_numpy()
    return weichert_mle(kk.mw.to_numpy(), y, tablo, kenarlar=kenar, bas=1000, son=son)


def z_model(sekil, izgara, *, b, rate_m95, mmin, ad='Z2', meta=None):
    """Z'nin şekli × Weichert M>=4.95 oranı; rate_ust hedefe göre seçilir."""
    rate_ust = float(rate_m95) * 10.0 ** (float(b) * (4.95 - float(mmin)))
    return UzunVade(sekil, izgara, b=float(b), mmin=float(mmin), rate_ust=rate_ust,
                    ad=ad, metadata=dict(meta or {}, b=float(b), mmin=float(mmin),
                                         rate_ust=rate_ust, rate_m95=float(rate_m95)))


def _z_sekilleri(bolge, secim):
    """Z'nin seçtiği şekli Z'nin eğitim kataloğundan yeniden kurar (aynen)."""
    cfg = BOLGELER[bolge]
    katalog = uzun_z.katalog_oku(cfg['katalog'], cfg['derinlik'])
    d2010 = katalog[katalog.zaman < uzun_z.utc('2011-01-01')]
    izgara = pd.read_csv(cfg['izgara'])
    return uzun_z.model_sec(bolge, secim, d2010, izgara), izgara


def _donem_ekle(rows, donem):
    for r in rows:
        r['donem'] = donem
    return rows


def olc(bolge, *, bootstrap=2000, secim=None):
    """Z2 birincil model + iki duyarlılık (2011-2015) ve 2006-2010 satırları."""
    cfg = BOLGELER[bolge]
    izgara = pd.read_csv(cfg['izgara'])
    if secim is None:
        z = json.loads((Z_DIR / 'OLCUM.json').read_text(encoding='utf-8'))
        secim = z['bolgeler'][bolge]['secim']
    sh, _ = _z_sekilleri(bolge, secim)
    sekil = sh.sekil

    if bolge != 'italya':
        raise ValueError(f'olc: yalnız italya tanımlı, {bolge!r} değil')
    kk2010, kk_tum = italya_kumesiz(2010)
    kk2005, _ = italya_kumesiz(2005)

    w2010 = weichert_kestir(bolge, kk2010, son=2010)
    tablo_sik = sikilastir(CPTI_TAMLIK)
    w2010_sik = weichert_kestir(bolge, kk2010, son=2010, tablo=tablo_sik)
    w2005 = weichert_kestir(bolge, kk2005, son=2005)
    b_z = float(sh.b)

    modeller = {
        'birincil': z_model(sekil, izgara, b=w2010['b'], rate_m95=w2010['oran_mref'],
                            mmin=sh.mmin, ad='Z2-birincil', meta=w2010),
        'b_Z': z_model(sekil, izgara, b=b_z, rate_m95=w2010['oran_mref'],
                       mmin=sh.mmin, ad='Z2-birden-b-Z', meta=w2010),
        'sik_tablo': z_model(sekil, izgara, b=w2010_sik['b'], rate_m95=w2010_sik['oran_mref'],
                             mmin=sh.mmin, ad='Z2-sik-tablo', meta=w2010_sik),
    }
    rows = []
    t0, t1 = DONEM_2011
    # Z hedef çerçeveleri (Z'nin katalogları)
    katalog = uzun_z.katalog_oku(cfg['katalog'], cfg['derinlik'])
    tam_k, tam_mask = arka_plan_maskesi(katalog, 'gk74')
    hedef_kumesiz = tam_k[tam_mask]
    for ad, model in modeller.items():
        for tur, frame in (('kumesiz', hedef_kumesiz), ('tum', katalog)):
            rows += _donem_ekle(uzun_z.hedef_satirlari(
                cfg, bolge, model, izgara, cfg['m_kenarlar'], frame, tur,
                bootstrap, t0, t1), '2011-2015')
    rows2006 = []
    m2005 = z_model(sekil, izgara, b=w2005['b'], rate_m95=w2005['oran_mref'],
                    mmin=sh.mmin, ad='Z2-le2005', meta=w2005)
    t0b, t1b = DONEM_2006
    for tur, frame in (('kumesiz', hedef_kumesiz), ('tum', katalog)):
        rows2006 += _donem_ekle(uzun_z.hedef_satirlari(
            cfg, bolge, m2005, izgara, cfg['m_kenarlar'], frame, tur,
            bootstrap, t0b, t1b), '2006-2010')
    # Stepp yedeği (tanı; yalnız İtalya <=2005)
    stepp = None
    if bolge == 'italya':
        try:
            d2005 = italya_katalog(2005)
            stepp = stepp_tamlik(d2005.yil.to_numpy(), d2005.mw.to_numpy(), 2005)
        except Exception as exc:  # tanı; birincil sonucu etkilemez
            stepp = [['HATA', str(exc)]]

    ozet = dict(
        bolge=bolge, sekil_ozet=dict(min=float(sekil.min()), max=float(sekil.max()),
                                     toplam=float(sekil.sum())),
        z_b=b_z, z_mmin=sh.mmin, weichert2010=w2010, weichert2010_sik=w2010_sik,
        weichert2005=w2005, stepp=stepp,
        modeller={ad: dict(ad=m.ad, b=m.b, mmin=m.mmin, rate_ust=m.rate_ust,
                           rate_m95=m.metadata.get('rate_m95')) for ad, m in modeller.items()},
        satirlar=rows, satirlar_2006_2010=rows2006)
    ozet['italya_katalog_N'] = len(kk_tum)
    ozet['italya_kumesiz_N'] = len(kk2010)
    return ozet


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bolge', choices=['italya'], default='italya')
    p.add_argument('--cikti', type=Path, default=Z2_DIR / 'OLCUM.json')
    p.add_argument('--bootstrap', type=int, default=2000)
    args = p.parse_args(argv)
    bolgeler = [args.bolge]
    sonuc = {'surum': 1, 'tohum': uzun_z.TOHUM, 'bootstrap': args.bootstrap,
             'kural': 'records/Z2/KURAL.md', 'weichert_kenar': WEI_KENAR.tolist(),
             'bolgeler': {}}
    for b in bolgeler:
        sonuc['bolgeler'][b] = olc(b, bootstrap=args.bootstrap)
    args.cikti.parent.mkdir(parents=True, exist_ok=True)
    args.cikti.write_text(json.dumps(uzun_z.json_temiz(sonuc), ensure_ascii=False,
                                     indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(args.cikti)


if __name__ == '__main__':
    main()
