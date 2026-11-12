DÜZELTMEYLE KABUL

# TR-7 koşu kodu: bağımsız kod incelemesi

Tarih: 12 Kasım 2026. İnceleyen kodu yazmadı. İncelenen dosyalar (`kayit/turetme/tr7/`): `tr7_cekirdek.py`,
`tr7_indir.py`, `tr7_kosu.py`, `tr7_test_yapay.py`; referans betikler `tr7_onkayit_yapay.py`, `tr7_onkayit_denetim2.py`,
`tr7_onkayit_denetim3.py`, `tr7_onkayit_d12c.py`, `tr7_inc2_taban*.py`. Bağlayıcı metin: dondurulmuş ön kayıt sürüm 3
(gövde sha256 df426ffc…4c20; özellikle §6, §7.1–§7.4, §8, §10 ve dondurma notu). Kodlayıcı okumaları:
`TR-7_KODLAYICI-OKUMALARI.md`.

**Körlük beyanı.** Hiçbir gerçek dalga formu ya da StationXML indirilmedi, açılmadı. Ağa yalnız sınamanın
127.0.0.1'deki yapay FDSN sunucusu için çıkıldı. 2026 verisi yok. Tam KD koşulmadı (kök oturum koşar); yalnız küçük ve
ara ölçekli yapay denemeler yapıldı. Ön kaydın dondurulmuş gövdesi değişmedi; dosyanın sonuna "Ek 1" eklendi ve gövde
sha'sı artık ilk 97 178 bayt üzerinden denetleniyor (aşağıda D3). Commit atılmadı.

## Hüküm

**DÜZELTMEYLE KABUL (koşulabilir), şu şartla: tam KD bu kodla (yeni kod sha'larıyla) yeniden koşulur.** Kod metne
sıkı biçimde uyuyor. Engelleyici hata bulunmadı. Metinle çelişen bir okuma düzeltildi (O-44: Kahramanmaraş negatifleri).
İki koşu güvenliği düzeltmesi yapıldı (gövde sha'sı, ham dizini). Bir hızlandırma eklendi; sonuçları bit düzeyinde
değiştirmiyor.

| Konu | Sonuç |
|---|---|
| §6 zarf, aşım, küme, ayıklama, maske | Metinle uyumlu; 30 mutasyonun 30'u kahinlerce yakalandı |
| §8 hüküm kalıpları (D11) | Metinden bağımsız yeniden türetildi: D11'in 13 cümlesi ve 3000 rastgele senaryo birebir aynı |
| K1 dal seçimi | Saf fonksiyona (`k1_dal`) ayrıldı, davranış aynı; sınırlar sınandı |
| Hız | Süzgeç obspy ile bit düzeyinde aynı, KD işleri 1,7–2,3 kat hızlı (ölçüm aşağıda) |
| Sınamalar | 26 → 32 sınama; hepsi geçti (1'i bilerek atlanan uzun KDKucuk) |

## A. Düzeltilen hatalar ve değişiklikler

**D1 (O-44, metne aykırı okuma, düzeltildi).** §7.4: "algılama vermemiş **her** negatif pencereye … yapay tremor
eklenir"; §7.3: negatif pencereler "Her birim (Kahramanmaraş bilgi birimleri dahil)" için kurulur. Kod Kahramanmaraş
negatiflerine çekiliş vermiyordu. Bu, ana birimlerin çekiliş dizisini de değiştirir (tek üreteç). Düzeltme:
Kahramanmaraş negatifleri ana şok T0 sırasında çekiliş alır, denemeleri `tr7_mda.csv`'ye yazılır. P(A), A50 ve A90
yalnız ana birimlerden hesaplanır (değişmedi; `k2_segment` süzgeci). Maliyet: MDA denemesi ≈ %10–15 artar.

**D2 (O-45, disk riski, kısmen giderildi).** Ham veri Marmara-negatif'in sonuna dek tutuluyor. Pencere bazında
"indir–zarfla–MDA–sil" sırası metne aykırı olmadan kurulamıyor. Nedeni: biçim hatası payı aşamanın bütün indirmeleri
bittikten sonra, hiçbir algılamadan önce denetlenmeli (O-28; pencere başına denetim, küçük paydalı ilk pencerelerde
sürdürmeyi kilitler). MDA de algılama sonucuna bağlı. Öteki yol (MDA için yeniden indirme) indirmeyi ikiye katlar ve
"veri değişti" riski getirir. Yapılan: ham dizini `TR7_HAM_DIZIN` ile yerel diske alınabilir (depo dışı denetlenir).
Böylece ham veri rclone bağlamasının yerel önbelleğini ikinci kez doldurmaz. Aşama başında boş alan günlüğe yazılır.
Öneri: Marmara-negatif'ten önce yerel diskte ≥ 12 GB boş alan.

**D3 (koşu güvenliği).** Ön kayıt dosyasının sonuna Ek 1 eklenince tüm dosyanın sha'sı değişir ve
`girdi_denetimi` koşuyu durdururdu. Gövde artık ilk `ONKAYIT_N = 97178` bayt üzerinden denetleniyor (sha256
df426ffc…4c20). Tüm dosyanın sha'sı ayrıca manifeste yazılıyor.

**D4 (hız, sonuç değişmez).** `bant_gecir` artık obspy `bandpass(corners=4, zerophase=True)`ın kendisiyle aynı
tasarımı (`iirfilter`, `sos`) ve aynı iki `sosfilt` geçişini kullanıyor. Fark yalnız uygulamada: 8192 örneklik
parçalarda `zi` aktarılıyor. Aritmetik aynı. Durum alt-normal düzeydeyken (|z| < 1e-290) ve girdi periyodikken,
durumun P örnek sonra **bit düzeyinde** başa döndüğü görülürse çıktının kalanı kopyalanıyor. Aynı durum ve aynı girdi
aynı çıktıyı verir; bu yüzden sonuç yaklaşık değil, birebirdir. Yavaşlığın nedeni: yapay sinyalin (tremor, deprem,
MDA enjeksiyonu) sıfır olduğu uzun bölümlerde IIR durumu alt-normal bir sınır döngüsüne giriyordu. Bu bölümde her
işlem 10–30 kat yavaştı. obspy yolu `bant_gecir_obspy` olarak korunuyor. Nyquist uç durumları obspy'ye bırakılıyor.
`kd_sinyal`'de H yokken aynı analitik sinyal iki kez hesaplanıyordu; biri kaldırıldı (birebir).

**D5 (bakım).** `asama_K1_algilama`'daki dal seçimi `k1_dal(...)` saf fonksiyonuna ayrıldı (aynı mantık), sınandı.

## B. Hız: önce / sonra (aynı tohum, bit düzeyinde karşılaştırma)

Süzgeç düzeyi: 5 sinyal türü (gürültü, ortada patlama, başta patlama, MDA biçimli enjeksiyon, üstel sönümlü deprem) ×
5 (fs, bant) birleşimi = 25 durumun 25'inde çıktı obspy ile **bit düzeyinde aynı**. Toplam süre 10,7 sn'den 3,0 sn'ye
indi. 2–8 Hz'te kazanç 5–20 kat. 100 Hz'te 0,5–1 Hz'te kazanç yok, çünkü alt-normal geçiş bölümü periyodik değil.

KD işleri (aynı tohum, aynı pencere sayısı; çıktı JSON'u birebir karşılaştırıldı; ölçüm 2 süreç yükte):

| İş | Pencere | Eski (sn) | Yeni (sn) | Çıktı |
|---|---|---|---|---|
| D2 (3 ist.) | 2 | 39,0 | 22,0 | AYNI |
| D6 ×100 | 3 | 42,1 | 19,0 | AYNI |
| D6b ×100 S–P 8 | 2 | 30,9 | 13,6 | AYNI |
| D7 | 2 | 35,5 | 17,6 | AYNI |
| D7d | 2 | 15,2 | 8,8 | AYNI |
| D10 | 2 | 33,9 | 17,2 | AYNI |
| D13 (MDA) | 2 | 29,1 | 13,3 | AYNI |

Kalıcı sınamalar: `Hiz.test_bant_gecir_obspy_ile_bit_ayni`, `Hiz.test_kd_isi_eski_yeni_ayni`.

Yeni süre kestirimleri (ölçülen; Ek 1 E1.7'de de var): bkz. "Süre kestirimleri" bölümü sonunda (KD tam planının her
işinden 1 pencere ölçüldü ve pencere sayısıyla ölçeklendi).

Yapılmayan: MDA'nın koşutlanması. Mümkün ve bit düzeyinde aynı kalır: her işin üreteç durumu, ham verinin yapısından
(istasyon, bileşen, fs) sırayla önceden ilerletilir; işler sonra herhangi bir sırada ya da koşut koşulur. Bu oturumda
yazılmadı, çünkü sürdürme mekanizmasına (`tr7_mda.jsonl` son satır durumu) dokunuyor ve ayrı bir sınama gerektiriyor.
`mda_deneme`'nin basamak başına yeniden kurulumu gerekli: basamaklar arası önbelleklenebilecek bir ara ürün yok
(enjeksiyon her saniyeyi değiştiriyor, L, aşım ve küme her basamakta yeniden kurulmalı).

## C. Mutasyon sınamaları (yeni; `KodIncelemeMutasyon`)

12 bağımsız kahin (doğru kodda geçer) ve 30 mutasyon. Mutasyonlar fonksiyon kaynağında tek bir yeri değiştirir ya da
sabiti değiştirir. **30/30 yakalandı.**

| Alan | Mutasyon |
|---|---|
| Eşik | 4σ → 3,5σ; σ'da R kenarı atılmıyor |
| Köprüleme ve aşım | maskeli boşluk köprülenir; boşluk ≤ 20 → < 20; "≥ 15 aşım saniyesi" şartı yok |
| Küme ölçütü | ±20 → ±19; farklı istasyon yerine parça sayısı; ≥ 3 yerine ≥ 1 tutarlı çift |
| E1 maskesi | M ≥ 7,0 → > 7,0; M 6,x'te S de maskeli; ikiz kuralı < 5 sn; ikiz kuralı büyüklüksüz |
| 3a W′_son | W′_son maskeyi yok sayar; 60 → 59 sn |
| Modülasyon ölçüsü | yalnız s = +1; gecikme 0…9; p = say/n |
| Binom | P(≥ X) yerine P(> X); Clopper–Pearson iki yanlı |
| n_açık / p_min | /0,9 yok; n_açık ≥ 5 → > 5; Wharton bir penceresiyle açık; ≤ 0,50 → < 0,50 |
| MDA basamağı | "üstündeki bütün basamaklarda" şartı yok |
| K1 dal seçimi | (b′) için "her küme" yerine "bir küme"; A90_PK ≤ → <; FAR_PK > → ≥; K1 aralığı dışı algılama → (c) |
| 2026 kapısı | pencere sınırı ≥ → >; istek sınırı ≥ → > |

## D. Hüküm kalıpları: bağımsız yeniden türetme (O-54, O-55)

`tr7_test_yapay.py` içindeki `bagimsiz_cumle` §7.2 ve §8'den, kodun `segment_hukmu`'suna bakmadan yazıldı. Kendi
Clopper–Pearson, binom ve X_min hesabını kullanır. Sonuç:

- D11'in kodlayıcı tarafından yazılmış 13 beklenen cümlesinin 13'ü bağımsız türetmeyle birebir aynı.
- Rastgele 3000 senaryonun 3000'inde kodun cümlesi birebir aynı. Her hüküm türünden en az 20 örnek vardı.

Ortak biçim seçimleri metin dışıdır ama zararsızdır: τ 2 ondalık, olasılık 3 ondalık, A 3 anlamlı basamak, ondalık
virgül, "n·f/N = 0,20". Kalıptaki Türkçe ekler sayıdan sonra metindeki gibi kalıyor: "3'unda", "7'ının". Bu dil
bakımından yanlış ama metnin harfidir. Ek 1'de karar olarak kayda geçirildi (E1.3).

## E. Kodlayıcı okumaları: hükümler

KABUL = okuma metne uygun, değişiklik yok. DÜZELT = kod değişti. EK-1'E = okuma metnin sustuğu bir yeri dolduruyor ve
koşudan önce Ek 1'de kayda geçmeli. Numaralar 1–66 arasında boşluklu: O-43, O-58–O-61 ve O-64 ne okumalar dosyasında ne
kodda var. O-65 yalnız O-9'un içinde anılıyor. Ayrıca O-12a var. Toplam 61 okuma.

| Okuma | Konu | Hüküm | Not |
|---|---|---|---|
| O-1 | Bağlayıcı sıra | KABUL | |
| O-2 | numpy Hilbert, obspy bandpass | KABUL | Hilbert scipy ile birebir sınanıyor; süzgeç D4 ile hızlandı (bit aynı) |
| O-3 | Ortalama + eğilim | KABUL | obspy ile birebir sınanıyor |
| O-4 | Kısmi 1 sn kutusu kayıtsız | KABUL | |
| O-5 | Yatay bileşen şartları | KABUL | |
| O-6 | float32 zarfla algılama | KABUL | |
| O-7 | Örtü tanımı; merge(method=1) | KABUL | |
| O-8 | σ = 0 istasyonu yerine aday yok | KABUL, EK-1'E | §6.0 12'yi "örtüden geçenlerden" seçer; σ = 0 §4.2'nin düşme listesinde yok, zarftan sonra bilinir. Kod onu aşım üretmeyen üye olarak tutar, sonuç "düşer" ile aynıdır. Yalnız Wb ve maskeli pay paydasına girer (etkisi saniyeler) |
| O-9 | Wb = istasyon W'lerinin zarfı; MDA başlangıcı Wb'ye göre (O-65) | EK-1'E | Metin "W" der; pencere-segment düzeyinde tek W yok |
| O-10 | Darbe: NaN şartı sağlamaz | KABUL | |
| O-11 | 3a "kayıtlı" = L tanımlı | KABUL | |
| O-12 | Maske saniyesi floor/ceil | KABUL | D12c referansıyla aynı |
| O-12a | Negatiflerin E1'i manifestteki ComCat yanıtından | KABUL | |
| O-13 | Büyüklüksüz kayıt maskelenmez | KABUL | |
| O-14 | φ için kayıtsız v = 0; L_k'da çıkarma | KABUL | |
| O-15 | Kaydırma `integers(120, |W|−120)` | KABUL | Referansla aynı |
| O-16 | < 20 denemede A50 de belirsiz | KABUL | P(A) "en az 20 ile hesaplanır" |
| O-17 | Kestiricide maskeli/kayıtsız çıkarılır | KABUL | |
| O-18 | Bit sayısı yalnız açıkça yazılıysa | KABUL | |
| O-19 | Değişken fs kanal istasyonu düşürür | EK-1'E | §4.2'nin düşme listesinde yok; pratikte biçim sorunu. Kayda geçmeli |
| O-20 | LP yolu parça başına; kenar atılmaz | KABUL, EK-1'E | remove_response %5 kenar inceltmesi (taper) uygular: boşluk yakınında PGV küçülür, büyümez (tutucu yön: n_ölç küçülür). Yalnız τ_ölç ve modülasyon fazını etkiler |
| O-21 | Kırpılma her kullanılan bileşende | KABUL | |
| O-22 | Eksen dizinleri | KABUL | |
| O-23 | KD dolgusu 600/620 sn | KABUL | |
| O-24 | D8 tanımı | KABUL | |
| O-25 | D12 "maskesiz algılanır" ≥ 0,95 | EK-1'E | Bant metinde yazılı değil |
| O-26 | Planlı istek paydası | KABUL | Tutucu |
| O-27 | Pay son durumla; yeniden tur yalnız servis hatalıları ister | KABUL | |
| O-28 | Biçim payı aşamanın sonunda bir kez | KABUL | İ2-E3 pencere başına denetime de izin verir; tek denetim daha sağlam |
| O-29 | Algılama aşamasında önce bütün indirme | KABUL | O-45'in nedeni |
| O-30 | Kod commit/push yapmaz; `baslat` → commit+push → `kos` | KABUL | |
| O-31 | Referans betik sha'ları sabitlendi | KABUL, EK-1'E | Ek 1 iki sha'yı yazar |
| O-32 | Girdi denetiminin kapsamı | KABUL | Gövde sha'sı artık ilk N bayt (D3) |
| O-33 | "Maske" ayıklama nedeni sayımı | KABUL | Bilgi |
| O-34 | ×3 sütunu alt sınır | KABUL | |
| O-35 | K1 aralığı iki ucu dahil | KABUL | |
| O-36 | Negatifler yalnız taranan birimler için | KABUL | |
| O-37 | Wharton negatifi tek deneme, ana şok alt penceresi | KABUL, EK-1'E | |
| O-38 | Modülasyon üreteci bağlam başına (K1 ayrı, Marmara ayrı) | EK-1'E | Metin tek üreteç ve "birim, segment, zaman" der; Parkfield bir Marmara birimi değil. Okuma makul |
| O-39 | D9: Δ koordinatlardan | KABUL | |
| O-40 | K1 aralığı dışında algılama → (d) | KABUL | "Algılama yoksa" harfiyen; mutasyonla sınandı |
| O-41 | (b′) bireysel E1 sonları; iz köşe ortalaması | KABUL | |
| O-42 | "Ayırt edici değil" yalnız (b)/(b′); modülasyon yalnız K1 kümelerinde | KABUL | |
| O-44 | MDA üreteci K1'den Marmara'ya taşınır; Kahramanmaraş çekiliş almaz | DÜZELT | Taşınma KABUL (tek üreteç, §7.4 çekiliş sırası). Kahramanmaraş kısmı metne aykırı: D1 |
| O-45 | Ham veri Marmara-negatif sonuna dek | KABUL, DÜZELT (kısmen) | Sıra metin gereği; ham dizini yerel diske alınabilir: D2 |
| O-46 | 1/2'de N'ye 1. yatayın yanıtı | KABUL | Yaklaşık; iki yatay yanıt pratikte aynı |
| O-47 | Enjeksiyon için ham yeniden okunur | KABUL | |
| O-48 | n_açık: bütün pencereler ≤ 0,50 | KABUL | Dondurma notuyla aynı; mutasyonla sınandı |
| O-49 | τ_ölç: 12 sınırı dışı; birim değeri pencerelerinin en büyüğü | EK-1'E | "En büyük" metinde yok (kaba τ kuralının eşi) |
| O-50 | LP başvuru istasyonu: penceredeki bütün istasyonlardan | KABUL | §6.4 segment listesiyle sınırlamaz |
| O-51 | Ölçü I ∩ W(ref); < 3 sn → ölçülemedi | KABUL | |
| O-52 | "Başvuru istasyonu var": algılayan pencerelerden birinde | EK-1'E | |
| O-53 | VAR'daki τ'lar algılayan (X_alg) birimlerden | KABUL | "en küçük algılayan birim" |
| O-54 | Kalıp doldurma biçimi | KABUL, EK-1'E | Bağımsız türetmeyle aynı (D) |
| O-55 | Aday listesinin sabit ifadeleri | KABUL, EK-1'E | Bağımsız türetmeyle aynı (D) |
| O-56 | S5/S6 bağımsız satırı | KABUL | Birim düzeyinde sınandı; uçtan uca değil (risk) |
| O-57 | K1 kalırsa ×1/3, ×3 önsayımdan | KABUL | |
| O-62 | Katalog: 204 boş; hata koşuyu durdurur | KABUL | |
| O-63 | Parkfield: NCEDC, yoksa EarthScope | KABUL | |
| O-65 | (O-9 içinde) MDA |W| = |Wb| | EK-1'E | O-9 ile birlikte |
| O-66 | Kısıtlı/yok istasyonun yerine sıradaki aday | KABUL | §6.1 planıyla uyumlu |

Sayım: 61 okumadan 44 KABUL (değişiklik yok), 1 DÜZELT (O-44), 1 KABUL + kısmi DÜZELT (O-45), 15'i Ek 1'e (bunların
7'si aynı zamanda KABUL).

## F. Özellikle bakılan yerler

- **Wharton.** İki pencere tek birim (`birim_ad`); n'de sayılma "pencerelerinden biri ≥ 3 istasyonla" (`tarananlar`);
  kaba τ sağ kalan pencerelerin en büyüğü (`k0_tam`); negatif pencere: iki alt pencere N'ye 1, alt pencerelerden birinde
  algılama varsa algılama (`k2_segment`); n_açık iki pencerenin ikisi de ≤ 0,50 (dondurma notu; mutasyonla sınandı).
  Metne uygun.
- **S5/S6 bağımsız satırı.** `k0_tam` bütün ölçeklerde `bagimsiz` alt satırı kuruyor (2009-01-01 sonrası birimler);
  `seg_veri` ve `k2_segment` aynı süzgeci kullanıyor; hüküm satırı bağımsız satır, öteki "Yöntem karşılaştırması,
  bağımsız değil" önekiyle. Önsayım sınaması S5 = 2, S6 = 1 veriyor. Uçtan uca koşmadı.
- **Kahramanmaraş.** n'ye girmiyor (`kahramanmaras_bilgi`), N ve P(A)'ya girmiyor. Negatifleri algılanıyor ve artık
  çekiliş alıyor (D1). Bilgi satırı `asama_hukum`'da.
- **Üreteçler.** MDA: tek üreteç, K1-negatif'te başlar, durumu `tr7_mda.jsonl`'de satır satır, Marmara-negatif'e
  taşınır. Sürdürme sınaması (test_4) kesintisizle aynı satırları veriyor. Modülasyon: O-38.

## G. Kalan riskler

1. Tam KD koşulmadı. D6 ×100 bandı (≥ 0,95) obspy süzgecinin öncülü yüzünden sınırda ya da altında (Ek 1 E1.5; 100
   bağımsız pencerede ölçüm orada).
2. Disk: Marmara-negatif'in ham verisi ≈ 8–10 GB, aşama sonuna dek. Yerel diskte 15 GB boş alan var.
3. MDA süresi tek süreçte saatler (aşağıda ölçüm). Koşutlama yazılmadı.
4. Uçtan uca prova yalnız S2 ve 2 birimle. Wharton, S5/S6 ve Kahramanmaraş yolları birim düzeyinde sınandı.
5. LP yolunda parça kenarı (O-20): yalnız τ_ölç'ü ve modülasyon fazını etkiler, tutucu yönde.
6. Gerçek StationXML'deki yanıt biçimleri (ör. çok aşamalı FIR, `get_evalresp_response` uç durumları) yalnız yapay
   envanterle sınandı. Biçim hatası payı (%1) bunu yakalar ve koşuyu algılamadan önce durdurur.

## Süre kestirimleri

| Kalem | Kestirim (yeni kod) | Nasıl |
|---|---|---|
| Tam KD | ≈ 15 saat CPU: 4 boş çekirdekte ≈ 4–5 saat, `--paralel 2` ile ≈ 7–8 saat | Plandaki her işin 1 penceresi ölçüldü (paylaşımlı makinede 2 süreçle), pencere sayısıyla çarpıldı |
| MDA | ≈ 9 saat tek süreç (Marmara ≈ 590 deneme × ≈ 55 sn; Parkfield ≤ 30 deneme) | 12 istasyonlu tek deneme 34 sn + ham okuma ≈ 11 sn; gerçek W ×1,3 |
| İndirme | Ölçülmedi (gerçek servis yok); hacim ≈ 8–10 GB ham | Kodlayıcının kestirimi |

D6 ×100 yeniden ölçümü (100 pencere, bağımsız tohumlar 777100/777101): 0,98 / 1,00; algılama 0,50 / 0,50; bilinen
yanlış kod 0,50 / 0,50. Öneri Ek 1 E1.5a'da: bant ≥ 0,95 tutarsa konu kapanır; tutmazsa "koşu öncesi ek" ile ≥ 0,85.

## Komutlar (kök oturum; depo kökünden)

Tam KD (bir kez):

    cd /home/user/knotenlinie && python3 -I -B kayit/turetme/tr7/tr7_kosu.py kd --paralel 4
    git add kayit/turetme/tr7/tr7_kd.json && git commit -m "TR-7 KD (tam)" && git push

Manifest, sonra K1'in üç aşaması (her biri baslat → commit+push → kos → commit+push):

    export TR7_HAM_DIZIN=/home/user/tr7-ham
    for A in manifest K1-indirme K1-negatif K1-algılama; do
      python3 -I -B kayit/turetme/tr7/tr7_kosu.py baslat "$A" &&
      git add kayit/turetme/tr7/TR7_KOSU_DURUM.json && git commit -m "TR-7 aşama başlıyor: $A" && git push &&
      python3 -I -B kayit/turetme/tr7/tr7_kosu.py kos "$A" &&
      git add kayit/turetme/tr7 && git commit -m "TR-7 aşama tamamlandı: $A" && git push || break
    done

Döngüyü aşama aşama, ayrı oturumlarda da koşabilirsiniz. Bir aşama durursa döngü kırılır. O durumda `durdu "<aşama>"
--neden "..."` → commit+push → `baslat "<aşama>" --surdur` → commit+push → `kos "<aşama>"`.
