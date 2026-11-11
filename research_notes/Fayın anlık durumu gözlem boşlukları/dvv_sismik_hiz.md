# Sürekli dalga formu ölçüleri (dv/v, sönüm, S dalgası ayrılması) fayın anlık gerilme durumunu ölçebilir mi? Deprem tahmini sınama literatürüyle boşluk ve Marmara/KAF için 0 € adaylar

Kapsam notu: Birincil kaynak OpenAlex (`kayit/oa.py`); tarama 11 Kasım 2026. Çoğu makalede yalnız özet okundu; "tam metin okunamadı" olanlar ayrıca işaretli. Köprü ölçümü dosyaları: `/home/user/knotenlinie/kayit/turetme/kopru/dvv/tohumlar.json`, `/home/user/knotenlinie/kayit/turetme/kopru/dvv/cikti/kopru_rapor.json`. Aday defterinde (`kayit.py ara`) "dv/v", "dvv", "sönüm", "S-dalga", "anizotropi", "ortam", "gürültü" için hiç kayıt yok. Komşu kayıtlar: DD-5 (gelgit duyarlılığı, güç yok), FA-6 (hazırlık evresi alarmı, elendi), S-7 ve EL-1 (tekrarlayan depremler), AV-5 (GONAF gerinim ölçer, veri kapalı), TK-1 (EEPAS, MDE 0,45 nat/olay, N≈40).

## S1. dv/v büyük depremlerden ÖNCE (ay–yıl ölçeğinde) sistematik değişim gösteriyor mu? Çok olaylı ve puanlanmış bir sınav var mı?

### Takeaway
Pasif (ortam gürültüsü) dv/v literatürünün çekirdeği tutarlı olarak yalnız **kosismik düşüş + logaritmik/kısmi iyileşme** gösteriyor. Öncül iddiaları (i) aktif kaynak ya da deprem tomografisiyle, (ii) tek olayda, (iii) saat–hafta ölçeğinde ve geriye dönük. Bir rakibe (durağan Poisson / ETAS) karşı log skor, bilgi kazancı ya da Molchan/ROC ile puanlanmış çok olaylı dv/v öncül sınavı **bulunamadı**. S dalgası ayrılmasında tek "sınav" (Seher & Main 2004) Poisson boş hipotezini reddedemedi. Yeni bir öncül iddiası **kanıtlanmadı**.

### Cited Findings
**Yalnız kosismik düşüş + iyileşme (öncül yok):**
- Wegler & Sens-Schönfelder 2007: Mw 6,6 Orta Niigata depreminin yakınında tek istasyonlu otokorelasyonda depremle çakışan **−%0,6** ani hız düşüşü. Öncül değişim bildirilmiyor. — [GJI 168:1029, 10.1111/j.1365-246x.2006.03284.x](https://doi.org/10.1111/j.1365-246x.2006.03284.x)
- Brenguier ve diğ. 2008: 2003 San Simeon ve 2004 Parkfield depremleri hızı düşürdü. Parkfield'dan sonra hız düşüşü **3 yıldan uzun** sürdü ve GPS art-kaymasına benzer biçimde söndü. Yorum: sığ hasar + derin kosismik gerilme değişimi ve art-sismik gevşeme. — [Science, 10.1126/science.1160943](https://doi.org/10.1126/science.1160943) (tam metin okunamadı, özet)
- Hobiger ve diğ. 2016: Japonya'da 1 büyük (Tohoku) ve 5 güçlü (Mw 6,2–6,9) kabuk depremi, 0,125–4 Hz. **Tüm** bölgelerde kosismik düşüş ve kısmi iyileşme. Düşüşlerin yaklaşık yarısı iyileşmiyor. Düşüş frekansla artıyor ve fay zonuna yakın en büyük. Özette öncül sinyal yok. Zaman serileri depremden önce başladığı hâlde öncül sinyal bildirilmemesi, olumsuz sonuç olarak not edilmeli. — [GJI 205:1053, 10.1093/gji/ggw066](https://doi.org/10.1093/gji/ggw066)
- Okubo, Delbridge & Denolle 2024, Parkfield 2002–2022 (20 yıl): kosismik düşüş, logaritmik iyileşme ve net uzun dönem artış. AIC/BIC ile doğrusal eğilim ya da "tamamlanmamış iyileşme" terimi uyumu iyileştiriyor. GNSS'ten hesaplanan ortalama hacimsel gerinim hafif **genişleme** gösteriyor; bu, hız artışının beklenen işaretinin **tersi**. Yazarlar eksen boyunca sıkışmayla mikro çatlak kapanmasını aday sayıyor. — [JGR 2024, 10.1029/2023jb028084](https://doi.org/10.1029/2023jb028084)
- Brenguier ve diğ. 2014: Tohoku-Oki'nin dinamik gerilmesiyle volkanik bölgelerde kosismik hız düşüşü. "Hız duyarlılığı" basınçlı akışkan bölgelerini haritalamak için öneriliyor. Bu uzamsal bir ölçü, zamansal öncül değil. — [Science, 10.1126/science.1254073](https://doi.org/10.1126/science.1254073) (tam metin okunamadı)
- Okubo/Hillers/Taira çizgisinde de aynı örüntü görülüyor. Taira ve diğ. 2009, Parkfield'da uzak depremlerin tetiklediği "fay dayanımı" değişimlerini bildiriyor. Özet OpenAlex'te yok, tam metin okunamadı. — [Nature, 10.1038/nature08395](https://doi.org/10.1038/nature08395)

**Öncül iddia edenler (hepsi tek olay, geriye dönük):**
- Niu ve diğ. 2008 (SAFOD, Parkfield): **aktif kaynakla** kuyu içi seyahat süresi izleme. Başlığa göre "ön-sismik hız değişimi". Özet OpenAlex'te yok, tam metin okunamadı. Akılda kalan ama doğrulanmamış ayrıntı: iki küçük olaydan (M≈1–3) **saatler** önce seyahat süresi sapması. Bu ölçek, ay–yıl ölçeğinden değil. — [Nature, 10.1038/nature07111](https://doi.org/10.1038/nature07111); açık kopya: https://digital.library.unt.edu/ark:/67531/metadc894577/
- Chiarabba, De Gori, Segou & Cattaneo 2020: 2016 Mw 6,5 Norcia ana şokundan önceki 3 ayda >13 000 depremle zaman pencereli tomografi. "Kilitli son durum" ve hiposantr yakınında ana şoktan **birkaç hafta önce** hızlı fay rijitliği değişimi bildiriyor. Tek olay, yoğun öncül deprem dizisi (Amatrice–Visso) gerekiyor, pasif gürültüyle değil deprem tomografisiyle yapılmış. — [Geology 48, 10.1130/g47048.1](https://doi.org/10.1130/g47048.1) (tam metin okunamadı)
- Furumoto ve diğ. 2001 (Kanto-Tokai): tekrarlanan patlatmalarla P hızının gelgit ve seküler gerilme birikimine yanıt verdiğini ileri sürüyor. Üst kabukta **~10⁻³/yıl** kesirsel hız değişimi. Aktif kaynak, tek bölge, deprem öncesi sınav değil. — [GRL, 10.1029/2001gl013172](https://doi.org/10.1029/2001gl013172)
- Crampin, Volti & Stefánsson 1999: İzlanda'da M5 depremin S dalgası ayrılması gecikme sürelerinden "başarılı stres tahmini" (zaman ve büyüklük). — [GJI 138:F1, 10.1046/j.1365-246x.1999.00891.x](https://doi.org/10.1046/j.1365-246x.1999.00891.x)

**Tek bulunan istatistiksel değerlendirme (S dalgası ayrılması):**
- Seher & Main 2004 aynı İzlanda verisini BIC ile yeniden değerlendirdi. Tahmin modeli 17 serbestlik dereceli çok doğrulu bir uyumdu ve sinyal/gürültü oranı ≈1. Rastgele oluş boş hipotezi yalnız 134,6 günlük sinüs modeline karşı reddedilebiliyor. %95 güven aralığında büyüklük **3,9–6,7**. Zaman aralığı olaydan 42 gün önce başlıyor, belirgin bir sonu yok. Sonuç: M5'in olağan Gutenberg–Richter etkinliğinin parçası olduğu biçimsel olarak reddedilemiyor. — [GJI, 10.1111/j.1365-246x.2004.02186.x](https://doi.org/10.1111/j.1365-246x.2004.02186.x)
- Peng & Ben-Zion 2005 (İzmit/Düzce artçıları, ~18 000 olay): Düzce ana şoku boyunca görülen %30'a varan görünür gecikme değişimleri çoğunlukla ışın yolu değişimiyle açıklanıyor. Benzer olay kümelerinde değişim en çok **%2**. "Düzce ana şokundan önce sistematik öncül değişim yok." — [GJI, 10.1111/j.1365-246x.2005.02569.x](https://doi.org/10.1111/j.1365-246x.2005.02569.x)

**Sönüm (koda-Q):** Loma Prieta dizisi boyunca koda-Q kararlı bulundu ([JGR 1995, 10.1029/94jb02574](https://doi.org/10.1029/94jb02574)). Koda-Q zaman değişimleri hiposantr göçüyle açıklanabiliyor ([JGR 2000, 10.1029/2000jb900104](https://doi.org/10.1029/2000jb900104)). Daha yeni çalışmalar Orta İtalya 2016–17'de sönümde hızlı değişimleri kırılma ve akışkan göçüne bağlıyor; bunlar dizi içi, öncül tahmin sınavı değil ([Front. Earth Sci. 2022, 10.3389/feart.2022.909698](https://doi.org/10.3389/feart.2022.909698)). Hiçbiri özet ötesinde okunmadı.

### Inferences
- Yayımlanmış kanıtın yapısı şu: pasif dv/v ile kosismik yanıt için onlarca olay var; öncül iddia için bir elin parmakları kadar tek olay var ve bunlar başka yöntemlerle (aktif kaynak, deprem tomografisi, S dalgası ayrılması) yapılmış. Puanlanmış çok olaylı sınav sıfır. Ay–yıl ölçeğinde pasif dv/v öncülü için yayımlanmış olumlu kanıt bulunamadı.
- Hobiger 2016 ve Okubo 2024 gibi uzun, depremi önceden kapsayan serilerin öncül bildirmemesi zayıf bir olumsuz kanıttır. Yayın yanlılığı iki yönde de işler: öncül aranıp bulunamadıysa çoğu zaman yazılmaz.
- Okubo 2024'ün işaret çelişkisi (genişleme varken hız artışı) önemli: 20 yıllık en iyi seride bile uzun dönem eğilim tek anlamlı bir gerilme göstergesine çevrilemiyor.

### Gaps
- Niu 2008, Taira 2009, Chiarabba 2020 ve Brenguier 2008/2014'ün tam metinleri okunamadı. Niu 2008'deki sayılar doğrulanmadı.
- OpenAlex'te "precursor + dv/v + Molchan/information gain" taraması sonuç vermedi. Bu bir yokluk bulgusu; Google Scholar ya da arXiv ile çapraz denetlenmedi.

## S2. dv/v'nin gerilme duyarlılığı ne kadar? Tektonik yüklenme (yılda ≈kPa) ölçülebilir mi, gürültü tabanı nedir?

### Takeaway
Gelgitle kalibre edilmiş duyarlılıklar **sığ** (birkaç yüz metre) gevşek malzemeye ait. Hillers 2014'te sS≈0,5 MPa⁻¹, hacimsel gerinim duyarlılığı ≈5×10³ ve tepe dv/v ≈%0,03. Bu değerle yılda 1–10 kPa yüklenme kâğıt üzerinde %0,05–0,5/yıl eder. Ancak (i) duyarlılık derinlikle hızla düşüyor, (ii) mevsimsel, hidrolojik ve iyileşme eğilimleri aynı büyüklükte, (iii) Okubo 2024'te uzun dönem eğilimin işareti jeodezik gerinimle çelişiyor. Daha temel sorun: dv/v en iyi durumda gerilme **değişimini** ölçer, mutlak gerilme/dayanım oranını ölçmez. Bu yüzden zaman eksenini daraltmak için gereken "kırılmaya uzaklık" bilgisi ölçülemiyor. Bu son çıkarım literatürden türetildi; doğrudan sınanmış değil.

### Cited Findings
- Hillers ve diğ. 2014, Piñon Flat, 2–8 Hz: gelgit deformasyonuna sistematik yanıt. Tepe göreli hız değişimi **%0,03**, mutlak hacimsel gerinim duyarlılığı **Sθ ≈ 5×10³**, gerilme duyarlılığı **≈0,5 MPa⁻¹**. Duyarlılık koda gecikmesiyle azalıyor, yani yanıt **sığ derinliklerle sınırlı**. Bileşene göre zıt işaretler (anizotrop yanıt) görülüyor. — [JGR, 10.1002/2014jb011318](https://doi.org/10.1002/2014jb011318)
- Sens-Schönfelder & Eulenfeld 2019: tek istasyonla gelgit bileşenlerine yanıt olarak **%0,026**'ya varan hız değişimi. Elastik doğrusalsızlık "ilke olarak" gerilme ve gözenek basıncının uzaktan izlenmesini mümkün kılar. — [PRL 122:138501, 10.1103/physrevlett.122.138501](https://doi.org/10.1103/physrevlett.122.138501)
- Rivet ve diğ. 2011, Guerrero 2006 M7,5 yavaş kayma: 7–17 s periyotta (5–20 km) göreli hız değişimi **~10⁻³**, hacimsel deformasyon ise **~10⁻⁶**. Değişim gerinimin kendisinden çok **gerinim hızıyla** ilişkili. Doğrusal olmayan elastik davranış. — [GRL, 10.1029/2011gl047151](https://doi.org/10.1029/2011gl047151)
- Furumoto ve diğ. 2001: aktif kaynakla üst kabukta gerilme birikimine bağlanan **~10⁻³/yıl** hız değişimi. — [GRL, 10.1029/2001gl013172](https://doi.org/10.1029/2001gl013172)
- Mevsimsel ve hidrolojik denetleyiciler baskın: Los Angeles havzasında mevsimsel dv/v ([GJI 2010, 10.1111/j.1365-246x.2010.04550.x](https://doi.org/10.1111/j.1365-246x.2010.04550.x)), yeraltı suyu izleme ([GRL 2018, 10.1029/2018gl077706](https://doi.org/10.1029/2018gl077706); [Nat. Commun. 2022, 10.1038/s41467-022-32194-3](https://doi.org/10.1038/s41467-022-32194-3)), İzlanda'da mevsimsel yükleme ([Sci. Adv. 2019, 10.1126/sciadv.aax6642](https://doi.org/10.1126/sciadv.aax6642)). Bu kaynaklarda genlik sayıları özetlerde yok; okunmadı.
- Okubo 2024: 20 yıllık Parkfield serisinde çevresel ve kosismik terimler modellendikten sonra kalan uzun dönem artış, GNSS hacimsel geriniminin (hafif genişleme) beklenen işaretinin tersi. — [10.1029/2023jb028084](https://doi.org/10.1029/2023jb028084)
- Wang, Brenguier ve diğ. 2019 (Japonya, Hi-net eğim ölçerleri 8–50 s ile 5 km altı): kısa periyottaki güçlü düşüşler güçlü sarsıntı bölgesiyle sınırlı. Uzun periyot değişimleri başka bir dağılıma uyuyor (özet kesildi). — [JGR, 10.1029/2019jb017803](https://doi.org/10.1029/2019jb017803)

### Inferences
- **Kaba büyüklük hesabı:** Hillers duyarlılığı Sθ≈5×10³ ile Marmara'da sıradan bir 10⁻⁷/yıl kabuk gerinim hızı (varsayım, kaynaklı değil) 5×10⁻⁴/yıl = **%0,05/yıl** dv/v eğilimi verir. Bu, gelgit tepe yanıtı (%0,03) ve tipik mevsimsel salınımlarla aynı mertebede. Birkaç yıllık seride eğilim olarak saptanabilir görünür. Ancak: (a) bu duyarlılık sığ gevşek katmana ait, sismojenik derinlikte (5–15 km) çok daha küçük olmalı. Rivet 2011 ise 10⁻³/10⁻⁶ oranıyla derinde de büyük doğrusalsızlık bildiriyor, bu yüzden derindeki duyarlılık belirsiz, aralık en az iki mertebe. (b) Marmara'da 1999 İzmit ve Düzce'nin, 2019 ve 2025 olaylarının iyileşme eğilimleri üst üste biniyor (Hobiger: düşüşün yarısı iyileşmiyor; Okubo: iyileşme yıllar sürüyor). Doğrusal tektonik eğilim bu log terimlerle karışır.
- **Kavramsal tavan:** dv/v mutlak gerilme ya da dayanım ölçmüyor, yalnız değişime ve doğrusalsızlığa duyarlı. Mükemmel ölçülmüş bir yüklenme hızı, GNSS'in zaten verdiği bilgiyi (Ergintav 2014 gerinim birikimi) yineler. Zaman eksenini daraltmak için kırılma eşiğine uzaklık gerekir; bunu dv/v'nin vereceğine dair kanıt yok. Tek olası istisna Brenguier 2014'ün "duyarlılık" fikri: dinamik gerilmeye yanıtın büyüklüğü ortamın kritikliğini (basınçlı akışkan, çatlak yoğunluğu) yansıtabilir. Bu uzamsal bir ölçü. Zamanla değişip değişmediği ve depremden önce arttığı sınanmamış.
- Gürültü tabanı: Marmara için yayımlanmış bir σ(dv/v) değeri bulunamadı (S3). Bu değer DV-1 adayının ilk çıktısı olmalı.

### Gaps
- Kabuk derinliğinde (5–15 km) gerilme duyarlılığı için güvenilir, kaynaklı bir değer bulunamadı.
- Mevsimsel dv/v genliklerinin bölgesel derlemesi (Japonya, Wang ve diğ. 2017) taranmadı.

## S3. Marmara/KAF için ne var? Yayımlanmış dv/v zaman serisi, veri erişimi

### Takeaway
Marmara için **yayımlanmış hakemli bir dv/v zaman serisi bulunamadı**. 2019 Silivri M5,8 ve 23 Nisan 2025 M6,2 (Kumburgaz) çevresinde de bulunamadı. Var olanlar: Doğu Marmara/Çınarcık'ta gürültüyle **yapı** görüntüleme (Acarel tezi, 2015), KAF'ın DANA dizisinde (2012–13) dv/v yöntem bildirisi, KAF Karadere–Düzce ve Manyas'ta S dalgası ayrılması zaman analizleri ve 2025 M6,2'nin DAS kaydı. KOERI (KO) sürekli verisi EIDA üzerinden açık. Bu oturumda FDSN dataselect isteği 200 döndü.

### Cited Findings
- Acarel 2015, FU Berlin doktora tezi: Çınarcık Havzası ve Prens Adaları segmenti çevresinde ortam gürültüsüyle grup hızı ve 1B S hızı yapısı. Zamansal izleme bölümü Marmara için değil, **2011 M7,1 Van** depremi için (ana şoku çevreleyen 6 ay). — [refubium, 10.17169/refubium-9394](https://refubium.fu-berlin.de/handle/fub188/5195)
- van Dinther, Campillo, Margerin & Lecointre, EGU 2020 bildirisi: DANA dizisi (63 istasyon, Mayıs 2012–Ekim 2013), 0,1–1 Hz, KAF'ta dv/v için heterojen saçılma çekirdekleri. Fay zonu içinde serbest yol ~10 km, dışında ~150 km. Yalnız bildiri, sonuç sayısı yok. — [EGU2020-15195](https://doi.org/10.5194/egusphere-egu2020-15195)
- EGU 2025 bildirisi: 2023 Kahramanmaraş için ön-, eş- ve ard-sismik izotrop hız ve anizotropi izleme amaçlanıyor. Özette sonuç yok. — [EGU25-16174](https://doi.org/10.5194/egusphere-egu25-16174)
- Polat, Özel, Crampin, Ergintav & Tan 2012: 2006 Mb 5,3 Manyas–Kuş Gölü depremi için 29 TURDEP + 33 KOERI istasyonuyla **geriye dönük** S dalgası ayrılması "stres tahmini". Gecikme sürelerinde öncül azalma **yalnız GEMT istasyonunda** görüldü, çevredeki diğer istasyonlarda benzer değişim gözlenemedi. Konum bilgisi yok. — [NHESS 12:1073, 10.5194/nhess-12-1073-2012](https://doi.org/10.5194/nhess-12-1073-2012)
- Peng & Ben-Zion 2004 ve 2005: Karadere–Düzce kolu boyunca ~1 km genişlikte anizotrop zon. Düzce öncesinde sistematik öncül değişim yok. — [GJI 2004, 10.1111/j.1365-246x.2004.02379.x](https://doi.org/10.1111/j.1365-246x.2004.02379.x); [GJI 2005, 10.1111/j.1365-246x.2005.02569.x](https://doi.org/10.1111/j.1365-246x.2005.02569.x)
- Kartal ve diğ. 2026: 23 Nisan 2025 Mw 6,2'nin Prens Adaları kuzeyinden geçen karanlık telekom fiberindeki DAS kaydı (≈34 km açıklık, 8 m kanal aralığı, 250 Hz). GONAF kuyu sismometreleriyle karşılaştırılıyor. Olay kaydı; zaman serisi izleme değil. — [GJI, 10.1093/gji/ggag203](https://doi.org/10.1093/gji/ggag203)
- Marmara gürültü tomografisi (yapı): [GJI 2024, 10.1093/gji/ggae109](https://doi.org/10.1093/gji/ggae109); KB Türkiye trans-boyutlu Bayesçi gürültü tomografisi: [GJI 2023, 10.1093/gji/ggad082](https://doi.org/10.1093/gji/ggad082).
- GONAF kuyu gözlemevi: [Sci. Drilling 22:19, 10.5194/sd-22-19-2017](https://doi.org/10.5194/sd-22-19-2017). Bohnhoff 2013 İstanbul güneyindeki boşluk: [Nat. Commun., 10.1038/ncomms2999](https://doi.org/10.1038/ncomms2999).
- 2025 olayı: [Seismica 4(2), 10.26443/seismica.v4i2.1773](https://doi.org/10.26443/seismica.v4i2.1773); [J. Seismol., 10.1007/s10950-025-10342-8](https://doi.org/10.1007/s10950-025-10342-8). 2019 Silivri: [GJI, 10.1093/gji/ggaa469](https://doi.org/10.1093/gji/ggaa469).
- İlgili: Alhan & Khabat 2026 (EarthArXiv ön baskı, hakemsiz): KOERI kataloğu (2003–2026) üzerinde ML ve ETAS karşılaştırması. ETAS×ML melezi, iyi kurulmuş ETAS'a karşı bilgi kazancında **−0,38 nat/olay**. 2025 M6,2 hücresi önceki yıl boyunca en üst ~%1 sismisite hücresindeydi, yani uzamsal yerelleşme var ama zaman ekseninde değil. dv/v içermiyor. — [10.31223/x5w78x](https://doi.org/10.31223/x5w78x)

**Veri erişimi (bu oturumda denetlendi, büyük indirme yapılmadı):**
- EIDA yönlendirme hizmeti KO ağının dataselect adresini `https://eida.koeri.boun.edu.tr/fdsnws/dataselect/1/query` olarak veriyor (başlangıç 1971). Kaynak: `https://www.orfeus-eu.org/eidaws/routing/1/query?network=KO`.
- `eida.koeri.boun.edu.tr` istasyon servisi 40,5–41,3°K / 27,8–29,6°D kutusunda **29 KO istasyonu** listeledi. Uzun kayıtlı olanlar: ISK (1997), YLV (2000), ARMT (2005), KLYT (2006), BGKT, SLVT, CTKS (2007), KAVV (2009), BOTS, SINB, YKBL, LAFA, TUZL, YLVH, HVHR (2010), BRGA, BUYA, HYBA (2012), AVCI (2014). Yeni olanlar: TZLA, BUYK, ESKY, GUZE, KOUK, MAEG (2021), KRTL, CRLU (2022), SILV (2023), SLVA (2025-12). 2 dakikalık bir HHZ dataselect isteği HTTP 200 ve 14 KB döndü. Yani 2010+ en az ~19 istasyonla 2019 ve 2025 olaylarını çevreleyen sürekli veri açık erişimde.
- `eida-service.koeri.boun.edu.tr` adresi TLS sertifika uyuşmazlığı verdi (doğrulama kapatılmadı). ETH federatörü KO için 500 döndü. IRIS fedcatalog KO için boş döndü.
- PIRES (Prens Adaları) ve GONAF kuyu verisinin kamuya açık sürekli akışı **doğrulanamadı**. Defterde AV-5, GONAF gerinim ölçer için "veri kapalı" diyor. Deniz tabanı sismometrelerinin açık sürekli verisi de doğrulanamadı.

### Inferences
- Marmara'da dv/v boşluğu gerçek: KO verisiyle 2019 ve 2025 olaylarını çevreleyen bir dv/v serisi hiç yayımlanmamış görünüyor. Bu 0 € ile doldurulabilir; DV-1 adayı bunu yapar. Ama tek bölgede M6+ sayısı N≈1 (2025 M6,2). 2019 M5,8 eşik altında. Bu yüzden Marmara içinde bir **tahmin sınavı** kurulamaz; yalnız gürültü tabanı ve kosismik duyarlılık ölçülür.
- Manyas 2012 çalışması, defterde elenmiş "hazırlık evresi alarmı" (FA-6) ile aynı ailede: tek istasyon, geriye dönük, konumsuz. S dalgası ayrılmasını yeniden aday yapmak için literatür gerekçe vermiyor.

### Gaps
- Türkçe dergiler, TÜBİTAK raporları ve 2025 sonrası EGU/AGU bildirileri OpenAlex'te eksik olabilir. Marmara dv/v yokluğu "OpenAlex'te bulunamadı" düzeyinde.
- KO istasyonlarının 2011–2026 kesintisizlik oranı (availability extent) ölçülmedi.

## S4. Köprü ölçümü: (A) dv/v izleme × (B) tahmin sınaması; pozitif kontrol (B) × ETAS; (A) × Marmara/KAF

### Takeaway
A×B kesişimi **k=6, J=0,0028**. Pozitif kontrol B×ETAS **k=183, J=0,065**; J oranı ≈23 kat. Ortak atıf yapan 6 iş de derleme veya genel bakış (OEF 2011 raporu, Physics Reports 2016, Hardebeck 2022 vb.). dv/v çekirdeğini sınama çekirdeğiyle birlikte kullanan bir **sınama** çalışması yok, boşluk doğrulandı. A×Marmara k=27 (J=0,0138); kontrol Marmara×ETAS k=3 (J=0,0011). Ancak A×Marmara kesişiminin çoğu S dalgası ayrılması ve anizotropi çalışmaları; Marmara dv/v serisi değil.

### Cited Findings
Tohumlar (`kayit/turetme/kopru/dvv/tohumlar.json`):
- A (11): Brenguier 2008, Wegler 2007, Hobiger 2016, Brenguier 2014, Rivet 2011, Hillers 2014, Sens-Schönfelder 2019, Niu 2008, Chiarabba 2020, Taira 2009, Crampin 1999. Atıf eden küme boyu 1496.
- B (6): Schorlemmer 2007 RELM ([10.1785/gssrl.78.1.17](https://doi.org/10.1785/gssrl.78.1.17)), Zechar 2010 ([10.1785/0120090192](https://doi.org/10.1785/0120090192)), Rhoades 2011 ([10.2478/s11600-011-0013-5](https://doi.org/10.2478/s11600-011-0013-5)), Bird 2015 GEAR1 ([10.1785/0120150058](https://doi.org/10.1785/0120150058)), Savran 2022 pyCSEP ([10.1785/0220220033](https://doi.org/10.1785/0220220033)), Zechar & Jordan 2008 Molchan ([10.1111/j.1365-246x.2007.03676.x](https://doi.org/10.1111/j.1365-246x.2007.03676.x)). Küme boyu 634.
- KONTROL: Ogata 1988 ETAS ([10.1080/01621459.1988.10478560](https://doi.org/10.1080/01621459.1988.10478560)). Küme boyu 2349.
- M (6): Ergintav 2014, Silivri 2019 (GJI 2020), Peng & Ben-Zion 2004, Bohnhoff 2013, GONAF 2017, Seismica 2025. Küme boyu 488.

| Köprü | k | J |
|---|---|---|
| A × B | 6 | 0,0028 |
| **Pozitif kontrol B × ETAS** | 183 | 0,0654 |
| A × ETAS | 13 | 0,0034 |
| A × Marmara | 27 | 0,0138 |
| Kontrol Marmara × ETAS | 3 | 0,0011 |
| A × B × Marmara | 0 | 0 |

- A×B'nin 6 işi: Hardebeck 2022 (aftershock konumları ve kabuk özellikleri, [10.1029/2022jb024727](https://doi.org/10.1029/2022jb024727)), Çin sayısal tahmin yol haritası 2018, İstatistik fizik derlemesi 2016 ([10.1016/j.physrep.2016.03.002](https://doi.org/10.1016/j.physrep.2016.03.002)), Parkfield tekrarlayan depremlerin öngörülebilirliği 2012, OEF raporu 2011 ([10.4401/ag-5350](https://doi.org/10.4401/ag-5350)), "Earthquake Prediction and Forecasting" 2004. Kaynak: kopru_rapor.json.
- A×Marmara'nın 27 işinin çoğu S dalgası ayrılması (Hindistan, Puebla, Euboea, Tyrnavos, Samos, Fuji) ve Parkfield dv/v (Okubo 2024). Marmara'ya özgü olanlar: Acarel tezi, Polat 2012 Manyas, Peng & Ben-Zion 2005.

### Inferences
- A×B/B×ETAS J oranı ≈0,04: dv/v çekirdeği, sınama literatürüyle ETAS'ın kurduğu bağın yaklaşık 1/23'ü kadar bağlı. Kesişimdeki işler de sınama değil derleme. Boşluk **gerçek ve derin**. Kimse dv/v'yi CSEP biçiminde puanlamamış. Bu iki şekilde okunabilir: ya yapılmamış bir fırsat, ya da alan içinden "öncül sinyal yok, puanlanacak bir şey yok" yargısı. S1'deki olumsuz örüntü ikinci okumayı destekliyor.
- A×Marmara > Marmara×ETAS sonucu, Marmara tohum kümesinin jeofizik ağırlıklı olmasından kaynaklanıyor olabilir; kontrol zayıf. Kesişimdeki işlerin içeriği Marmara'da dv/v serisi olmadığını doğruluyor.
- A×ETAS (k=13) A×B'den (k=6) büyük: dv/v literatürü sınama yerine tetikleme ve fizik tartışmalarına bağlanıyor.

### Gaps
- Köprü yalnız OpenAlex atıf grafiğine dayanıyor; atıf eksikleri k'yı küçültebilir. Kontroller aynı kaynaktan geldiği için oran yine de karşılaştırılabilir.

## S5. Hangi 0 € sınama mümkün? Hedef sayısı, ölçülebilir en küçük etki

### Takeaway
Marmara içinde tahmin sınavı kurulamaz: 2011+ KO döneminde M6+ yalnız 1 olay. Puanlanabilir tek yol, açık sürekli verili M6+ olaylarda **çok olaylı, ön kayıtlı, rakip pencereye karşı** bir dv/v öncül sınavı (DV-2). Literatüre göre beklenen etki sıfıra yakın. Kaba güç hesabı, ≤0,1 nat/olay etkileri yüzlerce olay olmadan ayırt edemiyor. En gerçekçi değer Marmara gürültü tabanını ve kosismik duyarlılığı ölçmek (DV-1); bu, "tektonik yüklenme Marmara'da ölçülebilir mi" sorusunu kesin yanıtlar. Zaman eksenini daraltan bir sonuç **beklenmiyor**.

### Cited Findings
- Sınama araçları açık: pyCSEP ([10.1785/0220220033](https://doi.org/10.1785/0220220033)), Molchan/alan beceri skoru ([10.1111/j.1365-246x.2007.03676.x](https://doi.org/10.1111/j.1365-246x.2007.03676.x)), log olabilirlik testleri ([10.1785/0120090192](https://doi.org/10.1785/0120090192)).
- Japonya'da dv/v'nin gerçek zamanlı ulusal izleme sistemi var (Hi-net). Olası çok olaylı veri kaynağı, ama erişim koşulu doğrulanmadı. — [EPS 2020, 10.1186/s40623-020-1147-y](https://doi.org/10.1186/s40623-020-1147-y)
- Defter: TK-1'de Türkiye M≥5 için etkin N≈40'ta MDE 0,45 nat/olay. Bu, olay başına log skor farkının standart sapmasının ≈1 nat olduğunu ima ediyor (0,45·√40/2,8 ≈ 1,0). Kaynak: `kayit.py ara hız` çıktısı, TK-1 kaydı.

### Inferences (kaba güç hesapları)
- **Bilgi kazancı ölçeği:** σ≈1 nat/olay, tek yanlı α=0,05 ve güç 0,8 için gereken N ≈ (2,49·σ/Δ)². Δ=0,45 → N≈31; Δ=0,3 → N≈69; Δ=0,1 → N≈620; Δ=0,05 → N≈2500.
- **Molchan (ikili alarm) ölçeği:** alarm zaman payı τ, isabet oranı h için N ≈ 6,2·τ(1−τ)/(h−τ)². τ=0,1 ile h=0,3 → N≈14; h=0,2 → N≈56; h=0,15 → N≈220. h=0,2, τ=0,1 alarmının olay başına bilgi kazancı ≈0,2·ln2 + 0,8·ln(0,8/0,9) ≈ **0,04 nat**. Bu, zaman eksenini anlamlı daraltmaz.
- **Hedef sayısı (kaba, kaynaksız tahmin):** dünyada yılda ~130–150 sığ M6+ var (genel bilgi, bu oturumda kaynaklanmadı). 2005–2025'te ≤50 km içinde ≥2 yıl öncesi açık sürekli kaydı olan kıta ve kabuk M6+ olay sayısı bilinmiyor; kaba tahmin birkaç yüz. Bu sayı DV-2'nin ilk adımında (IRIS/EIDA fedcatalog + ISC-GEM/GCMT) ölçülmeli. Türkiye dışı 2026 olayları ve 2027 sonrası kör tutulmalı.
- **DV-1 gürültü ölçütü:** Marmara'da çevresel model (sıcaklık, yağış, deniz düzeyi) sonrası kalan σ(dv/v) yıllık eğilim belirsizliği <%0,02/yıl ise, Sθ≈5×10³ ve 10⁻⁷/yıl ile beklenen %0,05/yıl sığ yanıt iki sigma düzeyinde ayırt edilebilir. Bu, gerilme **hızını** ölçer, kırılmaya yakınlığı ölçmez.
- **Hesap yükü (0 €):** DV-1 tek istasyonlu otokorelasyon veya kısa mesafeli çapraz korelasyonla ~5–10 KO istasyonu × 15 yıl gerektirir. 20–100 Hz'den 10 Hz'e düşürülmüş HHZ/HH? verisi istasyon-yılı başına kabaca birkaç GB eder (kaba). Yerel makinede günler ölçeğinde. Bu notta indirme yapılmadı.

### Aday tablosu

| aday adı | soru | köprü k ve J (kontrolle) | veri ve erişim | hedef sayısı ve kaba güç | zaman eksenine bağı | en büyük risk |
|---|---|---|---|---|---|---|
| **DV-1 Marmara dv/v gürültü tabanı ve 2019/2025 kosismik duyarlılık (ön kayıtlı betimsel sınav)** | KO verisiyle 2011–2026 dv/v serisinde (a) çevresel model sonrası kalan gürültü tabanı nedir, (b) 2019 M5,8 ve 2025 M6,2 öncesindeki 12 ayda, ön kayıtlı eşikle, olay dışı aynı uzunluktaki pencerelere göre sapma var mı, (c) %0,05/yıl tektonik eğilim saptanabilir mi? | A×Marmara k=27, J=0,0138; kontrol Marmara×ETAS k=3, J=0,0011. Marmara dv/v serisi kesişimde yok, boşluk doğrulandı. | KO, EIDA dataselect açık (HTTP 200 doğrulandı), 2010+ ≥19 istasyon; meteoroloji açık (ERA5, kayıtla ücretsiz). GONAF/PIRES sürekli akışı doğrulanamadı. | N=1 M6+ (+1 M5,8): tahmin sınavı değil. Güç ölçütü: eğilim belirsizliği <%0,02/yıl ise kâğıt üzerindeki %0,05/yıl sığ yanıt 2σ'da görülür. | Dolaylı: gerilme **hızını** ölçer (GNSS zaten veriyor). Kırılmaya uzaklık vermez. Olumsuz sonuç kolu kapatır. | 1999 İzmit/Düzce ve 2019/2025 iyileşme eğrileri tektonik eğilimle karışır (Okubo 2024'te işaret çelişkisi). Sonuç ayırt-edilemez olur. |
| **DV-2 Çok olaylı küresel dv/v öncül sınavı (Molchan + bilgi kazancı, rakip: olay dışı pencere / ETAS-eşli zaman)** | Açık sürekli verili M6+ kabuk depremlerinde, olay öncesi 1–12 ay dv/v sapması (ön kayıtlı istatistik), aynı istasyonun rastgele veya ETAS'a göre sakin pencerelerine göre fazla mı? | A×B k=6, J=0,0028; pozitif kontrol B×ETAS k=183, J=0,0654 (≈23 kat). Hiç puanlanmamış, boşluk derin. | IRIS/EIDA/GEOFON açık; Japonya Hi-net kayıt gerektirebilir (doğrulanmadı). İndirme hacmi yüksek ama ücretsiz. | Kaba N birkaç yüz (ölçülmeli). Δ=0,3 nat için N≈69; Δ=0,1 için N≈620. τ=0,1, h=0,2 için N≈56; bu alarmın kazancı ≈0,04 nat. | Doğrudan: olumlu sonuç ay ölçeğinde zaman daraltır. Literatür beklentisi sıfır etki. | Seçim yanlılığı (yalnız iyi kayıtlı olaylar), istasyon başına çevresel modelin el ayarı (serbestlik derecesi şişmesi, Seher & Main 2004 dersi), hesap ve indirme yükü. Beklenen sonuç: H0. |
| **DV-3 Kosismik dv/v "duyarlılığı" uzamsal ortak değişken (Brenguier 2014 fikri)** | 2019 ve 2025 olaylarının yol açtığı dv/v düşüş büyüklüğünün istasyonlar arası dağılımı, sonraki 1 yılda M≥3 sismisitenin uzamsal dağılımını, düzgünleştirilmiş sismisiteye ve ETAS'a karşı bilgi kazancıyla açıklıyor mu? (Hardebeck 2022'de kabuk özellikleri artçı yoğunluğunu açıklıyordu.) | A×ETAS k=13, J=0,0034 (Hardebeck 2022 kesişimde); kontrol B×ETAS k=183. | DV-1 ile aynı KO verisi + KOERI kataloğu. | Hedef M≥3 olaylar (yüzlerce, KOERI). Uzamsal çözünürlük istasyon sayısıyla (~20) sınırlı. Etkin serbestlik küçük. | **Yok ya da zayıf**: uzamsal. Yıl ölçeğinde zaman eksenini daraltmaz. | ~20 istasyonla uzamsal güç çok düşük. Defterdeki uzamsal adaylarla (DT-2, Alhan & Khabat 2026: konum zaten belli) örtüşür. |

**Önerilmeyenler (literatür gereği):** S dalgası ayrılması stres tahmini. Seher & Main 2004 Poisson'u reddedemedi; Peng & Ben-Zion 2005 Düzce'de öncül bulmadı; Polat 2012 Manyas'ta tek istasyon, geriye dönük. FA-6 ile aynı aile. Koda-Q ve sönüm zaman değişimi: hiposantr göçü karışıklığı var, sınanmış öncül yok.

**Genel hüküm:** dv/v ve akraba sürekli dalga formu ölçülerinin fayın **anlık gerilme durumunu ya da kırılmaya uzaklığını** ölçtüğü **kanıtlanmadı**. En iyi durumda sığ kabukta gerilme **değişimine** duyarlılar. Öncül iddiaları tek olaylı ve geriye dönük. Puanlanmış çok olaylı sınav yok. DV-1 ucuz ve kolu kapatıcı; DV-2 tek gerçek sınav ama beklentisi H0; DV-3 zaman eksenine bağlı değil.

### Gaps
- Açık veriyle DV-2'ye uygun M6+ olay sayısı ölçülmedi. "Birkaç yüz" kaba ve kaynaksız.
- Olay başına σ≈1 nat varsayımı TK-1'den (Türkiye M≥5, bir yıllık vade) taşındı. dv/v pencere istatistiği için farklı olabilir.
- Marmara'da kabuk gerinim hızı 10⁻⁷/yıl varsayımı kaynaklanmadı. Ergintav 2014 sayıları bu oturumda okunmadı.
