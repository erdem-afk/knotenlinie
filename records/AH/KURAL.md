# AH/KURAL — fay tabanlı zamana bağlı uzun vade ölçüm kuralı (2011–2015 puanlamasından önce donduruldu)

Yazıldığı an: 2026-10-12 UTC (saat dosya sonundaki damgada). Bu dosya yazılırken hiçbir 2006+ hedef puanlanmamıştı; 2006–2010
seçim penceresidir, 2011–2015 bir kez puanlanır ve hiçbir seçimi değiştirmez. Sonradan yalnız tarihli "Ek" gelir; sonuç
gördükten sonra denenen her şey `AH/EK.md`'de "kayıt dışı" kalır.

## Çerçeve (Z/Z2 ile aynı)

Hedef: kümesiz (GK74, tüm ≤2015 katalogla) ve bütün olaylar, M≥4,95, hücre×kutu Poisson; İtalya HORUS-Mw CSEP 8993 hücre
[0,30) km. Puanlayıcı: `tools/karsilastir/uzun_z.py` ilkelleri (`olay_ig`, `hedefler`, `poisson_logl`,
`tutarlilik`, taban okuyucuları). Tabanlar: HAZFX, TripleS, MPS04 (İtalya), ayrıca Z2 (bu deneyin ayar anındaki
yeniden kurulumu: Weichert toplamı × Z şekli, fay katmanı yok). Bootstrap 2000, tohum 20261005, olay yeniden örneklemeli.

## Arka plan (Z2'nin modeli, ayar anı kesimiyle)

- 2006–2010 puanı için her şey ≤2005'ten: Weichert b ve M≥4,95 oranı (Z2 kataloğu ve tamlık tabloları, kümesiz GK74) ve Z'nin
  seçtiği şekil ≤2005 katalogla yeniden kurulur (İtalya U0 σ=10 km).
- 2011–2015 puanı için ≤2010 (Z2'nin birincil modeli).

## Fay katmanı

**Kaynaklar.** İtalya: DISS 3.2.0 CSS'nin tümü (üst kenardan düzlem alanı A = L(z₂−z₁)/sin δ, `fay_oku`; yüzey izdüşümü
`csspln320`) ve ISS (A = uzunluk × genişlik). Moment: Ṁ₀ = μ A ṡ, μ = 3·10¹⁰ Pa, ṡ = (srmin+srmax)/2 mm/yıl, sismik
bağlaşım 1, M₀ = 10^(1,5 M + 9,05) N m. Mmax kaynağın `maxmag`'ı. ISS, ebeveyn CSS'nin içinde kalan alan payı ≥0,5 olan en çok
örtüşen CSS'ye bağlanır; ISS kendi Ṁ₀'ını taşır, ebeveyn CSS'ye max(Ṁ₀_CSS − ΣṀ₀_ISS, 0) kalır.
Mmax ≤ 5,45 olan kaynak katmana girmez; ızgara dışına düşen alan payı kaybolur (rapora yazılır).

**Zaman kesimi D** (2006,0 ya da 2011,0 kesirli yıl). ISS düşer, eğer son olayı D'den sonra ve (`created` ya da `updated` ≥ D).
CSS'lere kesim uygulanmaz (jeolojik içerik). Son olay: (i) DISS `latesteq` yalnız "GG Ay YYYY" biçiminde ve < D ise; D'den sonra
ise ayar anında bilinmiyor sayılır (Poisson); (ii) `latesteq` çözümlenemez (Unknown, aralık, B.C., Before) ise CPTI15 (≤D)
ilişkilendirmesi: ISS poligonu +0,05° içinde, Mw ≥ Mmax−0,5, en yeni olay; yoksa Poisson.

**Uzay.** Kaynak poligonunun hücrelere kesişim alanı payı; toplam pay + ızgara dışı = 1.

**Büyüklük (M_min_fay = 5,45 alt kenar = "M5,5" kutusu).** İki varyant, önceden sabit:
- *Karakteristik (YC85-tipi, basitleştirilmiş):* Mmax−1,5 altında GR(b); Mmax−1,5 … Mmax arası GR'nin Mmax−1,5 noktasındaki
  yoğunlukta düz (süreklilik; YC85'in tam sabitleri değil). Mmax−1,5 ≤ 5,45 ise [5,45, Mmax] tamamen düz.
- *Kesik GR:* b = bölgenin Weichert b'si (ayar anı), [5,45, Mmax].
Her kaynakta ölçek ∫ S f M₀ dm = Ṁ₀.

**Zamana bağlılık.** BPT(μ, α=0,5); μ = 1/λ_kar, λ_kar = Mmax−0,5 … Mmax aralığının yıllık Poisson hızı (moment dengesinden). Yalnız
son olayı bilinen ISS'lerde, Mmax−0,5 … Mmax aralığının oranı g = P_BPT(pencere | geçen süre)/P_Poisson ile çarpılır; geçen süre
pencere başlangıcından ölçülür. Son olay bilinmiyorsa g = 1. BPT kapalı varyantta hiçbir kaynakta g uygulanmaz.

**Çifte sayım ve toplam sınırı.** Her M ≥ 5,45 kutusu j için W_j = arka planın bölge toplamı (Z2), F_j = fay katmanının
Poisson-eşdeğer, ızgara içi toplamı. s_j = min(1, W_j/F_j). Arka plan bölge toplamı W_j − s_j F_j'ye iner (şekil aynı); fay
katmanı s_j ile ölçeklenir. g çarpanı bu eşitlemeden sonra uygulanır (zaman bağımlılığı toplamı değiştirebilir). M < 5,45
kutularında arka plan aynen kalır.

**Sınıf parametreleri:** MFD türü, BPT açık/kapalı, α = 0,5, bağlaşım = 1, μ, M_min_fay, karakteristik aralık,
s_j kuralı. Bölgeye özgü: b, Mmax, kayma hızı, alan, son olay, arka plan.

## Seçim (yalnız ≤2005 kurulum; 2006–2010 hedefleri)

Dört varyant: GR–BPT kapalı, GR–BPT açık, KAR–BPT kapalı, KAR–BPT açık. Ölçüt: kümesiz M≥4,95 2006–2010 hedeflerinde
hücre×0,1 büyüklük kutusu Poisson logL toplamı (İtalya). [Yayın notu: bu sürümün kayıtlarıyla
seçim GR-kapali varyantını verir; dört varyant 1,0 nat bağ bandı içindedir.] **Bağ kuralı:** en iyiden 1,0 nat içindeki varyantlar bağlı sayılır;
bağda öncelik sırası GR–kapalı, GR–açık, KAR–kapalı, KAR–açık (basit olan, kanıt gerektirir). Seçilen varyant ≤2010 verisiyle yeniden
kurulur ve 2011–2015'te bir kez puanlanır.

## Ölçüm

2011–2015 ve 2006–2010; kümesiz ve bütün olaylar; M≥4,95. Her satır: IG, olay terimi (IG_olay), integral terimi, toplamı tabana
eşitlenmiş şekil satırı (λ_bizim × Λ_taban/Λ_bizim), bootstrap SE, tek yönlü z, N/S/M, güç beyanı Φ(IG/SE−1,645), Poisson kimliği
zorunlu. Hüküm satırı: 2011–2015 kümesiz M≥4,95, "geçti" = IG>0 ve z>1,645; Z2'ye karşı satır bilgidir (fay bilgisinin değeri).

## Duyarlılık (hüküm ve seçim değil; önceden ilan)

(i) dört varyantın hepsinin 2011–2015 satırları; (ii) fay payı üst sınırı 0,5 (s_j = min(1, 0,5 W_j/F_j)); (iii) BPT seçilirse α = 0,3 ve 0,7.
Seçilen hiperparametreler bunlara göre değişmez.

## Sınırlar (peşin)

HAZFX'in kendi BPT α'sı ve katalog kesimi doğrulanamadı (TABANLAR). DISS parametreleri 2013–2015 sürümüdür. Bağlaşım 1 bir
üst sınırdır; s_j sınırı bölge toplamını Weichert'e bağlar, bu yüzden toplam oran Z2'dekiyle büyük ölçüde aynıdır ve fark uzay/büyüklük
dağılımında aranır. Hedef çerçeve ve tabanlar Z/Z2'dekiyle aynı, ileriye dönük değil.
Damga: 2026-10-12T05:21Z

## Ek 1 (2026-10-12; 2011–2015 hâlâ puanlanmadı)

İlk `sec` koşusunda (SECIM.json yazıldı, sonra silinip yeniden üretilecek) İtalya 2006–2010 kümesiz hücre×kutu logL'i dört varyantta
−23,1 … −23,3 (Z2 −24,9) çıktı. Neden: "fay payı üst sınırı = 1" ile F_j > W_j olan her M≥5,45
kutusunda arka plan sıfıra iner, fay çizgisinden uzak hücrelerdeki gözlenen M≥5,45 olaylar sıfır oranla karşılaşır. Sıfır oranlı
model kabul edilemez; bu yapısal bir kusurdur, sonuç optimizasyonu değil. Değişiklik: **fay payı üst sınırı 0,9** (s_j = min(1, 0,9 W_j/F_j));
arka plan her M≥5,45 kutusunda W_j'nin en az %10'unu korur. Bu artık birincil modeldir; 0,5 duyarlılığı olduğu gibi kalır. Seçim ölçütü,
bağ kuralı ve diğer her şey değişmedi. (İtalya'nın −23,1 … −23,3'ü dışında hiçbir 2006+ sayı görülmeden bu düzeltme
yazıldı.)
Ek 1 damgası: 2026-10-12T05:25Z
