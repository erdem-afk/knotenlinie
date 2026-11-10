# A4 veri envanteri: karadan kilitlenme tahmini, sonradan gelen deniz tabanı ölçümüne göre ne kadar yanılıyor?

10 Kasım 2026. Yalnız derleme: hesap yok, hüküm yok. Makine okunur sürüm: `/home/user/derive/a4/A4_envanter.json` (15 satır).

İşaretler: **[tam metin]** metinden okundu; **[özet]** yalnız özetten; **şekilden, doğrulanmadı**; **bulunamadı**.

## Özet

- **Sayısal karşılaştırma (kara ve deniz değeri ikisi de sayısal):**
  - **Sıkı N = 1 bölge:** Marmara–Kumburgaz. İki değer de metinde açıkça yazıyor ve aynı segmenti anlatıyor. Sakic 2016, Ergintav 2014'e doğrudan atıf yapıyor.
  - **Gevşek N = 2 bölge:** Marmara ve Nankai.
    - Marmara–Batı Sırtı eklenince Marmara'da 2 nokta oluyor. Bu noktanın Ergintav'ın segmentiyle eşleştiği doğrulanmadı.
    - Nankai–Kumano'da kara değeri bölgesel bir ifade ("<30 km tam kilitli"), nokta değeri değil.
- **Marmara dahil mi:** Evet, hem sıkı hem gevşek sayımda var. Marmara satırları tabloda **[MARMARA]** ile işaretli.
- **Fark yönü:**
  - Marmara–Kumburgaz'da kara kilitlenmeyi az tahmin etti: krip dedi, deniz tabanı kilitli buldu.
  - Batı Sırtı'nda kara krip için fazla tahmin vermiş olabilir: kara neredeyse tam krip dedi, deniz yaklaşık yarı krip buldu.
  - Nankai–Kumano'da kara biraz fazla tahmin etti: tam kilit dedi, deniz 0,6–0,8 buldu (belirsizlik içinde).
  - Nitel satırlarda yön karışık:
    - Ryukyu, Cascadia ve Kuril'de kara az tahmin etmiş ya da sonuç belirsiz.
    - Nankai'nin düşük SDR bölgelerinde kara fazla tahmin etmiş olabilir.
- **Yapısal not (iki çalışmada açıkça yazıyor):** Kara verisi en sığ kilitlenmeyi ayırt edemiyor.
  - Tomita 2026 (Kuril): "sığ kilitli" ve "sığ krip" modelleri kara sitelerinde aynı hızı veriyor.
  - Li 2018 (Cascadia): kara verisi en sığ kısımdaki kripi çözemiyor.
  - Bu durumda "yanılma" çoğu zaman ölçülebilir bir sayı değil, karar verilemezlik.
- **Hedef boşluk:** Adalar Fayı (PIF) için yayımlanmış bir deniz tabanı jeodezi ölçümü bulunamadı. Kara tahminleri:
  - Ergintav 2014: 10–15 mm/yıl.
  - Diao 2016: 18,9 ± 7,2 mm/yıl, kilitli derinlik 12,1 ± 7,0 km.

## Tablo

| # | Bölge | Deniz tabanı çalışması (DOI) — ölçüm | Önceki kara modeli (DOI) — aynı noktadaki tahmin | Geometri: kara istasyonuna uzaklık / kilitli derinlik (km) | Fark yönü | Sayısal mı |
|---|---|---|---|---|---|---|
| 1 | **[MARMARA] Kumburgaz Havzası, İstanbul–Silivri segmenti** (doğrultu atımlı) | Sakic+ 2016 GRL (10.1002/2016gl069600): yüzey kayması ≈0, üst sınır <6 mm/yıl (6 ay) [tam metin]. Lange+ 2019 Nat Commun (10.1038/s41467-019-11016-z): **0,80 ± 1,25 mm/yıl** doğrultu atım (2,5 yıl); ≥3 km, muhtemelen ~5,5 km'ye kadar tam kilitli [tam metin] | Ergintav+ 2014 GRL (10.1002/2014gl060985): orta Marmara Fayı'nın doğu (İstanbul güneyi) ve batı-orta segmentlerinde kayma açığı **üst sınırı ~2 mm/yıl** (10 km kilitli derinlik varsayımıyla) → "asismik krip" [tam metin] | Uzaklık bulunamadı. Sakic: kara GPS "uzak ve seyrek"; segment İstanbul'a 15 km'den yakın. Kilitli derinlik: kara 10 (varsayım); deniz ≥3, muhtemelen 5,5; temel ~4,5 | Kara kilitlenmeyi **az** tahmin etti | **Evet (sıkı)**. Nicelikler farklı: kara açık hızı, deniz yüzey krip hızı |
| 2 | **[MARMARA] Batı Sırtı** | Yamamoto+ 2019 GRL (10.1029/2018gl080984): sağ yanal krip **10,7 ± 4,7 mm/yıl** (%95), blok hareketinin ~yarısı [özet] | Ergintav 2014: batı-orta segmentte kayma açığı üst sınırı ~2 mm/yıl, yani neredeyse tam krip [tam metin]. Segment eşleşmesi doğrulanmadı | Uzaklık bulunamadı. Deniz modeli: 8 km kısmi krip eden sediman + 3 km kilitli katman | Kara kripi **fazla** (kilitlenmeyi az) tahmin etmiş olabilir | Evet (gevşek) |
| 3 | **[MARMARA] Adalar Fayı (PIF)** | **Bulunamadı** | Ergintav 2014: 10–15 mm/yıl (10 km kilitte 11 ± 2). Diao+ 2016 GJI (10.1093/gji/ggw048): 18,9 ± 7,2 mm/yıl, kilitli derinlik 12,1 ± 7,0 km | Ergintav: Armutlu'daki tek GPS sitesi PIF'e ~10 km | Karşılaştırılamaz | Hayır |
| 4 | Nankai, Kumano ve en sığ orta kesim | Tadokoro+ 2012 GRL (10.1029/2012gl051696): ~40 mm/yıl, bağlanma ~0,6–0,8. Yasuda+ 2017 GRL (10.1002/2017gl072918): TCA 38 ± 25, TOA 57 ± 21 mm/yıl, bağlanma **%70 ± 40** (1σ) [özet] | Ito & Hashimoto 2004 JGR (10.1029/2002jb002358): kayma açığı 5–6 cm/yıl, <30 km **tam kilitli** [özet; bölgesel ifade] | Uzaklık bulunamadı. Kilitli derinlik: kara <30; deniz ≥10 | Kara **biraz fazla** (belirsizlik içinde) | Evet (gevşek) |
| 5 | Nankai, tüm hendek (15 site) | Yokota+ 2016 Nature (10.1038/nature17632; arXiv 1802.04508): Tablo 1'de hızlar, ör. TOK1 5,0 / KUM1 3,6 / MRT1 3,4 / **HYG2 2,0** cm/yıl. Düşük SDR bölgeleri A, C ve E [tam metin] | Ito & Hashimoto 2004; Hok+ 2011 (10.1029/2011jb008492); Yoshioka & Matsuoka 2013 (10.1016/j.tecto.2013.01.023). Yokota'nın kendi yalnız-kara modeli Ext. Data Fig. 5a'da: **şekilden, doğrulanmadı**. Yokota, kara verisinin açık deniz arayüzünü çözemediğini yazıyor | Uzaklık bulunamadı (site koordinatları tabloda var). Kilitli derinlik bulunamadı | Düşük SDR bölgelerinde kara **fazla** tahmin etmiş olabilir (şekilden) | Hayır |
| 6 | Japonya Hendeği (2011 öncesi) | Sato+ 2013 JGR (10.1002/jgrb.50275): Miyagi açığı 2005 öncesi 6–7, 2006 sonrası 4–5 cm/yıl; Fukushima açığı ~2 cm/yıl, bağlanma zayıf [özet; hız, oran değil] | Loveless & Meade 2010 (10.1029/2008jb006248) ve 2011 (10.1029/2011gl048561): tepe kaymanın yakını ≥%80, kuzey <%20. Hashimoto+ 2009 (10.1038/ngeo421). Nokta değeri: **şekilden, doğrulanmadı** | Kara GPS ile hendek arası **~230 km** (L&M 2011). Kıyı altında arayüz 40–50 km | Bulunamadı | Hayır |
| 7 | GB Kuril, Nemuro açığı | Tomita+ 2026 CEE (10.1038/s43247-026-03297-2): G21 4,30 ± 1,39; **G22 7,98 ± 2,12**; G23 7,14 ± 3,83 cm/yıl (levha ~8); hendek yakınında bağlanma ~%100 [tam metin] | Tomita'nın ileri modelleri: kara siteleri sığ-kilit ile sığ-kripi ayırt edemiyor. Önceki kara modelinin nokta değeri bulunamadı | Uzaklık bulunamadı. Model sınırları: kilitli 0–50 km, krip 10–50 km | Kara **belirsiz**, deniz tam kilit | Hayır |
| 8 | Ryukyu, Okinawa GD | Tadokoro+ 2018 GRL (10.1029/2018gl078655): 63 ve 21 mm/yıl; bağlanma **0,9–1,0** (10–13 km) [özet] | Okinawa için önceki kara değeri bulunamadı. Heki & Kataoka 2008 (10.1029/2008jb005739), GB Ryukyu'yu "bağlanmamış" diye niteliyor; farklı segment | Siteler hendekten ~45 ve ~70 km. Kara uzaklığı bulunamadı | Genel "zayıf bağlanma" görüşüne göre kara **az** tahmin etmiş; doğrulanmadı | Hayır |
| 9 | Peru, Lima açığı | Gagnon+ 2005 **Nature** (Science değil) (10.1038/nature03412): 2–40 km kaymasız modelle uyumlu [Semantic Scholar tldr; özet kapalı] | Gagnon öncesi kara modeli bulunamadı. Sonraki Chlieh+ 2011 (10.1029/2010jb008166) yüksek ISC buluyor | Uzaklık bulunamadı. Kilitli derinlik 2–40 | Bulunamadı | Hayır |
| 10 | Cascadia, orta Oregon | DeSanto+ 2025 EPSL (10.1016/j.epsl.2025.119463): 4 GNSS-A sitesi (2016–2022), deformasyon cephesi neredeyse tam kilitli; hız sayısı özette yok | Schmalzle+ 2014 G3 (10.1002/2013gc005172): 43–46°K'de kısmi krip. Li+ 2018 (10.1029/2018jb015620): en sığ kısım çözülemiyor. Kıyı GNSS <1 cm/yıl | Bulunamadı | Kara **az** tahmin etmiş (Schmalzle'ye göre) ya da belirsiz | Hayır |
| 11 | Alaska, Shumagin/Semidi | Yalnız ard-kayma: Brooks+ 2023 Sci Adv (10.1126/sciadv.adf9299), cepheden ~60 km'de ~1,4 m yer değiştirme. İnterseismik deniz ölçümü bulunamadı. "Brooks 2021 GRL" OpenAlex ve Crossref'te bulunamadı | Senapati+ 2024 (10.1093/gji/ggae002): güçlüden zayıfa geçiş | Ard-kayma <20 km | Karşılaştırılamaz | Hayır |
| 12 | Hikurangi, Gisborne (geçici kayma) | Wallace+ 2016 Science (10.1126/science.aaf2349): SSE tabana 2 km yakın. Woods+ 2024 (10.1029/2024jb029068): yükselme 10–33 mm | Yohler+ 2019 (10.1029/2019gc008229): APG eklenince kayma hendeğe kayıyor | Bulunamadı | Kara hendek-yakını kaymayı **az** gösteriyor (SSE için) | Hayır (yardımcı) |
| 13 | Kosta Rika, Nicoya | Jiang+ 2017 GRL (10.1002/2017gl072803): SSE hendeğe kadar yayıldı | Nokta değeri bulunamadı | ~15 km | Bulunamadı | Hayır |
| 14 | Meksika, Guerrero | Cruz-Atienza+ 2025 Sci Adv (10.1126/sciadv.adu8259): eğim, basınç ve SSE ölçümleri. GNSS-A interseismik sonucu bulunamadı | Bulunamadı | Bulunamadı | Karşılaştırılamaz | Hayır |
| 15 | Kuzey Şili, GeoSEA (~21°G) | Lange+ 2019 GEOMAR özeti (DOI yok): çözünürlük üstünde deformasyon yok (yerel gerinim) | Bulunamadı | Bulunamadı | Karşılaştırılamaz | Hayır |

## Notlar ve sınırlar

- **Marmara–Kumburgaz'da nicelikler aynı değil.** Kara tarafı kayma açığı hızının üst sınırı (≤2 mm/yıl), deniz tarafı yüzey krip hızı (0,8 ± 1,25 mm/yıl).
  - Lange, uzak alan hızını 15–27 mm/yıl (GPS) ve 15–19,7 mm/yıl (jeoloji) olarak veriyor.
  - Bu iki niceliği birbirine dönüştürmedim.
  - Deniz ölçümü yalnız sığ (birkaç km) kaymayı kısıtlıyor. Derindeki kilitlenme için Lange, OBS sismisitesinin seyrek olmasını kanıt olarak kullanıyor.
- Sakic 2016 ile Lange 2019 aynı ağ. Yamamoto 2019 ise farklı yer (Batı Sırtı) ve farklı sonuç; Lange bunu "karmaşık kilit deseni" olarak tartışıyor.
- **Okunamayan tam metinler:** Klein+ 2017 GRL (10.1002/2017GL072777, "onland geodesy" sorusu, HAL bot engeli), Yamamoto 2019, Tadokoro 2018, Sato 2013, DeSanto 2025, Gagnon 2005.
  - Bu çalışmalardaki değerler yalnız özetten alındı.
  - Bu satırlarda kara istasyonu uzaklıkları "bulunamadı" kaldı.
- **Erişim yolları:** OpenAlex (anahtarlı), Europe PMC, arXiv, archimer.ifremer, ANU açık deposu, nature.com açık erişim, Semantic Scholar.
- **Dosya yerleri:**
  - Ham indirilenler: `/home/user/derive/a4/dl/`
  - Betikler: `/home/user/derive/a4/oa.py`, `/home/user/derive/a4/loc.py`, `/home/user/derive/a4/run.sh`, `/home/user/derive/a4/yaz_json.py`
