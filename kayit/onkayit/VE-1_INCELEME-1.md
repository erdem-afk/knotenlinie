# VE-1 ön kayıt taslağı: bağımsız inceleme 1

İncelenen: `kayit/onkayit/VE-1_gnss-hiz-degisimi_TASLAK.md` (11 Kasım 2026 hali). Bağlam: `kayit/kollar/VE.md` (VE-1, K10 şart önerisi), `kayit/kollar/AV.md` (AV-1, envanter satırı 1), `kayit/README.md`.
İnceleyici: bağımsız ajan. Taslağı ben yazmadım. 2017+ GNSS serilerini ne indirdim ne okudum. İnternete yalnız Crossref'te yayım tarihi ve DOI doğrulamak için çıktım.
Tarih: 11 Kasım 2026.

## Hüküm: **RED** (bu haliyle dondurulamaz)

Hükmü belirleyen dört gerekçe var:
1. H1a ve H1c'nin girdi makaleleri taslağın kendi sızıntı kapısını (kural 5) ihlal ediyor.
2. Hüküm satırı üç modelin en iyisini seçiyor. Bu, düzeltilmemiş bir çoklu karşılaştırma.
3. İstasyon seçim ölçütleri, kolların bildirdiği veri envanteriyle birlikte okunduğunda N'yi tahminen 1–3'e indiriyor. Taslak bunu fark etmemiş.
4. Ana analiz çizgisinde çerçeve, ortak kip, hız tahmincisi ve model öngörüsünün hesaplanış biçimi açık bırakılmış.

Aşağıdaki yüksek önemli bulgular düzeltilip ikinci inceleme yapılmadan DONDUR + OTS yapılmamalı.

---

## A. Hüküm satırı ve çoklu karşılaştırma

**B1 (yüksek): "En iyi H1 modeli − H0" seçim yanlılığı yaratıyor.**
Üç H1 skorunun en büyüğü, H0 doğru olsa bile beklentide sıfırın üstündedir. Her H1 modelinin içinde de bir parametre aralığı var (B4). Bu yüzden etkin karşılaştırma sayısı 3'ten fazla. "%95 alt sınırı > 0" koşulu seçimden önce hesaplanmış bir aralığa göre konmuş, seçimden sonraki dağılıma göre değil. Gerçek birinci tür hata %5'in üstünde olur ve kimse bunu ölçmüyor.
Düzeltme (ilki önerim, öteki iki seçenek de kabul edilebilir):
- (a) **Tek birincil tahmin olarak eşit ağırlıklı karışım:** p_H1 = (p_H1a + p_H1b + p_H1c)/3 (ya da sızıntı yüzünden H1a/H1c düşerse kalan modeller). Karışımın log skoru tek ve önceden belirlenmiş bir tahmindir. Model başına skorlar bilgi satırına iner.
- (b) Önceden tek model seçilir, gerekçesi yazılır (ör. ≤2016 literatüründe en çok desteklenen Burgers/Hearn 2009). Diğerleri bilgi satırı olur.
- (c) Üç ayrı test + Holm. O durumda "alt sınır" yerine her model için H0 altında simülasyonla p değeri tanımlanmalı ve Holm sırası yazılmalı. Bootstrap alt sınırıyla Holm doğal biçimde birleşmez, bu yüzden (a) daha temiz.
Hangisi seçilirse seçilsin, güç testi (B10) **tam karar kuralını** (karışım ya da seçim dahil) simüle etmeli.

**B2 (orta): Alt sınırın tanımı belirsiz.**
"%95 alt sınırı" iki biçimde okunabilir: tek yönlü %95 (yüzdelik 5) ya da iki yönlü %95 aralığın alt ucu (yüzdelik 2,5). Bootstrap türü de yazılmamış (yüzdelik, BCa, t).
Düzeltme: "tek yönlü, B = 10 000 yeniden örneklemenin 5. yüzdeliği, yüzdelik yöntemi, tohum = X" gibi tam yazılsın.

**B3 (orta): Tahmin yoğunluğu tanımlı değil.**
"Gauss log skoru" yazıyor ama H0 ve H1'in Δv için tahmin dağılımı (ortalama, kovaryans) yazılmamış. Şu sorular açık:
- Varyans yalnız gözlem belirsizliği mi, model belirsizliği de ekleniyor mu?
- Doğu ve kuzey arasındaki korelasyon kullanılıyor mu?
- İstasyonlar arası kovaryans kullanılıyor mu?
Model belirsizliği eklenmezse H1, öngörüsü doğru yönde ama abartılı olduğunda ağır cezalanır. Eklenirse H1 kendi varyansını büyütüp kazanabilir.
Düzeltme: H0 için N(0, C_obs). Her H1 için N(μ_model, C_obs + C_model). C_model'in nasıl hesaplanacağı yazılsın: ör. SRCMOD dokuz kaynak modelinin yaydığı Δv'nin örnek kovaryansı. Model içi parametre aralığından gelen yayılım da (B4) buraya girer. C_obs B13'e göre tanımlanır.

## B. Sızıntı

**B4 (yüksek): Özarpacı 2021 kapıyı ihlal ediyor; H1a bu haliyle geçersiz.**
Crossref'e göre 10.1093/gji/ggaa560 ilk çevrimiçi yayım 2020-11-19, baskı 2020-12. Başlığı: "Present GPS velocity field along 1999 Izmit rupture zone: evidence for continuing afterslip 20 yr after the earthquake". Yani hem yayım tarihi 2017'den sonra, hem de makale büyük olasılıkla 2017 sonrası GNSS gözlemlerine uydurulmuş. Bu, hedef dönemle **doğrudan örtüşme** demek. Kural 5 ("yayım < 2017-01-01") kendi taslağı tarafından çiğneniyor.
Düzeltme: H1a'nın 1/t (logaritmik) afterslip parametreleri yalnız ≤2016 kaynaklardan alınsın. Örneğin Ergintav 2009 ya da Hearn 2009'daki afterslip bileşeni; DOI ve tablo/satır numarasıyla yazılsın. Böyle bir kaynak yoksa H1a düşer. Hedef dönemi Özarpacı'nın verisinden sonraya kaydırmak işe yaramaz, çünkü NGL serilerinin çoğu Ocak 2024'te bitiyor.

**B5 (yüksek): Hussain 2018 de kapıyı ihlal ediyor; H1c etkileniyor.**
10.1038/s41467-018-03739-2 için Crossref çevrimiçi tarihi 2018-04-11. H1c'nin iki kaynağından biri bu.
Düzeltme: H1c yalnız Yamasaki 2014'ten (10.1002/2013jb010347, 2014-04-17) parametrelenir. Hussain 2018 "model girdisi değil, bilinen sonuç" olarak körlük beyanına taşınır (B16).
Diğer kaynaklar kapıdan geçiyor:
- Hearn 2009: 10.1029/2008jb006026, 2009-08-25
- DeVries 2016 G3: 10.1002/2016gc006313, 2016-07-17
- DeVries 2016 BSSA: 10.1785/0120160059, çevrimiçi 2016-11-29. Basılı sayısı 2017-02 olduğundan kural "ilk çevrimiçi tarih" diye yazılmalı.

**B6 (yüksek): "≤2016 yayım" sızıntısızlık için yeterli değil; parametreler nokta değer de değil.**
2016'da yayımlanmış bir makale de 2016'ya kadarki verilere uydurulmuştur. Burada sorun yok, çünkü hedef 2017+. Ama kapı yalnız yayım yılına bakıyor. Gözlem penceresinin sonu da yazılmalı: her girdi makalesi için "uydurulan verinin son epoğu < 2017-01-01".
Ayrıca VE.md'deki değerler **aralık**: Hearn geçici 2–5×10^19; DeVries Maxwell 4×10^18–10^19, Kelvin 10^18–10^19. "Parametreler dondurulur" ifadesi hangi değerin seçileceğini söylemiyor ve bu, koşudan sonra bir serbestlik.
Düzeltme: Her model için tek bir parametre vektörü yazılsın (makalenin "en iyi" değeri; tablo numarasıyla). Ya da aralık uçları ve ortası eşit ağırlıklı alt karışım olarak tanımlansın. Hangisi seçilirse SHA-256'lı bir YAML dosyasında donsun.
Bunlara ek olarak:
- İleri model "PSGRN/PSCMP **ya da** RELAX" diye bırakılmış. Tek araç ve sürüm seçilsin.
- Elastik katman modeli (CRUST1.0 mi, makaledeki mi) yazılsın.
- Afterslip (kinematik) ile viskoz akışın (H1b) hangi araçla hesaplanacağı yazılsın. PSGRN afterslip'i doğrudan modellemez.

**B7 (orta): Model öngörüsü ile gözlem aynı tahminciden geçmiyor.**
Δv anlık hız farkı değil. İki pencerede doğrusal + mevsimsel en küçük kareler eğimlerinin farkı. 1/t ya da üstel sönümde pencere içinde eğim değişir.
Düzeltme: Her model, gözlemle aynı epoklarda yer değiştirme serisi üretir. Gözlemle **aynı** tahminci (aynı atım terimleri, aynı pencereler, aynı boşluk deseni) bu seriye uygulanır, model Δv'si böyle elde edilir. Bu kural önceden yazılmazsa "anlık mı, pencere ortalaması mı" seçimi sonuçtan sonra yapılabilir.

## C. Veri, istasyon seçimi, atım, çerçeve

**B8 (yüksek): Seçim ölçütleri istasyonların neredeyse hepsini eler.**
- "2009-01-01 **öncesi** başlayan" ölçütü: AV.md'ye göre TUSAGA-Aktif serileri 2009-01'de başlıyor, VE.md'ye göre de "2009-01 → 2023/24". Katı "öncesi" bunların tamamını dışarıda bırakır. Kalanlar ISTA, TUBI ve belki birkaç IGS/EUREF istasyonu.
- "Her iki dönemde doluluk ≥ %60" ölçütü: AV.md genel doluluğu ≈%48 veriyor (≈2500 çözüm / ≈15 yıl). Ölçüt TUSAGA'nın büyük kısmını yine düşürür.
- Sonuç olarak VE.md'nin güç hesabındaki N ≈ 13 bu kurallarla tutarsız. Gerçek N tahminen 1–3. TUBI 2023-06'da bittiği için "2017+ ≥ 4 yıl" ölçütünü ancak geçiyor.
Düzeltme: Dondurmadan önce **yalnız üstveriden** (DataHoldings.txt: başlangıç, bitiş, çözüm sayısı) uygun istasyon listesi çıkarılsın ve listenin kendisi dondurulsun. Dönem başına doluluk konum değerine bakmadan hesaplanamıyorsa ölçüt "toplam çözüm sayısı/gün sayısı" ile değiştirilsin. Ölçüt eşikleri (başlangıç ≤ 2009-03-01, doluluk ≥ %40 gibi) önce N'ye bakarak ayarlanırsa bu sızıntı değildir, çünkü üstveri hedef değil. Ama bu ayar körlük beyanına yazılsın. N < 8 çıkarsa güç testine bile gerek yok: `guc-yok`.

**B9 (orta): Kutu, çerçeve ve istasyon sayısı tutarsız.**
- Taslak: kutu 26,5–31,5°D / 39,8–41,6°K, IGS14, "28 istasyon".
- AV.md: kutu 26–31,2°D / 40–41,6°K, **IGS20** tenv3, 28 istasyon. Yani 28 sayısı başka bir kutudan geliyor.
- NGL IGS14 serileri artık güncellenmiyor olabilir; Ocak 2024 sonrasını içermeyebilir. Emin değilim, üstveriden doğrulanmalı.
Düzeltme: Tek bir çerçeve seçilsin. Tercihim IGS20, çünkü serinin tamamı tek çözümde. Dosya yolu (`gps_timeseries/IGS20/tenv3/IGS20/`) ve indirme tarihi yazılsın, kutu tek tanımla verilsin. Taslağın tamamı tek çerçeve sürümünde ve tek seri sürümünde hesaplanmalı. NGL serileri zaman zaman yeniden işliyor; iki dönem farklı işleme sürümünden gelirse Δv'ye yapay terim girer.

**B10a (orta): Ortak kip ve referans çerçevesinde serbestlik var.**
Kural 3'ün dilbilgisi belirsiz. Ana çizgide ortak kipin çıkarılmadığı anlaşılıyor; çıkarılmış hal bilgi satırında. Sorunlar:
- (i) "10 Anadolu/Trakya istasyonu" adıyla verilmemiş, seçim serbest.
- (ii) Kutudan ≥150 km uzaktaki Anadolu istasyonları da İzmit postsismik alanında olabilir (Hearn 2009 türü manto gevşemesi yüzlerce km'ye yayılır). Kahramanmaraş 2023'ün alanında da olabilirler. Ortak kip çıkarmak sinyalin bir kısmını siler.
- (iii) Ortak kip çıkarılmadan IGS çerçevesinde Δv, çerçevenin kendi hız kararsızlığını taşır. Etkisi muhtemelen < 0,1 mm/yıl, ama bölgesel sistematik etkiler daha büyük olabilir.
Düzeltme: Ana çizgi olarak ham çerçeve mi, ortak kipi çıkarılmış mı, bir tanesi seçilsin. Ortak kip istasyonları adlarıyla listelensin. Modeller aynı istasyonlarda aynı çıkarma işlemiyle hesaplansın (kural 3 bunu söylüyor, iyi). Tercihim: ana çizgi ham IGS20, ama Avrasya-sabit dönme **iki dönemde ortak tek dönme** olarak çıkarılsın. Ortak kip bilgi satırı olsun.

**B10b (yüksek): Atım kuralı kendi içinde çelişkili ve 2023 olayı hedefi kirletir.**
- Kural 1 "steps.txt aynen, ek atım yok" diyor, kural 2 ise üç deprem için atım ekliyor. NGL steps.txt deprem atımlarını büyüklüğe bağlı bir yarıçap kuralıyla zaten işaretliyor; bildiğim kadarıyla r ≈ 10^(M/2 − 0,8) km, M7,8 için ≈1200 km. Kahramanmaraş muhtemelen Marmara istasyonlarında zaten var. Çifte atım olur mu, olmaz mı belirsiz.
- Kahramanmaraş Marmara'ya ≈700–900 km uzak. Uzak alan eş-sismik yer değiştirme Marmara'da muhtemelen birkaç mm ya da daha az; emin değilim. Uzak alan postsismik (manto) hızı mm/yıl altında, belki 0,1–0,5 mm/yıl; emin değilim. Ama hedef sinyal de ≈0,7 mm/yıl ya da daha az, yani **aynı mertebe**.
- Seri Ocak 2024'te bitiyorsa atımdan sonra yalnız ≈11 ay veri var. Atım genliği ve 2017+ eğimi korelasyonlu kestirilir, olay sonrası geçici eğilim de Δv'ye sızar.
- 90 günlük dışlama yalnız < 60 km için tanımlı, Kahramanmaraş için hiç dışlama yok.
- 2025 M6,2 olayı serilerin çoğu bittikten sonra; yalnız ISTA/QIBP/ORE1'i ilgilendiriyor.
Düzeltme:
- **Birincil hedef penceresi 2017-01-01 → 2023-02-05** (≈6,1 yıl) olsun. 2023-02-06 sonrası birincil analize girmesin; dahil hali bilgi satırı olsun.
- Atım listesi = steps.txt ∪ kural 2 listesi, ±2 gün içinde yinelenenler tekilleştirilir. steps.txt sürümünün SHA-256'sı ve indirme tarihi kayda girsin.
- Aykırı değer kuralı yazılsın: ör. artık > 5×MAD çıkar, tek tur. Belgelenmemiş sıçramalar için "eklenmez" kuralı kalsın, ama bir sıçramadan etkilenen istasyonun dışlanma kuralı yoksa bu da yazılsın ("dışlanmaz").

**B11 (orta): Ocak 2024'te biten serilerin anlamı.**
Hedef dönem fiilen 2017–2023, yani ≈6–7 yıl. B10b'deki düzeltmeyle ≈6 yıl. Sonuçları:
- (i) Δv 1999'dan ≈18–24 yıl sonrasını ölçer. 1/t afterslip için beklenen fark küçüktür; 2009–16 orta noktası ≈13,5 yıl, 2017–23 ≈21 yıl, hız oranı ≈0,64.
- (ii) Bu iş ileriye dönük izleme değil, tek seferlik geriye dönük sınamadır (AV.md bulgu 1).
- (iii) "2017+" ifadesi taslakta "bugüne kadar" diye okunabilir.
Düzeltme: Başlıkta ve hedef nicelikte açık pencere yazılsın (2017-01-01 → 2023-02-05). "Bugünkü yüklenme hızı" ifadesi "2017–2023 ortalama hızı" diye değiştirilsin.

**B12 (orta): Hız tahmincisi seçilmemiş.**
"HECTOR ya da MIDAS; incelemede sabitlenir" yazıyor. İnceleyici olarak öneriyorum:
- Eğim, en küçük kareler (doğrusal + yıllık + yarı yıllık + atımlar) ile hesaplansın.
- Eğim belirsizliği HECTOR'la, **yalnız 2009–2016 artıklarından** kestirilen güç yasası + beyaz gürültü modeliyle verilsin. Gürültü parametreleri bu dönemde dondurulsun ve 2017+ penceresine aynı parametrelerle uygulansın. Böylece 2017+ verisi gürültü modeline girmez.
- MIDAS yalnız bilgi satırı olsun. MIDAS'ın eğim kestirimi en küçük karelerden farklı olduğundan model öngörüsünün aynı tahminciden geçirilmesi (B7) MIDAS'la zordur.
HECTOR sürümü ve seçenekleri (gürültü modelleri, ön tanımlı spektral indeks sınırları) yazılsın.

## D. Güç testi

**B13 (yüksek): Gürültü modeli eksik; istasyonlar arası korelasyon yok sayılıyor.**
Yalnız 2009–2016'dan gürültü kestirmek körlük için doğru ve yeterli. Ama şu kalemler eksik:
- (i) **Renkli gürültü** açıkça güç yasası (+ olası rastgele yürüyüş) olarak tanımlanmalı. Kısa serilerde rastgele yürüyüş kestirilemeyebilir. Bu durumda duyarlılık için 0 ve 1 mm/√yıl iki senaryo koşulsun ve güç kapısı **kötü senaryoya** göre işlesin.
- (ii) **İstasyonlar arası korelasyon:** Marmara ölçeğinde (≈300 km) ortak kip gürültüsü günlük artıklarda baskın olabilir. Sentetik seriler bağımsız üretilirse güç abartılır. 2009–2016 artıklarından istasyonlar arası kovaryans (ya da ortak kip + bağımsız kalan) kestirilsin, sentetik seriler bu yapıyla üretilsin.
- (iii) **Boşluk deseni:** sentetiklere 2009–2016 desenleri ya da üstveri sayıları uygulansın. 2017+ gerçek boşluk deseni konum verisine bakmadan bilinemiyorsa bu açıkça yazılsın.
- (iv) **Atım terimleri:** gerçek steps listesindeki atımlar sentetik uydurmaya da konmalı, çünkü her atım güç kaybettirir.
- (v) Güç **gerçek karar kuralıyla** ölçülmeli: B1'deki karışım ya da seçim + bootstrap alt sınırı.
- (vi) Aynı düzenekle **H0 altında birinci tür hata** da ölçülsün ve ≤ 0,05 olsun. Aşarsa kural kalibre edilsin.

**B14 (orta): Gücün hangi H1'e karşı ölçüleceği ve eşikler.**
Güç yalnız H1a'ya karşı tanımlı, oysa H1a sızıntı yüzünden düşebilir (B4). Ayrıca en büyük genlikli modele karşı güç, en küçüğüne karşı gücü fazla gösterir.
Düzeltme: Güç her H1 için ayrı ve karışım için ölçülsün. Kapı **birincil tahmine** (B1) göre işlesin.
Eşikler 0,8 / 0,5 alışılmış ve makul. Ama 0,5–0,8 bandında "sonuç önceden ayırt edilemez ilan edilir" kuralı belirsiz: alt sınır > 0 çıkarsa hüküm ne olacak?
Düzeltme: Bu bantta hüküm satırı yine hesaplansın ama etiketi "H1 yönünde (düşük güç, kazanan laneti uyarısı)" olsun. Pozitif sonuç K10 şart önerisinin 2. maddesini **sağlamış sayılmasın**. Negatif sonuç ise yalnız üst sınır olarak yazılsın.
500 tekrar gücü ±0,02 hassasiyetle verir, yeterli. Tohum yazılsın.

**B15 (orta): Gerçekçi hız farkı belirsizliği.**
Literatürden kesin olmayan bilgimle: sürekli GNSS'te ≈6–8 yıllık seride, flicker + beyaz gürültüyle yatay hız belirsizliği tipik olarak ≈0,1–0,3 mm/yıl. Rastgele yürüyüş (≈1 mm/√yıl) varsa ≈0,4 mm/yıl'a çıkar. %50 doluluk ve ortak kip gürültüsü belirsizliği büyütür. İki pencerenin farkı için √2 çarpanıyla Δv σ'sı **≈0,2–0,6 mm/yıl/bileşen/istasyon** beklerim. VE kolunun 0,35–0,45'i bu aralığın içinde; emin değilim, güç testi belirlesin.
AV kolunun "≈2–3 mm/yıl altı görülemez" tahmini muhtemelen fazla karamsar. Yıllık ortalama artık sd'si 1,4 mm, beyaz kabul edilirse 7 yılda eğim σ'sı ≈1,4/√28 ≈ 0,26 mm/yıl çıkar. Renkli gürültüde daha büyük olur, ama 2–3 mm/yıl'a ulaşmaz.
Asıl sorun gürültü değil, **N** (B8) ve sistematikler (B10b). İzmit'e uzak istasyonlarda beklenen fark < σ.

## E. Skor ve bootstrap

**B16a (yüksek): Uzamsal korelasyon varken istasyon bootstrap'ı geçersiz; N küçükken de güvenilmez.**
İstasyon bootstrap'ı istasyon katkılarının bağımsız ve aynı dağılımlı olduğunu varsayar. Ortak kip ve uzamsal korelasyonlu gürültüde bu varsayım çöker ve aralık dar çıkar. Katkılar heterojen de: İzmit yakını birkaç istasyon toplam skoru belirler. N ≤ 13 iken yüzdelik bootstrap'ın kapsama oranı zaten nominalin altında.
Düzeltme:
- Birincil anlamlılık **parametrik**: güç testindeki aynı korelasyonlu gürültü modeliyle H0 altında 10 000 sentetik Δv kümesi üretilir. Gözlenen log skor farkının bu dağılımdaki üst yüzdeliği p değeri olur, ve karar p < 0,05.
- Log skor, korelasyonlu çok değişkenli Gauss olarak (C_obs tam kovaryans) hesaplansın; istasyon toplamı olarak değil.
- İstasyon bootstrap'ı, uzamsal blok bootstrap'ı (ör. İzmit/Doğu, Orta, Batı-Trakya üç blok) ve birini-dışarıda-bırak duyarlılığı bilgi satırı olsun. "Tek bir istasyon çıkarıldığında işaret dönüyorsa" bu ayrıca yazılsın.
- K10 şart önerisi (VE.md madde 2) bootstrap alt sınırına bağlı. Şart metni de bu karara göre güncellenmeli; bu Erdem'in kararı.

## F. Körlük beyanı

**B16 (yüksek): Körlük beyanı eksik.** Eklenmesi gerekenler:
- (i) **AV kolu ISTA'nın tam serisini indirdi** (1,9 MB, 2026-10'a kadar; AV.md envanter 1). Yıllık ortalama artık sd'si de **tüm seri üzerinden** hesaplandı, yani 2017+ verisi kullanıldı. "Hız farkı hesaplanmadı" doğru olabilir, ama seri görüldü. ISTA birincil analizden çıkarılsın ya da "görülmüş" etiketiyle yalnız bilgi satırında kalsın. İndirilen dosya silinmeli mi, mühürlenmeli mi, o da yazılsın.
- (ii) **Özarpacı 2021'in sonucu biliniyor:** "20 yıl sonra süren deformasyon logaritmik afterslip ile açıklanıyor" (VE.md Soru 2). Bu, 2017+ GNSS verisinin H1a yönünde davrandığına dair doğrudan ön bilgi ve model seçimini etkileyebilir (H1a'nın tanımı bile buradan). Hussain 2018 nasıl H0 lehine ön bilgi diye yazıldıysa bu da H1 lehine ön bilgi diye yazılmalı.
- (iii) de Blas 2022 (Anadolu'nun rijit hareketinin 1999'la değiştiği iddiası) ve Nalbant 2026 bilgisi.
- (iv) VE ve AV kolları NGL DataHoldings üstverisini (başlangıç, bitiş, çözüm sayısı) okudu. Bu hedef değil ama istasyon seçimini etkiler, yazılsın.
- (v) Kahramanmaraş 2023'ün uzak alan etkisine dair literatür bilgisi (varsa).
- (vi) Taslağı yazan ve inceleyen ajanların 2017–2023 Marmara GNSS sonuçlarına dair genel literatür bilgisi. Ben ayrıntılı sayı hatırlamıyorum; yine de "inceleyicinin literatür bilgisi sıfır değil" diye yazılsın.
- (vii) Koşuyu kimin yapacağı ve o kişinin 2017+ serilere daha önce bakıp bakmadığı.

## G. Yanlış yorumlanabilecek cümleler

**B17 (orta): "Tek doğrudan gözlenebilir iz" ifadesi aşırı iddialı ve yanlış genelleme davet ediyor.**
"Yıl–on yıl ölçeğinde zaman bağımlılığının fizik tarafındaki **tek** doğrudan gözlenebilir izi" cümlesi doğru değil: sismisite hızı, sünme hızı, InSAR da var. Ayrıca kara GNSS'i yüzey hızını ölçer; Marmara denizaltı segmentlerinin (CMF, PIF, Çınarcık) yüklenmesini yalnız uzak alandan görür (AV.md görüş sütunu).
Düzeltme: "doğrudan gözlenebilir izlerden biri, kara GNSS istasyonlarında yüzey hız değişimidir; denizaltı segmentlerinin yüklenmesi bu sınamada yalnız model üzerinden çıkarılır" denmeli.

**B18 (orta): "H1 yönünde" sonucu deprem olasılığına bağlanabilir.**
"Sonuç ne olursa" bölümünde iki risk var:
- "PIF, CMF için yüklenme hızı pertürbasyonu yazılır" ve "K10 şart önerisinin 2. maddesi sağlanmış olur" cümleleri birlikte okunduğunda, olumlu sonuç "İstanbul'da deprem olasılığı arttı/azaldı" diye aktarılabilir.
- "H0 / ayırt edilemez" sonucu "yüklenme sabit, olasılık zamanla değişmiyor" diye okunabilir. Oysa güç sınırlı. Ayrıca sonuç olumsuz olsa bile, olasılığın yüklenme dışındaki etkenlerle (ör. ETAS kümelenmesi) zamanla değişmesi bu sınamanın kapsamında değil.
Düzeltme: "Sonuç ne olursa" bölümüne şu cümle eklensin: "Bu sınavın hiçbir sonucu deprem olasılığı, zamanı ya da büyüklüğü hakkında bir ifade değildir; PIF/CMF pertürbasyonu, kara istasyonlarında doğrulanmamış bir model ekstrapolasyonudur." H0 ve ayırt edilemez sonuçları iki ayrı hüküm olarak yazılsın: H0 = "üst sınır X mm/yıl"; ayırt edilemez = "veri bu ayrımı yapamaz". İkisi aynı satırda birleşmesin.
VE-3'ten alınan "olay başına ≈0,005 nat" kaba ve doğrulanmamış bir el hesabı (VE.md d). Ön kayıtta sayı yerine "VE-3 formülüyle yeniden hesaplanır" yazılsın. README kural 6 (mutlak olasılık yazılmaz) korunuyor, iyi.

**B19 (düşük): H0 tanımı ile karar kuralı arasında uyumsuzluk.**
H0 "hızlar değişmedi" diye tanımlı, ama kural H0'ı reddetmiyor, iki tahmini karşılaştırıyor. H1 modeli yanlış işaretle öngörürse veri H0'ı reddetse bile hüküm "H1 yönünde" çıkmaz.
Düzeltme: Ayrı bir bilgi satırı eklensin: "model bağımsız değişim testi". χ² (Δv, C_obs) ile H0 altında p değeri verilir; hüküm satırına girmez. Bu AV-1'in asıl sorusunu da karşılar.

**B20 (düşük): Küçük düzeltmeler.**
- 2019 Silivri büyüklüğü kaynaklarda Mw 5,7–5,8 arasında; kaynak yazılsın.
- 90 gün ve 60 km eşiklerinin gerekçesi yazılsın.
- "SRCMOD dokuz modelin eşit ağırlıklı ortalaması": kaymaların ortalaması mı, öngörülerin ortalaması mı? Doğrusal elastik kısımda fark yok, ama afterslip/viskoz tepki için yazılsın. Tercihim öngörülerin ortalaması; ayrıca yayılım C_model'e girer (B3).
- Kural 5'teki "SHA-256 kayda" ifadesinde neyin hash'leneceği (PDF, parametre YAML'ı, steps.txt, istasyon listesi, kod) listelensin.

---

## Özet tablo

| # | Konu | Önem |
|---|---|---|
| B1 | En iyi H1 seçimi: çoklu karşılaştırma | yüksek |
| B2 | Alt sınır tanımı | orta |
| B3 | Tahmin yoğunluğu ve C_model | orta |
| B4 | Özarpacı 2021 (çevrimiçi 2020-11-19) kapıyı ihlal ediyor, veri örtüşüyor | yüksek |
| B5 | Hussain 2018 (2018-04-11) kapıyı ihlal ediyor | yüksek |
| B6 | Parametre aralıkları ve ileri model seçimi açık | yüksek |
| B7 | Model öngörüsü aynı tahminciden geçmiyor | orta |
| B8 | Seçim ölçütleri N'yi tahminen 1–3'e indiriyor | yüksek |
| B9 | Kutu, çerçeve ve istasyon sayısı tutarsız | orta |
| B10a | Ortak kip ve çerçeve serbestliği | orta |
| B10b | Atım kuralı çelişkisi, 2023 kirlenmesi | yüksek |
| B11 | Hedef ≈2017–2023; "bugünkü hız" ifadesi yanlış | orta |
| B12 | Hız tahmincisi seçilmemiş | orta |
| B13 | Güç testinde korelasyon, boşluk ve 1. tür hata yok | yüksek |
| B14 | Güç hangi H1'e karşı; 0,5–0,8 bandı belirsiz | orta |
| B15 | Gerçekçi σ ≈0,2–0,6 mm/yıl (kesin değil) | orta |
| B16a | Korelasyonda istasyon bootstrap'ı geçersiz | yüksek |
| B16 | Körlük beyanı eksik (ISTA tam seri, Özarpacı sonucu) | yüksek |
| B17 | "Tek doğrudan iz" aşırı iddia | orta |
| B18 | Olasılık yanlış okuması riski | orta |
| B19 | H0 ile karar kuralı uyumsuz | düşük |
| B20 | Küçük ayrıntılar | düşük |

Yeniden inceleme şartı: B1, B4, B5, B6, B8, B10b, B13, B16a ve B16 kapatılmış bir taslak (TASLAK-2).
