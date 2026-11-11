# TR-11 sonuç

Hüküm: **taban N0 bandında (b_f 2–4)**

## Veri kapısı ve düşmeler

- Küme-pencere: listede 803, geçerli 665; yer 300 (eşik 100), blok 50 (eşik 30).
- İndirme hatası: 0 istasyon (pay %0.00).
- (istasyon, T) nedenleri: {'gecerli': 6483, 'doluluk': 1185, 'rank': 30, 'satir_yok': 78}
- Küme-pencere düşme nedenleri: {'yakin<3': 125, 'referans<3': 13}
- Okuma: {'bozuk': 0, 'geri': 0, 'tekrar': 0, 'durdu': 4684, 'baslik_yok': 0, 'tenv3_hata': []}

## Kod denetimi (gerçek S görülmeden)

- (i) yapay N0: q95 1,545 / q95_N0 1,595 = 0,969 (aralık [0,9, 1,1]; geçti)
- (ii-b) yapay S düzeyi: ölçülen medyan(S_eklenen − S_özgün) 2,181, m* 2,174, aralık [1,957, 2,392] (geçti; 335 seçili KP)
- (ii-a) gerçek, istasyon düzeyi: medyan(d_E) 3,0000 (aralık [2,95, 3,05]), medyan(|d_N|) 0,0000 (< 0,05) (geçti; 2005 çift)

## Ana ölçü (Ö1)

- q95 = 2,42 [2,06, 2,76] mm/yıl (blok bootstrap, %90; KP 665, yer 300, blok 50)
- medyan 0,79 [0,75, 0,84]; %90 1,80 [1,67, 2,00]; %99 3,71 [3,26, 4,83]
- q95_N0 = 1,595; ρ = 1,517 [1,293, 1,727] (ρ_L > 1; bilgi satırı)
- b_f* = 4,581 [3,899, 5,221] mm/yıl^0,25 (σ_w = 1,5 mm sabit)
- Kuyruk ρ₉₅/ρ₅₀ = 1,935 [1,670, 2,156] → kuyruk Gauss N0'dan ağır
- N1 (bilgi): q95_N1 2,636; ρ_N1 0,917 [0,783, 1,043]

## Kırılımlar

| Katman | KP | Yer | Blok | q95 [L, U] | ρ [L, U] |
|---|---|---|---|---|---|
| n_y 3–4 | 213 | 161 | 47 | 2,76 [2,23, 3,13] | 1,589 [1,282, 1,796] |
| n_y 5–7 | 253 | 173 | 34 | 2,24 [1,96, 2,78] | 1,443 [1,259, 1,787] |
| n_y 8 | 199 | 124 | 26 | 1,94 [1,72, 2,84] | 1,320 [1,173, 1,952] |
| sınıf A | 0 | 0 | – | güç yok (< 30 yer) | – |
| sınıf B | 10 | 6 | – | güç yok (< 30 yer) | – |
| sınıf D | 655 | 294 | 50 | 2,45 [2,04, 2,79] | 1,537 [1,283, 1,734] |
| epok 2003-01-01 | 5 | 5 | 4 | 1,62 [1,04, 1,67] | 0,902 [0,582, 0,961] |
| epok 2008-01-01 | 35 | 35 | 14 | 3,98 [3,29, 5,40] | 2,387 [2,006, 3,156] |
| epok 2013-01-01 | 142 | 142 | 28 | 2,10 [1,79, 2,66] | 1,276 [1,087, 1,629] |
| epok 2018-01-01 | 226 | 226 | 40 | 2,03 [1,67, 2,38] | 1,285 [1,056, 1,507] |
| epok 2023-01-01 | 257 | 257 | 44 | 2,60 [1,79, 2,90] | 1,661 [1,152, 1,840] |

## Bilgi satırları (hüküm vermez)

- referans farkı alınmamış S: KP 665; q95 2,28 [2,14, 2,43]; ρ 1,601 [1,504, 1,712]
- yer bootstrap: KP 665; q95 2,42 [2,13, 2,68]; ρ 1,517 [1,331, 1,685]
- en büyük blok (4, 0) dışarıda: KP 613; q95 2,52 [2,11, 2,79]; ρ 1,577 [1,325, 1,748]
- kod 1'li istasyonlar dışarıda: KP 459; q95 2,78 [2,34, 3,03]; ρ 1,740 [1,470, 1,902]
- yer ağırlıklı: KP 665; q95 2,58 [2,10, 2,80]; ρ 1,599 [1,312, 1,741]
- bileşen bazında (ham; 3914 yakın istasyon): doğu medyan 0,010, %95 1,931, |.| %95 3,116; kuzey medyan 0,218, %95 2,305, |.| %95 3,406
- bileşen bazında (referans_farki; 3914 yakın istasyon): doğu medyan 0,024, %95 1,898, |.| %95 3,115; kuzey medyan -0,014, %95 1,986, |.| %95 3,390
- N1: yukarıda (ana ölçü).

## Marmara çevirisi (E3; önceden sabit)

Katman: havuz (n_y = 8 katmanında 199 < 300 küme-pencere). q95 2,42 [L₈ 2,06, U₈ 2,76], S50 0,79; √(L₈² − S50²) = 1,898. Etiket: alt sınır: düşük sismisiteli bölge tabanı (sınıf A güç yok).

| Geometri | D (km) | x (km) | G | Δs_alt | nokta √(q95²−S50²)/G | U₈/G |
|---|---|---|---|---|---|---|
| dengeli | 5 | 5 | 0,250 | 7,59 | 9,14 | 11,03 |
| dengeli | 5 | 10 | 0,352 | 5,39 | 6,48 | 7,82 |
| dengeli | 5 | 20 | 0,422 | 4,50 | 5,41 | 6,53 |
| dengeli | 5 | 30 | 0,447 | 4,24 | 5,11 | 6,16 |
| dengeli | 5 | 50 | 0,468 | 4,05 | 4,88 | 5,89 |
| dengeli | 10 | 5 | 0,148 | 12,86 | 15,48 | 18,68 |
| dengeli | 10 | 10 | 0,250 | 7,59 | 9,14 | 11,03 |
| dengeli | 10 | 20 | 0,352 | 5,39 | 6,48 | 7,82 |
| dengeli | 10 | 30 | 0,398 | 4,77 | 5,75 | 6,93 |
| dengeli | 10 | 50 | 0,437 | 4,34 | 5,23 | 6,31 |
| dengeli | 15 | 5 | 0,102 | 18,54 | 22,31 | 26,92 |
| dengeli | 15 | 10 | 0,187 | 10,14 | 12,21 | 14,73 |
| dengeli | 15 | 20 | 0,295 | 6,43 | 7,74 | 9,34 |
| dengeli | 15 | 30 | 0,352 | 5,39 | 6,48 | 7,82 |
| dengeli | 15 | 50 | 0,407 | 4,66 | 5,61 | 6,77 |
| ayni_yan | 5 | 5 | 0,250 | 7,59 | 9,14 | 11,03 |
| ayni_yan | 5 | 10 | 0,148 | 12,86 | 15,48 | 18,68 |
| ayni_yan | 5 | 20 | 0,078 | 24,35 | 29,30 | 35,36 |
| ayni_yan | 5 | 30 | 0,053 | 36,11 | 43,46 | 52,45 |
| ayni_yan | 5 | 50 | 0,032 | 59,84 | 72,01 | 86,91 |
| ayni_yan | 10 | 5 | 0,352 | 5,39 | 6,48 | 7,82 |
| ayni_yan | 10 | 10 | 0,250 | 7,59 | 9,14 | 11,03 |
| ayni_yan | 10 | 20 | 0,148 | 12,86 | 15,48 | 18,68 |
| ayni_yan | 10 | 30 | 0,102 | 18,54 | 22,31 | 26,92 |
| ayni_yan | 10 | 50 | 0,063 | 30,21 | 36,36 | 43,88 |
| ayni_yan | 15 | 5 | 0,398 | 4,77 | 5,75 | 6,93 |
| ayni_yan | 15 | 10 | 0,313 | 6,07 | 7,30 | 8,81 |
| ayni_yan | 15 | 20 | 0,205 | 9,27 | 11,15 | 13,46 |
| ayni_yan | 15 | 30 | 0,148 | 12,86 | 15,48 | 18,68 |
| ayni_yan | 15 | 50 | 0,093 | 20,46 | 24,63 | 29,72 |
| karsi_yan | 5 | 5 | 0,750 | 2,53 | 3,05 | 3,68 |
| karsi_yan | 5 | 10 | 0,852 | 2,23 | 2,68 | 3,23 |
| karsi_yan | 5 | 20 | 0,922 | 2,06 | 2,48 | 2,99 |
| karsi_yan | 5 | 30 | 0,947 | 2,00 | 2,41 | 2,91 |
| karsi_yan | 5 | 50 | 0,968 | 1,96 | 2,36 | 2,85 |
| karsi_yan | 10 | 5 | 0,648 | 2,93 | 3,53 | 4,26 |
| karsi_yan | 10 | 10 | 0,750 | 2,53 | 3,05 | 3,68 |
| karsi_yan | 10 | 20 | 0,852 | 2,23 | 2,68 | 3,23 |
| karsi_yan | 10 | 30 | 0,898 | 2,12 | 2,55 | 3,07 |
| karsi_yan | 10 | 50 | 0,937 | 2,03 | 2,44 | 2,94 |
| karsi_yan | 15 | 5 | 0,602 | 3,15 | 3,79 | 4,58 |
| karsi_yan | 15 | 10 | 0,687 | 2,76 | 3,32 | 4,01 |
| karsi_yan | 15 | 20 | 0,795 | 2,39 | 2,87 | 3,47 |
| karsi_yan | 15 | 30 | 0,852 | 2,23 | 2,68 | 3,23 |
| karsi_yan | 15 | 50 | 0,907 | 2,09 | 2,52 | 3,04 |

a = 1,96 mm/yıl ({'geometri': 'karsi_yan', 'D': 5.0, 'x': 50.0}); c (dengeli, D = 10, x = 20) = 5,39 mm/yıl.

> Bu ölçüm ve bu model altında, yıl ölçekli GNSS hız değişimi alarmı Marmara benzeri geometride derin kayma hızındaki 1,96 mm/yıl'dan küçük değişimleri %5 yanlış alarm düzeyinde yarıdan fazla olasılıkla göremez (alt sınır; temsilî geometride 5,39 mm/yıl). Karşılaştırma için Prens Adaları kesiminde yayımlanmış kayma açığı hızı 10–15 mm/yıl'dır (Ergintav 2014, özetten).

İstanbul kuralı (Ö3): Bu ölçüm yolu kapatamadı. Bu hüküm yolun açık olduğu anlamına gelmez.

TR-11 hiçbir durumda "yol açık" hükmü vermez. Sonuç bir olasılık terimi değildir.

## Girdiler (sha256)

- küme listesi: 79f6cf0f9a1a11d932617b20c7b866bb5125a3acea62d35325af9364f027cbbd
- DataHoldings.txt: 4a98b65ad74c425b7b173e91b25ce5fd03be48e4b56a01c902c878247df4ad30
- steps.txt: 887501a438c41c3464788e5f6b5b50ec915f4ed7d2a759fe1e2bd8970d8ec668
- m6_havuz.csv: 969c5c54851ee353f01194c27bdd3f78203e3fe166eaefa9aa0e10ef0f5e211c
- birincil_aday.csv: f905535cf0837dbba2a67f7d4056205bacfdec0880983387b88c4658e5cd548b
- birincil_aday_fm.csv: 8c9cae2206b35c1199c7dc60b2e26cf766aede561d0299ef81a282e2259e2e2e
- mekanizma.jsonl: eb30828a7a1fff1706dff3d350d28fdfa8d51d7df7d8ae8025c8b0407f716d63
- indirme manifesti: a5ed059239d7a95a0b0b9a8e0cbf153bfb4d60ed30f7ae6a4759d4a1471f9fbb (4730 tenv3 dosyası; tek tek sha256 değerleri JSON'da)
- Ö4 istasyonları (Marmara kutusuna < 150 km): AFYN, AKHR, CMLD, KLUU, KRBK; w1 sonrası satırlar okunmadan okuma durduruldu; dosyalar koşudan sonra silinir.
