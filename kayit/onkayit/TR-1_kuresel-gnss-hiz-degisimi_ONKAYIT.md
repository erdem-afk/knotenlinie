# TR-1 ön kayıt: büyük deprem öncesi yıl ölçekli GNSS hız değişimi, küresel çok olaylı sınav

Sürüm 2, 11 Kasım 2026. Durum: KAPANDI, güç yok (11 Kasım 2026). Sürüm 2 dondurulmadı, veri indirilmedi; üstveri sayımında K 11–12 < 20. Bkz. `TR-1_INCELEME-2.md`.
Sürüm 1 bağımsız incelemede RED aldı (`TR-1_INCELEME-1.md`); bu sürüm o raporun 1–7.
bulgularını işler. Kol: TR (türetme döngüsü). Tarama: `research_notes/Fayın anlık durumu gözlem boşlukları/jeodezik_gecici_gravite.md`.

## 1. Neden bu soru

Önceki sonuç: olay geçmişine koşullama (FA-1) H0, öncü artış modeli (TK-1) ayırt edilemez. Yıl ölçeğine açık kalan yol,
fayın anlık durumunu ölçen bir gözlem. Yer yüzeyinin hızı böyle bir gözlemdir: kilitlenme ya da derin sünme deprem öncesi
yıllarda değişiyorsa yakın GNSS istasyonlarının hızı değişir. Literatürde bu iddia tek olaylı ve rakipsizdir; büyük ölçekli
öncül iddiaları 2026'da bağımsız çözümlerde destek bulmadı (Weerasinghe 2026). Yanlış alarm oranı ölçülmüş, çok olaylı, ön
kayıtlı bir sınav bulunamadı (köprü: öncül jeodezik geçici × tahmin sınama k 8, J 0,0084; pozitif kontrol k 154, J 0,058).

Ölçülen şey bir "öncül" değildir. Ölçülen: M≥6,5 olaydan önceki son 2 yılda, dış merkez çevresindeki istasyonların hız
değişiminin boyu, aynı tarihte başka deprem bölgelerinde (o sırada depremsiz) ölçülen aynı büyüklükten sistematik olarak
büyük mü. Bu sınav deprem tahmini değildir.

## 2. Veri (hepsi açık, 0 €)

- Olay kataloğu: USGS ComCat FDSN, `starttime=2000-01-01`, `endtime=2026-01-01T00:00:00` (2025-12-31 dahil, 2026 hariç),
  `minmagnitude=6.5`, `maxdepth=30`, `orderby=time-asc`, `format=csv`. Dönen satırlardan tarihi ≥ 2026-01-01 olan varsa atılır.
  "Deprem yok" şartları için ikinci sorgu: aynı tarih aralığı, `minmagnitude=6.5`, `maxdepth=70`.
- GNSS: Nevada Geodetic Laboratory günlük çözümleri, `https://geodesy.unr.edu/gps_timeseries/IGS20/tenv3/IGS20/{STA}.tenv3`
  (küresel çerçeve; levhaya sabitli dizinler kullanılmaz). Yatay bileşenler (doğu, kuzey). İstasyon listesi ve konumları
  `DataHoldings.txt`. İndirilen her dosyanın SHA-256'sı ve indirme zamanı `indirme_kaydi.csv` dosyasına yazılır.
- Basamak listesi: NGL `steps.txt`. Tarih alanı `YYMONDD`; iki basamaklı yıl 00–79 → 2000–2079, 80–99 → 1980–1999.
  Tarihi ≥ 2026-01-01 olan satırlar ayrıştırmada atılır. Kod 1 ekipman değişimi. Kod 2 satırı
  `STA tarih 2 eşik_km uzaklık_km M olay_id` biçimindedir ve bir algılama değil yarıçap kuralıdır.
- Dışlanan istasyonlar: Marmara kutusu (39,5–42,0° K, 26,0–31,5° D). Gerekçe: VE-1 adayının 2017 sonrası Marmara GNSS
  körlüğü. Kutu içindeki hiçbir seri indirilmez.
- Zaman: tenv3'teki MJD. 1 yıl = 365,25 gün. Uzaklık: küre üzerinde haversine, R = 6371 km; boylamlar [−180, 180)'e sarılır.

## 3. Tanımlar

**Pencere.** Epok T (olay günü, UTC, MJD tam sayı) için W(T) = [T − 5 yıl − 7 gün, T − 7 gün]. Menteşe H = T − 2 yıl − 7 gün.
"Taban" = [T − 5 yıl − 7 gün, H), "yakın dönem" = [H, T − 7 gün]. T − 7 günden sonraki hiçbir gözlem ve hiçbir basamak
kaydı kullanılmaz (olayın kendi kod 2 kaydı dahil).

**İstasyon uygunluğu** (bir T için):
1. Doluluk: tabanda ve yakın dönemde, çözümü olan gün sayısı / takvim günü sayısı ≥ 0,60 (her biri ayrı).
2. Yakın deprem elemesi: [T − 8 yıl − 7 gün, T − 7 gün] aralığında, uzaklığı < eşik/4 olan bir kod 2 kaydı varsa istasyon
   uygun değildir (o depremin kosismik ve postsismik etkisi büyük). Kural olay, kontrol ve plasebo kümelerine aynen uygulanır.
3. Marmara kutusunda değildir.

**İstasyon ölçüsü.** Her yatay bileşen için W(T) içindeki günlük konumlara en küçük kareler ile şu model uydurulur:
sabit + doğrusal eğim + yıllık ve altı aylık sinüs/kosinüs + basamak terimleri + menteşe terimi max(0, t − H).
Basamak terimleri: W(T) içine düşen her kod 1 kaydı ve (2. kuralla elenmemiş) her kod 2 kaydı için bir Heaviside sıçraması.
Aynı güne düşen birden çok kayıt tek sıçramadır. Bir sıçrama H'ye ±30 günden yakınsa ya da pencerenin ilk ya da son
30 gününe düşüyorsa istasyon o T için uygun değildir (menteşeyle ayrışmaz). Dayanıklı ayıklama bir kez, bileşen başına:
ilk uydurmadan sonra |artık| > 5 × 1,4826 × MAD olan günler o bileşenden atılır ve model yeniden uydurulur.
Hız değişimi vektörü Δv = (menteşe katsayısı doğu, menteşe katsayısı kuzey), mm/yıl.

**Küme.** Bir merkez noktası ve T için: "yakın" = merkezin ≤ 100 km içindeki uygun istasyonlar; "referans" = halka içindeki
uygun istasyonlar. Halka, kümenin bağlı olduğu olayın büyüklüğüne göre: M < 7,5 için 200–500 km, M ≥ 7,5 için 500–1000 km
(büyük olaylarda olası sinyal 500 km'ye uzanabilir; halka onun dışında tutulur). İstasyonlar merkeze uzaklığa göre sıralanır
(eşitlikte istasyon adı). Olay kümesi: en yakın en çok 8 yakın ve en çok 8 referans istasyon; geçerlilik ≥ 3 yakın ve ≥ 3
referans. n_y ve n_r olay kümesinin bu sayılarıdır.

**Küme ölçüsü S.** Her yakın istasyonun Δv'sinden referans istasyonların Δv'lerinin bileşen bazında medyanı çıkarılır;
kalan vektörün boyu alınır; S bu boyların yakın istasyonlar üzerindeki medyanıdır (mm/yıl).

**Olay kümesi.** Merkez = dış merkez, T = olay günü. Ana satıra giren olaylar: T ≤ 2023-12-31 (kontrol şartı T + 2 yıl
ister ve katalog 2025 sonunda biter) ve küme geçerli.

**Kontrol kümeleri** (her olay için). Aday merkezler: katalogdaki ÖTEKİ M≥6,5, derinlik ≤30 km olayların dış merkezleri
(yani bilinen deprem üreten yerler; olay bölgeleriyle aynı türden). Epok aynı T. Şartlar:
(a) merkez, olayın dış merkezinden ≥ 600 km uzakta;
(b) merkezin 100 km içinde, [T − 8 yıl, T + 2 yıl] aralığında M≥6,5, derinlik ≤70 km olay yok;
(c) kümede tam n_y yakın ve tam n_r referans istasyon var (en yakınlar alınır; daha azı varsa aday geçersiz), halka olayınkiyle aynı;
(d) kontrolün hiçbir istasyonu olayın dış merkezine 600 km'den yakın değil;
(e) seçilen kontrol merkezleri birbirinden ≥ 150 km uzak.
Sıralama: adaylar SHA-256(olay ComCat kimliği + "|" + aday ComCat kimliği) onaltılık değerine göre artan sıralanır; sırayla
gezilir, (a)–(e)'yi sağlayan ilk 10 alınır. Geçerli kontrol sayısı < 5 ise olay ana satıra girmez (sayısı raporlanır).

**Olay puanı r.** r = [#(S_kontrol < S_olay) + 0,5 × #(S_kontrol = S_olay)] / n_kontrol. H0 altında E[r] = 0,5.

**Bağımsızlık kümeleri.** İki olay aynı kümededir, eğer (i) dış merkezleri < 300 km ve tarihleri < 1 yıl yakınsa, ya da
(ii) olay kümeleri (yakın + referans) en az bir ortak istasyon içeriyor ve pencereleri çakışıyorsa. Kümeler bu ilişkinin
bağlı bileşenleridir. Küme puanı = kümedeki olayların r ortalaması. K = küme sayısı.

## 4. Hüküm satırı (tek)

Ölçü: küme puanlarının ortalaması r̄ (K küme, eşit ağırlık). Sınırlar küme puanlarından t dağılımıyla:
r̄ ± t(0,95; K − 1) × s / √K (tek yanlı %95).

Sıra şöyledir ve kod bunu insan müdahalesi olmadan uygular:

1. **Güç kapısı.** K < 20 ise hüküm "güç yok"tur; olay puanları yazdırılmaz. K ≥ 20 ise yaklaşık ölçülebilir en küçük etki
   0,5 + 2,49 × 0,32 / √K olarak yazılır (10 kontrollü r'nin H0 standart sapması ≈ 0,316; K 25 için ≈ 0,66, K 40 için ≈ 0,63).
2. **Negatif kontrol.** Her olayın SHA sırasındaki ilk kontrolü "sahte olay" sayılır, kalan kontrollere karşı puanlanır.
   Sahte olay ortalamasının iki yanlı %95 t aralığı 0,5'i içermiyorsa hüküm "geçersiz (kod ya da tasarım)" olur ve durulur.
3. **Yerinde plasebo (yanlılık denetimi).** Aynı dış merkez, epok T − 5 yıl (penceresi olay penceresiyle çakışmaz), aynı
   kurallar ve o epok için yeniden seçilen kontroller; ayrıca merkezin 100 km içinde [T − 13 yıl, T − 7 gün] aralığında
   başka M≥6,5 olay olmamalı. Plasebo kümeleri ≥ 10 ise: plasebo ortalamasının tek yanlı %95 alt sınırı > 0,5 çıkarsa hüküm
   "ayırt edilemez (bölge yanlılığı)" olur; H1 ilan edilemez. Plasebo kümeleri < 10 ise yanlılık denetlenemedi sayılır ve
   H1 yine ilan edilemez (en çok "ayırt edilemez").
4. **Duyarlılık (pozitif kontrol).** Kontrol kümelerinin yakın istasyon serilerine H'den sonra max(0, t − H) × g biçiminde,
   doğu yönünde yapay hız değişimi eklenir (g = 0,5 / 1 / 2 / 3 mm/yıl; referanslara eklenmez); her biri için sahte olay
   ortalaması raporlanır. g = 3 mm/yıl'da ortalama < 0,75 ise ölçü kör sayılır ve hüküm "güç yok" olur.
5. **Hüküm.** Öncelik sırasıyla: H1, r̄ alt sınırı > 0,5 (ve 3. adım engel değilse); değilse H0, r̄ üst sınırı < 0,60;
   değilse "ayırt edilemez".

Hükümlerin anlamı:
- H1: olay öncesi hız değişimi boyu kontrollerden büyük ve plasebo bunu bölge farkıyla açıklamıyor. Tahmin becerisi iddiası
  değildir; yalnız bir sonraki sorunun (ileriye dönük alarm, yeni ön kayıt) açılma şartıdır.
- H0: bu ölçü (boy, 100 km, son 2 yıl / önceki 3 yıl) bu örneklemde (ağırlıkla Japonya ve Şili, dalma-batma) kontrollerden
  ayrışmıyor ve AUC 0,60 düzeyindeki bir etki dışlanıyor. Yönlü ölçüleri, başka pencereleri ve doğrultu atımlı fayları kapatmaz.
- Gerçek etki sıfırken H0 hükmü alma olasılığı K'ye bağlıdır (K 25'te ≈ %50, K 60'ta ≈ %80); K ilan edilirken yazılır.
  Yani "ayırt edilemez" bu tasarımda olası bir sonuçtur ve "etki var" anlamına gelmez.

## 5. Koşu düzeni ve körlük

- Kod yalnız yapay serilerle (beyaz + titreşim gürültüsü, mevsimsel, sıçrama, bilinen menteşe) ve dosya biçimi için
  hiçbir katalog olayına 1500 km'den yakın olmayan en çok 5 gerçek istasyonla geliştirilir ve sınanır.
- İndirme öncesi eleme yalnız üstveriyle yapılır (`DataHoldings.txt`, `steps.txt`, katalog); adaylar uzaklık sırasıyla
  indirilir, gereken sayı bulununca durulur.
- Ön kayıt ve kod commit + push edildikten sonra tek bir komut bütün zinciri koşar: K sayımı, negatif kontrol, plasebo,
  duyarlılık, hüküm. Olay kümelerinin S ve r değerleri yalnız 1. ve 2. adım geçerse dosyaya yazılır.
- Koşu bir kez yapılır. Kod hatası bulunursa düzeltme ek olarak kaydedilir ve ikinci koşunun kör olmadığı yazılır.

## 6. Bilgi satırları (hüküm vermez)

Olay ağırlıklı ortalama r; yakın dönem 1 yıl ve 3 yıl (taban 5 yılın kalanı); yalnız M≥7; yalnız doğrultu atımlı (USGS
moment tensörü, düğüm düzlemlerinden biri için |rake| ≤ 30° ya da ≥ 150°); Japonya hariç; referans farkı alınmadan;
T > 2023 olaylar (kontrol şartı kısaltılarak); olay başına S, r, n_y, n_r tablosu; elenen olay ve istasyon sayıları.

## 7. Bilinen sınırlar

- Ölçü gürültüyle yukarı kayar (vektör boyu). Kontrolleri deprem üreten yerlerden seçmek ve istasyon sayısını eşitlemek
  bölge farkını azaltır, sıfırlamaz; yerinde plasebo kalan farkı ölçer. Plasebo yalnız ≥ 10 yıllık serisi olan olaylarda
  hesaplanabilir.
- Yavaş kayma olayları, eski büyük depremlerin postsismik eğriliği (Tohoku, Maule, Sumatra) ve volkanik deformasyon olay
  bölgelerinde öncülden bağımsız olarak hız değişimi üretir; plasebo bunu yakalamak içindir.
- 2. uygunluk kuralı öncü dizisi olan olaylarda (yakında M≥~6 öncü) yakın istasyonları eleyebilir; yanlılık H0 yönündedir.
- Örneklem ağırlıkla dalma-batma. Doğrultu atımlı alt küme (kaba sayım ≤ 18 olay) tek başına güçsüzdür; sonuç Marmara'ya
  doğrudan aktarılamaz.
- Günlük çözümler ortak yörünge/saat ürününe dayanır; referans farkı ve aynı epokta kontrol bunu azaltır.
- NGL dosyaları sürekli yeniden işlenir; yeniden üretim için SHA kaydı tutulur, dosyalar depoya konmaz.

## 8. Marmara ile bağ

Marmara verisi kullanılmaz. H0 ya da ayırt edilemez: "yıl ölçekli hız değişimi boyu" Marmara için alarm adayı olarak
önerilmez; yönlü ölçü ayrı sorudur. H1: süren Marmara istasyonlarıyla (ISTA, QIBP, ORE1) ileriye dönük izleme ayrı ön
kayıtla önerilir. Mutlak olasılık yazılmaz.

## 9. Yeniden açma şartı

Güç yok, geçersiz ya da ayırt edilemez ile kapanırsa: (a) fay doğrultusuna izdüşümlü yönlü ölçü, ya da (b) uygun olay
sayısını en az iki katına çıkaran yeni bir açık GNSS arşivi, yeni ön kayıtla.
