"""C2 koşucusu: python -m knotenlinie.eepas.c2 --paket records/C/zemin2.json.

T'nin ETAS callable'ı doğrudan kullanılır; ETAS parametre ayarı/kopya model yok.
Şema alanları açık teslim eşlemesiyle okunur, eksik alan sessiz tahmin edilmez.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
from dataclasses import asdict

import numpy as np
import pandas as pd
from scipy.special import gammaln

from .model import Parametreler, ArkaPlan, EEPAS
from .katalog import kesik_oku
from .janus import agirlik_ayarla
from .ortak import (Alan, GecmisFiltresi, FiltreliModel, OrtakJanus, tamlik_sec,
                    EEPASOnhesap, eepas_ayarla_ortak, gunluk_puan, olcum_satiri,
                    AYAR_SONU, KESIM, utc, GUN)

from knotenlinie.yollar import KAYIT, KOSU, VERI  # noqa: E402

ORTAK = VERI / 'ortak'
C = KOSU / 'C'          # C2 outputs; the frozen input package is records/C/zemin2.json


def _veri_yolu(yol):
    """A package path: absolute as written, otherwise relative to the data root."""
    p = Path(yol)
    return p if p.is_absolute() else VERI / p


def _veri_goreli(yol):
    """Data-root-relative string for a package (absolute if outside the data root)."""
    try:
        return str(Path(yol).resolve().relative_to(Path(VERI).resolve()))
    except ValueError:
        return str(yol)


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def yaz(path, obj):
    path = Path(path)
    # Koşu çıktısı yalnız C altında.
    path.resolve().relative_to(C.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def alan_degeri(obj, anahtar):
    for key in anahtar.split('.'):
        obj = obj[key]
    return obj


def t_model_yukle(yol):
    """Deney T kodunu salt-okur import et; kopyalama/ETAS yeniden ayarı yok."""
    module = importlib.import_module('knotenlinie.ortak_zemin.arayuz')
    path = Path(yol)
    cfg = json.loads(path.read_text(encoding='utf-8'))
    from knotenlinie.etas import model as ETAS
    if sha256(ETAS.__file__) != cfg['kod_sha256']['knotenlinie/etas/model.py']:
        raise ValueError('T ayarındaki ETAS çekirdek kodu değişmiş')
    return module.model_yukle(cfg['bolge'], path.parent)


def etas_teslim_oku(spec):
    path = _veri_yolu(spec['dosya'])
    if sha256(path) != spec['sha256']:
        raise ValueError('Ortak ETAS sha256 teslimle eşleşmiyor')
    cfg = json.loads(path.read_text(encoding='utf-8'))
    if spec['yukleyici'] == 'knotenlinie.eepas.c2:t_model_yukle':
        metadata = path.parent/'kataloglar.json'
        if sha256(metadata) != spec['katalog_metadata_sha256']:
            raise ValueError('T katalog/derinlik teslimi değişmiş')
        report = json.loads(metadata.read_text(encoding='utf-8'))[cfg['bolge']]
        for key in ('katalog_sha256', 'izgara_sha256'):
            if cfg[key] != report[key]:
                raise ValueError('T katalog/ızgara ve ETAS teslimi eşleşmiyor')
        # T veri.kataloglari_yaz açık take: derinlik>=0 ve derinlik<=70/40.
        cfg['katalog_teslim'] = {'derinlik_min': 0., 'derinlik_max': report['derinlik_ust_km'],
                                'ust_dahil': True}
    keys = spec['anahtarlar']
    cutoff = utc(alan_degeri(cfg, keys['ayar_bitis']))
    branch = float(alan_degeri(cfg, keys['dallanma']))
    success = alan_degeri(cfg, keys['basari'])
    if pd.isna(cutoff) or cutoff > AYAR_SONU or not 0 <= branch < 1 or success is not True:
        raise ValueError('T: <=2010, yakınsamış alt-kritik dondurulmuş ETAS gerekli')
    filt = {k: alan_degeri(cfg, keys[k]) for k in ('baslangic', 'derinlik_min', 'derinlik_max', 'ust_dahil')}
    if not isinstance(filt['ust_dahil'], bool):
        raise ValueError('T derinlik üst sınırı dahil bayrağı bool olmalı')
    filtre = GecmisFiltresi(**filt)
    mod, name = spec['yukleyici'].split(':')
    factory = getattr(importlib.import_module(mod), name)
    model = factory(str(path))
    callback = model.beklenen if hasattr(model, 'beklenen') else model
    if not callable(callback):
        raise TypeError('T ETAS yükleyicisi beklenen callable döndürmeli')
    if sha256(path) != spec['sha256']:
        raise ValueError('ETAS yüklemede dondurulmuş dosya değişti')
    return callback, filtre


def dosyadan(yol, tur='janus'):
    """C2 model paketi -> filtreli bağımsız ortak callable; T kodu import edilebilir olmalı."""
    cfg = json.loads(Path(yol).read_text(encoding='utf-8'))
    if not cfg['hazir'] or utc(cfg['ayar_bitis']) > AYAR_SONU:
        raise ValueError('Yakınsamış <=2010 C2 ayarı gerekli')
    alan = Alan(pd.DataFrame(cfg['izgara']), cfg['m_kenarlar'])
    et, filt = etas_teslim_oku(cfg['etas_teslim'])
    if asdict(filt) != cfg['gecmis_filtresi']:
        raise ValueError('T ve C2 geçmiş filtreleri değişmiş')
    p = Parametreler(**cfg['eepas']['parametreler'])
    if p.mu < cfg['eepas']['ppe_mu_alt'] or cfg['eepas']['ppe_mu_alt'] <= 0:
        raise ValueError('C2 PPE tabanı korunmalı')
    bg = ArkaPlan(alan.kutu, pd.DataFrame(cfg['ppe_merkezler'], columns=['boylam', 'enlem']),
                  cfg['ppe_bant'], cfg['ppe_duzgun_pay'])
    ep = EEPAS(p, alan.kutu, bg)
    callbacks = {'eepas': ep.beklenen, 'etas': et,
                 'janus': OrtakJanus(ep.beklenen, et, cfg['janus']['agirlik']).beklenen}
    if tur not in callbacks:
        raise ValueError('tur: eepas, etas veya janus')
    return FiltreliModel(callbacks[tur], alan, filt).beklenen


def kosu_bolge(spec, maksiter=200):
    bolge = spec['bolge']
    if bolge not in ('italya',):
        raise ValueError('Bölge İtalya olmalı')
    path = _veri_yolu(spec['katalog'])
    if path.name != f'{bolge}_katalog_le2015.csv':
        raise ValueError('Yalnız deney T ortak le2015 katalog dosyası')
    if sha256(path) != spec['katalog_sha256']:
        raise ValueError('Ortak katalog sha256 teslimle eşleşmiyor')
    if sha256(_veri_yolu(spec['izgara'])) != spec['izgara_sha256']:
        raise ValueError('Ortak ızgara sha256 teslimle eşleşmiyor')
    alan = Alan(pd.read_csv(_veri_yolu(spec['izgara'])), spec['m_kenarlar'])
    etas, filtre = etas_teslim_oku(spec['etas_teslim'])
    df = filtre.uygula(kesik_oku(path), alan)
    fitstart = utc(spec['ayar_baslangic'])
    mcstart = utc(spec['tamlik_baslangic'])
    if not utc(filtre.baslangic) <= mcstart < fitstart < AYAR_SONU:
        raise ValueError('Tamlık/sıcak geçmiş başlangıcı < ayar başlangıcı < 2011 olmalı')
    m0, comp = tamlik_sec(df, mcstart, bolge)
    # >=1.5 M hedefidir, eksik tamlıkta m0 zorla düşürülmez; düşük fark yalnız tanı.
    # Bu durumda skor yine üretilir, fakat kör test aday kapısı kapalı işaretlenir.
    train = df.loc[df.zaman < AYAR_SONU]
    parents = train.loc[(train.zaman >= fitstart) & (train.mw >= m0)]
    if len(parents) < 100:
        raise ValueError('EEPAS b/r0 ayarı için <100 öncü')
    # Homojen sürekli HORUS Mw: önceki ML/Md köprüsü veya yuvarlak-M düzeltmesi yok.
    b = float(np.log10(np.e)/(parents.mw.mean()-m0))
    r0 = len(parents)/float((AYAR_SONU-fitstart)/GUN)
    warm = train.loc[(train.zaman >= mcstart) & (train.zaman < fitstart) & (train.mw >= 4.95)]
    bg = ArkaPlan(alan.kutu, warm, bant=25., duzgun_pay=.05)
    p = Parametreler(m0=m0, b=b, r0=r0)
    pre = EEPASOnhesap(EEPAS(p, alan.kutu, bg), train, alan, fitstart, AYAR_SONU)
    q, er = eepas_ayarla_ortak(pre, maksiter=maksiter, ppe_alt=.05)
    if not er['basari']:
        raise RuntimeError(f'{bolge} EEPAS yakınsamadı: {er}')
    efit, ei = pre.puan(q)
    mc_etas = float(etas.__self__.mc) if hasattr(etas, '__self__') and hasattr(etas.__self__, 'mc') else -np.inf
    # T callback da aynı Mc'yi uygular; yalnız gereksiz katalog sort/copy yükünü kaldırır.
    tfit, ti = gunluk_puan(etas, train.loc[train.mw >= mc_etas], alan, fitstart, AYAR_SONU)
    jr = agirlik_ayarla(efit, tfit, ei, ti)
    ep = EEPAS(q, alan.kutu, bg)
    # EEPAS'ın 50 günlük kesmesi hızlı yolu tam günlük integrale eşit kılar.
    valid = EEPASOnhesap(ep, df, alan, AYAR_SONU, KESIM)
    elam, etotal = valid.puan(q)
    tlam, ttotal = gunluk_puan(etas, df.loc[df.mw >= mc_etas], alan, AYAR_SONU, KESIM)
    w = jr['agirlik']
    jlam, jtotal = w*elam+(1-w)*tlam, w*etotal+(1-w)*ttotal
    # IG'de iptal olan log(n!) terimi, T'nin mutlak hücre-Poisson logL'sinde vardır.
    _, counts = np.unique(np.column_stack([valid.days, valid.ci, valid.mi]), axis=0, return_counts=True)
    factorial = float(gammaln(counts+1).sum())
    if sha256(_veri_yolu(spec['etas_teslim']['dosya'])) != spec['etas_teslim']['sha256']:
        raise ValueError('Ortak ETAS koşuda değişti')
    rows = [olcum_satiri(name, bolge, lam, total, tlam, ttotal)
            for name, lam, total in [('Janus-C2', jlam, jtotal), ('EEPAS-C2', elam, etotal),
                                      ('ortak ETAS', tlam, ttotal)]]
    cfg = {'bolge': bolge, 'hazir': True, 'ayar_baslangic': fitstart.isoformat(),
           'ayar_bitis': AYAR_SONU.isoformat(), 'gecmis_filtresi': asdict(filtre),
           'izgara': alan.izgara.to_dict('list'), 'm_kenarlar': alan.m_kenarlar.tolist(),
           'etas_teslim': spec['etas_teslim'], 'eepas': er, 'janus': jr, 'tamlik': comp,
           'ppe_merkezler': bg.merkezler.to_numpy().tolist(), 'ppe_bant': bg.bant,
           'ppe_duzgun_pay': bg.duzgun_pay, 'girdi': spec,
           'ufuk': '1 UTC gün; w sabit, <=2010 binned MLE; yayın ufuk formülü teyitsiz'}
    score = {'bolge': bolge, 'durum': 'olculdu', 'baslangic': AYAR_SONU.isoformat(),
             'bitis_haric': KESIM.isoformat(), 'satirlar': rows,
             'aday_kapisi': comp['fark_1_5_kapisi'], 'tamlik': comp,
             'log_factoriel': factorial, 'etas_durum': spec.get('etas_durum'),
             'olay_beklenen': {'EEPAS': elam.tolist(), 'ETAS': tlam.tolist(), 'Janus': jlam.tolist()},
             'logL': {name: float(np.log(lam).sum()-total-factorial)
                      for name, lam, total in [('EEPAS', elam, etotal), ('ETAS', tlam, ttotal),
                                               ('Janus', jlam, jtotal)]}}
    return cfg, score


def bekleyen(ortak=ORTAK):
    regions = []
    for region in ('italya',):
        files = [ortak/f'{region}_katalog_le2015.csv', ortak/f'etas_{region}_le2010.json']
        missing = [str(p) for p in files if not p.is_file()]
        reason = 'Deney T teslimi yok' if missing else 'T şema/yükleyici ve ızgara teslim eşlemesi gerekli'
        regions.append({'bolge': region, 'durum': 'bekliyor', 'neden': reason, 'eksik_dosyalar': missing,
                        'satirlar': [{'aday': 'Janus-C2', 'bolge': region, 'N': None, 'IG': None,
                                     'SE': None, 'p': None, 'beklenen_toplam': None,
                                     'taban': 'ortak ETAS', 'durum': 'bekliyor'}]})
    return {'deney': 'C2', 'durum': 'bekliyor', 'baslangic': AYAR_SONU.isoformat(),
            'bitis_haric': KESIM.isoformat(), 'm_alt': 4.95, 'bolgeler': regions,
            'bagimsiz_inceleme': 'C2 skor değişiklikleri henüz incelenmedi'}


def teslim_paketi(ortak=ORTAK):
    """Gerçek T tesliminin sha256 ve alan eşlemesi; parametre dosyalarına dokunmaz."""
    specs = []
    for region in ('italya',):
        et = ortak/f'etas_{region}_le2010.json'
        cat, grid = ortak/f'{region}_katalog_le2015.csv', ortak/f'{region}_izgara.csv'
        cfg = json.loads(et.read_text(encoding='utf-8'))
        specs.append({'bolge': region, 'katalog': _veri_goreli(cat), 'katalog_sha256': sha256(cat),
                      'izgara': _veri_goreli(grid), 'izgara_sha256': sha256(grid),
                      'm_kenarlar': np.round(np.arange(4.95, 9.051, .1), 8).tolist(),
                      'ayar_baslangic': '1995-01-01',
                      'tamlik_baslangic': cfg['ayar_baslangic'],
                      'etas_teslim': {'dosya': _veri_goreli(et), 'sha256': sha256(et),
                          'yukleyici': 'knotenlinie.eepas.c2:t_model_yukle',
                          'katalog_metadata_sha256': sha256(ortak/'kataloglar.json'),
                          'anahtarlar': {'ayar_bitis': 'ayar_bitis', 'dallanma': 'dallanma', 'basari': 'basari',
                              'baslangic': 'ayar_baslangic', 'derinlik_min': 'katalog_teslim.derinlik_min',
                              'derinlik_max': 'katalog_teslim.derinlik_max', 'ust_dahil': 'katalog_teslim.ust_dahil'}},
                      'etas_durum': cfg['durum']})
    return {'bolgeler': specs}


def hazirla(ortak=ORTAK):
    paket = teslim_paketi(ortak)
    yaz(C/'zemin2.json', paket)
    meta = []
    for spec in paket['bolgeler']:
        callback, filt = etas_teslim_oku(spec['etas_teslim'])
        alan = Alan(pd.read_csv(_veri_yolu(spec['izgara'])), spec['m_kenarlar'])
        df = filt.uygula(kesik_oku(_veri_yolu(spec['katalog'])), alan)
        m0, comp = tamlik_sec(df, spec['tamlik_baslangic'], spec['bolge'])
        # Küçük gerçek bağlama kontrolü: tek gün, tek hücre, ayar geçmişinin ilk 3 uygun annesi.
        train = df.loc[(df.zaman < AYAR_SONU) & (df.mw >= callback.__self__.mc)].iloc[:3]
        cell = int(alan.indeks(train.iloc[:1])[0])
        rates = callback(AYAR_SONU, AYAR_SONU+GUN, train, alan.izgara.iloc[[cell]], alan.m_kenarlar)
        meta.append({'bolge': spec['bolge'], 'hucre': len(alan.izgara), 'tamlik': comp,
                     'gecmis_filtresi': asdict(filt), 'etas_mc': callback.__self__.mc,
                     'etas_dallanma': callback.__self__.p['dallanma'], 'etas_durum': spec['etas_durum'],
                     'kucuk_baglama': {'gecmis_n': len(train), 'gun': 1, 'hucre': 1, 'hucre_indeksi': cell,
                                      'beklenen_toplam': float(rates.sum()), 'skor_degildir': True}})
    yaz(C/'GIRDI2.json', {'bolgeler': meta, 'teslim': paket})
    state = bekleyen(ortak)
    for b, r in zip(state['bolgeler'], meta):
        b.update(neden='T teslimine bağlandı; tam bölgesel koşu ayrıca yapılır',
                 tamlik=r['tamlik'], aday_kapisi=r['tamlik']['fark_1_5_kapisi'], eksik_dosyalar=[])
    yaz(C/'OLCUM2.json', state)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paket', default=str(KAYIT / 'C/zemin2.json'), help='İtalya T teslim eşlemesini taşıyan JSON')
    parser.add_argument('--ortak', type=Path, default=ORTAK, help='T teslim dizini; --hazirla/--kontrol için')
    parser.add_argument('--kontrol', action='store_true', help='Dosya varlığı; katalog açılmaz')
    parser.add_argument('--maksiter', type=int, default=200)
    parser.add_argument('--hazirla', action='store_true', help='T teslimini bağla, Mc ve küçük gerçek kontrol; tam skor değil')
    args = parser.parse_args()
    if args.hazirla:
        return hazirla(args.ortak)
    if args.kontrol:
        state = bekleyen(args.ortak)
        yaz(C/'OLCUM2.json', state)
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 2
    specs = json.loads(Path(args.paket).read_text(encoding='utf-8'))['bolgeler']
    if {s['bolge'] for s in specs} != {'italya'} or len(specs) != 1:
        raise ValueError('Teslim paketi tam bir bölge (İtalya) taşımalı')
    scores = []
    for spec in specs:
        cfg, score = kosu_bolge(spec, args.maksiter)
        yaz(C/f"model2-{spec['bolge']}.json", cfg)
        scores.append(score)
    yaz(C/'OLCUM2.json', {'deney': 'C2', 'durum': 'olculdu', 'bolgeler': scores,
                         'bagimsiz_inceleme': 'bekliyor'})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
