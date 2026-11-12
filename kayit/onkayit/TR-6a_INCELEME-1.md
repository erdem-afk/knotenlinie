DÜZELTMEYLE KABUL

# TR-6a ön kayıt: bağımsız inceleme 1

İncelenen: `TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md` (TASLAK sürüm 1, 12 Kasım 2026). Dayanak olarak okundu:
`TR-6_SAYIM.md` §2.1 ve Ek 1 (E1.1–E1.6); `kayit/turetme/tr6/` altındaki `tr6a_onkayit_sayilar.py`,
`tr6a_onkayit_sayilar.json`, `tr6a_olay_listesi.json` ve `tr6_a_kapi.py` (`kumele`, `gereken_n0`, `maxc`,
`fdsn_ayristir`). Biçim için `TR-2_INCELEME-1.md` ve `TR-11_INCELEME-1.md` örnek alındı.

Körlük: hiçbir katalog sorgusu yapılmadı. Hiçbir lobda oran, oran değişimi ya da ΔCFF hesaplanmadı. Olay öncesi ham
önbellek (`…/scratchpad/tr6a/onbellek/`) **açılmadı**. Gerekçe B3'te: bu önbellekteki dosyalar başka adayların olay
sonrası pencerelerini de kapsıyor. Bu yüzden "0 büyüklük" düzeltmesi önbellekte doğrulanmadı (K3).

Bütün hesaplar `python3 -I -B` ile ve yalnız yapay sayılar, binom ya da Poisson ifadeleri ve dondurulan listenin
üstverisiyle (zaman, konum, M, L, Ek 1 Mc ve N0) yapıldı. Betikler depo dışında, karalama dizinindedir:
`/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/inceleme_tr6a/denetim1.py` … `denetim5.py`.
Bu betikler taslağın koduna dayanmaz: oy eşikleri scipy ile ayrıca yazıldı. Depoya bu rapor dışında dosya eklenmedi,
`__pycache__` kalmadı.

## Hüküm

Tasarımın iskeleti sağlam: birim bağımsız küme, tek hüküm satırı, olay öncesi kapı, önceden çözülmüş testere dişi,
kontroller ve olumsuz sonucun iki açıklamayı ayıramayacağının dürüstçe yazılması. Sayılar yeniden üretildi:
- §6.1 tablosu K = 23–45 için birebir tutuyor.
- K = 28–200 aralığında güç hiç 0,80'in altına düşmüyor.
- H0 altında her n için P(D = 1 | n) ≤ 0,5 ve P(A = 1 | n) ≤ 0,5. Ana, negatif kontrol ve D2 pencerelerinde
  n = 1–30 000 için en büyük değerler 0,499997 ve 0,500000.
- P(D) 0,4585 (N0 31,36) değeri tutuyor.
- sha256 değerleri tutuyor (liste 01d73cad…, `tr6_a_sayim.json` 8da8ba3c…, `tr6_a_kapi.json` 5a90b0eb…).

Ancak metin bu hâliyle dondurulursa sınavın **α'sı korunmuyor**, ve bu sapma H1 yönünde. Sapmanın üç kaynağı var.
Taslağın denetimleri üçünü de yakalamıyor:
1. **Aşırı saçılım:** "P(D) ≤ 0,5 tanım gereği" savı yalnız Poisson H0'da geçerli (A1).
2. **Ana şok sonrası tamlık kaybı:** bölge geneli Mc_son bunu düzeltmiyor (A2). Ne pozitif ne negatif kontrol bu kaybı
   görür.
3. **Gözden geçirilmemiş ISC bülteni** (A4).

Ayrıca kırığa 20 km iç sınır, sonucu bilinen iki küme bilinerek yazıldı (A3). Ön indirmeler de 30 adayın olay sonrası
penceresini kapsıyor (B3).

Bu bulguların hepsi metinle ve olay öncesi veriyle düzeltilebilir; yeni bir olay sonrası sorgu gerekmez. Aşağıdaki
düzeltme metinleri işlenince dondurulabilir. Düzeltmelerin bedeli K'de 2–5 küme ve olası bir p₀ yükselmesidir. Yazarın
P(K < 23) ≈ 0,5 önseli bu yüzden biraz yükselir; §10'da bunun yazılması gerekir (B5).

---

## A. Engelleyici bulgular

### A1. Aşırı saçılım altında H0 düşüş oyu olasılığı 0,5'i aşıyor; "kural tutucudur" savı yanlış

- **Bulgu 1: Poisson H0 altında bile gerçek α taslağın yazdığından yüksek.** Taslak α'yı yalnız N0 = 31,36'da veriyor
  (0,007–0,019). Oysa kapıdan geçen kümelerin çoğunun N0'ı çok daha büyük. Ek A'daki kaba N0 medyanı ≈ 80; Tohoku 4501,
  Noto 1913. P(D) N0 büyüdükçe 0,5'e yaklaşır:

  | N0 (/yıl) | 17,08 | 31,36 | 50 | 111,2 | 300 | 1000 | 4500 |
  |---|---|---|---|---|---|---|---|
  | P(D \| H0, Poisson) | 0,4459 | 0,4585 | 0,4680 | 0,4783 | 0,4869 | 0,4928 | 0,4966 |

  Gerçek α (K = 23, c = 16) p₀'a göre şöyle değişir:

  | p₀ | 0,4585 | 0,47 | 0,48 | 0,49 | 0,50 | 0,52 | 0,55 |
  |---|---|---|---|---|---|---|---|
  | α (K = 23) | 0,019 | 0,025 | 0,031 | 0,038 | 0,047 | 0,069 | 0,115 |

  Gerçekçi N0 karışımında α ≈ 0,025–0,035 olur, 0,007–0,019 değil.

- **Bulgu 2: aşırı saçılımda P(D) 0,5'i aşıyor.** Kümesizleştirme artıkları, ağ değişimi ve küçük diziler yıllık sayıyı
  Poisson'dan geniş dağıtır (φ = var/ortalama > 1). Model: her yılın oranı bağımsız Gamma çarpanıyla çarpılır; φ, N0'da
  yıllık sayının saçılımıdır; 4000 Monte Carlo × kesin koşullu oy. Bu modelde 335 günlük pencerenin oranı 4,9 yıllık
  pencereninkinden daha çarpık dağılır, ve medyanı ortalamasının altına düşer. Sonuç: H0 altında düşüş oyu artar, artış
  oyu azalır. Sapmanın yönü H1'dir.

  | N0 | φ | P(D \| H0) | P(A \| H0) | α K = 23 | α K = 28 | α K = 39 |
  |---|---|---|---|---|---|---|
  | 31,36 | 1,5 | 0,472 | 0,463 | 0,025 | 0,022 | 0,011 |
  | 31,36 | 2 | 0,484 | 0,463 | 0,034 | 0,030 | 0,017 |
  | 31,36 | 3 | 0,499 | 0,457 | 0,046 | 0,042 | 0,026 |
  | 31,36 | 5 | 0,516 | 0,444 | **0,064** | **0,062** | 0,042 |
  | 100 | 3 | 0,505 | 0,474 | **0,051** | 0,049 | 0,031 |
  | 500 | 3 | 0,507 | 0,483 | **0,053** | **0,050** | 0,032 |
  | 500 | 5 | 0,513 | 0,474 | **0,060** | **0,058** | 0,039 |

  (Monte Carlo standart hatası P için ≈ 0,005.) Kümesizleştirilmiş, küçük alanlı katalog sayılarında φ = 2–5 olağandır.
  Bu durumda tutuculuk payı tükenir ve α 0,05'i aşar. Taslağın §4.3'teki "bilinmeyen arka plan oranına bağlı değildir"
  cümlesi doğru, ama "oranın yıldan yıla dalgalanmasına" bağlıdır.

- **Bulgu 3: korelasyon.** Kümeler arası korelasyon (B4) X'in saçılımını ayrıca büyütür. Bu, binomun bağımsızlık
  varsayımını zayıflatır.

- **Negatif kontrol bunu yakalamıyor.** S2 aynı yapıdadır, yani aynı şişmeyi taşır. Ama yalnız X_nk ≥ c(K) olduğunda
  hükmü niteler. Bunun gücü φ = 3'te bile ≈ 0,05'tir, yani bir koruma değildir.

- **Önerilen yol.** Kök oturum kararını (tam binom, birim küme) değiştirmeden p₀'ı ampirik olarak, yalnız olay öncesi
  veriyle kalibre etmek. Bu yapılırsa yalnız binomun p₀'ı yukarı kayabilir; aşağı kayamaz.

- **Düzeltme metni (§4.3'ün son paragrafının yerine; "Sonuç: hüküm kuralının …" cümlesinden paragraf sonuna kadar):**

  > H0 altında (Poisson, sabit oran) düşüş oyu olasılığı N0'a bağlıdır: 0,4585 (N0 31,36), 0,4783 (111,2), 0,4869 (300),
  > 0,4966 (4500). Bu yüzden, p₀ = 0,5'e karşı binom sınamasının gerçek α'sı kapıdan geçen kümelerin N0 karışımına göre
  > K = 23'te 0,019 ile 0,047 arasındadır. Bu sınır yalnız Poisson H0'da geçerlidir. Yıllık sayıların aşırı saçılımında
  > (φ > 1) 335 günlük pencerenin oranı çarpık dağılır. O zaman H0 altında P(D) 0,5'i aşabilir. Örneğin φ = 3 ve
  > N0 = 100'de P(D) 0,505 olur ve K = 23'te α 0,051'e çıkar. Bu nedenle p₀ §4.6'daki sahte olay kalibrasyonuyla
  > yalnız olay öncesi veriden kestirilir ve manifestte dondurulur.

- **Düzeltme metni (yeni §4.6, §4.5'ten sonra):**

  > ### 4.6 Sahte olay kalibrasyonu (p₀, yalnız olay öncesi)
  >
  > Manifestte, hükmün her kümesinin (testere dişi atmasından önceki kapı kümeleri) temsilcisi için üç sahte zaman
  > alınır: t'_j = t0 − 395 g − 335 g · (j − 1), j = 1, 2, 3. Bu zamanların sahte son pencereleri sırasıyla
  > [t0 − 365 g, t0 − 30 g), [t0 − 700 g, t0 − 365 g) ve [t0 − 1035 g, t0 − 700 g) olur; birbirleriyle örtüşmezler.
  >
  > Her t'_j için şunlar kullanılır:
  > - gölge lobu ve hücreleri gerçek olaydakilerle aynıdır;
  > - ön pencere [t'_j − 1826 g, t'_j − 30 g), son pencere [t'_j + 30 g, t'_j + 365 g);
  > - π = 0,15720;
  > - Mc kuralı §3.5'tekidir; Mc_son, sahte son pencerenin bölge olaylarıyla alt pencere kuralına göre hesaplanır;
  > - kümesizleştirme §3.6'dakidir;
  > - oy kuralı §4.3'tekidir.
  >
  > Bu hesap için ön indirmeler t0 − 2891 g'ye kadar uzatılır. Bu sınır 2025-12-31'den önce kalır ve bütün veri olay
  > öncesidir.
  >
  > Sahte düşüş oyu D'_ij'dir; p̂₀ = Σ D'_ij / (3 K_kapı). Ana eşik şöyle seçilir:
  > - **p̂₀ ≤ 0,50:** c(K) §6.1'deki gibi kalır (p₀ = 0,5).
  > - **p̂₀ > 0,50:** c(K), P(X ≥ c | K, p̂₀) ≤ 0,05 koşulunu sağlayan en küçük c olur. Ters yön eşiği aynı biçimde,
  >   p̂₀ yerine sahte artış oyu payı p̂₀⁺ ile hesaplanır.
  >
  > Testere dişi tablosu da p₀ = max(0,5; p̂₀) ile yeniden çözülür. Hükmün K'si, kapı K'sine eşit ya da ondan küçük,
  > 23'e eşit ya da büyük ve gücü (p₁ 0,75) ≥ 0,80 olan en büyük K'dir. Böyle bir K yoksa atma yapılmaz; güç
  > olduğu gibi yazılır ve hüküm adına "(tasarım gücünün altında: güç …)" eklenir. H0 eşiği h(K) değişmez.
  > p̂₀, p̂₀⁺, c(K) ve testere dişi tablosu manifestte, olay sonrası indirmeden önce dondurulur. Sahte oyların küme
  > başına dökümü manifestte yazılır. S2 negatif kontrolü j = 1'in özel bir hâli olarak raporlanmaya devam eder.

- **Düzeltme metni (§11 madde 12'nin yerine):**

  > 12. **Koşullu oyun H0 olasılığı N0'a ve saçılıma bağlıdır.** Poisson H0'da 0,446–0,497 aralığındadır. Aşırı
  > saçılımda 0,5'i aşabilir (φ = 3, N0 = 100'de 0,505). Önlem: §4.6'daki ampirik p₀ = max(0,5; p̂₀). p̂₀ üç sahte
  > zamandan kestirilir ve aynı kümenin sahte oyları birbiriyle ilişkilidir; etkin örneklem 3K'den küçüktür. Kalibrasyon
  > ortalamayı düzeltir, saçılımı tam düzeltmez.

### A2. Ana şok sonrası tamlık kaybı: bölge geneli Mc_son yetmiyor ve iki kontrol de bunu görmüyor

- **Sızıntı sorusu (yazarın 3. noktası).** Mc_son olay sonrası veriden hesaplanır, ama lobun sayı farkından değil,
  bölgenin büyüklük dağılımının tepesinden. Kural önceden yazıldığı için araştırmacıya bir serbestlik bırakmaz.
  İşaret bilgisi sızıntısı ihmal edilebilir. Tek zayıf bağlantı "50'den az olayda +0,3" dalıdır: bölge sayısı lob
  sayısıyla ilişkilidir. Ancak bu dal iki pencereyi birlikte kestiği için H0 altında işaret yanlılığı üretmez.
  **Asıl sorun sızıntı değil, düzeltmenin yetersiz kalmasıdır.**
- **Bulgu.** MAXC, 335 günlük havuzlanmış pencerede histogramın tepesini verir. Bu tepe pencerenin büyük kısmındaki geç
  dönemin tamlığıdır. İlk haftalarda Mc(t) daha yüksektir ve bu fark +0,2 ile kapanmaz. Hesap şöyle yapıldı:
  - taslağın kendi §9 sınama biçimi kullanıldı: Mc(t) = M_ana − 4,5 − 0,75 log10(t / 1 g), keskin kesim, b = 1;
  - bölge arka plan ile Omori artçılarının karışımıdır;
  - lobda yalnız arka plan vardır (H0);
  - beklenen histogram gürültüsüz alındı.

  | M_ana | Mc_lob | Bölge Mc_son (taslak) | Lob son penceresinde algılanan pay | P(D \| H0), N0 31,36 / 100 |
  |---|---|---|---|---|
  | 7,0 | 1,5 | 1,8 | 1,000 | 0,459 / 0,477 |
  | 7,5 | 1,5 | 1,8 | 0,971 | **0,516 / 0,580** |
  | 8,0 | 2,5 | 2,8 | 1,000 | 0,459 / 0,477 |
  | 9,0 | 3,0 | 3,2 | 0,928 | **0,601 / 0,722** |
  | 9,0 | 1,8 | 3,1 | 0,870 | **0,713 / 0,872** |

  %3'lük bir kayıp bile N0 = 100'de H0 düşüş oyunu 0,58'e çıkarır. Yanlılık N0 ile büyür. En çok etkilenen kümeler,
  hükmü taşıyacak yüksek N0'lı Japonya kümeleridir (Kumamoto 534, Noto 1913, Tohoku 4501). Bu formül yakın alan
  formülüdür ve 20 km ötede bir üst sınırdır; gerçek kayıp bilinmiyor.
- **Hangi kontrol yakalar?**
  - Pozitif kontrol yakalamaz: kayıp pozitif lobu da azaltır, ama artçı artışı baskın kalır.
  - Negatif kontrol yakalamaz: olay öncesinde ana şok yoktur.
  - D1 (+0,5) ve D2 (90 g) kısmen ölçer, ama hükmü etkilemez.
- **§9 adım 2 sorunu.** Yapay sınama başarısız olursa "kural koşudan önce değiştirilmez" deniyor. Yapay veride
  başarısız olan bir kuralı gerçek veride tutmanın körlük açısından hiçbir gerekçesi yok, çünkü yapay sınama gerçek
  veri görmez. Önceden sıralanmış bir yedek merdiven yazılmalı. Ayrıca sınama yalnız N0 31,36'da yapılırsa yanlılığı
  kaçırır; yanlılık N0 ile büyür.
- **Bedel.** Alt pencere kuralı aşağıdaki senaryoların hepsinde kaybı sıfırlar (M 7,5 / Mc 1,5 → Mc_son 2,1; M 9 → 3,6).
  Mc'nin yükselmesi oyun gücünü az etkiler: kapı sınırındaki bir lobda (N0 31,36, kalıcı −10 kPa) Mc +0,3'te
  P_D 0,987'den 0,934'e, +0,5'te 0,868'e iner (denetim4).
- **Düzeltme metni (§3.5'teki "(ii) Mc_son …" maddesinin yerine):**

  > (ii) **Mc_son** alt pencerelerin en kötüsüdür. Son pencere [t0 + 30 g, t0 + 45 g), [45, 60), [60, 90), [90, 180),
  > [180, 365) günlük alt pencerelere bölünür. Her alt pencerede bölgenin bütün hücrelerindeki olaylardan MAXC + 0,2
  > hesaplanır; Mc_son bunların en büyüğüdür. 50'den az olaylı bir alt pencere bir sonrakiyle birleştirilir; sonuncusu
  > 50'ye ulaşmazsa bir öncekiyle birleştirilir. Hiçbir birleşim 50'ye ulaşmazsa Mc_son = Mc_lob + 0,3 olur.
  > Negatif kontrolde ve sahte olaylarda (§4.6) aynı alt pencere düzeni sahte t0'a göre kurulur. Gerekçe: havuzlanmış
  > MAXC pencerenin geç dönemini gösterir. Yapay sınamada (Helmstetter biçimi) bölge geneli tek MAXC, M 7,5'te lobun
  > son penceresinden %3, M 9'da %7–13 olay kaybetti; bu da H0 düşüş oyunu 0,52–0,87'ye çıkardı. Alt pencere kuralı
  > bu kaybı sıfırladı.

- **Düzeltme metni (§7 tablosuna yeni satır, S6'dan sonra):**

  > | **S7 nötr kontrol** | Aynı K temsilci. Bölgede \|ΔCFF\| ≤ 2 kPa olan ve r_k'si gölge lobunun en uzak hücresinin r_k'sini aşmayan hücreler. Kendi Mc_lob'u, aynı Mc_son ve Mc_kul kuralı, aynı oy (X_nt, Y_nt). Kapı yok; n = 0 ise oy 0. Ayrıca gölge ve nötr oyların eşleşik tek yanlı kesin işaret (McNemar) sınaması: a = #(D_gölge = 1, D_nt = 0), b = #(D_gölge = 0, D_nt = 1), p = P(Binom(a + b, 0,5) ≥ a). | ana K |

- **Düzeltme metni (§6.2'ye, madde 2'den sonra yeni madde 2a):**

  > 2a. **Nötr kontrol (§7 S7):** H1 verilmiş ve X_nt ≥ c(K) ise hüküm **"ayırt edilemez (nötr bölgede de düşüş:
  > tamlık ya da ağ yapay olgusu)"** olur ve §13'e hiçbir şey taşınmaz. H1 verilmiş, X_nt < c(K) ve eşleşik McNemar
  > p > 0,10 ise hüküm **"H1 (nötr kontrolden ayrışmadı)"** diye adlandırılır. (Yapay hesap: gölgede p 0,75, nötrde
  > 0,46 iken McNemar p ≤ 0,10'un gücü K = 23'te 0,67, K = 28'de 0,75, K = 37'de 0,86.)

- **Düzeltme metni (§9 adım 2'deki üçüncü alt maddenin yerine):**

  > - ana şok sonrası tamlık kaybı sınaması: yapay kataloğa Mc(t) = M_ana − 4,5 − 0,75 log10(t / 1 g) uygulanır
  >   (Helmstetter vd. 2006 biçimi; sabitler sınama için seçildi). Izgara: M_ana ∈ {7,0; 7,5; 8,0; 9,0},
  >   Mc_lob ∈ {1,0; 1,8; 3,0}, N0 ∈ {31,36; 100; 500; 4500}, bölgede artçı payı ∈ {0; 0,9}. Δτ = 0 dünyasında §3.5
  >   kuralıyla gölge düşüş oyu oranı, her hücrede o N0'ın kesin Poisson H0 değerini (§4.3) 0,02'den fazla aşmamalıdır
  >   (en az 4000 deneme). Aşarsa yedekler sırayla denenir ve tutan ilki bağlayıcı olur:
  >   (a) alt pencere sınırları [30, 40), [40, 50), [50, 60), [60, 90), [90, 180), [180, 365);
  >   (b) (a) ile birlikte Mc_son'a +0,2 eklenir;
  >   (c) (b) ile birlikte ana son pencere [t0 + 90 g, t0 + 365 g) olur (π = 275/2071, D2 ana satır olur).
  >   Hiçbiri tutmazsa TR-6a "yöntem yapay sınamada yetersiz" diye kapanır; olay sonrası veri indirilmez. Bu sınama
  >   gerçek veri görmediği için yedek seçimi körlüğü bozmaz. Seçilen yedek manifestte yazılır.

### A3. Kırığa 20 km iç sınır, sonucu bilinen iki küme bilinerek yazıldı (yazarın 1. noktası)

- **Ne kadar ciddi?** Ön kayıtta parametre seçimi sonuç bilgisiyle yapılmamalıdır. Burada yazar, Kumamoto ve
  Ridgecrest'te gölge artçılarının yakın alanda olduğunu bilerek, onları dışarıda bırakan bir sınır seçti ve bunun H1
  lehine olduğunu kendisi yazıyor. 20 km'nin fiziksel bir gerekçesi var (küresel konum hatası 5–15 km). Ama bu iki
  kümede konum hatası ≈ 1 km'dir: JMA hiposantrları ISC üzerinden, Kaliforniya'da ComCat. Bu iki kümede sınırı
  gerekçelendiren hata yok, bilinen sonuç var. Ek A'ya göre ikisi de kapıdan rahat geçiyor (Kumamoto N0 534,
  Ridgecrest 75). Hükmün K'si 23–30 bölgesinde olacaksa iki oy c(K) ile h(K) arasındaki farkın önemli bir parçasıdır.
  D3a satırı bunu yalnız ölçer, hükmü korumaz.
- **Kural nasıl körleştirilir?** Tek yalın yol, sonucu bilinen birimleri ana hükümden çıkarmaktır; bu yol yöne
  bakmaz. Kuralı "literatürden bağımsız" bir ölçüte (ör. 0,25 L) çevirmek ise yeni bir serbestlik doğurur ve yazar o
  ölçütün de bu iki kümeye etkisini bilir. Tohoku'nun bilinen sonucu (nominal gölgede artış) H1 aleyhine ve 425 km'lik
  iç Japonya bölgesine ilişkin. 20 km kuralı ona dokunmaz. Ana hükümde kalması tutucudur, ama ayrıca raporlanmalıdır.
- **Düzeltme metni (§3.4 "Gerekçe" maddesinin sonuna):**

  > Bu sınır, Kumamoto 2016 (us20005iis) ve Ridgecrest 2019 (ci38457511) kümelerinin gölge artçılarının yakın alanda
  > olduğu bilinerek yazıldı. Bu yüzden bu iki olayı içeren kümeler **ana hükümden çıkarılır**. Çıkarma kapıdan önce,
  > kümelemeden sonra yapılır: bu olaylardan birini içeren bir küme bütünüyle çıkar; kümelemenin kendisi değişmez. Bu iki
  > küme B4 satırında ayrıca raporlanır. Tohoku 2011 (official20110311054624120_30) kümesi ana hükümde kalır. Bilinen
  > sonucu H1 aleyhinedir ve bu sınırdan etkilenmez. O da B4'te ayrıca yazılır.

- **Düzeltme metni (§7 tablosuna yeni satır):**

  > | B4 bilinen sonuçlu kümeler | Kumamoto ve Ridgecrest kümelerinin (ana hükümden çıkarılan) ve Tohoku kümesinin D, A, n_on, n_son, Δτ_est değerleri. Ayrıca bunlar eklenmiş (Kumamoto, Ridgecrest) ya da çıkarılmış (Tohoku) hâliyle X, K ve c(K). Hükmü değiştirmez. | ana K ± 3 |

- Körlük beyanının son cümlesi şöyle değişir: "§3.4'teki kırığa uzaklık sınırı bu bilgiyle yazıldı; bu yüzden
  Kumamoto ve Ridgecrest kümeleri ana hükümden çıkarıldı (§3.4, §7 B4)."

### A4. Gözden geçirilmemiş ISC bülteni: kural yetersiz, etkilenen ISC kümeleri ana hükümden çıkmalı (yazarın 4. noktası)

- **Bulgu.** Gözden geçirilmemiş dönemde ajans katkıları (özellikle JMA) eksik ya da gecikmeli olabilir. Bu durumda
  son pencerede hem küçük olaylar azalır hem de büyüklük türü bileşimi değişir. İkisi de lobda sahte düşüş üretir.
  Etkilenen ISC kümeleri tam da en yüksek N0'lılardır: Noto 2024 (ISC Mc 0,4, N0 1913) ve Hyūganada 2024 (Mc 1,0,
  N0 426). A1'deki hesaba göre bu kümelerde küçük bir eksiklik bile düşüş oyunu neredeyse kesinleştirir.
  - Kontroller yakalamıyor. Negatif kontrol gözden geçirilmiş döneme düşer. Pozitif kontrol yalnız eksiklik çok büyükse
    tutmaz.
  - D6 satırı yalnız bilgidir. Ayrıca ComCat'ten sayılan iki adayı da yanlışlıkla çıkarır (us7000kg30 ve
    nc75095651, ComCat en iyi). 2023-12-31 sınırı ISC'den okunmadı.
  - Koşu adaylarından 12'sinin son penceresi bu sınırı aşıyor; 10'unun en iyi kataloğu ISC. Ek A'da etkilenen
    temsilciler: Kahramanmaraş (son penceresinin yalnız 37 günü sınır sonrası; EMSC ve KOERI yedekleri var), Noto ve
    Hyūganada (yalnız ISC).
- **Düzeltme metni (§3.5 "Katalog seçimi" maddesinin sonuna):**

  > Seçilen katalog ISC ise ve son pencere 2023-12-31T23:59:59'u aşıyorsa (ISC gözden geçirilmiş bülteninin varsayılan
  > sınırı; ISC'den okunmaz), o katalog bu olay için seçilemez. Seçim, olayın `ek1_kataloglar` listesindeki öteki
  > kataloglar arasında aynı kuralla (en büyük kapı N0'ı) yapılır. Kapıdan geçen başka katalog yoksa olay ana hükümden
  > çıkar ve D6 satırında raporlanır. Bu kural kapı sayımından önce uygulanır ve manifestte yazılır. ComCat, GeoNet,
  > EMSC ve KOERI bu kuraldan etkilenmez.

- **Düzeltme metni (§7 D6 satırının yerine):**

  > | D6 gözden geçirilmemiş ISC | §3.5'teki ISC kuralıyla ana hükümden çıkan olaylar, ISC ile ve aynı kurallarla eklenir; kapı yeniden. Yalnız bilgi. | kendi K'si |

- §11 madde 2'nin son cümlesine eklenir: "Bu yüzden son penceresi bu sınırı aşan ISC olayları ana hükme girmez (§3.5)."

---

## B. Önemli bulgular

### B1. Pozitif kontrolün kapısı yok; yapısal nedenlerle tutmayabilir ve H1'i sebepsiz düşürebilir

- **Bulgu.** S1, ana K'nin bütün kümelerini kullanıyor; pozitif hücresi ya da olayı olmayan küme 0 oy alıyor. Başarı
  ölçütü X⁺ ≥ c(K), yani K = 23'te 16 küme. Megathrust kümelerinde (Ek 1'de 20/39) pozitif loblar büyük ölçüde kırık
  kenarında, 20 km iç sınırın içinde ya da açık denizde, olaysız kalır. Hat doğru çalışsa bile X⁺ < c(K) olabilir. Bu
  durumda yorum kuralı 1, H1'i "ayırt edilemez" yapar. Kontrolün başarısızlığı hattın değil geometrinin sonucu olur.
- **Düzeltme metni (§7 S1 satırının "Tanım" hücresinin yerine):**

  > Ana K temsilcilerinden pozitif lobunun olay öncesi N0⁺'ı (Mc_lob⁺ ile, ön pencere, kümesizleştirilmiş) ≥ 3,0 olay/yıl
  > olanlar; K⁺ bu kümelerin sayısıdır (manifestte, olay sonrası indirmeden önce). Kendi Mc_lob'u, artış oyu X⁺.
  > Başarı ölçütü X⁺ ≥ c(K⁺); c, p₀ = 0,5 ile §6.1'deki fonksiyondur. K⁺ < 10 ise S1 "koşulamadı" olur. K⁺ dışındaki
  > kümelerin oyları bilgi olarak yazılır.

- **§6.2 madde 1'e eklenir:** "S1 koşulamadıysa H1 hükmü 'H1 (pozitif kontrol koşulamadı)' diye adlandırılır."

### B2. Olay grupları: son pencere, kırık izi ve küme konumu tanımsız ya da hatalı (yazarın 7. noktası)

- **Bulgu 1: son pencere son üyeden bağımsız başlıyor.** Nepal 2015 grubunda M 7,3 artçısı t0'dan 17 gün sonra
  geliyor. Son pencere t0 + 30 g'de, yani bu olaydan yalnız 13 gün sonra başlıyor. M 7,3'ün en yoğun artçı dönemi bu
  yüzden son pencereye giriyor. Bu ilk 30 gün kuralının amacını bozar ve sonucu belirsizlik yönünde değiştirir.
- **Bulgu 2: kırık izi eşiği belirsiz.** "En büyük alt fay kaymasının %10'u" grupta grubun en büyüğüne göre okunursa,
  küçük üyenin kırığı izden düşer. Onun yakın alan artçıları da lob olur.
- **Bulgu 3: konum tanımsız.** `kumele` ve "bölge" için grubun hangi dış merkezinin kullanılacağı yazılmamış.
- **Düzeltme metni (§3.2'nin "Grubun t0'ı …" cümlesinden sonra):**

  > Grubun son üyesinin zamanı t_s'dir. Son pencere [t_s + 30 g, t0 + 365 g) olur. T_son ve π grup başına bu pencereden
  > hesaplanır: π = T_son / (1796 + T_son). Negatif kontrol, sahte olaylar ve D2 de aynı biçimde t_s'ye göre kaydırılır.
  > Kırık izi (§3.4) her üyenin kendi en büyük alt fay kaymasının %10'u eşiğiyle ayrı çıkarılır ve izler birleştirilir.
  > Grubun konumu (`kumele`, sorgu dairesinin merkezi, ızgara merkezi) en büyük M'li üyenin dış merkezidir.

- **ComCat "0 büyüklük":** K3'e bakınız.
- **`kumele`:** ilk uyan küme kuralı Ek 1 ile aynı. Bu yüzden ön kayıtta tek anlamlıdır; manifestte tek bağlantı farkı
  yazılır. Kabul. Ancak B4'e bakınız.
- **Alıcı düzlem:** K2'ye bakınız.

### B3. Ön indirmeler ve Ek 1 önbelleği, başka adayların olay sonrası pencerelerini içeriyor

- **Bulgu.** Bir adayın ön penceresi [t_B − 1826 g, t_B − 30 g), daha önceki bir A adayının son penceresini
  [t_A, t_A + 365 g) kapsayabilir. Bölgeleri örtüşebiliyorsa (dış merkez uzaklığı < 2L_A + 2L_B, kaba ölçüt), B'nin
  "olay öncesi" indirmesi A'nın olay sonrası lob olaylarını taşır. Koşu adayları arasında 44 böyle çift var ve 30 farklı
  A adayı etkileniyor (denetim5). Örnek: 2012 Hint Okyanusu ön penceresi 2008 Simeulue'nin son penceresini kapsıyor.
  - Bu yüzden §9 adım 3'teki "Manifest hiçbir olay sonrası veri içermez" ve §9 adım 5'teki "bir kez indirilir" savları
    harfiyen doğru değil.
  - Ek 1 önbelleği de aynı durumda. Bu inceleme o yüzden önbelleği açmadı.
  - Risk kodda değil, insan gözünde ve ileride yazılacak "kolaylık" kodunda: A'nın son sayımı B'nin önbelleğinden
    alınabilir.
- **Düzeltme metni (§9 adım 3'ün sonuna):**

  > Bir adayın ön indirmesi, başka bir adayın son penceresini ([t_A, t_A + 365 g)) ve bölgesini kapsayabilir. Koşu
  > adayları arasında 44 böyle çift var; 30 aday etkileniyor. Kural şudur:
  > - manifest kodu ve koşu kodu, bir adayın lob ya da bölge sayısını yalnız o adayın kendi indirmesinden üretir;
  > - hiçbir ön ham dosya insan gözüyle satır satır incelenmez;
  > - ön indirmelerde [t_A, t_A + 365 g) aralığına düşen satırlar için hiçbir özet (sayı, histogram, harita) yazılmaz.
  > Ek 1 önbelleği aynı kuraldadır. "Manifest hiçbir olay sonrası veri içermez" cümlesi, "manifest hiçbir adayın kendi
  > olay sonrası penceresinden türetilmiş sayı içermez" diye okunur.

- Körlük beyanına eklenir: "Ek 1 önbelleği başka adayların olay sonrası pencerelerini kapsıyor; yazar bu önbellekte
  yalnız Ek 1 betiğinin özet çıktılarını gördü."

### B4. Kümeler arası bağımlılık: son pencereye düşen havuz olayları

- **Bulgu.** 300 km'lik dış merkez ölçütü M 8–9 için kısadır. Ek A'da dört temsilcinin son penceresine, 2L içinde,
  başka bir büyük havuz olayı düşüyor:
  - 1994 Hokkaidō → 84 gün sonra Sanriku M 7,8 (484 km; ayrı küme);
  - 2004 Sumatra → 92 gün sonra Nias M 8,6 (aynı küme);
  - 2006 Kuril → 59 gün sonra 2007 Kuril M 8,1;
  - 2020 Simeonof → 89 gün sonra Sand Point M 7,6.

  İkinci olayın artçıları birincinin loblarında kümesizleştirilmez, çünkü ana olay lob dışındadır. Bu oy ölçmek
  istediği adımı ölçmez. 1994 çiftinde iki ayrı kümenin pencereleri aynı olayları da paylaşır; bu A1'deki korelasyonu
  besler. Etkisinin yönü çoğunlukla artıştır, yani α'yı değil gücü bozar. B3 bayrağı bunu yalnız raporlar.
- **Düzeltme metni (§3.7'ye yeni madde):**

  > - **Son pencerenin kesilmesi.** Temsilcinin son penceresinde, [t_s + 30 g, t0 + 365 g) aralığında ve bölgesinde
  >   (r_k ≤ 2L) havuzdan bir olay (grup dışı) varsa, son pencere o olaydan bir gün önce biter. T_son ve π buna göre
  >   yeniden hesaplanır. T_son < 60 g kalırsa küme ana hükümden çıkar ve B3'te yazılır. Kesme yalnız dondurulan
  >   havuz listesine dayanır (lob sayısına değil); manifestte yazılır. Kümelemenin kendisi değişmez. Ancak böyle bir
  >   olay başka bir kümenin temsilcisiyse, o kümenin ön penceresi bu temsilcinin son penceresiyle örtüşür; bu çift
  >   B3'te adıyla yazılır.

### B5. Güç iddiası ve p₁ = 0,75'in dayanağı (yazarın 8. ve 5. noktaları)

- **p₁ doğrudan oy olasılığıdır.** Bu yüzden 0,804 tanım gereği doğrudur (tablo yeniden üretildi). Ancak fiziksel
  yoruma ilişkin iki varsayım iyimserdir.
  1. **Yanlış lobların oy olasılığı.** §4.5'teki "doğru lob payı" f, yanlış lobların oyunun H0 düzeyinde (0,4585)
     olduğunu varsayıyor. Gölge sanılan yerde aslında artış varsa bu oy daha düşüktür. Mallman & Zoback'ın "her yerde
     artış" bulgusu ve Hardebeck & Harris'in gölge artçıları bunu gösteriyor. Yanlış loblarda oy 0,40 / 0,30 / 0,20
     ise gereken f 0,60 / 0,66 / 0,70 olur (0,55 değil). Hainzl vd.'nin CV ≈ 1 bulgusu göz önüne alınınca f ≥ 0,6
     iyimser bir dünyadır.
  2. **Mc_kul ile Mc_lob farkı.** Kapı Mc_lob ile sayılıyor, oy ise Mc_kul ≥ Mc_lob ile. A2 düzeltmesinden sonra bu
     fark büyük olaylarda 0,5–1,0 birime çıkabilir. Oy bu farka karşı sağlamdır: kapı sınırındaki bir lobda kalıcı
     −10 kPa için P_D, Mc farkı 0 / 0,3 / 0,5 / 1,0'da 0,987 / 0,934 / 0,868 / 0,644. Ama bu fark kapının söylediği
     gücün altına iner.
- **Aşırı tutuculuk gücü ne kadar düşürüyor?** A1'deki kalibrasyon olmadan p₀ = 0,5'e karşı sınama, gerçek H0'ı
  0,46–0,50 olan bir dünyada ek güç kaybettirmez; p₁ tanımı sabit. Kalibrasyonla p̂₀ > 0,5 çıkarsa güç belirgin
  düşer. Örneğin p̂₀ = 0,52 için c(K) şöyle olur: K = 23'te 17 (güç 0,654), K = 26'da 19 (0,685), K = 28'de 20 (0,75).
  Bu dünyada 0,80 güç ancak K ≈ 30'un üstünde gelir. A1'deki testere dişi kuralı (güç hiçbir K'de 0,80'e ulaşmıyorsa
  atma yok) bunu dürüstçe yazar. Yükselen p₀ ile düşen güç, korunmayan bir α'nın bedelidir.
- **Düzeltme metni (§4.5'in son paragrafının sonuna):**

  > Bu okuma yanlış lobların oyunun H0 düzeyinde (0,4585) kaldığını varsayar. Yanlış loblarda gerçekte artış varsa
  > (Mallman & Zoback 2007; Hardebeck & Harris 2025), oy olasılığı 0,40 / 0,30 / 0,20 için gereken doğru lob payı
  > 0,60 / 0,66 / 0,70 olur. Ayrıca oy Mc_kul ile sayılır, kapı ise Mc_lob ile. Kapı sınırındaki bir lobda Mc_kul −
  > Mc_lob = 0,3 / 0,5 / 1,0 için kalıcı −10 kPa'da P_D 0,934 / 0,868 / 0,644'tür. Tasarım gücü 0,804 yalnız
  > p = 0,75 dünyası içindir; bu dünyaya karşılık gelen fiziksel koşul iyimserdir.

- **Düzeltme metni (§10 ilk maddenin sonuna):**

  > Kumamoto ve Ridgecrest çıkarılır (§3.4). Son penceresi gözden geçirilmiş sınırı aşan ISC olayları ya başka
  > kataloğa geçer ya da çıkar (§3.5). Kısa son pencereli kümeler de çıkar (§3.7). Bu kurallar Ek A düzeyinde K'yi 37'den
  > ≈ 31–33'e indirir. Yazarın önseli bu yüzden P(K < 23) ≈ 0,55–0,6'dır.

### B6. Okada doğrulamasının yedeği zayıf; çözümü tek anlamlı belirleyen koşullara dayanmalı

- **Bulgu.** Okada 1992 Tablo 2 değerleri elde değil. Yedek olarak "Okada'nın açık DC3D kaynak kodunun çıktısı"
  öneriliyor. Ancak bu kod Fortran'dır; bulut oturumunda bir derleyici olacağı, kaynağın erişilebilir ve kullanım
  koşullarının açık olacağı doğrulanmadı. Yalnız numpy kuralıyla da çelişir. Yarı uzay elastik çözümü şu koşullarla tek
  anlamlı belirlenir: yüzeyde çekme sıfır, denge, fay üzerinde yer değiştirme süreksizliğinin kaymaya eşitliği ve
  sonsuzda sönüm. Bu koşulların sayısal denetimi, tablo değerlerinden bağımsız ve en az onlar kadar güçlü bir
  doğrulamadır.
- **Düzeltme metni (§3.3 "Doğrulama" maddesinin "Değerler okunamazsa …" cümlesinden sonrasının yerine):**

  > Tablo değerleri okunamazsa kayda "Okada 1992 tablo değerleri doğrulanamadı" diye geçer. Doğrulama o zaman yalnız
  > numpy ile şu beş sınamayla yapılır. Hepsi doğrultu, eğim ve açılma kaynaklarında, eğim 30°, 70° ve 90°'de, en az
  > 200 rastgele noktada koşulur:
  > (1) z = 0'da σ_xz, σ_yz ve σ_zz sıfırdır (|σ| / max|σ| < 1e−8);
  > (2) iç noktalarda denge: merkezi farkla hesaplanan div σ, |∇σ| ölçeğinin 1e−5'inden küçüktür;
  > (3) fay düzleminin iki yanında (±1e−6 W) yer değiştirme farkı birim kaymaya 1e−6 içinde eşittir;
  > (4) analitik türevler, yer değiştirmenin merkezi farklı sayısal türeviyle 1e−6 göreli içinde uyuşur;
  > (5) kaynak boyutu 0,01 km'ye küçültülünce sonlu kaynak, ayrıca yazılan nokta kaynak (DC3D0 karşılığı) çözümüyle
  > 1e−4 göreli içinde uyuşur. Uzak alanda (r > 20 L) aynı karşılaştırma 1e−3 içinde tutar.
  > Ek olarak King vd. (1994) dört lob işaret deseni denetlenir. Bir sınama başarısız olursa olay sonrası veri
  > indirilmez.

### B7. Sonlu fay modeli: sürüm, dosya biçimi ve dondurma

- **Bulgu.** ComCat `finite-fault` ürünleri sonradan güncellenebilir. "Tercihli (ilk listelenen)" ifadesi indirme
  anına bağlı ve manifestten koşuya kadar değişebilir. Hangi dosyanın okunacağı (`basic_inversion.param` mı, `.fsp`
  mi), çok kesimli modeller (Kaikōura, Kahramanmaraş) ve alt fay koordinatının neyi gösterdiği (merkez mi, üst kenar
  mı) yazılmamış. Bu Okada girdisini tek anlamlı yapmaz.
- **Düzeltme metni (§3.3 "Sonlu fay modeli" maddesinin yerine):**

  > - **Sonlu fay modeli.** Her üyenin ComCat `finite-fault` ürünü manifest anında bir kez indirilir. Ürün kimliği,
  >   `code`, `updateTime`, indirme zamanı ve dosyanın sha256'sı manifeste yazılır. Ham dosya
  >   `/mnt/project-files/turetme/tr6a-ham/` altına arşivlenir. Koşu yeniden indirmez; arşivdeki dosyayı sha256'sını
  >   doğrulayarak okur. Okunan dosya `basic_inversion.param`'dır. Bu dosya yoksa `.fsp` okunur; ikisi de yoksa olay
  >   "veri yok" olur. Bütün kesimler (segment) okunur. Alt fay koordinatının anlamı dosya başlığından alınır ve
  >   manifestte yazılır. Sağlama: alt fay momentlerinin toplamı (μ = 30 GPa ile değil, dosyadaki μ ya da moment
  >   sütunuyla) başlıktaki M0'ın %10'u içinde olmalıdır. Tutmazsa olay "veri yok" olur.

### B8. Veri görüldükten sonra karar bırakan iki yer

- **Bulgu 1: D satırları ana kapının yerine geçebilir mi?** §5 "K < 23 ise hüküm koşulmaz" diyor, ama D3a (5 km), D4
  ya da S5a (Aσ 13) satırlarının kapısı ana satırınkinden büyük olabilir. Bu satırların ana satırın yerine geçmediği
  açıkça yazılmamış. Manifest bütün satırların K'sini gösterecek; ana K < 23 iken "5 km'de K = 30" görmek bir baskı
  doğurur.
- **Bulgu 2: kod incelemesi manifestten sonra.** Kod incelemesi (§9 adım 4) manifestten (adım 3) sonra yapılıyor ve
  manifest S2 sonucunu içeriyor. İnceleme kodu değiştirirse manifestin yeniden koşulup koşulmayacağı yazılmamış.
- **Düzeltme metni (§5 madde 2'nin sonuna):**

  > Hükmün K'si yalnız bu ana kapının K'sidir. Hiçbir duyarlılık ya da ikincil satırın (S5a, D1, D3a, D3b, D4, D5) K'si,
  > ana K < 23 iken hüküm satırını açmaz, ana satırın yerine geçmez ve §14'teki yeniden açma şartını karşılamaz. Ana K
  > < 23 ise duyarlılık satırları da koşulmaz; yalnız kapı K'leri bilgi olarak yazılır.

- **Düzeltme metni (§9 adım 4'ün sonuna):**

  > İnceleme manifest kodunda bir hata bulursa yalnız o hata düzeltilir ve manifest yeniden koşulur. İki manifest de
  > commit edilir; farkları (K, atılan kümeler, p̂₀, S2) kayda yazılır. Bağlayıcı olan ikincisidir. Hata listesi
  > yeniden koşudan önce commit edilir.

### B9. Kümesizleştirmenin ön ve son pencerede asimetrik davranışı

- **Bulgu.** Son katalog [t0, t0 + 365 g) aralığında kümesizleştiriliyor. İlk 30 gün bir tampondur: oradaki lob içi
  olaylar ana olay olabilir, ama sayılmaz. Ön katalog ise [t0 − 1826 g, t0 − 30 g) aralığında, tamponsuz
  kümesizleştiriliyor. Ön pencerenin başında, pencereden önceki lob içi olayların artçıları bağımsız sayılıyor.
  GK zaman penceresi M 5'te 143 gün, M 6'da 499 gün; yani bu kenar etkisi önemsiz değil. Ön oran şişer ve bu H1
  lehinedir. Negatif kontrol bunu yalnız ön pencerenin kendi içinde ölçer.
- **Düzeltme metni (§3.6 "Pencereler ayrı ayrı kümesizleştirilir" maddesinin yerine):**

  > - **Pencereler ayrı ayrı ve aynı tampon yapısıyla kümesizleştirilir.** Ön katalog
  >   [t0 − 1826 g − 730 g, t0 − 30 g) aralığında kümesizleştirilir. İlk 730 günün lob içi olayları ana olay olabilir,
  >   sayılmaz. Son katalog [t0, t0 + 365 g) aralığında kümesizleştirilir; ilk 30 günün (grupta t_s + 30 g'ye kadar)
  >   lob içi olayları ana olay olabilir, sayılmaz. Sahte olaylarda (§4.6) ve negatif kontrolde aynı 730 günlük ön
  >   tampon kullanılır. Kapı yalnız ön kataloğun kümesizleştirmesiyle sayılır.

### B10. Sorgu dairesinin büyüklüğü ve satır sınırı (veri kapısı)

- **Bulgu.** R = 2L + (en uzak iz noktası) M 9 için ≈ 3000 km'dir. Japonya'da ISC Mc ≈ 1,8 ile yıllık parçalar
  `tr6_a_kapi`'deki 20 000 satır sınırını aşabilir. Kesilmiş bir yanıt sessizce eksik sayı verir. Bu ön pencerede ise
  N0'ı düşürür; son pencerede ise sahte düşüş üretir. Veri kapısında yalnız "sunucu kesmesi" anılıyor, satır sınırı
  anılmıyor.
- **Düzeltme metni (§5 madde 1'in sonuna):**

  > Satır sınırına ulaşan (dönen satır sayısı ≥ sorgunun limit değerinin %99'u) her yanıt, zaman aralığı ikiye
  > bölünerek yeniden istenir. Bölme, bütün parçalar sınırın altında kalana dek sürer. Bölünen sorgu sayısı manifestte ve
  > olay sonrası kayıtta yazılır. Son pencerede de aynı kural uygulanır. Bir parça 1 günlük aralıkta da sınırı aşıyorsa
  > olay "veri yok" olur.

---

## C. Küçük bulgular

### K1. Testere dişi çözümü: tek anlamlı, ama işlem sırası ve "ana K" tanımı yazılmalı (yazarın 6. noktası)

Atma kuralı yalnız olay öncesi veriye dayanır: kapı N0'ı, yani n_on / 4,917 yıl. n_on tamsayı olduğu için eşitlikler
olasıdır; kimliğe göre eşitlik bozma kuralı var. Gerekçe (ii) doğru: atılanlar H1 altında en düşük P_D'li kümelerdir.
Kalan belirsizlikler:
- A3, A4 ve B4 çıkarmalarının atmadan önce mi sonra mı yapılacağı;
- "sözlük sırası"nın neye göre tanımlandığı;
- ikincil satırlardaki "ana K"nin atmadan önceki mi sonraki mi olduğu.

**Düzeltme metni (§5 "En zayıf tanımı" maddesinden sonra):**

> - **Sıra:** veri kapısı → kapı (§4.2) → kümeleme → çıkarmalar (§3.4 bilinen kümeler, §3.5 ISC, §3.7 kısa son
>   pencere) → p₀ kalibrasyonu (§4.6) → testere dişi atması. Sözlük sırası, kimliğin UTF-8 bayt dizisine göre artan
>   sıradır (Python `str` karşılaştırması). §7'de "ana K" atmadan sonraki küme setidir; B1 atmadan önceki settir.

### K2. Alıcı düzlem: moment formülü ve medyan tensörün tanımsız kaldığı durum

- "M0 = √(ΣMij²/2)" ifadesi altı bileşen üzerinden okunursa yanlış olur.
- Bileşen bileşen alınan medyan tensör çift kuvvet olmayabilir, hatta izotropik bir bileşen taşıyabilir.
- USE koordinatından düğüm düzlemine dönüşüm ve rake işareti yazılmamış.

**Düzeltme metni (§3.3 alıcı düzlem madde 1 ve 2'ye ek):**

> M0 = √[(Mrr² + Mtt² + Mpp² + 2(Mrt² + Mrp² + Mtp²)) / 2]. Medyan tensörün izi çıkarılır. Özdeğerler λ1 ≥ λ2 ≥ λ3,
> özvektörler T ve P'dir. Düğüm düzlemi normalleri (T ± P)/√2'dir; kayma vektörü öteki normaldir. Rake Aki & Richards
> kuralıyla hesaplanır. Dönüşüm r → yukarı, t → güney, p → doğu'dur. Çift kuvvet payı 1 − 2|λ2|/max(|λ1|, |λ3|)
> < 0,5 ise medyan tensör kullanılmaz ve kural 3 uygulanır; manifestte yazılır.

### K3. ComCat "0 büyüklük" kuralı doğrulanmadı ve dar

Bu inceleme önbelleği açmadı (B3). "Büyüklük türü boş satırlar atılır" kuralı, "0" değerli ama türü dolu bir satırı
kaçırır. Asıl sorgu minmagnitude ile yapıldığı için bu satırlar gelmeyebilir de.

**Düzeltme metni (§3.5 "Olay seçimi" maddesindeki kalın cümlenin yerine):**

> **Büyüklük türü boş olan ya da büyüklüğü sorgu tabanının (Mc_halka − 0,05) altında olan satırlar atılır.** Atılan
> satır sayısı katalog ve pencere başına manifestte yazılır.

### K4. Olayın hücreye ve loba atanması tanımlı değil

**Düzeltme metni (§3.4'e ek madde):**

> - **Olayın atanması:** olayın dış merkezi aynı izdüşümle düzleme taşınır ve içine düştüğü 10 km hücrenin sınıfını
>   alır. Hücre sınıfı hücre merkezindeki ΔCFF'den gelir. r_k hücre merkezi için hesaplanır. Olay derinliği yalnız
>   ≤ 40 km süzgecine girer.

### K5. Kayma modeli belirsizliğinin lob işaretini çevirdiği hücreler

CV ≈ 1 ise −10 kPa'ya yakın hücrelerin önemli bir kısmının işareti belirsizdir. S6 bunu yalnız SRCMOD'un kapsadığı
alt kümede ölçer, ve SRCMOD erişimi doğrulanmamış.

**Düzeltme metni (§7 tablosuna bilgi satırı):**

> | D8 güçlü gölge | Gölge lobu ΔCFF ≤ −30 kPa hücreleri; kapı yeniden. Yalnız bilgi. | kendi K'si |

### K6. Tanımsız oranlar

Δτ_est için n_on = 0 olabilir: D1'de, S1'de ya da Mc_kul ile kapı dışı lobda. Bu durumda değer tanımsızdır (0/0 ya da
x/0). Spearman'da −∞ değerin sıralaması da belirtilmemiş.

**Düzeltme metni (§4.4'e ek):**

> n_on = 0'da Δτ_est "tanımsız" yazılır ve medyana girmez; sayısı yazılır. Spearman'da −∞ en küçük sıra alır,
> tanımsızlar dışarıda kalır.

### K7. §6.1 tablosundaki "ters yön: X ≤ t" sütunu

Metin bu sütunun kullanılmadığını söylüyor. Tabloda kalması okuru yanıltır. Sütun kaldırılmalı ya da başlığa "(kullanılmaz)"
eklenmeli. Ters yön eşiği ayrıca p̂₀⁺ ile yeniden hesaplanır (A1).

### K8. Megathrust ve beklenen K (yazarın 2. noktası)

Kapı kuralı bu sorunu dürüstçe taşıyor. K lob tanımından sonra, yalnız olay öncesi veriyle sayılıyor; K < 23 ise
"güç yok" çıkıyor ve aday elenmiyor. B8'deki cümle eklenince kaçış yolu da kapanır. Bir ekleme gerekiyor: manifest K'yi
mekanizma sınıfına göre ve "gölge hücrelerinin kaçı r_k < 20 km nedeniyle düştü" sayısıyla birlikte yazmalı. Böylece
"güç yok" çıkarsa nedeni belgelenmiş olur.

**Düzeltme metni (§9 adım 3 içerik listesine):**

> mekanizma sınıfına göre K; her aday için iç sınır yüzünden atılan gölge hücresi sayısı ve payı.

---

## D. Yazarın sekiz noktasına kısa hükümler

| # | Konu | Hüküm | Bulgu |
|---|---|---|---|
| 1 | 20 km iç sınır, bilinen kümeler | Ciddi bir körlük ihlali. Kumamoto ve Ridgecrest ana hükümden çıkmalı; Tohoku kalır, B4'te ayrıca yazılır | A3 (engelleyici) |
| 2 | Megathrust gölgesi, K | Kapı dürüst; duyarlılık satırlarının ana kapının yerine geçmediği yazılmalı | B8, K8 |
| 3 | Olay sonrası Mc | İşaret sızıntısı ihmal edilebilir; asıl sorun düzeltmenin yetmemesi. Hiçbir kontrol yakalamıyor. Alt pencere Mc_son, S7 nötr kontrol, yedek merdiveni | A2 (engelleyici) |
| 4 | ISC gözden geçirilmemiş | Kural yetmez; ISC olayları başka kataloğa geçer ya da ana hükümden çıkar; D6 ComCat'ı yanlış çıkarıyor | A4 (engelleyici) |
| 5 | Koşullu oy, α | Poisson H0'da P(D \| n) ≤ 0,5 doğrulandı; ama gerçek α 0,019–0,047 (0,007–0,019 değil), φ ≥ 3'te > 0,05 | A1 (engelleyici) |
| 6 | Testere dişi | Tek anlamlı, olay öncesi, eşitlik bozma var; işlem sırası yazılmalı | K1 |
| 7 | Grup, `kumele`, alıcı, 0 büyüklük | Son pencere son üyeye göre başlamalı; kırık izi üye başına çıkarılmalı; M0 formülü ve DC payı yazılmalı | B2, K2, K3 |
| 8 | p₁ = 0,75 | Güç tanımca doğru; fiziksel karşılığı (f ≈ 0,55) iyimser, gerçekte 0,60–0,70 | B5 |

## E. Denetimde temiz çıkanlar

- §6.1 tablosu (c, gerçek α, güç, h, P(X ≤ h | 0,75)) K = 23–45'te scipy ile birebir yeniden üretildi. K = 28–200'de
  güç ≥ 0,80.
- Oy eşikleri bağımsız yazıldı. Poisson H0 değerleri 0,4459 / 0,4585 / 0,4783 ve P(A) 0,4606 tutuyor.
- π değerleri 0,15720, 0,18653 ve 0,13279 doğru.
- Tarih kuralı listesi (7 olay), 83 koşu adayı, 71 / 12 ayrımı ve dört çok üyeli grup dondurulan listeden tutuyor.
- Ek A'da 37 küme var; Kumamoto, Ridgecrest ve Tohoku tek üyeli kümeler.
- Kapı eşiği formülü `gereken_n0` ile Ek 1 aynı.
- Metinde İstanbul için mutlak olasılık yok. §13 Marmara bağı yalnız işaret düzeyinde. CRS-ETAS ve KURESEL-CRS-GELGIT ile
  örtüşmenin "bağımsız kanıt sayılmaz" diye yazılması doğru.
- Kör veri sınırı tutarlı: bütün son pencereler ≤ 2025-12-31; A1 için gereken ek ön indirmeler de olay öncesi.

## F. Dondurma öncesi yapılacaklar (özet)

1. A1–A4 düzeltme metinleri işlenir. `tr6a_onkayit_sayilar.py`, §4.3'teki N0'a bağlı P(D) tablosunu ve p₀ = 0,50–0,55
   için testere dişi tablosunu üretecek biçimde genişletilir.
2. B1–B10 metinleri işlenir. §10 önseli güncellenir.
3. `tr6a_olay_listesi.json` değişmez. Çıkarmalar kural olarak yazılır, liste olarak değil. Bu yüzden sha256 değişmez.
4. Değişiklikler yapıldıktan sonra ikinci bir inceleme gerekmez; ancak A1'in yeni §4.6'sı ve A2'nin alt pencere kuralı
   kod incelemesinde (§9 adım 4) özellikle denetlenmelidir.
