# TR-1 ön kayıt: büyük deprem öncesi yıl ölçekli GNSS hız değişimi, küresel çok olaylı sınav

Tarih: 11 Kasım 2026. Durum: TASLAK (bağımsız incelemeden sonra dondurulur; dondurma commit'i veri işlenmeden önce atılır).
Kol: TR (türetme döngüsü). Kaynak tarama: `research_notes/Fayın anlık durumu gözlem boşlukları/jeodezik_gecici_gravite.md` (aday adı orada JG-1).

## 1. Neden bu soru

Önceki sonuç: olay geçmişine koşullama (FA-1) H0, öncü artış modeli (TK-1) ayırt edilemez. Yıl ölçeğine açık kalan yol,
fayın anlık durumunu ölçen bir gözlem. Yer yüzeyinin hızı böyle bir gözlemdir: kilitlenme ya da derin sünme deprem öncesi
yıllarda değişiyorsa yakın GNSS istasyonlarının hızı değişir. Literatürde bu iddia tek olaylı ve rakipsizdir (Mavrommatis
2014, Yokota ve Koketsu 2015, Melnick 2017, Bedford 2020); büyük ölçekli öncül iddiaları 2026'da bağımsız çözümlerde destek
bulmadı (Weerasinghe 2026). Yanlış alarm oranı ölçülmüş, çok olaylı, ön kayıtlı bir sınav bulunamadı. Köprü ölçümü: öncül
jeodezik geçici × tahmin sınama k 8, J 0,0084; pozitif kontrol (sınama × ETAS) k 154, J 0,058.

Bu sınav deprem tahmini değildir. Ölçtüğü şey: "M≥6,5 öncesi son 2 yılda yakın istasyonların hızı, aynı dönemde depremsiz
yerlerdeki istasyonlara göre daha çok değişiyor mu?" Hayırsa bu gözlem türü yıl ölçeği için Marmara'da da aday olamaz.

## 2. Veri (hepsi açık, 0 €)

- Olaylar: USGS ComCat, 2000-01-01 ile 2025-12-31 arası, M≥6,5, derinlik ≤30 km. Sorgu bitişi 2025-12-31; 2026 okunmaz.
- GNSS: Nevada Geodetic Laboratory günlük çözümleri (tenv3, NGL'in güncel küresel çerçevesi), yatay bileşenler (doğu, kuzey).
- Basamak listesi: NGL `steps.txt` (kod 1 ekipman değişimi, kod 2 olası deprem basamağı).
- Dışlanan istasyonlar: Marmara kutusu (39,5–42,0° K, 26,0–31,5° D). Gerekçe: VE-1 adayının 2017 sonrası Marmara GNSS
  körlüğü sürüyor. Kutu içindeki hiçbir seri indirilmez.
- Her seri olay tarihinden 7 gün önce kesilir. Olay sonrası veri hiçbir hesaba girmez.

## 3. Tanımlar

Pencere: epok T için [T − 5 yıl − 7 gün, T − 7 gün]. Son 2 yıl "yakın dönem", önceki 3 yıl "taban".

İstasyon uygunluğu (bir pencere için): taban ve yakın dönemin her birinde günlük çözüm doluluğu ≥ %60; pencere içinde ve
pencere başlangıcından önceki 3 yılda `steps.txt`'te kod 2 (deprem) basamağı yok. Kod 2 kuralı, önceki depremlerin kosismik
ve postsismik etkisini dışarıda bırakmak içindir ve olay ile kontrol pencerelerine aynen uygulanır.

İstasyon ölçüsü: her yatay bileşene en küçük kareler ile şu model uydurulur: sabit + doğrusal hız + yıllık ve altı aylık
sinüs/kosinüs + pencere içindeki her kod 1 basamağı için bir sıçrama + T − 2 yıl − 7 gün anında başlayan ek eğim (sürekli
parçalı doğrusal). Bir kez dayanıklı ayıklama yapılır (artık > 5 × 1,4826 × MAD olan günler atılır) ve model yeniden
uydurulur. Hız değişimi vektörü Δv = (ek eğim doğu, ek eğim kuzey), mm/yıl.

Küme: bir merkez noktasının 100 km içindeki uygun istasyonlardan en yakın 8'i ("yakın") ve 200–500 km arasındaki uygun
istasyonlardan en yakın 8'i ("referans"). Küme geçerliliği: ≥3 yakın ve ≥3 referans istasyon.

Küme ölçüsü S: her yakın istasyonun Δv'sinden referans istasyonların Δv'lerinin bileşen bazında medyanı çıkarılır; kalan
vektörün boyu alınır; S bu boyların yakın istasyonlar üzerindeki medyanıdır (mm/yıl). Referans farkı, çerçeve ve ortak mod
kaymalarını (yörünge/saat ürünü, bölgesel su yükü) gidermek içindir.

Olay kümesi: merkez = dış merkez, T = olay tarihi. Küme geçerli değilse olay sınava girmez (sayısı raporlanır).

Kontrol kümeleri (her olay için): aynı T'de, merkezi dış merkezden 500–1500 km uzaktaki bir NGL istasyonu olan kümeler.
Şartlar: kümenin kendisi geçerli; merkezin 100 km içinde, T'den sonraki 2 yılda (en geç 2025-12-31) M≥6,5 derinlik ≤70 km
olay yok (kontrol kendisi "deprem öncesi" olmasın); kontrol merkezleri birbirinden ≥150 km uzak. Aday merkezler istasyon
adına göre alfabetik sıralanır ve SHA-256(olay kimliği + istasyon adı) değerine göre sıralanıp ilk 10 geçerli olan alınır.
Geçerli kontrol sayısı < 5 ise uzaklık aralığı 500–3000 km'ye genişletilir; yine < 5 ise olay sınava girmez.

Olay puanı r: olayın S değerinden küçük S'ye sahip kontrollerin oranı (eşitlik yarım sayılır). H0 altında r, [0, 1]
aralığında tekdüze dağılır ve ortalaması 0,5'tir. r > 0,5: olay öncesi hız değişimi kontrollerden büyük.

Bağımsızlık kümeleri: dış merkezleri 300 km'den yakın ve tarihleri 1 yıldan yakın olaylar tek kümedir (tek bağlantılı).
Standart hata küme bootstrap'i ile (10 000 yineleme, tohum 20261111) hesaplanır.

## 4. Hüküm satırı (tek)

Ölçü: tüm geçerli olaylarda ortalama r (katmanlı AUC).

- Güç kapısı (koşudan önce, olay puanları hesaplanmadan ilan edilir): bağımsızlık kümesi sayısı K < 20 ise hüküm
  "güç yok"tur ve olay puanları hesaplanmaz. K ≥ 20 ise ölçülebilir en küçük etki yaklaşık 0,5 + 2,49 × 0,289 / √K
  (K 40 için 0,61) olarak yazılır.
- H1: ortalama r'nin tek yanlı %95 alt sınırı > 0,5.
- H0 (bu ölçüyle yol kapalı): tek yanlı %95 üst sınır < 0,60.
- Ayırt edilemez: diğer bütün durumlar.

Hüküm ne çıkarsa çıksın bir kez koşulur ve yazılır. H1 çıkarsa bu bir tahmin becerisi iddiası değildir; yalnız bir
sonraki sorunun (aynı ölçünün ileriye dönük alarm olarak puanlanması, yeni ön kayıtla) açılma şartıdır.

## 5. Denetimler (hükümden önce, olay puanlarına bakmadan)

- Negatif kontrol: her olayın kontrollerinden ilki "sahte olay" sayılır, kalanlarına karşı puanlanır. Beklenen ortalama
  0,5; tek yanlı iki yönde de %95 aralığı 0,5'i içermezse kod hatalı sayılır ve koşu durur.
- Pozitif kontrol (duyarlılık): kontrol kümelerinin yakın istasyon serilerine, yakın dönemde doğrusal artan yapay bir
  hız değişimi (0,5 / 1 / 2 / 3 mm/yıl, doğu yönünde, referanslara eklenmez) eklenir; ortalama r'nin hangi genlikte 0,61'i
  ve 0,75'i geçtiği raporlanır. Bu, hükmü mm/yıl cinsinden okunur kılar. 3 mm/yıl'da ortalama r < 0,75 ise ölçü kör
  sayılır ve hüküm "güç yok" olur.
- Kod geliştirme yalnız kontrol kümeleri ve yapay sinyalle yapılır. Olay kümelerinin S değeri, bu ön kayıt ve kod
  commit'lendikten sonra tek koşuda hesaplanır.

## 6. Bilgi satırları (hüküm vermez)

Yakın dönem 1 yıl ve 3 yıl (taban 5 yılın kalanı); yalnız M≥7; yalnız doğrultu atımlı (USGS moment tensörü, tırmık açısı
düğüm düzlemlerinden biri için |rake| ≤ 30° ya da ≥ 150°); Japonya hariç; referans farkı alınmadan; olay başına S ve r tablosu.

## 7. Bilinen sınırlar

- Kod 2 kuralı Japonya gibi sık depremli yerlerde çok istasyon ve olay eleyebilir; elenen sayı raporlanır.
- Günlük çözümler ortak yörünge/saat ürününe dayanır; referans farkı bunu azaltır, sıfırlamaz. Aynı epokta kontrol
  seçilmesi kalan etkiyi olay ve kontrolde eşitler.
- Kontroller 500–1500 km uzakta olduğu için gürültü düzeyi olay bölgesinden farklı olabilir (örn. ada istasyonları).
  Bu fark r'yi iki yöne de çekebilir; negatif kontrol bunu yakalamaz. Bilgi satırı "Japonya hariç" kısmen denetler.
- Sinyal yalnız dalma-batma olaylarında varsa sonuç doğrultu atımlı Marmara'ya aktarılamaz; doğrultu atımlı alt küme
  (kaba sayım 18 olay) tek başına güçsüzdür.
- Sonuç hız değişiminin BOYUNU sınar, yönünü değil. Yönlü bir sinyal (fay boyunca) daha güçlü bir ölçü olabilir; bu,
  sonuç ayırt edilemez çıkarsa türetilecek sıradaki sorudur.

## 8. Marmara ile bağ

Marmara verisi kullanılmaz. H0: yıl ölçekli hız değişimi alarmı Marmara için aday olmaz (deftere kapanış). H1: ISTA, QIBP,
ORE1 gibi süren istasyonlarla ileriye dönük izleme ayrı ön kayıtla önerilir. Mutlak olasılık yazılmaz.

## 9. Yeniden açma şartı

Güç yok ya da ayırt edilemez ile kapanırsa: yönlü ölçü (fay doğrultusuna izdüşüm) ya da uygun olay sayısını en az iki
katına çıkaran yeni bir açık GNSS arşivi (örn. GEONET F5 çözümleri doğrudan), yeni ön kayıtla.
