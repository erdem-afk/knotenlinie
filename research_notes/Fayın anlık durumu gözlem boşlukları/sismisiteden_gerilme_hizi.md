# Sismisite "gerilme ölçer" olarak: hız-durum gerilme hızı ters çözümü, doğrultu atımlı tremor/LFE, ETAS arka plan geçicileri — Marmara için sınanmış zaman terimi var mı?

Hazırlayan: araştırma kolu, 11 Kasım 2026. Kaynak: OpenAlex (`kayit/oa.py`), EMSC FDSN olay servisi (sayım), proje defteri (`kayit/kayit.py`). Tam metinlerin çoğu okunmadı; çoğu bulgu özetlerden. Özeti olmayan Nature makalelerinde (Dieterich 2000, Toda 2002, Segall 2006) yalnız başlık ve künye kullanıldı; "tam metin okunamadı".
Köprü dosyaları: `/home/user/knotenlinie/kayit/turetme/kopru/gerilme_hizi/tohumlar.json`, `kopru_rapor.json`.

Kısa hüküm: Üç ölçüden **hiçbiri**, kilitli bir fay segmentinin anlık yüklenme durumunu izleyip büyük deprem olasılığını zamanla değiştiren, **ileriye dönük puanlanmış (CSEP türü) bir terim vermiyor**. Büyük olaydan önceki bütün "yakalama" örnekleri geriye dönük ve tek olaylık. Kanıtlanmadı. Marmara'da/KAF'ta tektonik tremor ya da LFE gözlemi yayımlanmamış. Merkezî KAF'taki tek sistematik arama (Pfohl 2015) olumsuz. ETAS arka plan hızı μ(t) kolu (A3), projede kapanmış ETAS-TABAN, S-7 ve EL-1 adaylarından ayrışmıyor. Bu yüzden önerilmedi. 0 € ile sınanabilir iki aday var. Biri gerilme ölçerin Marmara'daki jeodezik geçicilerle doğrulanması (GH-1), öteki Marmara'da tetiklenmiş tremor varlık taraması (GH-2). İkisinin de yıl ölçeğine bağı dolaylı. İkisi de olasılık terimi değil, "yeni gözlem türü var mı" kapısı.

---

## 1. Sismisite hızından gerilme hızı ters çözümü (A1) büyük olaydan ÖNCE yüklenme değişimi yakalamış mı? Marmara'da çözünürlük ne?

### Takeaway
Hız-durum (Dieterich 1994) ters çözümü volkanik ve yapay yüklemelerde (Kilauea, Izu 2000, Reno-Mogul 2008) gerilme hızı geçicilerini geriye dönük olarak buluyor. Büyük tektonik olaydan önce bulunan örnekler de geriye dönük ve tek olaylık: Tokachi-oki 2003 göreli sessizliği, Tohoku öncesi Ocak–Şubat 2011 geçicisi, Reno-Mogul M5.1 öncesi 3 günlük yüklenme. Bunlardan hiçbiri önceden kayda alınıp puanlanmadı. Kaba hesaba göre Marmara'da segment başına yılda ≈20–80 M≥2 olayla, bir yıllık pencerede ancak ≈%30–100'lük gerilme hızı değişimi ya da ≈0,45·Aσ (≈5–20 kPa) büyüklüğünde bir gerilme basamağı görülebilir. Bu, kilitli segmentin ≈0,5–2 yıllık tektonik yüklemesine denk düşer.

### Cited Findings
**Yöntemin temeli**
- Dieterich (1994) sismisite üretim hızı ile gerilme geçmişini bağlayan yasayı kurdu. Heimisson & Segall (2018) bu yasayı keyfi gerilme geçmişlerine genelleştirdi — [Dieterich 1994, 10.1029/93jb02581](https://doi.org/10.1029/93jb02581); [Heimisson & Segall 2018, 10.1029/2018jb015656](https://doi.org/10.1029/2018jb015656)
- Dieterich, Cayol & Okubo (2000), Kilauea'da deprem hızı değişimlerini "gerilme ölçer" olarak kullandı. Tam metin okunamadı; OpenAlex'te özet yok, 228 atıf — [10.1038/35044054](https://doi.org/10.1038/35044054)
- Toda ve ark. (2002): Izu adaları 2000 deprem fırtınası, "sismisiteyi gerilme hızı yönetir" kanıtı olarak sunuldu. Tam metin okunamadı, 416 atıf — [10.1038/nature00997](https://doi.org/10.1038/nature00997)
- Segall ve ark. (2006): Kilauea'da sessiz kayma olaylarının tetiklediği depremler. Tam metin okunamadı — [10.1038/nature04938](https://doi.org/10.1038/nature04938)
- Llenos & McGuire (2011) ETAS ile hız-durum modelini tek bir veri özümleme modelinde birleştirdi. Salton Trough'da 1990–2009 M≥1,5 kataloğundan gerilme hızını ters çözdüler. Sonucu Obsidian Buttes sünme olayının jeodezik modeliyle doğruladılar. Gerilme hızının mutlak büyüklüğünü ancak "kabaca" (roughly) kısıtladıklarını yazıyorlar — [10.1029/2010jb007537](https://doi.org/10.1029/2010jb007537)
- Jiang, Trugman & González (2026, JGR) sismisiteden gerilme hızı evrimini çıkaran Bayesçi bir ters çözüm aracı (T-rate) kurdu. Reno-Mogul 2008 fırtınasında M5.1'den 3 gün önce başlayan bir yüklenme evresi buldular; evreyi GPS bağımsız olarak destekliyor. Ayrıca şunu yazıyorlar: "zamanlama görece kararlı, ama gerilme genliği varsayılan arka plan hızı r'ye **güçlü biçimde bağlı**" — [10.1029/2026jb033922](https://doi.org/10.1029/2026jb033922); kod [10.5281/zenodo.20251771](https://doi.org/10.5281/zenodo.20251771)

**Büyük olaydan önce "yakalama" örnekleri (hepsi geriye dönük)**
- Ogata (2005, Tokachi-oki M8.0, 2003): 1996'da üç artçı dizisinde ve kıta içi sismisitede ETAS'tan eşzamanlı sapmalar bulundu. Bunlar levha arayüzünde varsayılan asismik kaymanın ΔCFS'siyle açıklandı. 1926–2003 M≥5 verisinde 1952 ve 1968 Tokachi-oki depremlerinden önce de ≈10 yıllık göreli sessizlik bildirildi. Yöntem geriye dönük; olasılık puanı verilmedi — [10.1029/2004jb003323](https://doi.org/10.1029/2004jb003323)
- Ogata (2005b), ETAS'tan sapmayı (sessizlik/etkinleşme) "gerilme değişimi algılayıcısı" olarak tanımladı. Yazar güçlü depremlerden önceki hız düşüşlerini de asismik kaymayla yorumluyor; bu yorum bir varsayıma dayanıyor — [10.1029/2004jb003245](https://doi.org/10.1029/2004jb003245)
- Marsan ve ark. (2013b), Japonya 1990–2011 (Tohoku öncesi) için birkaç anlamlı asismik geçici buldu. Ibaraki açığında en güçlü dört geçici ≈5,9 yılda bir yinelendi. Ocak–Şubat 2011'de Tohoku merkezi yakınındaki sismisite asismik yüklemeye bağlandı. Ancak yazarlar bu geçicinin "dönemin ne en şiddetlisi ne en anlamlısı" olduğunu belirtiyor. Yani ileriye dönük bir alarm olarak ayırt edici değildi — [10.1002/jgrb.50323](https://doi.org/10.1002/jgrb.50323)
- Jiang ve ark. (2026): Reno-Mogul M5.1 öncesi 3 günlük yüklenme (yukarıda). Tek olay ve geriye dönük — [10.1029/2026jb033922](https://doi.org/10.1029/2026jb033922)
- Rundle ve ark. (2011), Kaliforniya–Nevada'da 25 yıllık geriye dönük sınamada M>6 öncesinde "sessizlik" modelini "etkinleşme" modelinden iyi buldu. Fark küçüktü ve "anlamlı değildi" — [10.1111/j.1365-246x.2011.05134.x](https://doi.org/10.1111/j.1365-246x.2011.05134.x)

**Marmara'da sismisite hızı ile gerilme ilişkisi**
- Doğu Marmara'da 1999 İzmit sonrası dört öncül kümede uzun süreli hız değişimleri görüldü. Statik Coulomb artışı olan genişleme kümeleri 10 yıldan uzun süre etkin kaldı ve klasik Omori azalmasına uymadı. Bu, bilinen bir gerilme basamağına verilen yanıttır; olay öncesi bir gözlem değildir — [10.1002/jgrb.50077](https://doi.org/10.1002/jgrb.50077)
- Batı Marmara'da 27 Kasım 2013 Mw 4,6 dizisinden önce, tekrarlayan depremlerin bulunduğu bölgede çok benzer olaylar (multiplet) görüldü. Bunlar aylarca süren, batıya ≈0,5 km/gün ilerleyen olası bir yavaş kayma olayıyla eşzamanlı. Yavaş kaymanın ana şoka aktardığı Coulomb gerilmesi yalnız "birkaç onda bir kPa" — [Tary ve ark. 2026, 10.1093/gji/ggag429](https://doi.org/10.1093/gji/ggag429)
- Armutlu yarımadasında ≈1 yıllık yüksek çözünürlüklü katalogda, jeodezik yavaş kayma geçicisi sönerken kümelenmiş olay payı arttı ve b-değeri düştü — [10.1029/2022gl099077](https://doi.org/10.1029/2022gl099077)
- İzmit segmentinde InSAR'la 2015, 2016, 2018 (Mw 4,3) ve 2019 (Mw 4,4) yavaş kayma olayları belirlendi. Bunlar 2–5 km derinlikteki sürekli sünmenin üstünde, sığ derinlikte — [10.1016/j.epsl.2024.119104](https://doi.org/10.1016/j.epsl.2024.119104)
- 2016–2023 arasında altı M_L 4,0–5,8 dizisi kuyu ve yüzey verisiyle derin öğrenme kullanılarak yeniden işlendi. Kuyu dizilerinin çevresinde ≈8 kat fazla olay bulundu. 2016 Çınarcık M_L 4,5 öncesinde dalga biçimi benzerliği arttı ve olaylar arası uzaklık azaldı — [10.1029/2026jb034241](https://doi.org/10.1029/2026jb034241)

**Marmara katalog sayımı (bu kol, EMSC FDSN, 40,4–41,1 K, 27,0–29,6 D, 2010–2025; ham sayım, kümeler ayıklanmadı, kutu kıyı ve kara kesimlerini de içerir)** — [EMSC seismicportal FDSN](https://www.seismicportal.eu/fdsnws/event/1/)
- Büyüklük modu: 2010–2014'te 2,6, 2015–2025'te 2,0. EMSC birleşik kataloğu homojen değil.
- M≥2,0, 2010–2025, yıllık medyan: Ganos/batı (27,0–27,8 D) 57,5; Orta/Kumburgaz (27,8–28,6 D) 51; Çınarcık/PIF (28,6–29,6 D) 79. Yıldan yıla 21–532 arası değişiyor (2019 Silivri, 2025 M6,2 dizileri).
- M≥3,0, yıllık medyan: 7 / 7,5 / 10.
- Projedeki AV-2 kaydı: ComCat M≥3,95, 2012–2025 için 66 olay. Etkin N ≈15 (kayıt: `kayit/kollar/AV.md`).

### Inferences
- **Kaba çözünürlük (bu kolun hesabı, doğrulanmadı):** Hız-durumda kalıcı durumda R ∝ τ̇. Bir pencerede N₂ arka plan olayı varsa ln r'nin standart hatası ≈1/√N₂ (taban süresi uzun kabul edildi). Kümelenme ayıklanınca arka plan payı ≈%30–50 kabul edilirse segment başına yılda N₂ ≈15–40 olur. Bu durumda 2σ'da saptanabilir hız çarpanı r ≈1,4–1,7 çıkar. Artık kümelenmeden gelen aşırı saçılım (SE ×1,5) eklenirse r ≈1,6–2,0 olur. Yani **bir yıllık pencerede ≈%40–100'lük gerilme hızı değişimi** gerekir.
- Gerilme basamağı eşdeğeri Δτ = Aσ·ln r ≈0,45–0,7·Aσ. Aσ ≈0,01–0,04 MPa varsayılırsa (literatür aralığı; Marmara için ölçülmedi, varsayım) bu **≈5–25 kPa** eder. Kilitli Marmara segmentinin tektonik yükleme hızı kabaca ≈10 kPa/yıl kabul edilirse (varsayım), görülebilen değişim ≈0,5–2 yıllık yüklemeye eşit. Görülebilmesi de t_a = Aσ/τ̇ ≈1–4 yıl gerektirir. Yöntem, Tary 2026'daki 0,1–0,5 kPa'lık yavaş kayma gerilmelerini **göremez**.
- Arka plan hızı r'ye güçlü bağımlılık (Jiang 2026) ve EMSC'deki Mc kaymaları birlikte düşünülürse, mutlak gerilme hızı Marmara'da kataloğun homojenliğinden daha iyi çözülemez.
- **Projeye çevirisi:** VE-3 formülüne göre beklenen kazanç ≈λT(r−1)²/2. Marmara M≥6 için λ ≈0,05/yıl alınırsa (kaba, tarihsel) ve r=1,5, T=1 yıl ise kazanç ≈0,006 nat/yıl olur. Bu, FA-1 tavanı (10 yılda 0,016 nat) düzeyindedir. Gerilme ölçer kusursuz çalışsa bile, gördüğü büyüklükteki değişimler M6+ olasılığını yıl ölçeğinde ancak %50 kadar oynatır.

### Gaps
- Marmara'da sismisite hızından gerilme hızı ters çözümü (Dieterich/Heimisson–Segall/Llenos/T-rate) yapan bir çalışma bulunamadı. OpenAlex "Marmara + rate-state stressing rate" aramaları bunu döndürmedi. Ancak bulunamamış olması yapılmadığını kanıtlamaz.
- GFZ homojen katalog 2006–2023'ün DOI'si ve Mc'si bu turda doğrulanmadı (AV.md'deki "Mc ≈2,1" değeri doğrulanmadı). KOERI kataloğu için segment bazında sayım yapılmadı.
- Dieterich 2000, Toda 2002 ve Segall 2006'nın sayısal sonuçları okunmadı (özet yok, açık erişim yok).

---

## 2. KAF/Marmara'da tektonik tremor ya da LFE var mı? Doğrultu atımlı faylarda tremor değişimi ile sonraki M6+ arasında çok olaylı bir sınav var mı?

### Takeaway
Marmara'da ya da batı KAF'ta tektonik tremor/LFE gözlemi **yayımlanmamış**; bulunamadı. Merkezî KAF'taki iki yıllık özel ağ taraması (Pfohl 2015) hem tetiklenmiş hem ortam tremoru için olumsuz sonuç verdi. Doğrultu atımlı faylarda "tremor hızı → sonraki M6+" ilişkisinin tek örneği Parkfield 2004. Shelly (2009) bu olaydan önceki 3 ayda tek yönlü göç ve yüksek tremor hızı buldu, ama kendisi "belirgin kısa vadeli öncü yok" diye yazıyor. Çok olaylı bir sınav **yok**.

### Cited Findings
- Pfohl ve ark. (2015): Merkezî KAF'ta ≈400 km'lik segment, iki yıllık geçici geniş bant ağ. Bölgesel ve uzak depremlerin yüzey dalgalarıyla **tetiklenmiş tremor gözlenmedi**. Ortam tremoruna benzeyen sinyaller istasyonlar arasında tutarlı değildi. Hüküm: "kesin tremor bölümü belirleyemiyoruz… tremor varsa SAF ya da Alpine'den daha düşük genlikte/hızda" — [10.1785/0120140312](https://doi.org/10.1785/0120140312)
- Marmara'da tremor/LFE yayını bulunamadı. Aramalar: "tectonic tremor North Anatolian Fault", "triggered tremor North Anatolian", Marmara OBS mikrosismisite. OBS çalışmaları ([10.1029/2008jb006244](https://doi.org/10.1029/2008jb006244), [10.1785/0120170258](https://doi.org/10.1785/0120170258), [10.1186/s40623-015-0325-9](https://doi.org/10.1186/s40623-015-0325-9), [10.1029/2019gc008349](https://doi.org/10.1029/2019gc008349)) mikrodepremleri ve sismik olmayan deniz tabanı sinyallerini konu alıyor. Hiçbirinin özetinde tremor/LFE bildirimi yok. Tam metinler okunmadı.
- Yakın bölgede olumlu bir örnek var: 2023 Kahramanmaraş Mw 7,6, Ölü Deniz Transformu'nda uzaktan tremor tetikledi — [10.1038/s43247-024-01266-1](https://doi.org/10.1038/s43247-024-01266-1). Doğu Akdeniz'de derin tremor da tartışılmış — [10.1029/2020jb020448](https://doi.org/10.1029/2020jb020448)
- **Parkfield:** Shelly (2009), 2001 ortası–2008 tremor kaydını inceledi. 2004 M6.0'dan önceki 3 ayda tek yönlü göç ve yükselmiş tremor hızı buldu; bunu ≈16 km derinde hızlanmış sünme olarak yorumladı. Yine de "belirgin kısa vadeli öncü yok" — [10.1029/2009gl039589](https://doi.org/10.1029/2009gl039589)
- Nadeau & Guilhem (2009): San Simeon 2003 ve Parkfield 2004'ten sonra tremor hızı arttı ve periyodikleşti. Bu artış 6–14 kPa statik kesme ve Coulomb artışıyla çakışıyor. Değişim 4 yıldan uzun sürdü; yazarlar bunu "1857 Ft. Tejon kırığının altında gerilme daha hızlı birikiyor" diye yorumladı. Bu yorum ileriye dönük bir olasılık sınamasına girmedi — [10.1126/science.1174155](https://doi.org/10.1126/science.1174155)
- Shelly (2017): 2001–2016 dönemi, 88 aile, >1 milyon LFE, SAF boyunca ≈150 km, 16–30 km derinlik. Katalog makalenin ekinde açık — [10.1002/2017jb014047](https://doi.org/10.1002/2017jb014047)
- Thomas ve ark. (2018): Epizodik LFE aileleri "derin sünme ölçer" olarak kullanılabiliyor, yavaş kayma olayları uzun vadeli hızın ≈16 katı kayıyor. Sürekli aileler ve kısa patlamalar sünmeyi doğrudan ölçmüyor — [10.1002/2017jb014404](https://doi.org/10.1002/2017jb014404)
- Zali, Martínez-Garzón, Mencin & Beroza (2026, Nat Commun): Parkfield'da derin öğrenmeyle gerinim ölçer verisinden kısa süreli yavaş kayma olayları yakaladılar; LFE'ler bu olaylardan sonra artıyor. "Komşu kilitli alanlarda gerilmeyi bozabilir" ifadesi bir olasılık önerisi, sınanmadı. Bu yayın Parkfield'ın geçmiş verisine dayanıyor; 2026 depremi içermiyor — [10.1038/s41467-026-74095-9](https://doi.org/10.1038/s41467-026-74095-9)
- Merkezî KAF'ta (İsmetpaşa) 31 günlük, en çok 2 cm'lik sığ (0–4 km) asismik kayma patlaması görüldü — [10.1002/2016gl068250](https://doi.org/10.1002/2016gl068250). Bu jeodezik bir gözlem; tremorla ilişkisi bildirilmedi.

### Inferences
- Doğrultu atımlı faylarda tremor/LFE'nin derin kaymayı izlediği gösterildi (SAF). Ancak "tremor hızı → büyük deprem olasılığı" iddiası **tek olaya (Parkfield 2004) dayanıyor ve kanıtlanmadı**. Tremor bulunan doğrultu atımlı faylarda (SAF Parkfield–Cholame, Alpine, San Jacinto) 2001'den beri yalnız bir M6+ olay tremor kataloğunun içine düştü. İstatistiksel sınav için gereken onlarca hedef olay yok.
- Marmara için A2 kolunun ön koşulu "tremor var mı?" sorusu, ve bu soru açık. Pfohl'un olumsuz sonucu merkezî KAF'a ve yüzey istasyonlarına ait. GONAF kuyu sismometreleri ([10.5194/sd-22-19-2017](https://doi.org/10.5194/sd-22-19-2017)) ve kuyu ile derin öğrenme hattı ([10.1029/2026jb034241](https://doi.org/10.1029/2026jb034241)) gürültü tabanını düşürdüğü için Marmara'da tremor aranmamış olması gerçek bir boşluk. Fakat beklenti düşük: KAF'ın derin kökü bilinen tremor kuşaklarından daha kuru ve soğuk olabilir. Bu bir varsayım, doğrulanmadı.

### Gaps
- Marmara'da tremor taraması yapılıp olumsuz sonuç alınmış ama yayımlanmamış olabilir; bilinmiyor. 2012 tarihli "Searching for Tectonic Tremor on the North Anatolian Fault" kaydının DOI'si yok, muhtemelen bir AGU özeti; okunamadı.
- KOERI (KO) ve GONAF dalga biçimlerine erişim: AV.md'de "KOERI sürekli dalga formu 2011+ açık" kaydı var. GONAF kuyu verisinin açıklığı bu turda doğrulanmadı.

---

## 3. ETAS arka plan hızı μ(t) (yavaş kayma, akışkan, yüklenme) Marmara'da incelenmiş mi? Öneri ETAS-TABAN'dan ayrışıyor mu?

### Takeaway
μ(t) yöntemleri (Hainzl & Ogata 2005, Llenos & McGuire 2011, Marsan 2013, Kumazawa & Ogata 2014, Kattamanchi 2017) olgunlaşmış durumda. Ancak yalnız akışkan, fırtına ve yavaş kayma tanılamasında kullanılıyor, ileriye dönük bir büyük deprem olasılık terimi olarak sınanmamış. Marmara'ya özel bir μ(t) çalışması bulunamadı. Bu kolun tahmine katkısı, kapalı ETAS-TABAN (zaman ağırlıklı arka plan, +0,014 ± 0,035) ile S-7/EL-1'in (asismik geçici → olasılık, IG −0,06 ± 0,12) birleşimine **ayrışmadan denk düşüyor. Önerilmez.**

### Cited Findings
- Hainzl & Ogata (2005): istatistiksel deprem modellemesiyle sismisitede akışkan sinyali saptama, 322 atıf — [10.1029/2004jb003247](https://doi.org/10.1029/2004jb003247)
- Marsan, Reverso, Helmstetter & Enescu (2013): Olaylar arası süre istatistikleri zorlama değişimlerini sönümlüyor. Etkileşimli tetiklenme modeline göre yapılan karşılaştırma yüklenme hızı değişimlerini süre ve şiddetiyle "iyi geri kazanıyor" (sentetik ve gerçek) — [10.1785/0120110304](https://doi.org/10.1785/0120110304)
- Kumazawa & Ogata (2014): durağan olmayan ETAS — [10.1214/14-aoas759](https://doi.org/10.1214/14-aoas759). Kumazawa & Ogata (2013): Tohoku öncesi ve sonrası, durağan olmayan ETAS — [10.1002/2013jb010259](https://doi.org/10.1002/2013jb010259)
- Kattamanchi ve ark. (2017): B-spline ile μ(t) kestiren durağan olmayan ETAS; Hikurangi'de yavaş kaymayla ilişkili fırtınalar — [10.1186/s40623-017-0741-0](https://doi.org/10.1186/s40623-017-0741-0)
- Muir & Ross (2023): arka plan hızı için derin Gauss süreci — [10.1093/gji/ggad074](https://doi.org/10.1093/gji/ggad074)
- Marmara'daki yakın çalışmalar: tekrarlayan depremlerden sünme hızı ([Uchida ve ark. 2019, 10.1016/j.tecto.2019.228185](https://doi.org/10.1016/j.tecto.2019.228185): 21 tekrarlayan olay, 9 dizi, 3–4 cm/yıl; [GRL 2023 (yazarlar bu turda okunmadı; Becker ve ark. olduğu doğrulanmadı), 10.1029/2022gl101471](https://doi.org/10.1029/2022gl101471): 15 yıllık katalogda sünme orta ve batı MMF'de en çok, Ganos ve Adalar'a doğru azalıyor). Sismik kenetlenme oranının 1999 öncesi ve sonrası zamanla değiştiği de bildirildi ([10.1093/gji/ggad341](https://doi.org/10.1093/gji/ggad341)). Hiçbiri μ(t) tahmin terimi değil.
- Proje defteri: ETAS-TABAN "Taban +0,127 ± 0,031; tetik3 +0,014 ± 0,035, S testi yine başarısız; yeniden açma şartı: kapalı (8 Kasım, 1698a7f1)". S-7 "IG −0,06 ± 0,12 nat (N 30)". VE-3 "r=1,1'de olay başına 0,005 nat" (`python3 kayit/kayit.py ara`).

### Inferences
- A3'ün tahmine sokulabilecek tek biçimi "son dönem arka plan hızı yüksekse büyük olay olasılığını çarp" olur. ETAS-TABAN zaman ağırlıklı arka planla bunu zaten denedi ve H0 çıktı. μ(t)'yi asismik geçiciye bağlamak ise S-7/EL-3/TK-E1'in çarpan sorusu. **Ayrışmıyor, önerilmedi.**
- A3'ün kalan tek meşru kullanımı A1 ile aynı: gerilme ölçeri bağımsız jeodeziyle doğrulamak (bkz. GH-1).

### Gaps
- Marmara'da μ(t) kestirimi bulunamadı (OpenAlex A3 × MARMARA kesişiminde Marmara'ya özgü tek iş Armutlu 2022 oldu; o da b-değeri ve küme payı çalışması).

---

## 4. Köprü ölçümü (A1, A2, A3 × B; kontroller; × Marmara)

### Takeaway
Gerilme ölçer literatürü tahmin sınama literatürüne zayıf bağlı: A1 × B J=0,024, A3 × B J=0,030. Pozitif kontrolün (ETAS × B, J=0,060) kabaca yarısı. Tremor/LFE (A2) sınama literatürüyle neredeyse bağsız: k=3, J=0,003, kontrolün ≈1/20'si. A1 × B kesişimindeki işlerin çoğu Coulomb tabanlı artçı tahmini (CRS) ve indüklenmiş sismisite. Sismisiteden ters çözülmüş gerilme hızını ileriye dönük puanlayan bir iş kesişimde görünmüyor. Marmara üçlü kesişimi (A1 × B × MARMARA) k=4, J=0,001.

### Cited Findings
Tohumlar: A1 = Dieterich 1994, Dieterich 2000, Toda 2002, Segall 2006, Heimisson–Segall 2018, Llenos–McGuire 2011; A2 = Shelly 2009, Nadeau–Guilhem 2009, Shelly 2017, Thomas 2018, Nadeau–Dolenc 2005 ([10.1126/science.1107142](https://doi.org/10.1126/science.1107142)), Veedu–Barbot 2016 ([10.1038/nature17190](https://doi.org/10.1038/nature17190)); A3 = Marsan 2013a/b, Ogata 2005a/b, Kumazawa–Ogata 2014, Hainzl–Ogata 2005; B = Schorlemmer 2007 ([10.1785/gssrl.78.1.17](https://doi.org/10.1785/gssrl.78.1.17)), Zechar 2010 ([10.1785/0120090192](https://doi.org/10.1785/0120090192)), Rhoades 2011 ([10.2478/s11600-011-0013-5](https://doi.org/10.2478/s11600-011-0013-5); görevde verilen 10.1007/… OpenAlex'te bulunamadı, bu DOI kullanıldı), Bird 2015 GEAR1 ([10.1785/0120150058](https://doi.org/10.1785/0120150058)); KONTROL (ETAS) = Ogata 1988 ([10.1080/01621459.1988.10478560](https://doi.org/10.1080/01621459.1988.10478560)), Ogata 1998, Zhuang 2002; COULOMB = King–Stein–Lin 1994 ([10.1785/bssa0840030935](https://doi.org/10.1785/bssa0840030935)), Stein 1999 ([10.1038/45144](https://doi.org/10.1038/45144)), Toda 2005; MARMARA = Bohnhoff 2013 ([10.1038/ncomms2999](https://doi.org/10.1038/ncomms2999)), Ergintav 2014 ([10.1002/2014gl060985](https://doi.org/10.1002/2014gl060985)), Marmara sünme 2023 ([10.1029/2022gl101471](https://doi.org/10.1029/2022gl101471)), Hergert–Heidbach 2010 ([10.1038/ngeo739](https://doi.org/10.1038/ngeo739)), Parsons 2000 ([10.1126/science.288.5466.661](https://doi.org/10.1126/science.288.5466.661)). Kaynak: `kayit/turetme/kopru/gerilme_hizi/kopru_rapor.json`. Ölçüm tarihi 11 Kasım 2026.

| Köprü | küme boyları (atıf yapan) | k | J |
|---|---|---|---|
| A1 × B | 2077 / 503 | 61 | 0,0242 |
| A2 × B | 582 / 503 | 3 | 0,0028 |
| A3 × B | 497 / 503 | 29 | 0,0299 |
| **pozitif kontrol ETAS × B** | 3174 / 503 | 208 | 0,0600 |
| **pozitif kontrol A1 × COULOMB** | 2077 / 3855 | 661 | 0,1254 |
| A1 × MARMARA | 2077 / 844 | 84 | 0,0296 |
| A2 × MARMARA | 582 / 844 | 17 (≈5 etkin) | 0,0121 |
| A3 × MARMARA | 497 / 844 | 6 | 0,0045 |
| COULOMB × MARMARA (karşılaştırma) | 3855 / 844 | 155 | 0,0341 |
| A1 × B × MARMARA | 2077 / 503 / 844 | 4 | 0,0012 |

- A2 × B'nin 3 işi: Chaman InSAR tezi, Parkfield LFE ile yavaş kayma ([10.1016/j.epsl.2017.07.032](https://doi.org/10.1016/j.epsl.2017.07.032)), OEF rehberi ([10.4401/ag-5350](https://doi.org/10.4401/ag-5350)). Hiçbiri tremoru tahmine sokup puanlamıyor.
- A2 × MARMARA'nın 17 işinin 13'ü Scholz, "The Mechanics of Earthquakes and Faulting" (2018) kitabının bölümleri ([10.1017/9781316681473](https://doi.org/10.1017/9781316681473)). Etkin k ≈4–5: MMF reoloji 2026, NFO Avrupa 2022, OEF 2011, kitap.
- A3 × MARMARA'nın 6 işinden Marmara/KAF'a ait olanlar: Armutlu yavaş kayma 2022 ([10.1029/2022gl099077](https://doi.org/10.1029/2022gl099077)) ve Düzce'nin İzmit artçılarını bozması 2006 ([10.1029/2005jb003978](https://doi.org/10.1029/2005jb003978)).
- A1 × B × MARMARA'nın 4 işi: indüklenmiş sismisitede artçı süresi 2023, Gorkha ileriye dönük tahmin 2016 ([10.1785/0220150195](https://doi.org/10.1785/0220150195)), hibrit Coulomb/istatistik artçı modeli 2013 ([10.1093/gji/ggt404](https://doi.org/10.1093/gji/ggt404)), OEF 2011. Marmara'da gerilme hızı tahmini sınayan bir iş yok.

### Inferences
- A1 ve A3'ün J değeri kontrolün ≈%40–50'si. Bu "bilinmeyen boşluk" değil, "seyrek ama var olan köprü" demek. Kesişimdeki işler ise Coulomb artçı tahmini (CRS), proje bunu CRS-ETAS/KURESEL-CRS-GELGIT olarak zaten kapattı. Sismisiteden ters çözülmüş gerilme hızının ileriye dönük puanlanması gerçek boşluk olarak kalıyor, ama ölçü bunu doğrudan göstermiyor (kesişim konu ayrımı yapmıyor).
- A2 × B ≈ kontrolün 1/20'si. Tremor/LFE ile tahmin sınama arasındaki boşluk büyük ve gerçek. Nedeni büyük ölçüde fiziksel: tremorlu doğrultu atımlı faylarda hedef olay neredeyse yok.

### Gaps
- Köprü ölçüsü konu ayrımı yapmıyor. A1 × B'deki 61 işin hangisinin "sismisiteden gerilme hızı → tahmin" olduğu tek tek okunmadı; yalnız başlıklar tarandı.

---

## 5. 0 € sınama taslağı ve aday önerileri

### Takeaway
Doğrudan bir "M6+ olasılık terimi" sınaması Marmara'da güçsüz. Sınama penceresinde M6+ hedef ≈0–1, M≥4 hedefi için etkin N ≈15 (AV-2). Bu yüzden iki kapı adayı öneriliyor; ikisi de **olasılık terimi değil, yeni gözlem türünün varlık ve doğrulama sınaması**. GH-1, sismisiteden çıkan gerilme ölçerin Marmara'daki bilinen jeodezik ve gerilme olaylarını geri kazanıp kazanmadığını sınar. GH-2, Marmara/batı KAF'ta tetiklenmiş tremor varlığını tarar. Üçüncü bir aday (A3 μ(t) çarpanı ya da tremor → M6+) kapalı adaylardan ayrışmadığı ya da tek olaya dayandığı için önerilmedi.

### Cited Findings
- Hedef ve sayımlar: Marmara M≥3,95 2012–2025: 66 olay; sınama penceresinde etkin N ≈15; TK-1 etkin N ≈40 ile 0,45 nat altını göremedi (AV-2 kaydı, `kayit/kollar/AV.md`). EMSC M≥3,0 segment medyanı 7–10/yıl (bu kol, yukarıda).
- Geri kazanılması gereken bağımsız olaylar (jeodezik/fiziksel "doğru cevap"): İzmit yavaş kaymaları 2015, 2016, 2018-03, 2019-11 ([10.1016/j.epsl.2024.119104](https://doi.org/10.1016/j.epsl.2024.119104)); Armutlu geçicisi ([10.1029/2022gl099077](https://doi.org/10.1029/2022gl099077)); batı Marmara 2013 olası yavaş kayması ([10.1093/gji/ggag429](https://doi.org/10.1093/gji/ggag429)); 1999 İzmit sonrası doğu Marmara uzun süreli etkinleşme, bilinen gerilme basamağı ([10.1002/jgrb.50077](https://doi.org/10.1002/jgrb.50077)).
- Araç: T-rate açık kod ([10.5281/zenodo.20251771](https://doi.org/10.5281/zenodo.20251771)); Llenos–McGuire yöntemi ([10.1029/2010jb007537](https://doi.org/10.1029/2010jb007537)).
- Tremor tetikleyici analog: Kahramanmaraş 2023'ün Ölü Deniz Transformu'nda tremor tetiklemesi ([10.1038/s43247-024-01266-1](https://doi.org/10.1038/s43247-024-01266-1)); merkezî KAF'ta olumsuz sonuç ([10.1785/0120140312](https://doi.org/10.1785/0120140312)).

### Inferences — aday taslakları

**GH-1: Sismisite gerilme ölçerinin Marmara'da kör doğrulanması**
- Soru: T-rate ya da Heimisson–Segall ters çözümü, bağımsız olarak tarihlenmiş 5–6 Marmara geçicisini (İzmit 2015, 2016, 2018, 2019; Armutlu; batı Marmara 2013) ve bilinen 1999 sonrası gerilme basamağını rastgele zamanlı sahte olaylardan (yer değiştirme sınaması) ayırt edebiliyor mu?
- Ön kayıt: Geçici takvimi, Aσ aralığı ve r kestirimi ters çözümden önce dondurulur. Ölçü, ters çözülmüş τ̇ tepelerinin jeodezik pencerelere ±30 gün içinde düşme oranıdır; 1000 rastgele takvime karşı p değeri hesaplanır.
- Veri: GFZ homojen katalog 2006–2023 (AV.md'de "açık"), KOERI zeqdb, EMSC FDSN. Tümü 0 €.
- Hedef sayısı: 5–7 geçici. Kaba güç: Segment başına ±30 günlük pencerede ≈2–7 M≥2 olay beklenir. Çözünürlük hesabına göre Mw 4,3–4,4 sığ yavaş kaymanın yarattığı ≲1 kPa'lık gerilme görülemez. **Beklenen sonuç büyük olasılıkla H0.** 1999 pozitif kontrolü (MPa ölçeğinde basamak) geçmezse yöntem Marmara kataloğunda çalışmıyor demektir.
- Ayrım: S-7/EL-1/TK-E1/EL-3, geçicilerin büyük deprem olasılığını çarpıp çarpmadığını sordu. GH-1 çarpan sormuyor, ölçerin kendisini sınıyor. ETAS-TABAN istatistiksel ağırlıktı; GH-1 fiziksel ters çözümü bağımsız jeodeziye karşı ölçüyor. DT-2/S-3 mekânsal kenetlenmeydi; GH-1 zamansal.
- Zaman eksenine bağı: **dolaylı**. Geçerse yalnız "yeni gözlem türü var" denir (FA-1 yeniden açma şartının ön koşulu). M6+ olasılığına geçiş ayrı bir ön kayıt ister ve S-7'nin ayırt edilemezlik sonucuyla yüzleşir.

**GH-2: Marmara/batı KAF'ta tetiklenmiş tremor varlık taraması**
- Soru: Büyük uzak depremlerin yüzey dalgaları geçerken KOERI geniş bant istasyonlarında (ve erişilebilirse GONAF kuyu sensörlerinde) 2–8 Hz'de, yüzey dalgası periyoduyla eş fazlı, istasyonlar arasında tutarlı tremor var mı? Aday tetikleyiciler: 2010–2025 arasında, ≥10 kPa tepe dinamik gerilme beklenen 8–12 uzak deprem ve Kahramanmaraş 2023. Türkiye dışı 2026 depremleri kör veri kuralı gereği kullanılmaz.
- Ön kayıt: Tetikleyici listesi, istasyonlar, süzgeç ve tutarlılık eşiği önceden dondurulur. Negatif kontrol olarak aynı istasyonlarda tetikleyici olmayan rastgele pencereler kullanılır.
- Veri: KOERI sürekli dalga formu 2011+ (AV.md: "açık (200)"), EIDA. GONAF erişimi doğrulanmadı. 0 €.
- Hedef sayısı: 8–12 tetikleyici. Kaba güç: Pfohl'un olumsuz sonucu ve kuyu dışı gürültü yüzünden pozitif bulma olasılığı düşük. Değeri olumsuz sonucun da kapı kapatması.
- Ayrım: Defterde tremor adayı yok (`kayit.py ara tremor` boş). S-7/EL-1 tekrarlayan depremlerdi; tremor farklı bir sinyal ve farklı bir derinlik (kilitlenme derinliğinin altı).
- Zaman eksenine bağı: **çok dolaylı**. Tremor bulunsa bile "tremor hızı → M6+" bağı yalnız Parkfield 2004 tek olayına dayanıyor (kanıtlanmadı). Marmara'da yıl ölçekli bir terime dönüşmesi için onlarca yıl gözlem gerekir.

**Önerilmeyenler**
- A3 μ(t) çarpanı: ETAS-TABAN ve S-7 ile aynı.
- Tremor → M6+ çok olaylı geriye dönük sınav: Dünyada tremor kataloğu içinde kalan doğrultu atımlı M6+ ≈1 (Parkfield 2004). Güç sıfır.
- Ogata türü "göreli sessizlik → büyük deprem": FA-6 (hazırlık evresi) kapsamına giriyor.

### Gaps
- GH-1'in güç hesabı el hesabıdır. Resmî MDE ya da yapay katalogla duyarlılık sınaması yapılmadı. GH-1 için Aσ'nın Marmara değeri bilinmiyor.
- GH-2 için KOERI istasyonlarının gürültü tabanı ve GONAF açıklığı doğrulanmadı.
- Görev metnindeki şu kaynaklar bu turda ayrıca okunmadı: Schmittbuhl 2016, Wollin 2018, Becker 2023 (DOI doğrulanmadı), Karabulut 2021, Nisan 2025 M6,2 çalışmaları. 2025 M6,2 için OpenAlex'te 2026 EGU özetleri ve gerilme evrimi özetleri görüldü ([10.5194/egusphere-egu26-1665](https://doi.org/10.5194/egusphere-egu26-1665), [10.5194/egusphere-egu26-12759](https://doi.org/10.5194/egusphere-egu26-12759)); olay öncesi gerilme hızı değişimi iddiası içerip içermedikleri okunmadı.
- Not: Adalar Ağustos 2026 kümesi üzerine tek yazarlı bir EarthArXiv ön baskısı ([10.31223/x5qj6q](https://doi.org/10.31223/x5qj6q)) var: 127 olay, en büyüğü ML 3,2, 2025 M6,2'nin Çınarcık'a aktardığı gerilme +0,204 kPa. Hakemsiz ve tek yazarlı, güvenilirliği belirsiz. Kendisi "tetiklemeyi göstermez" diyor.

### Özet tablo

| aday adı | soru | köprü k ve J (kontrolle) | veri ve erişim | hedef sayısı ve kaba güç | zaman eksenine bağı | en büyük risk |
|---|---|---|---|---|---|---|
| **GH-1** Sismisite gerilme ölçerinin Marmara'da kör doğrulanması | T-rate / Heimisson–Segall ters çözümü bağımsız tarihli Marmara geçicilerini (İzmit 2015/16/18/19 yavaş kaymaları, Armutlu, batı Marmara 2013) ve 1999 sonrası basamağı rastgele takvimden ayırıyor mu? | A1 × B k=61, J=0,024; A1 × MARMARA k=84, J=0,030; A1 × B × MARMARA k=4, J=0,001. Kontroller: ETAS × B k=208, J=0,060; A1 × COULOMB k=661, J=0,125 | GFZ homojen katalog 2006–2023, KOERI zeqdb, EMSC FDSN; T-rate kodu açık (zenodo). 0 € | 5–7 geçici + 1 pozitif kontrol. Segment başına yılda ≈50–80 M≥2 (EMSC ham) → 1 yılda görülebilen r ≈1,4–2,0 ya da Δτ ≈5–25 kPa. Yavaş kayma gerilmeleri ≲1 kPa: **büyük olasılıkla H0** | Dolaylı: geçerse yalnız "yeni gözlem türü var" (FA-1 şartının ön koşulu); olasılık terimi ayrı ön kayıt ister | Marmara yavaş kaymaları ölçerin eşiğinin 10–100 kat altında; sonucu arka plan hızı r ve Mc kaymaları belirler |
| **GH-2** Marmara/batı KAF tetiklenmiş tremor taraması | 8–12 uzak deprem ve Kahramanmaraş 2023'ün yüzey dalgalarıyla Marmara'da tutarlı tremor tetikleniyor mu? | A2 × B k=3, J=0,003 (kontrolün ≈1/20'si); A2 × MARMARA k=17, J=0,012 (etkin ≈5) | KOERI sürekli dalga formu 2011+ (açık), EIDA; GONAF erişimi doğrulanmadı. 0 € | 8–12 tetikleyici; Pfohl 2015 merkezî KAF'ta olumsuz → pozitif olasılığı düşük; olumsuz sonuç kapıyı kapatır | Çok dolaylı: tremor → M6+ bağı yalnız Parkfield 2004 (tek olay, kanıtlanmadı) | Tremor muhtemelen yok; varsa da olasılık terimine dönüşmesi onlarca yıl ister |
| (önerilmedi) A3 μ(t) çarpanı | Arka plan hızı geçicisi M4+/M6+ olasılığını artırır mı? | A3 × B k=29, J=0,030; A3 × MARMARA k=6, J=0,005 | GFZ/KOERI | M≥4 etkin N ≈15; ≥0,45 nat/olay altı görülmez | Doğrudan ama | ETAS-TABAN (+0,014 ± 0,035) ve S-7 (−0,06 ± 0,12) ile aynı soru: **ayrışmıyor** |
