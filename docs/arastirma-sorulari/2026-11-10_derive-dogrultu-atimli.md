# Başka doğrultu atımlı fay sistemlerinden İstanbul'a türetilen çalışmalar (10 Kasım 2026)

Erdem (10 Kasım 22:18): "önceki çalışmalardan yeni çalışma derive edelim, İstanbul odaklı fakat İstanbul için hazırlanmamış, benzer çalışmalardan yola çıkarak."

Bu belgenin alanı: diğer büyük doğrultu atımlı ve çek-ayır havzalı fay sistemleri (Alpine, Sumatra, Sagaing/Mandalay 2025, Denali, Altyn Tagh/Kunlun/Haiyuan, Ölü Deniz/Akabe, Kuzey İran, Kaikōura, Maduo, Palu, Kahramanmaraş 2023, San Andreas sünen kesimi, İsmetpaşa).

**Durum:** salt tarama ve okuma, 0 €, hiçbir şey koşulmadı, makine kiralanmadı. Türkiye dışı 2026 verisine dokunulmadı. Seçim Erdem'in. Olasılık yazılmaz.

## Yöntem

- Doğrudan öncül taraması: OpenAlex (anahtarlı) ile ≈25 hedefli sorgu, öne çıkan işlerin özetleri okundu.
- Köprü ölçümü (Erdem yöntemi): OpenCitations Index v2, `tools/literatur/bosluk_olc_v3.py` ile aynı betik, 10 Kasım v3 tohumlarına 6 yeni küme eklendi. k = iki (ya da üç) tohum kümesinin hepsine atıf yapan iş sayısı. Pozitif kontrol aynı koşuda yeniden ölçüldü: sınama × ETAS k 103, J 0,0551 (10 Kasım v3 ile aynı).
- Tohumlar, köprüler ve ham rapor: `docs/arastirma-sorulari/derive-dogrultu-atimli/`.

| Köprü | Küme boyları | k | J |
|---|---|---|---|
| Kontrol: sınama × ETAS | 368, 1604 | 103 | 0,0551 |
| Kenetlenme→kırık × 2016+ olaylar | 955, 1370 | 16 | 0,0069 |
| Kenetlenme→kırık × sınama | 955, 368 | 5 | 0,0038 |
| **Kenetlenme→kırık × 2016+ olaylar × sınama** | | **0** | 0 |
| Kayma öngörülebilirliği × 2016+ olaylar | 673, 1370 | 9 | 0,0044 |
| Sismisite kümelenmesi→kenetlenme × Marmara | 30, 418 | 2 | 0,0045 |
| **Sismisite kümelenmesi→kenetlenme × sınama** | 30, 368 | **0** | 0 |
| Sünen kesim bariyeri × sıçrama | 1019, 1419 | 83 | 0,0352 |
| **Sünen kesim × sıçrama × sınama** | | **0** | 0 |
| Sünen kesim × Marmara | 1019, 418 | 22 | 0,0155 |
| Çok-faylı tehlike modeli (UCERF3) × 2016+ olaylar | 671, 1370 | 74 | 0,0376 |
| **UCERF3 × 2016+ olaylar × sınama** | | **2** (ikisi de derleme) | 0,0009 |
| Sismik boşluk × 2016+ olaylar | 232, 1370 | 1 (derleme) | 0,0006 |
| Sismik boşluk × sınama | 232, 368 | 23 | 0,0399 |

Okuma: üçlü kesişimlerin hepsi 0 ya da yalnız derleme. "Sismik boşluk × sınama" kalın (J 0,040, kontrolün %72'si): boşluk hipotezi zaten sınanmış bir alan (Kagan–Jackson 1991, Rong–Jackson–Kagan 2003), yeni soru değil.

## İstanbul belirsizliğinin hedeflenen kaynakları (panelden)

İstanbul 30 yıl aralığı: uzamsal eksen ≈%46, dal içi parametreler ≈%37 (moment dalı %14, istatistik oranı %12, Parsons σ %6). Simülatör hattında (v2.x) CMF/PIF kilitlenmesi ve ortak kırılma. CMF kayma açığı 11 ± 3 mm/yıl (Y1b); PIF karadan ölçülemiyor (Y1c). v1.7 ortak kırılma f ≈ 0,10; S1 PIF→CMF geçiş P 0,21–0,85.

## Sıralı adaylar

### 1. Olay öncesi kenetlenme haritası M7 kırığının yerini ve kaymasını gösteriyor mu? (çok olaylı, ön kayıtlı)

- **Kaynak çalışmalar:** Moreno 2010 (Maule), Loveless–Meade 2011 (Tohoku), Chlieh 2008 (Sumatra): dalma-batmada kenetlenme–kayma ilişkisi. Doğrultu atımlıda tek olaylı, geriye dönük: Carrero Mustelier–Meade 2026 (Kahramanmaraş, ESSOAr; batı %75'te korelasyon yüksek, doğu %25'te düşük), Han 2025 (DAF kayma tamamlayıcılığı, CEE), Ulrich 2026 (Mandalay, Nat Commun; kayma ve geometri olay öncesi gözlemlerden "öngörülebilirdi").
- **Boşluk kanıtı:** kenetlenme × 2016+ olay × sınama üçlü k = 0. Var olan işlerin hepsi tek olay ve geriye dönük; ön kayıtlı, çok olaylı, log skorlu bir sınav yok.
- **İstanbul'a taşıma:** CMF kısmen kilitli (batısı sünüyor, Kumburgaz doğusu kilitli). Sınav geçerse M7 kaymasının Marmara içindeki uzamsal dağılımına kenetlenme ağırlıklı üçüncü bir bileşen eklenir (bugün ETAS 0,5 + gerinim 0,5).
- **H1:** Olay öncesi yayımlanmış kenetlenme haritasıyla ağırlıklandırılmış kayma yeri, tekdüze ve iz uzunluğu orantılı rakibi log skorda geçer. **H0:** ayırt edilemez ya da daha kötü (S3'te mikrosismisite için olan buydu).
- **Veri ve sızıntı:** Olaylar Kahramanmaraş 2023 (iki ana şok), Elazığ 2020, Mandalay 2025, Palu 2018, Kaikōura 2016, Maduo 2021. Girdi: olaydan önce yayımlanmış kenetlenme modelleri ya da yayımlanmış GNSS hız tablolarıyla kendi blok modelimiz (sızıntı kapısı: yayım tarihi < olay tarihi). Hedef: USGS/SRCMOD sonlu fay modelleri (≤2025). Türkiye dışı 2026 yok.
- **İstanbul M7+ beklenen katkısı:** uzamsal eksen en büyük pay (≈%46), ama N ≈ 6–8 olay, güç zayıf; ateşleme kapısı şart. v1.3b değişmez; sonuç ileri test defterine rakip olarak girer.
- **Maliyet/süre:** 0 €, 1–2 hafta (en uzun adım: olay öncesi kenetlenme modellerini sayısal hale getirmek).

### 2. Sismisite kümelenmesinden PIF kenetlenmesi: San Andreas ilişkisini Marmara'ya taşımak

- **Kaynak çalışma:** Liu, Ross, Cochran 2022 (Sci. Adv.): orta San Andreas'ta sünme hızı, kümelenmemiş deprem payıyla doğrusal orantılı (1984–2020). Benzer: Liu 2026 (Laohushan–Haiyuan, sismisite + jeodezi), Zaccagnino 2023 (Anadolu CV, nitel).
- **Boşluk kanıtı:** kümelenme × sınama k = 0; kümelenme × Marmara k = 2 (Becker 2023 tekrarlayan depremler; Zaccagnino 2023 nitel CV haritası). San Andreas kalibrasyonunu başka faya taşıyıp kenetlenme sayısı çıkaran iş yok.
- **İstanbul'a taşıma:** PIF kayma açığı jeodeziyle ölçülemiyor (Y1c: Çınarcık–Armutlu takası). Bu, PIF için jeodezi dışı tek sayısal yol. CMF pozitif kontrol: batısı sünüyor, doğusu kilitli, 11 ± 3 mm/yıl biliniyor.
- **H1:** San Andreas'ta kurulan ilişki, bağımsız sünen fayları (Hayward, Calaveras, İsmetpaşa, Haiyuan) önceden yazılmış toleransla tutturur ve Marmara'da CMF batı/doğu farkını doğru işaretler. Ancak bu ikisi geçerse PIF tahmini üretilir. **H0:** transfer başarısız (katalog Mc'si ya da kümesizleştirme farkı ilişkiyi bozar), PIF sayısı verilmez.
- **Veri ve sızıntı:** NCEDC/SCSN (San Andreas), yayımlanmış sünme hızları; Marmara KOERI/AFAD ≤2025 (mühür açıldı, geliştirme verisi). Türkiye dışı 2026 yok.
- **Beklenen katkı:** v1.3b'de küçük (kayma açığı yalnız ≈%2,6 ağırlıklı moment dalında); v2.x simülatör hattında büyük (v2.2'de varyansın %96'sı CMF/PIF kilitlenmesiydi, v2.3 CMF'yi kapattı, PIF açık). **Risk:** PIF'te sismisite seyrek; ilişki az olayla belirsiz kalabilir. S3 ve S7'de sismisite tabanlı sinyaller H0 çıktı.
- **Maliyet/süre:** 0 €, 3–5 gün. En ucuz aday, önce sentetik/çapraz fay kontrolüyle kapıdan geçer.

### 3. Kayma öngörülebilirliği (slip-predictable) çok olaylı sınavı → bir sonraki Marmara kırığının büyüklüğü

- **Kaynak çalışmalar:** Vavra, Fialko, Bulut 2025 (CEE): Kahramanmaraş "gevşek kayma öngörülebilir", eş-sismik kayma son depremden beri biriken açığa eşit ya da büyük. Ulrich 2026 (Mandalay): "asgari kayma öngörülebilir". Shimazaki–Nakata 1980. Paleosismik: Hope fayı Conway (2019), Alpine.
- **Boşluk kanıtı:** kayma öngörülebilirliği × 2016+ olay k = 9; hepsi tek olay ya da paleosismik. Yöntemi aynı kuralla birden çok olaya uygulayan ve uzunluk ölçekli büyüklük kestirimiyle yarıştıran iş bulunamadı.
- **İstanbul'a taşıma:** son olaydan beri açık (CMF 1766, PIF 1766/1894 tartışmalı, Ganos 1912, Çınarcık 1894) × kayma hızı (CMF 11 ± 3) → segment başına koşullu Mw dağılımı. Moment dalı ve Mchar'a girer; v2.x'te simülatör çıktısıyla karşılaştırılır.
- **H1:** açık tabanlı Mw kestirimi, yalnız kırık uzunluğuna dayalı ölçek ilişkisini (Wells–Coppersmith, Leonard) log skorda geçer. **H0:** ayırt edilemez.
- **Veri ve sızıntı:** yayımlanmış sonlu fay modelleri, tarihsel son olay tarihleri, olay öncesi yayımlanmış kayma hızları (≤2025). Olay-segment sayısı ≈ 8–12 (Kahramanmaraş segmentleri, Mandalay segmentleri, Palu, Elazığ).
- **Beklenen katkı:** moment dalı İstanbul aralığının ≈%14'ü ama v1.3b'de ağırlığı 0,05; etki küçük-orta. v2.x ve Mw dağılımı için orta.
- **Maliyet/süre:** 0 €, 4–6 gün.

### 4. Sünen kesim kırığı durdurur mu? Ganos–CMF–PIF ortak kırılması

- **Kaynak çalışmalar:** Harris 2017 (Rev. Geophys., büyük depremler ve sünen faylar), Kaneko 2010, Noda–Lapusta 2013 (sünen kesim dinamik zayıflamayla kırılabilir), Rolandone 2018. Analoglar: Parkfield (1857 ve 1966/2004 uçları), Haiyuan 1920 batı ucu ve Laohushan sünmesi, İsmetpaşa (1943/1944/1951), Chaman, Hayward.
- **Boşluk kanıtı:** sünme × sıçrama k 83, J 0,035 (nitel bilgi iyi biliniyor, 10 Kasım'da da "boşluk değil" diye yazılmıştı); ama sünme × sıçrama × sınama k = 0. Sünme oranına bağlı sayısal geçiş olasılığını çok olayda sınayan iş yok. Marmara'ya özel dinamik/simülatör çalışmaları var: Aochi–Ulrich 2015, Güvercin–Barbot 2025 (MMF'de kalıcı segmentasyon, 10.000 yıl), Osei-Tutu 2026 (Adalar çek-ayır havzası, EGU özeti).
- **İstanbul'a taşıma:** CMF batısı 10–15 mm/yıl yüzey sünmesi gösteriyor. Sünen kesim bariyerse Ganos–CMF ortak kırılması ve İstanbul'a yakın Mw üst kuyruğu küçülür; değilse büyür. v1.7 f ≈ 0,10 ve S1 geçiş olasılıklarını sınırlar.
- **H1:** kırık uçları sünen kesim sınırlarında rastgeleden sık durur, sünme oranıyla artan bir geçiş eğrisi öncedenkinden iyi tahmin eder. **H0:** ayırt edilemez.
- **Veri ve sızıntı:** SURE 2.0 / FDHI kırık uçları, Harris 2017 sünen fay derlemesi, yayımlanmış sünme hızları. N ≈ 10–15 uç; güç zayıf. S1'in (sıçrama kuralları) tamamlayıcısı, onunla birleşik raporlanmalı.
- **Beklenen katkı:** ortak kırılma payı ve Mw üst kuyruğu; v1.3b'de küçük, v2.x ve v1.7'de orta.
- **Maliyet/süre:** 0 €, 3–5 gün.

### 5. Olay öncesi tehlike modellerinin çok-faylı kırılma karnesi

- **Kaynak çalışmalar:** Kaikōura (21 fay; NZ NSHM 2010), Kahramanmaraş (ESHM13/TBDY 2018 segmentleri; Wang–Barbot 2024, Hara–Toda 2026), Mandalay 2025 ("değişken segmentasyon", 2025), Palu, Maduo. NZ'de segmentli ve çok-faylı model kıyası (2023).
- **Boşluk kanıtı:** UCERF3 × 2016+ olay × sınama k = 2, ikisi de derleme. 2016+ büyük doğrultu atımlı depremlerde olay öncesi ulusal modellerin gerçek kırığı (uzunluk, Mw) kendi senaryo kümesinde içerip içermediğini sistematik puanlayan karne bulunamadı.
- **İstanbul'a taşıma:** Marmara için segmentli modellerin (ESHM20, bizim v1.3b) bütün-Marmara Mw 7,5+ senaryosuna verdiği ağırlığı denetler. Mchar ve ortak kırılma dalı.
- **H1:** segmentli olay öncesi modeller gerçek kırığı sistematik olarak küçük tahmin etmiş (kırık/maks. senaryo oranı > 1 olay payı önceden yazılmış eşiği aşar). **H0:** ayırt edilemez.
- **Veri ve sızıntı:** olay öncesi yayımlanmış tehlike modeli kaynak dosyaları (EFEHR, GEM, USGS), SURE 2.0. N ≈ 7; bir karne, güçlü bir sınav değil.
- **Beklenen katkı:** küçük; daha çok v1.7 ortak kırılma dalı için bağlam.
- **Maliyet/süre:** 0 €, 3–4 gün.

## Elenenler (neden)

- **Sismik boşluk hipotezinin doğrultu atımlı karnesi:** sınama literatürü kalın (J 0,040), zaman ekseni bizde v1.3 (296 olay, Poisson 0,95), D1 ve D2 ile zaten sınandı.
- **Çek-ayır havza geçişi (Akabe 1995, Palu körfezi, Kokoxili Taiyang Gölü):** S1 sıçrama sınavının alt kümesi; Palu ve Akabe için açık kırık izi yok, S1 aynı nedenle dışarıda bırakmıştı. Marmara'ya özel simülasyon zaten var (Osei-Tutu 2026, Ozawa 2023 bükümde durma olasılığı). Aday 4'e bilgi satırı olarak eklenebilir.
- **Fay olgunluğu → kırık uzunluğu (Hutchison, Böse, Manighetti 2020):** erken uyarı için, ileri tahmin değil; Marmara'da olgunluk ölçüsü tek değer, segment ayrımı vermez.
- **Viskoelastik kenetlenme (Guo 2026), gevşeme:** K10 kapalı.

## Önerilen sıra

2 (en ucuz, PIF'e doğrudan) ve 1 (en büyük pay) paralel; 3 ve 4 sonra, 4 S1 sonuçlarıyla birlikte; 5 boşta. Her biri ön kayıtla başlar, sonuç ileri test defterine rakip olarak girer, v1.3b değişmez.

## Sınırlar

Tohum seçimi sonucu belirler. Üçlü kesişimin 0 çıkması "kimse yapmadı" demek değil, "bu tohumlara birlikte atıf yapan iş yok" demek. 2026 tarihli öncüller (EGU özetleri, ön baskılar) atıf ağına henüz tam girmedi; doğrudan aramayla bulundu ve yukarıda adıyla yazıldı.
