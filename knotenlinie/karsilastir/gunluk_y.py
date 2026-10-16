"""Deney Y günlük koşucusu: D0/D1/D2/D3'ü yan bölgelerde puanlar.

Yalnız ≤2020-12-31 geliştirme verisi; 2021 mührü `okuyucu` katmanında.
Küçük ölçek (yerel makine) ve tam ölçek (hesap sunucusu) aynı kod; `--taban-mc` yalnız deneme
için Mc tabanını yükseltir.
"""
from __future__ import annotations

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.karsilastir.blok import blok_ozeti
from knotenlinie.karsilastir.kosucu import olay_kutulari, utc
from knotenlinie.karsilastir.puan import tutarlilik
from knotenlinie.yan_tezgah import okuyucu as O
from knotenlinie.yan_tezgah import model as YM

from knotenlinie.yollar import KOSU, VERI  # noqa: E402

D = VERI / 'yan'
DEFTER = KOSU / 'defter/Y'
DERINLIK = {'scsn': (0.0, 30.0), 'geonet': (0.0, 40.0)}


def kenarlar(hedef):
    """[hedef, hedef+0.1, ..., 8.9, +inf) 0.1 M kutuları."""
    e = np.round(np.arange(hedef, 9.0 + 1e-9, 0.1), 2)
    return np.r_[e, np.inf]


def _json_temiz(o):
    if isinstance(o, dict):
        return {k: _json_temiz(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_json_temiz(v) for v in o]
    if isinstance(o, np.ndarray):
        return _json_temiz(o.tolist())
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    return o


def _rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)


def _indeks(run, esik):
    return int(np.flatnonzero(np.isclose(run['edges'][:-1], esik, atol=1e-10, rtol=0))[0])


def gunluk_kos(model, bas, son, katalog, grid, edges, derinlik):
    """Günlük adım; hedef olaylar [bas,son) içinde. Zaman×hücre küpü tutulmaz."""
    bas, son = utc(bas), utc(son)
    hedef = katalog[(katalog.zaman >= bas) & (katalog.zaman < son)].reset_index(drop=True)
    olaylar, ci, mi = olay_kutulari(hedef, grid, edges, derinlik)
    gun = ((olaylar.zaman - bas) / pd.Timedelta(days=1)).to_numpy(float).astype(int)
    gun_sayisi = int((son - bas) / pd.Timedelta(days=1))
    shape = (len(grid), len(edges) - 1)
    lam = np.empty(len(olaylar), float)
    toplam = np.zeros(shape, float)
    gunluk = np.zeros((gun_sayisi, len(edges) - 1), float)
    ll = 0.0
    for d in range(gun_sayisi):
        a = bas + pd.Timedelta(days=d)
        gecmis = katalog[katalog.zaman < a]
        lam_d = model.beklenen(a, a + pd.Timedelta(days=1), gecmis, grid, edges)
        if lam_d.shape != shape:
            raise ValueError(f'{getattr(model, "ad", "?")}: beklenen şekli {lam_d.shape} != {shape}')
        toplam += lam_d
        gunluk[d] = lam_d.sum(axis=0)
        idx = np.flatnonzero(gun == d)
        ll -= float(lam_d.sum())
        if len(idx):
            r = lam_d[ci[idx], mi[idx]]
            lam[idx] = r
            if (r == 0).any():
                ll = -np.inf
            else:
                ll += float(np.log(r).sum())
            _, n = np.unique(ci[idx] * shape[1] + mi[idx], return_counts=True)
            ll -= float(gammaln(n + 1).sum())
    return dict(ad=model.ad, events=olaylar, ci=ci, mi=mi, gun=gun, lam=lam,
                toplam=toplam, gunluk=gunluk, logL=float(ll), gun_sayisi=gun_sayisi,
                edges=edges, days=pd.date_range(bas, son - pd.Timedelta(days=1), freq='D'))


def cift_ozet(a, b, esik, *, tekrar=10000, tohum=20261011):
    ja, jb = _indeks(a, esik), _indeks(b, esik)
    if not a['events'].equals(b['events']):
        raise ValueError('koşuların hedef sırası eşleşmiyor')
    keep = (a['mi'] >= ja) & (b['mi'] >= jb)
    bek_a, bek_b = a['toplam'][:, ja:], b['toplam'][:, jb:]
    obs = np.zeros_like(bek_a, dtype=int)
    ci, mi = a['ci'][keep], a['mi'][keep] - ja
    np.add.at(obs, (ci, mi), 1)
    n = int(keep.sum())
    if n == 0:
        return dict(N=0, IG=None, IG_olay=None, integral=None, SE_blok=None, z=None,
                    p_tek=None, durum='belirsiz', NSM=None, Lambda_aday=float(bek_a.sum()),
                    Lambda_taban=float(bek_b.sum()), logL_aday=a['logL'], logL_taban=b['logL'])
    lam_a, lam_b = a['lam'][keep], b['lam'][keep]
    if (lam_a <= 0).any() or (lam_b <= 0).any():
        return dict(N=n, IG=None, IG_olay=None, integral=None, SE_blok=None, z=None,
                    p_tek=None, durum='belirsiz', NSM=None, sebep='gözlemli sıfır oran',
                    Lambda_aday=float(bek_a.sum()), Lambda_taban=float(bek_b.sum()),
                    logL_aday=a['logL'], logL_taban=b['logL'])
    logr = np.log(lam_a) - np.log(lam_b)
    gun_bek_a = a['gunluk'][:, ja:].sum(axis=1)
    gun_bek_b = b['gunluk'][:, jb:].sum(axis=1)
    gun_n = np.bincount(a['gun'][keep], minlength=a['gun_sayisi'])
    gun_delta = np.zeros(a['gun_sayisi'])
    for d in range(a['gun_sayisi']):
        idx = a['gun'][keep] == d
        gun_delta[d] = logr[idx].sum() - (gun_bek_a[d] - gun_bek_b[d])
    blok = blok_ozeti(gun_delta, gun_n, a['days'], n=n)
    ig = float(logr.mean() - (bek_a.sum() - bek_b.sum()) / n)
    if ja == 0 and jb == 0:
        # Tam eşikte Poisson logL farkı / N, IG'ye birebir eşit (n! terimi sadeleşir).
        assert np.isclose((a['logL'] - b['logL']) / n, ig, rtol=1e-9, atol=1e-9)
    nsm = tutarlilik(bek_a, obs, tekrar=int(tekrar), tohum=int(tohum))
    return dict(N=n, IG=ig, IG_olay=float(logr.mean()),
                integral=float(-(bek_a.sum() - bek_b.sum()) / n),
                SE_blok=blok['SE_blok'], z=blok['z'], p_tek=blok['p_tek'],
                birincil_hukum=blok.get('durum'), GA95=blok.get('GA95'),
                blok_sayisi=blok.get('blok_sayisi'),
                Lambda_aday=float(bek_a.sum()), Lambda_taban=float(bek_b.sum()),
                logL_aday=a['logL'], logL_taban=b['logL'], NSM=nsm, durum='tanımlı')


def _defter_yaz(klasor, ad, bolge, donem, run, esik, esik1):
    klasor.mkdir(parents=True, exist_ok=True)
    keep = run['mi'] >= _indeks(run, esik)
    ev = run['events'].iloc[np.flatnonzero(keep)].reset_index(drop=True)
    olay = pd.DataFrame(dict(
        zaman=ev.zaman.dt.strftime('%Y-%m-%dT%H:%M:%S.%f').str[:-3],
        enlem=ev.enlem, boylam=ev.boylam, mw=ev.mw,
        hucre=run['ci'][keep], kutu=run['mi'][keep],
        gun=ev.zaman.dt.strftime('%Y-%m-%d'), lam=run['lam'][keep]))
    olay.to_csv(klasor / f'{ad}__{bolge}__{donem}__olay.csv.gz', index=False, compression='gzip')
    g = pd.DataFrame(dict(gun=run['days'].strftime('%Y-%m-%d'),
                          Lam_hedef=run['gunluk'][:, _indeks(run, esik):].sum(axis=1),
                          Lam_hedef1=run['gunluk'][:, _indeks(run, esik1):].sum(axis=1)))
    g.to_csv(klasor / f'{ad}__{bolge}__{donem}__gun.csv.gz', index=False, compression='gzip')


def _d3_agirlik(hedefsel, gecici, args, df, grid, edges, bolge):
    """2006–2010 günlük logL ile ızgara taraması; bileşenler son=2006."""
    runs = {v: gunluk_kos(gecici[v], args.d3_bas, args.ayar_son, df, grid, edges, DERINLIK[bolge])
            for v in hedefsel}
    j = _indeks(runs['D0'], args.hedef)
    en_iyi, en_ll = None, -np.inf
    for w0 in np.arange(0, 1.001, .2):
        for w1 in np.arange(0, 1.001 - w0 + 1e-9, .2):
            w = (round(w0, 4), round(w1, 4), round(1 - w0 - w1, 4))
            if w[2] < -1e-9:
                continue
            lam = np.maximum(sum(wi * runs[v]['lam'] for wi, v in zip(w, hedefsel)), 1e-300)
            integral = sum(wi * runs[v]['toplam'][:, j:].sum() for wi, v in zip(w, hedefsel))
            ll = float(np.log(lam).sum() - integral)
            if ll > en_ll:
                en_ll, en_iyi = ll, w
    return en_iyi, en_ll


def _hkj_tani(run_d2, run_d1, esik):
    """HKJ kötüleşme tanısı (seçim için kullanılmaz).

    D2'nin hedef eşiği üstünde beklediği sayıyı D1'in beklediği sayıya ve gözlenene
    oranlar: ``beklenen_oran`` D2'nin D1'e dayattığı tespit düzeltmesi,``gozlenen_oran``
    D1 tabanına göre gözlenen oran. ``Lambda_D2_bol_N > 1`` fazla tahmin demektir.
    """
    i2, i1 = _indeks(run_d2, esik), _indeks(run_d1, esik)
    if not run_d2['events'].equals(run_d1['events']):
        raise ValueError('tanı: hedef sırası eşleşmiyor')
    n = int((run_d2['mi'] >= i2).sum())
    lam2 = float(run_d2['toplam'][:, i2:].sum())
    lam1 = float(run_d1['toplam'][:, i1:].sum())
    if n == 0 or lam1 <= 0:
        return dict(N=n, Lambda_D2=lam2, Lambda_D1=lam1, durum='tanımsız')
    # Gün bölümü: D2'nin D1'den belirgin düşük beklediği günler = HKJ'nin etkin olduğu günler.
    g2, g1 = run_d2['gunluk'][:, i2:].sum(axis=1), run_d1['gunluk'][:, i1:].sum(axis=1)
    oran = np.divide(g2, g1, out=np.full(len(g2), np.nan), where=g1 > 0)
    etkin = oran < 0.99 * np.nanmedian(oran)  # D2/D1 oranı tipikten belirgin düşük gün = HKJ etkin
    ngun = np.bincount(run_d2['gun'][run_d2['mi'] >= i2], minlength=len(g2))
    bolum = {}
    for ad, mk in (('hkj_etkin', etkin), ('hkj_etkin_degil', ~etkin)):
        bolum[ad] = dict(gun=int(mk.sum()), N=int(ngun[mk].sum()), Lambda_D1=float(g1[mk].sum()),
                         Lambda_D2=float(g2[mk].sum()))
    return dict(N=n, Lambda_D2=lam2, Lambda_D1=lam1, gun_bolumu=bolum,
                Lambda_D2_bol_N=lam2 / n, Lambda_D1_bol_N=lam1 / n,
                beklenen_tespit_orani=lam2 / lam1, gozlenen_oran=n / lam1,
                artik_bol_gozlenen=lam2 / n,
                durum=('HKJ fazla düzeltiyor' if lam2 / n > 1.05 else
                       'HKJ eksik düzeltiyor' if lam2 / n < 0.95 else 'dengeli'),
                notu='operasyonel tanı; seçimde kullanılmaz')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--bolge', choices=['scsn', 'geonet'], required=True)
    ap.add_argument('--veri', type=Path, default=D)
    ap.add_argument('--ayar-bas', default=None)
    ap.add_argument('--ayar-son', default='2011-01-01T00:00:00Z')
    ap.add_argument('--test-bas', default='2011-01-01T00:00:00Z')
    ap.add_argument('--test-son', default='2021-01-01T00:00:00Z')
    ap.add_argument('--taban-mc', type=float, default=None, help='yalnız küçük ölçek denemesi')
    ap.add_argument('--rmax-km', type=float, default=None, help='uzay kesmesi (varsayılan: bölge kesmesi)')
    ap.add_argument('--tmax-gun', type=float, default=None, help='zaman kesmesi (varsayılan: bölge kesmesi)')
    ap.add_argument('--maks-cift', type=int, default=20_000_000)
    ap.add_argument('--maksiter', type=int, default=400)
    ap.add_argument('--tekrar', type=int, default=10000)
    ap.add_argument('--d3', action='store_true')
    ap.add_argument('--d3-ayar-son', default='2006-01-01T00:00:00Z')
    ap.add_argument('--d3-bas', default='2006-01-01T00:00:00Z')
    ap.add_argument('--donem-adi', default=None)
    ap.add_argument('--cikti', type=Path, required=True)
    ap.add_argument('--defter-yaz', action='store_true')
    ap.add_argument('--defter', type=Path, default=DEFTER)
    args = ap.parse_args(argv)
    t0 = time.monotonic()
    df = O.oku(args.veri, args.bolge)
    ayar_df = df if args.ayar_bas is None else df[df.zaman >= utc(args.ayar_bas)].reset_index(drop=True)
    grid = O.izgara(args.bolge)
    tm_tam = O.tamlik(df, int(df.zaman.dt.year.min()), int(df.zaman.dt.year.max()))
    hedef = float(tm_tam['hedef'])
    if args.taban_mc is not None:
        hedef = max(hedef, float(args.taban_mc))
    edges = kenarlar(hedef)
    edges1 = float(edges[_indeks({'edges': edges}, hedef) + 1])
    modeller, fitler = {}, {}
    for v in ('D0', 'D1', 'D2'):
        modeller[v] = YM.kur(ayar_df, args.bolge, ayar_son=args.ayar_son, hedef=hedef,
                             varyant=v, taban_mc=args.taban_mc, maks_cift=args.maks_cift,
                             maksiter=args.maksiter, rmax_km=args.rmax_km, tmax_gun=args.tmax_gun)
        fitler[v] = modeller[v].metadata
        print(f'{args.bolge} {v} ayar: logL={modeller[v].p["logL"]:.1f} '
              f'n={modeller[v].metadata["n_fit"]} s={time.monotonic()-t0:.0f}', flush=True)
    ozet = dict(bolge=args.bolge, baslangic=utc(args.test_bas).isoformat(),
                bitis=utc(args.test_son).isoformat(), hedef=float(hedef), hedef1=float(edges1),
                taban_mc=args.taban_mc, hucre=len(grid),
                m_kenarlar=[float(x) if np.isfinite(x) else '+inf' for x in edges],
                fitler=fitler, python=sys.version.split()[0], numpy=np.__version__,
                pandas=pd.__version__, rss_tepe_byte=_rss(),
                NSM_notu='N Poisson iki kuyruk; S/M sabit N multinomial; gün-başı geçmişe koşullu '
                         'operasyonel tanı, kör hüküm değil',
                SE_tanimi='UTC Pazartesi haftalık blok; B/(B-1) Σ(D_w-IG·N_w)^2/N^2',
                muhur='deprem/ altındaki bütün satırlar <2021-01-01; 2021+ yok')
    if args.d3:
        hedefsel = ['D0', 'D1', 'D2']
        args.hedef = hedef
        gecici = {v: YM.kur(ayar_df, args.bolge, ayar_son=args.d3_ayar_son, hedef=hedef,
                            varyant=v, taban_mc=args.taban_mc, maks_cift=args.maks_cift,
                            maksiter=args.maksiter, rmax_km=args.rmax_km, tmax_gun=args.tmax_gun) for v in hedefsel}
        agirlik, secim_ll = _d3_agirlik(hedefsel, gecici, args, df, grid, edges, args.bolge)
        del gecici  # önbellekleri bırak (bellek)
        modeller['D3'] = YM.Karisim('D3', [modeller[v] for v in hedefsel], agirlik)
        ozet['d3_agirliklar'] = dict(zip(hedefsel, [float(x) for x in agirlik]))
        ozet['d3_secim_logL'] = secim_ll
        print(f'{args.bolge} D3 ağırlık={agirlik} logL={secim_ll:.1f}', flush=True)
    runs, satirlar = {}, []
    donem = args.donem_adi or f'{args.test_bas[:4]}-{args.test_son[:4]}'
    for ad, m in modeller.items():
        if ad == 'D3':
            # Sıcak önbellekle D3 geçişi bellekte 6 GB'a şişti (kök neden bulunamadı); bileşen
            # önbellekleri sıfırlanır, soğuk geçiş ölçüldü: ≤1,8 GB. Sayıyı değiştirmez.
            for bm in m.modeller:
                bm._sifirla_onbellek()
        runs[ad] = gunluk_kos(m, args.test_bas, args.test_son, df, grid, edges, DERINLIK[args.bolge])
        print(f'{args.bolge} {ad} puan: N={len(runs[ad]["events"])} logL={runs[ad]["logL"]:.1f} '
              f's={time.monotonic()-t0:.0f}', flush=True)
        if args.defter_yaz:
            _defter_yaz(args.defter, ad, args.bolge, donem, runs[ad], hedef, edges1)
    for ad, a, b in (('D1−D0', 'D1', 'D0'), ('D2−D1', 'D2', 'D1')):
        for esik in (hedef, edges1):
            r = cift_ozet(runs[a], runs[b], esik, tekrar=args.tekrar)
            r.update(aday=a, taban=b, karsilik=ad, bolge=args.bolge, esik=float(esik))
            if ad == 'D2−D1':
                r['hkj_tani'] = _hkj_tani(runs['D2'], runs['D1'], esik)
            satirlar.append(r)
    if 'D3' in runs:
        tek_en = max(('D0', 'D1', 'D2'), key=lambda v: runs[v]['logL'])
        for esik in (hedef, edges1):
            r = cift_ozet(runs['D3'], runs[tek_en], esik, tekrar=args.tekrar)
            r.update(aday='D3', taban=tek_en, karsilik='D3−en iyi tek', bolge=args.bolge,
                     esik=float(esik))
            satirlar.append(r)
    ozet['satirlar'] = satirlar
    ozet['duvar_saniye'] = time.monotonic() - t0
    ozet['rss_tepe_byte'] = _rss()
    args.cikti.parent.mkdir(parents=True, exist_ok=True)
    args.cikti.write_text(json.dumps(_json_temiz(ozet), ensure_ascii=False, indent=1, allow_nan=False) + '\n',
                          encoding='utf-8')
    print(args.cikti, flush=True)


if __name__ == '__main__':
    main()
