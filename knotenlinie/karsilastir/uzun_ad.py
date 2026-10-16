"""Experiment AD — Kaliforniya uzun vade: bizim model ve HKJ07 (RELM birincisi), benzer-benzere.

Akış (records/AD/KURAL.md): `sec` ≤2000 kurup 2001–2005'te hiperparametre seçer; `puan` seçileni ≤2005 (adil)
ve ≤2010 (güncel) verisiyle kurup 2006–2010 ve 2011–2020'de HKJ07-ana şok (kümesiz hedef) ve HKJ07-artçı
(bütün olaylar) karşısında puanlar. Skor yardımcıları Z'den (`uzun_z.olay_ig`) gelir.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from knotenlinie.kaliforniya import veri
from knotenlinie.kaliforniya.model import Kafes, kumesiz_maske, kur, oran_kestir
from knotenlinie.karsilastir.kosucu import olay_kutulari
from knotenlinie.karsilastir.puan import log_olabilirlik, tutarlilik
from knotenlinie.karsilastir.uzun_z import olay_ig, json_temiz

from knotenlinie.yollar import KAYIT, KOSU  # noqa: E402

AD_DIR = KOSU / 'AD'       # new AD outputs
AD_KAYIT = KAYIT / 'AD'    # frozen AD record (rule, hyper-parameter selection)
TOHUM = 20261005
BOOTSTRAP = 2000
K_ADAY = (2, 3, 5, 10, 20, 40)
MMIN_ADAY = (2.5, 3.0, 3.5)
MC_ADAY = (3.0, 3.5)
DEV_ESIK = 3.95
M_DEV = np.r_[DEV_ESIK, np.inf]


def utc(s):
    return pd.Timestamp(s, tz='UTC')


class Baglam:
    """Katalog, ızgara ve HKJ07 tahminleri bir kez yüklenir."""

    def __init__(self):
        self.izgara, self.hkj_ana = veri.hkj_oku(veri.HKJ_ANA)
        iz2, self.hkj_art = veri.hkj_oku(veri.HKJ_ARTCI)
        if not np.array_equal(self.izgara.to_numpy(), iz2.to_numpy()):
            raise ValueError('iki HKJ07 dosyasının ızgarası aynı değil')
        self.kafes = Kafes(self.izgara)
        k = veri.katalog_oku()
        self.kat = k[k['mw'] >= 2.5].reset_index(drop=True)
        self._maske = {}

    def maske(self, bitis, yontem='gk74'):
        """Kesimden (hariç) önceki olaylarla kümesizleştirme; (sıralı katalog, maske)."""
        anahtar = (str(bitis), yontem)
        if anahtar not in self._maske:
            self._maske[anahtar] = kumesiz_maske(self.kat[self.kat['zaman'] < utc(bitis)], yontem)
        return self._maske[anahtar]

    def hedef(self, tur, yontem='gk74'):
        """Hedef olaylar (tüm 1981–2020 katalogla kümesizleştirme; 'tum' bütün olaylar)."""
        if tur == 'tum':
            return self.kat
        k, m = self.maske('2021-01-01', yontem)
        return k[m].reset_index(drop=True)


def hucre_bin(baglam, frame, t0, t1, esik, kenarlar, derinlik=veri.DERINLIK):
    a = frame[(frame['zaman'] >= utc(t0)) & (frame['zaman'] < utc(t1)) & (frame['mw'] >= esik)]
    return olay_kutulari(a, baglam.izgara, kenarlar, derinlik)


def poisson_logl_toplam(lam, n):
    return n * np.log(lam) - lam


def sec(baglam):
    """≤2000 kur, 2001–2005'te seç. KURAL.md 'Seçim' bölümü."""
    kk, mm = baglam.maske('2001-01-01')
    dk, dm = baglam.maske('2006-01-01')
    hedef = {'ana': dk[dm], 'tum': dk}
    obs = {}
    for ad, fr in hedef.items():
        _, ci, _ = hucre_bin(baglam, fr, '2001-01-01', '2006-01-01', DEV_ESIK, M_DEV)
        obs[ad] = ci
    sekil_kayit = []
    for k in K_ADAY:
        for mmin in MMIN_ADAY:
            for gey in (False, True):
                ana, _ = kur(baglam.izgara, baglam.kafes, kk, mm, bitis='2001-01-01', k_komsu=k,
                             kde_mmin=mmin, geysers=gey)
                ll = float(np.sum(np.log(ana.sekil[obs['ana']])))
                sekil_kayit.append(dict(k=k, kde_mmin=mmin, geysers=gey, logL_uzay=ll,
                                        N=int(len(obs['ana']))))
    en = max(sekil_kayit, key=lambda r: r['logL_uzay'])
    oran_kayit = []
    for mc in MC_ADAY:
        ana, art = kur(baglam.izgara, baglam.kafes, kk, mm, bitis='2001-01-01', k_komsu=en['k'],
                       kde_mmin=en['kde_mmin'], geysers=en['geysers'], mc_oran_ana=mc, mc_oran_tum=mc)
        for ad, mdl in (('ana', ana), ('tum', art)):
            lam = 5.0 * mdl.rate_ust * 10.0 ** (mdl.b * (4.95 - DEV_ESIK))
            n = len(obs[ad])
            oran_kayit.append(dict(hedef=ad, mc=mc, b=mdl.b, Lambda=lam, N=n,
                                   logL_toplam=float(poisson_logl_toplam(lam, n))))
    secili = {h: max([r for r in oran_kayit if r['hedef'] == h], key=lambda r: r['logL_toplam'])['mc']
              for h in ('ana', 'tum')}
    return dict(sekil_adaylar=sekil_kayit, sekil_secili=en, oran_adaylar=oran_kayit,
                mc_oran_ana=secili['ana'], mc_oran_tum=secili['tum'],
                dev=dict(esik=DEV_ESIK, N_ana=len(obs['ana']), N_tum=len(obs['tum'])))


def modeller(baglam, secim, kesim, *, yontem='gk74', mc_koseli=8.0, geysers=None,
             mc_ana=None, mc_tum=None):
    """Seçilen hiperparametrelerle kesime kadar veriyle ana şok/artçı modeli."""
    s = secim['sekil_secili']
    kk, mm = baglam.maske(kesim, yontem)
    return kur(baglam.izgara, baglam.kafes, kk, mm, bitis=kesim, k_komsu=s['k'],
               kde_mmin=s['kde_mmin'], geysers=s['geysers'] if geysers is None else geysers,
               mc_oran_ana=secim['mc_oran_ana'] if mc_ana is None else mc_ana,
               mc_oran_tum=secim['mc_oran_tum'] if mc_tum is None else mc_tum,
               mc_koseli=mc_koseli)


def olay_ig_yil(x, yillar, integral, tekrar=BOOTSTRAP, tohum=TOHUM):
    """Yıl bloğu bootstrap SE: IG* = (S* - integral)/N*; olayları değil yılları yeniden örnekler."""
    x, yillar = np.asarray(x, float), np.asarray(yillar)
    bl = sorted(set(yillar.tolist()))
    if len(bl) < 2:
        return None
    s = np.array([x[yillar == b].sum() for b in bl])
    n = np.array([(yillar == b).sum() for b in bl], float)
    rng = np.random.default_rng(tohum)
    idx = rng.integers(0, len(bl), size=(tekrar, len(bl)))
    ns = n[idx].sum(axis=1)
    ok = ns > 0
    ig = (s[idx].sum(axis=1)[ok] - integral) / ns[ok]
    return float(np.std(ig, ddof=1))


def satir(baglam, aday_mat, taban_mat, frame, t0, t1, *, aday, taban, hat, donem, hedef, not_=None,
          bootstrap=BOOTSTRAP):
    """Bir karşılaştırma satırı: hücre×kutu Poisson, M>=4,95."""
    a, ci, mi = hucre_bin(baglam, frame, t0, t1, 4.95, veri.M_KENAR)
    n = len(ci)
    obs = np.zeros(aday_mat.shape, dtype=int)
    np.add.at(obs, (ci, mi), 1)
    la, lb = aday_mat[ci, mi], taban_mat[ci, mi]
    top_a, top_b = float(aday_mat.sum()), float(taban_mat.sum())
    r = olay_ig(la, lb, top_a, top_b, tekrar=bootstrap)
    r.update(aday=aday, taban=taban, hat=hat, donem=donem, hedef=hedef, esik=4.95, N=n,
             Lambda_aday=top_a, Lambda_taban=top_b)
    if r.get('durum') == 'tanımlı':
        r['logL_aday'] = log_olabilirlik(aday_mat, obs)
        r['logL_taban'] = log_olabilirlik(taban_mat, obs)
        kim = (r['logL_aday'] - r['logL_taban']) / n
        if not np.isclose(kim, r['IG'], rtol=1e-9, atol=1e-9):
            raise ValueError(f'Poisson kimliği tutmadı: {kim} != {r["IG"]}')
        x = np.log(la) - np.log(lb)
        yil = a['zaman'].dt.year.to_numpy()
        r['SE_yil'] = olay_ig_yil(x, yil, top_a - top_b, tekrar=bootstrap)
        r['z_yil'] = (r['IG'] / r['SE_yil']) if r['SE_yil'] else None
        r['NSM_aday'] = _nsm(aday_mat, obs)
        r['NSM_taban'] = _nsm(taban_mat, obs)
    if not_:
        r['not_'] = not_
    return r


def _nsm(mat, obs):
    t = tutarlilik(mat, obs, tekrar=2000, tohum=TOHUM)
    return dict(N=t['N'].get('gecti'), S=t['S'].get('gecti'), M=t['M'].get('gecti'),
                gecti=bool(t['gecti']), p_N=t['N'].get('p') if isinstance(t['N'], dict) else None,
                p_S=t['S'].get('p'), p_M=t['M'].get('p'))


def donem_satirlari(baglam, ana, art, hat, donemler, hedefler, *, etiket='', bootstrap=BOOTSTRAP,
                    sekil_satiri=True):
    rows = []
    for (t0, t1, yil, dn) in donemler:
        for tur, mdl, hkj in (('kumesiz', ana, baglam.hkj_ana), ('tum', art, baglam.hkj_art)):
            A = mdl.beklenen_yil(yil, veri.M_KENAR)
            B = hkj * (yil / veri.HKJ_YIL)
            tab = 'HKJ07-ana' if tur == 'kumesiz' else 'HKJ07-artci'
            rows.append(satir(baglam, A, B, hedefler[tur], t0, t1, aday=mdl.ad + etiket, taban=tab,
                              hat=hat, donem=dn, hedef=tur, bootstrap=bootstrap))
            if sekil_satiri:
                A2 = A * (B.sum() / A.sum())
                rows.append(satir(baglam, A2, B, hedefler[tur], t0, t1, aday=mdl.ad + etiket + '-sekil',
                                  taban=tab, hat=hat, donem=dn, hedef=tur, bootstrap=bootstrap,
                                  not_='Λ HKJ07 toplamına eşitlendi: yalnız uzay ve büyüklük dağılımı farkı'))
    return rows


def holm(p):
    """Holm düzeltmeli p (artan sıra); eşit aile içinde."""
    m = len(p)
    sira = np.argsort(p)
    out = np.empty(m)
    mx = 0.0
    for r, i in enumerate(sira):
        mx = max(mx, min(1.0, (m - r) * p[i]))
        out[i] = mx
    return out.tolist()


DONEM_P1 = ('2011-01-01', '2021-01-01', 10.0, '2011-2020')
DONEM_P2 = ('2006-01-01', '2011-01-01', 5.0, '2006-2010')


def puan(baglam, secim, bootstrap=BOOTSTRAP, duyarlilik=True):
    hedef = {'kumesiz': baglam.hedef('kumesiz'), 'tum': baglam.hedef('tum')}
    satirlar, ozet = [], {}
    for hat, kesim, donemler in (('adil', '2006-01-01', (DONEM_P1, DONEM_P2)),
                                 ('guncel', '2011-01-01', (DONEM_P1, DONEM_P2))):
        ana, art = modeller(baglam, secim, kesim)
        ozet[hat] = dict(ana=ana.metadata, artci=art.metadata)
        rows = donem_satirlari(baglam, ana, art, hat, donemler, hedef, bootstrap=bootstrap)
        if hat == 'guncel':
            for r in rows:
                if r['donem'] == '2006-2010':
                    r['not_'] = (r.get('not_', '') + ' Model 2006–2010 verisini gördü: veri içi, hüküm değil.').strip()
        satirlar += rows
    # Birincil aile: adil, 2011-2020, iki karşılaştırma, Holm
    aile = [r for r in satirlar if r['hat'] == 'adil' and r['donem'] == '2011-2020'
            and not r['aday'].endswith('-sekil') and r.get('p_tek') is not None]
    for r, hp in zip(aile, holm([r['p_tek'] for r in aile])):
        r['p_holm'] = hp
    dyr = []
    if duyarlilik:
        ana, art = modeller(baglam, secim, '2006-01-01')
        sec_ = secim['sekil_secili']
        alt_mc = {3.0: 3.5, 3.5: 3.0}
        varyant = [
            ('saf-GR', dict(mc_koseli=None)),
            ('mc-diger', dict(mc_ana=alt_mc[secim['mc_oran_ana']], mc_tum=alt_mc[secim['mc_oran_tum']])),
            ('geysers-ters', dict(geysers=not sec_['geysers'])),
        ]
        for ad, kw in varyant:
            a2, r2 = modeller(baglam, secim, '2006-01-01', **kw)
            dyr += donem_satirlari(baglam, a2, r2, 'adil', (DONEM_P1, DONEM_P2), hedef,
                                   etiket='|' + ad, bootstrap=bootstrap, sekil_satiri=False)
        # Reasenberg: eğitimde ve hedefte
        hedef_r = {'kumesiz': baglam.hedef('kumesiz', 'reasenberg'), 'tum': baglam.hedef('tum')}
        a3, r3 = modeller(baglam, secim, '2006-01-01', yontem='reasenberg')
        dyr += donem_satirlari(baglam, a3, r3, 'adil', (DONEM_P1, DONEM_P2), hedef_r,
                               etiket='|reasenberg', bootstrap=bootstrap, sekil_satiri=False)
        ozet['reasenberg_hedef_N_2011_2020'] = int(len(hucre_bin(baglam, hedef_r['kumesiz'], '2011-01-01',
                                                                  '2021-01-01', 4.95, veri.M_KENAR)[1]))
    ozet['hkj07'] = dict(ana_toplam_5yil=float(baglam.hkj_ana.sum()), artci_toplam_5yil=float(baglam.hkj_art.sum()))
    ozet['hedef_N'] = {f'{tur}|{dn}': int(len(hucre_bin(baglam, hedef[tur], t0, t1, 4.95, veri.M_KENAR)[1]))
                       for tur in hedef for (t0, t1, _, dn) in (DONEM_P1, DONEM_P2)}
    return satirlar, dyr, ozet


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('asama', choices=['sec', 'puan'])
    p.add_argument('--cikti', type=Path, default=AD_DIR / 'OLCUM.json')
    p.add_argument('--secim', type=Path, default=None,
                   help='sec: yazılacak seçim (varsayılan $KNOTENLINIE_RUNS/AD/SECIM.json); '
                        'puan: okunacak seçim (varsayılan donmuş records/AD/SECIM.json)')
    p.add_argument('--bootstrap', type=int, default=BOOTSTRAP)
    a = p.parse_args(argv)
    b = Baglam()
    if a.asama == 'sec':
        a.secim = a.secim or AD_DIR / 'SECIM.json'
        a.secim.parent.mkdir(parents=True, exist_ok=True)
        s = sec(b)
        a.secim.write_text(json.dumps(json_temiz(s), ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        print(a.secim, s['sekil_secili'], s['mc_oran_ana'], s['mc_oran_tum'], s['dev'])
        return
    secim = json.loads((a.secim or AD_KAYIT / 'SECIM.json').read_text(encoding='utf-8'))
    satirlar, dyr, ozet = puan(b, secim, a.bootstrap)
    out = dict(surum=1, tohum=TOHUM, bootstrap=a.bootstrap, kural='records/AD/KURAL.md', secim=secim,
               modeller=ozet, satirlar=satirlar, duyarlilik=dyr)
    a.cikti.parent.mkdir(parents=True, exist_ok=True)
    a.cikti.write_text(json.dumps(json_temiz(out), ensure_ascii=False, indent=1, allow_nan=False) + '\n',
                       encoding='utf-8')
    print(a.cikti)


if __name__ == '__main__':
    main()
