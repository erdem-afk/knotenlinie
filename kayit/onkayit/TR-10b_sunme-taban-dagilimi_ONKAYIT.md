# TR-10b ön kaydı: sünme ölçerlerde sakin pencerelerde 2 yıllık sünme hızı değişiminin taban dağılımı

Tarih: 12 Kasım 2026. Durum: **DONDURULDU sürüm 2 (12 Kasım 2026; bu commit dondurma kaydıdır) (İNCELEME-1 düzeltmeleri işlendi).** Dondurulduktan sonra
metin değişmez; ekler ayrı başlıkla yazılır.
Türediği yer: `kayit/onkayit/TR-10_SAYIM.md` §6 (olay gerektirmeyen ara ölçüm) ve tasarım + üstveri sayımı
`kayit/onkayit/TR-10b_SAYIM.md` (kapı SINIRDA). İnceleme: `kayit/onkayit/TR-10b_INCELEME-1.md` (DÜZELTMEYLE KABUL).
Kod: `kayit/turetme/tr10b/tr10b_sayim.py`; bu sürümün yeniden üretim betikleri `kayit/turetme/tr10b/onkayit_yardimci/`
(`inc1_*.py`; İNCELEME-1 betiklerinin kopyaları `inc10b/` altında). Maliyet 0 €.

Bu bir **ölçümdür**, hipotez sınavı değildir. Çıktısı bir yanlış alarm ölçeğidir: önceden tanımlı sakinlik kurallarını
geçen dönemlerde nokta sünme ölçeriyle ölçülen 2 yıllık hız değişiminin ne büyüklükte ve ne sıklıkta olduğu. Deprem
olasılığı üretmez. Mutlak İstanbul deprem olasılığı bu belgede ve koşunun hiçbir çıktısında yazılmaz.

Körlük beyanı (bu belge yazılırken, sürüm 1 ve 2): hiçbir sünme ölçer veri dosyası (DAY, 10MIN, MIC, CL10, PKF_EQ,
HaywardCreep), hiçbir HDR/Notes dosyası, HDRx.tar ve noise.pdf açılmadı ya da indirilmedi. Okunanlar: SAYIM'ın
önbelleğindeki indirme sayfası anlık görüntüsü, README (biçim belgesi, gürültü tablosu, "Comments specific to various
creepmeters" bölümü, dosya aralığı listesi), dizin listeleri (yalnız dosya adları), HEAD sonuçları, ComCat dosyası ve
`TR-10_SAYIM.md`. Bu belgedeki bütün yeni sayılar `tr10b_sayim.py`'nin değiştirilmemiş işlevleriyle (sayım için `say`,
yapay hesap için `pl_seri`, `dv_uc`, `gunler`) `python3 -I -B` altında üretildi; yapay hesaplar yalnız üretilmiş
gürültüyle yapıldı. Sürüm 2'nin yeni sayıları §19'daki betiklerle depodan yeniden üretilir.

## 0. Öncelik sırası ve SAYIM'dan farklar

**Öncelik sırası.** Çelişkide şu sıra geçerlidir:
1. **Bu belgenin sürüm 2 metni.** Metnin içinde §4'teki aday listeleri (kanonik sha256 ile) öteki bölümlerden önce
   gelir.
2. **`TR-10b_INCELEME-1.md` düzeltme metinleri.** Sürüm 2 bunları işledi (§20). Yalnız sürüm 2'nin bir noktada
   sustuğu ya da iki okumaya açık kaldığı yerde başvurulur; sürüm 2 metniyle çelişirse sürüm 2 geçerlidir.
3. **`TR-10b_SAYIM.md` §2** (tasarım), yalnız bu belgenin ve İNCELEME-1'in değiştirmediği yerlerde.

Bu belge SAYIM'ı şu noktalarda değiştirir ya da tamamlar (hepsi hiçbir sünme verisi görülmeden):

| # | SAYIM | Bu ön kayıt | Neden |
|---|---|---|---|
| F1 | Kapı R2 kapsam modeliyle sayıldı | Aday kümesi U (üst sınır) kapsamıyla kurulur; gerçek kapsamı veri belirler; kapı gerçek veriyle yeniden uygulanır (§4, §10.1) | R2 bir kapsam tahminiydi; veri okununca tahmine gerek kalmaz |
| F2 | Güven aralığı site bootstrap'ı, kesim bootstrap'ı bilgi | **Fay kesimi bloklu bootstrap ana**, site bootstrap'ı bilgi satırı (§9) | Kök oturum kararı 4 |
| F3 | Tek kural seti seçimi incelemeye bırakıldı | A ve B ikisi de bağlayıcı; **B ana hüküm satırı, A zorunlu ikinci satır** (§7) | Kök oturum kararı 1 |
| F4 | HDR kuralı açık | HDR okuma sırası ve mekanik kullanım kuralı sabit; HDR adımı son veren olay üretmez; kural README "Comments" bölümünde önceden sınandı (§6.4) | Kök oturum kararı 3; İNCELEME-1 E1 |
| F5 | Pozitif kontrol: medyan(d) ∈ [4,90, 5,03] | Telemetri katmanında deterministik sınır + medyan(d) ∈ [4,85, 5,03]; elle ölçüm katmanında analitik tam denetim (§10.3) | Gerçekçi ve en kötü maskelerle yapay doğrulama (§10.2.1) |
| F6 | (b) paydası tam maskeli MC | Payda aynı gerçek maskelerle ayrı MC; tam maskeli oran bilgi satırı (§10.2) | Payda maske seçiminden bağımsız olsun |
| F7 | Eşdeğer rastgele yürüyüş sabiti c₁ = 1,732 (4000 çekiliş) | c₁ = 1,78 (100 000 çekiliş) (§10.4) | 1,732'nin MC hatası ≈ ±0,027 (≈ 1,8 sd altta); fark %2,7 |
| F8 | %99 yazılmaz | q99 yazılır, "N < 300: bilgi" notuyla (§11) | Görev tanımındaki çıktı satırı |
| F9 | Site temsilcisi: en erken ilk gözlem | Önce telemetri, sonra en erken ilk gözlem (§9.1) | Eş konumlu elle ölçerin telemetriyi dışlamaması |
| F10 | K tamponu [w0 − 30 g, T] | [w0 − 30 g, T + 15 g] (§6.1) | Uç penceresinin ikinci yarısı; sayıma etkisi 0 (§6.1) |
| F11 | Literatür yerleşimi bütün doğrulanmış iddialar için | Yalnız Chihshang 2003, bilgi satırı (§10.5) | Kök oturum kararı 5 |
| F12 | "Sakinlik kapalı" değişkesi bilgi satırı (SAYIM §8) | Yazılmaz (§16 madde 12) | Olaylı pencereleri okumak TR-10'un körlüğünü bozar. Aday listesindeki tek örtüşme (1983 Coalinga × 1978 epoğu, yalnız TR-10'un taban dönemi) §16 madde 16'da yazılıdır |
| F13 | Etiket "README gürültü bandı"na göre | Etiketin adı "README'nin n = 2 istasyonlarının genlik aralığı"; README modeliyle karşılaştırma ayrı satır ρ_R (§10.4) | İNCELEME-1 E2: README modeli bu karışım için b* ≈ 10 öngörür |
| F14 | Blok sayısı şartı yok | Bloklu aralık, b* etiketi ve okumalı satırlar yalnız K ≥ 4 blokta (§9.3) | İNCELEME-1 Ö1 |

## 1. Soru

Orta Kaliforniya'nın sünen fay kesimlerinde, deprem etkisinden önceden tanımlı kurallarla arındırılmış ("sakin") 5
yıllık pencerelerde, bir sünme ölçerin son 2 yıldaki ortalama sünme hızı önceki 3 yıldakinden ne kadar farklıdır
(Δv, mm/yıl; ve sünen ölçerlerde hızın yüzdesi olarak r)? |Δv|'nin medyanı, %95 ve %99 nicelikleri nedir? Bu
nicelikler, bir sünme ölçerdeki yıl ölçekli hız değişiminin tek başına "olağandışı" sayılabilmesi için gereken
büyüklüğün, yani bir yanlış alarm ölçeğinin, ölçümüdür.

## 2. Veri ve erişim

### 2.1 Kaynaklar

- **İndirme sayfası:** `https://earthquake.usgs.gov/monitoring/deformation/data/download.php`, Creepmeter tablosu.
  Bağlayıcı anlık görüntü TR-10'unkidir (sha256 `74b3eb437b530436231e9758fe3d1c18d71c09c351530820e08bc32bb0f0edc1`;
  `tr10b_sayim.py` assert eder). Dosya listesinin kaynağı yalnız bu tablodaki bağlantılardır: 126 bağlantı (HDR 29,
  MIC 40, 10MIN 31, DAY 26). Bağlantı listesinin sha256'sı `d3daa5ab119b123292cc1f9fe7c5f2e6c074adc9402412dc9b2771677a07e51b`,
  HEAD sonuçlarınınki `96db292a432990049f47f1fcd87a00880921bb0a0dbb8f6f462473496f2b8b49`.
- **Arşiv kökü:** `https://escweb.wr.usgs.gov/share/langbein/Archive/CREEP/` (alt dizinler DAY, 10MIN, MIC, HDR,
  HDR2025). Bir 10MIN bağlantısı `https://escweb.wr.usgs.gov/share/langbein/Archive/HaywardCreep/10MIN/c461.10min.gz`
  yolundadır (C461; aday listesinde yok).
- **README:** `https://escweb.wr.usgs.gov/share/langbein/Archive/CREEP/README` (sha256
  `6b1e95c03d3eae822d614f764fa6ed286845cdf2470bc754d8316c813923b13b`). Biçim belgesi budur.
- **Atıf:** Langbein, Bilham, Snyder, Ericksen 2024, OFR 2024-1011, 10.3133/ofr20241011.
- **Katalog:** ComCat, SAYIM'ın sorgusu (M ≥ 4,5; 30,5–42,5° K, 128–113° B; 1955-01-01 → 2025-12-31T23:59:59;
  `type = earthquake`; 1674 deprem; sha256 `cbd2bc88b726d2c791b3407a59a3c53f3050cea0d4e543017963e5ab89c9bc98`).
  Koşu kataloğu yeniden sorgulamaz; sakinlik aday listesine işlenmiştir (§4). Yeni bir sorgu gerekirse bitiş
  ≤ 2025-12-31T23:59:59'dur (`tr2_sayim.sorgu` assert eder).

### 2.2 Kullanılan ve kullanılmayan dosyalar

- **Kullanılır:** aday listesindeki 35 istasyonun sayfadaki DAY (16), 10MIN (21) ve MIC (29) bağlantıları (toplam 66
  dosya) ve HDR adımı için §6.4'teki HDR dosyaları.
- **Kullanılmaz:** CL10 (birimi sayım, ölçeklenmemiş), PKF_EQ, PLOTS, HDRx.tar, noise.pdf, `xta1_orig.day.gz` ve
  sayfada bağlantısı olmayan her dosya, `HaywardCreep/*_merge.jl.gz`, "Big Creep" eşleri (XMBC, TABC; README:
  düzenlenmemiş) ve aday listesinde olmayan istasyonların dosyaları.

### 2.3 Veri sınırı

- Kullanılabilecek son gün **2023-10-16**'dır (son epoğun T + 15 g'si). 2024 ve sonrasının hiçbir satırının ilk iki
  sütundan sonrası ayrıştırılmaz (satırın atlanacağını anlamak için tarih ayrıştırılmak zorundadır). Aday listesinde 2023 epoğu olmadığı için fiilen kullanılan son gün 2018-10-16'dır.
- Okuma kuralı (TR-11 Ek 2 dersi): her satırın yalnız ilk iki sütunu (yıl, gün) ayrıştırılır. Tarih, istasyonun
  aday pencerelerinden birinin okuma aralığına ([w0 − 15 g, T + 15 g]) düşmüyorsa satırın değer sütunu
  ayrıştırılmadan ve saklanmadan atlanır, yalnız sayılır. Okuma dosya sonuna dek sürer; sırasız dosyada veri
  kaybolmaz.
- Katalog sorguları ≤ 2025-12-31.

### 2.4 İndirme ve sha256 manifesti

1. **HDR adımı** (§6.4, ön kayıt dondurulduktan hemen sonra): yalnız HDR dosyaları indirilir. Manifest
   `kayit/turetme/tr10b/tr10b_manifest_hdr.json` (URL, boy, Last-Modified, sha256, indirme zamanı) commit edilir.
2. **Veri adımı** (kod incelemesinden sonra): §2.2'deki 66 veri dosyası depo dışına (scratch) indirilir. Manifest
   `kayit/turetme/tr10b/tr10b_manifest_veri.json` aynı alanlarla commit edilir. Dosyalar depoya konmaz.
3. İndirme hatası dosya düzeyinde kayda geçer. Başarısız dosyaların payı %5'i aşarsa tek bir yeniden deneme turu
   yapılır; yine aşarsa koşu durur (hiçbir Δv hesaplanmadan). %5'in altındaki başarısız dosyalar "indirilemedi"
   nedeniyle düşer ve sayılır.
4. Koşu kodu her dosyanın sha256'sını manifestle karşılaştırır. Uyuşmazlıkta durur.
5. 10MIN dosyaları her gün güncellenir; manifest tek bir indirme anının görüntüsüdür ve yalnız o kullanılır.

## 3. Epoklar (önceden sabit, örtüşmez)

Y ∈ {1973, 1978, …, 2023}. w0 = (Y−5)-10-01, H = (Y−2)-10-01 (menteşe), T = Y-10-01. Taban dönemi [w0, H) 3 su yılı,
yakın dönem [H, T) 2 su yılı. Okuma aralığı [w0 − 15 g, T + 15 g]. Uç noktaları aynı takvim gününe (1 Ekim, kuru
mevsim sonu) düştüğü için durağan yıllık ve altı aylık döngü ölçüden düşer.

| Y | w0 | H | T | [w0, H) gün | [H, T) gün | Okuma aralığı |
|---|---|---|---|---|---|---|
| 1973 | 1968-10-01 | 1971-10-01 | 1973-10-01 | 1095 | 731 | 1968-09-16 → 1973-10-16 |
| 1978 | 1973-10-01 | 1976-10-01 | 1978-10-01 | 1096 | 730 | 1973-09-16 → 1978-10-16 |
| 1983 | 1978-10-01 | 1981-10-01 | 1983-10-01 | 1096 | 730 | (aday yok) |
| 1988 | 1983-10-01 | 1986-10-01 | 1988-10-01 | 1096 | 731 | (aday yok) |
| 1993 | 1988-10-01 | 1991-10-01 | 1993-10-01 | 1095 | 731 | (aday yok) |
| 1998 | 1993-10-01 | 1996-10-01 | 1998-10-01 | 1096 | 730 | 1993-09-16 → 1998-10-16 |
| 2003 | 1998-10-01 | 2001-10-01 | 2003-10-01 | 1096 | 730 | 1998-09-16 → 2003-10-16 |
| 2008 | 2003-10-01 | 2006-10-01 | 2008-10-01 | 1096 | 731 | 2003-09-16 → 2008-10-16 |
| 2013 | 2008-10-01 | 2011-10-01 | 2013-10-01 | 1095 | 731 | 2008-09-16 → 2013-10-16 |
| 2018 | 2013-10-01 | 2016-10-01 | 2018-10-01 | 1096 | 730 | 2013-09-16 → 2018-10-16 |
| 2023 | 2018-10-01 | 2021-10-01 | 2023-10-01 | 1096 | 730 | (aday yok; Ridgecrest) |

τ₃ = [w0, H) gün sayısı / 365,25, τ₂ = [H, T) gün sayısı / 365,25.

## 4. Aday listesi (bağlayıcı)

Aday istasyon-penceresi, şu üç şartı veri okunmadan sağlayan (istasyon, Y) çiftidir:
- kapsam: U senaryosu (sayfadaki ilk gözlem → dosyaların en geç Last-Modified tarihi; SAYIM §2.2);
- aygıt: SAYIM'ın K listesinden geçer (K_OLAY 32, K_SON 8; Big Creep dışarıda);
- sakinlik: kural seti B'den (B listesi) ya da A'dan (A listesi) geçer (§7).

Liste, `tr10b_sayim.py`'nin `say` işlevi değiştirilmeden, içindeki `degerlendir(kapsam_sen="U", kurallar=KB)` ve
`degerlendir(kapsam_sen="U")` çağrılarının dökümüyle üretildi. Üretim SAYIM'ın bütün `sonuc` alanlarını birebir
yeniden üretti (özet JSON ile karşılaştırıldı: aynı). **Kanonik biçim:** her istasyon-pencere için `f"{KOD}|{Y}\n"`
satırı, satırlar sıralanır ve birleştirilir, UTF-8 SHA-256 alınır.

- **B listesi:** 78 istasyon-pencere, 35 istasyon, 62 site-pencere, 29 site, 6 kesim.
  sha256 `17f120d295447f7aa102f3d8d18c223e7f0822ac9ca0467e6690b5c094997101`.
- **A listesi:** 38 istasyon-pencere, 30 istasyon, 31 site-pencere, 25 site, 5 kesim.
  sha256 `c027949015ff962f9e8ec56990f2808642c1a39c81c725c9bb615f094857a422`. A listesi B listesinin alt kümesidir.
- Karşılaştırma için SAYIM'ın R2 listeleri (§11 madde 9 bilgi satırının alt kümesi): B 42 istasyon-pencere, 23
  istasyon, 41 yer-pencere, 22 yer, 5 kesim; sha256 `560b49c1c634202a5451c85da8e26fb87059fe6e025a1956f53989cece6d036d`.
  A 22 istasyon-pencere, 19 istasyon, 22 yer-pencere, 19 yer, 4 kesim; sha256
  `cc238e03b244ec752928c705967647830e859b92d0c9e11f23df427e44b71426`. B_R2 B listesinin, A_R2 A listesinin alt
  kümesidir. Koşu bu alt kümeleri listelerin içinden bu sha256'larla seçer.
- Bütün sha256'lar ve sayılar `onkayit_yardimci/inc1_listeler.py` ile yeniden üretilir (§19).

| Kesim | İstasyon: B epokları (A epokları) |
|---|---|
| CAL_Hollister | XSH1 2013, 2018 (2018); SHR2 2013, 2018 (2018); HLC1 2013, 2018 (2018); HLD1 2013, 2018 (2018) |
| HAY | CPP1 2003 (2003); CTM1 2003 (2003); COZ1 2003, 2008, 2013 (2003); CHP1 2003, 2008, 2013 (2003); CFW1 2003, 2018 (2003); HWR1, HWR2, HWE1, HWW1, HWP1: her biri 1973, 2003, 2008, 2013 (1973, 2003) |
| SAF_SJB | SJN1 2018 (2018); XHR1 2018 (2018); XHR3 2018 (2018); CWN1 2018 (2018); XSJ3 2018 (2018) |
| SAF_sunen_orta | XDL2 1998, 2013, 2018 (–); BIT1 1998 (–); XMP1 1978, 1998 (–); XMP2 1978, 1998 (–); XSC1 2013, 2018 (–) |
| SAF_Parkfield | XMM1, XMD1, XVA1, XPK2, XTA1, WKR1, X461: her biri 2013, 2018 (2018); CRR1 1973, 1978, 2013, 2018 (1973, 1978, 2018); XGH1 1978, 2013, 2018 (1978, 2018) |
| SAF_guney_gecis | TWR1 2013, 2018 (2018); XPH1 2013, 2018 (2018) |

B'nin site-pencere dökümü (U, veri öncesi üst sınır): kesime göre Parkfield 21, Hayward 19, SAF orta sünen 8,
Calaveras 6, SAF SJB 4, SAF güney geçiş 4; epoğa göre 1973: 4, 1978: 3, 1998: 3, 2003: 7, 2008: 4, 2013: 20, 2018: 21.

U, R2'ye 36 istasyon-pencere (21 yer-pencere) ekler: HW* elle ölçerlerinin 1973 ve 2003–2013 pencereleri (20), HLC1,
HLD1 ve SHR2'nin 2013–2018 pencereleri (6), TWR1 ve XPH1'in 2013–2018 pencereleri (4), XDL2 2013 ve 2018 (2), BIT1,
XMP1 ve XMP2 1998 (3) ve XHR1 2018 (1). XHR1 dışındakilerin hepsi README dosya aralıklarının dışındadır. XHR1'in
README'de aralığı yoktur. README aralığı dışındaki adaylar veri okununca büyük olasılıkla doluluk şartıyla düşer.
Listeye alınmaları yalnız "kapsamı veri belirler" ilkesinin sonucudur; sayıyı artırmaları beklenmez (§13).

Koşu kodu listeyi bu belgeden okur, kanonik sha256'yı denetler (uyuşmazsa durur) ve sakinliği ya da kapsamı yeniden
hesaplamaz. Kapsamı yalnız gerçek veri ve §8'deki doluluk şartları daraltır; listeye aday eklenmez.

## 5. Okuma ve biçim kuralları

- **Biçim (README):** gzip'li ASCII; sütun 1 yıl, sütun 2 yılın günü ("Julian day"; 10MIN'de saat ve dakika
  ondalık), sütun 3 kayma (mm, sağ yanal pozitif). Dördüncü ve sonraki sütunlar yok sayılır.
- **Tarih:** gün = 1 Ocak(yıl) + (⌊gün sütunu⌋ − 1). Geçerli satır: en az 3 alan; ilk üç alan sonlu sayı; yıl tam
  sayı ve 1960 ≤ yıl ≤ 2026; 1 ≤ ⌊gün⌋ ≤ yılın gün sayısı.
- **Biçim hatası koşuyu durdurur, "veri yok" üretmez.**
  - Bir dosyada ilk sayısal satırdan sonra sayısal olmayan bir satır, ya da okuma aralığındaki satırlarda bozuk satır
    payı %1'i aşarsa koşu durur (KosuDur). İlk sayısal satırdan önceki sayısal olmayan satırlar başlık sayılır.
  - Okuma aralıkları dışındaki satırlarda yalnız ilk iki alan denetlenir. Bu satırlarda sütun 3'ün sayı olmaması
    koşuyu durdurmaz, "aralık dışı bozuk" diye sayılır.
  - ⌊gün⌋ = 0 olan tek bir satır bile durdurur. Bu, 0 tabanlı gün kuralını sessizce bir gün kaydırmamak içindir.
  - Bu durumlar bir veri sonucu değil, kod ya da biçim sorunudur. Hiçbir Δv hesaplanmadan, yalnız aşağıdaki biçim
    keşfi çıktısına dayanarak düzeltilir ve "koşu öncesi düzeltme" başlığıyla kayda geçer.
- **Biçim keşfi (körlüğü koruyarak).** Okuyucu bir dosyada kurala uymayan ilk satırda durduğunda yalnız şunları
  yazar: dosya adı, satır numarası, alan sayısı, her alan için tür deseni (tam sayı / ondalık / metin) ve sütun
  1–2'nin değerleri. Sütun 3 ve sonrasının değeri yazılmaz, `***` ile maskelenir. Koşu öncesi düzeltme yalnız bu
  çıktıya dayanır. Gerekirse ilk 5 sayısal satır aynı maskeyle gösterilir. Kayma değerlerine bakılarak yapılan
  hiçbir düzeltme kabul edilmez. Bu tür bir gereksinim doğarsa dosya "biçim belirsiz" nedeniyle düşer ve sayılır.
  (README'ye göre Bilham'ın Hayward ölçerleri CPP1, CTM1, COZ1, CHP1 ve CFW1 arşivin dışındadır ve 10MIN biçimleri
  belgelenmemiştir; biçim hatası en çok bu dosyalarda beklenir.)
- **Günlük değer:** her kaynakta (DAY, 10MIN, MIC) aynı takvim gününe düşen geçerli satırların medyanı. 10MIN
  böylece günlük medyana indirgenir.
- **Eksik değer kodu:** README bir kod tanımlamıyor. Kayma değeri sonlu değilse ya da |kayma| ≥ 10⁴ mm ise satır
  "bozuk" sayılır (yukarıdaki %1 kuralına girer). Bu eşik bir yanlış değer süzgeci değil, bir biçim denetimidir.

## 6. Aygıt olayı kuralları

### 6.1 K olayları (SAYIM `K_OLAY`, 32 kayıt; aynen bağlayıcı)

- Olay tarihi [w0 − 30 g, T + 15 g] içindeyse istasyon-pencere düşer. Tarihte gün bilinmiyorsa ayın 1'i, ay
  bilinmiyorsa 1 Ocak alınır.
- SAYIM'daki üst uç T idi; T + 15 g, u(T)'nin uç penceresini de korur (F10). Sayıma etkisi yoktur: K ve D
  listelerinde hiçbir tarih bir epok yılının 1–16 Ekim aralığına düşmüyor (listeler elle denetlendi).

### 6.2 Son veren K olayları (`K_SON`, 8 kayıt)

CWC3 2000-01-01, XHR2 2004-06-01, XHSW 2010-07-01, XRSW 2005-09-01, XFL1 1995-03-11, XPK1 2004-09-28, XSJ2 2006-07-01,
XMBC 2011-01-12. Bu tarihten sonraki bütün pencereler düşer.

### 6.3 D olayları ve Big Creep

- D olayları (`D_OLAY`, 12 kayıt): 2006–2008 DCP ve elektronik değişimi. Ana satırda kalır; "D dışarıda" bilgi
  satırında olayı [w0 − 30 g, T + 15 g] içinde olan pencere düşer.
- XMBC ve TABC hiçbir satıra girmez.

### 6.4 HDR (Notes) dosyaları: üstveridir, kapsam adımında okunur

1. **Ne zaman:** ön kayıt dondurulduktan hemen sonra, hiçbir veri dosyası indirilmeden ve ölçü kodu yazılmadan önce.
   HDR dosyaları seri değeri taşımaz; yalnız aygıt olayları için okunur. Bu adımda hiçbir hız hesaplanmaz. Kuralın
   kodu `onkayit_yardimci/inc1_hdr_kural.py`'nin çekirdek işlevleridir (`notlara_bol`, `tarih`, `onekler`, `tur`,
   `isle`; README'ye özgü istasyon ataması dışında); HDR adımı bu işlevleri değiştirmeden kullanır, uyarlama yalnız
   madde 5'e göre yapılır.
2. **Hangi dosyalar, hangi sırayla:**
   1. `CREEP/HDR/` altındaki, sayfada bağlantısı olan 29 `*.hdr1` dosyası (alfabetik; bağlantısız `c461.hdr1`
      okunmaz);
   2. `CREEP/HDR2025/` altındaki 30 `*.hdr1` dosyası (alfabetik; 1'deki 29 dosyanın adaşları ve c461);
   3. `CREEP/HDR/caveat.txt`.
   `._*` dosyaları (macOS kaynak çatalı) ve HDRx.tar okunmaz.
3. **Kullanım kuralı (mekanik; README "Comments specific to various creepmeters" bölümünde önceden sınandı,
   TR-10b_INCELEME-1 §D ve §19).**
   - **Not birimi:** boş satırla ya da yalnız `-`, `=`, `*`, `_` ve boşluktan oluşan bir satırla ayrılan paragraf.
     Dosyada hiç boş satır yoksa her satır bir nottur. Not, bulunduğu `.hdr1` dosyasının istasyonuna aittir.
     `caveat.txt`'teki bir not yalnız metninde kodu (büyük-küçük harf duyarsız) geçen istasyonlara işlenir. Kod
     geçmiyorsa not hiçbir istasyona işlenmez, yalnız listelenir.
   - **Tarih:** notun metninde en solda başlayan tam tarih. Tam tarih biçimleri büyük-küçük harf duyarsızdır.
     "Ay", İngilizce ay adının tam ya da ilk üç harfli biçimidir ("Sept" dahil) ve ardından nokta gelebilir.
     Biçimler: YYYY-MM-DD; YYYY/MM/DD; MM/DD/YY ya da MM/DD/YYYY (ABD sırası); "G Ay YYYY"; "Ay G YYYY" ve
     "Ay G, YYYY"; "Ay YYYY", "Ay, YYYY" ve "Ay–Ay YYYY" (ilk ayın 1'i); "YYYY GGG", "YYYY.GGG" ve "YYYY:GGG" (yılın
     günü). İki haneli yıl > 30 ise 19xx, değilse 20xx alınır. Notta tam tarih yoksa en soldaki yalın dört haneli yıl
     (1960–2023) alınır; tarih o yılın 1 Ocak'ıdır. Bir aralık yazılmışsa (ör. "1993 to 1996", "Sept-October 2005")
     en soldaki tarih kuralı başlangıcı verir.
   - Tarihi 2023-10-16'dan sonra olan notlar anahtar sözcük aranmadan atlanır.
   - **K olayı:** notun küçük harfe çevrilmiş metninde şu öneklerden biri bir sözcüğün başında geçiyorsa (önünde harf
     ya da rakam yok; sonu serbest): reset, re-set, rezero, re-zero, zero, broke, break, snap, replac, new wire,
     new rod, new sensor, new transducer, new lvdt, removed, relocat, reinstall, re-install, reposition, offset,
     repair, damage, vandal, collapse, caved, cave-in, cave in, flood, rodent, gopher, out of range, overrange,
     over-range, ran out, calibrat, recalibrat, re-calibrat, miscalibrat, mis-calibrat, fail, unreliab, touch,
     tighten, loosen, bump, peg, tension, slid, offline, glitch, spurious, bogus, delet, abandon, destroy,
     decommission, no longer. "moved" ve "bent" yalnız tam sözcük olarak eşleşir. (Satır sonları ve art arda
     boşluklar eşleştirmeden önce tek boşluğa indirgenir; böylece iki satıra bölünmüş çok sözcüklü önekler de
     eşleşir.)
   - **D olayı:** notta K öneklerinden hiçbiri yoksa ve electronic, dcp, scale factor ya da gain öneklerinden biri
     geçiyorsa.
   - **HDR adımı "son veren" olay üretmez.** Terk, söküm ya da kalıcı arıza anlatan notlar da yalnız K olayıdır ve
     yalnız [w0 − 30 g, T + 15 g] aralığı tarihini içeren pencereleri düşürür. Gerçekten terk edilmiş bir ölçerin
     sonraki pencereleri veri olmadığı için §8 şartlarıyla zaten düşer. Son veren olaylar yalnız §6.2'deki dondurulmuş
     listedir.
   - Olay tarihi notun tarihidir.
   - **Tarihsiz not:** K ya da D öneki içeren ama tarihi olmayan not, aynı dosyadaki iki tarih arasındaki aralık
     olarak işlenir. Aralığın başı kendisinden önceki son tarihli notun tarihidir; önceki tarihli not yoksa istasyonun
     sayfadaki ilk gözlemidir. Aralığın sonu sonraki ilk tarihli notun tarihidir; sonraki tarihli not yoksa
     2023-10-16'dır. ("Tarihli not", K ya da D öneki içersin içermesin tarihi olan her nottur. Notlar tarih sırasında
     değilse ve baş sondan sonra kalırsa iki uç yer değiştirir.) Bu aralık [w0 − 30 g, T + 15 g] ile kesişen her
     pencere düşer (D olayında yalnız "D dışarıda" bilgi satırında düşer). Elle yapılabilecek tek iş, notun kendi
     metninde açıkça yazan ama ayrıştırıcının tanımadığı bir tarihi, özgün satırı alıntılayarak yazmaktır. Bu durumda
     aralık yerine o tarih kullanılır. Başka hiçbir elle tarihleme ya da yorum yapılmaz.
   - **Önceden sınama sonucu (README vekili, §19).** Kural README bölümündeki K_OLAY listesinin 30 olayından 28'ini
     en çok 1 yıl önceki bir tarihle K olayı olarak yakalıyor. Kaçan ikisi XGH1 1997-12 (not 1998-04-17 tarihli; aynı
     1998 epoğunu düşürür) ve XMM1 1986 (notun en soldaki yılı 1993; 1988 epoğunda aday yok). Sahte son veren olay
     yok. Epok düzeyinde kural, K_OLAY'ın düşürdüğü 26 (istasyon, epok) çiftinden 25'ini düşürüyor (eksik XMM1 1988);
     fazladan düşürdüğü ikisi XGH1 2008 ("calibration confirms" yanlış pozitifi) ve XHR2 2013'tür, ikisi de aday
     değildir. Olay kümesi İNCELEME-1'in `hdr_kural3.py` çıktısıyla birebir aynıdır (55 olay). Kuralın K olayları B,
     A ve R2 listelerinden hiçbir istasyon-pencere düşürmüyor. Tarihsiz D notları
     ("Has CalTech style electronics", "Scale factor is now …") "D dışarıda" bilgi satırında B listesinden 6
     istasyon-pencere düşürüyor (CRR1 1973, 1978, 2013, 2018; WKR1 2013, 2018). Sürüm 1 kuralı aynı metinde B
     listesinden 3 istasyon-penceresini (CRR1 2013 ve 2018, CWN1 2018) sahte son veren olayla düşürüyordu.
4. **Kayıt:** sonuç "Ek: HDR K/D olayları (koşu öncesi)" başlığıyla bu belgeye eklenir. Her olay için dosya, satır
   numarası, tarih, eşleşen sözcük ve tür yazılır; aday listesinden düşürdüğü istasyon-pencereler sayılır. Notlarda
   geçen kayma ya da hız ifadeleri kayda alınmaz ve kullanılmaz. Rapor ayrıca şu sayıyı yazar: K olayıyla düşen
   istasyon-pencerelerden kaçının notunda "creep" ya da "event" sözcüğü de geçiyor (tam sözcük, tekil ya da çoğul;
   "creepmeter" sayılmaz). Bu sayı, gerçek bir sünme olayını anlatan notun aygıt olayı sayılma sıklığını gösterir.
   Bilgi içindir; kuralı değiştirmez.
5. **Biçim uyumsuzluğu.** HDR biçimi bu kurala uymuyorsa yalnız not birimi (paragraf, satır ya da tablo satırı) ve
   tarih tanıma uyarlanabilir. Önek listeleri, tür kuralı ve tarihsiz not kuralı değişmez. Uyarlama yalnız ekler;
   tanınan hiçbir biçim çıkarılmaz. Uyarlanmış kural sırasıyla şu adımlardan geçer: (i) kod olarak commit edilir;
   (ii) README'nin "Comments specific to various creepmeters" bölümünde yeniden koşulur ve
   `onkayit_yardimci/inc1_hdr_kural_basvuru.txt`'teki (TR-10b_INCELEME-1 §D'nin başvuru çıktısı) K ve D olaylarını
   aynı tarihlerle yeniden üretir; (iii) ancak bundan sonra HDR dosyalarına uygulanır. Hangi pencerelerin düştüğü
   yalnız bu commit edilmiş kodun tek koşusuyla sayılır. Sayım görüldükten sonra kural değişmez.
6. Yanlış pozitifler (ör. "no offset", "calibration confirms") de K sayılır. Bu, sayıyı düşürür ve önceden kabul
   edilir (§16).

## 7. Sakinlik kuralları (ikisi de bağlayıcı)

Uzaklık istasyon noktasına büyük daire uzaklığıdır (`tr2_sayim.mesafe_az`, R = 6371 km). SJN1'in sayfadaki boylamı 0
olduğu için XSJ2'nin boylamı kullanılır. Büyüklük ComCat'in bildirdiği büyüklüktür (ML, Mw, Md karışık), derinlik
ComCat derinliğidir. Zaman sınırları kapalıdır; 29 Şubat'tan yıl kaydırmada 28 Şubat alınır. Pencere, herhangi bir
şartı ihlal eden tek bir olayla düşer.

**B (kırık boyuna ölçekli; ANA HÜKÜM SATIRI).**
- B1, geçmiş ve iç etki: M ≥ 4,5, derinlik ≤ 30 km, uzaklık ≤ max(10 km, 5 L(M)), zaman [w0 − 2 y, T].
  L(M) = 10^(0,62 M − 2,57) km (Wells ve Coppersmith 1994, doğrultu atımlı; `tr2_sayim.L_km`): M 5 → 17 km,
  M 6 → 70 km, M 6,9 → 230 km, M 7,3 → 450 km.
- B2, hedef olay öncesi dışlama: M ≥ 5,5, derinlik ≤ 30 km, ≤ 50 km, zaman (T, T + 2 y] (T + 1 g'den başlar).
- B3, uzak büyük olay: M ≥ 7,0, derinlik ≤ 70 km, ≤ 500 km, zaman [w0, T].

**A (sabit yarıçaplı; ZORUNLU İKİNCİ SATIR).**
- Ş1: M ≥ 5,0, derinlik ≤ 30 km, ≤ 50 km, zaman [w0 − 2 y, T + 2 y].
- Ş2: M ≥ 6,0, derinlik ≤ 40 km, ≤ 150 km, zaman [w0 − 5 y, T + 2 y].
- Ş3: M ≥ 7,0, derinlik ≤ 70 km, ≤ 500 km, zaman [w0 − 2 y, T].

**Yazılış sırası (dürüstlük kaydı):** A önce yazıldı ve sayıldı. B, **A'nın sayımı görüldükten sonra, ama hiçbir
sünme verisi görülmeden** yazıldı. Sayım yalnız pencere sayısını gösterdi; hiçbir Δv, hız ya da seri değeri
görülmedi. B'nin ana satır olması sayım sonucuna dayanır (A kapıyı U'da bile geçemiyor: 25 site / 31 site-pencere,
SAYIM §5.4). Bu seçim yalnız örneklem boyunu değil, hangi pencerelerin girdiğini de değiştirir. B, A'nın dışladığı üç
tür pencereyi içerir: (i) 5L(M) ile 50 km arasında M 5,0–5,7 olayı olanlar; (ii) 5L(M) ile 150 km arasında M 6,0–6,5
olayı olanlar; (iii) w0'dan 2–5 yıl önceki M ≥ 6 olayların ardıl-sismik dönemine düşenler. Örneğin B'nin 2013
epoğundaki Parkfield pencereleri 2003 San Simeon ve 2004 Parkfield'dan 4–10 yıl sonradır. B tabanı bu yüzden A
tabanından büyük olabilir; ardıl kaymanın sönümü ayrıca işaretli Δv'yi negatife çekebilir. Seçim hiçbir sünme verisi
görülmeden yapıldığı için bu bir veri yanlılığı değil, bir tanım farkıdır. A satırı ve "B1 geçmiş 5 y" bilgi satırı
(§11) farkı gösterir. İki satır da her durumda yazılır; hiçbiri elenmez.

## 8. Ölçü tanımı

### 8.1 Günlük katman (DAY ya da 10MIN; "tele")

- **Uç noktası değeri:** u(P) = [P − 15 g, P + 15 g] (31 takvim günü) içindeki geçerli günlük değerlerin
  `numpy.median`'ı. P ∈ {w0, H, T}. 10'dan az geçerli gün varsa pencere düşer.
- **Ana ölçü:** Δv = (u(T) − u(H)) / τ₂ − (u(H) − u(w0)) / τ₃, mm/yıl.
- **Pencere hızı:** v₅ = (u(T) − u(w0)) / (τ₂ + τ₃).
- **Oran:** r = Δv / v₅, yalnız v₅ ≥ 2,0 mm/yıl olan "sünen katmanda". Payda bu katmanın kendi v₅'idir; v₅ < 2,0
  olan pencereler r satırlarına girmez.
- **Doluluk:** taban [w0, H) ve yakın [H, T) dönemde ayrı ayrı (geçerli gün sayısı) / (dönemin takvim günü sayısı,
  §3 tablosu) ≥ 0,60.
- **Boşluk:** okuma aralığında [w0 − 15 g, T + 15 g] ardışık eksik günlerin en uzun koşusu ≤ 60 gün. Aralık
  başındaki ve sonundaki eksik günler de koşu sayılır.
- **Doğrusal dolgu tanısı (bilgi; ana satırı ve kapıyı değiştirmez).** Günlük katmanda en az 15 ardışık geçerli
  günlük bir koşu, kendi en küçük kareler doğrusuna göre en büyük mutlak artığı ≤ 0,6·δ ise "doğrusal dolgu"
  sayılır. δ, o dosyanın kayma sütununda görülen en küçük ondalık adımdır (ör. iki ondalıkta 0,01 mm). Bir uç
  penceresinin ([P − 15 g, P + 15 g]) bütün geçerli günleri böyle bir koşunun içindeyse yer-pencere "dolgulu"
  işaretlenir. Eğimi sıfır olan koşular ayrıca sayılır. Kural değerin yönüne ve büyüklüğüne bakmaz. Kapı adımı
  dolgulu yer-pencerelerin sayısını kaynak türüne ve epoğa göre yazar; değer yazmaz. §11 madde 9'da "dolgulu
  yer-pencereler dışarıda" bilgi satırı vardır. Dolgulu yer-pencerelerin payı %20'yi aşarsa ana hüküm cümlesine
  "(yer-pencerelerin %[..]'inde uç değeri doğrusal dolgudan; Δv sıfıra yanlı olabilir)" eklenir (§12).

### 8.2 Elle ölçüm katmanı (MIC; "man")

- u(P): P'den önceki (≤ P) son ölçüm günü ile sonraki (≥ P) ilk ölçüm gününün günlük değerleri arasında doğrusal ara
  değer. P'de ölçüm varsa o değer. İki ölçümün de P'ye uzaklığı ≤ 90 gün olmalıdır.
- Taban döneminde ≥ 12, yakın dönemde ≥ 8 ölçüm günü. [w0, T]'yi çevreleyen ölçümler dahil, ardışık ölçüm günleri
  arasındaki en uzun aralık ≤ 180 gün.
- Δv, v₅ ve r aynı formüllerle hesaplanır.

### 8.3 Kaynak sırası

Her istasyon-pencere için önce DAY, sonra 10MIN (günlük medyana indirgenmiş), sonra MIC denenir. §8.1 ya da §8.2'nin
bütün şartlarını sağlayan ilk kaynak kullanılır. Sıra veri görülmeden sabittir ve yalnız gün varlığına bakar, değere
bakmaz.

### 8.4 Bilgi satırı: menteşe modeli

Günlük katmanda [w0, T) günleri üzerinde ağırlıksız en küçük kareler: sabit + eğim·t + menteşe max(0, t − t_H) +
sin/cos(2πt) + sin/cos(4πt) + penceredeki her D olayı için 1{gün ≥ olay}. t = (gün − w0) / 365,25 yıl. Artıklarda
|e − medyan(e)| > 5 × 1,4826 × MAD olan günler bir kez atılır ve model yeniden uydurulur (MAD = 0 ise atılmaz). Δv_m,
menteşe katsayısıdır. Rank eksikliğinde pencere bu satırdan düşer. Basamaklı sünmede artıklar ağır kuyruklu olduğu
için bu ana ölçü değildir.

### 8.5 Yağış

Düzeltilmez. CDEC verisi indirilmez. Yağışla tetiklenen sünme olayları tabanın gerçek parçası sayılır.

## 9. Bağımsızlık birimi ve belirsizlik

### 9.1 Yer (site)

- Yer, sayfadaki koordinatları 3 ondalığa yuvarlandığında aynı olan istasyonlardır (34 yer; 13 eş konumlu ölçer).
  Ana birim **yer-penceredir**.
- Bir yer ve epokta birden çok istasyon §6 ve §8 şartlarını sağlıyorsa tek temsilci alınır: (1) önce telemetri
  (DAY/10MIN) katmanı; (2) sonra sayfadaki en erken ilk gözlem; (3) eşitlikte kod sırası. Seçim yalnız gün varlığına
  ve üstveriye bakar, değere bakmaz.
- Temsilci her kural seti için ayrı seçilir; adaylar o setin listesinden gelir.

### 9.2 Fay kesimi (blok)

Calaveras-Hollister; Hayward; SAF San Juan Bautista–Cienega (≥ 36,70° K); SAF orta sünen (36,00–36,70); SAF Parkfield
(35,70–36,00); SAF güney geçiş (< 35,70). En çok 6 blok (`tr10b_sayim.kesim`).

### 9.3 Güven aralıkları

- **Ana: fay kesimi bloklu bootstrap.** Analizdeki K blok (en az bir yer-penceresi olan kesimler) iadeli olarak K kez
  çekilir. Seçilen blokların bütün yer-pencereleri tekrarlarıyla havuzlanır. Her nicelik bu havuzdan yeniden
  hesaplanır. B = 2000 yineleme, üreteç `numpy.random.default_rng(20261112)`. Çekiliş dizisi (B, K) biçimindedir;
  bloklar ad sırasındadır. Aralık, 2000 değerin %5 ve %95 nicelikleridir (yüzdelik yöntem, çift yanlı, nominal %90).
- **Blok sayısı şartı.** Bloklu aralık ve b* etiketi yalnız K ≥ 4 blokta verilir. K ≤ 3 ise ana satır "blok
  yetersiz (K = [K])" yazar. Nokta değerler ve yer bootstrap'ının aralığı bilgi olarak verilir, etiket konmaz.
  Chihshang satırı da aynı kurala uyar. (Bloklu aralığa dayanan öteki okumalar, yani README modeli satırının ρ_R
  okuması ve κ okuması da K ≤ 3'te yapılmaz; yalnız nokta değerleri yazılır.)
- **Kapsama notu.** 5–6 blokla yüzdelik bloklu aralık nominal %90'dan dardır. TR-10b_INCELEME-1 Ö1'in yapay
  denetiminde gerçek q95, üst sınırın üstünde %14–26 (K = 5–6), alt sınırın altında %0–3 sıklıkla kaldı. Aralık
  her yerde "nominal %90" diye yazılır.
- Bir yinelemede bir nicelik tanımsızsa (ör. sünen katmanda hiç pencere yoksa) o yineleme o nicelikten düşer ve düşen
  yineleme sayısı yazılır. Bir nicelik yinelemelerin %10'undan fazlasında tanımsızsa o niceliğin aralığı verilmez,
  "güç yok" yazılır.
- Her satır ve her bootstrap (ana, A, katmanlar, bilgi satırları) **yeni** bir `default_rng(20261112)` ile başlar.
- **Bilgi: yer bootstrap'ı.** Aynı yöntem, blok yerine yer; aynı tohum.
- Bütün nicelikler `numpy.quantile(..., method="linear")` ile alınır.

## 10. Hüküm sırası

Sıra şöyledir: **veri kapısı → kod denetimi yapay veriyle → pozitif kontrol gerçek veride → ölçü.** Gerçek Δv
havuzu yalnız ilk üç adım geçtikten sonra hesaplanır ve dosyaya yazılır. Kapı geçmese de 2. ve 3. adım koşar
(§10.1).

### 10.1 Veri kapısı

- §5, §6 (HDR eki dahil), §8 ve §9.1'den sonra kural seti B'de geçerli yer ve yer-pencere sayılır. Bu adım hiçbir
  Δv yazdırmaz; yalnız sayıları, düşme nedenlerini (kapsam yok, doluluk, boşluk, uç değeri, K, HDR, indirilemedi,
  biçim belirsiz), blok sayısını K ve dolgulu yer-pencere sayılarını (§8.1) yazar.
- **Kapı:** yer ≥ 20 **ve** yer-pencere ≥ 40.
- **Yer kümesi (bilgi).** Kapı adımı ayrıca, birbirine ≤ 3 km olan yerleri tek bağlantılı kümeleyerek "yer kümesi"
  sayısını bilgi olarak yazar. Kapı yer sayısıyla uygulanır. Küme sayısı 20'nin altındaysa ana hüküm cümlesine
  "(≤ 3 km'de kümelenince [..] yer kümesi)" eklenir (§12). Veri öncesi üst sınır: B listesinin 29 yeri 9 yakın çiftle
  21 kümeye iner (`inc1_tr10_ortusme.py`, §19).
- **Kapı geçmezse:** ana hüküm **"veri yok"** olur. 2. ve 3. adım yine koşar. Geçerlerse dağılım yine hesaplanır ve
  bütün çıktı satırlarıyla, güven aralığıyla ve her satırda **"kapı altı"** etiketiyle bir **bilgi satırı** olarak
  yazılır (eleme yok kuralı). Bu bilgi satırına etiket (§10.4) yazılmaz; ρ_R ve κ değerleri aralıklarıyla yazılır,
  okumaları yazılmaz. Chihshang satırı (§10.5) da yazılmaz.
- A için aynı kapı ayrı sayılır. A satırı her durumda yazılır; kapı geçmezse "kapı altı" etiketini taşır. Ana hüküm
  A'dan hiçbir durumda türetilmez.
- İstasyon düzeyi sayılar (istasyon ≥ 20, istasyon-pencere ≥ 40) bilgi satırıdır.

### 10.2 Kod denetimi, yapay veriyle (gerçek Δv görülmeden)

Denetim kümesi, B'deki (A ⊂ B) bütün geçerli yer-pencerelerdir; n bu kümenin boyudur. Her yer-pencerenin **gerçek gün
maskesi** (günlük katmanda geçerli günler, elle katmanda ölçüm günleri) kullanılır; değerleri kullanılmaz.

- **(a) Gürültüsüz doğruluk.**
  - Günlük katman: x(t) = 3 + 7t + 4·max(0, t − t_H) + 2 sin(2πt + 1) + 0,7 cos(4πt) + 3·1{gün ≥ H − 200 g}. Gerçek
    değer Δv₀ = 4 − 3/τ₃.
    - Tam maskede (mevsimli ve mevsimsiz): |Δv − Δv₀| ≤ 0,005 mm/yıl.
    - Gerçek maskelerde: |Δv − Δv₀|'nin en büyüğü ≤ 0,50 mm/yıl (yer-pencere başına bir seri). (Uç penceresinde
      ≥ 10 gün şartıyla doğru kod bu sınırı aşamaz: kullanılan epoklarda herhangi bir maskede erişilebilen en büyük
      hata 0,462–0,479 mm/yıl'dır; TR-10b_INCELEME-1 K2.)
  - Elle katman: x(t) = 3 + 7t ölçüm günlerinde: |Δv| ≤ 10⁻⁶ mm/yıl.
  - (a3) Medyan denetimi: x = 3 mm sabit; yalnız T gününde x = 503 mm (tam maske, günlük katman, dosya yolundan).
    |Δv| ≤ 10⁻⁶ mm/yıl olmalıdır. (u'yu ortalamayla alan bir kod epoğa göre ≈ 8,06–8,07 mm/yıl verir.)
  - (a4) Gün kayması denetimi (tam maske, günlük katman, dosya yolundan): x = 10·1{gün ≥ H} için Δv = −10/τ₃;
    x = 10·1{gün ≥ H + 1 g} için Δv = +10/τ₂. İkisinde de |hata| ≤ 10⁻⁶ mm/yıl olmalıdır. Bir günlük kayma bu iki
    değerden birini öbürüne çevirir.
- **(b) Uçtan uca ölçek.**
  - Yapay seri: rastgele yürüyüş b = 3 mm/yıl^0,5 + beyaz gürültü 0,1 mm, günlük tam ızgarada üretilir, gerçek maske
    uygulanır. Seri o yer-pencerenin kaynak türünün dosya biçiminde (DAY/MIC: günde bir satır; 10MIN: günde bir
    satır, öğlen) gzip'li metin olarak yazılır ve koşu kodunun bütün yolundan (okuma, biçim denetimi, günlük medyan,
    doluluk, uç değeri, Δv) geçer.
  - En az bir 10MIN yer-penceresinde yapay seri ayrıca günde 144 satırla (10 dakikada bir, aynı günlük değere ±0,01 mm
    beyaz gürültü eklenmiş) yazılır. Günlük medyana indirgemenin sonucu, günde bir satırlık yazımın sonucuyla
    |fark| ≤ 0,005 mm/yıl içinde eşleşmelidir. (Yapay doğrulama: 300 seride en büyük fark 0,0030 mm/yıl; §19.)
  - Yer-pencere başına R = ⌈820 / n⌉ gerçekleşme üretilir. j'inci gerçekleşmenin tohumu
    `int(sha256(f"{KOD}|{Y}|{j}").hexdigest()[:16], 16) ^ 20261112`'dir.
  - Pay: n·R değerin |Δv| havuzunun %95 niceliği.
  - **Payda:** her yer-pencere için aynı gerçek maskeyle M = 2000 çekiliş. Seri bellekte üretilir, dosyaya yazılmaz
    ve ölçü işlevi doğrudan çağrılır. Üreteç `default_rng(20261112 + 1)`; yer-pencereler kanonik sırayla. Payda, n·2000
    |Δv| değerinin %95 niceliğidir.
  - Oran pay / payda ∈ [0,88, 1,12] değilse hüküm "geçersiz (kod)".
  - Bilgi: aynı pay, tam maskeli 20 000 çekilişlik paydaya bölünür (SAYIM'ın tanımı).
- **(c-yapay) Pozitif kontrol.** Her yer-pencerenin ilk yapay gerçekleşmesine (j = 0) ρ(t) = 5 mm/yıl ·
  max(0, t − t_H) eklenir (ekleme kuralı §10.3'teki gibidir). d = Δv_eklenen − Δv_özgün, aynı koşu yolundan. Geçme
  şartları §10.3 ile aynıdır.
- **Başarısızlık:** kod, gerçek Δv görülmeden düzeltilir ve "koşu öncesi düzeltme" başlığıyla kayda geçer. 2. adım
  yeniden koşar. En çok iki düzeltme turu yapılır; üçüncü başarısızlıkta hüküm kesin olarak "geçersiz (kod)" olur.

#### 10.2.1 Eşiklerin yapay doğrulaması (bu belge için koşuldu)

Hesaplar `tr10b_sayim.py`'nin `pl_seri`, `dv_uc`, `gunler` işlevleriyle yapıldı. Tohumlar: SAYIM 20261113; bu
belgede 777 ve 4242. "Gerçekçi maske": doluluk hedefi U[0,6, 1], 1–60 günlük delikler, §8.1 şartlarını sağlayana dek
yeniden üretilir. "En kötü maske": her uç penceresinde yalnız 10 gün ve hepsi tek yanda.

| Denetim | Yapay sonuç | Eşik |
|---|---|---|
| (a) tam maske, mevsimsiz / mevsimli (SAYIM) | hata 0 / 0,00045 mm/yıl | ≤ 0,005 |
| (a) %10 eksik, 1–20 g delik, 495 seri (SAYIM) | %99: 0,22; en çok 0,27 | en büyük ≤ 0,50 |
| (a) gerçekçi maske, 500 seri | %99: 0,20; en çok 0,24 | en büyük ≤ 0,50 |
| (a) en kötü maske, 500 seri | %99 ve en çok: 0,48 | en büyük ≤ 0,50 |
| (a) herhangi bir ≥ 10 günlük uç maskesiyle erişilebilen en büyük hata (analitik üst sınır; İNCELEME-1 K2) | 0,462–0,479 (epoğa göre) | en büyük ≤ 0,50 (doğru kod aşamaz) |
| (a3) medyan denetimi, tam maske | medyanla 0; ortalamayla 8,06–8,07 | ≤ 10⁻⁶ |
| (a4) gün kayması denetimi, tam maske | hata 0 (−10/τ₃ ve +10/τ₂ tam) | ≤ 10⁻⁶ |
| (b) N = 820, 100 tekrar (SAYIM; payda tam maske) | ortalama 1,002, sd 0,033, aralık [0,923, 1,080] | [0,88, 1,12] (±3,6 sd) |
| (b) maske etkisi: q95 gerçekçi / tam, en kötü / tam (20 000'er) | 1,007 / 1,013 | payda aynı maskeyle alındığı için etkisiz (F6) |
| (c) 5 mm/yıl rampa, RW b = 3 + beyaz 0,1, tam maske, 2000 seri (SAYIM) | medyan(d) 4,963; %0,5–%99,5 [4,83, 5,07] | – |

Pozitif kontrolün gürültü rejimine duyarlılığı (2013 epoğu, rejim başına 400 seri; "20'li medyan", 20 pencerelik
rastgele alt örneklerin medyanının %0,1–%99,9 aralığıdır):

| Rejim | Tam maske: medyan(d); 20'li medyan | Gerçekçi maske: medyan(d); 20'li medyan | En kötü maske: 20'li medyan |
|---|---|---|---|
| RW b = 3 + beyaz 0,1 mm | 4,968; [4,934, 5,006] | 4,970; [4,932, 5,004] | [4,857, 5,060] |
| RW b = 3 + 3 mm yıllık döngü | 4,981; [4,947, 5,005] | 4,981; [4,944, 5,003] | [4,834, 5,023] |
| Düz, 0,01 mm nicemli | 4,997; [4,992, 5,000] | 4,995; [4,992, 5,000] | [4,867, 5,072] |
| Doğrusal 10 mm/yıl + beyaz 0,02 | 5,000; [4,993, 5,000] | 5,000; [4,992, 5,000] | [4,811, 5,011] |
| Basamaklı (yılda 4 olay, ort. 1 mm) + 2 mm/yıl | 4,993; [4,987, 4,999] | 4,992; [4,981, 5,000] | [4,821, 5,066] |
| Beyaz 1 mm (yağış eğilmesi benzeri) | 4,955; [4,903, 5,000] | 4,956; [4,906, 4,999] | [4,828, 5,013] |

**Deterministik sınır (günlük katman).** 0 ≤ ρ ≤ 5·15/365,25 = 0,205 mm olduğundan, H penceresinde medyan kayması
[0, 0,205] mm, T penceresinde [5τ₂ − 0,205, 5τ₂ + 0,205] mm aralığındadır. Bu yüzden her pencere için, verinin ne
olduğundan bağımsız olarak, d ∈ [5 − 0,410/τ₂ − 0,205/τ₃, 5 + 0,205/τ₂] = [4,726, 5,103] mm/yıl (epoklar arasında
farkı < 0,001). Bu aralığın dışındaki bir d yalnız kod hatasıyla oluşabilir.

**Elle katman: analitik değer.** Doğrusal ara değer doğrusal olduğu için d veriye bağlı değildir:
d_analitik = 5 − ρ̂_H (1/τ₂ + 1/τ₃). Burada ρ̂_H = 5·(t_b − H)(H − t_a) / ((t_b − t_a)·365,25) mm; t_a ≤ H ≤ t_b
H'yi çevreleyen ölçüm günleridir (H'de ölçüm varsa ρ̂_H = 0). T ve w0 uçlarında ara değer kesindir. Aralık
d ∈ [4,49, 5,00].

### 10.3 Pozitif kontrol, gerçek veride (yalnız d yazılır)

- **Seçim:** B'deki geçerli yer-pencereler, temsilci istasyon koduyla `f"{KOD}|{Y}"` dizgesinin UTF-8 SHA-256
  onaltılık değerine göre artan sıralanır; ilk ⌊n/2⌋ yer-pencere seçilir.
- Seçilenlerin gerçek serilerine ρ(t) = 5 mm/yıl · max(0, t − t_H) eklenir. d = Δv_eklenen − Δv_özgün hesaplanır.
  Kaynak, maske ve uç kuralları özgün serideki gibidir; sinyal ekleme maskeyi değiştirmez. ρ, günlük değere eklenir.
  10MIN'de değer önce günlük medyana indirgenir, sonra ρ eklenir. ρ gün tarihinde, t = (gün − w0)/365,25 ile
  hesaplanır. (ρ 10 dakikalık satırlara eklenirse uçtaki günün ρ'su 0,219 mm'ye çıkar ve deterministik alt sınır
  4,708'e iner; şart 1'in 4,72'si bu durumda doğru kodu düşürebilir.)
- **Geçme şartları (üçü birden):**
  1. telemetri katmanında her seçili pencere için 4,72 ≤ d ≤ 5,11 (deterministik sınır, dışa yuvarlanmış);
  2. telemetri katmanında medyan(d) ∈ [4,85, 5,03];
  3. elle katmanda her seçili pencere için |d − d_analitik| ≤ 10⁻⁶ mm/yıl.
- Telemetri katmanında seçili pencere yoksa şart 1 ve 2 boş geçer; elle katmanda yoksa şart 3 boş geçer. İkisi de
  boşsa (n < 2) denetim yapılamaz ve hüküm zaten "veri yok"tur.
- **Eşiklerin gerekçesi:** SAYIM'ın alt eşiği 4,90 idi. Gerçekçi maskelerde beyaz gürültüsü baskın bir pencere
  kümesi 20'li medyanı 4,903'e dek indirebiliyor, en kötü maskeler ise 4,81'e. Alt eşik bu yüzden 4,85'e
  indirildi (F5). Doğru kodun gerçekçi koşullarda bu aralıkta kalacağı yukarıdaki tabloda görülüyor; kaba hataları
  (işaret, menteşe yeri, τ birimi, uç penceresi kayması) şart 1 ve 3 kesin olarak yakalar.
- **Geçmezse:** hüküm "geçersiz (kod)". Bu adım Δv_özgün'ü hiçbir dosyaya, log satırına ya da istisna iletisine
  yazmaz; yalnız seçili sayıyı, katman başına medyan(d), en küçük ve en büyük d'yi ve şart 3'ün en büyük sapmasını
  yazar. Kod bu yüzden körlük bozulmadan §10.2'deki düzeltme kuralıyla düzeltilebilir (iki tur sınırı ortaktır).

### 10.4 Ana ölçü ve etiket (yalnız kapı geçtiyse ve K ≥ 4 ise etiket konur)

- **Ana satır (B):** |Δv| için q50, q95, q99 mm/yıl, her biri bloklu bootstrap aralığıyla [L, U] (nominal %90).
- **Eşdeğer rastgele yürüyüş genliği:** b* = q95 / c₁, c₁ = 1,78. c₁, b = 1 mm/yıl^0,5 saf rastgele yürüyüşte, tam
  maskede q95|Δv|'dir (100 000 çekiliş: 2003 ızgarası 1,7805, 2013 ızgarası 1,7748) (MC hatası ±0,005; 1978, 2003,
  2013 ızgaraları 1,775–1,781 arasında; bütün epoklarda aynı sabit kullanılır). SAYIM'daki 1,732 değeri 4000
  çekilişlik bir MC'dir (F7). Aralık uçları da aynı sabitle çevrilir: b*_L = L / c₁, b*_U = U / c₁.
- **Etiket (b* ile; yalnız kapı geçtiyse ve K ≥ 4 ise, §9.3):**
  - b*_L > 4,6 ise "taban, README'nin n = 2 istasyonlarının genlik aralığından büyük";
  - b*_U < 2,2 ise "taban, README'nin n = 2 istasyonlarının genlik aralığından küçük";
  - öteki durumlarda "taban, README'nin n = 2 istasyonlarının genlik aralığında".
  - Aralık [2,2, 4,6], README gürültü tablosunda indisi n = 2,00 olan altı istasyonun (XMM1, XVA1, XPK1, CRR1,
    CWC3, XMR1) rastgele yürüyüş genliğidir. Bu aralık README modelinin tamamı **değildir**. Tablodaki 18
    istasyonun 12'sinde n > 2'dir ve uç ölçüsünde bunların q95|Δv|'si 3,6–33 mm/yıl'dır.
- **README modeli satırı (ana satırın parçası; etiket değildir).** ρ_R = q95_ölçülen,R / q95_N0,R.
  - Alt küme R: temsilci istasyonunun kodu README tablosundaki 18 koddan biriyle birebir aynı olan B yer-pencereleri.
    Ardıl kodlar (XPK2, XSJ3, XHR3) öncülünün parametrelerini almaz.
  - q95_N0,R: §11 madde 9'da tanımlanan README N0 çekilişlerinin R üzerindeki birleşiminin %95 niceliği.
  - Aralık: aynı bloklu bootstrap yinelemelerinde hesaplanır. Pay ve payda aynı yer-pencerelerden (tekrarlarıyla)
    alınır.
  - Okuma: ρ_R,U < 1 ise "README modelinin öngördüğünden küçük"; ρ_R,L > 1 ise "README modelinin öngördüğünden
    büyük"; öteki durumlarda "README modeliyle uyumlu".
  - R'de 20'den az yer-pencere varsa satır "güç yok" yazar ve nokta değeri verir. (Veri öncesi üst sınır: B
    listesinde R'ye girebilecek 24 yer-pencere var, hepsi B_R2'de de bulunuyor; 21'i T ≥ 2008'dedir. Gerçek R büyük
    olasılıkla bundan küçüktür.)
- **Önceden hesaplanan beklenti** (TR-10b_INCELEME-1 E2; tam maske, 2013 ızgarası; `inc1_readme_n0.py` ile yeniden
  üretildi, §19). B listesinde README tablosunda kodu bulunan 24 istasyon-pencere için README modeli q95|Δv| ≈ 18,0
  mm/yıl (b* ≈ 10,1, κ ≈ 8) öngörür. Veriler README modeline tam uysa bile b* etiketi büyük olasılıkla "aralığından
  büyük" çıkar (§10.4.1: b = 9'da %93–100). Bu etiket bir model uyumu hükmü olarak okunmaz; README ile karşılaştırma
  ρ_R satırıdır.
- **Kuyruk ölçüsü:** κ = q95|Δv| / q50|Δv|, bloklu aralığıyla. Başvuru değerleri: tek ölçekli Gauss (saf rastgele
  yürüyüş, uç ölçüsüyle) 2,91 (Gauss, analitik: 1,960 / 0,674); README tablosunun 18 istasyonluk N0 havuzu 6,1
  (SAYIM §4.2: 14,6 / 2,4); README modelinde B listesinin karışımı ≈ 8 (yukarıdaki beklenti). Okuma kuralı:
  κ_L > 2,91 ise "kuyruk tek ölçekli Gauss'tan ağır (ölçek karışımı ya da basamaklı sünme)". Bu bir bilgi satırıdır;
  etiketi değiştirmez. q99 / q95 de yazılır.

#### 10.4.1 Etiketin yapay davranışı (bu belge için koşuldu; tohum 4242)

Yer-pencereler bağımsız, |Δv| tek ölçekli Gauss; 200 tekrar, B = 1000. "B_R2 yapısı" kesim boyları (21, 10, 4, 4, 2),
"B_U yapısı" (21, 19, 8, 6, 4, 4).

| Gerçek b | B_R2: büyük / aralıkta / küçük | b*_L, b*_U medyanı | B_U: büyük / aralıkta / küçük |
|---|---|---|---|
| 1,5 | 0 / 0,075 / 0,925 | 1,10, 1,67 | 0 / 0,015 / 0,985 |
| 3,0 | 0 / 0,995 / 0,005 | 2,14, 3,27 | 0 / 0,995 / 0,005 |
| 6,0 | 0,39 / 0,61 / 0 | 4,42, 6,63 | 0,585 / 0,415 / 0 |
| 9,0 | 0,93 / 0,07 / 0 | 6,48, 9,82 | 1 / 0 / 0 |

Okuma: N ≈ 40'ta q95 kestiricisi aşağı yanlıdır (b = 3'te aralık medyanları [2,14, 3,27]). Kesimler arası gerçek
farklar bloklu aralığı bu tablodakinden genişletir. "Aralığından büyük" etiketi ancak b ≳ 6'da olasıdır; README
modeli B karışımı için b* ≈ 10 öngördüğünden (§10.4) bu etiket README modeline uyan veride de beklenir.
Aralık [2,2, 4,6] içindeki gerçek değerlerde yanlış etiket olasılığı küçüktür (İNCELEME-1 Ö1: b = 2,5'te yanlış "küçük" K = 5 için
%5–7, K = 6 için %1–3; b = 4,0'da yanlış "büyük" ≤ %0,7), ama aralığın kapsaması nominalden düşüktür (§9.3).

### 10.5 Chihshang 2003 bilgi satırı (yalnız kapı geçtiyse; K ≤ 3'te §9.3'teki blok sayısı şartı)

- İddia: Lee vd. 2005 (10.1016/j.crte.2005.04.018). 2003 Chengkung Mw 6,6–6,8 öncesinde 1990–1997 ortalaması
  22 mm/yıl, 2000–2003 ortalaması 14 mm/yıl: Δv_c = −8 mm/yıl. Bu ön kaydın r tanımıyla (payda pencere ortalama
  hızı, taban 3 y ve yakın dönem 2 y ağırlıklı) r_c = −8 / ((3·22 + 2·14)/5) = −8 / 18,8 = −0,43. (−8/22 = −0,36
  tabana bölünmüş orandır ve r ile aynı tanım değildir.) Bindirme fayı; dönemler farklı aletlerle (yüzey ölçümü ve
  sünme ölçeri) ve farklı uzunluklarda (7 y ve 3–4 y) ölçülmüş.
- **Birincil:** P_r = (sünen katmanda |r| ≥ 0,43 olan yer-pencere sayısı) / (sünen katmandaki yer-pencere sayısı).
- **İkincil:** P_v = (|Δv| ≥ 8,0 mm/yıl olan yer-pencere sayısı) / (B'deki geçerli yer-pencere sayısı).
- Aralık bloklu bootstrap'la, aynı yinelemelerle.
- Okuma: üst sınır < 0,05 ise "tabanın üstünde"; alt sınır > 0,05 ise "tabanın içinde"; ötekilerde "sınırda".
- Bu satır bir öncül sınaması değildir. Tek bir iddianın, farklı mekanizmalı bir fayda ve farklı alet dönemiyle,
  bu tabanın neresine düştüğünü gösterir.

## 11. Çıktı satırları

Her satırda: yer S, yer-pencere N, kesim K, katman ve kural seti. Kapı altındaki her satır "kapı altı" etiketini
taşır. N < 20 olan katman satırları "güç yok" yazar, nokta değerleri verir, aralık vermez.

1. **Ana (B):** q50, q95, q99 |Δv| mm/yıl [L, U]; b* [b*_L, b*_U]; b* etiketi; README modeli satırı: N_R,
   q95_N0,R, ρ_R [L, U] ve okuması (§10.4).
2. **Sünen katman (B, v₅ ≥ 2):** q50, q95, q99 |r| (hızın %'si olarak) [L, U]; katmandaki N.
3. **İşaretli Δv:** medyan ve hızlanan/yavaşlayan pay (simetri).
4. **Kuyruk:** κ = q95/q50 [L, U]; q99/q95.
5. **A satırı:** 1–4'ün aynısı, A için.
6. **Kesim dökümü (B):** her kesim için N, q50, q95 |Δv| ve q95 |r|; aralık yer bootstrap'ıyla (kesim içinde
   blok yok).
7. **Epok dökümü (B):** her epok için N, q50 ve q95 |Δv|, işaretli Δv medyanı ve hızlanan/yavaşlayan pay; bloklu
   aralık.
8. **Katman dökümü (B):** telemetri / elle; kaynak türü (DAY, 10MIN, MIC).
9. **Bilgi satırları (B):**
   - Parkfield dışı;
   - yalnız T ≥ 2008 (README tablosu 2004 öncesi veriden kestirildi; döngüsellik denetimi);
   - D olayları dışarıda;
   - yalnız telemetri;
   - SAYIM'ın R2 aday alt kümesi (§4'teki sha256'larla);
   - yer bootstrap'ı aralıkları;
   - menteşe modeli Δv_m (§8.4) q50, q95;
   - HDR olayları uygulanmadan (yalnız §6.1–6.3 listeleri): q50, q95 |Δv| [L, U]. HDR'nin düşürdüğü pencereler
     sakin pencerelerdir; okunmaları TR-10 körlüğünü bozmaz;
   - **B1 geçmiş 5 y:** B1'in zaman aralığı [w0 − 5 y, T]; B2 ve B3 aynı. Aday alt kümesi önceden sayıldı (U kapsamı,
     `tr10b_sayim.degerlendir(kapsam_sen="U", kurallar={"B1": dict(B1, once=5), "B2": B2, "B3": B3})`): 52
     istasyon-pencere, 39 yer-pencere, 25 yer, 6 kesim; 2013 epoğunun yer-pencereleri 20'den 4'e, Parkfield'ınkiler
     21'den 11'e iner. Kanonik sha256
     `33b8eafab4782c417c70f55a1606aecdf4fb1466e2c96817a53f2ef453d20b52`. Koşu bu alt kümeyi B listesinin içinden
     bu sha256'yla seçer; sakinliği yeniden hesaplamaz;
   - dolgulu yer-pencereler dışarıda (§8.1);
   - XDL2 dışarıda (README durumu: "doesn't measure creep");
   - README N0 beklentisi: temsilcisi README tablosundaki 18 istasyondan biri olan yer-pencereler (§10.4'teki alt
     küme R) için, tablodaki (n, A) ile güç yasası gürültüsü, gerçek maskeyle yer-pencere başına 2000 çekiliş,
     üreteç `default_rng(20261112 + 3)`, yer-pencereler kanonik sırayla. Bu çekilişler §10.4'teki ρ_R'nin paydası
     q95_N0,R'yi verir; ρ_R ana satırdadır. Eşleşme yalnız kodun birebir aynı olmasıyla yapılır; ardıl kodlar (XPK2,
     XSJ3, XHR3) öncülün parametrelerini almaz. Güç yasası serisi okuma aralığının başında sıfırdan başlar
     (`pl_seri`). n > 2'de sonuç başlangıç seçimine bağlıdır; bu yazılır. Aynı oran yalnız T ≥ 2008 alt kümesi için
     de yazılır, çünkü README tablosu 2004 öncesi veriden kestirildi.
10. **Chihshang satırı** (§10.5).
11. **Denetim satırları:** kapı sayıları ve düşme nedenleri; blok sayısı K; yer kümesi sayısı (§10.1); dolgulu
    yer-pencere sayıları (§8.1); (a), (a3), (a4), (b), 144 satırlık 10MIN denetimi, (c-yapay), (c-gerçek) sonuçları;
    düzeltme turu sayısı; okuma sayaçları (bozuk, başlık, aralık dışı atlanan satır, aralık dışı bozuk); biçim
    belirsiz dosyalar; HDR adımının "creep/event" sayacı (§6.4 madde 4); manifest denetimi.

## 12. Hüküm cümlelerinin kalıpları

Yalnız aşağıdaki kalıplar kullanılır; köşeli parantezler sayılarla doldurulur.

- **Kapı geçti (K ≥ 4):** "TR-10b: [taban, README'nin n = 2 istasyonlarının genlik aralığından büyük | aralığında |
  aralığından küçük]; README modeline göre [küçük | uyumlu | büyük] (ρ_R = [..] [L, U], yer-pencere [N_R]). Kural seti
  B: Orta Kaliforniya sünme ölçerlerinde sakin 5 yıllık pencerelerde 2 yıllık sünme hızı değişimi |Δv|,
  yer-pencerelerin yarısında [q50] mm/yıl'ı, %5'inde [q95] [L, U] mm/yıl'ı aşar (sünen katmanda hızın %[r50]'sini ve
  %[r95] [L, U]'sunu); yer [S], yer-pencere [N], kesim [K]; aralık fay kesimi bloklu bootstrap, yüzdelik, nominal %90
  (5–6 blokla gerçek kapsama daha düşük). Kural seti A: q95 [..] [L, U] mm/yıl (yer [..], yer-pencere [..]; kapı
  [geçer | altı])." README modeli satırında N_R < 20 ise parantez "(ρ_R = [..], yer-pencere [N_R]; güç yok)" olur.
- **Kapı geçti, blok yetersiz (K ≤ 3):** "TR-10b: blok yetersiz (K = [K]); etiket yok. Kural seti B: |Δv| q50 [..],
  q95 [..] mm/yıl (yer bootstrap'ı aralığı [L, U], bilgi; sünen katmanda hızın %[..]'si); README modeline göre
  ρ_R = [..] (nokta değer); yer [S], yer-pencere [N]. Kural seti A: q95 [..] mm/yıl (yer [..], yer-pencere [..];
  kapı [geçer | altı])."
- **Ek kuyruklar** (yalnız şartı sağlanırsa, ana hüküm cümlesinin sonuna, bu sırayla): "(yer-pencerelerin %[..]'inde
  uç değeri doğrusal dolgudan; Δv sıfıra yanlı olabilir)" (§8.1, pay > %20); "(≤ 3 km'de kümelenince [..] yer
  kümesi)" (§10.1, küme < 20).
- **Kapı geçmedi:** "TR-10b: veri yok (kural seti B: yer [S] / yer-pencere [N]; kapı ≥ 20 / ≥ 40). Bilgi satırı,
  kapı altı: |Δv| q50 [..], q95 [..] [L, U] mm/yıl (sünen katmanda hızın %[..]'si [L, U]); bu satır bir hüküm
  değildir."
- **Kod:** "TR-10b: geçersiz (kod) ([hangi denetim], [değer] / [eşik]); gerçek Δv hesaplanmadı."
- **Yanlış alarm ölçeği cümlesi** (yalnız kapı geçtiyse ve K ≥ 4 ise): "Orta Kaliforniya sünme ölçerlerinde, önceden
  tanımlı sakinlik kuralı B'yi geçen 5 yıllık pencerelerde 2 yıllık sünme hızı değişimi %5 sıklıkla [q95] mm/yıl'ı
  (sünen ölçerlerde hızın %[r95]'ini) aşar. Bloklu üst sınır [U] mm/yıl'dır (nominal %90). Yer-pencerelerin
  %[p_PKF]'i Parkfield'da, %[p_0818]'i 2008–2018 epoklarındadır. Sakin pencere seçimi ve küçük örneklem bu değeri
  aşağı çeker. Bu yüzden [q95], koşulsuz yanlış alarm eşiğinin alt kestirimidir. [U] mm/yıl'dan küçük bir değişim bu
  tür bir ölçerde tek başına olağandışı sayılmaz. Daha büyük bir değişimin olağandışı olduğu ise bu ölçümden çıkmaz."
- **Chihshang cümlesi** (yalnız kapı geçtiyse ve K ≥ 4 ise): "Bilgi: Chihshang 2003 iddiası (−8 mm/yıl, r = −0,43;
  bindirme fayı, farklı alet dönemleri) bu sakin tabanda |r| ölçüsüyle [tabanın üstünde | içinde | sınırda] (P_r =
  [..] [L, U]). Taban sakin pencerelerden ve küçük örneklemle kestirildiği için 'üstünde' okuması koşulsuz tabana
  genellenemez. Pencere uzunluğu farkı ters yönde, 'içinde' yönüne iter."
- **Yasak:** mutlak İstanbul ya da Marmara deprem olasılığı, olasılık çarpanı, "Marmara'da alarm eşiği X'tir",
  "öncül bulundu", "öncül yok" cümleleri.

## 13. Önceden beyan edilen beklenti (yazarın beyanı)

- **Kapı:** gerçek veriyle "veri yok" olasılığı **0,65**. Gerekçe: U'nun R2'ye eklediği adayların çoğunun verisi
  yok (§4); gerçekçi tavan R2'nin 41 yer-penceresi. Doluluk, ≤ 60 g boşluk, uç şartı ve HDR olayları bundan en az
  ikisini düşürmeye yeter.
- **Kapı geçerse b* etiketi:** aralıktan büyük 0,55; aralıkta 0,40; küçük 0,05. Gerekçe: README modeli, B
  listesinin README'de bulunan istasyon karışımı için b* ≈ 10 öngörür (INCELEME-1 E2). Sakin pencere seçimi ve
  küçük örneklem değeri aşağı çeker. Bloklu aralığın genişliği "aralıkta" yönüne iter.
- **README modeli satırı:** küçük 0,50; uyumlu 0,40; büyük 0,10. README'nin n > 2,5 istasyonlarının (XSH1, XMD1,
  X461, XTA1) genlikleri büyük olasılıkla geçici olayları da taşıyor; sakin pencere seçimi bunları dışarıda bırakır.
- **Büyüklük:** b ≈ 3 ise q95|Δv| ≈ 5,3 mm/yıl. README modeli bu karışım için ≈ 18 mm/yıl öngörür. Önsel beklenti
  ikisinin arasıdır. Sünen istasyonların hızı 7–21 mm/yıl olduğundan 5,3 mm/yıl hızın %25–75'i demektir.
- **Chihshang:** |r| ölçüsüyle (r_c = −0,43) büyük olasılıkla "tabanın içinde". Bu önceden kabul edilir.

## 14. Koşu sırası, körlük ve tek koşu kuralı

1. Bu ön kayıt incelenir, düzeltilir, dondurulur, commit + push edilir.
2. **HDR adımı** (§6.4). Kural kodu (uyarlandıysa uyarlamasıyla) §6.4 madde 5'teki sırayla commit edilir ve README
   sınamasından geçer; ancak bundan sonra HDR dosyaları indirilir ve kod tek kez koşulur. Ek yazılır ve commit edilir.
3. **Kod** yalnız yapay serilerle yazılır ve sınanır. Dosya biçimi README'den (ve HDR adımında görülen HDR
   biçiminden) alınır. Hiçbir gerçek veri dosyası indirilmez ya da açılmaz. Testler §10.2'deki bütün denetimleri ((a3), (a4) ve 144
   satırlık 10MIN denetimi dahil) ve biçim hatası, biçim keşfi maskesi (§5), aralık dışı bozuk satır, sırasız dosya,
   ⌊gün⌋ = 0, 2023-10-16 sonrası satırı ve dolgu tanısı (§8.1) durumlarını kapsar. Bağlayıcı boyutta (n ≈ 40–62,
   B = 2000, M = 2000) uçtan uca bir yapay prova yapılır; süre ve bellek kaydedilir.
4. **Bağımsız kod incelemesi.** Gerçek veri indirilmeden yapılır.
5. **Veri indirme + manifest** (§2.4).
6. **Tek koşu.**
   - Gerçek veri bu adımda **bir kez** okunur.
   - Ana ölçü hesaplanmadan hemen önce iki işaret dosyası `x` kipinde oluşturulur: veri dizininde ve depoda
     (`kayit/turetme/tr10b/TR10B_GERCEK_DV_HESAPLANDI`). Depodaki dosya, manifest sha256'sını ve oluşturulma zamanını
     taşır. Koşu kodu başlangıçta iki yeri de denetler; biri varsa durur. Depodaki işaret dosyası çıktılarla aynı
     commit'te commit edilir.
   - Çıktı dosyaları `x` kipinde yazılır.
   - Çıktı ne olursa olsun yazılır. Bir istisna olursa yalnız doğrudan nedeni düzeltilir ve fark kayda geçer. Gerçek
     Δv görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik" başlığında yazılır ve sonucu ayrı satırdır.
7. Ham veri depoya konmaz. Yalnız manifestler, kod, çıktı JSON'u ve md raporu commit edilir.

## 15. Yeniden açma şartı

TR-10b, "veri yok" ya da tek kesime yığılmış bir sonuçla kapanırsa yalnız şunlardan biriyle yeniden açılır. Kural
gevşetmek (sakinlik, doluluk, boşluk, kapı) yeniden açma nedeni **değildir**.
- (a) Bu arşivden bağımsız, günlük çözünürlüklü, ≥ 10 yer veren yeni bir sünme ölçer veri kaynağı açılır. Örnekler:
  Bilham'ın Hayward ve öteki Kaliforniya ölçerlerinin işlenmiş serileri, Chihshang ya da İsmetpaşa sünme ölçerlerinin
  sayısal verisi. Yeni kaynak ayrı bir ön kayıtla eklenir.
- (b) USGS 2007 sonrası telemetriyi işlenmiş (sıfırlama ötelenmesi giderilmiş) biçimde yayımlar ve bu, 2008–2018
  epoklarında ≥ 10 yeni yer-pencere ekler.
- (c) Marmara'da ≥ 5 yıllık bir nokta sünme ölçeri serisi oluşur. Bu durumda TR-10b'nin ölçeği yalnız o serinin
  ayrı ön kaydına başvuru olarak girer. TR-10b yeniden koşulmaz.

TR-10b, TR-10'u (olaylı sınav, güç yok), S-7'yi ve AV-3'ü yeniden açmaz.

## 16. Bilinen zayıflıklar

1. **README gürültü tablosunun kısmi döngüselliği.** Etiket aralığı [2,2, 4,6] ve README modeli satırının (n, A)
   değerleri aynı arşivin 2004 öncesi verisinden, hız değişimleri (Coalinga, 1992–1995) modelden çıkarılarak
   kestirildi. Kaynak hakemli değil. 1973, 1978, 1998 ve 2003 pencereleri bu kestirimin verisiyle örtüşüyor. "T ≥ 2008"
   bilgi satırları bunu gösterir, düzeltmez. b* etiketi yalnız README'nin n = 2 istasyonlarının genlik aralığına
   göredir; README modelinin tamamıyla karşılaştırma ρ_R satırıdır (§10.4).
2. **Parkfield ağırlığı.** B'de yer-pencerelerin yaklaşık yarısı (R2'de 41'in 21'i) Parkfield'da. Bloklu bootstrap'ta
   Parkfield bloğu aralığı belirler. "Parkfield dışı" satırı bilgi içindir.
3. **1983–1993 boşluğu ve seçim yanlılığı.** Coalinga, Morgan Hill, Loma Prieta ve Landers bu epokları boşaltıyor.
   1993 Parkfield hızlanması (deprem gelmedi; bilinen bir "yanlış alarm" örneği) hiçbir kural setinde tabana
   girmiyor. Taban, tanımı gereği "sakin" dönemlerin tabanıdır. Koşulsuz yanlış alarm ölçeği bundan büyük olabilir.
   Küçük örneklemde q95'in aşağı yanlılığı (§10.4.1) da aynı yöndedir. İki yanlılık birbirini götürmez, toplanır.
   Hüküm kalıpları bu yüzden q95'i bir alt kestirim olarak yazar (§12).
4. **S-7 ile örtüşme.** Aynı bölge ve aynı fiziksel nicelik (sığ asismik kayma). B'nin pencerelerinin çoğu 2013 ve
   2018 epoklarında (2008-10 → 2018-10), yani S-7'nin 2004–2014 dönemiyle büyük ölçüde örtüşüyor. TR-10b, S-7'yi
   bağımsız olarak doğrulamaz ve S-7'nin yeniden açma şartını sağlamaz.
5. **Az blok.** En çok 6, büyük olasılıkla 5 kesim; Parkfield ve Hayward dışındaki kesimlerin verisi beklenmediği
   için K = 3–4 de olasıdır (K ≤ 3'te etiket yok, §9.3). Yüzdelik bloklu bootstrap kesiklidir ve 5–6 blokla nominal
   %90'dan dardır (§9.3 kapsama notu). Aralık ancak bir taban **ölçeği** verir, kesin bir kuyruk vermez. q99,
   N ≈ 40'ta en büyük iki değerin ara değeridir.
6. **Küçük örneklem yanlılığı.** N ≈ 40'ta q95 aşağı yanlıdır (§10.4.1).
7. **Arşivin dolgu ve uzlaştırması.** Sayfadaki "sabit hız varsayımıyla ötelenme" notu COVID dönemine aittir;
   kullanılan pencerelerin dışında kalır. README'ye göre ise erken telemetri dosyalarındaki bazı veriler mikrometre
   ölçümleri ya da kâğıttan sayısallaştırılmış kayıtlardır. Bunlar günlüğe ara değerlenmişse doluluk ve boşluk
   kuralları bunu göremez ve Δv sıfıra çekilir. Dolgu tanısı (§8.1) bunu bilgi satırıyla gösterir, düzeltmez.
8. **2007 sonrası işlenmemiş telemetri.** Glitch ve sıfırlama ötelenmeleri kalmış olabilir; tabanı büyütür. B'nin
   2013 ve 2018 pencereleri bu dönemde.
9. **HDR kuralı.** Önek kuralı yanlış pozitif üretir ve sayıyı düşürür. README metninde önceden sınandı: K listesinin
   30 olayından 28'ini en çok 1 yıl önceki bir tarihle yakalıyor ve hiç sahte son veren olay üretmiyor. HDR
   dosyalarında bunun ne kadar tuttuğu bilinmiyor. Notlar gerçek sünme olaylarını da anlatabilir ve bu notların
   düşürdüğü pencereler tabanı küçültür; §6.4 madde 4'teki sayaç bunu gösterir. HDR notlarını okumak, seri görülmeden
   yapılan sınırlı bir körlük bozulmasıdır. Notlardaki kayma ve hız ifadeleri kullanılmaz.
10. **Yağış ve ayak eğilmesi** düzeltilmez (README uyarısı: X461, XMD1, XTA1, XVA1).
11. **Uç penceresindeki küçük olaylar.** B1 T'de biter. (T, T + 15 g] içindeki M 4,5–5,5 bir olay u(T)'yi etkileyebilir
    ve düşürülmez. B2 yalnız M ≥ 5,5'i dışlar.
12. **"Sakinlik kapalı" satırı yok** (F12). Bu yüzden sakinlik kuralının tabanı ne kadar küçülttüğü ölçülmez.
13. **Büyüklük türleri karışık** (ML, Mw, Md); L(M) Mw için türetildi.
14. **Chihshang karşılaştırılabilirliği zayıf ve yanlılığı iki yönlü.** (i) Bindirme fayı, farklı aletler, 7 y ve
    3–4 y pencereler: uzun pencerenin gürültüsü küçük olduğundan karşılaştırma "içinde" yönüne yanlıdır. (ii) Taban,
    sakin pencerelerden ve N ≈ 40'la kestirildiği için küçüktür: bu da "üstünde" yönüne yanlıdır. Net yön bilinmez.
15. **Kapı büyük olasılıkla geçmez** (§13). Bu önceden kabul edilir.
16. **TR-10 körlüğüyle sınırlı örtüşme.** 1983 Coalinga (M 6,7 ve M 5,5; CRR1, XGH1, XMP1 ve XMP2'ye 43,6–45,9 km)
    için TR-10'un olay öncesi penceresi ≈ 1978-04 → 1983-04'tür. Bu dört istasyonun 1978 epoğu okuma aralığı onunla
    ≈ 6,5 ay (198 gün) örtüşür. Örtüşen kısım TR-10'un 48 aylık taban döneminin başıdır; 12 aylık olay öncesi
    dönemine dokunmaz. Aday listesinde başka örtüşme yoktur (`inc1_tr10_ortusme.py`, §19). Pencereler listede kalır.
    TR-10 yeniden açılırsa Coalinga'nın bu dört istasyonla çiftleri "taban döneminin ilk ≈ 6,5 ayı TR-10b'de görüldü"
    notunu taşır.

## 17. Marmara'ya bağ

- Marmara'ya **doğrudan çeviri yapılmaz.** Marmara'da ≥ 5 yıllık sünme serisi yok (Kumburgaz akustik 2017–2019, 2
  yıl). Orta Marmara fayı denizaltındadır. Nokta ölçerdeki ayak eğilmesi, InSAR'ın km ölçekli ortalaması ve denizaltı
  akustik ölçümü farklı gürültü süreçleridir.
- TR-10b'nin Marmara'ya verdiği yalnız iki şeydir:
  1. **Yanlış alarm ölçeği:** nokta sünme ölçeriyle ölçülen 2 yıllık hız değişiminin sakin pencerelerdeki taban
     büyüklüğü (mm/yıl ve hızın %'si; koşulsuz eşiğin alt kestirimi, §12), gelecekte Marmara'da kurulacak bir ölçer ya da yeterince uzun bir InSAR/NISAR serisi (AV-3) için
     bir başvuru ölçeği olarak;
  2. **Chihshang bilgi satırı.**
- Vermedikleri: hiçbir olasılık ya da olasılık çarpanı; Marmara'nın kendi tabanı; CMF için bir alarm eşiği.
  **Mutlak İstanbul deprem olasılığı hiçbir yerde yazılmaz.**

## 18. Maliyet

0 €. Veri USGS'den açık erişimle gelir, katalog SAYIM'ın önbelleğindedir. Tahmini iş yükü: HDR adımı birkaç saat;
kod ve yapay testler 1–2 gün; koşu bir saatin altında.

## 19. Sürüm 2 sayılarının yeniden üretimi

Betikler `kayit/turetme/tr10b/onkayit_yardimci/` altındadır, depo kökünden `python3 -I -B` ile koşulur,
`tr10b_sayim.py`'yi değiştirmeden kullanır ve yalnız üstveri (SAYIM önbelleği: indirme sayfası, HEAD sonuçları,
README, ComCat) ya da yapay gürültü okur. `<ham>` SAYIM'ın ham dizini, `<tr10_ham>` TR-10'unkidir; `<L>`
`inc1_listeler.py`'nin depo dışına yazdığı JSON'dur. İNCELEME-1'in betikleri yalnız yol düzeltmesiyle `inc10b/`
altına kopyalandı.

| Betik | Ürettiği | Sonuç | İNCELEME-1 ile |
|---|---|---|---|
| `inc1_listeler.py <ham> <tr10_ham> <L>` | B, A, B_R2, A_R2 ve "B1 geçmiş 5 y" listeleri, sha256'lar, U − R2 dökümü (§4, §11) | B 78/35/62/29/6; A 38/30/31/25/5; B_R2 42/23/41/22/5; A_R2 22/19/22/19/4; B1 geçmiş 5 y 52/30/39/25/6 (istasyon-pencere/istasyon/yer-pencere/yer/kesim); beş sha256 de §4 ve §11 madde 9'dakilerle aynı; U − R2 = 36 istasyon-pencere, 21 yer-pencere (20 + 6 + 4 + 2 + 3 + 1, XHR1 2018 dahil) | aynı |
| `inc1_hdr_kural.py <README> <L>` | §6.4 madde 3 kuralının README "Comments" bölümünde sınanması; başvuru çıktısı `inc1_hdr_kural_basvuru.txt` | 28/30 (kaçan XGH1 1997-12, XMM1 1986); sahte son veren 0; listelerden K olayıyla düşen 0; sürüm 1 kuralı B'den 3 düşürüyordu | aynı (ayrıca §20 E1 notu) |
| `inc10b/hdr_kural.py`, `inc10b/hdr_karsilastir.py`, `inc10b/hdr_kural3.py` | Sürüm 1 kuralının harfiyen ve cömert okuması; İNCELEME-1'in önerilen kural uygulaması | 0/30 ve 9/30; 28/30 | aynı |
| `inc1_readme_n0.py <L>` | README modeli beklentisi (tam maske, 2013, istasyon başına 1500 çekiliş, tohum 99) | 24 istasyon-pencere (hepsi B_R2'de; R üst sınırı 24 yer-pencere, 21'i T ≥ 2008): q50 2,25, q95 18,02, b* 10,13, κ 8,02; B'deki 11 istasyonun q95'i 3,6–33,2; tablodaki n > 2 olan 12 istasyonunki 3,6–33,2 | aynı |
| `inc1_kucuk_hesap.py` | r_c, κ_Gauss, q95 MC hatası, (a3), (a4), ρ sınırları, 144 satırlık 10MIN denetimi | r_c = −0,4255; κ 2,906; ±0,027 (4000 çekiliş); (a3) ortalamayla 8,059–8,070; (a4) hata 0; alt sınır 4,726 (günlük) ve 4,708 (10 dakikalık); 144 satır farkı ≤ 0,0030 | aynı; (a3) için "≈ 8,06" yerine 8,06–8,07 |
| `inc1_tr10_ortusme.py <ham> <L>` | TR-10 olay öncesi pencereleriyle örtüşme; ≤ 3 km yer kümeleri | yalnız Coalinga 1983 × {CRR1, XGH1, XMP1, XMP2} 1978, 43,6–45,9 km, 198 gün; B'nin 29 yeri 21 küme, A'nın 25 yeri 17 küme | aynı; uzaklık için "44–46 km" yerine 43,6–45,9 |
| `inc10b/c1.py` | c₁ ve κ, 100 000 çekiliş (tohum 8128) | 1,7760–1,7789 ± 0,005; κ 2,906–2,916 | aynı |
| `inc10b/a_sinir.py` | (a) serisinde ≥ 10 günlük herhangi bir maskeyle erişilebilen en büyük hata | 0,462–0,479 | aynı |
| `inc10b/blok.py`, `inc10b/etiket.py` | Bloklu aralığın kapsaması; bant içi yanlış etiket | U'nun üstünde K = 5: %23–26, K = 6: %14–20, K = 3: %30–31; yanlış "küçük" (b = 2,5) %1–7, yanlış "büyük" (b = 4) ≤ %0,7 | aynı |
| `inc10b/ek_liste.py <ham> <tr10_ham> <çıktı>` | B1 geçmiş 5 y alt kümesi (İNCELEME-1'in yolu) | 52; sha256 §11 madde 9'dakiyle aynı | aynı |

## 20. Sürüm 1 → 2 değişiklik listesi

Bütün İNCELEME-1 bulguları uygulandı; uygulanmayan bulgu yoktur. Uygulanmayan tek şey Ö6'daki **seçenek**tir (üç 1978
yer-penceresini listeden çıkarmak): İNCELEME-1 onu önermiyor, liste değişmedi.

| Bulgu | Değişen bölüm | Ne değişti |
|---|---|---|
| E1 | §6.4 madde 1, 2, 3, 4, 5, 6; §11 madde 9 ve 11; §14 madde 2; §16 madde 9; §0 F4 | Madde 3, 5, 6 düzeltme metniyle değiştirildi; madde 4'e "creep/event" sayacı eklendi; "HDR olayları uygulanmadan" bilgi satırı; §16 madde 9 yenilendi. Ekler (bu sürümün): kuralın kodu `inc1_hdr_kural.py` çekirdek işlevleri olarak sabitlendi (madde 1); madde 5(ii)'nin başvurusu `inc1_hdr_kural_basvuru.txt`; yeniden sınamada görülen iki boşluk kapatıldı: tarihsiz not aralığının uçları ters düşerse yer değiştirir (README'de XMM1 notu 2004-09-28 → 1993-01-01 ters aralık üretiyordu) ve "tarihli not" her tarihli nottur; çok sözcüklü öneklerden önce boşluk normalleştirmesi; "creep/event" tam sözcük ("creepmeter" sayılmaz). Sınama sonucu madde 3'e yazıldı |
| E2 | §10.4 (etiket, README modeli satırı, beklenti, κ başvurusu), §10.4.1, §11 madde 1, §12 "Kapı geçti", §13, §16 madde 1, §0 F13 | Etiket adı "README'nin n = 2 istasyonlarının genlik aralığı"; ρ_R satırı; önceden hesaplanan beklenti (q95 ≈ 18,0, b* ≈ 10,1, κ ≈ 8; yeniden üretildi). Çelişki çözümü (İNCELEME-1 lehine, değer aynı): ρ_R paydasının çekiliş parametreleri (çekiliş sayısı ve üreteç) bir kez, §11 madde 9'da yazılır; §10.4 oraya gönderir |
| Ö1 | §9.3 (blok sayısı şartı, kapsama notu, %10 tanımsızlık), §10.4, §10.4.1, §10.5 başlığı, §12 ("Kapı geçti", yeni "blok yetersiz" kalıbı, yanlış alarm cümlesi), §16 madde 5, §0 F14 | Düzeltme metinleri işlendi. Bu sürümün ekleri: "blok yetersiz" kalıbı (Ö1'in "K ≤ 3 ise ana satır 'blok yetersiz' yazar" kuralı §12'deki "yalnız aşağıdaki kalıplar" kuralıyla çelişmesin diye); bloklu aralığa dayanan ρ_R ve κ okumaları da K ≤ 3'te yapılmaz (§9.3); kapı altı bilgi satırında ρ_R ve κ okumasız yazılır (§10.1) |
| Ö2 | §12 Chihshang cümlesi, §16 madde 3 ve 14; başlık, giriş, §17 | Düzeltme metinleri işlendi. "Depremsiz pencere/dönem/taban" ifadeleri, Ö2 bulgusuna uyarak, başlıkta, girişte ve §17'de "sakin" ile değiştirildi |
| Ö3 | §7 "Yazılış sırası", §11 madde 7 ve 9 | Cümle değiştirildi; "B1 geçmiş 5 y" bilgi satırı (sha256 yeniden üretildi); epok dökümüne işaretli Δv |
| Ö4 | §10.5, §12 Chihshang cümlesi, §13 | r_c = −0,43, eşik |r| ≥ 0,43 |
| Ö5 | §8.1, §11 madde 9 ve 11, §12 ek kuyruklar, §16 madde 7, §10.1 | Doğrusal dolgu tanısı; bilgi satırı; §16 madde 7 değiştirildi |
| Ö6 | §16 madde 16, §0 F12 | Yeni madde; uzaklıklar yeniden hesaplanıp 43,6–45,9 km yazıldı (İNCELEME-1: 44–46) |
| Ö7 | §5 | Biçim keşfi kuralı; "koşu öncesi düzeltme" cümlesi bu kurala bağlandı; "biçim belirsiz" düşme nedeni §10.1'e ve §11 madde 11'e eklendi |
| K1 | §10.2 (a3), (a4); §10.2.1 tablo; §10.3; §10.2 (c-yapay) | Düzeltme metinleri işlendi; (a3)'teki "≈ 8,06" yeniden hesapla "≈ 8,06–8,07 (epoğa göre)" oldu |
| K2 | §10.2 (a) "Gerçek maskelerde"; §10.2.1 tablo | Eşik "en büyük ≤ 0,50"; tablo eşik sütunu buna uyduruldu ve analitik sınır satırı eklendi |
| K3 | §10.4 c₁ ve κ; §0 F7 | c₁ cümlesine MC hatası; κ 2,93 → 2,91; F7'de MC hatası ±0,026 → ±0,027 |
| K4 | §4; §11 madde 9 | U − R2 dökümü (XHR1 2018 dahil); "XDL2 dışarıda" bilgi satırı |
| K5 | §10.1, §12 ek kuyruklar, §11 madde 11 | Yer kümesi bilgisi; veri öncesi üst sınır 21 küme |
| K6 | §11 madde 9 | README N0 maddesine eşleşme, başlangıç ve T ≥ 2008 cümleleri |
| K7 | §14 madde 6 | İki işaret dosyası |
| K8 | §2.3, §5, §10.2 (b), §6.4 madde 2 | Üç metin düzeltmesi; 144 satırlık denetim yapay olarak doğrulandı (≤ 0,0030) |
| Tutarlılık | §0 öncelik sırası; başlık ve durum satırı; §4 R2 sha256'larının tam yazımı; §19 | Öncelik sırası: sürüm 2 > İNCELEME-1 > SAYIM. R2 sha256'ları kısaltılmış biçimden tam biçime |

---

## Ek 1 (12 Kasım 2026, dondurmadan sonra, hiçbir sünme verisi açılmadan)

Bu ek, dondurulmuş metni değiştirmez; koşu öncesi adımlarda ortaya çıkan okumaları ve §6.4'ün ürettiği aygıt olayı tablosunu kayda geçirir. Yazıldığı anda hiçbir telemetri, MIC, 10MIN ya da HaywardCreep dosyası indirilmemiş ve açılmamıştır.

**E1.1 Aygıt kayıtları (HDR) adımı yapıldı.** 60 dosya (29 HDR, 30 HDR2025, caveat.txt) okundu; manifest `kayit/turetme/tr10b/tr10b_manifest_hdr.json`, olay tablosu `tr10b_hdr_olaylar.csv`, listelere etkisi `tr10b_hdr_etki.json`. 394 K olayı (47 tarihsiz), 72 D olayı (20 tarihsiz). Veri öncesi üst sınır: B 43 yer-pencere / 22 yer / 6 kesim (önce 62 / 29); A 20 / 16; B_R2 18 / 13; B1 geçmiş 5 y 27 / 16. Kapı (≥ 20 yer, ≥ 40 yer-pencere) B'de yalnız üst sınırda ulaşılabilir; "veri yok" çok olası. Karar 2 gereği dağılım kapı altında da bilgi satırı olarak yazılır.

**E1.2 HDR biçim uyarlaması (§6.4 madde 5).** HDR dosyalarında README'de bulunmayan bir tablo biçimi çıktı. Uyarlama yalnız ekleme yapar: her tablo satırı (girintili devam satırlarıyla) ayrı bir nottur; üç zaman damgası biçimi tam tarih olarak tanınır. Uyarlanmış kural README başvuru çıktısını bayt bayt yeniden üretir. Kural bir kez koşuldu; kod `tr10b_hdr.py` (sha256 ad20b37f…) ve `onkayit_yardimci/inc1_hdr_kural.py` (69894531…) bu ekle aynı commit'tedir.

**E1.3 Tablo başlık satırları.** "Possible Offsets:" gibi tablo başlıkları ayrı tarihsiz not olarak işlendi (tutucu okuma; sayımdan önce seçildi). Bu okuma B'den 7 istasyon-pencere düşürür (CHP1, CRR1, XSC1, XSH1, XTA1, XVA1 2013; XSH1 2018). Başlık ilk tablo satırına katılsaydı B 47 yer-pencere / 25 yer olurdu. Bağlayıcı olan tutucu okumadır; öteki okuma yalnız "başlık katılmış" adlı bilgi satırı olarak yazılır ve hükmü değiştirmez. Kodlayıcı, okumayı seçerken CRR1 üzerindeki etkisini düşündüğünü bildirmiştir; bu burada kayıtlıdır.

**E1.4 Elle ölçüm (MIC) okuma aralığı.** §8.2'nin 90 günlük braket ve 180 günlük aralık şartı, okuma aralığı [w0 − 15 g, T + 15 g] ile sınırlı kalırsa uygulanamaz (uçlarda fiilen 15 gün olur). Yazılı kuralı işler kılan okuma bağlayıcıdır: **yalnız MIC kaynaklarında okuma aralığı [w0 − 90 g, T + 90 g]'dır**, üst ucu 2023-10-16'yı aşamaz; telemetri ve 10MIN kaynaklarında aralık değişmez. Dar okuma ([w0 − 15, T + 15]) "MIC dar aralık" bilgi satırı olarak yazılır. Bu karar hiçbir MIC dosyası görülmeden verildi.

**E1.5 Öteki kodlayıcı okumaları.** Kodlayıcının bildirdiği 24 okuma (kayıt: bu commit'in iletisi ve `TR-10b_KOD-INCELEME.md`) en dar/tutucu okuma ilkesiyle uygulanmıştır; kod incelemesi her birini denetler. (a) denetiminde x(t)'nin zaman başlangıcı okuma aralığının başıdır (SAYIM'daki 0,00045 doğrulaması bu başlangıçla yapılmıştır).

---

## Ek 2 (12 Kasım 2026, kod incelemesinden sonra, hiçbir sünme verisi açılmadan)

Kod incelemesi (`TR-10b_KOD-INCELEME.md`, hüküm DÜZELTMEYLE HAZIR; 57/57 yapay sınama, 9/9 mutasyon yakalandı) sonrasında, veri öncesinde kayda geçen okumalar. Bu ek yazıldığı anda hiçbir telemetri, MIC, 10MIN ya da HaywardCreep dosyası indirilmemiş ve açılmamıştır.

**E2.1 Kod hatası kapıdan önce gelir.** Kod denetimi kesin başarısızsa hüküm, veri kapısından bağımsız olarak "geçersiz (kod)" olur; kapı sayıları bilgi olarak yazılır (§10.2 "kesin olarak"; kodlayıcı okuması 19'un yerini alır).

**E2.2 E1.4'ün TR-10 örtüşmesine etkisi.** MIC okuma aralığının genişlemesiyle CRR1, XGH1, XMP1 ve XMP2'nin 1978 aralığı, 1983 Coalinga'nın TR-10 olay öncesi penceresiyle 198 yerine 273 gün örtüşür. Yeni bir örtüşme yoktur; 12 aylık olay öncesi döneme dokunmaz. §16 madde 16 bu sayıyla okunur.

**E2.3 MIC'de aygıt olayı tamponu.** E1.4 MIC braketini ±90 güne genişletti; K tamponu metindeki gibi [w0 − 30 g, T + 15 g] kalır (metin değiştirilmez). Bunun sonucu olarak §16 madde 11'deki uç olayı riski MIC kaynaklarında T + 90 güne kadar uzanır; bu bir bilinen zayıflıktır ve "yalnız telemetri" bilgi satırı bu riski taşımayan karşılaştırmadır.

**E2.4 Tek koşu mekanizmasının uygulanışı (§14 madde 6).** Gerçek Δv'ye bağlı olmayan bütün kurulum işaret dosyasından önce yapılır; işaretten önce aynı ölçü, hüküm ve çıktı kodu gerçek maskeler ve YAPAY değerlerle bir kez kuru koşulur; hata çıkarsa işaret yazılmaz. Ham okuma sonucu işaretle aynı anda depo dışına yazılır ve işaret onun sha256'sını taşır. İşaretten sonra hata olursa (çıkış 4) yalnız doğrudan neden düzeltilir ve `--devam` ile ham veri yeniden okunmadan sürdürülür; bu, veriye ikinci bakış sayılmaz, çünkü okuma sonucu değişmez.

**E2.5 Öteki okumalar.** (a) Ek kuyruklar "veri yok" kalıbına da eklenir. (b) §9.3'ün blok şartı (K ≥ 4) bütün satırlara uygulanır; K ≤ 3'te yer bootstrap'ı kullanılır ve etiket okunmaz. (c) Chihshang aralığı "güç yok" ya da K ≤ 3 iken okuma yazılmaz ("güç yok"). (d) Dolgu tanısı kodlayıcı okuması 13'teki gibi uygulanır (δ okuma aralığındaki en fazla ondalık basamaktan; aday koşu uzunluğu max(15, |V|); eğim ölçütü |eğim| < 1e-12). (e) Bilgi kayıtları: E1.3 "başlık katılmış" satırında 7 istasyon-pencereden 6'sı geri gelir (CHP1 2013 gelmez); "Ditto" satırları K sayılmaz; 144 satırlık denetimin yedek yolu kodlayıcı okuması 22'deki gibidir.

Koşu kodu bu ekle aynı commit'tedir.
