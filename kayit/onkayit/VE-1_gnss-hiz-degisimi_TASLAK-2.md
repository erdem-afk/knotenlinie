# VE-1 (+AV-1) ön kayıt TASLAK-2: Marmara GNSS hızları 2017–2023'te değişti mi, ≤2016 gevşeme modelleri bunu önceden söylüyor mu?

Durum: **taslak 2, dondurulmadı.** İnceleme 1 RED verdi (`VE-1_INCELEME-1.md`, 22 bulgu); bu sürüm yüksek önemdeki bulguları kapatmak için yazıldı. Hedef veri (2017+ günlük seriler) indirilmedi.
Tarih 11 Kasım 2026. Tür: veri işi. 0 €.

## Bu sınav ne değildir
Deprem olasılığı hakkında bir ifade **değildir** ve sonucundan Marmara M7+ sürümü çıkmaz. Yalnız şunu ölçer: 1999 sonrası gevşeme, GNSS hızlarında 2017–2023'te ölçülebilir bir değişim bıraktı mı. Yüklenme hızındaki zaman bağımlılığının gözlenebilir izlerinden biridir, tek izi değildir.

## Hipotezler ve tek hüküm satırı
- H0: Δv = 0 (hız sabit). Dağılım N(0, C_obs).
- H1: Δv = μ_karışım; μ_karışım, sızıntı kapısından geçen gevşeme modellerinin **eşit ağırlıklı ortalamasıdır** (model seçimi yok). Dağılım N(μ_karışım, C_obs + C_model).
- Hüküm satırı: tam kovaryanslı Gauss log skoru farkı L = ln p(Δv | H1) − ln p(Δv | H0). p değeri H0 altında parametrik simülasyonla (C_obs'tan 10.000 çekiliş). L > 0 ve p < 0,05 ise "H1 yönünde"; L < 0 ve H1 altındaki simülasyonda p < 0,05 ise "H0 yönünde"; öteki durumda "ayırt edilemez" (üç ayrı hüküm, birleştirilmez).
- Bilgi satırları: tek tek modeller, istasyon bootstrap'ı, ortak kip çıkarılmış hâl, ISTA dahil hâl, 2017–2026 penceresi (ISTA, ORE1).

## Modeller (sızıntı kapısı)
- Kural: bir modelin parametrelerini veren makalenin Crossref "ilk çevrimiçi" tarihi < 2017-01-01 olmalı ve parametreler 2017 sonrası GNSS verisine uydurulmamış olmalı. Tarihler dondurmada Crossref'ten çekilip kayda yazılır; kapıdan geçmeyen model düşer.
- Adaylar: (M1) Burgers/Maxwell alt kabuk–manto gevşemesi, Hearn 2009 tercih edilen parametre seti; (M2) zayıf zon, Yamasaki 2014 tercih edilen set; (M3) afterslip, yalnız ≤2016 parametreleriyle (Ergintav 2009 ya da Hearn 2009'un afterslip bileşeni). DeVries 2016 ancak tarih kapısından geçerse (M4).
- Dışarıda: Özarpacı 2021 (ilk çevrimiçi 2020-11-19, 2017+ veriyle uydurulmuş) ve Hussain 2018 (2018-04-11) model girdisi olamaz; ikisi de "bilinen sonuç" olarak körlük beyanında.
- Her model için **tek** parametre seti: makalenin "tercih edilen/en iyi" diye adlandırdığı değerler; makale aralık veriyorsa aralığın geometrik ortası. Seçilen sayılar ve sayfa/tablo numarası dondurma dosyasına yazılır. Tek değer çıkarılamayan model düşer.
- En az bir model kalmazsa iş `veri-yok` ile kapanır.
- İleri model aracı: **yalnız PSGRN/PSCMP** (katmanlı viskoelastik yarı uzay). Kaynak: 1999 İzmit ve Düzce için SRCMOD modellerinin eşit ağırlıklı ortalaması (proje kuralı). M2 (yanal zayıf zon) katmanlı araçla kurulamıyorsa düşer.
- C_model: SRCMOD kaynak modelleri tek tek kullanıldığında μ'nün örnek kovaryansı.

## Veri
- Kaynak: Nevada Geodetic Laboratory günlük tenv3 serileri, IGS14; çerçeve tek, ortak kip çıkarılmaz (model öngörüleri Avrasya sabit çerçevede aynı istasyon farklarıyla karşılaştırılır; Δv iki dönem farkı olduğu için sabit çerçeve dönmesi sadeleşir).
- **İstasyon listesi (yalnız üstveriden, `DataHoldings.txt` 11 Kasım 2026; seriler açılmadan):** kutu 26,5–31,5° D, 39,8–41,6° K içindeki 28 istasyondan, başlangıcı ≤ 2009-01-16 ve bitişi ≥ 2022-11-01 olanlar: TUBI, BILE, BURS, HEND, ISTN, IZMT, KARB, NAHA, SARY, SLEE, TEKR (11 istasyon). ISTA birincil analizden **çıkarıldı** (körlük beyanı). Liste budur; doluluk ölçütü yok, seri açıldıktan sonra istasyon çıkarılmaz (bir dönemde < 2 yıl verisi olan istasyon otomatik düşer ve bu raporlanır).
- Dönemler: taban 2009-01-16 → 2016-12-31; hedef **2017-01-01 → 2023-02-05** (Kahramanmaraş'tan önce biter; 2023 atımı ve uzak alan postsismik etkisi birincil analize girmez).
- Hedef nicelik: istasyon başına doğu ve kuzey Δv (22 sayı).
- Hız kestirimi: doğrusal + yıllık + yarı yıllık + atımlar, en küçük kareler. Atım listesi: NGL `steps.txt` (SHA-256 kayda) ile şu olayların **tekilleştirilmiş** birleşimi: 2019-09-26 M5,8 Silivri, 2014-05-24 M6,9 Kuzey Ege (60 km kuralı yerine: steps.txt'de yoksa ve merkez üssü < 100 km ise eklenir). Olaydan sonraki 90 gün yalnız o istasyonda dışarıda.
- C_obs: istasyon içi renkli gürültü (beyaz + titreşim gürültüsü, genlikler **yalnız 2009–2016 artıklarından**) ve istasyonlar arası korelasyon (2009–2016 artıklarının aylık ortalamalarının örnek korelasyonu, Ledoit–Wolf büzmesiyle).

## Ateşleme kapısı (2017+ veri açılmadan)
- Yalnız 2009–2016 serileri indirilir (tenv3 dosyaları 2017-01-01'de kesilerek okunur; kesme kodu incelenir, kesilmemiş dosya diske yazılmaz).
- Bu serilerin gürültü modeli ve gerçek boşluk deseniyle hedef dönem uzunluğunda sentetik veri üretilir; **hüküm kuralının aynısı** uygulanır, 1.000 tekrar.
- Ölçülen: (a) H0 altında birinci tür hata (≤ 0,07 olmalı; değilse kural düzeltilmeden koşulmaz), (b) H1 = μ_karışım altında güç.
- Güç ≥ 0,8: gerçek koşu. 0,5–0,8: koşulur, sonuç önceden "yalnız üst sınır" diye ilan edilir. < 0,5: iş `guc-yok` ile kapanır, 2017+ veri açılmaz.

## Körlük beyanı (Ek 0)
- AV kolu envanterde ISTA'nın 2026'ya kadarki tam serisini indirip artık sd'sini (1,4 mm) hesapladı → ISTA birincil analizden çıkarıldı.
- İstasyon başlangıç/bitiş tarihleri üstveriden görüldü; liste buna göre yazıldı.
- Bilinen sonuçlar: Hussain 2018 (gerinim hızı ≈10 yıl sonra sabit; H0 lehine), Özarpacı 2021 (20 yıl sonra süren logaritmik afterslip; H1 lehine). İkisi de tasarımı etkilemiş olabilir.
- İnceleyicinin σ beklentisi (0,2–0,6 mm/yıl/bileşen) ve kolların güç tahminleri görüldü; güç kapısı bunlardan bağımsız ölçülecek.

## Sonuç ne olursa
- Üç hükümden hangisi çıkarsa çıksın v1.3b değişmez ve bu sınavdan olasılık çıkarımı yapılmaz.
- "H1 yönünde" çıkarsa: yalnız K10 şart önerisinin jeodezik maddesi sağlanmış sayılır; K10'un açılması ayrı bir karardır (Erdem) ve şartın kendisi yeniden yazılmalıdır.
- "H0 yönünde" ya da "ayırt edilemez" ayrı ayrı raporlanır; ikincisinde yalnız Δv üst sınırı yazılır.

## Dürüstlük
Yıl ölçeğinde deprem tahmini bugün ileriye dönük testte kanıtlanmış değildir; bu çalışma resmî deprem tahmini değildir.
