# Doğrudan öncül taraması, sorular 1–3 (OpenAlex, 10 Kasım 2026)

Yarım kalan iş: `2026-11-10_yeni-arastirma-sorulari.md` sonundaki "OpenAlex kotası yenilenince doğrudan öncül taraması tamamlanmalı (1, 2, 3)". Anahtar (Doppler `knotenlinie/prd`, `OPENALEX_API_KEY`) çalışıyor; değer hiçbir dosyaya ya da loga yazılmadı. Yeni koşu yok, makine yok, 0 €. Olasılık yazılmaz.

## 1. OpenCitations kesişimlerinin OpenAlex ile yeniden ölçümü

Aynı tohumlar (`tohumlar_v3.json`), aynı köprüler. Betik `tools/literatur/oa_kesisim.py`, rapor `oncul/oa_kesisim_rapor.json` (kesişen işler başlıklarıyla).

| Köprü | OpenCitations k / J | OpenAlex k / J | Okuma |
|---|---|---|---|
| Pozitif kontrol sınama × ETAS | 103 / 0,055 | 164 / 0,061 | yoğun, tutuyor |
| Pozitif kontrol sınama × UCERF3 | 39 / 0,039 | 56 / 0,044 | yoğun |
| Kalibrasyon kıta içi × sınama | 16 / 0,0085 | 22 / 0,0093 | 8 Kasım ile aynı |
| K1 sıçrama × sınama | 2 / 0,0011 | 10 / 0,0044 | 10'un 5'i UCERF2/3 raporu, biri OEF derlemesi; hiçbiri sıçrama kuralını sınamıyor |
| K1c sıçrama × 2016+ olay × sınama | 0 | 1 | tek iş (Chaman InSAR, 2021), sınama değil |
| K7 TR segment tahmini × sınama | 7 / 0,0053 | 10 / 0,0058 | hiçbiri Türkiye tahminini puanlamıyor |
| K7b TR segment × 2016+ olay | 13 / 0,0056 | 15 / 0,0054 | hiçbiri puanlama değil |
| K2 mikrosismisite/kilit × sınama | 12 / 0,0077 | 20 / 0,0101 | ALM (Wiemer–Schorlemmer 2007, İtalya 2010) burada çıktı, aşağıda |
| K3b türbidit × sınama | 1 | 1 | aynı |
| K4b simülatör × türbidit | 3 | 4 | aynı |
| K5 tekrarlayan × sınama | 2 | 4 | aynı sıra |
| K6b tarihsel × sınama | 1 | 4 | aynı sıra |
| K8 Coulomb × sınama | 8 | 40 | Coulomb tohumlarında OpenAlex kapsaması çok daha geniş |

Sonuç: OpenAlex kapsaması %30–60 daha büyük, ama oranlar ve sıralama aynı. Hiçbir "boşluk" köprüsü pozitif kontrol düzeyine çıkmadı. v3 tablosunun okumaları geçerli.

## 2. Anahtar kelime ile doğrudan öncül arama

Her soru için 5 sorgu (OpenAlex `search`, ilk 25), artı 15.473 atıf yapan işin başlığında düzenli ifade taraması. Ham çıktı `oncul/oncul_arama.json`, okunan özetler `oncul/oncul_ozet.json`.

### Soru 1: sıçrama kuralları yayım sonrası depremlerde

En yakın öncüller:

- **Rodriguez Padilla, Oskin, Brodsky, Dascher-Cousineau 2024, GRL** (10.1029/2024gl109957): 31 doğrultu atımlı yüzey kırığında basamak, büküm, boşluk geçişlerini sayıp geometriye bağlı geçiş olasılığı modeli kuruyor (1,2 km basamak ve 32° büküm yarı yarıya geçiliyor; kırılmaların ≈%20'si düz kesimde duruyor). 2016 sonrası olayları içeriyor ama **uydurma**, donmuş kuralın yayım sonrası sınavı değil. Bizim S1 bulgusuyla (kırılmalar BW'nin beklediğinden sık geçiyor) aynı yönde.
- **Hara ve Toda 2026, Earth Planets Space** (10.1186/s40623-026-02567-9): BW tipi geçiş olasılıklarını 2023 Kahramanmaraş için geriye dönük uyguluyor. Tek olay; Elbistan kırılmasının geometrice avantajlı Sürgü'yü atlayıp Doğanşehir'e gittiğini, yani kuralın orada tutmadığını yazıyor. Puanlama/log skor yok.
- **Biasi ve Wesnousky 2021, BSSA** (10.1785/0120200370): kendi kurallarının güncellenmiş hali, erken uyarıda kırılma uzunluğu olasılığı. Yayım öncesi veriyle; sınama değil.
- Michel ve diğ. 2026 JGR (rate-state sıçrama ölçütü, yalnız simülasyonla sınanıyor); Scott ve diğ. 2023 Geosphere (fay haritasının kırık konumunu tahmini, sıçrama değil).

Hüküm: **boşluk daraldı ama kapanmadı.** Çok olaylı, donmuş katsayılı, ön kayıtlı sözde-ileriye dönük puanlama (bizim S1) yayımlanmış değil. Ama yenilik iddiası "ilk kez sıçrama kuralı yeni olaylarla karşılaştırıldı" olamaz: Hara–Toda tek olayda, Rodriguez Padilla uydurmada bunu yapıyor. Savunulabilir iddia: "ilk ön kayıtlı, çok olaylı, olasılık puanlamalı (log skor + kalibrasyon) sınav". S1 sonucunu yazarken bu üç iş anılmalı; Rodriguez Padilla 2024 modeli ikinci rakip olarak eklenebilirdi (S1 kuralı dondu, bu yalnız not).

### Soru 2: yayımlanmış Türkiye segment olasılıklarının karnesi

En yakın öncüller:

- **Vural 2026, EGUsphere ön baskı** (10.5194/egusphere-2026-5171): Türkiye'de 1990–2026 arası 46 Mw≥6 depremin Coulomb gerilmesini 6.970 alt segmente çözüp sonraki sismisiteye karşı sözde-ileriye dönük sınıyor (segment ağırlıklı AUC 0,711; olay eşit 0,589 ± 0,112, etkin örnek 42). Bu **Coulomb ailesinin Türkiye karnesine** doğrudan öncül. Ama yayımlanmış yenilenme olasılıklarını (Parsons, Stein, Erdik, Murru) puanlamıyor; kendi ürettiği gerilme haritasını sınıyor. Ayrıca not: GEM Global Active Faults'ta İstanbul güneyindeki KAF kolunda rake 180° ters kayıtlı, Coulomb işaretini çeviriyor (bizim Coulomb hattı GEM rake'i kullanıyorsa denetlenmeli).
- **Karaca 2020** (10.7240/jeps.526906): KB Türkiye'de düzleştirilmiş sismisite, PI ve RI yöntemlerinin ROC karşılaştırması. İstatistik yöntemler, segment tahmini değil.
- **Toda ve Stein 2024 SRL** (10.1785/0220230252): Kahramanmaraş dizisi için bir yıllık Coulomb tahmini; ileriye dönük, puanlama yok.
- **Murru, Akıncı ve diğ. 2016 JGR** (10.1002/2015jb012595): Marmara M≥7 segment tahmini. Puanlanacak tahminlerden biri (2016'da yayımlandı; 2016–25 Marmara M7 yok, katkısı yalnız "olay yok" satırı).
- Ağdaş 2026 (Doğu Anadolu, 7 günlük ML, sızıntı denetimli), Alhan ve Khabat 2026 (Marmara, ML ve ETAS, sızıntı denetimli), Karagöz ve diğ. 2026 (İstanbul ML): kısa vade, segment olasılığı değil.

Hüküm: **boşluk duruyor.** 1997–2016 arası yayımlanmış Türkiye segment/yenilenme olasılıklarını 2016–25 olaylarıyla puanlayan iş bulunmadı. Vural 2026 Coulomb kısmında yakın öncül; S2 sonucunda anılmalı. S2'nin kendi bulgusu (açık literatür yalnız Marmara M7, olay yok, ayırt edilemez) değişmiyor.

### Soru 3: mikrosismisite M7'yi yanlış yere mi koyuyor?

En yakın öncüller:

- **Wiemer ve Schorlemmer 2007 ALM** ve **Gulia ve diğ. 2010 İtalya** (asperite tabanlı olabilirlik modelleri; RELM/CSEP'te sınandı): düşük b-değerli kesimleri büyük deprem yeri sayan, sınanmış uzamsal tahmin. b-değeri kullanıyor, sünme düzeltmesi ya da ters sismisite değil.
- **Mousavi ve diğ. 2026, arXiv** (10.48550/arxiv.2605.23494): Alborz'da b-değeri ve arka plan oranı μ'nün uzamsal tahmin gücü; μ güçlü, b yalnız M≳5,3'te pozitif. Bölgesel, M4–5.
- **Ostapchuk ve Nugmanov 2026** (Kamçatka): arka plan sismisitesi kümeleri asperiteleri gösteriyor (dalma-batma, sınama yok).
- Harris 2017 (sünen faylar derlemesi), Jiang ve Lapusta 2017 (kilitlenme derinliği ve mikrosismisite, model).

Hüküm: v3'teki "yenilik ılımlı" okuması doğru, öncül listesine **ALM** eklenmeli. Çok faylı, küresel M7 doğrultu atımlı kırılmalarla, ters/sünme düzeltmeli sismisite ağırlığının ön kayıtlı sınavı bulunmadı. S3 sonucu (H0: ters −0,52 ± 0,28, tekdüze +0,23 ± 0,14, ayırt edilemez) Mousavi 2026'nın "μ güçlü uzamsal sinyal" bulgusuyla çelişmiyor.

## Neyi değiştirir

- S1–S3 sonuçlarının hükmü değişmez; yalnız yenilik cümleleri ve öncül listeleri.
- S1: "ilk sınav" değil, "ilk ön kayıtlı çok olaylı olasılık puanlaması"; Hara–Toda 2026 ve Rodriguez Padilla 2024 anılır.
- S2: Vural 2026 Coulomb karnesi anılır; GEM rake hatası Coulomb girdilerimizde denetlenecek bir not.
- S3: ALM ve Gulia 2010 öncül olarak eklenir.

## Sınırlar

Anahtar kelime araması dil ve terim seçimine bağlı; Türkçe dergiler ve kapalı erişimli kitap bölümleri eksik kalabilir. Nas ve diğ. 2024 (KAF koşullu olasılıklar) ve Talbi ve diğ. 2019 (Türkiye olaylar arası süre tahmini) özetsiz; başlıkları puanlama değil tahmin üretimi gösteriyor. Kesişim ölçümleri tohum seçimine bağlı (v3 ile aynı tohumlar).
