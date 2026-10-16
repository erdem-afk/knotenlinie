"""Experiment Z — uzun vadeli benzer-benzere ölçüm (İtalya).

Kümesizleştirilmiş 2011-2015 hedeflerinde (İtalya HORUS-Mw) ve bütün olaylarda,
seçilen uzun vadeli model ile yerleşik tabanları (CSEP İtalya HAZFX/TripleS/MPS04)
karşılaştırır. Tek 5 yıllık dönem; hücre×kutu Poisson logL, olay başına bilgi
kazancı (IG), olay yeniden örneklemeli bootstrap SE, N/S/M ve güç beyanı.

Yerleşik modeller yalnız M>=4.95'te yayımlanmıştır (CSEP XML taban kutuları
4.95'ten başlar). Bu nedenle hüküm satırları M>=4.95'tir; geliştirme eşiğindeki
(M>=3.95) satırlar düzgün alan sıfırına karşıdır. Donmuş okuyucu (`csep_xml`)
değiştirilmez. U3 (GEAR1 şekli) adayı bu sürümde kapalıdır; donmuş Z kaydında
ağırlığı 0'dır, seçilen İtalya şekli (U0) değişmez.

Girdi ≤2015; 2016+ veri okunmaz. Donmuş kayıt `records/Z/`'den okunur, yeni
çıktılar `$KNOTENLINIE_RUNS/Z/` altına yazılır.
"""
from __future__ import annotations

import argparse
import functools
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from knotenlinie.karsilastir.kosucu import olay_kutulari
from knotenlinie.karsilastir.puan import log_olabilirlik, tutarlilik
from knotenlinie.karsilastir.tabanlar import csep_xml
from knotenlinie.uzun_vade.duzgunlestir import (UzunVade, fay_sekli,
                                          izgara_dogrula, karistir, kur)
from knotenlinie.uzun_vade.kumesiz import arka_plan_maskesi
from knotenlinie.fay_butce.veri import fay_oku

from knotenlinie.yollar import KAYIT, KOSU, VERI  # noqa: E402

Z_DIR = KAYIT / 'Z'        # frozen Z record (shape selection), read only
Z_CIKTI = KOSU / 'Z'       # new Z outputs

M_ITALYA = np.r_[np.round(np.arange(3.95, 9.0, 0.1), 2), np.inf]
M_TABAN = np.r_[np.round(np.arange(4.95, 9.0, 0.1), 2), np.inf]

BOLGELER = {
    'italya': dict(
        katalog=VERI / 'ortak/italya_katalog_le2015.csv',
        izgara=VERI / 'ortak/italya_izgara.csv',
        derinlik=(0.0, 30.0), mmin=3.1, egitim_baslangic='1985-01-01',
        esik_gelistirme=3.95, m_kenarlar=M_ITALYA,
        fay=VERI / 'diss320/csstop320.geojson',
        tabanlar=[('HAZFX', VERI / 'tabanlar/akinci.HAZFX_BPT.italy.10yr.2010-01-01.xml'),
                  ('TripleS', VERI / 'tabanlar/zechar.TripleS-CPTI.italy.10yr.2010-01-01.xml'),
                  ('MPS04', VERI / 'tabanlar/meletti.MPS04.italy.10yr.2010-01-01.xml')]),
}

ADAY_AG = {'U0': [10.0, 20.0, 40.0], 'U1': [10, 20, 40]}
W_AGIRLIK = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
ZEMIN = 0.002
TOHUM = 20261005
BOOTSTRAP = 2000


def utc(s):
    return pd.Timestamp(s, tz='UTC')


def katalog_oku(yol, derinlik):
    d = pd.read_csv(yol)
    if (d['zaman'].str[:4].astype(int) >= 2016).any():
        raise ValueError('katalogda 2016+ satır var: dosya reddedildi')
    d['zaman'] = pd.to_datetime(d['zaman'], utc=True)
    return d[(d.derinlik >= derinlik[0]) & (d.derinlik < derinlik[1])].reset_index(drop=True)


def taban_yukle(ad, yol):
    return _taban_yukle(ad, str(yol))


@functools.lru_cache(maxsize=8)
def _taban_yukle(ad, yol):
    return csep_xml(Path(yol), sure_yil=10)


def hedefler(kat, izgara, m_kenarlar, derinlik, t0, t1):
    a = kat[(kat.zaman >= t0) & (kat.zaman < t1)]
    a, ci, mi = olay_kutulari(a, izgara, m_kenarlar, derinlik)
    return a, ci, mi


def poisson_logl(beklenen, gozlem):
    return log_olabilirlik(beklenen, gozlem)


def olay_ig(lam_aday, lam_taban, lam_aday_top, lam_taban_top, *,
            tekrar=BOOTSTRAP, tohum=TOHUM):
    """Olay yeniden örneklemeli IG ve bootstrap SE; olay/integral payları ayrı."""
    a = np.asarray(lam_aday, float)
    b = np.asarray(lam_taban, float)
    n = len(a)
    if n == 0:
        return dict(N=0, IG=None, IG_olay=None, integral=None, SE_blok=None,
                    z=None, p_tek=None, guc=None, durum='N=0')
    if (a <= 0).any() or (b <= 0).any():
        return dict(N=n, IG=None, IG_olay=None, integral=None, SE_blok=None,
                    z=None, p_tek=None, guc=None, durum='tanımsız',
                    sebep='gözlemli sıfır oran')
    x = np.log(a) - np.log(b)
    integral = float(lam_aday_top - lam_taban_top)
    ig = float(x.mean() - integral / n)
    rng = np.random.default_rng(tohum)
    idx = rng.integers(0, n, size=(int(tekrar), n))
    ig_b = x[idx].mean(axis=1) - integral / n
    se = float(np.std(ig_b, ddof=1))
    z = ig / se if se > 0 else (0.0 if ig == 0 else float(np.copysign(np.inf, ig)))
    return dict(N=n, IG=ig, IG_olay=float(x.mean()), integral=-integral,
                SE_blok=se, z=float(z), p_tek=float(stats.norm.sf(z)),
                guc=float(stats.norm.cdf(ig / se - 1.645)) if se > 0 else None,
                durum='tanımlı')


def _gozlem_matris(shape, ci, mi):
    o = np.zeros(shape, dtype=int)
    np.add.at(o, (ci, mi), 1)
    return o


def _uniform(beklenen_top, izgara):
    a = izgara_dogrula(izgara)
    lat = 0.5 * (a[:, 2] + a[:, 3])
    alan = np.cos(np.deg2rad(lat)) * (a[:, 1] - a[:, 0]) * (a[:, 3] - a[:, 2])
    return beklenen_top * alan / alan.sum()


def _k_from_ad(ad):
    return int(ad.split('k')[-1])


def _olsun(sekil, temel, ad):
    return UzunVade(sekil, temel.izgara, b=temel.b, mmin=temel.mmin,
                    rate_ust=temel.rate_ust, ad=ad, metadata=dict(temel.metadata, karisim_ad=ad))


def sec_model(bolge, katalog, izgara, hedef_kat):
    """≤2005 ile adayları kur, 2006-2010 logL'iyle U0-U3 ve ağırlıkları seç."""
    cfg = BOLGELER[bolge]
    edges, mmin = cfg['m_kenarlar'], cfg['mmin']
    bas, ayar_son = utc(cfg['egitim_baslangic']), utc('2006-01-01')
    eg = katalog[katalog.zaman >= bas]
    kayit, adaylar = {}, {}
    for sigma in ADAY_AG['U0']:
        m = kur(eg, izgara, mmin=mmin, m_kenarlar=edges, baslangic=bas, bitis=ayar_son,
                bant_km=sigma, zemin_payi=ZEMIN, ad=f'U0-{sigma:g}')
        adaylar[m.ad] = m
    for k in ADAY_AG['U1']:
        m = kur(eg, izgara, mmin=mmin, m_kenarlar=edges, baslangic=bas, bitis=ayar_son,
                k_komsu=k, zemin_payi=ZEMIN, ad=f'U1-k{k}')
        adaylar[m.ad] = m
    _, ci, mi = hedefler(hedef_kat, izgara, edges, cfg['derinlik'], utc('2006-01-01'),
                         utc('2011-01-01'))
    obs = _gozlem_matris((len(izgara), len(edges) - 1), ci, mi)
    j = int(np.searchsorted(edges, cfg['esik_gelistirme'], side='right') - 1)

    def skor(model):
        return poisson_logl(model.beklenen(utc('2006-01-01'), utc('2011-01-01'), None,
                                           izgara, edges)[:, j:], obs[:, j:])

    def sec(adaylar_):
        en = max(adaylar_, key=lambda a_: skor(adaylar[a_]))
        return en, {a_: skor(adaylar[a_]) for a_ in adaylar_}

    u0, kayit_u0 = sec([a_ for a_ in adaylar if a_.startswith('U0')])
    u1, kayit_u1 = sec([a_ for a_ in adaylar if a_.startswith('U1')])
    temel = adaylar[u1]
    kayit['U0'] = dict(ad=u0, logL=kayit_u0[u0], adaylar=kayit_u0)
    kayit['U1'] = dict(ad=u1, logL=kayit_u1[u1], adaylar=kayit_u1)
    ozellik = {}
    if cfg.get('fay'):
        faylar = fay_oku(cfg['fay'], surum='DISS3.2.0')
        ozellik['U2'] = fay_sekli(izgara, edges, faylar, esik=cfg['esik_gelistirme'])
    for ad, sek in ozellik.items():
        en_iyi, en_iyi_w, kayit_w = None, None, {}
        for w in W_AGIRLIK:
            m = _olsun(karistir(temel.sekil, sek, w), temel, f'{ad}-w{w:g}')
            s = skor(m)
            kayit_w[m.ad] = s
            if en_iyi is None or s > en_iyi:
                en_iyi, en_iyi_w = s, w
        kayit[ad] = dict(w=en_iyi_w, logL=en_iyi, adaylar=kayit_w, ad=f'{ad}-w{en_iyi_w:g}')
    for ad in ('U2', 'U3'):
        if ad not in kayit:
            kayit[ad] = None
    final = [(x, kayit[x]['logL']) for x in ('U0', 'U1', 'U2', 'U3') if kayit.get(x)]
    kayit['secili'] = max(final, key=lambda t: t[1])[0]
    return kayit


def model_sec(bolge, secim, katalog, izgara, yontem='gk74'):
    """Seçilen modeli ≤2010 verisiyle yeniden kur; yontem kümesizleştirme yöntemi."""
    cfg = BOLGELER[bolge]
    edges, mmin = cfg['m_kenarlar'], cfg['mmin']
    bas, son = utc(cfg['egitim_baslangic']), utc('2011-01-01')
    eg = katalog[katalog.zaman >= bas]
    ad = secim['secili']
    ortak = dict(mmin=mmin, m_kenarlar=edges, baslangic=bas, bitis=son, zemin_payi=ZEMIN,
                 yontem=yontem)
    if ad == 'U0':
        return kur(eg, izgara, bant_km=float(secim['U0']['ad'].split('-')[1]),
                   ad='U0-secili', metadata=dict(secim=ad, yontem=yontem), **ortak)
    temel = kur(eg, izgara, k_komsu=_k_from_ad(secim['U1']['ad']), ad='U1-secili',
                metadata=dict(secim=ad, yontem=yontem), **ortak)
    if ad == 'U1':
        return temel
    if ad != 'U2':
        raise ValueError(f'{ad}: U3 (GEAR1) adayı bu sürümde kapalı')
    sek = fay_sekli(izgara, edges, fay_oku(cfg['fay'], surum='DISS3.2.0'),
                    esik=cfg['esik_gelistirme'])
    if secim[ad]['w'] == 0:
        return temel
    return _olsun(karistir(temel.sekil, sek, secim[ad]['w']), temel, f'{ad}-secili')


def hedef_satirlari(cfg, bolge, model, izgara, edges, hedef_frame, hedef_turu,
                    bootstrap, t0, t1, yontem='gk74'):
    """Bir hedef kümesi için hüküm + geliştirme satırları.

    Hüküm satırı yalnız eşik üstü olayları (mi>=k_idx) kullanır; aksi halde
    olay-başı IG, tabanın yayımlamadığı alt büyüklükleri karıştırırdı.
    """
    _, ci, mi = hedefler(hedef_frame, izgara, edges, cfg['derinlik'], t0, t1)
    dob = model.beklenen(t0, t1, None, izgara, edges)
    n_hucre = len(izgara)
    rows = []
    k_idx = int(np.searchsorted(edges, 4.95, side='right') - 1)
    exp_a = dob[:, k_idx:].sum(axis=1)[:, None]
    for taban_ad, taban_yol in cfg['tabanlar']:
        taban = taban_yukle(taban_ad, taban_yol)
        bt = taban.beklenen(t0, t1, None, izgara, taban.m_kenarlar)
        exp_t = bt.sum(axis=1)[:, None]
        sec = mi >= k_idx
        ci_k = ci[sec]
        obs_k = _gozlem_matris((n_hucre, 1), ci_k, np.zeros(len(ci_k), int))
        r = olay_ig(dob[:, k_idx:].sum(axis=1)[ci_k], bt.sum(axis=1)[ci_k],
                    exp_a.sum(), exp_t.sum(), tekrar=bootstrap)
        r.update(aday=model.ad, taban=taban_ad, bolge=bolge, donem='2011-2015',
                 hedef=hedef_turu, esik=4.95, N=int(obs_k.sum()), yontem=yontem,
                 Lambda_aday=float(exp_a.sum()), Lambda_taban=float(exp_t.sum()),
                 logL_aday=poisson_logl(exp_a, obs_k), logL_taban=poisson_logl(exp_t, obs_k),
                 NSM=tutarlilik(exp_a, obs_k, tekrar=2000, tohum=TOHUM))
        _poisson_kimlik(r)
        rows.append(r)
    e = cfg['esik_gelistirme']
    j = int(np.searchsorted(edges, e, side='right') - 1)
    exp_g = dob[:, j:].sum(axis=1)
    top = float(exp_g.sum())
    uni = _uniform(top, izgara)
    sec = mi >= j
    ci_j = ci[sec]
    obs_g = _gozlem_matris((n_hucre, 1), ci_j, np.zeros(len(ci_j), int))
    r = olay_ig(exp_g[ci_j], uni[ci_j], top, top, tekrar=bootstrap)
    r.update(aday=model.ad, taban='duzgun', bolge=bolge, donem='2011-2015',
             hedef=hedef_turu, esik=float(e), N=int(obs_g.sum()), yontem=yontem,
             Lambda_aday=top, Lambda_taban=top,
             logL_aday=poisson_logl(exp_g[:, None], obs_g),
             logL_taban=poisson_logl(uni[:, None], obs_g),
             NSM=tutarlilik(exp_g[:, None], obs_g, tekrar=2000, tohum=TOHUM),
             not_='Yerleşikler <4.95 yayımlamaz; geliştirme sıfırı düzgün alan')
    _poisson_kimlik(r)
    rows.append(r)
    return rows


def _poisson_kimlik(row):
    """Poisson logL farkı/N = IG zorunluluğu; skor kodu iç doğrulaması."""
    if row.get('durum') != 'tanımlı' or not row.get('N'):
        return
    kimlik = (row['logL_aday'] - row['logL_taban']) / row['N']
    if not np.isclose(kimlik, row['IG'], rtol=1e-9, atol=1e-9):
        raise ValueError(f'Poisson kimliği tutmadı: {kimlik} != {row["IG"]}')


def olc(bolge, *, bootstrap=BOOTSTRAP, duyarlilik=False):
    cfg = BOLGELER[bolge]
    katalog = katalog_oku(cfg['katalog'], cfg['derinlik'])
    izgara = pd.read_csv(cfg['izgara'])
    edges = cfg['m_kenarlar']
    t0, t1 = utc('2011-01-01'), utc('2016-01-01')
    # Hedef kümesizleştirme ≤2015 tüm katalogla (hedefin kendi dönemi).
    tam_k, tam_mask = arka_plan_maskesi(katalog, 'gk74')
    hedef_kat = tam_k[tam_mask]
    d2005 = katalog[katalog.zaman < utc('2006-01-01')]
    d2010 = katalog[katalog.zaman < utc('2011-01-01')]
    k2010, m2010 = arka_plan_maskesi(d2010, 'gk74')
    secim = sec_model(bolge, d2005, izgara, k2010[m2010])
    model = model_sec(bolge, secim, d2010, izgara)
    tum = katalog[(katalog.zaman >= t0) & (katalog.zaman < t1)]
    rows = []
    for hedef_turu, hedef_frame in (('kumesiz', hedef_kat), ('tum', tum)):
        rows += hedef_satirlari(cfg, bolge, model, izgara, edges, hedef_frame, hedef_turu,
                                bootstrap, t0, t1)
    duy = []
    if duyarlilik:
        for yontem in ('uhrhammer', 'reasenberg'):
            km, mm = arka_plan_maskesi(katalog, yontem)
            mdl = model_sec(bolge, secim, d2010, izgara, yontem=yontem)
            for hedef_turu, hedef_frame in (('kumesiz', km[mm]), ('tum', tum)):
                duy += hedef_satirlari(cfg, bolge, mdl, izgara, edges, hedef_frame,
                                       hedef_turu, bootstrap, t0, t1, yontem=yontem)
    return dict(bolge=bolge, secim=secim, satirlar=rows, duyarlilik=duy, model=model,
                katalog_N=len(katalog), hedef_N=len(hedef_kat),
                hedef_derinlik=list(cfg['derinlik']), mmin=cfg['mmin'],
                esik_gelistirme=cfg['esik_gelistirme'])


def json_temiz(v):
    if isinstance(v, dict):
        return {str(k): json_temiz(x) for k, x in v.items()}
    if isinstance(v, (list, tuple, np.ndarray)):
        return [json_temiz(x) for x in v]
    if isinstance(v, (np.floating, float)):
        return float(v) if np.isfinite(v) else None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bolge', choices=['italya'], default='italya')
    p.add_argument('--cikti', type=Path, default=Z_CIKTI / 'OLCUM.json')
    p.add_argument('--bootstrap', type=int, default=BOOTSTRAP)
    p.add_argument('--duyarlilik', action='store_true', help='Uhrhammer ve Reasenberg duyarlılık satırları')
    args = p.parse_args(argv)
    bolgeler = [args.bolge]
    sonuc = {'surum': 1, 'tohum': TOHUM, 'zemin': ZEMIN, 'bootstrap': args.bootstrap,
             'bolgeler': {}}
    for b in bolgeler:
        r = olc(b, bootstrap=args.bootstrap, duyarlilik=args.duyarlilik)
        model = r.pop('model')
        r['model_ozet'] = json_temiz(model.metadata)
        r['model_sekil_ozet'] = dict(min=float(model.sekil.min()), max=float(model.sekil.max()),
                                     toplam=float(model.sekil.sum()))
        sonuc['bolgeler'][b] = r
    args.cikti.parent.mkdir(parents=True, exist_ok=True)
    args.cikti.write_text(json.dumps(json_temiz(sonuc), ensure_ascii=False, indent=2,
                                     allow_nan=False) + '\n', encoding='utf-8')
    print(args.cikti)


if __name__ == '__main__':
    main()
