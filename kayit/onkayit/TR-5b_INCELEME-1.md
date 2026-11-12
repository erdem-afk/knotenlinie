# TR-5b ön kayıt: bağımsız inceleme 1

İncelenen: `TR-5b_sismik-hiz-oncul_ONKAYIT.md`, TASLAK sürüm 1 (12 Kasım 2026). Dayanaklar: `TR-5_TR-4_SAYIM.md` (Ek 1,
Ek 2) ve `kayit/turetme/tr5/` (`tr5b_liste.py/.json`, `tr5b_olaylar.csv`, `tr5b_kontroller.csv`, `tr5b_yapay.py`,
`tr5b_guc.py`, sonuç json'ları, `sayim_ustveri.py`, `doluluk_yokla.py`). Hiçbir dalga formu indirilmedi, açılmadı ya da
yoklanmadı. Taslak ve `tr5` dizini değiştirilmedi. Yapılanlar:
- `tr5b_guc.py` ve `tr5b_yapay.py`, karalama dizinine kopyalanıp **bağımsız tohumla (777123)** `python3 -I -B` ile koşuldu.
- `tr5b_yapay.E3`, dört ayrı tohumla (11, 22, 33, 44) yeniden koşuldu.
- Ek benzetimler yazıldı: 4. adımın başka ölçütleri, plasebo şartının değeri, olay gürültüsünün etkisi.
- Bağlayıcı liste, TR-2 M ≥ 6 havuzu, M ≥ 5 kataloğu ve FDSN kanal üstverisi üstünden denetimler yapıldı: kontrol geçmişi,
  maske dilimleri, PK istasyonları, volkanik kontroller, kota, istasyon tekrarı, istek sayısı.
- Literatür `kayit/oa.py ara|ozet` ile yoklandı (yalnız özetler).

Betikler depo dışında, karalama dizininde: `inc5b/denetle.py`, `denetle2.py`, `guc_ek.py`, `guc_ek2.py`, `e3_tohum.py`.

## Hüküm

**DÜZELTMEYLE KABUL.** Tasarımın iskeleti sağlam. İşaretli sıra ölçüsü, eşleşik plasebo farkı, kontrol simetrisi,
kör sıra ve tek koşu doğru kurulmuş. Bildirilen güç sayıları bağımsız tohumla yeniden üretildi (aşağıda D bölümü).

Ama taslak bu hâliyle dondurulursa koşunun **büyük olasılıkla ve pahalı biçimde "güç yok" ile bitme** riski var. Sert
durma noktalarının üçü (gün doluluğu kapısı, 4. adım, pozitif kontrol) ancak 1,66 TB indirildikten sonra çalışıyor.
Bunlardan ikisi ya ana sınavın kendisinden sert (4. adım) ya da doğru kodu düşürebilecek tanımsızlıklar taşıyor (PK).

**Dondurmadan önce** E1–E3 düzeltilmeli. Ö1–Ö9 güçlü öneridir. Küçük bulgular metin düzeltmesidir.

Koşu düzeni için net öneri:
1. **Aşama 0** (zorunlu, bulut oturumundan, 0 €, ≈ 50 000 istek, ≈ 6–7 saat; E1): sunucu kiralanmadan önce K₀ ve K_p₀
   üst sınırları bulunur. Geçmezse koşu açılmaz.
2. **Aşama P** (önerilen pilot, ≈ 0,12 TB, sunucuda ≈ 1 gün ya da bulutta birkaç oturum, ≤ 5 €; E1):
   - P1, ölçülen σ_Δ ile 4. adımın geçme olasılığını kestirir;
   - P2, listede olmayan olaylarda kosismik düşüşün görülüp görülmediğini sınar.
   İkisinde de olay verisine dokunulmaz.
3. **1b sıralı yapılır.** Önce olay ve plasebo istasyonları indirilir (≈ 0,25 TB). Olay tarafı kapıyı geçmezse kontroller
   hiç indirilmez.
4. **4. adımın ölçütü** ana sınavın kendi ölçütüne bağlanır (E2): −%0,1 eklenmiş sahte olayların r̄ aralığı 0,5'i
   dışlamalı. Bu, sertliği "AUC ≥ 0,75 iste" düzeyinden "ana testin saptayabildiği" düzeyine indirir.

## A. Engelleyici bulgular

### E1. Koşu düzeni, boşa gidecek 1,7 TB'yi önlemiyor: bütün kapılar ana indirmeden sonra (yazar noktası 2 ve 6)

- **Sorun.** §4.2'nin 0. adımı (K ≥ 20, K_p ≥ 10) 1b'nin sonunda, yani kontroller dahil bütün indirmeden sonra
  çalışıyor. 1a (kontrol ay yoklaması) zaten dalga formu okumayan bir HTTP kod ve bayt yoklaması. Yine de taslakta
  kapı kararı vermiyor ve sunucuda koşacak diye yazılmış. Üç bileşen ve aygıt kuralı da "1. aşamada" denetleniyor.
  Olay tarafındaki K kaybı (37 → 35 → 32 → ?) 1,66 TB indirildikten sonra öğreniliyor. 4. adım ve PK da ana indirmeden
  sonra.
- **Sayılar.**
  - Kontrol adaylarının yoklaması: ilk 10 kontrol ve ilk 10 plasebo kontrolünde 1175 tekil istasyon-penceresi var
    (taslakta 1264, tekrarlı sayım). Ayda bir istekle 42 300 istek. Merkez dağılımı: EarthScope 27 396, GEOFON 4176,
    GEONET 3132, NOA 3096, INGV 2340, ORFEUS 1800, SCEDC 1800, NCEDC 1332, öteki 432.
  - Ek 1'de ölçülen gecikmeler: EarthScope medyanı 0,38 sn, 0,3 sn bekleme. EarthScope akışı ≈ 27 400 × 0,68 sn ≈ 5,2
    saat sürer; ötekiler paralel akışta ≤ 1,5 saat.
  - Ek 1'in 13 792 isteği aynı betikle, önbellekli ve 2 saatlik iş sınırında yürüdü. Ek 2'de önbellekten tamamlandı.
  - Sonuç: bu iş **bulut oturumunda, 0 €'ya, 3–4 arka plan işiyle** yapılabilir.
- **Yatay bileşenler** dalga formu açılmadan iki yoldan denetlenebilir:
  - (i) İstasyon servisinden `level=channel` üstverisi (≈ 550 tekil istasyon, ≈ 550 istek). Bu, aygıt kuralını da üç
    bileşenle uygular.
  - (ii) Her istasyon-penceresinde A, B ve C dilimlerinin orta ayında, iki yatay bileşen için ayrı 1 dakikalık istek
    (yalnız HTTP kodu ve bayt). 1268 pencere × 6 ≈ 7600 istek.
  - Toplam ≈ 50 000 istek; EarthScope payı ≈ 32 000 × 0,68 sn ≈ 6 saat; duvar saati ≈ 6–7 saat. Aktarım ≈ 0,3 GB,
    saklanmaz.
- **Düzeltme (metin, §5.1'in başına):**

  > **Aşama 0 (sunucu kiralanmadan, bulut oturumundan, 0 €).** Dalga formu okunmaz. Yalnız HTTP kodu ve bayt sayısı
  > kaydedilir; yöntem ve nezaket kuralları TR-5 Ek 1 (`doluluk_yokla.py`) ile aynıdır. Bütün istek zamanları
  > ≤ 2023-12-31'dir. İş önbellekli ve kaldığı yerden sürdürülebilir; 2 saatlik iş sınırında yeniden başlatılır.
  > 1. **Üstveri.** Listedeki bütün istasyonlar (olay, plasebo, 10 kontrol, 10 plasebo kontrolü) için merkezin istasyon
  >    servisinden `level=channel` üstverisi alınır. §3.1'in kanal ve konum kodu seçimi yapılır: pencereyi tümüyle
  >    kapsayan üç bileşen. Seçilen kanalların üç bileşenine §2.5'in aygıt kuralı uygulanır. Kuralın aralığı olay
  >    istasyonları için [T − 1095, T + 30]'dur (E3c).
  > 2. **Ay yoklaması (1a).** 10 kontrol ve 10 plasebo kontrolü adayının bütün istasyon-pencerelerine, ayın 15'inde
  >    12:00–12:01 UTC, seçilen konum kodunun Z kanalı için istek atılır. Ay doluluğu süzgeci `dolu_ana`dır.
  > 3. **Yatay yoklama.** Olay, plasebo ve aday kontrol istasyon-pencerelerinde A, B ve C dilimlerinin orta ayında,
  >    seçilen iki yatay kanala ayrı ayrı 1 dakikalık istek atılır. Altı istekten biri boş dönerse pencere "üç bileşen
  >    yok" sayılır.
  > 4. **Sayım.** Pencere şu durumda dolu sayılır: üç bileşen var, aygıt kuralını geçiyor ve Z ay doluluğu `dolu_ana`.
  >    Kontrol, ≥ 1 dolu istasyonu varsa dolu sayılır. Bir olay ≥ 1 dolu istasyon ve SHA sırasında ≥ 4 dolu kontrol
  >    isterse geçer.
  >    - K₀: geçen olaylardan oluşan volkaniksiz kümelerin sayısıdır.
  >    - K_p₀: aynı şartla, eşleşik plasebo kümelerinin sayısıdır.
  >    - Kotaya yedekler de dahil edilir (Ö4).
  > 5. **Kapı G0.** K₀ < 20 ya da K_p₀ < 10 ise hüküm **"güç yok (aşama 0)"** olur. Sunucu kiralanmaz; dalga formu
  >    indirilmez. K₀ ve K_p₀ 1b'nin üst sınırıdır. Kayda §4.4'ün tablosu K₀ ve K_p₀ ile yeniden hesaplanarak yazılır.
  >
  > **1b sırası.** Önce olay ve plasebo istasyonları indirilir (≈ 0,25 TB). Bunlar bitince olay tarafı sayılır:
  > ≥ 1 gün-dolu istasyonu olan volkaniksiz küme sayısı ve eşleşik plasebo kümesi sayısı. Biri 20'nin ya da 10'un
  > altındaysa koşu "güç yok (1b, olay tarafı)" ile durur ve kontroller indirilmez.

- **Pilot (yazar noktası 2'nin üçüncü seçeneği).** Önerim: pilot yapılsın, ama körlüğü korumak için iki parçaya
  ayrılsın. P1 yalnız bağlayıcı listenin kontrol verisini okur. Bu veri koşuda zaten indirilecek. Pilotta yalnız
  önceden yazılmış bir durdurma kuralı işler; hiçbir parametre değişmez. P2 için listede **olmayan** olaylar
  kullanılmalıdır, çünkü PK zinciri olay istasyonunun [T − 60, T − 8] günlerini, yani hüküm penceresinin C dilimini
  okur. Tam metin:

  > **Aşama P (pilot; aşama 0 geçtikten ve kod incelemesinden sonra; ana indirmeden önce).** Ön kayıt, liste ve koşu
  > kodu aşama P'den önce dondurulur ve push edilir. Aşama P'nin sonucu hiçbir işleme parametresini, listeyi ya da
  > hüküm kuralını değiştiremez. Yalnız aşağıdaki iki durdurma kuralını işletir. Olay ve plasebo istasyonlarının
  > hiçbir verisi bu aşamada indirilmez.
  >
  > **P1 (σ_Δ, yalnız kontrol verisi).**
  > - Volkaniksiz olaylar (T, kimlik) sırasıyla alınır. Her birinin aşama 0'dan geçen ilk kontrolünün en yakın dolu
  >   istasyonu seçilir. İlk 24 olayın bu istasyon-pencereleri ([T − 1095, T − 8]) §3.1–3.5 ile işlenir. Bu
  >   pencereler bağlayıcı listenin sahte olay verisidir; koşuda yeniden indirilmez.
  > - σ̂_P1 = 1,4826 × MAD(istasyon Δ'ları), %.
  > - P̂₄ hesaplanır: `tr5b_guc.py`'nin duyarlılık benzetimiyle, σ_Δ = σ̂_P1, K = K₀, n_c = 5 ve 4. adımın ölçütü (E2)
  >   kullanılarak, 4. adımın geçme olasılığı.
  > - **P̂₄ < 0,50 ise hüküm "güç yok (pilot P1)" olur ve ana indirme yapılmaz.** Bu eşik, E2 ölçütüyle ve K 35'te
  >   σ̂ ≈ %0,25'e karşılık gelir.
  > - σ̂_P1 ve 24 Δ değeri kayda geçer. Δ'lar hiçbir olay ölçüsüyle karşılaştırılmaz.
  >
  > **P2 (kosismik düşüş, listede olmayan olaylar).**
  > - Aday olaylar: ComCat `type = earthquake`, M ≥ 6,0, derinlik ≤ 30 km, 2005-01-01 ile 2023-12-31 arası, TR-5b
  >   listesinde olmayanlar. TR-4 kutusu (40,0–41,6° K, 26,5–30,5° D) ve TR-1'in Marmara kutusu dışında kalmalıdır.
  > - İstasyon şartı: en yakın açık BH ya da HH üç bileşenli istasyon ≤ max(30 km, 2 L(M)) uzakta olmalı.
  >   Üstverisi [T − 400 g, T + 30 g] aralığını kesintisiz kapsamalı ve bu aralıkta §2.5 aygıt kuralını geçmeli.
  > - Örtüşme yasağı: istasyon, bu aralıkla örtüşen bir pencerede TR-5b listesinin hiçbir rolünde (olay, plasebo,
  >   kontrol 1–10, plasebo kontrolü 1–10) yer almamalıdır.
  > - Sıralama SHA-256(`pilot|{kimlik}`) değerine göre artandır. 300 km ve 1 yıl içindeki olaylardan yalnız sırada ilk
  >   geleni alınır. İlk 20 olay kullanılır. Olay başına yalnız en yakın istasyon alınır.
  > - Ölçüm: başvuru [T − 400, T − 8] geçerli günlük ÇİF'lerinin ortalamasıdır. δ_ko §4.2 adım 8 tanımıyla, E3'teki
  >   PK düzeltmeleriyle (enerji reddi medyanı, ızgara, aygıt) hesaplanır.
  > - [T − 400, T − 8] için δ_ko'dan başka hiçbir ölçü (düzey, eğilim, Δ) hesaplanmaz ve yazdırılmaz.
  > - Geçme şartı: ≥ 8 geçerli olay ve tek yanlı kesin Wilcoxon işaretli sıra testinde p ≤ 0,05 (H1: medyan
  >   δ_ko < 0). **Geçmezse hüküm "güç yok (pilot P2: yöntem kosismik düşüşü göstermedi)" olur ve ana indirme
  >   yapılmaz.**
  > - P2'nin olayları listede olmadığı için, P2 geçmezse yeni bir ön kayıt sürümü başka bir bant ya da parametreyle P2'yi
  >   yeniden deneyebilir. Bu, TR-5b'nin körlüğünü bozmaz. Her deneme kayda geçer.
  >
  > **Hacim ve maliyet.** P1 ≈ 24 × 1095 × 3,3 MB ≈ 87 GB; P2 ≈ 20 × 422 × 3,3 MB ≈ 28 GB. Toplam ≈ 0,12 TB, A'nın
  > ≈ %7'si, ve P1'in verisi ana koşuda yeniden kullanılır. Tek akışta ≈ 13 saat; sunucuda ≈ 1 gün (≈ 1–2 €) ya da
  > bulut oturumunda 2 saatlik ≈ 7–8 iş (0 €; akış hâlinde işlenir, disk 16 GB'ye sığar).

- **Gerekçe.** Pilotun ikisi de, ana indirmeden önce "güç yok"un en olası iki nedenini ölçer: gerçek σ_Δ ve kosismik
  düşüşün bu uzaklıklarda görülebilirliği. P1, sahte olay verisini erken işler. Bu veri olay Δ'sı hakkında bilgi
  taşımaz. Tek risk, pilot görüldükten sonra parametre değiştirme isteğidir; metin bunu kapatıyor. P2 olay
  istasyonlarının verisine hiç dokunmaz.

### E2. 4. adımın ölçütü, ana sınavın kendi duyarlılığından sert ve onunla tutarsız (yazar noktası 2)

- **Sorun.** 4. adım −%0,1 eklenmiş sahte olaylardan r̄_sahte ≤ 0,25 istiyor. Bu, tek biçimli bir kaymanın kontrollere
  karşı AUC ≳ 0,75 vermesi demektir; δ ≈ 1 σ_Δ. Oysa ana sınav, kendi H1 ölçütüyle (ana aralık) δ = 0,58 σ_Δ'yı 0,8
  güçle saptıyor. H0'ın kendisi de |δ| ≳ 0,55 σ_Δ'yı dışlıyor.
  - Örneğin σ_Δ = %0,15'te H0, %0,08'den büyük tek yönlü kaymaları dışlayacak kadar duyarlı. Aynı durumda 4. adım
    ölçüyü %0,1'e "kör" sayıyor ve 0,90 olasılıkla durduruyor.
  - Adım, sınavın saptayabildiği büyüklükteki bir kaymayı "kör" ilan ediyor.
- **Benzetim** (`guc_ek2.py`, tohum 99001, 20 000 yineleme, sahte olay 4 kontrole karşı, küme yapısı listeden):

  | σ_Δ | %0,075 | %0,1 | %0,15 | %0,2 | %0,3 |
  |---|---|---|---|---|---|
  | Taslak ölçütü, −%0,1, r̄ ≤ 0,25 (K 35) | 0,96 | 0,61 | 0,10 | 0,02 | 0,00 |
  | −%0,2, r̄ ≤ 0,25 (K 35) | 1,00 | 1,00 | 0,96 | 0,60 | 0,10 |
  | **Önerilen: −%0,1, %95 üst sınır < 0,5 (K 35)** | **1,00** | **1,00** | **0,90** | **0,67** | **0,37** |
  | Önerilen ölçüt, K 20 | 1,00 | 0,93 | 0,65 | 0,42 | 0,22 |

- **Üç seçeneğin değerlendirmesi.**
  - **−%0,2 ile sınamak.** Sertliği gevşetir, ama ölçeği Napa kosismik düşüşünün 2,5 katına çıkarır. Fiziksel anlamı
    zayıflar.
  - **Bilgi satırına indirmek.** Ölçüyü hiç denetlemez; kör bir ölçünün H0'ı yazılır.
  - **Önerim üçüncü yol:** −%0,1 kalır, ölçüt ana sınavın kendi ölçütü olur. Adım şu soruyu sorar: "Gerçek ÇİF'te
    bütün olaylara %0,1'lik bir son yıl düşüşü olsaydı, aynı test onu görür müydü?"
  - Taslağın ölçütü (≤ 0,25) bilgi olarak kalır ve H0 cümlesinin ölçeğini belirler.
- **Düzeltme (metin, §4.2 adım 4):**

  > 4. **Duyarlılık (ii-b).** 2. adımdaki −%0,1 eklenmiş sahte olaylar kalan kontrollere karşı puanlanır. r̄_sahte ve
  >    iki yanlı %95 t aralığı (df = K − 1) yazılır. **Aralığın üst sınırı 0,5'ten küçük değilse ölçü "kör" sayılır
  >    ve hüküm "güç yok" olur.** Bu, ana ölçünün −%0,1'lik tek biçimli bir son yıl kaymasını kendi ölçütüyle
  >    saptayamadığı anlamına gelir. Ayrıca r̄_sahte ≤ 0,25 olup olmadığı yazılır (S4).
  >    - S4 tutuyorsa H0 cümlesi "%0,1 ölçeğinde" diye yazılır.
  >    - Tutmuyorsa H0 cümlesi "yalnız σ_Δ ölçeğinde; dışlanan tek yönlü kayma ≈ 0,55 · σ̂_Δ = …%" diye yazılır.
  >      σ̂_Δ, kontrol Δ_c'lerinin 1,4826 × MAD'idir.
  >    - Geçme olasılığı (K 35): σ_Δ %0,075 / 0,1 / 0,15 / 0,2 / 0,3 için 1,00 / 1,00 / 0,90 / 0,67 / 0,37.

  §6.2'deki duyarlılık tablosu bu iki satırla değiştirilir. §9 madde 2 ve §11 (c) buna göre düzeltilir.

### E3. Pozitif kontrol zinciri, doğru kodu düşürebilecek dört açık taşıyor (yazar noktası 3)

PK'nin "güç yok" kuralı doğrudur. Ölçü bilinen bir kosismik düşüşü görmüyorsa H0 anlamsızdır, H1 de kuşkuludur.
Yalnız yön sınaması yapılması da doğrudur; genlik eşiği konmamalıdır. Ama zincirde doğru kodu düşüren dört açık var.
Bunlar 1,66 TB'nin sonunda, en son adımda devreye giriyor.

**E3a. Enerji reddinin medyanı PK penceresinde tanımsız.**
- §3.2'deki medyan "aynı istasyon-bileşen-pencerenin bütün saatleri"nden hesaplanıyor. [T + 1, T + 30] ayrı bir pencere
  mi, yoksa olay öncesi pencerenin medyanı mı kullanılıyor? Belli değil.
- Olay öncesi medyan kullanılırsa sonuç ağır olur. 0,5–2 Hz'te 30 km'deki bir M2,5'in 30 saniyelik kodası, bir saatin
  RMS'ini kabaca 5–10 kat büyütür (kaba ölçek hesabı, doğrulanamadı).
- M ≥ 7 kümelerinde ilk 30 günün gecelerinin çoğu bu yüzden atılır: Kahramanmaraş, Ridgecrest (ci38443183'ün PK
  penceresinde 2 gün sonra M7,1 var), Simeonof us7000asvb. Bu kümeler "geçersiz" olur. Oysa beklenen en büyük düşüş bu
  kümelerdedir: Kahramanmaraş için fay üstünde −%1,79'a kadar düşüş bildirildi (GJI 2023, 10.1093/gji/ggad242, özetten).
- Düzeltme: "PK penceresinde enerji reddinin medyanı [T + 1, T + 30] saatlerinin kendi medyanıdır. Reddedilen saat
  oranı istasyon başına yazılır (bilgi satırı 13)."

**E3b. ±%0,5 germe ızgarası büyük düşüşleri sansürlüyor.**
- Izgara kenarına düşen ε geçersiz sayılıyor. En büyük düşüşler PK'nin en güçlü kanıtıdır, ama ızgara onları veriden
  atar. Örnek: fay yakınındaki istasyonlar, MN.AQU 6 km, NC.KCT 10 km. Kahramanmaraş için bildirilen −%1,79 de ızgaranın
  dışındadır.
- Düzeltme: "PK'de (yalnız [T − 60, T + 30] yığınları için) germe ızgarası ±%2,0'dır (adım %0,001). Hüküm ölçüsünde
  ±%0,5 kalır."

**E3c. Aygıt kuralı PK penceresini kapsamıyor; listede kanıtlı bir örnek var.**
- §2.5 kuralı pencere "içinde" başlayan epoklara bakıyor. Pencere [T − 1095, T − 8].
- KO.BODT (us20009ynd, Bodrum-Kos M6,6, T = 2017-07-20; PK kümesi us20009ly0) için FDSN üstverisi şunu gösteriyor:
  sensör 2017-07-27'de, yani T + 7'de, CMG-3ESP'den CMG-3T'ye değişmiş. Önce kısa bir HHZ epoğu var, 2017-07-30'da yeni
  bir BHZ epoğu başlıyor.
- Bu istasyonun δ_ko'su iki ayrı sensörü karşılaştırır. Olay sonrasında ağların sensör değiştirmesi olağandır.
- Düzeltme: "§2.5 kuralı olay istasyonlarında [T − 1095, T + 30] aralığına uygulanır. Kuralı yalnız [T − 7, T + 30]
  aralığında bozan istasyon PK'den düşer, hüküm ölçüsünde kalır. Bilinen örnek: KO.BODT (us20009ynd)." Bu,
  `tr5b_liste.json`'a `aygit_degisimi_PK` alanı olarak eklenmelidir.

**E3d. E3'ün geçme olasılıkları tohuma çok duyarlı; bildirilen "≈ ±0,03" Monte Carlo saçılımı yanlış.**
- E3, A başına 200 yapay istasyonluk tek bir havuzdan 2000 çekiliş yapıyor. Çekilişler bağımsız değil; belirsizliği
  havuzun kendisi belirliyor.
- Bağımsız tohumla (777123) CC₁₀ ≈ 0,5'te:

  | A | Taslak (tohum 20261112) | Tohum 777123 | Tohumlar 11 / 22 / 33 / 44 |
  |---|---|---|---|
  | %0 | – | – | 0,055 / 0,054 / 0,093 / 0,042 |
  | %0,02 | 0,12 | **0,43** | 0,16 / 0,10 / 0,14 / 0,18 |
  | %0,05 | 0,63 | 0,63 | – |
  | %0,08 | **0,90** | **0,74** | 0,79 / 0,81 / 0,70 / 0,81 |
  | %0,15 | 1,00 | 1,00 | – |

  Okuma: altı havuzda (taslak, 777123 ve dört tohum) A = %0,08 için geçme olasılığı 0,70–0,90 arasında, ortası ≈ 0,78; taslağın 0,90'ı üst uçta. A = %0,02 için 0,10–0,43 aralığında. Havuzlar arası saçılım ≈ ±0,1–0,15, yani taslağın ±0,03'ünün 3–5 katı. A = 0'da (düşüş yok) yanlış geçme bir havuzda 0,093, yani tek yanlı %5 düzeyini aşıyor. Bunun nedeni küçük havuzda mevsim evrelerinin rastlantısal dengesizliği; testin kendisi değil, ama E3'ün raporladığı sayıların havuza bağlı olduğunu gösteriyor. "Napa düzeyinde 0,9–0,99" cümlesi "≈ 0,7–0,9 (CC₁₀ 0,5) / ≈ 0,98 (CC₁₀ 0,7)" olarak düzeltilmeli.
- Düzeltme (metin, §6.1 E3):

  > E3 en az 5 bağımsız havuzla (tohum) ve havuz başına ≥ 1000 yapay istasyonla yeniden koşulur. Tabloya
  > havuzlar arası ortalama ve [en küçük; en büyük] yazılır. A = 0 satırı eklenir (yanlış geçme olasılığı; ≤ 0,05
  > olmalı). Gerçek mevsim genliği %0,1 (Hillers 2015) için ikinci bir satır eklenir.

  Ayrıca (E3a–c'nin yanında) PK ölçüsü küçük bir değişiklikle güçlenir:

  > PK'de olay δ_ko'su, olayın **en yakın geçerli istasyonunun** δ_ko'sudur (istasyon ortalaması değil). Küme δ_ko'su
  > kümedeki olay δ_ko'larının ortalamasıdır.

  Gerekçe: düşüş uzaklıkla sönüyor ve 50 km ötesinde sıfıra inebiliyor (Boschelli 2021). PK kümelerinde en yakın
  istasyon ile öteki istasyonlar arasında büyük fark var: BK.CVS 19 km ile BK.VAK 38 km; NC.KCT 10 km ile BK.JCC 53 km;
  HL.SMTH 24 km ile HL.LIA 47 km. Ortalama, sinyali sulandırır.

**E3e. Etiket.** PK geçmediğinde ana ölçü H1 şartlarını sağlıyorsa "güç yok" değil, **"ayırt edilemez (PK geçmedi)"**
yazılmalıdır. Ölçü bir şey görmüş, ama bilinen etkiyi görmediği için bu kanıt değildir. Metin (§4.2 adım 8 sonu):
"Geçmezse ya da geçerli küme < 8 ise: 9. adımın H1 şartları sağlanıyorsa hüküm 'ayırt edilemez (PK geçmedi)',
sağlanmıyorsa 'güç yok (yöntem bilinen kosismik düşüşü göstermedi)' olur."

**Geçerli PK küme sayısı riski.** 16 PK kümesinden:
- us7000irfb'nin tek istasyonu (IU.HNR) aygıt kuralında düşüyor;
- usb000m8ch'nin en yakın istasyonu (HL.VLS, 12 km) düşüyor; kalan HT.LKD2 67 km'de;
- KO.BODT PK'den düşüyor (E3c).
E3a düzeltilmezse M ≥ 7 kümeleri de düşer. ≥ 8 şartı tutar, ama payı küçüktür. E3a–c bu yüzden engelleyicidir.

## B. Önemli bulgular

### Ö1. Ölçünün geçerlilik şartı ile doluluk kuralı uyuşmuyor; K, 0. adımdan sonra sessizce küçülebilir

- **Sorun.**
  - 1b'de istasyon-penceresi "A, B ve C'nin her birinde gün doluluğu ≥ 0,60" ile dolu sayılıyor.
  - Δ ise ≥ 9 eşleşen takvim ayı istiyor ve her ay için hem C'de hem A∪B'de ≥ 10 geçerli ε günü.
  - Ay doluluğu süzgeci (`dolu_ana`) 3 aylık boşluğa izin veriyor. C'de 3 aylık bir boşluk ve maske (60 gün) ile ≥ 9
    eşleşen ay şartı tutmayabilir. Örnek: TU.ANDN'nin C diliminde 60 maske günü var (2022-10-11 M5,0).
  - Böyle bir istasyon 0. adımda K'ye sayılır, 6. adımda Δ'sı geçersiz çıkar.
  - 6. adımda K'nin yeniden sayılması ve K < 20 için bir kural yok.
- **Düzeltme (metin).**
  - §5.1 1b, "İstasyon-penceresi dolu" maddesine eklenir: "…ve ≥ 9 takvim ayında hem C'de hem A∪B'de ≥ 10 gün için yığın
    şartı (son 10 günde ≥ 5 dolu ve maskesiz gün) sağlanıyor. Bu, ε'nin CC dışındaki geçerlilik şartıdır ve ε
    hesaplanmadan sayılır."
  - "Dolu gün oranının paydası, dilimin maskesiz günleridir."
  - §4.2'ye 6. adımın başına eklenir: "6a. Geçerli Δ_e'si ve ≥ 3 geçerli kontrolü olan volkaniksiz küme sayısı K₆
    sayılır; yalnız sayı yazılır. K₆ < 20 ise hüküm 'güç yok (ε geçerliliği)' olur. t aralığı df = K₆ − 1 ile
    hesaplanır. Plasebo için de K_p6 < 10 ise H1 ilan edilemez."

### Ö2. "Koşu öncesi düzeltme" kapısı, 2–4. adımlar için sınırsız yeniden deneme bırakıyor

- **Sorun.** §5.5'e göre kod hatası 1–4. adımlarda bulunursa düzeltilir. Ama 2. ve 4. adımlar hem kod hem güç
  denetimidir. 4. adım geçmezse "kod hatası" bulup yeniden koşmak, kontrol verisine bakarak parametre ayarlamaya açık
  bir yoldur (ör. CC eşiği, bant kenarı). Bu, ana ölçüyü görmeden yapılsa da sınavın gücünü veri görüldükten sonra
  ayarlamaktır.
- **Düzeltme (metin, §5.5):**

  > Koşu öncesi düzeltme yalnız şu durumda yapılır: hata, gerçek veri kullanılmadan, yapay veriyle yeniden üretilebilen
  > bir kod hatasıdır ve yeni bir yapay sınamayla gösterilir. §3'teki hiçbir sayısal parametre (bant, pencereler,
  > eşikler, ızgara, yığın, maske) değiştirilemez. Düzeltmeden sonra 1–4. adımların hepsi baştan koşulur. Önceki
  > sonuçlar silinmez, kayda geçer. 3. ya da 4. adım iki kez başarısız olursa hüküm kesinleşir ("geçersiz" ya da
  > "güç yok").

### Ö3. Volkanik kural olaylara uygulanıyor, kontrollere uygulanmıyor (yazar noktası 8)

- **Sorun.** Hawaii olayları "dv/v magma basıncıyla oynar" gerekçesiyle ana hükümden çıkarılmış. Ama Hawaii ve İzlanda
  merkezleri kontrol olarak duruyor.
  - **hv70116556**: 2018 Leilani'nin kendisi; istasyonları HV.BYL, KKO, HAT, ya da JCUZ, STCD, PAUD (Kīlauea doğu
    rifti).
  - **hv19832953**: 1983 Kaoiki; HV.WRM, SDH, OBL, UWE, AIND, MLOD (Kīlauea zirvesi ve Mauna Loa).
  - **hv5532127**: Kona; PT.HPAH, KHLU, IU.POHA.
  - **usp0009urh**: Güney İzlanda; VI.GOD, II.BORG, OR.*.
- **Sayım.** Volkaniksiz olayların ilk 5 kontrolünde Hawaii 4, İzlanda 3 yuva var. Plasebo ilk 5'lerinde Hawaii 7,
  İzlanda 1. Yedeklerle birlikte 27 yuva.
  - Örnekler: usp000jr55'in 1. kontrolü (Jan Mayen olayı); us100031wx'in 1. kontrolü; us20005i1a'nın 1. plasebo
    kontrolü. 1. kontroller sahte olaydır.
  - Kīlauea 2008–2018 boyunca zirve lav gölü ve 2011 ile 2014 rift olaylarıyla etkindi. Bu kontrollerin Δ_c'si magma
    kaynaklı olabilir.
- **Etkisi.** Kontrol dağılımını genişletir ve H0'a doğru iter. Sahte olay Hawaii'deyse N1 ve 4. adımı bozar.
- **Düzeltme (metin, §2.3'e (f) şartı).**

  > (f) Volkanik dışlama, olay ve kontrollere simetrik uygulanır. İstasyonlarından biri bir Holosen volkanının
  > (Smithsonian GVP listesi, dondurmadan önce indirilip sha256'sı kayda geçer) 25 km içinde olan olay, plasebo ya da
  > kontrol merkezi:
  > - olaylarda ana hükümden çıkarılır, ayrı bilgi satırına gider;
  > - kontrollerde atlanır ve yerine sıradaki merkez gelir.
  > Kural `tr5b_liste.py`'de kodlanır ve liste yeniden üretilir. GVP listesi alınamazsa en azından ad kuralı
  > kontrollere de uygulanır: Hawaii adasındaki merkezler (hv70116556, hv19832953, hv5532127) kontrol olamaz.

  Ad kuralı (§2.7) bu durumda GVP kuralının sonucu olarak yeniden yazılır. Akutan ve Jan Mayen otomatik olarak ya
  içeri girer ya dışarıda kalır. Bu değişiklik dv/v verisi görülmeden yapılır ve K'ye etkisi kayda geçer.

### Ö4. Kota yedeklerde aşılıyor; bağımsızlık istasyon düzeyinde de bozuluyor

- **Sorun.**
  - `kontrol_kota` kotaya yalnız ilk 5'i yazıyor (`sec[:N_KONTROL]`). Koşuda dolu olmayan kontrolün yerine 6–10.
    sıradaki yedekler geliyor. İlk 10 sayıldığında bir merkez **9 kümede** görünüyor ve 52 merkez 3 kümeyi aşıyor.
  - Kota merkez başına, ama veri birimi istasyondur. Birbirine 25–200 km uzaklıktaki merkezler aynı istasyonları
    paylaşıyor. İlk 5'lerdeki 202 tekil kontrol istasyonunun 11'i 3'ten fazla kümede, biri 6 kümede.
  - Aynı olayın iki kontrolü bir istasyonu paylaşıyor: us7000imgl, MM.KTN. (e) şartı 150 km, ama yarıçap 100 km (TR-1
    inceleme 2, bulgu 7.2 ile aynı açık).
- **Düzeltme (metin, §2.3 Kota ve (e)).**

  > **Kota.** Bir kontrol **istasyonu**, aynı epok türünde en çok 3 bağımsızlık kümesinin kontrolünde kullanılır.
  > Kota, kontrolün koşuda kullanılıp kullanılmadığına göre işler; yedekler de dahildir. Olaylar (T, kimlik) sırasıyla
  > işlenir. Yedek seçiminde kotası dolmuş istasyonu içeren merkez atlanır. Aşama 0, kotayı yedeklerle birlikte
  > uygulayarak K₀'ı sayar.
  >
  > **(e).** Seçilen kontrollerin merkezleri birbirinden ≥ 200 km uzaktır ve aynı olayın kontrolleri ortak istasyon
  > içermez.

  Kota istasyon düzeyine alınırsa liste yeniden üretilmeli ve K'ye etkisi yazılmalıdır.

### Ö5. Plasebo, 5 olayda "aynı yer" değil (eşleşik farkın tanımı da eksik)

- **Sorun.** Plasebo istasyonları [T − 6 yıl, T − 1 g] kapsamına göre yeniden seçiliyor. 23 plasebolu volkaniksiz
  olaydan 18'inde istasyon kümesi aynı, 4'ünde kısmen aynı, 1'inde tümüyle farklı: usb000r2hc'de olay HL.LIA ve
  HL.SMTH, plasebo HT.ALN. HT.ALN ayrıca TR-1'in geniş kutusundaki tek istasyondur (§5.5).
  - Plaseboyla yakalanmak istenen "yere özgü yanlılık" istasyona özgüdür: sensör, yerleşim, yerel hidroloji.
    Farklı istasyonla yapılan d karşılaştırması bunu ölçmez.
  - d = r_e − r_p küme düzeyinde tanımsız: kümede plasebosu olmayan olaylar var mı, r_e hangi olaylardan alınıyor?
- **Düzeltme (metin, §2.4 ve §3.6).**

  > Plasebo Δ_p yalnız olayın da istasyonu olan istasyonlarla hesaplanır (kesişim). Kesişim boşsa olay plasebodan düşer.
  > Eşleşik fark küme başına d_k = ort(r_e) − ort(r_p) olarak hesaplanır. İki ortalama da kümenin **hem geçerli r_e'si
  > hem geçerli r_p'si olan** olayları üstündendir. d̄ ve tek yanlı %95 t sınırı df = K_p − 1 ile hesaplanır. K_p,
  > eşleşik volkaniksiz küme sayısıdır.

  Bu kuralla usb000r2hc plasebodan düşer. Eşleşik plasebo kümesi üstveride 18'den 17'ye iner. Güç değişimi küçük:
  δ = 0,75'te tam H1 0,54'ten 0,52'ye (`guc_ek.py`).

### Ö6. Hidroloji: kontrol eşlemesi değil, hüküm kalıbında zorunlu uyarı (yazar noktası 5)

- **Değerlendirme.**
  - İklim ya da uzaklık eşlemesi (enlem kuşağı, Köppen sınıfı) yerel çok yıllı kuraklığı eşlemez. Mevsimsel kısmı
    zaten ay eşlemesi düşürüyor. Eşleme yalnız kontrol havuzunu daraltır ve yeni bir serbestlik derecesi getirir.
  - Feng 2021 (10.1029/2021jb022650; SC, Tayvan, 15 istasyon, 1998–2019) mevsimselliği yağışla oluşan gözenek basıncına
    bağlıyor (özetten). Bu, SC yönteminin hidrolojiye birincil duyarlılığını doğruluyor.
  - Taslağın "en büyük risk" yargısı doğru.
- **Önerim.** Kontrol seçimi değişmesin. Hüküm kalıbına zorunlu bir cümle girsin. Var olan zaman kaydırma satırı
  (r̄_kay) bu riskin tek veri temelli göstergesi olarak hüküm metnine bağlansın.
- **Düzeltme (metin, §4.3 H1):**

  > H1 metnine her durumda şu cümle eklenir: "Bu fark, olay yerlerinde son yılı önceki iki yıldan farklı geçen yerel
  > çok yıllı hidrolojiden (kuraklık ya da yeniden beslenme) ayrılmadı. Kontroller yerel iklimi eşlemez, plasebo
  > yalnız yere özgü kalıcı yanlılığı yakalar. Bu açıklama, yağış ya da yeraltı suyu verisiyle yapılacak ayrı bir ön
  > kayıtla dışlanmadıkça H1 öncül kanıtı sayılmaz." r̄_kay aynı yönde 0,5'i dışlıyorsa (§4.2 adım 9) ek not
  > "son yıla özgü değil; hidroloji ya da yer eğilimiyle uyumlu" olur.

  Yağış modeli bilgi satırı olarak bile istenmiyorsa bu karar doğrudur, ama gerekçesi (serbestlik derecesi) §7'de
  kalmalıdır.

### Ö7. Tek istasyon SC'nin gördüğü yer: dış merkez değil, istasyonun çevresi (yazar noktası 7)

- **Sorun.**
  - Volkaniksiz 43 olayın 34'ünde (%79) tek istasyon var. Olay istasyonlarının dış merkeze uzaklığı: medyan 50 km;
    en yakın istasyonun medyanı 55 km.
  - Tek istasyon bileşenler arası ÇİF'in koda duyarlılığı istasyonun çevresinde yoğunlaşır. 0,5–2 Hz ve 10–40 sn
    gecikmede bu, kabaca istasyonun birkaç km ile birkaç on km yarıçapı ve üst birkaç km demektir. Obermann 2016
    (10.1093/gji/ggw264, özetten) derinlik duyarlılığının gecikmeyle cisim dalgalarına kaydığını gösteriyor;
    sayısal derinlik doğrulanamadı.
  - Ölçü fay hazırlık bölgesini değil, ondan ortanca 50 km uzaktaki sığ ortamı örnekler. Hobiger 2016 (10.1093/gji/
    ggw066) ve 2014: kosismik düşüşler fay yakınında en büyük. Taslak §1'de "üst birkaç km" yazıyor, "istasyon
    çevresi" yazmıyor.
- **Düzeltme (metin, §1 "Ölçü ne görür" ve §4.3 H0):**

  > Ölçü, istasyonun çevresindeki sığ ortamı örnekler. Bu, istasyonun kabaca birkaç km ile birkaç on km yarıçapı ve üst
  > birkaç km'sidir (yarıçap ve derinlik doğrulanamadı). Olay istasyonları dış merkeze ortanca 50 km uzaktadır. H0,
  > "dış merkezden ortanca 50 km uzaktaki sığ ortamda yıl ölçekli düzey değişimi yok" demektir. Fay bölgesindeki ya da
  > derindeki bir hazırlık sürecini kapatmaz. Bilgi satırı 9 (≤ 50 km) bu yüzden H0 metninde K'siyle birlikte anılır.

- **Ek (güç).** Olay Δ'sı çoğunlukla tek istasyondan gelir. Kontrol Δ_c ise ilk 5'lerde 1 / 2 / 3 istasyonun ortalaması
  (110 / 37 / 68 kontrol). §4.4'teki δ ve σ_Δ birimi bu yüzden tanımsız. Önerim: "σ_Δ, kontrol Δ_c'lerinin sd'sidir.
  Bilgi satırı 15, istasyon düzeyi ve kontrol düzeyi σ̂'yı ayrı yazar." Olay Δ'sı kontrollerden 1,5 kat gürültülüyse
  tam H1 gücü δ = 0,75'te 0,54'ten 0,31'e iner (`guc_ek.py`). Bu, §4.4'e bir satır olarak eklenmeli.

### Ö8. Öncü etkinliği, "düşüş" yönünde bir rakip açıklama; maske bunu yarım kapatıyor

- **Sorun.** Maske günleri C diliminde olaylarda kontrollerden fazla:
  - C'de maskesi olan istasyon oranı: olay 0,16, kontrol 0,09;
  - C'deki ortalama maske günü: olay 9,9, kontrol 5,4 (A∪B'de olay 12,2, kontrol 8,7).
  - Fark ağırlıkla Kahramanmaraş (TU.ANDN, 2022-10-11 M5,0), Lesvos (HL.PRK, Şubat 2017 M5,2–5,3 serisi), Petrolia
    ve Ferndale (NC.KCT, KMPB) ile Zagreb (CR.ZAG) kaynaklı.
  - Maske yalnız ≤ 50 km ve M ≥ 5 olaylarını siliyor. Büyük depremlerden önce artan M 4–5 etkinliğinin ve 50–150
    km'deki M5'lerin küçük kosismik düşüşleri C'de kalır. Bunlar Δ_e'yi aşağı iter.
  - Bu, "düşüş yönünde H1" için deprem etkinliği kaynaklı bir rakip açıklamadır. Etkinlik artışı öncül sayılabilir,
    ama dv/v öncülü değildir.
- **Düzeltme (metin, §8'e bilgi satırı 16 ve §4.3).**

  > 16. C diliminde istasyonun 150 km içinde M ≥ 5,0 (derinlik ≤ 70 km) olayı olan olaylar dışarıda bırakılarak r̄.
  > Aynı kural kontrollere de uygulanır.
  >
  > H1 düşüş yönündeyse ve 16. satırda 0,5'i aynı yönde dışlamıyorsa H1 metnine şu not eklenir: "Etki, öncü deprem
  > etkinliğinin kosismik etkisinden ayrılmadı."

### Ö9. Kod denetimi (i)'nin toleransı Monte Carlo saçılımı düzeyinde

- **Sorun.** 1. adım, koşu kodunun E1 ve E2'yi "aynı tohumla yeniden üretmesini" ve oran_medyan'ın ±0,01 içinde
  kalmasını istiyor.
  - Bağımsız tohumla oran_medyan CC₁₀ ≈ 0,5'te 0,935 çıktı (taslak 0,927). Fark 0,008, yani toleransın %80'i.
  - Yapay ÇİF'leri kendi üreteciyle (farklı RNG tüketim sırasıyla) üreten doğru bir bağımsız uygulama 1. adımda
    "geçersiz (kod)" alabilir.
  - Tersinden, aynı üreteci çağıran bir koşu kodu da işlem zincirini değil yalnız üreteci sınamış olur.
- **Düzeltme (metin, §4.2 adım 1).**

  > `tr5b_yapay.py`, E1/E2'nin yapay günlük ÇİF dizilerini (üç SNR düzeyi × 120 tekrar; özgün ve −%0,1 eklenmiş)
  > `tr5b_yapay_ccf.npz` dosyasına yazar. Dosyanın sha256'sı ön kayda geçer. Koşu kodu bu dizileri okur ve kendi
  > zinciriyle (§3.4–3.5) işler. Her dizide Δ ve oran, başvurudaki değerden en çok %0,0005 (Δ) ve 0,005 (oran) sapar.
  > Toplam sapma bu sınırı aşan dizi sayısı > 0 ise hüküm "geçersiz (kod)" olur.

  Dosya boyutu: 3 × 120 × 2 × 1095 × 2401 × 4 bayt ≈ 7,6 GB; bu fazla büyük. 3 SNR × 20 tekrarla ≈ 1,3 GB, float16 ile
  ≈ 0,6 GB yeter (tolerans buna göre aynı kalır).

## C. Küçük bulgular

### K1. Çatallanma beyanı yeterli; bir cümle ve bir bilgi satırı eklenmeli (yazar noktası 1)

Seçim yalnız K ve plasebo sayıları üstünden yapıldı. Hiçbir sonuç ölçüsü görülmedi; beyan dürüst ve yeterli.
"Ana tasarımın K 8–15'lik alt kümesi zorunlu ikinci hüküm satırı" önerilmez: K < 20'de güç kapısı her durumda "güç yok"
verir ve ikinci hüküm satırı çoklu sınama getirir. Önerilen metin (§0 sonu):

> TR-5b'de Ek 1'in 16 satırından başka hiçbir biçim koşulmaz ya da raporlanmaz. Ana tasarıma en yakın alt küme bilgi
> satırı olarak her durumda raporlanır ve hüküm vermez: "M ≥ 6,5 ve ≥ 2 dolu yerli olaylar". Satıra küme sayısı ve
> r̄ yazılır. (§8'e 17. satır.)

### K2. H0 eşdeğerlik sınırının gerekçesi yazılmamış

[0,35; 0,65], |δ| ≈ 0,55 σ_Δ'ya karşılık geliyor. K 35 ve δ = 0'da P(H0) = 0,65; K 20'de 0,19. Sayılar doğrulandı.
Eklenecek metin (§4.2 adım 9 H0):

> Sınır ±0,15 AUC'dir (|δ| ≈ 0,55 σ_Δ). Bu değer, K 35'te etki yokken H0 alma olasılığının ≥ 0,6 olması için
> seçildi. Daha dar bir sınır (±0,10) bu olasılığı ≈ 0,2'ye indirirdi. H0 cümlesinin yüzde karşılığı σ̂_Δ ile
> otomatik yazılır (E2).

±0,10 için ≈ 0,2 kaba bir kestirimdir; dondurmadan önce `tr5b_guc.py` ile hesaplanıp yazılmalıdır.

### K3. Gün tanımı ve UTC gece penceresi

Yerel gece penceresi doğu boylamlarında UTC gece yarısını aşar. Örnek: 30° D için UTC 22:00–02:00.
- "İstasyon-gün d" tanımı yok. Maske, T − 8 ve T + 1 sınırları UTC tarihle tanımlı.
- Metin: "Gün d, istasyonun yerel ortalama güneş tarihidir. Penceresi, UTC olarak [d 00:00 − boylam/15 saat]
  başlangıçlıdır, tam saate yuvarlanır. T, maske ve dilim sınırları bu tarihle karşılaştırılır. PK'nin ilk günü, ana
  şok zamanından sonra başlayan ilk tam penceredir."

### K4. Konum kodu seçimi doluluk yoklamasıyla uyuşmuyor

- Ek 1 yoklaması `loc=*` ile yapıldı. §3.1 ise "`''`, `00`, `10`, sonra alfabetik" sırasında ilk konum kodunu seçiyor.
- IU ve II istasyonlarında konum kodu pencere içinde değişebilir. Bu durumda seçilen kodun verisi pencerenin bir
  kısmında yoktur.
- Metin: "Kanal ve konum kodu, pencereyi üstveride tümüyle kapsayan üç bileşenli kodlar arasından bu sırayla
  seçilir. Aşama 0 yoklaması seçilen konum koduyla yapılır."

### K5. Kontrol merkezlerinin geçmişi kontrollerde daha "yaralı"

[T − 15 yıl, T − 5 yıl) içinde 150 km'de M ≥ 6,5 olan yerlerin oranı:
- kontrol merkezlerinde (ilk 5) **0,48**;
- olay dış merkezlerinde 0,28.

Kontrol merkezleri tanım gereği M ≥ 6,5 dış merkezleri. Kontrollerin %85'inde merkezin kendi olayı T − 5 yıldan önce,
%18'inde [T − 10, T − 5) içinde. Hobiger 2016'ya göre kosismik düşüşlerin yarısı yıllarca toparlanmıyor; toparlanan
kısmın süresi ≈ 0,55 yıl. Bu yüzden 5 yıldan sonraki toparlanma eğimi muhtemelen çok küçüktür.

Yön: kontrol Δ_c > 0, yani olaylar "düşüş" görünür. Plasebo kontrolleri aynı kuralla seçildiği için d'de büyük ölçüde
düşer. Metin (§7 tablosuna satır):

> "Kontrol merkezlerinde eski büyük depremden toparlanma (5–15 yıl önce M ≥ 6,5: kontrol %48, olay %28) | eşleşik d;
> bilgi satırı 18: [T − 15 yıl, T − 5 yıl) içinde 150 km'de M ≥ 6,5 olmayan kontrollerle r̄ | küçük, yönü düşüş"

### K6. Saat hatası ve aygıt

SC tek istasyonun bileşenlerini ilişkilendirdiği için **saat hatalarına duyarsızdır**. Bu bir güçlüdür ve §7'ye
yazılmalı. Kutup ya da bileşen değişimi (N↔E, işaret dönmesi) CC'yi düşürür ve günleri geçersiz kılar, yanlılık
üretmez. Üstveriye işlenmemiş sensör değişimi kalan risktir.

İstasyon düzeyinde M ≥ 6 kirlenmesi de denetlendi. Pencere başı − 2 yıl ile T − 8 arasında, istasyonun 50 km içinde
M ≥ 6 olayı olan olay ya da kontrol istasyonu yok. 75 km içinde yalnız NO.JMIC var (2011 M6,2, 67 km). §7'deki "Ş1
merkeze göre" kaygısı bu listede gerçekleşmiyor.

### K7. Tanımsız ya da eksik paydalar

1. **2. adım oranı.** "Sahte olay istasyonlarının medyan oranı": bütün sahte olayların geçerli istasyonları üstünden
   havuzlanmış medyan mı? Metin: "…bütün sahte olayların, Δ'sı hem özgün hem eklenmiş durumda geçerli olan
   istasyonları üstünden havuzlanmış medyan."
2. **0. adım.** "≥ 4 dolu kontrol" ile 4.1'deki "n_c ≥ 3 geçerli" aynı şey değil. Metin: "Olay, 6. adımda ≥ 3 geçerli
   kontrol ister; 0. adımdaki ≥ 4 dolu kontrol bunun önkoşuludur."
3. **K_p.** "Eşleşik" sözcüğü volkaniksiz kümeler için mi? Metin: "K_p, volkaniksiz ve K'de sayılan kümelerden ≥ 1
   plasebo olayı geçerli olanların sayısıdır."
4. **Hacim.** §5.2'de A'nın bileşenlerinin toplamı (0,17 + 0,08 + 1,08 + 0,71 = 2,04 TB), A'nın toplamından (1,66 TB)
   büyük. Bileşenler ayrı ayrı hesaplanmış, birleşimde örtüşme düşüyor. "Tekrarsız" sözcüğü yanıltıcı; "her biri ayrı
   birleşim; örtüşme ≈ 0,38 TB" yazılmalı.

### K8. Süre tahmininde istek yükü

A'da ≈ 505 bin istasyon-gün penceresi var; EarthScope payı ≈ 285 bin istek. 0,3 sn bekleme ≈ 1 gün ekler. 2,4 MB/s
ölçümü 2 MB'lık tek bir istekte alınmıştı; istek başı gecikme bu hıza dahil. EarthScope kalemi ≈ 4,5 gün yerine
≈ 5,5 gün sürer. Toplam "1–2 hafta" içinde kalır.

Metin (§5.3): "EarthScope istekleri POST ile istasyon başına 30 günlük paketler hâlinde atılır; 0,3 sn bekleme paket
başınadır."

### K9. 2020 kültürel gürültü kesintisi

Mart–Haziran 2020'de 1–20 Hz kültürel gürültü düştü (yaygın bilinen, bu oturumda doğrulanmadı). C dilimi bu döneme
düşen olaylar ve kontroller aynı epokta olduğundan etki kısmen ortaktır. Ama kentsel ve kırsal yerlerde farklıdır;
kaynak değişimi germede sahte dv/v üretebilir. Gece penceresi bunu azaltır. İsteğe bağlı bilgi satırı: "C'si
2020-03-01 ile 2020-06-30 arasıyla örtüşen olaylar hariç r̄."

### K10. Literatür denetimi (yazar noktası 9)

`oa.py` ile özetler okundu. Aranan tek istasyon dv/v çalışmalarının özetlerinde 10 günlük yığın, CC eşiği, koda
penceresi ya da günlük saat sayısı yok. Bu parametreler **doğrulanamadı** olarak kalır. Viens 2018 ve Yates 2019 adla
bulunamadı. Bulunan ve ilgili olanlar:

| İş | Özetten | İlgisi |
|---|---|---|
| De Plaen 2016 (10.1002/2016gl070078) | SC, 1–2 Hz'te volkan izlemede çapraz istasyon kadar iyi; istasyonlar püskürme yerine ≤ 3,5 km | 0,5–2 Hz SC'yi destekliyor; ama yakın kaynak |
| Feng 2021 (10.1029/2021jb022650) | SC, 0,1–0,9 Hz, germe, 15 BATS istasyonu, 1998–2019; yağışla gözenek basıncı mevsimselliğe baskın | SC'nin hidrolojiye duyarlılığı (Ö6). Büyük SC çalışması daha düşük bant kullanıyor |
| Yates 2018 (10.1029/2018gl080580) | Tek istasyonlarla volkanik, kosismik ve mevsimsel değişimler; uzak istasyonlarla ayrıştırma | Kontrol mantığını destekliyor |
| Hobiger 2016 (10.1093/gji/ggw066) | SC ve CC; düşüş frekansla artıyor, fay yakınında en büyük; düşüşlerin ≈ yarısı toparlanmıyor; toparlanma süresi ≈ 0,55 yıl | PK ve K5 |
| GJI 2023 (10.1093/gji/ggad242) | Kahramanmaraş: fay üstünde −%1,79'a kadar; 0,5 Hz üstünde yakın yerlerde daha büyük | E3b (±%0,5 ızgarası) |
| Obermann 2016 (10.1093/gji/ggw264) | Koda derinlik duyarlılığı gecikmeyle değişiyor (yüzey + cisim dalgası karışımı) | Ö7 |

Makul aralığın dışında kalan tek parametre **PK için ±%0,5 germe ızgarası** (E3b). Öteki değerler için yorumlar:
- CC ≥ 0,40: yaygın kullanılan eşiklerin alt ucunda. Yapay veride sorun çıkmadı.
- 4 saat/gün: alışılmadık; ölçüm gürültüsünü ≈ 2,4 kat büyütür. Ama gerçek σ_Δ'ya çevresel bileşenin baskın olması
  beklenir.
- 10 günlük yığın ve 10–40 sn koda: alışılmış değerler.

Bu yorumlar bellekten ve doğrulanamadı; hiçbiri kendi başına düzeltme gerektirmiyor.

### K11. Taslağın başvurusu son yılı içeriyor: sorun değil

Başvuru [T − 1095, T − 8] ortalaması ve C'yi içeriyor. Doğrusal yaklaşımda ε'lar ortak bir sabitle kayar; Δ = C − A∪B
farkında bu sabit düşer. E2 bunu doğruluyor: eklenen −%0,1'in %93–98'i geri ölçülüyor. Bağımsız tohumla oranlar
0,935 / 0,968 / 0,985. Bastırma yok. Çok büyük değişimlerde (≳ %0,5) başvurunun bulanıklaşması CC'yi düşürür; bu
yalnız PK'yi ilgilendirir (E3b).

### K12. Volkan yapısı satırı ve Hawaii

Ö3 kabul edilirse §2.7 ve §8'in 1. ve 2. satırları GVP kuralının çıktısıyla yeniden yazılır. Kabul edilmezse, en
azından Hawaii kontrol merkezlerinin dışlanması §0'daki "bu taslakta verilen kararlar" listesine eklenmelidir.

## D. Yeniden üretim (bağımsız tohum)

| Sayı | Taslak | Bağımsız (tohum 777123) |
|---|---|---|
| H1 / H0 / ayırt edilemez, δ = 0 | 0,014 / 0,654 / 0,332 | 0,015 / 0,651 / 0,335 |
| H1, δ = 0,5 / 0,75 / 1,0 | 0,287 / 0,540 / 0,754 | 0,282 / 0,551 / 0,754 |
| Yalnız ana aralık, δ = 0 / 0,5 / 0,75 | 0,048 / 0,679 / 0,950 | 0,051 / 0,679 / 0,954 |
| 0,8 güçte en küçük δ: ana / tam H1 | 0,58 / 1,07 | 0,58 / 1,057 |
| İşaretli ölçüde ölçek farkı (1,5×), yanlış H1 | 0,053 | 0,052 |
| \|Δ\| ölçüsünde ölçek farkı (1,5×), yanlış H1 | 0,666 | 0,658 |
| N1 yanlış "geçersiz" | 0,052 | 0,050 |
| Duyarlılık P, σ %0,05 / 0,075 / 0,1 / 0,15 / 0,2 | 1,00 / 0,96 / 0,60 / 0,09 / 0,02 | 1,00 / 0,963 / 0,600 / 0,095 / 0,018 |
| K 32 / 25 / 20: H0 (δ 0) | 0,575 / 0,377 / 0,192 | 0,582 / 0,384 / 0,188 |
| E1 σ_ölçüm, CC₁₀ 0,5 / 0,7 / 0,9 (%) | 0,018 / 0,011 / 0,005 | 0,015 / 0,010 / 0,004 |
| E1 ortalama Δ (%) | +0,0004 / +0,0021 / −0,0007 | +0,0018 / +0,0004 / +0,0003 |
| E2 oran medyanı | 0,927 / 0,967 / 0,982 | 0,935 / 0,968 / 0,985 |
| E2, 35 sahte olay [%1; %99] | [0,921; 0,938] … | [0,925; 0,945] / [0,963; 0,973] / [0,981; 0,989] |
| E3, CC₁₀ ≈ 0,5, A %0,02 / 0,05 / 0,08 / 0,15 | 0,12 / 0,63 / 0,90 / 1,00 | **0,43** / 0,63 / **0,74** / 1,00 |
| E3, CC₁₀ ≈ 0,7 | 0,11 / 0,66 / 0,99 / 1,00 | 0,27 / 0,79 / 0,98 / 1,00 |

Okuma:
- `tr5b_guc.py`'nin bütün sayıları Monte Carlo saçılımı içinde yeniden üretildi.
- E1 ve E2 tutarlı. Yanlılık önemsiz; 2. adımın [0,80; 1,20] eşiği doğru kodun rahatça geçeceği aralıkta.
- E3 tohuma duyarlı (E3d).

Ek benzetimler (`guc_ek.py`, tohum 424242):
- **Plasebo şartının değeri (yazar noktası 4).** Olay ve plasebo aynı yer yanlılığını taşıyorsa (b, σ_Δ biriminde),
  etki yokken yanlış H1 olasılığı:

  | b | d şartsız | tam kural |
  |---|---|---|
  | 0,25 | 0,20 | 0,03 |
  | 0,5 | 0,41 | 0,05 |
  | 0,75 | 0,28 | 0,04 |

  d şartı gücü yarıya indiriyor (δ 0,75'te 0,93 → 0,54), ama yer yanlılığına karşı tek koruma o. **Denge doğru;
  şart kalmalı.** TR-1 inceleme 2, bulgu 3'ün gerekçesi bu sayılarla nicel olarak doğrulandı.
- **Olay gürültüsü.** Olay Δ'sı kontrolden 1,5 kat gürültülüyse tam H1 gücü δ 0,5 / 0,75 / 1,0'da 0,15 / 0,31 / 0,49
  olur (Ö7).

## E. Yazar noktalarına kısa hükümler

| Nokta | Hüküm |
|---|---|
| 1. Çatallanma | Beyan yeterli. Zorunlu ikinci hüküm satırı önerilmez; bilgi satırı 17 eklenmeli (K1) |
| 2. 4. adımın sertliği | Ölçüt, ana sınavın kendi ölçütüne bağlanmalı (E2). Pilot P1, ana indirmeden önce, yalnız sahte olay verisiyle; tam metin E1'de |
| 3. Kosismik PK | Kural ve yön eşiği doğru. Enerji reddi medyanı, ızgara, aygıt aralığı, en yakın istasyon ve E3'ün belirsizliği düzeltilmeli (E3). "Güç yok" etiketi H1 durumunda "ayırt edilemez" olmalı. Pilot P2 önerilir |
| 4. Plasebo şartı | Dengeli; kalmalı. Ama plasebo istasyonu olay istasyonuyla kesişmeli (Ö5) |
| 5. Hidroloji | Eşleme değil, zorunlu uyarı cümlesi (Ö6) |
| 6. Doluluk ilk aşaması | Taslakta tam tanımlı değil, kapı ana indirmeden sonra. Aşama 0 bulutta 0 €'ya yapılabilir: ≈ 50 000 istek, ≈ 6–7 saat, 3–4 iş. Metin E1'de. 1b sıralı yapılmalı |
| 7. Tek istasyon | Hüküm metni "istasyon çevresi, ortanca 50 km" demeli. σ_Δ birimi tanımlanmalı (Ö7) |
| 8. Volkanik kural | GVP ile kurala bağlanmalı ve kontrollere de uygulanmalı (Ö3) |
| 9. İşleme parametreleri | Özetlerden doğrulanamadı. PK için ±%0,5 ızgarası aralık dışı (E3b); ötekiler makul (K10) |
