# X/KURAL.md — sonlu kaynak uzaysal çekirdek: seçim kuralı (2011–2015 puanlamasından önce)

Bu kural, 2011–2015 puanlaması **görülmeden** yazıldı. Seçim ve ölçüm çerçevesi
ortak günlük çerçevedir. Aşağıdaki hiçbir sayı 2011–2015
sonucuna göre değiştirilmez.

## Aday listesi (önceden sabit)

R tabanı: `tools/etas_uzun/` (uzun pencereli, Mc(t)'li, CSEP-maskeli ETAS +
gün içi kaskad). Sonlu varyant X, R'nin bütün ETAS parametrelerini ve b değerini
aynen alır; **yalnız** M ≥ M_s ebeveynlerin doğrudan uzaysal çekirdeğini
değiştirir. Yeniden MLE yapılmaz (isteğe bağlı MLE varyantı bu deneyde yok).

Adaylar: `R`, `X-a-5.0`, `X-a-5.5`, `X-b-5.0`, `X-b-5.5`.

- `a`: doğrultu GCMT düğüm düzleminden.
- `b`: doğrultu artçı bulutunun temel bileşen ekseninden.
- `5.0` / `5.5`: sonlu çekirdeğin uygulandığı ebeveyn büyüklük eşiği M_s.

## Çekirdek (bütün adaylarda ortak)

M ≥ M_s ebeveyn için R'nin radyal uzaysal çekirdeği, ebeveyn merkezli ve
doğrultu boyunca uzanan, boyu

    L(M) = 10^(−2.44 + 0.59 M)   km        (Wells & Coppersmith 1994, Tablo 2A,
                                            yüzey altı kırık boyu, bütün faylanma türleri)

olan bir doğru parçası boyunca konvolve edilir. Sayısal konvolüsyon, parça
üzerinde eşit ağırlıklı `K` düğümle yapılır:

    K = tek sayı, aralık ≈ D_i/2 (D_i = D·10^(γ(M−Mc))), K ∈ [3, 15].

Toplam kütle korunur (düğüm çekirdeklerinin ortalaması); üretkenlik, K, α, c, p,
D, q, γ ve b R'den aynen geçer. Yalnız M ≥ M_s ebeveynler değişir; küçük
ebeveynler izotrop kalır.

## Doğrultu (iki önceden sabit yol)

Her iki yol da yalnız gün başından önceki olayları kullanır (nedensel).

- **(a) GCMT yolu** (`$KNOTENLINIE_DATA/kesik-2015/gcmt_le2015.ndk`, ≤2015):
  ebeveynle eşleşen çözüm, origin zamanı ±60 s ve uzaklık ≤50 km; ayrıca
  çözümün merkez zamanı gün başından önce olmalı. Eşleşen çözüm yoksa ebeveyn
  izotrop kalır. İki düğüm düzleminden, ebeveynin ilk günündeki (< gün başı)
  ve ≤100 km içindeki artçıların PCA büyük eksenine `|cos|` ile daha uyanı
  seçilir; hiç artçı yoksa **ilk düzlem** alınır. Şerit merkezi ebeveyn
  merkez üssüdür.
- **(b) Artçı yolu**: ebeveynden sonra, ≤L(M) km ve ≤3 gün içinde, gün
  başından önceki artçılar. En az **10** olay varsa PCA büyük ekseni
  doğrultudur; şerit merkezi artçı bulutunun ağırlık merkezidir. 10'dan az
  olay varsa izotrop.

Doğrultu birim vektörü yerel km düzleminde `(doğu, kuzey) = (sin θ, cos θ)`,
θ kuzeyden saat yönü. Bağlam (b) için L, ebeveynin M'sinden WC94 ile gelir.

## Seçim kuralı

- Seçim modelleri **≤2005 verisiyle** kurulur: R için `S`'nin ≤2005 R-tipi
  ayarı `$KNOTENLINIE_DATA/ortak/uzun/etas_s_le2005.json` kullanılır; X aynı parametre
  ve çekirdekle kurulur.
- Seçim penceresi **2006-01-01 – 2010-12-31**, eşik **M ≥ 2,95**, çerçeve
  CSEP İtalya 8993 hücre, [0,30) km, günlük, 0,1 M kutuları. Ölçüt, adayın
  günlük Poisson logL'idir (`kosucu.kos` ile aynı; gün başı geçmişi).
- **Seçilen aday: en yüksek 2006–2010 M ≥ 2,95 logL.** Beraberlikte sırayla:
  (1) `R`, (2) küçük M_s, (3) yol `a`.

## Puanlama

- Seçilen varyant **≤2010 verisiyle yeniden kurulur** (`etas_ortak.json`) ve
  **2011-01-01 – 2015-12-31**'te **bir kez** puanlanır.
- Tabanlar: `R-ortak-kaskad` (≤2010 ayarı) ve `ETAS-LM` (deney J).
- Eşikler: M ≥ 2,95 (geliştirme), M ≥ 3,95 (hüküm), M ≥ 4,95 (ek).
- Raporlanan alanlar: N, Λ_aday, Λ_taban, IG, IG_olay, integral, SE_blok
  (haftalık blok), z, p_tek, N/S/M. Ayrıca hedeflerin, önceki 30 gün / 100 km
  içinde M ≥ 5 ebeveyni olan alt kümesinde IG.
- Her puanlanan model ve dönem için skor defteri yazılır
  (`$KNOTENLINIE_RUNS/defter/X/`).

`SECIM.json` seçim sonucunu ve bu dosyanın SHA256'sını taşır; KURAL.md
değişirse seçim kaydı geçersiz olur.
