#!/usr/bin/env python3
"""TR-7b Tur 2 seçim ölçütünü (ön kayıt taslağı §11.2–§11.3) iki tohumun çıktısına uygular; Markdown tablo + karar.

Kullanım: python3 -I -B tr7b_tur2_secim.py tr7b_yapay2_t1.json tr7b_yapay2_t2.json
"""
import json, sys

A = json.load(open(sys.argv[1]))['satirlar']
B = json.load(open(sys.argv[2]))['satirlar']
KUR = ('K0', 'K1', 'K2', 'K3', 'K4', 'K5')
SIMETRIK = {'K0', 'K2', 'K5'}


def sart(ad):
    """(ölçü anahtarı soneki, yön, eşik) ya da None (bilgi)."""
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


def pay(v, yon, e):
    if v is None:          # algılama yok: atılma tanımsız; 'atılma ≤' şartları sağlanmış, '≥' şartları da (sağ = 0)
        return 1.0
    return e - v if yon == '<=' else v - e


fmt = lambda x: '—' if x is None else f'{x:.2f}'.replace('.', ',')
en_kotu = {k: 9.0 for k in KUR}
kalan = {k: [] for k in KUR}
print('| Satır | Şart | Algılama | ' + ' | '.join(KUR) + ' |')
print('|' + '---|' * (3 + len(KUR)))
for ad in A:
    s = sart(ad)
    hucre = []
    for k in KUR:
        anah = f'{k}_{s[0] if s else "atilma_tam"}'
        va, vb = A[ad][anah], B[ad][anah]
        hucre.append(f'{fmt(va)} / {fmt(vb)}')
        if s:
            for v in (va, vb):
                p = pay(v, s[1], s[2])
                en_kotu[k] = min(en_kotu[k], p)
                if p < 0:
                    kalan[k].append(ad)
    if s:
        sart_y = f"{'tam' if s[0] == 'atilma_tam' else 'sızıntı' if s[0] == 'atilma_sizinti' else 'sağ'} {'≤' if s[1] == '<=' else '≥'} {fmt(s[2])}"
    else:
        sart_y = 'bilgi'
    print(f"| {ad} | {sart_y} | {fmt(A[ad]['algilama'])} / {fmt(B[ad]['algilama'])} | " + ' | '.join(hucre) + ' |')
# F2 − F1 asimetri şartı
print()
for k in KUR:
    for X in (A, B):
        d = X['F2 tetikleyicili kentsel'][f'{k}_sag'] - X['F1 tetikleyicisiz kentsel'][f'{k}_sag']
        en_kotu[k] = min(en_kotu[k], 0.02 - d)
        if d > 0.02:
            kalan[k].append('F2 − F1')
kabul = [k for k in ('K4', 'K5') if not kalan[k]]   # §11: Tur 2'de yalnız K4 ve K5 seçilebilir
for k in KUR:
    print(f"{k}: en kötü pay {en_kotu[k]:+.3f}; kalan: {sorted(set(kalan[k])) or 'yok'}")
sec = None
if kabul:
    sec = sorted(kabul, key=lambda k: (k not in SIMETRIK, -en_kotu[k]))[0]
print('kabul edilebilir:', kabul, '| seçilen:', sec or 'YOK (kapı altında: kural bulunamadı)')
