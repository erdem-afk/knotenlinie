# TR-7c ön kaydı: sabit sızıntı kuralı (K5) ve kör Parkfield kontrolüyle Marmara'da tetiklenmiş tremor taraması

Durum: KARAR METNİ DONDURULDU (17 Kasım 2026; sürüm 2 + INCELEME-2'nin E-1 ve E-2 cümleleri). D-3 uyarınca bu dondurma Tohoku duman sınamasından ve m_f ölçümünden öncedir; bu andan sonra karar metni (ölçüt, dallar, kurallar, yazarın seçimleri) değişmez. Koşu dondurması (kod sha256'ları, yapay sınama sonuçları, beklenti beyanı) kod incelemesinden sonra ayrı bir ekle yapılır. Kod yok; kör olaylarda ve Marmara'da dalga formu açılmadı. İncelemeler: INCELEME-0, INCELEME-1, INCELEME-2 ("iki cümle eklenince hazır").
Tarih: 17 Kasım 2026. Sürüm 1: `TR-7c_tetiklenmis-tremor_ONKAYIT_surum1.md` (commit 4ba57ab).

Bağımsız incelemeler:
- `TR-7c_INCELEME-0.md` (fikir düzeyinde, hüküm **DÜZELTMEYLE KABUL**). Bu taslak o incelemenin §6'daki düzeltme
  cümlelerini (Z1–Z8) **değiştirmeden** taşır.
- `TR-7c_INCELEME-1.md` (sürüm 1 üzerine, commit 8b3a16c, hüküm **DÜZELTMEYLE KABUL**). Bu sürüm onun zorunlu
  düzeltmelerini (D-1…D-10) incelemedeki kesin cümlelerle **aynen** işler. Öneriler Ö-a…Ö-i'den hangilerinin alındığı
  gerekçesiyle §14.2'dedir. INCELEME-1'in hesabı: `kayit/turetme/tr7c/inc1/tr7c_inc1.py` (sha256 c809ce97…58a8),
  `tr7c_inc1.json` (sha256 4974dbe6…2974).

Hangi cümlenin nerede olduğu §14'teki eşleme tablolarındadır.

Bu metinde üç tür cümle var:
- İncelemenin cümlesi: alıntı (">") olarak ve "Z…" etiketiyle verilir. Değiştirilmez.
- İncelemenin boş bıraktığı yerde yazarın kararı: **"yazarın seçimi"** diye işaretlenir. Bağımsız kod incelemesinde ve
  dondurma öncesinde itiraz edilebilir.
- Depodan ya da literatürden doğrulanamayan şey: **"doğrulanamadı"** diye yazılır. Her biri için koşudan önce yapılacak
  0 € yoklama §8'de.

Türediği yerler (hepsi değiştirilmeden okunur):
- `TR-7_tetiklenmis-tremor_ONKAYIT.md` (sürüm 3, DONDURULDU, Ek 1 ile). "TR-7 §x aynen", o bölümün sayısı, eşiği ve
  cümlesiyle birebir geçerli demektir.
- `TR-7b_tetiklenmis-tremor_ONKAYIT.md` (TASLAK 1, kapı altında). "TR-7b §x aynen" aynı anlamdadır.
- `TR-7b_SAYIM.md` (veri varlığı kapısı; Chao 2012 Ek Tablo S1).
- `kayit/turetme/tr7/tr7_sonuc.md` (TR-7 tek koşusu: K1 (c), A50_PK 8,9, A90_PK 11,2 nm/s).
- `kayit/turetme/ESIK-DAYANAGI.md` (görülebilir en küçük etki ve ×0,5 / ×2 kuralı).
- Güç hesabı: `kayit/turetme/tr7c/tr7c_guc.py` (sha256 `f9c9289a99ed6dbbbf06bb33a4e5ea9020e847fa3fa4b79d81db3138c692e39b`),
  çıktısı `tr7c_guc.json` (sha256 `e225b0e67cdd15c08b969fce964547f782b265e3712065bea10fdf43fe705427`). İncelemeci yazdı,
  bu taslak yalnız okur.

Maliyet 0 €. Bu taslak için hiçbir ağ isteği yapılmadı, hiçbir dalga formu indirilmedi ya da açılmadı. 2026 ve sonrası
veri kullanılmadı.

## 0. Bağlayıcı metinlerin sırası (dondurulursa)

1. Bu metin; alıntılanan Z1–Z8 ve D-1…D-10 cümleleri bu metnin parçasıdır.
2. `TR-7c_INCELEME-1.md`, sonra `TR-7c_INCELEME-0.md`, yalnız bu metnin sustuğu yerde.
3. TR-7b taslağının bu metnin "aynen" dediği bölümleri (§4.2 tanımları, §6.2, §6.3, §6.4 (b′) ve (c) cümleleri, §7,
   §11.1). TR-7b'nin seçim kuralları (§4.3, §11.3, §12.4) TR-7c için **bağlayıcı değildir**; Z1 bu sapmayı beyan eder.
4. TR-7 sürüm 3 ve Ek 1, yalnız yukarıdakilerin sustuğu ve "aynen" denen yerlerde.

## 1. Soru

TR-7 §1 aynen. Uzak büyük depremlerin yüzey dalgaları Marmara'da (S1–S7) tetiklenmiş tremor üretiyor mu? Bu, dinamik
gerilmeye duyarlı derin bir kayma bölgesinin varlığına dair dolaylı bir gözlemdir. Ama soru ancak algılayıcı önce bir
kör kontrolden geçerse sorulur. Yani TR-7c'nin **ilk ve asıl sorusu** şudur:

> Önceden sabitlenmiş K5 sızıntı kuralıyla çalışan TR-7 algılayıcısı, 2001–2010 Parkfield olaylarında Chao 2012'nin
> "tetikledi" ve "tetiklemedi" etiketlerini, tetikleyici genliğinden ayrılabilen ve yüzey dalgasıyla eş periyotlu
> modülasyon taşıyan bir sinyalle, kör olarak ayırabiliyor mu?

Marmara sorusu yalnız bunun yanıtı "evet" (§6 dal (b)) ise açılır. Sonuç bir olasılık terimi değildir.

## 2. TR-7b'den beyanlı sapma ve gerekçesi

**Z1 (aynen):**

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

**Gerekçe** (INCELEME-0 §1'den; burada yalnız özetlenir):
1. **Sapma gerçektir.** Sonuç görüldükten sonra seçim kuralı gevşetiliyor. Motivasyon da sonuçtan geliyor: Tur 3'ün bilgi
   satırında K4/K5 6 istasyonla bütün şartları geçti (0,03 / 0,04). Bu yüzden sapma TR-7b'nin içinde yapılmaz, ayrı bir
   ön kayıt olarak beyan edilir.
2. **Hatanın yönü tutucudur.** K5'in kaldığı tek hücre, tremor varken kümelerin fazla atılmasını ölçer (≈ %5–6). Bu
   hata kör kontrolde algılamayı azaltır, yani "sınanamadı" yönüne iter. Yanlış "sınandı" ya da yanlış "VAR" üretmez.
3. **Yanlış alarmı belirleyen satırlar iki turda da geçti:** Y2'nin 18 hücresi (sağ 0,00–0,02), Y3 (0,97–1,00),
   F1/F2 (0,00).
4. **Yapay kapının yerine daha sıkı bir gerçek kapı geliyor:** 40 kör olay ve modülasyon şartı (§5). Kapı kaldırılmıyor.
5. **K5'in seçimi tanıma dayanır, veriye dayanmaz.** K4 ile K5 iki turun bütün hücrelerinde aynı değeri verdi. Aralarındaki
   seçim, Tur 2 sonucundan önce yazılmış simetri kuralıyla yapılıyor. Tohoku geliştirme verisinde K5 hiç hesaplanmadı.

**Kapatılan yollar** (yazarın seçimi; Z1'in "hiçbir eşik değişmez" cümlesinin uygulaması):
- K1 kalıntı eşiği (2σ), ρ eşiği (−0,7), 30 saniyelik Q referans şartı ve TR-7'nin bütün algılama eşikleri sabittir.
- Literatürdeki tremor zamanlaması (Peng 2009) hiçbir pencereyi, maskeyi ya da eşiği belirlemez. Pencereler yalnız
  katalogdan ve TR-7b §6.2'nin hız formülünden hesaplanır.
- Kör kontrol "sınanamadı" ile kalırsa, bu 40 olay başka hiçbir kural için kör kontrol olarak yeniden kullanılmaz.

## 3. Kör kontrol olay listesi

**Z2 (aynen):**

> "P (kör pozitif) = Chao 2012 Tablo S1'de Q_CC = 1 ve PKD PGV_T ≥ 0,027 cm/s olan, Tohoku hariç 10 olay: Peru 2001,
> Denali 2002, Colima 2003, Tokachi-oki 2003, Sumatra 2004, Kuril 2006, Kuril 2007, Wenchuan 2008, Samoa 2009,
> Maule 2010. N (kör negatif) = Tablo S1'de Q_CC = 0 olan 30 olayın hepsi (TR-7b_SAYIM §3). Kunlun 2001 ve Tonga 2006
> bilgi satırıdır. n_P ve n_N, TR-7 §4.2 örtü kuralından ve E1 maskesinden sonra K1b aralığının ≥ %50'si açık ve ≥ 3 liste
> istasyonu olan olay sayısıdır. E1 maske payları dondurmadan önce yalnız katalogla hesaplanır. Rastgele negatif pencereler
> TR-7b §6.3 aynen (yalnız P ve TR-7b'nin iki N olayı için; N_PK ≤ 120)."

**Veri yetersizliği kuralı** (Z4 (a)'nın kendisi; §6): **n_P < 8 ya da n_N < 20 → "ölçü sınanamadı (Parkfield verisi
yok)".** D-1 gereği n_N en çok 29'dur (30 olay, 29 birim).

### 3.1 P (10 olay)

T0, Δ ve PGV_T `TR-7b_SAYIM.md` §3'ten. Δ, iz köşe ortalamasına (35,9125° K, 120,4625° B) göredir.

| Olay | T0 (UTC) | Mw | Δ (km) | PKD PGV_T (cm/s) |
|---|---|---|---|---|
| Peru 2001 | 2001-06-23 20:33 | 8,4 | 7608 | 0,0639 |
| Denali 2002 | 2002-11-03 22:12 | 7,9 | 3573 | 0,4960 |
| Colima 2003 | 2003-01-22 02:06 | 7,6 | 2491 | 0,0739 |
| Tokachi-oki 2003 | 2003-09-25 19:50 | 8,3 | 7852 | 0,0324 |
| Sumatra 2004 | 2004-12-26 00:58 | 9,0 | 14242 | 0,0870 |
| Kuril 2006 | 2006-11-15 11:14 | 8,3 | 6946 | 0,0767 |
| Kuril 2007 | 2007-01-13 04:23 | 8,1 | 6873 | 0,1440 |
| Wenchuan 2008 | 2008-05-12 06:28 | 7,9 | 11284 | 0,0418 |
| Samoa 2009 | 2009-09-29 17:48 | 8,1 | 7880 | 0,0288 |
| Maule 2010 | 2010-02-27 06:34 | 8,8 | 9397 | 0,1390 |

### 3.2 N (30 olay; Chao 2012 Tablo S1'de Q_CC = 0 olanların hepsi)

| # | T0 (UTC) | Olay (SAYIM adıyla) | PGV_T | # | T0 (UTC) | Olay | PGV_T |
|---|---|---|---|---|---|---|---|
| 1 | 2001-07-07 09:38 | M7,6 (−17,5; −72,1) | 0,0062 | 16 | 2007-01-21 11:27 | M7,5 (1,1; 126,3) | 0,0079 |
| 2 | 2001-10-19 03:28 | M7,5 (−4,1; 123,9) | 0,0021 | 17 | 2007-04-01 20:39 | Solomon 2007 | 0,0254 |
| 3 | 2002-03-05 21:16 | M7,5 (6,0; 124,2) | 0,0024 | 18 | 2007-08-15 23:40 | Peru 2007 | 0,0272 |
| 4 | 2002-09-08 18:44 | M7,6 (−3,3; 142,9) | 0,0086 | 19 | 2007-09-12 11:10 | G. Sumatra 2007 | 0,0190 |
| 5 | 2002-10-10 10:50 | M7,6 (−1,8; 134,3) | 0,0094 | 20 | 2007-09-12 23:49 | M7,9 (−2,6; 100,8) | 0,0186 |
| 6 | 2003-07-15 20:27 | M7,6 (−2,6; 68,4) | 0,0076 | 21 | 2007-11-14 15:40 | M7,7 (−22,2; −69,9) | 0,0139 |
| 7 | 2003-08-04 04:37 | M7,6 (−60,5; −43,4) | 0,0098 | 22 | 2009-01-03 19:43 | M7,7 (−0,4; 132,9) | 0,0074 |
| 8 | 2003-11-17 06:43 | M7,8 (51,1; 178,7) | 0,0091 | 23 | 2009-03-19 18:17 | M7,6 (−23,0; −174,7) | 0,0095 |
| 9 | 2004-11-11 21:26 | M7,5 (−8,2; 124,9) | 0,0101 | 24 | 2009-07-15 09:22 | M7,8 (−45,8; 166,6) | 0,0130 |
| 10 | 2004-12-23 14:59 | Macquarie 2004, M8,1 | 0,0615 | 25 | 2009-08-10 19:55 | M7,5 (14,1; 92,9) | 0,0035 |
| 11 | 2005-03-28 16:09 | Nias 2005, M8,6 | 0,0217 | 26 | 2009-09-30 10:16 | M7,5 (−0,7; 99,9) | 0,0029 |
| 12 | 2005-09-09 07:26 | M7,7 (−4,5; 153,5) | 0,0024 | 27 | 2009-10-07 22:03 | M7,7 (−13,0; 166,5) | 0,0095 |
| 13 | 2005-10-08 03:50 | M7,6 (34,5; 73,6) | 0,0128 | 28 | 2009-10-07 22:18 | M7,8 (−12,5; 166,4) | 0,0095 |
| 14 | 2006-04-20 23:25 | M7,6 (60,9; 167,1) | 0,0199 | 29 | 2010-04-06 22:15 | M7,8 (2,4; 97,0) | 0,0046 |
| 15 | 2006-07-17 08:19 | M7,7 (−9,3; 107,4) | 0,0013 | 30 | 2010-06-12 19:26 | M7,5 (7,9; 91,9) | 0,0069 |

- **Bilgi satırları (dalları değiştirmez):** Kunlun 2001 ve Tonga 2006 (Q = 1, PGV_T 0,017 ve 0,013; zayıf), Tohoku 2011
  (geliştirme verisi).
- **Genlik karıştırıcısı.** N'nin medyan PGV_T'si 0,0095 cm/s; 30 olayın 19'u 0,01'in altında. P'nin aralığı 0,029–0,496.
  PGV_T ≥ 0,02 olan yalnız 4 N olayı var: Macquarie 2004, Nias 2005, Solomon 2007, Peru 2007. Bu, D30M3'te modülasyon
  şartının neden bulunduğunu açıklar (§5).
- **Olaylar arası bağımlılık.**
  - Kuril 2006 ile Kuril 2007 aynı bölgeden, 2 ay arayla geldi.
  - Macquarie 2004 ile Sumatra 2004 arasında 3 gün var.
  - **N 27 ve N 28 (2009-10-07, Vanuatu) 15,6 dakika arayla geldi.** W'leri 1142 sn, K1b aralıkları 156 sn örtüşür;
    N 27'nin W'si N 28'in Q referans aralığının 932 saniyesini kapsar (INCELEME-1 §4; varışlar kaba, doğrulanamadı).
    43 olayda pencereleri başka bir olayın R'sine ya da W'sine taşan tek çift budur. **D-1 (aynen):**

    > "N 27 (2009-10-07 22:03) ile N 28 (2009-10-07 22:18) tek bir N birimidir ('Vanuatu 2009 birimi'; TR-7'nin Wharton
    > birimi örneği). Birimin W'si [N 27'nin W başı, N 28'in W sonu], K1b aralığı [N 27'nin K1b başı, N 28'in K1b sonu]'dur;
    > R ve Q N 27'ninkidir. E1'de birimin tetikleyicisi N 27'dir; N 28 'öteki olay' olarak M ≥ 7,0 kuralıyla (P ve S,
    > 240 sn) maskelenir. Birim, birleşik K1b aralığıyla kesişen ve ayıklamadan sağ çıkan en az bir küme varsa algılama
    > verir. n_N ve X_N'de birim bir kez sayılır; n_N en çok 29'dur. Z2'nin olay listesi ve dal (a)'nın n_N < 20 sınırı
    > değişmez. Bilgi satırı (dalı değiştirmez): iki olay ayrı sayılarak hesaplanan Z3 (iii)."

    Bu metinde "N birimi" 29 birimdir: 28 tek olay ve Vanuatu 2009 birimi. Sürüm 1'in "ayrı say" seçimi kaldırıldı.
- **Rastgele negatif pencereler:** TR-7b §6.3 aynen. Üreteç `default_rng(20261116 + 1)`, olaylar T0 sırasıyla, yalnız
  10 P ile Macquarie 2004 ve Peru 2007 için, olay başına 10 pencere (N_PK ≤ 120). Öteki N olayları için rastgele
  pencere çekilmez.

## 4. Ölçü: algılayıcı, pencereler ve sabit sızıntı kuralı K5

### 4.1 Değişmeyenler

- **Algılayıcı:** TR-7 §6.0–§6.5 aynen; yalnız §6.5 madde 3'ün sızıntı kuralı K5'tir.
- **Veri:** Parkfield istasyon listesi `tr7_parkfield_liste.csv` (sha256 9dca3380…b2b8), kanal seçimi ve 12 sınırı TR-7
  §3.2 aynen. Ana sınıf **liste (yüzey)** sınıfıdır. Kuyu sınıfı (BP/HRSN, PB) aynı kodla ayrı bir bilgi satırıdır ve
  hiçbir dalı değiştirmez (TR-7b §3).
- **Pencereler ve olay algılaması:** TR-7b §6.2 aynen. W ve R, TR-7 §5 ile istasyon başına Δ'dan hesaplanır. **K1b
  aralığı** = [T0 + Δ/4,6 km/s, T0 + Δ/3,0 km/s] (iz ortasında), olay başına saniyeye yuvarlanıp dondurulur. **Olay
  algılaması** = I′'su K1b aralığıyla kesişen ve ayıklamadan sağ çıkan en az bir küme.
- **E1 maskesi:** TR-7 §6.5.1a aynen. Olay başına pay dondurmadan önce yalnız katalogdan hesaplanır (Z2).
- **Negatif pencereler, f_PK, N_PK, MDA ve A90_PK:** TR-7b §6.3 aynen (MDA TR-7 §7.4 yöntemiyle, pencere başına 3
  başlangıç).
- **Modülasyon ölçüsü:** TR-7 §6.4 aynen. Başvuru istasyonu, ölçü M, dairesel kaydırmalı boş dağılım (1000 kaydırma) ve
  p ≤ 0,01 eşiği değişmez.
  - **Yazarın seçimi (üreteç sırası):** Parkfield kör koşusunda `default_rng(20261112 + 3)` yeni bir örnekle başlatılır.
    Kümeler olaylar T0 sırasıyla, olay içinde I′ başı sırasıyla işlenir. Marmara aşamasında TR-7 §6.4'ün sırası aynen
    uygulanır (yine yeni bir örnekle).
  - Parkfield'da "segment" Parkfield izidir; başvuru istasyonu iz köşe ortalamasına en yakın uygun istasyondur.
    Olay başına ayrı seçilir.

  **E-1 (INCELEME-2, aynen):**

  > "Başvuru istasyonu ve kanalı koşuda olay başına şöyle belirlenir (TR-7 §6.4 ve §6.6'nın uygulaması): liste
  > sınıfındaki istasyonların bant kodu B ya da H, alet kodu H olan ve olay anındaki StationXML epokunda |H(0,02 Hz)| /
  > |H(1 Hz)| ≥ 0,5 veren düşey kanallarından, indirilen veride W ve R örtüsü (TR-7 §4.2 sayımıyla) ≥ %90 olanlar
  > uygundur. Uygun kanalı olan istasyonlardan iz köşe ortalamasına en yakını seçilir; onun uygun kanallarından önce HH,
  > yoksa BH alınır. Yatay kanallar seçilen düşey kanalla aynı konum ve bant kodundan alınır; ikisi birden yoksa M yalnız
  > Z bileşeniyle hesaplanır. Bu seçim 2–8 Hz yolunun TR-7 §3.2 `z_kanal` seçiminden bağımsızdır. Aynı kural D-9'un 4 N
  > olayında da uygulanır."


### 4.2 K5 (TR-7b §11.1 ve §4.2'den aynen; eşik oynatılmaz)

Tanımlar, istasyonun kümedeki aşım saniyeleri üzerindedir (TR-7b §4.2 aynen):

> - Δ_y = medyan(L − m), Δ_d = medyan(L_d − m_d).
> - Q = [T0 + t_P(iz ortası, iasp91), W başı) ∖ maske. Bu, tetikleyicinin kendi cisim dalgası aralığıdır, yani
>   tetikleyiciden gelen ama tremor dışı bir referanstır.
> - Q'da L_d − m_d > 4σ_d olan saniyeler ≥ 30 ise (L − m) = a + b·(L_d − m_d) doğrusu en küçük karelerle kurulur.
> - Kalıntı e = (L − m) − (a + b·(L_d − m_d)), aşım saniyelerinde hesaplanır.
> - Bayrak: medyan(e) < 2σ.

TR-7b §11.1 aynen:

> - **ρ** = Spearman(L, zaman), aşım saniyelerinde. 10 saniyeden az varsa tanımsızdır.
> - **Sönüm şartı** = Δ_d ≥ Δ_y **ve** ρ ≤ −0,7. Amaç tekdüze sönen bölgesel kodayı yakalamaktır. −0,7 önceden sabittir;
>   veriyle seçilmedi.
> - **K5 (simetrik)** = Δ_d ≥ Δ_y **ve** (kalıntı < 2σ **veya** ρ ≤ −0,7).
>   - Kalıntı Q doğrusundan hesaplanır.
>   - Q'da L_d − m_d > 4σ_d olan saniye 30'dan azsa doğru a = b = 0 alınır. O zaman kalıntı = L − m ≥ 4σ olur ve kalıntı
>     şartı hiç sağlanmaz.
>   - Tetikleyici ve negatif pencerelerde formül aynıdır. Fark yalnız verinin kendisinden gelir.

**Toplama** TR-7 ile aynıdır: istasyonların ≥ yarısı bayraklıysa küme atılır. Darbe (§6.5.2), taban kayması (§6.5.3a)
ve maskeler TR-7 aynen.

**Uygulama** (yazarın seçimi; Z1'in "bayt bayt aynı" şartının denetlenebilir biçimi): Koşu kodu K5'i yeniden yazmaz.
`kayit/turetme/tr7b/tr7b_yapay2.py`'deki `K5` işlevini değiştirmeden içe aktarır. Gerçek veride ρ tanımsızsa (10
saniyeden az aşım saniyesi) ρ şartı sağlanmamış sayılır. Bu, `K5`'in kendi davranışıdır; bağımsız kod incelemesi bunu
doğrulamalıdır (§10, Z8).

**D-2 (aynen):**

> "Koşu kodu başlangıçta K5'in çağırdığı her dosyanın sha256'sını denetler: `kayit/turetme/tr7b/tr7b_yapay2.py`
> (ae995ba8802a934577cbf26051229360bcfb1a85d5d4d7dc16d358dfeaef437f; `K5`, `_rho`, `_delta`),
> `kayit/turetme/tr7b/tr7b_yapay.py` (e92715318e21a0200b66e3c130853f73cbc382b0398aef561619fcbe1bb74374; `secili`,
> `_k1_kalinti`) ve `kayit/turetme/tr7/tr7_cekirdek.py` (4a1b9131603d0f3d519cacb183fdbcccc106157b66392bf2d09350c9f49206f6;
> `KSIG`). Biri uyuşmazsa hiçbir şey hesaplanmadan durur. Bağımsız kod incelemesi K5'in çağrı ağacında başka dosya
> olmadığını doğrular."

**Ö-h (alındı; bilgi satırı, dal değiştirmez):** Olay başına "Q doğrusu kuruldu mu" yazılır. Gerekçe: Küçük
tetikleyicilerde Q'da 4σ_d'yi aşan saniye 30'dan az kalabilir. O zaman K5 N olaylarında çoğunlukla yalnız ρ koluyla
bayraklar, P'de kalıntı kolu da çalışır (INCELEME-1 §1 ek bulgu; tutucu yön, doğrulanamadı).

## 5. Başarı ölçütü: D30M3

**Z3 (aynen):**

> "'Ölçü sınandı' ⇔ aşağıdakilerin hepsi:
> (i) X_P ≥ max(⌈n_P/2⌉, X_min(n_P, f_PK)) (TR-7 §8 tanımı);
> (ii) FAR_PK = f_PK/N_PK ≤ 0,30;
> (iii) P'ye karşı N'de algılama oranı için Fisher kesin sınaması, tek yanlı p ≤ 0,05;
> (iv) algılama veren P olaylarından en az 3'ünde, algılama kümelerinden en az biri TR-7 §6.4 modülasyon ölçüsünde
> p ≤ 0,01 verir (başvuru istasyonu ve boş dağılım TR-7 §6.4 aynen).
> 'Olay algılaması' TR-7b §6.2 aynen."

**Tanımlar** (TR-7b §6.4'ten; n'ler Z2'den):
- n_P, n_N: §3 Z2 tanımıyla taranan P olayı ve N birimi sayısı (D-1: Vanuatu 2009 birimi bir kez sayılır).
- X_P, X_N: olay algılaması veren P ve N olayı sayısı.
- p_üst ve X_min(n, f): TR-7 §8 tanımları; n = n_P, f = f_PK, N = N_PK.

**Yazarın seçimleri** (Z3'ün boş bıraktığı uygulama ayrıntıları):
1. **Fisher sınaması:** 2×2 tablo [[X_P, n_P − X_P], [X_N, n_N − X_N]]. H1: P'de algılama oranı N'dekinden büyük.
   p = hipergeometrik üst kuyruk, P(X ≥ X_P | X_P + X_N, n_P, n_N). Bu, `tr7c_guc.py` `fisher_tek` işleviyle aynıdır;
   güç tablosu (§7) da bu tanımla hesaplandı.
2. **N_PK < 5 ise** (ii) sağlanmamış sayılır. TR-7 §7.2'nin "N_PK < 5 → ayırt edici değil" kuralının D30M3'teki
   karşılığı budur.
3. TR-7b §6.4'ün **"geçti, ayırt edici değil"** etiketi TR-7c'de yoktur. Onu doğuran iki şart, FAR tavanı ve P–N
   karşılaştırması, artık "sınandı"nın kendi parçalarıdır ((ii) ve (iii)). Sağlanmazlarsa dal (c) ya da (d) işler.
4. **Modülasyonun "ölçülebildiği" olay:** başvuru istasyonu olan (PGV'ye uygun, TR-7 §6.6; W ve R örtüsü ≥ %90) ve
   algılama kümesi için M hesaplanabilen olay. Bu tanım TR-7 §6.4'ün "yoksa 'ölçülemedi'" cümlesinin olay düzeyindeki
   okunuşudur.
5. **"Parkfield modülasyonu geçti" etiketi** (Marmara "VAR"ının şartı; TR-7 §8 sıra 5) TR-7b §6.4 aynen kalır:
   algılama veren P olaylarının en az ⌈X_P/2⌉'sinde en az bir algılama kümesi p ≤ 0,01. Z3 (iv) bundan bağımsız bir
   "sınandı" şartıdır. X_P ≥ 7 iken (iv) sağlanıp bu etiket sağlanmayabilir. O durumda dal (b) işler ve Marmara açılır,
   ama Marmara'da "VAR" verilemez (en çok "aday (modülasyon ölçüsü pozitif kontrolde doğrulanmadı)"). Bu, TR-7b §7'nin
   "aynen" okunmasının sonucudur, yeni kural değildir. **D-10 (aynen):**

   > "K1c (b) sağlanır ama 'Parkfield modülasyonu geçti' sağlanmazsa, K1c satırı Marmara indirilmeden önce 'ölçü sınandı
   > (Parkfield modülasyonu geçmedi: Marmara'da en çok \"aday\")' diye yazılır ve Marmara aşamaları açılır. Bu durumun
   > (b) içindeki olasılığı m_t 0,8'de ≈ 0,02, m_t 0,5'te ≈ 0,30–0,38'dir (`tr7c_inc1.json` `marmara_etiket`); o durumda
   > Marmara'nın kör verisi en çok 'aday' verebilecek bir taramada harcanır."
6. **Genliği eşlenmiş negatif etiketi. D-9 (aynen):**

   > "Genlik etiketi (bağlayıcı; dal değiştirmez): PGV_T ≥ 0,02 cm/s olan 4 N olayının (Macquarie 2004, Nias 2005,
   > Solomon 2007, Peru 2007) en az birinde, K1b aralığıyla kesişen ve ayıklamadan sağ çıkan bir kümede TR-7 §6.4
   > modülasyon ölçüsü (P olaylarındaki başvuru istasyonu tanımı ve boş dağılımla) p ≤ 0,01 verirse K1c satırına 'genlik
   > karıştırıcısı dışlanmadı' yazılır. Etkisi: Marmara'da 'VAR' verilemez, en çok 'aday'. Modülasyonu ölçülemeyen olay
   > etiketi tetiklemez; bu 4 olayda ölçülemeyen olay sayısı K1c satırına yazılır. Üreteç sırasında bu 4 olayın kümeleri
   > N olaylarıyla birlikte, T0 sırasıyla işlenir."

   Neden dal şartı değil de etiket (INCELEME-1 §5): Kural (en az bir olayda modülasyonlu algılama, G1) v0 ≤ 0,03 olan
   kilitli sızıntıyı büyük ölçüde yakalar (m_f 0,5'te "sınandı ve etiket yok" 0,89 → 0,09). Gerçek tremorda bedeli temiz
   negatifte 0,013–0,019'dur. Kirli negatifte ise 0,33–0,60'tır; dal şartı olsaydı gücün bu kadarını yerdi. Etiket olarak
   yalnız "VAR"ı engeller, yani tutucudur.

**"Ölçü sınandı"nın okunuşu. D-9 (aynen):**

> "'Ölçü sınandı' şu demektir: algılayıcı, Chao etiketini yüzey dalgasıyla eş periyotlu modülasyon taşıyan bir sinyalle,
> FAR ve Fisher şartları içinde kör olarak yeniden üretiyor. Tetikleyicinin yüzey dalgası genliğini izleyen tremor dışı
> bir 2–8 Hz sinyali (aletsel doğrusalsızlık, dinamik tetiklenmiş yerel ya da bölgesel mikrodepremler) bu sınamadan
> geçebilir. Bu biçim yalnız 4 genliği eşlenmiş negatifle ve kısmen sınanır. Marmara 'VAR' kalıbının sonuna '(Parkfield
> kör kontrolü genliğe bağlı, yüzey dalgasına kilitli sızıntıyı yalnız 4 genliği eşlenmiş negatifle sınadı)' eklenir."

**Neden D30M3** (INCELEME-0 §2 ve §5):
- TR-7b §6.4 (b) yalnız 2 negatifle kullanılsaydı, ayırt etmeyen bir algılayıcıyı %34–44 olasılıkla "sınandı" sayardı.
- Chao etiketi tetikleyici genliğiyle karışıktır. Genliğe duyarlı bir sızıntı algılayıcısı, 30 negatifle bile %95–99
  olasılıkla "ayırt ediyor" görünür (D30, v0 0,01–0,03 cm/s).
- Modülasyon şartı, zarfı yüzey dalgasından bağımsız olan sızıntıyı kıran, etiketten bağımsız fiziksel bir tanıktır.
  D30M3'ün genliğe bağlı sızıntıda yanlış kabulü ≤ 0,01 (m_f 0,05) ya da ≤ 0,06'dır (m_f 0,10). **D-4 (aynen):**

  > "m_f, §10 adım 2'de Y2 ve Y3 satırlarında ayıklamadan önce algılanan bütün kümelerde, K5'ten sağ çıkıp çıkmadığına
  > bakılmadan, TR-7 §6.4 ölçüsüyle ölçülür (en az 100 küme; daha azsa pencere sayısı artırılır); K5'ten sağ kalanlardaki
  > pay ayrıca yazılır. Ölçülen m_f > 0,10 ise taslak bağımsız incelemeye döner. Bu ölçüm yalnız yüzey dalgasına kilitli
  > olmayan sızıntıyı kapsar: Y2/Y3'ün telesismik zarfında yüzey dalgası periyodu yoktur. 2–8 Hz zarfı tetikleyicinin
  > yüzey dalgası genliğini izleyen tremor dışı bir sinyal için m_f tanım gereği 1'e yakındır; bu biçimde D30M3'ün yanlış
  > kabulü m_f 0,3'te 0,07–0,56, m_f 0,5'te 0,20–0,89'dur (`kayit/turetme/tr7c/inc1/tr7c_inc1.json`
  > `kilitli_sizinti`). '≤ 0,01 ya da ≤ 0,06' değerleri yalnız kilitli olmayan sızıntı için geçerlidir."
- "Sınandı" sonucu "algılayıcı yayımlanmış görsel tremor tanımını kör olarak yeniden üretiyor" diye okunur.
  "Algılayıcı tremoru doğru buluyor" sonucu çıkmaz (INCELEME-0 §3).

## 6. Hüküm dalları ve sırası

### 6.1 Parkfield kör kontrolü ("K1c"; sıra bağlayıcı)

**Yazarın seçimi (ad):** Kör kontrol TR-7b'nin K1b'sinden ayrılsın diye **K1c** diye anılır. TR-7b §7'de ve TR-7 §8
sıra 1'de "K1b (a), (c) ya da (d)" yerine "K1c (a), (c), (d) ya da (e)" okunur.

**Z4 (aynen; sıra bağlayıcı):**

> "(a) n_P < 8 ya da n_N < 20 → 'ölçü sınanamadı (Parkfield verisi yok)'.
> (b) Z3 sağlanır → 'ölçü sınandı'. Marmara aşamaları TR-7b §7 aynen açılır. (b′) etiketi TR-7b §6.4 aynen.
> (c) Z3 (i) ve (ii) sağlanır, modülasyon ≥ 3 algılama veren P olayında ölçülebilir, ama (iii) ya da (iv) sağlanmaz → 'ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş tremoru tetikleyici genliğinden ayıramadı)'.
> (d) Z3 (i) ya da (ii) sağlanmaz, MDA tanımlı ve A90_PK ≤ 100 µm/s → TR-7b §6.4 (c) cümlesi.
> (e) Öteki durumlar → 'ölçü sınanamadı (yöntem)'. Modülasyonun ölçülebildiği algılama veren P olayı 3'ten azsa
> (başvuru istasyonu yok ya da örtü < %90) dal (e)'dir: 'ölçü sınanamadı (modülasyon ölçülemedi)'.
> (b) dışında Marmara verisi indirilmez. Bilgi satırları: Kuril 2007 çıkarılmış Z3; liste sınıfına karşı kuyu sınıfı;
> PGV_T ≥ 0,02 cm/s olan 4 N olayında algılama sayısı; X_N/n_N ile X_P/n_P."

**D-7 (aynen; Z4'ün metni değişmez):**

> "Okuma kuralı (bağlayıcı): Z4 (e)'nin ikinci cümlesi ('Modülasyonun ölçülebildiği algılama veren P olayı 3'ten azsa …
> dal (e)'dir') yalnız (a) sağlanmıyorsa ve Z3 (i) ile (ii) sağlanıyorsa uygulanır; (i) ya da (ii) sağlanmıyorsa sıra
> (d) ve (e)'nin birinci cümlesidir. X_min(n_P, f_PK) yoksa (TR-7 §8) (i) sağlanmamış sayılır. A90_PK 'belirsiz' ya da
> '> 100 µm/s' ise (d)'nin A90 şartı sağlanmamış sayılır."

Örnek (INCELEME-1 §2): n_P 8, X_P 0, n_N 20, X_N 0, MDA tanımlı, A90 uygun → (i) sağlanmaz → dal (d); "modülasyon
ölçülemedi" yazılmaz.

**D-8, ikinci cümle (aynen):**

> "(c), (d) ve (e) cümlelerinin sonuna '(ayırt edilemez: gerçekleşen n_P, n_N ile, q 0,1'de görülebilir en küçük
> s = [..] (m_t 0,8) / [..] (m_t 0,5))' eklenir. Değerler `tr7c_inc1.json` `esik.MDE_tablosu_q0.1`'den okunur;
> tabloda olmayan n'ler için aynı işlevle (`tr7c_inc1.py` `esik`) koşudan önce hesaplanıp dondurulur."

**Ö-d (alındı):** Dal (c) cümlesinden sonra hangi şartın kaldığı parantezle yazılır: "(kalan: (iii))", "(kalan: (iv))"
ya da "(kalan: (iii) ve (iv))". Gerekçe: (iv)'ün tek başına kalması genlik karıştırıcısından çok m_t'nin düşüklüğünü
gösterir; Z4 cümlesi bunu ayırmıyor. Ek, D-8 ekinden önce gelir; Z4'ün cümlesi değişmez.

Sıranın özeti (yeni kural değildir; çelişkide Z4 ve D-7 geçerlidir):

| Sıra | Dal | Şart | Yazılan | Marmara |
|---|---|---|---|---|
| 1 | (a) | n_P < 8 ya da n_N < 20 | "ölçü sınanamadı (Parkfield verisi yok)" | indirilmez |
| 2 | (b) | Z3 (i)–(iv) hepsi | "ölçü sınandı" (+ (b′) "belirsiz"; + D-10 "Parkfield modülasyonu geçmedi"; + D-9 "genlik karıştırıcısı dışlanmadı" etiketleri varsa) | **açılır** (TR-7b §7); etiketlerden biri varsa Marmara'da en çok "aday" |
| 3 | (c) | (i), (ii) var; modülasyon ≥ 3 P olayında ölçülebilir; (iii) ya da (iv) yok | "ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş tremoru tetikleyici genliğinden ayıramadı)" + Ö-d + D-8 eki | indirilmez |
| 4 | (d) | (i) ya da (ii) yok (X_min yoksa (i) yok); MDA tanımlı; A90_PK ≤ 100 µm/s (belirsiz değil) | "ölçü sınanamadı (kör Parkfield olaylarında tetiklenmiş tremor ölçütü karşılamadı: X_P = [..] / n_P = [..]; A90_PK = [..] nm/s)" + D-8 eki | indirilmez |
| 5 | (e) | öteki; ikinci cümlesi yalnız (i) ve (ii) varken (D-7) | "ölçü sınanamadı (yöntem)" / "ölçü sınanamadı (modülasyon ölçülemedi)" + D-8 eki | indirilmez |

- **(b′) etiketi** (TR-7b §6.4 aynen): Algılama veren P olaylarının hepsinde bütün algılama kümeleri TR-7 §7.2 (b′) (i)
  ya da (ii) durumundaysa (çekirdek fazları olay başına iasp91 ile), "geçti, belirsiz" yazılır. Etkisi TR-7 (b′) aynen:
  Marmara açılır, "VAR" verilemez, her "görülmedi" cümlesine "(K1c yalnız belirsiz geçti)" eklenir.
- **Uygulama hatası yolu:** TR-7 §7.2 aynen, bir kez; yalnız (d) ya da (e) dalında. Tanım, eşik, pencere, liste ve
  sızıntı kuralı değişmez. Yazarın seçimi: (c) dalında bu yol **yoktur**. Gerekçe: (c), algılayıcının kör olaylarda
  çalıştığını ama ayırmadığını söyler; bir "hata düzeltmesi" orada sonuca bakarak kural seçmeye dönüşür.
- **Ek bilgi satırları** (yazarın seçimi; dalları değiştirmez):
  - N 27 ve N 28 ayrı sayılarak hesaplanan Z3 (iii) (D-1);
  - olay başına "Q doğrusu kuruldu mu" (Ö-h);
  - olay başına algılama, küme sayısı, atılma nedenleri ve K5 bayrak sayıları;
  - N olaylarındaki algılama kümelerinin modülasyon p'leri (m_f'nin gerçek veride kaba bir göstergesi);
  - Tohoku duman satırı (§9).

### 6.2 Marmara taraması (yalnız K1c (b) ise)

TR-7b §7 aynen: TR-7'nin Marmara tarafı (birimler, K0 ve bant, önsayım, pencereler, işleme zinciri, K2 negatif kontrol,
MDA, kestirici, §8 hüküm kuralları, X_min tabloları, kuyruk eşikleri, kalıplar, çıktı tabloları, tek koşu) değişmez.
Yalnız §6.5 madde 3 K5'tir. Segment hükümleri TR-7 §8 sırasıyladır: "veri yok", "ölçü güvenilmez (…)", "tetiklenmiş
tremor VAR", "aday, doğrulanmadı", "görülmedi". "VAR" ancak şunlar birlikte varsa verilebilir: K1c (b) "belirsiz" değil,
"Parkfield modülasyonu geçti" (§5 madde 5, D-10), K1c satırında "genlik karıştırıcısı dışlanmadı" etiketi yok (§5
madde 6, D-9) ve TR-7 §8 sıra 5'in öteki şartları. "VAR" kalıbının sonuna D-9'un eki yazılır: "(Parkfield kör kontrolü
genliğe bağlı, yüzey dalgasına kilitli sızıntıyı yalnız 4 genliği eşlenmiş negatifle sınadı)".

**"Görülmedi" cümlesi** (Z6: INCELEME-0 §4'teki alıntı aynen; TR-7 §8 "görülmedi" kalıbına eklenir):

> "S_k'de kaba τ ≥ 2 kPa olan n = [..] tetikleyicide tetiklenmiş tremor görülmedi. Bu segmentte algılanabilir en küçük
> genlik A90(S_k) = [..] nm/s'dir. Parkfield kör olaylarında algılanan tremorun 25 km'ye indirgenmiş medyan genliği
> A_PK = [..] nm/s'dir. A90(S_k) ≤ A_PK ise: Parkfield türü, ≈ 2 kPa'da tetiklenen ve Parkfield'dakine eşit genlikte
> tremor veren bir kaynak bu gürültüde görülürdü. Tetikleyici başına algılama olasılığı Parkfield'da ölçülen ŝ = [..] ise
> n tetikleyicide hiç görülmeme olasılığı (1 − ŝ)^n = [..] olur. A90(S_k) > A_PK ise: bu tarama Parkfield türü bir
> kaynağı dışlamaz, yalnız A90(S_k)'nın üstündeki tremoru dışlar. Bu cümle deprem olasılığı hakkında hiçbir şey
> söylemez."

**Z6 ek kural (aynen):**

> "A90(S_k)/A_PK > 1 olan segmentte 'görülmedi' cümlesine 'Parkfield türü kaynak bu gürültüde görülemezdi' eki
> bağlayıcıdır."

**D-6 (aynen):**

> "Z6 cümlesindeki (1 − ŝ)^n, segmentin n_açık'ıyla (TR-7 §8: taranan ana birimlerden W'sinin maskeli payı ≤ 0,50
> olanlar) hesaplanır ve '(1 − ŝ)^n = [..]' yerine '(1 − ŝ)^n_açık = [..] (n_açık = [..])' yazılır. n_açık < 5 ise bu
> yan cümlenin yerine 'hiç görülmeme olasılığı hesaplanmadı (n_açık < 5)' yazılır. A90(S_k) 'belirsiz' ya da
> '> 100 µm/s' ise ya da A_PK = 0 ise A90(S_k)/A_PK > 1 sayılır ve Z6 eki bağlayıcıdır."

**Boş tarama ne söyler.** Boş bir tarama ("görülmedi") **yalnız A90(S_k)/A_PK ≤ 1 olan segmentte** Parkfield türü bir
kaynak hakkında bir şey söyler. A90(S_k)/A_PK > 1 olan segmentte yalnız "A90(S_k)'nın üstündeki tremor yok" der ve Z6
eki zorunludur. A90(S_k) belirsizse ya da A_PK = 0 ise oran > 1 sayılır (D-6). Kentsel gürültüde gerçek s_Marmara,
ŝ_Parkfield'dan küçük olacaktır. (1 − ŝ)^n_açık bu yüzden bir alt
sınır değil, Parkfield koşullarında bir ölçektir. TR-7 §7.5 bu oranı yalnız bilgi satırı olarak yazıyordu; TR-7c'de
cümlenin şartıdır.

**Yazarın seçimleri (Z6 cümlesindeki köşeli yerlerin tanımı):**
- **A_PK:** Algılama veren her P olayında TR-7 §7.5 kestiricisiyle a (25 km'ye indirgenmiş, istasyon medyanı; olayda
  birden çok algılama kümesi varsa en büyüğü). A_PK, bu olay değerlerinin medyanıdır. X_P = 0 ise A_PK tanımsızdır,
  ama o durumda dal (b) zaten işlemez.
  - **Ö-a (alındı; bilgi):** A_PK yukarı yanlıdır: olay başına en büyük küme alınıyor ve P'deki yanlış alarm kümeleri de
    içeride. Bu yüzden iki bilgi satırı daha yazılır: yalnız modülasyonlu (p ≤ 0,01) kümelerden ve olay başına medyan
    kümeden hesaplanan A_PK. Üçünün en küçüğüyle A90(S_k)/A_PK da bilgi olarak yazılır. Bağlayıcı oran (Z6, D-6) TR-7
    §7.5 aynen tanımlı A_PK ile kalır.
- **ŝ:** INCELEME-0 §2 modelindeki p_P = 1 − (1 − s)(1 − q) bağıntısından,
  ŝ = max(0, (X_P/n_P − X_N/n_N) / (1 − X_N/n_N)). Yani P'deki algılama oranı, N'de ölçülen tetikleyicili yanlış alarm
  payından arındırılır. X_P/n_P de bilgi olarak yazılır. Gerekçe: ham X_P/n_P yanlış alarmı içerir, s'yi büyütür ve
  (1 − ŝ)^n'i iyimser yapar. Arındırılmış değer tutucudur.
  - **Ö-e (alındı; bilgi):** ŝ'nin yanına, X_P/n_P'nin Clopper–Pearson tek yanlı %95 alt sınırını aynı formüle koyarak
    hesaplanan ŝ_alt ile (1 − ŝ_alt)^n_açık yazılır. Gerekçe: n_P ≈ 10 ile ŝ'nin belirsizliği büyüktür.
- **Üs:** D-6 gereği n_açık (sürüm 1'deki "n" seçimi kaldırıldı; n'yi üs almak hiç görülmeme olasılığını olduğundan
  küçük gösteriyordu, yani yanlış kabul yönündeydi).

Ölçek için (1 − s)^n (INCELEME-0 §4; `tr7c_guc.json` `marmara_bos_olasiligi`; burada n, D-6 gereği n_açık yerine okunur):

| n | s = 0,2 | s = 0,3 | s = 0,5 |
|---|---|---|---|
| 8 | 0,17 | 0,06 | 0,004 |
| 12 | 0,07 | 0,01 | 0,0002 |
| 4 (kaba τ ×1/3) | 0,41 | 0,24 | 0,06 |

Bu değerler "Parkfield türü bir kaynak varken hiç görülmeme" olasılığıdır. Marmara'da kaynak olup olmadığının ya da
deprem olasılığının ölçüsü değildir.

**Marmara duyarlılığı.** TR-7'de Marmara verisi hiç indirilmedi. **Ölçülmüş bir Marmara A90'ı yoktur.** Elde olanlar:
Parkfield'da A50_PK 8,9 nm/s, A90_PK 11,2 nm/s (Tohoku dönemi negatifleri, K0); durağan gürültüde A50 ≈ 0,43 × gürültü
RMS (A_300 ölçeğinde). Kentsel gürültüde A90'ın daha büyük çıkacağı TR-7 §11'de önceden yazıldı.

## 7. Güç ve görülebilir en küçük etki

**Z5 (aynen):**

> "Ölçütün gücü 0,80 olan en küçük gerçek pozitif algılama oranı, tetikleyicili yanlış alarm 0,1 iken s ≈ 0,57'dir (gerçek
> tremor kümelerinin modülasyondan geçme olasılığı 0,8 varsayımıyla; 0,5 ise s ≈ 0,77). Bu değer yayımlanmış bir
> değerden değil, bizim seçimimizden gelir. s yarı olsaydı güç ≈ 0,2, iki katı olsaydı ≈ 1 olurdu. 'Sınanamadı' sonucu
> bu yüzden yalnız 'algılayıcı yüzey ağında bu olayların yarısından fazlasını, modülasyonlu biçimde, görmüyor'
> demektir. Hesap: `kayit/turetme/tr7c/tr7c_guc.py`."

**Varsayımlar** (betik başlığında; bunlar sonuç değil, model): olaylar bağımsız; P olayında algılama
p_P = 1 − (1 − s)(1 − q); N olayında q; rastgele negatif pencerede r (ana tabloda r = q); N_PK = 120; n_P = 10,
n_N = 30 (D-1'den sonra en çok 29; güçteki fark ≤ 0,006, §7.3). m_t, gerçek tremor kümesinin modülasyondan (p ≤ 0,01) geçme olasılığıdır. m_f, sızıntı kümesinin geçme
olasılığıdır.

### 7.1 Etki büyüklüğünün kaynağı (ESIK-DAYANAGI biçimi)

| Nicelik | Değer | Kaynak etiketi | Not |
|---|---|---|---|
| s: yüzey ağında otomatik algılayıcının Chao "tetikledi" olaylarındaki gerçek algılama oranı | görülebilir en küçük s ≈ 0,57 (m_t 0,8) / ≈ 0,77 (m_t 0,5) | **tahmin / bizim seçimimiz** | Yayımlanmış değer yok. Tek dolaylı işaret Tohoku geliştirmesi: yüzey ağında ayıklamadan önce 4 küme |
| q: tetikleyicili ama tremorsuz pencerede yanlış alarm | 0,1 (tabloda 0,05–0,3) | **tahmin / bizim seçimimiz** | TR-7 Parkfield negatiflerinde f_PK/N_PK = 2/10 (rastgele pencere, K0) yalnız ölçek verir |
| m_t | 0,8 ya da 0,5 | **tahmin / bizim seçimimiz** | Peng 2009'un "Love dalgasıyla modüle" gözlemi görseldir. TR-7 yapay sınamasında kilitli tremor 1,00 |
| m_f | 0,05 ya da 0,10 | **tahmin / bizim seçimimiz** | TR-7 yapay: sabit ve patlamalı tremor 0,00; 20 sn periyotlu kilitsiz 0,33–0,56. Sızıntı kümesinde ölçülmedi |
| Genliğe bağlı sızıntı q(v) = 1/(1 + (v0/v)²) | v0 0,01 / 0,03 / 0,1 cm/s | **tahmin** (karıştırıcının biçimi için model) | Chao PGV_T değerleri **literatür** (Ek Tablo S1) |
| α | Fisher tek yanlı 0,05; modülasyon p ≤ 0,01 | **uzlaşım** (TR-7 ile aynı) | – |

Literatürden ya da kuramdan gelen bir etki büyüklüğü **yoktur**. 0,57 / 0,77 bizim "güç 0,80" seçimimizin karşılığıdır.

### 7.2 "Sınandı" deme olasılığı (D30M3, n_P 10, n_N 30; `tr7c_guc.json` `D30M3_izgara_*`)

| Gerçek s | q = 0,05 | q = 0,1 | q = 0,2 | q = 0,3 |
|---|---|---|---|---|
| m_t 0,8: s 0,3 | 0,19 | 0,23 | 0,15 | 0,07 |
| s 0,5 | 0,65 | 0,67 | 0,51 | 0,23 |
| s 0,7 | 0,95 | 0,95 | 0,86 | 0,43 |
| s 0,9 | 1,00 | 1,00 | 0,99 | 0,54 |
| m_t 0,5: s 0,3 | 0,10 | 0,12 | 0,08 | 0,04 |
| s 0,5 | 0,42 | 0,42 | 0,34 | 0,16 |
| s 0,7 | 0,73 | 0,73 | 0,68 | 0,34 |
| s 0,9 | 0,90 | 0,90 | 0,90 | 0,49 |

q = 0,3 sütununu FAR ≤ 0,30 tavanı yaklaşık yarı yarıya keser; sütun bilerek tutucudur.

**Yanlış kabul** (tremor yok, s = 0; INCELEME-0 §2 ve §5):

| Durum | D30M3 "sınandı" olasılığı |
|---|---|
| Ayırt etmeyen algılayıcı (her büyük tetikleyicide t 0,3–0,9 olasılıkla ateşler; r = 0,05) | ≤ 0,0002 (dayanak: `tr7c_inc1.json` `bagimsiz.ayirt_etmeyen_D30M3_kendi`; Ö-g) |
| Genliğe bağlı, yüzey dalgasına kilitli olmayan sızıntı, v0 0,01 / 0,03 / 0,1 cm/s, m_f 0,05 | 0,010 / 0,006 / 0,001 |
| Aynı, m_f 0,10 | 0,062 / 0,040 / 0,004 |
| **Genliğe bağlı, kilitli sızıntı** (D-4; `tr7c_inc1.json` `kilitli_sizinti`), m_f 0,3 | 0,56 / 0,45 / 0,07 |
| Aynı, m_f 0,5 | 0,89 / 0,83 / 0,20 |
| Aynı, m_f 0,8 | 0,95 / 0,99 / 0,34 |
| Kilitli sızıntı, m_f 0,5, "sınandı **ve** D-9 genlik etiketi yok" | 0,09 / 0,25 / 0,16 |

Karşılaştırma: TR-7b §6.4 (b) (|N| = 2) ayırt etmeyen algılayıcıda 0,09–0,44; D30 (modülasyonsuz) genliğe bağlı
sızıntıda 0,36–0,99. Kilitli sızıntının Parkfield yüzey ağında var olup olmadığı ve m_f'nin gerçek değeri
**doğrulanamadı**; 0 € ile ölçülemez. Kalan açık "sınandı"nın okunuşuna (§5, D-9) yazılıdır.

### 7.3 Olay sayısına duyarlılık (s 0,7, q 0,1; `D30M3_olay_sayisi`)

| n_P | n_N = 30 | n_N = 20 | n_N = 10 |
|---|---|---|---|
| 10 | 0,95 / 0,73 | 0,93 / 0,72 | 0,85 / 0,67 |
| 8 | 0,88 / 0,56 | 0,86 / 0,55 | 0,77 / 0,51 |
| 6 | 0,71 / 0,34 | 0,67 / 0,33 | 0,62 / 0,31 |
| 5 | 0,58 / 0,23 | 0,56 / 0,22 | 0,50 / 0,21 |

Değerler "m_t 0,8 / m_t 0,5" biçimindedir. n_P < 8 ya da n_N < 20 dal (a)'dır. n_P = 8'de m_t 0,5 iken güç 0,56'ya düşer;
dal (a)'nın sınırı bu yüzden ancak m_t yüksekse yeterlidir (doğrulanamadı, §8). D-1 gereği n_N en çok 29'dur; 29 ile
30 arasındaki fark güçte ≤ 0,006'dır (INCELEME-1 §4).

**Gerçekleşen n'lerle görülebilir en küçük s** (q 0,1, güç 0,80; `tr7c_inc1.json` `esik.MDE_tablosu_q0.1`; m_t 0,8 /
0,5). D-8 ekinin değerleri buradan okunur:

| n_P \ n_N | 20 | 24 | 29 |
|---|---|---|---|
| 10 | 0,60 / 0,78 | 0,59 / 0,77 | 0,58 / 0,77 |
| 9 | 0,64 / 0,84 | 0,63 / 0,84 | 0,63 / 0,84 |
| 8 | 0,66 / 0,93 | 0,65 / 0,93 | 0,64 / 0,93 |

**Başvuru istasyonlu P olayı sayısı k'ya göre güç** (s 0,7, q 0,1; `esik.D1_kref_guc_s0.7_q0.1`; m_t 0,8 / 0,5; D-5
eşiğinin dayanağı):

| k | 3 | 4 | 5 | 6 | 7 | 8 | 10 |
|---|---|---|---|---|---|---|---|
| güç | 0,18 / 0,04 | 0,41 / 0,13 | 0,61 / 0,24 | 0,75 / 0,35 | 0,85 / 0,47 | 0,90 / 0,57 | 0,95 / 0,73 |

**Üstveri yoklamasının sonucu (D-5 gereği; sürüm 2 commit'inden sonra eklendi, `TR-7c_USTVERI.md`):** k = 10,
kestirilen n_P = 10, n_N = 29. Bu n'lerle görülebilir en küçük s ≈ 0,58 (m_t 0,8) / 0,77 (m_t 0,5) (q 0,1;
`esik.MDE_tablosu_q0.1`, nP10_nN29). 2001–2003'ün dört P olayında tek başvuru istasyonu BK.PKD'dir.

### 7.4 ×0,5 / ×2 duyarlılığı

Sürüm 1'in tablosu kaldırıldı: q satırları s₀'da değil s = 0,7'de hesaplanmıştı ve iki hücre kabaydı (INCELEME-1 §3).
**D-8, birinci cümle (aynen):**

> "×0,5 / ×2 duyarlılığı s₀'da (q 0,1; `kayit/turetme/tr7c/inc1/tr7c_inc1.json` `esik`): m_t 0,8 (s₀ 0,57): s ×0,5 →
> 0,20; s ×2 (1'de kırpılmış) → 1,00; q ×0,5 → 0,79; q ×2 → 0,65; m_t ×0,5 → 0,39. m_t 0,5 (s₀ 0,77): s ×0,5 → 0,23;
> s ×2 → 0,95; q ×0,5 → 0,81; q ×2 → 0,78; m_t ×0,5 → 0,30. Dal (a) sınırında (n_P 8, n_N 20) görülebilir en küçük s
> 0,66 (m_t 0,8) / 0,93 (m_t 0,5)'tir."

Aynı sayılar tablo olarak (güç, s₀'da):

| | m_t 0,8 (s₀ 0,57) | m_t 0,5 (s₀ 0,77) |
|---|---|---|
| s ×0,5 | 0,20 | 0,23 |
| s ×2 (1'de kırpılmış) | 1,00 | 0,95 |
| q ×0,5 (0,05) | 0,79 | 0,81 |
| q ×2 (0,2) | 0,65 | 0,78 |
| m_t ×0,5 | 0,39 | 0,30 |
| Dal (a) sınırında görülebilir en küçük s | 0,66 | 0,93 |

**Okuma.** "Sınanamadı" sonucu yalnız şunu dışlar: algılayıcı yüzey ağında bu olayların yarısından fazlasını
modülasyonlu biçimde görüyor. Yarı yarıya duyarlı bir algılayıcı, beş denemenin dördünde yine "sınanamadı" verir.
Kirli negatifler (Q = 0 olaylarının bir kısmında algılanabilir zayıf tremor) yanlış ret yönüne iter: π = 0,4'te D30'un
gücü s 0,7'de 0,58'e iner. Yanlış kabul yönüne itmez.

### 7.5 Marmara tarafının görülebilir en küçük etkisi

Önceden kestirilmedi. A90(S_k) koşuda TR-7 §7.4 ile ölçülür. Görülebilir etkinin anlamı Z6'nın A90(S_k)/A_PK oranına
bağlıdır (§6.2). Segment başına tetikleyici sayısı (≥ 2 kPa, kaba τ ×1) 9–12, ×1/3'te 1–4 (TR-7 sonucu).

## 8. Doğrulanamayanlar ve koşudan önce yapılacak 0 € yoklamalar

Kural (yazarın seçimi): Aşağıdaki yoklamalar **dondurmadan önce** yapılır. Yalnız üstveri (fdsnws/station, StationXML
yanıtı, fdsnws/availability), katalog ve literatür kullanılır. **Hiçbir kör olayın W ya da R penceresinde dalga formu
istenmez; dataselect çağrısı yapılmaz.** Sonuçlar ayrı bir "TR-7c ÜSTVERİ" belgesine ve betiğe yazılır, sonra bu taslağın
§3–§7'si gerekiyorsa yalnız sayı olarak (n_P, n_N kestirimi) güncellenir. Hiçbir eşik değişmez.

| # | Doğrulanamayan | Neden | Koşudan önce 0 € yoklama | Yoklamanın sonucu ne yapar |
|---|---|---|---|---|
| D1 | **Uzun periyot başvuru istasyonu, 2001–2010** (Z3 (iv) bunsuz uygulanamaz) | INCELEME-0 §7: kör P olaylarında sayılmadı | Her P olayı için TR-7 §6.6 ölçütü (bant B ya da H, alet H, \|H(0,02 Hz)\|/\|H(1 Hz)\| ≥ 0,5) StationXML yanıtından, W ve R örtüsü ≥ %90 availability'den. İz köşe ortalamasına en yakın uygun istasyon olay başına yazılır | **D-5 (aynen):** "Başvuru istasyonu olan (TR-7 §6.6; W ve R örtüsü ≥ %90) P olayı sayısı k < 7 ise TR-7c dondurulmaz ve kör koşu yapılmaz; kayda 'modülasyon şartı için yeterli başvuru istasyonu yok (k = [..]), kör olaylar harcanmadı' yazılır. Gerekçe: s 0,7, q 0,1'de D30M3'ün gücü k = 7'de 0,85 / 0,47, k = 6'da 0,75 / 0,35, k = 3'te 0,18 / 0,04'tür (m_t 0,8 / 0,5; `tr7c_inc1.json` `esik.D1_kref_guc_s0.7_q0.1`). k ≥ 7 ise k ve k ile hesaplanan görülebilir en küçük s §7'ye yazılır." |
| D2 | **Modülasyon geçme olasılıkları m_t ve m_f** | Tohoku'da hiçbir küme ayıklamadan sağ çıkmadı; Peng 2009 gözlemi görsel; faz sürümünün sızıntı kümelerindeki yanlış oranı ölçülmedi | m_t: dalga formu olmadan ölçülemez; literatürden (Peng 2009 ve Ghosh 2009'un yayımlanmış şekilleri) yalnız nitel okuma. m_f: §5'teki D-4 cümlesi aynen (Y2 ve Y3'te ayıklamadan önce algılanan bütün kümeler, en az 100 küme; K5'ten sağ kalanlardaki pay ayrıca) | m_t doğrulanamadı olarak kalır; güç tablosu iki değerle (0,8 / 0,5) yazılı kalır. D-4: ölçülen m_f > 0,10 ise taslak bağımsız incelemeye döner. **Kapsam (D-4):** bu ölçüm yalnız yüzey dalgasına kilitli olmayan sızıntıyı kapsar; kilitli sızıntının m_f'si 0 € ile ölçülemez (doğrulanamadı) |
| D3 | **Chao 2012'de Q'yu belirleyen istasyonlar ve inceleme yöntemi** | Tam metin okunmadı | Chao 2012 tam metni ve Peng 2009 Ek Tablo S1–S2, açık ve yasal bir kaynakta varsa okunur (0 €). Yoksa doğrulanamadı kalır | Yalnız yorum değişir (Q'nun kuyu mu yüzey mi olduğu, s'nin anlamı). Olay listesi Z2'de sabittir, değişmez |
| D4 | **Kör olaylarda gerçek W örtüsü ve E1 maske payları** (n_P, n_N) | Availability gün dosyası düzeyinde; E1 hesaplanmadı | E1: ComCat M ≥ 6,0 katalog satırlarıyla, TR-7 §6.5.1a kuralıyla, olay (birim) başına K1b aralığının açık payı. Örtü: availability'den liste istasyonu sayısı | Kestirilen n_P < 8 ya da n_N < 20 (N birimleriyle, en çok 29) ise dal (a) önceden belli olur. **Yazarın seçimi:** o durumda da dondurulmaz, kör koşu yapılmaz. Kayda "Parkfield verisi yok (üstveriden)" yazılır |
| D5 | **CI istasyonları** | EarthScope availability 404 verdi (SAYIM §5.2) | Aynı servis bir kez daha, belgelenmiş GET biçimiyle | Yalnız sayı (n_P, n_N) |
| D6 | **PGV → kPa dönüşümü** (G, β) | Varsayım | Yok (kuram). Z6 cümlesi "≈ 2 kPa" der; ölçek TR-7 §12 aynen | Değişmez |
| D7 | **Marmara A90** | Hiç ölçülmedi | Yok; ancak koşuda (dal (b) sonrası) ölçülür | – |
| D8 | **Ham yoklama günlükleri** (`/mnt/project-files/turetme/tr7b-ham/`) | INCELEME-0'da açılmadı; körlük beyanı yalnız betik koduna dayanıyor | Bağımsız kod incelemecisi günlükte W'ye düşen bir dataselect satırı olmadığını denetler (yalnız istek satırları; gövde yok) | W'ye düşen bir istek bulunursa §11'e yazılır, o olay için "kör değil" notu eklenir |
| D9 | **2009-10-07 çifti** (N 27, N 28) | W pencereleri örtüşüyor; varışlar kaba | E1 hesabında (D4) birleşik birimin W'si, K1b aralığı ve N 28'in E1 maskesi katalogla ve iasp91 ile hesaplanır | D-1 gereği çift tek birimdir; yoklama yalnız birimin pencerelerini sayıyla sabitler |

**Yoklama sırası** (yazarın seçimi): D4 ve D1 önce yapılır. İkisinden biri dondurmayı engellerse ötekiler yapılmaz.

**E-2 (INCELEME-2, aynen; D-5'in tamamlayıcısı):**

> "D-5 yalnız koşudan önce, üstveriyle bir kez uygulanır (sonuç: k = 10, `TR-7c_USTVERI.md`). Koşuda E-1 ile başvuru
> kanalı bulunamayan olay modülasyon bakımından 'ölçülemedi' sayılır; n_P ya da n_N'de, X_P ya da X_N'de ve Fisher
> sınamasında kalır, yalnız modülasyonun ölçülebildiği olaylara girmez. Koşudaki k (k_koşu) 7'nin altına inse de koşu
> durdurulmaz ve yeniden koşulmaz; dal yalnız Z4 ve D-7 ile verilir. Verideki örtü eksikliği uygulama hatası sayılmaz.
> K1c satırına 'k: üstveriden 10, koşuda [k_koşu]' yazılır. k_koşu < 10 ise k_koşu ile hesaplanan güç (s 0,7, q 0,1;
> `tr7c_inc1.json` `esik.D1_kref_guc_s0.7_q0.1` işlevi) bilgi olarak eklenir."

## 9. Tohoku'da duman sınaması

**Z7 (aynen):**

> "K5 dondurulmadan önce Tohoku geliştirme verisinde (`tr7b_gelistirme.py` girdileri) bir kez çalıştırılır. Yalnız kodun
> gerçek zarflarla çalıştığını gösterir. Sonucu ne olursa olsun K5 ve Z3 değişmez."

**Yazarın seçimleri:**
- Yeni indirme yapılmaz. Yalnız TR-7'nin hâlihazırda işlenmiş Tohoku–Parkfield zarfları kullanılır.
- Koşu kodu K1c dalını hesaplamaz. Yazılanlar: kodun çalışıp çalışmadığı, TR-7'nin 4 W kümesinde ve saf P aralığı
  kümesinde K5 bayrak sayıları, sağ kalan küme sayısı.
- TR-7 zarf deposunda başvuru istasyonunun uzun periyot hızı varsa modülasyon yolu da bir kez çalıştırılır; yoksa
  "duman sınaması modülasyonu kapsamadı" yazılır (doğrulanamadı: depoda bu verinin olup olmadığı bu taslakta
  denetlenmedi).
- Sonuç ne olursa olsun hiçbir dal değişmez. Kod çökerse yalnız okuma ve ayrıştırma katmanı düzeltilir, düzeltme
  "duman sonrası düzeltme" başlığıyla yazılır ve bağımsız kod incelemesine (§10 adım 4) dahil edilir.
- **D-3:** Duman sınaması karar metni dondurulduktan **sonra** yapılır (§10 adım 3). Duman sonucu hiçbir "yazarın
  seçimi"ni değiştirmez.
- **Ö-c (alındı):** Dört TR-7 kümesinin ve saf telesismik P kümesinin (05:57:43–06:05:57) modülasyon M'si ve p'si
  yazılır (modülasyon yolu çalıştırılabiliyorsa). Saf P kümesi bilinen, tremor dışı gerçek bir kümedir. Okunuşu önceden
  yazılır: "p ≤ 0,01 ise kilitsiz sızıntıda da m_f'nin küçük olmadığına dair tek gözlemlik işaret; dal değişmez, D-3
  gereği metin değişmez, yalnız §12'ye yazılır."

## 10. Koşu sırası

Tek koşu kuralı TR-7 §10.6 aynen, aşama adlarında K1 → K1c.

1. **Üstveri yoklaması** (§8; 0 €; dalga formu yok). D1 (D-5: k < 7) ya da D4 engellerse burada durulur, kör olaylar
   harcanmaz.

   **D-3 (aynen; adım 1 ile adım 2 arasına):**

   > "Karar metni dondurması: §8'in üstveri yoklamaları bittikten sonra, §10 adım 2'deki m_f ölçümünden ve adım 3'teki
   > Tohoku duman sınamasından önce, bu metin 'Durum: KARAR METNİ DONDURULDU' satırıyla commit ve push edilir; sha256'sı
   > deftere yazılır. Bundan sonra yalnız şunlar değişebilir: §8 yoklamalarının sayıları (n_P, n_N kestirimi, başvuru
   > istasyonlu P olayı sayısı k), koşu kodunun okuma ve ayrıştırma katmanı ('duman sonrası düzeltme') ve bağımsız kod
   > incelemesinin dal, eşik, olay listesi, birim, A_PK, ŝ ve n tanımlarına dokunmayan düzeltmeleri. Bu tanımlara dokunan
   > her değişiklik yeni bir bağımsız metin incelemesi ister. Tohoku duman sınamasının sonucu hiçbir 'yazarın seçimi'ni
   > değiştirmez."

   D-3'teki "adım 2" ve "adım 3" aşağıdaki 2. ve 3. adımlardır. Karar metni dondurmasını koordinatör yapar.
2. **Kod, yalnız yapay veride.** TR-7'nin KD'si (§7.1 D1–D15, bantlar aynen) ve TR-7b §11.2 satırları K5 ile koşulur.
   Bunlara Z3/Z4 dal mantığı için yapay sayılarla birim sınamaları ve mutasyonlar eklenir. Örnek mutasyonlar: Fisher
   yönü ters; (iv)'de "≥ 3" yerine "≥ 1"; dal (a) eşiği n_N < 2; (b) dışında Marmara indirme; Vanuatu birimi iki kez
   sayılır (D-1); D-7 okuma kuralı kaldırılır; D-9 etiketi Marmara "VAR"ını engellemez. D2'nin m_f ölçümü (D-4) de bu
   adımdadır. KD bantlarından biri kalırsa kod düzeltilir; K5 ve eşikler değişmez. TR-7b §11.2 satırları yalnız bilgidir.
   Değerlerin Tur 2/3 değerleriyle tutarlılığı (Monte Carlo hatası içinde) kodun K5'i doğru çağırdığını gösterir; K5
   seçimini etkilemez.
3. **Tohoku duman sınaması** (§9, Z7). Karar metni dondurulduktan sonra (D-3) ve kod incelemesinden önce yapılır;
   böylece duman sonrası bir düzeltme varsa o da incelenir.
4. **Bağımsız kod incelemesi** (Z8, aynen): "TR-7b koşu kodu (K5 ile K1b) dondurulmadan önce bağımsız kod incelemesi
   gerekir. Gerekçe: K5 bu kodda ilk kez yapay ortam dışında çalışacak; Q referansı ve ρ gerçek maske parçalarıyla
   hesaplanacak." "Koşulabilir" hükmü gerekir. İnceleme D8'i, D-2'nin çağrı ağacını ve Ö-i'nin iki notunu da denetler:
   `_rho` Spearman'ının eşit değerlerde ortalama sıra kullanmaması ve `_k1_kalinti`'nin Q indislerinin gerçek veride
   saniye eşlemesi ile maske hizası.
5. **Koşu dondurması.** Bu metin "Durum: DONDURULDU …" satırıyla commit ve push edilir. Kod, dondurulmuş metnin ve
   D-2'deki üç dosyanın sha256'larını denetlemeden gerçek kipte çalışmaz (TR-13b §12.1 örneği; yazarın seçimi).
6. **Parkfield kör kontrolü, tek koşu.** Aşamalar: manifest → K1c-indirme (P, N ve rastgele negatifler) → K1c-negatif
   (rastgele negatifler: f_PK, N_PK, MDA) → K1c-algılama. Algılama aşamasında sıra (yazarın seçimi): önce 29 N birimi
   (30 olay), sonra 10 P olayı. Z3 ve Z4 yalnız bütün olaylar bittikten sonra hesaplanır. Hüküm dosyası bir kez yazılır.
   Durum dosyası `kayit/turetme/tr7c/TR7C_KOSU_DURUM.json`, her aşamada commit ve push edilir.
   **Ö-b (alındı):** Durum dosyası aşama sonlarında yalnız "tamamlandı / hata" ve dosya sha256'larını taşır; X_N, f_PK
   gibi sayılar hüküm dosyasına kadar yazılmaz. N aşamasından sonra koşu yalnız teknik çöküşle durur (TR-7 §10.6).
7. **Ancak K1c (b) ise:** Marmara-indirme → Marmara-negatif → Marmara-algılama → hüküm (TR-7b §7 aynen, Z6 ile). (b)
   dışındaki her dalda koşu 6. adımda biter ve Marmara verisi indirilmez.

## 11. Körlük beyanı

- Bu taslak için hiçbir ağ isteği yapılmadı. Hiçbir dalga formu indirilmedi, açılmadı ya da işlenmedi. 2026 ve sonrası
  veri yoktur; bütün kör olaylar 2001–2010 arasındadır.
- **Kör olaylar.** W pencerelerinde bugüne dek hiçbir dalga formu istenmedi (Z1). SAYIM'ın tek dataselect isteği olay
  başına sınıf başına T0 − 1800 sn'den başlayan 10 sn'dir; bu aralık R'nin içinde, W'nin öncesindedir. Gövde
  saklanmadı. Bu beyan betik koduna ve SAYIM metnine dayanır. Ham günlükler açılmadı (D8).
- **TR-7'nin Parkfield negatif pencereleri** 2011-02-10 ile 2011-03-08 arasındadır; kör olaylarla kesişmez.
- **Tohoku 2011 geliştirme verisidir.** Kural tanısı orada yapıldı. Kör değildir ve hiçbir dalı değiştirmez.
- **Marmara** dalga formu hiç indirilmedi; Marmara tarafı tam kördür.
- **Kör olmayan kısım.** Yazar Peng 2009'un tam metnini okudu ve olaylarda tremorun ne zaman, hangi dalgayla geldiğini
  literatürden bilir (SAYIM §5.4). K5'in eşikleri bundan önce yapay veriyle sabitlendi. Bu bilgi ancak bundan sonra bir
  ayar yapılırsa zarar verir; §2 bu yolu kapatır. Yazar K5'in Tur 2 ve Tur 3 yapay sonuçlarını, INCELEME-0 ve
  INCELEME-1'in hesaplarını ve Chao etiketleriyle PGV_T değerlerini biliyor. Algılayıcının bu 40 olaydaki çıktısını
  bilmiyor.
- **Tohoku duman sınaması** (D-3): karar metni dondurulmadan görülmez; Z7'nin korumadığı seçimler bu yolla
  değiştirilemez.
- **Sürüm 2 için** hiçbir ağ isteği yapılmadı. §8'in üstveri yoklaması (D1, D4) sürüm 2 commit edildikten sonra yapılır
  ve ayrı bir belgeye yazılır (`TR-7c_USTVERI.md`).

## 12. Bilinen zayıflıklar (INCELEME-0 §3–§4'ten; çözülmez, yazılır)

1. **İlişkili hatalar.** Chao/Peng etiketleri NCSN yüzey istasyonlarını da içeren aynı kayıtlardan çıktı. Görsel
   incelemeyi yanıltan bir sızıntı (ör. Kuril 2006'da artçı P'leri) algılayıcıyı da yanıltabilir ve uyumu şişirir.
2. **Yöntem benzerliği.** Etiket ile algılayıcı aynı şeye bakıyor: 2–8 Hz zarfın yüzey dalgasıyla eş zamanlılığına.
3. **Kirli negatif.** "Tetiklemedi" etiketi görsel incelemedir ve büyük ölçüde kuyu kayıtlarına dayanır. Daha duyarlı bir
   algılayıcı Q = 0 olaylarında gerçek zayıf tremor bulabilir. Bunun yönü yanlış rettir.
4. **Yüzey–kuyu farkı.** Ana sınıf yüzey ağıdır, Chao'nun büyük ölçüde kuyu/PKD. s düşer; yanlış ret yönündedir.
5. **Bağımsızlık.** Kuril 2006/2007 ve Macquarie/Sumatra 2004. Binom ve Fisher bağımsızlık varsayar. 2009-10-07
   çifti D-1 ile tek birimdir.
6. **Kilitli, genliğe bağlı sızıntı** (INCELEME-1 §5). Tetikleyicinin yüzey dalgası genliğini izleyen tremor dışı bir
   2–8 Hz sinyali (aletsel doğrusalsızlık, dinamik tetiklenmiş yerel ya da bölgesel mikrodepremler; ör. Peng 2010'un
   Maule'de bildirdiği Coso depremleri) modülasyon şartından geçebilir. Tohoku'da bu ağda genliğe bağlı, ağ çapında
   tutarlı 2–8 Hz artışı gerçektir (TR-7b §2), ama tremor mu sızıntı mı olduğu gösterilemedi. Bu biçim yalnız 4 genliği
   eşlenmiş negatifle ve kısmen sınanır (D-9). Büyük v0 ve büyük m_f birlikteyse açık kalır; 0 € ile kapatılamaz.
7. **Aktarım.** Parkfield'da geçen bir kör kontrol yalnız şunu gösterir: kırsal, yoğun, yerel bir yüzey ağında,
   Parkfield–Cholame türü (20–25 km) ve ≈ 2 kPa'nın üstünde tetiklenen bir kaynağın tremoru bu algılayıcıyla s oranında
   yakalanır. Marmara'ya taşınmayanlar: kentsel ve durağan olmayan gürültü, KO'ya dayalı geometri, kaynağın varlığı ve
   derinliği, kaba τ'daki ×3 belirsizlik.
8. TR-7 §12'nin bütün maddeleri aynen geçerlidir.

## 13. İstanbul'a bağ

TR-7 §13 aynen. Mutlak olasılık ya da olasılık çarpanı yazılmaz; sonuç bir olasılık terimi değildir. Marmara sonucunun
anlamı yalnız TR-7 §13'ün iki cümlesinden biridir: "dinamik gerilmeye duyarlı derin kayma bölgesi gözlendi" ya da "bu
duyarlılıkla (A90, kaba τ, n) gözlenmedi". TR-7c bunlara Z6'nın A90(S_k)/A_PK şartını ekler. Z6 cümlesindeki
(1 − ŝ)^n_açık (D-6), Parkfield türü bir kaynağın bu taramada görülmeme olasılığıdır. İstanbul'da deprem olasılığı hakkında hiçbir
şey söylemez. K1c (b) dışında Marmara hakkında hiçbir cümle kurulmaz.

## 14. İnceleme eşleme tabloları

### 14.1 `TR-7c_INCELEME-0.md` §6

| Madde | İçerik | Bu metinde nerede | Biçim |
|---|---|---|---|
| Z1 | Sapma ve körlük beyanı | §2 (aynen), §11 | alıntı aynen; §2 sonunda kapatılan yollar (yazarın seçimi), §4.2 uygulama (yazarın seçimi) |
| Z2 | Olay listesi; n_P, n_N tanımı; E1 katalogdan; rastgele negatifler | §3 (aynen), §3.1–§3.2 tablolar | alıntı aynen; N 27/28 sürüm 2'de D-1 ile tek birim |
| Z3 | Başarı ölçütü D30M3 | §5 (aynen) | alıntı aynen; Fisher biçimi, N_PK < 5, "ölçülebilir" tanımı yazarın seçimi |
| Z4 | Dallar ve sırası; bilgi satırları | §6.1 (aynen) | alıntı aynen; "K1c" adı, (c)'de uygulama hatası yolunun olmaması ve ek bilgi satırları yazarın seçimi |
| Z5 | Görülebilir en küçük etki, kaynak, ×0,5 / ×2 | §7 (aynen), §7.1–§7.4 | alıntı aynen; tablolar `tr7c_guc.json`'dan |
| Z6 | Marmara "görülmedi" cümlesi ve A90/A_PK eki | §6.2 (aynen), §13 | alıntı aynen; A_PK ve ŝ tanımları yazarın seçimi |
| Z7 | Tohoku duman sınaması, dal değiştirmez | §9 (aynen), §10 adım 3 | alıntı aynen; yer ve kapsam yazarın seçimi |
| Z8 | Dondurmadan önce bağımsız kod incelemesi | §10 adım 4 (aynen) | aynen; D8 denetimi eklendi |
| §7 doğrulanamayanlar | ham günlükler, Chao istasyonları, m_t/m_f, başvuru istasyonu, PGV→kPa, örtü/E1, Marmara A90 | §8 D1–D8 | her biri için 0 € yoklama |

### 14.2 `TR-7c_INCELEME-1.md` §9–§10 (sürüm 2)

Zorunlu düzeltmeler (hepsi incelemedeki kesin cümleyle aynen işlendi):

| Madde | İçerik | Bu metinde nerede |
|---|---|---|
| D-1 | N 27 / N 28 tek birim ("Vanuatu 2009 birimi"), n_N ≤ 29 | §3.2 (aynen); §3 veri kuralı, §6.1 bilgi satırı, §7.3, §8 D4/D9, §10 adım 2 ve 6 |
| D-2 | K5'in çağrı ağacındaki üç dosyanın sha256 denetimi | §4.2 (aynen); §10 adım 4–5 |
| D-3 | Karar metni, m_f ölçümünden ve Tohoku duman sınamasından önce dondurulur | §10 adım 1 ile 2 arası (aynen); §9, §10 adım 3, §11 |
| D-4 | m_f ≥ 100 kümede, ayıklamadan önce; kapsam yalnız kilitsiz sızıntı | §5 "Neden D30M3" (aynen); §7.2, §8 D2 |
| D-5 | D1 durma eşiği k < 7 | §8 D1 (aynen); §7.3 k tablosu; §10 adım 1 |
| D-6 | (1 − ŝ)^n_açık; n_açık < 5; A90 belirsiz ya da A_PK = 0 ise oran > 1 | §6.2 (aynen); §13 |
| D-7 | Dal (e) ikinci cümlesinin okunuşu; X_min yoksa ve A90 belirsizse | §6.1 Z4'ün altı (aynen); özet tablo |
| D-8 | §7.4'ün s₀'daki sayıları; (c), (d), (e)'ye "ayırt edilemez (MDE)" eki | §7.4 (aynen, birinci cümle); §6.1 (aynen, ikinci cümle); §7.3 MDE tablosu |
| D-9 | Genliği eşlenmiş 4 N olayı etiketi; "sınandı"nın okunuşu; Marmara "VAR" eki | §5 madde 6 ve okunuş (aynen); §6.1 özet tablo; §6.2; §7.2; §12 madde 6 |
| D-10 | (b) iken "Parkfield modülasyonu geçti" yoksa K1c satırı ve olasılığı | §5 madde 5 (aynen); §6.1 özet tablo; §6.2 |

Öneriler:

| Öneri | Alındı mı | Nerede / gerekçe |
|---|---|---|
| Ö-a A_PK'nın iki ek bilgi satırı | alındı (bilgi) | §6.2. Bağlayıcı oran TR-7 §7.5 aynen tanımlı A_PK ile kalır, çünkü TR-7b §7 "aynen" der |
| Ö-b durum dosyasında ara sayı yok | alındı | §10 adım 6 |
| Ö-c Tohoku duman satırında modülasyon M ve p, önceden yazılı okunuş | alındı | §9 |
| Ö-d dal (c)'de kalan şartın parantezle yazılması | alındı | §6.1 |
| Ö-e (1 − ŝ_alt)^n_açık bilgi satırı | alındı (bilgi) | §6.2 |
| Ö-f `ESIK-DAYANAGI.md`'ye TR-7c satırı | **alınmadı (ertelendi)** | İnceleme bunu "dondurma sürümünde" istiyor; dondurmayı koordinatör yapar. Bu sürüm `ESIK-DAYANAGI.md`'yi değiştirmez; satırın içeriği §7.4'te hazır |
| Ö-g "≤ 0,0002" satırının dayanağı | alındı | §7.2 |
| Ö-h olay başına "Q doğrusu kuruldu mu" | alındı (bilgi) | §4.2, §6.1 |
| Ö-i `_rho` eşitlikleri ve `_k1_kalinti` indis hizası | alındı (kod incelemesine not) | §10 adım 4 |

Not: Koordinatör eşleme tablosunu "§11" diye andı. Bu metinde §11 körlük beyanıdır ve INCELEME-1'in düzeltme cümleleri
bölüm numaralarına (§3.2, §4.2, §5, §6.1, §6.2, §7.4, §8, §10) atıf yapar. Numaralar değişmesin diye tablo §14.2'ye
kondu.

## 15. Bu taslakta açık kalanlar (dondurmadan önce kapanmalı)

- §8'in D1, D4 ve D5 yoklamaları sürüm 2'den sonra yapıldı (`TR-7c_USTVERI.md`): k = 10, n_P = 10, n_N = 29; kural
  sonucu "dondurulabilir". D2, D3 ve D8 yapılmadı.
- Karar metni dondurması (D-3) ve koşu dondurması yapılmadı; ikisini de koordinatör yapar.
- `ESIK-DAYANAGI.md` TR-7c satırı (Ö-f) dondurma sürümüne ertelendi.
- Koşu kodu yazılmadı; yapay sınamalar, mutasyonlar ve m_f ölçümü yok.
- Tohoku duman sınaması yapılmadı.
- Yazarın sınav öncesi beklentisi (TR-7 §11 ve TR-7b §10 biçiminde) dondurma sürümünde, kör koşudan önce yazılır.
- "Yazarın seçimi" işaretli maddeler bağımsız kod incelemesinde ya da ayrı bir metin incelemesinde onaylanmadı.
