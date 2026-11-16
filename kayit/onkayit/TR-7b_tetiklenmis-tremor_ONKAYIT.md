# TR-7b ön kaydı (TASLAK): Marmara'da tetiklenmiş tremor taraması, yeniden tasarlanmış sızıntı kuralı ve kör Parkfield pozitif kontrolüyle

Tarih: 16 Kasım 2026. Durum: **TASLAK 1, DONDURULMADI.** Bu metin hiçbir koşu için bağlayıcı değildir. Bağımsız
inceleme yapılmadı.

**Taslağın bugünkü hükmü: dondurulamaz.** Veri varlığı kapısı (`TR-7b_SAYIM.md`) geçti. Ama sızıntı kuralının dört
adayından hiçbiri, koşudan önce yazılmış seçim ölçütünün bütün şartlarını iki tohumda birden sağlamadı (§4.4). Ölçüte
göre kural seçilmedi. Tur 2 (§11; K4, K5) de tek hücrede kaldı (Y1 A3 kalibre: 0,05 / 0,06, şart ≤ 0,05).
TR-7b **"kapı altında (kural bulunamadı)"** kalır: aday elenmez, ama yeni bir kural turu ve bağımsız inceleme gelmeden
dondurulmaz (§4.6).

Türediği yerler:
- `TR-7_tetiklenmis-tremor_ONKAYIT.md` (sürüm 3, DONDURULDU, Ek 1 ile). Bu metin yalnız farkları yazar. "TR-7 §x aynen"
  diye geçen her yer, TR-7 metninin o bölümünün sayısı, eşiği ve cümlesiyle birebir geçerli demektir.
- TR-7 sonucu (`kayit/turetme/tr7/tr7_sonuc.md`, `tr7_k1.json`, `tr7_k1_negatif.json`; ZINCIR Halka 11).
- `TR-7b_SAYIM.md` (veri varlığı kapısı).

Kod (`kayit/turetme/tr7b/`):
- `tr7b_sayim.py`: sayım.
- `tr7b_yapay.py` (sha256 e9271531…4374): aday kurallar ve yapay sınama. TR-7'nin `tr7_cekirdek.py`'si değiştirilmeden
  içe aktarılır.
- Çıktılar `tr7b_yapay_t1.json` (tohum 20261116, sha256 03572d3e…0be22) ve `tr7b_yapay_t2.json` (tohum 7171,
  sha256 6f2d8ce4…e4bf).
- `tr7b_gelistirme.py` (sha256 d8d3f9d6…e1b5): Tohoku geliştirme verisi. Çıktısı `tr7b_gelistirme.json`
  (sha256 997c4c00…5660).

Maliyet 0 €. Bu taslak yazılırken Marmara'nın hiçbir dalga formu istenmedi. Kör pozitif ve negatif kontrol olaylarının
W pencerelerinde de hiçbir dalga formu istenmedi. Kullanılan gerçek veri yalnız TR-7'nin hâlihazırda işlenmiş Tohoku–Parkfield
1 Hz zarflarıdır. Bu veri **geliştirme verisidir**, aşağıda her geçtiği yerde öyle işaretlenir.

## 0. Bağlayıcı metinlerin sırası

Dondurulursa çelişkide sıra şöyle olacaktır:
1. Bu metin.
2. TR-7 sürüm 3 ve Ek 1, yalnız bu metnin sustuğu ve "aynen" dediği yerlerde.
3. TR-7'nin inceleme metinleri, TR-7'deki sıralarıyla.

Bu taslak TR-7'nin hiçbir dondurulmuş sayısını değiştirmez. Değişenler yalnız şu üçüdür: pozitif kontrol (K1 → K1b,
§6), sızıntı kuralı (§6.5.3 → §4) ve yapay denetim seti (§5).

## 1. Soru

TR-7 §1 aynen. Ölçmedikleri ve İstanbul'a bağ: TR-7 §1 ve §13 aynen. Mutlak olasılık yazılmaz.

## 2. Neden TR-7b (TR-7 K1'in başarısızlık biçimi)

TR-7'nin tek koşusunda K1 (c) dalında kaldı. Bütün segmentler "ölçü sınanamadı", Marmara verisi indirilmedi. Tanı satırı
şunu gösteriyor: Tohoku penceresinde ayıklamadan önce 4 tutarlı küme vardı. İlk ikisi 10'ar istasyonluydu, 44 ve 40
tutarlı çiftle. Dördü de sızıntı kuralıyla atıldı. Kural sonuçtan sonra değiştirilmedi.

**Geliştirme verisiyle tanı** (`tr7b_gelistirme.py`; Tohoku–Parkfield, TR-7'nin 12 istasyonu, E1 maskesi aynen). On iki
istasyonun dakikalık medyanı:

| Aralık (UTC) | Δ_y (2–8 Hz) | Δ_d (0,5–1 Hz) | Not |
|---|---|---|---|
| 05:36–05:56 | −0,03…0,03 | −0,03…0,02 | olay öncesi |
| 05:58–06:00 (Tohoku P) | 0,89–1,02 | 2,01–2,17 | saf telesismik cisim dalgası |
| 06:04–06:05 | 0,11–0,17 | 1,22–1,35 | P kodası |
| 06:13–06:16 (W başı, Love) | 0,41–0,61 | 0,57–0,83 | TR-7 kümesi 1 |
| 06:21–06:24 | 0,57–0,77 | 1,02–1,21 | TR-7 kümesi 2 |

İki şey görünüyor:
1. Tetikleyicinin kendi telesismik sinyali 0,5–1 Hz'i W boyunca ~1 log birimi yukarıda tutuyor. TR-7 §6.5.3'ün "Δ_d ≥ Δ_y"
   şartı bu yüzden tremor olsa da olmasa da sağlanıyor.
2. 2–8 Hz telesismik kodası 0,5–1 Hz'inkinden hızlı sönüyor (06:04'te Δ_y 0,1–0,2 iken Δ_d 1,2–1,35). W'deki
   Δ_y = 0,4–0,8 düzeyi bu kodayla tek başına açıklanmıyor.

Saf telesismik sınamada (tetikleyicinin P'si ile S'si arası, 05:57:43–06:07:11, %13 maskeli; sahte W olarak) algılayıcı
**10 istasyonlu, 45 tutarlı çiftli bir küme** kurdu. Yani telesismik P tek başına tutarlı küme kuruyor; ayıklama kuralı
gereklidir. Kural kaldırılamaz, yeniden tasarlanmalıdır.

Bu bir yapay denetim boşluğudur. TR-7'nin D7c'si yalnız tremor, D7d'si yalnız koda içeriyordu. "Tremor + eş zamanlı
telesismik düşük frekans" satırı yoktu.

## 3. Veri

- **Marmara:** TR-7 §3.1, §3.3 (Marmara negatifleri), §3.4 (Marmara satırları), §3.5 ve §3.6 aynen. Liste, birimler,
  pencereler ve manifest kuralı değişmez. Tohoku birimi Marmara'da körlüğünü korur: TR-7'de Marmara verisi hiç
  indirilmedi.
- **Parkfield:** TR-7 §3.2'nin istasyon listesi (`tr7_parkfield_liste.csv`, sha256 9dca3380…b2b8), kanal seçimi ve
  12 sınırı aynen. Fark: Tohoku yerine kör olaylar (§6). Ana sınıf **liste (yüzey)** sınıfıdır, çünkü Marmara'da kuyu
  sensörü yoktur (TR-7 §12). Kuyu sınıfı (BP/HRSN ve PB) aynı kodla ayrı bir **bilgi satırı** olarak koşulur ve hiçbir
  dalı değiştirmez. Gerekçe: kuyu duyarlılığı yüzey ağıyla karşılaştırılamaz, Marmara'ya taşınamaz.
- **Varlık (SAYIM).** Her kör olayda liste sınıfında 34–52, kuyu sınıfında 7–20 istasyon "var".
  - Örtü yalnız availability yanıtından ve R ortasındaki tek bir 10 sn'lik yoklamadan çıkarıldı (SAYIM §5).
  - %90 örtü kuralı koşuda TR-7 §4.2 ile yeniden uygulanır.
- **Veri sınırı:** TR-7 §3.6 aynen. Kör Parkfield olaylarının hepsi 2001–2010 arasındadır.

## 4. Sızıntı kuralının yeniden tasarımı (TR-7 §6.5 madde 3'ün yerine)

### 4.1 Tasarım şartı

Yeni kural iki şeyi birlikte yapmalı:
1. Tetikleyicinin kendi düşük frekans enerjisi varken tremoru silmemeli.
2. Bölgesel deprem kodasını ve telesismik cisim dalgası sızıntısını yine atmalı.

Toplama TR-7 ile aynıdır: istasyon başına bayrak konur, istasyonların ≥ yarısı bayraklıysa küme atılır. Darbe (§6.5.2),
taban kayması (§6.5.3a), maskeler (§6.5.1, 1a) ve bütün öteki adımlar TR-7 aynen.

### 4.2 Adaylar (K0–K2 yapay sınamadan önce tanımlandı; K3 ön denemeden sonra eklendi, §8 madde 1)

Tanımlar, istasyonun kümedeki aşım saniyeleri üzerinde (TR-7 §6.5.3 ile aynı saniyeler):
- Δ_y = medyan(L − m), Δ_d = medyan(L_d − m_d).
- r = Pearson(L, L_d), aynı saniyelerde.
- Q = [T0 + t_P(iz ortası, iasp91), W başı) ∖ maske. Bu, tetikleyicinin kendi cisim dalgası aralığıdır, yani
  tetikleyiciden gelen ama tremor dışı bir referanstır.

Adaylar:
- **K0 (TR-7, taban çizgisi):** Δ_d ≥ Δ_y.
- **K1 (referans-göreli sızıntı):**
  - Q'da L_d − m_d > 4σ_d olan saniyeler ≥ 30 ise (L − m) = a + b·(L_d − m_d) doğrusu en küçük karelerle kurulur.
  - Kalıntı e = (L − m) − (a + b·(L_d − m_d)), aşım saniyelerinde hesaplanır.
  - Bayrak: medyan(e) < 2σ. Yani 2–8 Hz fazlasının, tetikleyicinin kendi telesismik sinyalinin öngördüğünün üstündeki
    kısmı, algılama eşiğinin (4σ) yarısından küçükse istasyon bayraklanır.
  - Q'da referans yoksa K0'a düşer.
- **K2 (eşzamanlılık):** Δ_d ≥ Δ_y **ve** r ≥ 0,5.
  - 10'dan az saniye varsa r = 1 sayılır (tutucu).
  - 0,5, TR-7 §6.3'ün KORR eşiğidir; veriyle seçilmedi.
  - Gerekçe: koda ve telesismik sızıntıda iki bandın zarfı aynı kaynaktan gelir ve birlikte iner çıkar. Tremor 2–8 Hz'e
    bağımsız bir zaman biçimi ekler.
- **K3 (birleşik):** Δ_d ≥ Δ_y **ve** (K1'in kalıntı şartı **veya** K2'nin r şartı).
  - Q'da referans yoksa K2'ye eşittir.

### 4.3 Seçim ölçütü (tam koşudan önce yazıldı; `tr7b_yapay.py` başlığında)

Bir aday iki bağımsız tohumda da §5 tablosunun bütün şart satırlarını sağlıyorsa "kabul edilebilir"dir. Kabul
edilebilirler arasında seçim şöyle yapılır:
1. Önce simetrik kural seçilir, yani tetikleyici ve negatif pencerelerde aynı hesabı yapan.
2. Eşitlikte, şartlara en kötü pay farkı en büyük olan seçilir.

Hiçbiri kabul edilebilir değilse kural seçilmez ve TR-7b dondurulamaz. Tohoku geliştirme sonuçları ölçüte **girmez**;
yalnız bilgi olarak yazılır (§4.5).

### 4.4 Sonuç

§5'teki sayılarla:

| Aday | Kaldığı şartlar (tohum 1 / tohum 2) | Kabul edilebilir mi |
|---|---|---|
| K0 | Y1 kalibre A3 ve A10: 1,00 / 1,00 (≤ 0,05 gerekir) | hayır (TR-7'nin başarısızlığını yapayda yeniden üretiyor) |
| K1 | Y1 kalibre A3: 0,06 / 0,01 (≤ 0,05); Y3: 0,00 / 0,00 (≥ 0,95) | hayır |
| K2 | Y2 kalibre: 0,33 / 0,17 (≥ 0,95; algılama 0,24 / 0,29); Y2 a_y 5, κ 25: 0,89 / 0,93; Y3: 0,51 / 0,52 | hayır |
| K3 | Y1 kalibre A3: 0,06 / 0,01; Y3: 0,51 / 0,52 | hayır |

**Kural seçilmedi.** Başarısızlığın biçimi adaya göre değişiyor:
- K1 telesismik sızıntıyı atıyor: Y2'nin bütün düzeylerinde 0,99–1,00. Ama referansı telesismik olduğu için, aynı
  pencerede kataloglanmamış bölgesel bir koda varsa onu tremor sanıyor (Y3: 0,00). Ayrıca tetikleyici ve negatif
  pencerelerde farklı hesap yapıyor, yani simetrik değil.
- K2 tremoru hiç silmiyor: Y1 kalibre 0,00. Ama kalibre telesismik modelde zayıf 2–8 Hz kümelerini, yani 2–8 Hz'in
  gürültüye yakın olduğu ve r'nin düştüğü durumları, atamıyor. Y3'te de yarı yarıya kalıyor.
- K3 ikisinin zayıflığını tam kapatmıyor: Y1 A3'te tohum 1'de sınırın 0,01 üstünde; Y3 0,51.

### 4.5 Geliştirme verisi (Tohoku–Parkfield; seçim ölçütüne girmez)

`tr7b_gelistirme.py` TR-7'nin 4 kümesini aynı istasyonlar, maske ve W'lerle yeniden kurdu. I′ değerleri TR-7 ile
eşleşti; dördüncü kümenin sonunda 1 sn fark var. Tablo, her kümede bayraklanan istasyon sayısını gösterir.

| Küme (I′, UTC) | İstasyon | K0 | K1 | K2 | K3 | Taban | Not |
|---|---|---|---|---|---|---|---|
| 06:13:29–06:17:29 | 10 | 9 → atılır | 0 | 0 | 0 | yok | r 0,06–0,42; K1 kalıntısı 0,21–0,61 |
| 06:20:57–06:23:51 | 10 | 10 → atılır | 0 | 1 | 1 | yok | r 0,11–0,63 |
| 06:25:35–06:26:37 | 7 | 7 → atılır | 2 | 0 | 2 | yok | |
| 06:41:38–06:45:09 | 9 | 9 → atılır | 3 | 0 | 3 | **atılır** | |
| Saf telesismik P aralığı 05:57:43–06:05:57 (sahte W) | 10 | 10 → atılır | 10 (K0'a düşer) → atılır | 9 → atılır | 9 → atılır | yok | r 0,44–0,84 |

Okuma:
- K1–K3'ün üçü de ilk üç kümeyi korur ve saf telesismik kümeyi atar. TR-7'nin metni bu kurallardan biriyle yazılmış
  olsaydı, K1 aralığıyla kesişen 06:13:29 kümesi (b) dalını açardı.
- **Bu bir pozitif kontrol sonucu değildir.** Kurallar bu verinin tanısından sonra yazıldı, yani veri geliştirme verisidir.
- Kümenin tremor olduğu (Hill 2013) ya da başka bir şey olduğu bu sınamayla gösterilemez.
- Parkfield negatif pencereleri: TR-7'de sızıntıyla atılan küme yoktu (`tr7_algilama_K1-negatif.jsonl`: 10 pencerede
  4 küme, hepsi sağ). K1–K3, K0'ın bayrakladığının alt kümesini bayrakladığı için f_PK = 2/10 değişmez.

### 4.6 Sonraki tur (TR-7b dondurulmadan önce; hepsi sonradan, yani sonuçlar görüldükten sonra, önerilmiştir)

1. **Y3'ün ayrıştırıcısı.** Bölgesel koda tekdüze söner, tremor sönmez. Önerilen ek bayrak: aşım saniyelerinde
   L_d'nin zamana göre eğimi < 0 ve L ile L_d'nin eğimleri aynı işaretli.
   - Bu bayrak yalnız K1'in "tremor" dediği kümelere uygulanır.
   - Bu "K4 = K1 ∧ ¬(tekdüze sönüm)" demektir.
   - Simetriyi sağlamak için Q referansı negatif pencerelerde de aynı takvim aralığından hesaplanır. Orada telesismik
     sinyal olmadığı için doğru hiç kurulmaz ve K0'a düşülür. Bu asimetri açıkça yazılmalı ya da kaldırılmalıdır.
2. **Yapay setin gerçekçiliği.** Y2/Y3'ün telesismik modeli yalnız Tohoku'nun P aralığına göre kalibre edildi (§5).
   Kör olaylar Mw 7,6–9,0 arasındadır. Daha küçük tetikleyicilerde Q referansı 4σ_d'yi 30 sn aşmayabilir; K1 o zaman
   K0'a düşer. Kör olay düzeylerini kapsayan bir genlik ızgarası eklenmelidir (a_y 1–10).
3. **Y1 'sabit' biçimi** (2–8 Hz telesismik sinyal 0,5–1 Hz kadar yavaş sönüyor): Hiçbir kural tremoru ayıramadı, çünkü
   W boyunca tek küme oluşuyor. Bu, küme tanımının (§6.3) sınırıdır, sızıntı kuralının değil. Bilgi satırı olarak kalır.
   Bu biçim gerçekteyse (incelemeci denetlemeli) büyük tetikleyicilerde tremor ölçülemez.
4. Yeni tur, bu taslağın tohumlarından bağımsız iki yeni tohumla koşulur. Seçim ölçütü değişmez.

## 5. Yapay denetim seti (TR-7 §7.1'e eklenenler)

TR-7 §7.1'in D1–D15 satırları ve bantları aynen kalır. Sızıntı kuralı değiştiği için D7, D7b, D7c ve D7d seçilen
kuralla yeniden koşulur. Yeni satırlar Y1, Y2 ve Y3'tür.

**Yapay ortam:** 20 Hz, FFT ile 4 kutuplu ileri-geri Butterworth, 3 istasyon, 3 bileşen, Gauss gürültü. Zaman ekseni:
R 3600 sn, Q 900 sn, W 1900 sn. Her satırda 100 pencere vardır. Tohumlar 20261116 / 7171.

**Telesismik model:** Beyaz taşıyıcı kullanılır; iki bandın genliği ayrıdır.
- Genlikler: 2–8 Hz a_y·e_y(t), 0,5–1 Hz κ·a_y·e(t).
- e(t) şunların toplamıdır:
  - P'de 1 olup 150 sn'de e-katlı sönen koda;
  - 0,1 taban;
  - artçı P darbeleri: Poisson, ortalama 120 sn arayla; genlik 0,1·LN(0, 0,5); 60–180 sn sönüm.
- Biçimler: 'egim' biçiminde e_y = e·exp(−t/600 sn), 'sabit' biçiminde e_y = e.

**Kalibrasyon** (geliştirme verisi; yalnız tetikleyicinin W'den önceki P aralığı):
- P tepesi Δ_y ≈ 1,0, Δ_d ≈ 2,1 → a_y = 10, κ = 12,5.
- P'den 7 dk sonra Δ_y ≈ 0,1–0,2, Δ_d ≈ 1,2–1,35 → 150 sn sönüm, 0,1 taban ve 'egim'.

"Kalibre" diye geçen satırlar bu modeldir; ötekiler zorlama varyantlarıdır. Tremor TR-7 ile aynıdır: yarım sinüs, 300 sn,
20 sn periyot, A_etkin.

**Satır tanımları:**
- Y1: kalibre telesismik sinyal + eş zamanlı tremor. Yalnız I′'su tremor aralığıyla kesişen kümeler sayılır.
- Y2: yalnız telesismik sinyal, tremor yok.
- Y3: kalibre telesismik sinyal + W içinde ×20 bölgesel koda (D7d gibi), tremor yok.

**Tablonun okunuşu:** Değerler "tohum 1 / tohum 2" biçimindedir. "Tam" = darbe + sızıntı adayı + taban ile, algılananlar
içinde atılma payı. "Sızıntı" = yalnız sızıntı adayıyla atılma payı.

| Satır | Şart | Algılama | K0 | K1 | K2 | K3 |
|---|---|---|---|---|---|---|
| D7 yarım A10 | tam ≤ 0,03 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7b patlama A3 | tam ≤ 0,03 | 1,00 / 0,98 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7b patlama A10 | tam ≤ 0,03 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7b patlama A30 | tam ≤ 0,03 | 1,00 / 1,00 | 0,00 / 0,01 | 0,00 / 0,01 | 0,00 / 0,01 | 0,00 / 0,01 |
| D7c düz A3 | sızıntı ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7c düz A10 | sızıntı ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7d koda x20 | sızıntı ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y1 tremor A3 + tele a_y10 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 1,00 / 1,00 | 0,06 / 0,01 | 0,00 / 0,00 | 0,06 / 0,01 |
| Y1 tremor A3 + tele a_y10 κ12.5 sabit | tam bilgi | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y1 tremor A10 + tele a_y10 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y1 tremor A10 + tele a_y10 κ12.5 sabit | tam bilgi | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y2 tele a_y10 κ12.5 egim | tam ≥ 0,95 | 0,24 / 0,29 | 1,00 / 1,00 | 1,00 / 1,00 | 0,33 / 0,17 | 1,00 / 1,00 |
| Y2 tele a_y10 κ12.5 sabit | tam ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y2 tele a_y20 κ6 sabit | tam ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y2 tele a_y5 κ25 sabit | tam ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 0,99 / 1,00 | 0,89 / 0,93 | 0,99 / 1,00 |
| Y3 koda x20 + tele kalibre | sızıntı ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 0,51 / 0,52 | 0,51 / 0,52 |

Notlar:
- Y2 kalibre satırında algılama 0,24 / 0,29'dur (24 ve 29 pencere). K2'de sağ kalan yanlış algılama bütün pencerelerin
  0,16 / 0,24'üdür.
- D1–D6b, D8–D15 sızıntı kuralına bağlı değildir. TR-7'deki değerleri aynen geçerlidir (TR-7 §7.1, Ek 1 E1.5a), ama
  koşu kodu değişeceği için tam KD yeniden koşulur.

## 6. Kör pozitif kontrol K1b (TR-7 §7.2'nin yerine)

**6.1 Olaylar** (`TR-7b_SAYIM.md` §4; seçim kuralı veri görülmeden: Chao 2012 Tablo S1, PKD PGV_T ≥ 0,027 cm/s):
- **P (kör pozitif, 10 olay):** Peru 2001, Denali 2002, Colima 2003, Tokachi-oki 2003, Sumatra 2004, Kuril 2006,
  Kuril 2007, Wenchuan 2008, Samoa 2009, Maule 2010.
- **N (kör "yayımlanmış tetiklenme yok", 2 olay):** Macquarie 2004, Peru 2007.
- Bilgi satırları: Kunlun 2001, Tonga 2006 (zayıf, tetiklemiş), Solomon 2007, Nias 2005 (eşik altı, tetiklememiş).
- Tohoku 2011 yalnız geliştirme satırıdır ve hiçbir dalı değiştirmez.

**6.2 Pencereler ve algılama.** Her olay için TR-7 §5 pencereleri istasyon başına Δ ile hesaplanır. Algılayıcı TR-7
§6.0–§6.5 aynen kullanılır; sızıntı kuralı §4'te seçilecek kuraldır. E1 maskesi TR-7 §6.5.1a aynen uygulanır; maske
payı olay başına önceden, yalnız katalogdan hesaplanır ve dondurulur. **Olay algılaması** şöyle tanımlanır: I′'su
[T0 + Δ/4,6 km/s, T0 + Δ/3,0 km/s] aralığıyla (iz ortasında; TR-7 K1 aralığının tanımı) kesişen ve ayıklamadan sağ
çıkan en az bir küme. Bu aralık olay başına saniyeye yuvarlanıp dondurulur.

**6.3 Negatif pencereler ve MDA.** Her P ve N olayı için 10 negatif pencere seçilir. Kural TR-7 §7.3 aynen; üreteç
`default_rng(20261116 + 1)`, olaylar T0 sırasıyla.
- N_PK = ≥ 3 istasyonu kalan negatif pencere sayısı; en çok 120.
- f_PK = bu pencerelerde W'nin herhangi bir yerinde algılama sayısı.
- MDA, TR-7 §7.4 aynen (pencere başına 3 başlangıç).

**6.4 Dallar** (sıra bağlayıcı). Tanımlar:
- n_P = ≥ 3 istasyonla taranan P olayı sayısı.
- X_P = algılama veren P olayı sayısı.
- X_N, N olayları için aynı sayı.
- p_üst ve X_min(n, f): TR-7 §8 tanımları; n = n_P, f = f_PK, N = N_PK.

Dallar:
- (a) n_P < 5 → **"ölçü sınanamadı (Parkfield verisi yok)"**.
- (b) X_P ≥ max(⌈n_P/2⌉, X_min(n_P, f_PK)) → **"K1b GEÇTİ"**. Ek etiketler:
  - FAR_PK = f_PK/N_PK > 0,30 ise ya da (|N| ≥ 1 ve X_N/|N| ≥ X_P/n_P) ise **"geçti, ayırt edici değil"** yazılır.
    Bu durumda Marmara'da "VAR" verilemez.
  - Algılama veren P olaylarının hepsinde bütün algılama kümeleri TR-7 §7.2 (b′) (i) ya da (ii) durumundaysa (çekirdek
    fazları olay başına iasp91 ile) **"geçti, belirsiz"** yazılır. Etkisi TR-7 (b′) aynen.
- (c) (b) sağlanmıyorsa ve MDA tanımlıysa ve A90_PK ≤ 100 µm/s ise → **"ölçü sınanamadı (kör Parkfield olaylarında
  tetiklenmiş tremor ölçütü karşılamadı: X_P = [..] / n_P = [..]; A90_PK = [..] nm/s)"**.
- (d) Öteki durumlar → **"ölçü sınanamadı (yöntem)"**.

(b) dışındaki her dalda Marmara verisi indirilmez. Uygulama hatası yolu TR-7 §7.2 aynen, bir kez.

Bilgi satırları:
- Olay başına algılama, küme ve atılma nedenleri.
- Kuyu sınıfının aynı dalları.
- Tohoku geliştirme satırı.
- Olay başına A_PK.
- τ_ölç / kaba τ.

**Parkfield modülasyonu geçti** = algılama veren P olaylarının en az ⌈X_P/2⌉'sinde en az bir algılama kümesinde
p ≤ 0,01. Geçmezse ya da ölçülemezse etkisi TR-7 §7.2 aynen: "VAR" verilemez.

**6.5 Neden bu dallar.**
- Tek bir olaya dayanan K1, tek olayın kendine özgü koşullarına (Tohoku: %65 maske, M9 düşük frekansı) teslim oldu. On
  olayın yarısı ve binom şartı, hem duyarlılığı hem yanlış alarmı sınar.
- N olayları literatürde "görülmedi"dir; görsel incelemeden daha duyarlı bir algılayıcının onlarda algılama vermesi
  hata kanıtı değildir. Bu yüzden N tek başına kalma şartı değildir. Yalnız P'den ayırt edilemiyorsa "ayırt edici değil"
  etiketini koyar.

## 7. Marmara aşamaları

TR-7'nin Marmara tarafı aynen kalır:
- birimler (§4.1), K0 ve bant (§4.2), önsayım (§4.3);
- pencereler (§5), işleme zinciri (§6, yalnız §6.5 madde 3 bu metnin §4'üyle değişir);
- K2 negatif kontrol (§7.3), MDA (§7.4), kestirici (§7.5);
- hüküm kuralları, X_min tabloları, kuyruk eşikleri, hüküm kalıpları ve özet cümleleri (§8);
- çıktı tabloları (§9), koşu sırası ve tek koşu kuralı (§10; aşama adlarında K1 → K1b), §12, §13, Ek 1 E1.1–E1.3.

TR-7 §8 sıra 1'de "K1 (a), (c) ya da (d)" yerine "K1b (a), (c) ya da (d)" okunur. Hüküm kalıplarında "Parkfield–Tohoku'da
τ_ölç / kaba τ" yerine "Parkfield kör olaylarında τ_ölç / kaba τ (medyan)" okunur. Bunlar dışında cümleler aynen kalır.

**Marmara aşamaları ancak K1b (b) dalında açılır** ("geçti", "ayırt edici değil" ya da "belirsiz" etiketleriyle; etkileri
TR-7 özet tablosu aynen). Aşama sırası:

manifest → K1b-indirme (P, N ve negatifleri) → K1b-negatif → K1b-algılama → Marmara-indirme → Marmara-negatif →
Marmara-algılama → hüküm

Kurallar:
- TR-7 §10.6'nın tek koşu, durdurma ve sürdürme kuralları aynen.
- TR-7'nin Marmara körlüğü bugün tamdır: hiçbir Marmara dalga formu işlenmedi. TR-7b koşusuna kadar da öyle kalmalıdır.

## 8. Açık riskler ve bağımsız incelemecinin bakması gerekenler

1. **Çatallanan yollar.** Kurallar Tohoku'nun tanısından sonra yazıldı. K3, Y3 ve Y1 'sabit'in bilgiye indirilmesi
   20 pencerelik bir ön denemeden (tohum 11) sonra eklendi (`tr7b_yapay.py` başlığındaki açıklık notu).
   - İncelemeci şunları denetlemeli: (i) ön denemenin bir ayar adımı olduğunu; (ii) seçim ölçütünün tam koşudan önce
     yazıldığını; (iii) Y1 'sabit'in bilgiye indirilmesinin gerekçesini (§4.6 madde 3).
   - Gerekçe şudur: W boyunca süren tek kümede tremor, hiçbir sızıntı kuralıyla ayrılamaz.
2. **Telesismik modelin tek kalibrasyonu.** Model yalnız Tohoku–Parkfield'ın P aralığından ve 12 istasyonun medyanından
   kalibre edildi. Sonuçlar bu kalibrasyona duyarlı:
   - 'egim' ile 'sabit' arasındaki fark bütün kuralların Y1 sonucunu 0'dan 1'e taşıyor.
   - İncelemeci, 2–8 Hz telesismik kodanın 0,5–1 Hz'ten hızlı söndüğü varsayımını (06:04'te Δ_y 0,1–0,2 iken Δ_d 1,2–1,35)
     tek olaya dayanan bir varsayım olarak değerlendirmeli.
3. **K1'in asimetrisi.** K1 ve K3, tetikleyici pencerelerinde tetikleyicinin kendi Q referansını kullanır. Negatif
   pencerelerde referans yoktur ve K0'a ya da K2'ye düşer. FAR (f/N) bu yüzden tetikleyici penceresindeki kuralla tam
   aynı ölçülmez. K1 ve K3, K0'ın alt kümesini bayrakladığı için tetikleyici pencereleri negatiflere göre daha "serbest"
   olabilir. Bu, "VAR" yönünde bir yanlılıktır ve incelemecinin en çok bakması gereken noktadır.
4. **Y3 (koda + telesismik).** Hiçbir aday geçmedi (en iyi K2 ve K3: 0,51–0,52). Kataloglanmamış bölgesel deprem kodası
   (M < 4 ya da 1000 km ötesi) büyük tetikleyici pencerelerinde tremor sanılabilir.
5. **Literatürle kurulmuş pozitif kontrolün sınırı.** P olaylarının "tetikledi" işareti görsel incelemedir ve büyük ölçüde
   PKD ve HRSN kuyu kayıtlarına dayanır (Peng 2009: PKD, NCSN, 13 HRSN). Liste sınıfı yüzey ağıdır. Tohoku'da tremor yüzey
   ağında da kümelendi (geliştirme), ama öteki olaylarda yüzey ağının gürültüsünde görünmeyebilir. Bu durumda (c) dalı
   yine "yüzey ağı görmedi" der, yöntem hatası demez.
6. **Kör olaylar arası bağımlılık.** Kuril 2006 ve 2007 aynı bölgeden ve 2 ay arayla geldi. Sumatra 2004, Macquarie 2004'ten
   3 gün sonra. Binom şartı bağımsızlık varsayar.
7. **Varlık sayımının kesinliği.** Availability gün dosyası düzeyindedir; CI istasyonları sayılamadı; 2001–2003 NC
   istasyonlarının sürekli arşivi yalnız bu yanıta dayanıyor (SAYIM §5). Koşudaki gerçek örtü sayıyı düşürebilir. n_P < 5
   ise (a) dalına düşülür.
8. **E1 maskesi.** Sumatra 2004, Maule 2010 ve Kuril olaylarının artçı dizileri W'nin büyük kısmını maskeleyebilir
   (Tohoku'da %58–65). Maske payları dondurmadan önce yalnız katalogla hesaplanmalıdır.
9. **Kaba τ ve ölçek.** TR-7 §12 aynen. Değişen yok.
10. **Tek koşu ve Marmara körlüğü.** TR-7b, TR-7'nin Marmara birimlerini ilk kez görecektir. TR-7b'nin Marmara sonucu,
    TR-7'nin "ölçü sınanamadı" hükmünü geriye dönük değiştirmez; ayrı bir ön kaydın sonucudur.
11. **İncelemecinin yeniden üretmesi gerekenler:**
    - `tr7b_yapay.py` iki tohumla (yaklaşık 15 dakika, 2 süreç);
    - `tr7b_gelistirme.py` (TR-7 zarf deposu gerekir);
    - `tr7b_sayim.py` (ağ gerekir, yaklaşık 15 dakika).

## 9. Doğrulanamayanlar

- Peng 2009 ve Chao 2012'nin ek tablolarındaki istasyon başına ayrıntı: Peng 2009 ek tabloları okunmadı.
- 2011–2025 arası Parkfield'da tetiklenme bildiren ya da bildirmeyen olay listesi: Hutchison ve Poli 2021'den yalnız
  özet okundu.
- Shelly vd. 2011 (özet yok).
- Kör olaylarda W içi gerçek örtü.
- Kör olaylarda tremorun yüzey ağında hangi genlikte olduğu.
- Telesismik model parametrelerinin Tohoku dışındaki olaylara uyup uymadığı.

## 10. Yazarın beyanı (sınav öncesi, taslak düzeyinde)

Seçilecek kural §4.6'daki ek turla bulunursa, K1b için beklentiler:
- "GEÇTİ" 0,35;
- "geçti, ayırt edici değil ya da belirsiz" 0,20;
- (c) 0,35;
- (a)/(d) 0,10.

Kural bulunamazsa TR-7b dondurulmaz ve ZINCIR'e "kapı altında" olarak yazılır.

## 11. Tur 2 (16 Kasım 2026; koşudan ÖNCE yazıldı ve commit edildi)

Tur 1'de (§4.4) hiçbir aday geçmedi. Bu tur §4.6'da önerilen K4'ü ve onun simetrik biçimi K5'i sınar. Başka aday yoktur.
Kod: `kayit/turetme/tr7b/tr7b_yapay2.py`. `tr7b_yapay.py` (Tur 1) ve `tr7_cekirdek.py` değiştirilmeden içe aktarılır.
K0–K3 karşılaştırma için aynı pencerelerde yeniden hesaplanır, ama Tur 2'de seçilemez (Tur 1'de kaldılar).

Koşudan önceki tek çalıştırma, kodun çalıştığını gösteren bir duman sınamasıdır: tohum 1, iki pencere, F1 ve Y3 a_y 5
satırları. Sonucu tablolara girmez.

### 11.1 Aday tanımları

Tanımlar istasyonun kümedeki aşım saniyeleri üzerindedir. Δ_y, Δ_d, Q referansı ve K1 kalıntısı §4.2 ile aynıdır. Toplama
TR-7 ile aynıdır: istasyonların ≥ yarısı bayraklıysa küme atılır.

- **ρ** = Spearman(L, zaman), aşım saniyelerinde. 10 saniyeden az varsa tanımsızdır.
- **Sönüm şartı** = Δ_d ≥ Δ_y **ve** ρ ≤ −0,7. Amaç tekdüze sönen bölgesel kodayı yakalamaktır. −0,7 önceden sabittir;
  veriyle seçilmedi.
- **K4 (asimetrik)** = K1 **veya** sönüm şartı. K1, Q referansı varsa kalıntı < 2σ şartıdır, yoksa K0'dır. Tetikleyicisiz
  pencerede K4 = K0 olur.
- **K5 (simetrik)** = Δ_d ≥ Δ_y **ve** (kalıntı < 2σ **veya** ρ ≤ −0,7).
  - Kalıntı Q doğrusundan hesaplanır.
  - Q'da L_d − m_d > 4σ_d olan saniye 30'dan azsa doğru a = b = 0 alınır. O zaman kalıntı = L − m ≥ 4σ olur ve kalıntı
    şartı hiç sağlanmaz.
  - Tetikleyici ve negatif pencerelerde formül aynıdır. Fark yalnız verinin kendisinden gelir.

### 11.2 Satırlar ve şartlar

Pencere sayısı 100'dür; iki **yeni** tohum kullanılır: **20261117** ve **9393**. Telesismik model ve kalibrasyon §5 ile
aynıdır.

"Sağ" = en az bir sağ küme veren pencere / bütün pencereler. Bu tanım, algılamanın az olduğu hücrelerde "algılananlarda
atılma" payının kararsız kalmasını önler. Algılama 1'e yakınsa "atılma ≥ 0,95" ile eşdeğerdir.

| Satır | Hücreler | Şart |
|---|---|---|
| D7 | yarım sinüs, A 10 | tam atılma ≤ 0,03 |
| D7b | patlama, A 3 / 10 / 30 | tam atılma ≤ 0,03 |
| D7c | düz, A 3 / 10 | sızıntıyla atılma ≤ 0,05 |
| D7d | koda ×20 | sızıntıyla atılma ≥ 0,95 |
| Y1 | tremor A 3 / 10 + tele 'egim', a_y 2 / 5 / 10, κ 12,5 (6 hücre) | tam atılma ≤ 0,05 (I′'su tremorla kesişen kümeler) |
| Y1 'sabit' | a_y 10 | bilgi |
| Y2 | yalnız tele; a_y 2 / 5 / 10 × κ 6 / 12,5 / 25 × 'egim' / 'sabit' (18 hücre) | sağ ≤ 0,05 |
| Y3 | koda ×20 + tele 'egim', κ 12,5, a_y 2 / 5 / 10 | sızıntıyla atılma ≥ 0,95 |
| F1 | tetikleyicisiz pencere, kentsel gürültü, tremor yok | sağ ≤ 0,05 |
| F2 | tetikleyicili pencere (tele 'egim', a_y 10, κ 12,5), kentsel gürültü, tremor yok | sağ ≤ 0,05 ve sağ(F2) − sağ(F1) ≤ 0,02 |

Kentsel gürültü TR-7 §7.1 ile aynıdır: 2–8 Hz'te ≈ 300 sn'lik rastgele ×exp(0,35 z).

**Asimetri.** F1/F2 çifti, asimetrinin yanlış alarm oranına etkisini doğrudan ölçer. Tetikleyicili ama tremorsuz bir
pencerenin sağ kalma oranı, negatif pencerelerden ölçülen orandan en çok 0,02 fazla olabilir. K4 bu şartı geçse bile
asimetriktir. Seçimde K5'in önünde gelmez.

### 11.3 Seçim ölçütü

1. Bir aday, iki tohumda da §11.2'nin bütün şart satırlarını sağlıyorsa kabul edilebilirdir.
2. Kabul edilebilirlerden önce simetrik olan (K5) seçilir. İkisi de simetrik ya da ikisi de asimetrikse, şartlara göre en
   kötü pay farkı en büyük olan seçilir.
3. Seçilen kural §4'ün yerine geçer. Ön kayıt taslağı bağımsız incelemeye hazırlanır; dondurulmaz.
4. **Hiçbir aday geçmezse** TR-7b **"kapı altında (kural bulunamadı)"** kalır. Üçüncü tur yalnız yeni bir fikirle açılır:
   K4/K5'in eşiklerini değiştirmek yeni fikir sayılmaz.

### 11.4 Sonuç (koşudan sonra)

Koşu 100 pencereyle ve iki tohumla (20261117 / 9393) yapıldı. Kod commit 1e03d20'dekiyle aynıdır.
- Çıktılar: `tr7b_yapay2_t1.json` (sha256 8fc735c9…5476), `tr7b_yapay2_t2.json` (sha256 d4ec8631…860d).
- Ölçüt uygulayıcı: `tr7b_tur2_secim.py` (sha256 be830a18…ed08).
- Değerler "tohum 1 / tohum 2" biçimindedir. Şart sütunu hangi ölçünün gösterildiğini söyler: tam atılma, sızıntıyla
  atılma ya da sağ.
- K0–K3 yalnız karşılaştırma içindir.

| Satır | Şart | Algılama | K0 | K1 | K2 | K3 | K4 | K5 |
|---|---|---|---|---|---|---|---|---|
| D7 yarım A10 | tam ≤ 0,03 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7b patlama A3 | tam ≤ 0,03 | 0,99 / 0,99 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7b patlama A10 | tam ≤ 0,03 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7b patlama A30 | tam ≤ 0,03 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7c düz A3 | sızıntı ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7c düz A10 | sızıntı ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| D7d koda x20 | sızıntı ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y1 A3 a_y2 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y1 A3 a_y5 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y1 A3 a_y10 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 1,00 / 1,00 | 0,05 / 0,06 | 0,00 / 0,00 | 0,05 / 0,06 | 0,05 / 0,06 | 0,05 / 0,06 |
| Y1 A10 a_y2 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 0,22 / 0,17 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y1 A10 a_y5 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 0,97 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y1 A10 a_y10 κ12.5 egim | tam ≤ 0,05 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y1 A3 a_y10 κ12.5 sabit | bilgi | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y1 A10 a_y10 κ12.5 sabit | bilgi | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y2 a_y2 κ6 egim | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y2 κ6 sabit | sağ ≤ 0,05 | 0,79 / 0,78 | 0,00 / 0,00 | 0,00 / 0,00 | 0,63 / 0,66 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y2 κ12.5 egim | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y2 κ12.5 sabit | sağ ≤ 0,05 | 0,73 / 0,86 | 0,00 / 0,00 | 0,00 / 0,00 | 0,58 / 0,67 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y2 κ25 egim | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y2 κ25 sabit | sağ ≤ 0,05 | 0,82 / 0,69 | 0,00 / 0,00 | 0,00 / 0,00 | 0,64 / 0,54 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y5 κ6 egim | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y5 κ6 sabit | sağ ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,02 / 0,01 | 0,11 / 0,09 | 0,01 / 0,01 | 0,02 / 0,00 | 0,02 / 0,00 |
| Y2 a_y5 κ12.5 egim | sağ ≤ 0,05 | 0,01 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,01 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y5 κ12.5 sabit | sağ ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,01 | 0,14 / 0,13 | 0,00 / 0,01 | 0,00 / 0,01 | 0,00 / 0,01 |
| Y2 a_y5 κ25 egim | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y5 κ25 sabit | sağ ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,07 / 0,11 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y10 κ6 egim | sağ ≤ 0,05 | 0,21 / 0,21 | 0,00 / 0,00 | 0,00 / 0,00 | 0,19 / 0,15 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y10 κ6 sabit | sağ ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y10 κ12.5 egim | sağ ≤ 0,05 | 0,24 / 0,26 | 0,00 / 0,00 | 0,00 / 0,00 | 0,17 / 0,19 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y10 κ12.5 sabit | sağ ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y10 κ25 egim | sağ ≤ 0,05 | 0,18 / 0,29 | 0,00 / 0,00 | 0,00 / 0,00 | 0,10 / 0,26 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y2 a_y10 κ25 sabit | sağ ≤ 0,05 | 1,00 / 1,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| Y3 koda x20 + tele a_y2 | sızıntı ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y3 koda x20 + tele a_y5 | sızıntı ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 0,00 / 0,00 | 0,79 / 0,78 | 0,80 / 0,78 | 1,00 / 1,00 | 1,00 / 1,00 |
| Y3 koda x20 + tele a_y10 | sızıntı ≥ 0,95 | 1,00 / 1,00 | 1,00 / 1,00 | 0,01 / 0,01 | 0,49 / 0,41 | 0,57 / 0,50 | 1,00 / 0,99 | 1,00 / 0,99 |
| F1 tetikleyicisiz kentsel | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |
| F2 tetikleyicili kentsel | sağ ≤ 0,05 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 | 0,00 / 0,00 |

F2 − F1 (asimetrinin yanlış alarm oranına etkisi): bütün adaylarda 0,00 / 0,00. Kentsel gürültüde, tremorsuz pencerelerde,
tetikleyici olsun olmasın, hiçbir kural sağ küme bırakmadı.

**Karar: kabul edilebilir aday yok. TR-7b "kapı altında (kural bulunamadı)" kalır.**
- K4 ve K5, 36 şart satırının 35'ini ve F2 − F1 şartını iki tohumda geçti. Bunların arasında 18 Y2 hücresinin hepsi (sağ 0,00–0,02),
  Y3'ün üç düzeyi (0,99–1,00) ve F1/F2 var.
- Tek bir hücrede kaldılar: **Y1, tremor A_etkin 3 + kalibre telesismik sinyal (a_y 10, κ 12,5, 'egim'), tam atılma
  0,05 / 0,06** (şart ≤ 0,05). Tohum 2'de 100 pencerenin 6'sında tremor kümesi atıldı. En kötü pay −0,01'dir.
- Nedeni K1'in kalıntı bileşenidir: K1 aynı hücrede 0,05 / 0,06 veriyor; K2'nin r şartı burada 0,00.
- Ölçüt önceden yazıldığı için bu fark bir yuvarlama sayılmaz. Eşik gevşetilmez.
- Asimetri riski bu sınamada ölçülebilir bir etki göstermedi (F2 − F1 = 0). Ama K4 seçilmiş olsaydı bile simetrik K5'in
  önüne geçemezdi.

Bu sonuç §11.3 madde 4'ü işletir. Üçüncü tur yalnız yeni bir fikirle açılır; K1 kalıntı eşiğini (2σ) ya da ρ eşiğini
değiştirmek yeni fikir sayılmaz. Ön kayıt taslağı bu hâliyle bağımsız incelemeye gönderilmez, çünkü seçilmiş bir kural
yoktur. Öteki bölümler (§3, §6, §7) taslak olarak kalır.

## 12. Tur 3 (16 Kasım 2026; koşudan ÖNCE yazıldı ve commit edildi)

Tur 1 (§4.4) ve Tur 2 (§11.4) sonuçsuz kaldı. Bu tur yalnız **yeni bir bilgi kaynağını** sınar: frekans bandı oranı
değil, **kaynağın yeri**. Telesismik enerji diziyi yüksek görünür hızla (≥ ~8 km/s) geçer. Tremor ve bölgesel koda yerel
kaynaklıdır; istasyonlar arası zarf gecikmeleri S hızıyla (~3,5 km/s) bir yerel kaynağa uyar. Tek aday K6'dır.
K1'in 2σ'sı, ρ eşiği (−0,7) ve bütün şart eşikleri Tur 2 ile aynıdır.

Kod: `kayit/turetme/tr7b/tr7b_yapay3.py`. `tr7b_yapay.py`, `tr7b_yapay2.py` ve `tr7_cekirdek.py` değiştirilmeden içe
aktarılır.

### 12.1 Üreteç değişikliği: gerçekçi gecikmeler

Tur 1–2 üreteci istasyonlar arası gecikme içermiyordu (bütün istasyonlarda aynı zarf). Bu turda:
- **İstasyonlar:** TR-7 Parkfield listesinin `ilk12` istasyonları ize göre (birinci temel bileşen) güneyden kuzeye
  sıralanır; 0, 2, 4, 6, 8, 10. sıradakiler alınır: NC.PTR, NC.PSN, NC.PGH, NC.PHF, NC.PL11B, NC.PPT (iz doğrultusunda
  ≈ 68 km açıklık). Tur 1–2'de 3 istasyon vardı.
- **Tremor:** kaynak, iz (4 noktalı çizgi, ≈ 82 km) üzerinde düzgün dağılımlı bir noktanın U[20, 25] km altındadır;
  gecikme r_i / 3,5 km/s.
- **Bölgesel koda (D7d, Y3):** dış merkez dizi ortasından U[20, 150] km, azimut U[0, 360), derinlik 10 km; r_i / 3,5 km/s.
- **Telesismik sinyal (Y1, Y2, Y3, F2):** dizi doğrultusunda düzlem dalga, görünür hız U[8, 25] km/s, yönü rastgele.
  Taşıyıcılar istasyonlar arasında bağımsızdır (Tur 1 gibi); yalnız zarf gecikir.
- Gecikmeler 20 Hz zarfa doğrusal ara değerlemeyle uygulanır. Genlikler istasyonlar arasında eşittir.
- **Gecikme ölçüm gürültüsü** ayrıca eklenmez, çünkü gecikmeler gürültülü yapay zarflardan (1 Hz) ölçülür; ölçüm
  hatası böylece kendiliğinden içeridedir.

**Üreteç denetimi.** D7, D7b ×3, D7c ×2 ve D7d satırları aynı 6 istasyonla bir kez gecikmeli, bir kez gecikmesiz koşulur.
Üreteç K0–K5 için **kararlı** sayılır ⇔ her iki tohumda bu 7 satırın her birinde K0–K5'in şartı geçme/kalma durumu aynıdır
**ve** gecikmeli ile gecikmesiz paylar arasındaki fark ≤ 0,03'tür. Kararlı değilse K6 seçilemez (gecikmeler, eski
kuralların sonucunu değiştirmiş olur; bu durumda önce o açıklanmalıdır).

### 12.2 K6'nın tanımı

Küme düzeyinde, simetrik: her pencerede (tetikleyici olsun olmasın) aynı hesap.
1. Kümenin her istasyon çifti (i, j) için I üzerinde (maskesiz, tanımlı saniyeler) Pearson(L_i(t), L_j(t + k)),
   k = −10…+10 sn. En büyük değer ≥ 0,5 ise çift kullanılır; gecikme τ_ij = k* + parabolik ara değerleme (k* ± 1
   komşularıyla).
2. Kullanılan çift < 3 ya da kapsanan istasyon < 3 ise konum "belirsiz"dir; küme telesismik sayılmaz.
3. (a) **Düzlem dalga**, dizi doğrultusunda: τ_ij = s (u_j − u_i), en küçük kareler; RMS_a; v_a = 1/|s|.
   (b) **Yerel kaynak**: iz üzerinde her iki uçtan 10 km uzatılmış, 1 km adımlı noktalar × derinlik {15, 20, 25} km,
   v = 3,5 km/s; τ_ij = (r_j − r_i)/v; RMS_b = ızgaradaki en küçük RMS.
4. Konum **telesismik** ⇔ RMS_a ≤ 1,0 sn **ve** RMS_a < RMS_b **ve** v_a ≥ 6 km/s.
5. Küme sızıntı nedeniyle atılır ⇔ konum telesismik **veya** istasyonların ≥ yarısında sönüm şartı (Δ_d ≥ Δ_y ve
   ρ ≤ −0,7; §11.1 ile aynı). Bölgesel koda için sönüm şartı korunur (koda yerel bir kaynaktır, konum onu ayırmaz).
6. Darbe ve taban kuralları TR-7 ile aynıdır.

K6'da K1 kalıntısı (2σ) ve Q referansı **kullanılmaz**; Tur 2'deki tek başarısızlığın nedeni oydu.

**Koşudan önceki çalıştırmalar (açıklama).** Kodu sınamak için atılan tohumlarla (1, 2, 3) toplam ≈ 150 pencere
koşuldu: D7 yarım A10, D7b patlama A3, D7d, Y1 A3 a_y10 'egim' (10 pencere) ve Y2 a_y 5/10 'egim'/'sabit' (20'şer).
Bu sınamada madde 4'ün ilk tanımı yalnız "RMS_a < RMS_b ve v_a ≥ 6" idi. Y1 A3 a_y10 'egim'de tremor ile tele
enerjisinin karıştığı kümelerde iki model de kötü uyuyordu (RMS_a ve RMS_b ≈ 3–7 sn) ve 10 pencerenin 4'ünde tremor
kümesi "telesismik" çıktı. Bunun üzerine "uyum" sözcüğü sayıya bağlandı: **RMS_a ≤ 1,0 sn** (1 Hz zarfın çözünürlüğü;
saf telesismik 'sabit' kümelerde RMS_a çoğunlukla 0,2–0,5 sn, saf tremor kümelerinde RMS_b 0,1–0,5 sn). Bu eşik
ayarlanmadı, yalnız bir kez konuldu; sonra başka bir değişiklik yapılmadı. Bu sınamanın sayıları tablolara girmez.

### 12.3 Satırlar ve şartlar

Satırlar ve şartlar §11.2 ile **aynıdır** (D7 tam ≤ 0,03; D7b tam ≤ 0,03; D7c sızıntı ≤ 0,05; D7d sızıntı ≥ 0,95; Y1
'egim' 6 hücre tam ≤ 0,05; Y1 'sabit' bilgi; Y2 18 hücre sağ ≤ 0,05; Y3 3 hücre sızıntı ≥ 0,95; F1, F2 sağ ≤ 0,05 ve
sağ(F2) − sağ(F1) ≤ 0,02). Ek olarak §12.1'deki üreteç denetimi satırları (bilgi + kararlılık şartı).

- **Pencere sayısı: 200** (her satır, her tohum). Koşudan önce sabittir.
- **İki yeni tohum: 20261118 ve 5151.** Her tohum iki süreçte koşulur: bölüm 1 (D7 satırları, gecikmesiz denetim, Y1)
  tohumla, bölüm 2 (Y2, Y3, F1, F2) tohum + 1000003 ile.
- Çıktılar: `kayit/turetme/tr7b/tr7b_yapay3_t{1,2}_b{1,2}.json`.
- K0–K5 yalnız karşılaştırma ve üreteç denetimi içindir.

### 12.4 Seçim ölçütü

1. Seçilebilir tek aday K6'dır.
2. K6 kabul edilir ⇔ iki tohumda da §12.3'ün bütün şart satırlarını sağlar **ve** §12.1'in üreteç denetimi kararlıdır.
3. Kabul edilirse K6 §4'ün yerine geçer. Ön kayıt taslağı bağımsız incelemeye hazırlanır (kör kontrol K1b §6 ve
   Marmara aşamaları §7 aynen); **dondurulmaz**.
4. **Kabul edilmezse** TR-7b **"kapı altında (kural bulunamadı), iki tasarım turu sonuçsuz"** olarak bekler.
   **Dördüncü tur açılmaz.**
