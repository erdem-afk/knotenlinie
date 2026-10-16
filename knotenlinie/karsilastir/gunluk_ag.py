"""Experiment AG günlük koşucusu: X-b-5,5 (sonlu kaynak) yan tezgâhın D1 modeline karşı.

Yalnız ≤2020-12-31 geliştirme verisi (SCSN/GeoNet, `$KNOTENLINIE_DATA/yan/`). D0/D1 ayarı
`gunluk_y` ile aynıdır (aynı kesme, aynı veri); X, D1'in parametrelerini aynen alır
(yeniden MLE yok) ve yalnız M>=5,5 ebeveynlerin uzaysal satırını değiştirir.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.karsilastir import gunluk_y as GY
from knotenlinie.karsilastir.blok import blok_ozeti
from knotenlinie.karsilastir.kosucu import utc
from knotenlinie.yan_tezgah import model as YM
from knotenlinie.yan_tezgah import okuyucu as O
from knotenlinie.yan_tezgah.sonlu import SonluYan

from knotenlinie.yollar import KOSU  # noqa: E402

DEFTER = KOSU / 'defter/AG'


def buyuk_ebeveyn_maske(hedef, katalog, met, *, mw_esik=5.5, gun=30.0, km=100.0):
    """Hedef başına: önceki `gun` gün ve `km` içinde M>=mw_esik bir olay var mı."""
    p = katalog[katalog.mw >= mw_esik].sort_values('zaman').reset_index(drop=True)
    out = np.zeros(len(hedef), bool)
    if not len(p):
        return out
    xp, yp = met.km(p.boylam.to_numpy(float), p.enlem.to_numpy(float))
    for i, row in enumerate(hedef.itertuples(index=False)):
        lo = row.zaman - pd.Timedelta(days=gun)
        j0 = int(p.zaman.searchsorted(lo, side='left'))
        j1 = int(p.zaman.searchsorted(row.zaman, side='left'))
        if j1 > j0:
            x0, y0 = met.km(row.boylam, row.enlem)
            out[i] = bool((np.hypot(xp[j0:j1] - x0, yp[j0:j1] - y0) <= km).any())
    return out


def alt_kume(a, b, esik, maske_tam):
    """Alt küme IG: olay terimi (SE'li) ve X'in tanımıyla (toplam integral / N_alt)."""
    ja, jb = GY._indeks(a, esik), GY._indeks(b, esik)
    keep = (a['mi'] >= ja) & (b['mi'] >= jb)
    sub = maske_tam[keep]
    n = int(sub.sum())
    if n == 0:
        return dict(N=0, IG_olay=None, IG=None)
    logr = (np.log(a['lam'][keep]) - np.log(b['lam'][keep]))
    delta = float(a['toplam'][:, ja:].sum() - b['toplam'][:, jb:].sum())
    gun = a['gun'][keep]
    gun_delta = np.zeros(a['gun_sayisi'])
    gun_n = np.zeros(a['gun_sayisi'], int)
    np.add.at(gun_delta, gun[sub], logr[sub])
    np.add.at(gun_n, gun[sub], 1)
    blok = blok_ozeti(gun_delta, gun_n, a['days'], n=n)
    return dict(N=n, IG_olay=float(logr[sub].mean()), SE_blok_olay=blok.get('SE_blok'),
                z_olay=blok.get('z'), integral_toplam_bol_N=float(-delta / n),
                IG=float(logr[sub].mean() - delta / n),
                Lambda_aday_toplam=float(a['toplam'][:, ja:].sum()),
                Lambda_taban_toplam=float(b['toplam'][:, jb:].sum()))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bolge', choices=['scsn', 'geonet'], default='scsn')
    ap.add_argument('--veri', type=Path, default=GY.D)
    ap.add_argument('--ayar-son', default='2011-01-01T00:00:00Z')
    ap.add_argument('--test-bas', default='2011-01-01T00:00:00Z')
    ap.add_argument('--test-son', default='2021-01-01T00:00:00Z')
    ap.add_argument('--taban-mc', type=float, default=None)
    ap.add_argument('--m-s', type=float, default=5.5)
    ap.add_argument('--maks-cift', type=int, default=200_000_000)
    ap.add_argument('--maksiter', type=int, default=400)
    ap.add_argument('--tekrar', type=int, default=10000)
    ap.add_argument('--d0', action='store_true', help='D0 de ayarla/puanla (X − D0 satırı)')
    ap.add_argument('--donem-adi', default=None)
    ap.add_argument('--cikti', type=Path, required=True)
    ap.add_argument('--defter-yaz', action='store_true')
    ap.add_argument('--defter', type=Path, default=DEFTER)
    args = ap.parse_args(argv)
    t0 = time.monotonic()
    bolge = args.bolge
    df = O.oku(args.veri, bolge)
    grid = O.izgara(bolge)
    tm_tam = O.tamlik(df, int(df.zaman.dt.year.min()), int(df.zaman.dt.year.max()))
    hedef = float(tm_tam['hedef'])
    if args.taban_mc is not None:
        hedef = max(hedef, float(args.taban_mc))
    edges = GY.kenarlar(hedef)
    edges1 = float(edges[GY._indeks({'edges': edges}, hedef) + 1])
    modeller, fitler = {}, {}
    for v in (('D0', 'D1') if args.d0 else ('D1',)):
        modeller[v] = YM.kur(df, bolge, ayar_son=args.ayar_son, hedef=hedef, varyant=v,
                             taban_mc=args.taban_mc, maks_cift=args.maks_cift,
                             maksiter=args.maksiter)
        fitler[v] = modeller[v].metadata
        print(f'{bolge} {v} ayar: logL={modeller[v].p["logL"]:.1f} s={time.monotonic()-t0:.0f}', flush=True)
    modeller['X'] = SonluYan(modeller['D1'], m_s=args.m_s)
    ozet = dict(bolge=bolge, baslangic=utc(args.test_bas).isoformat(), bitis=utc(args.test_son).isoformat(),
                hedef=float(hedef), hedef1=float(edges1), taban_mc=args.taban_mc, hucre=len(grid),
                m_s=float(args.m_s), fitler=fitler, python=sys.version.split()[0],
                numpy=np.__version__, pandas=pd.__version__,
                d1_parametreler={k: float(v) for k, v in modeller['D1'].th.items()},
                SE_tanimi='UTC Pazartesi haftalık blok; B/(B-1) Σ(D_w-IG·N_w)^2/N^2',
                muhur='deprem/ altındaki bütün satırlar <2021-01-01; 2021+ yok')
    donem = args.donem_adi or f'{args.test_bas[:4]}-{args.test_son[:4]}'
    runs = {}
    sira = ['D1', 'X'] + (['D0'] if args.d0 else [])
    for ad in sira:
        m = modeller[ad]
        if ad == 'D0':
            modeller['D1']._sifirla_onbellek()
        runs[ad] = GY.gunluk_kos(m, args.test_bas, args.test_son, df, grid, edges, GY.DERINLIK[bolge])
        print(f'{bolge} {ad} puan: N={len(runs[ad]["events"])} logL={runs[ad]["logL"]:.1f} '
              f's={time.monotonic()-t0:.0f} rss={GY._rss()/1e9:.2f}GB', flush=True)
        if args.defter_yaz:
            GY._defter_yaz(args.defter, ad, bolge, donem, runs[ad], hedef, edges1)
    met = modeller['D1']._mekan_met
    tam_maske = buyuk_ebeveyn_maske(runs['D1']['events'], df, met, mw_esik=args.m_s)
    satirlar = []
    ciftler = [('X−D1', 'X', 'D1')] + ([('X−D0', 'X', 'D0'), ('D1−D0', 'D1', 'D0')] if args.d0 else [])
    for ad, a, b in ciftler:
        for esik in (hedef, edges1):
            r = GY.cift_ozet(runs[a], runs[b], esik, tekrar=args.tekrar)
            r.update(aday=a, taban=b, karsilik=ad, bolge=bolge, esik=float(esik))
            r['buyuk_ebeveyn_altkume'] = alt_kume(runs[a], runs[b], esik, tam_maske)
            satirlar.append(r)
    ozet['satirlar'] = satirlar
    son_yon = {}
    for z, m_, d, n in modeller['X'].kayit.values():  # ebeveyn başına son (donmuş) doğrultu
        son_yon[(z, m_)] = (d, n)
    ozet['sonlu_ebeveynler'] = [dict(zaman=z, mw=m_, dogrultu=d, artci_n=n)
                                for (z, m_), (d, n) in sorted(son_yon.items())]
    ozet['buyuk_ebeveyn_maske_N'] = int(tam_maske.sum())
    ozet['duvar_saniye'] = time.monotonic() - t0
    ozet['rss_tepe_byte'] = GY._rss()
    args.cikti.parent.mkdir(parents=True, exist_ok=True)
    args.cikti.write_text(json.dumps(GY._json_temiz(ozet), ensure_ascii=False, indent=1, allow_nan=False) + '\n',
                          encoding='utf-8')
    print(args.cikti, flush=True)


if __name__ == '__main__':
    main()
