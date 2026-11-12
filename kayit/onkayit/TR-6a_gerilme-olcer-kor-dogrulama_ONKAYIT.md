# TR-6a ön kaydı: hız-durum gerilme ölçeri bilinen kosismik Coulomb gölgelerini kör olarak doğru işaretle buluyor mu?

Tarih: 12 Kasım 2026. Durum: **TASLAK sürüm 1, incelemeye hazır.** Dondurulmadı. İnceleme bulguları işlendikten sonra
"DONDURULDU" başlığıyla commit edilir; ondan sonra metin değişmez, ekler ayrı başlıkla yazılır.
Türediği yer: `kayit/onkayit/TR-6_SAYIM.md` (tasarım §2.1, sayım §4, Ek 1: Aσ ve katalog kapısı).
Sayıların kaynağı: `kayit/turetme/tr6/tr6a_onkayit_sayilar.py` → `tr6a_onkayit_sayilar.json` ve dondurulan aday
listesi `tr6a_olay_listesi.json`. Bu belgedeki her sayı bu iki dosyadan ya da Ek 1 çıktısı `tr6_a_kapi.json`'dan
alınmıştır; tablolar `python3 -I -B kayit/turetme/tr6/tr6a_onkayit_sayilar.py --md` çıktısından yapıştırıldı.
Maliyet: 0 €. Kör veri: hüküm verisi (olay sonrası katalog) hiçbir amaçla sorgulanmadı; bütün sorgular 2025-12-31'de
biter; Türkiye dışı 2026 kör verisine dokunulmaz.

**Körlük beyanı (yazar).** Bu taslak yazılırken hiçbir olay sonrası katalog sorgusu yapılmadı, hiçbir lobda oran ya da
oran değişimi hesaplanmadı, hiçbir ΔCFF hesaplanmadı. Görülen veri yalnız Ek 1'in olay öncesi sayımları, halka Mc'leri,
küme listesi ve ComCat mekanizma sınıflarıdır. Yazar literatürden üç kümenin sonucunu kısmen biliyor: Kumamoto 2016 ve
Ridgecrest 2019'da gölge loblarında artçı bulunduğunu (Hardebeck & Harris 2025) ve Tohoku 2011 sonrası nominal gölgede
yaygın artış görüldüğünü (Toda vd. 2011). §3.4'teki kırığa uzaklık sınırı bu bilgiyle yazıldı; yönü H1 lehinedir ve
§7'deki D3a satırı bunu ölçer.

## 0. Tek cümlelik soru ve hüküm satırı

Sismisite oranı değişiminden gerilme değişimi çıkaran Dieterich (1994) hız-durum gerilme ölçeri, sonlu fay modellerinden
hesaplanan kosismik Coulomb gölge loblarında (ΔCFF ≤ −10 kPa) olay sonrası 1 yılda oran düşüşünü, bağımsız kümelerin
rastlantıdan anlamlı biçimde fazlasında buluyor mu? Hüküm satırı: K bağımsız kümede "düşüş oyu" sayısı X, tek yanlı kesin
binom (p = 0,5'e karşı, α 0,05), Aσ = 19 kPa ile sayılan güç kapısından geçen kümelerde (§5, §6).

## 1. Soru, neden ve neyi ölçmediği

TR-6 bir olasılık terimi değil, bir ölçü doğrulamasıdır. Hız-durum modeli ters çevrildiğinde sismisite oranı değişimi
gerilme değişimine çevrilir: Δτ_est = Aσ ln(R_son / R_on). Marmara'da (b ayağı) bu ölçü 1 yılda 15–37 kPa/yıl'ın
altını göremiyor (TR-6_SAYIM §6, GEÇMEZ). (a) ayağı daha temel bir soruyu sorar: ölçü, gerilmesi bağımsız olarak bilinen
yerlerde en azından işareti doğru buluyor mu? Bilinen gerilme olarak kosismik Coulomb değişimi kullanılır; bu "bilinen"
değer bir modeldir (§11).

Bu sınav yalnız **gölge tarafını** hükme bağlar. Artış tarafı (pozitif lob) bilinen ve kolay taraftır: artçılar oradadır.
Bu yüzden artış tarafı yalnız hattın çalıştığını gösteren pozitif kontroldür. Gölge tarafı tartışmalıdır (§2).

Ölçülmeyenler:
- Gerilme büyüklüğü hükme girmez; yalnız işaret. Büyüklük (Δτ_est) bilgi satırıdır.
- Aσ'nın kendisi sınanmaz. Oy (§4.3) Aσ'ya bağlı değildir; Aσ yalnız hangi kümenin "ölçülebilir" olduğunu (güç kapısı)
  belirler.
- Büyük deprem olasılığına çeviri yoktur. İstanbul için mutlak olasılık bu belgede ve sonuçta yazılmaz.

## 2. Rakip açıklamalar ve önceki bulgular

Doğrulama türleri: **ö** sayı ya da sav OpenAlex özetinde okundu (bu belgede, 12 Kasım); **S** TR-6_SAYIM'da
doğrulandı, bu belgede yeniden okunmadı; **d** doğrulanamadı.

| Bulgu | Yön | Kaynak | Doğr. |
|---|---|---|---|
| Landers ve Kobe sonrası oran değişimi çözülebilen hemen her yerde ARTTI, ΔCFF işaretinden bağımsız; oran düşüşleri güvenilir biçimde çözülemedi | gölge yok | Mallman & Zoback 2007, 10.1029/2005jb004076 | ö |
| Loma Prieta, Landers, Northridge, Hector Mine: "zaman oranı" sınamasıyla gölge yok (Loma Prieta ve Landers için en az %98 güven) | gölge yok | Felzer & Brodsky 2005, 10.1029/2004jb003277 | ö |
| Kaliforniya'da kısa zaman ölçeğinde (≤ 100 gün) tetiklenme yaygın, sessizleşme seyrek; oran değişimi kestiricisinin kısa ölçekte artış lehine doğal yanlılığı var | gölge seyrek | Marsan 2003, 10.1029/2002jb001946 | ö |
| Chi-Chi 1999: dört lobda 50 ay süren, istatistikçe anlamlı %40–90 oran düşüşü; doğrultu atımlı alıcılarla hesaplanan gölgelerle çakışıyor; uzun, düşük Mc'li, yüksek oranlı katalog gerekiyor | gölge var | Ma vd. 2005, 10.1029/2004jb003389 | ö |
| Tohoku 2011: iç Japonya'da 425 km'ye dek geniş artış; 15 bölgeden 11'inde ΔCFF ile pozitif, 3'ünde negatif ilişki; "nominal gölgede" küçük, farklı yönlü faylar varsa sismisite artabilir | karışık | Toda vd. 2011, 10.1029/2011gl047834 | ö |
| Kumamoto ve Ridgecrest'te gölge artçılarının yarısı Coulomb modeliyle açıklanamıyor | gölgede artış | Hardebeck & Harris 2025 | S |
| Kayma modeli belirsizliği: farklı yayımlanmış modellerden ΔCFF'nin standart sapması mutlak değeri kadar (CV ≈ 1); Aσ ≈ 17 kPa | gölgeyi bulandırır | Hainzl vd. 2009, 10.1029/2008jb006011 | ö |
| Hız-durum parametreleri (Aσ, gerilme hızı, arka plan oranı) güçlü ilişkili | döngüsellik uyarısı | Cocco vd. 2010, 10.1029/2009jb006838 | ö |

Rakip açıklamalar ve sınav öncesi güven (yazarın notu; K ≥ 23 koşuluyla):
- **R1, gerilme ölçer işareti buluyor** (gölgede oran düşer, rastlantıdan fazla): 0,20.
- **R2, gölge küresel ölçekte görünmez** (dinamik tetiklenme, konum hatası, kayma modeli belirsizliği, küçük faylar
  gölgeyi siler; oy olasılığı ≈ 0,5): 0,50.
- **R3, gölgede bile artış baskın** (Hardebeck & Harris 2025 ve Mallman & Zoback 2007'nin küresel karşılığı): 0,30.

R2 ile R3 bu sınavda kısmen ayrılır (§6.2 ters yön satırı); R1'in olumsuzu ise iki açıklamayı ayıramaz: gerilme ölçer
mi, Coulomb modeli mi başarısız (§6.3).

## 3. Veri, tanımlar ve dondurulan liste

### 3.1 Havuz ve aday listesi

Havuz `tr6_a_sayim.json`'daki 155 olaydır: USGS ComCat'te `finite-fault` ürünü olan, 1990-01-01–2025-12-31, M ≥ 6,0,
derinlik ≤ 30 km. Dondurulan liste `kayit/turetme/tr6/tr6a_olay_listesi.json`, **sha256
01d73cad5b75bf818d200cf2b9d13614eb77fcb200ac819d135d8b10a3828765**. Liste olay sonrası hiçbir bilgi taşımaz. Satır
başına: kimlik, zaman, M, dış merkez, L, Ek 1 halkası, son pencere bitişi, tarih kuralı, Ek 1'de Mc'si kestirilebilen
kataloglar (Mc ve kaba N0 ile), Ek 1 en iyi katalog, Ek 1 küme numarası, ComCat mekanizma sınıfı, olay grubu, koşu
adaylığı. Girdi dosyalarının sha256'sı listenin içinde yazılı (`tr6_a_sayim.json` 8da8ba3c…a7684, `tr6_a_kapi.json`
5a90b0eb…aedee22). Ek 1 ham önbelleği: `/mnt/project-files/turetme/tr6a-ham/tr6a_onbellek_2026-11-12.tar.gz`, sha256
f350d2e091be2d82b4026db03262a8eecbdb732aad26bf328a23224c9ced0d60 (bu belgede yeniden doğrulandı).

**Tarih kuralı (karar 5).** Son pencere [t0 + 30 g, t0 + 365 g) 2025-12-31T23:59:59'u aşan olay listeden çıkar. Koddan
sayım: havuzda **7 olay** çıkar (us6000pi9w 2025-01-07, us7000pcdl 2025-02-08, us7000pn9s 2025-03-28, us7000pntq
2025-03-30, us7000pwkn 2025-05-02, us7000qx2g 2025-09-18, us6000rsy1 2025-12-06). Bunların 4'ünün zaten kataloğu yoktu.
Ek 1'in kaba kapısında (Aσ 19 kPa) 2 olay düşer (us7000qx2g, us6000rsy1): 48 olay / 39 küme → **46 olay / 37 küme**.
Aσ 13 kPa'da 57/46 → 55/44; Aσ 39 kPa'da 12/11 değişmez.

**Katalog kuralı.** Ek 1'de hiçbir açık katalogda halka Mc'si kestirilemeyen 69 olay (3 örnek pencerede 20'den az olay)
koşuya girmez. Gerekçe: kapıdan geçmek için gölge lobunda 5 yılda en az 155 kümesizleştirilmiş olay gerekir (§4.2).
Koşu adayı: **83 olay** (86 kataloglu − 3 tarih dışı). Bunların 71'inin son penceresi 2023-12-31'den önce biter (§7 D6).

### 3.2 Olay grubu (çift ve öncü)

Havuzdan zincirle 30 gün ve 300 km içinde kalan olaylar tek **olay grubu**dur. Grubun t0'ı en erken üyenin zamanıdır;
ΔCFF bütün üyelerin sonlu fay modellerinin toplamıdır (doğrusal üst üste binme); L, halka ve alıcı düzlem kuralı en büyük
M'li üyeden alınır. Dört çok üyeli grup var: Santa Cruz Adaları 2013 (usc000f1s0, usc000f40j), Iquique 2014
(usc000nzvd, usc000p27i), Nepal 2015 (us20002926, us20002ejl), Kahramanmaraş 2023 (us6000jllz, us6000jlqa). Havuz
dışındaki öncüler (ör. Ridgecrest 2019 M 6,4) toplanmaz (§11). Bundan sonra "olay" olay grubu demektir.

### 3.3 Gerilme kaynağı ve ΔCFF

- **Sonlu fay modeli.** Her üyenin ComCat `finite-fault` ürünündeki alt fay dosyası (alt fay konumu, derinliği,
  doğrultu, eğim, kayma, rake, boyutlar). Birden çok sürüm varsa ComCat'in tercihli (ilk listelenen) ürünü. Dosya
  sha256'sı manifeste yazılır.
- **Okada (1992) yarı uzayı**, numpy ile yazılan DC3D eşdeğeri. μ = 30 GPa, ν = 0,25 (α = 2/3). Hesap derinliği
  **7,5 km**. Etkin sürtünme **μ' = 0,4**. ΔCFF = Δτ (alıcı rake yönünde kayma gerilmesi) + μ' Δσ_n (Δσ_n çekme
  pozitif). Birim kPa.
- **Doğrulama (kod geliştirmede, koşudan önce).** Okada 1992'nin sonlu dikdörtgen kaynak sınama satırları (doğrultu,
  eğim ve açılma kaynakları; yer değiştirme ve türevleri) 5 anlamlı basamakta tutmalı. Tablo değerleri yayımlanmış
  makaleden ya da açık bir kopyasından sınama dosyasına elle yazılır ve kaynağı dosyada belirtilir. Değerler okunamazsa
  karşılaştırma Okada'nın açık DC3D kaynak kodunun çıktısıyla yapılır ve kayda "Okada 1992 tablo değerleri
  doğrulanamadı" diye geçer. Ek sınamalar: uzak alanda nokta kaynak sınırı; dikey doğrultu atımlı kaynakta King vd.
  (1994) dört lob işaret deseni.
- **Izgara.** Dış merkezde ortalanmış azimutal eşit uzaklık izdüşümünde 10 km hücre; hücre merkezinde ΔCFF.

**Alıcı düzlem (karar 6, Ek 1 E1.5).**
1. ComCat'ten halkada (dış merkezden [L/2 + 10 km, 2L]), derinlik 0–40 km, [1976-01-01, t0) aralığında `moment-tensor`
   ürünü olan olaylar. Her olayın tercihli tensörü (Mrr, Mtt, Mpp, Mrt, Mrp, Mtp) skaler momentine bölünür
   (M0 = √(ΣMij²/2)).
2. En az 5 tensör varsa altı bileşenin ayrı ayrı medyanı alınır; medyan tensörün özvektörlerinden iki düğüm düzlemi
   çıkarılır. Alıcı, normali sonlu fay modelinin moment ağırlıklı ortalama düzlem normaline en yakın (|n·n_ff| en büyük)
   düğüm düzlemidir; rake o düzlemin rake'idir.
3. 5'ten az tensör varsa alıcı ana şok düzlemidir: sonlu fay modelinin moment ağırlıklı ortalama doğrultu ve eğimi,
   moment ağırlıklı vektör ortalaması rake.
Her olay için alıcının kaynağı (medyan / ana şok) ve tensör sayısı manifeste yazılır. Duyarlılık D5: iki düğüm düzlemi
birlikte (§7).

### 3.4 Loblar ve kırığa uzaklık (karar 7)

- **Kırık izi.** Kayması en büyük alt fay kaymasının %10'u ve üstü olan alt fay dikdörtgenlerinin yüzey izdüşümü, en çok
  2 km aralıklı nokta örneklemesiyle. **r_k** = hücre merkezinin bu nokta kümesine yatay uzaklığı.
- **Bölge:** 20 km ≤ r_k ≤ 2L (L, en büyük üyenin M'sinden Wells–Coppersmith, `tr6_a_sayim.py` ile aynı:
  L = 10^(−3,55 + 0,74 M) km).
- **Gölge lobu:** bölgede ΔCFF ≤ −10 kPa olan hücrelerin birleşimi. **Pozitif lob:** ΔCFF ≥ +10 kPa. Arası atılır.
- **Gerekçe.** 20 km iç sınır, küresel kataloglardaki konum hatasını (≈ 5–15 km) ve kayma modelinin geometri hatasını
  aşar; kırık üzerindeki ve kenarındaki doğrudan artçı bulutunu dışarıda bırakır. Bu seçim yakın alan gölge artçılarını
  da (Hardebeck & Harris 2025) dışarıda bırakır; yönü H1 lehinedir. D3a (5 km) ve D3b (40 km) satırları bunu ölçer.
- Megathrust olaylarında kırık izdüşümü büyük olduğu için gölgenin önemli bir kısmı (kırığın üstü) dışarıda kalır;
  bunun K'ye etkisi bilinmiyor (§10, §11).

### 3.5 Katalog, büyüklük ve tamlık

- **Olay seçimi:** bölgede, derinlik ≤ 40 km, tür deprem (`tr6_a_kapi.fdsn_ayristir` ile aynı süzgeç). **Büyüklük türü
  boş olan satırlar atılır.** Gerekçe: Ek 1'de ComCat'in 2012 Hint Okyanusu satırında büyüklüğü eksik olaylar "0" diye
  yazılıyor ve en sık kutu olarak Mc'yi 0,2'ye çekti (önbellekte doğrulandı; `tr6a_onkayit_sayilar.json`
  `supheli_dusuk_mc`). Bu kural Ek 1'in o satırını geçersiz kılar; olay ISC ile (Mc 4,0, kaba N0 111) yine kapıya
  yakındır.
- **Katalog seçimi (yalnız olay öncesi veriyle).** Olayın Ek 1'de Mc'si kestirilebilen her kataloğu için (listede
  `ek1_kataloglar`) gölge lobunun kapı N0'ı (§4.2) hesaplanır; en büyük N0'ı veren katalog seçilir. Eşitlikte sıra ISC, ComCat,
  GeoNet, EMSC, KOERI. Seçim manifeste yazılır; olay sonrası veri yalnız seçilen katalogdan indirilir.
- **Sorgu:** dış merkezden R = 2L + (kırık izinin dış merkeze en uzak noktasının uzaklığı) yarıçaplı daire (bölgeyi
  kapsar), minmagnitude = Mc_halka − 0,05 (Mc_halka = o kataloğun Ek 1 Mc'si), yıllık parçalar; bölge süzgeci yerelde.
  Olay sonrası sorgu da aynı daire ve aynı taban büyüklükle yapılır.
- **MAXC:** `tr6_a_kapi.maxc` ile aynı (0,1 kutu, en sık kutu; eşitlikte küçük olan).
- **Mc_lob** (her lob için ayrı, yalnız olay öncesi): max(Mc_halka, MAXC(lobun ön penceresindeki olaylar) + 0,2).
  Kapıdan geçen her lobda en az 155 olay olduğu için MAXC her zaman tanımlıdır; 50'den az olayda Mc_lob = Mc_halka + 0,3
  (bu durumda lob zaten kapıdan geçemez).
- **Ana şok sonrası tamlık.** (i) Son pencere t0 + 30 günde başlar; ilk 30 gün yalnız kümesizleştirmede ana olay olarak
  kullanılır. (ii) **Mc_son** = MAXC(bölgenin bütün hücrelerindeki [t0 + 30 g, t0 + 365 g) olayları) + 0,2; 50'den az
  olayda Mc_son = Mc_lob + 0,3. Bölge geneli Mc kullanılır, çünkü lobun kendi son pencere sayısı hükmün kendisidir;
  bölge sayısı işaret bilgisi taşımaz ve yakın alandaki tamlık kaybını en çok gösteren yerdir (tutucu).
  (iii) **Mc_kul** = max(Mc_lob, Mc_son). Hem ön hem son pencere sayımı Mc_kul ile yapılır.
- **Negatif kontrolde** aynı kural, simetrik: Mc_son yerine [t0 − 365 g, t0 − 30 g) bölge olaylarının MAXC + 0,2'si.

### 3.6 Kümesizleştirme

`tr6_sayim.kumesizlestir` ile aynı Gardner–Knopoff (1974) pencere yöntemi: d = 10^(0,1238 M + 0,983) km;
t = 10^(0,032 M + 2,7389) gün (M ≥ 6,5), 10^(0,5409 M − 0,547) gün (M < 6,5); büyükten küçüğe, önce ve sonra
pencereli; bağımlı olay ana olay olamaz.
- Her lob ayrı kümesizleştirilir. **Yalnız o lobun içindeki olaylar** (Mc_kul üstü) ana olay ve bağımlı olabilir. Ana şok ve lob dışındaki olaylar ana olay
  olamaz. Gerekçe: ana şokun GK penceresi (M 7'de ≈ 70 km, ≈ 2,5 yıl) bütün lobu silerdi; yakın alandaki büyük artçıları
  ana olay saymak da son pencereyi asimetrik olarak boşaltır ve gölgede H1 lehine yanlılık yaratır.
- **Pencereler ayrı ayrı kümesizleştirilir:** ön katalog [t0 − 1826 g, t0 − 30 g); son katalog [t0, t0 + 365 g)
  (ilk 30 günün lob içi olayları ana olay olabilir, sayılmaz). Kapı yalnız ön kataloğun kümesizleştirmesiyle sayılır;
  hiçbir son pencere olayı ön sayıyı değiştiremez.
- Duyarlılık D4: kümesizleştirme yok (iki pencere ham).

### 3.7 Bağımsızlık, küme ve temsilci

- Kapıdan geçen olaylar `tr6_a_kapi.kumele` ile kümelenir (zaman sıralı, ilk uyan kümeye ekleme; 300 km dış merkez ve
  1826 gün). Bu, Ek 1 ile aynı fonksiyondur; tek bağlantılı kümelemeyle aynı değildir (manifest, tek bağlantıda
  birleşecek küme çiftlerinin sayısını yazar).
- **Temsilci:** kümenin zamanca ilk olayı. Bir kümenin tek oyu temsilcisinin oyudur. Kümenin sonraki olayları,
  temsilcinin son penceresine düşüyorsa onun "yanıtının" parçasıdır; lob içindeyseler kümesizleştirmede ana olay olurlar.
- Manifest bayrağı (bilgi): temsilcinin [t0, t0 + 365 g) penceresinde ve 2L içinde havuzdan başka bir olay.

## 4. Ölçü

### 4.1 Sayılar

Bir olay ve bir lob için: n_on = ön penceredeki [t0 − 1826 g, t0 − 30 g) kümesizleştirilmiş Mc_kul üstü lob olayı;
T_on = 1796 g. n_son = [t0 + 30 g, t0 + 365 g) penceresindeki kümesizleştirilmiş Mc_kul üstü lob olayı; T_son = 335 g.
n = n_on + n_son.

### 4.2 Ölçülebilirlik kapısı (karar 2 ve 7; Ek 1 ile aynı kural)

Gölge lobunun ön penceresinde, **Mc_lob** ile ve yalnız ön kataloğun kümesizleştirmesiyle: **N0 = n_on / (1796/365,25)
≥ 31,36 olay/yıl** (yani n_on ≥ 155). Eşik, Aσ = 19 kPa'da Δτ = −10 kPa'lık adımın 1 yılda %80 güçle (tek yanlı
α 0,05) görülmesi için gereken orandır: N0 ≥ [(z_α + z_β √k)/(1 − k)]², k = e^(−10/19) (`tr6_a_kapi.gereken_n0`).
Duyarlılık eşikleri: Aσ 13 kPa → 17,08; Aσ 39 kPa → 111,21. Aσ veriden kestirilmez (karar 1).

K = kapıdan geçen olayların bağımsız küme sayısı. Kapı yalnız olay öncesi veriyle sayılır ve manifestte dondurulur.

### 4.3 Oy: koşullu binom ortanca kuralı

H0 (oran değişmedi) altında, n verildiğinde n_son ~ Binom(n, π), **π = T_son / (T_on + T_son) = 335/2131 = 0,15720**.
F(·; n, π) bu dağılımın birikimli fonksiyonu.
- **Düşüş oyu** D = 1 ⟺ n ≥ 1 ve F(n_son; n, π) ≤ 0,5.
- **Artış oyu** A = 1 ⟺ n ≥ 1 ve P(Binom(n, π) ≥ n_son) ≤ 0,5.
- n = 0 ise iki oy da 0'dır; küme K'de kalır (payda değişmez).
H0 altında her n için P(D = 1) ≤ 0,5 ve P(A = 1) ≤ 0,5 tanım gereğidir; bilinmeyen arka plan oranına bağlı değildir.
Negatif kontrolde aynı kural, π_nk = 335 / (1461 + 335) = 0,18653.

**Neden saf oran karşılaştırması değil.** "n_son/T_son < n_on/T_on" oyu, Poisson çarpıklığı yüzünden H0 altında düşüş
yönüne kayar: N0 = 31,36'da P = 0,5088 (kesin hesap). Bununla K = 23'te gerçek α 0,0554 olurdu (> 0,05). Koşullu oyla
H0 altında P(D = 1) = **0,4585** (N0 31,36), 0,4459 (17,08), 0,4783 (111,2); P(A = 1) = 0,4606 (31,36). 200 000
denemelik Monte Carlo denetimi 0,4582. Sonuç: hüküm kuralının (p = 0,5'e karşı binom) gerçek α'sı N0 ≈ 31'de K = 23 için
0,019, K = 39 için 0,007; yani kural tutucudur. Marsan (2003) kısa ölçekli oran değişimi kestiricilerinde başka yönlü
bir küçük sayı yanlılığı bildiriyor; iki durumda da ders aynıdır: oy kuralı H0 altında kesin olarak hesaplanmalıdır.

### 4.4 Büyüklük ölçeri (bilgi)

Δτ_est = Aσ · ln[(n_son / T_son) / (n_on / T_on)], T yıl, Aσ = 19 kPa (13 ve 39 ayrıca). n_son = 0'da −∞ yazılır;
özetler medyanla verilir. Bu, T ≪ t_a sınırındaki kaba ölçerdir; yapay sınamada (§4.5) gerilme hızının bilinmemesi
yüzünden sıfıra doğru yanlıdır.

### 4.5 Yapay Dieterich sınaması (karar 8, eşiklerin önceden denetimi)

Dieterich (1994) adım yanıtı R(t)/r = 1 / [(e^(−Δτ/Aσ) − 1) e^(−t/t_a) + 1], t_a = Aσ/τ̇0; [30 g, 365 g) integrali
kesin; n_on ve n_son bağımsız Poisson; oy olasılığı kesin toplamla. Aσ = 19 kPa, Δτ = ∓10 kPa.

| τ̇0 (t_a) | Gölge düşüş oyu, N0 31,36 / 50 / 111,2 | Pozitif artış oyu, N0 31,36 | Δτ_est medyanı (q10, q90), N0 31,36; beklenen | p = 0,75 için gereken "doğru lob" payı |
|---|---|---|---|---|
| kalıcı adım (t_a → ∞) | 0,987 / 0,998 / 1,000 | 0,997 | −10,23 (−17,16, −4,38); −10,00 | 0,55 |
| 2 kPa/yıl (9,5 yıl) | 0,984 / 0,997 / 1,000 | 0,995 | −9,73 (−16,49, −4,05); −9,57 | 0,56 |
| 10 kPa/yıl (1,9 yıl) | 0,964 / 0,990 / 1,000 | 0,972 | −8,13 (−14,62, −2,66); −7,99 | 0,58 |
| 50 kPa/yıl (0,38 yıl) | 0,771 / 0,839 / 0,939 | 0,734 | −3,43 (−9,25, 1,58); −3,39 | 0,93 |

"Doğru lob payı" f: f · P_D + (1 − f) · 0,4585 = 0,75. Okuma: kapıdan geçen bir lob gerçekten −10 kPa görmüşse oy
neredeyse kesin tutar; tasarım p₁ = 0,75, kümelerin yaklaşık %55–58'inde lobun doğru yerde olduğu (geri kalanında
oyun rastlantı düzeyinde kaldığı) dünyaya karşılık gelir. Yüksek gerilme hızlı bölgelerde (t_a ≈ 0,4 yıl) gölge 1 yılda
büyük ölçüde toparlanır ve tasarım gücü ancak lobların hemen hepsi doğruysa tutar.

## 5. Kapılar ve sıraları

Kapılar bu sırayla, otomatik uygulanır. Bir kapı kapanırsa sonrakiler koşulmaz.

1. **Veri kapısı (manifest, yalnız olay öncesi).** Her koşu adayı için sonlu fay dosyası indirilebilir ve okunabilir
   olmalı; okunamayan olay "veri yok" diye düşer (sayısı yazılır). Ön katalog indirmeleri tamamlanmalı (ComCat sayım
   servisi yerine olay satırı; sunucu kesmesinde Ek 1'deki yeniden deneme kuralı).
2. **Güç kapısı (manifest, yalnız olay öncesi).** K sayılır (§4.2, Aσ 19 kPa).
   - **K < 23:** hüküm satırı koşulmaz; olay sonrası katalog **indirilmez**. Hüküm **"güç yok"**. Aday elenmez.
     Manifestteki olay öncesi satırlar (negatif kontrol dahil) bilgi olarak yayımlanır.
   - **23 ≤ K < 28 (testere dişi):** aşağıdaki tablo uygulanır.
   - **K ≥ 28:** bütün kümeler kullanılır. K = 28–200 için güç 0,8'in altına hiç düşmüyor (koddan denetlendi).
3. **Kod denetimi (yapay veri, koşudan önce; §9).**
4. **Hüküm satırı ve kontroller (tek koşu).**

**Testere dişinin çözümü (karar 2).** Tek yanlı tam binom, p₀ = 0,5, p₁ = 0,75, α 0,05:

| K (kapıdan geçen) | Kritik (X ≥) | Gerçek α | Güç (p₁ 0,75) | Kural | Hükmün K'si | Güç sonra |
|---|---|---|---|---|---|---|
| 23 | 16 | 0,0466 | 0,804 | olduğu gibi | 23 | 0,804 |
| 24 | 17 | 0,0320 | 0,766 | en zayıf 1 küme atılır | 23 | 0,804 |
| 25 | 18 | 0,0216 | 0,727 | en zayıf 2 küme atılır | 23 | 0,804 |
| 26 | 18 | 0,0378 | 0,820 | olduğu gibi | 26 | 0,820 |
| 27 | 19 | 0,0261 | 0,786 | en zayıf 1 küme atılır | 26 | 0,820 |
| ≥ 28 | tablo §6.1 | | ≥ 0,83 | olduğu gibi | K | |

- **"En zayıf" tanımı:** temsilcinin kapı N0'ı (gölge lobu, Mc_lob, ön pencere) en küçük olan küme; eşitlikte olay
  kimliğinin sözlük sırasında sonra geleni. Bu sıralama yalnız olay öncesi veriye dayanır ve manifestte yazılır.
- **Gerekçe.** (i) Kritik değer kesikli olduğu için K = 24, 25 ve 27'de gerçek α 0,05'in çok altına iner ve güç düşer;
  K'yi bir alt "dişe" indirmek gücü tasarım düzeyine geri getirir. (ii) Atılan kümeler en az olay öncesi sayıya sahip
  olanlardır: oyları en gürültülü olanlardır (H0'da P(D) 0,5'ten en uzak, H1'de en düşük). Atmak kalan kümelerin
  ortalama oy olasılığını düşürmez. (iii) "Zayıf" etiketi alternatifi hüküm adını sonradan yorumlanabilir kılardı;
  atma kuralı hükmü tek anlamlı tutar. (iv) Atılan kümeler kaybolmaz: "K tam" bilgi satırı (§7 B1) bütün kümelerle,
  kendi kritik değeriyle yazılır; hükmü değiştirmez.

## 6. Hüküm satırı (tek)

Birim: bağımsız küme (temsilcinin gölge lobu). X = düşüş oyu sayısı, Y = artış oyu sayısı (gölge lobunda), K =
§5'teki hükmün K'si. Payda her zaman K'dir.

### 6.1 Eşikler (koddan)

- **H1 (gölge işareti bulunuyor):** X ≥ c(K), c: P(X ≥ c | K, 0,5) ≤ 0,05 olan en küçük c.
- **H0 (büyük etki yok):** X ≤ h(K), h: P(X ≤ h | K, 0,75) ≤ 0,05 olan en büyük h.
- **Ayırt edilemez:** h < X < c.
- **Ters yön notu:** Y ≥ c(K) (gölgede anlamlı artış). Not, H0 ya da ayırt edilemez hükmünün yanına düşülür. Y, X'ten
  ayrı bir sayımdır; H0 altında P(A = 1) ≤ 0,5 olduğu için aynı c(K) eşiği tutucudur.
- **Güç yok:** K < 23 (§5).

| K | H1: X ≥ c | P(X ≥ c \| 0,5) | güç P(X ≥ c \| 0,75) | H0: X ≤ h | P(X ≤ h \| 0,75) | ters yön: X ≤ t | P(X ≤ t \| 0,5) |
|---|---|---|---|---|---|---|---|
| 23 | 16 | 0,0466 | 0,804 | 13 | 0,0408 | 7 | 0,0466 |
| 24 | 17 | 0,0320 | 0,766 | 13 | 0,0213 | 7 | 0,0320 |
| 25 | 18 | 0,0216 | 0,727 | 14 | 0,0297 | 7 | 0,0216 |
| 26 | 18 | 0,0378 | 0,820 | 15 | 0,0401 | 8 | 0,0378 |
| 27 | 19 | 0,0261 | 0,786 | 15 | 0,0216 | 8 | 0,0261 |
| 28 | 19 | 0,0436 | 0,862 | 16 | 0,0294 | 9 | 0,0436 |
| 29 | 20 | 0,0307 | 0,834 | 17 | 0,0390 | 9 | 0,0307 |
| 30 | 20 | 0,0494 | 0,894 | 17 | 0,0216 | 10 | 0,0494 |
| 31 | 21 | 0,0354 | 0,872 | 18 | 0,0289 | 10 | 0,0354 |
| 32 | 22 | 0,0251 | 0,846 | 19 | 0,0378 | 10 | 0,0251 |
| 33 | 22 | 0,0401 | 0,901 | 20 | 0,0484 | 11 | 0,0401 |
| 34 | 23 | 0,0288 | 0,881 | 20 | 0,0281 | 11 | 0,0288 |
| 35 | 23 | 0,0448 | 0,924 | 21 | 0,0363 | 12 | 0,0448 |
| 36 | 24 | 0,0326 | 0,908 | 22 | 0,0461 | 12 | 0,0326 |
| 37 | 24 | 0,0494 | 0,942 | 22 | 0,0272 | 13 | 0,0494 |
| 38 | 25 | 0,0365 | 0,929 | 23 | 0,0348 | 13 | 0,0365 |
| 39 | 26 | 0,0266 | 0,914 | 24 | 0,0439 | 13 | 0,0266 |
| 40 | 26 | 0,0403 | 0,946 | 24 | 0,0262 | 14 | 0,0403 |
| 41 | 27 | 0,0298 | 0,933 | 25 | 0,0333 | 14 | 0,0298 |
| 42 | 27 | 0,0442 | 0,958 | 26 | 0,0416 | 15 | 0,0442 |
| 43 | 28 | 0,0330 | 0,949 | 26 | 0,0252 | 15 | 0,0330 |
| 44 | 28 | 0,0481 | 0,968 | 27 | 0,0318 | 16 | 0,0481 |
| 45 | 29 | 0,0362 | 0,961 | 28 | 0,0395 | 16 | 0,0362 |

"Ters yön: X ≤ t" sütunu yalnız bilgi içindir (tablo bütünlüğü); ters yön notu Y ≥ c(K) ile verilir, çünkü koşullu oyda
H0 altında P(D) < 0,5 olduğundan X ≤ t sınaması tutucu değildir. K > 45 için eşikler aynı fonksiyonla
(`tr6a_onkayit_sayilar.esikler`) hesaplanır; JSON'da K = 15–60 var.

**Önceden hesaplanan hüküm olasılıkları** (P(H1) / P(ayırt edilemez) / P(H0); gerçek küme başına oy olasılığı p):

| K | p = 0,45 | p = 0,50 | p = 0,55 | p = 0,60 | p = 0,65 | p = 0,70 | p = 0,75 |
|---|---|---|---|---|---|---|---|
| 23 | 0,01 / 0,08 / 0,91 | 0,05 / 0,16 / 0,80 | 0,12 / 0,25 / 0,64 | 0,24 / 0,32 / 0,44 | 0,41 / 0,33 / 0,26 | 0,62 / 0,26 / 0,12 | 0,80 / 0,16 / 0,04 |
| 26 | 0,01 / 0,06 / 0,93 | 0,04 / 0,13 / 0,84 | 0,10 / 0,22 / 0,68 | 0,23 / 0,30 / 0,48 | 0,41 / 0,31 / 0,28 | 0,63 / 0,25 / 0,12 | 0,82 / 0,14 / 0,04 |
| 28 | 0,01 / 0,06 / 0,93 | 0,04 / 0,13 / 0,83 | 0,12 / 0,22 / 0,66 | 0,26 / 0,29 / 0,45 | 0,46 / 0,29 / 0,25 | 0,68 / 0,21 / 0,10 | 0,86 / 0,11 / 0,03 |
| 30 | 0,01 / 0,06 / 0,93 | 0,05 / 0,13 / 0,82 | 0,14 / 0,22 / 0,64 | 0,29 / 0,29 / 0,42 | 0,51 / 0,27 / 0,22 | 0,73 / 0,18 / 0,08 | 0,89 / 0,08 / 0,02 |
| 33 | 0,01 / 0,01 / 0,98 | 0,04 / 0,04 / 0,92 | 0,12 / 0,09 / 0,79 | 0,28 / 0,13 / 0,59 | 0,50 / 0,14 / 0,36 | 0,73 / 0,10 / 0,16 | 0,90 / 0,05 / 0,05 |
| 37 | 0,01 / 0,01 / 0,97 | 0,05 / 0,04 / 0,91 | 0,15 / 0,09 / 0,76 | 0,34 / 0,13 / 0,54 | 0,58 / 0,13 / 0,29 | 0,81 / 0,08 / 0,11 | 0,94 / 0,03 / 0,03 |

Bu sınav yalnız büyük etkiyi (p ≈ 0,75) görür. "H0" yalnız "p ≥ 0,75 bu örneklemle dışlandı" demektir; küçük bir gölge
etkisinin yokluğu demek değildir. H0 altında koşullu oyun p'si ≈ 0,46'dır (§4.3); tablodaki p = 0,45 satırı o dünyaya
yakındır.

### 6.2 Yorum kuralları (hükmü değiştirmez, adını niteler; sırayla uygulanır)

1. **Pozitif kontrol (§7 S1) tutmazsa** (X⁺ < c(K)): H1 hükmü **"ayırt edilemez (pozitif kontrol tutmadı)"** diye
   yazılır. H0 ya da ayırt edilemez hükmüne "pozitif kontrol de tutmadı: hat ya da model başarısız; ayrılamaz" eklenir.
2. **Negatif kontrol (§7 S2):** H1 hükmü verilmiş ve X_nk ≥ c(K) ise (son yıl öncesinde de anlamlı düşüş), hüküm
   **"H1, olay öncesi eğilimle ayırt edilemez"** diye yazılır ve §13'e hiçbir şey taşınmaz. H0 ya da ters yön notu ve
   Y_nk ≥ c(K) ise, "olay öncesi artış eğilimiyle ayırt edilemez" eklenir.
3. **Megathrust ağırlığı:** H1 ve megathrust hariç satırda (S4) X_S4/K_S4 ≤ 0,5 ise, hüküm "H1 (megathrust kümelerine
   dayanıyor)" diye adlandırılır.
4. **Sağlamlık cümlesi:** D1–D7 satırlarından X/K ≤ 0,5 olanlar adıyla listelenir. Liste hükmü değiştirmez.
5. **Türkiye kümeleri** (1999 İzmit, 2020 Sisam, 2023 Kahramanmaraş, hangisi K'deyse) yalnız anılır; hiçbir Marmara
   cümlesine dayanak olmaz.

### 6.3 Hüküm cümleleri (kalıplar)

- **H1:** "Kosismik Coulomb gölge loblarında (ΔCFF ≤ −10 kPa, kırıktan 20 km–2L) olay sonrası [30 g, 365 g) oran
  düşüşü K bağımsız kümenin X'inde görüldü (kritik c; tek yanlı kesin binom p = …). Hız-durum gerilme ölçeri bu
  örneklemde gölgelerin işaretini rastlantı düzeyinin üstünde buluyor. Bu, yöntemin işaret düzeyinde geçerliliğidir;
  Marmara'da kullanılabilirliği göstermez ((b) ayağı çözünürlük kapısını geçmedi)."
- **H0:** "Gölge loblarında düşüş oyu K kümenin X'inde (X ≤ h). Küme başına 0,75 ve üstü oy olasılığı bu örneklemle
  dışlandı. Bu sonuç iki açıklamayı ayıramaz: (i) hız-durum gerilme ölçeri (Aσ 19 kPa) gölgeyi 1 yılda göremiyor,
  (ii) Coulomb modelinin gölgesi (tek sonlu fay modeli, tek alıcı düzlem, μ' 0,4, 7,5 km) yanlış yerde ya da gerçek
  değil." Ters yön notu düşüldüyse eklenir: "Gölgede anlamlı artış (Y ≥ c): Hardebeck & Harris (2025) bulgusunun
  küresel karşılığı; aynı iki açıklama burada da ayrılmaz."
- **Ayırt edilemez:** "X = …, h < X < c. Bu örneklem p ≈ 0,5 ile p ≈ 0,75'i ayıramıyor." Olumsuz sonuçtaki iki
  açıklama cümlesi bu kalıba da eklenir.
- **Güç yok:** "Lob Mc'siyle olay öncesi sayılan bağımsız küme K = … < 23. Hüküm satırı koşulmadı, olay sonrası veri
  indirilmedi. Aday elenmedi; yeniden açma şartı §14."

## 7. İkincil satırlar (zorunlu; hükmü değiştirmez)

Her satırda: K_satır, X, Y, X/K, c(K_satır), p = 0,5'e karşı tek yanlı kesin binom p (üst kuyruk, X için; ayrıca Y
için), koşullu kesin Poisson-binom p (bilgi; küme başına p₀ᵢ = F(b*(nᵢ); nᵢ, π)). Testere dişi atması yalnız ana
satırda yapılır; ikincil satırlar kendi K'leriyle yazılır.

| Satır | Tanım | Kapı / küme seti |
|---|---|---|
| **S1 pozitif kontrol** | Aynı K temsilcinin pozitif lobu (ΔCFF ≥ +10 kPa), kendi Mc_lob'u, artış oyu X⁺. Pozitif hücresi ya da olayı olmayan küme oy 0 alır (sayısı yazılır). Başarı ölçütü X⁺ ≥ c(K). | ana K |
| **S2 negatif kontrol (zaman ters çevrimi)** | Aynı K temsilci, aynı gölge lobu, aynı kümesizleştirilmiş ön katalog; "ön" [t0 − 1826 g, t0 − 365 g), "son" [t0 − 365 g, t0 − 30 g), π_nk 0,18653, Mc §3.5. X_nk ve Y_nk; iki kuyruk ayrı. Tamamen olay öncesi veridir; manifestte, olay sonrası indirmeden önce hesaplanır ve commit edilir. | ana K |
| **S3 doğrultu atımlı alt küme** | Temsilci grubunun en büyük üyesinin ComCat mekanizması "doğrultu atımlı". Ek 1'de 12 küme; yalnız bilgi. | ana K'nin alt kümesi |
| **S4 megathrust hariç** | "ters, düşük eğimli (megathrust dahil)" sınıfı çıkarılır. | ana K'nin alt kümesi |
| **S5a, S5b Aσ 13 / 39 kPa** | Kapı eşiği 17,08 / 111,21; kapı, kümeleme ve temsilci yeniden; oylar aynı kuralla. | kendi K'si |
| **S6 ikinci kayma modeli (SRCMOD)** | SRCMOD'da grubun her üyesi için model varsa en son yayımlanan (eşitlikte SRCMOD listesindeki ilk); ΔCFF, loblar, Mc ve oy aynı kuralla. Ayrıca hücre uyuşma payı (iki modelde aynı sınıfta olan hücre / ComCat modelinde gölge ya da pozitif sınıftaki hücre) ve aynı alt kümede ComCat oyu. SRCMOD erişilemezse "koşulamadı". | ana K'nin SRCMOD'lu alt kümesi, kapı yeniden |
| D1 Mc + 0,5 | Mc_kul + 0,5 (iki pencere); kapı yeniden. | kendi K'si |
| D2 geç pencere | Son pencere [t0 + 90 g, t0 + 365 g), π = 275/2071. | ana K |
| D3a, D3b iç sınır | r_k ≥ 5 km ve r_k ≥ 40 km; loblar ve kapı yeniden. | kendi K'si |
| D4 kümesizleştirme yok | Ön ve son pencere ham; kapı yeniden. | kendi K'si |
| D5 iki düğüm düzlemi | Hücre yalnız iki düğüm düzleminde aynı sınıftaysa (ikisi ≤ −10 ya da ikisi ≥ +10 kPa) loba girer; kapı yeniden. | kendi K'si |
| D6 gözden geçirilmiş bülten | Son penceresi 2023-12-31'den sonra biten temsilciler çıkarılır (sabit varsayım; ISC'nin gerçek sınırı okunmaz). Koşu adaylarının 12'si bu durumda. | ana K'nin alt kümesi |
| D7 temiz ön pencere | Bölgede ön pencerede M ≥ 6,0 (Mc_kul süzgeçsiz, aynı katalog) olan temsilciler çıkarılır. | ana K'nin alt kümesi |
| B1 K tam | Testere dişi atması yapılmadan bütün kapı kümeleri; kendi c(K)'si. Yalnız ana K atma yaptıysa. | kapı K'si |
| B2 büyüklük | Gölge ve pozitif lobda Δτ_est medyanı (Aσ 13 / 19 / 39); pozitif lobda Spearman(lob ortalama ΔCFF, Δτ_est). | ana K |
| B3 bağımlılık bayrakları | Temsilcinin son penceresinde 2L içinde havuz olayı olan kümelerde X/K; tek bağlantıda birleşecek küme çifti sayısı. | ana K |

## 8. Çıktı tablosu (kalıp)

`tr6a_sonuc.md` aşağıdaki tabloyu ve §6.3'teki kalıplardan biriyle hüküm cümlesini taşır; `tr6a_sonuc.json` aynı
sayıları ve girdi dosyalarının sha256'larını taşır.

| Satır | K | X (düşüş) | Y (artış) | X/K | c(K) | p (X, üst kuyruk, p₀ 0,5) | p (Y) | koşullu p (bilgi) | Hüküm / etiket |
|---|---|---|---|---|---|---|---|---|---|
| Ana (gölge, Aσ 19) | | | | | | | | | H1 / H0 / ayırt edilemez / güç yok |
| S1 pozitif kontrol | | X⁺ | | | | | | | tuttu / tutmadı |
| S2 negatif kontrol | | X_nk | Y_nk | | | | | | eğilim yok / düşüş / artış |
| S3 … D7, B1 | | | | | | | | | — |

Ek tablolar: küme başına satır (küme, temsilci, grup üyeleri, katalog, Mc_halka, Mc_lob, Mc_son, Mc_kul, gölge ve
pozitif lob hücre sayısı, n_on, n_son, D, A, Δτ_est, alıcı kaynağı, mekanizma sınıfı, bayraklar); atılan kümeler.

## 9. Koşu sırası ve körlük

1. Bu taslak incelenir, bulgular işlenir, metin "DONDURULDU" diye commit + push edilir. Dondurulan dosyalar:
   bu metin, `tr6a_olay_listesi.json` (sha256 yukarıda), `tr6a_onkayit_sayilar.py` ve `.json`.
2. **Kod yalnız yapay veriyle geliştirilir** (`kayit/turetme/tr6/`, yalnız numpy ve standart kitaplık,
   `python3 -I -B`):
   - `tr6a_okada.py` ve sınaması (§3.3);
   - yapay katalog sınaması: bilinen bir yapay sonlu fay, bilinen Aσ = 19 kPa ve τ̇0 ile Dieterich oran yanıtı, arka
     planda Poisson + GK tipi ikincil diziler; bütün hat (lob, Mc, kümesizleştirme, oy) çalıştırılır. Ölçütler:
     Δτ = 0 dünyasında gölge düşüş oyu oranı §4.3'teki kesin değerle (N0 31,36'da 0,4585) 3 standart hata içinde;
     kalıcı −10 kPa dünyasında 0,987 ile 3 standart hata içinde; Δτ_est medyanı §4.5 tablosuyla 3 standart hata içinde;
   - ana şok sonrası tamlık kaybı sınaması: yapay kataloğa Mc(t) = M_ana − 4,5 − 0,75 log10(t / 1 gün) (Helmstetter
     vd. 2006 biçimi; bu sabitler sınama için seçildi, doğrulanmadı) uygulanır; Δτ = 0 dünyasında §3.5 kuralıyla gölge
     düşüş oyu oranı 0,4585 + 0,02'yi aşmamalı. Aşarsa kural koşudan önce değiştirilmez; durum "tamlık kuralı yapay
     sınamada yetersiz" diye kayda geçer ve D2 satırı ana satırla birlikte hükme eşlik eder (hükmü değiştirmez).
3. **Manifest (yalnız olay öncesi veri):** `tr6a_manifest.py` → `tr6a_manifest.json` + `tr6a_on_ham_sha256.txt`.
   İçerik: her aday için sonlu fay dosyası ve sha256'sı, alıcı, lob hücre sayıları, katalog seçimi, Mc_halka, Mc_lob,
   kapı N0'ı (gölge ve pozitif; Aσ 13/19/39 ve D1, D3a, D3b, D4, D5 eşikleri), olay grupları, kümeler, temsilciler, K,
   testere dişi atma listesi, bayraklar ve **S2 negatif kontrolün sonucu**. Manifest hiçbir olay sonrası veri içermez.
   Ham ön indirmeler `/mnt/project-files/turetme/tr6a-ham/` altına arşivlenir. Manifest commit edilir. K < 23 ise burada
   durulur (§5).
4. **Kod incelemesi** (bağımsız), olay sonrası veri indirilmeden önce. Gerçek veride yalnız manifest koşulmuş olur.
5. **Olay sonrası katalog bir kez indirilir:** manifestteki bütün kapı kümelerinin (bütün satırların birleşimi) seçilen
   kataloğundan [t0, t0 + 365 g) bölge olayları ve [t0 + 30 g, t0 + 365 g) Mc_son sorgusu. Hiçbir sorgu
   2025-12-31'i aşmaz. Ham yanıtlar arşivlenir, `tr6a_son_ham_sha256.txt` commit edilir.
6. **Tek koşu:** `tr6a_kosu.py` manifesti, ham listeleri ve kendi sha256'sını doğrular; sonuç dosyalarını bellekte
   üretip birlikte yazar; var olan çıktının üzerine yazmaz. Çıktı ne olursa olsun yazılır. Koşudan sonra tanım, eşik,
   manifest ya da küme kuralı değişmez. Koşu bir istisnayla durursa yalnız istisnanın doğrudan nedeni düzeltilir ve fark
   kayda geçer; herhangi bir oy ya da X görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik" başlığında
   yazılır.

Bugüne dek hiçbir lobda oran hesaplanmadı. Ek 1 kaba kapısının küme listesi Ek A'da bilgi olarak verildi; bağlayıcı
küme listesi manifesttir.

## 10. Önceden beyan edilen beklenti

- **K.** Ek 1'in kaba kapısı (lob payı 0,25 varsayımı) tarih kuralından sonra 37 küme veriyor. Gerçek lob tanımı
  (§3.4) megathrust olaylarında gölgenin büyük kısmını (kırığın üstü) dışarıda bırakır; Ek 1 kümelerinin 20/39'u
  megathrust'tır. Lob Mc'si ve Mc_son ayrıca sayıyı düşürür. Yazarın önseli: **P(K < 23) ≈ 0,5**.
- **K ≥ 23 ise küme başına oy olasılığı p ≈ 0,50–0,60** (§2'deki literatürün çoğu gölgeyi bulamıyor; Ma vd. 2005
  bulduğu yerde uzun, düşük Mc'li katalog vardı). Bu beklentiyle §6.1 tablosundan (K = 23–30): **P(H1) ≈ 0,05–0,25,
  P(ayırt edilemez) ≈ 0,15–0,30, P(H0) ≈ 0,45–0,80.** §2'deki önsellerle (0,20 / 0,50 / 0,30) tutarlı.
- **Pozitif kontrol** büyük olasılıkla tutar (yapay dünyada 0,97–1,00; gerçek veride artçılar 20 km ötesinde de
  baskın). Tutmazsa hat ya da model ciddi biçimde bozuktur.
- **Negatif kontrol:** ISC'nin son iki yılı ve ağ yoğunlaşması yüzünden hafif bir düşüş ya da artış eğilimi
  beklenebilir; yönü önceden bilinmiyor.
- **En olası sonuç:** "güç yok" ya da "H0 / ayırt edilemez, iki açıklama ayrılamaz". Bu sonuçların kayda geçmesi
  sınavın amacıdır.

## 11. Bilinen zayıflıklar

1. **ISC büyüklük türleri karışık** (JMA M, ML, mb, Ms aynı sütunda). MAXC karışık türler üzerinde hesaplanır; bölgede
   tür bileşimi zamanla değişirse oran değişimi büyüklük türü değişiminden ayrışmaz.
2. **ISC'nin son iki yılı gözden geçirilmemiş bülten.** 2024–2025 son pencereleri daha az ajans katkısı taşıyabilir:
   olay sonrası sayı düşer ve gölgede H1 lehine sahte düşüş üretir. Bölge geneli Mc_son bunu kısmen yakalar; D6 satırı
   ölçer. 2023-12-31 sınırı sabit bir varsayımdır, ISC'den okunmadı.
3. **Lob Mc'si.** Loblar çoğunlukla açık denizde; MAXC, sorgu tabanı Mc_halka − 0,05 ile kesildiği için Mc_lob'u ancak
   yukarı itebilir (tutucu). 5 yıllık ön pencerede ağ değişimi (Mc'nin zamanla düşmesi) ön oranı şişirmez ama Mc_lob'u
   pencerenin en kötü dönemine kilitlemez; MAXC havuzlanmış pencereden alınır. Negatif kontrol bu tür eğilimleri ölçer.
4. **Megathrust ağırlığı.** Ek 1 kümelerinin 20/39'u düşük eğimli ters faylanma. Alıcılar 7,5 km'de, sismisite 0–40 km;
   megathrust gölgesinin derinlikle işaret değiştirdiği yerler var. S4 ve yorum kuralı 3 bunu adlandırır; derinlik
   duyarlılığı (ör. 15 km) bu sürümde yok.
5. **Kayma modeli belirsizliği.** ΔCFF'nin CV'si ≈ 1 (Hainzl vd. 2009). Tek ComCat modeli; SRCMOD erişimi ve kapsamı bu
   belgede doğrulanmadı (S6 koşulamayabilir).
6. **Coulomb sadeleştirmeleri.** Tek alıcı düzlem, sabit μ' 0,4, sabit derinlik, gözenek basıncı ve poroelastik etki
   yok, artkayma yok, dinamik tetiklenme yok. Dinamik tetiklenme ve konum hatası gölgeyi "artış"a iter (H1 aleyhine).
7. **Ana şok sonrası tamlık.** Tamlık kaybı gölgede H1 lehine sahte düşüş üretir. Önlem: ilk 30 gün dışarıda, bölge
   geneli Mc_son, D1 ve D2 satırları ve §9 adım 2'deki yapay sınama. Gerçek kayıp bölgeden bölgeye değişir.
8. **Kümesizleştirme yalnız lob içi.** Lob dışındaki büyük bir artçının loba taşan dizisi ayıklanmaz (H1 aleyhine);
   önceki büyük bir olayın sönen dizisi ön oranı şişirir (H1 lehine). Negatif kontrol ve D7 ikincisini ölçer.
9. **Havuz seçimi.** ComCat sonlu fay ürünü olan olaylar büyük ve iyi çalışılmış olaylardır; 1990'lar seyrek.
10. **Ek 1 hatası.** 2012 Hint Okyanusu satırında ComCat Mc'si 0,2 (eksik büyüklükler "0" yazılmış); bu belgede
    bulundu ve §3.5 kuralıyla düzeltildi. Ek 1'in kaba K'si bu olayı yine de doğru tarafa koyar (ISC N0 111).
11. **Havuz dışı öncü ve çiftler** (Ridgecrest M 6,4 gibi) ΔCFF'ye girmez.
12. **Koşullu oy tutucu:** gerçek α N0 ≈ 31'de 0,007–0,019. Bu, tasarım gücünü değiştirmez (p₁ oy olasılığı
    üzerinden tanımlı) ama H0 dünyasında X'i 0,5K'nin biraz altına çeker; H0 hükmünü hafifçe kolaylaştırır.
13. **Aσ yalnız kapıda.** Oy Aσ'dan bağımsızdır; bu yüzden sınav "hız-durum ölçerinin Aσ = 19 kPa ile kalibre
    edilmiş hâlini" değil, ölçerin işaret düzeyindeki çıktısını sınar. Δτ_est büyüklüğü t_a bilinmediği için sıfıra
    doğru yanlıdır (§4.5).
14. **Kümeleme ilk-uyan sırayla** (Ek 1 ile aynı), tek bağlantı değil.
15. **Yazarın literatür bilgisi** (körlük beyanı): iç sınır 20 km yakın alan gölge artçılarını dışarıda bırakır; D3a
    satırı ve sağlamlık cümlesi bunu görünür kılar.

## 12. Defterle örtüşme

- **CRS-ETAS** (Marmara kısa vade CRS + ETAS, ayırt edilemez) ve **KURESEL-CRS-GELGIT** (küresel hatta CRS katmanı
  kısa vadede ETAS üstüne ≈ 0, H0): aynı fizik (Coulomb + Dieterich). TR-6a ileri tahmin puanı değil işaret geri
  kazanımı ölçer, ama aynı model zincirini kullanır. **Bağımsız doğrulama sayılmaz:** H1 çıkarsa bu iki kapalı adayı
  yeniden açmaz; H0 çıkarsa onların sonucuyla aynı yönde ek bir bulgu olarak anılır, "üçüncü bağımsız kanıt" diye
  sayılmaz.
- **M7-D1D4** (KAF Coulomb, katkı vermedi): aynı fizik, farklı ölçü; örtüşme orta.
- **TR-6 (b)** Marmara çözünürlüğü GEÇMEDİ; TR-6a sonucu bunu değiştirmez.
- **ETAS-TABAN, AV-2, TR-11, TR-4:** TR-6_SAYIM §7'deki gibi; değişiklik yok.

## 13. Marmara ve İstanbul'a bağ

- H1 (yorum kurallarından geçmiş hâliyle) çıkarsa Marmara'ya taşınan tek cümle: "sismisite oranından gerilme işareti
  çıkaran hız-durum ölçeri, küresel kosismik gölgelerde işaret düzeyinde geçerli." Bu, Marmara'da kullanılabilirlik
  değildir: (b) ayağının 1 yıllık çözünürlüğü beklenen sinyalin 2,4–82 katı (TR-6_SAYIM §6).
- H0, ayırt edilemez ya da güç yok çıkarsa Marmara'ya hiçbir şey taşınmaz.
- İstanbul için mutlak olasılık, olasılık çarpanı ya da tarih bu sınavdan hiçbir durumda yazılmaz.

## 14. Yeniden açma şartı

- **Güç yok:** lob Mc'siyle olay öncesi sayılan K ≥ 23 sağlayan yeni bir açık katalog (ör. JMA birleşik hiposantr
  dosyalarının doğrudan kullanımı, Şili CSN toplu erişimi) ya da ISC'nin gözden geçirilmiş bülteni genişledikçe aynı
  kurallarla yeniden sayım. Kurallar bu metindekilerdir; yalnız katalog listesi değişir ve önceden yazılır.
- **H0 ya da ayırt edilemez:** (i) en az iki bağımsız kayma modelinin lob sınıfında ≥ %80 hücre uyuşması olan en az
  28 küme (Coulomb tarafının belirsizliğini daraltan bir sınav), ya da (ii) 2026 ve sonrası olaylar, olay sonrası
  pencereleri kapandıktan sonra, ayrı ön kayıtla.
- **H1:** yeniden açma gerekmez; Marmara'ya taşıma (b) ayağının yeniden açma şartına bağlı kalır (Mc ≈ 1 homojen açık
  katalog ve çok yıllı pencere).

## 15. Maliyet ve iş yükü

0 €. Bütün veriler açık (ComCat, ISC, GeoNet, EMSC, KOERI, SRCMOD erişimi doğrulanmadı). Tahmin (ölçülmedi): kod 1–2 gün,
manifest için olay öncesi indirmeler birkaç saat sunucu süresi (ISC yavaş, KOERI çok yavaş), Okada hesabı < 1 saat CPU,
olay sonrası indirme birkaç saat. Bulut oturumunda; makine gerekmez.

## Ek A (bilgi, bağlayıcı değil): Ek 1 kaba kapısının küme listesi, tarih kuralından sonra

Ek 1'in lob payı 0,25 varsayımıyla, en iyi açık katalog, ≤ 40 km, Aσ 19 kPa (eşik 31,36). Gerçek K manifestte lob
Mc'siyle yeniden sayılır ve bu listeden farklı olacaktır. 2012 Hint Okyanusu satırının Mc'si hatalıdır (§11 madde 10).

| Küme | Olay | Tarih | M | Enlem, boylam | Ek 1 katalog (Mc) | Ek 1 kaba N0 (/yıl) | Mekanizma (ComCat) |
|---|---|---|---|---|---|---|---|
| 1 | usp0006kdp | 1994-10-04 | 8,3 | 43,77, 147,32 | ISC (3,0) | 345,5 | ters (diğer) |
| 2 | usp0006qh3 | 1994-12-28 | 7,8 | 40,52, 143,42 | ISC (3,1) | 96,8 | ters, düşük eğimli (megathrust dahil) |
| 3 | usp0006sef | 1995-02-05 | 7,1 | -37,76, 178,75 | GeoNet (2,6) | 55,2 | normal |
| 4 | usp0009d4z | 1999-08-17 | 7,6 | 40,75, 29,86 | ISC (2,8) | 82,9 | doğrultu atımlı |
| 5 | ak002e435qpj | 2002-11-03 | 7,9 | 63,51, -147,45 | ComCat (1,6) | 316,3 | doğrultu atımlı |
| 6 | official20030925195006360_27 | 2003-09-25 | 8,16 | 41,81, 143,91 | ISC (2,5) | 583,7 | ters, düşük eğimli (megathrust dahil) |
| 7 | official20041226005853450_30 | 2004-12-26 | 9,1 | 3,29, 95,98 | ISC (4,8) | 52,8 | ters, düşük eğimli (megathrust dahil) |
| 7 | official20050328160936530_30 | 2005-03-28 | 8,6 | 2,08, 97,11 | ComCat (4,5) | 95,9 | ters, düşük eğimli (megathrust dahil) |
| 7 | usp000fzau | 2008-02-20 | 7,4 | 2,77, 95,96 | ISC (4,0) | 35,7 | ters, düşük eğimli (megathrust dahil) |
| 8 | usp000exfn | 2006-11-15 | 8,3 | 46,59, 153,27 | ISC (3,9) | 37,7 | ters, düşük eğimli (megathrust dahil) |
| 8 | usp000f2ab | 2007-01-13 | 8,1 | 46,24, 154,52 | ISC (3,7) | 49,3 | normal |
| 9 | usp000gz8j | 2009-07-15 | 7,8 | -45,76, 166,56 | GeoNet (2,7) | 89,1 | ters, düşük eğimli (megathrust dahil) |
| 10 | official20100227063411530_30 | 2010-02-27 | 8,8 | -36,12, -72,90 | ISC (3,6) | 78,3 | ters, düşük eğimli (megathrust dahil) |
| 11 | usp000hnj4 | 2010-10-25 | 7,8 | -3,49, 100,08 | ISC (4,0) | 36,8 | ters, düşük eğimli (megathrust dahil) |
| 12 | usp000hrw0 | 2010-12-25 | 7,3 | -19,70, 167,95 | ISC (2,6) | 39,9 | normal |
| 13 | official20110311054624120_30 | 2011-03-11 | 9,1 | 38,30, 142,37 | ISC (1,8) | 4501,4 | ters, düşük eğimli (megathrust dahil) |
| 14 | official20120411083836720_20 | 2012-04-11 | 8,6 | 2,33, 93,06 | ComCat (0,2) | 115,7 | doğrultu atımlı |
| 15 | usp000juhz | 2012-10-28 | 7,8 | 52,79, -132,10 | ISC (3,2) | 34,2 | ters, düşük eğimli (megathrust dahil) |
| 16 | usc000f1s0 | 2013-02-06 | 8,0 | -10,80, 165,11 | ISC (2,3) | 99,2 | ters, düşük eğimli (megathrust dahil) |
| 17 | usc000nzvd | 2014-04-01 | 8,2 | -19,61, -70,77 | ISC (2,3) | 50,3 | ters, düşük eğimli (megathrust dahil) |
| 17 | usc000p27i | 2014-04-03 | 7,7 | -20,57, -70,49 | ISC (2,5) | 34,2 | ters, düşük eğimli (megathrust dahil) |
| 18 | us200030aq | 2015-07-27 | 6,9 | 52,38, -169,45 | ComCat (2,5) | 69,1 | ters, düşük eğimli (megathrust dahil) |
| 19 | us20003k7a | 2015-09-16 | 8,3 | -31,57, -71,67 | ISC (3,6) | 82,2 | ters, düşük eğimli (megathrust dahil) |
| 20 | us20005iis | 2016-04-15 | 7,0 | 32,79, 130,75 | ISC (0,5) | 534,5 | doğrultu atımlı |
| 21 | us20005j32 | 2016-04-16 | 7,8 | 0,38, -79,92 | ISC (1,1) | 81,5 | ters, düşük eğimli (megathrust dahil) |
| 22 | us1000778i | 2016-11-13 | 7,8 | -42,74, 173,05 | ISC (2,6) | 206,8 | ters (diğer) |
| 23 | us2000cmy3 | 2018-01-23 | 7,9 | 56,00, -149,17 | ComCat (1,6) | 53,0 | doğrultu atımlı |
| 24 | hv70116556 | 2018-05-04 | 6,9 | 19,32, -155,00 | ComCat (2,0) | 102,6 | ters, düşük eğimli (megathrust dahil) |
| 25 | us1000h3p4 | 2018-09-28 | 7,5 | -0,26, 119,85 | ISC (3,2) | 34,3 | doğrultu atımlı |
| 26 | us1000hhb1 | 2018-10-25 | 6,8 | 37,52, 20,56 | ISC (2,1) | 47,3 | doğrultu atımlı |
| 27 | us1000i2gt | 2018-12-05 | 7,5 | -21,95, 169,43 | ISC (3,5) | 68,5 | normal |
| 27 | us6000dg77 | 2021-02-10 | 7,7 | -23,05, 171,66 | ISC (4,0) | 34,9 | ters, düşük eğimli (megathrust dahil) |
| 27 | us6000kd0n | 2023-05-19 | 7,7 | -23,21, 170,74 | ISC (4,0) | 53,3 | normal |
| 28 | us70003kyy | 2019-05-14 | 7,6 | -4,05, 152,60 | ISC (3,7) | 60,4 | doğrultu atımlı |
| 29 | ci38457511 | 2019-07-06 | 7,1 | 35,77, -117,60 | ComCat (1,5) | 75,2 | doğrultu atımlı |
| 30 | us7000asvb | 2020-07-22 | 7,8 | 55,07, -158,60 | ComCat (2,4) | 94,8 | ters, düşük eğimli (megathrust dahil) |
| 30 | us6000c9hg | 2020-10-19 | 7,6 | 54,60, -159,63 | ComCat (2,2) | 99,0 | doğrultu atımlı |
| 30 | us7000kg30 | 2023-07-16 | 7,2 | 54,39, -160,76 | ComCat (2,7) | 131,9 | ters, düşük eğimli (megathrust dahil) |
| 31 | us7000c7y0 | 2020-10-30 | 7,0 | 37,90, 26,78 | KOERI (2,3) | 37,6 | normal |
| 32 | us7000dflf | 2021-03-04 | 8,1 | -29,72, -177,28 | ISC (3,9) | 84,1 | ters, düşük eğimli (megathrust dahil) |
| 33 | us7000i90q | 2022-09-18 | 6,9 | 23,14, 121,34 | ISC (2,8) | 71,8 | doğrultu atımlı |
| 34 | us6000jllz | 2023-02-06 | 7,8 | 37,23, 37,01 | ISC (1,5) | 623,6 | doğrultu atımlı |
| 34 | us6000jlqa | 2023-02-06 | 7,5 | 38,01, 37,20 | ISC (1,9) | 264,6 | doğrultu atımlı |
| 35 | us6000m0xl | 2024-01-01 | 7,5 | 37,49, 137,27 | ISC (0,4) | 1912,8 | ters (diğer) |
| 36 | us6000nith | 2024-08-08 | 7,1 | 31,76, 131,50 | ISC (1,0) | 426,3 | ters, düşük eğimli (megathrust dahil) |
| 37 | nc75095651 | 2024-12-05 | 7,0 | 40,37, -125,02 | ComCat (2,1) | 52,5 | doğrultu atımlı |

46 olay, 37 küme. (Bu listedeki mekanizma sınıfı her olayın kendisinindir; Ek 1 E1.4 dökümü kümenin en büyük olayına
göredir.)

## Ek B: yeniden üretim

`python3 -I -B kayit/turetme/tr6/tr6a_onkayit_sayilar.py` (≈ 5 sn, ağ yok, `__pycache__` bırakmaz) iki dosyayı yazar;
`--md` bu belgedeki §6.1 ve Ek A tablolarını basar. Betik `tr6_a_kapi.py`'den yalnız `kumele`, `gereken_n0`,
`binom_ust` ve `uzaklik_km` fonksiyonlarını alır (ağ kodu çağrılmaz). Rastgele tohum 20261112 (yalnız §4.5'teki
Δτ_est dağılımı ve Monte Carlo denetimi).
