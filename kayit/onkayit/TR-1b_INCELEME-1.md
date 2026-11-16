# TR-1b ön kayıt: bağımsız inceleme 1

İncelenen: `TR-1b_sinirli-kosu_ONKAYIT.md` (TASLAK, 16 Kasım 2026) ve `kayit/turetme/tr1b/` (`tr1b_mde.py`, `.json`).
Dayanaklar: `ESIK-DAYANAGI.md`, TR-1 sürüm 2 ve iki incelemesi, `kayit/turetme/tr11/tr11_sonuc.json/.md`.
Taslak ve yazarın betikleri değiştirilmedi. Hiçbir tenv3 serisi, hiçbir olay penceresi indirilmedi ya da açılmadı;
hiçbir gerçek olay-öncesi S hesaplanmadı. Tek gerçek girdi TR-11'in commit edilmiş 665 depremsiz küme-pencere tablosudur
(`kume_pencere_tablosu`; yer, epok, n_y, S, sınıf).

Bağımsız betikler (`python3 -I -B`, numpy):
- `kayit/turetme/tr1b/inc1/tr1b_inc1.py` → `tr1b_inc1.json` (tohum 1116, ≈ 50 sn). Yazardan bilerek farklı: sıfır
  dağılımı modelden değil **TR-11'in gerçek 665 S'inden** (koşudaki gibi, katman içi orta-sıra ECDF); sinyal modeli
  **katman başına** ayrı uydurulan log-normal σ; yanlış alarm c_gerçek ≠ c0, karışım kirlenmesi ve epok yanlılığı
  altında; TR-11 içi alt kümelerin eşdeğer şişme katsayısı; "bir kümeyi dışarıda bırak" şartı dahil.
- `kayit/turetme/tr1b/inc1/tr1b_inc1_eslesik.py` → `tr1b_inc1_eslesik.json` (tohum 1117, ≈ 7 sn): önerilen
  yerinde kaydırılmış plasebo ile eşli işaret çevirme sınamasının MDE'si.

## Hüküm

**DÜZELTMEYLE KABUL — koşullu.** Tek koşuluk, kör, ucuz (0 €) ve sayıları doğru bir tasarım. Ama taslağın asıl
dayanağı olan c0 = 1,64 payı **savunulamaz**: (i) ölçtüğü şey bölge yanlılığı değil, TR-11'in 2008 epoğundaki
**dönem/işleme** şişmesidir; (ii) q95 oranından alınmış, sınama ise ortalama yüzdelikle yapılıyor; (iii) gerçek bölge
şişmesi 1,64'ü biraz aşarsa "Büyük etki VAR"ın yanlış alarmı hızla %14–77'ye çıkar (aşağıda B). Bunun çaresi veri
görülmeden sabitlenebilir: **olay yerinin kendi, 730 g geriye kaydırılmış penceresiyle eşli sınama.** Yapayda bu
tasarım c0'a hiç dayanmadan, K_p = 6 eşli kümeyle bile c0 = 1,64 tasarımının K = 12'deki MDE'sine eşit, K_p ≥ 8 ile
daha iyi MDE veriyor (C).

Koşul: aşama 0 (yalnız üstveri) eşli plasebosu kurulabilen küme sayısını K_p ≥ 6 bulursa düzeltilmiş tasarım
dondurulup koşulur. K_p < 6 ise **koşulmasın** (o dalda RET): c0'a dayanan bir "VAR" yorumlanamaz, "ayırt edilemez"
ise kuramın öngördüğü etkinin 3–150 katı bir MDE ile önceden bilinir; koşu bilgi üretmez.

## A. Körlük, tek koşu ve kalan serbestlik

Kör ve tek koşuluk olan: H0', istatistik (ū), sıfır çekilişi, α, LOO şartı, hüküm sırası, pencere ve dışlama
kuralları, referans halkası (200–500 km) önceden sabit. MDE'ler yalnız yapaydan. Gerçek S görülmemiş. İyi.

Kalan serbestlikler (zorunlu düzeltme Z-numaralı, öneri Ö-numaralı):
1. **Olay listesi dondurulmuyor (Z1).** Aşama 0 yalnız "K ve bileşim yazılır" diyor. Olay kimlikleri (ComCat id),
   kümeler, n_y katmanı (üst sınır) ve dosya sha256'sı aşama 0 çıktısında dondurulmalı; koşu bu listeye assert etmeli.
   Yoksa ComCat'in koşu günündeki hâli (büyüklük revizyonu, yeni çözüm) örneklemi sessizce değiştirir.
2. **Aşama 0'dan sonraki tasarım seçimi (Z2).** Aşağıdaki düzeltmeler (eşli plasebo, dönem kuralı) aşama 0 sayısına
   bağlı dallar getiriyor. Dal kuralı **aşama 0 koşmadan önce** ön kayda yazılmalı (aşağıda Z3–Z5'te verildi);
   aşama 0 sonucu yalnız kuralı uygular, kural seçmez.
3. **c0 = 1 cümlesi (Z6).** Dal 4'e eklenen "Saf depremsiz tabandan büyük, ama aktif bölge payı içinde" cümlesi
   fiilen ikinci bir hükümdür ve hiçbir yanlış alarm denetimi yoktur: gerçek bölge şişmesi yalnız 1,3 olsa, c0 = 1'deki
   eşiği (K = 12'de ū > 0,637) beklenen ū 0,633 ile yaklaşık yarı yarıya aşar. Bu cümle çıkarılmalı ya da "bölge farkı
   ile öncül bu sınamada ayrılamaz" diye yazılmalı.
4. **Hesap sırası (Ö1).** Kod, gerçek K'yi (doluluk sonrası), TR-11 yeniden hesabını ve kod denetimlerini olay S'i
   hesaplanmadan **önce** günlüğe yazmalı; "veri yok" ve "geçersiz" dalları S'e bakmadan kapanmalı. Taslakta sıra
   "kodda sabit" deniyor ama S'in ne zaman hesaplandığı yazılmıyor.
5. **Bilgi satırları çok (Ö2).** c0 = 1 / 1,3, TR-1 plasebo, sınıf B, epok ECDF'i, LOO aralığı, uzaklık medyanları,
   bileşim: hükmü değiştirmiyorlar, ama raporda "c0 = 1,3'te anlamlı" gibi seçmeli okunmaya açıklar. Hepsinin tek
   tabloda, sabit sırayla ve "hüküm vermez" başlığıyla basılacağı yazılmalı.
6. Sorunsuz bulduklarım: küme puanı (ortalama u), 10° blok kuralı, Ö4 istasyon kuralı, binom ikincil sınamanın
   eşiği (K = 12, p0 0,187: c = 6, gerçek α 0,0140; yeniden hesaplandı).

## B. MDE ve yanlış alarm: yeniden hesap

**MDE (A sınaması, güç 0,8, tek yanlı α 0,05; sıfır gerçek TR-11 S'i, sinyal katman modeli):**

| K | c0 | uyumlu: yazar / bu inceleme | dağınık: yazar / bu inceleme |
|---|---|---|---|
| 12 | 1,64 | 1,37 / **1,44** mm/yıl | 3,09 / **3,25** mm/yıl |
| 12 | 1,3 | 1,09 / 1,09 | 2,27 / 2,28 |
| 12 | 1,0 | 0,79 / 0,76 | 1,58 / 1,46 |
| 6 | 1,64 | 1,64 / 1,71 | 3,96 / 4,12 |
| 20 | 1,64 | 1,26 / 1,31 | 2,70 / 2,83 |

- Fark ≤ %6; yazarın ana satırları yeniden üretildi. Katman modelim TR-11 katman q95'lerini tutuyor (model 2,65 / 2,13 /
  1,83; gerçek 2,76 / 2,24 / 1,94); g = 3'te medyan artış 2,32 (TR-11 MC beklentisi 2,17; yazarın modeli 2,35). Yani
  "≈ %10 iyimser" uyarısı benim modelimde de geçerli.
- c0 = 1,64'ün tek başına AUC'si gerçek TR-11 S'iyle **0,737** (yazar modelden 0,70). Mesaj aynı: pay, aranan etkiden
  büyük.
- Bölge şişmesi gerçekten 1,64 ise (σ × 1,64) ve sinyal onun üstüne biniyorsa K = 12'de gereken g: uyumlu 1,2,
  dağınık 2,5 (taslaktaki MDE'ler "şişme yok" varsayımıyla hesaplanmış; büyüklük değişmiyor, yorumu değişiyor).

**"Büyük etki VAR"ın yanlış alarmı (sinyal yok; olay S'i = c_gerçek × TR-11 S'i; ana p ≤ 0,05 ve LOO p ≤ 0,10):**

| c_gerçek | 1,0 | 1,3 | 1,64 | 1,8 | 2,0 | 2,2 | 2,5 |
|---|---|---|---|---|---|---|---|
| K = 6 | 0,000 | 0,004 | 0,039 | 0,090 | 0,179 | 0,309 | 0,508 |
| K = 12 | 0,000 | 0,002 | 0,049 | **0,143** | **0,316** | 0,528 | 0,772 |
| K = 20 | 0,000 | 0,000 | 0,048 | 0,169 | 0,456 | 0,712 | 0,917 |

- ≤ %5 yalnız şu varsayımla doğru: **olay bölgelerinin gürültüsü, TR-11 tabanının tekdüze en çok 1,64 katı.** Bu
  aşılınca yanlış alarm dik çıkar ve K büyüdükçe **kötüleşir** (yanlılık K ile birikir). LOO şartı bunu hiç tutmaz
  (tekdüze şişmede her alt örnek de anlamlıdır).
- Karışım kirlenmesine (kümelerin π'si 3 kat şişmiş, kalanı temiz) sınama dayanıklı: K = 12'de π = 0,4 bile 0,020.
  Ortalama yüzdelik sınırlı olduğu için birkaç kirli küme hükmü taşımıyor. Tehlike tekdüze şişmede.
- **Dönem yanlılığı:** olayların gürültüsü TR-11'in 2008 epoğu gibiyse (2003–2008 penceresi) ve bölge şişmesi
  yalnız 1,3 ise yanlış alarm K = 12'de **0,192**, K = 20'de 0,232.

**c0 = 1,64'ün kaynağı ne ölçüyor (TR-11 içi alt kümeler, ū ve eşdeğer çarpan; katman içi tüm-taban ECDF'i):**

| Alt küme | KP | ū (se) | eşdeğer c |
|---|---|---|---|
| epok 2003 | 5 | 0,577 (0,115) | 1,16 |
| **epok 2008** | 35 | 0,685 (0,050) | **1,45** |
| epok 2013 / 2018 / 2023 | 142 / 226 / 257 | 0,498 / 0,474 / 0,497 | 1,00 / 0,95 / 1,00 |
| sınıf B (aktif kuşak) | 10 | 0,560 (0,101) | 1,12 |
| Batı ABD (−125…−110° D, 30…50° K) | 36 | 0,322 (0,040) | **0,70** |

Okuma: TR-11'de şişen tek alt küme bir **dönem**dir (2003–2008 GNSS'i), bölge türü değil. Tektonik olarak en etkin alt
kümeler (sınıf B, Batı ABD) şişme göstermiyor; ama bunlar TR-11'in "sakin pencere" seçiminden geçmiş yerlerdir, aktif
sınırdaki olay merkezlerini temsil etmezler. Sonuç: **c0 = 1,64 bölge yanlılığının ölçüsü değil, hiçbir şeyin ölçüsü
olmayan bir sayıdır**; üstelik q95 oranıdır, ū biriminde aynı alt küme 1,45 verir. Olay merkezleri (dalma-batma
kuşakları, yavaş kayma bölgeleri, volkanik yaylar) için ≥ 2 kat şişme fiziksel olarak olağandır: yavaş kayma
olayları ve önceki depremlerin eşik altı postsismik kalıntısı 2 yıllık hız değişiminde mm/yıl düzeyinde iz bırakır.
Taslağın kendi §6.1'i de yanlılığın "VAR" yönünde olduğunu söylüyor. Pay bunu karşılamaz.

## C. TR-1b'ye özel soru: c0 veri görülmeden nasıl daha iyi sabitlenir

1. **TR-11 tabanı plasebo yerine:** ölçü, sürüm, n_y ve pencere farkını eşitler (doğru), bölge farkını eşitlemez.
   Pay ile "taşınması" yalnız payın kendisi ölçülmüşse işe yarar. Ölçülmemiş.
2. **Önerilen çözüm (Z3): yerinde kaydırılmış plasebo, eşli sınama.**
   - Plasebo penceresi: aynı yer, aynı istasyon seçimi kuralı, pencere **730 g geriye kaydırılmış**: w1_p = H =
     T − 7 − 730 g, w0_p = w1_p − 1826 g, menteşe H_p = w1_p − 730 g. Olay penceresinin H'den sonraki 2 yılına
     (öncülün arandığı kısım) hiç girmez.
   - Gerekli veri T − 7,0 yıla iner (TR-1'in T − 5 yıl epoğu ≈ T − 10 yıl istiyordu ve 3 olay vermişti). Ş1–Ş3 ve
     kod 2 kuralı plasebo penceresine aynen uygulanır.
   - İstatistik: küme başına d_k = log(S_olay / S_plasebo) (çok olaylı kümede ortalama), ortalama d, **kesin tek yanlı
     işaret çevirme** (2^K_p desen). Bölge şişmesi, ağ ve dönem her iki pencerede ortaktır; c0 gerekmez.
   - Yapay MDE (`tr1b_inc1_eslesik.json`; σ_c aynı yerde ortak; sinyalsiz yanlış alarm 0,045–0,053):

     | K_p | 6 | 8 | 10 | 12 |
     |---|---|---|---|---|
     | uyumlu g (mm/yıl) | 1,35 | 1,10 | 0,95 | 0,87 |
     | dağınık g | 2,82 | 2,15 | 1,84 | 1,68 |

     K_p = 6 ile c0 tasarımının K = 12 MDE'sine (1,44 / 3,25) eşit; K_p = 12 ile yaklaşık yarısı, ve bu MDE bir
     varsayıma değil bölgenin kendisine göredir.
   - Seçenek olarak sınanan ve elenen: plasebodan c0'ı tahmin edip c0* = max(1,64, ĉ'nin %95 üst sınırı) almak.
     Yanlış alarm ≤ 0,006 kalıyor, ama c_gerçek 1,64 iken c0*'ın medyanı 2,4–2,7, c_gerçek 2 iken 3,0–3,5 oluyor
     (`tr1b_inc1.json`, `kaydirilmis_plasebo_kurali`): güç yok olur. Eşli sınama daha iyi.
   - Yanlılık yönleri: (a) olaydan bağımsız ama T'ye doğru artan gürültü (yeni bir yavaş kayma döngüsü, volkanik
     kabarma, ağ bozulması) "VAR" yönündedir: tek kalan karıştırıcı budur ve bilgi satırında, olay bölgesi için bilinen
     yavaş kayma/volkan listesiyle (önceden sabit) ayrılmalıdır. (b) Eski pencerenin daha gürültülü olması (dönem),
     sönen postsismik, 2 yıldan uzun öncül plasebo penceresine taşar: hepsi H0 yönünde, yani tutucu.
   - Kalan açık (Z4): iki pencere [w0, H] ile [H_p, H] parçasını paylaşır. Bu, işaret çevirmenin değiş tokuş
     edilebilirliğini yaklaşık kılar. Koşudan önce TR-11'in yapay istasyon modeliyle (renkli gürültü dahil) eşli
     sınamanın sinyalsiz yanlış alarmı ölçülmeli; > 0,07 ise "geçersiz (kod)".
3. **T − 7…T − 5 yıl gibi erken pencereler:** ilke olarak daha temiz (paylaşılan parça yok), ama T − 10 yıla inen
   veri ister; TR-1 sayımında benzeri 3 olay verdi. Bilgi satırı olarak kalsın, ana tasarım olmasın.
4. **c0 dalının tutulması gerekiyorsa (Z5):** c0'ın birimi ū olmalı (q95 oranı değil) ve dönem yanlılığı ondan önce
   kaldırılmalı: olaylar w0 ≥ 2008-01-01 ile sınırlanır (TR-11'de 2013+ epokları şişmesiz: 1,00 / 0,95 / 1,00), ya da
   bu sınır aşama 0'da K'yi 6'nın altına düşürüyorsa c0 dalı koşulmaz. Payın değeri yine bir tahmin kalır; hüküm
   cümlesi "c_gerçek ≤ c0 varsayımı altında" diye başlamalı.
5. **Aşama 0 tanımı yeterli mi:** yalnız K için evet; düzeltilmiş tasarım için hayır. Aşama 0 (yalnız
   `DataHoldings.txt`, `steps.txt`, ComCat) ayrıca şunları yazmalı: dondurulmuş olay/küme listesi ve sha256 (Z1);
   eşli plasebosu kurulabilen küme sayısı K_p (aynı istasyonlar, T − 7,0 yıla inen kapsam, plasebo için Ş1–Ş3 ve kod 2);
   w0 ≥ 2008 alt kümesinde K; katman ve bölge bileşimi (dalma-batma / doğrultu atımlı / volkanik). Dal kuralı (Z2):
   K_p ≥ 6 → eşli sınama ana, c0 sınaması bilgi; K_p < 6 → koşu yok, kayıt "güç yok (eşli plasebo < 6)".

## D. Bilimsel değer

- MDE (uyumlu ≈ 1,4, dağınık ≈ 3,2 mm/yıl; eşli tasarımda K_p'ye göre 0,9–2,8) kuramın öngördüğünün (0,02–0,5)
  3–150 katı. Olumsuz sonuç kuram hakkında **hiçbir şey** söylemez; taslak bunu dürüstçe yazıyor.
- Öğrettiği tek şey: yayımlanmış büyük, yıl ölçekli GNSS öncül iddialarının (Bedford 2020 tersinmesinin 0,3–2,8
  mm/yıl üst ucu gibi) **olağan** olmadığı. Bu dar ama gerçek bir bilgidir ve 0 €'dur. Ö3: örneklemde bu iddiaların
  kendi olayları varsa (ör. Bedford 2020'nin dalma-batma olayları), "VAR" onlarsız da tutmalı; liste aşama 0'da
  önceden yazılır.
- c0 tasarımıyla "VAR" çıkması ise bugünkü hâliyle yorumlanamaz (B tablosu): en olası açıklama bölge şişmesidir. Bu
  yüzden eşli plasebo olmadan koşmaya değmez.

## Zorunlu düzeltmeler (dondurmadan önce)

- **Z1.** Aşama 0 çıktısı olay ve küme listesini (ComCat id, T, M, küme, katman üst sınırı) sha256 ile dondurur;
  koşu bu listeye assert eder.
- **Z2.** Aşama 0'a bağlı dal kuralı aşama 0 koşmadan ön kayda yazılır: K_p ≥ 6 → eşli sınama ana hüküm; K_p < 6 →
  koşu yapılmaz ("güç yok").
- **Z3.** Ana sınama, 730 g geriye kaydırılmış yerinde plasebo ile eşli log oran ve kesin işaret çevirme olur (C.2).
  "Büyük etki VAR": eşli p ≤ 0,05 ve her LOO'da p ≤ 0,10. MDE tablosu K_p'ye göre yazılır.
- **Z4.** Eşli sınamanın sinyalsiz yanlış alarmı, paylaşılan pencere parçası ve renkli gürültüyle yapayda ölçülür;
  > 0,07 ise "geçersiz (kod)". Bu, gerçek S'ten önce koşar.
- **Z5.** c0 sınaması bilgi satırına iner. Tutulacaksa birimi ū'dur, olaylar w0 ≥ 2008-01-01 ile sınırlanır ve
  cümle "c_gerçek ≤ c0 varsayımı altında" diye başlar. §4'teki "c0 = 1,64: TR-11 içindeki en büyük alt küme şişmesi"
  satırı "dönem (2008) şişmesi; bölge yanlılığının ölçüsü değil" diye düzeltilir.
- **Z6.** Dal 4'teki c0 = 1 cümlesi çıkarılır ya da "bölge farkı ile öncül bu sınamada ayrılamaz" olur.

Öneriler: Ö1 hesap sırası günlüğü; Ö2 bilgi satırlarının sabit tablosu; Ö3 literatür olaylarının dışarıda
bırakıldığı bilgi satırı (aşama 0'da yazılan liste).

## Yeniden üretim

```
cd kayit/turetme/tr1b/inc1
python3 -I -B tr1b_inc1.py ../../tr11/tr11_sonuc.json tr1b_inc1.json
python3 -I -B tr1b_inc1_eslesik.py tr1b_inc1.json tr1b_inc1_eslesik.json
```
Sınırlar: sinyal modeli yapaydır (Gauss istasyon gürültüsü, katman log-normal σ); eşli modelde iki pencere bağımsız
gürültü çeker (paylaşılan parça yok, Z4 bunu koşudan önce kapatır); plasebo kuralında K_p'nin gerçek değeri bilinmiyor.
