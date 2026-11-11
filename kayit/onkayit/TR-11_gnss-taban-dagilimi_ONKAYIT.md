# TR-11 ön kaydı: GNSS 2 yıllık hız değişiminin depremsiz pencerelerdeki taban dağılımı

Tarih: 11 Kasım 2026. Durum: TASLAK (inceleme bekliyor).
Türediği yer: `kayit/turetme/ZINCIR.md` Halka 2 (TR-1 "güç yok" ile kapandı; "olağan" ölçülmeden "olağandan büyük"
sorulamıyor). Tasarım ve üstveri sayımı: `kayit/onkayit/TR-11_SAYIM.md` (commit 2fb0a7b). Maliyet 0 €.

## 1. Soru

Depremle ilgisi olmayan 5 yıllık pencerelerde, bir GNSS istasyon kümesinin son 2 yıldaki hızı önceki 3 yıla göre ne
kadar değişir (küme ölçüsü S, mm/yıl) ve S hangi sıklıkta belli bir büyüklüğü aşar? Bu bir yanlış alarm oranıdır.
İkinci adımda bu taban tek bir formülle "Marmara benzeri geometride tabanı aşmak için derin kayma hızının en az ne
kadar değişmesi gerekir" sorusuna çevrilir. Bu bir tahmin sınavı değildir; sonucu bir ölçüm sınırı cümlesidir.
Deprem olasılığı üretmez, mutlak İstanbul olasılığı yazılmaz.

Rakip açıklamalar ve sınav öncesi güven (not): taban, olağan gürültü modeli N0'ın öngördüğünden büyüktür (0,60);
N0 ile uyumludur (0,30); N0'dan küçüktür (0,10).

## 2. Bağlayıcı tanımlar

`TR-11_SAYIM.md` §2 (tasarım), §4 (çıktılar, beklenti N0, hüküm sırası) ve §5 (Marmara çevirisi) bu ön kaydın
bağlayıcı metnidir ve harfiyen geçerlidir. Özet: NGL IGS20 günlük çözümleri (yatay); epoklar 2003, 2008, 2013, 2018,
2023 yıllarının 1 Ocak'ı; pencere 1826 gün, menteşe sondan 730 gün; küme merkezleri 2°'lik sabit ızgara; yakın
istasyonlar ≤ 100 km (3–8), referans 200–500 km (3–8); sakin pencere şartları Ş1–Ş3; pencerede ve önceki 2 yılda
deprem basamağı (kod 2) kaydı olan istasyon dışarıda; bağımsızlık birimi yer, güven aralıkları 10°×10° blok
bootstrap'ı (2000 yineleme, tohum 20261111); Marmara kutusu (39,5–42,0° K, 26,0–31,5° D) istasyonları ve merkezleri
tümüyle dışarıda.

Metin ile kod çelişirse (TR-2 dersi): küme-pencere listesi `kayit/turetme/tr11/tr11_kume_listesi.json` bağlayıcıdır
(803 küme-pencere, sayım betiğinin çıktısı, sha256 dosyada). Koşu kodu kümeleri yeniden kurmaz, bu listeyi okur;
yalnız doluluk şartını (taban ve yakın dönemde ayrı ayrı ≥ 0,60) seriler indikten sonra uygular. Doluluk yüzünden
bir kümede yakın ya da referans istasyon sayısı 3'ün altına düşerse küme-pencere düşer; yerine istasyon alınmaz.

## 3. Hüküm satırı

SAYIM §4.3'teki sıra aynen: (1) veri kapısı: yer < 100 ya da blok < 30 ise "veri yok"; (2) kod denetimi: yapay N0
serilerinde oran [0,9, 1,1] dışında ya da 3 mm/yıl eklenen sinyalde medyan artış [2,4, 3,6] dışında ise "geçersiz
(kod)"; (3) ana ölçü ρ = ölçülen %95 / N0'ın öngördüğü %95, %90 güven aralığı: alt sınır > 1 ise "taban N0'dan
büyük", üst sınır < 1 ise "taban N0'dan küçük", değilse "N0 ile uyumlu"; (4) sınıf satırları yalnız ≥ 30 yer
varsa; (5) çeviri her zaman %95'in üst güven sınırı U ile.

Önceden bilinen ve kabul edilen sınır: sayımda yerlerin %97'si düşük sismisiteli bölgede; doğrultu atımlı kuşakta
(sınıf A) 2 yer, öteki aktif kuşakta (sınıf B) 11 yer var. A ve B için hüküm şimdiden "güç yok"tur. Ölçülen taban
"az sismik bölge tabanı"dır; Marmara çevirisi yalnız ALT SINIR olarak yazılır.

## 4. Marmara çevirisi (önceden sabit)

Δs_min = U / G, G = medyan_i |arctan(x_i/D) − m_r| / π (SAYIM §5). Sonuçta SAYIM §5'teki tablo ızgarası
(D 5, 10, 15 km; x 5, 10, 20, 30, 50 km; dengeli referans) için U/G yazılır. Yorum cümlesi yalnız şu biçimde
kurulur: "Yıl ölçekli GNSS hız değişimi alarmı, Marmara benzeri geometride derin kayma hızındaki en az a–b mm/yıl'lık
değişimi görebilir (alt sınır); karşılaştırma için Prens Adaları kesiminde yayımlanmış kayma açığı hızı
10–15 mm/yıl (Ergintav 2014, özetten)". a ve b tablonun en küçük ve en büyük değeridir. Sonlu yama, geç başlayan
değişim, tek yanlı referans ve aktif kuşakta daha büyük taban hep aynı yöne iter: gerçek eşik daha büyüktür.

## 5. Koşu sırası

1. Bu ön kayıt incelenir, dondurulur, commit + push edilir.
2. Kod yazılır; yalnız yapay serilerle (N0'dan üretilmiş, gerçek tenv3 biçiminde) geliştirilir ve sınanır. Gerçek
   seri indirilmeden kod incelemesi yapılır.
3. Seriler indirilir (4730 istasyon; depoya konmaz). İndirme hatası alan istasyon "veri yok" sayılır ve listesi
   yazılır; tekrar deneme 3 kez.
4. Tek koşu. Çıktı ne olursa olsun yazılır. İstisna olursa yalnız doğrudan nedeni düzeltilir ve fark kayda geçer;
   herhangi bir S değeri görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik" başlığında yazılır.

Körlük: bugüne dek hiçbir tenv3 serisi indirilmedi (yalnız ağ erişimini sınamak için ALGO istasyonunun dosya boyu
ölçüldü, içeriği okunmadı). 2026 deprem verisi kullanılmaz; katalog 2025-12-31'de biter. Marmara kutusunun hiçbir
serisi indirilmez (VE-1 körlüğü).

## 6. Sınırlar

- Taban aktif fay çevresini temsil etmez (sınıf A güç yok); sakin pencere seçimi dağılımı aşağı çeker.
- N0 bir varsayımdır: genlikler (beyaz 1,5 mm; kırpışma 3 mm/yıl^0,25) özetten doğrulanamadı. "N0'dan büyük" hükmü
  yalnız bu N0'a göredir; N1 (rastgele yürüyüş ekli) bilgi satırıdır.
- NGL işleme ve çerçeve değişimleri bütün kümelerde aynı tarihte iz bırakabilir; epok kırılımı ve referans farkı
  alınmamış S bilgi satırı bunu gösterir, düzeltmez.
- Kayıtsız anten değişimleri ve çok yıllı hidrolojik yükleme kuyruğu şişirir.
- Çeviri sonsuz vida dislokasyonudur; sığ sünme ve kilitlenme derinliğinin üstündeki geçiciler kapsam dışıdır.

## 7. İstanbul'a bağ

Sonuç bir olasılık terimi değildir ve ileri test defterine rakip girmez. Vereceği tek şey şu cümledir: yıl ölçekli
GNSS izlemesi Marmara'da derin kayma hızındaki hangi büyüklükten küçük değişimi göremez. Bu, "GNSS ile yıl ölçekli
alarm" yolunun (TR-1, AV-1, VE-1 ailesi) açık mı kapalı mı olduğunu söyler. Eşik, yayımlanmış kayma açığı hızının
kendisine yakın ya da ondan büyük çıkarsa bu yol bugünkü ağla kapalıdır; küçük çıkarsa Marmara'ya özgü ayrı bir
ön kayıt gerekir (2017 sonrası veri hâlâ kördür).

## 8. Yeniden açma şartı

Aktif doğrultu atımlı kuşakta ≥ 30 sakin yer veren bir veri kaynağı (yoğun bölgesel ağ çözümleri, postsismik
modeli çıkarılmış seriler) bulunursa sınıf A satırı için yeniden açılır.
