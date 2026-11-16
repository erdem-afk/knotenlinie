# TR-4 koşu kodu: kodlayıcının okumaları

Kapsam: `kayit/turetme/tr4/tr4_indir.py`, `tr4_kosu.py`, `tr4_test_yapay.py`. Ölçüt:
`TR-4_marmara-hiz-tabani_ONKAYIT.md` DONDURULDU sürüm 2 + Ek 1 (değiştirilmedi), `TR-4_INCELEME-1.md`,
`TR-4_ASAMA0-KOD-INCELEME.md` (K7), `TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 3 §3 ve §5 (1b tanımı). 16 Kasım 2026,
veri öncesi. Hiçbir gerçek dalga formu ya da üstveri istenmedi ya da açılmadı. Bütün sınamalar yapaydı ve yerel sahte
sunucu yalnız 127.0.0.1'deydi.

Aşağıdaki her madde, metnin açık bıraktığı ve kodun bir yolu seçtiği bir noktadır. **K** işaretli maddeler ön kayıt
sahibinin ya da kod incelemecisinin kararını ister. Kod şimdilik önerilen okumayı uygular.

## A. İndirme (`tr4_indir.py`)

1. **Sunucu.** `eida.koeri.boun.edu.tr` (Ek 1). Aşama 0 ve aşama H ile aynı.
2. **İstek birimi istasyon-aydır.** Bir POST isteği o ayın indirilecek her günü için bir satır taşır:
   `KO <ist> -- HH? <başlangıç> <bitiş>`. Bu, aşama H'nin ölçtüğü biçimdir (§5.2). Kanal joker (`HH?`) aşama H'deki
   gibidir. Seçilen üç kanal (Z, N/E ya da 1/2) çözümden sonra süzülür. İstasyonun pencereleri arasında kanal seçimi
   farklıysa (bugünkü `istekler.json`'da yok) plan kurulmaz ve iş durur. `hiz_sonuc.json` "GET" derse gün gün GET
   atılır ve günler tek bir ham dosyada birleştirilir.
3. **Zaman aşımı (K7).** Soket zaman aşımı 900 sn'dir; bu, aşama H'nin `H_TAVAN_SN` değeridir. §5.2'nin "istek başına
   en çok 15 dk" tavanı yalnız aşama H'nin ölçüm kuralı olarak okundu. Üretim isteğinin toplam süresine tavan konmadı:
   140 MB'lık bir istek 120 KiB/s'de ≈ 20 dk sürer, 15 dk'lık bir tavan her isteği keserdi. İşin süre sınırı
   (`sure_sn`) dolarsa süren istek bırakılır. Bu kesme deneme sayılmaz ve istek sonraki işte yeniden atılır.
4. **Nezaket.** Tek akış, istekler arası ≥ 2 sn (aşama H). 429/503'te Retry-After beklenir (en çok 120 sn, başlık
   yoksa 30 sn). Bağlantı hatasından sonra 10 sn beklenir. User-Agent geneldir (`fdsn-client/0.1 (python-urllib)`).
5. **Kesin kodlar ve deneme.** `KESIN = (200, 204, 404, 401, 403)` aşama 0 ile aynıdır (K7). 401/403 kesindir:
   yeniden denenmez ve aşılmaz. Öteki kodlar ve bağlantı hataları sonraki turda bir kez daha denenir, yani istek
   başına en çok iki deneme yapılır. Kuyruk bitince kesin olmayan son durum oranı %5'i aşıyorsa tek bir yeniden
   deneme turu yapılır (§5.5 son cümlesi): o isteklere üçüncü bir deneme hakkı verilir. "ε'dan önce" koşulu bu
   turun indirme bitmeden yapılmasıyla sağlanır.
6. **Eksik gövde.** Yanıt 200 ama gövde `Content-Length`'ten kısaysa (bağlantı ortada koptuysa) istek kesin
   sayılmaz (`EksikGovde`) ve yeniden denenir. Yapay sunucuda bulundu: `http.client` bu durumda hata vermiyor.
7. **200 ama çözülemeyen miniSEED.** Sunucu kesin bir kodla yanıt verdiği için istek kesin sayılır. ÇİF dosyası
   yazılmaz ve günlüğe `bicim_hata` düşülür. O günler 1b'de boş görünür. (Risk R6.)
8. **Etkin indirme süresi (K).** "21 gün (504 iş-saati)", `indir` işlerinin duvar saatlerinin toplamı olarak
   okundu: başlangıçtan çıkışa kadar, işleme süresi dahil. Öteki okuma yalnız aktarım sürelerini toplamaktır. İşleme
   C'de ≈ 7–9 saat tutar (bkz. kaynak), yani fark ≈ %2'dir. Takvim süresi ilk indirme isteğinden sayılır.
9. **Bütçe sınaması** her istek başlamadan önce yapılır. Süren bir istek bütçeyi en çok kendi süresi kadar aşabilir.
   Bütçe dolunca durum `kesildi` olur ve kalıcıdır; sonraki çağrılar istek atmaz.
10. **Sıra.** Ana aylar önce, 2014-01'den 2023-12'ye, her ayda istasyon kodu sırasıyla. Yer kodu istasyon kodudur;
    tek birleşik yer ISK'dır ve onun temsilcisi KO.ISK'dır. Bilgi satırı 13'ün ayları (KO.SLVT, 2024-03 … 2025-05)
    ana aylardan sonra gelir ve aynı bütçeden harcanır. Bütçe bilgi satırı 13 sırasında dolarsa ana örneklem tamdır.
    Koşu kesik sayılmaz, bilgi satırı 13 "veri yok" yazar.
11. **Gün ve pencere.** d istasyonun yerel ortalama güneş tarihidir. UTC penceresi
    [d 00:00 + ⌊−boylam/15 + 0,5⌋ saat, +4 saat]'tir; Marmara'da bu (d − 1) 22:00 – d 02:00'dır. Bu, aşama H ile aynı
    yuvarlamadır. Kademe C'de d'nin ayın 1–20. günleri alınır. Bilgi satırı 13'te [T − 69, T + 30] her gün,
    [T − 400, T − 70] kademeye göre alınır (İ1-K5).
12. **Körlük.** Bağlantı kurulmadan önce iki denetim yapılır: isteğin UTC bitişi < 2026-01-01 ve ≤ 2025-12-31 olmalı;
    gün d ana pencerelerde ≤ 2023-12-24, bilgi satırı 13'te ≤ 2025-05-31 olmalı. Plan kurulurken de aynı sınır
    `assert` ile denetlenir.
13. **Ham veri** yerel geçici dizine `.part` adıyla yazılır, sonra yeniden adlandırılır. İşlendikten sonra hata olsa
    da silinir. İş başında önceki işten kalmış ham dosyalar silinir. ÇİF dosyası depoya geçici adla yazılır,
    `os.replace` ile yerine konur, sha256'sı günlük satırına yazılır. Günlük satırı ÇİF yazıldıktan sonra eklenir.
    İş ikisinin arasında kesilirse istek yeniden atılır. Bu israftır ama doğrudur.

## B. Saatlik ön işlem ve ÇİF (TR-5b §3.2–3.3)

14. **Saat kabulü.** Saatlik ızgara [t0, t0 + 3600 sn)'dir. Örnekler en yakın ızgara indisine yerleştirilir;
    kesirli örnek kayması yok sayılır. Tamlık, dolu indislerin payıdır. Bir kanal istasyon-ay içinde birden çok
    örnekleme hızı taşıyorsa o kanalın saatleri reddedilir.
15. **Boşluk (K).** ≤ 1 sn'lik iç boşluklar doğrusal aradeğerlenir. Daha uzun boşluklar ve uçlardaki boşluklar,
    ortalama ve doğrusal eğilim dolu örneklerden çıkarıldıktan sonra sıfır yapılır. Bu saatler tamlık ≥ %99 ise yine
    kabul edilir. Metin, %99 ile %100 arasında kalan > 1 sn'lik boşluğu tanımlamıyor; öteki okuma o saati
    reddetmektir.
16. **Konik.** "%5 Hann", her uçta %5 olarak okundu. Bu obspy'nin `max_percentage = 0,05` kuralıdır ve
    `inc1_islem_suresi.py` ile aynıdır.
17. **İndirgeme.** FFT ile 20 sn⁻¹'e indirilir. 7,5–8,0 Hz arası kosinüs geçiştir, 8 Hz üstü sıfırdır. Beyazlatma 2,1 Hz
    üstünü zaten sıfırladığı için bu seçimin ÇİF'e etkisi yoktur.
18. **RMS.** 0,5–2 Hz bant RMS'i, koniklenmiş ve indirgenmiş saatin spektrumundan Parseval ile hesaplanır.
    Beyazlatmadan önce hesaplanır.
19. **Enerji reddi (K).** Bir saat, üç bileşenden herhangi birinin RMS'i o bileşenin medyanının 3 katını aşarsa bütün
    çiftlerden atılır. Saat düzeyindeki kabul (madde 1) de üç bileşen birlikte olduğu için bu yol seçildi. Medyan,
    yer-penceresinin [a, b] = [T − 1095, T − 8] aralığındaki tamlığı geçen bütün saatlerinden hesaplanır. Bu saatlere
    maskeli günler dahildir. Kademe C'de yalnız örneklenen günler vardır. Öteki okumalar: yalnız ilgili bileşeni içeren
    çiftlerden atmak, ya da medyanı maskesiz günlerden almak.
20. **ÇİF kuralı.** c[τ] = Σ_t a(t) · b(t + τ), sıfır dolgulu (dairesel değil). Çiftler ZE, ZN, EN'dir; 1/2
    bileşenlerde Z1, Z2, 12. Normalleştirme beyazlatılmış saatlerin enerji çarpımının kareköküdür. Gecikme ±60 sn'dir
    (2401 örnek). Sınama doğrudan zaman alanı toplamıyla 1e-6 içinde eşleşti ve bilinen gecikme (+2 sn) doğru işaretle
    bulundu.
21. **2–4 Hz bandı da saklanır (K).** Bilgi satırı 10'un 2–4 Hz Δ'sı, ham veri silindikten sonra ancak bu bandın saatlik
    ÇİF'i saklanırsa hesaplanabilir. Bu yüzden ikinci bir beyazlatma (2,0–4,0 Hz, 0,1 Hz kosinüs kenar) aynı saatlerden
    hesaplanır ve `ccf24` olarak saklanır. Enerji reddi aynı (0,5–2 Hz RMS'i) ve koda aynıdır. Bedeli: saklama C'de
    ≈ 4,0 GB yerine ≈ 8,5 GB olur. Hüküm ölçüsüne etkisi yoktur. Öteki seçenek bilgi satırı 10'un 2–4 Hz yarısından
    vazgeçmektir.
22. **Günlük ÇİF.** Her çift için, kabul edilen (tam ve enerjisi geçen) saatlerin ortalamasıdır; ≥ 2 saat gerekir.
    Maskeli gün geçersizdir.

## C. Koşu (`tr4_kosu.py`)

23. **Zincir kodu.** `zincir`, `germe_olc`, `ay_esle` ve `ger`, `kayit/turetme/tr5/tr5b_yapay.py`'den; `germe_pk`,
    `tr5b_yapay2.py`'den değiştirilmeden içe aktarılır ve sha256'ları denetlenir. Koşu kodunun kendi parçaları günlük
    ÇİF kurma, maske, kademe C maskesi, çift → istasyon toplama, ekleme ve sarmalayıcılardır. Kod denetimi (i) bu
    parçaları dondurulmuş npz üstünde sınar.
24. **1b'nin "aynı kapısı"** G0'dır: dolu yer sayısı ≥ 10 olan T'ler arasında en az 3 yıl arayla bir çift. "Gün dolu"
    ve "yer-penceresi dolu" TR-5b §5'in 1b tanımıdır. Gün dolu: 4 saatin ≥ 2'sinde üç bileşenin tamlığı ≥ %99. Yer-
    penceresi dolu: A, B ve C dilimlerinin her birinde dolu gün oranı ≥ 0,60, ve ≥ 9 takvim ayında hem C'de hem A∪B'de
    ≥ 10 gün için yığın şartı (son 10 günde ≥ 5 dolu ve maskesiz gün). Yalnız tamlık okunur, ε hesaplanmaz. Aygıt
    kuralı aşama 0'da uygulandı.
25. **1b paydası kademe C'de (K, önemli).** "Payda: dilimin maskesiz günleri" ifadesi örneklenen (1–20.) maskesiz
    günler olarak okundu. Takvim günleri payda alınırsa C'de oran en çok 20/30,4 ≈ 0,66 olur. O zaman küçük bir veri
    kaybı bile 0,60'ı kırar ve kapı büyük olasılıkla tutmaz. §3.2 "zincir değişmez" der ve 1b'yi C için ayrıca
    tanımlamaz. Bu madde kod incelemesinde açıkça onaylanmalıdır.
26. **M5 maskesi.** Olay kimlikleri `tr4_pencereler.csv`'nin `maske_olay` sütunundan, olay tarihleri
    `tr4_onkayit_sayim.json` → `olay_uzaklik`'tan alınır. Her yer-penceresinin maskeli gün sayısı csv'deki
    `maske_gun` ile denetlenir; uyuşmazlıkta iş durur. Olayın UTC tarihi yerel güneş tarihi d ile karşılaştırılır.
27. **Kesik koşu (K).** "İndirildi", yer-penceresinin bütün istasyon-ay isteklerinin KESIN kodla tamamlanması
    demektir (K7). İki denemede de kesin olmayan bir ay, kesik koşuda o pencerenin T'sini eksik bırakır. Tam (kesilmemiş)
    koşuda aynı ay yalnız eksik gün olarak 1b'ye girer. Bu asimetri metnin harfidir. Öteki okuma "iki deneme bitti"
    sayımıdır. Hiç penceresi olmayan T eksik sayılmaz. "T 2017–2021 tamamlanmamış" şartı, bu T'lerden birinin eksik
    olması olarak okundu.
28. **Hangi pencereler işlenir.** Tam olan T'lerin 1b'yi geçen yer-pencereleri işlenir. "Veri yok" hükmünden sonra
    da 2. ve 3. adım koşar. Biri geçmezse hüküm kalır ve ek metin "bilgi satırı 0: hesaplanmadı (n = 0, yer = 0)"
    olur. Bunun nedeni hiçbir Δ'nın yazılmamasıdır.
29. **(ii-a).** −%0,1 germe, saatlik ÇİF'ten kurulan günlük ÇİF'lere uygulanır, C diliminde ([T − 365, T − 8]).
    Başvuru ve yığınlar yeniden kurulur. Oran istasyon Δ'sı üstündendir. Havuz, Δ'sı hem özgün hem ekli durumda geçerli
    bütün yer-pencereleridir. Hiçbir oran yoksa adım değerlendirilemez ve sıra 4. adıma geçer. 4. adım bu durumda
    "veri yok (ε geçerliliği)" verir.
30. **Kod denetimi (i)** her `olc` çağrısında yeniden koşar. Npz'nin, iki başvuru dosyasının ve TR-5b kodunun
    sha256'ları denetlenir. (b) yalnız kademe C'de koşar. Sapma sayılırken geçerlilik uyuşmazlığı da (biri NaN, öteki
    değil) sapma sayılır. `denetim_i` kipi indirmeden önce de koşabilir. Bugünkü sonuç: 60 + 60 dizi, sapan 0; en
    büyük fark Δ'da 4,9·10⁻⁷ %, oranda 4,9·10⁻⁶.
31. **Hüküm metni.** Biçim "<hüküm adı>. <zorunlu ek metin>" olarak seçildi. Sayılar yüzde birimindedir, üç ondalık
    hane, Türkçe virgül ve U+2212 eksi işaretiyle yazılır. "T başına" listeleri "2017: n, …, 2024: n" biçimindedir.
    Kalıp T'nin [kademe] yeri "kademe C" ya da "kademe C, kesik, T 2017–2021" olur (§5.3). [ilk]–[son] geçerli
    pencerelerin T'leridir. Bilgi satırı 14'ün yeri "x % (istasyon ortalaması)" ya da "hesaplanamadı" olur.
    "geçersiz (kod)" ek metni "sapan dizi sayısı N" ya da "medyan oran x"tir.
32. **Bilgi satırı 0'ın "Kapı altı; …; hüküm [hüküm adı]." cümlesi** hüküm metnine eklenmez (§4.5: "başka metin
    eklenmez"). `hukum.json` → `bilgi_0.ek` alanına yazılır.
33. **Önyükleme.** `tr4_guc.bootstrap` ile aynıdır: çokterimli çokluklar, `np.repeat`, < 5 değerli çekiliş NaN,
    `nanquantile` (doğrusal). Tohum `sha256("tr4-hukum|20261202")`'nin ilk 8 hanesidir. Bilgi satırlarının tohumu
    `tr4-bilgi|<ad>|20261202`'dir.
34. **Bilgi satırları.**
    - 1: csv sütunları `sakin_ileri_2y`, `sakin_M7_500`, `sakin_M5_50_pencere`, `sakin_M55_100_genis` kullanılır. Ek
      değişke (pencere içi M ≥ 7 ≤ 1000 km) metnin eşdeğerliğiyle T ≤ 2020 olarak uygulanır.
    - 2: gevşek ve sıkı küme yalnız indirilen pencerelerle kesişimdir. Gevşek kümenin fazladan pencereleri
      indirilmez.
    - 6: aynı T'den rastgele 2000 yer çifti çekilir, tohum `tr4-bilgi6|20261202`.
    - 7: saat reddi oranı, enerjiyle atılan saatlerin tam saatlere oranıdır.
    - 10: eğilimden arındırılmış Δ için A∪B'deki ε'a doğrusal eğilim uydurulur, bütün ε'dan çıkarılır, sonra ay
      eşlemesi yapılır.
    - 11: her pencere-çift için 12 aylık ortalama ε'nın (≥ 9 ay) tepeden tepeye farkı alınır. Yer değeri bunların
      medyanıdır; satır yer değerlerinin medyanını yazar.
    - 13: δ_ko `germe_pk` (±%2) ile hesaplanır. Başvuru [T − 400, T − 8]'dir. Öncesinde M5 maskesi uygulanmaz,
      çünkü katalog açılmadı; Nisan 2025 olayının kendisi [T, T + 30]'dadır. İstasyon δ_ko'su çiftlerin medyanıdır
      (≥ 2). Yeri `tr4_guc_sonuc.json`'un A = 0 %5 eşikleriyle (CC10 ≈ 0,5 ve 0,7; 4 saat) yazılır.
    - 14: başvuru [t − 1095, t − 8] ile indirilmiş günlerin kesişimidir. Maske yoktur. İstasyon başına değer ve
      ortalama yazılır.
35. **Tek koşu.** `hukum.json` bir kez yazılır. Aynı hüküm ve metinle yeniden yazım zararsızdır; farklısı durur.
    "Geçersiz (kod)"dan sonraki tek yeniden koşu (§11) yeni bir kod incelemesi ister. Kod bunu kendisi açmaz: depo
    `kosu/` dizini elle arşivlenmelidir.
36. **İşlem süresinin ölçümü (§5.5).** Her istasyon-ayın `islem_sn`'si günlüğe yazılır. İlk satır, metnin istediği
    "ilk istasyon-ayda gerçek süre"dir.

## D. Riskli yerler

- **R1. Hacim ve bütçe.** Aşama H'nin ölçtüğü bayt/örnek ≈ 1,60'tır (1,26–2,11); ön kayıt 1,3 varsaymıştı. Kademe
  kuralı ön kayıttaki formülü kullanır ve değişmez. Gerçek C hacmi ise ≈ 206,1 × 1,60 / 1,3 ≈ 253 GB'tır. v ≈ 119 KiB/s
  ile bu ≈ 24 gün eder ve 21 günlük etkin bütçeyi aşar. Kesik koşu olasıdır. D kısmı (T 2017–2021, ≈ 189 GB) ≈ 18
  günde biter, kronolojik sırada önce gelir ve bütçeye sığar.
- **R2.** 1b paydası (madde 25). Yanlış okuma kapıyı kırar.
- **R3.** Enerji reddinin kapsamı ve medyanı (madde 19).
- **R4.** Kesik koşuda kesin kod şartı (madde 27). Tek bir kalıcı hata bütün bir T'yi düşürebilir.
- **R5.** 2–4 Hz saklaması (madde 21). Saklama ve işlem süresi ≈ 2 katına çıkar.
- **R6.** 200 yanıtla gelen bozuk miniSEED (madde 7) eksik gün olarak sessizce geçer. Yalnız günlükte görünür.
- **R7.** Gerçek KOERI davranışı sınanmadı: büyük POST gövdeleri, parçalı aktarım, `HH?` jokerinin ek kanal getirmesi,
  obspy'nin 140 MB'lık dosyada bellek ve süresi. Yapay sunucu bunların yalnız biçimini taklit eder.
- **R8.** Kesirli örnek zamanları (madde 14) bileşenler arasında ≤ 5 ms kaymaya yol açabilir. 0,5–2 Hz'te önemsiz.
- **R9.** `tr5b_yapay_ccf.npz` `/mnt/project-files/turetme/tr5b-ham/` altında YOK. Sınama için `tr5b_yapay2.py donder`'in
  karalama dizinindeki bir kopyasıyla yeniden üretildi: sha256 `44189a31…` ve başvuru json'u `36339a46…` bit düzeyinde
  aynı. Gerçek koşudan önce aynı yolla üretilip yerine konmalıdır. Bunu yapmak bir işletim kararıdır.
- **R10.** `isle_istasyon_ay` bir kanalın bütün izlerini float64'e çevirir. C'de istasyon-ay başına bellek tepesi
  ≈ 1–1,5 GB'tır.
