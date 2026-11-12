#!/usr/bin/env python3
"""TR-7 ön kayıt sürüm 3 (İNCELEME-2 İ2-Ö2, İ2-Ö6): n_açık, p_min(n_açık) ve X_min^(0,05/7) tablosu.

YALNIZ dondurulmuş dosyalardan (dalga formu yok, ağa çıkılmaz; numpy bile gerekmez, yalnız standart kitaplık):
  - tr7_onkayit_sayilar.json  `K0_on.x1.<segment>.birimler` (önsayımda taranan ana birimler, n)
  - tr7_e1_maske_ozet.json     `pencere.<olay>|<segment>.E1-C.W_maskeli_pay` (segment orta noktasıyla, W birleşimi)
  - tr7_onkayit_sayilar.py     `cp_ust`, `binom_ust` (sürüm 2'nin X_min tablolarını üreten fonksiyonların kendisi)

Tanım (ön kayıt §8, İ2-Ö2): n_açık = taranan ana birimlerden W'sinin maskeli payı (§6.5.1 ve 1a birlikte, segment
orta noktasıyla) ≤ 0,50 olanların sayısı; p_min = (1 − 0,05^(1/n_açık)) / 0,9.
Önsayımda §6.5.1 (yerel katalog maskesi) henüz yoktur (sorgusu koşu manifestinde yapılır); bu yüzden önsayımın n_açık'ı
yalnız 1a (E1-C) payıyla hesaplanır. Wharton biriminin iki penceresi ayrı ayrı yazılır (önsayımda ikisi de 0,000).

X_min^(0,05/7) (İ2-Ö6): sürüm 2 ile aynı tanım (N = 10n; f > ⌊0,05 N⌋ ise 'K2'; X ∈ [2, n]), kuyruk eşiği 0,05/7.
Kullanım: python3 -I -B tr7_onkayit_sayilar3.py [--yaz]   -> tr7_onkayit_sayilar3.json
"""
import hashlib, json, math, os, sys

BURADA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BURADA)
from tr7_onkayit_sayilar import binom_ust, cp_ust      # noqa: E402  (main() korumalı; yan etkisiz)

WHARTON = ('official20120411083836720_20', 'usp000jhjb')
ESIK = 0.50


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def p_min(n):
    return (1 - 0.05 ** (1 / n)) / 0.9


def xmin(n, f, a):
    N = 10 * n
    if f > math.floor(0.05 * N):
        return 'K2'
    pu = cp_ust(f, N)
    return next((x for x in range(2, n + 1) if binom_ust(n, pu, x) <= a), None)


def main():
    js = os.path.join(BURADA, 'tr7_onkayit_sayilar.json')
    e1 = os.path.join(BURADA, 'tr7_e1_maske_ozet.json')
    S = json.load(open(js, encoding='utf-8'))
    E = json.load(open(e1, encoding='utf-8'))['pencere']
    seg_out = {}
    for seg in ('S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7'):
        birimler = S['K0_on']['x1'][seg]['birimler']
        satir = []
        for b in birimler:
            olaylar = list(WHARTON) if b == 'WHARTON2012' else [b]
            paylar = [E[f'{o}|{seg}']['E1-C']['W_maskeli_pay'] for o in olaylar]
            satir.append(dict(birim=b, W_maskeli_pay=paylar, acik=all(p <= ESIK for p in paylar)))
        n = len(birimler)
        n_acik = sum(r['acik'] for r in satir)
        seg_out[seg] = dict(n=n, n_acik=n_acik, p_min_n=round(p_min(n), 3),
                            p_min_n_acik=round(p_min(n_acik), 3) if n_acik >= 5 else None,
                            dislama='hesaplanır' if n_acik >= 5 else 'dışlama hesaplanmadı (W\'si yarıdan az maskeli birim < 5)',
                            birimler=satir)
    sonuc = dict(
        girdi_sha256={'tr7_onkayit_sayilar.json': sha(js), 'tr7_e1_maske_ozet.json': sha(e1),
                      'tr7_onkayit_sayilar.py': sha(os.path.join(BURADA, 'tr7_onkayit_sayilar.py'))},
        tanim='n_açık: W maskeli payı ≤ 0,50 olan ana birim sayısı (önsayımda yalnız 1a/E1-C payı); '
              'p_min = (1 − 0,05^(1/n_açık)) / 0,9',
        p_min_tablo={n: round(p_min(n), 3) for n in range(5, 11)},
        segment=seg_out,
        X_min_tablo_005_7={n: [xmin(n, f, 0.05 / 7) for f in range(6)] for n in range(5, 11)},
        X_min_tablo_005_7_kuyruk_esigi=round(0.05 / 7, 5),
        X_min_tablo_005_yeniden={n: [xmin(n, f, 0.05) for f in range(6)] for n in range(5, 11)},
        X_min_tablo_005_3_yeniden={n: [xmin(n, f, 0.05 / 3) for f in range(6)] for n in range(5, 11)},
    )
    # sürüm 2 tablolarıyla tutarlılık (aynı fonksiyon, aynı tanım)
    for a_ad, k in (('0.05', 'X_min_tablo_005_yeniden'), ('0.05/3', 'X_min_tablo_005_3_yeniden')):
        eski = {int(n): v for n, v in S['X_min_tablo'][a_ad].items()}
        sonuc[k + '_surum2_ile_ayni'] = all(eski[n] == v for n, v in sonuc[k].items())
    out = json.dumps(sonuc, ensure_ascii=False, indent=1)
    print(out)
    if '--yaz' in sys.argv:
        with open(os.path.join(BURADA, 'tr7_onkayit_sayilar3.json'), 'x', encoding='utf-8') as f:
            f.write(out + '\n')


if __name__ == '__main__':
    main()
