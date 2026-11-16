# TR-1b ön kayıt TASLAĞI, sürüm 2: deprem öncesi 2 yıllık GNSS hız değişimi, yerinde eşli sınırlı koşu

Tarih: 16 Kasım 2026. Durum: **TASLAK (sürüm 2). Dondurulmadı. Hiçbir tenv3 serisi, hiçbir olay penceresi açılmadı.**
Sürüm 1: `TR-1b_sinirli-kosu_ONKAYIT_surum1.md`. İnceleme: `TR-1b_INCELEME-1.md` ("düzeltmeyle kabul, koşullu";
commit 2eba1d7). Bu sürüm zorunlu düzeltmeler Z1–Z6'nın hepsini ve öneriler Ö1–Ö3'ü işler (§12 eşleme tablosu).
Dayanaklar: `ESIK-DAYANAGI.md`, TR-1 sürüm 2 ve iki incelemesi, TR-11 sonucu.

Hesaplar (yalnız yapay veri ve commit edilmiş TR-11 nicelikleri):
- `kayit/turetme/tr1b/tr1b_v2_z4.py` → `tr1b_v2_z4.json`: eşli sınamanın yapay yanlış alarmı ve MDE'si (Z4).
- İnceleme betikleri `kayit/turetme/tr1b/inc1/` (bağımsız modelle eşli MDE; c0 yanlış alarmı).
- Sürüm 1'in c0 hesabı `tr1b_mde.py/.json` (artık yalnız bilgi satırının dayanağı).
- Aşama 0 (yalnız üstveri): `kayit/turetme/tr1b/tr1b_asama0.py`, çıktısı `kayit/turetme/tr1b/asama0/`. Aşama 0 bu metin
  ve dal kuralı commit edildikten **sonra** bir kez koşulur; sonucu Ek 2'ye yazılır, kural seçmez (Z2).

## 0. Özet

- **Ana sınama artık eşli:** her olay kümesi kendi yerinin, 730 g geriye kaydırılmış penceresiyle (yerinde plasebo)
  karşılaştırılır. İstatistik d = log(S_olay / S_plasebo), sınama kesin tek yanlı işaret çevirme (2^K_p desen). Bölge
  şişmesi, ağ ve dönem iki pencerede ortaktır; sürüm 1'in tahmini c0 = 1,64 payına artık gerek yoktur (Z3).
- c0 sınaması **bilgi satırına** indi (Z5). Sürüm 1'in "c0 = 1" cümlesi kaldırıldı (Z6).
- **Dal kuralı (aşama 0'dan önce sabit, Z2):** aşama 0'ın üst sınır sayımında K_p ≥ 6 ise ön kayıt ikinci incelemeye
  gider ve koşulabilir; K_p < 6 ise **"veri yok (eşli küme)"** yazılır, koşu yapılmaz.
- MDE (Z4 yapay modeli, ısınmalı kırpışma, paylaşılan pencere parçası dahil): K_p = 8'de uyumlu sinyalde **g ≈ 2,0**,
  dağınıkta **≈ 3,9 mm/yıl**; K_p = 12'de 1,6 / 2,9 (§5). Z4 yapay yanlış alarmı 0,041–0,058: kapı (≤ 0,07) geçildi.
- Olumsuz sonuç kuramın öngördüğü (≈ 0,02–0,5 mm/yıl) etki hakkında yine **hiçbir şey** söylemez.

## 1. Soru (sınırlı)

M ≥ 6,5 sığ olaylardan önceki son 2 yılda, dış merkezin 100 km içindeki istasyonların hız değişimi boyu S, aynı yerde
aynı istasyonlarla 730 gün önce biten pencerede ölçülen S'ten sistematik olarak **büyük ölçüde** büyük mü? Yalnız büyük
etkiyi sorar; tahmin becerisi iddiası değildir.

## 2. Veri, pencereler, örneklem

- Olaylar: ComCat, 2000-01-01 → 2026-01-01T00:00:00 (2026 hariç), M ≥ 6,5, derinlik ≤ 30 km, T ≤ 2025-12-31. Dış
  merkezi Marmara kutusunda (39,5–42,0° K, 26,0–31,5° D) olan olay sayılmaz.
- GNSS: NGL IGS20 tenv3, yatay. Marmara kutusu istasyonları indirilmez; kutuya 150 km'den yakın istasyonlarda w1'den
  sonraki satırlar ayrıştırılmadan atlanır (TR-11 Ö4 ve Ek 2 kuralı).
- **Olay penceresi:** w1 = T − 7 g, w0 = w1 − 1825 g (1826 gün), menteşe H = T − 6 g − 730 g.
- **Plasebo penceresi (Z3):** aynı uzunluk, 730 g geriye kaydırılmış: w1_p = w1 − 730 g, w0_p = w0 − 730 g, menteşe
  H_p = H − 730 g. Plasebo, olay penceresinin H'den sonraki 2 yılına (öncülün arandığı kısım) hiç girmez. İki pencere
  [w0, w1_p] parçasını (1096 g) paylaşır; etkisi Z4'te ölçüldü (Ek 1).
- **İstasyonlar (iki pencerede aynı):** TR-11 §2.3 kuralları (kapsama, doluluk ≥ 0,60, kod 1 kenar ve menteşe ±30 g,
  kendi penceresinin [w0 − 730 g, w1] aralığında hiçbir kod 2 kaydı yok) **her iki pencerede ayrı ayrı** sağlanmalı.
  İkisinde de uygun istasyonlardan yakın ≤ 100 km (en yakın 3–8) ve referans 200–500 km (3–8) seçilir; iki pencere
  aynı istasyonlarla ölçülür.
- **Sakinlik (dış merkez; olay ve plasebo birlikte):** Ş1 200 km içinde [w0_p − 5 y, w1] arasında M ≥ 6,0 (z ≤ 40) yok;
  Ş2 500 km içinde [w0_p − 10 y, w1] arasında M ≥ 7,0 (z ≤ 70) yok; Ş3 1000 km içinde [w0_p − 10 y, w1] arasında M ≥ 8,0
  yok. Hedef olay w1'den sonradır ve kurala girmez.
- **Bağımsızlık kümeleri:** (i) dış merkezler < 300 km ve tarihler < 1 yıl; (ii) ortak istasyon ve [w0_p, w1]
  aralıkları çakışıyor; (iii) aynı 10° × 10° blok ve aralıklar çakışıyor. Bağlı bileşenler. **K_p** = eşli plasebosu
  kurulabilen küme sayısı. K = yalnız olay penceresiyle kurulan küme sayısı (bilgi).
- **Ölçü:** TR-11 koşu kodunun istasyon modeli ve S tanımı (`tr11_kosu.py`: olc, S_hesapla), iki pencerede aynı.

## 3. Ana sınama (eşli, kesin)

- Küme puanı d_k = kümedeki olayların log(S_olay / S_plasebo) ortalaması.
- İstatistik Σ d_k. Sıfır dağılımı: 2^K_p işaret deseni (K_p ≤ 20'de tam sayım; üstünde 10^6 rastgele desen).
  p = P(Σ ±d_k ≥ Σ d_k). Tek yanlı α = 0,05.
- **"Büyük etki VAR":** p ≤ 0,05 **ve** her "bir kümeyi dışarıda bırak" sınamasında p ≤ 0,10 **ve** Z4 kapısı geçilmiş
  (Ek 1: yapay yanlış alarm ≤ 0,07).
- Değiş tokuş edilebilirlik yaklaşıktır (paylaşılan parça, gürültünün zamanla değişmesi); Z4 bunu yapayda ölçer.

## 4. Etki büyüklüğü ve kaynağı

| Kaynak | Değer (S cinsinden) | Etiket | Durum |
|---|---|---|---|
| Yıl ölçekli GNSS öncül iddiaları (TR-12) | TR-11 tabanının (2,42) üstünde doğrulanan 0; 3 iddia altında; Bedford 2020 tersinmesi 0,3–2,8 mm/yıl; 8 iddia çevrilemedi | **literatür** | bir kısmı özetten; çevrilemeyenler "doğrulanamadı" |
| Sünme cephesinin 2 yıllık yüzey izi (Halka 8) | TR-11 tabanının 5–100 kat altı, ≈ 0,02–0,5 mm/yıl | **kuram** (tarayıcının hesabı) | doğrulanmadı |
| Bu sınavın "büyük etki"si | varsayım değil; K_p ile görülebilen en küçük g (§5) | **hesap** (yapay) | Ek 1 |
| c0 = 1,64 (sürüm 1) | TR-11'in **2008 epoğu (dönem) şişmesi**; ū biriminde 1,45. **Bölge yanlılığının ölçüsü değildir** (INCELEME-1 B) | **tahmin** | yalnız bilgi satırı (§6) |

## 5. MDE ve ×0,5 / ×2 duyarlılığı

Hüküm kuralının (p ≤ 0,05 ve LOO p ≤ 0,10) gücü 0,8. Sinyal, yakın istasyonlara doğuda g × max(0, t − H) eklenir;
"uyumlu" bütün istasyonlarda aynı, "dağınık" istasyon başına g × U(0, 1). Ana tablo Z4 modelinden (Ek 1:
TR-11'in b_f* = 4,6 kırpışması, ısınmalı, paylaşılan parça dahil). İncelemenin bağımsız modeli (pencereler bağımsız,
`tr1b_inc1_eslesik.json`) karşılaştırma için yanındadır.

| K_p | 6 | 8 | 10 | 12 |
|---|---|---|---|---|
| uyumlu g (mm/yıl), Z4 modeli (**ana**) | 2,39 | 1,96 | 1,74 | 1,58 |
| dağınık g, Z4 modeli (**ana**) | 4,76 | 3,87 | 3,32 | 2,89 |
| uyumlu g, inceleme modeli (pencereler bağımsız) | 1,35 | 1,10 | 0,95 | 0,87 |
| dağınık g, inceleme modeli | 2,82 | 2,15 | 1,84 | 1,68 |

Z4 modelinin MDE'si inceleme modelininkinin ≈ 1,7–1,8 katı. Nedeni büyük olasılıkla gürültü düzeyi: Z4, TR-11'in
ölçülen eşdeğer kırpışmasını (b_f* = 4,6 mm/yıl^0,25) kullanır; inceleme modeli TR-11'in S niceliklerine uydurulmuş
log-normal σ'dır. Ayrıştırılmadı. Tutucu olduğu için ana tablo Z4'tür.

**×0,5 / ×2 (Z4, K_p = 8; parantezde K_p = 12):** uyumlu MDE 1,96 → yarısı g = 0,98'de güç 0,25 (0,34), iki katı
g = 3,92'de 1,00 (1,00). Dağınık 3,87 → yarısı 1,94'te 0,31 (0,44), iki katı 7,74'te 1,00 (1,00). Yarısı için
K_p = 12 bile yetmez; gereken K_p ölçülmedi (≈ 1/etki² ölçeklemesiyle ≈ 30–35 beklenir; **tahmin**).

Sürüm 1 ile kıyas: c0 = 1,64 tasarımının K = 12 MDE'si 1,37 / 3,09 idi. Eşli tasarımın MDE'si K_p = 12'de 1,58 /
2,89, K_p = 8'de 1,96 / 3,87. Bedel daha büyük MDE; kazanç, yanlış alarmın bölge şişmesinden bağımsız olması.

Okuma: bölge şişmesi ne olursa olsun yanlış alarm değişmez (Ek 1, BOLGE2 satırı).

## 6. Bilgi satırları (hüküm vermez; Ö2)

Raporda **tek tabloda, şu sırayla** ve "hüküm vermez" başlığıyla basılır:
1. K (yalnız olay penceresi) ve K_p; bölge, mekanizma ve n_y katmanı bileşimi.
2. c0 sınaması (Z5): yalnız w0 ≥ 2008-01-01 olan olaylar; TR-11 tabanına karşı ortalama yüzdelik ū; c0 ū biriminde
   1,45; cümle "**c_gerçek ≤ c0 varsayımı altında** …" diye başlar. Bu alt kümede K < 6 ise satır "koşulmadı" yazılır.
3. TR-11 sınıf B küme-pencerelerinin ū'su (10 KP).
4. Bir kümeyi dışarıda bırakma p aralığı.
5. Literatür olayları (Ö3; aşama 0'da yazılan liste) dışarıda eşli p.
6. Bilinen yavaş kayma / volkanik bölge listesindeki kümeler dışarıda eşli p. Liste koşudan önce, olay S'i görülmeden,
   aşama 0 listesindeki her küme için "yavaş kayma bildirilmiş (evet/hayır)", "100 km içinde Holosen volkanı
   (evet/hayır)" diye yazılır.
7. Olay ve plasebo için yakın istasyon uzaklıklarının medyanı.

## 7. Aşama 0 (yalnız üstveri) ve dal kuralı (Z1, Z2)

- Girdi yalnız NGL `DataHoldings.txt`, `steps.txt` ve ComCat (≤ 2025-12-31). TR-1 ve TR-11 sayımlarının önbellekleri
  kullanılır (sha256 denetimli). Hiçbir konum zaman serisi indirilmez ya da açılmaz.
- Çıktı: K, **K_p**, w0 ≥ 2008 alt kümesinde K, bölge/mekanizma/katman bileşimi, literatür olaylarının durumu.
  **Dondurulan liste (Z1):** eşli kümeler ve olaylar (ComCat id, T, M, konum, katman üst sınırı, yakın ve referans
  istasyonlar), `asama0/tr1b_asama0_liste.json`, sha256 ile. Koşu bu sha256'ya assert eder.
- Doluluk aşama 0'da yalnız yaklaşık bilinir. **Dal kuralı üst sınır sayımını (doluluk atlanarak) kullanır:**
  - K_p ≥ 6 → eşli sınama ana hükümdür; ön kayıt ikinci incelemeden sonra dondurulup koşulabilir.
  - K_p < 6 → **"veri yok (eşli küme)"**; koşu yapılmaz, hiçbir seri indirilmez.
- Koşuda doluluk uygulandıktan sonra K_p < 6'ya düşerse yine "veri yok (eşli küme)" yazılır (§8.1).
- Aşama 0 bir kez koşulur. Kural, sonucu görüp değiştirilmez (TR-1 INCELEME-2 bulgu 9).

## 8. Hüküm dalları ve hesap sırası (Ö1)

Kod şu sırayla çalışır ve her adımı olay S'i hesaplanmadan **önce** günlüğe yazar:
1. **Veri yok:** liste sha256'sı uyuşmuyor, ya da doluluk sonrası K_p < 6, ya da TR-11 yeniden hesabı veri kapısını
   (≥ 100 yer, ≥ 30 blok) geçmiyor. MDE (K_p'ye göre tablo) yine yazılır.
2. **Geçersiz:** (a) Z4 yapay yanlış alarmı > 0,07 (Ek 1; koşu kodunun kendisiyle yeniden ölçülür); (b) TR-11 kod
   denetimleri (i), (ii-a), (ii-b) kalır; (c) TR-11 yeniden hesaplanan q95 [2,06, 2,76] dışında.
3. Ancak bunlardan sonra olay ve plasebo S'leri hesaplanır.
4. **Büyük etki VAR:** §3'ün üç şartı. Cümle: "Bu K_p kümede, olay öncesi 2 yıllık hız değişimi boyu aynı yerin 2 yıl
   önceki penceresinden belirgin biçimde büyük. Bu bir öncül ya da tahmin iddiası değildir; olaydan bağımsız ama
   T'ye doğru artan gürültü (yavaş kayma döngüsü, volkanik kabarma, ağ bozulması) bu sınamada öncülden ayrılmaz
   (§9, bilgi satırı 6)."
5. **Ayırt edilemez (MDE = …):** öteki her durum. Cümle: "K_p = …, görülebilir en küçük etki uyumlu sinyalde g = … mm/yıl,
   dağınık sinyalde g = … mm/yıl (Ek 1 tablosu). Daha küçük etkiler hakkında bilgi yok."
6. **H0 hükmü yoktur.** c0 bilgi satırı hiçbir dalı değiştirmez; "saf tabandan büyük" türü ikinci bir cümle yazılmaz (Z6).

## 9. Varsayımdan bağımsız kusurlar ve çözümleri

1. **Plasebo eksikliği:** eşli tasarımla çözüldü; 665 KP'lik TR-11 tabanı artık yalnız kod denetimi ve bilgi satırıdır.
2. **Tek kalan karıştırıcı — T'ye doğru artan, olaydan bağımsız gürültü:** "VAR" yönündedir ve büyüktür (Ek 1, ARTAN
   satırı: son 2 yılda gürültü × 1,5 olunca yanlış alarm K_p = 8'de 0,35, K_p = 12'de 0,51). Çözüm: hüküm cümlesi bunu açıkça söyler;
   bilgi satırı 6 bilinen yavaş kayma ve volkan bölgelerini dışarıda bırakır. Ayırt edemediği şey yazılır.
3. **Öteki yanlılıklar H0 yönündedir (tutucu):** eski pencerenin daha gürültülü olması (dönem, 2003–2008 GNSS'i),
   sönen postsismik, 2 yıldan uzun süren öncülün plasebo penceresine taşması.
4. **Paylaşılan pencere parçası:** iki ölçü bağımlıdır; işaret çevirmenin geçerliği Z4'te ölçüldü (Ek 1).
5. **Postsismik dışlama** önceden sabit (§2: kod 2 ve Ş1–Ş3, iki pencerede). Ş1, son 7 yılda 200 km'de M ≥ 6 öncüsü olan
   olayları atar (H0 yönünde).
6. **Ortak mod hatası:** referans farkı ve 10° blok kuralı; iki pencere aynı istasyonlarla ölçüldüğü için ortak mod
   büyük ölçüde sadeleşir.
7. **MDE model bağımlı:** Gauss istasyon gürültüsü, MAD ayıklaması ve kod 1 sıçraması yok, n_r = 8. Belirsizlik
   ≈ ±%10–20.

## 10. Olumsuz sonuç ne söyler, ne söylemez

- Söyler: bu K_p kümede, 100 km içindeki istasyonları birlikte (uyumlu) ya da dağınık biçimde Ek 1'deki g kadar
  oynatan, 2 yıl süren olay öncesi hız değişimi, aynı yerin 2 yıl önceki penceresine göre olağan değildir (güç 0,8).
- Söylemez: öncül yok. Kuramın öngördüğü ≤ 0,5 mm/yıl'lık izler, yönlü sinyaller, 2 yıldan farklı pencereler, 4 yıldan
  uzun süren öncüller (plasebo penceresine taşar), Ş1'in attığı öncü dizili olaylar ve Marmara hakkında bilgi yoktur.
  TR-11 Ö3 kuralı geçerlidir. H0 değildir.

## 11. Yeniden açma şartı

(a) Aktif kuşakta ölçülmüş taban (TR-11 sınıf A/B ≥ 30 yer). (b) K_p'yi iki katına çıkaran açık GNSS arşivi (ör. GEONET
F5 doğrudan). (c) Yönlü ölçü (TR-1 §9 (a)). (d) "VAR" çıkarsa: aktif bölge tabanı ve bilinen yavaş kayma kataloğuyla
ayrı ön kayıt. Her biri yeni ön kayıt ister.

## 12. INCELEME-1 eşleme

| Madde | Nerede |
|---|---|
| Z1 liste ve sha256 | §7, §8.1 |
| Z2 dal kuralı aşama 0'dan önce | §0, §7 (bu metin aşama 0'dan önce commit edildi) |
| Z3 eşli sınama ana hüküm | §2, §3, §5 |
| Z4 yapay yanlış alarm, > 0,07 geçersiz | §8.2, Ek 1 |
| Z5 c0 bilgi satırı, ū birimi, w0 ≥ 2008, "c_gerçek ≤ c0 varsayımı altında" | §4, §6.2 |
| Z6 c0 = 1 cümlesi kaldırıldı | §8.6 |
| Ö1 hesap sırası | §8 |
| Ö2 sabit bilgi tablosu | §6 |
| Ö3 literatür olayları | §6.5, aşama 0 |

## 13. Körlük ve İstanbul

Bu sürüm için hiçbir tenv3 indirilmedi ya da açılmadı; gerçek S hesaplanmadı. Aşama 0 yalnız üstveri okur. Marmara
kutusunun 2017+ GNSS'i ve bütün 2026 verisi kördür. Sonuç bir olasılık terimi üretmez; İstanbul için mutlak olasılık
yazılmaz.

## Ek 1: Z4 yapay yanlış alarm ve MDE (16 Kasım 2026, hiçbir gerçek seri açılmadan)

Betik `kayit/turetme/tr1b/tr1b_v2_z4.py` → `tr1b_v2_z4.json` (tohum 20261122; sıfır havuzu 6000 küme, sinyal 2000,
4000 çekiliş; ≈ 13 dk). Model: 2556 günlük günlük seri (plasebo w0_p'den olay w1'e), önünde 2000 günlük ısınma, iki
yatay bileşen; beyaz 1,5 mm + kırpışma (TR-11 `h_katsayi` süzgeci); TR-11 `tasarim` ile menteşe katsayısı; TR-11
`S_hesapla`; n_y TR-11 katman sayılarıyla 3–8, n_r = 8; küme ölçeği exp(0,4 Z) iki pencerede ortak. İki pencere
1096 günü paylaşır. MAD ayıklaması ve kod 1 yok.

**Sinyalsiz yanlış alarm (p ≤ 0,05 ve LOO p ≤ 0,10):**

| Gürültü | K_p 6 | 8 | 10 | 12 | ort. d (sd) |
|---|---|---|---|---|---|
| N0: kırpışma 4,6 | 0,051 | 0,049 | 0,047 | 0,057 | +0,005 (0,40) |
| kırpışma 3,0 | 0,053 | 0,058 | 0,050 | 0,047 | +0,002 (0,40) |
| N1: + rastgele yürüyüş 1 mm/yıl^0,5 | 0,054 | 0,051 | 0,050 | 0,050 | −0,004 (0,41) |
| BOLGE2: bütün gürültü × 2 (iki pencerede) | 0,041 | 0,045 | 0,048 | 0,055 | −0,004 (0,40) |
| ARTAN: son 2 yılda gürültü × 1,5 (karıştırıcı; kapıya girmez) | 0,27 | 0,35 | 0,45 | 0,51 | +0,20 (0,40) |

- **Z4 kapısı (≤ 0,07) geçildi:** en büyük değer 0,058 (Monte Carlo hatası ≈ ±0,004). Paylaşılan parça ve renkli
  gürültü işaret çevirmenin geçerliğini bozmuyor.
- **Uyarı (koşu öncesi düzeltme):** ısınmasız ilk denemede (kırpışma pencerenin başında başlatılmış) ort. d +0,014 ve
  K_p = 10'da yanlış alarm 0,072 çıktı: yapay süreç pencerede durağan değildi. Gerçek istasyonların gürültüsü pencereden
  önce başlamıştır; ısınma bu yüzden doğru modeldir. Ama gerçek seride gürültünün dönemle değişmesi (ARTAN satırı)
  aynı yönde ve çok daha büyük bir etki yapar. Bu, ölçülemeyen, "VAR" yönlü tek karıştırıcıdır (§9.2).
- LOO şartı yapayda hiçbir yanlış alarmı kesmedi (p ≤ 0,05 olan her durumda LOO da geçti).

**Güç (uyumlu / dağınık; hüküm kuralı):** MDE tablosu §5'te. Güç eğrileri `tr1b_v2_z4.json` içinde.
