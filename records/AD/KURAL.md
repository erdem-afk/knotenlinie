# AD/KURAL — Kaliforniya uzun vade ölçüm kuralı (2006+ puanlamasından önce donduruldu)

Yazıldığı an: 2026-10-12, 2006+ hiçbir hedef puanlanmadan; yalnız HKJ07 dosyalarının biçimi ve ComCat
yıllık olay sayıları (tamlık için) görülmüştü. Sonradan değişiklik yalnız tarihli "Ek" olarak gelir.

## Veri ve çerçeve

Katalog: ANSS ComCat FDSN, `eventtype=earthquake`, M≥2,5, kutu enlem 30,55–43,95, boylam −126,35 – −112,15
(HKJ07'nin kutusu; RELM test alanından 1° tampon), 1981-01-01 – **2020-12-31**. Hedef ve puan alanı: HKJ07
dosyasındaki 7682 hücre (RELM test alanı, 0,1°), derinlik `[0,30)` km, büyüklük kutuları 4,95 + 0,1·k
(k=0…40), son kutu `[8,95, +∞)`. Mw yerine ComCat `mag` (karışık tür, HKJ07 de ANSS) kullanılır.
Mühür: `endtime=2020-12-31T23:59:59`; `tools/muhur.py` temiz.

## Karşı taraf

HKJ07 (Helmstetter, Kagan, Jackson 2007) iki sürüm: **ana şok** (bağımsız olaylar; Reasenberg
kümesizleştirilmiş katalogdan, bağımsızlık olasılığı ağırlıklı, N0=4,41/yıl, b=0,89) ve **artçı** (bütün olaylar,
N0=7,38/yıl, b=0,95); ikisi aynı uzaysal yoğunlukta, bükülü GR (köşe M 8). Veri 1981-01-01 – 2005-08-23, M≥2.
Dosya 5 yıllık sayılar; süreye orantılı ölçeklenir (2011–2020 için ×2).

## Bizim model (`tools/kaliforniya/model.py`)

Uyarlamalı Gauss KDE (k'inci komşu bandı, alt sınır 0,5 km, üst 300 km), **hücre üzerinde entegre**, bölge içi
kütle 1'e normalize, düzgün zemin payı 0,002; girdi kümesizleştirilmiş (Gardner–Knopoff 1974 birincil)
olaylar, derinlik <30 km, M≥`kde_mmin`. Toplam oran ve b: Weichert (1980), tek tamlık dönemi (1981'den, Mc),
bölge içi olaylar, M≥4,95'e saf GR ile; magnitüd dağılımı HKJ07 gibi **bükülü GR, köşe M 8**. Ana şok modeli
kümesiz katalogdan, artçı modeli bütün katalogdan oran ve b alır; ikisi aynı şekli kullanır.
Kümesizleştirme her kesimde yalnız o kesimden önceki olaylarla yapılır (simetrik pencere geleceği sızdırır).

## Seçim (yalnız ≤2005 verisiyle; 2006+ görülmez)

Modeller ≤2000 (kesim 2001-01-01) kurulur, **2001–2005** hedefleriyle seçilir. Hedef: GK74 kümesiz (ana şok)
ve bütün olaylar, bölge, derinlik <30, **M≥3,95** (geliştirme eşiği). Adaylar (24): `k ∈ {5,10,20,40}`,
`kde_mmin ∈ {2,5; 3,0; 3,5}`, `geysers ∈ {kapalı, açık}` (açıkken boylam −122,95…−122,65, enlem 38,7…38,9
kutusunda M<4 olaylar KDE'den çıkarılır; HKJ07'nin Geysers düzeltmesinin sadeleşmişi). Şekil ölçütü
koşullu uzaysal log-olabilirlik `Σ log(şekil_hücre)` (kümesiz hedef). Oran `Mc ∈ {3,0; 3,5}` ayrı ayrı ana şok
ve artçı için, 2001–2005 M≥3,95 toplam sayısına Poisson logL ile seçilir. Seçilen değerler olduğu gibi
≤2005 (adil satır, kesim 2006-01-01) ve ≤2010 (güncel satır, kesim 2011-01-01) verisiyle yeniden kurulur;
yeniden seçim yoktur.

## Ölçüm

Dönemler: **2011-01-01 – 2021-01-01 (10 yıl)** ve 2006-01-01 – 2011-01-01 (5 yıl, RELM penceresi); hedefler
M≥4,95, hücre×kutu. İki hedef türü: **kümesiz** (GK74, tüm 1981–2020 katalogda; bizim ana şok − HKJ07-ana şok)
ve **bütün olaylar** (bizim artçı − HKJ07-artçı). Hücre×kutu Poisson logL; olay başına
`IG = mean(log λ_bizim − log λ_HKJ) − (Λ_bizim − Λ_HKJ)/N`; olay yeniden örneklemeli bootstrap SE (2000, tohum
20261005), tek yönlü z; yıl bloğu bootstrap SE ek; N/S/M (Zechar) her iki tarafa; güç beyanı
`Φ(IG/SE − 1,645)`. Poisson kimliği `(logL_bizim − logL_HKJ)/N = IG` her satırda zorunlu.

**Birincil (hüküm) satır:** adil satır (≤2005 veri), 2011–2020, M≥4,95; iki karşılaştırma (ana şok, artçı)
Holm ile; "geçti" = IG>0 ve z>1,645. **İkincil:** adil satır 2006–2010 (RELM penceresi), güncel satır
(≤2010 veri) 2011–2020; güncel satırın 2006–2010 puanı veri içidir ve yalnız bilgi olarak verilir.
Ek ayrıştırma: bizim şekil × HKJ07 toplamı (Λ eşitlenmiş) satırı, oran farkını şekil farkından ayırır.

## Duyarlılık (hüküm değil)

(i) saf GR (bükülmesiz); (ii) Reasenberg kümesizleştirme (HKJ07 parametreleri, eğitimde ve hedefte);
(iii) oran için diğer Mc; (iv) Geysers bayrağının tersi. Seçilen hiperparametreler sabit kalır.

## Sınırlar (peşin)

HKJ07 spatial Mc düzeltmesi ve güç-yasası çekirdeği yoktur; Gauss çekirdek ve `kde_mmin` seçimi bunun yerine
konur. GEAR1 Kaliforniya M≥5,95 ek satırı için yerelde 0,1° Kaliforniya kesiti yoktur; varsa eklenir, yoksa
açık kalan olarak yazılır. Olay bootstrap'ı kümelenmeyi hesaba katmaz; bütün-olay
satırlarında SE küçük kalır, yıl bloğu SE bunun kaba bir kontrolüdür.

## Ek 1 (2026-10-12 02:45 UTC; 2006+ hâlâ puanlanmadı)

İlk seçim koşusunda (24 aday) en iyi `k=5` ızgara sınırındaydı (logL_uzay k=40→20→10→5 monoton arttı).
Seçim ≤2005 verisiyle olduğundan ızgara `k ∈ {2,3,5,10,20,40}` (36 aday) olarak genişletildi ve seçim yeniden
koşuldu. En iyi yine sınırda (`k=2`, kde_mmin 3,0, Geysers kapalı); bu **son** genişletmedir (k=1 kendini
sayar ve dejeneredir). Sınırda seçim "açık kalan" olarak raporlanır; 2006+ sonucuna göre seçim değişmez.
Seçim çıktısı `SECIM.json`'da (36 aday). İlk 24-aday koşusu `k=5, kde_mmin 3,0, Geysers kapalı` seçmişti;
genişletme yalnız sınır uyarısıyla yapıldı, sonuç görülmeden.
