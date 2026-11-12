#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 2: `tr7_onkayit_denetim2.py` denetimlerini iki bağımsız tohumla koşar ve toplar (yalnız yapay).

Tohumlar: tohum1 = 20261112 + 300 + i, tohum2 = 4242 + i (i iş sırası). Bilinen yanlış kod değişkeleri tohum1
pencerelerinde aynı betik içinde değerlendirilir (D5b'de ayrı iş). 4 eşzamanlı süreç.
Kullanım: python3 -I -B tr7_onkayit_denetim2_kos.py [--yaz]   -> tr7_onkayit_denetim2.json
          python3 -I -B tr7_onkayit_denetim2_kos.py --ek [--yaz] -> tr7_onkayit_denetim2_ek.json
  --ek: yalnız D12b'nin ikinci tohumu (ana dosya D12b'yi tek tohumla üretti; tohumlar tam koşudakiyle aynıdır).
"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

BURADA = os.path.dirname(os.path.abspath(__file__))
BETIK = os.path.join(BURADA, 'tr7_onkayit_denetim2.py')
NP = 100
ISLER = [('A300', None, 1)]
for A in ('1', '3'):
    ISLER += [('D5b', A, 2), ('D5b', A + ' karistirma', 1)]
for A in ('20', '100'):
    ISLER += [('D6', A, 2)]
    for sp in ('3', '5', '8'):
        ISLER += [('D6b', f'{sp}:{A}', 2)]
ISLER += [('D7', None, 2)]
for A in ('3', '10', '30'):
    ISLER += [('D7b', A, 2)]
for x in ('3:gauss', '10:gauss', '3:kentsel', '10:kentsel'):
    ISLER += [('D7c', x, 2)]
for x in ('gauss', 'kentsel'):
    ISLER += [('D7d', x, 2)]
for x in ('yarim', 'sabit'):
    ISLER += [('D10', x, 2)]
ISLER += [('D12', None, 2)]
for x in ('2:30', '3:30', '5:30', '5:60'):
    ISLER += [('D12b', x, 2 if x.endswith(':30') else 1)]
ISLER += [('D13', None, 2), ('D14', 'jeofon4.5', 2), ('D14', 'bh20', 1), ('O4', None, 1)]


def kos(i, ad, ek, k):
    tohum = 20261112 + 300 + i if k == 0 else 4242 + i
    arg = ['python3', '-I', '-B', BETIK, ad, str(tohum), str(NP if ad != 'A300' else 1)] + (ek.split() if ek else [])
    out = subprocess.run(arg, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    plan = [(i, ad, ek, k) for i, (ad, ek, nt) in enumerate(ISLER) for k in range(nt)]
    cikti = 'tr7_onkayit_denetim2.json'
    if '--ek' in sys.argv:
        plan = [x for x in plan if x[1] == 'D12b' and x[3] == 1]
        cikti = 'tr7_onkayit_denetim2_ek.json'
    else:
        plan = [x for x in plan if not (x[1] == 'D12b' and x[3] == 1)]
    with ThreadPoolExecutor(4) as ex:
        sonuc = list(ex.map(lambda x: kos(*x), plan))
    js = json.dumps(dict(n_pencere=NP, sonuclar=sonuc), ensure_ascii=False, indent=1)
    print(js)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, cikti), 'x', encoding='utf-8') as f:
            f.write(js + '\n')


if __name__ == '__main__':
    main()
