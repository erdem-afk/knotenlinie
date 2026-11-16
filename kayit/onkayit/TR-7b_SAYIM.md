# TR-7b SAYIM: Parkfield'de kör pozitif kontrol için 0 € veri varlığı kapısı

Tarih: 16 Kasım 2026. Durum: **sayım tamam; kapı GEÇTİ (aşağıdaki sınırlamalarla)**. Bu belge TR-7'nin §14 (d) yeniden
açma şartının ilk adımıdır; TR-7b ön kayıt taslağı `TR-7b_tetiklenmis-tremor_ONKAYIT.md`.
Kod: `kayit/turetme/tr7b/tr7b_sayim.py` (sha256 b173309a…f61b), çıktı `kayit/turetme/tr7b/tr7b_sayim.json`
(sha256 55318360…5114). Yoklama günlükleri ve sorgu yanıtları depo dışında `/mnt/project-files/turetme/tr7b-ham/`
(131 dosya, 15 MB; günlük `tr7b_sayim_gunluk.jsonl` sha256 e5c86bc1…3c0c). Maliyet 0 €.

**Körlük beyanı.** Hiçbir pozitif ya da negatif kontrol olayının W penceresinde dalga formu istenmedi. İstenenler:
fdsnws/station (üstveri), fdsnws/availability (yalnız zaman aralıkları) ve olay başına sınıf başına bir 10 sn'lik
dataselect isteği **R ortasında (T0 − 30 dk, olaydan önce)**; bu isteklerde yalnız HTTP kodu ve bayt sayıldı, içerik
çözülmedi, diske yazılmadı. Tohoku 2011 geliştirme verisidir (TR-7'de işlendi). Marmara kutusuna hiçbir sorgu yapılmadı.
Bütün olaylar ≤ 2011-03-11.

## 1. Literatür: hangi olaylarda Parkfield–Cholame'de tetiklenme bildirildi

| Kaynak | Ne doğrulandı | Düzey |
|---|---|---|
| Chao vd. 2012, BSSA, 10.1785/0120110151, Ek Tablo S1 (`chao2012_TableS1.txt`, sha256 42b5c8d1…f177; seismosoc.org esupp, açık) | 2001–2010 arası 42 Mw ≥ 7,5 olay; Orta Kaliforniya (CC) için Q = 1 (tetikledi) / 0; PKD (Tokachi'de FROB, Tonga'da PROB) PGV_Z, PGV_T. **12 olay Q = 1**, 30 olay Q = 0 | makine okunur tablo; özet "12 earthquakes" ile tutarlı |
| Peng vd. 2009, JGR, 10.1029/2008jb006049 (tam metin, yazar sayfasındaki PDF'ten pdftotext) | 2001–2008 31 olay, 10'u tetikledi: Peru 2001, Kunlun 2001, Denali 2002, Colima 2003, Tokachi-oki 2003, Sumatra 2004, Tonga 2006, Kuril 2006, Kuril 2007, Wenchuan 2008. Chao 2012'nin 2008-05-12'ye kadarki 31 satırı ve Q = 1 olan 10'u bununla birebir aynı. Tetiklemeyen ve adı geçen: Macquarie 2004 (PGV_T yüksek ama tremor yok), Solomon 2007, Peru 2007, G. Sumatra 2007 (Gomberg vd. 2008b atfıyla). Zayıf: Kunlun ve Tonga yalnız kaynağa yakın istasyonlarda görüldü. Kuril 2006 tremoru artçıların telesismik P'leriyle karıştı | tam metinden. Ek Tablo S1–S2 (aux) okunmadı |
| Peng vd. 2008, GRL, 10.1029/2008gl036080 | Denali 2002, 2–8 Hz, birçok istasyonda tutarlı zarf, Love ile | özetten |
| Ghosh vd. 2009, JGR, 10.1029/2008jb006062 | Sumatra 2004, en zengin örnek, Love ile, bazıları P ile | özetten |
| Peng vd. 2010, GRL, 10.1029/2010gl045462 | Maule 2010, Parkfield–Cholame'de çok sayıda patlama; Coso'nun bölgesel tetiklenmiş depremleri düşük frekansta tremoru kısmen örtüyor | özetten |
| Hill vd. 2013, BSSA, 10.1785/0120120114 | Tohoku 2011 (geliştirme verisi) | özetten (TR-7 §2) |
| Hutchison ve Poli 2021, EGU özeti, 10.5194/egusphere-egu21-12141 | 2001–2020, M > 7 genişletilmiş katalog var | **olay listesi doğrulanamadı** (yalnız özet) |
| Shelly vd. 2011, 10.1038/ngeo1141 | gecikmeli tetiklenme (Parkfield) | özet yok, okunmadı |

2011–2025 arası (Tohoku dışında) hiçbir olay için Parkfield'da tetiklenme var/yok yayımlanmış bir olay listesi
doğrulanamadı; bu yüzden aday küme 2001–2010 ile sınırlıdır. "YOK" işareti, yazarların görsel incelemesinde (PKD ve
NCSN/HRSN) tremor görülmemesi demektir; daha duyarlı bir yöntemde tremorun bulunmayacağı anlamına gelmez (§4).

## 2. Sayım kuralı (betikte)

Pencereler TR-7 §5 ile, iz köşe ortalamasına (35,9125° K, 120,4625° B) Δ ile: W = [T0 + Δ/5,0, T0 + Δ/2,8 + 600 s],
R = [T0 − 3600, T0). Kanal seçimi TR-7 §3.2 kutusu ve kuralıyla (düşey, alet H/P, ≥ 20 Hz, M/S, ize ≤ 50 km), NCEDC
ve EarthScope station servislerinin birleşimi. İstasyon "var" = en az bir düşey kanalında availability'e göre W örtüsü
≥ 0,90 **ve** R örtüsü ≥ 0,90. Sınıflar: **liste** = TR-7'nin 56 istasyonluk Parkfield yüzey listesi; **kuyu** = BP (HRSN)
ve PB; **diğer yüzey** (bilgi). Kapı: ≥ 2 pozitif (Q_CC = 1, Tohoku hariç) ve ≥ 1 negatif (Q_CC = 0) olay, her biri
**aynı sınıfta** ≥ 3 "var" istasyonla.

HTTP: 258 istek (NCEDC station 43, availability 43, dataselect 86 — hepsi 200; EarthScope station 43 — 200;
EarthScope availability 43 — hepsi 404). 429/503 gelmedi.

## 3. Aday olay tablosu

"liste" ve "kuyu" sütunları: "var" istasyon / üstveride bulunan istasyon. Yoklama: liste / kuyu sınıfında ize en yakın
"var" istasyonun R ortası 10 sn isteğinin HTTP kodu. PGV_T: Chao 2012 Tablo S1, PKD (cm/s).

| T0 (UTC) | Olay | Mw | Δ (km) | PGV_T | Tetiklenme (CC) | Kaynak | liste | kuyu | yoklama |
|---|---|---|---|---|---|---|---|---|---|
| 2001-06-23 20:33 | Peru 2001 | 8,4 | 7608 | 0,0639 | VAR | Chao12; Peng09 (tam metin §5.5) | 38/43 | 7/7 | 200/200 |
| 2001-07-07 09:38 | 2001 M7.60 (-17.5, -72.1) | 7,6 | 7824 | 0,0062 | YOK | Chao12 | 38/43 | 7/7 | 200/200 |
| 2001-10-19 03:28 | 2001 M7.50 (-4.1, 123.9) | 7,5 | 12570 | 0,0021 | YOK | Chao12 | 38/43 | 13/13 | 200/200 |
| 2001-11-14 09:26 | Kunlun 2001 | 7,8 | 11406 | 0,0170 | VAR | Chao12; Peng09 (tam metin §5.9; zayıf, yalnız kaynağa yakın istasyonlarda) | 38/43 | 11/13 | 200/200 |
| 2002-03-05 21:16 | 2002 M7.50 (6.0, 124.2) | 7,5 | 11832 | 0,0024 | YOK | Chao12 | 38/43 | 12/13 | 200/200 |
| 2002-09-08 18:44 | 2002 M7.60 (-3.3, 142.9) | 7,6 | 10816 | 0,0086 | YOK | Chao12 | 38/43 | 13/13 | 200/200 |
| 2002-10-10 10:50 | 2002 M7.60 (-1.8, 134.3) | 7,6 | 11491 | 0,0094 | YOK | Chao12 | 38/43 | 11/13 | 200/200 |
| 2002-11-03 22:12 | Denali 2002 | 7,9 | 3573 | 0,4960 | VAR | Chao12; Peng08 (özet); Peng09 (tam metin §5.1) | 38/43 | 13/13 | 200/200 |
| 2003-01-22 02:06 | Colima 2003 | 7,6 | 2491 | 0,0739 | VAR | Chao12; Peng09 (tam metin §5.4) | 38/43 | 13/13 | 200/200 |
| 2003-07-15 20:27 | 2003 M7.60 (-2.6, 68.4) | 7,6 | 16200 | 0,0076 | YOK | Chao12 | 34/43 | 13/13 | 200/200 |
| 2003-08-04 04:37 | 2003 M7.60 (-60.5, -43.4) | 7,6 | 12779 | 0,0098 | YOK | Chao12 | 41/43 | 12/13 | 200/200 |
| 2003-09-25 19:50 | Tokachi-oki 2003 | 8,3 | 7852 | 0,0324 | VAR | Chao12; Peng09 (tam metin §5.8) | 41/43 | 13/13 | 200/200 |
| 2003-11-17 06:43 | 2003 M7.80 (51.1, 178.7) | 7,8 | 5032 | 0,0091 | YOK | Chao12 | 40/43 | 12/13 | 200/200 |
| 2004-11-11 21:26 | 2004 M7.50 (-8.2, 124.9) | 7,5 | 12754 | 0,0101 | YOK | Chao12 | 41/51 | 13/13 | 200/200 |
| 2004-12-23 14:59 | 2004 M8.10 (-49.3, 161.3) | 8,1 | 12196 | 0,0615 | YOK | Chao12 | 41/52 | 13/13 | 200/200 |
| 2004-12-26 00:58 | Sumatra 2004 | 9,0 | 14242 | 0,0870 | VAR | Chao12; Ghosh09 (özet); Peng09 (tam metin §5.3) | 49/52 | 13/13 | 200/200 |
| 2005-03-28 16:09 | 2005 M8.60 (2.1, 97.1) | 8,6 | 14270 | 0,0217 | YOK | Chao12 | 50/52 | 13/13 | 200/200 |
| 2005-09-09 07:26 | 2005 M7.70 (-4.5, 153.5) | 7,7 | 9950 | 0,0024 | YOK | Chao12 | 50/52 | 13/13 | 200/200 |
| 2005-10-08 03:50 | 2005 M7.60 (34.5, 73.6) | 7,6 | 12047 | 0,0128 | YOK | Chao12 | 50/52 | 13/13 | 200/200 |
| 2006-04-20 23:25 | 2006 M7.60 (60.9, 167.1) | 7,6 | 5654 | 0,0199 | YOK | Chao12 | 50/53 | 12/12 | 200/200 |
| 2006-05-03 15:26 | Tonga 2006 | 8,0 | 8411 | 0,0133 | VAR | Chao12; Peng09 (tam metin §5.10; zayıf) | 50/53 | 12/12 | 200/200 |
| 2006-07-17 08:19 | 2006 M7.70 (-9.3, 107.4) | 7,7 | 14355 | 0,0013 | YOK | Chao12 | 50/53 | 13/13 | 200/200 |
| 2006-11-15 11:14 | Kuril 2006 | 8,3 | 6946 | 0,0767 | VAR | Chao12; Peng09 (tam metin §5.6; artçı P dalgalarıyla karışık, konumlanamadı) | 50/53 | 13/18 | 200/200 |
| 2007-01-13 04:23 | Kuril 2007 | 8,1 | 6873 | 0,1440 | VAR | Chao12; Peng09 (tam metin §5.2) | 50/53 | 13/18 | 200/200 |
| 2007-01-21 11:27 | 2007 M7.50 (1.1, 126.3) | 7,5 | 12008 | 0,0079 | YOK | Chao12 | 50/53 | 13/18 | 200/200 |
| 2007-04-01 20:39 | Solomon 2007 | 8,1 | 9891 | 0,0254 | YOK | Chao12; Peng09 (tam metin, Gomberg vd. 2008b atfıyla: tetiklemedi) | 50/53 | 13/18 | 200/200 |
| 2007-08-15 23:40 | Peru 2007 | 8,0 | 7159 | 0,0272 | YOK | Chao12; Peng09 (tam metin, Gomberg vd. 2008b atfıyla: tetiklemedi) | 51/54 | 12/18 | 200/200 |
| 2007-09-12 11:10 | G. Sumatra 2007 | 8,4 | 14491 | 0,0190 | YOK | Chao12; Peng09 (tam metin, Gomberg vd. 2008b atfıyla: tetiklemedi) | 49/54 | 13/20 | 200/200 |
| 2007-09-12 23:49 | 2007 M7.90 (-2.6, 100.8) | 7,9 | 14388 | 0,0186 | YOK | Chao12 | 50/54 | 13/20 | 200/200 |
| 2007-11-14 15:40 | 2007 M7.70 (-22.2, -69.9) | 7,7 | 8371 | 0,0139 | YOK | Chao12 | 51/54 | 13/21 | 200/200 |
| 2008-05-12 06:28 | Wenchuan 2008 | 7,9 | 11284 | 0,0418 | VAR | Chao12; Peng09 (tam metin §5.7) | 51/54 | 12/21 | 200/200 |
| 2009-01-03 19:43 | 2009 M7.70 (-0.4, 132.9) | 7,7 | 11528 | 0,0074 | YOK | Chao12 | 51/56 | 12/21 | 200/200 |
| 2009-03-19 18:17 | 2009 M7.60 (-23.0, -174.7) | 7,6 | 8683 | 0,0095 | YOK | Chao12 | 49/56 | 11/21 | 200/200 |
| 2009-07-15 09:22 | 2009 M7.80 (-45.8, 166.6) | 7,8 | 11649 | 0,0130 | YOK | Chao12 | 51/56 | 11/21 | 200/200 |
| 2009-08-10 19:55 | 2009 M7.50 (14.1, 92.9) | 7,5 | 13442 | 0,0035 | YOK | Chao12 | 51/56 | 12/21 | 200/200 |
| 2009-09-29 17:48 | Samoa 2009 | 8,1 | 7880 | 0,0288 | VAR | Chao12; Chao12 (yalnız Q) | 52/56 | 12/21 | 200/200 |
| 2009-09-30 10:16 | 2009 M7.50 (-0.7, 99.9) | 7,5 | 14307 | 0,0029 | YOK | Chao12 | 46/56 | 12/21 | 200/200 |
| 2009-10-07 22:03 | 2009 M7.70 (-13.0, 166.5) | 7,7 | 9380 | 0,0095 | YOK | Chao12 | 52/56 | 12/21 | 200/200 |
| 2009-10-07 22:18 | 2009 M7.80 (-12.5, 166.4) | 7,8 | 9357 | 0,0095 | YOK | Chao12 | 52/56 | 12/21 | 200/200 |
| 2010-02-27 06:34 | Maule 2010 | 8,8 | 9397 | 0,1390 | VAR | Chao12; Peng10 (özet) | 45/56 | 10/21 | 200/200 |
| 2010-04-06 22:15 | 2010 M7.80 (2.4, 97.0) | 7,8 | 14248 | 0,0046 | YOK | Chao12 | 52/56 | 17/21 | 200/200 |
| 2010-06-12 19:26 | 2010 M7.50 (7.9, 91.9) | 7,5 | 14083 | 0,0069 | YOK | Chao12 | 52/56 | 20/21 | 200/200 |
| 2011-03-11 05:46 | Tohoku 2011 (GELİŞTİRME VERİSİ, kör değil) | 9,1 | 8171 | — | VAR | Hill13 (özet) | 52/56 | 19/21 | 200/200 |

Toplam: 43 olay (12 VAR, 30 YOK, Tohoku geliştirme). Her olayda liste sınıfında **34–52**, kuyu sınıfında **7–20** istasyon
"var"; 86 yoklama isteğinin 86'sı 200 (4096 ya da 8192 bayt).

## 4. Kapı sonucu

**Öneri kapısı (≥ 2 bağımsız kör pozitif + ≥ 1 kör negatif, ≥ 3 istasyon): GEÇTİ**, iki sınıfta da ayrı ayrı:
liste sınıfında 12/12 pozitif ve 30/30 negatif olay ≥ 3 istasyonlu; kuyu sınıfında da 12/12 ve 30/30.

TR-7b için önerilen **önceden sabit seçim** (veri görülmeden; PGV eşiği Peng 2009 §6'nın "zayıf eşik ~0,027 cm/s
PGV_T" bulgusundan, böylece pozitifler literatürde açık görülen, negatifler de tetikleyebilecek güçte olaylardır):
- **Kör pozitif küme P (10 olay):** Q_CC = 1 ve PGV_T ≥ 0,027 cm/s, Tohoku hariç: Peru 2001, Denali 2002, Colima 2003,
  Tokachi-oki 2003, Sumatra 2004, Kuril 2006, Kuril 2007, Wenchuan 2008, Samoa 2009, Maule 2010. Kunlun 2001 ve
  Tonga 2006 (PGV_T 0,017 ve 0,013; yazarlara göre yalnız kaynağa yakın istasyonlarda görülen zayıf tremor) bilgi satırı.
- **Kör negatif küme N (2 olay):** Q_CC = 0 ve PGV_T ≥ 0,027 cm/s: Macquarie 2004 (0,0615), Peru 2007 (0,0272). Eşiğin
  hemen altındaki Solomon 2007 (0,0254) ve Nias 2005 (0,0217) bilgi satırı.
- Bağımsızlık: Kuril 2006 ile Kuril 2007 aynı kaynak bölgesinden, 2 ay arayla (iki ayrı tetikleyici sayılır, ama tremor
  kaynağının durumu ortak olabilir); Macquarie 2004, Sumatra 2004'ten 3 gün önce.

## 5. Sınırlamalar ve doğrulanamayanlar

1. **Availability tanecikliği.** NCEDC yanıtları çoğunlukla gün dosyası boyunca tek parça (00:00–23:59) verdi; dosya içi
   boşluklar bu yanıtla doğrulanmadı. %90 örtü yalnız bu yanıta ve R ortasındaki tek 10 sn yoklamasına dayanır (TR-7'de
   olduğu gibi bir olay düşerse kapı yine geçer: her sınıfta 10 pozitif, 2 negatif).
2. **CI istasyonları.** EarthScope availability bütün isteklerde 404 verdi (POST biçimi ya da veri yokluğu ayrılamadı);
   listedeki 6 CI istasyonu hiçbir olayda "var" sayılmadı. Sayılar bu yüzden alt sınırdır.
3. **NCEDC POST biçimi.** Boş konum kodu "--" ile POST 204 döndü; "*" ile düzeldi (betik notu). İlk, iptal edilen deneme
   günlükleri silindi; sonuçlara girmedi.
4. **Literatür körlüğü değil.** Yazar Peng 2009'un tam metnini okudu (tremorun Love/Rayleigh ile zamanlaması, bazı
   olaylarda P ve PKP ile tremor). Kör olan, TR-7b algılayıcısının bu olaylardaki çıktısıdır.
5. **"YOK" işaretinin anlamı.** Görsel incelemede görülmemek. Daha duyarlı bir algılayıcının N olaylarında algılama vermesi
   yöntem hatası kadar gerçek zayıf tremoru da gösterebilir (ön kayıt taslağı bu yüzden N'yi tek başına kalma şartı
   yapmaz).
6. Kuyu sınıfı (BP/PB) TR-7'nin Marmara tarafında karşılığı olmayan bir sensör türüdür (TR-7 §12); liste sınıfı Marmara ile
   doğrudan karşılaştırılabilirdir.
7. Sumatra 2004'te Peng 2009, HRSN'de olaydan sonraki günlerde güç kesintisi bildirir; availability W'yi kapsıyor gösterdi
   (13/13), ayrıntı doğrulanmadı.
8. E1 (telesismik cisim dalgası) maskesinin aday pencerelerdeki payı henüz hesaplanmadı (yalnız katalog gerektirir; ön
   kayıt dondurulmadan önce yapılacak, 0 €).
