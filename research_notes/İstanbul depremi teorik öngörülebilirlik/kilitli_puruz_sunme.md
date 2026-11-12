# Kilitli pürüzlerin (asperity) sünen fay alanlarında geç-interseismik evrimi: kuram, modelleme ve Ana Marmara Fayı'na uygulanabilirlik (durum: Kasım 2026)

Kapsam notu: Bu notlar yalnız kuram ve sayısal deprem-döngüsü modellemesine dayanır. Gözlemler yalnızca bir kuramsal öngörüyü sınadıkları ya da kalibre ettikleri yerde anılır. 2017 sonrası Marmara GNSS verisi ve 2026 deprem kataloğu kullanılmadı. İstanbul depremi için mutlak olasılık verilmez. Literatür taraması OpenAlex üzerinden yapıldı. Wiley ve OUP tam metinleri 403 döndürdü (aşılmadı), bu yüzden o makalelerdeki sayılar çoğunlukla yalnız özetlerden alındı. Özette olmayan ve tam metinden doğrulanamayan sayılar "doğrulanamadı" diye işaretlendi. Tam metni okunabilen makaleler şunlardır: Zhu et al. 2020 (Nat. Commun.) ve Lange et al. 2019 (Nat. Commun.). "Çıkarım" diye işaretli sayısal tahminler kaynakta yoktur. Bunları kendim temel formüllerle hesapladım (Savage–Burford vida dislokasyonu, Nadeau–Johnson ve Eshelby ölçeklemesi).

Referans parametreler (görevde verilenler): kayma açığı hızı s ≈ 10–20 mm/yıl, kilitlenme derinliği D ≈ 10–15 km. Marmara için kalibrasyon: Prens Adaları segmentinde kayma açığı 10–15 mm/yıl (Ergintav et al. 2014, GRL, doi:10.1002/2014GL060985). InSAR+GPS ile 18,9 ± 7,2 mm/yıl ve D = 12,1 ± 7,0 km bulunmuştur (Diao et al. 2016, GJI, doi:10.1093/gji/ggw048).

---

## 1. Pürüz erozyonu / "kilitli alanın küçülmesi" kuramı: sünme cephesinin ilerleme hızı, gerilme yoğunlaşması, mikrosismisite göçü, yüzey deformasyon hızı değişimi

### Takeaway
Kuram, kilitli pürüzün interseismik dönemde kenarlarından (yanal ve aşağıdan) sünme cephesiyle aşındığını öngörür. Bunu destekleyen mekanizmalar şunlardır:
- thermal pressurization sonrası yavaş gerilme toparlanması,
- yavaş updip sünme yayılması,
- akışkanla sürülen sünme cepheleri.

Kalibre edilmiş ilerleme hızları dalma-batma örneklerinde 30–120 m/yıl (Cascadia) ile on yılda alanın %30–75'inin kaybı (Tohoku) arasındadır. 10–20 mm/yıl'lık doğrultu-atımlı bir fay için 2 yıllık bir pencerede, ±x'teki istasyon çiftinde beklenen yüzey hız değişimi yalnız ~0,1–0,5 mm/yıl'dır. Bu, 2–5 mm/yıl'lık tipik gürültünün çok altındadır. Saptanabilir (>2 mm/yıl) bir sinyal ancak birkaç km'lik (D'nin ≳%30–50'si) kilitlenme kaybında oluşur. Bu da onyıl ölçekli, sürekli ve sistematik hataları iyi denetlenmiş bir zaman serisi gerektirir.

### Cited Findings
- **Mavrommatis, Segall & Johnson (2017)**: Klasik "asperity model" sabit VW (kilitli) ve VS (sünen) bölgeler varsayar. Kuramsal değişiklik şudur: thermal pressurization (TP) VW bölgeyi ve çevresindeki VS bölgenin bir kısmını kapsar. Bu durumda kayma gerilmesi kosismik olarak çok düşük düzeylere iner, interseismik dönemde yavaşça "plaka hızındaki kararlı sürtünme" düzeyine toparlanır, sonra kararlı sünme başlar ve sünme cephesi içeri doğru ilerleyerek kilitli pürüzü aşındırır. Özellikler tekdüze ise kilitli alan VS bölge boyunca zamanla yaklaşık doğrusal küçülür. Küçülme şu durumlarda yavaşlar: VS bölgede nominal sürtünme katsayısı veya efektif normal gerilme yüksekse, hidrolik difüzivite düşükse, TP bölgesi genişse. Yanal heterojenlik doğrusal olmayan erozyon üretir. Tohoku'da 1996–2011 GPS gerinim hızındaki düşüş, kilitli pürüzlerin alanca ~%75 küçülmesiyle uyumludur — [Mavrommatis et al. 2017, JGR Solid Earth, doi:10.1002/2017JB014533](https://doi.org/10.1002/2017JB014533)
- **Mavrommatis et al. (2014)**: Kuramın sınandığı gözlem budur. KD Japonya GPS serilerinde 1996–2011 arasında anlamlı ve uzaysal olarak tutarlı ivmelenmeler bulunur. Güney-orta Tohoku'daki ivmelenme postsismik etkilerle açıklanamaz. Bu ivmelenme, plaka arayüzünde artan kayma hızıyla ve/veya derin asismik kaymanın updip göçüyle açıklanabilir — [Mavrommatis et al. 2014, GRL, doi:10.1002/2014GL060139](https://doi.org/10.1002/2014GL060139)
- **Johnson & Burton (2026)**: En güncel kalibrasyon. Kuzey Japon Hendeği'nde Tohoku öncesi onyıl ölçekli asismik kayma ivmelenmesi, heterojen kilitli pürüzleri aşındıran sünme cephesi yayılımıyla açıklanır. 1998–2009 GNSS ters çözümünde pürüzler tarihsel kırılma alanlarının 1998'de ~%66'sını, 2009'da ~%37'sini kaplıyordu. Küçülme hızları, makul kosismik gerilme düşümleri için kırılma mekaniği öngörüleriyle uyumludur. Model, repeater'lardan kestirilen kayma ivmelenmesini de öngörür — [Johnson & Burton 2026, GRL, doi:10.1029/2026GL125713](https://doi.org/10.1029/2026GL125713)
- **Bruhat & Segall (2017)**: Sünen bölgeyi, alt ucundan plaka hızıyla sürülen yarı-statik bir çatlak olarak ele alır. Zamanla yayılan çatlak için gerilme düşümü, kayma ve kayma hızına analitik ifadeler türetilir. Kayma hızı dağılımı Chebyshev polinomlarıyla açılır. Kuzey Cascadia verisine en iyi uyan modeller fay boyunca 30–120 m/yıl'lık çok yavaş bir updip yayılım verir. Bu, verinin gerektirdiği dik kayma-hızı gradyanını açıklayabilir — [Bruhat & Segall 2017, GJI, doi:10.1093/gji/ggx317](https://doi.org/10.1093/gji/ggx317)
- **Jiang & Lapusta (2017)**: Laboratuvar tabanlı (rate-and-state + güçlü dinamik zayıflama) modellerde kilitli–tam sünen geçişi geniş bir derinlik aralığına yayılabilir. "Effective locking depth" D_elock, yüklemenin yoğunlaştığı ve mikrosismisiteyi besleyen derinliktir; geçiş zonunun tepesindedir. "Geodetic locking depth" D_glock ise uzun dönem hızın yaklaşık yarısıyla sünen derinliğe karşılık gelir. Büyük depremden sonra D_elock ya sabit kalır ya da sünmenin sığdaki kilitli bölgeye sızmasıyla sığlaşır. D_glock ise afterslip'i telafi eden kayma açığı bölgesi genişledikçe derinleşir. Sonuçta iki derinlik geç-interseismik dönemde birbirinden ayrışır. Bu, Güney Kaliforniya'daki birkaç büyük segmentin gözlemleriyle uyumludur. D_glock, modellerde büyük depremlerin derinlik sınırı için bir sınır verir — [Jiang & Lapusta 2017, JGR Solid Earth, doi:10.1002/2017JB014030](https://doi.org/10.1002/2017JB014030)
- **Jiang & Lapusta (2016)**: İnterseismik dönemde sessiz büyük doğrultu-atımlı faylarda sismojenik zonun tabanında yoğunlaşmış mikrosismisite yoktur. Model bunu, önceki büyük depremlerin sismojenik zonun altına derin sızmasının (yükleme yoğunlaşmasını ortadan kaldırmasının) göstergesi olarak yorumlar. 1857 Fort Tejon depremi için sismojenik zonun ≥3–5 km altına sızma çıkarılmıştır — [Jiang & Lapusta 2016, Science, doi:10.1126/science.aaf1496](https://doi.org/10.1126/science.aaf1496)
- **Noda & Lapusta (2013)**: Hız-güçlenmeli ve interseismik dönemde kararlı sünen fay segmentleri, dinamik zayıflama (ör. thermal pressurization) nedeniyle büyük bir kırılmayı geçirebilir ve hatta en büyük kaymayı orada üretebilir. Özet OpenAlex'te yoktu; bu ifade makalenin bilinen başlık-tezine dayanır, sayısal ayrıntıları doğrulanamadı — [Noda & Lapusta 2013, Nature, doi:10.1038/nature11703](https://doi.org/10.1038/nature11703)
- **Hetland & Simons (2010)**: Postsismik ve interseismik sünme ile "interseismic stress shadows" çalışılmıştır. Kilitli pürüzün çevresindeki sünen alanın pürüz tarafından frenlenmesi, geodezik olarak görülen "coupling" alanını kilitli alandan geniş gösterir. Tam metin okunamadı, sayısal sonuçlar doğrulanamadı — [Hetland & Simons 2010, GJI, doi:10.1111/j.1365-246X.2009.04482.x](https://doi.org/10.1111/j.1365-246X.2009.04482.x)
- **Sato, Hori & Fukahata (2025)**: Sürtünmesel kilitlenme ile kinematik coupling'i ayırır. Kilitli bölge "pre-yield", kilitsiz bölge ise gerilmenin dayanıma eşit olduğu, interseismik dönemde sabit gerilmeli yarı-durağan sünme bölgesidir. Coupled bölge her zaman kilitli bölgeden geniştir. Bu fikir, dairesel pürüzlerle çalışan bir "locking inversion" yöntemi olarak önerilmiştir — [Sato et al. 2025, JGR Solid Earth, doi:10.1029/2024JB030357](https://doi.org/10.1029/2024JB030357)
- **Kaneko, Avouac & Lapusta (2010)**: İnterseismik coupling dağılımından deprem örüntülerinin çıkarımı için kuramsal çerçeve sunar. Yarı-kilitli bariyerlerin kırılma geçişini etkilediğini gösterir. Sayısal ayrıntılar doğrulanamadı — [Kaneko et al. 2010, Nature Geoscience, doi:10.1038/ngeo843](https://doi.org/10.1038/ngeo843)
- **Cattania & Segall (2018)**: Kuramsal mekanizmanın küçük ölçekli karşılığıdır. VS fay içindeki küçük VW pürüzlerde interseismik sünme kenardan içeri sızar ve kayma bütçesinin ~%25'ini oluşturur. Depremler merkezden çekirdeklenir — [Cattania & Segall 2018, JGR Solid Earth, doi:10.1029/2018JB016056](https://doi.org/10.1029/2018JB016056)
- **Marmara gözlem kalibrasyonu**: 2007–2012 sismisitesine göre Orta Baseni'nde (Central Basin) GPS'in sığ kilitlenme derinliğinin altında belirgin sismisite, düşük b-değeri ve yüksek ortalama sismik kayma vardır; bu derin sünmeyle uyumludur. Kumburgaz baseni ise kilitli segment işaretleri taşır. Prens Adaları segmentinde sismisite dağılımı 10 km'lik geodezik kilitlenme derinliğiyle uyumludur. Kilitli alanlardan, kırılmanın sünen bölgelere önemli ölçüde girmediği varsayımıyla ~M7,3 kestirilir — [Schmittbuhl et al. 2016a, G-cubed, doi:10.1002/2015GC006120](https://doi.org/10.1002/2015GC006120)

### Inferences
- **Hız ölçeği (çıkarım).** Cascadia değeri 30–120 m/yıl (Bruhat & Segall 2017). Akışkan-valf modelinde 20→13 km/15 yıl ≈ 470 m/yıl'dır (Zhu et al. 2020, bkz. bölüm 5). Tohoku'da ~100 km'lik pürüzler için alanın %66'dan %37'ye düşmesi, uzunluk ölçeğinde yıllık birkaç km düzeyindedir. Bu sonuncusu benim kaba çıkarımımdır; kesin km/yıl değeri özetlerden doğrulanamadı. Dolayısıyla Marmara için makul aralık, aşağı-yukarı yönde 0,03–0,5 km/yıl'dır.
- **Savage–Burford tahmini (çıkarım).** Derinlik değişiminin yüzeydeki etkisi şu formüllerle hesaplandı (kendi hesabım, sonsuz uzun 2B vida dislokasyonu):
  - Hız profili: v(x) = (s/π)·arctan(x/D).
  - ±x'teki istasyon çiftinin fay-paralel bağıl hızı: Δv = (2s/π)·arctan(x/D).
  - s = 15 mm/yıl, D = 12 km, x = 10 km için D'nin azalmasına göre değişim:

| D'deki azalma | Senaryo | Δv değişimi |
|---|---|---|
| 0,3 km | 120 m/yıl × 2,5 yıl | ~0,12 mm/yıl |
| 1,2 km | 120 m/yıl × 10 yıl | ~0,50 mm/yıl |
| 3 km | | ~1,4 mm/yıl |
| 7 km | | ~3,9 mm/yıl |

  - D = 10 km'de bu değerler ~0,15 / 0,6 / 1,7 / 4,7 mm/yıl, D = 15 km'de ~0,09 / 0,37 / 1,0 / 2,9 mm/yıl olur.
  - Sonuç: 2 yılda 2–5 mm/yıl'lık bir değişimin saptanabilmesi, kuramsal hız aralığının 10–50 katı hızlı bir sünme cephesi gerektirir. Kuram, saptanabilir sinyali onyıllık ölçeğe ve birkaç km'lik kilit kaybına yerleştirir.
- **Deniz tabanı akustik ağı (çıkarım).** Fay üzerindeki gerinim hızı ε̇(0) = s/(2πD) ≈ 2×10⁻⁷/yıl'dır (s = 15 mm/yıl, D = 12 km). Lange et al. (2019) ağının gerinim hızı duyarlılığı 1,6×10⁻⁶/yıl'dır. Bu ağ, sığ (≤3–4,5 km) sünmeyi kilitli durumdan ayırabilir; ancak 10–15 km'deki kilitlenme derinliği değişimlerine kuramsal olarak duyarsızdır. Lange et al. 16 km altındaki kaymanın sinyalinin ölçüm belirsizliğiyle karşılaştırılabilir olduğunu kendileri belirtir. Dolayısıyla derin sünme cephesi göçü için deniz tabanı geodezisi değil, kıyı GNSS/InSAR'ın x ≈ 10–20 km bandı en duyarlı geometridir. Bu, İstanbul kıyısının Prens Adaları segmentine uzaklığıyla örtüşür.
- **Yanal erozyon (çıkarım).** Marmara'da batıda sünen Orta Baseni / Batı Yükseltisi, doğuda Prens Adaları'na doğru kilitli segmentler vardır. Bu geometride Mavrommatis/Johnson tipi erozyon yanal sünme cephesi olarak Kumburgaz → doğu yönünde ilerlemelidir. Öngörülen gözlenebilirler iki tanedir. (i) Kilitli–sünen sınırda mikrosismisite ve repeater kümelerinin sınır boyunca göçü; hız birkaç yüz m/yıl'dan birkaç km/yıl'a kadardır (kuramsal aralık; Marmara'ya özgü model yok, doğrulanamadı). (ii) Kıyıda fay-paralel hız profilinin segment kenarlarında yavaş değişimi.
- **Locking depth'te zıt eğilimler.** D_elock (mikrosismisite tabanı) ile D_glock'un geç dönemde ayrışması (Jiang & Lapusta 2017) Marmara için şu anlama gelir: Sismisitenin alt sınırı sığlaşırken geodezik kilit derinliği derinleşebilir. Bu iki ölçütün zaman içinde karşılaştırılması doğrudan bir kuram sınamasıdır.

### Gaps
- Jiang & Lapusta (2017) modellerinde D_elock ile D_glock ayrışmasının km cinsinden büyüklüğü ve zamanlaması tam metne erişilemediği (Wiley 403) için doğrulanamadı.
- Johnson & Burton (2026) çalışmasındaki küçülme hızlarının km/yıl karşılığı ve gerilme düşümü bağımlılığının formülü tam metinden doğrulanamadı.
- Ana Marmara Fayı için kilitli bir Prens Adaları/Kumburgaz pürüzünün batıdaki sünen segmentle etkileşimini simüle eden yayımlanmış bir rate-and-state deprem-döngüsü modeli (SEAS tipi) bulunamadı. Bulunan en yakın çalışma, 2019 Mw 5,8 Silivri depreminin kilitli segment döngüsüne etkisini inceleyen Tectonophysics 2023 makalesidir (doi:10.1016/j.tecto.2023.229888). Özeti okunmadığı için içeriği doğrulanamadı.

---

## 2. Tetikleyici olarak yavaş kayma olayları (SSE): kuram, geç döngü değişimleri, doğrultu-atımlı faylara ve Marmara'ya uygulanabilirlik

### Takeaway
Dalma-batma modelleri, SSE'lerin tekrarlanma aralığının geç-interseismik dönemde kısaldığını öngörür. Aynı modeller SSE'lerin tepe hızının ve toplam kaymasının arttığını, son SSE'nin ise önceki SSE'lerden ayırt edilemeyecek biçimde dinamik kırılmaya dönüşebileceğini öngörür. Bu son durum, kuramın "uyarı vermeyen son olay" tahminidir. Kıtasal doğrultu-atımlı faylarda sığ, sediment kontrollü sünme olayları (Superstition Hills, İsmetpaşa) kuram ve gözlemle desteklenir. Marmara'nın sünen orta/batı kesimleri için kuram SSE'yi mümkün kılar. Ancak Marmara'ya özgü, kilitli segmentle eşleşmiş bir SSE-döngü modeli yayımlanmamıştır.

### Cited Findings
- **Segall & Bradley (2012)**: 2B yarı-dinamik modelde rate-state sürtünme, dilatansi ve eşleşmiş 1B gözenek akışkanı ve ısı taşınımı birlikte çalışır. Kararlı-hal zayıflaması geçici kaymanın çekirdeklenmesine izin verir; dilatant güçlenme bunu bastırır, thermal pressurization ise kararsızlaştırır. SSE'ler düşük efektif gerilmeli VW (LESVW) bölgelerde kendiliğinden doğar. LESVW küçükse SSE'ler updip uçta tuzaklanır ve kilitli zonda güçlü gerilme yoğunlaşması yaratır. Birkaç yüzyıl sonra SSE'ler yüksek efektif gerilmeli bölgeye sızar ve TP sonunda dinamik kırılma üretir. LESVW büyükse SSE'ler zamanla uzar. Her iki durumda **son SSE'nin başlangıcı öncekilerden esasen ayırt edilemez** — [Segall & Bradley 2012, GRL, doi:10.1029/2012GL052811](https://doi.org/10.1029/2012GL052811)
- **Segall et al. (2010)**: Dilatant güçlenme SSE mekanizması olarak önerilir. Membran difüzyonunda yavaş ile hızlı kayma arasındaki sınır ℰ = 1 − a/b'dir; burada ℰ ≡ f₀ε/[βb(σ − p∞)]. ℰ < 1 − a/b ise yeterince büyük faylarda kayma kararsızlığa ivmelenir; ℰ > 1 − a/b ise yarı-statik kalır. Homojen difüzyonda dilatansi etkinliği E_p ≡ εh/[β(σ − p∞)] ile tanımlanır. E_p'nin thermal pressurization etkinliğine oranı 1/(σ − p∞) ile ölçeklenir; yani yüksek gözenek basıncı SSE'yi kayırır — [Segall et al. 2010, JGR, doi:10.1029/2010JB007449](https://doi.org/10.1029/2010JB007449)
- **Matsuzawa et al. (2010)**: Nankai için rate-state (cutoff velocity) modelinde hem kısa hem uzun dönemli SSE'lerin tekrarlanma aralıkları interseismik dönemin geç evrelerinde kısalır. Büyük depremler SSE bölgesi ile kilitli bölge arasında çekirdeklenir — [Matsuzawa et al. 2010, JGR, doi:10.1029/2010JB007566](https://doi.org/10.1029/2010JB007566)
- **Lu & Liu (2026)**: Kosta Rika (2012 Mw 7,6 Nicoya) için deprem+SSE dizisi modeli kuruldu. Model geç döngüde **daha yüksek tepe hızlı ve daha büyük toplam kaymalı SSE'ler** öngörür. Bunun nedeni SSE'ler ile deprem zonu arasındaki karşılıklı gerilme aktarımıdır. SSE özelliklerinin sistematik değişimi uzun dönemli "unlocking" sürecini yansıtabilir — [Lu & Liu 2026, GRL, doi:10.1029/2026GL123904](https://doi.org/10.1029/2026GL123904)
- **Liu & Rice (2007)**: Dalma-batma fay modelinde kendiliğinden ve tetiklenmiş asismik deformasyon geçicileri (SSE) üretilir. Sayısal ayrıntılar bu çalışmada doğrulanmadı — [Liu & Rice 2007, JGR, doi:10.1029/2007JB004930](https://doi.org/10.1029/2007JB004930). Liu & Rice 2005 makalesinin DOI'si OpenAlex'te bu çalışmada aranmadı, doğrulanamadı.
- **Barbot (2019)**: Tek pürüzlü bir rate-state fayda yavaş kayma, yavaş depremler, period-two döngüler, tam ve kısmi kırılmalar ve deterministik kaos aynı modelde ortaya çıkar. Davranış R/h* (pürüz boyutu / çekirdeklenme boyutu) oranıyla düzenlenir. Bu ayrıntı makalenin bilinen içeriğidir; özet okunmadı — [Barbot 2019, Tectonophysics, doi:10.1016/j.tecto.2019.228171](https://doi.org/10.1016/j.tecto.2019.228171)
- **Luo & Liu (2021)**: Fay zonu heterojenlikleri Cascadia'da yavaş depremlerin derinlik-bağımlı örüntüsünü ve evrimini açıklar. Görevde anılan "Luo & Liu 2019" OpenAlex'te bu başlıkla bulunamadı; içeriği doğrulanamadı — [Luo & Liu 2021, Nat. Commun., doi:10.1038/s41467-021-22232-x](https://doi.org/10.1038/s41467-021-22232-x)
- **Wei et al. (2013)**: Kaliforniya'daki epizodik fay sünme olayları sığ sürtünme heterojenliğiyle (sığda VS sediment altında VW katman) denetlenir. Bu, doğrultu-atımlı faylarda sığ SSE için kuramsal temeldir. Özet OpenAlex'te yoktu, ayrıntılar doğrulanamadı — [Wei et al. 2013, Nature Geoscience, doi:10.1038/ngeo1835](https://doi.org/10.1038/ngeo1835). Superstition Hills fayında karakteristik SSE'ler 2024'te ayrıca raporlanmıştır — [GRL 2024, doi:10.1029/2023GL107244](https://doi.org/10.1029/2023GL107244)
- **Rousset et al. (2016)**: KAF İsmetpaşa sünme segmenti (1944 Mw 7,3'ten beri sünüyor; InSAR ortalaması 8 ± 3 mm/yıl, uzun dönem hızın ~1/3'ü). Burada 31 gün süren, maksimum 2 cm kaymalı, yüzey ile 4 km derinlik arasında bir asismik kayma patlaması bulunmuştur. Sünme kararlı hızda değildir — [Rousset et al. 2016, GRL, doi:10.1002/2016GL068250](https://doi.org/10.1002/2016GL068250)
- **Jolivet et al. (2023)**: Aynı bölgede yüzey asismik kayması sığ kilitlenme derinliğiyle çakışır. Dönüş periyodu 2,5 yıl olan SSE'ler belirli bir kesimle sınırlıdır — [Jolivet et al. 2023, JGR Solid Earth, doi:10.1029/2022JB026018](https://doi.org/10.1029/2022JB026018)
- **Tary et al. (2026), Marmara batısı**: 2013 Mw 4,6 depremi öncesinde repeater/creep bölgesinde çok benzer olaylar (multiplet) gözlendi. Bu, kıyı geodezisi ve deniz tabanı gözenek basıncından önerilen, ~0,5 km/gün hızla batıya ilerleyen, aylarca süren bir SSE ile zamanca çakışır. SSE modeli (sağ-yanal kayma + tensil açılma) ana şok konumunda Coulomb gerilmesini yalnız kPa'nın onda biri mertebesinde artırır. Önerilen sıralamaya göre SSE önce multiplet–ana şok dizisini, sonra fay vadisindeki hidrolojik ağı etkilemiştir (gözenek basıncı düşüşleri) — [Tary et al. 2026, GJI, doi:10.1093/gji/ggag429](https://doi.org/10.1093/gji/ggag429)

### Inferences
- **Marmara'ya aktarım (çıkarım, spekülatif).** Doğuda kilitli Prens Adaları/Kumburgaz pürüzü, batıda (Orta Baseni) sünen bir segmentle komşudur. Segall & Bradley mekanizmasının yanal eşdeğerinde, sünen tarafta tekrarlayan SSE'ler kilitli kenarda gerilme yoğunlaştırır. Bu durumda geç döngüde şunlar beklenir: (i) SSE/sünme patlamalarının sıklaşması (Matsuzawa et al. 2010), (ii) SSE'lerin tepe hızının ve kaymasının büyümesi (Lu & Liu 2026), (iii) SSE'lerin kilitli bölgeye doğru sızma mesafesinin artması. Bu öngörülerin hiçbiri Marmara'ya özgü bir modelde nicel olarak hesaplanmamıştır.
- **Uyarı içermeyen son olay.** Segall & Bradley (2012) son SSE'nin öncekilerden ayırt edilemediğini bulmuştur. Bu, SSE izlemenin bir "erken uyarı" değil, en iyi durumda istatistiksel bir döngü-evresi göstergesi olabileceğini gösterir.
- **Marmara SSE'sinin yüzey izi (çıkarım).** Tary et al. (2026) SSE kaynaklı gerilme değişimini ~0,1–0,5 kPa olarak hesaplar. Bu, gelgit gerilmesinden (~kPa) küçüktür. Kuramsal tetikleme etkinliği bu büyüklükte zayıftır.

### Gaps
- Doğrultu-atımlı bir kilitli segment ile yanındaki sünen segmentte SSE tekrarlanma aralığının geç döngüde ne kadar kısaldığını nicelleştiren bir model bulunamadı. Mevcut sayılar dalma-batma bağlamındandır ve tam metinlerden sayısal değer doğrulanamadı.
- Liu & Rice (2005) ve "Luo & Liu (2019)" künyeleri bu çalışmada doğrulanamadı.

---

## 3. Repeater (tekrarlayan deprem) kuramı: creep-meter olarak kullanım, geç döngüde tekrarlanma ivmelenmesi, katalog gereksinimi

### Takeaway
Kuram (Chen & Lapusta 2009; Cattania & Segall 2018), repeater'ları çevredeki sünmeyle yüklenen küçük VW pürüzler olarak açıklar. Tekrarlanma aralığı T_r yükleme hızıyla ters orantılıdır (T_r ∝ 1/v_pl). Bu nedenle sünme cephesi yaklaştıkça veya derin sünme hızlandıkça T_r kısalmalıdır. Pratik ölçüt şudur: sünme hızındaki %20'lik bir artışı ayırt etmek, birkaç dizide yıllar boyunca M ≥ ~2 olayların eksiksiz ve dalga biçimi benzerliğiyle seçilmiş bir kataloğunu gerektirir. Ayrıca slip–moment ölçeklemesinin seçimi mutlak sünme hızını ~10 kat değiştirebilir.

### Cited Findings
- **Chen & Lapusta (2009)**: Büyük bir VS bölgeyle çevrili küçük bir VW yama modeli, gözlenen T_r–M₀ ölçeklemesini laboratuvar rate-state yasalarıyla üretir. VW yamada kaymanın önemli bir kısmı asismik birikir — [Chen & Lapusta 2009, JGR, doi:10.1029/2008JB005749](https://doi.org/10.1029/2008JB005749)
- **Cattania & Segall (2018)**: Gözlenen ölçekleme T_r ∼ M₀^(1/6)'dır; sabit gerilme düşümü ve asismik kaymasız beklenti ise T_r ∼ M₀^(1/3) olurdu. Basit çatlak modelleri M₀^(1/6)'yı üretir. Rejimden bağımsız olarak T_r'nin Δτ, çekirdeklenme uzunluğu ve sünme hızı v_pl ile ölçeklenmesi aynıdır. Bu, repeater'ların creep-meter olarak kullanımını destekler. Özette formülün tam üsleri karakter kaybına uğramıştır, doğrulanamadı — [Cattania & Segall 2018, JGR Solid Earth, doi:10.1029/2018JB016056](https://doi.org/10.1029/2018JB016056)
- **Nadeau & Johnson (1998)**: Parkfield repeater'ları için ampirik kayma–moment ilişkisini verir. Yaygın kullanılan biçim d[cm] = 10^(−2,36) · M₀[dyn·cm]^0,17'dir; bu katsayılar makalenin standart alıntısından alınmıştır, özetten doğrulanamadı — [Nadeau & Johnson 1998, BSSA, doi:10.1785/BSSA0880030790](https://doi.org/10.1785/BSSA0880030790)
- **Uchida & Bürgmann (2019)**: Repeater tespiti ve yavaş kaymanın nitelendirilmesindeki kullanımlarına dair bir derlemedir — [Uchida & Bürgmann 2019, PEPS, doi:10.1186/s40645-019-0284-z](https://doi.org/10.1186/s40645-019-0284-z)
- **Nakajima & Hasegawa (2023)**: Repeater'lar ve repeater olmayan olaylar aynı süreçten doğar: çevredeki kararlı bölgedeki asismik kaymanın yüklediği kilitli pürüzlerin kırılması. Asismik kayma, pürüzü ikiden fazla kez kıracak kadar büyük değilse repeater dizisi oluşmaz — [Nakajima & Hasegawa 2023, JGR Solid Earth, doi:10.1029/2022JB024667](https://doi.org/10.1029/2022JB024667)
- **Johnson & Burton (2026)**: Pürüz erozyonu modeli, Tohoku öncesi repeater'lardan bağımsız olarak kestirilen kayma ivmelenmesiyle tutarlıdır. Bu, kuramın repeater gözlemiyle sınanmış bir örneğidir — [Johnson & Burton 2026, GRL, doi:10.1029/2026GL125713](https://doi.org/10.1029/2026GL125713)
- **Marmara kalibrasyonları:**
  - Orta Baseni'nde 9 uzun ömürlü doğrultu-atımlı repeater dizisi bulunmuştur (2008–2015). Tipik tekrarlanma ~8 aydır. Dizilerin 10 km'lik tek bir pürüzün parçası olduğu varsayılırsa toplam kayma bölgesel geodezik hızla uyumludur. Kısa süreli krizler vardır ve bunlar muhtemelen sünme patlamalarıyla ilişkilidir — [Schmittbuhl et al. 2016b, GRL, doi:10.1002/2016GL070505](https://doi.org/10.1002/2016GL070505)
  - Batı Marmara'da iki M ~2,8 repeater çifti bulunmuştur; bunlar batı kesimin önemli ölçüde asismik deforme olduğunu gösterir — [Bohnhoff et al. 2017, GJI, doi:10.1093/gji/ggx169](https://doi.org/10.1093/gji/ggx169)
  - 2005–2013 döneminde 12 geniş bantlı istasyonla M 2,3–3,2 aralığında 9 dizide 21 repeater bulunmuştur (koherans > 0,95, 40 s). Diziler büyük kırılma sınırlarının yakınındadır — [Uchida et al. 2019, Tectonophysics, doi:10.1016/j.tecto.2019.228185](https://doi.org/10.1016/j.tecto.2019.228185)

### Inferences
- **Ölçekleme seçiminin etkisi (çıkarım, kendi hesabım).** M₀ = 10^(1,5M+9,1) N·m alındı.
  - M 2,8 için Nadeau–Johnson ölçeklemesi d ≈ 12 cm verir. 10 mm/yıl sünmede bu T_r ≈ 12 yıl demektir.
  - Sabit gerilme düşümlü (Δτ = 3 MPa, μ = 30 GPa) Eshelby dairesel çatlağında r ≈ 140 m ve d ≈ 1,0 cm olur; bu da T_r ≈ 1 yıl demektir.
  - Marmara'da gözlenen ~8 aylık T_r (Schmittbuhl et al. 2016b) ikinci ölçeklemeyle daha uyumludur. Ölçekleme seçimi, sünme hızı kestirimini ~10 kat değiştirir. Bu nedenle mutlak hızlar değil, **göreli değişimler** (ΔT_r/T_r = −Δv/v) kuramsal sınama için kullanılmalıdır.
- **Geç döngü öngörüsü (çıkarım).** Kilitli–sünen sınırın yakınındaki repeater'larda iki şey beklenir: (a) sünme cephesi pürüze yaklaştıkça yerel yükleme hızı arttığı için T_r kısalır; (b) cephe pürüzü geçip onu yuttuğunda dizi kesilebilir (pürüz tamamen sünen alana kalır ya da Cattania & Segall rejimine göre kısmi kırılmalara geçer). Johnson & Burton (2026) Tohoku için bunun onyıl ölçekli ivmelenme olarak gözlendiğini ve modelle tutarlı olduğunu raporlar.
- **Katalog gereksinimi (çıkarım, basit istatistik).** Tek bir dizide T_r'nin değişim katsayısı CoV ≈ 0,3 kabul edildi (doğrulanmamış varsayım). Bu durumda %20'lik bir hız değişimini 2σ ile ayırt etmek pencere başına ~(2·0,3/0,2)² ≈ 9 olay gerektirir. Karşılaştırılacak iki pencere için ≥18 olay gerekir. 9 dizi ve T_r ≈ 0,7–1 yıl ile bu ~2–4 yıllık kesintisiz veri demektir. Ek koşullar: M ≥ ~2 olaylar için tam katalog; aynı istasyon ve geometri (koherans tabanlı seçim istasyon değişikliklerine hassastır); en az 100 Hz dalga biçimi arşivi.

### Gaps
- Beeler et al. (2001) repeater modelinin künyesi OpenAlex'te doğrulanamadı; yalnız Beeler ekibinin 2018 Parkfield yüksek gerilme-düşümü modeli bulundu (JGR 2018, doi:10.1029/2018JB016472).
- Cattania & Segall (2018) genel ölçekleme formülünün tam üsleri doğrulanamadı.

---

## 4. Derinliğe bağlı sürtünme kuramı: sismojenik derinlik sınırları, döngü boyunca derin sünme evrimi, viskoelastik döngüler, kilitlenme derinliğinin zaman evrimi ve derin mikrosismisite "streak"leri

### Takeaway
Rate-and-state modelleri (Lapusta et al. 2000 temelinde), büyük depremden sonra derin sünmenin hızlanıp (afterslip) döngü boyunca yavaşladığını öngörür. D_glock ve D_elock bu süreçte zıt yönlerde evrilir. Güç-yasası viskoelastik (Allison & Dunham 2018) ve hasar zonu/plastisite içeren modeller, kilitlenme derinliğinin geç döngüde yavaş değiştiğini ancak modelden modele değiştiğini gösterir. Dayanıklı ve modelden bağımsız bir "geç döngü derinlik sinyali" yoktur. En dayanıklı öngörü şudur: büyük depremlerin derinliğe sızdığı faylarda sismojenik tabanda mikrosismisite yoğunlaşması beklenmez.

### Cited Findings
- **Lapusta et al. (2000)**: Yavaş tektonik yükleme ve kendiliğinden kırılma epizotları için rate-state elastodinamik yöntemin temel makalesidir. Derinliğe bağlı a−b ile doğrultu-atımlı fay döngüleri üretir — [Lapusta et al. 2000, JGR, doi:10.1029/2000JB900250](https://doi.org/10.1029/2000JB900250)
- **Jiang & Lapusta (2017)**: D_elock ile D_glock'un geç dönemde ayrışması ve D_glock'un büyük depremlerin derinlik sınırına bir sınır vermesi (bkz. bölüm 1). Katmanlı sürtünme ve basit derinlik kestirimleri, belirgin doğrultu-boyu değişimi olan faylar için yetersizdir — [Jiang & Lapusta 2017, JGR Solid Earth, doi:10.1002/2017JB014030](https://doi.org/10.1002/2017JB014030)
- **Lambert & Lapusta (2021)**: Sünen bir bariyerle ayrılmış iki eş-düzlemli segmentli 2B kıtasal fay modelidir. Ataletin basitleştirilmesi ve büyük hücreler sonuçları önemli ölçüde değiştirir. Statik gerilme düşümü gibi bazı çıktılar yeterli çözünürlükte modeller arasında benzerdir. İki-segment kırılma oranı ise sayısal işlem ve varsayımlara çok hassastır. Bu, Marmara'nın sünen bariyerle ayrılmış segmentleri için doğrudan ilgilidir — [Lambert & Lapusta 2021, JGR Solid Earth, doi:10.1029/2021JB022193](https://doi.org/10.1029/2021JB022193)
- **Allison & Dunham (2018)**: Rate-state sürtünme ve güç-yasası viskoelastisiteyle (sıcaklığa bağlı) doğrultu-atımlı deprem döngüsü simülasyonları. Özet OpenAlex'te yok; bu tez makalenin bilinen içeriğidir. Viskoelastik akışın kosismik olarak gevrek–sünek geçişe gerilme yüklediği ve sismojenik derinliğin döngü içinde etkilenebildiği, makalenin bilinen sonuçlarıdır; nicel değerler doğrulanamadı — [Allison & Dunham 2018, Tectonophysics, doi:10.1016/j.tecto.2017.10.021](https://doi.org/10.1016/j.tecto.2017.10.021)
- **Lambert & Barbot (2016)**: Litosfer–astenosfer sisteminde viskoelastik akışın deprem döngüsüne katkısı. Yalnız başlık ve atıf bilgisi görüldü, ayrıntılar doğrulanamadı — [GRL 2016, doi:10.1002/2016GL070345](https://doi.org/10.1002/2016GL070345)
- **Jiang & Lapusta (2016)**: Büyük depremler sismojenik zonun altına sızdığında, interseismik dönemde sismojenik tabanda yoğunlaşmış mikrosismisite görülmez. Sızma yoksa sismojenik tabanda sürekli küçük depremler beklenir — [Jiang & Lapusta 2016, Science, doi:10.1126/science.aaf1496](https://doi.org/10.1126/science.aaf1496)
- **Kuramın Marmara'da sınanması**: Lange et al. (2019), Kumburgaz/merkez kesiminde OBS ile 17 ayda yalnız 45 olay (M_L 1,4–4,2; 9–25 km derinlik) saptamıştır. Bu olaylar geodezik deney alanının yakınında değildir. Yazarlar bunu, sığda kilitli ve derinde sünen bir modelle bağdaşmaz bulur, çünkü o durumda kilitli–sünen geçişte sismisite odaklanırdı (Prens Adaları segmentinde olduğu gibi). Bu çıkarım, Jiang & Lapusta (2016) mantığının Marmara'daki karşılığıdır — [Lange et al. 2019, Nat. Commun., doi:10.1038/s41467-019-11016-z](https://doi.org/10.1038/s41467-019-11016-z)

### Inferences
- **Marmara'da segmentler arası fark (çıkarım).** Jiang & Lapusta (2016) çerçevesinde Prens Adaları segmentinde ~10 km'deki sismisite yoğunlaşması (Schmittbuhl et al. 2016a) iki şekilde yorumlanabilir: (a) son büyük olayın (1766/1894?) derin sızmadığının, (b) derin sünmenin halen sismojenik tabanı yüklediğinin göstergesi. Kumburgaz'ın sessizliği ise derin sızma geçmişini ya da tamamen kilitli bir derinlik profilini ima eder. Bu, aynı fay boyunca farklı "geç döngü" durumlarının kuramsal olarak ayırt edilebileceğini gösterir. Spekülatif: tarihsel olayların derinlikleri bilinmiyor.
- **Derin sünme hızı ve kilitlenme derinliği evrimi (çıkarım).** Büyük olaydan 250+ yıl sonra (Kumburgaz/merkez, 1766?) derin sünme hızı modellerde plaka hızına asimptotik yaklaşmış olmalıdır. Bu durumda yıllık D değişimi yalnız sünme cephesi göçüyle sınırlıdır (bölüm 1'deki 0,03–0,5 km/yıl) ve yüzey sinyali onyılda ≤1–4 mm/yıl'dır. Prens Adaları segmenti 1999 İzmit depreminin hemen batısındadır. Bu segment için postsismik viskoelastik relaksasyon (güç-yasası) onyıllarca ek, zamana bağlı bir hız alanı üretir. Bu alan, geç döngü kilit kaybı sinyalinden ayrılmadan yorumlanamaz.
- **Mikrosismisite "streak"leri.** Bunlar kuramda kilitli–sünen sınırda yükleme yoğunlaşmasıyla açıklanır. Geç döngüde D_elock sığlaşırsa streak'lerin derinliğinin yavaşça sığlaşması beklenir. Büyüklüğü, D_elock'un döngüdeki değişimiyle sınırlıdır; Jiang & Lapusta (2017) ölçeğinde birkaç km/döngü olabilir (doğrulanamadı). Bu, yıllar ölçeğinde konum belirsizliğinin (~0,5–1 km) altında kalır.

### Gaps
- Allison & Dunham (2018) ve Jiang & Lapusta (2017) çalışmalarının geç döngü derinlik değişim hızlarının nicel değerleri doğrulanamadı (paywall/özet eksik).
- Marmara'nın sıcaklık yapısı ve güç-yasası reolojisiyle kalibre edilmiş bir döngü modeli bulunamadı.

---

## 5. Akışkanlar: dilatant güçlenme, thermal pressurization, fault-valve döngüleri, akışkanla sürülen asismik kayma cepheleri, yıl ölçekli kırılma-öncesi zaman ölçeği ve gaz/sızıntı değişimi

### Takeaway
Akışkanlı modeller, geç-interseismik dönemde yıl–onyıl ölçekli üç süreç öngörür. (1) Fault-valve: sızdırmazlaşma (sealing) ile aşırı basınç birikir ve aşırı basınç cephesiyle eşleşmiş bir asismik kayma cephesi yukarı göç eder; örnek modelde 20→13 km/15 yıl, ardından sürü (swarm) sismisitesi ve büyük kırılma gelir. (2) Dilatant güçlenme, kaymanın yavaş mı hızlı mı olacağını ℰ ≶ 1 − a/b ölçütüyle belirler. (3) Akışkanla sürülen sürtünme kırılmaları basınç cephesini λ katsayısıyla geçer. Yıl ölçekli zaman ölçeği vardır, ancak modelden bağımsız değildir. T (iyileşme/sızdırmazlaşma zaman ölçeği) ile döngü süresi oranına güçlü biçimde bağlıdır. Gaz/sızıntı emisyonlarının değişmesi için doğrudan kuramsal bir model bulunamadı; bağlantı spekülatiftir.

### Cited Findings
- **Zhu, Allison, Dunham & Yang (2020)**: 2B antiplane doğrultu-atımlı modelde rate-state sürtünme, permeabl fay zonunda yukarı Darcy akışı ve permeabilite evrimi birlikte çalışır.
  - Parametreler: σ* = 30 MPa, k_min = 10⁻¹⁹ m², k_max = 10⁻¹⁵ m², L = 1 m, T = 3,17 yıl, q₀ = 3×10⁻⁹ m/s.
  - Faz 1: depremden sonra yüksek permeabiliteli sismojenik zon boşalır ve efektif gerilme artar.
  - Faz 2: iyileşme/sızdırmazlaşma permeabiliteyi düşürdükten 5–10 yıl sonra başlar. Derinden gelen akışkan aşırı basınç yaratır ve **20 km'den 13 km'ye 15 yılda göç eden akışkanla sürülen bir asismik kayma cephesi** başlar. Cephe VW zonuna girince 13–18 km'yi kıran küçük bir deprem çekirdeklenir.
  - Faz 3: cephe ~10 yılda 8 km'de durur. İkinci bir aşırı basınç/kayma cephesi 20 km'den yükselir ve 8–19 km'yi kıran daha büyük bir deprem doğar.
  - Faz 4: yükselen basınç darbesini izleyen sürü-benzeri sismisite gelir ve yüzeyi kıran büyük bir kırılmayla sonuçlanır.
  - Geodezik görünüm, plaka coupling'inin kademeli azalması ya da kilitlenme derinliğinin sığlaşmasıdır; ancak ters çözüm ödünleşimleri bunu çözmeyi zorlaştırabilir.
  - Maksimum akı sonrası basınç düşüm hızı ~10 MPa/yıl, aşırı basınç ölçeği ~10 MPa'dır.
  - T, deprem tekrarlanma aralığıyla karşılaştırılabilir ya da ondan büyükse (31,7 ve 317 yıl) valf davranışı azalır veya ihmal edilebilir olur. T = 0,317 yıl ~1 yıl süren, birkaç yılda bir tekrarlayan, birkaç cm kaymalı yarı-periyodik kayma olayları üretir.
  - Yazarlar Cascadia'daki 30–120 m/yıl updip göçü kendi örneklerine "çok da benzemeyen değil" diye karşılaştırır.
  - Kaynak: [Zhu et al. 2020, Nat. Commun., doi:10.1038/s41467-020-18598-z](https://doi.org/10.1038/s41467-020-18598-z), tam metin okundu.
- **Segall & Rice (1995)**: Akışkan-sızmış bir fayda dilatansi, kompaksiyon ve kayma kararsızlığı. Dilatansi kaymayı stabilize eder (dilatant güçlenme) — [Segall & Rice 1995, JGR, doi:10.1029/95JB02403](https://doi.org/10.1029/95JB02403)
- **Rice (2006)**: Deprem kayması sırasında ısınma ve zayıflama (thermal pressurization, flash heating) — [Rice 2006, JGR, doi:10.1029/2005JB004006](https://doi.org/10.1029/2005JB004006)
- **Segall et al. (2010)**: ℰ ölçütü ve E_p tanımı (bkz. bölüm 2) — [doi:10.1029/2010JB007449](https://doi.org/10.1029/2010JB007449)
- **Chen (2023)**: Mikrofiziksel (gözeneklilik durum değişkenli) sürtünme modelinde dilatant ve geçirimsiz faylar bile potansiyel olarak sismojeniktir (pozitif kritik frekans). Elastik ortamda kritik dalga boyu onlarca km olabilir. Dört tip periyodik yavaş kayma döngüsü ortaya çıkar — [Chen 2023, JGR Solid Earth, doi:10.1029/2022JB024382](https://doi.org/10.1029/2022JB024382)
- **Bhattacharya & Viesca (2019)**: Akışkanla aktive edilen asismik kayma cephesi, basınçlı gözenek akışkanının difüzyonundan daha hızlı ve uzağa yayılır. Kayma zayıflamalı sürtünme × yerel efektif normal gerilme dayanımı vardır. Bu kuram saha enjeksiyon deneyleriyle sınanmıştır — [Bhattacharya & Viesca 2019, Science, doi:10.1126/science.aaw7354](https://doi.org/10.1126/science.aaw7354)
- **Sáez, Lecampion, Bhattacharya & Viesca (2022)**: Sabit hacim hızlı enjeksiyonda 3B akışkanla sürülen kararlı sürtünme kırılması kendine benzer büyür. Kırılma yarıçapı R(t) = λ·L(t)'dir; burada L(t) basınç cephesinin nominal konumu, λ ise tek bir boyutsuz parametre T'nin bilinen fonksiyonudur. T, ortam koşullarında kırılmaya uzaklığın enjeksiyon gücüne oranıdır. λ > 1 ise kayma cephesi basınç cephesini geçer. Kritik gerilmeli faylarda λ ≫ 1 ve T ≪ 1'dir — [Sáez et al. 2022, JMPS, doi:10.1016/j.jmps.2021.104754](https://doi.org/10.1016/j.jmps.2021.104754). Difüzif yayılım L(t) ∝ √(4αt) biçimindedir; bu standart difüzyon ölçeğidir (çıkarım).
- **Mavrommatis et al. (2017)**: TP bölgesi büyüdükçe ve hidrolik difüzivite düştükçe pürüz erozyonu yavaşlar; akışkan parametreleri erozyon hızını denetler — [doi:10.1002/2017JB014533](https://doi.org/10.1002/2017JB014533)
- **Marmara gaz ve sızıntı gözlemleri (yalnız bağlam)**:
  - Marmara'da gaz emisyonları aktif tektonikle uzaysal olarak ilişkilidir — [Géli et al. 2008, EPSL, doi:10.1016/j.epsl.2008.06.047](https://doi.org/10.1016/j.epsl.2008.06.047)
  - Emisyonları birden çok gaz rezervuarı besler — [Deep-Sea Res. II 2017, doi:10.1016/j.dsr2.2017.11.011](https://doi.org/10.1016/j.dsr2.2017.11.011)
  - Önerilen SSE ile fay vadisindeki gözenek basıncı düşüşlerinin zamanlaması uyumludur — [Tary et al. 2026, doi:10.1093/gji/ggag429](https://doi.org/10.1093/gji/ggag429)
  - Lange et al. (2019), denizaltı faylarda yukarı göç eden yüksek gaz miktarının farklı davranışa yol açabileceğini not eder — [doi:10.1038/s41467-019-11016-z](https://doi.org/10.1038/s41467-019-11016-z)

### Inferences
- **Yıl ölçekli zaman ölçeği (çıkarım).** Zhu et al. (2020) kuramında son büyük kırılmadan önce, onyıllar süren yukarı doğru asismik kayma ve basınç cephesi göçü ile ardından gelen aylar–yıllar ölçekli sürü sismisitesi vardır (Faz 4 göç hızı şekilde 0,2 yıl aralıklarla çizilmiştir). Bu, kuramda **yıl ölçekli bir öncü** olarak var olan tek mekanizmadır. Ancak yalnız T ≪ döngü süresi rejiminde ortaya çıkar. Marmara'da T ve k değerleri bilinmiyor.
- **Spekülatif bağlantı — gaz/sızıntı.** Kuramda (i) asismik kayma permeabiliteyi artırır ve (ii) aşırı basınç cephesi yükselir (Zhu et al. 2020). Bu bir akı artışı ima eder: Darcy akısı q = −(k/η)∇p, ve k kaymayla k_max'a doğru artar. Bu nedenle geç döngüde sığ sızıntılarda akı artışı ve kimyasal değişim *beklenebilir*. Ancak (a) sığ sediment gaz rezervuarları derin fay sıvısından büyük ölçüde bağımsızdır, (b) Zhu modeli 2B ve derin kaynaklıdır, (c) sızıntı akısını fay gerilmesine bağlayan doğrulanmış bir model bulunamadı. Bu bağlantı yalnız hipotezdir.
- **Dilatansi ve Marmara.** Segall et al. (2010) ölçütüne göre yüksek gözenek basıncı (düşük σ − p∞) SSE'yi kayırır. Marmara'nın gazlı sedimentleri sığda düşük efektif gerilme yaratıyorsa, sığ kesimde SSE ve sünme patlamaları kuramsal olarak beklenir. Derin kilitli pürüzün davranışını ise bu belirlemez.

### Gaps
- Marmara fay zonu için hidrolik difüzivite, permeabilite ve sealing zaman ölçeği T'nin kuram-uyumlu kestirimleri bulunamadı.
- Gaz emisyonu ile fay mekaniğini eşleştiren kuramsal veya sayısal bir model bulunamadı.

---

## 6. SCEC SEAS kıyaslama sonuçları: geç-interseismik davranışın modelden bağımsız dayanıklı özellikleri

### Takeaway
SEAS kod-doğrulama alıştırmaları (BP1–BP7, 2B/3B, dinamik ve eğimli faylar), yeterli çözünürlükte kodların uzun dönem deprem dizilerinde, interseismik sünme profillerinde ve tekrarlanma aralıklarında uyuştuğunu gösterir. Ancak ince ayrıntılar (dizi zamanlaması, iki-segment kırılma oranı) çözünürlük ve atalet işlemine hassastır. Dayanıklı özellikler şunlardır: VS bölgeden kilitli bölgeye sünme sızması, kilit sınırında gerilme yoğunlaşması, sünme hızının döngü boyunca evrimi ve çekirdeklenmenin kilitli–sünen sınıra yakın olması. Kesin zamanlama ve dizi detayı dayanıklı değildir.

### Cited Findings
- **Erickson et al. (2020)**: SEAS topluluk kod doğrulama alıştırmasıdır; 2B antiplane doğrultu-atımlı (BP1) kıyaslamaları içerir. Özet okunmadı, sayısal sonuçlar doğrulanamadı — [Erickson et al. 2020, SRL, doi:10.1785/0220190248](https://doi.org/10.1785/0220190248)
- **Jiang et al. (2022)**: 3B dinamik deprem dizisi ve asismik kayma modellerinin topluluk kod karşılaştırmasıdır. Özet okunmadı — [Jiang et al. 2022, JGR Solid Earth, doi:10.1029/2021JB023519](https://doi.org/10.1029/2021JB023519)
- **Erickson et al. (2023)**: Tam elastodinamik etkiler ve eğimli fay geometrileri SEAS alıştırmalarına eklenmiştir. Özet okunmadı — [Erickson et al. 2023, BSSA, doi:10.1785/0120220066](https://doi.org/10.1785/0120220066)
- **Lambert & Lapusta (2021)**: Ataletin basitleştirilmesi ve büyük hücreler dizileri önemli ölçüde değiştirir. Statik gerilme düşümü dayanıklıdır, iki-segment kırılma oranı hassastır. Yeterince uzun faylarda iyi çözünürlüklü simülasyonlar bile uzun dönem dizilerde farklılaşabilir — [doi:10.1029/2021JB022193](https://doi.org/10.1029/2021JB022193)
- SEAS'ın akışkan ve fay zonu etkilerine dair 2025 alıştırmaları yalnız konferans özeti olarak görüldü — [EGU25-14426, doi:10.5194/egusphere-egu25-14426](https://doi.org/10.5194/egusphere-egu25-14426)

### Inferences
- **Marmara uygulaması (çıkarım).** Lambert & Lapusta (2021) "sünen bariyerle ayrılmış iki segment" geometrisini inceler ve bu geometri Marmara'nın Orta Baseni / Kumburgaz / Prens Adaları dizilimine benzer. Bu çalışmaya göre segmentlerin birlikte mi ayrı mı kırılacağı model ayrıntılarına çok hassastır. Dolayısıyla kuram, sünen orta segmentin bir bariyer mi yoksa Noda & Lapusta (2013) tipi geçirgen bir segment mi olduğunu dayanıklı biçimde öngöremez.
- Geç döngü öngörülerinin "modelden bağımsız" olarak kabul edilebilecek kısmı nitelikseldir: sünme sızması, sınırdaki gerilme yoğunlaşması ve yükleme hızının artması. Bölüm 1–3'teki nicel değerler modele özgüdür.

### Gaps
- SEAS makalelerinin tam metinleri ve özetleri okunamadı. Kıyaslamalar arası uyum metrikleri (ör. tekrarlanma aralığı farkları) doğrulanamadı.

---

## 7. Her geç döngü sinyali için beklenen genlik (s ≈ 10–20 mm/yıl, D ≈ 10–15 km) ve gereken minimum duyarlılık ve zaman aralığı

### Takeaway
Kuramın öngördüğü geç döngü sinyallerinin neredeyse tamamı yıllık geodezik gürültünün altındadır. En duyarlı geometri, faydan x ≈ 10–20 km uzaklıktaki kıyı GNSS/InSAR çiftleridir. Bu geometride birkaç km'lik kilit kaybı onyılda ~1–4 mm/yıl üretir. Repeater tekrarlanma oranları ve mikrosismisite derinlik dağılımı göreli değişimleri daha iyi çözebilir, ama ancak homojen ve uzun kataloglarla. Deniz tabanı akustik ağları sığ sünmeyi ayırt eder; derin kilit değişimlerine duyarsızdır.

### Cited Findings
- Lange et al. (2019) deniz tabanı akustik ağının duyarlılıkları şunlardır: uzun dönem baz çözünürlüğü 8 mm'den iyidir; gerinim hızı duyarlılığı 1,6×10⁻⁶/yıl'dır ve 0,8 mm/yıl'lık kaymaya karşılık gelir. Ölçülen doğrultu-atım hızı 0,80 ± 1,25 mm/yıl'dır (2,5 yıl). Kilitlenme yüzeyden en az 3 km'ye kadar sürer. 16 km'nin altındaki kayma belirsizlikle karşılaştırılabilir sinyal verir — [Lange et al. 2019, doi:10.1038/s41467-019-11016-z](https://doi.org/10.1038/s41467-019-11016-z)
- 6 aylık akustik ölçüm, yüzey sünmesinin < 6 mm/yıl olduğunu gösterir (uzak alan > 20 mm/yıl) — [Sakic et al. 2016, GRL, doi:10.1002/2016GL069600](https://doi.org/10.1002/2016GL069600)
- Kıyı GPS'iyle Marmara sünen segmentlerinin model belirsizlikleri büyüktür; ağ optimizasyonu önerilmiştir — [Klein et al. 2017, GRL, doi:10.1002/2017GL072777](https://doi.org/10.1002/2017GL072777)

### Inferences
Genlik tablosu (kendi hesabım; 2B Savage–Burford ve basit ölçeklemeler; s = 15 mm/yıl, D = 12 km merkez değerleri):

| Sinyal | Kuramsal hız/değişim | 2 yılda beklenen genlik | 10–20 yılda beklenen genlik | Gerekli duyarlılık |
|---|---|---|---|---|
| Updip derin sünme cephesi (D azalması) | 0,03–0,5 km/yıl | ΔD = 0,06–1 km → Δv(±10 km) ≈ 0,02–0,4 mm/yıl | ΔD = 0,3–7 km → 0,1–3,9 mm/yıl | ~0,3 mm/yıl hız belirsizliği; ≥10 yıl sürekli GNSS |
| Yanal pürüz erozyonu (alanın %30–75'i/onyıl, dalma-batma kalibrasyonu) | km/yıl mertebesi (doğrulanamadı) | segment ucundaki istasyonlarda ≤1 mm/yıl (çıkarım) | birkaç mm/yıl | 3B ters çözüm; deniz tabanı + kıyı |
| Fay üstü gerinim hızı (deniz tabanı) | ε̇ = s/(2πD) ≈ 1,6–4,8×10⁻⁷/yıl | D'de %10 değişim → ~2×10⁻⁸/yıl | ~10⁻⁷/yıl | Mevcut 1,6×10⁻⁶/yıl'dan 10–100 kat iyi |
| Repeater T_r kısalması | ΔT_r/T_r = −Δv/v | %10–20 ancak cephe yakınsa | %20–100 | Tam M ≥ 2 katalog; ≥18 olay/pencere |
| D_elock sığlaşması (mikrosismisite tabanı) | ≤ birkaç km/döngü (doğrulanamadı) | < 0,1 km | ~0,5–1 km (?) | 3B yeniden konumlama ±0,5 km; OBS |
| Akışkan-valf kayma cephesi | ~0,5 km/yıl (Zhu et al. örneği) | ~1 km → ~0,4 mm/yıl | 7 km/15 yıl → ~4 mm/yıl | GNSS + derin sürü sismisitesi + basınç |
| SSE sıklığı ve büyüklüğü | geç döngüde artar (nicel değer yok) | — | — | Sürekli InSAR/GNSS/deniz tabanı basınç |

- Hesap için 2B formüller kullanıldı. Sonlu segment uzunluğu L ≈ 30–50 km sinyali L/D oranına bağlı olarak azaltır (çıkarım). 2–5 mm/yıl/2 yıl'lık gürültü eşiğinin üzerine çıkan kuramsal senaryo yalnız "hızlı" uç örneklerdir: birkaç km/yıl yanal erozyon ya da ~0,5 km/yıl akışkan-valf cephesinin onyıllık birikimi.
- **Marmara geometrisi.** Prens Adaları segmenti kıyıya ~10–20 km uzaklıktadır. Bu, Δv'nin maksimuma yakın olduğu bant olduğu için kuramsal olarak avantajdır. Ancak fayın güney tarafı denizde ve uzaktadır. Simetrik ±x çifti kurulamaz; tek taraflı ölçüm D–s ödünleşimini artırır (Diao et al. 2016'da D = 12,1 ± 7,0 km).

### Gaps
- Sonlu uzunluklu 3B pürüz erozyonu için Marmara geometrisinde ileri modelleme yapılmadı; bu tablo 2B üst-sınır tahminidir.
- GNSS gürültü modelleri (renkli gürültü, ≥10 yıllık hız belirsizliği) bu notların kapsamı dışında kaldı ve doğrulanmadı.

---

## 8. Sınanabilir kuramsal öngörüler

### Takeaway
Aşağıdaki tablo, kuramın Marmara için ürettiği somut ve sınanabilir öngörüleri, gereken veriyi ve sınanabilirlik durumunu listeler. Önemli kısıt: 2017 sonrası Marmara GNSS verisi ve 2026 kataloğu bu çalışmada kullanılmadı. "0 € ile şimdi sınanabilir" ifadesi açık verinin mevcut olduğunu belirtir; sınamanın kendisi yapılmamıştır.

### Cited Findings
- Tablo, yukarıdaki bölümlerde kaynakları verilen kuramlardan türetilmiştir: Mavrommatis et al. 2017; Johnson & Burton 2026; Bruhat & Segall 2017; Jiang & Lapusta 2016/2017; Segall & Bradley 2012; Matsuzawa et al. 2010; Lu & Liu 2026; Chen & Lapusta 2009; Cattania & Segall 2018; Zhu et al. 2020; Sáez et al. 2022; Lange et al. 2019.

### Inferences

| # | Gözlenebilir | Öngörülen büyüklük | Zaman ölçeği | Gerekli veri | Açık veri var mı? | Durum |
|---|---|---|---|---|---|---|
| 1 | Kıyı GNSS'te Prens Adaları'na dik profilde fay-paralel hız gradyanının zamanla değişimi (D_glock'un evrimi) | Onyılda ~0,1–4 mm/yıl (x ≈ 10–20 km); 2 yılda < 0,5 mm/yıl | 10–20 yıl | ≥10 yıllık sürekli GNSS (her iki yakada ideal); 1999 postsismik relaksasyon modeli | Kısmen: yayımlanmış hız alanları (Ergintav et al. 2014 vb.) ve açık IGS/EUREF istasyonları var; yoğun yerel ağ verisi kısıtlı (doğrulanamadı) | Kısmen 0 € ile (kaba); güçlü sınama için yeni/sürekli veri gerekir |
| 2 | Sentinel-1 InSAR ile kıyıda hız alanının dönemler arası farkı | ~1 mm/yıl düzeyi (onyıllık) | ≥2 bağımsız 5–6 yıllık pencere | Sentinel-1 (2014–), atmosfer ve referans düzeltmeleri | Evet (Copernicus açık; ancak 2017 sonrası Marmara verisi bu görevde yasak) | 0 € ile teknik olarak mümkün; bu çalışmada yapılmadı |
| 3 | Repeater T_r'nin kilitli–sünen sınıra (Orta Baseni→Kumburgaz) yakınlıkla kısalması ve zamanla ivmelenmesi | ΔT_r/T_r = −Δv/v; cephe yakınsa onyılda %20–100 | 5–15 yıl | Homojen dalga biçimi arşivi (KOERI/AFAD/GONAF), M ≥ 2 tam katalog, ≥18 olay/pencere | Kısmen: yayımlanmış repeater listeleri (2005–2015); ham dalga biçimi erişimi kısmi (doğrulanamadı) | 2017 öncesi için 0 € ile kısmen; geç döngü sınaması yeni/sürekli veri gerektirir |
| 4 | Repeater dizilerinin kilitli bölge içine doğru göçü ya da kesilmesi (pürüzün yutulması) | Sınır boyunca 0,03–birkaç km/yıl göç | Onyıl | Yeniden konumlanmış (çift fark) uzun katalog | Kısmen (Schmittbuhl et al. 2016b ve Uchida et al. 2019 yayımlanmış dizileri) | Yeni veri gerekir |
| 5 | D_elock (mikrosismisite tabanı) ile D_glock ayrışması: D_elock sığ ya da sabit, D_glock derinleşen | Birkaç km/döngü; yıllık < 0,1 km | Onyıllar | 3B hassas konumlama + OBS; GNSS ters çözümü | Kısmen (2007–2012 relokasyonlar yayımlanmış) | Yıllık değişim için sınanamaz; segmentler arası uzaysal karşılaştırma 0 € ile mümkün |
| 6 | Kumburgaz'ın kilitli–sünen sınırındaki sismisite sessizliği (Jiang & Lapusta 2016 ölçütü) | İkili: tabanda yoğunlaşma var/yok | Statik | OBS + kara ağı katalogları | Kısmen (Lange et al. 2019; Schmittbuhl et al. 2016a) | 0 € ile literatür düzeyinde sınanabilir (yapıldı: Lange et al. 2019 sessizliği raporlar) |
| 7 | Batı/orta Marmara'da sünme patlamaları ve SSE'lerin sıklaşması, büyümesi (Matsuzawa / Lu & Liu öngörüsü) | Tekrarlanma kısalması ve tepe hızı artışı (nicel değer yok) | Döngü ölçeği (yüzyıllar); yıllık değişim çok küçük | Sürekli deniz tabanı geodezisi, gözenek basıncı, InSAR | Hayır (deniz tabanı verileri büyük ölçüde açık değil, doğrulanamadı) | Yeni veri gerekir; tek döngüde pratikte sınanamaz |
| 8 | Son SSE'nin öncekilerden ayırt edilememesi (Segall & Bradley 2012) | — | — | — | — | Sınanamaz (kırılma sonrasına kadar) |
| 9 | Akışkan-valf modelinde yukarı göç eden asismik kayma ve sürü sismisitesi | ~0,5 km/yıl cephe; aylar–yıllar süren derin→sığ sürü göçü | Yıl–onyıl | Derin sismisite göç analizi + GNSS + akışkan basıncı | Kısmen (katalog); gözenek basıncı yok | Yeni veri gerekir |
| 10 | Deniz tabanı akustik baz değişimlerinde derin kilit kaybı | ε̇ değişimi ~10⁻⁸–10⁻⁷/yıl | Onyıl | 10–100 kat iyileştirilmiş akustik ağ duyarlılığı | Hayır | Mevcut teknolojiyle sınanamaz (çıkarım) |
| 11 | Sığ sızıntı/gaz akısı artışı (kayma–permeabilite eşleşmesi) | Nicel kuram yok — **spekülatif** | ? | Sürekli kimya/akı gözlemevi + eşzamanlı geodezi | Hayır | Kuramsal temel zayıf; yeni veri ve yeni model gerekir |
| 12 | Doğrultu-atımlı fayda yanal pürüz erozyon hızının kosismik gerilme düşümüyle ölçeklenmesi (Johnson & Burton 2026 analoğu) | Alan kaybı %/onyıl | Onyıl | 3B mekanik ters çözüm; 1999 sonrası tam GNSS | Kısmen | Yayımlanmış hızlarla 0 € ile ön model kurulabilir; sınama yeni veri gerektirir |

### Gaps
- Tablodaki "açık veri" durumları (KOERI/AFAD dalga biçimi arşivlerine ve deniz tabanı verilerine erişim) bu çalışmada test edilmedi; doğrulanamadı.
- Marmara'ya özgü, kalibre edilmiş bir SEAS tipi deprem-döngüsü modeli olmadığından, 1–12 numaralı öngörülerin genlikleri dalma-batma ve genel doğrultu-atımlı modellerden aktarılmıştır. Bu belirsizlik bir mertebe ve üzeridir.
