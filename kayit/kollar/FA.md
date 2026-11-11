# Kol FA — fay ağı ve kabuk mekaniği (11 Kasım 2026)

Yalnız tasarım; koşu yok. Alt ajan aracı bu oturumda yoktu, tarama tek elden yapıldı (ORTAK-BRIEF'ten tek sapma).
Hiçbir aday "çalışır" değildir; her biri sınama önerisidir. Mutlak İstanbul olasılığı yazılmadı.

## (a) Tarama özeti

Aranan beş başlık: (1) deprem döngüsü modellerinde veri asimilasyonu, (2) simülatörde kümelenme / koşullu tehlike, (3) nükleasyon–hazırlık evresi ve laboratuvar ML, (4) tam dinamik kırılma + döngü (Marmara), (5) akışkan / gözenek basıncı / gaz.
Yöntem: WebSearch + Crossref (DOI çözümü; 78 DOI'nin tümü Crossref, doi.org ya da Zenodo API'de çözüldü) + köprü ölçüsü `bosluk_olc_v3.py` (OpenCitations; SINAMA tohumu v3 ile aynı, 368 atıf yapan iş). Ham rapor: `/tmp/claude-0/-home-user/7ac1c2ea-b572-5451-8a86-ec49a317416b/scratchpad/fa/out/bosluk_rapor_v3.json` (geçici; tohumlar aynı dizinde `tohum.json`).

| Köprü | boylar | k | Jaccard | okuma |
|---|---|---|---|---|
| POZ sınama × ETAS (pozitif kontrol) | 368 / 1604 | 103 | 0,0551 | v3 ile aynı |
| POZ simülatör × sınama | 270 / 368 | 10 | 0,0159 | v3 ile aynı |
| F1 veri asimilasyonu × sınama | 85 / 368 | **1** | 0,0022 | tek iş ilgisiz (Karaca 2021, Monte Carlo sismisite) |
| F1b veri asimilasyonu × simülatör | 85 / 270 | 6 | 0,0172 | 3'ü blok-fay derlemesi, 3'ü DA'nın kendisi |
| F1d veri asimilasyonu × Marmara modelleri | 85 / 218 | 1 | 0,0033 | derleme; Marmara'da DA yok |
| F2 süperdöngü × simülatör | 235 / 270 | 9 | 0,0181 | Hatem 2021, Barani 2025, Field 2025 yol haritası |
| F2b süperdöngü × sınama | 235 / 368 | 5 | 0,0084 | hiçbiri skorlu sınav değil |
| F2c süperdöngü × yenilenme | 235 / 801 | 44 | 0,0444 | istatistik tarafı dolu |
| **F2d süperdöngü × simülatör × sınama** | — | **0** | 0 | üçlü boş |
| F3 lab-ML × sınama | 615 / 368 | 5 | 0,0051 | derlemeler (Mizrahi 2024), deprem sınavı yok |
| F3c hazırlık evresi × sınama | 973 / 368 | 4 | 0,0030 | |
| F3d hazırlık evresi × ETAS | 973 / 1604 | 64 | 0,0255 | boşluk değil; ETAS'la zaten yüzleşmiş |
| F3e lab-ML × hazırlık evresi | 615 / 973 | 52 | 0,0339 | iç içe |
| F4 SEAS/dinamik döngü × sınama | 284 / 368 | 2 | 0,0031 | ikisi de PSHA derlemesi |
| F4b SEAS × Marmara modelleri | 284 / 218 | 3 | 0,0060 | |
| F4c Marmara modelleri × sınama | 218 / 368 | **0** | 0 | |
| F4d SEAS × simülatör | 284 / 270 | 43 | 0,0841 | aynı topluluk |
| F5 Marmara akışkan/gaz × sınama | 169 / 368 | **0** | 0 | |
| F5b Marmara akışkan × fay vanası | 169 / 888 | 2 | 0,0019 | |
| F5c fay vanası × sınama | 888 / 368 | 0 | 0 | |

Başlık başına bulgu:

1. **Veri asimilasyonu.** van Dinther 2019 (EnKF, 2B yitim, sentetik), Hirahara–Nishikiori 2019 (EnKF, uzun süreli yavaş kayma, sentetik), Diab-Montero 2023 ve 2025 (EnKF / parçacık akışı, tek fay ve Burridge–Knopoff, sentetik), Banerjee 2023 (parametre yanlılığı durumu bozar), Kaveh 2024 ve 2025 (indirgenmiş model + EnKF, sentetik). Hepsi "kusursuz model ikiz deneyi". Gerçek veriyle tek örnek Kano 2020: 2003 Tokachi-oki deprem sonrası kayması, GNSS, yitim; tahmin edilen şey sonraki olay zamanı değil, deprem sonrası deformasyon. **Gerçek veriyle bir sonraki depremin zamanını daraltan ve skorlanan iş bulunamadı; doğrultu atımlı kıta içi fayda hiç yok; Marmara'da yok.** Werner 2011 parçacık filtresini yenilenme süreçlerine uygular (fizik yok).
2. **Kümelenme / koşullu tehlike.** İstatistik tarafı dolu (Salditch 2020 uzun vadeli fay belleği, Griffin 2020, Biasi–Scharer 2019, Barani 2025). Simülatör tarafında en yakın işler: Howarth 2021 (Alpine Fayı göl kaydı + fizik tabanlı simülatör, koşullu olasılık; skor yok, rakip yok — özetten), Marschall 2026 (SCEC posteri, DOI yok: RSQSim, Hayward–Calaveras üç hendek sitesinin tekrar ve kovaryansını aynı anda üretemiyor), Gilchrist 2017 (AGU özeti: RSQSim koşullu olasılıkları UCERF3 ile kıyas, paleosismik sınav yok). Açık kataloglar var: RSQSim Kaliforniya 715 bin yıl ve Yeni Zelanda 276 bin yıl (Zenodo).
3. **Hazırlık evresi / lab ML.** Laboratuvarda sağlam (Rouet-Leduc 2017, Hulbert 2019, Johnson 2021 yarışması, Laurenti 2022, Borate 2023). Doğaya taşınanlar: Cascadia yavaş kayması (Rouet-Leduc 2019, Hulbert 2020) ve Kīlauea kaldera çöküşleri (McBrearty–Segall 2024; ≈1 günlük yarı-periyodik döngü). **Tektonik M6+ depremde skorlu başarı yok.** Bletery–Nocquet 2023'ün 2 saatlik GNSS öncü sinyali ortak-kip gürültü süzgeciyle kayboluyor; yazarların 2025 yanıtı sinyali "destekleniyor ama kanıtlanmadı" diye bırakıyor. Marmara'da geriye dönük hazırlık anlatıları var (Bouchon 2011 ile Ellsworth–Bulut 2018 aynı İzmit verisini zıt okur; Malin 2018; Durand 2020; Kwiatek 2023). Mignan–Broccardo 2020: sinir ağı tahminleri basit taban modellere üstünlük göstermedi.
4. **Tam dinamik + döngü.** SEAS (Erickson 2020, Jiang 2022) ve Tandem (Uphoff 2022) kod doğrulamasıdır, tahmin sınavı değil. Lambert–Lapusta 2021: uzun dizilerde tekil olay zamanları sayısal çözünürlüğe duyarlı, yalnız istatistikler sağlam. Marmara: Oglesby–Mai 2012 ve Aochi–Ulrich 2015 (tek olay senaryoları), Sopacı–Özacar 2023 (yay-kaydırıcı, 2019 Mw 5,8'in saat ilerlemesi), **Güvercin–Barbot 2025** (Unicycle, 10 000 yıl, ısıl yapı + çökel kalınlığı; yayım 4 Aralık 2025; tam metne erişilemedi, özet + basın bülteninden: doğu segmentlerinde M6,2–6,8 çiftleri ≈100 yılda bir, M7,0 ≈500 yılda bir), Osei-Tutu 2026 (yalnız EGU özeti, PyQuake3D, yarı-dinamik, Adalar çek-ayır havzası). Hiçbiri ileriye dönük skorlanmadı (F4c k = 0).
5. **Akışkan / gaz.** Gaz çıkışı ve sığ gazla ilişkili mikro-sismisite belgeli (Géli 2008, 2018; Batsi 2018; Tary 2019; Embriaco 2013). Sınanmış tek zaman değişimi: Martínez-Garzón 2023, Armutlu hidrotermal bölgesinde deniz seviyesiyle mevsimlik mikro-deprem hızı. Fay dayanımının zamanla değiştiğini gösteren çok yıllı gözenek basıncı ya da gaz akısı serisi yok (2018 piyezometre kaydı yalnız kongre özeti). Zhu 2020 fay vanası modeli yalnız simülasyon.

## (b) Aday tablosu

### FA-1 — MCQsim ikiz deneyi: öngörülebilirlik tavanı (öner)
- **Soru:** Marmara fay ağında, paleosismik kalitede bir olay geçmişi (segment + tarih ± hata, eksik olaylar) verildiğinde simülatör durumu bir sonraki M7+ zamanını Poisson'a göre kaç nat daraltabilir; bu tavan 1, 5, 10, 30 yıl ufkunda ne?
- **Neden yeni:** van Dinther 2019 (10.1093/gji/ggz063), Diab-Montero 2023 (10.1093/gji/ggad154), Kaveh 2025 (10.1093/gji/ggaf518) ikiz deneyleri tek/ideal fayda, jeodezi benzeri gözlemle, nat skoru ve Poisson rakibi olmadan. Gerçek bir bölgenin 3B fay ağında, paleosismik gözlem operatörüyle, parametre hatası altında tavan ölçümü yok (F1 k = 1). Defterdeki SIM-V2 dersi tek segment yenilenme (BPT) içindi; bu, çok segmentli geçmişe koşullamadır.
- **Zaman ekseni:** yıl–on yıl; M7+ (ikincil M6,5+). Aday bir tahmin değil, tahminin üst sınırıdır.
- **Tasarım:** mevcut v2.4abc katalogları üzerinde "analog eşleme" (yeni simülasyon gerekmeyebilir): bir katalogdan "doğru" pencere seçilir, gözlem operatörü uygulanır (tarih hatası 1500 öncesi ±50 yıl, 1500–1900 ±5, sonrası 0; kaçırma olasılığı), kalan topluluktan son K olayı eşleşen pencereler ağırlıklanır, sonraki M7+ zamanının dağılımı skorlanır. İki düzey: (i) aynı parametre (üst sınır), (ii) farklı sürtünme çekimi (gerçekçi model hatası). H1: (ii)'de 10 yıl ufkunda bilgi kazancı ≥ 0,10 nat/pencere. H0: < 0,05 → hat **kalıcı kapanır** (gerçek veri asimilasyonu, FA-5 dahil). Rakipler: aynı hızlı Poisson, BPT, son-olaydan-beri-süre tablosu.
- **N ve güç:** sentetik; pencere sayısı serbest (≥ 2000), güç sorun değil. Asıl risk parçacık yozlaşması (ABC ESS 16,6) ve katalog uzunluğu.
- **Sızıntı:** yok (sentetik). Kural (K, eşik, ufuklar, gözlem hataları) koşudan önce dondurulur.
- **Veri:** sunucudaki MCQsim katalogları; yeni veri yok.
- **Maliyet/süre:** 0 EUR; 2–4 gün (yalnız ardıl işleme). Katalog kısa kalırsa ek koşu gerekir.
- **Tür:** fizik.
- **Hüküm: öner.** Ucuz ve iki sonucu da karar verdirici; olumsuz çıkarsa pahalı asimilasyon hattını tümüyle kapatır. Beklentim: segment düzeyi 16–35 kat sürtünme duyarlılığı nedeniyle (ii) düzeyi H0'a yakın çıkar.

### FA-2 — Açık simülatör kataloglarından koşullu tehlike × gerçek paleosismik diziler (öner)
- **Soru:** Fizik tabanlı simülatörün ürettiği koşullu aralık dağılımı (önceki aralık(lar) ve komşu kesim kırılmaları verildiğinde sonraki olay) gerçek uzun paleosismik dizilerde Poisson'u ve istatistik küme modellerini log skorda geçiyor mu?
- **Neden yeni:** Howarth 2021 (10.1038/s41561-021-00721-4) Alpine Fayı'nda simülatör + göl kaydıyla koşullu olasılık verir ama skor ve rakip yok; Marschall 2026 (SCEC posteri) yalnız nitel uyumsuzluk bildirir; Salditch 2020 (10.1016/j.tecto.2019.228289) ve Barani 2025 (10.1038/s43247-025-02608-3) istatistik modeldir. Üçlü köprü süperdöngü × simülatör × sınama k = 0. EL-8'den farkı: RSQSim koşulmaz, yayımlanmış açık kataloglar veri olarak kullanılır.
- **Zaman ekseni:** on yıl; M7+. Kazanç çıkarsa aynı koşullu tablo MCQsim'den Marmara için türetilip ileri test defterine rakip girer.
- **Tasarım:** site başına ortalama aralık bir-dışarıda bırakılarak sabitlenir (hız sızıntısı kapanır); simülatörün aynı fay kesimindeki M ≥ 7 kırılmalarından koşullu yoğunluk çıkarılır; her gerçek aralık skorlanır. H1: simülatör-koşullu − Poisson > 0 nat/aralık (tek yanlı, 2σ). Rakipler: Poisson, BPT (α 0,5), Weibull (k < 1), uzun vadeli fay belleği. Tarih hatası olasılık dağılımı olarak taşınır.
- **Hedef küme ve N:** Kaliforniya (Wrightwood, Pallett Creek, Frazier Mountain, Hog Lake, Tyson Lagoon ≈ 80–90 aralık) + Yeni Zelanda (Hokuri Creek 24 olay, Alpine göl kayıtları, Hope/Wellington ≈ 60) ≈ **140–150 aralık**.
- **Güç:** aralık başına skor farkı SS ≈ 1 nat alınırsa SH ≈ 0,085; 2σ ile ancak ≥ 0,17 nat/aralık görülebilir. Daha küçük etki **önceden ayırt edilemez**. ZAMAN-BPT'de BPT −0,58 nat/olay kaybetti; RSQSim'in dar aralık dağılımı aynı yönde kaybedebilir (bu da bilgidir).
- **Sızıntı:** simülatör hızları paleosismik hızlara ayarlı (ortalama sızıyor, bu yüzden ortalama sabitlenir; koşullu yapı sızmıyor). Bu siteler ZAMAN-BPT sınavında görüldü; yeni model için ayar yapılmadığından kabul edilebilir, ama kural kataloglar açılmadan önce dondurulmalı. Kör veri değil (tarih öncesi kayıt).
- **Veri:** açık. RSQSim Kaliforniya 4983 (10.5281/zenodo.5542222; `catalog_m6.5.csv` 0,03 GB, tümü ≈ 30 GB) ve Yeni Zelanda 5091 (10.5281/zenodo.5534462; 2,8 GB). Paleosismik tarihler: UCERF3 Ek G ve yayımlar (Scharer 2010, Lienkaemper 2010, Berryman 2012).
- **Maliyet/süre:** 0 EUR; 4–6 gün.
- **Tür:** fizik (istatistik ağırlıklı).
- **Hüküm: öner.** Güç sınırda; FA-1'den sonra koşulmalı (FA-1 tavanı düşükse beklenti de düşer).

### FA-3 — Güvercin–Barbot 2025 model çıktılarının karnesi ve M6+ çift (doublet) savı (bekle)
- **Soru:** Yayımlanmış Unicycle Marmara modelinin segment tekrar süreleri ve "doğu segmentlerinde M6,2–6,8 çiftleri" savı ileri test defterine sayısal rakip olarak yazılabilir mi; çift savı ETAS'ın ötesinde yıl ölçeğinde koşullu bilgi taşıyor mu?
- **Neden yeni:** 10.1038/s43247-025-03007-4 ileriye dönük skorlanmadı (F4c k = 0); Sopacı–Özacar 2023 (10.1016/j.tecto.2023.229888) tek yay-kaydırıcı; Oglesby–Mai 2012 (10.1111/j.1365-246X.2011.05289.x) tek olay senaryosu. DK-3'ten farkı: hedef M6 → M7 değil, reolojik bariyerin ürettiği M6 → M6 eşleşmesi ve yıl–on yıl gecikmesi.
- **Zaman ekseni:** yıl–on yıl; **M6+** (yedek hedef).
- **Tasarım:** (i) literatür/veri: model katalogu elde edilir, segment tekrar ve çift gecikme dağılımı MCQsim v2.4abc ile aynı niceliklerde kıyaslanır; (ii) çift savı Türkiye dışı kıta içi doğrultu atımlı M6–6,9 olaylarında ETAS'a karşı skorlanır. H0: ETAS'a göre kazanç ≤ 0 (DK-3 dersi bunu öngörür).
- **N ve güç:** hesaplanmadı; küresel katalog sayımı ön koşul. Marmara'da on yılda beklenen hedef olay ≈ 0–1: Marmara içi sınav **güçsüz**.
- **Sızıntı:** makale Aralık 2025'te çıktı; Nisan 2025 Marmara depremi ondan önce, o olay için ileriye dönük sayılmaz.
- **Veri:** veri/kod erişim beyanı okunamadı (tam metin açılmadı); Unicycle açık kaynak.
- **Maliyet/süre:** 0 EUR; 2 gün (i), 3–4 gün (ii).
- **Tür:** literatur + veri.
- **Hüküm: bekle.** (i) ucuz ve defter için yararlı; (ii) ancak model katalogu elde edilirse ve N sayımı güç verirse açılır.

## (c) Elenenler

| Kimlik | Fikir | Neden |
|---|---|---|
| FA-4 | Lab-ML kalan süre tahminini Marmara tekrarlayan depremlerine taşımak | Hedef M < 3; M6+/M7+ zaman eksenine dokunmuyor, sürekli dalga biçimi yükü ağır. Doğada yalnız yavaş kayma ve kaldera çöküşünde çalıştı. |
| FA-5 | Gerçek GNSS/tekrarlayan veriyle MCQsim durum asimilasyonu (EnKF / parçacık filtresi) | Gerçek veriyle olay zamanı sınavı hiçbir yerde yok; PIF karadan görülmüyor (Y-1 dersi). FA-1 tavanı H1 vermeden açılmaz. |
| FA-6 | Hazırlık evresi göstergeleriyle (hızlanan ön-kayma, öncü sismisite) alarm | Boşluk değil (hazırlık × ETAS k = 64); S-7 ve DT-2 aynı mekanizmayı kapattı; Bletery sinyali tartışmalı. |
| FA-7 | Kendi tam dinamik döngü modelimiz (Tandem / PyLith / Unicycle) | Olay zamanları çözünürlüğe duyarlı (Lambert–Lapusta 2021); makine kiralama yasak; K10 şartı sağlanmadı. |
| FA-8 | Gözenek basıncı / gaz çıkışıyla zamana bağlı fay dayanımı | Veri yok: çok yıllı deniz tabanı piyezometre ya da gaz akısı serisi yayımlanmadı; sınanan tek etki mevsimlik mikro-sismisite. |

## (d) Dürüst sınır

- Bu kolda yıl ölçeğinde M7+ zamanını daraltacağına dair sınanmış tek bir fizik yöntemi bulunmadı. Veri asimilasyonu literatürü tümüyle sentetik; lab ML tektonik depreme taşınamadı; Marmara döngü modelleri skorlanmadı.
- FA-1 bir tavan ölçümüdür; H1 çıksa bile gerçek dünyada kazanç bundan küçük olur. FA-2'nin gücü ancak ≥ 0,17 nat/aralık etkiye yeter.
- Köprü ölçüleri OpenCitations kapsamasıyla (≈ %65–70) sınırlı; k = 0 "hiç iş yok" değil, "atıf kesişimi yok" demektir. Web taraması tek geçişti; SCEC/EGU özetleri hakemli değil.
- Özetten/ikincil kaynaktan işaretlenenler: Güvercin–Barbot 2025 (özet + basın bülteni), Howarth 2021, Marschall 2026 ve Gilchrist 2017 (kongre özetleri), Osei-Tutu 2026 (EGU özeti), Bletery–Nocquet 2025 (özet). Diğer kaynaklar da tam metinden değil, başlık/özet düzeyinde ve önceki bilgiyle kullanıldı; sayısal ayrıntıları koşudan önce tam metinden doğrulanmalı.
- FA-2 site sayıları ve N kabadır (tek tek sayılmadı); FA-3 için N hiç hesaplanmadı.
