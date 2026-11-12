# Türetme zinciri

Her halka: önceki sonuç, ondan çıkan soru, köprü ölçümü, karar. İstem: `kayit/prompt/2026-11-11_fable52-turetme-gorevi.md`.
Köprü ölçümü: iki tohum kümesinin ikisine de atıf yapan iş sayısı k ve Jaccard J (OpenAlex, `kayit/oa.py kopru`);
her ölçümün yanında pozitif kontrol olarak "tahmin sınama × ETAS" (k 154–208, J ≈ 0,06).

## Halka 0 (11 Kasım 2026): başlangıç

Önceki sonuç: 79 aday. Zaman ekseninde olay geçmişine koşullama (FA-1) H0, öncü artış modeli (TK-1) ayırt edilemez,
gevşeme modelleri yarışı (VE-1) veri yok, düşük eşikli katalog (AV-2) güç yok.
Çıkan soru: fayın anlık gerilme ya da kayma durumunu ölçen, daha önce bakılmamış bir gözlem türü var mı ve sınanmış mı?

## Halka 1 (11 Kasım 2026): beş gözlem türünün taraması

Beş kol, Opus alt ajanlarla, OpenAlex. Notlar: `research_notes/Fayın anlık durumu gözlem boşlukları/`.

| Kol | Köprü (× tahmin sınama) | Literatür hükmü | Çıkan aday | Karar |
|---|---|---|---|---|
| Ortam gürültüsüyle sismik hız değişimi | k 6, J 0,0028 (kontrolün 1/23'ü) | Yalnız deprem anı düşüşü ve iyileşme; öncül iddialar tek olaylı. Marmara serisi yayımlanmamış | TR-4 Marmara gürültü tabanı; TR-5 küresel öncül sınavı | Bekle: ölçü en iyi durumda gerilme hızını ölçer; dalga formu işlemesi ağır |
| Ardışık kırılmada komşu segment gecikmesi | k 32, J 0,0127 (1/4'ü) | Sayısal gecikme dağılımı ve puanlı sınav yok | TR-3 gecikme çekirdeği | Kapandı, güç yok: kaba sayımda 1–30 yıl oran artışı 1,14 kat (p ≈ 0,12); gereken olay sayısının 4–20'de biri var |
| Sismisiteden gerilme hızı; tremor | k 61, J 0,024; tremor k 3, J 0,003 | Hepsi geriye dönük, tek olaylı. KAF'ta tremor bulunmamış | TR-6 gerilme ölçerin kör doğrulaması; TR-7 tetiklenmiş tremor taraması | Bekle: çözünürlük 5–25 kPa, Marmara yavaş kaymaları ≲ 1 kPa |
| Nisan 2025 Mw 6,2 doğal deneyi | k 2, J 0,0022 | Kırık doğuya ilerledi, sessiz "Avcılar" kesiminin kenarında durdu; kayma açığı sayısı yok | TR-2 sonraki M≥6'nın yönü; TR-9 artçı cephesi ile jeodezik sınır | TR-2 için önce olay sayımı; TR-9 bekle (2 dizi) |
| Jeodezik geçici ve uydu gravitesi | k 8, J 0,0084; gravite k 0 | Öncül iddiaları 2024–2026'da bağımsız analizde düştü; çok olaylı puanlı sınav yok | TR-1 küresel GNSS hız değişimi sınavı; TR-10 sünme hızı değişimi; TR-8 gravite | TR-1 ÖNE ALINDI; TR-8 elendi (M7 sinyali ölçüm eşiğinin ≈1/125'i); TR-10 bekle |

Neden TR-1: beş kolun ortak bulgusu aynı, hiçbir gözlem türünde yanlış alarm oranı ölçülmüş çok olaylı sınav yok.
TR-1 bunlardan (a) hedef olay sayısı güç kapısını geçebilecek tek aday (kaba sayım 60 olay), (b) verisi açık ve hazır,
(c) fayın kayma durumunu doğrudan ölçen büyüklüğe (yüzey hızı) bakan aday. Ön kayıt: `kayit/onkayit/TR-1_*`.

Kapanmış adayların yeniden açma şartları denetlendi: hiçbiri sağlanmıyor (Y-1: Klein 2026 hakemli değil; FA-3: model
kataloğu kapalı; VE-1: dört tam metinden ikisinin açık bağlantısı var ama okunamadı; S-2: Murru 2016 açık bağlantısı
bulundu, içerik işlenmedi).

## Halka 2 (11 Kasım 2026): TR-1 koşulmadan kapandı, TR-2 donduruldu

Önceki sonuç: TR-1 (büyük deprem öncesi 2 yıllık GNSS hız değişimi, küresel sınav) ön kaydı iki incelemeden geçti
(1: RED, 2: düzelt-sonra-kabul). Sürüm 2 kurallarıyla yalnız üstveriden sayım: en az 5 kontrollü olay 15, bağımsız
küme 11–12 (kapı 20), plasebosu hesaplanabilen olay 3 (gereken 10 küme). Hüküm: güç yok; hiçbir seri indirilmedi.
Kaba sayımdaki 60 olay, temiz pencere şartı sayılmadan bulunmuştu. Kayıt: `kayit/onkayit/TR-1_INCELEME-2.md`.

Başarısızlığın biçimi: darboğaz olay sayısı değil, kirlenmemiş karşılaştırma penceresi. Büyük depremler, daha
önceki depremlerin basamak ve postsismik izlerinin sürdüğü yerlerde oluyor; Japonya'da 7 olayın kümesi geçerli ama
aynı anda sakin kontrol merkezi yok. Yani "olay önü hız değişimi olağandan büyük mü" sorusu, "olağan" ölçülmeden
sorulamıyor.

Çıkan soru (TR-11): depremden bağımsız olarak, bir GNSS kümesinin 2 yıllık hız değişiminin taban dağılımı nedir?
Yani hiç deprem olmayan pencerelerde belli büyüklükte bir hız değişimi ne sıklıkta görülür (yanlış alarm oranı) ve
bu tabanın üstüne çıkabilmek için bir ön kaymanın en az kaç mm/yıl yüzey hızı değişimi üretmesi gerekir? Bu bir
tahmin sınavı değil, ölçüm sınırıdır: sonucu "yıl ölçekli GNSS alarmı Marmara'da şu büyüklükten küçük ön kaymayı
göremez" cümlesidir. Olay gerektirmediği için TR-1'in darboğazına takılmaz. Marmara istasyonlarının 2017 sonrası
verisi VE-1 için kör kalır; taban Marmara dışı istasyonlardan ve Marmara'nın 2016 ve öncesinden ölçülür.

Köprü ölçümü: Halka 1'deki jeodezik geçici kolu (k 8, J 0,0084; kontrol k 154–208). Yeni ölçüm yapılmadı.

Karar: TR-11 aday olarak deftere girdi; TR-2 koşusundan sonra ön kayda alınır.

Paralel kol, TR-2 (doğrultu atımlı Mw 6,0–7,2 sonrası gelen M≥6 artçısı az tarafta mı): olay sayımı 40 bağımsız
küme, güç kapısı sınırda geçti (ölçülebilir en küçük isabet oranı 0,699, eşik 0,70). Ön kayıt incelendi (düzeltmeyle
kabul; zaman ters çevrimi negatif kontrolü, manifest, ETAS formülü eklendi) ve 0614c3d ile donduruldu. Bu sınav zamanı
değil yönü ölçer.

## Halka 3 (11 Kasım 2026): TR-2 sonucu H0

Önceki sonuç: TR-2 tek koşu (ön kayıt 0614c3d + Ek 1, kod incelemesi 4d22ee2, sonuç `kayit/turetme/tr2/tr2_sonuc.md`).
40 bağımsız kümenin 15'inde sonraki M≥6 artçısı az tarafta: oran 0,375. Hüküm H0, yani 0,70 ve üstü bir "sessiz
taraf" etkisi yok. Eğilim tersine (artçısı çok taraf 0,625) ama ters yön notu eşiği (15'e karşı 14) aşılmadı; iki
yanlı p ≈ 0,15, kanıtlanmadı. Zaman ters çevrimi 16/28: tanımın kendisi yön yanlılığı üretmiyor. ETAS yön modeli
tabandan ayrışmadı (−0,57 nat, aralık [−7,8, +6,3]). Türkiye'deki tek küme (1999 Düzce) ıska; tek olay yorumlanmaz.
Alt gruplar (bilgi): büyük olay gölgesindekiler çıkınca 14/29; çift ve öncüler çıkınca 12/34.

Başarısızlığın biçimi: etki yok değil, yönü belirsiz ve küçük. 0,625 düzeyinde bir eğilimi %80 güçle görmek için
≈100 bağımsız küme gerekir; küresel M≥4 kataloğu en gevşek tanımla 55 veriyor. Taşıyan varsayım "artçı asimetrisi
kırılmamış komşu kesimi gösterir" idi; veri bunu desteklemedi.

Çıkan soru: yok (bu kolda). Sınır hükmü: artçı asimetrisinden sonraki M≥6'nın yönü bugünkü küresel katalogla
ayırt edilemez; eksik veri, M≥3,5 tamlığında küresel artçı kataloğu ya da ≥30 kümede sonlu fay kırılma yönü.
Marmara'ya taşınan: hiçbir şey. Nisan 2025 Mw 6,2 sonrası "sıradaki olay sessiz Avcılar tarafında" okuması küresel
örneklemden destek almıyor; tersi de kanıtlanmadı.

Karar: TR-2 kapandı (H0). Sıradaki halka TR-11 (GNSS hız değişiminin taban dağılımı; Halka 2'de türedi).

## Halka 4 (11–12 Kasım 2026): TR-11 ölçümü

Önceki sonuç: TR-11 tek koşu (ön kayıt cbdfb9e + Ek 1–2; inceleme 1 düzeltmeyle kabul; kod incelemesi koşulabilir;
sonuç `kayit/turetme/tr11/tr11_sonuc.md`). 4730 istasyon indirildi (hata 0), 665 depremsiz küme-pencere, 300 yer,
50 blok. Kod denetimleri gerçek S görülmeden geçti (yapay oran 0,969; eklenen 3 mm/yıl sinyal istasyon düzeyinde
3,0000).

- Taban: 2 yıllık hız değişimi ölçüsü S'nin %95'i 2,42 [2,06, 2,76] mm/yıl; medyan 0,79; %99 3,71 [3,26, 4,83].
- Önceden beyan edilen gürültü modeline göre: eşdeğer kırpışma genliği 4,58 [3,90, 5,22]; etiket "N0 bandında",
  çünkü alt sınır 4'ün hemen altında. Kuyruk Gauss modelinden ağır (oran 1,94 [1,67, 2,16]). Yazarın önsel beyanı
  (0,45 "N0-yüksek'ten büyük", 0,45 "bantta") ikisi arasında kaldı.
- Marmara çevirisi (alt sınır, %5 yanlış alarm, %50 algılama): en elverişli geometride 1,96 mm/yıl, temsilî
  geometride (kilitlenme 10 km, istasyonlar 20 km, dengeli referans) 5,39 mm/yıl'dan küçük derin kayma hızı değişimi
  görülemez. Yayımlanmış kayma açığı hızı 10–15 mm/yıl (özetten). Önceden sabit kural: "bu ölçüm yolu kapatamadı";
  bu, yolun açık olduğu anlamına gelmez.
- Sınırlar: doğrultu atımlı kuşakta 0 yer (güç yok), öteki aktif kuşakta 6 yer; taban az sismik bölge tabanıdır.
  n_y = 8 katmanında 199 küme-pencere kaldığı için çeviri kural gereği havuzla yapıldı. 2008 epoğu belirgin yüksek
  (q95 3,98 [3,29, 5,40], 35 küme-pencere); nedeni ayrıştırılmadı. Sonuç dosyasındaki "okuma durduruldu" ifadesi
  Ek 2'den önceki metinden kaldı; kod satırları atlayarak okudu, sonuç dosyası koşudan sonra değiştirilmedi.

Başarısızlığın biçimi: bu kol bir "hayır" vermedi, bir ölçek verdi. Yıl ölçekli GNSS alarmı Marmara benzeri
geometride ancak yükleme hızının kabaca üçte biri ile yarısı kadar (ve bu alt sınır) bir derin kayma değişimini
görebilir. Soru artık "öncül var mı" değil, "iddia edilen öncüller bu ölçeğe ulaşıyor mu".

Çıkan soru (TR-12): yayımlanmış yıl ölçekli öncül GNSS hız değişimi iddialarının büyüklükleri, aynı ölçüye
çevrildiğinde bu tabanın (%95: 2,4; %99: 3,7 mm/yıl) üstünde mi? Bu bir literatür tablosudur; tam metin sayıları
gerekir, özetten doğrulanamayan sayı kullanılmaz.

Köprü ölçümü: jeodezik geçici × tahmin sınama k 8, J 0,0084 (Halka 1; kontrol k 154–208). Yeni ölçüm yapılmadı.

Karar: TR-11 kapandı (ölçüm tamam). TR-12 aday.

## Halka 5 (12 Kasım 2026): TR-12 tablosu, GNSS kolunun sınırı

Önceki sonuç: TR-12 literatür tablosu (`research_notes/Fayın anlık durumu gözlem boşlukları/oncul_iddia_buyuklukleri.md`).
12 yıl ölçekli öncül GNSS iddiası TR-11 ölçüsüne çevrildi. Tabanın (2,42 mm/yıl) üstünde doğrulanmış iddia yok;
3'ü altında, Bedford 2020 büyük olasılıkla altında (4–8 mm'lik tersinme 0,3–2,8 mm/yıl), 8'i çevrilemiyor (yüzeyde
küme düzeyinde büyüklük yayımlanmamış ya da tam metin okunamadı; yayıncı 403'leri atlatılmadı). Tek olaylı 11
iddianın hepsi dalma-batma; kıta içi doğrultu atımlı fay için yıl ölçekli GNSS öncül iddiası bulunamadı.

Başarısızlığın biçimi: sınanacak bir etki büyüklüğü yok. İddialar fay kayması ya da moment cinsinden, tek olaylı ve
başka mekanizmada; TR-11 ölçüsü de en sık bildirilen biçimlere (5 yıldan eski hız adımı, geri dönen tersinme)
yapısal olarak duyarsız.

Sınır hükmü: "yıl ölçekli GNSS hız değişimi Marmara'da büyük depremin zamanını daraltır mı" sorusu bugünkü açık
veriyle sınanamaz. Eksik veri: (a) olay öncesi yoğun ağ serileriyle en az 20 bağımsız olay kümesi (TR-1), (b) aktif
doğrultu atımlı kuşakta en az 30 sakin yer (TR-11 sınıf A), (c) kıta içi doğrultu atımlı fayda yayımlanmış bir
öncül büyüklüğü. Elde kalan tek sayı TR-11'in ölçeği: temsilî Marmara geometrisinde 5,4 mm/yıl'dan küçük derin
kayma hızı değişimi görülemez (alt sınır).

Çıkan soru: bu koldan 0 € ile sınanabilir yeni soru çıkmadı. Halka 1'den bekleyen adaylar yeni iş paketi gerektiriyor
(seçim Erdem'in): TR-5/TR-4 ortam gürültüsüyle sismik hız değişimi (dalga formu işlemesi), TR-6 sismisiteden
gerilme ölçerin kör doğrulaması, TR-7 tetiklenmiş tremor taraması, TR-9 artçı cephesi ile jeodezik sınır, TR-10
sünme hızı değişimi (NISAR serisi bekleniyor).

Üç turun özeti: TR-1 güç yok (koşulmadı), TR-2 H0, TR-3 güç yok, TR-8 elendi, TR-11 ölçek verdi, TR-12 veri yok.
Zaman eksenini yıl ölçeğine indiren bir terim bulunmadı; yeni bir iddia kanıtlanmadı.

## Halka 6 (12 Kasım 2026): bütün açık adaylar ilerletildi, eleme yok

Erdem'in talimatı (12 Kasım 00:41Z): "Tüm açık ihtimalleri götür, seçim yapmadan ilerlet, ihtimalleri elemeyelim."
Halka 5'teki "yeni iş paketi, seçim Erdem'in" cümlesinin yerini bu aldı: altı adayın her biri için ayrıntılı 0 €
sayım ve güç kapısı yapıldı; kapıyı geçenler ön kayıt, bağımsız inceleme ve tek koşu hattına girdi.

Sayım sonuçları (hepsi 0 €):

| Aday | Kapı | Durum |
|---|---|---|
| TR-9 artçı cephesi ile jeodezik sınır | 4–6 bağımsız küme, kapı 20: geçmedi | aday olarak duruyor (yeniden açma şartlarıyla) |
| TR-10 sünme hızı değişimi → yakın M≥6 | 17 küme, açık veriyle 3, kapı 20: geçmedi | aday; olaysız taban ölçümü TR-10b türetildi |
| TR-10b sünme ölçer taban dağılımı | üstveride sınırda (22 yer / 41 pencere) | TEK KOŞU: veri yok (8 yer / 11 pencere) |
| TR-7 tetiklenmiş tremor taraması | 935 varlık yoklamasıyla geçti (71 çift, 17 olay) | ön kayıt sürüm 3 donduruldu; kod yazılıyor |
| TR-6 (b) Marmara çözünürlüğü | 15–134 kPa/yıl, sinyal üst ucu ≈6,5: geçmedi | aday (Mc ≈ 1 katalog şartıyla) |
| TR-6 (a) küresel kör doğrulama | Aσ 19 kPa sabit; 39 küme, yeni kurallarla 29 (gereken 23): geçti, kırılgan | ön kayıt sürüm 2, ikinci incelemede |
| TR-5 küresel sismik hız öncül sınavı | ana tasarım K 8–15 geçmedi; M≥6,0 / 3 yıl / tek yer biçimi gerçek dolulukla K 37, plasebo 20: geçti | TR-5b ön kaydı yazılıyor; koşu sunucu ister (karar Erdem'de) |
| TR-4 Marmara sismik hız tabanı | 24 KO istasyonu; doluluk %76 yoklandı, sınırda | yoklama sürüyor |

TR-10b sonucu (ilk biten koşu). Ön kayıt sürüm 2 + Ek 1 + Ek 2; 66 dosya, 49 milyon satır. Sakinlik kuralı B'de
aygıt kaydı, kapsam, doluluk ve uç şartlarından sonra 8 yer / 11 yer-pencere / 2 fay kesimi kaldı (kapı ≥ 20 / ≥ 40):
hüküm "veri yok". Kod denetimleri ve pozitif kontrol geçti. Kapı altı bilgi satırı (hüküm değil): sakin pencerelerde
2 yıllık sünme hızı değişimi |Δv| medyan 1,59, %95 3,41 [2,23, 3,81] mm/yıl; sünen istasyonlarda hızın %45'i; 11
pencerenin 9'u yavaşlama yönünde. Aygıt kayıtları uygulanmazsa %95 5,70 [2,77, 13,85] mm/yıl (27 pencere).

Başarısızlığın biçimi: yine örneklem. Üstveri sayımı (43 pencere) gerçek veriyle 4 kat küçüldü; küçülmenin yarısından
fazlası aygıt kayıtlarındaki tarihsiz notlardan. Önceki turların dersi (kaba sayım 3–5 kat iyimser) dördüncü kez
tuttu. Yan bilgi: yayımlanmış tek sayılı öncül sünme iddiası (Chihshang 2003, −8 mm/yıl) bu 11 pencerelik kapı altı
dağılımın %95'inin (3,41) üstünde, ama aygıt kayıtsız dağılımın belirsizlik aralığının içinde; karşılaştırma bindirme
fayıyla doğrultu atımlı fay arasında ve hüküm taşımaz.

Çıkan soru: TR-10b'den yeni bir 0 € soru çıkmadı; yeniden açma şartları defterde (tarihlenmiş aygıt kayıtları,
başka sünme ağları, NISAR). Sıradaki halkalar TR-7, TR-6a ve TR-5b koşularının biçiminden okunacak.

## Halka 7 (12 Kasım 2026): TR-5b aşama 0, güç yok

TR-5b ön kaydı (M ≥ 6,0 sığ depremlerden önceki son yılda tek istasyon dv/v, küresel olay–kontrol sınavı) iki bağımsız
incelemeden sonra sürüm 3 olarak donduruldu (bfd9b0a). Sunucu kiralamadan önce koşulması şart koşulan aşama 0 (doluluk
sayımı; 292 istasyon, 25 315 yoklama isteği, 0 €, dalga formu indirilmeden) bir kez koşuldu.

Sonuç: bağımsız küme K₀ = 18 (kapı 20), eşleşik plasebo kümesi K_p₀ = 7 (kapı 10). Hüküm "güç yok (aşama 0)". Üstveri
sayımı 31 / 16 idi. 1246 pencerenin 478'i dolu; 547'si Z bileşeninde boş ay, 110'u aygıt değişimi, 99'u üç bileşen
yok, 12'si yatay bileşen yüzünden düştü. 51 istek (hepsi SCEDC) iki denemede de hata döndü ve kural gereği dolu
sayılmadı; bunların sonucu değiştirip değiştirmeyeceği ayrıca hesaplanmadı, plasebo kapısı 7 / 10'da. dv/v
hesaplanmadı, olay verisi indirilmedi; TR-5b'nin olay verisi kör kaldı. Sunucu kiralanmadı (≈1,5 TB indirme
önlendi); Erdem'e açılan sunucu kartı geri çekildi.

Başarısızlığın biçimi: beşinci kez örneklem, bu kez doluluk. Darboğaz hesap gücü değil, M ≥ 6 öncesinde 3 yıl
kesintisiz üç bileşenli açık kayıt. Yeniden açma şartları ön kayıt §11'de (Hi-net / F-net gibi yeni açık arşiv;
istasyon çifti tasarımı; TR-4'ün ölçeceği σ_Δ'nın küçük çıkması).

Çıkan soru: TR-4 (Marmara KO istasyonlarında olaysız dv/v tabanı) artık tek başına anlamlı: hem Marmara'da
algılanabilir en küçük hız değişimini verir hem de TR-5b'nin (c) yeniden açma şartını ölçer. Ön kaydı sıradaki iş.
Aynı gün TR-6a ve TR-7'nin koşu kodları bağımsız kod incelemesinden geçti (ikisi de DÜZELTMEYLE KABUL, veri öncesi
Ek 1); yapay verili bağlayıcı yöntem sınamaları koşuyor.

## Halka 8 (12 Kasım 2026): teorik literatür taraması

Erdem'in isteğiyle (12 Kasım 08:12Z: "teorik de çok kıymetli") zincire kuramsal kol eklendi; o ana dek halkalar yalnız
ampirikti. Beş kol (çekirdeklenme ve ön kayma; döngü dinamiği ve kaos; gerilme etkileşimi ve yükleme; istatistiksel
fizik ve bilgi sınırı; kilitli pürüz ve sünme), OpenAlex ile, 0 €. Notlar
`research_notes/İstanbul depremi teorik öngörülebilirlik/`, rapor `reports/İstanbul depremi teorik öngörülebilirlik.md`.

Sonuç: beş kuram ailesinin hiçbiri büyük bir doğrultu atımlı depremin zamanını ilkece yıl ölçeğine daraltmıyor;
onlarca yıla daraltıyor. Yenilenme kuramı geç çevrimde tehlikeyi Poisson'un 1,5–3 katına çıkarır (tarayıcının hesabı);
çekirdeklenme evresi algılanabilir olarak saatler–günler sürer; sünme cephesinin iki yıllık yüzey izi TR-11
tabanının 5–100 kat altındadır (tarayıcının hesabı); mükemmel modelli ikiz deneyler alarmı yinelenmenin %10–17'sine
indirir. Bu, zincirin ampirik halkalarında görülen biçimle (güç yok, taban altında) tutarlıdır. Birçok tam metin 403
döndü ve aşılmadı; o sayılar notlarda "doğrulanamadı" işaretli.

Çıkan sorular (deftere aday olarak girdi): TR-13 sismisite yerelleşmesi depremden 2–3 yıl önce artıyor mu, ETAS
tabanına karşı (yıl ölçeğine dokunan ve projede benzeri olmayan tek açık kuramsal öngörü); TR-14 iki boyutlu
hız-durum modelinde öngörülebilirlik ufku (koşullu tavan); TR-15 öncü dizilerinde 1/t ivmelenme (gün ölçeği).
Kuramın yıl ölçeğinde bıraktığı öteki pencere, sismisitenin gerilme hızına tepki süresi, TR-6a ile zaten sınanıyor.
Sıradaki iş: TR-13 için 0 € sayım ve güç kapısı.

## Halka 9 (12 Kasım 2026): TR-13 sayımı güç yok; TR-4 doluluk kapısını geçti

TR-13 (kuramdan türeyen, yıl ölçeğine dokunan tek açık öngörü: büyük depremden 2–3 yıl önce sismisite yerelleşmesi,
Ben-Zion ve Zaliapin 2020) için 0 € sayım ve güç kapısı yapıldı (`kayit/onkayit/TR-13_SAYIM.md` + Ek 1). 1980–2025'te
1175 sığ doğrultu atımlı Mw ≥ 6,0 ana şok / 538 küme; önce-penceresi temiz ve yeterli arka planlı 25–31 küme;
referans dönemi de dolu olunca 11–20 (ana tasarım 14); eşleşik depremsiz kontrol de istenince 3–7. Kapı 20. ETAS
yapay kataloglarında tek pencerelik yanlış alarm oranı %13–37 (anma %5) ve kümesizleştirme seçimi sonucu tek başına
belirliyor. Ölçünün tanımı kaynaktan okunamadı (403), yeniden kurulum kullanıldı. Hüküm: güç yok (sayım); ön kayıt
yazılmadı, gerçek katalogda ölçü hesaplanmadı. Biçim yine örneklem: darboğaz, geçmişe doğru katalog tamlığı.

TR-4 (Marmara sismik hız tabanı): ön kayıt sürüm 2 donduruldu (430b4a0; Ek 1 968dca2), aşama 0 doluluk sayımı (597
yoklama, 0 €) kapıyı geçti: 105 dolu yer-penceresi, T başına 15, 16, 15, 14, 14, 9, 11, 11 yer. Zincirde gerçek
dolulukla küçülmeyen ilk sayım (önceden yoklanmış olduğu için). Sıradaki: Kandilli indirme hızı ölçümü kademeyi
belirler; hız 23–40 KiB/s ise ön kayıt gereği "veri yok (aktarım hızı)".

Kuramsal koldan kalan adaylar: TR-14 (hız-durum modelinde öngörülebilirlik ufku; hesap, veri değil) ve TR-15 (öncü
dizilerinde 1/t; gün ölçeği).
