#!/usr/bin/env python3
"""TR-5b İNCELEME-2: kota okunuşu, volkanik olayların kotaya etkisi, P1 birimi (ağsız; yalnız bağlayıcı liste).

1. Dinamik kota (tr5b_asama0.kota_ata), "hepsi dolu" ve "Z aygıt" önizlemeleri: K0 / K_p0 yeniden.
2. Statik okuma (10 adayın hepsi kotaya yazılır) bağımsız yeniden yazıldı: K0 / K_p0.
3. Dinamik kota, volkanik 6 olay kotaya yazmadan: K0 / K_p0 (fark var mı?).
4. P1 birimi: ilk 5 adayın istasyon sayısı dağılımı; ortalama(1/n) (bağımsız istasyon gürültüsünde kontrol düzeyi
   σ'nın istasyon düzeyi σ'ya oranı^2); P1 vekil olaylarının 1. adayının istasyon sayısı.
Kullanım: python3 -I -B inc2_kota_p1.py   (çıktı: inc2_kota_p1.json bu dizine)
"""
import collections, importlib.util, json, math, os

BURASI = os.path.dirname(os.path.abspath(__file__))
TR5 = os.path.dirname(BURASI)
sp = importlib.util.spec_from_file_location('a0', os.path.join(TR5, 'tr5b_asama0.py'))
A0 = importlib.util.module_from_spec(sp); sp.loader.exec_module(A0)
L = json.load(open(os.path.join(TR5, 'tr5b_liste_s2.json')))
ol = L['olaylar']
out = {}

hepsi = lambda rol, r, s: True
zayg = lambda rol, r, s: not s.get('aygit_degisimi_Z', False)
for ad, f in (('hepsi_dolu', hepsi), ('Z_aygit', zayg)):
    K0, Kp0, ayr = A0.K_say(L, f)
    out[f'dinamik_{ad}'] = dict(K0=K0, K_p0=Kp0,
                                kontrol_sayisi=dict(collections.Counter(len(v['kontrol']) for v in ayr.values())))


def statik(olaylar, f, rol_k):
    """Bağımsız yazım: aday sırasıyla dolu ve kotaya uygun ilk 5 atanır; ama kotaya o olayın 10 adayının HEPSİNİN
    dolu istasyonları yazılır (statik okuma)."""
    kota = collections.defaultdict(set); at = {}
    for r in sorted(olaylar, key=lambda r: (r['t'], r['id'])):
        ad = r['kontrol'] if rol_k == 'kontrol' else (r['plasebo']['kontrol'] if r.get('plasebo') else [])
        sec = []
        for c in ad:
            dl = [s['ist'] for s in c['istasyon'] if f(rol_k, r, s)]
            if not dl: continue
            if len(sec) < 5 and not any(r['kume'] not in kota[x] and len(kota[x]) >= 3 for x in dl):
                sec.append(c['sira'])
        for c in ad:
            for s in c['istasyon']:
                if f(rol_k, r, s): kota[s['ist']].add(r['kume'])
        at[r['id']] = sec
    return at


def K_bagimsiz(olaylar, f, at_k, at_p):
    k, kp = set(), set()
    for r in olaylar:
        if r['volkanik']: continue
        e = any(f('olay', r, s) for s in r['istasyon']) and len(at_k[r['id']]) >= 4
        p = r.get('plasebo')
        pk = bool(p) and any(f('plasebo', r, s) for s in p['istasyon']) and len(at_p[r['id']]) >= 4
        if e: k.add(r['kume'])
        if e and pk: kp.add(r['kume'])
    return len(k), len(kp)


for ad, f in (('hepsi_dolu', hepsi), ('Z_aygit', zayg)):
    ak, ap = statik(ol, f, 'kontrol'), statik(ol, f, 'plasebo_kontrol')
    K0, Kp0 = K_bagimsiz(ol, f, ak, ap)
    out[f'statik_{ad}'] = dict(K0=K0, K_p0=Kp0, kontrol_4ten_az=sorted(i for i, v in ak.items() if len(v) < 4),
                               kontrol_sayisi=dict(collections.Counter(len(v) for v in ak.values())))
    # volkaniksiz olaylar kotaya tek başına (volkanik 6 olay kotaya yazmaz)
    olv = [r for r in ol if not r['volkanik']]
    K0v, Kp0v, _ = A0.K_say(dict(olaylar=olv), f)
    out[f'dinamik_volkaniksiz_kota_{ad}'] = dict(K0=K0v, K_p0=Kp0v)

# P1 birimi
ana = sorted([r for r in ol if not r['volkanik']], key=lambda r: (r['t'], r['id']))
n5 = [len(c['istasyon']) for r in ana for c in r['kontrol'][:5]]
n1 = [len(r['kontrol'][0]['istasyon']) for r in ana[:24] if r['kontrol']]
out['P1'] = dict(ilk5_istasyon_sayisi=dict(collections.Counter(n5)), ort_1_bolu_n_ilk5=round(sum(1 / n for n in n5) / len(n5), 3),
                 oran_kontrol_istasyon_sigma_bagimsiz=round(math.sqrt(sum(1 / n for n in n5) / len(n5)), 3),
                 p1_vekil_1aday_istasyon_sayisi=dict(collections.Counter(n1)),
                 p1_vekil_ek_istasyon_penceresi=sum(n - 1 for n in n1))
json.dump(out, open(os.path.join(BURASI, 'inc2_kota_p1.json'), 'w'), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
