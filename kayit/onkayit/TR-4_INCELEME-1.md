DÜZELTMEYLE KABUL

# TR-4 ön kayıt: bağımsız inceleme 1 (tek ve son tur)

İncelenen: `TR-4_marmara-hiz-tabani_ONKAYIT.md`, TASLAK sürüm 1 (12 Kasım 2026). Dayanaklar: `TR-5_TR-4_SAYIM.md` Ek 2,
`TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 3 (DONDURULDU; §3 zinciri, §11 (c)), `TR-5b_INCELEME-2.md` (aşama 0 kodunun
kusurları), `ZINCIR.md` Halka 7, `kayit/turetme/tr4/` (sayım ve güç betikleri, çıktıları), `kayit/turetme/tr5/tr5b_asama0.py`.
Taslağı bu incelemeci yazmadı.

Bu inceleme ne yaptı, ne yapmadı:
- Hiçbir dalga formu istenmedi, indirilmedi, açılmadı ya da yoklanmadı. Ağa hiç çıkılmadı.
- Sayım betiği, depo dosyalarına dokunmamak için karalama dizinindeki bir kopyada, `/mnt/project-files/turetme/tr5b-ham/`
  arşivlerinden açılan girdilerle koşuldu.
- Denetim betikleri ve çıktıları `kayit/turetme/tr4/inc1/` altında (E bölümü). Hepsi `python3 -I -B`, yalnız numpy, tek
  süreç, her biri 4 dakikadan kısa. `__pycache__` kalmadı. Ön kayıt ve `tr4/` dizinindeki dosyalar değiştirilmedi. Git
  işlemi yapılmadı.

## Hüküm

**DÜZELTMEYLE KABUL.** Soru doğru kurulmuş ve ölçülebilir. Bağlayıcı sayılar bit düzeyinde yeniden üretildi. Güç
tablosu bağımsız yazımla Monte Carlo saçılımı içinde tutuyor. Zincir TR-5b'ninkidir. Hüküm kuralı otomatik ve sıralı.
Körlük, kapalı hüküm listesi ve İstanbul yasağı yerinde.

Dondurmadan önce dört engelleyici düzeltme gerekir:

- **İ1-E1. Aktarım hızı kuralı açık uçlu.** "Ertelendi (aktarım hızı)" bir son durum değil. Sonraki adım proje
  sahibine bırakılmış ve önerilen üç seçenekten biri geçersiz: "yalnız T 2021–2024" sürümünde kapı tanım gereği kırılır
  (14 / 9 / 10 / 9 yer; 3 yıl arayla tek çift 2021–2024'tür ve 2024'te 9 yer var). İndirme sırasında hız düşerse ne
  olacağı tanımsız. Aşama H, yanlış rejimi ölçüyor: 341 ve 633 KiB/s ≤ 1 MB'lık tek isteklerden geldi, 40 KiB/s ise
  11,2 MB'lık 284 sn'lik sürekli aktarımdan. Üretim istekleri istasyon-ay başına 110–170 MB'tır. Düzeltme şunları
  getirir: kronolojik indirme sırası, sabit bir indirme bütçesi, tamamlanmış T'lerle "kesik koşu", önceden tanımlı en
  küçük küme (kademe D = T 2017–2021, 153,6 GB) ve kapalı bir son hüküm ("veri yok (aktarım hızı)").
- **İ1-E2. Kapı kırılırsa σ_Δ hiç yazılmıyor.** G0 kırılırsa indirme yapılmıyor. 1b ya da 4. adım kırılırsa "sonrakiler
  koşmaz". Gerçek dolulukta kapının kırılması küçük bir olasılık değildir: tek tip kayıpta %29 kayıp kapıyı kırar,
  rastgele %30 kayıpta kırılma olasılığı 0,26–0,43'tür. Düzeltme: "veri yok" hükmü kalır, ama dolu kalan yer-pencereleri
  yine işlenir ve σ̂_Δ ile q95 **bilgi satırı 0 ("kapı altı taban")** olarak yazılır.
- **İ1-E3. Günlük ÇİF saklamak dondurulmuş zinciri bozar.** TR-5b §3.2 adım 4'ün enerji reddi, medyanı her
  yer-penceresinin kendi [T − 1095, T − 8] saatlerinden alır. Ardışık T'ler aynı günü farklı medyanlarla görür. Bu yüzden
  günlük ÇİF, T'den bağımsız olarak bir kez kurulup saklanamaz (§5.5). Düzeltme: saatlik ÇİF, RMS ve tamlık saklanır.
  Bu C'de ≈ 4,0 GB, A'da ≈ 6,1 GB'tır.
- **İ1-E4. Aşama 0 betiği yok (Z1).** G0 ancak betikle bağlanır. TR-5b İNCELEME-2'nin bulduğu kusurlar (sha denetimi,
  yeniden deneme, eksikken kapı vermeme, yarım satır, atomik yazım, koşullu yatay kural) burada yinelenmemeli.
  Betiğin karşılaması gereken şartlar aşağıda kesin bir liste olarak verildi.

Önemli bulgular beş tane (İ1-Ö1–Ö5). En önemlisi İ1-Ö1: "karşılanmadı" eşiği istasyon düzeyi ile kontrol düzeyi
arasındaki farkı yanlış yönde ele alıyor. İstasyon düzeyi, "karşılandı" için tutucudur, "karşılanmadı" için değildir.

Düzeltmelerin hepsi metindir ya da henüz yazılmamış kodun şartıdır. Sayım, örneklem, §3 zinciri, kapı tanımı,
"karşılandı" eşiği (U < %0,20) ve iki yönlü önyükleme değişmez. Değişen eşik yalnız "karşılanmadı"nınkidir (İ1-Ö1);
değişen aralık yalnız q95'inkidir (İ1-Ö2). Yeni sayım ve dalga formu erişimi gerekmez. Üçüncü tura gerek yoktur. Ama
aşama 0 betiği ve dv/v koşu kodu, ilk ağ isteğinden önce bağımsız kod incelemesinden geçer (İ1-E4, İ1-Ö4).

**Bağımsız olarak doğrulananlar.**
- **Sayım.** `tr4_onkayit_sayim.py` karalama kopyasında arşivlenmiş girdilerle koşuldu (2,5 sn). Arşivler:
  `tr5_ham_ustveri` `27837799…`, `tr5b_kat` `1bdfec2c…`. `tr4_onkayit_sayim.json` `39e91fce…` ve `tr4_pencereler.csv`
  `166e42ea…` **bit düzeyinde aynı**. Yer düzeyinde T başına 15, 16, 15, 14, 14, 9, 10, 9; 102 yer-penceresi; 21 yer;
  ISK + KAVV tek yer. Eleme nedenleri 115 / 44 (20 + 18 + 6) / 29 / 3 / 3 / 110 aynı. Hacim 298,5 / 196,7 GB, 53 150 /
  35 020 istasyon-gün, 1752 istek, 486 / 320 KiB/s aynı. Aşama 0 istekleri 26 + 502 + 84 + 45 + 90 + 24 = 771 aynı.
  Değişke sayıları (86, 46, 92, 59, 118, 72, 39, 39) aynı.
- **Yer sayımı bağımsız yazımla** (`inc1_kapi_hacim.py`, yalnız csv'den): 15, 16, 15, 14, 14, 9, 10, 9 / 102 / 21;
  C hacmi 196,7 GB.
- **Kademe C başvurusu** (`inc1_yeniden.py ref`): 60 dondurulmuş dizinin C maskesiyle Δ'ları, bu betikte
  `tr5b_yapay` fonksiyonlarıyla yeniden kuruldu. Geçerlilik uyuşmazlığı 0. En büyük fark Δ'da 4,9·10⁻⁷ %, oranda
  4,8·10⁻⁶; toleranslar %0,0005 ve 0,005. `tr4_yapay_ref.json` 2. adımın (b) başvurusu olarak geçerli.
- **§6.1 C | CC10 ≈ 0,5 satırı** (`inc1_yeniden.py olcum`; 100 tekrar, tek süreç, aynı tohumlar): 0,91 / 0,0259 % /
  0,901 [0,839; 0,945]. Kayıtlı değerlerle **aynı**.
- **§6.2 kesinlik**, bağımsız yazımla (`inc1_kesinlik.py`): yer düzeyi (Z12 düzeltilmiş), R = 300, B = 300.

  | Ana satır (C, ρ 0,3) | Ön kayıt (istasyon, R 200) | Bağımsız (yer, R 300) |
  |---|---|---|
  | σ̂ / σ medyanı | 0,96–0,99 | 0,99–1,00 |
  | σ aralığı genişliği / σ | 0,68–0,71 | 0,72–0,74 |
  | Kapsama σ / q95 | 0,97–1,00 / 0,88–0,93 | 0,98–1,00 / 0,87–0,90 |
  | Karşılandı, σ 0,10 / 0,15 / 0,20 | 1,00 / 0,59 / 0,03 | 1,00 / 0,43 / 0,01 |
  | Karşılanmadı (L > %0,20), σ 0,30 | 0,28 | 0,19 |

  Tek fark σ = %0,15'teki "karşılandı" olasılığıdır (0,59 ve 0,43). Bu nokta eşiğe yakındır ve σ̂'nın medyan
  sapmasına duyarlıdır: ön kayıtta 0,96, bağımsız yazımda 0,99. Metin bu değeri "≈ 0,4–0,6" diye yazar (İ1-Ö2).
- **İşlem süresi (Z5)**, `inc1_islem_suresi.py`: bir istasyon-günün ön işlemi ve saatlik ÇİF'i 0,54 sn sürüyor (numpy, tek
  çekirdek, yapay veri; miniSEED çözme ve germe hariç). C'de ≈ 5,3 saat, A'da ≈ 8 saat. İndirmenin yanında küçük.
- **Kaynaklar.** 1,3 bayt/örnek TR-5 §5.1'de ölçüldü (KO.ISK HHZ 1 gün, 11,2 MB). Hız ölçümleri TR-7_SAYIM'da (341 / 633,
  ≤ 1 MB) ve TR-5'te (40 KB/s, 11,2 MB, 284 sn). Literatür satırları TR-5 §6.1 ve TR-5b §3.7 ile tutarlı (İ1-K6).

---

## B. Yazarın zayıf noktalarına (Z1–Z12) hükümler

| Z | Hüküm | Bulgu |
|---|---|---|
| Z1 aşama 0 betiği yok | **Engelleyici**; şart listesi verildi | İ1-E4 |
| Z2 hız bilinmiyor | **Engelleyici**; kural yeniden yazıldı | İ1-E1 |
| Z3 kapı payı | **Engelleyici** (kapı altında σ yok); kapı kalır | İ1-E2 |
| Z4 istasyon / kontrol düzeyi | **Önemli**; "karşılanmadı" eşiği %0,245 | İ1-Ö1 |
| Z5 işlem süresi | Çözüldü: ≈ 0,54 sn/istasyon-gün | İ1-K2 |
| Z6 kademe C zincirden sapar | KABUL. Başvuru dizileri ve (ii-a) yeterli | – |
| Z7 olaysızlık eşikleri, Samos | Kural KALIR; Samos cümlesi yanlış; bir değişke eklenir | İ1-Ö5 |
| Z8 yapay modelde ortam gürültüsü yok | KABUL. ρ 0,6 satırı bağlayıcı zayıflık olarak yazılır | İ1-Ö2 |
| Z9 1,3 bayt/örnek | Metin yanlış: tek örnekte ölçüldü | İ1-K1 |
| Z10 PK yok | Uzak PK kapsam dışı; "karşılandı"nın anlamı daraltılır, ücretsiz bilgi satırı eklenir | İ1-Ö3 |
| Z11 asimetri, q95 kapsaması | Asimetri bilerek kabul edilir ve sayıyla yazılır; q95 aralığının yöntemi ve adı düzeltilir | İ1-Ö2 |
| Z12 benzetim birimi | KABUL. Yer düzeyi yeniden benzetim aynı sonucu veriyor | – |

### Z3 ayrıntısı: kapı payı ve TR-5b'nin küçülmesi

TR-5b'de 31 → 18 küçülmesi (%42) bir küme sayısındaydı. O sayının çoğu Z boş aylarından geldi (1246 pencerenin 547'si).
TR-4'ün sayıları Z ay yoklamasını zaten içeriyor. TR-5b'de pencere düzeyinde Z dışındaki kayıplar şunlardı: üç bileşen
yok 99 / 1246 (%7,9), aygıt 110 / 1147 (%9,6), yatay 12 / 490 (%2,4). Bileşik kayıp ≈ %19'dur. Yazarın "≈ %9 + %9"
okuması doğrudur. Ama gün düzeyi doluluk (1b) bilinmiyor ve KO'ya özgü oranlar ölçülmedi. Bu yüzden %30–40 kayıp
dışlanamaz.

Kapının kırılma olasılığı (`inc1_kapi_hacim.json`, 20 000 çekiliş; yer-penceresi / yer / karışık kayıp):

| Kayıp | %10 | %20 | %30 | %40 | %50 |
|---|---|---|---|---|---|
| P(kapı kırılır) | 0,00–0,01 | 0,02–0,13 | 0,26–0,43 | 0,69–0,75 | 0,92–0,95 |
| Kalan yer-penceresi (medyan) | 92–93 | 82 | 71–72 | 61–62 | 51 |

Tek tip kayıpta kapı %29'da kırılır. Kapının kendisi değiştirilmez. Kapının amacı, bağlayıcı (c) hükmünü korumaktır.
Ama kapı altında da ölçü bilgi taşır: %40 yer kaybında (≈ 47 geçerli yer-penceresi) σ aralığının genişliği
≈ 0,95–1,0 σ'dır. σ_Δ %0,10 ise "U < %0,20" yine 0,94–0,98 olasılıkla gelir. Metin bugün bu durumda σ̂'yı hiç
vermiyor (İ1-E2).

### Z2 ayrıntısı: 0 € bulut düzeni gerçekten yürür mü

- **Disk:** Yürür. Yerel tepe bir istasyon-aylık ham veridir (0,11–0,17 GB) ve 15 GB'ın çok altındadır. Saatlik ÇİF
  `/mnt/project-files/` altında C'de ≈ 4,0 GB, A'da ≈ 6,1 GB tutar.
- **İşlem:** Yürür. C ≈ 5,3 saat, A ≈ 8 saat; miniSEED çözme hariç.
- **İş sayısı:** Darboğaz budur. C, 341 KiB/s'de ≈ 80 iki saatlik iştir, 106 KiB/s'de ≈ 250. İşlerin zincirlenmesi
  (tetikleyici ya da kök oturum) koşu düzeninin parçası olmalı ve aşama 0'da provası yapılmalı (İ1-E4 madde 12).
- **En kötü hız:** 23 KiB/s'de C 97 gün sürer, 40 KiB/s'de 56 gün. Kapıyı koruyan hiçbir küme bu hızlarda 21 güne
  sığmaz. Kapı için en az ≈ 10 yer × iki örtüşmeyen 3 yıllık pencere gerekir; bu ≥ 81 GB eder. Pratikte en küçük küme
  T 2017–2020'dir: 134,7 GB, 60 yer-penceresi. Hacim yer sayısıyla orantılıdır. T'leri azaltmak hacmi az küçültür,
  çünkü pencereler örtüşür: örtüşmeyen T 2018/2021/2024 kümesi 157,5 GB'tır, ama yalnız 39 yer-penceresi verir.
- **Kademe D gerekli mi:** Ayrı bir örnekleme olarak gerekli değil. Gerekli olan, kesik koşunun önceden tanımlı en
  küçük kümesidir. Bu küme **D = C örneklemesi, T 2017–2021**'dir: 153,6 GB, 74 yer-penceresi, kapı sayıları 15 / 16 /
  15 / 14 / 14. Kapı %29'a kadar tek tip kayba dayanır. Kronolojik indirme sırasıyla D, C'nin ilk %78'idir; ayrı bir
  karar gerektirmez. D 21 güne v ≥ 83 KiB/s ile sığar, tam C v ≥ 106 KiB/s ile.
  D'nin kesinliği (`inc1_kesinlik_D.json`): σ aralığının genişliği 0,81–0,89 σ (tam C'de 0,72–0,82). "Karşılandı"
  olasılığı σ %0,10'da 0,93–1,00, σ = %0,20'de 0,02 (ρ 0,3) ve 0,10 (ρ 0,6). D, 23–40 KiB/s'yi kurtarmaz, yalnız
  83–106 KiB/s bandını kurtarır.
- **Kademe seçiminde oynama payı:** A / C seçimi yalnız v'ye ve aşama 0'ın hacmine bağlıdır, dv/v'ye bağlı değildir. Bu
  doğru. Oynama payı "ertelendi"dedir: son durum değildir ve seçenekleri sonradan seçilir. İ1-E1 bunu kapatır.

## C. Numaralı bulgular ve düzeltme metinleri

Kök oturum aşağıdaki metinleri harfiyen işler. "Değiştir" verilen metnin tamamını yerine koyar; "ekle" verilen yere
ekler. Paragraf ve madde adresleri sürüm 1'e göredir.

### İ1-E1 (E). Aktarım: aşama H, kademe, bütçe, kesik koşu, son hüküm

**§5.2 değiştir:**
> **5.2 Aşama H (hız).** 8 istek, üretim biçiminde. Her istek, tek bir istasyonun 5 gününün 4 saatlik üç bileşen
> penceresini tek bir dataselect POST isteğinde ister (≈ 28 MB). İstasyon ve günler ana örneklemin yer-pencerelerinden,
> 2014–2023 içinden, `sha256("tr4-asamaH|20261202")` tohumuyla seçilir. Tek akış, istekler arası ≥ 2 sn. İstek başına en
> çok 15 dk; aşılırsa o ana kadarki bayt ve süre sayılır. v = Σ bayt / Σ süre (bağlantı ve bekleme dahil). Gövde
> çözülmez, açılmaz, saklanmaz; yalnız bayt sayısı ve sha256 yazılır. Bayt / beklenen örnek sayısı Z9'u ölçer.
> KOERI POST'u reddederse istekler gün gün GET ile atılır, v bu biçimle ölçülür ve üretim de bu biçimle yapılır.
> Gerekçe: 341 ve 633 KiB/s ≤ 1 MB'lık tek isteklerden geldi, 40 KiB/s 11,2 MB'lık 284 sn'lik sürekli aktarımdan.
> Üretim istekleri istasyon-ay başına 110–170 MB'tır. Hız ancak üretim boyutundaki isteklerle ölçülür. Bu istekler
> ölçüde kullanılmaz.

**§5.3 değiştir:**
> **5.3 Kademe, bütçe ve kesik koşu (veri görülmeden; yalnız v'den ve aşama 0'ın hacminden).** V_A ve V_C, aşama 0'dan
> sonra dolu kalan yer-pencerelerinin §5.4 formülüyle hacmidir (21 yerde 298,5 / 196,7 GB). V_D, bunların T 2017–2021
> kısmıdır (21 yerde 153,6 GB; 74 yer-penceresi; T başına 15 / 16 / 15 / 14 / 14 yer). **Bütçe:** etkin indirme süresi
> 21 gün (504 iş-saati) ya da ilk indirme isteğinden itibaren 42 takvim günü; hangisi önce dolarsa.
> 1. V_A / v ≤ 7 gün → **A**.
> 2. Değilse V_D / v ≤ 21 gün → **C**.
> 3. Değilse aşama H, en az 2 gün arayla en çok 2 kez daha koşulur. v üç ölçümün medyanıdır; 1–2 yeniden uygulanır.
> 4. Hâlâ seçilmezse hüküm **"veri yok (aktarım hızı)"**dır.
>
> **Kronolojik sıra ve kesik koşu.** İndirme ay ay gider: 2014-01'den 2023-12'ye, her ayda yerler kod sırasıyla. Bir
> yer-penceresi, bütün istasyon-ay istekleri kesin kodla tamamlanınca "indirildi" sayılır. Bütçe dolarsa indirme durur.
> Analiz yalnız bütün yer-pencereleri indirilmiş T'lerle yapılır. Kalıp T'de kademe "[A | C], kesik, T [ilk]–[son]"
> diye yazılır. Bütçe dolduğunda T 2017–2021 tamamlanmamışsa ya da tamamlanan T'lerle kapı (§4.3 adım 0) tutmuyorsa hüküm
> **"veri yok (indirme bütçesi)"**dır. Kesme yalnız takvime bağlıdır: indirme bitmeden ya da kesilmeden hiçbir ε ya da Δ
> hesaplanmaz (§5.5).
>
> **Önceden bildirilen süreler** (21 yer; v = 23 / 40 / 83 / 106 / 341 KiB/s): V_C 97 / 56 / 27 / 21 / 6,5 gün;
> V_D 76 / 43 / 21 / 16 / 5,1 gün. 40 KiB/s ve altında kapıyı koruyan hiçbir 0 € tasarım bütçeye sığmaz. Bu hızlarda
> "veri yok (aktarım hızı)" beklenen sonuçtur.
>
> Kural tek akış ister. İki paralel akış, KOERI ile özel düzen ya da T veya yer kapsamının değiştirilmesi yeni sürüm ve
> yeni inceleme ister. Sunucu KOERI hızını artırmaz.

**§4.3 adım 0'daki "Ara durum, hüküm değil: …" maddesi değiştir:**
> - **Ara durum, hüküm değil:** §5.3 madde 3'ün yinelemeleri sürerken "ertelendi (aktarım hızı)" yazılır. Bu durum en
>   çok 5 gün sürer ve §5.3 madde 1, 2 ya da 4 ile biter.

**§4.5 tablosuna iki satır ekle** (adım "0" satırından sonra):

| Hüküm adı (aynen) | Adım | Şart | Zorunlu ek metin |
|---|---|---|---|
| veri yok (aktarım hızı) | 0 | §5.3 madde 4 | "aşama H hızları [..] KiB/s; medyan [..]; V_D / v = [..] gün; bilgi satırı 0: hesaplanmadı (indirme yok)" |
| veri yok (indirme bütçesi) | 0 | §5.3 kesik koşu | "tamamlanan T: [..]; T başına yer: [..]; etkin süre [..] gün, takvim [..] gün; bilgi satırı 0: [..]" |

**§4.5 tablosunun altındaki "Ara durum (hüküm değil): …" cümlesini değiştir:**
> Ara durum (hüküm değil): "ertelendi (aktarım hızı)", ek metin "ölçülen hız [..] KiB/s (ölçüm [..] adet); V_D / v =
> [..] gün". En çok 5 gün sürer (§4.3 adım 0).

**Başlıktaki "Koşu düzeni" paragrafını değiştir:**
> **Koşu düzeni.** Aşama 0 (≈ 630 hafif istek, bulut oturumu, 0 €) → aşama H (8 üretim biçiminde istek, §5.2) → kademe
> (A ya da C, yalnız hızdan ve aşama 0'ın hacminden; §5.3) → kronolojik indirme ve saatlik ÇİF (0 € bulut oturumunda,
> her biri ≤ 2 saatlik, kaldığı yerden süren işler; bütçe 21 etkin gün / 42 takvim günü) → ölçü. Bütçe dolarsa analiz
> tamamlanmış T'lerle yapılır; en küçük küme T 2017–2021'dir (153,6 GB). 40 KiB/s ve altında hiçbir kapıyı koruyan küme
> bütçeye sığmaz; hüküm "veri yok (aktarım hızı)" olur. Sunucu kiralanmaz; kiralama Erdem'in onayını ister ve hızı
> artırmaz.

**§11 madde (a) değiştir:**
> - (a) "veri yok (aktarım hızı)" ile kapanırsa: en erken 30 gün sonra, tasarım değişmeden, §5.2–5.3 aynen bir kez daha
>   koşulabilir. Bu yeni sürüm değildir; sürüm 1'in değişiklik kaydına yazılır ve inceleme gerektirmez. Aşama 0
>   yeniden koşulmaz.

**§11'in ilk cümlesinde** "'Veri yok' ya da 'ertelendi' ile kapanırsa" ifadesi "'Veri yok' ile kapanırsa" olur.

**Z2 maddesini değiştir:**
> - **Z2. Hız bilinmiyor (İNCELEME-1 İ1-E1).** Kural kapalıdır: A / C yalnız v'den, kronolojik sıra, 21 / 42 günlük
>   bütçe, kesik koşu (en küçük küme T 2017–2021). 40 KiB/s ve altında sonuç "veri yok (aktarım hızı)"dır.

### İ1-E2 (E). Kapı altı taban: bilgi satırı 0

**§4.3'ün giriş paragrafındaki** "Bir adım hüküm verirse sonrakiler koşmaz; ama o ana kadar hesaplanabilen her sayı ve
bilgi satırı 'kapı altı' etiketiyle yazılır." **cümlesini değiştir:**
> Bir adım hüküm verirse hüküm kesinleşir ve değişmez. "geçersiz (kod)" ile kesinleşirse sonraki adımların hiçbiri koşmaz
> ve hiçbir Δ sayısı yazılmaz. "veri yok" ile kesinleşirse (adım 0, 1, 4 ya da §5.3'ün bütçesi), dolu kalan
> yer-pencereleri yine işlenir. Kapıyı tutmasalar da indirme §5.3'e göre yapılır ve 2. ile 3. adımlar koşar. İkisi de
> geçerse 5. adımın sayıları **bilgi satırı 0 ("kapı altı taban")** olarak yazılır. Bilgi satırı 0 (c) sınamasını
> yapmaz. Bilgi satırı 0 ancak ≥ 30 geçerli yer-penceresi ve ≥ 6 yer varsa hesaplanır; yoksa "hesaplanmadı (n = [..],
> yer = [..])" yazılır. Aşama 0'dan sonra dolu yer-penceresi < 30 ise indirme yapılmaz. Gerekçe: %40 yer kaybında
> (≈ 47 geçerli yer-penceresi) σ aralığının genişliği ≈ 1,0 σ'dır; ölçü kapı altında da bilgi taşır (İNCELEME-1).

**§4.5 tablosunda** "veri yok (aşama 0)", "veri yok (gün doluluğu)" ve "veri yok (ε geçerliliği)" satırlarının
"Zorunlu ek metin" hücrelerinin sonuna ekle:
> "; bilgi satırı 0: σ̂_Δ [..] % ([L–U]), q95 [..] % ([L–U]), n [..], yer [..], T [..]" ya da "; bilgi satırı 0:
> hesaplanmadı (n = [..], yer = [..])"

**§8'in başına ekle:**
> 0. **Kapı altı taban** (yalnız "veri yok" hükümlerinde; §4.3): σ̂_Δ, q95, %90 / %95 iki yönlü önyükleme aralıkları,
>    n, yer ve T listesi. Ek metin aynen: "Kapı altı; TR-5b (c) için dayanak değildir; hüküm [hüküm adı]."

**Z3 maddesini değiştir:**
> - **Z3. Kapı payı (İNCELEME-1 İ1-E2).** TR-5b'de Z dışı pencere kaybı ≈ %19'du (üç bileşen %7,9, aygıt %9,6, yatay
>   %2,4). 31 → 18 (%42) bir küme sayısıdır ve Z kaybını içerir. Gün düzeyi kayıp bilinmiyor. Rastgele kayıpta kapının
>   kırılma olasılığı %20'de 0,02–0,13, %30'da 0,26–0,43, %40'ta 0,69–0,75; tek tip kayıpta kapı %29'da kırılır. Kapı
>   kırılırsa hüküm "veri yok"tur ve σ̂_Δ bilgi satırı 0'da yazılır.

### İ1-E3 (E). Saatlik ÇİF saklama ve sonuç körlüğü

**§5.5'teki "Ham veri istasyon-ay işlendikten sonra silinir; … (≈ 0,11–0,17 GB)." cümlelerini değiştir:**
> Ham veri istasyon-ay işlendikten sonra silinir. Saklanan, **saatlik** ÇİF'lerdir (3 çift × 2401 gecikme × float32
> ≈ 29 KB/saat; 4 saatlik günde ≈ 115 KB). Ayrıca her saat-bileşen için 0,5–2 Hz RMS'i ve örnek tamlığı saklanır.
> Gerekçe: TR-5b §3.2 adım 4'ün enerji reddi, medyanı her yer-penceresinin kendi [T − 1095, T − 8] saatlerinden alır.
> Ardışık T'ler aynı günü farklı medyanlarla görür, bu yüzden günlük ÇİF T'den bağımsız saklanamaz. Günlük ÇİF her
> yer-penceresi için saatlik ÇİF'lerden, o pencerenin medyanıyla kurulur. 1b'nin gün doluluğu (üç bileşen, saat ≥ %99
> tamlık) da saklanan tamlıktan hesaplanır. Saklama C'de ≈ 4,0 GB, A'da ≈ 6,1 GB'tır. Dosyalar `/mnt/project-files/`
> altına yazılır: istasyon-ay başına bir dosya, sha256'sıyla, geçici adla yazılıp yeniden adlandırılarak. Durum dosyası
> da oradadır ve her iş oradan sürer. Yerel disk tepe değeri bir istasyon-aylık ham veri (≈ 0,11–0,17 GB) ile o ayın
> saatlik ÇİF'idir. **İndirme bitmeden ya da §5.3'e göre kesilmeden hiçbir ε ya da Δ hesaplanmaz.** Yalnız saatlik ÇİF,
> RMS ve tamlık yazılır.

**§5.5'teki "İşlem süresi indirmenin yanında küçüktür (kestirilmedi; zayıf nokta Z5)." cümlesini değiştir:**
> İşlem süresi indirmenin yanında küçüktür. Bir istasyon-günün ön işlemi ve saatlik ÇİF'i ≈ 0,54 sn sürer (yapay veri,
> numpy, tek çekirdek; miniSEED çözme ve germe hariç; İNCELEME-1). Bu C'de ≈ 5,3, A'da ≈ 8 saattir. İlk indirilen
> istasyon-ayda gerçek süre ölçülür ve günlüğe yazılır.

**§3.2'nin "Kademe C" maddesinin sonuna ekle:**
> "Gün", TR-5b §3.1'in yerel ortalama güneş tarihi d'dir; 1–20. günler d'ye göre sayılır.

### İ1-E4 (E). Aşama 0 betiği: şartlar (Z1)

**§5.1'in son paragrafını** ("Aşama 0 kodu, TR-5b'deki gibi, … (zayıf nokta Z1).") **değiştir:**
> Aşama 0 betiği `kayit/turetme/tr4/tr4_asama0.py`'dir. `tr5b_asama0.py`'nin düzeltilmiş hâlinden (sürüm 3)
> türetilir ve İNCELEME-1 İ1-E4'ün 14 şartını karşılar. Ağsız kuru kipte ve sahte bir yanıtlayıcıyla sınanır. Betik
> bağımsız bir kod incelemesinden geçer ve ilk ağ isteğinden önce dondurulur (§5.6).

**İstek tablosu (§5.1) değiştir:**

| İstek | Sayı |
|---|---|
| Üstveri (istasyon, kanal yanıtı) | 26 |
| Yatay yoklama: her aday yer-penceresinin A, B, C dilimlerinin orta ayı × 2 yatay bileşen (temsilci olmayan KO.KAVV hariç) | 468 |
| Yoklanmamış Z adayları (GAZK T 2023, 2024; GEML T 2024), ay başına | 84 |
| Bilgi satırı 13 (yalnız SLVT; 2024-03…2025-05) Z | 15 |
| Aynısı, yatay | 30 |
| Aşama H hız denemesi (§5.2; üretim biçiminde) | 8 |
| **Toplam** | **631 (≈ 0,5 saat hafif istek + aşama H ≈ 0,1–1,6 saat)** |

Gerekçe: KO.KAVV'nin 34 yatay isteği gereksiz; temsilci sabittir ve KAVV indirilmez. BOTS ve NMR9'un 2024-03…2025-05
istekleri gereksiz; ikisi de §3.4'e göre kullanılamaz (kanal kapsamı yok). Aşama H İ1-E1'e göre 8 istektir.

**`tr4_asama0.py`'nin şartları** (kod incelemesi bu listeyi madde madde denetler):

1. **Girdi sha256'ları her kipte denetlenir; uyuşmazlıkta iş durur.** Denetlenenler: `tr4_pencereler.csv`
   `166e42ea5b2fbe97ed608daf0f533252c13ef0959d78950c9b3213998915a4ef`, `tr4_onkayit_sayim.json`
   `39e91fcecb2b6c9554a7f9d79569b1b81fc20427a72ca207244a85b5151cb2ee`, `onbellek.jsonl` (`ce4fe524…`, tam değer
   dondurmada), `marmara_fed_kanal.txt` (`dbcc3ba8…`). Sabitler kodda yazılıdır; `None` olamaz (`assert`).
2. **Aday kümesi yalnız csv'den kurulur:** `ana_T ∧ (DOLU_ana ∨ aday_yoklanmamis)`, temsilci kuralı (ISK yerinde
   yalnız KO.ISK). Toplam 105 istasyon-penceresi (110 + 3 − 8 KAVV). Temsilci aşama 0'dan sonra yeniden seçilmez.
   `kuru` kip §5.1 tablosunun sayılarını (26 / 468 / 84 / 15 / 30 / 8) yeniden üretir; sapma varsa durur.
3. **Üstveri:** KOERI istasyon servisi, `level=channel`, `BH?,HH?`, istasyon başına, [ilk a, son b] aralığı. Dosya
   önce geçici adla yazılır, sonra `os.replace` ile yerine konur. Kesin olmayan kodda en çok iki deneme yapılır.
4. **Kanal seçimi ve aygıt kuralı** TR-5b §3.1 ve `tr5b_asama0.kanal_sec`'in aynısıdır: üç bileşen kapsama, BH sonra
   HH, konum sırası, N/E sonra 1/2, 30 günlük boşluk birleştirme. Aygıt kuralı üç bileşende [a, b]'de uygulanır. Z
   önizlemesinden farklı sonuç veren pencereler ayrıca listelenir.
5. **Yoklama biçimi** TR-5b'nin aynısıdır: ayın 15'i 12:00–12:01 UTC; tek akış; istekler arası ≥ 2 sn; genel
   User-Agent; TLS doğrulaması açık; 429/503'te Retry-After (en çok 120 sn). Gövde okunur, saklanmaz, çözülmez.
6. **Kesin kodlar `(200, 204, 404, 401, 403)`.** Öteki kodlar ve bağlantı hataları sonraki çağrıda bir kez yeniden
   denenir; en çok iki deneme. `son_durum`, `satirlar` ve `ekle_ac` `tr5b_asama0.py`'deki gibidir: yarım satır yok
   sayılır ve yeni satırı bozmaz.
7. **Z durumu iki kaynaktan okunur:** 2012–2023 için TR-5 önbelleği (`KO.<ist>.<YYYY-MM>`; `loc=*`, `BHZ,HHZ`), üç
   aday ve SLVT için yeni yoklama. KO'nun bütün kanal epoklarında konum kodu boştur, bu yüzden `loc=*` tek kanala düşer;
   kod bunu `assert` ile denetler.
8. **Yatay kural koşulludur** (TR-5b İ2-E2). Bir dilimin yatay istekleri, aynı ayın Z'si "var" ise bilgilidir. Bilgili
   her dilimde iki yatay istek de "var" olmalıdır. Hiçbir dilim bilgili değilse neden kodu `yatay_bilgisiz`'dir.
9. **Körlük `assert`'leri:** her isteğin bitişi ≤ 2025-12-31; hüküm yer-pencerelerinin yoklamaları ≤ 2023-12-24;
   bilgi satırı 13'ünkiler ≤ 2025-05-31. Bilgi satırı 13'ün istekleri ayrı rol etiketiyle yazılır ve G0 sayımına girmez.
10. **`say`:** istek listesindeki her istek ve her üstveri isteği tamamlanmadıkça hiçbir sayı ve hüküm vermez ve
    durur ("aşama 0 tamamlanmadı: [n] istek, [m] üstveri; G0 verilmez"). Çıktı `asama0_sonuc.json`'dur. İçeriği:
    yer düzeyinde T başına dolu yer; kapı (adım 0); neden kırılımı (`uc_bilesen_yok`, `aygit`, `z_ay`, `yatay`,
    `yatay_bilgisiz`); `istek_durum` (`var`, `bos`, `kisitli`, `hata`, rol kırılımıyla); `ustveri_alinamayan`; V_A, V_C,
    V_D (§5.3); önbellek, istek listesi ve girdi sha256'ları. Dosya geçici adla yazılıp `os.replace` ile konur ve
    `sort_keys=True` ile yazılır. Aynı girdi aynı baytları verir.
11. **Aşama H kipi (`hiz`):** §5.2'nin aynısı. Seçim tohumludur ve kuru kipte yazdırılır. İstek başına bayt, süre, kod ve
    sha256 yazılır. Kademe kararı (§5.3 madde 1–4) koddaki sabit eşiklerle ve `asama0_sonuc.json`'un V'leriyle verilir.
    Elle girdi alınmaz.
12. **Süre:** `sure_sn` en çok 6000'dir. Kalan süre o kipteki en uzun beklenen istek süresinin iki katından azsa yeni
    istek başlatılmaz. Sürdürme provası: `urlopen` yasaklanıp `_getir` sahte bir yanıtlayıcıyla değiştirilerek üç ardışık
    çağrı koşulur. Gösterilmesi gerekenler: hata satırları ikinci çağrıda yeniden denenir, üçüncüde denenmez; çift
    kayıt 0; yarım satır `say`'ı düşürmez; eksikte G0 verilmez. Prova çıktısı `kayit/turetme/tr4/` altına yazılır.
13. **Ağ kipleri** `--ag-onay` bayrağı olmadan çalışmaz.
14. **Tek koşu:** aşama 0 bir kez koşulur. Önbellek silinmez, yeniden yoklama yapılmaz (§5.6).

**Z1 maddesini değiştir:**
> - **Z1. Aşama 0 betiği (İNCELEME-1 İ1-E4).** Şartlar İ1-E4'te. Betik ve ağsız provası dondurmadan önce yazılır,
>   kod incelemesinden geçer.

### İ1-Ö1 (Ö). (c) eşiği: istasyon düzeyi ve kontrol düzeyi (Z4)

**§4.3 adım 5'in ikinci maddesini değiştir:**
> - L(σ̂_Δ) > %0,245 → **"taban ölçüldü; TR-5b (c) karşılanmadı"**;

**§4.5 tablosunda** "karşılanmadı" satırının "Şart" hücresi "L(σ̂) > %0,245" olur.

**§1'in son maddesini** ("σ̂_Δ burada istasyon düzeyidir. …") **değiştir:**
> - σ̂_Δ burada **istasyon düzeyidir**. TR-5b'nin σ_Δ'sı kontrol düzeyidir. Bir kontrol 1–3 istasyonun ortalamasıdır;
>   TR-5b'nin ilk 5 adayında ortalama 1/n = 0,668'dir (TR-5b İNCELEME-2 İ2-Ö2). İstasyonlar bağımsızsa σ_kontrol
>   ≈ 0,817 · σ_istasyon olur, tam ilişkide ikisi eşittir. Bu yüzden istasyon düzeyinde σ < %0,20 ise kontrol düzeyinde
>   de < %0,20'dir; "karşılandı" tutucudur. "Karşılanmadı" ise ancak istasyon düzeyinde σ > %0,20 / 0,817 = %0,245
>   olduğunda kontrol düzeyinde de geçerlidir. §4.3 adım 5'in eşikleri buna göredir. Kontrol düzeyi eşleniği bilgi
>   satırı 6'dadır.

**Z4 maddesini değiştir:**
> - **Z4. Birim farkı (İNCELEME-1 İ1-Ö1).** "Karşılandı" eşiği U < %0,20 (tutucu), "karşılanmadı" eşiği L > %0,245
>   (= 0,20 / 0,817). Bilgi satırı 6 kontrol düzeyi eşleniğini yazar, hükmü değiştirmez.

### İ1-Ö2 (Ö). Asimetri, aralık yöntemi ve q95'in anlamı (Z11, Z8)

**§4.2'nin son iki cümlesini** ("Her iki ölçü için %90 yüzdelik aralığı [L, U] yazılır. … Benzetimde bu aralığın
kapsaması §6.2'de.") **değiştir:**
> σ̂_Δ için 5.–95. yüzdelikler [L, U] yazılır: "%90 iki yönlü önyükleme aralığı". q95 için 2,5.–97,5. yüzdelikler
> yazılır: "%95 iki yönlü önyükleme aralığı". Yer-pencereler hem yerde (aynı istasyon) hem zamanda (örtüşen pencereler,
> ortak hidroloji) ilişkili olduğu için tek yönlü önyükleme kullanılmaz. Benzetimde (İNCELEME-1, yer düzeyi, R = 300)
> σ aralığı gerçek σ_Δ'yı ρ 0,3'te 0,98–1,00, ρ 0,6'da 0,91–0,94 olasılıkla kapsar. q95 aralığı gerçek q95'i ρ 0,3'te
> 0,94–0,97, ρ 0,6'da 0,83–0,89 olasılıkla kapsar; T 2017–2021 kesik koşuda ρ 0,6'da 0,79–0,81. Aralıklar bu
> kapsamalarla anılır; "güven aralığı" denmez.

Gerekçe: %90 q95 aralığının kapsaması ρ 0,6'da 0,70–0,81'dir. Bu düşüklük σ̂ ve q̂95'in ortak yıl bileşeninden gelen
aşağı yanlılığından (q̂95 / q95 medyanı 0,89–0,96) kaynaklanır. Aralığı genişletmek bunu tümüyle gidermez, ama ρ 0,3'te
kapsamayı 0,94–0,97'ye çıkarır. σ için %80 aralık reddedildi: σ = %0,20'de yanlış "karşılandı" olasılığını ρ 0,6'da
0,13'e (D'de 0,19'a) çıkarır.

**Kalıp T'yi değiştir:**
> **Kalıp T:** "Marmara KO ağında [kademe], [n] yer-penceresinde ([yer] yer, T [ilk]–[son]), olaysız pencerelerde tek
> istasyonun bir yıllık dv/v düzey değişiminin (0,5–2 Hz, TR-5b ölçüsü) örneklem %95 niceliği q95 = [..] %'dir (%95 iki
> yönlü önyükleme aralığı [L–U]; benzetimde bu aralık gerçek değeri 0,79–0,97 olasılıkla kapsar). σ̂_Δ = [..] % (%90 iki
> yönlü önyükleme aralığı [L–U]). q95, tek istasyonda %5 yanlış alarm oranındaki saptama eşiğidir. Bu büyüklükte bir
> düzey değişimi yaklaşık yarı yarıya saptanır. %80 olasılıkla saptanacak değişim, normal yaklaşımla, ≈ q95 + 0,84 ·
> σ̂_Δ = [..] %'dir. Bu bir olasılık ya da alarm eşiği değildir. Ölçü istasyon çevresindeki sığ ortamı örnekler. Zincir
> bu ön kayıtta Marmara'da gerçek bir hız değişimiyle sınanmadı; mevsimsel genliğin yer medyanı (bilgi satırı 11)
> [..] %, 2019 Silivri δ_ko'su (bilgi satırı 14) [..]."

**Başlıktaki "Tek cümle" paragrafında** "q95, 'olaysız bir yılda tek istasyonda dv/v'nin %95 olasılıkla kalacağı sınır',
yani bu ölçüyle Marmara'da tek istasyonda algılanabilir en küçük yıl ölçekli hız değişimidir." ifadesini **değiştir:**
> q95, olaysız bir yılda tek istasyonda Δ'nın %95 olasılıkla kalacağı sınırdır. Yani bu ölçüyle Marmara'da tek
> istasyonda %5 yanlış alarm oranında saptama eşiğidir. Bu büyüklükte bir değişim yarı yarıya saptanır; %80 saptama
> ≈ q95 + 0,84 σ̂_Δ ister.

**§6.2 "Okuma"nın "Hüküm asimetrik." maddesini değiştir:**
> - **Hüküm bilerek asimetriktir.** TR-5b için yalnız "karşılandı" bir yeniden açma dayanağıdır. "Belirsiz" ve
>   "karşılanmadı" aynı sonucu doğurur: dayanak yok. Bu yüzden sınırlanan hata yanlış "karşılandı"dır. σ_Δ = %0,20'de
>   "karşılandı" olasılığı ρ 0,3'te 0,01–0,03, ρ 0,6'da 0,08; T 2017–2021 kesik koşuda 0,02 / 0,10. σ_Δ %0,10'da
>   "karşılandı" 0,95–1,00, %0,15'te ≈ 0,4–0,6 olasılıkla gelir. "Karşılanmadı" (L > %0,245; İ1-Ö1) σ_Δ %0,30'da bile
>   ≤ 0,02 olasılıklıdır; yalnız σ_Δ %0,30'un belirgin üstündeyse olasıdır. Bu önceden kabul edilir; "belirsiz" hükmü
>   σ̂'yı ve aralığını yine yazar. Kaynak: İNCELEME-1 `inc1_kesinlik.json`, `inc1_kesinlik_D.json`.

**§6.2 "Okuma"nın "q95 aralığı …" maddesini değiştir:**
> - **q95 aralığı** 2,5.–97,5. yüzdeliklerdir (§4.2). Kapsaması ρ 0,6'da ve az epokta yine 0,79–0,89'dur. Bu, ortak yıl
>   bileşeninin (ρ) bu örneklemde iyi kestirilemeyeceği anlamına gelir (Z8). Bilgi satırı 5 bu bileşeni kaba olarak
>   yazar.

**§4.6'nın "Karşılanmadı" maddesini değiştir:**
> - **Karşılanmadı:** σ_Δ kontrol düzeyinde de %0,20'nin üstündedir. TR-5b (c) yolu bu ölçüyle açılmaz. Marmara'da tek
>   istasyonla yıl ölçekli bir düzey değişimi ancak q95'ten büyükse olaysız yıllardan ayrılır (Kalıp T).

**Z11 maddesini değiştir:**
> - **Z11. Asimetri ve q95 aralığı (İNCELEME-1 İ1-Ö2).** Asimetri bilerek kabul edildi ve olasılıklar §6.2'de yazıldı.
>   q95 aralığı %95 iki yönlü önyükleme aralığıdır; kapsaması kendi adıyla birlikte yazılır.

### İ1-Ö3 (Ö). Pozitif kontrol yokluğu: "karşılandı"nın anlamı ve ücretsiz bilgi satırı (Z10)

Hüküm: Uzak bir pozitif kontrol (TR-5b P2 türü, KO dışı olaylar) TR-4'ün kapsamı dışında kalır. KOERI dışında indirme
gerektirir ve 0 € bütçeyi aşar. Ama bunun bir bedeli var. Duyarsız bir zincir de küçük σ̂ üretir, yani zincir hatası
"karşılandı" yönüne yanlılık yaratır. (ii-a) bunu yakalamaz: ÇİF olmayan bir bileşen (örneğin aygıt kaynaklı sabit
ilişki) de yapay germeyi geri ölçer. Bu yüzden "karşılandı"nın kullanımı koşula bağlanır.

**§4.6'nın "Karşılandı" maddesini değiştir:**
> - **Karşılandı:** TR-5b (c) şartının σ yarısı Marmara verisinde tutar. Bu, yeni bir ön kayıtla yeniden açmanın
>   dayanaklarından biridir; tek başına yeniden açma değildir. Nedenleri: (1) TR-5b'nin kontrolleri Marmara'da değil.
>   (2) TR-5b aşama 0'da K₀ = 18 < 20 ile kapandı; yeni ön kayıt K kapısını σ̂_Δ ile yeniden türetmelidir. (3) TR-4
>   zincirin gerçek bir hız değişimini gördüğünü göstermez (Z10); duyarsız bir zincir de küçük σ̂ üretir. Bu yüzden (c)
>   yoluyla açılan her ön kayıt, σ̂_Δ'ya dayanmadan önce gerçek olaylı bir pozitif kontrolü (TR-5b P2 ya da eşdeğeri)
>   geçmek zorundadır.

**§8'e ekle:**
> 14. 26 Eylül 2019 Silivri Mw 5,7 (`us70005lkl`), SLVT (36,5 km), CRLT (42,9 km), CTKS (47,7 km). δ_ko TR-5b §4.2
>     adım 8 tanımıyla, ±%2 ızgarayla hesaplanır; M5 maskesi bu satırda uygulanmaz. İstasyon başına ve ortalama
>     yazılır. Veri ana örneklemin indirdiği günlerdir (T 2020 penceresi); ek indirme yoktur. Kademe C'de olay sonrası
>     yalnız ayın 1–20. günleri vardır. Saptama olasılığı düşüktür (§3.4'teki 0,05–0,27 mertebesi); "görülmedi"
>     bilgisizdir.

**§3.4'ün son paragrafının sonuna ekle:**
> İNCELEME-1'e göre uzak bir PK kapsam dışıdır. Bedeli §4.6 "Karşılandı" maddesinin (3) şartıdır. Bilgi satırı 11
> (mevsimsel genlik) ve 14 (2019 Silivri) zincirin duyarlılığına dair bağlayıcı olmayan iki işarettir ve Kalıp T'de
> yazılır.

**Z10 maddesini değiştir:**
> - **Z10. PK yok (İNCELEME-1 İ1-Ö3).** Uzak PK kapsam dışıdır. "Karşılandı", ancak gerçek olaylı bir PK'yi geçen yeni
>   bir ön kayıtta dayanak olarak kullanılabilir. Bilgi satırları 11 ve 14 bağlayıcı olmayan iki işarettir.

### İ1-Ö4 (Ö). Dondurma anı ve aşama 0'da tek koşu

**§5.6'yı değiştir:**
> **5.6 Dondurma.** Ön kayıt, `tr4_asama0.py` ve onun ağsız provası aşama 0'ın ilk ağ isteğinden önce dondurulur ve push
> edilir. dv/v koşu kodu (`tr4_kosu.py`) bağımsız kod incelemesinden sonra ve ilk dalga formu indirme isteğinden önce
> dondurulur; sha256'sı kayda geçer. Bundan sonra kod yalnız §11'in "geçersiz (kod)" yoluyla değişir. Koşu kodu
> dondurulmuş saatlik ÇİF'lerden (§5.5) günlük ÇİF'i her yer-penceresi için yeniden kurar. Aşama 0 bir kez koşulur:
> önbellek silinmez, yeniden yoklama yapılmaz. Tek yeniden deneme, İ1-E4 madde 6'nın kesin olmayan kodlar için
> tanımladığıdır. `say` bir kez, bütün istekler tamamlanınca koşulur. `asama0_sonuc.json`, `onbellek.jsonl` ve
> `istekler.json`'un sha256'ları kayda geçer ve push edilir. G0'dan sonra aşama 0'ın hiçbir kuralı değiştirilemez.

Gerekçe: Sürüm 1'deki "3. adımdan sonra kod değiştirilemez" cümlesi, gerçek ÇİF'ler ve gün doluluğu görüldükten sonra
koşu kodunun değiştirilmesine izin veriyordu.

**§11'in son cümlesine ekle:**
> Bu yeniden koşu bir kez yapılır. İkinci kez "geçersiz (kod)" verirse hüküm kesinleşir.

### İ1-Ö5 (Ö). Olaysızlık: Samos ve Kahramanmaraş (Z7)

Hüküm: 150 / 300 / 1000 km kuralı kalır. Ama Z7'nin Samos cümlesi yanlış. Samos ana tanımda beş istasyonda dışarıda
kalıyor: GONE 251, LAP 275, KRBG 281, EDC 288, KCTX 295 km (eleme nedenlerindeki 20 istasyon-penceresi). T ≥ 2020'de
içeride kalan örneklem istasyonları ≥ 309 km'de (ERIK 309, RKY 312). 6 Şubat 2023 Kahramanmaraş M7,8 ve M7,5 örneklem
istasyonlarına 664–985 km'dedir. M ≥ 8 kuralına girmez, T 2024'ün C diliminde içeride kalır. Etkileri büyük olasılıkla
küçüktür, ama ölçülebilir ve ücretsizdir.

**Z7 maddesini değiştir:**
> - **Z7. Olaysızlık eşikleri yargıdır (İNCELEME-1 İ1-Ö5).** 150 / 300 / 1000 km ve [T − 5 y, T + 1 y) SAYIM §3.2'den
>   alındı. Samos 2020 (M7,0), 300 km kuralıyla beş istasyonda T 2020–2024'ü dışlar (GONE, LAP, KRBG, EDC, KCTX; 20
>   istasyon-penceresi). Öteki örneklem istasyonları ≥ 309 km'dedir ve içeride kalır. Kahramanmaraş 2023 (M7,8 / M7,5,
>   664–985 km) T 2024'ün C diliminde içeride kalır. 500 km değişkesi kapıyı kırar. İki etki bilgi satırı 1'de ayrı yazılır.

**§2.3'teki** "TR-5b kontrollerinin 500 km'si Marmara'da Samos 2020 (M7,0) yüzünden 2020–2024'ün bütün T'lerini düşürür
(bilgi satırı 1, N 46)." cümlesinin sonuna ekle:
> 300 km kuralıyla Samos beş istasyonda (251–295 km) dışarıda, ötekilerde (≥ 309 km) içeridedir.

**§8 madde 1'in sonuna ekle:**
> Ek değişke: pencerenin kendisinde ([T − 1095, T − 8]) M ≥ 7 ve ≤ 1000 km olayı olan yer-pencereleri dışarıda (Samos
> 2020 ve Kahramanmaraş 2023; T 2021–2024 düşer; N 60, T 2017–2020; kapı geçer).

### Küçük bulgular

**İ1-K1. 1,3 bayt/örnek (Z9).** §5.4'teki "1,3 bayt/örnek STEIM2 varsayımıdır, doğrulanamadı" ifadesi şununla
değiştirilir:
> 1,3 bayt/örnek TR-5 §5.1'de tek bir örnekte ölçüldü (KO.ISK HHZ, 1 gün, 11,2 MB → 1,30); yatay bileşenler ve öteki
> istasyonlar için ölçülmedi. Aşama H oranı yeniden ölçer.

Z9 maddesi aynı biçimde düzeltilir.

**İ1-K2. İşlem süresi (Z5).** Z5 maddesi şununla değiştirilir:
> - **Z5. İşlem süresi (İNCELEME-1).** Kaba ölçüm ≈ 0,54 sn/istasyon-gün (C ≈ 5,3 saat, A ≈ 8 saat; miniSEED çözme
>   ve germe hariç). İlk indirilen istasyon-ayda gerçek süre ölçülür.

**İ1-K3. İstek sayısı.** Başlıktaki ve §5.1'deki "771" sayıları İ1-E4 tablosuna göre "631" olur. `tr4_onkayit_sayim.py`
değiştirilmez; fark İ1-E4'te gerekçelidir.

**İ1-K4. Kapının Ek 2'den farkı.** §4.4'ün sonuna ekle:
> Ek 2'nin kapısı "≥ 5 yıl arayla iki epok" idi; orada T tanımı farklıydı. Burada 3 yıl, iki pencerenin örtüşmemesi
> için yeterli ve gerekli olan aralıktır. Değişiklik Ek 2'nin Z doluluğu görüldükten sonra, dv/v görülmeden yapıldı.
> 5 yıl arayla kapı burada da geçer, ama tam sınırdadır (2017 ve 2023: 15 ve 10 yer).

**İ1-K5. Bilgi satırı 13'ün örneklemesi.** §8 madde 13'e ekle:
> Kademeden bağımsız olarak [T − 69, T + 30] her gün indirilir, [T − 400, T − 70] kademeye göre örneklenir (§5.4'ün ek
> hacmi bu tanımladır).

**İ1-K6. Literatür tablosu.** §9 tablosunun "Durum" sütunundaki "Doğrulandı (depodaki önceki okuma)" ifadesi
"Doğrulandı (TR-5 §6.1; TR-5b §3.7)" olur. "Kaynak" sütununa DOI'ler eklenir: Hillers 2015 10.1093/gji/ggv151; Meier
2010 10.1111/j.1365-246x.2010.04550.x; Sens-Schönfelder ve Wegler 2006 10.1029/2006gl027797; Taira 2015
10.1002/2015gl065308; Clements ve Denolle 2023 10.1029/2022jb025553. van Dinther 2020 ve Delouche 2022 depoda
okunmadı; "doğrulanamadı" etiketleri doğru ve kalır.

**İ1-K7. Paralel süreç.** Ek'teki komutların altına ekle:
> `olcum` ve `pk` kipleri 4 süreçle koşar (`Pool(4)`). Paylaşılan makinede tek süreçle yeniden üretim
> `inc1_yeniden.py olcum` biçimindedir (C | CC10 ≈ 0,5 satırı 29 sn).

**İ1-K8. TR-5b'nin bugünkü durumu.** §10'un üçüncü maddesinin sonuna ekle:
> TR-5b aşama 0'da "güç yok (aşama 0)" ile kapandı (K₀ 18 / 20; ZINCIR Halka 7). (c) yolunun açılması, K kapısının da
> yeni ön kayıtta yeniden türetilmesini gerektirir.

**İ1-K9. Başlık ve durum.** Dondurmada:
- Başlıktaki durum satırı "Sürüm 2, DONDURULDU (İNCELEME-1 düzeltmeleri işlendi)" olur.
- §0'daki öncelik sırasına `TR-4_INCELEME-1.md`, bu belgeden sonra ve TR-5b'den önce eklenir.
- Sona bir "Sürüm 1 → 2 değişiklik listesi" eklenir: İ1-E1–E4, İ1-Ö1–Ö5 ve İ1-K1–K9 için birer satır, ayrıca bu
  incelemenin ve `inc1/` dosyalarının sha256'ları.

## D. Görevde sorulan kalemlere kısa hükümler

| Kalem | Hüküm |
|---|---|
| Sayılar (15, 16, 15, 14, 14, 9, 10, 9; 102; 21) | Bit düzeyinde ve bağımsız yazımla yeniden üretildi |
| Güç tablosu | Bağımsız yer düzeyi benzetimde Monte Carlo saçılımı içinde (σ %0,15'te 0,43 / 0,59 farkı) |
| Kademe C başvurusu, §6.1 C satırı | Aynı (fark ≤ 5·10⁻⁶) |
| Z3 kapı payı, σ bilgi satırı | Metin bugün sağlamıyor; bilgi satırı 0 eklenir (İ1-E2) |
| Z2 kademe kuralı, "ertelendi" | Oynama payı var, bir seçenek geçersiz, bütçe yok; kapatıldı (İ1-E1) |
| Kademe seçimi yalnız hızdan, veri görülmeden mi | Evet; V'ler aşama 0'dan, v aşama H'den. Ölçüm rejimi düzeltildi |
| 0 € bulut düzeni | Disk ve işlem yeterli; darboğaz iş sayısı ve hız. Prova şartı İ1-E4 madde 12 |
| Kademe D | Ayrı örnekleme olarak gerekmez. Kesik koşunun en küçük kümesi olarak tanımlandı: T 2017–2021, 153,6 GB, 74 yer-penceresi, v ≥ 83 KiB/s. 23–40 KiB/s'yi kurtarmaz |
| Z7 Samos | Kural kalır; metin düzeltilir; değişke eklenir (İ1-Ö5) |
| Z4 birim | "Karşılanmadı" eşiği %0,245 (İ1-Ö1) |
| Z10 PK | Uzak PK kapsam dışı; "karşılandı" koşullu; bilgi satırı 14 (İ1-Ö3) |
| Z11 asimetri, q95 | Asimetri bilerek kabul, olasılıklarıyla yazılır; q95 %95 aralığı ve doğru ad; q95'in anlamı (%50 saptama) Kalıp T'de (İ1-Ö2) |
| Körlük | Sağlam. 2026 verisi yok; istekler ≤ 2025-12-31, hüküm verisi ≤ 2023-12-24, bilgi satırı 13 ≤ 2025-05-31; katalog ≤ 2025-12-31; GNSS yok. Kodda `assert` şartı İ1-E4 madde 9 |
| Tek koşu | Sağlam, iki ek: kod dondurma indirmeden önce, aşama 0 tek koşu (İ1-Ö4) |
| Kapalı hüküm listesi | Sağlam; iki "veri yok" adı eklenir, "ertelendi" 5 günle sınırlanır (İ1-E1) |
| Yeniden açma (§11) | Yeterli; (a) tasarım değişmeden tek tekrar olarak netleşti |
| İstanbul mutlak olasılığı | Yok; §1 ve §10'da yasak cümlesi yerinde |
| Literatür | Doğrulanmış satırlar TR-5 / TR-5b ile tutarlı; iki "doğrulanamadı" doğru (İ1-K6) |

## E. Yeniden hesaplar ve betikler (`kayit/turetme/tr4/inc1/`)

| Betik | Ne yapar | Çıktı | Süre |
|---|---|---|---|
| `inc1_kapi_hacim.py <tr4_pencereler.csv>` | Yer sayımı; alt kümelerde kapı; kayıp benzetimi (20 000, tohum 404040); A / C / D hacmi; yer sıralı kesik koşu | `inc1_kapi_hacim.json` | 16 sn |
| `inc1_kesinlik.py <csv> 300 [D]` | Bağımsız σ̂ / q95 kesinliği, yer düzeyi; %90 / %80 σ, %90 / %95 q95 aralığı; eşik 0,20 / 0,245; tam, T 2017–2020, %40 yer kaybı; D: T 2017–2021 | `inc1_kesinlik.json`, `inc1_kesinlik_D.json` | 228 sn + 74 sn |
| `inc1_yeniden.py ref <npz>` | Kademe C başvuru Δ'ları, dizi dizi | `inc1_yeniden_ref.json` | 45 sn |
| `inc1_yeniden.py olcum` | §6.1 C \| CC10 ≈ 0,5 satırı, 100 tekrar, tek süreç | `inc1_yeniden_olcum.json` | 29 sn |
| `inc1_islem_suresi.py` | İstasyon-gün başına ön işlem ve saatlik ÇİF süresi (yapay) | ekran | < 10 sn |

Kesinlik özeti (bağımsız, yer düzeyi, R = 300, B = 300; (c) olasılıkları %90 aralıkla; "karşılanmadı" L > %0,245):

| Desen, ρ | n (geçerli) | σ aralığı / σ | Kapsama σ / q95 (%95) | Karşılandı σ 0,10 / 0,15 / 0,20 | Karşılanmadı σ 0,30 |
|---|---|---|---|---|---|
| Tam, 0,3 | 84 | 0,72–0,74 | 0,98–1,00 / 0,94–0,97 | 1,00 / 0,43 / 0,01 | 0,01 |
| Tam, 0,6 | 84 | 0,77–0,82 | 0,91–0,94 / 0,83–0,89 | 0,95 / 0,51 / 0,08 | 0,00 |
| T 2017–2021 (D), 0,3 | 61 | 0,81–0,84 | 0,96–0,99 / 0,90–0,92 | 1,00 / 0,42 / 0,02 | 0,00 |
| T 2017–2021 (D), 0,6 | 61 | 0,85–0,89 | 0,87–0,91 / 0,79–0,81 | 0,93 / 0,48 / 0,10 | 0,00 |
| %40 yer kaybı (kapı altı), 0,3 | 47 | 0,93–0,96 | 0,97–0,99 / 0,85–0,89 | 0,98 / 0,30 / 0,01 | 0,00 |

Eski eşikle (L > %0,20) tam desende "karşılanmadı" σ 0,30'da 0,19 (ρ 0,3) ve 0,09 (ρ 0,6) çıktı.

Kesik koşu hacmi (C, 21 yer; `inc1_kapi_hacim.json`): tam 196,7 GB; T 2017–2021 153,6; T 2017–2020 134,7; T 2021–2024
99,7 GB (kapı geçmez); örtüşmeyen T 2018/2021/2024 157,5 GB (39 yer-penceresi). Yer sırasıyla kesme (T'ler tam) kapıyı
ancak 12. yerde, 141,5 GB'ta geçirir ve tam sınırdadır (10 / 10 / 10 / 11 / 11). Bu yüzden kronolojik sıra seçildi.
