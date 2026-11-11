# VE-1 ön kayıt taslağı: bağımsız inceleme 2

İncelenen: `kayit/onkayit/VE-1_gnss-hiz-degisimi_TASLAK-2.md` (11 Kasım 2026). Karşılaştırma: `VE-1_INCELEME-1.md`, `VE-1_gnss-hiz-degisimi_TASLAK.md`, `kayit/kollar/VE.md`.
İnceleyici: bağımsız ajan (ikinci tur). Taslağı ben yazmadım. 2017+ GNSS serilerini, NGL istasyon sayfalarını ve grafiklerini açmadım. İnternete yalnız Crossref'te beş DOI'nin yayım tarihini doğrulamak için çıktım.
Tarih: 11 Kasım 2026.

## Hüküm: **DÜZELT-SONRA-KABUL**

TASLAK-2 tasarımın iskeletini düzeltti. Model seçimi kalktı, Özarpacı 2021 ve Hussain 2018 düştü, istasyon listesi üstveriden donduruldu, hedef pencere Kahramanmaraş'tan önce bitiyor ve anlamlılık artık parametrik. Ama dört yerde metin hâlâ dondurulamaz:
1. Hüküm kuralı tek değil. 0,5–0,8 güç bandındaki "yalnız üst sınır" kuralı üç hükümle çelişiyor. "H0 yönünde" tanımı, iki hipotezin de reddedildiği durumda yanlış etiket veriyor (Y1, Y2).
2. Model parametreleri taslakta yok. "Tercih edilen set" ve "geometrik orta" kuralı sayılar yazılmadan uygulanamaz, M3'te "ya da" serbestliği kalmış, afterslip'in nasıl hesaplanacağı belirsiz (Y3–Y6).
3. Birinci tür hata ölçümü, kurulduğu biçimiyle kendi kendini doğruluyor (Y8).
4. Atım kuralında 90 gün dışlamasının kapsamı belirsiz, 2022-11-23 Düzce M5,9 olayı hedef penceredeyken listede yok. Çerçeve ile üstveri kaynağının uyumu da doğrulanmamış (Y10, Y11).

Bunların hepsi metin düzeltmesiyle kapanır, yeni bir tasarım gerekmiyor. Koşul: Y1–Y4, Y6, Y8, Y10, Y11 ve Y13 düzeltilsin. Y3'teki parametre tablosu dondurmadan önce kısa bir üçüncü bakıştan geçsin; tam inceleme gerekmez. Ancak bundan sonra DONDUR + OTS.

---

## Eski yüksek bulguların durumu

| # | Konu | Durum | Gerekçe |
|---|---|---|---|
| B1 | En iyi H1 seçimi | **kapandı** (koşullu) | Seçim yok, tek birincil tahmin var: μ_karışım. Koşul: karışıma giren model kümesi güç testinden **önce** donmalı (Y5). Karışım, yoğunluk karışımı yerine ortalamaların ortalaması olarak kurulmuş. Bu kabul edilebilir, ama C_model modeller arası yayılımı içermiyor (Y7). |
| B4 | Özarpacı 2021 | **kısmen** | Özarpacı dışarıda (doğru). Ama yerine gelen M3 "Ergintav 2009 **ya da** Hearn 2009" diye bırakılmış, yani kaynak seçimi serbest. Afterslip'in uzamsal dağılımı ve hesaplama aracı da yazılmamış (Y4, Y6). |
| B5 | Hussain 2018 | **kapandı** | Model girdisinden çıktı, körlük beyanında. M2 yalnız Yamasaki 2014'e dayanıyor. |
| B6 | Parametre aralıkları, ileri model | **kısmen** | Tek araç (PSGRN/PSCMP) ve tek set kuralı yazılmış. Açık kalanlar: sayılar, tablo numaraları, tek yönlü sınırlar ("≥ 2×10^20"), elastik katman yapısı, PSGRN/PSCMP sürümü, hangi DeVries makalesi, hash'lenecek dosyalar (Y3, Y4, Y6). |
| B8 | İstasyon seçimi N'yi eziyor | **kapandı** (Y11 şartıyla) | Liste üstveriden çıkarılıp adlarıyla yazılmış, N = 11, doluluk ölçütü kaldırılmış. Ancak üstverinin hangi çerçeve dosyasından okunduğu belirsiz (Y11). |
| B10b | Atım çelişkisi, 2023 kirlenmesi | **kısmen** | Hedef pencere 2023-02-05'te bitiyor, "ek atım yok" çelişkisi gitti. Açık kalanlar: tekilleştirme penceresi, 90 gün dışlamasının kapsamı, 2022 Düzce olayı, aykırı değer kuralı, belgelenmemiş sıçrama kuralı (Y10). |
| B13 | Güç testinde gürültü, korelasyon, 1. tür hata | **kısmen** | Korelasyon C_obs'a girdi, 1. tür hata ölçülüyor. Açık kalanlar: rastgele yürüyüş senaryosu yok; sentetik serilerin korelasyonlu üretileceği ve atım terimlerinin sentetik uydurmaya konacağı açıkça yazılmamış; 1. tür hata ölçümü tasarımı gereği ≈0,05 çıkar (Y8, Y9). |
| B16a | İstasyon bootstrap'ı | **kısmen** | Parametrik p ve tam kovaryans geldi, bootstrap bilgi satırına indi. Ama gürültü genliklerinden ve aylık korelasyondan 22×22'lik Δv kovaryansına nasıl geçileceği yazılmamış (Y9). |
| B16 | Körlük beyanı | **kısmen** | Özarpacı, Hussain, ISTA ve üstveri eklendi. Eksikler: ISTA dosyasının akıbeti, de Blas 2022, Nalbant 2026, DeVries 2016'nın "2023'e kadar" ifadesi, ajanların genel literatür bilgisi, koşuyu kimin yapacağı, NGL istasyon sayfası grafiklerine bakılıp bakılmadığı (Y13). |

Orta önemli eski bulgulardan açık kalanlar (yeniden incelemeyi engellemez ama Y maddelerine bağlandı):
- **B7**: model Δv'sinin gözlemle aynı tahminciden geçmesi yazılmamış (Y6).
- **B9**: kutu ve "28 istasyon" AV.md ile hâlâ uyuşmuyor. IGS14'te kalınmış (Y11).
- **B12**: gürültü kestirim aracı (HECTOR mı, başka mı) ve spektral indeks seçimi yazılmamış (Y9).
- **B14**: 0,5–0,8 bandı hâlâ çelişkili (Y1).
- **B19**: model bağımsız değişim testi eklenmemiş. Bu eksiklik artık Y2'nin kökü.
- **B20**: Silivri büyüklüğünün kaynağı ve 90 gün / 100 km eşiklerinin gerekçesi yazılmamış.

Kapananlar: B2 (bootstrap birincil değil, konu düştü), B10a (ham çerçeve, ortak kip yok; seçim yapılmış), B11 (pencere açık yazılı), B17, B18 (VE-3 nat sayısı ve PIF/CMF cümlesi çıkmış; "Bu sınav ne değildir" bölümü iyi).

---

## Crossref doğrulaması (11 Kasım 2026)

| Makale | DOI | İlk çevrimiçi | Kapı |
|---|---|---|---|
| Hearn 2009, JGR | 10.1029/2008jb006026 | 2009-08-25 | geçer |
| Ergintav 2009, JGR | 10.1029/2008jb006021 | 2009-07-09 | geçer |
| Yamasaki 2014, JGR | 10.1002/2013jb010347 | 2014-04-17 | geçer |
| DeVries 2016, G3 | 10.1002/2016gc006313 | 2016-07-17 | geçer |
| DeVries 2016, BSSA | 10.1785/0120160059 | 2016-11-29 (baskı 2017-02) | "ilk çevrimiçi" kuralıyla geçer |

Dördü de tarih kapısından geçiyor. Taslaktaki "DeVries 2016 ancak tarih kapısından geçerse (M4)" koşulu bu yüzden boş, ama hangi DeVries makalesinin kastedildiği belirsiz (Y4). Veri penceresi açısından Ergintav 2009 (1999–2006 GPS) ve Hearn 2009 gözlemleri 2017'den çok önce bitiyor. DeVries 2016'nın uydurduğu GNSS hızlarının son epoğunu tam metinden doğrulamadım. Yayım tarihi 2016 olduğu için < 2017 olmak zorunda; bu yeterli.

---

## Yeni bulgular

### A. Hüküm kuralı

**Y1 (yüksek): 0,5–0,8 güç bandındaki kural, üç hükümlü kuralla çelişiyor.**
Hüküm satırı üç hüküm tanımlıyor. Ateşleme kapısı ise 0,5–0,8 bandında "sonuç önceden 'yalnız üst sınır' diye ilan edilir" diyor. Bu bantta L > 0 ve p < 0,05 çıkarsa ne yazılacağı belirsiz: "H1 yönünde" mi, "üst sınır" mı? Bu, sonuçtan sonra seçilebilecek bir serbestlik. Ayrıca "Sonuç ne olursa" bölümü üst sınırı yalnız "ayırt edilemez" için tanımlıyor.
Düzeltme metni: "Güç 0,5–0,8 ise hüküm kuralı aynen uygulanır ve üç hükümden biri yazılır. Hükmün yanına 'düşük güç' etiketi eklenir. Bu bantta 'H1 yönünde' sonucu K10 şart önerisinin jeodezik maddesini sağlamış sayılmaz. 'H0 yönünde' ve 'ayırt edilemez' sonuçları yalnız α üst sınırı olarak yorumlanır (bkz. Y2)."

**Y2 (yüksek): "H0 yönünde" tanımı, iki hipotez de uymadığında yanlış etiket verir; "üst sınır" tanımsız.**
Tanım şöyle: "L < 0 ve H1 altındaki simülasyonda p < 0,05". Bu yalnız H1'in reddi demek, H0'ın desteklendiği anlamına gelmez. Gözlenen Δv, μ_karışım'ın tersi yönde büyük çıkarsa, ya da modellerin öngörmediği bir desende çıkarsa, L < 0 olur ve H1 reddedilir. Bu durumda hüküm "H0 yönünde" çıkar, oysa H0 da (Δv = 0) kötü uyuyor. Simetrik bir sorun da var: Δv, μ_karışım'ın birkaç katıysa L > 0 ve p < 0,05 çıkar, hüküm "H1 yönünde" olur, ama model öngörüsü de reddedilir. "H1 altındaki simülasyon"un hangi dağılımdan çekileceği de yazılmamış: N(μ, C_obs) mı, N(μ, C_obs + C_model) mi? Son olarak "üst sınır"ın hangi nicelik için yazılacağı belirsiz.
Düzeltme metni (hüküm satırının yerine):
> L = ln N(Δv; μ_karışım, C_obs + C_model) − ln N(Δv; 0, C_obs).
> p₀ = P(L* ≥ L | H0), L* için Δv* ~ N(0, C_obs), 10.000 çekiliş.
> p₁ = P(L* ≤ L | H1), L* için Δv* ~ N(μ_karışım, C_obs + C_model), 10.000 çekiliş.
> Uyum denetimleri: χ²₀ = Δvᵀ C_obs⁻¹ Δv; χ²₁ = (Δv − μ)ᵀ (C_obs + C_model)⁻¹ (Δv − μ); 22 serbestlik derecesi, her biri için q₀, q₁ p değerleri.
> - **H1 yönünde:** p₀ < 0,05 ve q₁ ≥ 0,01.
> - **H0 yönünde:** p₁ < 0,05 ve q₀ ≥ 0,01.
> - **İkisi de uymuyor:** p₀ < 0,05 ya da p₁ < 0,05, ama ilgili uyum denetimi < 0,01. Bu dördüncü ayrı hükümdür: "veri değişti ama ≤2016 modelleri bunu öngörmüyor".
> - **Ayırt edilemez:** öteki her durum.
> Üst sınır: Δv = α·μ_karışım + ε, ε ~ N(0, C_obs) modelinde α'nın en çok olabilirlik kestirimi ve tek yönlü %95 güven aralığı. "Ayırt edilemez" ve "H0 yönünde" hükümlerinde α'nın %95 üst sınırı yazılır.

Uyum eşiğini 0,01 önerdim, çünkü uyum denetimi hüküm satırının yanında ikincil bir korumadır. Yazar başka bir eşik seçebilir, ama sayı dondurmadan önce yazılmalı. Güç testi bu dört hükümlü kuralın tamamını simüle etmeli.

### B. Model sızıntı kapısı ve ileri model

**Y3 (yüksek): Parametre sayıları ön kayıtta yok; "tercih edilen set" seçimi dondurmaya ertelenmiş.**
Taslak, sayıların "dondurma dosyasına" yazılacağını söylüyor. Bu durumda seçim incelenmeden yapılır. VE.md'deki sayılar özetten alınmış, tam metin okunmamış (VE.md, "Dürüst sınır"). Özetten kaynaklanan serbestlikler:
- Hearn 2009: "kalıcı ≥ 2×10^20 Pa s" tek yönlü bir sınır. Geometrik orta tanımsız. "Tek değer çıkarılamayan model düşer" kuralı sonuçtan sonra iki yönlü de okunabilir.
- Burgers modeli viskozitelerin yanında başka parametreler de ister: Kelvin/Maxwell kayma modülü oranı, viskoz katmanın derinliği ve kalınlığı, elastik üst kabuk kalınlığı. "Tercih edilen set" bunların hepsini kapsamalı.
- Hearn 2009'un birden çok modeli var (afterslip + manto, zayıf alt kabuk vb.). Hangisinin "tercih edilen" olduğu tam metinden okunmalı.
Düzeltme metni: "Ek 1 tablosu: her model için tam parametre vektörü (her parametre için sayı, birim, makale sayfası/tablo/şekil numarası). Tek yönlü sınır verilen parametre için makalenin ileri modelde kullandığı değer alınır. Böyle bir değer yoksa sınır değerin kendisi alınır. Tablo dondurmadan önce inceleyiciye gösterilir; SHA-256 ile ön kayda bağlanır." Tablo dolmadan DONDUR yapılmaz.

**Y4 (yüksek): Model kümesinde "ya da" ve "ancak" serbestlikleri.**
- M3 "Ergintav 2009 **ya da** Hearn 2009'un afterslip bileşeni": bu iki kaynaktan biri sonradan seçilebilir. Bir tane seçilsin. Önerim Ergintav 2009 (10.1029/2008jb006021, 2009-07-09), çünkü 7 yıllık afterslip zaman serisini doğrudan veriyor. Hearn bilgi satırına gitsin.
- M4 "DeVries 2016": G3 mi, BSSA mı belirsiz. İkisi de kapıdan geçiyor. Biri seçilsin. Önerim G3 (10.1002/2016gc006313), çünkü BSSA'daki blok modeli yapısı PSGRN/PSCMP ile kurulamaz.
- DeVries modelleri 1939–1999 dizisinin tamamıyla kalibre edilmiş. Yalnız 1999 kaynaklarıyla koşulursa model makaledekiyle aynı olmaz. Yazılsın: kaynaklar yalnız 1999 İzmit ve Düzce mi, yoksa 1912–1967 depremleri de giriyor mu? Önerim yalnız 1999. Daha eski olayların 2009–2023 arasındaki hız değişimine katkısı, düşük viskozitede küçük ama sıfır değildir; bu bilgi satırında verilsin.
- M2 (Yamasaki 2014): makale fayın altında yanal olarak sınırlı bir zayıf zon kullanıyor. PSGRN/PSCMP yalnız yatay katmanlı (1B) yapı kurar, yanal heterojenlik kuramaz. Bu bildiğime göre kesin. Yani M2 neredeyse kesin düşer. Taslak "kurulamıyorsa düşer" diye bırakmamalı, "M2 düşer" diye yazmalı. Böylece karışımın üyeleri güç testinden önce bellidir.

**Y5 (orta): Karışımın üyeleri güç testinden önce donmalı.**
Model düşürme kararı güç sonucuna bakılarak verilirse güç kapısı aşılabilir (μ_karışım büyür). Düzeltme metni: "Karışımdaki modeller ve parametre tablosu, sentetik güç testi koşulmadan önce SHA-256 ile kayda geçer. Güç testinden sonra model eklenmez ve çıkarılmaz."

**Y6 (yüksek): Afterslip nasıl hesaplanacak; model Δv'si hangi tahminciyle elde edilecek (B7 açık)?**
- PSGRN/PSCMP'nin viskoelastik Green fonksiyonları Maxwell, SLS ve Burgers gövdelerini destekler. Bildiğim kadarıyla Burgers 2008 ve sonraki sürümlerde var; kullanılan sürüm adı ve sürüm numarasıyla yazılsın. Afterslip, kinematik bir kayma geçmişidir. PSCMP'de ancak zamana yayılmış alt olaylarla (farklı başlangıç zamanlı kayma artımları) ya da elastik Green fonksiyonu × zaman fonksiyonu olarak kurulabilir. Taslak bunu yazmıyor.
- Afterslip'in uzamsal dağılımı SRCMOD'dan değil, afterslip makalesinden gelir. Taslaktaki "Kaynak: SRCMOD ortalaması" cümlesi M3 için yanlış ya da çelişkili.
- Model Δv'si gözlemle **aynı tahminciden** geçirilmeli: aynı epoklar, boşluklar, atım terimleri ve pencereler.
- Elastik katman yapısı yazılmamış: makaledeki mi, CRUST1.0 mı?
Düzeltme metni:
> "İleri model PSGRN/PSCMP sürüm [X]; elastik yapı her model için kendi makalesindeki katmanlar (Ek 1). Viskoelastik modellerde (M1, M4) kaynak 1999 İzmit ve Düzce için SRCMOD kaymalarıdır; M3'te kaynak, Ergintav 2009'un afterslip dağılımı × makaledeki logaritmik zaman fonksiyonudur (elastik Green fonksiyonu). Her model, her istasyonda gözlemle aynı günlük epoklarda yer değiştirme serisi üretir. Bu seriye gözlemle aynı en küçük kareler tahmincisi (aynı atım ve mevsimsel terimler, aynı dışlanan günler, aynı pencereler) uygulanır; model Δv'si budur."

Ek olarak, ön kayıtlı bir doğrulama adımı önerilir. Yeniden kurulan her model, kendi makalesinde yayımlanmış bir ≤2016 gözlem uyumunu (ör. Ergintav 2009'daki bir istasyon zaman serisi ya da Hearn 2009'daki bir hız profili) önceden yazılmış bir toleransla yeniden üretsin. Üretemeyen model düşsün. Bunun nedeni: 1B katmanlı yeniden kurulum, makaledeki modelin kendisi değildir. Bu adım yalnız ≤2016 veri kullanır, körlüğü bozmaz.

**Y7 (orta): C_model modeller arası yayılımı dışarıda bırakıyor.**
C_model yalnız SRCMOD kaynaklarının yayılımı olarak tanımlı. μ_karışım ise modellerin ortalaması. Modeller birbirinden çok farklı öngörürse (ör. M3 0,6 mm/yıl, M1 0,05 mm/yıl), karışımın ortalaması dar bir varyansla tek bir orta değere kilitlenir. Böylece hiçbir modelin öngörmediği bir değer "tahmin" olarak ilan edilir.
Düzeltme metni: "C_model = (model × SRCMOD kaynağı) kombinasyonlarının tamamı üzerinde μ'nün örnek kovaryansı; modeller eşit ağırlıklı, her model içinde kaynaklar eşit ağırlıklı." Ya da açık bir Gauss karışım yoğunluğu: p_H1 = (1/K) Σ N(μ_k, C_obs + C_k). Hangisi seçilirse güç testi o yoğunlukla koşulsun.

### C. C_obs, güç kapısı, körlük

**Y8 (yüksek): Birinci tür hata ölçümü tasarımı gereği ≈0,05 çıkar; 0,07 eşiği gevşek.**
Sentetik seriler "bu serilerin gürültü modeliyle" üretiliyor. p değeri de aynı gürültü modelinden türetilen C_obs'la hesaplanıyor. Model kendisiyle sınandığında birinci tür hata Monte Carlo hatası içinde 0,05 çıkar. Bu ölçüm, gürültü modelinin yanlış kurulmasını (rastgele yürüyüş, spektral indeks, ortak kip yapısı, aylık korelasyonun düşük frekansta yanlış olması) **yakalayamaz**. Asıl risk de budur.
1.000 tekrarda 0,05'in standart hatası ≈0,007. 0,07 eşiği, gerçek oranı 0,065–0,07 olan bir kuralı geçirir.
Düzeltme metni:
> "Birinci tür hata, gürültü modelinden bağımsız bir üreteçle ölçülür: 2009–2016 artıklarından, tüm istasyonlarda aynı takvim bloklarıyla (blok uzunluğu 365 gün) dairesel blok bootstrap ile hedef uzunlukta sentetik artık serileri üretilir; uzamsal korelasyon ve renkli gürültü böylece korunur. 2.000 tekrar; eşik ≤ 0,065. Ek senaryo: parametrik üreteç + 1 mm/√yıl rastgele yürüyüş; güç ve birinci tür hata kötü senaryoya göre karar verir (B13-i). Tohumlar yazılır."

2009–2016 serisi yaklaşık 8 yıl, hedef yaklaşık 6 yıl. Bu yüzden blok bootstrap için yeterli malzeme var. Rastgele yürüyüş senaryosu TASLAK-2'de kaybolmuş; geri gelsin.

**Y9 (orta): C_obs'un Δv uzayına taşınması tanımsız.**
"Beyaz + titreşim genlikleri" ve "aylık ortalamaların korelasyonu (Ledoit–Wolf)" tanımlanmış. Bunlardan 22×22'lik Δv kovaryansının nasıl hesaplanacağı yazılmamış. Aylık artıkların korelasyonu, eğim (düşük frekans) korelasyonuyla aynı değildir. Ayrıca şunlar açık: doğu–kuzey çapraz korelasyonu dahil mi; Ledoit–Wolf hedef matrisi ne; gürültü kestirim aracı, sürümü ve spektral indeks seçimi (−1'e sabit mi, serbest mi).
Düzeltme metni: "C_obs, gürültü modelinden (istasyon içi beyaz + güç yasası, spektral indeks [sabit −1 / serbest]; [araç, sürüm]) ve istasyonlar arası korelasyon matrisinden (doğu ve kuzey birlikte, 22×22, Ledoit–Wolf, hedef = birim korelasyon) üretilen 10.000 korelasyonlu sentetik seri kümesine gözlem tahmincisinin uygulanmasıyla elde edilen Δv'lerin örnek kovaryansıdır. Her istasyonun gerçek taban ve hedef pencere uzunluğu ile 2009–2016 boşluk deseni kullanılır." Böylece eşit olmayan hedef uzunlukları (2022-11 ile 2023-02 arasında biten istasyonlar) kendiliğinden hesaba girer; bu bir sorun değil, yeter ki yazılsın.

**Y10 (yüksek): Atım kuralı hâlâ eksik; 2022 Düzce hedef penceresinin içinde.**
- **2022-11-23 Düzce Mw ≈5,9** (≈40,84° K, 31,0° D) hedef penceresinin içinde, bitişten 74 gün önce. HEND, SARY ve muhtemelen IZMT ve BILE ≈100 km içinde. Kural "olaydan sonraki 90 gün o istasyonda dışarıda" diyor. Uygulanırsa bu istasyonların hedef penceresi fiilen 2022-11-22'de biter. Uygulanmazsa atım 74 günlük veriden kestirilir ve Δv'ye sızar. Taslak olayı adıyla anmıyor. Yalnız steps.txt'ye bırakmak, bu kritik olayın işlenişini dosyaya bırakmak demek.
- **2020-10-30 Sisam Mw 7,0**: kutunun ≈250–400 km güneyinde. Uzak alan atımı muhtemelen mm altı ile birkaç mm arası; emin değilim. NGL'nin yarıçap kuralına göre (inceleme 1'de verdiğim yaklaşık formül, M7 için ≈500 km) steps.txt'de büyük olasılıkla var. Yine de açıkça anılsın.
- Taban dönemde **2011-05-19 Simav M5,9** (39,1° K, 29,0° D): BURS ≈120 km uzakta. steps.txt'ye bırakılabilir, ama anılsın.
- 2014 Kuzey Ege için "< 100 km" kuralı listedeki hiçbir istasyonu kapsamaz (en yakını ≈150 km'den uzak, TEKR ya da yakını). Yani kural fiilen boş. Atım steps.txt'den gelir. Bu da yazılsın, aksi halde "atım eklenmedi" sanılır.
- "Tekilleştirilmiş" kaç günlük pencereyle? (±2 gün önerilmişti.)
- 90 günlük dışlama hangi istasyonlara uygulanacak: kural 100 km ile eklenen atımlara mı, steps.txt'deki her deprem atımına mı? Önerim: deprem atımı olan ve merkez üssüne < 100 km olan istasyonlar.
- Aykırı değer ve belgelenmemiş sıçrama kuralı yok (inceleme 1 B10b'de istenmişti).
Düzeltme metni:
> "Atım listesi = steps.txt (SHA-256, indirme tarihi) ∪ {2011-05-19 Simav, 2014-05-24 Kuzey Ege, 2019-09-26 Silivri, 2020-10-30 Sisam, 2022-11-23 Düzce}; ±2 gün içindeki yinelenenler tek atım sayılır. Olaydan sonraki 90 günlük dışlama, merkez üssüne < 100 km olan istasyonlarda uygulanır; dışlama hedef pencerenin sonuna taşıyorsa (2022 Düzce) o istasyonun hedef penceresi olay gününden bir gün önce biter ve olay atımı kestirilmez. Aykırı değer: tek tur, artık > 5×MAD olan günler çıkarılır. Belgelenmemiş sıçramalar için atım eklenmez ve istasyon dışlanmaz."
Bu kural, modelin ve C_obs'un aynı pencerelerle hesaplanmasını gerektirir (Y6, Y9).

**Y11 (yüksek): Çerçeve ile üstveri kaynağının uyumu doğrulanmamış.**
- Taslak IGS14 tenv3 kullanıyor. AV.md ise envanteri **IGS20** tenv3 üzerinden çıkarmış ve 28 istasyonun 25'inin Ocak 2024'te bittiğini yazmış. TASLAK-2'deki istasyonların bir kısmının bitişi 2022-11 ile 2023-01 arası.
- Bu fark, iki ayrı DataHoldings dosyasının (IGS14 ve IGS20) karıştırıldığını düşündürüyor. NGL'nin IGS14 ürününün 2023 dolaylarında durdurulmuş olabileceğini düşünüyorum; emin değilim. Durdurulduysa "bitiş" tarihleri istasyonun kapanmasını değil, ürünün bitişini gösterir.
- Kutu ve "28 istasyon" sayısı AV.md ile hâlâ uyuşmuyor (B9).
- Hangi çerçeve seçilirse seçilsin, istasyon listesi **o çerçevenin** DataHoldings dosyasından gelmeli.
Düzeltme metni: "Çerçeve: [IGS14 | IGS20]; tenv3 yolu: [tam yol]; istasyon listesi bu çerçevenin DataHoldings dosyasından (URL, indirme tarihi, SHA-256) çıkarılmıştır. Kutu: [tek tanım]; kutu içindeki istasyon sayısı: [sayı, bu dosyadan]." Liste değişirse N ve güç yeniden hesaplanır. Bu adım yalnız üstveriyle yapılır, körlüğü bozmaz.

**Y12 (orta): "2017-01-01'de kesilerek okuma" körlüğü yalnız yordamsal olarak koruyor.**
Tam dosya ağ üzerinden analiz yapan sürecin belleğine giriyor. Hata iletileri, günlükler, ara bellek ya da bir yazım hatası 2017+ satırları açığa çıkarabilir. Kesme kodunu yazan ile analizi yapan aynı ajan olursa koruma yalnız beyana dayanır. NGL istasyon sayfalarındaki zaman serisi grafikleri de serinin tamamını gösterir.
Düzeltme metni: "Kesme işlemini analizi yapmayan ayrı bir ajan/oturum yapar. Kesilmiş dosyaları SHA-256 ile kayda geçirip analiz dizinine koyar; tam dosyayı silindiğini beyan ederek siler. Analiz ajanı NGL istasyon sayfalarını ve grafiklerini açmaz. 2017+ açılışı, güç kapısı geçildikten sonra aynı ajanın ayrı bir adımla yaptığı tek bir indirmedir." Kesme süzgeci tarih sütununa göre çalışmalı, `< 2017-01-01` koşuluyla ve satır sayısı denetimiyle. tenv3'te ondalık yıl sütunu yuvarlama sorunu yaratabilir, YYMMMDD sütunu kullanılsın.

**Y13 (yüksek): Körlük beyanında eksikler sürüyor.**
Eklensin:
- (i) AV kolunun indirdiği ISTA dosyasının durumu: silindi mi, mühürlendi mi, nerede? ISTA'nın "ISTA dahil" ve "2017–2026" bilgi satırlarında kullanılması, görülmüş veriyle yapılan bir hesap olarak etiketlensin.
- (ii) de Blas 2022 (Anadolu rijit hareketi 1999'la değişti iddiası) ve Nalbant 2026 bilgisi.
- (iii) DeVries 2016 G3'ün "2023'e kadar eşik" ifadesi biliniyor (VE.md Soru 1). M4 bu makaleden geliyorsa bu, modelin yazarlarının ileriye dönük bir ifadesinin bilindiği anlamına gelir.
- (iv) Taslak yazarının ve iki inceleyicinin 2017–2023 Marmara GNSS sonuçlarına dair genel literatür bilgisi sıfır değil. Ayrıntılı sayı hatırlamıyorum, bu da yazılsın.
- (v) Koşuyu kimin yapacağı ve o kişinin/ajanın 2017+ serilere ya da NGL grafiklerine daha önce bakıp bakmadığı.
- (vi) Liste eşiklerinin (başlangıç ≤ 2009-01-16, bitiş ≥ 2022-11-01) N görülerek seçildiği. Bu sızıntı değil, ama yazılsın.
- (vii) Kahramanmaraş 2023'ün uzak alan etkisine dair bilgi (pencere dışında kaldığı için kısa bir not yeter).

### D. Yanlış okunabilecek cümleler

**Y14 (orta): "H1 yönünde çıkarsa: K10 şart önerisinin jeodezik maddesi sağlanmış sayılır".**
VE.md madde 2 şunu istiyor: "en az bir model ... istasyon-bootstrap %95 alt sınırı > 0". TASLAK-2 ise karışım ve parametrik p kullanıyor. Şart metni değişmeden "sağlanmış sayılır" demek yanlış. Aynı cümlenin devamı ("şartın kendisi yeniden yazılmalıdır") ilk yarıyla çelişiyor.
Düzeltme metni: "'H1 yönünde' (güç ≥ 0,8) çıkarsa bu, K10 şart önerisinin jeodezik maddesinin bu ön kayda göre yeniden yazılmış biçimini sağlar; yeniden yazım ve K10 kararı Erdem'indir. Mevcut madde metni (en iyi model + bootstrap) bu sınavla sınanmamıştır."

**Y15 (düşük): "model öngörüleri Avrasya sabit çerçevede aynı istasyon farklarıyla karşılaştırılır".**
"İstasyon farkları" ifadesi istasyonlar arası farklama diye okunabilir. Oysa kastedilen dönemler arası fark. Ayrıca sabit bir çerçeve dönmesinin Δv'de sadeleşmesi yalnız dönme zamanla sabitse doğrudur. Bu doğru bir varsayım, ama yazılsın.
Düzeltme metni: "Ortak kip çıkarılmaz. Δv iki dönemin hız farkı olduğundan, çerçevenin zamanla sabit herhangi bir dönmesi ya da öteleme hızı Δv'de sadeleşir; model öngörüleri de bu yüzden ek çerçeve dönüşümü olmadan karşılaştırılır."

**Y16 (düşük): "bir dönemde < 2 yıl verisi olan istasyon otomatik düşer".**
"Veri" günlük çözüm sayısı mı, açıklık süresi mi? Ayrıca Düzce dışlaması ve 2022-11'de biten istasyonlarla birlikte bazı hedef pencereler kısalıyor.
Düzeltme metni: "Dönem başına ≥ 730 günlük çözüm; altında kalan istasyon her iki dönemden ve modelden birlikte düşer, raporlanır; güç testi düşmemiş haliyle (11 istasyon) yapılmıştır, bu da raporlanır."

**Y17 (düşük): Tohum, 10.000/1.000 çekiliş sayıları ve hash listesi.**
Tohumlar, karışım üyeleri dosyası, parametre tablosu, steps.txt, DataHoldings, istasyon listesi ve kod için hash listesi tek yerde yazılsın (B20).

---

## Özet tablo

| # | Konu | Önem |
|---|---|---|
| Y1 | 0,5–0,8 bandı üç hükümle çelişiyor | yüksek |
| Y2 | "H0 yönünde" tanımı; dördüncü hüküm; üst sınır tanımı | yüksek |
| Y3 | Parametre sayıları ön kayıtta yok | yüksek |
| Y4 | M3 "ya da", M4 hangi DeVries, kaynak olaylar, M2 kesin düşer | yüksek |
| Y5 | Karışım üyeleri güç testinden önce donmalı | orta |
| Y6 | Afterslip hesabı ve aynı tahminci (B7) | yüksek |
| Y7 | C_model modeller arası yayılımı içermiyor | orta |
| Y8 | 1. tür hata ölçümü kendini doğruluyor; eşik 0,07 gevşek; rastgele yürüyüş kayıp | yüksek |
| Y9 | C_obs → Δv kovaryansı ve gürültü aracı tanımsız | orta |
| Y10 | Atım: 2022 Düzce, 90 gün kapsamı, tekilleştirme, aykırı değer | yüksek |
| Y11 | IGS14 / IGS20 ve DataHoldings uyumu | yüksek |
| Y12 | Kesme körlüğü yalnız yordamsal | orta |
| Y13 | Körlük beyanında eksikler | yüksek |
| Y14 | K10 "sağlanmış sayılır" cümlesi | orta |
| Y15 | Çerçeve cümlesi | düşük |
| Y16 | "< 2 yıl veri" tanımı | düşük |
| Y17 | Tohum ve hash listesi | düşük |

Dondurma şartı: Y1–Y4, Y6, Y8, Y10, Y11 ve Y13 metne işlensin. Y3 parametre tablosu dondurmadan önce kısa bir üçüncü bakıştan geçsin. Orta ve düşük maddeler aynı turda düzeltilmeli, ama tek başlarına dondurmayı engellemez.
