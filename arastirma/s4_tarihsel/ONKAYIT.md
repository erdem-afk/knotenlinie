# S4 ön kaydı: tarihsel Marmara depremlerinin segment ataması (şiddet + türbidit + tsunami)

Sürüm 2 (bağımsız inceleme KABUL-ŞARTLI; 9 zorunlu değişiklik işlendi, `INCELEME.md`). Yazım
10 Kasım 2026. Bu kural, aşağıdaki olayların segment atama sonsalları hesaplanmadan önce yazıldı.
Girdilerin sayısı ve biçimi görüldü; hiçbir aday kırık için olabilirlik hesaplanmadı.

Kaynak soru: `docs/arastirma-sorulari/2026-11-10_yeni-arastirma-sorulari.md`, soru 4.

## Körlük beyanı

Bu sınav kör değil. Yazar (Claude) literatürdeki atamaları biliyor (1912 Ganos; 1766 Ağustos batı;
1509 ve 1894 doğu/Çınarcık tartışması). Türbidit atamalarının bir kısmı yazarların kendi tarihsel konum
varsayımlarıyla yapıldı (döngüsellik). Bu yüzden türbidit bileşeni sonuçta "literatür-koşullu" diye
etiketlenir; sonuç ileri test defterine yalnız RAKİP olarak girer; v1.3b NİHAİ, değişmez. Türkiye dışı
2026 verisi kullanılmaz.

## Olaylar

Hedef olaylar (AHEAD/EPICA v1.1): 1509-09-10, 1719-05-25, 1754-09-02, 1766-05-22, 1766-08-05,
1894-07-10. Bilgi satırı: 1659-02-17, 1556-05-10, 1737-03-06 (yalnız UNITH003; TAXE003 EMS seti
kullanılmaz). 1855-02-28 Bursa dosyası envanterde ama kapsam dışı (güney kol, hedef değil).
Pozitif kontroller: 1999-08-17 İzmit; 1912-08-09 Mürefte–Şarköy (yalnız türbidit + tsunami; açık
sayısal şiddet verisi yok).

## Veri (`GIRDILER.json`, her dosya SHA-256 ile)

1. Şiddet noktaları (MDP): AHEAD makrosismik servisi, UNITH003 (Papazachos ve Papazachou 2003), MM.
   Nokta sayıları: 1509 12, 1719 13, 1754 8, 1766-05 13, 1766-08 20, 1894 6, 1659 6, 1556 3, 1737 15.
2. Kalibrasyon: USGS ShakeMap Atlas istasyon listeleri (`station_type == macroseismic`, değeri boş
   olanlar atılır) ve aynı ShakeMap'in kırık poligonu. Olaylar: 1999 İzmit (92), 1999 Düzce (31),
   1992 Erzincan (49), 1976 Çaldıran (68), 1975 Lice (26), 1988 Spitak (294), 2002 Sultandağı (12).
   Çıkarılan: 2011 Van (DYFI, MMI değil), 1966 Varto (yalnız MMI ≥ 6, alttan kesik örnek).
3. Türbidit: Drab vd. 2012; Drab vd. 2015 BSSA (doi:10.1785/0120130083); Çağatay vd. 2012 Sed. Geol.;
   Çağatay vd. 2025 Mar. Geol.; McHugh vd. 2006 EPSL. Kodlama `TURBIDIT.csv`.
4. Tsunami: Altınok vd. 2011 NHESS (doi:10.5194/nhess-11-273-2011). Rel yalnız tablodan okunur:
   Rel ≥ 3 → "var"; tabloda yok → "bildirilmemiş"; Rel aralığı 3'ü kesiyorsa (ör. 2–3) → "belirsiz".
5. Fay geometrisi: EDSF13 (Basili vd. 2013) bileşik kaynak üst izleri.

## Segmentler (EDSF13 izleri, boylamla kesilmiş)

Kuzey kol: GAN 26,60–27,25 (TRCS290 + TRCS996); TEK 27,25–27,75; CEN 27,75–28,30 (TRCS996 + TRCS013);
KUM 28,30–28,75; PIF 28,75–29,23; IZG 29,23–29,79 (TRCS013 doğu ucu ile TRCS012 batı ucunu birleştiren
doğru); IZE 29,79–30,40; SAK 30,40–30,97 (TRCS012). Alternatif: SCI Güney Çınarcık (TRCS014),
GEM Gemlik–Bandırma (TRCS023), GEY Geyve–Gemlik (TRCS022).

Aday kırıklar (33): kuzey kolda ardışık 1–4 segment (26); SCI; SCI+IZG; SCI+IZG+IZE; GEM; GEY; GEM+GEY;
ve KÜME DIŞI: AHEAD merkezinde nokta kaynak, R = merkeze uzaklık, M düzgün 6,5–7,6 (12 noktalı ızgara).
Küme dışının olay başına kütlesi raporlanır. Önsel: 33 aday üzerinde düzgün. Aday düzeyinde düzgün
önsel segment düzeyinde düzgün olmadığı için çıktı 2'de segment başına önsel marjinal ve sonsal/önsel
oranı birlikte yazılır.

Deniz altı: TEK, CEN, KUM, PIF, IZG, SCI, GEM. Kara: GAN, IZE, SAK, GEY. Küme dışı: AHEAD merkezi
denizdeyse deniz altı.

## Olabilirlik

### Şiddet

- Büyüklük (adaylar ve pozitif kontroller): Mw = 5,16 + 1,12·log10(L), L = aday iz uzunluğu km
  (Wells ve Coppersmith 1994); σ_M = 0,25; Mw ±2σ üzerinde 9 noktalı ızgara, normalleştirilmiş Gauss
  ağırlıkları.
- IPE: I = a + b·M − c·log10(√(R² + h²)), h = 10 km. R: kalibrasyonda kırık poligonunun yüzey
  izdüşümüne Joyner–Boore uzaklığı; adaylarda EDSF izine en kısa yatay uzaklık.
- Gözlem modeli: I_gözlem = I_tahmin + δ_olay + ε; δ ~ N(0, τ²), ε ~ N(0, σ²); δ analitik
  marjinalleştirilir (kovaryans σ²I + τ²11ᵀ).
- Kalibrasyon: (a, b, c, σ, τ) en büyük sonsal; b ~ N(1,5; 0,5²) önseli, diğerleri düz; her olayın
  log olabilirliği (n̄ / n_olay) ile ağırlıklanır (olaylar eşit ağırlıklı). Kalibrasyonda M = USGS Mw.
  1999 İzmit pozitif kontrolleri için kalibrasyon İzmit hariç; tarihsel olaylar için 7 olayın tümü.
- Ölçek farkı (MM ↔ MMI) ayrıca düzeltilmez, τ içinde kalır.
- Duyarlılık (hükme girmez): h = 5 ve 15 km.

### Türbidit (etiket: literatür-koşullu)

Havza noktaları: TB Tekirdağ havzası 40,82 K 27,55 D; CB Orta havza 40,83 K 28,00 D; KB Kumburgaz
40,87 K 28,55 D; CiB Çınarcık 40,72 K 29,05 D; IGB Karamürsel 40,70 K 29,55 D. Bir segment, izi havza
noktasına ≤ 10 km geçiyorsa "komşu".

P(türbidit | kırık) = 0,7 (komşu segment kırıldıysa); 0,2 (kırık havza noktasına ≤ 50 km); 0,05
(diğer). Gözlem güvenilirliği w: radyonüklit tarihli 0,9; radyokarbon penceresi tek M ≥ 6,5 tarihsel
aday içeriyorsa 0,6; birden çok aday içeriyorsa ya da pencere yayımda verilmemişse 0,3.
P("var") = w·P(türbidit | kırık) + (1 − w)·0,3; "yok" bunun tümleyeni; çelişkili ya da veri yoksa 1.

1766 çifti ortak çözülür: önsel 33×33 = 1089 çift üzerinde düzgün; P("var") = w·[1 − (1 − p₁)(1 − p₂)]
+ (1 − w)·0,3; "yok" tümleyeni; tsunami ve şiddet olay başına ayrı; olay başına marjinaller çift
sonsalından alınır.

### Tsunami

P(bildirilmiş | kırık) = 0,6 (en az bir deniz altı segment) ya da 0,15 (yalnız kara). "var" için bu
değer; "bildirilmemiş" için 1 − r·P, r = 0,7 (eski çağ kayıt eksikliği); "belirsiz" için 1.
Kodlama (`TSUNAMI.csv`): 1509 var (Rel 4); 1719 bildirilmemiş; 1754 belirsiz (Rel 2–3); 1766-05 var
(Rel 4); 1766-08 bildirilmemiş; 1894 var (no 114, Rel 4); 1912 var (Rel 4); 1999 var (Rel 4).

### Ortak sonsal

Sonsal ∝ önsel × L_şiddet × L_türbidit × L_tsunami. Ayrıca bileşen satırları (yalnız şiddet, yalnız
türbidit, yalnız tsunami, ortak) ve sıralı bırakma tablosu (ortak − her bileşen) raporlanır.

## Pozitif kontrol ve ateşleme kapısı

Doğru küme 1999: {IZG, IZE, SAK}; 1912: {GAN, TEK} (Armijo görüşü {GAN, TEK, CEN} bilgi satırı).
"Doğru aday" = doğru kümeyle Jaccard ≥ 2/3. "Batıya yanlış aday" = doğru olmayan ve GAN..PIF, SCI,
GEM'den en az birini içeren aday.

K1 (1999, tüm şiddet, İzmit hariç kalibrasyon): doğru adaylara sonsal kütle ≥ 0,5.
K2 (1999, tarihsel geometri): her hedef tarihsel olay için (6 olay), o olayın her AHEAD yerine en yakın
3 adet 1999 noktasından biri rastgele ve yerine koymadan seçilir; 6 olay × 200 tekrar (tohum
20261110). Geçme: doğru kütle ortalaması ≥ 0,35 ve batıya yanlış kütle ortalaması ≤ 0,25. Olay
bazında ayrıca raporlanır.
K3 (1912, yalnız türbidit + tsunami): doğru adaylara sonsal kütle ≥ 0,4.
K4 (1999 ortak; yalnız tutarlılık denetimi, H1 kanıtı sayılmaz): ortak sonsalda doğru kütlenin log'u,
yalnız şiddet sonsalınınkinden ≥ −0,1.

Hüküm:
- K1 kalırsa yöntem KAPANIR: olasılığa yayılmaz, yalnız rapor.
- K2 kalırsa şiddet hiçbir tarihsel olayda ortak sonsala girmez (yalnız bilgi satırı).
- K3 kalırsa türbidit + tsunami ortak sonsala girmez (yalnız bilgi satırı).
- K4 kalırsa ortak yerine yalnız şiddet sonsalı yayılıma gider.

## Çıktılar

1. Her hedef olay için segment başına kırılma olasılığı, en olası 3 aday ve küme dışı kütlesi,
   bileşen bazında.
2. CEN, KUM, PIF için 1500 sonrası kırılma sayısı ve son kırılma yılı dağılımı; segment başına önsel
   marjinal ve sonsal/önsel oranı.
3. Parsons–Ambraseys: v1.5'in iki atama dalı, v1.5 dondurulmuş dosyalarından (magma-corbasi, v1.5
   commit 18872d36 ve OTS'li DONDUR dosyası; bu ön kayıttan önce dondurulmuş, değiştirilemez) okunur.
   Okuma sırasında dal dosyalarının sha256'sı sonuçta yazılır. BF = (sonsal oran) / (önsel oran)
   (dal atamalarının ortak sonsal altındaki olasılık oranı, düzgün önsele göre). |ln BF| ≥ 1 → "fark
   daraltıldı"; değilse H0.
4. v1.9 (RAKİP): v1.5'in tarihsel/paleosismik dalında segment atamaları sabit değerler yerine bu
   sonsaldan örneklenir; diğer her şey v1.5 ile aynı. Rapor: İstanbul 30 yıl oranı v1.9/v1.3b ve
   v1.9/v1.5, %10–90 genişlik oranı, aralık kaynak payları. Mutlak olasılık yazılmaz.
   3 ve 4 sunucu (magma-corbasi) gerektirir; bulut koşusu 1–2 ve kontrolleri üretir.

## H1 / H0

H1: kontroller (K1–K3) geçer ve ortak sonsal Parsons–Ambraseys dallarını |ln BF| ≥ 1 ile ayırır.
H0: ayıramaz ya da kontroller kalır.

## Sapma kuralı

"Hata" = kod ile bu metin arasındaki fark; kural değişikliği değildir. Hata düzeltmesi sonrası tek
yeniden koşu, iki koşu da raporlanır. Bu metinden bilinçli sapma "SAPMA" başlığıyla, gerekçesiyle
yazılır ve o satır "ön kayıt dışı" işaretlenir.

Maliyet: 0 € (bulut). Sonuç: `arastirma/s4_tarihsel/SONUC.md`.
