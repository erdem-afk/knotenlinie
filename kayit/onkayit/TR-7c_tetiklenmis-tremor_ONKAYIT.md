# TR-7c ön kaydı: sabit sızıntı kuralı (K5) ve kör Parkfield kontrolüyle Marmara'da tetiklenmiş tremor taraması

Durum: TASLAK (sürüm 1); dondurulmadı, hiçbir koşu için bağlayıcı değildir. Kod yok, gerçek veri yok.
Tarih: 17 Kasım 2026.

Bağımsız inceleme: `TR-7c_INCELEME-0.md` (fikir düzeyinde, hüküm **DÜZELTMEYLE KABUL**). Bu taslak o incelemenin §6'daki
düzeltme cümlelerini (Z1–Z8) **değiştirmeden** taşır. Hangi cümlenin nerede olduğu §14'teki eşleme tablosundadır.

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

1. Bu metin; alıntılanan Z1–Z8 cümleleri bu metnin parçasıdır.
2. `TR-7c_INCELEME-0.md`, yalnız bu metnin sustuğu yerde.
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
yok)".**

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
  - **N 27 ve N 28 (2009-10-07, Vanuatu) 15 dakika arayla geldi.** Δ ≈ 9370 km'de W pencereleri (T0 + Δ/5,0 ile
    T0 + Δ/2,8 + 600 sn arası) büyük ölçüde örtüşür (≈ 20 dk). Kaba iasp91 kestirimine göre ikinci olayın P'si
    birincinin W'sinden hemen önce, S'si W'nin içine düşer; E1 (M ≥ 7: P ve S, 240 sn) bunu maskeler (doğrulanamadı:
    varış zamanları hesaplanmadı, yalnız kaba). Bu iki satır büyük ölçüde aynı veriye bakar. INCELEME-0 bunu ayrıca anmıyor. **Yazarın seçimi:** Z2 gereği ikisi de N'de kalır ve
    ayrı sayılır. Bir bilgi satırında N 28 çıkarılarak Z3 (iii) yeniden hesaplanır. Bu satır dalı değiştirmez.
- **Rastgele negatif pencereler:** TR-7b §6.3 aynen. Üreteç `default_rng(20261116 + 1)`, olaylar T0 sırasıyla, yalnız
  10 P ile Macquarie 2004 ve Peru 2007 için, olay başına 10 pencere (N_PK ≤ 120). 28 N olayı için rastgele pencere
  çekilmez.

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
`kayit/turetme/tr7b/tr7b_yapay2.py`'deki `K5` işlevini değiştirmeden içe aktarır. Başlangıçta dosyanın sha256'sını
`ae995ba8…f437f` ile karşılaştırır; uyuşmazsa hiçbir şey hesaplamadan durur. Gerçek veride ρ tanımsızsa (10 saniyeden
az aşım saniyesi) ρ şartı sağlanmamış sayılır. Bu, `K5`'in kendi davranışıdır; bağımsız kod incelemesi bunu
doğrulamalıdır (§10, Z8).

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
- n_P, n_N: §3 Z2 tanımıyla taranan P ve N olayı sayısı.
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
   "aynen" okunmasının sonucudur, yeni kural değildir.

**Neden D30M3** (INCELEME-0 §2 ve §5):
- TR-7b §6.4 (b) yalnız 2 negatifle kullanılsaydı, ayırt etmeyen bir algılayıcıyı %34–44 olasılıkla "sınandı" sayardı.
- Chao etiketi tetikleyici genliğiyle karışıktır. Genliğe duyarlı bir sızıntı algılayıcısı, 30 negatifle bile %95–99
  olasılıkla "ayırt ediyor" görünür (D30, v0 0,01–0,03 cm/s).
- Modülasyon şartı bu karıştırıcıyı kıran tek fiziksel, etiketten bağımsız tanıktır. D30M3'ün genliğe bağlı sızıntıda
  yanlış kabulü ≤ 0,01 (m_f 0,05) ya da ≤ 0,06'dır (m_f 0,10).
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

Sıranın özeti (yeni kural değildir; çelişkide Z4 geçerlidir):

| Sıra | Dal | Şart | Yazılan | Marmara |
|---|---|---|---|---|
| 1 | (a) | n_P < 8 ya da n_N < 20 | "ölçü sınanamadı (Parkfield verisi yok)" | indirilmez |
| 2 | (b) | Z3 (i)–(iv) hepsi | "ölçü sınandı" (+ (b′) "belirsiz" etiketi varsa) | **açılır** (TR-7b §7) |
| 3 | (c) | (i), (ii) var; modülasyon ≥ 3 P olayında ölçülebilir; (iii) ya da (iv) yok | "ölçü sınanamadı (algılayıcı kör olaylarda tetiklenmiş tremoru tetikleyici genliğinden ayıramadı)" | indirilmez |
| 4 | (d) | (i) ya da (ii) yok; MDA tanımlı; A90_PK ≤ 100 µm/s | "ölçü sınanamadı (kör Parkfield olaylarında tetiklenmiş tremor ölçütü karşılamadı: X_P = [..] / n_P = [..]; A90_PK = [..] nm/s)" | indirilmez |
| 5 | (e) | öteki; modülasyon < 3 P olayında ölçülebilir | "ölçü sınanamadı (yöntem)" / "ölçü sınanamadı (modülasyon ölçülemedi)" | indirilmez |

- **(b′) etiketi** (TR-7b §6.4 aynen): Algılama veren P olaylarının hepsinde bütün algılama kümeleri TR-7 §7.2 (b′) (i)
  ya da (ii) durumundaysa (çekirdek fazları olay başına iasp91 ile), "geçti, belirsiz" yazılır. Etkisi TR-7 (b′) aynen:
  Marmara açılır, "VAR" verilemez, her "görülmedi" cümlesine "(K1c yalnız belirsiz geçti)" eklenir.
- **Uygulama hatası yolu:** TR-7 §7.2 aynen, bir kez; yalnız (d) ya da (e) dalında. Tanım, eşik, pencere, liste ve
  sızıntı kuralı değişmez. Yazarın seçimi: (c) dalında bu yol **yoktur**. Gerekçe: (c), algılayıcının kör olaylarda
  çalıştığını ama ayırmadığını söyler; bir "hata düzeltmesi" orada sonuca bakarak kural seçmeye dönüşür.
- **Ek bilgi satırları** (yazarın seçimi; dalları değiştirmez):
  - N 28 çıkarılmış Z3 (iii) (§3.2);
  - olay başına algılama, küme sayısı, atılma nedenleri ve K5 bayrak sayıları;
  - N olaylarındaki algılama kümelerinin modülasyon p'leri (m_f'nin gerçek veride kaba bir göstergesi);
  - Tohoku duman satırı (§9).

### 6.2 Marmara taraması (yalnız K1c (b) ise)

TR-7b §7 aynen: TR-7'nin Marmara tarafı (birimler, K0 ve bant, önsayım, pencereler, işleme zinciri, K2 negatif kontrol,
MDA, kestirici, §8 hüküm kuralları, X_min tabloları, kuyruk eşikleri, kalıplar, çıktı tabloları, tek koşu) değişmez.
Yalnız §6.5 madde 3 K5'tir. Segment hükümleri TR-7 §8 sırasıyladır: "veri yok", "ölçü güvenilmez (…)", "tetiklenmiş
tremor VAR", "aday, doğrulanmadı", "görülmedi". "VAR" ancak şu üçü birlikte varsa verilebilir: K1c (b) "belirsiz" değil,
"Parkfield modülasyonu geçti" (§5 madde 5) ve TR-7 §8 sıra 5'in öteki şartları.

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

**Boş tarama ne söyler.** Boş bir tarama ("görülmedi") **yalnız A90(S_k)/A_PK ≤ 1 olan segmentte** Parkfield türü bir
kaynak hakkında bir şey söyler. A90(S_k)/A_PK > 1 olan segmentte yalnız "A90(S_k)'nın üstündeki tremor yok" der ve Z6
eki zorunludur. Kentsel gürültüde gerçek s_Marmara, ŝ_Parkfield'dan küçük olacaktır. (1 − ŝ)^n bu yüzden bir alt
sınır değil, Parkfield koşullarında bir ölçektir. TR-7 §7.5 bu oranı yalnız bilgi satırı olarak yazıyordu; TR-7c'de
cümlenin şartıdır.

**Yazarın seçimleri (Z6 cümlesindeki köşeli yerlerin tanımı):**
- **A_PK:** Algılama veren her P olayında TR-7 §7.5 kestiricisiyle a (25 km'ye indirgenmiş, istasyon medyanı; olayda
  birden çok algılama kümesi varsa en büyüğü). A_PK, bu olay değerlerinin medyanıdır. X_P = 0 ise A_PK tanımsızdır,
  ama o durumda dal (b) zaten işlemez.
- **ŝ:** INCELEME-0 §2 modelindeki p_P = 1 − (1 − s)(1 − q) bağıntısından,
  ŝ = max(0, (X_P/n_P − X_N/n_N) / (1 − X_N/n_N)). Yani P'deki algılama oranı, N'de ölçülen tetikleyicili yanlış alarm
  payından arındırılır. X_P/n_P de bilgi olarak yazılır. Gerekçe: ham X_P/n_P yanlış alarmı içerir, s'yi büyütür ve
  (1 − ŝ)^n'i iyimser yapar. Arındırılmış değer tutucudur.
- **n:** TR-7 §8'deki segmentin n'si (K0-tam ana birim).

Ölçek için (1 − s)^n (INCELEME-0 §4; `tr7c_guc.json` `marmara_bos_olasiligi`):

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
n_N = 30. m_t, gerçek tremor kümesinin modülasyondan (p ≤ 0,01) geçme olasılığıdır. m_f, sızıntı kümesinin geçme
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
| Ayırt etmeyen algılayıcı (her büyük tetikleyicide t 0,3–0,9 olasılıkla ateşler; r = 0,05) | ≤ 0,0002 |
| Genliğe bağlı sızıntı, v0 0,01 / 0,03 / 0,1 cm/s, m_f 0,05 | 0,010 / 0,006 / 0,001 |
| Aynı, m_f 0,10 | 0,062 / 0,040 / 0,004 |

Karşılaştırma: TR-7b §6.4 (b) (|N| = 2) ayırt etmeyen algılayıcıda 0,09–0,44; D30 (modülasyonsuz) genliğe bağlı
sızıntıda 0,36–0,99.

### 7.3 Olay sayısına duyarlılık (s 0,7, q 0,1; `D30M3_olay_sayisi`)

| n_P | n_N = 30 | n_N = 20 | n_N = 10 |
|---|---|---|---|
| 10 | 0,95 / 0,73 | 0,93 / 0,72 | 0,85 / 0,67 |
| 8 | 0,88 / 0,56 | 0,86 / 0,55 | 0,77 / 0,51 |
| 6 | 0,71 / 0,34 | 0,67 / 0,33 | 0,62 / 0,31 |
| 5 | 0,58 / 0,23 | 0,56 / 0,22 | 0,50 / 0,21 |

Değerler "m_t 0,8 / m_t 0,5" biçimindedir. n_P < 8 ya da n_N < 20 dal (a)'dır. n_P = 8'de m_t 0,5 iken güç 0,56'ya düşer;
dal (a)'nın sınırı bu yüzden ancak m_t yüksekse yeterlidir (doğrulanamadı, §8).

### 7.4 ×0,5 / ×2 duyarlılığı

| | m_t 0,8 (s₀ ≈ 0,57) | m_t 0,5 (s₀ ≈ 0,77) |
|---|---|---|
| s ×0,5 | s ≈ 0,29: güç ≈ 0,2 (ızgarada s 0,3, q 0,1: 0,23) | s ≈ 0,39: güç ≈ 0,1–0,4 (ızgarada s 0,3–0,5: 0,12–0,42) |
| s ×2 | s ≥ 1: güç ≈ 1 (s 0,9: 1,00) | s ≥ 1: güç ≈ 0,9 (s 0,9: 0,90; tavanı m_t koyar) |
| q ×0,5 (0,05) | 0,95 (s 0,7) | 0,73 |
| q ×2 (0,2) | 0,86 (s 0,7) | 0,68 |

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
| D1 | **Uzun periyot başvuru istasyonu, 2001–2010** (Z3 (iv) bunsuz uygulanamaz) | INCELEME-0 §7: kör P olaylarında sayılmadı | Her P olayı için TR-7 §6.6 ölçütü (bant B ya da H, alet H, \|H(0,02 Hz)\|/\|H(1 Hz)\| ≥ 0,5) StationXML yanıtından, W ve R örtüsü ≥ %90 availability'den. İz köşe ortalamasına en yakın uygun istasyon olay başına yazılır | **Yazarın seçimi:** başvuru istasyonu olan P olayı 3'ten azsa TR-7c **dondurulmaz** ve kör koşu yapılmaz. Gerekçe: dal (e) önceden kesinleşmiş olur; kör olayları sonucu belli bir koşuda harcamak boşunadır. Kayda "modülasyon ölçülemez, kör olaylar harcanmadı" yazılır |
| D2 | **Modülasyon geçme olasılıkları m_t ve m_f** | Tohoku'da hiçbir küme ayıklamadan sağ çıkmadı; Peng 2009 gözlemi görsel; faz sürümünün sızıntı kümelerindeki yanlış oranı ölçülmedi | m_t: dalga formu olmadan ölçülemez; literatürden (Peng 2009 ve Ghosh 2009'un yayımlanmış şekilleri) yalnız nitel okuma. m_f: kod yalnız yapay veride (§10 adım 2) Y2 ve Y3 satırlarının sağ kalan sızıntı kümelerinde TR-7 §6.4 ölçüsüyle ölçülür (0 €, gerçek veri yok) | m_t doğrulanamadı olarak kalır; güç tablosu iki değerle (0,8 / 0,5) yazılı kalır. Yapay m_f > 0,10 çıkarsa bu, D30M3'ün yanlış kabul tavanının (≤ 0,06) geçerli olmadığı demektir. **Yazarın seçimi:** o durumda taslak bağımsız incelemeye geri döner; Z3 kendiliğinden değiştirilmez |
| D3 | **Chao 2012'de Q'yu belirleyen istasyonlar ve inceleme yöntemi** | Tam metin okunmadı | Chao 2012 tam metni ve Peng 2009 Ek Tablo S1–S2, açık ve yasal bir kaynakta varsa okunur (0 €). Yoksa doğrulanamadı kalır | Yalnız yorum değişir (Q'nun kuyu mu yüzey mi olduğu, s'nin anlamı). Olay listesi Z2'de sabittir, değişmez |
| D4 | **Kör olaylarda gerçek W örtüsü ve E1 maske payları** (n_P, n_N) | Availability gün dosyası düzeyinde; E1 hesaplanmadı | E1: ComCat M ≥ 6,0 katalog satırlarıyla, TR-7 §6.5.1a kuralıyla, olay başına K1b aralığının açık payı. Örtü: availability'den liste istasyonu sayısı | Kestirilen n_P < 8 ya da n_N < 20 ise dal (a) önceden belli olur. **Yazarın seçimi:** o durumda da dondurulmaz, kör koşu yapılmaz. Kayda "Parkfield verisi yok (üstveriden)" yazılır |
| D5 | **CI istasyonları** | EarthScope availability 404 verdi (SAYIM §5.2) | Aynı servis bir kez daha, belgelenmiş GET biçimiyle | Yalnız sayı (n_P, n_N) |
| D6 | **PGV → kPa dönüşümü** (G, β) | Varsayım | Yok (kuram). Z6 cümlesi "≈ 2 kPa" der; ölçek TR-7 §12 aynen | Değişmez |
| D7 | **Marmara A90** | Hiç ölçülmedi | Yok; ancak koşuda (dal (b) sonrası) ölçülür | – |
| D8 | **Ham yoklama günlükleri** (`/mnt/project-files/turetme/tr7b-ham/`) | INCELEME-0'da açılmadı; körlük beyanı yalnız betik koduna dayanıyor | Bağımsız kod incelemecisi günlükte W'ye düşen bir dataselect satırı olmadığını denetler (yalnız istek satırları; gövde yok) | W'ye düşen bir istek bulunursa §11'e yazılır, o olay için "kör değil" notu eklenir |
| D9 | **2009-10-07 çifti** (N 27, N 28) | W pencereleri örtüşüyor | E1 hesabında (D4) iki W'nin örtüşme payı yazılır | Yalnız §3.2'deki bilgi satırı |

**Yoklama sırası** (yazarın seçimi): D4 ve D1 önce yapılır. İkisinden biri dondurmayı engellerse ötekiler yapılmaz.

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

## 10. Koşu sırası

Tek koşu kuralı TR-7 §10.6 aynen, aşama adlarında K1 → K1c.

1. **Üstveri yoklaması** (§8; 0 €; dalga formu yok). D1 ya da D4 engellerse burada durulur, kör olaylar harcanmaz.
2. **Kod, yalnız yapay veride.** TR-7'nin KD'si (§7.1 D1–D15, bantlar aynen) ve TR-7b §11.2 satırları K5 ile koşulur.
   Bunlara Z3/Z4 dal mantığı için yapay sayılarla birim sınamaları ve mutasyonlar eklenir. Örnek mutasyonlar: Fisher
   yönü ters; (iv)'de "≥ 3" yerine "≥ 1"; dal (a) eşiği n_N < 2; (b) dışında Marmara indirme. D2'nin m_f ölçümü de bu
   adımdadır. KD bantlarından biri kalırsa kod düzeltilir; K5 ve eşikler değişmez. TR-7b §11.2 satırları yalnız bilgidir.
   Değerlerin Tur 2/3 değerleriyle tutarlılığı (Monte Carlo hatası içinde) kodun K5'i doğru çağırdığını gösterir; K5
   seçimini etkilemez.
3. **Tohoku duman sınaması** (§9, Z7). Yazarın seçimi: kod incelemesinden önce yapılır, böylece duman sonrası bir
   düzeltme varsa o da incelenir.
4. **Bağımsız kod incelemesi** (Z8, aynen): "TR-7b koşu kodu (K5 ile K1b) dondurulmadan önce bağımsız kod incelemesi
   gerekir. Gerekçe: K5 bu kodda ilk kez yapay ortam dışında çalışacak; Q referansı ve ρ gerçek maske parçalarıyla
   hesaplanacak." "Koşulabilir" hükmü gerekir. İnceleme D8'i de denetler.
5. **Dondurma.** Bu metin "Durum: DONDURULDU …" satırıyla commit ve push edilir. Kod, dondurulmuş metnin ve
   `tr7b_yapay2.py`'nin sha256'larını denetlemeden gerçek kipte çalışmaz (TR-13b §12.1 örneği; yazarın seçimi).
6. **Parkfield kör kontrolü, tek koşu.** Aşamalar: manifest → K1c-indirme (P, N ve rastgele negatifler) → K1c-negatif
   (rastgele negatifler: f_PK, N_PK, MDA) → K1c-algılama. Algılama aşamasında sıra (yazarın seçimi): önce 30 N olayı,
   sonra 10 P olayı. Z3 ve Z4 yalnız bütün olaylar bittikten sonra hesaplanır. Hüküm dosyası bir kez yazılır. Durum
   dosyası `kayit/turetme/tr7c/TR7C_KOSU_DURUM.json`, her aşamada commit ve push edilir.
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
  ayar yapılırsa zarar verir; §2 bu yolu kapatır. Yazar K5'in Tur 2 ve Tur 3 yapay sonuçlarını, INCELEME-0'ın güç
  hesabını ve Chao etiketleriyle PGV_T değerlerini biliyor. Algılayıcının bu 40 olaydaki çıktısını bilmiyor.

## 12. Bilinen zayıflıklar (INCELEME-0 §3–§4'ten; çözülmez, yazılır)

1. **İlişkili hatalar.** Chao/Peng etiketleri NCSN yüzey istasyonlarını da içeren aynı kayıtlardan çıktı. Görsel
   incelemeyi yanıltan bir sızıntı (ör. Kuril 2006'da artçı P'leri) algılayıcıyı da yanıltabilir ve uyumu şişirir.
2. **Yöntem benzerliği.** Etiket ile algılayıcı aynı şeye bakıyor: 2–8 Hz zarfın yüzey dalgasıyla eş zamanlılığına.
3. **Kirli negatif.** "Tetiklemedi" etiketi görsel incelemedir ve büyük ölçüde kuyu kayıtlarına dayanır. Daha duyarlı bir
   algılayıcı Q = 0 olaylarında gerçek zayıf tremor bulabilir. Bunun yönü yanlış rettir.
4. **Yüzey–kuyu farkı.** Ana sınıf yüzey ağıdır, Chao'nun büyük ölçüde kuyu/PKD. s düşer; yanlış ret yönündedir.
5. **Bağımsızlık.** Kuril 2006/2007, Macquarie/Sumatra 2004, 2009-10-07 çifti. Binom ve Fisher bağımsızlık varsayar.
6. **Aktarım.** Parkfield'da geçen bir kör kontrol yalnız şunu gösterir: kırsal, yoğun, yerel bir yüzey ağında,
   Parkfield–Cholame türü (20–25 km) ve ≈ 2 kPa'nın üstünde tetiklenen bir kaynağın tremoru bu algılayıcıyla s oranında
   yakalanır. Marmara'ya taşınmayanlar: kentsel ve durağan olmayan gürültü, KO'ya dayalı geometri, kaynağın varlığı ve
   derinliği, kaba τ'daki ×3 belirsizlik.
7. TR-7 §12'nin bütün maddeleri aynen geçerlidir.

## 13. İstanbul'a bağ

TR-7 §13 aynen. Mutlak olasılık ya da olasılık çarpanı yazılmaz; sonuç bir olasılık terimi değildir. Marmara sonucunun
anlamı yalnız TR-7 §13'ün iki cümlesinden biridir: "dinamik gerilmeye duyarlı derin kayma bölgesi gözlendi" ya da "bu
duyarlılıkla (A90, kaba τ, n) gözlenmedi". TR-7c bunlara Z6'nın A90(S_k)/A_PK şartını ekler. Z6 cümlesindeki
(1 − ŝ)^n, Parkfield türü bir kaynağın bu taramada görülmeme olasılığıdır. İstanbul'da deprem olasılığı hakkında hiçbir
şey söylemez. K1c (b) dışında Marmara hakkında hiçbir cümle kurulmaz.

## 14. İnceleme eşleme tablosu (`TR-7c_INCELEME-0.md` §6)

| Madde | İçerik | Bu metinde nerede | Biçim |
|---|---|---|---|
| Z1 | Sapma ve körlük beyanı | §2 (aynen), §11 | alıntı aynen; §2 sonunda kapatılan yollar (yazarın seçimi), §4.2 uygulama (yazarın seçimi) |
| Z2 | Olay listesi; n_P, n_N tanımı; E1 katalogdan; rastgele negatifler | §3 (aynen), §3.1–§3.2 tablolar | alıntı aynen; N 27/28 bilgi satırı yazarın seçimi |
| Z3 | Başarı ölçütü D30M3 | §5 (aynen) | alıntı aynen; Fisher biçimi, N_PK < 5, "ölçülebilir" tanımı yazarın seçimi |
| Z4 | Dallar ve sırası; bilgi satırları | §6.1 (aynen) | alıntı aynen; "K1c" adı, (c)'de uygulama hatası yolunun olmaması ve ek bilgi satırları yazarın seçimi |
| Z5 | Görülebilir en küçük etki, kaynak, ×0,5 / ×2 | §7 (aynen), §7.1–§7.4 | alıntı aynen; tablolar `tr7c_guc.json`'dan |
| Z6 | Marmara "görülmedi" cümlesi ve A90/A_PK eki | §6.2 (aynen), §13 | alıntı aynen; A_PK ve ŝ tanımları yazarın seçimi |
| Z7 | Tohoku duman sınaması, dal değiştirmez | §9 (aynen), §10 adım 3 | alıntı aynen; yer ve kapsam yazarın seçimi |
| Z8 | Dondurmadan önce bağımsız kod incelemesi | §10 adım 4 (aynen) | aynen; D8 denetimi eklendi |
| §7 doğrulanamayanlar | ham günlükler, Chao istasyonları, m_t/m_f, başvuru istasyonu, PGV→kPa, örtü/E1, Marmara A90 | §8 D1–D8 | her biri için 0 € yoklama |

## 15. Bu taslakta açık kalanlar (dondurmadan önce kapanmalı)

- §8'in yoklamaları yapılmadı (D1–D5, D8, D9).
- Koşu kodu yazılmadı; yapay sınamalar, mutasyonlar ve m_f ölçümü yok.
- Tohoku duman sınaması yapılmadı.
- Yazarın sınav öncesi beklentisi (TR-7 §11 ve TR-7b §10 biçiminde) dondurma sürümünde, kör koşudan önce yazılır.
- "Yazarın seçimi" işaretli maddeler bağımsız kod incelemesinde ya da ayrı bir metin incelemesinde onaylanmadı.
