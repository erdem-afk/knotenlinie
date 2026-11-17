# TR-7c bağımsız inceleme 0: "kural seçimini kör gerçek kontrol yapsın" fikri

Tarih: 17 Kasım 2026. İncelenen: koordinatörün TR-7c fikri (ZINCIR Halka 12 sonu). Henüz ön kayıt metni yok; bu inceleme
fikrin kendisini ve TR-7b taslağının §6 (K1b) dallarını birlikte değerlendirir.

Yöntem: yalnız depo dosyaları okundu, git geçmişi denetlendi ve yapay ikiterimli hesap yapıldı:
- Hesap betiği: `kayit/turetme/tr7c/tr7c_guc.py` (sha256 f9c9289a…e39b).
- Çıktı: `kayit/turetme/tr7c/tr7c_guc.json` (sha256 e225b0e6…5427).
- Tek girdi `tr7b/tr7b_sayim.json`. Bu dosya Chao 2012 S1 etiketlerini, PGV_T değerlerini ve istasyon sayılarını taşır;
  yalnız üstveridir.

Hiçbir dalga formu indirilmedi ya da açılmadı. 2026 ve sonrası veri kullanılmadı. Chao 2012'nin tam metni okunmadı ve
erişilmeye de çalışılmadı. Maliyet 0 €.

## Hüküm: DÜZELTMEYLE KABUL

Fikrin özü sağlam. K5 önceden sabitlenir, tek bir kör gerçek kontrol yapılır ve Marmara ancak bu kontrol geçerse açılır.
Sapma da tutucu yöndedir. Ama TR-7b §6.4'ün yazılı başarı ölçütü iki noktada bu iş için yetersizdir:
- Yalnız 2 negatifle, ayırt etmeyen bir algılayıcıyı %34–44 olasılıkla "sınandı" sayar.
- Chao etiketleri tetikleyici genliğiyle karışıktır. Genliğe duyarlı bir sızıntı algılayıcısı, 30 negatifle bile
  %95–99 olasılıkla "ayırt ediyor" görünür.

Önerilen ölçüt (D30M3, §5): 30 negatif, Fisher sınaması ve **modülasyon şartı** birlikte. Bu ölçüt sızıntıda yanlış
kabulü ≤ 0,01–0,06'ya indirir. Gücü 0,73–0,95'tir (gerçek duyarlılık 0,7). Değerlerin hangi varsayımlara bağlı olduğu
§2'de.

## 1. Sapma meşru mu?

**TR-7b'nin yazılı kurallarıyla çelişiyor.** Çelişkiyi gösteren maddeler:
- §4.3: "hiçbiri kabul edilebilir değilse kural seçilmez ve TR-7b dondurulamaz".
- §11.3 madde 4: Tur 2 sonuçsuzsa TR-7b "kapı altında" kalır.
- §12.4 madde 4: "dördüncü tur açılmaz".

TR-7c dördüncü bir yapay tur açmıyor ve hiçbir eşiği oynatmıyor. Ama yazılı yapay ölçütü kaldıramamış bir kuralı (K5,
Y1 A3 a_y10 'egim' hücresi, tohum 2'de 0,06 > 0,05) kullanmaya karar veriyor. Bu, **sonuç görüldükten sonra seçim
kuralının gevşetilmesidir**. Yalnız beyanla meşru olabilir; bunu TR-7b'nin içinde yapmak meşru olmaz. Ayrıca motivasyon
da sonuçtan geliyor: Tur 3'ün bilgi satırında K4/K5 6 istasyonla bütün şartları geçmişti (0,03 / 0,04).

**Neden yine de kabul edilebilir?**
1. Kaldığı hücre, **tremorun fazla atılmasını** ölçer. Gerçek etki, "tremor varken K5'in ~%5–6 küme silmesi"dir. Bu
   hata kör kontrolde algılamayı azaltır, yani "sınanamadı" yönüne iter. Yanlış "sınandı" ya da yanlış "VAR" üretmez.
2. K5'in, yanlış alarmı belirleyen satırları iki turda da geçti:
   - Y2'nin 18 hücresi: sağ kalan 0,00–0,02.
   - Y3: 0,97–1,00.
   - F1/F2: 0,00.
3. Yapay kapının yerine daha sıkı ve gerçek bir kapı geliyor: kör olaylar. Kapı kaldırılmıyor.

**K5 hangi bilgiyle seçiliyor?**
- K4 ile K5, Tur 2'nin ve Tur 3'ün bütün hücrelerinde aynı değerleri verdi (ONKAYIT §11.4 ve §12.5 tabloları).
- Aralarındaki seçim, önceden yazılmış simetri kuralıyla yapılıyor (§11.3 madde 2: "önce simetrik olan (K5) seçilir").
- Bu kural commit 1e03d20'de girdi (16 Kasım 17:28 UTC). Tur 2 sonucu commit d5ede9b'dedir (17:50).
- Yani K5'in seçimi tanıma dayanır, veriye dayanmaz. Seçimde kullanılan bilgi yalnız yapay sınama ve tanımdır.

Tohoku geliştirme verisinde K5 hiç hesaplanmadı:
- `tr7b_gelistirme.json` yalnız K0–K3'ü içeriyor.
- `tr7b_gelistirme3.json` yalnız K6'nın konum adımını içeriyor.

Bu durum körlük açısından iyidir. Ama K5'in gerçek veride bir kez bile çalıştırılmadığı anlamına gelir (§6 Z7).

**Kör olaylardan sızıntı var mı?** Dosyalardan doğrulananlar:
- **SAYIM yoklamaları W'ye düşmüyor.** `tr7b_sayim.py` (satır 245–259) olay başına sınıf başına tek bir dataselect isteği
  yapıyor: T0 − 1800 sn'den başlayan 10 sn. Bu aralık W'den önce, R'nin içindedir. Gövdenin sha256'sı tutulmuyor
  (`kaydet` verilmemiş) ve gövde `del g` ile siliniyor.
- **Öteki betikler.** `kayit/turetme/` altında dataselect çağıran başka bir tr7b betiği yok.
- **TR-7'nin Parkfield negatif pencereleri.** Bu pencereler 2011-02-10 ile 2011-03-08 arasındadır
  (`tr7_negatif_pencere.csv`), yani 2001–2010 kör olaylarıyla kesişmiyor.
- **Yapay ve geliştirme betikleri.** `tr7b_yapay*.py` ve `tr7b_gelistirme*.py` kör olay adı ya da zamanı içermiyor.

**Doğrulanamadı:** depo dışındaki ham günlükler (`/mnt/project-files/turetme/tr7b-ham/`) bu incelemede açılmadı.
Körlük beyanı bu yüzden yalnız betik koduna ve SAYIM metnine dayanır.

**Kör olmayan kısım:** yazar Peng 2009'un tam metnini okudu. Hangi olayda tremorun ne zaman ve hangi dalgayla geldiği
literatürden biliniyor (SAYIM §5 madde 4). K5'in eşikleri bundan önce yapay veriyle sabitlendi. Bu yüzden bu bilgi
ancak bundan sonra bir ayar yapılırsa zarar verir. Ön kayıt bu yolu açıkça kapatmalı (§6 Z1).

## 2. Kör kontrolün gücü

**Model** (betik başlığında; varsayımdır, sonuç değildir):
- Pozitif olay başına gerçek algılama olasılığı s.
- Tetikleyicili ama tremorsuz pencerede yanlış alarm olasılığı q.
- Rastgele negatif pencerede yanlış alarm olasılığı r. Ana tabloda r = q alındı. N_PK = 120.
- Olaylar bağımsız sayıldı.

Pozitif olayda algılama olasılığı p_P = 1 − (1 − s)(1 − q) olarak alındı.

**Ölçütler:**
- **A** = TR-7b §6.4 (b) aynen, |N| = 2. "Sınandı" sayılması için şunlar gerekir: X_P ≥ max(5, X_min(10, f_PK)),
  FAR ≤ 0,30 ve "ayırt edici değil" etiketi olmaması.
- **B** = X_P ≥ 5/10 ve X_N = 0/2.
- **F2** = A'nın X_P şartı ve Fisher tek yanlı p ≤ 0,05, |N| = 2.
- **D30** = A'nın X_P şartı ve FAR ≤ 0,30 ve Fisher p ≤ 0,05; P (10) ile Chao Q = 0'ın 30 olayı karşılaştırılır.
- **D30M3** = D30 ve ≥ 3 P olayında modülasyon. Önerilen ölçüt budur (§5).

**"Sınandı" deme olasılığı:**

| Gerçek s | q | A (N=2) | B | F2 | D30 | D30M3 (m_t 0,8) | D30M3 (m_t 0,5) |
|---|---|---|---|---|---|---|---|
| 0,3 | 0,05 / 0,1 / 0,2 / 0,3 | 0,20 / 0,26 / 0,22 / 0,10 | 0,20 / 0,24 / 0,30 / 0,32 | ≤ 0,003 | 0,22 / 0,28 / 0,19 / 0,09 | 0,19 / 0,23 / 0,15 / 0,07 | 0,10 / 0,12 / 0,08 / 0,04 |
| 0,5 | 〃 | 0,66 / 0,68 / 0,57 / 0,26 | 0,62 / 0,60 / 0,53 / 0,44 | 0,01–0,03 | 0,68 / 0,71 / 0,54 / 0,24 | 0,65 / 0,67 / 0,51 / 0,23 | 0,42 / 0,42 / 0,34 / 0,16 |
| 0,7 | 〃 | 0,95 / 0,95 / 0,87 / 0,43 | 0,87 / 0,79 / 0,63 / 0,49 | 0,09–0,17 | 0,96 / 0,96 / 0,87 / 0,43 | 0,95 / 0,95 / 0,86 / 0,43 | 0,73 / 0,73 / 0,68 / 0,34 |
| 0,9 | 〃 | 1,00 / 0,99 / 0,96 / 0,49 | 0,90 / 0,81 / 0,64 / 0,49 | 0,23–0,68 | 1,00 / 1,00 / 0,99 / 0,54 | 1,00 / 1,00 / 0,99 / 0,54 | 0,90 / 0,90 / 0,90 / 0,49 |

q = 0,3 sütunu: FAR ≤ 0,30 tavanı (TR-7b'de var) yaklaşık yarı yarıya keser. Bu sütun bilerek tutucudur.

**Yanlış kabul.** Asıl tehlike TR-7'nin başarısızlık biçiminin tersidir: tremor yok (s = 0), ama algılayıcı her büyük
tetikleyicide t olasılıkla ateşliyor. Rastgele pencerede r = 0,05.

| t | A (N=2) | B | D30 | D11 (Q=0 ve PGV_T ≥ 0,01; 11 olay) | D30M3 |
|---|---|---|---|---|---|
| 0,3 | 0,09 | 0,07 | 0,03 | 0,01 | 0,00 |
| 0,5 | **0,34** | 0,16 | 0,03 | 0,02 | 0,00 |
| 0,7 | **0,44** | 0,09 | 0,02 | 0,02 | 0,00 |
| 0,9 | 0,19 | 0,01 | 0,00 | 0,00 | 0,00 |

A'nın açığı şurada: X_N = 1/2 ve X_P ≥ 6/10 olduğunda "X_N/|N| ≥ X_P/n_P" sağlanmaz. Böylece hiç ayırt etmeyen bir
algılayıcı "geçti" etiketini alır.

**Genlik karıştırıcısı (en önemli bulgu).**
- Chao etiketi tetikleyici genliğiyle güçlü biçimde ilişkili:
  - P'nin PGV_T aralığı 0,029–0,496 cm/s.
  - Q = 0 olaylarının medyan PGV_T'si 0,0095 cm/s; 30 olayın 19'u 0,01'in altında.
- Model: yanlış alarm genliğe bağlı, q(v) = 1/(1 + (v0/v)²), s = 0. "Sınandı" olasılıkları:

| v0 (cm/s) | D30 | D11 | D30M3 (m_f 0,05 / 0,10) |
|---|---|---|---|
| 0,01 | **0,95** | 0,07 | 0,010 / 0,062 |
| 0,03 | **0,99** | **0,57** | 0,006 / 0,040 |
| 0,1 | 0,36 | 0,24 | 0,001 / 0,004 |

Yani "P'de algılama oranı N'dekinden yüksek" bulgusu tek başına tremoru göstermez; "büyük tetikleyicide daha çok sızıntı"
da aynı sonucu verir. Genliği eşlenmiş negatif sayısı çok azdır: PGV_T ≥ 0,02 olan yalnız 4 Q = 0 olayı var. Bu yüzden
karıştırıcıyı ancak fiziksel bir şart kırar. O şart modülasyondur: kümenin, tetikleyici yüzey dalgasının gerilme evresine
bağlı olması (TR-7 §6.4 ölçüsü). TR-7b §6.4 bu şartı tanımlıyor ama yalnız Marmara'da "VAR"ı engellemek için kullanıyor; "sınandı"ya
bağlamıyor.

**Doğrulanamadı:**
- m_t, yani gerçek tetiklenmiş tremor kümesinin TR-7 modülasyon sınamasından p ≤ 0,01 ile geçme olasılığı. Tohoku'da
  hiçbir küme ayıklamadan sağ çıkmadığı için ölçülmedi. Peng 2009'un "Love dalgasıyla modüle" gözlemi görseldir.
- m_f, yani sızıntı kümesinin modülasyondan geçme olasılığı (0,05 / 0,10 varsayıldı). Yüzey dalgasına kilitli bir sızıntı
  biçimi (örneğin alet doğrusalsızlığı) varsa m_f daha büyük olur.

**2 negatif yeterli mi?** Hayır.
- 2 negatifle Fisher tek yanlı p ≤ 0,05 ancak 9/10 ile 0/2'de (p = 0,045) ya da 10/10 ile 0/2'de (0,015) mümkündür.
  F2'nin gücü bu yüzden s = 0,7'de 0,09–0,17'dir.
- Etiket kuralıyla (A) kullanıldığında da yukarıdaki yanlış kabul açığını bırakır.
- Bütün Q = 0 olayları kullanılmalıdır. 30'unun 30'u ≥ 3 liste istasyonuyla taranabilir (SAYIM). Gerçek koşuda
  (E1 maskesi ve örtü düşünce) en az 20 kalmalıdır:
  - n_N = 20'de güç 0,93 (m_t 0,8) / 0,72 (m_t 0,5);
  - n_N = 10'da 0,85 / 0,67.
- n_P'ye duyarlılık daha büyüktür. n_P = 8'de güç 0,88 / 0,56, n_P = 6'da 0,71 / 0,34 olur.

**Chao'nun "tetiklemedi" etiketi bizim için gerçek negatif mi?** Kesin değil, iki yönde:
1. Etiket görsel incelemedir ve büyük ölçüde PKD/HRSN kuyu kayıtlarına dayanır (Peng 2009). Daha duyarlı bir algılayıcı
   Q = 0 olaylarında gerçek zayıf tremor bulabilir. Bu da q_N'yi şişirir. Q = 0 olaylarının π'sinde algılanabilir tremor
   varsa (q = 0,1 için):

   | π | Ölçüt | Güç: s = 0,5 / 0,7 / 0,9 |
   |---|---|---|
   | 0,2 | D30 | 0,56 / 0,84 / 0,99 |
   | 0,4 | D30 | 0,35 / 0,58 / 0,86 |
   | 0,4 | E30 (X_N ≤ 6/30 tavanı) | 0,17 / 0,05 / 0,01 |

   Mutlak bir N tavanı kirli negatifte çöküyor. Göreli sınama (Fisher) bu yüzden tercih edilir. Bu hatanın yönü yanlış
   rettir ("sınanamadı"), yanlış kabul değildir.
2. Bizim ana sınıfımız yüzey ağıdır, Chao'nunki büyük ölçüde kuyu/PKD'dir. Bu durumda bizim algılama eşiğimiz daha
   yüksektir. Q = 1 olaylarının bir kısmı yüzey ağında görünmez, s düşer. Bu da yanlış ret yönündedir (TR-7b §8 madde 5).
- Hangi istasyonların Chao 2012'de Q'yu belirlediği tam metinden doğrulanamadı.

## 3. Döngüsellik ve bağımsızlık

- **Aynı veri.** Chao/Peng etiketleri NCSN yüzey istasyonlarını da içeren aynı Parkfield kayıtlarından çıktı. Liste
  sınıfımız NC istasyonlarını kapsar. Etiketin kendisi döngüsel değildir (uzman etiketi ile otomatik algılayıcı
  karşılaştırması olağandır), ama **hatalar ilişkili olabilir**. Peng 2009 Kuril 2006'da tremorun artçı P'leriyle
  karıştığını yazıyor. Görsel incelemeyi yanıltan bir sızıntı bizim algılayıcıyı da yanıltabilir. Bu da uyumu şişirir.
- **Benzer yöntem.** Etiket 2–8 Hz zarfın yüzey dalgasıyla eş zamanlılığına bakıyor; algılayıcı da aynı şeye bakıyor.
  "Sınandı" sonucu bu yüzden "algılayıcı yayımlanmış görsel tremor tanımını kör olarak yeniden üretiyor" diye okunmalı.
  "Algılayıcı tremoru doğru buluyor" sonucu çıkmaz.
- **Karıştırıcı.** Etiket genlikle ilişkili (§2). Bağımsızlığı en çok bozan unsur budur.
- **Olaylar arası bağımlılık.** Kuril 2006 ile 2007 aynı bölgeden, 2 ay arayla geldi; Macquarie 2004 ile Sumatra 2004
  arasında 3 gün var. Binom/Fisher bağımsızlık varsayar. Kuril 2007'siz bir duyarlılık satırı bilgi olarak yazılmalıdır.
- **Sonuç.** "Sınandı" kararı tek başına Chao etiketine bırakılmamalıdır. Modülasyon şartı, etiketten bağımsız
  fiziksel bir ikinci tanıktır. Bu şart olmadan genlik karıştırıcısı kapanmaz.

## 4. Marmara'ya aktarım

Parkfield'da geçen bir kör kontrol yalnız şunu gösterir: kırsal, yoğun, yerel yüzey ağında, Parkfield–Cholame türü
(sığ değil, 20–25 km) ve ≈ 2 kPa'nın üstünde tetiklenen bir kaynağın tremoru bu algılayıcıyla s oranında yakalanır.

Kaba hesap (τ ≈ G·PGV/β, G = 30 GPa, β = 3,5 km/s; dönüşüm doğrulanamadı): P eşiği PGV_T 0,027 cm/s ≈ 2,3 kPa.

Marmara'ya taşınmayanlar:
1. **Gürültü.** KO istasyonları kentsel yüzey istasyonlarıdır, 2–8 Hz gürültüleri durağan değildir ve kuyu yoktur
   (TR-7 §12).
2. **Ağ geometrisi.** S2/S3 pratikte yalnız KO ile taranır.
3. **Kaynak.** Marmara'da tetiklenebilir tremor kaynağının varlığı, derinliği ve eşiği bilinmiyor. Pfohl 2015 merkezî
   KAF'ta olumsuzdur.
4. **Kaba τ.** Marmara tarafında ×3 belirsizlik var.

**Marmara duyarlılık sayıları.** TR-7'de Marmara verisi hiç indirilmedi; **ölçülmüş bir Marmara A90'ı yoktur**. Elde
olanlar şunlardır:
- Parkfield'da (Tohoku dönemi negatif pencereleri, K0): A50_PK = 8,9 nm/s, A90_PK = 11,2 nm/s.
- Durağan gürültüde yapay bağıntı: A50 ≈ 0,43 × gürültü RMS (A_300 ölçeğinde; TR-7 §11). Kentsel gürültüde A90'ın daha
  büyük çıkacağı TR-7'de önceden yazıldı.
- Segment başına tetikleyici sayısı (≥ 2 kPa, ×1): 9–12. ×1/3 alındığında 1–4.

**Ön kayda girmesi önerilen cümle** (köşeli yerler koşuda doldurulur):

> "S_k'de kaba τ ≥ 2 kPa olan n = [..] tetikleyicide tetiklenmiş tremor görülmedi. Bu segmentte algılanabilir en küçük
> genlik A90(S_k) = [..] nm/s'dir. Parkfield kör olaylarında algılanan tremorun 25 km'ye indirgenmiş medyan genliği
> A_PK = [..] nm/s'dir. A90(S_k) ≤ A_PK ise: Parkfield türü, ≈ 2 kPa'da tetiklenen ve Parkfield'dakine eşit genlikte
> tremor veren bir kaynak bu gürültüde görülürdü. Tetikleyici başına algılama olasılığı Parkfield'da ölçülen ŝ = [..] ise
> n tetikleyicide hiç görülmeme olasılığı (1 − ŝ)^n = [..] olur. A90(S_k) > A_PK ise: bu tarama Parkfield türü bir
> kaynağı dışlamaz, yalnız A90(S_k)'nın üstündeki tremoru dışlar. Bu cümle deprem olasılığı hakkında hiçbir şey
> söylemez."

Ölçek için (1 − s)^n değerleri:

| n | s = 0,2 | s = 0,3 | s = 0,5 |
|---|---|---|---|
| 8 | 0,17 | 0,06 | 0,004 |
| 12 | 0,07 | 0,01 | 0,0002 |
| 4 (×1/3) | 0,41 | 0,24 | 0,06 |

Kentsel gürültüde gerçek s_Marmara, ŝ_Parkfield'dan küçük olacaktır. Boş tarama bu yüzden ancak A90(S_k)/A_PK ≤ 1 olan
segmentlerde bir şey söyler. TR-7 §7.5 bu oranı yalnız bilgi satırı olarak yazıyor; TR-7c'de "görülmedi" cümlesinin
şartı olmalıdır (Z8).

## 5. Önerilen başarı ölçütü (D30M3) ve görülebilir en küçük etki

- **Güç** (gerçek s = 0,7, q ≤ 0,1, n_P = 10, n_N = 30): m_t = 0,8 ise 0,95, m_t = 0,5 ise 0,73.
- **Yanlış kabul.** Ayırt etmeyen algılayıcıda ≤ 0,0002. Genliğe bağlı sızıntıda ≤ 0,01 (m_f 0,05) ya da ≤ 0,06
  (m_f 0,10).
- **Görülebilir en küçük etki** (güç 0,80, q = 0,1): s ≥ 0,57 (m_t 0,8) ya da s ≥ 0,77 (m_t 0,5).
  - Kaynak: **bizim seçimimiz**. Yüzey ağında otomatik algılayıcının Chao olaylarındaki duyarlılığı için yayımlanmış bir
    değer yok.
  - Tek dolaylı işaret Tohoku geliştirmesidir: yüzey ağında ayıklamadan önce 4 küme vardı.
- **×0,5 / ×2 duyarlılığı.**
  - s ×0,5 (≈ 0,29): güç ≈ 0,2 (m_t 0,8). "Sınanamadı" sonucu, ancak yarı yarıya duyarlı bir algılayıcıyı dışlar.
  - s ×2 (≥ 1): güç ≈ 1.

## 6. Düzeltmeler (TR-7c ön kaydına aynen girecek cümleler)

**Z1 – Sapma ve körlük beyanı.**
> "TR-7c, TR-7b'nin §4.3, §11.3 madde 4 ve §12.4 madde 4 kurallarından beyanlı bir sapmadır. TR-7b 'kapı altında (kural
> bulunamadı), iki tasarım turu sonuçsuz' olarak kapanmış kalır; TR-7c onun sonucunu değiştirmez. Sızıntı kuralı K5'tir
> (TR-7b §11.1), `tr7b_yapay2.py` (sha256 ae995ba8802a934577cbf26051229360bcfb1a85d5d4d7dc16d358dfeaef437f) içindeki `K5`
> işleviyle bayt bayt aynı. K5, Tur 2'de yazılı yapay ölçütü bir hücrede kaldı (Y1 A3 a_y10 'egim', tam atılma 0,05 / 0,06;
> şart ≤ 0,05). Bu hücre tremorun fazla atılmasını ölçer, yani kör kontrolde 'sınanamadı' yönüne iter. K5'in seçimi
> TR-7b §11.3 madde 2'nin simetri kuralına dayanır (commit 1e03d20, Tur 2 sonucundan önce); K4 ile K5 iki turun bütün
> hücrelerinde aynı değeri verdi. Hiçbir eşik değişmez. Kör koşu bir kez yapılır. Kör kontrol kalırsa K4, K6 ya da başka
> bir kural aynı kör olaylarda denenmez; bu olaylar harcanmış sayılır. Kör olayların W pencerelerinde bugüne kadar hiçbir
> dalga formu istenmedi (`tr7b_sayim.py`: yalnız T0 − 1800 sn'de 10 sn'lik içeriği saklanmayan yoklamalar). Tohoku 2011
> geliştirme verisidir. Marmara dalga formu hiç indirilmedi. Yazar Peng 2009'un tam metnini okudu; olayların literatürdeki
> tremor zamanlamasını bilir, algılayıcının bu olaylardaki çıktısını bilmez."

**Z2 – Olay listesi.**
> "P (kör pozitif) = Chao 2012 Tablo S1'de Q_CC = 1 ve PKD PGV_T ≥ 0,027 cm/s olan, Tohoku hariç 10 olay: Peru 2001,
> Denali 2002, Colima 2003, Tokachi-oki 2003, Sumatra 2004, Kuril 2006, Kuril 2007, Wenchuan 2008, Samoa 2009,
> Maule 2010. N (kör negatif) = Tablo S1'de Q_CC = 0 olan 30 olayın hepsi (TR-7b_SAYIM §3). Kunlun 2001 ve Tonga 2006
> bilgi satırıdır. n_P ve n_N, TR-7 §4.2 örtü kuralından ve E1 maskesinden sonra K1b aralığının ≥ %50'si açık ve ≥ 3 liste
> istasyonu olan olay sayısıdır. E1 maske payları dondurmadan önce yalnız katalogla hesaplanır. Rastgele negatif pencereler
> TR-7b §6.3 aynen (yalnız P ve TR-7b'nin iki N olayı için; N_PK ≤ 120)."

**Z3 – Başarı ölçütü.**
> "'Ölçü sınandı' ⇔ aşağıdakilerin hepsi:
> (i) X_P ≥ max(⌈n_P/2⌉, X_min(n_P, f_PK)) (TR-7 §8 tanımı);
> (ii) FAR_PK = f_PK/N_PK ≤ 0,30;
> (iii) P'ye karşı N'de algılama oranı için Fisher kesin sınaması, tek yanlı p ≤ 0,05;
> (iv) algılama veren P olaylarından en az 3'ünde, algılama kümelerinden en az biri TR-7 §6.4 modülasyon ölçüsünde
> p ≤ 0,01 verir (başvuru istasyonu ve boş dağılım TR-7 §6.4 aynen).
> 'Olay algılaması' TR-7b §6.2 aynen."

**Z4 – Dallar** (sıra bağlayıcı):
> "(a) n_P < 8 ya da n_N < 20 → 'ölçü sınanamadı (Parkfield verisi yok)'.
> (b) Z3 sağlanır → 'ölçü sınandı'. Marmara aşamaları TR-7b §7 aynen açılır. (b′) etiketi TR-7b §6.4 aynen.
> (c) Z3 (i) ve (ii) sağlanır, modülasyon ≥ 3 algılama veren P olayında ölçülebilir, ama (iii) ya da (iv) sağlanmaz → 'ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş tremoru
> tetikleyici genliğinden ayıramadı)'.
> (d) Z3 (i) ya da (ii) sağlanmaz, MDA tanımlı ve A90_PK ≤ 100 µm/s → TR-7b §6.4 (c) cümlesi.
> (e) Öteki durumlar → 'ölçü sınanamadı (yöntem)'. Modülasyonun ölçülebildiği algılama veren P olayı 3'ten azsa
> (başvuru istasyonu yok ya da örtü < %90) dal (e)'dir: 'ölçü sınanamadı (modülasyon ölçülemedi)'.
> (b) dışında Marmara verisi indirilmez. Bilgi satırları: Kuril 2007 çıkarılmış Z3; liste sınıfına karşı kuyu sınıfı;
> PGV_T ≥ 0,02 cm/s olan 4 N olayında algılama sayısı; X_N/n_N ile X_P/n_P."

**Z5 – Görülebilir en küçük etki.**
> "Ölçütün gücü 0,80 olan en küçük gerçek pozitif algılama oranı, tetikleyicili yanlış alarm 0,1 iken s ≈ 0,57'dir (gerçek
> tremor kümelerinin modülasyondan geçme olasılığı 0,8 varsayımıyla; 0,5 ise s ≈ 0,77). Bu değer yayımlanmış bir
> değerden değil, bizim seçimimizden gelir. s yarı olsaydı güç ≈ 0,2, iki katı olsaydı ≈ 1 olurdu. 'Sınanamadı' sonucu
> bu yüzden yalnız 'algılayıcı yüzey ağında bu olayların yarısından fazlasını, modülasyonlu biçimde, görmüyor'
> demektir. Hesap: `kayit/turetme/tr7c/tr7c_guc.py`."

**Z6 – Marmara cümlesi.** §4'teki alıntı aynen. Ek kural:
> "A90(S_k)/A_PK > 1 olan segmentte 'görülmedi' cümlesine 'Parkfield türü kaynak bu gürültüde görülemezdi' eki
> bağlayıcıdır."

**Z7 – Gerçek veride duman sınaması (bilgi, dal değiştirmez).**
> "K5 dondurulmadan önce Tohoku geliştirme verisinde (`tr7b_gelistirme.py` girdileri) bir kez çalıştırılır. Yalnız kodun
> gerçek zarflarla çalıştığını gösterir. Sonucu ne olursa olsun K5 ve Z3 değişmez."

**Z8 – Bağımsız kod incelemesi.** TR-7b koşu kodu (K5 ile K1b) dondurulmadan önce bağımsız kod incelemesi gerekir.
Gerekçe: K5 bu kodda ilk kez yapay ortam dışında çalışacak; Q referansı ve ρ gerçek maske parçalarıyla hesaplanacak.

## 7. Doğrulanamayanlar

- Ham yoklama günlükleri (depo dışı) açılmadı.
- Chao 2012'de Q'yu belirleyen istasyonlar ve inceleme yöntemi (tam metin okunmadı).
- m_t ve m_f (§2). Önerilen ölçütün gücü ve yanlış kabul değerleri bu iki varsayıma bağlıdır. TR-7 §6.4 notuna göre
  ölçünün hızla çalışan ilk sürümü modülasyonsuz tremorda %20 yanlış p ≤ 0,01 vermişti; faz sürümünün sızıntı kümelerindeki
  yanlış oranı ölçülmedi.
- Kör P olaylarında TR-7 §6.4'ün uzun periyot başvuru istasyonunun (2001–2010) varlığı sayılmadı. Dondurmadan önce
  yalnız üstveriyle sayılmalıdır (0 €); yetmezse ölçüt (iv) uygulanamaz.
- PGV → kPa dönüşümü (G ve β varsayımı).
- Kör olaylarda gerçek W örtüsü ve E1 maske payları (n_P < 8 olursa (a) dalına düşülür).
- Marmara A90 (hiç ölçülmedi).
