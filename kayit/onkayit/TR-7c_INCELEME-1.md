# TR-7c bağımsız inceleme 1: ön kayıt taslağı (sürüm 1)

Tarih: 17 Kasım 2026. İncelenen: `TR-7c_tetiklenmis-tremor_ONKAYIT.md`, commit 4ba57ab (TASLAK, sürüm 1). İncelemeci
yazar değildir; amacı kusur bulmaktır.

Yöntem: yalnız depo dosyaları okundu ve yapay/kombinatorik hesap yapıldı.
- Hesap betiği: `kayit/turetme/tr7c/inc1/tr7c_inc1.py` (sha256 c809ce9755058fcba4f92c84cebf8e7cfadeb5cf055b8f0b8320e2e7499d58a8).
- Çıktı: `kayit/turetme/tr7c/inc1/tr7c_inc1.json` (sha256 4974dbe66163b49ba8c1b7dab699121c45cdce5aa1fba53c0cb1b0791d912974).
  Girdi dosyalarının sha256'ları json'un `girdi_sha256` alanındadır.
- Okunan dayanaklar: TR-7c_INCELEME-0 (Z1–Z8), `tr7c_guc.py/.json`, TR-7b taslağı (§2, §4–§7, §11–§12), TR-7b_SAYIM,
  TR-7 sürüm 3 (§5, §6, §7.1–§7.5, §8), `tr7_sonuc.md`, ESIK-DAYANAGI, ZINCIR Halka 11–13, `tr7b_yapay2.py` ve
  `tr7b_yapay.py`'nin K5 çağrı ağacı.

Hiçbir dalga formu indirilmedi ya da açılmadı, ağ isteği yapılmadı, 2026 ve sonrası veri kullanılmadı. Mevcut hiçbir
dosya değiştirilmedi. `tr7c_guc.py` yeniden üretim için modül olarak yüklendi, çıktısı depo dışına yazdırıldı. Maliyet 0 €.

## Hüküm: DÜZELTMEYLE KABUL

Taslak Z1–Z8'i birebir taşıyor (kodla denetlendi). Sayıları yeniden üretilebilir: `tr7c_guc.json` bayt bayt aynı çıktı.
Bağımsız hesabım altı güç hücresini, sızıntı satırlarını ve X_min tablosunu doğruladı. Hüküm dalları sırayla
uygulanınca bütün tamsayı ızgarasında boşluk bırakmıyor.

Taslak bu hâliyle dondurulmamalıdır. Altı noktada düzeltme gerekiyor:
1. **Genlik karıştırıcısı kapanmıyor.** Modülasyon şartı, sızıntı yüzey dalgasına kilitli değilse işe yarar.
   Tetikleyicinin yüzey dalgası genliğini izleyen tremor dışı bir 2–8 Hz sinyali bu sınamadan geçebilir. O biçimde
   D30M3'ün yanlış kabulü m_f 0,5'te 0,20–0,89'dur. Taslaktaki "≤ 0,01 / ≤ 0,06" yalnız kilitsiz sızıntı için
   geçerlidir. D2'nin yapay m_f ölçümü bu biçimi göremez, çünkü yapay telesismik zarfta yüzey dalgası periyodu yok.
2. **Körlük sızıntısı.** Tohoku duman sınaması metin dondurulmadan önce koşuluyor. Z7 yalnız K5'i ve Z3'ü korur. Öteki
   bütün "yazarın seçimleri" duman sonucu görüldükten sonra değiştirilebilir durumda.
3. **N 27 / N 28 aynı veriye bakıyor.** İki olayı ayrı saymak Fisher sınamasının bağımsızlık varsayımını bozar.
   Etkisi küçüktür, ama yönü belirsizdir; kural yazılmalı.
4. **Dal (e)'nin ikinci cümlesi (d) ile harfiyen çelişiyor.** En olası başarısızlık durumunda (X_P ≤ 2) iki farklı
   cümle yazdırıyor.
5. **Marmara cümlesinde iki iyimser tanım var.** (1 − ŝ)^n'nin üssü n_açık yerine n. A90 "belirsiz" olduğunda A90/A_PK
   oranının nasıl okunacağı yazılmamış.
6. **Sayı ve eşik hataları.** D1'in durma eşiği (3 başvuru istasyonlu P olayı) gücü 0,04–0,18'de bırakıyor. §7.4'ün
   q satırları s₀'da değil, s = 0,7'de hesaplanmış. K5'in sha denetimi çağrı ağacının yalnız bir dosyasını kapsıyor.

Hiçbiri fikrin özünü bozmuyor. Hepsi 0 € ile ve veri görülmeden düzeltilebilir. RET gerekmez.

## 1. Z1–Z8 ve yazarın seçimleri

**Z1–Z8 birebir.** `tr7c_inc1.py` `z_aynen` bölümü INCELEME-0 §6'daki her alıntı bloğunu, boşluklar normalleştirilerek,
ön kayıtta aradı. Z1, Z2, Z3, Z4, Z5, Z6 (ek kural), Z7 ve Z8 (düz cümle) birebir bulundu. Z6'nın ana cümlesi
(INCELEME-0 §4) de §6.2'de birebir yer alıyor. §14'teki eşleme tablosu doğru.

**Yazarın seçimleri:**

| Seçim | Savunulabilir mi | Sonuç görüldükten sonra serbestlik bırakıyor mu | Karar |
|---|---|---|---|
| Kör kontrolün adı K1c | evet | hayır | kabul |
| K5'in `tr7b_yapay2.py`'den içe aktarılması ve o dosyanın sha denetimi | ilke doğru, uygulama eksik | **evet, küçük.** `K5`, `tr7b_yapay.py`'nin `secili` ve `_k1_kalinti` işlevlerini ve `tr7_cekirdek.py`'nin `KSIG` sabitini çağırıyor. Yalnız `tr7b_yapay2.py`'nin sha'sı denetlenirse bu iki dosya değiştiğinde K5 sessizce değişir | **D-2** |
| N_PK < 5 → (ii) sağlanmaz | evet. Tutucu ve TR-7 §7.2'nin karşılığı. N_PK < 5'te MDA denemesi ≤ 12 olur (< 20), A90 "belirsiz" çıkar ve dal (e) işler. Tutarlı | hayır | kabul |
| ŝ'nin yanlış alarmdan arındırılması | evet. Tutucu: ŝ küçülür, (1 − ŝ)^n büyür. Fisher geçen her tabloda X_P/n_P > X_N/n_N (ızgarada 0 istisna), yani (b) dalında ŝ > 0 | hayır. Ama üs n'dir, n_açık olmalıdır (§6) | **D-6** |
| Önce 30 N, sonra 10 P | evet. N sonucu P görülmeden sabitlenir | durum dosyası ara sayıları gösterirse ara durdurma isteği doğabilir | Ö-b |
| Üstveri yoklamasının dondurmayı durdurması | evet. Karar yalnız üstveriye dayanır, sonuca dayanmaz; kör olayları korur | eşik çok gevşek: k = 3 başvuru istasyonlu P olayıyla koşu yapılır, gücü 0,18 / 0,04 olur (§8) | **D-5** |
| m_f > 0,10 ise incelemeye geri dönüş | ilke doğru | ölçüm yöntemi bu kuralı neredeyse hiç tetikleyemez. K5'ten sağ çıkan Y2 kümesi 100 pencerede 0–2 tanedir. Y2/Y3 zarfında yüzey dalgası periyodu yoktur (§5) | **D-4** |
| Tohoku duman sınamasının yeri (kod incelemesinden önce) | kod incelemesinden önce olması doğru | **evet.** Metin o anda dondurulmamış. Duman sonucu (K5 bayrakları, sağ kalan Tohoku kümeleri, varsa modülasyon p'si) görüldükten sonra Z7'nin korumadığı her seçim değiştirilebilir: A_PK, ŝ, n, N 27/28, D1 eşiği, (c)'de hata yolunun olmaması | **D-3** |
| (c)'de uygulama hatası yolunun olmaması | evet | hayır | kabul |
| Parkfield üreteç sırası (`default_rng(20261112 + 3)`, T0 ve I′ sırası) | evet | hayır | kabul |
| A_PK = olay başına en büyük küme, olaylar arası medyan | TR-7 §7.5 aynen | yukarı yanlı: en büyük küme seçiliyor ve P'deki yanlış alarmlar da içeride. A90/A_PK ≤ 1 böylece kolaylaşır | Ö-a |
| N 27 ve N 28'in ayrı sayılması | hayır (§4) | yönü belirsiz bir bağımlılık bırakır | **D-1** |

Ek bulgu (dal değiştirmez; doğrulanamadı). K5'in Q referansı küçük tetikleyicilerde çoğunlukla kurulmaz: Q'da
L_d − m_d > 4σ_d olan saniye sayısı 30'un altında kalır. O zaman K5, N olaylarında yalnız "Δ_d ≥ Δ_y ve ρ ≤ −0,7" ile
bayraklar. P olaylarında kalıntı şartı da çalışır. Sızıntı bu yüzden P'de N'den daha çok silinir. Bu, sızıntıdan
doğan "sınandı" için tutucu yöndür. Gerçek veride Q doğrusunun hangi olaylarda kurulduğu bilinmiyor (Ö-h).

## 2. Hüküm dalları: bütün ızgara

`tr7c_inc1.py` `dal_izgarasi` bölümü bütün tamsayı ızgarasını dolaştı:
- n_P 0–10, X_P ≤ n_P;
- n_N 0–30, X_N ≤ n_N;
- N_PK 0–120, f_PK ≤ N_PK;
- M_ölç (modülasyonu ölçülebilen, algılama veren P olayı) ≤ X_P, M_mod ≤ M_ölç;
- "MDA tanımlı" ve "A90_PK ≤ 100 µm/s" ikili.

Toplam 14 658 547 904 nokta. Her noktada Z3 (i)–(iv) ve Z4 şartları harfiyen hesaplandı (Fisher: kendi
hipergeometrik uygulamam; X_min: TR-7 §8).

**Sırayla (Z4 "sıra bağlayıcı"):** Her nokta tam olarak bir dala düşer. Hiçbir dala düşmeyen nokta 0.
- (a) 8 992 715 160
- (b) 301 929 064
- (c) 838 032 616
- (d) 1 079 879 658
- (e) 3 445 991 406

**Sırasız okunursa** (a) ile (b), (c) ve (d) çakışır. Z4 (b), (c) ve (d)'de "n_P ≥ 8, n_N ≥ 20" yazmıyor. Sıra kuralı
bunu çözer. Kusur değildir.

**Gerçek belirsizlik.** Z4 (e)'nin ikinci cümlesi şöyledir: "Modülasyonun ölçülebildiği algılama veren P olayı
3'ten azsa … dal (e)'dir". Bu cümle bir tanım olarak yazılmış, sıra şartı taşımıyor.
- (d) ile çelişen nokta sayısı 277 722 588'dir. Bu noktalarda sıra (d)'yi seçer, cümle ise "dal (e)" der. Örnek:
  n_P 8, X_P 0, n_N 20, X_N 0, MDA tanımlı, A90 uygun. Hiç algılama yoksa M_ölç = 0 < 3'tür. Yani en olası başarısızlık
  durumunda (X_P ≤ 2) metin iki ayrı cümle yazdırıyor: "ölçütü karşılamadı" ve "modülasyon ölçülemedi".
- (a) ile çelişen nokta sayısı 3 237 011 360'tır. Burada (a) önce geldiği için daha az zararlıdır, ama aynı türdendir.

Düzeltme: **D-7**.

Tanımı yazılı olmayan iki uç durum var:
- X_min(n_P, f_PK) "yok" (TR-7 §8: X ∈ [2, n] arasında şartı sağlayan yok). Bu durumda (i) sağlanmamış sayılmalıdır.
  Betik böyle saydı.
- A90_PK "belirsiz" (< 20 deneme) ya da "> 100 µm/s". Bu durumda (d)'nin A90 şartı sağlanmamış sayılmalı ve dal (e)
  işlemelidir.

İkisi de D-7'de yazılır.

## 3. Güç ve yanlış kabul sayılarının yeniden üretimi

**Yeniden üretim.** `tr7c_guc.py` (sha256 f9c9289a…e39b) değiştirilmeden yüklendi ve `main()` yeniden koşuldu. Çıktısı
depo dışına yazdırıldı. Yeni json'un sha256'sı e225b0e67cdd…5427'dir, yani depodakiyle bayt bayt aynı.

**Bağımsız hesap** (kendi kodum; `tr7c_guc.py`'den hiçbir işlev kullanılmadı):

| Denetim | Yöntem | Sonuç |
|---|---|---|
| Clopper–Pearson üst sınırı | ikiye bölme, P(Bin(N, p) ≤ f) = 0,05 | scipy `beta.ppf` ile en büyük fark 3,9·10⁻¹⁵. X_min(10, f) tablosu (f 0–40) birebir aynı |
| Fisher tek yanlı | lgamma ile hipergeometrik üst kuyruk | scipy `fisher_exact(greater)` ile en büyük fark 3,6·10⁻¹⁴. Örnek: 9/10'a karşı 0/2 → 0,04545 |
| D30M3, m_t 0,8, s 0,7, q 0,1 | kendi tam sayım | 0,9487 (ön kayıt 0,95) |
| aynı | Monte Carlo, 100 000 tekrar | 0,9508 ± 0,0007 |
| D30M3, m_t 0,5, s 0,7, q 0,1 | tam sayım | 0,7301 (0,73) |
| D30M3, m_t 0,8, s 0,5, q 0,2 | tam sayım | 0,5085 (0,51) |
| D30M3, m_t 0,5, s 0,9, q 0,3 | tam sayım | 0,4850 (0,49) |
| D30M3, m_t 0,8, s 0,3, q 0,05 | tam sayım | 0,1939 (0,19) |
| D30M3, m_t 0,5, s 0,5, q 0,05 | tam sayım | 0,4159 (0,42) |
| Genliğe bağlı sızıntı, m_f 0,05; v0 0,01 / 0,03 / 0,1 | Poisson-ikiterimli, Chao PGV_T | 0,0101 / 0,0062 / 0,0006 (0,010 / 0,006 / 0,001) |
| Aynısı, m_f 0,10 | aynı | 0,0622 / 0,0400 / 0,0044 (0,062 / 0,040 / 0,004) |
| Ayırt etmeyen algılayıcı, D30M3, t 0,3 / 0,5 / 0,7 / 0,9 | tam sayım | 6,6·10⁻⁵ / 1,7·10⁻⁴ / 1,8·10⁻⁴ / 1,8·10⁻⁶ (ön kayıt "≤ 0,0002": doğru) |

§7.2'nin 32 hücresi ve §7.3'ün 24 hücresi `tr7c_guc.json` ile yuvarlamada uyuşuyor.

Kaynak notu: `tr7c_guc.json` ayırt etmeyen algılayıcı için D30M3'ü yalnız t = 0,7'de veriyor
(`D30M3_olay_sayisi`). t 0,3 / 0,5 / 0,9 değerleri orada D30M (⌈X_P/2⌉) içindir. Ön kayıttaki "≤ 0,0002" yargısı
doğru, ama dayanağı `tr7c_inc1.json` `bagimsiz.ayirt_etmeyen_D30M3_kendi` olarak gösterilmelidir (Ö-g).

**Hatalı satırlar (§7.4):**
- Tablonun başlığı "m_t 0,8 (s₀ ≈ 0,57)" ve "m_t 0,5 (s₀ ≈ 0,77)". Ama q ×0,5 / ×2 satırları s = 0,7'deki değerler
  (0,95 / 0,86 ve 0,73 / 0,68). s₀'da doğru değerler: m_t 0,8'de 0,79 / 0,65; m_t 0,5'te 0,81 / 0,78.
- "s ×0,5, m_t 0,5: güç ≈ 0,1–0,4" yazılmış. Kesin değer 0,23.
- "s ×2, m_t 0,5: güç ≈ 0,9" yazılmış. s 1'de kırpılınca kesin değer 0,95.

Düzeltme: **D-8**.

## 4. N 27 / N 28 (2009-10-07 Vanuatu)

`cift_N27_N28` bölümünün sonuçları (T0 ve Δ `tr7b_sayim.json`'dan; P ve S varışları ezber iasp91 tablosundan kaba ara
değerleme, **doğrulanamadı**):

| | N 27 | N 28 |
|---|---|---|
| T0 | 22:03:14 | 22:18:51 (15,6 dk sonra) |
| W | 22:34:29–23:09:03 | 22:50:02–23:24:32 |
| K1b aralığı | 22:37:13–22:55:20 | 22:52:45–23:10:49 |
| Kaba P / S | 22:15:41 / 22:26:05 | 22:31:17 / 22:41:40 |

- W örtüşmesi 1142 sn; K1b aralıkları 156 sn örtüşüyor.
- N 27'nin W'si, N 28'in Q referans aralığının (≈ 22:31–22:50) 932 saniyesini kapsıyor. Yani N 28'de K5'in Q doğrusu,
  N 27'nin yüzey dalgaları sırasında kuruluyor.
- N 27'nin T0'ı N 28'in R'sinin içinde.
- Chao 2012 S1'de iki satırın PGV_T'si aynı: 0,0095 cm/s. Bu, iki satırın aynı kayıttan ölçüldüğünü düşündürüyor
  (çıkarım, **doğrulanamadı**).
- 43 olayın hepsi tarandı. Pencereleri başka bir olayın R'sine ya da W'sine taşan tek çift budur.

**Bağımsızlık bozuluyor mu?** Evet. İki satır büyük ölçüde aynı veri parçasının iki okumasıdır. Fisher sınaması 30
bağımsız N gözlemi varsayar. Hatanın yönü sonuca bağlıdır:
- İkisi birlikte algılama vermezse n_N bir fazla "temiz" gözlem kazanır. Bu yanlış kabul yönündedir.
- İkisi birlikte algılama verirse X_N iki kez artar. Bu tutucu yöndedir.

Yazarın seçtiği "ayrı say, N 28'siz satırı bilgi olarak yaz" çözümü, dalın hangi sayımla verileceğini değiştirmez. Ama
bilgi satırı dalla çelişirse hangisinin doğru olduğunu söylemez.

**Etki** (`etki` ve `fisher_esik` alanları):
- Fisher'de izin verilen en büyük X_N, n_N 30'dan 29'a inince X_P = 5 / 7 / 8 / 9 için birer azalır (5→4, 10→9,
  13→12, 16→15). X_P = 6 ve 10'da değişmez.
- Güç (s 0,7, q 0,1, m_t 0,8): bağımsız 30 → 0,9487; çift tam bağımlı ama iki kez sayılırsa 0,9479; tek birim (29)
  → 0,9433.
- Kilitli sızıntıda yanlış kabul (v0 0,01, m_f 0,5): 0,8865 / 0,8834 / 0,8736.

Etki küçüktür (güçte ≤ 0,006, yanlış kabulde ≤ 0,013), ama kural bugün yazılmalıdır. Önerim, TR-7'nin Wharton birimi
örneğiyle çifti tek birim saymak: **D-1**.

## 5. Genlik karıştırıcısı: modülasyon şartı yeterli mi?

**Ne kırar, ne kırmaz.** TR-7 §6.4 ölçüsü faz kilidini değil, **yüzey dalgasıyla eş periyotlu modülasyonu** ölçer.
20 sn periyotlu ama kilitsiz tremorda bile %33–56 oranında p ≤ 0,01 verir.
- **Kırdığı biçim:** zarfı yüzey dalgasından bağımsız olan sızıntı. Örnekler: telesismik koda, artçı P'leri, bölgesel
  koda, kentsel gürültü. Bunlar için m_f küçüktür; TR-7 yapay sınamasında sabit ve patlamalı tremor 0,00 verdi.
- **Kırmadığı biçim:** 2–8 Hz zarfı tetikleyicinin yüzey dalgası genliğini izleyen tremor dışı bir sinyal. Bu sinyal
  tanım gereği eş periyotlu modüledir (m_f ≈ 1) ve genliğe bağlıdır. Fiziksel adaylar:
  - aletsel doğrusalsızlık;
  - dinamik tetiklenmiş yerel ya da bölgesel mikrodepremler. Örnek: Peng 2010'un Maule'de bildirdiği, Coso'nun
    bölgesel tetiklenmiş depremleri (SAYIM §1). Darbe kuralı ancak tek tek ayrışan olayları atar.

**Sayılar** (`kilitli_sizinti.yanlis_kabul_s0`; tremor yok, q(v) = 1/(1 + (v0/v)²), m_f değişken):

| m_f | v0 0,01 | v0 0,03 | v0 0,1 |
|---|---|---|---|
| 0,05 (ön kayıt) | 0,010 | 0,006 | 0,001 |
| 0,10 (ön kayıt) | 0,062 | 0,040 | 0,004 |
| 0,3 | 0,564 | 0,446 | 0,074 |
| 0,5 | 0,887 | 0,835 | 0,204 |
| 0,8 | 0,947 | 0,988 | 0,343 |

Ön kayıttaki "D30M3'ün genliğe bağlı sızıntıda yanlış kabulü ≤ 0,01 ya da ≤ 0,06" cümlesi **yalnız m_f ≤ 0,10 iken**
doğrudur. Kilitli sızıntı biçiminde m_f'nin değeri bilinmiyor (**doğrulanamadı**). Bunu ölçecek 0 €'luk bir yol da yok.

**D2 bunu ölçemez.** D2, m_f'yi Y2/Y3 yapay satırlarının sızıntı kümelerinde ölçüyor. O satırların telesismik zarfı
şunlardan oluşur: 150 sn'de sönen koda, 0,1 taban ve artçı P darbeleri (TR-7b §5). İçinde yüzey dalgası periyodu
yoktur. Bu ölçüm yalnız kırılan biçimin m_f'sini verir. Ayrıca K5'ten sağ çıkan Y2 kümesi 100 pencerede 0–2'dir
(TR-7b §11.4), yani tahmin bir avuç kümeye dayanır. "m_f > 0,10 → geri dönüş" kuralı bu yüzden pratikte tetiklenemez.
Düzeltme: **D-4**.

**TR-7'nin Tohoku sonucu ne söylüyor?** Üç şey:
1. Büyük bir tetikleyici sırasında Parkfield yüzey ağında W boyunca iki bant birlikte yükseliyor: Δ_y 0,4–0,8 ve
   Δ_d 0,57–1,21 (TR-7b §2). Bu yükselmeler 10 istasyonda tutarlı küme kuruyor (44 ve 40 çift). Saf telesismik P
   aralığı da 10 istasyonlu küme kurdu. Yani genliğe bağlı, ağ çapında tutarlı, tremor olması gerekmeyen 2–8 Hz
   artışı bu ağda gerçektir.
2. Dört kümenin hiçbiri ayıklamadan sağ çıkmadı. Modülasyon ölçüsü hiçbirinde hesaplanmadı ("Parkfield modülasyonu
   geçmedi" = ölçülemedi). Tohoku bu yüzden ne m_t ne de m_f hakkında bir şey söyler.
3. K1–K3 ilk üç kümeyi korur (TR-7b §4.5). K5 Tohoku'da hiç hesaplanmadı; kalıntı bileşeni K1'inkiyle aynıdır, ρ
   bileşeninin bu kümelerde ne vereceği **doğrulanamadı**. Bu kümelerin tremor mu (Hill 2013)
   yoksa genliğe bağlı sızıntı mı olduğu gösterilemedi. Bu tam olarak D30M3'ün çözmesi beklenen karıştırıcıdır. Tohoku,
   sorunun bu ağda var olduğunu gösterir, çözüldüğünü göstermez.

**Genliği eşlenmiş 4 negatif bağlayıcı olmalı mı?** Evet, ama dal şartı olarak değil, **Marmara "VAR"ını engelleyen
bir etiket** olarak. Gerekçe aşağıdaki iki tablodadır.

Kural G1: PGV_T ≥ 0,02 olan 4 N olayının **en az birinde** modülasyonlu (p ≤ 0,01) algılama varsa etiket yazılır.
Karşılaştırma için G2: en az ikisinde.

Tablo 1. Kilitli sızıntıda "sınandı ve etiket yok" olasılığı (`kilitli_sizinti.yanlis_kabul_s0`):

| m_f | v0 | D30M3 | D30M3 + G1 | D30M3 + G2 |
|---|---|---|---|---|
| 0,3 | 0,01 / 0,03 / 0,1 | 0,56 / 0,45 / 0,07 | 0,16 / 0,23 / 0,06 | 0,40 / 0,40 / 0,07 |
| 0,5 | 〃 | 0,89 / 0,83 / 0,20 | 0,09 / 0,25 / 0,16 | 0,36 / 0,62 / 0,20 |
| 0,8 | 〃 | 0,95 / 0,99 / 0,34 | 0,007 / 0,11 / 0,23 | 0,07 / 0,46 / 0,33 |

Tablo 2. Gerçek tremorda etiketin bedeli, yani "sınandı" iken etiket yazılma olasılığı
(`gercek_tremorda_etiket_bedeli`). Temiz negatifte (π = 0):
- G1: 0,013–0,019;
- G2: 0,0001.

Kirli negatifte (4 olayın her birinde 0,4 olasılıkla gerçek zayıf tremor):
- G1: 0,33–0,60;
- G2: 0,07–0,21.

Okuma:
- G1, v0 ≤ 0,03 olan kilitli sızıntıyı büyük ölçüde yakalar. v0 = 0,1'i yakalayamaz: sızıntı yalnız çok büyük
  tetikleyicide başlıyorsa, genliği eşlenmiş negatiflerin genliği (≤ 0,062) yetmez.
- G1'in bedeli yalnız kirli negatifte büyüktür. O durumda da yalnız "VAR"ı engeller, yani tutucudur.
- Bu yüzden G1 dal şartı değil, etiket olmalıdır. Dal şartı olursa, kirli negatif varken gücün %33–60'ını yer.
- Kalan açık (v0 büyük, m_f büyük) 0 € ile kapatılamaz. "Sınandı"nın okunuşuna yazılmalıdır.

Düzeltme: **D-9**.

## 6. Marmara tarafı

- **Dallar.** TR-7b §7 aynen, TR-7 §8 sırasıyla. Tutarlıdır. "VAR"ın üç şartı (K1c "belirsiz" değil, "Parkfield
  modülasyonu geçti", TR-7 §8 sıra 5) TR-7 özet tablosuyla uyuşuyor.
- **(1 − ŝ)^n'nin üssü.** TR-7 §8 dışlama cümlesini n_açık ile kurar, yani W'sinin en çok yarısı maskeli birimlerle.
  Gerekçesi şudur: MDA'nın ölçüldüğü negatif pencerelerde E1 neredeyse yoktur, bu yüzden çok maskeli bir birim A90
  duyarlılığıyla taranmış sayılmaz. Taslak üssü n (bütün K0-tam ana birimler) alıyor. TR-7 önsayımında S1–S3'te
  n_açık 8 / 7 / 7 iken segment başına n 9–12'dir. n'yi üs almak hiç görülmeme olasılığını olduğundan küçük gösterir, yani yanlış kabul yönündedir.
  **D-6.**
- **A90/A_PK'nın tanımsız olduğu durumlar.** A90(S_k) "belirsiz" (< 20 deneme) ya da "> 100 µm/s" olabilir. A_PK = 0
  da olabilir: kestiricide max(0, ·) var. Bu durumlarda oranın nasıl okunacağı yazılmamış. Tutucu okuma "> 1"dir, yani
  Z6 eki bağlayıcı olur. **D-6.**
- **A_PK yukarı yanlı.** Olay başına en büyük küme alınıyor ve P'deki yanlış alarm kümeleri de içeride. Bu, A90/A_PK ≤ 1
  yargısını kolaylaştırır. TR-7 §7.5 aynen olduğu için zorunlu düzeltme yazmıyorum (Ö-a).
- **K1c (b) iken "Parkfield modülasyonu geçti" sağlanmayabilir.** Z3 (iv) "≥ 3" ister, etiket "≥ ⌈X_P/2⌉" ister; X_P ≥ 7
  iken ikisi ayrılır. Hesap (`marmara_etiket`): (b) gerçekleştiğinde etiketin sağlanmama olasılığı m_t 0,8'de 0,02,
  m_t 0,5'te 0,30 (s 0,7) ve 0,38 (s 0,9).
  - Bu bir geçerlilik sorunu değildir; tutucudur. TR-7'de "ayırt edici değil" etiketi de Marmara'yı açıp yalnız "VAR"ı
    engelliyordu.
  - Ama bir bedeli var: m_t düşükse Marmara'nın tek kullanımlık kör verisi, olası en güçlü sonucu "aday" olan bir
    taramada harcanır. Taslak bunu "yeni kural değildir" diye geçiyor; olasılığı yazılmalı ve K1c satırında, Marmara
    indirilmeden önce görünmelidir. **D-10.**
- **Boş tarama cümlesi.** Z6 ve ekiyle tutarlıdır. "Bu cümle deprem olasılığı hakkında hiçbir şey söylemez" kalıbı yerinde.

## 7. Körlük ve koşu sırası

- **Üstveri yoklaması (§8):** station, availability ve katalog kullanılıyor. Dataselect yok, W içeriği yok. Sızıntı yolu
  görmüyorum. Availability boşlukları güçlü sarsıntıdaki telemetri kesintisiyle ilişkili olabilir, ama bu tremor
  çıktısı hakkında bilgi vermez.
- **Tohoku duman sınaması:** yeni bilgi Tohoku'dandır ve Tohoku geliştirme verisidir. Kör olaylara veri sızmaz. Ama
  metin dondurulmadan görülür. Z7'nin korumadığı her karar, duman sonucuna bakılarak değiştirilebilir. Asıl sızıntı yolu
  budur. **D-3.**
- **Rastgele negatif pencereler:** TR-7 §7.3 (i), kaydırılmış pencerede M ≥ 6,5 olay bulunmasını yasaklıyor. Kör
  olayların hepsi Mw ≥ 7,5 olduğundan hiçbir rastgele pencere bir kör olayın W'sine düşemez. Sızıntı yok.
- **N, sonra P:** TR-7 §10.6'nın tek koşu kuralı işliyor. Ama durum dosyası her aşamada commit ediliyor. Algılama
  sayıları orada görünürse, P aşamasından önce "yöntem hatası" gerekçesiyle durma isteği doğabilir (Ö-b).
- **Ham günlükler (D8):** kod incelemecisine bırakılmış. Uygun. Bu inceleme de günlükleri açmadı: **doğrulanamadı**.
- **Marmara:** dokunulmamış. Yalnız K1c (b) dalında açılıyor. Körlük tam.

## 8. ESIK-DAYANAGI kuralı

| Öğe | Taslakta | Denetim |
|---|---|---|
| Görülebilir en küçük etki | s₀ ≈ 0,57 (m_t 0,8) / 0,77 (m_t 0,5), q 0,1 | doğru (kendi hesabım: 0,57 / 0,77; güç 0,802 / 0,805) |
| Kaynak | "tahmin / bizim seçimimiz"; literatürden değer yok | doğru ve dürüst |
| s ×0,5 | 0,2 / "0,1–0,4" | 0,20 / **0,23** |
| s ×2 | ≈ 1 / ≈ 0,9 | 1,00 / **0,95** (s 1'de kırpılmış) |
| q ×0,5 / ×2 | s 0,7'deki değerler yazılmış | s₀'da: **0,79 / 0,65** (m_t 0,8), **0,81 / 0,78** (m_t 0,5) |
| m_t ×0,5 (varsayım duyarlılığı) | yok | s₀'da 0,39 (m_t 0,8 → 0,4) / 0,30 (m_t 0,5 → 0,25) |
| Dal (a) sınırında MDE | yalnız güç (0,86 / 0,55) | n_P 8, n_N 20: s₀ = **0,66 / 0,93** |
| Olumsuz sonucun "ayırt edilemez (MDE)" diye okunması (Halka 13) | Z5'te genel cümle var; (c), (d), (e) hüküm cümlelerinde yok | eksik |
| ESIK-DAYANAGI.md'de TR-7c satırı | yok | eksik (Ö-f; o dosyayı bu inceleme değiştirmez) |

Gerçekleşen n'lerle MDE tablosu (q 0,1; `esik.MDE_tablosu_q0.1`; m_t 0,8 / 0,5):

| n_P \ n_N | 20 | 24 | 29 | 30 |
|---|---|---|---|---|
| 10 | 0,60 / 0,78 | 0,59 / 0,77 | 0,58 / 0,77 | 0,57 / 0,77 |
| 9 | 0,64 / 0,84 | 0,63 / 0,84 | 0,63 / 0,84 | 0,63 / 0,84 |
| 8 | 0,66 / 0,93 | 0,65 / 0,93 | 0,64 / 0,93 | 0,64 / 0,93 |

D1 eşiği için, başvuru istasyonu olan P olayı sayısı k'ya göre güç (s 0,7, q 0,1; `esik.D1_kref_guc_s0.7_q0.1`; m_t 0,8 / 0,5):

| k | 3 | 4 | 5 | 6 | 7 | 8 | 10 |
|---|---|---|---|---|---|---|---|
| güç | 0,18 / 0,04 | 0,41 / 0,13 | 0,61 / 0,24 | 0,75 / 0,35 | 0,85 / 0,47 | 0,90 / 0,57 | 0,95 / 0,73 |

## 9. Zorunlu düzeltmeler (ön kayda aynen girecek cümleler)

**D-1 – 2009-10-07 çifti tek birim** (§3.2'deki "yazarın seçimi" maddesinin yerine):
> "N 27 (2009-10-07 22:03) ile N 28 (2009-10-07 22:18) tek bir N birimidir ('Vanuatu 2009 birimi'; TR-7'nin Wharton
> birimi örneği). Birimin W'si [N 27'nin W başı, N 28'in W sonu], K1b aralığı [N 27'nin K1b başı, N 28'in K1b sonu]'dur;
> R ve Q N 27'ninkidir. E1'de birimin tetikleyicisi N 27'dir; N 28 'öteki olay' olarak M ≥ 7,0 kuralıyla (P ve S,
> 240 sn) maskelenir. Birim, birleşik K1b aralığıyla kesişen ve ayıklamadan sağ çıkan en az bir küme varsa algılama
> verir. n_N ve X_N'de birim bir kez sayılır; n_N en çok 29'dur. Z2'nin olay listesi ve dal (a)'nın n_N < 20 sınırı
> değişmez. Bilgi satırı (dalı değiştirmez): iki olay ayrı sayılarak hesaplanan Z3 (iii)."

**D-2 – K5'in bütün çağrı ağacı** (§4.2 "Uygulama" paragrafına):
> "Koşu kodu başlangıçta K5'in çağırdığı her dosyanın sha256'sını denetler: `kayit/turetme/tr7b/tr7b_yapay2.py`
> (ae995ba8802a934577cbf26051229360bcfb1a85d5d4d7dc16d358dfeaef437f; `K5`, `_rho`, `_delta`),
> `kayit/turetme/tr7b/tr7b_yapay.py` (e92715318e21a0200b66e3c130853f73cbc382b0398aef561619fcbe1bb74374; `secili`,
> `_k1_kalinti`) ve `kayit/turetme/tr7/tr7_cekirdek.py` (4a1b9131603d0f3d519cacb183fdbcccc106157b66392bf2d09350c9f49206f6;
> `KSIG`). Biri uyuşmazsa hiçbir şey hesaplanmadan durur. Bağımsız kod incelemesi K5'in çağrı ağacında başka dosya
> olmadığını doğrular."

**D-3 – Karar metni, duman sınamasından önce dondurulur** (§10'a, adım 1 ile adım 2 arasına):
> "Karar metni dondurması: §8'in üstveri yoklamaları bittikten sonra, §10 adım 2'deki m_f ölçümünden ve adım 3'teki
> Tohoku duman sınamasından önce, bu metin 'Durum: KARAR METNİ DONDURULDU' satırıyla commit ve push edilir; sha256'sı
> deftere yazılır. Bundan sonra yalnız şunlar değişebilir: §8 yoklamalarının sayıları (n_P, n_N kestirimi, başvuru
> istasyonlu P olayı sayısı k), koşu kodunun okuma ve ayrıştırma katmanı ('duman sonrası düzeltme') ve bağımsız kod
> incelemesinin dal, eşik, olay listesi, birim, A_PK, ŝ ve n tanımlarına dokunmayan düzeltmeleri. Bu tanımlara dokunan
> her değişiklik yeni bir bağımsız metin incelemesi ister. Tohoku duman sınamasının sonucu hiçbir 'yazarın seçimi'ni
> değiştirmez."

**D-4 – D2'nin m_f ölçümü ve kapsamı** (§8 D2 satırının "Koşudan önce 0 € yoklama" ve "sonuç" hücrelerine; §5 "Neden D30M3"
listesinin üçüncü maddesine eklenir):
> "m_f, §10 adım 2'de Y2 ve Y3 satırlarında ayıklamadan önce algılanan bütün kümelerde, K5'ten sağ çıkıp çıkmadığına
> bakılmadan, TR-7 §6.4 ölçüsüyle ölçülür (en az 100 küme; daha azsa pencere sayısı artırılır); K5'ten sağ kalanlardaki
> pay ayrıca yazılır. Ölçülen m_f > 0,10 ise taslak bağımsız incelemeye döner. Bu ölçüm yalnız yüzey dalgasına kilitli
> olmayan sızıntıyı kapsar: Y2/Y3'ün telesismik zarfında yüzey dalgası periyodu yoktur. 2–8 Hz zarfı tetikleyicinin
> yüzey dalgası genliğini izleyen tremor dışı bir sinyal için m_f tanım gereği 1'e yakındır; bu biçimde D30M3'ün yanlış
> kabulü m_f 0,3'te 0,07–0,56, m_f 0,5'te 0,20–0,89'dur (`kayit/turetme/tr7c/inc1/tr7c_inc1.json`
> `kilitli_sizinti`). '≤ 0,01 ya da ≤ 0,06' değerleri yalnız kilitli olmayan sızıntı için geçerlidir."

**D-5 – D1'in durma eşiği** (§8 D1 satırının "sonuç" hücresindeki "3'ten azsa" yerine):
> "Başvuru istasyonu olan (TR-7 §6.6; W ve R örtüsü ≥ %90) P olayı sayısı k < 7 ise TR-7c dondurulmaz ve kör koşu
> yapılmaz; kayda 'modülasyon şartı için yeterli başvuru istasyonu yok (k = [..]), kör olaylar harcanmadı' yazılır.
> Gerekçe: s 0,7, q 0,1'de D30M3'ün gücü k = 7'de 0,85 / 0,47, k = 6'da 0,75 / 0,35, k = 3'te 0,18 / 0,04'tür
> (m_t 0,8 / 0,5; `tr7c_inc1.json` `esik.D1_kref_guc_s0.7_q0.1`). k ≥ 7 ise k ve k ile hesaplanan görülebilir en küçük
> s §7'ye yazılır."

**D-6 – Z6 cümlesinin köşeli yerleri** (§6.2 "Yazarın seçimleri" listesindeki "n" maddesinin yerine):
> "Z6 cümlesindeki (1 − ŝ)^n, segmentin n_açık'ıyla (TR-7 §8: taranan ana birimlerden W'sinin maskeli payı ≤ 0,50
> olanlar) hesaplanır ve '(1 − ŝ)^n = [..]' yerine '(1 − ŝ)^n_açık = [..] (n_açık = [..])' yazılır. n_açık < 5 ise bu
> yan cümlenin yerine 'hiç görülmeme olasılığı hesaplanmadı (n_açık < 5)' yazılır. A90(S_k) 'belirsiz' ya da
> '> 100 µm/s' ise ya da A_PK = 0 ise A90(S_k)/A_PK > 1 sayılır ve Z6 eki bağlayıcıdır."

**D-7 – Dal (e)'nin okunuşu ve uç durumlar** (§6.1'de Z4 alıntısının hemen altına; Z4'ün metni değişmez):
> "Okuma kuralı (bağlayıcı): Z4 (e)'nin ikinci cümlesi ('Modülasyonun ölçülebildiği algılama veren P olayı 3'ten azsa …
> dal (e)'dir') yalnız (a) sağlanmıyorsa ve Z3 (i) ile (ii) sağlanıyorsa uygulanır; (i) ya da (ii) sağlanmıyorsa sıra
> (d) ve (e)'nin birinci cümlesidir. X_min(n_P, f_PK) yoksa (TR-7 §8) (i) sağlanmamış sayılır. A90_PK 'belirsiz' ya da
> '> 100 µm/s' ise (d)'nin A90 şartı sağlanmamış sayılır."

**D-8 – Duyarlılık tablosu ve olumsuz sonucun MDE'si** (§7.4 tablosunun yerine ve §6.1'deki (c), (d), (e) cümlelerine):
> "×0,5 / ×2 duyarlılığı s₀'da (q 0,1; `kayit/turetme/tr7c/inc1/tr7c_inc1.json` `esik`): m_t 0,8 (s₀ 0,57): s ×0,5 →
> 0,20; s ×2 (1'de kırpılmış) → 1,00; q ×0,5 → 0,79; q ×2 → 0,65; m_t ×0,5 → 0,39. m_t 0,5 (s₀ 0,77): s ×0,5 → 0,23;
> s ×2 → 0,95; q ×0,5 → 0,81; q ×2 → 0,78; m_t ×0,5 → 0,30. Dal (a) sınırında (n_P 8, n_N 20) görülebilir en küçük s
> 0,66 (m_t 0,8) / 0,93 (m_t 0,5)'tir."
>
> "(c), (d) ve (e) cümlelerinin sonuna '(ayırt edilemez: gerçekleşen n_P, n_N ile, q 0,1'de görülebilir en küçük
> s = [..] (m_t 0,8) / [..] (m_t 0,5))' eklenir. Değerler `tr7c_inc1.json` `esik.MDE_tablosu_q0.1`'den okunur;
> tabloda olmayan n'ler için aynı işlevle (`tr7c_inc1.py` `esik`) koşudan önce hesaplanıp dondurulur."

**D-9 – Genliği eşlenmiş negatif etiketi ve "sınandı"nın okunuşu** (§5 "Yazarın seçimleri"ne yeni madde; §6.2 "VAR"
şartlarına ek):
> "Genlik etiketi (bağlayıcı; dal değiştirmez): PGV_T ≥ 0,02 cm/s olan 4 N olayının (Macquarie 2004, Nias 2005,
> Solomon 2007, Peru 2007) en az birinde, K1b aralığıyla kesişen ve ayıklamadan sağ çıkan bir kümede TR-7 §6.4
> modülasyon ölçüsü (P olaylarındaki başvuru istasyonu tanımı ve boş dağılımla) p ≤ 0,01 verirse K1c satırına 'genlik
> karıştırıcısı dışlanmadı' yazılır. Etkisi: Marmara'da 'VAR' verilemez, en çok 'aday'. Modülasyonu ölçülemeyen olay
> etiketi tetiklemez; bu 4 olayda ölçülemeyen olay sayısı K1c satırına yazılır. Üreteç sırasında bu 4 olayın kümeleri
> N olaylarıyla birlikte, T0 sırasıyla işlenir."
>
> "'Ölçü sınandı' şu demektir: algılayıcı, Chao etiketini yüzey dalgasıyla eş periyotlu modülasyon taşıyan bir sinyalle,
> FAR ve Fisher şartları içinde kör olarak yeniden üretiyor. Tetikleyicinin yüzey dalgası genliğini izleyen tremor dışı
> bir 2–8 Hz sinyali (aletsel doğrusalsızlık, dinamik tetiklenmiş yerel ya da bölgesel mikrodepremler) bu sınamadan
> geçebilir. Bu biçim yalnız 4 genliği eşlenmiş negatifle ve kısmen sınanır. Marmara 'VAR' kalıbının sonuna '(Parkfield
> kör kontrolü genliğe bağlı, yüzey dalgasına kilitli sızıntıyı yalnız 4 genliği eşlenmiş negatifle sınadı)' eklenir."

**D-10 – (b) iken modülasyon etiketi yoksa** (§5 "Yazarın seçimleri" madde 5'in sonuna):
> "K1c (b) sağlanır ama 'Parkfield modülasyonu geçti' sağlanmazsa, K1c satırı Marmara indirilmeden önce 'ölçü sınandı
> (Parkfield modülasyonu geçmedi: Marmara'da en çok \"aday\")' diye yazılır ve Marmara aşamaları açılır. Bu durumun
> (b) içindeki olasılığı m_t 0,8'de ≈ 0,02, m_t 0,5'te ≈ 0,30–0,38'dir (`tr7c_inc1.json` `marmara_etiket`); o durumda
> Marmara'nın kör verisi en çok 'aday' verebilecek bir taramada harcanır."

## 10. Öneriler (bağlayıcı değil)

- **Ö-a:** A_PK'nın yanına iki bilgi satırı: yalnız modülasyonlu (p ≤ 0,01) kümelerden ve olay başına medyan kümeden
  hesaplanan A_PK. Üçünün en küçüğüyle A90/A_PK bilgi olarak da yazılır.
- **Ö-b:** `TR7C_KOSU_DURUM.json` aşama sonlarında yalnız "tamamlandı / hata" ve dosya sha256'larını taşısın; X_N,
  f_PK gibi sayılar hüküm dosyasına kadar yazılmasın. N aşamasından sonra koşu yalnız teknik çöküşle durur (TR-7 §10.6).
- **Ö-c:** Tohoku duman sınamasında (geliştirme verisi, dal değiştirmez) dört TR-7 kümesinin ve saf telesismik P
  kümesinin (05:57:43–06:05:57) modülasyon M'si ve p'si yazılsın. Saf P kümesi bilinen bir tremor dışı gerçek kümedir.
  Okunuşu önceden yazılsın: "p ≤ 0,01 ise kilitsiz sızıntıda da m_f'nin küçük olmadığına dair tek gözlemlik işaret;
  dal değişmez, D-3 gereği metin değişmez, yalnız §12'ye yazılır."
- **Ö-d:** Dal (c) cümlesinden sonra parantezle hangi şartın kaldığı yazılsın: "(iii)", "(iv)" ya da "(iii) ve (iv)".
  (iv)'ün tek başına kalması genlik karıştırıcısından çok m_t'nin düşüklüğünü gösterir; cümle bunu ayırmıyor.
- **Ö-e:** ŝ'nin yanına Clopper–Pearson %95 alt sınırıyla hesaplanmış bir (1 − ŝ_alt)^n_açık bilgi satırı. n_P ≈ 10
  ile ŝ'nin belirsizliği büyüktür.
- **Ö-f:** Dondurma sürümünde `ESIK-DAYANAGI.md` tablosuna TR-7c satırı eklensin: kapı D30M3; etki s₀ 0,57 / 0,77
  (tahmin); ×2 → 1,00 / 0,95; ×0,5 → 0,20 / 0,23; dal (a) sınırında 0,66 / 0,93.
- **Ö-g:** §7.2'deki "Ayırt etmeyen algılayıcı ≤ 0,0002" satırının dayanağı `tr7c_inc1.json`
  `bagimsiz.ayirt_etmeyen_D30M3_kendi` olarak gösterilsin.
- **Ö-h:** Olay başına "Q doğrusu kuruldu mu" bilgi satırı (K5'in N'de çoğunlukla ρ dalına düşmesi beklenir; §1 ek bulgu).
- **Ö-i:** Kod incelemesine iki not:
  - `_rho` Spearman'ı eşit değerlerde ortalama sıra kullanmıyor. 1 Hz log zarfta eşitlik nadirdir, ama denetlenmeli.
  - `_k1_kalinti`'nin Q indisleri yapay dizinin indisleridir. Gerçek veride saniye eşlemesi ve maske hizası
    denetlenmeli.

## 11. Doğrulanamayanlar

- N 27 / N 28 için P ve S varışları (ezber iasp91 tablosundan kaba ara değerleme; taup çalıştırılmadı).
- Chao 2012'de N 27 ve N 28'in aynı kayıttan ölçüldüğü (eşit PGV_T'den çıkarım).
- Kilitli, genliğe bağlı sızıntının Parkfield yüzey ağında var olup olmadığı ve m_f'nin gerçek değeri. §5'teki tablolar
  varsayım ızgarasıdır.
- m_t (INCELEME-0'daki gibi).
- Ham yoklama günlükleri (`/mnt/project-files/turetme/tr7b-ham/`): açılmadı.
- K5'in gerçek veride Q doğrusunu hangi olaylarda kuracağı.
- Tohoku kümelerinin tremor mu sızıntı mı olduğu.
