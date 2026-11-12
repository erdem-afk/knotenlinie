# Büyük (M6.5–7.5) kıtasal doğrultu atımlı depremlerde çekirdeklenme ve ön-kayma (preslip): kuram ne öngörür? (durum: Kasım 2026)

Kapsam notu: Yalnız kuram ve modelleme literatürü. Gözlemler yalnız bir kuramsal öngörüyü sınadıkları yerde anılır. İstanbul depremi için hiçbir mutlak olasılık yazılmamıştır; 2026 katalog verisi ve Marmara GNSS verisi kullanılmamış ve aranmamıştır. Hesaplarda kullanılan yükleme hızı (V_L = 10–25 mm/yıl), kilitli derinlik (10–15 km) ve normal gerilme değerleri **varsayım parametresidir**, veri değildir.

Doğrulama durumu: Literatür taraması OpenAlex üzerinden yapıldı; özetler OpenAlex'ten okundu. Wiley tam metinleri 403 verdi, Nature (Fryer vd. 2026) giriş sayfasına yönlendirdi, bir ikincil PDF aynası izin sisteminin reddine takıldı; bunların hiçbiri aşılmadı. Bu yüzden yalnız özette geçen sayılar "kaynaktan" diye işaretlendi. Klasik formüllerin bir kısmı (Rice 1993 h*, Dieterich 1992'nin tam çözümü, SEAS BP1 parametreleri) genel literatür bilgisidir ve bu çalışmada birincil metinden **doğrulanamadı** diye işaretlenmiştir. "Kendi kaba hesap" etiketli sayılar bu notun yazarına aittir, yayımlanmış değildir.

---

## 1. Rate-and-state çekirdeklenme kuramı: h*, L_b, L_∞; a, b, D_c, σ ile ölçekleme; kilitli 10–15 km'lik bir fayda yüzeyden algılanabilirlik

### Takeaway
Rate-and-state (RSF) kuramında çekirdeklenme boyu L_b = μ′D_c/(bσ) ile ölçeklenir ve a/b'ye bağlı olarak 1.38·L_b (sabit uzunluk rejimi) ile (1/π)(b/(b−a))²·L_b (genişleyen çatlak rejimi) arasında değişir. Laboratuvar D_c değerleri (10 µm–1 mm) ve σ_eff ≈ 50–150 MPa için bu boy metreler ile birkaç km arasında kalır. 1/t biçimindeki hızlanmanın tektonik yükleme hızını aştığı süre ≈ (a/b)·D_c/V_L'dir: D_c = 1 mm için bu yaklaşık **iki hafta**, D_c = 10 mm için **aylar** eder. Yıl ölçeği ancak D_c ≥ ~0.1 m ve a/b → 1 gibi uç parametrelerle elde edilir. Bu uç durumda çekirdeklenme, bütün kilitli genişliğe yayılan Mw 5–6 büyüklüğünde bir yavaş kaymaya dönüşür.

### Cited Findings
- **Dieterich (1992), sabit uzunluk / iyileşmesiz limit:** RSF'de çekirdeklenme, belirli bir yamada (patch) zamana karşı hızlanan kaymadır. Dieterich'in çözümünde kayma hızı, kararsızlığa kalan süreyle ters orantılıdır: V(t) ≈ (a/H)/(t_f − t), H = b/D_c − k/σ. Sabit gerilme yüklemesi altında kararsızlık süresi t_f = (aσ/τ̇)·ln[1 + τ̇/(HσV₀)] olur. Dieterich bu modelden minimum çekirdeklenme boyunu L_c ≈ μD_c/(bσ) (geometri katsayısıyla) olarak türetir. Formüller birincil metinden **doğrulanamadı**: OpenAlex'te özet yok, Zenodo kopyası açılmadı. — [Dieterich 1992, Tectonophysics 211, 115–134, doi:10.1016/0040-1951(92)90055-B](https://doi.org/10.1016/0040-1951(92)90055-b)
- **Rubin & Ampuero (2005), yaşlanma yasası (aging law):** İki rejim var ve aralarındaki sınır a/b ≈ 0.5'tir. (i) İyileşme önemsizken (Vθ/D_c ≫ 1) yama, sabit yarı uzunluğa yerleşir: **L_ν ≈ 1.3774·μ′D_c/(bσ)** (K = 0 çözümü). Bu çözüm yalnız a/b < 0.3781 için kararsızlığa kadar korunur. (ii) a/b ≳ 0.5'te Vθ/D_c ≈ 1'e yaklaşır ve çekirdeklenme, genişleyen bir kayma-zayıflama çatlağına benzer. Asimptotik boy **L_∞ = π⁻¹·[b/(b−a)]²·μ′D_c/(bσ)** olur. Bu, a/b = 0.95'te Dieterich boyunun yaklaşık 100 katıdır. Yazarların özetinden: "nucleation might produce signals detectable by surface seismometers for values of D_c at the upper end of the lab range (100 μm)". Ama bu kadar büyük boyları üreten yaşlanma-yasası özellikleri "may be nonphysical". — [Rubin & Ampuero 2005, JGR 110, B11312, doi:10.1029/2005JB003686](https://doi.org/10.1029/2005jb003686)
- **Ampuero & Rubin (2008), yaşlanma ve kayma yasası (slip law):** Kayma yasasında çekirdeklenme bölgesi daha küçüktür ve hızlandıkça daralır. Genişleme, tek yönlü ilerleyen hızlanan bir kayma darbesi (slip pulse) biçimini alır. Kırılma enerjisi G_c, yaşlanma yasasında hız sıçramasının logaritmasının karesiyle, kayma yasasında logaritmasıyla büyür. Çekirdeklenme cephesi, kayma hızından kabaca (μ′/bσ)/ln(hız sıçraması) kat daha hızlı ilerler. Bunun yitim zonu yavaş kayma olaylarındaki ilerleme hızlarıyla tutarlı olması için σ_eff ≈ 1 MPa gerekiyor. — [Ampuero & Rubin 2008, JGR 113, B01302, doi:10.1029/2007JB005082](https://doi.org/10.1029/2007jb005082)
- **Rubin & Ampuero (2009), öz-benzer darbe:** Kayma yasasında darbenin taşıdığı toplam kayma ≈ **D_c(1 − a/b)⁻¹**. Kalan ilerleme mesafesi ∝ (1 − a/b)⁻²·[ln(V_maxθ_bg/D_c)]⁻¹ (bir "kararsızlığa kalan mesafe"). Kayma hızının anlamlı olduğu uzunluk, ln V_max ile ters orantılı küçülür. — [Rubin & Ampuero 2009, JGR 114, B11306, doi:10.1029/2009JB006529](https://doi.org/10.1029/2009jb006529)
- **Lapusta & Rice (2003):** 2-B, derinliğe bağlı özellikli bir doğrultu atımlı fay modeli. D_c küçüldükçe küçük olaylar, kilitli-sünen geçişte, sismojenik zonun tabanında ortaya çıkar. "Small and large events have very similar nucleation phases": çekirdeklenme, küçük ve yavaş genişleyen bir bölgede giderek hızlanan aseismik kaymadır. h*_RR = (π/4)μ′D_c/[(b−a)σ] ve h*_RA = (2/π)μ′bD_c/[(b−a)²σ] tanımları bu çalışmada birincil metinden **doğrulanamadı** (Wiley 403; genel literatür formülü olarak verilmiştir). — [Lapusta & Rice 2003, JGR 108(B4), 2205, doi:10.1029/2001JB000793](https://doi.org/10.1029/2001jb000793)
- **Kaneko, Nielsen & Carpenter (2016):** Laboratuvar ve RSF simülasyonlarında çekirdeklenmenin iki aseismik evresi var: yavaş ilerleme ve ardından hızlanma. Bu evreler arasındaki geçiş uzaklığı kuramsal kritik çekirdeklenme boyuyla kabaca öngörülebilir. Kritik boy arka plan yükleme hızına bağlıdır. Öncü depremlerin göç hızı σ_eff'e, dolayısıyla akışkan basıncına bağlı olmalıdır. — [Kaneko vd. 2016, JGR 121, doi:10.1002/2016JB013143](https://doi.org/10.1002/2016jb013143)
- **Guérin-Marthe vd. (2018), laboratuvar:** Yükleme hızı 10⁻² MPa/s'den 6 MPa/s'ye çıkınca çekirdeklenme boyu 3 kat kısalıyor. Ölçülen boylar Rubin & Ampuero'nun L_b–L_∞ sınırları arasında kalıyor. — [Guérin-Marthe vd. 2018, JGR, doi:10.1029/2018JB016803](https://doi.org/10.1029/2018jb016803)
- **Zhai & Huang (2024), tam dinamik döngü:** Küçük D_c için genişleyen çatlak tarzı çekirdeklenme ancak a/b > 0.75'te görülüyor. Yazarlar buradan doğal ve laboratuvar faylarında sabit uzunluk tarzının baskın olabileceği sonucunu çıkarıyor. — [Zhai & Huang 2024, JGR, doi:10.1029/2024JB029719](https://doi.org/10.1029/2024jb029719)
- **Kaneki & Noda (2025), tam dinamik, farklı durum yasaları:** Son evrede moment hızı, yaşlanma ve Nagata yasalarında dM/dt ∝ t_f⁻¹, değiştirilmiş kayma yasasında ≈ t_f⁻⁰·⁹. Yaşlanma yasasında sünme cephesi hızlanmayla birlikte sismojenik yamanın içine ilerliyor. — [Kaneki & Noda 2025, Earth Planets Space, doi:10.1186/s40623-025-02269-8](https://doi.org/10.1186/s40623-025-02269-8)
- **He vd. (2023):** Homojen RSF fayında "kilitli" başlangıçtan çekirdeklenme. Zayıflama çekirdeği (WZcore), yükleme hızının birkaç katı kayma hızıyla süreklilik gösteriyor. Süresi "weeks before large subduction earthquakes under high driving rate, but **years on low-rate continental faults**". — [He vd. 2023, JGR, doi:10.1029/2023JB026422](https://doi.org/10.1029/2023jb026422)
- **SEAS kıyas problemi BP1:** 2-B antiplane doğrultu atımlı, H = 15 km. Bilinen parametreler: a = 0.010, b = 0.015, D_c = 8 mm, σ = 50 MPa, V_p = 10⁻⁹ m/s. Bu parametreler ve künye **doğrulanamadı**: Erickson vd. 2020, Seismol. Res. Lett., SEAS kod doğrulama makalesi; bu oturumda erişilmedi.

### Inferences (kendi kaba hesap; μ = 30–32 GPa, mod II için μ′ = μ/(1−ν) ≈ 40 GPa, mod III için μ′ = μ; b = 0.01–0.015)
- **σ_eff aralığı.** 10 km'de hidrostatik boşluk basıncıyla σ_eff ≈ (ρ_r − ρ_w)gz ≈ 1700·9.8·10⁴ ≈ 170 MPa. Aşırı basınçlı fayda 20–50 MPa.
- **L_b = μ′D_c/(bσ), b = 0.01, σ = 100 MPa, μ′ = 40 GPa:**

| D_c | L_b |
|---|---|
| 10 µm | ≈ 0.4 m |
| 1 mm | ≈ 40 m |
| 10 mm | ≈ 400 m (σ = 30 MPa'da ≈ 1.3 km) |
| 0.1 m | ≈ 4 km |

- **L_∞ / L_b = (1/π)(b/(b−a))²:**

| a/b | L_∞ / L_b |
|---|---|
| 0.5 | 1.3 |
| 0.8 | 8 |
| 0.9 | 32 |
| 0.95 | 127 |

  D_c = 10 mm ve a/b = 0.9 iken L_∞ ≈ 13 km olur, yani 10–15 km'lik kilitli genişlikle aynı mertebede. Bu durumda "çekirdeklenme" ile "bölgesel yavaş kayma" ayrımı ortadan kalkar; McLaskey'nin (2019) "ignition-limited" uç üyesi budur (bkz. Bölüm 2).
- **SEAS BP1 parametreleriyle (doğrulanamadı):** L_b ≈ 3.2·10¹⁰·0.008/(0.015·5·10⁷) ≈ 340 m. h*_RA ≈ 2 km. L_∞ ≈ (1/π)·9·340 ≈ 1 km. Bu, sismik döngü modellerinin bilinçli olarak km-mertebesinde çekirdeklenme kullandığını gösterir; çözünürlük gereği böyledir ve doğadaki değerin kanıtı değildir.
- **1/t hızlanmanın yükleme hızını geçtiği an.** V(t) ≈ (a/b)D_c/(t_f − t) (H ≈ b/D_c, düzen-büyüklüğü). V = V_L koşulu t* ≈ (a/b)D_c/V_L verir. V_L = 20 mm/yıl ≈ 6.3·10⁻¹⁰ m/s ve a/b = 0.8 için:

| D_c | t* |
|---|---|
| 10 µm | ≈ 3.5 saat |
| 1 mm | ≈ 15 gün |
| 10 mm | ≈ 5 ay |
| 0.1 m | ≈ 4 yıl |

  BP1 parametreleriyle (V_p = 10⁻⁹ m/s) t* ≈ 60 gün. **Sonuç:** saf homojen RSF'de yıl ölçekli bir hızlanma ancak D_c ~ 0.1 m mertebesinde mümkündür. Bu değer laboratuvar değerlerinin 100–10⁴ katıdır ve Fryer vd. (2026) tahminiyle (0.3–3 mm, Bölüm 5) çelişir.
- **Moment ve gözlenebilirlik (nokta kaynak, u ~ M₀/(μR²), ε ~ M₀/(μR³), düzen-büyüklüğü):**

| Durum | Yama | Toplam kayma | M₀ | Mw | Ne demek |
|---|---|---|---|---|---|
| D_c = 1 mm, L_b = 40 m | sabit yama, yarıçap ≈ 55 m | ≈ 5 mm | ≈ 1.4·10¹² N·m | ≈ 2.0 | 10 km'de u ≈ 0.5 µm, ε ≈ 5·10⁻¹¹; GNSS ve sondaj kuyusu gerinimölçerinin çok altında |
| D_c = 10 mm, a/b = 0.8 | L_∞ ≈ 3 km | ≈ D_c/(1−a/b) ≈ 5 cm | ≈ 5·10¹⁶ N·m | ≈ 5.1 | yüzeyde mm–cm mertebesinde yer değiştirme; sınırda algılanır |
| D_c = 10 mm, a/b = 0.9 | ≈ 13 km | ~0.1 m | ~10¹⁸ N·m | ~6 | her geodezik ağın göreceği bir yavaş kayma |

  **Gözlenebilirlik tamamen D_c ve a/b'nin bilinmeyen doğal değerlerine bağlıdır.**
- **Deniz altı.** Kilitli kısım deniz altında ve kıyıdan 10–20 km uzaktaysa R büyür. Bu, u'yu R⁻², ε'yi R⁻³ ile düşürür. Kıyı istasyonları için küçük çekirdeklenme durumu kesinlikle görünmez; deniz tabanı geodezisi gerekir.
- **Yükleme zaman ölçeği.** t_a = aσ/τ̇. a = 0.01, σ = 100 MPa ve τ̇ ≈ 0.01–0.1 MPa/yıl (varsayım) için t_a ≈ 10–100 yıl. Bu, Dieterich (1992) çözümündeki üstel terimin geç-döngü yükleme etkisinin onlarca yıl ölçeğinde işlediğini gösterir. Ama bu bir "hızlanma sinyali" değil, yavaş bir arka plandır.

### Gaps
- Doğal faylar için D_c, a/b ve σ_eff doğrudan ölçülemiyor; kuramın sayısal çıktısı bu üç bilinmeyene logaritmik değil doğrusal ya da karesel duyarlı. Bu nedenle tek bir "öngörülen çekirdeklenme boyu" verilemiyor.
- Rice (1993) h* formülü, Dieterich (1992) tam çözümü ve SEAS BP1 parametreleri birincil metinden doğrulanamadı (erişim reddi / özet yok).
- 3-B ve tam dinamik etkiler (mod II/III karışımı, serbest yüzey) için kapalı-form L_∞ yok; Zhai & Huang (2024) ile Kaneki & Noda (2025) yalnız 2-B.

---

## 2. Ön-kayma (preslip) ve çağlayan (cascade) modeli; bütünleşik modeller

### Takeaway
Ön-kayma modeli, öncü depremleri ve ana şokun başlangıcını, ana şoku denetleyen ve kararlı biçimde büyüyen aseismik bir yamanın yan ürünü sayar. Çağlayan modeli bunları yalnız depremden depreme gerilme aktarımıyla açıklar; aseismik öncül öngörmez. 2019–2026 kuramı iki uç üyeyi tek bir süreklilikte birleştirir. Fay heterojenliği, yükleme hızı ve boşluk basıncı süreci ön-kayma ucundan çağlayan ucuna kaydırır. McLaskey (2019) doğal koşullar için L_c'nin 1 m'den küçük değerlerden 10 km'den büyük değerlere kadar uzanan bir yelpazeye yayılmasını bekler.

### Cited Findings
- **Ellsworth & Beroza (1995):** M2.6–8.1 aralığındaki 30 depremde, moment salınımı düşük bir "sismik çekirdeklenme evresi" görülüyor. Bu evrenin boyu ve süresi nihai büyüklükle ölçekleniyor; ardından moment hızı karesel büyüyor. Yazarların yorumu: "the nucleation process exerts a strong influence on the size of the eventual earthquake". Bu gözlemsel çalışma ön-kayma görüşünün temelidir. — [Ellsworth & Beroza 1995, Science 268, 851–855, doi:10.1126/science.268.5212.851](https://doi.org/10.1126/science.268.5212.851)
- **McLaskey (2019), derleme + 3 m'lik kaya deneyi:** Yavaş ve düzgün hızlanan çekirdeklenme L_c'ye kadar genişliyor, sonra dinamik kırılmaya geçiyor. Kararlı durumun üzerine bir "kick" verildiğinde başlangıç daha küçük ve ani oluyor. Daha güçlü bir yamaya sünme cephelerinin yakınsaması da ani başlangıç üretiyor. Bu iki mekanizma birlikte, hıza bağlı bir **"cascade up"** modelini öneriyor. Yerkabuğunda "slip limited environments with L_c < 1 m, to ignition-limited environments with L_c > 10 km" bekleniyor. İkinci durumda tetikleyen, yamanın kritik boya ulaşması değil, kayma hızının kritik bir güç yoğunluğunu aşmasıdır. — [McLaskey 2019, JGR 124, doi:10.1029/2019JB018363](https://doi.org/10.1029/2019jb018363) (açık erişim yok; özet üzerinden)
- **Kato & Ben-Zion (2021) derlemesi:** Bulguları şöyle özetliyor: depremlerin yol açtığı kaya hasarıyla bölgesel zayıflama, ve bazı büyük depremlerden "a few years before" deformasyonun nihai kırılma zonuna doğru giderek yerelleşmesi. Son evre, koşullara göre çok ölçekli yavaş kayma geçicileri ve öncü depremlerin karışımı. Yazarlar ön-kayma, çağlayan ve "progressive localization" çerçevelerini birleştiren bir model öneriyor. Kaynak: yalnız özet ve web özeti; tam metin erişilmedi. — [Kato & Ben-Zion 2021, Nat. Rev. Earth Environ. 2, 26–39, doi:10.1038/s43017-020-00108-w](https://doi.org/10.1038/s43017-020-00108-w); [ERI özeti](https://www.eri.u-tokyo.ac.jp/en/?p=4019)
- **Yamashita vd. (2021), metre ölçekli fay:** Az heterojen fayda az sayıda öncü deprem oluşuyor ve bunlar ön-kayma güdümlü. Çok heterojen (ön-mevcut fay unu, gouge) fayda daha çok öncü ve daha düşük b-değeri görülüyor, "cascade-up" özellikleriyle. — [Yamashita vd. 2021, Nat. Commun. 12, doi:10.1038/s41467-021-24625-4](https://doi.org/10.1038/s41467-021-24625-4)
- **Marty vd. (2023), 30–60 MPa:** Akustik emisyon (AE) etkinliği fay boyunca kayma hızınca sürükleniyor. Yığılmış diziler ters-Omori yasasına uyuyor; Omori c zamanı 1/σ ile ölçekleniyor. b-değeri son evrede ≈1'den ≈0.5'e düşüyor. Öncüler, RSF çekirdeklenme boyuyla uyumlu bir uzaklıkta duruluyor. Süreç "almost fully aseismic" başlıyor ve dinamik kırılma eşiğinde çağlayana evriliyor. — [Marty vd. 2023, JGR, doi:10.1029/2022JB026294](https://doi.org/10.1029/2022jb026294)
- **Goebel vd. (2024):** Yüksek akışkan basıncı ve düşük pürüzlülük, daha hızlı kayma ivmelenmesi ve **daha kısa öncül süreleri** veriyor. Uzun öncü etkinliği daha çok "immature faults at shallow depth" için olası. — [Goebel vd. 2024, Nat. Commun., doi:10.1038/s41467-024-49959-7](https://doi.org/10.1038/s41467-024-49959-7)
- **Wang vd. (2023), DEM:** Son olay, etkileşen birden çok ön-kayma çekirdeklenme alanının ürünü olabiliyor. Ayrıca **"non-precursory" hızlanan aseismik kayma** var: hızlanıyor ama gelecek ana şokla ilişkili değil. — [Wang vd. 2023, JGR, doi:10.1029/2022JB026066](https://doi.org/10.1029/2022jb026066)
- **Gözlemsel sınama (Hector Mine, M7.1 doğrultu atımlı):** Öncüler ve ana şok çekirdeklenmesi yeniden incelenmiş. — [Yoon vd. 2019, JGR, doi:10.1029/2018JB016383](https://doi.org/10.1029/2018jb016383) (yalnız başlık ve künye; ayrıntılar bu oturumda okunmadı)
- **1999 İzmit:** Ellsworth & Bulut (2018, Nature Geoscience) öncü dizinin bir çağlayanla uyumlu olduğunu savunmuştur. Künye ve DOI bu oturumda **doğrulanamadı**.

### Inferences
- **Nicel karşılaştırma (kendi çıkarım).**
  - *Ön-kayma modeli:* Toplam öncül moment ≈ μ·(π L²)·(birkaç D_c). Süre ∝ D_c/V_L (Bölüm 1). Öncüler yama kenarında ve L ölçeğinde bir alana sıkışır. Öncü göç hızı Ampuero & Rubin'deki gibi ∝ V·μ′/(bσ ln).
  - *Çağlayan modeli:* Aseismik öncül moment ≈ 0. Öncülerin zamanlaması ETAS-benzeri istatistikle verilir. Ana şok büyüklüğü öncülerden bilgi taşımaz.
  - Bütünleşik model sınanabilir bir ayrım verir: aseismik/sismik moment oranı ve bu oranın zamanla değişimi (Marty vd. 2023).
- Kuzey Anadolu Fayı (KAF) büyük atımlı ve olgun bir faydır. Goebel vd. (2024) ve Yamashita vd. (2021) laboratuvar eğilimleri doğaya taşınabilirse, böyle bir fayda uzun süreli öncü etkinliği değil, kısa ve ön-kayma güdümlü bir son evre beklenir. Bu bir analoji çıkarımıdır; doğrudan kanıtlanmış değildir.

### Gaps
- McLaskey (2019) ve Kato & Ben-Zion (2021) tam metinlerine erişilemedi. Bu yüzden ignition-limited rejimin güç yoğunluğu eşiği ve bütünleşik modelin nicel parametreleri **doğrulanamadı**.

---

## 3. Nihai büyüklük çekirdeklenmeden bilinebilir mi? (büyüklük belirlenimciliği, kuram tarafı)

### Takeaway
Homojen RSF kuramı ve Lapusta & Rice (2003) **zayıf ya da sıfır belirlenimcilik** öngörür: çekirdeklenme L_b–L_∞ ile, nihai büyüklük ise yayılmayı durduran gerilme ve sürtünme dağılımıyla belirlenir. Sabit uzunluk tarzı çekirdeklenme en çok **minimum** kırılma boyutunu kestirmeye izin verir. Laboratuvar temelli yarı-ampirik ölçeklemeler (Acosta vd. 2019) ve kaynak zaman fonksiyonu (STF) çalışmaları bir ilişki önerir, ama gözlemsel sınamaların çoğu "zayıf belirlenimcilik" lehine çıkıyor.

### Cited Findings
- **Lapusta & Rice (2003):** "Small and large events have very similar nucleation phases". Erken moment ivmesindeki düzensizlikler önceki olayların bıraktığı gerilme heterojenliğinden kaynaklanıyor. Bu, büyüklüğün çekirdeklenmede kodlanmadığı anlamına gelir. — [doi:10.1029/2001JB000793](https://doi.org/10.1029/2001jb000793)
- **Zhai & Huang (2024):** Sabit uzunluk tarzının baskın olması "suggests that the minimum size of earthquake rupture may be estimated at the early stage of the nucleation phase". Yani alt sınır kestirilebilir, nihai boyut değil. — [doi:10.1029/2024JB029719](https://doi.org/10.1029/2024jb029719)
- **Acosta vd. (2019):** Laboratuvarda öncül moment salınımı ile ana şok büyüklüğü arasında sistematik bir ilişki var. Çekirdeklenme kuramından yarı-ampirik bir ölçekleme türetilmiş. Mw 6–9 doğal örnekler bu ölçeklemenin dışdeğerlemesine "seem to follow". Ölçekleme formülü özet üzerinden **doğrulanamadı**. — [Acosta vd. 2019, GRL, doi:10.1029/2019GL084744](https://doi.org/10.1029/2019gl084744)
- **Fryer vd. (2026):** Öncü depremin yarattığı kayma patlaması bir geçici hız V_min üretiyor ve bu hız çekirdeklenme süresini ve uzunluğunu "robustly predicts". Büyük öncü, dinamik kırılmaya daha hızlı geçiş demek. Çok küçük impulslar kırılmayı tamamen durdurabiliyor. Bu bir zamanlama belirlenimciliğidir, büyüklük belirlenimciliği değil. — [Fryer, Garagash, Lebihain & Passelègue 2026, Nature, doi:10.1038/s41586-026-10497-5](https://doi.org/10.1038/s41586-026-10497-5)
- **Gözlemsel sınamalar (STF / erken uyarı):**
  - Zayıf belirlenimcilik: [Goldberg vd. 2018, JGR, doi:10.1029/2018JB015962](https://doi.org/10.1029/2018jb015962); [Melgar & Hayes 2019, Sci. Adv., doi:10.1126/sciadv.aav2032](https://doi.org/10.1126/sciadv.aav2032)
  - "No evidence for strong determinism": [Trugman vd. 2019, GRL, doi:10.1029/2019GL083624](https://doi.org/10.1029/2019gl083624)
  - "Apparent" öngörülebilirliğin seçim etkisi olabileceği: [Meier vd. 2021, GJI, doi:10.1093/gji/ggaa610](https://doi.org/10.1093/gji/ggaa610)
  - Karşı yönde: Zeng vd. (2025), 2126 STF (Mw ≥ 5.5) üzerinde eğittikleri bir transformer modeliyle Mw ≤ 7 için saniyenin altında %80.0, Mw 7–8 için 3–5 s'de %86.9 doğruluk bildiriyor. — [Zeng vd. 2025, JGR Mach. Learn. Comput., doi:10.1029/2025JH000801](https://doi.org/10.1029/2025jh000801)
  - Bunların hepsi kırılma başladıktan sonraki saniyeler içindir; deprem öncesi çekirdeklenme için değil.

### Inferences
- Yıl ölçekli öngörü açısından belirlenimcilik tartışmasının pratik değeri sınırlıdır. Taraflarca savunulan en güçlü belirlenimcilik bile kırılma başladıktan **saniyeler** sonrasına aittir. Acosta tipi bir ölçekleme doğru olsa bile, Mw 7 için gereken öncül momentin geodezik olarak görülmesi Bölüm 1'deki D_c ikilemine bağlıdır.

### Gaps
- Fayın 3-B segmentasyonu (Marmara'nın çok segmentli geometrisi gibi) ile çekirdeklenme arasındaki ilişki için kuramsal bir büyüklük kestirimi bulunamadı.

---

## 4. Heterojen faylar: pürüzlü faylarda çekirdeklenme, aseismik kaymayla sürülen öncü depremler, zaman ölçekleri

### Takeaway
Heterojenlik (pürüzlülük kaynaklı σ değişimi, sürtünme ya da D_c değişkenliği) çekirdeklenmeyi homojen tek yamadan, sünme ile öncü depremler arasındaki karşılıklı geri beslemeye dönüştürür. Cattania & Segall (2021) bu geri besleme için **kayma hızı ve sismisite hızı ∝ 1/t** (t: ana şoka kalan süre) öngörür. Heterojenlik ölçeği çekirdeklenme boyuna göre ortalamaya giren, yerel ya da uç değer güdümlü rejimler tanımlar. Bulunan kuramsal zaman ölçekleri saatler–aylar aralığındadır. Yıl ölçeği yalnız düşük yükleme hızlı kıtasal faylar için (He vd. 2023) ve hasar/yerelleşme çerçevesinde (Kato & Ben-Zion) önerilmiştir.

### Cited Findings
- **Cattania & Segall (2021):** 2-B quasi-dinamik, sürtünmece homojen ama fraktal pürüzlü RSF fayları, pürüzlülük dalga boyu > çekirdeklenme boyu. Düşük σ bölgeleri sünüyor, yüksek σ bölgeleri kilitli kalıp sismik kırılıyor. Ana şoklar tercihen daha güçlü pürüzlerde başlıyor. Öncül evrede öncü patlamaları sünmeyi hızlandırıyor, sünme de başka pürüzleri yüklüyor. Analitik geri besleme modeli "predicts slip velocities and seismicity rates increase as **1/t**". Model yığılmış kataloglardaki 1/t ivmelenmeyi ve öncülerin hiposantra göçünü yeniden üretiyor. Simülasyonlardaki mutlak süreler ve parametre değerleri **doğrulanamadı** (Wiley 403; ikincil PDF erişimi reddedildi). — [Cattania & Segall 2021, JGR 126, e2020JB020430, doi:10.1029/2020JB020430](https://doi.org/10.1029/2020jb020430)
- **Schaal & Lapusta (2019), 3-B:** Daha yüksek sıkışmalı yamalar, büyük ölçekli aseismik çekirdeklenme sırasında küçük depremler üretiyor. Bu ancak öncü olaylar ile ana şokların çekirdeklenme ölçekleri arasında yeterli ayrım varsa oluyor. — [Schaal & Lapusta 2019, JGR, doi:10.1029/2018JB016395](https://doi.org/10.1029/2018jb016395)
- **Lebihain vd. (2021):** Zayıflama hızı heterojenliği için analitik çerçeve, üç kararsızlık rejimi: yerel, uç değer (extremal) ve homojenleşmiş. Çekirdeklenme boyundan çok küçük ölçekli heterojenlikler ortalamaya girer. — [Lebihain vd. 2021, GRL, doi:10.1029/2021GL094901](https://doi.org/10.1029/2021gl094901)
- **Li, Niemeijer & van Dinther (2024):** Stokastik σ heterojenliği altında, heterojenlik dalga boyu ile çekirdeklenme boyu oranına göre beş rejim var. Çekirdeklenme düşük σ bölgesinden komşu yüksek σ bölgesine göçebiliyor. Bu sırada başlangıçtaki bölgede büyük aseismik kayma ve gerilme düşümü oluyor; bu süreç öncü göçüyle bağlantılı olabilir. — [Li vd. 2024, JGR, doi:10.1029/2024JB029857](https://doi.org/10.1029/2024jb029857)
- **Harbord vd. (2017), pürüzlü granit:** Hız-pekleşmeli rejimde de stick-slip gözleniyor; σ arttıkça kayma kararlılaşıyor. Bu, standart kararlılık analizinin öngörmediği bir durum. Yeni ölçüt, kırılma enerjisine ve pürüzlülüğün yarattığı zayıf yama boyuna dayanıyor. — [Harbord vd. 2017, Geology 45, 931, doi:10.1130/G39181.1](https://doi.org/10.1130/g39181.1)
- **Buijze vd. (2020), fay unlu (gouge) büyük ölçekli deney:** Çekirdeklenme yüksek τ/σ_n bölgelerinde başlıyor. Öncül kayma fayın büyük bir kesrini kaplıyor. σ₂ düşünce çekirdeklenme boyu artıyor. — [Buijze vd. 2020, JGR, doi:10.1029/2019JB018429](https://doi.org/10.1029/2019jb018429)
- **He vd. (2023):** WZcore süresi yitim zonlarında haftalar, düşük yükleme hızlı kıtasal faylarda yıllar. — [doi:10.1029/2023JB026422](https://doi.org/10.1029/2023jb026422)
- **Sismisite hızı kuramı:** Dieterich (1994), sismisiteyi RSF çekirdeklenme kaynaklarından oluşan bir nüfus olarak modeller. Bir gerilme basamağından sonra Omori bozunmasını verir; artçı süresi t_a = Aσ/τ̇ ana şok yinelenme süresiyle orantılıdır. Formülasyon "may be applied to stressing histories of arbitrary complexity". — [Dieterich 1994, JGR 99, 2601–2618, doi:10.1029/93JB02581](https://doi.org/10.1029/93jb02581). Heimisson & Segall (2018) modeli yeniden türetiyor: kararlı durum üzerinde olmayan kaynaklar için Omori dizisi oluşmuyor. — [doi:10.1029/2018JB015656](https://doi.org/10.1029/2018jb015656)

### Inferences
- **Zaman ölçeği (kendi çıkarım).** Cattania–Segall türü 1/t yasası çekirdeklenme zamanı t_f'yi tanımlar. Ancak sinyalin arka plan gürültüsünden ayrıldığı süre, hızın arka plan değerini kaç kat aştığına bağlıdır. 1/t yasasında hız t_f − t = T₀'da arka planın 10 katı ise, 10·T₀'da arka plan düzeyindedir. Yani **algılanabilir pencere, katsayıyı belirleyen D_c ve σ ile, sinyal-gürültü oranıyla logaritmik değil doğrusal biçimde sınırlanır**.
- **Dieterich 1994'ten:** Sismisite hızı oranı R/r, yeni gerilme hızının arka plan gerilme hızına oranına (τ̇/τ̇_r) yaklaşır; geçiş süresi t_a'dır. Çekirdeklenme bölgesi çevresinde gerilme hızı 1/t ile artarsa, öncü sismisite de yalnız o bölgenin ~L boyutlu çevresinde 1/t ile artar. L ≤ 1 km ise bu sinyal, kayıtlı katalogdaki birkaç olaya, ya da tamamlılık eşiğinin altındaki olaylara indirgenir.

### Gaps
- Cattania & Segall (2021) simülasyonlarındaki öncül evrenin mutlak süresi ve a, b, D_c, σ değerleri tam metinden okunamadı.
- "2026 San Jacinto 19 kümelenmiş öncü dizi" (doi:10.1029/2025GL120398) yalnız başlıktan görüldü; içeriği okunmadı.

---

## 5. D_c ve çekirdeklenme boyunun laboratuvardan doğaya ölçeklenmesi; hızlanmanın algılanabilir süresi (1/t, Voight / ters hız)

### Takeaway
Laboratuvar D_c değerleri 1–100 µm aralığında. Sismolojik kırılma enerjisinden türetilen dinamik zayıflama mesafeleri cm–m mertebesinde, ama bunlar çekirdeklenmeyi yöneten D_c değil. Fryer vd. (2026) doğal çekirdeklenme için D_c ≈ **0.3–3 mm** öneriyor. Bu aralık, Bölüm 1'in hesabıyla yükleme hızının aşılmasını **saatler–haftalar** ölçeğine yerleştirir; yıl ölçeğine değil. 1/t (ters hız doğrusal) yasası, başarısızlığa kadar ivmelenen her olgu için başarısızlık zamanı tahmin yönteminin (FFM, Voight) α = 2 durumuna karşılık gelir. Ancak volkan ve heyelan literatürü bu yöntemin gürültü ve tek-gerçekleşme sınırlarını belgeliyor.

### Cited Findings
- **Fryer vd. (2026):** Öncülerin yarattığı geçici V_min ölçeklemesi doğal öncü ve yavaş kayma dizilerine uygulanmış; bu diziler "seem to follow the same scaling". Buradan "realistic characteristic nucleation slip distances of **0.3–3.0 mm**, orders of magnitude smaller than those inferred for dynamic rupture" çıkarılıyor. Formül ve doğal örnek listesi **doğrulanamadı**: Nature tam metni giriş yönlendirmesi verdi, aşılmadı. — [doi:10.1038/s41586-026-10497-5](https://doi.org/10.1038/s41586-026-10497-5)
- **Rubin & Ampuero (2005):** Yüzey sismometresiyle algılanabilirlik için D_c ≈ 100 µm ve a/b ≈ 0.95 gibi laboratuvar aralığının üst ucu gerekiyor. — [doi:10.1029/2005JB003686](https://doi.org/10.1029/2005jb003686)
- **McLaskey (2019):** L_c doğada 1 m'nin altından 10 km'nin üstüne kadar değişebilir. — [doi:10.1029/2019JB018363](https://doi.org/10.1029/2019jb018363)
- **Kaneki & Noda (2025):** Son evrede dM/dt ∝ t_f⁻¹ (yaşlanma ve Nagata yasaları), ≈ t_f⁻⁰·⁹ (değiştirilmiş kayma yasası). Bu, ters moment hızının t_f'ye doğrusal yaklaştığı anlamına gelir. — [doi:10.1186/s40623-025-02269-8](https://doi.org/10.1186/s40623-025-02269-8)
- **Marty vd. (2023):** Yığılmış AE dizileri ters-Omori yasasına uyuyor. Çekirdeklenme zaman ölçeği σ ve çekirdeklenme boyuyla ters ölçekleniyor. — [doi:10.1029/2022JB026294](https://doi.org/10.1029/2022jb026294)
- **Kuramın gözlemle sınanması, Blétery & Nocquet (2023):** 90 Mw ≥ 7 depremden önceki 48 saat boyunca 3026 yüksek örneklemeli GPS zaman serisi yığılmış. Sonuç: "≈2-hour-long exponential acceleration". Zaman ölçeği küçük D_c ile uyumlu, yıl ölçeğiyle değil. — [Science 381, 297–301, doi:10.1126/science.adg2565](https://doi.org/10.1126/science.adg2565)
  - Tartışma: Ağ ortak-mod gürültüsü düzeltildiğinde sinyal kayboluyor. Yazarlara göre ortak-mod filtresi tektonik sinyali de silebilir, ve sinyalin yalnız gürültüden doğma olasılığı geçmiş kayıtlara göre %1'in altında. Yine de "do not irrefutably demonstrate". — [Blétery & Nocquet 2025, Seismica 3(2), doi:10.26443/seismica.v3i2.1383](https://doi.org/10.26443/seismica.v3i2.1383)
  - Bağımsız eleştiri makaleleri (ör. Bradley & Hubbard 2024) bu oturumda **doğrulanamadı**.
- **FFM / ters hız yöntemi:** Volkan ve malzeme yenilmesi bağlamında değerlendirilmiş: [Bell, Naylor & Main 2011, GRL, doi:10.1029/2011GL048155](https://doi.org/10.1029/2011gl048155). Öngörülebilirlik sınırları: [Bell vd. 2013, GJI, doi:10.1093/gji/ggt191](https://doi.org/10.1093/gji/ggt191). İçerik yalnız başlıktan görüldü; yazar adları bilgiye dayalıdır.

### Inferences (kendi kaba hesap)
- D_c = 0.3–3 mm, a/b = 0.8 ve V_L = 20 mm/yıl için yükleme hızının aşıldığı süre t* ≈ (a/b)D_c/V_L ≈ **4–45 gün**. Bu, 10 kat aşmayı aramak değil, kaymanın yükleme hızına yalnızca eşitlendiği anı vermektedir. Algılanabilir aşma bunun ~1/10'u, yani **saatler–birkaç gün** olur.
- Kaba sonuç: **homojen ya da sürtünme heterojen RSF kuramı, D_c'nin bugünkü en iyi tahminleriyle, büyük doğrultu atımlı bir depremden önce yıl ölçekli bir 1/t ivmelenmesi öngörmez.** Yıl ölçeği için D_c'nin ~10–100 kat büyük olması, ya da RSF dışı bir mekanizma gerekir: hasar ve yerelleşme, akışkan basıncı geçicileri ya da derin sünme transientleri (Bölüm 6).
- Voight/FFM ile t_f kestirimi ancak hızlanma başladıktan sonra ve gürültü tabanının üstünde yapılabilir. Yukarıdaki hesapla bu pencere günler–saatler mertebesinde.

### Gaps
- Fryer vd. (2026) ölçeklemesinin tam biçimi ve kullanılan doğal örnekler (doğrultu atımlı olup olmadıkları) okunamadı.
- D_c'nin derinlik ve sıcaklık bağımlılığına dair kuramsal bir çerçeve bu taramada bulunamadı.

---

## 6. Kısmen sünen faylar ve geç döngü: yıl ölçekli öncül veren kuramsal öngörüler

### Takeaway
Yıl ölçekli bir sinyali öngören tek kuramsal yollar şunlardır:
- (a) Düşük yükleme hızlı kıtasal faylarda zayıflama çekirdeğinin (WZcore) uzun süresi (He vd. 2023);
- (b) Sünme cephesinin kilitli yamanın içine ilerlemesi ve kilitli-sünen sınırında çekirdeklenme (Lapusta & Rice 2003; Kaneki & Noda 2025);
- (c) Hasar reolojisi ve "progressive localization" (Kato & Ben-Zion 2021; Ben-Zion & Zaliapin 2020: büyük depremlerden 2–3 yıl önce sismisite yerelleşmesi);
- (d) Dieterich (1994) sismisite hızının, derin sünme transientleriyle değişen gerilme hızına duyarlılığı.

Bunların hiçbiri bir "zaman daraltma" garantisi vermez. (b) ve (d) ayrıca ana şokla ilişkisiz olabilir: "non-precursory" hızlanma (Wang vd. 2023) ve ortak-mod gürültüsü tartışması.

### Cited Findings
- **He vd. (2023):** "Duration of the WZcore is weeks before large subduction earthquakes under high driving rate, but years on low-rate continental faults". Yazarlar WZcore'daki yüksek kayma hızının küçük pürüzlerde sismisiteyi artıracağını **varsayıyor**. — [doi:10.1029/2023JB026422](https://doi.org/10.1029/2023jb026422)
- **Lapusta & Rice (2003):** Doğrultu atımlı modelde olaylar kilitli-sünen geçişte, sismojenik zonun tabanında çekirdekleniyor. Erken moment ivmesi sünen bölgelerin sınırındaki gerilme yoğunlaşmasından etkileniyor. — [doi:10.1029/2001JB000793](https://doi.org/10.1029/2001jb000793)
- **Kaneki & Noda (2025):** Yaşlanma yasasında sünme cephesi hızlanmayla birlikte sismojenik yamanın içine ilerliyor. Diğer yasalarda yavaş kırılmanın ara sıra geri dönüşü (switchback) daha uzun bir sünen bölge bırakıyor. — [doi:10.1186/s40623-025-02269-8](https://doi.org/10.1186/s40623-025-02269-8)
- **Harris (2017) derlemesi:** Sünen kıtasal faylarda ≤ M6.6 depremler kilitli eşdeğerleriyle benzer kırılma alanı ve sarsıntı üretiyor. Daha büyük depremler için gözlem kıt; boşluğu simülasyonlar doldurmalı. — [Harris 2017, Rev. Geophys. 55, doi:10.1002/2016RG000539](https://doi.org/10.1002/2016rg000539)
- **Kato & Ben-Zion (2021):** Bazı büyük depremlerden "a few years before" kırılma zonu çevresinde ilerleyen yerelleşme. — [doi:10.1038/s43017-020-00108-w](https://doi.org/10.1038/s43017-020-00108-w)
- **Ben-Zion & Zaliapin (2020):** Landers 1992, Hector Mine 1999, El Mayor-Cucapah 2010 ve Ridgecrest 2019 ana şoklarından önceki onyıllarda kırılma zonları çevresinde kaya hasarı oluşmuş. Bu ana şoklardan 2–3 yıl önce sismisitede yerelleşme (azalan kesirsel alan) görülmüş. — [Ben-Zion & Zaliapin 2020, GJI 223, doi:10.1093/gji/ggaa315](https://doi.org/10.1093/gji/ggaa315). Arama özeti üzerinden; tam metin okunmadı. Ölçütün yanlış alarm oranı **doğrulanamadı**.
- **Wang vd. (2023):** Hızlanan ama öncül olmayan aseismik kayma, "weakly coupled but possesses the potential to be triggered seismically" bir segmenti gösteriyor olabilir. — [doi:10.1029/2022JB026066](https://doi.org/10.1029/2022jb026066)
- **Kaya hasarı ve kırılgan yenilme laboratuvarı:** Granitte yenilme öncesi aseismik gerinim yerelleşmesi ve buna eşlik eden sismisite. — [Sci. Rep. 2024, doi:10.1038/s41598-024-75942-9](https://doi.org/10.1038/s41598-024-75942-9) (yalnız başlık görüldü)

### Inferences
- Kuram bir "yıl ölçekli sinyal olabilir" penceresi bırakır, ama bu pencere çekirdeklenmenin kendisinden çok **çekirdeklenmeye hazırlayan** süreçlere aittir: sünme cephesi, hasar, yerelleşme. Bu süreçlerin sinyali, ana şoku izlemeyen benzer sinyallerden (yanlış alarm) kuramsal olarak ayrılamaz. Ayrım ancak istatistiksel sınamayla yapılabilir.
- Marmara için (kendi çıkarım):
  - Kilitli segmentin kenarları, yani batıdaki sünme ya da kısmi kilitlenme bölgeleri ve kilitli-sünen derinlik geçişi, (b) mekanizmasının kuramsal olarak beklendiği yerlerdir.
  - Bu bölgelerin büyük kısmı deniz altında kalır. Yer değiştirme R⁻², gerinim R⁻³ ile azaldığından kıyı ağının duyarlılığı sınırlıdır.
  - Bu not Marmara verisine bakmadığı için hangi segmentin bu durumda olduğuna dair bir şey iddia etmez.

### Gaps
- Kısmen sünen bir doğrultu atımlı fayda geç döngüde öncül yavaş kaymanın olasılık dağılımını veren kuramsal bir çalışma bulunamadı. Mevcut simülasyonlar 2-B ve tek segmentli.
- Hasar reolojisi modellerinin (Lyakhovsky–Ben-Zion çizgisi) nicel öncül öngörüleri bu taramada birincil kaynaktan okunamadı.

---

## Sınanabilir kuramsal öngörüler

Etiketler: **[0 €]** = açık veriyle şimdi sınanabilir · **[yeni veri]** = yeni ölçüm ya da ağ gerekir · **[sınanamaz]** = mevcut ilkelerle sınanamaz.

| # | Kuramsal öngörü (kaynak) | Gözlenebilir | Öngörülen büyüklük | Zaman ölçeği | Gereken veri | Açık veri var mı? | Durum |
|---|---|---|---|---|---|---|---|
| 1 | Homojen RSF, D_c = 0.3–3 mm: kayma 1/t, V > V_L ancak t_f − t ≲ (a/b)D_c/V_L (Dieterich 1992; Fryer vd. 2026; kendi hesap) | Fay üzerinde kayma hızı / yüzey yer değiştirmesi | Çekirdeklenme momenti ~Mw 1–3 (L ~ 10–100 m); 10 km'de u ≲ 1 µm, ε ~ 10⁻¹¹–10⁻¹⁰ | Saatler–haftalar | Fay üstü / kuyu içi gerinim, deniz tabanı geodezisi | Hayır, bu duyarlılıkta değil | **[yeni veri]**; doğal fayda pratikte **[sınanamaz]** |
| 2 | Yaşlanma yasası, a/b → 1, D_c ≥ 10 mm: genişleyen çekirdeklenme L_∞ ~ km–10 km (Rubin & Ampuero 2005) | Bölgesel yavaş kayma, cm mertebesinde GNSS sinyali | Mw ~5–6 eşdeğeri öncül moment | Aylar–yıllar | Sürekli GNSS / InSAR | Evet, küresel ve geçmiş depremler için (Nevada Geodetic Lab vb. ve Sentinel-1 açık arşivleri) | **[0 €]**: Geçmiş M ≥ 6.5 doğrultu atımlı depremlerden önceki aylarda cm ölçekli transientin **yokluğu**, a/b → 1 ve büyük D_c birleşimini geriye dönük sınar |
| 3 | GPS yığınında ≈2 saatlik üstel öncül ivmelenme (Blétery & Nocquet 2023, 2025) | Hiposantra yönlenmiş, yığılmış yüksek örneklemeli GPS | Bireysel istasyonda gürültünün altında; yalnız yığında | ≈2 saat | 5 dk / 1 Hz GNSS, ortak-mod analizi | Evet (yayımlanan yöntem + açık GNSS arşivleri) | **[0 €]**: Bağımsız yeniden üretim ve doğrultu atımlı alt-küme sınaması mümkün |
| 4 | Pürüzlü fayda sünme–öncü geri beslemesi: sismisite ∝ 1/t, hiposantra göç (Cattania & Segall 2021) | Yığılmış öncü sismisite hızı (ters-Omori, p ≈ 1) | Hiposantr çevresinde ~L ölçekli bölgede hız artışı | Saatler–günler (doğrulanamadı) | Yüksek çözünürlüklü, yeniden konumlanmış katalog | Evet, geçmiş Kaliforniya ve küresel kataloglar için | **[0 €]**: Geçmiş dizilerde 1/t ile ETAS (çağlayan) sıfır hipotezi karşılaştırması |
| 5 | Ön-kayma–çağlayan ayrımı: öncül aseismik/sismik moment oranı artar (Marty vd. 2023; Yamashita vd. 2021) | Öncü momentinin geodezik öncül momentle karşılaştırması; b-değeri düşüşü | Laboratuvarda b: 1 → 0.5 | Son evre | Katalog + geodezi | Kısmen (katalog açık, geodezi çoğunlukla duyarsız) | b-değeri kısmı **[0 €]**; moment oranı kısmı **[yeni veri]** |
| 6 | Öncül moment ∝ nihai Mw yarı-ampirik ölçeklemesi (Acosta vd. 2019) | Öncül (sismik + aseismik) moment | Ölçekleme formülü doğrulanamadı | Günler–aylar | Geçmiş depremlerin öncül moment derlemesi | Kısmen | **[0 €]** (geriye dönük, küçük örneklem); ileriye dönük **[yeni veri]** |
| 7 | Öncü depremin yarattığı geçici V_min çekirdeklenme süresini belirler (Fryer vd. 2026) | Öncü büyüklüğü ile ana şoka kalan süre ilişkisi | Büyük öncü → kısa çekirdeklenme | Dakikalar–günler | Öncülü ana şok kataloğu | Evet (geçmiş diziler) | **[0 €]**: Geriye dönük istatistik |
| 8 | Kıtasal düşük yükleme hızlı faylarda WZcore süresi yıllar (He vd. 2023) | Kilitli segmentte yükleme hızını birkaç kat aşan yerel kayma + artan sismisite | Kayma hızı > birkaç × V_L | Yıllar | Fay üstü / yakın geodezi + katalog | Geçmiş kıtasal depremler için kısmen | **[0 €]** geriye dönük (InSAR dönemindeki depremler); ileriye dönük **[yeni veri]** |
| 9 | Sismisite yerelleşmesi (kesirsel alan azalması), büyük depremden 2–3 yıl önce (Ben-Zion & Zaliapin 2020; Kato & Ben-Zion 2021) | Bölgesel katalogda yerelleşme ölçütü | Ölçüt büyüklüğü doğrulanamadı | 2–3 yıl | Uzun, homojen katalog | Evet (geçmiş kataloglar) | **[0 €]**: Yanlış alarm oranıyla birlikte geriye dönük sınama; bu not o sınamayı yapmadı |
| 10 | Dieterich (1994): derin sünme transienti → gerilme hızı değişimi → sismisite hızı R/r → τ̇/τ̇_r, geçiş süresi t_a = aσ/τ̇ ~ 10–100 yıl (varsayım) | Sismisite hızı değişimi ile geodezik transient arasında korelasyon | R/r, gerilme hızı oranına eşit | Aylar–yıllar | Katalog + GNSS | Evet (küresel geçmiş örnekler) | **[0 €]** (geçmiş transient–sismisite çiftleri) |
| 11 | Nihai büyüklük çekirdeklenmede kodlu değil, en fazla minimum boyut (Lapusta & Rice 2003; Zhai & Huang 2024) | Erken STF / P-dalgası ile nihai Mw ilişkisi | Zayıf belirlenimcilik | Kırılma başladıktan sonra 0–5 s | Kaynak zaman fonksiyonu katalogları | Evet (ör. SCARDEC türü açık STF veritabanları) | **[0 €]**, ama yıl ölçekli öngörüyle ilgisiz |
| 12 | Doğal fayda D_c ve a/b'nin doğrudan değeri | Fay üzerinde sürtünme parametreleri | Laboratuvar 1–100 µm; doğal 0.3–3 mm (Fryer vd. 2026) | — | Yerinde deneyler, sondaj | Hayır | **[sınanamaz]** doğrudan; yalnız dolaylı yollarla (satırlar 3, 7) |

### Kaynakça (tam künye; erişim durumu)
- Acosta, M., Passelègue, F., Schubnel, A., Madariaga, R., Violay, M. (2019). Can precursory moment release scale with earthquake magnitude? A view from the laboratory. *GRL*. [doi:10.1029/2019GL084744](https://doi.org/10.1029/2019gl084744). Özet.
- Ampuero, J.-P., Rubin, A.M. (2008). Earthquake nucleation on rate and state faults – Aging and slip laws. *JGR* 113. [doi:10.1029/2007JB005082](https://doi.org/10.1029/2007jb005082). Özet.
- Bell, A.F., Naylor, M., Main, I.G. (2011, 2013). *GRL* [doi:10.1029/2011GL048155](https://doi.org/10.1029/2011gl048155); *GJI* [doi:10.1093/gji/ggt191](https://doi.org/10.1093/gji/ggt191). Yalnız başlık.
- Ben-Zion, Y., Zaliapin, I. (2020). *GJI* 223. [doi:10.1093/gji/ggaa315](https://doi.org/10.1093/gji/ggaa315). Arama özeti.
- Blétery, Q., Nocquet, J.-M. (2023). The precursory phase of large earthquakes. *Science* 381. [doi:10.1126/science.adg2565](https://doi.org/10.1126/science.adg2565). Özet.
- Blétery, Q., Nocquet, J.-M. (2025). Do large earthquakes start with a precursory phase of slow slip? *Seismica* 3(2). [doi:10.26443/seismica.v3i2.1383](https://doi.org/10.26443/seismica.v3i2.1383). Özet.
- Buijze, L. vd. (2020). *JGR*. [doi:10.1029/2019JB018429](https://doi.org/10.1029/2019jb018429). Özet.
- Cattania, C., Segall, P. (2021). Precursory slow slip and foreshocks on rough faults. *JGR* 126, e2020JB020430. [doi:10.1029/2020JB020430](https://doi.org/10.1029/2020jb020430). Özet; tam metin 403.
- Dieterich, J.H. (1992). Earthquake nucleation on faults with rate- and state-dependent strength. *Tectonophysics* 211. [doi:10.1016/0040-1951(92)90055-B](https://doi.org/10.1016/0040-1951(92)90055-b). Özet yok; formüller doğrulanamadı.
- Dieterich, J.H. (1994). A constitutive law for rate of earthquake production and its application to earthquake clustering. *JGR* 99. [doi:10.1029/93JB02581](https://doi.org/10.1029/93jb02581). Özet.
- Ellsworth, W.L., Beroza, G.C. (1995). Seismic evidence for an earthquake nucleation phase. *Science* 268. [doi:10.1126/science.268.5212.851](https://doi.org/10.1126/science.268.5212.851). Özet.
- Fryer, B., Garagash, D.I., Lebihain, M., Passelègue, F. (2026). Foreshock-induced slip transients set mainshock nucleation timing. *Nature*. [doi:10.1038/s41586-026-10497-5](https://doi.org/10.1038/s41586-026-10497-5). Özet; tam metin giriş yönlendirmesi.
- Goebel, T.H.W., Schuster, V., Kwiatek, G., Pandey, K., Dresen, G. (2024). *Nat. Commun.* [doi:10.1038/s41467-024-49959-7](https://doi.org/10.1038/s41467-024-49959-7). Özet.
- Goldberg, D.E. vd. (2018). *JGR*. [doi:10.1029/2018JB015962](https://doi.org/10.1029/2018jb015962); Melgar, D., Hayes, G.P. (2019). *Sci. Adv.* [doi:10.1126/sciadv.aav2032](https://doi.org/10.1126/sciadv.aav2032); Trugman, D.T. vd. (2019). *GRL*. [doi:10.1029/2019GL083624](https://doi.org/10.1029/2019gl083624); Meier, M.-A. vd. (2021). *GJI*. [doi:10.1093/gji/ggaa610](https://doi.org/10.1093/gji/ggaa610). Yalnız başlık; yazar listeleri kısmen doğrulanamadı.
- Guérin-Marthe, S., Nielsen, S., Bird, R., Giani, S., Di Toro, G. (2018). *JGR*. [doi:10.1029/2018JB016803](https://doi.org/10.1029/2018jb016803). Özet.
- Harbord, C., Nielsen, S., De Paola, N., Holdsworth, R. (2017). *Geology* 45. [doi:10.1130/G39181.1](https://doi.org/10.1130/g39181.1). Özet.
- Harris, R.A. (2017). Large earthquakes and creeping faults. *Rev. Geophys.* 55. [doi:10.1002/2016RG000539](https://doi.org/10.1002/2016rg000539). Özet.
- He, C., Zhang, L., Liu, P., Chen, Q.-F. (2023). *JGR*. [doi:10.1029/2023JB026422](https://doi.org/10.1029/2023jb026422). Özet.
- Heimisson, E.R., Segall, P. (2018). *JGR*. [doi:10.1029/2018JB015656](https://doi.org/10.1029/2018jb015656). Özet.
- Kaneki, S., Noda, H. (2025). *Earth Planets Space*. [doi:10.1186/s40623-025-02269-8](https://doi.org/10.1186/s40623-025-02269-8). Özet.
- Kaneko, Y., Nielsen, S.B., Carpenter, B.M. (2016). *JGR* 121. [doi:10.1002/2016JB013143](https://doi.org/10.1002/2016jb013143). Özet.
- Kato, A., Ben-Zion, Y. (2021). The generation of large earthquakes. *Nat. Rev. Earth Environ.* 2. [doi:10.1038/s43017-020-00108-w](https://doi.org/10.1038/s43017-020-00108-w). Özet yok; ERI ve arama özeti.
- Lapusta, N., Rice, J.R. (2003). *JGR* 108(B4). [doi:10.1029/2001JB000793](https://doi.org/10.1029/2001jb000793). Özet.
- Lebihain, M., Roch, T., Violay, M., Molinari, J.-F. (2021). *GRL*. [doi:10.1029/2021GL094901](https://doi.org/10.1029/2021gl094901). Özet.
- Li, M., Niemeijer, A., van Dinther, Y. (2024). *JGR*. [doi:10.1029/2024JB029857](https://doi.org/10.1029/2024jb029857). Özet.
- Marty, S. vd. (2023). *JGR*. [doi:10.1029/2022JB026294](https://doi.org/10.1029/2022jb026294). Özet.
- McLaskey, G.C. (2019). Earthquake initiation from laboratory observations and implications for foreshocks. *JGR* 124. [doi:10.1029/2019JB018363](https://doi.org/10.1029/2019jb018363). Özet.
- Rubin, A.M., Ampuero, J.-P. (2005). *JGR* 110. [doi:10.1029/2005JB003686](https://doi.org/10.1029/2005jb003686); (2009) *JGR* 114. [doi:10.1029/2009JB006529](https://doi.org/10.1029/2009jb006529). Özet.
- Schaal, N., Lapusta, N. (2019). *JGR*. [doi:10.1029/2018JB016395](https://doi.org/10.1029/2018jb016395). Özet.
- Wang, X., Dal Zilio, L., Morgan, J.K., Kammer, D.S. (2023). *JGR*. [doi:10.1029/2022JB026066](https://doi.org/10.1029/2022jb026066). Özet.
- Yamashita, F. vd. (2021). *Nat. Commun.* 12. [doi:10.1038/s41467-021-24625-4](https://doi.org/10.1038/s41467-021-24625-4). Özet.
- Yoon, C.E. vd. (2019). *JGR*. [doi:10.1029/2018JB016383](https://doi.org/10.1029/2018jb016383). Yalnız başlık.
- Zeng, S. vd. (2025). *JGR Mach. Learn. Comput.* [doi:10.1029/2025JH000801](https://doi.org/10.1029/2025jh000801). Özet.
- Zhai, P., Huang, Y. (2024). *JGR*. [doi:10.1029/2024JB029719](https://doi.org/10.1029/2024jb029719). Özet.
- Doğrulanamayan künyeler: Rice (1993, JGR, h* formülü); Erickson vd. (2020, SRL, SEAS BP1); Ellsworth & Bulut (2018, Nat. Geosci., İzmit öncüleri); Bradley & Hubbard (2024, Blétery & Nocquet eleştirisi).
