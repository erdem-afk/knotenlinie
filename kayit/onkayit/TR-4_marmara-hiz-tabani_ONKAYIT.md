# TR-4 ön kayıt: Marmara KO istasyonlarında olaysız yıllarda ortam gürültüsü dv/v tabanı

Durum: **DONDURULDU sürüm 2, 12 Kasım 2026 (İNCELEME-1 düzeltmeleri işlendi).** Dondurma commit'i bu dosyayı, pencere
listesini ve `tr4_asama0.py`'yi içerir; aşama 0'ın ilk ağ isteğinden önce push edilir. dv/v koşu kodu ayrı yazılır ve
ilk dalga formu isteğinden önce bağımsız kod incelemesinden geçip dondurulur.
Hiçbir dalga formu indirilmedi, açılmadı ya da yoklanmadı. Bu taslak yalnız var olan üstveri, doluluk önbelleği ve
TR-5b kataloğuyla, ağsız hesaplandı. Kol: TR. Ata: `TR-5_TR-4_SAYIM.md` Ek 2 (sha256 `df912cb0…`). Zincir:
`TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 3, DONDURULDU (sha256 `506c0470…`). Maliyet bu belgeye kadar 0 €.

**Tek cümle.** TR-4, Marmara'daki KO istasyonlarında, depremden uzak (olaysız) pencerelerde, TR-5b'nin dondurulmuş
dv/v zinciriyle tek istasyonun "son yıl − önceki iki yıl" düzey farkını (Δ) ölçer ve bu farkın dağılımını yazar:
**σ̂_Δ** (1,4826 · MAD) ve **q95 = |Δ|'nın %95 niceliği**. q95, olaysız bir yılda tek istasyonda Δ'nın %95
olasılıkla kalacağı sınırdır. Yani bu ölçüyle Marmara'da tek istasyonda %5 yanlış alarm oranında saptama eşiğidir. Bu
büyüklükte bir değişim yarı yarıya saptanır; %80 saptama ≈ q95 + 0,84 σ̂_Δ ister. Bu bir ölçüm tabanıdır; olasılık, alarm ya da tahmin değildir.

**Kapı sayıları (üstveri ve Z doluluğu, aşama 0'dan önce).** Ana tanımla 21 yer (22 istasyon), 102 yer-penceresi;
yıllık T 2017–2024 için yer sayısı 15, 16, 15, 14, 14, 9, 10, 9. Kapı (≥ 10 yer, en az 3 yıl arayla ≥ 2 epok)
geçiyor; ama TR-5b'de aygıt kuralı ve yatay bileşenler sayıyı ≈ %9 + %9 küçülttü. Aynı küçülme burada 2017 ve 2020'yi
≈ 12'ye indirir; kapı yine geçer, pay dardır.

**Koşu düzeni.** Aşama 0 (≈ 630 hafif istek, bulut oturumu, 0 €) → aşama H (8 üretim biçiminde istek, §5.2) → kademe
(A ya da C, yalnız hızdan ve aşama 0'ın hacminden; §5.3) → kronolojik indirme ve saatlik ÇİF (0 € bulut oturumunda,
her biri ≤ 2 saatlik, kaldığı yerden süren işler; bütçe 21 etkin gün / 42 takvim günü) → ölçü. Bütçe dolarsa analiz
tamamlanmış T'lerle yapılır; en küçük küme T 2017–2021'dir (153,6 GB). 40 KiB/s ve altında hiçbir kapıyı koruyan küme
bütçeye sığmaz; hüküm "veri yok (aktarım hızı)" olur. Sunucu kiralanmaz; kiralama Erdem'in onayını ister ve hızı
artırmaz.

---

## 0. Kimlik, öncelik ve TR-5b'den farklar

Çelişkide öncelik: bu belge > `TR-4_INCELEME-1.md` > `TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 3 >
`TR-5_TR-4_SAYIM.md`. Bu belgede
yazılmayan her ölçü kuralı TR-5b §3'teki gibidir ve değiştirilmez. Aşağıdaki tablo farkların tamamıdır.

| Konu | TR-5b (sürüm 3) | TR-4 |
|---|---|---|
| Soru | Olay öncesi son yıl, kontrollere göre farklı mı | Olaysız yıllarda Δ'nın dağılımı (taban) |
| Yerler | Küresel olay, plasebo, kontrol istasyonları | KO, kutu 40,0–41,6° K, 26,5–30,5° D |
| T | Olay zamanı | Yıllık, 1 Ocak, 2017–2024 (§2.2) |
| Olaysızlık | Kontroller için TR-1 kuralları | §2.3 (M ≥ 7 için 300 km; SAYIM §3.2) |
| Gün örneklemesi | Her gün, 4 saat | Kademe A (her gün, 4 saat) ya da C (ayın 1–20. günleri, 4 saat); hızdan, §5.3 |
| Yer | İstasyon | ≤ 1 km'deki istasyonlar bir yerdir (yalnız KO.ISK + KO.KAVV; temsilci önceden sabit, §2.4) |
| Ana ölçü | İşaretli r̄ (AUC) | σ̂_Δ ve q95, yer-pencere Δ'larından (§4) |
| Hüküm | H1 / H0 / ayırt edilemez / güç yok | Taban ölçüldü + TR-5b (c) şartı: karşılandı / karşılanmadı / belirsiz; ya da veri yok (§4.5) |
| PK | Olayların kosismik düşüşü, hüküm adımı | Yok. Nisan 2025 M6,2 yalnız bilgi satırı (§3.4) |
| Plasebo, N1, kör adımı | Var | Yok (ölçülecek bir etki yok). Kod denetimleri (i) ve (ii-a) aynen var |

## 1. Soru ve neyi ölçmediği

**Soru.** Marmara'daki KO istasyonlarında, M ≥ 6 depremlerden uzak yıllarda, TR-5b ölçüsünün (0,5–2 Hz, tek istasyon
bileşenler arası, 4 saat/gün, ay eşlemeli düzey farkı Δ = C − (A∪B)) istasyon-pencere dağılımı ne kadar geniştir?

İki iş için gerekir:
1. **dv/v zaman daraltma yolunun Marmara'daki çözünürlüğü.** q95, "son yılda tek istasyonda şu kadardan küçük bir
   düzey değişimi, olaysız yılların doğal saçılımından ayrılamaz" cümlesinin sayısıdır.
2. **TR-5b yeniden açma şartı (c):** σ_Δ ≲ %0,2 (TR-5b §11). TR-4 bunu Marmara için sınar.

**Neyi ölçmez.**
- Bir deprem olasılığı, alarm eşiği ya da yanlış alarm oranı değildir. **İstanbul için mutlak olasılık bu belgenin
  hiçbir yerinde yazılmaz ve hiçbir sonuçtan türetilmez.**
- Gerilme ölçmez. Gelgit duyarlılığı (Hillers 2014, ≈ 0,5 MPa⁻¹, 2–8 Hz, sığ) yalnız mertebe çevirisi için bilgi
  satırında anılır (%0,1 ≈ 2 kPa); 0,5–2 Hz'e taşınabilirliği doğrulanamadı.
- Ölçü istasyonun çevresindeki sığ ortamı örnekler (TR-5b §1). Fay zonunun derinini ya da deniz altındaki ana kolu
  ölçmez.
- σ̂_Δ burada **istasyon düzeyidir**. TR-5b'nin σ_Δ'sı kontrol düzeyidir. Bir kontrol 1–3 istasyonun ortalamasıdır;
  TR-5b'nin ilk 5 adayında ortalama 1/n = 0,668'dir (TR-5b İNCELEME-2 İ2-Ö2). İstasyonlar bağımsızsa σ_kontrol
  ≈ 0,817 · σ_istasyon olur, tam ilişkide ikisi eşittir. Bu yüzden istasyon düzeyinde σ < %0,20 ise kontrol düzeyinde
  de < %0,20'dir; "karşılandı" tutucudur. "Karşılanmadı" ise ancak istasyon düzeyinde σ > %0,20 / 0,817 = %0,245
  olduğunda kontrol düzeyinde de geçerlidir. §4.3 adım 5'in eşikleri buna göredir. Kontrol düzeyi eşleniği bilgi
  satırı 6'dadır.

## 2. Veri ve olaysız pencereler

**2.1 Ağ ve kaynak.** KOERI FDSN (`eida-service.koeri.boun.edu.tr`), ağ KO, kutu 40,0–41,6° K, 26,5–30,5° D:
38 istasyon (`marmara_fed_kanal.txt`, sha256 `dbcc3ba8…`). Z doluluğu TR-5'in yoklama önbelleğinden
(`onbellek.jsonl`, sha256 `ce4fe524…`, 2012-01…2023-12; 24 istasyon yoklanmış). Kanal seçimi, kapsama ve aygıt kuralı
TR-5b §2.5 ve §3.1'deki gibidir (`tr5b_asama0.py`'nin `kapsar`, `aygit`, `ay_listesi` işlevleri birebir kopyalandı).

**2.2 T epokları.** T her yılın 1 Ocak'ıdır, 2017–2024. Pencere [T − 1095, T − 8] (TR-5b §3.5). Sınırlar:
- **Alt:** KO'da BH → HH geçişi 2013-11-08. 2016'dan önceki T'lerin penceresi bu geçişi içerir ve "pencere içinde kanal
  değişmez" kuralını bozar. İlk temiz T 2017'dir.
- **Üst:** T 2024'ün penceresi 2023-12-24'te biter. T 2025 olaysızlık kuralıyla (§2.3, [T, T + 1 yıl) içinde
  2025-04-23 M6,2) düşer. Bütün dalga formu istekleri ≤ 2025-12-31; fiilen hüküm verisi ≤ 2023-12-24, bilgi satırı
  13'ün verisi ≤ 2025-05-31.
- Ardışık T'lerin pencereleri örtüşür (3 yıllık pencere, yıllık adım). Bu yüzden belirsizlik iki yönlü (yer × T)
  önyüklemeyle hesaplanır (§4.3) ve örtüşmeyen T kümeleri bilgi satırıdır.

**2.3 Olaysızlık (istasyona göre).** Yer-penceresi olaysızdır, eğer [T − 5 yıl, T + 1 yıl) aralığında, ComCat
`type = earthquake` kataloğunda (TR-5b `m5_*.csv`, sha256'ları §Ek'te):
- M ≥ 6,0 ve derinlik ≤ 40 km, istasyona ≤ 150 km;
- M ≥ 7,0 ve derinlik ≤ 70 km, ≤ 300 km;
- M ≥ 8,0, ≤ 1000 km

olay yoksa. M ≥ 7 için 300 km SAYIM §3.2'nin tanımıdır; TR-5b kontrollerinin 500 km'si Marmara'da Samos 2020
(M7,0) yüzünden 2020–2024'ün bütün T'lerini düşürür (bilgi satırı 1, N 46). 300 km kuralıyla Samos beş istasyonda
(251–295 km) dışarıda, ötekilerde (≥ 309 km) içeridedir. Eleme nedenleri (istasyon düzeyi,
kutudaki 38 istasyon × 8 T = 304 hücre): kanal kapsamı yok 115, olaysızlık 44 (Samos 2020 `us7000c7y0` 20,
Düzce 2022 `us7000irp8` 18, Kuzey Ege 2014 `usb000r2hc` 6), Z doluluğu 29, yoklanmamış aday 3 (GAZK 2023 ve 2024,
GEML 2024), aygıt (Z önizlemesi) 3 (KLYT 2019–2021, sensör değişimi 2018-12-24), **dolu ve olaysız 110**.

**M5 maskesi aynen TR-5b §2.6'dır:** M ≥ 5, derinlik ≤ 70 km, ≤ 50 km olaylarda [t, t + 59] günleri ε'dan atılır.
Ana örneklemde maskeli pencereler:
- **26 Eylül 2019 Silivri açıkları Mw 5,7** (`us70005lkl`): CRLT (42,9 km), CTKS (47,7 km), SLVT (36,5 km); T 2020,
  2021, 2022'nin pencerelerinde 60'ar gün maskeli. BOTS (17,2 km) o tarihte kurulmamıştı.
- **4 Aralık 2023 Mudanya M5,1** (`us7000lg2l`): MDNY (8 km), T 2024'te 21 gün.

Gerekçe: TR-5b'nin σ_Δ'sı bu maskeyle tanımlıdır; (c) için aynı tanım gerekir. Daha sıkı olaysızlık (2019 olayının
çevresini tümüyle dışlamak) bilgi satırı 1'dedir.

**23 Nisan 2025 Silivri açıkları M6,2** (`us7000pufs`) [T, T + 1 yıl) kuralıyla T 2025'i ve 2024-04-23
sonrasını dışlar. Ana örneklemde ona dokunan pencere yoktur.

**2.4 Yer ve temsilci.** ≤ 1 km'deki istasyonlar tek yerdir; yalnız KO.ISK ve KO.KAVV birleşir. Temsilci önceden sabittir: en çok dolu pencereli istasyon, eşitlikte ortalama ay doluluğu yüksek olan,
sonra kod sırası → **KO.ISK**. Öteki istasyon indirilmez. Ölçünün birimi yer-penceresidir.

**2.5 Bağlayıcı sayılar** (`tr4_onkayit_sayim.json`, `tr4_pencereler.csv`).

| Tanım | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | Yer-pencere | Kapı |
|---|---|---|---|---|---|---|---|---|---|---|
| **Ana (Z dolu: ay ≥ %80, en uzun boşluk ≤ 3 ay)** | 15 | 16 | 15 | 14 | 14 | 9 | 10 | 9 | **102** | geçer |
| Gevşek doluluk (≥ %60, ≤ 6) | 17 | 19 | 17 | 16 | 17 | 11 | 11 | 10 | 118 | geçer |
| Sıkı doluluk (≥ %90, ≤ 2) | 7 | 12 | 11 | 9 | 9 | 9 | 8 | 7 | 72 | **geçmez** |
| Yalnız üstveri | 21 | 21 | 19 | 17 | 17 | 12 | 13 | 14 | 134 | geçer |

Doluluk tanımları TR-5b'nin dolu tanımıdır; aşama 0 ve 1b'de günlük doluluk ve yatay bileşenler eklenir.

## 3. Ölçü

**3.1 Zincir.** TR-5b §3.1–3.6 değiştirilmeden: yerel güneş gecesi 4 saat, saat kabulü ≥ %99, 20 sn⁻¹, enerji reddi
3 × medyan, beyazlatma 0,5–2 Hz, ZE/ZN/EN, ±60 sn, gün ≥ 2 saat, 10 günlük geriye yığın ≥ 5 gün, germe ±%0,5 adım
%0,001, koda 10–40 sn, CC ≥ 0,40, Δ ay eşlemeli (ayda ≥ 10 geçerli gün, ≥ 9 eşleşen ay), istasyon Δ = geçerli
çiftlerin medyanı (≥ 2 çift). Kanal ve konum kodu pencere içinde değişmez. Başvuru uygulaması `tr5b_yapay.py`
(`germe_olc`, `zincir`, `ay_esle`).

**3.2 Tek fark: gün örneklemesi (kademe).**
- **Kademe A:** her gün (TR-5b aynen).
- **Kademe C:** yalnız takvim ayının 1–20. günleri indirilir; öteki günler "veri yok" sayılır, zincir değişmez.
  Bir ayda en çok 20 gün olduğu için "ayda ≥ 10 geçerli gün" şartı daha sık tutmaz; yapay doğrulama bunu içerir
  (§6.1). Hacim A'nın %66'sı. "Gün", TR-5b §3.1'in yerel ortalama güneş tarihi d'dir; 1–20. günler d'ye göre
  sayılır.

Kademe veri görülmeden, yalnız hızdan seçilir (§5.3). A seçilirse C, A'nın alt kümesi olarak bilgi satırı 9'da
hesaplanır.

**3.3 Neden başka kademeler değil.** Hacmi küçülten öteki seçenekler yapay veride sınandı (§6.1): 2 saatlik günler
(ayda 20 ya da 16 gün, ya da her gün) ve ayda 16 gün × 4 saat en düşük SNR'de (CC10 ≈ 0,5) Δ'yı yer-pencerelerin
%0–42'sinde üretemiyor. 3 saat/her gün (H) %89'da üretiyor, ama C'den büyük. Yalnız A ve C bütün SNR'lerde ≥ %91
geçerli Δ veriyor. 1 saat/gün TR-5b zincirini değiştirir (gün ≥ 2 saat), dışarıda bırakıldı.

**3.4 Pozitif kontrol: Nisan 2025 M6,2 hükme uygun değil.** İncelendi ve reddedildi, gerekçeler:
- 2 L(M6,2) ≈ 33 km. Bu yarıçapta kullanılabilir istasyon yok: BOTS (24,7 km) 2025-03-14'te açıldı (olay öncesi
  ≈ 40 gün, başvuru için yetmez), NMR9 2025-05'te. Kullanılabilir tek istasyon **SLVT, 43,9 km**. CRLT (50,2 km)
  HHZ 2024-08-15'te bitiyor.
- Tek istasyonda tek yanlı %5 saptama olasılığı (yapay, `tr5b_yapay2.pk_istasyon`, 300 tekrar, 4 saat/gün):
  kosismik düşüş %0 / 0,01 / 0,02 / 0,05 / 0,08 için CC10 ≈ 0,5'te 0,05 / 0,06 / 0,09 / 0,09 / 0,18; CC10 ≈ 0,7'de
  0,05 / 0,06 / 0,07 / 0,16 / 0,27. Napa ölçeğinde (%0,08) bile ≤ 0,27. n = 1 olduğundan "geçmedi" bilgisizdir.
- 26 Eylül 2019 Mw 5,7 da uygun değil: ≤ 30 km'de istasyon yok (BOTS kurulmamıştı).

Bu yüzden PK hüküm adımı değildir. SLVT'nin Nisan 2025 δ_ko'su (±%2 ızgara, TR-5b §4.2 adım 8 tanımı) bilgi
satırı 13'tür. Bedeli: TR-4'te zincirin Marmara'da kosismik düşüşü gördüğü gösterilmez; kod doğruluğu yalnız (i)
ve (ii-a) ile sınanır. İNCELEME-1'e göre uzak bir PK kapsam dışıdır. Bedeli §4.6 "Karşılandı" maddesinin (3) şartıdır.
Bilgi satırı 11 (mevsimsel genlik) ve 14 (2019 Silivri) zincirin duyarlılığına dair bağlayıcı olmayan iki işarettir ve
Kalıp T'de yazılır.

## 4. Hüküm satırı (tek, sıralı, otomatik)

**4.1 Ölçü.** n yer-penceresinin Δ'larından:
- **σ̂_Δ = 1,4826 · MAD(Δ)**, TR-5b §3.6'nın kestiricisi;
- **q95 = |Δ|'nın %95 niceliği** (iki yanlı, işaretsiz).

**4.2 Kesinlik.** İki yönlü önyükleme: yerler ve T yılları ayrı ayrı yerine koyarak çekilir, hücre ağırlığı iki
çokluğun çarpımı; B = 2000; tohum `sha256("tr4-hukum|20261202")`'nin ilk 8 onaltılık hanesi. σ̂_Δ için 5.–95.
yüzdelikler [L, U] yazılır: "%90 iki yönlü önyükleme aralığı". q95 için 2,5.–97,5. yüzdelikler yazılır: "%95 iki yönlü
önyükleme aralığı". Yer-pencereler hem yerde (aynı istasyon) hem zamanda (örtüşen pencereler, ortak hidroloji) ilişkili
olduğu için tek yönlü önyükleme kullanılmaz. Benzetimde (İNCELEME-1, yer düzeyi, R = 300) σ aralığı gerçek σ_Δ'yı
ρ 0,3'te 0,98–1,00, ρ 0,6'da 0,91–0,94 olasılıkla kapsar. q95 aralığı gerçek q95'i ρ 0,3'te 0,94–0,97, ρ 0,6'da
0,83–0,89 olasılıkla kapsar; T 2017–2021 kesik koşuda ρ 0,6'da 0,79–0,81. Aralıklar bu kapsamalarla anılır; "güven
aralığı" denmez.

**4.3 Sıra.** Kod bu sırayı insan müdahalesi olmadan uygular. Bir adım hüküm verirse hüküm kesinleşir ve değişmez.
"geçersiz (kod)" ile kesinleşirse sonraki adımların hiçbiri koşmaz ve hiçbir Δ sayısı yazılmaz. "veri yok" ile
kesinleşirse (adım 0, 1, 4 ya da §5.3'ün bütçesi), dolu kalan yer-pencereleri yine işlenir. Kapıyı tutmasalar da
indirme §5.3'e göre yapılır ve 2. ile 3. adımlar koşar. İkisi de geçerse 5. adımın sayıları **bilgi satırı 0 ("kapı
altı taban")** olarak yazılır. Bilgi satırı 0 (c) sınamasını yapmaz. Bilgi satırı 0 ancak ≥ 30 geçerli yer-penceresi
ve ≥ 6 yer varsa hesaplanır; yoksa "hesaplanmadı (n = [..], yer = [..])" yazılır. Aşama 0'dan sonra dolu
yer-penceresi < 30 ise indirme yapılmaz. Gerekçe: %40 yer kaybında (≈ 47 geçerli yer-penceresi) σ aralığının
genişliği ≈ 1,0 σ'dır; ölçü kapı altında da bilgi taşır (İNCELEME-1).

0. **G0 (aşama 0).** Aşama 0'ın üç bileşen yoklaması ve aygıt kuralından sonra: dolu yer sayısı ≥ 10 olan T'ler
   içinde en az 3 yıl arayla iki T yoksa **"veri yok (aşama 0)"**.
   - **Ara durum, hüküm değil:** §5.3 madde 3'ün yinelemeleri sürerken "ertelendi (aktarım hızı)" yazılır. Bu durum en
     çok 5 gün sürer ve §5.3 madde 1, 2 ya da 4 ile biter.
1. **1b (gün doluluğu).** İndirilen verinin gün düzeyi doluluğuyla (TR-5b dolu tanımı, üç bileşen) aynı kapı.
   Tutmazsa **"veri yok (gün doluluğu)"**.
2. **Kod denetimi (i).** Koşu kodu `tr5b_yapay_ccf.npz`'yi (sha256 `44189a31…`) okur ve (a) TR-5b'nin
   `tr5b_yapay_ccf_ref.json`'unu (sha256 `36339a46…`) TR-5b §4.2 adım 1'in toleranslarıyla yeniden üretir;
   (b) kademe C seçildiyse ayrıca `tr4_yapay_ref.json`'u (sha256 `238b6e09…`; ayın 1–20. günleri maskesiyle) aynı
   toleranslarla (Δ %0,0005, oran 0,005) üretir. Sapan dizi > 0 ise **"geçersiz (kod)"**.
3. **Kod denetimi (ii-a), gerçek ÇİF'te.** Bütün yer-pencerelerin C dilimi günlük ÇİF'lerine −%0,1 germe eklenir,
   başvuru ve yığınlar yeniden kurulur, oran = (Δ_ekli − Δ_özgün) / (−%0,1). Havuzlanmış medyan oran [0,80; 1,20]
   dışındaysa **"geçersiz (kod)"**.
4. **ε geçerliliği.** Geçerli Δ'sı olan yer-pencerelerle 0. adımın kapısı yeniden sınanır. Tutmazsa
   **"veri yok (ε geçerliliği)"**.
5. **Taban.** σ̂_Δ, q95 ve %90 aralıkları hesaplanır, dosyaya yazılır, sha256'sı günlüğe geçer. Ardından (c):
   - U(σ̂_Δ) < %0,20 → **"taban ölçüldü; TR-5b (c) karşılandı"**;
   - L(σ̂_Δ) > %0,245 → **"taban ölçüldü; TR-5b (c) karşılanmadı"**;
   - öteki → **"taban ölçüldü; TR-5b (c) belirsiz"**.

**4.4 Neden bu kapı.** TR-5b'nin kontrol kapısı istasyon sayısıydı; burada tek bir σ ve bir nicelik kestirilir.
≥ 10 yer, istasyon etkisinin tek bir yere bağlı kalmamasını; 3 yıl arayla iki epok, pencereleri örtüşmeyen en az
iki bağımsız zaman örneğini garanti eder. Daha sıkı bir kapı (≥ 3 örtüşmeyen epok) ana tanımda da geçiyor (2017 /
2020 / 2023: 15 / 14 / 10) ama aşama 0 küçülmesinden sonra 2023'te kırılır; bu yüzden seçilmedi. Kapı altında aday
elenmez. Ek 2'nin kapısı "≥ 5 yıl arayla iki epok" idi; orada T tanımı farklıydı. Burada 3 yıl, iki pencerenin
örtüşmemesi için yeterli ve gerekli olan aralıktır. Değişiklik Ek 2'nin Z doluluğu görüldükten sonra, dv/v görülmeden
yapıldı. 5 yıl arayla kapı burada da geçer, ama tam sınırdadır (2017 ve 2023: 15 ve 10 yer).

**4.5 Kapalı hüküm listesi ve kalıplar.** Köşeli parantezler otomatik doldurulur; başka metin eklenmez.

| Hüküm adı (aynen) | Adım | Şart | Zorunlu ek metin |
|---|---|---|---|
| veri yok (aşama 0) | 0 | kapı tutmadı | "T başına dolu yer: [..]" "; bilgi satırı 0: σ̂_Δ [..] % ([L–U]), q95 [..] % ([L–U]), n [..], yer [..], T [..]" ya da "; bilgi satırı 0: hesaplanmadı (n = [..], yer = [..])" |
| veri yok (aktarım hızı) | 0 | §5.3 madde 4 | "aşama H hızları [..] KiB/s; medyan [..]; V_D / v = [..] gün; bilgi satırı 0: hesaplanmadı (indirme yok)" |
| veri yok (indirme bütçesi) | 0 | §5.3 kesik koşu | "tamamlanan T: [..]; T başına yer: [..]; etkin süre [..] gün, takvim [..] gün; bilgi satırı 0: [..]" |
| veri yok (gün doluluğu) | 1 | kapı tutmadı | "T başına dolu yer: [..]" "; bilgi satırı 0: σ̂_Δ [..] % ([L–U]), q95 [..] % ([L–U]), n [..], yer [..], T [..]" ya da "; bilgi satırı 0: hesaplanmadı (n = [..], yer = [..])" |
| geçersiz (kod) | 2, 3 | §4.3 adım 2–3 | sapan dizi sayısı ya da medyan oran |
| veri yok (ε geçerliliği) | 4 | kapı tutmadı | "T başına geçerli yer: [..]" "; bilgi satırı 0: σ̂_Δ [..] % ([L–U]), q95 [..] % ([L–U]), n [..], yer [..], T [..]" ya da "; bilgi satırı 0: hesaplanmadı (n = [..], yer = [..])" |
| taban ölçüldü; TR-5b (c) karşılandı | 5 | U(σ̂) < %0,20 | Kalıp T |
| taban ölçüldü; TR-5b (c) karşılanmadı | 5 | L(σ̂) > %0,245 | Kalıp T |
| taban ölçüldü; TR-5b (c) belirsiz | 5 | öteki | Kalıp T |

Ara durum (hüküm değil): "ertelendi (aktarım hızı)", ek metin "ölçülen hız [..] KiB/s (ölçüm [..] adet); V_D / v =
[..] gün". En çok 5 gün sürer (§4.3 adım 0).

**Kalıp T:** "Marmara KO ağında [kademe], [n] yer-penceresinde ([yer] yer, T [ilk]–[son]), olaysız pencerelerde tek
istasyonun bir yıllık dv/v düzey değişiminin (0,5–2 Hz, TR-5b ölçüsü) örneklem %95 niceliği q95 = [..] %'dir (%95 iki
yönlü önyükleme aralığı [L–U]; benzetimde bu aralık gerçek değeri 0,79–0,97 olasılıkla kapsar). σ̂_Δ = [..] % (%90 iki
yönlü önyükleme aralığı [L–U]). q95, tek istasyonda %5 yanlış alarm oranındaki saptama eşiğidir. Bu büyüklükte bir
düzey değişimi yaklaşık yarı yarıya saptanır. %80 olasılıkla saptanacak değişim, normal yaklaşımla, ≈ q95 + 0,84 ·
σ̂_Δ = [..] %'dir. Bu bir olasılık ya da alarm eşiği değildir. Ölçü istasyon çevresindeki sığ ortamı örnekler. Zincir
bu ön kayıtta Marmara'da gerçek bir hız değişimiyle sınanmadı; mevsimsel genliğin yer medyanı (bilgi satırı 11)
[..] %, 2019 Silivri δ_ko'su (bilgi satırı 14) [..]."

**4.6 Anlam.**
- **Karşılandı:** TR-5b (c) şartının σ yarısı Marmara verisinde tutar. Bu, yeni bir ön kayıtla yeniden açmanın
  dayanaklarından biridir; tek başına yeniden açma değildir. Nedenleri: (1) TR-5b'nin kontrolleri Marmara'da değil.
  (2) TR-5b aşama 0'da K₀ = 18 < 20 ile kapandı; yeni ön kayıt K kapısını σ̂_Δ ile yeniden türetmelidir. (3) TR-4
  zincirin gerçek bir hız değişimini gördüğünü göstermez (Z10); duyarsız bir zincir de küçük σ̂ üretir. Bu yüzden (c)
  yoluyla açılan her ön kayıt, σ̂_Δ'ya dayanmadan önce gerçek olaylı bir pozitif kontrolü (TR-5b P2 ya da eşdeğeri)
  geçmek zorundadır.
- **Karşılanmadı:** σ_Δ kontrol düzeyinde de %0,20'nin üstündedir. TR-5b (c) yolu bu ölçüyle açılmaz. Marmara'da tek
  istasyonla yıl ölçekli bir düzey değişimi ancak q95'ten büyükse olaysız yıllardan ayrılır (Kalıp T).
- **Belirsiz:** Veri σ_Δ'yı %0,2'ye göre ayıracak kadar kesin değil; taban sayıları yine yazılır.
- **Veri yok:** Ölçü bu veriyle kurulamadı. Aday elenmez.
- **Geçersiz:** Kod hatası; sayılar yorumlanmaz.

## 5. Koşu düzeni, hacim, süre

**5.1 Aşama 0 (gerekli).** KOERI'nin kullanılabilirlik (availability) servisi doluluk için güvenilmez kabul
edilir; doluluk TR-5 Ek 2'deki gibi dataselect yoklamasıyla ölçülür. TR-5 yalnız Z'yi yokladı. TR-5b aşama 0'ı Z ay sayısının ötesinde aygıt (≈ %9) ve üç
bileşen/yatay (≈ %9) küçülmesi gösterdi; TR-4'ün kapısı dar olduğu için bu küçülme indirmeden önce ölçülmelidir.
`tr5b_asama0.py`'nin yoklama yöntemi (kısa dataselect isteği, tek akış, istekler arası ≥ 2 sn) değiştirilmeden:

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

Aşama 0 betiği `kayit/turetme/tr4/tr4_asama0.py`'dir. `tr5b_asama0.py`'nin düzeltilmiş hâlinden (sürüm 3)
türetilir ve İNCELEME-1 İ1-E4'ün 14 şartını karşılar. Ağsız kuru kipte ve sahte bir yanıtlayıcıyla sınanır. Betik
bağımsız bir kod incelemesinden geçer ve ilk ağ isteğinden önce dondurulur (§5.6).

**5.2 Aşama H (hız).** 8 istek, üretim biçiminde. Her istek, tek bir istasyonun 5 gününün 4 saatlik üç bileşen
penceresini tek bir dataselect POST isteğinde ister (≈ 28 MB). İstasyon ve günler ana örneklemin yer-pencerelerinden,
2014–2023 içinden, `sha256("tr4-asamaH|20261202")` tohumuyla seçilir. Tek akış, istekler arası ≥ 2 sn. İstek başına en
çok 15 dk; aşılırsa o ana kadarki bayt ve süre sayılır. v = Σ bayt / Σ süre (bağlantı ve bekleme dahil). Gövde
çözülmez, açılmaz, saklanmaz; yalnız bayt sayısı ve sha256 yazılır. Bayt / beklenen örnek sayısı Z9'u ölçer.
KOERI POST'u reddederse istekler gün gün GET ile atılır, v bu biçimle ölçülür ve üretim de bu biçimle yapılır.
Gerekçe: 341 ve 633 KiB/s ≤ 1 MB'lık tek isteklerden geldi, 40 KiB/s 11,2 MB'lık 284 sn'lik sürekli aktarımdan.
Üretim istekleri istasyon-ay başına 110–170 MB'tır. Hız ancak üretim boyutundaki isteklerle ölçülür. Bu istekler
ölçüde kullanılmaz.

**5.3 Kademe, bütçe ve kesik koşu (veri görülmeden; yalnız v'den ve aşama 0'ın hacminden).** V_A ve V_C, aşama 0'dan
sonra dolu kalan yer-pencerelerinin §5.4 formülüyle hacmidir (21 yerde 298,5 / 196,7 GB). V_D, bunların T 2017–2021
kısmıdır (21 yerde 153,6 GB; 74 yer-penceresi; T başına 15 / 16 / 15 / 14 / 14 yer). **Bütçe:** etkin indirme süresi
21 gün (504 iş-saati) ya da ilk indirme isteğinden itibaren 42 takvim günü; hangisi önce dolarsa.
1. V_A / v ≤ 7 gün → **A**.
2. Değilse V_D / v ≤ 21 gün → **C**.
3. Değilse aşama H, en az 2 gün arayla en çok 2 kez daha koşulur. v üç ölçümün medyanıdır; 1–2 yeniden uygulanır.
4. Hâlâ seçilmezse hüküm **"veri yok (aktarım hızı)"**dır.

**Kronolojik sıra ve kesik koşu.** İndirme ay ay gider: 2014-01'den 2023-12'ye, her ayda yerler kod sırasıyla. Bir
yer-penceresi, bütün istasyon-ay istekleri kesin kodla tamamlanınca "indirildi" sayılır. Bütçe dolarsa indirme durur.
Analiz yalnız bütün yer-pencereleri indirilmiş T'lerle yapılır. Kalıp T'de kademe "[A | C], kesik, T [ilk]–[son]"
diye yazılır. Bütçe dolduğunda T 2017–2021 tamamlanmamışsa ya da tamamlanan T'lerle kapı (§4.3 adım 0) tutmuyorsa hüküm
**"veri yok (indirme bütçesi)"**dır. Kesme yalnız takvime bağlıdır: indirme bitmeden ya da kesilmeden hiçbir ε ya da Δ
hesaplanmaz (§5.5).

**Önceden bildirilen süreler** (21 yer; v = 23 / 40 / 83 / 106 / 341 KiB/s): V_C 97 / 56 / 27 / 21 / 6,5 gün;
V_D 76 / 43 / 21 / 16 / 5,1 gün. 40 KiB/s ve altında kapıyı koruyan hiçbir 0 € tasarım bütçeye sığmaz. Bu hızlarda
"veri yok (aktarım hızı)" beklenen sonuçtur.

Kural tek akış ister. İki paralel akış, KOERI ile özel düzen ya da T veya yer kapsamının değiştirilmesi yeni sürüm ve
yeni inceleme ister. Sunucu KOERI hızını artırmaz.

**5.4 Hacim ve süre** (`tr4_onkayit_sayim.json` → `hacim`; bayt = saat × 3600 × 100 sn⁻¹ × 3 bileşen × 1,3 bayt;
1,3 bayt/örnek TR-5 §5.1'de tek bir örnekte ölçüldü (KO.ISK HHZ, 1 gün, 11,2 MB → 1,30); yatay bileşenler ve öteki
istasyonlar için ölçülmedi. Aşama H oranı yeniden ölçer; 21 yer, ana T 2017–2024).

| Kademe | İstasyon-gün | GB | 23 KiB/s | 40 KiB/s | 341 KiB/s | 633 KiB/s (2 akış) | 1 hafta için gereken |
|---|---|---|---|---|---|---|---|
| **A** (her gün, 4 s) | 53 150 | 298,5 | 147 g | 84 g | 9,9 g | 5,4 g | 486 KiB/s |
| **C** (1–20. gün, 4 s) | 35 020 | 196,7 | 97 g | 56 g | 6,6 g | 3,6 g | 320 KiB/s |
| H (her gün, 3 s; reddedildi) | 53 150 | 223,9 | 110 g | 63 g | 7,5 g | 4,1 g | 365 KiB/s |
| E (16 gün, 2 s; reddedildi) | 28 012 | 78,7 | 39 g | 23 g | 2,7 g | 1,4 g | 128 KiB/s |

İndirilen günler istasyon-ay başına bir dataselect isteğinde toplanır (1752 istek). Bilgi satırı 13'ün ek hacmi
2,4 GB (A) ya da 1,8 GB (C).

**5.5 0 € bulut düzeni.** Her iş ≤ 2 saat, bir durum dosyası (jsonl: istasyon-ay, bayt, sha256, sonuç) tutar ve
kaldığı yerden sürer. Ham veri istasyon-ay işlendikten sonra silinir. Saklanan,
**saatlik** ÇİF'lerdir (3 çift × 2401 gecikme × float32 ≈ 29 KB/saat; 4 saatlik günde ≈ 115 KB). Ayrıca her
saat-bileşen için 0,5–2 Hz RMS'i ve örnek tamlığı saklanır. Gerekçe: TR-5b §3.2 adım 4'ün enerji reddi, medyanı her
yer-penceresinin kendi [T − 1095, T − 8] saatlerinden alır. Ardışık T'ler aynı günü farklı medyanlarla görür, bu yüzden
günlük ÇİF T'den bağımsız saklanamaz. Günlük ÇİF her yer-penceresi için saatlik ÇİF'lerden, o pencerenin medyanıyla
kurulur. 1b'nin gün doluluğu (üç bileşen, saat ≥ %99 tamlık) da saklanan tamlıktan hesaplanır. Saklama C'de ≈ 4,0 GB,
A'da ≈ 6,1 GB'tır. Dosyalar `/mnt/project-files/` altına yazılır: istasyon-ay başına bir dosya, sha256'sıyla, geçici
adla yazılıp yeniden adlandırılarak. Durum dosyası da oradadır ve her iş oradan sürer. Yerel disk tepe değeri bir
istasyon-aylık ham veri (≈ 0,11–0,17 GB) ile o ayın saatlik ÇİF'idir. **İndirme bitmeden ya da §5.3'e göre
kesilmeden hiçbir ε ya da Δ hesaplanmaz.** Yalnız saatlik ÇİF, RMS ve tamlık yazılır. C, 341 KiB/s'de ≈ 80 iki
saatlik iştir. İşlem süresi indirmenin yanında küçüktür. Bir istasyon-günün ön işlemi ve saatlik ÇİF'i ≈ 0,54 sn sürer
(yapay veri, numpy, tek çekirdek; miniSEED çözme ve germe hariç; İNCELEME-1). Bu C'de ≈ 5,3, A'da ≈ 8 saattir. İlk
indirilen istasyon-ayda gerçek süre ölçülür ve günlüğe yazılır. Başarısız istek oranı %5'i aşarsa ε'dan önce tek yeniden deneme turu (TR-5b §5).

**5.6 Dondurma.** Ön kayıt, `tr4_asama0.py` ve onun ağsız provası aşama 0'ın ilk ağ isteğinden önce dondurulur ve push
edilir. dv/v koşu kodu (`tr4_kosu.py`) bağımsız kod incelemesinden sonra ve ilk dalga formu indirme isteğinden önce
dondurulur; sha256'sı kayda geçer. Bundan sonra kod yalnız §11'in "geçersiz (kod)" yoluyla değişir. Koşu kodu
dondurulmuş saatlik ÇİF'lerden (§5.5) günlük ÇİF'i her yer-penceresi için yeniden kurar. Aşama 0 bir kez koşulur:
önbellek silinmez, yeniden yoklama yapılmaz. Tek yeniden deneme, İ1-E4 madde 6'nın kesin olmayan kodlar için
tanımladığıdır. `say` bir kez, bütün istekler tamamlanınca koşulur. `asama0_sonuc.json`, `onbellek.jsonl` ve
`istekler.json`'un sha256'ları kayda geçer ve push edilir. G0'dan sonra aşama 0'ın hiçbir kuralı değiştirilemez.

## 6. Yapay doğrulama ve kesinlik

Hepsi `tr4_guc.py` ile, `tr5b_yapay.py` ve `tr5b_yapay2.py` değiştirilmeden içe aktarılarak, sabit tohumlarla.
Yapay dizi TR-5b'ninkidir: üç SNR düzeyi (4 saatlik günde CC10 ≈ 0,5 / 0,7 / 0,9), %0,05 mevsimsellik, saat reddi
%10, gün kesintisi %10 + 30 günlük bir boşluk, 100 tekrar.

**6.1 Ölçüm gürültüsü ve kademe** (`tr4_guc_sonuc.json` → `olcum`; σ_ölçüm = sabit ε'lu dizide Δ'nın standart
sapması; oran = −%0,1 eklemesinin geri ölçülen payı, medyan [%5; %95]).

| Kademe | Geçerli Δ (CC10 0,5 / 0,7 / 0,9) | σ_ölçüm % (0,5 / 0,7 / 0,9) | Oran, CC10 0,5 |
|---|---|---|---|
| **A** her gün 4 s | 1,00 / 1,00 / 1,00 | 0,019 / 0,011 / 0,005 | 0,93 [0,90; 0,96] |
| H her gün 3 s | 0,89 / 1,00 / 1,00 | 0,025 / 0,011 / 0,006 | 0,91 [0,86; 0,95] |
| B her gün 2 s | 0,00 / 1,00 / 1,00 | – / 0,015 / 0,007 | – |
| **C** 1–20. gün 4 s | 0,91 / 1,00 / 1,00 | 0,026 / 0,011 / 0,006 | 0,90 [0,84; 0,95] |
| G 1–20. gün 3 s | 0,01 / 1,00 / 1,00 | – / 0,015 / 0,007 | – |
| D 1–20. gün 2 s | 0,00 / 1,00 / 1,00 | – / 0,018 / 0,009 | – |
| F 1–16. gün 4 s | 0,42 / 1,00 / 1,00 | 0,030 / 0,014 / 0,007 | 0,89 [0,82; 0,95] |
| E 1–16. gün 2 s | 0,00 / 0,87 / 0,96 | – / 0,022 / 0,010 | – |

**Sonuç.** Yapay ölçüm gürültüsü %0,2'nin onda biri mertebesindedir. σ_Δ'yı gerçekte belirleyecek olan ortam
değişkenliğidir (hidroloji, ısı, kaynak değişimi), yapay dizide yoktur. Kademe seçimi bu yüzden σ_ölçüm için değil,
Δ'nın düşük SNR'de **kurulabilmesi** için yapıldı. TR-5b §3.1'in √6 notu burada da geçerlidir.

**Dondurulmuş dizilerde kademe C** (`tr4_yapay_ref.json`, TR-5b npz'nin 60 dizisi, ayın 1–20. günleri): 58 dizide
Δ geçerli (eksik 2'si CC10 ≈ 0,5'te); medyan oran 0,954 (0,825–1,004); SNR'ye göre medyan 0,90 / 0,95 / 0,98.
F (1–16. gün): 55 dizi, 0,962 (0,695–1,002). Bu dosya 2. adımın (b) başvurusudur.

**6.2 σ̂_Δ ve q95'in kesinliği** (`tr4_guc_sonuc.json` → `kesinlik`). Model: yer-pencere Δ =
[L(T−1) − (L(T−2) + L(T−3))/2] · ölçek + ölçüm gürültüsü; yıllık düzey L = √ρ · C(yıl) + √(1−ρ) · U(istasyon, yıl);
C ve U AR(1) (φ); bir değişkede U Student-t(4). Ölçek, Δ'nın gerçek σ'sını σ_Δ yapar. Hücre deseni ana örneklemin
kendisi (`tr4_pencereler.csv`); her hücre ek %10 olasılıkla düşer (gün doluluğu ve yatay kaybı varsayımı).
R = 200 benzetim, her birinde B = 300 iki yönlü önyükleme.

**Ana satır** (kademe C, ρ = 0,3, φ = 0, normal; ≈ 90 geçerli hücre). σ̂ / σ ve q̂95 / q95 oranları benzetimler
arası [%5; medyan; %95]; aralık genişliği medyan (U − L) / σ; kapsama = %90 aralığının gerçek değeri içerme payı;
son üç sütun (c) hükmünün olasılığı.

| Gerçek σ_Δ % | Gerçek q95 % | σ̂ / σ | q̂95 / q95 | σ aralığı genişliği | Kapsama σ / q95 | Karşılandı | Belirsiz | Karşılanmadı |
|---|---|---|---|---|---|---|---|---|
| 0,05 | 0,11 | [0,79; 0,96; 1,29] | [0,81; 0,96; 1,15] | 0,70 | 1,00 / 0,91 | 1,00 | 0,00 | 0,00 |
| 0,10 | 0,20 | [0,77; 0,96; 1,21] | [0,80; 0,96; 1,17] | 0,71 | 0,99 / 0,93 | 1,00 | 0,00 | 0,00 |
| 0,15 | 0,30 | [0,79; 0,96; 1,24] | [0,77; 0,95; 1,19] | 0,68 | 0,99 / 0,88 | 0,59 | 0,42 | 0,00 |
| 0,20 | 0,40 | [0,75; 0,98; 1,25] | [0,79; 0,96; 1,16] | 0,70 | 0,97 / 0,90 | 0,03 | 0,97 | 0,00 |
| 0,30 | 0,59 | [0,75; 0,99; 1,30] | [0,77; 0,98; 1,15] | 0,71 | 0,99 / 0,88 | 0,00 | 0,73 | 0,28 |

**Duyarlılık** (karşılandı olasılığı σ = 0,10 / 0,15'te; karşılanmadı olasılığı σ = 0,30'da):

| Değişke | Karşılandı (0,10 / 0,15) | Karşılanmadı (0,30) | q95 kapsaması |
|---|---|---|---|
| A, ρ 0,3 | 1,00 / 0,54 | 0,34 | 0,88–0,95 |
| C, ρ 0 | 1,00 / 0,48 | 0,40 | 0,94–0,97 |
| C, ρ 0,6 (güçlü ortak yıl bileşeni) | 0,97 / 0,43 | 0,12 | 0,75–0,85 |
| C, ρ 0,3, φ 0,5 | 1,00 / 0,56 | 0,22 | 0,89–0,91 |
| C, ρ 0,3, t4 kuyruk | 1,00 / 0,73 | 0,06 | 0,85–0,92 |
| C, örtüşmeyen T 2018/2021/2024 (≈ 34 hücre) | 0,99 / 0,47 | 0,00 | 0,75–0,78 |
| C, yalnız T 2021–2024 (≈ 38 hücre) | 0,97 / 0,37 | 0,01 | 0,77–0,82 |
| C, istasyonların yarısı (≈ 50 hücre) | 0,98 / 0,30 | 0,04 | 0,86–0,92 |

**Okuma.**
- **σ̂_Δ yansız** (medyan oran 0,95–1,00) ve tek koşuda gerçek değerin ≈ ±%25'i içinde (ρ 0,6'da −%30 / +%40).
- **Hüküm bilerek asimetriktir.** TR-5b için yalnız "karşılandı" bir yeniden açma dayanağıdır. "Belirsiz" ve
  "karşılanmadı" aynı sonucu doğurur: dayanak yok. Bu yüzden sınırlanan hata yanlış "karşılandı"dır. σ_Δ = %0,20'de
  "karşılandı" olasılığı ρ 0,3'te 0,01–0,03, ρ 0,6'da 0,08; T 2017–2021 kesik koşuda 0,02 / 0,10. σ_Δ %0,10'da
  "karşılandı" 0,95–1,00, %0,15'te ≈ 0,4–0,6 olasılıkla gelir. "Karşılanmadı" (L > %0,245; İ1-Ö1) σ_Δ %0,30'da bile
  ≤ 0,02 olasılıklıdır; yalnız σ_Δ %0,30'un belirgin üstündeyse olasıdır. Bu önceden kabul edilir; "belirsiz" hükmü
  σ̂'yı ve aralığını yine yazar. Kaynak: İNCELEME-1 `inc1_kesinlik.json`, `inc1_kesinlik_D.json`.
- **q95 aralığı** 2,5.–97,5. yüzdeliklerdir (§4.2). Kapsaması ρ 0,6'da ve az epokta yine 0,79–0,89'dur. Bu, ortak yıl
  bileşeninin (ρ) bu örneklemde iyi kestirilemeyeceği anlamına gelir (Z8). Bilgi satırı 5 bu bileşeni kaba olarak
  yazar.
- A ile C arasında kesinlik farkı yok denecek kadar küçük; kesinliği yer ve epok sayısı belirler, gün örneklemesi
  değil. Ana örneklemin yarıya inmesi (aşama 0 küçülmesinin kötü ucu) σ aralığını ≈ 0,7'den ≈ 0,93 σ'ya genişletir.

## 7. Bilinen karıştırıcılar

- **Hidroloji ve mevsim.** Ay eşlemesi durağan mevsimselliği düşürür; çok yıllı kuraklık ve yeniden beslenme
  düşürülmez ve tabanın bir parçasıdır. Bu bilinçli: taban, olaysız yılların bu değişkenliği dahil saçılımıdır.
- **Kültürel gürültü.** İstanbul istasyonlarında gece penceresi bile trafik ve inşaat içerir. 2020 kapanmaları
  (Mart–Haziran 2020) T 2021'in C, T 2022'nin B, T 2023'ün A diliminde; gürültü kaynağı değişimi Δ'ya sızabilir. Bilgi satırı 8 T 2021'i
  dışlayarak yazar.
- **Aygıt ve kayıtçı değişimi.** TR-5b aygıt kuralı; üstveride görünmeyen değişimler (tepki aynı, kayıtçı farklı)
  yakalanmaz.
- **2019 Mw 5,7 artçı toparlanması.** 60 günlük maske, kosismik düşüşün yarı toparlanma süresinden (Napa ≈ 50 gün)
  kısa değil, ama uzun kuyruğu (Hobiger 2016, ≈ 0,55 yıl) kesmez. Etkilenen 9 yer-pencere bilinir; bilgi satırı 1
  onları dışlar.
- **Örtüşen pencereler.** Ardışık T'ler aynı yılları paylaşır; n = 102 bağımsız örnek değildir. Bu §4.2'deki
  iki yönlü önyüklemeyle ve bilgi satırı 3'le ele alınır.

## 8. Bilgi satırları (hükmü değiştirmez)

0. **Kapı altı taban** (yalnız "veri yok" hükümlerinde; §4.3): σ̂_Δ, q95, %90 / %95 iki yönlü önyükleme aralıkları,
   n, yer ve T listesi. Ek metin aynen: "Kapı altı; TR-5b (c) için dayanak değildir; hüküm [hüküm adı]."
1. Olaysızlık değişkeleri: ileri 2 yıl (N 86), M ≥ 7 için 500 km (N 46, kapı altı), pencere içinde M ≥ 5 ≤ 50 km
   olan yer-pencereler dışarıda (N 92), M ≥ 5,5 ≤ 100 km ±1 yıl (N 59, kapı altı). Her biri için σ̂, q95, aralık.
   Ek değişke: pencerenin kendisinde ([T − 1095, T − 8]) M ≥ 7 ve ≤ 1000 km olayı olan yer-pencereleri dışarıda (Samos
   2020 ve Kahramanmaraş 2023; T 2021–2024 düşer; N 60, T 2017–2020; kapı geçer).
2. Doluluk değişkeleri: gevşek (N 118) ve sıkı (N 72, kapı altı).
3. Örtüşmeyen T kümeleri: 2017/2020/2023 ve 2018/2021/2024 (her biri N 39).
4. İşaretli dağılım: Δ'nın medyanı ve %2,5 / %97,5 nicelikleri (yön asimetrisi).
5. Ağ ortalaması: her T için yerlerin ortalama Δ'sı ve T'ler arası saçılımı (ortak bileşen; n = 8, çok kaba).
6. Kontrol düzeyi eşleniği: aynı T'den rastgele 2 yerin ortalamasının σ̂'sı (TR-5b'nin σ_Δ'sıyla doğrudan kıyas).
7. Yer başına tablo: n, medyan Δ, MAD, geçerli çift sayısı, saat reddi oranı.
8. T 2021'siz (kapanma) σ̂ ve q95.
9. Kademe A seçildiyse kademe C alt kümesinin σ̂ ve q95'i.
10. 2–4 Hz bandı (TR-5b bilgi bandı) ve eğilimden arındırılmış Δ.
11. Mevsimsel genlik: yer başına aylık ortalama ε'nın tepeden tepeye genliği (Hillers 2015'in ≈ %0,2'siyle kıyas).
12. Gerilme mertebesi: q95 / 0,5 MPa⁻¹ (Hillers 2014; bant farklı, yalnız mertebe).
13. Nisan 2025 M6,2, SLVT: δ_ko (±%2 ızgara, TR-5b §4.2 adım 8 tanımı; T = 2025-04-23; TR-5b P2'deki gibi veri
    [T − 400, T + 30], başvuru [T − 400, T − 8])
    ve kendi A = 0 dağılımına göre yeri (benzetimden: tek istasyonda saptama olasılığı ≤ 0,27). Aşama 0'da SLVT
    2024-03…2025-05 doluluğu tutmazsa satır "veri yok" yazar. Kademeden bağımsız olarak [T − 69, T + 30] her gün
    indirilir, [T − 400, T − 70] kademeye göre örneklenir (§5.4'ün ek hacmi bu tanımladır).
14. 26 Eylül 2019 Silivri Mw 5,7 (`us70005lkl`), SLVT (36,5 km), CRLT (42,9 km), CTKS (47,7 km). δ_ko TR-5b §4.2
    adım 8 tanımıyla, ±%2 ızgarayla hesaplanır; M5 maskesi bu satırda uygulanmaz. İstasyon başına ve ortalama
    yazılır. Veri ana örneklemin indirdiği günlerdir (T 2020 penceresi); ek indirme yoktur. Kademe C'de olay sonrası
    yalnız ayın 1–20. günleri vardır. Saptama olasılığı düşüktür (§3.4'teki 0,05–0,27 mertebesi); "görülmedi"
    bilgisizdir.

## 9. Karşılaştırma ve literatür

Yayımlanmış bir Marmara dv/v serisi bulunamadı (OpenAlex aramaları). TR-4'ün sayısı bu yüzden bir ilk ölçümdür;
karşılaştırma başka bölgelerle ve mertebe düzeyindedir.

| Kaynak | Söylediği | Durum |
|---|---|---|
| Hillers 2015 (San Jacinto), 10.1093/gji/ggv151 | Mevsimsel tepeden tepeye ≈ %0,2, 0,5–2 Hz | Doğrulandı (TR-5 §6.1; TR-5b §3.7) |
| Meier 2010 (Los Angeles), 10.1111/j.1365-246x.2010.04550.x | ≈ %0,1 değişimler ölçülebilir | Doğrulandı |
| Sens-Schönfelder ve Wegler 2006 (Merapi), 10.1029/2006gl027797 | Günlük çözünürlükte ≈ %0,1 doğruluk | Doğrulandı |
| Taira 2015 (Napa M6,0), 10.1002/2015gl065308 | Kosismik ≈ %0,08 | Doğrulandı |
| Hillers 2014 | Gelgit duyarlılığı ≈ 0,5 MPa⁻¹ (2–8 Hz, sığ) | Doğrulandı; bant farklı |
| Clements ve Denolle 2023 (Kaliforniya, 700 istasyon), 10.1029/2022jb025553 | Çok yıllı hidrolojik dv/v | Nitel doğrulandı; genlik **doğrulanamadı** |
| van Dinther 2020 (DANA, Kuzey Anadolu, EGU özeti) | 2012–2013 dv/v | Sayı yok; **doğrulanamadı** |
| Delouche 2022 (Yunanistan) | "Güçlü mevsimsellik" | Sayı yok; **doğrulanamadı** |

Beklenti (önceden yazılır, hükmü etkilemez): mevsimsel genlik ≈ %0,1–0,2 ise ve ay eşlemesi onu düşürürse, kalan
yıllar arası değişkenlik σ_Δ ≈ %0,05–0,15 mertebesinde olabilir. Bu bir tahmindir, dayanağı yukarıdaki doğrulanmış
genliklerdir; yanlış çıkması TR-4'ün ölçmek istediği şeydir.

## 10. Marmara'ya anlam ve TR-5b ile ilişki

- TR-4 tek başına bir izleme ya da alarm önerisi değildir. TR-5b H1 verirse, TR-5b §10'un ileriye dönük izleme ön
  kaydı TR-4'ün q95'ini gürültü tabanı olarak kullanır.
- TR-5b H0 verirse TR-4 yalnız ölçüm sınırı cümlesi (Kalıp T) olarak kalır.
- TR-5b güç yok ile kapanırsa ve TR-4 "(c) karşılandı" verirse, TR-5b §11 (c) yolu açılabilir; açılış yeni ön
  kayıt ister. TR-5b aşama 0'da "güç yok (aşama 0)" ile kapandı (K₀ 18 / 20; ZINCIR Halka 7). (c) yolunun açılması, K
  kapısının da yeni ön kayıtta yeniden türetilmesini gerektirir.
- **İstanbul için mutlak olasılık bu belgenin hiçbir yerinde yazılmaz ve hiçbir sonuçtan türetilmez.**

## 11. Yeniden açma şartı

"Veri yok" ile kapanırsa yeniden açma yeni bir sürümle ve şu yollardan biriyle olur:
- (a) "veri yok (aktarım hızı)" ile kapanırsa: en erken 30 gün sonra, tasarım değişmeden, §5.2–5.3 aynen bir kez daha
  koşulabilir. Bu yeni sürüm değildir; sürüm 2'nin değişiklik kaydına yazılır ve inceleme gerektirmez. Aşama 0
  yeniden koşulmaz.
- (b) KO'nun kutudaki istasyon sayısını artıran yeni üstveri (≥ 2 yeni dolu yer);
- (c) T ≥ 2026 için kör olmayan veri: körlük kuralı kaldırıldığında, aynı tasarımla ileriye dönük uzatma.

"Taban ölçüldü" tek koşudur; parametre değiştirilerek yeniden koşulmaz. "Geçersiz (kod)" ile kapanırsa düzeltilmiş
kod yeni bir kod incelemesinden sonra aynı veride bir kez koşabilir; düzeltme kaydı hükümle birlikte yazılır. Bu
yeniden koşu bir kez yapılır. İkinci kez "geçersiz (kod)" verirse hüküm kesinleşir.

## 12. Zayıf noktalar (incelemecinin bakması gerekenler)

- **Z1. Aşama 0 betiği (İNCELEME-1 İ1-E4).** Şartlar İ1-E4'te. Betik ve ağsız provası dondurmadan önce yazılır,
  kod incelemesinden geçer.
- **Z2. Hız bilinmiyor (İNCELEME-1 İ1-E1).** Kural kapalıdır: A / C yalnız v'den, kronolojik sıra, 21 / 42 günlük
  bütçe, kesik koşu (en küçük küme T 2017–2021). 40 KiB/s ve altında sonuç "veri yok (aktarım hızı)"dır.
- **Z3. Kapı payı (İNCELEME-1 İ1-E2).** TR-5b'de Z dışı pencere kaybı ≈ %19'du (üç bileşen %7,9, aygıt %9,6, yatay
  %2,4). 31 → 18 (%42) bir küme sayısıdır ve Z kaybını içerir. Gün düzeyi kayıp bilinmiyor. Rastgele kayıpta kapının
  kırılma olasılığı %20'de 0,02–0,13, %30'da 0,26–0,43, %40'ta 0,69–0,75; tek tip kayıpta kapı %29'da kırılır. Kapı
  kırılırsa hüküm "veri yok"tur ve σ̂_Δ bilgi satırı 0'da yazılır.
- **Z4. Birim farkı (İNCELEME-1 İ1-Ö1).** "Karşılandı" eşiği U < %0,20 (tutucu), "karşılanmadı" eşiği L > %0,245
  (= 0,20 / 0,817). Bilgi satırı 6 kontrol düzeyi eşleniğini yazar, hükmü değiştirmez.
- **Z5. İşlem süresi (İNCELEME-1).** Kaba ölçüm ≈ 0,54 sn/istasyon-gün (C ≈ 5,3 saat, A ≈ 8 saat; miniSEED çözme
  ve germe hariç). İlk indirilen istasyon-ayda gerçek süre ölçülür.
- **Z6. Kademe C zincirden sapar.** Gün örneklemesi TR-5b'den farklıdır; yapay dizide geçer, gerçek veride
  (ii-a) ile sınanır. A ile C arasındaki gerçek fark ancak A seçilirse görülür (bilgi satırı 9).
- **Z7. Olaysızlık eşikleri yargıdır (İNCELEME-1 İ1-Ö5).** 150 / 300 / 1000 km ve [T − 5 y, T + 1 y) SAYIM §3.2'den
  alındı. Samos 2020 (M7,0), 300 km kuralıyla beş istasyonda T 2020–2024'ü dışlar (GONE, LAP, KRBG, EDC, KCTX; 20
  istasyon-penceresi). Öteki örneklem istasyonları ≥ 309 km'dedir ve içeride kalır. Kahramanmaraş 2023 (M7,8 / M7,5,
  664–985 km) T 2024'ün C diliminde içeride kalır. 500 km değişkesi kapıyı kırar. İki etki bilgi satırı 1'de ayrı yazılır.
- **Z8. Yapay modelde ortam gürültüsü yok.** §6.2'nin σ_Δ'sı serbest parametredir; gerçek değeri ve dağılım biçimi
  (kalın kuyruk, istasyonlar arası ilişki) bilinmiyor. t4 ve ρ değişkeleri yalnız duyarlılıktır.
- **Z9. 1,3 bayt/örnek (İNCELEME-1 İ1-K1).** TR-5 §5.1'de tek bir örnekte ölçüldü (KO.ISK HHZ, 1 gün, 11,2 MB →
  1,30); yatay bileşenler ve öteki istasyonlar için ölçülmedi. Aşama H oranı yeniden ölçer.
- **Z10. PK yok (İNCELEME-1 İ1-Ö3).** Uzak PK kapsam dışıdır. "Karşılandı", ancak gerçek olaylı bir PK'yi geçen yeni
  bir ön kayıtta dayanak olarak kullanılabilir. Bilgi satırları 11 ve 14 bağlayıcı olmayan iki işarettir.
- **Z11. Asimetri ve q95 aralığı (İNCELEME-1 İ1-Ö2).** Asimetri bilerek kabul edildi ve olasılıklar §6.2'de yazıldı.
  q95 aralığı %95 iki yönlü önyükleme aralığıdır; kapsaması kendi adıyla birlikte yazılır.
- **Z12. Benzetimin hücre birimi istasyondur, hükmünki yerdir.** ISK ve KAVV benzetimde ayrı sayıldı (22 istasyon,
  ≈ 110 hücre); hükümde tek yerdir (21 yer, 102). Fark ≈ %7; sonuçları değiştirmesi beklenmez, ama düzeltilmedi.

## 13. Defterle örtüşme

- **TR-5b:** TR-4 onun (c) şartını sınar. TR-5b kontrollerinde KO yok; indirme çakışması yok. TR-5b'nin P1'i ve 4.
  adımı TR-4'ün sayısını beklemez; ikisi bağımsız koşar.
- **TR-5 / SAYIM Ek 2:** Bu belgenin sayıları Ek 2'nin Z doluluğundan türetildi; Ek 2'nin 18 istasyonu ile buradaki
  22 istasyonun farkı T tanımından (Ek 2: 2017 ve 2022 için 10, burada yıllık T) ve olaysızlık kuralından gelir.
- **Marmara GNSS:** Dokunulmaz; TR-4 GNSS kullanmaz.
- **DD-5 (gelgit, güç yok):** Gerilme çevirisi yalnız bilgi satırı 12'dir.
- **FA-6:** Tek ana bant, tek ölçü çifti (σ̂, q95), tek hüküm adımı; ötekiler bilgi satırı.

## Ek: dosyalar ve yeniden üretim

Girdiler (depo dışı, `/mnt/project-files/turetme/tr5b-ham/`):
- `tr5_ham_ustveri_2026-11-12.tar.gz` (sha256 `27837799…`) → `marmara_fed_kanal.txt` (`dbcc3ba8ed75…`),
  `onbellek.jsonl` (`ce4fe524392b…`);
- `tr5b_kat_2026-11-12.tar.gz` (`1bdfec2c…`) → `m5_1990.csv` (`7369617d…`), `m5_2002.csv` (`0dd381d5…`),
  `m5_2010.csv` (`046a6f10…`), `m5_2018.csv` (`9c54cef3…`);
- `tr5b_yapay_ccf.npz` (`44189a31…`).

Çıktılar (`kayit/turetme/tr4/`):
- `tr4_onkayit_sayim.py` `5a6f9504f4a9014e7898e06cf78bdc5e964005e8c72b8bea33fdbdbb75f42691`
- `tr4_onkayit_sayim.json` `39e91fcecb2b6c9554a7f9d79569b1b81fc20427a72ca207244a85b5151cb2ee`
- `tr4_pencereler.csv` `166e42ea5b2fbe97ed608daf0f533252c13ef0959d78950c9b3213998915a4ef`
- `tr4_guc.py` `f4f1636035e0d9ee9d691c9e56002fc8373ac830651d20899138de2866f2894f`
- `tr4_guc_sonuc.json` `ed81dfd06660a1c2e986988e7f8e57ba884179fb4b91a0a39e04db90f6e31ee2`
- `tr4_yapay_ref.json` `238b6e09289db01819bb9ea1719fc8f964476d4653a5ab9557970ea14e0717b5`
- `tr4_asama0.py` `e5d8c33cdeb824b5103cf27f27436d1c1b7260b16684883e99078dfd3aa8c550` (İ1-E4; aşama 0 ve aşama H)
- `tr4_asama0_kuru.json` `ecbde36cb4782261e9a0979cf519c444fdcb56fa6655471c2e89d6064e6969e3` (kuru kip çıktısı; iki koşuda aynı)
- `tr4_asama0_prova.py` `6ce012b7e41a9667fdc91d91e32878e62059ff24328552ea65993791c8b631da` (ağsız sürdürme provası, İ1-E4 madde 12)
- `tr4_asama0_prova.json` `42adc1af54b85df15161028f9a23efb3fd7125155af7b913e76464f997ee90ae`


Komutlar (her biri `cd /home/user/knotenlinie` ile; `OMP_NUM_THREADS=1`):
```
python3 -I -B kayit/turetme/tr4/tr4_onkayit_sayim.py <ust/ham> <ust/doluluk/onbellek.jsonl> <kat/tr5b_kat>
python3 -I -B kayit/turetme/tr4/tr4_guc.py olcum
python3 -I -B kayit/turetme/tr4/tr4_guc.py pk
python3 -I -B kayit/turetme/tr4/tr4_guc.py ref /mnt/project-files/turetme/tr5b-ham/tr5b_yapay_ccf.npz
python3 -I -B kayit/turetme/tr4/tr4_guc.py kesinlik
```
`olcum` ve `pk` kipleri 4 süreçle koşar (`Pool(4)`). Paylaşılan makinede tek süreçle yeniden üretim
`inc1_yeniden.py olcum` biçimindedir (C | CC10 ≈ 0,5 satırı 29 sn).

Aşama 0 (`<g>` arşivin açıldığı dizin, `<ob>` aşama 0 dizini; ağ kipleri yalnız `--ag-onay` ile):
```
python3 -I -B kayit/turetme/tr4/tr4_asama0.py kuru    <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl
python3 -I -B kayit/turetme/tr4/tr4_asama0.py ustveri <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl <ob> 6000 --ag-onay
python3 -I -B kayit/turetme/tr4/tr4_asama0.py kur     <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl <ob> --ag-onay
python3 -I -B kayit/turetme/tr4/tr4_asama0.py yokla   <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl <ob> 6000 --ag-onay
python3 -I -B kayit/turetme/tr4/tr4_asama0.py say     <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl <ob>
python3 -I -B kayit/turetme/tr4/tr4_asama0.py hiz     <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl <ob> 6000 --ag-onay
python3 -I -B kayit/turetme/tr4/tr4_asama0_prova.py   <g>/ham/marmara_fed_kanal.txt <g>/doluluk/onbellek.jsonl <geçici_kök>
```
Süreler: sayım < 1 dk; olcum ≈ 19 dk; pk ≈ 2,5 dk; ref ≈ 1,5 dk; kesinlik ≈ 6 dk.

## Sürüm 1 → 2 değişiklik listesi

Kaynak: `TR-4_INCELEME-1.md` (tek ve son tur; DÜZELTMEYLE KABUL). Metinler incelemenin C bölümünden harfiyen işlendi.
Sürüm 1 `TR-4_marmara-hiz-tabani_ONKAYIT_surum1.md` adıyla saklandı.

| Bulgu | Yer | Değişiklik |
|---|---|---|
| İ1-E1 | Başlık "Koşu düzeni", §4.3 adım 0, §4.5, §5.2, §5.3, §11 (a) ve ilk cümle, Z2 | Aşama H 8 üretim biçiminde istek; kademe, bütçe (21 etkin / 42 takvim günü), kronolojik sıra, kesik koşu (en küçük küme T 2017–2021); iki yeni hüküm ("veri yok (aktarım hızı)", "veri yok (indirme bütçesi)"); "ertelendi" en çok 5 günlük ara durum |
| İ1-E2 | §4.3 giriş, §4.5 ek metinleri, §8 madde 0, Z3 | "Veri yok"ta dolu yer-pencereleri yine işlenir; bilgi satırı 0 ("kapı altı taban"); < 30 dolu yer-penceresinde indirme yok |
| İ1-E3 | §5.5, §3.2 Kademe C | Saatlik ÇİF, RMS ve tamlık saklanır (C ≈ 4,0 GB, A ≈ 6,1 GB); işlem süresi ≈ 0,54 sn/istasyon-gün; "gün" = yerel ortalama güneş tarihi d |
| İ1-E4 | §5.1 tablo ve son paragraf, Z1; `tr4_asama0.py` | İstek tablosu 26 / 468 / 84 / 15 / 30 / 8 = 631; aşama 0 betiği 14 şarta göre yazıldı, ağsız kuru kipte ve sahte yanıtlayıcıyla sınandı |
| İ1-Ö1 | §1 son madde, §4.3 adım 5, §4.5, Z4 | "Karşılanmadı" eşiği L > %0,245 (= 0,20 / 0,817) |
| İ1-Ö2 | §4.2, Kalıp T, başlık "Tek cümle", §6.2 "Okuma" iki madde, §4.6 "Karşılanmadı", Z11 | σ için %90, q95 için %95 iki yönlü önyükleme aralığı; kapsamalar; q95'in anlamı (%5 yanlış alarm, yarı yarıya saptama, %80 için q95 + 0,84 σ̂_Δ) |
| İ1-Ö3 | §4.6 "Karşılandı", §8 madde 14, §3.4 son paragraf, Z10 | "Karşılandı" koşullu (gerçek olaylı PK şartı); bilgi satırı 14 (2019 Silivri) |
| İ1-Ö4 | §5.6, §11 son cümle | Dondurma anı (ön kayıt + aşama 0 betiği ve provası ilk ağ isteğinden önce; koşu kodu ilk dalga formu isteğinden önce); aşama 0 tek koşu; "geçersiz (kod)" sonrası tek yeniden koşu |
| İ1-Ö5 | Z7, §2.3, §8 madde 1 | Samos cümlesi düzeltildi; pencere içi M ≥ 7 ≤ 1000 km değişkesi |
| İ1-K1 | §5.4, Z9 | 1,3 bayt/örnek tek örnekte ölçüldü |
| İ1-K2 | Z5 | İşlem süresi kaba ölçümü |
| İ1-K3 | Başlık, §5.1 | 771 → 631 istek (başlıkta İ1-E1'in "≈ 630 hafif istek" metni); `tr4_onkayit_sayim.py` değişmedi |
| İ1-K4 | §4.4 sonu | Kapının Ek 2'den farkı |
| İ1-K5 | §8 madde 13 | Bilgi satırı 13'ün örneklemesi |
| İ1-K6 | §9 | "Doğrulandı (TR-5 §6.1; TR-5b §3.7)"; beş DOI |
| İ1-K7 | Ek | Paralel süreç notu |
| İ1-K8 | §10 üçüncü madde | TR-5b'nin aşama 0 kapanışı |
| İ1-K9 | Durum satırı, §0, bu liste | Sürüm 2, DONDURULDU; öncelik sırasına `TR-4_INCELEME-1.md` |

**İnceleme ve denetim dosyaları (sha256):**
- `kayit/onkayit/TR-4_INCELEME-1.md` `2769aaefa461bcae276bde73214bc5c5e48df91aa58e9c232b55fdb11e838fa2`
- `kayit/onkayit/TR-4_marmara-hiz-tabani_ONKAYIT_surum1.md` `ef4d04f928246352fa7ff3c1217b65b5406a56b39668ec19069f3a1dc92fb432`
- `kayit/turetme/tr4/inc1/inc1_islem_suresi.py` `c2b0ec805e7977d97665da378e7030dddbea75b5220cb8f337e4accfa74395fe`
- `kayit/turetme/tr4/inc1/inc1_kapi_hacim.py` `14627e3093ac64416e772466dde6c6f199e5ac753b303ab8722d1b083e3cf0f5`
- `kayit/turetme/tr4/inc1/inc1_kapi_hacim.json` `113a451c46711b82ca2200f6990db5187443daf9e831638eddba0616d5eec9f3`
- `kayit/turetme/tr4/inc1/inc1_kesinlik.py` `cd64b8bc644024b233305b70ad0ed0a46bc59115c922cf535ddf211dca8846f2`
- `kayit/turetme/tr4/inc1/inc1_kesinlik.json` `5892ffdccec206c66fd120d39a9ffaa5fc2a0b10d6cc56dc484983f09f6fe480`
- `kayit/turetme/tr4/inc1/inc1_kesinlik_D.json` `b86e0780ab1bd3ae4a7c16490f0cb048c64f657f9810d75d16c80980a7c2a2dd`
- `kayit/turetme/tr4/inc1/inc1_yeniden.py` `c17a000ae5985d8467c3b74d73ab71c8d4b40dd85f85849881bfc5032d3122e2`
- `kayit/turetme/tr4/inc1/inc1_yeniden_olcum.json` `1ca4c83ce22c6076095e6fa79614933cba719e369c9515d1061e6475eda5d0db`
- `kayit/turetme/tr4/inc1/inc1_yeniden_ref.json` `61e73ff795e222e25e43d4a2d9e9f460073bff24329f7e1238d5520d0038fc63`

**Sayım yeniden koşusu (dondurmada).** `tr4_onkayit_sayim.py` (`5a6f9504…`, değişmedi) arşivlenmiş girdilerle karalama
dizinindeki bir kopyada yeniden koşuldu (2,2 sn): `tr4_pencereler.csv` `166e42ea…` ve `tr4_onkayit_sayim.json`
`39e91fce…` bit düzeyinde aynı. İncelemenin hiçbir düzeltmesi sayımı değiştirmez; istek tablosu farkı (771 → 631)
yalnız `tr4_asama0.py`'de uygulanır.

**Aşama 0 betiğinin ağsız sınaması** (`tr4_asama0_prova.json`): `kuru` iki koşuda aynı sha256'yı verdi; istek tablosu 26 / 468 / 84 / 15 / 30 / 8 ve 105 aday yeniden üretildi; ağ isteği 0. Provada `urlopen` yasaklandı, `_getir` ve `_akit` sahte yanıtlayıcıyla değiştirildi: bayraksız çağrı 0 istek; girdi sha256 uyuşmazlığında iş durdu; 2026 bitişli istek bağlantı kurulmadan reddedildi; üstveri çağrıları 26 / 2 / 0 (kesin olmayan kod ikinci çağrıda yeniden denendi, iki denemeden sonra bırakıldı), üstveri tamamlanmadan `kur` ve `say` koşmadı; süre sınırında `yokla` 172 istekten sonra temiz çıktı, `say` G0 vermedi, sonraki çağrı kalanları sürdürdü; üç ardışık `yokla` çağrısı 597 / 40 / 0 istek attı (hata satırları ikinci çağrıda yeniden denendi, üçüncüde denenmedi), çift kayıt 0; yarım satır `yokla`'yı ve `say`'ı düşürmedi, `say` iki kez aynı baytları yazdı; aşama H'de A ve C kararları, "ertelendi" → 2 gün kuralı → üç ölçümün medyanı → "veri yok (aktarım hızı)", POST reddinde gün gün GET ve süre sınırında sürdürme gösterildi.

## Dondurma notu

İnceleme hükmü DÜZELTMEYLE KABUL'dür; dört engelleyici, beş önemli ve dokuz küçük bulgunun hepsi işlendi, üçüncü tur
yoktur. Bilinen zayıflıklar dondurmada açıkça kabul edilir:
- **Aktarım hızı.** KOERI hızı 23–40 KiB/s ise (TR-7 §4, TR-5 §4.1) beklenen sonuç **"veri yok (aktarım hızı)"**dır;
  kapıyı koruyan hiçbir 0 € küme bütçeye sığmaz (§5.3).
- **Kapı.** Gerçek dolulukta kapının kırılma olasılığı küçük değildir (rastgele %30 kayıpta 0,26–0,43; tek tip kayıpta
  %29'da kırılır). Kırılırsa hüküm "veri yok"tur; σ̂_Δ yalnız bilgi satırı 0 olarak yazılır (§4.3).
- **Pozitif kontrol yok.** Zincirin Marmara'da gerçek bir hız değişimini gördüğü gösterilmez; "karşılandı" ancak gerçek
  olaylı bir PK'yi geçen yeni bir ön kayıtta dayanak olur (§4.6, Z10).
