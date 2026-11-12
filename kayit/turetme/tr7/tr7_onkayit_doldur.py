import json, hashlib, sys
J = '/home/user/knotenlinie/kayit/turetme/tr7/tr7_onkayit_denetim2.json'
DOC = '/home/user/knotenlinie/kayit/onkayit/TR-7_tetiklenmis-tremor_ONKAYIT.md'
d = json.load(open(J))['sonuclar']
JE = J.replace('.json', '_ek.json')
d += json.load(open(JE))['sonuclar']
for r in d:
    if r['denetim'] == 'D5b' and r['sonuc'].get('bos_dagilim') == 'karistirma':
        r['ek'] = r['ek'] + ' karistirma'


def g(ad, ek=None, k=0):
    xs = [r for r in d if r['denetim'] == ad and r['ek'] == ek]
    return xs[k]['sonuc'] if k < len(xs) else None


def v(x):
    if x is None:
        return '—'
    return f'{x:.2f}'.replace('.', ',')


def ar(xs):
    a, b = v(min(xs)), v(max(xs))
    return a if a == b else f'{a}–{b}'


def v3(x):
    return f'{x:.3f}'.replace('.', ',')


def iki(ad, ek, anahtar):
    a, b = g(ad, ek, 0), g(ad, ek, 1)
    return f'{v(a[anahtar])} / {v(b[anahtar])}' if b else v(a[anahtar])


R = {}
d5 = [g('D5b', '1', 0)['p_le_001_orani'], g('D5b', '1', 1)['p_le_001_orani'],
      g('D5b', '3', 0)['p_le_001_orani'], g('D5b', '3', 1)['p_le_001_orani']]
R['D5B_ARALIK'] = (f'{v(min(d5))}–{v(max(d5))} (sürüm 2, A = 1 ve 3, iki tohum; İNCELEME-1: 0,33–0,56)')
R['D5B_BANT'] = '[0,25, 0,65]'
R['D5B_DOGRU'] = f"A = 1: {iki('D5b', '1', 'p_le_001_orani')}; A = 3: {iki('D5b', '3', 'p_le_001_orani')}"
R['D5B_YANLIS'] = (f"A = 1: {v(g('D5b', '1 karistirma')['p_le_001_orani'])}; "
                   f"A = 3: {v(g('D5b', '3 karistirma')['p_le_001_orani'])}")
lo, hi = min(d5 + [0.33]), max(d5 + [0.56])
R['D5B_KALIP'] = f'{v(lo)}–{v(hi)}'
R['D5B_YUZDE'] = f'{round(lo * 100)}–{round(hi * 100)}'
R['D6_DOGRU'] = (f"×20: {iki('D6', '20', 'algilanmama_ya_da_darbe')} (algılama {iki('D6', '20', 'algilama')}); "
                 f"×100: {iki('D6', '100', 'algilanmama_ya_da_darbe')} (algılama {iki('D6', '100', 'algilama')}, "
                 f"algılananların hepsi darbeyle); katalogda maske ile {iki('D6', '100', 'katalog_maskesi_atilma')}")
R['D6_YANLIS'] = (f"×100: {iki('D6', '100', 'yanlis_yumusak_algilanmama_ya_da_darbe')} "
                  f"(×20'de {iki('D6', '20', 'yanlis_yumusak_algilanmama_ya_da_darbe')}: ayırt etmez)")
R['D6B_DOGRU'] = ("×20, S–P 3 / 5 / 8: " + '; '.join(iki('D6b', f'{sp}:20', 'algilanmama_ya_da_darbe') for sp in '358')
                  + f"; ×100, S–P 8: {iki('D6b', '8:100', 'algilanmama_ya_da_darbe')}; ×100, S–P 3 / 5 (bilgi, şart dışı, §17 S9): "
                  + f"{iki('D6b', '3:100', 'algilanmama_ya_da_darbe')}; {iki('D6b', '5:100', 'algilanmama_ya_da_darbe')}")
R['D6B_YANLIS'] = (f"×100, S–P 8: {iki('D6b', '8:100', 'yanlis_yumusak_algilanmama_ya_da_darbe')} "
                   f"(×20, S–P 8: {iki('D6b', '8:20', 'yanlis_yumusak_algilanmama_ya_da_darbe')}: ayırt etmez)")
R['D6B_100_KISA'] = (f"S–P 3: {iki('D6b', '3:100', 'algilanmama_ya_da_darbe')}, "
                     f"S–P 5: {iki('D6b', '5:100', 'algilanmama_ya_da_darbe')}")
R['D7_DOGRU'] = f"{iki('D7', None, 'tam_kural_atilma_3a_dahil')} (algılama {iki('D7', None, 'algilama')})"
R['D7_YANLIS'] = iki('D7', None, 'yanlis_on_esik_atilma')
R['D7B_DOGRU'] = '; '.join(f"A = {A}: {iki('D7b', A, 'darbe_ya_da_sizinti_atilma')}" for A in ('3', '10', '30'))
R['D7B_YANLIS'] = '; '.join(f"A = {A}: {iki('D7b', A, 'yanlis_on_esik_atilma')}" for A in ('3', '10', '30'))
yb = [g('D7b', A, k)['yanlis_on_esik_atilma'] for A in ('3', '10', '30') for k in (0, 1)]
R['D7B_YANLIS_KISA'] = f'{v(min(yb))}–{v(max(yb))}'
R['D7B_KISA'] = '; '.join(f"A = {A}: {iki('D7b', A, 'darbe_ya_da_sizinti_atilma')}" for A in ('3', '10', '30'))
c = [('3:gauss', 'A = 3 Gauss'), ('10:gauss', 'A = 10 Gauss'), ('3:kentsel', 'A = 3 kentsel'), ('10:kentsel', 'A = 10 kentsel')]
R['D7C_DOGRU'] = '; '.join(f"{t}: {iki('D7c', e, 'sizinti_atilma')}" for e, t in c)
R['D7C_INC1'] = '; '.join(f"{t}: {iki('D7c', e, 'inc1_I_sizinti_atilma')}" for e, t in c)
R['D7C_YANLIS'] = '; '.join(f"{t}: {iki('D7c', e, 'yanlis_z_sizinti_atilma')}" for e, t in c)
dc = [g('D7c', e, k)['sizinti_atilma'] for e, _ in c for k in (0, 1)]
R['D7C_DOGRU_KISA'] = ar(dc)
ic = [g('D7c', e, k)['inc1_I_sizinti_atilma'] for e, _ in c for k in (0, 1)]
R['D7C_INC1_KISA'] = f'{v(min(ic))}–{v(max(ic))}'
zk = [g('D7c', e, k)['yanlis_z_sizinti_atilma'] for e in ('3:kentsel', '10:kentsel') for k in (0, 1)]
R['D7C_Z_KENTSEL'] = f'kentsel gürültüde {v(min(zk))}–{v(max(zk))}'
R['D7D_DOGRU'] = '; '.join(f"{t}: {iki('D7d', e, 'sizinti_atilma')}" for e, t in (('gauss', 'Gauss'), ('kentsel', 'kentsel')))
R['D7D_YANLIS'] = '; '.join(f"{t}: {iki('D7d', e, 'yanlis_ters_sizinti_atilma')}" for e, t in (('gauss', 'Gauss'), ('kentsel', 'kentsel')))
dd = [g('D7d', e, k)['sizinti_atilma'] for e in ('gauss', 'kentsel') for k in (0, 1)]
R['D7D_DOGRU_KISA'] = ar(dd)
R['D10_DOGRU'] = (f"sabit {iki('D10', 'sabit', 'kestirilen_bolu_A300_dogru')}; yarım sinüs "
                  f"{iki('D10', 'yarim', 'kestirilen_bolu_A300_dogru')}")
R['D10_YANLIS_I'] = (f"sabit {iki('D10', 'sabit', 'yanlis_I_artieksi60')}; yarım sinüs "
                     f"{iki('D10', 'yarim', 'yanlis_I_artieksi60')}")
R['D10_YANLIS_ETKIN'] = f"yarım sinüs {v3(g('D10', 'yarim', 0)['yanlis_A_etkin_paydasi'])} / {v3(g('D10', 'yarim', 1)['yanlis_A_etkin_paydasi'])}"
R['D12_DOGRU'] = (f"maskesiz algılama {iki('D12', None, 'algilama_maskesiz')}; maske ile atılma "
                  f"{iki('D12', None, 'maske_atilma_kuyruk240')}")
R['D12_YANLIS'] = iki('D12', None, 'maske_atilma_kuyruk60')
R['D12B_DOGRU'] = ('; '.join(f"×{x.split(':')[0]}: {iki('D12b', x, 'maske_atilma_kuyruk60')}" for x in ('2:30', '3:30', '5:30'))
                   + f"; bilgi ×5, 60 sn sönüm: {v(g('D12b', '5:60')['maske_atilma_kuyruk60'])}")
R['D12B_YANLIS'] = '; '.join(f"×{x.split(':')[0]}: {iki('D12b', x, 'maske_atilma_kuyruk30')}" for x in ('2:30', '3:30', '5:30'))
R['SHA_DENETIM2_EK'] = hashlib.sha256(open(JE, 'rb').read()).hexdigest()
R['D12B_60'] = v(g('D12b', '5:60')['maske_atilma_kuyruk60'])
R['D12B_MASKESIZ'] = f"{iki('D12b', '2:30', 'algilama_maskesiz')} (ayıklamadan sağ: {iki('D12b', '2:30', 'ayiklamadan_sag_maskesiz')})"
a, b = g('D13', None, 0), g('D13', None, 1)
R['D13_A50_BANT'] = '[0,42, 0,48]'
R['D13_A90_BANT'] = '[0,44, 0,53]'
R['D13_DOGRU'] = (f"A50 {v3(a['A50_basamak_j20'])} / {v3(b['A50_basamak_j20'])}, A90 {v3(a['A90_basamak_j20'])} / "
                  f"{v3(b['A90_basamak_j20'])} (ara değerlemeyle A50 {v3(a['A50_ara_deger'])} / {v3(b['A50_ara_deger'])}, "
                  f"A90 {v3(a['A90_ara_deger'])} / {v3(b['A90_ara_deger'])})")
R['D13_YANLIS'] = f"A50 = A90 = {v3(a['A50_basamak_j8_yanlis'])} / {v3(b['A50_basamak_j8_yanlis'])}"
a, b = g('D14', 'jeofon4.5', 0), g('D14', 'jeofon4.5', 1)
R['D14_BANT'] = '[0,55, 0,67]'
R['D14_DOGRU'] = (f"A50 {v3(a['A50_yanitli'])} / {v3(b['A50_yanitli'])} (oran {v3(b['A50_yanitli'] / a['A50_yanitli'])}); "
                  f"A90 {v3(a['A90_yanitli'])} / {v3(b['A90_yanitli'])}")
R['D14_YANLIS'] = (f"A50 {v3(a['A50_duz_yanlis'])} / {v3(b['A50_duz_yanlis'])} (yanıtlının "
                   f"{v(a['A50_duz_yanlis'] / a['A50_yanitli'])} katı: A90 bu kadar iyimser çıkar)")
c = g('D14', 'bh20')
R['D14_BH'] = f"{v3(c['A50_duz_yanlis'])} / {v3(c['A50_yanitli'])} = {v(c['A50_duz_yanlis'] / c['A50_yanitli'])} katıdır"
o = g('O4')
R['O4'] = (f"ayıklamasız algılama {v(o['algilama_ayiklamasiz'])}; taban kuralı bu gürültüde sınanamadı "
           f"(algılama yok)" if not o['algilama_ayiklamasiz'] else
           f"ayıklamasız algılama {v(o['algilama_ayiklamasiz'])}, 3a ile atılma {v(o['taban_3a_atilma_algilananda'])}")
R['SHA_DENETIM2'] = hashlib.sha256(open(J, 'rb').read()).hexdigest()
s = open(DOC).read()
for k, x in R.items():
    s = s.replace(f'⟨{k}⟩', x)
kalan = sorted(set(__import__('re').findall('⟨[A-Z0-9_]+⟩', s)))
print('kalan', kalan)
if '--yaz' in sys.argv:
    open(DOC, 'w').write(s)
for k, x in R.items():
    print(k, '=', x)
