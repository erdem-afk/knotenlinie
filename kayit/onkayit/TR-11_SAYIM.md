# TR-11 tasarım ve üstveri sayımı: GNSS 2 yıllık hız değişiminin sakin pencerelerdeki taban dağılımı

11 Kasım 2026. Durum: tasarım + üstveri sayımı. Hiçbir tenv3 ya da başka zaman serisi indirilmedi, S hesaplanmadı.
2026 tarihli deprem verisi sorgulanmadı. Marmara kutusundaki (39,5–42,0° K, 26,0–31,5° D) istasyonlar tümüyle dışlandı.
Betikler: `kayit/turetme/tr11/sayim_ustveri.py` (sayım), `kayit/turetme/tr11/beklenti_gurultu.py` (yalnız yapay
gürültüyle beklenen S). Kaynak: `kayit/turetme/ZINCIR.md` Halka 2, TR-1 ön kayıt sürüm 2 ve `TR-1_INCELEME-2.md`.

## Hüküm

**Sınav kurulabilir, ama yalnız küresel ve ağırlıkla "sakin iç bölge" tabanı olarak.** Önceden yazılmış kurallarla
üstveriden 803 sakin küme-penceresi, 336 bağımsız yer ve 61 adet 10°×10° blok çıkıyor. Doluluk şartı yaklaşık
uygulanınca 744 / 321 / 58 oluyor. Kapı (≥ 100 yer, ≥ 30 blok) rahatça geçiliyor. Ancak birimlerin %97'si düşük
sismisiteli yerlerde (sınıf D: 323 yer). Marmara benzeri doğrultu atımlı levha sınırı kuşağında (sınıf A) yalnız
**2 yer** var ve ikisi de volkanik okyanus adası (Azorlar, İzlanda). Öteki aktif kuşakta (sınıf B) 11 yer var.
On altı kural değişkesinin hiçbirinde A sınıfı 9 yeri aşmıyor. Yani ölçüm "kararlı ya da az sismik bir bölgede
yıl ölçekli GNSS gürültü tabanı" için güçlü, "aktif doğrultu atımlı fay çevresindeki taban" için **güç yok**.
Marmara'ya yapılacak çeviri bu yüzden bir alt sınır olur: gerçek Marmara tabanı ölçülenden büyükse,
algılanabilir en küçük derin kayma hızı değişimi de buradaki formülün verdiğinden büyüktür. İndirme yükü 4730
istasyon, kabaca 4 GB.

## 1. Soru ve neyi ölçmediği

TR-11, TR-1 sürüm 2'nin menteşe modeli ve S istatistiğiyle şunu ölçer: depremle ilgisi olmayan 5 yıllık pencerelerde
S ne sıklıkla belli bir büyüklüğü aşar. Bu bir yanlış alarm oranıdır. İkinci adımda bu taban, sonsuz vida
dislokasyonu formülüyle "aşılması için gereken derin kayma hızı değişimi"ne çevrilir. Bir olayla karşılaştırma,
tahmin ya da olasılık yoktur. Sonuç bir ölçüm sınırı cümlesidir. Mutlak İstanbul deprem olasılığı yazılmaz.

## 2. Tasarım (kodlanabilir tanımlar)

TR-1 sürüm 2'den aynen alınanlar: veri kaynağı (NGL IGS20 tenv3, yatay bileşenler), steps.txt ayrıştırması (YYMONDD,
00–79 → 20xx), haversine (R = 6371 km), istasyon ölçüsü (sabit + eğim + yıllık ve altı aylık + kod 1 sıçramaları +
menteşe max(0, t − H); bir kez 5 × 1,4826 × MAD ayıklaması), Δv = menteşe katsayısı (doğu, kuzey), küme ölçüsü S
(yakın istasyon Δv'si eksi referans Δv'lerinin bileşen bazında medyanı; boyların medyanı). INCELEME-2 bulgu 7.1
uygulanır: her yıl aralığı floor(n × 365,25) gün (5 yıl = 1826 g, 2 yıl = 730 g).

**2.1 Pencere epokları (önceden sabit takvim, örtüşmez).** T ∈ {2003-01-01, 2008-01-01, 2013-01-01, 2018-01-01,
2023-01-01}. Pencere W = [w0, w1] = [T − 1826 g, T − 1 g]. Menteşe H = T − 730 g (taban 3 yıl, yakın dönem 2 yıl).
Son epokta T + 2 yıl = 2025-01-01; katalog 2025 sonunda bittiği için gelecek şartları hesaplanabiliyor. 2028 ve
sonrası için epok eklemek ayrı bir karar olur.

**2.2 Küme merkezleri (önceden sabit ızgara).** Enlem satırları φ = −89°, −87°, …, 89° (2° ≈ 222 km). Her satırda
n = floor(360 cos φ / 2) eşit aralıklı boylam: λ_k = −180° + k × 360°/n. Aradaki uzaklık ≥ 2 × 100 km olduğu için
iki merkezin yakın istasyon kümeleri ortak istasyon taşımaz. Marmara kutusundaki merkezler atılır. 10 268 merkezden
820'sinin 100 km içinde (zamandan bağımsız) ≥ 3 Marmara dışı istasyonu var. Yalnız bunlar sayılır.

**2.3 İstasyon uygunluğu (her T için).**
1. Marmara kutusunda değil.
2. DataHoldings Dtbeg ≤ w0 ve Dtend ≥ w1. Koşuda doluluk şartı TR-1'deki gibi uygulanır (taban ve yakın dönemde
   ayrı ayrı ≥ 0,60). Sayımda bu şart ya atlandı (üst sınır) ya da NumSol / gün aralığı ≥ 0,60 ile yaklaşık kondu.
3. [w0 − 730 g, w1] aralığında steps.txt kod 2 kaydı yok (uzaklığı ne olursa olsun). Kod 2, NGL'nin yarıçap
   kuralıdır (r = 10^(M/2 − 0,79) km). Yani istasyon bu sürede kosismik etkili hiçbir depremin yarıçapında değildir.
   TR-1'den farkı: eşik/4 yerine bütün kayıtlar. Sakin pencerede kod 2 sıçrama terimi bu yüzden hiç olmaz.
4. Kod 1 (ekipman) kayıtları sıçrama terimi olur. Aynı güne düşenler tek sıçramadır. H'ye 30 günden yakın ya da
   pencerenin ilk ya da son 30 gününe düşen bir kayıt varsa istasyon uygun değildir (TR-1 ile aynı).

**2.4 Küme kurma (TR-1 ile aynı).** Yakın: merkezin ≤ 100 km içindeki uygun istasyonlar. Referans: 200–500 km
halkasındaki uygun istasyonlar (olay olmadığı için M < 7,5 halkası). Uzaklığa göre sıralanır, eşitlikte istasyon adı.
En yakın en çok 8 + 8 alınır. Geçerlilik: ≥ 3 yakın ve ≥ 3 referans.

**2.5 Sakin pencere (merkeze göre, katalog).** Üçü birden sağlanmalıdır:
- Ş1: merkezin 200 km içinde, [w0 − 5 yıl, T + 2 yıl] aralığında M ≥ 6,0, derinlik ≤ 40 km deprem yok
  (ComCat, 1976–2025, yalnız `type = earthquake`).
- Ş2: merkezin 500 km içinde, [w0 − 10 yıl, T + 2 yıl] aralığında M ≥ 7,0, derinlik ≤ 70 km deprem yok
  (ComCat 1985–2025).
- Ş3: merkezin 1000 km içinde, [w0 − 10 yıl, T] aralığında M ≥ 8,0 deprem yok (Tohoku, Maule ve Sumatra tipi
  büyük postsismik alanlar).
"T + 2 yıl" uzantısı olay öncesi pencereleri dışarıda tutar. Böylece taban, TR-1'deki olay penceresi
türünden olmaz.

**2.6 Bağımsızlık birimi.** Birincil birim **yer** (ızgara merkezi). Aynı yerin farklı epokları tek birimdir,
çünkü istasyon ve anıt etkileri ile kırpışma gürültüsü epoklar arasında süreklidir. Ortak mod hatası yüzlerce
km'ye uzandığı için güven aralıkları **10°×10° blok** bootstrap'ıyla verilir (blok = floor(φ/10), floor(λ/10)).
Yer bootstrap'ı bilgi satırıdır. Referans halkaları komşu yerlerde örtüşebilir; blok bootstrap'ı bunu da kapsar.

**2.7 Ortam sınıfı (yer özelliği; yalnız katalog üstverisinden).** Merkezin 150 km içinde:
- **D (düşük sismisite):** 1976–2025 arasında M ≥ 6,0, derinlik ≤ 40 km olay yok.
- **A (doğrultu atımlı kuşak):** M6,0–7,2, derinlik ≤ 25 km olan ve ComCat mekanizması bulunan en az 2 olay var,
  bunların ≥ %50'si doğrultu atımlı. Mekanizma: en yüksek ağırlıklı `moment-tensor`, yoksa `focal-mechanism` ürünü.
  Düğüm düzlemi 1'in rake'i için |rake| ≤ 30° ya da ≥ 150° (TR-2 indirmesi, 2952 olay).
- **B (öteki aktif):** kalanlar.
Sınıf, pencerenin dışındaki depremlerle de atanır. Sakinlik zamana bağlı bir şarttır, sınıf ise yere ait bir özelliktir.
Bölge etiketi kaba enlem-boylam kutularıyla verilir (betikteki `bolge`) ve yalnız raporlama içindir.

**2.8 Marmara.** Kutudaki istasyonlar ve merkezler tümüyle dışlanır. ZINCIR Halka 2 "Marmara'nın 2016 ve öncesi"
seçeneğini açık bırakmıştı, ama tenv3 dosyası bütün seriyi taşır. 2016 öncesini kullanmak için 2017 sonrası veriyi
de indirmek gerekir, bu da VE-1 körlüğünü bozar. Kayıp da önemsiz: kutuda 2008 ve 2013 epoklarında pencereyi
kapsayan, kod 2 kaydı olmayan yalnız 2 istasyon var. Bunlar tek başına bir küme kurmaya yetmez.

## 3. Üstveri sayımı

Girdi (depo dışı; SHA-256 ilk 16 hane): DataHoldings.txt `4a98b65ad74c425b`, steps.txt `887501a438c41c34`, ev70.csv
`370b728af37ee330`, ev70_pre.csv `60e448a8655ceb46`, m6_havuz.csv `969c5c54851ee353`, birincil_aday.csv
`f905535cf0837dbb`, birincil_aday_fm.csv `8c9cae2206b35c11`, mekanizma.jsonl `eb30828a7a1fff17`. Son dördü TR-2'nin
ComCat indirmesidir (bitiş 2025-12-31). Yeni sorgu yapılmadı. Koşu yaklaşık 13 sn.
`python3 -I -B kayit/turetme/tr11/sayim_ustveri.py <ngl> <tr2/ham> [--json ana.json]`

**3.1 Toplam**

| Kural seti | Küme-pencere | Bağımsız yer | 10° blok | İndirilecek istasyon | Kaba hacim |
|---|---|---|---|---|---|
| **Ana (doluluk atlandı, üst sınır)** | **803** | **336** | **61** | **4730** (yakın rolünde 3017) | **≈ 4,0 GB** |
| Doluluk ≈ NumSol / gün aralığı ≥ 0,60 | 744 | 321 | 58 | 4316 | ≈ 4,0 GB |

Epok başına (ana): 2003: 14, 2008: 68, 2013: 171, 2018: 259, 2023: 291. Yer başına epok sayısı: 1 epok 83, 2 epok
104, 3 epok 95, 4 epok 43, 5 epok 11. Küme boyutu: n_y = 3: 160, 4: 104, 5: 59, 6: 54, 7: 55, 8: 371; n_r = 8 olan
774 (%96). Yakın istasyon uzaklığının küme-pencere medyanı: çeyrekler 52 / 64 / 76 km. Hacim 23,6 milyon çözüm günü ×
yaklaşık 170 B/satır olarak hesaplandı. Satır boyu kaba bir tahmindir, dosya boyu ölçülmedi.

**3.2 Ortam sınıfına göre (ana)**

| Sınıf | Küme-pencere | Yer | Blok |
|---|---|---|---|
| D, düşük sismisite | 779 | 323 | 59 |
| B, öteki aktif | 22 | 11 | 8 |
| **A, doğrultu atımlı kuşak** | **2** | **2** | **2** |

A sınıfındaki iki yer Azorlar (39° K, 27,2° B; 2023 epoğu) ve İzlanda'dır (63° K, 20° B; 2023). İkisi de volkanik
okyanus adasıdır, Marmara benzeri değildir. B sınıfının 11 yeri: Nevada ve Idaho (2), Kuzey İtalya, Avusturya ve
Alpler (4), Tiren (1), Batı Avustralya (1) ve Anadolu'da Marmara dışı 3 yer. Anadolu yerleri (35° K 33,1° D;
37° K 34,0° D; 41° K 33,3° D) yalnız 2018 epoğunda geçerli. 41° K 33,3° D merkezi İsmetpaşa sünme kesimine yakındır.
Bu bir bilgi notudur, tasarıma girmez.

**3.3 Bölgeye göre (ana; küme-pencere / yer / blok)**

| Bölge | KP | Yer | Blok |
|---|---|---|---|
| K. Amerika (Kaliforniya-Nevada dışı) | 296 | 111 | 12 |
| Avrupa (öteki) | 273 | 92 | 13 |
| öteki | 79 | 46 | 20 |
| Avustralya | 53 | 32 | 10 |
| ABD batı / Kaliforniya-Nevada | 37 | 18 | 3 |
| Meksika / Orta Amerika | 34 | 19 | 4 |
| Alp-İtalya-Balkan-Ege | 24 | 11 | 3 |
| Anadolu (Marmara dışı) | 3 | 3 | 2 |
| And / G. Amerika batı | 2 | 2 | 2 |
| İzlanda | 2 | 2 | 1 |
| Japonya, Yeni Zelanda, Alaska, Çin/Tayvan | 0 | 0 | 0 |

En kalabalık 5 blok küme-pencerelerin %31'ini taşıyor (Avrupa ve ABD doğusu). Bu yüzden bootstrap blok
düzeyinde yapılır ve "en büyük bloğu dışarıda bırak" bilgi satırı eklenir. Bu satır, INCELEME-2 bulgu 4'teki dar
havuz sorununun karşılığıdır.

**3.4 Tanı: hangi kural ne kadar eliyor** (ön kayıt kuralı değil; INCELEME-2 bulgu 9 uyarınca kayıt için)

| Değişke | KP | Yer | Blok | A sınıfı (KP / yer) |
|---|---|---|---|---|
| Ş1–Ş3 kapalı (yalnız istasyon kuralları) | 853 | 360 | 64 | 19 / 10 (7'si Kaliforniya) |
| Yalnız Ş1 kapalı | 817 | 342 | 63 | – |
| Yalnız Ş2 kapalı | 829 | 352 | 63 | – |
| Yalnız Ş3 kapalı | 803 | 336 | 61 | – |
| Kod 2 istasyon kuralı kapalı | 918 | 378 | 79 | – |
| Kod 1 sıçrama kuralı kapalı | 811 | 337 | 61 | – |
| Sınıf yarıçapı 150/200 km × en az 1/2 mekanizma × Ş2 300/500 km × kod 2 ön süresi 0/2 yıl (16 değişke) | 803–860 | 336–365 | – | en çok 12 / 9 |

Okuma şöyle: Sakinlik şartları toplamı az etkiliyor (−%6). Ama aktif yerleri seçerek eliyor: A+B 55 küme-pencereden
24'e iniyor. Kaliforniya'yı kod 2 kuralı (her M5 civarı olay bir yarıçap kaydı üretiyor) ve Ş2 (Landers, Hector
Mine, El Mayor-Cucapah, Ridgecrest) eliyor. A sınıfı hiçbir savunulabilir ayarda 20 yere çıkmıyor. Bu, TR-1'deki
darboğazın aynısı: aktif fayın yanında kirlenmemiş pencere nadir.

## 4. Önceden yazılacak çıktılar ve beklenti

**4.1 Çıktılar (koşuda yazdırılacak).** Bütün sakin küme-pencerelerinde S'nin medyanı ile %90, %95 ve %99
nicelikleri. Her birinin %90 güven aralığı blok bootstrap'ıyla hesaplanır: B = 2000, tohum 20261111, blok yeniden
örneklenir ve içindeki bütün küme-pencereler alınır. Kırılımlar:
(a) küme boyutu n_y ∈ {3–4, 5–7, 8};
(b) ortam sınıfı A, B, D (her biri ancak ≥ 30 yer varsa; yoksa "güç yok");
(c) epok;
(d) bilgi satırları: referans farkı alınmadan S; yer bootstrap'ı; en büyük blok dışarıda; doğu ve kuzey bileşen
    Δv'lerinin ayrı medyanı ve %95'i; pencerede kod 1 kaydı olan istasyonlar dışarıda.
%99 niceliği yalnız ≥ 300 küme-pencerelik katmanda yazılır.

**4.2 Beklenti (sınanan şey).** Gürültü modeli N0: her yatay bileşende bağımsız beyaz gürültü σ_w = 1,5 mm ve
kırpışma gürültüsü b_f = 3,0 mm/yıl^0,25 (Williams 2003 kesirli fark kovaryansı). Ortak mod hatası yoktur ya da
referans farkıyla tümüyle siler. İstasyonlar birbirinden bağımsızdır. Bu modelde menteşe katsayısının standart
sapması (boşluksuz 1826 gün) σ_h = 0,748 mm/yıl'dır. Birim katkılar: beyaz 1 mm → 0,069; kırpışma 1 mm/yıl^0,25 →
0,247; rastgele yürüyüş 1 mm/yıl^0,5 → 1,022 mm/yıl. S/σ_h dağılımı Monte Carlo ile ve ana sayımdaki n_y karışımıyla
(n_r = 8) hesaplandı: medyan 1,275; %90 1,783; %95 1,955; %99 2,32.

| Model (boşluksuz, ana karışım) | σ_h | S medyan | %90 | %95 | %99 (mm/yıl) |
|---|---|---|---|---|---|
| **N0** (1,5 mm; 3 mm/yıl^0,25) | 0,75 | 0,95 | 1,33 | **1,46** | 1,73 |
| N0-düşük (b_f 2) | 0,50 | 0,64 | 0,90 | 0,99 | 1,17 |
| N0-yüksek (b_f 4) | 0,99 | 1,26 | 1,77 | 1,94 | 2,30 |
| N1 = N0 + rastgele yürüyüş 1 mm/yıl^0,5 | 1,27 | 1,61 | 2,26 | 2,48 | 2,94 |

Bu sayılar ölçüm değildir; yalnız N0'ın ne öngördüğünü gösterir. Koşuda beklenti her küme-pencere için yeniden
hesaplanır. Hesap gerçek gün maskesiyle (hangi günlerin çözümü var; konum değerleri kullanılmaz) ve gerçek
n_y/n_r ile yapılır. Havuzlanan beklenen %95 değeri q95_N0'dır. Boşluklar σ_h'yi büyüttüğü için q95_N0 tablodaki
1,46'dan biraz büyük çıkacaktır.

Önsel yön (beyan): ölçülen %95'in N0'ı **aşması** beklenir. Gerekçe: AV-1'in ön ölçümünde ISTA'nın yıllık ortalama
artık sd'si 1,4 mm idi (defterde). N0 aynı büyüklük için yaklaşık 0,38 mm veriyor (betikte MC; model ayrıntısı AV-1
ile aynı değil). Bu, N0 dışında renkli ya da yerel gürültü olduğuna işaret ediyor. Beyan bir hipotezdir, hükmü
değiştirmez.

**4.3 Önerilen hüküm satırı (tek, sırayla, otomatik)**

1. **Veri kapısı.** İndirmeden sonra, gerçek doluluk şartıyla yer < 100 ya da blok < 30 ise hüküm **"veri yok"** olur.
2. **Kod denetimi.** (i) N0'dan üretilmiş yapay serilerde (gerçek gün maskeleri) ölçülen q95 / q95_N0 oranı
   [0,9, 1,1] dışında kalırsa hüküm "geçersiz (kod)" olur. (ii) Pozitif kontrol: küme-pencerelerin
   SHA-256(T | merkez) sırasındaki ilk yarısının yalnız yakın istasyonlarına doğu yönünde max(0, t − H) × 3 mm/yıl
   eklenir. medyan(S_eklenen − S_özgün) [2,4, 3,6] dışında kalırsa hüküm "geçersiz (kod)" olur.
3. **Ana ölçü.** ρ = q95_ölçülen / q95_N0. %90 güven aralığı [ρ_L, ρ_U] blok bootstrap'ıyla hesaplanır (pay ve
   payda aynı örneklemde). ρ_L > 1 ise **"taban N0'dan büyük"** (N0 yanlış alarmı küçümsüyor). ρ_U < 1 ise
   **"taban N0'dan küçük"**. Ötekilerde **"N0 ile uyumlu"**. N1 aynı biçimde bilgi satırı olarak yazılır.
4. **Sınıf satırları.** A, B, D için q95 ve aralığı ancak ≥ 30 yer varsa yazılır, yoksa o sınıf **"güç yok"** olur.
   Bugünkü sayımla A (2 yer) ve B (11 yer) için güç yok önceden bellidir. Bu sonuç önceden kabul edilir.
5. **Çeviri satırı (bölüm 5).** Her zaman q95'in **üst** güven sınırı U kullanılır. A sınıfı "güç yok" ise satıra
   "alt sınır: düşük sismisiteli bölge tabanı" etiketi zorunludur.

Hüküm cümlesinin biçimi: "TR-11: [veri yok | geçersiz | taban N0'dan büyük | N0 ile uyumlu | taban N0'dan küçük];
sakin pencerelerde S, küme-pencerelerin %5'inde q95 = X [L, U] mm/yıl'ı aşar (yer K, blok B, KP N; sınıf D). Sınıf A:
güç yok. Marmara çevirisi: Δs_min(D, x) ≥ π·U / medyan_i|arctan(x_i/D) − m_r| (alt sınır)."

**"Veri yok"** yalnız 1. adımda verilir. **"Güç yok"** yalnız sınıf satırında verilir (≥ 30 yer şartı). Ana satırda
güç yok hükmü yoktur, çünkü sınav bir yoklama değil, bir ölçümdür.

## 5. Marmara'ya çeviri (tek formül; yeni fizik iş paketi değil)

Kilitlenme derinliği D'nin altında, sonsuz uzun doğrultu atımlı bir fayda derin kayma hızı Δs kadar değişsin.
Faydan işaretli x uzaklığındaki istasyonun faya paralel hız değişimi:

  Δv(x) = (Δs/π) · arctan(x/D)

Referans halkası 200–500 km'dedir ve arctan(x_r/D) ≈ ±π/2 olur. m_r = medyan_r arctan(x_r/D) olsun. Dengeli bir
halkada (fayın iki yanında eşit sayıda referans) m_r ≈ 0'dır. Halkanın tamamı bir yandaysa m_r ≈ ±π/2 olur.
Menteşe Δs'nin başladığı güne denk gelirse sinyalin S'ye katkısı Δs'yle doğrusaldır:

  S_sinyal = Δs · G,  G(D, {x_i}) = medyan_i |arctan(x_i/D) − m_r| / π

**Algılanabilir en küçük değişim:** Δs_min = U / G. Burada U, ölçülen %95 S'nin üst güven sınırıdır. Sinyal ve
gürültü vektörel toplanır. Buna göre %50 algılama için yaklaşık alt değer
Δs_min ≈ √(U² − S50²) / G'dir (S50 sakin medyan). Ana çeviri birinci formüldür (tutucu), ikincisi bilgi satırıdır.

G değerleri (dengeli referans, tek uzaklıklı küme; 1/G = Δs_min / U):

| D \ x | 5 km | 10 km | 20 km | 30 km | 50 km |
|---|---|---|---|---|---|
| 5 km | 0,250 (4,0) | 0,352 (2,8) | 0,422 (2,4) | 0,447 (2,2) | 0,468 (2,1) |
| 10 km | 0,148 (6,8) | 0,250 (4,0) | 0,352 (2,8) | 0,398 (2,5) | 0,437 (2,3) |
| 15 km | 0,102 (9,8) | 0,187 (5,3) | 0,295 (3,4) | 0,352 (2,8) | 0,407 (2,5) |

Yani Marmara geometrisinde (D 5–15 km, istasyonlar 5–50 km) Δs_min, ölçülen U'nun yaklaşık 2–10 katıdır. Burada
sayı verilmez, çünkü U ölçülmedi. Formülün yanlılıkları:
(i) sonsuz fay varsayımı sinyali abartır, sonlu bir yama (uzunluk L) daha az sinyal üretir; Δs_min yukarı gider;
(ii) değişim H'den sonra başlarsa menteşe katsayısı küçülür; Δs_min yukarı gider;
(iii) referanslar tek yandaysa (Marmara'nın kuzeyi ve güneyi dengesiz olabilir) G aynı yandaki istasyonlar için
     arctan(D/|x|)/π'ye düşer;
(iv) taban aktif kuşakta ölçülmediği için U Marmara'da büyük olasılıkla daha büyüktür.
Dört yanlılığın hepsi aynı yöndedir: buradaki Δs_min bir **alt sınırdır**. Sığ sünme ve D'nin üstündeki geçiciler
(İsmetpaşa tipi) bu modelin kapsamı dışındadır (AV-3, InSAR).

Ölçek için karşılaştırma (literatür, aşağıda): Prens Adaları kesiminde kayma açığı hızı 10–15 mm/yıl. Kilit tümüyle
çözülse Δs bu mertebede olur. Bu bir tavandır, beklenti değildir.

## 6. Literatür taraması (OpenAlex; yalnız özetler okundu)

| İş | Sayı | Durum |
|---|---|---|
| Blewitt, Kreemer, Hammond, Gazeaux 2016, MIDAS (10.1002/2015jb012552) | Kuzey Amerika levha içinde yatay hız RMS doğruluğu ±0,23 mm/yıl; yapay kör sınavda ±0,33 mm/yıl | Doğrulandı (özet). Uzun serilerin tüm dönem hızıdır; 2 yıllık menteşe farkı için değildir. |
| Mao, Harrison, Dixon 1999 (10.1029/1998jb900033) | Beyaz + kırpışma en iyi model; yalnız beyaz varsayımı hız hatasını 5–11 kat küçümsüyor | Doğrulandı. Genlik değerleri özette yok, **doğrulanamadı**. |
| Williams vd. 2004 (10.1029/2003jb002741) | Küresel çözümlerde beyaz + kırpışma; ortak mod silinmiş bölgesel çözümlerde gürültü belirgin düşük | Nitel olarak doğrulandı. Yatay genlikler (σ_w ≈ 1–2 mm, b_f ≈ 2–4 mm/yıl^0,25 diye bilinen değerler) **doğrulanamadı**. N0 bu aralıktan seçilmiş bir varsayımdır. |
| Santamaría-Gómez vd. 2011 (10.1029/2010jb007701) | Haftalık seriler: beyaz ≈ 2 mm, güç yasası ≈ 6 mm ortalama genlik; düşey hız belirsizliği ≈ 0,3 mm/yıl, beyaz varsayımının 4–5 katı; eski verinin 2–3 yıllık serisi 12 yıllıklar kadar gürültülü | Doğrulandı (özet). Bileşen ayrımı (yatay değerler) **doğrulanamadı**. |
| Dong vd. 2006 (10.1029/2005jb003806) | Günlük çözümlerde baskın hata kaynağı uzamsal ve zamansal ilişkili ortak mod hatası; SCIGN ölçeğinde yaklaşık düzgün | Doğrulandı (nitel; sayı yok). |
| Kłos vd. 2017 (10.1007/s10291-017-0674-x) | Mevsimsel terimler kısa serilerde hız belirsizliğini büyütüyor; kırpışma için ≈ 9 yıl eşiği | Doğrulandı. |
| Ergintav vd. 2014 (10.1002/2014gl060985) | Prens Adaları kayma açığı 10–15 mm/yıl; orta kesimde birikim yok (sünme) | Doğrulandı. |
| Rousset vd. 2016 (10.1002/2016gl068250); Jolivet vd. 2023 (10.1029/2022jb026018) | İsmetpaşa: sünme 8 ± 3 mm/yıl, 31 günlük 2 cm'lik geçici (0–4 km); yavaş kayma olaylarının yinelenme süresi 2,5 yıl | Doğrulandı. Sığ olaylardır, vida modelinin D'si altında değildir. |
| Blétery ve Nocquet 2025 (10.26443/seismica.v3i2.1383) | Ortak mod süzgeci uygulanınca öncül sinyal kayboluyor (yazarlar bunu kabul ediyor, ama süzgecin tektonik sinyali de silebileceğini söylüyor) | Doğrulandı. |
| Marmara veya KAF'ta yıl ölçekli GNSS geçici algılama eşiği | – | Tarama ("Marmara GPS velocity transient", "North Anatolian Fault aseismic slip transient GPS") özel bir eşik çalışması **bulamadı**. |

## 7. Defterle örtüşme

- **TR-1 (güç yok):** S ve menteşe aynısı. TR-11 TR-1'in eksik "olağan" dağılımını verir, ama TR-1'i yeniden açmaz.
  TR-1'in darboğazı olay sayısıydı. Ayrıca TR-11'in sınıf A'daki güçsüzlüğü TR-1'deki temiz pencere darboğazının
  aynısıdır.
- **VE-1 (veri yok; Marmara 2017+ kör):** Marmara kutusu tümüyle dışlandığı için körlük bozulmaz. TR-11'in çıktısı
  (U ve Δs_min) VE-1 yeniden açılırsa bir algılama eşiği olarak kullanılabilir. VE-1 sonucu hakkında bilgi
  sızdırmaz.
- **AV-1 (VE-1'e birleşti):** ISTA'nın yıllık ortalama artık sd'si 1,4 mm. Bölüm 4.2'deki önsel yönün tek dayanağıdır.
- **S-7 (ayırt edilemez), TK-E1:** yavaş geçicilerin olasılık çarpanı. TR-11 olasılık terimi üretmez. Yalnız
  "Marmara'da GNSS'in görebileceği en küçük derin geçici" sınırını verir. Bu, S-7'nin yeniden açma şartını tek başına
  sağlamaz.
- **AV-3 ve TR-10 (InSAR/NISAR sünme):** tamamlayıcıdır. Sığ sünme InSAR'ın, D'nin altındaki kayma GNSS'in alanıdır.
  Örtüşme yok.
- **FA-6 (Blétery–Nocquet, ortak mod):** risk 2 ile aynı mekanizma. Ortak mod hatası referans farkıyla silinir ve
  bunun bedeli bölüm 8'de yazılıdır.
- **Y-1 ve DD-2 (PIF karadan görülmüyor):** aynı geometri dersinin genelleştirilmesidir. G çarpanı, karadan uzaklık
  arttıkça Δs_min'in nasıl büyüdüğünü sayıya döker.

## 8. En büyük üç risk

1. **Sakin seçim tabanı aşağı çeker ve temsil Marmara değildir (en büyük risk).** Küme-pencerelerin %97'si D
   sınıfında: Kuzey Amerika içi, Avrupa, Avustralya. Bu yerlerde postsismik eğrilik, sünme, aktif fay yükleme
   değişimi ve aktif tektoniğin hidrolojiyle etkileşimi yoktur. Marmara'da ise 1999 postsismiği sürüyor ve orta
   kesimde sünme var. Ölçülen q95 Marmara için büyük olasılıkla küçüktür, Δs_min de iyimserdir. Önlem: çeviri her
   zaman U ve "alt sınır" etiketiyle yazılır; A ve B sınıfları güç yok diye yazdırılır; Ş1–Ş3 kapalı değişkesinin
   q95'i bilgi satırı olarak raporlanır (kirlenmiş tarafın sınırı).
2. **Ortak mod hatası ve NGL işleme değişimleri.** Günlük küresel çözümlerde ortak mod hatası baskındır (Dong 2006,
   Williams 2004). Referans halkası (200–500 km) bunu ancak düzgünse siler. Yüzlerce km'de değişen ortak mod hatası
   ve 2017 başı gibi çerçeve veya model değişimleri bütün kümelerde aynı tarihte menteşe benzeri bir izlenim
   bırakabilir. Önlem: epok kırılımı; referans farkı alınmadan S bilgi satırı; blok bootstrap. Ters yönlü yan etki:
   referans farkı gerçek geniş ölçekli tektonik sinyali de siler (Blétery–Nocquet tartışması).
3. **Belgelenmemiş sıçramalar ve anten değişimleri; hidroloji.** steps.txt yalnız kayıtlı ekipman değişimlerini
   taşır. Kayıtsız bir anten değişimi ya da anıt sorunu H yakınına düşerse S'nin kuyruğunu (q95, q99) doğrudan
   şişirir. Çok yıllı hidrolojik yükleme (kuraklık, yeraltı suyu çekimi; örneğin 2012–2016 Kaliforniya) yatayda da
   mm düzeyinde, yıl ölçekli ve yüzlerce km'lik eğim değişimi üretir. Yakın ve referans grupları farklı havzalarda
   kalırsa silinmez. Bunlar Marmara'da da gerçek tabanın parçasıdır, ama iklim ve jeoloji farkı aktarımı bozar.
   Önlem: "kod 1'li istasyonlar dışarıda" bilgi satırı; q99'un yalnız ≥ 300 küme-pencerede yazılması; tek bir
   istasyonun etkisi S'nin medyan yapısıyla sınırlıdır.

Ayrıca: volkanik yerler sınıflandırılmadı (A sınıfının iki yeri de volkanik ada). Doluluk şartı gerçek veriyle
sayıları %5–10 düşürebilir. İndirme yaklaşık 4730 dosya ve 4 GB'tır. NGL hız sınırı için uzaklık sırasıyla indirip
gereken sayıya ulaşınca durmak uygulanamaz (bütün küme-pencereler gerekli). Hacim sorun olursa önceden yazılmış bir
SHA-256 sırasıyla 150 yerlik alt örneklem seçilebilir.

## 9. Sonraki adım

Bu sayım bir ön kayıt değildir. Ön kayıt metni bölüm 2 ve 4'ü aynen alır, bağımsız incelemeden geçer, sonra
dondurulur. Kod yalnız yapay serilerle ve Marmara dışındaki, herhangi bir küme-penceresine girmeyen en çok 5 gerçek
istasyonla geliştirilir. Koşu tektir. Sınıf A'nın güçsüzlüğü önceden bilindiği için, Marmara benzeri tabanı ölçmenin
tek yolu ayrı bir sorudur: yoğun ve kesintisiz bir aktif fay ağı, örneğin Kaliforniya'da kod 2 kuralının
postsismik modelle değiştirilmesi. Bu TR-1 bölüm 9(a) ile aynı yeniden açma şartıdır ve bu sayımın kapsamında değildir.
