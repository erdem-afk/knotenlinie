# Kol VE — viskoelastik gevşeme, afterslip, zamana bağlı yüklenme hızı (11 Kasım 2026)

Kural denetimi: K10 `kapali-sartli`. Bu kol K10'u **yeniden açmıyor**; F-CRS V2 şart metni sunucuda, buradan okunamadı. Aşağıdaki "şart önerisi" yalnız öneridir, karar Erdem'in.
Yöntem notu: bu oturumda Agent aracı yoktu; alt ajan açılamadı, tarama tek elden yapıldı (Crossref + OpenAlex özetleri + OpenCitations). Tam metin okunmadı; aşağıdaki sayılar **özetten** (aksi yazılmadıkça).

## (a) Tarama özeti

Köprü ölçümü (OpenCitations Index v2, `bosluk_olc_v3.py` yöntemi; tohumlar `VE.doi.txt` içinde):

| Köprü | \|A\| | \|B\| | k | Jaccard |
|---|---|---|---|---|
| Pozitif kontrol: CRS (5 tohum) ∩ CSEP sınama (3 tohum) | 232 | 309 | 48 | 0,097 |
| Viskoelastik gerilme aktarımı (10 tohum) ∩ CSEP sınama | 607 | 309 | 10 | 0,011 |
| İzmit postsismik jeodezi (7 tohum) ∩ CSEP sınama | 593 | 309 | 1 | 0,001 |
| Viskoelastik ∩ Marmara (5 tohum) | 607 | 458 | 27 | 0,026 |
| Viskoelastik ∩ CSEP ∩ Marmara | | | **0** | |

Viskoelastik∩CSEP'teki 10 işin okunabilenleri derleme, CRS ya da hibrit işi (Hardebeck 2024 derlemesi, Savran 2020, Bayona 2022, Marzocchi 2008, Jia 2020); hiçbiri viskoelastik yüklenmeyle M7 zamanını puanlamıyor. İzmit postsismik∩CSEP'teki tek iş Hardebeck 2024.

Soru 1 — viskoelastik yüklenme sonraki büyük depremin zamanını sınadı mı, log skorla mı?
- Landers→Hector Mine (Freed & Lin 2001; Zeng 2001; Pollitz & Sacks 2002): olay sonrası açıklama, N = 1, puan yok.
- KAF 1939–1999: Lorenzo-Martín 2006 ve DeVries 2016 (G3) geriye dönük. DeVries 2016 tarihli tek ifadeyi veriyor: Marmara kuzey kolunda ortalama zamana bağlı gerilme "2023'e kadar" önceki KAF depremlerinin görünür eşik ortalamasına ulaşabilir. Eşik aralığı 0,02–3,15 MPa (iki mertebe). 2023 geçti, M7 olmadı; ifade olasılık biçiminde olmadığı için puanlanamaz.
- Sumatra: McCloskey 2005 (elastik, olaydan önce yayımlandı, N = 1, puansız); Pollitz 2006 viskoelastik, puansız.
- Wasatch (Verdecchia 2019): kosismik + postsismik ΔCFS olasılığa çevrilmiş, sınanmamış.
- Log olabilirlik kullananlar: Pollitz & Cattania 2017 (G. Kaliforniya 1981–2014, küçük deprem uzamsal deseni, örnek içi; statik ve viskoelastik ikisi de katkı veriyor) ve Cattania 2015 (afterslip, Parkfield ve Tohoku, örnek içi; etki haftalar–aylar). İkisi de M7 zamanı değil, ikisi de ileriye dönük değil.
- Sözde-ileriye dönük CSEP sınamaları (Segou & Parsons 2014, Cattania 2018, Mancini 2019/2020, Strader & Jackson 2015) viskoelastik terim içermiyor.
- Denali ve Tohoku için M7 zaman sınaması bulunamadı (tarama tüketici değil).
Sonuç: viskoelastik yüklenmeyle büyük deprem zamanının ileriye dönük, log skorlu sınaması bulunamadı.

Soru 2 — Marmara reoloji kısıtları daraldı mı? Hayır.
- Hearn 2009: geçici 2–5×10^19, kalıcı ≥ 2×10^20 Pa s (Burgers manto). Wang 2009: alt kabuk ~2×10^18 (SLS), manto 7×10^19. Yamasaki 2014: fay altı zayıf zon ~10^18, dışı > 10^20. DeVries 2016: Maxwell 4×10^18–10^19, Kelvin 10^18–10^19. Hussain 2018: alt kabuk > ~10^20, zayıf fay zonu; gerinim hızı depremden sonraki ~10 yıl dışında sabit. Özarpacı 2021: 20 yıl sonra süren deformasyon yalnız logaritmik afterslip ile açıklanıyor. Wang 2025 (EGU özeti, Doğu Anadolu 2023): üst manto < 10^19.
- Kalıcı viskozite 4×10^18 ile > 10^20 arasında (gevşeme süresi kabaca 5–10 yıldan > 100 yıla); mekanizma (afterslip / yayılı akış / zayıf zon) ayrışmamış. 26 Ekim itirazı literatürle aşılmıyor.
- Görevde anılan işler: Diao 2016 (GJI) reoloji değil kilitlenme makalesi (başlıktan). de Blas 2022 reoloji değil, Anadolu mikrolevhasının rijit hareketinin 1999'la değiştiği iddiası; özet sayı vermiyor. Nalbant 2026 yalnız EGU özeti; viskozite ve gerilme sayısı yok; 2006 Gemlik, 2019 Silivri, 2023 Mudanya, 2025 Silivri için geriye dönük anlatı.
- Ama bu modeller 2010 sonrası hız değişimi için **farklı** öngörü veriyor; bu ayrım GNSS ile ölçülebilir (VE-1).

Soru 3 — ETAS örtüşmesini aşan tasarım: (i) hedefi deprem değil GNSS hız değişimi olan sınama (VE-1; ETAS'la örtüşme tanım gereği yok), (ii) M7 olduğu koşulunda segment sıralaması (VE-2; zaman değil uzam eksenine dokunur).

Soru 4 — açık kod ve girdi: PSGRN/PSCMP (Wang 2006; GFZ, Pyrocko fomosto arka ucu), RELAX (Barbot & Fialko 2010; CIG), PyLith (Aagaard 2013; CIG), VISCO1D v3 (Pollitz 1997; USGS yazılım sayfası açıldı), Unicycle (Moore 2017). GitHub bu oturumda kapalıydı; depo adresleri doğrulanmadı. Girdi: Nevada Geodetic Laboratory günlük seriler (`geodesy.unr.edu/NGLStationPages/DataHoldings.txt` okundu): ISTA 1999-12→2026-10 (9175 çözüm), TUBI 1998-05→2023-06 (8415), TUSAGA-Aktif 2009-01→2023/24: ISTN, IZMT, KARB, SARY, SLEE, TEKR, BAND, BURS, BILE, HEND, NAHA (her biri ~2500 gün). Toplam birkaç on MB. COMET LiCSAR portalı açık.

## (b) Aday tablosu

| Kimlik | Soru | Neden yeni (en yakın işler) | Zaman ekseni | Sınama | Veri | Maliyet | Tür | Hüküm |
|---|---|---|---|---|---|---|---|---|
| **VE-1** | ≤ 2016'da yayımlanmış parametrelerle dondurulmuş gevşeme modelleri, Marmara çevresi GNSS hızlarının 2017+ değişimini "sabit hız"dan iyi öngörüyor mu; bugünkü yüklenme hızı zamanla değişiyor mu, üst sınırı ne? | Hussain 2018 (10.1038/s41467-018-03739-2) sabitliği gerinim profillerinden çıkarıyor, ileriye dönük puan yok; Özarpacı 2021 (10.1093/gji/ggaa560) ve DeVries 2016 (10.1785/0120160059) örnek içi uyum. Rakip modellerin görülmemiş seride log skorla yarışması yok (İzmit postsismik∩CSEP k = 1). | Doğrudan dokunmaz; yüklenme hızının yıl–on yıl değişimine ölçülmüş sınır koyar (K10 için ön koşul). | H0: sabit hız. H1a: 1/t afterslip (Özarpacı). H1b: Burgers (Hearn, DeVries). H1c: zayıf zon (Yamasaki, Hussain). Hedef: istasyon başına 2009–16 ile 2017–23/26 hız farkı (2 yatay bileşen), Gauss log skoru, istasyon bootstrap. N ≈ 13 istasyon. Kaba güç: fark σ'sı ~0,35–0,45 mm/yıl/istasyon; İzmit yakınında beklenen fark ~0,7 mm/yıl (1/t) → H0'a karşı toplamda ~4σ; 1/t ile üstel ayrımı ~2σ (sınırda); Marmara batısında genlik < 1 mm/yıl, çoğunlukla üst sınır çıkar. Sızıntı: modeller ≤ 2016, hedef 2017+; risk: 2019 M5,8, 2023 Şubat, 2025 M6,2 atımları ve anten değişimleri (kural önceden yazılmalı). | Açık, NGL, ~50 MB | 0 €, 2–3 gün (ileri model PSGRN/PSCMP ya da RELAX) | veri | **öner** |
| **VE-2** | M7 olduğu koşulunda, kosismik + viskoelastik ΔCFS sıralaması bir sonraki kırılan segmenti yalnız kosismik ΔCFS'den ve kayma açığından iyi seçiyor mu? | DeVries 2016 (10.1002/2016gc006313), Lorenzo-Martín 2006 (10.1016/j.tecto.2006.03.046), Verdecchia 2016 (10.1002/2015tc004091): hepsi tek dizide geriye dönük, puansız. Defterde M7-D1D4 yalnız elastik Coulomb'u sınadı (−0,02/−0,40). | Zaman eksenine dokunmaz; uzam eksenine (≈ %46) dokunur. Vade: on yıl; M7+. | H1: viskoelastik ekli sıralama log skoru > kosismik. Rakip: kosismik ΔCFS; kayma açığı. Hedef: KAF 1939–99 (7), Sumatra 2004–10 (~5), Bayan Har (~7), DKKZ (3), Moğolistan (~4): kaba N ≈ 25. Güç: olay başı kazanç ~0,3 nat, σ ~1 varsayılırsa t ≈ 1,5: **güç sınırda/yetersiz**. Sızıntı yüksek: fay geometrisi ve reoloji olaydan sonra seçilmiş. | Yayımlanmış tablolar; açık derli toplu veri yok | 0 €, önce 1 gün veri sayımı | literatur | **bekle** (önce N ve sızıntısız alt küme sayılsın) |
| **VE-3** | Gevşeme düzeltmeli yüklenme hızı Marmara M6+/M7+ için zamana bağlı olasılık terimine çevrilebilir mi? | Parsons 2004 (10.1029/2003jb002667) ve Verdecchia 2019 (10.1093/gji/ggz336) yapıyor, sınamıyor. | Yıl–on yıl; M6+/M7+. | Hız çarpanı r için beklenen kazanç ≈ λT·[r ln r − (r − 1)] ≈ λT(r − 1)²/2: r = 1,1'de beklenen olay başına 0,005 nat, r = 1,5'te 0,11 nat. Kendi kaba hesabım (doğrulanmadı): 1999 kaynaklı bugünkü pertürbasyon PIF'te tektonik hızın ≲ %5–10'u. Marmara'da güç yok. | — | — | fizik | **eleme** (güç-yok); K10 kapsamı, K10 açılmadı |
| **VE-4** | DeVries 2016 eşik saatinin 1939–1999 dizisinde birini-dışarıda-bırak karnesi | DeVries 2016; Stein 1997 (10.1111/j.1365-246x.1997.tb05321.x) | Yıl; M7 | N = 7 aralık; eşik 0,02–3,15 MPa; reoloji aynı diziden (1999) kısıtlı → sızıntı; güç yok. | Yayımlanmış | — | literatur | **eleme** |
| **VE-5** | Nalbant 2026: gevşeme gerilme gölgesini silip Marmara M5+ olaylarını (2006, 2019, 2023, 2025) öne çekti mi? | Nalbant 2026 (10.5194/egusphere-egu26-11337), yalnız özet | Yıl; M5+ | 4 olay, geriye dönük; CRS-ETAS rakibinin alanı (9 tetikte ayırt edilemez). ETAS örtüşmesi itirazının kendisi. | — | — | fizik | **eleme** |

## K10 için şart önerisi (karar değil)

K10 ancak şu dördü birlikte sağlanırsa yeniden tartışılsın:
1. **F-CRS V2 şart metni** sunucudan harfiyen doğrulanmış olsun; bu öneri onun yerine geçmez.
2. **Jeodezik ayırt edilebilirlik:** VE-1 türü ön kayıtlı sınamada, ≤ 2016 parametreleriyle dondurulmuş en az bir gevşeme modeli 2017+ GNSS hız değişiminde sabit hız rakibini geçsin (toplam log skor farkının istasyon-bootstrap %95 alt sınırı > 0).
3. **Etki büyüklüğü:** o modelin PIF ve Orta Marmara'daki bugünkü Coulomb gerilme hızı pertürbasyonu tektonik hızın en az ~%20'si olsun ve reoloji topluluğu içindeki yayılımı 2 katın altında kalsın. (Eşik sayıları önerimdir; ön kayıtta sabitlenmeli.)
4. **Güç ve artık kazanç:** ön kayıtlı güç hesabı hedef kümede ≥ 2σ ayırt edilebilirlik göstersin ve terim canlı ETAS'ın **üstüne** eklenerek puanlansın.
Beklentim (ölçülmedi): 3. madde sağlanmaz.

## (c) Elenenler
VE-3 (güç yok), VE-4 (N = 7, sızıntı), VE-5 (ETAS örtüşmesi, N = 4). 2019 Silivri ve 2025 M6,2 sonrası gevşeme ayrı aday yapılmadı: moment küçük, etki yerel ve aylık ölçekte, ETAS'ın alanı. 1912 Ganos için ayrı aday yok: 114 yıl önce, jeodezik kısıt yok.

## (d) Dürüst sınır
- Tam metin okunmadı; viskozite sayıları özetlerden. Diao 2016 ve Özarpacı 2021 kapalı erişim.
- VE-1 güç tahmini ve VE-3'teki %5–10 kaba el hesabıdır, model koşulmadı.
- VE-1 başarılı olsa bile deprem olasılığı hakkında bir şey göstermez; yalnız yüklenme hızının zaman bağımlılığına sınır koyar.
- Doğrulanamayan iz: Crossref aramasında "Adalar at the Eastern Marmara Seismic Gap: The August 2026 Earthquake Cluster" (Ahmed, 10.31223/x5qj6q) göründü, DOI tek başına çözdürülemedi; listeye alınmadı.
- Köprü sayıları OpenCitations kapsamıyla sınırlı (~%65–70).
