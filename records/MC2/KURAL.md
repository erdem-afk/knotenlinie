# MC2 — hesap öncesi sabit kural

Bu dosya yeniden okuma çalıştırılmadan önce yazıldı; sonuçtan sonra değişmez. SHA256'sı `OLCUM.json` içindedir.
Yeni model koşulmaz; girdiler mevcut defterler (`$KNOTENLINIE_RUNS/defter/<deney>/`) ve AH kodudur. Mühür: 2021+ deprem verisi okunmaz.

## 1. NBD sayı testi (dağılım parametresi)
- Test: iki kuyruk, δ1 = P(X ≥ N), δ2 = P(X ≤ N), X ~ NBD(ortalama Λ, varyans V). Geçer ⇔ min(δ1, δ2) ≥ 0,025
  (Zechar 2010; pyCSEP `negative_binomial_number_test`). V ≤ Λ ise Poisson.
- Varyans biçimi: **V(Λ) = Λ + a·Λ²** (NB2). Tek parametre a ≥ 0 yalnız ayar dönemi verisinden kestirilir.
- Kestirim (İtalya günlük, eşik başına ayrı): HORUS ≤2010 kataloğu (`tools.ortak_zemin.veri`, yalnız `zaman < 2011-01-01`),
  CSEP İtalya ızgarası ve [0,30) km (`olay_kutulari`), M ≥ eşik. Pencere uzunluğu hedef pencereninki (1826 gün).
  Pencereler 1985-01-01'den başlar, her 30 günde bir kayar, bitişi 2011-01-01'i aşmaz. Her pencerede olay sayısı;
  m = ortalama, v = örnek varyansı (ddof=1); **a = max(0, (v − m)/m²)**. Üst üste binen pencereler a'yı aşağı çeker
  (gerçek bağımsız pencere ≈ 5); bu bir sınırlamadır, kural değişmez.
- Duyarlılık (yalnız OLCUM.json'da, hükme girmez): a×0,5 ve a×2.
- Uzun vade (AH): aynı pencere kuralı; katalog AH'nin bölgesel kataloğu, hedef türüne göre (kümesiz / bütün), M ≥ 4,95,
  `kayma 30 gün`, başlangıç 1985-01-01, <2011-01-01.
- Kaliforniya (SCSN): ≤2010 katalogunda dönem Mc'si sabit değil; NBD uygulanmaz (yalnız Poisson N). Bu açık satırdır.

## 2. İkili olabilirlik
- Hücre-gün-kutu başına p = 1 − exp(−λ). Gözlenen: hücre-gün-kutuda ≥1 olay.
- Tam fark (defterden, simülasyonsuz): lnL_ikili = Σ_{farklı olay hücre-gün-kutusu} [ln(1 − e^{−λ}) + λ] − Λ_toplam.
  Eşik başına yalnız M ≥ eşik olaylar ve Lam sütunu. Olay başına fark IG_ikili = (lnL_aday − lnL_taban) / N.
- Simülasyonlu S ve L testleri defterde hücre-gün λ'sı olmadığı için **pyCSEP protokolüyle zaman-toplanmış** (hücre,
  büyüklük kutusu) marjinaline (`*__marjinal.npz`, `beklenen`) uygulanır: p = 1 − exp(−Λ_kutu); gözlenen = kutuda ≥1 olay;
  simülasyon: gözlenen dolu kutu sayısı kadar *farklı* kutu, ağırlık ∝ Λ_kutu, ardışık örnekleme (reddederek).
  S: kutular hücreye toplanır (büyüklük toplamı). L: hücre×büyüklük. Alt kuyruk p = (#sim ≤ gözlenen)/R
  (pyCSEP tanımı; ayrıca (1+k)/(1+R) de saklanır).
- **Tekrar sayısı R = 10000; tohumlar:** S-Poisson 20261005, M-Poisson 20261006, S-ikili 20261007, L-ikili 20261008
  (`numpy.random.default_rng`). Aynı sayılar bütün satırlarda.
- Uzun vade: tek pencere, tek büyüklük kutusu (≥4,95); S ve L aynı (hücre) vektörde.

## 3. HAC / Diebold–Mariano SE
- Günlük kazanç D_t ve olay sayısı n_t (karisim.gun_kazanci). IG = ΣD/N. u_t = D_t − IG·n_t.
- Newey–West (Bartlett çekirdek): SE = sqrt( T/(T−1) · [ Σu_t² + 2 Σ_{l=1..L} (1 − l/(L+1)) Σ_t u_t u_{t−l} ] ) / N.
- **L = floor(4·(T/100)^(2/9))**, T = takvim günü sayısı (1826 → 7; 3653 → 8). Yan satır: **L = 7 gün**.
- L = 0 ⇒ günlük bloklu sandwich (haftalık blok SE'nin gün-bloklu ikizi); z_HAC = IG/SE_HAC.
- Haftalık blok SE (`kor_ac.blok_ozeti`) yan yana raporlanır; hükümde ikisi de gerekir.
- Uzun vade (AH) tek zaman penceresidir: HAC tanımsız, uygulanmaz.

## 4. İki yanlı testler ve tek yönlü z
- Eşleştirilmiş T ve Wilcoxon W iki yanlı p'leri `puan.eslestirilmis` ile (olay λ'ları + Λ toplamları).
- Tek yönlü z > 1,645, iki yanlı %90 güven düzeyine denktir (iki yanlı p < 0,10); tablo bunu açık yazar.
- W öncelik kuralı: N < 30 ise W, değilse T hükme girer.

## 5. Hüküm kuralı (eski / yeni)
- **Eski**: başarı ⇔ IG > 0 ∧ z_blok > 1,645; IG ≤ 0 ⇒ başarısızlık; öbürü belirsiz.
- **Yeni**: başarı ⇔ IG > 0 ∧ z_blok > 1,645 ∧ z_HAC > 1,645 ∧ (N<30 ? p_W < 0,10 : p_T < 0,10);
  IG ≤ 0 ⇒ başarısızlık; öbürü belirsiz. Tutarlılık (N-NBD, S) ayrıca raporlanır, hükme eklenmez (eski kural da böyleydi).
- Eşikler yan yana: M ≥ 2,95 ve 3,95 (+4,95). Kaliforniya: defterdeki iki eşik (2,8 ve 2,9); M ≥ 3,95 için gün Λ'sı
  defterde yok, satır açık bırakılır.

## 6. Kanıt düzeyi
- Her satırda `kanit_duzeyi`: bugün **"SP-ic"** (2011–2015 / 2011–2020 iç doğrulama, sözde ileriye dönük). İleride "SP-kor", "P-karsi-SP".

## 7. Satırlar
- İtalya 2011–2015: R−LM, AJ−LM, T1 eşit {R-ortak-kaskad, ETAS-LM}−LM, E7 {AJ, ETAS-LM}−LM; eşikler 2,95 / 3,95 / 4,95.
  R = R-ortak-kaskad (U defteri). Defterler: U/, AJ/.
- Kaliforniya SCSN 2011–2020: D1 − D0 (Y/).
- Uzun vade 2011–2015, hedef kümesiz (hüküm) ve bütün, M ≥ 4,95: AH-GR-kapali − {HAZFX, TripleS, MPS04} (İtalya).
  Ağır koşu çıkarsa (yerel makinede 4 GB / 60 dk) hesap sunucusunda koşulur.

## Ek 1 (15 Ekim, inceleme sonrası)
Uzun vade satırlarında z_HAC şartı aranmaz (§3: HAC tanımsız, tek pencere). Hüküm yine §5'in N kuralıyla verilir
(N<30 → `puan.eslestirilmis`'in asimptotik p_W'si, aksi p_T). Exact W, bağ-düzeltmeli işaret-çevirme permütasyonu ve
bağ bayrağı yalnız yan sütundur, hükme girmez. Bu ek hiçbir hükmü değiştirmez.
İlk sürüm SHA256: 769540e59c7f78940bba7be47f3fcf32411feff7a4f6e5a4ca86e1ab9c6eef7c (ölçüm bu sürümle yapıldı).
