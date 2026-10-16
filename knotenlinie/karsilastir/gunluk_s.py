"""S: geçmiş toplam ölçeği, dört sabit R-ortak varyantı ve J çerçevesi."""
import argparse
from dataclasses import replace
import gc
import json
from pathlib import Path
import sys
import time
import numpy as np
import pandas as pd

from knotenlinie.etas import katalog as K
from knotenlinie.etas_uzun.arayuz import DIZIN, TamGecmis
from knotenlinie.etas_uzun.olcek import AYAR_SON, OLCEK_SON, kur, model_kur, olcek_hesapla
from knotenlinie.etas_lm.arayuz import ETASLM
from knotenlinie.ortak_zemin.arayuz import ayar_tabani, utc
from knotenlinie.ortak_zemin.veri import VERI, katalog_dogrula, katalog_oku, sha256, json_yaz
from knotenlinie.yollar import KAYIT, KOSU, kayit_hazirla
from .kosucu import Model, kos, karsilastir
from .ortak4 import AyriGecmis, gecmis_ayari, gecmis_filtrele, ayristir, rss_byte
from .gunluk_j import BAS, SON, TOHUM, esik_kosu, tek_model_ozeti
from .puan import holm

OUT = KOSU / 'S'   # frozen inputs are seeded from records/S/ by kayit_hazirla
KURAL = KAYIT / 'S' / 'KURAL.md'   # frozen rule, read only
FIT = DIZIN/'etas_s_le2005.json'
SCALE = OUT/'OLCEK.json'
VARIANTS = ('R-ortak-kaskad', 'R-ortak-kaskad-olcekli', 'R-ortak-kaskadsiz', 'R-ortak-kaskadsiz-olcekli')
REFS = ('ETAS-LM', 'ortak-ETAS')


def kaynak_oku(son_yil):
    """Glob yok; kalibrasyonda yalnız ≤2010, doğrulamada ≤2015."""
    if son_yil not in (2005, 2010, 2015):
        raise ValueError('Yalnız açık/sabit yıl kesimleri')
    paths = [VERI/'kesik-2015/horus'/f'horus_{y}.txt' for y in range(1985, son_yil+1)]
    raw, report = K.horus_oku([str(p) for p in paths])
    if report['atilan_kesim']:
        raise ValueError('HORUS 2016+ kapısı')
    raw = katalog_dogrula(raw.rename(columns=dict(time_utc='zaman', lat='enlem', lon='boylam', depth_km='derinlik', mag='mw')))
    if (raw.zaman >= pd.Timestamp(f'{son_yil+1}-01-01', tz='UTC')).any():
        raise ValueError('HORUS dosya-yıl kapısı')
    return raw, paths, report


def olcekle(run, c, name):
    """Sabit yüzey ölçeği günlük Poisson skoruna analitik olarak uygulanır."""
    if not np.isfinite(c) or c <= 0:
        raise ValueError('Ölçek pozitif/sonlu olmalı')
    return replace(run, ad=name, beklenen=run.beklenen*c, olay_oranlari=run.olay_oranlari*c,
                   logL=float(run.logL+len(run.olaylar)*np.log(c)+(1-c)*run.beklenen.sum()))


def r_kosu(p, raw, cat, grid, edges, bas, son, kaskad):
    model = model_kur(p, grid, kaskad=kaskad)
    settings = gecmis_ayari(model, 'italya'); settings['derinlik_max'] = 30
    name = VARIANTS[0 if kaskad else 2]
    run = kos([Model(name, TamGecmis(model, raw).beklenen, True, settings)], bas, son, cat, grid, edges,
              bolge='italya', derinlik=(0,30))[name]
    cascade = model.model
    diagnosis = dict(cascade.metadata, ek_nesil=cascade.nesil,
                     son_nesil_ham_payi_ust_max=cascade.max_last_ratio,
                     atlanan_kuyruk_goreli_ust_max=cascade.max_remainder_ratio)
    # Nesil=0 doğrudan analitik gün integrali; zaman kuadratürü gerektirmez.
    if kaskad:
        wrapper = TamGecmis(model, raw)
        a = utc(bas); z = a+pd.Timedelta(days=1)
        f32 = wrapper.beklenen(a,z,cat.iloc[:0],grid,edges)
        cascade.adim = 64
        f64 = wrapper.beklenen(a,z,cat.iloc[:0],grid,edges)
        diagnosis['ilk_gun_zaman_L1'] = float(abs(f32-f64).sum()/f64.sum())
        diagnosis['ilk_gun'] = a.isoformat()
    del model, cascade; gc.collect()
    return run, diagnosis


def kalibre_et(grid):
    """Ölçek kaydı doğrulama verisi açılmadan yazılır."""
    started = time.monotonic()
    rule_hash = sha256(KURAL)
    raw, paths, report = kaynak_oku(2005)
    p = kur(raw, grid)
    p.update(izgara_sha256=sha256(VERI/'ortak/italya_izgara.csv'),
             ayar_girdi_SHA256={str(path):sha256(path) for path in paths}, kural_SHA256=rule_hash)
    json_yaz(FIT, p)
    print('MLE <2006 tamam', p['parametreler'], 'n=',p['dallanma'], 's=',time.monotonic()-started, 'RSS=',rss_byte()/1e9, flush=True)
    del raw; gc.collect()
    raw, history_paths, report = kaynak_oku(2010)
    # Hedef aynı HORUS okuyucusu/maskesi; kos hedef dışını zaten eler.
    scales, diagnosis = {}, {}
    for cascade in (True, False):
        name = 'kaskad' if cascade else 'kaskadsiz'
        run, diag = r_kosu(p,raw,raw,grid,np.array([3.95,np.inf]),AYAR_SON,OLCEK_SON,cascade)
        scales[name] = olcek_hesapla(run,grid)
        diagnosis[name] = diag
        print('ÖLÇEK', name, scales[name], 's=',time.monotonic()-started, 'RSS=',rss_byte()/1e9, flush=True)
        del run; gc.collect()
    sources = history_paths+[FIT,KURAL,VERI/'ortak/italya_izgara.csv']
    out = dict(baslangic=AYAR_SON,bitis_haric=OLCEK_SON,M_alt=3.95,derinlik=[0,30],
               olcekler=scales,parametreler=p,kaskad_tani=diagnosis,horus_okuyucu=report,
               kural_SHA256=rule_hash,kaynak_SHA256={str(path):sha256(path) for path in sources},
               duvar_saniye=time.monotonic()-started,rss_tepe_byte=rss_byte(),python=sys.version,
               not_='2011–2015 açılmadan yazıldı; bu kayıt ölçümden sonra yeniden ayarlanmaz')
    json_yaz(SCALE,out)
    return out


def olcek_yukle():
    scale = json.loads(SCALE.read_text())
    if scale['kural_SHA256'] != sha256(KURAL):
        raise ValueError('Ölçek önkural SHA uyuşmuyor')
    if utc(scale['baslangic']) != utc(AYAR_SON) or utc(scale['bitis_haric']) != utc(OLCEK_SON):
        raise ValueError('Ölçek ayar penceresi uyuşmuyor')
    for path, digest in scale['kaynak_SHA256'].items():
        if sha256(path) != digest:
            raise ValueError('Ölçek kaynak SHA uyuşmuyor: '+path)
    for name in ('kaskad','kaskadsiz'):
        if not np.isfinite(scale['olcekler'][name]['c']) or scale['olcekler'][name]['c'] <= 0:
            raise ValueError('Sabit ölçek geçersiz')
    return scale


def ozetle(runs, grid, edges, clusters, tekrar):
    rows = []
    for alt in (3.95,4.95):
        sub = {name:esik_kosu(run,grid,edges,alt) for name,run in runs.items()}
        summaries = {name:tek_model_ozeti(run,tekrar) for name,run in sub.items()}
        for row in summaries.values():
            row['Lambda_bolu_N'] = row['Lambda']/row['N'] if row['N'] else None
        pairs = {}
        for name in VARIANTS:
            pairs[name] = {}
            for ref in REFS:
                pair = karsilastir(sub[name],sub[ref])
                pair['ayristirma'] = ayristir(sub[name],sub[ref],clusters)
                pairs[name][ref] = pair
        for ref in REFS:
            for field in ('p_T','p_W'):
                adjusted = holm([pairs[name][ref][field] for name in VARIANTS])
                for name,value in zip(VARIANTS,adjusted):
                    pairs[name][ref][field+'_Holm4'] = value
        rows.append(dict(M_alt=alt,modeller=summaries,ciftler=pairs))
    return rows


def olc(grid, scale, tekrar):
    start = time.monotonic()
    raw, paths, report = kaynak_oku(2015)
    cat_path = VERI/'ortak/italya_katalog_le2015.csv'
    cat = katalog_oku(cat_path)
    edges = np.r_[np.round(np.arange(3.95,9.,.1),2),np.inf]
    runs, metadata, diagnosis = {}, {}, {}
    base = ayar_tabani('italya', son='2011-01-01')
    if base.p['katalog_sha256'] != sha256(cat_path):
        raise ValueError('J katalog SHA uyuşmuyor')
    settings = gecmis_ayari(base,'italya'); clusters = gecmis_filtrele(cat,settings)
    runs.update(kos([Model('ortak-ETAS',AyriGecmis(base,cat,settings).beklenen,True,settings)],
                    BAS,SON,cat,grid,edges,bolge='italya',derinlik=(0,30)))
    metadata['ortak-ETAS'] = base.p
    del base; gc.collect(); print('Ortak tamam',time.monotonic()-start,flush=True)
    lm = ETASLM(cat[cat.zaman < utc(BAS)],grid,adim=32,nesil=10)
    box = lm.met.kutu
    settings = dict(sinir=(box[2],box[3],box[0],box[1]),baslangic_yil=2005,derinlik_max=30)
    runs.update(kos([Model('ETAS-LM',lm.beklenen,True,settings)],BAS,SON,cat,grid,edges,bolge='italya',derinlik=(0,30)))
    metadata['ETAS-LM'] = lm.metadata
    del lm; gc.collect(); print('LM tamam',time.monotonic()-start,flush=True)
    p = json.loads((DIZIN/'etas_ortak.json').read_text())
    if (utc(p['ayar_bitis']) != utc(BAS) or utc(p['ayar_max_zaman']) >= utc(BAS) or
            p['izgara_sha256'] != sha256(VERI/'ortak/italya_izgara.csv') or p['katalog_sha256'] != sha256(cat_path)):
        raise ValueError('Donmuş R ayar kapısı')
    for cascade,raw_name,scaled_name in ((True,VARIANTS[0],VARIANTS[1]),(False,VARIANTS[2],VARIANTS[3])):
        name = 'kaskad' if cascade else 'kaskadsiz'
        run, diag = r_kosu(p,raw,cat,grid,edges,BAS,SON,cascade)
        c = scale['olcekler'][name]['c']
        runs[raw_name] = run
        runs[scaled_name] = olcekle(run,c,scaled_name)
        metadata[raw_name] = p
        metadata[scaled_name] = dict(parametre_kaynagi=raw_name,c=c,olcek_penceresi=[AYAR_SON,OLCEK_SON])
        diagnosis[raw_name] = diag
        print(raw_name,'tamam',time.monotonic()-start,'RSS=',rss_byte()/1e9,flush=True)
    rows = ozetle(runs,grid,edges,clusters,tekrar)
    sources = paths+[cat_path,VERI/'ortak/italya_izgara.csv',VERI/'ortak/etas_italya_le2010.json',
                     DIZIN/'etas_ortak.json',FIT,SCALE,KURAL]
    codes = [Path(__file__),Path('knotenlinie/etas_uzun/olcek.py'),Path('knotenlinie/karsilastir/kosucu.py'),
             Path('knotenlinie/karsilastir/puan.py'),Path('knotenlinie/karsilastir/gunluk_j.py'),Path('knotenlinie/karsilastir/ortak4.py')]
    for package in ('etas_uzun','etas_mc25','etas_lm','kaskad','ortak_zemin'):
        codes += sorted(Path('tools',package).glob('*.py'))
    codes += [Path('knotenlinie/etas/model.py'),Path('knotenlinie/etas/katalog.py')]
    return dict(durum='PROVISIONAL; bağımsız skor-kodu incelemesi bekler; kör üstünlük hükmü değil',
                baslangic=BAS,bitis_haric=SON,derinlik=[0,30],hucre=len(grid),varyantlar=VARIANTS,
                olcekler=scale['olcekler'],olcek_kaynak_SHA256=sha256(SCALE),satirlar=rows,
                parametreler=metadata,kaskad_tani=diagnosis,tekrar=tekrar,tohum=TOHUM,M_tohum=TOHUM+1,
                Holm='Her eşik/referans/T-W için dört sabit varyant; ek eşik keşifsel',
                IG_tanimi='ortalama log(lambda_aday/lambda_ref) − (Lambda_aday−Lambda_ref)/N',
                NSM_notu='N Poisson iki kuyruk; S/M sabit N multinomial; adaptif tahminde operasyonel tanı',
                p_notu='İki yönlü eşleştirilmiş T/W; kümelenmede olay bağımsızlığı ihtiyatla okunur',
                kumelenme='J/H4 hemen önceki M≥4.5 ≤30 gün/50 km; integral gruplara dağıtılmaz',
                kapilar='MLE/KDE/b <2006; ölçek <2011; R doğrulama ayarı <2011; her ebeveyn <gün başı; 2016+ yok',
                indirmeler=[],horus_okuyucu=report,kaynak_SHA256={str(path):sha256(path) for path in sources},
                kod_SHA256={str(path):sha256(path) for path in codes},duvar_saniye=time.monotonic()-start,
                rss_tepe_byte=rss_byte(),python=sys.version,numpy=np.__version__,pandas=pd.__version__)


def main():
    kayit_hazirla('S')
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--asama',choices=('ayar','olcum','hepsi'),default='hepsi')
    ap.add_argument('--cikti',type=Path,default=OUT/'OLCUM.json')
    args = ap.parse_args()
    if not (KURAL).exists():
        raise ValueError('Hesaptan önce S/KURAL.md yazılmalı')
    grid = pd.read_csv(VERI/'ortak/italya_izgara.csv')
    if args.asama in ('ayar','hepsi'):
        if SCALE.exists():
            raise ValueError('Ölçek zaten donduruldu; yeniden ayar kapalı')
        kalibre_et(grid)
    if args.asama == 'ayar':
        return
    scale = olcek_yukle()
    out = olc(grid,scale,10000)
    json_yaz(args.cikti,out)
    print(args.cikti,'s=',out['duvar_saniye'],'RSS=',rss_byte()/1e9,flush=True)


if __name__ == '__main__':
    main()
