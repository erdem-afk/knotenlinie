# TR-13b ön kayıt TASLAĞI, sürüm 2: büyük doğrultu atımlı depremden 2–3 yıl önce sismisite yerelleşmesi, sınırlı koşu

Tarih: 16 Kasım 2026. Durum: **TASLAK (sürüm 2). Dondurulmadı. Gerçek katalogda hiçbir yerelleşme ölçüsü (V(q), z)
hesaplanmadı. Hiçbir katalog indirilmedi, ham arşiv açılmadı.**
Sürüm 1: `TR-13b_sinirli-kosu_ONKAYIT_surum1.md`. İnceleme: `TR-13b_INCELEME-1.md` ("düzeltmeyle kabul"; commit
d846acf). Bu sürüm zorunlu düzeltmeler Z1–Z5'in hepsini ve öneriler Ö1–Ö4'ü işler (§11 eşleme tablosu).
Dayanaklar: `ESIK-DAYANAGI.md`, `TR-13_SAYIM.md` + Ek 1, `kayit/turetme/tr13/`.

Hesaplar (yalnız yapay ETAS; tek gerçek girdi `tr13_tamsayim.json`'daki üstveri satırları: olay, küme, R, Mc, N3bg):
- `kayit/turetme/tr13b/tr13b_v2_mde.py` → `tr13b_v2_mde.json` (tohum 20261121, ≈ 9 dk): listenin gerçek (R, N3bg)
  bileşimiyle MDE (Z2), çok olaylı küme puanı (Z3), üç dallanma kuralı (Z4), keşif kümeleri (Z1), plasebo denetimi (Z5).
- Sürüm 1 hesapları (`tr13b_mde.*`, `tr13b_K.*`) ve inceleme hesapları (`inc1/`) karşılaştırma içindir.

## 0. Özet

- **Örneklem (üstveriden tahmin):** ana tasarım 16 olay / 14 küme. Ortak Mc kuralı (§3) Ishigaki 2009'u düşürür
  (N3bg 58 → ≈ 37 < 50; b = 1 varsayımıyla): **15 olay / 13 küme**. Keşif kümeleri (397 Superstition Hills + Hector
  Mine, 979 Ridgecrest, 395 İzmit) dışarıda **K = 10**. Hükmün öznesi bu K = 10 satırıdır (Z1). İnceleme K = 11
  diyordu; fark Ishigaki'dir. Gerçek sayı koşuda, gerçek Mc'lerle belli olur.
- **MDE (güç 0,8; listenin gerçek R'leri 58–426 km ve doyma sonrası N3bg 74–100 ile; f = önce-penceredeki arka planın
  kırık bandına taşınan kesri):**
  - T1, dallanma 0,6, bütün liste (K = 13): **f ≈ 0,33**
  - üç dallanmanın üçünde de, bütün liste: 0,35
  - üç dallanma, keşif dışı (K = 10): 0,385
  - üç dallanma, bütün liste ve keşif dışı birlikte: **0,39**
  - **tam "VAR" kuralı (yukarıdaki + Z5 plasebo denetimi): f ≤ 0,5 içinde güç 0,8'e ulaşılmıyor** (f = 0,4'te 0,65;
    0,5'te 0,70). MDE **> 0,5**.
- Sürüm 1'in "f ≈ 0,20–0,28" başlığı R = 80 km, türdeş N3bg ve K = 14 içindi. Gerçek bileşim, keşif dışı K, dallanma
  kuralı ve plasebo denetimi MDE'yi yaklaşık iki katına çıkardı.
- **Tasarım kendi içinde tutarlı, ama tam kuralla güçsüz.** f > 0,5, üç yılda arka planın yarıdan fazlasının 2 km'lik
  banda toplanması, yani bant payının yapayda ≥ 2,5 katına çıkması demektir. Makullüğü doğrulanamadı; büyük olasılıkla
  ancak abartılı bir etkiyi görür. Olumsuz sonuç bundan küçük her etki için bilgisizdir. Bu sayı adayı kurtarmak için
  değiştirilmedi.
- **Z5 denetiminin bedeli ve getirisi (yapay, R 80, N3bg 100, K 14):** durağan sürülerde yanlış alarmı 0,091'den
  0,064'e, kenar ağ kaybında 0,078'den 0,057'ye indiriyor; f = 0,3'te gücü 0,82'den 0,55'e düşürüyor. İkinci
  incelemeye açık soru (§9.4): denetim hükmü bağlasın mı, bilgi satırı mı olsun. Bu sürümde inceleme kuralı (bağlar)
  uygulanmıştır.

## 1. Soru (sınırlı)

Temiz önce-pencereli, referans dönemi dolu, sığ doğrultu atımlı Mw ≥ 6,5 ana şoklardan önceki 3 yılda,
kümesizleştirilmiş arka plan sismisitesinin kesirsel alanı V(0,5), aynı bölgenin önceki 7 yılına göre, ETAS'ın
sinyalsiz ürettiğinden **büyük ölçüde** daha mı küçük (yerelleşme)? Yalnız büyük etkiyi sorar. Tahmin değildir.
"VAR" cümlesi yalnız BZ20'nin keşif olayları dışındaki bölgeler için kurulur (Z1).

## 2. Örneklem

- Ana tasarım (TR-13 Ek 1, değiştirilmeden): M ≥ 6,5, Mc = MAXC + 0,2, N3bg ≥ 50, temiz önce-pencere, referans dolu
  (tol 0,3). Liste `tr13_tamsayim.json`'dan (`M ≥ 6,5` ve `ref_gecer["0.3"]`) aynen alınır: 16 olay, 14 küme.
- Eşleşik depremsiz kontrol şartı yok; yerine ETAS kalibrasyonu (§3).
- **Keşif kümeleri (Z1):** 397 (Superstition Hills 1987 + Hector Mine 1999), 979 (Ridgecrest 2019), 395 (İzmit 1999).
  Bunlar BZ20'nin ya da EGU 2020 özetinin iddiayı kurduğu olaylardır. Ana satırda tutulur ama "VAR" ayrıca bunlar
  dışarıdayken ister.
- **Üstveriden bileşim (b = 1 varsayımıyla; koşuda gerçek sayılarla yeniden kurulur):**

| Küme | Olay | R (km) | N3bg (Mc_önce) | Mc_önce / Mc_ref | Mc artışı | doyma sonrası N3bg |
|---|---|---|---|---|---|---|
| 397* | Superstition Hills 1987 | 66,5 | 215 | 2,0 / 1,7 | 0,4 | 86 |
| 397* | Hector Mine 1999 | 135,8 | 991 | 1,6 / 1,8 | 1,0 | 99 |
| 160 | Loma Prieta 1989 | 102,1 | 608 | 1,3 / 1,4 | 0,8 | 96 |
| 303 | Kobe 1995 | 102,1 | 194 | 2,6 / 2,6 | 0,3 | 97 |
| 395* | İzmit 1999 | 277,4 | 227 | 2,9 / 2,9 | 0,4 | 90 |
| 1141 | Big Lagoon açığı 2005 | 156,7 | 112 | 2,4 / 2,5 | 0,1 | 89 |
| 727 | Darfield 2010 | 117,8 | 100 | 2,7 / 2,7 | 0 | 100 |
| 802 | Cook Boğazı 2013 | 57,7 | 74 | 2,6 / 2,6 | 0 | 74 |
| 901 | Kumamoto 2016 | 117,8 | 4225 | 0,5 / 0,6 | 1,7 | 84 |
| 942 | Chiniak açığı 2018 | 425,6 | 575 | 1,8 / 2,1 | 0,8 | 91 |
| 979* | Ridgecrest 2019 | 135,8 | 576 | 1,4 / 1,4 | 0,8 | 91 |
| 1139 | Jamaika açığı 2020 | 319,9 | 310 | 2,2 / 2,4 | 0,5 | 98 |
| 1139 | Küba açığı 2024 | 88,5 | 156 | 1,0 / 1,0 | 0,2 | 98 |
| 1035 | Gisborne açığı 2021 | 180,7 | 431 | 2,6 / 2,8 | 0,7 | 86 |
| 1144 | Jan Mayen 2025 | 57,7 | 223 | 1,7 / 1,8 | 0,4 | 89 |
| (689) | Ishigaki 2009 — **düşer** | 76,7 | 58 | 2,1 / 2,3 | – | ≈ 37 < 50 |

  (* keşif kümesi.) R 57,7–425,6 km (sürüm 1'deki "50–200 km" yanlıştı; Z2).
- **Eksik parça kuralı (Ö1):** ham arşivde (`tr13-ham`, sha256 listesi `tr13_ham_sha256.txt`) bir olayın önce ya da
  referans penceresinin herhangi bir parçası yoksa o olay "veri yok" sayılır ve düşer; yeni indirme yapılmaz.

## 3. Ölçü ve sınama (önceden sabit)

Adım sırası (Ö2), her olay için:
1. Mc_önce ve Mc_ref TR-13 Ek 1'deki gibi; **ortak Mc_b = max(Mc_önce, Mc_ref)**, önce ve referansa birlikte uygulanır.
2. GK74 Mc_b ile koşulur; önce-pencere arka plan sayısı N3bg < 50 ise olay düşer.
3. **Doyma kuralı:** N3bg > 100 ise Mc_b 0,1 artırılır, **GK74 yeniden koşulur**, sayı ≤ 100 olana dek yinelenir. Yükseltilen
   Mc hem önce-pencereye hem referansa uygulanır. Son adımda N3bg < 50 olursa olay düşer.
   **Gerekçe (Ö3): güç.** Yapayda eşleşik kalibrasyonla doymuş bölgede α 0,03–0,04 kalıyor (INCELEME-1 D6), ama güç
   f = 0,3'te 0,30–0,36'ya iniyor (N3bg 50'de 0,94). Sürüm 1'deki "α %21" gerekçesi kalibrasyon uyuşmazlığıydı.
4. Ölçü: 5 km hücre, V(0,5), referanstan aynı sayıda olayla 200 alt örnek, z = (V_önce − ort) / sd; yerelleşme z < 0.
   BZ20'nin gerekçeli yeniden kurulumudur, aynısı değildir.
5. **ETAS sıfır havuzları (Z4, Ö4):** her olay için kendi R'si ve son N3bg'siyle, dallanma **0,4, 0,6 ve 0,8** için
   ayrı ayrı ≥ 2000 sinyalsiz ETAS bölgesi (öteki parametreler TR-13 §4.1). Her bölgede hem olay z'si hem plasebo z_p'si
   (önce [t − 6 y, t − 3 y), referans [t − 10 y, t − 6 y)) alınır. En çok olabilirlik dallanma uydurması yapılmaz.
6. **Küme puanı (Z3):** küme z = üyelerin z ortalaması. Sıfırda her üye kendi havuzundan bir çekiliş alır, küme içinde
   ortalanır. İki çok olaylı küme: 397 (Superstition Hills + Hector Mine), 1139 (Jamaika + Küba).
7. **T1:** z̄ = küme z'lerinin ortalaması. Her dallanma d için p_d = P(z̄_sıfır,d ≤ z̄_gözlenen), 200 000 çekiliş.
   Hem bütün liste (K_ana) hem keşif dışı (K_kd) için ayrı ayrı.
8. **Plasebo T1 (Z5):** z̄_p = küme z_p ortalaması; dallanma 0,6 havuzundan sıfır; p_plasebo = P(z̄_p,sıfır ≤ z̄_p).
9. Monte Carlo hatası (Ö4): her p için ikiterimli standart hata yazılır; 2000'lik tek havuzda havuz hatası ±0,02–0,03
   (INCELEME-1). p eşiğe ±0,03'ten yakınsa raporda "sınırda" diye işaretlenir; hüküm değişmez.
- T2 (eşli işaret çevirme) ve T3 (binom) bilgi satırıdır.

## 4. Etki büyüklüğü ve kaynağı

| Kaynak | Değer | Etiket | Durum |
|---|---|---|---|
| BZ20 (GJI 223, 561–583): 5 ana şok öncesi 2–3 yıl yerelleşme; Parkfield'da ters yön | kesirsel alan azalmasının büyüklüğü **okunamadı** | **literatür** | tam metin 403; özetten yalnız yön ve zaman |
| EGU 2023 özeti | 2–10 yıl önce geniş hacimde etkinleşme, 2–3 yıl önce sönme; yer dış merkezi içermeyebilir | **literatür** (özet) | yön ve yer tek anlamlı değil |
| Hasar reolojisi (Ben-Zion ve Zaliapin) | nitel öngörü, sayı yok | **kuram** | nicel değer yok |
| f ≈ 0,2 (TR-13 sayımı, "orta") | bant içi oran ≈ 2,5 kat | **tahmin** (benzetim) | makullük doğrulanamadı |
| Bu taslağın MDE'si | f ≈ 0,39 (Z5'siz), > 0,5 (tam kural) | **hesap** (yapay, gerçek bileşim) | §5 |

Etki büyüklüğünün kaynağı olmadığı için "MDE kuramın kaç katı" sorusu yanıtlanamıyor (INCELEME-1 F).

## 5. MDE ve ×0,5 / ×2 duyarlılığı (`tr13b_v2_mde.json`)

Güç (veri dallanma 0,6, her f için üye başına 150 bölge, 20 000 çekiliş):

| f | T1 (0,6), K = 13 | üç dallanma, K = 13 | üç dallanma, keşif dışı K = 10 | ikisi birlikte | **tam kural** (+ Z5) |
|---|---|---|---|---|---|
| 0 (bağımsız sıfır verisi) | 0,043 | 0,032 | 0,035 | 0,019 | 0,012 |
| 0,15 | 0,30 | 0,26 | 0,19 | 0,16 | 0,12 |
| 0,20 | 0,39 | 0,35 | 0,29 | 0,24 | 0,17 |
| 0,25 | 0,63 | 0,59 | 0,49 | 0,45 | 0,30 |
| 0,30 | 0,73 | 0,70 | 0,62 | 0,58 | 0,44 |
| 0,40 | 0,93 | 0,92 | 0,83 | 0,82 | 0,65 |
| 0,50 | 0,97 | 0,96 | 0,92 | 0,91 | 0,70 |
| **MDE f** | **0,33** | 0,35 | 0,385 | **0,39** | **> 0,5** |

- Karşılaştırma: sürüm 1 (R 80, türdeş N3bg, K 14) 0,20–0,28; inceleme (aynı) 0,24 / 0,29.
- Bant payı (yapay, R 80, N3bg 100; sürüm 1 hesabı): f = 0 → %8, f = 0,4 → %18 (2,2 kat), f = 0,5 → %20 (2,5 kat).
  Büyük R'li bölgelerde (Chiniak 426 km, Jamaika 320 km) bandın payı daha küçüktür; ölçülmedi.
- **×0,5 / ×2** (Z5'siz kural, MDE 0,39): yarısı f ≈ 0,2'de güç 0,24; iki katı f ≈ 0,78 benzetim aralığının dışında
  (f = 0,5'te zaten 0,91). Tam kural: MDE > 0,5; f = 0,25'te (yarısından da büyük) güç 0,30. Yarısı için gereken K
  ölçülmedi; sürüm 1'in K tablosuna göre ≈ 60–80 bölge (**tahmin**).
- Monte Carlo: güç sayılarının hatası ≈ ±0,03–0,05 (üye başına 150 bölgelik havuz; kalibrasyon başına μ ayarı
  gürültülü). MDE'ler ≈ ±0,03–0,05.

## 6. Z5 denetiminin yapay sınaması (R 80, N3bg 100, K 14, türdeş; aynı betik, bölüm B)

| Veri | T1 yanlış alarm / güç | T1 ve plasebo p > 0,20 | plasebo denetiminin "red" oranı |
|---|---|---|---|
| D0 ETAS, sinyalsiz | 0,035 | 0,025 | 0,28 (anma 0,20) |
| D1 durağan sürüler (INCELEME-1 tanımı) | **0,091** | **0,064** | 0,28 |
| D4 kenar ağ kaybı (aynı) | **0,078** | **0,057** | 0,22 |
| D0, f = 0,2 (güç) | 0,60 | 0,47 | 0,20 |
| D0, f = 0,3 (güç) | 0,82 | 0,55 | 0,33 |

- Denetim sürü ve ağ bozulmasının yanlış alarmını ≈ %30 azaltıyor, %5'e indirmiyor. Bedeli güçte ≈ %20–35.
- Plasebo denetiminin sinyalsiz red oranı 0,28 (anma 0,20): kalibrasyon havuzu ile veri havuzunun ayrı ayrı ayarlanan
  arka plan hızı farkından. Koşuda olay başına tek ayar kullanılır; yine de denetim tutucudur (gücü düşürür).
- Sürü ve ağ senaryolarının gerçek bölgelerdeki sıklığı ölçülmedi (INCELEME-1'in seçimi).

## 7. Hüküm dalları (sıra kodda sabit; gerçek z'ler 1–2'den sonra hesaplanır)

1. **Veri yok:** §2–3 kurallarından sonra keşif dışı K < 8, ya da ham arşiv sha256'ları `tr13_ham_sha256.txt` ile
   uyuşmuyor. MDE yine yazılır.
2. **Geçersiz:** yapay ETAS'ta bilinen f = 0,3 eklenince ortalama z `tr13b_v2_mde.json` beklentisinin ±%25'i dışında,
   ya da sinyalsiz yapayda kalibre T1 α > 0,08. Gerçek z görülmeden koşar.
3. **Büyük etki VAR:** (a) üç dallanmanın üçünde de bütün listede p ≤ 0,05; (b) üçünde de keşif dışı listede
   p ≤ 0,05; (c) p_plasebo > 0,20. Cümle (öznesi keşif dışı satır): "BZ20'nin keşif olayları dışındaki K = … bölgede,
   ana şoktan önceki 3 yılda kümesizleştirilmiş arka plan, ETAS'ın ürettiğinden belirgin biçimde yerelleşmiş; aynı
   bölgelerin 3 yıl önceki penceresi ETAS ile uyumlu. Tahmin ya da alarm iddiası değildir; ileriye dönük sınav ayrı ön
   kayıt ister."
4. **Ayırt edilemez (ETAS uyumsuzluğu):** (a) ve (b) sağlanıyor ama p_plasebo ≤ 0,20.
5. **Ayırt edilemez (MDE = …):** öteki her durum. Cümle: "Keşif dışı K = …; bu bileşimle görülebilir en küçük etki f ≈ …
   (koşudan önce, listenin gerçek R ve N3bg'siyle yapayda yeniden hesaplanan değer; bu taslakta > 0,5). Daha küçük
   yerelleşme hakkında bilgi yok."
6. **H0 hükmü yoktur.** z̄ > 0 da "ayırt edilemez"dir.

## 8. Olumsuz sonuç ne söyler, ne söylemez

- Söyler: bu ölçüyle (dış merkezli R = max(2L, 50 km) daire, 5 km hücre, V(0,5), GK74, referans alt örneklemeli z)
  ve ETAS sıfırına göre, önce-penceredeki arka planın yarısından fazlasının kırık bandına toplanması (bant payının
  ≳ 2,5 katına çıkması) BZ20'nin keşif olayları **dışındaki** 10 bölgede olağan değildir.
- Söylemez: BZ20 yanlış. BZ20'nin kendi olayları hakkında hiçbir şey; BZ20'nin ölçüsü (voksel, en yakın komşu
  kümesizleştirmesi, seçimsiz bölgesel ızgara, yeniden karıştırılmış katalog anlamlılığı); daha küçük yerelleşme;
  dış merkezi içermeyen yerelleşme; "sönme"; M ≥ 6,0 örneklemi; Marmara.

## 9. Varsayımdan bağımsız kusurlar ve çözümleri

1. **Yanlış alarm (%13–37 anma):** ETAS'tan olay başına, üç dallanmayla kalibre eşik (§3). ETAS içinde α ≤ 0,05.
2. **ETAS dışı bozulmalar (sürü, ağ):** Z5 denetimi; yanlış alarmı tam kapatmıyor (§6: 0,057–0,064). Kalan risk yazılır.
3. **Ölçü yeniden kurulum:** BZ20 tam metni okunursa dondurmadan önce karşılaştırılır; fark yazılır, ölçü değişmez.
4. **Açık soru (ikinci incelemeye):** Z5 hükmü bağlarsa MDE > 0,5 ve sınav pratikte yalnız abartılı etkiyi görür;
   bilgi satırı olursa MDE 0,39 ama sürü/ağ yanlış alarmı 0,08–0,09'a çıkar. Bu sürüm incelemenin kuralını uygular.
5. **Doyma kuralı** yoğun bölgelerde küçük olayları atar (Kumamoto'da Mc 1,7 birim artar); H0 yönünde.
6. **Temsil:** keşif dışı 10 küme: Yeni Zelanda 3, Kaliforniya 2, Japonya 2, Alaska 1, Karayip 1 (iki olay),
   Jan Mayen 1. Doğu Akdeniz yok. Marmara'ya çevrilmez.
7. **Bölge yarıçapı:** MDE artık gerçek R'lerle (58–426 km) hesaplandı. Benzetimde öteki fay parçalarının boyu
   20–60 km sabit; büyük R'li bölgelerde yapı gerçekçi olmayabilir.

## 10. Yeniden açma şartı

(a) BZ20 tam metni meşru yoldan okunur ve ölçü ya da etki büyüklüğü bu taslaktakinden farklıdır. (b) Yazarlardan bağımsız
bir ETAS yanlış alarm sınaması yayımlanır. (c) Daha düşük Mc'li açık bölgesel katalog keşif dışı K'yi ≥ 25'e çıkarır.
(d) "VAR" çıkarsa: ileriye dönük, alarm biçimli ayrı ön kayıt.

## 11. INCELEME-1 eşleme

| Madde | Nerede |
|---|---|
| Z1 keşif kümeleri dışarıda, hükmün öznesi | §0, §2, §7.3, §8 |
| Z2 MDE gerçek (R, N3bg) bileşimiyle; başlık; R 58–426 | §0, §2, §5 |
| Z3 çok olaylı küme puanı | §3.6 |
| Z4 tek dallanma kuralı (0,4/0,6/0,8'in üçü); uydurma yok | §3.5, §3.7, §7.3 |
| Z5 plasebo ETAS uyumsuzluk denetimi ve yapay etkisi | §3.8, §6, §7.4 |
| Ö1 eksik parça | §2 |
| Ö2 doyma adım sırası | §3 |
| Ö3 doyma gerekçesi "güç" | §3.3 |
| Ö4 havuz ≥ 2000, Monte Carlo hatası | §3.5, §3.9 |

## 12. Körlük ve İstanbul

Gerçek katalogda V(q), Gini ya da z hesaplanmadı; katalog indirilmedi, ham arşiv açılmadı; ana şok sonrası pencere
yok. Bütün 2026 verisi kördür; katalog 2025-12-31'de biter. Sonuç bir olasılık terimi değildir. İstanbul için mutlak
olasılık yazılmaz. İzmit 1999 bir keşif kümesidir ve Marmara terimi değildir.
