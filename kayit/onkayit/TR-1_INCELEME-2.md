# TR-1 ön kayıt: bağımsız inceleme 2 (sürüm 2)

İncelenen: `TR-1_kuresel-gnss-hiz-degisimi_ONKAYIT.md`, sürüm 2 (11 Kasım 2026). Hiçbir tenv3 serisi indirilmedi ya da
işlenmedi. S, Δv ya da r hesaplanmadı. Sayım yalnız üstveriyle yapıldı: NGL `DataHoldings.txt` ve `steps.txt`, ComCat
katalogları, USGS moment tensörleri. Betik: `kayit/turetme/tr1/sayim_ustveri.py`. Ham dosyalar depo dışında.

## Hüküm

**Metin: DÜZELT-SONRA-KABUL.** Aşağıdaki 1–8. düzeltmelerden sonra dondurulabilir. Tasarım bulgularının hiçbiri
sürüm 1'deki kadar ağır değil. Yalnız bulgu 2 (pozitif kontrol) düzeltilmezse ölçü otomatik olarak "kör" çıkar.

**Uygulanabilirlik: K < 20.** Sürüm 2 kurallarıyla, üstveriden elde edilen üst sınır K = 11–12. Doluluk şartı
DataHoldings oranıyla yaklaşık uygulanırsa K = 9. Plaseboyu hesaplanabilen olay sayısı 3 (≥ 10 gerekiyor).
Ön kayıt bu hâliyle dondurulup koşulursa sonuç önceden belli: **"güç yok"**. H1 ise plasebo şartı yüzünden zaten
ilan edilemez. Önerim şu: indirme yapılmasın; bu sayım "güç yok (üstveriyle, koşudan önce)" olarak kayda geçsin ve
bölüm 9'a geçilsin. Bulgu 9 bunun gerekçesini ve uyarısını veriyor.

## A. Üstveri sayımı (sürüm 2 kuralları)

Uygulanan kurallar: T ≤ 2023-12-31; pencere ve menteşe; 2. uygunluk kuralı (eşik/4, 8 yıl); sıçrama ±30 gün ve kenar
30 gün kuralı; Marmara kutusu; halka M'ye göre; (a)–(e); SHA sırası; ≥ 5 kontrol; plasebo T − 5 yıl ile
[T − 13 yıl, T − 7 gün] arasında sükûnet. Yıllar tam güne aşağı yuvarlandı (5 yıl = 1826 g). Durum aralığı (Dtbeg–Dtend)
pencereyi kapsamalı. Plaseboda "hesaplanabilir" = plasebo kümesi geçerli ve ≥ 5 plasebo kontrolü var.

| Kural seti | Geçerli olay kümesi | ≥ 5 kontrol | K: yalnız (i), üst | K: (i)+(ii), alt | Plasebosu hesaplanabilen olay |
|---|---|---|---|---|---|
| Sürüm 2, doluluk atlandı (üst sınır) | 27 | **15** | **12** | **11** | **3** |
| Sürüm 2, doluluk ≈ NumSol / gün aralığı ≥ 0,6 | 23 | 11 | 9 | 9 | 1 |
| Tanı: (b) yalnız [T, T + 2 yıl] | 27 | 19 | 15 | 14 | 4 |
| Tanı: 2. kural ve sıçrama kuralı tümüyle kapalı | 65 | 50 | 31 | 19 | 12 (10 küme) |

- **Bölge dağılımı (sürüm 2, 15 olay):** Japonya 0, Şili 0, öteki 15. Bu 15 olay: Kaliforniya/Meksika/Idaho 3,
  Yunanistan 3, Tayvan 3, Nepal 2, Yeni Zelanda 1, Hawaii 1, Alaska 1, Endonezya 1.
- **Japonya:** 7 Japon olayının kümesi geçerli, ama hiçbirinde ≥ 5 kontrol yok. (c)'nin gevşetilmesi bunu değiştirmedi;
  kısıtlayan (a)/(d) ile (b).
- **Doğrultu atımlı (USGS MT, |rake| ≤ 30° ya da ≥ 150°):** 15 olaydan 8'i (El Mayor-Cucapah, Darfield, Lefkada,
  Zakynthos, Ridgecrest, Stanley, Tayvan 2022'nin ikisi). M ≥ 7,5 olan olay 1 (Nepal 2015).
- **Kontrol havuzu:** 114 kontrol yuvası yalnız 33 benzersiz merkezden dolduruluyor. Bir merkez 11 olayda kontrol.
  Kontrollerin 41'i Japonya'da; ötekiler ağırlıkla Alaska, Kaliforniya, Yeni Zelanda, İzlanda (7) ve Nevada.
- **Sonuç: K < 20.** Bütün basamak kuralları kaldırılsa bile K 19–31 aralığında kalıyor ve bu durumda sürüm 1'in
  postsismik kirlenmesi geri geliyor.

Sınırlar: Doluluk atlanınca sayılar üst sınırdır. DataHoldings oranı yalnız bütün seri için ortalama bir doluluktur.
"Deprem yok" şartları için 1985–1999 kataloğu da kullanıldı (bkz. bulgu 6). Kosismik kurallar steps.txt'teki uzaklık
sütunuyla uygulandı.

## B. Bulgular (önem sırasıyla)

### 1. Kontrol (b) şartı olaylara uygulanmayan bir geçmiş sükûneti şartı koyuyor

- **Sorun:** Kontrol merkezinin 100 km içinde [T − 8 yıl, T] aralığında M ≥ 6,5 olay olmaması isteniyor. Olay için böyle
  bir şart yok: olay merkezinin yakınında 8 yıl içinde başka bir M ≥ 6,5 olabilir. 2. kural yalnız eşik/4 içindeki
  istasyonları eler; M6,5 için bu ≈ 72 km. Daha uzaktaki istasyonlarda önceki depremin postsismik eğriliği olay
  tarafında kalır, kontrol tarafında kalmaz.
- **Neden önemli:** Sürüm 1'deki yanlılık daha küçük ölçekte geri geliyor ve yönü yine r > 0,5. Ayrıca kontrol bulmayı
  da zorlaştırıyor: geçmiş şartı kaldırılınca ≥ 5 kontrollü olay sayısı 15'ten 19'a çıkıyor.
- **Düzeltme (metin):** "(b) merkezin 100 km içinde, [T − 7 gün, T + 2 yıl] aralığında M≥6,5, derinlik ≤70 km olay yok.
  Geçmiş depremlerin etkisi olay ve kontrolde yalnız 2. uygunluk kuralıyla, aynı biçimde elenir."

### 2. Pozitif kontrol metni kendi kendini boşa çıkarıyor

- **Sorun:** "Kontrol kümelerinin yakın istasyon serilerine ... eklenir; ... sahte olay ortalaması raporlanır." Sinyal
  bütün kontrollere eklenirse sahte olay da, karşılaştırıldığı kontroller de aynı sinyali taşır ve r ≈ 0,5 kalır.
- **Neden önemli:** 3 mm/yıl'da ortalama < 0,75 çıkar, ölçü "kör" sayılır ve hüküm otomatik olarak "güç yok" olur.
  Otomatik koşu düzeninde bu ölümcül.
- **Düzeltme (metin):** "Sinyal yalnız sahte olayın (SHA sırasındaki ilk kontrolün) yakın istasyonlarına eklenir. Kalan
  kontroller ve bütün referans istasyonlar değişmez. Sahte olay kalan kontrollere karşı puanlanır."

### 3. Plasebo denetimi gücü düşük ve tek yanlı; ana örneklemden farklı bir alt kümeyi ölçüyor

- **Sorun a:** Durdurma şartı "plasebo alt sınırı > 0,5". ≥ 10 kümede SE ≈ 0,1, yani ancak ≈ 0,17'den büyük bir bölge
  yanlılığı yakalanır. Örneğin 0,08'lik bir yanlılık geçer ve r̄'yi H1 eşiğinin üstüne taşıyabilir.
- **Sorun b:** Plaseboya giriş şartı [T − 13 yıl, T − 7 gün] boyunca sükûnet. Bu, ana örneklemin sakin bir alt kümesini
  seçer (sayımda 15 olaydan 3'ü). Plasebo, H1'in hesaplandığı olaylardaki yanlılığı ölçmez.
- **Düzeltme (metin):** "Plaseboyla eşleşen kümelerde fark d = r_olay − r_plasebo hesaplanır. H1 için hem r̄ alt sınırı
  > 0,5 hem d̄'nin tek yanlı %95 alt sınırı > 0 gerekir. Plasebo sükûnet şartı (b) ile aynı tutulur:
  [T' − 7 gün, T' + 2 yıl] = [T − 5 yıl − 7 gün, T − 3 yıl]. Ayrıca T' ile T − 7 gün arasında merkezin 100 km içinde
  M≥6,5 olmamalı; bu, plasebonun ardından olay dışında bir deprem gelmesini engeller."

### 4. Kontrol havuzu dar; kümeler arası bağımlılık modellenmiyor

- **Sorun:** Sayımda 114 kontrol yuvası 33 merkezden dolduruluyor; bir merkez 11 olayda kullanılıyor. Aynı kontrol
  istasyonları farklı bağımsızlık kümelerinin r'lerine ortak giriyor. t aralığı küme puanlarını bağımsız sayar,
  dolayısıyla güven aralığı olduğundan dar çıkar.
- **Düzeltme (metin):** "Bir kontrol merkezi en çok 3 bağımsızlık kümesinde kullanılır. Olaylar zaman sırasıyla işlenir;
  kotası dolmuş merkez SHA sırasında atlanır. Bilgi satırı olarak 'bir kontrol merkezini dışarıda bırak' r̄ aralığı
  (en küçük ve en büyük) raporlanır."

### 5. n_y/n_r eşitlemesi sayıyı eşitliyor, geometriyi eşitlemiyor

- **Sorun:** Olay merkezleri çoğunlukla açık deniz ya da seyrek ağdır; yakın istasyonlar 40–100 km'dedir. Kontroller
  yoğun ağlardadır (Japonya, Kaliforniya); en yakın n_y istasyon birkaç km içinde ve birbiriyle yüksek korelasyonludur.
  Korelasyonlu istasyonların medyanı daha az ortalama alır, S'nin dağılımı farklılaşır. Yanlılığın yönü belirsizdir.
  Ayrıca kontrol merkezleri İzlanda (volkanik) ve Tohoku sonrası Japonya'da (postsismik) yoğunlaşıyor. Bu iki bölge
  kontrol S'sini büyütür, yani yanlılık H0 yönündedir.
- **Düzeltme (metin):** "Kontrolde yakın istasyonlar, her biri olayın yakın istasyonlarının uzaklık sırasına en yakın
  uzaklıkta olacak biçimde seçilir (olayın k. yakın istasyonu d_k km'deyse kontrolde d_k'ye en yakın, henüz seçilmemiş
  uygun istasyon). Bilgi satırı: olay ve kontrollerde yakın istasyon uzaklıklarının medyanı, kontrol bölgelerinin
  sayımı." Daha sade bir seçenek: bu satır yalnız bilgi olarak eklenir ve sınırlar bölümüne yanlılık yönü belirsiz diye
  yazılır.

### 6. "Deprem yok" kataloğu yanlış aralıkta

- **Sorun:** İkinci sorgu "aynı tarih aralığı" (2000'den başlıyor). Oysa (b) T − 8 yıla, plasebo T − 13 yıla, 2. kural
  T − 8 yıla kadar geri bakar. T = 2000 için bu 1987'ye iner. 2000 öncesi depremler görünmez; erken olaylarda şart
  gevşek kalır.
- **Düzeltme (metin):** "'Deprem yok' sorgusu: `starttime=1985-01-01`, `endtime=2026-01-01T00:00:00`, `minmagnitude=6.5`,
  `maxdepth=70`."

### 7. Kalan tek anlamsızlıklar

1. Yıllar tam gün değil (5 yıl = 1826,25 g; 2 yıl = 730,5 g; 13 yıl = 4748,25 g). Metin: "Her yıl aralığı
   floor(n × 365,25) gün."
2. (e) 150 km < 2 × 100 km olduğu için iki kontrolün yakın kümeleri ortak istasyon paylaşabilir. Metin: "≥ 200 km ve
   seçilen kontrollerin yakın ya da referans kümeleri ortak istasyon içermez."
3. (d) ile (a) birlikte M ≥ 7,5'te merkezi fiilen ≥ 1600 km'ye iter. Bu tutarlı, ama (a) gereksizleşiyor; metinde
   "(d) belirleyicidir" diye yazılsın.
4. Kontrol adaylarına giren olaylar: "ÖTEKİ olaylar" T > 2023 olanları ve olayla aynı diziden olanları da kapsar mı?
   Metin: "Aday havuzu 2000–2025 arası, derinlik ≤ 30 km olan bütün M ≥ 6,5 olaylardır (T > 2023 dahil), olayın
   kendisi hariç."
5. Negatif kontrolde sahte olayın n_kontrol değeri 4–9 arası; 5 kontrollü bir olayda sahte olay 4 kontrole karşı
   puanlanır. Bunun kabul edildiği yazılsın; "en az 4" diye açıkça.
6. Güç kapısı sd'si 0,32 sabit (10 kontrol varsayımı). Sayımda kontrollerin yarısı 5–6 kontrollü; sd ≈ 0,34. Metin:
   "sd = √((n̄+2)/(12 n̄)), n̄ = olayların kontrol sayısı ortalaması."
7. K sayımı için olay istasyonlarının doluluğu bilinmeli; bu da olay penceresi dosyalarını indirmeyi gerektirir. Metin:
   "K sayımında olay dosyalarından yalnız MJD sütunu okunur; konum sütunları ayrıştırılmaz."
8. Rake ölçütü: "düğüm düzlemlerinden biri için" (Stanley 2020 gibi eğik olayları içeri alır). Bilgi satırı olduğu için
   kabul edilebilir.

### 8. Metin ile örneklem çelişiyor

- **Sorun:** Bölüm 4 H0 anlamı "ağırlıkla Japonya ve Şili, dalma-batma" diyor. Bölüm 7 "doğrultu atımlı alt küme
  ≤ 18" diyor. Sürüm 2 kurallarıyla örneklemde Japonya ve Şili yok; 15 olayın 8'i doğrultu atımlı, örneklem ağırlıkla
  kıtasal ve sınır-dönüşüm.
- **Düzeltme (metin):** "Örneklem bileşimi (bölge, mekanizma, M) K sayımıyla birlikte otomatik yazılır ve H0'ın anlamı o
  bileşimle ifade edilir." Ön kayıttaki sabit bölge ifadesi silinsin.

### 9. Sayımın sonucu ve çatallanma riski

- **Durum:** K = 11–12 (üst sınır), plasebo 3 olay. Kurallar ne kadar gevşetilirse gevşetilsin, K ancak bütün basamak
  kuralları kaldırılınca 19–31'e çıkıyor ve bu da sürüm 1'in reddedildiği kirlenmeyi geri getiriyor. Plasebo hiçbir
  savunulabilir ayarda ≥ 10 kümeye ulaşmıyor; yani bu tasarımda H1 yapısal olarak ilan edilemez.
- **Uyarı:** Kurallar şimdi K'yi büyütmek için ayarlanırsa bu sonuca kör bir ayar olur (puanlar görülmedi), ama yine de
  bir çatallanmadır. Yapılan her değişiklik bu raporun sayılarıyla birlikte kayda geçmeli.
- **Öneri:** "TR-1: güç yok (üstveri sayımı, K ≈ 11–12 < 20; plasebo 3 < 10). Hiçbir seri indirilmedi." Ardından
  bölüm 9: GEONET F5 doğrudan (Japonya'yı geri getirir) ya da fay doğrultusuna izdüşümlü yönlü ölçü. Yeni ön kayıtta
  bu betik önce koşulmalı; K ≥ 20 ve plasebo ≥ 10 sağlanmadan dondurulmamalı.

## C. Sürüm 1 bulgularının durumu

| Sürüm 1 bulgusu | Durum |
|---|---|
| 1. Kod 2 kuralı | Düzeltildi. Ancak K hâlâ < 20 (bulgu 9). |
| 2. Kontrol yanlılığı | Büyük ölçüde düzeltildi. Kalanlar: bulgu 1, 3, 5. |
| 3. İstatistik | Düzeltildi. Kalanlar: bulgu 4 ve 7.6. |
| 4. Tanımlar | Düzeltildi. Kalanlar: bulgu 6 ve 7. |
| 5. Sızıntı ve körlük | Düzeltildi. 7.7 ile tamamlanmalı. |
| 6. Hacim | Düzeltildi (üstveri ön elemesi). |
| 7. İddia dili | Düzeltildi. Bulgu 8 hariç. |
