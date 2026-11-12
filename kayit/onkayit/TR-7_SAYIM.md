# TR-7 tasarım ve 0 € güç kapısı sayımı: Marmara/KAF'ta uzak depremlerle tetiklenmiş tremor taraması

12 Kasım 2026. Durum: tasarım + üstveri sayımı. Tarama koşulmadı. Toplu dalga formu indirilmedi; yalnız iki kısa erişim
denemesi yapıldı (bölüm 4) ve içerikleri açılmadı. Tetikleyici listesi 2025-12-31'de biter (2026 kör). Betik:
`kayit/turetme/tr7/tr7_sayim.py`. Çıktılar: `tr7_tetikleyici.csv`, `tr7_cift.csv`, `tr7_istasyon.csv`,
`tr7_sayim_ozet.json` (aynı dizin). Ham üstveri yanıtları depo dışında (scratchpad `tr7_onb/`).
Talimat: Erdem, 12 Kasım ("tüm açık ihtimalleri götür, seçim yapmadan ilerlet, elemeyelim").

## Hüküm

**Ek 1 (12 Kasım, varlık yoklaması): K0 GEÇTİ (×1); S1/S2/S3'te 12/11/11 doğrulanmış tetikleyici, τ₍₈₎ = 3,8/4,0/4,1 kPa; bölgesel hariç 10/9/9 (τ₍₈₎ 2,7–2,9 kPa); τ×1/3 ile ZAYIF (6/6/5). Aşağıdaki SINIRDA hükmü bununla kapandı.**

**Kapı SINIRDA; aday elenmedi.** 2005–2025 arasındaki 111 M≥7,5 depremden 85'i sığdır (≤100 km). Kaba Ms bağıntısıyla
Marmara'da ≥2 kPa dinamik gerilme beklenen 17 olay var. Bunların ikisi Kahramanmaraş 2023'tür ve bölgesel olaydır.
Fay izine ≤50 km uzaklıkta 247 açık sismometre var (KO, 6G, TL, IJ ve geçici ağlar). Taranabilir (tetikleyici × segment)
çift sayısı (≥3 istasyon, ≥2 kPa) iki sınır arasında kaldı:
- KOERI kullanılabilirlik dizinine göre (alt sınır): 16 çift, 4 olay. Marmara segmentlerinin her birinde 2–3 tetikleyici.
- İstasyon epoklarına göre (üst sınır): 92 çift, 17 olay. Bölgesel olaylar dışarıda bırakılınca 78 çift, 15 olay.
  Marmara segmentlerinin her birinde 15–16 tetikleyici.

Aradaki farkın nedeni ölçüldü: KOERI'nin kullanılabilirlik ve WFCatalog servisleri Kahramanmaraş penceresi için "veri yok"
(204) döndü. Aynı pencereye yapılan dataselect isteği ise 421 KB veri getirdi. Yani dizinler eksik, gerçek sayı alt sınırın
üstünde. Önerilen kapı, her Marmara segmentinde (S1–S3) en az 8 doğrulanmış tetikleyici ister. Bu sayı, tetikleyici
başına 1/3 olasılıkla tetiklenen bir kaynağı %95 düzeyinde dışlamak için gerekir ((2/3)^8 ≈ 0,04). Alt sınır bu şartın
altında, üst sınır üstünde. Kapı, ~760 küçük varlık yoklamasıyla (her biri 10 sn; toplam birkaç MB) kesinleşir. Bu yoklama
benim yetkimin dışında kalan bir dalga formu isteğidir, onay gerekir.

Kapı geçerse taramanın verebileceği en güçlü olumsuz cümle şudur: "S2/S3'te, kaba τ ≈ 4–5 kPa'nın üstündeki 8 tetikleyicide
tremor görülmedi. Dolayısıyla Parkfield türü bir kaynak (eşik 2–3 kPa) istasyon gürültü tabanının üstünde yok." Tayvan türü
bir kaynak (eşik 7–8 kPa) bu veriyle dışlanamaz: o gerilmeye ulaşan tetikleyici segment başına en çok 6–7 tane.
İstanbul'a verdiği şey bir durum göstergesinin var/yok bilgisidir. Olasılık terimi vermez.

## 1. Soru ve neyi ölçmediği

Soru: Büyük uzak depremlerin yüzey dalgaları geçerken KAF'ın Marmara ve batı kesimlerinde, 2–8 Hz'te, yüzey dalgasıyla eş
zamanlı ve istasyonlar arasında tutarlı bir tremor zarfı oluşuyor mu? Oluşmuyorsa hangi dinamik gerilme ve hangi genlik
eşiğine kadar "yok" denebilir? Yanıt bir varlık sınamasıdır. Ölçmedikleri şunlar:
- tremor hızı ile deprem olasılığı arasındaki ilişki (dünyada tek olay var, Parkfield 2004),
- ortam (tetiklenmemiş) tremoru,
- sığ sünme. Sığ sünme TR-10/AV-3'ün konusu; tremor kilitli derinliğin altında beklenir.

Mutlak İstanbul deprem olasılığı yazılmaz.

## 2. Kodlanabilir tasarım (betikteki sabitler)

**2.1 Tetikleyiciler.** ComCat fdsnws/event sorgusu: M≥7,5, 2005-01-01T00:00:00 – 2025-12-31T23:59:59, `type=earthquake`.
Derinliği 100 km'yi aşan olaylar çıkarılır (yüzey dalgası zayıftır; 26 olay). Her olay için kaba yüzey dalgası tepe yer
hızı Prag bağıntısından tersine hesaplanır: log10(A/T) = M − 1,66·log10(Δ°) − 3,3 (A μm, T = 20 s), PGV = 2π·A/T.
Bağıntı ders kitabındandır, OpenAlex özetinden doğrulanmadı. 20°'den yakın olaylar "bölgesel" işaretlenir (bağıntı
geçerlilik dışında; yalnız Kahramanmaraş 2023'ün iki olayı). M>8'de Ms doygunluğu yok sayılır, bu da büyük olaylarda
gerilmeyi fazla tahmin ettirir. Dinamik gerilme τ = G·PGV/c alınır (G = 30 GPa, c = 3,5 km/s; 1 cm/s ≈ 86 kPa). τ her
segmentin orta noktasına göre hesaplanır. Belirsizlik ×3 kabul edilir; sayımlar ×1/3, ×1 ve ×3 için verilir. Koşu
sırasında τ, istasyonların ölçülmüş düşük frekanslı PGV'siyle değiştirilir; kaba τ yalnız kapı içindir.

**2.2 Eşiğin gerekçesi (OpenAlex özetlerinden doğrulanmış sayılar).**

| Kaynak | Bölge | Sayı | Bildirilen eşik |
|---|---|---|---|
| Peng vd. 2009, [10.1029/2008jb006049](https://doi.org/10.1029/2008jb006049) | SAF Parkfield–Cholame | 31 Mw≥7,5 (2001+), 10'u tetikledi | ~2–3 kPa |
| Chao vd. 2011, [10.1111/j.1365-246x.2011.05261.x](https://doi.org/10.1111/j.1365-246x.2011.05261.x) | Tayvan Orta Sıradağlar | 45 Mw≥7,5 (1998–2009), 9'u tetikledi | ~0,1 cm/s ≈ 7–8 kPa (kısmen gürültüye bağlı) |
| Chao vd. 2012, [10.1785/0120110151](https://doi.org/10.1785/0120110151) | Calaveras, San Jacinto | 42 Mw≥7,5 (2001–2010), yalnız Denali 2002 | — (Parkfield'da 12 olay) |
| Hill vd. 2013, [10.1785/0120120114](https://doi.org/10.1785/0120120114) | Parkfield, Tohoku 2011 (~8200 km) | PKD istasyonunda kayıtlı | 0,7–10 kPa |
| Saini vd. 2023, [10.1038/s41598-023-49068-3](https://doi.org/10.1038/s41598-023-49068-3) | Arunachal Himalaya | 34 olay, 6'sı tetikledi (deprem + tremor) | 1 kPa'ya kadar |
| Pfohl vd. 2015, [10.1785/0120140312](https://doi.org/10.1785/0120140312) | Merkezî KAF, 2 yıllık geçici ağ | Tetiklenmiş tremor yok | Sayısal eşik özette yok |
| Inbal 2024, [10.1038/s43247-024-01266-1](https://doi.org/10.1038/s43247-024-01266-1); Yao vd. 2024, [10.1029/2024gl110786](https://doi.org/10.1029/2024gl110786) | Ölü Deniz Transformu; Kafkasya | Kahramanmaraş 2023 tetikledi | Sayı özette yok |

Ana eşik **2 kPa**: bildirilen en hassas doğrultu atımlı eşiğin (Parkfield) alt ucu. "Tremor yok" demek, bilinen en
hassas kaynağı tetikleyecek gerilme uygulandıysa anlamlıdır. Duyarlılık için 1, 3, 5 ve 7,5 kPa da hesaplanır. Tetikleme
oranı 10/31 ≈ 1/3, Peng 2009 özetinden ve genlikten bağımsız olarak alındı. Eşik üstü olaylarda oran büyük olasılıkla
daha yüksektir; bu yüzden 1/3 temkinli bir varsayımdır. Eşik üstü olaylardaki oran özetten doğrulanamadı.

**2.3 Segmentler (elle sayısallaştırılmış kaba iz, ±5–10 km).** S1 Ganos–Saros, S2 Orta Marmara–Adalar, S3 Çınarcık–İzmit,
S4 Sapanca–Düzce, S5 Bolu–Gerede–İsmetpaşa, S6 Çerkeş–Tosya, S7 güney kol (Geyve–İznik–Gemlik–Biga). Köşe noktaları
betikte. İstanbul'a ait olanlar S2 ve S3.

**2.4 İstasyonlar.** Kutu 26–34° D, 39,5–41,5° K. Kaynaklar: KOERI, EIDA federatör (ORFEUS), EarthScope fdsnws/station,
kanal düzeyi. Seçim şartları:
- Z bileşeni, bant kodu H/B/E/S, alet kodu H/P (sismometre ya da geofon), örnekleme ≥20 Hz;
- ZQ (2023 İstanbul DAS ayı, gerinim hızı) ve SY (sentetik) ağları dışarıda;
- (ağ, istasyon) tekilleştirilir.

İstasyon, bir segmentin izine ≤50 km uzaklıktaysa o segmente sayılır. GONAF kuyuları EarthScope'ta yalnız gerinimölçer
olarak görünüyor (BS, 20 Hz). Kuyu sismometreleri açık FDSN'de bulunamadı, sayıma girmedi.

**2.5 Pencere.** Segment s ve olay e için yüzey dalgası penceresi W = [T0 + Δ/5,0 km/s, T0 + Δ/2,8 km/s + 600 s].
Bu pencere Love dalgasının başından Rayleigh kodasına kadar uzanır. Başvuru (gürültü) penceresi P varışından önceki 1 saattir.

**2.6 Veri varlığı.** KO, TL, IJ ve 6G için KOERI fdsnws/availability, öteki EIDA ağları için federatör availability
kullanılır. Bir istasyon, W'nin en az %90'ı kayıtta ise sayılır. EarthScope availability servisi kaldırılmış (404 "retired").
Bu yüzden YH, YL ve IU için yalnız epok kullanılabildi. Değişke olarak tam 00:00:00'da biten aralıklar ertesi güne
uzatıldı, çünkü dizinin gün sınırında kesildiği görüldü.

**2.7 İşleme ve algılama ölçütü (koşu için, önceden sabit).**
1. Her bileşen: ortalama ve eğilim çıkarılır; 2–8 Hz 4 kutuplu sıfır fazlı Butterworth süzgeç uygulanır; Hilbert zarfı
   alınır; 5 sn kayan ortalama ile 1 Hz'e indirilir; log10 alınır. Üç bileşenin karesel ortalaması kullanılır (yatay
   bileşen yoksa Z).
2. İstasyon düzeyi aşım: W içinde en az 30 sn kesintisiz log-zarf > m + 4·σ. Burada m başvuru penceresinin medyanı,
   σ = 1,4826·MAD.
3. Tutarlılık: aynı segmentin ≥3 istasyonunda aşımlar ±20 sn içinde örtüşür. Zarf çapraz ilişkisi ≥0,5 (gecikme
   ≤10 sn) en az 3 istasyon çiftinde sağlanır.
4. Yüzey dalgasıyla eş zamanlılık: istasyon medyan zarfı ile 0,01–0,1 Hz süzülmüş yatay yer hızının pozitif kısmı
   arasındaki ilişki ≥0,3 olur, ya da aşım W içinde başlar ve W içinde biter.
5. Yerel deprem dışlaması: aşım aralığının ±60 sn içinde KOERI ya da ComCat kataloğunda segmentin 150 km'sinde bir olay
   varsa aşım sayılmaz. Zarfı tek darbeli olan (yükselme <2 sn ve 20 sn'de yarıya inen) aşım da sayılmaz.
6. Yüksek genlikte süzgeç sızıntısı dışlaması (özellikle Kahramanmaraş): 0,5–1 Hz zarfı 2–8 Hz zarfından hızlı yükselirse
   aşım "sızıntı" işaretlenir ve sayılmaz.

(Tetikleyici, segment) çifti 1–5 sağlanırsa "algılama" sayılır.

**2.8 Negatif kontrol.** Her tetikleyici için aynı istasyonlarda, T0 ± 30 gün içinden rastgele (tohum sabit) seçilmiş
10 pencere kullanılır. Pencere uzunluğu W ile, başvuru penceresi aynı biçimde 1 saattir. Önceki 3 saatte küresel bir
M≥6,5 ya da 200 km içinde bir M≥3 bulunan pencereler dışarıda kalır. Aynı kod koşar; yanlış algılama oranı
FAR = algılama / pencere. Şart: FAR ≤ 0,05. Şart sağlanmazsa hüküm "ölçü güvenilmez" olur ve eşikler değiştirilmez.

**2.9 Pozitif kontrol.** Parkfield'da Tohoku 2011, aynı kod ve aynı sabitlerle. BK.PKD ile NCEDC'deki BK/BP/NC
istasyonları kullanılır; ≥3 istasyon gerekir. Hill vd. 2013 bu olayın PKD'de tetiklediği tremoru bildiriyor (özetten
doğrulandı). Kod bu olayı algılamazsa koşu durur ve Marmara verisine bakılmaz. NCEDC station servisi erişilebilir (200);
dataselect denenmedi. İkinci pozitif kontrol (isteğe bağlı): Kahramanmaraş 2023 ile Ölü Deniz Transformu (Inbal 2024).
Bu bölgenin istasyon erişimi denetlenmedi. Japonya (Chao ve Obara 2015) Hi-net kaydı gerektirdiği için 0 € açık sayılmadı.

**2.10 Hüküm satırı (biçim).** Her segment için tek satır:
`S_k: ALGILAMA VAR (a/n) | YOK (0/n); n = taranan tetikleyici; τ_(n) = n'inci en büyük ölçülmüş τ (kPa); gürültü tabanı =
negatif kontrol 2–8 Hz zarfının %95'i (nm/s); FAR = …; pozitif kontrol = geçti/kaldı`.
- "YOK" yalnız n ≥ 8 iken şu cümleye çevrilir: "τ_(8) kPa üstünde, tetikleyici başına ≥1/3 olasılıkla tetiklenen ve
  gürültü tabanını aşan bir kaynak %95 düzeyinde yok".
- n = 5–7 iken "zayıf YOK" denir: yalnız tetikleyici başına ≥1/2 olasılıkla tetiklenen kaynak dışlanır ((1/2)^5 ≈ 0,03).
- "VAR" denebilmesi için iki ayrı tetikleyicide algılama ve FAR ≤ 0,05 gerekir. Tek algılama "aday" kalır.

**2.11 Güç kapısı.** Bkz. bölüm 5.

## 3. Sayım (12 Kasım 2026, `tr7_sayim.py`)

**3.1 Tetikleyiciler.** ComCat: 111 olay. 26'sı derin, 85'i sığ. İstanbul başvuru noktasında (40,85° K, 29,0° D) kaba τ:

| eşik (kPa) | ≥1 | ≥2 | ≥3 | ≥5 | ≥7,5 |
|---|---|---|---|---|---|
| sığ olay sayısı | 33 | 17 | 12 | 7 | 6 |
| bölgesel hariç | 31 | 15 | 10 | 5 | 4 |

En büyükleri (kaba τ, İstanbul): Kahramanmaraş Mw 7,8 (64 kPa; bölgesel), Elbistan Mw 7,5 (34; bölgesel), Tohoku 2011
(23), Kamçatka 2025-07-29 (12), Sumatra 2012 Mw 8,6 (9,5), Nias 2005 (8,8), Maule 2010 (6,0). Tohoku ve Kamçatka
değerleri Ms doygunluğu yüzünden büyük olasılıkla fazladır.

**3.2 İstasyonlar.** Kutuda şartları sağlayan 276 istasyon var, 247'si fay izine ≤50 km. Ağlara göre: YH 73
(DANA 2012–13), KO 52, 6G 34 (MARsite 2013–15), YJ 33 (1999–2000; pencere dışında), TL 16, YL 9 (2005–08; Pfohl'un
verisi), IJ 8, 1O 6, YI 6, XW 4, XY 4, HT 1, TU 1. KOERI arşivinde KO geniş bant verisi büyük ölçüde 2010–2011'de başlıyor
(ISK HHZ: 2011-10-30). 2005–2010 tetikleyicileri pratikte yalnız geçici ağlarla taranabilir.

**3.3 Taranabilir çiftler (≥3 istasyon, ≤50 km, ≥2 kPa, ×1).** Eşik üstü çift 120, olay 18.

| Segment | eşik üstü çift | doğrulanmış (alt) | epok (üst) | üst, bölgesel hariç | τ_(8) üst (kPa) | τ_(5) üst (kPa) | ≤50 km istasyon |
|---|---|---|---|---|---|---|---|
| S1 Ganos–Saros | 18 | 2 | 16 | 14 | 4,4 | 9,2 | 38 |
| S2 Orta Marmara–Adalar | 17 | 3 | 15 | 13 | 4,7 | 9,4 | 61 |
| S3 Çınarcık–İzmit | 17 | 3 | 15 | 13 | 4,8 | 9,6 | 80 |
| S4 Sapanca–Düzce | 17 | 2 | 12 | 10 | 4,3 | 9,8 | 122 |
| S5 Bolu–Gerede–İsmetpaşa | 17 | 1 | 10 | 8 | 3,2 | 4,9 | 54 |
| S6 Çerkeş–Tosya | 17 | 1 | 9 | 7 | 2,7 | 3,9 | 20 |
| S7 Güney kol | 17 | 4 | 15 | 13 | 4,7 | 9,4 | 148 |
| **Toplam** | 120 | **16 çift / 4 olay** | **92 / 17** | 78 / 15 | | | 247 |

Gece uzatması değişkesiyle alt sınır 17 çift / 5 olay olur (Illapel 2015 eklenir). Alt sınırdaki dört olay: İran
2013-04-16 M 7,7; Pakistan 2013-09-24 M 7,7; Nepal 2015-04-25 M 7,8; Kamçatka 2025-07-29 M 8,8. Kamçatka tek başına
7 segmentin hepsinde taranabilir. S5 ve S6'nın üst sınırındaki 2005–2008 olaylarını YL ağı taşıyor, yani Pfohl'un zaten
incelediği veri.

**3.4 Duyarlılık (kaba τ'nun ×1/3, ×1, ×3 çarpanı).** Tablo (eşik üstü çift / doğrulanmış taranabilir çift / olay):

| eşik | ×1/3 | ×1 | ×3 |
|---|---|---|---|
| 1 kPa | 89 / 13 / 3 | 232 / 35 / 8 | 542 / 73 / 17 |
| 2 kPa | 45 / 7 / 1 | 120 / 16 / 4 | 339 / 49 / 12 |
| 3 kPa | 38 / 7 / 1 | 89 / 13 / 3 | 232 / 35 / 8 |
| 5 kPa | 21 / 0 / 0 | 53 / 8 / 2 | 142 / 21 / 6 |
| 7,5 kPa | 21 / 0 / 0 | 42 / 7 / 1 | 108 / 16 / 4 |

Üst sınırda (epok) kaba τ ≥6 kPa (×1/3 altında da 2 kPa'yı geçen) çift sayısı: S1 6, S2 6, S3 5, S4 5, S5 3, S6 3, S7 6.

**3.5 Servis durumu.** Bütün servisler yanıt verdi, reddedilen kaynak yok:
- ComCat event 200;
- KOERI station 200 (120 KB), availability 200/204, WFCatalog 204;
- federatör station 200 (78 KB), availability 200/204, bir kez IncompleteRead (yeniden denemede geldi);
- EarthScope station 200 (213 KB); EarthScope availability 404 ("This service has been retired"; atlatılmadı, yalnız
  epokla sayıldı);
- GEOFON station 200;
- NCEDC station 200.

## 4. Veri erişimi denemesi (yalnız HTTP durumu ve bayt; içerik açılmadı)

| İstek | HTTP | Bayt | Not |
|---|---|---|---|
| KOERI dataselect KO.ISK.HHZ 2015-09-16 23:50–00:50 (Illapel M 8,3, 1 saat) | 200 | 554 496 | 23,9 sn, ≈23 KB/s |
| KOERI dataselect KO.ISK.HHZ 2023-02-06 01:20–01:50 (Kahramanmaraş, 30 dk) | 200 | 421 376 | aynı pencere için availability 204, WFCatalog 204 |

Sonuç: KOERI dalga formu açık ve anahtarsız erişiliyor. Availability ve WFCatalog dizinleri eksik: Illapel'de gece
yarısından sonrasını, Kahramanmaraş'ta bütün pencereyi göstermiyor. Bu yüzden bölüm 3'teki "doğrulanmış" sayı bir alt
sınırdır.

## 5. İş yükü, maliyet ve kapı

**Hacim.** 100 Hz, 3 bileşen, ≈0,55 MB/saat/kanal (ölçülen). Bir istasyon-tetikleyici için W + 1 saat başvuru ≈ 1,6 saat,
yani ≈2,6 MB. 10 negatif kontrol penceresiyle bu ≈29 MB olur.
- Üst sınır: ≈760 istasyon-tetikleyici → ≈22 GB.
- Alt sınır: ≈160 → ≈4,6 GB.
- Pozitif kontrol (Parkfield): <0,5 GB.

**Süre.** Ölçülen tek akış hızı ≈23 KB/s. 22 GB tek akışla ≈11 gün, 8 paralel akışla ≈1,5 gün sürer (KOERI paralel
isteğe izin verirse; denenmedi). Darboğaz işlem değil, aktarım.

**Bulut oturumu.** 4 çekirdek ve 15 GB bellek yeterli: süzgeç ve zarf işlemi hafif, istasyon-gün başına saniyeler sürer.
Disk: 17 GB boş. Ham veri indir–zarfla–sil akışıyla tutulmazsa 22 GB sığmaz. Zarflar (1 Hz) birkaç yüz MB tutar.

**Yazılım.** obspy kurulu değil; scipy de yok, numpy 2.5.3 var. `pip download obspy` ile obspy-1.5.1 tekerleği (cp313,
manylinux) indirilebildi, yani PyPI erişimi açık. Kurulum koşu adımına bırakıldı. scipy ve öteki bağımlılıklar da aynı
yoldan gelir. Sınama için indirilen tekerlek silindi. Maliyet 0 €.

**Kapı kuralı (öneri).**
- **K0, veri varlığı:** S1, S2 ve S3'ün her birinde, dalga formu varlığı doğrulanmış ≥3 istasyonlu ve kaba τ ≥ 2 kPa
  tetikleyici sayısı n ≥ 8 olmalı. n = 5–7 ise "zayıf hüküm" kipine geçilir; n < 5 ise o segment taranmaz.
  S4–S7 bilgi satırıdır.
- **K1, pozitif kontrol:** Koşunun ilk adımı; aynı kod Tohoku–Parkfield'ı algılamalı.
- **K2, negatif kontrol:** FAR ≤ 0,05.

K1 ve K2 koşu içindedir, sayımla değerlendirilemez.

**Bugünkü durum: SINIRDA.**
- K0 alt sınırla (2–3 / 3 / 3) GEÇMEZ.
- K0 üst sınırla (16 / 15 / 15; bölgesel hariç 14 / 13 / 13) GEÇER.
- Kaba τ'yu ×1/3 alıp yalnız τ ≥ 6 kPa olanları sayınca (5–6) "zayıf hüküm" bandına düşer.

**Kesinleştirme yolu (0 €, onay gerekir):** Her (istasyon × tetikleyici) için W'nin ortasından 10 sn'lik dataselect
varlık yoklaması. ≈760 istek, her biri birkaç KB, toplam ≈5–10 MB. Yalnız HTTP durumu ve bayt kaydedilir. Bu istekler
dalga formu isteği olduğu ve bu görevin "en çok iki deneme" sınırını aştığı için yapılmadı.

## 6. İstanbul'a ne verir

Olasılık terimi vermez. Verdiği şey, kilitli derinliğin altında (S2/S3, İstanbul açığı) dinamik gerilmeye duyarlı,
sıvıca zengin bir kayma bölgesi olup olmadığına dair bir **var/yok bilgisidir**. Durum göstergesinin kendisi budur.
- "Var" çıkarsa: Marmara'da daha önce bildirilmemiş bir gözlem türü açılır (tremor kataloğu, göç, ortam tremoru araması).
  Zaman eksenine bağı yine dolaylıdır, çünkü tremor ile M6+ arasındaki bağ tek olaya dayanıyor (Parkfield 2004). Bu bağ
  kanıtlanmamıştır. FA-1'in yeniden açılma şartı için ön koşul olur, kendisi şart değildir.
- "Yok" çıkarsa (n ≥ 8): "İstanbul açığında Parkfield türü tetiklenebilir tremor kaynağı, ölçülen gürültü tabanının
  üstünde yok" cümlesi kurulur. Bu cümle Pfohl 2015'in merkezî KAF hükmünü Marmara'ya taşır. "Tremor ölçerle İstanbul
  izleme" yolunu bugünkü yüzey istasyonlarıyla kapatır, kuyu sensörleri için açık bırakır.
- Tayvan türü (7–8 kPa) daha yüksek eşikli kaynaklar bu veriyle dışlanamaz. Tetikleyici sayısı yetmez.

## 7. En büyük üç risk

1. **Veri varlığı ve aktarım.** Gerçek taranabilir sayı 16 ile 92 çift arasında; KOERI dizinleri eksik. 2011 öncesi
   KO verisi EIDA'da çok az. Ölçülen aktarım hızı düşük (≈23 KB/s). Geçici ağların (YH, YL, 6G, 1O) açık olup olmadığı
   ağ ağ denetlenmedi; 1O 2022–2028 epoklu, kısıtlı olabilir.
2. **Fiziksel önsel düşük ve gürültü yüksek.** Pfohl 2015 merkezî KAF'ta özel ağla olumsuz sonuç buldu. İstanbul'daki
   yüzey istasyonlarının 2–8 Hz kültürel gürültüsü yüksektir, bu da gürültü tabanını ve "yok" cümlesinin genlik eşiğini
   büyütür. GONAF kuyu sismometreleri açık FDSN'de yok. En olası sonuç "yok", ve bu yok yüksek bir gürültü tabanında
   söylenmiş olur.
3. **Kaba τ ve yanlış algılama.** Ms bağıntısı, M>8 doygunluğu, azimut ve Love/Rayleigh oranı yüzünden τ ×3 belirsiz.
   τ_(8) üst sınırda 4,4–4,8 kPa; ×1/3 ile 1,5–1,6 kPa olur ve Parkfield eşiğinin altına düşer. Kahramanmaraş gibi
   yakın ve büyük olaylarda süzgeç sızıntısı ve artçılar, Marmara'da yerel mikrodeprem ve kültürel gürültü yanlış pozitif
   üretebilir. Negatif kontrol bunu ölçer ama düzeltmez.

## 8. Defterle ve literatürle örtüşme

- **TR-4** (Marmara dv/v): aynı KO dalga formu hattı ve aynı aktarım darboğazı. İndirme altyapısı ortak kurulabilir.
  Pencereler farklı (TR-4 sürekli gün, TR-7 olay penceresi).
- **TR-6 / GH-1** (sismisiteden gerilme ölçer): ikisi de "gerilme durumu göstergesi" ama farklı fizik. Örtüşme yok.
- **S-7 / EL-1** (tekrarlayan depremler): farklı sinyal ve farklı derinlik. EL-1'in elenme gerekçesi (Uchida, Kalafat,
  Pınar 2019 yöntemi zaten Marmara'ya taşımış) TR-7 için geçerli değil: Marmara'da tremor yayını bulunamadı.
- **TR-10 / AV-3** (sünme): sığ, jeodezik; örtüşme yok.
- **Pfohl 2015:** S5 ve S6'daki 2005–2008 tetikleyicileri onların YL verisi; yeniden inceleme bağımsız sayılmaz.
- **İşaretli:** 2012 tarihli "Searching for Tectonic Tremor on the North Anatolian Fault" (DOI'siz, büyük olasılıkla
  AGU özeti) okunamadı. Marmara'yı kapsayıp kapsamadığı bilinmiyor.
- **Özetten doğrulanamayan sayılar:** Peng 2009'daki eşik üstü olaylarda tetikleme oranı; Parkfield'ı 2005 sonrasında
  tetikleyen olayların listesi; Pfohl 2015'in istasyon sayısı ve gürültü düzeyi; Kahramanmaraş'ın Ölü Deniz ve Kafkasya'da
  ürettiği dinamik gerilme değerleri.

Aday kendi başına elenmedi. Kapının kesinleşmesi, bölüm 5'teki varlık yoklaması için Erdem'in onayına bağlı.

## Ek 1: veri varlığı yoklaması (12 Kasım)

Betik `kayit/turetme/tr7/tr7_varlik.py`; çıktılar `tr7_varlik.csv`, `tr7_varlik_ozet.json`. Yanıt özeti (kod, bayt)
depo dışındaki önbellekte (`tr7_onb/varlik_onb.jsonl`); betik yeniden koşunca ağa çıkmaz. İçerik çözülmedi, diske
yazılmadı. Tetikleyiciler ≤ 2025-12-31; Marmara GNSS verisine dokunulmadı.

**Yöntem.** Epok üst sınırındaki her (istasyon × tetikleyici) adayı için (çiftte epokla ≥3 istasyon, τ ≥ 2 kPa, ×1),
istasyonun kendi uzaklığına göre W'nin ortasından 10 sn, tek Z kanalı (HHZ > BHZ > EHZ > SHZ). Servis: KO/TL/IJ/6G →
KOERI, EIDA ağları → federatör, YH/YL → EarthScope. 200 ve >0 bayt = var; 404 = yok. Tek akış, istekler arası ≥0,5 sn,
genel User-Agent.

**İstek.** 935 istek (tahmin ~760'tı; aday kümesi bölüm 3 kurallarıyla yeniden üretildi). 481 × 200, 454 × 404.
Toplam 1,75 MB. 429/503, 401/403 ve belirsiz yanıt yok. Bir istek bağlantı sıfırlandı, yeniden denemede geldi.

| Ağ (servis) | var | yok |
|---|---|---|
| KO (KOERI) | 311 | 104 |
| 6G (KOERI) | 37 | 210 |
| IJ (KOERI) | 8 | 6 |
| TL (KOERI) | 0 | 28 |
| YH (EarthScope) | 71 | 75 |
| YL (EarthScope) | 30 | 2 |
| HT / XW / XY (federatör) | 12 / 6 / 6 | 4 / 2 / 1 |
| 1O / TU (federatör) | 0 / 0 | 16 / 6 |

- 6G'nin üstveri epoku 2013'ten beri açık, ama veri 2015 sonrasında yok. TL hiç gelmedi: joker konum ve kanalla yapılan
  bir tanı isteği de 404 döndü. 1O ve TU federatörden 404 döndü. Bunların "arşivde yok" mu, "kısıtlı" mı olduğu
  ayrılamadı, çünkü servis 401/403 vermedi.
- KO'nun 2006–2008 pencerelerinin hepsi 404 (46 istek). KO verisi 2010'dan itibaren geliyor. Bu, 2011 öncesi KO
  verisinin seyrek olduğu bilgisiyle tutarlı.

**Segment sayımı** (≥3 istasyonda veri var ve kaba τ ≥ 2 kPa olan tetikleyici sayısı):

| Segment | eşik üstü | ×1 | bölgesel hariç | τ₍₈₎ ×1 (kPa) | τ₍₈₎ bölg. hariç | ×1/3 | ×3 (alt sınır) |
|---|---|---|---|---|---|---|---|
| S1 Ganos–Saros | 18 | **12** | 10 | 3,8 | 2,7 | 6 | 12 |
| S2 Orta Marmara–Adalar | 17 | **11** | 9 | 4,0 | 2,8 | 6 | 12 |
| S3 Çınarcık–İzmit | 17 | **11** | 9 | 4,1 | 2,9 | 5 | 11 |
| S4 Sapanca–Düzce | 17 | 11 | 9 | 4,3 | 3,0 | 5 | 11 |
| S5 Bolu–Gerede | 17 | 8 | 6 | 2,4 | — | 3 | 8 |
| S6 Çerkeş–Tosya | 17 | 5 | 5 | — | — | 1 | 5 |
| S7 Güney kol | 17 | 13 | 11 | 4,7 | 3,7 | 6 | 14 |

×3 sütunu alt sınırdır. Yalnız ×1 adayları yoklandı; ×3'te ortaya çıkan ek çiftler (S1–S3'te ~29'ar) yoklanmadı.
Doğrulanmış tetikleyiciler (S2): Kahramanmaraş ×2 (bölgesel), Tohoku 2011, Kamçatka 2025, Wharton Basin 2012 ana şok ve
artçısı, Maule 2010, İran 2013, Pakistan 2013, Nepal 2015, Chignik 2021. S1'de ayrıca Illapel 2015 var.

**K0 hükmü: GEÇTİ** (×1; S1/S2/S3 = 12/11/11; bölgesel hariç 10/9/9). Doğrulanmış τ₍₈₎ değeri 3,8/4,0/4,1 kPa,
bölgesel hariç 2,7/2,8/2,9 kPa. Önceki üst sınır τ₍₈₎ 4,4–4,8 kPa'ydı. Kaba τ ×1/3 alınırsa hüküm **ZAYIF** olur
(6/6/5). Uyarılar:
- Wharton 2012 ana şoku ile artçısı arasında 2 saat var. Bağımsız sayılmazlarsa bölgesel hariç sayı 9/8/8 olur; yine
  ≥8, ama S2 ve S3 sınırda kalır.
- "Var" bilgisi W içindeki tek bir 10 sn'lik örneğe dayanıyor. W'nin %90 örtüsü doğrulanamadı; tam koşuda boşluklu
  istasyonlar düşebilir.

**Doğrulanmış tam tarama hacmi.** 71 çift, 17 olay, 475 istasyon-tetikleyici (353'ü KOERI). Varsayım: 3 bileşen,
0,55 MB/saat/kanal, W + 1 saat başvuru, 10 negatif kontrol penceresi. Tetikleyici pencereleri ≈1,1 GB, negatif
kontrol ≈11,2 GB, toplam **≈12 GB**. Bu, 17 GB boş diske indir–sil yapmadan da sığar.

**Hız (KOERI, 2 deneme, her biri ≤1 MB).**
- Tek akış, KO.ISK.HHZ 1 saat: 434 KB 1,27 sn'de geldi, ≈341 KB/s.
- 2 paralel akış (ISK + BGKT, 1'er saat): toplam ≈633 KB/s, yani ×1,85. Hız katlanmaya yakın arttı.

Bugünkü hız bölüm 4'teki 23 KB/s'nin ~15 katı. Fark yüksek olasılıkla arşivin soğuk ya da sıcak okumasından ve saatten
geliyor (doğrulanamadı). Süre (12 GB):
- 23 KB/s ile ≈152 saat (6,3 gün);
- 341 KB/s tek akışla ≈10 saat;
- 2 akışla ≈5,5 saat.

Bunlara ≈5 200 istek için ~2 saatlik istek gecikmesi eklenir. EarthScope ve federatör hızı ölçülmedi. Bu iki servis
işin ~%26'sını taşıyor.

**Engeller.** Erişim reddi yok. TL, 1O ve TU'nun verisi gelmedi (kısıtlı mı, yok mu, ayrılamadı). 6G'nin 2015 sonrası
epoku verisiz. KOERI availability dizininin eksikliği bu yoklamayla aşıldı: önceki alt sınır 16 çiftti, doğrulanmış
sayı 71 çift.

