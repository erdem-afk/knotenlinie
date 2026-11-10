# Kaliforniya çalışmalarından İstanbul'a türetilen adaylar (10 Kasım 2026)

Erdem'in isteği: İstanbul için hazırlanmamış ama benzer çalışmalardan İstanbul odaklı yeni iş türetmek. Bu belge San Andreas / Kaliforniya alanı (UCERF3, UCERF3-ETAS, RSQSim, CSEP Kaliforniya, Parkfield, Hayward, sünen kesim). Salt tarama ve okuma, 0 €, hiçbir koşu yapılmadı, makine kiralanmadı. Olasılık yazılmaz. Seçim Erdem'in.

## Yöntem

Erdem yöntemi (köprü sorusu, eş-atıf kesişimi, pozitif kontrol). Kaynak OpenAlex (anahtarlı), 10 Kasım akşamı. Sınama çekirdeği bugünkü S1–S7 ile aynı 5 makale. Yeni kümeler: MARMARA (7 tohum: Parsons 2004, Murru 2016, Hergert ve Heidbach 2010, Ergintav 2014, Bohnhoff 2013, Armijo 2005, Lange 2019), UCERF3 ters çözüm + SHERIFS (4), UCERF3-ETAS (3), sünen faylar (4), Hayward (3), CSEP Kaliforniya (5), öncü şok (3), karakteristik / GR (5), çarpımsal hibrit (3). 38 tohumun hepsi DOI ile bulundu. Kod ve ham çıktı: `tools/literatur/derive_kaliforniya/` (`oa_kesisim_rapor_ca.json` kesişim işlerinin başlıklarını içerir).

| Köprü | Küme boyları | k | Jaccard |
|---|---|---|---|
| Pozitif kontrol: ETAS × sınama | 2349 / 508 | 164 | 0,061 |
| Kontrol: ETAS × Marmara | 2349 / 824 | 14 | 0,004 |
| UCERF3 ters çözüm × Marmara | 702 / 824 | 19 | 0,013 |
| UCERF3 ters çözüm × Marmara × sınama | | 1 (ilgisiz) | 0,0005 |
| UCERF3-ETAS × Marmara | 262 / 824 | 4 | 0,004 |
| UCERF3-ETAS × sınama | 262 / 508 | 42 | 0,058 |
| Sünen faylar × Marmara | 1092 / 824 | 20 | 0,011 |
| Sünen faylar × sınama | 1092 / 508 | 10 | 0,006 |
| Sünen faylar × Marmara × sınama | | 1 (ilgisiz) | 0,0004 |
| Hayward × Marmara | 323 / 824 | 10 | 0,009 |
| Hayward × sınama | 323 / 508 | 1 | 0,001 |
| CSEP Kaliforniya × Marmara | 275 / 824 | 2 | 0,002 |
| Çarpımsal hibrit × Marmara | 104 / 824 | 1 | 0,001 |
| Öncü şok × Marmara | 1205 / 824 | 10 | 0,005 |
| Karakteristik/GR × Marmara | 728 / 824 | 18 | 0,012 |
| Karakteristik/GR × sınama | 728 / 508 | 16 | 0,013 |

Okuma: Kaliforniya yöntemleri Marmara'ya ulaşmış (k 10–20), ama Marmara'ya taşınan hiçbir Kaliforniya yöntemi sınanmamış: her üçlü kesişim 0–1 ve o tek iş ilgisiz (bir yer gözlemi derlemesi).

## Doğrudan öncüller (kesişim başlıkları okundu, özetler OpenAlex'ten)

- **Chartier, Scotti, Lyon-Caen 2021, NHESS** (10.5194/nhess-21-2733-2021): SHERIFS (UCERF3 tarzı sistem düzeyi oran çözümü) Marmara'ya uygulanmış. Mantık ağacında Marmara'nın kilitlenme durumu, en büyük kırılma, MFD şekli, fay dışı pay; dallar katalog oranına uyumla ağırlıklı. Sınav yok, 2016+ kilitlenme verisi yok.
- **Koca ve Şeşetyan 2025, BEE**: KAF ve DAF için karakteristik hibrit tekrar modeli, çok segmentli kırılma dahil. Sınav yok.
- **Murru ve diğ. 2016, JGR**: Marmara M≥7 BPT + Coulomb (zaten tohum; v1.3 ile ilgili).
- **Güvercin ve Barbot 2025, Commun. Earth Environ.**: 10 000 yıllık döngü simülasyonu, Ana Marmara Fayı'nda kalıcı kırılma bölünmesi (büküm + kalın tortul). Simülasyon, veri sınavı değil.
- **Martínez-Garzón ve diğ. 2025, Science**: son 15 yılda M>5 olayların doğuya ilerlemesi, 2025 M6,2. Betimsel.
- **Becker ve diğ. 2023, GRL**: tekrarlayan depremlerle orta ve batı CMF sünmesi, Ganos ve PIF'e doğru azalıyor (bizim v1.8 tablosunda var).
- **Alhan ve Khabat 2026, EarthArXiv**: Marmara'da sızıntı denetimli ML − ETAS, M≥3,5 / 30 gün. Kısa vade, M7 yok.
- **Savran ve diğ. 2020, BSSA**: UCERF3-ETAS'ın Ridgecrest dizisinde sözde-ileriye dönük sınavı. Yalnız Kaliforniya, tek dizi.
- **Bayona ve diğ. 2020 GJI, 2022 GJI; Rhoades 2014**: gerinim × sismisite çarpımsal hibritleri (küresel ve Kaliforniya), ileriye dönük sınanmış. GEAR1 de log-doğrusal hibrit.

## Adaylar (sıralı)

İstanbul aralığının bugünkü kaynakları (v1.5/v1.6): uzamsal %46, dal içi %37 (moment dalı %14, istatistik dalı oranı %12, Parsons σ %6). v1.6 dersi: dış veri yalnız moment dalına ve segment birleşimine ulaşıyor; uzamsal eksen ve istatistik oranı dış veriyle daralmadı. Sıra bu yüzden istatistik oranına ve moment dalına dokunan işleri öne alıyor.

### K1 · Karakteristik çarpan: fay yakını sismisitenin GR uzatması M7 oranını ne kadar ıskalıyor?
- **Kaynak:** Wesnousky 1994 (BSSA), Kagan 1996 yorumu, Stirling, Wesnousky, Shimazaki 1996 (GJI, iz karmaşıklığı ve MFD şekli), Page ve van der Elst 2018 (Kaliforniya fayları, fay toleranslı b), Parsons 2018.
- **İstanbul'a taşıma:** istatistik dalı M7 oranını GR uzatmasıyla alıyor. v1.3'ün 17 Türkiye dışı doğrultu atımlı fay grubunda (296 paleosismik olay, açılmış) ≤2025 fay yakını sismisiteden GR ile uzatılan M7 oranı paleosismik oranla kıyaslanır; çarpan fay olgunluğu ve iz karmaşıklığıyla açıklanabiliyor mu (birini dışarıda bırak)? Açıklanıyorsa Marmara segmentlerine (Ganos, CMF, PIF, Çınarcık) önceden yazılmış kuralla uygulanır.
- **Boşluk:** Karakteristik × Marmara k 18; içinde Chartier 2021 ve Koca–Şeşetyan 2025 MFD şeklini varsayıyor ya da katalogla ağırlıklıyor, hiçbiri paleosismik oranla fay bazında sınamıyor. Stirling 1996 küresel ama 1990'ların katalogları, Türkiye'ye uygulanmamış.
- **H1:** çarpan (log oran) fay özelliklerinden LOO ile sabit çarpandan iyi tahmin ediliyor (önceden yazılmış eşikle). **H0:** sabit çarpan ya da 1 (saf GR) yeterli; istatistik dalı değişmez.
- **Veri ve kör kuralı:** v1.3 fay grupları ve ≤2025 ISC/GCMT; ikisi de açılmış, sınav geliştirme düzeyinde, ön kayıt + birini dışarıda bırak. Türkiye dışı 2026'ya dokunulmaz. Marmara'ya uygulama v1.x rakibi olarak ileri test defterine.
- **İstanbul M7 beklenen katkısı:** istatistik dalı oranı (%12) için ilk dış kalibrasyon; v1.6'nın açamadığı kaynak. Orta.
- **Maliyet/süre:** 0 €, 4–5 gün.

### K2 · UCERF3 / SHERIFS ters çözümü: çürüyen moment dalının yerine
- **Kaynak:** Field ve diğ. 2014 (UCERF3), Page ve diğ. 2014 (büyük ters çözüm), Chartier 2017, 2019 (SHERIFS) ve **Chartier 2021 (SHERIFS Marmara, doğrudan öncül)**.
- **İstanbul'a taşıma:** moment dalımız tarihi üç yerden ıskaladı (15,5–21 beklenen / 9 gözlenen M≥7) ve ağırlığı 0,05. UCERF3'ün çözümü tam bu sorun için: kayma hızını çok segmentli kırılmalara dağıtıp toplam MFD'yi ve paleosismik oranları birlikte tutturmak. İki adım: (a) Chartier 2021'in yayımlanmış Marmara oranlarını defterde rakip olarak D4' + EPICA + 2016–25 tutarlılık satırlarıyla puanlamak; (b) SHERIFS'i 2026 girdileriyle yeniden kurmak: Y1b CMF 11 ± 3 mm/yıl, v1.8 kısmi kilit, v1.5 paleosismik oranlar kısıt olarak, S1 geçiş olasılıkları kırılma süzgeci olarak.
- **Boşluk:** ters çözüm × Marmara k 19; tek doğrudan öncül Chartier 2021, sınanmamış ve 2016+ kilitlenme verisinden önce. Ters çözüm × Marmara × sınama 1 (ilgisiz).
- **H1:** ters çözüm dalı tarihsel M≥7 sayısını moment dalından iyi tutuyor (tutarlılık satırında moment dalı − ters çözüm < 0, önceden yazılmış eşik) ve CMF+PIF+Ganos ortak kırılma oranlarını v1.7'den bağımsız veriyor. **H0:** ters çözüm de ıskalıyor ya da Parsons dalından ayırt edilemiyor.
- **Veri ve kör kuralı:** EDSF13, Y1b, v1.5, SHERIFS açık kaynak (Python). Kör veri yok, yalnız tutarlılık; v1.3b değişmez, sürüm rakip olur.
- **İstanbul M7 beklenen katkısı:** moment dalı (%14) ve segment birleşimi. Dal geçerse ağırlığı 0,05'ten büyüyebilir; dış verinin İstanbul'a ulaştığı tek kanal bu dal. Orta.
- **Maliyet/süre:** 0 € (mantık ağacı büyürse tek CPX ≈1 €, Erdem seçerse), 4–6 gün.
- **Çakışma:** yöntem kolunun D4'ü (SHERIFS + yeni kilit kanıtı) aynı iş. Ayrı açılmamalı; bu kolun eki D4'e iki şart: paleosismik oranlar kısıt olarak girsin ve dal moment dalının yerine geçebilir mi diye D4' + EPICA tutarlılık satırında sınansın.

### K3 · UCERF3-ETAS dersi: M6'dan sonra koşullu M7 olasılığı
- **Kaynak:** Field ve diğ. 2017 (UCERF3-ETAS; karakteristik MFD + elastik geri sekme olmadan tetiklenmiş büyük olay oranı yanlış), Field 2021 iyileştirmeleri, Savran 2020 (Ridgecrest sözde-ileriye dönük sınav).
- **İstanbul'a taşıma:** canlı ETAS'ımız GR; 23 Nisan 2025 M6,2 gibi bir CMF/PIF olayından sonra M7 olasılığını GR uzatmasıyla veriyor. Soru: büyük doğrultu atımlı fay üzerinde M≥5,95 olaydan sonra 1–365 gün içinde aynı fayda M≥6,95 oranı GR-ETAS'la mı, fayın karakteristik çarpanıyla büyütülmüş ETAS'la mı daha iyi tahmin ediliyor? Pozitif kontroller: Kumamoto 2016, Ridgecrest 2019, Kahramanmaraş 2023 (7,8 → 7,6).
- **Boşluk:** UCERF3-ETAS × Marmara k 4, hiçbiri Marmara işi değil; UCERF3-ETAS'ın tek sınavı Kaliforniya'da tek dizi. Marmara'daki tek kısa vade sınavı (Alhan 2026) M≥3,5.
- **H1:** karakteristik-ETAS − GR-ETAS > 0 nat (M≥6,95 hedefleri, ateşleme kapısıyla). **H0:** ayırt edilemez; canlı ETAS değişmez.
- **Veri ve kör kuralı:** küresel GCMT/ISC-GEM ≤2025 (açılmış). N muhtemelen 15–30 hedef: önce güç hesabı, yetmezse iş kapanır. K1'in çarpanını kullanır, K1'den sonra.
- **İstanbul M7 beklenen katkısı:** uzun vade aralığına yok; bir sonraki Marmara M5,5–6,5 sonrasında kısa vade M7 olasılığının dürüstlüğü (operasyonel). Düşük–orta.
- **Maliyet/süre:** 0 €, 4–6 gün.

### K4 · Sünen kesim bariyer mi? Kırılma uçlarının sünme geçişleriyle çakışması
- **Kaynak:** Harris 2017 (Rev. Geophys., büyük depremler ve sünen faylar), Chen ve Bürgmann 2017, Noda ve Lapusta 2013; San Andreas sünen kesimi 1857 ve 1906'nın uçlarında, Parkfield, Hayward, İsmetpaşa.
- **İstanbul'a taşıma:** Becker 2023'e göre orta ve batı CMF sünüyor, Ganos ve PIF kilitli; Güvercin–Barbot 2025 simülasyonu kalıcı bölünme diyor. S1'in sıçrama kuralına benzer bir "sünme geçişinde durma olasılığı" kuralı küresel kırılmalarda olasılıkla puanlanır, sonra Marmara kırılma uzunluğu ve Mw dağılımına (CMF doğusu + PIF mi, tüm Ana Marmara Fayı mı) taşınır.
- **Boşluk:** sünen × Marmara k 20 (betimsel ve simülasyon), sünen × sınama 10, üçlü 1 (ilgisiz). Harris 2017 nitel derleme; olasılık puanlaması yok.
- **H1:** kırılma uçları sünme geçişlerinde S1 taban durma oranından sık. **H0:** fark yok.
- **Uyarı:** S3'te 8 sünme haritasının hiçbiri D3 koridorlarına düşmedi; N büyük olasılıkla 8–15 uç. Önce 1 günlük sentetik güç testi (S6 gibi); eşik tutmazsa kapanır.
- **İstanbul M7 beklenen katkısı:** segment birleşimi ve Mw (S1'de PIF → CMF geçişi 0,21–0,85 arası geniş). Güç düşükse sıfır. Düşük–orta.
- **Maliyet/süre:** 0 €, güç testi 1 gün, sonra 4–5 gün.
- **Çakışma:** deniz tabanı kolunun 3. adayı (kilitlenme haritaları kırığın nerede duracağını söyledi mi) aynı soru, kilitlenme haritalarıyla. Ayrı açılmamalı; bu kolun eki oraya Kaliforniya olayları (1857 ve 1906'nın sünen kesim uçları, Parkfield 2004, Hayward) ve yüzey sünmesi ölçümleri.

### K5 · Hayward benzeri: kısmen sünen fayda moment dengesi tekrar aralığını veriyor mu?
- **Kaynak:** Lienkaemper ve diğ. 2010, 2012 (Hayward, 1900 yılda 12 olay; sünme hızı büyüklüğü ve sıklığı denetliyor), Chaussard 2015 (Hayward–Calaveras kenetlenme), Bürgmann 2000.
- **İstanbul'a taşıma:** jeodezik kenetlenme haritası ve paleosismik/tarihsel tekrarı birlikte olan kısmen sünen faylarda (Hayward, Calaveras, Parkfield, İsmetpaşa, Haiyuan, Longitudinal Valley) kenetlenmiş moment açığı gözlenen tekrarı tutuyor mu? Sünen faylar için ayrı c; CMF 11 ± 3 mm/yıl ile moment dalı ve v2.x simülatör yüklemesine.
- **Boşluk:** Hayward × Marmara k 10 (hepsi Türkiye'de sünme gözlemi; moment dengesi sınavı yok), Hayward × sınama 1.
- **H1:** sünen faylarda c, K4' bölgesel c ≈ 0,34'ten farklı ve tekrarı 2 kat içinde tutuyor. **H0:** fark yok; K4' yeterli.
- **İstanbul M7 beklenen katkısı:** v1.3b'de küçük (moment dalı); v2.x simülatör hattında CMF yüklemesi. Düşük. N ≈5–8 fay, derleme ağır.
- **Maliyet/süre:** 0 €, 1 hafta.

## Elenenler (neden)

- **CSEP Kaliforniya sonuçları / çarpımsal hibritle uzamsal ağırlık:** öncül güçlü (Rhoades 2014, Bayona 2020 küresel, Bayona 2022 Kaliforniya); GEAR1 zaten log-doğrusal hibrit ve v1.1'de en iyi uzamsal bileşen çıkmıştı; Kaliforniya 2011–25'te M≥6 ≈8 olay. İstanbul'un en büyük kaynağı uzamsal eksen (%46) Kaliforniya'dan yeni bilgiyle daralmıyor; dürüst sonuç bu.
- **RSQSim:** MCQsim hattı (v2–v2.4), S5 ABC kalibrasyonu ve Güvercin–Barbot 2025 aynı işi kapsıyor.
- **Parkfield / zaman bağımlılığı:** v1.3 (Poisson 0,95) kapattı.
- **Asismik geçiciler:** S7 kapattı.
- **Öncü şok trafik ışığı (Gulia ve Wiemer 2019):** tartışmalı (van der Elst 2020), M7 gücü yok; K3'ün bilgi satırı olabilir.
- **Sıçrama kuralları, CRS+ETAS, Bayesçi ETAS:** S1 ve bugünkü thread'ler yaptı.

## Önerilen sıra

Bu koldan ayrı açılacaklar üç: **K1 önce** (istatistik oranı %12'ye ilk dış kalibrasyon, yöntem kolunun D2 hiyerarşik havuzlamasıyla aynı paya farklı yoldan dokunuyor, birlikte koşulabilir), **K3** K1'in çarpanını kullandığı için ondan sonra, **K5** boşta. K2 yöntem kolunun D4'üne, K4 deniz tabanı kolunun 3. adayına ek olarak verilir. Her biri ön kayıtla başlar, sonuç ileri test defterine rakip olarak girer, v1.3b değişmez.

## Sınır

Tohum seçimi sonucu belirler; kesişim boşluğu gösterir, nedenini göstermez. OpenAlex 2025–26 atıflarını eksik sayabilir. Öncüller başlık ve özetle okundu, tam metin değil. Kör veri (Türkiye dışı 2026) okunmadı.
