"""R: iki sabit uzun-maskeli ETAS varyantının J/N çerçevesinde ölçümü."""
import argparse
import gc
import json
from pathlib import Path
import sys
import time
import numpy as np
import pandas as pd
from knotenlinie.etas import model as M
from knotenlinie.etas import katalog as K
from knotenlinie.etas_uzun.mle import Olabilirlik, ayarla, tamlik, b_ayarla
from knotenlinie.etas_uzun.maske import arka_plan_sec
from knotenlinie.etas_uzun.arayuz import DIZIN, ebeveynler, yukle, TamGecmis
from knotenlinie.etas_mc25.arayuz import yukle as n_yukle, SigGecmis
from knotenlinie.ortak_zemin.ayar import dallanma
from knotenlinie.ortak_zemin.arayuz import ayar_tabani
from knotenlinie.ortak_zemin.veri import VERI, katalog_oku, katalog_dogrula, hucre_indeks, sha256, json_yaz
from knotenlinie.yollar import KOSU, kayit_hazirla
from knotenlinie.etas_lm.arayuz import ETASLM
from .kosucu import Model, kos, karsilastir, utc
from .ortak4 import AyriGecmis, gecmis_ayari, gecmis_filtrele, ayristir, rss_byte
from .gunluk_j import BAS, SON, TOHUM, esik_kosu, tek_model_ozeti
from .puan import holm

OUT = KOSU / 'R'   # kayit_hazirla seeds frozen inputs from records/R/ when that folder exists
VARIANTS = ('R-ortak-kaskad', 'R-lm-kaskad')


def kaynak_oku():
    """Ham HORUS yalnız açık 1985–2015 yılları; ortak maskeli hedef değişmez."""
    paths = [VERI/'kesik-2015/horus'/f'horus_{y}.txt' for y in range(1985, 2016)]
    raw, report = K.horus_oku([str(p) for p in paths])
    if report['atilan_kesim']: raise ValueError('HORUS 2016+ kapısı')
    raw = katalog_dogrula(raw.rename(columns=dict(time_utc='zaman', lat='enlem', lon='boylam', depth_km='derinlik', mag='mw')))
    return raw, paths, report


def kur(raw, grid, maksiter):
    start = time.monotonic(); epoch = utc('1985-01-01T00:00:00Z')
    kutu = (grid.enlem_min.min(), grid.enlem_max.max(), grid.boylam_min.min(), grid.boylam_max.max())
    d = ebeveynler(raw, kutu, BAS)
    target = d[hucre_indeks(d, grid) >= 0].reset_index(drop=True)
    mc = np.where(target.zaman < utc('2005-01-01T00:00:00Z'), 3.1, 2.5)
    # Aynı sabit b: kendi Mc'sinden fazlanın ortak yordamla GR MLE'si.
    bmeta = b_ayarla(target.mw.to_numpy(), mc)
    b = bmeta['deger']
    hist = arka_plan_sec(target, grid, kutu, utc(BAS))
    t = ((d.zaman-epoch)/pd.Timedelta(days=1)).to_numpy(float)
    T = float((utc(BAS)-epoch)/pd.Timedelta(days=1)); change = float((utc('2005-01-01T00:00:00Z')-epoch)/pd.Timedelta(days=1))
    u = M.arka_plan_degeri(d.boylam.to_numpy(), d.enlem.to_numpy(), hist)
    L = Olabilirlik(t, d.mw.to_numpy(), d.boylam.to_numpy(), d.enlem.to_numpy(), b, T, change, grid, kutu, u)
    print('KUR N ebeveyn/hedef/dış', len(d), len(target), len(d)-len(target), 'çift', L.cift,
          'sınır', L.mask.kenar, 'KDE', hist['bant_km'], hist['zemin_payi'], 'RSS', rss_byte()/1e9, flush=True)
    DIZIN.mkdir(parents=True, exist_ok=True)
    for tur in ('ortak', 'lm'):
        fit = ayarla(L, tur, maksiter=maksiter)
        fit.update(mc=2.5, b=bmeta, baslangic_yili=1985, ayar_baslangic=epoch.isoformat(), ayar_bitis=BAS,
                   ayar_max_zaman=d.zaman.max().isoformat(), ayar_n=len(d), hedef_n=len(target), dis_ebeveyn_n=len(d)-len(target),
                   kutu=kutu, arka_plan=hist, metrik=M.yerel_metrik(kutu).kayit(), normalizasyon=M.NORMALIZASYON,
                   uzay_ayar_destegi='CSEP İtalya maskesi; dış dikdörtgen yalnız ebeveyn erişim sınırı',
                   tamlik=dict(donemler=[dict(bas='1985-01-01', son='2005-01-01', Mc=3.1), dict(bas='2005-01-01', son='2011-01-01', Mc=2.5)],
                               referans_Mc=2.5, eksik_ebeveyn='impute edilmez; gözlenen-ebeveyn koşullu ETAS'),
                   katalog_sha256=sha256(VERI/'ortak/italya_katalog_le2015.csv'), izgara_sha256=sha256(VERI/'ortak/italya_izgara.csv'),
                   duvar_saniye=time.monotonic()-start)
        json_yaz(DIZIN/f'etas_{tur}.json', fit)
        print('MLE', tur, fit['parametreler'], 'n', fit['dallanma'], 's', time.monotonic()-start, 'RSS', rss_byte()/1e9, flush=True)
    del L; gc.collect()


def olc(cat, raw, grid, args):
    start = time.monotonic(); edges = np.r_[np.round(np.arange(3.95, 9., .1), 2), np.inf]
    runs = {}; metadata = {}; convergence = {}
    base = ayar_tabani('italya', son='2011-01-01')
    if base.p['katalog_sha256'] != sha256(VERI/'ortak/italya_katalog_le2015.csv'): raise ValueError('J katalog hash')
    settings = gecmis_ayari(base, 'italya'); clusters = gecmis_filtrele(cat, settings)
    runs.update(kos([Model('ortak-ETAS', AyriGecmis(base, cat, settings).beklenen, True, settings)], BAS, SON, cat, grid, edges, bolge='italya', derinlik=(0,30)))
    metadata['ortak-ETAS'] = base.p
    del base; gc.collect(); print('ortak bitti', time.monotonic()-start, flush=True)
    lm = ETASLM(cat[cat.zaman < utc(BAS)], grid, adim=32, nesil=10)
    box = lm.met.kutu; settings = dict(sinir=(box[2], box[3], box[0], box[1]), baslangic_yil=2005, derinlik_max=30)
    runs.update(kos([Model('ETAS-LM', lm.beklenen, True, settings)], BAS, SON, cat, grid, edges, bolge='italya', derinlik=(0,30)))
    metadata['ETAS-LM'] = lm.metadata
    del lm; gc.collect(); print('LM bitti', time.monotonic()-start, flush=True)
    n = n_yukle('ortak', grid, kaskad=True, adim=32, nesil=10)
    settings = gecmis_ayari(n.taban, 'italya'); settings['derinlik_max'] = 30
    runs.update(kos([Model('N-ortak-kaskad', SigGecmis(n, cat, settings).beklenen, True, settings)], BAS, SON, cat, grid, edges, bolge='italya', derinlik=(0,30)))
    metadata['N-ortak-kaskad'] = n.taban.p
    del n; gc.collect(); print('N bitti', time.monotonic()-start, flush=True)
    for tur, name in zip(('ortak','lm'), VARIANTS):
        model = yukle(tur, grid, adim=args.adim, nesil=args.nesil)
        settings = gecmis_ayari(model, 'italya'); settings['derinlik_max'] = 30
        runs.update(kos([Model(name, TamGecmis(model, raw).beklenen, True, settings)], BAS, SON, cat, grid, edges, bolge='italya', derinlik=(0,30)))
        metadata[name] = model.p
        cascade = model.model
        convergence[name] = dict(cascade.metadata, son_nesil_ham_payi_ust_max=cascade.max_last_ratio,
                                 atlanan_kuyruk_goreli_ust_max=cascade.max_remainder_ratio)
        h = ebeveynler(raw, model.kutu, BAS); a = utc(BAS); z = a+pd.Timedelta(days=1)
        coarse = model.beklenen(a,z,h,grid,edges); cascade.adim *= 2
        fine = model.beklenen(a,z,h,grid,edges)
        convergence[name]['ilk_gun_zaman_L1'] = float(abs(coarse-fine).sum()/fine.sum())
        print(name, 'bitti', time.monotonic()-start, 'RSS', rss_byte()/1e9, flush=True)
        del model, cascade; gc.collect()
    rows = []
    for alt in (3.95,4.95):
        sub = {name:esik_kosu(run,grid,edges,alt) for name,run in runs.items()}
        summaries = {name:tek_model_ozeti(run,args.tekrar) for name,run in sub.items()}
        for row in summaries.values(): row['Lambda_bolu_N'] = row['Lambda']/row['N'] if row['N'] else None
        pairs = {}
        for name in VARIANTS:
            pairs[name] = {}
            for ref in ('ETAS-LM','ortak-ETAS','N-ortak-kaskad'):
                pair = karsilastir(sub[name],sub[ref]); pair['ayristirma'] = ayristir(sub[name],sub[ref],clusters)
                pairs[name][ref] = pair
        for ref in ('ETAS-LM','ortak-ETAS','N-ortak-kaskad'):
            for field in ('p_T','p_W'):
                adjusted = holm([pairs[name][ref][field] for name in VARIANTS])
                for name,value in zip(VARIANTS,adjusted): pairs[name][ref][field+'_Holm2'] = value
        rows.append(dict(M_alt=alt, modeller=summaries, ciftler=pairs))
    return dict(satirlar=rows,parametreler=metadata,kaskad_tani=convergence,duvar_saniye=time.monotonic()-start)


def main():
    kayit_hazirla('R')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama', choices=('ayar','olcum','hepsi'), default='hepsi')
    ap.add_argument('--maksiter', type=int, default=300)
    ap.add_argument('--adim', type=int, default=32); ap.add_argument('--nesil', type=int, default=10)
    ap.add_argument('--tekrar', type=int, default=10000)
    args = ap.parse_args(); OUT.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    grid = pd.read_csv(VERI/'ortak/italya_izgara.csv'); raw, paths, report = kaynak_oku()
    if args.asama in ('ayar','hepsi'): kur(raw,grid,args.maksiter)
    if args.asama == 'ayar': return
    cat = katalog_oku(VERI/'ortak/italya_katalog_le2015.csv')
    result = olc(cat,raw,grid,args)
    code = list(Path('knotenlinie/etas_uzun').glob('*.py'))+[Path(__file__),Path('knotenlinie/karsilastir/kosucu.py'),Path('knotenlinie/karsilastir/puan.py'),Path('knotenlinie/kaskad/arayuz.py'),Path('knotenlinie/kaskad/cekirdek.py'),Path('knotenlinie/etas/model.py'),Path('knotenlinie/etas_mc25/mle.py')]
    sources = paths+[VERI/'ortak/italya_katalog_le2015.csv',VERI/'ortak/italya_izgara.csv',VERI/'ortak/etas_italya_le2010.json']+list(DIZIN.glob('etas_*.json'))+[VERI/'ortak/mc25/etas_ortak.json']
    result.update(durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler; kör üstünlük hükmü değil',
                  baslangic=BAS,bitis_haric=SON,derinlik=[0,30],hucre=len(grid),varyantlar=VARIANTS,tekrar=args.tekrar,tohum=TOHUM,M_tohum=TOHUM+1,
                  Holm='Her eşik/referans/T-W için iki sabit varyant; ek eşik keşifsel',
                  IG_tanimi='ortalama log(lambda_aday/lambda_ref) − (Lambda_aday−Lambda_ref)/N',
                  NSM_notu='N Poisson iki kuyruk; S/M sabit N multinomial; adaptif tahminde operasyonel tanı, koşulsuz ETAS testi değil',
                  p_notu='İki yönlü eşleştirilmiş T/W; olay bağımsızlığı varsayımı kümelenmede ihtiyatlı okunur',
                  kumelenme='J/H4 hemen önceki M≥4.5 ≤30 gün/50 km; integral gruplara dağıtılmaz',
                  kapilar='Ham HORUS 1985–2015 açık yıllar; MLE/KDE/b <2011; her ebeveyn kendi Mc ve [0,30), maskenin dışı ebeveyn olabilir; 2016+ erişim yok',
                  horus_okuyucu=report,kaynak_SHA256={str(p):sha256(p) for p in sources},kod_SHA256={str(p):sha256(p) for p in code},
                  toplam_duvar_saniye=time.monotonic()-start,rss_tepe_byte=rss_byte(),python=sys.version,numpy=np.__version__,pandas=pd.__version__)
    json_yaz(OUT/'OLCUM.json',result)
    print(OUT/'OLCUM.json','RSS',rss_byte()/1e9,flush=True)

if __name__ == '__main__': main()
