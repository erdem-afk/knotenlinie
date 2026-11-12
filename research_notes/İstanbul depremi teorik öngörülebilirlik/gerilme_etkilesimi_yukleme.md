# Gerilme etkileşimi, zamana bağlı yükleme ve kırılma zamanının öne alınması: kuram (2026 itibarıyla)

Kapsam: Marmara Denizi altındaki kilitli Kuzey Anadolu Fayı (KAF) segmenti gibi, 1912 Ganos ve 1999 İzmit depremleriyle yüklenmiş bir doğrultu atımlı fayda M7+ bir depremin kırılma zamanının statik, geçici ve zamana bağlı (viskoelastik, gözenek basıncı) gerilme değişimleriyle nasıl kaydığı ya da daraldığı. Yalnızca kuram ve modelleme literatürü var. Gözlemler, yalnızca bir kuramsal öngörüyü sınadıkları yerde anılıyor.

Notlar ve kurallar:
- "doğrulanamadı": birincil kaynakta bu çalışma sırasında kontrol edilemeyen sayı veya ayrıntı.
- "çıkarım": bu notlarda kaynaktaki formüllerden yapılan hesap. Kaynakta bu sayı yok.
- İstanbul için mutlak olasılık verilmiyor. Yalnızca oranlar ve zaman kaymaları var.
- 2026 deprem kataloğu ve Marmara GNSS verisi kullanılmadı.
- Kaynak araması OpenAlex (kayit/oa.py), Crossref ve açık erişim tam metinlerle yapıldı.
- Tam metni okunanlar: Pondard vd. 2007, Hussain vd. 2018 (Europe PMC) ve Brinkman vd. 2015. Öteki kaynaklar için yalnız özet okundu.
- Erişilemeyenler: GFZ'deki Lorenzo-Martín vd. 2006 PDF'i ve AGU'daki DeVries vd. 2016 PDF'i 403 döndü. Bu engel aşılmaya çalışılmadı.

---

## 1. Saat ilerletme (clock advance) kuramı: Coulomb adımı ve rate-and-state kararsızlık zamanı

### Takeaway
- **Coulomb eşik modeli:** Bir statik Coulomb adımı kırılmayı çevrimin her anında aynı miktarda öne alır: Δt = ΔCFF/τ̇.
- **Rate-and-state:** Sonuç ancak kalan süre T, nükleasyon zaman ölçeği t_a = Aσ/τ̇'den çok büyükse aynıdır. Çevrim sonunda (T ≲ t_a) statik bir adımın sağladığı ilerleme T(1−e^(−Δτ/Aσ)) ile, yani kalan süreyle sınırlanır. Buna karşılık geçici (dinamik) yükler çevrimin sonuna doğru daha etkili olur (Gomberg vd. 1998).
- **Marmara:** Seküler gerilme hızı yaklaşık 0,02–0,03 MPa/yıl. Buna göre her 0,1 MPa'lık (1 bar) adım yaklaşık 3–5 yıllık ilerlemeye karşılık gelir.

### Cited Findings

**Coulomb ölçeği**
- Coulomb gerilme değişimi ΔCFF = Δτ − μ*Δσ (sıkışma pozitif). Perfettini vd. 2003a'nın 2-B sürekli rate-and-state doğrultu atımlı fay modelinde kesme ve normal gerilme pertürbasyonları ΔCFF sabitse aynı tetikleme etkisini verir. Basit Coulomb modelinin saat ilerletme/geciktirme tahmini, çevrimin ilk %90'ında rate-and-state ile birinci mertebede uyumludur. Son %10'da ise kırılma öncesi keskin hız artışı nedeniyle belirgin biçimde ayrışır. — [Perfettini, Schmittbuhl & Cochard 2003a, JGR 108(B9), doi:10.1029/2002JB001804](https://doi.org/10.1029/2002JB001804)

**Gomberg vd. 1998: tek serbestlik dereceli yay-blok modeli**
- Modelde rate-and-state sürtünme, sabit tektonik yükleme ve sabit normal gerilme var. Tetiklenmiş deprem, kırılma zamanı Δt kadar öne alınmış deprem olarak tanımlanıyor.
- Sonuçlar:
  - Çevrim sonunda uygulanan statik adım, erken uygulanan eşit bir adımdan daha az saat ilerlemesi yaratır.
  - Geçici (kare dalga) yükte durum tersidir: geç uygulanan geçici yük daha fazla ilerleme yaratır.
  - Eşit Δt için geçici genliklerin statik adımlardan "birkaç on ila yüzlerce kat" büyük olması gerekir (t0'a bağlı).
  - Kırılmadaki toplam kayma yükleme geçmişinden bağımsızdır.
- Yaklaşık kapalı çözümler tam çözümü az tahmin eder. Fark, t0 çevrimin sonuna yaklaştıkça küçülür.
- Kaynak: [Gomberg, Beeler, Blanpied & Bodin 1998, JGR 103(B10), doi:10.1029/98JB01125](https://doi.org/10.1029/98JB01125)

**Dieterich 1994 kararsızlık zamanı formülü**
- Dieterich (1994) nükleasyon çözümü, sabit gerilme hızı τ̇ altında kaynak kayma hızı δ̇ olan bir yamanın kararsızlığa kadar geçen süresini verir:
  - t = (Aσ/τ̇)·ln[1 + τ̇/(Hσ·δ̇)]
  - t_a = Aσ/τ̇ (nükleasyon/artçı süresi)
- Bir Δτ adımı kayma hızını δ̇ → δ̇·exp(Δτ/Aσ) yapar (sabit σ).
- Dieterich artçı süresinin (t_a) ana şok yineleme süresiyle orantılı olduğunu öngörüp verilerin bunu desteklediğini belirtir.
- Kaynaklar: [Dieterich 1994, JGR 99(B2), 2601–2618, doi:10.1029/93JB02581](https://doi.org/10.1029/93JB02581). Formülün yeniden türetilmesi ve "kararsızlık zamanı" yaklaşımı: [Heimisson & Segall 2018, JGR 123, doi:10.1029/2018JB015656](https://doi.org/10.1029/2018JB015656)
- Formülün kesin yazımı (H = B/Dc − k/σ) Dieterich 1994 tam metninden doğrulanamadı. Yazım standart literatür biçimidir.

**Dinamik tetikleme ve kapanma periyodu (Perfettini vd. 2003b)**
- 2-B rate-and-state fay modelinde dinamik tetikleme (gerilme darbeleri, dalga paketleri) "kural değil istisnadır". Ancak yüksek gözenek basınçlı bölgelerde ya da "çevriminin en sonundaki faylarda" beklenir.
- Periyodik pertürbasyonlar için fay tepkisi, T0'dan kısa periyotlarda frekanstan bağımsızdır. Daha uzun periyotlarda frekansa güçlü biçimde bağlıdır.
- Kesim (crossover) periyodu T0, kararsızlığa kalan süreye eşittir.
- Gelgit tetiklemesinin "çevrim sonundan önce çok olası olmadığı" sonucuna varılır.
- Kaynak: [Perfettini, Schmittbuhl & Cochard 2003b, JGR 108(B9), doi:10.1029/2002JB001805](https://doi.org/10.1029/2002JB001805)

**KAF 1939–1992 dizisi (Stein, Barka & Dieterich 1997)**
- 10 kırılmanın 9'u önceki şoklarca kırılmaya yaklaştırılmış: tipik olarak 1–10 bar, yani 3–30 yıllık seküler yüklemeye eşdeğer. Bu, yaklaşık 0,33 bar/yıl ≈ 0,033 MPa/yıl ima eder (çıkarım).
- Geçici etkiler, tetikleyen ve kırılan şok arasındaki ortalama ~10 yıllık aralığa egemen.
- Her olaydan sonraki on yılda olasılıkta ortalama ~3 kat kazanç (oran).
- Kaynak: [Stein, Barka & Dieterich 1997, GJI 128(3), 594–604, doi:10.1111/j.1365-246X.1997.tb05321.x](https://doi.org/10.1111/j.1365-246X.1997.tb05321.x)

**Marmara seküler yüklemesi (Pondard vd. 2007, tam metin)**
- 12 km kilitlenme derinliği ve GPS'e dayalı dislokasyon modeli kullanılıyor.
- "200 yıllık yükleme, 5 km derinlikte fay segmentleri boyunca yaklaşık 40 bar Coulomb gerilme artışına karşılık gelir." Bu ≈ 0,2 bar/yıl = 0,02 MPa/yıl demektir.
- Bir M~7 olayının statik gerilme değişimi, kırılma ucundan birkaç on km uzakta "~1–10 bar"dır.
- Kaynak: [Pondard, Armijo, King, Meyer & Flerit 2007, GJI 171(3), 1185–1197, doi:10.1111/j.1365-246X.2007.03580.x](https://doi.org/10.1111/j.1365-246X.2007.03580.x)

**Tek fay ve popülasyon ayrımı (Gomberg vd. 2005)**
- Tek bir fayın koşullu kırılma olasılığı ile bağımsız fay popülasyonunun sismisite hızı ayrı tutuluyor.
- İki uç-üye tek-fay modeli öneriliyor. Bunlar, fay olgunlaşmamışken pertürbasyonlara farklı tepki verir. Olgun faylarda koşullu olasılık tahminleri genellikle anlamlı biçimde farklılaşmaz.
- Kaynak: [Gomberg, Belardinelli, Cocco & Reasenberg 2005, JGR 110, B05S04, doi:10.1029/2004JB003405](https://doi.org/10.1029/2004JB003405)

**1999'un Marmara'ya etkisi: oranlar (Parsons 2004)**
- Zamana bağlılık ve gerilme aktarımı eklenince bölgesel 30 yıllık olasılık Poisson değerinin ≈1,4 katına çıkıyor. Gerilme aktarımının tek başına katkısı, zamana bağlı modele göre ≈1,2 kat. İstanbul için toplam artış Poisson'a göre ≈2 kat.
- Bu oranlar özetteki değerlerden hesaplandı. Mutlak değerler bilinçli olarak yazılmadı.
- Parsons, belirsizliklerin gerilme aktarımı etkisine göre büyük olduğunu vurgular.
- Kaynak: [Parsons 2004, JGR 109, B05304, doi:10.1029/2003JB002667](https://doi.org/10.1029/2003JB002667). Önceki sürüm: [Parsons, Toda, Stein, Barka & Dieterich 2000, Science 288, 661–665, doi:10.1126/science.288.5466.661](https://doi.org/10.1126/science.288.5466.661)

**1894 depreminin Çınarcık kuzeyindeki etkisi**
- Pondard vd. 2007, Çınarcık havzası kuzeyindeki segmentte gerilmenin 1894 (Ms~7,3, yakın normal fay) nedeniyle azaldığını hesaplar.
- Yalnızca 1999 aktarımını dikkate alan çalışmaların (Parsons 2004) "tersine" sonuca vardığını belirtir.
- Kaynak: [Pondard vd. 2007](https://doi.org/10.1111/j.1365-246X.2007.03580.x)

### Inferences

**Çevrim içi konuma bağlılık (çıkarım; formüller Dieterich 1994 ve Gomberg vd. 1998'den)**
- Adım öncesi kalan süre T için:
  - τ̇/(Hσδ̇) = e^(T/t_a) − 1
  - Adımdan sonra kalan süre: T′ = t_a·ln[1 + (e^(T/t_a) − 1)·e^(−Δτ/Aσ)]
  - Saat ilerlemesi: Δt = T − T′
- Sınırlar:
  - T ≫ t_a (ve T′ ≫ t_a): Δt → Δτ/τ̇. Bu, Coulomb sonucudur ve çevrimin konumundan bağımsızdır.
  - T ≪ t_a (çevrim sonu): Δt ≈ T·(1 − e^(−Δτ/Aσ)) < T. Mutlak ilerleme kalan süreyle sınırlanır, ama göreli ilerleme Δt/T → 1'e yaklaşır.
  - Δτ ≳ birkaç Aσ ise anında tetiklenmeye karşılık gelir.

**Marmara için sayısal ölçek (çıkarım)**
- Seküler gerilme hızı: τ̇ = 0,02 MPa/yıl (Pondard) ile 0,033 MPa/yıl (Stein vd. ima) arası.
- Coulomb ilerlemesi:
  - ΔCFF = 0,1 MPa → 3–5 yıl
  - ΔCFF = 0,5 MPa → 15–25 yıl
- Rate-and-state ölçeği: Aσ için literatürde sık kullanılan 0,01–0,1 MPa aralığıyla (Marmara'ya özgü değer doğrulanamadı) t_a = Aσ/τ̇ ≈ 0,3–5 yıl çıkar.
- Bu ölçeklerin anlamı:
  - Marmara segmenti kırılmaya birkaç yıldan fazla uzaksa, 1999 statik adımının ilerlemesi Coulomb değerine yakındır (yıl ölçeği).
  - Ancak kalan süre birkaç yıl veya daha azsa, yeni küçük statik adımlar mutlak olarak ancak "kalan süre kadar" ilerletebilir.
  - Aynı dönemde dinamik ve geçici pertürbasyonlara duyarlılık artar.

**"Geç çevrim duyarlılığı"nın kuramsal anlamı**
- Statik adıma mutlak zaman tepkisi azalır, geçici yüke tepki artar (Gomberg 1998).
- Periyodik yüklere tepki ise kalan süre periyotla karşılaştırılabilir hale geldiğinde değişir (Perfettini 2003b).
- Yani geç çevrim, "küçük ve kısa pertürbasyonlara duyarlılığın arttığı" dönemdir. Bu, kalan süre hakkında bilgi taşıyabilecek tek kuramsal sinyaldir. Ancak etkisi kalan sürenin t_a mertebesine inmesinden sonra ortaya çıkar, yani yıl veya daha kısa ölçekte.

### Gaps
- Marmara'ya özgü Aσ ve kritik kayma mesafesi D_c bilinmiyor. t_a için yalnız mertebe aralığı verilebildi.
- 1999 İzmit + Düzce kosismik ΔCFF'nin Ana Marmara Fayı segmentleri üzerindeki değerleri bu çalışmada birincil kaynaktan sayısal olarak doğrulanamadı (Parsons 2004 ve Hubert-Ferrari vd. 2000 tam metinleri okunmadı). Yalnız oranlar alındı.
- Gomberg, Beeler & Blanpied (2000, JGR, "On rate-state and Coulomb failure models") tam metnine erişilmedi. Künyesi ve DOI'si doğrulanamadı.

---

## 2. Dieterich (1994) sismisite hızı kuramı ve uzantıları: geç çevrimde arka plan hızı, sessizlik ve hızlanma

### Takeaway
- **Dieterich teorisi:** Etkileşimsiz bir kaynak popülasyonunda arka plan sismisite hızı yalnızca gerilme hızı geçmişiyle belirlenir. Sabit yüklemede kendiliğinden bir "geç çevrim ivmelenmesi" öngörmez.
- **Gölgeler:** Gerilme gölgesi kaynaklı sessizlik yaklaşık |ΔCFF|/τ̇ sürer ve ardından geri döner.
- **AMR ve halka modelleri:** Hızlanan moment salımı (AMR) ve Mogi-halkası türü örüntüler yalnız belirli modellerde (King & Bowman 2003, hasar reolojisi) üretilir. AMR'nin istatistiksel anlamlılığı ise çürütülmüştür (Hardebeck vd. 2008).

### Cited Findings

**Temel model (Dieterich 1994)**
- Sismisite, başlangıç koşulları dağılmış bir nükleasyon kaynakları popülasyonu olarak modellenir.
- Omori artçı bozunumu öngörülür. Artçı süresi t_a, ana şok yineleme süresiyle orantılıdır.
- Formülasyon, rastgele karmaşıklıktaki gerilme geçmişlerine uygulanabilir ve sismisite hızı değişimlerinden sürücü gerilmenin terslenmesini önerir.
- Kaynak: [Dieterich 1994, doi:10.1029/93JB02581](https://doi.org/10.1029/93JB02581)

**Standart denklemler (literatürde standart biçim; Dieterich 1994 tam metni okunmadı, yazım doğrulanamadı)**
- Durum değişkeni yazımı:
  - R = r / (γ·τ̇_r)
  - dγ = (dt − γ·dS)/Aσ
- Adım yanıtı:
  - R(t)/r = 1 / [1 + (e^(−Δτ/Aσ) − 1)·e^(−t/t_a)]
  - t_a = Aσ/τ̇_r

**Heimisson & Segall 2018 genellemesi**
- Model, durum değişkeni kullanmadan, keyfî kesme gerilmesi geçmişi için sabit normal gerilmede geçerli olarak yeniden türetilir.
- Normal gerilme zamanla değişirse sonuçlar hafifçe farklıdır.
- Toplam olay sayısı ve hız için, gerilme geçmişinin türevine açıkça bağlı olmayan "basit integral ifadeler" verilir. Biçim: R/r = K(t) / [1 + (1/t_a)∫₀ᵗ K(t′)dt′], K = exp(S(t)/Aσ), S pertürbasyon gerilmesi. Kesin gösterim tam metinden doğrulanamadı.
- Omori bozunumu yalnızca adımla kararlı durumun üstüne çıkan ya da üstünde kalan kaynaklardan gelir. Hiçbir kaynak kararlı durumun üstüne çıkmazsa Omori dizisi oluşmaz.
- Kaynak: [Heimisson & Segall 2018, doi:10.1029/2018JB015656](https://doi.org/10.1029/2018JB015656)

**Etkileşimli kaynaklar (Heimisson 2019)**
- Belirli koşullarda etkileşimli popülasyon, eşdeğer bir etkileşimsiz popülasyon olarak modellenebilir.
- Pertürbasyon b-değerini değiştirirse Dieterich modeli hızı az ya da fazla tahmin edebilir.
- Etkileşimler, t ≫ t_a için toplam kümülatif olay sayısını değiştirmez.
- Kaynak: [Heimisson 2019, JGR 124, doi:10.1029/2018JB016823](https://doi.org/10.1029/2018JB016823)

**Gerilme geçmişinin katalogdan terslenmesi (Jiang, Trugman & González 2026)**
- Bayesçi, fizik-bilgili bir ters çözüm (T-rate aracı) gerilme hızı evrimini sismisite hızından çıkarıyor.
- Reno-Mogul 2008 uygulamasında M5.1'den 3 gün önce başlayan geçici bir gerilme artışını ayırt ediyor.
- Zamanlama tercihlere karşı kararlı, ama genlik arka plan hızı r varsayımına "güçlü biçimde" bağlı.
- Kaynak: [Jiang, Trugman & González 2026, JGR, doi:10.1029/2026JB033922](https://doi.org/10.1029/2026JB033922)

**Bölgesel sismisite modeli (King & Bowman 2003)**
- Gerilme alanı, kırılma gerilmesine göre ve rastgele heterojenlikle modelleniyor.
- Büyük olaydan hemen sonra artçı bölgeleri ve gerilme gölgeleri oluşur. Yükleme, artçı bölgelerindeki yüksek gerilmeyi azaltır. Gölgeyle birleşince episantr çevresinde geniş bir sessiz bölge oluşur.
- Olay öncesi sismisite, gölgeler yüklemeyle "dolduğunda" ortaya çıkar. Artış önce birkaç fay uzunluğu uzakta başlar ve olay yaklaştıkça içe doğru ilerler. Böylece bölgesel moment salımı artar (AMR).
- Kaynak: [King & Bowman 2003, JGR 108(B2), doi:10.1029/2001JB000783](https://doi.org/10.1029/2001JB000783)

**AMR'nin istatistiksel sınaması (Hardebeck, Felzer & Michael 2008)**
- Kaliforniya-Nevada (1950–2006, M≥6,5) ve Sumatra 2004 için veri uydurmayla hem AMR hem yavaşlayan moment salımı bulunabiliyor.
- Kümelenmeli sentetik kataloglar (gerçek AMR içermeyen) benzer AMR üretiyor.
- Daha önce önerilen ölçekleme bağıntıları istatistiksel yapaylık. AMR "istatistiksel olarak anlamsız".
- Kaynak: [Hardebeck, Felzer & Michael 2008, JGR 113, B08310, doi:10.1029/2007JB005410](https://doi.org/10.1029/2007JB005410)

**Hasar reolojisi (Ben-Zion & Lyakhovsky 2002)**
- Hasar reolojisi çerçevesinde hızlanan sismik salım ve ilişkili örüntüler inceleniyor. Kaynak OpenAlex'te özetsiz.
- Hangi parametre rejiminde AMR'nin ve hangi zaman ölçeğinde (yıl veya on yıl) ortaya çıktığı doğrulanamadı.
- Kaynak: [Ben-Zion & Lyakhovsky 2002, PAGEOPH 159, doi:10.1007/s00024-002-8740-9](https://doi.org/10.1007/s00024-002-8740-9)
- Güncel hasar-reolojisi + rate-and-state çevrim modelleri, fay zonu katılık azalmasının çevrimler boyunca birikebildiğini gösteriyor: [Zhai, Huang, Chao & Ampuero 2025, GJI 242, ggaf274, doi:10.1093/gji/ggaf274](https://doi.org/10.1093/gji/ggaf274)

**Aktivasyon mu sessizlik mi (Rundle vd. 2011)**
- Uç-üye aktivasyon ve sessizlik tahmin modelleri karşılaştırılıyor.
- Kaliforniya verisiyle geriye dönük testte sessizlik modeli "hafif ama anlamlı olmayan" bir farkla daha iyi.
- Kaynak: [Rundle vd. 2011, GJI 187, 225–236, doi:10.1111/j.1365-246X.2011.05134.x](https://doi.org/10.1111/j.1365-246X.2011.05134.x)

### Inferences

**Gölge süresi (çıkarım)**
- Adım yanıtı formülünden, büyük negatif Δτ için hız ancak t ≈ t_a·|Δτ|/Aσ = |Δτ|/τ̇ sonra geri döner. Yani gölge süresi, gölgeyi seküler yüklemeyle doldurma süresine eşittir.
- Örnek: Marmara'da 1894 benzeri −0,2 MPa'lık bir gölge, 0,02 MPa/yıl ile yaklaşık 10 yıl sürer.

**Geç çevrimde sabit gerilme hızı (çıkarım)**
- Bu durumda Dieterich modeli R = r (sabit) öngörür.
- Geç çevrim "ivmelenmesi" ancak üç yoldan gelebilir:
  - τ̇'nin artması (ör. derin kaymanın hızlanması, viskoelastik yeniden yükleme)
  - Kaynak popülasyonunun kendisinin değişmesi (b-değeri, hasar)
  - Ana fay üzerinde nükleasyon (popülasyon modeli dışı)
- Bu nedenle kuram, "uzun süreli sabit hız + 1999 sonrası viskoelastik yükleme nedeniyle hafif yükselmiş ve bozunan hız" bekler.
- Hız, gerilme hızı oranıyla ölçeklenir: R/r = τ̇(t)/τ̇_r (uzun zaman sınırı).

**Mogi halkası**
- Nicel olarak yalnız King & Bowman tipi gölge-dolma modellerinde "fay uzunluğunun birkaç katı uzaklıktan içe göç" biçiminde öngörülür.
- Zaman ölçeği, gölgenin ΔCFF/τ̇ ile dolma süresidir. 1999 gölgeleri için bu on yıl mertebesindedir (çıkarım).

### Gaps
- Ben-Zion & Lyakhovsky (2002) için AMR'nin parametre koşulları ve zaman ölçeği birincil kaynaktan doğrulanamadı.
- Cattania vd. (heterojen gerilme / rate-and-state artçı modelleri; ör. Cattania vd. 2014 JGR) bu turda sorgulanmadı. Künyeler doğrulanamadı.
- Marmara için geç çevrim popülasyon-hızı öngörüsü yapan yayımlanmış bir Dieterich modeli bulunamadı.

---

## 3. Viskoelastik deprem çevrimi kuramı: gerinim hızının çevrim içi evrimi ve 1999 sonrası Marmara'nın yeniden yüklenmesi

### Takeaway
- **Maxwell modeli:** Basit Maxwell elastik-tabaka/viskoelastik-yarım-uzay modelleri (Savage & Prescott 1978), τ0 = T·μ/(2η) ≫ 1 olduğunda çevrimin başında yüksek, sonunda düşük fay-yakını gerinim hızı öngörür.
- **KAF gözlemleri:** KAF'ta gözlenen gerinim hızı tarihçesi, ~10 yıllık postsismik geçiciden sonra sabittir (~0,5 μstrain/yıl). Bu, gerinim hızının geç çevrim değişimini kullanılamayacak kadar küçük kılar (Hussain vd. 2018).
- **1999 sonrası yeniden yükleme:** Burgers tipi mantoyla 1999 sonrası viskoelastik yeniden yükleme on yıllar sürer. DeVries vd. 2016, Marmara'daki zamana bağlı ΔCFS'nin 2023'e kadar önceki KAF depremlerinin ortalama "görünür eşiklerine" ulaşabileceğini öngördü.

### Cited Findings

**Klasik model (Savage & Prescott 1978)**
- Viskoelastik altlık üzerindeki elastik levhada periyodik doğrultu atımlı çevrim modelleniyor.
- Astenosfer gevşemesinin yüzey deformasyonu, elastik yarım uzayda makul bir derin kayma dağılımıyla tıpatıp üretilebilir. Yani iki mekanizmanın ayırt edilmesi zordur.
- Viskoelastikliğin ana etkileri: hızlı postsismik deformasyon ve gerinimin faya daha yakın yoğunlaşması.
- Kaynak: [Savage & Prescott 1978, JGR 83(B7), 3369–3376, doi:10.1029/JB083iB07p03369](https://doi.org/10.1029/JB083iB07p03369)

**Hussain vd. 2018: τ0 parametresi ve KAF ölçümleri (tam metin)**
- Davranışı kontrol eden parametre τ0: olaylar arası süre T'nin Maxwell gevşeme süresine (2η/μ) oranı.
  - τ0 ≫ 1: hızla azalan gerinim hızı.
  - τ0 ≲ 1: neredeyse sabit gerinim hızı.
- KAF için T = 250 yıl ve μ = 3×10¹⁰ Pa ile τ0 = 1000, 100, 10, 1 ve 0,1 değerleri, sırasıyla ~10¹⁷, 10¹⁸, 10¹⁹, 10²⁰ ve 10²¹ Pa s viskoziteye karşılık geliyor.
- KAF'ta yüzey gerinim hızı "~0,5 microstrain/yıl" ve fay boyunca kayda değer biçimde sabit.
- Gerinim hızı, ~10 yıllık postsismik geçiciden sonra son depremden bu yana geçen süreden bağımsız. Veri, depremden 10–85 yıl sonrası (Envisat) ve 1754'ten ~245 yıl sonrası (1999 öncesi GNSS) aralığını kapsıyor.
- Alt kabuk viskozitesi >~10²⁰ Pa s olmalı. Fay zonu zayıf.
- ~10 yıllık geçicinin toplam gerinimi, 250 yıllık birikimin ~%10'u.
- Kaynak: [Hussain, Wright, Walters, Bekaert, Lloyd & Hooper 2018, Nat. Commun. 9, 1392, doi:10.1038/s41467-018-03739-2](https://doi.org/10.1038/s41467-018-03739-2)

**Hetland & Hager: genel doğrusal viskoelastik çözüm**
- Herhangi bir doğrusal viskoelastik reoloji (Maxwell, SLS, Burgers, üç-viskoziteli) ve herhangi bir deprem dizisi için analitik 2-B çözüm. Kaynak: [Hetland & Hager 2005, JGR 110, B10401, doi:10.1029/2005JB003689](https://doi.org/10.1029/2005JB003689)
- "Isınmış" (spun-up) olgun faylarda çevrimler arası hız, aynı geometrideki elastik modelin hızına eşit.
- Periyodik olmayan kırılmada fay, ortalama kayma hızıyla periyodik kırılıyormuş gibi olgun duruma yaklaşır.
- Son çevrimlerde kayma hızı ortalamadan hızlı (yavaş) olmuşsa, çevrimler arası hızlar daha büyük (küçük) olur.
- Kaynak: [Hetland & Hager 2006, G-cubed 7, doi:10.1029/2005GC001087](https://doi.org/10.1029/2005GC001087)

**Meade, Klinger & Hetland 2013**
- 15 kıtasal doğrultu atımlı fayda jeolojik ve jeodezik hızlar topluca 0,94 ± 0,09 eğimle uyumlu.
- Tek gevşeme süreli iki-tabaka Maxwell modeli bunu hızlı postsismik deformasyonla birlikte açıklayamıyor. İki gevşeme süreli Burgers modeli açıklayabiliyor. Bu, "hızlı, gerilmece geri kazanılabilir postsismik evre + çok yavaş değişen interseismik evre" demek.
- Kaynak: [Meade, Klinger & Hetland 2013, BSSA 103(5), doi:10.1785/0120130006](https://doi.org/10.1785/0120130006)

**Dolan & Meade 2017**
- 1999 İzmit kırığı boyunca deprem öncesi jeodezik hız 26–28 mm/yıl. Bu, Holosen jeolojik hızından ~%40 hızlı.
- Denali'de jeodezik hız jeolojiğin ~yarısı, Kunlun'da ikisi eşit.
- Sonuç: jeodezik/jeolojik oran "bir sonraki depreme kalan süre için tanısal olmayabilir". Bu, reolojik çevrim modellerinin öngörüsüyle çelişir.
- Kaynak: [Dolan & Meade 2017, G-cubed 18, doi:10.1002/2017GC007014](https://doi.org/10.1002/2017GC007014)

**Takeuchi & Fialko 2012**
- Laboratuvar kökenli üstel-yasa reolojiler ve termomekanik bağlaşımla, alt kabukta ~3–5 km genişlikte, plaka hareketinin >%50'sini taşıyan yerelleşmiş makaslama zonu öngörülüyor.
- Litosferdeki deviatorik gerilme ~10² MPa mertebesinde.
- Kaynak: [Takeuchi & Fialko 2012, JGR 117, B05403, doi:10.1029/2011JB009056](https://doi.org/10.1029/2011JB009056)

**Johnson & Segall 2004**
- Derin, gerilme-sürücülü krip içeren viskoelastik çevrim modelleri (San Andreas).
- Kaynak: [Johnson & Segall 2004, JGR 109, B10403, doi:10.1029/2004JB003096](https://doi.org/10.1029/2004JB003096)
- Yalnız künye doğrulandı. Sayısal sonuçlar bu turda okunmadı.

**1999 sonrası postsismik deformasyon (Ergintav vd. 2009)**
- 7 yıl sonra KAF boyunca göreli postsismik hız ~10–12 mm/yıl, yani kararlı interseismik hızın ~%50'si.
- Zaman serileri 1, 150 ve 3500 gün bozunum sabitli üç logaritmik terimle uyduruluyor.
- Etki ~200 km uzaktaki Ankara'ya kadar çözünür.
- Marmara'da K-G genişleme bileşeni var.
- Kaynak: [Ergintav vd. 2009, JGR 114, B07403, doi:10.1029/2008JB006021](https://doi.org/10.1029/2008JB006021)

**Hearn vd. 2009 (3-B sonlu elemanlar)**
- İlk aylar sığ ve derin afterslip'e bağlı.
- Sonrası için 2–5×10¹⁹ Pa s viskoelastik gevşeme gerekiyor. Ancak doğrusal reolojide bu değer, 1999 öncesi gözlenen yerelleşmiş interseismik deformasyonla çelişiyor.
- Çözüm: zamanla artan etkin viskozite, yani iki viskoziteli Burgers (2–5×10¹⁹ ve ≥2×10²⁰ Pa s) ya da üstel-yasa reoloji.
- Kaynak: [Hearn, McClusky, Ergintav & Reilinger 2009, JGR 114, B08405, doi:10.1029/2008JB006026](https://doi.org/10.1029/2008JB006026)

**Hearn 2002**
- Hız-güçlenmeli sürtünmeli afterslip, İzmit postsismik GPS verisini alt kabuk viskoelastik gevşemesinden daha iyi açıklıyor.
- Özetin, Düzce hiposantrındaki Coulomb gerilme artışının sayısal değerini veren kısmı kesik. Değer doğrulanamadı.
- Kaynak: [Hearn 2002, BSSA 92(1), 172–193, doi:10.1785/0120000832](https://doi.org/10.1785/0120000832)

**DeVries, Krastev & Meade 2016**
- 1939'dan beri 40°D'nin batısında 8 adet M>6,7 olay doğudan batıya ilerliyor. Ortalama olaylar arası süre 8,5 ± 11 yıl (%67).
- Gecikmeli tetikleme, üst mantodaki difüzif viskoelastik cephelerle açıklanıyor. Model: elastik üst kabuk + Burgers manto (Maxwell ηM = 4×10¹⁸–1×10¹⁹ Pa s, Kelvin ηK = 1×10¹⁸–1×10¹⁹ Pa s, 1999 öncesi/sonrası jeodeziyle kısıtlı).
- Depremlerin gerçekleştiği "görünür eşik" ortalama ΔCFS'leri ~0,02–3,15 MPa. Bunlar statik değerleri %177'ye kadar aşabiliyor.
- "2023'e kadar" Marmara'da İstanbul yakınındaki kuzey kolda zamana bağlı ortalama ΔCFS'nin önceki KAF depremlerinin ortalama görünür eşiklerine ulaşabileceği çıkarılıyor.
- Kaynak: [DeVries, Krastev & Meade 2016, G-cubed 17, doi:10.1002/2016GC006313](https://doi.org/10.1002/2016GC006313)
- Tam metin 403 döndü. Marmara için yıla göre ΔCFS değerleri doğrulanamadı.

**Lorenzo-Martín, Roth & Wang 2006**
- KAF zonunda elastik ve inelastik (viskoelastik) tetikleme modeli.
- Özet OpenAlex/Crossref'te yok, tam metin 403 döndü. Reoloji, Marmara için öngörülen gecikme ve ΔCFF değerleri doğrulanamadı.
- Kaynak: [Lorenzo-Martín, Roth & Wang 2006, Tectonophysics 424, doi:10.1016/j.tecto.2006.03.046](https://doi.org/10.1016/j.tecto.2006.03.046)

**Nalbant, Uzunca, Utkucu & Durmuş 2026 (EGU26 bildiri özeti, hakemsiz)**
- 1999 çiftinin viskoelastik postsismik gevşemesi:
  - 2006 Gemlik (Mw5,0) ve 2023 Mudanya (Mw5,0) konumlarındaki kosismik gerilme gölgelerini "aşamalı olarak silmiş ve pozitife çevirmiş".
  - 2019 Silivri (Mw5,7) ve 2025 Silivri (Mw6,2) konumlarındaki pozitif kosismik değişimleri ise "önemli ölçüde büyütmüş".
- Yazarlar, 1766'dan beri kırılmamış Ana Marmara Segmenti'nde artan orta büyüklükteki deprem sıklığının "geç evre, kritik gerilmeli rejime geçişi yansıtabileceğini" öne sürüyor (yoruma dayalı ifade).
- Kaynak: [Nalbant vd. 2026, EGU General Assembly abstract, doi:10.5194/egusphere-egu26-11337](https://doi.org/10.5194/egusphere-egu26-11337)

**Utkucu vd. 2023 (EGU23 bildiri özeti, hakemsiz)**
- 715'ten beri çoklu çevrimli Coulomb evrim modeli (kosismik + viskoelastik + seküler).
- Doğu Marmara boşluğundaki örnekleme noktalarında bugünkü gerilme: doğu 115, orta 131, batı 85 bar.
- Önceki büyük olaylardan (989, 1343, 1509, 1766) önceki toplam değişimler 26–131 bar.
- Karşılaştırma ölçütü: kıtasal doğrultu atımlı ortalama gerilme düşümü ~35 bar.
- Kaynak: [Utkucu, Durmuş, Uzunca, Nalbant & Kızılbuğa 2023, EGU abstract, doi:10.5194/egusphere-egu23-7909](https://doi.org/10.5194/egusphere-egu23-7909)

### Inferences

**Gevşeme süreleri ve 2026'daki kalıntı yükleme (çıkarım)**
- Maxwell gevşeme süresi τ_M = η/μ (μ = 3×10¹⁰ Pa ile):
  - η = 4×10¹⁸ Pa s → ~4 yıl
  - 1×10¹⁹ → ~11 yıl
  - 2×10²⁰ → ~210 yıl
- 1999'dan 27 yıl sonra (2026), kısa (Maxwell/Kelvin) bileşenin yeniden yüklemesi büyük ölçüde tamamlanmış olmalı: e^(−27/11) ≈ %9 kalan. Uzun (≥2×10²⁰) bileşen ise hâlâ yavaşça katkı veriyor olmalı.
- Örnek: toplam viskoelastik artış 0,1 MPa ve τ = 10 yıl ise, 2026'daki ek gerilme hızı ≈ (0,1/10)·e^(−2,7) ≈ 7×10⁻⁴ MPa/yıl. Bu, seküler hızın (0,02 MPa/yıl) yalnız ~%3'ü. Dolayısıyla viskoelastik katkının bugünkü etkisi, 1999 sonrası toplanmış kümülatif değeriyle (yıllar mertebesinde ilerleme) belirlenir. Bugünkü hız artışı belirleyici değildir.

**Reoloji çelişkisi**
- DeVries vd. 2016'nın düşük manto viskoziteleri, Hussain vd. 2018'in alt kabuk için >10²⁰ Pa s sonucuyla ve Hearn vd. 2009'un ikinci viskozitesiyle birebir çelişmez. Katmanlar farklıdır: DeVries manto, Hussain alt kabuk.
- Ancak 1999'un Marmara'ya viskoelastik katkısının büyüklüğü bu seçimlere çok duyarlıdır.

**Geç çevrim gerinim hızı**
- Kuram (τ0 ≫ 1 ise) geç çevrimde yavaşlama öngörür. KAF verisi (Hussain) ise geç çevrimde sabitlik gösterir.
- Bu durumda kuramsal olarak beklenen "geç çevrim gerinim hızı sinyali" ya sıfıra yakındır ya da GNSS duyarlılığının altındadır.
- Yıl ölçeğinde gözlenebilecek tek kuramsal gerinim sinyali, nükleasyona bağlı derin kayma hızlanmasıdır. Bu, popülasyon değil tek fay rate-and-state öngörüsüdür (bkz. Bölüm 1, 4).

### Gaps
- DeVries vd. 2016 ve Lorenzo-Martín vd. 2006'nın Marmara için yıla göre ΔCFS eğrileri ve öngörülen "gecikme" değerleri birincil kaynaktan okunamadı (403).
- Pollitz'in katmanlı viskoelastik İzmit/Marmara çalışmaları ve Nalbant vd. (1998, 2002) stres evrimi makalelerinin künyeleri bu turda doğrulanmadı.
- 1999'un Marmara segmentlerinde ürettiği kümülatif viskoelastik ΔCFF'nin hakemli bir kaynakta yıl yıl verilmiş değeri bulunamadı. Yalnız EGU özetlerinde nitel ifadeler var.

---

## 4. Gözenek basıncı ve akışkan kuramları

### Takeaway
- **Poroelastik Coulomb:** Poroelastik etki, Coulomb hesabına drenajsız ani tepki (etkin sürtünme veya Skempton yaklaşımı) ve difüzyonla gecikmiş bir bileşen olarak girer.
- **Difüzyon süresi:** L ~ 10 km için t ~ L²/(4πD) ≈ aylar ile birkaç yıl (D = 0,1–1 m²/s).
- **Fay-valf modelleri:** Sibson ve Zhu vd. 2020, interseismik aşırı basınç birikimini ve geç çevrimde kilidin çözülmesini veya sürü sismisitesini öngörür, ama Marmara için nicel bir zaman öngörüsü vermez.
- **Dilatans-difüzyon:** Kestirim kuramı olarak 1970'ler sonrası terk edilmiştir. Bugün dilatansın rate-and-state ile birlikte nükleasyonu kararlılaştırıcı rolü inceleniyor.

### Cited Findings

**Poroelastik Coulomb (Cocco & Rice 2002)**
- Gözenek basıncı normal gerilmeyle orantılı varsayılırsa "etkin sürtünme" kavramı çıkar.
- Fay zonu kesme modülü çevreden çok küçükse gözenek basıncı fay-normal gerilmeyle, elastik uyumsuzluk küçükse ortalama gerilmeyle belirlenir.
- Daha uzun sürelerde geçirgen bir fay çevresiyle yerel basınç dengesine gelebilir.
- Kaynak: [Cocco & Rice 2002, JGR 107(B2), doi:10.1029/2000JB000138](https://doi.org/10.1029/2000JB000138)

**Fay-valf davranışı (Sibson)**
- Kaynak (özet bu turda okunmadı; künye doğrulandı): [Sibson 1992, Tectonophysics 211, 283–293, doi:10.1016/0040-1951(92)90065-E](https://doi.org/10.1016/0040-1951(92)90065-E)
- Güncel sentez: neredeyse litostatik aşırı basınçlı akışkanlar sismojenik zonun alt kısmına yerel olarak sızar. Kırılma, artan akışkan basıncı (sürtünme dayanımı düşer) ve artan kesme gerilmesinin ikili sürüşüyle olur.
- Kırılma sonrası boşalım artçı dönemi boyunca dayanımı artırır. Hidrotermal kapanma (sealing) sonrası aşırı basınç yeniden birikir.
- Sibson, bunun en çok sıkışmalı/transpresif rejimlerde beklendiğini belirtir. Marmara transtansiyoneldir; bu bir çıkarım ve uyarıdır.
- Kaynak: [Sibson 2020, Earth Planets Space 72, 31, doi:10.1186/s40623-020-01153-x](https://doi.org/10.1186/s40623-020-01153-x)

**Akışkan-bağlaşımlı çevrim simülasyonu (Zhu, Allison, Dunham & Yang 2020)**
- 2-B antiplane doğrultu atımlı rate-and-state çevrim modeli: Darcy akışı, geçirgenlik evrimi.
- İnterseismik dönemde iyileşme/kapanma geçirgenliği düşürür ve aşırı basınç gelişir. Deprem geçirgenliği artırınca basınç boşalır.
- Yükselen akışkanlar sismojenik zonun tabanında akışkan sürücülü sismik olmayan kayma ve sismojenik zon içinde sürüler üretir.
- Model "geç interseismik kilit çözülmesi, yavaş kayma ve krip geçicileri"ni açıklayabilir.
- Kaynak: [Zhu vd. 2020, Nat. Commun. 11, 4833, doi:10.1038/s41467-020-18598-z](https://doi.org/10.1038/s41467-020-18598-z)

**Dilatans-difüzyon ve dilatansın güncel rolü**
- Klasik kestirim kuramı: [Scholz, Sykes & Aggarwal 1973, Science 181, 803–810, doi:10.1126/science.181.4102.803](https://doi.org/10.1126/science.181.4102.803). Özet yok; yalnız künye doğrulandı.
- Güncel rate-and-state + poroelastik doğrusal kararlılık analizi: dilatans ve sıkışmanın kararlılığa etkisi. Kaynak: [Heimisson vd. 2021, JGR 126, doi:10.1029/2021JB022071](https://doi.org/10.1029/2021JB022071). Yazar listesi ve sonuç ayrıntıları bu turda doğrulanamadı.
- Dilatans-difüzyonun 1970'lerden sonra (Vp/Vs öncül iddialarının tekrarlanamaması nedeniyle) genel kestirim kuramı olarak terk edildiği bilgisi bu turda birincil kaynaktan doğrulanamadı. Standart literatür bilgisidir.

**Gelgit ve hidrolojik modülasyon (Zhao vd. 2025)**
- Orta San Andreas'ta olağan depremler uzun periyotlu (hidrolojik), LFE'ler kısa periyotlu (gelgit) yüklemeye daha duyarlı.
- Bu, anlık olmayan nükleasyon sırasında gözenek akışkanı difüzyonuna işaret ediyor.
- Kaynak: [Zhao, Xue, Bürgmann, Heimisson, Lu & Yue 2025, Sci. Adv., doi:10.1126/sciadv.ady6350](https://doi.org/10.1126/sciadv.ady6350)

**Difüzyon tetiklemesinin olay ölçeğinde uygulamaları**
- Vogtland 2000 sürüsü (Hainzl & Ogata 2005; künye OpenAlex aramasından): [doi:10.1029/2004JB003267](https://doi.org/10.1029/2004JB003267)
- Iquique 2014 üst levha artçıları: [Nat. Commun. 2025, doi:10.1038/s41467-025-65013-6](https://doi.org/10.1038/s41467-025-65013-6)
- Yazar ayrıntıları ikisi için de doğrulanamadı.

### Inferences

**Difüzyon zaman ölçeği (çıkarım)**
- Yaygın kullanılan tetikleme cephesi bağıntısı r = √(4πDt) (Shapiro vd. 1997 türü; bu turda doğrulanamadı) ile t = r²/(4πD):
  - r = 10 km, D = 1 m²/s → ~3 ay
  - D = 0,1 m²/s → ~2,5 yıl
- Bu, poroelastik gecikmenin İzmit sonrası birkaç yıl içinde tamamlanmış olması gerektiğini ve 2026'da 1999'dan kaynaklı ek bir difüzyon yüklemesi beklenmediğini ima eder.

**Fay-valf ve gözlenebilirlik**
- Fay-valf modelleri yıl ölçeğinde gözlenebilir şunları öngörebilir: sismojenik tabanda sürü göçleri ve tekrarlayan deprem hızlanmaları. Ancak periyot ve genlik, geçirgenlik ve kapanma parametrelerine bağlı ve Marmara için kısıtsız.

### Gaps
- Marmara fay zonu hidrolik difüzivitesi ve geçirgenlik evrimi için kuramsal veya modelsel değer bulunamadı.
- Dilatans-difüzyon kuramının tarihçesi ve terk edilişi için birincil inceleme (ör. Scholz'un ders kitabı, Segall & Rice 1995) bu turda okunmadı.

---

## 5. Levha sınırı boyunca deprem dizileri ve yayılma kuramı: olaylar arası gecikme dağılımı

### Takeaway
- **Gecikme ölçekleri:** KAF için kuram ve modeller olaylar arası gecikmeyi iki ölçekte verir:
  - Statik/rate-and-state Coulomb + seküler yüklemeyle ~10 yıl (Stein vd. 1997: ortalama ~10 yıl; DeVries vd. 2016: 8,5 ± 11 yıl).
  - Marmara pull-apart'ta yayılan dizilerin "linear KAF dizisinden onlarca yıl sonra" gelmesi (Pondard vd. 2007: 18. yy dizisi 1719–1766).
- **Yayılma koşulu:** Yayılma, ancak yükleme "kırılmaya yakın ve tekdüze" ise beklenir. 20. yy dizisi Marmara'yı dizi olarak geçmemiştir.

### Cited Findings

**KAF 1939–1992 dizisi**
- Stein vd. 1997: 9/10 olay önceki şoklarca yüklenmiş, 1–10 bar ≈ 3–30 yıl. Tetikleyici ile kırılan şok arası ortalama ~10 yıl. Olasılık kazancı ~3 kat (oran). — [Stein vd. 1997](https://doi.org/10.1111/j.1365-246X.1997.tb05321.x)
- DeVries vd. 2016: batıya ilerleme ortalama 8,5 ± 11 yıl (%67). Gecikme mantodaki viskoelastik difüzif cephelerle açıklanıyor. — [DeVries vd. 2016](https://doi.org/10.1002/2016GC006313)

**Pondard vd. 2007 (tam metin)**
- KAF'ın lineer kısmı yüzlerce yıllık ölçekte tek segment gibi davranıyor: 1939–1944 arasında ~700 km, 3–7 m kayma, 5 yılda.
- Marmara'da depremler zamanda daha dağınık (1719–1766 ve 1894–1999). Kümelenme ve yayılan diziler, her iki çevrimde de lineer KAF dizisinin "birkaç on yıl sonrasında" Marmara'ya ulaşıyor.
- Marmara fay sistemi diziyi "durdurabilir veya geciktirebilir".
- 200 yıllık seküler yükleme ≈ 40 bar.
- 50–80 bar'dan fazla yüklenmiş bir segmentin kırılmadan kalması "olası değil". Senaryo h'de merkez Marmara segmentinde 500 yıllık kırılmasızlık >10 m kayma açığı ve M>7,6 gerektirirdi. Bu, tarihsel sismisite ve 150–280 yıllık yineleme ile uyumsuz bulunuyor.
- Büyük olaylarda seküler yükleme, orta büyüklükteki olaylarda (M~6) yanal etkileşim daha belirleyici.
- 1894 ve 1912 izole olayları, 18. yy dizisinin tekdüze olmayan gerilme boşaltımının sonucu. Bu nedenle 20. yy dizisi Marmara'yı dizi olarak geçmedi.
- Bugünkü yükleme, İstanbul'un GB'sındaki 70 km'lik merkez Marmara segmentinde "özellikle yüksek".
- Kaynak: [Pondard vd. 2007](https://doi.org/10.1111/j.1365-246X.2007.03580.x)

**Gerilme gölgeleri (Harris 1998)**
- Gerilme tetikleme ve gölge çalışmalarının nicel derlemesi.
- Kaynak: [Harris 1998, JGR 103(B10), 24347–24358, doi:10.1029/98JB01576](https://doi.org/10.1029/98JB01576)

### Inferences

**İki gecikme ölçeği (çıkarım)**
- "Statik adım ölçeği": ~1–10 bar / ~0,2–0,3 bar/yıl ≈ 3–50 yıl.
- "Viskoelastik difüzyon ölçeği": τ_M ~ 4–11 yıl (Burgers manto).
- Gözlenen 8,5 ± 11 yıllık dağılım iki mekanizmayla da tutarlı. Büyük saçılım, kuramın tekil bir gecikme değil geniş bir dağılım öngördüğünü gösterir.

**1999 → Marmara**
- Rate-and-state'te olasılık kazancının geçici kısmı t_a (~yıllar) içinde söner. Kalıcı kısım ΔCFF/τ̇ kadar saat ilerlemesidir.
- 27 yıl sonra kuram, "geçici kazançtan" çok "kalıcı ilerleme + viskoelastik ek yükleme"nin geçerli olduğunu söyler.

### Gaps
- King & Bowman 2003 ve Pondard 2007 modellerinin, bir sonraki Marmara olayı için olasılık yoğunluğu biçiminde nicel bir gecikme dağılımı vermediği görülüyor. Pondard'da böyle bir dağılım yok.
- Tek-fay rate-and-state ile dizi istatistiği (ör. gecikme pdf'i) üreten Marmara'ya özgü fizik-tabanlı çevrim simülatörü (RSQSim türü) çalışması bu turda bulunamadı.

---

## 6. Gelgit ve mevsimsel gerilme duyarlılığı kuramı

### Takeaway
- **Rate-and-state ölçeklemesi:** Rate-and-state kuramı modülasyon genliğini kısa periyotlarda (T ≪ t_a) Δτ/Aσ ile, uzun periyotlarda (T ≫ t_a) ωΔτ/τ̇ ile ölçekler. Bu yüzden yıllık yükler, aynı genlikteki günlük gelgitten çok daha etkili olabilir (Heimisson & Avouac 2020; Ader vd. 2014).
- **Geç çevrimde artan korelasyon:** Bu yalnızca bazı modellerde öngörülür: ortalama-alan (Brinkman vd. 2015) ve tek-yama kalan-süre etkisi (Perfettini 2003b). Popülasyon tipi Dieterich modelinde böyle bir öngörü yoktur.
- **Katalog boyutu:** Günlük gelgit korelasyonunu saptamak için 10³–10⁴'ten fazla olay gerekir (Beeler & Lockner 2003: >13.000).

### Cited Findings

**Laboratuvar ve kuram (Beeler & Lockner 2003)**
- Periyot karakteristik süre t_n'yi aşarsa korelasyon eşik (Coulomb) modeliyle tutarlıdır. Periyot t_n'den kısaysa çok daha yüksek genlik gerekir. t_n, nükleasyon süresidir.
- Günlük gelgitle korelasyonu saptamak için ">13.000 deprem" gerekir.
- San Andreas sisteminde tipik minimum nükleasyon süresi ~1 yıl.
- Kaynak: [Beeler & Lockner 2003, JGR 108(B8), doi:10.1029/2001JB001518](https://doi.org/10.1029/2001JB001518)

**Sonlu fay modeli (Ader, Lapusta, Avouac & Ampuero 2014)**
- 2-B sonlu rate-and-state fayda modülasyon genliği belirli bir periyot T_a'da en büyük. Daha kısa ve uzun periyotlarda yay-blok modeli öngörüsüne iner, ama geniş bir aralıkta ondan çok büyük kalır.
- T ≪ T_a'da gerilmeyle, T ≫ T_a'da gerilme hızıyla eş fazlı.
- Makul parametrelerle T_a = 1 yıl (Nepal muson modülasyonu).
- Yay-blok modeline dayanan Aσ tahminleri ciddi biçimde düşük olabilir.
- Kaynak: [Ader vd. 2014, GJI 198, 385–413, doi:10.1093/gji/ggu144](https://doi.org/10.1093/gji/ggu144)

**Analitik model (Heimisson & Avouac 2020)**
- Kısa periyotlu gerilmede sismisite hızı modülasyonu gerilme genliğiyle, uzun periyotta gerilme hızıyla ölçeklenir.
- Kısa periyotlu yükleme sırasında ortalama hız, arka plan hızı r'ye eşit.
- Model t_a'ya yakın periyotlarda geçersiz.
- Tek harmonikle yaklaşıklanırsa Aσ az tahmin edilebilir.
- Kaynak: [Heimisson & Avouac 2020, GRL 47, doi:10.1029/2020GL090827](https://doi.org/10.1029/2020GL090827)

**Tek-yama kalan-süre etkisi (Perfettini vd. 2003b)**
- Kesim periyodu T0, kararsızlığa kalan süreye eşit. Gelgit tetiklemesi çevrim sonundan önce çok olası değil. — [Perfettini vd. 2003b](https://doi.org/10.1029/2002JB001805)

**Ortalama-alan modeli (Brinkman, LeBlanc, Ben-Zion, Uhl & Dahmen 2015; tam metin)**
- Fay gerilmesi kritik gerilmeye yaklaştıkça küçük olay hızı gerilmeyi izlemeye başlar ve Schuster P değeri düşer. Bu, fayın artan duyarlılığını gösterir.
- Schuster testi: p = exp(−D²/n), en az 200 olay biriktikten sonra.
- Günlük gelgit genliği büyük deprem gerilme düşümünün:
  - <%1'i ise: P değeri büyük olayların >%90'ında >0,1, yani öngörücü değil.
  - ≳%1,2–2,5'i ise: anlamlı korelasyon olasılığı belirgin.
- Gözlenen gelgit gerilmeleri ~10³–10⁴ Pa, MPa'lık gerilme düşümünün ~%0,1–1'i. Bu, modelin istediğinden "biraz küçük". Yazarlar normal gerilme katkısının ve gerilme düşümü değişkenliğinin bu farkı kapatabileceğini öne sürüyor.
- Kaynak: [Brinkman vd. 2015, Nat. Commun. 6, 6157, doi:10.1038/ncomms7157](https://doi.org/10.1038/ncomms7157)

**Kuramı sınayan gözlemler**
- Tanaka 2010: Sumatra 2004, 2005 ve 2007 öncesinde "birkaç ila on yıl" yüksek gelgit korelasyonu, ana şoktan sonra kayboluyor. — [Tanaka 2010, GRL 37, doi:10.1029/2009GL041581](https://doi.org/10.1029/2009GL041581)
- Tanaka 2012: Tohoku-Oki 2011 öncesinde, başlangıç bölgesinde birkaç ila on yıl anlamlı korelasyon; sonrasında yok. — [Tanaka 2012, GRL 39, doi:10.1029/2012GL051179](https://doi.org/10.1029/2012GL051179)
- Ide, Yabe & Tanaka 2016: gelgit gerilmesinin büyüklük-frekans istatistiğine (b-değeri) etkisi. — [Ide vd. 2016, Nat. Geosci. 9, 834–837, doi:10.1038/ngeo2796](https://doi.org/10.1038/ngeo2796). Özet yok; sayısal sonuçlar doğrulanamadı.
- Kuramsal derleme: [Earthquake sensitivity to tides and seasons: theoretical studies, J. Stat. Mech. 2021, doi:10.1088/1742-5468/abda29](https://doi.org/10.1088/1742-5468/abda29). Yazarlar ve içerik doğrulanamadı.

### Inferences

**Genlik formülleri (çıkarım; Dieterich çerçevesi, Heimisson & Avouac 2020 ölçeklemesi)**
- Kısa periyot (T ≪ t_a): R(t)/r ∝ exp(Δτ₀·sin ωt / Aσ). Kesirsel genlik α ≈ Δτ₀/Aσ (küçük genlikte).
  - Örnek: Δτ₀ = 1–5 kPa (gelgit Coulomb) ve Aσ = 10–100 kPa → α ≈ %1–50.
  - Gözlenen zayıf korelasyonlar, etkin Aσ'nın üst uçta olduğunu ya da t_n > 1 gün olduğunu gösterir (Beeler & Lockner).
- Uzun periyot (T ≫ t_a): R/r ≈ 1 + (ωΔτ₀/τ̇)·cos ωt.
  - Örnek: yıllık Δτ₀ = 1 kPa ve τ̇ = 20 kPa/yıl → α ≈ 2π·1/20 ≈ 0,3.
  - Yani Marmara'nın yavaş seküler yüklemesi, yıllık yüklerin (deniz seviyesi, hidroloji) görece büyük modülasyon üretmesini kuramsal olarak mümkün kılar. Marmara için mevsimsel Coulomb genliği doğrulanamadı.

**Katalog boyutu (Schuster/Rayleigh, çıkarım)**
- Hız R = r(1 + α·cos φ) için beklenen D ≈ Nα/2, dolayısıyla p ≈ exp(−Nα²/4). Gerekli N = 4·ln(1/p)/α².
- p = 0,01 için:
  - α = 0,10 → N ≈ 1.800
  - α = 0,05 → ≈ 7.400
  - α = 0,03 → ≈ 20.000
  - α = 0,02 → ≈ 46.000
- Beeler & Lockner'ın ">13.000" değeri α ≈ %3–4'e karşılık gelir.
- "Zamanla artış" iddiasını sınamak için her zaman penceresinde bu N gerekir. Bu, segment ölçeğinde (ör. Ana Marmara Fayı ±10 km) tamamlılığı düşük bir kataloğu gerektirir.

**Geç çevrimde artan gelgit korelasyonu**
- Dieterich popülasyon modelinde α, Aσ ve τ̇'ye bağlıdır, çevrimdeki konuma bağlı değildir. Bu yüzden "artan korelasyon" ancak üç yoldan çıkar:
  - Etkin Aσ'nın düşmesi (ör. gözenek basıncı artışı, yani σ_eff düşüşü)
  - Ortalama-alan kritiklik (Brinkman)
  - Tek-yama kalan süre (Perfettini)
- Kuram bu nedenle bölünmüştür. Sınama, öncesi ve sonrası gelgit korelasyonunun karşılaştırılmasıyla yapılabilir.

### Gaps
- Marmara için hesaplanmış gelgit (okyanus yükü dahil) ve mevsimsel Coulomb gerilme genlikleri bu turda bulunamadı. Marmara kapalı bir deniz olduğundan okyanus yükü katkısı küçük olabilir; bu bir çıkarımdır ve doğrulanmadı.
- Brinkman vd. 2015'in yıllık periyot sonuçları yalnız Ek Malzemede (ön sonuç) ve okunmadı.

---

## Sınanabilir kuramsal öngörüler

Bayraklar:
- **0 €, şimdi**: açık veriyle bugün sınanabilir.
- **Yeni veri**: yeni ölçüm veya ağ gerekir.
- **Sınanamaz**: pratikte sınanamaz.

Açık veri sütunu yalnızca verinin varlığını belirtir. 2026 kataloğu ve Marmara GNSS verisi bu çalışmada kullanılmadı.

| # | Gözlenebilir | Öngörülen büyüklük (formül) | Zaman ölçeği | Gerekli veri | Açık veri var mı | Bayrak |
|---|---|---|---|---|---|---|
| 1 | 1999 İzmit/Düzce kaynaklı statik ΔCFF ile Marmara segmentlerinde saat ilerlemesi | Δt = ΔCFF/τ̇. τ̇ ≈ 0,02–0,033 MPa/yıl ile her 0,1 MPa → 3–5 yıl. Rate-and-state'te kalan süre ≲ t_a ise Δt ≤ T(1−e^(−Δτ/Aσ)) | Kalıcı kayma (yıllar) | Kayma modelleri, fay geometrisi, sürtünme μ′ | Evet (yayımlanmış kayma modelleri, Coulomb 3 vb.) | 0 €, şimdi (model hesabı). Ancak gerçek ilerleme doğrudan gözlenemez → Sınanamaz (olay olmadan) |
| 2 | Gerilme gölgelerinde sessizlik süresi (ör. 1999 gölgeleri, Çınarcık kuzeyi 1894 gölgesi) | Sessizlik süresi ≈ \|ΔCFF\|/τ̇. −0,2 MPa → ~10 yıl | On yıl | Tamamlılığı sabit bölgesel katalog (M≥2–2,5), ΔCFF haritası | Evet (KOERI/AFAD açık katalogları) | 0 €, şimdi |
| 3 | 1999 sonrası viskoelastik yeniden yükleme nedeniyle gölgelerin pozitife dönmesi (Gemlik, Mudanya) ve Silivri'de artış | Viskoelastik ΔCFF (hakemli değer doğrulanamadı). Hız oranı R/r ≈ τ̇(t)/τ̇_r | τ_M ≈ 4–11 yıl (kısa), ≥100–200 yıl (uzun bileşen) | Katalog + Burgers reolojili model | Katalog evet. Model girdileri yayımlanmış (Hearn 2009, DeVries 2016) | 0 €, şimdi (geriye dönük sınama) |
| 4 | Marmara çevresinde arka plan sismisite hızının 1999 öncesi seviyeye göre bozunan bir yükselişi | R/r ≈ 1 + ΔCFF_ve-hızı/τ̇. 2026'da ek hız katkısı seküler hızın yalnız ~%3'ü olabilir (örnek hesap) | 1999 → ~2030 bozunum | 1990'lardan beri tamamlılık değişimi düzeltilmiş katalog | Kısmen (eski katalogların tamamlılığı sorunlu) | 0 €, şimdi (düşük güç) |
| 5 | Gerinim hızının geç çevrim değişimi (Maxwell τ0 ≫ 1 ise yavaşlama) | KAF'ta ~0,5 μstrain/yıl, ~10 yıldan sonra sabit (Hussain 2018). Kuramsal geç çevrim değişimi ≈ 0 (η > 10²⁰ Pa s) | Yüzyıl | Fay-yakını gerinim (Marmara'da deniz tabanı) | Kara GNSS/InSAR açık. Fay deniz altında olduğundan fay-yakını ölçüm yok | Yeni veri (deniz tabanı jeodezisi). Geç çevrim yavaşlaması fiilen sınanamaz |
| 6 | Nükleasyona bağlı derin kayma hızlanması (tek-fay rate-and-state) | Kayma hızı ∝ 1/(t_f − t). Gözlenebilir ancak son ~t_a içinde | Aylar ile yıllar arası (t_a ≈ 0,3–5 yıl, Aσ'ya bağlı) | Sürekli fay-yakını GNSS, deniz tabanı, sondaj kuyusu gerinim ölçerleri | Kısmen (kuyu ölçerler var, açıklığı doğrulanamadı) | Yeni veri |
| 7 | Gelgit (günlük) modülasyonunun geç çevrimde artması (Brinkman, Perfettini) | α ≈ Δτ₀/Aσ. Saptama için N ≈ 4·ln(1/p)/α². α = %3 → ~20.000 olay (p = 0,01) | Pencere başına yıllar | Segmente sınırlı uzun katalog + Coulomb gelgit hesabı | Katalog evet, ancak segment ölçeğinde olay sayısı muhtemelen yetersiz (doğrulanamadı) | 0 €, şimdi (taban çizgisi). Zaman trendi için → büyük olasılıkla Sınanamaz (istatistik gücü yetersiz) |
| 8 | Yıllık (mevsimsel, hidrolojik, deniz seviyesi) modülasyon | α ≈ ωΔτ₀/τ̇. Δτ₀ = 1 kPa, τ̇ = 20 kPa/yıl → ~%30 | Yıllık; birkaç on yıllık katalog | Katalog + hidrolojik ve deniz seviyesi yük modeli (GRACE, mareograf) | Evet (açık katalog, GRACE, mareograf) | 0 €, şimdi |
| 9 | Ader vd. 2014'ün rezonans periyodu T_a (maksimum modülasyon) | Makul parametrelerle T_a ≈ 1 yıl | — | Çoklu periyotta (günlük, 14 gün, yıllık) modülasyon spektrumu | Evet | 0 €, şimdi |
| 10 | KAF boyunca olaylar arası gecikme dağılımı | ~10 yıl ortalama (Stein 1997). 8,5 ± 11 yıl (DeVries 2016). Marmara'ya geçiş "onlarca yıl" (Pondard 2007) | On yıl | Tarihsel katalog | Evet | 0 €, şimdi (geriye dönük). İleriye dönük sınama tek olay bekler |
| 11 | AMR / Mogi halkası (gölge dolmasının içe göçü, King & Bowman) | Moment salımında güç-yasası artışı. Hardebeck 2008'e göre istatistiksel olarak anlamsız | On yıl | Bölgesel katalog + önceden belirlenmiş bölge ve parametreler (veri uydurma yapmadan) | Evet | 0 €, şimdi. Önceden kayıtlı (preregistered) protokol şart |
| 12 | Katalogdan gerilme hızı terslemesi (Jiang vd. 2026, T-rate) | Gerilme hızı geçicisi. Genlik r varsayımına duyarlı, zamanlama kararlı | Gün ile yıl arası | Tamamlılığı yüksek katalog | Evet (açık araç ve katalog) | 0 €, şimdi |
| 13 | Fay-valf / akışkan sürü göçü (Zhu vd. 2020) | Sismojenik tabanda göç eden sürüler, √t difüzyonu (D ≈ 0,1–1 m²/s) | Aylar ile yıllar arası | Yüksek çözünürlüklü yeniden konumlanmış katalog (deniz tabanı OBS) | Kısmen | Yeni veri (deniz tabanı ağı) |
| 14 | Görünür eşik ΔCFS'ye ulaşma (DeVries 2016) | 0,02–3,15 MPa aralığı | "2023'e kadar" ortalama eşiğe ulaşılabilir (öngörü) | — | — | Sınanamaz (eşik aralığı çok geniş, tek olay) |

Genel uyarılar:
- Kuram, bir sonraki Marmara olayının zamanını yıl ölçeğinde daraltacak bir "gerinim veya sismisite hızı öncülü" öngörmez.
- Yıl ölçeğinde fiziksel olarak beklenen tek sinyal ailesi, kalan süre t_a mertebesine indiğinde ortaya çıkar: nükleasyon kayması ve küçük pertürbasyonlara artan duyarlılık. Bunların gözlenebilirliği deniz tabanı ve kuyu ölçümüne ve büyük kataloglara bağlıdır.
- Birden çok kaynak hakemsiz EGU özetidir (Nalbant vd. 2026, Utkucu vd. 2023). Hakemli sonuçlarla aynı ağırlıkta kullanılmamalıdır.
