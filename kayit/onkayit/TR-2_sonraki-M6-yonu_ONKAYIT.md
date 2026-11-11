# TR-2 ön kaydı: doğrultu atımlı Mw 6,0–7,2 sonrası gelen M≥6, artçısı az olan tarafta mı?

Tarih: 11 Kasım 2026. Durum: DONDURULDU (sürüm 2; inceleme 1 "düzeltmeyle kabul", bütün bulgular işlendi:
`kayit/onkayit/TR-2_INCELEME-1.md`). Bu commit'ten sonra metin değişmez; ekler ayrı başlıkla yazılır.
Sayım ve tanımların kaynağı: `kayit/onkayit/TR-2_SAYIM.md`, kod `kayit/turetme/tr2/tr2_sayim.py` (commit d7a4e84).
Maliyet: 0 €. Kör veri: yok; veri 2025-12-31'de biter, 2026 hiçbir amaçla sorgulanmaz.

## 1. Soru ve neden

Bir doğrultu atımlı fayda Mw 6,0–7,2 olay, artçılarını çoğu zaman bir yana yığar. Aynı kuşakta bir sonraki M≥6,
artçıların az olduğu tarafta mı olur? Nisan 2025 Marmara Mw 6,2 olayının artçıları yerel kataloglarda doğuya yığıldı.
Bu, "sıradaki olay az artçılı tarafta" anlatısını besledi. Bulabildiğimiz kadarıyla bu savın puanlı, çok olaylı bir
sınavı yok: bu konudaki işlerle tahmin sınama literatürünün ikisine birden atıf yapan 2 iş bulduk; aynı ölçüyle
bilinen dolu bir köprüde (tahmin sınama ile ETAS) 154–208 iş var. Bu sınav zamanı değil yönü ölçer.

Bu belgede "sessiz taraf" yalnız "30 günlük artçısı az olan taraf" demektir; sismik boşluk ya da kilitli kesim
anlamına gelmez.

Rakip açıklamalar ve sınav öncesi güven (not): sonraki olay artçısı az taraftadır (0,30); sonraki olay artçısı çok
taraftadır, yani ETAS yönü ya da ortak arka plan (0,30); yön bilgi taşımaz (0,40).

## 2. Veri ve tanımlar

Tanımlar `TR-2_SAYIM.md` §1'deki ANA tanımdır ve harfiyen geçerlidir; varyant aranmaz. Özet: USGS ComCat 1976–2025;
birincil Mw 6,0–7,2, derinlik ≤ 25 km, doğrultu atımlı; kırık boyu L Wells–Coppersmith; artçılar (t0, t0 + 30 gün],
≤ 3 L, M ≥ 4, M < Mw; fay doğrultusu artçı ana ekseninden (≥ 5 artçı, λ1/λ2 ≥ 2); |s| < 5 km tarafsız; asimetri
ölçülebilir n+ + n− ≥ 10 ve |A| ≥ 1/3; sessiz taraf artçısı az olan taraf; sonraki olay havuzu M ≥ 6, derinlik
≤ 40 km, büyüklük türü ve mekanizma serbest; 0,5 L ≤ |s| ≤ 5 L, |d| ≤ max(L, 30 km), zamanca ilki; bağımsızlık 300 km
ve 365,25 gün tek bağlantılı küme, kümeden zamanca ilk nitelikli birincil. Koddaki kaba enlem ön süzgeci
(|Δenlem| > 8°) kutudan geniştir, sonucu etkilemez.

SAYIM §1'e göre üç netleştirme:
- Sonraki olay aralığı (t0 + 30 gün, min(t0 + 15 yıl, 2025-12-31)] (30. gün artçı aralığına aittir).
- s işareti, sessiz tarafın hesaplandığı doğrultu (stk) ile ve aynı `eksen_bilesen` fonksiyonuyla, dış merkez
  kökenli hesaplanır. Eşitlik olamaz: |s| ≥ 0,5 L > 0 ve |A| ≥ 1/3.
- Bir M ≥ 6 olayı birden çok kümenin ilk sonraki olayıysa yalnız zamanca ilk birincilin kümesi için sayılır; diğer
  kümeler sıradaki adayla değerlendirilir. Anlık görüntüde bu durum taraf bilgisi olmadan sayıldı: 0 küme.

Sayım (taraf bilgisi hesaplanmadan): nitelikli 49 birincil, bağımsız küme K = 40. Koşu, sayımın kullandığı
11 Kasım 2026 ComCat anlık görüntüsüyle yapılır; ComCat yeniden sorgulanmaz. Görüntü:
`/mnt/project-files/turetme/tr2-ham/tr2_ham_2026-11-11.tar.gz`, sha256
07881910d94d8b66c377c9ae42ce8f1e18843b5117a92cec53aaa527f61efd59 (depoda değil, 1,4 MB). Gerekçe: binom kesikli
olduğu için ölçülebilir en küçük oran K ile tekdüze değişmiyor (0,001 adımla K 39: 0,715; 40: 0,699; 41: 0,706;
42: 0,691); katalogdaki tek olaylık bir güncelleme kapıyı keyfî açıp kapatırdı.

İsabet: sınanan sonraki olayın s işareti sessiz tarafın işaretine eşitse 1, değilse 0.

## 3. Hüküm satırı (tek)

Birim küme, X = isabet sayısı, kesin binom, K = 40.

- H1 (sessiz taraf): X ≥ 26 (tek yanlı, p = 0,5 altında olasılık 0,040).
- H0 (büyük etki yok): X ≤ 22 (p = 0,70 altında olasılık 0,032).
- X 23–25: ayırt edilemez.

Güç kapısı: K ≥ 30 ve ölçülebilir en küçük isabet oranı (güç 0,80) ≤ 0,70. Sayımda K 40, oran 0,699: kapı sınırda
geçti. Eşikte geçişin nedeni binomun kesikliliğidir: kesin testin gerçek büyüklüğü K = 40'ta 0,040, K = 39'da
0,027; kesiklilik olmasaydı oran K 39–41 için ≈ 0,69 olurdu. Kapı eşiği sayımla aynı commit'te (d7a4e84) yazıldı;
taraf bilgisi taşımadığı için körlüğü bozmaz, ama "sayımdan önce konmuş" sayılmaz.

Önceden hesaplanan hüküm olasılıkları:

| Gerçek isabet oranı | H1 | Ayırt edilemez | H0 |
|---|---|---|---|
| 0,50 | 0,04 | 0,18 | 0,78 |
| 0,60 | 0,32 | 0,37 | 0,31 |
| 0,65 | 0,57 | 0,31 | 0,12 |
| 0,70 | 0,81 | 0,16 | 0,03 |

Bu sınav yalnız büyük etkiyi (≈ 0,70) görür. "Ayırt edilemez" küçük etkinin yokluğu demek değildir; H0 yalnız
"0,70 ve üstü yok" demektir.

Yorum kuralları (hükmü değiştirmez, adını niteler):

- "Yön bilgi taşımaz" durumunda isabet olasılığı tam 0,5 olmayabilir. Bir yanda daha etkin bir yapı varsa o yan hem
  30 günde daha çok M ≥ 4, hem 15 yılda daha çok M ≥ 6 üretir; çift ya da öncü durumları ve büyük bir ana şokun
  gölgesi de aynı yöne iter. Bu kayma büyük olasılıkla artçısı çok tarafa doğrudur (H1'e karşı). Bunu §5.8'deki
  zaman ters çevrimi ölçer.
- Hüküm H1 ise ve zaman ters çevrimi de p = 0,5'i üst kuyrukta α 0,05 ile reddediyorsa, hüküm "H1, sıraya özgü
  değil, statik geometriyle ayırt edilemez" diye yazılır ve §8'e hiçbir şey taşınmaz.
- Hüküm H0 ise ya da ters yön notu (§5.6) düşüldüyse ve zaman ters çevrimi alt kuyrukta p = 0,5'i reddediyorsa,
  sonuç "arka plan asimetrisiyle ayırt edilemez" diye yazılır; ETAS lehine okunmaz.
- Hükmün adı "sessiz taraf"tır. "Kırılmamış komşu kesim" yorumu ancak (i) §5.1'de isabet oranı u/L medyanının
  altında ve üstünde ikisinde de 0,5'ten büyükse ve (ii) §5.2'deki ağırlık merkezi tanımında X/K ≥ 0,6 ise yazılır.
  Aksi halde H1 "dış merkezin arkası" diye yazılır ve kırılma yönüyle ayırt edilemez sayılır. Kutular dış merkeze
  bağlıdır; tek yönlü kırılmada artçısı çok taraf kırığın ilerlediği yandır.

## 4. İkincil satır: ETAS yönüne karşı (önceden "büyük olasılıkla ayırt edilemez")

Üç modelin küme başına Bernoulli log skoru (nat):

- Taban: p = 0,5.
- Boşluk modeli: P(isabet) = 0,65, sabit.
- ETAS yönü: p_i = R_sessiz / (R_sessiz + R_yoğun), sonra [0,05, 0,95] aralığına kırpılır. Arka plan terimi
  yoktur: simetrik bir arka plan yalnız p_i'yi 0,5'e çeker, bilinçli olarak eklenmez.
  - j kümesi: birincil ve 30 günlük artçı bulutu. Bulut, doğrultu hesabına giren kümenin tamamıdır:
    (t0, t0 + 30 gün], dış merkezden ≤ 3 L, M ≥ 4, M < Mw; |s| < 5 km olanlar dahildir.
  - R_taraf = Σ_j 10^(1,0·(M_j − 4)) · Σ_hücre (r_jh² + c_j²)^(−1,5) · 4 km².
  - c_j = max(5 km, 0,5·L(M_j)), L Wells–Coppersmith. Birincil için M_j = Mw. Birincil dış merkezde nokta kaynaktır,
    iki yana simetrik katkı verir; yalnız seyreltir.
  - Koordinatlar: birincilin dış merkezine göre `eksen_bilesen` ile (s, d) km. j olayları da aynı fonksiyonla aynı
    düzleme taşınır; r_jh bu düzlemde Öklid uzaklığıdır.
  - Hücre merkezleri: |s| = 0,5 L + 1 + 2k km (k = 0, 1, …) ve d = −D + 1 + 2m km (m = 0, 1, …), D = max(L, 30 km);
    merkezi kutunun (0,5 L ≤ |s| ≤ 5 L, |d| ≤ D) içinde kalan hücreler alınır.
  - Zaman çekirdeği kullanılmaz; j'ler arasındaki zaman farkı ihmal edilir. Sonraki olayın büyüklüğü oranda
    sadeleşir.
  - Parametreler (üs 1,5; verim üssü 1,0, log10 tabanında; c_j kuralı) seçilmiştir, uydurulmamıştır; Zhuang–Ogata
    tipi çekirdeklerle aynı mertebededir.
  - p_i değerleri isabet kodu çalışmadan önce `kayit/turetme/tr2/tr2_etas_p.csv` dosyasına (küme, birincil id, p_i)
    yazılır ve commit edilir.

Satırlar: boşluk − taban, ETAS − taban, boşluk − ETAS; küme bootstrap'i 10 000 yineleme, tohum 20261111, %95
yüzdelik aralık.

Öncelik: karar yalnız §3'ün binom satırıyla verilir. Boşluk − taban farkı X'in tekdüze bir dönüşümüdür; K = 40'ta
bootstrap aralığı yalnız X ≥ 30 iken sıfırı dışlar (inceleyici önceden hesapladı). X 26–29 aralığında "H1, log skor
aralığı sıfırı içeriyor" diye birlikte yazılır; bu H1'i zayıflatmaz ve güçlendirmez. "Aralık sıfırı içermiyor"
okuması yalnız ETAS'lı iki satır için yorum taşır ve §3'teki arka plan kuralına tabidir.

## 5. Bilgi satırları (hükmü değiştirmez)

1. Dış merkezin artçı ağırlık merkezine doğrultu boyunca uzaklığı u/L. İsabet oranı u/L medyanının altı ve üstü
   için ayrı yazılır.
2. Merkez olarak dış merkez yerine artçı ağırlık merkezini kullanan tanımla X ve K.
3. Zayıf düzlem seçimi (düğüm düzlemi ile artçı ekseni arası > 30°) olan ve olmayan kümelerde X.
4. Sonraki olay adayı ≥ 3 olan ve olmayan kümelerde X.
5. Daha büyük bir olayın gölgesindeki birinciller (1 yıl, 3 L_büyük) dışlanınca X ve K.
6. Ters yön: X ≤ 14 ise "artçısı çok taraf lehine" notu düşülür; §3'teki arka plan kuralına tabidir.
7. Türkiye: kutuda tek küme (1999 Düzce). Sonucu yalnız anılır; hiçbir Marmara cümlesine dayanak olmaz.
8. Negatif kontrol, zaman ters çevrimi: aynı 40 küme, aynı birincil, aynı doğrultu, aynı sessiz taraf, aynı kutu.
   "Önceki olay": aynı havuzdan, [max(t0 − 15 yıl, 1976-01-01), t0 − 30 gün) aralığında kutuya düşen olayların
   zamanca en sonuncusu. İsabet_ters: önceki olayın s işareti sessiz tarafın işaretine eşitse 1. K_ters, X_ters ve
   p = 0,5'e karşı tek yanlı kesin binom üst ve alt kuyruk olasılıkları yazılır. Aynı koşuda, aynı kodla hesaplanır.
9. Çift ya da öncü: birincilden sonraki 30 gün içinde, 3 L içinde M ≥ Mw olayı olan kümeler (sayımda 6/40)
   çıkarılınca X ve K.
10. Alt gruplarda isabet oranı: ilk sonraki olay |s|/L ≤ 1 (6/40); sonraki olayın büyüklüğü ≥ Mw (10/40); sonraki
    olayın kendisi doğrultu atımlı bir birincil (14/40).

## 6. Koşu sırası ve körlük

1. Bu ön kayıt dondurulur, commit + push edilir.
2. İsabet öncesi manifest: `kayit/turetme/tr2/tr2_manifest.csv` üretilir ve commit edilir. Satır başına: küme,
   birincil id, t0, Mw, L, stk, sessiz tarafın işareti (yalnız artçılardan gelir), n+ + n−, |A|, ilk sonraki olayın
   id'si, |s|/L, |d|, aday sayısı, ilk önceki olayın id'si (§5.8). Manifest sonraki ve önceki olayın s işaretini
   İÇERMEZ. Yanında, açılmış anlık görüntüdeki her dosyanın sha256 listesi (`tr2_ham_sha256.txt`) commit edilir;
   koşu kodu listeyi doğrular. Manifest K = 40 vermezse sınav koşulmaz, kayıt "anlık görüntüden yeniden
   üretilemedi" diye kapanır, yeni ComCat sorgusu yapılmaz.
3. ETAS p_i dosyası üretilir ve commit edilir.
4. İsabet kodu yazılır; yalnız manifestteki id'leri, stk'yi ve dış merkezi kullanır. Yalnız yapay katalogla
   (işareti bilinen uydurma olaylar) sınanır. Kod incelemesi gerçek isabet çıktısı üretilmeden yapılır.
5. Tek koşu. Çıktı ne olursa olsun yazılır. Koşudan sonra tanım, eşik, manifest ya da küme kuralı değişmez.
   Koşu bir istisnayla durursa yalnız istisnanın doğrudan nedeni düzeltilir ve fark kayda geçer. Herhangi bir isabet
   ya da X değeri görüldükten sonra yapılan her kod değişikliği "koşu sonrası değişiklik" başlığında yazılır.

Bugüne dek sonraki olayın tarafı hiçbir kodda hesaplanmadı. Yazar birkaç olayı (1999 İzmit–Düzce, 2025 Marmara)
literatürden tanıyor; tanımlar sayım ajanınca taraf bilgisi olmadan seçildi ve burada değiştirilmedi.

## 7. Sınırlar

- "Aynı fay" geometrik bir vekildir; sonraki olayın mekanizması sınanmaz.
- Küresel M ≥ 4 tamlığı ağ geometrisine bağlıdır; asimetrinin bir bölümü örnekleme olabilir.
- 49 nitelikli birincilin 40'ı 2000–2019 arasındadır; 19'unun izleme süresi 15 yıldan kısadır.
- Aynı levha sınırındaki kümeler arası zayıf bağımlılık modellenmez.
- Kapı yalnız ana tanımla ve sınırda geçiyor; altı varyantın üçünde kapanıyor. Ana tanım varyant sayımlarıyla aynı
  commit'te (d7a4e84) yazıldı; varyant sayıları ana tanım seçilmeden önce görülmüş olabilir. Seçim taraf bilgisi
  olmadan yapıldı. Kapıyı geçen başka varyantlar da vardı ve ana tanım bunların K'si en büyük olanı değil.

## 8. İstanbul'a bağ

H1 çıkarsa ve §3'teki "kırılmamış komşu kesim" koşulları ile zaman ters çevrimi koşulu sağlanırsa, ileri test
defterine bir rakip terim aday olarak girer. Terim yalnız oran olarak cevap verir: "sıradaki M ≥ 6 hangi yanda daha
olası". Mutlak olasılık yazılmaz.

- Marmara 2025 bu sınavın tanımıyla (ComCat M ≥ 4) ölçülemiyor: yalnız 6 yanlı artçısı var. Yerel, düşük eşikli
  bir katalogla hesaplanacak asimetri farklı bir tanımdır. Aktarım ayrı bir doğrulama ister: aynı küresel olaylarda
  ComCat M ≥ 4 ile yerel katalogdan elde edilen sessiz tarafın uyuşma oranı.
- Bu doğrulama yapılmadan Marmara'ya yalnız "küresel örneklemde artçısı az taraf lehine bir eğilim var" cümlesi
  taşınır.
- H0 ya da ayırt edilemez çıkarsa Marmara'ya hiçbir şey taşınmaz.
- Bu sınav zaman eksenini daraltmaz; yalnız uzamsal eksene dokunur.

## 9. Yeniden açma şartı

Kapanırsa: (a) küresel M ≥ 3,5 tamlığı olan bir katalogla K ≥ 80 elde edilirse, ya da (b) kırılma yönü (yayımlanmış
sonlu fay modelleri) en az 30 kümede bilinir ve sessiz taraf kırılma yönünden ayrıştırılabilirse.
