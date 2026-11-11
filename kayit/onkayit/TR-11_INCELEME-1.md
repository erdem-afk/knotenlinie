DÜZELTMEYLE KABUL

# TR-11 ön kayıt: bağımsız inceleme 1

İncelenen: `TR-11_gnss-taban-dagilimi_ONKAYIT.md` (taslak, 11 Kasım 2026; commit 6e83c05) ve bağlayıcı saydığı
`TR-11_SAYIM.md` §2, §4, §5. Kaynak olarak okundu: TR-1 ön kayıt sürüm 2, `TR-1_INCELEME-2.md`, `sayim_ustveri.py`,
`beklenti_gurultu.py`, `tr11_kume_listesi.json`. Hiçbir tenv3 ya da başka zaman serisi indirilmedi, S hesaplanmadı,
2026 deprem verisi sorgulanmadı, Marmara kutusundaki hiçbir istasyonun verisine bakılmadı. Yapılan hesaplar yalnız
yapay Gauss Δv'leriyle (N0 ölçeğinde) ve üstveriyle (DataHoldings, llh) yapıldı. Betikler depo dışında, karalama
dizinindedir; depoya dosya eklenmedi (bu rapor dışında).

## Hüküm

Tasarım sağlam ve sayım dürüst. Ancak metin bu hâliyle dondurulup otomatik koşulursa **sonuç büyük olasılıkla
"geçersiz (kod)" çıkar**. Bunun nedeni E1'deki pozitif kontrol eşiğidir. Ayrıca hüküm kuralının paydası (q95_N0)
koşu kodunu tek anlamlı bağlayacak kadar tanımlı değil (E2), Marmara çevirisindeki "alt sınır" savı ise iki yerde
kendi seçimleriyle çelişiyor (E3). Üç engelleyici bulgu da metin düzeltmesiyle giderilebilir. Aşağıdaki düzeltme
metinleri işlendikten sonra dondurulabilir. Yeni sayım gerekmiyor.

Denetimde temiz çıkanlar: küme listesinde ve referans halkalarında Marmara kutusunda istasyon yok (4730 istasyonun
hiçbiri, DataHoldings ve llh koordinatlarıyla ayrı ayrı denetlendi). Aynı epokta iki kümenin yakın istasyon kümesi
ortak istasyon taşımıyor. DataHoldings'te yinelenen istasyon adı yok. n_y dağılımı SAYIM §3.1 ile birebir aynı
(3: 160, 4: 104, 5: 59, 6: 54, 7: 55, 8: 371). Metinde mutlak İstanbul olasılığı yok.

---

## A. Engelleyici bulgular

### E1. Pozitif kontrol eşiği [2,4, 3,6] N0 altında bile tutmuyor; hüküm otomatik olarak "geçersiz (kod)" olur

- **Bulgu.** S bir vektör boyunun medyanıdır. Doğuya 3 mm/yıl eklenince S_eklenen ≈ medyan_i |(3, 0) + z_i| olur,
  yani 3'ün biraz üstü. S_özgün ise yaklaşık 0,95'tir (N0). Fark bu yüzden 3 değil, kabaca 3 − S_özgün + küçük bir
  terimdir. Yapay hesap: n_y karışımı SAYIM'dakiyle aynı, n_r = 8, Δv ~ N(0, σ_h² I₂), 401 küme-pencerelik yarı,
  300 yineleme.

  | σ_h (mm/yıl) | S_özgün medyanı | medyan(S_eklenen − S_özgün) | sd |
  |---|---|---|---|
  | 0,50 (N0-düşük) | 0,64 | 2,45 | 0,02 |
  | **0,75 (N0)** | **0,95** | **2,21** | 0,03 |
  | 0,90 | 1,15 | 2,09 | 0,04 |
  | 1,10 | 1,40 | 1,91 | 0,05 |
  | 1,50 | 1,91 | 1,63 | 0,06 |

  N0'ın kendisinde bile beklenen değer 2,21'dir ve alt eşik 2,4'ün 6 sd altında kalır. Ön kaydın kendi önsel beyanı
  (taban N0'dan büyük, olasılık 0,60) doğruysa fark daha da küçülür. Bu durumda doğru çalışan bir kod "geçersiz (kod)"
  hükmü alır. Artış n_y'ye neredeyse bağlı değil (σ_h 0,75'te n_y = 3 için 2,24, n_y = 8 için 2,21).
- **Neden önemli.** Hüküm sırası otomatiktir ve 2. adım 3. adımdan önce gelir. Bu eşikle sınav ana ölçüye hiç
  ulaşamaz. Ayrıca kontrol gerçek veride S'ye bağlı olduğu için, başarısız olduğu anda gerçek S dağılımı görülmüş
  olur ve kod düzeltmesi artık kör yapılamaz.
- **İkinci belirsizlik.** Aynı epokta bir istasyon bir kümede yakın, başka bir kümede referans olabiliyor. Listede bu
  durumdaki istasyon sayıları epoklara göre şöyle: 2003'te 14, 2008'de 174, 2013'te 546, 2018'de 816, 2023'te 870.
  "Sinyal seriye eklenir" okunuşunda ilk yarıdaki bir kümenin yakın istasyonu, ikinci yarıdaki bir kümenin referansını
  ya da başka bir ilk yarı kümesinin referansını kirletir. Ayrıca "SHA-256(T | merkez)" dizgesinin biçimi yazılmamış.
  Listedeki boylamlar tam float gösterimiyle tutuluyor (örneğin −95.1592356687898). Bu da TR-2'deki |A| = 1/3 türünden
  bir kod–metin farkına açık kapıdır. Tek sayıdaki 803 için "ilk yarı" 401 mi, 402 mi, o da belirsiz.
- **Düzeltme metni (§3 madde 2'nin (ii) bölümünün yerine; SAYIM §4.3 madde 2(ii) için de geçerli):**

  > (ii) Pozitif kontrol iki düzeyde yapılır. Sinyal küme-pencere başına eklenir. Seçilen bir küme-pencerenin yalnız
  > yakın istasyonlarının o küme için okunan kopyasına doğu bileşeninde max(0, t − H) × 3 mm/yıl eklenir. Aynı
  > istasyonun başka bir küme-penceredeki (yakın ya da referans) kullanımı değişmez. Seçim: listedeki her küme-pencere
  > için anahtar `f"{T}|{la:.4f}|{lo:.4f}"` (T ISO tarihi; la, lo listedeki değerler) dizgesinin UTF-8 SHA-256'sının
  > onaltılık değeri hesaplanır. Liste bu değere göre artan sıralanır ve ilk floor(803 / 2) = 401 küme-pencere seçilir.
  > Sonradan düşen küme-pencereler seçimden çıkar, yerine başkası alınmaz.
  > (ii-a) İstasyon düzeyi, gerçek veride. Seçilen kümelerin bütün yakın istasyonlarında
  > d_E = Δv_E(eklenen) − Δv_E(özgün) ve d_N = Δv_N(eklenen) − Δv_N(özgün) hesaplanır. medyan(d_E) ∈ [2,95, 3,05] ve
  > medyan(|d_N|) < 0,05 mm/yıl değilse hüküm "geçersiz (kod)" olur. En küçük kareler doğrusal olduğu için fark
  > MAD ayıklamasının değiştirdiği günler dışında tam 3'tür. Bu adım S hesaplamaz.
  > (ii-b) S düzeyi, yalnız yapay N0 serilerinde (madde (i) ile aynı seriler). Beklenen m* = medyan(S_eklenen − S_özgün),
  > q95_N0 ile aynı Monte Carlo'dan, aynı küme-pencereler ve aynı σ_h'lerle hesaplanır. Ölçülen değer
  > [0,9 m*, 1,1 m*] dışındaysa hüküm "geçersiz (kod)" olur. (Boşluksuz N0'da m* ≈ 2,2; ön kayıt bu sayıyı eşik olarak
  > kullanmaz.)

### E2. Ana ölçünün paydası (q95_N0) ve kod denetimi (i) tek anlamlı tanımlı değil

- **Bulgu.** "Havuzlanan beklenen %95" iki farklı şey olabilir: (a) her küme-pencerenin N0 S dağılımının eşit ağırlıklı
  karışımının %95'i, ya da (b) küme-pencere başına %95'lerin ortalaması ya da medyanı. Ölçülen q95, KP havuzunun
  ampirik %95'idir. Ona karşılık gelen (a)'dır, ama metin bunu söylemiyor. Ayrıca şunlar yazılı değil:
  1. **Gün maskesi.** MAD ayıklamasından önceki mi, sonraki mi? Ön kayıt "konum değerleri kullanılmaz" diyor, ama MAD
     konum değerine bağlıdır.
  2. **σ_h nasıl bulunur?** Analitik (sandviç) mi, yoksa Monte Carlo mu?
  3. **Kaç yineleme, hangi tohum?**
  4. **Kırpışma gürültüsü nasıl üretilir?** Yapay serilerde bu yazılı değil, boşluklu serilerde de üretim yolu belirsiz.
  5. **Yapay seri aynı istasyonun farklı küme-pencerelerinde aynı mı?** Bir istasyon aynı epokta hem yakın hem
     referans olabildiği için bu soru önemlidir.
  6. **Bootstrap'ta payda yeniden mi hesaplanır?** "Pay ve payda aynı örneklemde" deniyor ama bunun nasıl yapılacağı
     yazılı değil.
  7. **Güven aralığı yöntemi.** Yüzdelik mi, BCa mı? Aralığın uçları hangi nicelikler?
  8. **Nicelik kestiricisi.** Hangi nicelik tanımı kullanılır?
- **Denetim ([0,9, 1,1] savunulur mu).** Bağımsız küme-pencereler varsayımıyla 803 ya da 744 KP'de
  q95_yapay / q95_N0 oranının sd'si 0,019'dur. Yer düzeyinde etkin örneklem 336 alınırsa sd 0,027 olur. [0,9, 1,1] en
  kötü durumda ±3,7 sd demektir. Doğru kodun yanlışlıkla düşme olasılığı ihmal edilebilir. Kaba hataları (yanlış birim,
  yanlış menteşe sütunu, %20'yi aşan σ_h hatası) yakalar. Eşik savunulur. Tek şart şudur: payda, yapay serinin
  kendisinden değil, ayrı ve büyük bir Monte Carlo'dan gelmelidir.
- **Neden önemli.** Hüküm ρ'nun 1'e göre konumuna bağlıdır. Tanım belirsizliği tek başına %5–10'luk fark yaratabilir
  (boşluklu σ_h ile boşluksuz σ_h arasındaki fark, maske seçimi, karışımın tanımı). ρ_L ya da ρ_U 1'e yakın çıkarsa,
  hüküm koşu kodunun hangi okumayı seçtiğine bağlı kalır.
- **Düzeltme metni (§3'e "3a. Tanımlar" olarak eklenir):**

  > **ρ'nun tanımı.** Bütün nicelikler `numpy.quantile(..., method="linear")` ile alınır.
  > (1) Gün maskesi: bir (istasyon, T) için pencerede tenv3 satırı olan MJD günleri, MAD ayıklamasından önce. Doğu ve
  > kuzey aynı maskeyi kullanır.
  > (2) σ_h(istasyon, T): menteşe satırı a, maskeli en küçük kareler tasarımından hesaplanır (eksik günlerde a = 0).
  > Kovaryans N0 ile analitik (sandviç) olarak kurulur: σ_h² = σ_w² aᵀa + b_f² ΔT^(1/2) ‖Tᵀa‖². T, Williams (2003)
  > kesirli fark katsayılarının (κ = −1) 1826 günlük alt üçgen Toeplitz matrisidir (`beklenti_gurultu.py` `var_pl`
  > ile aynı).
  > (3) q95_N0: her küme-pencere k için M = 2000 çekiliş yapılır. Her çekilişte her yakın ve referans istasyon için
  > Δv ~ N(0, σ_h(i, T)² I₂) bağımsız çekilir ve S aynı kodla hesaplanır. Üreteç `numpy.random.default_rng(20261111)`;
  > küme-pencereler liste sırasıyla işlenir. q95_N0, geçerli bütün küme-pencerelerin çekilişlerinin eşit ağırlıklı
  > birleşiminin %95 niceliğidir.
  > (4) ρ = q95_ölçülen / q95_N0. q95_ölçülen, geçerli küme-pencerelerin S değerlerinin %95 niceliğidir.
  > (5) Bootstrap: 10°×10° blok listesi, blok sayısı kadar iadeli çekilir; B = 2000; üreteç
  > `default_rng(20261111 + 1)`. Her yinelemede pay, seçilen blokların bütün küme-pencerelerinin S değerlerinden
  > (tekrarlarıyla) hesaplanır. Payda, aynı küme-pencerelerin (3)'teki hazır çekilişlerinden (tekrarlarıyla) hesaplanır.
  > [ρ_L, ρ_U], 2000 ρ değerinin %5 ve %95 nicelikleridir (yüzdelik yöntem, çift yanlı %90). Her iki yön kararı tek
  > yanlı %5 düzeyindedir.
  > (6) Kod denetimi (i): her (istasyon, T) için bir yapay seri üretilir. Tohum
  > int(SHA-256(f"{STA}|{T}")[:16], 16) XOR 20261111'dir. Seri 1826 günlük tam ızgarada beyaz gürültü artı kesirli
  > farkla süzülmüş kırpışma gürültüsüdür, sonra gerçek maske uygulanır. Aynı (istasyon, T) her küme-pencerede aynı
  > seridir. Yapay seri gerçek tenv3 biçiminde yazılır ve koşu kodunun tamamından (ayrıştırma, MAD, uydurma, küme)
  > geçer. Oran, bu tek gerçekleşmenin q95'inin (3)'teki q95_N0'a bölümüdür.
  > (7) Sıra: veri kapısı → kod denetimi (i) ve (ii-b) yapay serilerde → (ii-a) → gerçek S. Gerçek küme-pencerelerin
  > S değerleri, yalnız 1. ve 2. adım geçtikten sonra hesaplanır ve dosyaya yazılır. 2. adım başarısız olursa kod gerçek
  > hiçbir S görülmeden düzeltilebilir. Düzeltme "koşu öncesi düzeltme" başlığıyla kayda geçer.

### E3. Marmara çevirisi: "alt sınır" savı U seçimiyle ve yanlılık (iii) ile çelişiyor; algılama olasılığı tanımsız

- **Bulgu 1: U, alt sınır savıyla ters yönde.** Ön kaydın İstanbul cümlesi (§7) bir olanaksızlık cümlesidir:
  "Δs_min'den küçük değişimi göremez." Bu cümle ancak Δs_min gerçek eşiğin alt sınırıysa doğrudur. q95'in üst güven
  sınırı U ise Δs_min'i yukarı iter, yani istatistik tarafında alt sınır savının tersine çalışır. Alt sınır için
  doğru taraf q95'in **alt** güven sınırı L'dir. U ancak "en az bu büyüklükteki değişimi görebilir" türünden bir
  olabilirlik cümlesi için tutucudur. §4'teki yorum cümlesi ("en az a–b mm/yıl'lık değişimi görebilir (alt sınır)")
  bu iki cümleyi birbirine karıştırıyor.
- **Bulgu 2: algılama olasılığı tanımsız.** Δs_min = U/G, sinyalin tek başına q95'e eşit olduğu noktadır. Yapay
  hesapla N0 ölçeğinde, %5 yanlış alarmda bu noktadaki algılama olasılığı n_y = 3 için 0,65, n_y = 8 için 0,70'tir.
  %50 algılama noktası s50 ≈ 0,82 × q95'tir. √(q95² − S50²) yaklaşımı 0,76 × q95 verir, yani s50'nin hemen altındadır
  ve bu yüzden alt sınır olarak geçerlidir. %90 algılama 1,2–1,4 × q95'tir. "Algılanabilir" sözcüğü bir olasılık
  düzeyine bağlanmadıkça U/G, %50 eşiğinin alt sınırı değildir.
- **Bulgu 3: yanlılık (iii) aynı yönde değil.** n_r = 8 için m_r, 4. ve 5. sıradaki referansın ortalamasıdır. Bu
  yüzden "dengeli" durum yalnız tam 4:4 dağılımda geçerlidir. 5:3 gibi bir dengesizlikte m_r ≈ ±π/2 olur. Referans
  çoğunluğunun **karşı** yanındaki yakın istasyonlar için G = ½ + arctan(|x|/D)/π'dir ve bu değer dengeli G'den büyüktür:

  | D \ x | 5 km | 10 km | 20 km | 30 km | 50 km |
  |---|---|---|---|---|---|
  | 5 km | 0,750 (1/G 1,33) | 0,852 (1,17) | 0,922 (1,08) | 0,947 (1,06) | 0,968 (1,03) |
  | 10 km | 0,648 (1,54) | 0,750 (1,33) | 0,852 (1,17) | 0,898 (1,11) | 0,937 (1,07) |
  | 15 km | 0,602 (1,66) | 0,687 (1,46) | 0,795 (1,26) | 0,852 (1,17) | 0,907 (1,10) |

  Aynı yandaki istasyonlarda ise 1/G 2,5–31,5'e çıkar. Yani yanlılık (iii) Δs_min'i, istasyonun hangi yanda olduğuna
  göre 6 kata kadar aşağı da, yukarı da itebilir. Marmara'nın 200–500 km halkası kuzeyde Karadeniz ve Trakya, güneyde
  ise yoğun Anadolu ağıdır. Dengesizlik bu yüzden olası durumdur, istisna değil. "Dört yanlılığın hepsi aynı yönde"
  savı (iii) için yanlıştır. (iv) için ise bir varsayımdır, kanıt değildir.
- **Bulgu 4: n_y karışımı.** N0 altında q95/σ_h değeri n_y = 3'te 2,18, n_y = 8'de 1,84, havuzda 1,96'dır. Marmara'da
  yoğun bir ağ (n_y = 8) varsayılırsa havuz U'su Δs_min'i yaklaşık %6 büyütür. Bu da alt sınırın tersi yöndedir.
- **Düzeltme metni (ön kayıt §4'ün yerine; SAYIM §4.3 madde 5, hüküm cümlesinin çeviri kısmı ve §5 için de geçerli):**

  > ## 4. Marmara çevirisi (önceden sabit)
  > Algılama tanımı: yanlış alarm %5 (eşik q95), algılama olasılığı %50. Çeviri n_y = 8 katmanının q95'i ve
  > bootstrap aralığı [L₈, U₈] ile yapılır. Bu katmanda 300'den az küme-pencere kalırsa havuz kullanılır ve bu durum
  > yazılır. S50₈ aynı katmanın sakin medyanıdır.
  > **Ana satır (alt sınır):** Δs_alt(D, x, m_r) = √(L₈² − S50₈²) / G(D, x, m_r).
  > Bilgi satırları: √(q95₈² − S50₈²)/G (nokta) ve U₈/G (sinyal tek başına eşiği aşar; yaklaşık %65–70 algılama).
  > G tablosu üç referans geometrisiyle yazılır: m_r = 0 (dengeli), m_r = +π/2 (referanslar aynı yanda) ve
  > m_r = −π/2 (referanslar karşı yanda). D ∈ {5, 10, 15} km, x ∈ {5, 10, 20, 30, 50} km. a, bu 45 hücrenin en küçük
  > Δs_alt değeridir. Dengeli satırın D = 10, x = 20 hücresi "temsilî" diye ayrıca yazılır.
  > Yorum cümlesi yalnız şu biçimde kurulur: "Bu ölçüm ve bu model altında, yıl ölçekli GNSS hız değişimi alarmı
  > Marmara benzeri geometride derin kayma hızındaki a mm/yıl'dan küçük değişimleri %5 yanlış alarm düzeyinde
  > yarıdan fazla olasılıkla göremez (alt sınır; temsilî geometride c mm/yıl). Karşılaştırma için Prens Adaları
  > kesiminde yayımlanmış kayma açığı hızı 10–15 mm/yıl'dır (Ergintav 2014, özetten)."
  > Yanlılıklar: sonlu yama (i) ve geç ya da kademeli başlayan değişim (ii) gerçek eşiği büyütür. Referans dengesizliği
  > (iii) iki yöne de gidebilir ve a'nın karşı yan satırından alınmasıyla kapsanır. Aktif kuşakta daha büyük taban (iv)
  > bir varsayımdır ve doğruysa gerçek eşiği büyütür. Alt sınır savı (i), (ii) ve (iii)'ün bu biçimde ele alınmasına
  > dayanır, (iv)'e dayanmaz.

  (Daha güçlü ama daha çok iş isteyen seçenek: G, Marmara'nın bugünkü istasyonlarının yalnız DataHoldings
  koordinatlarıyla ve önceden sabit bir KAF iz çizgisiyle tek bir G_M(D) olarak hesaplanır. Koordinat üstveridir,
  seri değildir. VE-1 körlüğünü bozmaz, ama iz çizgisi kaynağı ve ayrıntısı ön kayıtta sabitlenmelidir. Bu
  incelemede hesaplanmadı.)

---

## B. Önemli bulgular

### Ö1. "N0'dan büyük / küçük / uyumlu" hükmü, keyfî bir genliğe göre verilmiş tek eşik hükmü

- **Bulgu.** N0'da σ_h'nin %98'i kırpışmadan gelir (0,247 × 3 = 0,74; beyaz 0,069 × 1,5 = 0,10). Bu yüzden ρ
  pratikte "eşdeğer kırpışma genliği / 3" demektir. Ön kayıt §6 ve SAYIM §6, 3 mm/yıl^0,25 değerinin özetlerden
  doğrulanamadığını kendisi yazıyor. "Taban N0'dan büyük" hükmü bu yüzden yalnız "b_f* > 3" bilgisini taşır ve 3
  keyfîdir. Gauss N0'ın kuyruk biçimi de gerçek dağılımdan farklı olabilir (kayıtsız sıçramalar, hidroloji). Tek
  bir %95 oranı ölçeği ve kuyruğu birbirinden ayıramaz. Önsel güvenler (0,60 / 0,30 / 0,10) de aynı keyfî eşiğe
  bağlı olduğu için az bilgi taşır.
- **n_y bağımlılığı.** Pay ve payda aynı karışımla hesaplandığı için ρ'da sorun yok (E2 tanımıyla). Sınıf ve bölge
  satırlarında katmanlar farklı n_y karışımları taşır. Ham q95'ler bu yüzden katmanlar arasında doğrudan kıyaslanamaz,
  katmanların ρ'ları kıyaslanabilir. Çeviri için E3 Bulgu 4'e bakın.
- **Düzeltme metni (§3 madde 3'ün yerine):**

  > 3. **Ana ölçü.** Birincil çıktı ölçümün kendisidir: q95 [L, U] mm/yıl ve ρ [ρ_L, ρ_U]. Ek olarak b_f* yazılır:
  > σ_w = 1,5 mm sabitken q95_N0(b_f) = q95_ölçülen eşitliğini sağlayan kırpışma genliği. b_f*'nin aralığı, aynı
  > bootstrap yinelemelerinde çözülür; q95_N0 b_f'de tekdüze olduğu için tek çözüm vardır. Etiket şöyle konur:
  > b_f*'nin alt sınırı > 4 ise **"taban N0-yüksek'ten büyük"**, üst sınırı < 2 ise **"taban N0-düşük'ten küçük"**,
  > ötekilerde **"taban N0 bandında (b_f 2–4)"**. ρ'nun 1'e göre konumu bilgi satırıdır. Kuyruk satırı:
  > ρ₉₅ / ρ₅₀ (ρ₅₀ medyanlar oranıdır) ve aralığı. Alt sınırı > 1,1 ise "kuyruk Gauss N0'dan ağır" yazılır.
  > Rakip açıklamalar ve önsel güven: N0-yüksek'ten büyük 0,45; N0 bandında 0,45; N0-düşük'ten küçük 0,10. (Önsel
  > rakamlar yazarındır; inceleme yalnız bandı öneriyor.)

### Ö2. Menteşe modelinin tahmin ayrıntıları koşu kodunu bağlamaya yetmiyor

- **Bulgu.** TR-1 §3 ve SAYIM §2 modelin terimlerini sayıyor, ama şunları tanımlamıyor: tenv3'ün hangi sütunu, birim,
  zaman ekseni ve başlangıç noktası, ağırlık, MAD'in tam tanımı, doluluk paydaları, sıçrama regresörünün eşitlik
  durumu, eksik/tekrar gün, rank eksikliği, steps.txt sürümü, n_r çiftken medyan. Her biri bir çatallanma noktasıdır.
  Ön kaydın "kod sonradan incelenir" güvencesi bunu kapatmaz, çünkü kod incelemesi neyin doğru olduğunu ancak metne
  bakarak yargılayabilir.
- **Düzeltme metni (§2'ye "Menteşe modeli, koşu ayrıntıları (en dar okuma)" olarak eklenir):**

  > - Girdi: NGL IGS20 tenv3. Doğu = `_e0(m)` + `__east(m)`, kuzey = `____n0(m)` + `_north(m)`, metreden mm'ye
  >   (× 1000). `_e0`/`n0` ya da `reflon` pencere içinde değişirse toplam yine kullanılır. Zaman: `__MJD` sütunu.
  >   Pencere dışındaki satırlar okununca atılır. Aynı MJD'li birden çok satır varsa dosyadaki ilki alınır.
  >   `sig_e`, `sig_n` ve korelasyon sütunları kullanılmaz.
  > - Zaman ekseni t = (MJD − MJD(w0)) / 365,25 yıl. Menteşe regresörü max(0, t − t_H), t_H = (MJD(H) − MJD(w0)) /
  >   365,25. Yıllık ve altı aylık terimler sin/cos(2π t) ve sin/cos(4π t).
  > - Sıçrama: penceredeki her farklı kod 1 tarihi t_k için regresör 1{MJD ≥ MJD(t_k)}. Tarihler dondurulmuş
  >   steps.txt'ten alınır (SHA-256 ilk 16 hane 887501a438c41c34). Koşu anında yeniden indirilmez.
  > - Ağırlıksız sıradan en küçük kareler; bileşenler ayrı ayrı. Tasarım matrisinin rankı sütun sayısından küçükse
  >   (örneğin bir sıçramadan sonra veri yoksa) istasyon o T için düşer ve sayılır.
  > - Ayıklama, bileşen başına bir kez: r ilk uydurmanın artıkları, MAD = medyan|r − medyan(r)|.
  >   |r − medyan(r)| > 5 × 1,4826 × MAD olan günler o bileşenden atılır, model yeniden uydurulur. MAD = 0 ise
  >   ayıklama yapılmaz.
  > - Doluluk (ayıklamadan önce, satır günleriyle): taban [w0, H) 1096 takvim günü, yakın dönem [H, w1] 730 takvim
  >   günü. Her birinde gün sayısı / takvim günü ≥ 0,60.
  > - Küme ölçüsünde medyanlar `numpy.median` ile alınır (çift sayıda ortadaki ikisinin ortalaması). Δv, ikinci
  >   uydurmanın menteşe katsayısıdır (mm/yıl).

### Ö3. İstanbul'a bağ (§7): "açık mı kapalı mı" sorusu sayısal bir kurala bağlı değil ve mantıkça tek yönlü

- **Bulgu.** "Eşik kayma açığına yakın ya da büyükse yol kapalı; küçükse ayrı ön kayıt" cümlesinde "yakın" tanımsız.
  Daha önemlisi, bir alt sınır yalnız kapatma yönünde sonuç verir. Gerçek eşik ≥ a ≥ kayma açığı ise yol kapalıdır.
  Ama a küçükse bu yolun açık olduğu sonucu çıkmaz. E3'teki karşı yan satırı a'yı 1,03–1,66 × √(L² − S50²)'ye
  indirir. Bu yüzden önceden görünen sonuç büyük olasılıkla "kapatılamadı"dır. Bu önceden yazılmalıdır, yoksa sonuç
  sonradan "yol açık" diye okunabilir.
- **Düzeltme metni (§7'nin son iki cümlesinin yerine):**

  > Önceden sabit kural: a ≥ 10 mm/yıl (yayımlanmış kayma açığının alt ucu) ise "GNSS yıl ölçekli alarm yolu bugünkü
  > ağla Marmara'da kapalı (alt sınır en elverişli geometride bile kayma açığına ulaşıyor)" yazılır. a < 10 mm/yıl
  > ise "bu ölçüm yolu kapatamadı" yazılır. Bu hüküm yolun açık olduğu anlamına gelmez. Temsilî hücre c < 5 mm/yıl
  > ise ayrıca "Marmara'ya özgü ön kayıt düşünülebilir (2017 sonrası veri hâlâ kör)" notu eklenir. TR-11 hiçbir
  > durumda "yol açık" hükmü vermez. Bugünkü N0 ölçeğinde (L ≈ 1,5 mm/yıl) a'nın 10'a ulaşmadığı önceden görülüyor.
  > Beklenen sonuç "kapatılamadı"dır ve bu önceden kabul edilir.

### Ö4. Körlük: Marmara kutusu korunuyor, ama kutuya 100 km'den yakın iki yakın istasyon ve tenv3'ün tamamı

- **Bulgu.** Kutu içinde hiç istasyon yok; bu doğrulandı. Kutuya en yakın istasyonlar şunlar: CMLD (82 km, yakın),
  AFYN (85 km, referans), KRBK (98 km, yakın), AKHR (126 km, referans), KLUU (143 km, referans). İlk dördü 2018
  epoğunda 41° K, 33,33° D küme-penceresinde, KLUU ise ayrıca 37° K, 33,99° D küme-penceresinde kullanılıyor. 2018
  penceresi 2013–2017'yi kapsıyor, yani 2017 yılı içeride. tenv3 dosyası ayrıca 2026'ya kadar bütün seriyi taşıyor.
  Kutu tanımı bozulmuyor. Ama bu dosyalar indirilince Marmara'nın 100 km yakınından 2017 sonrası konum verisi diskte
  olur. VE-1 yeniden açılırsa referans halkası olarak tam bu istasyonları kullanabilir.
- **Düzeltme metni (§5 Körlük paragrafına eklenir):**

  > Marmara kutusuna 150 km'den yakın istasyonların (bugünkü listede CMLD, AFYN, KRBK, AKHR, KLUU) dosyaları okunurken
  > w1'den sonraki satırlar belleğe alınmadan atılır. Dosyalar koşudan sonra silinir, yalnız SHA-256'ları kalır.
  > Bu istasyonların pencere dışı verisi hiçbir çizimde ya da tabloda gösterilmez.

### Ö5. Bağlayıcı listenin sha256'sı "dosyada" değil; metin ile sayım betiği arasında küçük farklar

- **Bulgu.**
  1. Ön kayıt "sha256 dosyada" diyor. JSON yalın bir liste ve sha taşımıyor; SAYIM'da da yok. Ölçülen değer:
     `79f6cf0f9a1a11d932617b20c7b866bb5125a3acea62d35325af9364f027cbbd`.
  2. Ş3 metinde derinlik sınırı olmadan "M ≥ 8,0 yok" diyor. Kod ise E70'i, yani derinlik ≤ 70 km kataloğunu
     kullanıyor. 2013 Okhotsk ve 2018 Fiji gibi derin M8'ler bu yüzden şarta girmiyor.
  3. Ş1 ve Ş2'nin üst ucu kodda T + 730 g − 1 gündür (T + 2 yıl hariç). Ş3'ün üst ucu kodda T − 1 gündür, metinde
     T'dir.
  4. Sınıf A, TR-2'nin `birincil_aday*` dosyalarındaki mekanizmalarla atanıyor. "Birincil" bir ayıklanmış alt küme
     olabilir. Metin ise "ComCat mekanizması bulunan olaylar" diyor.
  5. Izgara savı "merkezler arası ≥ 200 km", 89° satırında tutmuyor (3 merkez, aradaki büyük daire uzaklığı ≈ 193 km).
     Pratikte etkisiz: listede aynı epokta ortak yakın istasyon yok.

  Kod 1 sınırları (|t − H| < 30 g; ilk ve son 30 gün), kod 2 aralığı [w0 − 730 g, w1], halka [200, 500] km ve
  eşitlikte istasyon adı sırası metinle uyumlu.
- **Neden önemli.** Liste bağlayıcı olduğu için 2–5 hükmü değiştirmez. Ama ön kayıt "metin ile kod çelişirse liste
  bağlayıcıdır" diyor, bu yüzden farkların listelenmesi gerekir ki sonradan "metin farklı diyordu" tartışması
  açılmasın.
- **Düzeltme metni (§2'nin son paragrafına eklenir):**

  > Listenin SHA-256'sı 79f6cf0f9a1a11d932617b20c7b866bb5125a3acea62d35325af9364f027cbbd'dir. Koşu kodu bu değeri
  > denetler, uyuşmazsa durur. Bilinen metin–kod farkları (liste geçerlidir): Ş3 yalnız derinlik ≤ 70 km olayları
  > sayar; Ş1–Ş2 üst ucu T + 730 g − 1 g, Ş3 üst ucu T − 1 g; sınıf A mekanizmaları TR-2 `birincil_aday*`
  > dosyalarındandır; 89° satırında merkez aralığı 200 km'nin altındadır (listede etkisi yok).

---

## C. Küçük bulgular

### K1. Kestirilen nicelik küme-pencere ağırlıklı

- **Bulgu.** 5 epoklu bir yer 5 kez sayılır. Bu bir kusur değil, ama yazılmalı.
- **Düzeltme:** "q95, küme-pencere ağırlıklı havuzun niceliğidir; yer ağırlıklı q95 (her yerin küme-pencereleri
  1/n_epok ağırlıklı) bilgi satırıdır."

### K2. Veri kapısındaki "yer" tanımı

- **Düzeltme:** "Yer ve blok sayımı; doluluk, indirme hatası, rank eksikliği ve n ≥ 3 şartından sonra en az bir
  geçerli küme-penceresi kalan merkezler üzerinden yapılır."

### K3. Gerçek istasyonla geliştirme: SAYIM ile ön kayıt çelişiyor

- **Bulgu.** SAYIM §9 "en çok 5 gerçek istasyonla geliştirilir" diyor, ön kayıt §5.2 "yalnız yapay seriler" diyor.
- **Düzeltme (§5.2'ye):** "Dosya biçimi için gerçek istasyon kullanılmaz; yapay seriler gerçek tenv3 başlığı ve
  sütun düzeniyle yazılır." Ya da en çok 5 istasyonluk istisna açıkça yazılır: listede olmayan, kutuya 1500 km'den
  uzak istasyonlar.

### K4. Önsel yönün dayanağı bir Marmara istasyonu

- **Bulgu.** ISTA verisi AV-1'de zaten görülmüş, hükmü değiştirmiyor. Yine de belirtilmeli.
- **Düzeltme (SAYIM §4.2 önsel paragrafına):** "ISTA bir Marmara kutusu istasyonudur. Bu sayı AV-1'de önceden
  görülmüştü; TR-11 kapsamında yeni bir Marmara verisi okunmadı."

### K5. Dil

- **"Hep aynı yöne iter: gerçek eşik daha büyüktür" (§4).** Kanıtlanmış gibi sunulan bir sav, E3 ile düzeltilir.
- **"Bu, … yolunun açık mı kapalı mı olduğunu söyler" (§7).** Alt sınır yalnız kapatabilir, Ö3 ile düzeltilir.
- **SAYIM hüküm cümlesindeki "Δs_min(D, x) ≥ π·U / …".** Eşitsizlik bir varsayımlar sonucudur.
  "… (alt sınır, §4 varsayımları altında)" biçiminde yazılmalı ve L ile kurulmalıdır.
- **"Görebilir" (yorum cümlesi).** Olanaklılık sözcüğüdür, ölçülen şey ise bir olanaksızlık sınırıdır. E3'teki
  cümleyle değiştirilir.

Mutlak İstanbul olasılığı ya da olasılık çarpanı hiçbir yerde geçmiyor.

### K6. Koşu adımı 3: başarısız indirmeler için ölçüt

- **Düzeltme:** "İndirme başarısızlığı istasyon düzeyinde kayda geçer. Başarısız istasyonların payı %5'i aşarsa koşu
  durur ve tek bir yeniden deneme turu yapılır (S hesaplanmadan)."

---

## D. Yapay hesapların özeti (yeniden üretim)

Betikler: karalama dizininde `inc/sim1.py` (pozitif kontrol) ve `inc/sim2.py` (oran sd'si, n_y'ye göre nicelikler,
algılama olasılığı). İkisi de yalnız N(0, σ_h²) Δv'leri kullanır, seri okumaz. Tohumlar 7 ve 11.

| Hesap | Sonuç |
|---|---|
| N0 (σ_h 0,75) medyan(S_eklenen − S_özgün), 3 mm/yıl doğu | 2,21 (sd 0,03); [2,4, 3,6] dışında |
| q95_yapay / q95_N0 sd (803 / 744 / 336 bağımsız birim) | 0,019 / 0,019 / 0,027 |
| f = S/σ_h %95, n_y = 3 / 8 / havuz (n_r = 8) | 2,18 / 1,84 / 1,96 |
| %5 yanlış alarmda %50 algılama s50 / q95 | 0,82 (√ yaklaşımı 0,76) |
| s = q95'te algılama olasılığı (n_y 3 / 8) | 0,65 / 0,70 |
| Karşı yan referansta 1/G aralığı (D 5–15, x 5–50 km) | 1,03–1,66 (dengeli 2,1–9,8; aynı yan 2,5–31,5) |
