# TR-10b sonuç

Hüküm: TR-10b: veri yok (kural seti B: yer 8 / yer-pencere 11; kapı ≥ 20 / ≥ 40). Bilgi satırı, kapı altı: |Δv| q50 1,59, q95 3,41 [2,23, 3,81] mm/yıl (sünen katmanda hızın %45'si [25, 49]); bu satır bir hüküm değildir. (≤ 3 km'de kümelenince 8 yer kümesi)

## Veri kapısı

- Kural seti B: yer 8, yer-pencere 11, kesim K = 2; kapı geçmedi (≥ 20 / ≥ 40). Yer kümesi (≤ 3 km): 8.
- Kural seti A: yer 4, yer-pencere 4; kapı altı.
- İstasyon düzeyi (bilgi): istasyon 8, istasyon-pencere 11.
- Düşme nedenleri (istasyon-pencere): {'doluluk': 6, 'boşluk': 2, 'HDR': 23, 'geçerli': 11, 'kapsam yok': 29, 'uç değeri': 7}.
- Kaynak dökümü (yer-pencere): {'DAY': 0, '10MIN': 11, 'MIC': 0}.
- Bilgi değişkelerinin sayımları (hükmü değiştirmez): {'başlık katılmış (Ek 1 E1.3)': {'yer': 12, 'yer_pencere': 15, 'kesim': 3, 'kaynak': {'DAY': 0, '10MIN': 15, 'MIC': 0}}, 'MIC dar aralık (Ek 1 E1.4)': {'yer': 8, 'yer_pencere': 11, 'kesim': 2, 'kaynak': {'DAY': 0, '10MIN': 11, 'MIC': 0}}, 'HDR olayları uygulanmadan': {'yer': 16, 'yer_pencere': 27, 'kesim': 4, 'kaynak': {'DAY': 0, '10MIN': 27, 'MIC': 0}}}.
- Dolgulu yer-pencere: 0 (eğimi sıfır 0); kaynak|epok: {}.
- Manifest: başarısız 0 (pay 0,000); sha256 denetimi geçti.
- Okuma sayaçları: {'satir': 49023666, 'baslik': 0, 'bos': 0, 'aralik_ici': 7593834, 'aralik_disi': 41429832, 'aralik_disi_bozuk': 0, 'bozuk': 0}; biçim belirsiz: ['https://escweb.wr.usgs.gov/share/langbein/Archive/CREEP/DAY/xhr3.day.gz'].
- HDR adımı sayacı (§6.4 madde 4): {'K_dusen_B': 23, 'K_dusen_creep_event_B': 1, 'not_': "§6.4 madde 4: HDR adımında (veri öncesi, U kapsamı) K olayıyla düşen B istasyon-pencerelerinden notunda 'creep'/'event' geçenler; bilgi"}.
- Düzeltme turu: 0.

## Kod denetimleri (gerçek Δv görülmeden)

- (a) tam maske en büyük hata 0,000446 (≤ 0,005); gerçek maske en büyük 0,0725 (≤ 0,50); elle katman 0,000000000 (≤ 1e-6).
- (a3) 0,000000000; (a4) 0,000000000 (≤ 1e-6).
- (b) n 11, R 75: q95 pay 5,458 / payda 5,302 = 1,029 ([0,88, 1,12]; geçti). Bilgi, tam maskeli payda: 5,339, oran 1,022.
- 144 satırlık 10MIN: 11 yer-pencere, en büyük fark 0,00286 (≤ 0,005).
- (c-yapay): {'tele_N': 11, 'man_N': 0, 'tele_medyan': 4.962709254445964, 'tele_en_kucuk': 4.843349945906338, 'tele_en_buyuk': 5.041585487328765, 'sart1': True, 'sart2': True, 'sart3': True, 'gecti': True}.
- (c-gerçek): {'tele_N': 5, 'man_N': 0, 'tele_medyan': 5.000000000000001, 'tele_en_kucuk': 4.959998369656879, 'tele_en_buyuk': 5.000000000000003, 'sart1': True, 'sart2': True, 'sart3': True, 'gecti': True, 'secili': 5}.

## Ölçü satırları (§11)

- 1. Ana (B) [kapı altı]: N 11, yer 8, kesim 2 (aralık: site bootstrap'ı, K = 8); |Δv| q50 1,59 [0,72, 2,53], q95 3,41 [2,23, 3,81], q99 3,73 [2,47, 3,81] mm/yıl; |r| % q50 25 [12, 38], q95 45 [25, 49], q99 48 [25, 49] (sünen N 10); işaretli medyan -1,25 [-2,53, -0,42], hızlanan pay 0,18 [0,00, 0,40], yavaşlayan pay 0,82 [0,60, 1,00]; κ 2,15 [1,36, 4,02]; q99/q95 1,09 [1,00, 1,22]; b* 1,92 [1,25, 2,14]
   - README modeli: N_R 3, q95_N0,R 17,04, ρ_R 0,22 [0,13, 0,88] (güç yok); T ≥ 2008: N 3, ρ 0,22. Güç yasası serisi okuma aralığının başında sıfırdan başlar; n > 2'de sonuç bu seçime bağlıdır.
   - q99: N < 300: bilgi.
- 5. A satırı [kapı altı]: N 4, yer 4, kesim 1 (aralık: site bootstrap'ı, K = 4); |Δv| q50 1,09 [0,66, 1,55], q95 1,77 [0,94, 1,86], q99 1,84 [0,94, 1,86] mm/yıl; |r| % q50 32 [18, 44], q95 48 [26, 49], q99 49 [26, 49] (sünen N 4); işaretli medyan -0,81 [-1,55, 0,94], hızlanan pay 0,25 [0,00, 0,75], yavaşlayan pay 0,75 [0,25, 1,00]; κ 1,61 [1,00, 2,62]; q99/q95 1,04 [1,00, 1,06]; b* 0,99 [0,53, 1,04]

### Kesim dökümü (yer bootstrap'ı)
- kesim HAY [kapı altı]: N 7, yer 4, kesim 1 (güç yok; aralık yok); |Δv| q50 1,25, q95 1,95, q99 1,98 mm/yıl; |r| % q50 38, q95 46, q99 49 (sünen N 7); işaretli medyan -0,46, hızlanan pay 0,29, yavaşlayan pay 0,71; κ 1,56; q99/q95 1,02; b* 1,10
- kesim SAF_Parkfield [kapı altı]: N 4, yer 4, kesim 1 (güç yok; aralık yok); |Δv| q50 2,77, q95 3,69, q99 3,79 mm/yıl; |r| % q50 22, q95 24, q99 24 (sünen N 3); işaretli medyan -2,77, hızlanan pay 0,00, yavaşlayan pay 1,00; κ 1,33; q99/q95 1,03; b* 2,07

### Epok dökümü (bloklu)
- epok 2003 [kapı altı]: N 4, yer 4, kesim 1 (güç yok; aralık yok); |Δv| q50 1,09, q95 1,77, q99 1,84 mm/yıl; |r| % q50 32, q95 48, q99 49 (sünen N 4); işaretli medyan -0,81, hızlanan pay 0,25, yavaşlayan pay 0,75; κ 1,61; q99/q95 1,04; b* 0,99
- epok 2008 [kapı altı]: N 2, yer 2, kesim 1 (güç yok; aralık yok); |Δv| q50 1,22, q95 1,92, q99 1,98 mm/yıl; |r| % q50 25, q95 37, q99 38 (sünen N 2); işaretli medyan -1,22, hızlanan pay 0,00, yavaşlayan pay 1,00; κ 1,56; q99/q95 1,03; b* 1,08
- epok 2013 [kapı altı]: N 5, yer 5, kesim 2 (güç yok; aralık yok); |Δv| q50 2,53, q95 3,65, q99 3,78 mm/yıl; |r| % q50 23, q95 38, q99 39 (sünen N 4); işaretli medyan -2,53, hızlanan pay 0,20, yavaşlayan pay 0,80; κ 1,44; q99/q95 1,04; b* 2,05

### Katman ve kaynak dökümü
- katman tele [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- katman man: N 0
- kaynak DAY: N 0
- kaynak 10MIN [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- kaynak MIC: N 0

### Bilgi satırları
- Parkfield dışı [kapı altı]: N 7, yer 4, kesim 1 (güç yok; aralık yok); |Δv| q50 1,25, q95 1,95, q99 1,98 mm/yıl; |r| % q50 38, q95 46, q99 49 (sünen N 7); işaretli medyan -0,46, hızlanan pay 0,29, yavaşlayan pay 0,71; κ 1,56; q99/q95 1,02; b* 1,10
- yalnız T ≥ 2008 [kapı altı]: N 7, yer 6, kesim 2 (güç yok; aralık yok); |Δv| q50 1,99, q95 3,57, q99 3,76 mm/yıl; |r| % q50 23, q95 39, q99 40 (sünen N 6); işaretli medyan -1,99, hızlanan pay 0,14, yavaşlayan pay 0,86; κ 1,79; q99/q95 1,05; b* 2,01
- D olayları dışarıda [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- yalnız telemetri [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- SAYIM R2 alt kümesi [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- HDR olayları uygulanmadan [kapı altı]: N 27, yer 16, kesim 4 (aralık: kesim bootstrap'ı, K = 4); |Δv| q50 1,87 [1,25, 3,29], q95 5,70 [2,77, 13,85], q99 20,27 [5,38, 25,22] mm/yıl; |r| % q50 23 [22, 26], q95 53 [27, 93], q99 107 [27, 124] (sünen N 26); işaretli medyan -0,46 [-2,07, -0,37], hızlanan pay 0,41 [0,31, 0,47], yavaşlayan pay 0,59 [0,53, 0,69]; κ 3,05 [1,88, 5,37]; q99/q95 3,56 [1,00, 4,58]; b* 3,20 [1,56, 7,78]
- B1 geçmiş 5 y [kapı altı]: N 7, yer 4, kesim 1 (güç yok; aralık yok); |Δv| q50 1,25, q95 1,95, q99 1,98 mm/yıl; |r| % q50 38, q95 46, q99 49 (sünen N 7); işaretli medyan -0,46, hızlanan pay 0,29, yavaşlayan pay 0,71; κ 1,56; q99/q95 1,02; b* 1,10
- dolgulu yer-pencereler dışarıda [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- XDL2 dışarıda [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- başlık katılmış (Ek 1 E1.3) [kapı altı]: N 15, yer 12, kesim 3 (güç yok; aralık yok); |Δv| q50 1,59, q95 4,52, q99 5,86 mm/yıl; |r| % q50 25, q95 49, q99 49 (sünen N 14); işaretli medyan -1,25, hızlanan pay 0,20, yavaşlayan pay 0,80; κ 2,85; q99/q95 1,29; b* 2,54
- MIC dar aralık (Ek 1 E1.4) [kapı altı]: N 11, yer 8, kesim 2 (güç yok; aralık yok); |Δv| q50 1,59, q95 3,41, q99 3,73 mm/yıl; |r| % q50 25, q95 45, q99 48 (sünen N 10); işaretli medyan -1,25, hızlanan pay 0,18, yavaşlayan pay 0,82; κ 2,15; q99/q95 1,09; b* 1,92
- yer bootstrap'ı aralıkları [kapı altı]: N 11, yer 8, kesim 2 (aralık: site bootstrap'ı, K = 8); |Δv| q50 1,59 [0,72, 2,53], q95 3,41 [2,23, 3,81], q99 3,73 [2,47, 3,81] mm/yıl; |r| % q50 25 [12, 38], q95 45 [25, 49], q99 48 [25, 49] (sünen N 10); işaretli medyan -1,25 [-2,53, -0,42], hızlanan pay 0,18 [0,00, 0,40], yavaşlayan pay 0,82 [0,60, 1,00]; κ 2,15 [1,36, 4,02]; q99/q95 1,09 [1,00, 1,22]; b* 1,92 [1,25, 2,14]
- README N0, T ≥ 2008 [kapı altı]: N 3, yer 3, kesim 1 (güç yok; aralık yok); |Δv| q50 3,01, q95 3,73, q99 3,79 mm/yıl; |r| % q50 15, q95 21, q99 21 (sünen N 2); işaretli medyan -3,01, hızlanan pay 0,00, yavaşlayan pay 1,00; κ 1,24; q99/q95 1,02; b* 2,10
- Menteşe modeli Δv_m: N 11, |Δv_m| q50 1,55, q95 5,47 (rank düşen 0).

## Girdiler

```
{
 "onkayit_sha256": "6993ae4a6432f482d0507dde5e479ade18bf4517adbd5540584bbeec51b64da4",
 "onkayit_donmus_boy": 77114,
 "onkayit_tam_dosya_sha256": "dedaed32fb445493e45316c309e16c66233de21f6f7fbadebb41e425dee1545c",
 "onkayit_tam_boy": 82818,
 "listeler_json_sha256": "d0c2246007c25f11027cc3325ff3cfa53b3984296d0cf6c82f30e8dacffdcba5",
 "hdr_csv_sha256": "5171bd52941b47bb260cd6444eb4c5933c19b9ce10fb15b50fd667ead110531a",
 "hdr_baslik_csv_sha256": "c3f8cabb95ed2415cf540399d6dfb3a9195cb7a52377315b7015840885796dea",
 "hdr_etki_sha256": "89632d2f57ac11f2081df3bf85b63b42ede495ef059f94098aa7e5635185ea03",
 "manifest_veri_sha256": "c3c83720f06b08335c7a24888e75585ea9a777e5a742578d28d6ffa79a1197d3",
 "kosu_kodu_sha256": "fe4d7251b2057f29c63a128c1f0d01f3cfa40e3c37ea5dc081c210005ffa2fd0",
 "yardimci_kod_sha256": {
  "tr10b_listeler.py": "551fd4042c5b1b4628862065821f33a3c9c9f78b05562f78bbb0245843e535fc",
  "tr10b_sayim.py": "9d42555187b091fad118662efafd4a4cd8982cb11af7ad110ddd9022e71205c0",
  "tr2_sayim.py": "898f9a41d94daf567a3b270ad1c612c509c5444f1f0dbed51199c423bf908c95"
 },
 "liste_sha256": {
  "B": "17f120d295447f7aa102f3d8d18c223e7f0822ac9ca0467e6690b5c094997101",
  "A": "c027949015ff962f9e8ec56990f2808642c1a39c81c725c9bb615f094857a422",
  "B_R2": "560b49c1c634202a5451c85da8e26fb87059fe6e025a1956f53989cece6d036d",
  "A_R2": "cc238e03b244ec752928c705967647830e859b92d0c9e11f23df427e44b71426",
  "B1_gecmis5": "33b8eafab4782c417c70f55a1606aecdf4fb1466e2c96817a53f2ef453d20b52"
 }
}
```

