# TR-13d sayımı: açık bölgesel kataloglarla kaç yeni bağımsız küme

Tarih: 17 Kasım 2026. 0 €. Ön kayıt değil. Kural sayımdan önce yazıldı: `TR-13d_SAYIM-KURALI.md` (commit 8a99970).
Kod ve json: `kayit/turetme/tr13d/` (`tr13d_aday.py` → `tr13d_aday.json`; `tr13d_sayim.py` sayım; `tr13d_ozet.py`
→ `tr13d_sayim.json`; `tr13d_ham.py` → `tr13d_ham_sha256.txt`). Gerçek katalogda V(q), Gini ya da z hesaplanmadı.
`tr13b_kosu.kos()` çağrılmadı; yalnız `hazirla` değiştirilmeden içe aktarıldı.

## Hüküm

**Birincil yeni K (M ≥ 6,5) = 7.** İkincil (M ≥ 6,0) = 8; TR-13c'nin 5 kümesiyle birleşik 13. Dal (kural §6):
**yeni K < 10 → aday durur.** Açık bölgesel kataloglar TR-13'te düşen 164 M ≥ 6,5 kümesinden 7'sini kurtarıyor.
Darboğaz katalog değil, kataloğun olduğu yerde doğrultu atımlı M ≥ 6,5 olay sayısı: 887 adayın 420'si okyanus
sırtlarında, 305'i açık bölgesel kataloğu bilinmeyen ada yaylarında ve kıta içinde (Çin dahil); 53'ü erişilemeyen
katalogların bölgesinde. Hiçbir aday elenmedi. Bu bir H0 değildir.

## Bölge tablosu (aday = temiz önce-pencere, TR-13b kümesi dışı, TR-13'te düşmüş)

| Bölge | Aday olay / küme (M ≥ 6,5) | Katalog | Erişim | Geçen olay / küme (M ≥ 6,5 küme) |
|---|---|---|---|---|
| Japonya | 17 / 13 (6 / 6) | JMA yıllık dosyaları (1967–2024) | açık | **4 / 4 (4)** |
| Tayvan | 3 / 3 (1 / 1) | CWA → JMA | CWA GDMS oturum ister; JMA ile sayıldı | 0 |
| Kanada (BC) | 20 / 3 (6 / 2) | NRCan FDSN | açık | **1 / 1 (1)** |
| Yunanistan-Ege | 8 / 6 (3 / 3) | NOA → AUTH | NOA FDSN 2011-06'dan önce boş (hiçbir adayın [t − 10 y, t)'sini kapsamıyor); AUTH dosyası (1995+) açık | **1 / 1 (1)** |
| Yeni Zelanda | 11 / 7 (3 / 2) | GeoNet FDSN | açık | **1 / 1 (1)** |
| İzlanda | 3 / 2 (1 / 1) | IMO quakes API (SIL, 1991-01-07+) | açık | 1 / 1 (0; M 6,3) |
| Türkiye | 11 / 8 (3 / 3) | AFAD → KOERI | AFAD her sorguya boş [] (işlevsiz); KOERI zeqdb açık (yavaş) | 0 |
| Svalbard-Jan Mayen | 6 / 6 (2 / 2) | NNSN FDSN | açık (daire parametresi yok sayılıyor; kutu + yerel süzgeç) | 0 |
| İtalya-Adriyatik | 1 / 1 (0) | INGV FDSN | açık | 0 |
| Şili-Arjantin | 4 / 4 (1 / 1) | CSN günlük HTML | 2001 öncesi sayfalar 403 (aşılmadı) | 0 (2 M < 6,5 olay sayım sürüyor; aşağıda) |
| İran-Kafkas | 14 / 12 (6 / 5) | IRSC | erişilemedi (https sıfırlandı, http 503) | – |
| Kuzey And | 10 / 10 (3 / 3) | SGC FDSN | erişilemedi (port 8080 kapalı, 443'te yol 404) | – |
| Meksika | 29 / 19 (7 / 4) | SSN | erişilemedi (bağlantı sıfırlandı) | – |
| Kaliforniya / ABD iç batı / Alaska | 25 / 20 (10 / 10) | yeni katalog yok (bölgesel ağlar ComCat içinde) | – | TR-13 sonucu aynen: 0 |
| Çin-Tibet | 29 / 23 (10 / 9) | CENC kayıt ister; denenmedi | – | – |
| Okyanus sırtları ve öteki (Pasifik adaları, Endonezya, PNG, Filipinler, Mariana, Myanmar, Orta Asya, Kamçatka, Orta Amerika, Karayip, Peru-Bolivya, Afrika, Avustralya) | 696 / ≈ 355 | açık makine kataloğu bilinmiyor | denenmedi | – |

Toplam aday 887 olay / 488 küme (M ≥ 6,5: 212 / 164). Bölgesel katalogla sayılan 82 olay (+2 CSN sürüyor). Denenmeyen (katalog yok/kayıt) 725 olay / 378 küme
(M ≥ 6,5: 160 / 124).

## Geçen olaylar (§3.1–3.3; hepsi tek üyeli, TR-13b'nin 16 olayıyla doğrudan çakışma yok)

| Olay | Küme | R km | Katalog | Mc önce / ref / ortak / son | N3bg | N_ref | TR-13'te neden düştü | §2 süzgeci |
|---|---|---|---|---|---|---|---|---|
| Tottori (Matsue) 2000 M 6,7 | 421 | 76,7 | JMA | 1,6 / 1,7 / 1,7 / 1,9 | 99 | 204 | arka plan (küresel 0) | geçer |
| Fukuoka 2005 M 6,6 | 543 | 66,5 | JMA | 0,5 / 0,7 / 0,7 / 1,2 | 86 | 175 | referans | geçer |
| Okinawa açığı 2010 M 7,0 | 710 | 117,8 | JMA | 2,2 / 2,2 / 2,2 / 2,4 | 93 | 231 | referans | geçer |
| Makurazaki açığı 2015 M 6,7 | 882 | 76,7 | JMA | 1,6 / 2,1 / 2,1 / 2,1 | 75 | 144 | referans | **geçmez** (Mc_ref > Mc_önce + 0,3) |
| Arthur's Pass 1994 M 6,8 | 327 | 88,5 | GeoNet | 2,6 / 2,7 / 2,7 / 2,7 | 74 | 93 | referans | geçer |
| Zakynthos 2018 M 6,8 | 959 | 88,5 | AUTH | 2,4 / 2,7 / 2,7 / 2,8 | 95 | 247 | referans | geçer |
| Vancouver Adası açığı 2014 M 6,5 | 1133 | 57,7 | NRCan | 1,8 / 1,7 / 1,8 / 1,8 | 92 | 193 | arka plan (küresel 0) | geçer |
| Ölfus 2008 M 6,3 (ikincil) | 645 | 50,0 | IMO | 0,4 / 0,6 / 0,6 / 1,7 | 90 | 144 | arka plan (küresel 0) | geçer |

Bilgi (K'ye girmez): §2 süzgeci de istenirse birincil K 6, ikincil 7. Sınırda kalanlar: Selfoss 2000 M 6,5 (N3bg 93,
referans 94 < 98), Vancouver Adası 2011 M 6,4 (N3bg 48), Lixouri 2014 (44), Haida/Explorer 2018 M 6,8 (44),
Marmara Ereğlisi 2025 (KOERI, 44; Marmara kutusu: yalnız sayı, Marmara terimi değildir). Türkiye'de KOERI ile ortak Mc
1,9–3,7 ve N3bg 2–44; Doğanyol 2020 N3bg 11, Düzce 2022 N3bg 12.

## Görülebilir en küçük etki (kaba ölçek; tahmindir, yapay hesap yapılmadı)

MDE ∝ 1/√K, TR-13c_SAYIM'daki noktalardan (K 10 → 0,39 büyük R / 0,58 R = 50 km; K 18 → 0,32):
- **Birincil K 7:** MDE ≈ 0,47 (iyimser) … 0,69. Yeni üyelerin R'si 58–118 km; 50 km değil, ama 57,7 km'lik
  üye (1133) kalibrasyon sorununa yakın.
- İkincil K 8: ≈ 0,44 … 0,65. TR-13c ile birleşik 13 (TR-13c'nin 5'i R = 50 km): ≈ 0,34 … 0,51.
- f ≈ 0,2–0,25 için kuralda yazılan K ≈ 24–84 (ölçüde 29–46). Elde 7–13. f ≈ 0,2 **tahmin**dir (TR-13 benzetimi);
  etki yarıysa K 4 katı, iki katıysa K/4 gerekir.
- Bilgi: TR-13b'nin keşif dışı 10 kümesi + bu 7 = 17 → ≈ 0,33; ama TR-13b z'leri görüldüğü için bağımsız sınav olmaz.

## Öneri

TR-13d ön kaydı yazılmaz; sınırlı koşu seçeneği de dal kuralıyla açılmaz (K < 10). Bu açık veriyle TR-13 ailesinde
bağımsız yeni kümelerle f ≈ 0,2'ye inmek mümkün değil. Bir sonraki bilgi kazancı ancak (1) IRSC, SSN, SGC, CWA gibi
erişilemeyen kataloglara meşru erişim (İran 5, Meksika 4, Kuzey And 3 M ≥ 6,5 kümesi; ama çoğu küresel katalogda
Mc ≥ 4 ve bölgesel tamlıkları bilinmiyor), ya da (2) TR-13c'de yazılan yöntem değişikliğiyle olur.

## Körlük, sapmalar ve doğrulanamayanlar

- Bütün sorgular t'den önce ve ≤ 2025-12-31 biter; 2026 satırı okunurken atılır. Ana şok sonrası pencere yok; Marmara
  GNSS'e dokunulmadı; İstanbul için olasılık yazılmadı; dış servise ad/e-posta/proje bilgisi gönderilmedi; genel
  User-Agent; 401/403 aşılmadı; kayıt isteyen servise başvurulmadı.
- **AUTH `finalcat.cat` 2026-05'e kadar satır içeriyor** (tek dosya, başka biçimi yok). 2026 satırları okunurken atıldı;
  ham pakete yalnız < 2026 satırları kondu, özgün sha256 ayrıca yazıldı.
- **Sapma (beyan): JMA ayrıştırma hatası sonuç görüldükten sonra düzeltildi.** İlk koşuda eski (1997 öncesi) kayıtlarda
  boş düşük haneler yanlış okunuyordu (örn. '548 ' = 54,8' yerine 5,48'). Düzeltilip bütün JMA olayları yeniden
  sayıldı. Geçen dört olay değişmedi; yalnız 1997 öncesi olayların sayıları değişti (hepsi yine düşüyor).
- Yorum (beyan): kuraldaki "ilki olayı kapsamıyorsa" = katalog başlangıcı > t − 10 y. NOA (2011-06+) bu yüzden hiçbir
  Yunan adayında kullanılmadı; AUTH kullanıldı. Kapsam başlangıcı ≥ t ise olay sayılmadan düşer (yalnız İzlanda 1987).
- Büyüklük türleri dönüştürülmedi: JMA MJMA (V/v/D/J), NRCan ML ağırlıklı (+Mw), GeoNet ML, AUTH ML ağırlıklı, IMO SIL
  "Mw ölçekli boyut", KOERI xM, NNSN karışık, CSN Ml/Mc. IMO'da yalnız type = earthquake, SIL sistemi, otomatik +
  el ile.
- **Doğrulanamayan / tamamlanmayan:** CSN ile Constitución 2020 (M 6,1) ve Pocito 2021 (M 6,4) sayımı rapor
  yazılırken sürüyordu (günlük sayfalar, ≈ 1 sayfa/s). İkisi M < 6,5'tir; birincil K'yi değiştiremez, ikincil K'yi en
  çok 2 artırır. Süre sınırı yüzünden iş 19:50 UTC'de durduruldu (≈ 3576 günlük sayfa önbellekte, scratch'ta; pakete
  girmedi). Bu iki olay **sayılmadı**; sürdürmek için aynı komut önbellekten devam eder. Teno 2004: 2001 öncesi sayfalar 403,
  Mc kestirilemedi. KOERI'nin web listesinin üst sınırı belgelenmemiş; yıllık parçalar 700 satırın altında kaldı.
- Ham: `/mnt/project-files/turetme/tr13d-ham/` (sha256 `kayit/turetme/tr13d/tr13d_ham_sha256.txt`).
