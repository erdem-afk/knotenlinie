# TR-2 hedef sayımı ve tasarım (kör): sonraki M≥6 sessiz tarafta mı?

Tarih: 11 Kasım 2026. Durum: SAYIM (ön kayıt değil). İsabet hesaplanmadı, sonraki olayın hangi tarafta olduğu hiçbir
kodda hesaplanmadı ve hiçbir çıktıya yazılmadı.
Kaynak: `research_notes/Fayın anlık durumu gözlem boşlukları/nisan_2025_marmara.md` (NA-2), defter satırı TR-2.
Kod: `kayit/turetme/tr2/tr2_sayim.py`. Özet çıktı: `kayit/turetme/tr2/tr2_sayim_ozet.json`.
Ham kataloglar ve satır düzeyi çıktı depoda değil, scratch'te (`.../scratchpad/tr2/`).

## 0. Hüküm

| Ölçüt | Değer | Kapı |
|---|---|---|
| Bağımsız küme sayısı K | **40** | K ≥ 30: geçer |
| Ölçülebilir en küçük isabet oranı (güç 0,80, tek yanlı α 0,05) | **0,699** | ≤ 0,70: geçer (0,001 payla) |
| **Güç kapısı** | | **GEÇER, sınırda** |

Kapı yalnız ana tanımla geçiyor. Altı tanım varyantının üçünde kapı kapanıyor (§4). Gerçek etki 0,65 ise güç 0,57.
ETAS'a karşı fark daha küçük olacağından o karşılaştırmanın gücü bundan da düşük olur. Öneri: ana tanımı bu belgeyle
dondur, varyant arama. Sınavı yalnız "%50'ye karşı büyük etki var mı" sorusu için koş. Küçük bir etkinin yokluğunu
bu sınav kanıtlayamaz.

## 1. Tanımlar (kodlanabilir, `tr2_sayim.py` sabitleri)

Bütün ComCat sorguları `endtime ≤ 2025-12-31T23:59:59` (kodda assert). 2026 hiçbir amaçla sorgulanmaz.

**Birincil olay.**
- Kaynak: USGS ComCat, olay zamanı 1976-01-01 ile 2025-12-31 arası.
- Büyüklük: 6,0 ≤ M ≤ 7,2 ve büyüklük türü `mw*` (Mww, Mwc, Mwb, Mwr, Mw). Ms ya da mb olanlar dışarıda (154 olay).
- Derinlik ≤ 25 km (ComCat tercihli derinlik).
- Mekanizma: ComCat `moment-tensor` ürünü, yoksa `focal-mechanism` ürünü. İkisi de varsa en yüksek
  `preferredWeight` alınır. Düğüm düzlemi alanları yoksa düzlemler tensör bileşenlerinden türetilir (8 olay).
  - 1976–1989 olaylarında mekanizma yalnız `focal-mechanism` ürünündedir. İki aday sorgusu birleştirilir.
- Doğrultu atımlı: iki düğüm düzleminden en az biri için |rake| ≤ 30° ya da |rake| ≥ 150°.
- Kırık boyu L (km): Wells ve Coppersmith 1994, doğrultu atımlı yeraltı boyu, log10 L = 0,62 Mw − 2,57.
  Örnek: Mw 6,0 için 14 km, Mw 7,2 için 78 km.

**Artçı bulutu.**
- Zaman: birincilden sonraki (t0, t0 + 30 gün].
- Uzaklık: dış merkezden ≤ 3 L.
- Büyüklük: M ≥ 4,0, herhangi bir büyüklük türü. Birincilin büyüklüğüne eşit ya da büyük olaylar artçı sayılmaz.

**Fay doğrultusu.**
- Artçı dış merkezlerinin yerel düzlemdeki kovaryansından ana eksen azimutu bulunur (PCA, 180° kipinde).
- Koşul: en az 5 artçı ve λ1/λ2 ≥ 2.
- İki düğüm düzleminden doğrultusu ana eksene açısal olarak daha yakın olan seçilir.
- Koşul sağlanmazsa doğrultu "belirsiz" sayılır ve olay sınava girmez.
  - Az artçı (n < 5): 884 olay.
  - Uzanım yetersiz (λ1/λ2 < 2): 87 olay.

**Sessiz taraf ve asimetri.**
- s: artçının doğrultu boyunca dış merkeze göre konumu (büyük çember mesafesi × cos(azimut − doğrultu)).
- |s| < 5 km olan artçılar tarafsız sayılır (konum hatası payı).
- n+ ve n−: iki yandaki artçı sayıları. Asimetri A = (n+ − n−)/(n+ + n−).
- Asimetri ölçülebilir: n+ + n− ≥ 10 ve |A| ≥ 1/3 (2:1 oranı).
- Sessiz taraf, artçı sayısı az olan taraftır. A = 0 olamaz, çünkü |A| ≥ 1/3 koşulu bunu dışlar.

**Sonraki olay.**
- Havuz: ComCat, M ≥ 6,0, derinlik ≤ 40 km, büyüklük türü serbest, mekanizma koşulu yok.
- Zaman: [t0 + 30 gün, min(t0 + 15 yıl, 2025-12-31)].
- Konum: doğrultu boyunca 0,5 L ≤ |s| ≤ 5 L ve doğrultuya dik |d| ≤ max(L, 30 km).
- Birden çok aday varsa zamanca **ilki** sınanır.

**İsabet.** İlk sonraki olayın s işareti sessiz tarafın işaretine eşitse isabet sayılır. Bu adım bu belgede KODLANMADI.

**Bağımsızlık.**
- Tüm doğrultu atımlı birinciller, 300 km ve 365,25 gün eşikleriyle tek bağlantılı kümelere ayrılır.
- Sınav birimi küme. Her kümeden, nitelikli (asimetrisi ölçülebilir ve sonraki olayı olan) birinciller içinde zamanca ilki alınır.

**Türkiye.** Kaba kutu: enlem 35,8–42,2° K, boylam 25,5–44,8° D. Komşu ülkelerden kenar olaylar da kutuya girebilir.

## 2. Sayım (ComCat, 11 Kasım 2026, bitiş 2025-12-31)

| Aşama | Dünya | Türkiye kutusu |
|---|---|---|
| Aday (M 6,0–7,2, ≤25 km, mekanizma ürünü olan) | 2953 | — |
| Birincil (Mw, doğrultu atımlı) | **1340** | 15 |
| Doğrultusu seçilebilen | 369 | 8 |
| Asimetrisi ölçülebilen (n ≥ 10, \|A\| ≥ 1/3) | **116** | 2 |
| Sonraki olay adayı olan (doğrultusu seçilebilenler içinde; taraf bakılmadı) | **153** | 2 |
| Nitelikli: asimetri ölçülebilir ve sonraki olay var | 49 | 1 |
| **Bağımsız küme K** (nitelikli) | **40** | **1** (1999 Düzce Mw 7,2) |
| Tüm birincillerin küme sayısı | 988 | — |

Ek ayrıntılar:
- Türkiye payı: K'nin 1/40'ı. 2025 Marmara Mw 6,2 (us7000pufs) doğrultusu seçilebilen olaylar arasında. Ancak
  ComCat M ≥ 4 ile yalnız 6 yanlı artçısı var, bu yüzden asimetrisi ölçülemiyor. Gerekçe olayı sınavın içinde değil.
  Sızıntı açısından iyi, aktarılabilirlik açısından zayıf.
- Kümelerin boyutu: 35 tekil, 3 çift, 1 üçlü, 1 beşli.
- Nitelikli birincillerin 19'unun takip süresi 15 yıldan kısa (2011 sonrası olaylar).
- Sonraki olay aday sayısı:
  - 13 birincilde 1, 14'ünde 2 aday.
  - 22'sinde ≥ 3 aday, en çok 17 aday. Bunlar yalın dizilerdir.
- 12 nitelikli birincilde seçilen düğüm düzlemi ile artçı ana ekseni arasındaki açı 30°'den büyük. Tüm doğrultulu
  olaylarda medyan 15°.
- On yıllara göre nitelikli birinciller: 1980'ler 5, 1990'lar 3, 2000'ler 20, 2010'lar 20, 2020'ler 1. Pencere
  2000 sonrasına yığılıyor, çünkü M ≥ 4 küresel tamlığı o dönemde daha iyi.

|A| dağılımı (yalnız mutlak değer; doğrultusu seçilebilen ve n+ + n− ≥ 10 olan 189 olay):

| \|A\| | [0, 0,10) | [0,10, 0,20) | [0,20, 0,33) | [0,33, 0,50) | [0,50, 0,75) | [0,75, 1] |
|---|---|---|---|---|---|---|
| Olay | 25 | 16 | 32 | 22 | 53 | 41 |

Çeyrekler (%10/25/50/75/90): 0,08 / 0,20 / 0,50 / 0,71 / 0,89. Asimetri sık görülüyor; yarısında |A| ≥ 0,5.
Bunun bir bölümü dış merkezin kırık ucunda olmasından (tek yönlü kırılma) kaynaklanıyor olabilir. Sessiz taraf bu
durumda çoğu zaman "kırığın başladığı taraf" olur (bkz. risk 3).

## 3. Güç (kesin binom, tek yanlı α 0,05, H0 p = 0,5)

| K | Kritik isabet | Güç p=0,60 | p=0,65 | p=0,70 | En küçük ölçülebilir p (güç 0,80) |
|---|---|---|---|---|---|
| 29 | 20 | 0,22 | 0,41 | 0,64 | 0,741 |
| 31 | 21 | 0,25 | 0,46 | 0,69 | 0,728 |
| **40 (ana)** | **26** | **0,32** | **0,57** | **0,81** | **0,699** |
| 47 | 30 | 0,35 | 0,63 | 0,86 | 0,685 |
| 55 | 35 | 0,34 | 0,64 | 0,88 | 0,680 |

Defterdeki kaba varsayım "N 60–120, z ≈ 2,7" iyimserdi. Gerçek bağımsız N 40.

## 4. Tanım duyarlılığı (yalnız sayılar; hangi varyantın seçileceği isabetten bağımsız)

| Varyant | Birincil | Doğrultulu | Asim. ölçülür | Sonraki var | Nitelikli | K | K_TR | En küçük p | Kapı |
|---|---|---|---|---|---|---|---|---|---|
| Ana | 1340 | 369 | 116 | 153 | 49 | 40 | 1 | 0,699 | geçer |
| PCA λ1/λ2 ≥ 1,5 | 1340 | 426 | 138 | 176 | 58 | 47 | 1 | 0,685 | geçer |
| \|A\| ≥ 0,2 | 1340 | 369 | 148 | 153 | 66 | 55 | 2 | 0,680 | geçer |
| n+ + n− ≥ 8 | 1340 | 369 | 135 | 153 | 55 | 44 | 1 | 0,684 | geçer |
| Büyük olayın gölgesindeki birincil dışarıda (1 yıl, 3 L_büyük) | 1125 | 270 | 77 | 106 | 30 | 29 | 0 | 0,741 | **geçmez** |
| Dik mesafe ≤ 1 L (30 km tabanı yok) | 1340 | 369 | 116 | 146 | 47 | 39 | 1 | 0,715 | **geçmez** |
| Artçı M ≥ 4,5 | 1340 | 272 | 70 | 115 | 40 | 31 | 0 | 0,728 | **geçmez** |
| Ek: tek bağlantılı binom p ≤ 0,05 ile asimetri | — | — | — | — | — | 34 | — | 0,726 | geçmez |

Varyantların yorumu:
- K'yi büyüten varyantlar (eşiği düşürmek) etkiyi de seyreltir. |A| 0,2 olan bir olayda "sessiz taraf" zayıf bir sinyaldir.
- Fiziksel olarak en savunulur varyant ("başka bir ana şokun artçısı olan birincili at") kapıyı kapatıyor.
- Hangi varyantın kullanılacağı ön kayıt dondurulmadan önce seçilmeli. Bu sayımlar taraf bilgisi taşımadığı için
  seçim körlüğü bozmaz. Yine de seçim K'yi kapının üstüne çıkarmak için yapılmamalı.

## 5. Rakip: "artçı yoğun taraf" (ETAS) nasıl girer

İkili sonuçta "sessiz taraf" ile "yoğun taraf" tümleyendir. %50'ye karşı tek yanlı sınav ETAS yönünü otomatik olarak
H0'ın içine koyar. Gözlenen oran 0,5'in altında kalırsa bu ETAS lehine okunur, ama sınav ETAS'ı ayrı puanlamaz. Öneri,
üç modelli Bernoulli log skoru (nat), birim küme:

1. **Taban:** p = 0,5.
2. **Boşluk (sessiz komşu) modeli:** P(isabet) = q. q ön kayıtta sabitlenir. Öneri: q = 0,65. Alternatif:
   q = 0,5 + 0,25·|A|. Hangisi seçilecekse önceden dondurulur.
3. **ETAS:** her küme için p_i = λ_sessiz / (λ_sessiz + λ_yoğun).
   - λ: birincil ve 30 günlük artçılarının, iki taraftaki hedef kutusuna (0,5–5 L, |d| ≤ max(L, 30 km)) 30 gün–15
     yıl penceresinde verdiği M ≥ 6 beklenen tetikleme oranı.
   - Çekirdek: izotropik kuvvet yasası (Zhuang–Ogata tipi), parametreleri yayımlanmış küresel bir ETAS'tan.
   - Öneri: parametreler 1976–1999 küresel ComCat'e uydurulup dondurulur. Yalnız 2000 sonrası kümeler puanlanır.
     Ya da yayımlanmış bir küresel ETAS parametre seti doğrudan kullanılır.
   - Arka plan oranı simetrik alınır (iki kutuda eşit). ETAS'ın tek bilgisi artçı konumlarıdır.

Hüküm satırları (küme bootstrap'i, 10 000 yineleme):
- Boşluk − taban.
- ETAS − taban.
- Boşluk − ETAS (eşleştirilmiş fark).

Güç notları:
- K = 40 ile boşluk − taban için beklenen kazanç kabaca 40·[0,65·ln(1,3) + 0,35·ln(0,7)] ≈ 40·0,046 ≈ 1,8 nat.
  Ölçüm gürültüsü bunun aynı mertebesinde.
- ETAS p_i'leri büyük olasılıkla 0,5'e yakın çıkar: hedef kutuları 0,5–5 L uzakta, çekirdek orada sönmüş durumda.
  Bu nedenle boşluk − ETAS farkı, boşluk − taban farkından daha zor ayrışır.
- ETAS çekirdeğinin p_i'leri sonuç görülmeden, ön kayıtta tüm kümeler için hesaplanıp yayımlanmalı (sızıntı kapısı).

## 6. Defterle örtüşme (`kayit.py ara`: koşullu, yön, Nisan, artçı, DK-3, S-1)

- **DK-3 (kapandı, H0).** Sorusu: M6 sonrası M7'nin oranı. Sonuç GR-ETAS ile tutarlı. TR-2 sonraki olayın var
  olmasına koşulludur. Oranı sınamaz, yalnız iki taraf arasındaki paylaşımı sınar. Çakışma yok.
  - Örtük bağ: DK-3, ETAS'ın oranı doğru verdiğini gösterdi. ETAS'ın uzamsal yönünün doğru olduğunu göstermedi.
    TR-2'nin ETAS satırı bu boşluğu doldurur.
  - TR-2'nin sonraki olayı M ≥ 6'dır, M7 değil. DK-3'ün hedefiyle karıştırılmamalı.
- **S-1 (ayırt edilemez).** Konusu, tek kırığın geçitleri sıçrayıp sıçramadığı (kosismik). TR-2'nin konusu ise
  olaylar arası, 30 gün–15 yıl.
  - Bağ: sonraki olayların bir kısmı geçit ötesindeki segmentte olacaktır (0,5–5 L).
  - S-1'in bilgi bulgusu "kırılmalar BW kurallarından çok daha sık geçiyor" idi. Bu, sessiz tarafın bir geçitle
    ayrılmış olmasının sonraki olayı engellemediğini düşündürür. Sınav tasarımını değiştirmez.
  - Geçit bilgisi TR-2'ye eklenmemeli. Açık kırık izi küresel olarak yok (S-1 dersi).
- **TK-E5 (elendi).** Konusu Marmara içi doğuya göç, 1–5 olay, geriye dönük. TR-2 bunun küresel, çok olaylı ve ön
  kayıtlı karşılığıdır. TK-E5'in eleme gerekçesi (N yok) burada K = 40 ile karşılanıyor.
- **TR-9 (bekle).** Konusu Marmara'da artçı cephesi ile kilitlenme sınırı. TR-2'nin Marmara'ya köprüsü, ama ayrı soru.
- **VE-2 (aday).** Konusu ΔCFS ile segment sıralaması. Doğrultu atımlıda statik ΔCFS iki uçta da pozitiftir. Bu
  nedenle ΔCFS tarafı ayırt etmez ve TR-2'ye rakip olamaz.
- Defterde başka bir "yön" adayı yok (DY-1..5 farklı konular).

## 7. En büyük üç risk

1. **Güç kırılgan.** Ana tanım kapıyı 0,001 payla geçiyor. Üç makul varyant kapıyı kapatıyor. Etki 0,60–0,65
   ise sınav büyük olasılıkla "ayırt edilemez" verir. Bu sonuç bir H0 kanıtı sayılmamalı.
2. **"Aynı fay" yalnız geometrik vekil.**
   - Sonraki olayın mekanizması sınanmıyor. Nitelikli birincillerin 22'sinde ≥ 3 aday var. Bunlar dalma-batma
     kenarlarındaki ya da yoğun dizilerdeki başka faylara ait olabilir.
   - Birincillerin bir kısmı daha büyük bir ana şokun artçısı (örneğin 1999 Düzce, İzmit'in gölgesinde). Bu
     birinciller dışarıda bırakılınca K 29'a düşüyor.
   - 12 nitelikli birincilde düğüm düzlemi seçimi zayıf (artçı ekseninden > 30° sapma).
3. **Asimetrinin kaynağı fizik değil, örnekleme olabilir.**
   - Küresel ComCat M ≥ 4 tamlığı ağ geometrisine bağlı. Örneğin deniz tarafı ve kıyı tarafı ağlar arasında fark var.
   - Dış merkez kırığın başlangıç ucundadır. Tek yönlü kırılmada artçılar ilerleme yönünde yoğunlaşır, bu da sessiz
     tarafı "kırığın arkası" yapar.
   - Dolayısıyla sınav "boşluk" hipotezinden çok "sonraki olay kırılma yönünün tersinde mi" sorusunu sınayabilir.
   - Öneri: ön kayıtta |A| ile birlikte dış merkezin artçı bulutu merkezine uzaklığı da bir ortak değişken olarak
     dondurulsun. Merkez olarak artçı centroidi kullanan ikinci bir tanım bilgi satırı olarak eklensin.
   - Marmara 2025 olayı ComCat M ≥ 4 ile ölçülemiyor. Gerekçedeki "Avcılar sessiz" gözlemi düşük Mc'li yerel
     kataloglara dayanıyor. Küresel sınav bu ölçek farkını taşımaz.

## 8. Körlük beyanı

- Sorgular: aday listesi (`moment-tensor` ve `focal-mechanism`), olay ayrıntıları, M ≥ 6 havuzu ve 1340 artçı
  sorgusu. Hepsinin bitişi ≤ 2025-12-31 ve kod bunu assert eder.
- Bir olay ayrıntısı ComCat'te 409 döndürdü (us20008uzn, 2017 Aleut). "Mekanizma yok" sayıldı.
- Sonraki olay için yalnız |s| ve |d| hesaplanır (`mutlak_eksen`). İşaret o fonksiyonun dışına çıkmaz.
- Artçı sayımında n+ ve n− yerel değişkenlerdir ve yalnız |A| ile simetrik binom p yazılır. Sonraki olayın tarafı
  ile asimetrinin işareti hiçbir yerde karşılaştırılmadı.
- Satır düzeyi çıktı (scratch) olay başına |A|, aday sayısı ve var/yok içerir. Taraf içermez.
