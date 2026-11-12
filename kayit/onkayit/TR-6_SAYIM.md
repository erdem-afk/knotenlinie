# TR-6 tasarım ve 0 € güç kapısı sayımı: sismisiteden gerilme hızı ters çözümünün kör doğrulaması

12 Kasım 2026. Durum: tasarım + sayım. Hüküm satırı koşulmadı; hiçbir oran değişimi, hiçbir ters çözüm hesaplanmadı.
2026 deprem verisi sorgulanmadı (bütün sorguların bitişi 2025-12-31; okuyucu ayrıca 2026 satırını sayılmadan atar).
Betikler: `kayit/turetme/tr6/tr6_indir_koeri.py` (KOERI indirme), `tr6_indir.py` (EMSC, yalnız karşılaştırma),
`tr6_sayim.py` (Mc, kümesizleştirme, güç), `tr6_a_sayim.py` ((a) ayağı durum sayımı). Çıktılar: `tr6_sayim.json`,
`tr6_a_sayim.json`, `tr6_ham_sha256.txt`. Kaynaklar: `kayit/turetme/ZINCIR.md` Halka 1 ve 5,
`research_notes/Fayın anlık durumu gözlem boşlukları/sismisiteden_gerilme_hizi.md`, defter (TR-6, S-7, ETAS-TABAN,
CRS-ETAS, KURESEL-CRS-GELGIT, AV-2).

## Hüküm

**(b) Marmara çözünürlüğü kapıyı geçmiyor; (a) küresel doğrulama sınırda ve Aσ'ya bağlı.** Açık KOERI kataloğuyla
(2016–2025, Mc 2,1) kümesizleştirilmiş (GK74) arka plan oranı segment başına yılda Ganos 2,3, Orta Marmara 20,3,
Prens Adaları 2,9, Çınarcık 9,8, İzmit 1,1 olay. Bu oranlarla 1 yılda %80 güçle algılanabilecek en küçük gerilme hızı
artışı **Aσ = 10 kPa'da 15–37 kPa/yıl, Aσ = 50 kPa'da 63–134 kPa/yıl**. En iyi segment Çınarcık. Bir gerilme adımı
için eşik 9–25 kPa (Aσ = 50 kPa'da 35–82 kPa). Yükleme hızının azalması 1 yılda hiçbir segmentte görülemiyor.
Kaba el hesabı ("≈ 5–25 kPa") adım olarak 2–3 kat, hız olarak 3–5 kat iyimser çıktı. Çünkü hız-durum modelinde
gerilme hızındaki değişim 1 yılda oranı ancak r T² Δτ̇ / (2Aσ) kadar oynatıyor. Beklenen sinyallerle kıyas:
yavaş kayma adımı ≤ 1 kPa (Tary 2026: "birkaç onda bir kPa") ve yıl ölçekli yükleme değişimi ≈ 0,6–6,5 kPa/yıl.
Adım ölçüsü her segmentte GEÇMEZ (9–82 kat altta). Hız ölçüsü dört segmentte GEÇMEZ. Çınarcık yalnız
Aσ = 10 kPa'da ve sinyalin üst ucuna karşı SINIRDA (ρ = 2,4). Ayak (a): ComCat'te sonlu fay modeli olan
155 olaydan, gölge lobunda −10 kPa'yı 1 yılda görecek kadar öncül sismisitesi olan bağımsız küme sayısı
Aσ = 10 / 20 / 30 / 50 kPa için 44 / 22 / 13 / 3. Gereken sayı 23. Yavaş kayma sınıfında ≈ 4 bağımsız bölge var.
Kapı durumu: (a) SINIRDA, (b) GEÇMEZ. Aday elenmedi; sayılar Erdem'in kararı içindir.
**Ek 1 (12 Kasım):** Aσ literatürden 19 kPa'ya sabitlendi (doğrulanmış 10 kosismik dizi kestiriminin medyanı) ve öncül
sismisite en iyi açık katalogla (çoğunlukla ISC) yeniden sayıldı: koşulabilir bağımsız küme 39, gereken 23. (a) **GEÇTİ**
ama sonuç kırılgan: Mc + 0,5'te 18, Aσ = 39 kPa'da 11 kümeye düşüyor.

## 1. Soru ve neyi ölçmediği

TR-6 bir olasılık terimi değil, bir ölçü doğrulamasıdır: Dieterich (1994) hız-durum sismisite modeli ters
çevrildiğinde, bağımsız olarak bilinen bir gerilme değişiminin işareti ve büyüklüğü sismisite oranından geri
bulunabiliyor mu (ayak a), ve Marmara'nın açık kataloğuyla bu ölçünün 1 yıllık çözünürlüğü kaç kPa/yıl (ayak b)?
Büyük deprem olasılığına çeviri yoktur; mutlak İstanbul deprem olasılığı yazılmaz. S-7'den (asismik geçici →
olasılık çarpanı, ayırt edilemez) farkı çarpan sormamasıdır.

### 1.1 Kullanılan model (açık formüller)

Arka plan oranı r (olay/yıl, Mc üstü, kümesizleştirilmiş), arka plan gerilme hızı τ̇₀, Aσ, t_a = Aσ/τ̇.

- **Gerilme hızı değişimi** τ̇₀ → qτ̇₀ (q = 1 + Δτ̇/τ̇₀), t = 0'da. [0, T]'de beklenen sayı
  N₁ = r q t_a1 ln[(e^{T/t_a1} + q − 1)/q], t_a1 = Aσ/(qτ̇₀).
  **T ≪ t_a sınırı** (Marmara'da geçerli: Aσ 10–50 kPa, τ̇₀ 1–10 kPa/yıl → t_a 1–50 yıl):
  **N₁ − N₀ ≈ r T² Δτ̇ / (2Aσ)**. Yani 1 yılda hız değişimi hemen oran değişimi vermez; oran ancak biriken
  gerilmeyle (Δτ̇·t) üstel olarak kayar. Kaba el hesabı (R ∝ τ̇, anında) bu terimi atlamıştı.
- **Gerilme adımı** Δτ: N₁ = r t_a ln[(e^{T/t_a} + e^{−Δτ/Aσ} − 1)/e^{−Δτ/Aσ}], t_a = Aσ/τ̇₀.
- **Algılama (tek yanlı α = 0,05, güç 0,80):** taban oranı T_b yıllık katalogdan kestirilir; aşırı saçılım φ
  (kümesizleştirilmiş yıllık sayıların varyans/ortalaması, en az 1):
  |N₁ − N₀| ≥ z_α √(φ N₀ (1 + T/T_b)) + z_β √(φ (N₁ + N₀ T/T_b)), z_α = 1,645, z_β = 0,842.
  Kısa zaman sınırında açık çözüm: **Δτ̇_min ≈ 2 Aσ (z_α + z_β) √(φ (1 + T/T_b)) / (T^{3/2} √r)**.
- Yapay sınama (betikte değil, bu sayımda bir kez): r = 20/yıl, T_b = 10, Aσ = 10 kPa, τ̇₀ = 5 kPa/yıl için
  bulunan Δτ̇_min = 11,35 kPa/yıl; 200 000 Monte Carlo denemede güç 0,797, yanlış alarm 0,058 (normal yaklaşım
  hafif gevşek; kesin Poisson satırı ayrıca verildi).

## 2. Kodlanabilir tasarım

### 2.1 Ayak (a): küresel kör doğrulama

**Birim.** Bağımsız gerilme değişimi bilinen durum. İki sınıf:

- **(a-K) Kosismik Coulomb adımı.** Ana şok: USGS ComCat'te `finite-fault` ürünü olan, 1990–2025, M ≥ 6,0,
  derinlik ≤ 30 km. Bilinen değer: sonlu fay modelinden (ComCat ürünü; yoksa SRCMOD) Okada yarı uzayında ΔCFF,
  μ' = 0,4, 7,5 km derinlik, 10 km hücre, alıcı mekanizma bölgenin ComCat moment tensörlerinin medyanı.
  Alıcı alan: episantrdan [L/2 + 10 km, 2L] halkası, L = 10^(−3,55 + 0,74M) km. Hücreler |ΔCFF| ≥ 10 kPa ile
  "artış" ve "gölge" diye ayrılır; ±10 kPa arası atılır.
- **(a-Y) Jeodezik yavaş kayma / gerilme hızı geçicisi.** Kilauea güney yamacı (1997–2007'de 8 olay,
  Montgomery-Brown 2009, özetten doğrulandı), Boso (4–7 yılda bir, Hirose 2014, özetten doğrulandı), Salton Trough
  Obsidian Buttes (Llenos & McGuire 2011, özetten), İzmit sığ yavaş kaymaları 2015/2016/2018/2019 (Neyrinck 2024,
  özetten). Bilinen değer: yayımlanmış kayma modelinden gerilme. Sınıf ayrı satırdır, birincil hükme girmez
  (bağımsız bölge sayısı 4; aşağıda).

**Ölçü (a-K).** Her durum için gölge hücrelerinde: N₀ = olaydan önceki 5 yılın (son 30 gün hariç) kümesizleştirilmiş
(GK74) yıllık Mc üstü sayısı; N_post = olaydan sonraki [1 g, 365 g] sayısı (kümesizleştirme YOK; hız-durumda
artçı da adıma verilen yanıttır). Ters çözüm Δτ_est = Aσ ln(N_post / N₀), Aσ önceden dört değerde sabit
(10, 20, 30, 50 kPa). Durum başına tek oy: gölgede N_post < N₀ ise "işaret tuttu".

**Hüküm satırı (a).** Gölge oyu tutan durum oranı p̂, durum sayısı K, tek yanlı binom sınaması H0: p = 0,5.
H1 (gerilme ölçer işareti geri buluyor): p̂ kritik değerin üstünde (K = 23'te ≥ 16). Ters yön notu: p̂ ≤ 0,3
(gölgede artış; Hardebeck & Harris 2025'in "gölge artçıları" bulgusunun küresel karşılığı). Büyüklük satırı
(bilgi): artış hücrelerinde Spearman(ΔCFF, Δτ_est) ve |log(Δτ_est/ΔCFF)| ≤ ln 3 olan durum payı, üç Aσ için ayrı.
Negatif kontrol: aynı hücreler, sahte olay zamanı 3 yıl önce (yer değiştirme). Pozitif kontrol: artış hücreleri
(büyük olasılıkla tutar; tutmazsa hattın kendisi bozuktur).

**Güç kapısı (a).** p₁ = 0,75'i %80 güçle görmek için K ≥ 23 bağımsız durum (p₁ = 0,70 → 37; 0,80 → 18).
Bir durumun sayılması için gölge lobunda Δτ = −10 kPa'lık adımın 1 yılda görülebilmesi gerekir:
Aσ = 10 kPa'da düşüş e^{−1} = 0,37 kat → N₀ ≥ 11,6 olay/yıl; 20 kPa → 34,2; 30 kPa → 69,2; Aσ = 50 kPa'da
e^{−0,2} = 0,82 kat → N₀ ≥ 176. Formül: N₀ ≥ [(z_α + z_β √k)/(1 − k)]², k = düşüş katı (φ = 1, taban biliniyor).

### 2.2 Ayak (b): Marmara çözünürlüğü

**Katalog.** KOERI zeqdb (Boğaziçi Ü. Kandilli), `Tip = Deprem`, kutu 40,20–41,30 K, 26,30–30,30 D, 2006–2025,
büyüklük xM (KOERI tercihli büyüklük; örnek satırlarda 2006'da MD, 2018'de ML). GFZ homojen Marmara kataloğu
(10.5880/gfz.4.2.2023.002) yine indirilemedi: açılış sayfasının dosya listesi boş (`"files":[]`), datapub dizini
403. AFAD API'si tarihsel sorguya yine boş döndü. EMSC FDSN aynı kutuda yalnız karşılaştırma için indirildi
(yılda 113–1670 satır, KOERI'nin altında ve yıllar arası homojen değil).

**Segment kutuları** (fay izine göre değil, beyan edilmiş kaba kutular; enlem × boylam):
Ganos 40,45–40,90 × 26,50–27,35; Orta Marmara 40,70–41,00 × 27,35–28,60; Prens Adaları 40,78–40,98 × 28,60–29,10;
Çınarcık 40,50–40,78 × 28,60–29,35; İzmit 40,62–40,85 × 29,35–30,10. "Kuşak (zarf)" beşinin zarfıdır ve tek bir
değişimin bütün kuşağa eşit düştüğü en iyi durumu gösterir (fiziksel olarak iyimser).

**Mc.** Yıllık, kutu bütünü: max(MAXC + 0,2; GFT-%90). Dönem Mc'si iki kuralla: "max" (dönemdeki yıllık Mc'lerin
en büyüğü; ana satır) ve "medyan" (duyarlılık). Segment havuz Mc'si bilgi olarak verilir.

**Kümesizleştirme.** Gardner–Knopoff 1974 pencereleri (ana satır) ve Uhrhammer 1986 (daha dar; duyarlılık), kutu
kataloğunun Mc üstü olaylarında, büyükten küçüğe, önce ve sonra pencereli.

**Dönemler.** 2006–2025, 2011–2025, 2016–2025 (hepsi verildi; seçim yapılmadı).

**Güç.** §1.1 formülleri, T = 1 yıl (adım için ayrıca T = 3 ay), Aσ ∈ {10, 20, 30, 50} kPa, τ̇₀ ∈ {1, 5, 10} kPa/yıl,
φ = 1 ve φ = ölçülen.

**Hüküm satırı (b), koşulursa.** Segment başına, aylık adımlı Dieterich ters çözümü (T-rate, 10.5281/zenodo.20251771,
ya da aynı denklemlerle temiz oda kodu) ile Δτ̇(t); "bilinen" değerler: İzmit yavaş kaymaları (2015, 2016-12,
2018-03, 2019-11) ve 23 Nisan 2025 Mw 6,2'nin komşu segmentlere Coulomb adımı. Ölçü: bilinen pencerelerde
|Δτ̇_est| > Δτ̇_min olma oranı, 1000 rastgele takvime karşı. 2026 kör.

## 3. Gerçek sayım (ayak b)

`python3 -I -B kayit/turetme/tr6/tr6_sayim.py <ham_dizin> tr6_sayim.json` (≈ 2 sn). Ham dosyalar depo dışında:
`/mnt/project-files/turetme/tr6-ham/` (3,1 MB; KOERI ve EMSC yıl dosyaları); SHA-256 listesi `kayit/turetme/tr6/tr6_ham_sha256.txt`. İndirme: 2006–2017 yıllık, 2018 ve 2022 aylık,
öteki 2019–2025 yılları çeyreklik sorgu (sunucu büyük yanıtları ve eşzamanlı sorguları kesiyor; toplam ≈ 2 saat sunucu süresi).
Her parçada sunucunun beyan ettiği "Bulunan: N" ile ayrıştırılan satır sayısı eşit ve "Liste sonu" işareti var.
Her yıl dosyasındaki bütün tarihler kendi yılında; 2026 satırı yok (okuyucu yine de süzer).

**3.1 Katalog ve Mc**

KOERI kutu kataloğu 2006–2025: 15 638 olay (yılda en az 273 olay (2007), en çok 2025 yılında; o yılın sayısı 2 026 olaydır ve 2026 yılı verisi değildir). Yıllık Mc (MAXC + 0,2 ile GFT-%90'ın büyüğü):

| 2006 | 2007 | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2,8 | 2,9 | 2,9 | 2,8 | 2,8 | 2,7 | 2,5 | 2,2 | 2,1 | 2,0 | 2,1 | 1,9 | 1,8 | 1,9 | 2,0 | 1,9 | 1,8 | 1,8 | 1,9 | 2,0 |

GFT-%90 tek başına 2013 sonrası 1,4–1,8 veriyor; ana satır tutucu olan MAXC + 0,2'yi kullanır. Mc 2012–2013'te
≈ 0,7 birim düştü (ağ yoğunlaşması); 2006–2025'i tek Mc ile kullanmak ya 2,9'a çıkmayı (oran çok düşer) ya da
eksik yılları içeri almayı (b = 0,78, açıkça eksik) gerektirir. **Ana satır: 2016–2025, Mc 2,1, b 0,85, Mc üstü
3071 olay.** Segment havuz Mc'leri 2016–2025'te 1,7–2,0 (İzmit kutusunda 50'den az olay, hesaplanmadı).
**Mc ≈ 1 düzeyine inen açık katalog yok:** GFZ homojen kataloğu ve Fabisch 2026 dizi kataloğu indirilemedi ya da
yalnız dizi pencerelerini kapsıyor (AV-2 envanteri).

**3.2 Arka plan oranı (olay/yıl, Mc üstü). Hücre: GK74 r (φ) / Uhrhammer86 r.** φ = kümesizleştirilmiş yıllık
sayıların varyans/ortalaması.

| Dönem · Mc kuralı | Mc | b | Ganos | Orta Marmara | Prens Adaları | Çınarcık | İzmit | Kuşak (zarf) |
|---|---|---|---|---|---|---|---|---|
| 2006–2025 · max | 2,9 | 1,13 | 1,15 (1,4) / 1,55 | 6,7 (1,6) / 11,5 | 0,8 (0,6) / 1,05 | 3,6 (1,4) / 7,3 | 0,6 (1,7) / 0,8 | 15,6 (3,4) / 26,9 |
| 2006–2025 · medyan | 2,0 | 0,78 | 6,4 (4,8) / 10,9 | 24,6 (5,0) / 66,4 | 5,8 (3,0) / 10,8 | 12,8 (2,0) / 38,2 | 2,8 (1,3) / 3,8 | 69,7 (9,6) / 168 |
| 2011–2025 · max | 2,7 | 0,99 | 1,4 (1,1) / 2,0 | 8,3 (1,6) / 17,2 | 1,4 (1,0) / 1,9 | 4,3 (1,5) / 8,2 | 0,33 (1,1) / 0,4 | 18,6 (1,7) / 36,0 |
| 2011–2025 · medyan | 2,0 | 0,86 | 5,3 (5,0) / 9,1 | 23,2 (6,3) / 65,0 | 5,6 (3,6) / 10,9 | 13,1 (1,7) / 31,5 | 2,0 (0,9) / 2,4 | 65,5 (8,4) / 151 |
| **2016–2025 · max (ana)** | **2,1** | **0,85** | **2,3 (1,7) / 4,9** | **20,3 (5,7) / 49,0** | **2,9 (2,3) / 6,7** | **9,8 (0,6) / 21,3** | **1,1 (0,3) / 1,1** | **48,1 (6,9) / 103** |
| 2016–2025 · medyan | 1,9 | 0,84 | 3,5 (1,2) / 7,3 | 24,6 (7,6) / 66,1 | 4,5 (3,5) / 10,2 | 14,0 (1,5) / 34,0 | 1,4 (0,5) / 1,6 | 64,2 (12,2) / 151 |

Kümesizleştirme payı (kutu): GK74 %25–41 arka plan, Uhrhammer %54–68. Ham (kümesizleştirilmemiş) Mc üstü oran
2016–2025'te Ganos 5,3, Orta Marmara 135, Prens Adaları 9,9, Çınarcık 37,6, İzmit 1,4, kuşak 214 olay/yıl; Orta
Marmara'nın hamı 2019 Silivri ve 2025 Mw 6,2 dizilerini taşır. Kaba araştırma notundaki "segment başına yılda
≈ 50–80 M ≥ 2" (EMSC ham) ile kümesizleştirilmiş gerçek arka plan arasında ≈ 2,5–30 kat fark var (kutular aynı değil); en büyük kayıp Prens
Adaları (kilitli segment, yılda ≈ 3) ve İzmit'te (yılda ≈ 1).

**3.3 Algılanabilir en küçük gerilme hızı değişimi, T = 1 yıl, %80 güç, α = 0,05 (kPa/yıl).**
Hücre: Aσ = 10 kPa / Aσ = 50 kPa; GK74, φ ölçülen (en az 1), τ̇₀ = 5 kPa/yıl.

| Dönem · Mc | Ganos | Orta Marmara | Prens Adaları | Çınarcık | İzmit | Kuşak (zarf) |
|---|---|---|---|---|---|---|
| 2006–2025 · max | 41 / 145 | 22 / 86 | 42 / 146 | 26 / 101 | 59 / 185 | 21 / 83 |
| 2006–2025 · medyan | 34 / 125 | 20 / 80 | 29 / 111 | 18 / 73 | 28 / 106 | 17 / 70 |
| 2011–2025 · max | 34 / 127 | 19 / 78 | 33 / 123 | 25 / 97 | 65 / 198 | 14 / 59 |
| 2011–2025 · medyan | 37 / 135 | 23 / 90 | 32 / 120 | 17 / 68 | 29 / 110 | 17 / 68 |
| **2016–2025 · max (ana)** | **33 / 124** | **23 / 91** | **35 / 129** | **15 / 63** | **37 / 134** | **18 / 72** |
| 2016–2025 · medyan | 25 / 98 | 24 / 94 | 34 / 127 | 16 / 64 | 33 / 124 | 20 / 80 |

Ana satırın ayrıntısı (2016–2025, Mc 2,1, GK74, φ ölçülen; Aσ = 10 / 30 / 50 kPa):

| Segment | r | Hız artışı τ̇₀ = 1 / 5 / 10 (Aσ 10) | Hız, Aσ 30 / 50 (τ̇₀ 5) | Adım, 1 yıl (Aσ 10 / 30 / 50; τ̇₀ 5) | Adım, 3 ay (Aσ 10) | Kesin Poisson (φ = 1): gereken kat |
|---|---|---|---|---|---|---|
| Ganos | 2,3 | 25 / 33 / 46 | 79 / 124 | 22 / 48 / 75 kPa | 25 kPa | 3,4 |
| Orta Marmara | 20,3 | 18 / 23 / 30 | 57 / 91 | 15 / 34 / 53 kPa | 18 kPa | 1,65 |
| Prens Adaları | 2,9 | 26 / 35 / 48 | 82 / 129 | 23 / 51 / 79 kPa | 26 kPa | 3,1 |
| Çınarcık | 9,8 | 13 / 15 / 19 | 39 / 63 | 9 / 22 / 35 kPa | 12 kPa | 1,96 |
| İzmit | 1,1 | 27 / 37 / 51 | 85 / 134 | 25 / 53 / 82 kPa | 27 kPa | 5,0 |
| Kuşak (zarf) | 48,1 | 14 / 18 / 22 | 45 / 72 | 11 / 26 / 41 kPa | 14 kPa | 1,40 |

**Hız düşüşü:** τ̇₀ ≤ 10 kPa/yıl iken yüklemenin tamamen durması bile 1 yılda hiçbir
segmentte görülemez (betik "inf" veriyor); yalnız kuşak zarfında, Uhrhammer ve φ = 1 ile 7,7 kPa/yıl.
**En iyimser hücre** (bütün dönem, Mc kuralı, kümesizleştirme, φ seçenekleri içinde; Aσ = 10 kPa, τ̇₀ = 5):
kuşak zarfı 4,3 kPa/yıl ve adım 2,4 kPa; tek segmentte Orta Marmara 6,6 kPa/yıl, adım 3,7 kPa. Bu hücrelerin
hepsi "2006–2025 · medyan" satırından gelir, yani Mc'nin 2013 öncesinde açıkça eksik olduğu (b = 0,78) ve
φ = 1 varsayılan satırdan; geçerli sayılmamalı.

Kaba el hesabıyla kıyas: kaba hesap "1 yılda ≈ 5–25 kPa" diyordu (adım eşdeğeri; R ∝ τ̇ anında kabul edilmişti).
Ayrıntılı sayımda, ana satırda, segment başına **adım 9–25 kPa (Aσ 10) ile 35–82 kPa (Aσ 50)**, **hız 15–37
kPa/yıl (Aσ 10) ile 63–134 kPa/yıl (Aσ 50)**. Yani kaba hesabın alt ucu (5 kPa) hiçbir segmentte tutmadı; adım
olarak 2–3 kat, hız olarak 3–5 kat kötüleşti. Bu turdaki öteki kaba sayımlarla aynı yönde.

**3.4 Bilgi notları.** Gündüz payı (05–15 UTC; beklenen ≈ 0,42): Ganos GK74 0,61 (n = 23), öteki segmentler
0,27–0,44. Ganos kutusunda taş ocağı patlaması kirlenmesi olabilir (2012 sonrası `Tip = Deprem` süzgecine rağmen);
ayrıştırılmadı. EMSC FDSN aynı kutuda 2017–2022'de yılda 113–258 satır döndü (KOERI 522–1305); EMSC birleşik
kataloğu Marmara arka plan oranı için kullanılamaz.

## 4. Gerçek sayım (ayak a)

`python3 -I -B kayit/turetme/tr6/tr6_a_sayim.py tr6_a_sayim.json` (ComCat, 155 count sorgusu, ≈1 dk). Sayılan
yalnız üstveri ve olay öncesi sayılar; hiçbir olay sonrası oran görülmedi.

| Satır | Sayı |
|---|---|
| Havuz: ComCat `finite-fault` ürünlü, 1990–2025, M ≥ 6,0, derinlik ≤ 30 km | **155 olay** |
| Gölge lobunda kaba N₀ ≥ 1 olay/yıl (halka M ≥ 2,5 sayısı × 0,25 / 5 yıl) | 122 |
| N₀ ≥ 11,6/yıl (Aσ = 10 kPa'da −10 kPa görülür) | **54 olay → 44 bağımsız küme** (300 km ve 5 yıl içindekiler tek küme) |
| N₀ ≥ 34,2/yıl (Aσ = 20 kPa) | 28 olay → 22 küme |
| N₀ ≥ 69,2/yıl (Aσ = 30 kPa) | 16 olay → 13 küme |
| N₀ ≥ 176/yıl (Aσ = 50 kPa'da −10 kPa görülür) | **3 olay / 3 küme** (2010 Maule, 2011 Tohoku, 2023 Alaska M7,2) |
| Gereken bağımsız durum (p₁ = 0,75 / 0,70 / 0,80) | 23 / 37 / 18 |
| (a-Y) yavaş kayma sınıfı: bağımsız bölge | ≈ 4 (Kilauea 8 olay, Boso ≈ 5–6, Salton 1, İzmit 4); olay sayısı ≈ 18–19 ama bölge içi bağımlı |

Okuma: (a-K) için durum sayısı Aσ'ya bütünüyle bağlı. Aσ = 10 kPa'da 44 küme kapıyı (23) geçer; 20 kPa'da 22 ile
bir eksik kalır; 30 kPa'da 13, 50 kPa'da 3. Literatürdeki tek doğrulanmış değer (Catalli 2008, 40 kPa) 30 ile 50
arasına düşer. 44 kümenin çoğu dalma-batma megathrust olayı (Japonya, Şili, Endonezya, Alaska, Kuril);
1999 İzmit listede (N₀ ≈ 86/yıl, ComCat'in o bölgedeki M ≥ 2,5 kapsamıyla). Doğrultu atımlı kıta içi alt küme
sayılmadı (mekanizma sorgusu yapılmadı). ComCat M ≥ 2,5 sayıları ABD dışında eksik; N₀ bölgeye göre farklı Mc'de
ölçülmüş olur. Bu yüzden 44 bir üst sınırdır; gerçek koşuda yerel katalog (JMA, CSN, BMKG) gerekir ve JMA dışındakiler
bu turda sınanmadı. (a-Y) sınıfı 4 bağımsız bölgeyle kapıya (≥ 18) hiçbir varsayımla ulaşmaz; üstelik Montgomery-Brown
2009 özetine göre Kilauea yavaş kaymalarının hepsi bir mikrodeprem fırtınasıyla çakışıyor; fırtınasız yavaş kayma
sayımı olmadığı için işaret sınaması seçim yanlılığına açık (çıkarım).

## 5. Beklenen sinyal (literatürden; doğrulama durumu işaretli)

| Sinyal | Büyüklük | Kaynak ve durum |
|---|---|---|
| Batı Marmara 2013 olası yavaş kayması, Mw 4,6 dizisine Coulomb adımı | "birkaç onda bir kPa" (≈ 0,1–0,5 kPa) | Tary vd. 2026, 10.1093/gji/ggag429, **özetten doğrulandı** |
| İzmit sığ yavaş kaymaları (2016-12, 2018-03 Mw 4,3, 2019-11 Mw 4,4; dönüş ≈ 1,3 yıl), 2–5 km sünme üstünde | Gerilme yayımlanmadı. Nokta kaynak kaba hesabı (M₀/2πr³, bu belge): 5 km'de ≈ 6 kPa, 10 km'de ≈ 0,8, 20 km'de ≈ 0,1 kPa | Olaylar Neyrinck vd. 2024, 10.1016/j.epsl.2024.119104, **özetten doğrulandı**; kPa sayısı **doğrulanmadı** (türetme) |
| 2025 Mw 6,2'nin Çınarcık'a aktardığı gerilme | +0,204 kPa | EarthArXiv 10.31223/x5qj6q, **hakemsiz, tek yazar** (araştırma notundan) |
| Kilitli segmentin tektonik yükleme hızı | τ̇ ≈ μv/(πD): v = 10–15 mm/yıl, D = 11–15 km, μ = 30 GPa → **6–13 kPa/yıl** | v: Ergintav 2014 (10.1002/2014gl060985) Prens Adaları kayma açığı 10–15 mm/yıl, **özetten doğrulandı**; D = 11 km İzmit kilitlenme derinliği Neyrinck 2024, **özetten**; vida dislokasyonu çevirisi **bu belgenin türetmesi** |
| Yıl ölçekli yükleme değişimi | Yükleme hızının %10–50'si → **≈ 0,6–6,5 kPa/yıl**. TR-11'in GNSS sınırı (5,4 mm/yıl derin kayma hızı değişimi) aynı çeviriyle 3,4–4,7 kPa/yıl | Oran aralığı **varsayım**; TR-11 sayısı defterden |
| 1999 sonrası viskoelastik gerilme evrimi (Marmara) | Sayı okunmadı | DeVries 2016 (10.1002/2016gc006313) özetinde Marmara için yıl başına değer yok; **doğrulanamadı** |
| Aσ | 0,04 MPa (Umbria-Marche 1997 en çok olabilirlik) | Catalli 2008, 10.1029/2007jb005356, **özetten doğrulandı**; Marmara için ölçülmedi |

Kıyas için kullanılacak üst sınırlar: **adım sinyali ≤ 1 kPa** (segment ölçeğinde; 5 km yakın alan hariç),
**hız sinyali ≤ 6,5 kPa/yıl** (yükleme hızının yarısı kadar bir değişim; iyimser).

## 6. Kapı kuralı ve sonuç

**Açıklama:** kural, 2006–2015 için yapılan bir deneme koşusunun sayıları görüldükten sonra yazıldı (o koşuda
segment başına hız 21–46 kPa/yıl çıkmıştı). Eşikler bu yüzden sinyal tarafında iyimser seçildi.

**Kural (b).** Oran ρ = algılanabilir en küçük değer / beklenen sinyalin üst ucu. Ana satır (2016–2025, Mc max,
GK74, φ ölçülen, τ̇₀ = 5), segment başına, iki ölçü ayrı:
- hız ölçüsü: sinyal üst ucu 6,5 kPa/yıl; adım ölçüsü: sinyal üst ucu 1 kPa;
- ρ ≤ 1 → GEÇER; 1 < ρ ≤ 3 → SINIRDA; ρ > 3 → GEÇMEZ. Aσ = 10 kPa (en elverişli) ve 50 kPa ayrı yazılır.

| Segment | Hız ρ (Aσ 10 / 50) | Adım ρ, 1 yıl (Aσ 10 / 50) | Durum |
|---|---|---|---|
| Ganos | 5,2 / 19 | 22 / 75 | GEÇMEZ |
| Orta Marmara | 3,5 / 14 | 15 / 53 | GEÇMEZ (hız, Aσ 10'da eşiğe yakın) |
| Prens Adaları | 5,4 / 20 | 23 / 79 | GEÇMEZ |
| **Çınarcık** | **2,4** / 9,7 | 9,2 / 35 | **hız: SINIRDA yalnız Aσ = 10 kPa'da**; adım GEÇMEZ |
| İzmit | 5,7 / 21 | 25 / 82 | GEÇMEZ |
| Kuşak (zarf, bilgi) | 2,7 / 11 | 11 / 41 | hız SINIRDA yalnız Aσ 10'da; adım GEÇMEZ |

**Sonuç (b): GEÇMEZ.** Yavaş kayma ölçeğindeki adımlar (≤ 1 kPa) her seçenekte 9–82 kat altta kalıyor; en
iyimser geçersiz hücrede bile 2,4 kat. Yıl ölçekli yükleme değişimi için tek SINIRDA hücre Çınarcık'ta (ve kuşak
zarfında) Aσ = 10 kPa ile sinyalin üst ucuna (yüklemenin yarısı) karşı; sinyalin orta değeri (≈ 3 kPa/yıl, TR-11
ölçeği) alınırsa ρ ≈ 5, Aσ = 40 kPa (Catalli 2008) alınırsa ρ ≈ 8. Hız düşüşü (yüklemenin azalması) hiçbir
segmentte görülemez.

**Kural (a).** K = Aσ'ya göre gölge lobu N₀ eşiğini geçen bağımsız küme sayısı; gereken 23 (p₁ = 0,75).
K ≥ 23 her Aσ'da → GEÇER; yalnız bir kısmında → SINIRDA; hiçbirinde → GEÇMEZ. Ayrıca (a-Y) için gereken ≥ 18
bağımsız bölge.

**Sonuç (a): SINIRDA.** (a-K) Aσ = 10 kPa'da 44 küme (üst sınır) ile geçer, 20 kPa'da 22 ile bir eksik, 30 kPa'da
13, 50 kPa'da 3 ile geçmez. Literatürde doğrulanmış tek değer (40 kPa) geçmeyen tarafa düşer. (a-Y) yavaş kayma
sınıfı ≈ 4 bağımsız bölgeyle GEÇMEZ. Geçen tarafın da iki kısıtı var: kümelerin çoğu megathrust (Marmara'ya
mekanizma aktarımı yok) ve N₀ sayıları ComCat'in bölgeye göre değişen tamlığıyla ölçüldü.

Aday elenmedi: (a-K) ayağı Aσ ≤ 20 kPa ve yerel kataloglarla koşulabilir durumda; (b) ayağı bugünkü açık katalogla
kapıdan geçmiyor ve defterdeki yeniden açma şartı (Mc ≈ 1 katalog, ≲ 1 kPa/yıl) bu sayımla ölçülmüş oldu:
1 yıllık pencerede 1 kPa/yıl'a inmek için r'nin ana satıra göre kabaca (15/1)² ≈ 225 kat (Çınarcık) artması
gerekir. b = 0,85 ile Mc'yi 2,1'den 1,0'a indirmek r'yi ≈ 10^(0,85 × 1,1) ≈ 8,7 kat artırır (Çınarcık r ≈ 85/yıl):
aynı formülle 1 yılda 5,2–7,1 kPa/yıl (Aσ = 10 kPa, τ̇₀ 1–10, φ = 1). Yani Mc ≈ 1 katalog 1 yıllık pencerede
yetmez. Pencere 5 yıla çıkarsa 0,65–1,8 kPa/yıl (bugünkü katalogla 5 yılda 1,7–5,4). Bu satırlar varsayımsal
kataloğa uygulanmış formüldür, ölçüm değildir.

## 7. Maliyet, iş yükü, riskler, defterle örtüşme

**Maliyet:** 0 €. Bu sayım: KOERI ≈ 2 saat sunucu süresi (yavaş ve eşzamanlı sorguyu kesiyor), ComCat 155 sorgu,
OpenAlex özetleri; hesap saniyeler.

**İş yükü, koşulursa.** (b): ters çözüm kodu (T-rate ya da temiz oda Dieterich + ETAS), segment başına aylık adım,
1000 rastgele takvim: 1–2 gün, 0 €; ama kapı geçmediği için beklenen sonuç önceden "ayırt edilemez" olur.
(a-K): her kümeye sonlu fay modeli (ComCat ürünü ya da SRCMOD), Okada ΔCFF ızgarası (temiz oda ya da açık kod),
bölge katalogları (JMA, CSN, BMKG, GeoNet, ANSS) ve her birinde Mc; 44 kümede ≈ 1–2 hafta iş, 0 € (veriler açık;
JMA dışı katalogların erişimi bu turda sınanmadı).

**En büyük üç risk.**
1. **Aσ belirsizliği sonucu belirliyor.** Hem (a) kapısı hem (b) çözünürlüğü Aσ ile doğrusal ölçekleniyor; 10 ile
   50 kPa arasında kapı geçerden geçmeze dönüyor. Aσ'yı aynı veriden kestirmek (Catalli 2008 türü) ters çözümü
   döngüsel yapar; Cocco 2010 özeti parametrelerin "güçlü ilişkili" olduğunu yazıyor (10.1029/2009jb006838,
   özetten doğrulandı). Ön kayıtta Aσ önceden sabitlenmezse ölçü serbest parametreye dönüşür.
2. **Katalog tamlığı ve homojenliği.** KOERI Mc'si 2012–2013'te 0,7 birim düştü; Marmara'da ağ değişimi ile oran
   değişimi ayrışmaz. Mc ≈ 1 açık katalog yok (GFZ dosyası yine indirilemedi). (a)'da ComCat M ≥ 2,5 sayıları ABD
   dışında eksik, 44 küme bir üst sınır.
3. **"Bilinen" gerilmenin kendisi bilinmiyor.** Coulomb modelinin gölge lobları gözlemle tutarsız çıkıyor
   (Hardebeck & Harris 2025, Kumamoto ve Ridgecrest'te gölge artçılarının yarısı açıklanamıyor; özetten
   doğrulandı); yavaş kayma sınıfında bilinen olayların hepsi fırtınayla çakışıyor (Kilauea), fırtınasız olay sayımı yok.
   (a) sonucunun olumsuz çıkması gerilme ölçerin mi, Coulomb modelinin mi başarısız olduğunu ayırmaz.

**Defterle örtüşme.**
- **S-7 / EL-3 / TK-E1** (asismik geçici → olasılık çarpanı): TR-6 çarpan sormaz; ama (a-Y) sınıfı aynı olay
  türlerini kullanır. Örtüşme orta.
- **CRS-ETAS** (Marmara, ayırt edilemez) ve **KURESEL-CRS-GELGIT** (kısa vadede ETAS üstüne ≈ 0): (a-K) ayağı
  Coulomb + hız-durum modelinin ileri sınamasının tersidir; aynı fizik, farklı ölçü (olasılık puanı değil işaret
  ve büyüklük geri kazanımı). Örtüşme yüksek; (a-K) olumlu çıksa bile bu iki kapalı adayın sonucunu değiştirmez.
- **ETAS-TABAN**: arka plan oranı r ve kümesizleştirme aynı nicelik; TR-6 bunu gerilmeye çevirir. Örtüşme düşük.
- **AV-2** (düşük Mc katalog, güç yok): AV-2'nin dersi "kaba el hesabıyla güç sayma" idi; burada güç açık Poisson
  formülü ve Monte Carlo denetimiyle sayıldı. TR-6'nın yeniden açma şartı AV-2 aşama 1 ile aynı kataloğa bağlı;
  yukarıdaki sayım o kataloğun da 1 yıllık pencerede yetmeyeceğini gösteriyor.
- **TR-11**: GNSS ölçeği (5,4 mm/yıl ≈ 3,4–4,7 kPa/yıl) sismisite ölçüsünden (15–37 kPa/yıl) 3–10 kat daha ince;
  Marmara'da yıl ölçekli yükleme değişimi için sismisite, GNSS'in gerisinde.
- **TR-4** (dv/v): o da en iyi durumda gerilme hızını ölçer; TR-6'nın (b) sonucu TR-4 için bir kıyas çizgisi verir.
- **VE-5 / K10**: 1999 sonrası viskoelastik gerilme evrimi (b)'nin "bilinen" değeri olabilirdi; sayısı okunmadı.

## Ek 1: (a) ayağı için Aσ ve katalog kapısı (12 Kasım)

Betik `kayit/turetme/tr6/tr6_a_kapi.py`, çıktı `tr6_a_kapi.json`. Yalnız numpy ve standart kütüphane kullanıldı; koşu
`python3 -I -B` ile yapıldı. Ham yanıtlar depo dışında duruyor: 1706 dosya, 48 MB; yer
`/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr6a/onbellek/`. Her dosyanın URL'si ve
SHA-256'sı `URL_LISTESI.tsv` içinde. Hüküm satırı koşulmadı: olay sonrası tek sorgu yapılmadı, oran değişimi ve ters
çözüm hesaplanmadı. Bütün sorgular olaydan 30 gün önce bitiyor; en geç bitiş 2025-11-06.

### E1.1 Aσ, veriden önce literatürden

Doğrulama türleri:
- **ö**: sayı OpenAlex özetinde geçiyor.
- **t**: sayı açık tam metinde okundu.
- **i**: sayı başka bir açık tam metnin aktarımı. Bu satırlarda kaynağın kendi metni kapalı ya da sayıyı özetinde vermiyor.

Wiley (403), Springer (istemci sınaması) ve Bristol deposu (Cloudflare) erişimi reddetti; hiçbiri atlatılmadı.

| Bölge | Ortam | Aσ (kPa) | Yöntem | Kaynak | Doğr. |
|---|---|---|---|---|---|
| Landers 1992 | doğrultu atımlı | ≈ 17 | erken artçılarla en çok olabilirlik, gerilme belirsizliği dahil | Hainzl 2009, 10.1029/2008jb006011 | ö |
| G. Kaliforniya 1986–2003 | doğrultu atımlı | 40 | CRS ileri modeli | Toda 2005, 10.1029/2004jb003415 | i (Cocco 2010) |
| Kobe 1995 | doğrultu atımlı | 35 ± 15 | artçı oranı ile ΔCFF ilişkisi | Toda 1998, 10.1029/98jb00765 | i (CORSSA 2010, Hainzl 2010/2024) |
| Kagoshima 1997 | doğrultu atımlı | 40 | hız-durum ileri modeli | Toda & Stein 2003, 10.1029/2003jb002527 | i (Cocco 2010) |
| Umbria-Marche 1997 | normal | 40 | en çok olabilirlik | Catalli 2008, 10.1029/2007jb005356 | ö |
| Japonya 1970–2003 | karışık | 12 | fiziksel-istatistiksel kümelenme | Console 2006 | i (CORSSA, Hainzl 2024) |
| Tohoku 2011 | megathrust | 18 (belirsizliksiz modelde 100) | CRS, Monte Carlo | Cattania 2014, 10.1002/2014jb011183 | t (Tablo 2) |
| Parkfield 2004 | doğrultu atımlı | 4 (belirsizliksiz modelde 8) | CRS, Monte Carlo | Cattania 2014 | t |
| Orta İtalya 2016–17 | normal | ≈ 20 | CRS parametre eniyileme | Mancini 2019, 10.1029/2019jb017874 | i (Hainzl 2024) |
| G. Kaliforniya, 6 ana şok | doğrultu atımlı | < 10 (küçük bölmelerde ≈ 5) | a-pozitif erken artçı, c-değeri | Hainzl, Page & van der Elst 2024, 10.1785/0220240176 | ö, t |
| Izu 2000 sürüsü | volkanik dayk | 10 | gerilme hızı ile oran ilişkisi | Toda 2002, 10.1038/nature00997 | i |
| Westmorland 2020 | yavaş kayma + akışkan | 0,4–1,2 | yavaş kaymayla sürülen hız-durum | Sirorattanakul 2022, 10.1029/2022jb024693 | i (Hainzl 2024) |
| Val d'Agri | baraj kaynaklı | 0,8 | poroelastik + hız-durum | Rinaldi 2020, 10.1016/j.jrmge.2020.04.003 | i |

**Doğrulanamadı.** Aşağıdaki çalışmalarda sayı ne özette ne de erişilebilen bir açık metinde bulunabildi:
- Dieterich, Cayol & Okubo 2000 (Kilauea)
- Segall 2006 (Kilauea yavaş kayması)
- Llenos 2009 ve Llenos & McGuire 2011 (Salton)
- Toda & Enescu 2011 (Japonya CSEP)
- Cattania 2018 (Canterbury): tam metin indirildi ama metin çıkarımında Aσ sayısı okunamadı.
- Jiang, Trugman & González 2026 (T-rate, Reno)

**Aσ'ya çevrilemedi.** Heimisson & Segall 2020 (Bárðarbunga) yalnız boyutsuz A veriyor (1e-5–0,01). Hainzl,
Zöller & Wang 2010 bir benzetim taraması; 17 kPa için "etkin uydurma parametresi" diyor. Ader 2014 nitel: tek kayma
bloğu modeli aσ'yı ciddi biçimde düşük kestirebilir.

**Sabitleme kuralı.** Kural, sayımdan önce yazıldı. Yalnız doğal kosismik tektonik diziler alındı (tablonun ilk 10
satırı). Her çalışmadan tek değer, yazarın tercih ettiği satır kullanıldı. Üst sınırlar kendi değeriyle girdi; bu
Aσ'yı büyüttüğü için tutucu yöndedir.
- 10 değer: 4, 10, 12, 17, 18, 20, 35, 40, 40, 40 kPa.
- **Medyan 19 kPa. Ön kayıt değeri: Aσ = 19 kPa.**
- Duyarlılık için çeyrekler alındı: **13 ve 39 kPa**. Aralık 4–40 kPa.
- Sürü, yavaş kayma ve indüklenmiş satırlar eklenince 13 değerin medyanı 17 kPa.

Hainzl 2024, eski kestirimlerin eksik erken artçılar yüzünden yukarı sapmış olabileceğini yazıyor; bu, kapı açısından
elverişli yönde bir belirsizlik. Gerekli eşik: Δτ = −10 kPa, 1 yıl, %80 güç. Bu eşik Aσ = 19 kPa için
N₀ ≥ 31,4/yıl, 13 kPa için 17,1/yıl, 39 kPa için 111,2/yıl.

### E1.2 Katalog erişimi

Her servis küçük sorgularla sınandı. User-Agent genel tutuldu, hiçbir form doldurulmadı.

| Servis | Durum |
|---|---|
| ComCat | erişildi (155 olay) |
| ISC Bulletin FDSN | erişildi (155 olay). JMA, CWB/TAP, BJI, GUC gibi yerel ajans katkılarını taşıyor; Japonya'da M 1 düzeyine iniyor. |
| GeoNet FDSN | erişildi (8 olay). `limit` parametresini reddediyor. |
| EMSC | erişildi (9 Akdeniz–İran olayı) |
| KOERI zeqdb | erişildi (6 Türkiye çevresi olayı; yavaş) |
| INGV FDSN | erişildi; havuzda kutusuna düşen olay yok |
| JMA birleşik | yıllık `hypo` zip dosyaları açık. Doğrudan kullanılmadı; aynı JMA hiposantrları ISC üzerinden geldi. |
| CENC | veri portalı kayıt istiyor; **atlandı** |
| CSN (Şili) | toplu sorgu arayüzü bulunamadı; Şili için ISC kullanıldı |
| AFAD | tarihsel sorguya boş döndü |
| NOA FDSN | 204 döndü; Yunanistan için EMSC ve ISC kullanıldı |
| BMKG | sınanmadı; Endonezya için ISC kullanıldı |

### E1.3 Yeniden sayım yöntemi

Halka ve 0,25 lob/arka plan payı `tr6_a_sayim.py` ile aynı. Dört değişiklik var:

1. **Pencere** [t − 5 y, t − 30 g].
2. **Derinlik ≤ 40 km.** Alıcılar 7,5 km'de; dalan levha içindeki derin olaylar gölge lobunun nüfusu değil. Tüm
   derinlikler bilgi satırında ayrıca veriliyor.
3. **Mc her katalogda ayrı.** Her katalog için üç örnek pencere (45 g) alındı. Mc, en az 50 olaylı pencerelerde
   MAXC + 0,2 değerlerinin en büyüğü.
4. **Sayım.** Sayı eşiklere yakınsa 77 olayda tam sayım yapıldı; uzaksa 9 olayda örnekten tahmin edildi.

Her olay için en büyük N₀'ı veren katalog seçildi. Bu katalog 86 olayın 82'sinde en düşük Mc'yi veren katalogla aynı.
Olaylara göre en iyi katalog:

| En iyi katalog | Olay sayısı |
|---|---|
| ISC | 66 |
| ComCat (Alaska, Kaliforniya, Hawaii) | 14 |
| GeoNet | 4 |
| EMSC | 1 |
| KOERI | 1 |
| Sığ halkada Mc kestirilemedi (okyanus ya da uzak bölge) | 69 |

**Duyarlılık: Mc + 0,5.** Halka geneli MAXC, kıyıdaki yoğun ağın etkisiyle açık deniz loblarında iyimser olabilir.
Örneğin Japonya'da ISC Mc'si 0,4–1,8 çıkıyor.

### E1.4 Kapı

Tablodaki her hücre koşulabilir bağımsız küme sayısı (300 km / 5 yıl kuralı).

| Satır | Aσ 13 | **Aσ 19 (sabit)** | Aσ 39 | 10 / 20 / 30 / 50 (eski ızgara) |
|---|---|---|---|---|
| ComCat, eski sayım (M ≥ 2,5, tüm derinlik) | 33 | 24 | 6 | 44 / 22 / 13 / 3 |
| ComCat, kendi Mc'si, ≤ 40 km | 20 | 14 | 4 | 22 / 13 / 8 / 1 |
| ISC, kendi Mc'si, ≤ 40 km | 39 | 32 | 8 | 46 / 32 / 21 / 8 |
| **En iyi açık katalog, ≤ 40 km (ana)** | 46 | **39** (48 olay) | 11 | 53 / 39 / 24 / 9 |
| En iyi açık katalog, Mc + 0,5 | 31 | 18 | 9 | 33 / 16 / 11 / 5 |
| En iyi açık katalog, tüm derinlik (bilgi) | 52 | 44 | 23 | 59 / 43 / 31 / 12 |

Ana satırda Aσ = 19 kPa için 39 kümenin mekanizma dökümü (ComCat moment tensörü):

| Mekanizma | Küme |
|---|---|
| ters, düşük eğimli (çoğu dalma-batma megathrust; Hawaii ayrılma yüzeyi ve Kuril gibi birkaçı dahil) | 20 |
| doğrultu atımlı | 12 (1999 İzmit, 2023 Kahramanmaraş, 2016 Kumamoto, 2019 Ridgecrest, 2002 Denali dahil) |
| ters, diğer | 4 |
| normal | 3 |

Mc + 0,5 satırında döküm 10 / 5 / 3 / 0.

**Gereken K.** Tek yanlı tam binom sınaması kullanıldı: H0 p = 0,5, p₁ = 0,75, α = 0,05.
- K = 23'te kritik değer 16. Gerçek α = P(X ≥ 16 | 0,5) = 0,047; güç P(X ≥ 16 | 0,75) = 0,804.
- Güç eğrisi testere dişli: K = 24 / 25 / 27'de güç 0,77 / 0,73 / 0,79'a düşüyor. K ≥ 28'de güç kalıcı olarak 0,8'in
  üstünde (K = 28'de kritik 19, güç 0,86).
- Normal yaklaşım: K = [(z_α·0,5 + z_β·√(p₁(1 − p₁))) / (p₁ − 0,5)]² = [(0,822 + 0,365)/0,25]² = 22,5.
- **Gereken: K = 23 (kritik 16) ya da her K ≥ 28.**

**Hüküm (a-K): GEÇTİ, ama kırılgan.**
- Sabit Aσ = 19 kPa ve en iyi açık katalogla 39 bağımsız küme var. Bu 23'ün ve kalıcı eşik 28'in üstünde.
- Aσ = 13 kPa'da da 46 küme ile geçiyor.
- Aσ = 39 kPa'da (üst çeyrek) 11 kümeyle geçmiyor.
- Mc + 0,5 ile 18 kümeyle geçmiyor; Aσ = 13 kPa'da ise 31 kümeyle geçiyor.

Önceki "44 üst sınır" kısmen yanlış yönde bir sayıydı. ComCat kendi Mc'si ve ≤ 40 km ile yalnız 14 küme verir.
Kazanç ISC'den geliyor: JMA ve yerel ajansların katkısı. Megathrust payı yarıya yakın (20/39); doğrultu atımlı alt küme
tek başına 12 ile geçmez. (a-Y) yavaş kayma sınıfı değişmedi (≈ 4 bölge, GEÇMEZ).

**Koşu öncesi ön kayıt şartı (kırılganlık yüzünden).** Gerçek koşuda Mc halka için değil, her gölge lobu için ayrı
kestirilir. Kapı, yalnız olay öncesi veriyle yeniden sayılır. Lob Mc'siyle bağımsız küme sayısı Aσ = 19 kPa'da 23'ün
altına düşerse hüküm satırı koşulmaz. Aday elenmez; yeniden açma şartı şudur: lob Mc'siyle K ≥ 23 (ya da K ≥ 28).

### E1.5 Koşulursa iş yükü ve maliyet

Tahmin; ölçülmedi.

- **Gerilme kaynağı.** Sonlu fay modeli olarak her olayın ComCat `finite-fault` ürünü kullanılır (havuz bu ürünle
  tanımlı; alt fay kayma dosyası). Duyarlılık için SRCMOD'da varsa ikinci model alınır.
- **Alıcı düzlem kuralı (önceden).** Halkadaki olay öncesi ComCat moment tensörlerinin medyanı; 0–40 km, en az 5
  çözüm. Yetmezse ana şok düzlemi kullanılır. Duyarlılık: ana şok mekanizması.
- **Hesap.** ΔCFF, μ' = 0,4, 7,5 km. Okada (1992) dikdörtgen dislokasyonu numpy ile yazılabilir (≈ 300 satır).
  Okada 1992'nin yayımlanmış sınama değerleriyle doğrulanır.
- **Hesap yükü.** Ana satırda 48 olay var. M 7,5 için ≈ 3 000 hücre × 400 alt fay. M 9 halkasında ≈ 3·10⁵ hücre;
  vektörlü numpy ile dakikalar sürer. Toplam CPU < 1 saat.
- **Katalog.** Olay sonrası 1 yıllık pencereler ISC'den alınır; bu turdaki hızla birkaç saat sunucu süresi.
- **Toplam.** 2–4 gün ajan işi, bulut oturumunda. Makine gerekmez; maliyet **0 €**.

### E1.6 Sınırlar

- Halka/lob geometrisi ve 0,25 payı kaba bir beyandır (önceki sayımla aynı).
- ISC'de büyüklük türleri karışık (JMA M, ML, mb). MAXC, bu karışık türlerin üzerinde hesaplandı.
- 9 olayın sayısı örnekten tahmin; bunlar eşiğin ya çok altında (N₀ 1–3) ya da çok üstünde (Tohoku, Noto 2024, 2003 Tokachi-oki).
- ISC'nin son iki yılı gözden geçirilmemiş bülten.
- Kümeleme ilk-gelen sırasıyla yapıldı.
