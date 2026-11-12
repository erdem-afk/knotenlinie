# TR-10b ön kaydı: sünme ölçerlerde depremsiz pencerelerde 2 yıllık sünme hızı değişiminin taban dağılımı

Tarih: 12 Kasım 2026. Durum: **TASLAK sürüm 1, incelemeye hazır.** Dondurulmadı; inceleme bulguları işlendikten sonra
dondurulur, ondan sonra metin değişmez ve ekler ayrı başlıkla yazılır.
Türediği yer: `kayit/onkayit/TR-10_SAYIM.md` §6 (olay gerektirmeyen ara ölçüm) ve tasarım + üstveri sayımı
`kayit/onkayit/TR-10b_SAYIM.md` (kapı SINIRDA). Kod: `kayit/turetme/tr10b/tr10b_sayim.py`. Maliyet 0 €.

Bu bir **ölçümdür**, hipotez sınavı değildir. Çıktısı bir yanlış alarm ölçeğidir: depremsiz dönemlerde nokta sünme
ölçeriyle ölçülen 2 yıllık hız değişiminin ne büyüklükte ve ne sıklıkta olduğu. Deprem olasılığı üretmez. Mutlak
İstanbul deprem olasılığı bu belgede ve koşunun hiçbir çıktısında yazılmaz.

Körlük beyanı (bu belge yazılırken): hiçbir sünme ölçer veri dosyası (DAY, 10MIN, MIC, CL10, PKF_EQ, HaywardCreep),
hiçbir HDR/Notes dosyası, HDRx.tar ve noise.pdf açılmadı ya da indirilmedi. Okunanlar: SAYIM'ın önbelleğindeki
indirme sayfası anlık görüntüsü, README, dizin listeleri (yalnız dosya adları), HEAD sonuçları ve ComCat dosyası.
Bu belgedeki bütün yeni sayılar `tr10b_sayim.py`'nin değiştirilmemiş işlevleriyle (sayım için `say`, yapay hesap için
`pl_seri`, `dv_uc`, `gunler`) `python3 -I -B` altında üretildi; yapay hesaplar yalnız üretilmiş gürültüyle yapıldı.

## 0. Bağlayıcı metinlerin sırası ve SAYIM'dan farklar

Çelişkide şu sıra geçerlidir:
1. §4'teki **aday listesi** (kanonik sha256 ile).
2. Bu belge.
3. `TR-10b_SAYIM.md` §2 (tasarım), yalnız bu belgenin değiştirmediği yerlerde.

Bu belge SAYIM'ı şu noktalarda değiştirir ya da tamamlar (hepsi hiçbir sünme verisi görülmeden):

| # | SAYIM | Bu ön kayıt | Neden |
|---|---|---|---|
| F1 | Kapı R2 kapsam modeliyle sayıldı | Aday kümesi U (üst sınır) kapsamıyla kurulur; gerçek kapsamı veri belirler; kapı gerçek veriyle yeniden uygulanır (§4, §10.1) | R2 bir kapsam tahminiydi; veri okununca tahmine gerek kalmaz |
| F2 | Güven aralığı site bootstrap'ı, kesim bootstrap'ı bilgi | **Fay kesimi bloklu bootstrap ana**, site bootstrap'ı bilgi satırı (§9) | Kök oturum kararı 4 |
| F3 | Tek kural seti seçimi incelemeye bırakıldı | A ve B ikisi de bağlayıcı; **B ana hüküm satırı, A zorunlu ikinci satır** (§7) | Kök oturum kararı 1 |
| F4 | HDR kuralı açık | HDR okuma sırası ve mekanik kullanım kuralı sabit (§6.4) | Kök oturum kararı 3 |
| F5 | Pozitif kontrol: medyan(d) ∈ [4,90, 5,03] | Telemetri katmanında deterministik sınır + medyan(d) ∈ [4,85, 5,03]; elle ölçüm katmanında analitik tam denetim (§10.3) | Gerçekçi ve en kötü maskelerle yapay doğrulama (§10.2.1) |
| F6 | (b) paydası tam maskeli MC | Payda aynı gerçek maskelerle ayrı MC; tam maskeli oran bilgi satırı (§10.2) | Payda maske seçiminden bağımsız olsun |
| F7 | Eşdeğer rastgele yürüyüş sabiti c₁ = 1,732 (4000 çekiliş) | c₁ = 1,78 (100 000 çekiliş) (§10.4) | 1,732'nin MC hatası ≈ ±0,026; fark %2,7 |
| F8 | %99 yazılmaz | q99 yazılır, "N < 300: bilgi" notuyla (§11) | Görev tanımındaki çıktı satırı |
| F9 | Site temsilcisi: en erken ilk gözlem | Önce telemetri, sonra en erken ilk gözlem (§9.1) | Eş konumlu elle ölçerin telemetriyi dışlamaması |
| F10 | K tamponu [w0 − 30 g, T] | [w0 − 30 g, T + 15 g] (§6.1) | Uç penceresinin ikinci yarısı; sayıma etkisi 0 (§6.1) |
| F11 | Literatür yerleşimi bütün doğrulanmış iddialar için | Yalnız Chihshang 2003, bilgi satırı (§10.5) | Kök oturum kararı 5 |
| F12 | "Sakinlik kapalı" değişkesi bilgi satırı (SAYIM §8) | Yazılmaz (§16 madde 12) | Olaylı pencereleri okumak TR-10'un körlüğünü bozar |

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

- Kullanılabilecek son gün **2023-10-16**'dır (son epoğun T + 15 g'si). 2024 ve sonrasının hiçbir satırı
  ayrıştırılmaz. Aday listesinde 2023 epoğu olmadığı için fiilen kullanılan son gün 2018-10-16'dır.
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
- Karşılaştırma için SAYIM'ın R2 listeleri: B 42 istasyon-pencere (sha256 `560b49c1…cece6d036d`), A 22 (sha256
  `cc238e03…e44b71426`). İkisi de U listelerinin alt kümesidir.

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

U'nun R2'ye eklediği adayların çoğunun (HW* elle ölçerlerinin 2003–2013 pencereleri, HLC1/HLD1/SHR2, TWR1/XPH1,
XDL2 2013/2018, BIT1 ve XMP* 1998) README aralıklarına göre verisi yoktur. Bunlar veri okununca doluluk şartıyla
kendiliğinden düşer. Listeye alınmaları yalnız "kapsamı veri belirler" ilkesinin sonucudur; sayıyı artırmaları
beklenmez (§13).

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
  - ⌊gün⌋ = 0 olan tek bir satır bile durdurur. Bu, 0 tabanlı gün kuralını sessizce bir gün kaydırmamak içindir.
  - Bu durumlar bir veri sonucu değil, kod ya da biçim sorunudur. Hiçbir Δv hesaplanmadan düzeltilir ve
    "koşu öncesi düzeltme" başlığıyla kayda geçer.
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

1. **Ne zaman:** ön kayıt dondurulduktan hemen sonra, hiçbir veri dosyası indirilmeden ve kod yazılmadan önce. HDR
   dosyaları seri değeri taşımaz; yalnız aygıt olayları için okunur. Bu adımda hiçbir hız hesaplanmaz.
2. **Hangi dosyalar, hangi sırayla:**
   1. `CREEP/HDR/` altındaki, sayfada bağlantısı olan 29 `*.hdr1` dosyası (alfabetik);
   2. `CREEP/HDR2025/` altındaki 30 `*.hdr1` dosyası (alfabetik; 1'deki 29 dosyanın adaşları ve c461);
   3. `CREEP/HDR/caveat.txt`.
   `._*` dosyaları (macOS kaynak çatalı) ve HDRx.tar okunmaz.
3. **Kullanım kuralı (mekanik):**
   - Bir not, tarih içeren bir satırla başlar ve bir sonraki tarihli satıra dek sürer. Tanınan tarih biçimleri
     şunlardır: YYYY-MM-DD, YYYY/MM/DD, MM/DD/YY(YY), DD Mon YYYY, Mon DD YYYY, Mon YYYY, "YYYY GGG" (yıl ve yılın
     günü). İki haneli yıl > 30 ise 19xx, değilse 20xx alınır.
   - Tarihi 2023-10-16'dan sonra olan notlar anahtar sözcük aranmadan atlanır.
   - Notta (büyük-küçük harf duyarsız) şu sözcüklerden biri geçiyorsa not bir **K olayıdır**: reset, re-set, rezero,
     re-zero, zeroed, "new zero", broke, broken, break, snapped, replaced, replace, "new wire", "new rod",
     "new sensor", "new transducer", "new lvdt", moved, relocat, reinstall, re-install, reposition, offset, repair,
     damaged, vandal, collapse, flood, rodent, "out of range", overrange, over-range, "ran out", recalibrat.
   - Ek olarak abandon, removed, destroyed, decommission ya da "no longer" geçiyorsa olay **son veren** K olayıdır.
   - Yalnız electronics, DCP, "scale factor" ya da gain geçiyorsa olay bir **D olayıdır**.
   - Olay tarihi notun tarihidir. Bir aralık verilmişse başlangıcı alınır.
   - Anahtar sözcük içeren ama tanınan tarihi olmayan satırlar listelenir. Tarihleri, yalnız aynı notun metninden,
     elle yazılır; her biri özgün satır alıntılanarak kayda geçer. O sırada diskte hiçbir seri bulunmaz.
4. **Kayıt:** sonuç "Ek: HDR K/D olayları (koşu öncesi)" başlığıyla bu belgeye eklenir. Her olay için dosya, satır
   numarası, tarih, eşleşen sözcük ve tür yazılır; aday listesinden düşürdüğü istasyon-pencereler sayılır. Notlarda
   geçen kayma ya da hız ifadeleri kayda alınmaz ve kullanılmaz.
5. **Biçim uyumsuzluğu:** HDR biçimi bu kurala uymuyorsa (ör. tablo biçimi), uyarlama aynı Ek'e yazılır. Anlam
   kuralı (anahtar sözcük → K, son veren ya da D) değişmez.
6. Yanlış pozitifler (ör. "no offset") de K sayılır. Bu, sayıyı düşürür ve önceden kabul edilir (§16).

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
SAYIM §5.4). Bu seçim tabanın büyüklüğünü değil, yalnız örneklem boyunu etkiler. İki satır da her durumda yazılır;
hiçbiri elenmez.

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
  bloklar ad sırasındadır. Aralık, 2000 değerin %5 ve %95 nicelikleridir (yüzdelik yöntem, çift yanlı %90).
- Bir yinelemede bir nicelik tanımsızsa (ör. sünen katmanda hiç pencere yoksa) o yineleme o nicelikten düşer ve düşen
  yineleme sayısı yazılır.
- Her satır ve her bootstrap (ana, A, katmanlar, bilgi satırları) **yeni** bir `default_rng(20261112)` ile başlar.
- **Bilgi: yer bootstrap'ı.** Aynı yöntem, blok yerine yer; aynı tohum.
- Bütün nicelikler `numpy.quantile(..., method="linear")` ile alınır.

## 10. Hüküm sırası

Sıra şöyledir: **veri kapısı → kod denetimi yapay veriyle → pozitif kontrol gerçek veride → ölçü.** Gerçek Δv
havuzu yalnız ilk üç adım geçtikten sonra hesaplanır ve dosyaya yazılır. Kapı geçmese de 2. ve 3. adım koşar
(§10.1).

### 10.1 Veri kapısı

- §5, §6 (HDR eki dahil), §8 ve §9.1'den sonra kural seti B'de geçerli yer ve yer-pencere sayılır. Bu adım hiçbir
  Δv yazdırmaz; yalnız sayıları, düşme nedenlerini (kapsam yok, doluluk, boşluk, uç değeri, K, HDR, indirilemedi)
  yazar.
- **Kapı:** yer ≥ 20 **ve** yer-pencere ≥ 40.
- **Kapı geçmezse:** ana hüküm **"veri yok"** olur. 2. ve 3. adım yine koşar. Geçerlerse dağılım yine hesaplanır ve
  bütün çıktı satırlarıyla, güven aralığıyla ve her satırda **"kapı altı"** etiketiyle bir **bilgi satırı** olarak
  yazılır (eleme yok kuralı). Bu bilgi satırına etiket (§10.4) yazılmaz. Chihshang satırı (§10.5) da yazılmaz.
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
    - Gerçek maskelerde: |Δv − Δv₀|'nin %99'u ≤ 0,5 mm/yıl (yer-pencere başına bir seri).
  - Elle katman: x(t) = 3 + 7t ölçüm günlerinde: |Δv| ≤ 10⁻⁶ mm/yıl.
- **(b) Uçtan uca ölçek.**
  - Yapay seri: rastgele yürüyüş b = 3 mm/yıl^0,5 + beyaz gürültü 0,1 mm, günlük tam ızgarada üretilir, gerçek maske
    uygulanır. Seri o yer-pencerenin kaynak türünün dosya biçiminde (DAY/MIC: günde bir satır; 10MIN: günde bir
    satır, öğlen) gzip'li metin olarak yazılır ve koşu kodunun bütün yolundan (okuma, biçim denetimi, günlük medyan,
    doluluk, uç değeri, Δv) geçer.
  - Yer-pencere başına R = ⌈820 / n⌉ gerçekleşme üretilir. j'inci gerçekleşmenin tohumu
    `int(sha256(f"{KOD}|{Y}|{j}").hexdigest()[:16], 16) ^ 20261112`'dir.
  - Pay: n·R değerin |Δv| havuzunun %95 niceliği.
  - **Payda:** her yer-pencere için aynı gerçek maskeyle M = 2000 çekiliş. Seri bellekte üretilir, dosyaya yazılmaz
    ve ölçü işlevi doğrudan çağrılır. Üreteç `default_rng(20261112 + 1)`; yer-pencereler kanonik sırayla. Payda, n·2000
    |Δv| değerinin %95 niceliğidir.
  - Oran pay / payda ∈ [0,88, 1,12] değilse hüküm "geçersiz (kod)".
  - Bilgi: aynı pay, tam maskeli 20 000 çekilişlik paydaya bölünür (SAYIM'ın tanımı).
- **(c-yapay) Pozitif kontrol.** Her yer-pencerenin ilk yapay gerçekleşmesine (j = 0) ρ(t) = 5 mm/yıl ·
  max(0, t − t_H) eklenir. d = Δv_eklenen − Δv_özgün, aynı koşu yolundan. Geçme şartları §10.3 ile aynıdır.
- **Başarısızlık:** kod, gerçek Δv görülmeden düzeltilir ve "koşu öncesi düzeltme" başlığıyla kayda geçer. 2. adım
  yeniden koşar. En çok iki düzeltme turu yapılır; üçüncü başarısızlıkta hüküm kesin olarak "geçersiz (kod)" olur.

#### 10.2.1 Eşiklerin yapay doğrulaması (bu belge için koşuldu)

Hesaplar `tr10b_sayim.py`'nin `pl_seri`, `dv_uc`, `gunler` işlevleriyle yapıldı. Tohumlar: SAYIM 20261113; bu
belgede 777 ve 4242. "Gerçekçi maske": doluluk hedefi U[0,6, 1], 1–60 günlük delikler, §8.1 şartlarını sağlayana dek
yeniden üretilir. "En kötü maske": her uç penceresinde yalnız 10 gün ve hepsi tek yanda.

| Denetim | Yapay sonuç | Eşik |
|---|---|---|
| (a) tam maske, mevsimsiz / mevsimli (SAYIM) | hata 0 / 0,00045 mm/yıl | ≤ 0,005 |
| (a) %10 eksik, 1–20 g delik, 495 seri (SAYIM) | %99: 0,22; en çok 0,27 | %99 ≤ 0,5 |
| (a) gerçekçi maske, 500 seri | %99: 0,20; en çok 0,24 | %99 ≤ 0,5 |
| (a) en kötü maske, 500 seri | %99 ve en çok: 0,48 | %99 ≤ 0,5 (sınırda; gerçek maskelerin hepsi en kötü olmaz) |
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
  Kaynak, maske ve uç kuralları özgün serideki gibidir; sinyal ekleme maskeyi değiştirmez.
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

### 10.4 Ana ölçü ve etiket (yalnız kapı geçtiyse etiket konur)

- **Ana satır (B):** |Δv| için q50, q95, q99 mm/yıl, her biri bloklu bootstrap aralığıyla [L, U].
- **Eşdeğer rastgele yürüyüş genliği:** b* = q95 / c₁, c₁ = 1,78. c₁, b = 1 mm/yıl^0,5 saf rastgele yürüyüşte, tam
  maskede q95|Δv|'dir (100 000 çekiliş: 2003 ızgarası 1,7805, 2013 ızgarası 1,7748). SAYIM'daki 1,732 değeri 4000
  çekilişlik bir MC'dir (F7). Aralık uçları da aynı sabitle çevrilir: b*_L = L / c₁, b*_U = U / c₁.
- **Etiket:**
  - b*_L > 4,6 ise "taban README gürültü bandından büyük";
  - b*_U < 2,2 ise "taban README gürültü bandından küçük";
  - ötekilerde "taban README gürültü bandında".
  - Bant [2,2, 4,6], README gürültü tablosunda indisi n = 2,00 olan altı istasyonun (XMM1, XVA1, XPK1, CRR1, CWC3,
    XMR1) genlik aralığıdır.
- **Kuyruk ölçüsü:** κ = q95|Δv| / q50|Δv|, bloklu aralığıyla. Başvuru değerleri: tek ölçekli Gauss (saf rastgele
  yürüyüş, uç ölçüsüyle) 2,93; README tablosunun 18 istasyonluk N0 havuzu 6,1 (SAYIM §4.2: 14,6 / 2,4). Okuma
  kuralı: κ_L > 2,93 ise "kuyruk tek ölçekli Gauss'tan ağır (ölçek karışımı ya da basamaklı sünme)". Bu bir bilgi
  satırıdır; etiketi değiştirmez. q99 / q95 de yazılır.

#### 10.4.1 Etiketin yapay davranışı (bu belge için koşuldu; tohum 4242)

Yer-pencereler bağımsız, |Δv| tek ölçekli Gauss; 200 tekrar, B = 1000. "B_R2 yapısı" kesim boyları (21, 10, 4, 4, 2),
"B_U yapısı" (21, 19, 8, 6, 4, 4).

| Gerçek b | B_R2: büyük / bant / küçük | b*_L, b*_U medyanı | B_U: büyük / bant / küçük |
|---|---|---|---|
| 1,5 | 0 / 0,075 / 0,925 | 1,10, 1,67 | 0 / 0,015 / 0,985 |
| 3,0 | 0 / 0,995 / 0,005 | 2,14, 3,27 | 0 / 0,995 / 0,005 |
| 6,0 | 0,39 / 0,61 / 0 | 4,42, 6,63 | 0,585 / 0,415 / 0 |
| 9,0 | 0,93 / 0,07 / 0 | 6,48, 9,82 | 1 / 0 / 0 |

Okuma: N ≈ 40'ta q95 kestiricisi aşağı yanlıdır (b = 3'te aralık medyanları [2,14, 3,27]). Kesimler arası gerçek
farklar bloklu aralığı bu tablodakinden genişletir. "Bandından büyük" hükmü ancak b ≳ 6'da olasıdır.

### 10.5 Chihshang 2003 bilgi satırı (yalnız kapı geçtiyse)

- İddia: Lee vd. 2005 (10.1016/j.crte.2005.04.018), 2003 Chengkung Mw 6,6–6,8 öncesi, 1990–1997 ortalaması 22 mm/yıl
  → 2000–2003 ortalaması 14 mm/yıl: Δv_c = −8 mm/yıl, r_c = −0,36. Bindirme fayı; dönemler farklı aletlerle (yüzey
  ölçümü ve sünme ölçeri) ve farklı uzunluklarda (7 y ve 3–4 y) ölçülmüş.
- **Birincil:** P_r = (sünen katmanda |r| ≥ 0,36 olan yer-pencere sayısı) / (sünen katmandaki yer-pencere sayısı).
- **İkincil:** P_v = (|Δv| ≥ 8,0 mm/yıl olan yer-pencere sayısı) / (B'deki geçerli yer-pencere sayısı).
- Aralık bloklu bootstrap'la, aynı yinelemelerle.
- Okuma: üst sınır < 0,05 ise "tabanın üstünde"; alt sınır > 0,05 ise "tabanın içinde"; ötekilerde "sınırda".
- Bu satır bir öncül sınaması değildir. Tek bir iddianın, farklı mekanizmalı bir fayda ve farklı alet dönemiyle,
  bu tabanın neresine düştüğünü gösterir.

## 11. Çıktı satırları

Her satırda: yer S, yer-pencere N, kesim K, katman ve kural seti. Kapı altındaki her satır "kapı altı" etiketini
taşır. N < 20 olan katman satırları "güç yok" yazar, nokta değerleri verir, aralık vermez.

1. **Ana (B):** q50, q95, q99 |Δv| mm/yıl [L, U]; b* [b*_L, b*_U]; etiket.
2. **Sünen katman (B, v₅ ≥ 2):** q50, q95, q99 |r| (hızın %'si olarak) [L, U]; katmandaki N.
3. **İşaretli Δv:** medyan ve hızlanan/yavaşlayan pay (simetri).
4. **Kuyruk:** κ = q95/q50 [L, U]; q99/q95.
5. **A satırı:** 1–4'ün aynısı, A için.
6. **Kesim dökümü (B):** her kesim için N, q50, q95 |Δv| ve q95 |r|; aralık yer bootstrap'ıyla (kesim içinde
   blok yok).
7. **Epok dökümü (B):** her epok için N, q50, q95 |Δv|; bloklu aralık.
8. **Katman dökümü (B):** telemetri / elle; kaynak türü (DAY, 10MIN, MIC).
9. **Bilgi satırları (B):**
   - Parkfield dışı;
   - yalnız T ≥ 2008 (README tablosu 2004 öncesi veriden kestirildi; döngüsellik denetimi);
   - D olayları dışarıda;
   - yalnız telemetri;
   - SAYIM'ın R2 aday alt kümesi;
   - yer bootstrap'ı aralıkları;
   - menteşe modeli Δv_m (§8.4) q50, q95;
   - README N0 beklentisi: temsilcisi README tablosundaki 18 istasyondan biri olan yer-pencereler için, tablodaki
     (n, A) ile güç yasası gürültüsü, gerçek maskeyle yer-pencere başına 2000 çekiliş, üreteç
     `default_rng(20261112 + 3)`; q95_N0,README ve q95_ölçülen / q95_N0,README (aynı alt küme).
10. **Chihshang satırı** (§10.5).
11. **Denetim satırları:** kapı sayıları ve düşme nedenleri; (a), (b), (c-yapay), (c-gerçek) sonuçları; düzeltme
    turu sayısı; okuma sayaçları (bozuk, başlık, aralık dışı atlanan satır); manifest denetimi.

## 12. Hüküm cümlelerinin kalıpları

Yalnız aşağıdaki kalıplar kullanılır; köşeli parantezler sayılarla doldurulur.

- **Kapı geçti:** "TR-10b: [taban README gürültü bandından büyük | bandında | bandından küçük]. Kural seti B: Orta
  Kaliforniya sünme ölçerlerinde sakin 5 yıllık pencerelerde 2 yıllık sünme hızı değişimi |Δv|, yer-pencerelerin
  yarısında [q50] mm/yıl'ı, %5'inde [q95] [L, U] mm/yıl'ı aşar (sünen katmanda hızın %[r50]'sini ve
  %[r95] [L, U]'sunu); yer [S], yer-pencere [N], kesim [K]; aralık fay kesimi bloklu bootstrap, %90. Kural seti A:
  q95 [..] [L, U] mm/yıl (yer [..], yer-pencere [..]; kapı [geçer | altı])."
- **Kapı geçmedi:** "TR-10b: veri yok (kural seti B: yer [S] / yer-pencere [N]; kapı ≥ 20 / ≥ 40). Bilgi satırı,
  kapı altı: |Δv| q50 [..], q95 [..] [L, U] mm/yıl (sünen katmanda hızın %[..]'si [L, U]); bu satır bir hüküm
  değildir."
- **Kod:** "TR-10b: geçersiz (kod) ([hangi denetim], [değer] / [eşik]); gerçek Δv hesaplanmadı."
- **Yanlış alarm ölçeği cümlesi** (yalnız kapı geçtiyse): "Orta Kaliforniya'da nokta sünme ölçeriyle ölçülen 2
  yıllık sünme hızı değişimi depremsiz pencerelerde %5 sıklıkla [q95] mm/yıl'ı (sünen ölçerlerde hızın
  %[r95]'ini) aşar; bundan küçük bir değişim bu tür bir ölçerde tek başına olağandışı sayılmaz."
- **Chihshang cümlesi** (yalnız kapı geçtiyse): "Bilgi: Chihshang 2003 iddiası (−8 mm/yıl, −%36; bindirme fayı,
  farklı alet dönemleri) bu tabanda |r| ölçüsüyle [tabanın üstünde | içinde | sınırda] (P_r = [..] [L, U])."
- **Yasak:** mutlak İstanbul ya da Marmara deprem olasılığı, olasılık çarpanı, "Marmara'da alarm eşiği X'tir",
  "öncül bulundu", "öncül yok" cümleleri.

## 13. Önceden beyan edilen beklenti (yazarın beyanı)

- **Kapı:** gerçek veriyle "veri yok" olasılığı **0,65**. Gerekçe: U'nun R2'ye eklediği adayların çoğunun verisi
  yok (§4); gerçekçi tavan R2'nin 41 yer-penceresi. Doluluk, ≤ 60 g boşluk, uç şartı ve HDR olayları bundan en az
  ikisini düşürmeye yeter.
- **Kapı geçerse etiket:** büyük 0,40; bantta 0,50; küçük 0,10 (SAYIM §4.1). Gerekçe: README kestirimleri Coalinga ve
  1992–1995 hız değişimlerini modelden çıkardı, yağış olayları da var. Bloklu aralığın genişliği "bantta" yönüne
  iter.
- **Büyüklük:** b ≈ 3 ise q95|Δv| ≈ 5–5,5 mm/yıl. Sünen istasyonların hızı 7–21 mm/yıl olduğundan bu, hızın
  %25–70'i demektir.
- **Chihshang:** |r| ölçüsüyle büyük olasılıkla "tabanın içinde". Bu önceden kabul edilir.

## 14. Koşu sırası, körlük ve tek koşu kuralı

1. Bu ön kayıt incelenir, düzeltilir, dondurulur, commit + push edilir.
2. **HDR adımı** (§6.4). Ek yazılır ve commit edilir.
3. **Kod** yalnız yapay serilerle yazılır ve sınanır. Dosya biçimi README'den (ve HDR adımında görülen HDR
   biçiminden) alınır. Hiçbir gerçek veri dosyası indirilmez ya da açılmaz. Testler §10.2'deki bütün denetimleri ve
   biçim hatası, sırasız dosya, ⌊gün⌋ = 0, 2023-10-16 sonrası satırı durumlarını kapsar. Bağlayıcı boyutta (n ≈ 40–62,
   B = 2000, M = 2000) uçtan uca bir yapay prova yapılır; süre ve bellek kaydedilir.
4. **Bağımsız kod incelemesi.** Gerçek veri indirilmeden yapılır.
5. **Veri indirme + manifest** (§2.4).
6. **Tek koşu.**
   - Gerçek veri bu adımda **bir kez** okunur.
   - Ana ölçü hesaplanmadan hemen önce veri dizininde `TR10B_GERCEK_DV_HESAPLANDI` dosyası `x` kipinde oluşturulur.
     Dosya varsa koşu kodu başlangıçta durur.
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

1. **README gürültü tablosunun kısmi döngüselliği.** Etiket bandı [2,2, 4,6] aynı arşivin 2004 öncesi verisinden,
   hız değişimleri (Coalinga, 1992–1995) modelden çıkarılarak kestirildi. Kaynak hakemli değil. 1973, 1978, 1998 ve
   2003 pencereleri bu kestirimin verisiyle örtüşüyor. "T ≥ 2008" bilgi satırı bunu gösterir, düzeltmez. Etiket
   yalnız bu banda göredir.
2. **Parkfield ağırlığı.** B'de yer-pencerelerin yaklaşık yarısı (R2'de 41'in 21'i) Parkfield'da. Bloklu bootstrap'ta
   Parkfield bloğu aralığı belirler. "Parkfield dışı" satırı bilgi içindir.
3. **1983–1993 boşluğu ve seçim yanlılığı.** Coalinga, Morgan Hill, Loma Prieta ve Landers bu epokları boşaltıyor.
   1993 Parkfield hızlanması (deprem gelmedi; bilinen bir "yanlış alarm" örneği) hiçbir kural setinde tabana
   girmiyor. Taban, tanımı gereği "sakin" dönemlerin tabanıdır. Koşulsuz yanlış alarm ölçeği bundan büyük olabilir.
4. **S-7 ile örtüşme.** Aynı bölge ve aynı fiziksel nicelik (sığ asismik kayma). B'nin pencerelerinin çoğu 2013 ve
   2018 epoklarında (2008-10 → 2018-10), yani S-7'nin 2004–2014 dönemiyle büyük ölçüde örtüşüyor. TR-10b, S-7'yi
   bağımsız olarak doğrulamaz ve S-7'nin yeniden açma şartını sağlamaz.
5. **Az blok.** En çok 6, büyük olasılıkla 5 kesim. Yüzdelik bloklu bootstrap kesiklidir. Aralık ancak bir taban
   **ölçeği** verir, kesin bir kuyruk vermez. q99, N ≈ 40'ta en büyük iki değerin ara değeridir.
6. **Küçük örneklem yanlılığı.** N ≈ 40'ta q95 aşağı yanlıdır (§10.4.1).
7. **Arşivin boşluk doldurması.** Sayfaya göre uzun boşlukların ötelenmesi sabit hız varsayımıyla kestirildi. Arşiv
   boşluğu değerle doldurduysa doluluk ve boşluk kuralları bunu göremez; Δv sıfıra çekilir ve taban küçülür.
8. **2007 sonrası işlenmemiş telemetri.** Glitch ve sıfırlama ötelenmeleri kalmış olabilir; tabanı büyütür. B'nin
   2013 ve 2018 pencereleri bu dönemde.
9. **HDR kuralı.** Mekanik anahtar sözcük kuralı yanlış pozitif üretir ("no offset" gibi) ve sayıyı düşürür. Notlar
   sünme davranışını anlatıyor olabilir; bu, seri görülmeden yapılan sınırlı bir körlük bozulmasıdır. Not içeriğindeki
   kayma ve hız ifadeleri kullanılmaz (§6.4).
10. **Yağış ve ayak eğilmesi** düzeltilmez (README uyarısı: X461, XMD1, XTA1, XVA1).
11. **Uç penceresindeki küçük olaylar.** B1 T'de biter. (T, T + 15 g] içindeki M 4,5–5,5 bir olay u(T)'yi etkileyebilir
    ve düşürülmez. B2 yalnız M ≥ 5,5'i dışlar.
12. **"Sakinlik kapalı" satırı yok** (F12). Bu yüzden sakinlik kuralının tabanı ne kadar küçülttüğü ölçülmez.
13. **Büyüklük türleri karışık** (ML, Mw, Md); L(M) Mw için türetildi.
14. **Chihshang karşılaştırılabilirliği zayıf:** bindirme fayı, farklı aletler, 7 y ve 3–4 y pencereler. Uzun pencerenin
    gürültüsü küçük olduğundan karşılaştırma "içinde" yönüne yanlıdır.
15. **Kapı büyük olasılıkla geçmez** (§13). Bu önceden kabul edilir.

## 17. Marmara'ya bağ

- Marmara'ya **doğrudan çeviri yapılmaz.** Marmara'da ≥ 5 yıllık sünme serisi yok (Kumburgaz akustik 2017–2019, 2
  yıl). Orta Marmara fayı denizaltındadır. Nokta ölçerdeki ayak eğilmesi, InSAR'ın km ölçekli ortalaması ve denizaltı
  akustik ölçümü farklı gürültü süreçleridir.
- TR-10b'nin Marmara'ya verdiği yalnız iki şeydir:
  1. **Yanlış alarm ölçeği:** nokta sünme ölçeriyle ölçülen 2 yıllık hız değişiminin depremsiz taban büyüklüğü (mm/yıl
     ve hızın %'si), gelecekte Marmara'da kurulacak bir ölçer ya da yeterince uzun bir InSAR/NISAR serisi (AV-3) için
     bir başvuru ölçeği olarak;
  2. **Chihshang bilgi satırı.**
- Vermedikleri: hiçbir olasılık ya da olasılık çarpanı; Marmara'nın kendi tabanı; CMF için bir alarm eşiği.
  **Mutlak İstanbul deprem olasılığı hiçbir yerde yazılmaz.**

## 18. Maliyet

0 €. Veri USGS'den açık erişimle gelir, katalog SAYIM'ın önbelleğindedir. Tahmini iş yükü: HDR adımı birkaç saat;
kod ve yapay testler 1–2 gün; koşu bir saatin altında.
