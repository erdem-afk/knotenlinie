DÜZELTMEYLE KABUL

# TR-4 koşu kodu: bağımsız kod incelemesi

İncelenen (commit `301b5a8`): `kayit/turetme/tr4/tr4_indir.py` (`1dc4f294…`), `tr4_kosu.py` (`ecdba3ad…`),
`tr4_test_yapay.py` (`434901a1…`) ve `kayit/onkayit/TR-4_KODLAYICI-OKUMALARI.md` (`8ba4bf05…`; 36 okuma, R1–R10). Ölçüt:
`TR-4_marmara-hiz-tabani_ONKAYIT.md` DONDURULDU sürüm 2 + Ek 1 (`93fb3c8e…`; değiştirilmedi); 1b tanımı için TR-5b sürüm 3 §3,
§5.1 "1b", §5.5. Karşılaştırma: `TR-4_ASAMA0-KOD-INCELEME.md`. İncelemeci kodu yazmadı. 16 Kasım 2026, veri öncesi.

Ne yapıldı, ne yapılmadı:
- **Hiçbir gerçek dalga formu, üstveri ya da KOERI/FDSN isteği atılmadı.** Bütün sınamalar yapay veriyle ve yalnız
  127.0.0.1'deki sahte sunucuyla koştu (yazarın ağ korkuluğu `urlopen` ve `socket.create_connection`'ı sarar).
- Okunan gerçek dosyalar yalnız dondurulmuş aşama 0 çıktılarıdır (`/mnt/project-files/turetme/tr4-asama0/`
  `asama0_sonuc.json`, `hiz_sonuc.json`, `istekler.json`, `girdi/ham/marmara_fed_kanal.txt`): planın istek sayısını,
  kronolojik hacmi (R1) ve M5 maskesinin csv ile uyumunu ağsız hesaplamak için. Bunlar dalga formu değildir; hiçbiri
  değiştirilmedi.
- `tr5b_yapay_ccf.npz` (`44189a31…`, R9) karalama dizinindeki kopyadan okundu; sha256 tutuyor.
- Hepsi `python3 -I -B`, `OMP_NUM_THREADS=1`, numpy 2.5.3, obspy 1.5.1; `__pycache__` bırakılmadı.

## Hüküm

**DÜZELTMEYLE KABUL.** Kod ön kaydın hüküm sırasını (§4.3 adım 0–5), kapalı hüküm listesini ve kalıplarını (§4.5),
körlük sınırlarını (§2.2), bütçe ve kesik koşu kurallarını (§5.3), saklama düzenini (§5.5) ve kod denetimlerini (i) ve
(ii-a) metne uygun uyguluyor. İndirme "bitti" ya da "kesildi" olmadan `olc` hiçbir ε ya da Δ hesaplamıyor; hüküm
dosyası farklı bir hükümle yeniden yazılamıyor (I14, S06, S12). Kritik kusur yok. İki önemli kusur bulundu ve
düzeltildi; ikisi de yalnız `tr4_indir.py`'nin işletimini ilgilendirir, hiçbir ölçü kuralını, eşiği ya da hükmü
değiştirmez. Altı küçük kusur düzeltilmeden listelendi.

Yazarın altı "karar gereken" okumasından beşinde kodun okuması metne en yakın okumadır; biri (1b paydası) metinde
gerçekten iki anlamlıdır ve hükmün sınıfını belirler. Veri öncesi bir **Ek 2** için kesin cümleler §3'tedir.

## 1. Bulunan kusurlar

### Ö1. Kesin olmayan yanıt aynı işte hemen yeniden deneniyordu; bir sunucu kesintisi kuyruğu "yakardı" (düzeltildi)

`indir` her turda kuyruğun ilk işini (`Q[0]`) seçer. Kesin olmayan kodla biten istek (n = 1) kronolojik olarak hâlâ
ilk iş olduğu için **aynı işte, 2–10 sn sonra** ikinci kez atılıyordu. Yazarın belge dizesi ("sonraki çağrıda bir kez
yeniden denenir"), okuma 5 ("sonraki turda") ve aşama 0 betiğinin kabul edilmiş davranışı ("hata satırları ikinci
çağrıda yeniden denendi", Ek 1) ise ikinci denemeyi sonraki işe bırakır. Sonuç: KOERI birkaç dakika bağlantı
reddederse her istasyon-ay ≈ 20 sn'de iki denemesini tüketip bırakılırdı (10 dakikalık kesintide ≈ 30 istasyon-ay).
Tek yeniden deneme turu (§5.5) yalnız kuyruk bitince açılır; R1'e göre bütçe büyük olasılıkla kuyruk bitmeden dolar
(§4), bu yüzden bu aylar hiç geri gelmezdi. Kesik koşuda tek bir bırakılmış ay o yer-penceresinin T'sini "eksik" yapar
(§5.3, okuma 27); 2014–2020 aylarından biri T 2017–2021'i düşürürse hüküm, veri sunucuda olduğu hâlde, **"veri yok
(indirme bütçesi)"** olurdu. Ayrıca işler arasında akış durumu taşınmıyordu: hızlı yeniden başlatılan bir iş, önceki
işin son isteğinden 2 sn geçmeden ya da bekleyen bir Retry-After bitmeden istek atabiliyordu.

**Düzeltme** (`tr4_indir.py`): kesin olmayan yanıt alan istek aynı işte yeniden atılmaz (`bu_is_hata`); kuyrukta
yalnız bu işte başarısız olanlar kaldıysa iş temiz biter ve ikinci deneme sonraki işte yapılır. Bir işte 5 ardışık
kesin olmayan yanıt gelirse iş temiz biter (`ARDISIK_HATA_MAX = 5`; bir kesintide iş başına en çok 5 istasyon-ay
ikinci denemesini harcar). Akış durumu (son isteğin başlangıcı, Retry-After bitişi) `indirme_durum.json`'da işten işe
taşınır. Deneme sayısı (en çok 2, turda 3), KESIN kümesi, tur eşiği ve bütçe değişmedi. Sınamalar: I11, I12; mutantlar
N11, N12, N13.

### Ö2. İş sonu tahmini 1,3 bayt/örnekle yapılıyordu; ölçülen oran 1,60 (R1) (düzeltildi)

İş, bir isteği ancak kalan süre `1,25 × tahmin` ise başlatır; tahmin `gün × 4 × 3600 × 100 × 3 × 1,3 / hız`'dı. Aşama H
1,60 (1,26–2,11) ölçtü (R1): tahmin ortalamada %19, 2,11'lik istasyonlarda %38 kısa kalır ve 1,25'lik pay ortalamada
neredeyse tümüyle tükenir. İşin sonunda başlatılan istek süre sınırında kesilir (`sure_kesti`): aktarılan bayt atılır,
süresi etkin bütçeden düşer ve istek sonraki işte baştan atılır. 6000 sn'lik işte bir istasyon-ay ≈ 19 dk sürer
(119 KiB/s); kesilen her istek ≈ 20–25 dk'lık bütçe yakar. Kaba hesapla bu, 21 günlük bütçenin %2–5'idir (0,4–1 gün);
R1'e göre T 2017–2021'in bütçeye sığma payı medyan hızda ≈ 2 gündür. **Düzeltme:** tahmin, günlükteki son 20 başarılı
isteğin gözlenen bayt/gün ve bayt/sn değerleriyle yapılır; günlük boşsa eski formül ve aşama H medyanı kullanılır.
Sınama I13; mutant N14.

### Küçük kusurlar (düzeltilmedi; hükme etkileri yok ya da yok denecek kadar küçük)

- **D1. "veri yok (aşama 0)" dalı indirmeden ve bilgi satırı 0'sız hüküm yazar.** §4.3'e göre "veri yok" ile
  kesinleşen adım 0'dan sonra da (dolu yer-penceresi ≥ 30 ise) indirme yapılır ve bilgi satırı 0 yazılır; kalıpta
  "hesaplanmadı (indirme yok)" seçeneği yoktur. Dondurulmuş `asama0_sonuc.json` "G0 geçti" dediği için bu dal
  koşamaz; yalnız kayıt için.
- **D2. Kalıp T'nin son iki köşeli yeri.** Bilgi satırı 14 "x % (istasyon ortalaması)" diye doldurulur (kalıpta
  parantez yok; okuma 31 bunu bildiriyor) ve bilgi satırı 11 hesaplanamazsa "hesaplanamadı %" çıkar. Öneri: "x %" ve
  "hesaplanamadı".
- **D3. Bütçe bilgi satırı 13 sırasında dolarsa** bütün ana T'ler tam olduğu hâlde Kalıp T "kademe C, kesik, T …"
  yazar. Okuma 10 "koşu kesik sayılmaz" diyor; kod bunun tersini yapıyor. Metin ("bütçe dolarsa … kesik") kodu
  destekler; okuma belgesi kodla uyumlu hâle getirilmeli. R1'e göre bütçe büyük olasılıkla ana aylar bitmeden dolar.
- **D4. Eşzamanlı iki `indir` işine karşı kilit yok.** İşletim hatasıyla iki iş aynı anda koşarsa tek akış kuralı
  (§5.3) bozulur ve bütçe iki kez sayılır. Öneri: işletim kuralı olarak bir önceki iş kapanmadan (ya da başlangıcından
  2 saat geçmeden) yeni iş başlatılmaz.
- **D5. GET yolunda** bir istasyon-ayın bir günü 403/404 ile, ötekiler 200 ile biterse ayın kodu 200 olur ve o gün
  sessizce eksik kalır. Aşama H POST'u kabul ettiği için (`hiz_sonuc.json` "POST") bugün koşmaz.
- **D6. 200 ile gelen çözülemeyen miniSEED** (R6) yalnız günlükte `bicim_hata` olarak görünür; `ozet` bunları
  saymaz. Öneri: işletimde her işin sonunda `bicim_hata` sayısına bakılsın.

## 2. Metne uygunluk, madde madde

| Konu | Ön kayıt | Kod | Durum |
|---|---|---|---|
| Sunucu, istek birimi, biçim | §2.1 + Ek 1 `eida.koeri.boun.edu.tr`; §5.4 istasyon-ay başına bir istek; §5.2 POST, reddedilirse GET | `DS`; istasyon-ay POST, `hiz_sonuc.json` "GET" derse gün gün GET | Tamam (gerçek plan: 1851 istek, 37 013 istasyon-gün, C) |
| Kronolojik sıra | §5.3 2014-01 → 2023-12, ayda yerler kod sırasıyla | `plan`: ay, sonra istasyon kodu; bilgi 13 en sonda | Tamam (S01) |
| Kademe C günleri | §3.2 yerel güneş tarihi d'nin 1–20'si | `gun_secimi`, `gun_utc` (⌊−boylam/15 + 0,5⌋; Marmara'da (d − 1) 22:00–d 02:00) | Tamam |
| Körlük | §2.2 istekler ≤ 2025-12-31; hüküm verisi ≤ 2023-12-24; bilgi 13 ≤ 2025-05-31 | `kor_denet` bağlantıdan önce (POST ve GET), `plan`'da `assert` | Tamam. Tam boy planda (A, T 2017–2024, bilgi 13) en geç bitiş 2023-12-24 02:00 ve 2025-05-23 02:00 (I10); 2026 isteği GET yolunda bağlantısız reddedildi (I10, S02) |
| Bütçe | §5.3 21 etkin gün (504 iş-saati) ya da ilk istekten 42 takvim günü | `butce_asildi` her istekten önce; zorla kesilen işin süresi son kayıtlı ana kadar eklenir; "kesildi" kalıcı | Tamam (S05; N20, N21, N23) |
| Kesik koşu | §5.3 kesin kodla "indirildi"; analiz yalnız tam T'lerle; T 2017–2021 eksik ya da kapı tutmuyor → "veri yok (indirme bütçesi)"; Kalıp T "C, kesik, T …" | `olc` kesik dalı | Tamam (S05, S11, I01, I02; N01, N02). Bkz. D3 |
| ε/Δ yasağı | §5.3, §5.5 indirme bitmeden ya da kesilmeden ε/Δ yok | `olc` `indirme_durum.json` "bitti"/"kesildi" değilse durur; `tr4_indir.py` zincir işlevi içermez | Tamam (S06, M08) |
| Tek yeniden deneme turu | §5.5 başarısız > %5 → ε'dan önce tek tur | kuyruk bitince, bir kez, üçüncü deneme | Tamam (S03, I09; N10). Kesik koşuda tura ulaşılmaz (metnin sonucu) |
| Ön işlem | TR-5b §3.2 1–5 | `saat_onisle`, `beyazlat`: ≥ %99 üç bileşen, ≤ 1 sn aradeğer, ortalama + eğilim, %5 Hann, FFT ile 20 sn⁻¹ (7,5–8 Hz kosinüs), 0,5–2 Hz RMS, beyazlatma 0,4–0,5 / 2,0–2,1 Hz | Tamam (S07: bağımsız yazımla 1e-6) |
| ÇİF | TR-5b §3.3 ZE/ZN/EN, ±60 sn, enerji çarpımıyla normal | `cif3`, doğrusal (sıfır dolgulu) | Tamam (S07; bilinen +2 sn gecikme) |
| Enerji reddi, günlük ÇİF | TR-5b §3.2 m. 4, §3.3 ≥ 2 saat, maske | `gunluk_cif`; medyan pencerenin [a, b] saatlerinden | Tamam (S08, I06; N07). Okuma (2) §3 |
| Saklama | §5.5 saatlik ÇİF + RMS + tamlık; ham veri silinir; geçici ad + `os.replace`; sha256 günlükte | `cif_yaz`, `_akit` `.part` | Tamam. 2–4 Hz de saklanır (okuma (3)) |
| M5 maskesi | §2.3 60 gün, csv ile | `maske_gunleri` csv `maske_gun` ile denetler | Tamam: gerçek csv ile 11 maskeli pencere (60 / 21 gün) uyuşuyor; I08, N09 |
| 1b | §4.3 adım 1, TR-5b §5.1 dolu tanımı | `b1_hesapla` | Tamam; payda okuma (1) §3; I07, N08 |
| Kod denetimi (i) | §4.3 adım 2 (a) TR-5b başvurusu, (b) C'de `tr4_yapay_ref.json`, toleranslar | `denetim_i`, sha256'lı | Tamam: 60 + 60 dizi, sapan 0 (S14 gerçek npz ile) |
| Kod denetimi (ii-a) | §4.3 adım 3, C dilimine −%0,1, havuz medyanı [0,80; 1,20] | `ekle` (`tr5b_yapay.ger`), `olc` | Tamam (S09, S11, I04; N05) |
| ε geçerliliği | §4.3 adım 4 | `yer_T(Wg)` + `kapi` | Tamam (S11) |
| Ölçü ve önyükleme | §4.1–4.2 1,4826·MAD, \|Δ\| %95; iki yönlü, çarpım ağırlık, B = 2000, tohum sha256("tr4-hukum\|20261202")[:8]; σ %5–95, q95 %2,5–97,5 | `kestir`, `onyukleme` | Tamam: olc yolunda bağımsız yazımla 1e-12 (I05; N06), S10 |
| Hüküm eşikleri | §4.3 adım 5 U < %0,20; L > %0,245 | `c_hukmu` | Tamam (S10; M04, N17) |
| 9 hüküm, kalıplar | §4.5 | `olc`, `kalip_T`, `bilgi0_metin` | Tamam (S11'de 9 adın hepsi; Kalıp T düzenli ifadeyle birebir; I15 sayıları; N16). Bkz. D1, D2 |
| Bilgi satırı 0 | §4.3 ≥ 30 yer-penceresi ve ≥ 6 yer; ek cümle | `bilgi0_metin`; ek cümle `bilgi_0.ek`'te | Tamam (I03; N03, N04) |
| Bilgi satırları 1–14 | §8 | `bilgi_satirlari` | Tamam; hükmü değiştirmezler (S14 hepsini üretir) |
| Tek koşu | §5.6, §11 | `hukum_yaz`, `olc` başında erken dönüş | Tamam (S12, I14; M18, N15) |

## 3. Yazarın "karar gereken" altı okuması

Her birinde: metin tek anlamlı mı; değilse metne en yakın okuma; hüküm yönünü etkiler mi. Hiçbir karar veri
görülerek verilmedi; hiçbir gerçek dalga formu açılmadı.

**(1) 1b paydası kademe C'de (okuma 25).** *Tek anlamlı değil.* TR-5b §5.1 "payda: dilimin maskesiz günleri" der;
TR-4 §3.2 "öteki günler 'veri yok' sayılır, zincir değişmez" der. Harfiyen birlikte okununca payda takvim günleridir ve
C'de oran en çok 20/30,44 ≈ 0,657 olur: bir dilimde %8,7'den fazla gün kaybı 0,60'ı kırar. Öte yandan §4.3 adım 1 kapıyı
"**indirilen verinin** gün düzeyi doluluğu" diye tanımlar; §3.2 C'nin "ayda ≥ 10 geçerli gün" şartını açıkça C'ye
uyarlar; §3.3 ve §6.1 C'yi Δ'yı ≥ %91 kurduğu için seçer; §6.2'nin ana satırı (kademe C) gün doluluğu ve yatay kaybını
yalnız %10 hücre kaybı olarak varsayar. Takvim okumasıyla bu varsayımların hiçbiri tutmazdı ve C seçimi kapıyı
neredeyse kendiliğinden kırardı. **Metne en yakın okuma kodunkidir: payda dilimin örneklenen (1–20.) maskesiz
günleridir.** Hüküm yönünü (σ̂'nın değeri) etkilemez, ama hükmün sınıfını belirler: takvim okumasında C ile en olası
sonuç "veri yok (gün doluluğu)" olurdu. Ek 2 gerekli.

**(2) Enerji reddinin kapsamı ve medyanı (okuma 19).** *Büyük ölçüde tek anlamlı.* TR-5b §3.2 madde 1 "saat
penceresi"ni üç bileşenli birim olarak kabul eder; madde 4 "… aşan saat atılır" ve §3.3 "her kabul edilen saat için
ÇİF" aynı birimi kullanır. Kodun okuması (herhangi bir bileşen eşiği aşarsa saat bütün çiftlerden atılır) bu kullanıma
en yakındır. Medyan "aynı istasyon-bileşenin aynı penceresinin bütün saatlerinden" alınır: kod [T − 1095, T − 8]
içindeki, o bileşende tamlığı geçen bütün saatleri (maskeli günler dahil; maske gün geçerliliğine §3.3'te uygulanır)
kullanır; C'de yalnız örneklenen saatler vardır. Öteki okumalar (yalnız ilgili çiftten atmak) EN çiftini etkileyen
küçük bir gürültü farkıdır; yönlü bir etki beklenmez. Ek 2'de açıklık için bir cümle önerilir; zorunlu değil.

**(3) 2–4 Hz ÇİF'in saklanması (okuma 21).** *Tek anlamlı:* §8 madde 10 2–4 Hz Δ'yı ister ve §5.5 ham veriyi işlendikten
sonra sildirir; ikisi birlikte ancak 2–4 Hz saatlik ÇİF saklanırsa tutar. §5.5'in "C'de ≈ 4,0 GB" sayısı tek bant için
bir tahmindir, kural değil (TR-5b §5.2 de iki bandı saklar). Hükme etkisi yoktur. Bütçeye etkisi ölçüldü: ikinci bandın
beyazlatma + ÇİF'i saat başına 0,016 sn, istasyon-gün başına ≈ 0,06 sn, C'nin 37 013 istasyon-gününde ≈ 37 dk
(21 günlük bütçenin %0,1'i). Ek 2'de bir cümle önerilir.

**(4) Kesik koşuda "indirildi" kesin kod ister (okuma 27).** *Tek anlamlı:* §5.3 "bütün istasyon-ay istekleri kesin
kodla tamamlanınca 'indirildi' sayılır". "Kesin kod" aşama 0'ın KESIN kümesidir (200, 204, 404, 401, 403; Ek 1 K7);
204/404 "veri yok ama tamam" sayılır. Kod harfi uygular. Riskin (tek kalıcı hata bir T'yi düşürür) bedeli metindedir;
Ö1'in düzeltmesi bu riski geçici kesintiler için büyük ölçüde kaldırır. Hüküm yönünü değil, kesik koşuda "veri yok
(indirme bütçesi)" olasılığını etkiler. Ek 2 gerekmez.

**(5) Etkin süre (okuma 8).** *Büyük ölçüde tek anlamlı:* "21 gün (504 **iş**-saati)"; §5.5 "iş"i ≤ 2 saatlik koşu
birimi olarak tanımlar. Etkin süre işlerin duvar saatleri toplamıdır (işleme dahil). Kodun okuması budur. Fark küçüktür:
işleme ≈ 0,6 sn/istasyon-gün (ölçüldü: ön işlem 0,51 + iki bant ÇİF 0,06), miniSEED çözme ile C'de ≈ 6–8 saat
(bütçenin ≈ %1,5). Yalnız sınırda T 2022'nin tamamlanıp tamamlanmamasını etkileyebilir; T 2017–2021'i değil (§4).
Zorla kesilen işin süresi son kayıtlı isteğin sonuna kadar sayılır (kod); bu da Ek 2'de yazılabilir.

**(6) > 1 sn boşlukta sıfır doldurma (okuma 15).** *Tek anlamlı değil:* TR-5b §3.2 madde 1 kabulü yalnız ≥ %99 tamlığa
bağlar ve aradeğeri ≤ 1 sn ile sınırlar; %99–100 arasında kalan > 1 sn'lik boşluğu tanımlamaz. Kabul şartı açık olduğu
için saati reddetmek metne uymaz; aradeğer sınırı uzun boşluğun aradeğerlenmemesini ima eder. **En yakın okuma
kodunkidir:** saat kabul edilir, uzun boşluk ortalama ve eğilim çıkarıldıktan sonra sıfırla (yani ortalamayla)
doldurulur. Etki ≤ %1 örnekte, ÇİF genliğinde, oran ölçüsünde; yönsüz. Ek 2'de bir cümle önerilir.

### Önerilen Ek 2 cümleleri (veri öncesi; incelemeci eklemedi)

1. "Kademe C'de 1b'nin dolu gün oranının paydası, dilimin takvim ayının 1–20. günlerine (yerel ortalama güneş tarihi
   d) düşen maskesiz günleridir; ötekiler 'veri yok' oldukları için ne paya ne paydaya girer. Kademe A'da payda dilimin
   bütün maskesiz günleridir."
2. "Enerji reddinde üç bileşenden herhangi birinin 0,5–2 Hz RMS'i o bileşenin medyanının 3 katını aşarsa o saat üç
   çiftin hepsinden atılır. Medyan, yer-penceresinin [T − 1095, T − 8] aralığında o bileşenin tamlığı ≥ %99 olan bütün
   indirilmiş saatlerinden (M5 maskeli günler dahil) alınır."
3. "Bilgi satırı 10 için 2,0–4,0 Hz bandının (0,1 Hz kosinüs kenarlı beyazlatma) saatlik ÇİF'i de saklanır; §5.5'teki
   saklama hacimleri tek bant içindir ve iki bantta yaklaşık iki katıdır."
4. "Etkin indirme süresi, `indir` işlerinin başlangıcından çıkışına kadarki duvar saatlerinin toplamıdır (işleme
   dahil); zorla kesilen bir iş, son kaydedilen isteğinin bitişine kadar sayılır."
5. "Kabul edilen bir saatte 1 sn'den uzun boşluklar ve uçtaki boşluklar, ortalama ve doğrusal eğilim dolu örneklerden
   çıkarıldıktan sonra sıfırla doldurulur; saat reddedilmez."
6. (Bilgi; kural değiştirmez) "Aşama H'de ölçülen bayt/örnek 1,60'tır (1,26–2,11). §5.3'ün kademe kuralı §5.4
   formülündeki 1,3 ile uygulanır ve değişmez; gerçek hacmin bütçeyi aşması §5.3'ün kesik koşu kuralıyla karşılanır."

## 4. R1: ölçülen 1,60 bayt/örnek ve bütçe

**Metnin emri.** §5.3 kademeyi "veri görülmeden; yalnız v'den ve aşama 0'ın hacminden" seçtirir; V_A, V_C, V_D "§5.4
formülüyle" hesaplanır ve formül 1,3 bayt/örnek içerir. §5.4 ve Z9 aşama H'nin oranı "yeniden ölçtüğünü" yazar ama
ölçülen oranı kademe formülüne koymayı emretmez. Yani kademe, aşama 0'ın V'leriyle (A 312,8, C 206,1, D 153,6 GB;
`asama0_sonuc.json`) ve v'yle seçilir; 1,60 kararı değiştirmez. "D" bir kademe değildir: yalnız madde 2'nin eşiği ve
kesik koşunun en küçük kümesidir; "D'ye geçiş" diye bir adım yoktur. Gerçek hacim bütçeyi aşarsa §5.3'ün kesik koşu
kuralı işler: indirme kronolojik sürer, bütçe dolunca durur, analiz tamamlanmış T'lerle yapılır, Kalıp T "C, kesik, T
[ilk]–[son]" der; T 2017–2021 tamamlanmamışsa ya da tamamlanan T'lerle kapı tutmuyorsa hüküm "veri yok (indirme
bütçesi)"dır. Ölçülen 1,60'ı şimdi kademe kuralına koymak hız ölçüldükten sonra yapılmış bir kural değişikliği olurdu.

**Kodun davranışı.** Kademe `tr4_asama0.py`'de (dondurulmuş) 1,3'lü V'lerle seçilir; `tr4_indir.py` seçilen kademeyle
bütün planı kronolojik indirir, bütçeyi sayar ve kesik koşuyu metne göre uygular (S05, S11, I01, I02). Kod metnin
emrettiğini yapıyor. Tek sapma iş sonu tahminindeki 1,3'tü (Ö2; düzeltildi).

**Sayılar** (gerçek plan, 1851 istasyon-ay, ağsız; `inc_r1` hesabı; aktarım süresi, işleme ve bekleme hariç):

| bayt/örnek | v (KiB/s) | C tamamı | T 2017–2021'in kronolojik bitişi (KO.SLVT 2020-12, iş 1416) |
|---|---|---|---|
| 1,3 | 119,2 | 207,9 GB, 19,7 g | 158,9 GB, 15,1 g |
| 1,6 | 62,0 | 255,8 GB, 46,6 g | 195,6 GB, 35,7 g |
| 1,6 | 119,2 | 255,8 GB, 24,3 g | 195,6 GB, 18,6 g |
| 1,6 | 176,4 | 255,8 GB, 16,4 g | 195,6 GB, 12,5 g |

Kronolojik sırada T 2017–2021'in bitişi V_D'den (aynı oranla 189,0 GB) ≈ %3,5 büyüktür, çünkü 2019–2020 aylarında
T 2022–2023 pencerelerinin günleri de indirilir. 1,60 ve 119 KiB/s'de C bütçeyi aşar (24,3 > 21 gün): kesik koşu
beklenen durumdur. T 2017–2021 ≈ 18,6 gün aktarım + ≈ 0,3 gün işleme + istek aralıklarıyla ≈ 19 günde biter; pay
≈ 2 gündür. Etkin hız ≈ 105 KiB/s'nin altına düşerse T 2017–2021 bütçeye sığmaz ve hüküm "veri yok (indirme
bütçesi)" olur. 42 takvim günü sınırı, işlerin takvim süresinin en az yarısında koşmasını ister (günde ≈ 12 iş-saati).
Bugün `hiz_sonuc.json` "ertelendi (aktarım hızı)"dır: iki ölçüm 61,96 ve 176,39 KiB/s, medyan 119,17 (V_D / v =
14,6 gün → madde 2 tutar); karar Ek 1'in 5 gün kuralı ya da üçüncü ölçümle verilir (aşama 0 betiğinin işi).
Bilgi satırı 13'ün ayları kuyruğun sonundadır; kesik koşuda büyük olasılıkla indirilmez ve "veri yok" yazar.

## 5. Sınamalar ve mutasyonlar

**Yazarın sınamaları** (`tr4_test_yapay.py`, değiştirilmedi): düzeltmeden önce 14 / 14, düzeltmeden sonra 14 / 14
(S09 ve S14 dahil; gerçek npz ile kod denetimi (i) sapan 0). Yazarın 18 mutantı düzeltilmiş kodda: 18 / 18 yakalandı.

**İncelemecinin sınamaları** (`kayit/turetme/tr4/inc_kod/tr4_inc_kod_sinama.py`, I01–I16): 16 / 16. Yazarın
düzeneğini (sahte sunucu, ağ korkuluğu, yapay girdiler) içe aktarır; sınamalar ondan bağımsızdır: kesik gövde (yalnız
T 2021 eksik; T'ler tam ama kapı tutmuyor), bilgi satırı 0'ın iki sınırı, (ii-a)'nın iki ucu, olc yolunda önyüklemenin
bağımsız yazımla eşitliği, enerji medyanının pencere sınırı, 1b'de maske, M5 maskesinin 60 günü, tur eşiğinin tam
%5'i, tam boy planda körlük ve GET yolunda 2026 reddi, işler arası yeniden deneme ve akış, iş sonu tahmini, var olan
hükmün korunması, Kalıp T'nin sayıları, "kesildi"nin kalıcılığı.

**İncelemecinin mutantları** (N01–N23; yazarın M01–M18'inden ayrı; her biri yazarın hızlı sınamaları ve incelemecinin
sınamaları altında): 23 / 23 yakalandı (yazarın sınamaları 8, incelemecinin sınamaları 17).

| Mutant | Değişiklik | Yazarın hızlı sınamaları | İncelemenin sınamaları | Yakalayan |
|---|---|---|---|---|
| N01 | kesik: T 2021 D kümesinden düşer | hayır | evet | I01 |
| N02 | kesik: tamamlanan T ile kapı sınanmaz | hayır | evet | I02 |
| N03 | bilgi 0: n ≥ 31 | hayır | evet | I03 |
| N04 | bilgi 0: yer ≥ 7 | hayır | evet | I03 |
| N05 | (ii-a) üst sınır 1,30 | hayır | evet | I04 |
| N06 | hüküm önyüklemesi başka tohumla (olc yolunda) | hayır | evet | I05 |
| N07 | enerji medyanı pencere dışı saatlerle | hayır | evet | I06 |
| N08 | 1b: maskeli gün dolu sayılır | hayır | evet | I07 |
| N09 | M5 maskesi 59 gün | hayır | evet | I08 |
| N10 | tur eşiği ≥ %5 | hayır | evet | I09 |
| N11 | aynı işte yeniden deneme (Ö1 geri) | hayır | evet | I11 |
| N12 | akış durumu işler arasında taşınmaz (Ö1 geri) | evet | evet | S03, I12 |
| N13 | ardışık hata durdurması yok (Ö1 geri) | hayır | evet | I11 |
| N14 | iş sonu tahmini 1,3 formülüyle (Ö2 geri) | evet | evet | S04, I13 |
| N15 | olc var olan hükmü yeniden hesaplar | hayır | evet | I14 |
| N16 | Kalıp T: %80 için q95 + 1,0 σ̂ | hayır | evet | I15 |
| N17 | "karşılanmadı" U ile | evet | hayır | S10 |
| N18 | bilgi 13 körlük sınırı 2025-06-30 | evet | hayır | S02 |
| N19 | körlük sınırı role bakmaz | evet | hayır | S02 |
| N20 | bütçe: süren iş sayılmaz | evet | hayır | S05 |
| N21 | "kesildi" kalıcı değil | hayır | evet (I16 sonradan eklendi) | I16 |
| N22 | kesik gövde kesin sayılır | evet | hayır | S03 |
| N23 | sürdürme: zorla kesilen işin süresi kaybolur | evet | hayır | S05 |

N21 ilk koşuda iki takımdan da kaçtı: "kesildi" denetimi kaldırılınca bütçe sınaması yine istek attırmıyor, ama her
çağrı yeni bir iş kaydı açıp kesme anını (`bitis`) ileri taşıyor; hüküm metnindeki "takvim [..] gün" değişirdi. I16
eklendi ve mutantı yakaladı. Mutantların 15'ini yazarın sınamaları yakalamıyor: kesik koşunun iki dalı, bilgi satırı
0'ın sınırları, (ii-a)'nın üst ucu, olc yolunda tohum, enerji medyanının penceresi, 1b'de maske, M5 maskesinin gün
sayısı, tur eşiği, var olan hükmün korunması ve Kalıp T'nin sayısı. Bu yerlerde kod doğruydu; eksik olan sınamaydı.

Komutlar (kök dizinden):
```
OMP_NUM_THREADS=1 python3 -I -B kayit/turetme/tr4/tr4_test_yapay.py <karalama> <npz> [--mutasyon]
OMP_NUM_THREADS=1 python3 -I -B kayit/turetme/tr4/inc_kod/tr4_inc_kod_sinama.py <karalama> <npz> [--mutasyon]
```

## 6. İşletim notları (kod dışı)

- R9: `tr5b_yapay_ccf.npz` `/mnt/project-files/turetme/tr5b-ham/` altında yok; gerçek koşudan önce `tr5b_yapay2.py
  donder` ile yeniden üretilip sha256'sı (`44189a31…`) denetlenerek yerine konmalı. `denetim_i` kipi indirmeden önce
  koşturulabilir.
- D4: bir anda tek `indir` işi.
- Her işin sonunda `ozet` ve günlükteki `bicim_hata` satırları okunmalı (D6, R6).
- Dondurma: koşu kodu bu incelemenin son sha256'larıyla dondurulur (§5.6).

## 7. Son kod sha256'ları

Yalnız `tr4_indir.py` değişti (Ö1, Ö2). `tr4_kosu.py`, `tr4_test_yapay.py` ve okuma belgesi değişmedi.

| Dosya | sha256 |
|---|---|
| `kayit/turetme/tr4/tr4_indir.py` | `8ceefcd8d5db9737f6887fbfc49bb9b5c6c32baab930e630359cf45b35594574` (önce `1dc4f294c0ce79e2adeea8d4e007443abe28aa7c202d5f85ed82c40709002db3`) |
| `kayit/turetme/tr4/tr4_kosu.py` | `ecdba3ad0a3a7d13d15dd6008f172993b1d6a25d5d37b6585f1a455fa8f64b72` (değişmedi) |
| `kayit/turetme/tr4/tr4_test_yapay.py` | `434901a16c06dbafc05c5263513ccfe23b00be288e734b0b0340ab113bf2f60d` (değişmedi) |
| `kayit/turetme/tr4/inc_kod/tr4_inc_kod_sinama.py` | `93afed670e7a63c44e12598a1ad5edea94deb43bc2b588233db50ad4c1b94305` (yeni; inceleme sınamaları) |
| `kayit/onkayit/TR-4_KODLAYICI-OKUMALARI.md` | `8ba4bf058f2e5a2d607d4cd28aaf033cb97070ab8dd77b4a59b2c56a2facbaa1` (değişmedi) |
| `kayit/onkayit/TR-4_marmara-hiz-tabani_ONKAYIT.md` | `93fb3c8ea5f0b789318f41d1c5b1bbf6f134ebd8f8d4e213980c4a15f0a41f66` (değişmedi) |

Dondurulacak koşu kodu `tr4_indir.py` (`8ceefcd8…`) ve `tr4_kosu.py` (`ecdba3ad…`)'dir. Ek 2 eklenirse (§3) kod
değişmez: kod önerilen okumaları zaten uygular.
