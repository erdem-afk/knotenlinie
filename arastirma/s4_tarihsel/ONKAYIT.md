# S4 ön kaydı: tarihsel Marmara depremlerinin segment ataması (şiddet + türbidit + tsunami)

Durum: TASLAK → inceleme → DONDUR (sha256 + OTS). Yazım 10 Kasım 2026. Bu kural, aşağıdaki
olayların segment atama sonsalları hesaplanmadan önce yazıldı. Girdilerin sayısı ve biçimi
görüldü (nokta sayıları aşağıda); hiçbir aday kırık için olabilirlik hesaplanmadı.

Kaynak soru: `docs/arastirma-sorulari/2026-11-10_yeni-arastirma-sorulari.md`, soru 4.

## Körlük beyanı (dürüstlük)

Bu sınav kör değil. Yazar (Claude) literatürdeki atamaları biliyor (1912 Ganos; 1766 Ağustos
batı; 1509 ve 1894 doğu/Çınarcık tartışması). Türbidit atamalarının bir kısmı yazarların kendi
tarihsel konum varsayımlarıyla yapılmış (döngüsellik riski). Bu yüzden sonuç ileri test defterine
yalnız RAKİP olarak girer; v1.3b NİHAİ, değişmez. Türkiye dışı 2026 verisi kullanılmaz.

## Olaylar

Hedef olaylar (AHEAD/EPICA v1.1 kimlikleri): 1509-09-10, 1719-05-25, 1754-09-02, 1766-05-22,
1766-08-05, 1894-07-10. Bilgi satırı: 1659-02-17, 1556-05-10, 1737-03-06 (güney/ batı dışı aday).
Pozitif kontroller: 1999-08-17 İzmit (şiddet + türbidit + tsunami), 1912-08-09 Mürefte–Şarköy
(yalnız türbidit + tsunami; açık sayısal şiddet verisi bulunamadı, Ambraseys ve Finkel 1987
tabloları sayısal değil).

## Veri (girdi envanteri `GIRDILER.json`, her dosya SHA-256 ile)

1. Şiddet noktaları (MDP): AHEAD makrosismik web servisi, veri kümesi UNITH003
   (Papazachos ve Papazachou 2003, Aristoteles Üniv.), ölçek MM. Nokta sayıları: 1509 12, 1719 13,
   1754 8, 1766-05 13, 1766-08 20, 1894 6, 1659 6, 1556 3, 1737 15 (+TAXE003).
2. Kalibrasyon ve pozitif kontrol şiddetleri: USGS ShakeMap Atlas istasyon listeleri
   (`station_type == macroseismic`) ve aynı ShakeMap'in kırık modeli (rupture.json). Kalibrasyon
   olayları: 1999 İzmit (92), 1999 Düzce (32), 1992 Erzincan (49), 1966 Varto (391), 1976 Çaldıran (68),
   1975 Lice (26), 1988 Spitak (294), 2011 Van (20), 2002 Sultandağı (12). Hepsi ≤2015.
3. Türbidit: Drab vd. 2012 (Batı: Tekirdağ havzası, Batı Sırtı, Orta havza), Drab vd. 2015 BSSA
   (Çınarcık, doi:10.1785/0120130083), Çağatay vd. 2012 Sed. Geol. (İzmit körfezi/Karamürsel),
   Çağatay vd. 2025 Mar. Geol. ve McHugh vd. 2006 EPSL. Kodlama `TURBIDIT.csv` (aşağıda kural).
4. Tsunami: Altınok vd. 2011 NHESS (doi:10.5194/nhess-11-273-2011), güvenilirlik Rel ≥ 3 → "var";
   katalogda olmayan → "bildirilmemiş"; Rel 1–2 → "belirsiz" (olabilirliğe girmez).
5. Fay geometrisi: EDSF13 (Basili vd. 2013, doi:10.6092/INGV.IT-SHARE-EDSF) bileşik kaynak üst
   izleri; zaten `/mnt/project-files/marmara-girdiler/` içinde SHA-256'lı.

## Segmentler (EDSF13 izleri, boylamla kesilmiş)

Kuzey kol, batıdan doğuya: GAN 26,60–27,25 (TRCS290 + TRCS996); TEK 27,25–27,75; CEN 27,75–28,30
(TRCS996 + TRCS013); KUM 28,30–28,75; PIF 28,75–29,23 (TRCS013); IZG 29,23–29,79 (TRCS013 doğu ucu ile
TRCS012 batı ucunu birleştiren doğru); IZE 29,79–30,40 (TRCS012); SAK 30,40–30,97 (TRCS012).
Alternatif (yanlış yere atamayı yakalamak için): SCI Güney Çınarcık (TRCS014), GEM Gemlik–Bandırma
(TRCS023), GEY Geyve–Gemlik (TRCS022).

Aday kırıklar (32): kuzey kolda ardışık 1–4 segment (26 aday); SCI; SCI+IZG; SCI+IZG+IZE; GEM; GEY;
GEM+GEY. Önsel: adaylar arasında düzgün.

Kıyı/deniz: TEK, CEN, KUM, PIF, IZG, SCI, GEM deniz altı; GAN, IZE, SAK, GEY kara.

## Olabilirlik

### Şiddet (ana bileşen)

- Büyüklük: Mw = 5,16 + 1,12·log10(L) (Wells ve Coppersmith 1994, doğrultu atımlı, yüzey kırık
  uzunluğu km), σ_M = 0,25; Mw ±2σ üzerinde 9 noktalı ızgara ile marjinalleştirilir.
- Şiddet tahmin denklemi (IPE): I = a + b·M − c·log10(√(R² + h²)), R = noktanın kırık izine en kısa
  yatay uzaklığı (km), h = 10 km.
- Gözlem modeli: I_gözlem = I_tahmin + δ_olay + ε; δ_olay ~ N(0, τ²), ε ~ N(0, σ²), δ analitik
  marjinalleştirilir (kovaryans σ²I + τ²11ᵀ). Şiddet ≥ 10 sağdan sansürlü değil, olduğu gibi.
- Kalibrasyon: (a, b, c, σ, τ) kalibrasyon olaylarında (veri 2) en büyük marjinal olabilirlikle; her
  kalibrasyon olayında M = USGS Mw, R = ShakeMap kırık modeline uzaklık. 1999 İzmit pozitif kontrolü
  için kalibrasyon İzmit hariç yapılır (birini dışarıda bırak). Tarihsel olaylar için tüm 9 olay.
- Ölçek farkı (MM ↔ ShakeMap MMI) ayrıca düzeltilmez; τ içinde kalır.

### Türbidit

Havzalar ve komşu segmentler: TB Tekirdağ havzası + Batı Sırtı (GAN'ın doğu ucu, TEK); CB Orta havza +
Orta Sırt (CEN); KB Kumburgaz (KUM); CiB Çınarcık (PIF, SCI); IGB İzmit körfezi havzaları (IZG, IZE).

P(türbidit | kırık): komşu segment kırıldıysa p_hit = 0,7; kırığın havzaya en yakın ucu ≤ 50 km ise
p_near = 0,2; aksi halde p_far = 0,05. Gözlem güvenilirliği w: radyonüklit tarihli 0,9; radyokarbon
penceresi tek tarihsel adayı içeriyorsa 0,6; birden çok adayı içeriyorsa 0,3. Olabilirlik:
P(gözlem "var") = w·P(türbidit | kırık) + (1 − w)·0,3; "yok" bunun tümleyeni; çelişkili ya da veri
yoksa çarpan 1.

1766 Mayıs ve Ağustos radyokarbonla ayrılamıyor: iki olay ortak çözülür (32×32 aday çifti); "var"
gözlemi birleşimin P'sini kullanır: 1 − (1 − p₁)(1 − p₂).

Kodlama (önceden sabit, `TURBIDIT.csv`):
- 1999: IGB var (0,9, Çağatay 2012); CiB var (0,6, Drab 2015 "tA, uzak alan"); TB yok (0,9).
- 1912: TB var (0,9, Drab 2012); CB çelişkili (Drab 2012 var, Çağatay 2025 yok) → 1; CiB yok (0,9, Drab
  2015 en genç olay 1894).
- 1894: CiB var (0,9, Drab 2015); CB var (0,6, Çağatay 2025 "Orta Sırt ve Orta havza"); TB yok (0,6).
- 1766 (çift): TB var (0,6, Drab 2012, Çağatay 2025 batı listesi); CB var (0,6, Çağatay 2025); CiB yok
  (0,6, Drab 2015); IGB yok (0,3, Çağatay 2012 "ayırt edici sinyal yok").
- 1509: CB var (0,6, Çağatay 2025); CiB var (0,6, Drab 2015 E2 1288–1664); IGB var (0,6, Çağatay 2012);
  TB yok (0,6, Çağatay 2025 batı listesinde yok).
- 1719 ve 1754: CiB yok (0,3, Drab 2015 penceresi 1288–1664 sonrası boşluk), CB yok (0,3), TB yok (0,3).

### Tsunami

P(tsunami bildirilmiş | kırık): kırık en az bir deniz altı segment içeriyorsa 0,6, yoksa 0,15.
Kodlama: 1509 var (Rel 4), 1766-05 var (Rel 4), 1894 var (Çınarcık ve Boğaz; Altınok tablo dışı metin,
Drab 2015 alıntısı; Rel ≥ 3 sayılır), 1912 var (Rel 4), 1999 var (Rel 4), 1754 belirsiz (Rel 2–3) → 1,
1719 ve 1766-08 bildirilmemiş.

### Ortak sonsal

Sonsal ∝ önsel × L_şiddet × L_türbidit × L_tsunami. Her bileşen ayrı satır olarak da raporlanır
(yalnız şiddet, yalnız türbidit, yalnız tsunami, ortak).

## Pozitif kontrol ve ateşleme kapısı (önceden sabit)

Doğru küme 1999: {IZG, IZE, SAK}; 1912: {GAN, TEK}. "Doğru aday" = doğru kümeyle Jaccard ≥ 2/3.

K1 (1999, şiddet tam veri, İzmit hariç kalibrasyon): doğru adaylara sonsal kütle ≥ 0,5.
K2 (1999, tarihsel yoğunluk): 92 noktadan rastgele n = 12 nokta (tarihsel olayların medyanı), 200
tekrar (tohum 20261110); doğru adaylara ortalama sonsal kütle ≥ 0,35 ve batıya yanlış kütle
(GAN..PIF, SCI, GEM'den en az birini içeren adaylar) ortalaması ≤ 0,25. n = 6 bilgi satırı.
K3 (1912, yalnız türbidit + tsunami): doğru adaylara sonsal kütle, düzgün önseldeki kütlenin ≥ 2 katı.
K4 (1999 ortak): ortak sonsalda doğru kütle, yalnız şiddet sonsalından düşük değil (log skor farkı
≥ −0,1).

Hüküm:
- K1 ve K2 geçerse şiddet bileşeni tarihsel olaylara uygulanır; K2 kalırsa şiddet yalnız n ≥ 12
  noktalı olaylarda kullanılır ve diğerleri "şiddet zayıf" diye işaretlenir; K1 kalırsa yöntem
  KAPANIR, olasılığa yayılmaz, yalnız rapor yazılır.
- K3 kalırsa türbidit + tsunami bileşeni yalnız bilgi satırı olur, ortak sonsala girmez.
- K4 kalırsa ortak sonsal yerine yalnız şiddet sonsalı yayılıma gider.

## Çıktılar (önceden tanımlı)

1. Her hedef olay için segment başına kırılma olasılığı (marjinal) ve en olası 3 aday, bileşen bazında.
2. "Son kırılma tarihi" sonsalı: CEN, KUM, PIF (İstanbul önü) için 1500 sonrası kırılma sayısı ve son
   kırılma yılı dağılımı.
3. Parsons–Ambraseys karşılaştırması: v1.5'teki iki atama dalının (sunucuda) her biri için ortak sonsal
   altındaki log olasılığı; Bayes çarpanı |ln BF| ≥ 1 ise "fark daraltıldı", değilse H0.
4. v1.9 (RAKİP): v1.5'in tarihsel/paleosismik dalında segment atamaları sabit değerler yerine bu
   sonsaldan örneklenir; diğer her şey v1.5 ile aynı. Rapor: İstanbul 30 yıl oranı v1.9/v1.3b ve
   v1.9/v1.5, %10–90 genişlik oranı, aralık kaynak payları. Mutlak olasılık yazılmaz. Bu adım sunucu
   (magma-corbasi) gerektirir; bulut koşusu 1–3'ün sunucusuz kısmını üretir.

## H1 / H0

H1: ortak ters çözüm, pozitif kontrollerde tek kaynaktan iyi (K4) ve Parsons–Ambraseys farkını
|ln BF| ≥ 1 ile ayırır. H0: ayıramaz ya da kontroller kalır.

## Sapma kuralı

Kod bu metinden saparsa sapma sonuç dosyasında "SAPMA" başlığıyla, gerekçesiyle yazılır; sonuç
o satır için "ön kayıt dışı" işaretlenir. Hata düzeltmesi kuralı değiştirmez; düzeltme sonrası tek
yeniden koşu, iki koşu da raporlanır.

Maliyet: 0 € (bulut). Sonuç dosyası: `arastirma/s4_tarihsel/SONUC.md`.
