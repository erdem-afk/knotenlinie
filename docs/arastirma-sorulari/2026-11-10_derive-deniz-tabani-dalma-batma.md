# Japonya, Cascadia, Şili, Hikurangi çalışmalarından İstanbul'a türetilen adaylar (10 Kasım 2026)

Erdem'in isteği: İstanbul için hazırlanmamış ama benzer çalışmalardan İstanbul odaklı yeni çalışma türetmek. Bu belgenin alanı dalma-batma bölgelerinin deniz tabanı jeodezisi, kilitlenme ters çözümü, tekrarlayan depremler, gelgit ve yavaş kayma literatürü. Asıl hedef karadan ölçülemeyen PIF (ve kısmen CMF) kilitlenmesi.

Salt tarama, 0 €, hiçbir şey koşulmadı, makine kiralanmadı. Seçim Erdem'in. Olasılık yazılmaz. Türkiye dışı 2026 verisine dokunulmadı.

## Çıkış noktası (tekrar edilmeyenler)

- Y1/Y1b/Y1c (10 Kasım): karadan GNSS + InSAR **kinematik** ters çözüm CMF'yi 11 ± 3 mm/yıl verdi, PIF'i Çınarcık–Armutlu deformasyonundan ayıramadı (veri geometrisi sınırı). "PIF için deniz tabanı ölçümü gerekir."
- Y4 tekrarlayan deprem kataloğu, Y5 b-değeri, Y7 yavaş kayma, Y10 DAS/basınç/kablolu gözlemevi, Y11 yeni kampanya: kilitlenme ölçme yolları belgesinde değerlendirildi.
- S3 (mikrosismisite M7 yeri), S7 (asismik geçiciler), S1 (sıçrama kuralları), S6 (türbidit eşzamanlılığı): kapandı.

## Boşluk ölçümü (OpenAlex, anahtarlı)

Yöntem: her yöntem ailesi için 3–6 tohum makale (DOI ile doğrulandı). Tohumlara atıf yapan işler içinde başlık/özetinde "Marmara", "Istanbul" ya da "North Anatolian" geçenler sayıldı. Pozitif kontrol: aynı atıf yapanlar içinde köken bölgesi (Japonya, Cascadia, Şili, Nankai, Hikurangi, Tohoku, dalma-batma) geçenler. Oran = Marmara / köken. Ardından Marmara isabetlerinin başlık ve özetleri okunup gerçek öncül olup olmadıkları elle ayrıldı.

| Aile | Tohumlar | Atıf yapan | Köken | Marmara | Oran | Gerçek öncül |
|---|---|---|---|---|---|---|
| A mekanik tutarlı kilitlenme (gerilme gölgesi) | Johnson & Fukuda 2010, Lindsey 2021, Herman 2018, Kaneko 2010, Hetland 2010 | 660 | 305 | 12 | 0,039 | **Yok.** 12'nin hepsi kinematik ters çözüm (Blétery 2020, Diao 2016) ya da simülasyon (Güvercin ve Barbot 2025). Hedefli arama "stress shadow / mechanically consistent × Marmara/NAF": 8 iş, hiçbiri kilitlenme ters çözümü değil |
| B gelgit tetiklenmesi, gelgit–b değeri | Tanaka 2012, Ide 2016, Delorey 2017, Cochran 2004 | 557 | 96 | 1 | 0,010 | **Kısmi:** Martínez-Garzón 2023 (deniz seviyesi, Doğu Marmara hidrotermal alan, 6 ay). Segment karşılaştırması ve kilitlenme vekili yok. "tide × b-value × doğrultu atımlı": 1 iş, ilgisiz |
| C tekrarlayan deprem kayma hızı | Nadeau & Johnson 1998, Igarashi 2003, Uchida & Bürgmann 2019, Chen & Lapusta 2009 | 902 | 318 | 11 | 0,035 | **Var:** Uchida, Kalafat, Pınar 2019 (Japon yöntemi Marmara'ya taşınmış, 9 dizi), Schmittbuhl 2016, Becker 2023. Aday çıkarılmadı |
| D kilitlenme → kırık sınırı | Moreno 2010, Loveless & Meade 2011, Métois 2016, Protti 2014, Chlieh 2011, Bürgmann 2005 | 1237 | 842 | 6 | 0,007 | **Yok:** Marmara isabetleri kilitlenme haritası (Diao 2016, Bohnhoff 2013), sınav değil. "coupling × rupture extent × strike-slip": 14 iş, sistematik sınav yok |
| E ölçüm ağı tasarımı, bilgi değeri | Sathiakumar 2017, Yokota 2016, "seafloor geodetic … shallowest" 2017 (GRL) | 339 | 233 | 3 | 0,013 | **Kısmi:** Klein 2017 (karadan neyi çözeriz), Sakic 2016 (Marmara akustik ağ tasarımı, tez). Tahmin belirsizliğine göre bilgi değeri yok |
| F gerilme rotasyonu, mutlak gerilme | Hasegawa 2011, Hardebeck 2012, Hardebeck & Michael 2004 | 426 | 225 | 4 | 0,018 | **Kısmi:** Ickrath 2015 (İzmit–Düzce rotasyonu). Marmara'da 2025 sonrası yok |

Okuma: köken bölgesine göre Marmara oranı A ve C'de ≈0,04, D'de 0,007. C'nin yüksek oranı gerçek bir taşımadan geliyor (Uchida 2019), bu yüzden C pozitif kontrol gibi davranıyor. A'nın oranı C'ye yakın ama isabetlerin hiçbiri yöntemin kendisi değil: boşluk ölçü değil okuma ile kanıtlandı. Sınır: tohum seçimi sonucu belirler; başlık/özet araması tam metni görmez.

Ham çıktı: `oncul/derive_bosluk_rapor.json`, betikler `tools/literatur/derive_oa_bosluk.py`, `derive_oa_ozet.py`, `derive_oa_say.py`.

## Adaylar (sıralı)

Ortak kurallar: her aday önce ön kayıtla dondurulur (OTS), sonuç ileri test defterine rakip ya da bilgi satırı olarak girer, v1.3b değişmez. Tüm veri Türkiye ≤2025 (mühür açık, geliştirme verisi) ya da Türkiye dışı ≤2025 yayımlanmış; Türkiye dışı 2026'ya dokunan aday yok. Dürüst ortak sınır: kilitlenme nihai v1.3b'yi neredeyse oynatmıyor (kayma açığı yalnız ≈%2,6 ağırlıklı moment dalında); asıl etki simülatör hattında (v2.x) ve segment birleşiminde.

### 1. Mekanik tutarlı kilitlenme ters çözümü: PIF'i gerilme gölgesi fiziğiyle ayırmak

- **Kaynak:** Johnson ve Fukuda 2010 (kilitli pürüzler + gerilme güdümlü sünme), Hetland ve Simons 2010, Kaneko, Avouac ve Lapusta 2010, Herman, Furlong ve Govers 2018, Lindsey ve diğ. 2021 (Japonya, Cascadia, Şili: karadan görülen "kilitlenme" çoğunlukla kilitli yamaların gerilme gölgesi).
- **İstanbul'a taşıma:** Y1c kinematikti; her yamanın kayma hızı serbestti, bu yüzden PIF açığı Çınarcık koluna kaçtı. Mekanik tutarlı çözümde serbest parametre yalnız kilitli yamaların yeri; sünen kesimler kilitli yamalardan gelen gerilmeye göre kendiliğinden kayar. Bu, PIF ile Çınarcık arasındaki takası fiziksel olarak kısıtlar: Çınarcık kolu PIF'in gerilme gölgesinde kalıyorsa ondan bağımsız kayamaz.
- **Boşluk:** Marmara/KAF'ta mekanik tutarlı kilitlenme ters çözümü yok (yukarıda A satırı).
- **H1:** Y1c'nin sentetik testinde (aynı istasyonlar, aynı gürültü) mekanik tutarlı çözüm PIF 11 ile 18 mm/yıl'ı ayırır ve model yanlışlığı testi F2'yi geçer. **H0:** yine ayıramaz; "PIF için deniz tabanı şart" sonucu güçlenir ve iş kapanır.
- **Önce yapılacak kapı:** aynı sentetik eşik (Y1c ile aynı, değiştirilmeden). Ayrıca "yalnız ön bilgi" satırı (veri olmadan aynı modelin PIF dağılımı): sonucun veriden mi varsayımdan mı geldiğini gösterir; ön bilgiden ayrışmıyorsa hüküm H0.
- **Veri:** Kurt 2023 GNSS + Y1b istasyonları (sunucuda), EDSF13 geometrisi, 1999 gevşeme vekili (Y1b'deki). Hepsi Türkiye, açık.
- **İstanbul M7+ katkısı:** v1.3b'ye ≈0. v2.x hattında PIF yüklemesi (v2.2'de PIF 2,8 kat oranının kaynağı) ve CMF+PIF ortak kırılma. Başarırsa ilk sayısal PIF açığı.
- **Maliyet/süre:** 0 € (sunucuda), 2–4 gün. Risk: sonuç kilitli yama sayısı ve sürtünme varsayımına duyarlı; ön kayıtta sabitlenmeli.

### 2. Bilgi değeri: hangi tek deniz tabanı ölçümü İstanbul belirsizliğini en çok daraltır?

- **Kaynak:** Sathiakumar ve diğ. 2017 (en iyi jeodezik ağ tasarımı), Yokota ve diğ. 2016 ve en sığ kesim GNSS-A kilitlenmesi 2017 (Nankai GNSS-A ile kara modellerinin göremediği kilitlenme), Japonya'da GNSS-A ağının kara ters çözümlerinin çözünürlük boşluğuna göre yerleştirilmesi.
- **İstanbul'a taşıma:** Y1c "PIF için deniz tabanı ölçümü gerekir" dedi ama hangisi, nerede, kaç yıl? Aday ölçümler (PIF'i kesen akustik taban çizgisi, Adalar'a yakın GNSS-A noktası, Kumburgaz doğusunda ek taban çizgisi) için Y1c Green fonksiyonları ve gerçekçi hassasiyetle (Lange 2019: 2,5 yılda ±1,25 mm/yıl; GNSS-A yıllık cm düzeyi) beklenen sonsal daralma hesaplanır, sonra v2.x İstanbul 30 yıl yayılımına yansıması.
- **Boşluk:** Marmara'da ağ tasarımı var (Sakic 2016, Klein 2017) ama tahmin belirsizliğine göre bilgi değeri hesabı yok.
- **H1:** en az bir ölçüm ≤5 yılda PIF 11 ile 18 mm/yıl'ı ayırır ve v2.x İstanbul yayılımını belirgin daraltır. **H0:** hiçbir tek ölçüm 5 yılda ayıramaz; PIF belirsizliği 2030'lara kadar kalır, bunu defterde açık sınır olarak yazarız.
- **Veri:** sentetik; Y1c kurulumu, v2.2/v2.3 yapılandırma duyarlılıkları. Sızıntı yok.
- **İstanbul M7+ katkısı:** doğrudan değil. Çıktı bir ölçüm önerisi; dış gruplara (JAMSTEC, GEOMAR, Ifremer, Kandilli) iletilmesi Erdem'in kararı. PIF'i gerçekten ölçecek tek yol bu.
- **Maliyet/süre:** 0 €, 2–3 gün. Aday 1'den sonra (onun ileri modeli kullanılırsa daha doğru).

### 3. Kilitlenme haritaları kırığın nerede duracağını önceden söyledi mi? (çok olaylı sözde-ileriye dönük sınav)

- **Kaynak:** Moreno, Rosenau ve Oncken 2010 (Maule kayması olay öncesi kilitlenmeyle örtüştü), Loveless ve Meade 2011 (Tohoku), Métois ve diğ. 2016 (Şili: düşük kilitlenme kırık sınırı), Protti ve diğ. 2014 (Nicoya önceden kestirildi), Chlieh 2011 (And).
- **İstanbul'a taşıma:** CMF batısı kısmen sünüyor, Kumburgaz doğusu kilitli. Sünen kesim M7 kırığını durdurur mu? Bu, segment birleşimini (CMF+PIF ortak kırılma, v1.7'de f ≈ 0,10) ve kırığın batıya uzanıp uzanmayacağını doğrudan etkiler. Sınav: olay öncesi yayımlanmış kilitlenme modeli olan büyük depremlerde (dalma-batma: Maule, Tohoku, Iquique, Illapel, Nicoya, Pedernales, Gorkha; doğrultu atımlı: Kahramanmaraş 2023 için Blétery 2020 ve Aktuğ 2016, Kaikoura, Palu, Sagaing 2025) kırık uçları düşük kilitlenmeli kesime, rastgele yerleşime göre daha sık mı düşüyor?
- **Boşluk:** tek tek olay çalışmaları var (yukarıda), ön kayıtlı çok olaylı log skorlu sınav yok; doğrultu atımlı faylarda sistematik sınav yok (D satırı).
- **H1:** kırık sınırı = kilitlenme < eşik kuralı, tekdüze sınır kuralına göre olay başına pozitif log skor, ateşleme kapısı açık. **H0:** ayırt edilemez (N ≈ 10–14, güç zayıf; kapı büyük olasılıkla önceden kapalı, dürüstçe yazılır).
- **Sızıntı:** her olayda yalnız olay tarihinden önce yayımlanmış kilitlenme modeli (muhur.py mantığı, yayım tarihi kapısı). Kırık modelleri USGS/SRCMOD, ≤2025.
- **İstanbul M7+ katkısı:** segment birleşimi ve kırık uzunluğu (Mw 7,0 mı 7,3–7,6 mı); uzamsal eksen (%46) ile kesişir. S1'in geometrik sıçrama kurallarını reolojik bariyerle tamamlar. Güvercin ve Barbot 2025 simülasyonu da "kalın çökel bariyerleri" diyor; bu sınav o iddianın gözlemsel karşılığı.
- **Maliyet/süre:** 0 €, 5–7 gün (kilitlenme modellerini sayısallaştırma işin çoğu; bazıları yalnız şekil olarak yayımlı).

### 4. Karadan kilitlenme ne kadar yanılıyor? Japonya ve Şili'de kara ile deniz tabanı karşılaştırmasından PIF için ön bilgi

- **Kaynak:** Nankai (kara modelleri ile Yokota 2016 GNSS-A), Tohoku (2011 öncesi kara kilitlenmesi ile sonradan deniz tabanı), Şili ve Peru kıyı ötesi ölçümleri, Hikurangi (Wallace: deniz tabanı basıncıyla kara modellerinin göremediği sığ yavaş kayma), Cascadia (Lindsey 2021).
- **İstanbul'a taşıma:** her karşılaştırmada "kara tahmini − deniz tabanı ölçümü" farkını, ölçülen yamanın en yakın kara istasyonuna uzaklığı / kilitli derinlik oranının fonksiyonu olarak derleyip PIF için deneysel bir yanlılık ve belirsizlik ön bilgisi çıkarmak. PIF'te bu oran dalma-batmadan çok daha iyi (Adalar faya 2–5 km).
- **Boşluk:** derleme olarak yok (taramada bulunmadı; zayıf kanıt, hedefli arama sınırlı).
- **H1:** yanlılık uzaklık oranıyla sistematik değişir ve PIF geometrisinde küçüktür; Y1b'nin PIF tahmini yanlılık düzeltmesiyle kullanılabilir. **H0:** dağılım geometriyle açıklanamaz ya da N < 6; ön bilgi kurulmaz.
- **Veri:** yayımlanmış sayılar, ≤2025. Sızıntı yok.
- **İstanbul M7+ katkısı:** dolaylı; aday 1 başarısız olursa PIF için tek sayısal ön bilgi. Aktarım zayıf: dalma-batma ile doğrultu atımlı geometri farklı.
- **Maliyet/süre:** 0 €, 3–4 gün.

### 5. Gelgit duyarlılığı kilitli ve sünen kesimi ayırıyor mu?

- **Kaynak:** Tanaka 2012 (Tohoku öncesi gelgit tetiklenmesi artışı), Ide, Yabe ve Tanaka 2016 (gelgit gerilmesi yüksekken b değeri düşük; büyük depremler gelgit tepesinde), Delorey 2017 (San Andreas), Martínez-Garzón 2023 (Doğu Marmara'da deniz seviyesi sismisiteyi değiştiriyor).
- **İstanbul'a taşıma:** Türkiye ≤2025 kataloğunda (KOERI/AFAD, ayrıca yayımlanmış yüksek çözünürlüklü Marmara katalogları) gelgit Coulomb gerilmesi fazına göre olay oranı ve b değeri: CMF batısı (sünen) ile Kumburgaz doğusu ve PIF (kilitli) arasında fark var mı? Japonya'da duyarlılık kritik gerilme vekili olarak okunuyor.
- **Boşluk:** Marmara'da yalnız hidrotermal alanda 6 aylık deniz seviyesi çalışması; segment karşılaştırması ve kilitlenme vekili yok (B satırı).
- **H1:** kilitli kesimlerde gelgit faz korelasyonu (Schuster p) ve gelgit–b değeri eğimi sünen kesimden anlamlı farklı. **H0:** fark yok ya da güç yetmiyor. Önce sentetik güç testi (Marmara gelgiti küçük; katı yer gelgiti baskın).
- **Veri:** Türkiye kataloğu ≤2025, gelgit hesabı (katı yer + okyanus yüklemesi). Sızıntı yok.
- **İstanbul M7+ katkısı:** nitel; doğrudan M7 sayısı vermez. Panelde L1 "zayıf dolaylı ipucu" olarak geçiyordu; bu aday onu ölçülebilir hale getirir ama büyük olasılıkla H0.
- **Maliyet/süre:** 0 €, 2–3 gün.

## Elenenler

- **Tekrarlayan depremlerden kayma hızı (C):** Uchida, Kalafat ve Pınar 2019 Japon yöntemini Marmara'ya zaten taşımış; Y4 ile örtüşüyor. PIF'te tekrarlayan yok.
- **Gerilme rotasyonu ve mutlak gerilme (F):** Hasegawa 2011 / Hardebeck 2012 yöntemi Marmara'da 2025 M6,2 sonrası denenebilir ama çıktısı Δτ düzeyi; Δτ İstanbul aralığına girmiyor (v1.6'da sabitlenince ×1,000). Değer düşük.
- **Yavaş kayma ve deniz tabanı basıncı (Hikurangi, Cascadia ETS):** S7 ve Y7 kapsıyor; Marmara doğrultu atımlı, düşey sinyal yok, basınç ölçeri kaymayı ölçmüyor (Y10).
- **Güvercin ve Barbot 2025 (Marmara deprem döngüsü simülasyonu, kalıcı segmentasyon):** yeni aday değil, simülatör ABC kalibrasyonu (S5) için kıyas kaynağı; S5'e not.

## Önerilen sıra

1 ve 2 önce (ikisi de 0 €, aynı Y1c kurulumunu kullanır, sunucuda 1 hafta içinde). 1 başarısız olursa 4, PIF için ön bilgi olarak. 3 bağımsız, paralel yürüyebilir. 5 boşta. Hepsi seçilirse toplam 0 €, makine gerekmez.
