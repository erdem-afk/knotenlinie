# TR-10b tasarım ve üstveri sayımı: sünme ölçerlerde depremsiz pencerelerde 2 yıllık sünme hızı değişiminin taban dağılımı

Tarih: 12 Kasım 2026. Durum: TASARIM + ÜSTVERİ SAYIMI (ön kayıt değil). Sınav koşulmadı: hiçbir sünme ölçer veri
dosyasının (DAY, 10MIN, MIC, CL10, PKF_EQ, HDR, HaywardCreep) içeriği okunmadı, hiçbir sünme hızı ya da Δv
hesaplanmadı. Erdem'in 12 Kasım talimatıyla (açık adaylar seçimsiz ve elemesiz ilerletilsin) yapıldı. Kaynak:
`kayit/onkayit/TR-10_SAYIM.md` §6 (olay gerektirmeyen ara ölçüm) ve TR-11'in tasarımı.
Kod: `kayit/turetme/tr10b/tr10b_sayim.py`. Özet: `kayit/turetme/tr10b/tr10b_sayim_ozet.json` (sha256 228b0e01…).
Ham veri depoda değil, scratch'te (`.../scratchpad/tr10b/ham/`; sha256 ilk 16 hane):
- USGS indirme sayfası, TR-10 anlık görüntüsü `74b3eb437b530436` (kod assert eder);
- arşiv README'si `6b1e95c03d3eae82` (35 510 B; biçim belgesi);
- 126 veri bağlantısının HEAD sonuçları `96db292a43299004` (boy, Last-Modified);
- yeni ComCat sorgusu (M ≥ 4,5; 30,5–42,5° K, 128–113° B; 1955-01-01 → 2025-12-31T23:59:59; 1674 deprem)
  `cbd2bc88b726d2c7`.

## 0. Hüküm

**Sınav kurulabilir, ama yalnız bir kural setiyle ve sınırda: kapı SINIRDA.** Kapsam şartıyla (veri penceresi
README listesinin ve OFR 2024-1011 özetinin desteklediği aralıkta) 47 istasyondan 43'ü, 34 ayrı sitede, 11 sabit
epokta 226 istasyon-pencere (210 site-pencere) verir. Aygıt kopması, sıfırlama ve terk kayıtları bunu 206'ya indirir.
Asıl eleyen sakinlik şartıdır. İki kural seti önceden yazıldı; ikisi de sürüyor, hiçbiri elenmedi.
- **A (sabit yarıçaplı, katı):** 22 istasyon-pencere, 19 istasyon, 19 site, 4 fay kesimi. Kapı **GEÇMEZ**; kapsamın üst
  sınırında bile geçmez (31 site-pencere, 25 site).
- **B (kırık boyuna ölçekli):** 42 istasyon-pencere, 23 istasyon, 41 site-pencere, 22 site, 5 fay kesimi. Kapı ana
  kapsamda sınırda geçiyor, katı kapsamda geçmiyor (31 / 18), üst sınırda rahat geçiyor (62 / 29). Hüküm **SINIRDA**.

Kapı ≥ 20 site ve ≥ 40 site-pencere. Bu sayılar üstveriden gelen üst sınırlardır. Veri okununca doluluk ve boşluk
şartları sayıyı düşürür; B'de 2 site-pencerelik kayıp bile "veri yok" demektir. Bağımsız fay kesimi en çok 5; bunların
yarısı Parkfield'da (B: 41'in 21'i), pencerelerin üçte ikisi 2013 ve 2018 epoklarında. Ölçüm ancak "Orta Kaliforniya
sünen kesimlerinde son 15 yılın sakin taban dağılımını" verir. Marmara'ya doğrudan çevrilemez (§7). B seti, A'nın
sayımı görüldükten sonra yazıldı; bu dürüstçe kayda geçer. Hiçbir sünme verisi görülmediği için seçim sonucu
yanlılaştırmaz; ama ön kayıt hangisinin ana olacağını incelemeye bırakmalıdır (§5.4).

## 1. Veri (yalnız sayfa, README ve HEAD)

### 1.1 Kaynak

- İndirme sayfası: `https://earthquake.usgs.gov/monitoring/deformation/data/download.php` (Creepmeter tablosu).
  Atıf: Langbein, Bilham, Snyder, Ericksen 2024, OFR 2024-1011, 10.3133/ofr20241011. Özet (OpenAlex): veri Schulz
  (1989) sonrasından **2020 ortasına** dek; çoğu ölçer otomatik iletiliyor; elle (mikrometre) ölçümlerle
  karşılaştırılıyor; sensör bozulmasında sayısal veri düzeltiliyor; en büyük geçici 2004 Parkfield sonrası.
- Arşiv kökü: `https://escweb.wr.usgs.gov/share/langbein/Archive/CREEP/`, alt dizinler: 10MIN, CL10, DAY, HDR,
  HDR2025, HDRx.tar, MIC, PKF_EQ, PLOTS, README, noise.pdf. Hayward Bilham ölçerleri için ayrıca
  `.../Archive/HaywardCreep/` (`*_merge.jl.gz`; açılmadı).
- **Biçim (sayfa ve README):** ASCII, gzip. Sütunlar: yıl, yılın günü (CL10'da saat ve dakika ondalık olarak),
  kayma (mm; CL10'da sayım). Dördüncü sütun varsa yok sayılır. Sağ yanal pozitif. DAY: mikrometreyle uzlaştırılmış
  günlük; MIC: elle ölçüm (kesinlik 0,05 mm; 0,5 mm'lik okuma hataları olabilir); CL10: işlenmemiş sayım;
  10MIN (2011 notu): "all time", temizlenmiş ve mm'ye ölçeklenmiş. README'ye göre DAY tercih edilir; telemetrisi
  olmayanlarda MIC.
- **README uyarıları:** veri yalnız 2007 ortasına dek "işlenmiş" (glitch, sıfırlama ötelenmesi, mikrometre
  uzlaştırması); ayaklar 2–3 m derinde ve yağışla eğiliyor ("rainfall records" incelenmeli); 2006–2008'de
  DCP/elektronik değişimi ve ölçek değişimi; Hayward'daki 5 telemetrili ölçer bu arşivde değil (Bilham'ın), ama
  sayfada CPP1, CTM1, COZ1, CHP1, CFW1 için 10MIN bağlantısı var. Sayfa: COVID döneminde bakım aksadı, uzun
  boşluklarda ötelenme **sabit hız varsayımıyla** en küçük kareler ile kestirildi.
- README'de istasyon başına güç yasası gürültü kestirimi tablosu var (2004 öncesi; §4.2).

### 1.2 İstasyonlar (sayfa sırası, kuzeyden güneye)

47 istasyon: Calaveras 4, Hayward 10, San Andreas 33. Dosya türleri: H = HDR (Notes), M = MIC, 10 = 10MIN,
D = DAY. "Tele" ve "MIC" README dosya listesindeki aralıklardır (2013 anlık görüntüsü; sayfadaki ilk gözlemle
kırpılmış). "10MIN LM" 10MIN dosyasının Last-Modified tarihidir. 2026 tarihi o dosyanın bugün güncellendiğini
gösterir. A ve B: ana kapsamda (R2) sakin kalan epoklar.

| Kod | Kesim | Enlem, boylam | İlk gözlem (sayfa) | Dosya | Tele (README) | MIC (README) | 10MIN LM | A | B |
|---|---|---|---|---|---|---|---|---|---|
| XSH1 | CAL_Hollister | 36.943, −121.445 | 1971 | H/M/10/D | 1971-06–1997-07 | 1971-06–2013-03 | 2026-11-11 | 2018 | 2013, 2018 |
| SHR2 | CAL_Hollister | 36.943, −121.445 | Apr-86 | M | – | 1985-05–1999-08 | – | – | – |
| HLC1 | CAL_Hollister | 36.857, −121.405 | Apr-70 | M | – | 1970-04–2009-07 | – | – | – |
| HLD1 | CAL_Hollister | 36.842, −121.403 | Apr-70 | M | – | 1970-04–2008-05 | – | – | – |
| CPP1 | HAY | 37.990, −122.356 | Aug. 1995 | H/10 | – | – | 2026-11-11 | 2003 | 2003 |
| CTM1 | HAY | 37.844, −122.227 | Mar. 1997 | H/10 | – | – | 2026-11-11 | 2003 | 2003 |
| COZ1 | HAY | 37.753, −122.150 | Nov. 1996 | H/10 | – | – | 2026-11-11 | 2003 | 2003, 2008, 2013 |
| HWR1 | HAY | 37.680, −122.092 | Apr-68 | M | – | 1969-06–1988-09 | – | – | – |
| HWR2 | HAY | 37.680, −122.092 | Apr-68 | M | – | 1969-06–1995-06 | – | – | – |
| HWE1 | HAY | 37.670, −122.080 | Apr-68 | M | – | 1969-06–1995-04 | – | – | – |
| HWW1 | HAY | 37.670, −122.080 | Apr-68 | M | – | 1969-06–1994-10 | – | – | – |
| HWP1 | HAY | 37.663, −122.074 | Apr-68 | M | – | 1970-05–1993-12 | – | – | – |
| CHP1 | HAY | 37.663, −122.074 | Apr-94 | H/10 | – | – | 2026-11-11 | 2003 | 2003, 2008, 2013 |
| CFW1 | HAY | 37.532, −121.952 | Dec. 1993 | H/10 | – | 1993-12–1994-02 | 2026-11-11 | 2003 | 2003, 2018 |
| SJN1 | SAF_SJB | 36.855, −121.521* | 2004 | H/10 | – | – | 2026-11-11 | 2018 | 2018 |
| XSJ2 | SAF_SJB | 36.836, −121.521 | Jun-69 | H/M/10/D | 1969-06–2006-07 | 2007-02–2010-02 | 2020-07-09 | – | – |
| XSJ3 | SAF_SJB | 36.836, −121.521 | Jan. 2007 | H/M/10/D | 2007-01–2013-07 | 2007-02–2013-03 | 2020-07-09 | 2018 | 2018 |
| XHR1 | SAF_SJB | 36.772, −121.422 | 1970 | H/M/10 | – | – | 2020-07-09 | – | – |
| XHR2 | SAF_SJB | 36.772, −121.422 | Apr-85 | H/M/10/D | 1985-04–2005-06 | 1985-04–2008-05 | 2020-07-09 | – | – |
| XHR3 | SAF_SJB | 36.772, −121.422 | Aug. 2009 | H/M/10/D | 2009-08–2013-07 | 2009-08–2013-03 | 2026-11-11 | 2018 | 2018 |
| CWC3 | SAF_SJB | 36.750, −121.385 | Nov. 1968 | H/M/10/D | 1968-11–2000-12 | 1977-01–2004-01 | 2020-07-09 | – | – |
| CWN1 | SAF_SJB | 36.750, −121.385 | Jun-72 | H/M/10/D | 1972-06–2013-07 | 1972-06–2013-03 | 2023-12-23 | 2018 | 2018 |
| XFL1 | SAF_sunen_orta | 36.665, −121.272 | Apr-73 | M/D | 1973-04–1995-03 | 1973-04–1996-08 | – | – | – |
| XMR1 | SAF_sunen_orta | 36.595, −121.187 | Jun-69 | H/M/10/D | 1969-06–2013-07 | 1969-06–2013-03 | 2026-11-11 | – | – |
| MRW1 | SAF_sunen_orta | 36.585, −121.177 | Sept. 1972 | M | – | 1972-10–2004-10 | – | – | – |
| XDL2 | SAF_sunen_orta | 36.492, −121.078 | 1978 | M | – | 1978-01–2002-02 | – | – | 1998 (MIC) |
| BIT1 | SAF_sunen_orta | 36.398, −120.982 | Jul-79 | M | – | 1979-07–1995-11 | – | – | – |
| XMP1 | SAF_sunen_orta | 36.217, −120.798 | Jun-69 | M | – | 1969-06–1988-08 | – | – | 1978 (MIC) |
| XMP2 | SAF_sunen_orta | 36.217, −120.798 | Jun-69 | M | – | 1969-06–1997-06 | – | – | 1978 (MIC) |
| XSC1 | SAF_sunen_orta | 36.065, −120.628 | Jun-79 | H/M/10/D | 1979-06–2013-07 | 1979-06–2013-03 | 2026-11-11 | – | 2013, 2018 |
| XMM1 | SAF_Parkfield | 35.958, −120.502 | Oct. 1979 | H/M/10/D | 1979-10–2013-07 | 1979-10–2013-02 | 2026-11-11 | 2018 | 2013, 2018 |
| XMBC | SAF_Parkfield | 35.958, −120.502 | Apr-04 | H/M/10/D | 2004-04–2011-06 | 2004-04–2011-01 | 2020-07-09 | Big Creep | Big Creep |
| XMD1 | SAF_Parkfield | 35.943, −120.485 | Jul-86 | H/M/10/D | 1986-09–2013-07 | 1986-07–2013-03 | 2026-11-11 | 2018 | 2013, 2018 |
| XVA1 | SAF_Parkfield | 35.922, −120.462 | Apr-87 | H/M/10/D | 1987-05–2013-07 | 1987-04–2013-03 | 2020-07-09 | 2018 | 2013, 2018 |
| XRSW | SAF_Parkfield | 35.907, −120.460 | May-87 | H/M/10/D | 1987-06–2005-09 | 1987-05–2005-09 | 2020-07-09 | – | – |
| XPK1 | SAF_Parkfield | 35.902, −120.442 | Oct. 1979 | H/M/10/D | 1979-10–2004-09 | 1979-10–2004-09 | 2020-07-09 | – | – |
| XPK2 | SAF_Parkfield | 35.902, −120.442 | Sept. 2004 | H/M/10/D | 2004-09–2013-07 | 2004-09–2013-02 | 2026-11-11 | 2018 | 2013, 2018 |
| XTA1 | SAF_Parkfield | 35.890, −120.427 | Sept. 1985 | H/M/10/D | 1985-12–2013-07 | 1985-09–2012-12 | 2026-11-11 | 2018 | 2013, 2018 |
| TABC | SAF_Parkfield | 35.890, −120.427 | Mar-04 | M/10/D | 2004-04–2013-07 | 2004-03–2012-12 | 2020-07-09 | Big Creep | Big Creep |
| XHSW | SAF_Parkfield | 35.862, −120.420 | Jun-87 | H/M/10/D | 1987-07–2010-07 | 1987-06–2009-12 | 2020-07-09 | – | – |
| WKR1 | SAF_Parkfield | 35.858, −120.392 | 1976 | H/M/10/D | 1976-09–2013-07 | 1977-01–2013-02 | 2026-11-11 | 2018 | 2013, 2018 |
| CRR1 | SAF_Parkfield | 35.835, −120.363 | May-66 | H/M/10/D | 1966-06–2013-07 | 1966-06–2012-11 | 2020-07-09 | 1973, 1978, 2018 | 1973, 1978, 2013, 2018 |
| XGH1 | SAF_Parkfield | 35.820, −120.348 | Jul-69 | H/M/10/D | 1969-07–2013-07 | 1977-02–2012-11 | 2023-06-15 | 1978, 2018 | 1978, 2013, 2018 |
| C461 | SAF_Parkfield | 35.724, −120.282 | Sept. 2004 | 10 | – | – | (bağlantı yanıt vermedi) | – | – |
| X461 | SAF_Parkfield | 35.723, −120.278 | Aug. 1986 | H/M/10/D | 1986-10–2013-07 | 1986-08–2013-02 | 2020-07-09 | 2018 | 2013, 2018 |
| TWR1 | SAF_guney_gecis | 35.597, −120.147 | Nov. 1976 | M/D | 1979-12–1992-02 | 1977-04–2007-06 | – | – | – |
| XPH1 | SAF_guney_gecis | 35.148, −119.692 | Aug. 1977 | M/D | 1977-08–1991-11 | 1977-08–2007-10 | – | – | – |

\* SJN1'in boylamı sayfada 0,0000 yazıyor; uzaklık için XSJ2'nin boylamı kullanıldı (TR-10 ile aynı).

Notlar:
- **Dosya özeti:** 126 bağlantı (HDR 29, MIC 40, 10MIN 31 (biri `HaywardCreep/` yolunda), DAY 26; sayfa TR-10'da 235 sayılmıştı, o sayı
  dilatometre ve gerinim ölçer bağlantılarını da içeriyordu). 10MIN dosyalarının 15'i bugün güncelleniyor
  (Last-Modified 2026-11-11): XSH1, CPP1, CTM1, COZ1, CHP1, CFW1, SJN1, XHR3, XMR1, XSC1, XMM1, XMD1, XPK2, XTA1,
  WKR1. Ötekiler 2020-07-09 tarihli; bu tarih 79 dosyada ortak olan toplu arşiv tarihidir, son gözlem tarihi
  değildir. CWN1 10MIN 2023-12-23'te, XGH1 10MIN 2023-06-15'te durmuş görünüyor. HDRx.tar 2026-09-10 tarihli.
- **Son gözlem** yalnız şu üç kaynaktan sınırlanabildi: README listesi (2013-07'ye dek doğrulanmış), OFR özeti
  ("mid-2020") ve Last-Modified (üst sınır). Veri dosyası açılmadan gerçek son gün ve boşluklar bilinemez.
- **Kırpma:** sınavın kullandığı en son veri günü 2023-10-16'dır (son epok, §2.1). 2024–2026 gözlemleri hiçbir
  yerde kullanılmaz. Okuma sırasında 2023-10-16 sonrası satırlar ayrıştırılmadan atlanır (TR-11 Ek 2 kuralı).

## 2. Kodlanabilir tasarım

### 2.1 Epoklar (önceden sabit takvim, örtüşmez)

- Y ∈ {1973, 1978, …, 2023} (11 epok). T = Y-10-01, menteşe H = (Y−2)-10-01, w0 = (Y−5)-10-01.
- Taban dönemi [w0, H) 3 su yılı, yakın dönem [H, T) 2 su yılı.
- Uç noktaları 1 Ekim'dir, yani kuru mevsimin sonu ve su yılı başı. Üç uç noktası aynı takvim gününe düştüğü için
  durağan yıllık ve altı aylık döngü ölçüden kendiliğinden düşer. Ayak eğilmesinin en az olduğu mevsim de budur.
- Gereken veri aralığı [w0 − 15 g, T + 15 g]. Son epokta T + 2 yıl = 2025-10-01, yani katalog bitişinden
  (2025-12-31) önce. 2026 kör kalır.

### 2.2 Kapsam (veri okunmadan, üç senaryo; kod `kapsam()`)

- **R (katı):** README dosya listesinin DAY/CL10 (telemetri) ve MIC aralıkları, sayfadaki ilk gözlemle kırpılmış.
  10MIN dosyası bugün güncelleniyorsa telemetri aralığının sonu 2025-12-31'e uzar. README'de aralığı olmayan
  etkin 10MIN istasyonunda (Bilham'ın Hayward ölçerleri, SJN1) başlangıç sayfadaki ilk gözlemdir.
- **R2 (ana):** R'ye ek olarak OFR özeti. README anında çalışan (aralığı ≥ 2012'ye ulaşan) ve dosyası 2020-07
  tarihli istasyonlarda aralık 2020-06-30'a uzar. 2020'den sonra durmuş 10MIN dosyasında (CWN1, XGH1) sonu
  Last-Modified tarihidir.
- **U (üst sınır):** sayfadaki ilk gözlemden en geç Last-Modified tarihine. Dosya kendi değişiklik tarihinden
  sonraki veriyi taşıyamaz.
- Pencere, istasyonun tek bir kayıt türü aralığına tümüyle girmelidir. Önce telemetri ("tele") denenir, olmazsa
  elle ölçüm ("man").

### 2.3 Aygıt kayıtları (README'den dondurulmuş liste; kod `K_OLAY`, `K_SON`, `D_OLAY`)

- **K olayları (32):** kopma, yeniden sıfırlama, sensör ya da çubuk değişimi, Parkfield 2004 taşması, çarpma,
  göçük, sahte aralık, güvenilmezlik. Olay [w0 − 30 g, T] içindeyse pencere düşer. Tarih bilinmiyorsa ayın 1'i,
  ay bilinmiyorsa 1 Ocak alınır.
- **Son veren K olayları (8):** terk, kalıcı güvenilmezlik ve kod değişimi (CWC3 2000, XHR2 2004, XHSW 2010,
  XRSW 2005, XFL1 1995, XPK1 2004 → XPK2, XSJ2 2006 → XSJ3, XMBC 2011). Bunlardan sonraki bütün pencereler düşer.
- **D olayları (12):** 2006–2008 DCP ve elektronik değişimi. README'de ölçek ve ötelenme veriliyor. Ana sayımda
  kalır, bilgi satırında düşer. Sayımda etkisi 0, çünkü bu pencereler zaten 2003 San Simeon ve 2004 Parkfield
  yüzünden düşüyor.
- **Big Creep eşleri (XMBC, TABC):** düşük çözünürlüklü ve README'ye göre düzenlenmemiş; ana sayıma girmez.
- **HDR (Notes) dosyaları bu sayımda açılmadı.** Ön kayıtta HDR'nin veri sayılıp sayılmadığı kararlaştırılmalıdır.
  Önerim şu: HDR yalnız seriler açılmadan önce okunsun. 2023-10-16 sonrası notlar yok sayılsın. Yeni K olayları
  "koşu öncesi ek" başlığıyla listeye eklensin. Sayım bu yüzden HDR'yle bir miktar daha düşebilir.

### 2.4 Sakin pencere (istasyon noktasına uzaklık; ComCat, `type = earthquake`, ≤ 2025-12-31)

İki kural seti önceden yazıldı. İkisi de koşuda hesaplanır.

**A (sabit yarıçaplı; NGL kod 2 yarıçapı r = 10^(M/2 − 0,79) km'nin yuvarlanmışı):**
- Ş1: M ≥ 5,0, derinlik ≤ 30 km, ≤ 50 km, zaman [w0 − 2 y, T + 2 y];
- Ş2: M ≥ 6,0, derinlik ≤ 40 km, ≤ 150 km, zaman [w0 − 5 y, T + 2 y];
- Ş3: M ≥ 7,0, derinlik ≤ 70 km, ≤ 500 km, zaman [w0 − 2 y, T].

**B (kırık boyuna ölçekli; A sayımı görüldükten sonra yazıldı):**
- B1, geçmiş ve iç etki: M ≥ 4,5, derinlik ≤ 30 km, uzaklık ≤ max(10 km, 5 L(M)), zaman [w0 − 2 y, T]. L, Wells ve
  Coppersmith doğrultu atımlı kırık boyudur (`tr2_sayim.L_km`): M 5 → 17 km, M 6 → 70 km, M 6,9 → 230 km,
  M 7,3 → 450 km.
- B2, hedef olay öncesi dışlama (TR-10 varyant tanımı): M ≥ 5,5, derinlik ≤ 30 km, ≤ 50 km, zaman (T, T + 2 y].
- B3, uzak büyük olay (dinamik tetikleme): M ≥ 7,0, derinlik ≤ 70 km, ≤ 500 km, zaman [w0, T].

Gerekçe: Mavko (1982) Hollister'de sünme hızındaki birçok aylık değişimi yerel orta büyüklükte depremlere
bağlıyor. Toda ve Stein (2002) 1983 Coalinga'dan sonra Parkfield'da sünmenin yavaşladığını ya da ters döndüğünü
yazıyor (özetler; §6). Yani sünme ölçer bir gerilme ölçerdir ve yakın olayların izini taşır. "T + 2 y" uzantısı
olay öncesi pencereleri tabandan çıkarır. Bunlar TR-10'un olaylı sınavının penceresidir.

### 2.5 Hız değişimi ölçüsü (ana: uç noktası farkı)

- Uç noktası değeri: u(P) = P ± 15 gün aralığındaki geçerli günlük değerlerin medyanı. En az 10 gün gerekir, yoksa
  pencere düşer.
- **Ana ölçü:** Δv = (u(T) − u(H)) / τ₂ − (u(H) − u(w0)) / τ₃, mm/yıl. τ, gerçek gün sayısının 365,25'e
  bölümüdür.
- **Oran ölçüsü:** r = Δv / v₅, burada v₅ = (u(T) − u(w0)) / (τ₂ + τ₃) pencere ortalama hızıdır. r yalnız
  v₅ ≥ 2 mm/yıl olan "sünen" katmanda hesaplanır, yoksa payda sıfıra yakındır.
- **Neden uç noktası:**
  - Sünme büyük ölçüde basamaklı olaylarla birikir (Gittins ve Hawthorne 2022: 18 ölçerde 2120 olay kaydı). Uç
    noktası farkı, olayları ve aradaki yavaş sünmeyi birlikte sayar; tek bir olayın pencere içindeki zamanına
    duyarsızdır.
  - README ve Langbein'ın tablosuna göre gürültü rastgele yürüyüşe yakın (güç yasası indisi 2,0–2,7). Saf
    rastgele yürüyüşte hızın en iyi doğrusal kestiricisi uç noktası farkıdır.
  - Mevsimsel döngü aynı takvim günü sayesinde düşer.
- **Elle ölçüm (MIC) katmanı:** u(P), P'yi çevreleyen iki ölçümün doğrusal ara değeridir. İki ölçümün de P'ye
  uzaklığı ≤ 90 gün olmalıdır. Taban döneminde ≥ 12, yakın dönemde ≥ 8 ölçüm, en uzun aralık ≤ 180 gün.
- **Doluluk (günlük):** taban ve yakın dönemde ayrı ayrı gün sayısı / takvim günü ≥ 0,60. [w0 − 15, T + 15]
  içinde en uzun boşluk ≤ 60 gün. Gerekçe: arşivde uzun boşlukların ötelenmesi sabit hız varsayımıyla kestirildi,
  bu da boşluğu kapsayan pencerede Δv'yi yapay olarak sıfıra çeker.
- **Kaynak sırası:** DAY → 10MIN (günlük medyana indirgenmiş) → MIC. Pencerede doluluk şartını sağlayan ilk kaynak
  kullanılır; bu sıra veri görülmeden sabittir.
- **Bilgi satırı:** TR-11 tipi menteşe modeli. Sabit + eğim + max(0, t − H) + yıllık ve altı aylık sin/cos, D
  olayları sıçrama terimi, 5 × 1,4826 × MAD ile bir kez ayıklama. Basamaklı sünmede kalıntıları ağır kuyrukludur;
  bu yüzden ana ölçü değildir.
- **Yağış:** düzeltilmez (CDEC yağış verisi indirilmez). Yağışla tetiklenen sünme olayları (Roeloffs 2001,
  Schulz 1983) tabanın gerçek parçası sayılır. Bilgi satırı olarak su yılı yağışına göre katman yazılabilir; bu,
  ön kaydın kararıdır.

### 2.6 Bağımsızlık birimi

- **Site:** sayfadaki koordinatları 3 ondalığa dek aynı olan ölçerler. Aynı site ve epokta tek ölçer alınır (en
  erken ilk gözlem, eşitlikte kod sırası). Ana birim site-penceredir. 47 istasyon 34 site eder; 13 eş konumlu ölçer
  vardır.
- **Fay kesimi (blok):** Calaveras-Hollister, Hayward, SAF San Juan Bautista–Cienega (≥ 36,70° K), SAF orta sünen
  (36,00–36,70), SAF Parkfield (35,70–36,00), SAF güney geçiş (< 35,70). Toplam 6.
- **Güven aralıkları:** site bootstrap'ı, B = 2000, tohum 20261112, yüzdelik %90. Kesim bootstrap'ı yalnız bilgi
  satırıdır, çünkü 4–5 blok bir aralık kurmaya yetmez.

### 2.7 Çıktılar

- Site-pencere havuzunda |Δv|'nin medyanı, %90 ve %95 nicelikleri, mm/yıl. %99 yazılmaz (≥ 300 birim yok).
- Sünen katmanda |r|'nin medyanı ve %95'i, yüzde olarak.
- İşaretli Δv'nin medyanı (hızlanma ve yavaşlama simetrisi).
- Kırılımlar: kesim, epok, tele ve man, kural seti (A ve B), kapsam katmanı.
- Bilgi satırları: menteşe modeli, D olayları dışarıda, "Parkfield dışı".
- Bütün nicelikler `numpy.quantile(method="linear")` ile alınır.

## 3. Hüküm sırası ve kuralları (tek anlamlı, otomatik)

Sıra şöyledir: veri kapısı → kod denetimi yapay veriyle (a, b, c-yapay) → pozitif kontrol gerçek veride istasyon
düzeyinde (c-gerçek) → ölçü. Gerçek Δv havuzu ancak ilk iki adım geçtikten sonra hesaplanır ve dosyaya yazılır.

1. **Veri kapısı ("veri yok"):** doluluk, boşluk ve uç noktası şartlarından sonra ana kural setinde < 20 site ya da
   < 40 site-pencere kalırsa hüküm "veri yok" olur. Bu adım hiçbir Δv yazdırmaz; yalnız sayıları yazar.
2. **Kod denetimi.** Eşikler bu belgede yapay veriyle önceden doğrulandı (§3.1).
   - (a) Gürültüsüz doğrusal + menteşe + mevsimsel + pencere içi basamak, tam maskede: |Δv − gerçek| ≤ 0,005 mm/yıl.
     Gerçek gün maskelerinde: hata %99'u ≤ 0,5 mm/yıl.
   - (b) Yapay N0 serileri: rastgele yürüyüş b = 3 mm/yıl^0,5 + beyaz 0,1 mm, gerçek gün maskeleriyle. Seri,
     gerçek dosya biçiminde yazılıp ayrıştırıcıdan geçer. Site-pencere başına ⌈820 / n⌉ gerçekleşme üretilir.
     q95|Δv| / q95_N0 oranı [0,88, 1,12] dışındaysa hüküm "geçersiz (kod)" olur. Payda, aynı üreteçle ayrı
     20 000 çekilişlik tam maske Monte Carlo'sundan alınır.
   - (c-yapay) Pozitif kontrol: yapay seriye max(0, t − H) × 5 mm/yıl eklenir. d = Δv_eklenen − Δv_özgün için
     medyan(d) ∈ [4,90, 5,03] olmalıdır.
   - Başarısızlıkta kod gerçek Δv görülmeden düzeltilir ve "koşu öncesi düzeltme" başlığıyla kayda geçer.
3. **Pozitif kontrol, gerçek veri (c-gerçek):** seçilen site-pencerelerin gerçek serilerine aynı rampa eklenir.
   Seçim: `f"{kod}|{Y}"` dizgesinin SHA-256 sırasında ilk yarı. medyan(d) ∈ [4,90, 5,03] değilse hüküm "geçersiz
   (kod)" olur. Bu adım yalnız d'yi yazar, Δv_özgün'ü yazmaz.
4. **Ana ölçü ve etiket.** q95|Δv| [L, U] yazılır. Eşdeğer rastgele yürüyüş genliği b* = q95 / 1,732 olarak
   hesaplanır; 1,732, b = 1 için tam maskedeki q95|Δv|'dir (§4.2). Aralığın uçları da aynı biçimde çevrilir.
   - b*_L > 4,6 ise "taban README gürültü bandından büyük";
   - b*_U < 2,2 ise "taban README gürültü bandından küçük";
   - öteki durumlarda "taban README gürültü bandında".
   - Bant [2,2, 4,6], README tablosunda indisi n = 2 olan altı istasyonun genlik aralığıdır.
5. **Literatür yerleşimi (§6):** her doğrulanmış iddia için aşım oranı P_c = (|Δv| ≥ |Δv_c| olan site-pencere payı)
   hesaplanır. Sünen katman için aynısı |r| ile yapılır. Aralık site bootstrap'ıyla verilir.
   - P_c'nin üst sınırı < 0,05 ise "tabanın üstünde";
   - alt sınırı > 0,05 ise "tabanın içinde";
   - öteki durumlarda "sınırda".
   - Birincil karşılaştırma |r| ile yapılır, çünkü iddialar farklı hızlı faylardandır. |Δv| bilgi satırıdır.
6. **"Güç yok"** yalnız katman satırlarında verilir: bir katmanda < 20 site-pencere varsa. Ana satırda verilmez.

Hüküm cümlesi biçimi: "TR-10b: [veri yok | geçersiz (kod) | taban README bandından büyük | bandında | küçük];
sakin pencerelerde 2 yıllık sünme hızı değişimi |Δv| site-pencerelerin %5'inde X [L, U] mm/yıl'ı (sünen katmanda
hızın %Y'sini) aşar (site S, site-pencere N, kesim K; kural seti A/B)."

### 3.1 Eşiklerin yapay doğrulaması (bu belgede koşuldu; `tr10b_sayim.py denetim_on`)

| Denetim | Yapay sonuç | Önerilen eşik |
|---|---|---|
| (a) tam maske, mevsimsiz / mevsimli | hata 0 / 0,00045 mm/yıl | ≤ 0,005 |
| (a) %10 eksik gün (1–20 günlük delikler), 495 seri | %99: 0,22; en çok 0,27 mm/yıl | %99 ≤ 0,5 |
| (b) N = 41, 300 tekrar | oran ortalaması 0,956, sd 0,135, aralık [0,56, 1,38] | kullanılmaz (N küçük) |
| (b) N = 820 (≈ 20 gerçekleşme × 41), 100 tekrar | ortalama 1,002, sd 0,033, aralık [0,923, 1,080] | [0,88, 1,12] (±3,6 sd) |
| (c) 5 mm/yıl rampa, 2000 seri | medyan(d) 4,963; %0,5–%99,5 [4,83, 5,07] | medyan ∈ [4,90, 5,03] |

(c)'deki −0,037'lik yanlılık deterministiktir. H ± 15 gün penceresinin ikinci yarısındaki rampa u(H)'yi yaklaşık
0,05 mm yükseltir. Beklenen değer 5 − 0,05/2 − 0,05/3 ≈ 4,96'dır.

## 4. Önceden beyan edilen beklenti

### 4.1 Rakip açıklamalar ve önsel güven (yazarın beyanı)

- Taban README bandından büyük: 0,40. README kestirimleri Coalinga ve 1992–1995 hız değişimlerini modelden
  çıkarmış, yağış olayları da var.
- Bantta: 0,50.
- Küçük: 0,10.

### 4.2 Gürültü modeli N0 (README tablosu; yalnız yapay hesap, `tr10b_sayim.py beklenti`)

README'deki tablo 18 istasyon için güç yasası indisi n (2,00–2,74) ve genlik A (mm/yıl^(n/4); 1,23–8,94) ile seküler
hız veriyor. Tablonun dayanakları:
- 2004 öncesi kestirimdir;
- hakemli değildir; yöntem Langbein 2004'e dayanır (10.1029/2003JB002819, özet: EDM verisinin %30'u rastgele
  yürüyüş, %30'u indis 1–2 güç yasası, gerisi bant geçiren + rastgele yürüyüş ya da güç yasası);
- aynı verinin erken bölümünden türediği için kısmen döngüseldir.

Uç noktası ölçüsüyle ve tam maskeyle (2000 çekiliş/istasyon) beklenti şöyle:

| Büyüklük | Değer |
|---|---|
| Saf rastgele yürüyüş b = 1 mm/yıl^0,5: sd(Δv) (analitik √(1/2 + 1/3) = 0,913) | 0,893 (MC); q95|Δv| = 1,732 |
| n = 2 olan istasyonlar (XMM1, XVA1, XPK1, CRR1, CWC3, XMR1): q95|Δv| | 4,1–8,1 mm/yıl |
| 18 istasyonun eşit ağırlıklı havuzu: medyan / %90 / %95 |Δv| | 2,4 / 9,5 / 14,6 mm/yıl |
| Sünen istasyonlar (v ≥ 2 mm/yıl), |r| medyan / %95 | %26 / %168 |

Havuzun kuyruğunu n > 2,5 olan dört istasyon taşıyor: XSH1 (A 8,94), XMD1, X461 ve XTA1. Bant geçiren bileşen ve
beyaz gürültü dahil değildir; aynı takvim günü kuralı bant geçiren yıllık bileşenin çoğunu siler. Bu sayılar ölçüm
değildir. Koşuda beklenti her site-pencere için gerçek gün maskesiyle yeniden hesaplanır.

**Doğrulanamayan:** README tablosunun hakemli bir kaynağı bulunamadı. Roeloffs 2001 ve Langbein 1999'un tam
metinleri yayıncıda 403 döndü ve atlatılmadı. "noise.pdf" (1,7 KB) indirilmedi; README'ye göre aynı tablonun
biçimli sürümüdür.

### 4.3 Önceden görülen sonuç

Rastgele yürüyüş genliği b ≈ 3 ise sakin taban q95|Δv| ≈ 5 mm/yıl olur. Sünen istasyonların hızı 7–21 mm/yıl
olduğuna göre bu, 2 yıllık hız değişiminin %25–70'i kadar bir taban demektir. Chihshang tipi bir iddia (−8 mm/yıl,
−%36; §6) |r| ölçüsüyle büyük olasılıkla "tabanın içinde" çıkar. Bu önceden kabul edilir.

## 5. Üstveri sayımı

Komut: `python3 -I -B kayit/turetme/tr10b/tr10b_sayim.py say <scratch>/tr10b/ham <cikti.json> <scratch>/tr10/ham`.
Koşu bir dakikadan kısa sürer.

### 5.1 Toplam

| Aşama | İstasyon-pencere | İstasyon | Site-pencere | Site | Kesim |
|---|---|---|---|---|---|
| Kapsam yalnız, R (katı) | 213 | 42 | 197 | 34 | 6 |
| **Kapsam yalnız, R2 (ana)** | **226** | **43** | **210** | **34** | **6** |
| Kapsam yalnız, U (üst sınır) | 328 | 44 | 269 | 34 | 6 |
| R2 + K olayları | 206 | – | – | – | – |
| **A, R2** | **22** | **19** | **22** | **19** | **4** |
| A, R | 16 | 15 | 16 | 15 | 4 |
| A, U | 38 | 30 | 31 | 25 | 5 |
| **B, R2** | **42** | **23** | **41** | **22** | **5** |
| B, R | 32 | 19 | 31 | 18 | 5 |
| B, U | 78 | 35 | 62 | 29 | 6 |

B, R2 kırılımları:
- Kesime göre: Parkfield 21, Hayward 10, SAF orta sünen 4, SAF SJB 4, Calaveras 2, SAF güney geçiş 0.
- Epoğa göre: 1973: 1, 1978: 3, 1998: 1, 2003: 5, 2008: 2, 2013: 13, 2018: 16. 1983, 1988, 1993 ve 2023 boş.
- Türe göre: telemetri 39, elle ölçüm 2.

A, R2 kırılımları:
- Kesime göre: Parkfield 12, Hayward 5, SJB 4, Calaveras 1.
- Epoğa göre: 1973: 1, 1978: 2, 2003: 5, 2018: 14.

### 5.2 Sakinlik ne kadar eliyor (taban: R2 kapsamı + K, 206 istasyon-pencere)

A: kural başına Ş1 127, Ş2 130, Ş3 87 pencere eliyor (örtüşmeli); sakin kalan 22 (−%89). B: sakin kalan 42 (−%80).
"Tek neden": pencereyi yalnız o olay düşürüyorsa.

| Olay (ComCat) | M | A: elediği / tek neden | B: elediği / tek neden |
|---|---|---|---|
| Coyote Lake 1979-08-06 | 5,8 | 12 / 0 | 12 / 0 |
| Livermore 1980-01-24 | 5,8 | 10 / 0 | 10 / 5 |
| Coalinga 1983-05-02 | 6,7 | 36 / 4 | 36 / 7 |
| Morgan Hill 1984-04-24 | 6,2 | 51 / 0 | 14 / 0 |
| Loma Prieta 1989-10-18 | 6,9 | 45 / 0 | 34 / 0 |
| Petrolia 1992-04-25 | 7,2 | 25 / 0 | 15 / 0 |
| Landers 1992-06-28 | 7,3 | 26 / 10 | 25 / 3 |
| Hector Mine 1999-10-16 | 7,1 | 13 / 0 | 13 / 1 |
| San Simeon 2003-12-22 | 6,5 | 39 / 16 | 8 / 2 |
| Parkfield 2004-09-28 | 5,97 | 14 / 0 | 14 / 0 |
| Alum Rock 2007-10-31 | 5,4–5,6 | 6 / 3 | 2 / 2 |
| South Napa 2014-08-24 | 6,02 | 15 / 7 | 6 / 6 |
| Ridgecrest 2019-07-06 | 7,1 | 16 / 10 | 16 / 15 |

Parkfield 2004'ün etkisi küçük görünüyor, çünkü taşma ve tel kopması K olayları Parkfield ölçerlerinin 2003 ve
2008 pencerelerini zaten düşürüyor. 1983–1993 epoklarını Coalinga, Morgan Hill, Loma Prieta ve Landers birlikte
boşaltıyor. 2023 epoğunu tek başına Ridgecrest (Ş3/B3) boşaltıyor; B3 kapatılırsa 9 site-pencere geri gelir.
Bu yüzden 1993 Parkfield hızlanması (Langbein 1999, Roeloffs 2001; ardından 11 yıl deprem gelmedi, yani bir
"yanlış alarm" örneği) hiçbir kural setinde tabana girmiyor.

### 5.3 Tanı: hangi kural ne kadar eliyor (R2; site-pencere / site / kesim)

Bu tablo ön kayıt kuralı değildir; kayıt içindir.

| Değişke | A | B |
|---|---|---|
| Ana | 22 / 19 / 4 | 41 / 22 / 5 |
| Ş1 (B1) kapalı | 39 / 28 / 5 | 111 / 33 / 6 |
| Ş2 (B2) kapalı | 49 / 26 / 6 | 46 / 24 / 5 |
| Ş3 (B3) kapalı | 44 / 23 / 6 | 52 / 22 / 5 |
| Bütün sakinlik kapalı | 191 / 34 / 6 | 191 / 34 / 6 |
| Ş1 M ≥ 4,5 / B1 M ≥ 4,0 | 12 / 12 / 2 | 41 / 22 / 5 |
| Ş1 30 km / B1 3 L | 30 / 24 / 5 | 54 / 25 / 6 |
| B1 10 L | – | 13 / 12 / 3 |
| Ş2 100 km / B1 geçmiş 5 y | 30 / 21 / 5 | 25 / 18 / 5 |
| Ş3 [w0 − 5 y, T + 2 y] / B3 300 km | 3 / 2 / 1 | 52 / 22 / 5 |
| K kapalı; D açık; yalnız telemetri | 22; 22; 22 | 41; 41; 39 |

### 5.4 Kapı

Önerilen kapı: ≥ 20 site ve ≥ 40 site-pencere, ana kapsamda (R2). İstasyon düzeyi (≥ 20 istasyon, ≥ 40
istasyon-pencere) bilgi satırıdır, çünkü eş konumlu ölçerler bağımsız değildir.

Üç kademeli sonuç kuralı:
- **GEÇER:** R2'de ve katı R'de geçer;
- **SINIRDA:** R2'de geçer ama R'de geçmez, ya da R2'de geçmez ama U'da geçer;
- **GEÇMEZ:** U'da da geçmez.

| Kural seti | R | R2 (ana) | U | Kapı |
|---|---|---|---|---|
| A | 15 site / 16 sp | 19 / 22 | 25 / 31 | **GEÇMEZ** |
| B | 18 / 31 | 22 / 41 | 29 / 62 | **SINIRDA** |

B'de istasyon düzeyi 23 istasyon ve 42 istasyon-pencere eder; bu da sınırda geçer.

Gerekçe ve güç:
- q95'i ±%15 duyarlılıkla kestirmek için (b) satırındaki yapay hesap N = 41'de sd 0,135 veriyor. Yani 40
  site-pencere bir taban **ölçeği** verir, kesin bir kuyruk vermez.
- Aralık TR-11'in (q95 aralığı ±%15) yaklaşık iki katı geniş olur.
- 40'ın altında bir q95, en büyük 2 değere bağlı kalır.

## 6. Literatür karşılaştırması: iskelet tablo (yalnız özetten ya da tam metinden doğrulananlar)

| İddia | Olay | Mekanizma | Bildirilen değişim | Δv (mm/yıl) / r | Doğrulama | TR-10b'ye çevrilebilir mi |
|---|---|---|---|---|---|---|
| Chihshang sünme ölçerleri, Lee vd. 2005, 10.1016/j.crte.2005.04.018 | 2003 Chengkung Mw 6,6–6,8 | bindirme (kısalma) | 1990–1997 ortalaması 22 mm/yıl (yüzey ölçümü) → 2000–2003 ortalaması 14 mm/yıl (sünme ölçeri); yıllık açık 1999 %18,2, 2000 %36,4, 2001 %43,2, sonra %36,4 | −8 / −%36 | **Tam metin** (açık PDF, s. 2–3) | Kısmen: farklı alet dönemleri, pencereler 7 y ile 3–4 y (bizim 3 + 2 değil); daha uzun pencere gürültüsü daha küçük olduğundan karşılaştırma "içinde" yönüne yanlı |
| Chihshang, Lee vd. 2003, 10.1029/2003JB002394 | (2003 öncesi) | bindirme | "son birkaç yılda yıllık sünme hızında belirgin azalma"; yağış mevsiminde kayma (Nisan–Ekim) | sayı yok | Özet | Hayır (büyüklük yok; tam metin 403) |
| Chihshang 2022 öncesi yavaşlama | 2022 Chihshang Mw 6,9–7,0, Yuli 6,7 | bindirme | – | – | **Bulunamadı** (OpenAlex; Ishimaru 2025 yalnız Coulomb etkileşimi) | Hayır |
| Parkfield 1993 hızlanması, Langbein vd. 1999, 10.1029/1999GL900557; Roeloffs 2001, 10.1029/2001JB000352 | Deprem yok (2004 olayı 11 yıl sonra): yanlış alarm örneği | doğrultu atımlı | 1993'te başlayan ve ≥ 5 yıl süren hız artışı; dört ölçerde daha yüksek hız; CRR1'de tektonik, ötekilerde yağış dışlanamıyor | sayı yok | Özet | Büyüklük yok; ayrıca bu pencereler A ve B'de tabana girmiyor (§5.2) |
| Parkfield 2004 öncesi, Langbein vd. 2005, 10.1785/gssrl.76.1.10; Bakun vd. 2005, 10.1038/nature04067 | 2004 Parkfield Mw 6,0 | doğrultu atımlı | özette öncül sünme ifadesi yok; Bakun 2005'in özeti OpenAlex'te yok | – | Doğrulanamadı | Hayır |
| Coyote Lake 1979 öncesi 3 yıllık sünme gecikmesi, Mavko 1982, 10.1029/JB087iB09p07807 | 1979 Coyote Lake ML 5,8 | doğrultu atımlı | gecikme, 1974 Thanksgiving (Busch fayı) depreminin doğrudan sonucu olarak modellenmiş, yani öncül değil | sayı yok | Özet | Hayır (büyüklük yok) |
| Burford 1988, 10.1007/BF00879008 | yerel orta depremler | doğrultu atımlı | başlık: orta depremlerden önce sünme hızında gecikmeler | – | Özet yok | Hayır |
| Thurber 1996, 10.1038/380425a0 | küçük-orta depremler | doğrultu atımlı | başlık: depremlerden önce sünme olayları (saat-gün ölçeği) | – | Özet yok | Hayır (zaman ölçeği farklı) |
| Coalinga 1983 → Parkfield, Toda ve Stein 2002, 10.1029/2001JB000172 | olay sonrası | – | Parkfield'dan güneye sünme yavaşladı ya da ters döndü; 1991'de yeniden başladı | sayı yok | Özet | Olay sonrası; öncül değil, sakinlik gerekçesi |
| Coalinga öncesi Ocak 1983 hızlanması, Roeloffs 2001 | 1983 Coalinga | – | "büyük olasılıkla yağışla tetiklendi, tektonik değil" | – | Özet | Karşı örnek |
| Aceh, Salman 2026 (not JG-2) | 2013 Mw 6,1 | doğrultu atımlı | 2007–2010'dan 2017–2023'e ≈ −%60; uzak tetikleme ve postsismik | r ≈ −0,6 | Özet | Kısmen (InSAR, 7–13 yıl arası; öncül iddiası değil) |

Okuma: doğrulanmış ve sayılı tek öncül iddia Chihshang 2003'tür (−8 mm/yıl, −%36). O da bindirme fayında, farklı
alet dönemlerinde ve farklı pencere uzunluklarında ölçülmüş. Doğrultu atımlı kıta faylarında sayılı, yıl ölçekli
bir öncül sünme hızı değişimi iddiası bulunamadı. Bu, TR-12'deki GNSS bulgusunun sünmedeki karşılığıdır. Tablonun
asıl ürünü bu yüzden bir yerleştirme değil, bir eşik olur: bir iddia, "|r| > tabanın %95'i" olmadıkça bu ölçümle
ayırt edilemez.

## 7. Marmara'ya bağ

- **Marmara'da ≥ 5 yıllık sünme serisi yok.** Kumburgaz akustik ölçümü 2017–2019 (Yamamoto 2019), yani 2 yıl.
  İzmit FLATSIM InSAR 2016–2021, ama postsismik ve karada. İsmetpaşa (Marmara değil) 2014+ sünme ölçeri ve
  seyrek duvar ölçümleri var. Orta Marmara fayı denizaltında; InSAR görmez. Bu ölçüm Marmara'ya **doğrudan
  çevrilemez**.
- **Ne verir:**
  1. Sünen doğrultu atımlı faylarda, nokta sünme ölçerle ölçülen 2 yıllık hız değişiminin depremsiz taban ölçeği
     (mm/yıl ve hızın %'si).
  2. Gelecekte Marmara'da kurulacak bir sünme ölçer ya da yeterince uzun bir InSAR/NISAR serisi (AV-3: İzmit ve
     Ganos karada) için "bundan küçük değişim alarm sayılmaz" eşiği.
  3. Yayımlanmış sünme öncülü iddialarının bu ölçeğe göre ayırt edilebilir olup olmadığı.
- **Ne vermez:**
  - Hiçbir olasılık ya da olasılık çarpanı (S-7 ve TK-E1 ile aynı sınır);
  - Marmara'nın kendi tabanı. Nokta ölçerdeki ayak eğilmesi, InSAR'ın km ölçekli ortalaması ve denizaltı akustik
    ölçümü farklı gürültü süreçleridir.
  - CMF için bir alarm eşiği;
  - TR-10'un olaylı sınavını yeniden açma şartı.
- Mutlak İstanbul deprem olasılığı yazılmaz.

## 8. En büyük üç risk

1. **Sayı sınırda ve kural setine bağlı.** A 22, B 41 site-pencere veriyor. Kuralların makul değişkeleri 3 ile
   111 arasında gidip geliyor. Doluluk, boşluk (≤ 60 gün) ve HDR notları sayıyı veri okununca kesin düşürür. B'de
   iki pencerelik kayıp kapıyı kapatır. Sakin pencere seçimi tabanı aşağı da çekebilir: en çok kaymış dönemler
   (1983–1993, büyük olaylar sonrası) tümüyle dışarıda. Önlem: kapı veri kapısında yeniden uygulanır, "veri yok"
   kuralı otomatiktir, sakinlik kapalı değişkesi bilgi satırı olarak yazılır.
2. **Aygıt ve çevre yapıntıları ölçünün kendisinden büyük olabilir.** Arşivde şunlar var:
   - yağışla ayak eğilmesi (X461, XMD1, XTA1, XVA1 için README uyarısı);
   - kalibrasyon kayması (XGH1, XTA1, XMM1);
   - sabit hız varsayımıyla kapatılmış boşluk ötelenmeleri (ilki tabanı büyütür, ikincisi küçültür);
   - 2007 sonrası "işlenmemiş" telemetri;
   - Bilham'ın Hayward ölçerlerinin (B'nin dörtte biri) ayrı işleme zinciri.
   - Ayrıca README gürültü tablosu aynı verinin 2004 öncesinden ve hız değişimleri modelden çıkarılarak
     kestirildi; N0 bu yüzden döngüsel ve muhtemelen küçük.
   - Önlem: K/D listeleri, boşluk kuralı, aynı takvim günü uç noktaları, D açık bilgi satırı, tele/man kırılımı.
3. **Bağımsızlık ve temsil.** Bütün birimler 4–5 fay kesiminde. Parkfield yarıya yakın, Hayward dörtte bir.
   Komşu ölçerler aynı yağış ve aynı yerel olaylardan etkilenir; etkin bağımsız birim site sayısından çok daha az
   olabilir. Site bootstrap'ı aralığı daraltır, kesim bootstrap'ı ise 5 blokla anlamsızdır. Sonuç "Orta Kaliforniya,
   ağırlıkla 2008–2018" tabanıdır.

## 9. Defterle örtüşme (`kayit.py ara sünme`, `S-7`, `AV-3`)

- **S-7 (ayırt edilemez):** K. Kaliforniya 2004–2014, tekrarlayan depremlerle ölçülen asismik geçicilerin bilgi
  kazancı −0,06 ± 0,12 nat (N 30).
  - TR-10b aynı bölgede ve aynı fiziksel nicelikte (sığ asismik kayma). B'nin 29/41 site-penceresi 2013 ve 2018
    epoklarında (2008-10 → 2018-10), yani S-7 dönemiyle (2004–2014) büyük ölçüde örtüşüyor.
  - TR-10b bir olasılık terimi sınamaz, yalnız yanlış alarm tabanını ölçer. S-7'nin yeniden açma şartını ("farklı
    bölge ya da daha uzun katalogda yeni bağımsız doğrulama seti") **sağlamaz**.
  - İki sonuç aynı veri bölgesinden geldiği için birbirini bağımsız olarak doğrulamaz.
- **AV-3 (aday, NISAR ≥ 1,5 yıl bekleniyor):** TR-10b, AV-3'ün gelecekteki İzmit/Ganos serisi için ölçek önerir.
  Ama alet farkı yüzünden eşik doğrudan aktarılmaz (§7). AV-3'ün yeniden açma şartını değiştirmez.
- **TR-10 (güç yok, K 17):** aynı arşiv. TR-10b'nin sakin pencereleri, TR-10'un olay pencerelerinin tümleyenidir.
  B2 kuralı, TR-10 varyant tanımının olay öncesi pencerelerini (M ≥ 5,5, ≤ 50 km, 2 yıl) tabandan çıkarır.
  TR-10b, TR-10'u yeniden açmaz.
- **TR-11 / TR-12:** aynı mantığın GNSS karşılığı. TR-12 GNSS'te sayılı öncül iddia bulamamıştı; burada da
  doğrultu atımlı faylarda yok (§6).
- **DK-5 (güç yok):** aynı sünen kesim evreni.
- **TK-E1, FA-6 (elendi):** aynı mekanizma ailesi; S-7 gerekçesi geçerli.
- **S-3:** sünme haritaları; örtüşme yok (uzamsal soru).

## 10. Körlük beyanı ve metin–kod notları

**Körlük:**
- Okunanlar: indirme sayfası (TR-10 anlık görüntüsü) ve README. Dizin listeleri yalnız dosya adları için alındı.
- 126 veri bağlantısına yalnız HEAD isteği yapıldı. Hiçbir veri dosyası, HDR, HDRx.tar, noise.pdf, PLOTS ya da
  HaywardCreep dosyası indirilmedi.
- ComCat sorgusu `tr2_sayim.sorgu` ile yapıldı (bitiş ≤ 2025-12-31T23:59:59 assert edilir). Olay tarihleri kodda
  ayrıca assert edilir.
- Marmara verisi indirilmedi.
- Lee 2005'in açık PDF'i okundu. Wiley tam metinleri 403 döndü ve atlatılmadı.

**Metin–kod notları (ön kayıtta kod bağlayıcı olacaksa listelenmeli):**
- Site, koordinatın 3 ondalık yuvarlamasıdır.
- 29 Şubat'tan yıl kaydırmada 28 Şubat alınır.
- B1'de L(M) ComCat büyüklüğüyle (ML, Mw, Md karışık) hesaplanır.
- Derinlik süzgeci ComCat derinliğine uygulanır.
- Beklenti tablosu yalnız 2003 epoğunun gün sayısıyla ve tam maskeyle hesaplandı.
- `kapsam()` R2'de "2020-07-09 = toplu arşiv tarihi" okumasını kullanır.
- C461 bağlantısı (`HaywardCreep/10MIN/c461.10min.gz`) HEAD'e yanıt vermedi.
- XSC1 ve BIT1'in README aralıkları kurulumdan (1979) önce başlıyor; sayfadaki ilk gözlemle kırpıldı.

## 11. Sonraki adım

Bu bir sayımdır, ön kayıt değil. Ön kayıt sırası:
1. Kural seti A/B kararı ya da ikisinin de bağlayıcı yazılması.
2. HDR kuralı.
3. Bölüm 2–3'ün aynen alınması.
4. Bağımsız inceleme ve dondurma.
5. Kod yalnız yapay serilerle yazılır; dosya biçimi README'den alınır, gerçek dosya açılmaz.
6. Kod incelemesi.
7. İndirme. 2023-10-16 sonrası satırlar ayrıştırılmadan atlanır.
8. Veri kapısı, kod denetimi, tek koşu.

Kapı SINIRDA olduğundan "veri yok" sonucu yüksek olasılıktır. Bu önceden kabul edilir.
