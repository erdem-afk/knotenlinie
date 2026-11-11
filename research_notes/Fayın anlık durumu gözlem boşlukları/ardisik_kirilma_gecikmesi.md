# Ardışık kırılma gecikmesi: komşu segmentin "kaç yıl sonra" kırıldığı ve tahmin sınama boşluğu (Marmara / KAF)

Kapsam: doğrultu atımlı sistemlerde bir segment büyük depremle kırıldıktan sonra bitişik segmentin kırılma gecikmesi dağılımı; bu dağılımdan zamana bağlı tehlike eğrisi çıkarılıp Poisson/ETAS'a karşı puanlanmış mı; 0 € sınama taslağı ve kaba güç. Tarih: 11 Kasım 2026. Katalog sorguları bitişi 2025-12-31. Mutlak İstanbul olasılığı yazılmadı; yalnız oran ve nat.

Defter araması (kayit.py: göç, Coulomb, koşullu, BPT, sıçrama, gecikme, komşu, ETAS) yapıldı. "gecikme" ve "komşu" için defterde kayıt yok. En yakın kayıtlar: DK-3 (M6 sonrası koşullu M7, H0), VE-2 (viskoelastik ΔCFS sıralaması, aday), VE-4 (DeVries eşik saati, güç yok), TK-E5 (M>5 doğuya göç, N yok), M7-D1D4 (Coulomb −0,02/−0,40), ZAMAN-BPT (−171,8 nat), FA-1 (olay geçmişine koşullamanın tavanı ≈ +0,016 nat / 10 yıl penceresi, H0), EL-4 (sismik boşluk).

Köprü ölçüm dosyaları: `/home/user/knotenlinie/kayit/turetme/kopru/gecikme/tohumlar.json`, `kopru_rapor.json`. Sayım betikleri ve doğrultu atımlı olay kimlikleri aynı dizinde: `cift.py`, `oran.py`, `mek.py`, `ss_ids.json`.

## 1. Literatürde komşu segment kırılma gecikmesi derlenmiş mi; dağılımın biçimi, medyanı, kuyruğu

### Takeaway
Sayısal gecikme dağılımı veren küresel çalışma yalnız birkaç tane: Parsons 2002 (Ms≥7 sonrası kayma gerilmesi artan düzlemlerde Omori bozunması, yaklaşık 7–11 yıl sürüyor) ve Kagan & Jackson 1999 (Mw≥7,5 çiftlerinin aralıkları üstel/periyodik değil, kuvvet yasası). KAF 1939–1992 için Stein-Barka-Dieterich 1997 ortalama ~10 yıl gecikme veriyor. "Doğrultu atımlı, bitişik segment, M7→M7" diye süzülmüş, medyanı ve kuyruğu verilmiş bir küresel gecikme dağılımı bulunamadı. Kendi kaba sayımımda (ComCat, M≥7 doğrultu atımlı birincil, 1976–2025) komşu banttaki oran yükselmesi ilk ay dışında küçük (1–3 yıl ≈1,7×, 3–10 yıl ≈0,9×, 10–30 yıl ≈1,2×) ve taban belirsiz.

### Cited Findings
- Stein, Barka & Dieterich 1997 (GJI, 10.1111/j.1365-246x.1997.tb05321.x): KAF'ta 1939–1992 arasında 10 adet M≥6,7 deprem ~1000 km'yi kırdı. 10 kırığın 9'u önceki depremlerle 1–10 bar (3–30 yıllık seküler yüklenme karşılığı) kırılmaya yaklaştırılmış. Tetikleyen ile tetiklenen arasındaki ortalama süre 10 yıl. Kırılmadan sonraki on yılda olasılık kazancı ortalama 3 kat (model hesabı; puanlanmış sınav değil). — [OpenAlex özet](https://doi.org/10.1111/j.1365-246x.1997.tb05321.x)
- Parsons 2002 (JGR, 10.1029/2001jb000646): Harvard CMT'de Ms≥7 olaylar dislokasyon olarak modellendi. |Δτ|≥0,01 MPa olan komşu olayların ~%61'i kayma gerilmesi artışına, ~%39'u azalmasına denk geliyor. Artışla ilişkili olaylar katalogun en az %8'i. Bu olaylar küresel olarak "~7–11 yıl süren" Omori bozunmasına uyuyor ve ana şok merkezinden 240 km'ye kadar arka plandan yüksek oranda görülüyor. El Salvador 2001 örneğinde küresel istatistiğin Coulomb'dan daha iyi hızlı kestirim verdiği öne sürülüyor. Bu tek örnek; çok olaylı log skor sınavı yapılmamış. — [OpenAlex özet](https://doi.org/10.1029/2001jb000646)
- Kagan & Jackson 1999 (BSSA, 10.1785/bssa0890051147): Harvard katalogunda merkezleri 100 km'den yakın tüm Mw≥7,5 sığ çiftleri incelendi. Çiftlerin çoğunun odak mekanizması benzer, kırık alanları kesişiyor. Aralıklar levha hareketinin yeniden biriktirmesi için gereken süreden çok kısa. Yarı periyodik model ve sismik boşluk hipoteziyle çelişiyor; kuvvet yasası yinelenme çok daha iyi uyuyor. — [OpenAlex özet](https://doi.org/10.1785/bssa0890051147)
- Scholz 2010 (BSSA, 10.1785/0120090309): Tetikleme gecikmeleri ve Coulomb aktarımı (gerilme düşümünün 10⁻²–10⁻³'ü) doğal yinelenme süresine göre küçük. Paleosismik veriler, uzun sessizliklerle ayrılmış küme hâlinde çok faylı kırılmalar gösteriyor. Model "bulanık senkron". Sayısal gecikme dağılımı yok; nitel ve kavramsal. — [OpenAlex özet / açık erişim](https://doi.org/10.7916/d8qv3mmt)
- Pondard ve ark. 2007 (GJI, 10.1111/j.1365-246x.2007.03580.x): KAF–Marmara'da ~500 yıl (iki döngü) için M≥7 kayıtları kullanıldı. "Yayılan diziler her döngüde olmuyor". 1894 ve 1912 yalıtılmış olaylar. 20. yüzyıl dizisi Marmara'yı bir dizi olarak geçmedi. Orta Marmara'daki ~70 km'lik segmentte bugünkü yüklenme özellikle yüksek. 18. yüzyıl kümesi için batıya yayılan senaryolar tarihsel veriyle uyumlu. — [OpenAlex özet](https://doi.org/10.1111/j.1365-246x.2007.03580.x)
- Dolan, Bowman & Sammis 2007 (Geology, 10.1130/g23789a.1): Güney Kaliforniya'da uzun menzilli ve uzun süreli fay etkileşimi (küme/sessizlik dönemleri). OpenAlex özeti boş geldi; sayısal içerik doğrulanmadı. — [künye](https://doi.org/10.1130/g23789a.1)
- Philibosian & Meltzner 2020 (QSR, 10.1016/j.quascirev.2020.106390): Dünya fayları için kırılma deseni katalogu. Dört sınıf: yarı periyodik benzer kırılmalar, kümeli benzer kırılmalar, kümeli tamamlayıcı kırılmalar / kırılma kaskadları, üst üste binmiş döngüler. Engeller kalıcı, sık aşılan veya geçici. Bu, ardışık kırılmalar için en kapsamlı nitel derleme; sayısal gecikme dağılımı özetinde yok. — [OpenAlex özet](https://doi.org/10.1016/j.quascirev.2020.106390)
- Pinzón ve ark. 2024 (JGR, 10.1029/2024jb028912), Altın Dağ (Altyn Tagh) Fayı: Aksay bölümünde ortalama yinelenme 1329 ± 588 yıl (COV ~0,44). Komşu bölümlerle senkron kırılmalar var. "Patlamalı" dönemlerde olaylar arası ortalama 475 ± 108 yıl, aralarında 1,1–1,6 bin yıllık sessizlikler. Komşu kırılma ölçeği yüzyıllar, yıl değil. — [OpenAlex özet](https://doi.org/10.1029/2024jb028912)
- Doğu Anadolu: 24 Ocak 2020 Sivrice (Mw6,8) Pütürge segmentinde oldu, 6 Şubat 2023 Kahramanmaraş (Mw7,8/7,6) izledi (~3,0 yıl). Kürçer ve ark. Coulomb ile 2020'nin Erkenek ve komşu segmentlere gerilme aktardığını ve "tetikleyici" olduğunu savunuyor. Bu tek olaylı geriye dönük yorum; puanlanmış değil. — [Kürçer ve ark. 2026, Nat. Hazards](https://doi.org/10.1007/s11069-025-07896-8)
- Sagaing Fayı: 2025 Mw7,7 Mandalay kırığı 1839'dan beri kırılmamış boşluğu kırdı ve uçları 1930 ve 1946 kırıklarına uzandı. Yarı dinamik benzetimde Mw>7,5 için olaylar arası ~141 yıl, SS ~40 yıl. — [Antoine ve ark. 2025, PNAS](https://doi.org/10.1073/pnas.2514378122)
- Wesnousky 2006 (Nature, 10.1038/nature05275), kırık uçları: öncü çalışma (722 atıf), ancak gecikme değil, kırılmanın nerede durduğu üzerine. OpenAlex özeti yok. Projede S-1 (Biasi–Wesnousky sıçrama) bu hattı zaten kapattı. — [künye](https://doi.org/10.1038/nature05275)
- Kendi sayımım (USGS ComCat FDSN, M≥6,5, derinlik ≤40 km, 1904-01-01…2025-12-31, 3479 olay). Doğrultu atımlı süzgeç: ComCat moment-tensör ürününde iki düğüm düzleminin de rake'i 0/180'e ±30° yakın. 1976+ M≥7 birincil 459 olay, 456'sı mekanizmalı, 87'si doğrultu atımlı. "Komşu" kaba tanımı: ikincil merkez üssü, birincilin WC94 RLD yarı boyundan uzak ve en fazla 100 km ötede. Oran = çift sayısı / birincil-yıl maruziyeti (katalog sonuna göre sansürlü). Sonuçlar:
  - Doğrultu atımlı birincil → herhangi bir mekanizmada M≥6,5 ikincil:
    - 0–1 ay: n=16 (taban 48×)
    - 1 ay–1 yıl: n=4 (1,1×)
    - 1–3 yıl: n=13 (1,7×; Poisson p≈0,04)
    - 3–10 yıl: n=20 (0,85×)
    - 10–30 yıl: n=51 (1,2×)
    - 30–60 yıl: n=15 (taban, 326 birincil-yıl)
  - İkincil M≥7: 1–30 yıl toplamı n=23, taban beklentisi 14,7 (1,56×, nominal p≈0,027). Bu değer çok kutulu taramada nominal ve taban yalnız 3 olaya dayanıyor.
  - Tüm mekanizmalar, 1904+ M≥7 (1122 birincil) → M≥6,5: 1 ay–1 yıl 2,1×, 1–3 yıl 1,3×, 3–10 yıl 1,1×, 10–30 yıl 1,1×.
  — [USGS ComCat FDSN sorgusu](https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=1904-01-01&endtime=2025-12-31&minmagnitude=6.5&maxdepth=40&orderby=time-asc)
- Aynı süzgeçle M≥7 doğrultu atımlı → M≥7 doğrultu atımlı çiftler (gecikme >1 ay, 100 km bant): yalnız 10 çift. Çoğu okyanusal transform ve Mendosino üçlü eklemi: 1980→2024, 1994→2005, 1994→2024, 2005→2024 ve 1991→2005 (Kuzey Kaliforniya açıkları); Macquarie 1982→1989; Biak 1979→1985; Alaska Körfezi 1987→1988; Swan/Kayman 2018→2025. Kıta içi tek çift İzmit→Düzce 1999 (0,24 yıl). Gecikmeler 0,24–44 yıl. — [ComCat olay ayrıntıları](https://earthquake.usgs.gov/fdsnws/event/1/)

### Inferences
- Dağılım biçimi: küresel veride ilk aylarda Omori benzeri, sonra hızla tabana yakın, çok uzun ve zayıf bir kuyruk. Kaba sayımda 3 yıldan sonra fazlalık %10–20 düzeyinde. Bu, Parsons 2002'nin "7–11 yıl süren Omori" bulgusuyla nitel olarak uyumlu, ama kuyruk ETAS'ın Omori kuyruğundan ayırt edilemeyecek kadar küçük görünüyor. Log-normal tepe (ör. "~10 yılda bir tepe") kanıtlanmadı. KAF'ın ~10 yıllık ortalaması tek dizi.
- Medyan: "komşu kırıldı" koşullu gecikme medyanı küresel olarak tanımlı değil. Çoğu komşu, gözlem süresinde (≤50 yıl) hiç kırılmıyor (sağdan sansür). Tanımlı tek nicelik, birincil-yıl başına oran oranı.
- KAF 1939–1999 "batıya göç" ve 2020→2023 Doğu Anadolu, seçilmiş başarılı örnekler. Pondard 2007'nin 1894/1912 yalıtılmış olayları ve "her döngüde yayılım yok" bulgusu karşı örnek.

### Gaps
- KAF 1939–1999 tek tek gecikmeleri (1939→1942→1943→1944→1951→1957→1967→1999) Stein 1997'nin kapalı erişimli tablosunda. Özetten yalnız "ortalama 10 yıl" doğrulandı; olay bazlı liste bu notta kaynaklı verilmedi.
- Sumatra fayı, Xianshuihe, Kunlun/Bayan Har, Alpine, Ölü Deniz ve Denali için olay bazlı gecikme derlemesi bulunamadı (OpenAlex aramaları yalnız tek olay ve Coulomb çalışmaları döndürdü). Sumatra 2004→2005→2007 dalma-batma kaskadı için Philibosian & Meltzner 2020 kataloğu kaynak; sayısal tablo özette yok.
- GCMT ndk dosyası TLS zinciri hatası nedeniyle indirilemedi (atlatma yapılmadı). Mekanizma ComCat'ten alındı. ISC-GEM toplu indirme bağlantısı 404 verdi. 1976 öncesi doğrultu atımlı süzgeç yapılamadı.

## 2. Bu dağılımla kırılmamış komşu için koşullu olasılığı Poisson/ETAS'a karşı puanlayan çok olaylı sınav var mı; ETAS bunu kapsıyor mu

### Takeaway
Komşu segment gecikme eğrisini, çok olaylı ve log skorlu olarak Poisson/ETAS'a karşı puanlayan bir sınav bulunamadı: kanıtlanmadı. En yakın puanlanmış işler küresel uzun süreli kümelenme modelleri: Marzocchi & Lombardi 2008'in çift dallanma modeli ETAS ve Poisson'dan iyi; Nandan ve ark. 2022'de büyüklük korelasyonlu ETAS sözde-ileriye dönük sınavda basit ETAS'ı geçiyor. Bunlar fay segmenti komşuluğunu kullanmıyor. Michael 2011 ise M≥7 küresel kaydın "sabit oran + yerel artçılar" sıfır hipotezini reddedemediğini gösteriyor.

### Cited Findings
- Marzocchi & Lombardi 2008 (JGR, 10.1029/2007jb005472), çift dallanma modeli: ETAS'tan kalan "arka plan" ikinci bir dallanmayla, daha uzun zaman ve uzay kümelenmesiyle betimleniyor ("uzun süreli sismik etkileşim" olabilir). İki küresel katalogda tahmin performansı ETAS ve Poisson'dan üstün. Yazarlara göre bu uzun süreli evrim tehlike hesabında hiç kullanılmıyor. — [OpenAlex özet](https://doi.org/10.1029/2007jb005472)
- Nandan, Ouillon & Sornette 2022 (JGR, 10.1029/2022jb024380): Tetikleyen ve tetiklenen büyüklüğü arasında korelasyon kuran ve büyüklüğe bağlı Omori çekirdeği kullanan ETAS türleri, "sıkı sözde-ileriye dönük deneylerde" basit ETAS'ı anlamlı biçimde geçiyor. Büyük olaylar tercihen büyükleri tetikliyor. — [OpenAlex özet](https://doi.org/10.1029/2022jb024380)
- Michael 2011 (GRL, 10.1029/2011gl049443): 1900'den beri M≥7 kaydı, "bağımsız sabit oranlı olaylar + yerel artçı dizileri" sıfır hipotezini üç test sınıfıyla reddedemiyor. Risk yalnız süren artçı dizilerinde artıyor. — [OpenAlex özet](https://doi.org/10.1029/2011gl049443)
- Kagan & Jackson 2010 (GJI, 10.1111/j.1365-246x.2010.04857.x): Küresel günlük kısa ve uzun vadeli tahmin, zamansal ve uzamsal kümelenmeyle. Kısa vadeli olasılık kazancı GCMT'de ~2,0, PDE'de ~3,7 (zamanca rastgele ama uzamsal yerel sıfıra karşı). — [OpenAlex özet](https://doi.org/10.1111/j.1365-246x.2010.04857.x)
- Faenza, Marzocchi, Serretti & Boschi 2007 (Tectonophysics, 10.1016/j.tecto.2007.11.066): M7,0+ küresel sismisitenin parametrik olmayan uzay-zaman dağılımı. Özet OpenAlex'te yok; içerik doğrulanmadı. — [künye](https://doi.org/10.1016/j.tecto.2007.11.066)
- Parsons, Ji & Kirby 2023 (Seismic Record, 10.1785/0320230021): Wenchuan 2008 sonrası 4. günde verilmiş ileriye dönük gerilme aktarımı tahmininin 15 yıl sonraki değerlendirmesi. M≥4,5 artçıların biri dışında tümü gerilmesi artan faylarda. 7 ölümcül M>4,5 olayın 6'sı gerilmesi artan faylarda. Bu konum ve mekanizma uyumu; zaman ekseninde log skor ve Poisson/ETAS kıyası yok. — [OpenAlex özet](https://doi.org/10.1785/0320230021)
- Murru ve ark. 2016 (JGR, 10.1002/2015jb012595), Marmara: 26 kaynak, Poisson / BPT / BPT+ΔCFF. 30 yıllık olasılık kazancı (zamana bağlı / zamandan bağımsız) güney kollarda ~2 kat. Gerede segmentinde Poisson %29, etkileşimli %48. Bu bir tahmin, sınav değil. — [OpenAlex özet](https://doi.org/10.1002/2015jb012595)
- Parsons 2004 (JGR, 10.1029/2003jb002667): Marmara 2004–2034 bölgesel M≥7 olasılığı Poisson ~%38, zamana bağlı %44 ± 18, gerilme aktarımıyla %53 ± 18. İstanbul için Poisson %21, zamana bağlı + aktarım 41 ± 14 (oran ≈2,0). Yazar duyarlılıkların ortalama değerlere göre büyük olduğunu not ediyor. — [OpenAlex özet](https://doi.org/10.1029/2003jb002667)
- Parsons ve ark. 2000 (Science, 10.1126/science.288.5466.661): 1999 İzmit gerilme aktarımı dahil, İstanbul'da güçlü sarsıntı için 30 yılda 62 ± 15, 10 yılda 32 ± 12 olasılık. — [OpenAlex özet](https://doi.org/10.1126/science.288.5466.661)
- Ceferino, Kiremidjian & Deierlein 2020 (BSSA, 10.1785/0120180220): BPT + uzamsal korelogramlı çok değişkenli Bernoulli kırılma modeli. Lima dalma-batma zonunda AIC ile uzamsal etkileşimsiz modelden iyi. Bu AIC içi uyum, ileriye dönük log skor değil. — [OpenAlex özet](https://doi.org/10.1785/0120180220)
- Proje defteri: DK-3'te GR-ETAS, karakteristik koşullu M7'ye karşı tutarlı çıktı (−44,2 ± 8,2 nat karakteristik aleyhine). FA-1'de paleosismik kalitede tam olay geçmişine koşullama 10 yıl ufkunda yalnız +0,016 nat/pencere verdi. — kayit/kayit.py kayıtları DK-3, FA-1

### Inferences
- ETAS'ın kapsaması: ETAS, M7 sonrası komşu bantta ilk aylardaki 20–50 kat yükselmeyi zaten üretiyor. Kaba sayımdaki 1–30 yıllık %10–60'lık fazlalık, p≈1,1 Omori kuyruğunun on yıllara uzatılmasıyla büyük ölçüde açıklanabilir görünüyor. Bunun ayrıca sınanması gerek: ETAS'ın kendi beklentisi bu notta hesaplanmadı. "Gecikme eğrisi ETAS'tan fazlasını taşıyor" iddiası kanıtlanmadı.
- Marzocchi & Lombardi 2008'deki ikinci dallanma, bu adayın fay segmenti olmayan, puanlanmış en yakın akrabası. Adayın tek yeni öğesi, "komşu = fay geometrisiyle tanımlı bitişik segment" koşulu.
- FA-1 tavanı (MCQsim dünyasında tam olay geçmişiyle ≈0,016 nat / 10 yıl) bu adayın da yıl ölçeğinde büyük kazanç vermesini olası kılmıyor. Gecikme eğrisi zaten olay geçmişinin bir özeti.

### Gaps
- Bountzis, Tsaklidis & Papadimitriou 2022 (Physica A, 10.1016/j.physa.2022.127945), çevre-Pasifik büyük depremleri için durağan olmayan sözde-ileriye dönük tahmin: özet erişilemedi, içerik doğrulanmadı.
- Rhoades ve ark. 2011 için verilen DOI (10.1007/s11600-011-0013-5) OpenAlex'te bulunamadı; köprü B kümesi 3 tohumla koşuldu.
- Parsons & Velasco 2011 (Nat. Geosci., 10.1038/ngeo1110) özeti boş geldi. "Ana şok bölgesi dışında uzaktan tetiklenen büyük deprem yokluğu" başlıktan; sayılar doğrulanmadı.

## 3. Köprü ölçümü ve 0 € sınama taslağı: kaba N, komşuluk tanımı, en küçük ölçülebilir etki, Marmara için oran

### Takeaway
Köprüler (OpenAlex, 11 Kasım 2026):

| Köprü | k | J |
|---|---|---|
| A × B (ardışık kırılma × sınama) | 32 | 0,0127 |
| B × ETAS (pozitif kontrol) | 195 | 0,0564 |
| A × M (Marmara) | 401 | 0,144 |
| A × B × M | 5 | — |

A × B'nin J değeri kontrolün ≈0,23'ü. Kesişimde komşu segment gecikme eğrisini puanlayan iş yok: boşluk gerçek, ama nedeni büyük olasılıkla güç yokluğu. Kaba sayımda doğrultu atımlı M≥7 birincil 87 (1976–2025); komşu bantta 1–30 yıl içinde M≥7 hedef 23, M≥6,5 hedef 84. Gözlenen oran yükselmesi 1,1–1,6 kat. t=2 için bu etki ~130–550 hedef ister, eldeki sayı 4–20 kat az.

### Cited Findings
- Köprü tohumları:
  - A (ardışık kırılma, 8 tohum): Stein 1997, Parsons 2002, Scholz 2010, Kagan & Jackson 1999, Pondard 2007, Dolan 2007, Philibosian & Meltzner 2020, Parsons & Velasco 2011. Tekil atıf birleşimi 2072.
  - A_SAYISAL (4 tohum): Parsons 2002, Kagan & Jackson 1999, Scholz 2010, Stein 1997. Birleşim 1644.
  - B (sınama): Schorlemmer 2007 (10.1785/gssrl.78.1.17), Zechar ve ark. 2010 (10.1785/0120090192), Bird 2015 GEAR1 (10.1785/0120150058). Birleşim 476.
  - KONTROL (ETAS): Ogata 1988 (10.1080/01621459.1988.10478560), Ogata 1998 (10.1023/a:1003403601725), Zhuang 2002 (10.1198/016214502760046925). Birleşim 3174.
  - M (Marmara): Parsons 2000, Parsons 2004, Hubert-Ferrari 2000 (10.1038/35005054), Armijo 2005 (10.1029/2004gc000896). Birleşim 1115.
  — `/home/user/knotenlinie/kayit/turetme/kopru/gecikme/kopru_rapor.json` ([OpenAlex](https://openalex.org))
- Köprü sonuçlarının tamamı: A×B k=32, J=0,0127; A_SAYISAL×B k=28, J=0,0134; B×ETAS (pozitif kontrol) k=195, J=0,0564; A×M k=401, J=0,1439; A×B×M k=5, J=0,0016; A×ETAS k=165, J=0,0325; A×B×ETAS k=16, J=0,0030. — [kopru_rapor.json, OpenAlex](https://openalex.org)
- A×B×M kesişimindeki 5 işin hiçbiri çok olaylı sınav değil: Earth Observation incelemesi 2020; Wasatch gerilme-olasılık 2019 (10.1093/gji/ggz336); Çin sayısal tahmin yol haritası 2018; bir kitap kaynakçası; OEF kılavuzu 2011 (10.4401/ag-5350). A×B'de uzun süreli kümelenmeyi puanlayan işler yalnız Marzocchi & Lombardi 2008 ve Faenza 2007 (bkz. bölüm 2). — [kopru_rapor.json](https://openalex.org)
- Kaba N ve oranlar bölüm 1'deki ComCat sayımından:
  - 1976–2025 doğrultu atımlı M≥7 birincil: 87.
  - Komşu bantta ikincil (gecikme 1 ay–60 yıl): M≥6,5 103, M≥7 29.
  - Doğrultu atımlı → doğrultu atımlı M≥7 çift: 10. Kıta içi bunlardan 1 (İzmit→Düzce).
  - 1904–2025, tüm mekanizmalar: M≥7 birincil 1122.
  — [USGS ComCat](https://earthquake.usgs.gov/fdsnws/event/1/)
- Kaba güç hesabı (benim hesabım; varsayım: model doğru ve oran çarpanı g sabit). Tek pencerede LLR = n·ln g − λE(g−1). Ortalama/SS = √(λEg)·[ln g − (g−1)/g]/ln g. t=2 için gereken beklenen hedef sayısı: g=1,1 → ~1900; 1,2 → ~540; 1,5 → ~130; 2 → ~52; 3 → ~26. Olay başına beklenen kazanç (KL): g=1,2 → 0,016 nat; 1,5 → 0,072 nat; 2 → 0,19 nat. — [hesap; bu not]
- Hubert-Ferrari ve ark. 2000 (Nature, 10.1038/35005054) ve Armijo ve ark. 2005 (G³, 10.1029/2004gc000896), İzmit sonrası Marmara gerilme ve fay geometrisi çekirdeği. Özetler OpenAlex'te boş veya kısmi. — [künye](https://doi.org/10.1038/35005054); [Armijo 2005](https://doi.org/10.1029/2004gc000896)

### Inferences
- Komşuluğun nesnel tanımı (öneri, ön kayıt için):
  1. GEM Global Active Faults iz geometrisi üzerinde birincil kırığın iki ucu belirlenir. Uç, ComCat/USGS sonlu-fay ürününden veya WC94 RLD ile merkez üssünden ±L/2 alınır.
  2. İkincilin kırık ucu ile birincilin kırık ucu arası en kısa mesafe ≤ D (ör. 20 km) ve ikincil merkez üssü birincil kırığının dışında olmalı.
  3. Aynı fay sistemi: GEM'de aynı fay adı/sistemi ya da azimut farkı <30°.
  4. D önceden sabitlenir ve tek değer kullanılır.
  
  Bu notta merkez üssü + 100 km bant kullanıldı. Bu kaba tanım Landers→Hector Mine gibi örtüşen kırıkları dışarıda bırakıyor, birbirine paralel ama ayrı fayları içeri alıyor.
- En küçük ölçülebilir etki: 1976–2025 doğrultu atımlı M≥7 birincil ve M≥6,5 hedefle 1–30 yıl penceresinde beklenen hedef ~75–85 (gözlenen 84). Bu sayıyla t=2'de ancak g≈1,6–1,7 ve üstü görülebilir. Gözlenen oran yükselmesi ≈1,14 (p≈0,12). M≥7 hedefle (beklenen ~15) ancak g≳2,3 görülebilir; gözlenen 1,56 nominal. 1904+ tüm mekanizmalara genişletmek N'yi ~10 kat artırır, ama sınav artık "doğrultu atımlı fay segmenti" sorusu olmaz. Ayrıca 1964 öncesi M6,5 tamlığı ve konum hatası komşuluk tanımını bozar.
- ETAS'a karşı fark daha da küçük olmalı: gözlenen fazlalığın bir kısmını ETAS'ın Omori kuyruğu zaten veriyor. ETAS'a karşı ayırt edilebilir etki, Poisson'a karşı olandan küçük. Kaba hüküm: güç yok.
- Marmara için eğrinin söyledikleri (yalnız oran; küresel sayımın doğrudan aktarımı, kanıtlanmış değil):
  - 1999 İzmit'in batı ucundaki Prens Adaları ve Orta Marmara segmentleri için 2026'da gecikme ~27 yıl, 10–30 yıl kutusuna düşüyor. Küresel doğrultu atımlı sayımda bu kutunun oran oranı M≥6,5 hedef için ≈1,2×, M≥7 için ≈1,65× (n=14, taban n=3). Güven aralığı 1'i rahatça içeriyor.
  - 1912 Ganos'un doğu ucu için gecikme 114 yıl, sayımın kapsadığı 60 yılın dışında. Eğri burada tabana (1×) iner; bilgi yok.
  - Parsons 2004'ün aktarım + zamana bağlılık oranı ≈2 (İstanbul, 30 yıl) fizik modelinden; bu ampirik eğri ondan küçük bir oran öneriyor. İkisi de sınanmadı.
- Sağ kalım ve seçim yanlılığından korunma:
  1. Birincil kümesi yalnız büyüklük, mekanizma ve tarih ölçütüyle seçilir. "Göç etmiş" diziler (KAF, Doğu Anadolu) önceden anılmış diye eklenmez ve çıkarılmaz.
  2. Her birincilin her iki ucu ayrı bir "komşu" sayılır. Kırılmayan komşular sıfır olay olarak paydaya girer (birincil-yıl maruziyeti, sağdan sansür katalog sonu).
  3. Taban oran aynı komşu bölgelerin birincilden önceki dönemi veya uzun gecikmeli dönem ile kıyaslanır, ikisi birden raporlanır.
  4. Türkiye olayları (1939–1999 KAF, 2020/2023 DAF) model kurulumundan çıkarılıp yalnız bekletilmiş sınav kümesi yapılır. Böylece Marmara sezgisini doğuran dizi eğriyi eğitmez.
  5. Sözde-ileriye dönük: eğri 1976–2005 birincilleriyle kurulur, 2006–2025 birincilleri ve hedefleriyle puanlanır. Ancak 2006–2025'te doğrultu atımlı M≥7 birincil ~35–40, hedef sayısı birkaç düzinede kalır.
  6. Aynı bölgedeki çoklu sayım (Mendosino gibi aynı yere 4–5 çift düşen bölgeler) kümelenmiş standart hata ile düzeltilir.
- Defterle farkı:
  - DK-3: M6 öncüyle koşullu M7, H0. Bu aday M7 sonrası, kırık dışı ama bitişik bölgede, fiziksiz ampirik gecikme çekirdeği kullanıyor.
  - TK-E5: M>5 doğuya göç, ay ölçekli. Bu aday M7→M6,5/7 ve yıl–on yıl ölçekli.
  - VE-2 ve M7-D1D4: ΔCFS fiziği ve segment sıralaması. Bu aday fizik kullanmıyor.
  - EL-4 (boşluk): bunun tersi; burada "yakın zamanda komşu kırıldı" etkisi aranıyor.
  - ZAMAN-BPT: aynı segmentin kendi saati. Burada komşunun saati söz konusu.
  
  Örtüşme riski: FA-1 tavanı ve DK-3'ün ETAS bulgusu, bu adayın ETAS'tan fazlasını vermeyeceğini öngörüyor.

### Gaps
- ETAS'ın aynı komşu bantta 1–30 yıl için beklediği oran fazlalığı hesaplanmadı. Bu, adayın asıl sıfır modelini belirler ve ilk yapılacak iş.
- GEM Global Active Faults ile segment ucu tabanlı komşuluk uygulanmadı. N, merkez üssü bandına göre değişebilir.
- 1976 öncesi mekanizma (ISC-GEM moment tensörleri) indirilemedi. Tarihsel derlemeler (ör. Ambraseys) taranmadı.

### Aday tablosu

| aday adı | soru | köprü k ve J (kontrolle) | veri ve erişim | hedef sayısı ve kaba güç | zaman eksenine bağı | en büyük risk |
|---|---|---|---|---|---|---|
| GK-1 "Komşu segment gecikme çekirdeği" (öneri; deftere yazılmadı) | M≥7 doğrultu atımlı kırılmadan sonra bitişik segmentte M≥6,5/7 olasılığı, birincilden geçen süreye bağlı ampirik oran eğrisiyle (fizik yok) Poisson ve ETAS'ı sözde-ileriye dönük log skorla geçer mi? | A×B k=32, J=0,0127; kontrol B×ETAS k=195, J=0,0564 (J oranı ≈0,23). A×B×M k=5, hiçbiri sınav değil. A×M k=401, J=0,144 (Marmara anlatısı bol, sınav yok). | USGS ComCat FDSN (açık, 1904–2025-12-31) + ComCat moment tensör (1976+, 456/459 M7 mekanizmalı). GCMT ndk TLS hatası, ISC-GEM toplu indirme 404 (atlatılmadı). GEM GAF açık. 0 €. | 1976–2025: 87 doğrultu atımlı M7 birincil. 1–30 yıl hedef M≥6,5 84 (beklenen ~73, oran 1,14) ve M≥7 23 (beklenen ~15, oran 1,56). t=2 için g=1,2'de ~540, g=1,5'te ~130 hedef gerekir. Eldeki 4–20 kat az. Güç yok. | Doğrudan: yıl ölçekli tehlike eğrisi. Marmara'da 1999 + 27 yıl → 10–30 yıl kutusu, oran ~1,2–1,65 (belirsiz). 1912 + 114 yıl → eğri dışı (1×). | Fazlalık ETAS Omori kuyruğuyla zaten açıklanıyor olabilir (DK-3, FA-1 bulgularıyla uyumlu). Ayrıca seçim/sağ kalım yanlılığı: KAF ve DAF dizileri eğitime sızarsa sonuç şişer. |
