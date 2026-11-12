# TR-6a ön kaydı: hız-durum gerilme ölçeri bilinen kosismik Coulomb gölgelerini kör olarak doğru işaretle buluyor mu?

Tarih: 12 Kasım 2026. Durum: **DONDURULDU sürüm 3 (12 Kasım 2026; bu commit dondurma kaydıdır) (İNCELEME-1 ve İNCELEME-2 düzeltmeleri işlendi).**
Üçüncü inceleme turu yoktur. Metin "DONDURULDU" başlığıyla commit edilir; ondan sonra değişmez, ekler ayrı başlıkla
yazılır. İNCELEME-2 bulgularının işlendiği yerler sondaki "Sürüm 2 → 3 değişiklik listesi"ndedir.

**Kök oturum kararı.** Kaba önsayım 29 küme, yazar önseli P(K < 23) ≈ 0,7; buna rağmen ön kayıt dondurulur; kapı
gerçek koşuda yalnız olay öncesi veriyle sayılır; K < 23 ise olay sonrası veri indirilmez, hüküm 'güç yok', aday
elenmez.

**Önsayım özeti (başta, açıkça).** Ek 1'in kaba kapısı (halka Mc'si, lob payı 0,25 varsayımı) sürüm 2 kurallarıyla
yeniden sayıldı (§3.1, §10): Aσ 19 kPa'da **K_kaba = 29** (sürüm 1'de 37). Bu 23'ün üstündedir; bu yüzden ön kayıt
koşulabilir bir sınav olarak dondurulabilir. Ancak pay dar: kaba N0'lar yarıya indirilirse K_kaba 19, Mc + 0,5 ile 11
olur. Gerçek lob tanımı ve lob Mc'si K'yi aşağı çeker. Yazarın önseli **P(K < 23) ≈ 0,7**'dir (sürüm 1: 0,5). K < 23
çıkarsa kural sürüm 1'deki gibidir: hüküm "güç yok", olay sonrası veri indirilmez, aday elenmez (§5). Kök oturum
bu koşullarla dondurma kararı verdi (yukarıda). Sürüm 3 kuralları kaba önsayımı değiştirmez (K_kaba 29). Aynı kaba
varsayımla pozitif kontrol kapısından (N0⁺ ≥ 10,0) K⁺ = 29, nötr kapıdan (N0_nt ≥ 31,36) K_nt = 29 küme geçer; bu iki
sayı lob payı varsayımının kopyasıdır, gerçek alanlar ΔCFF'ye bağlıdır (§10).

Türediği yerler: `kayit/onkayit/TR-6_SAYIM.md` (tasarım §2.1, sayım §4, Ek 1: Aσ ve katalog kapısı) ve
`kayit/onkayit/TR-6a_INCELEME-1.md` (DÜZELTMEYLE KABUL; A1–A4 engelleyici, B1–B10 önemli, K1–K8 küçük) ve
`kayit/onkayit/TR-6a_INCELEME-2.md` (DÜZELTMEYLE KABUL; A1–A3 engelleyici, B1–B6 önemli, K1–K15 küçük; son tur).

Kod (`kayit/turetme/tr6/`, yalnız numpy ve standart kitaplık, `python3 -I -B`, `__pycache__` bırakmaz, ağ yok):
- `tr6a_onkayit_sayilar.py` → `tr6a_olay_listesi.json` (dondurulan liste) ve `tr6a_onkayit_sayilar.json`;
  `--md` bu belgedeki tabloları basar;
- `tr6a_onbellek_kor.py`: önbelleğin tek okuma yolu, İNCELEME-1 B3 maskesiyle (§9 adım 3); önbellek yalnız ham
  arşivden sha256 denetimiyle açılır, yol argümanla ya da `TR6A_ONBELLEK` ortam değişkeniyle verilir; `tr6_a_kapi.getir`
  bu dizini açmayı reddeder;
- `tr6a_sifir_buyukluk.py` → `tr6a_sifir_buyukluk.json`: "0 büyüklük" denetimi (§3.5);
- `tr6a_inc1_denetim.py` → `tr6a_inc1_denetim.json`: İNCELEME-1'in `denetim1.py`–`denetim5.py` betiklerinin
  (scipy) numpy ile yeniden yazımı ve genişletmesi (aşırı saçılım, tamlık ızgarası, McNemar gücü; İNCELEME-1 B3 çift
  sayımı `tr6a_onkayit_sayilar.py` içinde);
- `tr6a_inc2_b1.py`–`tr6a_inc2_b4.py`: İNCELEME-2'nin bağımsız denetim betiklerinin (b1–b3 scipy kullanıyordu) numpy
  ve standart kitaplıkla yeniden yazımı: binom ve p₀ ızgarası denetimi, ortak veri ve temsil benzetimleri, sahte
  geçerlilik ve öncül komşu;
- `tr6a_md_denetim.py`: `--md` çıktısındaki her tablo satırının bu metinde birebir bulunduğunu denetler.

Bu belgedeki her sayı bu dosyalardan ya da Ek 1 çıktısı `tr6_a_kapi.json`'dan alınmıştır. "Yapay hesap (İNCELEME-2)"
diye anılan sayılar incelemecinin hesaplarıdır; `tr6a_inc2_b2.py` ve `tr6a_inc2_b3.py` onları Monte Carlo hatası
içinde yeniden üretir (Ek B). Maliyet: 0 €.

**Körlük beyanı (yazar).** Bu taslak yazılırken hiçbir olay sonrası katalog sorgusu yapılmadı. Hiçbir lobda oran ya da
oran değişimi hesaplanmadı. Hiçbir ΔCFF hesaplanmadı. Sürüm 2'de hiçbir yeni katalog sorgusu yapılmadı. Görülen veri:
Ek 1'in olay öncesi özet sayımları, halka Mc'leri, küme listesi ve ComCat mekanizma sınıfları. Ek 1 önbelleği başka
adayların olay sonrası pencerelerini kapsıyor (§9 adım 3). Sürüm 1'in yazarı bu önbellekte yalnız Ek 1 betiğinin özet
çıktılarını gördü. Sürüm 2'de önbellek yalnız bir kez açıldı: "0 büyüklük" denetimi için (§3.5), yalnız
`tr6a_onbellek_kor.py`'nin maskeli okuma yoluyla. O denetimin çıktısı yalnız katalog toplamları ve iki olayın Mc'sidir.
Sürüm 3'te hiçbir katalog sorgusu yapılmadı ve hiçbir lobda oran hesaplanmadı. Önbellek bir kez daha açıldı: yalnız
`tr6a_sifir_buyukluk.py`'nin yeni okuma yolundan (ham arşivden sha256 denetimiyle açılan dizin, maskeli
`oku_sorgu`) bayt bayt aynı çıktıyı verdiğini denetlemek için. Karşılaştırılan yalnız çıktının sha256'sıdır.

Yazar literatürden üç kümenin sonucunu kısmen biliyor:
- Kumamoto 2016 ve Ridgecrest 2019'da gölge loblarında artçı bulunduğunu (Hardebeck & Harris 2025);
- Tohoku 2011 sonrası nominal gölgede yaygın artış görüldüğünü (Toda vd. 2011).

§3.4'teki kırığa uzaklık sınırı bu bilgiyle yazıldı. Bu yüzden Kumamoto ve Ridgecrest kümeleri ana hükümden çıkarıldı
(§3.4, §7 B4).

## 0. Bağlayıcı metinlerin sırası

Çelişkide sıra şöyledir:
1. **Bu metin (sürüm 3).** §3.1'de sha256'sı verilen `tr6a_olay_listesi.json` bu metnin parçasıdır.
2. **İNCELEME-2'nin düzeltme metinleri**, yalnız bu metnin sustuğu yerde.
3. **İNCELEME-1'in düzeltme metinleri**, yalnız bu metnin ve İNCELEME-2'nin sustuğu yerde.
4. **`TR-6_SAYIM.md`** §2.1 ve Ek 1.

Bu metnin inceleme düzeltme metinlerinden bilerek saptığı yerler §16'da gerekçeleriyle yazılıdır; orada bu metin
geçerlidir.

Metin ile kod çelişirse metindeki sayısal tanım geçerlidir. Koşu kodu listeyi yeniden kurmaz; okur ve sha256'sını
denetler.

## 1. Tek cümlelik soru ve hüküm satırı

Sismisite oranı değişiminden gerilme değişimi çıkaran Dieterich (1994) hız-durum gerilme ölçeri, sonlu fay modellerinden
hesaplanan kosismik Coulomb gölge loblarında (ΔCFF ≤ −10 kPa) olay sonrası 1 yılda oran düşüşünü, bağımsız kümelerin
rastlantıdan anlamlı biçimde fazlasında buluyor mu?

Hüküm satırı: K bağımsız kümede "düşüş oyu" sayısı X; tek yanlı kesin binom, α 0,05. Boş hipotezin oy olasılığı
p₀ = max(0,50; ⌈100 p̂₀⌉/100)'dür (J < 30 ise taban 0,52; §4.6). p̂₀ olay öncesi sahte zamanlardan kalibre edilir
(§4.6). Kümeler Aσ = 19 kPa ile
sayılan güç kapısından geçen, bilinen sonuçlu ve kısa pencereli kümeleri çıkarılmış kümelerdir (§3, §5, §6).

### 1.1 Soru, neden ve neyi ölçmediği

TR-6 bir olasılık terimi değil, bir ölçü doğrulamasıdır. Hız-durum modeli ters çevrildiğinde sismisite oranı değişimi
gerilme değişimine çevrilir: Δτ_est = Aσ ln(R_son / R_on). Marmara'da (b ayağı) bu ölçü 1 yılda 15–37 kPa/yıl'ın
altını göremiyor (TR-6_SAYIM §6, GEÇMEZ). (a) ayağı daha temel bir soruyu sorar: ölçü, gerilmesi bağımsız olarak bilinen
yerlerde en azından işareti doğru buluyor mu? Bilinen gerilme olarak kosismik Coulomb değişimi kullanılır; bu "bilinen"
değer bir modeldir (§11).

Bu sınav yalnız **gölge tarafını** hükme bağlar. Artış tarafı (pozitif lob) bilinen ve kolay taraftır: artçılar oradadır.
Bu yüzden artış tarafı yalnız hattın çalıştığını gösteren pozitif kontroldür. Gölge tarafı tartışmalıdır (§2).

Ölçülmeyenler:
- Gerilme büyüklüğü hükme girmez; yalnız işaret. Büyüklük (Δτ_est) bilgi satırıdır.
- Aσ'nın kendisi sınanmaz. Oy (§4.3) Aσ'ya bağlı değildir. Aσ yalnız hangi kümenin "ölçülebilir" olduğunu (güç kapısı)
  belirler.
- Büyük deprem olasılığına çeviri yoktur. İstanbul ve Marmara için mutlak olasılık bu belgede ve sonuçta yazılmaz.

## 2. Rakip açıklamalar ve önceki bulgular

Doğrulama türleri: **ö** sayı ya da sav OpenAlex özetinde okundu (sürüm 1'de, 12 Kasım); **S** TR-6_SAYIM'da
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
  gölgeyi siler; oy olasılığı ≈ p₀): 0,50.
- **R3, gölgede bile artış baskın** (Hardebeck & Harris 2025 ve Mallman & Zoback 2007'nin küresel karşılığı): 0,30.

R2 ile R3 bu sınavda kısmen ayrılır (§6.1 ters yön notu). R1'in olumsuzu ise iki açıklamayı ayıramaz: gerilme ölçer mi,
Coulomb modeli mi başarısız (§6.3).

## 3. Veri, tanımlar ve dondurulan liste

### 3.1 Havuz, birimler ve aday listesi

Havuz `tr6_a_sayim.json`'daki **155 olaydır**: USGS ComCat'te `finite-fault` ürünü olan, 1990-01-01–2025-12-31,
M ≥ 6,0, derinlik ≤ 30 km. Olay grupları (§3.2) birleştirilince **151 birim** kalır. Bundan sonra "olay" ya da "birim"
olay grubu demektir.

Dondurulan liste `kayit/turetme/tr6/tr6a_olay_listesi.json`, **sha256
0cde4fa1433eaa11f513460b1c728e4f3f142d3dc091c120f4f55b677728048f** (sürüm 3 listeyi değiştirmedi). Liste olay
sonrası hiçbir katalog bilgisi taşımaz. İçeriği:
- `olaylar` (155): kimlik, zaman, M, dış merkez, L, Ek 1 halkası, Ek 1'de Mc'si kestirilebilen kataloglar (Mc, kaba N0,
  Mc + 0,5 kaba N0, "0 büyüklük" işareti), Ek 1 en iyi katalog, Ek 1 küme numarası, ComCat mekanizma sınıfı, grup;
- `birimler` (151): üyeler, en büyük üye, t0, t_s, son pencere başı, kesilmemiş son pencere sonu, tarih kuralı, ISC
  sınırı, seçilebilir kataloglar, kaba seçim ve kaba N0, §3.7 kesmesi (önsayım yaklaşımıyla), π, üç sahte zaman ve
  geçerlilikleri (§4.6), ön indirme başlangıçları, bilinen sonuç işareti.

Girdi dosyalarının sha256'sı listenin içinde yazılıdır:
- `tr6_a_sayim.json`: 8da8ba3c30fab3034841043bc894a7d3a973dc959ab816663f39b9425e1a7684;
- `tr6_a_kapi.json`: 5a90b0ebf39cb95556b5d91830c9622d11a12878fc4b6b02465e3c2c3aedee22;
- `tr6a_sifir_buyukluk.json`: ff20aebfd73ef84498da5826488a7031e8ecc360ed5637707ee83b0f105bc732.

Ek 1 ham önbelleği: `/mnt/project-files/turetme/tr6a-ham/tr6a_onbellek_2026-11-12.tar.gz`, sha256
f350d2e091be2d82b4026db03262a8eecbdb732aad26bf328a23224c9ced0d60 (sürüm 1'de doğrulandı, sürüm 3'te yeniden;
`kayit/turetme/tr6/tr6a_ham_sha256.txt`).

**Tarih kuralı (karar 5).** Kesilmemiş son pencere [t0 + 30 g, t0 + 365 g) 2025-12-31T23:59:59'u aşan birim listeden
çıkar. Havuzda **7 birim** çıkar: us6000pi9w (2025-01-07), us7000pcdl (2025-02-08), us7000pn9s (2025-03-28),
us7000pntq (2025-03-30), us7000pwkn (2025-05-02), us7000qx2g (2025-09-18), us6000rsy1 (2025-12-06). En geç sorgu
bitişi 2025-12-05'tir.

**Katalog kuralı.** Ek 1'de hiçbir açık katalogda halka Mc'si kestirilemeyen 67 birim (3 örnek pencerede 20'den az olay;
4'ü zaten tarih dışı) koşuya girmez. Gerekçe: kapıdan geçmek için gölge lobunda 5 yılda en az 155 kümesizleştirilmiş olay gerekir (§4.2).
Koşu adayı **81 birim (84 olay)**. Bunların 11'inin kesilmemiş son penceresi 2023-12-31'i aşar; 11'inin de ISC satırı
vardır (§3.5 ISC kuralı).

### 3.2 Olay grubu (çift ve öncü)

Havuzdan zincirle 30 gün ve 300 km içinde kalan olaylar tek **olay grubu**dur. Grubun t0'ı en erken üyenin zamanıdır.
ΔCFF bütün üyelerin sonlu fay modellerinin toplamıdır (doğrusal üst üste binme). L, halka ve alıcı düzlem kuralı en büyük
M'li üyeden alınır. Grubun kimliği en erken üyenin kimliğidir.

Grubun son üyesinin zamanı t_s'dir. Son pencere [t_s + 30 g, t0 + 365 g) olur. T_son ve π grup başına bu pencereden
hesaplanır: π = T_son / (1796 + T_son). Negatif kontrol, sahte olaylar ve D2 de aynı biçimde t_s'ye göre kaydırılır
(§4.6, §7). Kırık izi (§3.4) her üyenin kendi en büyük alt fay kaymasının %10'u eşiğiyle ayrı çıkarılır ve izler
birleştirilir. Grubun konumu (`kumele`, sorgu dairesinin merkezi, ızgara merkezi) en büyük M'li üyenin dış merkezidir.

Dört çok üyeli grup var; t_s − t0 kayması parantezde:
- Santa Cruz Adaları 2013: usc000f1s0, usc000f40j (2,59 g);
- Iquique 2014: usc000nzvd, usc000p27i (1,12 g);
- Nepal 2015: us20002926, us20002ejl (17,04 g);
- Kahramanmaraş 2023: us6000jllz, us6000jlqa (0,38 g).

Havuz dışındaki öncüler (ör. Ridgecrest 2019 M 6,4) toplanmaz (§11).

### 3.3 Gerilme kaynağı ve ΔCFF

- **Sonlu fay modeli.** Her üyenin ComCat `finite-fault` ürünü manifest anında bir kez indirilir. Bir üyenin birden
  çok `finite-fault` ürünü varsa ComCat'in indirme anındaki tercihli ürünü (olay ayrıntı yanıtında ilk listelenen)
  alınır. Ötekilerin kimlikleri ve `updateTime`'ları manifestte yazılır. Ürünün `updateTime`'ı 2025-12-31'den sonra
  olabilir; tarih sınırı katalog olaylarına uygulanır, kaynak modele uygulanmaz. Bir grup üyesi "veri yok" olursa
  bütün birim "veri yok" olur, çünkü grup ΔCFF'si eksik kalır. Ürün kimliği, `code`, `updateTime`, indirme zamanı ve
  dosyanın sha256'sı manifeste yazılır. Ham dosya
  `/mnt/project-files/turetme/tr6a-ham/` altına arşivlenir. Koşu yeniden indirmez; arşivdeki dosyayı sha256'sını
  doğrulayarak okur.
  - Okunan dosya `basic_inversion.param`'dır. Bu dosya yoksa `.fsp` okunur; ikisi de yoksa olay "veri yok" olur.
  - Bütün kesimler (segment) okunur.
  - Alt fay koordinatının anlamı (merkez ya da üst kenar) dosya başlığından alınır ve manifestte yazılır.
  - Sağlama: alt fay momentlerinin toplamı (μ = 30 GPa ile değil, dosyadaki μ ya da moment sütunuyla) başlıktaki
    M0'ın %10'u içinde olmalıdır. Tutmazsa olay "veri yok" olur.
- **Okada (1992) yarı uzayı**, numpy ile yazılan DC3D eşdeğeri. μ = 30 GPa, ν = 0,25 (α = 2/3). Hesap derinliği
  **7,5 km**. Etkin sürtünme **μ' = 0,4**. ΔCFF = Δτ (alıcı rake yönünde kayma gerilmesi) + μ' Δσ_n (Δσ_n çekme
  pozitif). Birim kPa.
- **Doğrulama (kod geliştirmede, koşudan önce).** Okada 1992'nin sonlu dikdörtgen kaynak sınama satırları (doğrultu,
  eğim ve açılma kaynakları; yer değiştirme ve türevleri) 5 anlamlı basamakta tutmalı. Tablo değerleri yayımlanmış
  makaleden ya da açık bir kopyasından sınama dosyasına elle yazılır ve kaynağı dosyada belirtilir. Tablo değerleri
  okunamazsa kayda "Okada 1992 tablo değerleri doğrulanamadı" diye geçer. Doğrulama o zaman yalnız numpy ile şu beş
  sınamayla yapılır. Hepsi doğrultu, eğim ve açılma kaynaklarında, eğim 30°, 70° ve 90°'de, en az 200 rastgele noktada
  koşulur:
  1. z = 0'da σ_xz, σ_yz ve σ_zz sıfırdır (|σ| / max|σ| < 1e−8);
  2. iç noktalarda denge: merkezi farkla hesaplanan div σ, |∇σ| ölçeğinin 1e−5'inden küçüktür;
  3. fay düzleminin iki yanında (±1e−6 W) yer değiştirme farkı birim kaymaya 1e−6 içinde eşittir;
  4. analitik türevler, yer değiştirmenin merkezi farklı sayısal türeviyle 1e−6 göreli içinde uyuşur;
  5. kaynak boyutu 0,01 km'ye küçültülünce sonlu kaynak, ayrıca yazılan nokta kaynak (DC3D0 karşılığı) çözümüyle 1e−4
     göreli içinde uyuşur. Uzak alanda (r > 20 L) aynı karşılaştırma 1e−3 içinde tutar.

  Doğrulama listesinin 6–9 maddeleri (İNCELEME-2 B4) yönelim, işaret, fay dışı süreklilik ve ΔCFF izdüşümünü sınar;
  tablo değerleri okunsa da okunmasa da koşulur:
  6. **Süreklilik.** Fay düzleminin uzantısında, dikdörtgenin dışında (kenardan en az 0,05 W uzakta), ±1e−6 W iki yan
     arasındaki yer değiştirme farkı birim kaymanın 1e−6'sından küçüktür.
  7. **Üst üste binme.** Bir dikdörtgen dört eş parçaya bölünür. Parçaların toplam çözümü tek dikdörtgen çözümüyle
     yer değiştirme ve gerilmede 1e−10 göreli içinde uyuşur.
  8. **Yönelim ve simetri.** Düşey, sağ yanal, 0–15 km derinlikte, boyu 30 km bir fay alınır; doğrultusu 0°, 90° ve
     225° olan üç hâli koşulur. Alıcı kaynakla aynıdır, μ' = 0, derinlik 7,5 km.
     - Fay ucunun doğrultu uzantısında, uçtan 15 km ötede Δτ > 0'dır.
     - Fay ortasından faya dik 15 km ötede Δτ < 0'dır.
     - Fay merkezli yerel eksenlerde (x doğrultu, y dik) |Δτ(x, y) − Δτ(−x, y)| ve |Δτ(x, y) − Δτ(x, −y)| değerleri
       max|Δτ|'nin 1e−8'inden küçüktür. |Δσ_n(x, y) + Δσ_n(−x, y)| için de aynı sınır geçerlidir.
     - Üç doğrultunun çözümleri koordinat döndürmesiyle 1e−8 göreli içinde uyuşur.
  9. **ΔCFF izdüşümü.** Doğu-kuzey-yukarı eksenlerinde, çekme pozitif. Alıcı normali tavan bloğuna doğrudur; kayma
     vektörü Aki & Richards kuralıyla cos λ · ŝ − sin λ · d̂'dir (ŝ doğrultu, d̂ eğim aşağı birim vektörü).
     - (a) Yalnız σ_EN = s; alıcı doğrultu 0°, eğim 90°, rake 180° → Δτ = −s, Δσ_n = 0.
     - (b) Yalnız σ_EE = s; aynı alıcı → Δτ = 0, Δσ_n = +s.
     - (c) Yalnız σ_EU = s; alıcı doğrultu 0°, eğim 30°, rake 90° → Δτ = −s · cos 60° = −0,5 s,
       Δσ_n = s · sin 60° = 0,866 s.

     Üçü de 1e−12 göreli içinde tutar.

  Tekil noktalar: sınamalar, DC3D'nin tekil kümelerinde (kenar uzantıları, fay düzlemi) en az 50 nokta içerir. Kod
  orada sonlu bir değer ya da açık bir "tekil" işareti döndürür. Izgaraya NaN ya da sonsuz değer girmez.

  **Izgara kuralı (§3.4'e de yazılır).** Hücre merkezinin, kayması sıfırdan büyük herhangi bir alt fay
  dikdörtgenine 3B uzaklığı 5 km'den küçükse hücre "tekil yakın alan" sayılır. Böyle bir hücre hiçbir loba ve nötr
  bölgeye girmez. Sayısı aday başına manifestte yazılır.

  Ek olarak King vd. (1994) dört lob işaret deseni denetlenir; nicel karşılığı 8. maddedir. Bir sınama başarısız
  olursa olay sonrası veri indirilmez; hüküm "koşulmadı (yöntem: Okada sınaması)" olur (§6.4).
- **Izgara.** Dış merkezde (grupta en büyük üyenin) ortalanmış azimutal eşit uzaklık izdüşümünde 10 km hücre; hücre
  merkezinde ΔCFF.

**Alıcı düzlem (karar 6, Ek 1 E1.5).**
1. ComCat'ten halkada (dış merkezden [L/2 + 10 km, 2L]), derinlik 0–40 km, [1976-01-01, t0) aralığında
   `moment-tensor` ürünü olan olaylar alınır. Her olayın tercihli tensörü (Mrr, Mtt, Mpp, Mrt, Mrp, Mtp) skaler
   momentine bölünür: M0 = √[(Mrr² + Mtt² + Mpp² + 2(Mrt² + Mrp² + Mtp²)) / 2].
2. En az 5 tensör varsa altı bileşenin ayrı ayrı medyanı alınır. Medyan tensörün izi çıkarılır. Özdeğerler
   λ1 ≥ λ2 ≥ λ3, özvektörler T (λ1) ve P (λ3)'tür. Düğüm düzlemi normalleri (T ± P)/√2'dir; her düzlemin kayma
   vektörü öteki normaldir. Dönüşüm r → yukarı, t → güney, p → doğu'dur. Rake Aki & Richards kuralıyla hesaplanır.
   Çift kuvvet payı 1 − 2|λ2|/max(|λ1|, |λ3|) < 0,5 ise medyan tensör kullanılmaz ve kural 3 uygulanır; manifestte
   yazılır. Aksi hâlde alıcı, normali sonlu fay modelinin moment ağırlıklı ortalama düzlem normaline en yakın
   (|n·n_ff| en büyük) düğüm düzlemidir; rake o düzlemin rake'idir.
3. 5'ten az tensör varsa (ya da kural 2'nin çift kuvvet koşulu tutmazsa) alıcı ana şok düzlemidir: sonlu fay modelinin
   moment ağırlıklı ortalama doğrultu ve eğimi, moment ağırlıklı vektör ortalaması rake.

Her olay için alıcının kaynağı (medyan / ana şok), tensör sayısı ve çift kuvvet payı manifeste yazılır. Duyarlılık D5:
iki düğüm düzlemi birlikte (§7).

### 3.4 Loblar ve kırığa uzaklık (karar 7)

- **Kırık izi.** Kayması, üyenin en büyük alt fay kaymasının %10'u ve üstü olan alt fay dikdörtgenlerinin yüzey
  izdüşümü, en çok 2 km aralıklı nokta örneklemesiyle (grupta üye başına ayrı, sonra birleştirilir). **r_k** = hücre
  merkezinin bu nokta kümesine yatay uzaklığı.
- **Bölge:** 20 km ≤ r_k ≤ 2L (L, en büyük üyenin M'sinden Wells–Coppersmith, `tr6_a_sayim.py` ile aynı:
  L = 10^(−3,55 + 0,74 M) km).
- **Gölge lobu:** bölgede ΔCFF ≤ −10 kPa olan hücrelerin birleşimi. **Pozitif lob:** ΔCFF ≥ +10 kPa. **Nötr bölge**
  (yalnız S7): |ΔCFF| ≤ 2 kPa. Arası atılır.
- **Tekil yakın alan (§3.3 ızgara kuralı).** Hücre merkezinin, kayması sıfırdan büyük herhangi bir alt fay
  dikdörtgenine 3B uzaklığı 5 km'den küçükse hücre "tekil yakın alan" sayılır. Böyle bir hücre hiçbir loba ve nötr
  bölgeye girmez. Sayısı aday başına manifestte yazılır.
- **Olayın atanması:** olayın dış merkezi aynı izdüşümle düzleme taşınır ve içine düştüğü 10 km hücrenin sınıfını
  alır. Hücre sınıfı hücre merkezindeki ΔCFF'den gelir. r_k hücre merkezi için hesaplanır. Olay derinliği yalnız
  ≤ 40 km süzgecine girer.
- **Gerekçe.** 20 km iç sınır küresel kataloglardaki konum hatasını (≈ 5–15 km) ve kayma modelinin geometri hatasını
  aşar. Kırık üzerindeki ve kenarındaki doğrudan artçı bulutunu dışarıda bırakır. Bu seçim yakın alan gölge
  artçılarını da (Hardebeck & Harris 2025) dışarıda bırakır; yönü H1 lehinedir. D3a (5 km) ve D3b (40 km) satırları
  bunu ölçer. Bu sınır, Kumamoto 2016 (us20005iis) ve Ridgecrest 2019 (ci38457511) kümelerinin gölge artçılarının
  yakın alanda olduğu bilinerek yazıldı. Bu yüzden bu iki olayı içeren kümeler **ana hükümden çıkarılır**. Çıkarma
  kümelemeden sonra, hükmün K'si sayılmadan önce yapılır (§5 işlem sırası): bu olaylardan birini içeren bir küme
  bütünüyle çıkar; kümelemenin kendisi değişmez. Bu iki küme §7 B4 satırında ayrıca raporlanır. Tohoku 2011
  (official20110311054624120_30) kümesi ana hükümde kalır: bilinen sonucu H1 aleyhinedir ve bu sınırdan etkilenmez.
  O da B4'te ayrıca yazılır.
- Megathrust olaylarında kırık izdüşümü büyük olduğu için gölgenin önemli bir kısmı (kırığın üstü) dışarıda kalır.
  Bunun K'ye etkisi bilinmiyor. Manifest, her aday için iç sınır yüzünden atılan gölge hücresi sayısını ve payını yazar
  (§9 adım 3).

### 3.5 Katalog, büyüklük ve tamlık

- **Olay seçimi:** bölgede, derinlik ≤ 40 km, tür deprem (`tr6_a_kapi.fdsn_ayristir` ile aynı süzgeç). Büyüklük
  satırları için üç kural vardır:
  1. Büyüklük alanı boş satırlar atılır (Ek 1 ayrıştırıcısı da atıyor).
  2. **Büyüklük türü boş ve büyüklüğü ≤ 0,05 olan satırlar atılır.**
  3. Sayım sorgularında büyüklüğü sorgu tabanının (Mc_halka − 0,05) altında kalan satırlar atılır.

  Türü dolu sıfır ya da negatif büyüklükler atılmaz. Atılan satır sayısı katalog, pencere ve kural başına manifestte
  yazılır.

  **Dayanak (K3, önbellekte doğrulandı).** `tr6a_sifir_buyukluk.py`, Ek 1 önbelleğinin 1440 olay sorgusunu (ComCat 465,
  ISC 825, EMSC 57, GeoNet 49, KOERI 44) maskeli okuma yoluyla taradı:
  - ComCat'te büyüklük türü boş 306 satırın 144'ünde büyüklük boş, 162'sinde büyüklük "0"dır. Türü boş ve
    büyüklüğü 0'dan büyük satır yoktur.
  - ComCat'te türü dolu ve büyüklüğü ≤ 0,05 olan 78 satır, ayrıca 66 negatif büyüklük var. Bunlar gerçek mikro
    depremlerdir.
  - ISC'de türü boş 8232 satırın hepsinin büyüklüğü de boştur (kural 1 zaten atar). Türü dolu ve büyüklüğü ≤ 0,05
    olan 3085 satır, ayrıca 2573 negatif büyüklük var. Bunlar da gerçek mikro depremlerdir.
  - EMSC'de türü boş 1 satır var, büyüklüğü de boş. GeoNet ve KOERI'de türü boş satır yok.
  - Türü boş ve büyüklüğü 0 olan satır yalnız ComCat'te, 23 olayın Ek 1 sorgularında var. Ek 1 Mc'sini bozdukları iki olay:
    2012 Hint Okyanusu (ComCat Mc 0,2 → kural 2 ile 4,7) ve 2003 Tokachi-oki (official20030925195006360_27; 0,3 →
    4,3).

  Sürüm 1'in kuralı ("türü boş satır atılır") bu veride kural 1 + 2 ile aynı satırları atar. Ancak olay sonrası
  pencerede gerçek büyüklüğü olan, türü eksik bir satırı da atabilirdi; bu iki pencereyi farklı etkileyebilir. Bu yüzden
  kural yalnız bilinen yapay olguya daraltıldı. İki olayın Ek 1 ComCat satırı geçersizdir ve kapı önsayımına girmez.
  İkisi de ISC ile kapıdan geçer (ISC N0 111,2 ve 583,7).
- **Katalog seçimi (yalnız olay öncesi veriyle).** Olayın Ek 1'de Mc'si kestirilebilen her kataloğu için
  (`ek1_kataloglar`; grupta en büyük üyenin) gölge lobunun kapı N0'ı (§4.2) hesaplanır. En büyük N0'ı veren katalog
  seçilir. Eşitlikte sıra ISC, ComCat, GeoNet, EMSC, KOERI. Seçim manifeste yazılır. Olay sonrası veri yalnız seçilen
  katalogdan indirilir.
  - **ISC kuralı (A4).** Seçilen katalog ISC ise ve kesilmemiş son pencere (t0 + 365 g) 2023-12-31T23:59:59'u
    aşıyorsa, o katalog bu olay için seçilemez. Bu tarih ISC gözden geçirilmiş bülteninin varsayılan sınırıdır; ISC'den
    okunmaz. Seçim öteki kataloglar arasında aynı kuralla (en büyük kapı N0'ı) yapılır. Kapıdan geçen başka katalog
    yoksa olay ana hükümden çıkar ve D6 satırında raporlanır. Bu kural kapı sayımından önce uygulanır ve manifestte
    yazılır. ComCat, GeoNet, EMSC ve KOERI bu kuraldan etkilenmez.
  - Önsayımda (§10) bu kural üç birimi kapıdan düşürür: Noto 2024 (us6000m0xl, ISC N0 1912,8), Hyūganada 2024
    (us6000nith, 426,3) ve Loyalty Adaları 2023 (us6000kd0n, 53,3). Kahramanmaraş 2023 ISC'den KOERI'ye geçer (kaba N0
    623,6 → 147,8). nc75095651'in seçimi zaten ComCat'tir.
  - **"0 büyüklük" işaretli** Ek 1 satırları (2012 Hint Okyanusu ve 2003 Tokachi-oki, ComCat) bu olaylar için seçime
    ve hiçbir satıra girmez; yeniden kestirilmez.
- **Sorgu:** dış merkezden R = 2L + (kırık izinin dış merkeze en uzak noktasının uzaklığı) yarıçaplı daire (bölgeyi
  kapsar), minmagnitude = Mc_halka − 0,05 (Mc_halka = o kataloğun Ek 1 Mc'si), yıllık parçalar. Bölge süzgeci yerelde uygulanır. Olay sonrası sorgu da aynı daire ve aynı taban büyüklükle
  yapılır. Satır sınırı kuralı §5 madde 1'dedir.
- **MAXC:** `tr6_a_kapi.maxc` ile aynı (0,1 kutu, en sık kutu; eşitlikte küçük olan).
- **Mc_lob** (her lob için ayrı, yalnız olay öncesi): max(Mc_halka, MAXC(lobun ön penceresindeki olaylar) + 0,2).
  50'den az olayda Mc_lob = Mc_halka + 0,3 (bu durumda gölge lobu zaten kapıdan geçemez).
- **Ana şok sonrası tamlık.**
  1. Son pencere t_s + 30 günde başlar. Önceki günler yalnız kümesizleştirmede ana olay olarak kullanılır.
  2. **Mc_son** alt pencerelerin en kötüsüdür. Son pencere [t_s + 30 g, t_s + 45 g), [45, 60), [60, 90), [90, 180),
     [180, 365) günlük alt pencerelere bölünür (gün sayısı t_s'den; son alt pencere son pencerenin sonunda, t0 + 365 g
     ya da §3.7 kesmesinde biter; boş kalan alt pencere atlanır). Her alt pencerede bölgenin bütün hücrelerindeki
     olaylardan MAXC + 0,2 hesaplanır; Mc_son bunların en büyüğüdür. 50'den az olaylı bir alt pencere bir sonrakiyle
     birleştirilir; sonuncusu 50'ye ulaşmazsa bir öncekiyle birleştirilir. Hiçbir birleşim 50'ye ulaşmazsa
     Mc_son = Mc_lob + 0,3 olur. Negatif kontrolde ve sahte olaylarda (§4.6) aynı alt pencere düzeni o pencerenin kendi
     başlangıcına göre kurulur (sahte j'de gün sayısı t'_j + (t_s − t0)'dan, S2'de t0 − 395 g + (t_s − t0)'dan
     sayılır).
  3. **Mc_kul** = max(Mc_lob, Mc_son). Hem ön hem son pencere sayımı Mc_kul ile yapılır.

  Gerekçe: Mc_son olay sonrası veriden hesaplanır, ama lobun sayı farkından değil, bölgenin büyüklük dağılımının
  tepesinden. Kural önceden yazıldığı için serbestlik bırakmaz; işaret bilgisi sızıntısı ihmal edilebilir. Havuzlanmış
  MAXC ise pencerenin geç dönemini gösterir. Gürültüsüz yapay hesapta (`tr6a_inc1_denetim.json`, §9 adım 2'deki 96
  hücrelik ızgara) sürüm 1'in havuzlanmış kuralı lobun son penceresinde %1,3–3,1 olay kaybetti. Bu kayıp H0 düşüş oyunu
  96 hücrenin 56'sında kesin Poisson değerinin 0,02'den fazla üstüne çıkardı (en çok +0,469, N0 4500'de). Alt pencere
  kuralı bütün hücrelerde kaybı sıfırladı.
- **Negatif kontrolde ve sahte olaylarda** aynı kural, o pencerelerin kendi zamanlarına göre (§4.6, §7 S2).

### 3.6 Kümesizleştirme

`tr6_sayim.kumesizlestir` ile aynı Gardner–Knopoff (1974) pencere yöntemi: d = 10^(0,1238 M + 0,983) km;
t = 10^(0,032 M + 2,7389) gün (M ≥ 6,5), 10^(0,5409 M − 0,547) gün (M < 6,5); büyükten küçüğe, önce ve sonra
pencereli; bağımlı olay ana olay olamaz.
- Her lob ayrı kümesizleştirilir. **Yalnız o lobun içindeki olaylar** (Mc_kul üstü) ana olay ve bağımlı olabilir. Ana
  şok ve lob dışındaki olaylar ana olay olamaz. Gerekçe: ana şokun GK penceresi (M 7'de ≈ 70 km, ≈ 2,5 yıl) bütün lobu
  silerdi; yakın alandaki büyük artçıları ana olay saymak da son pencereyi asimetrik olarak boşaltır ve gölgede H1
  lehine yanlılık yaratır. Kapı (§4.2) ve sahte oylar için ön katalog Mc_lob (sahtede sahte Mc_lob) üstü olaylarla
  kümesizleştirilir. Oy için ön ve son katalog Mc_kul üstü olaylarla ayrıca kümesizleştirilir. İki kümesizleştirme
  aynı kuralladır.
- **Pencereler ayrı ayrı ve aynı tampon yapısıyla kümesizleştirilir.**
  - Ön katalog [t0 − 1826 g − 730 g, t0 − 30 g) aralığında kümesizleştirilir. İlk 730 günün lob içi olayları ana olay
    olabilir, sayılmaz.
  - Son katalog [t0, son pencere sonu) aralığında kümesizleştirilir. t_s + 30 g'ye kadarki lob içi olaylar ana olay
    olabilir, sayılmaz.
  - Sahte olaylarda (§4.6) ve negatif kontrolde aynı 730 günlük ön tampon kullanılır.
  - Kapı yalnız ön kataloğun kümesizleştirmesiyle sayılır. Hiçbir son pencere olayı ön sayıyı değiştiremez.

  Gerekçe: tamponsuz ön pencerede, pencereden önceki lob içi olayların artçıları bağımsız sayılır (GK zaman penceresi
  M 5'te 143 gün, M 6'da 499 gün); ön oran şişer ve bu H1 lehinedir.
- Duyarlılık D4: kümesizleştirme yok (iki pencere ham).

### 3.7 Bağımsızlık, küme, temsilci ve son pencerenin kesilmesi

- Kapıdan geçen birimler `tr6_a_kapi.kumele` ile kümelenir (zaman sıralı, ilk uyan kümeye ekleme; 300 km dış merkez ve
  1826 gün; grupta t0 ve en büyük üyenin dış merkezi). Bu, Ek 1 ile aynı fonksiyondur. Tek bağlantılı kümelemeyle aynı
  değildir; manifest, tek bağlantıda birleşecek küme çiftlerinin sayısını yazar.
- **Temsilci:** kümenin zamanca ilk birimi. Bir kümenin tek oyu temsilcisinin oyudur. Kümenin sonraki olayları,
  temsilcinin son penceresine düşüyorsa onun "yanıtının" parçasıdır; lob içindeyseler kümesizleştirmede ana olay olurlar.
- **Son pencerenin kesilmesi (İNCELEME-1 B4).** Temsilcinin son penceresinde, [t_s + 30 g, t0 + 365 g) aralığında ve
  bölgesinde (havuz olayının dış merkezinin, temsilci grubunun kırık izi nokta kümesine (§3.4) yatay uzaklığı ≤ 2L;
  L grubun en büyük üyesinden; olay hücreye atanmaz ve 20 km iç sınır uygulanmaz) havuzdan bir olay (grup dışı)
  varsa, son pencere o olaydan bir gün önce biter. T_son ve
  π buna göre yeniden hesaplanır. **T_son < 60 g kalırsa küme ana hükümden çıkar** ve §7 B3'te yazılır. Kesme yalnız
  dondurulan havuz listesine dayanır, lob sayısına değil; manifestte yazılır. Kümelemenin kendisi değişmez. Böyle bir
  olay başka bir kümenin temsilcisiyse, o kümenin ön penceresi bu temsilcinin son penceresiyle örtüşür; bu çift B3'te
  adıyla yazılır.
  - Önsayım (§10) r_k yerine dış merkez uzaklığı ≤ 2L ile yapıldı (kırık izi henüz yok). Bu yaklaşımla dört küme çıkar:
    1994 Hokkaidō (usp0006kdp; 1994 Sanriku ile T_son 54,0 g), 2006 Kuril (usp000exfn; 2007 Kuril ile 27,7 g), 2012
    Haida Gwaii (usp000juhz; ak0138esnzr ile 38,2 g), 2020 Simeonof (us7000asvb; Sand Point ile 58,6 g).
  - 2004 Sumatra kümesi kalır (Nias ile T_son 61,6 g). Dış merkez ≤ 3L ile de sonuç değişmez (K_kaba 29).
  - Bağlayıcı karar manifestte r_k ile verilir. Önsayımda dış merkez ≤ 3L ile K_kaba değişmedi (29); r_k ≤ 2L, dış
    merkezi bu sınırın içinde kalan bütün olayları kapsar. 81 koşu adayının hiçbirinde [t0, t_s + 30 g) aralığında,
    3L içinde grup dışı bir havuz olayı yoktur (`ilk30_gun_3L`).
- Manifest bayrağı (bilgi): temsilcinin [t0, t0 + 365 g) penceresinde ve 2L içinde havuzdan başka bir olay.

## 4. Ölçü

### 4.1 Sayılar

Bir birim ve bir lob için:
- n_on = ön penceredeki [t0 − 1826 g, t0 − 30 g) kümesizleştirilmiş Mc_kul üstü lob olayı; T_on = 1796 g.
- n_son = son penceredeki [t_s + 30 g, son pencere sonu) kümesizleştirilmiş Mc_kul üstü lob olayı. Tek olaylı ve
  kesilmemiş pencerede T_son = 335 g.
- n = n_on + n_son.

### 4.2 Ölçülebilirlik kapısı (karar 2 ve 7; Ek 1 ile aynı kural)

Gölge lobunun ön penceresinde, **Mc_lob** ile ve yalnız ön kataloğun kümesizleştirmesiyle: **N0 = n_on / (1796/365,25)
≥ 31,36 olay/yıl** (yani n_on ≥ 155). Eşik, Aσ = 19 kPa'da Δτ = −10 kPa'lık adımın 1 yılda %80 güçle (tek yanlı
α 0,05) görülmesi için gereken orandır: N0 ≥ [(z_α + z_β √k)/(1 − k)]², k = e^(−10/19) (`tr6_a_kapi.gereken_n0`).
Duyarlılık eşikleri: Aσ 13 kPa → 17,08; Aσ 39 kPa → 111,21 (n_on ≥ 84 ve n_on ≥ 547). Aσ veriden kestirilmez
(karar 1).

K_kapı = kapıdan geçen birimlerin bağımsız küme sayısı, §3.4 ve §3.7 çıkarmalarından sonra. Kapı yalnız olay öncesi
veriyle sayılır ve manifestte dondurulur.

### 4.3 Oy: koşullu binom ortanca kuralı

H0 (oran değişmedi) altında, n verildiğinde n_son ~ Binom(n, π), **π = T_son / (T_on + T_son)**. Tek olaylı ve
kesilmemiş pencerede π = 335/2131 = 0,15720. Grupta ve kesilmiş pencerede π birim başınadır (§3.2, §3.7). F(·; n, π)
bu dağılımın birikimli fonksiyonudur.
- **Düşüş oyu** D = 1 ⟺ n ≥ 1 ve F(n_son; n, π) ≤ 0,5.
- **Artış oyu** A = 1 ⟺ n ≥ 1 ve P(Binom(n, π) ≥ n_son) ≤ 0,5.
- n = 0 ise iki oy da 0'dır; küme K'de kalır (payda değişmez).

Poisson H0 altında her n ve her π için P(D = 1 | n) ≤ 0,5 ve P(A = 1 | n) ≤ 0,5 tanım gereğidir. Negatif kontrolde aynı
kural, π_nk = 335 / (1461 + 335) = 0,18653.

**Neden saf oran karşılaştırması değil.** "n_son/T_son < n_on/T_on" oyu, Poisson çarpıklığı yüzünden H0 altında düşüş
yönüne kayar: N0 = 31,36'da P = 0,5088 (sürüm 1 hesabı). Koşullu oy bu kaymayı Poisson H0'da kaldırır.

**H0 oy olasılığı N0'a ve saçılıma bağlıdır.** H0 altında (Poisson, sabit oran) düşüş oyu olasılığı N0'a bağlıdır:

| N0 (/yıl) | 17,08 | 31,36 | 50 | 111,2 | 300 | 1000 | 4500 |
|---|---|---|---|---|---|---|---|
| P(D \| H0, Poisson) | 0,4459 | 0,4585 | 0,4680 | 0,4783 | 0,4869 | 0,4928 | 0,4966 |
| α, p₀ 0,50, K = 23 | 0,0139 | 0,0188 | 0,0235 | 0,0295 | 0,0355 | 0,0402 | 0,0435 |

P(A) N0 31,36'da 0,4606'dır. 200 000 denemelik Monte Carlo denetimi P(D) için 0,4582 verir (N0 31,36). Bu yüzden
p₀ = 0,5'e karşı binom sınamasının gerçek α'sı, kapıdan geçen kümelerin N0 karışımına göre K = 23'te 0,014 ile 0,044
arasındadır.

Bu sınır yalnız Poisson H0'da geçerlidir. Yıllık sayıların aşırı saçılımında (φ = var/ortalama > 1) 335 günlük
pencerenin oranı 4,9 yıllık pencereninkinden daha çarpık dağılır. O zaman H0 altında P(D) 0,5'i aşabilir. Yapay hesap
(`tr6a_inc1_denetim.json`; her yılın oranı bağımsız Gamma çarpanıyla çarpılır; 400 000 deneme; standart hata 0,0008):

| N0 | φ | P(D \| H0) | P(A \| H0) | α K = 23, p₀ 0,50 | α K = 23, §4.6 kalibrasyonuyla | α K = 39, p₀ 0,50 |
|---|---|---|---|---|---|---|
| 31,36 | 1 | 0,4586 | 0,4614 | 0,0188 | 0,0153 | 0,0071 |
| 31,36 | 2 | 0,4830 | 0,4594 | 0,0327 | 0,0231 | 0,0160 |
| 31,36 | 3 | 0,4965 | 0,4567 | 0,0434 | 0,0276 | 0,0241 |
| 31,36 | 5 | 0,5151 | 0,4484 | **0,0625** | 0,0336 | 0,0405 |
| 100 | 3 | 0,4993 | 0,4746 | 0,0459 | 0,0285 | 0,0261 |
| 100 | 5 | 0,5086 | 0,4712 | **0,0551** | 0,0316 | 0,0339 |
| 500 | 5 | 0,5029 | 0,4880 | 0,0494 | 0,0297 | 0,0289 |

Sapmanın yönü H1'dir: düşüş oyu artar, artış oyu azalır. Kalibrasyonlu α hesabında sahte oylar bağımsız ve aynı
dağılımlı varsayıldı (S ~ Binom(3K, P(D))). Bu varsayımla, ızgaranın bütün hücrelerinde ve K = 23, 28, 39'da α ≤ 0,035
kalır. Bu nedenle p₀ §4.6'daki sahte olay kalibrasyonuyla yalnız olay öncesi veriden kestirilir ve manifestte dondurulur.
Kümeler arası korelasyon (§3.7 çiftleri, ortak bölgeler) X'in saçılımını ayrıca büyütür; kalibrasyon bunu düzeltmez
(§11 madde 12).

### 4.4 Büyüklük ölçeri (bilgi)

Δτ_est = Aσ · ln[(n_son / T_son) / (n_on / T_on)], T yıl, Aσ = 19 kPa (13 ve 39 ayrıca). Özel durumlar:
- n_son = 0 ve n_on > 0'da −∞ yazılır.
- n_on = 0'da Δτ_est "tanımsız" yazılır ve medyana girmez; sayısı yazılır.

Özetler medyanla verilir. Spearman'da −∞ en küçük sıra alır, tanımsızlar dışarıda kalır. Bu, T ≪ t_a sınırındaki kaba
ölçerdir. Yapay sınamada (§4.5) gerilme hızının bilinmemesi yüzünden sıfıra doğru yanlıdır.

### 4.5 Yapay Dieterich sınaması (karar 8, eşiklerin önceden denetimi)

Dieterich (1994) adım yanıtı R(t)/r = 1 / [(e^(−Δτ/Aσ) − 1) e^(−t/t_a) + 1], t_a = Aσ/τ̇0. [30 g, 365 g) integrali
kesindir. n_on ve n_son bağımsız Poisson'dur; oy olasılığı kesin toplamla hesaplanır. Aσ = 19 kPa, Δτ = ∓10 kPa.

| τ̇0 (t_a) | Gölge düşüş oyu, N0 31,36 / 50 / 111,2 | Pozitif artış oyu, N0 31,36 | Δτ_est medyanı (q10, q90), N0 31,36; beklenen |
|---|---|---|---|
| kalıcı adım (t_a → ∞) | 0,987 / 0,998 / 1,000 | 0,997 | −10,23 (−17,16, −4,38); −10,00 |
| 2 kPa/yıl (9,5 yıl) | 0,984 / 0,997 / 1,000 | 0,995 | −9,73 (−16,49, −4,05); −9,57 |
| 10 kPa/yıl (1,9 yıl) | 0,964 / 0,990 / 1,000 | 0,972 | −8,13 (−14,62, −2,66); −7,99 |
| 50 kPa/yıl (0,38 yıl) | 0,771 / 0,839 / 0,939 | 0,734 | −3,43 (−9,25, 1,58); −3,39 |

**"Doğru lob payı" (İNCELEME-1 B5).** Kapıdan geçen bir lob gerçekten −10 kPa görmüşse oy neredeyse kesin tutar. Tasarımdaki
p₁ = 0,75, yalnız kümelerin bir f payında lobun doğru yerde olduğu dünyaya karşılık gelir. Kalan (1 − f) payında oy
olasılığı w'dir: f · P_D + (1 − f) · w = p₁*. Burada p₁*, p₀ ve K verilmişken gücü 0,80 yapan en küçük küme başına oy
olasılığıdır. Aşağıdaki tablo f'yi verir (`tr6a_onkayit_sayilar.json` `dogru_lob_payi`):
- P_D = 0,987 (kalıcı −10 kPa, Mc farkı 0);
- son sütunda P_D = 0,868 (Mc_kul − Mc_lob = 0,5).

| p₀ | K | p₁* | f (w = H0 düzeyi*) | f (w 0,40) | f (w 0,30) | f (w 0,20) | f (w 0,30; ΔMc 0,5) |
|---|---|---|---|---|---|---|---|
| 0,50 | 23 | 0,749 | 0,549 | 0,594 | 0,653 | 0,697 | 0,790 |
| 0,50 | 28 | 0,730 | 0,514 | 0,563 | 0,626 | 0,674 | 0,758 |
| 0,50 | 33 | 0,717 | 0,489 | 0,539 | 0,606 | 0,656 | 0,734 |
| 0,52 | 23 | 0,788 | 0,573 | 0,660 | 0,710 | 0,747 | 0,859 |
| 0,52 | 28 | 0,763 | 0,520 | 0,618 | 0,674 | 0,715 | 0,815 |
| 0,52 | 33 | 0,745 | 0,481 | 0,587 | 0,647 | 0,692 | 0,783 |
| 0,55 | 23 | 0,826 | 0,631 | 0,725 | 0,765 | 0,795 | 0,926 |
| 0,55 | 28 | 0,795 | 0,561 | 0,673 | 0,720 | 0,756 | 0,872 |
| 0,55 | 33 | 0,773 | 0,509 | 0,634 | 0,688 | 0,727 | 0,832 |

\* H0 düzeyi: p₀ = 0,50'de 0,4585 (Poisson, N0 31,36); p₀ > 0,50'de w = p₀.

Okuma:
- Yanlış loblar H0 düzeyindeyse, kümelerin yaklaşık yarısında lobun doğru olması yeter.
- Yanlış loblarda gerçekte artış varsa (Mallman & Zoback 2007; Hardebeck & Harris 2025; w 0,30–0,20), gereken pay
  0,63–0,80'e çıkar.
- Oy Mc_kul ile sayılır, kapı ise Mc_lob ile. Kapı sınırındaki bir lobda Mc_kul − Mc_lob = 0,3 / 0,5 / 1,0 için
  kalıcı −10 kPa'da P_D 0,934 / 0,868 / 0,644'tür. ΔMc 1,0'da p₁* hiçbir f ile sağlanamaz.
- Hainzl vd.'nin CV ≈ 1 bulgusu göz önüne alınınca f ≥ 0,6 iyimser bir dünyadır. Tasarım gücü 0,804 yalnız p = 0,75
  dünyası içindir; bu dünyaya karşılık gelen fiziksel koşul iyimserdir.
- Yüksek gerilme hızlı bölgelerde (t_a ≈ 0,4 yıl) gölge 1 yılda büyük ölçüde toparlanır. Tasarım gücü ancak lobların
  hemen hepsi doğruysa tutar.

### 4.6 Sahte olay kalibrasyonu (p₀, yalnız olay öncesi)

Manifestte, K_kapı'nın her kümesinin (§3.4 ve §3.7 çıkarmalarından sonra, testere dişi atmasından önce) temsilcisi için
üç sahte zaman alınır: t'_j = t0 − 395 g − 335 g · (j − 1), j = 1, 2, 3.
- Sahte son pencere gerçek pencereyle aynı kaymalara sahiptir: [t'_j + (t_s − t0) + 30 g, t'_j + e), e gerçek son
  pencerenin t0'a göre bitişidir (365 g ya da §3.7 kesmesi).
- Kesilmemiş bir birimde sahte son pencereler sırasıyla [t0 − 365 g, t0 − 30 g), [t0 − 700 g, t0 − 365 g) ve
  [t0 − 1035 g, t0 − 700 g)'dir. Bunlar birbiriyle örtüşmez.

Her t'_j için şunlar kullanılır:
- gölge lobu ve hücreleri gerçek olaydakilerle aynıdır;
- ön pencere [t'_j − 1826 g, t'_j − 30 g), 730 g ön tamponla (§3.6);
- π gerçek birimdekiyle aynıdır;
- Mc kuralı §3.5'tekidir; Mc_son sahte son pencerenin bölge olaylarıyla alt pencere kuralına göre hesaplanır;
- kümesizleştirme §3.6'dakidir;
- oy kuralı §4.3'tekidir. n = 0 ise oy 0'dır ve paydada kalır.

Bu hesap için ön indirmeler t0 − 3621 g'ye kadar uzatılır (395 + 670 + 1826 + 730 g). Koşu adaylarında en erken
başlangıç 1983-08-13'tür. Bütün veri olay öncesidir ve 2025-12-31'den önce kalır.

**Sahte zamanın geçerliliği (yalnız havuz listesinden; listede yazılı).** Sahte j geçersizdir ve hesaplanmaz, eğer
havuzdan (grup dışı) bir A olayı şu iki koşulu birlikte sağlıyorsa:
- [t_A, t_A + 365 g), kesilmemiş sahte son pencere [t'_j + (t_s − t0) + 30 g, t'_j + 365 g) ile kesişiyor;
- A ile temsilcinin dış merkez uzaklığı < 3 L_A + 3 L_temsilci.

Ayrıca sahte j, sahte ön penceredeki kümesizleştirilmiş gölge lobu sayısı n_on' (sahte Mc_lob ile, §3.6'nın 730 g
tamponuyla) 155'ten küçükse geçersizdir (neden: "sahte kapı"; manifestte yazılır). Gerekçe: gerçek oylar kapıdan
geçmiş loblardan gelir. Poisson H0'da P(D) N0 ile artar ve n ≤ 4'te düşüş oyu tanım gereği 0'dır. Kapı altı sahte
oylar p̂₀'ı aşağı, H1 yönüne çeker.

Geçerlilik ölçütü (3 L_A + 3 L_temsilci) "olay yok" dünyasının fiziksel ölçütüdür. §9 adım 3'teki 4 L_A maskesi
yalnız ad hoc önbellek okumaları içindir; manifest sahte oyları adayın kendi indirmesinden, maskesiz sayar.

Gerekçeler (havuz ölçütü):
- (i) O sahte pencere "olay yok" dünyasını temsil etmez: A'nın artçı dizisi sahte oyu bir yöne iter.
- (ii) O sahte oy, A'nın olay sonrası penceresinde bölgesel bir sayı özeti olurdu (körlük, §9 adım 3).

Önsayımın 29 kümesinde 87 sahte zamanın 64'ü geçerlidir (`onsayim.19.sahte_gecerli_toplam`). Tohoku, 2012 Hint
Okyanusu, 1994 Sanriku, 2004 Sumatra ve 2024 Mendocino (nc75095651) temsilcilerinde hiçbir sahte zaman geçerli değil.
Sahte j'de §3.7 kesmesi ayrıca uygulanmaz; geçerlilik kuralı onun yerine geçer. Sahte kapı önsayımda uygulanamaz
(sahte ön penceredeki lob sayısı gerekir); manifestteki J bu yüzden 64'ün altında kalabilir.

**Kestirim ve eşik.** Sahte düşüş oyu D'_ij'dir; J geçerli sahte zaman sayısıdır.
- p̂₀ = Σ D'_ij / J ve p̂₀⁺ = Σ A'_ij / J (sahte artış oyu payı).
- **J ≥ 30 ise p₀ = max(0,50; ⌈100 p̂₀⌉/100)**: p̂₀ yukarı doğru iki ondalığa yuvarlanır. Tamsayı aritmetiğiyle
  ⌈100 S / J⌉, S = Σ D'_ij. Bu yuvarlama, §6.1'deki p₀ ızgara tablosunu tek anlamlı ve bağlayıcı yapar; tablo dışı ara
  değer yoktur.
- Ters yön için (J ≥ 30) p₀⁺ = max(0,50; ⌈100 p̂₀⁺⌉/100).
- **J < 30 ise kalibrasyon zayıftır.** O zaman p₀ = max(0,52; ⌈100 S / J⌉/100) ve p₀⁺ = max(0,52; ⌈100 S⁺ / J⌉/100)
  olur (S⁺ = Σ A'_ij; J = 0 ise ikisi de 0,52). p₀ > 0,60 ve p₀⁺ > 0,60 kuralları aynen uygulanır. Hüküm adına
  "kalibrasyon zayıf: J = …, p₀ = …" niteleyicisi eklenir (§6.4). Gerekçe: §4.3 aşırı saçılım ızgarasının en kötü
  hücresinde (N0 31,36, φ = 5) P(D | H0) = 0,5151'dir. Bu dünyada p₀ = 0,50'ye karşı gerçek α K = 23–45'te en çok
  0,072, p₀ = 0,52'ye karşı en çok 0,044'tür. J < 30'da p̂₀ yalnız p₀'ı yukarı itebilir.
- **p₀ > 0,60 ise** (yani p̂₀ > 0,60): ölçü H0 altında yanlıdır. Hüküm satırı koşulmaz ve olay sonrası veri
  indirilmez. Hüküm **"güç yok (ölçü yanlı)"** olur (§6.4); §6.3 kalıbı p̂₀ ve J'yi yazar. Gerekçe: p₀ = 0,60'ta
  güç 0,80'e ancak K ≥ 62'de ulaşır (§6.1). Bu sınavın K'si bunun çok altındadır (§10).
- **p₀⁺ > 0,60 ise** ters yön notu sınanmaz ve onun yerine "ters yön sınanamadı (p̂₀⁺ = …)" yazılır (§6.4 madde 4).
- c(K) = P(X ≥ c | K, p₀) ≤ 0,05 koşulunu sağlayan en küçük c'dir. Ters yön eşiği c⁺(K) aynı biçimde p₀⁺ ile
  hesaplanır. H0 eşiği h(K) değişmez (p₁ = 0,75'e karşı).
- Testere dişi tablosu p₀ ile çözülür (§5).
- p̂₀, p̂₀⁺, J, J < 30 kuralının uygulanıp uygulanmadığı, p₀, p₀⁺, c(K), c⁺(K) ve testere dişi çözümü manifestte,
  olay sonrası indirmeden önce dondurulur. Sahte oyların küme başına dökümü manifestte yazılır.
- Bilgi (hükmü değiştirmez): manifest şunları ayrıca yazar:
  - p̂₀'ı, kapı N0'ı K_kapı medyanının altında ve üstünde kalan kümeler için ayrı ayrı;
  - hiç geçerli sahte zamanı olmayan küme sayısı K_0 ve bu kümelerin kimlikleri, kapı N0'ları.

J < 30 tabanının dayanağı (`tr6a_onkayit_sayilar.json` `j30_dali`; K = 23–45'te en büyük gerçek α ve o K; ilk satır
§4.3 ızgarasının en kötü hücresi):

| P(D \| H0) | en çok α, p₀ 0,50 (K) | en çok α, p₀ 0,52 (K) |
|---|---|---|
| 0,5151 | 0,0717 (44) | 0,0441 (24) |
| 0,53 | 0,1028 (44) | 0,0608 (29) |

P(D) 0,53 dünyasına karşı ayrıca p₀ > 0,60 kuralı ve "kalibrasyon zayıf" niteleyicisi durur. Güç bedeli: p₀ 0,52'de
K = 23 / 26 / 29 / 33'te güç 0,654 / 0,685 / 0,834 / 0,819'dur (§6.1 güç tablosu). Önsayımda J = 64; J < 30 olasılığı
düşüktür, ama sahte kapı J'yi düşürür.

S2 negatif kontrolü sürüm 1 tanımıyla ayrı satır olarak kalır (§7). Sahte j = 1'in son penceresi S2'ninkiyle aynıdır,
ön pencereleri farklıdır. S2 yalnız sahte j = 1'i geçerli olan kümelerde hesaplanır; K_nk bu kümelerin sayısıdır.

**Kalibrasyonun bedeli (İNCELEME-1 B5, `p0_kestirim`).** p̂₀ gürültülüdür. Sahte oylar bağımsız ve J = 3K varsayılırsa, gerçek
sahte oy olasılığı 0,46 iken bile P(p₀ > 0,50) K = 23'te 0,25, K = 28'de 0,20'dir. Testere atması olmadan beklenen güç
(p₁ 0,75) şöyle değişir:
- K = 23'te 0,804'ten 0,745'e (sahte p 0,46) ve 0,659'a (sahte p 0,50) iner;
- K = 28'de 0,862'den 0,825'e ve 0,750'ye;
- K = 33'te 0,901'den 0,874'e ve 0,811'e.

P(p₀ > 0,60) K = 23–39'da sahte p 0,46 iken ≤ 0,01, 0,50 iken ≤ 0,046'dır. Korunmayan bir α yerine düşen güç kabul edildi.

## 5. Kapılar ve sıraları

Kapılar bu sırayla, otomatik uygulanır. Bir kapı kapanırsa sonrakiler koşulmaz.

**İşlem sırası (K1):** veri kapısı → katalog seçimi (§3.5, ISC ve "0 büyüklük" kuralları) → güç kapısı (§4.2) →
kümeleme (§3.7) → çıkarmalar (§3.4 bilinen kümeler, §3.7 kısa son pencere) → K_kapı < 23 denetimi → p₀ kalibrasyonu
(§4.6, J < 30 kuralı dahil) → p₀ > 0,60 denetimi → testere dişi atması. Sözlük sırası, kimliğin UTF-8 bayt dizisine göre artan sıradır
(Python `str` karşılaştırması). §7'de "ana K" atmadan sonraki küme setidir; B1 atmadan önceki settir.

1. **Veri kapısı (manifest, yalnız olay öncesi).**
   - Her koşu adayı için sonlu fay dosyası indirilebilir, okunabilir ve §3.3 sağlamasından geçer olmalıdır.
     Geçmeyen olay "veri yok" diye düşer; sayısı yazılır.
   - Ön katalog indirmeleri tamamlanmalıdır (ComCat sayım servisi yerine olay satırı; sunucu kesmesinde Ek 1'deki
     yeniden deneme kuralı).
   - **Satır sınırı:** dönen satır sayısı sorgunun limit değerinin %99'u ve üstüyse, yanıt zaman aralığı ikiye
     bölünerek yeniden istenir. Bölme, bütün parçalar sınırın altında kalana dek sürer. Bölünen sorgu sayısı
     manifestte ve olay sonrası kayıtta yazılır. Son pencerede de aynı kural uygulanır. Bir parça 1 günlük aralıkta
     da sınırı aşıyorsa olay "veri yok" olur. Limit parametresini kabul etmeyen servislerde (GeoNet) her yıllık
     parça ikiye bölünür. İki yarının satır sayıları toplamı bütünün satır sayısına eşitse bütün kabul edilir.
     Değilse her yarıya aynı işlem uygulanır. 1 günlük parçada da eşitlik sağlanmazsa olay "veri yok" olur.
2. **Güç kapısı (manifest, yalnız olay öncesi).** K_kapı sayılır (§4.2, Aσ 19 kPa).
   - **K_kapı < 23:** hüküm satırı koşulmaz; olay sonrası katalog **indirilmez**. Hüküm **"güç yok"**. Aday elenmez.
     Manifestteki olay öncesi satırlar (negatif kontrol ve sahte oylar dahil) bilgi olarak yayımlanır.
   - **K_kapı ≥ 23:** kalibrasyon (§4.6), sonra testere dişi.
   - Hükmün K'si yalnız bu ana kapının K'sidir. Hiçbir duyarlılık ya da ikincil satırın (S5a, D1, D3a, D3b, D4, D5,
     D8) K'si ana K < 23 iken hüküm satırını açmaz. Ana satırın yerine geçmez ve §14'teki yeniden açma şartını
     karşılamaz. Ana K < 23 ise duyarlılık satırları da koşulmaz; yalnız kapı K'leri bilgi olarak yazılır.
3. **Kalibrasyon kapısı (manifest).** p₀ > 0,60 ise hüküm "güç yok (ölçü yanlı)" (§4.6); olay sonrası veri
   indirilmez.
4. **Kod incelemesi** (§9 adım 4; yapay sınamalar §9 adım 2'de manifestten önce tamamlanmıştır).
5. **Hüküm satırı ve kontroller (tek koşu).**

**Testere dişinin çözümü (karar 2, p₀'a bağlı).** Tek yanlı tam binom, p₁ = 0,75, α 0,05:
- **Hükmün K'si**, K_kapı'ya eşit ya da ondan küçük, 23'e eşit ya da büyük ve gücü P(X ≥ c(K; p₀) | K, 0,75) ≥ 0,80
  olan en büyük K'dir. Aradaki fark kadar "en zayıf" küme atılır.
- Böyle bir K yoksa atma yapılmaz: K = K_kapı. Güç olduğu gibi yazılır ve hüküm adına "(tasarım gücünün altında:
  güç …)" eklenir.
- Çözüm aşağıdaki tablodadır. Sütun, manifestteki p₀'dır (§4.6'daki yuvarlamayla tek anlamlı); satır K_kapı'dır.
  Hücrede hükmün K'si ve parantezde atılan küme sayısı vardır; * = tasarım gücünün altında, atma yok. K_kapı = 46–80
  için çözüm `tr6a_onkayit_sayilar.json` `p0_izgarasi.<p₀>.testere` anahtarından okunur ve bağlayıcıdır. K_kapı > 80
  için aynı kural aynı fonksiyonla uygulanır.

| K_kapı | p₀ 0,50 | p₀ 0,51 | p₀ 0,52 | p₀ 0,53 | p₀ 0,54 | p₀ 0,55 | p₀ 0,56 | p₀ 0,57 | p₀ 0,58 | p₀ 0,59 | p₀ 0,60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23 | 23 | 23* | 23* | 23* | 23* | 23* | 23* | 23* | 23* | 23* | 23* |
| 24 | 23 (−1) | 24* | 24* | 24* | 24* | 24* | 24* | 24* | 24* | 24* | 24* |
| 25 | 23 (−2) | 25* | 25* | 25* | 25* | 25* | 25* | 25* | 25* | 25* | 25* |
| 26 | 26 | 26 | 26* | 26* | 26* | 26* | 26* | 26* | 26* | 26* | 26* |
| 27 | 26 (−1) | 26 (−1) | 27* | 27* | 27* | 27* | 27* | 27* | 27* | 27* | 27* |
| 28 | 28 | 26 (−2) | 28* | 28* | 28* | 28* | 28* | 28* | 28* | 28* | 28* |
| 29 | 29 | 29 | 29 | 29* | 29* | 29* | 29* | 29* | 29* | 29* | 29* |
| 30 | 30 | 30 | 30 | 30 | 30* | 30* | 30* | 30* | 30* | 30* | 30* |
| 31 | 31 | 31 | 30 (−1) | 30 (−1) | 31* | 31* | 31* | 31* | 31* | 31* | 31* |
| 32 | 32 | 32 | 32 | 30 (−2) | 32* | 32* | 32* | 32* | 32* | 32* | 32* |
| 33 | 33 | 33 | 33 | 33 | 33 | 33* | 33* | 33* | 33* | 33* | 33* |
| 34 | 34 | 34 | 34 | 33 (−1) | 33 (−1) | 34* | 34* | 34* | 34* | 34* | 34* |
| 35 | 35 | 35 | 35 | 35 | 33 (−2) | 35* | 35* | 35* | 35* | 35* | 35* |
| 36 | 36 | 36 | 36 | 36 | 36 | 36* | 36* | 36* | 36* | 36* | 36* |
| 37 | 37 | 37 | 37 | 37 | 37 | 37 | 37* | 37* | 37* | 37* | 37* |
| 38 | 38 | 38 | 38 | 38 | 37 (−1) | 37 (−1) | 38* | 38* | 38* | 38* | 38* |
| 39 | 39 | 39 | 39 | 39 | 39 | 37 (−2) | 39* | 39* | 39* | 39* | 39* |
| 40 | 40 | 40 | 40 | 40 | 40 | 40 | 40* | 40* | 40* | 40* | 40* |
| 41 | 41 | 41 | 41 | 41 | 41 | 40 (−1) | 41* | 41* | 41* | 41* | 41* |
| 42 | 42 | 42 | 42 | 42 | 42 | 42 | 42* | 42* | 42* | 42* | 42* |
| 43 | 43 | 43 | 43 | 43 | 43 | 43 | 43 | 43* | 43* | 43* | 43* |
| 44 | 44 | 44 | 44 | 44 | 44 | 44 | 44 | 44 | 44* | 44* | 44* |
| 45 | 45 | 45 | 45 | 45 | 45 | 45 | 44 (−1) | 44 (−1) | 45* | 45* | 45* |

- p₀ = 0,50 sütunu sürüm 1 çözümüyle aynıdır: K = 24 ve 25 → 23; 27 → 26; K ≥ 28'de K = 28–200 aralığında güç
  0,80'in altına hiç düşmüyor (koddan denetlendi).
- Gücün 0,80'e ilk ulaştığı ve kalıcı olarak üstünde kaldığı K değerleri şöyledir (`ilk_K_guc08`, `kalici_K_guc08`):
  p₀ 0,50: 23 / 28; 0,51: 26 / 29; 0,52: 29 / 32; 0,53: 30 / 35; 0,54: 33 / 39; 0,55: 37 / 42; 0,56: 43 / 46;
  0,57: 44 / 50; 0,58: 48 / 54; 0,59: 55 / 64; 0,60: 62 / 71.
- **"En zayıf" tanımı:** temsilcinin kapı N0'ı (gölge lobu, Mc_lob, ön pencere) en küçük olan küme. Eşitlikte olay
  kimliği sözlük sırasında sonra gelen önce atılır. Bu sıralama yalnız olay öncesi veriye dayanır ve manifestte yazılır.
- **Gerekçe.**
  1. Kritik değer kesikli olduğu için bazı K'lerde gerçek α 0,05'in çok altına iner ve güç düşer. K'yi bir alt "dişe"
     indirmek gücü tasarım düzeyine geri getirir.
  2. Atılan kümeler en az olay öncesi sayıya sahip olanlardır: oyları en gürültülü olanlardır (H0'da P(D) 0,5'ten en
     uzak, H1'de en düşük). Atmak kalan kümelerin ortalama oy olasılığını düşürmez.
  3. "Zayıf" etiketi alternatifi hüküm adını sonradan yorumlanabilir kılardı; atma kuralı hükmü tek anlamlı tutar.
  4. Atılan kümeler kaybolmaz: "K tam" bilgi satırı (§7 B1) bütün kümelerle, kendi kritik değeriyle yazılır; hükmü
     değiştirmez.

## 6. Hüküm satırı (tek)

Birim: bağımsız küme (temsilcinin gölge lobu). X = düşüş oyu sayısı, Y = artış oyu sayısı (gölge lobunda), K = §5'teki
hükmün K'si. Payda her zaman K'dir.

### 6.1 Eşikler (koddan)

- **H1 (gölge işareti bulunuyor):** X ≥ c(K; p₀), c: P(X ≥ c | K, p₀) ≤ 0,05 olan en küçük c.
- **H0 (büyük etki yok):** X ≤ h(K), h: P(X ≤ h | K, 0,75) ≤ 0,05 olan en büyük h.
- **Ayırt edilemez:** h < X < c.
- **Ters yön notu:** Y ≥ c(K; p₀⁺) (gölgede anlamlı artış). Not, H0 ya da ayırt edilemez hükmünün yanına düşülür. Y,
  X'ten ayrı bir sayımdır.
- **Güç yok:** K_kapı < 23 (§5; ad "güç yok") ya da p₀ > 0,60 (§4.6; ad "güç yok (ölçü yanlı)").
- c(K) ≤ h(K) olan K'lerde (p₀ 0,50'de K ≥ 49) X ≥ c ise hüküm H1'dir; H0 yalnız X ≤ h ve X < c ise verilir. (Bu K'ler
  p₀ ızgarasında `c_le_h` anahtarındadır: p₀ 0,50'de K = 49 ve 51–80; p₀ 0,57–0,60'ta K ≤ 80'de yoktur.)

p₀ = 0,50 için eşikler:

| K | H1: X ≥ c | P(X ≥ c \| 0,5) | güç P(X ≥ c \| 0,75) | H0: X ≤ h | P(X ≤ h \| 0,75) |
|---|---|---|---|---|---|
| 23 | 16 | 0,0466 | 0,804 | 13 | 0,0408 |
| 24 | 17 | 0,0320 | 0,766 | 13 | 0,0213 |
| 25 | 18 | 0,0216 | 0,727 | 14 | 0,0297 |
| 26 | 18 | 0,0378 | 0,820 | 15 | 0,0401 |
| 27 | 19 | 0,0261 | 0,786 | 15 | 0,0216 |
| 28 | 19 | 0,0436 | 0,862 | 16 | 0,0294 |
| 29 | 20 | 0,0307 | 0,834 | 17 | 0,0390 |
| 30 | 20 | 0,0494 | 0,894 | 17 | 0,0216 |
| 31 | 21 | 0,0354 | 0,872 | 18 | 0,0289 |
| 32 | 22 | 0,0251 | 0,846 | 19 | 0,0378 |
| 33 | 22 | 0,0401 | 0,901 | 20 | 0,0484 |
| 34 | 23 | 0,0288 | 0,881 | 20 | 0,0281 |
| 35 | 23 | 0,0448 | 0,924 | 21 | 0,0363 |
| 36 | 24 | 0,0326 | 0,908 | 22 | 0,0461 |
| 37 | 24 | 0,0494 | 0,942 | 22 | 0,0272 |
| 38 | 25 | 0,0365 | 0,929 | 23 | 0,0348 |
| 39 | 26 | 0,0266 | 0,914 | 24 | 0,0439 |
| 40 | 26 | 0,0403 | 0,946 | 24 | 0,0262 |
| 41 | 27 | 0,0298 | 0,933 | 25 | 0,0333 |
| 42 | 27 | 0,0442 | 0,958 | 26 | 0,0416 |
| 43 | 28 | 0,0330 | 0,949 | 26 | 0,0252 |
| 44 | 28 | 0,0481 | 0,968 | 27 | 0,0318 |
| 45 | 29 | 0,0362 | 0,961 | 28 | 0,0395 |

K > 45 için eşikler aynı fonksiyonla (`tr6a_onkayit_sayilar.kritik`, `esik_H0`) hesaplanır; JSON'da K = 18–60 var.

p₀ ızgarası için c(K; p₀) ve güç P(X ≥ c | K, 0,75) bağlayıcıdır (ters yönde aynı tablo p₀⁺ ile okunur). JSON'da
K = 23–80 var:

| K | p₀ 0,50 | p₀ 0,51 | p₀ 0,52 | p₀ 0,53 | p₀ 0,54 | p₀ 0,55 | p₀ 0,56 | p₀ 0,57 | p₀ 0,58 | p₀ 0,59 | p₀ 0,60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 23 | 16 / 0,80 | 17 / 0,65 | 17 / 0,65 | 17 / 0,65 | 17 / 0,65 | 18 / 0,47 | 18 / 0,47 | 18 / 0,47 | 18 / 0,47 | 18 / 0,47 | 19 / 0,28 |
| 24 | 17 / 0,77 | 17 / 0,77 | 17 / 0,77 | 18 / 0,61 | 18 / 0,61 | 18 / 0,61 | 18 / 0,61 | 19 / 0,42 | 19 / 0,42 | 19 / 0,42 | 19 / 0,42 |
| 25 | 18 / 0,73 | 18 / 0,73 | 18 / 0,73 | 18 / 0,73 | 19 / 0,56 | 19 / 0,56 | 19 / 0,56 | 19 / 0,56 | 19 / 0,56 | 20 / 0,38 | 20 / 0,38 |
| 26 | 18 / 0,82 | 18 / 0,82 | 19 / 0,69 | 19 / 0,69 | 19 / 0,69 | 19 / 0,69 | 20 / 0,52 | 20 / 0,52 | 20 / 0,52 | 20 / 0,52 | 21 / 0,34 |
| 27 | 19 / 0,79 | 19 / 0,79 | 19 / 0,79 | 20 / 0,64 | 20 / 0,64 | 20 / 0,64 | 20 / 0,64 | 21 / 0,47 | 21 / 0,47 | 21 / 0,47 | 21 / 0,47 |
| 28 | 19 / 0,86 | 20 / 0,75 | 20 / 0,75 | 20 / 0,75 | 20 / 0,75 | 21 / 0,60 | 21 / 0,60 | 21 / 0,60 | 21 / 0,60 | 22 / 0,43 | 22 / 0,43 |
| 29 | 20 / 0,83 | 20 / 0,83 | 20 / 0,83 | 21 / 0,71 | 21 / 0,71 | 21 / 0,71 | 22 / 0,56 | 22 / 0,56 | 22 / 0,56 | 22 / 0,56 | 23 / 0,39 |
| 30 | 20 / 0,89 | 21 / 0,80 | 21 / 0,80 | 21 / 0,80 | 22 / 0,67 | 22 / 0,67 | 22 / 0,67 | 22 / 0,67 | 23 / 0,51 | 23 / 0,51 | 23 / 0,51 |
| 31 | 21 / 0,87 | 21 / 0,87 | 22 / 0,77 | 22 / 0,77 | 22 / 0,77 | 23 / 0,63 | 23 / 0,63 | 23 / 0,63 | 23 / 0,63 | 24 / 0,47 | 24 / 0,47 |
| 32 | 22 / 0,85 | 22 / 0,85 | 22 / 0,85 | 23 / 0,74 | 23 / 0,74 | 23 / 0,74 | 23 / 0,74 | 24 / 0,59 | 24 / 0,59 | 24 / 0,59 | 25 / 0,43 |
| 33 | 22 / 0,90 | 23 / 0,82 | 23 / 0,82 | 23 / 0,82 | 23 / 0,82 | 24 / 0,70 | 24 / 0,70 | 24 / 0,70 | 25 / 0,55 | 25 / 0,55 | 25 / 0,55 |
| 34 | 23 / 0,88 | 23 / 0,88 | 23 / 0,88 | 24 / 0,79 | 24 / 0,79 | 24 / 0,79 | 25 / 0,66 | 25 / 0,66 | 25 / 0,66 | 26 / 0,51 | 26 / 0,51 |
| 35 | 23 / 0,92 | 24 / 0,86 | 24 / 0,86 | 24 / 0,86 | 25 / 0,76 | 25 / 0,76 | 25 / 0,76 | 26 / 0,63 | 26 / 0,63 | 26 / 0,63 | 27 / 0,47 |
| 36 | 24 / 0,91 | 24 / 0,91 | 25 / 0,83 | 25 / 0,83 | 25 / 0,83 | 26 / 0,73 | 26 / 0,73 | 26 / 0,73 | 27 / 0,59 | 27 / 0,59 | 27 / 0,59 |
| 37 | 24 / 0,94 | 25 / 0,89 | 25 / 0,89 | 26 / 0,81 | 26 / 0,81 | 26 / 0,81 | 27 / 0,69 | 27 / 0,69 | 27 / 0,69 | 28 / 0,55 | 28 / 0,55 |
| 38 | 25 / 0,93 | 25 / 0,93 | 26 / 0,87 | 26 / 0,87 | 27 / 0,78 | 27 / 0,78 | 27 / 0,78 | 28 / 0,66 | 28 / 0,66 | 28 / 0,66 | 29 / 0,51 |
| 39 | 26 / 0,91 | 26 / 0,91 | 26 / 0,91 | 27 / 0,85 | 27 / 0,85 | 28 / 0,75 | 28 / 0,75 | 28 / 0,75 | 29 / 0,62 | 29 / 0,62 | 29 / 0,62 |
| 40 | 26 / 0,95 | 27 / 0,90 | 27 / 0,90 | 27 / 0,90 | 28 / 0,82 | 28 / 0,82 | 29 / 0,72 | 29 / 0,72 | 29 / 0,72 | 30 / 0,58 | 30 / 0,58 |
| 41 | 27 / 0,93 | 27 / 0,93 | 28 / 0,88 | 28 / 0,88 | 28 / 0,88 | 29 / 0,79 | 29 / 0,79 | 30 / 0,68 | 30 / 0,68 | 30 / 0,68 | 31 / 0,55 |
| 42 | 27 / 0,96 | 28 / 0,92 | 28 / 0,92 | 29 / 0,86 | 29 / 0,86 | 29 / 0,86 | 30 / 0,77 | 30 / 0,77 | 31 / 0,65 | 31 / 0,65 | 31 / 0,65 |
| 43 | 28 / 0,95 | 28 / 0,95 | 29 / 0,90 | 29 / 0,90 | 30 / 0,83 | 30 / 0,83 | 30 / 0,83 | 31 / 0,74 | 31 / 0,74 | 32 / 0,61 | 32 / 0,61 |
| 44 | 28 / 0,97 | 29 / 0,94 | 29 / 0,94 | 30 / 0,89 | 30 / 0,89 | 31 / 0,81 | 31 / 0,81 | 31 / 0,81 | 32 / 0,71 | 32 / 0,71 | 33 / 0,58 |
| 45 | 29 / 0,96 | 29 / 0,96 | 30 / 0,92 | 30 / 0,92 | 31 / 0,87 | 31 / 0,87 | 32 / 0,78 | 32 / 0,78 | 32 / 0,78 | 33 / 0,67 | 33 / 0,67 |

Güç tablosu, p₀ = 0,50 / 0,52 / 0,55 (c / gerçek α p₀'da / güç p₁ 0,75):

| K | c / α / güç (p₀ 0,50) | c / α / güç (p₀ 0,52) | c / α / güç (p₀ 0,55) |
|---|---|---|---|
| 23 | 16 / 0,0466 / 0,804 | 17 / 0,0273 / 0,654 | 18 / 0,0186 / 0,469 |
| 24 | 17 / 0,0320 / 0,766 | 17 / 0,0487 / 0,766 | 18 / 0,0364 / 0,607 |
| 25 | 18 / 0,0216 / 0,727 | 18 / 0,0342 / 0,727 | 19 / 0,0258 / 0,561 |
| 26 | 18 / 0,0378 / 0,820 | 19 / 0,0238 / 0,685 | 19 / 0,0467 / 0,685 |
| 27 | 19 / 0,0261 / 0,786 | 19 / 0,0415 / 0,786 | 20 / 0,0338 / 0,643 |
| 28 | 19 / 0,0436 / 0,862 | 20 / 0,0294 / 0,750 | 21 / 0,0242 / 0,600 |
| 29 | 20 / 0,0307 / 0,834 | 20 / 0,0489 / 0,834 | 21 / 0,0427 / 0,713 |
| 30 | 20 / 0,0494 / 0,894 | 21 / 0,0353 / 0,803 | 22 / 0,0312 / 0,674 |
| 31 | 21 / 0,0354 / 0,872 | 22 / 0,0252 / 0,771 | 23 / 0,0226 / 0,634 |
| 32 | 22 / 0,0251 / 0,846 | 22 / 0,0415 / 0,846 | 23 / 0,0389 / 0,737 |
| 33 | 22 / 0,0401 / 0,901 | 23 / 0,0301 / 0,819 | 24 / 0,0287 / 0,701 |
| 34 | 23 / 0,0288 / 0,881 | 23 / 0,0479 / 0,881 | 24 / 0,0472 / 0,789 |
| 35 | 23 / 0,0448 / 0,924 | 24 / 0,0353 / 0,858 | 25 / 0,0354 / 0,758 |
| 36 | 24 / 0,0326 / 0,908 | 25 / 0,0258 / 0,833 | 26 / 0,0263 / 0,725 |
| 37 | 24 / 0,0494 / 0,942 | 25 / 0,0406 / 0,889 | 26 / 0,0427 / 0,806 |
| 38 | 25 / 0,0365 / 0,929 | 26 / 0,0301 / 0,868 | 27 / 0,0322 / 0,777 |
| 39 | 26 / 0,0266 / 0,914 | 26 / 0,0461 / 0,914 | 28 / 0,0241 / 0,747 |
| 40 | 26 / 0,0403 / 0,946 | 27 / 0,0346 / 0,897 | 28 / 0,0386 / 0,821 |
| 41 | 27 / 0,0298 / 0,933 | 28 / 0,0257 / 0,878 | 29 / 0,0293 / 0,794 |
| 42 | 27 / 0,0442 / 0,958 | 28 / 0,0392 / 0,919 | 29 / 0,0454 / 0,857 |
| 43 | 28 / 0,0330 / 0,949 | 29 / 0,0295 / 0,904 | 30 / 0,0349 / 0,834 |
| 44 | 28 / 0,0481 / 0,968 | 29 / 0,0440 / 0,937 | 31 / 0,0266 / 0,810 |
| 45 | 29 / 0,0362 / 0,961 | 30 / 0,0334 / 0,925 | 31 / 0,0409 / 0,867 |

**Önceden hesaplanan hüküm olasılıkları** (p₀ = 0,50; P(H1) / P(ayırt edilemez) / P(H0); gerçek küme başına oy
olasılığı p):

| K | p = 0,45 | p = 0,50 | p = 0,55 | p = 0,60 | p = 0,65 | p = 0,70 | p = 0,75 |
|---|---|---|---|---|---|---|---|
| 23 | 0,01 / 0,08 / 0,91 | 0,05 / 0,16 / 0,80 | 0,12 / 0,25 / 0,64 | 0,24 / 0,32 / 0,44 | 0,41 / 0,33 / 0,26 | 0,62 / 0,26 / 0,12 | 0,80 / 0,16 / 0,04 |
| 26 | 0,01 / 0,06 / 0,93 | 0,04 / 0,13 / 0,84 | 0,10 / 0,22 / 0,68 | 0,23 / 0,30 / 0,48 | 0,41 / 0,31 / 0,28 | 0,63 / 0,25 / 0,12 | 0,82 / 0,14 / 0,04 |
| 28 | 0,01 / 0,06 / 0,93 | 0,04 / 0,13 / 0,83 | 0,12 / 0,22 / 0,66 | 0,26 / 0,29 / 0,45 | 0,46 / 0,29 / 0,25 | 0,68 / 0,21 / 0,10 | 0,86 / 0,11 / 0,03 |
| 30 | 0,01 / 0,06 / 0,93 | 0,05 / 0,13 / 0,82 | 0,14 / 0,22 / 0,64 | 0,29 / 0,29 / 0,42 | 0,51 / 0,27 / 0,22 | 0,73 / 0,18 / 0,08 | 0,89 / 0,08 / 0,02 |
| 33 | 0,01 / 0,01 / 0,98 | 0,04 / 0,04 / 0,92 | 0,12 / 0,09 / 0,79 | 0,28 / 0,13 / 0,59 | 0,50 / 0,14 / 0,36 | 0,73 / 0,10 / 0,16 | 0,90 / 0,05 / 0,05 |
| 37 | 0,01 / 0,01 / 0,97 | 0,05 / 0,04 / 0,91 | 0,15 / 0,09 / 0,76 | 0,34 / 0,13 / 0,54 | 0,58 / 0,13 / 0,29 | 0,81 / 0,08 / 0,11 | 0,94 / 0,03 / 0,03 |

Bu sınav yalnız büyük etkiyi (p ≈ 0,75) görür. "H0" yalnız "p ≥ 0,75 bu örneklemle dışlandı" demektir; küçük bir gölge
etkisinin yokluğu demek değildir. Poisson H0 altında koşullu oyun p'si N0'a göre 0,446–0,497'dir (§4.3). Tablodaki
p = 0,45–0,50 satırları o dünyaya yakındır.

### 6.2 Yorum kuralları (hükmü değiştirmez, adını niteler; §6.4'e göre bileşir)

1. **Pozitif kontrol (§7 S1):**
   - S1 tutmazsa (X⁺ < c(K⁺; 0,50)), H1 hükmü **"ayırt edilemez (pozitif kontrol tutmadı)"** diye yazılır (düşürücü;
     §6.4). H0 ya da ayırt edilemez hükmüne "pozitif kontrol de tutmadı: hat ya da model başarısız; ayrılamaz" eklenir.
   - S1 koşulamadıysa (K⁺ < 10), H1 hükmü **"H1 (pozitif kontrol koşulamadı)"** diye adlandırılır (niteleyici; §6.4).
2. **Negatif kontrol (§7 S2):** H1 hükmü verilmiş ve X_nk ≥ c(K_nk; 0,50) ise (son yıl öncesinde de anlamlı düşüş),
   "olay öncesi düşüş eğilimi" düşürücüsü uygulanır (§6.4) ve §13'e hiçbir şey taşınmaz. H0 ya da ters yön notu varsa
   ve Y_nk ≥ c(K_nk; 0,50) ise, "olay öncesi artış eğilimiyle ayırt edilemez" eklenir. K_nk < 10 ise bu kural
   uygulanmaz (§7 S2).

   2a. **Nötr kontrol (§7 S7).**
   - K_nt < 10 ise H1 "nötr kontrol koşulamadı" niteleyicisini alır.
   - K_nt ≥ 10, H1 verilmiş ve X_nt ≥ c(K_nt; p₀) ise "nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu"
     düşürücüsü uygulanır (§6.4) ve §13'e hiçbir şey taşınmaz.
   - K_nt ≥ 10, H1 verilmiş, X_nt < c(K_nt; p₀) ve McNemar p > 0,10 ise "nötr kontrolden ayrışmadı" niteleyicisi
     eklenir.

   Gerekçe: π = 0,15720'de n ≤ 4 olan pencerede düşüş oyu tanım gereği 0'dır. Kapısız bir nötr bölgede D_nt = 0
   kendiliğinden olur ve McNemar gölge lehine ayrışma gösterir. Kesin hesap (`tr6a_inc1_denetim.json`
   `mcnemar_gucu`): gölgede p 0,75, nötrde 0,4585 iken McNemar p ≤ 0,10'un gücü K_nt = 23'te 0,677, 28'de 0,757,
   33'te 0,819, 37'de 0,860.
3. **Megathrust ağırlığı:** H1 verilmiş ve megathrust hariç satırda (S4) K_S4 < 5 ya da X_S4/K_S4 ≤ 0,5 ise, hüküm
   "H1 (megathrust kümelerine dayanıyor)" diye adlandırılır (niteleyici; §6.4).
4. **Sağlamlık cümlesi:** D1–D8 satırlarından X/K ≤ 0,5 olanlar adıyla listelenir. Liste hükmü değiştirmez. K = 0
   olan satırlar 'koşulamadı' diye adıyla listelenir.
5. **Türkiye kümeleri** (1999 İzmit, 2020 Sisam, 2023 Kahramanmaraş; hangisi K'deyse) yalnız anılır; hiçbir Marmara
   cümlesine dayanak olmaz.
6. **Etkin N0.** Her küme için N0_kul = n_on(Mc_kul) / (1796/365,25) yazılır (ön pencere, kümesizleştirilmiş,
   Mc_kul ile). Hükmün K kümesinin yarısından fazlasında N0_kul < 31,36 ise H0 ve ayırt edilemez kalıplarına şu cümle
   eklenir: "Oy Mc'si kapı Mc'sinin belirgin üstünde: K kümenin …'inde etkin N0_kul < 31,36. Olumsuz sonuç (iii) ana
   şok sonrası tamlık sınırıyla da açıklanabilir; (i), (ii) ve (iii) ayrılamaz." H1'e uygulanmaz.

### 6.3 Hüküm cümleleri (kalıplar)

- **H1:** "Kosismik Coulomb gölge loblarında (ΔCFF ≤ −10 kPa, kırıktan 20 km–2L) olay sonrası [30 g, 365 g) oran
  düşüşü K bağımsız kümenin X'inde görüldü (kritik c; p₀ = …, tek yanlı kesin binom p = …). Hız-durum gerilme ölçeri bu
  örneklemde gölgelerin işaretini olay öncesi sahte zamanlarla kalibre edilmiş rastlantı düzeyinin üstünde buluyor. Bu,
  yöntemin işaret düzeyinde geçerliliğidir; Marmara'da kullanılabilirliği göstermez ((b) ayağı çözünürlük kapısını
  geçmedi)."
- **H0:** "Gölge loblarında düşüş oyu K kümenin X'inde (X ≤ h). Küme başına 0,75 ve üstü oy olasılığı bu örneklemle
  dışlandı. Bu sonuç iki açıklamayı ayıramaz: (i) hız-durum gerilme ölçeri (Aσ 19 kPa) gölgeyi 1 yılda göremiyor,
  (ii) Coulomb modelinin gölgesi (tek sonlu fay modeli, tek alıcı düzlem, μ' 0,4, 7,5 km) yanlış yerde ya da gerçek
  değil." Ters yön notu düşüldüyse eklenir: "Gölgede anlamlı artış (Y ≥ c⁺): Hardebeck & Harris (2025) bulgusunun
  küresel karşılığı; aynı iki açıklama burada da ayrılmaz."
- **Ayırt edilemez:** "X = …, h < X < c. Bu örneklem p ≈ p₀ ile p ≈ 0,75'i ayıramıyor." Olumsuz sonuçtaki iki açıklama
  cümlesi bu kalıba da eklenir.
- **Güç yok (K):** "Lob Mc'siyle olay öncesi sayılan bağımsız küme K_kapı = … < 23. Hüküm satırı koşulmadı, olay
  sonrası veri indirilmedi. Aday elenmedi; yeniden açma şartı §14."
- **Güç yok (ölçü yanlı):** "Olay öncesi sahte zamanlarda düşüş oyu payı p̂₀ = … (J = …) > 0,60. Ölçü H0 altında
  yanlı; hüküm satırı koşulmadı, olay sonrası veri indirilmedi."
- **Koşulmadı (yöntem):** "TR-6a koşulmadı: <sınama> önceden yazılan ölçütü tutmadı (<ölçüt, değer>). Olay sonrası
  veri indirilmedi. Aday elenmedi; yeniden açma ayrı ön kayıtla."
- **Kalibrasyon zayıf eki:** "Olay öncesi sahte zamanlardan yalnız J = … geçerli oy elde edildi (< 30). p₀ tabanı
  0,52 alındı (§4.6)."

### 6.4 Hüküm adlarının kapalı listesi ve bileşimi

Sonuç dosyasındaki hüküm adı yalnız bu kurallarla kurulur; başka ad yazılmaz.

1. **Taban hüküm.** Tam olarak biri seçilir; aşağıdakilerden ilk uyan geçerlidir.
   - (a) **"koşulmadı (yöntem: Okada sınaması | yapay katalog sınaması | tamlık sınaması)".** §3.3 doğrulaması,
     §9 adım 2'nin yapay katalog sınaması ya da tamlık yedek merdiveni §9 adım 2'deki sonuç kuralıyla kesin
     biçimde tutmadı. Olay sonrası veri indirilmez, aday elenmez. Yeniden açma ancak ayrı bir ön kayıtla olur.
   - (b) **"güç yok"**: K_kapı < 23 (§5).
   - (c) **"güç yok (ölçü yanlı)"**: p₀ > 0,60 (§4.6).
   - (d) **"H1", "H0" ya da "ayırt edilemez"** (§6.1). c(K) ≤ h(K) olan bir K'de X ≥ c ise taban H1'dir.
2. **Düşürücüler.** Yalnız taban H1'e uygulanır. Hepsi özgün taban H1'e göre denetlenir; birinin uygulanması ötekilerin
   koşulunu değiştirmez. Uyanlar §6.2 sırasıyla, noktalı virgülle aynı parantezde yazılır ve taban "ayırt
   edilemez" olur. Düşürücüler:
   - "pozitif kontrol tutmadı" (§6.2 kural 1);
   - "olay öncesi düşüş eğilimi" (kural 2);
   - "nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu" (kural 2a).

   Örnek: "ayırt edilemez (pozitif kontrol tutmadı; nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu)". Düşürülen
   hükme madde 4'teki H0 ve ayırt edilemez ekleri uygulanmaz. X, c ve p yine yazılır.
3. **Niteleyiciler.** Düşürülmemiş H1'e eklenir; bu sırayla, tek parantezde, noktalı virgülle:
   - "pozitif kontrol koşulamadı";
   - "negatif kontrol koşulamadı";
   - "nötr kontrol koşulamadı" ya da "nötr kontrolden ayrışmadı";
   - "megathrust kümelerine dayanıyor";
   - "tasarım gücünün altında: güç …";
   - "kalibrasyon zayıf: J = …, p₀ = …".

   Örnek: "H1 (nötr kontrolden ayrışmadı; tasarım gücünün altında: güç 0,654)".
4. **H0 ve ayırt edilemez ekleri.** Bu sırayla, cümle olarak:
   - ters yön notu (§6.1);
   - "pozitif kontrol de tutmadı: hat ya da model başarısız; ayrılamaz" (§6.2 kural 1);
   - "olay öncesi artış eğilimiyle ayırt edilemez" (kural 2);
   - etkin N0 cümlesi (§6.2 kural 6);
   - "(tasarım gücünün altında: güç …)";
   - "(kalibrasyon zayıf: J = …, p₀ = …)".
5. **§13'e taşıma.** §13'ün H1 cümlesi yalnız hüküm adı tam olarak "H1" ya da "H1 (tasarım gücünün altında: güç …)"
   ise yazılır. Başka herhangi bir niteleyici varsa §13 cümlesi yazılmaz; yerine "Marmara'ya taşınmadı:
   <niteleyici>" yazılır.
6. **Koşu sonrası değişiklik eki.** §9 adım 6'daki "(koşu sonrası değişiklikle: <ad>)" eki, yukarıdaki kurallarla
   kurulmuş adın sonuna yazılır; <ad> aynı kurallarla kurulur. Ek hüküm adını ve §13'e taşımayı değiştirmez.

## 7. İkincil satırlar (zorunlu; hükmü değiştirmez)

Her satırda şunlar yazılır:
- K_satır, X, Y, X/K;
- c(K_satır; p₀) ve c(K_satır; 0,50);
- p₀'a ve 0,50'ye karşı tek yanlı kesin binom p (üst kuyruk, X için; ayrıca Y için p₀⁺ ve 0,50'ye karşı);
- koşullu kesin Poisson-binom p (bilgi; küme başına p₀ᵢ = F(b*(nᵢ); nᵢ, πᵢ)).

Testere dişi atması yalnız ana satırda yapılır. İkincil satırlar kendi K'leriyle yazılır. "Ana K" atmadan sonraki
settir.

| Satır | Tanım | Kapı / küme seti |
|---|---|---|
| **S1 pozitif kontrol** | Ana K temsilcilerinden pozitif lobunun olay öncesi N0⁺'ı (Mc_lob⁺ ile, ön pencere, kümesizleştirilmiş) ≥ 10,0 olay/yıl (n_on⁺ ≥ 50) olanlar; K⁺ bu kümelerin sayısıdır (manifestte, olay sonrası indirmeden önce). Kendi Mc_lob'u, artış oyu X⁺. Başarı ölçütü X⁺ ≥ c(K⁺; 0,50). K⁺ < 10 ise S1 "koşulamadı". K⁺ dışındaki kümelerin oyları bilgi olarak yazılır. | ana K'nin alt kümesi |
| **S2 negatif kontrol (zaman ters çevrimi)** | Aynı temsilciler, aynı gölge lobu; "ön" [t0 − 1826 g, t0 − 365 g), "son" [t0 − 365 g + (t_s − t0), t0 − 30 g); 730 g ön tampon; π_nk = T_son,nk / (1461 + T_son,nk) (tek olayda 0,18653); Mc §3.5. X_nk ve Y_nk; iki kuyruk ayrı, p₀ = 0,50. Yalnız sahte j = 1'i geçerli kümeler (§4.6); K_nk. Tamamen olay öncesi veridir; manifestte, olay sonrası indirmeden önce hesaplanır ve commit edilir. K_nk < 10 ise S2 'koşulamadı'; §6.2 kural 2 uygulanmaz ve H1 'negatif kontrol koşulamadı' niteleyicisini alır (§6.4). | ana K'nin alt kümesi |
| **S3 doğrultu atımlı alt küme** | Temsilci grubunun en büyük üyesinin ComCat mekanizması "doğrultu atımlı". Yalnız bilgi. | ana K'nin alt kümesi |
| **S4 megathrust hariç** | "ters, düşük eğimli (megathrust dahil)" sınıfı çıkarılır. | ana K'nin alt kümesi |
| **S5a, S5b Aσ 13 / 39 kPa** | Kapı eşiği 17,08 / 111,21; kapı, kümeleme, çıkarmalar ve temsilci yeniden; oylar aynı kuralla; p₀ ana kalibrasyondaki değer. | kendi K'si |
| **S6 ikinci kayma modeli (SRCMOD)** | SRCMOD'da grubun her üyesi için model varsa en son yayımlanan (eşitlikte SRCMOD listesindeki ilk). ΔCFF, loblar, Mc ve oy aynı kuralla. Ayrıca hücre uyuşma payı (iki modelde aynı sınıfta olan hücre / ComCat modelinde gölge ya da pozitif sınıftaki hücre) ve aynı alt kümede ComCat oyu. SRCMOD erişilemezse "koşulamadı". | ana K'nin SRCMOD'lu alt kümesi, kapı yeniden |
| **S7 nötr kontrol** | Ana K temsilcileri. Nötr bölge: bölgede \|ΔCFF\| ≤ 2 kPa olan ve r_k'si gölge lobunun en uzak hücresinin r_k'sini aşmayan hücreler. Kendi Mc_lob_nt'si (§3.5 kuralı), aynı Mc_son, Mc_kul,nt = max(Mc_lob_nt, Mc_son); aynı kümesizleştirme ve oy (X_nt, Y_nt). **Nötr kapı:** olay öncesi N0_nt (Mc_lob_nt ile, ön pencere, kümesizleştirilmiş) ≥ 31,36 olay/yıl (n_on,nt ≥ 155). K_nt bu kümelerin sayısıdır ve manifestte, olay sonrası indirmeden önce yazılır. X_nt, Y_nt ve McNemar yalnız bu K_nt kümede sayılır: a = #(D_gölge = 1, D_nt = 0), b = #(D_gölge = 0, D_nt = 1), p = P(Binom(a + b, 0,5) ≥ a); a + b = 0 ise p = 1. K_nt < 10 ise S7 "koşulamadı". Kapı dışı kümelerin nötr oyları bilgi olarak yazılır. | ana K'nin alt kümesi (K_nt) |
| D1 Mc + 0,5 | Mc_kul + 0,5 (iki pencere); kapı yeniden. | kendi K'si |
| D2 geç pencere | Son pencere [t_s + 90 g, son pencere sonu); tek olaylı ve kesilmemiş pencerede π = 275/2071. | ana K |
| D3a, D3b iç sınır | r_k ≥ 5 km ve r_k ≥ 40 km; loblar ve kapı yeniden. | kendi K'si |
| D4 kümesizleştirme yok | Ön ve son pencere ham; kapı yeniden. | kendi K'si |
| D5 iki düğüm düzlemi | Hücre yalnız iki düğüm düzleminde aynı sınıftaysa (ikisi ≤ −10 ya da ikisi ≥ +10 kPa) loba girer; kapı yeniden. | kendi K'si |
| D6 gözden geçirilmemiş ISC | §3.5'teki ISC kuralıyla ana hükümden çıkan olaylar ISC ile ve aynı kurallarla eklenir; kapı yeniden. Yalnız bilgi. Önsayımda Noto 2024, Hyūganada 2024 ve Loyalty Adaları 2023. | kendi K'si |
| D7 temiz ön pencere | Bölgede ön pencerede M ≥ 6,0 (Mc_kul süzgeçsiz, aynı katalog) olan temsilciler çıkarılır. | ana K'nin alt kümesi |
| D8 güçlü gölge | Gölge lobu ΔCFF ≤ −30 kPa hücreleri; kapı yeniden. Yalnız bilgi. | kendi K'si |
| B1 K tam | Testere dişi atması yapılmadan bütün K_kapı kümeleri; kendi c(K; p₀)'ı. Yalnız ana K atma yaptıysa. | K_kapı |
| B2 büyüklük | Gölge ve pozitif lobda Δτ_est medyanı (Aσ 13 / 19 / 39); pozitif lobda Spearman(lob ortalama ΔCFF, Δτ_est). | ana K |
| B3 bağımlılık ve kesme | Temsilcinin son penceresinde 2L içinde havuz olayı olan kümelerde X/K; §3.7 kesmesiyle çıkan kümeler ve kesilen T_son'lar; adıyla yazılan örtüşen çiftler; tek bağlantıda birleşecek küme çifti sayısı. "Öncül komşulu" kümeler: temsilcinin [t0 − 365 g, t0) aralığında, dış merkez uzaklığı < 3 L_A + 3 L_temsilci olan bir havuz olayı A (grup dışı) varsa küme işaretlenir. Önsayımda 5 küme işaretli: usp0006qh3, official20041226005853450_30, usp000hrw0, official20110311054624120_30, official20120411083836720_20. Bu kümeler çıkarılmış hâliyle X, K ve c(K; p₀) de yazılır. | ana K ve çıkanlar |
| B4 bilinen sonuçlu kümeler | Kumamoto ve Ridgecrest kümelerinin (ana hükümden çıkarılan) ve Tohoku kümesinin D, A, n_on, n_son, Δτ_est değerleri. Ayrıca ilk ikisi eklenmiş, Tohoku çıkarılmış hâliyle X, K ve c(K; p₀). Hükmü değiştirmez. | ana K ± 3 |

## 8. Çıktı tablosu (kalıp)

`tr6a_sonuc.md` aşağıdaki tabloyu, §6.4'e göre kurulan hüküm adını ve §6.3'teki kalıplardan biriyle hüküm cümlesini
taşır. `tr6a_sonuc.json` aynı
sayıları ve girdi dosyalarının sha256'larını taşır.

| Satır | K | X (düşüş) | Y (artış) | X/K | c(K; p₀) | c(K; 0,5) | p (X, p₀) | p (X, 0,5) | p (Y) | koşullu p (bilgi) | Hüküm / etiket |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Ana (gölge, Aσ 19) | | | | | | | | | | | §6.4'teki kapalı listeden ad (taban + düşürücüler ya da niteleyiciler + ekler) |
| S1 pozitif kontrol | K⁺ | X⁺ | | | | | | | | | tuttu / tutmadı / koşulamadı |
| S2 negatif kontrol | K_nk | X_nk | Y_nk | | | | | | | | eğilim yok / düşüş / artış |
| S7 nötr kontrol | K_nt | X_nt | Y_nt | | | | | | | McNemar p | |
| S3 … D8, B1, B4 | | | | | | | | | | | — |

Üst bilgi: p̂₀, p̂₀⁺, J, J < 30 kuralı uygulandı mı, p₀, p₀⁺, testere çözümü. Ek tablolar:
- küme başına satır: küme, temsilci, grup üyeleri, katalog, Mc_halka, Mc_lob, Mc_son (alt pencere başına), Mc_kul,
  T_son, π, gölge, pozitif ve nötr hücre sayısı, n_on, n_son, N0_kul, D, A, Δτ_est, alıcı kaynağı, mekanizma sınıfı, sahte
  oylar, bayraklar;
- atılan ve çıkarılan kümeler.

## 9. Koşu sırası ve körlük

1. Taslak iki kez bağımsız incelendi ve bulgular işlendi (sürüm 3); üçüncü inceleme turu yoktur. Metin
   "DONDURULDU" diye commit + push edilir. Dondurulan dosyalar: bu metin, `tr6a_olay_listesi.json` (sha256 §3.1),
   `tr6a_onkayit_sayilar.py` ve `.json`, `tr6a_onbellek_kor.py`, `tr6a_ham_sha256.txt`, `tr6_a_kapi.py` (sürüm 3'te
   yalnız `getir`'e önbellek engeli eklendi), `tr6a_sifir_buyukluk.py` ve `.json`, `tr6a_inc1_denetim.py` ve `.json`,
   `tr6a_inc2_b1.py`–`tr6a_inc2_b4.py`, `tr6a_md_denetim.py`. Dondurulan çıktıların sha256'sı:
   - `tr6a_onkayit_sayilar.json`: e39b3252a9f5db6b1c201936c245edb93b94b0a7c4ad94b5ed41d5c48db78c4f;
   - `tr6a_inc1_denetim.json`: 4ff6f4d090a7e060fb2fea4e0ebf72adbd3e0900d8008c693be6d6764e11050a;
   - `tr6a_olay_listesi.json` ve `tr6a_sifir_buyukluk.json`: §3.1.
2. **Kod yalnız yapay veriyle geliştirilir** (`kayit/turetme/tr6/`, yalnız numpy ve standart kitaplık,
   `python3 -I -B`):
   - `tr6a_okada.py` ve sınaması (§3.3, 1–9 sınamaları, tekil noktalar ve ızgara kuralı).
   - **Yapay katalog sınaması** iki biçimde koşulur. Tohum 20261114, her ölçüt için en az 20 000 deneme. Bilinen bir
     yapay sonlu fay, bilinen Aσ = 19 kPa ve τ̇0 ile Dieterich oran yanıtı kullanılır; bütün hat (lob, Mc,
     kümesizleştirme, oy, sahte kalibrasyon) çalıştırılır.
     - (i) Lobda arka plan saf Poisson'dur; bölgede ikincil diziler vardır. Ölçütler:
       - Δτ = 0 dünyasında gölge düşüş oyu oranı N0 ∈ {31,36; 100; 500} için §4.3'teki kesin değerle 3,5 SE içinde;
       - kalıcı −10 kPa dünyasında N0 31,36'da 0,987 ile 3,5 SE içinde;
       - Δτ_est medyanı §4.5 tablosuyla 3,5 SE içinde.
     - (ii) Lobda da GK tipi ikincil diziler vardır. Ölçüt: Δτ = 0 dünyasında p̂₀'ın beklenen değeri, gerçek düşüş oyu
       oranıyla 3,5 SE içinde. Bu biçimde P(D)'nin kendisi bilgi olarak yazılır.

     Bir ölçüt tutmazsa kod hatası aranır. Bulunan her hata düzeltilir, hata listesi commit edilir ve bütün sınama aynı
     tohumla yeniden koşulur. Hata bulunamazsa TR-6a "koşulmadı (yöntem: yapay katalog sınaması)" diye kapanır (§6.4).
   - **Ana şok sonrası tamlık kaybı sınaması.** Yapay kataloğa Mc(t) = M_ana − 4,5 − 0,75 log10(t / 1 g) uygulanır
     (Helmstetter vd. 2006 biçimi; sabitler sınama için seçildi, doğrulanmadı).
     - Izgara: M_ana ∈ {7,0; 7,5; 8,0; 9,0}, Mc_lob ∈ {1,0; 1,8; 3,0}, N0 ∈ {31,36; 100; 500; 4500}, bölgede artçı payı
       ∈ {0; 0,9}.
     - Ölçüt: Δτ = 0 dünyasında §3.5 kuralıyla gölge düşüş oyu oranı, her hücrede o N0'ın kesin Poisson H0 değerini
       (§4.3) 0,02'den fazla aşmamalıdır (hücre başına en az 20 000 deneme, standart hata ≤ 0,0036; tohum 20261115;
       lobda arka plan saf Poisson).
     - Aşarsa yedekler sırayla denenir ve tutan ilki bağlayıcı olur. Her basamak bir kez, aynı tohumla koşulur. Bütün
       basamakların bütün hücre sonuçları, manifestten önce commit edilir. Yedekler:
       - (a) alt pencere sınırları [30, 40), [40, 50), [50, 60), [60, 90), [90, 180), [180, 365);
       - (b) (a) ile birlikte Mc_son'a +0,2 eklenir;
       - (c) (b) ile birlikte ana son pencere [t_s + 90 g, son pencere sonu) olur (tek olayda π = 275/2071; D2 ana
         satır olur); alt pencereler [90, 180), [180, 365). (c) seçilirse 90 g başlangıcı her yerde uygulanır:
         - §3.7'deki T_son < 60 g ölçütü yeni başlangıçla yeniden uygulanır. Önsayımda 2004 Sumatra kümesi T_son
           1,6 g ile çıkar (`onsayim.19.yedek_c`: K_kaba 29 → 28).
         - Sahte son pencereler [t'_j + (t_s − t0) + 90 g, t'_j + e) olur.
         - S2'nin "son" penceresi [t0 − 305 g + (t_s − t0), t0 − 30 g) olur; π_nk aynı formülle hesaplanır.
         - D2 satırı kalkar.
         - Mc_son alt pencereleri [90, 180) ve [180, 365) olur.
     - Hiçbiri tutmazsa TR-6a "koşulmadı (yöntem: tamlık sınaması)" diye kapanır (§6.4); olay sonrası veri indirilmez. Bu sınama
       gerçek veri görmediği için yedek seçimi körlüğü bozmaz. Seçilen yedek manifestte yazılır.
     - Gürültüsüz ön denetim (`tr6a_inc1_denetim.json` `tamlik`): aynı 96 hücrede beklenen histogramla, kısmi algılama
       (Mc(t) > Mc_kul iken algılanan pay 10^−(Mc(t) − Mc_kul)) hesaplandı. Sürüm 1 kuralı 56 hücrede başarısız (en
       büyük fark +0,469). A2 alt pencere kuralı ve yedekler (a)–(c) bütün hücrelerde 0 fark verdi. MAXC gürültüsü bu ön
       denetimde yoktur; bağlayıcı olan yukarıdaki 20 000 denemelik sınamadır. 4000 denemede (SE ≈ 0,0079) kusursuz bir
       kural bile 96 hücreden en az birinde ≈ 0,42 olasılıkla gürültüyle düşerdi; 20 000 denemede 0,02 = 5,6 SE'dir ve
       bu olasılık < 1e−6'dır (İNCELEME-2 B3).
3. **Manifest (yalnız olay öncesi veri):** `tr6a_manifest.py` → `tr6a_manifest.json` + `tr6a_on_ham_sha256.txt`.
   İçerik:
   - her aday için sonlu fay ürünü (kimlik, `code`, `updateTime`), öteki ürünlerin kimlikleri ve `updateTime`'ları,
     dosya ve sha256'sı, M0 sağlaması, alıcı (kaynak, tensör sayısı, çift kuvvet payı);
   - lob hücre sayıları (gölge, pozitif, nötr, D8), iç sınır yüzünden atılan gölge hücresi sayısı ve payı, "tekil
     yakın alan" hücre sayısı (§3.4);
   - katalog seçimi (ISC ve "0 büyüklük" kuralları dahil), atılan satır sayıları, bölünen sorgu sayısı, Mc_halka,
     Mc_lob;
   - kapı N0'ı (gölge ve pozitif; Aσ 13/19/39 ve D1, D3a, D3b, D4, D5, D8 eşikleri), K⁺; nötr kapı N0_nt'leri ve K_nt;
   - olay grupları, kümeler, temsilciler, §3.7 kesmeleri (r_k ile), çıkarmalar, K_kapı, mekanizma sınıfına göre K;
   - sahte zamanlar, geçerlilikleri ve geçersizlik nedenleri ("sahte kapı" dahil), sahte oylar (küme başına), p̂₀,
     p̂₀⁺, J, J < 30 kuralının uygulanıp uygulanmadığı, p₀, p₀⁺, c(K), c⁺(K), testere dişi atma listesi; §4.6 bilgi
     satırları (medyana göre ikiye bölünmüş p̂₀, K_0 ve kimlikleri);
   - her havuz olayı için R_A (aşağıda);
   - bayraklar ("öncül komşu" dahil) ve **S2 negatif kontrolün sonucu**.

   Ham ön indirmeler `/mnt/project-files/turetme/tr6a-ham/` altına arşivlenir. Manifest commit edilir. K_kapı < 23 ya
   da p₀ > 0,60 ise burada durulur (§5).

   **Başka adayların olay sonrası pencereleri (İNCELEME-1 B3).** Bir adayın ön indirmesi, başka bir A adayının son penceresini
   ([t_A, t_A + 365 g)) ve bölgesini kapsayabilir. Koşu adayları arasında (birim düzeyinde, kaba ölçüt: dış merkez
   uzaklığı < 2L_A + 2L_B) bu durumda 42 çift var ve 30 A adayı etkileniyor; 730 g ön tamponla 52 çift ve 33 aday
   (`b3`). Kural şudur:
   - Manifest kodu ve koşu kodu bir adayın lob ya da bölge sayısını yalnız o adayın kendi indirmesinden ve yalnız o
     adayın kendi pencere ve lob tanımlarıyla üretir. Bu sayılar (kapı, negatif kontrol, geçerli sahte oylar) A'nın
     penceresine düşen satırları da içerebilir. Ama hiçbir sayı A'nın penceresi ve bölgesiyle sınırlanmış olarak
     üretilmez.
   - Bir sahte pencere bir A'nın olay sonrası penceresiyle örtüşüyorsa o sahte oy hesaplanmaz (§4.6 geçerlilik).
   - Hiçbir ön ham dosya insan gözüyle satır satır incelenmez.
   - Ön indirmelerde [t_A, t_A + 365 g) aralığına ve A'nın 4 L_A yarıçapına düşen satırlar için hiçbir özet (sayı,
     histogram, harita) yazılmaz.
   - Bu kuralların dışındaki her önbellek okuması (tanı, denetim, ad hoc sayım) yalnız `tr6a_onbellek_kor.oku_sorgu`
     üzerinden yapılır. Bu işlev sözü edilen satırları döndürmeden önce atar ve onlar hakkında hiçbir bilgi vermez.
     Ek 1 önbelleği aynı kuraldadır. Önbellek yalnız arşivden (sha256 f350d2e0…0d60) açılan bir dizinden okunur; yol
     `oku_sorgu(…, onb=…)` ile verilir. Kod incelemesi (§9 adım 4), önbelleği ya da ön ham dizinleri açan her `open(`
     çağrısını listeler. `oku_sorgu` ve manifestin aday başına kendi indirmesini okuyan işlevi dışında bir çağrı varsa
     bu hata sayılır. Manifest, kırık izleri çıkınca her havuz olayı için R_A = 2 L_A + (izin dış merkeze en uzak
     noktası) değerini yazar. R_A > 4 L_A olan bir olay varsa maske o olay için R_A'ya genişletilir ve sonraki ad hoc
     okumalar genişletilmiş maskeyle yapılır. (Kodda: `tr6a_onbellek_kor.arsivden_ac` arşivin sha256'sını
     `tr6a_ham_sha256.txt` ile denetleyip dizini işaretler; okuma yolu `onb=` ya da `TR6A_ONBELLEK` ister, sabit yol
     yoktur; `tr6_a_kapi.getir` işaretli dizini açmayı reddeder.)

   "Manifest hiçbir olay sonrası veri içermez" cümlesi, "manifest hiçbir adayın kendi olay sonrası penceresinden ya da
   başka bir adayın olay sonrası penceresiyle sınırlanmış bir bölgeden türetilmiş sayı içermez" diye okunur.
4. **Kod incelemesi** (bağımsız), olay sonrası veri indirilmeden önce. Gerçek veride yalnız manifest koşulmuş olur.
   İnceleme §4.6 kalibrasyonunu, §3.5 alt pencere Mc_son kuralını ve §3.7 kesmesini özellikle denetler; ayrıca J < 30
   ve sahte kapı dallarını, nötr kapısını, §6.4 ad kurucusunu, §3.3'ün 6–9 sınamalarını ve §9 adım 3'teki `open(`
   denetimini (İNCELEME-2 §H madde 6). İnceleme
   manifest kodunda bir hata bulursa yalnız o hata düzeltilir ve manifest yeniden koşulur. İki manifest de commit
   edilir. Farkları (K, atılan kümeler, p̂₀, S2) kayda yazılır. Bağlayıcı olan ikincisidir. Hata listesi yeniden
   koşudan önce commit edilir.
5. **Olay sonrası katalog bir kez indirilir:** manifestteki bütün kapı kümelerinin (bütün satırların birleşimi) seçilen
   kataloğundan [t0, son pencere sonu) bölge olayları. D6 satırının olayları için ayrıca ISC'den; S6 için SRCMOD
   modelleri (katalog değil) aynı adımda bir kez. Satır sınırı kuralı uygulanır. Hiçbir sorgu 2025-12-31'i aşmaz.
   Ham yanıtlar arşivlenir, `tr6a_son_ham_sha256.txt` commit edilir.
6. **Tek koşu:** `tr6a_kosu.py` manifesti, ham listeleri ve kendi sha256'sını doğrular. Sonuç dosyalarını bellekte
   üretip birlikte yazar; var olan çıktının üzerine yazmaz. Çıktı ne olursa olsun yazılır. Koşudan sonra tanım, eşik,
   manifest ya da küme kuralı değişmez. Koşu bir istisnayla durursa yalnız istisnanın doğrudan nedeni düzeltilir ve
   fark kayda geçer. Herhangi bir oy ya da X görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik"
   başlığında yazılır ve sonucu ayrı satırdır. Hüküm adı, değişiklikten önce tamamlanmış koşudan gelir. Değişiklikten
   sonraki koşu farklı bir taban hüküm verirse hüküm adına "(koşu sonrası değişiklikle: <ad>)" eklenir. İstisnayla
   duran bir koşunun doğrudan nedeni düzeltilip tamamlanan ilk koşu, bu kuralda "değişiklikten önceki koşu" sayılır.

Bugüne dek hiçbir lobda oran hesaplanmadı. Sürüm 2 önsayımının küme listesi Ek A'da bilgi olarak verildi; bağlayıcı
küme listesi manifesttir.

## 10. Önceden beyan edilen beklenti

- **K.** Ek 1'in kaba kapısı (lob payı 0,25 ve halka Mc'si varsayımı) sürüm 2 kurallarıyla şöyle sayılır
  (`onsayim.19`):
  - koşu adayı 81 birim → kapıdan geçen 41 birim → 35 küme;
  - bilinen sonuçlu 2 küme çıkar (Kumamoto, Ridgecrest);
  - kısa son pencereli 4 küme çıkar (§3.7);
  - sonuç **K_kaba = 29**.

  ISC kuralı kapıdan önce 3 birimi düşürür (§3.5). Sürüm 1'in 46 olay / 37 küme sayımı aynı kodla yeniden üretildi
  (`surum1_yeniden`). Aσ 13 kPa'da K_kaba 35 (49 birim, 41 küme), Aσ 39 kPa'da 6 (8 birim, 8 küme). Sürüm 3
  kuralları kaba önsayımı değiştirmez: K_kaba yine 29'dur ("0 büyüklük" satırları sürüm 2 önsayımında da seçime
  girmiyordu; nötr ve pozitif kapı, sahte kapı ve tekil yakın alan kaba kapıyı etkilemez). Yedek (c) seçilirse 2004
  Sumatra kümesi T_son 1,6 g ile çıkar ve K_kaba 28 olur (`onsayim.19.yedek_c`).
- **K⁺ ve K_nt (kaba, bilgi).** Ek 1'in lob payı varsayımı pozitif loba ve nötr bölgeye de uygulanırsa her temsilcinin
  kaba N0'ı bu iki kapının da üstündedir (en küçüğü 34,3): pozitif kapıyla (N0⁺ ≥ 10,0) **K⁺ = 29**, nötr kapıyla
  (N0_nt ≥ 31,36) **K_nt = 29** (`onsayim.19.pozitif_kapi_K`, `notr_kapi_K`). Bu sayılar varsayımın kopyasıdır; gerçek
  pozitif lob ve nötr bölge alanları ΔCFF'ye bağlıdır ve ΔCFF henüz hesaplanmadı. Duyarlılık (aynı 29 temsilci, kaba N0
  çarpanla): K⁺ × 0,5 / × 0,25 / × 0,125 ile 29 / 25 / 14; K_nt × 0,5 / × 0,25 ile 18 / 5.
- **Duyarlılık (bilgi).** K_kaba şu varsayımlarla değişir:
  - kesme ölçütü dış merkez ≤ 3L ile: 29;
  - kaba N0 × 0,5 ile (lob payı 0,125): **19**;
  - kaba N0 × 0,25 ile: 6;
  - Mc + 0,5 ile (Ek 1 `N0_mc05`): 11;
  - ikisi birlikte: 7.
- **Neden aşağı?** Gerçek lob tanımı (§3.4) megathrust olaylarında gölgenin büyük kısmını (kırığın üstü) dışarıda
  bırakır. Önsayımın 29 kümesinin 14'ünün temsilcisi megathrust'tır (doğrultu atımlı 10, normal 4, ters diğer 1;
  S3/S4 tanımıyla). Lob Mc'si (MAXC + 0,2, çoğu açık denizde) ve 730 g tamponlu kümesizleştirme sayıyı ayrıca düşürür.
- **Yazarın önseli: P(K < 23) ≈ 0,7** (sürüm 1: 0,5). Dayanağı: kaba sayı eşiğin yalnız 6 üstünde ve kaba N0'ın yarıya
  inmesi K'yi 19'a düşürüyor.
- **p₀.** Kapıdan geçen kümelerin çoğunun N0'ı yüksektir (önsayımda temsilcilerin kaba N0 medyanı 78,4, Tohoku 4501). Bu yüzden Poisson H0'da
  sahte düşüş oyu payı ≈ 0,47–0,49 beklenir. Aşırı saçılım ve sahte pencerelerdeki ağ değişimi bunu 0,50'nin üstüne
  itebilir. Yazarın önseli: P(p₀ > 0,50) ≈ 0,4, P(p₀ > 0,60) ≈ 0,05. K ≈ 23–29 bölgesinde p₀ ≥ 0,53 tasarım gücünün
  altına düşürür (§5 tablosu).
- **K ≥ 23 ise küme başına oy olasılığı p ≈ p₀ … p₀ + 0,1** (§2'deki literatürün çoğu gölgeyi bulamıyor; Ma vd. 2005
  bulduğu yerde uzun, düşük Mc'li katalog vardı). p₀ = 0,50 ile §6.1 tablosundan (K = 23–30):
  - P(H1) ≈ 0,05–0,25;
  - P(ayırt edilemez) ≈ 0,15–0,30;
  - P(H0) ≈ 0,45–0,80.

  Bu, §2'deki önsellerle (0,20 / 0,50 / 0,30) tutarlıdır.
- **Pozitif kontrol.** Yalnız +10 kPa'lık kalıcı adımla bile küme başına artış oyu N0⁺ = 10'da 0,928'dir. S1 bu
  durumda K⁺ = 10'da 0,84, K⁺ = 15'te 0,98 olasılıkla tutar (`tr6a_onkayit_sayilar.json` `pozitif_kapi`). Gerçek
  pozitif loblarda ΔCFF çoğunlukla daha büyüktür. K⁺ < 10 olasılığı, kapı 3,0'dan 10,0'a çıktığı için sürüm 2'deki
  ≈ 0,2'den büyüktür; yazarın önseli ≈ 0,3.

  Yapay hesap (`pozitif_kapi`; Aσ 19 kPa, pozitif lobda yalnız +10 kPa'lık Dieterich adımı; kesin Poisson toplamı):

| N0⁺ (/yıl) | 3 | 5 | 10 | 20 | 31,36 |
|---|---|---|---|---|---|
| P(A), kalıcı adım | 0,727 | 0,823 | 0,928 | 0,986 | 0,997 |
| P(A), t_a 1,9 yıl | 0,627 | 0,716 | 0,832 | 0,930 | 0,971 |
| P(A \| H0) | 0,376 | 0,406 | 0,429 | 0,451 | 0,461 |

  S1'in tutma olasılığı P(X⁺ ≥ c(K⁺; 0,50)), kalıcı adım:

| K⁺ | N0⁺ 3 | N0⁺ 5 | N0⁺ 10 | N0⁺ 20 | N0⁺ 31,36 |
|---|---|---|---|---|---|
| 10 | 0,197 | 0,450 | 0,842 | 0,991 | 1,000 |
| 15 | 0,383 | 0,733 | 0,981 | 1,000 | 1,000 |
| 20 | 0,526 | 0,873 | 0,998 | 1,000 | 1,000 |

- **Negatif ve nötr kontrol:** ISC'nin ağ yoğunlaşması yüzünden hafif bir düşüş ya da artış eğilimi beklenebilir; yönü
  önceden bilinmiyor. Nötr kapı yüzünden K_nt < 10 olasılığı küçük değildir. O durumda H1 yalnız 'nötr kontrol
  koşulamadı' niteleyicisiyle verilebilir ve §13'e taşınmaz (§6.4).
- **En olası sonuç:** "güç yok" ya da "H0 / ayırt edilemez, iki açıklama ayrılamaz". Bu sonuçların kayda geçmesi
  sınavın amacıdır. Büyük olaylarda Mc_kul − Mc_lob ≥ 1 olası; yapay ızgarada 2,6'ya kadar.

## 11. Bilinen zayıflıklar

1. **ISC büyüklük türleri karışık** (JMA M, ML, mb, Ms aynı sütunda). MAXC karışık türler üzerinde hesaplanır. Bölgede
   tür bileşimi zamanla değişirse oran değişimi büyüklük türü değişiminden ayrışmaz.
2. **ISC'nin son iki yılı gözden geçirilmemiş bülten.** 2024–2025 son pencereleri daha az ajans katkısı taşıyabilir:
   olay sonrası sayı düşer ve gölgede H1 lehine sahte düşüş üretir. 2023-12-31 sınırı sabit bir varsayımdır, ISC'den
   okunmadı. Bu yüzden son penceresi bu sınırı aşan ISC olayları ana hükme girmez (§3.5). Önsayımda bu kural en yüksek
   N0'lı iki Japonya kümesini (Noto, Hyūganada) çıkarır.
3. **Lob Mc'si.** Loblar çoğunlukla açık denizde. MAXC, sorgu tabanı Mc_halka − 0,05 ile kesildiği için Mc_lob'u ancak
   yukarı itebilir (tutucu). 5 yıllık ön pencerede ağ değişimi (Mc'nin zamanla düşmesi) ön oranı şişirmez, ama
   Mc_lob'u pencerenin en kötü dönemine kilitlemez; MAXC havuzlanmış pencereden alınır. Negatif kontrol ve sahte
   kalibrasyon bu tür eğilimleri ölçer.
4. **Megathrust ağırlığı.** Önsayımın 29 kümesinin 14'ünün temsilcisi megathrust'tır (doğrultu atımlı 10, normal 4,
   ters diğer 1; S3/S4 tanımıyla). Alıcılar 7,5 km'de, sismisite
   0–40 km. Megathrust gölgesinin derinlikle işaret değiştirdiği yerler var. S4 ve yorum kuralı 3 bunu adlandırır.
   Derinlik duyarlılığı (ör. 15 km) bu sürümde yok.
5. **Kayma modeli belirsizliği.** ΔCFF'nin CV'si ≈ 1 (Hainzl vd. 2009). Tek ComCat modeli var. SRCMOD erişimi ve
   kapsamı bu belgede doğrulanmadı (S6 koşulamayabilir). D8 (−30 kPa) işaretin daha sağlam olduğu hücreleri ayrı
   yazar.
6. **Coulomb sadeleştirmeleri.** Tek alıcı düzlem, sabit μ' 0,4, sabit derinlik; gözenek basıncı ve poroelastik etki
   yok, artkayma yok, dinamik tetiklenme yok. Dinamik tetiklenme ve konum hatası gölgeyi "artış"a iter (H1 aleyhine).
7. **Ana şok sonrası tamlık.** Tamlık kaybı gölgede H1 lehine sahte düşüş üretir ve yanlılık N0 ile büyür. Önlemler:
   - t_s + 30 g'ye kadar dışarıda;
   - alt pencere Mc_son (§3.5);
   - S7 nötr kontrol ve eşleşik McNemar;
   - D1 ve D2;
   - §9 adım 2'deki 96 hücrelik yapay sınama ve yedek merdiveni.

   Gerçek kayıp bölgeden bölgeye değişir; Helmstetter biçimi 20 km ötede bir üst sınırdır.
8. **Kümesizleştirme yalnız lob içi.** Lob dışındaki büyük bir artçının loba taşan dizisi ayıklanmaz (H1 aleyhine).
   Önceki büyük bir olayın sönen dizisi ön oranı şişirir (H1 lehine); 730 g tampon bunun lob içi kısmını azaltır.
   Negatif kontrol ve D7 kalanını ölçer.
9. **Havuz seçimi.** ComCat sonlu fay ürünü olan olaylar büyük ve iyi çalışılmış olaylardır; 1990'lar seyrek.
10. **Ek 1 hatası.** 2012 Hint Okyanusu ve 2003 Tokachi-oki satırlarında ComCat Mc'si 0,2 ve 0,3 (eksik büyüklükler "0"
    yazılmış). Sürüm 2'de önbellekte doğrulandı (§3.5). İki olay da ISC ile kapıdan geçer.
11. **Havuz dışı öncü ve çiftler** (Ridgecrest M 6,4 gibi) ΔCFF'ye girmez.
12. **Koşullu oyun H0 olasılığı N0'a ve saçılıma bağlıdır.** Poisson H0'da 0,446–0,497 aralığındadır. Aşırı saçılımda
    0,5'i aşabilir (φ = 5, N0 = 31,36'da 0,515). Önlem: §4.6'daki ampirik p₀ = max(0,50; ⌈100 p̂₀⌉/100). p̂₀ en çok üç
    sahte zamandan kestirilir ve aynı kümenin sahte oyları birbiriyle ilişkilidir; etkin örneklem J'den küçüktür.
    Kalibrasyon ortalamayı düzeltir, saçılımı tam düzeltmez. Kümeler arası korelasyon binomun bağımsızlık varsayımını
    ayrıca zayıflatır. Sahte ve gerçek pencereler veri paylaşır (sahte j = 1'in son penceresi gerçek ön pencerenin
    içindedir). Yapay hesap (İNCELEME-2; Gamma beyaz gürültü, N0 31,36–500, φ 1–5, K 23 ve 28) şunu verdi: gerçek ve
    sahte oy arasında korelasyon ≈ −0,02; tam yordamın α'sı, bağımsız sahte oy varsayımındakinden 0,001–0,005 yüksek
    ve en çok 0,037.
13. **Aσ yalnız kapıda.** Oy Aσ'dan bağımsızdır. Bu yüzden sınav "hız-durum ölçerinin Aσ = 19 kPa ile kalibre edilmiş
    hâlini" değil, ölçerin işaret düzeyindeki çıktısını sınar. Δτ_est büyüklüğü t_a bilinmediği için sıfıra doğru
    yanlıdır (§4.5).
14. **Kümeleme ilk uyan sırayla** (Ek 1 ile aynı), tek bağlantı değil.
15. **Yazarın literatür bilgisi** (körlük beyanı). İç sınır 20 km yakın alan gölge artçılarını dışarıda bırakır. Bu
    yüzden Kumamoto ve Ridgecrest ana hükümden çıkarıldı. D3a satırı ve B4 bunu görünür kılar.
16. **p̂₀ gürültüsü gücü düşürür** (§4.6 sonu). Kalibrasyon yanlış yönde de olsa (gerçek sahte p 0,46) K = 23'te beklenen
    güç 0,745'tir.
17. **Sahte geçerlilik kuralı** yoğun bölgelerde (Japonya, Sumatra) kalibrasyonu yüksek N0'lı kümelerden yoksun
    bırakır (önsayımda Tohoku'nun üç sahte zamanı da geçersiz). p̂₀ ağırlıkla orta N0'lı kümelerden gelir. Bu kümeler
    H0'da daha düşük P(D) taşır; kalibrasyon yüksek N0'lı kümelerin yanlılığını eksik görebilir. Yapay hesap
    (İNCELEME-2): yıllık oran CV'si 0,1–0,3 iken (φ = 1 + CV² N0), K = 23'ün 5–8 kümesi N0 500–1000 ve sahte zamansız,
    kalanı N0 50 olsun. Bu durumda kalibrasyonlu α 0,026–0,041, kalibrasyonsuz (p₀ 0,50) α 0,033–0,070 olur. "Sahte
    kapı" (§4.6) kalan küçük yanlılığı tutucu yöne çeker.
18. **Son pencere kesmesi** (§3.7) kesilen kümelerde T_son'u kısaltır (Sumatra 2004: 61,6 g) ve onların oy gücünü
    düşürür.

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

- H1 çıkarsa ve §6.4 madde 5'in taşıma ölçütü tutarsa Marmara'ya taşınan tek cümle: "sismisite oranından gerilme işareti
  çıkaran hız-durum ölçeri, küresel kosismik gölgelerde işaret düzeyinde geçerli." Bu, Marmara'da kullanılabilirlik
  değildir: (b) ayağının 1 yıllık çözünürlüğü beklenen sinyalin 2,4–82 katı (TR-6_SAYIM §6).
- H0, ayırt edilemez, güç yok ya da koşulmadı çıkarsa Marmara'ya hiçbir şey taşınmaz. H1 taşıma ölçütünü tutmazsa
  yalnız §6.4 madde 5'teki "Marmara'ya taşınmadı: <niteleyici>" satırı yazılır.
- İstanbul ya da Marmara için mutlak olasılık, olasılık çarpanı ya da tarih bu sınavdan hiçbir durumda yazılmaz.

## 14. Yeniden açma şartı

- **Güç yok (K):** lob Mc'siyle olay öncesi sayılan K_kapı ≥ 23 sağlayan yeni bir açık katalog (ör. JMA birleşik
  hiposantr dosyalarının doğrudan kullanımı, Şili CSN toplu erişimi) ya da ISC'nin gözden geçirilmiş bülteni genişledikçe
  aynı kurallarla yeniden sayım. Kurallar bu metindekilerdir; yalnız katalog listesi değişir ve önceden yazılır. İkincil
  ve duyarlılık satırlarının K'leri bu şartı karşılamaz (§5).
- **Güç yok (ölçü yanlı, p₀ > 0,60):** yeniden açma ancak sahte zamanlardaki yanlılığın kaynağını (ağ değişimi, saçılım)
  ölçen ayrı bir ön kayıtla.
- **H0 ya da ayırt edilemez:** (i) en az iki bağımsız kayma modelinin lob sınıfında ≥ %80 hücre uyuşması olan en az
  28 küme (Coulomb tarafının belirsizliğini daraltan bir sınav), ya da (ii) 2026 ve sonrası olaylar, olay sonrası
  pencereleri kapandıktan sonra, ayrı ön kayıtla.
- **Koşulmadı (yöntem):** aday elenmez; yeniden açma ancak ayrı bir ön kayıtla (§6.4).
- **H1:** yeniden açma gerekmez; Marmara'ya taşıma (b) ayağının yeniden açma şartına bağlı kalır (Mc ≈ 1 homojen açık
  katalog ve çok yıllı pencere).

## 15. Maliyet ve iş yükü

0 €. Bütün veriler açık (ComCat, ISC, GeoNet, EMSC, KOERI; SRCMOD erişimi doğrulanmadı). Tahmin (ölçülmedi):
- kod 2–3 gün (sahte kalibrasyon ve alt pencere Mc_son eklendi);
- manifest için olay öncesi indirmeler birkaç saat sunucu süresi; sahte zamanlar ve 730 g tampon yüzünden ön indirmeler
  sürüm 1'in ≈ 2 katı (ISC yavaş, KOERI çok yavaş);
- Okada hesabı < 1 saat CPU;
- olay sonrası indirme birkaç saat.

Bulut oturumunda yapılır; makine gerekmez.

## 16. İnceleme düzeltme metinlerinden sapmalar (gerekçeli)

İNCELEME-1'in (A1–A4, B1–B10, K1–K8) ve İNCELEME-2'nin (A1–A3, B1–B6, K1–K15) bütün bulguları işlendi. Madde 1–15
İNCELEME-1 düzeltme metinlerinden sapmalardır. İNCELEME-2 bunların 14'ünü kabul etti; J < 30 kuralını reddetti ve
madde 2 onun düzeltmesiyle yeniden yazıldı. §0 gereği burada bu metin geçerlidir.

1. **A1, p₀'ın yuvarlanması.** Düzeltme metni c(K)'yi p̂₀'ın kendisiyle hesaplıyordu. Bu metin p₀ = max(0,50;
   ⌈100 p̂₀⌉/100) kullanır. Böylece §5 ve §6.1 tabloları bağlayıcı ve tek anlamlıdır. Yuvarlama yukarı olduğu için
   tutucudur.
2. **A1, p₀ > 0,60 kuralı ve J < 30 kuralı** düzeltme metninde yoktu. p₀ = 0,60'ta güç 0,80'e ancak K ≥ 62'de
   ulaşır. J < 30'da p₀ tabanı 0,52'dir (İNCELEME-2 A1).
3. **A1, payda ve sahte geçerlilik.** Düzeltme metninde payda 3 K_kapı idi. Bu metinde payda geçerli sahte zaman
   sayısı J'dir. Yeni geçerlilik kuralı, başka bir havuz olayının olay sonrası penceresiyle örtüşen sahte zamanı atar.
   İki gerekçesi var: sahte oyun "olay yok" dünyasını temsil etmesi ve İNCELEME-1 B3'teki körlük. Sahte son pencere
   gerçek pencereyle aynı kaymaları taşır (grup t_s, §3.7 kesmesi).
4. **A1, ön indirme sınırı** t0 − 2891 g değil t0 − 3621 g'dir, çünkü B9'un 730 g tamponu sahte zamanlara da uygulanır.
5. **A1 ve A2 sayıları** bu belgenin kendi kodundan (`tr6a_inc1_denetim.py`, numpy) alındı. Farklar:
   - φ = 3, N0 = 100'de P(D) İNCELEME-1'de 0,505, burada 0,4993 (400 000 deneme; İNCELEME-1'de 4000). Bu yüzden
     §4.3'te "0,5'i aşabilir" örneği φ = 5'tir.
   - Tamlık hesabında İNCELEME-1 lobda "ya hep ya hiç" algılama kullanmıştı. Bu metin kısmi algılama payı
     10^−(Mc(t) − Mc_kul) kullanır. Bu yüzden sürüm 1 kuralının kaybı %1,3–3,1'dir (İNCELEME-1: %3 ve %7–13). Sonuç
     değişmez: kural 96 hücrenin 56'sında başarısız, alt pencere kuralı hiçbirinde.
6. **A3, işlem sırası.** Düzeltme metni çıkarmayı "kapıdan önce, kümelemeden sonra" diye yazıyordu. Kümeleme kapıdan
   geçenler üzerinde yapıldığı için bu iki koşul birlikte sağlanamaz. Bu metin K1 sırasını izler: kapı → kümeleme →
   çıkarma → K_kapı.
7. **A4, "son pencere"** kesilmemiş t0 + 365 g'dir; kesme ISC kuralını değiştirmez.
8. **B3 sayımı** birim (grup) düzeyinde yapıldı: 42 çift ve 30 aday (İNCELEME-1: olay düzeyinde 44 ve 30). Kurala
   bir okuma işlevi (`tr6a_onbellek_kor.py`) ve 4 L_A maske yarıçapı eklendi.
9. **B4, önsayım** dış merkez ≤ 2L ile yapıldı (r_k manifestte). S2'nin son penceresi grup kaymasıyla kayar, kesmeyle
   kısalmaz.
10. **B5, §10 metni.** Düzeltme metni K'yi "≈ 31–33" ve P(K < 23)'ü "≈ 0,55–0,6" veriyordu. Koddan önsayım 29'dur;
    yazarın önseli 0,7'dir.
11. **K3, "0 büyüklük" kuralı** düzeltme metnindeki gibi genişletilmedi, daraltıldı. Önbellekte türü dolu sıfır ve
    negatif büyüklüklü binlerce gerçek satır var. Bu yüzden kural yalnız türü boş ve büyüklüğü ≤ 0,05 olan satırları
    atar; sorgu tabanı kuralı ayrıca eklendi (§3.5).
12. **F.3, liste değişti.** İNCELEME-1 listenin değişmeyeceğini söylüyordu. Bu metin birimleri, ISC kuralını, kesmeyi,
    sahte zamanları ve "0 büyüklük" işaretini listeye yazar. Böylece manifest bunları yeniden kurmaz, okur. Yeni sha256
    §3.1'dedir.
13. **S2 ve sahte j = 1.** Düzeltme metni S2'yi "j = 1'in özel hâli" sayıyordu. İkisinin ön pencereleri farklıdır. S2
    sürüm 1 tanımıyla ayrı satır kalır; yalnız j = 1'i geçerli kümelerde hesaplanır.
14. **S7 McNemar gücü** nötrde 0,4585 ile kesin hesaplandı (İNCELEME-1: 0,46, Monte Carlo).
15. **B10, GeoNet:** servis limit parametresini kabul etmiyor. Satır sınırı kuralına bunun için bir yedek eklendi
    (§5 madde 1).
16. İNCELEME-2 düzeltmeleri işlendi (A1–A3, B1–B6, K1–K15); sapma yok.

## Ek A (bilgi, bağlayıcı değil): sürüm 2 önsayımının küme listesi

Ek 1'in lob payı 0,25 varsayımıyla ve halka Mc'siyle, ≤ 40 km, Aσ 19 kPa (eşik 31,36). Kurallar: tarih, "0 büyüklük",
ISC, gruplar, kümeleme, bilinen kümelerin ve kısa son pencereli kümelerin çıkarılması. "Kesilmiş T_son"un yanında
kesmeyi yapan havuz olayı yazılıdır. ‡: ISC bu birim için seçilemez (§3.5). Gerçek K manifestte lob Mc'siyle yeniden
sayılır ve bu listeden farklı olacaktır.

| Küme | Birim (üyeler) | Tarih | M | Enlem, boylam | Katalog (Mc) | Kaba N0 (/yıl) | Mekanizma | Kesilmiş T_son (g) | Geçerli sahte j |
|---|---|---|---|---|---|---|---|---|---|
| 1 | usp0006qh3 | 1994-12-28 | 7,8 | 40,52, 143,42 | ISC (3,1) | 96,8 | ters, düşük eğimli (megathrust dahil) | 335,0 | 0 |
| 2 | usp0006sef | 1995-02-05 | 7,1 | -37,76, 178,75 | GeoNet (2,6) | 55,2 | normal | 335,0 | 3 |
| 3 | usp0009d4z | 1999-08-17 | 7,6 | 40,75, 29,86 | ISC (2,8) | 82,9 | doğrultu atımlı | 335,0 | 3 |
| 4 | ak002e435qpj | 2002-11-03 | 7,9 | 63,51, -147,45 | ComCat (1,6) | 316,3 | doğrultu atımlı | 335,0 | 3 |
| 5 | official20030925195006360_27 | 2003-09-25 | 8,16 | 41,81, 143,91 | ISC (2,5) | 583,7 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 6 | official20041226005853450_30 | 2004-12-26 | 9,1 | 3,29, 95,98 | ISC (4,8) | 52,8 | ters, düşük eğimli (megathrust dahil) | 61,6 (official20050328160936530_30) | 0 |
| 6 | official20050328160936530_30 | 2005-03-28 | 8,6 | 2,08, 97,11 | ComCat (4,5) | 95,9 | ters, düşük eğimli (megathrust dahil) | 335,0 | 0 |
| 6 | usp000fzau | 2008-02-20 | 7,4 | 2,77, 95,96 | ISC (4,0) | 35,7 | ters, düşük eğimli (megathrust dahil) | 335,0 | 1 |
| 7 | usp000gz8j | 2009-07-15 | 7,8 | -45,76, 166,56 | GeoNet (2,7) | 89,1 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 8 | official20100227063411530_30 | 2010-02-27 | 8,8 | -36,12, -72,90 | ISC (3,6) | 78,3 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 9 | usp000hnj4 | 2010-10-25 | 7,8 | -3,49, 100,08 | ISC (4,0) | 36,8 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 10 | usp000hrw0 | 2010-12-25 | 7,3 | -19,70, 167,95 | ISC (2,6) | 39,9 | normal | 335,0 | 2 |
| 11 | official20110311054624120_30 | 2011-03-11 | 9,1 | 38,30, 142,37 | ISC (1,8) | 4501,4 | ters, düşük eğimli (megathrust dahil) | 335,0 | 0 |
| 12 | official20120411083836720_20 | 2012-04-11 | 8,6 | 2,33, 93,06 | ISC (4,0) | 111,2 | doğrultu atımlı | 335,0 | 0 |
| 13 | usc000f1s0 (+usc000f40j) | 2013-02-06 | 8,0 | -10,80, 165,11 | ISC (2,3) | 99,2 | ters, düşük eğimli (megathrust dahil) | 332,4 | 1 |
| 14 | usc000nzvd (+usc000p27i) | 2014-04-01 | 8,2 | -19,61, -70,77 | ISC (2,3) | 50,3 | ters, düşük eğimli (megathrust dahil) | 333,9 | 3 |
| 15 | us200030aq | 2015-07-27 | 6,9 | 52,38, -169,45 | ComCat (2,5) | 69,1 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 16 | us20003k7a | 2015-09-16 | 8,3 | -31,57, -71,67 | ISC (3,6) | 82,2 | ters, düşük eğimli (megathrust dahil) | 335,0 | 1 |
| 17 | us20005j32 | 2016-04-16 | 7,8 | 0,38, -79,92 | ISC (1,1) | 81,5 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 18 | us1000778i | 2016-11-13 | 7,8 | -42,74, 173,05 | ISC (2,6) | 206,8 | ters (diğer) | 335,0 | 3 |
| 19 | us2000cmy3 | 2018-01-23 | 7,9 | 56,00, -149,17 | ComCat (1,6) | 53,0 | doğrultu atımlı | 335,0 | 3 |
| 20 | hv70116556 | 2018-05-04 | 6,9 | 19,32, -155,00 | ComCat (2,0) | 102,6 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 21 | us1000h3p4 | 2018-09-28 | 7,5 | -0,26, 119,85 | ISC (3,2) | 34,3 | doğrultu atımlı | 335,0 | 3 |
| 22 | us1000hhb1 | 2018-10-25 | 6,8 | 37,52, 20,56 | ISC (2,1) | 47,3 | doğrultu atımlı | 335,0 | 3 |
| 23 | us1000i2gt | 2018-12-05 | 7,5 | -21,95, 169,43 | ISC (3,5) | 68,5 | normal | 335,0 | 1 |
| 23 | us6000dg77 | 2021-02-10 | 7,7 | -23,05, 171,66 | ISC (4,0) | 34,9 | ters, düşük eğimli (megathrust dahil) | 335,0 | 1 |
| 24 | us70003kyy | 2019-05-14 | 7,6 | -4,05, 152,60 | ISC (3,7) | 60,4 | doğrultu atımlı | 335,0 | 3 |
| 25 | us7000c7y0 | 2020-10-30 | 7,0 | 37,90, 26,78 | KOERI (2,3) | 37,6 | normal | 335,0 | 3 |
| 26 | us7000dflf | 2021-03-04 | 8,1 | -29,72, -177,28 | ISC (3,9) | 84,1 | ters, düşük eğimli (megathrust dahil) | 335,0 | 3 |
| 27 | us7000i90q | 2022-09-18 | 6,9 | 23,14, 121,34 | ISC (2,8) | 71,8 | doğrultu atımlı | 335,0 | 3 |
| 28 | us6000jllz (+us6000jlqa) | 2023-02-06 | 7,8 | 37,23, 37,01 | KOERI (2,3) ‡ | 147,8 | doğrultu atımlı | 334,6 | 2 |
| 29 | nc75095651 | 2024-12-05 | 7,0 | 40,37, -125,02 | ComCat (2,1) ‡ | 52,5 | doğrultu atımlı | 335,0 | 0 |

29 küme, 32 birim. Çıkarılan kümeler (temsilci):
- A3 bilinen sonuçlu: us20005iis (Kumamoto 2016), ci38457511 (Ridgecrest 2019);
- B4 kısa son pencere: usp0006kdp (1994 Hokkaidō; 54,0 g, usp0006qh3), usp000exfn (2006 Kuril; 27,7 g, usp000f2ab),
  usp000juhz (2012 Haida Gwaii; 38,2 g, ak0138esnzr), us7000asvb (2020 Simeonof; 58,6 g, us6000c9hg).

ISC kuralıyla kapıdan düşen birimler (D6): us6000kd0n, us6000m0xl, us6000nith.

## Ek B: yeniden üretim

```
python3 -I -B kayit/turetme/tr6/tr6a_onbellek_kor.py ac /mnt/project-files/turetme/tr6a-ham/tr6a_onbellek_2026-11-12.tar.gz <geçici_dizin>
python3 -I -B kayit/turetme/tr6/tr6a_sifir_buyukluk.py <geçici_dizin>/onbellek  # maskeli -> tr6a_sifir_buyukluk.json, ≈ 2 sn
python3 -I -B kayit/turetme/tr6/tr6a_onkayit_sayilar.py     # -> tr6a_olay_listesi.json, tr6a_onkayit_sayilar.json, ≈ 5 sn
python3 -I -B kayit/turetme/tr6/tr6a_onkayit_sayilar.py --md  # bu belgedeki tablolar
python3 -I -B kayit/turetme/tr6/tr6a_inc1_denetim.py        # -> tr6a_inc1_denetim.json, ≈ 45 sn
python3 -I -B kayit/turetme/tr6/tr6a_inc2_b1.py             # İNCELEME-2 b1: binom, p₀ ızgarası, testere, Poisson P(D), ≈ 3 sn
python3 -I -B kayit/turetme/tr6/tr6a_inc2_b2.py             # İNCELEME-2 b2: ortak veri ve α (yapay), ≈ 14 sn
python3 -I -B kayit/turetme/tr6/tr6a_inc2_b3.py             # İNCELEME-2 b3: temsil, sabit CV (yapay), ≈ 10 sn
python3 -I -B kayit/turetme/tr6/tr6a_inc2_b4.py             # İNCELEME-2 b4: sahte geçerlilik ve öncül komşu (liste)
python3 -I -B kayit/turetme/tr6/tr6a_md_denetim.py          # --md tablo satırları bu metinde birebir mi
```

Ağ erişimi yok; `__pycache__` kalmaz. `tr6_a_kapi.py`'den yalnız `kumele`, `gereken_n0`, `binom_ust`, `uzaklik_km`,
`maxc` ve `DERIN_KM` alınır; ağ kodu çağrılmaz. Rastgele tohumlar: 20261112 (`tr6a_onkayit_sayilar.py`: Δτ_est
dağılımı ve Monte Carlo denetimi), 20261113 (`tr6a_inc1_denetim.py`: aşırı saçılım). İNCELEME-1'in scipy betikleri
(`denetim1.py`–`denetim5.py`) depoya kopyalanmadı. Yalnız numpy kuralı gereği aynı hesaplar
`tr6a_inc1_denetim.py` ve `tr6a_onkayit_sayilar.py` içinde yeniden yazıldı:
- denetim1 → `asiri_sacilim` ve `yapay_dieterich.H0`;
- denetim2 ve 3 → `tamlik`;
- denetim4 → `mc_farki`, `dogru_lob_payi` ve `mcnemar_gucu`;
- denetim5 → `b3`.

İNCELEME-2'nin bağımsız betikleri (b1–b4; b1–b3 scipy kullanıyordu) numpy ve standart kitaplıkla
`tr6a_inc2_b1.py`–`tr6a_inc2_b4.py` olarak yeniden yazıldı (tohumlar 7 ve 8, özgündeki gibi). b1 bütün binom, p₀
ızgarası, testere, ilk/kalıcı K, `c_le_h` ve `j30_dali` değerlerini bağımsız kesin binomla denetler (uyuşmayan yok) ve
Poisson P(D) 0,4459 / 0,4585 / 0,4680 / 0,4783 / 0,4869'u üretir. b2 ve b3, İNCELEME-2'nin B2 sayılarını Monte Carlo
hatası içinde yeniden üretir: korelasyon −0,019 … −0,024; kalibrasyonlu α en çok 0,037; temsil benzetiminde
kalibrasyonlu α 0,027–0,042, kalibrasyonsuz 0,035–0,069. b4 J = 64 (4 L_A ile 61) ve beş öncül komşulu kümeyi
üretir. Tohum 20261114 ve 20261115 §9 adım 2'nin yapay sınamaları için ayrılmıştır.

Dondurmadan sonra bu betikler depo kopyasında değil, geçici bir kopyada koşulur. Yeniden üretim, çıktıların sha256'sı
§3.1'deki ve §9 adım 1'deki değerlerle karşılaştırılarak denetlenir. `tr6a_sifir_buyukluk.py` listenin yalnız
`olaylar` alanının kimlik, zaman, konum ve L değerlerini okur; bunlar "0 büyüklük" işaretinden bağımsızdır.

## Sürüm 1 → 2 değişiklik listesi

(Tarihsel kayıt; sürüm 3'te değişen kurallar için sondaki "Sürüm 2 → 3 değişiklik listesi" geçerlidir.)

| Bulgu | Değişiklik | Yer |
|---|---|---|
| A1 | §4.3 son paragrafı yerine N0'a bağlı P(D) ve α tablosu, aşırı saçılım tablosu; yeni §4.6 sahte kalibrasyonu (p₀ yuvarlaması, geçerlilik, J < 30, p₀ > 0,60); testere dişi p₀'a bağlı; §11 madde 12 | §4.3, §4.6, §5, §6.1, §11 |
| A2 | Mc_son alt pencerelerin en kötüsü; S7 nötr kontrol ve McNemar; yorum kuralı 2a; tamlık sınaması 96 hücre ve yedek merdiveni; gürültüsüz ön denetim | §3.5, §6.2, §7, §9 |
| A3 | Kumamoto ve Ridgecrest ana hükümden çıkar; Tohoku kalır; B4 satırı; körlük beyanı | başlık, §3.4, §7 |
| A4 | ISC kuralı katalog seçiminde; D6 yeniden tanımlandı; §11 madde 2 | §3.5, §7, §11 |
| B1 | S1'e N0⁺ kapısı (sürüm 2'de 3,0; sürüm 3'te 10,0, İNCELEME-2 B1), K⁺, K⁺ < 10 "koşulamadı"; yorum kuralı 1 | §6.2, §7 |
| B2 | Grup son penceresi t_s'den; π grup başına; kırık izi üye başına; grup konumu en büyük üye | §3.2, §3.4, §4.1, §4.3 |
| B3 | Okuma kuralı ve `tr6a_onbellek_kor.py`; sahte geçerlilik; körlük beyanı | başlık, §4.6, §9 |
| B4 | Son pencere kesmesi, T_son < 60 g çıkarma; B3 satırı genişledi | §3.7, §7 |
| B5 | Doğru lob payı tablosu (p₀, K, w, ΔMc); güç tablosu p₀ 0,50/0,52/0,55; kalibrasyonun beklenen güç kaybı; §10 K ve P(K < 23) | §4.5, §4.6, §6.1, §10 |
| B6 | Okada doğrulamasının numpy beş sınamalı yedeği | §3.3 |
| B7 | Sonlu fay ürününün dondurulması, dosya seçimi, kesimler, M0 sağlaması | §3.3 |
| B8 | İkincil satırlar ana kapının yerine geçmez; manifest yeniden koşma kuralı | §5, §9 |
| B9 | 730 g ön tampon (ana, sahte, negatif kontrol) | §3.6 |
| B10 | Satır sınırında sorgu bölme (GeoNet yedeğiyle) | §5 |
| K1 | İşlem sırası, sözlük sırası, "ana K" tanımı | §5 |
| K2 | M0 formülü, iz çıkarma, T/P, rake, çift kuvvet payı | §3.3 |
| K3 | "0 büyüklük" önbellekte doğrulandı ve daraltıldı; ikinci bozuk olay (2003) bulundu | §3.5, §11 |
| K4 | Olayın hücreye atanması | §3.4 |
| K5 | D8 güçlü gölge satırı | §7 |
| K6 | Tanımsız Δτ_est ve Spearman sırası | §4.4 |
| K7 | "Ters yön: X ≤ t" sütunu kaldırıldı; ters yön p₀⁺ ile | §6.1 |
| K8 | Manifestte mekanizma sınıfına göre K ve iç sınırla atılan hücre | §3.4, §9 |
| — | §0 öncelik sırası (sürüm 1'in §0 sorusu §1'e, §1'i §1.1'e taşındı); durum satırı; önsayım özeti başta; yeni liste ve sha256 (sürüm 1: 01d73cad…); §16 sapmalar; Ek A yeniden; Ek B | başlık, §0, §1, §3.1, §16, Ek A, Ek B |

## Sürüm 2 → 3 değişiklik listesi

| Bulgu (İNCELEME-2) | Değişiklik | Yer |
|---|---|---|
| A1 | J < 30'da p₀ = max(0,52; ⌈100 S/J⌉/100), p₀⁺ aynı biçimde; p₀ > 0,60 ve p₀⁺ > 0,60 kuralları aynen; "kalibrasyon zayıf" niteleyicisi ve eki; dayanak tablosu (`j30_dali`); hüküm satırı, işlem sırası, §8 üst bilgisi, §16 madde 2 | §1, §4.6, §5, §6.3, §6.4, §8, §16 |
| A2 | Yeni §6.4: hüküm adlarının kapalı listesi, taban / düşürücü / niteleyici / ek sırası, §13'e taşıma ölçütü; §6.2 başlığı ve kural 2'nin düşürücü adı; §6.3'e "koşulmadı (yöntem)" ve "kalibrasyon zayıf" kalıpları; §8 hüküm hücresi; §13 ilk madde; Okada, yapay katalog ve tamlık sınaması başarısızlıklarının adı; §4.6'daki ad "güç yok (ölçü yanlı)" | §3.3, §4.6, §6.1–§6.4, §8, §9, §13, §14 |
| A3 | S7 nötr kapısı N0_nt ≥ 31,36 (n_on,nt ≥ 155), K_nt manifestte; K_nt < 10 ise "koşulamadı"; McNemar yalnız K_nt kümede, a + b = 0 ise p = 1; kural 2a yeniden yazıldı; §10 cümlesi | §6.2, §7, §8, §9, §10 |
| B1 | S1 kapısı N0⁺ ≥ 10,0 (n_on⁺ ≥ 50); §10 pozitif kontrol metni; `pozitif_kapi` anahtarı ve iki tablo | §7, §10, kod |
| B2 | Sahte kapı n_on' ≥ 155; geçerlilik ve maske geometrisi cümlesi; manifest bilgi satırları (medyana göre p̂₀, K_0); "öncül komşu" bayrağı (önsayımda 5 küme); §11 madde 12 ve 17 | §4.6, §7 B3, §9, §11 |
| B3 | Yapay katalog sınaması (i) ve (ii), tohum 20261114, ≥ 20 000 deneme, 3,5 SE, sonuç kuralı; tamlık sınaması ≥ 20 000 deneme, tohum 20261115; basamak başına tek koşu ve commit; yedek (c)'nin yayılımı (Sumatra T_son 1,6 g); "koşulmadı (yöntem: tamlık sınaması)" | §9 adım 2, §10 |
| B4 | Okada 6–9 sınamaları, tekil noktalar, tekil yakın alan ızgara kuralı; King deseninin nicel karşılığı | §3.3, §3.4, §9 |
| B5 | Kural 6 (etkin N0) ve H0 / ayırt edilemez eki; §8 N0_kul; §10 cümlesi | §6.2, §6.4, §8, §10 |
| B6 | Koşu sonrası değişikliğin sonucu ayrı satır; hüküm değişiklikten önceki koşudan; ek §6.4 madde 6'ya bağlandı | §6.4, §9 adım 6 |
| K1 | c(K) ≤ h(K) öncelik kuralı; `c_le_h` anahtarı | §6.1, kod |
| K2 | K_kapı = 46–80 testere çözümü JSON'dan, bağlayıcı; > 80 aynı fonksiyonla | §5 |
| K3 | Kesmede r_k'nin tanımı; 3L duyarlılığı ve ilk 30 gün denetimi (`ilk30_gun_3L`) | §3.7, kod |
| K4 | "0 büyüklük" satırları seçime ve hiçbir satıra girmez, yeniden kestirilmez; sorgu maddesi sadeleşti | §3.5 |
| K5 | Mekanizma dökümü temsilciye göre: 14 megathrust, 10 doğrultu atımlı, 4 normal, 1 ters diğer (`mekanizma_dokumu_temsilci`) | §10, §11, kod |
| K6 | Kapı ve sahte oylar Mc_lob ile, oy Mc_kul ile kümesizleştirilir | §3.6 |
| K7 | K_nk < 10 ise S2 koşulamadı; K_S4 < 5; K = 0 satırları | §6.2, §7 |
| K8 | Önbellek yalnız arşivden; `oku_sorgu(…, onb=…)`; `open(` denetimi; R_A ve maske genişletme. Kodda: sabit yol kaldırıldı (`onb=` ya da `TR6A_ONBELLEK`), `arsivden_ac` sha256 denetimi ve işaret dosyası, `tr6_a_kapi.getir` işaretli dizini reddeder | §9 adım 3, kod |
| K9 | Birden çok sonlu fay ürünü, `updateTime`, grup üyesi "veri yok" | §3.3, §9 |
| K10 | D6 için ISC, S6 için SRCMOD aynı indirme adımında | §9 adım 5 |
| K11 | n_on ≥ 84 ve ≥ 547 (`esik_n_on`) | §4.2, kod |
| K12 | §5 kapı 4 "Kod incelemesi" | §5 |
| K13 | GeoNet: yarıların toplamı bütüne eşitse kabul | §5 |
| K14 | Dondurmadan sonra betikler geçici kopyada; sha256 karşılaştırması; docstring "≈ 4 sn" | Ek B, kod |
| K15 | Sahte j ve S2'de Mc_son gün sayısının başlangıcı | §3.5 |
| §H | `pozitif_kapi` ve metindeki öteki sayıların bilgi anahtarları eklendi; liste değişmedi (sha256 §3.1, sürüm 2 ile aynı); §16 madde 16; kod incelemesinin özel denetim listesi | kod, §9 adım 4, §16 |
| — | Durum satırı, kök oturum kararı, önsayım özeti (K⁺, K_nt), §0 öncelik sırası, körlük beyanı, kod listesi; §9 adım 1 dondurulan dosyalar ve çıktı sha256'ları; İNCELEME-2 betikleri numpy ile (`tr6a_inc2_b1.py`–`b4.py`); `tr6a_md_denetim.py` | başlık, §0, §9, Ek B |

Uygulanamayan bulgu yoktur. Okuma notları (sapma değil):
- B4'ün 6–9 sınamaları "Doğrulama listesine" eklendiği için Okada tablo değerleri okunsa da koşulur; bulgunun gerekçesi
  (yönelim ve izdüşüm hataları 1–5'ten de tablo satırlarından da geçer) bunu gerektirir.
- §10'daki S1 tutma tablosu yuvarlanmamış P(A)'dan hesaplanır. Üçüncü ondalıkta İNCELEME-2 B1 tablosundan farklıdır
  (N0⁺ 3: 0,197 / 0,383 / 0,526, İNCELEME-2'de 0,196 / 0,381 / 0,524; N0⁺ 10, K⁺ 10: 0,842, İNCELEME-2'de 0,841).
  Metindeki iki ondalıklı değerler (0,84; 0,98) aynıdır.
- §6.4 madde 6 yeni bir kural değildir: B6'nın hüküm adına eklediği "(koşu sonrası değişiklikle: <ad>)" ekini kapalı
  listeye bağlar.
- §9 adım 2'de sürüm 2'nin "arka planda Poisson + GK tipi ikincil diziler" ifadesi B3'ün (i) ve (ii) biçimleriyle
  değiştirildi; yapay sonlu fay ve Dieterich yanıtı cümlesi korundu.


---

## Dondurma notu (12 Kasım 2026)

Bu sürüm, iki bağımsız incelemenin (İNCELEME-1, İNCELEME-2) bütün düzeltmeleri işlenerek donduruldu. Dondurma anına kadar olay sonrası hiçbir katalog sorgusu yapılmadı, hiçbir lobda oran ya da ΔCFF hesaplanmadı. Değişiklik listesindeki iki "okuma notu" (Okada 6–9 sınamaları her durumda koşulur; §6.4 madde 6) bağlayıcıdır.
