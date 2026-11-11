# VE-1 (+AV-1) ön kayıt TASLAĞI: Marmara GNSS hızları 2017 sonrasında değişti mi, gevşeme modelleri bunu önceden söylüyor mu?

Durum: **taslak, dondurulmadı.** Bağımsız inceleme ve DONDUR + OTS bekliyor. Hedef veri (2017+ günlük seriler) bu taslak yazılırken indirilmedi.
Tarih 11 Kasım 2026. Tür: veri işi. Maliyet 0 €. Defter: `VE-1` (AV-1 bununla birleşti).

## Neden
Yıl–on yıl ölçeğinde zaman bağımlılığının fizik tarafındaki tek doğrudan gözlenebilir izi, yüklenme hızının zamanla değişmesidir.
1999 İzmit–Düzce sonrası gevşeme sürüyorsa Marmara çevresindeki GNSS hızları yavaşça değişmelidir. Bu sınav deprem tahmini **değildir**;
yüklenme hızının zaman bağımlılığına ölçülmüş bir sınır koyar ve K10'un (viskoelastik iş paketi) yeniden açılması için önerilen şartlardan biridir.

## Hipotezler
- H0: istasyon hızları 2009–2016 ile 2017+ arasında değişmedi (sabit hız).
- H1a: 1/t afterslip (Özarpacı 2021 parametreleri). H1b: Burgers gevşemesi (Hearn 2009, DeVries 2016). H1c: zayıf zon (Yamasaki 2014, Hussain 2018).
- Tek hüküm satırı: en iyi H1 modeli − H0, toplam Gauss log skoru, istasyon bootstrap %95 alt sınırı > 0 ise "H1 yönünde". Diğer her şey bilgi satırı.

## Veri
- Nevada Geodetic Laboratory günlük konum serileri (IGS14, tenv3), Marmara kutusu 26,5–31,5° D, 39,8–41,6° K. Kol taramasına göre 28 istasyonun 25'i Ocak 2024'te ya da önce bitiyor; sürenler ISTA, QIBP, ORE1.
- İstasyon seçimi (veriye bakmadan): 2009-01-01 öncesi başlayan, 2017-01-01 sonrası en az 4 yıl verisi olan, iki dönemde de doluluk ≥ %60.
- Hedef nicelik: istasyon başına doğu ve kuzey hız farkı, Δv = v(2017+) − v(2009–2016). Hız: doğrusal + yıllık + yarı yıllık + bilinen atım (NGL steps dosyası) en küçük kareler; belirsizlik renkli gürültü (HECTOR ya da MIDAS belirsizliği; hangisi olacağı incelemede sabitlenir).

## Önceden yazılan kurallar
1. Atımlar: NGL `steps.txt` içindeki donanım ve deprem atımları aynen; ek atım elle eklenmez.
2. Depremler: 2019-09-26 M5,8 Silivri, 2023-02-06 Kahramanmaraş, 2025-04-23 M6,2 Marmara için eş-sismik atım + istasyon merkez üssüne < 60 km ise olaydan sonraki 90 gün dışarıda.
3. Ortak kip: kutunun dışındaki ≥ 150 km uzak 10 Anadolu/Trakya istasyonunun ortalaması çıkarılmaz (model öngörüleri de aynı çerçevede hesaplanır); bilgi satırında çıkarılmış hali verilir.
4. Modeller: parametreler **yalnız ≤ 2016'da yayımlanmış** değerlerle dondurulur, bu veriye uydurma yok. İleri model PSGRN/PSCMP ya da RELAX; kaynak 1999 için SRCMOD dokuz modelin eşit ağırlıklı ortalaması (proje kuralı).
5. Sızıntı kapısı: model girdisi olan her makalenin yayım tarihi < 2017-01-01; SHA-256 kayda.

## Ateşleme kapısı (gerçek veriden önce)
İki kol güç konusunda ayrıştı: VE kolunun el hesabı istasyon başına fark σ'sı ≈ 0,35–0,45 mm/yıl (H0'a karşı toplamda ≈ 4σ); AV kolu ISTA'da yıllık ortalama artık sd'sini 1,4 mm buldu ve ≈ 2–3 mm/yıl altının görülemeyeceğini söylüyor.
Bu yüzden ilk adım sentetik güç testidir: **yalnız 2009–2016 serilerinden** kestirilen gürültü modeliyle 2017+ uzunluğunda sentetik seri üretilir, H1a genliği eklenir, 500 tekrar.
- Güç (H1a'yı H0'dan %5 düzeyinde ayırma) ≥ 0,8 ise gerçek koşu yapılır.
- 0,5–0,8 ise koşulur ama sonuç önceden "ayırt edilemez, yalnız üst sınır" ilan edilir.
- < 0,5 ise iş kapanır (`guc-yok`), 2017+ veri hiç açılmaz.

## Körlük beyanı (Ek 0)
- AV kolu envanter sırasında ISTA serisinin yıllık ortalama artık sd'sine (1,4 mm) baktı; hız farkı hesaplanmadı. Kısmi körlük kaybı olarak kayıtlı.
- Hussain 2018 "depremden ~10 yıl sonra gerinim hızı sabit" sonucunu biliyoruz; bu H0 lehine ön bilgidir.

## Sonuç ne olursa
- H1 yönünde: yüklenme hızı pertürbasyonu (PIF, CMF için model öngörüsü, bilgi satırı) yazılır; K10 şart önerisinin 2. maddesi sağlanmış olur, karar Erdem'in.
- H0 / ayırt edilemez: yüklenme hızındaki yıl ölçekli değişime üst sınır yazılır; viskoelastik terimin olasılığa katkısı için beklenen kazanç bu sınırla yeniden hesaplanır (VE-3 hesabı: r = 1,1'de olay başına ≈ 0,005 nat).
- Her iki durumda v1.3b değişmez; bu sınavdan Marmara M7+ sürümü çıkmaz.

## Dürüstlük
Yıl ölçeğinde deprem tahmini bugün ileriye dönük testte kanıtlanmış değildir; bu çalışma resmî deprem tahmini değildir. Bu sınav olumlu çıksa bile deprem zamanı hakkında bir şey göstermez.
