# TR-11 ön kaydı: GNSS 2 yıllık hız değişiminin depremsiz pencerelerdeki taban dağılımı

Tarih: 11 Kasım 2026. Durum: DONDURULDU (sürüm 2; inceleme 1 "düzeltmeyle kabul", bütün bulgular işlendi).
Bu commit'ten sonra metin değişmez; ekler ayrı başlıkla yazılır.
Türediği yer: `kayit/turetme/ZINCIR.md` Halka 2 (TR-1 "güç yok" ile kapandı; "olağan" ölçülmeden "olağandan büyük"
sorulamıyor). Tasarım ve üstveri sayımı: `kayit/onkayit/TR-11_SAYIM.md` (commit 2fb0a7b). Maliyet 0 €.

## 0. Bağlayıcı metinlerin sırası

Üç belge birlikte bağlayıcıdır ve çelişkide şu sıra geçerlidir:
1. `kayit/onkayit/TR-11_INCELEME-1.md` içindeki "Düzeltme metni" blokları: E1 (pozitif kontrol, iki düzeyli), E2
   (ρ'nun tanımı ve sıra, "3a. Tanımlar"), E3 (Marmara çevirisi, §4'ün yerine), Ö1 (ana ölçü ve etiket), Ö2 (menteşe
   modelinin koşu ayrıntıları), Ö3 (İstanbul kuralı), Ö4 (kutuya yakın istasyonlar), Ö5 (liste sha256 ve bilinen
   metin–kod farkları), K1, K2, K4, K6. K3 için birinci seçenek geçerlidir: gerçek istasyonla geliştirme yapılmaz.
   Ö1'deki önsel güvenler yazarın beyanı olarak kabul edilmiştir (0,45 / 0,45 / 0,10).
2. Bu belge.
3. `kayit/onkayit/TR-11_SAYIM.md` §2, §4, §5.
Küme-pencere listesi (`tr11_kume_listesi.json`, sha256 79f6cf0f…27cbbd) her üçünün üstündedir.

## 1. Soru

Depremle ilgisi olmayan 5 yıllık pencerelerde, bir GNSS istasyon kümesinin son 2 yıldaki hızı önceki 3 yıla göre ne
kadar değişir (küme ölçüsü S, mm/yıl) ve S hangi sıklıkta belli bir büyüklüğü aşar? Bu bir yanlış alarm oranıdır.
İkinci adımda bu taban tek bir formülle "Marmara benzeri geometride tabanı aşmak için derin kayma hızının en az ne
kadar değişmesi gerekir" sorusuna çevrilir. Bu bir tahmin sınavı değildir; sonucu bir ölçüm sınırı cümlesidir.
Deprem olasılığı üretmez, mutlak İstanbul olasılığı yazılmaz.

Rakip açıklamalar ve sınav öncesi güven (not): taban N0-yüksek'ten büyük (0,45); N0 bandında, eşdeğer kırpışma
genliği 2–4 mm/yıl^0,25 (0,45); N0-düşük'ten küçük (0,10).

## 2. Bağlayıcı tanımlar

`TR-11_SAYIM.md` §2 (tasarım), §4 (çıktılar, beklenti N0, hüküm sırası) ve §5 (Marmara çevirisi) bu ön kaydın
bağlayıcı metnidir ve harfiyen geçerlidir. Özet: NGL IGS20 günlük çözümleri (yatay); epoklar 2003, 2008, 2013, 2018,
2023 yıllarının 1 Ocak'ı; pencere 1826 gün, menteşe sondan 730 gün; küme merkezleri 2°'lik sabit ızgara; yakın
istasyonlar ≤ 100 km (3–8), referans 200–500 km (3–8); sakin pencere şartları Ş1–Ş3; pencerede ve önceki 2 yılda
deprem basamağı (kod 2) kaydı olan istasyon dışarıda; bağımsızlık birimi yer, güven aralıkları 10°×10° blok
bootstrap'ı (2000 yineleme, tohum 20261111); Marmara kutusu (39,5–42,0° K, 26,0–31,5° D) istasyonları ve merkezleri
tümüyle dışarıda.

Metin ile kod çelişirse (TR-2 dersi): küme-pencere listesi `kayit/turetme/tr11/tr11_kume_listesi.json` bağlayıcıdır
(803 küme-pencere, sayım betiğinin çıktısı; sha256
79f6cf0f9a1a11d932617b20c7b866bb5125a3acea62d35325af9364f027cbbd, koşu kodu denetler). Koşu kodu kümeleri yeniden kurmaz, bu listeyi okur;
yalnız doluluk şartını (taban ve yakın dönemde ayrı ayrı ≥ 0,60) seriler indikten sonra uygular. Doluluk yüzünden
bir kümede yakın ya da referans istasyon sayısı 3'ün altına düşerse küme-pencere düşer; yerine istasyon alınmaz.

## 3. Hüküm satırı

Sıra (INCELEME-1 E2 madde 7): veri kapısı; kod denetimi (i) ve (ii-b) yapay serilerde; (ii-a) gerçek veride
istasyon düzeyinde; ancak bunlar geçtikten sonra gerçek S hesaplanır.

1. Veri kapısı: geçerli yer < 100 ya da blok < 30 ise "veri yok" (yer tanımı K2).
2. Kod denetimi: (i) yapay N0 serilerinde q95 / q95_N0 oranı [0,9, 1,1] dışındaysa; (ii-a) eklenen 3 mm/yıl doğu
   sinyalinde istasyon düzeyi medyan(d_E) [2,95, 3,05] dışında ya da medyan(|d_N|) ≥ 0,05 ise; (ii-b) yapay
   serilerde S düzeyi artış Monte Carlo beklentisinin ±%10'u dışındaysa: "geçersiz (kod)". Bu adım gerçek S
   görülmeden koşar; başarısız olursa kod "koşu öncesi düzeltme" başlığıyla düzeltilebilir.
3. Ana ölçü (Ö1): birincil çıktı ölçümün kendisidir, q95 [L, U] mm/yıl ve ρ [ρ_L, ρ_U]. Etiket eşdeğer kırpışma
   genliği b_f*'ye göre konur: alt sınırı > 4 ise "taban N0-yüksek'ten büyük"; üst sınırı < 2 ise "taban
   N0-düşük'ten küçük"; ötekilerde "taban N0 bandında". Kuyruk satırı ρ₉₅/ρ₅₀: alt sınırı > 1,1 ise "kuyruk Gauss
   N0'dan ağır".
4. Sınıf satırları yalnız ≥ 30 yer varsa; yoksa o sınıf "güç yok".

Önceden bilinen ve kabul edilen sınır: sayımda yerlerin %97'si düşük sismisiteli bölgede; doğrultu atımlı kuşakta
(sınıf A) 2 yer, öteki aktif kuşakta (sınıf B) 11 yer var. A ve B için hüküm şimdiden "güç yok"tur. Ölçülen taban
"az sismik bölge tabanı"dır.

## 4. Marmara çevirisi (önceden sabit)

INCELEME-1 E3 düzeltme metni aynen geçerlidir. Özet: algılama tanımı %5 yanlış alarm, %50 algılama; çeviri
n_y = 8 katmanının q95'i ve aralığı [L₈, U₈] ile; ana satır Δs_alt = √(L₈² − S50₈²) / G(D, x, m_r); G tablosu üç
referans geometrisiyle (dengeli, aynı yan, karşı yan), D 5, 10, 15 km ve x 5, 10, 20, 30, 50 km; a bu 45 hücrenin
en küçüğü, c dengeli D = 10, x = 20 hücresi. Yorum cümlesi yalnız E3'teki biçimde kurulur.

## 5. Koşu sırası

1. Bu ön kayıt incelenir, dondurulur, commit + push edilir.
2. Kod yazılır; yalnız yapay serilerle (N0'dan üretilmiş, gerçek tenv3 başlığı ve sütun düzeniyle) geliştirilir ve
   sınanır; gerçek istasyon kullanılmaz. Gerçek seri indirilmeden kod incelemesi yapılır.
3. Seriler indirilir (4730 istasyon; depoya konmaz). İndirme hatası istasyon düzeyinde kayda geçer; başarısız
   istasyonların payı %5'i aşarsa koşu durur ve tek bir yeniden deneme turu yapılır (S hesaplanmadan). Marmara
   kutusuna 150 km'den yakın istasyonların (CMLD, AFYN, KRBK, AKHR, KLUU) dosyalarında w1 sonrası satırlar belleğe
   alınmadan atılır; dosyalar koşudan sonra silinir.
4. Tek koşu. Çıktı ne olursa olsun yazılır. İstisna olursa yalnız doğrudan nedeni düzeltilir ve fark kayda geçer;
   herhangi bir S değeri görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik" başlığında yazılır.

Körlük: bugüne dek hiçbir tenv3 serisi indirilmedi (yalnız ağ erişimini sınamak için ALGO istasyonunun dosya boyu
ölçüldü, içeriği okunmadı). 2026 deprem verisi kullanılmaz; katalog 2025-12-31'de biter. Marmara kutusunun hiçbir
serisi indirilmez (VE-1 körlüğü).

## 6. Sınırlar

- Taban aktif fay çevresini temsil etmez (sınıf A güç yok); sakin pencere seçimi dağılımı aşağı çekiyor olabilir.
- N0 bir varsayımdır: genlikler (beyaz 1,5 mm; kırpışma 3 mm/yıl^0,25) özetten doğrulanamadı. "N0'dan büyük" hükmü
  yalnız bu N0'a göredir; N1 (rastgele yürüyüş ekli) bilgi satırıdır.
- NGL işleme ve çerçeve değişimleri bütün kümelerde aynı tarihte iz bırakabilir; epok kırılımı ve referans farkı
  alınmamış S bilgi satırı bunu gösterir, düzeltmez.
- Kayıtsız anten değişimleri ve çok yıllı hidrolojik yükleme kuyruğu şişirir.
- Çeviri sonsuz vida dislokasyonudur; sığ sünme ve kilitlenme derinliğinin üstündeki geçiciler kapsam dışıdır.

## 7. İstanbul'a bağ

Sonuç bir olasılık terimi değildir ve ileri test defterine rakip girmez. Önceden sabit kural (INCELEME-1 Ö3):
a ≥ 10 mm/yıl ise "GNSS yıl ölçekli alarm yolu bugünkü ağla Marmara'da kapalı" yazılır; a < 10 mm/yıl ise "bu ölçüm
yolu kapatamadı" yazılır ve bu, yolun açık olduğu anlamına gelmez. Temsilî hücre c < 5 mm/yıl ise "Marmara'ya özgü
ön kayıt düşünülebilir (2017 sonrası veri hâlâ kör)" notu eklenir. TR-11 hiçbir durumda "yol açık" hükmü vermez.
Beklenen sonuç "kapatılamadı"dır ve bu önceden kabul edilir; ölçümün asıl ürünü q95 tabanının kendisi ve temsilî
geometrideki eşiktir.

## 8. Yeniden açma şartı

Aktif doğrultu atımlı kuşakta ≥ 30 sakin yer veren bir veri kaynağı (yoğun bölgesel ağ çözümleri, postsismik
modeli çıkarılmış seriler) bulunursa sınıf A satırı için yeniden açılır.

## Ek 1 (11 Kasım 2026, dondurmadan sonra, hiçbir gerçek seri indirilmeden): kodlayıcının en dar okumaları

Kod yalnız yapay serilerle yazıldı (26 test geçti). Bağlayıcı metinde açık kalan noktalarda uygulanan okumalar,
gerçek veri görülmeden kayda geçer: Monte Carlo çekiliş düzeni küme-pencere başına (2000, n_y + n_r, 2), önce
yakınlar; yapay seride kırpışma gürültüsü FFT süzgeciyle üretilir ve seri bellekte tenv3 metni olarak ayrıştırıcıdan
geçer; m* seçili küme-pencerelerin bütün çekilişlerinin birleşik medyanıdır; bootstrap seçimi
`default_rng(20261112)` ile ve aynı tohum bütün katman satırlarında; b_f* nokta değeri ikiye bölmeyle, aralığı
121 noktalı ızgarada doğrusal ara değerle; σ_h istasyonun kendi tasarımıyla (kod 1 sıçrama sütunları dahil); rank
denetimi ayıklamadan sonra da yapılır; her dosyada okuma, gereken son pencere bitince durur (yalnız Marmara'ya yakın
beş istasyonda değil, hepsinde); L₈ ≤ S50₈ olursa kök 0 alınır; yer ağırlıklı q95 60/n_epok tam sayı ağırlığıyla;
NGL sigma sütunları kullanılmaz ve büyük sigmalı satırlar ayıklanmaz. tenv3 sütun düzeni NGL'nin
`readmes/README_tenv3.txt` belgesinden alındı.

## Ek 2 (11 Kasım 2026, kod incelemesinden sonra, hiçbir gerçek seri indirilmeden): koşu öncesi düzeltmeler

Kod incelemesi (`TR-11_KOD-INCELEME.md`) "koşulabilir" hükmü verdi; engelleyici bulgu yok. Üç önemli bulgu koşudan
önce işlendi: (1) okuma, son pencereden sonraki ilk satırda durmaz; o satırların değerleri ayrıştırılmadan ve
saklanmadan atlanır ve sayılır (sırasız dosyada sessiz veri kaybına karşı; Ek 1'deki "okuma durur" okumasının yerini
alır). (2) tenv3 biçim hatası ya da %1'i aşan bozuk satır payı koşuyu S hesaplanmadan durdurur; "veri yok" hükmü
yazılmaz. (3) b_f* bootstrap ızgarası her zaman 2 ve 4 eşiklerini içine alır (alt uç ≤ 1, üst uç ≥ 6). Ayrıca
kayda geçer: n_y = 8 katmanı doluluk sonrası istasyon sayısıyla kurulur. 26 yapay sınav düzeltmelerden sonra geçti.
