# TR-7c ÜSTVERİ: dondurmadan önceki 0 € yoklama (ön kayıt §8 D4 ve D1; D5 ve D9 bilgi)

Tarih: 17 Kasım 2026 (koşu 19:24 UTC). Durum: **yoklama tamam; kural sonucu: DONDURULABİLİR (üstveri kapısı geçti).**

- Ön kayıt: `TR-7c_tetiklenmis-tremor_ONKAYIT.md` sürüm 2 (commit 41d2ff5). Kural yoklamadan önce orada yazılıydı.
- Betik: `kayit/turetme/tr7c/ustveri/tr7c_ustveri.py`. Kuralın işlemsel tanımı betik başlığındadır ve betik ilk koşudan
  önce commit edildi (22871d8). Son hâlinin sha256'sı `e0577855…bd92`.
- Çıktı: `kayit/turetme/tr7c/ustveri/tr7c_ustveri.json` (sha256 `ed8cf3c6…ad8c`).
- Ham yanıtlar depo dışında: `/mnt/project-files/turetme/tr7c-ustveri-ham/` (184 dosya, 2,2 MB). Günlük
  `tr7c_ustveri_gunluk.jsonl` (sha256 `b1f2d2e3…f33c`).
- Maliyet 0 €.

## Körlük beyanı

- **Hiçbir dataselect isteği yapılmadı** (günlükte 0; betik `dataselect` içeren URL'yi `assert` ile reddeder). Hiçbir
  dalga formu indirilmedi ya da açılmadı. Kör olayların ne W'sinde ne R'sinde içerik istendi.
- **İstenenler:** USGS ComCat fdsnws/event (M ≥ 6,0 katalog satırları); NCEDC, EarthScope ve SCEDC fdsnws/station
  (`level=response`, StationXML); NCEDC, EarthScope ve SCEDC fdsnws/availability (yalnız zaman aralıkları).
- Bütün sorgular ≤ 2025-12-31'dir; olaylar 2001–2010 arasındadır. Marmara'ya hiçbir sorgu yapılmadı.
- Genel bir User-Agent kullanıldı (`fdsn-client/1.0 (python-urllib)`). Kişisel ya da proje bilgisi gönderilmedi.
- Son koşuda HTTP sonuçları: 200 × 183, 204 × 1 (NC.PAGB BHZ yanıtı), 404 × 74 (EarthScope'un CI availability'si). 401,
  403 ya da 429 gelmedi.
- **Açıklık notu:** Betik üç kez çalıştı.
  1. Birinci koşu yol hatasıyla, istek yapmadan durdu.
  2. İkinci koşu ComCat, StationXML ve availability isteklerinden sonra durdu: SCEDC availability yanıtındaki boş
     Quality sütunu ayrıştırıcıyı bozdu. O ana kadar ekrana olay başına liste sayısı, K1b açık payı ve tetikleyici
     kaydı yazıldı (bu belgedeki değerlerle aynı). Ayrıştırıcı düzeltildi.
  3. Üçüncü koşuya bilgi satırı k_3 eklendi; o koşu tam sonuçtur. k_3 ikinci koşunun başlığında vardı ama
     uygulanmamıştı. Başlıktaki "yüzey_diger sınıfıyla k" bilgi satırı kapsamdan çıkarıldı.

  Karar kuralına, eşiklere ya da aday listesine dokunulmadı. İkinci koşunun günlüğü bellekteydi, yazılamadı; ham
  dosyaları üçüncü koşu aynı adlarla yeniden yazdı.

## 1. Kural (ön kayıt sürüm 2'den; yoklamadan önce yazılı)

- **D1, D-5 (aynen):** "Başvuru istasyonu olan (TR-7 §6.6; W ve R örtüsü ≥ %90) P olayı sayısı k < 7 ise TR-7c
  dondurulmaz ve kör koşu yapılmaz; …"
- **D4 (yazarın seçimi, sürüm 2 §8):** kestirilen n_P < 8 ya da n_N < 20 ise dondurulmaz, kör koşu yapılmaz.
- **n_P ve n_N (Z2):** ≥ 3 liste istasyonu "var" olan ve K1b aralığının E1 maskesinden sonra ≥ %50'si açık olan P olayı
  ya da N birimi sayısı. N birimleri D-1'e göre sayılır: N 27 ile N 28 "Vanuatu 2009 birimi"dir, n_N en çok 29'dur.

**İşlemsel tanım** (betik başlığı):
- **Liste sayısı:** TR-7b_SAYIM'ın availability sayımı (seçili düşey kanalda W ve R örtüsü ≥ 0,90). Vanuatu biriminde
  iki olayın küçüğü alınır.
- **E1:** TR-7 §6.5.1a aynen.
  - ComCat [R başı − 3 sa, W sonu], M ≥ 6,0.
  - Tetikleyici çıkarılır: T0'a ±60 sn içinde M ≥ 7,0 olan en yakın kayıt, ayrıca ±5 sn ikiz kayıt kuralı.
  - iasp91, olay derinliği, iz köşe ortalaması.
  - M ≥ 7,0 için P ve S [−10, +240] sn; 6,0 ≤ M < 7,0 için yalnız P [−10, +60] sn.
  - Vanuatu biriminde tetikleyici yalnız N 27'dir; N 28 "öteki olay" olarak maskelenir.
- **Başvuru istasyonu:**
  - Liste sınıfı istasyonun bant B ya da H, alet H olan bir düşey kanalı.
  - StationXML yanıtında, olay anındaki epokta |H(0,02 Hz)| / |H(1 Hz)| ≥ 0,5 (obspy 1.5.1 evalresp, hız).
  - W ve R örtüsü ≥ 0,90. CI kanallarında örtü yeniden sorgulandı (D5): EarthScope, olmazsa SCEDC.
  - Başvuru istasyonu iz köşe ortalamasına en yakın uygun istasyondur.

## 2. Sonuç

| Nicelik | Değer | Eşik | Durum |
|---|---|---|---|
| k (başvuru istasyonlu P olayı) | **10 / 10** | k ≥ 7 | geçti |
| n_P (kestirilen) | **10 / 10** | ≥ 8 | geçti |
| n_N (kestirilen, N birimi) | **29 / 29** | ≥ 20 | geçti |

**Kuralın verdiği dal: DONDURULABİLİR (üstveri kapısı geçti).** Bu bir dondurma değildir; dondurmayı koordinatör yapar
(D-3: önce karar metni dondurması).

D-5 gereği k ile hesaplanan görülebilir en küçük s: k = 10, n_P = 10, n_N = 29, q 0,1 → **s ≈ 0,58 (m_t 0,8) / 0,77
(m_t 0,5)** (`tr7c_inc1.json` `esik.MDE_tablosu_q0.1`, nP10_nN29).

**Bilgi satırları (karara girmez):**
- k'nin n_P'ye giren olaylarla sınırlı hâli: 10.
- **k_3 = 10:** Başvuru istasyonunun aynı bantta iki yatay kanalı da W ve R'de ≥ 0,90. Peru 2001 ve Colima 2003'te
  yalnız BH bandında.
- D-9'un 4 genliği eşlenmiş N olayının (Macquarie 2004, Nias 2005, Solomon 2007, Peru 2007) dördünde de başvuru
  istasyonu var (BK.PKD, BHZ).

### 2.1 Başvuru istasyonu (D1)

| Olay | Başvuru (iz ortasına km) | Uygun istasyonlar | PKD BHZ oran |
|---|---|---|---|
| Peru 2001 | BK.PKD BHZ (8,0) | BK.PKD | 1,012 |
| Denali 2002 | BK.PKD BHZ (8,0) | BK.PKD | 1,012 |
| Colima 2003 | BK.PKD BHZ (8,0) | BK.PKD | 1,012 |
| Tokachi-oki 2003 | BK.PKD BHZ (8,0) | BK.PKD | 1,012 |
| Sumatra 2004 | BK.PKD BHZ (8,0) | BK.PKD, BK.RAMR, NC.PAGB, NC.PMPB | 1,001 |
| Kuril 2006 | BK.PKD BHZ (8,0) | aynı 4 | 1,001 |
| Kuril 2007 | BK.PKD BHZ (8,0) | aynı 4 | 1,001 |
| Wenchuan 2008 | BK.PKD BHZ (8,0) | aynı 4 | 1,001 |
| Samoa 2009 | BK.PKD BHZ (8,0) | 9 (BK.PKD, BK.RAMR, CI.CAR, CI.PHL, CI.SMM, CI.SMR, NC.BBGB, NC.PAGB, NC.PMPB) | 1,001 |
| Maule 2010 | BK.PKD BHZ (8,0) | aynı 9 | 1,001 |

**Okuma ve risk.** 2001–2003'ün dört P olayında modülasyon ölçüsü **tek istasyona (BK.PKD) bağlıdır**. Bu istasyonun
o pencerede gerçek örtüsü düşükse ya da kanal bozuksa, bu olaylarda modülasyon "ölçülemedi" olur. k 10'dan 6'ya inerse
dal (e) olasılığı artar (ön kayıt §7.3 k tablosu: k = 6'da güç 0,75 / 0,35). Availability yanıtları gün dosyası düzeyindedir; PKD'nin W içi boşlukları bu
yoklamayla görülemez (**doğrulanamadı**). Koşu bunu TR-7 §4.2'nin gerçek örtüsüyle yeniden belirler.

**CI istasyonları (D5).** EarthScope availability CI kanallarının hepsinde yine 404 verdi. SCEDC availability 200
döndü. Yalnız 2009–2010'da (Samoa, Maule) W ve R'yi kapsayan aralık var; 2001–2008 olaylarında CI kanallarının örtüsü
0'dır. SCEDC yanıtı "extent" biçimindedir (TimeSpans "NA"). İçerdeki boşluklar görülmez; örtü bir üst sınırdır.

### 2.2 E1 ve K1b açık payı (D4)

Bütün birimlerde liste sınıfında 34–52 istasyon "var". K1b aralığının açık payı 1,00 olmayan birimler:

| Birim | K1b aralığı (UTC) | K1b açık pay | Maskelenen varış (W ± 3 sa) |
|---|---|---|---|
| P Sumatra 2004 | 01:50:29–02:18:00 | 0,958 | 4 (M 6,x P) |
| P Kuril 2006 | 11:39:23–11:52:48 | 0,729 | 5 (M 6,x P; artçılar) |
| P Maule 2010 | 07:08:14–07:26:23 | 0,936 | 4 |
| N 2006-07-17 (Java) | 09:11:27–09:39:11 | 0,958 | 1 |
| N Solomon 2007 | 21:15:48–21:34:55 | 0,878 | 4 |
| N 2009-01-03 | 20:25:36–20:47:53 | 0,948 | 1 |
| N Vanuatu 2009 birimi | 22:37:13–23:10:50 | 0,841 | 6: N 28 (M 7,8) P 22:31:18, S 22:40:04; M 7,4 P 23:26:17, S 23:35:02; 2 M 6,x |

Öteki 32 birimde K1b aralığı tümüyle açıktır.

**Tetikleyicinin ComCat kaydı:** Bütün birimlerde bulundu. Sapma çoğunda 0,0 sn; Wenchuan 2008'de 0,57 sn, 2009-08-10'da
3,12 sn, 2010-06-12'de 0,01 sn.

**Vanuatu birimi.**
- INCELEME-1'in kaba varış kestirimleri iasp91 ile 1–2 dk içinde doğrulandı: N 28'in S'si 22:40:04 (kaba kestirim
  22:41:40). INCELEME-1 §11'deki "doğrulanamadı" maddesi bu yoklamayla kısmen kapandı.
- Varış birleşik birimin K1b aralığına düşer ve maskelenir.
- M 7,4'ün varışları W sonundan (23:24:32) sonradır; W'yi etkilemez.

## 3. Doğrulanamayanlar (bu yoklamadan sonra da açık)

- **W içi gerçek örtü.** NCEDC availability gün dosyası düzeyindedir, SCEDC'ninki extent düzeyindedir. %90 örtü yalnız bu
  yanıtlara dayanır. Koşu TR-7 §4.2 ile gerçek örtüyü yeniden sayar; n_P ya da n_N düşerse (a) dalı orada da işler.
- **PKD'nin 2001–2003'teki tek başına yükü.** Bkz. §2.1.
- **Seçilen kanalın TR-7 kodundaki karşılığı.** TR-7 kodu PGV uygunluğunu istasyonun tek bir `z_kanal`ı üzerinden
  değerlendirir. Bu yoklama herhangi bir uygun düşey kanalı yeterli saydı (yazarın seçimi). PKD'de BHZ ve HHZ ikisi de
  uygun (oran 1,00 ve 0,98). 2001 ve 2003'te HHZ'nin örtüsü 0 olduğundan uygun kanal BHZ'dir.
- m_t, m_f, Chao'nun istasyonları (D2, D3): bu yoklamanın kapsamı dışında. Durumları ön kayıt §8'deki gibi.
- Ham yoklama günlükleri (D8): bu yoklama TR-7b'nin ham günlüklerini açmadı.
