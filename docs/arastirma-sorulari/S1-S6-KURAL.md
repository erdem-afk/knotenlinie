# S1 + S6 ön kaydı: fay sıçrama kurallarının yayım sonrası sınavı ve türbidit eşzamanlılığı (10 Kasım 2026)

Erdem 10 Kasım 17:28'de 7 sorunun hepsini seçti ("Hepsi"). Bu kural veri derlenmeden önce yazılıp donduruldu (sha + OTS). Kural kör değil: yazar 2016 sonrası büyük kırılmaları nitel olarak biliyor (ör. Kahramanmaraş'ın bir faydan ötekine sıçradığını), ama geçit envanterini ve ölçümleri görmedi. Bu kısmi körlük kaybı sınır olarak kayıtlı.

## S1. Soru

Biasi ve Wesnousky'nin (2016, 2017) yayımlanmış geçiş olasılıkları, katsayıları yayımda sabitlendikten sonraki doğrultu atımlı yüzey kırılmalarında, kırılmanın bir geometrik geçitten geçip geçmeyeceğini rakipten iyi tahmin ediyor mu?

## S1. Tahmin edici (aday, değişmez)

Katsayılar OpenSHA'daki `BiasiWesnouskyJumpProb.java` uygulamasından (USGS/SCEC açık kodu; makalelere bağlı tablo değerleri):

- **Basamak (BW16, doğrultu atımlı):** geçiş oranı PR(d) = max(0, 1,89 − 0,31·d), d = basamak genişliği (km). P = PR / (1 + PR).
- **Büküm (BW17, doğrultu atımlı):** doğrultu değişimi θ için en yakın kutu merkezinin PR'si: 5° → 2,7; 15° → 1,35; 25° → 1,3; 35° → 0,1; 45° ve üstü → 0,08. P = PR / (1 + PR).
- **Mekanizma değişimi (BW17):** P = 4/75.
- **Kırpma:** puanlamada P [0,02, 0,98] aralığına kırpılır (BW16'nın d ≥ 6,1 km'de P = 0 vermesi tek gözlemle −∞ üretmesin diye). Kırpılmamış sonuç bilgi satırıdır.

## S1. Rakipler

- **R0 (hüküm rakibi):** BW16 Tablo 4'ün mesafeden bağımsız olasılığı, P = 0,46 (OpenSHA'da doğrultu atımlı ve genel). Aynı makaleden, aynı veri kümesinden. Soru şu: geometri bilgisi işe yarıyor mu?
- **R1 (bilgi):** yeni veride gözlenen geçiş oranı (örneklem içi üst sınır).

## S1. Veri ve olay listesi (önceden tanımlı)

- **Olaylar:** 2016-01-01 – 2025-12-31 arası, GCMT'ye göre doğrultu atımlı (eğim atımı açısı ±30° içinde ya da 180° ± 30°), Mw ≥ 6,5, karada, haritası yayımlanmış ya da açık veri olarak paylaşılmış ≥ 10 km yüzey kırığı olan depremler. Beklenen liste (taramayla tamamlanır, sonuç görülmeden kapanır): Kumamoto 2016, Kaikoura 2016, Palu 2018, Ridgecrest 2019 (Mw 6,4 ve 7,1), Maduo 2021, Kahramanmaraş 2023 (Mw 7,8 ve 7,6), Myanmar 2025. Türkiye olayları mühür açıldığı için geliştirme verisi; Türkiye dışı 2026 kullanılmaz.
- **Kırık izleri:** öncelik açık veri (SURE 2.0, Zenodo/ScienceBase kırık haritaları), yoksa yayımlanmış harita.
- **Kırılmamış fay devamı:** GEM Global Active Faults (harmonize geojson). Kırık izine 1 km'den yakın GEM çizgileri kırık sayılır.

## S1. Geçit tanımı (algoritmik)

1. Kırık parçaları, aralarındaki boşluk < 0,2 km ise tek kol sayılır.
2. **İçerideki basamak (geçildi):** doğrultu boyunca ardışık iki kol arasındaki dik uzaklık ≥ 1 km ise bir basamak geçidi. d = kollar arasındaki en kısa dik uzaklık.
3. **İçerideki büküm (geçildi):** 5 km'lik kayan ortalamayla kol doğrultusunun değişimi ≥ 10° olan her nokta (aynı büküm 5 km içinde bir kez sayılır).
4. **Uçlar (durdu):** her kırık ucunda, uçtan doğrultu yönünde 10 km içinde kırılmamış GEM fayı varsa bir durma geçidi. Basamak ise d = dik uzaklık, aynı çizgide devam ediyorsa büküm θ = doğrultu farkı; θ < 10° ve d < 1 km ise geometrik geçit yok: uç "geometrisiz durma" olarak sayılır, puanlanmaz, bilgi satırına yazılır.
5. **Mekanizma değişimi:** GEM ya da yayımlanmış kayma vektörüne göre ana kol doğrultu atımlıdan bindirme/normal kola geçişte geçiş/durma geçidi (Kaikoura gibi).
6. Kahramanmaraş Mw 7,8'in Narlı fayından Doğu Anadolu Fayı'na geçişi bir dallanma. Dallanma BW16/17'de tanımlı olmadığı için puanlanmaz, ayrı bilgi satırına yazılır.

## S1. Skor ve hüküm

- Her geçit Bernoulli log olabilirliği. ΔL = L(BW) − L(R0), geçit başına IG ve olay bloklu bootstrap (10 000) ile %95 aralık.
- **Ateşleme kapısı:** envanter çıkınca, sonuç puanlanmadan önce, N geçitle R0'a karşı beklenen IG'nin olay bloklu SE'si sentetik veriyle (BW doğru varsayımı) hesaplanır. Beklenen IG < 2 SE ise sonuç önceden "ayırt edilemez" ilan edilir, yine yayımlanır.
- **H1:** ΔL > 0 ve aralık 0'ı içermiyor. **H0:** değil.
- **Kalibrasyon (bilgi):** P kutularında (0–0,2, 0,2–0,5, 0,5–0,8, 0,8–1) gözlenen/beklenen, binom p.
- **Duyarlılık (bilgi):** basamak eşiği 0,5 ve 2 km; büküm eşiği 15°; kırpma 0,01 ve 0,05.
- Tek koşu. Kural değişikliği gerekirse "Ek" olarak tarih ve gerekçeyle yazılır; özgün sonuç da yayımlanır.

## S1. Marmara'ya bağlama (puandan bağımsız, önceden tanımlı)

Sonuç ne çıkarsa çıksın, Marmara geçitleri (Çınarcık–PIF bükümü, PIF–CMF ve Kumburgaz bölgesi, CMF–Ganos bükümü, Ganos–Saros) EDSF13 geometrisiyle aynı algoritmayla ölçülür ve CMF+PIF ortak kırılma payı f'nin BW tahmini çıkarılır. H1 ise BW tahmini, H0 ise R0 tahmini, v1.7'nin f ≈ 0,10 (0,05–0,15) değeriyle kıyaslanır ve ileri test defterine yeni sürüm (rakip) olarak önerilir. v1.3b değişmez.

## S6. Soru ve öldürme ölçütü

Havzalar arası türbidit yaş eşzamanlılığı CMF+PIF ortak kırılma payını f ölçebilir mi?

- **Sentetik test önce:** iki segmentte (PIF ve CMF) 1000 yıllık olay dizileri üretilir: segment başına tekrar 250 yıl (Poisson), ortak kırılma payı f ∈ {0,1, 0,5}. Ortak olmayan olaylar arasında gerçek yakın zamanlı çiftler oluşur (Poisson rastlantısı ve 1766 Mayıs/Ağustos gibi dizileri temsilen, olayların %20'sine 0–30 yıl içinde komşu segmentte tetiklenmiş eş eklenir). Türbidit yaşlarına 1σ ∈ {30, 60, 100} yıl hata eklenir. "Eşzamanlı" ölçütü |Δt| < 2σ√2.
- **Ölçüt:** f = 0,1 ile f = 0,5'i ayırma gücü (olabilirlik oranı testi, α 0,05) 1000 yıllık kayıt için ≥ 0,8 değilse S6 "ölçülemez" diye kapanır; yalnız gerçek verinin σ'sı ≤ ayırt edebilen σ ise gerçek türbidit verisine geçilir.

## Maliyet ve sınır

0 €, makine yok. Envanter ve ölçüm bulut oturumunda. Sonuç dosyası `docs/arastirma-sorulari/S1-S6-SONUC.md`.
