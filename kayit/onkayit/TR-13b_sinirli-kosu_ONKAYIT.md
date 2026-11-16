# TR-13b ön kayıt TASLAĞI: büyük doğrultu atımlı depremden 2–3 yıl önce sismisite yerelleşmesi, sınırlı koşu

Tarih: 16 Kasım 2026. Durum: **TASLAK. Dondurulmadı, incelenmedi. Gerçek katalogda hiçbir yerelleşme ölçüsü
(V(q), z) hesaplanmadı. Hiçbir yeni katalog indirilmedi.**
Türediği yer: `kayit/turetme/ESIK-DAYANAGI.md` (düzeltme 4) ve `kayit/onkayit/TR-13_SAYIM.md` + Ek 1 (K kesin
sayımı). Güç hesabı: `kayit/turetme/tr13b/tr13b_mde.py` → `tr13b_mde.json` ve `tr13b_K.py` → `tr13b_K.json`
(commit 7898a2a). İkisi de yalnız yapay ETAS kataloğu kullanır. Üreteç, GK74 ve ölçü `kayit/turetme/tr13/tr13_guc.py`'den
aynen alındı. Tohum 20261116 / 20261117. Süre ≈ 6 + 5 dk.

## 0. Özet hüküm (taslağın kendisi hakkında)

- **Ana sınama (T1, ETAS-kalibre ortalama z) yapayda tutuyor.** K = 14 ile görülebilir en küçük etki
  **f ≈ 0,20–0,28**. Bu, önce-penceredeki arka plan olaylarının beşte biri ile dörtte birinin kırık bandına
  taşınmasıdır. Bant içi payı 3 yılda ≈ **2 katına** çıkar (yapayda %8–10 → %15–21).
- Anma eşiği yerine ETAS'tan kalibre eşik kullanınca gerçek α %5'e iner. Dallanma 0,4 ya da 0,8 olsa da
  %4,5–6,7 arasında kalır. Ama bölgenin arka plan sayısı kalibrasyondakinin 2 katı ve GK74 doyma bölgesindeyse
  α %21'e çıkar. Çözüm: eşik her bölge için kendi N3bg'siyle kalibre edilir ve N3bg ≤ 100'e indirilir (§3).
- **Bölgenin kendi geçmişinden plasebo (T2), eşleşik kontrolün yerini tutmaz.** Kesin ve iyi kalibre (α %2–6),
  ama MDE f ≈ 0,43 (N3bg 50). N3bg 100'de f ≤ 0,5 içinde güç 0,8'e hiç ulaşmıyor. Ayrıca plasebo penceresi
  kuramın "2–10 yıl önce etkinleşme" dediği döneme düşüyor (§6.3). Yalnız bilgi satırıdır.
- **Etkinin makullüğü doğrulanamadı.** BZ20'nin bildirdiği büyüklük okunamadı (403). MDE fiziksel olarak anlamsız
  değil, ama "büyük": bant içi oranın iki katına çıkması. Olumsuz sonuç bundan küçük etkiler hakkında bilgi taşımaz.
- Tasarım kendi içinde tutarlı. En büyük açık kusur, ölçünün BZ20'nin aynısı değil, yeniden kurulumu olması.
  İkincisi, ETAS'ın gerçek bölgelerin durağan olmayan arka planını (sürüler, ağ değişimi) taşımaması (§6).

## 1. Soru (sınırlı)

Temiz önce-pencereli, referans dönemi dolu, sığ doğrultu atımlı Mw ≥ 6,5 ana şoklardan önceki 3 yılda,
kümesizleştirilmiş arka plan sismisitesinin kesirsel alanı V(0,5), aynı bölgenin önceki 7 yılına göre, ETAS'ın
sinyalsiz olarak ürettiğinden **büyük ölçüde** daha mı küçük (yerelleşme)? Yalnız büyük etkiyi sorar. Tahmin değildir.

## 2. Örneklem (TR-13_SAYIM Ek 1, değiştirilmeden)

- Ana tasarım: M ≥ 6,5, Mc = MAXC + 0,2, N3bg ≥ 50, temiz önce-pencere, referans dolu, tol 0,3 → **K = 14 küme**
  (Ek 1 §E1.2, E1.3). Liste Ek 1'deki `tr13_tamsayim.json`'dan aynen alınır. Yeni olay eklenmez, olay çıkarılmaz.
- Eşleşik depremsiz kontrol şartı **kaldırılır**. Onun yerini ETAS kalibrasyonu alır (§3). Kontrol şartıyla K 3–7'ye
  düşüyordu.
- Bilgi satırları: M ≥ 6,0 tol 0,3 (K = 20); tol 0,1 (K = 11). Hüküm yalnız ana satırdan.
- Bölge: R = max(2L, 50 km) daire. Önce [t − 3 y, t − 2 g); referans [t − 10 y, t − 3 y). Mevcut ham arşivler
  (`/mnt/project-files/turetme/tr13-ham/`) kullanılır. Yeni indirme yalnız eksik parça varsa yapılır, o da yalnız
  ana şoktan önceki pencere için.

## 3. Ölçü ve sınama (önceden sabit)

- **Ortak Mc:** bölgede Mc_b = max(Mc_önce, Mc_ref). Önce ve referans aynı eşikle sayılır (ağ iyileşmesi kaymasını
  kaldırır).
- **Doyma kuralı:** Mc_b'de önce-penceredeki GK74 arka plan sayısı 100'ü aşıyorsa Mc_b, sayı ≤ 100 olana dek
  0,1'lik adımlarla yükseltilir. Gerekçe: yapayda N3bg ≳ 150'de GK74 sinyali siliyor ve kalibre eşikte bile α %21'e
  çıkıyor. Varsayım: α = b ETAS'ında büyüklük eşiğini yükseltmek, aynı yapının daha seyrek bir kopyasını verir. Bu
  kural Kumamoto (4225), Ridgecrest (576), Loma Prieta (608) gibi yoğun bölgelerde eşiği 1–1,6 birim yükseltir.
  Yükseltme sonrası N3bg < 50 olursa bölge düşer. Düşen sayısı yazılır.
- **Kümesizleştirme:** GK74 (TR-13 ile aynı). En yakın komşu (BZ20 yöntemi) bilgi satırıdır.
- **Ölçü:** 5 km hücre, V(0,5), referanstan aynı sayıda olayla 200 alt örnek, z = (V_önce − ort) / sd. Yerelleşme
  z < 0. Bu, BZ20'nin gerekçeli yeniden kurulumudur, aynısı değildir (TR-13 §2.2).
- **ETAS sıfır dağılımı (bölge başına):** her bölge için, o bölgenin R'si ve yükseltilmiş Mc'deki N3bg'si ile
  sinyalsiz ETAS (TR-13 §4.1 parametreleri: dallanma 0,6, α = b = 1, p 1,1, c 0,01 g) 2000 kez üretilir, aynı
  GK74 ve ölçüyle z_0 dağılımı alınır.
- **T1 (ana):** z̄ = K bölgenin ortalama z'si. Sıfır dağılımı: her bölgenin kendi z_0 havuzundan birer çekiliş,
  ortalama; 200 000 çekiliş. p = P(z̄_0 ≤ z̄_gözlenen). Tek yanlı α = 0,05. ETAS doğruysa kesindir (Monte Carlo hatası
  dışında).
- **T2 (bilgi):** kendi geçmişiyle eş: plasebo z_p, önce [t − 6 y, t − 3 y), referans [t − 10 y, t − 6 y). d = z − z_p,
  kesin işaret çevirme (2^14 = 16 384 desen).
- **T3 (bilgi):** bölge başına kendi ETAS z_0'ının %5 niceliği aşılıyor mu; aşım sayısı, kesin binom (K = 14'te
  eşik 3 aşım, gerçek α 0,030).

## 4. Etki büyüklüğü ve kaynağı

| Kaynak | Değer | Etiket | Durum |
|---|---|---|---|
| BZ20 (GJI 223, 561–583): 5 ana şok öncesi 2–3 yıl yerelleşme; Parkfield'da ters yön | kesirsel alan azalmasının büyüklüğü **okunamadı** | **literatür** | tam metin 403; özetten yalnız yön ve zaman doğrulandı |
| EGU 2023 özeti | 2–10 yıl önce geniş hacimde etkinleşme, 2–3 yıl önce sönme; yer dış merkezi içermeyebilir | **literatür** (özet) | yönü ve yeri tek anlamlı değil |
| Hasar reolojisi (Ben-Zion ve Zaliapin) | yerelleşme öngörüsü nitel, sayı yok | **kuram** | nicel değer yok |
| f ≈ 0,2 (TR-13 sayımı, "orta") | bant içi oran ≈ 2,5 kat | **tahmin** (benzetimden) | makullük doğrulanamadı |
| Bu taslağın MDE'si | f ≈ 0,20–0,28, bant payı ≈ 2 kat | **hesap** (yapay) | aşağıda |

## 5. MDE ve ×0,5 / ×2 duyarlılığı

**K = 14, T1, güç 0,8, α 0,05** (iki bağımsız benzetim; fark Monte Carlo ve GK74'ün güç eğrisini düzleştirmesinden):

| N3bg (yükseltilmiş Mc'de) | tr13b_mde (tohum …16) | tr13b_K (tohum …17) | bant payı, f = 0 → MDE |
|---|---|---|---|
| 50 | 0,22 | 0,21 | %9,8 → ≈ %20 (≈ 2,0 kat) |
| 100 | 0,20 | 0,28 | %8,5 → ≈ %15–16 (≈ 1,9 kat) |

N3bg 100'de güç eğrisi f 0,2–0,25 arasında düzleşiyor (0,68 / 0,69). GK74 kırık bandındaki yoğun arka planın
bir kısmını küme sayıp atıyor. Bu yüzden MDE için aralık verilir: **f ≈ 0,20–0,28**.

**K'ye bağımlılık (T1, tr13b_K):**

| K | 8 | 11 | 14 | 17 | 20 |
|---|---|---|---|---|---|
| MDE f, N3bg 50 | 0,28 | 0,25 | 0,21 | 0,19 | 0,19 |
| MDE f, N3bg 100 | 0,43 | 0,33 | 0,28 | 0,27 | 0,20 |

**×0,5 / ×2 (K = 14, T1):**

| N3bg | MDE | ×0,5: f; güç K = 14; gereken K | ×2: f; güç K = 14 |
|---|---|---|---|
| 50 | 0,22 | 0,11; 0,33; ≈ 80 | 0,44; 1,00 |
| 100 | 0,20 | 0,10; 0,34; ≈ 60 | 0,40; 0,92 |

T2 (kendi geçmişi): MDE 0,43 (N3bg 50); N3bg 100'de f ≤ 0,5 içinde güç 0,8'e ulaşılmıyor (f = 0,5'te 0,63). Yarısı
için gereken K ≈ 120. T3 (binom): MDE 0,28 (50), 0,46 (100).

**Gerçek α (eşik dallanma 0,6 ve hedef N ile kalibre edildi; veri başka ETAS'tan):**

| Veri | N3bg 50: T1 / T2 / T3 | N3bg 100: T1 / T2 / T3 |
|---|---|---|
| aynı ayar (bağımsız havuz) | 0,026 / 0,032 / 0,031 | 0,040 / 0,055 / 0,038 |
| dallanma 0,4 | 0,054 / 0,055 / 0,030 | 0,067 / 0,057 / 0,034 |
| dallanma 0,8 | 0,045 / 0,054 / 0,052 | 0,052 / 0,064 / 0,018 |
| N3bg yarısı | 0,019 / 0,024 / 0,037 | 0,098 / 0,084 / 0,033 |
| N3bg iki katı | 0,059 / 0,042 / 0,039 | **0,214** / 0,038 / 0,160 |

Anma eşiğinde (z < −1,645) tek pencere yanlış alarmı bu benzetimde %13,4 (TR-13'te %13–37). Okuma: kalibrasyon
dallanmaya karşı dayanıklı, N3bg uyuşmazlığına ve doymaya karşı değil. Bu yüzden §3'teki bölge başına N3bg ile
kalibrasyon ve ≤ 100 kuralı zorunludur.

## 6. Varsayımdan bağımsız kusurlar ve çözümleri

1. **Yanlış alarm oranı (%13–37, anma %5):** ETAS'tan bölge başına kalibre eşikle çözülür (§5: α %2–7). Kalan
   risk: gerçek arka plan ETAS değildir. Sürüler, volkanik ve akışkan kaynaklı geçiciler, ağ değişimleri ETAS'ta yok.
   Bunlar z'yi her iki yöne oynatır. Ortalama z'yi daha çok **yerelleşme** yönünde iterler, çünkü sürüler dar
   alanda toplanır. Çözüm: (a) bölge başına dallanma oranı referans döneminden en çok olabilirlikle uydurulur ve
   eşik 0,4 / 0,6 / 0,8'in **en tutucusuyla** alınır; (b) bilgi satırı: z'si en küçük bölge dışarıda bırakılınca p.
   Bu tutuculuk bölgenin gerçek α'sını ölçmez; yalnız ETAS içindeki belirsizliği kapatır.
2. **Ölçü yeniden kurulum:** hücre, q, standartlaştırma ve kümesizleştirme bizim seçimimiz. Hepsi §3'te tek değere
   bağlandı (TR-13 §7'nin 12 serbestliği). BZ20 tam metni okunursa bu taslak dondurulmadan karşılaştırılır.
   Fark varsa ölçü değiştirilmez, ama fark ön kayda yazılır.
3. **Eşleşik kontrol yerine kendi geçmişi (T2) neden yetmez:**
   - Güçsüz: d'nin sd'si ≈ 2,8–3,2, z'ninki ≈ 1,4–1,5. Fark alınca varyans ikiye katlanıyor. MDE iki katına çıkıyor.
   - Plasebonun önce-penceresi [t − 6, t − 3) olayın referansıyla örtüşüyor. İkisi bağımsız değil.
   - EGU 2023'e göre 2–10 yıl önce "etkinleşme" var. Gerçekse plasebo penceresi sinyalin bir parçasını taşır.
   - Daha eski pencereler (t − 20 y'ye inen) Ek 1'e göre katalog boşluğu yüzünden K'yi 3–7'ye düşürüyor.
   Sonuç: T2 bilgi satırıdır, hüküm vermez.
4. **Doyma ve eşik yükseltme:** ≤ 100 kuralı yoğun bölgelerde çözünürlüğü atar (Kumamoto'da olayların %98'i).
   Etki f bir oran olduğu için ilke olarak eşikten bağımsızdır. Ama küçük olaylara özgü bir yerelleşme varsa bu kural
   onu kaçırır. Bilinen bedel; H0 yönünde.
5. **Bağımsızlık ve temsil:** 14 kümenin yarısı Kaliforniya, Japonya ve Yeni Zelanda. Mekanizma ölçütü gevşek.
   Örneklem "yoğun ağlı kıta ve yay içi doğrultu atımlı faylar"dır. İzmit 1999 örneklemde; Marmara terimi değildir.
6. **Bölge yarıçapı:** benzetim yalnız R = 80 km. Gerçek R 50 km ile ≈ 200 km arasında. Bölge başına kalibrasyon
   kendi R'siyle yapıldığı için sınama geçerliği etkilenmez; MDE tablosu yalnız R ≈ 80 için geçerlidir.

## 7. Hüküm dalları (sıra kodda sabit)

1. **Veri yok:** doyma kuralından sonra K < 8, ya da ham arşiv sha256'sı `tr13_ham_sha256.txt` ile uyuşmuyor.
   MDE (K'ye göre tablo) yine yazılır.
2. **Geçersiz:** kod denetimi kalır. Yapay ETAS'ta bilinen f = 0,3 eklenince ortalama z, `tr13b_mde.json`'daki
   beklentinin ±%25'i dışındaysa; ya da sinyalsiz yapayda kalibre α > 0,08 ise. Bu denetim gerçek z görülmeden koşar.
3. **Büyük etki VAR:** T1 p ≤ 0,05 **ve** en tutucu dallanma eşiğiyle p ≤ 0,05 **ve** z'si en küçük bölge
   dışarıdayken p ≤ 0,10. Cümle: "Bu 14 bölgede ana şoktan önceki 3 yılda kümesizleştirilmiş arka plan,
   ETAS'ın ürettiğinden belirgin biçimde yerelleşmiş. Tahmin ya da alarm iddiası değildir; ileriye dönük sınav ayrı
   ön kayıt ister."
4. **Ayırt edilemez (MDE = …):** öteki her durum. Cümle: "K = …, görülebilir en küçük etki f ≈ … (bant içi oranın
   ≈ … katı). Daha küçük yerelleşme hakkında bilgi yok."
5. **H0 hükmü yoktur.** z̄ > 0 (yayılma) çıkması da "ayırt edilemez"dir. Yön tek yanlı sabittir.

## 8. Olumsuz sonuç ne söyler, ne söylemez

- Söyler: bu 14 bölgede, önce-penceredeki arka planın ≳ %20–28'inin kırık bandına toplanması (bant içi oranın
  ≈ 2 katına çıkması) olağan bir öncü değildir (güç 0,8, bu ölçü ve ETAS altında).
- Söylemez: BZ20 yanlış. Bildirilen azalmanın büyüklüğü bilinmiyor; daha küçük yerelleşme, başka bir hücre ya da q,
  en yakın komşu kümesizleştirmesi, dış merkezi içermeyen yerelleşme ve "sönme" hakkında bilgi yoktur. M ≥ 6,0
  örneklemi ve Marmara hakkında bilgi yoktur.

## 9. Yeniden açma şartı

(a) BZ20 tam metni meşru yoldan okunur ve ölçü ya da etki büyüklüğü bu taslaktakinden farklıdır.
(b) Yazarlardan bağımsız bir ETAS yanlış alarm sınaması yayımlanır.
(c) Daha düşük Mc'li açık bölgesel katalog K'yi (doyma kuralından sonra) ≥ 28'e çıkarır.
(d) "VAR" çıkarsa: ileriye dönük, alarm biçimli ayrı ön kayıt.

## 10. Körlük ve İstanbul

Bu taslakta gerçek katalogda V(q), Gini ya da z hesaplanmadı. Yeni katalog indirilmedi. Ana şok sonrası hiçbir
pencere açılmadı. Bütün 2026 verisi kördür; katalog 2025-12-31'de biter. Marmara kutusunun 2017+ GNSS'i bu adayla
ilgisizdir ve kullanılmaz. Sonuç bir olasılık terimi değildir. İstanbul için mutlak olasılık yazılmaz.
