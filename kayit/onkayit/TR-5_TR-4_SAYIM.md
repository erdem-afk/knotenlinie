# TR-5 ve TR-4 tasarım ve üstveri sayımı: ortam gürültüsüyle dv/v, küresel öncül sınavı ve Marmara gürültü tabanı

12 Kasım 2026. Durum: tasarım + 0 € üstveri sayımı. Sınav koşulmadı; dalga formu indirilmedi. Yalnız yedi küçük
erişim denemesi yapıldı, içerikleri okunmadı ve silindi (bölüm 4.1). 2026 tarihli deprem verisi sorgulanmadı.
Katalog olarak hazır ComCat dosyaları kullanıldı (bitiş 2025-12-31). Erişimi reddedilen ya da bozuk servisler
atlatılmadı. Betikler `kayit/turetme/tr5/` altında: `ustveri_indir.py` (FDSN istasyon üstverisi),
`sayim_ustveri.py` (TR-5 sayımı), `kullanilabilirlik.py` (availability servisinden doluluk), `tr4_sayim.py` (TR-4).
Talimat: Erdem, 12 Kasım ("tüm açık ihtimalleri götür, seçim yapmadan ilerlet, elemeyelim"). Bu belge adayları
elemez. Yalnız sayıları ve kapı durumunu verir; karar kök oturumundur.

## Hüküm

**TR-5'in ana tasarımı kapıyı geçmiyor.** Ana tasarım: M ≥ 6,5, derinlik ≤ 30 km, 2000–2023 olayları; olaydan önce
5 yıl kesintisiz kayıtlı açık geniş bant istasyonlar; 100 km içinde en az 2 yer; temiz pencere. Bu kurallarla
üstveriden **K = 8 bağımsız küme** çıkıyor. Şart 1 yere gevşetilirse K = 15 oluyor. Kapı K ≥ 20 olduğu için iki
durumda da sonuç **GEÇMEZ**. Yerinde plasebo kümesi n ≥ 2 için 0, n ≥ 1 için 5.

Darboğaz TR-1 ve TR-11'deki ile aynı. 627 olayın 466'sında, 100 km içinde olay anında çalışan açık BH/HH istasyonu
yok: Japonya'da 29 olay, ayrıca Pasifik adaları, Endonezya ve Orta Amerika. İstasyonu olan 46 olay da temiz pencere
şartında 8'e iniyor; yalnız M ≥ 6 öncül/komşu kuralı bile 46'yı 13'e indiriyor.

Bilgi değişkesi: hedef eşiği M ≥ 6,0'a inerse kapı üstveride geçiyor. 5 yıllık tabanla K 50 (plasebo kümesi 17),
3 yıllık tabanla K 77 (plasebo 41). Ama gerçek veri doluluğu ölçülemedi. EarthScope availability servisi kapatılmış;
KOERI'nin servisi eksik raporluyor. TR-1 ve TR-11'deki 3–5 kat küçülme burada da olursa K 10–26 aralığına düşer.
Bu yüzden değişke **SINIRDA**. Ayrıca bir tasarım değişikliğidir (hedef "büyük deprem" olmaktan çıkar); karar kök
oturumundur.

**Ek 1 (doluluk yoklaması, 12 Kasım):** M ≥ 6,0 değişkesinde doluluğu doğrulanmış sayım, 3 yıllık taban ve n ≥ 1
ile K 37, plasebo kümesi 20; G1 ve G2 **GEÇTİ**. 5 yıllık taban ve n ≥ 1 ile K 25, G1 geçti, G2 (plasebo 6) **GEÇMEDİ**.
n ≥ 2 iki tabanda da GEÇMEDİ (K 8 ve 11). TR-4'te ana kuralla epok başına en çok 10 dolu KO istasyonu var; 24
istasyonun 6'sı süre sınırı yüzünden yoklanamadı. Kapı **doğrulanamadı (SINIRDA)**; gevşek kuralla geçiyor.

**TR-4'ün veri kapısı üstveride geçiyor, ama doluluk doğrulanamadığı için SINIRDA.** KO ağının 24 istasyonu
2012–2023 epoklarında sakin, 5 yıllık, örtüşmeyen 50 istasyon-penceresi veriyor (epok başına 5–22 istasyon). 6G
ağının 26 istasyonu üstveride var, ama deneme isteği 204 döndü, yani veri yok. KOERI tek akış indirme hızı
≈ 40 KB/s ölçüldü (tek deneme). Bu hız değişmezse TR-4'ün indirmesi kısaltılmış biçimde bile haftalar sürer.

Maliyet: tek koşu Hetzner'de kabaca 10–40 € tutar, 50 €'yu aşması beklenmiyor (fiyatlar doğrulanamadı). Asıl sınır
süre ve KOERI bant genişliği. Literatürde yıl ölçekli pasif dv/v öncülü için doğrulanmış bir etki büyüklüğü yok
(Wenchuan 2008 serisinde "öncül değişim yok"). Beklenen sonuç H0'dır.

## 1. Soru ve neyi ölçmediği

**TR-5.** Büyük sığ depremlerden önceki son yılda dv/v, kendi tabanına göre, aynı epoktaki depremsiz kontrol
yerlerinden daha çok mu değişiyor? Bu bir yanlış alarm oranı ya da olasılık iddiası değildir. Olumlu bir sonuç
yalnız ileriye dönük yeni bir ön kaydın açılma şartıdır. dv/v en iyi durumda gerilme **değişimini** ölçer,
kırılmaya uzaklığı ölçmez (`dvv_sismik_hiz.md` S2).

**TR-4.** Marmara'da depremsiz pencerelerde aynı Δ ölçüsünün dağılımı nedir? Yani belli büyüklükte bir dv/v
değişimi depremsiz dönemde ne sıklıkla görülür? Bu, TR-11'in GNSS için yaptığının sismik karşılığıdır. Sonuç bir
ölçüm sınırı cümlesidir: "Marmara'da yıl ölçekli dv/v alarmı, %5 yanlış alarm düzeyinde X %'den küçük değişimi
göremez." Mutlak İstanbul deprem olasılığı yazılmaz.

## 2. TR-5 tasarımı (kodlanabilir tanımlar)

**2.1 Hedef olaylar.** ComCat, `type = earthquake`, M ≥ 6,5, derinlik ≤ 30 km, 2000-01-01 ile 2023-12-31 arası
(T + 2 yıllık kontrol şartı 2025 sonunda kapanan katalog yüzünden). T, olay günüdür. Bilgi değişkeleri: derinlik
≤ 40 km; T ≤ 2025 (kontrol şartı kısalır); M ≥ 6,0.

**2.2 İstasyon uygunluğu.** BHZ ya da HHZ kanalı, ≥ 10 örnek/sn, açık (merkezin `includerestricted=false`
listesinde). Kanal epokları 30 günden kısa boşluklar birleştirilerek tek aralık sayılır; [T − 5 yıl, T − 1 g]
kesintisiz kapsanmalıdır. Olay dış merkezine uzaklık R = 100 km (bilgi: 50 km). 1 km içindeki istasyonlar tek yer
sayılır. Uzaklık sırasıyla en yakın en çok 3 yer alınır. Ana şart ≥ 2 yerdir, ≥ 1 ve ≥ 3 bilgi satırıdır. Koşuda
doluluk şartı da gerekir: taban ve son yıl için ayrı ayrı ≥ 0,60 gün doluluğu. Bu şart sayımda uygulanamadı
(bölüm 4.3).

**2.3 Yöntem.** Ana yöntem, tek istasyon bileşenler arası çapraz korelasyondur (SC: ZE, ZN, EN). Hobiger 2014'e göre
SC yüksek frekansta, istasyonlar arası CC ise 0,5 Hz altında en iyi sonucu veriyor (özetten doğrulandı). Tek istasyon
yöntemi, olay başına çift gerektirmediği için sayımı büyütür.
- Bant 0,5–2 Hz. Koda gecikme penceresi ±(10–40) s. Ön işlem: 20 sps'e indirme, tepki giderme yok (oran ölçüsü),
  1 bitlik normalizasyon yerine spektral beyazlatma + 1 saatlik pencere, saat başı CCF, günlük yığın.
- Bilgi bandı 0,2–0,5 Hz: 60 km'den yakın istasyon çiftlerinde CC. Meier 2010'a göre ölçüm ancak 60 km çift
  uzaklığına kadar mümkün (özetten doğrulandı).
- dv/v: germe (stretching) yöntemi, 10 günlük kayan yığınlar. Referans, taban penceresinin ortalama CCF'sidir.
  Korelasyon katsayısı < 0,5 olan günler atılır. Üç bileşen çiftinin medyanı alınır.

**2.4 Ölçü Δ (istasyon başına).** Δ = ort[T − 365 g, T − 7 g] − ort[T − 5 yıl, T − 365 g), yüzde cinsinden. İki
pencere de tam yıl uzunluğunda olduğu için durağan mevsimsel döngü ortalamada kendiliğinden düşer. Boşluk varsa
taban yıllarının ay ortalamalarından kurulan klimatoloji önce çıkarılır. Olay ölçüsü S = medyan_i |Δ_i|'dir (iki
yanlı; işaret önceden bilinmiyor). Bilgi satırları: işaretli medyan Δ (dilatans düşüş öngörür); son 2 yıl/önceki 3
yıl; istasyonun kendi taban artığıyla ölçeklenmiş z = Δ/σ_i.

**2.5 Temiz pencere (olay dış merkezine göre, [T − 7 yıl, T)).** Olayın kendisi dışında:
- Ş1: 150 km içinde M ≥ 6,0, derinlik ≤ 40 km deprem yok.
- Ş2: 500 km içinde M ≥ 7,0, derinlik ≤ 70 km deprem yok.
- Ş3: 1000 km içinde M ≥ 8,0 deprem yok.

7 yıl, 5 yıllık taban ile 2 yıllık iyileşme payıdır: Parkfield'da düşüş 3 yıldan uzun sürdü (Brenguier 2008);
California'da on yıllık ard-sismik yanıt var (Clements ve Denolle 2023). Gün çözünürlüğü yüzünden aynı gün olan öncü
olaylar kurala girmez. Örneğin Kahramanmaraş'ın 3 olayı tek kümede sayılır.

**2.6 Kontrol (aynı epok, depremsiz yer).** Aday merkezler başka M ≥ 6,5 (derinlik ≤ 40 km, 1976–2025) olayların
dış merkezleridir; 25 km içinde tekilleştirilmiş 1161 merkez var. Sıralama SHA-256(olay kimliği | aday kimliği)
ile yapılır. Şartlar:
- (a) olaydan ≥ 600 km uzak;
- (b) [T − 7 yıl, T + 2 yıl] aralığında Ş1–Ş3 sağlanıyor;
- (c) olayla aynı R ve n kuralı;
- (d) hiçbir kontrol istasyonu olaya 600 km'den yakın değil;
- (e) seçilen kontroller birbirinden ≥ 150 km uzak.

İlk 10 kontrol alınır; en az 5 gerekir. Olay puanı r, kontrollerin S_olay'dan küçük olma oranıdır (eşitlikte 0,5).

**2.7 Bağımsızlık birimi.** TR-1 ile aynıdır. İki olay aynı kümededir, eğer dış merkezleri 300 km'den yakın ve
tarihleri 1 yıldan yakınsa, ya da ortak istasyonları varken pencereleri 5 yıldan yakınsa. K, bağlı bileşen
sayısıdır; küme puanı kümedeki r'lerin ortalamasıdır.

**2.8 Hüküm satırı (TR-1 sürüm 2 ruhuyla; tek, sıralı, otomatik).**
1. **Güç kapısı.** K < 20 ise hüküm "güç yok" olur. K ≥ 20 ise ölçülebilir en küçük etki şöyle yazılır:
   r̄_min = 0,5 + 2,49 × 0,316/√K.
2. **Negatif kontrol.** Her olayın ilk kontrolü sahte olaydır. Ortalamasının iki yanlı %95 aralığı 0,5'i içermezse
   hüküm "geçersiz" olur.
3. **Yerinde plasebo.** Epok T − 5 yıldır; istasyonlar [T − 10 yıl, T) kesintisiz ve [T − 12 yıl, T) sakin olmalıdır.
   Plasebo kümesi < 10 ise H1 ilan edilemez; tabanı > 0,5 ise "ayırt edilemez (bölge yanlılığı)" olur.
4. **Duyarlılık (pozitif kontrol).** Kontrollerin son yılına −0,05 / −0,1 / −0,2 % basamak eklenir. Pratikte bu, CCF
   germe ile yapay gecikme vermektir; dv/v serisine doğrudan eklemek bilgi satırıdır. −0,1 %'de sahte ortalama
   < 0,75 ise ölçü kör sayılır ve hüküm "güç yok" olur.
5. **Hüküm.** H1: alt sınır > 0,5 ve 3. adım engel değil. H0: üst sınır < 0,60. Öteki durumlarda "ayırt edilemez".

**2.9 Mevsimsel ve hidrolojik önlemler.** Sırasıyla:
1. Tam yıl pencereleri ve klimatoloji çıkarma (2.4).
2. Aynı epok kontrolleri. Küresel iklim yılı ortaktır, ama yerel kuraklık ortak değildir.
3. Yerinde plasebo. Yere özgü çok yıllı eğilimi yakalar.
4. Bilgi satırı: ERA5 yağışından difüzyon modeli (Clements ve Denolle 2023 türü) ve sıcaklık gecikmeli regresyonu
   çıkarıldıktan sonra Δ.
5. Bilgi satırı: 0,2–0,5 Hz ve 20–60 s gecikmeyle daha derine duyarlı ölçü.
6. Volkanik yerler bilgi satırında dışarıda bırakılır. Kīlauea'da püskürmeden önceki 10 günde hız düşüşü var
   (Donaldson 2019, özetten); ana örneklemde 2018 Hawaii olayı bu türdendir.

Çok yıllı hidroloji mevsimselden büyük olabilir. Oklahoma'da kuraklık ve yeniden beslenme toplam değişime baskın
(Zhang 2023, nitel; genlik özette yok). Bu yüzden 1–4 numaralı önlemler riski azaltır ama sıfırlamaz (risk 2).

## 3. TR-4 tasarımı (Marmara gürültü tabanı)

**3.1 Veri.** Kutu 40,0–41,6° K, 26,5–30,5° D; KO ağı, BHZ/HHZ (KO'da çoğunlukla BH 50 sps ve HH 100 sps;
koşuda BH). Seri 2011-01-01'de başlar ve 2025-12-31'de kesin olarak biter. 2026 dalga formu kullanılmaz, çünkü
kosismik düşüşler 2026 depremlerini sızdırır ve 2026 kataloğu kördür. Marmara GNSS'inin 2017+ körlüğü (VE-1) sismik
dalga formunu kapsamaz.

**3.2 Pencereler.** T ∈ {2012-01-01, …, 2023-01-01}, yıllık. Pencere [T − 5 yıl, T). Ölçü TR-5'teki Δ'dır.
İstasyon konumuna göre sakinlik:
- [T − 7 yıl, T + 2 yıl) içinde 150 km'de M ≥ 6,0 (derinlik ≤ 40 km) yok;
- 300 km'de M ≥ 7,0 yok (sıkı değişke 500 km; Samos 2020 M7,0, merkeze 355 km).

T + 2 yıl şartı, pencereyi Nisan 2025 M6,2'nin olay öncesi penceresinden ayırır. 2019 Silivri (Mw ≈ 5,8) eşik
altındadır ve pencerelerde kalır; bilgi satırında o tarih çevresi ayrıca işaretlenir. Olay penceresi satırları
(sınav değil, N = 1–2, bilgi): [2014-09-26, 2019-09-25] ve [2020-04-23, 2025-04-22].

**3.3 Çıktılar.** Medyan ile %90, %95 ve %99 |Δ|. Güven aralığı istasyon ve epok blok bootstrap'ıyla verilir.
Bölgesel ortak mod (sıcaklık, yağış) istasyonları birbirine bağladığı için bağımsız birim istasyon değil **epoktur**.
Bu yüzden aralık geniş olacaktır. Çeviri, TR-11'deki gibi alt sınır etiketiyle yazılır: Hillers 2014'ün sığ
duyarlılığıyla (gerilme ≈ 0,5 MPa⁻¹) q95 → "tespit edilebilir en küçük gerilme değişimi".

**3.4 Veri kapısı.** En az 10 KO istasyonunda, en az 2 örtüşmeyen epokta (örneğin T = 2017 ve T = 2023), taban ve
son yıl doluluğu ayrı ayrı ≥ 0,60 olmalıdır. Sağlanmazsa hüküm "veri yok" olur.

## 4. Üstveri sayımı

### 4.1 Servis erişimi (12 Kasım 2026)

| Servis | Durum |
|---|---|
| EarthScope (IRIS) station | `service.iris.edu` 307 ile `service.earthscope.org`'a yönlendiriyor, 200. `includerestricted` destekleniyor (21 662'ye karşı 22 180 satır) |
| EarthScope fedcatalog | 200; 19 merkez (AUSPASS, BGR, EPOSFR, GEOFON, ICGC, IGN, INGV, IPGP, IRISDMC, KOERI, LMU, NCEDC, NIEP, NOA, ORFEUS, SCEDC, SED, UIB-NORSAR, USPSC); 66 787 BHZ/HHZ kanal epoğu, 10,2 MB, 4 sn. `includerestricted` dikkate alınmıyor, bu yüzden açıklık merkezlerden ayrıca sorgulandı |
| EarthScope availability | **404, "This service has been retired"**. IRISDMC istasyonları için gerçek doluluk ölçülemez |
| EarthScope dataselect | 200. IU.ANMO.00.BHZ 1 gün: 1,96 MB, 0,83 sn |
| GEOFON, ORFEUS, NOA, BGR, EPOSFR, INGV, IPGP, LMU, NIEP, SED, UIB-NORSAR, USPSC, ICGC, IGN, AUSPASS, KIT, BGS, NRCAN station | 200 |
| NCEDC, SCEDC, GeoNet | station 200. `includerestricted` parametresine 400 döndü; açık sayıldı (açık arşivler, denetlenmedi) |
| KOERI station | 200 (http ve https). `includerestricted=true` bir kez 503 döndü |
| KOERI availability | 200, ama **eksik raporluyor**. ISK için 2018–2022 "0", oysa 2018 ve 2020 deneme isteklerinde veri geldi |
| KOERI dataselect | KO.ISK HHZ 1 gün (2016-06-01): 200, 11,2 MB, **284 sn (≈ 40 KB/s)**. 1 saatlik denemeler: 2010 → 204 (veri yok); 2012, 2018, 2020 → 200 (≈ 0,4 MB). 6G.BUYM 2016 1 saat → **204** |
| ETH EIDA federatörü | TLS sertifika hatası; doğrulama kapatılmadı, kullanılmadı |
| IESDMC (Tayvan BATS) | 404; eski adres bağlantıyı sıfırladı |
| KAGSR (Rusya) | bağlantı sıfırlandı. OSDC: 503 |
| GF/PZ (GONAF) | kapalı (defter AV-5: restrictedStatus=closed, 403) |
| NIED (Japonya Hi-net/F-net) | FDSN üzerinden açık değil; denenmedi |

İndirilen üstverinin SHA-256 ilk 16 hanesi: `fedcatalog_kanal.txt` `e6f21dddd921c100`, `marmara_fed_kanal.txt`
`dbcc3ba8ed756405`, `durum.json` `0871f0f38d8ff16c`. Katalog dosyaları TR-11 ile aynıdır: `ev70` `370b728af37ee330`,
`ev70_pre` `60e448a8655ceb46`, `m6_havuz` `969c5c54851ee353`, `mekanizma.jsonl` `eb30828a7a1fff17`. Yeni olarak
`ev.csv` (M ≥ 6,5, derinlik ≤ 30 km, 665 olay) `2d8e16b83a85b58f`. Hepsi depo dışında.

Komutlar:
`python3 -I -B kayit/turetme/tr5/ustveri_indir.py <ham>`
`python3 -I -B kayit/turetme/tr5/sayim_ustveri.py <ham> <ngl> <tr2/ham> --json sayim.json` (≈ 16 sn)

### 4.2 TR-5 sayımı

Evren: 31 252 BHZ/HHZ istasyonu (1995–2020 ile kesişen epoklu); 30 482'si açık, 770'i kısıtlı. 627 hedef olay var
(derinlik ≤ 30 km, T ≤ 2023).

| Kural seti | R | n ≥ | İstasyonlu | Temiz | Kontrollü (≥ 5) | **K** | Plasebo kümesi | Doğrultu atımlı |
|---|---|---|---|---|---|---|---|---|
| **Ana** | 100 | **2** | 46 | 8 | 8 | **8** | 0 | 4 |
| Ana | 100 | 1 | 103 | 18 | 18 | **15** | 5 | 6 |
| Ana | 100 | 3 | 27 | 5 | 5 | 5 | 0 | 3 |
| Ana | 50 | 1 | 38 | 7 | 7 | 7 | 1 | 3 |
| Ana | 50 | 2 | 9 | 1 | 1 | 1 | 0 | 0 |
| derinlik ≤ 40 km | 100 | 2 | 52 | 10 | 9 | 9 | 0 | 4 |
| T ≤ 2025 (bilgi) | 100 | 2 | 51 | 10 | 10 | 10 | 0 | 4 |
| *bilgi:* taban 3 yıl | 100 | 1 / 2 | 114 / 53 | 27 / 12 | 27 / 12 | 24 / 12 | 14 / 8 | 10 / 5 |
| *bilgi:* M ≥ 6,0 (2128 olay) | 100 | 1 / 2 | 288 / 136 | 58 / 27 | 58 / 26 | **50 / 25** | 17 / 6 | 22 / 9 |
| *bilgi:* M ≥ 6,0, taban 3 yıl | 100 | 1 / 2 | 328 / 156 | 88 / 38 | 88 / 38 | **77 / 35** | 41 / 23 | 36 / 13 |
| *bilgi:* M ≥ 6,0 | 50 | 1 | 111 | 30 | 29 | 27 | 8 | 9 |

Tanı (ana, R = 100, n ≥ 2): Ş1–Ş3 kapalıyken temiz 46, K 33. Yalnız Ş1 ile 13. Ş1 yarıçapı 100 km iken 10. Ş1
M ≥ 6,5 iken 13. Son 30 günün öncüleri serbest bırakılınca 9. Okuma: TR-1'deki gibi temiz pencere kuralı aktif
yerleri seçerek eliyor. Kirli pencereleri de alan K 33, ancak pencerelerinde kosismik düşüş ve iyileşme sürdüğü için
ölçü anlamını yitirir.

Ana satırın 8 kümesi: El Mayor-Cucapah 2010, Van 2011, Jan Mayen 2012, Kuzey Ege 2014, Hawaii 2018 (volkanik),
Doğanyol 2020, Kıbrıs 2022, Panama 2023. Bunların 3'ü Anadolu, 1'i Ege. n ≥ 1 satırındaki 18 olaya İzlanda 2000,
Scotia 2003, Mora 2008 (2 olay), Idaho 2020, Perryville 2020, Haiti 2021 ve Kahramanmaraş 2023 (3 olay, tek küme)
ekleniyor.

Eleme nedenleri (627 olay, R = 100):

| Neden | Olay |
|---|---|
| 100 km içinde hiç BHZ/HHZ epoğu yok | 352 |
| Olay anında çalışan istasyon yok | 114 |
| Çalışan var, ama 5 yıl kesintisiz değil | 57 |
| 5 yıl var, ama kısıtlı | 1 |
| ≥ 1 açık, 5 yıllık istasyon var | 103 |

İstasyonsuz 466 olayın dağılımı: öteki 166, PNG/Solomon/Vanuatu/Fiji 95, Endonezya/Filipinler 89, Japonya 29,
Orta Amerika 26, Alaska 17, And 15, Çin 12, İran 9, Yeni Zelanda 4.

**Kontrol havuzu.** Epok başına 5 yıl kesintisiz açık istasyon sayısı: 2005'te 837, 2010'da 1404, 2015'te 2657,
2020'de 4158, 2023'te 4507. Sakin ve ≥ 2 yerli kontrol merkezi aynı epoklarda yalnız 7, 11, 27, 21 ve 21. Her olay 10
kontrol buluyor, ama bunlar aynı 7–27 yerden çekiliyor. Kontroller olaylar arasında tekrar ediyor, bu yüzden kontrol
dağılımının etkin bağımsızlığı sınırlı. Negatif kontrol (2.8/2) bunu ölçer.

### 4.3 Gerçek doluluk (ölçülemedi)

Metadata epoğu, verinin arşivde olduğunu göstermez. EarthScope availability servisi kapatıldığı için IRISDMC
istasyonlarında ölçüm yapılamadı. n ≥ 1 ana satırının IRISDMC dışındaki 19 istasyon-penceresinde ölçülen doluluk:
- CQ.AKMS, CQ.NATA 1,00; GE.ARPR 0,81;
- GE.MALT 0,00 ve NS.JMI 0,00 (kanal adı uyuşmazlığı olabilir);
- KO istasyonları 0,00–0,15 (KOERI servisi eksik raporluyor; bkz. 4.4);
- TU.ANDN 504; CI/RB (SCEDC) servis boş döndü.

Sonuç: gerçek doluluk bilinmiyor. TR-1 ve TR-11 dersine göre ayrıntılı sayım bu tabloyu küçültür; yön kesin,
büyüklük ölçülmedi.

### 4.4 TR-4 sayımı (Marmara)

Kutudaki BHZ/HHZ üstverisi: KO'da 2021 öncesi başlayan 29 istasyon (ISK 1997; çoğu 2006–2008; KAVV 2010, YLV 2011,
SAUV 2012, GAZK 2019, GEML 2020; GONE 2010'da, SPNC 2015'te, GEMT 2018'de kapanmış), ayrıca 2025'te eklenen 9 istasyon. 6G 28 istasyon (2013+, site adı "X"). Kısa süreli geçici ağlar: TL
2013–2016, IJ 2014–2016, YH/DANA 2012–2013, 9P 2019–2020. GF/PZ kapalı. AFAD'ın TU ağının Marmara istasyonları
federasyonda yok; TU'nun 11 istasyonu ORFEUS'ta, Marmara dışında. AFAD'ın kendi portalı denenmedi.

Çevrede M ≥ 6 depremler (merkez 40,8° K 28,5° D, 400 km, 2000–2025): 2014 Kuzey Ege M6,9 (269 km), 2017 Midilli
M6,3 (276), 2020 Samos M7,0 (355), 2022 Düzce M6,1 (209), 2025-04-23 M6,2 (26 km), 2025 Bigadiç M6,1 (164) ve
Sındırgı M6,0 (180).

| T (1 Ocak) | 2012 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KO istasyon-pencere (ana kural) | 5 | 13 | 20 | 20 | 20 | 21 | 22 | 18 | 18 | 12 | 13 | 13 |
| 6G (üstveri; veri yok görünüyor) | – | – | – | – | – | – | 25 | 21 | 21 | 19 | 20 | 20 |
| Sıkı kural (M7 500 km) KO | 5 | 13 | 20 | 20 | 20 | 21 | 22 | 0 | 0 | 0 | 0 | 0 |

KO'da 24 istasyon var. İstasyon başına ≥ 5 yıl aralıklı örtüşmeyen pencere sayısı 50; 6G ile birlikte 95. KOERI
availability servisine göre KO istasyonlarının hiçbiri hiçbir epokta %60 doluluğu geçmiyor: 2013 öncesi ≈ 0,
2015–2017 %20–80, 2018–2022 ≈ 0, 2023–2025 %40–80. Ama deneme istekleri servisin eksik olduğunu gösteriyor: 2012,
2018 ve 2020'de veri var, 2010'da yok. Gerçek doluluk ancak istek yoklamasıyla ölçülebilir (bölüm 5.3).

## 5. İş yükü ve maliyet

**5.1 Hacim.** Hacim, her istasyonun olay ve kontrol pencerelerinin birleşiminden hesaplandı. Ölçülen sıkıştırma
≈ 1,3 bayt/örnek (KO HHZ 1,30; ANMO BHZ 1,13); en düşük ≥ 10 sps kanal ve 3 bileşen varsayıldı.

| Satır | İstasyon-gün (olay) | Tam gün, 3 bileşen | 4 saat/gün, 3 bileşen | 4 saat/gün, yalnız Z |
|---|---|---|---|---|
| Ana n ≥ 2 (K 8) | 322 648 (38 346) | 6,9 TB | 1,2 TB | 0,39 TB |
| Ana n ≥ 1 (K 15) | 415 267 (56 606) | 7,4 TB | 1,24 TB | 0,41 TB |
| M ≥ 6,0 n ≥ 1, 5 yıl (K 50) | 848 492 | 15,7 TB | 2,6 TB | 0,87 TB |
| M ≥ 6,0 n ≥ 1, 3 yıl (K 77) | 931 360 | 17,6 TB | 2,9 TB | 0,98 TB |
| TR-4: 24 KO × 2011–2025 (BH 50 sps) | ≈ 131 000 | 2,2 TB | 0,37 TB | 0,12 TB |

Kontroller hacmin ≈ %85–90'ını taşıyor. Yerinde plasebo, plasebosu hesaplanabilen olaylar için ≈ %20–50 ekler.

**5.2 Süre ve makine.**
- **İndirme.** EarthScope tek akış ≈ 2,4 MB/s (tek ölçüm). Paralel 5–10 akışta 10–20 MB/s varsayılırsa (doğrulanmadı)
  1,2 TB ≈ 1 gün, 7,4 TB ≈ 5–9 gün sürer. KOERI tek akışta ≈ 40 KB/s ölçüldü. Bu hızla TR-4'ün en kısa biçimi
  (0,12 TB) ≈ 35 gün, 0,37 TB ≈ 107 gün sürer. Paralel akışların hızı ölçülmedi. TR-5'in KO istasyonları (Anadolu
  ve Ege olayları) aynı darboğaza takılır.
- **İşlem (kaba, doğrulanmadı).** Tam gün 3 bileşen için ≈ 1–2 sn CPU/istasyon-gün; 4 saatlikte ≈ 0,3 sn. Ana
  n ≥ 1 için tam günde 120–230 CPU saati (4 çekirdekte 1,5–2,5 gün), 4 saatlikte ≈ 35 CPU saati.
- **Disk.** Akış hâlinde işlenirse ham veri tutulmaz. CCF deposu ≈ 30 KB/istasyon-gün, yani 415 bin gün ≈ 12 GB.
- **Bulut oturumu** (4 çekirdek, 15 GB, boş disk 16 GB, obspy kurulu değil). Pilot ve TR-4'ün küçük bir dilimi için
  yeter. Tam koşu için yetmez: indirme günler ile haftalar sürer, oturum ömrü ve disk sınırlı.
- **Hetzner.** 8 vCPU/16 GB sınıfı bulut sunucu ayda kabaca 30–60 € (2024–2025 liste fiyatlarından, doğrulanamadı).
  Saatlik faturalanır, gelen trafik ücretsiz. 1–3 haftalık bir koşu ≈ 10–40 € eder. Tek koşunun 50 €'yu aşması
  beklenmiyor. Aşabileceği tek durum, KOERI hızı yüzünden TR-4'ün sunucuda bir aydan uzun beklemesi; bu durumda TR-4
  ayda ≈ 30–60 € tutar.

**5.3 Pilot.** 10 olaylık bir pilot kapıyı ölçemez. Kapı bir sayıdır (K) ve üstveriden zaten 8–15 olarak biliniyor;
pilot K'yi büyütmez. Pilotun ölçebilecekleri:
- (i) σ_Δ: kontrol yerlerinde depremsiz Δ dağılımı. Güç çevirisi için tek eksik sayı budur.
- (ii) Pozitif kontrol: −0,1 % basamak görülüyor mu?
- (iii) Gerçek indirme hızı ve paralel akış.

Daha ucuz bir ara adım da var: **doluluk yoklaması.** Her aday istasyon-pencere için ayda bir 1 dakikalık istek
atılır; toplam ≈ 60 istek, birkaç KB. Bu, gerçek doluluğu dalga formu indirmeden ölçer ve K'nin ayrıntılı değerini
verir. Bu adım da bir karar gerektirir (çok sayıda küçük istek).

## 6. Güç hesabı

**6.1 Literatür (OpenAlex, yalnız özetler).**

| İş | Sayı | Durum |
|---|---|---|
| Sens-Schönfelder ve Wegler 2006, Merapi (10.1029/2006gl027797) | Günlük çözünürlükte %0,1 doğruluk | Doğrulandı |
| Meier, Shapiro, Brenguier 2010, LA havzası (10.1111/j.1365-246x.2010.04550.x) | %0,1 mertebesinde değişim ölçülebilir; mevsimsel sinyal; çift uzaklığı en çok 60 km | Doğrulandı |
| Hillers ve diğ. 2015, San Jacinto (10.1093/gji/ggv151) | 0,5–2 Hz'de tepeden tepeye mevsimsel ≈ %0,2; ısıl-elastik baskın | Doğrulandı |
| Hillers ve diğ. 2014 (not S2) | Gelgit tepe yanıtı %0,03; ≈ 0,5 MPa⁻¹ | Doğrulandı (önceki not) |
| Clements ve Denolle 2023, California, 700 istasyon (10.1029/2022jb025553) | Isıl ve hidrolojik etkiler benzer büyüklükte; 2011–2016 kuraklığı çok yıllı artış; on yıllık ard-sismik yanıt | Nitel doğrulandı; **genlikler doğrulanamadı** |
| Zhang ve diğ. 2023, Oklahoma (10.1029/2023gl103419) | Çok yıllı hidroloji toplam değişime baskın | Nitel doğrulandı; genlik doğrulanamadı |
| Mao ve diğ. 2022 (10.1038/s41467-022-32194-3); Clements ve Denolle 2018 (10.1029/2018gl077706) | Yeraltı suyu ile çok yıllı dv/v uyumu | Nitel; genlik doğrulanamadı |
| Hobiger ve diğ. 2014 (10.1093/gji/ggu115) | SC yüksek frekansta, CC 0,5 Hz altında en iyi | Doğrulandı |
| Wegler ve Sens-Schönfelder 2007; Chen ve diğ. 2013 Wenchuan (10.1002/2013gl058682); Minato ve diğ. 2012 Tohoku (10.1029/2012gl051405) | Kosismik düşüş −%0,6; %0,2'ye kadar; %1,5'e kadar | Doğrulandı |
| Chen ve diğ. 2013 | "Ana şoktan hemen önce belirgin öncül değişim yok" (2004–2011 serisi) | Doğrulandı (olumsuz) |
| Brenguier ve diğ. 2008 | Parkfield düşüşü 3 yıldan uzun sürdü | Doğrulandı |
| Donaldson ve diğ. 2019, Kīlauea (10.1029/2018gl081609) | Püskürmeden önceki 10 günde hızlı düşüş (volkanik) | Nitel doğrulandı; genlik doğrulanamadı |
| Yıl ölçekli pasif dv/v deprem öncülü, çok olaylı | – | Bulunamadı (not S1 ile aynı) |

**6.2 Ölçülebilir en küçük etki.** H0 altında 10 kontrollü r'nin standart sapması ≈ 0,316'dır. Olay ve kontrol
ölçüleri aynı dağılımlıysa ve olay δ·σ_Δ kaydırılmışsa AUC = Φ(δ/√2) olur. Tek yanlı α = 0,05 ve güç 0,8 için:

| K | r̄_min (AUC) | δ (σ_Δ birimi) | σ_Δ = 0,05 % | 0,1 % | 0,2 % |
|---|---|---|---|---|---|
| 8 (ana) | 0,778 | 1,08 | 0,054 % | 0,11 % | 0,22 % |
| 15 (n ≥ 1) | 0,703 | 0,75 | 0,038 % | 0,075 % | 0,15 % |
| 20 (kapı) | 0,676 | 0,65 | 0,032 % | 0,065 % | 0,13 % |
| 50 (M ≥ 6,0) | 0,611 | 0,40 | 0,020 % | 0,040 % | 0,080 % |
| 77 (M ≥ 6,0, 3 yıl) | 0,590 | 0,32 | 0,016 % | 0,032 % | 0,064 % |

σ_Δ ölçülmedi. 0,05–0,2 % aralığı şu üç sayıya dayanan bir **varsayımdır**: %0,1 ölçüm doğruluğu, %0,2 tepeden tepeye
mevsimsel genlik, ve mevsimselden büyük olabilen çok yıllı hidroloji (genliği doğrulanamadı). Kapıdaki (K 20)
ölçülebilir etki kabaca 0,03–0,13 %'lik son yıl kayması. Bu, kosismik düşüşlerin (%0,2–1,5) onda biri ile yarısı
arasında. Beklenen öncül büyüklüğü için doğrulanmış sayı yok; tek doğrudan olumsuz bulgu Wenchuan. Literatüre göre
beklenti AUC ≈ 0,5'tir.

**6.3 Kapı kuralı ve kıyas.**

| Kapı | Kural | Sayım | Durum |
|---|---|---|---|
| G1 güç (TR-5) | Ana kural setinde K ≥ 20 | 8 (n ≥ 2), 15 (n ≥ 1) | **GEÇMEZ** |
| G2 plasebo (TR-5) | Plasebo kümesi ≥ 10 (yoksa H1 ilan edilemez) | 0 / 5 | GEÇMEZ (yalnız H0 ya da ayırt edilemez çıkabilir) |
| G3 doluluk (TR-5) | G1 ayrıntılı doluluk sayımında da sağlanmalı | ölçülemedi | – |
| G1, bilgi değişkesi M ≥ 6,0 | K ≥ 20 | 50 (5 yıl), 77 (3 yıl); n ≥ 2: 25 / 35 | Üstveride geçer. 3–5 kat küçülmeyle 10–26: **SINIRDA** |
| G2, M ≥ 6,0 | ≥ 10 | 17 / 41 | Geçer (üstveri) |
| G4 duyarlılık | −0,1 % basamakta sahte r̄ ≥ 0,75 | koşuda | – |
| TR-4 veri kapısı | ≥ 10 KO istasyonu, ≥ 2 örtüşmeyen epokta doluluk ≥ 0,60 | Üstveride 20–22 (T 2014–2018) ve 12–13 (T 2021–2023) | Üstveride geçer; doluluk doğrulanamadı: **SINIRDA** |

## 7. En büyük üç risk

1. **Temiz pencere ve açık veri darboğazı (TR-1 ile aynı mekanizma).** M ≥ 6,5 olaylarının dörtte üçünde 100 km
   içinde açık istasyon yok. Dalma-batma kuşaklarının büyük kısmı (Japonya, Endonezya, Pasifik adaları) dışarıda
   kalıyor. İstasyonu olanlar ise aktif yerlerde ve önceki depremlerin iyileşme izleri içinde. Kalan örneklem
   Anadolu ve Ege, Kaliforniya, volkanik adalar ve ağırlıkla doğrultu atımlı olaylar. Marmara'ya mekanizma yönünden
   yakın, ama sayısı küçük. Kontroller aynı 7–27 yerden tekrar çekiliyor.
2. **Çok yıllı hidroloji ve ısıl etki, öncül ölçüsüyle aynı zaman ölçeğinde.** Son yıl ile önceki 4 yıl farkı tam
   olarak kuraklık ve yeniden beslenmenin ürettiği değişim türüdür (Clements ve Denolle 2023; Zhang 2023). Tam yıl
   pencereleri mevsimseli siler, çok yıllıyı silmez. Yağış modeli bilgi satırıdır ve istasyon başına ayar serbestlik
   derecesini şişirir (Seher ve Main 2004 dersi). Okubo 2024'teki işaret çelişkisi, 20 yıllık en iyi seride bile uzun
   dönem eğilimin tek anlamlı okunamadığını gösteriyor.
3. **Gerçek doluluk ve bant genişliği bilinmiyor.** EarthScope availability servisi kapatılmış. KOERI availability
   eksik raporluyor ve KOERI tek akışta ≈ 40 KB/s. KO arşivinin 2010 ve öncesi en az kısmen boş (1 saatlik deneme
   204). Hem TR-4 hem TR-5'in Anadolu olayları buna bağlı. 6G ağı üstveride görünüyor ama verisi yok. Sayımlar bu
   yüzden üst sınırdır.

Ayrıca: aynı gün olan öncü ve artçılar günlük çözünürlükte Ş1'e girmiyor (Kahramanmaraş üçlüsü tek kümede). Hawaii
2018 volkanik. NCEDC, SCEDC ve GeoNet'te açıklık denetlenemedi.

## 8. Defterle örtüşme

- **TR-1 (güç yok):** iskelet aynı (kontrol seçimi, kümeler, plasebo, hüküm sırası); darboğaz da aynı (temiz pencere;
  46 → 8). TR-5'in GNSS'ten farkı, hiç öncül büyüklüğü bilinmeyen bir ölçü olması.
- **TR-11 / TR-12:** TR-4, TR-11'in sismik karşılığıdır. TR-12'nin dersi ("sınanacak etki büyüklüğü yok") dv/v için de
  geçerli (bölüm 6.1).
- **FA-6 (elendi):** S dalgası ayrılması ve hazırlık evresi alarmı aynı ailedendir. TR-5 bundan farklı olarak
  kontrollü ve çok olaylıdır, ama Seher ve Main 2004'teki serbestlik derecesi riski ortaktır.
- **AV-5 (GONAF kapalı):** Marmara'nın en iyi kuyu verisi kapalı (GF/PZ). TR-4 yalnız KO ile kurulabilir.
- **DD-5 (gelgit duyarlılığı, güç yok):** dv/v'nin gerilme duyarlılığı Hillers 2014'ün gelgit kalibrasyonuna dayanır.
  Sığdır.
- **TR-6 ve TR-7 (koşuyor):** TR-7 (tetiklenmiş tremor) aynı KO dalga formunu kullanır. TR-4 ile ortak indirme KOERI
  darboğazını bir kez öder.
- **VE-1 (Marmara GNSS 2017+ kör):** sismik veri bu körlüğün kapsamında değil. TR-4 GNSS kullanmaz.
- **TK-1:** σ ≈ 1 nat varsayımı (not S5) bu tasarımda kullanılmadı. Güç, sıra puanı r ile hesaplandı (TR-1 gibi).

## 9. Sonraki adım (karar kök oturumda)

Bu bir ön kayıt değildir. Açık seçenekler (eleme yapılmadan):
- (a) TR-5 ana tasarım: güç kapısı sayımla geçmiyor.
- (b) TR-5'in M ≥ 6,0 değişkesi: ayrı ön kayıt gerektirir; önce doluluk yoklaması.
- (c) TR-4: önce KO doluluk yoklaması ve KOERI paralel hız ölçümü, sonra ön kayıt. Ölçeceği σ_Δ, TR-5'in güç
  çevirisindeki eksik sayıdır.

## Ek 1: doluluk yoklaması (12 Kasım)

Yalnız varlık sayımı yapıldı. dv/v ölçülmedi, dalga formu okunmadı ve saklanmadı. Betik
`kayit/turetme/tr5/doluluk_yokla.py` (`aday`, `yokla`, `say`). Çıktılar aynı dizinde: `tr5_doluluk.csv`,
`tr4_doluluk.csv`, `doluluk_ozet.json`. Önbellek depo dışında. Bütün istek zamanları 2023 ve öncesinde.

**Yöntem.** Her (istasyon, ay) için ayın 15'inde 12:00–12:01 UTC aralığına 60 saniyelik bir dataselect isteği
atıldı (`cha=BHZ,HHZ`, `loc=*`). Kayda yalnız HTTP kodu ve bayt sayısı girdi. İki kod birlikte istendi, çünkü
üstveride BHZ görünüp arşivde yalnız HHZ bulunan istasyonlar var (AC.PHP: BHZ 204, BHZ,HHZ 200). Bir ay "var"
sayıldı: 200 ve bayt > 0. 204 ve 404 boş sayıldı; 401/403 kısıtlı; başka kodlar hata. Hatalar ana kuralda veri yok
sayıldı. **Dolu** istasyon-penceresi: ayların ≥ %80'inde veri var ve en uzun ardışık boşluk ≤ 3 ay. Duyarlılık için
iki kural daha: gevşek ≥ %60 / ≤ 6 ay, sıkı ≥ %90 / ≤ 2 ay. Sınırlılık: ayda tek dakika, kısa kesintileri görmez.
Hedef olay pencereleri [T − taban, T − 1 g], plasebo pencereleri [T − 2·taban, T − 1 g]. Kontrol havuzu yoklanmadı;
kontroller sayımda üstveriyle kaldı.

**Kapsam.** Aday listesinde 802 çift (temiz ve ≥ 5 kontrollü olaylar; 100 km içindeki bütün açık ve kesintisiz
istasyonlar) ve 21 688 istek çıktı. Bu 15 000'i aştığı için liste **olay başına en yakın 3 yerle** sınırlandı:
373 çift, 152 istasyon, 10 336 istek. TR-4 için 3456 istek (24 KO istasyonu, 2012-01 ile 2023-12 arası).
Benzersiz toplam 13 792 istek, 12 957'si atıldı (%93,9). TR-5 %100 tamamlandı. TR-4 %75,8 (2621/3456): arka plan
işi 2 saatlik üst süre sınırında durduruldu, sınır zaten en büyük değerindeydi ve iş yeniden başlatılmadı. KO.SAUV,
SILT, SLVT, SPNC ve YLV hiç, KO.RKY 29/144 ay yoklandı. Akış servis başına tekti. Bekleme EarthScope, GEOFON ve
ORFEUS'ta 0,3 sn, KOERI'de 2 sn, ötekilerde 0,5 sn idi. User-Agent geneldi, TLS doğrulaması açıktı.

| Servis | 200 | 204 | Öteki | Medyan sn |
|---|---|---|---|---|
| EarthScope (IRISDMC) | 2670 | 2794 | – | 0,38 |
| KOERI | 2642 | 915 | 835 atılmadı | 0,97 |
| INGV | 845 | 223 | – | 1,14 |
| GEOFON | 453 | 123 | – | 0,52 |
| NOA | 434 | 34 | – | 0,61 |
| NCEDC | 424 | 8 | – | 0,75 |
| ORFEUS | 314 | 238 | – | 0,77 |
| SCEDC | 277 | 57 | **500: 50** (geçici; elle yinelenen bir istek 200 döndü, yeniden yoklanmadı) | 0,68 |
| IGN / EPOSFR / AUSPASS / GEONET | 106 / 70 / 23 / 36 | 38 / 38 / 13 / 0 | – | 0,4–1,4 |
| UIB-NORSAR | 2 | 130 | neden doğrulanamadı | 1,75 |

401, 403, 429 ve 503 hiç görülmedi. EarthScope isteklerinin yarısı boş döndü, çünkü bazı istasyonlarda pencerenin
başı arşivde yok (örnek: AI.ORCD 1997–2003 boş, 2012'de BHZ var).

**TR-5 çiftleri.** Ana kurala göre dolu olan çiftler:
- olay penceresi: 3 yıllık tabanda 60/151, 5 yıllıkta 44/103 (≈ %40);
- plasebo penceresi: 34/88 ve 10/31;
- 373 çiftin tamamında: ana 148, gevşek 185, sıkı 113.

**Doğrulanmış sayım** (M ≥ 6,0, z ≤ 30 km, 2000–2023, R = 100 km; `sayim_ustveri.py` kuralları; olay ve plasebo
istasyonlarına doluluk süzgeci). İlk satır öncekiyle aynı sayıları üretir.

| Süzgeç | Taban | n ≥ | K | Plasebo kümesi | Doğrultu atımlı | G1 (K ≥ 20) | G2 (≥ 10) |
|---|---|---|---|---|---|---|---|
| yalnız üstveri | 5 / 3 | 1 | 50 / 77 | 17 / 41 | 22 / 36 | – | – |
| yalnız üstveri | 5 / 3 | 2 | 25 / 35 | 6 / 23 | 9 / 13 | – | – |
| **ana** | **5** | 1 | **25** | **6** | 11 | GEÇTİ | **GEÇMEDİ** |
| **ana** | **3** | 1 | **37** | **20** | 17 | **GEÇTİ** | **GEÇTİ** |
| ana | 5 / 3 | 2 | 8 / 11 | 0 / 6 | 0 / 2 | GEÇMEDİ | GEÇMEDİ |
| gevşek | 5 / 3 | 1 | 28 / 51 | 6 / 24 | 13 / 21 | geçti / geçti | geçmedi / geçti |
| gevşek | 5 / 3 | 2 | 10 / 16 | 0 / 8 | 0 / 2 | geçmedi | geçmedi |
| sıkı | 5 / 3 | 1 | 20 / 26 | 4 / 14 | 8 / 12 | geçti / geçti | geçmedi / geçti |
| sıkı | 5 / 3 | 2 | 7 / 6 | 0 / 3 | 0 / 0 | geçmedi | geçmedi |

Küçülme 1,5–3 kat (n ≥ 1) ve 2–3 kat (n ≥ 2). Bu sayılar **alt sınırdır**, üç nedenle: yalnız en yakın 3 yer
yoklandığı için dolu olmayan bir yerin yerine 4. yer giremedi; SCEDC'nin 50 hatası boş sayıldı; kontroller
doluluk süzgecinden geçmedi (≥ 5 kontrol şartı üstveriyle sağlandı). Son nedenin yönü ters: kontrol tarafında da
küçülme beklenir ve bu doğrulanamadı. Kapıyı iki koşulda da geçen tek biçim **3 yıllık taban, n ≥ 1** (ana, gevşek
ve sıkı kuralların üçünde de). Bu biçim, ana tasarımdaki n ≥ 2'den ve 5 yıllık tabandan iki değişiklik ister.

**TR-4.** T ≥ 2017 epoklarında pencere tamamen 2012 sonrasında, bu yüzden tam kapsanıyor. Öncesi kapsam dışında.
Dolu KO istasyon-penceresi sayısı (yoklananlar üzerinden):

| T | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|---|---|
| ana | 8 | 10 | 9 | 9 | 8 | 9 | 9 |
| gevşek | 13 | 13 | 12 | 12 | 9 | 10 | 10 |
| sıkı | 3 | 4 | 8 | 8 | 7 | 9 | 9 |
| yoklanmamış ama aday | 4 | 5 | 5 | 5 | 2 | 2 | 2 |

Dolu istasyon sayısı: ana 13, gevşek 15, sıkı 11. Kapı ≥ 10 istasyon ve ≥ 5 yıl arayla iki epok istiyor
(2017–2022 ya da 2018–2023):
- ana kural: yoklananlarla **GEÇMEDİ** (10 ve 9); yoklanmayan 6 istasyonla geçebilir, yani **doğrulanamadı**;
- gevşek: GEÇTİ (13 ve 10);
- sıkı: GEÇMEDİ.

Ay doluluğu yıl başına %57–72 arasında. KOERI availability servisinin 2018–2022 için verdiği "≈ 0" yanlıştır. İstasyon
başına 2012–2023 ay oranı ISK, CTKS, KLYT ve MDNY'de 0,92–0,97, GEMT'de 0,49, MRMT'de 0,61.

**Hacim ve süre.** Kapıyı geçen biçim için (3 yıllık taban, n ≥ 1, ana süzgeç) hacim 590 552 istasyon-gün; bunun
65 700'ü olay penceresi, kalanı kontroller. 1,3 bayt/örnek ve en düşük ≥ 10 sps kanal varsayıldı:

| Biçim | Hacim | KOERI payı | KOERI süresi (40 KB/s) | Öteki merkezler (2,4 MB/s, tek akış) |
|---|---|---|---|---|
| Tam gün, 3 bileşen | 11,9 TB | 0,87 TB | ≈ 250 gün | ≈ 53 gün |
| 4 saat/gün, 3 bileşen | **1,98 TB** | 0,145 TB | **≈ 42 gün** | ≈ 9 gün |
| Tam gün, yalnız Z | 3,97 TB | 0,29 TB | ≈ 84 gün | ≈ 18 gün |
| 4 saat/gün, yalnız Z | **0,66 TB** | 0,048 TB | **≈ 14 gün** | ≈ 3 gün |

- **Plasebo pencereleri** bu hacme dahil değil; kabaca %20–50 eklerler.
- **Kontroller** doğrulanmadığı için hacim üst sınırdır.
- **Hız varsayımları:** 2,4 MB/s yalnız EarthScope'ta tek ölçümle bulundu; öteki merkezlere genellenmesi doğrulanmadı.
  POST ile istek toplama da varsayıldı. Gün başına ayrı istek atılırsa 590 bin istek tek akışta ≈ 7 gün ek gecikme getirir.
- **Yalnız Z biçimi** tek istasyon bileşenler arası yöntemi (ZE, ZN, EN) bozar. Geriye yalnız 60 km'den yakın
  istasyon çiftleriyle Z–Z CC kalır, bu da n ≥ 1 olaylarının çoğunda çift olmadığı anlamına gelir. Ana yöntemin en
  küçük geçerli biçimi bu yüzden 4 saat/gün, 3 bileşendir: ≈ 2 TB, KOERI yüzünden ≈ 6 hafta.
- **TR-4** (yalnız KO): 4 saat/gün 3 bileşen ≈ 0,37 TB, ≈ 107 gün; yalnız Z ≈ 0,12 TB, ≈ 35 gün (bölüm 5). KOERI
  paralel akış hızı hâlâ ölçülmedi.
- **Sunucu:** Bu koşu bulut oturumunun süresine ve diskine sığmaz; bunu bu yoklama da gösterdi (2 saatlik iş sınırı).
  Akış hâlinde işlemeyle disk küçük kalır, ama haftalarca açık kalacak bir makine gerekir. Hetzner 8 vCPU sınıfı ayda
  kabaca 30–60 € tutar (**doğrulanamadı**). 6–8 haftalık bir koşu ≈ 45–120 € eder. Yalnız Z ve 4 saat/gün biçiminde
  koşu ≈ 2–3 hafta, ≈ 15–45 € eder. Bu iş 0 € harcadı; makine kiralanmadı.

**Engeller.**
- TR-4'ün 6 istasyonu yoklanmadı.
- SCEDC'nin 50 isteği 500 döndü ve yinelenmedi.
- UIB-NORSAR'ın neredeyse tamamen boş dönmesinin nedeni doğrulanamadı.
- Kontrol havuzunun doluluğu ölçülmedi.
- İstek başına yalnız 1 dakika alındığı için gün doluluğu (≥ 0,60 şartı) ölçülmedi; ay doluluğu yerine kullanıldı.

## Ek 2: TR-4 doluluk yoklaması tamamlandı (12 Kasım)

Ek 1'de süre sınırı yüzünden yoklanamayan 835 KOERI isteği kök oturumda aynı betikle ve aynı önbellekten tamamlandı (13 792 / 13 792 istek; 401/403/429 yok). `say` adımı yeniden koşuldu; TR-5 satırları Ek 1 ile aynı.

TR-4 (24 KO istasyonu, aylık yoklama, 2012–2023):

| Kural | Dolu istasyon | T 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | Kapı (≥10 istasyon, ≥5 yıl arayla iki epok) |
|---|---|---|---|---|---|---|---|---|---|
| Ana (≥%80, boşluk ≤3 ay) | 18 | 10 | 14 | 13 | 14 | 10 | 10 | 10 | GEÇTİ (2017 ve 2022; tam sınırda) |
| Gevşek (≥%60, ≤6 ay) | 20 | 16 | 17 | 16 | 17 | 11 | 12 | 12 | GEÇTİ |
| Sıkı (≥%90, ≤2 ay) | 15 | 5 | 7 | 12 | 12 | 9 | 10 | 10 | GEÇMEDİ |

Hüküm: TR-4 veri kapısı ana kuralla GEÇTİ, ama iki epokta tam 10 istasyonla; gün düzeyinde doluluk ölçülünce bir istasyon kaybı kapıyı kapatır. Ölçüm TR-5b ile aynı yöntemi ve aynı indirme altyapısını kullanır; ön kaydı TR-5b ön kaydının incelemesinden sonra, aynı işleme zinciriyle yazılır.
