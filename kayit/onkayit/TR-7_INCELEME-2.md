DÜZELTMEYLE KABUL

# TR-7 ön kayıt: bağımsız inceleme 2 (son tur)

İncelenen: `TR-7_tetiklenmis-tremor_ONKAYIT.md` (TASLAK sürüm 2, 12 Kasım 2026). Karşılaştırılan: `TR-7_INCELEME-1.md`.
Dayanaklar: `TR-7_SAYIM.md`, `kayit/turetme/tr7/` (listeler, `tr7_e1_maske.*`, `tr7_negatif_pencere.*`,
`tr7_parkfield_varlik.*`, `tr7_onkayit_denetim2*.py/.json`, `tr7_onkayit_sayilar.*`, `tr7_inc1_*.py`).

Bu inceleme ne yaptı, ne yapmadı: hiçbir dalga formu istenmedi, indirilmedi, açılmadı (varlık yoklaması dahil). Ağa
yalnız `kayit/oa.py` ile dört kez çıkıldı (üç özet, bir arama). Katalog önhesapları yeni sorgu yapılmadan, kök oturumun
karalama dizinindeki ComCat önbelleğinden yeniden üretildi; önbellek dosyalarının sha256'ları dondurulan özetlerdekiyle
aynı. Yapay denetimler `python3 -I -B` ile, bağımsız tohumlarla yeniden koşuldu. İnceleme betikleri ve çıktıları depo
dışında: `/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/inc2_tr7/` (`tr7_inc2_taban.py`,
`tr7_inc2_taban_ek.py`, `rr_*.json`, `o4b_n100_*.json`). Taslak değiştirilmedi. Git işlemi yapılmadı. Depoya bu rapor
dışında dosya eklenmedi. `__pycache__` bırakılmadı.

## Hüküm

**DÜZELTMEYLE KABUL.** Sürüm 2, İNCELEME-1'in 3 engelleyici, 8 önemli ve 7 küçük bulgusunun hepsini işlemiş. Metin
ile §18 değişiklik listesi tutarlı, sayılar dosyalarla birebir. Sapmaların (§17) dokuzu gerekçeli ve kabul edilebilir.
S1 (E1-C) da kabul edilebilir, ama aşağıdaki eklerle.

Ancak üç yer dondurmadan önce düzeltilmeli:

- **İ2-E1. Taban kayması kuralı (3a) Tohoku pencerelerinde hiç çalışamaz.** E1 maskesi, Tohoku'nun S1–S4 ve S7
  pencerelerinde W'nin son 144–222 sn'sini kapatıyor. Maskeli saniye aşım sayılmadığı için hiçbir parça "W sonu −
  60 sn"ye ulaşamaz. Bu, İNCELEME-1 Ö4'ün sabah artışı tablosundaki ilk birimdir. Yapay sınamada W içinde ×2 yükselen
  gürültü, 3a olmadan %100 sahte tutarlı küme veriyor. 3a bunların %100'ünü atıyor, ama W'nin son 120 sn'si maskeliyken
  sürüm 2 metniyle %0'ını atıyor.
- **İ2-E2. Dört KD şartı yanlış yerde ya da hiç sınamıyor.** D6 ve D6b'nin şartı ×20'de konmuş, ama ×20'de olay
  algılanmıyor (algılama 0,00–0,03). Yani şart darbe kuralını sınamıyor. D6b ×100'ün doğru değeri (0,96–0,98) ise
  ≥ 0,95 bandının hemen sınırında; doğru kod bu bandı %8–14 olasılıkla kaçırır. D12b ×2 ve ×3'te yanlış kodu ayırmıyor.
  O4 hiç algılama üretmediği için 3a'yı sınamıyor. Düzeltme ayırt edici satırlardır: D6/D6b'de şart ×100'de, D12c
  deterministik maske sınaması, D15 3a için.
- **İ2-E3. Tek koşu aşamaları negatif pencere algılamasını kilidin dışında bırakıyor.** §7.4'e göre MDA ham veri
  bellekteyken yapılır. Bu yüzden negatif pencere algılaması ve MDA indirme sırasında hesaplanır. §10.6'nın aşama
  listesinde ise bunlar "Marmara-indirme" içinde kalıyor. Sonuç: FAR ve MDA görüldükten sonra koşu yeniden
  başlatılabilir. "Hiçbir algılama hesaplanmadan durur" cümlesi de bu aşamada uygulanamaz. Ayrıca durum dosyası
  yalnız commit ediliyor; oturum sıfırlanırsa push edilmemiş commit kaybolur (İNCELEME-1 Ö8'in kapattığı açık).

Önemli bulgular sekiz tane (İ2-Ö1–Ö8). En önemlisi İ2-Ö1 ve İ2-Ö2. **İ2-Ö1:** E1-C kabul, K1'e "belirsiz geçme"
etiketi eklenir. **İ2-Ö2:** "görülmedi"nin dışlama cümlesi, W'sinin yarıdan çoğu maskeli Tohoku birimini saymaz.
Bunlardan sonra üçüncü tura gerek yoktur. Bütün düzeltmeler metin, ek ayırt edici KD satırı ve bilgi/tanı satırıdır.
Yeni sayım, yeni liste ya da dalga formu erişimi gerekmez.

**Bağımsız olarak doğrulananlar.**

- **sha256.** §3 ve §18'de verilen 13 dosya sha256'sının hepsi aynı. Liste, Parkfield listesi, varlık ve özeti,
  negatif pencere csv ve özeti, E1 csv ve özeti, `tr7_onkayit_sayilar.json`, `denetim2.json`, `denetim2_ek.json`, dört
  girdi dosyası ve `comcat_m75.csv` (karalamada).
- **Negatif pencereler (170).** `tr7_negatif_pencere.py` bir kopyayla önbellekten yeniden koşuldu. Csv ve özet
  **bit düzeyinde aynı** çıktı. Betik yalnız ComCat yanıtını, takvimi (zoneinfo) ve `default_rng`'yi kullanıyor;
  dalga formuna hiç dokunmuyor. Seçim gerçekten yalnız takvim ve katalogdan. Bilgi: Tohoku'nun 10 penceresinden 6'sı
  ana şoktan sonra (d = 4…12), Parkfield'ınkilerin hepsi önce. Bunun nedeni ABD'de 2011-03-13 yaz saati geçişi ve
  (iv) şartıdır.
- **E1 önhesabı.** `tr7_e1_maske.py` önbellekten yeniden koşuldu, csv ve özet **bit düzeyinde aynı**. 17 önbellek
  dosyasının sha256'ları özetteki değerlerle aynı.
- **E1 sayıları.** §4.3, §6.5.1a ve §17 S1 tablosundaki bütün E1-lit, B, C ve A sayıları json ile aynı.
- **Kombinatorik.** X_min tabloları (0,05 ve 0,05/3), p_min ve 0,0572 scipy ile bağımsız hesaplandı, aynı çıktı.
- **Parkfield listesi.** 56 / 52 istasyon, `ilk12`, 112 satır ve 120 HTTP isteği dosyalarla aynı.
- **Yapay denetimler.** Sekiz koşu, bağımsız tohumlar 777001–777008, 100'er pencere. Hepsi bandın içinde (§E).

---

## A. İNCELEME-1 bulgularının sürüm 2'de işlenişi

| Bulgu | İşlendi mi | Not |
|---|---|---|
| E1 | Evet, sapmayla (S1) | Madde 1a, önhesap §3.4, D12/D12b, maskeli pay çıktıda, K1 tanı satırı. Kodda olup metinde olmayan "±5 sn ikiz kayıt" kuralı → İ2-Ö4. D12/D12b'nin ayırt ediciliği → İ2-E2. |
| E2 | Evet | Yoklama yapıldı: 52/56, ilk 12'de 11. Liste `var_R`/`var_W` ile yeniden üretildi, sha256'lar tutuyor. İsteğe bağlı kuyu listesi yapılmadı (S2, kabul). |
| E3 | Evet | 12 sınırı, (a)–(d) dalları, zamanlı geçme, FAR_PK, uygulama hatası yolu, tanı satırları. "10 istasyon" bilgi satırı kaldırılmış. FAR_PK'nin payı ve paydası → İ2-Ö7. |
| Ö1 | Evet | Wharton τ'su, ölçek uyarısı, ön ek ve özet cümlesi metne aynen girmiş. |
| Ö2 | Evet | VAR kalıbı, D5b (bant S7), §12 oranı. |
| Ö3 | Evet | X_min yoksa VAR yok, N tanımı, Wharton, N < 5n, 0,05/3, n = 6 ve 7 satırları, aday kalıbı. Tablolar yeniden hesaplandı. |
| Ö4 | Evet, ama 3a kusurlu | (iii), (iv), ±60 genişletme, 3a, D7 3a ile. 3a maskeli W sonunda çalışmıyor → İ2-E1. Rampa bilgi satırı hiçbir şey sınamıyor → İ2-E2. |
| Ö5 | Evet | Yanıtla çarpılmış enjeksiyon, manifestte g(f) ve örnekleme hızı, D14, §12. |
| Ö6 | Evet, sapmayla (S8, S9) | Darbe kuralında en büyük c_p'li parça; sızıntı yeni tanımla; D6b, D7b, D7c, D7d; "kural kalırsa" yolu. D6/D6b şart yeri → İ2-E2. |
| Ö7 | Evet | A_300, I′, D10 bandı. |
| Ö8 | Kısmen | Durum dosyası, sürdürme, paydalar, ikinci tur. Push yok; negatif pencere aşaması tanımsız → İ2-E3. |
| K1 | Evet | D2 ara değerleme, 10^(j/20) basamak, "üstündeki bütün basamaklar", ≥ 20 deneme, D13. |
| K2–K7 | Evet | Hepsi metinde (§6.6, §6.5.1, §4.3, §7.1, §6.1, §5/§7.2/§7.5). |
| D, nokta 6 | Evet | Ayrıca eşiğe bağlandı (S6). |

Metin ile §18 arasında çelişki bulunmadı. Küçük bir tutarsızlık var: `tr7_e1_maske.py`'deki `K1_ARALIK` 06:16:00
kullanıyor, metin ise 06:16:01. K1 aralığının maskeli payı iki uçla da 613 sn; pay 0,6466 ile 0,6473 arasında
değişiyor, yuvarlanmış değer (%65) değişmiyor (K-a).

---

## B. Sürüm 2'nin İNCELEME-1'den sapmalarına (§17) hükümler

### S1: E1 büyüklük ve süre kuralı (E1-C). Hüküm: KABUL, İ2-Ö1'deki eklerle

**Doğrulama.** E1-lit'in Tohoku'yu %100 maskelediği doğru (`E1-lit_ozet`). Tohoku penceresinde ComCat'te 17 tane
M 6,1–6,7 ve 2 tane M ≥ 7,7 olay var; 06:48–06:49'da oluşan iki M 6,1–6,2'nin varışları W'den sonra. İNCELEME-1'in "Love ve Rayleigh
açık kalır" notu yalnız iki büyük artçıya dayanıyordu. Sürüm 2'nin sapması zorunluydu.

**(i) Artçı cisim dalgalarına karşı koruma yeterli mi?**

- **M < 7 S dalgası.** Maskelenmemesi fiziksel olarak savunulabilir. 2–8 Hz'te teleseismik S'nin soğurulması
  (t*_S ≈ 4 t*_P ≈ 3–4 sn) genliği 2 Hz'te bile ~e^(−20)'nin altına indirir.
- **+60 sn kuyruk neyi örter.** Yeniden hesap (iasp91, 29 km). 73,5°'de pP +9, sP +13, PcP +16 sn sonra gelir;
  80,6°'de +10, +13, +7 sn. Hepsi örtülür. PP ise 73,5°'de +164 sn, 80,6°'de +183 sn sonra gelir ve M 6,x için
  örtülmez. PP'nin yolu iki kat uzun, t*'ı da yaklaşık iki katıdır; 2–8 Hz'te P'den bir mertebeden çok küçüktür.
- **Kalan risk: P kodasının 60 sn'yi aşan kuyruğu.** D12b bunu açıkça gösteriyor: C ×5, 60 sn sönümlü bir P +60 sn
  maskeyle 0,00 oranında atılıyor. M 6,x'in 73–81°'deki 2–8 Hz P genliği bilinmiyor (§16). Bu genlik hiçbir değişkede
  veriden önce bilinemez.
- **Önerilen çözüm.** Riski maskeyi uzatarak değil, **K1'in geçme etiketiyle** görünür kılmak (İ2-Ö1 b′). Böylece
  K1'in duyarlılığı daha da azalmaz, ama maske kenarında başlayan bir geçme "temiz" sayılmaz.

**(ii) K1 hâlâ anlamlı mı? 173 sn'lik açık parçada Hill 2013'ün tremoru var mı?**

Hill 2013'ün özeti (OpenAlex, bu incelemede okundu) faz ilişkisini veriyor, **saat vermiyor**:

- tremor "~100 sn periyotlu S'nin ortasında" başlıyor;
- SHSH'de küçük bir patlama var;
- "daha belirgin patlama Love varışıyla çakışıyor";
- ardından 20–30 sn Rayleigh ile modüle olmuş dürtüsel patlamalar geliyor.

Patlamaların UTC zamanları **özetten doğrulanamadı**. Grup hızlarından kaba kestirim (iz köşe ortalaması, Δ = 8171 km,
T0 05:46:24) şöyle:

| Faz (kestirim) | Zaman (UTC) | E1-C altında |
|---|---|---|
| S (iasp91) | ≈ 06:07:22 | W dışında (§5, bilinçli) |
| SS ≈ SHSH | ≈ 06:12:06 | W dışında |
| Love başı, 4,6 / 4,4 km/s | 06:16:00 / 06:17:21 | **açık** (06:16:01–06:17:29, 88 sn) |
| Love, 4,2 / 4,0 km/s | 06:18:50 / 06:20:27 | **maskeli** (06:17:29–06:20:57; yalnız 06:18:39–06:18:48 açık) |
| Rayleigh, 3,9 / 3,7 km/s | 06:21:19 / 06:23:12 | **açık** (06:20:57–06:23:51, 173–174 sn) |
| Rayleigh, 3,5 km/s | 06:25:19 | maskeli 06:23:51–06:25:35, sonra açık 06:25:35–06:26:37 (62 sn) |
| Tetikleyicinin kendi PKKP / PKIKPPKIKP (iasp91) | 06:17:29 / 06:25:30 | açık parçaların kenarında (İ2-Ö1 b′) |

Sonuç: K1 aralığının açık kısmı ~334 sn. Bunun içinde ≥ 30 sn'lik parça barındırabilen üç parça var: 88, 174 ve 62
sn. "Love varışındaki belirgin patlama" büyük olasılıkla ilk 88 sn'ye düşüyor, ama 06:17:29'dan uzun sürerse kesilir.
Rayleigh'le modüle patlamaların başı 174 sn'lik parçaya düşüyor. Yani **K1 anlamlı, ama zayıflamış bir sınamadır**.
Bu metinde de §11 beklentisinde de açıkça yazılmalı (İ2-Ö1 a).

Bilgi: BK.PKD, yani Hill'in kaydı bildirdiği istasyon, `iz_sira` 14 ile 12 sınırının dışında. K1 sınaması
PKD'siz yapılacak. Bu bir hata değil, ama tanı satırına girmeli (K-d).

**(iii) Marmara Tohoku biriminde ne kadar açık süre kalıyor?**

| Segment | Açık süre | Açık pay | ≥ 30 sn'lik açık parçalar |
|---|---|---|---|
| S1 | 690 / 2058 sn | %34 | 114, 180, 76, 259 sn |
| S2 | 712 / 2058 sn | %35 | 127, 180, 76, 263 sn |
| S3 | 718 / 2025 sn | %35 | 130, 180, 76, 265 sn |

S2 orta noktasında (Δ ≈ 8971 km) Love başı 4,6–4,4 km/s ile 06:18:54–06:20:23'e denk geliyor. Bu aralık neredeyse
tümüyle maskeli (06:18:08–06:21:44; yalnız 8 sn açık). Peng 2009'a göre Parkfield'da tremoru başlatan faz Love'dır.
Rayleigh'in 3,8–3,6 km/s bölümü 06:25:45–06:27:56'ya düşüyor ve büyük ölçüde maskeli (yalnız 06:26:11–06:27:27
açık). Marmara'nın en büyük kaba τ'lu birimi (23 kPa) bu yüzden en zayıf taranan birimdir. Birimin n'de sayılması
kural gereği doğru (bant veri görülmeden sabit kalmalı). Ama "görülmedi"nin dışlama olasılığı bu birimi tam saymamalı
→ İ2-Ö2.

**D12/D12b yeterli mi?** Değil, ama düzeltmesi basit:

- D12 ayırt ediyor (+240 ile 1,00; +60 ile 0,00; İNCELEME-2 tohum 777006'da da aynı).
- D12b ×2 ve ×3'te yanlış kodu (+30) ayırmıyor; ayıran yalnız ×5 / 30 sn satırı (777003: +60 ile 1,00, +30 ile 0,32).
- Maske kuyruğunun uzunluğu, M sınırı ve P/S seçimi deterministik kurallardır; olasılıklı bir yapay sınamayla
  değil, **birebir birim sınamasıyla** denetlenmeli. Ayrıca koşu kodu dondurulan önhesabı yeniden üretmelidir.
  → D12c (İ2-E2).

**Değerlendirilen öteki kurallar ve neden önerilmedi:**

1. **Maskeyi beklenen 2–8 Hz genliğine göre ölçeklemek.**
   - Gerektirdikleri: mb–Q(Δ, h) tablosu, t*_P(f) ve köşe frekansı varsayımı, eşik için de gürültü düzeyi.
   - Sorun: Bunların hiçbiri özetten doğrulanamaz. Gürültü düzeyine bağlanırsa kural R'deki veriye bağlanır, yani
     yeni bir çatallanma noktası olur.
   - Kaba hesap (mb 6,0, 73°, Q ≈ 6,9, t* 0,5–0,7 sn) 3 Hz'te ~3–13 nm/s veriyor. Bu, kırsal kısa periyot gürültüsü
     düzeyindedir, yani karar tam belirsizlik bölgesine düşer.
   - Veri görmeden savunulabilir bir sayı yazılamaz. **Önerilmez.**
2. **E1-D: yalnız M ≥ 6,5 P'leri +60 ile maskelemek.** Bu incelemede `tr7_e1_maske.csv`'den hesaplandı.
   - Kazanç: Parkfield W'sinin %36'sı maskeli olur, K1 aralığının %37'si. Açık parçalar 06:16:01–06:19:47 (226 sn) ve
     06:20:57–06:27:09 (372 sn). Tohoku S2 W'sinin %46'sı maskeli olur.
   - Bedel: K1 aralığının içinde, tam Love ve Rayleigh zamanlarında beş tane M 6,2–6,4 P varışı (06:17:39, 06:18:58,
     06:24:01, 06:24:35, 06:26:47) maskesiz kalır. O zaman K1'in geçmesi yorumlanamaz.
   - Simetri gerekçesi ("negatif pencereler de M 6,0–6,4 içerir") Tohoku için geçmez. Tohoku penceresinde 30 dakikada
     14 M 6,0–6,4 olay var; küresel arka plan ~0,007.
   - **Önerilmez.**
3. **K1'i başka bir yayımlanmış olaya taşımak.** En temiz aday **Denali 2002**. Peng vd. 2008, 10.1029/2008gl036080,
   özeti okundu: tremor 2–8 Hz'te, "zarfı birçok istasyonda tutarlı", "geçen yüzey dalgalarıyla aynı periyotta", Love
   ile uyarılıyor. Bu, bu ön kaydın algılayıcısının tam tanımıdır. Denali 2002'nin ilk saatlerinde M ≥ 6 artçı yok
   (bu inceleme katalogla doğrulamadı).
   - Sorun 1: 2002'deki NC/BK sürekli veri varlığı **yoklanmadı**. Yoklama, E2 gibi yeni bir dalga formu erişimi
     gerektirir.
   - Sorun 2: Taşımak yeni liste, yeni E1 önhesabı, yeni negatif pencere ve yeni K1 aralığı gerektirir. Bunlar yeni
     bir inceleme turu demektir.
   - Sorun 3: Parkfield–Tohoku'nun τ_ölç / kaba τ kalibrasyonu (Hill 2013'ün 0,7–10 kPa'sı) kaybolur.
   - Sumatra 2004/2012 aynı artçı sorununu taşır (2012'de iki saat sonra M 8,2).
   - **Bu ön kayıtta önerilmez.** §14 (d)'de adıyla yazılmalı (İ2-Ö1 e).

**Net öneri:** E1-C olduğu gibi kalır. Eklenenler (tam metinleri İ2-Ö1 ve İ2-E2'de):

- K1 için "belirsiz geçme" etiketi: maske kenarı ve tetikleyicinin kendi çekirdek fazları;
- açık parçaların ve kestirilen faz zamanlarının metinde yazılması;
- D12c;
- §14 (d)'de Denali 2002;
- "görülmedi"de n_açık (İ2-Ö2).

### S2: Kuyu listesi yapılmadı. Hüküm: KABUL

Yetki 112 istekle sınırlıydı. Tanı satırının kaldırılması tutarlı. §14 (d) yolu açık.

### S3: K1 aralığında I yerine I′, başlangıç 06:16:01. Hüküm: KABUL

I′ kullanmak doğru: I'nın ±60 sn'si K1 aralığını yapay olarak 2 dakika genişletirdi. Saniye yuvarlaması
`tr7_onkayit_sayilar.json` ile tutarlı.

### S4: Parkfield'da pencere başına üç enjeksiyon. Hüküm: KABUL, küçük ekle

Aynı penceredeki üç deneme aynı gürültüyü paylaşır, bu yüzden bağımsız değildir. A90_PK yalnız K1 (c) etiketine girer,
bu yüzden kabul edilebilir. Üretecin çekiliş sırası tanımsız: Parkfield ve Marmara aynı `default_rng(20261112 + 2)`'yi
kullanıyor → K-c.

### S5–S7: Hüküm: KABUL

- **S5.** Negatif pencereler bit düzeyinde yeniden üretildi.
- **S6.** Bit sayısının eşiğe bağlanması gerekliydi.
- **S7.** D5b için bilgi bandı.

### S8: Sızıntı kuralı aşım saniyelerinde. Hüküm: KABUL

İNCELEME-1'in I tanımının kendi D7c'sini geçemediği doğrulandı (0,09–0,44). Yeni tanım D7c'de 0,00, D7d'de 1,00. Yeni
tohumla (777005) D7c 3 / kentsel yine 0,00.

Bilinmesi gereken iki not:

- Aşım saniyeleri 2–8 Hz'e göre seçildiği için Δ_y yukarı yanlıdır. Kural bu yüzden sınırdaki sızıntıya karşı
  hoşgörülüdür. D7d yalnız f⁻¹ kodasıyla sınanıyor.
- İNCELEME-1 değişkesi A = 3 kentselde yeni tohumla 0,04 verdi, yani ≤ 0,05 bandının içinde. D7c'nin bilinen yanlış
  kodu ayıran satırı Gauss satırlarıdır (0,42–0,44) → K-f.

Rejimi değiştiren bir sorun yok.

### S9: D6b ×100'de S–P ≤ 5 sn'lik olaylar atılmıyor. Hüküm: KABUL, gerekçe ve rakip açıklama eklenerek

Kural değiştirilmemeli: başlangıca bakan bir darbe kuralı yarım sinüs tremoru atar. Ama gerekçenin bir eksiği var.
Kataloglanmamış yerel depremler negatif pencerelerde de vardır ve FAR'a girer. **Yüzey dalgasının tetiklediği** yerel
mikrodepremler ise yalnız tetikleyici penceresinde olur, FAR'a girmez. Bu, R1–R3'te olmayan bir rakip açıklamadır
→ İ2-Ö5.

### S10: D7/D7b bandı ≤ 0,03. Hüküm: KABUL

Doğru kod 0,00–0,01, bilinen yanlış kod 0,05–0,11.

### D6/D6b ×20 ve O4 ayırt etmiyor: kabul edilebilir mi?

**Hayır, şart yeri değişmeli.** Kurallar kalmalı.

- **D6 ve D6b ×20.** Her iki kod da 1,00 veriyor, çünkü olay **algılanmıyor** (algılama 0,00–0,03). Şart darbe
  kuralını değil, ≥ 15 aşım saniyesi şartını sınıyor. Darbe kuralını sınayan satırlar şunlar:
  - D6 ×100: doğru 1,00; yanlış 0,52 / 0,52 / 0,49.
  - D6b ×100, S–P 8: doğru 0,96 / 0,97 / 0,96 / 0,98; yanlış 0,00.

  D6b ×100'ün doğru değeri ~0,97 olduğundan, ≥ 0,95 bandını doğru kod tohum başına %8–14 olasılıkla kaçırır
  (Bin(100, 0,97–0,965)). Bant ≥ 0,90 olmalı: doğru kodun kaçırma olasılığı 0,0002, yanlış kod 0,00.
- **O4.** "R'den W sonuna ×2" o kadar yavaş ki hiç algılama vermiyor. Sabah artışında R'nin içinde yükselip W'de düz
  kalan gürültü de tutarlı küme vermiyor. Bu incelemede denendi: ×4 ve ×8 platoda algılama 0/30; düz bölümde L
  serileri birbiriyle ilişkisiz. Tehlikeli olan **W içinde** yükselen gürültüdür. Onu sınayan ayırt edici satır D15'tir
  (İ2-E2). D15 aynı zamanda 3a'nın maskeli W sonundaki kusurunu da yakalar (İ2-E1). **3a kalmalı:** onsuz W içindeki
  ×2 yükseliş %100 sahte küme bırakıyor.

---

## C. Numaralı bulgular ve düzeltme metinleri

Önem: **E** = dondurmadan önce zorunlu; **Ö** = önemli, metne işlenmeli; **K** = küçük.

### İ2-E1 (E). §6.5 madde 3a: maskeli ya da kayıtsız W sonunda kural çalışmıyor

- **Bulgu.** E1-C önhesabına göre W'nin son saniyeleri maskeli pencereler:

  | Pencere | W sonundaki maskeli kısım |
  |---|---|
  | Tohoku S1 | 222 sn |
  | Tohoku S2 | 205 sn |
  | Tohoku S3 | 167 sn |
  | Tohoku S4 | 144 sn |
  | Tohoku S7 | 204 sn |
  | Nepal S7 | 2 sn |

  Bu pencerelerde W'nin son 60 sn'si tümüyle maskeli. Maskeli saniye aşım sayılmadığı için "parça sonu ≥ W sonu − 60"
  şartı hiç sağlanamaz. Negatif pencerelerde de M 6,0–6,4 P maskesi W sonuna denk gelebilir. Aynı şey sonu kayıtsız
  W'ler için de geçerli.

  Yapay sınama (`tr7_inc2_taban.py`): tremor yok, 3 istasyon, 2–8 Hz gürültü W başından 300 sn sonra 900 sn içinde
  ×2'ye yükseliyor, W sonuna kadar ×2 kalıyor.

  | Durum | Algılama | 3a ile atılma |
  |---|---|---|
  | Maskesiz, sürüm 2 metni (tohum 9201 / 9202) | 1,00 / 1,00 | 1,00 / 1,00 |
  | Son 120 sn maskeli, sürüm 2 metni (9203 / 9204) | 1,00 / 1,00 | **0,00 / 0,00** |
  | Son 120 sn maskeli, düzeltilmiş tanım (9203 / 9204) | 1,00 / 1,00 | 1,00 / 1,00 |
  | 3a olmadan (9301 / 9302, 50 pencere) | 1,00 / 1,00 | darbe ve sızıntıdan sağ çıkma 1,00 / 1,00 |

  "W sonu"nun istasyonun kendi W'si mi, segment birleşimi mi olduğu da yazılı değil.
- **Düzeltme metni (§6.5 madde 3a'nın yerine):**

  > 3a. **Taban kayması (Ö4).** Kümedeki istasyonların ≥ yarısında, istasyonun kümedeki aşım parçalarından biri
  > W′_son − 60 sn'ye ya da daha sonrasına kadar sürüyorsa küme atılır. W′_son, o istasyonun kendi W'si içinde
  > maskelenmemiş (§6.5.1, 1a) ve kayıtlı olan son saniyedir. W sonu maskeli ya da kayıtsızsa W′_son, ondan önceki son
  > açık saniyedir. Kural tetikleyici, negatif ve Parkfield pencerelerine aynen uygulanır. (İNCELEME-2: sürüm 2'nin
  > "W sonu − 60" tanımı, Tohoku'nun S1–S4 ve S7 pencerelerinde, W'nin son 144–222 sn'si E1 ile maskeli olduğu için hiç
  > çalışamazdı.)

- **§12 "Kültürel gürültü" maddesinin sonuna:**

  > Yapayda W içinde ×2 yükselen gürültü, 3a olmadan %100 tutarlı küme verir. 3a bunları atar (D15). W içinde yükselip
  > yine W içinde sönen bir artış atılmaz; negatif kontrol bunu yalnız aynı saat, gün türü ve yaz saati eşlemesi kadar
  > ölçer.

### İ2-E2 (E). KD tablosu: şartlar ayırt edici satırlara taşınır; D12c ve D15 eklenir

- **Bulgu.** §B'deki "D6/D6b ×20 ve O4" bölümü ile S1'in "D12/D12b" bölümü.
- **Düzeltme metni.** §7.1 tablosunda D6, D6b ve D12b satırlarının yerine, D12b'den sonra D12c ve D14'ten sonra D15:

  > | D6 | Yapay yerel deprem (ani başlangıç, C ×20 ve ×100 sıçrama, 5 sn e-katlı sönüm), katalogsuz, 100 pencere | **×100'de** algılanmama ya da darbeyle atılma ≥ 0,95; aynı olay katalogdaysa maske ile atılma 1,00. ×20 yalnız bilgidir (olay algılanmadığı için darbe kuralını sınamaz) | ×100: 1,00 / 1,00 (algılama 0,48 / 0,48, algılananların hepsi darbeyle; İNCELEME-2 tohum 777007: 1,00, algılama 0,51); katalogda maske ile 1,00 / 1,00; bilgi ×20: 1,00 / 1,00 (algılama 0,00 / 0,00) | darbe kuralı 5 sn yumuşatılmış C'de: ×100: 0,52 / 0,52 (777007: 0,49) |
  > | D6b | Yapay yerel deprem; P tepenin 1/4'ü, S–P = 3, 5 ve 8 sn; ×20 ve ×100; katalogsuz; 100 pencere | **×100, S–P = 8: algılanmama ya da darbeyle atılma ≥ 0,90.** ×20 (bütün S–P'ler) ve ×100 S–P 3 / 5 yalnız bilgidir (§17 S9) | ×100, S–P 8: 0,96 / 0,97 (İNCELEME-2 tohum 777001 / 777002: 0,96 / 0,98); bilgi: ×20, S–P 3 / 5 / 8: 1,00 / 1,00 her biri (algılama 0,00–0,03); ×100, S–P 3 / 5: 0,00 / 0,00; 0,29 / 0,27 | yumuşatılmış C: ×100, S–P 8: 0,00 / 0,00 |
  > | D12b | Aynı, 6,0 ≤ M < 7,0 vekili: C ×2, ×3, ×5 sıçrama, 30 sn e-katlı sönüm; ×5 ve 60 sn sönüm (bilgi) | 30 sn sönümlülerde +60 sn maske ile atılma ≥ 0,95. Bilinen yanlış kodu ayıran satır ×5'tir; ×2 ve ×3 ayırmaz. Kuyruk uzunluğunun asıl denetimi D12c'dir | ×2: 1,00 / 1,00; ×3: 1,00 / 1,00; ×5: 1,00 / 1,00 (İNCELEME-2 tohum 777003: 1,00); bilgi ×5, 60 sn sönüm: 0,00 | maske kuyruğu +30 sn: ×5: 0,38 / 0,32 (777003: 0,32); ×2 ve ×3: 1,00 (ayırmaz) |
  > | D12c | E1 maskesi birim sınaması (deterministik). Elle kurulmuş katalog: M 6,95, 6,99, 7,00 ve 7,9 olaylar; P ve S varışları; tetikleyicinin kendisi; tetikleyiciye ±5 sn içinde M ≥ 7,0 ikinci kimlikli kayıt; Wharton biriminin öteki olayı; W dışında kalan bir varış. Ayrıca koşu kodu, tetikleyici ve Parkfield pencerelerinin maskesini `tr7_e1_maske.csv`'den segment orta noktasıyla kurar | Elle kurulmuş katalogda maskelenen saniye kümesi, §6.5.1a'dan elle hesaplanan kümeyle birebir aynı. Gerçek varışlarda W maskeli payı ve K1 aralığının maskeli payı ±0,001 içinde: Tohoku S1 / S2 / S3 0,664 / 0,654 / 0,645; Parkfield W 0,578; K1 aralığı [06:16:01, 06:31:48] 0,647 (613 / 947 sn) | — | +30 sn kuyruk, M 6,x S'nin maskelenmesi (Parkfield W 0,791) ya da 7,0 sınırının "> 7,0" yazılması birebir karşılaştırmada kalır |
  > | D15 | Taban kayması (§6.5.3a): tremor yok; 3 istasyon, 100 pencere; 2–8 Hz gürültü W başından 300 sn sonra 900 sn içinde doğrusal ×2'ye yükselir, W sonuna kadar ×2 kalır; (a) maskesiz, (b) W'nin son 120 sn'si maskeli | ayıklamasız algılama ≥ 0,90 ve 3a ile atılma ≥ 0,95, (a)'da ve (b)'de | algılama 1,00; (a): 1,00 / 1,00; (b): 1,00 / 1,00 (İNCELEME-2 `tr7_inc2_taban.py`, tohum 9201 / 9202 ve 9203 / 9204) | 3a yok: atılma 0,00 (darbe ve sızıntıdan sağ 1,00; `tr7_inc2_taban_ek.py`, tohum 9301 / 9302, 50 pencere); sürüm 2'nin "W sonu − 60" tanımı (b)'de: 0,00 / 0,00 |

- **"Bilgi satırları" paragrafının ilk cümlesinin yerine:**

  > Bilgi satırları (şart değil): R'den W sonuna doğrusal ×2 yükselen 2–8 Hz gürültü (Ö4), 100 pencere: ayıklamasız
  > algılama 0,00. Bu eğim W içinde tutarlı küme kuramayacak kadar küçüktür, 3a'yı sınamaz. 3a'nın ayırt edici
  > denetimi D15'tir.

- **§7.1'in referans betik cümlesine ek:**

  > ve D12c, D15 için İNCELEME-2'nin `tr7_inc2_taban.py`, `tr7_inc2_taban_ek.py` betikleri (kök oturum
  > `kayit/turetme/tr7/` altına kopyalar)

### İ2-E3 (E). §10: aşamalar, negatif pencerelerin yeri, push

- **Bulgu.** §B'de ve Hüküm bölümünde. §10.5'teki sıra ("önce örtü ve K0-tam, sonra negatif pencereler, K2 ve MDA,
  sonra tetikleyici") doğrudur, ama aşama listesinde karşılığı yok.
- **Düzeltme metni.**
  - §10 madde 4'ün yerine:

    > 4. K1: önce Tohoku penceresi indirilir ve zarflanır (algılama yok). Sonra Parkfield negatif pencereleri indirilir
    > ve işlenir (algılama, FAR_PK, MDA). En son Tohoku penceresinde algılama yapılır ve K1 dalı yazılır. (b) ve (b′)
    > dışındaki her dalda dur (§7.2).

  - §10 madde 5'in yerine:

    > 5. Marmara: önce bütün tetikleyici pencereleri indirilir ve zarflanır (algılama yok); örtü ve K0-tam bandı
    > yazılır. Sonra negatif pencereler indirilir ve işlenir; K2 ve MDA yazılır. Sonra tetikleyici pencereleri zarf
    > deposundan işlenir. En son hüküm.

  - §10 madde 6'nın ilk dört cümlesinin yerine:

    > 6. **Tek koşu (Ö8).** Koşu kodu her aşamanın başında, depodaki `kayit/turetme/tr7/TR7_KOSU_DURUM.json`
    > dosyasına aşama adını yazar, commit ve push eder. Push başarısızsa aşama başlamaz. Aşamalar sırayla şunlardır:
    > manifest, K1-indirme, K1-negatif, K1-algılama, Marmara-indirme, Marmara-negatif, Marmara-algılama, hüküm.
    > Aynı bilgi depo dışında bir bekçi dosyasına (`TR7_GERCEK_KOSU_BASLADI`) da yazılır. **Algılama aşamaları**
    > K1-negatif, K1-algılama, Marmara-negatif ve Marmara-algılama'dır. Bunlardan birine bir kez girilmişse koşu, §7.2'deki
    > uygulama hatası yolu dışında yeniden başlatılmaz. Bir algılama aşamasında duran koşu, durma nedeni kayda
    > geçtikten sonra kaldığı pencereden sürdürülür; o ana dek yazılmış algılama ve MDA satırları yeniden hesaplanmaz.
    > Algılama aşamalarından önce duran koşu kaldığı aşamadan sürdürülür. Her iki durumda da kod değişikliği yalnız
    > indirme ve ayrıştırma katmanında yapılabilir ve "koşu öncesi düzeltme" başlığıyla yazılır.

  - Aynı maddenin "Servis hatası" ve "Biçim hatası" alt maddelerine:

    > Paylar her indirme yapan aşama (K1-indirme, K1-negatif, Marmara-indirme, Marmara-negatif) için ayrı hesaplanır.
    > Bir algılama aşamasında "hiçbir algılama hesaplanmadan durur", "o aşamanın kalan pencereleri işlenmeden durur"
    > demektir.

### İ2-Ö1 (Ö). S1'in ekleri: K1'in "belirsiz geçme" etiketi, açık parçalar, Denali

**a) §6.5.1a önhesap paragrafının sonuna:**

> K1 aralığında açık parçalar: 06:16:01–06:17:29 (88 sn), 06:18:39–06:18:48, 06:20:57–06:23:51 (174 sn),
> 06:25:35–06:26:37 (62 sn) ve 06:31:29–06:31:30. Toplam ~334 sn. Grup hızıyla kaba kestirimde (iz köşe ortalaması,
> Δ = 8171 km) Love başı 4,6–4,4 km/s ile 06:16:00–06:17:21'e düşer ve açıktır. Love'ın 4,2–4,0 km/s bölümü
> (06:18:50–06:20:27) maskelidir. Rayleigh 3,9–3,7 km/s (06:21:19–06:23:12) açıktır. Hill 2013'ün özeti tremor
> patlamalarını fazlarla ilişkilendirir, saat vermez; patlamaların açık parçalara düştüğü **özetten doğrulanamadı**.
> Marmara'da (S2 orta noktası, Δ ≈ 8971 km) Love başı (06:18:54–06:20:23) maskelidir. Açık süre Tohoku S1 / S2 / S3'te
> 690 / 712 / 718 sn'dir (%34–35); ≥ 30 sn'lik açık parçalar S2'de 127, 180, 76 ve 263 sn'dir.

**b) §7.2 K1 sonucunda, (b) maddesinden sonra yeni madde:**

> - (b′) **Belirsiz geçme.** (b)'yi sağlayan kümelerin hepsinde I′ başı şu iki durumdan birindeyse K1 **"geçti,
>   belirsiz (cisim dalgası açıklaması dışlanamadı)"** olarak yazılır:
>   (i) bir E1 maske aralığının bitişinden sonraki ilk 5 sn içinde (0 ≤ I′ başı − maske sonu ≤ 5 sn);
>   (ii) tetikleyicinin kendi PKKP, SKKP, PKKS, PKIKPPKIKP ya da PKPPKP varışının [−10, +120] sn içinde. Varışlar
>   iasp91 ile, olay derinliğinde, iz köşe ortalamasına hesaplanır; Parkfield'da PKKP 06:17:29, PKIKPPKIKP 06:25:30
>   UTC (öteki üç faz taup'ta bu uzaklıkta yok).
>
>   Bu durumda Marmara verisi indirilir, ama Marmara'da "VAR" verilemez (en çok "aday") ve her "görülmedi" cümlesinin
>   sonuna "(K1 yalnız belirsiz geçti)" eklenir. (b′), "geçti, ayırt edici değil" etiketiyle birlikte de yazılabilir.

**c) §7.2 "Tanı satırları"na:**

> - K1 kümelerinin her biri için I′ başı ile ondan önceki en yakın E1 maske sonu arasındaki süre;
> - tetikleyicinin kendi çekirdek fazlarına (b′ ii) en yakın uzaklık;
> - BK.PKD'nin (`iz_sira` 14, 12 sınırının dışında; Hill 2013'ün kaydı bildirdiği istasyon) Tohoku penceresindeki
>   istasyon aşımları.

**d) §12 "Teleseismik cisim dalgaları (E1)" maddesinin sonuna:**

> +60 sn kuyruk M 6,x için pP, sP ve PcP'yi örter (73–81°'de P'den 7–16 sn sonra). PP'yi (P'den 164–183 sn sonra)
> örtmez. Tetikleyicinin kendi geç çekirdek fazları (PKKP, P′P′) maskelenmez. M ≥ 8,5 tetikleyicilerde bunlar W
> içindedir: Tohoku–Parkfield PKKP 06:17:29, PKIKPPKIKP 06:25:30; Tohoku–S2 PKKP 06:17:13, SKKP/PKKS 06:20:48–52,
> PKIKPPKIKP 06:25:17. K1'de (b′) ile görünür kılınır; Marmara'da bilgi satırına yazılır.

**e) §14 (d)'nin sonuna:**

> Böyle bir tasarımın ilk adayı Parkfield–Denali 2002'dir (Peng vd. 2008, 10.1029/2008gl036080: 2–8 Hz, birçok
> istasyonda tutarlı zarf, yüzey dalgasıyla eş periyot, Love ile uyarılmış). 2002'nin sürekli veri varlığı bu ön
> kayıtta yoklanmadı.

**f) §11'de "Sürüm 1'e göre 'ölçü sınanamadı' yükseltildi: …" cümlesinin sonuna:**

> Açık ~334 sn'lik K1 parçalarından Love başına (88 sn) ve Rayleigh başına (174 sn) düşenler sınamayı taşır. K1'in
> "belirsiz" geçmesi (b′) ayrı bir olasılık olarak beklenir.

### İ2-Ö2 (Ö). "Görülmedi"nin dışlama olasılığı, W'si büyük ölçüde maskeli birimi tam saymamalı

- **Bulgu.** p_min = (1 − 0,05^(1/n)) / 0,9 her birimin A90'ı aşan tremoru en az 0,9 olasılıkla algılayacağını
  varsayıyor. A90 ise negatif pencerelerde ölçülüyor. Orada E1 yalnız M 6,0–6,4 P'lerini kapatır; önhesapta W'nin
  maskeli payı ~%0'dır. Tohoku'nun S1–S3 W'si %65–66 maskeli ve Love başı Marmara'da maskeli. Bu birimin algılama
  olasılığı 0,9'un çok altında. Bugünkü cümle S2 için "8 tetikleyici, p_min 0,35" der; savunulabilir değer 7 birim ve
  0,39'dur.
- **Düzeltme metni.**
  - §8 "Dışlama oranı" paragrafının yerine:

    > Dışlama oranı: n birimde algılama yoksa, tetikleyici başına ≥ p_min olasılıkla A90'ı aşan tremor üreten bir
    > kaynak %95 düzeyinde dışlanır; p_min = (1 − 0,05^(1/n_açık)) / 0,9. n_açık, taranan ana birimlerden W'sinin
    > maskeli payı (§6.5.1 ve 1a birlikte, segment orta noktasıyla, §9.1) ≤ 0,50 olanların sayısıdır. MDA'nın ölçüldüğü
    > negatif pencerelerde E1 yalnız M 6,0–6,4 P'lerini kapattığı için, W'sinin yarısından çoğu maskeli bir birim
    > A90 duyarlılığıyla taranmış sayılmaz. Bu kural n'yi ve bandı değiştirmez. Değerler: n_açık 5 → 0,50; 6 → 0,44;
    > 7 → 0,39; 8 → 0,35; 9 → 0,32; 10 → 0,29. n_açık < 5 ise dışlama cümlesi yerine "dışlama hesaplanmadı (W'si
    > yarıdan az maskeli birim < 5)" yazılır. Önsayımda Tohoku'nun S1–S3 W'si %65–66 maskeli olduğundan n_açık
    > S1 / S2 / S3 için 8 / 7 / 7, p_min 0,35 / 0,39 / 0,39'dur.

  - "Görülmedi" kalıbında "kaba τ ≥ X kPa üstündeki n bağımsız tetikleyicide tetiklenmiş tremor görülmedi" yerine:

    > kaba τ ≥ X kPa üstündeki n bağımsız tetikleyicide (n_açık'ının W'si en az yarı yarıya maskesiz) tetiklenmiş
    > tremor görülmedi

  - "tetikleyici başına ≥ p_min olasılıkla" yerine:

    > tetikleyici başına ≥ p_min(n_açık) olasılıkla

  - §4.3 "E1'in önsayıma etkisi" paragrafının sonuna:

    > Bu yüzden "görülmedi" cümlesinin dışlama olasılığı n_açık ile hesaplanır (§8).

  - §9.2'ye n_açık sütunu eklenir.

### İ2-Ö3 (Ö). Tetikleyicinin kendi geç çekirdek fazları

Hesap ve metin İ2-Ö1 (b′ ii) ve (d)'dedir. Bu ayrı bir bulgudur: E1 "tetikleyici olayın kendisi dışarıda kalır" der.
M 9,1 için PKKP ve P′P′ W'nin içinde, 100 km'lik ağa eş zamanlı gelir. 2–8 Hz'te görünürlükleri bilinmiyor (§16'ya
eklenmeli). Maskeye eklenmesi önerilmez: K1'in açık parçalarını daha da daraltır. Etiket ve tanı satırı yeterlidir.

**§16'ya:**

> tetikleyicinin kendi PKKP ve P′P′ fazlarının 2–8 Hz'te Parkfield ve Marmara'da görünür olup olmadığı.

### İ2-Ö4 (Ö). E1: kodda olup metinde olmayan "ikiz kayıt" kuralı

- **Bulgu.** `tr7_e1_maske.py`, tetikleyicinin ±5 sn içindeki M ≥ 7,0 başka kimlikli kaydını da tetikleyici sayıp
  dışlıyor. Metin yalnız "tetikleyici olayın kendisi" diyor. 17 önbellek dosyasında bu kural hiçbir kaydı düşürmedi
  (bu inceleme denetledi), ama negatif pencerelerin E1 sorguları koşuda yapılacak ve koşu kodu metne göre yazılacak.
- **Düzeltme metni (§6.5.1a'da "tetikleyici olayın kendisi dışarıda kalır"dan sonra):**

  > (aynı olayın ComCat'teki başka kimlikli kaydı, yani T0'a ±5 sn içinde ve M ≥ 7,0 olan kayıt, de tetikleyici
  > sayılır; §3.4 önhesabında bu kural hiçbir kaydı düşürmedi)

### İ2-Ö5 (Ö). Rakip açıklama: tetiklenmiş yerel mikrodepremlilik

- **Bulgu.** Yüzey dalgaları kataloglanmamış küçük yerel depremleri de tetikleyebilir. Darbe kuralı S–P ≤ 5 sn'lik
  ×100'lük yerel depremleri atmıyor (D6b bilgi: 0,00 ve 0,29). Bunlar FAR'a girmez, çünkü yalnız tetikleyici
  penceresinde olur. "VAR" ve "aday" hükümleri bu kaynağı tremorden ayırmıyor ve metin bunu söylemiyor.
- **Düzeltme metni.**
  - §2 rakip açıklamalarının sonuna:

    > (R4) Yüzey dalgalarının tetiklediği kataloglanmamış yerel mikrodepremler (tremor değil). Bu ölçüm R4'ü tremorden
    > yalnız darbe kuralı kadar ayırır: S–P ≤ 5 sn ve gürültünün ~100 katı olaylar ayrılmaz (D6b).

  - §8 VAR kalıbında "2–8 Hz tremor;" yerine:

    > 2–8 Hz tremor (tetiklenmiş yerel mikrodeprem kümesi darbe kuralının ayırabildiği kadar dışlandı);

  - §9.1'e sütun:

    > Her algılama kümesi için darbe sayılan istasyon payı ve istasyon başına c_p / medyan_I′(C)'nin medyanı (bilgi).

  - §12'ye madde:

    > **Tetiklenmiş mikrodepremlilik (R4).** Darbe kuralı S–P ≤ 5 sn'lik güçlü yerel depremleri atmaz. Tetiklenmiş
    > olanlar negatif pencerelerde bulunmaz, FAR'a girmez. "VAR" bu kaynağı tümüyle dışlamaz.

### İ2-Ö6 (Ö). Çoklu karşılaştırma: yedi segmentlik segment satırları

- **Bulgu.** Özet için 0,05/3 var. Ama segment satırları yedi segmentte de α = 0,05 ile "VAR" yazabilir. S4 ya da S7'de
  tek bir "VAR" satırı, düzeltilmemiş bir sonuç olarak okunur.
- **Düzeltme metni (§8'de "S4–S7 ikinci satırlardır, özete girmez."den sonra):**

  > Her segmentin "VAR" cümlesinin sonuna "(segment düzeyi α = 0,05; yedi segment için düzeltilmedi;
  > X_min^(0,05/7) = [..], [sağlandı | sağlanmadı])" eklenir. X_min^(0,05/7) aynı tanımla, kuyruk eşiği 0,00714 ile
  > hesaplanır. N = 10n'de f = 0…5 için: n = 5: 3, 3, 4, K2, K2, K2; n = 6: 3, 4, 4, 4, K2, K2; n = 7: 3, 4, 4, 4, K2,
  > K2; n = 8: 3, 4, 4, 4, 5, K2; n = 9: 3, 4, 4, 4, 5, K2; n = 10: 3, 4, 4, 4, 5, 5.

  (Değerler bu incelemede scipy ile hesaplandı.)

### İ2-Ö7 (Ö). FAR_PK'nin payı ve paydası tanımsız

- **Düzeltme metni (§7.2 (b)'de "FAR_PK = f_PK / N_PK > 0,30 ise"den önce):**

  > N_PK, ≥ 3 istasyonu kalan Parkfield negatif pencerelerinin sayısıdır. f_PK bunlardan W'nin herhangi bir yerinde
  > algılama (§6.3, §6.5) verenlerin sayısıdır. N_PK < 5 ise K1 "geçti, ayırt edici değil" yazılır.

### İ2-Ö8 (Ö). Parkfield modülasyonunun "ölçülemedi" durumu

- **Bulgu.** Parkfield'da uzun periyot başvuru istasyonu yoksa (§6.4) modülasyon "ölçülemedi" olur. Bunun "geçmedi"
  sayılıp sayılmadığı yazılı değil. Listedeki yedi geniş bant istasyondan üçü (CI.SMM, SMR, CAR) varlık yoklamasında düştü.
- **Düzeltme metni (§7.2 "Bilgi satırları"nın son cümlesine):**

  > Parkfield modülasyonu "ölçülemedi" ise "geçmedi" sayılır.

### Küçük bulgular

- **K-a.** `tr7_e1_maske.py`'deki `K1_ARALIK` 06:16:00. Metin ve koşu 06:16:01. Pay 613/948 ile 613/947 (0,6466 ve
  0,6473) arasında, yuvarlanmış değer değişmiyor. **§18'e not:**

  > E1 önhesabında K1 aralığı 06:16:00 ile hesaplandı; 06:16:01 ile maskeli pay 0,647, en uzun açık parça 173–174 sn
  > (değişmez).

- **K-b.** §6.1 zarf deposu tahmini. 475 × 11 × 7 × 6314 × 4 B = 0,92 GB; Parkfield 52 × 11 pencere için ek ~0,1 GB.
  **"(tahmini ≤ 0,9 GB" yerine:**

  > (tahmini ≈ 0,92 GB, Parkfield ile ≈ 1,0 GB

- **K-c.** §7.4: üretecin çekiliş sırası. **"Üreteç `default_rng(20261112 + 2)`." cümlesinden sonra:**

  > Çekiliş sırası: önce Parkfield (negatif pencereler `tr7_negatif_pencere.csv` sırasıyla, pencere başına üç
  > başlangıç), sonra Marmara (segment S1…S7, birimler ana şok T0 sırasıyla, pencereler `sira` ile). Her denemede önce
  > başlangıç, sonra istasyon ve bileşen sırasıyla (`iz_sira`; Z, N, E) Gauss gerçekleşmeleri çekilir. Algılama veren
  > ya da düşen pencere için çekiliş yapılmaz.

- **K-d.** BK.PKD tanı satırı: İ2-Ö1 (c).
- **K-e.** §9.1'de "W'nin ve R'nin maskeli saniye payı"nın paydası. **"(§6.5.1 ve 1a ayrı)"dan sonra:**

  > payda: segment orta noktasıyla, istasyon W'lerinin (R'lerinin) birleşimi

- **K-f.** §7.1 D7c satırına:

  > İNCELEME-1 değişkesini ayıran satırlar Gauss satırlarıdır. Kentsel A = 3'te bu değişke bağımsız bir tohumla 0,04
  > verdi (İNCELEME-2 tohum 777005).

- **K-g.** §7.2'deki uygulama hatası yolu yalnız K1 kalınca açılıyor, yani hata arayışı asimetrik. Kabul edilebilir:
  aşırı duyarlı bir hata K2 ve FAR_PK ile görünür. Değişiklik gerekmez.

---

## D. Görevde sorulan kalemlere kısa hükümler

| Kalem | Hüküm |
|---|---|
| Tanımsız paydalar | FAR_PK (İ2-Ö7), maskeli pay (K-e), 3a'nın "W sonu"su (İ2-E1). Servis ve biçim hatası paydaları tanımlı. N, n, p_üst, X_min ve A90 deneme sayısı tanımlı. |
| Veri sonrası karar bırakan cümleler | Negatif pencere aşamasının yeniden başlatılabilmesi (İ2-E3). K1 uygulama hatası yolu tek seferlik ve asimetrik, ama kabul (K-g). §7.1'deki "kural kalırsa" yolu yalnız gerçek veriden önce, kabul. |
| A90, kaba τ, n'nin tanımı | Hepsi tanımlı. A90'ın dayandığı negatif pencereler maskesiz, Tohoku maskeli → n_açık (İ2-Ö2). |
| S2/S3 n = 8 ve ×1/3'te veri yok | Kalıplar dürüst. "(yalnız kaba τ ölçeğinde)" ön eki ve özet cümlesi ×1/3'ün veri yok bandını hükmün içine taşıyor. n_açık ile birlikte S2/S3 cümlesi "8 tetikleyici (7'sinin W'si en az yarı yarıya maskesiz) … p_min 0,39" olur. |
| Tek koşu | İ2-E3 düzeltmesiyle yeterli (push, negatif aşamalar, sürdürme). |
| Çoklu karşılaştırma | Özet 0,05/3 ile korunuyor. Segment satırları için İ2-Ö6. S1–S3'ün bağımlılığı modellenmiyor, §12'de yazılı. |
| Negatif pencereler veri görülmeden mi üretildi | **Evet.** Betik yalnız katalog, takvim ve üreteç kullanıyor; önbellekten bit düzeyinde yeniden üretildi (170 pencere, hepsi ±30 gün içinde). |
| Zarf deposu ve yeniden üretilebilirlik | Algılama, ayıklama, modülasyon ve PGV için yeterli. MDA için `tr7_mda.csv` ve yeniden indirme notu yeterli. Boyut tahmini küçük düzeltme (K-b). |
| Veri sınırı ve İstanbul | Sorunsuz: en geç W sonu 2025-07-30T00:27:26; negatif pencereler (ii) ile 2026 öncesinde. Metinde mutlak İstanbul olasılığı ya da çarpanı yok. |

---

## E. Yeniden hesaplar (bağımsız tohumlar, `python3 -I -B`, 100 pencere)

| Denetim | Tohum | Sonuç | Sürüm 2 tablosu | Bant |
|---|---|---|---|---|
| D6 ×100 | 777007 | algılanmama ya da darbe 1,00 (algılama 0,51); yanlış (yumuşatılmış) 0,49; katalog maskesi 1,00 | 1,00 / 1,00; yanlış 0,52 | içinde (önerilen şartla) |
| D6b S–P 8, ×100 | 777001 / 777002 | 0,96 / 0,98; yanlış 0,00 / 0,00 | 0,96 / 0,97 | ≥ 0,95'in sınırında; ≥ 0,90 önerildi |
| D7c 3, kentsel | 777005 | sızıntı 0,00; İNCELEME-1 değişkesi 0,04; z kuralı 0,09 | 0,00 / 0,00 | içinde |
| D10 yarım sinüs | 777008 | 1,041 (q05–q95 1,034–1,046); I ±60: 0,875; A_etkin paydası 0,735 | 1,04 / 1,04 | içinde |
| D12 | 777006 | maskesiz algılama 1,00; +240 ile 1,00; +60 ile 0,00 | aynı | içinde |
| D12b ×5 / 30 | 777003 | +60 ile 1,00; +30 ile 0,32 | 1,00; yanlış 0,38 / 0,32 | içinde |
| D12b ×2 / 30 | 777004 | maskesiz algılama 0,98; +60 ile 1,00; +30 ile 1,00 | aynı | içinde (ayırt etmez) |
| D15 (yeni) | 9201 / 9202; 9203 / 9204 | İ2-E1 tablosu | — | — |
| Negatif pencereler | — | csv ve özet sha256 aynı | — | — |
| E1 önhesabı | — | csv ve özet sha256 aynı | — | — |
| X_min (0,05; 0,05/3; 0,05/7), p_min | — | aynı; 0,05/7 tablosu İ2-Ö6'da | — | — |
| Faz zamanları (iasp91, 29 km) | — | İ2-Ö1 ve S1 bölümündeki tablolar | — | — |
