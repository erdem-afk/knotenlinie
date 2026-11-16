# TR-13b ön kayıt: bağımsız inceleme 1

İncelenen: `TR-13b_sinirli-kosu_ONKAYIT.md` (TASLAK, 16 Kasım 2026) ve `kayit/turetme/tr13b/` (`tr13b_mde.py/.json`,
`tr13b_K.py/.json`). Dayanaklar: `ESIK-DAYANAGI.md`, `TR-13_SAYIM.md` (gövde ve Ek 1), `kayit/turetme/tr13/`
(`tr13_guc.py`, `tr13_tamsayim.json`). Taslak ve yazarın betikleri değiştirilmedi. Gerçek katalogda hiçbir V(q), Gini
ya da z hesaplanmadı; hiçbir katalog indirilmedi, ham arşiv açılmadı. Tek gerçek girdi `tr13_tamsayim.json`'daki
üstveri satırlarıdır (olay, küme, R, katalog, Mc, N3bg sayısı).

Bağımsız betik: `kayit/turetme/tr13b/inc1/tr13b_inc1.py` (`python3 -I -B`, numpy). ETAS üreteci, GK74 ve V(0,5)/z
ölçüsü `tr13_guc.py`'den çağrılır (yazarın ölçüsü sınansın diye); sınama düzeni, bozulma senaryoları ve özet bağımsız
yazıldı. Çıktılar:
- `tr13b_inc1_mde.json` (tohum 20261120, ≈ 3 dk): T1 MDE'si, K = 14, N3bg 50 ve 100 (sıfır havuzu 2000, her f 600).
- `tr13b_inc1.json` (tohum 20261118, sıfır 800 / bozulma 300) ve `tr13b_inc1_buyuk.json` (tohum 20261119, 3000 / 1500;
  ≈ 4 dk): T1'in ETAS dışı bozulmalar altındaki yanlış alarmı ve doyma denetimi.

## Hüküm

**DÜZELTMEYLE KABUL.** Sınama kesin tanımlı, kör, 0 € ve hızlı; ETAS'tan bölge başına kalibrasyon, TR-13'ün
%13–37'lik anma yanlış alarmını gerçekten çözüyor (ETAS içinde). Ama dört şey dondurmadan önce düzeltilmeli:
(1) 14 kümenin 3'ü iddianın **keşif örneklemidir** (Hector Mine, Ridgecrest, İzmit–Düzce bölgesi); (2) MDE iyimser
yazılmış ve örneklemin gerçek R'leriyle (58–426 km) hesaplanmamış; (3) çok olaylı kümelerin puanı ve dallanma kuralı
tanımsız ya da çelişkili; (4) ETAS'ta olmayan **durağan sürüler** ve **kenar ağ kaybı** yapayda T1'in yanlış alarmını
%10–18'e çıkarıyor, taslağın önerdiği tutucu dallanma ve LOO bunu kapatmıyor. Düzeltmelerle sonuç ya yorumlanabilir
bir "VAR" (keşif olayları dışında da tutan) ya da dürüst bir "ayırt edilemez (MDE f ≈ 0,3)" olur.

## A. Körlük, tek koşu ve kalan serbestlik

Kör ve sabit olan: örneklem (Ek 1 listesi, yeni olay yok), pencereler, ortak Mc, GK74, hücre 5 km, q 0,5, z tanımı,
yön (tek yanlı), T1 istatistiği, α, hüküm sırası. Gerçek z hesaplanmamış (TR-13 §9 ve Ek 1 beyanı; ben de
yapmadım). İyi.

Kalan serbestlik:
1. **Çok olaylı küme puanı tanımsız (Z3).** M ≥ 6,5 tol 0,3 satırında 16 olay 14 kümeye düşüyor: küme 397 =
   Superstition Hills 1987 + Hector Mine 1999, küme 1139 = Jamaika 2020 + Küba 2024. Taslak "K bölgenin ortalama z'si"
   diyor; küme z'sinin ne olduğu (üyelerin ortalaması mı, ilk olay mı) ve sıfır çekilişinin buna nasıl uyduğu yazılmalı.
   Öneri: küme z = üyelerin ortalaması; sıfırda her üyenin kendi havuzundan çekilip ortalanır.
2. **Dallanma kuralı çelişkili (Z4).** §6.1(a) "dallanma referans döneminden en çok olabilirlikle uydurulur ve eşik
   0,4 / 0,6 / 0,8'in en tutucusuyla alınır" diyor; §3 sabit 0,6 diyor; §7.3 ikisini birden istiyor. Uydurulan
   dallanma hiçbir yerde kullanılmıyor ama çıktıda görünecek. Tek kural: her bölge için 0,4 / 0,6 / 0,8 havuzları;
   "VAR" üçünde de p ≤ 0,05 ister; uydurma yalnız bilgi satırıdır (ya da hiç yapılmaz).
3. **Katalog kaynağı ve "eksik parça" (Ö1).** "Yeni indirme yalnız eksik parça varsa" açık uçlu. Hangi parçanın eksik
   sayılacağı (sha256 listesinde olmayan) ve indirilen parçanın hükme girip girmeyeceği önceden yazılmalı; en iyisi
   ham arşivde eksik olan olay "veri yok" sayılsın.
4. **Doyma kuralının uygulama ayrıntısı (Ö2).** 16 olayın 13'ünde N3bg > 100 (yalnız Ishigaki 58, Cook Boğazı 74,
   Darfield 100 değil); Mc neredeyse her bölgede yükselecek. Yükseltilmiş Mc'nin referansa da uygulandığı, adım
   sırasının (önce ortak Mc_b, sonra doyma) ve GK74'ün her adımda yeniden koşulduğu yazılmalı.
5. Sorunsuz bulduklarım: T3 binom eşiği (K = 14, p0 0,05 → 3 aşım, gerçek α 0,0301; yeniden hesaplandı), T2'nin
   2^14 = 16 384 deseni, kod denetimi tanımı (dal 2), "z̄ > 0 da ayırt edilemez" kuralı.

## B. Örneklem: keşif olayları (Z1)

Ana listede (`tr13_tamsayim.json`, M ≥ 6,5, referans tol 0,3) BZ20'nin ve EGU 2020 özetinin kendi olayları var:
**Hector Mine 1999** (küme 397), **Ridgecrest 2019** (küme 979) ve **İzmit 1999** (küme 395; BZ20 Düzce'yi, EGU 2020
İzmit–Düzce bölgesini inceliyor). İddia bu olaylarda görülerek kurulmuştur; onları içeren bir "VAR" bağımsız tekrar
değildir, yalnız yeniden üretimdir. Ölçü BZ20'nin aynısı olmadığı için yarım bir yeniden üretim bile değildir.

Düzeltme: "Büyük etki VAR" ayrıca bu üç küme dışarıdayken (K = 11) T1 p ≤ 0,05 ister. Bunun MDE bedeli yazarın K
tablosunda var: K = 11'de f 0,25 (N3bg 50), 0,33 (N3bg 100). Keşif kümeleri dışarıdaki satır, "VAR" cümlesinin
öznesi olur.

## C. MDE: yeniden hesap

**T1, K = 14, güç 0,8 (yazarla aynı üreteç ve ölçü, bağımsız sınama kodu ve tohum):**

| N3bg | f: 0 / 0,1 / 0,15 / 0,2 / 0,25 / 0,3 / 0,4 | MDE f (bu inceleme) | yazar (mde / K betiği) |
|---|---|---|---|
| 50 | 0,026 / 0,16 / 0,50 / 0,66 / 0,82 / 0,94 / 1,00 | **0,24** | 0,22 / 0,21 |
| 100 | 0,035 / 0,16 / 0,37 / 0,63 / 0,71 / 0,82 / 0,94 | **0,29** | 0,20 / 0,28 |

- Yazarın N3bg 100'deki 0,20'si Monte Carlo çıkıntısıdır (kendi tablosunda 0,2'de 0,81, 0,25'te 0,76). Üç bağımsız
  hesap 0,20 / 0,28 / 0,29 veriyor. Doyma kuralından sonra bölgelerin çoğu N3bg ≈ 80–100'de olacağı için **ana MDE N3bg
  100 satırıdır: f ≈ 0,28–0,29**, bant içi pay ≈ %8 → ≈ %16 (≈ 2 kat). Taslağın "f ≈ 0,20–0,28" başlığı "f ≈ 0,25–0,30"
  olmalı (Z2).
- **R uyuşmuyor (Z2).** Taslak §6.6 "gerçek R 50 ile ≈ 200 km" diyor; listede R 57,7–425,6 km (Chiniak 426, Jamaika
  320, İzmit 277, Gisborne 181). MDE yalnız R = 80 için hesaplandı. Bölge başına kalibrasyon α'yı korur, ama MDE
  büyük R'de farklıdır: 426 km dairede ≈ 22 800 hücre ve 100 olay varken V(0,5) neredeyse ayrık olaylarla belirlenir,
  kırık bandının payı alanla küçülür. Olumsuz hükmün cümlesi MDE'yi andığı için, **MDE listenin gerçek (R, N3bg)
  bileşimiyle** koşudan önce yapayda hesaplanmalı ve hüküm cümlesinde o sayı kullanılmalı.
- **×0,5 / ×2:** yazarın tablosu tutarlı (yarısı için K ≈ 60–80, iki katında güç ≈ 0,9–1,0).

## D. Yanlış alarm: ETAS kalibrasyonu gerçek katalogdaki bozulmaları tutar mı

Kalibrasyon: sinyalsiz ETAS (dallanma 0,6, pay_fay 0,6), N3bg ≈ 52, R 80, K = 14. Veri tarafına kalibrasyonun
bilmediği bozulmalar eklendi. Değerler iki bağımsız koşudan (sıfır havuzu 800 / 3000):

| Senaryo (veri) | T1 gerçek α | ort. z kayması (D0'a göre) |
|---|---|---|
| D0 aynı ayar | 0,053 / 0,071 | – |
| D1 durağan sürüler: yılda 0,4 sürü, her biri 15 olay, M 2,5–3,2, 3 km, 180 gün | **0,164 / 0,179** | −0,20 / −0,22 |
| D2 yalnız önce-pencerede tek sürü, bölgelerin %30'unda | 0,081 / 0,080 | +0,03 / −0,02 |
| D3 referans döneminde 20 km'lik bir dairede m < 3 olaylar %40 görülüyor (yerel ağ iyileşmesi) | 0,080 / 0,053 | ≈ 0 |
| D4 önce-pencerede bölge kenarında (x > 30 km) m < 3 olaylar %30 görülüyor (kenar ağ kaybı) | **0,113 / 0,100** | −0,16 / −0,12 |
| D5 arka plan yapısı farklı (pay_fay 0,9) | 0,038 / 0,032 | +0,1 / +0,18 |
| D7 verim üssü farklı (α = 0,8 ln10) | 0,029 / 0,092 | belirsiz |
| D6 doyma, eşleşik kalibrasyon (hedef 200 → gerçekleşen 143) | 0,027 / 0,037 | güç f = 0,3'te 0,30 / 0,36 |

Okuma:
- Tek koşudaki Monte Carlo saçılımı ±0,02–0,03 (D0 iki koşuda 0,053 ve 0,071). Bunun üstünde sağlam iki bulgu var:
  **durağan sürüler α'yı ≈ 3 katına (0,16–0,18), kenar ağ kaybı ≈ 2 katına (0,10–0,11) çıkarıyor.** İkisi de
  "yerelleşme" yönünde. Neden: 180 günlük sürüleri GK74 küme saymıyor (M 3,2'nin GK74 penceresi ≈ 15 gün); sürü
  bölgeye, ETAS'ın öngörmediği bir uzaysal yoğunlaşma ekliyor. Kenar kaybı ise dağınık olayları siliyor, kalanlar
  daha yoğun görünüyor. Sürünün etkisi (ort. z −0,2), aranan etkinin (f = 0,2'de ≈ −0,85; TR-13 §4.2: d −0,61 × sd 1,38) dörtte biri
  kadar.
- Bu iki bozulma tekdüze (her bölgeyi biraz iter); "z'si en küçük bölge dışarıda" şartı onları tutmaz. "En tutucu
  dallanma" da tutmaz: dallanma ETAS'ın içinde bir parametre, sürü ETAS'ın dışında.
- **Doyma kuralı:** taslağın gerekçesi ("kalibre eşikte bile α %21") yanlış etiketlenmiş. O sayı N3bg 100'e kalibre
  edilip 2 katı veriye uygulanınca çıkıyor, yani **uyuşmazlıktır**. Eşleşik kalibrasyonla doymuş bölgede α 0,03–0,04
  kalıyor. Doymanın asıl bedeli **güç**: f = 0,3'te 0,30–0,36 (N3bg 50'de 0,94). Kural yine doğru, gerekçesi "α"
  değil "güç" olarak düzeltilmeli (Ö3).

**Zorunlu düzeltme (Z5): ETAS dışı bozulmaya karşı yerinde denetim.** Bölgenin kendi geçmişi zaten taslakta (T2'nin
plasebo penceresi [t − 6, t − 3), referans [t − 10, t − 6)). Aynı pencere **T1'in kendi ETAS kalibrasyonuyla**
puanlanır (z_p'nin ETAS sıfırına göre ortalaması; bölge başına ayrı havuz, plasebo R ve N3bg'siyle). "VAR" ayrıca bu
plasebo T1'inin p > 0,20 olmasını ister; p ≤ 0,20 ise hüküm "ayırt edilemez (ETAS uyumsuzluğu)" olur. Bu, sürü ve ağ
gibi durağan bozulmaları, sinyal penceresine dokunmadan, aynı bölgede yakalar. Sınırı: EGU 2023'ün "2–10 yıl önce
etkinleşme" sinyali plasebo penceresine düşerse z_p'yi yayılma yönüne iter ve denetimi gevşetir; bu yön tutucu değil,
bilgi satırında yazılmalı. Ayrıca yapayda D1 ve D4 ile bu denetimin yanlış "VAR"ı ne kadar kestiği koşudan önce
ölçülüp ön kayda yazılmalı.

## E. Ölçü BZ20'nin aynısı değil: olumsuz sonuç neyi dışlar

Dışlar: bu ölçüyle (dış merkezli R = max(2L, 50 km) daire, 5 km hücre, V(0,5), GK74, referans alt örneklemeli z) ve
ETAS sıfırına göre, ≈ 0,3 kesirlik bir arka plan göçünün (bant içi payın ≈ 2 katına çıkması) bu 11–14 bölgede olağan
olmadığını. Dışlamaz: BZ20'nin kendi ölçüsünü (voksel, en yakın komşu kümesizleştirmesi, seçimsiz bölgesel ızgara,
yeniden karıştırılmış katalog anlamlılığı), dış merkezi içermeyen yerelleşmeyi, daha küçük etkiyi ve "sönme"yi.
Taslağın §8'i bunu doğru yazıyor; tek ek: keşif olayları (B) dışarıda kalınca "BZ20'nin olaylarında" hiçbir şey
söylenmez, yalnız "başka olaylarda" söylenir. Hüküm cümlesi buna göre kurulmalı.

## F. Bilimsel değer

- Etki büyüklüğünün kaynağı yok (BZ20 tam metni okunamadı); kuram nicel değer vermiyor. Bu yüzden "MDE kuramın çok
  üstünde mi" sorusu TR-1b'deki gibi yanıtlanamıyor: ne kadar üstünde olduğu bilinmiyor. MDE fiziksel olarak abartılı
  değil (3 yılda bant payının iki katına çıkması), ama "büyük".
- Koşmaya değer, çünkü maliyeti ≈ 0 (ham arşiv ve kod hazır, benzetim dakikalar), sınama kesin ve olası iki sonucun da
  önceden yazılmış bir anlamı var. En olası sonuç "ayırt edilemez (MDE f ≈ 0,3)"tır ve bu önceden kabul edilmeli.
- Değeri artıran tek şey BZ20 tam metninin meşru okunmasıdır (yeniden açma (a)). Okunmadan dondurulursa sonuç
  BZ20'yi ne doğrular ne çürütür; yalnız "bu ölçüde büyük bir yerelleşme olağan değil" der.

## Zorunlu düzeltmeler (dondurmadan önce)

- **Z1.** "Büyük etki VAR", keşif kümeleri (397 Hector Mine/Superstition Hills, 979 Ridgecrest, 395 İzmit) dışarıdayken
  de T1 p ≤ 0,05 ister; hüküm cümlesinin öznesi bu K = 11 satırıdır.
- **Z2.** MDE başlığı "f ≈ 0,25–0,30" (ana satır N3bg 100) olarak düzeltilir; listenin gerçek (R, N3bg) bileşimiyle
  yapay MDE koşudan önce hesaplanır ve dal 4'ün cümlesi o sayıyı kullanır. §6.6'daki "R 50–200 km" "58–426 km" olur.
- **Z3.** Çok olaylı küme puanı tanımlanır (üyelerin z ortalaması; sıfırda üyelerin kendi havuzlarından ortalama).
- **Z4.** Dallanma için tek kural: bölge başına 0,4 / 0,6 / 0,8 havuzları, "VAR" üçünde de p ≤ 0,05; en çok
  olabilirlik uydurması kaldırılır ya da bilgi satırı olur.
- **Z5.** ETAS uyumsuzluk denetimi: plasebo penceresinin T1'i (ETAS sıfırına göre) p > 0,20 değilse hüküm "ayırt
  edilemez (ETAS uyumsuzluğu)". Denetimin yapay sürü/ağ senaryolarındaki etkisi koşudan önce ön kayda yazılır.

Öneriler: Ö1 eksik parça kuralı; Ö2 doyma adımlarının sırası; Ö3 doyma kuralının gerekçesi "güç" olarak; Ö4 bölge
başına kalibrasyon havuzu ≥ 2000 (taslakta yazılı) ve Monte Carlo hatasının p'ye etkisi (benim tek havuzlu
denetimimde ±0,02–0,03) raporda yazılsın.

## Yeniden üretim

```
cd kayit/turetme/tr13b/inc1
python3 -I -B tr13b_inc1.py tr13b_inc1_mde.json mde
python3 -I -B tr13b_inc1.py tr13b_inc1.json tam
python3 -I -B tr13b_inc1.py tr13b_inc1_buyuk.json buyuk
```
Sınırlar: bütün sayılar R = 80 km yapay bölgede; sürü ve ağ senaryolarının yoğunluğu benim seçimimdir (gerçek
bölgelerdeki sıklıkları ölçülmedi); D7'nin iki koşusu tutarsız (0,029 / 0,092), sonuç çıkarılmadı.
