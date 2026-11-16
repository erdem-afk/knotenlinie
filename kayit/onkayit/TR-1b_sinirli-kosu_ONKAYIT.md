# TR-1b ön kayıt TASLAĞI: deprem öncesi 2 yıllık GNSS hız değişimi, yalnız büyük etkiye bakan sınırlı koşu

Tarih: 16 Kasım 2026. Durum: **TASLAK. Dondurulmadı, incelenmedi, hiçbir seri ya da olay penceresi açılmadı.**
Türediği yer: `kayit/turetme/ESIK-DAYANAGI.md` (düzeltme 4: kapı "geç/kal" yerine önceden yazılmış MDE) ve TR-1
sürüm 2 (`TR-1_kuresel-gnss-hiz-degisimi_ONKAYIT.md`, `TR-1_INCELEME-1.md`, `TR-1_INCELEME-2.md`), TR-11 sonucu
(`kayit/turetme/tr11/tr11_sonuc.md`). Güç hesabı: `kayit/turetme/tr1b/tr1b_mde.py` → `tr1b_mde.json` (commit
6e926c9; yalnız yapay veri ve TR-11'in commit edilmiş nicelikleri; tohum 20261116, ≈ 13 sn).

## 0. Özet hüküm (taslağın kendisi hakkında)

- **İstatistik olarak tasarım tutuyor; bilimsel olarak dar.** K = 12 ile, önceden sabit bölge payı c0 = 1,64 altında,
  görülebilir en küçük etki: **uyumlu sinyalde g ≈ 1,4 mm/yıl, dağınık sinyalde g ≈ 3,1 mm/yıl** (2 yıllık hız
  değişimi, 100 km içindeki istasyonlarda). Saf TR-11 tabanına göre AUC karşılığı ≈ 0,84–0,85.
- Bu MDE, kuramın öngördüğü büyüklüğün (≈ 0,02–0,5 mm/yıl; aşağıda "kuram") uyumlu sinyalde **3–70**, dağınık
  sinyalde **6–150 katı**dır. Olumsuz
  sonuç kuramın öngördüğü etki hakkında **hiçbir şey söylemez.**
- Plasebo eksikliğini TR-11 tabanı **çözmez, yalnız taşır**: yerinde plasebonun ölçeceği bölge yanlılığı, burada
  önceden konmuş bir pay (c0) olur. c0'ın kendisi bir **tahmindir**. Bu pay, saf tabana göre görülebilir en küçük
  etki kadar büyüktür (c0 = 1,64 tek başına AUC 0,70 üretir; c0 = 1'de MDE AUC'si 0,68). Yani pay konmazsa sınama
  etkiyi yanlılıktan ayıramaz. Pay konunca da AUC ≈ 0,70'in altındaki etkiler **hiçbir K ile görülemez**.
- **K bilinmiyor.** TR-1 sürüm 2'nin 11–12 kümesi eşleşik kontrol şartıyla sayılmıştı. Bu taslak kontrol şartını
  kaldırır ama TR-11'in daha katı sakinlik kurallarını ekler. Dondurmadan önce yalnız üstveriyle bir aşama 0 sayımı
  gerekir (§7). MDE tablosu K = 5–40 için verildi.

## 1. Soru (sınırlı)

M ≥ 6,5 sığ olaylardan önceki son 2 yılda, dış merkezin 100 km içindeki istasyonlarda ölçülen hız değişimi boyu S,
TR-11'in depremsiz pencerelerindeki S dağılımının **c0 = 1,64 katına ölçeklenmiş** hâlinden sistematik olarak büyük
mü? Bu, yalnız **büyük** bir etkinin varlığını sorar. Küçük etkiyi sormaz. Tahmin becerisi iddiası değildir.

## 2. Veri ve örneklem (TR-1 sürüm 2'den farklar işaretli)

- Olaylar: ComCat, 2000-01-01 → 2026-01-01T00:00:00 (2026 hariç), M ≥ 6,5, derinlik ≤ 30 km. **Fark:** T ≤ 2025-12-31
  (kontrol için T + 2 yıl artık gerekmez). Dış merkezi Marmara kutusunda (39,5–42,0° K, 26,0–31,5° D) olan olay yok sayılır.
- GNSS: NGL IGS20 tenv3, yatay. Marmara kutusu istasyonları indirilmez. Kutuya 150 km'den yakın istasyonlarda
  (TR-11 Ö4: CMLD, AFYN, KRBK, AKHR, KLUU ve listeye giren yenileri) w1'den sonraki satırlar ayrıştırılmadan atlanır.
- **Pencere TR-11 ile özdeş uzunlukta:** w1 = T − 7 g, w0 = w1 − 1826 g, menteşe H = w1 − 730 g. T − 7 günden sonraki
  hiçbir gözlem ve hiçbir basamak kaydı kullanılmaz.
- **İstasyon ve küme ölçüsü TR-11 koşu koduyla aynı** (`tr11_kosu.py`'nin istasyon modeli, doluluk ≥ 0,60, kod 1
  sıçrama kuralı, ayıklama, S = medyan |Δv_yakın − medyan Δv_ref|). Yakın ≤ 100 km (3–8), **referans her olayda
  200–500 km** (TR-1'in M ≥ 7,5 için 500–1000 km halkası kaldırıldı; büyük olayda sinyal referansa taşarsa yanlılık
  H0 yönündedir).
- **Postsismik ve kosismik dışlama (önceden sabit; TR-11 kurallarının olay penceresine çevirisi):**
  - İstasyon: [w0 − 730 g, w1] içinde uzaklığı ne olursa olsun hiçbir kod 2 kaydı yok (TR-11 §2.3 kural 3; TR-1'in
    "eşik/4" kuralının yerine). Hedef olayın kendi kaydı w1'den sonradır ve kurala girmez.
  - Merkez (dış merkez): Ş1 merkezin 200 km içinde [w0 − 5 y, w1] arasında M ≥ 6,0, derinlik ≤ 40 km olay yok;
    Ş2 500 km içinde [w0 − 10 y, w1] arasında M ≥ 7,0, derinlik ≤ 70 km olay yok; Ş3 1000 km içinde [w0 − 10 y, w1]
    arasında M ≥ 8,0 yok. TR-11'deki "T + 2 yıl" uzantısı olay penceresinde uygulanamaz (hedef olayın kendisi).
    "Deprem yok" sorgusu 1976-01-01'den başlar (INCELEME-2 bulgu 6).
  - Gerekçe: dışlama olay ve taban için **aynı** kuraldır. Böylece kirlenme farkı yalnız bölge türünden kalır (§5.1).
  - Bilinen bedel: Ş1, hedeften önceki 7 yıl içinde 200 km'de M ≥ 6 öncü dizisi olan olayları atar. Öncül bu
    dizilerde ise yanlılık H0 yönündedir; kabul edilir.
- **Bağımsızlık kümeleri:** TR-1 (i) ve (ii), ayrıca **(iii)** aynı 10° × 10° blokta ve pencereleri çakışan olaylar
  aynı kümedir (TR-11'in ortak mod birimi). Küme puanı = olayların ortalaması. K = küme sayısı.

## 3. Sınama (kesin, rastgeleleştirme)

- **Sıfır örneklemi:** TR-11'in 665 küme-penceresi, aynı koşuda, aynı kod ve aynı indirme tarihiyle **yeniden
  hesaplanır** (NGL yeniden işleme farkını kaldırmak için). Yeniden hesaplanan q95, TR-11'in [2,06, 2,76] aralığının
  dışındaysa hüküm "geçersiz (sürüm)" olur.
- **Olay puanı:** u = F̂_s(S_olay), F̂_s olayın n_y katmanındaki (3–4 / 5–7 / 8) TR-11 S'lerinin orta-sıra ECDF'i.
  Küme puanı u_k; istatistik ū = ortalama u_k.
- **H0' (önceden sabit):** olay S'i, c0 × (aynı katmandan çekilmiş TR-11 S'i) gibi dağılır; **c0 = 1,64**.
- **Sıfır dağılımı:** her küme için (m olaylıysa m tane) aynı katmandan rastgele TR-11 küme-penceresi çekilir, S'i
  c0 ile çarpılır, F̂_s ile puanlanır; ū'nun 200 000 çekilişlik dağılımı. p = P(ū_sıfır ≥ ū_gözlenen). Tek yanlı
  α = 0,05. Bu, değiş tokuş edilebilirlik varsayımı altında kesin bir rastgeleleştirme sınamasıdır; asıl varsayım
  c0'dır (§5.1).
- **İkincil (hüküm vermez):** q95 aşım sayısı, kesin binom. Yapayda A sınamasından belirgin güçsüz çıktı (uyumlu
  sinyalde K = 12 için MDE 2,3 mm/yıl, A'da 1,4), bu yüzden birincil değildir.
- **Bilgi satırları:** c0 = 1 ve c0 = 1,3 ile p; TR-1'in yerinde plasebo pencereleri (sayımda 3 olay) aynı yolla
  puanlanır; TR-11 sınıf B küme-pencerelerinin (10 KP, 6 yer) c0 = 1 altındaki ū'su; bir kümeyi dışarıda bırakma
  aralığı; olay ve TR-11 için yakın istasyon uzaklıklarının medyanı; bölge ve mekanizma bileşimi.

## 4. Etki büyüklüğü ve kaynağı

| Kaynak | Değer (aynı ölçü, S cinsinden) | Etiket | Durum |
|---|---|---|---|
| Yayımlanmış yıl ölçekli GNSS öncül iddiaları (TR-12) | TR-11 tabanının (2,42) üstünde doğrulanan 0; 3 iddia altında; Bedford 2020 tersinmesi 0,3–2,8 mm/yıl; 8 iddia çevrilemedi | **literatür** | tablo projede; sayıların bir kısmı özetten, çevrilemeyenler "doğrulanamadı" |
| Sünme cephesinin 2 yıllık yüzey izi (Halka 8) | TR-11 tabanının 5–100 kat altı, yani ≈ 0,02–0,5 mm/yıl | **kuram** (tarayıcının hesabı) | bağımsız doğrulanmadı |
| Bu taslağın "büyük etki"si | bir varsayım değil; K ile görülebilen en küçük g (§5) | **hesap** (yapay model) | aşağıda |
| Bölge payı c0 = 1,64 | TR-11 içinde gözlenen en büyük alt küme şişmesi: epok 2008 q95 3,98 / tüm 2,42 | **tahmin** | aktif bölge şişmesinin bundan küçük olduğuna dair kanıt yok |

Yani bu sınavın görebildiği etkiyi ne literatür ne kuram öngörüyor. Sınav yalnız "beklenmedik ölçüde büyük ve
yaygın bir sinyal var mı" sorusunu kapatabilir.

## 5. MDE ve ×0,5 / ×2 duyarlılığı (hesap: `tr1b_mde.json`)

**Yapay model (varsayım):** küme başına n_y yakın istasyon (TR-11 katman sayıları); istasyon artık vektörü
N2(0, σ_c²), σ_c log-normal; S = medyan boy. μ = −0,38, τ = 0,60, TR-11'in q50/q90/q95/q99'una uyduruldu (model
0,79 / 1,83 / 2,33 / 3,66; TR-11 0,79 / 1,80 / 2,42 / 3,71). Sinyal g, bütün yakın istasyonlara aynı yönde
eklenir ("uyumlu"); "dağınık" kipte istasyon başına g × U(0, 1). Güç 0,8, tek yanlı α 0,05.

Doğrulama ve sınırları:
- Modelde 3 mm/yıl eklenince S'in medyan artışı 2,35; TR-11'in kendi Monte Carlo beklentisi 2,17. Model sinyale ≈ %8
  fazla duyarlı, yani MDE'ler **≈ %10 iyimser** olabilir.
- Model katman farkını tutmuyor: q95 model 2,42 / 2,33 / 2,28; TR-11'de 2,76 / 2,24 / 1,94 (n_y 3–4 / 5–7 / 8).
  Koşuda puanlama katman içinde yapıldığı için bu yalnız MDE'nin kesinliğini etkiler, sınamanın geçerliğini etkilemez.

**MDE, g (mm/yıl); parantezde saf TR-11 tabanına göre AUC; A sınaması:**

| K | c0 = 1,64 uyumlu (**ana**) | c0 = 1,64 dağınık (**ana**) | c0 = 1,3 uyumlu / dağınık | c0 = 1 uyumlu / dağınık (yanlılık payı yok) |
|---|---|---|---|---|
| 5 | 1,74 (0,90) | 4,32 (0,92) | 1,39 / 3,14 | 1,06 / 2,22 |
| 6 | 1,64 (0,89) | 3,96 (0,90) | 1,29 / 2,91 | 0,99 / 2,06 |
| 8 | 1,51 (0,87) | 3,52 (0,88) | 1,21 / 2,60 | 0,90 / 1,83 |
| 10 | 1,44 (0,85) | 3,24 (0,86) | 1,14 / 2,41 | 0,84 / 1,68 |
| 11 | 1,40 (0,84) | 3,16 (0,86) | 1,12 / 2,30 | 0,82 / 1,62 |
| **12** | **1,37 (0,84)** | **3,09 (0,85)** | 1,09 / 2,27 | 0,79 / 1,58 |
| 15 | 1,31 (0,83) | 2,91 (0,84) | 1,05 / 2,17 | 0,74 / 1,45 |
| 20 | 1,26 (0,82) | 2,70 (0,82) | 0,98 / 2,00 | 0,68 / 1,32 |
| 27 | 1,19 (0,80) | 2,51 (0,80) | 0,93 / 1,86 | 0,64 / 1,19 |
| 40 | 1,14 (0,79) | 2,35 (0,79) | 0,87 / 1,71 | 0,57 / 1,06 |

- H0' altında saf tabana göre AUC: c0 = 1,3 → 0,61; c0 = 1,64 → 0,70. **Bu, c0 = 1'deki MDE AUC'sine (K = 12'de
  0,68) eşittir.** Bölge payı ile aranan etki aynı büyüklüktedir.
- K'nin MDE'ye etkisi zayıf: K 12 → 20 ana MDE'yi yalnız %8 düşürüyor. Darboğaz K değil, c0.
- İkincil binom sınaması (q95 aşımı): K = 12'de uyumlu MDE 2,29 (c0 = 1,64), 2,06 (c0 = 1). Kesin eşik c = 6
  aşım, gerçek α 0,014.

**×0,5 / ×2 (K = 12, A):**

| Kip | MDE | ×0,5: g (AUC); güç K = 12; gereken K | ×2: g (AUC); güç K = 12 |
|---|---|---|---|
| uyumlu, c0 = 1,64 | 1,37 | 0,69 (0,65); 0,001; **hiçbir K ile görülmez** (AUC < 0,70 payı) | 2,74 (0,97); 1,00 |
| dağınık, c0 = 1,64 | 3,09 | 1,54 (0,68); 0,006; **hiçbir K ile görülmez** | 6,18 (0,96); 1,00 |
| uyumlu, c0 = 1,3 | 1,09 | 0,55 (0,60); 0,014; > 300 | 2,18 (0,94); 1,00 |
| uyumlu, c0 = 1 | 0,79 | 0,40 (0,55); 0,13; ≈ 200 | 1,58 (0,88); 1,00 |
| dağınık, c0 = 1 | 1,58 | 0,79 (0,57); 0,15; ≈ 130 | 3,16 (0,86); 1,00 |

Okuma: güç eğrisi dik. Etki MDE'nin iki katıysa K = 12 kesin görür; yarısıysa pay konduğu sürece hiç görülmez. Yani
sonuç, c0'ın doğruluğuna K'den çok daha duyarlıdır.

## 6. Varsayımdan bağımsız kusurlar ve çözümleri

1. **Plasebo yok; TR-11 tabanı onun yerini tutar mı?** Kısmen.
   - Çözdüğü: ölçü, işleme sürümü, istasyon modeli, n_y ve pencere uzunluğu farkı. Yeniden hesaplama ve katman
     içinde puanlama bunları eşitler. Sayı sorunu da çözülür: 665 KP, plasebo için gereken ≥ 10'un çok üstünde.
   - **Getirdiği yeni yanlılık:** TR-11 tabanı "az sismik bölge tabanı"dır (KP'lerin %98'i sınıf D; doğrultu atımlı
     kuşakta 0 yer). Olay merkezleri ise aktif sınırlardadır. Orada eşik altı postsismik kalıntı, yavaş kayma,
     volkanizma, büyük gerinim hızı ve seyrek, açık deniz geometrisi öncülden bağımsız olarak S'i büyütür. Yanlılığın
     yönü **"büyük etki VAR"** yönündedir. Yerinde plasebo bunu ölçerdi; TR-11 ölçemez.
   - Çözüm: önceden sabit c0 = 1,64 payı ve "VAR" hükmünün dili (§8). Bu bir **tahmin**dir. Ölçülmüş bir aktif bölge
     tabanı (TR-11 sınıf A/B ≥ 30 yer) gelirse c0'ın yerini o alır (§10).
   - Epok yanlılığı: TR-11 yalnız 5 epokta (1 Ocak 2003…2023) ölçüldü; 2008 epoğu belirgin yüksek. Olay T'leri her
     tarihte. Bilgi satırı: olayın w1'ine en yakın TR-11 epoğunun ECDF'i ile puanlama.
2. **Postsismik kirlenme:** §2'deki dışlama olay ve tabana aynı kuraldır, önceden sabittir. Kalan kirlenme
   (eşik altındaki depremler, 200 km dışındaki M6'lar) aktif bölgelerde daha sık olduğu için 1. maddedeki paya girer.
3. **Ortak mod hatası ve bağımlılık:** 10° blok kuralı (§2 (iii)) aynı bölgedeki eşzamanlı olayları tek küme yapar.
   Sıfır çekilişleri bağımsız KP'lerdir; TR-11'de aynı yerin farklı epokları ayrı KP'dir. Bu, sıfır dağılımının
   varyansını hafifçe küçük gösterebilir. Bilgi satırı: yer başına tek KP ile çekiliş.
4. **K bilinmiyor:** §7 aşama 0 olmadan dondurulmaz.
5. **MDE model bağımlı:** sinyal yanıtı ≈ %8 iyimser, katman farkı tutulmuyor (§5). MDE'ler ±%10–20 belirsizdir.
6. **Çoklu c0:** hükmü yalnız c0 = 1,64 verir. Ötekiler bilgi satırıdır.
7. **Kod denetimi:** TR-11'in (i) ve (ii-b) yapay denetimleri, ayrıca (ii-a) gerçek tabanda 3 mm/yıl doğu sinyali
   ekleme (istasyon düzeyi medyan d_E [2,95, 3,05]). Biri kalırsa "geçersiz (kod)". Bunlar olay S'i görülmeden koşar.
   INCELEME-2 bulgu 2'nin kendini boşa çıkaran pozitif kontrolü yok: sinyal yalnız sahte olaya, burada TR-11 KP'sine eklenir.

## 7. Aşama 0 (dondurmadan önce, yalnız üstveri)

TR-1 sayım betiği (`kayit/turetme/tr1/sayim_ustveri.py`) §2 kurallarıyla yeniden yazılır. Girdi yalnız
`DataHoldings.txt`, `steps.txt` ve ComCat'tir. Olay penceresi serisi indirilmez. Sonuç K (üst sınır, doluluk
atlanarak) ve bileşim yazılır. Bu taslak K'yi tahmin etmez. Kontrol şartı kalktığı için TR-1 sayımındaki 27 geçerli olay
kümesi tavan sayılabilir. Ş1–Ş3 ve kod 2 kuralı bunu düşürür. Bu adımda kural K'yi büyütmek için değiştirilmez
(INCELEME-2 bulgu 9).

## 8. Hüküm dalları (sıra kodda sabit)

1. **Veri yok:** aşama 0'da ya da koşuda K < 6, veya TR-11 yeniden hesabı veri kapısını (≥ 100 yer, ≥ 30 blok)
   geçmiyor. MDE yine K ile birlikte yazılır.
2. **Geçersiz:** kod denetimi kaldı ya da yeniden hesaplanan q95 [2,06, 2,76] dışında.
3. **Büyük etki VAR:** c0 = 1,64 altında p ≤ 0,05 **ve** her "bir kümeyi dışarıda bırak" koşusunda p ≤ 0,10.
   Cümle: "Bu K kümede, olay öncesi 2 yıllık hız değişimi boyu, depremsiz tabanın 1,64 katından bile büyük. Bu bir
   öncül ya da tahmin iddiası değildir; aktif bölge tabanıyla yeniden sınanmadan Marmara'ya taşınmaz."
4. **Ayırt edilemez (MDE = …):** öteki her durum. Cümle: "K = …, bu örneklemle görülebilir en küçük etki uyumlu
   sinyalde g = … mm/yıl, dağınık sinyalde g = … mm/yıl (AUC …, c0 = 1,64). Daha küçük etkiler hakkında bilgi yok."
   c0 = 1'de p ≤ 0,05 ise şu da eklenir: "Saf depremsiz tabandan büyük, ama aktif bölge payı içinde."
5. **H0 hükmü yoktur.**

## 9. Olumsuz sonuç ne söyler, ne söylemez

- Söyler: bu K kümede, 100 km içindeki istasyonları birlikte g ≳ 1,4 mm/yıl (uyumlu) ya da g ≳ 3,1 mm/yıl (dağınık)
  oynatan, 2 yıl süren bir olay öncesi hız değişimi olağan değildir (güç 0,8; ana tablo K = 12).
- Söylemez: öncül yok. Kuramın öngördüğü ≤ 0,5 mm/yıl'lık izler, yönlü (fay doğrultusuna izdüşümlü) sinyaller,
  2 yıldan kısa ya da uzun pencereler, Ş1'in attığı öncü dizili olaylar ve doğrultu atımlı alt küme hakkında bilgi
  yoktur. Marmara için alarm yolu kapandı demek değildir. TR-11 Ö3 kuralı geçerlidir.

## 10. Yeniden açma şartı

(a) Aktif kuşakta ölçülmüş bir taban (TR-11 sınıf A ya da B, ≥ 30 yer): c0'ın yerine ölçülen değer gelir.
(b) Yerinde plasebosu ≥ 10 kümede hesaplanabilen bir arşiv (ör. GEONET F5 doğrudan).
(c) Yönlü ölçü (TR-1 §9 (a)).
(d) Aşama 0'daki K'yi en az iki katına çıkaran yeni açık GNSS arşivi.
Her biri yeni ön kayıt ister.

## 11. Körlük ve İstanbul

Bu taslak için hiçbir tenv3 serisi indirilmedi. Hiçbir olay penceresi açılmadı. Gerçek S hesaplanmadı. Tek gerçek
girdi, TR-11'in commit edilmiş nicelikleri (q50, q90, q95, q99, katman q95'leri). Marmara kutusunun 2017+ GNSS'i ve
bütün 2026 verisi kördür. Sonuç bir olasılık terimi üretmez. İstanbul için mutlak olasılık yazılmaz.
