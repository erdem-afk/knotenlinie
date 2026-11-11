# TR-2 ön kaydı: doğrultu atımlı M 6,0–7,2 sonrası gelen M≥6 artçı bulutunun sessiz tarafında mı?

Tarih: 11 Kasım 2026. Durum: TASLAK (inceleme bekliyor; dondurma commit'i bu satırı "DONDURULDU" yapar).
Sayım ve tanımların kaynağı: `kayit/onkayit/TR-2_SAYIM.md`, kod `kayit/turetme/tr2/tr2_sayim.py` (commit d7a4e84).
Maliyet: 0 €. Kör veri: yok; bütün sorguların bitişi 2025-12-31, 2026 hiçbir amaçla sorgulanmaz.

## 1. Soru ve neden

Bir doğrultu atımlı fayda M 6,0–7,2 olay, artçılarını çoğu zaman bir yana yığar. Aynı fay kuşağında bir sonraki
M≥6, artçıların az olduğu (sessiz) tarafta mı olur? Nisan 2025 Marmara Mw 6,2 kırığı doğuya ilerleyip sessiz
kesimin kenarında durdu; "sıradaki olay sessiz tarafta" savı tek olaylı anlatılardan ibaret, puanlı çok olaylı sınavı
yok (köprü k 2, J 0,0022; kontrolde k 154–208). Bu sınav zamanı değil yönü ölçer.

Rakip açıklamalar ve sınav öncesi güven (not): sessiz taraf kırılmamış komşu kesimdir, sonraki olay oradadır (0,35);
artçı yoğun taraf gerilmenin yoğunlaştığı yerdir, sonraki olay oradadır, yani ETAS yönü (0,25); yön bilgi taşımaz
(0,40).

## 2. Veri ve tanımlar

Tanımlar `TR-2_SAYIM.md` §1'deki ANA tanımdır ve harfiyen geçerlidir; varyant aranmaz. Özet: USGS ComCat 1976–2025;
birincil Mw 6,0–7,2, derinlik ≤ 25 km, doğrultu atımlı; kırık boyu L Wells–Coppersmith; artçılar 30 gün, ≤ 3 L,
M ≥ 4; fay doğrultusu artçı ana ekseninden (≥ 5 artçı, λ1/λ2 ≥ 2); |s| < 5 km tarafsız; asimetri ölçülebilir
n+ + n− ≥ 10 ve |A| ≥ 1/3; sessiz taraf artçısı az olan taraf; sonraki olay M ≥ 6, derinlik ≤ 40 km, 30 gün ile
min(15 yıl, 2025-12-31) arası, 0,5 L ≤ |s| ≤ 5 L, |d| ≤ max(L, 30 km), zamanca ilki; bağımsızlık 300 km ve 365,25 gün
tek bağlantılı küme, kümeden zamanca ilk nitelikli birincil.

Sayım (taraf bilgisi hesaplanmadan): nitelikli 49 birincil, bağımsız küme K = 40. Koşu, sayımın kullandığı
11 Kasım 2026 ComCat anlık görüntüsüyle yapılır; ComCat yeniden sorgulanmaz. Görüntü:
`/mnt/project-files/turetme/tr2-ham/tr2_ham_2026-11-11.tar.gz`, sha256
07881910d94d8b66c377c9ae42ce8f1e18843b5117a92cec53aaa527f61efd59 (depoda değil, 1,4 MB). Kod önce K = 40 olduğunu
doğrular; değilse durur. Gerekçe: binom kesikli olduğu için ölçülebilir en küçük oran K ile tekdüze değişmiyor
(K 39: 0,715; 40: 0,699; 41: 0,706; 42: 0,691); katalogdaki tek olaylık bir güncelleme kapıyı keyfî açıp kapatırdı.

İsabet: sınanan sonraki olayın s işareti sessiz tarafın işaretine eşitse 1, değilse 0.

## 3. Hüküm satırı (tek)

Birim küme, X = isabet sayısı, kesin binom.

- H1 (sessiz taraf): X, tek yanlı α 0,05 ile p = 0,5'i reddediyorsa. K = 40 için X ≥ 26.
- H0 (büyük etki yok): X, tek yanlı α 0,05 ile p = 0,70'i reddediyorsa (P(X' ≤ X | p = 0,70) ≤ 0,05). K = 40 için
  X ≤ 22.
- İkisi de değilse: ayırt edilemez.
- İki koşul birlikte sağlanamaz (26 > 22). X 23–25 ayırt edilemez bölgesidir.

Güç kapısı: K ≥ 30 ve ölçülebilir en küçük isabet oranı (güç 0,80) ≤ 0,70. Sayımda K 40, oran 0,699: kapı geçiyor,
0,001 payla ve K 39 ya da 41 olsaydı geçmezdi. Kapı bu yüzden "sınırda geçti" diye kayda girer. Dürüstlük notu: gerçek isabet 0,65 ise güç 0,57, 0,60 ise 0,32. Bu sınav yalnız büyük etkiyi (≈ 0,70)
görür; "ayırt edilemez" küçük etkinin yokluğu demek değildir, H0 da yalnız "0,70 ve üstü yok" demektir.

## 4. İkincil satır: ETAS yönüne karşı (önceden "büyük olasılıkla ayırt edilemez")

Üç modelin küme başına Bernoulli log skoru (nat):

- Taban: p = 0,5.
- Boşluk modeli: P(isabet) = 0,65, sabit.
- ETAS yönü: p_i = R_sessiz / (R_sessiz + R_yoğun), [0,05, 0,95] aralığına kırpılır.
  - R_taraf = Σ_j 10^(1,0·(M_j − 4)) · ∫_kutu (r² + d_j²)^(−1,5) dA; j birincil ve 30 günlük artçıları (sınav
    tanımındaki bulut, tarafsızlar dahil).
  - d_j = max(5 km, 0,5·L(M_j)), L Wells–Coppersmith. Kutu: o taraftaki hedef alanı (0,5 L ≤ |s| ≤ 5 L,
    |d| ≤ max(L, 30 km)), 2 km ızgarayla sayısal toplam.
  - Parametreler uydurulmaz; üs 1,5 ve verim üssü 1,0 küresel ETAS çalışmalarındaki olağan değerlerdir. Arka plan
    iki kutuda eşit sayılır.
  - p_i değerleri isabetler hesaplanmadan önce ayrı bir dosyaya yazılır ve commit edilir.

Satırlar: boşluk − taban, ETAS − taban, boşluk − ETAS; küme bootstrap'i 10 000 yineleme, tohum 20261111, %95
aralık. Bir fark için "ayrışır" hükmü: aralık sıfırı içermiyorsa. Beklenen boşluk − taban kazancı p = 0,65'te
≈ 1,8 nat ve gürültüyle aynı mertebede; bu satır karar satırı değil, ETAS'ın yön bilgisinin ilk ölçümüdür.

## 5. Bilgi satırları (hükmü değiştirmez)

1. Örnekleme yanlılığı denetimi: dış merkezin artçı ağırlık merkezine doğrultu boyunca uzaklığı u/L. İsabet oranı
   u/L medyanının altı ve üstü için ayrı yazılır. Tek yönlü kırılmada sessiz taraf "kırığın arkası"dır; etki yalnız
   üst yarıdaysa bulgu kırılma yönüne aittir.
2. Merkez olarak dış merkez yerine artçı ağırlık merkezini kullanan tanımla X.
3. Zayıf düzlem seçimi (düğüm düzlemi ile artçı ekseni arası > 30°) olan ve olmayan kümelerde X.
4. Sonraki olay adayı ≥ 3 olan ve olmayan kümelerde X.
5. Daha büyük bir olayın gölgesindeki birinciller dışlanınca X ve K (sayımda K 29, kapı kapalı).
6. Ters yön: X, tek yanlı α 0,05 ile p = 0,5'in altındaysa (K = 40 için X ≤ 14) "yoğun taraf lehine" notu düşülür.
7. Türkiye: kutuda tek küme (1999 Düzce); sonucu yalnız anılır.

## 6. Koşu sırası ve körlük

1. Bu ön kayıt incelenir, dondurulur, commit + push edilir.
2. İsabet kodu `tr2_sayim.py` üstüne eklenir; yalnız yapay katalogla (işareti bilinen uydurma olaylar) sınanır.
   Kod incelemesi gerçek isabet çıktısı üretilmeden yapılır.
3. ETAS p_i dosyası üretilir ve commit edilir.
4. Tek koşu. Çıktı ne olursa olsun yazılır. Koşudan sonra tanım, eşik ya da küme kuralı değişmez.

Bugüne dek sonraki olayın tarafı hiçbir kodda hesaplanmadı. Yazar, olayların birkaçını (1999 İzmit–Düzce, 2025
Marmara) literatürden tanıyor; bu yüzden tanımlar sayım ajanınca taraf bilgisi olmadan seçildi ve burada değiştirilmedi.

## 7. Sınırlar

- "Aynı fay" geometrik bir vekildir; sonraki olayın mekanizması sınanmaz.
- Küresel M ≥ 4 tamlığı ağ geometrisine bağlıdır; asimetrinin bir bölümü örnekleme olabilir.
- 49 nitelikli birincilin 40'ı 2000–2019 arasındadır; 19'unun izleme süresi 15 yıldan kısadır.
- Kapı yalnız ana tanımla geçiyor; altı varyantın üçünde kapanıyor. Ana tanım kapı için seçilmedi, sayımdan önce
  yazılmış çerçevedir.

## 8. İstanbul'a bağ

H1 çıkarsa: Nisan 2025 Mw 6,2 için KOERI kataloğuyla (2025, geliştirme verisi) aynı asimetri ölçüsü hesaplanır ve
"sıradaki M≥6 hangi yanda daha olası" sorusuna yalnız oran olarak cevap veren bir uzamsal terim ileri test defterine
rakip girer. Mutlak olasılık yazılmaz. H0 ya da ayırt edilemez çıkarsa Marmara'ya hiçbir şey taşınmaz.
Bu sınav zaman eksenini daraltmaz; yalnız uzamsal ekseni (İstanbul 30 yıl aralığının ≈ %46'sı) hedefler.

## 9. Yeniden açma şartı

Kapanırsa: (a) küresel M ≥ 3,5 tamlığı olan bir katalogla K ≥ 80 elde edilirse, ya da (b) kırılma yönü (yayımlanmış
sonlu fay modelleri) en az 30 kümede bilinir ve sessiz taraf kırılma yönünden ayrıştırılabilirse.
