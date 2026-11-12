# TR-4 ön kayıt: Marmara KO istasyonlarında olaysız yıllarda ortam gürültüsü dv/v tabanı

Durum: **TASLAK sürüm 1, bağımsız incelemeye hazır.** 12 Kasım 2026.
Hiçbir dalga formu indirilmedi, açılmadı ya da yoklanmadı. Bu taslak yalnız var olan üstveri, doluluk önbelleği ve
TR-5b kataloğuyla, ağsız hesaplandı. Kol: TR. Ata: `TR-5_TR-4_SAYIM.md` Ek 2 (sha256 `df912cb0…`). Zincir:
`TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 3, DONDURULDU (sha256 `506c0470…`). Maliyet bu belgeye kadar 0 €.

**Tek cümle.** TR-4, Marmara'daki KO istasyonlarında, depremden uzak (olaysız) pencerelerde, TR-5b'nin dondurulmuş
dv/v zinciriyle tek istasyonun "son yıl − önceki iki yıl" düzey farkını (Δ) ölçer ve bu farkın dağılımını yazar:
**σ̂_Δ** (1,4826 · MAD) ve **q95 = |Δ|'nın %95 niceliği**. q95, "olaysız bir yılda tek istasyonda dv/v'nin %95
olasılıkla kalacağı sınır", yani bu ölçüyle Marmara'da tek istasyonda algılanabilir en küçük yıl ölçekli hız
değişimidir. Bu bir ölçüm tabanıdır; olasılık, alarm ya da tahmin değildir.

**Kapı sayıları (üstveri ve Z doluluğu, aşama 0'dan önce).** Ana tanımla 21 yer (22 istasyon), 102 yer-penceresi;
yıllık T 2017–2024 için yer sayısı 15, 16, 15, 14, 14, 9, 10, 9. Kapı (≥ 10 yer, en az 3 yıl arayla ≥ 2 epok)
geçiyor; ama TR-5b'de aygıt kuralı ve yatay bileşenler sayıyı ≈ %9 + %9 küçülttü. Aynı küçülme burada 2017 ve 2020'yi
≈ 12'ye indirir; kapı yine geçer, pay dardır.

**Koşu düzeni.** Aşama 0 (771 hafif istek, ≈ 0,6 saat, bulut oturumu, 0 €) → aşama H (hız ölçümü, aşama 0'ın
içinde) → kademe seçimi (A ya da C, hızdan; §5.3) → indirme ve ölçü (0 € bulut oturumunda, her biri ≤ 2 saatlik,
kaldığı yerden süren işler). Kademe C, TR-7'nin tek akış hızında (341 KiB/s) ≈ 6,6 gün, 197 GB'tır. Hız 23–40 KiB/s
ise (TR-7 §4 ve TR-5 §4.1 ölçümleri) hiçbir zincire sadık kademe bir haftaya sığmaz; o durumda koşu
**"ertelendi (aktarım hızı)"** durumunda durur ve karar proje sahibinindir (§5.3). Sunucu kiralanmaz; kiralama
Erdem'in onayını ister ve hızı artırmaz, yalnız gözetimsiz koşturur.

---

## 0. Kimlik, öncelik ve TR-5b'den farklar

Çelişkide öncelik: bu belge > `TR-5b_sismik-hiz-oncul_ONKAYIT.md` sürüm 3 > `TR-5_TR-4_SAYIM.md`. Bu belgede
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
- σ̂_Δ burada **istasyon düzeyidir**. TR-5b'nin σ_Δ'sı kontrol düzeyidir (1–3 istasyonun ortalaması). İstasyon düzeyi,
  istasyonlar arası ilişki küçükse kontrol düzeyinden büyüktür; bu yüzden (c) için tutucu yöndedir. Kontrol düzeyi
  eşleniği bilgi satırı 6'dadır.

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
(M7,0) yüzünden 2020–2024'ün bütün T'lerini düşürür (bilgi satırı 1, N 46). Eleme nedenleri (istasyon düzeyi,
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
  (§6.1). Hacim A'nın %66'sı.

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
ve (ii-a) ile sınanır.

## 4. Hüküm satırı (tek, sıralı, otomatik)

**4.1 Ölçü.** n yer-penceresinin Δ'larından:
- **σ̂_Δ = 1,4826 · MAD(Δ)**, TR-5b §3.6'nın kestiricisi;
- **q95 = |Δ|'nın %95 niceliği** (iki yanlı, işaretsiz).

**4.2 Kesinlik.** İki yönlü önyükleme: yerler ve T yılları ayrı ayrı yerine koyarak çekilir, hücre ağırlığı iki
çokluğun çarpımı; B = 2000; tohum `sha256("tr4-hukum|20261202")`'nin ilk 8 onaltılık hanesi. Her iki ölçü için %90
yüzdelik aralığı [L, U] yazılır. Yer-pencereler hem yerde (aynı istasyon) hem zamanda (örtüşen pencereler, ortak
hidroloji) ilişkili olduğundan tek yönlü önyükleme kullanılmaz. Benzetimde bu aralığın kapsaması §6.2'de.

**4.3 Sıra.** Kod bu sırayı insan müdahalesi olmadan uygular. Bir adım hüküm verirse sonrakiler koşmaz; ama
o ana kadar hesaplanabilen her sayı ve bilgi satırı "kapı altı" etiketiyle yazılır.

0. **G0 (aşama 0).** Aşama 0'ın üç bileşen yoklaması ve aygıt kuralından sonra: dolu yer sayısı ≥ 10 olan T'ler
   içinde en az 3 yıl arayla iki T yoksa **"veri yok (aşama 0)"**.
   - **Ara durum, hüküm değil:** Kademe kuralı (§5.3) hiçbir kademeyi seçmezse **"ertelendi (aktarım hızı)"** yazılır
     ve koşu durur. Sonraki adım proje sahibinin kararıdır.
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
   - L(σ̂_Δ) > %0,20 → **"taban ölçüldü; TR-5b (c) karşılanmadı"**;
   - öteki → **"taban ölçüldü; TR-5b (c) belirsiz"**.

**4.4 Neden bu kapı.** TR-5b'nin kontrol kapısı istasyon sayısıydı; burada tek bir σ ve bir nicelik kestirilir.
≥ 10 yer, istasyon etkisinin tek bir yere bağlı kalmamasını; 3 yıl arayla iki epok, pencereleri örtüşmeyen en az
iki bağımsız zaman örneğini garanti eder. Daha sıkı bir kapı (≥ 3 örtüşmeyen epok) ana tanımda da geçiyor (2017 /
2020 / 2023: 15 / 14 / 10) ama aşama 0 küçülmesinden sonra 2023'te kırılır; bu yüzden seçilmedi. Kapı altında aday
elenmez.

**4.5 Kapalı hüküm listesi ve kalıplar.** Köşeli parantezler otomatik doldurulur; başka metin eklenmez.

| Hüküm adı (aynen) | Adım | Şart | Zorunlu ek metin |
|---|---|---|---|
| veri yok (aşama 0) | 0 | kapı tutmadı | "T başına dolu yer: [..]" |
| veri yok (gün doluluğu) | 1 | kapı tutmadı | "T başına dolu yer: [..]" |
| geçersiz (kod) | 2, 3 | §4.3 adım 2–3 | sapan dizi sayısı ya da medyan oran |
| veri yok (ε geçerliliği) | 4 | kapı tutmadı | "T başına geçerli yer: [..]" |
| taban ölçüldü; TR-5b (c) karşılandı | 5 | U(σ̂) < %0,20 | Kalıp T |
| taban ölçüldü; TR-5b (c) karşılanmadı | 5 | L(σ̂) > %0,20 | Kalıp T |
| taban ölçüldü; TR-5b (c) belirsiz | 5 | öteki | Kalıp T |

Ara durum (hüküm değil): "ertelendi (aktarım hızı)", ek metin "ölçülen hız [..] KiB/s (ölçüm [..] adet); kademe C
süresi [..] gün".

**Kalıp T:** "Marmara KO ağında [kademe], [n] yer-penceresinde ([yer] yer, T [ilk]–[son]), olaysız pencerelerde tek
istasyonun bir yıllık dv/v düzey değişiminin (0,5–2 Hz, TR-5b ölçüsü) %95'i [q95] %'den küçüktür (%90 aralık
[L–U]). σ̂_Δ = [..] % (%90 aralık [L–U]). Bu, tek istasyonda bu ölçüyle olaysız yıllardan ayrılabilecek en küçük
düzey değişimidir; bir olasılık ya da alarm eşiği değildir. Ölçü istasyon çevresindeki sığ ortamı örnekler."

**4.6 Anlam.**
- **Karşılandı:** TR-5b (c) şartı Marmara verisinde tutar. TR-5b "güç yok" ile kapanırsa bu, yeni bir ön kayıtla
  yeniden açmanın bir dayanağıdır; tek başına yeniden açma değildir (TR-5b'nin kontrolleri Marmara'da değil).
- **Karşılanmadı:** Bu ölçüyle Marmara'da yıl ölçekli dv/v izlemesi %0,2'nin altını çözemez; dv/v zaman daraltma
  yolu bu bant ve bu pencereyle Marmara'da kapalıdır.
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
| Yatay yoklama: her aday yer-penceresinin A, B, C dilimlerinin orta ayı × 2 yatay bileşen | 502 |
| Yoklanmamış Z adayları (GAZK T 2023, 2024; GEML T 2024), ay başına | 84 |
| Bilgi satırı 13 (SLVT, BOTS, NMR9; 2024-03…2025-05) Z | 45 |
| Aynısı, yatay | 90 |
| Aşama H hız denemesi (§5.2) | 24 |
| **Toplam** | **771 (≈ 0,64 saat; istek başına 3 sn)** |

Aşama 0 kodu, TR-5b'deki gibi, ağsız kuru kipte ve sahte yanıtlayıcıyla sınanır, incelenir ve ilk ağ isteğinden
önce dondurulur. Bu taslakta yazılmadı (zayıf nokta Z1).

**5.2 Aşama H (hız).** 24 istek: rastgele ama tohumlu seçilmiş 24 ana yer-penceresi gününden 1 saatlik üç bileşen
(TR-5b biçimi), tek akış, sıralı. v = Σ bayt / Σ süre (istek ek süreleri dahil). Bu istekler ölçüde kullanılmaz.
Gerekçe: KOERI hızı için elimizdeki dört ölçüm 15 kat dağınık: 23 KiB/s (TR-7 §4, 1 saatlik istekler,
2026-11-11), 40 KiB/s (TR-5 §4.1, 1 günlük), 341,3 KiB/s (TR-7 varlık, tek akış), 632,5 KiB/s (iki paralel akış).
Hacim tasarımı hız bilinmeden bağlanamaz.

**5.3 Kademe kuralı (veri görülmeden, yalnız v'den).**
1. t_A = 298,5 GB / v ≤ 7 gün (v ≥ 486 KiB/s) → **A**.
2. Değilse t_C = 196,7 GB / v ≤ 7 gün (v ≥ 320 KiB/s) → **C**.
3. Değilse aşama H, en az 2 gün arayla en çok 3 kez yinelenir; v ölçümlerin medyanıdır. 1–2 yeniden uygulanır.
4. Hâlâ sığmıyorsa: t_C ≤ 21 gün (v ≥ ≈ 106 KiB/s) → **C, uzatılmış** (aynı 0 € düzen, daha çok iş).
5. Değilse **"ertelendi (aktarım hızı)"**. Seçenekler (proje sahibinin kararı): iki paralel akış (KOERI'ye nezaket
   sorunu; TR-7'de ×1,85), KOERI ile iletişim, ya da TR-4'ün yalnız T 2021–2024 ile küçültülmüş bir sürüm 2'si
   (A 151 GB, C 100 GB). Bu belge onların hiçbirini önceden seçmez.

Kural tek akış ister. Sunucu KOERI hızını artırmaz.

**5.4 Hacim ve süre** (`tr4_onkayit_sayim.json` → `hacim`; bayt = saat × 3600 × 100 sn⁻¹ × 3 bileşen × 1,3 bayt;
1,3 bayt/örnek STEIM2 varsayımıdır, doğrulanamadı; 21 yer, ana T 2017–2024).

| Kademe | İstasyon-gün | GB | 23 KiB/s | 40 KiB/s | 341 KiB/s | 633 KiB/s (2 akış) | 1 hafta için gereken |
|---|---|---|---|---|---|---|---|
| **A** (her gün, 4 s) | 53 150 | 298,5 | 147 g | 84 g | 9,9 g | 5,4 g | 486 KiB/s |
| **C** (1–20. gün, 4 s) | 35 020 | 196,7 | 97 g | 56 g | 6,6 g | 3,6 g | 320 KiB/s |
| H (her gün, 3 s; reddedildi) | 53 150 | 223,9 | 110 g | 63 g | 7,5 g | 4,1 g | 365 KiB/s |
| E (16 gün, 2 s; reddedildi) | 28 012 | 78,7 | 39 g | 23 g | 2,7 g | 1,4 g | 128 KiB/s |

İndirilen günler istasyon-ay başına bir dataselect isteğinde toplanır (1752 istek). Bilgi satırı 13'ün ek hacmi
2,4 GB (A) ya da 1,8 GB (C).

**5.5 0 € bulut düzeni.** Her iş ≤ 2 saat, bir durum dosyası (jsonl: istasyon-ay, bayt, sha256, sonuç) tutar ve
kaldığı yerden sürer. Ham veri istasyon-ay işlendikten sonra silinir; saklanan günlük ÇİF'lerdir (3 çift × 2401
gecikme × float32 ≈ 29 KB/gün; C'de ≈ 1,0 GB, A'da ≈ 1,5 GB). Disk tepe değeri bir istasyon-aylık ham veridir
(≈ 0,11–0,17 GB). C, 341 KiB/s'de ≈ 80 iki saatlik iştir. İşlem süresi indirmenin yanında küçüktür (kestirilmedi;
zayıf nokta Z5). Başarısız istek oranı %5'i aşarsa ε'dan önce tek yeniden deneme turu (TR-5b §5).

**5.6 Kod donması.** 3. adımdan sonra kod değiştirilemez. Kod ve aşama 0 betiği ilk ağ isteğinden önce commit
edilir.

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
- **Hüküm asimetrik.** σ_Δ ≤ %0,10 ise "karşılandı" ≥ 0,97 olasılıkla gelir. σ_Δ ≈ %0,15'te yazı tura. σ_Δ %0,20'de
  "belirsiz" neredeyse kesin. **σ_Δ %0,30'da bile "karşılanmadı" ancak 0,00–0,40 olasılıkla** gelir: iki yönlü
  önyüklemenin σ aralığı geniştir (≈ 0,7 σ) ve tutucudur (kapsama 0,97–1,00, %90 değil). Yani TR-4 "(c) tutar"
  diyebilir, "(c) tutmaz" demesi zordur. Bu önceden kabul edilir; "belirsiz" hükmü σ̂'yı ve aralığını yine yazar.
- **q95 aralığı ρ büyükken ve az epokta kapsamasının altında** (0,75–0,85). q95 hükmü bağlamaz; Kalıp T'de aralığıyla
  yazılır, bu zayıflık Z11'dir.
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

1. Olaysızlık değişkeleri: ileri 2 yıl (N 86), M ≥ 7 için 500 km (N 46, kapı altı), pencere içinde M ≥ 5 ≤ 50 km
   olan yer-pencereler dışarıda (N 92), M ≥ 5,5 ≤ 100 km ±1 yıl (N 59, kapı altı). Her biri için σ̂, q95, aralık.
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
    2024-03…2025-05 doluluğu tutmazsa satır "veri yok" yazar.

## 9. Karşılaştırma ve literatür

Yayımlanmış bir Marmara dv/v serisi bulunamadı (OpenAlex aramaları). TR-4'ün sayısı bu yüzden bir ilk ölçümdür;
karşılaştırma başka bölgelerle ve mertebe düzeyindedir.

| Kaynak | Söylediği | Durum |
|---|---|---|
| Hillers 2015 (San Jacinto) | Mevsimsel tepeden tepeye ≈ %0,2, 0,5–2 Hz | Doğrulandı (depodaki önceki okuma) |
| Meier 2010 (Los Angeles) | ≈ %0,1 değişimler ölçülebilir | Doğrulandı |
| Sens-Schönfelder ve Wegler 2006 (Merapi) | Günlük çözünürlükte ≈ %0,1 doğruluk | Doğrulandı |
| Taira 2015 (Napa M6,0) | Kosismik ≈ %0,08 | Doğrulandı |
| Hillers 2014 | Gelgit duyarlılığı ≈ 0,5 MPa⁻¹ (2–8 Hz, sığ) | Doğrulandı; bant farklı |
| Clements ve Denolle 2023 (Kaliforniya, 700 istasyon) | Çok yıllı hidrolojik dv/v | Nitel doğrulandı; genlik **doğrulanamadı** |
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
  kayıt ister.
- **İstanbul için mutlak olasılık bu belgenin hiçbir yerinde yazılmaz ve hiçbir sonuçtan türetilmez.**

## 11. Yeniden açma şartı

"Veri yok" ya da "ertelendi" ile kapanırsa yeniden açma yeni bir sürümle ve şu yollardan biriyle olur:
- (a) KOERI aktarım hızının kademe C'yi ≤ 21 günde taşıması (yeni aşama H);
- (b) KO'nun kutudaki istasyon sayısını artıran yeni üstveri (≥ 2 yeni dolu yer);
- (c) T ≥ 2026 için kör olmayan veri: körlük kuralı kaldırıldığında, aynı tasarımla ileriye dönük uzatma.

"Taban ölçüldü" tek koşudur; parametre değiştirilerek yeniden koşulmaz. "Geçersiz (kod)" ile kapanırsa düzeltilmiş
kod yeni bir kod incelemesinden sonra aynı veride bir kez koşabilir; düzeltme kaydı hükümle birlikte yazılır.

## 12. Zayıf noktalar (incelemecinin bakması gerekenler)

- **Z1. Aşama 0 betiği yazılmadı.** Bu taslak yalnız istek sayısını kestirdi. Betik `tr5b_asama0.py`'den türetilecek
  ve kuru kipte sınanacak; G0 ancak onunla bağlanır.
- **Z2. Hız bilinmiyor.** Dört ölçüm 15 kat dağınık. 23–40 KiB/s doğruysa TR-4 bir haftada koşamaz ve "ertelendi"
  en olası sonuçtur. Kademe kuralı bunu açıkça kabul eder ama sonucu proje sahibine bırakır.
- **Z3. Kapı payı dar.** Ana tanımda 2017 ve 2020 14–15 yer; TR-5b'nin ≈ %18'lik küçülmesi ≈ 12'ye indirir. Sıkı
  doluluk tanımında kapı kırılır. 2022–2024 zaten < 10 yer.
- **Z4. İstasyon düzeyi σ ile TR-5b'nin kontrol düzeyi σ'sı aynı nesne değil.** (c) karşılaştırması istasyon
  düzeyinde tutucudur; ama istasyonlar arası ilişki yüksekse (ρ büyük, ortak hidroloji) iki düzey birbirine yaklaşır
  ve tutuculuk kaybolur. Bilgi satırı 6 bunu ölçer, hükmü değiştirmez.
- **Z5. İşlem süresi kestirilmedi.** İndirme baskın varsayıldı; 35 000–53 000 istasyon-günün tek çekirdekte işlenme
  süresi koşudan önce bir istasyon-ayla ölçülmeli (aşama 0'dan sonra, ilk indirilen ayda).
- **Z6. Kademe C zincirden sapar.** Gün örneklemesi TR-5b'den farklıdır; yapay dizide geçer, gerçek veride
  (ii-a) ile sınanır. A ile C arasındaki gerçek fark ancak A seçilirse görülür (bilgi satırı 9).
- **Z7. Olaysızlık eşikleri yargıdır.** 150/300/1000 km ve [T − 5 y, T + 1 y) SAYIM §3.2'den alındı; Samos 2020'yi
  ana tanımda içeride bırakır (M7,0, Marmara istasyonlarına > 300 km). 500 km değişkesi kapıyı kırar (bilgi satırı 1).
- **Z8. Yapay modelde ortam gürültüsü yok.** §6.2'nin σ_Δ'sı serbest parametredir; gerçek değeri ve dağılım biçimi
  (kalın kuyruk, istasyonlar arası ilişki) bilinmiyor. t4 ve ρ değişkeleri yalnız duyarlılıktır.
- **Z9. 1,3 bayt/örnek** STEIM2 sıkıştırması varsayımıdır; KO verisinde doğrulanmadı. Aşama H bunu da ölçer.
- **Z10. PK yok.** Zincirin Marmara'da gerçek bir hız değişimini gördüğü bu ön kayıtta gösterilmez.
- **Z11. Hüküm eşiği asimetrik ve q95 aralığı iyimser.** §6.2: "karşılanmadı" σ_Δ %0,30'da bile ≤ 0,40 olasılıklı;
  q95'in %90 aralığı ρ büyükken %75–85 kapsıyor. Alternatif (σ̂'nın nokta değeriyle hüküm, ya da %80 aralık)
  incelemecinin kararına açık bırakıldı; taslak tutucu olanı seçti.
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


Komutlar (her biri `cd /home/user/knotenlinie` ile; `OMP_NUM_THREADS=1`):
```
python3 -I -B kayit/turetme/tr4/tr4_onkayit_sayim.py <ust/ham> <ust/doluluk/onbellek.jsonl> <kat/tr5b_kat>
python3 -I -B kayit/turetme/tr4/tr4_guc.py olcum
python3 -I -B kayit/turetme/tr4/tr4_guc.py pk
python3 -I -B kayit/turetme/tr4/tr4_guc.py ref /mnt/project-files/turetme/tr5b-ham/tr5b_yapay_ccf.npz
python3 -I -B kayit/turetme/tr4/tr4_guc.py kesinlik
```
Süreler: sayım < 1 dk; olcum ≈ 19 dk; pk ≈ 2,5 dk; ref ≈ 1,5 dk; kesinlik ≈ 6 dk.
