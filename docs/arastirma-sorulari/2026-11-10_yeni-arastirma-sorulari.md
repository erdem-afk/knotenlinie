# Yeni araştırma soruları: literatür boşluklarından Marmara M7+'ya (10 Kasım 2026)

Erdem'in isteği: elimizdekini birleştirmek ya da taklit etmek yetmez; daha önce yapılmamış, sınanabilir, İstanbul M7+ tahminine hizmet eden sorular. Bu belge yalnız tarama ve öneri. Hiçbir koşu başlatılmadı, makine kiralanmadı, 0 €. Seçim Erdem'in. Olasılık yazılmaz.

## Yöntem (Erdem yöntemi, 8 Kasım'ın üstüne)

- **Köprü sorusu:** iki literatür (A: bir fizik/veri alanı, B: tahmin sınama çekirdeği) birbirine atıf yapan işlerde buluşuyor mu? Ölçü: ikisine birden atıf yapan iş sayısı (k) ve Jaccard.
- **B çekirdeği** 8 Kasım'dakiyle aynı 5 makale (GEAR1, CSEP/RELM sınama, sınama altyapısı), sonuçlar karşılaştırılabilir.
- **Pozitif kontrol:** aynı B çekirdeğiyle bilinen yoğun köprüler. Sınama × ETAS (Ogata 1988) k 103, J 0,055; sınama × UCERF3 k 39, J 0,039.
- **Kalibrasyon:** OpenAlex'in bulut IP kotası bugün bitti, bu yüzden kaynak OpenCitations (anahtarsız). 8 Kasım köprüsü yeniden ölçüldü: kıta içi deformasyon × sınama J 0,0085 (OpenAlex'te 0,0093), ETAS kontrolü 0,055 (OpenAlex'te 0,061). İki kaynak ≈%90 uyumlu. OpenCitations kapsaması daha düşük (Ogata 1988: 1604 atıf, S2'de 2396).
- **Yeni:** atıf listeleri yerelde tutulduğu için üçlü kesişim ölçülebiliyor (A ∩ B ∩ C).
- **Kesişen işler okundu:** k küçükse işlerin başlığına bakıldı; "boşluk" sayılması için kesişen işlerin hiçbiri sorunun kendisini yapmamalı.
- Betik `tools/literatur/bosluk_olc_v3.py`, tohumlar `tohumlar_v3.json`, köprüler `kopruler_v3.json`, ham rapor `bosluk_rapor_v3.json` (bu klasör).

## Ölçüm tablosu

| Köprü | A atıf alanı | B | k | Jaccard | Okuma |
|---|---|---|---|---|---|
| Pozitif kontrol: sınama × ETAS | 368 | 1604 | 103 | 0,0551 | yoğun |
| Pozitif kontrol: sınama × UCERF3 | 368 | 671 | 39 | 0,0390 | yoğun |
| Kalibrasyon: kıta içi × sınama (8 Kasım) | 1526 | 368 | 16 | 0,0085 | ince (8 Kasım ile aynı) |
| **K1 sıçrama kuralları × sınama** | 1419 | 368 | **2** | 0,0011 | iki iş de sınama değil |
| K1b sıçrama kuralları × 2016+ çok parçalı olaylar | 1419 | 1370 | 206 | 0,0798 | yoğun kullanılıyor |
| K1d sıçrama kuralları × UCERF3 | 1419 | 671 | 139 | 0,0712 | tahmin kurmada kullanılıyor |
| **K1c sıçrama × 2016+ olaylar × sınama (üçlü)** | | | **0** | 0 | hiç yok |
| **K7 Türkiye segment tahminleri × sınama** | 951 | 368 | 7 | 0,0053 | hiçbiri Türkiye tahminini puanlamıyor |
| K7b Türkiye segment tahminleri × 2016+ olaylar | 951 | 1370 | 13 | 0,0056 | hiçbiri puanlamıyor |
| K2 mikrosismisite/kilit × sınama | 1199 | 368 | 12 | 0,0077 | ince |
| K2b mikrosismisite/kilit × ETAS | 1199 | 1604 | 50 | 0,0182 | orta |
| **K6 tarihsel deprem konumlama × sınama** | 719 | 368 | **1** | 0,0009 | tek iş, ilgisiz |
| K6 tarihsel × yenilenme modelleri | 719 | 801 | 20 | 0,0133 | ince |
| K6c tarihsel × türbidit | 719 | 653 | 51 | 0,0386 | yoğun |
| **K3 türbidit × sınama** | 653 | 368 | **1** | 0,0010 | tek iş, ilgisiz |
| K3 türbidit × yenilenme modelleri | 653 | 801 | 17 | 0,0118 | ince, çoğu dalma-batma |
| K9 sıçrama × türbidit | 1419 | 653 | 18 | 0,0088 | ince |
| K4 simülatör × sınama | 270 | 368 | 10 | 0,0159 | orta (simülatör doğrulama işleri var) |
| **K4b simülatör × türbidit** | 270 | 653 | **3** | 0,0033 | hiçbiri kalibrasyon değil |
| **K5 tekrarlayan deprem/yavaş kayma × sınama** | 1115 | 368 | **2** | 0,0014 | biri Parkfield tekrarlayan tahmini |
| K5b tekrarlayan × yenilenme | 1115 | 801 | 34 | 0,0181 | orta |
| Negatif örnek: mikrosismisite/kilit × sıçrama | 1199 | 1419 | 70 | 0,0275 | yoğun (sünen kesim bariyer: bilinen) |
| Karşılaştırma: Coulomb (Stein 1997) × sınama | 990 | 368 | 8 | 0,0059 | sınandı, bizde ≈0 verdi |

Sınır: tohum seçimi sonucu belirler; B çekirdeği küçük (368 iş), bu yüzden mutlak Jaccard düşük, asıl ölçüt aynı çekirdekle pozitif kontrole oran. Anahtar kelime aramasıyla doğrudan öncül taraması (Crossref) gürültülü; tam tarama OpenAlex kotası yenilenince (gece yarısı UTC) yapılmalı. Bulunan en yakın öncüller her sorunun altında.

## Sıralı sorular

Sıra ölçütü: İstanbul M7+ aralığının hangi kaynağına dokunuyor × boşluk kanıtı × bugün sınanabilir mi × maliyet. İstanbul aralığının payları (v1.5): uzamsal eksen %46, dal içi parametreler %37 (moment dalı %14, istatistik oranı %12, Parsons σ %6), tekrar %6.

### 1. Fay sıçrama kuralları yayımlandıktan sonraki depremleri doğru tahmin ediyor mu?

- **Soru:** Biasi ve Wesnousky 2016/2017'nin basamak ve büküm geçiş olasılıkları (katsayıları 2017'de donmuş), 2016 sonrası doğrultu atımlı kırılmalarda (Kaikoura 2016, Palu 2018, Ridgecrest 2019, Maduo 2021, Kahramanmaraş 2023, Myanmar 2025 ve diğerleri) hangi basamağın geçilip hangisinde durulacağını kalibre olasılıkla söylüyor muydu?
- **Boşluk kanıtı:** sıçrama kuralları 2016+ olay çalışmalarında (k 206) ve UCERF3'te (k 139) yoğun kullanılıyor, ama sınama çekirdeğiyle kesişim 2 (ikisi de sınama değil) ve üçlü kesişim 0. Pozitif kontrol k 39–103.
- **H1:** basamak genişliği ve büküm açısına bağlı yayımlanmış olasılıklar, geometriden bağımsız sabit geçiş oranına göre log skorda kazançlı ve kalibre. **H0:** kazanç yok ya da kalibre değil (ör. Kahramanmaraş'ın Narlı sıçraması gibi "imkânsız" geçişler beklenenden sık).
- **Sınanabilir mi, hangi veri:** evet, bugün. Açık veri: FDHI kırılma veritabanı (2019'a kadar), 2020–2025 olaylarının yayımlanmış yüzey kırığı haritaları. Tahmin edici yayımla dondurulmuş, olaylar ondan sonra: gerçek sözde-ileriye dönük sınav. Kör veri harcanmaz; Türkiye dışı 2026'ya dokunulmaz. Kahramanmaraş Türkiye 2016+ (mühür açık, geliştirme verisi).
- **İstanbul katkısı:** CMF+PIF ortak kırılma payı (v1.7'de f ≈ 0,10, yalnız 4/50 sonlu fay modelinden) ve Çınarcık–PIF, Kumburgaz, Ganos bükümleri doğrudan bu kurallarla hesaplanır. İstanbul'u Mw ≈7,0 tek parça ile Mw 7,3–7,6 ortak kırılma arasında belirleyen soru; moment dalını ve simülatör hattının segment birleşimini daraltır.
- **Maliyet/süre:** 0 €, 3–5 gün (≈30–60 basamak/büküm geçidini sayısallaştırmak). Güç: ≈40 geçit büyük kalibrasyon hatasını yakalar, küçüğünü yakalamaz.
- **Yenilik neden savunulabilir:** kurallar tahmin modellerine giriyor ama yayım sonrası olaylarla hiç puanlanmamış (üçlü kesişim 0). En yakın öncül: Biasi ve Wesnousky'nin kendi uyum çalışmaları (yayım öncesi veri).

### 2. Türkiye için yayımlanmış segment olasılıklarının karnesi

- **Soru:** 1997–2015 arasında yayımlanmış Türkiye segment tahminleri (Stein 1997, Nalbant 1998, Parsons 2000/2004, Hubert-Ferrari 2000, Erdik 2004, Pondard 2007, Doğu Anadolu Coulomb çalışmaları, ESHM13) 2016–2025 M6+ depremlerine (Elazığ 2020 Pütürge, Sisam 2020, Kahramanmaraş 2023 ×2, Marmara 2025 M6,2 ve diğerleri) olay öncesi ne kadar olasılık vermişti? Yenilenme/Coulomb ailesi düzleştirilmiş sismisiteyi ve Poisson tehlike haritasını geçti mi?
- **Boşluk kanıtı:** Türkiye segment tahminleri × sınama k 7 (Güney Kaliforniya Coulomb sınavı, derlemeler; Türkiye tahmini puanlayan yok); × 2016+ olaylar k 13 (hiçbiri puanlama değil).
- **H1:** segment/fizik tahminleri (yenilenme + Coulomb) olan segmentlere düzleştirilmiş sismisiteden fazla olasılık verdi. **H0:** vermedi.
- **Sınanabilir mi:** evet. Yayımlanmış tahminler sabit, olaylar sonradan. Türkiye 2016–2025 mühür açıldı, geliştirme verisi; bu tahminler modelimize hiç girmediği için onlar için örneklem dışı. Güç zayıf (N ≈6–9 olay), yalnız büyük farkı görür; önceden ateşleme kapısıyla (MDE) yazılmalı.
- **İstanbul katkısı:** İstanbul için literatürdeki geniş olasılık aralığının çoğu bu aileden. Ailenin Türkiye'de hiç karnesi yok. v1.3b zaman ekseninde Poisson 0,95 seçimini Türkiye'nin kendi verisiyle denetler; Coulomb kapalı 0,73 ağırlığını da.
- **Maliyet/süre:** 0 €, 3–5 gün (tablolardan olasılıkları ve segment sınırlarını sayısallaştırmak).
- **Yenilik:** yayımlanmış Türkiye tahminleri için ilk geriye dönük karne. Yakın öncül: Kaliforniya'da Coulomb tahminlerinin sözde-ileriye dönük sınavı (Strader ve Jackson 2015), Kagan ve Jackson'ın boşluk sınavları (Pasifik).

### 3. Mikrosismisite M7'yi yanlış yere mi koyuyor?

- **Soru:** Olgun doğrultu atımlı faylarda M≥3 arka plan sismisitesi sünen kesimlerde yüksek, kilitli kesimlerde düşük. ETAS'a orantılı uzamsal ağırlık M7 kırılmalarını sünen kesimlere mi yığıyor? Sünme düzeltmeli (ya da ters) sismisite haritası, M7 kırılma konumlarını segment ölçeğinde daha iyi tahmin ediyor mu?
- **Boşluk kanıtı:** mikrosismisite/kilit × sınama k 12 (J 0,0077), × ETAS 50. Bariyer bilgisi iyi bilinen ama (sünen kesim × sıçrama k 70) uzamsal tahmin ağırlığına çevrilip sınanmamış.
- **H1:** segment düzeyinde M7 kırılma uzunluğu payı, sünme düzeltmeli haritada ETAS-orantılıdan daha yüksek log olabilirlik alır. **H0:** ETAS-orantılı en az o kadar iyi (Kagan ve Jackson'ın boşluk sonucu bu yönde).
- **Sınanabilir mi:** evet; D3'ün 49 küresel doğrultu atımlı M7+ olayı, olay öncesi ISC kataloğu ve yayımlanmış sünme haritaları. Bu olaylar açık (geliştirme), kör veri harcanmaz.
- **İstanbul katkısı:** en büyük pay olan uzamsal eksen (%46). CMF'nin batısı sünüyor ve sismik, Kumburgaz doğusu kilitli ve sessiz (v1.8). H1 doğruysa ETAS 0,5 ağırlığı İstanbul önündeki kilitli kesimi küçümsüyor demektir.
- **Maliyet/süre:** 0 €, 4–6 gün.
- **Yenilik:** ılımlı. Schorlemmer ve Wiemer 2005 (Parkfield b-değeri) ve Kaneko 2010 yakın; ama M7 konumu için sınanmış uzamsal ağırlık olarak, çok faylı ve ön kayıtlı yapılmadı.

### 4. Tarihsel Marmara depremleri hangi segmentte kırıldı? Atama belirsizliğinin olasılığa yayılması

- **Soru:** 1509, 1719, 1766, 1894, 1912 olaylarının segment ataması makrosismik şiddet (Bakun–Wentworth, KAF'a 1912/1999 şiddetleriyle kalibre), türbidit ve tsunami kayıtlarının ortak olabilirliğiyle çözülürse, segment olasılıkları ve "Parsons mı Ambraseys mi" dalı nasıl değişir?
- **Boşluk kanıtı:** tarihsel konumlama × sınama k 1 (ilgisiz), × yenilenme 20; tarihsel × türbidit 51 (iki veri birbirini tanıyor ama olasılık sınamasına bağlanmamış).
- **H1:** ortak ters çözüm, bilinen kırıkları (1912 Ganos, 1999 İzmit, 1894?) birini dışarıda bırak sınavında tek kaynaktan daha iyi konumlar ve segment oranlarında Parsons–Ambraseys farkını daraltır. **H0:** daraltmaz.
- **Sınanabilir mi:** evet; Ambraseys şiddet tabloları, 1912 ve 1999 şiddetleri, derlenmiş 30 paleosismik çalışma. Pozitif kontrol: 1912 ve 1999 kırığı biliniyor.
- **İstanbul katkısı:** CMF/PIF'in son depremi ve olay sayısı buna bağlı; Parsons σ (%6) ve tekrar (%6). Poisson 0,95 olduğu için zamanlamadan çok oran üzerinden etki eder; orta.
- **Maliyet/süre:** 0 €, 1 hafta.
- **Yenilik:** Bakun–Wentworth Marmara'da tek tek uygulanmış olabilir; türbiditle ortak olabilirlik ve olasılığa yayılım yok.

### 5. Simülatörü paleosismik kayıtla olabilirlik tabanlı kalibre etmek

- **Soru:** MCQsim'in segment düzeyi sürtünmesini toplam orana değil, Marmara türbidit ve hendek kronolojilerinin olabilirliğine (yaklaşık Bayesçi hesap, ABC) uydurmak, segment olasılıklarındaki 16–35 katlık ayar farkını daraltır mı?
- **Boşluk kanıtı:** simülatör × türbidit k 3 (hiçbiri kalibrasyon değil); simülatör × sınama k 10 (doğrulama işleri var, kalibrasyon olabilirliği yok).
- **H1:** ABC sonsalı v2.1'in iki noktalı kalibrasyonundan EPICA ve 2016–25 tutarlılık satırlarında iyi. **H0:** değil.
- **Sınanabilir mi:** evet, ama bilinen veriyle tutarlılık; asıl sınav 2027 ileri testi.
- **İstanbul katkısı:** v2.x hattının segment düzeyi belirsizliği; Y2 (simülatör kalibrasyonu) önerisinin yeni versiyonu.
- **Maliyet/süre:** 3–10 € (kiralık makine), 1–2 hafta. Makine gerektirdiği için en çok Erdem onayına bağlı olan bu.
- **Yenilik:** RSQSim/UCERF3 kıyasları var; paleosismik kronolojiyi doğrudan olabilirlik olarak kullanan simülatör kalibrasyonu yok.

### 6. Havzalar arası türbidit eşzamanlılığı ortak kırılmayı ölçüyor mu?

- **Soru:** Çınarcık, Orta ve Tekirdağ havzalarındaki türbidit yaşlarının eşzamanlılığı CMF+PIF ortak kırılma payını (f) kısıtlayabilir mi, yoksa tarihleme çözünürlüğü (±50–150 yıl) bunu imkânsız mı kılar?
- **Boşluk kanıtı:** sıçrama × türbidit k 18, türbidit × sınama k 1. Eşzamanlılık Cascadia'da tartışıldı, doğrultu atımlı ortak kırılma oranı olarak sınanmadı.
- **H1:** eşzamanlılık f'yi v1.7'nin 0,05–0,15 aralığından dar kısıtlar. **H0:** çözünürlük yetmez (önce sentetik çözünürlük testi; yetmezse iş kapanır).
- **Sınanabilir mi:** kısmen; önce sentetik test.
- **İstanbul katkısı:** 1. soruyla aynı hedef (ortak kırılma), bağımsız veri. 1 ile birlikte yürür.
- **Maliyet/süre:** 0 €, 2–3 gün (sentetik test 1 gün).
- **Yenilik:** Marmara türbidit kayıtları var ama ortak kırılma olasılığına bağlanmadı.

### 7. Asismik kayma geçicileri büyük deprem olasılığını modüle ediyor mu (doğrultu atımlı)?

- **Soru:** Tekrarlayan depremlerden çıkan kayma hızı ivmelenmeleri, Uchida 2016'nın dalma-batmada gösterdiği gibi, doğrultu atımlı faylarda (Parkfield, Hayward, Marmara) M5+ oranını ETAS'ın üstünde artırıyor mu?
- **Boşluk kanıtı:** tekrarlayan/yavaş kayma × sınama k 2 (Parkfield tekrarlayan deprem tahmini ve bir sinir ağı işi); × yenilenme 34.
- **H1:** ivmelenme dönemlerinde M5+ olasılık kazancı ETAS'a göre > 0. **H0:** yok.
- **Sınanabilir mi:** Kaliforniya'da evet (NCEDC tekrarlayan kataloğu); Marmara kataloğu kısa.
- **İstanbul katkısı:** dolaylı, kısa vade. M7 için gücü yok; CMF'de yarın bir hızlanma görülürse ne demek olduğunu söyler.
- **Maliyet/süre:** 0 €, 1 hafta.
- **Yenilik:** dalma-batmada var, doğrultu atımlıda sınama olarak yok.

## Önerilen sıra

1 ve 2 önce ve paralel: ikisi de 0 €, bugün sınanabilir, boşluk en net (üçlü kesişim 0 ve "hiç karne yok"), İstanbul'a doğrudan dokunuyor. 6, 1'in yanına 1 günlük sentetik testle eklenir. 3 ardından (en büyük pay, ama yenilik iddiası ılımlı). 4 ve 7 boşta. 5 makine istediği için en son ve ayrıca onay ister.

Her biri ön kayıtla başlar (kural, ateşleme kapısı, rakip önceden donar); sonuç yeni sürüm olarak ileri test defterine rakip girer, v1.3b değişmez.

## Neyi yapmadık

Hiçbir soru koşulmadı. Kör veri (Türkiye dışı 2026) okunmadı. OpenAlex kotası yenilenince doğrudan öncül taraması tamamlanmalı (özellikle 1, 2 ve 3 için).
