# S4 sonucu: tarihsel Marmara depremlerinin segment ataması

**Özet (10 Kasım 2026, ön kayıt DONDUR-s4-s7 sha 91506751…, OTS; tek koşu; 0 €)**
- Hüküm: **H0. Yöntem bugünkü açık veriyle segmentleri ayıramıyor; olasılığa yayılmaz, v1.9 kurulmaz.**
  v1.3b ve v1.5 değişmez; Parsons–Ambraseys farkı daraltılamadı. Sunucu adımı (v1.9, BF) gereksiz kaldı.
- K1 geçti: 1999 İzmit tüm 91 şiddet noktasıyla (İzmit hariç kalibrasyon) doğru kırığa ≈1,00 kütle
  (en olası PIF+IZG+IZE+SAK: bir segment batıya taşıyor).
- K2 kaldı: aynı 1999 depremi tarihsel olayların yer dağılımıyla (6–20 nokta) örneklenince doğru kütle
  ort. 0,44 (eşik ≥ 0,35), ama batıya yanlış kütle ort. 0,49 (eşik ≤ 0,25). 1766 yer dağılımlarında
  batıya yanlış 0,81–0,90, 1509'da 0,56 (1754'te 0,01). Yani 1509 ve 1766 yer ağları doğu kırığını batıya çekiyor.
  Kurala göre şiddet hiçbir tarihsel olayda kullanılmaz.
- K3 kaldı: 1912 yalnız türbidit + tsunami ile doğru kütle 0,24 (eşik 0,4; düzgün önsel 0,06).
  Türbidit + tsunami ortak sonsala girmez.
- K4 geçti (tutarlılık, −0,00).
- Aşağıdaki tarihsel olay sonsalları yalnız BİLGİ satırıdır; deftere ya da panele olasılık yazılmaz.

## Koşu

`python3 -I s4.py /mnt/project-files/marmara-girdiler/edsf13/DB-CFS-ESRI-shapefile.zip cikti`
Çıktı `cikti/sonuc.json` (kod sha256 içinde), günlük `kosu1.log`.

## SAPMA (hata düzeltmesi, koşudan önce)

1. Ön kayıt GAN için "TRCS290 + TRCS996" diyor. EDSF13'te TRCS290 kimliği 38° K'deki başka bir kaynağa
   ait (ilk geometri denetiminde SAK 2 311 km çıktı). Kuzey Ege "North NAT" kaynağı GRCS290'dır ve
   26,60'ın batısında; TRCS996 zaten 26,60'a uzanıyor. Yalnız TRCS996 kullanıldı.
2. IZG için ön kayıttaki düz bağlantı yerine EDSF'nin kendi TRCS012 izi (29,33–29,79) kullanıldı; IZG
   48,0 km (düz bağlantıyla ≈47 km).
3. Küme dışı adayın "deniz altı" sayılması, merkezin denizde olup olmadığıyla değil, merkezin bir deniz
   segmentine ≤ 10 km olup olmadığıyla belirlendi (beyan edilmemiş, incelemede bulundu). 1912 merkezi bu
   yüzden deniz sayıldı; kara sayılsa K3 0,238 → 0,245, kapı yine kalır. 1894 merkezi kara sayıldı;
   yalnız bilgi satırını etkiler.

1 ve 2, olabilirlik hesaplanmadan önce, yalnız segment uzunluk denetimiyle bulundu.

## Kalibrasyon (7 olay, eşit ağırlık)

IPE (tüm olaylar): a −3,31, b 2,02, c 2,98, σ 0,89, τ 0,70. İzmit hariç: a −3,32, b 2,08, c 3,23,
σ 0,73, τ 0,79. b önseli (1,5 ± 0,5) yukarı itildi; Mw aralığı dar (6,5–7,6) olduğundan a–b bağımlı.
h duyarlılığı: K1 h = 5 km 1,00, h = 15 km 1,00.

## Pozitif kontroller

| Kapı | Ölçü | Değer | Eşik | Sonuç |
|---|---|---|---|---|
| K1 1999 tüm nokta | doğru kütle | 1,00 | ≥ 0,5 | geçti |
| K2 1999 tarihsel geometri | doğru / batıya yanlış (ort.) | 0,44 / 0,49 | ≥ 0,35 / ≤ 0,25 | kaldı |
| K3 1912 türbidit + tsunami | doğru kütle | 0,24 (Armijo kümesiyle 0,46) | ≥ 0,4 | kaldı |
| K4 1999 ortak − şiddet | log fark | −0,00 | ≥ −0,1 | geçti |

K2 olay bazında (doğru / batıya yanlış): 1509 0,44/0,56; 1719 0,59/0,40; 1754 0,92/0,01;
1766-05 0,19/0,81; 1766-08 0,10/0,90; 1894 0,43/0,26.

Not: K1'deki ≈1,00 kütle aşırı güven işareti; noktalar arası bağımlılık (yer etkisi, ortak kaynak)
modelde yok. Bu, tarihsel olaylarda da sonsalların fazla keskin çıkacağı anlamına gelir.

## Tarihsel olaylar (yalnız bilgi; ateşleme kapıları kaldığı için kullanılmaz)

| Olay | Yalnız şiddet (en olası) | Ortak (en olası) | Küme dışı (ortak) |
|---|---|---|---|
| 1509 | küme dışı 0,32; CEN+KUM 0,24 | CEN+KUM 0,28; CEN+KUM+PIF 0,24 | 0,05 |
| 1719 | IZG+IZE 0,31; küme dışı 0,20 | IZG+IZE 0,31 | 0,21 |
| 1754 | IZE+SAK 0,30; IZE 0,18 | IZE+SAK 0,31 | 0,13 |
| 1766-05 | KUM+PIF+IZG 0,17; PIF+IZG 0,16 | KUM+PIF+IZG 0,17 | 0,00 |
| 1766-08 | GAN+TEK 0,62; GAN+TEK+CEN 0,22 | GAN+TEK 0,57 | 0,00 |
| 1894 | küme dışı 0,34; PIF 0,23 | PIF 0,32; KUM+PIF 0,26 | 0,04 |

K2 gösteriyor ki 1509 ve 1766 yer dağılımlarında şiddet doğu kırığını batıya taşıyor; bu yüzden 1509'un
CEN+KUM'a çıkması kanıt değildir. Segment düzeyinde düzgün olmayan önsel (KUM, PIF, IZG önsel marjinali
0,30–0,33; GAN, SAK 0,12) `cikti/sonuc.json` içinde.

## Eksik çıktılar

Sıralı bırakma tablosu ayrıca üretilmedi (bileşen satırları var); çıktı 2 (İstanbul önü son kırılma)
yayılım satırı olmadığı için yazılmadı. `sonuc.json`'daki "hukum" metninde "ortak yayilim" ifadesi
görünüş hatası; yayılım satırı null.

## Sonuç incelemesi

Bağımsız alt ajan: KABUL. Yeniden koşu birebir aynı `sonuc.json`; mvn_ll, Joyner–Boore, maskeler,
K2 örneklemesi, türbidit/tsunami formülleri doğru; K3'ün kalması yapısal (TB ve CiB gözlemleri GAN+TEK'i
TEK ve TEK+CEN'den ayıramıyor).

## Ne öğrendik

- Açık sayısal şiddet verisi (AHEAD UNITH003, olay başına 6–20 nokta, İstanbul ve kıyı kentlerinde
  kümeli) segment ölçeğinde (40–50 km) atama yapmaya yetmiyor; hata yönü batıya.
- Türbidit + tsunami kodlaması (literatür-koşullu, çoğu w = 0,3) 1912'yi bile eşik üstünde bulamıyor;
  havzaların çoğu birden çok segmente komşu.
- İlerlemek için gereken veri: Ambraseys (2009) ve Ambraseys ve Finkel (1991) şiddet tablolarının yer
  bazında sayısallaştırılması (daha çok ve daha dağınık nokta) ve tek tek radyonüklit/radyokarbon
  pencereleri yayımlanmış türbidit kayıtları. Bunlar olmadan bu soru kapanır.

## Defter

İleri test defterine bilgi satırı: "S4 tarihsel segment ataması: H0, K2 ve K3 kaldı, yayılım yok, v1.9
kurulmadı." Olasılık yazılmaz.
