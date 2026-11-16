#!/usr/bin/env python3
"""TR-7b Tur 3 seçim ölçütünü (ön kayıt taslağı §12.1, §12.3–§12.4) iki tohumun çıktısına uygular.

Her tohum iki bölüm dosyasından okunur. Çıktı: Markdown tablo, üreteç denetimi, karar.
Kullanım: python3 -I -B tr7b_tur3_secim.py t1_b1.json t1_b2.json t2_b1.json t2_b2.json
"""
import json, sys

oku = lambda a, b: {**json.load(open(a))['satirlar'], **json.load(open(b))['satirlar']}
A = oku(sys.argv[1], sys.argv[2])
B = oku(sys.argv[3], sys.argv[4])
KUR = ('K0', 'K1', 'K2', 'K3', 'K4', 'K5', 'K6')


def sart(ad):
    """(ölçü anahtarı soneki, yön, eşik) ya da None (bilgi). §11.2 ile aynı."""
    if ad.startswith(('D7 ', 'D7b')):
        return ('atilma_tam', '<=', 0.03)
    if ad.startswith('D7c'):
        return ('atilma_sizinti', '<=', 0.05)
    if ad.startswith('D7d') or ad.startswith('Y3'):
        return ('atilma_sizinti', '>=', 0.95)
    if ad.startswith('Y1'):
        return None if 'sabit' in ad else ('atilma_tam', '<=', 0.05)
    if ad.startswith(('Y2', 'F1', 'F2')):
        return ('sag', '<=', 0.05)
    raise ValueError(ad)


def gecti(v, s):
    if v is None:
        return True
    return v <= s[2] + 1e-9 if s[1] == '<=' else v >= s[2] - 1e-9


def pay(v, s):
    if v is None:
        return 1.0
    return s[2] - v if s[1] == '<=' else v - s[2]


fmt = lambda x: '—' if x is None else f'{x:.2f}'.replace('.', ',')
en_kotu = {k: 9.0 for k in KUR}
kalan = {k: [] for k in KUR}
ana = [ad for ad in A if 'gecikmesiz' not in ad]
print('| Satır | Şart | Algılama | Konum tele / küme | ' + ' | '.join(KUR) + ' |')
print('|' + '---|' * (4 + len(KUR)))
for ad in ana:
    s = sart(ad)
    hucre = []
    for k in KUR:
        anah = f'{k}_{s[0] if s else "atilma_tam"}'
        va, vb = A[ad][anah], B[ad][anah]
        hucre.append(f'{fmt(va)} / {fmt(vb)}')
        if s:
            for v in (va, vb):
                en_kotu[k] = min(en_kotu[k], pay(v, s))
                if not gecti(v, s):
                    kalan[k].append(ad)
    sart_y = (f"{'tam' if s[0] == 'atilma_tam' else 'sızıntı' if s[0] == 'atilma_sizinti' else 'sağ'} "
              f"{'≤' if s[1] == '<=' else '≥'} {fmt(s[2])}") if s else 'bilgi'
    kt = f"{A[ad]['kume_konum_tele']}/{A[ad]['kume']} ; {B[ad]['kume_konum_tele']}/{B[ad]['kume']}"
    print(f"| {ad} | {sart_y} | {fmt(A[ad]['algilama'])} / {fmt(B[ad]['algilama'])} | {kt} | " + ' | '.join(hucre) + ' |')
print()
for k in KUR:
    for X in (A, B):
        d = X['F2 tetikleyicili kentsel'][f'{k}_sag'] - X['F1 tetikleyicisiz kentsel'][f'{k}_sag']
        en_kotu[k] = min(en_kotu[k], 0.02 - d)
        if d > 0.02 + 1e-9:
            kalan[k].append('F2 − F1')
for k in KUR:
    print(f"{k}: en kötü pay {en_kotu[k]:+.3f}; kalan: {sorted(set(kalan[k])) or 'yok'}")

# Üreteç denetimi (§12.1)
print('\nÜreteç denetimi: gecikmeli / gecikmesiz (tohum 1 ; tohum 2), K0–K5')
print('| Satır | Şart | ' + ' | '.join(KUR[:6]) + ' |')
print('|' + '---|' * 8)
kararli, en_fark = True, 0.0
for ad in [a for a in A if a.endswith(' gecikmesiz')]:
    g = ad[:-len(' gecikmesiz')]
    s = sart(g)
    hucre = []
    for k in KUR[:6]:
        an = f'{k}_{s[0]}'
        parca = []
        for X in (A, B):
            v1, v0 = X[g][an], X[ad][an]
            parca.append(f'{fmt(v1)}/{fmt(v0)}')
            if gecti(v1, s) != gecti(v0, s):
                kararli = False
            if v1 is not None and v0 is not None:
                en_fark = max(en_fark, abs(v1 - v0))
                if abs(v1 - v0) > 0.03 + 1e-9:
                    kararli = False
        hucre.append(' ; '.join(parca))
    print(f'| {g} | {s[0]} | ' + ' | '.join(hucre) + ' |')
print(f'en büyük fark {en_fark:.3f}; kararlı: {kararli}')
kabul = not kalan['K6'] and kararli
print('K6 kabul:', kabul, '| karar:', 'K6 SEÇİLDİ' if kabul else
      'YOK — kapı altında (kural bulunamadı), iki tasarım turu sonuçsuz')
