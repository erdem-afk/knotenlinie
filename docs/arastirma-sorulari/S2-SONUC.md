# S2 sonucu: Türkiye segment tahminlerinin 2016–2025 karnesi (10 Kasım 2026)

Kural: `S2-KURAL.md` (sha `14f3ab55…`, OTS, commit f7baa9d). Tek koşu, 10 Kasım 17:45 UTC. Hedef kataloğu ComCat 2016–2025 M≥6 (sha `983859c1aa2a0d2e82eb4eb293ba98076b9ca5b1d2672081feecc8ae11ffd2e3`, 25 satır, son olay 2025-10-27; 2026 sorgulanmadı). 0 €. Nihai Marmara modeli v1.3b değişmedi.

## Kısa cevap

**Karne yazılamadı; yazılabilen kısmı hiçbir şeyi ayırt etmiyor.** Açık erişimle okunabilen 1997–2015 sayısal Türkiye segment tahminlerinin hepsi Marmara M≥7 içindi (Parsons 2000, 2004) ve Marmara'da 2016–2025'te M7 olmadı. 2016–2025'in 12 ana şokunun **hiçbiri** için kendi büyüklük eşiğinde sayısal bir literatür olasılığı elimizde yok. Olayların olduğu yerlerin tahminleri (Doğu Anadolu: Nalbant 2002, Bayrak 2015; Batı Türkiye: Paradisopoulou 2010) kapalı erişimde kaldı. Yan satırda, aynı ailenin açık girdisi EDSF13 ile kurulan fay Poisson'u M6'ların yerini düzleştirilmiş sismisiteden iyi bilmedi (+0,02 ± 0,19 nat).

## Hedefler (Türkiye + 25 km, M≥6, GK ana şokları, N = 12)

Kos/Bodrum 2017 M6,6; Elazığ (Doğanyol) 2020 M6,7; Özalp 2020 M6,0; Sisam 2020 M7,0; Düzce 2022 M6,1; Pazarcık 2023 M7,8; Çelikhan 2023 M6,0; Göksun 2023 M6,0; Hatay 2023 M6,3; Doğanyol 2024 M6,0; Marmara 2025 M6,2; Sındırgı 2025 M6,1. GK pencereleri Elbistan M7,5'i ve Nurdağı M6,7'yi Pazarcık'ın artçısı saydı; Çelikhan, Göksun ve Hatay 6 Şubat kırığının parçası ya da artçısı olduğu halde merkez üssü 89 km penceresinin dışında kaldığı için ana şok sayıldı (kurala göre; 2023 hariç satırı aşağıda). Sındırgı Ekim 2025 M6,0 artçı sayıldı.

## L1 (hüküm, önceden "ayırt edilemez"): literatür, Marmara M≥7

Olay yok (kutu içinde M≥6 tek olay: 23 Nisan 2025 M6,2). Her satırın olaysızlığa verdiği log olabilirlik:

| Satır | Aile | pW (2016–2025) | ln(1 − pW) |
|---|---|---:|---:|
| Parsons 2000 birleşik, etkileşimli | yenilenme + Coulomb | 0,253 | −0,291 |
| Parsons 2000 birleşik, arka plan | yenilenme | 0,202 | −0,225 |
| Parsons 2000 Poisson (%15–25 orta) | Poisson | 0,072 | −0,074 |
| Parsons 2004 bölge, + aktarım | yenilenme + Coulomb | 0,223 | −0,252 |
| Parsons 2004 bölge, zamana bağlı | yenilenme | 0,176 | −0,193 |
| Parsons 2004 bölge Poisson | Poisson | 0,147 | −0,159 |
| Parsons 2004 İstanbul, + aktarım | yenilenme + Coulomb | 0,161 | −0,176 |
| Parsons 2004 İstanbul Poisson | Poisson | 0,076 | −0,079 |

- Coulomb katkısı (aynı makalede etkileşimli − arka plan): −0,066 (2000), −0,058 (2004) nat.
- Zaman bağımlılığı katkısı (yenilenme − Poisson): −0,151 (2000), −0,034 (2004) nat.
- **Okuma:** işaret v1.3b'nin seçimleriyle aynı yönde (Poisson 0,95; Coulomb kapalı 0,73), ama büyüklük tek bir ikili gözlemden geliyor: en yüksek tahmin (%25) bile kendi altında %75 olasılıkla olaysız bir on yıl bekliyordu. Bu bir kanıt değil, yalnız işaret. R1 kıyası bilgi değeri taşımıyor (R1 N testinde başarısız, aşağıda); R1 satırı depoya yazılmadı.

## L2 (bilgi): Hubert-Ferrari 2000 Coulomb bayrağı

Bayrak bölgesinin R1 ağırlıklı alarm payı τ 0,043; 12 ana şoktan 1'i içinde (Marmara 2025 M6,2). p = 0,41, anlamsız. Bayrak İzmit büyüklüğünde (M≈7,4) olaylar içindi; M6,2 onun hedefi değildi.

## K (bilgi): kapsam

| Bölge | Ana şok | Açık sayısal literatür | Erişilemeyen |
|---|---:|---|---|
| Marmara | 1 (2025 M6,2) | var, ama M≥7 için | Pondard 2007 |
| Düzce (1999 kırığının batı ucu) | 1 | yok (Stein 1997 okunamadı, İzmit/Düzce 1999'da kırıldı) | — |
| Doğu Anadolu Fayı | 6 (Elazığ 2020, 2023 ×4, Doğanyol 2024) | yok | Nalbant 2002, Bayrak 2015 |
| Batı Türkiye ve Ege | 3 (Kos 2017, Sisam 2020, Sındırgı 2025) | yok | Paradisopoulou 2010 |
| İran sınırı | 1 (Özalp 2020) | yok | — |

Kendi eşiğinde sayısal olasılığı olan olay: 0/12. Bölge düzeyinde dokunan: 1/12. Erişilemeyen çalışmalar 9/12 olayın bölgesini hedefliyor. Karnenin asıl eksiği budur.

## B1 (hüküm 2): EDSF13 fay Poisson'u − düzleştirilmiş sismisite, şekil

| Satır | N | IG ± SE (nat) | z | Hüküm |
|---|---:|---|---:|---|
| **B1 R2 (şekil, toplam R1'e eşit) − R1** | 12 | **+0,021 ± 0,194** | 0,11 | **ayırt edilemez** |
| B1b karışım 0,5/0,5 − R1 | 12 | +0,062 ± 0,100 | 0,62 | ayırt edilemez |
| B1c 2023 hariç | 8 | +0,014 ± 0,272 | 0,05 | ayırt edilemez |
| B1d kümesizleştirmesiz | 15 | −0,000 ± 0,169 | 0,00 | ayırt edilemez |
| B1k ham (moment dengeli) R2 − R1 | 12 | −0,894 ± 0,198 | −4,52 | rakip önde (toplam teriminden) |

- Olay başı log oranlar −1,34 (Sisam) ile +1,43 (Düzce) arasında; fay haritası Düzce, Çelikhan, Kos ve Marmara'da önde; Sisam, Elazığ, Pazarcık ve Doğanyol'da geride.
- Gerçek SE (0,19) kuru koşu tahmininden (0,6–0,8) küçük çıktı; gerçek MDE ≈ 0,32 nat. Yine de v1.2'nin +0,42'lik uzamsal kazancı büyüklüğündeki bir farkı ancak sınırda görebilirdi; görülen fark sıfıra yakın.
- **Tutarlılık (N testi, bilgi):** R1 10 yılda 3,08 M6 bekledi, 12 geldi (P(X ≥ 12) ≈ 9·10⁻⁵; 2023 hariç 8, P ≈ 0,014). Ham R2 46,7 bekledi (P(X ≤ 12) ≈ 2·10⁻⁹). İkisi de başarısız: ComCat M5'ten b = 1 ile M6'ya çıkmak Türkiye'de oranı düşük veriyor, tam kenetlenmeli moment dengesi ise ≈4 kat yüksek. (Sonradan görülen not, kural değil: iki toplamın geometrik ortalaması 12,0.)

## Ne öğrendik

1. Türkiye için yayımlanmış segment tahminlerinin 2016–2025'te puanlanabilen bir karnesi **açık literatürle çıkmıyor**. Puanlanabilen tek bölge Marmara ve orada M7 olmadığı için karne yalnız "yüksek tahminler küçük bir ceza aldı" diyor. Bu, Kagan–Jackson'ın boşluk sınavlarındaki sonuçla aynı yönde ama kanıt gücü yok.
2. 2016–2025 Türkiye M6'larının yerini fay kaynakları (EDSF13) düzleştirilmiş sismisiteden iyi bilmedi. Bu, v1.3b'nin uzamsal ekseninin kendisi değil (orada gerinim var, burada fay kayma hızı), ama aynı soruya (fiziksel şekil sismisiteye bir şey katar mı) Türkiye'nin kendi M6'larıyla verilen ilk cevap: "ek bilgi görülmedi, zarar da görülmedi" (karışım +0,06 ± 0,10).
3. Tutarlılık satırları Türkiye M6 sayısının ≤2015 sismisitesiyle ciddi düşük beklendiğini gösteriyor (12 gözlenen / 3,1 beklenen). Bu, M7 modelinin istatistik dalının oran belirsizliğiyle (İstanbul aralığının %12'si) ilgili bir uyarı; M6 sayısını tek on yılla düzeltmek doğru olmaz, ama bilgi olarak deftere girer.

## Sınırlar

- Kural kör değil (olaylar nitel olarak biliniyordu). Kuru koşu bilinen 2006–2015 verisiyle yapıldı ve B1'in şekil kıyası olmasına o karar verdirdi; bu karar 2016–2025 görülmeden donduruldu.
- Literatür derlemesi erişime bağlı. Doğu Anadolu ve Batı Türkiye tahminleri okunabilirse aynı kuralla EK satırı olarak eklenir; hüküm satırları değişmez.
- GK pencereleri 2023 gibi uzun kırıkları merkez üssünden ayıramıyor (Çelikhan, Göksun, Hatay); 2023 hariç ve kümeli satırlar aynı sonucu veriyor.
- Hücre oranları ve R1/R2'nin segment olasılıkları depoya ve panele yazılmadı.
