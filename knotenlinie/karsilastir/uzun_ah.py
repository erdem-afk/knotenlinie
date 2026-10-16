"""Experiment AH — fay tabanlı zamana bağlı uzun vade (İtalya), yerleşiklere ve Z2'ye karşı.

Komutlar: `sec` (≤2005 kurulum, 2006-2010 logL ile dört varyant arasından seçim,
`$KNOTENLINIE_RUNS/AH/SECIM.json`), `puan` (donmuş `records/AH/SECIM.json` seçimi ≤2010
ile yeniden kurulur, 2011-2015 bir kez puanlanır; 2006-2010 satırları da yazılır,
`$KNOTENLINIE_RUNS/AH/OLCUM.json`). Kural: `records/AH/KURAL.md` (puanlamadan önce
yazıldı). Puanlayıcı ilkelleri `uzun_z`'dendir; 2016+ okunmaz.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from knotenlinie.fay_zaman import kaynak as kay
from knotenlinie.fay_zaman.model import FayKatmani, FayZaman
from knotenlinie.karsilastir import uzun_z, uzun_z2
from knotenlinie.karsilastir.puan import tutarlilik
from knotenlinie.uzun_vade.duzgunlestir import kur
from knotenlinie.yollar import KAYIT, KOSU
from knotenlinie.uzun_vade.kumesiz import arka_plan_maskesi

AH_DIR = KOSU / 'AH'       # new AH outputs
AH_KAYIT = KAYIT / 'AH'    # frozen AH record (rule, variant selection), read only
Z_DIR = uzun_z.Z_DIR
VARYANTLAR = [('GR-kapali', 'gr', False), ('GR-BPT', 'gr', True),
              ('KAR-kapali', 'kar', False), ('KAR-BPT', 'kar', True)]
BAG_TOLERANSI = 1.0  # nat
AYARLAR = {  # D (kesirli yıl), katalog kesimi yılı, ayar zaman damgası, hedef dönem
    'ayar2005': dict(D=2006.0, son=2005, ts='2006-01-01', donem='2006-2010',
                     t0='2006-01-01', t1='2011-01-01'),
    'ayar2010': dict(D=2011.0, son=2010, ts='2011-01-01', donem='2011-2015',
                     t0='2011-01-01', t1='2016-01-01'),
}


def z_sekil(bolge, secim, katalog, ts):
    """Z'nin seçtiği şekil, `ts` kesimiyle yeniden kurulur (uzun_z.model_sec'in kesim parametreli kopyası)."""
    cfg = uzun_z.BOLGELER[bolge]
    edges, mmin = cfg['m_kenarlar'], cfg['mmin']
    bas, son = uzun_z.utc(cfg['egitim_baslangic']), uzun_z.utc(ts)
    izgara = pd.read_csv(cfg['izgara'])
    eg = katalog[(katalog.zaman >= bas) & (katalog.zaman < son)]
    ortak = dict(mmin=mmin, m_kenarlar=edges, baslangic=bas, bitis=son,
                 zemin_payi=uzun_z.ZEMIN, yontem='gk74')
    ad = secim['secili']
    if ad == 'U0':
        return kur(eg, izgara, bant_km=float(secim['U0']['ad'].split('-')[1]), ad='U0', **ortak)
    temel = kur(eg, izgara, k_komsu=uzun_z._k_from_ad(secim['U1']['ad']), ad='U1', **ortak)
    if ad == 'U1':
        return temel
    raise ValueError('AH yalnız U0/U1 şekillerini kurar (U3/GEAR1 bu sürümde kapalı)')


def hazirla(bolge, ayar, secim_z):
    """Arka plan (Z2'nin modeli), fay kaynak tablosu ve hedef çerçeve; ayar anı kesimiyle."""
    a = AYARLAR[ayar]
    cfg = uzun_z.BOLGELER[bolge]
    izgara = pd.read_csv(cfg['izgara'])
    katalog = uzun_z.katalog_oku(cfg['katalog'], cfg['derinlik'])
    sh = z_sekil(bolge, secim_z, katalog[katalog.zaman < uzun_z.utc(a['ts'])], a['ts'])
    if bolge != 'italya':
        raise ValueError(f'hazirla: yalnız italya tanımlı, {bolge!r} değil')
    kk, _ = uzun_z2.italya_kumesiz(a['son'])
    tablo, gunluk = kay.italya(a['D'])
    w = uzun_z2.weichert_kestir(bolge, kk, son=a['son'])
    bg = uzun_z2.z_model(sh.sekil, izgara, b=w['b'], rate_m95=w['oran_mref'], mmin=sh.mmin,
                         ad=f'Z2-{ayar}', meta=w)
    tablo = kay.moment_dagit(tablo)
    tam_k, tam_mask = arka_plan_maskesi(katalog, 'gk74')
    return dict(bolge=bolge, ayar=ayar, cfg=cfg, izgara=izgara, katalog=katalog, bg=bg, w=w,
                tablo=tablo, gunluk=gunluk, kumesiz=tam_k[tam_mask], edges=cfg['m_kenarlar'])


def model_kur(h, mfd, bpt, *, ad, alfa=0.5, pay_ust=0.9):
    kat = FayKatmani(h['tablo'], h['izgara'], mfd=mfd, b=h['w']['b'], bpt=bpt, alfa=alfa)
    return FayZaman(kat, h['bg'], ad=ad, pay_ust=pay_ust)


def hedef(h, tur):
    cfg, a = h['cfg'], AYARLAR[h['ayar']]
    frame = h['kumesiz'] if tur == 'kumesiz' else h['katalog']
    return uzun_z.hedefler(frame, h['izgara'], h['edges'], cfg['derinlik'],
                           uzun_z.utc(a['t0']), uzun_z.utc(a['t1']))


def logl_kutu(model, h):
    """Seçim ölçütü: kümesiz hedef, hücre×0,1 kutu Poisson logL, M≥4,95."""
    a = AYARLAR[h['ayar']]
    t0, t1 = uzun_z.utc(a['t0']), uzun_z.utc(a['t1'])
    _, ci, mi = hedef(h, 'kumesiz')
    edges = h['edges']
    k = int(np.searchsorted(edges, 4.95, side='right') - 1)
    dob = model.beklenen(t0, t1, None, h['izgara'], edges)
    obs = uzun_z._gozlem_matris(dob.shape, ci, mi)
    return float(uzun_z.poisson_logl(dob[:, k:], obs[:, k:])), int((mi >= k).sum())


def sec_komut(bolgeler=('italya',)):
    z = json.loads((Z_DIR / 'OLCUM.json').read_text(encoding='utf-8'))
    toplam, ayrinti = {v[0]: 0.0 for v in VARYANTLAR}, {}
    for bolge in bolgeler:
        h = hazirla(bolge, 'ayar2005', z['bolgeler'][bolge]['secim'])
        ayrinti[bolge] = dict(w=h['w']['b'], oran=h['w']['oran_mref'], gunluk={
            k: (v if not isinstance(v, list) else len(v)) for k, v in h['gunluk'].items()})
        z2 = logl_kutu(h['bg'], h)
        ayrinti[bolge]['Z2'] = z2[0]
        ayrinti[bolge]['N'] = z2[1]
        for ad, mfd, bpt in VARYANTLAR:
            m = model_kur(h, mfd, bpt, ad=ad)
            ll, _ = logl_kutu(m, h)
            ayrinti[bolge][ad] = ll
            ayrinti[bolge][ad + '_tani'] = {k: v for k, v in m.son_tani.items() if k in ('td_toplam', 'poi_toplam')}
            toplam[ad] += ll
    en = max(toplam.values())
    bagli = [v[0] for v in VARYANTLAR if toplam[v[0]] >= en - BAG_TOLERANSI]
    secili = bagli[0]  # VARYANTLAR sırası = bağ önceliği
    out = dict(toplam_logL=toplam, en_iyi=en, tolerans=BAG_TOLERANSI, bagli=bagli, secili=secili,
               z2_toplam=sum(ayrinti[b]['Z2'] for b in bolgeler), ayrinti=ayrinti,
               zaman='%s' % pd.Timestamp.utcnow().isoformat())
    AH_DIR.mkdir(parents=True, exist_ok=True)
    (AH_DIR / 'SECIM.json').write_text(json.dumps(uzun_z.json_temiz(out), ensure_ascii=False, indent=2) + '\n',
                                       encoding='utf-8')
    return out


def satir(lam_a, lam_r, ci, mi, k, n_hucre, *, bootstrap, ad_a, ad_r, bolge, donem, tur):
    """Bir (aday, referans) için hüküm satırı: M≥4,95; IG, olay/integral, şekil satırı, N/S/M, güç."""
    sec = mi >= k
    ci_k = ci[sec]
    obs = uzun_z._gozlem_matris((n_hucre, 1), ci_k, np.zeros(len(ci_k), int))
    La, Lr = float(lam_a.sum()), float(lam_r.sum())
    r = uzun_z.olay_ig(lam_a[ci_k], lam_r[ci_k], La, Lr, tekrar=bootstrap)
    r.update(aday=ad_a, taban=ad_r, bolge=bolge, donem=donem, hedef=tur, esik=4.95, N=int(obs.sum()),
             Lambda_aday=La, Lambda_taban=Lr,
             logL_aday=uzun_z.poisson_logl(lam_a[:, None], obs),
             logL_taban=uzun_z.poisson_logl(lam_r[:, None], obs),
             NSM=tutarlilik(lam_a[:, None], obs, tekrar=2000, tohum=uzun_z.TOHUM))
    uzun_z._poisson_kimlik(r)
    if r['durum'] == 'tanımlı':
        c = Lr / La
        s = uzun_z.olay_ig(lam_a[ci_k] * c, lam_r[ci_k], Lr, Lr, tekrar=bootstrap)
        r['IG_sekil'] = s['IG']
        r['SE_sekil'] = s['SE_blok']
        r['z_sekil'] = s['z']
    return r


def olc(h, modeller, *, bootstrap=2000):
    """Her model × {kümesiz, bütün} × {tabanlar + Z2}; M≥4,95 satırları."""
    a = AYARLAR[h['ayar']]
    t0, t1 = uzun_z.utc(a['t0']), uzun_z.utc(a['t1'])
    edges, izgara, cfg = h['edges'], h['izgara'], h['cfg']
    k = int(np.searchsorted(edges, 4.95, side='right') - 1)
    n = len(izgara)
    ref = {'Z2': h['bg'].beklenen(t0, t1, None, izgara, edges)[:, k:].sum(axis=1)}
    for ad, yol in cfg['tabanlar']:
        tb = uzun_z.taban_yukle(ad, yol)
        ref[ad] = tb.beklenen(t0, t1, None, izgara, tb.m_kenarlar).sum(axis=1)
    rows = []
    for m in modeller:
        lam_a = m.beklenen(t0, t1, None, izgara, edges)[:, k:].sum(axis=1)
        for tur in ('kumesiz', 'tum'):
            _, ci, mi = hedef(h, tur)
            for rad, lam_r in ref.items():
                rows.append(satir(lam_a, lam_r, ci, mi, k, n, bootstrap=bootstrap, ad_a=m.ad,
                                  ad_r=rad, bolge=h['bolge'], donem=a['donem'], tur=tur))
    return rows


def puan_komut(bootstrap=2000):
    z = json.loads((Z_DIR / 'OLCUM.json').read_text(encoding='utf-8'))
    secim = json.loads((AH_KAYIT / 'SECIM.json').read_text(encoding='utf-8'))
    ad_sec = secim['secili']
    v = {x[0]: x for x in VARYANTLAR}
    sonuc = dict(surum=1, tohum=uzun_z.TOHUM, bootstrap=bootstrap, kural='records/AH/KURAL.md', secili=ad_sec,
                 bolgeler={})
    for bolge in ('italya',):
        sz = z['bolgeler'][bolge]['secim']
        b = dict(satirlar={}, duyarlilik=[])
        for ayar in ('ayar2005', 'ayar2010'):
            h = hazirla(bolge, ayar, sz)
            ana = model_kur(h, v[ad_sec][1], v[ad_sec][2], ad='AH-' + ad_sec)
            rows = olc(h, [ana], bootstrap=bootstrap)
            b['satirlar'][AYARLAR[ayar]['donem']] = rows
            b.setdefault('model', {})[AYARLAR[ayar]['donem']] = dict(
                ana.metadata, tani=ana.son_tani, weichert_b=h['w']['b'], weichert_oran=h['w']['oran_mref'],
                gunluk=h['gunluk'], kaynak_tablo=dict(
                    n=len(h['tablo']), iss=int((h['tablo'].katman == 'ISS').sum()),
                    iss_son_bilinen=int(h['tablo'][h['tablo'].katman == 'ISS'].son_yil.notna().sum()),
                    mdot_toplam=float(h['tablo'].mdot.sum())))
            if ayar == 'ayar2010':
                dus = [model_kur(h, v[x][1], v[x][2], ad='AH-' + x) for x in v]
                dus.append(model_kur(h, v[ad_sec][1], v[ad_sec][2], ad='AH-' + ad_sec + '-pay0.5', pay_ust=0.5))
                if v[ad_sec][2]:
                    for al in (0.3, 0.7):
                        dus.append(model_kur(h, v[ad_sec][1], True, ad=f'AH-{ad_sec}-a{al}', alfa=al))
                b['duyarlilik'] = olc(h, dus, bootstrap=bootstrap)
        sonuc['bolgeler'][bolge] = b
    AH_DIR.mkdir(parents=True, exist_ok=True)
    (AH_DIR / 'OLCUM.json').write_text(
        json.dumps(uzun_z.json_temiz(sonuc), ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    return sonuc


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('komut', choices=['sec', 'puan'])
    p.add_argument('--bootstrap', type=int, default=2000)
    args = p.parse_args(argv)
    if args.komut == 'sec':
        o = sec_komut()
        print(json.dumps(uzun_z.json_temiz({k: o[k] for k in ('toplam_logL', 'bagli', 'secili', 'z2_toplam')}), indent=1))
    else:
        puan_komut(args.bootstrap)
        print(AH_DIR / 'OLCUM.json')


if __name__ == '__main__':
    main()
