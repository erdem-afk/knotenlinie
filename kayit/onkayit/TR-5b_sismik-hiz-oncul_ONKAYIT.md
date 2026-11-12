# TR-5b ön kayıt: M ≥ 6,0 sığ depremlerden önceki son yılda ortam gürültüsü dv/v, küresel olay–kontrol sınavı

Sürüm 1, 12 Kasım 2026. Durum: **TASLAK sürüm 1, incelemeye hazır.** Dondurulmadı; hiçbir dalga formu indirilmedi,
açılmadı ya da yoklanmadı. Kol: TR. Ata: TR-5 (`TR-5_TR-4_SAYIM.md`, Ek 1). Maliyet bu belgeye kadar 0 €.
**Koşu, sunucu onayı gelince başlar** (makine kiralama ve 50 €'yu aşan her harcama proje sahibinin kararıdır, §5.4).
Ön kayıt bu karardan bağımsız dondurulur.

Betikler ve bağlayıcı liste `kayit/turetme/tr5/` altında (yeni dosyalar, `tr5b_` önekli; mevcut TR-5 dosyaları
değişmedi). Hepsi yalnız numpy ve standart kitaplıkla, `python3 -I -B` ile çalışır:
- `tr5b_liste.py`: olay, istasyon, kontrol ve plasebo listesini kurar; hacmi hesaplar (≈ 14 sn).
- `tr5b_yapay.py`: dv/v zincirinin başvuru uygulaması ve yapay veri doğrulaması (§6.1; ≈ 10 dk).
- `tr5b_guc.py`: hüküm kuralının güç ve hata olasılıkları (§6.2; ≈ 6 sn).
- Çıktılar: `tr5b_liste.json` (bağlayıcı), `tr5b_olaylar.csv`, `tr5b_kontroller.csv`, `tr5b_ozet.json`,
  `tr5b_yapay_sonuc.json`, `tr5b_guc_sonuc.json`.

Bu metindeki bütün sayılar bu betiklerin çıktısıdır. Literatür sayıları OpenAlex özetlerinden alındı. Özetten
doğrulanamayan her sayı "doğrulanamadı" diye işaretlidir.

## 0. Kimlik ve tasarım değişikliğinin kaydı

**TR-5b, TR-5'ten ayrı bir kimliktir.** TR-5'in ana tasarımı (M ≥ 6,5; 5 yıl taban; 100 km içinde ≥ 2 yer)
üstveri sayımında K = 8, tek yer şartıyla K = 15 verdi. Gerçek doluluk süzgecinden sonra bu sayılar K 8–11'e indi.
Kapı K ≥ 20 olduğu için TR-5 ana tasarımı **güç yok** durumundadır (`TR-5_TR-4_SAYIM.md` Hüküm ve Ek 1).

TR-5b üç tasarım değişikliğiyle kuruldu:
1. M ≥ 6,5 yerine M ≥ 6,0;
2. 5 yıllık taban yerine 3 yıllık taban;
3. ≥ 2 yer şartı yerine ≥ 1 yer.

**Bu değişiklikler sayım görüldükten sonra yapıldı.** Görülen sayılar K ve plasebo kümesi sayılarıdır. Hiçbir dv/v
değeri, dalga formu ya da olay penceresinden türetilmiş bir ölçü görülmedi. Seçim şöyle yapıldı: Ek 1'in 16 satırlık
doğrulanmış sayım tablosunda **iki kapıyı (K ≥ 20, plasebo ≥ 10) üç doluluk kuralının üçünde de geçen tek biçim**
alındı (ana 37/20, gevşek 51/24, sıkı 26/14). Bu bir çatallanmadır. K üstünden yapılmıştır, sonuç üstünden değil. Ama
"sayımdan önce konmuş" sayılmaz. Hedef artık "büyük deprem" değildir: örneklemin %69'u (31/45 olay) M 6,0–6,4'tür.

Bu taslakta ayrıca şu kararlar verildi. Hepsi dv/v verisi görülmeden alındı ve hepsinin K'ye etkisi aşağıda
yazılıdır:
- Hawaii adasındaki iki olay ana hükümden çıkarıldı, ayrı satırda raporlanır (§2.7). K 37 → 35.
- Kontrol sayısı 10'dan 5'e indi, 5 yedek eklendi (§2.3). K değişmedi.
- Kontrol merkezi başına kota 3 küme kondu (§2.3). K değişmedi.
- KOERI ve 6G istasyonları kontrollerden çıkarıldı (§2.3). K değişmedi.
- Ölçü işaretli seçildi (§4.1).

Yazarın bildiği olaylar var: Napa 2014, L'Aquila 2009, Kahramanmaraş 2023, Ridgecrest 2019 öncüsü. Bu olaylarla ilgili
yayımlanmış dv/v sonuçlarının bir kısmını yazar özetlerden okudu (§3.7). Hiçbiri olay öncesi yıl ölçekli bir dv/v
değeri içermiyor. Muñoz-Burbano 2023 bildirisi Kahramanmaraş için öncül incelemesinin "sürdüğünü" yazıyor, sonuç
vermiyor.

## 1. Soru ve neyi ölçmediği

**Soru.** M ≥ 6,0 sığ bir depremden önceki son yılda, dış merkezin 100 km içindeki istasyonlarda ortam gürültüsünden
ölçülen sismik hız değişimi (dv/v), aynı istasyonun önceki iki yılına göre, aynı tarihlerde depremsiz kontrol
yerlerinde ölçülen aynı farktan sistematik olarak farklı mı?

İşaret önceden bilinmiyor. Sınav bu yüzden iki yönlüdür (§4.1).

**Neyi ölçmez.** Bu bir deprem tahmini, yanlış alarm oranı ya da olasılık iddiası değildir. Olumlu bir sonuç yalnız
ileriye dönük yeni bir ön kaydın (TR-4 türü izleme) açılma şartıdır. dv/v en iyi durumda gerilme **değişimini**
ölçer, kırılmaya uzaklığı ölçmez. Gelgit duyarlılığı ≈ 0,5 MPa⁻¹'dir (Hillers 2014; DD-5 ve TR-5 S2 notu).

**Ölçü ne görür, ne görmez.**
- Ana bant 0,5–2 Hz'dir ve tek istasyon bileşenler arası çapraz ilişki (SC) kullanılır. Bu, kabaca üst birkaç km'yi
  örnekler, en çok sığ kısmı. Derin hazırlık sürecinin yüzeye yansımayan kısmı görülmez.
- Ana hüküm örneklemi 35 kümedir (volkaniksiz). 37 kümenin bölge dağılımı: İtalya-Balkan-Ege 7, Kaliforniya 3,
  Alaska-Aleut 3, Meksika-Orta Amerika-Karayip 3, Anadolu 2, Endonezya-Filipinler 2, Çin-Himalaya 2, Japonya, Yeni
  Zelanda, And ve PNG-Solomon birer, öteki 11 (Hawaii'nin iki olayı dahil). Örneklem ağırlıkla kıtasal ve
  sınır-dönüşüm ortamındadır. Mekanizma (45 olay): doğrultu atımlı 17, öteki 19, bilinmeyen 9. Japonya'dan yalnız
  Kumamoto öncüleri girer (tek istasyon, JP.JNU). Sonuç dalma-batma kuşaklarına genellenmez.

## 2. Veri ve bağlayıcı liste

**2.1 Olaylar.** ComCat, `type = earthquake`, M ≥ 6,0, derinlik ≤ 30 km, 2000-01-01 ile 2023-12-31 arası (TR-2
`m6_havuz.csv`, sha256 `969c5c54…`). T, olay günüdür (UTC tarih). Temiz pencere şartları, olayın kendisi dışında,
[T − 5 yıl, T) aralığında dış merkeze göre uygulanır (5 yıl = 3 yıl taban + 2 yıl iyileşme payı):
- Ş1: 150 km içinde M ≥ 6,0, derinlik ≤ 40 km olay yok;
- Ş2: 500 km içinde M ≥ 7,0, derinlik ≤ 70 km olay yok;
- Ş3: 1000 km içinde M ≥ 8,0, derinlik ≤ 70 km olay yok.

Aynı gün olan olaylar tek kümeye düşer. Kahramanmaraş'ın dört olayı tek kümedir; Kumamoto'nun iki öncüsü (14 Nisan
2016) da tek kümedir. Kural ve kod `sayim_ustveri.py` ile aynıdır (`TR-5_TR-4_SAYIM.md` §2.5).

**2.2 İstasyonlar.** BHZ ya da HHZ, ≥ 10 örnek/sn, açık. Kanal epokları 30 günden kısa boşluklar birleştirilerek
[T − 3 yıl, T − 1 g] aralığını kesintisiz kapsamalıdır. R = 100 km. 1 km içindeki istasyonlar tek yer sayılır ve en
yakın en çok 3 yer alınır. Olay ve plasebo istasyonlarına ayrıca TR-5 Ek 1'in ay doluluğu süzgeci uygulanır
(`tr5_doluluk.csv`, `dolu_ana`: ayların ≥ %80'inde veri ve en uzun boşluk ≤ 3 ay). Sonuç:
- 45 olay, **K = 37** bağımsız küme;
- plasebosu olan 25 olay, 20 küme.

Bu sayılar Ek 1'deki sayıların aynısıdır; betik eşitliği denetler. Olay başına istasyon sayısı: 1 istasyon 34 olay,
2 istasyon 7 olay, 3 istasyon 4 olay. 60 olay istasyon-penceresinin dış merkeze uzaklığı: medyan 50,2 km, çeyrekler
25,1 ve 75,7 km.

**2.3 Kontroller (aynı epok, depremsiz yer).** Aday merkezler, 1976–2025 arası M ≥ 6,5 (derinlik ≤ 40 km) olayların
dış merkezleridir. Bunlar 25 km içinde tekilleştirilmiş 1161 merkezdir. Sıralama SHA-256(`{olay ComCat kimliği}|{merkez
ComCat kimliği}`) onaltılık değerine göre artandır. Şartlar `sayim_ustveri.py` ile aynıdır:
- (a) merkez olaya ≥ 600 km uzak;
- (b) [T − 5 yıl, T + 2 yıl] aralığında merkez için Ş1–Ş3 sağlanıyor;
- (c) 100 km içinde ≥ 1 yer var;
- (d) hiçbir kontrol istasyonu olaya 600 km'den yakın değil;
- (e) seçilen kontroller birbirinden ≥ 150 km uzak.

TR-5b'de bunlara üç ek kural eklendi:
- **Kota.** Bir merkez, aynı epok türünde (olay ya da plasebo) en çok 3 bağımsızlık kümesinde kontrol olur (TR-1
  inceleme 2, bulgu 4). Olaylar (T, kimlik) sırasıyla işlenir; kotası dolmuş merkez atlanır.
- **Kontrol istasyonu dışlaması.** KOERI'de barınan istasyonlar ve 6G ağı kontrol olarak kullanılmaz. KOERI'nin tek
  akış hızı ≈ 40 KB/s ölçüldü; bu hızla kontroller koşuyu haftalarca uzatırdı (§5.2). 6G'ye atılan deneme isteği 204
  döndü, yani veri yok. Bu kural yalnız kontrollere uygulanır. Olay istasyonu KO.DKL ve KO.BODT kalır.
- **5 bağlayıcı + 5 yedek.** Her olay için SHA sırasında ilk 10 geçerli merkez listelenir. Koşuda 1. aşamada gün
  doluluğu tutan ilk 5 merkez kullanılır (§5.1).

Sonuç: 45 olayın hepsinde 10 aday var. İlk 5'lerdeki 225 yuva 117 farklı merkezden doluyor ve hiçbir merkez 3'ten
fazla kümede yok. Kotasız sayımda bir merkez 10 kümede kullanılıyordu.

**2.4 Plasebo (aynı yer, olaysız zaman).** Plasebo epoğu T′ = T − 1095 g, penceresi [T′ − 1095 g, T′ − 8 g]'dir.
İstasyonlar [T − 2190 g, T − 1 g] aralığını kesintisiz kapsamalı ve ay doluluğu süzgecini geçmelidir. Dış merkez
[T − 8 yıl, T) aralığında Ş1–Ş3'e göre sakin olmalıdır, olayın kendisi hariç (`sayim_ustveri.plasebo_say`).
Plasebo kontrolleri T′ epoğunda aynı kurallarla ve kotayla seçilir. SHA anahtarı `{kimlik}|plasebo|{merkez}`
biçimindedir. Sonuç: 25 olay, 20 küme. Volkaniksiz eşleşik plasebo kümesi **18**'dir. Plasebo kontrollerinin ilk
5'leri 68 farklı merkezden doluyor.

**2.5 Aygıt değişimi.** Bir istasyon-penceresi şu durumda geçersizdir: pencere içinde başlayan bir kanal epoğunda,
aynı konum ve kanal kodunun önceki epoğuna göre sensör tanımı ya da yönelim (azimut, eğim) değişmişse. Sensör tanımı
seri numarası (`S/N…`) atılarak karşılaştırılır. Örnekleme hızı ve ölçek değişimi sayılmaz, çünkü veri 20 sn⁻¹'e
indirgenir ve ÇİF'ler normalleştirilir. Kural koşunun 1. aşamasında üç bileşenin üstverisiyle uygulanır. Olay,
kontrol ve plasebo için aynıdır.

Bugünkü üstveri yalnız Z kanallarını içeriyor. Z kanallarıyla yapılan önizleme şunu gösteriyor:
- 6 olay istasyon-penceresi düşüyor (HL.VLS, ES.EALB, IV.CAMP, CM.PRV, IU.HNR ×2);
- 4 olay bütün istasyonlarını kaybediyor (us10004gy9, us1000hwaj, us7000irfb, us7000irfm);
- bunun sonucunda **K 35 → 32**, eşleşik plasebo 18 → 17;
- ilk 5 kontrollerde 27 istasyon-penceresi etkileniyor (bunların yerine yedek gelir).

Bu kural listeyi değiştirmez. Listede bir alan olarak (`aygit_degisimi_Z`) önizleme diye durur.

**2.6 M ≥ 5 maskesi (yakın orta depremler).** ComCat'ten M ≥ 5,0, derinlik ≤ 70 km, 1990-01-01 ile 2025-12-31 arası
olaylar indirildi. Sorgu 12 Kasım 2026 03:33 UTC'de, `endtime=2026-01-01T00:00:00` ile dört parça hâlinde yapıldı:
49 971 olay; parçaların sha256'ları `tr5b_liste.json` → `girdi_sha256` alanında. Dosyalar (≈ 12 MB) şu an depo
dışında, karalama dizinindedir. Dondurmadan önce TR-2'nin anlık görüntüsü gibi proje dosyalarına arşivlenmelidir. Bir istasyonun 50 km içindeki her
böyle olay için [t_q, t_q + 59 g] günlerinin ÇİF'leri yığından, başvurudan ve ε'dan atılır. Bu kural olay, kontrol ve
plasebo istasyonlarına aynen uygulanır.

Olayın kendisi maskeye girmez. Ama olay penceresindeki **öncüler** (son yıl dahil) maskelenir. Maskenin bedeli: 60
olay istasyon-penceresinin 17'sinde ortalama 26,2 gün; ilk 5 kontrollerin 408 istasyon-penceresinin 83'ünde maskeli
gün var. M ≥ 6 olaylar için Ş1–Ş3 temiz pencere kuralları geçerlidir. Kosismik etkinin 60 günden uzun süren kuyruğu
(Napa'da 50 günde ≈ %50 toparlanma; Taira 2015, özetten) maskeyle tam silinmez. Kalan etki M 5–6 ve ≤ 50 km olaylar
içindir ve olay ile kontrole simetriktir.

**2.7 Volkanik yerler.** Ana hükümden çıkarılan iki olay var: hv70116556 (2018 Leilani M6,9; istasyonlar HV.JOKA,
JCUZ, NPOC Kīlauea doğu riftinde) ve hv6000471 (2006 Hawaii M6,0; IU.POHA, GE.MAUI). Gerekçe: Kīlauea'da
püskürmeden önce hız düşüşü raporlanmıştır (Donaldson 2019, özetten nitel). Hawaii'de dv/v magma basıncıyla
oynar; sinyal deprem öncülünden ayrılamaz. Bu iki olay ayrı bir bilgi satırında raporlanır.

İkinci bir bilgi satırında, olay istasyonu volkan yapısının üstünde olan iki olay daha dışlanır: usp000br01 (AV.AKT,
Akutan) ve usp000jr55 (NO.JMIC, Jan Mayen). Bunlar ana hükümde kalır. Kural yalnız bu adlarla tanımlıdır, çünkü bu
oturumda Holosen volkan listesi yoklanmadı.

**2.8 Bağlayıcı liste.** Liste `tr5b_liste.json`'dur. Kurallar, olaylar, istasyonlar (merkez, uzaklık, en düşük
≥ 10 sps, maske günleri, aygıt önizlemesi), 10 kontrol, plasebo ve 10 plasebo kontrolü bu dosyadadır. Girdi
dosyalarının sha256'ları da içindedir. Metinle liste çelişirse liste geçerlidir.

| Dosya | sha256 |
|---|---|
| `tr5b_liste.json` | `581b0ccabc400083bbc58c68c23be878988fbcc3f74b4ba44ddbf4a1aacaacfb` |
| `tr5b_olaylar.csv` | `3e44c96fa41ad341564c11ef4ebcccd1243dc81ebc6784986a78d109b68bdf99` |
| `tr5b_kontroller.csv` | `245d496968327a245bea158481cd41a61cf7ebe44e770f94b4c72a6e5e3f217b` |

Yeniden üretim:
`python3 -I -B kayit/turetme/tr5/tr5b_liste.py <tr5/ham> <ngl> <tr2/ham> <tr5b_kat>`.
Girdiler depo dışındadır: TR-5 üstverisi, TR-1 ve TR-2 katalogları, M ≥ 5 kataloğu. Depodaki tek girdi
`tr5_doluluk.csv`'dir (sha256 `1e078723…`). `doluluk_yokla.py say` yeniden koşulursa bu dosya yeniden yazılır. TR-5
satırları değişmemelidir; liste sha256'yı denetler. Koşu kodu listenin sha256'sını
denetler ve uyuşmazlıkta durur. Bilinen metin–kod farkları şunlardır, liste geçerlidir:
- Yıllar `floor(n × 365,25)` gündür (3 yıl = 1095 g).
- Ş1–Ş3'ün "yok" aralığı yarı açıktır, [a, b).
- Plasebo istasyon kapsamı [T − 2191 g, T − 1 g] olarak hesaplanır (`yil(6)` = 2191 g).

## 3. dv/v ölçümü (sayısal, veri görülmeden sabit)

**3.1 İndirme biçimi.** Her istasyon-gün için yerel ortalama güneş saatiyle 00:00–04:00 arasındaki 4 saat
indirilir. UTC başlangıç saati (24 − boylam/15) mod 24'tür, tam saate yuvarlanır. Bu pencere gece olduğu için
kültürel gürültü en azdır. Üç bileşen alınır: Z ile N/E ya da 1/2. Kanal, aynı konum kodunda üç bileşeni olan en
düşük ≥ 10 sps bant kodudur; BH, HH'ye tercih edilir. Konum kodu sırası `''`, `00`, `10`, sonra alfabetik. Bir
istasyon-penceresi içinde kanal ve konum kodu değişmez. Tam gün yerine 4 saat seçildi, çünkü hacmi 6 kat küçültür.
Bedeli, ölçüm gürültüsünün kabaca √6 ≈ 2,4 kat büyümesidir: Illien 2023'e göre dv/v SNR'si toplam işlenen veri
süresiyle ölçeklenir (özetten nitel doğrulandı). §6.1'deki yapay değerler bu bedeli içermez.

**3.2 Ön işlem (saatlik pencere, bileşen başına).**
1. Saat penceresi kabul edilir, eğer üç bileşenin her birinde örneklerin ≥ %99'u varsa. 1 sn'ye kadar olan boşluklar
   doğrusal aradeğerlenir.
2. Ortalama ve doğrusal eğilim çıkarılır, %5 Hann konik uygulanır.
3. Veri 20 sn⁻¹'e indirgenir: FFT ile, 8 Hz üstü sıfırlanarak, 0,5 Hz'lik kosinüs geçişle. Tepki giderilmez. Ölçü bir
   oran olduğu ve kanal pencere içinde değişmediği için gerekmez.
4. Enerji reddi: 0,5–2 Hz bant RMS'i, aynı istasyon-bileşen-pencerenin bütün saatlerinin medyan RMS'inin 3 katını
   aşan saat atılır. Bu, deprem ve aksaklıkları ayıklar. Medyan 1. aşamada yalnız veriden hesaplanır, sonuçtan
   bağımsızdır.
5. Spektral beyazlatma: genlik spektrumu [0,5; 2,0] Hz'de 1'e eşitlenir, 0,4–0,5 ve 2,0–2,1 Hz kosinüs kenarlı;
   bant dışı 0. Faz korunur.

**3.3 Çapraz ilişki.** Çiftler ZE, ZN ve EN'dir (yatay bileşenler 1/2 ise Z1, Z2, 12). Döndürme yapılmaz. Her kabul
edilen saat için ÇİF gecikme ±60 sn aralığında hesaplanır ve enerji çarpımının karekökü ile normalleştirilir. Günlük
ÇİF, kabul edilen saatlerin ortalamasıdır; ≥ 2 saat gerekir. Bir çift için gün geçerlidir, eğer ≥ 2 saati kabul
edilmişse ve gün maskede değilse (§2.6).

**3.4 Başvuru, yığma, germe.**
- **Başvuru:** pencere [T − 1095 g, T − 8 g] içindeki geçerli günlük ÇİF'lerin ortalaması. Çift ve istasyon-pencere
  başına ayrı.
- **Yığın:** d gününe ait ε, [d − 9, d] aralığındaki geçerli günlük ÇİF'lerin ortalamasından gelir (geriye dönük
  10 gün). ≥ 5 geçerli gün gerekir.
- **Germe:** iki yanlı koda penceresi 10 ≤ |τ| ≤ 40 sn. Başvuru R(τ(1 + ε)) ile yığın arasında, ε ∈ [−%0,5; +%0,5]
  ızgarasında (adım %0,001) ilişki katsayısı hesaplanır. En büyük değer parabolle inceltilir. ε doğrudan dv/v'dir:
  hız artışı ε > 0.
- **Geçerlilik:** CC ≥ 0,40 ve ε ızgara kenarında değil.

Ana yöntem germedir. MWCS kullanılmaz, çünkü germe düşük SNR'de daha kararlıdır (Hadziioannou 2009; bu oturumda
özeti okunmadı, doğrulanamadı) ve tek parametreyle çalışır. Başvuru uygulaması `tr5b_yapay.py`'dir
(`germe_olc`, `zincir`, `ay_esle`). Koşu kodu bu fonksiyonların sayısal sonucunu yeniden üretmek zorundadır (§4.2,
adım 1).

**3.5 Hüküm ölçüsü Δ (çift başına, %).** Pencere üç yıl dilimine ayrılır:
- A = [T − 1095, T − 731];
- B = [T − 730, T − 366];
- C = [T − 365, T − 8].

Takvim ayı m = 1…12 için C'deki ve A∪B'deki ε'ların ortalamaları alınır; ikisinde de ≥ 10 geçerli gün gerekir. Ölçü:

**Δ = ortalama_m [ ort(ε | C, m) − ort(ε | A∪B, m) ]**

Ortalama eşleşen aylar üzerinden alınır ve ≥ 9 eşleşen ay gerekir. Ay eşlemesi durağan mevsimsel döngüyü boşluklu
veride de düşürür. Tam yıl pencerelerinden farkı budur. Ana ölçü **düzey farkıdır**, eğilim değildir. Gerekçe: A∪B'ye
uydurulan doğrusal eğilimi C'nin ortasına uzatmak, beyaz gürültüde ölçü gürültüsünü ≈ 2,8 kat büyütür (orta noktaya
1,5 yıl uzaklık, 2 yıllık taban; ilişkili gürültüde daha çok). Çok yıllı eğilimler (hidroloji, eski depremlerden
toparlanma) aynı epoktaki kontrollerle ve aynı yerdeki plaseboyla karşılaştırılır. Eğilimden arındırılmış Δ bir
bilgi satırıdır.

**3.6 Toplama.**
- İstasyon Δ: geçerli çiftlerin medyanı. ≥ 2 geçerli çift gerekir; 2 çiftte medyan ortalamaya eşittir.
- Olay Δ_e: geçerli istasyonların ortalaması.
- Kontrol Δ_c: o kontrolün geçerli istasyonlarının ortalaması.
- Plasebo Δ_p: plasebo penceresinde aynı tanım.

**3.7 Gerekçe ve literatür (OpenAlex, yalnız özetler).**

| Seçim | Dayanak | Durum |
|---|---|---|
| SC, yüksek frekans | Hobiger 2014 (10.1093/gji/ggu115): SC yüksek, CC 0,5 Hz altı frekansta en iyi | Doğrulandı |
| 0,5–2 Hz ana bant | Hobiger 2016 (10.1093/gji/ggw066): kosismik düşüş frekansla artar, fay yakınında en büyük; Zaccarelli 2011 (10.1029/2011gl049750): L'Aquila'da en güçlü 0,5–1 Hz; Ikeda ve Tsuji 2018 (10.1186/s40645-018-0211-8): 0,7–2 Hz | Nitel doğrulandı. Bant sınırları literatürün ortak aralığından seçildi; tek bir kaynaktan değil |
| Bilgi bandı 2–4 Hz | Clements ve Denolle 2023 (10.1029/2022jb025553): SC, 2–4 Hz, germe, 700 istasyon; üst ≈ 500 m | Doğrulandı. Hidrolojiye en duyarlı bant; bu yüzden bilgi satırı |
| Germe | Clements ve Denolle 2023 germe kullanır; Hadziioannou 2009 | İlki doğrulandı, ikincisi doğrulanamadı |
| 10 günlük yığın, CC ≥ 0,40, koda 10–40 sn, 4 saat/gün | Yaygın değerler | **Doğrulanamadı.** Yalnız yapay veride sınandı (§6.1) |
| Kosismik büyüklük (PK) | Taira 2015 (10.1002/2015gl065308): Napa M6,0'da ≈ %0,08 düşüş, 50 günde ≈ %50 toparlanma; Yu ve Hung 2012 (10.1029/2012gl051970): Taitung M6,1, CCF 0,1–0,9 Hz'de ≈ %0,1, ACF 2–8 Hz'de > %1 | Doğrulandı |
| Uzaklıkla sönüm | Boschelli 2021 (10.1029/2020jb021465): Ridgecrest M7,1 sonrası 50 km'den uzak istasyonlarda düşüş yok (yüksek frekans ACF); düşüş kırığa uzaklığın logaritmasıyla ölçekli | Doğrulandı |
| İstasyonlar arası genlik saçılımı | Richter 2014 (10.1002/2013jb010695): tek istasyonda düşüş ∝ PGA, istasyonlar arasında tutmaz; Ikeda ve Tsuji 2018: düşüş PGV ile ilişkili | Doğrulandı |
| Öncül yönü belirsiz | Tinti/Scuderi 2016 (10.1002/2016jb013545): laboratuvarda hazırlık evresinde Vp düşüşü. Ikeda ve Tsuji 2018: Nankai'de uzun dönem hız artışı, gerilme birikimine bağlandı. Chen 2013 (10.1002/2013gl058682): Wenchuan'dan hemen önce belirgin öncül yok | Doğrulandı (nitel). Biri düşüş, biri artış yönünde: iki yönlü sınav |
| Çok yıllı hidroloji | Clements ve Denolle 2023 (2011–2016 kuraklığında çok yıllı artış); Zhang 2023 (10.1029/2023gl103419) | Nitel doğrulandı. Genlik doğrulanamadı |
| Yıl ölçekli, çok olaylı pasif dv/v öncülü | – | Bulunamadı. Beklenen sonuç H0 ya da ayırt edilemez |
| Kırık boyu L(M) = 10^(−2,44 + 0,59 M) km | Wells ve Coppersmith 1994, yeraltı kırık boyu, bütün türler | Bellekten. **Doğrulanamadı** |

## 4. Hüküm satırı (tek, sıralı, otomatik)

**4.1 Puan ve ölçü.**
- **Olay puanı:** r = [#(Δ_c < Δ_e) + 0,5 · #(Δ_c = Δ_e)] / n_c. Burada n_c, olayın geçerli kontrol sayısıdır;
  ≥ 3 gerekir.
- **Küme puanı:** kümedeki olayların r ortalaması.
- **Ana ölçü r̄:** volkaniksiz geçerli kümelerin puanlarının eşit ağırlıklı ortalaması. Güven aralığı t dağılımıyla
  (df = K − 1): r̄ ± t · s / √K.

**Neden işaretli.** Ölçü işaretlidir: Δ'nın kendisi sıralanır, |Δ| değil. İki gerekçe var, ikisi de
`tr5b_guc.py` ile hesaplandı:
1. **Ölçek farkına dayanıklılık (TR-1 dersi).** Olay yerleri kontrollerden 1,5 kat gürültülüyse ve gerçek etki
   sıfırsa, |Δ| ölçüsü %66,6 olasılıkla yanlış H1 verir. İşaretli ölçüde bu oran %5,3'tür.
2. **Güç.** δ = 0,5 σ_Δ kayma için güç işaretli ölçüde 0,68, |Δ| ölçüsünde 0,16'dır.

Bedeli de var. Kümelerin yarısında +δ, yarısında −δ olan karışık işaretli bir etki işaretli ölçüde görünmez
(δ = 1 σ_Δ'da güç 0,009; |Δ| ölçüsünde 0,73). |Δ| ölçüsü bu yüzden bilgi satırıdır.

**Neden iki yönlü.** Literatür iki yönü de destekliyor: laboratuvar hazırlık evresinde düşüş, gerilme birikiminde
artış (§3.7). Hiçbir yön için yıl ölçekli, doğrulanmış bir önsel yok. Hüküm sınaması bu yüzden iki yanlıdır,
α = 0,05.

**4.2 Sıra.** Kod bu sırayı insan müdahalesi olmadan uygular. Bir adım hüküm verirse sonraki adımlar koşmaz.

0. **Veri kapısı (§5.1, 1. aşama sonu).** Sayılan K, gün doluluğu, üç bileşen ve aygıt kuralından sonra en az 1 dolu
   istasyonu ve ≥ 4 dolu kontrolü olan volkaniksiz kümelerin sayısıdır. K_p, ≥ 4 dolu plasebo kontrolü ve dolu
   plasebo istasyonu olan eşleşik kümelerin sayısıdır. **K < 20 ya da K_p < 10 ise hüküm "güç yok" olur.** Bu adımda
   dv/v hesaplanmaz. Aday elenmez; yalnız güç eksikliği yazılır.
1. **Kod denetimi (i), yapay.** Koşu kodu `tr5b_yapay.py`'nin E1/E2 deneyini aynı tohumla yeniden üretir.
   Üç SNR düzeyinde oran_medyan değeri, başvurudakinin ±0,01'i içinde olmalıdır. Değilse hüküm "geçersiz (kod)"
   olur. Kod gerçek veri görülmeden düzeltilir.
2. **Kod denetimi (ii-a), gerçek ÇİF'te.** Sahte olay, her olayın ilk geçerli kontrolüdür. Sahte olayın bütün
   istasyon ve çiftlerinin C dilimindeki günlük ÇİF'lerine −%0,1 germe eklenir: R(τ) → R(τ(1 − 0,001)). Başvuru ve
   yığınlar yeniden kurulur ve oran = (Δ_eklenmiş − Δ_özgün) / (−%0,1) hesaplanır. Sahte olay istasyonlarının
   medyan oranı [0,80; 1,20] dışındaysa hüküm "geçersiz (kod)" olur. Bu adımda yalnız kontrol verisi okunur.
3. **Negatif kontrol N1.** Sahte olay, kalan kontrollere karşı puanlanır. Sahte r̄'nin iki yanlı %95 aralığı 0,5'i
   dışlarsa hüküm "geçersiz (kod ya da tasarım)" olur. H0 altında yanlış tetiklenme olasılığı 0,052'dir (§6.2).
4. **Duyarlılık (ii-b).** 2. adımdaki −%0,1 eklenmiş sahte olay kalan kontrollere karşı puanlanır. r̄_sahte > 0,25
   ise ölçü "kör" sayılır ve hüküm "güç yok" olur. Bu bir kod denetimi değil, güç denetimidir. Gerçek σ_Δ
   %0,1'den büyükse doğru kod da bu adımda durur (§6.2).
5. **Plasebo.** Eşleşik kümelerde r_p hesaplanır (plasebo Δ_p, T′ epoğunun plasebo kontrollerine karşı). r̄_p ve
   aralığı yazılır.
6. **Ana ölçü.** Olay Δ'ları ilk kez bu adımda hesaplanır. r̄, %95 ve %90 t aralıkları ve eşleşik fark
   d = r_e − r_p dosyaya yazılır. Dosyanın sha256'sı koşu günlüğüne geçer.
7. **Zaman kaydırma (bilgi, hükmü değiştirmez).** Aynı veriyle Δ_kay = B − A hesaplanır (ay eşlemeli, aynı kurallar)
   ve kontrollerin aynı ölçüsüne karşı puanlanır: r̄_kay. Ek veri gerektirmez.
8. **Pozitif kontrol (kosismik).** Olay istasyonlarının [T + 1, T + 30] verisi **ilk kez bu adımda okunur**. Okuma
   6. adımın çıktısı yazıldıktan sonra yapılır; gerekçe §4.5'te.
   - δ_ko, istasyon başına: ort ε(yığın sonu [T + 10, T + 30]) − ort ε(yığın sonu [T − 60, T − 8]).
   - Başvuru 3.4'teki olay öncesi başvurudur. Maske [T, T + 30] için uygulanmaz. Öncesinde ≥ 10, sonrasında ≥ 5
     geçerli ε gerekir.
   - Küme δ_ko, kümedeki olayların istasyon ortalamalarının ortalamasıdır.
   - PK kümeleri (önceden sabit, 16 küme): en yakın olay istasyonu ≤ max(30 km, 2 · L(M)) olan volkaniksiz kümeler.
     Kimlikler `tr5b_ozet.json`'da `pk_yakin_*` alanındadır; liste §Ek'tedir.
   - Geçme şartı: ≥ 8 geçerli PK kümesi ve tek yanlı kesin Wilcoxon işaretli sıra testinde p ≤ 0,05 (H1: medyan
     δ_ko < 0). Geçmezse ya da geçerli küme < 8 ise hüküm **"güç yok (yöntem bilinen kosismik düşüşü göstermedi)"**
     olur. 6. adımın r̄'si yalnız bilgi olarak yazılır.
9. **Hüküm** (öncelik sırasıyla):
   - **H1 (yön: artış ya da düşüş).** Üç şart birlikte gerekir:
     - r̄'nin %95 aralığı 0,5'i dışlar;
     - d̄'nin tek yanlı %95 sınırı 0'ı aynı yönde dışlar;
     - r̄_p'nin %95 aralığı 0,5'i aynı yönde dışlamaz.

     H1 ile birlikte r̄'nin %90 aralığı [0,35; 0,65] içinde kalıyorsa hüküm "H1, küçük etki" diye yazılır.
     r̄_kay da aynı yönde 0,5'i dışlıyorsa "H1, son yıla özgü değil" notu eklenir.
   - **H0 (eşdeğerlik).** r̄'nin %90 aralığı [0,35; 0,65] içinde. Bu, iki tek yanlı %5 sınaması (TOST) demektir.
   - **Ayırt edilemez:** öteki bütün durumlar. Ana aralık 0,5'i dışladığı hâlde plasebo şartı tutmuyorsa hüküm
     "ayırt edilemez (yer yanlılığı dışlanamadı)" diye yazılır.

**4.3 Hükümlerin anlamı.**
- **H1:** Bu örneklemde, olay öncesi son yılın dv/v düzeyi, aynı yerin önceki iki yılına göre, aynı epoktaki kontrol
  yerlerinden sistematik olarak farklıdır. Bu fark aynı yerin üç yıl önceki penceresinde yoktur. Tahmin becerisi
  iddiası değildir.
- **H0:** Bu ölçü (0,5–2 Hz SC, düzey farkı, 1 yıl / 2 yıl) bu örneklemde 0,35–0,65 AUC dışında bir etki
  göstermiyor. Kabaca |δ| ≳ 0,55 σ_Δ'lık tek yönlü kayma dışlanır. Karışık işaretli etkiyi, başka bantları, daha kısa
  öncül pencerelerini ve M ≥ 7'yi kapatmaz.
- **Ayırt edilemez:** Etki yok anlamına gelmez.
- **Güç yok:** Ölçü bu veriyle sınanamadı.

**4.4 Önceden hesaplanan hüküm olasılıkları.** Hesap `tr5b_guc.py` ile yapıldı: K = 35, eşleşik plasebo 18,
n_c = 5, 20 000 yineleme, küme yapısı listeden. δ, σ_Δ birimiyle olay kaymasıdır; AUC = Φ(δ/√2). Plasebo etkisiz
varsayıldı. Dört satırdaki σ_Δ, gerçek dünya σ_Δ'sıdır (bilinmiyor; §6.2).

| δ (σ_Δ) | AUC | H1 | H0 | Ayırt edilemez | Yalnız ana aralık 0,5'i dışlar |
|---|---|---|---|---|---|
| 0 | 0,500 | 0,014 | 0,654 | 0,332 | 0,048 |
| 0,25 | 0,570 | 0,076 | 0,367 | 0,557 | 0,229 |
| 0,50 | 0,638 | 0,287 | 0,064 | 0,649 | 0,679 |
| 0,75 | 0,702 | 0,540 | 0,003 | 0,457 | 0,950 |
| 1,00 | 0,760 | 0,754 | 0,000 | 0,246 | 0,998 |

- **0,8 güçle ölçülebilir en küçük etki.** Yalnız ana aralıkla δ = 0,58 σ_Δ (AUC 0,66). Tam H1 kuralıyla, yani
  plasebo eşleşik fark şartıyla, δ = 1,07 σ_Δ (AUC 0,77).
- **Yüzde karşılığı.** σ_Δ = 0,05 / 0,1 / 0,2 % için ana aralıkta 0,029 / 0,058 / 0,116 %, tam H1'de 0,053 / 0,107 /
  0,213 %.
- **Kosismik düşüşle kıyas.** Napa'nın kosismik düşüşü ≈ %0,08'dir. σ_Δ ≈ %0,1 ise tam H1 kuralı ancak bir M6
  kosismik düşüşü büyüklüğündeki bir öncülü 0,8 olasılıkla görür.
- **K'ye göre** (aygıt kuralından ya da doluluktan sonra küçülürse; aynı tablonun δ = 0 / 0,5 / 0,75 satırları):

  | K / K_p | H0 (δ 0) | H1 (δ 0,5) | H1 (δ 0,75) |
  |---|---|---|---|
  | 32 / 16 | 0,575 | 0,251 | 0,498 |
  | 25 / 13 | 0,377 | 0,206 | 0,425 |
  | 20 / 10 | 0,192 | 0,155 | 0,333 |

  Kapıda (K 20), gerçek etki sıfırken bile H0 alma olasılığı 0,19'dur. "Ayırt edilemez" bu tasarımda en olası tek
  sonuçtur ve bu önceden kabul edilir.

**4.5 Pozitif kontrol için olay sonrası penceresinin seçimi.** İki seçenek vardı: (a) kümelerin kendi ana şokları,
olay sonrası penceresinde; (b) ayrı bir olay kümesi. (a) seçildi, dört gerekçeyle:
1. **Aynı zincir sınanır.** PK, hükmü üreten aynı istasyon, kanal, başvuru ve kod zinciriyle yapılır. Ayrı bir küme
   başka istasyonları ve başka gürültüyü sınar.
2. **Ek seçim serbestliği yok.** Ayrı kümenin seçimi bir serbestlik derecesi daha getirirdi (hangi olaylar, hangi
   uzaklıklar).
3. **Hacim küçük.** Ek hacim 60 istasyon × 30 gündür, A biçiminin ≈ %0,4'ü.
4. **Sızıntı riski düşük.** Olay sonrası veri, hüküm ölçüsünün hiçbir girdisinde kullanılmaz. Ölçünün kendisi 6.
   adımda yazılıp sha256'sı kayda geçtikten sonra okunur. Böylece olay sonrası görüntü, işleme seçeneklerine
   (bant, eşik, maske) geri besleme yapamaz.

Bedeli: PK'nin geçmesi hüküm verisini görmüş bir kodla sınanır. Ama kod 6. adımdan sonra değiştirilemez (§5.5).
Bu yüzden bedel yalnız bilgidir.

PK eşiğinde genlik şartı yok, yalnız yön sınaması var. Bunun nedeni literatür genliklerinin istasyondan istasyona
saçılması (Richter 2014) ve 50 km'den uzakta sıfıra inebilmesidir (Boschelli 2021). Kökün andığı %0,2–1,5'lik
kosismik düşüşler M 6,6–9 olaylarının yakın alanından gelir. Bu örneklemdeki M 6,0–6,4 ve ≈ 50 km'lik istasyonlar
için doğru ölçek Napa'nın ≈ %0,08'idir. Eşik bu yüzden %0,2'ye dayanmaz. Geçme olasılığı §6.1'de E3 ile yapay veride
hesaplandı.

## 5. Koşu düzeni, hacim, süre ve maliyet

**5.1 Aşamalar.**
- **1a. Kontrol adaylarının ay yoklaması.** TR-5 Ek 1 yöntemiyle yapılır: ayın 15'inde 1 dakikalık istek, yalnız HTTP
  kodu ve bayt sayısı kaydedilir, içerik okunmaz. Kapsam: 10 kontrol ve 10 plasebo kontrol adayının 1264
  istasyon-penceresi, ≈ 45 500 istek. Ay doluluğu süzgecini (`dolu_ana`) geçen adaylar SHA sırasıyla 1b'ye gider.
- **1b. İndirme ve gün doluluğu.** İndirme §3.1 biçimiyle yapılır. Kapsam: olay ve plasebo istasyonları ile 1a'dan
  geçen ilk 5 kontrol ve ilk 5 plasebo kontrolü.
  - **Gün dolu:** 4 saatin ≥ 2'si üç bileşende kabul edilmiş (§3.2 madde 1).
  - **İstasyon-penceresi dolu:** A, B ve C dilimlerinin her birinde dolu gün oranı ≥ 0,60, üç bileşen var ve aygıt
    kuralı (§2.5) geçiyor.
  - Dolu olmayan kontrolün yerine 1a'dan geçen sıradaki aday gelir. 10 aday tükenirse yeni aday eklenmez.
  - Bu aşamada ÇİF hesaplanabilir, ama ε ve Δ hesaplanmaz.
- **Kapı (§4.2 adım 0).** K ve K_p sayılır ve kayda geçer. Geçmezse koşu "güç yok" ile durur.
- **2. aşama.** §4.2 adım 1–7.
- **3. aşama.** Olay sonrası indirme ve §4.2 adım 8–9.

**5.2 Hacim.** Hesap `tr5b_liste.py` → `tr5b_ozet.json` → `hacim` ile yapıldı. İstasyon başına pencerelerin gün
birleşimi alındı. Varsayımlar: 1,3 bayt/örnek (TR-5 §5.1 ölçümü); en düşük ≥ 10 sps kanal; 3 bileşen. 4 saat/gün
sütunu bağlayıcıdır.

| Biçim | İstasyon | İstasyon-gün | 4 saat/gün, 3 bileşen | Tam gün, 3 bileşen | KOERI payı (4 sa) |
|---|---|---|---|---|---|
| **A (bağlayıcı):** olay + plasebo, kontrol 5, plasebo kontrolü 5 | 281 | 504 937 | **1,66 TB** | 9,97 TB | 0,004 TB |
| A0: plasebo kontrolsüz | 250 | 397 184 | 1,31 TB | 7,85 TB | 0,004 TB |
| A3: kontrol 3, plasebo kontrolü 3 | 246 | 392 655 | 1,29 TB | 7,71 TB | 0,004 TB |
| B (tam): kontrol 10, plasebo kontrolü 10 | 337 | 672 441 | 2,20 TB | 13,2 TB | 0,004 TB |

- **A'nın bileşenleri** (tekrarsız): olay + PK 0,17 TB; plasebo 0,08 TB; kontrol 1–5 1,08 TB; plasebo kontrol 1–5
  0,71 TB. Yedek kontrollerin hepsi (6–10) indirilirse toplam B'ye, yani 2,20 TB'ye çıkar. A'nın gerçekçi üst sınırı
  budur.
- **Merkez payı (A):** EarthScope 0,94 TB, NOA 0,17, GEONET 0,13, GEOFON 0,13, INGV 0,10, öteki merkezler ≤ 0,06.
- **Önceki tahminle kıyas.** TR-5 Ek 1'in "≈ 2 TB, ≈ 6 hafta" tahmininde KOERI payı 0,145 TB idi. Kontrollerden
  KOERI'nin çıkarılması bu payı 0,004 TB'ye indirdi; altı haftalık darboğaz bu kalemdi.

Hükmü bozmadan hacmi küçülten seçenekler:

| Seçenek | Hacim etkisi | Hükme etkisi | Karar |
|---|---|---|---|
| Kontrol 10 → 5 (5 yedek) | 2,20 → 1,66 TB (−%25) | r'nin sd'si 0,316 → 0,342; en küçük δ ≈ %8 büyür | **Bağlayıcı** |
| Kontrol 3 | 1,29 TB | sd 0,373; N1 için 2 kontrol kalır | Reddedildi |
| Plasebo kontrolsüz (A0) | 1,31 TB | Plasebo yalnız olay kontrolleriyle kıyaslanır, epok eşleşmez; d şartı zayıflar | Reddedildi |
| 4 saat/gün (tam gün yerine) | ÷ 6 | Ölçüm gürültüsü ≈ × 2,4 (§3.1) | **Bağlayıcı** |
| KOERI ve 6G kontrollerden çıkar | KOERI süresi ≈ 39 gün → ≈ 1 gün | Kontrol havuzunda Anadolu merkezleri azalır; kontroller zaten bölge eşlemeli değil | **Bağlayıcı** |
| Yalnız hüküm bandının ÇİF'lerini saklamak | İndirmeyi değiştirmez; disk bant başına ≈ 15 GB (3 çift × 2401 örnek × 4 bayt × 505 bin gün), iki bantta ≈ 29 GB | Yeniden çözümleme yeniden indirme ister | **Bağlayıcı** (0,5–2 Hz ve bilgi bandı 2–4 Hz saklanır; ham miniSEED işlendikten sonra silinir, istek ve sha256 günlüğü kalır) |
| Yalnız Z | ÷ 3 | SC yöntemi bozulur (TR-5 Ek 1) | Reddedildi |

**5.3 Süre.** Ölçülen hızlar: EarthScope tek akış ≈ 2,4 MB/s, KOERI tek akış ≈ 40 KB/s. İkisi de TR-5'te tek
denemeyle ölçüldü. Öteki merkezlerin hızı ölçülmedi. Ay yoklamasındaki istek gecikmeleri (0,4–1,4 sn) bant
genişliği değildir.

| Kalem | A | B |
|---|---|---|
| 1a ay yoklaması (≈ 45 500 istek; merkez başına tek akış, 0,3–2 sn bekleme; kaba) | ≈ 5–10 saat | aynı |
| EarthScope indirme (tek akış 2,4 MB/s) | 0,94 TB → ≈ 4,5 gün | 1,23 TB → ≈ 5,9 gün |
| En büyük öteki merkez (NOA), 1 MB/s / 0,4 MB/s varsayımıyla (doğrulanamadı) | 0,17 TB → 2 / 5 gün | 0,29 TB → 3,4 / 8,5 gün |
| KOERI (40 KB/s) | 0,004 TB → ≈ 1,2 gün | aynı |
| İşlem (≈ 0,3 CPU-sn / istasyon-gün, 4 saat; TR-5 §5.2 kaba tahmini, doğrulanamadı) | ≈ 42 CPU-saat; 8 çekirdekte ≈ 6 saat, indirmeyle örtüşür | ≈ 56 CPU-saat |
| Yedek kontrollerin ek indirmesi | ≤ +0,54 TB, ≈ +2,5 gün (EarthScope) | – |
| **Toplam duvar saati** | **≈ 1–2 hafta** | **≈ 1,5–2,5 hafta** |

Merkezler paralel indirilir: merkez başına tek akış, TR-5 Ek 1 nezaket kuralları. EarthScope'ta ikinci bir akış ancak
1b'nin ilk gününde ölçülen hıza göre açılır; bu, hükmü etkilemeyen bir işletim kararıdır.

**5.4 Makine ve maliyet.** Koşu bulut oturumuna sığmaz. Bu oturumun iş sınırı 2 saat, boş diski 16 GB'dir; koşu
1–2 hafta açık kalacak bir makine ister.

Örnek makine: Hetzner 8 vCPU / 16 GB sınıfı, ayda kabaca 30–60 € (2024–2025 liste fiyatlarından; **doğrulanamadı**).
Saatlik faturalanır, gelen trafik ücretsizdir. Disk: ÇİF deposu ≈ 29 GB (iki bant), ayrıca geçici ham veri. 80 GB
yeter.

| Biçim | Süre | € (30–60 €/ay ile) |
|---|---|---|
| A (bağlayıcı) | ≈ 1–2 hafta | **≈ 7–28 €** |
| B | ≈ 1,5–2,5 hafta | ≈ 11–35 € |

İki biçim de beklenen durumda 50 €'nun altındadır. Fiyat doğrulanmadığı için makine kiralama ve harcama **proje
sahibinin kararıdır.** **Koşu, sunucu onayı gelince başlar.** Onay gelmezse ön kayıt dondurulmuş ve koşulmamış olarak
kalır.

**5.5 Körlük ve tek koşu.**
- Kod yalnız yapay veriyle geliştirilir ve sınanır (`tr5b_yapay.py` başvurudur). Dosya biçimi için yapay miniSEED
  kullanılır; gerçek istasyon kullanılmaz.
- Gerçek dalga formu ancak kod incelemesinden sonra indirilir.
- Ön kayıt, liste, betikler ve koşu kodu commit + push edildikten sonra tek bir komut bütün zinciri koşar.
- Olay Δ'ları 6. adımdan önce hiçbir yerde hesaplanmaz, çizilmez, yazdırılmaz. 1b'de olay istasyonlarının yalnız
  doluluk ve enerji istatistikleri yazılır.
- Olay sonrası veri 8. adımdan önce indirilmez.
- Koşu bir kez yapılır. Kod hatası 1–4. adımlarda bulunursa, olay Δ'ları görülmeden düzeltilir ve "koşu öncesi
  düzeltme" başlığıyla kayda geçer. 6. adımdan sonra bulunan her hata "koşu sonrası değişiklik" başlığıyla yazılır ve
  ikinci koşunun kör olmadığı belirtilir.
- İndirme başarısızlığı istasyon-pencere düzeyinde kayda geçer. 1b'de başarısız pay %5'i aşarsa, ε hesaplanmadan tek
  bir yeniden deneme turu yapılır.
- **Veri sınırı.** Olaylar T ≤ 2023-12-31. Bütün dalga formu istekleri ≤ 2025-12-31; en geç istek PK penceresinin
  sonu, 2023-03-08. 2026 hiçbir amaçla sorgulanmaz.
- **Marmara ile temas.** Marmara GNSS'e dokunulmaz. TR-4 kutusunda (40,0–41,6° K, 26,5–30,5° D) hiçbir liste
  istasyonu yok. TR-1'in daha geniş kutusunda tek bir istasyon var: HT.ALN, plasebo penceresi 2008–2011.

## 6. Yapay doğrulama ve güç

**6.1 Yapay veri (`tr5b_yapay.py`, tohum 20261112).**

Kurulum: Green fonksiyonu 0,5–2 Hz bant sınırlı gürültü × exp(−|τ|/20 sn) olarak üretildi. Günlük ÇİF'ler gerçek
dv/v ile gerildi, üstüne bağımsız bant sınırlı gürültü eklendi. Mevsimsel bileşen %0,05 genlikli, evresi rastgele.
Günlerin %15'i rastgele eksik ve ayrıca bir 30 günlük boşluk var. Zincir §3.4–3.5'in aynısıdır. SNR, 10 günlük
yığının başvuruyla beklenen CC'siyle adlandırıldı.

| Düzey | σ_ölçüm (Δ, %) | Ort. Δ (%) | Ek. oranı medyan [%5; %95] | 35 sahte olay medyanı [%1; %99] | P(aralık dışı) | Geçersiz ε günü |
|---|---|---|---|---|---|---|
| CC₁₀ ≈ 0,5 | 0,018 | +0,0004 | 0,927 [0,905; 0,959] | [0,921; 0,938] | 0 | %13,2 |
| CC₁₀ ≈ 0,7 | 0,011 | +0,0021 | 0,967 [0,949; 0,984] | [0,963; 0,974] | 0 | %3,4 |
| CC₁₀ ≈ 0,9 | 0,005 | −0,0007 | 0,982 [0,971; 0,992] | [0,979; 0,986] | 0 | %3,4 |

Okuma:
- **Yanlılık önemsiz.** Mevsimsel döngü ay eşlemesiyle düşüyor. Ortalama Δ en çok %0,002, yani σ_ölçüm'ün en çok
  %20'si. En büyüğü (CC₁₀ ≈ 0,7) 2,2 standart hata; üç düzeyden biri. Ana ölçü kontrollere göre sıra olduğu için
  ortak küçük bir yanlılık r'yi değiştirmez.
- **Germe kestiricisi küçülme veriyor.** Eklenen −%0,1'in %2–7'si kayboluyor ve kayıp SNR düştükçe büyüyor. Kodun
  yanlış olduğunu göstermez.
- **[0,80; 1,20] eşiği doğru kodun rahatça geçeceği aralıkta.** En düşük SNR'de bile %1 niceliği 0,92'dir. Eşik
  birim, işaret ya da pencere hatasını (oran ≈ 0, ≈ −1, ≈ 0,5) yakalar.
- **σ_ölçüm küçük.** Yapay σ_ölçüm (0,005–0,018 %) gerçek σ_Δ'nın alt sınırıdır: hidroloji, ısıl etki ve gerçek
  gürültü kaynakları yok, 4 saat/gün etkisi yok.

**E3, pozitif kontrolün geçme olasılığı.** Kurulum: 16 küme, küme başına bir istasyon. Kümenin genliği A'nın
0,5–1,5 katı arasında tekdüze. Toparlanma 50 günde yarıya iniyor. Mevsimsel bileşen var. Her A için 200 yapay
istasyonluk havuzdan 2000 çekiliş yapıldı. Sonuçta ≈ ±0,03'lük Monte Carlo saçılımı var.

| A (küme genliği A'nın 0,5–1,5 katı) | CC₁₀ ≈ 0,5: P(geçer) | ölçülen medyan δ_ko | CC₁₀ ≈ 0,7: P(geçer) | ölçülen medyan δ_ko |
|---|---|---|---|---|
| %0,02 | 0,12 | −%0,014 | 0,11 | −%0,012 |
| %0,05 | 0,63 | −%0,043 | 0,66 | −%0,027 |
| **%0,08 (Napa)** | **0,90** | −%0,060 | **0,99** | −%0,050 |
| %0,15 | 1,00 | −%0,096 | 1,00 | −%0,093 |

δ_ko'nun istasyonlar arası sd'si %0,05–0,08'dir. Bu saçılımı ölçüm gürültüsü değil, büyük ölçüde iki pencere
arasındaki mevsimsel fark üretir (yapay mevsim genliği %0,05). Bir değişke de sınandı: aynı takvim pencerelerinin bir
yıl önceki farkı çıkarılarak mevsimden arındırılmış δ_ko. Bu değişke daha iyi değil (A = %0,08'de P 0,66 / 0,97;
gürültü iki katına çıkıyor). Bu yüzden ana PK tanımı arındırılmamış farktır (§4.2 adım 8).

Okuma: Napa düzeyindeki bir düşüş (%0,08) PK kümelerinde ortalama olarak varsa, PK ≈ 0,9–0,99 olasılıkla geçer.
Ortalama düşüş %0,05 civarındaysa olasılık ≈ 0,65'e iner. Ortalama düşüş %0,02 ise PK büyük olasılıkla geçmez ve
hüküm "güç yok" olur. Gerçek mevsim genliği yapaydakinden büyükse (Hillers 2015: 0,5–2 Hz'de tepeden tepeye ≈ %0,2,
yani genlik ≈ %0,1) geçme olasılığı düşer. Bu, §9 madde 3'teki zayıf noktadır.

**6.2 Güç (`tr5b_guc.py`, tohum 20261112).** Hüküm olasılıkları §4.4'tedir. Ek sonuçlar:
- **r'nin sd'si.** n_c = 5 için kuramsal √((n+2)/(12n)) = 0,342. Benzetimde küme ortalamasının SE'si K = 35'te
  0,057.
- **N1.** H0 altında yanlış "geçersiz" olasılığı 0,052.
- **Duyarlılık (4. adım).** P(r̄_sahte ≤ 0,25), gerçek σ_Δ'ya göre:

  | σ_Δ | 0,05 % | 0,075 % | 0,1 % | 0,15 % | 0,2 % |
  |---|---|---|---|---|---|
  | P | 1,00 | 0,96 | 0,60 | 0,09 | 0,02 |
  | ort. r̄_sahte | 0,08 | 0,17 | 0,24 | 0,32 | 0,36 |

  Gerçek σ_Δ ≳ %0,1 ise sınav büyük olasılıkla 4. adımda "güç yok" ile durur. σ_Δ ölçülmedi; tek bilinen sayılar
  TR-5 §6.2'deki varsayım aralığıdır (0,05–0,2 %). Bu adım bilerek sert tutuldu: bir M6'nın kosismik düşüşü
  büyüklüğündeki (%0,1) bir kaymayı AUC 0,75 ile göremeyen bir ölçü öncül sınavı için kördür.

## 7. Bilinen karıştırıcılar ve önlemler

| Karıştırıcı | Önlem | Kalan risk |
|---|---|---|
| Mevsimsellik (ısıl, yağış) | Ay eşlemeli Δ (§3.5); aynı epokta kontroller | Yıldan yıla değişen mevsim genliği |
| Çok yıllı hidroloji (kuraklık, yeniden beslenme) | Aynı epokta kontroller (küresel iklim yılı ortaktır, yerel kuraklık değildir); aynı yerde plasebo ve eşleşik d şartı; zaman kaydırma bilgi satırı | **En büyük risk.** Son yılı kurak geçen bir yerde Δ > 0 çıkar. Kontrol bunu eşlemez, plasebo yalnız yere özgü çok yıllı yanlılığı yakalar. Yağış modeli bilerek bilgi satırına bile konmadı (serbestlik derecesi; Seher ve Main 2004 dersi) |
| Yakın M ≥ 6 depremlerin düşüş ve toparlanması | Ş1–Ş3 temiz pencere, [T − 5 yıl, T) (olay ve plasebo için dış merkeze, kontrol için merkeze göre) | Ş1 merkeze göre uygulanır; 100 km'deki bir istasyona 150 km'den uzak, ama istasyona yakın bir M6 kalabilir. Maske yalnız M 5–6 için 60 gün; M ≥ 6'nın on yıllık kuyruğu (Clements ve Denolle 2023) 5 yıldan önceki olaylarda sürebilir |
| Yakın M ≥ 5 öncüler ve öteki olaylar | §2.6 maskesi (50 km, 60 gün) | Kuyruk; 50 km'den uzak büyük M5'ler |
| İstasyon ve aygıt değişimi | §2.5 kuralı; pencere içinde kanal ve konum kodu sabit | Üstveriye işlenmemiş değişimler (saat, yerleşim, kazı) |
| Volkanik yerler | Hawaii ana hükümden dışarıda (§2.7); Akutan ve Jan Mayen bilgi satırı | Volkan listesi yoklanmadı |
| Gürültü kaynağı değişimi (mevsimsel kaynak yönü) | Beyazlatma, gece saatleri, koda penceresi | Kaynak değişimi germe ölçüsünde sahte dv/v üretebilir (Daskalakis 2016, özetten nitel) |
| Ölçek farkı (olay yerleri daha gürültülü) | İşaretli sıra ölçüsü (§4.1) | Yok: işaretli ölçü H0'da ölçek farkına dayanıklı (0,053) |
| Kontrollerin tekrarı | Kota 3 küme | Ortak kontroller t aralığını biraz daraltır; "bir merkezi dışarıda bırak" bilgi satırı |

## 8. Bilgi satırları (hükmü değiştirmez)

1. Hawaii'nin iki olayı dahil r̄.
2. Akutan ve Jan Mayen hariç r̄.
3. |Δ| sıra ölçüsü (tek yanlı, büyük |Δ|).
4. Eğilimden arındırılmış Δ: A∪B'ye doğrusal + yıllık sinüs uydurulur, C'ye uzatılır.
5. 2–4 Hz bant.
6. Olay ağırlıklı r̄.
7. Yalnız M ≥ 6,5.
8. Yalnız doğrultu atımlı (USGS MT, |rake| ≤ 30° ya da ≥ 150°).
9. Yalnız en yakın istasyonu ≤ 50 km olan olaylar.
10. Δ / σ_i: istasyonun A ve B dilimleri arasındaki ay eşlemeli farkın mutlak değeriyle ölçeklenmiş Δ.
11. Bir kontrol merkezini dışarıda bırakma: en küçük ve en büyük r̄.
12. Olay başına tablo: Δ_e, r, n_c, istasyonlar, maske günleri, geçersiz gün oranı, CC medyanı.
13. PK'de küme başına δ_ko ve medyan.
14. 1a ve 1b'de elenen istasyon ve kontrol sayıları, nedenleriyle.
15. Gerçek σ_Δ (kontrollerin Δ dağılımı): TR-4'ün güç çevirisi için.

## 9. Zayıf noktalar (incelemecinin bakması gerekenler)

1. **Çatallanma (§0).** Biçim kapıdan geçtiği için seçildi. Sonuç görülmedi, ama "önceden konmuş" değil.
2. **4. adımın sertliği.** Gerçek σ_Δ ≥ %0,1 ise, doğru kodla bile hüküm büyük olasılıkla "güç yok" olur. Bunun
   bilerek seçildiği yazılı. İncelemeci bu eşiğin bu tasarımda adil olup olmadığına bakmalı. Seçenekler: −%0,2 ile
   sınamak ya da adımı bilgi satırına indirmek.
3. **PK'nin geçme olasılığı.** Gerçek kosismik genliğe ve istasyon uzaklığına bağlıdır. PK kümelerinin istasyonları
   6–89 km arasında. Kahramanmaraş kümesi 55–89 km'de ve M7,8. E3 yalnız yapay gürültüyle hesaplandı. Gerçek
   artçılı günlerde enerji reddi, olay sonrası saatlerin çoğunu atabilir.
4. **Plasebo şartı gücü yarıya indiriyor.** δ = 0,75 σ_Δ'da ana aralığın gücü 0,95, tam H1'in gücü 0,54. Bu bilerek
   kabul edildi (TR-1 inceleme 2, bulgu 3), ama H1 ancak büyük etkide çıkabilir.
5. **Hidroloji.** Kontrol, yerel çok yıllı kuraklığı eşlemez. H1 çıkarsa ilk rakip açıklama budur. Plasebo yalnız yere
   özgü bir yanlılığı yakalar, zamana özgü olanı yakalamaz.
6. **Doğrulanamayan işleme sayıları.** 10 günlük yığın, CC ≥ 0,40, koda 10–40 sn, 4 saat/gün, enerji reddi 3 kat:
   hiçbiri özetten doğrulanamadı. Yapay veri yalnız iç tutarlılığı gösterir.
7. **Üç bileşen doğrulanmadı.** Üstveri ve doluluk yoklaması yalnız Z kanalına bakıyor. Yalnız Z'si olan istasyonlar
   1b'de düşer ve K yeniden küçülür. K'nin 37'den 35'e (volkanik), 32'ye (aygıt) ve daha aşağıya inme riski
   gerçektir.
8. **Kontrol doluluğu yoklanmadı.** TR-5 Ek 1'de olay istasyonlarının yalnız ≈ %40'ı ay doluluğu süzgecini geçti.
   Kontrollerde de böyleyse 10 aday bazı olaylar için yetmez. Bu durumda ≥ 4 kontrol şartı olay düşürür.
9. **Kontrol bölge eşlemesi yok.** Kontroller aynı epoktadır ama başka iklim ve jeolojidedir. İşaretli ölçü ölçek
   farkına dayanıklıdır, ortalama kaymaya (örneğin küresel bir ısınma eğilimine) olay ve kontrol birlikte maruz kalır.
10. **Olayların çoğunda tek istasyon.** 45 olayın 34'ünün (%76) tek istasyonu var. Tek istasyonun yerel olayları (yapı, bina,
    su kuyusu) ölçüyü belirler.
11. **Volkanik kural adla tanımlı.** Holosen volkan listesi yoklanmadı.
12. **Wells–Coppersmith katsayıları bellekten.** PK kümelerinin seçiminde kullanıldı, liste sabit olduğu için sonucu
    değiştirmez.
13. **Hız ve fiyat doğrulanmadı.** Süre tahmininde yalnız EarthScope ve KOERI hızı ölçüldü (tek denemeyle). Hetzner
    fiyatı doğrulanmadı.

## 10. Marmara'ya anlam

Bu sınav Marmara verisi kullanmaz.
- **H1** (yer yanlılığı dışlanmış, PK geçmiş): TR-4'ü anlamlı kılar. Marmara KO ağıyla dv/v izlemesi, TR-4'ün ölçeceği
  gürültü tabanıyla birlikte, ayrı ve ileriye dönük bir ön kayıtla önerilir. O ön kayıt, TR-5b'nin işaretini ve
  büyüklüğünü önceden sabit alır. Bu bir alarm ya da olasılık değildir.
- **H0:** Yıl ölçekli pasif dv/v düzey farkını, bu ölçü ve bu örneklem için öncül olarak kapatır. TR-4 o zaman yalnız
  bir ölçüm sınırı cümlesi üretir ("Marmara'da X %'den küçük değişim görülemez"); alarm adayı olarak önerilmez.
- **Ayırt edilemez ya da güç yok:** Marmara'ya hiçbir şey taşınmaz.

**İstanbul için mutlak olasılık bu belgenin hiçbir yerinde yazılmaz ve hiçbir sonuçtan türetilmez.**

## 11. Yeniden açma şartı

"Güç yok" ya da "ayırt edilemez" ile kapanırsa yeniden açma ancak yeni bir ön kayıtla ve şu yollardan biriyle olur:
- (a) K'yi en az iki katına çıkaran yeni bir açık arşiv; örneğin Japonya Hi-net ya da F-net'e erişim;
- (b) istasyon çiftleriyle CC ve 0,2–0,5 Hz bandı. Bunun için ≥ 2 yer şartı gerekir; TR-5'te bu şart K 8–11 verdi;
- (c) TR-4'ün ölçtüğü σ_Δ'nın, 4. adımı geçecek kadar küçük çıkması.

## 12. Defterle örtüşme

- **TR-5 (ata):** Ana tasarım güç yok (K 8–15). TR-5b, Ek 1'deki tek geçen biçimdir. TR-5'in defter kaydı
  "koşuyor" durumunda; ana tasarımın "güç yok (sayım)" ile kapatılması kök oturumun kararıdır.
- **TR-4:** σ_Δ'yı Marmara'da ölçer. TR-5b'nin 4. adımı ve güç çevirisi bu sayıya bağlıdır. TR-5b kontrollerinde
  KO kullanılmadığı için TR-4 ile indirme çakışması yoktur.
- **TR-1 (güç yok):** İskelet ondandır: kontrol merkezleri, SHA sırası, plasebo, eşleşik d, kota. İki inceleme dersi
  burada uygulandı: kontrol (b) şartı simetrik, kota var.
- **TR-11, E1:** Pozitif kontrol eşiği yapay veriyle önceden sınandı (§6.1). Eşik [0,80; 1,20] doğru kodun %1
  niceliğinin (0,92) dışında değil.
- **FA-6 (elendi):** Serbestlik derecesi riski. Tek ana bant (0,5–2 Hz), tek ana ölçü (ay eşlemeli düzey farkı), tek
  sınama (işaretli r̄). Yağış ve ısı modelleri yok. Ötekiler bilgi satırı.
- **DD-5 (gelgit, güç yok):** dv/v'nin gerilme duyarlılığı yalnız sığ bir gelgit kalibrasyonuna dayanır (Hillers
  2014, ≈ 0,5 MPa⁻¹). Derinlikte geçerli olup olmadığı bilinmiyor. Bu yüzden Δ'nın gerilmeye çevirisi bu sınavda
  yapılmaz. Beklenen sonuç, literatürde doğrulanmış etki büyüklüğü olmadığı için H0 ya da ayırt edilemezdir.

## Ek: PK kümeleri ve komutlar

**PK kümeleri** (16, volkaniksiz; en yakın istasyon ≤ max(30 km, 2 L(M))):

ci38443183, nc72282711, nc73666231, us10006g7d, us10006n6r, us20009ly0, us2000bmhe, us6000jllz, us7000asvb,
us7000d18q, us7000gaqu, us7000irfb, usb000m8ch, usb000r2hc, usp000fuvt, usp000gvtu.

Bunların ikisi (us7000irfb kümesi ve usb000m8ch'nin HL.VLS istasyonu) aygıt önizlemesinde etkilenir.

**Plasebo eşleşik kümeleri** (18, volkaniksiz): ci38443183, nc72282711, us100031wx, us10004gy9, us10006n6r,
us10008mel, us2000272b, us20002m5s, us20005hzn, us20009ly0, us6000d3zh, us6000jllz, us7000gaqu, us7000imgl,
usb000r2hc, usc000m1w9, usp000gjgt, usp000gvtu.

**Komutlar** (girdiler depo dışında, karalama dizininde):
```
python3 -I -B kayit/turetme/tr5/tr5b_liste.py <tr5/ham> <ngl> <tr2/ham> <tr5b_kat>   # ≈ 14 sn
python3 -I -B kayit/turetme/tr5/tr5b_yapay.py                                     # ≈ 10 dk
python3 -I -B kayit/turetme/tr5/tr5b_guc.py                                       # ≈ 6 sn
```
