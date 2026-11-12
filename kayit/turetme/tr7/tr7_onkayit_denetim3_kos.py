#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 3: İNCELEME-2 ile yeni ya da yeniden tanımlanan yapay denetimleri iki bağımsız tohumla koşar
ve toplar (yalnız yapay veri; dalga formu yok, ağa çıkılmaz).

Denetimler (§7.1): D6 ×100 (şart ×100'e taşındı), D6b ×100 S–P 8 (bant ≥ 0,90), D15 (a) maskesiz ve (b) W'nin son
120 sn'si maskeli (3a, W′_son), D12c (deterministik E1 maske birim sınaması; rastgele katalog bölümü iki tohumla).
Tohumlar: tohum1 = 20261112 + 500 + i, tohum2 = 6262 + i (i iş sırası); sürüm 2 (20261112 + 300 + i, 4242 + i) ve
İNCELEME-2 (777001–777008, 9201–9204, 9301–9302) tohumlarından ayrıdır. Bilinen yanlış kodlar aynı pencerelerde.
Kabul bantları (§7.1, İ2-E2 metni): D6 ×100 algılanmama ya da darbeyle atılma ≥ 0,95; D6b ×100 S–P 8 ≥ 0,90;
D15 ayıklamasız algılama ≥ 0,90 ve 3a ile atılma ≥ 0,95 ((a) ve (b)); D12c birebir ve ±0,001.
Kullanım: python3 -I -B tr7_onkayit_denetim3_kos.py [--yaz]   -> tr7_onkayit_denetim3.json
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

BURADA = os.path.dirname(os.path.abspath(__file__))
NP = 100
ISLER = [('tr7_onkayit_denetim2.py', 'D6', '100'), ('tr7_onkayit_denetim2.py', 'D6b', '8:100'),
         ('tr7_onkayit_denetim3.py', 'D15', '0'), ('tr7_onkayit_denetim3.py', 'D15', '120')]


def kos(i, betik, ad, ek, k):
    tohum = 20261112 + 500 + i if k == 0 else 6262 + i
    arg = ['python3', '-I', '-B', os.path.join(BURADA, betik), ad, str(tohum), str(NP), ek]
    return json.loads(subprocess.run(arg, capture_output=True, text=True, check=True).stdout)


def bant(r):
    s, ad = r['sonuc'], r['denetim']
    if ad == 'D6':
        return dict(dogru=s['algilanmama_ya_da_darbe'] >= 0.95, yanlis=s['yanlis_yumusak_algilanmama_ya_da_darbe'] >= 0.95)
    if ad == 'D6b':
        return dict(dogru=s['algilanmama_ya_da_darbe'] >= 0.90, yanlis=s['yanlis_yumusak_algilanmama_ya_da_darbe'] >= 0.90)
    if ad == 'D15':
        alg = s['algilama_ayiklamasiz'] >= 0.90
        y = dict(yanlis_3a_yok=alg and (s['yanlis_3a_yok_atilma'] or 0) >= 0.95)
        if r['ek'] == '120':
            y['yanlis_surum2_W_sonu'] = alg and (s['yanlis_surum2_W_sonu_atilma'] or 0) >= 0.95
        return dict(dogru=alg and (s['taban_3a_Wson_atilma'] or 0) >= 0.95, **y)
    raise ValueError(ad)


def main():
    plan = [(i, b, ad, ek, k) for i, (b, ad, ek) in enumerate(ISLER) for k in (0, 1)]
    with ThreadPoolExecutor(4) as ex:
        sonuc = list(ex.map(lambda x: kos(*x), plan))
    for r in sonuc:
        r['bant_icinde'] = bant(r)        # 'dogru' True olmalı; her 'yanlis' False olmalı
    d12c = json.loads(subprocess.run(['python3', '-I', '-B', os.path.join(BURADA, 'tr7_onkayit_d12c.py'),
                                      str(20261112 + 500 + len(ISLER)), str(6262 + len(ISLER))],
                                     capture_output=True, text=True, check=True).stdout)
    hepsi = (all(r['bant_icinde']['dogru'] for r in sonuc) and d12c['dogru_kod_bantta']
             and not any(v for r in sonuc for k, v in r['bant_icinde'].items() if k != 'dogru')
             and all(d12c['yanlis_kod_bant_disinda'].values()))
    js = json.dumps(dict(n_pencere=NP, sonuclar=sonuc, D12c=d12c, dogru_iceride_yanlis_disarida=hepsi),
                    ensure_ascii=False, indent=1)
    print(js)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, 'tr7_onkayit_denetim3.json'), 'x', encoding='utf-8') as f:
            f.write(js + '\n')


if __name__ == '__main__':
    main()
