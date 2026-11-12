DÜZELTMEYLE KABUL

# TR-7 ön kayıt: bağımsız inceleme 1

İncelenen: `TR-7_tetiklenmis-tremor_ONKAYIT.md` (TASLAK sürüm 1, 12 Kasım 2026). Dayanaklar: `TR-7_SAYIM.md`
(§2, Ek 1), `kayit/turetme/tr7/` içinde `tr7_dondurulan_liste.csv`, `tr7_parkfield_liste.csv`, `tr7_varlik.csv`,
`tr7_tetikleyici.csv`, `tr7_onkayit_sayilar.py/.json`, `tr7_onkayit_yapay.py/.json`, `tr7_onkayit_modulasyon.py`.
Hiçbir dalga formu indirilmedi ya da açılmadı, ağa çıkılmadı, git işlemi yapılmadı, taslak değiştirilmedi. Hesaplar
yalnız yazarın yapay betikleriyle (bağımsız tohumlarla, `python3 -I -B`) ve inceleme için yazılmış yapay betiklerle
yapıldı. Bu betikler depo dışında, karalama dizinindedir. Depoya bu rapor dışında dosya eklenmedi.

## Hüküm

Tasarım dikkatli, sayılar betiklerle tutarlı. Dürüstlük çizgisi de sağlam: ×1/3 satırı zorunlu, İstanbul için olasılık
yok, Kahramanmaraş ve Pfohl dönemi verisi ayrı tutuluyor. Ancak metin bu hâliyle dondurulursa üç yerde koşudan sonra
pişman olunur:

- **E1.** Tohoku penceresinin içinde, hem Marmara'da hem Parkfield'da, iki büyük artçının (M 7,9 ve M 7,7) teleseismik
  cisim dalgaları var. Algılayıcı bunları maskelemiyor. Negatif pencereler ise M ≥ 6,5 olayları dışladığı için bu
  kaynağı hiç görmüyor. Sonuçta K1 tremor yerine artçı P dalgasıyla geçebilir.
- **E2.** K1'in en büyük riski olan Parkfield veri varlığı, dondurmadan önce 0 € ile ve körlüğü bozmadan yoklanabilir.
  Dondurduktan sonra yoklanırsa olumsuz sonuç bütün TR-7'yi geri dönüşsüz biçimde kapatır.
- **E3.** K1 kalırsa "kod", "veri" ve "Parkfield yüzey gürültüsü" başarısızlıkları ayrılmıyor. Ayrıca 56 istasyonlu
  Parkfield kümesi, ~10 istasyonlu Marmara için kalibrasyon sayılamaz.

Bunlara ek olarak sekiz önemli bulgu var. Hepsi metin düzeltmesiyle ve E2'deki kısa varlık yoklamasıyla giderilebilir.
Yeni sayım gerekmiyor.

**Bağımsız olarak doğrulananlar:**
- Liste ve girdi sha256'ları §3 ile birebir aynı (6/6).
- Liste: 71 çift, 17 olay, 475 istasyon-tetikleyici, 884 satır, 16 birim, 14 ana birim.
- §4.3 tablosunun ×1, ×1/3 ve ×3 sütunları json ile aynı.
- Parkfield: 56 istasyon (NC 47, CI 6, BK 2, NP 1), kaba τ 27,12 kPa.
- X_min tablosu ve p_min değerleri yeniden hesaplandı, aynı çıktı.
- Rastlantıyla ≥2 algılama olasılığı 0,0572.
- "R+W ortalaması 6314 sn" istasyon-tetikleyici ortalamasıdır; satır ortalaması 6209 sn (K7).
- Yapay sayılar (§D) bağımsız tohumlarla yeniden üretildi.

---

## A. Engelleyici bulgular

### E1. Tetikleyici pencerelerinde öteki büyük olayların cisim dalgaları maskelenmiyor; negatif kontrol bunu ölçmüyor

- **Bulgu.** `tr7_tetikleyici.csv` iki artçıyı kaydediyor: usp000hvpa (2011-03-11T06:15:40, M 7,9) ve usp000hvpg
  (06:25:50, M 7,7). İkisinin de kaba τ'su 2 kPa'nın altında, bu yüzden birim değiller, ama pencerelerin içine
  düşüyorlar:
  - **Marmara (Δ ≈ 9000 km, ~81°).** P varışları ≈ 06:27:40 ve ≈ 06:37:50, S varışları ≈ 06:37:30 ve ≈ 06:47:40.
    Tohoku'nun S2 penceresi W = 06:16:14–06:49:40.
  - **Parkfield (Δ ≈ 8150 km, ~73°).** P varışları ≈ 06:27:00 ve ≈ 06:37:10. K1 penceresi W = 06:13:38–06:45:02.

  Teleseismik P, 100 km'lik bir ağa saniyeler içinde neredeyse eş zamanlı gelir. Bu yüzden ≥3 istasyonda örtüşen ve
  zarf ilişkisi yüksek bir aşım üretebilir. Bu, §6.3'ün "tutarlı küme" tanımının tam karşılığıdır. Katalog maskesi
  (§6.5.1) yalnız ≤1000 km'yi kapsıyor. Darbe kuralı da P kodasının dakikalarca süren sönümünü güvenle atmaz. Negatif
  pencereler ise "[R başı − 3 sa, W sonu] içinde M ≥ 6,5 yok" şartıyla seçildiğinden bu kaynaktan arınmıştır. Sonuçta
  FAR, tetikleyici pencerelerindeki yanlış algılama oranını sistematik olarak küçük gösterir. K1 "en az bir algılama"
  şartını tremor yerine artçı P'siyle geçebilir.
- **Neden engelleyici.** K1 bütün koşunun kapısıdır. Yanlış nedenle geçerse Marmara'nın "görülmedi" ya da "VAR"
  hükmünün dayanağı çöker. Maske bir kuraldır, dondurmadan sonra eklenemez.
- **Düzeltme metni (§6.5'e yeni madde 1a; §3.3 (b)'ye ve §7.1 tablosuna ek):**

  > 1a. **Teleseismik cisim dalgası maskesi.** Her pencere için (tetikleyici, negatif ve Parkfield) ComCat'ten
  > [R başı − 3 sa, W sonu] aralığındaki bütün M ≥ 6,0 olaylar alınır; tetikleyici olayın kendisi dışarıda kalır
  > (Wharton biriminde öteki olay dahildir). Her olay için segment orta noktasına (Parkfield'da iz ortasına) Δ ile
  > `obspy.taup.TauPyModel("iasp91")` üzerinden, olay derinliğinde t_P (adı P ile başlayan fazların en erkeni: P, Pdiff,
  > PKP…) ve t_S (adı S ile başlayan fazların en erkeni) hesaplanır. [t₀ + t_P − 10 s, t₀ + t_P + 240 s] ve
  > [t₀ + t_S − 10 s, t₀ + t_S + 240 s] bütün istasyonlarda maskelenir (§6.5.1'deki maske gibi: aşım değildir,
  > köprülenmez). Sorgu yanıtı sha256'sıyla manifeste girer. Pencere başına maskeli saniye payı çıktı tablosuna (§9.1)
  > yazılır. Bu madde birim sayımını (§4.2) değiştirmez.
  >
  > D12 (yapay): 3 istasyon, 100 pencere. W içine eş zamanlı (istasyonlar arası ±2 sn) yapay teleseismik P zarfı
  > eklenir: ani başlangıç, C ×5 sıçrama, 60 sn e-katlı sönüm. Olay katalogda olduğunda maske ile atılma 1,00
  > olmalıdır.

  Not (bilgi, taslağa girmez): bu maske Marmara Tohoku penceresinde 06:27:30–06:31:40 ve 06:37:20–06:41:50 aralıklarını
  kapatır, M 7,7'nin S'sinden sonra da 06:47:20'den W sonuna kadarını. Love ve Rayleigh'in ana bölümü (≈06:20–06:27)
  açık kalır. Parkfield'da Hill 2013'ün Love'la gelen patlaması (Love ≈ 06:17:30, Rayleigh ≈ 06:25) de açık kalır.

### E2. Parkfield veri varlığı dondurmadan önce yoklanmalı

- **Bulgu.** §16 bunu "K1'in en büyük riski" sayıyor, ama yoklama yapılmamış. Parkfield listesinin 49/56 istasyonu NC
  ya da NP kısa periyot (EHZ/SHZ), yalnız 7'si geniş bant (BK.PKD, BK.RAMR, CI.PHL, SMM, SMR, CAR, NC.BBGB). Dondurmadan
  sonra K1'de "≥3 istasyon örtüsü yok" çıkarsa hüküm otomatik olarak "ölçü sınanamadı" olur ve geri dönüş yoktur
  (§7.2). Yoklama tremor içeriği göstermez. Ek 1'de olduğu gibi yalnız HTTP kodu ve bayt sayılır, Marmara körlüğüne
  dokunmaz. Maliyeti 112 istek ve birkaç yüz KB.
- **Öneri: dondurmadan önce yapılmalı.** Bu inceleme yoklamayı yapmadı.
- **Düzeltme metni (§3.2'nin sonuna; yoklama yapıldıktan sonra sayılarla doldurulur):**

  > **Parkfield varlık yoklaması (dondurmadan önce, 0 €).** `tr7_parkfield_liste.csv`'deki 56 istasyonun her biri için
  > listedeki Z kanalından iki 10 sn'lik NCEDC dataselect isteği yapıldı (EarthScope yalnız NCEDC 404 dönerse
  > denendi): R ortası (2011-03-11T05:16:24) ve iz ortası W ortası (06:29:20). Yalnız HTTP kodu ve bayt kaydedildi,
  > içerik çözülmedi, diske yazılmadı. Sonuç listeye `var_R` ve `var_W` sütunları olarak eklendi; yeni sha256 yukarıda.
  > İki örnekte de "var" olan istasyon sayısı [..]'dir (ilk 12'de [..]). Bu sayı < 3 ise K1 bu tasarımla yapılamaz; ön
  > kayıt dondurulmaz, kök oturuma döner. 3–11 ise K1 kümesi yalnız bu istasyonlardır ve E3'teki 12 sınırı bunlara
  > uygulanır.

  İsteğe bağlı (aynı istekte, tanı için): HRSN (BP) kuyu istasyonları ayrı bir `tr7_parkfield_kuyu_liste.csv` olarak
  aynı yoklamayla dondurulur. Bu liste yalnız E3'teki tanı satırında kullanılır.

### E3. K1'in geçme ve kalma kuralı nedenleri ayırmıyor ve Marmara'yla karşılaştırılabilir değil

- **Bulgu.**
  1. **Kalma nedenleri ayrılmıyor.** K1 kalırsa üç farklı durum aynı "ölçü sınanamadı" etiketini alıyor: veri yok, kod
     hatası, ya da kod doğru ama Hill 2013'ün tremoru Parkfield yüzey istasyonlarının gürültüsünün altında (Hill bunu
     PKD'de, Peng 2009 Cholame'de büyük ölçüde HRSN kuyularında gördü). Üçüncüsü kendi başına bir bulgudur: kırsal bir
     yüzey ağı bilinen tetiklenmiş tremoru göremiyorsa kentsel Marmara ağının görme şansı daha düşüktür. Bu sonuç
     ayrıca yazılmalıdır. Kök karar ("geçmezse Marmara koşulmaz") değişmez, yalnız etiket ayrılır.
  2. **Kod hatası için yol yok.** K1 Parkfield verisini gördükten sonra kalırsa ve kodun metne aykırı olduğu
     anlaşılırsa ne yapılacağı yazılı değil. "Eşik değiştirilmez" doğru, ama bir uygulama hatasının düzeltilememesi
     TR-7'yi bir yazılım hatasına kurban eder. Marmara verisi o noktada hâlâ körken bu düzeltmenin maliyeti yalnız
     pozitif kontrolün kendi bütünlüğüdür.
  3. **Geçme şartı zamansız.** Algılama W içinde herhangi bir yerde olabiliyor. Cholame'nin ortam tremoru §7.2'de kabul
     ediliyor. Parkfield FAR'ı yüksek çıkarsa K1'in geçmesi neredeyse hiçbir şey söylemez.
  4. **İstasyon sayısı farkı.** Parkfield'da 56 istasyon var, Marmara'da S1–S3 pencerelerinde ise 7–22. Rastlantıyla
     ≥3 istasyonun örtüşmesi ve ≥3 çiftte r ≥ 0,5 bulunması istasyon sayısıyla hızla artar. Yapayda 8 istasyonda A50
     ≈ 0,57, 3 istasyonda ≈ 0,61. 56 istasyonla geçen bir K1, ~10 istasyonlu kod için kalibrasyon değildir. Aynı sorun
     Marmara'nın içinde de var: S3'te İran 2013 penceresinde 59 istasyon (45'i YH), S4'te 75, S7'de 89. Birimler
     arasında yanlış algılama olasılığı bu yüzden farklıdır, oysa binom şartı (§8) tek bir p varsayıyor.
- **Düzeltme metni (§7.2'nin "Geçme şartı" cümlesinin ve ardından gelen iki cümlenin yerine):**

  > **İstasyon sınırı (Marmara ve Parkfield'da aynı).** Her (pencere, segment) için örtüden geçen istasyonlardan, o
  > segmentin izine en yakın en çok 12'si kullanılır. Uzaklık `tr7_onkayit_sayilar.py`'deki `nokta_cizgi` ile
  > hesaplanır, eşitlikte ağ ve istasyon adı alfabetik sıralanır. Sınır §6.3, §6.4, §7.3 ve §7.4'ün hepsine uygulanır.
  > §7.2'deki "yalnız ize en yakın 10 istasyonla algılama" bilgi satırı kaldırılır.
  >
  > **K1 sonucu (sıra bağlayıcı).**
  > (a) Tohoku penceresinde ≥3 istasyon örtüsü yoksa: "ölçü sınanamadı (Parkfield verisi yok)".
  > (b) Tohoku penceresinde, kümesi [2011-03-11T06:16:00, 06:31:48] UTC aralığıyla kesişen en az bir algılama varsa
  > (§6.3 ve §6.5, E1 maskesi dahil; aralık, iz ortasında T0 + Δ/4,6 km/s ile T0 + Δ/3,0 km/s arasıdır): **K1 GEÇTİ**.
  > Ayrıca Parkfield'ın 10 negatif penceresinde f_PK ≥ 4 (FAR_PK > 0,30) ise K1 "geçti, ayırt edici değil" olarak
  > yazılır ve Marmara'da "VAR" hükmü verilemez (en çok "aday").
  > (c) Algılama yoksa ve Parkfield MDA'sı (§7.4 yöntemi, Parkfield negatif pencerelerinde) A90_PK ≤ 100 µm/s ise:
  > "ölçü sınanamadı (Tohoku tremoru Parkfield yüzey ağının gürültüsünde görülmedi; A90_PK = [..] nm/s)".
  > (d) Öteki durumlar: "ölçü sınanamadı (yöntem)".
  > (b) dışındaki her durumda Marmara verisi indirilmez.
  >
  > **Uygulama hatası yolu (bir kez).** K1 (c) ya da (d) ile kalırsa ve kodun bu metne aykırı olduğu, K1 verisine
  > bakılmadan yazılmış bir yapay denetimle gösterilirse, kod bir kez düzeltilir. Düzeltme bağımsız kod incelemesinden
  > geçer ve K1 bir kez yeniden koşulur. Tanım, eşik, pencere, liste ve birim kuralı değişmez. Bu yol yalnız bir kez
  > kullanılır ve "K1 sonrası düzeltme" başlığıyla kayda geçer.
  >
  > **Tanı satırları (K1'i değiştirmez).** Tohoku penceresinde ayıklamadan önceki küme sayısı ve her kümenin atılma
  > nedeni (maske, darbe, sızıntı). İsteğe bağlı olarak aynı kod HRSN (BP) kuyu listesinde (E2) koşulur ve yalnız
  > bilgi olarak yazılır.

---

## B. Önemli bulgular

### Ö1. (Yazarın 1. noktası) Kaba τ ana değer olabilir, ama hüküm cümlesi ölçek uyarısını kendi içinde taşımalı

- **Hüküm.** Bant ve birim seçiminin veri görülmeden sabitlenen kaba τ'ya bağlanması savunulabilir (§6.6 gerekçe (i)).
  Ölçülen τ'ya geçmek, hangi tetikleyicinin sayılacağını veriye bağlardı. Ancak Parkfield–Tohoku karşılaştırması (kaba
  τ 27 kPa, Hill 2013 0,7–10 kPa) büyük olaylarda ×3–×40'lık bir fazlalığa işaret ediyor. S2'nin ilk iki birimi Tohoku
  (23,25) ve Kamçatka'dır (12,35); fazlalık en çok bu tür M ≥ 8,8 birimlerdedir. Bugünkü kalıpta "kaba τ ≥ 2,75 kPa
  üstündeki 8 tetikleyici" ifadesi cümlenin başında yer alıyor, ×1/3 ve ölçülen τ ise ayrı satırlarda kalıyor. Marmara
  özetindeki "bu duyarlılıkla (A90 ve kaba τ değerleriyle) gözlenmedi" cümlesine ise hiçbiri girmiyor. Önsayımda
  ×1/3'te üç segmentin üçü de "veri yok" bandında (S1 4, S2 4, S3 3).
- **Ek açık.** Wharton biriminin kaba τ'su "iki olayınkinin büyüğü" olarak tanımlı. Ana şok penceresi K0-tam'da düşerse
  bu değer 9,39 kPa'da kalır, oysa yalnız artçı (3,68 kPa) taranmış olur.
- **Düzeltme metni.**
  - §4.1, Wharton maddesinin "kaba τ'su …" cümlesinin yerine:

    > Birimin kaba τ'su, K0-tam'dan sağ çıkan pencerelerindeki olayların kaba τ'larının en büyüğüdür.

  - §8 "Görülmedi" kalıbının sonuna:

    > Ölçek uyarısı: kaba τ ×1/3 alınırsa [n₁/₃] birim ≥ 2 kPa ([bant₁/₃]); ölçülen τ ile [n_ölç] birim ≥ 2 kPa
    > ([bant_ölç]); Parkfield–Tohoku'da τ_ölç / kaba τ = [..]. bant₁/₃ ya da bant_ölç "veri yok" ise cümle
    > "S_k (yalnız kaba τ ölçeğinde):" ile başlar.

  - Marmara özeti cümlesine:

    > Özete giren bir segmentte bu ön ek varsa özet cümlesi "bu duyarlılıkla (A90 ve kaba τ değerleriyle; kaba τ
    > ölçeği ×1/3'te ya da ölçülen τ ile veri yok bandında) gözlenmedi" olur.

### Ö2. (Yazarın 4. noktası) Modülasyon ölçüsü kilitlenmeyi değil, periyot eşleşmesini ölçüyor; "VAR" cümlesi buna göre yazılmalı

- **Bulgu.** Dalgaya kilitli olmayan, 20 sn periyotlu yarım sinüs tremorda yanlış p ≤ 0,01 oranı bağımsız tohumlarla
  şöyle çıktı:
  - yazarın 1 Hz oyuncak modelinde: A = 1'de 0,39 (100 pencere), A = 3'te 0,56 (100 pencere);
  - gerçek zarf zincirinde (20 Hz, 3 istasyon, 30 pencere): A = 2'de 0,33.

  Taslağın 0,35'i alt uçta kalıyor ve oran SNR ile artıyor. Nedeni şu: ölçü s ∈ {+1, −1} ve 0–10 sn gecikme üzerinden
  en büyük değeri alıyor. 20 sn periyotta bu, faz farkının hemen tamamını tarar. Dairesel kaydırma boş dağılımı ise
  periyodu uymayan bölümleri getirir. Bu yüzden boş hipotez "kilit yok" değil, "periyot uyuşmuyor" olur. Arama dar
  tutulduğunda (yalnız s = +1, gecikme 0–5 sn) oran yalnız 0,31'e iniyor; kilitli tremorda algılama 1,00'da kalıyor.
  Gecikmeyi daraltmak sorunu çözmüyor.
- **Hüküm.** "VAR" için kendi başına yeterince sıkı değil. VAR'ın öteki şartları (X_min tane bağımsız birimde, ayrıca
  Parkfield modülasyonu geçmeli) birim başına ~0,4'lük bu açığı büyük ölçüde kapatıyor. Ancak cümle ölçülmeyen bir şey
  ("fazına kilitli") söylüyor.
- **Düzeltme metni.**
  - §8 VAR kalıbında "yüzey dalgası fazına kilitli (p ≤ 0,01)" yerine:

    > yüzey dalgasıyla eş periyotlu modülasyonlu (p ≤ 0,01; ölçü faz kilidini 20 sn periyodik, kilitsiz modülasyondan
    > ayıramaz, yapayda yanlış pozitif 0,33–0,56)

  - §7.1 tablosuna:

    > D5b. Modülasyon, 20 sn periyotlu kilitsiz yarım sinüs tremor, A = 1 ve 3, 100 pencere. Şart yok; oran yazılır.
    > Beklenen 0,3–0,6.

  - §12'deki "(yapayda %35)" ifadesi "(yapayda %33–56, SNR ile artar)" olur.

### Ö3. (Yazarın 5. noktası) Binom şartı: tanım çoğunlukla tam, dört boşluk var

- **Bulgunun tam olan kısmı.** Kuyruk yönü açık: üst kuyruk, P(Bin(n, p_üst) ≥ X) ≤ 0,05. Payda N, o segmentin ana
  birimlerinin kullanılabilir negatif pencere sayısıdır. p_üst, f/N için tek yanlı %95 Clopper–Pearson üst sınırıdır.
  Kod ile metin aynı.
- **Boşluklar.**
  1. **X_min bulunamazsa.** Hiçbir X ≤ n şartı sağlamazsa ne olacağı yazılı değil (kod `None` döner).
  2. **Segment çokluğu.** Marmara özeti "en az bir segment VAR" ile kuruluyor, yani üç sınamanın birleşimi. Üstelik S1,
     S2 ve S3 aynı istasyonları paylaşıyor. Birim başına ortak istasyon sayıları:

     | Birim | S2 / S3, ortak | S1–S2, ortak |
     |---|---|---|
     | Tohoku | 10 / 7, ortak 5 | 3 |
     | Nepal | 22 / 12, ortak 8 | 12 |

     Segment bazında α = 0,05 iken özet için gerçek hata oranı 0,05'ten büyüktür.
  3. **Negatif kontrolün küçülmesi.** Çok sayıda negatif pencere düşerse N küçülür (n = 8 için N = 40'ta X_min,
     f = 0 iken 3'e çıkar). N = 0'da tanım çöker.
  4. **Ölçü ve şart uyuşmazlığı.** Şart X_mod'a uygulanıyor, ama p_üst algılama FAR'ından geliyor. Bu tutucu bir
     seçim, yazılmalı. Ayrıca Wharton biriminin iki penceresi var, yanlış algılama şansı yaklaşık iki katı.
- **Ek gözlem.** FAR = 0,05 ve n = 8'de, kaynak yokken bile en az bir algılama olasılığı 1 − 0,95⁸ = 0,34. Hükmün
  "görülmedi" yerine "aday" çıkması büyük olasılıkla bundan olacaktır. Aday kalıbı bu bilgiyi taşımalı.
- **Düzeltme metni (§8 tanımlarının sonuna):**

  > X_min(n, f) tanımında N, o segmentin ana birimlerinden kullanılabilir negatif pencere sayısıdır. Wharton biriminin
  > bir negatif penceresi iki alt pencereden oluşur: N'ye 1 katkı yapar, alt pencerelerden birinde algılama varsa
  > algılama sayılır. X_min, algılama FAR'ından hesaplanır ve X_mod'a uygulanır; bu bilerek tutucu bir seçimdir.
  > n ile 2 arasında şartı sağlayan X yoksa o segmentte "VAR" verilemez. N < 5n ise o segmentin hükmü
  > "ölçü güvenilmez (negatif kontrol yetersiz)" olur.
  >
  > Marmara özetinin "gözlendi" cümlesi için en az bir S1–S3 segmentinde X_mod ≥ X_min^(0,05/3)(n, f) gerekir.
  > Tanım aynıdır, yalnız kuyruk eşiği 0,0167'dir. Önceden hesaplanmış değerler (N = 10n), f = 0…5 sırasıyla:
  > n = 5: 3, 3, 3, K2, K2, K2; n = 6: 3, 3, 3, 4, K2, K2; n = 7: 3, 3, 4, 4, K2, K2; n = 8: 3, 3, 4, 4, 4, K2;
  > n = 9: 3, 3, 4, 4, 4, K2; n = 10: 3, 3, 4, 4, 4, 4. Segment satırı 0,05'lik X_min ile yazılır.
  > X_min tablosuna n = 6 ve n = 7 satırları da eklenir (n = 6: 2, 3, 3, 3, K2, K2; n = 7: 2, 3, 3, 3, K2, K2).

  Aday kalıbı şöyle olur:

  > "S_k: aday, doğrulanmadı. [X_alg] tetikleyicide algılama; negatif kontrole göre n tetikleyicide beklenen yanlış
  > algılama n·f/N = [..], P(Bin(n, p_üst) ≥ X_alg) = [..]; VAR şartlarından sağlanmayan: [liste]."

### Ö4. Negatif pencereler gün saatini eşliyor, ama gün türünü ve yaz saatini eşlemiyor; sabah artışı K2'yi boşa harcatabilir

- **Bulgu.** S2'nin 8 ana biriminden 4'ünde R penceresi yerel sabah artışının içinde, W ise artıştan sonra:

  | Birim | Gün | R (yerel) | W (yerel) |
  |---|---|---|---|
  | Tohoku | Cuma | 06:46–07:46 | 08:16–08:49 |
  | Maule | Cumartesi | 07:34–08:34 | 09:18–10:03 |
  | Nepal | Cumartesi | 08:11–09:11 | 09:28–09:52 |
  | Chignik | Perşembe | 08:15–09:15 | 09:46–10:21 |

  Kamçatka gece (W 02:53–03:26). R'den W'ye yükselen kültürel gürültü bütün kentsel KO istasyonlarında aynı yönde
  artar. W'nin sonuna kadar süren aşımlar ±20 sn genişletmeyle birbirine bağlanır. L serilerindeki ortak eğilim de
  Pearson ilişkisini 0,5'in üstüne taşır. Sonuç tutarlı bir küme olur. Aynı UTC saatindeki negatif pencereler bunu
  ölçer, ama hafta içi ve hafta sonu karışık ölçer. Tohoku'nun ±30 günü 2011-03-28 yaz saati geçişini, Maule'ninki
  2010-03-28'i, Nepal'inki 2015-03-29'u kesiyor. Sonuç ya K2'nin "ölçü güvenilmez" vermesi, ya da hafta sonu ağırlıklı
  bir FAR'ın hafta içi tetikleyicilerin yanlış algılama oranını küçük göstermesidir.
- **Düzeltme metni.**
  - §7.3'e, "şu şartları sağlayan ilk 10 alınır" listesine:

    > (iii) Kaydırılmış T0'ın yerel gün türü (Pazartesi–Cuma ya da Cumartesi–Pazar; Marmara'da Türkiye, Parkfield'da
    > ABD Pasifik saati; resmî tatil dikkate alınmaz) tetikleyicininkiyle aynıdır. (iv) Kaydırılmış pencerenin yerel
    > saat farkı (yaz saati durumu) tetikleyicininkiyle aynıdır. Bu şartlarla 10 aday bulunamazsa aday kümesi
    > d ∈ {−60, …, −31, +31, …, +60} ile aynı sırayla genişletilir; 2026 sınırı korunur.

  - §6.5'e madde 3a:

    > **Taban kayması.** Kümedeki istasyonların ≥ yarısında aşım parçası W'nin son 60 sn'sine kadar sürüyorsa küme
    > atılır. Kural negatif pencerelere de aynen uygulanır.

  - §7.1'deki D7'ye:

    > D7, 3a kuralıyla birlikte koşulur; tremor W sonundan ≥ 60 sn önce biter.

  Ek bilgi satırı: W'yi tamamen kapsayan doğrusal yükselen gürültü (R'den W sonuna ×2) ile 100 pencere; 3a ile atılma
  oranı yazılır.

### Ö5. (Yazarın 7. noktası) Genlik ölçeği: sorun S1–S3'te jeofon değil, BH kanalları ve enjeksiyonun yanıtı atlaması

- **Bulgu.**
  - **Jeofon yok.** S1–S3'te hiç EH ya da SH kanalı yok. Listedeki 9 EHZ satırının hepsi S5, S7 ya da Kahramanmaraş'ta.
  - **BHZ ağırlığı.** Listede 478 satır BHZ. S2'nin 2010–2012 birimleri büyük ölçüde BHZ: Maule 10/10, Tohoku 10/10,
    Wharton 10/11. Örnekleme hızı listede yok. 20 sps'lik bir kanalda 8 Hz Nyquist'in 0,8'idir ve sayısallaştırıcının
    yumuşatma süzgeci 6–8 Hz'i bastırabilir.
  - **Parkfield.** 49/56 istasyon kısa periyot. Doğal frekansları 2–8 Hz bandının altındaysa sorun küçüktür.
  - **Asıl iyimserlik kaynağı.** MDA'da yapay tremor, sayım/S biriminde düz yanıtla ekleniyor. Gerçek bir tremor ise
    kanalın yanıtından geçerek gelir. g(f) = |H(f)|/S < 1 olan frekanslarda enjekte edilen sinyal gerçeğinden büyük
    görünür ve A90 küçük çıkar.
- **Düzeltme metni.**
  - §7.4'e, "Süzgeç ve Hilbert doğrusal olduğundan" cümlesinden önce:

    > Yapay tremor eklenmeden önce, frekans ortamında kanalın StationXML yanıtının normalize edilmiş karmaşık değeri
    > H(f)/InstrumentSensitivity ile çarpılır. Böylece veri ile yapay sinyal aynı ölçekte kalır.

  - §3.3 (c)'ye:

    > Her kanalın örnekleme hızı ve g(f) = |H(f)|/S değerleri f = 2, 4, 6 ve 8 Hz'te. g ∉ [0,5, 2] olan kanal sayısı
    > segment başına bilgi satırına yazılır.

  - §12'deki "Kısa periyotlu kanallar" maddesinin yerine:

    > S1–S3'te kısa periyot kanal yok. BH kanallarında 6–8 Hz yumuşatma süzgecine yakın. Enjeksiyon yanıttan
    > geçirildiği için A90 bu yüzden iyimser değildir; mutlak genlik yine de yalnız duyarlılık bölmesine dayanır.

### Ö6. (Yazarın 6. noktası) Darbe ve sızıntı kuralları: darbe gerçek tremoru nadiren atar, sızıntı kuralının ölçeği yanlış seçilmiş

- **Darbe kuralı.** İnceleme karalamasında gerçek zarf zinciriyle (20 Hz, 3 istasyon, 40 pencere) şu sonuçlar alındı:

  | Yapay sinyal | Darbeyle atılma |
  |---|---|
  | Yarım sinüs tremor, A = 10 (10 sn periyot) ve A = 30 (20 sn periyot) | 0/40 |
  | Kutu biçimli patlamalı tremor (5–15 sn, ani kenar), A = 10 | **8/40 (0,20)** |
  | Kutu biçimli patlamalı tremor, A = 3 | 0/40 |
  | Patlamalı tremor, 3 sn kenar yükselmesi, A = 10 | 0/40 |
  | Patlamalı tremor, 2 sn kenar yükselmesi, A = 30 | 1/40 |
  | Yapay yerel deprem, S–P = 8 sn, P tepenin 1/4'ü | algılandı ve 40/40 atıldı |
  | Yapay yerel deprem, S–P = 3 sn | algılanmadı (≥15 aşım saniyesi şartı) |

  Sonuç: kural yavaş yükselen tremoru atmıyor. Ani kenarlı, yüksek SNR'li patlamaları atabiliyor; gerçek tremorda
  kenarlar genellikle yavaştır, risk düşük ama sıfır değil. Bir istasyonun kümede birden çok aşım parçası olduğunda
  hangisine bakılacağı da tanımsız.
- **Sızıntı kuralı.** Kural z_d ile z_y'yi karşılaştırıyor ve her biri kendi R'sindeki σ ile ölçekleniyor. 0,5–1 Hz'te
  R gürültüsü mikrosismik nedeniyle durağandır, σ_d küçüktür. Kentsel 2–8 Hz'te σ_y büyüktür. Bu yüzden tremorun
  0,5–1 Hz'teki küçük bir izi bile z_d'yi z_y'nin üstüne çıkarabilir. Tohoku gibi büyük yüzey dalgalarında 0,5–1 Hz
  kodası da yükselir. Bu iki etki birlikte K1'de gerçek tremoru atabilir. Fiziksel olarak "sızıntı", alçak bandın
  desibel olarak daha çok yükselmesi demektir.
- **Kuralın kendisi kalırsa.** KD'de kod doğru olduğu hâlde bir kural kalırsa ne yapılacağı yazılı değil. Yalnız "kod
  düzeltilir" deniyor.
- **Düzeltme metni.**
  - §6.5.2'ye:

    > Bir istasyonun kümede birden çok aşım parçası varsa c_p'si en büyük olan değerlendirilir.

  - §6.5.3'ün yerine:

    > Küme aralığında her istasyon için Δ_y = medyan_I(L_y) − m_y ve Δ_d = medyan_I(L_d) − m_d hesaplanır (log10
    > genlik artışı; σ ile bölünmez). Δ_d ≥ Δ_y ise istasyon "sızıntı"dır. İstasyonların ≥ yarısı sızıntı ise küme
    > atılır.

  - §7.1 tablosuna:

    > D6b. Yapay yerel deprem; P genliği tepenin 1/4'ü, S–P = 3, 5 ve 8 sn; katalogsuz; 100 pencere. Algılanmama ya da
    > darbeyle atılma ≥ 0,95.
    >
    > D7b. Patlamalı tremor (5–15 sn patlamalar, aralıklar üstel ortalama 15 sn, 2 sn kenar yükselmesi), A = 3, 10 ve
    > 30. Darbe ya da sızıntıyla atılma ≤ 0,05.
    >
    > D7c. Spektrumu 0,5–8 Hz'te düz tremor, A = 3 ve 10. Sızıntıyla atılma ≤ 0,05.
    >
    > D7d. Yapay bölgesel deprem kodası (0,5–8 Hz, genlik ∝ f⁻¹). Sızıntıyla atılma ≥ 0,95.

  - §7.1'in "biri kalırsa" cümlesine:

    > Kod metne uygun olduğu hâlde bir denetim kuralın kendisi yüzünden kalırsa (bağımsız referans betik de aynı sonucu
    > verirse), kural gerçek veri görülmeden, yalnız yapay sonuçlara dayanarak ve bağımsız bir incelemeden geçerek
    > "koşu öncesi ek" başlığıyla değiştirilebilir.

### Ö7. A'nın tanımı belirsiz ve tremor genliği kestiricisi (§7.5) yanlı; D10 doğru kodu sınırdan geçiriyor

- **Bulgu.** Yapay betikte A, etkin (zarf > 0) örneklerdeki RMS'tir. §7.4 ise "bileşen başına 2–8 Hz RMS" diyor ve
  hangi örneklerin sayıldığını söylemiyor. 300 sn'lik yarım sinüs zarfında iki tanım arasındaki oran 0,7065
  (karalamada hesaplandı). §7.5 kestiricisi ⟨C²⟩'yi I = [aşım başı − 60, aşım sonu + 60] üzerinde ortalıyor. Bu, gücü
  tremorun olmadığı 120 sn'ye de yayar. Gerçek zarf zincirinde ölçülen kestirilen/gerçek oranları:

  | Kestirici | Sabit tremor A = 3 | Sabit tremor A = 10 | Yarım sinüs |
  |---|---|---|---|
  | Bugünkü tanım (I) | 0,866 (q05–q95: 0,862–0,869) | 0,861 | 0,615 |
  | Önerilen I′ (±60 sn yok) | 1,026 (A = 3), 1,036 (A = 1) | — | 0,732–0,741 (A_etkin ölçeğinde); A_300 ölçeğinde 1,04 |

  D10'un bandı [0,85, 1,15]; doğru kod bu banda yalnız 0,01–0,02 payla giriyor. A90/A_PK oranı ise yarım sinüs
  benzeri bir tremorda ~1,6 kat şişer.
- **Düzeltme metni.**
  - §7.4'te "A, kaynağın tam üstünde … (nm/s)" cümlesinin yerine:

    > A, kaynağın tam üstünde (25 km) tremorun 300 sn'lik süresi boyunca (sıfır yarım dönemler dahil) bileşen başına
    > 2–8 Hz RMS'tir (nm/s; A_300). §7.1'deki yapay A (A_etkin, etkin örneklerde) ile bağıntı: A_300 = 0,7065 · A_etkin.
    > D2 ve D3 bantları A_etkin ölçeğindedir.

  - §7.5'te "I" yerine:

    > I′ = [kümedeki en erken aşım başı, en geç aşım sonu]

  - D10'un yerine:

    > D10. Kestirici, A_etkin = 3 için 100 pencerede. Sabit tremorda kestirilen/A_300 ∈ [0,90, 1,15]; yarım sinüs
    > tremorda kestirilen/A_300 ∈ [0,90, 1,15]. Beklenen değerler 1,03 ve 1,04.

### Ö8. Tek koşu mekanizması kendi içinde çelişiyor ve kalıcı değil

- **Bulgu.**
  - **Yeniden başlatma çelişkisi.** §10.6'ya göre biçim ya da servis hatası koşuyu "hiçbir algılama hesaplanmadan"
    durdurur. Ama bekçi dosyası koşunun başında oluşturuluyor ve "dosya varsa yeniden koşmaz" deniyor. Bu yüzden
    algılama öncesinde duran bir koşu bir daha başlatılamaz.
  - **Bekçi kalıcı değil.** Bekçi depo dışında duruyor. Bulut oturumu sıfırlanırsa kaybolur ve tek koşu güvencesi
    ortadan kalkar.
  - **İkinci turdan sonrası tanımsız.** "Tek bir yeniden deneme turu"ndan sonra servis hatası payı hâlâ %10'un
    üstündeyse ne olacağı yazılı değil.
  - **Paydalar tanımsız.** "%10" ve ">%1" oranlarının paydası belirtilmemiş.
- **Düzeltme metni (§10.6'nın bekçi ve hata cümlelerinin yerine):**

  > Koşu kodu, her aşamanın başında depodaki `kayit/turetme/tr7/TR7_KOSU_DURUM.json` dosyasına aşama adını yazar ve
  > commit eder. Aşamalar: manifest, K1-indirme, K1-algılama, Marmara-indirme, Marmara-algılama, hüküm. Aynı bilgi depo
  > dışında bir bekçi dosyasına da yazılır. K1-algılama ya da Marmara-algılama aşamasına bir kez girilmişse, koşu
  > E3'teki uygulama hatası yolu dışında yeniden başlatılmaz. Bu aşamalardan önce duran bir koşu, durma nedeni kayda
  > geçtikten sonra kaldığı aşamadan sürdürülür. Bunun için kod değişikliği gerekiyorsa yalnız indirme ve ayrıştırma
  > katmanında yapılabilir ve "koşu öncesi düzeltme" başlığıyla yazılır.
  >
  > Servis hatası payının paydası, manifest (d)'deki planlı istek sayısıdır. Yeniden deneme turundan sonra pay hâlâ
  > %10'dan büyükse eksik istasyon-pencereler örtü kuralıyla (§4.2) düşer ve koşu sürer. Biçim hatası payının paydası, HTTP
  > 200 dönen istasyon-pencere sayısıdır.

---

## C. Küçük bulgular

### K1. D2'de A50 ve A90'ın tanımı ve MDA basamak aralığı

- **D2 tanımı.** Bildirilen A50 ≈ 0,61 ve A90 ≈ 0,65, ara değerlemeyle bulunmuş değerlerdir. §7.4'ün "en küçük basamak"
  kuralı ise 0,631 ve 0,668 verir. İkisi de bandın içinde, ama koşu kodunun hangisini kullanacağı yazılmalı.
- **MDA basamağı.** MDA'nın 10^(1/8) adımı (×1,33), P'nin 0,02'den 0,98'e çıktığı ×1,19'luk geçişten kaba. A50 ile A90
  çoğunlukla aynı basamağa düşer ve A90'ı en çok ×1,33 abartır.
- **Düzeltme metni.**
  - D2'ye:

    > A50 ve A90, P'nin log10 A'ya göre doğrusal ara değerlemesiyle bulunur.

  - §7.4'te:

    > A basamakları 10^(j/20) nm/s, j = 0…100. A50 ve A90, P ≥ 0,5 ve P ≥ 0,9 olan ve üstündeki bütün basamaklarda da
    > bu şartı sağlayan en küçük basamaktır. P(A), ana birimlerin algılama vermemiş negatif pencerelerinden en az 20
    > tanesiyle hesaplanır; daha azsa A90 "belirsiz" yazılır.

### K2. §6.6'da kullanılan bileşenler saklanmıyor

- **Bulgu.** §6.6 max(|v_Z|, |v_N|, |v_E|) kullanıyor, ama §6.2.5 v_Z, v_R ve v_T'yi saklıyor.
- **Düzeltme:** "max(|v_Z|, |v_R|, |v_T|)".

### K3. Katalog maskesinin ayrıntıları

- **Düzeltme metni (§6.5.1'e):**

  > İki katalogdan herhangi birinde şartı sağlayan her kayıt maskelenir; kayıtlar eşleştirilmez (birleşim). Sorgu
  > aralığı [R başı − 1 sa, W sonu]. R'deki maskeli ve kayıtsız saniyeler m ve σ hesabından, I'daki maskeli saniyeler
  > Pearson ilişkisinden ve L_k'dan çıkarılır.

### K4. S5 ve S6'nın bandı §4.3 ile §8 arasında çelişiyor

- **Bulgu.** §4.3 tablosu S5'i (6) ve S6'yı (5) "zayıf" bantta gösteriyor. §8'e göre ise bağımsız satır yalnız 2009
  sonrası birimlerle kuruluyor: S5'te 2 birim (Kamçatka, Chignik), S6'da 1 (Kamçatka). Bu her durumda "veri yok"
  demektir. Pfohl dönemi etiketlemesi (Kashmir 2005, Kuril 2006 ve 2007, Bengkulu 2007; YL) doğru.
- **Düzeltme (§4.3 tablosunun altına):** "S5/S6'nın bağımsız satırı: S5 n = 2, S6 n = 1, 'veri yok'. Tablodaki S5/S6
  bantları yöntem karşılaştırma satırınındır."

### K5. Referans betikteki küme kurgusu §6.3'ten farklı

- **Bulgu.** `tr7_onkayit_yapay.py` kümeyi bağlantılı bileşen olarak değil, bir aralığın komşuları olarak kuruyor.
  Küme aralığına ise o istasyonların zaman olarak uzak parçalarını da katıyor. Gauss gürültüsünde etkisi ihmal
  edilebilir, ama kod incelemesinde D1–D3 karşılaştırılırken bilinmeli.
- **Düzeltme (§7.1 notuna):** "Referans betik kümeyi komşuluk olarak kurar; koşu kodu §6.3'teki bağlantılı bileşeni
  kullanır. D2 ve D3 bantları bu fark için yeterince geniştir."

### K6. Yeniden üretilebilirlik (yazarın 8. noktası)

- **Bulgu.** 1 Hz zarf deposu ve depodaki sha256 manifesti algılama, ayıklama ve modülasyon adımlarını yeniden
  üretmeye yeter. MDA'yı ise yeniden üretmez: MDA 100 Hz analitik sinyal ister ve ham veri silinir.
- **Düzeltme metni (§6.1'e):**

  > Her (segment, negatif pencere, A basamağı) için algılama E/H ve enjeksiyon başlangıcı depoda `tr7_mda.csv`'ye
  > yazılır. MDA'nın yeniden üretimi yeniden indirme gerektirir; yeniden indirilen miniSEED'in sha256'sı manifesttekinden
  > farklıysa sonuç "veri değişti" notuyla yazılır.

### K7. Sayı tanımları

- §5'te "Listede R+W ortalaması 6314 sn" yerine "istasyon-tetikleyici başına R+W ortalaması 6314 sn (satır
  ortalaması 6209)".
- §7.5'te A_PK = 0 ya da tanımsız olabilir. Bu durumda A90/A_PK "tanımsız" yazılır.
- "Parkfield modülasyonu geçti" şöyle tanımlanır: "K1 aralığıyla kesişen Tohoku kümelerinden en az birinde p ≤ 0,01".

---

## D. Yazarın sekiz noktasına kısa hükümler

| # | Konu | Hüküm |
|---|---|---|
| 1 | S2/S3 sınırda; kaba τ ana, ölçülen τ ikinci değer | Seçim savunulabilir, bant ve birim seçimini veriden korur. Kalıplar uyarıyı taşımıyor → Ö1. |
| 2 | K1 veri varlığı; K1 kalırsa | Dondurmadan önce yoklanmalı → E2. Kural kalma nedenlerini ayırmıyor → E3 (kök karar korunuyor). |
| 3 | §15 sapmaları | Hepsi dalga formu görülmeden yazılmış. Aşım ve modülasyon yapay sınamaya dayanıyor ve yeniden üretildi (eski kural A = 1'de 0/100, yeni kural A50 ≈ 0,61). Maske ve darbe kuralı yalnız akıl yürütmeye dayanıyor; D6 ve D7'nin önceden hesaplanmış değeri yok → Ö6. Sızıntının gerekçesi yok → Ö6. R penceresi ve negatif kontrol simetrisi tutarlı. Hiçbiri Marmara verisine dayanmıyor. |
| 4 | Modülasyonda %35 | Kendi başına yeterince sıkı değil (0,33–0,56). Öteki VAR şartları açığı büyük ölçüde kapatıyor; cümle düzeltilmeli → Ö2. |
| 5 | Binom şartı | Kuyruk, payda ve p_üst tanımlı; dört boşluk var → Ö3. |
| 6 | Sabit eşikler; darbe kuralı | Darbe kuralı yumuşak tremoru atmıyor, ani kenarlı patlamaları %20 atabiliyor. Sızıntı kuralının ölçeği yanlış → Ö6. 10⁶ sayım eşiği 24 bit kanallarda zararsız; 16 bit kanal varsa kırpılma hiç yakalanmaz (manifest (c)'ye sayısallaştırıcı bit sayısı eklenirse kapanır). |
| 7 | Genlik ölçeği | S1–S3'te jeofon yok. İyimserliğin asıl kaynağı enjeksiyonun yanıtı atlaması → Ö5. |
| 8 | Zarf deposu | Algılama için yeterli, MDA için değil → K6. |

**Kendi başıma aradıklarım:**
- **Tanımsız paydalar:** Ö3, Ö8, K1.
- **Veri görüldükten sonra karar bırakan yerler:** K1 kalırsa ne olacağı (E3); KD'de bir kural kalırsa ne olacağı
  (Ö6); ikinci yeniden deneme turundan sonrası (Ö8).
- **"Görülmedi"nin gücünü veren sayılar:** A tanımı (Ö7), Wharton τ'su (Ö1), N alt sınırı (Ö3).
- **Gün saati:** Ö4.
- **İstasyon bağımsızlığı ve çoklu karşılaştırma:** E3 ve Ö3.
- **Pfohl etiketi:** K4.
- **Tek koşu:** Ö8.
- **Kör veri sınırı:** sorunsuz. En geç W sonu 2025-07-30T00:27:26; negatif pencereler ve E1 sorguları 2026-01-01
  sınırına bağlı kalır. E2'deki yoklama yalnız Parkfield 2011 içindir.

Mutlak İstanbul olasılığı ya da olasılık çarpanı metnin hiçbir yerinde geçmiyor.

---

## E. Yapay hesapların özeti (yeniden üretim)

Yazarın betikleri bağımsız tohumlarla koşuldu (`python3 -I -B`, karalama dizininden). İnceleme betikleri karalama
dizininde: `d10.py`/`d10b.py` (kestirici), `modv.py` (daraltılmış modülasyon araması), `modreal.py` (modülasyon gerçek
zarf zincirinde), `darbe.py` (darbe kuralı).

| Hesap (tohum) | Sonuç |
|---|---|
| D2: 3 istasyon, 200 pencere (31337 / 4711) | P(0,596) = 0,295 / 0,345; P(0,631) = 0,805 / 0,85; P(0,668) = 0,985 / 1,00 → A50 ≈ 0,61, A90 ≈ 0,645 (ara değerleme); basamak kuralıyla 0,631 / 0,668. Bant içinde. |
| D2: 3 istasyon, 400 pencere (5555) | P(0,596) = 0,29; P(0,631) = 0,80; P(0,668) = 0,99; A = 0'da 0/400 |
| D3: 8 istasyon, 100 pencere (2718) | P(0,562) = 0,43; P(0,596) = 0,99 → A50 ≈ 0,565 |
| 3σ / 5σ (1618 / 1619) | A50 ≈ 0,52 / ≈ 0,70; D2 bandı ikisini de ayırıyor |
| Sabit tremor (1620) | P(0,631) = 0,76 |
| Eski "≥30 sn kesintisiz" kuralı (1621) | Bütün A'larda 0/100 |
| Modülasyon, kilitsiz 20 sn (101 / 102), oyuncak model | A = 1: 0,39; A = 3: 0,56 |
| Modülasyon, gerçek zarf zinciri (1–4) | Kilitli A = 0,7 / 1 / 2: 1,00 (algılama 1,00); kilitsiz A = 2: 0,33 |
| Modülasyon, s = +1 ve gecikme 0–5 (202) | Kilitsiz A = 1: 0,31; kilitli A = 0,5: 1,00 |
| §7.5 kestirici (1–3, 11–14) | Ö7'deki tablo |
| Darbe kuralı (1–8) | Ö6'daki tablo |
| X_min, α = 0,05 / 0,0167 | Ö3; 0,05 satırları json ile aynı |
| Rastlantıyla ≥1 algılama, FAR 0,05 | n = 8: 0,337; n = 9: 0,370 |
