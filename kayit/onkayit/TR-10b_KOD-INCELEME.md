DÜZELTMEYLE HAZIR

# TR-10b koşu kodu: bağımsız kod incelemesi

Tarih: 12 Kasım 2026. İncelenen dosyalar (`kayit/turetme/tr10b/`): `tr10b_kosu.py`, `tr10b_indir.py`, `tr10b_hdr.py`,
`tr10b_listeler.py`, `tr10b_liste_dondur.py`, `tr10b_listeler.json`, `tr10b_test_yapay.py`. Bağlayıcı metinler
öncelik sırasıyla okundu: ön kaydın Ek 1'i, sürüm 2 metni (DONDURULDU), `TR-10b_INCELEME-1.md`'nin düzeltme metinleri
ve `TR-10b_SAYIM.md`. Kodlayıcının okumaları `TR-10b_KODLAYICI-OKUMALARI.md`'den alındı (24 madde ve riskli yerler).

**Körlük beyanı.** Hiçbir sünme ölçer veri dosyası (DAY, 10MIN, MIC) indirilmedi ya da açılmadı. `tr10b_indir.py` ve
`tr10b_kosu.py` gerçek veriye karşı çalıştırılmadı; koşu kodu yalnız yapay dünyalarla, indirme betiği yalnız yerel
yapay sunucuyla (sınama) koşuldu. Okunan üstveri: HDR adımında zaten açılmış HDR/HDR2025 `.hdr1` dosyaları ve
`caveat.txt` (yalnız "başlık katılmış" olay tablosunu üretmek için, bkz. Ö4), SAYIM'ın ComCat önbelleği ve indirme
sayfası anlık görüntüsü (TR-10 örtüşmesinin yeniden sayımı, bkz. Ek 2 adayı 2). Ön kayıt metni değişmedi. Commit
atılmadı. `__pycache__` bırakılmadı. Depo dışı denetim betiği: karalama dizininde `kodinc10b/ortusme_mic.py`.

## Hüküm

**DÜZELTMEYLE HAZIR.** Kodun çekirdeği (okuma kuralları, §8 şartları, ölçü formülü, uç medyanları, kaynak sırası,
temsilci, K/HDR olay kuralı, kod denetimleri ve eşikleri, pozitif kontrol, bootstrap ve tohumlar, hüküm kalıpları)
ön kayıtla harfiyen uyuşuyor. Engelleyici bir hesap hatası bulunmadı. Ancak dört önemli bulgu vardı ve bu inceleme
hepsini koda işledi:

- Ö1: Ek 1 E1.4 (MIC okuma aralığı ±90 g) uygulanmamıştı;
- Ö2: kod denetimi başarısız ve kapı geçmemişse hüküm "veri yok" oluyor, kod hatası bunun ardına saklanıyordu;
- Ö3: işaret dosyalarından sonra ilk kez koşan kod tek koşuyu tüketebiliyordu. Somut bir çökme yolu da vardı: ρ_R
  aralığı "güç yok" iken `rho_okuma(None, None)`;
- Ö4: Ek 1 E1.3'ün "başlık katılmış" bilgi satırı yoktu.

Düzeltmelerle birlikte bütün sınamalar geçiyor: 57 sınama (44'ü eski, 13'ü yeni). Bağlayıcı boyuttaki yapay prova
yinelendi. Dokuz kasıtlı hatalı kod değişkesinin dokuzu da §10.2/§10.3 kod denetimlerince yakalandı. Denetimlerin
kapsamadığı iki değişkeyi (bootstrap birimi, boşluk eşiği) birim sınamaları yakaladı.

Koşudan önce kök oturumun dokuz yorum kararını "Ek 2" olarak kayda geçirmesi önerilir. Bunların ikisi kodun
davranışını belirler: okuma 19'un düzeltilmiş hali ve `--devam` mekanizması. Hiçbiri veri görülmesini gerektirmez.

---

## A. Engelleyici bulgular

Yok. Ölçü formülü, uç medyanı, gün kuralı, τ, menteşe yeri, ρ ekleme, d_analitik, (a)–(c) eşikleri, bootstrap
çekilişi ve tohumları bağımsız yeniden hesapla (sınama `test_bootstrap_tohum_ve_cekilis`, `test_b_payda_ve_pay_tohumlari`,
`test_n0_cekilisleri_pl_seri_ile_ayni`) ve mutasyon provasıyla doğrulandı.

## B. Önemli bulgular (hepsi düzeltildi)

### Ö1. Ek 1 E1.4: MIC okuma aralığı dar kalmıştı

- **Yer:** `pencere`, `oku_hepsi`, `istasyon_penceresi`, `man_sart` (`tr10b_kosu.py`).
- **Bulgu:** Bütün kaynaklar [w0 − 15 g, T + 15 g] ile okunuyordu (okuma 8). E1.4'e göre yalnız MIC kaynaklarında
  aralık [w0 − 90 g, T + 90 g]'dır ve üst uç 2023-10-16'yı aşamaz.
- **Düzeltme:** `pencere(Y, genis)` ve `kaynak_penceresi(Y, kaynak, mic_dar)` eklendi. MIC ızgarası
  [w0 − 90, min(T + 90, 2023-10-16)] oldu. `oku_hepsi` her kaynak türünü kendi aralığıyla okuyor; 2023-10-16'yı aşan
  aralıkta KosuDur. τ ve i0/iH/iT ızgaradan bağımsız. (a), (b), (c-yapay), README N0 ve d_analitik MIC'de geniş ızgarayı
  kullanıyor; N0 serisi okuma aralığının başında, yani w0 − 90 g'de, sıfırdan başlıyor (§11 madde 9). "MIC dar aralık
  (Ek 1 E1.4)" bilgi satırı, aynı okumanın [w0 − 15, T + 15]'e kısıtlanmasıyla kuruluyor. Kaynak sırası ve temsilci
  bu satır içinde yeniden seçiliyor; sayısı kapı bölümünde de yazılıyor.
- **Sınama:** `test_E14_mic_okuma_araligi` (aralıklar, 2023-10-16 tavanı, oku_hepsi'ye geçen aralıklar),
  `test_E14_mic_braket_genis_ve_dar` (geniş ızgarada geçerli olan pencere dar ızgarada "uç değeri" ile düşüyor).
  Yapay provada geçerli yer-pencere sayısı 41'den 43'e, yer sayısı 20'den 22'ye çıktı.

### Ö2. Okuma 19: kod hatası "veri yok" ardına saklanıyordu

- **Yer:** `kos`.
- **Bulgu:** Kapı geçmez ve kod denetimi üçüncü turda (ya da c-gerçek) başarısız olursa hüküm "veri yok" yazılıyor,
  kod hatası yalnız JSON'da kalıyordu.
- **Neden çelişki:** §10.2'ye göre hüküm üçüncü başarısızlıkta "kesin olarak 'geçersiz (kod)'" olur; §10.3 de aynı.
  Bu kural kapıya koşullu değildir. Kapı sayıları da başarısız olan aynı kodun (okuma, §8 şartları) ürünüdür.
  "Veri yok" o koddan çıkan bir veri hükmüdür. Kod denetimi geçmemişse bu hükme dayanılamaz.
- **Düzeltme:** Kod denetimi kesin başarısızsa hüküm kapıdan bağımsız olarak "TR-10b: geçersiz (kod) (…); gerçek Δv
  hesaplanmadı." olur. Kapı durumu `kod_hata.kapi_bilgi` alanına bilgi olarak yazılır. Tur 0–1 davranışı değişmedi.
- **Sınama:** `test_okuma19_kod_hatasi_kapi_altinda_saklanmaz`. **Ek 2 adayı 1.**

### Ö3. İşaret sonrası tek koşu riski

- **Yer:** `kos`: işaret dosyaları yazıldıktan sonra `olc_hepsi`, N0, bootstrap, satırlar, hüküm, `md_yap` ve yazım
  koşuyordu.
- **Bulgu 1 (somut çökme yolu):** Kapı geçmiş, K ≥ 4 ve N_R ≥ 20 iken ρ_R'nin bloklu aralığı yinelemelerin > %10'unda
  tanımsız olabilir. Bu, README alt kümesi R'nin tek bir blokta yığıldığı durumdur. HDR adımından sonra R büyük
  olasılıkla yalnız Parkfield'da kalıyor: K = 5–6 iken Parkfield'ın hiç çekilmeme olasılığı (4/5)^5 – (5/6)^6 ≈
  %33'tür. Bu durumda `bootstrap` `L = U = None` döndürür ve `rho_okuma(None, None)` TypeError verir. Hata işaretten
  sonra çıkar: tek koşu kullanılmış, çıktı yazılmamış olur.
  **Düzeltme:** Bu durumda okuma yapılmaz. Kalıp N_R < 20'deki "güç yok" biçimini alır: "README modeline göre (ρ_R =
  [..], yer-pencere [N_R]; güç yok)" (§9.3 %10 kuralı). Sınama: `test_rho_R_aralik_guc_yok`. Düzeltmeden önce bu
  sınama işaretten sonra TypeError verirdi.
- **Bulgu 2 (yapısal):** Gerçek veriye bağlı olmayan kurulum işaretten sonra ilk kez koşuyordu.
  **Düzeltme (ön kaydın tek koşu tanımı korunarak):**
  1. `hazirla`: girdi denetimi, okuma, bütün değişkelerin şartları ve temsilcileri, kapı, dolgu tanısı, kod
     denetimleri, c-gerçek ve README N0 çekilişleri (yalnız maske kullanır) işaretten ÖNCE koşar.
  2. **Kuru prova:** İşaretten önce `olcu_kur`, `md_yap` ve JSON dökümü D'nin bir kopyasında koşar. Kopyada gerçek
     değerler yapay serilerle değiştirilir: gerçek gün maskesi korunur, yarısı sünen (10 mm/yıl), yarısı sünmeyen
     (0,5 mm/yıl). Kopyanın blok ve R yapısı gerçek kümeyle aynıdır. Prova bir istisna verirse KosuDur atılır; işaret
     yazılmaz, gerçek Δv hesaplanmaz. Bulgu 1'deki hata bu provada yakalanırdı. Sınama:
     `test_kuru_prova_isaretten_once_yakalar`.
  3. **Okuma anlık görüntüsü:** D (okuma sonucu, maskeler, değişkeler, denetim sonuçları, N0) işaretle aynı adımda
     veri dizinine (depo dışı) `TR10B_HAM_OKUMA_ANLIK.pickle` adıyla "x" kipinde yazılır. İşaret dosyası bu görüntünün
     sha256'sını, manifest sha256'sını ve koşu kodu sha256'sını taşır.
  4. **`--devam`:** İşaretten sonra bir istisna olursa çıkış kodu 4'tür ve hiçbir çıktı yazılmaz. Bu durumda yalnız
     doğrudan neden düzeltilir ve aynı komut `--devam` ile koşulur. `--devam` ham veriyi yeniden okumaz; anlık görüntüyü
     işaretteki sha256 ile, manifesti de işaretteki sha256 ile doğrular. İki işaret de bulunmalı, çıktılar bulunmamalı.
     Çıktıya `devam` alanı yazılır: işaret anındaki ve devam anındaki kod sha256'ları (§14 madde 6: "fark kayda
     geçer"). Olağan koşu, işaret ya da anlık görüntü varken durur. Sınama: `test_isaret_sonrasi_istisna_ve_devam`.
     Bu sınama devam sırasında `oku_dosya` çağrılırsa başarısız olacak biçimde kurulmuştur.
  İşaretten sonra yalnız Δv hesabı, satır ve kalıp kurulumu ve iki "x" yazımı kalır. **Ek 2 adayı 4.**

### Ö4. Ek 1 E1.3: "başlık katılmış" bilgi satırı yoktu

- **Düzeltme:** Yeni betik `tr10b_hdr_baslik.py`. Betik `tr10b_hdr.py`'yi değiştirmeden içe aktarır (sha256'sı
  `ad20b37f…` aynı kaldı; E1.2'de kayıtlı). Değiştirdiği tek şey not birimidir: uyarlanmış not biriminde tablo satırı
  olmayan bir not, aynı paragrafta hemen ardından gelen ilk tablo satırının notuna katılır. Tarih, değişmeyen "en
  soldaki tam tarih" kuralıyla tablo satırının damgasından gelir. Betik HDR manifestinin sha256'larını denetler ve
  `tr10b_hdr_olaylar_baslik_katilmis.csv`'yi üretir (sha256 `c3f8cabb95ed2415cf540399d6dfb3a9195cb7a52377315b7015840885796dea`).
  Koşu kodu bu dosyanın sha256'sını sabitle denetler.
- **Doğrulama:** Betiğin B'ye etkisi E1.3'teki sayıyı birebir yeniden üretiyor: 47 yer-pencere / 25 yer
  (`test_E13_csv_yeniden_uretilir`). Başlık notlarının düşürdüğü yedi istasyon-pencereden altısı katılmış okumada geri
  geliyor. **CHP1 2013 yine düşüyor:** katılmış notun tarihi, ilk tablo satırının 2009-08-30 damgası, 2013
  penceresine düşüyor. E1.3'ün "7 istasyon-pencere düşürür" cümlesi bununla tutarlıdır; yedisinin de geri geleceği
  anlamına gelmez (`test_E13_baslik_katilmis_olaylari`).
- Bilgi satırı "başlık katılmış (Ek 1 E1.3)" B'nin kendi değişkesiyle kurulur (temsilci yeniden seçilir). Hükmü
  değiştirmez; sayısı kapı bölümünde de yazılır.

## C. Küçük bulgular (hepsi düzeltildi)

| # | Yer | Bulgu | Düzeltme | Sınama |
|---|---|---|---|---|
| K1 | `satir` | K ≤ 3 olan döküm ve bilgi satırlarında (epok, katman, Parkfield dışı …) bloklu aralık veriliyordu (§9.3: bloklu aralık yalnız K ≥ 4) | `birim="kesim"` ve K ≤ 3 ise yer bootstrap'ı; satırda "blok yetersiz, bilgi" | `test_satir_blok_yetersizde_yer_bootstrapi` |
| K2 | `md_yap` | A satırının "[kapı altı]" etiketi B'nin kapısına bağlıydı (§10.1: A kendi kapısıyla) | Satır kendi kural setinin kapısıyla etiketlenir | `test_1` |
| K3 | `kos`/`olcu_kur` | §8.1 ve §10.1'e göre kapıdan bağımsız olan ek kuyruklar (küme < 20, dolgu > %20) "veri yok" kalıbına eklenmiyordu | `kuyruklar()` bütün Δv'li kalıplara ve kısa "veri yok"a ekler | `test_2` (Ek 2 adayı 5) |
| K4 | `olcu_kur` | P_r aralığı "güç yok" iken Chihshang okuması "sınırda" diye uyduruluyordu. K ≤ 3'te Chihshang nokta değerleri hiç yazılmıyordu (§9.3: "Chihshang satırı da aynı kurala uyar") | "okunamaz (P_r aralığı: güç yok)"; K ≤ 3'te P_r ve P_v nokta değerleri ve yer bootstrap aralığı, bilgi olarak | kod okuması (Ek 2 adayı 8) |
| K5 | `md_yap` | q99 "N < 300: bilgi" notu yalnız etiketli durumda yazılıyordu (F8, §11); P_v ve ρ_R okuması md'de yoktu | Her durumda yazılır | `test_1` |
| K6 | `hazirla` | §11 madde 11'in "HDR adımının creep/event sayacı" denetim satırı yoktu | `tr10b_hdr_etki.json`'dan (sha256 sabit) okunur ve yazılır | `test_1` |
| K7 | `oku_dosya` | Biçim keşfinde aralık dışındaki ve 2024 sonrasındaki satırların 3. sütununun tür deseni `float()` ile hesaplanıyordu (§2.3: ilk iki sütundan sonrası ayrıştırılmaz). Değer yazılmıyordu; yalnız ayrıştırma vardı | Bu satırlarda desen "denetlenmedi" yazılır, ayrıştırma yapılmaz | `test_bicim_kesfi_desen_maskesi` |
| K8 | `oku_dosya` | Bozuk gzip gövdesi `zlib.error` veriyordu; yakalanmıyordu (işaretten önce, ama biçim keşfi iletisi olmadan) | BicimHata (KosuDur) | `test_bozuk_gzip_govdesi` |
| K9 | `hazirla`/`girdi_denetimi` | `--bicim-belirsiz` yanlış yazılmış bir URL'yi sessizce yok sayıyordu; veri dizininin depo dışında olduğu denetlenmiyordu; aynı düzeltme turu ikinci kez koşulunca yakalanmamış FileExistsError çıkıyordu | Üçü de KosuDur | `test_bicim_belirsiz_ve_veri_dizini_denetimi` |
| K10 | `hazirla` | Sonuca yalnız ön kaydın dondurulmuş önekinin sha256'sı yazılıyordu | Ek 1 dahil tam dosya sha256'sı ve boyu, yardımcı modüllerin (`tr10b_listeler.py`, `tr10b_sayim.py`, `tr2_sayim.py`) ve "başlık katılmış" ile etki dosyalarının sha256'ları da yazılır | `test_1` |

## D. Denetlenen ve uygun bulunan noktalar

- **Ölçü (§8.1–8.2):** Δv = (u(T) − u(H))/τ₂ − (u(H) − u(w0))/τ₃; v₅; τ = gün/365,25. u(P), [P − 15, P + 15]
  içindeki geçerli günlük değerlerin `numpy.median`'ıdır ve en az 10 gün gerekir. MIC'de ≤ 90 g braketle doğrusal ara
  değer alınır. Taban ≥ 12 ve yakın ≥ 8 ölçüm, [w0, T]'yi çevreleyen aralık ≤ 180 g.
- **Doluluk ve boşluk:** Doluluk iki dönemde ayrı ayrı ≥ 0,60. En uzun boşluk, uçlar dahil, ≤ 60 g.
- **Günlük değer:** Aynı güne düşen satırların medyanı; 10MIN için ⌊gün⌋.
- **Kaynak sırası (§8.3):** DAY → 10MIN → MIC, yalnız gün varlığına bakar. Temsilci (§9.1): önce telemetri, sonra en
  erken ilk gözlem, sonra kod; her kural setinde ve her değişkede ayrı seçilir.
- **Aygıt olayları:** K_OLAY [w0 − 30, T + 15]; K_SON ≤ T; HDR K olayının aralığı kesişirse düşer; D yalnız "D
  dışarıda" satırında; XMBC ve TABC listede yok.
- **Veri kapısı:** yer ≥ 20 ve yer-pencere ≥ 40; ≤ 3 km tek bağlantılı küme; düşme nedenleri; dolgulu sayılar.
- **Kod denetimleri ve eşikleri:**
  - (a) ≤ 0,005 / ≤ 0,50 / ≤ 1e-6; (a3) ve (a4) dosya yolundan, ≤ 1e-6;
  - (b): R = ⌈820/n⌉, tohum sha256(KOD|Y|j) ^ 20261112, payda M = 2000 aynı maskeyle `default_rng(20261113)`, oran
    [0,88, 1,12];
  - 144 satırlık 10MIN denetimi ≤ 0,005;
  - (c-yapay) ve (c-gerçek): şartlar [4,72, 5,11], medyan [4,85, 5,03], elle ≤ 1e-6;
  - (c-gerçek) seçimi sha256(KOD|Y) sırasıyla ilk ⌊n/2⌋; ρ günlük değere (10MIN'de medyandan sonra) gün tarihinde
    eklenir; Δv_özgün hiçbir dosyaya, log satırına ya da istisnaya yazılmaz.
- **Bootstrap (§9.3):** Fay kesimi bloklu; (B, K) çekiliş dizisi; bloklar ad sırasında; B = 2000; her satırda yeni
  `default_rng(20261112)`; yüzdelik %5–%95; > %10 tanımsızsa "güç yok"; `method="linear"`. ρ_R'nin payı ve paydası
  aynı yinelemede, aynı yer-pencerelerden tekrarlarıyla alınır. K ≥ 4 şartı ana satırda vardı; K1 ile bütün satırlara
  genişletildi.
- **Etiket ve okumalar:** b*_L > 4,6 / b*_U < 2,2; c₁ = 1,78; κ_L > 2,91; Chihshang eşiği 0,05; |r| ≥ 0,43; |Δv| ≥ 8.
- **Kalıplar (§12):** Dört hüküm kalıbı, ek kuyruklar, yanlış alarm cümlesi ve Chihshang cümlesi metindeki sözcüklerle
  birebir kuruluyor ve hem `tr10b_sonuc.md`'de hem `tr10b_sonuc.json`'da yer alıyor (sınamalar regex ile denetliyor).
  Yasak cümleler (İstanbul, Marmara, olasılık, "öncül bulundu/yok") çıktıda yok.
- **Tek koşu:** İşaretler "x" kipinde; başlangıçta iki işaret de denetleniyor; depodaki işaret manifest sha256'sını ve
  zamanı taşıyor; çıktılar "x" kipinde. Girdi sha256'ları sonuca yazılıyor: liste JSON'u, HDR CSV'si, manifest, 66
  dosyanın her biri, koşu kodu.
- **2024+ verinin okunmaması:** Bir satırın değer sütunu ancak tarihi bir okuma aralığına düşüyorsa ayrıştırılıyor.
  Bütün aralıklar ≤ 2018-12-30 (MIC) ve 2023-10-16 tavanı assert'li. `_deger` çağrıları sınamada izleniyor.
  K7 ile tür deseni de ayrıştırılmıyor.
- **Biçim hatası:** İlk sayısal satırdan sonra sayısal olmayan satır, ⌊gün⌋ = 0, geçersiz yıl ya da gün, okuma
  aralığında > %1 bozuk satır ve gzip hatası durduruyor. Keşif çıktısında sütun 3 ve sonrası `***` ile maskeli.
- **Erken çıkış:** `oku_dosya`'da `break` ya da erken `return` yok. Sırasız dosyada veri kaybolmuyor
  (`test_sirasiz_dosya_veri_kaybetmez`).
- **Liste kaynağı:** B ve A §4 tablosundan okunup kanonik sha256 ile denetleniyor; öteki üçü dondurulmuş JSON'dan;
  ön kaydın ilk 77114 baytı sha256'lı. Kod sakinliği ve kapsamı yeniden hesaplamıyor.

## E. Kodlayıcının 24 okuması

| # | Okuma (kısa) | Hüküm |
|---|---|---|
| 1 | HDR tablo satırı not birimi; üç damga biçimi | Uygun; Ek 1 E1.2 ile bağlayıcı |
| 2 | Tablo başlıkları ayrı tarihsiz not | Uygun; E1.3 ile bağlayıcı. Eksik olan "başlık katılmış" bilgi satırı bu incelemede eklendi (Ö4) |
| 3 | "Ditto" satırları K sayılmaz | Uygun (§6.4 madde 5: önek listesi değişmez). Etkisi K olaylarını az saymaktır (daha az düşme). Bilgi olarak Ek 2'ye yazılması önerilir (aday 9) |
| 4 | HDR ve HDR2025 ayrı işlenir, olaylar birleşir | Uygun (§6.4 madde 2 sırası; "aynı dosyadaki iki tarih") |
| 5 | caveat.txt'de kod sözcük sınırıyla | Uygun (daha dar okuma; 16 notun hiçbirinde kod geçmiyor, etkisiz) |
| 6 | C461 tarihsiz not başı 1960-01-01 | Uygun (sayfada yok; listelere etkisi yok) |
| 7 | B ve A §4'ten; öteki üç liste dondurulmuş JSON'dan; sha256 ilk 77114 bayt üzerinden | Uygun. Tam dosyanın (Ek 1 dahil) sha256'sı artık sonuca da yazılıyor (K10) |
| 8 | MIC dar okuma | **Ön kayıtla çelişiyordu (Ek 1 E1.4).** Düzeltildi (Ö1); dar okuma bilgi satırı oldu |
| 9 | (a)'da zaman başlangıcı okuma aralığının başı | Uygun; Ek 1 E1.5 ile bağlayıcı. MIC'de (a) doğrusal olduğu için başlangıçtan bağımsız |
| 10 | Boş satırlar hata değil, sayılır | Uygun (§5 sayısal olmayan satırı tanımlar; boş satırın alanı yoktur) |
| 11 | Aralık dışı "bozuk" yalnız < 3 alanlı satır; sütun 3 aralık dışında ayrıştırılmaz | Uygun. §5'in "sütun 3'ün sayı olmaması … aralık dışı bozuk" cümlesiyle §2.3'ün "değer sütunu ayrıştırılmadan" cümlesi arasında körlük lehine dar okuma. Sayaç bu yüzden eksik sayar; hükme etkisi yok |
| 12 | Geçersiz yıl ya da gün koşuyu durdurur | Uygun (ön kayıttan sıkı). Tarihlenemeyen satırın aralıkta olup olmadığı bilinemez; durma §5'in biçim keşfi sürecine gider. Veri kaybı ya da kayma riski yok |
| 13 | Dolgu: δ = 10^(−en çok ondalık), aday koşular uzunluğu max(15, \|V\|) olan ve V'yi içeren pencereler, eğim sıfır \|eğim\| < 1e-12 | Uygun ve en geniş yakalayan okuma. Kısa koşu daha kolay doğrusal çıktığı için en kısa aday koşuyu denemek tespiti en çoğa çıkarır; tek istisna en küçük karelerle en büyük sapma arasındaki kenar durumudur. δ'nın yalnız okuma aralığındaki değerlerden alınması körlüğün gereğidir. Dolgu payı > %20 hüküm cümlesine kuyruk eklediği için **Ek 2'ye yazılması önerilir** (aday 6) |
| 14 | Düşme nedeni önceliği | Uygun (§10.1 sıra vermiyor) |
| 15 | Menteşe modelinde yalnız (w0, T) içindeki tarihli D olayları | Uygun (w0'daki basamak sabitle eşdoğrusal; tarihsiz D'nin basamak günü yok) |
| 16 | Bilgi satırlarında temsilcinin yeniden seçilmesi ya da süzme | Uygun. "Dolgulu dışarıda" birim olarak yer-pencereyi düşürdüğü için süzme doğrudur. Yeni iki satır ("başlık katılmış", "MIC dar") temsilciyi yeniden seçer |
| 17 | Ana ve A satırı N ≥ 2'de her zaman aralık alır; öteki satırlarda N < 20 "güç yok"; A K ≥ 4 ise bloklu, değilse yer | Uygun. Yanında bir eksik vardı: N ≥ 20 olan öteki satırlar K ≤ 3'te de bloklu aralık alıyordu. K1 ile düzeltildi |
| 18 | Kapı altında K ≤ 3 ise [L, U] yer bootstrap'ı | Uygun (§9.3 ve §10.1 birlikte) |
| 19 | Kapı geçmez ve kod başarısızsa "veri yok" | **Ön kayıtla çelişiyordu (§10.2 "kesin olarak", §10.3).** Düzeltildi (Ö2): hüküm "geçersiz (kod)", kapı bilgisi. **Ek 2 adayı 1** |
| 20 | `--duzeltme-turu`; tur 0–1'de başarısızlık yalnız denetim JSON'u ve çıkış 3 | Uygun. Aynı turun yinelenmesi artık KosuDur (K9) |
| 21 | Tam maskeli bilgi paydası ⌈20000/n⌉, tohum 20261112 + 2 | Uygun (metin tohumu ve bölüşümü belirtmiyor; bilgi satırı) |
| 22 | 144 satır bütün 10MIN yer-pencerelerinde; yoksa 2013 tam maskeli yapay pencere | Uygun ("en az bir"). Yedek yol metinde yok; Ek 2'de kayıt önerilir (aday 9) |
| 23 | README N0 FFT ile; `pl_seri` ile 1e-9 içinde aynı | Uygun (sınandı; aynı rastgele akış sırası) |
| 24 | Biçim belirsiz dosyalar `--bicim-belirsiz` ile | Uygun. URL'nin manifestte olduğu artık denetleniyor (K9). Karar yalnız maskeli keşif çıktısına dayanmalı (§5) |

Riskli yerler listesindeki öteki maddeler:
- `oku_dosya`, `man_sart`/`_man_braket`, `istasyon_penceresi`/`temsilci`: uygun; E1.4 ile değişti.
- `pk_gercek`: Δv_özgün yalnız bellekte, yazılmıyor.
- `bootstrap`: ağırlıklı nicelik `np.repeat` ile doğru; ρ_R paydası doğru.
- Kalıplar ve `dolgu`: uygun.
- `tr10b_hdr.py` düzenli ifadeleri: HDR adımı tamamlandı ve E1.2 ile donduruldu; sınama çıktıyı bayt bayt yeniden
  üretiyor.
- `tr10b_indir.py`: aşağıda.

## F. `tr10b_indir.py`

Uygun; değişiklik yapılmadı.

- **Nazik indirme:** İstekler sırayla gider; aralarında 2 sn beklenir; dosya başına en çok 3 deneme yapılır (2 ve
  4 sn bekleme). Retry-After başlığı okunmuyor. 66 dosyada bunun önemi küçük; istenirse eklenebilir.
- **User-Agent:** Genel ("Mozilla/5.0 (compatible; data-fetch)"); kişisel bilgi yok.
- **401/403/404:** Yeniden denenmez, atlatılmaz (sınamada 403 tek istek).
- **Manifest:** Bellekte kurulup en sonda "x" kipinde bir kez yazılır. Manifest varsa ya da hedef dizin boş değilse
  durur; hedef depo içindeyse durur.
- **Dosya listesi:** Yalnız sha256'sı denetlenmiş `tr10b_listeler.json`'dan gelir (66 dosya; listede olmayan URL
  yok). Dosya içeriği açılmaz.
- **§2.4 madde 3:** Başarısız pay > %5 ise yalnız başarısızlar için tek yeniden deneme turu yapılır; yine aşarsa çıkış
  3 olur ve koşu kodu da durur. Tur içindeki deneme başına 3 istek, metindeki "tek tur" kuralının dışında bir
  uygulama ayrıntısıdır; tur sayısını artırmaz.
- **2024+ satırlar:** İndirme dosyanın tamamını alır, 2024–2026 satırları dahil. Bu, ön kayıtla uyumludur: §2.4
  dosyaların olduğu gibi indirilip sha256'larının alınmasını ister; §2.3 yalnız ayrıştırmayı sınırlar. İndirme betiği
  hiçbir satırı ayrıştırmaz; sha256 için baytları okur. Ham dosyalar depo dışında kalır.

## G. Mutasyon provası

`Mutasyon.test_mutasyonlar_yakalanir` ile yapıldı. Yapay dünya 66 dosyadan oluşuyor; koşu kodunun okuma ve şart
yolundan geçen 43 yer-pencere kullanıldı. R = 20, pay bağlayıcı; son koşuda payda M = 2000
(`TR10B_MUTASYON_TAM=1`). Her değişke yalnız kod denetimlerinden (a, a3, a4, b, 144, c-yapay) geçirildi.

| Değişke | Yakalayan denetim | Belirleyici değer (eşik) |
|---|---|---|
| Kontrol (doğru kod) | hepsi geçti | tam 0,00045 (≤ 0,005); gerçek maske 0,201 (≤ 0,50); (b) 0,968; c-yapay d ∈ [4,842, 5,079] |
| Uç değeri ortalamayla (medyan yerine) | (a) tam, (a3), (a4) | (a3) 8,07 (≤ 1e-6); (a4) 4,03 |
| Uç penceresi ±20 g (±15 yerine) | (a) tam | 0,025 (≤ 0,005) |
| Yıl 365 gün (τ birimi) | (a4), (c-yapay) elle | (a4) 0,0034 (≤ 1e-6); elle sapma 0,0034 (≤ 1e-6) |
| τ₂ ile τ₃ yer değiştirmiş | (a) tam, gerçek maske, elle, (a4), (c-yapay) | (a) 7,68; c-yapay d ≈ 3,2–3,4 |
| İşaret hatası | (a) tam, gerçek maske, (a4), (c-yapay) | (a) 6,00; c-yapay d ≈ −5 |
| Menteşe 30 g kaymış | (a) tam, elle, (a4), (c-yapay) | (a) 0,75; c-yapay en küçük d 4,54 (< 4,72) |
| Gün kayması (0 tabanlı gün sütunu) | (a4); (b) yolu da durur ("maskeyi korumadı") | (a4) 8,34 |
| MIC ara değer yerine en yakın ölçüm | (a) elle, (c-yapay) elle | elle 0,278 (≤ 1e-6) |
| Bloklu yerine yer bootstrap'ı | Kod denetimleri kapsamıyor; birim sınaması `Olcu.test_bootstrap_tohum_ve_cekilis` yakaladı | – |
| Boşluk eşiği 90 g (60 yerine) | Kod denetimleri kapsamıyor; birim sınaması `Sartlar.test_tele_bosluk_doluluk_uc` yakaladı | – |

Okuma: §10.2/§10.3 denetimleri ölçü yolundaki bütün kaba hataları yakalıyor. Bootstrap ve §8 şartlarının eşikleri
bu denetimlerin kapsamında değil. Onları birim sınamaları koruyor ve sınamalar koşudan önce koşuluyor.

## H. Son sınama sayıları

`python3 -I -B kayit/turetme/tr10b/tr10b_test_yapay.py -v` komutu bütün ortam değişkenleriyle (README ve HDR
sınamaları dahil) ve `TR10B_MUTASYON_TAM=1` ile koşuldu: **57 sınama, 57 geçti, 0 atlandı** (533 sn).
Bağlayıcı boyutta yapay prova (`UctanUca.test_1`; B = 2000, M = 2000, R = 20, N0 2000): 52,1 sn, en yüksek RSS 291 MB; 43 yer-pencere, 22 yer, K = 6; (b) oranı 0,968; 144 satırlık denetim 8 yer-pencerede, en büyük fark 0,00208.
Kuru prova ve anlık görüntü dahildir. Önceki prova (incelemeden önce): 41 yer-pencere, 20 yer, 46–48 sn, 289 MB.

Sınama komutu (depo kökünden; `<S>` = karalama dizini
`/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad`):

```
TR10B_HAM=<S>/tr10b/ham TR10B_INC1=<S>/tr10b_hdr/listeler.json TR10B_HDR=<S>/tr10b_hdr/dosyalar \
TR10B_TR10HAM=<S>/tr10/ham TR10B_MUTASYON_TAM=1 python3 -I -B kayit/turetme/tr10b/tr10b_test_yapay.py -v
```

## I. Koşu komutları

Bütün komutlar depo kökünden koşulur (`/home/user/knotenlinie`). `<V>` boş ya da var olmayan, depo dışındaki bir veri
dizinidir, ör. `/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/tr10b_veri`.

1. Liste denetimi (ağ yok):
   `python3 -I -B kayit/turetme/tr10b/tr10b_indir.py --hedef <V> --kuru`
2. Veri indirme (§2.4 madde 2; manifest `kayit/turetme/tr10b/tr10b_manifest_veri.json` bir kez yazılır):
   `SSL_CERT_FILE=/root/.ccr/ca-bundle.crt python3 -I -B kayit/turetme/tr10b/tr10b_indir.py --hedef <V>`
   Çıkış 3 ise başarısız pay yeniden deneme turundan sonra da > %5'tir; koşu yapılmaz.
3. Tek koşu (manifest commit edildikten sonra):
   `python3 -I -B kayit/turetme/tr10b/tr10b_kosu.py --veri <V>`
   Çıktılar: `kayit/turetme/tr10b/tr10b_sonuc.json`, `tr10b_sonuc.md` ve işaret `TR10B_GERCEK_DV_HESAPLANDI`. Bunlar
   aynı commit'e girer. `<V>` altındaki işaret ve `TR10B_HAM_OKUMA_ANLIK.pickle` depoya konmaz.
   - Çıkış 2, biçim hatası: Keşif çıktısı maskelidir. Yalnız ona dayanarak "koşu öncesi düzeltme" yapılır ve aynı
     komut yinelenir. Bir dosya biçim belirsizse `--bicim-belirsiz <URL>[,<URL>…]` eklenir.
   - Çıkış 3, kod denetimi başarısız: Kod düzeltilir ve
     `python3 -I -B kayit/turetme/tr10b/tr10b_kosu.py --veri <V> --duzeltme-turu 1` koşulur. Gerekirse sonraki tur
     `--duzeltme-turu 2` ile koşulur; bu son turdur.
   - Çıkış 4, işaret sonrası istisna: Yalnız doğrudan neden düzeltilir, fark kayda geçer ve
     `python3 -I -B kayit/turetme/tr10b/tr10b_kosu.py --veri <V> --devam` koşulur. Önceki çağrıdaki
     `--duzeltme-turu` ve `--bicim-belirsiz` değerleri aynen yinelenir.

## J. Ek 2 adayları (kök oturumun veri öncesinde kayda geçirmesi önerilir)

1. **Kod hatası kapıdan önce gelir (okuma 19).** Kod denetimi kesin olarak başarısızsa (üçüncü tur ya da c-gerçek)
   hüküm, kapı geçse de geçmese de "TR-10b: geçersiz (kod) (…); gerçek Δv hesaplanmadı." olur. Kapı sayıları denetim
   satırında bilgi olarak yazılır. Gerekçe: §10.2 "kesin olarak"; kapı sayıları da başarısız kodun ürünüdür. Kod bunu
   uyguluyor.
2. **E1.4'ün TR-10 körlüğüne etkisi (§16 madde 16'nın güncellenmesi).** MIC okuma aralığı genişleyince 1978 epoğunda
   CRR1, XGH1, XMP1 ve XMP2'nin MIC okuma aralığı TR-10'un Coalinga 1983 olay öncesi penceresiyle (1978-04-02 →
   1983-04-02) 198 gün yerine **273 gün** örtüşür (1978-04-02 → 1978-12-30). Örtüşen kısım yine TR-10'un 48 aylık
   taban döneminin başıdır; 12 aylık olay öncesi dönemine dokunmaz. Aday listesinde yeni örtüşme yoktur (yeniden
   sayım: karalama `kodinc10b/ortusme_mic.py`; SAYIM ComCat önbelleği, M ≥ 5,5, ≤ 30 km, ≤ 50 km). TR-10 yeniden
   açılırsa Coalinga notundaki "≈ 6,5 ay" bu dört istasyonun MIC kaynağında "≈ 9 ay" olur.
3. **E1.4 ile K tamponu ve uç olayları.** E1.4 MIC braketini w0 − 90 g'ye ve T + 90 g'ye dek açar. §6.1'in K
   tamponu ise [w0 − 30 g, T + 15 g] kalır. [w0 − 90, w0 − 31] ya da [T + 16, T + 90] içindeki bir K olayı (sıfırlama,
   tel değişimi) MIC ara değerini olayın öbür yanındaki ölçümle kurabilir. §16 madde 11'deki (T, T + 15 g] uç olayı
   zayıflığı da MIC'de (T, T + 90 g]'ye uzar. Kod metni uyguluyor ve tamponu genişletmiyor. Önerilen karar,
   seçeneklerden biri: (a) tamponu değiştirmeden zayıflık olarak kaydetmek; (b) yalnız MIC kaynağıyla geçerli olan
   istasyon-pencerelerde K tamponunu [w0 − 90 g, T + 90 g] yapmak. (b) daha tutucudur; uygulanırsa küçük bir kod
   değişikliği ve sınama gerekir.
4. **Tek koşunun uygulanışı.** İşaretten önce yapay değerlerle kuru prova yapılır. Okuma anlık görüntüsü işaretle
   birlikte veri dizinine yazılır; işaret görüntünün sha256'sını taşır. İşaret sonrası istisnada yalnız doğrudan neden
   düzeltilir ve `--devam` ile ham veri yeniden okunmadan sürdürülür. Çıktıya işaret anındaki ve devam anındaki kod
   sha256'ları yazılır. Bu, §14 madde 6'daki "yalnız doğrudan nedeni düzeltilir" kuralının mekanizmasıdır.
5. **Ek kuyruklar "veri yok" kalıbına da eklenir** (§8.1 ve §10.1 kuyrukları kapıya koşullu yazmıyor; §12 "ana hüküm
   cümlesinin sonuna" diyor). Eklendikleri yer, kalıbın sonudur.
6. **Dolgu tanısının okuması (okuma 13).**
   - δ, okuma aralığındaki kayma değerlerinde görülen en çok ondalık basamaktan alınır.
   - Bir uç penceresinin geçerli günleri ardışık olmalıdır.
   - Aday koşular, bu günleri içeren, uzunluğu max(15, geçerli gün sayısı) olan ve maksimal geçerli koşunun içinde
     kalan ardışık pencerelerdir.
   - "Eğimi sıfır" ölçütü |eğim| < 1e-12 mm/gündür.
   Okuma, hüküm cümlesine eklenen %20 kuyruğunu belirlediği için kaydedilmelidir.
7. **§9.3 blok sayısı şartı bütün satırlarda.** Bloklu aralık isteyen her satırda (epok, katman, kaynak, bilgi
   satırları, README T ≥ 2008) K ≤ 3 ise aralık yer bootstrap'ıyla verilir ve "blok yetersiz, bilgi" diye işaretlenir.
8. **Chihshang okuması tanımsızsa.** P_r'nin bloklu aralığı "güç yok" ise okuma "okunamaz (P_r aralığı: güç yok)"
   yazılır; kalıbın üç sözcüğünden biri uydurulmaz. K ≤ 3'te Chihshang satırının yalnız nokta değerleri ve yer
   bootstrap aralığı bilgi olarak yazılır; cümle yazılmaz.
9. **Bilgi kayıtları.**
   - E1.3: Başlık notlarının düşürdüğü yedi istasyon-pencereden altısı katılmış okumada geri gelir; CHP1 2013 gelmez.
     Katılmış tablonun üretim kodu `tr10b_hdr_baslik.py`, tablonun sha256'sı `c3f8cabb…6dea`'dır.
   - Okuma 3 ("Ditto" satırları K sayılmaz) K olaylarını az sayar.
   - Okuma 22: 10MIN yer-penceresi yoksa 144 satırlık denetim 2013 tam maskeli yapay pencereyle yapılır.

## K. Değişen ve eklenen dosyalar (commit edilmedi)

- `kayit/turetme/tr10b/tr10b_kosu.py`: Ö1–Ö3 ve K1–K10.
- `kayit/turetme/tr10b/tr10b_test_yapay.py`: 13 yeni sınama (`IncelemeDuzeltmeleri` 12, `Mutasyon` 1). Eski sınamalarda
  yalnız üç uyarlama yapıldı: yapay dünyanın veri kapsamı MIC aralığını aşacak biçimde ±100 g'ye genişletildi;
  "veri yok" kalıbının regex'i kuyruklara izin verecek biçimde genişletildi; işaret log satırının adı değişti.
- `kayit/turetme/tr10b/tr10b_hdr_baslik.py` (yeni) ve `tr10b_hdr_olaylar_baslik_katilmis.csv` (yeni; yalnız
  üstveri).
- `kayit/onkayit/TR-10b_KOD-INCELEME.md` (bu belge).

Değişmeyenler: `tr10b_hdr.py` (sha256 `ad20b37f…`), `tr10b_indir.py`, `tr10b_listeler.py`, `tr10b_listeler.json`,
`tr10b_liste_dondur.py`, `tr10b_hdr_olaylar.csv` ve ön kayıt metni. `tr10b_kosu.py` değiştiği için, varsa onun
sha256'sını anan kayıtlar güncellenmelidir.
