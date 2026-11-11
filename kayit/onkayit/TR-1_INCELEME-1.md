# TR-1 ön kayıt: bağımsız inceleme 1

İncelenen: `TR-1_kuresel-gnss-hiz-degisimi_ONKAYIT.md` (TASLAK, 11 Kasım 2026). İnceleme tarihi: 11 Kasım 2026.
Olay pencerelerine ait hiçbir GNSS serisi indirilmedi ya da işlenmedi. Yapılan doğrulamalar yalnız olaydan bağımsız
dosyalarla yapıldı: NGL `steps.txt`, `DataHoldings.txt`, `llh.out`, bir kontrol amaçlı örnek dosya (P123, ABD, olaysız) ve
ComCat sayım/katalog sorgusu. Uygunluk tahmini yalnız istasyon üstverisiyle (başlangıç/bitiş tarihi, basamak listesi)
yapıldı; hiçbir hız ya da S değeri hesaplanmadı.

## Hüküm: RED (bu metinle dondurulamaz). 1–4 düzeltilip yeniden incelenirse kabul edilebilir.

Gerekçe tek cümle: yazıldığı hâliyle (a) kod 2 kuralı uygun olay sayısını ~3'e düşürdüğü için sonuç önceden "güç yok"tur,
(b) kontrol tasarımı öncül olmadan da r > 0,5 üretecek bir yanlılık taşır ve bunu hiçbir denetim yakalamaz; dolayısıyla
H1 çıksa bile yorumlanamaz. İkisi de tasarım düzeyinde, K'yi değiştirir; bu yüzden ikinci inceleme gerekir.

## Doğrulama notları (olaydan bağımsız)

- NGL dizini: `https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{STA}.tenv3` çalışıyor (P123: HTTP 200, 1,5 MB,
  ~20 yıl). `.../tenv3/IGS20/` altında levhaya sabitli dizinler de var (AF, AN, AR, AU, EU, IN, ...). Eski kalıp
  `gps_timeseries/tenv3/IGS14/` 404 veriyor. Dosyalar her gün yeniden yazılıyor (dizin tarihi bugün).
- tenv3 sütunları: `site YYMMMDD yyyy.yyyy __MJD week d reflon e0 east n0 north u0 up ant sig_e sig_n sig_u corr_en
  corr_eu corr_nu lat lon height`; birim metre.
- `steps.txt`: kod 1 satırları 4 alan (`STA YYMONDD 1 açıklama`), kod 2 satırları 7 alan
  (`STA YYMONDD 2 eşik_km uzaklık_km M olay_kimliği`). Tarih iki basamaklı yıl (`94JAN17` = 1994). Kod 2 bir
  algılama değil, yarıçap kuralıdır: eşik = 10^(M/2 − 0,79) km (M6,5 → 288 km, M7 → 513 km, M8 → 1622 km,
  M9,1 → 5754 km). Kod 2 kayıtlarında M 4,9–9,1 arası; 4697 farklı olay, 9046 istasyon. Dosya 2026 kayıtları içeriyor.
- `DataHoldings.txt`: 23 839 istasyon; `Dtbeg Dtend Dtmod NumSol` sütunları var (indirmeden ön eleme için kullanılabilir).
  `llh.out` boylamları −229 gibi sarılmamış değerler içerebiliyor.
- ComCat: `starttime=2000-01-01&endtime=2026-01-01&minmagnitude=6.5&maxdepth=30` → 665 olay
  (`eventtype=earthquake` eklemek sayıyı değiştirmiyor). Not: `endtime=2025-12-31` 31 Aralık'ı DIŞARIDA bırakır.
- Üstveriyle kaba uygunluk tahmini (doluluk ≥%60 uygulanmadan, yani üst sınır; Marmara dahil): 665 olaydan
  ≥3 yakın + ≥3 referans istasyonu olan olay sayısı:
  - kod 2 kuralı yok: 68 olay, ~46 bağımsızlık kümesi (Japonya 21, Şili 12, Yeni Zelanda 5, Nepal 4, Yunanistan 4 ...)
  - taslaktaki kural (pencere + önceki 3 yılda herhangi bir kod 2): **3 olay, K ≈ 3**
  - yalnız pencere içi kod 2: 3 olay; yalnız M ≥ 6 kod 2: 4 olay
  - yalnız uzaklık < eşik/2 olan kod 2 (pencere içi): 18 olay
  - yalnız uzaklık < eşik/4 olan kod 2 (pencere + önceki 3 yıl): 33 olay, K ≈ 25

## Bulgular (önem sırasıyla)

### 1. Kod 2 kuralı sınavı önceden "güç yok"a mahkûm ediyor

- Sorun: NGL kod 2'si M ≥ ~5 her olay için cömert bir yarıçaptır (M6,5 için 288 km). "Pencere ve önceki 3 yılda hiç kod 2
  yok" şartı aktif bölgelerdeki hemen her istasyonu eler. Üstveri tahmini: 68 → 3 olay, K ≈ 3 < 20.
- Neden önemli: Hüküm koşudan önce belli; ayrıca kural seçici: hayatta kalan istasyonlar 8 yıldır yakınında orta
  büyüklükte deprem olmamış yerlerdir (sismik sükûnete koşullama, kendisi bir öncül adayı). Öncü dizisi olan olaylar
  (ör. 2014 Iquique'nin M6,7 öncüsü, olaydan 16 gün önce, pencere içinde) yakın istasyonlarını kaybeder: H0 yönüne yanlılık.
- Önerilen düzeltme (metin): "Kod 2 kaydı istasyonu yalnız uzaklık_km < eşik_km / 4 ise ve kaydın tarihi
  [T − 8 yıl − 7 gün, T − 7 gün] içindeyse eler. Pencere içinde kalan diğer kod 2 kayıtları için modele kod 1 gibi bir
  sıçrama terimi eklenir. Kaydın tarihi T − 7 günden sonraysa (olayın kendisi dahil) yok sayılır." Bu kuralla üst sınır
  33 olay / K ≈ 25; doluluk şartından sonra daha az olacaktır. Güç kapısının yine geçilemeyebileceği bölüm 1'de açıkça
  yazılmalı.

### 2. Kontrol tasarımı H0 altında r > 0,5 üretir; negatif kontrol bunu görmez

- Sorun: Olay kümeleri tanım gereği aktif levha sınırlarındadır (uygun olayların ~yarısı Japonya ve Şili dalma-batma
  bölgesi). Kontroller rastgele bir NGL istasyonunda merkezlenir; istasyonlar yoğun ağlarda (ABD, Avrupa, Japonya içi)
  toplandığı için kontroller sistematik olarak daha sakin, daha yoğun ağlı yerlere düşer. Öncül olmadan da olay
  bölgesinde |Δv| büyük çıkar: (a) yavaş kayma olayları (Boso, Bungo, Guerrero, Hikurangi; 2+3 yıllık pencerede eğim
  farkı üretir), (b) 8 yıldan eski büyük depremlerin postsismik eğriliği (Sumatra 2004, Maule 2010, Tohoku 2011 on yıldan
  uzun sürer; eğrilik doğrusal parçalı modelde sıfırdan farklı ek eğimdir), (c) volkanik deformasyon, (d) yüksek gürültü.
  S bir vektör BOYU olduğu için gürültüyle yukarı kayar (Rayleigh benzeri): gürültüsü fazla olan taraf her zaman büyük S
  alır. Küme büyüklüğü de etkiler: 3 yakın + 3 referanslı bir kümenin medyanı 8+8'liğe göre daha geniş dağılır ve
  ortak referans gürültüsü tüm yakın istasyonlara aynı anda biner. Sonuç: H0 altında r tekdüze değildir, beklentisi
  0,5'ten büyüktür. Bölüm 7'deki "iki yöne de çekebilir" ifadesi yanlış iyimser; beklenen yön bellidir (yukarı).
- Negatif kontrol: "sahte olay" yine bir kontrol kümesidir, kontrol kümelerine karşı puanlanır. Yalnız kontrollerin kendi
  aralarında değiş-tokuş edilebilirliğini ve kodu sınar; olay-kontrol uyumsuzluğunu hiç görmez.
- Önerilen en sade düzeltme (metin, ikisi birlikte):
  1. "Kontrol merkezleri NGL istasyonları değil, katalogdaki öteki M≥6,5 (derinlik ≤30 km) olayların dış merkezleridir.
     Aynı T kullanılır. Şart: o dış merkezin 100 km içinde [T − 8 yıl, T + 2 yıl] aralığında M≥6,5 olay yok, dış merkez
     olaydan ≥ 600 km uzak, küme geçerli. Uzaklık üst sınırı yoktur (aynı epok ortak modu zaten eşitler)." Böylece kontrol
     de aktif, deprem üretebilen bir kaynağın üstündedir; yalnız zamanlaması farklıdır.
  2. "Kontrol kümesinde yakın ve referans istasyon sayısı olay kümesininkine eşitlenir (en yakın n_yakın ve n_ref alınır;
     daha azı varsa kontrol geçersizdir)." Bu, küme büyüklüğünün medyan dağılımına etkisini giderir.
  Ek, hüküm vermeyen ama durdurma şartı olan denetim: "Yerinde plasebo: her olayın aynı dış merkezi ve aynı kurallarla
  T' = T − 5 yıl epokunda (pencere [T − 10 yıl − 7 gün, T − 5 yıl − 7 gün], olay penceresiyle çakışmaz) puanlanır. Verisi
  olan olaylarda ortalama plasebo r'nin iki yanlı %95 aralığı 0,5'in üstündeyse tasarım yanlı sayılır, hüküm
  'ayırt edilemez (yanlılık)' olur." Bu, bölgesel yanlılığı yakalayabilen tek denetimdir; olay penceresine dokunmaz.
  Not: yerinde zaman kaydırmalı kontrol tek başına ana tasarım olamaz; 10 yıllık seri ister ve 2010 öncesi olayları
  neredeyse tamamen eler.

### 3. Güç kapısı ve hüküm eşikleri tutarsız

- Sorun a (dağılım): r kesiklidir; n kontrol için r ∈ {0, 1/n, ..., 1}, varyans (n+2)/(12n). n=10 → sd 0,316;
  n=5 → 0,342. 0,289 (sürekli tekdüze) gücü olduğundan iyi gösterir. Ayrıca K küme sayısıdır ama ortalama olay
  üzerinden alınıyor; kümede birden çok olay varsa etkin örneklem K'den küçük ya da farklıdır.
- Sorun b (H0'a ulaşılabilirlik): H0 şartı "üst sınır < 0,60". Gerçek etki tam sıfırken bile bu, ortalamanın
  0,60 − 1,645·SE altında kalmasını ister. K=25, sd 0,316 → SE 0,063, eşik 0,496 → H0 olasılığı ≈ %48. K=46 → ≈ %69.
  %80 için K ≈ 60 gerekir. Kapı K ≥ 20'de açılıyor ama o noktada doğru H0 bile yazı-tura. Tasarım asimetrik:
  H1'e (eşik 0,5) H0'a göre çok daha kolay ulaşılır; bulgu 2'deki yukarı yanlılıkla birleşince sahte H1 riski yüksek.
- Sorun c (çakışma): H1 (alt sınır > 0,5) ile H0 (üst sınır < 0,60) birlikte doğru olabilir (örn. ortalama 0,55, SE 0,02).
  Öncelik yazılmamış.
- Sorun d (bootstrap): K ≈ 20–40 kümede yüzdelik bootstrap tek yanlı %95 sınırları dar kalır (gerçek kapsama ~%90–93).
  Ayrıca kümeler bağımsız değil: aynı kontrol istasyonları farklı olayların kontrollerinde, bir olayın yakın istasyonları
  ötekinin referansında yer alabilir (300 km / 1 yıl kuralı 5 yıllık pencereleri ve 500 km referans halkasını kapsamaz).
- Önerilen düzeltme (metin): "SE = sd(küme ortalamaları)/√K; sınırlar t dağılımıyla (sd K−1) hesaplanır; bootstrap
  (10 000, tohum 20261111, küme düzeyinde, BCa) yalnız bilgi satırıdır. Ölçü küme ortalamalarının ortalamasıdır.
  Bağımsızlık kümesi: iki olayın yakın ya da referans istasyon kümeleri en az bir ortak istasyon içeriyorsa ve pencereleri
  çakışıyorsa (|T1 − T2| < 5 yıl) aynı kümededir (tek bağlantılı). Güç kapısı sd = √((n̄+2)/(12 n̄)) ile yazılır ve
  'doğru H0'ın bu K'de H0 hükmü alma olasılığı' da kapıda ilan edilir. Hüküm önceliği: H1 > H0 > ayırt edilemez;
  H1 ve H0 birlikte sağlanırsa hüküm 'H1, etki < 0,60 (küçük)' diye yazılır."

### 4. Tanımlar tek anlamlı değil (uygulayıcının vermesi gereken kararlar)

Her madde için önerilen metin:

1. Dizin/çerçeve: "`https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{STA}.tenv3` (IGS20, levhaya sabitli
   değil). Dosyalar bir kez indirilir; indirme tarihi ve SHA-256'ları kayda geçer." (Levha dizinleri var; dosyalar her
   gün değişiyor.)
2. Zaman birimi: "Zaman ekseni MJD sütunudur. 1 yıl = 365,25 gün. T = ComCat UTC kaynak zamanının tarihi (MJD_T).
   Pencere [MJD_T − 1826 − 7, MJD_T − 7] (iki uç dahil), menteşe MJD_T − 730 − 7, taban [başlangıç, menteşe),
   yakın dönem [menteşe, bitiş]. Eğimler mm / 365,25 gün."
3. Doluluk: "Alt aralıktaki farklı MJD'lerin (ayıklamadan önce) alt aralık gün sayısına oranı."
4. `steps.txt` ayrıştırma: "İki basamaklı yıl: ≥ 90 → 19xx, aksi 20xx. Aynı tarihte birden çok kod 1 satırı tek sıçrama.
   Pencerenin ilk ya da son 60 gününde ya da menteşeye 60 günden yakın kod 1 basamağı varsa istasyon o pencere için
   uygunsuzdur (ek eğimle eşdoğrusallık). Kod 2 için bulgu 1'deki kural."
5. Model ayrıntısı: "Sinüs periyotları 365,25 ve 182,625 gün. Ayıklama bileşen başına yapılır; bir bileşende atılan gün
   iki bileşenden de atılır. MAD her bileşenin ilk uydurma artıklarından."
6. Uzaklık: "Küre, R = 6371 km, büyük daire; koordinat kaynağı `DataHoldings.txt` Lat/Long (boylam [−180, 180)'e
   sarılır). Sınırlar dahil. Eşit uzaklıkta istasyon adına göre sıra." Marmara kutusu da sarılmış boylamla uygulanmalı.
7. Kontrol merkezi istasyonsa (taslaktaki tasarım korunursa): merkez istasyonun kendisi uzaklık 0 ile yakın kümeye
   girer ve uygun olması gerekir mi, yazılmamış. Olay kümesinde 0 km'de istasyon yok, bu bir asimetri. Bulgu 2'deki
   dış merkezli kontrol bu soruyu ortadan kaldırır.
8. Olay bölgesi istasyonları kontrolde: taslakta 500 km'deki bir kontrolün referans halkası (200–500 km) dış merkeze
   kadar uzanır; olayın yakın istasyonları kontrolün referansı olabilir ve kontrolün yakın istasyonları olayın referans
   halkasına düşebilir. Metin: "Dış merkezin 600 km içindeki hiçbir istasyon o olayın hiçbir kontrol kümesinde
   (yakın ya da referans) kullanılmaz."
9. Kontrol seçimi: "alfabetik sıralanır ve SHA-256'ya göre sıralanır" çelişik ve gereksiz. Metin: "Anahtar =
   SHA-256(UTF-8 `{ComCat id}|{merkez kimliği}`), küçük harf onaltılık; artan sıra. Bu sırayla açgözlü seçilir: aday,
   seçilmiş her kontrol merkezinden ≥ 150 km uzaksa ve kümesi geçerliyse alınır; 10'da durulur. Genişletme gerekirse
   aday kümesi büyütülür ve sıralama baştan yapılır." `olay kimliği` = ComCat `id` sütunu (birincil id).
10. Hüküm ölçüsü: "ortalama r (katmanlı AUC)" olay ağırlıklı mı küme ağırlıklı mı belirsiz (bulgu 3'te çözüm).
11. Negatif kontrol: "tek yanlı iki yönde de %95 aralığı" belirsiz. Metin: "iki yanlı %95 aralığı 0,5'i dışlarsa durulur."
12. Pozitif kontrol: "doğrusal artan yapay hız değişimi" iki türlü okunur (sabit hız sıçraması mı, doğrusal artan hız
    mı). Metin: "Menteşeden sonra doğu konumuna A·(t − t_menteşe) eklenir (A = 0,5/1/2/3 mm/yıl). Her olayın ilk kontrolü
    sahte olay seçilir, yalnız onun yakın istasyonlarına eklenir ve kalan kontrollere karşı puanlanır." Bu 0,61 ve 0,75
    eşiklerinin hangi karşılaştırmayla ölçüldüğünü sabitler. Ayrıca yapay sinyal kontrol bölgesinin gürültüsüne göre
    ölçülür; olay bölgesi daha gürültülüyse duyarlılık abartılır, bu sınır olarak yazılmalı.
13. ComCat sorgusu: "`format=csv&starttime=2000-01-01T00:00:00&endtime=2026-01-01T00:00:00&minmagnitude=6.5&maxdepth=30
    &orderby=time-asc`, tercih edilen büyüklük; sorgu sonucu CSV olarak ve sorgu zamanıyla kayda geçer (büyüklükler
    sonradan revize edilir)." Taslaktaki "2025-12-31 bitiş" 31 Aralık'ı dışarıda bırakır.

### 5. Sızıntı ve körlük

- Olayın kendi kod 2 kaydı (tarih T) pencere bitişinden (T − 7 gün) sonradır. Kural tarih sınırıyla açıkça yazılırsa
  (bulgu 1) asimetri yaratmaz. Yazılmazsa ("istasyonda kod 2 yok" diye okunursa) olay kümeleri yakın istasyonlarını
  kaybeder, kontroller kaybetmez: sert asimetri. Tarih sınırı metne girmeli.
- Kontrolün "sonraki 2 yılda deprem yok" şartı 2025-12-31'de kesilir: 2024–2025 epoklu kontroller 2026 depreminin
  öncesinde olabilir, olaylarda böyle bir kirlenme yok. Küçük ama asimetrik. Metin: "T > 2023-12-31 olaylar ana satıra
  girmez, bilgi satırında raporlanır." (2026 okunmadan çözülür.)
- `steps.txt`'nin güncel sürümü 2026 kayıtları içerir. Metin: "Ayrıştırmada 2025-12-31 sonrası satırlar atılır."
- NGL yeniden işleme: tenv3 serileri olay katalogundan basamak düzeltmesi ya da olaya göre aykırı temizliği içermez
  (basamaklar ayrı listede; seri ham). Çerçeve gerçekleştirmesi küresel ve olay sonrası verinin etkisi tüm istasyonlara
  ortak; referans farkı ve aynı epok bunu giderir. Ciddi sızıntı görmüyorum. Tek sorun yeniden üretilebilirlik: dosyalar
  günlük değişiyor, indirme anının arşivlenmesi gerekir (madde 4.1).
- Körlük açığı: kontrol kümeleri, başka olayların pencerelerine ait istasyon-günleri içerir (bir olayın yakın
  istasyonları başka bir T'deki kontrolün üyesi olabilir). "Kod geliştirme yalnız kontrollerle" kuralı olay verisini
  görmeyi engellemez. Metin: "Geliştirme sırasında hiçbir olayın [T − 5 yıl − 7 gün, T] aralığında, dış merkezinin
  100 km içindeki istasyon-günleri çizilmez ve onlardan S hesaplanmaz; kontrol geliştirmesi bu istasyon-epok çiftlerini
  maskeleyen bir filtreyle yapılır."

### 6. Veri hacmi ve uygulanabilirlik

- Taslak hacmi yazmıyor. Örnek dosya 1,5 MB / 20 yıl (~75 KB/yıl). Arşivde 23 839 istasyon; hepsini indirmek
  ~15–25 GB. Olay kümeleri için en çok ~560 benzersiz istasyon (kod 2 kuralı olmadan üst sınır); asıl hacim
  kontrollerden gelir (olay başına 10 × 16 istasyon-epok, birkaç bin benzersiz dosya, birkaç GB).
- Önerilen azaltma (metin): "Uygunluk önce indirmeden `DataHoldings.txt` (Dtbeg ≤ pencere başı, Dtend ≥ pencere sonu,
  NumSol/gün ≥ 0,6) ve `steps.txt` ile elenir. Adaylar uzaklık sırasıyla indirilir; 8 uygun bulununca durulur.
  Her dosya bir kez indirilir ve yerelde önbelleklenir." Bu, indirmeyi kabaca üçte bire indirir ve Marmara körlüğünü de
  kolaylaştırır.

### 7. İddia edilen ile ölçülen arasındaki fark; hüküm dili

- Ölçülen: dış merkezin 100 km içindeki istasyonların son 2 yıl ile önceki 3 yıl arasındaki yatay eğim farkının boyu,
  200–500 km halkasının medyanına göre; seçilen kontrollere göre sıra. Bu "öncül" değil, "olaydan önceki bölgenin, kontrol
  bölgelerine göre yakın-dönem eğim değişkenliği"dir. Bulgu 2 düzeltilmeden H1 tektonik aktivite farkını ölçer.
- Sabit 100 km ve 200–500 km referans: M8–9 olaylarda olası öncül deformasyon 500 km'den geniştir; referans farkı sinyalin
  kendisini çıkarır. Büyük olaylarda ölçü sinyale kördür. Bölüm 7'ye yazılmalı.
- Örneklem: uygun olayların çoğu Japonya ve Şili dalma-batma; doğrultu atımlı alt küme küçük. "Hayırsa bu gözlem türü
  yıl ölçeği için Marmara'da da aday olamaz" (bölüm 1) ve "H0: ... Marmara için aday olmaz (deftere kapanış)" (bölüm 8)
  fazla iddialı. H0 yalnız şunu söyler: "küresel, ağırlıkla dalma-batma örnekleminde, bu ölçüyle ortalama r ≥ 0,60
  büyüklüğünde bir boy farkı yok." Metin önerisi: "H0: bu ölçü (boy, 100 km, 2/3 yıl) ve bu örneklemde ortalama r ≥ 0,60
  dışlandı. Yönlü ölçü, doğrultu atımlı olaylar ve fay ölçeğine göre ayarlı yarıçap açık kalır; Marmara için yalnız bu
  ölçü kapanır."
- H1 dili "bir sonraki sorunun açılma şartı" olarak dürüst; ancak yerinde plasebo (bulgu 2) geçmeden H1 yazılmamalı.
- "Güç yok" dili dürüst; fakat bulgu 1 düzeltilmezse kesin sonuçtur ve bu, dondurmadan önce bilinmelidir.
- Bölüm 1'deki "köprü ölçümü (k 8, J 0,0084)" sınavla ilişkisiz; ön kayda bir şey eklemiyor, çıkarılabilir.

## Dondurmadan önce zorunlu olanlar

1. Kod 2 kuralı (bulgu 1) ve tarih sınırı (bulgu 5).
2. Dış merkezli, küme boyu eşitlenmiş kontroller ve yerinde plasebo durdurma şartı (bulgu 2).
3. sd, CI yöntemi, bağımsızlık kümesi, hüküm önceliği (bulgu 3).
4. Bulgu 4'teki 13 tanım.
5. Bunlardan sonra K'yi yalnız üstveriyle yeniden say; K < 20 ise dondurmadan önce yeniden açma şartına (bölüm 9) geç.
