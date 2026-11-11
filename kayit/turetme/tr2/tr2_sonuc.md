# TR-2 sonucu: sonraki M≥6 sessiz tarafta mı?

Ön kayıt: `kayit/onkayit/TR-2_sonraki-M6-yonu_ONKAYIT.md` (DONDURULDU). Kod: `kayit/turetme/tr2/tr2_kosu.py`.

## Hüküm (§3)

- K = 40, X = 15, oran 0.375.
- Hüküm: **H0 (büyük etki yok)** (eşikler: X ≥ 26 H1, X ≤ 22 H0, 23–25 ayırt edilemez).
- P(X ≥ 15 | p = 0,5) = 0.9597; P(X ≤ 15 | p = 0,70) = 0.0000.
- Ek 1 (K = 42 okuması; eşikler X ≥ 27 H1, X ≤ 23 H0; dışarıda kalan iki kümenin isabeti hesaplanmadı): X = 15 → H0, X = 16 → H0, X = 17 → H0. Hüküm K = 42 okumasında değişmez.

## Yorum kuralları (§3; hükmü değiştirmez)

1. Arka plan kayması (§5.8 ile ölçülür): ters çevrim üst kuyruk reddi False, alt kuyruk reddi False.
2. H1 ve ters çevrim üst kuyrukta red: False.
3. (H0 ya da ters yön notu) ve ters çevrim alt kuyrukta red: False.
4. Hükmün adı "sessiz taraf". Koşul (i) u/L iki yarıda oran > 0,5: False; koşul (ii) ağırlık merkezi X/K ≥ 0,6: False. H1 yorumu: — (hüküm H1 değil).
- §4 öncelik: karar yalnız binomla. ETAS satırları sıfırı dışlıyor mu: {'etas_eksi_taban': False, 'bosluk_eksi_etas': False}; arka plan kuralına tabi okuma: False.
- §8 aktarım adayı: False.

## Log skorlar (§4; nat, küme bootstrap'i 10 000, tohum 20261111, %95 yüzdelik)

| Satır | Fark | %95 aralık | Sıfırı içerir |
|---|---|---|---|
| Boşluk − taban | -4.981 | [-8.696, -1.267] | hayır |
| ETAS − taban | -0.574 | [-7.846, +6.313] | evet |
| Boşluk − ETAS | -4.408 | [-14.605, +6.216] | evet |

Toplam log skor: taban -27.726, boşluk -32.707, ETAS -28.300.

## Bilgi satırları (§5; hükmü değiştirmez)

1. u/L medyanı 0.536. Altı: X = 7, K = 20, oran 0.350. Üstü: X = 8, K = 20, oran 0.400.
2. Ağırlık merkezi tanımı: X = 4, K = 8, oran 0.500.
3. Zayıf düzlem (> 30°) var: X = 5, K = 11, oran 0.455; yok: X = 10, K = 29, oran 0.345.
4. Aday ≥ 3: X = 10, K = 19, oran 0.526; aday < 3: X = 5, K = 21, oran 0.238.
5. Büyük olay gölgesindekiler dışlanınca: X = 14, K = 29, oran 0.483.
6. Ters yön notu (X ≤ 14): düşülmez.
7. Türkiye (yalnız anılır): K08 usp0009hev isabet 0.
8. Zaman ters çevrimi: K_ters = 28, X_ters = 16, oran 0.571; P(X ≥ X_ters | 0,5) = 0.2858, P(X ≤ X_ters | 0,5) = 0.8275.
9. Çift/öncü dışlanınca: X = 12, K = 34, oran 0.353.
10. Sonraki |s|/L ≤ 1: X = 3, K = 6, oran 0.500 (tümleyen X = 12, K = 34, oran 0.353); sonraki M ≥ Mw: X = 5, K = 10, oran 0.500 (tümleyen X = 10, K = 30, oran 0.333); sonraki doğrultu atımlı birincil: X = 8, K = 14, oran 0.571 (tümleyen X = 7, K = 26, oran 0.269).

## Küme satırları

| Küme | Birincil | t0 | Mw | Sessiz | Sonraki | İsabet | Önceki | İsabet_ters | p_ETAS | u/L | zayıf | aday≥3 | gölge | çift | TR |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K01 | usp0001aq1 | 1980-11-08 | 7.2 | +1 | nc228027 | 0 | — | — | 0.228 | 1.104 | 0 | 1 | 0 | 0 | 0 |
| K02 | usp000278e | 1984-09-10 | 6.7 | -1 | nc268031 | 1 | — | — | 0.393 | 0.229 | 0 | 1 | 0 | 0 | 0 |
| K03 | usp0002jsc | 1985-09-15 | 6.3 | -1 | usp0003z73 | 1 | — | — | 0.324 | 0.897 | 0 | 0 | 0 | 1 | 0 |
| K04 | usp0002mvw | 1985-11-17 | 7.1 | -1 | usp0006nyy | 1 | usp00013j3 | 1 | 0.187 | 0.484 | 0 | 1 | 0 | 0 | 0 |
| K05 | usp0003gxk | 1988-06-12 | 6.5 | -1 | usp000585d | 0 | usp0002z8y | 0 | 0.379 | 0.265 | 1 | 0 | 0 | 0 | 0 |
| K06 | usp0006rzb | 1995-01-27 | 6.8 | -1 | usp0006ue3 | 1 | usp0006d2j | 1 | 0.232 | 1.086 | 0 | 1 | 0 | 0 | 0 |
| K07 | usp00075n1 | 1995-10-23 | 6.2 | -1 | usp000c30u | 1 | — | — | 0.314 | 0.418 | 1 | 0 | 0 | 0 | 0 |
| K08 | usp0009hev | 1999-11-12 | 7.2 | +1 | usp0009u3d | 0 | usp0009d4z | 1 | 0.431 | 0.128 | 0 | 0 | 1 | 0 | 1 |
| K09 | usp000araj | 2001-10-21 | 6.7 | -1 | usc000sxye | 0 | — | — | 0.161 | 1.699 | 0 | 0 | 1 | 0 | 0 |
| K10 | usp000avpw | 2002-01-02 | 7.2 | +1 | usp000csk2 | 0 | usp000arq0 | 0 | 0.404 | 0.148 | 1 | 1 | 0 | 0 | 0 |
| K11 | usp000b923 | 2002-07-31 | 6.5 | -1 | usp000cfzw | 0 | usp000an03 | 1 | 0.292 | 0.572 | 0 | 1 | 0 | 0 | 0 |
| K12 | usp000bcdg | 2002-09-16 | 6.3 | -1 | usp000ecub | 0 | usp000aw5z | 1 | 0.145 | 1.300 | 0 | 0 | 1 | 0 | 0 |
| K13 | usp000c4tt | 2003-08-14 | 6.3 | +1 | usb000m8ch | 0 | — | — | 0.178 | 1.416 | 0 | 1 | 0 | 0 | 0 |
| K14 | usp000ckg7 | 2004-02-05 | 7.0 | +1 | usp000he3d | 1 | usp000bkg3 | 0 | 0.269 | 0.312 | 0 | 1 | 0 | 1 | 0 |
| K15 | usp000d3fm | 2004-09-03 | 6.2 | +1 | usp000dr3h | 1 | usp000c6ju | 1 | 0.163 | 0.889 | 1 | 1 | 0 | 0 | 0 |
| K16 | usp000d7h4 | 2004-11-02 | 6.7 | -1 | usb000px6r | 0 | usp000a7fx | 1 | 0.367 | 0.443 | 0 | 1 | 0 | 0 | 0 |
| K17 | usp000dcbh | 2005-01-01 | 6.7 | -1 | usp000eme6 | 0 | — | — | 0.364 | 1.304 | 1 | 0 | 1 | 0 | 0 |
| K18 | usp000ekaq | 2006-06-14 | 6.5 | -1 | us2000k9d7 | 0 | usp000c0rc | 1 | 0.234 | 0.256 | 0 | 0 | 0 | 0 | 0 |
| K19 | usp000f115 | 2006-12-26 | 6.9 | -1 | usp000g0k8 | 0 | usp0009wkm | 0 | 0.287 | 0.501 | 1 | 1 | 1 | 0 | 0 |
| K20 | usp000f57a | 2007-02-20 | 6.7 | +1 | usp000fcze | 0 | usp0006svx | 0 | 0.148 | 1.006 | 1 | 0 | 1 | 0 | 0 |
| K21 | usp000fjw7 | 2007-08-16 | 6.5 | +1 | usp000jpeh | 0 | usp0009kvr | 0 | 0.263 | 0.459 | 0 | 0 | 1 | 0 | 0 |
| K22 | usp000fp85 | 2007-09-27 | 6.1 | -1 | us1000aytk | 0 | usp000f8mu | 1 | 0.098 | 0.986 | 0 | 1 | 1 | 1 | 0 |
| K23 | usp000g412 | 2008-04-15 | 6.4 | -1 | us10008qhu | 0 | — | — | 0.380 | 0.584 | 0 | 0 | 1 | 1 | 0 |
| K24 | usp000gu5x | 2009-02-18 | 7.0 | -1 | usp000h4ha | 1 | usp000edbg | 1 | 0.202 | 0.936 | 0 | 1 | 0 | 0 | 0 |
| K25 | usp000h0gm | 2009-08-17 | 6.7 | -1 | us200027ps | 1 | usp000d7yk | 1 | 0.308 | 0.067 | 0 | 1 | 0 | 0 | 0 |
| K26 | usp000h60h | 2010-01-12 | 7.0 | -1 | us6000f65h | 0 | — | — | 0.121 | 0.353 | 0 | 0 | 0 | 0 | 0 |
| K27 | usp000hfdm | 2010-07-18 | 6.7 | +1 | usp000jq4r | 0 | usp000h2wq | 0 | 0.075 | 0.781 | 0 | 1 | 0 | 0 | 0 |
| K28 | usp000jdar | 2012-01-10 | 7.2 | +1 | usp000jj0a | 0 | usp000g1j1 | 1 | 0.485 | 0.103 | 0 | 0 | 0 | 0 | 0 |
| K29 | usc000eyur | 2013-01-30 | 6.1 | -1 | us7000fwzz | 1 | — | — | 0.473 | 0.805 | 0 | 0 | 0 | 1 | 0 |
| K30 | usc000mnvj | 2014-02-12 | 6.9 | +1 | us7000abmk | 0 | usp000g1w2 | 0 | 0.472 | 0.013 | 0 | 0 | 0 | 0 | 0 |
| K31 | us10002b03 | 2015-05-20 | 6.8 | -1 | us10002mw0 | 0 | usc000f29g | 1 | 0.081 | 1.419 | 0 | 1 | 0 | 1 | 0 |
| K32 | us20002whh | 2015-07-10 | 6.7 | -1 | us100030pg | 1 | usp000h5vu | 1 | 0.545 | 0.056 | 1 | 1 | 0 | 0 | 0 |
| K33 | us100044k6 | 2015-12-07 | 7.2 | +1 | us200066x9 | 0 | usp000gjd4 | 0 | 0.192 | 0.345 | 0 | 0 | 0 | 0 | 0 |
| K34 | us2000bibm | 2017-11-04 | 6.8 | -1 | us700034ya | 1 | us10001ryq | 1 | 0.360 | 0.452 | 0 | 1 | 0 | 0 | 0 |
| K35 | us1000hfh3 | 2018-10-22 | 6.5 | +1 | us7000mykj | 0 | — | — | 0.365 | 0.469 | 0 | 0 | 1 | 0 | 0 |
| K36 | us2000j545 | 2019-01-17 | 6.2 | +1 | us6000dfad | 1 | us2000cq5t | 1 | 0.197 | 0.762 | 1 | 1 | 0 | 0 | 0 |
| K37 | us6000434e | 2019-06-19 | 6.3 | -1 | us6000iika | 1 | usp000fv00 | 0 | 0.099 | 1.364 | 1 | 0 | 0 | 0 | 0 |
| K38 | us70004jyv | 2019-07-14 | 7.2 | -1 | us7000e9bi | 0 | us200062l9 | 0 | 0.373 | 0.672 | 0 | 0 | 0 | 0 | 0 |
| K39 | us60006rp9 | 2019-12-15 | 6.8 | +1 | us70007jwn | 0 | usb000rsr5 | 0 | 0.169 | 0.355 | 1 | 0 | 0 | 0 | 0 |
| K40 | us6000f5h2 | 2021-08-13 | 6.1 | +1 | us6000frfw | 1 | — | — | 0.211 | 0.713 | 0 | 0 | 1 | 0 | 0 |

Ağırlık merkezi tanımı (§5.2): K01 usp0001xcs 0, K02 usp000dvtc 1, K03 usp000jdar 0, K04 usc000mnvj 0, K05 us20002whh 1, K06 us1000hfgv 1, K07 us70004jyv 1, K08 us6000645n 0.
