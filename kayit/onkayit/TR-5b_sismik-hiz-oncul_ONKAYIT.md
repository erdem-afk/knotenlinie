# TR-5b ön kayıt: M ≥ 6,0 sığ depremlerden önceki son yılda ortam gürültüsü dv/v, küresel olay–kontrol sınavı

Sürüm 2, 12 Kasım 2026. Durum: **TASLAK sürüm 2 (İNCELEME-1 düzeltmeleri işlendi), ikinci incelemeye hazır.**
Dondurulmadı. Hiçbir dalga formu indirilmedi, açılmadı ya da yoklanmadı; aşama 0 betiği yalnız ağsız (`kuru`) kipte
koşuldu. Kol: TR. Ata: TR-5 (`TR-5_TR-4_SAYIM.md`, Ek 1). Maliyet bu belgeye kadar 0 €. Sürüm 1 bu dizinde
`TR-5b_sismik-hiz-oncul_ONKAYIT_surum1.md` adıyla korunur (sha256 `2d7649a3…`, değişiklik listesinde tam).

**Kapı sayıları (üstveri, aşama 0'dan önce).** Volkaniksiz bağımsız küme **K = 31** (≥ 20), volkaniksiz eşleşik
plasebo kümesi **K_p = 16** (≥ 10). Aygıt kuralının Z önizlemesiyle 28 ve 15. İkisi de kapının üstünde; ama bunlar
üst sınırdır. Gerçek sayıyı aşama 0 verir ve kapı G0 (K₀ < 20 ya da K_p₀ < 10 ise "güç yok (aşama 0)") sunucu
kiralanmadan önce karar verir (§5.1).

**Koşu düzeni.** Aşama 0 (bulut oturumu, 0 €) → pilot P1 ve P2 (bulut oturumu, 0 €; sığmazsa sunucu) → ana indirme
1b, sıralı (önce olay ve plasebo istasyonları, ≈ 0,23 TB; olay tarafı kapıyı geçmezse kontroller indirilmez) → ölçü.
**Sunucu ancak aşama 0 ve pilot geçince ve proje sahibi onaylayınca kiralanır** (makine kiralama ve 50 €'yu aşan her
harcama proje sahibinin kararıdır, §5.4). Ön kayıt bu karardan bağımsız dondurulur.

Betikler ve bağlayıcı liste `kayit/turetme/tr5/` altındadır. Sürüm 1 dosyaları değiştirilmedi; sürüm 2 dosyaları
`_s2` ya da `2` ekiyle yenidir. Hepsi yalnız numpy ve standart kitaplıkla, `python3 -I -B` ile çalışır:
- `tr5b_liste_s2.py`: olay, istasyon, kontrol, plasebo ve pilot P2 listesini kurar; hacmi hesaplar (≈ 20 sn).
- `tr5b_asama0.py`: aşama 0'ın bütün kipleri (`kuru`, `ustveri`, `kur`, `yokla`, `say`) ve istasyon kotası (§5.1).
- `tr5b_guc2.py`: hüküm kuralı, 4. adım, pilot P1 kapısı ve geçme olasılıkları (§4.4, §6.2; ≈ 1 dk).
- `tr5b_yapay2.py`: Ö9 dondurulmuş yapay ÇİF'ler (`donder`) ve sürüm 2 pozitif kontrolünün yapay sınaması (`e3`).
- Başvuru zinciri sürüm 1'deki `tr5b_yapay.py`'dir (değişmedi).

Bu metindeki bütün sayılar bu betiklerin çıktısıdır. Literatür sayıları OpenAlex özetlerinden alındı. Özetten
doğrulanamayan her sayı "doğrulanamadı" diye işaretlidir.

## 0. Kimlik, öncelik sırası ve tasarım değişikliğinin kaydı

**Öncelik sırası.** Bu belgenin sürüm 2'si bağlayıcıdır. Bağlayıcı liste (`tr5b_liste_s2.json`, §2.8) bu belgenin
parçasıdır; metinle liste çelişirse liste geçerlidir. Bu belgede karşılığı olmayan bir noktada `TR-5b_INCELEME-1.md`'nin
düzeltme metinleri geçerlidir. Üçüncü sırada `TR-5_TR-4_SAYIM.md` gelir. Sürüm 1 yalnız kayıttır, bağlamaz.

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
"sayımdan önce konmuş" sayılmaz. Hedef artık "büyük deprem" değildir: volkaniksiz örneklemin %72'si (28/39 olay)
M 6,0–6,4'tür.

TR-5b'de Ek 1'in 16 satırından başka hiçbir biçim koşulmaz ya da raporlanmaz. Ana tasarıma en yakın alt küme bilgi
satırı olarak her durumda raporlanır ve hüküm vermez: "M ≥ 6,5 ve ≥ 2 dolu yerli olaylar" (§8 satır 17). Satıra küme
sayısı ve r̄ yazılır.

Sürüm 1 ve 2'de şu kararlar verildi. Hepsi dv/v verisi görülmeden alındı ve hepsinin K'ye etkisi yazılıdır:
- Volkanik kural Smithsonian GVP Holosen listesine bağlandı; olaylara ve kontrollere simetrik uygulanır (§2.7).
  6 olay (6 küme) ana hükümden çıkar: K 37 → **31**. Eşleşik plasebo 20 → 16 (biri Ö5 kesişim kuralından).
- Kontrol: 5 bağlayıcı, aday listesi 10 (§2.3). K değişmedi.
- Kota istasyon düzeyinde, kullanılan kontrollere göre, aşama 0'da (§2.3). Listede K değişmedi (hepsi dolu
  önizlemesinde 31 kümenin hepsi ≥ 4 kontrol alıyor).
- KOERI ve 6G istasyonları kontrollerden ve pilot P2'den çıkarıldı (§2.3). K değişmedi.
- Kontrol merkezleri arası en az uzaklık 150 km → 200 km; aynı olayın adayları ortak istasyon içermez (§2.3).
- Plasebo istasyonları olay istasyonlarıyla kesişir (§2.4). Eşleşik plasebo 17 → 16 (usb000r2hc düşer).
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
- Ana bant 0,5–2 Hz'dir ve tek istasyon bileşenler arası çapraz ilişki (SC) kullanılır. Ölçü, istasyonun
  çevresindeki sığ ortamı örnekler. Bu, istasyonun kabaca birkaç km ile birkaç on km yarıçapı ve üst birkaç km'sidir
  (yarıçap ve derinlik doğrulanamadı; Obermann 2016, 10.1093/gji/ggw264, özetten nitel). Olay istasyonları dış
  merkeze ortanca 50 km uzaktadır (volkaniksiz 51 istasyon-penceresi: medyan 49,5 km, çeyrekler 25,1 ve 69,8 km; en
  yakın istasyonun medyanı 50,2 km). H0, "dış merkezden ortanca 50 km uzaktaki sığ ortamda yıl ölçekli düzey değişimi
  yok" demektir. Fay bölgesindeki ya da derindeki bir hazırlık sürecini kapatmaz. Bilgi satırı 9 (≤ 50 km) bu yüzden
  H0 metninde K'siyle birlikte anılır.
- Ana hüküm örneklemi 31 kümedir (39 volkaniksiz olay). Bölge dağılımı (küme): İtalya-Balkan-Ege 7, Kaliforniya 3,
  Meksika-Orta Amerika-Karayip 3, Alaska-Aleut 2, Anadolu 2, Çin-Himalaya 2, Japonya, Yeni Zelanda, And,
  Endonezya-Filipinler ve PNG-Solomon birer, öteki 7. Örneklem ağırlıkla kıtasal ve sınır-dönüşüm ortamındadır.
  Mekanizma (39 olay): doğrultu atımlı 15, öteki 15, bilinmeyen 9. Japonya'dan yalnız Kumamoto öncüleri girer
  (tek istasyon, JP.JNU). Sonuç dalma-batma kuşaklarına ve volkanik ortamlara genellenmez.
- Olay başına istasyon (volkaniksiz): 1 istasyon 30 olay (%77), 2 istasyon 6, 3 istasyon 3.

## 2. Veri ve bağlayıcı liste

**2.1 Olaylar.** ComCat, `type = earthquake`, M ≥ 6,0, derinlik ≤ 30 km, 2000-01-01 ile 2023-12-31 arası (TR-2
`m6_havuz.csv`, sha256 `969c5c54…`). T, olay günüdür (UTC tarih; istasyon-gün tanımı §3.1). Temiz pencere
şartları, olayın kendisi dışında, [T − 5 yıl, T) aralığında dış merkeze göre uygulanır (5 yıl = 3 yıl taban + 2 yıl
iyileşme payı):
- Ş1: 150 km içinde M ≥ 6,0, derinlik ≤ 40 km olay yok;
- Ş2: 500 km içinde M ≥ 7,0, derinlik ≤ 70 km olay yok;
- Ş3: 1000 km içinde M ≥ 8,0, derinlik ≤ 70 km olay yok.

Aynı gün olan olaylar tek kümeye düşer. Kahramanmaraş'ın dört olayı tek kümedir; Kumamoto'nun iki öncüsü (14 Nisan
2016) da tek kümedir. Kural ve kod `sayim_ustveri.py` ile aynıdır (`TR-5_TR-4_SAYIM.md` §2.5).

**2.2 İstasyonlar.** BHZ ya da HHZ, ≥ 10 örnek/sn, açık. Kanal epokları 30 günden kısa boşluklar birleştirilerek
[T − 3 yıl, T − 1 g] aralığını kesintisiz kapsamalıdır. R = 100 km. 1 km içindeki istasyonlar tek yer sayılır ve en
yakın en çok 3 yer alınır. Olay ve plasebo istasyonlarına ayrıca TR-5 Ek 1'in ay doluluğu süzgeci uygulanır
(`tr5_doluluk.csv`, `dolu_ana`: ayların ≥ %80'inde veri ve en uzun boşluk ≤ 3 ay). Sonuç: 45 olay, 37 bağımsız
küme (Ek 1 ile aynı; betik eşitliği denetler). Volkanik kuraldan (§2.7) sonra **39 olay, K = 31**.

**2.3 Kontroller (aynı epok, depremsiz yer).** Aday merkezler, 1976–2025 arası M ≥ 6,5 (derinlik ≤ 40 km) olayların
dış merkezleridir. Bunlar 25 km içinde tekilleştirilmiş 1161 merkezdir. Sıralama SHA-256(`{olay ComCat kimliği}|{merkez
ComCat kimliği}`) onaltılık değerine göre artandır. Şartlar:
- (a) merkez olaya ≥ 600 km uzak;
- (b) [T − 5 yıl, T + 2 yıl] aralığında merkez için Ş1–Ş3 sağlanıyor;
- (c) 100 km içinde ≥ 1 yer var (açık, [T − 3 yıl, T − 1 g] kesintisiz, KOERI ve 6G dışı);
- (d) hiçbir kontrol istasyonu olaya 600 km'den yakın değil;
- (e) seçilen adayların merkezleri birbirinden ≥ 200 km uzaktır ve aynı olayın adayları ortak istasyon içermez;
- (f) volkanik dışlama (§2.7): istasyonlarından biri bir Holosen volkanına ≤ 25 km olan merkez atlanır, yerine
  sıradaki gelir.

Her olay için SHA sırasında (a)–(f)'yi sağlayan ilk 10 merkez **aday** olarak listelenir (1–10). Koşuda aşama 0 ve
1b'den geçen, kotaya uyan ilk 5 aday kullanılır (§5.1).

**Kota (istasyon düzeyinde).** Bir kontrol **istasyonu**, aynı epok türünde (olay ya da plasebo) en çok 3
bağımsızlık kümesinin kontrolünde kullanılır. Kota, kontrolün koşuda kullanılıp kullanılmadığına göre işler:
koşuda kullanılan her aday (yedekler dahil) kotaya yazılır, kullanılmayan yazılmaz. Olaylar (T, kimlik) sırasıyla
işlenir. Her olay için aday sırasıyla, dolu olan ve dolu istasyonlarından hiçbiri başka 3 kümede kullanılmış olmayan
ilk 5 aday atanır; kotası dolmuş istasyonu içeren aday atlanır. Aşama 0, kotayı yedeklerle birlikte uygulayarak K₀'ı
sayar (kod: `tr5b_asama0.kota_ata`, liste betiği de aynı fonksiyonu çağırır). 1b'de bir kontrol gün doluluğunu
tutmazsa atama, (T, kimlik) sırasıyla baştan yeniden yapılır; yeni atanan aday indirilir; atama değişmeyene dek sürer.

**KOERI ve 6G dışlaması.** KOERI'de barınan istasyonlar ve 6G ağı kontrol olarak ve pilot P2'de kullanılmaz.
KOERI'nin tek akış hızı ≈ 40 KB/s ölçüldü; bu hızla kontroller koşuyu haftalarca uzatırdı (§5.3). 6G'ye atılan deneme
isteği 204 döndü. Olay istasyonu KO.DKL ve KO.BODT kalır.

Sonuç: 45 olayın hepsinde 10 aday, plasebolu 24 olayın hepsinde 10 plasebo kontrol adayı var. (f) kuralı 87 olay ve
62 plasebo aday merkezini atladı. Adaylar 228 tekil istasyon kullanıyor; statik sayımda bir istasyon 15 kümenin aday
listesinde, 80 istasyon 3'ten fazla kümede yer alıyor. Kota bu yüzden adaylara değil kullanılan kontrollere işler.
"Hepsi dolu" önizlemesinde (`tr5b_ozet_s2.json` → `kota_onizleme`) 31 kümenin her olayı ≥ 4 kontrol alır: K₀ ≤ 31,
K_p₀ ≤ 16. Hawaii ve İzlanda kontrol merkezi kalmadı.

**2.4 Plasebo (aynı yer, olaysız zaman).** Plasebo epoğu T′ = T − 1095 g, penceresi [T′ − 1095 g, T′ − 8 g]'dir.
Dış merkez [T − 8 yıl, T) aralığında Ş1–Ş3'e göre sakin olmalıdır, olayın kendisi hariç (`sayim_ustveri.plasebo_say`).
**Plasebo istasyonları yalnız olayın da istasyonu olan istasyonlardır (kesişim):** olay istasyonlarından [T − 2191 g,
T − 1 g] aralığını kesintisiz kapsayan ve bu aralıkta ay doluluğu süzgecini geçenler. Kesişim boşsa olay plasebodan
düşer. Plasebo kontrolleri T′ epoğunda §2.3'ün aynı kurallarıyla ve kotayla seçilir; SHA anahtarı
`{kimlik}|plasebo|{merkez}` biçimindedir.

Sonuç: plasebolu 24 olay, 19 küme; volkaniksiz eşleşik plasebo kümesi **K_p = 16**. Kesişim kuralıyla düşen tek olay
usb000r2hc'dir (olay HL.LIA ve HL.SMTH, sürüm 1'in plasebosu HT.ALN). 21 volkaniksiz plasebo olayının 17'sinde plasebo
istasyonları olayınkilerin aynısı, 4'ünde alt kümesidir.

**Eşleşik fark.** Küme başına d_k = ort(r_e) − ort(r_p). İki ortalama da kümenin **hem geçerli r_e'si hem geçerli
r_p'si olan** olayları üstündendir. d̄ ve tek yanlı %95 t sınırı df = K_p − 1 ile hesaplanır. K_p, 6. adımda (6a)
sayılan eşleşik volkaniksiz küme sayısıdır.

**2.5 Aygıt değişimi.** Bir istasyon-penceresi şu durumda geçersizdir: pencere içinde başlayan bir kanal epoğunda,
aynı konum ve kanal kodunun önceki epoğuna göre sensör tanımı ya da yönelim (azimut, eğim) değişmişse. Sensör tanımı
seri numarası (`S/N…`) atılarak karşılaştırılır. Örnekleme hızı ve ölçek değişimi sayılmaz, çünkü veri 20 sn⁻¹'e
indirgenir ve ÇİF'ler normalleştirilir. Kural aşama 0'da seçilen üç kanalın üstverisiyle uygulanır; olay, kontrol ve
plasebo için aynıdır.

**Olay istasyonlarında kuralın aralığı [T − 1095, T + 30]'dur.** Kuralı yalnız (T − 8, T + 30] aralığında bozan
istasyon PK'den (§4.2 adım 8) düşer, hüküm ölçüsünde kalır. Bilinen örnek: KO.BODT (us20009ynd, Bodrum-Kos M6,6;
sensör T + 7'de değişmiş). Listede `aygit_degisimi_PK` alanıdır.

Z üstverisiyle önizleme (`aygit_degisimi_Z`, bağlamaz):
- 6 olay istasyon-penceresi düşüyor (HL.VLS, ES.EALB, IV.CAMP, CM.PRV, IU.HNR × 2);
- 4 olay bütün istasyonlarını kaybediyor (us10004gy9, us1000hwaj, us7000irfb, us7000irfm);
- sonuç: **K 31 → 28**, K_p 16 → 15;
- yalnız PK'den düşen: KO.BODT;
- kontrol adaylarında 67 istasyon-penceresi etkileniyor.

**2.6 M ≥ 5 maskesi (yakın orta depremler).** ComCat'ten M ≥ 5,0, derinlik ≤ 70 km, 1990-01-01 ile 2025-12-31 arası
olaylar indirildi. Sorgu 12 Kasım 2026 03:33 UTC'de, `endtime=2026-01-01T00:00:00` ile dört parça hâlinde yapıldı:
49 971 olay; parçaların sha256'ları `tr5b_liste_s2.json` → `girdi_sha256` alanında. Dosyalar
`/mnt/project-files/turetme/tr5b-ham/tr5b_kat_2026-11-12.tar.gz` olarak arşivlendi (sha256 `1bdfec2c…`,
`kayit/turetme/tr5/tr5b_ham_sha256.txt`). Bir istasyonun 50 km içindeki her böyle olay için [t_q, t_q + 59 g]
günlerinin ÇİF'leri yığından, başvurudan ve ε'dan atılır. Bu kural olay, kontrol ve plasebo istasyonlarına aynen
uygulanır.

Olayın kendisi maskeye girmez. Ama olay penceresindeki **öncüler** (son yıl dahil) maskelenir. Maskenin bedeli:
volkaniksiz 51 olay istasyon-penceresinin 13'ünde maskeli gün var (ortalama 22,6 gün); ilk 5 kontrol adaylarının 370
istasyon-penceresinin 71'inde maskeli gün var. M ≥ 6 olaylar için Ş1–Ş3 temiz pencere kuralları geçerlidir. Kosismik
etkinin 60 günden uzun süren kuyruğu (Napa'da 50 günde ≈ %50 toparlanma; Taira 2015, özetten) maskeyle tam silinmez.
Kalan etki M 5–6 ve ≤ 50 km olaylar içindir ve olay ile kontrole simetriktir. Öncü etkinliğinin kalan kısmı bir rakip
açıklamadır (§7, bilgi satırı 16).

**2.7 Volkanik yerler (Ö3).** Kural: **bir istasyonu bir Holosen volkanına ≤ 25 km olan olay ana hükümden çıkar ve
bilgi satırı 1'e gider; böyle bir kontrol ya da plasebo kontrol merkezi atlanır, yerine sıradaki merkez gelir
(§2.3 (f)).** Uzaklık istasyon koordinatıyla volkan koordinatı arasındaki büyük daire uzaklığıdır.

Volkan listesi: Smithsonian Global Volcanism Program, *Volcanoes of the World* Holosen listesi. 12 Kasım 2026 04:33
UTC'de GVP'nin açık WFS servisinden (`webservices.volcano.si.edu/geoserver/GVP-VOTW/ows`, katman
`Smithsonian_VOTW_Holocene_Volcanoes`, `outputFormat=csv`) genel bir istemci adıyla, kişisel bilgi verilmeden
indirildi: 1214 volkan (kanıt sınıfı: gözlenmiş püskürme 551, tarihlenmiş 293, güvenilir kanıt 242, belirsiz 88,
huzursuzluk 40; hepsi kullanılır). Ham dosya `/mnt/project-files/turetme/tr5b-ham/gvp_holosen_votw_wfs_2026-11-12.csv`
(sha256 `4e394d4a9b6ddccc6fea88d2e66e4859f57d2743bb6ba1856a4e1ec2bee6c484`). Bağlayıcı olan, depodaki sıkıştırılmış
kopyasıdır: `kayit/turetme/tr5/tr5b_gvp_holosen.csv` (numara, ad, enlem, boylam, son püskürme, kanıt, ülke;
sha256 `be85234874a1a85a1610552f67348b3ea1ac29ff24417575cbe92f57f145f25d`). Ham dosyanın satır kimliği (FID) sunucu
oturumuna bağlı olabilir; yeniden indirmede ham sha256 değişebilir, bağlayıcı kopya değişmez.

Ana hükümden çıkan 6 olay (6 küme):

| Olay | T | M | Yer | İstasyon → volkan (km) |
|---|---|---|---|---|
| usp000br01 | 2003-02-19 | 6,6 | Akutan, Alaska | AV.AKT → Akutan 13,9 |
| hv6000471 | 2006-10-15 | 6,0 | Hawaii | IU.POHA → Mauna Kea 9,6; GE.MAUI → Haleakala 6,4 |
| usp000jr55 | 2012-08-30 | 6,8 | Jan Mayen | NO.JMIC → Jan Mayen 16,5 |
| usp000jtqw | 2012-10-08 | 6,1 | Banda Denizi | GE.BNDI → Banda Api 2,6 |
| us100031wx | 2015-08-13 | 6,0 | Orta Hint Sırtı | G.AIS → Amsterdam Island 5,7 |
| hv70116556 | 2018-05-04 | 6,9 | Leilani, Hawaii | HV.JCUZ → Kilauea 19,9; HV.NPOC → Kilauea 18,9 |

Gerekçe: Kīlauea'da püskürmeden önce hız düşüşü raporlanmıştır (Donaldson 2019, özetten nitel). Volkanik yerlerde
dv/v magma ve hidrotermal basınçla oynar; sinyal deprem öncülünden ayrılamaz. Sürüm 1'in ad kuralı (Hawaii adası;
Akutan ve Jan Mayen bilgi satırı) bu kuralın sonucu olarak kaldırıldı. K'ye etkisi: 37 → 31. Bu değişiklik dv/v
verisi görülmeden yapıldı.

**2.8 Bağlayıcı liste.** Liste `tr5b_liste_s2.json`'dur. Kurallar, olaylar, istasyonlar (merkez, uzaklık, en düşük
≥ 10 sps, maske günleri, volkan uzaklığı, aygıt önizlemesi `aygit_degisimi_Z` ve `aygit_degisimi_PK`), 10 kontrol
adayı, plasebo, 10 plasebo kontrol adayı, PK kümeleri ve pilot P2 olayları bu dosyadadır. Girdi dosyalarının
sha256'ları da içindedir. Metinle liste çelişirse liste geçerlidir.

| Dosya | sha256 |
|---|---|
| `tr5b_liste_s2.json` | `a3a6a45a97d9e6a625f3aa6157093cda75b2190a026740573369d64bd46e8763` |
| `tr5b_olaylar_s2.csv` | `8e2f908c7f846f190f11b49b98504018ebf200333dd7d54b74e8c9a6dd814140` |
| `tr5b_kontroller_s2.csv` | `00e489e72f322d933d4a76bcb0d7f9740f45360c6c1ade0403da860846a8065a` |
| `tr5b_pilot_s2.csv` | `f36cfe746d736d4ef1b13ece33963be3b52621af97daa8dc570f70f57ad04ec9` |
| `tr5b_gvp_holosen.csv` (girdi) | `be85234874a1a85a1610552f67348b3ea1ac29ff24417575cbe92f57f145f25d` |
| `tr5_doluluk.csv` (girdi) | `1e07872307f8b777049a1e5937664ea23f07d8f156134720cef01cc8f386c25a` |

Yeniden üretim: `python3 -I -B kayit/turetme/tr5/tr5b_liste_s2.py <tr5/ham> <ngl> <tr2/ham> <tr5b_kat>`.
Girdiler depo dışındadır (TR-5 üstverisi, TR-1 ve TR-2 katalogları, M ≥ 5 kataloğu); yedekleri
`/mnt/project-files/turetme/tr5b-ham/` altında (sha256'lar `tr5b_ham_sha256.txt`). Koşu kodu listenin sha256'sını
denetler ve uyuşmazlıkta durur (`tr5b_asama0.LISTE_SHA` dondurmada bu değere sabitlenir). Bilinen metin–kod farkları,
liste geçerlidir:
- Yıllar `floor(n × 365,25)` gündür (3 yıl = 1095 g).
- Ş1–Ş3'ün "yok" aralığı yarı açıktır, [a, b).
- Plasebo istasyon kapsamı [T − 2191 g, T − 1 g] olarak hesaplanır (`yil(6)` = 2191 g).
- Aygıt önizlemesi "(a, b] içinde başlayan epok" biçimindedir.

## 3. dv/v ölçümü (sayısal, veri görülmeden sabit)

**3.1 İndirme biçimi ve gün tanımı.** Gün d, istasyonun yerel ortalama güneş tarihidir. Penceresi UTC olarak
[d 00:00 − boylam/15 saat] başlangıçlıdır, tam saate yuvarlanır, 4 saat sürer (yerel güneş saatiyle 00:00–04:00).
T, maske ve dilim sınırları bu tarihle karşılaştırılır. PK'nin ilk günü, ana şok zamanından sonra başlayan ilk tam
penceredir. Bu pencere gece olduğu için kültürel gürültü en azdır.

Üç bileşen alınır: Z ile N/E ya da 1/2. **Kanal ve konum kodu, pencereyi üstveride üç bileşenle tümüyle kapsayan
kodlar arasından seçilir:** önce bant (BH, sonra HH; ≥ 10 sps), sonra konum kodu sırası `''`, `00`, `10`, sonra
alfabetik; yatay çift önce N/E, sonra 1/2. Kapsama, epok boşlukları 30 günden kısaysa birleştirilerek sınanır. Olay
istasyonlarında kapsanacak aralık [T − 1095, T + 30], ötekilerde pencerenin kendisidir. Bir istasyon-penceresi içinde
kanal ve konum kodu değişmez. Aşama 0 yoklaması seçilen konum koduyla yapılır.

Tam gün yerine 4 saat seçildi, çünkü hacmi 6 kat küçültür. Bedeli, ölçüm gürültüsünün kabaca √6 ≈ 2,4 kat
büyümesidir: Illien 2023'e göre dv/v SNR'si toplam işlenen veri süresiyle ölçeklenir (özetten nitel doğrulandı).
§6.1'deki yapay değerler bu bedeli içermez.

**3.2 Ön işlem (saatlik pencere, bileşen başına).**
1. Saat penceresi kabul edilir, eğer üç bileşenin her birinde örneklerin ≥ %99'u varsa. 1 sn'ye kadar olan boşluklar
   doğrusal aradeğerlenir.
2. Ortalama ve doğrusal eğilim çıkarılır, %5 Hann konik uygulanır.
3. Veri 20 sn⁻¹'e indirgenir: FFT ile, 8 Hz üstü sıfırlanarak, 0,5 Hz'lik kosinüs geçişle. Tepki giderilmez. Ölçü bir
   oran olduğu ve kanal pencere içinde değişmediği için gerekmez.
4. Enerji reddi: 0,5–2 Hz bant RMS'i, medyan RMS'in 3 katını aşan saat atılır. Medyan, aynı istasyon-bileşenin
   **aynı penceresinin** bütün saatlerinden hesaplanır: hüküm penceresinde [T − 1095, T − 8] (plasebo ve kontrolde
   kendi pencereleri) saatlerinden; **PK'nin olay sonrası penceresinde [T + 1, T + 30] saatlerinin kendi
   medyanından**. Reddedilen saat oranı istasyon ve pencere başına yazılır (bilgi satırı 13). Medyan yalnız veriden
   hesaplanır, sonuçtan bağımsızdır.
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
  hız artışı ε > 0. **PK'de (yalnız yığın sonu [T − 60, T + 30] olan yığınlar için) ızgara ±%2,0'dır (adım %0,001);
  hüküm ölçüsünde ±%0,5 kalır.**
- **Geçerlilik:** CC ≥ 0,40 ve ε ızgara kenarında değil.

Ana yöntem germedir. MWCS kullanılmaz, çünkü germe düşük SNR'de daha kararlıdır (Hadziioannou 2009; bu oturumda
özeti okunmadı, doğrulanamadı) ve tek parametreyle çalışır. Başvuru uygulaması `tr5b_yapay.py`'dir
(`germe_olc`, `zincir`, `ay_esle`); PK ızgarasının başvurusu `tr5b_yapay2.germe_pk`'dir. Koşu kodu dondurulmuş yapay
diziler üstünde bu fonksiyonların sayısal sonucunu yeniden üretmek zorundadır (§4.2, adım 1).

**3.5 Hüküm ölçüsü Δ (çift başına, %).** Pencere üç yıl dilimine ayrılır:
- A = [T − 1095, T − 731];
- B = [T − 730, T − 366];
- C = [T − 365, T − 8].

Takvim ayı m = 1…12 için C'deki ve A∪B'deki ε'ların ortalamaları alınır; ikisinde de ≥ 10 geçerli gün gerekir. Ölçü:

**Δ = ortalama_m [ ort(ε | C, m) − ort(ε | A∪B, m) ]**

Ortalama eşleşen aylar üzerinden alınır ve ≥ 9 eşleşen ay gerekir. Ay eşlemesi durağan mevsimsel döngüyü boşluklu
veride de düşürür. Ana ölçü **düzey farkıdır**, eğilim değildir. Gerekçe: A∪B'ye uydurulan doğrusal eğilimi C'nin
ortasına uzatmak, beyaz gürültüde ölçü gürültüsünü ≈ 2,8 kat büyütür (orta noktaya 1,5 yıl uzaklık, 2 yıllık taban;
ilişkili gürültüde daha çok). Çok yıllı eğilimler (hidroloji, eski depremlerden toparlanma) aynı epoktaki
kontrollerle ve aynı yerdeki plaseboyla karşılaştırılır. Eğilimden arındırılmış Δ bir bilgi satırıdır. Başvurunun
son yılı içermesi sorun değildir: doğrusal yaklaşımda ε'lar ortak bir sabitle kayar, Δ'da bu sabit düşer (İNCELEME-1
K11; E2 eklenen −%0,1'in %93–98'ini geri ölçer).

**3.6 Toplama.**
- İstasyon Δ: geçerli çiftlerin medyanı. ≥ 2 geçerli çift gerekir; 2 çiftte medyan ortalamaya eşittir.
- Olay Δ_e: geçerli istasyonların ortalaması.
- Kontrol Δ_c: o kontrolün geçerli istasyonlarının ortalaması.
- Plasebo Δ_p: plasebo penceresinde aynı tanım, yalnız plasebo istasyonlarıyla (§2.4 kesişim).
- **σ_Δ**, kontrol Δ_c'lerinin standart sapmasıdır (§4.4'ün birimi). Bilgi satırı 15 istasyon düzeyi ve kontrol
  düzeyi σ̂'yı ayrı yazar. σ̂_Δ = 1,4826 × MAD(Δ_c).

**3.7 Gerekçe ve literatür (OpenAlex, yalnız özetler).**

| Seçim | Dayanak | Durum |
|---|---|---|
| SC, yüksek frekans | Hobiger 2014 (10.1093/gji/ggu115): SC yüksek, CC 0,5 Hz altı frekansta en iyi; De Plaen 2016 (10.1002/2016gl070078): SC 1–2 Hz'te çapraz istasyon kadar iyi (yakın kaynak) | Doğrulandı |
| 0,5–2 Hz ana bant | Hobiger 2016 (10.1093/gji/ggw066): kosismik düşüş frekansla artar, fay yakınında en büyük; Zaccarelli 2011 (10.1029/2011gl049750): L'Aquila'da en güçlü 0,5–1 Hz; Ikeda ve Tsuji 2018 (10.1186/s40645-018-0211-8): 0,7–2 Hz | Nitel doğrulandı. Bant sınırları literatürün ortak aralığından seçildi; tek bir kaynaktan değil |
| Bilgi bandı 2–4 Hz | Clements ve Denolle 2023 (10.1029/2022jb025553): SC, 2–4 Hz, germe, 700 istasyon; üst ≈ 500 m | Doğrulandı. Hidrolojiye en duyarlı bant; bu yüzden bilgi satırı |
| Germe | Clements ve Denolle 2023 germe kullanır; Hadziioannou 2009 | İlki doğrulandı, ikincisi doğrulanamadı |
| 10 günlük yığın, CC ≥ 0,40, koda 10–40 sn, 4 saat/gün | Yaygın değerler; İNCELEME-1 K10: özetlerde bu parametreler yok | **Doğrulanamadı.** Yalnız yapay veride sınandı (§6.1) |
| PK ızgarası ±%2 | GJI 2023 (10.1093/gji/ggad242): Kahramanmaraş'ta fay üstünde −%1,79'a kadar | Doğrulandı (özetten). ±%0,5 PK için dardı |
| Kosismik büyüklük (PK) | Taira 2015 (10.1002/2015gl065308): Napa M6,0'da ≈ %0,08 düşüş, 50 günde ≈ %50 toparlanma; Yu ve Hung 2012 (10.1029/2012gl051970): Taitung M6,1, CCF 0,1–0,9 Hz'de ≈ %0,1, ACF 2–8 Hz'de > %1 | Doğrulandı |
| Uzaklıkla sönüm | Boschelli 2021 (10.1029/2020jb021465): Ridgecrest M7,1 sonrası 50 km'den uzak istasyonlarda düşüş yok (yüksek frekans ACF); düşüş kırığa uzaklığın logaritmasıyla ölçekli | Doğrulandı |
| İstasyonlar arası genlik saçılımı | Richter 2014 (10.1002/2013jb010695): tek istasyonda düşüş ∝ PGA, istasyonlar arasında tutmaz; Ikeda ve Tsuji 2018: düşüş PGV ile ilişkili | Doğrulandı |
| Toparlanma | Hobiger 2016: düşüşlerin ≈ yarısı yıllarca toparlanmıyor; toparlanan kısmın süresi ≈ 0,55 yıl | Doğrulandı (özetten). §7 K5 satırı |
| Öncül yönü belirsiz | Tinti/Scuderi 2016 (10.1002/2016jb013545): laboratuvarda hazırlık evresinde Vp düşüşü. Ikeda ve Tsuji 2018: Nankai'de uzun dönem hız artışı, gerilme birikimine bağlandı. Chen 2013 (10.1002/2013gl058682): Wenchuan'dan hemen önce belirgin öncül yok | Doğrulandı (nitel). Biri düşüş, biri artış yönünde: iki yönlü sınav |
| Çok yıllı hidroloji | Clements ve Denolle 2023 (2011–2016 kuraklığında çok yıllı artış); Zhang 2023 (10.1029/2023gl103419); Feng 2021 (10.1029/2021jb022650): SC, 0,1–0,9 Hz, yağışla gözenek basıncı mevsimselliğe baskın | Nitel doğrulandı. Genlik doğrulanamadı |
| Kontrol mantığı | Yates 2018 (10.1029/2018gl080580): tek istasyonlarla volkanik, kosismik, mevsimsel değişimler; uzak istasyonlarla ayrıştırma | Doğrulandı (nitel) |
| Yıl ölçekli, çok olaylı pasif dv/v öncülü | – | Bulunamadı. Beklenen sonuç H0 ya da ayırt edilemez |
| Kırık boyu L(M) = 10^(−2,44 + 0,59 M) km | Wells ve Coppersmith 1994, yeraltı kırık boyu, bütün türler | Bellekten. **Doğrulanamadı** |

## 4. Hüküm satırı (tek, sıralı, otomatik)

**4.1 Puan ve ölçü.**
- **Olay puanı:** r = [#(Δ_c < Δ_e) + 0,5 · #(Δ_c = Δ_e)] / n_c. Burada n_c, olayın geçerli kontrol sayısıdır;
  ≥ 3 gerekir.
- **Küme puanı:** kümedeki olayların r ortalaması.
- **Ana ölçü r̄:** volkaniksiz geçerli kümelerin puanlarının eşit ağırlıklı ortalaması. Güven aralığı t dağılımıyla
  (df = K₆ − 1, §4.2 adım 6a): r̄ ± t · s / √K₆.

**Neden işaretli.** Ölçü işaretlidir: Δ'nın kendisi sıralanır, |Δ| değil. İki gerekçe var:
1. **Ölçek farkına dayanıklılık (TR-1 dersi).** Olay yerleri kontrollerden 1,5 kat gürültülüyse ve gerçek etki
   sıfırsa, |Δ| ölçüsü 0,620 olasılıkla yanlış H1 verir; işaretli ölçüde bu oran 0,053'tür (`tr5b_guc2.py`, K 31).
2. **Güç.** δ = 0,5 σ_Δ kayma için güç işaretli ölçüde 0,68, |Δ| ölçüsünde 0,16'dır (sürüm 1, `tr5b_guc.py`, K 35).

Bedeli de var. Kümelerin yarısında +δ, yarısında −δ olan karışık işaretli bir etki işaretli ölçüde görünmez
(δ = 1 σ_Δ'da güç 0,009; |Δ| ölçüsünde 0,73; sürüm 1, K 35). |Δ| ölçüsü bu yüzden bilgi satırıdır.

**Neden iki yönlü.** Literatür iki yönü de destekliyor: laboratuvar hazırlık evresinde düşüş, gerilme birikiminde
artış (§3.7). Hiçbir yön için yıl ölçekli, doğrulanmış bir önsel yok. Hüküm sınaması bu yüzden iki yanlıdır,
α = 0,05.

**4.2 Sıra.** Kod bu sırayı insan müdahalesi olmadan uygular. Bir adım hüküm verirse sonraki adımlar koşmaz. Hüküm
adları §4.6'daki kapalı listedendir.

0. **Veri kapıları** (§5.1; hepsinde dv/v hesaplanmaz ya da olay verisi ölçülmez; aday elenmez, yalnız güç eksikliği
   yazılır):
   - **G0 (aşama 0).** K₀ < 20 ya da K_p₀ < 10 ise "güç yok (aşama 0)".
   - **P1 (pilot).** P̂₄ < 0,50 ise "güç yok (pilot P1)".
   - **P2 (pilot).** Geçmezse "güç yok (pilot P2: yöntem kosismik düşüşü göstermedi)".
   - **1b olay tarafı.** Olay ve plasebo istasyonları indirildikten sonra: ≥ 1 dolu istasyonu olan volkaniksiz küme
     sayısı < 20 ya da eşleşik plasebo kümesi (≥ 1 dolu plasebo istasyonu) < 10 ise "güç yok (1b, olay tarafı)";
     kontroller indirilmez.
   - **1b.** K: ≥ 1 dolu istasyonu ve ≥ 4 atanmış dolu kontrolü olan volkaniksiz küme sayısı. K_p: K'de sayılan
     kümelerden, aynı olayda ≥ 1 dolu plasebo istasyonu ve ≥ 4 atanmış dolu plasebo kontrolü olanların sayısı.
     K < 20 ya da K_p < 10 ise "güç yok (1b)". Olay, 6. adımda ≥ 3 geçerli kontrol ister; burada istenen ≥ 4 dolu
     kontrol bunun önkoşuludur.
1. **Kod denetimi (i), dondurulmuş yapay diziler.** `tr5b_yapay2.py donder` E1/E2'nin yapay günlük ÇİF dizilerini
   (üç SNR düzeyi × 20 tekrar; özgün ve son yılı −%0,1 gerilmiş; float16) `tr5b_yapay_ccf.npz` dosyasına yazdı
   (sha256 `44189a31d1642e273186bfebc5c6625c62be26bf9cf090a79334da6e46a1cb29`, 631 137 078 bayt;
   `/mnt/project-files/turetme/tr5b-ham/`). Başvuru değerleri `tr5b_yapay_ccf_ref.json`'dadır (sha256
   `36339a46ac3ac75423573852ec5e0677a425d1da951e732dee52123a02580e5c`). Koşu kodu bu dizileri okur ve kendi zinciriyle
   (§3.4–3.5) işler. Her dizide Δ başvurudaki değerden en çok %0,0005, oran en çok 0,005 sapabilir. Bu sınırı aşan dizi
   sayısı > 0 ise hüküm "geçersiz (kod)" olur. PK ızgarası (±%2) aynı dosyanın ilk 5 dizisinin son 90 günü üstünde
   `tr5b_yapay2.germe_pk` ile ε başına 1e-6 içinde eşleşmelidir; değilse "geçersiz (kod)".
2. **Kod denetimi (ii-a), gerçek ÇİF'te.** Sahte olay, her olayın ilk atanmış kontrolüdür. Sahte olayın bütün
   istasyon ve çiftlerinin C dilimindeki günlük ÇİF'lerine −%0,1 germe eklenir: R(τ) → R(τ(1 − 0,001)). Başvuru ve
   yığınlar yeniden kurulur ve oran = (Δ_eklenmiş − Δ_özgün) / (−%0,1) hesaplanır. Ölçüt: bütün sahte olayların, Δ'sı
   hem özgün hem eklenmiş durumda geçerli olan istasyonları üstünden havuzlanmış medyan oran. [0,80; 1,20] dışındaysa
   hüküm "geçersiz (kod)" olur. Bu adımda yalnız kontrol verisi okunur.
3. **Negatif kontrol N1.** Sahte olay, kalan kontrollere karşı puanlanır. Sahte r̄'nin iki yanlı %95 aralığı 0,5'i
   dışlarsa hüküm "geçersiz (kod ya da tasarım)" olur. H0 altında yanlış tetiklenme olasılığı 0,05'tir (§6.2).
4. **Duyarlılık (ii-b).** 2. adımdaki −%0,1 eklenmiş sahte olaylar kalan kontrollere karşı puanlanır. r̄_sahte ve
   iki yanlı %95 t aralığı (df = K − 1) yazılır. **Aralığın üst sınırı 0,5'ten küçük değilse ölçü "kör" sayılır ve
   hüküm "güç yok (4. adım: ölçü −%0,1'e kör)" olur.** Bu, ana ölçünün −%0,1'lik tek biçimli bir son yıl kaymasını
   kendi ölçütüyle saptayamadığı anlamına gelir. Ayrıca r̄_sahte ≤ 0,25 olup olmadığı yazılır (S4, bilgi):
   - S4 tutuyorsa H0 cümlesi "%0,1 ölçeğinde" diye yazılır.
   - Tutmuyorsa H0 cümlesi "yalnız σ_Δ ölçeğinde; dışlanan tek yönlü kayma ≈ 0,55 · σ̂_Δ = …%" diye yazılır.
   - Geçme olasılığı (K 31; `tr5b_guc2.py`): σ_Δ %0,075 / 0,1 / 0,15 / 0,2 / 0,3 için 1,00 / 0,99 / 0,86 / 0,63 /
     0,34. K 28'de 1,00 / 0,99 / 0,83 / 0,59 / 0,31.
5. **Plasebo.** Eşleşik kümelerde r_p hesaplanır (plasebo Δ_p, T′ epoğunun plasebo kontrollerine karşı). r̄_p ve
   aralığı yazılır.
6. **Ana ölçü.** Olay Δ'ları ilk kez bu adımda hesaplanır.
   - **6a.** Geçerli Δ_e'si ve ≥ 3 geçerli kontrolü olan volkaniksiz küme sayısı K₆ sayılır; yalnız sayı yazılır.
     K₆ < 20 ise hüküm "güç yok (ε geçerliliği)" olur. Aynı şartla, hem geçerli r_e'si hem geçerli r_p'si olan olayı
     bulunan eşleşik küme sayısı K_p6 sayılır.
   - r̄, %95 ve %90 t aralıkları (df = K₆ − 1) ve eşleşik fark d̄ (§2.4; df = K_p6 − 1) dosyaya yazılır. Dosyanın
     sha256'sı koşu günlüğüne geçer.
7. **Zaman kaydırma (bilgi, hükmü değiştirmez).** Aynı veriyle Δ_kay = B − A hesaplanır (ay eşlemeli, aynı kurallar)
   ve kontrollerin aynı ölçüsüne karşı puanlanır: r̄_kay. Ek veri gerektirmez.
8. **Pozitif kontrol (kosismik).** Olay istasyonlarının [T + 1, T + 30] verisi **ilk kez bu adımda okunur**. Okuma
   6. adımın çıktısı yazıldıktan sonra yapılır; gerekçe §4.5'te.
   - İstasyon δ_ko: ort ε(yığın sonu [T + 10, T + 30]) − ort ε(yığın sonu [T − 60, T − 8]). Bu yığınlar ±%2 ızgarasıyla
     ölçülür (§3.4). Başvuru 3.4'teki olay öncesi başvurudur. Enerji reddi medyanı olay sonrası penceresinde
     [T + 1, T + 30] saatlerinin kendi medyanıdır (§3.2). Maske [T, T + 30] için uygulanmaz. Öncesinde ≥ 10, sonrasında
     ≥ 5 geçerli ε gerekir. Aygıt kuralını [T − 1095, T + 30]'da bozan istasyon kullanılmaz (§2.5).
   - **Olay δ_ko, olayın en yakın geçerli istasyonunun δ_ko'sudur** (istasyon ortalaması değil). Küme δ_ko, kümedeki
     olay δ_ko'larının ortalamasıdır.
   - PK kümeleri (önceden sabit, 16 küme): en yakın olay istasyonu ≤ max(30 km, 2 · L(M)) olan volkaniksiz kümeler.
     Kimlikler `tr5b_liste_s2.json` → `kural.pk_kume`; liste §Ek'tedir.
   - Geçme şartı: ≥ 8 geçerli PK kümesi ve tek yanlı kesin Wilcoxon işaretli sıra testinde p ≤ 0,05 (H1: medyan
     δ_ko < 0). Genlik şartı yoktur.
   - Geçmezse ya da geçerli küme < 8 ise: 9. adımın H1 şartları sağlanıyorsa hüküm **"ayırt edilemez (PK geçmedi)"**,
     sağlanmıyorsa **"güç yok (yöntem bilinen kosismik düşüşü göstermedi)"** olur. 6. adımın r̄'si yalnız bilgi olarak
     yazılır.
9. **Hüküm** (öncelik sırasıyla):
   - **H1 (yön: artış ya da düşüş).** Dört şart birlikte gerekir:
     - r̄'nin %95 aralığı 0,5'i dışlar;
     - K_p6 ≥ 10;
     - d̄'nin tek yanlı %95 sınırı 0'ı aynı yönde dışlar;
     - r̄_p'nin %95 aralığı 0,5'i aynı yönde dışlamaz.

     H1 ile birlikte r̄'nin %90 aralığı [0,35; 0,65] içinde kalıyorsa "küçük etki" notu eklenir. r̄_kay da aynı yönde
     0,5'i dışlıyorsa "son yıla özgü değil; hidroloji ya da yer eğilimiyle uyumlu" notu eklenir. Hidroloji cümlesi
     (§4.3) her H1'e eklenir. H1 düşüş yönündeyse ve bilgi satırı 16 0,5'i aynı yönde dışlamıyorsa "Etki, öncü
     deprem etkinliğinin kosismik etkisinden ayrılmadı." notu eklenir.
   - **H0 (eşdeğerlik).** r̄'nin %90 aralığı [0,35; 0,65] içinde. Bu, iki tek yanlı %5 sınaması (TOST) demektir.
     Sınır ±0,15 AUC'dir (|δ| ≈ 0,55 σ_Δ). Bu değer, etki yokken H0 alma olasılığının yeterince büyük olması için
     seçildi: K 31'de 0,56. Daha dar bir sınır (±0,10) bu olasılığı 0,025'e indirirdi (`tr5b_guc2.py`). H0 cümlesinin
     yüzde karşılığı σ̂_Δ ile otomatik yazılır (4. adım).
   - **Ayırt edilemez:** öteki bütün durumlar. Ana aralık 0,5'i dışladığı hâlde plasebo şartlarından (d̄ ya da r̄_p)
     biri tutmuyorsa hüküm "ayırt edilemez (yer yanlılığı dışlanamadı)", K_p6 < 10 ise "ayırt edilemez (plasebo
     kümesi < 10)" diye yazılır.

**4.3 Hükümlerin anlamı.**
- **H1:** Bu örneklemde, olay öncesi son yılın dv/v düzeyi, aynı yerin önceki iki yılına göre, aynı epoktaki kontrol
  yerlerinden sistematik olarak farklıdır. Bu fark aynı yerin üç yıl önceki penceresinde yoktur. Tahmin becerisi
  iddiası değildir. Her H1 metnine şu cümle eklenir: "Bu fark, olay yerlerinde son yılı önceki iki yıldan farklı
  geçen yerel çok yıllı hidrolojiden (kuraklık ya da yeniden beslenme) ayrılmadı. Kontroller yerel iklimi eşlemez,
  plasebo yalnız yere özgü kalıcı yanlılığı yakalar. Bu açıklama, yağış ya da yeraltı suyu verisiyle yapılacak ayrı
  bir ön kayıtla dışlanmadıkça H1 öncül kanıtı sayılmaz."
- **H0:** Bu ölçü (0,5–2 Hz SC, düzey farkı, 1 yıl / 2 yıl), dış merkezden ortanca 50 km uzaktaki istasyonların
  çevresindeki sığ ortamda, bu örneklemde 0,35–0,65 AUC dışında bir etki göstermiyor. Kabaca |δ| ≳ 0,55 σ_Δ'lık tek
  yönlü kayma dışlanır (yüzdesi 4. adımdan). Karışık işaretli etkiyi, başka bantları, daha kısa öncül pencerelerini,
  fay bölgesindeki ya da derindeki süreçleri ve M ≥ 7'yi kapatmaz. Metne bilgi satırı 9'un K'si ve r̄'si yazılır.
- **Ayırt edilemez:** Etki yok anlamına gelmez. "(PK geçmedi)": ölçü bir şey görmüş, ama bilinen kosismik etkiyi
  görmediği için bu kanıt değildir.
- **Güç yok:** Ölçü bu veriyle sınanamadı. Aday elenmez.
- **Geçersiz:** Kod ya da tasarım hatası; ölçü yorumlanmaz.

**4.4 Önceden hesaplanan hüküm olasılıkları.** Hesap `tr5b_guc2.py` ile yapıldı (tohum 20261113): K = 31,
eşleşik plasebo 16, n_c = 5, 20 000 yineleme, küme yapısı `tr5b_liste_s2.json`dan. δ, σ_Δ birimiyle (§3.6) olay
kaymasıdır; AUC = Φ(δ/√2). Plasebo etkisiz varsayıldı. Tablodaki σ_Δ, gerçek dünya σ_Δ'sıdır (bilinmiyor; §6.2).

| δ (σ_Δ) | AUC | H1 | H0 | Ayırt edilemez | Yalnız ana aralık 0,5'i dışlar |
|---|---|---|---|---|---|
| 0 | 0,500 | 0,012 | 0,561 | 0,427 | 0,047 |
| 0,25 | 0,570 | 0,067 | 0,324 | 0,609 | 0,209 |
| 0,50 | 0,638 | 0,251 | 0,059 | 0,690 | 0,619 |
| 0,75 | 0,702 | 0,505 | 0,003 | 0,492 | 0,926 |
| 1,00 | 0,760 | 0,709 | 0,000 | 0,291 | 0,994 |

- **0,8 güçle ölçülebilir en küçük etki.** Yalnız ana aralıkla δ = 0,62 σ_Δ (AUC 0,67). Tam H1 kuralıyla, yani
  plasebo eşleşik fark şartıyla, δ = 1,16 σ_Δ (AUC 0,79).
- **Yüzde karşılığı.** σ_Δ = 0,05 / 0,1 / 0,2 % için ana aralıkta 0,031 / 0,062 / 0,124 %, tam H1'de 0,058 / 0,116 /
  0,231 %.
- **Kosismik düşüşle kıyas.** Napa'nın kosismik düşüşü ≈ %0,08'dir. σ_Δ ≈ %0,1 ise tam H1 kuralı ancak bir M6
  kosismik düşüşünün ≈ 1,5 katı büyüklüğündeki bir öncülü 0,8 olasılıkla görür.
- **Olay gürültüsü (Ö7).** Olay Δ'sı çoğunlukla tek istasyondan gelir, kontrol Δ_c 1–3 istasyonun ortalamasıdır.
  Olay Δ'sı kontrollerden 1,5 kat gürültülüyse tam H1 gücü δ = 0,5 / 0,75 / 1,0'da 0,13 / 0,28 / 0,45'e iner.
- **K'ye göre** (aygıt kuralından ya da doluluktan sonra küçülürse):

  | K / K_p | H0 (δ 0) | H1 (δ 0,5) | H1 (δ 0,75) |
  |---|---|---|---|
  | 31 / 16 | 0,561 | 0,251 | 0,505 |
  | 28 / 15 (Z önizlemesi) | 0,482 | 0,238 | 0,475 |
  | 25 / 13 | 0,386 | 0,201 | 0,417 |
  | 20 / 10 | 0,191 | 0,150 | 0,330 |

  Kapıda (K 20), gerçek etki sıfırken bile H0 alma olasılığı 0,19'dur. "Ayırt edilemez" bu tasarımda en olası tek
  sonuçtur ve bu önceden kabul edilir.

**4.5 Pozitif kontrol için olay sonrası penceresinin seçimi.** İki seçenek vardı: (a) kümelerin kendi ana şokları,
olay sonrası penceresinde; (b) ayrı bir olay kümesi. Hüküm için (a) seçildi, dört gerekçeyle:
1. **Aynı zincir sınanır.** PK, hükmü üreten aynı istasyon, kanal, başvuru ve kod zinciriyle yapılır.
2. **Ek seçim serbestliği yok.** PK kümeleri listede sabittir.
3. **Hacim küçük.** Ek hacim 51 istasyon × 30 gündür, A biçiminin ≈ %0,4'ü.
4. **Sızıntı riski düşük.** Olay sonrası veri, hüküm ölçüsünün hiçbir girdisinde kullanılmaz. Ölçünün kendisi 6.
   adımda yazılıp sha256'sı kayda geçtikten sonra okunur.

(b) ise ana indirmeden önce, ayrı bir durdurma kuralı olarak pilot P2'de kullanılır (§5.1): listede olmayan olaylarla,
olay istasyonlarına dokunmadan, "yöntem bu uzaklıklarda kosismik düşüşü görüyor mu" sorusunu sorar.

Bedeli: PK'nin geçmesi hüküm verisini görmüş bir kodla sınanır. Ama kod 6. adımdan sonra değiştirilemez (§5.5).
Bu yüzden bedel yalnız bilgidir.

PK eşiğinde genlik şartı yok, yalnız yön sınaması var. Bunun nedeni literatür genliklerinin istasyondan istasyona
saçılması (Richter 2014) ve 50 km'den uzakta sıfıra inebilmesidir (Boschelli 2021). Kökün andığı %0,2–1,5'lik
kosismik düşüşler M 6,6–9 olaylarının yakın alanından gelir. Bu örneklemdeki M 6,0–6,4 ve ≈ 50 km'lik istasyonlar
için doğru ölçek Napa'nın ≈ %0,08'idir. Geçme olasılığı §6.1'de E3 ile yapay veride hesaplandı.

**4.6 Hüküm adlarının kapalı listesi ve kalıpları.** Koşu yalnız bu adlardan birini yazar. Köşeli parantezler
otomatik doldurulur; başka metin eklenmez.

| Hüküm adı (aynen) | Nerede | Şart | Zorunlu ek metin |
|---|---|---|---|
| güç yok (aşama 0) | 0 / G0 | K₀ < 20 ya da K_p₀ < 10 | "K₀ = [..], K_p₀ = [..]" |
| güç yok (pilot P1) | 0 / P1 | P̂₄ < 0,50 | "σ̂_P1 = [..] %, P̂₄ = [..]" |
| güç yok (pilot P2: yöntem kosismik düşüşü göstermedi) | 0 / P2 | geçerli < 8 ya da p > 0,05 | "geçerli olay [..], p = [..]" |
| güç yok (1b, olay tarafı) | 0 / 1b | olay tarafı küme < 20 ya da plasebo < 10 | sayılar |
| güç yok (1b) | 0 / 1b | K < 20 ya da K_p < 10 | sayılar |
| geçersiz (kod) | 1, 2 | §4.2 adım 1–2 | sapan dizi sayısı ya da medyan oran |
| geçersiz (kod ya da tasarım) | 3 | N1 aralığı 0,5'i dışlar | r̄_sahte ve aralık |
| güç yok (4. adım: ölçü −%0,1'e kör) | 4 | üst sınır ≥ 0,5 | r̄_sahte, aralık, S4 |
| güç yok (ε geçerliliği) | 6a | K₆ < 20 | K₆ |
| güç yok (yöntem bilinen kosismik düşüşü göstermedi) | 8 | PK geçmedi, H1 şartları yok | geçerli PK kümesi, p |
| ayırt edilemez (PK geçmedi) | 8 | PK geçmedi, H1 şartları var | r̄, aralık, geçerli PK kümesi, p |
| H1 (artış) / H1 (düşüş) | 9 | dört H1 şartı | hidroloji cümlesi; varsa "küçük etki", "son yıla özgü değil; hidroloji ya da yer eğilimiyle uyumlu", öncü etkinliği notu |
| H0 (eşdeğerlik) | 9 | %90 aralığı [0,35; 0,65] içinde | dışlanan kayma (S4'e göre "%0,1 ölçeğinde" ya da "yalnız σ_Δ ölçeğinde; ≈ 0,55 · σ̂_Δ = [..] %"); bilgi satırı 9 |
| ayırt edilemez (yer yanlılığı dışlanamadı) | 9 | ana aralık dışlar, d̄ ya da r̄_p şartı tutmaz | r̄, d̄, r̄_p |
| ayırt edilemez (plasebo kümesi < 10) | 9 | ana aralık dışlar, K_p6 < 10 | K_p6 |
| ayırt edilemez | 9 | öteki bütün durumlar | r̄ ve aralıklar |

Her hükümle birlikte, ulaşılan son adıma kadarki bütün sayılar ve §8'in o ana kadar hesaplanabilen bilgi satırları
yazılır.

## 5. Koşu düzeni, hacim, süre ve maliyet

**5.1 Aşamalar.** Sıra: aşama 0 → kod incelemesi → aşama P (pilot) → 1b olay tarafı → 1b kontroller → 2. aşama →
3. aşama. Ön kayıt, liste ve koşu kodu aşama P'den önce dondurulur ve push edilir. Bütün istek zamanları
≤ 2023-12-31'dir (aşama 0 ve 1b; P2 için ≤ 2025-12-31, listede en geç 2022-10-18).

**Aşama 0 (sunucu kiralanmadan, bulut oturumundan, 0 €).** Dalga formu okunmaz. Yalnız HTTP kodu ve bayt sayısı
kaydedilir; istasyon servisinden yalnız kanal üstverisi metni alınır. Kod: `tr5b_asama0.py`.
1. **Üstveri (`ustveri`).** Listedeki bütün istasyonlar (olay, plasebo, kontrol adayı 1–10, plasebo kontrol adayı
   1–10; 292 istasyon) için merkezin fdsnws-station servisinden `level=channel&format=text&channel=BH?,HH?`, istasyon
   başına tek istek, istasyonun bütün pencerelerini kapsayan zaman aralığıyla. Servis adresleri `doluluk_yokla.py`'nin
   dataselect adreslerinden türetilir (`/dataselect/1/` → `/station/1/`). Her yanıt `ustveri/<ağ.istasyon>.txt`
   olarak önbelleğe yazılır; olan dosya yeniden istenmez.
2. **Kanal seçimi ve istek listesi (`kur`, ağsız).** Her istasyon-penceresi için §3.1'in kanal ve konum kodu seçimi
   yapılır ve seçilen üç kanala §2.5'in aygıt kuralı uygulanır (olayda [T − 1095, T + 30]; yalnız (T − 8, T + 30]
   içinde bozan istasyon PK'den düşer). Sonra istekler kurulur ve `(ağ, istasyon, konum, kanal, ay)` anahtarıyla
   tekilleştirilir:
   - **Z ay yoklaması:** bütün istasyon-pencerelerinde (olay ve plasebo dahil; Ek 1'in `loc=*` yoklaması seçilen
     konum koduyla yinelenir), penceredeki her ayın 15'inde 12:00:00–12:01:00 UTC, seçilen konum kodunun Z kanalı.
   - **Yatay yoklama:** her istasyon-penceresinde A, B ve C dilimlerinin orta gününün ayında (15'i, 12:00–12:01),
     seçilen iki yatay kanala ayrı ayrı. Altı istekten biri "var" değilse pencere "üç bileşen yok" sayılır.
3. **Yoklama (`yokla`).** Kurallar ve nezaket TR-5 Ek 1 (`doluluk_yokla.py`) ile aynıdır: merkez başına tek akış;
   EarthScope, GEOFON ve ORFEUS'ta istekler arası ≥ 0,3 sn, KOERI'de ≥ 2 sn, öteki merkezlerde ≥ 0,5 sn; 429/503'te
   Retry-After (en çok 120 sn) ya da 30/60 sn beklenir, en çok 2 yeniden deneme; genel User-Agent; TLS doğrulaması
   açık; yanıt gövdesi okunur ama çözülmez ve saklanmaz. Her yanıt `onbellek.jsonl`'a satır olarak eklenir. İş
   önbellekten sürdürülür: yeniden çağrı yalnız kalan istekleri atar. `sure_sn` ile iş 2 saatlik sınırdan önce kendini
   durdurur. Ağ kipleri yalnız `--ag-onay` bayrağıyla çalışır.
4. **Sayım (`say`).** Ay "var": HTTP 200 ve bayt > 0; 204/404 ya da 200 ile 0 bayt: yok; 401/403: kısıtlı (yok
   sayılır, atlatılmaz); öteki: hata (yok sayılır, ayrıca sayılır). İstasyon-penceresi **dolu**: kanal seçildi, aygıt
   kuralı geçti, Z ay doluluğu `dolu_ana` (ayların ≥ %80'i var ve en uzun ardışık boş ay ≤ 3) ve altı yatay istek
   "var". Kontrol dolu: ≥ 1 dolu istasyonu var. Kota (§2.3) uygulanarak kontroller atanır. Olay geçer: ≥ 1 dolu
   istasyon ve ≥ 4 atanmış kontrol. **K₀:** geçen olayı olan volkaniksiz küme sayısı. **K_p₀:** K₀ kümelerinden, aynı
   olayın plasebo tarafı da geçen (≥ 1 dolu plasebo istasyonu ve ≥ 4 atanmış plasebo kontrolü) kümelerin sayısı.
5. **Kapı G0.** K₀ < 20 ya da K_p₀ < 10 ise hüküm "güç yok (aşama 0)" olur. Sunucu kiralanmaz; dalga formu
   indirilmez; aday elenmez. K₀ ve K_p₀ 1b'nin üst sınırıdır. Kayda §4.4'ün tablosu K₀ ve K_p₀ ile `tr5b_guc2.py`'nin
   `benzet` fonksiyonuyla yeniden hesaplanarak yazılır. Aşama 0 ayrıca pilot P1'in istasyonlarını belirler.

Aşama 0'ın boyutu (`tr5b_asama0.py kuru`, ağsız; konum kodu yerel Z üstverisinden vekil; çıktı
`tr5b_asama0_kuru.json`):
- 1246 istasyon-penceresi: olay 60, plasebo 26, kontrol adayı 815, plasebo kontrol adayı 438; 292 istasyon.
- **27 410 istek:** 292 üstveri, 20 424 Z ayı, 6694 yatay. Merkez payı: EarthScope 14 887, INGV 2780, GEOFON 2613,
  NOA 2377, SCEDC 1360, GEONET 1147, NCEDC 1070, ORFEUS 878, öteki 298. (İNCELEME-1'in ≈ 50 000'i istasyon-pencere
  başına sayıyordu; aynı istasyonun örtüşen pencereleri aynı ayı bir kez ister.)
- Süre: merkezler paralel, EarthScope darboğaz. İstek başına "gecikme + bekleme" ile 2,9 saat (tutucu), betiğin
  gerçek akışıyla (bekleme bir önceki isteğin başından ölçülür) 1,6 saat. Gecikmeler Ek 1'in ölçülen medyanlarıdır
  (EarthScope 0,38 sn; bilinmeyen merkez 1,0 sn; üstveri isteği 2 sn varsayıldı).
- **Bulut oturumunda 2 iş** (2 saatlik iş sınırı; ikinci iş önbellekten sürer), 0 €. Aktarım ≈ 0,3 GB, saklanmaz.

**Aşama P (pilot; aşama 0 geçtikten ve kod incelemesinden sonra; ana indirmeden önce).** Aşama P'nin sonucu hiçbir
işleme parametresini, listeyi ya da hüküm kuralını değiştiremez. Yalnız aşağıdaki iki durdurma kuralını işletir. Olay
ve plasebo istasyonlarının hiçbir verisi bu aşamada indirilmez.

**P1 (σ_Δ, yalnız kontrol verisi).**
- Volkaniksiz olaylar (T, kimlik) sırasıyla alınır. Her birinin aşama 0'da atanan ilk kontrolünün en yakın dolu
  istasyonu seçilir (`asama0_sonuc.json` → `p1`). İlk 24 olayın bu istasyon-pencereleri ([T − 1095, T − 8]) §3.1–3.5
  ile işlenir. Bu pencereler bağlayıcı listenin sahte olay verisidir; koşuda yeniden indirilmez.
- σ̂_P1 = 1,4826 × MAD(24 istasyon Δ'sı), %. Geçersiz Δ'lı istasyon sayılmaz; geçerli Δ < 12 ise σ̂_P1 tanımsızdır ve
  hüküm "güç yok (pilot P1)" olur.
- P̂₄: 4. adımın geçme olasılığı; `tr5b_guc2.py`'nin `adim4` fonksiyonuyla, σ_Δ = σ̂_P1, K = K₀, n_c = 5, 20 000
  yineleme, yeni üreteç tohumu 20261113.
- **P̂₄ < 0,50 ise hüküm "güç yok (pilot P1)" olur ve ana indirme yapılmaz.** Eşdeğer eşik σ*(K): P̂₄ = 0,5'te
  σ_Δ = %0,234 (K 31), %0,222 (K 28), %0,212 (K 25), %0,187 (K 20). Çelişkide P̂₄ geçerlidir.
- σ̂_P1 ve 24 Δ değeri kayda geçer. Δ'lar hiçbir olay ölçüsüyle karşılaştırılmaz.
- Not: σ̂_P1 istasyon düzeyindedir; σ_Δ kontrol düzeyindedir (1–3 istasyon ortalaması). σ̂_P1 bu yüzden σ_Δ'yı büyük
  kestirir; kural tutucu yöndedir.

**P2 (kosismik düşüş, listede olmayan olaylar).**
- Aday olaylar: ComCat `type = earthquake`, M ≥ 6,0, derinlik ≤ 30 km, 2005-01-01 ile 2023-12-31 arası, TR-5b
  listesinde olmayanlar (TR-2 `m6_havuz.csv`). Dış merkez TR-4 kutusu (40,0–41,6° K, 26,5–30,5° D) ve TR-1'in Marmara
  kutusu (39,5–42,0° K, 26,0–31,5° D) dışında olmalıdır.
- İstasyon: dış merkeze ≤ max(30 km, 2 L(M)) uzaklıktaki açık BH ya da HH istasyonlarından, şu şartları sağlayan
  en yakını: üstverisi [T − 400 g, T + 30 g] aralığını kesintisiz kapsar; bu aralıkta §2.5 aygıt kuralını geçer;
  TR-1 kutusunda değil; KOERI ya da 6G değil; bir Holosen volkanına > 25 km; bu aralıkla örtüşen bir pencerede TR-5b
  listesinin hiçbir rolünde (olay ve PK, plasebo, kontrol adayı 1–10, plasebo kontrol adayı 1–10) yer almıyor. Üç
  bileşen ve aygıt kuralı pilotta, aşama 0'ın kanal seçimiyle sınanır; tutmayan olay geçersiz sayılır, yerine olay
  gelmez.
- Sıralama SHA-256(`pilot|{kimlik}`) değerine göre artandır. İstasyon şartını sağlayan adaylar arasında, sırada önce
  gelmiş bir adaya 300 km ve 365 gün içinde olan aday atlanır. İlk 20 olay kullanılır; olay başına yalnız bu istasyon
  alınır. Liste `tr5b_pilot_s2.csv` ve `tr5b_liste_s2.json` → `pilot_p2` (20 olay; istasyon uzaklıklarının medyanı
  29,2 km; §Ek).
- Ölçüm: başvuru [T − 400, T − 8] geçerli günlük ÇİF'lerinin ortalamasıdır. δ_ko §4.2 adım 8 tanımıyla (enerji reddi
  medyanı, ±%2 ızgarası, aygıt aralığı dahil) hesaplanır. M ≥ 5 maskesi olay öncesi günlere uygulanır.
- [T − 400, T − 8] için δ_ko'dan başka hiçbir ölçü (düzey, eğilim, Δ) hesaplanmaz ve yazdırılmaz.
- Geçme şartı: ≥ 8 geçerli olay ve tek yanlı kesin Wilcoxon işaretli sıra testinde p ≤ 0,05 (H1: medyan δ_ko < 0).
  **Geçmezse hüküm "güç yok (pilot P2: yöntem kosismik düşüşü göstermedi)" olur ve ana indirme yapılmaz.**
- Bu ön kayıt içinde P2 yeniden denenmez. P2'nin olayları listede olmadığı için, ayrı bir yeni ön kayıt başka bir bant
  ya da parametreyle P2'yi deneyebilir; bu TR-5b'nin körlüğünü bozmaz ve her deneme kayda geçer (§11).

**Pilotun boyutu** (`tr5b_ozet_s2.json` → `hacim`; P1 istasyonları aşama 0'dan önce bilinmediği için her olayın 1.
adayının en yakın istasyonu vekil alındı):
- P1: 22 istasyon, 24 682 istasyon-günü, ≈ 0,094 TB (EarthScope 0,032; INGV 0,018; ORFEUS, GEONET, NOA 0,012'şer;
  GEOFON 0,007). P1 verisi ana koşuda yeniden kullanılır.
- P2: 20 istasyon, 8620 istasyon-günü, ≈ 0,024 TB (EarthScope 0,015).
- Toplam ≈ 0,12 TB, A'nın ≈ %8'i. Merkezler paralel; EarthScope 2,4 MB/s ile ≈ 5,4 saat; ölçülmemiş merkezler
  1 / 0,4 MB/s varsayımıyla ≈ 5 / 13 saat (INGV). Duvar saati ≈ 5–13 saat.
- **Bulut oturumunda 3–7 iş** (2 saatlik; istek ve ÇİF önbelleğiyle sürdürülür), 0 €. Akış hâlinde işlenir: ham
  miniSEED istasyon-gün işlendikten sonra silinir, günlük ÇİF'ler saklanır (P1 ≈ 0,75 GB, P2 ≈ 0,25 GB); 16 GB disk
  yeter. İşlem ≈ 33 000 istasyon-günü × 0,3 CPU-sn ≈ 3 CPU-saat (doğrulanamadı). Pilot bulutta 7 işi aşarsa kalan
  kısım sunucuda koşulur; bu yalnız işletim kararıdır.

**1b. İndirme ve gün doluluğu (sıralı).** İndirme §3.1 biçimiyle yapılır. EarthScope istekleri POST ile istasyon
başına 30 günlük paketler hâlinde atılır; 0,3 sn bekleme paket başınadır.
- **1b-olay:** önce olay istasyonları (hüküm penceresi ve [T + 1, T + 30]) ve plasebo istasyonları indirilir
  (≈ 0,23 TB). Olay sonrası veri bu aşamada indirilir ama 8. adımdan önce açılmaz (§5.5). Bunlar bitince olay tarafı
  sayılır (§4.2 adım 0); geçmezse kontroller indirilmez.
- **1b-kontrol:** sonra aşama 0'da atanan kontroller ve plasebo kontrolleri.
- **Gün dolu:** 4 saatin ≥ 2'si üç bileşende kabul edilmiş (§3.2 madde 1).
- **İstasyon-penceresi dolu:** A, B ve C dilimlerinin her birinde dolu gün oranı ≥ 0,60 (payda: dilimin maskesiz
  günleri), üç bileşen var, aygıt kuralı (§2.5) geçiyor ve ≥ 9 takvim ayında hem C'de hem A∪B'de ≥ 10 gün için
  yığın şartı (son 10 günde ≥ 5 dolu ve maskesiz gün) sağlanıyor. Bu, ε'nin CC dışındaki geçerlilik şartıdır ve ε
  hesaplanmadan sayılır.
- Dolu olmayan kontrolün yerine kota atamasıyla (§2.3) sıradaki aday gelir. 10 aday tükenirse yeni aday eklenmez.
- Bu aşamada ÇİF hesaplanabilir, ama ε ve Δ hesaplanmaz.
- **Kapı (§4.2 adım 0, 1b).** K ve K_p sayılır ve kayda geçer.
- **2. aşama.** §4.2 adım 1–7. **3. aşama.** §4.2 adım 8–9.

**5.2 Hacim.** Hesap `tr5b_liste_s2.py` → `tr5b_ozet_s2.json` → `hacim`. İstasyon başına pencerelerin gün birleşimi
alındı; satırlar kendi içinde tekrarsızdır. Varsayımlar: 1,3 bayt/örnek (TR-5 §5.1 ölçümü); en düşük ≥ 10 sps kanal;
3 bileşen; 4 saat/gün.

| Kalem | İstasyon | İstasyon-gün | 4 saat/gün, 3 bileşen |
|---|---|---|---|
| 1b-olay: olay [T − 1095, T − 8] + PK [T + 1, T + 30] + plasebo | 52 | 82 102 | **0,226 TB** |
| 1b-kontrol: kontrol 1–5 + plasebo kontrol 1–5 (1b-olay'a ek) | 209 | 394 139 | **1,246 TB** |
| **A (bağlayıcı) = 1b-olay + 1b-kontrol** | 250 | 476 241 | **1,471 TB** |
| A, P1 verisi düşülmüş | 250 | 451 559 | 1,377 TB |
| B (bütün adaylar: kontrol 10, plasebo kontrol 10; üst sınır) | 292 | 613 921 | 1,902 TB |
| Pilot P1 + P2 | 42 | 33 302 | 0,118 TB |

- **Merkez payı (A):** EarthScope 0,69 TB, NOA 0,21, INGV 0,17, GEOFON 0,12, GEONET 0,11, ORFEUS 0,07, öteki ≤ 0,04.
  KOERI 0,004 TB (yalnız olay istasyonları KO.DKL ve KO.BODT).
- **1b-olay merkez payı:** EarthScope 0,083, NOA 0,062, ORFEUS 0,019, GEOFON 0,015, IGN 0,012, NCEDC 0,010, öteki
  ≤ 0,006 TB.
- Yalnız hüküm bandının ÇİF'leri saklanır (0,5–2 Hz ve bilgi bandı 2–4 Hz; ≈ 15 GB bant başına); ham miniSEED
  işlendikten sonra silinir, istek ve sha256 günlüğü kalır.

| Seçenek | Hacim etkisi | Hükme etkisi | Karar |
|---|---|---|---|
| Kontrol 10 → 5 (5 yedek) | 1,90 → 1,47 TB | r'nin sd'si 0,316 → 0,342; en küçük δ ≈ %8 büyür | **Bağlayıcı** |
| Kontrol 3 | – | sd 0,373; N1 için 2 kontrol kalır | Reddedildi |
| Plasebo kontrolsüz | – | Plasebo yalnız olay kontrolleriyle kıyaslanır, epok eşleşmez; d şartı zayıflar | Reddedildi |
| 4 saat/gün (tam gün yerine) | ÷ 6 | Ölçüm gürültüsü ≈ × 2,4 (§3.1) | **Bağlayıcı** |
| KOERI ve 6G kontrollerden çıkar | KOERI süresi ≈ 39 gün → ≈ 1,3 gün (yalnız olay) | Kontrol havuzunda Anadolu merkezleri azalır | **Bağlayıcı** |
| Yalnız Z | ÷ 3 | SC yöntemi bozulur (TR-5 Ek 1) | Reddedildi |

**5.3 Süre.** Ölçülen hızlar: EarthScope tek akış ≈ 2,4 MB/s, KOERI tek akış ≈ 40 KB/s. İkisi de TR-5'te tek
denemeyle ölçüldü. Öteki merkezlerin hızı ölçülmedi; 1 MB/s ve 0,4 MB/s iki varsayım olarak alındı (doğrulanamadı).

| Kalem | Süre |
|---|---|
| Aşama 0 (27 410 istek; bulut) | 1,6–2,9 saat; 2 iş |
| Pilot P1 + P2 (0,12 TB; bulut) | ≈ 5–13 saat; 3–7 iş |
| 1b-olay (0,23 TB) | EarthScope ≈ 9,6 saat; NOA ≈ 17 / 43 saat; KOERI 4,4 GB ≈ 31 saat → **≈ 1,3–1,8 gün** |
| 1b-kontrol (1,25 TB) | EarthScope 0,61 TB ≈ 2,9 gün (+ paket beklemesi ≈ 0,5 saat); INGV 0,17 TB ≈ 1,9 / 4,9 gün; NOA 0,15 TB ≈ 1,8 / 4,4 gün → **≈ 2,9–4,9 gün** |
| Yedek adayların ek indirmesi (A → B üst sınırı) | ≤ +0,43 TB; ≈ +1–2,7 gün |
| İşlem (≈ 0,3 CPU-sn / istasyon-gün; doğrulanamadı) | ≈ 40 CPU-saat; 8 çekirdekte ≈ 5 saat, indirmeyle örtüşür |
| **Sunucuda toplam duvar saati (1b + 2. ve 3. aşama)** | **≈ 4,5–9 gün, yani ≈ 1–1,5 hafta** |

Merkezler paralel indirilir: merkez başına tek akış, TR-5 Ek 1 nezaket kuralları. EarthScope'ta ikinci akış açılmaz.

**5.4 Makine ve maliyet.** Aşama 0 ve pilot bulut oturumunda 0 €'ya yapılır (iş sınırı 2 saat, boş disk 16 GB; iş
önbellekten sürdürülür). 1b ve sonrası bulut oturumuna sığmaz: ≈ 1–1,5 hafta açık kalacak bir makine ister.

Örnek makine: Hetzner 8 vCPU / 16 GB sınıfı, ayda kabaca 30–60 € (2024–2025 liste fiyatlarından; **doğrulanamadı**).
Saatlik faturalanır, gelen trafik ücretsizdir. Disk: ÇİF deposu ≈ 30 GB (iki bant), ayrıca geçici ham veri. 80 GB
yeter.

| Kalem | Süre | € (30–60 €/ay ile) |
|---|---|---|
| Aşama 0 + pilot | bulut | 0 |
| A (bağlayıcı) | ≈ 1–1,5 hafta | **≈ 7–21 €** |
| B üst sınırı | ≈ 1,5–2 hafta | ≈ 11–28 € |

Beklenen durumda 50 €'nun altındadır. Fiyat doğrulanmadığı için makine kiralama ve harcama **proje sahibinin
kararıdır.** Sunucu ancak G0, P1 ve P2 geçtikten sonra kiralanır. Onay gelmezse ön kayıt dondurulmuş ve 1b'den
önce durmuş olarak kalır.

**5.5 Körlük ve tek koşu.**
- Kod yalnız yapay veriyle geliştirilir ve sınanır (`tr5b_yapay.py` ve `tr5b_yapay2.py` başvurudur). Dosya biçimi
  için yapay miniSEED kullanılır; gerçek istasyon kullanılmaz.
- Gerçek dalga formu ancak kod incelemesinden sonra indirilir. Aşama 0 dalga formu açmaz.
- Ön kayıt, liste, betikler ve koşu kodu commit + push edildikten sonra tek bir komut her aşamayı koşar.
- Olay Δ'ları 6. adımdan önce hiçbir yerde hesaplanmaz, çizilmez, yazdırılmaz. 1b'de olay istasyonlarının yalnız
  doluluk ve enerji istatistikleri yazılır.
- Olay sonrası veri 1b-olay'da indirilir, 8. adımdan önce açılmaz; dosyaları ayrı bir dizinde, sha256 günlüğüyle
  durur.
- **Koşu öncesi düzeltme** yalnız şu durumda yapılır: hata, gerçek veri kullanılmadan, yapay veriyle yeniden
  üretilebilen bir kod hatasıdır ve yeni bir yapay sınamayla gösterilir. §3'teki hiçbir sayısal parametre (bant,
  pencereler, eşikler, ızgara, yığın, maske) değiştirilemez. Düzeltmeden sonra 1–4. adımların hepsi baştan koşulur.
  Önceki sonuçlar silinmez, kayda geçer. 3. ya da 4. adım iki kez başarısız olursa hüküm kesinleşir ("geçersiz (kod
  ya da tasarım)" ya da "güç yok (4. adım: ölçü −%0,1'e kör)").
- 6. adımdan sonra bulunan her hata "koşu sonrası değişiklik" başlığıyla yazılır ve ikinci koşunun kör olmadığı
  belirtilir; hüküm değişmez.
- İndirme başarısızlığı istasyon-pencere düzeyinde kayda geçer. 1b'de başarısız pay %5'i aşarsa, ε hesaplanmadan tek
  bir yeniden deneme turu yapılır.
- **Veri sınırı.** Olaylar T ≤ 2023-12-31. Bütün dalga formu istekleri ≤ 2025-12-31; fiilen en geç istek PK
  penceresinin sonu 2023-03-08 (P2'de 2022-10-18). 2026 hiçbir amaçla sorgulanmaz.
- **Marmara ile temas.** Marmara GNSS'e dokunulmaz. TR-4 kutusunda ve TR-1'in daha geniş kutusunda hiçbir liste
  istasyonu yok (sürüm 1'deki HT.ALN, Ö5 kesişim kuralıyla düştü). P2 iki kutuyu da dışlar.

## 6. Yapay doğrulama ve güç

**6.1 Yapay veri.** Sürüm 1'in E1 ve E2 deneyleri (`tr5b_yapay.py`, tohum 20261112) değişmedi; bağımsız tohumla
yeniden üretildi (İNCELEME-1 D).

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
  %20'si. Ana ölçü kontrollere göre sıra olduğu için ortak küçük bir yanlılık r'yi değiştirmez.
- **Germe kestiricisi küçülme veriyor.** Eklenen −%0,1'in %2–7'si kayboluyor ve kayıp SNR düştükçe büyüyor.
- **[0,80; 1,20] eşiği doğru kodun rahatça geçeceği aralıkta.** En düşük SNR'de bile %1 niceliği 0,92'dir. Eşik
  birim, işaret ya da pencere hatasını (oran ≈ 0, ≈ −1, ≈ 0,5) yakalar.
- **σ_ölçüm küçük.** Yapay σ_ölçüm (0,005–0,018 %) gerçek σ_Δ'nın alt sınırıdır.

**Dondurulmuş diziler (Ö9; `tr5b_yapay2.py donder`, tohum 20261114).** 60 dizi (3 SNR × 20). Başvuru zincirinin
dosyadan geri okunan dizilerdeki oranları: medyan 0,937 / 0,968 / 0,982, en küçük 0,900 / 0,945 / 0,972, en büyük
0,981 / 0,981 / 0,995 (CC₁₀ ≈ 0,5 / 0,7 / 0,9). Üç dizide dosyadan bağımsız yeniden hesap Δ ve oranı birebir verdi.

**E3, pozitif kontrolün geçme olasılığı (sürüm 2 tanımıyla; `tr5b_yapay2.py e3`).** Kurulum: küme başına bir
istasyon; kümenin genliği A'nın 0,5–1,5 katı arasında tekdüze; toparlanma 50 günde yarıya; δ_ko ±%2 ızgarasıyla.
15 küme çekilir (16 PK kümesinden us7000irfb'nin tek istasyonu Z önizlemesinde düşer). Her satır 5 bağımsız havuzdan
(havuz başına 1000 yapay istasyon, 2000 çekiliş) gelir; tabloda havuzlar arası ortalama ve [en küçük; en büyük].
Kaba-ince ızgara aramasının tam ızgarayla eşdeğerliği 60 istasyonda sınandı (en büyük δ_ko farkı 0).

| A (%) | P(PK geçer), CC₁₀ ≈ 0,5, mevsim %0,05 | CC₁₀ ≈ 0,7, mevsim %0,05 | CC₁₀ ≈ 0,5, mevsim %0,10 | δ_ko medyanı (%), CC 0,5 / 0,7 / 0,5-%0,10 |
|---|---|---|---|---|
| 0 | 0,051 [0,042; 0,058] | 0,042 [0,036; 0,053] | 0,043 [0,030; 0,060] | −0,003 / 0,000 / +0,001 |
| 0,02 | 0,167 [0,124; 0,186] | 0,235 [0,216; 0,257] | 0,112 [0,086; 0,169] | −0,013 / −0,013 / −0,009 |
| 0,05 | 0,451 [0,395; 0,516] | 0,738 [0,691; 0,772] | 0,350 [0,290; 0,391] | −0,031 / −0,032 / −0,034 |
| **0,08 (Napa ölçeği)** | **0,795 [0,753; 0,829]** | **0,973 [0,964; 0,980]** | **0,601 [0,530; 0,664]** | −0,055 / −0,052 / −0,051 |
| 0,15 | 0,995 [0,994; 0,996] | 1,000 [1,000; 1,000] | 0,975 [0,963; 0,982] | −0,098 / −0,100 / −0,100 |

Geçerli δ_ko oranı her satırda ≥ 0,973. Sonuç dosyası `tr5b_yapay2_e3_sonuc.json`; süre 32 dk (4 süreç).

Okuma:
- **A = 0'da yanlış geçme ≈ düzey.** Ortalamalar 0,051 / 0,042 / 0,043. En kötü havuz 0,060 (2000 çekilişte Monte
  Carlo standart hatası ≈ 0,005). Fazlalık örnekleme gürültüsü düzeyindedir; düzeltme yapılmaz, §9'da açık madde
  olarak kalır.
- **δ_ko medyanı, A'nın ≈ %65'idir.** Bunun bir kısmı toparlanmadan (50 gün yarı ömürle 30 günlük ortalamada
  ≈ %18 kayıp), bir kısmı germe küçülmesinden gelir; kalan ayrıştırılmadı. Napa ölçeğinde (A %0,08) düşük SNR'de geçme 0,80, yüksek
  mevsimde 0,60'tır. PK geçmediğinde "güç yok" ya da "ayırt edilemez (PK geçmedi)" hükmünün (§4.6) olasılığı bu
  nedenle göz ardı edilemez.

**6.2 Güç ve geçme olasılıkları (`tr5b_guc2.py`, tohum 20261113).** Hüküm olasılıkları §4.4'tedir. Ek sonuçlar:
- **r'nin sd'si.** n_c = 5 için kuramsal √((n+2)/(12n)) = 0,342.
- **N1.** H0 altında yanlış "geçersiz" olasılığı 0,05 (K 31).
- **4. adım (E2 ölçütü) ve S4.** P(üst sınır < 0,5) ve bilgi olarak P(r̄_sahte ≤ 0,25):

  | σ_Δ | %0,05 | %0,075 | %0,1 | %0,15 | %0,2 | %0,3 |
  |---|---|---|---|---|---|---|
  | **4. adım geçer, K 31** | 1,00 | 1,00 | 0,99 | 0,86 | 0,63 | 0,34 |
  | 4. adım geçer, K 28 | 1,00 | 1,00 | 0,99 | 0,83 | 0,59 | 0,31 |
  | 4. adım geçer, K 20 | 1,00 | 1,00 | 0,94 | 0,69 | 0,43 | 0,23 |
  | S4 (r̄_sahte ≤ 0,25), K 31 | 1,00 | 0,95 | 0,60 | 0,11 | 0,03 | 0,00 |
  | ort. r̄_sahte | 0,08 | 0,17 | 0,24 | 0,32 | 0,36 | 0,41 |

- **Pilot P1'in geçme olasılığı** (gerçek σ_Δ verilmişken σ̂_P1 ≤ σ*(K); 24 istasyon, normal Δ; σ̂/σ'nın %10–%90
  aralığı 0,68–1,27):

  | σ_Δ | %0,05 | %0,075 | %0,1 | %0,15 | %0,2 | %0,3 |
  |---|---|---|---|---|---|---|
  | P1 geçer, K 31 | 1,00 | 1,00 | 1,00 | 0,99 | 0,81 | 0,21 |
  | P1 geçer, K 28 | 1,00 | 1,00 | 1,00 | 0,98 | 0,74 | 0,16 |
  | P1 geçer, K 20 | 1,00 | 1,00 | 1,00 | 0,89 | 0,47 | 0,06 |
  | P1 × 4. adım, K 28 (bağımsızlık varsayımıyla, kaba) | 1,00 | 1,00 | 0,99 | 0,81 | 0,44 | 0,05 |

  Okuma: σ_Δ ≤ %0,15 ise pilot ve 4. adım büyük olasılıkla geçer; σ_Δ ≈ %0,3 ise pilot büyük olasılıkla ana
  indirmeden önce durdurur. İki olay aynı σ'ya bağlı olduğu için çarpım yalnız kaba bir kestirimdir.
- **G0'ın geçme olasılığı (varsayımsal; karar vermez).** Kontrol istasyon-pencerelerinin dolu olma olasılığı p_c ve
  olay istasyonlarının üç bileşen ve yeniden yoklamadan sağ çıkma olasılığı q_e bağımsız varsayıldığında
  (`tr5b_ozet_s2.json` → `G0_benzetim_varsayimsal`, 300 çekiliş): (q_e 1,0; p_c 0,4 / 0,6 / 0,8) → P(G0 geçer) 0,61 /
  1,00 / 1,00; (q_e 0,85; p_c 0,4 / 0,6 / 0,8) → 0,16 / 0,81 / 0,93. Ek 1'de olay istasyonlarının ≈ %40'ı ay
  doluluğunu geçmişti; kontrollerde bu oran ölçülmedi. Aşama 0'ın amacı tam olarak bunu 0 €'ya ölçmektir.

## 7. Bilinen karıştırıcılar ve önlemler

| Karıştırıcı | Önlem | Kalan risk |
|---|---|---|
| Mevsimsellik (ısıl, yağış) | Ay eşlemeli Δ (§3.5); aynı epokta kontroller | Yıldan yıla değişen mevsim genliği |
| Çok yıllı hidroloji (kuraklık, yeniden beslenme) | Aynı epokta kontroller; aynı yerde plasebo ve eşleşik d şartı; zaman kaydırma bilgi satırı; her H1'de zorunlu hidroloji cümlesi (§4.3) | **En büyük risk.** Kontrol bunu eşlemez, plasebo yalnız yere özgü çok yıllı yanlılığı yakalar. Kontrol iklim eşlemesi bilerek yapılmadı: yerel çok yıllı kuraklığı eşlemez, havuzu daraltır ve yeni bir serbestlik derecesi getirir. Yağış modeli bilgi satırına bile konmadı (Seher ve Main 2004 dersi) |
| Yakın M ≥ 6 depremlerin düşüş ve toparlanması | Ş1–Ş3 temiz pencere, [T − 5 yıl, T) | Ş1 merkeze göre uygulanır. Denetlendi: pencere başı − 2 yıl ile T − 8 arasında istasyonun 50 km içinde M ≥ 6 olan olay ya da kontrol istasyonu yok; 75 km içinde yalnız NO.JMIC (artık volkanik, ana hükümde değil) |
| Kontrol merkezlerinde eski büyük depremden toparlanma (5–15 yıl önce M ≥ 6,5: kontrol %48, olay %28; sürüm 1 sayımı) | Eşleşik d (plasebo kontrolleri aynı kuralla seçilir); bilgi satırı 18 | Küçük; yönü düşüş (kontrol Δ_c > 0) |
| Yakın M ≥ 5 öncüler ve öteki olaylar | §2.6 maskesi (50 km, 60 gün) | Kuyruk; 50–150 km'deki M5'ler; olay öncesi artan etkinlik (bilgi satırı 16; H1 düşüşte zorunlu not) |
| İstasyon ve aygıt değişimi | §2.5 kuralı, olayda [T − 1095, T + 30]; pencere içinde kanal ve konum kodu sabit | Üstveriye işlenmemiş değişimler (yerleşim, kazı) |
| Saat hatası; bileşen değişimi | SC tek istasyonun bileşenlerini ilişkilendirdiği için saat hatalarına duyarsızdır. Kutup ya da bileşen değişimi (N↔E, işaret) CC'yi düşürür ve günleri geçersiz kılar, yanlılık üretmez | Üstveriye işlenmemiş sensör değişimi |
| Volkanik yerler | GVP Holosen listesi, 25 km, olay ve kontrollere simetrik (§2.7) | 25 km'den uzak magma sistemleri; liste dışı hidrotermal alanlar |
| Gürültü kaynağı değişimi (mevsimsel kaynak yönü) | Beyazlatma, gece saatleri, koda penceresi | Kaynak değişimi germe ölçüsünde sahte dv/v üretebilir (Daskalakis 2016, özetten nitel) |
| 2020 kültürel gürültü kesintisi (Mart–Haziran 2020; yaygın bilinen, doğrulanmadı) | Gece penceresi; olay ve kontrol aynı epokta | Kentsel ve kırsal yerlerde farklı; bilgi satırı 19 |
| Ölçek farkı (olay yerleri daha gürültülü) | İşaretli sıra ölçüsü (§4.1) | H0'da yok (0,053); güç düşer (§4.4 Ö7 satırı) |
| Kontrollerin tekrarı | İstasyon kotası 3 küme, kullanılan kontrollere göre (§2.3) | Ortak kontroller t aralığını biraz daraltır; "bir merkezi dışarıda bırak" bilgi satırı |

## 8. Bilgi satırları (hükmü değiştirmez)

1. GVP volkanik kuralıyla çıkan 6 olay dahil r̄.
2. (Sürüm 2'de kaldırıldı: sürüm 1'in Akutan ve Jan Mayen satırı, 1. satıra katıldı. Numara korunur.)
3. |Δ| sıra ölçüsü (tek yanlı, büyük |Δ|).
4. Eğilimden arındırılmış Δ: A∪B'ye doğrusal + yıllık sinüs uydurulur, C'ye uzatılır.
5. 2–4 Hz bant.
6. Olay ağırlıklı r̄.
7. Yalnız M ≥ 6,5.
8. Yalnız doğrultu atımlı (USGS MT, |rake| ≤ 30° ya da ≥ 150°).
9. Yalnız en yakın istasyonu ≤ 50 km olan olaylar (H0 metninde K'siyle anılır).
10. Δ / σ_i: istasyonun A ve B dilimleri arasındaki ay eşlemeli farkın mutlak değeriyle ölçeklenmiş Δ.
11. Bir kontrol merkezini dışarıda bırakma: en küçük ve en büyük r̄.
12. Olay başına tablo: Δ_e, r, n_c, istasyonlar, maske günleri, geçersiz gün oranı, CC medyanı.
13. PK'de küme başına δ_ko ve medyan; istasyon başına olay sonrası penceresinde reddedilen saat oranı.
14. Aşama 0, pilot ve 1b'de elenen istasyon ve kontrol sayıları, nedenleriyle (`asama0_sonuc.json` → `pencere_neden`).
15. Gerçek σ_Δ: istasyon düzeyi ve kontrol düzeyi σ̂ ayrı (TR-4'ün güç çevirisi için).
16. C diliminde istasyonun 150 km içinde M ≥ 5,0 (derinlik ≤ 70 km) olayı olan olaylar dışarıda bırakılarak r̄. Aynı
    kural kontrollere de uygulanır.
17. Ana tasarıma en yakın alt küme: M ≥ 6,5 ve ≥ 2 dolu yerli olaylar; küme sayısı ve r̄.
18. [T − 15 yıl, T − 5 yıl) içinde 150 km'de M ≥ 6,5 olmayan kontrollerle r̄.
19. C'si 2020-03-01 ile 2020-06-30 arasıyla örtüşen olaylar hariç r̄.

## 9. Zayıf noktalar (ikinci incelemecinin bakması gerekenler)

1. **Çatallanma (§0).** Biçim kapıdan geçtiği için seçildi. Sonuç görülmedi, ama "önceden konmuş" değil.
2. **Kotanın okunuşu (§2.3).** İNCELEME-1 Ö4'ün "kullanılıp kullanılmadığına göre işler" cümlesi dinamik okundu:
   kota yalnız koşuda kullanılan (atanan) adaylara yazılır. Statik okuma (10 adayın hepsi kotaya yazılır) denendi:
   3 olay 3, 3 olay 4 adayla kaldı ve K 29'a indi. Dinamik kural koda bağlıdır ve veri görülmeden sabittir, ama
   ataması aşama 0'ın doluluk sonucuna bağlıdır.
3. **Yatay yoklamanın sertliği.** Altı yatay isteğin hepsinin "var" olması isteniyor (İNCELEME-1 E1 metni). Tek bir
   boş ay pencereyi düşürür. Yatay doluluğu Z ile ilişkili olduğu için gerçek kayıp küçük beklenir; doğrulanmadı.
4. **P1'in birimi.** σ̂_P1 istasyon düzeyindedir, 4. adımın σ_Δ'sı kontrol düzeyindedir. Kural tutucu yöndedir
   (fazla "güç yok"), ama ne kadar tutucu olduğu bilinmiyor.
5. **PK'nin geçme olasılığı.** Gerçek kosismik genliğe ve istasyon uzaklığına bağlıdır. PK kümelerinin en yakın
   istasyonları 6–71 km arasında. E3 yalnız yapay gürültüyle hesaplandı; enerji reddi yapay veride yok. Napa
   ölçeğinde (A %0,08) geçme 0,60–0,97 arasında (§6.1); düşük SNR ve yüksek mevsimde ≈ %40 olasılıkla PK geçmez.
   A = 0'da yanlış geçme 0,051 / 0,042 / 0,043 (en kötü havuz 0,060): düzeyin %5'inin örnekleme gürültüsü
   içinde aşılması kabul edildi; eşik (p ≤ 0,05) değiştirilmedi.
6. **Plasebo şartı gücü yarıya indiriyor.** δ = 0,75 σ_Δ'da ana aralığın gücü 0,93, tam H1'in gücü 0,51. Bu bilerek
   kabul edildi (İNCELEME-1 D: yer yanlılığına karşı tek koruma).
7. **Hidroloji.** Kontrol, yerel çok yıllı kuraklığı eşlemez. H1 çıkarsa ilk rakip açıklama budur; metin bunu
   zorunlu cümleyle söyler.
8. **Doğrulanamayan işleme sayıları.** 10 günlük yığın, CC ≥ 0,40, koda 10–40 sn, 4 saat/gün, enerji reddi 3 kat.
9. **Kontrol bölge eşlemesi yok.** Kontroller aynı epoktadır ama başka iklim ve jeolojidedir.
10. **Olayların çoğunda tek istasyon** (30/39). Tek istasyonun yerel olayları ölçüyü belirler.
11. **Wells–Coppersmith katsayıları bellekten.** PK kümelerinin ve P2 istasyon eşiğinin seçiminde kullanıldı; liste
    sabit olduğu için sonucu değiştirmez.
12. **Hız ve fiyat doğrulanmadı.** Yalnız EarthScope ve KOERI hızı ölçüldü (tek denemeyle). Hetzner fiyatı
    doğrulanmadı.
13. **P2'nin istasyonları** büyük olaylarda uzak düşebiliyor (Sumatra 2005 M8,6: 213 km; Solomon 2007 M8,1: 337 km),
    çünkü eşik 2 L(M) ile büyüyor. Bu uzaklıklarda düşüş beklenmez (Boschelli 2021); P2'nin gücünü azaltır.

## 10. Marmara'ya anlam

Bu sınav Marmara verisi kullanmaz.
- **H1** (yer yanlılığı dışlanmış, PK geçmiş): TR-4'ü anlamlı kılar. Marmara KO ağıyla dv/v izlemesi, TR-4'ün ölçeceği
  gürültü tabanıyla birlikte, ayrı ve ileriye dönük bir ön kayıtla önerilir. O ön kayıt, TR-5b'nin işaretini ve
  büyüklüğünü önceden sabit alır. Bu bir alarm ya da olasılık değildir.
- **H0:** Yıl ölçekli pasif dv/v düzey farkını, bu ölçü ve bu örneklem için öncül olarak kapatır. TR-4 o zaman yalnız
  bir ölçüm sınırı cümlesi üretir ("Marmara'da X %'den küçük değişim görülemez"); alarm adayı olarak önerilmez.
- **Ayırt edilemez, güç yok ya da geçersiz:** Marmara'ya hiçbir şey taşınmaz.

**İstanbul için mutlak olasılık bu belgenin hiçbir yerinde yazılmaz ve hiçbir sonuçtan türetilmez.**

## 11. Yeniden açma şartı

"Güç yok" ya da "ayırt edilemez" ile kapanırsa yeniden açma ancak yeni bir ön kayıtla ve şu yollardan biriyle olur:
- (a) K'yi en az iki katına çıkaran yeni bir açık arşiv; örneğin Japonya Hi-net ya da F-net'e erişim;
- (b) istasyon çiftleriyle CC ve 0,2–0,5 Hz bandı. Bunun için ≥ 2 yer şartı gerekir; TR-5'te bu şart K 8–11 verdi;
- (c) TR-4'ün ölçtüğü σ_Δ'nın, pilot P1'i ve 4. adımı geçecek kadar küçük çıkması (σ_Δ ≲ %0,2);
- (d) "güç yok (pilot P2)" ile kapanırsa: P2'yi başka bant ya da parametreyle deneyen ayrı bir ön kayıt. TR-5b'nin
  olay verisi indirilmemiş olduğu için TR-5b o ön kayıtla kör kalır.

## 12. Defterle örtüşme

- **TR-5 (ata):** Ana tasarım güç yok (K 8–15). TR-5b, Ek 1'deki tek geçen biçimdir. TR-5'in defter kaydı
  "koşuyor" durumunda; ana tasarımın "güç yok (sayım)" ile kapatılması kök oturumun kararıdır.
- **TR-4:** σ_Δ'yı Marmara'da ölçer. TR-5b'nin P1'i ve 4. adımı bu sayıya bağlıdır. TR-5b kontrollerinde KO
  kullanılmadığı için TR-4 ile indirme çakışması yoktur.
- **TR-1 (güç yok):** İskelet ondandır: kontrol merkezleri, SHA sırası, plasebo, eşleşik d, kota. TR-1 inceleme 2'nin
  dersleri uygulandı: kontrol (b) şartı simetrik, kota var ve artık istasyon düzeyinde, (e) 200 km.
- **TR-11, E1:** Pozitif kontrol eşiği yapay veriyle önceden sınandı (§6.1).
- **FA-6 (elendi):** Serbestlik derecesi riski. Tek ana bant (0,5–2 Hz), tek ana ölçü (ay eşlemeli düzey farkı), tek
  sınama (işaretli r̄). Yağış ve ısı modelleri yok. Ötekiler bilgi satırı.
- **DD-5 (gelgit, güç yok):** dv/v'nin gerilme duyarlılığı yalnız sığ bir gelgit kalibrasyonuna dayanır (Hillers
  2014, ≈ 0,5 MPa⁻¹). Δ'nın gerilmeye çevirisi bu sınavda yapılmaz.

## Ek: kümeler, pilot olayları ve komutlar

**PK kümeleri** (16, volkaniksiz; en yakın istasyon ≤ max(30 km, 2 L(M))):
ci38443183, nc72282711, nc73666231, us10006g7d, us10006n6r, us20009ly0, us2000bmhe, us6000jllz, us7000asvb,
us7000d18q, us7000gaqu, us7000irfb, usb000m8ch, usb000r2hc, usp000fuvt, usp000gvtu.
Z önizlemesinde etkilenenler: us7000irfb (tek istasyonu IU.HNR düşer; küme PK'de geçersiz), usb000m8ch (en yakın
HL.VLS düşer, HT.LKD2 kalır), us10006g7d (IV.CAMP düşer, en yakın IV.NRCA kalır), us20009ly0 (KO.BODT yalnız PK'den
düşer, HL.PRK kalır).

**Plasebo eşleşik kümeleri** (16, volkaniksiz): ci38443183, nc72282711, us10004gy9, us10006n6r, us10008mel,
us2000272b, us20002m5s, us20005hzn, us20009ly0, us6000d3zh, us6000jllz, us7000gaqu, us7000imgl, usc000m1w9,
usp000gjgt, usp000gvtu.

**Pilot P2 olayları** (`tr5b_pilot_s2.csv`, sırasıyla): us7000fes8 (Girit 2021, HL.IACM 19 km), us6000f65h (Haiti
2021, CN.LGNH 93 km), us1000cfn6 (Hualien 2018, TW.NACB 12 km), us10003ywp (Lefkada 2015, HT.LKD 6 km), us6000ah9t
(Oaxaca 2020, MU.HUIG 17 km), usp000f83m (Solomon 2007, IU.HNR 337 km), us7000df40 (Tirnavos 2021, HT.TYRN 7 km),
us7000dffl (Yeni Zelanda 2021, NZ.MXZ 102 km), usp000jj3u (Şili 2012, C.ROC1 51 km), ak018aasz24z (Alaska 2018,
TA.C27K 27 km), official20050328160936530_30 (Sumatra 2005, PS.PSI 213 km), us7000eijt (Şili 2021, 3Y.SC01 26 km),
us60007ewc (Elazığ 2020, GE.MALT 57 km), usp000jdvv (Şili 2012, 3A.U40B 29 km), us7000i90q (Tayvan 2022, TW.YULB
29 km), usc000p27i (Iquique 2014, CX.PATCX 45 km), nc71338066 (Eureka 2010, NC.KCT 36 km), usp000fsmf (Tocopilla
2007, CX.PB05 9 km), us60004yps (Şili 2019, C1.BO03 43 km), us1000gc0k (Kosta Rika 2018, OV.PNPB 13 km).

**Komutlar** (girdiler depo dışında):
```
python3 -I -B kayit/turetme/tr5/tr5b_liste_s2.py <tr5/ham> <ngl> <tr2/ham> <tr5b_kat>      # ≈ 20 sn
python3 -I -B kayit/turetme/tr5/tr5b_asama0.py kuru kayit/turetme/tr5/tr5b_liste_s2.json <tr5/ham>   # ağsız
python3 -I -B kayit/turetme/tr5/tr5b_asama0.py ustveri <liste> <ob> 6600 --ag-onay          # aşama 0, bulut
python3 -I -B kayit/turetme/tr5/tr5b_asama0.py kur <liste> <ob>
python3 -I -B kayit/turetme/tr5/tr5b_asama0.py yokla <ob> 6600 --ag-onay                    # 2 iş
python3 -I -B kayit/turetme/tr5/tr5b_asama0.py say <liste> <ob>
python3 -I -B kayit/turetme/tr5/tr5b_guc2.py                                                # ≈ 1 dk
python3 -I -B kayit/turetme/tr5/tr5b_yapay2.py donder <çıktı.npz>                          # ≈ 1 dk
python3 -I -B kayit/turetme/tr5/tr5b_yapay2.py e3                                           # ≈ 1 saat, 4 çekirdek
```

## Sürüm 1 → 2 değişiklik listesi

Her satır İNCELEME-1'in bir bulgusunu ya da yazarın bu sürümdeki bir değişikliğini karşılar. Atlanan bulgu yoktur.

| Bulgu | Değişiklik | Yer |
|---|---|---|
| E1 aşama 0 | Aşama 0 tam metni, kapı G0; betik `tr5b_asama0.py` yazıldı, yalnız `kuru` kipte sınandı (27 410 istek, 1,6–2,9 saat, 2 iş) | §5.1, §4.2 adım 0 |
| E1 pilot | P1 ve P2 tam metni; P2 olay listesi koddan üretildi (20 olay); hacim ≈ 0,12 TB, bulutta 3–7 iş | §5.1 |
| E1 1b sırası | 1b-olay (0,23 TB) önce, kapı "güç yok (1b, olay tarafı)", sonra kontroller | §5.1, §5.2 |
| E2 | 4. adım: −%0,1 kalır, ölçüt "%95 üst sınırı < 0,5"; eski ölçüt S4 bilgi; geçme olasılıkları K 31 / 28 / 20 ile yeniden hesaplandı | §4.2 adım 4, §6.2 |
| E3a | PK penceresinde enerji reddi medyanı [T + 1, T + 30]'un kendi medyanı; reddedilen saat oranı bilgi satırı 13 | §3.2, §4.2 adım 8 |
| E3b | PK'de germe ızgarası ±%2 | §3.4 |
| E3c | Aygıt kuralı olayda [T − 1095, T + 30]; `aygit_degisimi_PK` alanı; KO.BODT örneği | §2.5 |
| E3d | E3, 5 havuz × 1000 istasyon, A = 0 satırı, mevsim %0,10 satırı, havuzlar arası aralık | §6.1 |
| E3 ek öneri | Olay δ_ko en yakın geçerli istasyondan | §4.2 adım 8 |
| E3e | "ayırt edilemez (PK geçmedi)" etiketi | §4.2 adım 8, §4.6 |
| Ö1 | 1b dolu tanımına ≥ 9 ay yığın şartı ve maskesiz payda; 6a K₆, K_p6 | §5.1, §4.2 adım 6 |
| Ö2 | Koşu öncesi düzeltme kuralı; parametre değişmez; iki başarısızlıkta hüküm kesin | §5.5 |
| Ö3 | GVP Holosen listesi indirildi ve donduruldu (1214 volkan, sha256 `be852348…`); kural (f) olay ve kontrollere; liste yeniden üretildi; 6 olay çıktı, K 37 → 31 | §2.3, §2.7 |
| Ö4 | Kota istasyon düzeyinde, kullanılan kontrollere göre (dinamik; `kota_ata`); (e) 200 km ve ortak istasyon yasağı | §2.3, §9 madde 2 |
| Ö5 | Plasebo istasyonu = olay istasyonu ∩ plasebo kapsamı; d_k tanımı; usb000r2hc düştü | §2.4 |
| Ö6 | Her H1'e zorunlu hidroloji cümlesi; r̄_kay notu; iklim eşlemesi yapılmamasının gerekçesi §7'de | §4.2 adım 9, §4.3, §7 |
| Ö7 | "İstasyon çevresi, ortanca 50 km" metni; σ_Δ birimi; olay gürültüsü 1,5 kat satırı | §1, §3.6, §4.3, §4.4 |
| Ö8 | Bilgi satırı 16; H1 düşüşte öncü etkinliği notu | §8, §4.2 adım 9 |
| Ö9 | Yapay ÇİF'ler dondurularak `tr5b_yapay_ccf.npz`'ye yazıldı (3 SNR × 20, float16, 631 MB, sha256 `44189a31…`); dizi başına tolerans | §4.2 adım 1, §6.1 |
| K1 | Çatallanma cümlesi ve bilgi satırı 17 | §0, §8 |
| K2 | H0 sınırının gerekçesi; ±0,10 ile H0 olasılığı hesaplandı: 0,025 (İNCELEME-1'in kaba ≈ 0,2 kestirimi yerine) | §4.2 adım 9 |
| K3 | Gün tanımı (yerel ortalama güneş tarihi) | §3.1 |
| K4 | Kanal ve konum kodu pencereyi üç bileşenle kapsayanlardan; aşama 0 seçilen konum koduyla | §3.1, §5.1 |
| K5 | §7'ye toparlanma satırı; bilgi satırı 18 | §7, §8 |
| K6 | Saat hatasına duyarsızlık ve bileşen değişimi §7'de; M ≥ 6 istasyon denetimi §7'de | §7 |
| K7 | 2. adım havuzlanmış medyan; 0. adım ≥ 4 / ≥ 3 ilişkisi; K_p tanımı; hacim tablosu tekrarsız kalemlerle yeniden yazıldı | §4.2, §5.2 |
| K8 | EarthScope POST, 30 günlük paket; süre tablosu yeniden | §5.1, §5.3 |
| K9 | 2020 bilgi satırı 19; §7 satırı | §7, §8 |
| K10 | Literatür tablosuna De Plaen 2016, Feng 2021, Yates 2018, GJI 2023, Obermann 2016 ve Hobiger 2016 toparlanması eklendi; değişiklik gerektiren tek parametre PK ızgarasıydı (E3b) | §3.7 |
| K11 | Değişiklik gerekmiyor; gerekçe cümlesi §3.5'e eklendi | §3.5 |
| K12 | Ö3 ile karşılandı; §2.7 ve §8 satır 1–2 yeniden yazıldı | §2.7, §8 |
| D | Değişiklik gerekmiyor; sürüm 1 sayıları bağımsız tohumla yeniden üretilmişti | – |
| Yazar 1 | P2 istasyonuna volkanik kural (> 25 km) ve KOERI/6G dışlaması eklendi (Ö3 simetrisi; KOERI hızı) | §5.1 |
| Yazar 2 | Hüküm adlarının kapalı listesi ve kalıpları tek tabloda; "ayırt edilemez (plasebo kümesi < 10)" adı eklendi (Ö1'in "K_p6 < 10 ise H1 ilan edilemez" kuralının adı) | §4.6 |
| Yazar 3 | Öncelik sırası (§0); sürüm 1 belgesi `_surum1.md` olarak korundu | §0 |
| Yazar 4 | Aşama 0'ın "hepsi dolu" önizlemesi ve G0 için varsayımsal doluluk benzetimi | §2.3, §6.2 |

**Dosyalar ve sha256'lar.** Sürüm 1 dosyaları değiştirilmedi ve silinmedi:

| Sürüm 1 dosyası | sha256 | Sürüm 2 karşılığı | sha256 |
|---|---|---|---|
| `TR-5b_sismik-hiz-oncul_ONKAYIT.md` (şimdi `_surum1.md`) | `2d7649a35f7d4c2d842191cd0b90340dde1e0cf5b821119d1c28be6fa8b42f80` | bu belge | – |
| `tr5b_liste.py` | `bde395c4456809a2fb6612701e2971c25d984f52555a69e7aca2f8837e8f5409` | `tr5b_liste_s2.py` | `1e4e418d5bb89991b484f2b0f7b2564328bfdee2b3d19a42b86f20ce8e8b4ca1` |
| `tr5b_liste.json` | `581b0ccabc400083bbc58c68c23be878988fbcc3f74b4ba44ddbf4a1aacaacfb` | `tr5b_liste_s2.json` | `a3a6a45a97d9e6a625f3aa6157093cda75b2190a026740573369d64bd46e8763` |
| `tr5b_olaylar.csv` | `3e44c96fa41ad341564c11ef4ebcccd1243dc81ebc6784986a78d109b68bdf99` | `tr5b_olaylar_s2.csv` | `8e2f908c7f846f190f11b49b98504018ebf200333dd7d54b74e8c9a6dd814140` |
| `tr5b_kontroller.csv` | `245d496968327a245bea158481cd41a61cf7ebe44e770f94b4c72a6e5e3f217b` | `tr5b_kontroller_s2.csv` | `00e489e72f322d933d4a76bcb0d7f9740f45360c6c1ade0403da860846a8065a` |
| `tr5b_ozet.json` | `6e59060f294d469b0649cff5d050b468b8bf386a7afe4076ab73a470d8d30ab7` | `tr5b_ozet_s2.json` | `217d6d74555ba8cf2702fab3750265b787e52fd118c32554e0754e5c196a0bf2` |
| `tr5b_guc.py` | `be4fa04cec346b95b8e3679eaaa193a50d275c4771ab5fed5e86078cd257815c` | `tr5b_guc2.py` | `69c8a096c485bd1d25a131757c342095900dbd66d413bb714b532c24de903de5` |
| `tr5b_guc_sonuc.json` | `ab13c9d45dcf02f9bd2e035e0649a69a4f10f9a832ba2809207a35e19e1234a2` | `tr5b_guc2_sonuc.json` | `40eea7ca202c97a7390079dbe0f87203a3363e5455e8f685b715e0710175607c` |
| `tr5b_yapay.py` | `70e8fbaba4b01753798b03976d261101cef30e7d9ea44dcf874b443de7b6c024` | (değişmedi) + `tr5b_yapay2.py` | `785690b0fbe7d6cb758c62607c603b448afa65167c5b1a282053e1a374822fbf` |
| `tr5b_yapay_sonuc.json` | `b8495bde85d131e9a344527938c96cb884e9b3cd5a7371473b799764fc8277d2` | `tr5b_yapay2_e3_sonuc.json`, `tr5b_yapay_ccf_ref.json` | `ed24793333b6c06b16d69e17a2ea19063bf3cb22cc15244f5b3b8e3594facaa5`; `36339a46ac3ac75423573852ec5e0677a425d1da951e732dee52123a02580e5c` |
| – | – | `tr5b_asama0.py` | `d01781962d217988bf70607920a776b91fc303b07ea655cf4a78e75c64e236c5` |
| – | – | `tr5b_asama0_kuru.json` | `5a782a84fbb44ce31bec71bce0b6a343feed86eea4fac987fb6a44908fae6330` |
| – | – | `tr5b_pilot_s2.csv` | `f36cfe746d736d4ef1b13ece33963be3b52621af97daa8dc570f70f57ad04ec9` |
| – | – | `tr5b_gvp_holosen.csv` | `be85234874a1a85a1610552f67348b3ea1ac29ff24417575cbe92f57f145f25d` |
