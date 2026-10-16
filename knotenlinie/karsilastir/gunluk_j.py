"""Deney J: 2011–2015 ortak ETAS − ETAS-LM yaklaşık yeniden kurulum."""
from __future__ import annotations

import argparse
from dataclasses import replace
import gc
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np
import pandas as pd
from scipy.special import gammaln

from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.etas_lm.arka_plan import SON as AYAR_SON, kur
from knotenlinie.etas_lm.cekirdek import D, radyal_kutle
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, sha256
from knotenlinie.yollar import KOSU, kayit_hazirla
from .kosucu import Model, kos, karsilastir, olay_kutulari, utc
from .ortak4 import AyriGecmis, gecmis_ayari, gecmis_filtrele, ayristir
from .komut import json_temiz

OUT = KOSU / 'J'   # kayit_hazirla seeds frozen inputs from records/J/ when that folder exists
BAS, SON = '2011-01-01T00:00:00Z', '2016-01-01T00:00:00Z'
TOHUM = 20261005


def esik_kosu(run, grid, edges, alt):
    """Tahminleri tekrar hesaplamadan günlük skorun üst-M alt uzayı."""
    j = int(np.flatnonzero(np.isclose(edges[:-1], alt, rtol=0, atol=1e-10))[0])
    keep = run.olaylar.mw.to_numpy(float) >= alt-1e-12
    events, ci, mi = olay_kutulari(run.olaylar, grid, edges[j:], (0, 30))
    # Float kutulama ile aynı seçilen olay dizisi şart.
    if not events.equals(run.olaylar.loc[keep].reset_index(drop=True)):
        raise ValueError('Alt eşik olay sırası uyuşmuyor')
    rates = run.olay_oranlari[keep]
    expected, observed = run.beklenen[:, j:], run.gozlem[:, j:]
    day = ((events.zaman-utc(BAS))/pd.Timedelta(days=1)).to_numpy(float).astype(int)
    _, n = np.unique(np.column_stack([day, ci, mi]), axis=0, return_counts=True)
    ll = float(np.log(rates).sum()-expected.sum()-gammaln(n+1).sum()) if (rates > 0).all() else -np.inf
    frame = run.cerceve[:3] + (run.cerceve[3] + f'-M{alt}',) + run.cerceve[4:]
    return replace(run, beklenen=expected, gozlem=observed, olay_oranlari=rates,
                   logL=ll, olaylar=events, cerceve=frame)


def tek_model_ozeti(run, tekrar):
    return dict(N=len(run.olaylar), Lambda=float(run.beklenen.sum()), logL=run.logL,
                NSM=run.tutarlilik(tekrar=tekrar, tohum=TOHUM))


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1 if sys.platform == 'darwin' else 1024)


def main():
    kayit_hazirla('J')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cikti', type=Path, default=OUT/'OLCUM.json')
    ap.add_argument('--tekrar', type=int, default=10000)
    ap.add_argument('--adim', type=int, default=32)
    ap.add_argument('--nesil', type=int, default=10)
    args = ap.parse_args()
    start = time.monotonic()
    shared = VERI/'ortak'
    cat_path = shared/'italya_katalog_le2015.csv'
    cat = katalog_oku(cat_path)
    base = ayar_tabani('italya', son='2011-01-01')
    if sha256(cat_path) != base.p['katalog_sha256']:
        raise ValueError('Ortak katalog hash uyuşmuyor')
    grid = base.izgara
    edges = np.round(np.arange(3.95, 9.0, .1), 2)
    edges = np.r_[edges, np.inf]  # [8.95,+inf), H4 ile aynı son kutu.
    ayar = gecmis_ayari(base, 'italya')
    wrapped = AyriGecmis(base, cat, ayar)
    run_base = kos([Model('ortak-ETAS', wrapped.beklenen, True, ayar)], BAS, SON, cat, grid, edges, bolge='italya', derinlik=(0, 30))['ortak-ETAS']
    base_params = dict(mc=base.mc, b=base.b, gecmis=ayar)
    clusters = gecmis_filtrele(cat, ayar)
    del base, wrapped
    gc.collect()
    print('Ortak taban tamamlandı', time.monotonic()-start, flush=True)
    lm = ETASLM(cat[cat.zaman < AYAR_SON], grid, adim=args.adim, nesil=args.nesil)
    box = lm.met.kutu
    history_settings = dict(sinir=(box[2], box[3], box[0], box[1]), baslangic_yil=2005, derinlik_max=30)
    run_lm = kos([Model('ETAS-LM-yeniden-kurulum', lm.beklenen, True, history_settings)], BAS, SON, cat, grid, edges, bolge='italya', derinlik=(0, 30))['ETAS-LM-yeniden-kurulum']
    metadata = dict(lm.metadata, son_nesil_ham_payi_ust_max=lm.max_last_ratio)
    # Sayısal yakınsama tanısı: doğrulama ilk günü, parametre seçimi değildir.
    h = cat[cat.zaman < utc(BAS)]
    a, z = utc(BAS), utc(BAS)+pd.Timedelta(days=1)
    f32 = lm.beklenen(a, z, h, grid, edges)
    lm.adim = args.adim*2
    f64 = lm.beklenen(a, z, h, grid, edges)
    convergence = dict(gun=BAS, adimlar=[args.adim, args.adim*2],
                       Lambda=[float(f32.sum()), float(f64.sum())],
                       goreli_L1=float(np.abs(f32-f64).sum()/f64.sum()))
    del lm
    gc.collect()
    rows = []
    for alt in (3.95, 4.95):
        b = esik_kosu(run_base, grid, edges, alt)
        l = esik_kosu(run_lm, grid, edges, alt)
        pair = karsilastir(b, l)
        pair['ayristirma'] = ayristir(b, l, clusters)
        rows.append(dict(M_alt=alt, hedef='HORUS homojen Mw; INGV ML ile özdeş değil',
                         ortak=tek_model_ozeti(b, args.tekrar), ETAS_LM=tek_model_ozeti(l, args.tekrar), cift=pair))
    # Makalenin özgün öğrenme aralığındaki HORUS farkı da sayısal olarak açık.
    published_end = pd.Timestamp('2009-06-01', tz='UTC')
    _, _, learned = kur(cat[cat.zaman < published_end], grid, son=published_end)
    radial_half = D*np.sqrt(3)
    check = dict(figur4b=dict(makale_yari_kutle_yaricap_km_yaklasik=2, yeniden_km=float(radial_half),
                              goreli_yaricap_farki=float(radial_half/2-1), kod_kutlesi_2km=float(radyal_kutle(2))),
                 tablo1_fig3=dict(makale_N=2100, HORUS_N=learned['N'], N_goreli_fark=learned['N']/2100-1,
                                 makale_mu_yil=237, yeniden_mu_yil=learned['mu_yil'],
                                 makale_arka_plan_payi=.54, yeniden_payi=learned['arka_plan_payi'],
                                 yeniden_not='Mu ve pay yalnız HORUS/bant farklılığının tanısı; hedefe göre kalibrasyon yok'),
                 zaman_yakinsama=convergence)
    sources = [cat_path, shared/'italya_izgara.csv', shared/'etas_italya_le2010.json']
    sources += sorted((OUT/'kaynaklar').glob('*.pdf'))
    codes = sorted(Path('knotenlinie/etas_lm').glob('*.py')) + [Path(__file__)]
    out = dict(durum='PROVISIONAL; yayımlanmış operasyonel tahmin değil; bağımsız skor incelemesi bekler',
               baslangic=BAS, bitis_haric=SON, derinlik=[0,30], hucre=len(grid),
               m_kenarlar=[float(e) if np.isfinite(e) else '+inf' for e in edges], ortak_ayar=base_params, ETAS_LM=metadata,
               yeniden_kurulum_kontrolu=check, satirlar=rows, tekrar=args.tekrar, tohum=TOHUM,
               IG_tanimi='ortak − LM: ortalama log(lambda_ortak/lambda_LM) − (Lambda_ortak−Lambda_LM)/N',
               NSM_notu='N Poisson çift kuyruk; S/M sabit N multinomial 10000, zamandan toplanmış oran. Günlük adaptif model için operasyonel tanı; koşulsuz ETAS testi değil.',
               p_notu='Ham iki yönlü T/W; kümelenme altında bağımsızlık varsayımı ihtiyatlı okunur; üstünlük hükmü değil.',
               kumelenme_tanimi='H4: aynı HORUS okuyucusunda hemen önceki M>=4.5, tam zaman <olay, <=30gün/50km; integral ayrı.',
               kapilar='Yalnız 2015 sonuna kadar katalog; ayar <2011; gün başı geçmiş; 2016+ yayın/olay içerikleri açılmadı.',
               STEP_LG=dict(durum='eklenmedi', sebep='Özgün kod/tahmin bulunmadı; 2010 yönteminde güncellenen generic/sequence/spatial model ve AIC ağırlıkları, STEP declustering ve ayrı CSI/BSI arka-plan girdileri gerekir; basit Omori kopyası eşdeğer olmaz.'),
               kaynak_SHA256={str(p):sha256(p) for p in sources}, kod_SHA256={str(p):sha256(p) for p in codes},
               duvar_saniye=time.monotonic()-start, rss_tepe_byte=rss(), python=sys.version, numpy=np.__version__, pandas=pd.__version__)
    args.cikti.write_text(json.dumps(json_temiz(out), ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    print(args.cikti, 's=',out['duvar_saniye'], 'RSS=',rss()/1e9, flush=True)


if __name__ == '__main__':
    main()
