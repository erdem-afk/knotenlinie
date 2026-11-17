# TR-7c bağımsız inceleme 2: sürüm 2 ve üstveri yoklamasının doğrulaması (kısa)

Tarih: 17 Kasım 2026. İncelenenler:
- `TR-7c_tetiklenmis-tremor_ONKAYIT.md` sürüm 2 (commit 41d2ff5) ve b6a3e86'da eklenen D-5 sonuç satırı;
- `TR-7c_USTVERI.md`;
- `kayit/turetme/tr7c/ustveri/tr7c_ustveri.py` ve `.json`.

Hesap: `kayit/turetme/tr7c/inc2/tr7c_inc2.py` (sha256 cff9cdc39bf0bb698218fcdaab9b2333bc52b3f74906d1b6592198ed338846db),
çıktısı `tr7c_inc2.json` (sha256 b8d4bd0ac9bc37443563cc0e4fac40f47e3fff8b8467ed9302bbf42a78606595). Fisher ve X_min
için INCELEME-1'in `tr7c_inc1.py`'si değiştirilmeden yüklendi. Ağ isteği yapılmadı, dalga formu açılmadı, mevcut hiçbir
dosya değiştirilmedi.

## Hüküm: iki cümle eklenince karar metni dondurulabilir

D-1…D-10 sürüm 2'ye birebir ve çelişkisiz girmiş. Dal ızgarası artık temiz: hiçbir nokta dışarıda kalmıyor, hiçbir
nokta iki dala düşmüyor. Üstveri yoklaması körlüğü bozmadan yapılmış ve kural sonuçtan önce commit edilmiş.

Yazarın işaret ettiği BK.PKD riski için iki şey eksik: bir kanal seçim kuralı ve koşuda k düşerse ne olacağını söyleyen
bir kural. İkisi de karar metni dondurulmadan önce girmeli (E-1, E-2). D-3'e göre bunlar dondurmadan sonra
değiştirilemeyen tanımlardır.

## 1. D-1…D-10 ve dal ızgarası

**Birebir denetimi.** `d_aynen` bölümü INCELEME-1 §9'daki 12 alıntı cümlesini (D-8 ve D-9 ikişer cümle) boşluklar
normalleştirilerek sürüm 2'de aradı; 12'si de birebir bulundu. Z1–Z8 de hâlâ birebir duruyor.

**Yerleşim.** Eşleme tablosu §14.2 doğru. D-7 Z4'ün altında, D-8'in iki cümlesi doğru yerlerde (§7.4 ve §6.1), D-9 ile
D-10'un etkileri §6.1 özet tablosunda ve §6.2'nin "VAR" şartlarında görünüyor.

**Izgara.** `dal_v2` bölümü bütün tamsayı ızgarasını yeniden saydı: n_N 0–29 (D-1), Z4 ve D-7 okuma kuralıyla.

| Sonuç | Nokta sayısı |
|---|---|
| Toplam | 13 742 388 660 |
| (a) | 8 690 684 640 |
| (b) | 268 505 632 |
| (c) | 747 893 768 |
| (d) | 962 829 765 |
| (e) | 3 072 474 855 |
| Hiçbir dala düşmeyen | 0 |
| İki dala düşen | 0 |
| D-7 ikinci cümlesinin (e) dışında uygulandığı | 0 |

INCELEME-1'in bulduğu (d) / (e) çelişkisi kapanmış.

**Etiketler.** D-9, D-10 ve (b′) etiketleri yalnız (b) içinde iş görüyor ve yalnız "VAR"ı engelliyor. Dal
değiştirmiyorlar, birbiriyle de çelişmiyorlar.

**Sonuçtan sonra oynanabilecek serbestlik.** Metinde yalnız şu ikisini buldum:
- Başvuru kanalının seçimi (§3, E-1).
- Koşuda başvuru istasyonu düşerse ne yapılacağı (§3, E-2).

## 2. Üstveri yoklaması ve körlük

**Sıra doğru.**
- 41d2ff5 (19:10:18): kural sürüm 2'de, k < 7 ile.
- 22871d8 (19:13:12): betik commit edildi.
- 19:24: koşu.
- b6a3e86 (19:25:56): sonuç.

22871d8 ile b6a3e86 arasındaki betik farkı üç şeyden ibaret:
- yol düzeltmesi;
- SCEDC availability ayrıştırıcısı;
- k_3 bilgi satırı.

Karar satırına (`k < 7 ya da n_P < 8 ya da n_N < 20`) dokunulmamış.

**İstekler.** Betik `dataselect` içeren her URL'yi `assert` ile reddediyor. json'da `dataselect_istegi` 0. İstenenler
yalnız ComCat event, StationXML ve availability. k_3 için availability, R başı ile W sonu arasını sorguluyor. Bu yalnız
zaman aralığıdır, içerik değildir.

**İkinci koşunun ekrana düşen sayıları körlük sorunu değil.** Görülenler üç şeydi:
- liste istasyonu sayısı;
- K1b açık payı;
- tetikleyici kaydı.

Hepsi katalog ve üstveridir. Algılayıcının W içeriği hakkında hiçbir bilgi taşımaz.

Bu koşudan sonra yapılan ayrıştırıcı düzeltmesi yalnız CI (SCEDC) kanallarının örtüsünü etkiler. Karar bu düzeltmeden
bağımsızdır: her P olayında başvuru istasyonu BK.PKD'dir (8 km), k = 10 PKD'den gelir ve CI istasyonları hiçbir olayda
seçilen istasyon değildir.

Tek eksik, ikinci koşunun istek günlüğünün saklanmamış olması. Aynı kod ve aynı `assert` ile yapıldığı için kabul
edilebilir, belgede de açıkça yazılı.

## 3. BK.PKD riski

**Sürüm 2 bu riski kısmen kapsıyor.** Koşuda W içi örtü yetersiz çıkarsa olay "modülasyon ölçülemedi" sayılır (§5
madde 4). Ölçülebilen olay 3'ten azsa D-7 ile dal (e) işler.

**Kapsamadığı iki boşluk var:**

1. **Kanal.** Üstveri yoklaması "herhangi bir uygun düşey kanal"ı yeterli saydı (USTVERI §3, yazarın seçimi). Oysa TR-7
   kodu PGV uygunluğunu istasyonun tek `z_kanal`ı üzerinden değerlendiriyor. PKD'de 2001 ve 2003'te HHZ'nin örtüsü 0.
   Koşu kodu PKD için HH kanalını alırsa 2001–2003'ün dört P olayında modülasyon kendiliğinden "ölçülemedi" olur ve k 6'ya
   iner. Bu seçim bugün metinde yok; kod yazılırken, yani koşudan önce ama karar metni dondurulduktan sonra, verilmiş
   olur.
2. **Koşuda k < 7.** D-5 bir dondurma kuralıdır. Koşuda k'nin düşmesi durumunda metin "durulur mu, yeniden mi koşulur,
   hangi dal" sorusunu açık bırakıyor. Sonuç görüldükten sonra bir "yöntem" ya da "uygulama hatası" yorumuna kapı
   açmamak için bunu yazmak gerekiyor.

## 4. Karar metni dondurması için eklenecek cümleler

**E-1** (§4.1 "Modülasyon ölçüsü" maddesinin altına):

> "Başvuru istasyonu ve kanalı koşuda olay başına şöyle belirlenir (TR-7 §6.4 ve §6.6'nın uygulaması): liste
> sınıfındaki istasyonların bant kodu B ya da H, alet kodu H olan ve olay anındaki StationXML epokunda |H(0,02 Hz)| /
> |H(1 Hz)| ≥ 0,5 veren düşey kanallarından, indirilen veride W ve R örtüsü (TR-7 §4.2 sayımıyla) ≥ %90 olanlar
> uygundur. Uygun kanalı olan istasyonlardan iz köşe ortalamasına en yakını seçilir; onun uygun kanallarından önce HH,
> yoksa BH alınır. Yatay kanallar seçilen düşey kanalla aynı konum ve bant kodundan alınır; ikisi birden yoksa M yalnız
> Z bileşeniyle hesaplanır. Bu seçim 2–8 Hz yolunun TR-7 §3.2 `z_kanal` seçiminden bağımsızdır. Aynı kural D-9'un 4 N
> olayında da uygulanır."

**E-2** (§8 D1 satırının altına; D-5'in tamamlayıcısı):

> "D-5 yalnız koşudan önce, üstveriyle bir kez uygulanır (sonuç: k = 10, `TR-7c_USTVERI.md`). Koşuda E-1 ile başvuru
> kanalı bulunamayan olay modülasyon bakımından 'ölçülemedi' sayılır; n_P ya da n_N'de, X_P ya da X_N'de ve Fisher
> sınamasında kalır, yalnız modülasyonun ölçülebildiği olaylara girmez. Koşudaki k (k_koşu) 7'nin altına inse de koşu
> durdurulmaz ve yeniden koşulmaz; dal yalnız Z4 ve D-7 ile verilir. Verideki örtü eksikliği uygulama hatası sayılmaz.
> K1c satırına 'k: üstveriden 10, koşuda [k_koşu]' yazılır. k_koşu < 10 ise k_koşu ile hesaplanan güç (s 0,7, q 0,1;
> `tr7c_inc1.json` `esik.D1_kref_guc_s0.7_q0.1` işlevi) bilgi olarak eklenir."

Bu iki cümle girince metin D-3'ün "karar metni dondurması" için **HAZIR**dır.

## 5. Öneriler (bağlayıcı değil)

- **Ö-j:** Yazarın sınav öncesi beklentisi (§15) karar metni dondurmasına konsun, Tohoku duman sınamasından önce olsun.
  Böylece duman sonucunu da görmeden yazılmış olur.
- **Ö-k:** `TR-7c_USTVERI.md` §1'de "Tetikleyici: ±60 sn içinde M ≥ 7,0 en yakın kayıt" yazıyor. Bu TR-7 §6.5.1a'nın
  işlemsel okuması. Bulunan sapmalar 0–3,1 sn olduğu için sonucu etkilemiyor; koşu kodu aynı tanımı kullanmalı.
- **Ö-f** (INCELEME-1): `ESIK-DAYANAGI.md` satırı, ertelendiği gibi koşu dondurmasında eklensin.

## 6. Doğrulanamayanlar

- BK.PKD'nin 2001–2003 W pencerelerindeki gerçek örtüsü. Availability gün dosyası düzeyinde; koşudan önce
  görülemez.
- TR-7 kodunun PKD için hangi kanalı `z_kanal` seçeceği. Kod okunmadı; E-1 bu sorunu kodun seçiminden ayırır.
- İkinci üstveri koşusunun istek günlüğü. Saklanmamış.
