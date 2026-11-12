#!/usr/bin/env python3
"""TR-5b İNCELEME-2: `tr5b_asama0.py` sürdürme mantığının AĞSIZ denetimi.

Ağ kesinlikle kullanılmaz: `urllib.request.urlopen` istisna atan bir işlevle değiştirilir, `_getir` sahte bir
yanıtlayıcıyla değiştirilir (istek atmadan kod/bayt döndürür). Geçici dizin karalamada açılır ve sonunda silinir.
Sınananlar:
  1. sure_sn ile yarıda kesilen `yokla` ikinci çağrıda yalnız kalanları atar; çift kayıt yok.
  2. "hata" (ör. 500, bağlantı hatası) satırları önbellekte "yapıldı" sayılır ve sonraki çağrıda YENİDEN denenmez.
  3. Yarım yazılmış son satır: `yokla` onu atlar (yeniden dener), `say`'ın okuma döngüsü ise json hatasıyla düşer.
  4. LISTE_SHA = None iken `say` liste sha256'sını denetlemez.
Kullanım: python3 -I -B inc2_asama0_denetim.py <geçici_dizin_kökü>
"""
import importlib.util, json, os, shutil, sys, tempfile, time, urllib.request

BURASI = os.path.dirname(os.path.abspath(__file__))
sp = importlib.util.spec_from_file_location('a0', os.path.join(os.path.dirname(BURASI), 'tr5b_asama0.py'))
A0 = importlib.util.module_from_spec(sp); sp.loader.exec_module(A0)


def _yasak(*a, **k): raise RuntimeError('AĞ YASAK (denetim)')
urllib.request.urlopen = _yasak
A0.urllib.request.urlopen = _yasak
cagri = []
def sahte(url, ara, son):
    cagri.append(url); time.sleep(0.01)
    return (500, 0, None, time.time(), 2) if 'cha=HHE' in url else (200, 512, b'', time.time(), 0)
A0._getir = sahte
sys.argv.append('--ag-onay')     # yalnız ag_onayi() kapısı için; _getir sahtedir

kok = tempfile.mkdtemp(dir=sys.argv[1])
out = {}
try:
    ist = []
    for i in range(40):
        for c in ('HHZ', 'HHN', 'HHE'):
            ist.append(dict(tur='Z', ag='XX', ist=f'S{i:02d}', loc='', cha=c, ay='2015-06', merkez='IRISDMC'))
    json.dump(dict(istekler=ist, secim={}), open(os.path.join(kok, 'istekler.json'), 'w'))
    A0.yokla(kok, sure=0.3)                                  # yarıda kes
    n1 = sum(1 for _ in open(os.path.join(kok, 'onbellek.jsonl')))
    A0.yokla(kok)                                            # sürdür
    sat = [json.loads(l) for l in open(os.path.join(kok, 'onbellek.jsonl'))]
    out['1_surdurme'] = dict(ilk_cagri_satir=n1, toplam_satir=len(sat), istek=len(ist),
                             cift_kayit=len(sat) - len({s['k'] for s in sat}))
    once = len(cagri); A0.yokla(kok)
    out['2_hata_yeniden_denenmez'] = dict(hata_satiri=sum(1 for s in sat if s['kod'] == 500),
                                          ucuncu_cagrida_atilan=len(cagri) - once)
    with open(os.path.join(kok, 'onbellek.jsonl'), 'a') as f: f.write('{"k": "XX.S00.')
    try:
        for l in open(os.path.join(kok, 'onbellek.jsonl')): json.loads(l)    # say()'ın okuma döngüsünün aynısı
        out['3_yarim_satir_say'] = 'okundu'
    except json.JSONDecodeError as e:
        out['3_yarim_satir_say'] = f'say() düşer: {type(e).__name__}'
    out['4_LISTE_SHA'] = A0.LISTE_SHA
    out['ag_cagrisi'] = 0
finally:
    shutil.rmtree(kok)
json.dump(out, open(os.path.join(BURASI, 'inc2_asama0_denetim.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
