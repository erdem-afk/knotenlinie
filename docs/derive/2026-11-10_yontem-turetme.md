# İstanbul için hazırlanmamış yöntemlerden İstanbul'a türetme: bölgeden bağımsız yöntemler (10 Kasım 2026)

Erdem (10 Kasım 22:18): "önceki çalışmalardan yeni çalışma derive edelim, İstanbul odaklı fakat İstanbul için hazırlanmamış, benzer çalışmalardan yola çıkarak". Bu belge bölgeden bağımsız yöntem aileleri koludur (ML katalogları ve nöral tahmin, laboratuvar/rate-state, simülatör kalibrasyonu, Bayesçi birleştirme, CSEP dersleri, BPT ötesi tekrar, gerinim–sismisite).

Salt tarama ve okuma, 0 €, hiçbir şey koşulmadı, makine kiralanmadı. Olasılık yazılmaz. Seçim Erdem'in. Türkiye dışı 2026 verisine dokunulmadı.

## 1. Ölçüm (Erdem yöntemi: köprü sorusu, eş-atıf kesişimi, pozitif kontrol)

Köprü sorusu: "Yöntem ailesi X, Marmara M7 literatürüyle konuşuyor mu?" Ölçü: X'in tohum makalelerine VE Marmara çekirdeğine birlikte atıf yapan iş sayısı (k) ve Jaccard (J). Aynı ailenin sınama çekirdeğiyle (GEAR1, CSEP; 8 Kasım'ın 5 makalesi) kesişimi ikinci satır: yöntem tahmin sınamasına girmiş mi.

Kaynak OpenAlex (anahtarlı). Marmara çekirdeği 8 iş: Parsons 2000, 2004; Murru 2016; Bohnhoff 2013; Ergintav 2014; Lange 2019; Le Pichon 2003; Armijo 2005 (1.280 atıf yapan). Tohumlar `tools/literatur/derive/tohumlar_derive_yontem.json` (DOI'ler başlık aramasıyla doğrulandı), rapor `oa_kesisim_rapor_derive_yontem.json` (kesişen işler başlıklarıyla).

| Köprü | × Marmara k / J | × Sınama k / J | Üçlü (X ∩ Marmara ∩ Sınama) |
|---|---|---|---|
| **Pozitif kontrol** Marmara × Coulomb (Stein 1997, King 1994) | 375 / 0,089 | — | — |
| Pozitif kontrol sınama × ETAS | — | 164 / 0,061 | — |
| Kalibrasyon Marmara × ETAS | 28 / 0,0078 | — | — |
| Laboratuvar / rate-state (Dieterich 1994, Marone 1998, Rouet-Leduc 2017) | 122 / 0,024 | 61 / 0,014 | 6 |
| BPT ötesi tekrar (Salditch 2020 LTFM, Rhoades–Van Dissen 2003, aperiyodiklik testi) | 10 / 0,0069 | 7 / 0,010 | 1 (kaynakça) |
| Simülatör kalibrasyonu (Shaw 2018 RSQSim, Dieterich–Richards-Dinger 2010, Khodaverdian 2016 KB İran, MPS19 İtalya) | 7 / 0,0046 | 8 / 0,011 | 1 (OEF raporu) |
| ML katalogları (PhaseNet, EQTransformer, Ross 2019) | 14 / 0,0041 | 10 / 0,0037 | 0 |
| CSEP dersleri (RELM 2010/2013, pyCSEP, Bayona 2022, Cattania 2018) | 5 / 0,0031 | 170 / 0,257 | 2 (rapor, kaynakça) |
| **Gerinim × sismisite melezi** (Bird–Kreemer 2015, Rhoades 2017, NZ NSHM 2022, Hindistan 2018) | **2 / 0,0014** | 64 / 0,109 | 1 (derleme) |
| Nöral nokta süreçleri (Dascher-Cousineau 2023, Stockman 2023, Zlydenko 2023, SB-ETAS) | 1 / 0,0007 | 9 / 0,015 | 0 |
| **Bayesçi birleştirme / hiyerarşik** (Marzocchi 2012, Rhoades 2013, Marzocchi–Jordan 2014, Nomura 2011, Fitzenz 2012) | **1 / 0,0006** | 77 / 0,106 | 0 |

Okuma: Marmara köprüsünün pozitif kontrolü 0,089. Laboratuvar/rate-state dışında hiçbir aile Marmara'ya onda birden fazla yaklaşmıyor. En net boşluklar sınama literatüründe yoğun (J ≈ 0,1) ama Marmara'da sıfıra yakın olanlar: **Bayesçi birleştirme (k 1, ilgisiz: Afrika)** ve **gerinim × sismisite melezi (k 2, ikisi de derleme)**. Laboratuvar/rate-state boşluk değil (CRS+ETAS da kuruldu).

## 2. Doğrudan öncüller (kesişimlerin ve anahtar kelime aramalarının okunması)

- **Alhan ve Khabat 2026, EarthArXiv** (10.31223/x5w78x): Marmara'da sızıntı denetimli ML ve ETAS. ETAS×ML melezi düzgün kurulmuş ETAS'ı bilgi kazancında geçemiyor (−0,38 nat/olay). Nöral/ML kısa vade kolunun Marmara'daki öncülü ve sonucu olumsuz.
- **Fabisch, Bohnhoff, Martínez-Garzón 2026, JGR** (10.1029/2026jb034241): GONAF kuyu verisi + derin öğrenme faz seçimiyle 2016–2023 altı Marmara dizisi; olay sayısı ≈8 kat. ML katalog kolu Marmara'da yapılmış; tahmin sınaması yok.
- **Chartier, Scotti, Lyon-Caen, Richards-Dinger 2021, NHESS** (10.5194/nhess-21-2733-2021): SHERIFS ile Marmara fay sistemi oranları; mantık ağacında CMF kilit durumu, en büyük kırılma, MFD şekli; dallar katalog + paleosismik uyumla ve RSQSim sonuçlarıyla ağırlıklandırılıyor. Simülatör kalibrasyonunun Marmara öncülü; bizim S5 (ABC) ve v2.x hattıyla yakın.
- **Nas, Bayrak vd. 2024, J. Seismol.** (10.1007/s10950-024-10244-1): KAF boyunca ters Gauss ve lognormal yenilenme. BPT ailesi içinde; uzun süreli fay belleği (LTFM) ya da kümelenme modeli KAF'ta uygulanmamış.
- Gerinim × sismisite, Bayesçi birleştirme, hiyerarşik havuzlama için Marmara ya da Türkiye öncülü bulunamadı (6 hedefli arama + kesişim başlıkları). ESHM13/20 Türkiye'de fay + sismisite toplayan (çarpımsal değil) modeller kullanıyor.

## 3. Sıralı adaylar

İstanbul belirsizliğinin bugünkü kaynakları (panel #demir, v1.6 ve S3 sonrası): uzamsal eksen (%37–46), dal içi parametreler (%32–38; moment dalı %14 + istatistik dalı oranı %12 + Parsons σ %6), tekrar ve zaman (%4–13), CMF/PIF kilitlenmesi (CMF 11 ± 3 mm/yıl; PIF ölçülemiyor), segment birleşimi ve ortak kırılma.

Hepsi için ortak kural: ön kayıt veriden önce dondurulur (OTS), tek koşu, sonuç ileri test defterine rakip olarak girer, v1.3b değişmez. Veri yalnız açılmış ≤2025 geliştirme verisi; Türkiye dışı 2026 okunmaz.

### D1. Çarpımsal gerinim × sismisite melezi (uzamsal eksen) — önerilen 1

- **Kaynak:** Rhoades, Christophersen, Gerstenberger 2017 GJI (çarpımsal olabilirlik modelleri, gerinim hızlı); Bayona vd. 2022 GJI (Kaliforniya'da çarpımsal melezlerin ileriye dönük sınavı); Bird ve Kreemer 2015 BSSA (GSRM 2.1 tektonik tahmin); NZ NSHM 2022 sismisite oran modeli (Gerstenberger vd. 2024).
- **İstanbul'a taşıma:** v1.2'nin uzamsal ekseni toplamalı karışım (ETAS 0,5 + gerinim 0,5). Çarpımsal melez log-doğrusal: λ ∝ λ_ETAS^a · ε̇^b, normalize. Üsler Türkiye dışı açılmış 223 doğrultu atımlı olayda (v1.2 seti) blok LOO ile seçilir, Marmara segment paylarına aynen taşınır.
- **Boşluk kanıtı:** gerinim × sismisite köprüsü sınamada J 0,109, Marmara'da 0,0014 (k 2, ikisi derleme); Türkiye'de çarpımsal melez yok.
- **H1:** çarpımsal − toplamalı > MDE (223 olay, blok SE). **H0:** fark MDE içinde → toplamalı 0,5 kalır, aday kapanır. Bilgi satırı: 2016–25 Türkiye M≥6 (N 12) ve D3 M7 (18 olay).
- **Veri ve sızıntı:** Sun 2026 ve Elliott 2026 gerinim dosyaları sunucuda; GSRM 2.1 açık; ETAS haritaları depoda. Hepsi geliştirme verisi. Kısmi körlük: v1.2 aynı 223 olayla seçildi; bu ön kayıtta açıkça yazılır.
- **İstanbul M7+ beklenen katkısı:** en büyük pay olan uzamsal eksene doğrudan dokunan tek yöntem. K3'te (v1.6) M7'de ağırlığın 0,5'ten ayrılmadığı görüldü; çarpımsal biçim farklı bir fonksiyon, sonuç önceden bilinmiyor. Dürüst beklenti: küçük ila orta; büyük olasılıkla "ayırt edilemez".
- **Maliyet/süre:** 0 €, 2–3 gün.

### D2. Analog doğrultu atımlı faylardan hiyerarşik Bayes havuzlama (istatistik oranı + Parsons σ) — önerilen 2

- **Kaynak:** Nomura, Ogata, Komaki, Toda 2011 JGR (küçük örnekte Bayesçi tekrar tahmini); Fitzenz, Jalobeanu, Ferry 2012 BSSA (faya özgü tekrar modellerini Bayesçi sıralama ve birleştirme); Marzocchi, Zechar, Jordan 2012 BSSA (Bayesçi tahmin değerlendirme ve topluluk); hiyerarşik kısmi havuzlama (genel istatistik yöntemi).
- **İstanbul'a taşıma:** Marmara segmentlerinde M7 sayısı az, oranı ve aperiyodikliği kendi kaydından kestirmek geniş aralık veriyor. Açılmış 17 fay grubu (31 kronoloji, 296 olay; v1.3 seti) ve Marmara paleosismik kaydı (v1.5) tek hiyerarşik modelde: segment oranı ve σ bir üst dağılımdan, Marmara kısmen havuzlanır. Çıktı moment dalı dışındaki iki dal içi kaynağı (istatistik oranı %12, Parsons σ %6) hedefler.
- **Boşluk kanıtı:** Bayesçi birleştirme × sınama J 0,106, × Marmara k 1 (ilgisiz). Türkiye'de hiyerarşik tekrar modeli bulunamadı.
- **H1:** hiyerarşik model − bağımsız (havuzsuz) model > MDE (grup dışarıda bırakma log skoru, 17 grup). **H0:** fark yok → havuzlama Marmara'ya taşınmaz.
- **Veri ve sızıntı:** tamamı açılmış geliştirme verisi; yeni veri yok.
- **İstanbul M7+ beklenen katkısı:** dal içi payın yaklaşık yarısına (%18) dokunur. Havuzlama işe yararsa en olası etki aralığın daralması; ortalamanın kayması küçük.
- **Maliyet/süre:** 0 € (sunucuda MCMC), 3–4 gün.

### D3. Uzun süreli fay belleği (LTFM) ve kümelenme: BPT'nin yenildiği yerde Poisson'un tek alternatifi olmamak — önerilen 3

- **Kaynak:** Salditch, Stein, Neely vd. 2020 Tectonophysics (süper döngüler ve LTFM); Rhoades ve Van Dissen 2003 (Alpine Fay zamana bağlı tehlike); Zöller vd. 2007 NHESS (küçük örnekte aperiyodiklik testi).
- **İstanbul'a taşıma:** v1.3'te 17 grupta BPT Poisson'a −171,8 nat kaybetti; MCQsim simülasyonlarında da döngüler kümeli. LTFM, her depremin birikmiş gerinimin yalnız bir kısmını boşalttığı ve kümelenme üreten bir yenilenme modeli; BPT'nin tersine kümeli kayıtlarda Poisson'u geçebilir. Aynı 17 grupta sınanır, kazanırsa Marmara'ya (1509, 1766, 1894, 1912, 1999 dizisi; CMF'de 1766'dan beri olay yok) taşınır.
- **Boşluk kanıtı:** BPT ötesi × Marmara k 10, hepsi BPT/lognormal/ters Gauss ailesi (Nas 2024) ya da paleosismik derleme; KAF'ta LTFM ya da kümelenme modeli yok.
- **H1:** LTFM − Poisson > 0 (grup dışarıda bırakma, 17 grup, toplam nat ve grup başına SE). **H0:** Poisson 0,95 kalır.
- **Veri ve sızıntı:** açılmış 296 olay + Marmara paleo + EPICA (kısmi körlük kayıtlı).
- **İstanbul M7+ beklenen katkısı:** zaman payı bugün %4–11, aralığa katkısı küçük. Ama ortalamayı en çok oynatabilecek aday bu: LTFM, 1766'dan beri boşalmamış CMF gerinimini "bellek" olarak sayar. Kazanma olasılığı düşük (BPT'nin ağır yenilgisi), sonucu her iki yönde öğretici.
- **Maliyet/süre:** 0 €, 2–3 gün.

### D4. SHERIFS sistem MFD'si: CMF kilit hipotezlerini yeni kanıtla yeniden ağırlıklandırmak ve dış rakip

- **Kaynak:** Chartier, Scotti vd. 2017–2021 (SHERIFS; Marmara uygulaması 2021, RSQSim ile dal ağırlığı).
- **İstanbul'a taşıma:** SHERIFS kayma hızlarını sistem düzeyinde bir MFD'ye uyan çok faylı kırılma oranlarına çevirir. 2021 mantık ağacında CMF kilit durumu ana dallardan biri, ama 2016+ deniz tabanı kanıtı (bizim v1.8: kısmen kilitli; Y1b: CMF 0–12 km 11 ± 3 mm/yıl) yoktu. Açık kodla Marmara modeli bizim kilit ve kayma açığı sonsalımızla yeniden koşulur. İki çıktı: (a) yayımlanmış modelin yeniden üretimi ileri test defterine dış rakip (CSEP dersi: güçlü dış model olmadan kazanç ölçülmez); (b) CMF+PIF ortak kırılma oranı, v1.7 (f ≈ 0,10) ve S1 (geçiş P 0,21–0,85) ile karşılaştırma.
- **Boşluk kanıtı:** öncül var (Chartier 2021) ama 2016+ kilitlenme kanıtıyla güncellenmemiş ve ileriye dönük sınava girmemiş. Yenilik iddiası "yeni yöntem" değil, "yeni kanıtla güncelleme + defterde sınav".
- **H1/H0:** (a) için hüküm yok, rakip satırı. (b) SHERIFS ortak kırılma oranı v1.7'nin %10–90 aralığı dışındaysa v1.7'ye bilgi satırı; içindeyse bağımsız teyit.
- **Veri ve sızıntı:** EDSF13 (sunucuda), yayımlanmış kayma hızları, bizim v1.8 sonsalı; hepsi ≤2025.
- **İstanbul M7+ beklenen katkısı:** segment birleşimi ve ortak kırılma sorusuna simülatörden bağımsız ikinci bir yol; v2.x hattının (MCQsim) çapraz kontrolü. Nihai v1.3b'ye etkisi küçük (moment dalı 0,05).
- **Maliyet/süre:** 0 € (SHERIFS dizüstü ölçeğinde koşuyor; sunucuda), 3–5 gün. S5 (ABC) thread'iyle çakışmaması için onunla eşgüdüm.

### D5. Ontolojik hata testi ve istifleme (stacking): ileri test defterindeki 10+ sürüm tek tahmine nasıl iner?

- **Kaynak:** Marzocchi ve Jordan 2014 PNAS (ontolojik hata testi); Marzocchi vd. 2012 (Bayesçi topluluk); Rhoades 2013 BSSA (karışım modelleri).
- **İstanbul'a taşıma:** defterde v1.3b nihai, yanında 10'dan fazla rakip (v1.4–v1.9m, v2.x). Hepsinin tutarlılık satırları (D4', EPICA, 2016–25) zaten var. (a) Ontolojik test: tarihsel Marmara kaydı ve EPICA, topluluğun öngörü dağılımının içinde mi? Dışındaysa "hiçbir dal doğruyu içermiyor" uyarısı. (b) LOO istifleme ağırlıkları: sürümleri seçmek yerine birleştirme; v1.3b değişmez, istif yalnız defterde ek rakip.
- **Boşluk kanıtı:** D2 ile aynı köprü (Bayes × Marmara k 1).
- **H1:** istif − v1.3b > MDE tutarlılık satırlarında. **H0:** fark yok (beklenen; satırlar az olaylı). Ontolojik test hükümden bağımsız raporlanır.
- **Veri ve sızıntı:** defter çıktıları; yeni veri yok. Kısıt: tutarlılık satırları ağırlık seçiminde de kullanıldıysa iki kez sayma, ön kayıtta ayrılır.
- **İstanbul M7+ beklenen katkısı:** aralığı daraltmaz; aralığın dürüst olup olmadığını söyler. 1 Ocak 2027 ileri testine "topluluk" satırı ekler.
- **Maliyet/süre:** 0 €, 1–2 gün.

## 4. Açmamayı önerdiklerim

- **Nöral nokta süreçleri / ML ile kısa vade tahmin:** Marmara'da yapılmış (Alhan ve Khabat 2026), sonuç ETAS'ı geçemiyor; EarthquakeNPP kıyas setinde de (2024) nöral modeller ETAS'ı genelde geçmiyor. M7 gücü yok; bizim Bayesçi ETAS ve CRS+ETAS zaten aynı rolde.
- **ML ile yeniden işlenmiş Marmara kataloğu:** Fabisch 2026 GONAF ile yaptı. Bizim için tek kullanım uzamsal eksen olurdu, ama S3 (H0) sismisitenin M7 yerini tekdüzeden iyi bilmediğini gösterdi. Dalga biçimi işleme makine ister.
- **Laboratuvar / rate-state:** boşluk değil (Marmara köprüsü J 0,024); CRS+ETAS kuruldu. Laboratuvarda ML ile deprem zamanı tahmini (Rouet-Leduc 2017) doğal faylara taşınamadı.

## 5. Önerilen sıra

D1 ve D3 önce ve paralel (0 €, en kısa, ikisi farklı eksen). D2, D1'den sonra (aynı sunucu MCMC). D5 boşta, 1 gün. D4, S5 ile eşgüdüm gerektirdiği için en son. Hiçbiri Erdem seçmeden başlamaz.

## Sınırlar

Kesişim ölçüsü tohum seçimine bağlı; her ailede 3–5 tohum. Anahtar kelime araması İngilizce; Türkçe dergiler eksik kalabilir. OpenAlex harcaması ≈250 kredi (günlük 10.000; paylaşılan anahtar). "Beklenen katkı" cümleleri tahmindir, ölçüm değil.
