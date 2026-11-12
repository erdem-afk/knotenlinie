DÜZELTMEYLE KABUL

# TR-4 aşama 0 betiği: bağımsız kod incelemesi

İncelenen: `kayit/turetme/tr4/tr4_asama0.py` (`e5d8c33c…`), `tr4_asama0_prova.py` (`6ce012b7…`),
`tr4_asama0_kuru.json` (`ecbde36c…`), `tr4_asama0_prova.json` (`42adc1af…`). Ölçüt:
`TR-4_marmara-hiz-tabani_ONKAYIT.md` DONDURULDU sürüm 2 (`7d6e48a0…`; §4.3, §4.5, §5.1–5.3, §5.6) ve
`TR-4_INCELEME-1.md` İ1-E4'ün 14 şartı ile İ1-E1. Karşılaştırma: `tr5b_asama0.py` ve `TR-5b_INCELEME-2.md`.
İncelemeci betiği yazmadı. 12 Kasım 2026, veri öncesi.

Ne yapıldı, ne yapılmadı:
- **Ağ kipleri çalıştırılmadı.** Hiçbir dalga formu ya da üstveri istenmedi. Sınamalarda `urlopen` istisna atan bir
  işlevle değiştirildi, `_getir` ve `_akit` sahte yanıtlayıcılarla, saat sahte bir saatle. 2026 verisi yok.
- Girdiler `/mnt/project-files/turetme/tr5b-ham/tr5_ham_ustveri_2026-11-12.tar.gz` arşivinden karalama dizinine
  açıldı (`marmara_fed_kanal.txt` `dbcc3ba8…`, `onbellek.jsonl` `ce4fe524…`; tutuyor).
- Hepsi `python3 -I -B`, yalnız numpy (2.5.3), tek süreç; `__pycache__` kalmadı. Denetim bataryası ve mutasyon
  koşucusu karalama dizinindedir; depoya konmadı. Git işlemi yapılmadı.

## Hüküm

**DÜZELTMEYLE KABUL.** Betik, ön kaydın aşama 0 ve aşama H kurallarını ve İ1-E4'ün 14 şartını karşılıyor. TR-5b
İNCELEME-2'nin bulduğu kusurların hiçbiri yinelenmiyor: sha denetimi her kipte var, kesin olmayan kodlar bir kez
yeniden deneniyor, `say` eksikte G0 vermiyor, yarım satır düşürmüyor, yazımlar atomik, yatay kural koşullu.

İki önemli ve bir küçük hata bulundu ve düzeltildi. Üçü de yalnız aşama H'yi ilgilendirir. G0'ın hesabı, istek
listesi, `kuru` ve prova çıktıları değişmedi (aşağıda sha256'lar). Değişiklik ön kaydın sonuna "Ek 1" olarak yazıldı;
ön kaydın gövdesine dokunulmadı.

- **Ö1. Aşama H'nin soket zaman aşımı 60 sn idi; §5.2 isteğe 15 dk tanır.** `_akit`, `urlopen(timeout=60)` ile
  açıyordu. KOERI 28 MB'lık bir POST'u 60 sn içinde akıtmaya başlamazsa istek bağlantı hatası olurdu. İkinci deneme de
  böyle biterse satır 0 bayt ile sayılırdı. Sekiz isteğin hepsinde bu olursa v ≈ 0 olur ve hüküm "veri yok (aktarım
  hızı)" çıkar. Bu, metinde olmayan bir uygulama ayrıntısından gelen bir hüküm olurdu. Ayrıca tavanı aşan bir okuma zaman
  aşımına uğrarsa istek "kesik" yerine hata sayılıyordu. Metne göre "o ana kadarki bayt ve süre sayılır".
  **Düzeltme:** zaman aşımı `tavan_sn` (900 sn). Yanıt kodu alındıktan sonra tavanda zaman aşımı olursa istek kesik
  sayılır ve o ana kadarki bayt ve süre tutulur.
- **Ö2. Aşama H seçimi numpy sürümüne bağlıydı ve bu denetlenmiyordu.** Seçim `np.random.default_rng(...).choice` ile
  yapılıyor. NumPy, `Generator` akışlarının sürümler arasında aynı kalacağını güvence etmez. `hiz` seçimi koşu anında
  yeniden hesaplıyor ve kuru kipte yazdırılan seçimle (İ1-E4 madde 11) karşılaştırmıyordu. Ortam değişirse önceden
  yazılmış seçim sessizce başka bir seçimle değişebilirdi. **Düzeltme:** seçimin sha256'sı (`e355b787…`) koda yazıldı.
  `hiz_secim` farklı bir seçim üretirse `kuru` da `hiz` de durur. Bugünkü seçim aynıdır: `kuru` çıktısı bit düzeyinde
  aynı.
- **K1. Aşama H'nin GET yolunda (POST reddedilirse) beş günden biri kesin olmayan kodla biterse istek yine 200
  sayılıyordu.** Eksik gün yeniden denenmez ve v'ye 0 baytla girerdi. **Düzeltme:** bir gün kesin olmayan kodla biterse
  isteğin kodu odur ve istek İ1-E4 madde 6'ya göre bir kez yeniden denenir.

## 1. 14 şart, madde madde

| Şart | Durum | Not |
|---|---|---|
| 1 sha256'lar | Tamam | Dört girdi her kipte (`kuru`, `ustveri`, `kur`, `yokla`, `say`, `hiz`) denetleniyor; sabitler 64 hane, `assert`. Kod kendi sha'sını ya da ön kaydın sha'sını denetlemiyor; Ek 1 hiçbir denetimi bozmaz |
| 2 aday kümesi | Tamam | `ana_T ∧ (DOLU_ana ∨ aday_yoklanmamis)`, KAVV dışarıda; 110 + 3 − 8 = 105 ve 26 / 468 / 84 / 15 / 30 / 8 sapmada durur. Mutantlar M04, M25 durduruldu |
| 3 üstveri | Tamam | `level=channel`, `BH?,HH?`, [ilk a, son b]; geçici ad + `os.replace`; kesin olmayan kodda iki deneme (`ug[s] < 2`) |
| 4 kanal seçimi, aygıt | Tamam | `kanal_sec`, `kapsar`, `aygit` `tr5b_asama0.py`'dekilerle AST düzeyinde aynı (yalnız belge dizesi farklı). Aygıt [a, b]'de, üç bileşende. Önizleme farkı `istekler.json`'da |
| 5 yoklama biçimi | Tamam | 15'i 12:00–12:01 UTC, tek akış, ≥ 2 sn, genel UA, TLS açık, 429/503'te Retry-After ≤ 120 sn |
| 6 kesin kodlar | Tamam | `(200, 204, 404, 401, 403)`; `son_durum`, `satirlar`, `ekle_ac`, `ay_durum` TR-5b ile aynı. Yeniden deneme bir sonraki çağrıda, istek başına en çok iki |
| 7 Z iki kaynaktan | Tamam | TR-5 önbelleği (`KO.<ist>.<ay>`), üç aday ve SLVT için yeni yoklama; konum kodu boşluğu hem fed'de hem üstveride `assert` |
| 8 koşullu yatay kural | Tamam | Z'si "var" olan dilim bilgili; ≥ 1 bilgili dilim ve her bilgilide iki yatay "var"; yoksa `yatay_bilgisiz` (B6m–o) |
| 9 körlük | Tamam | `kor_denet` her istekten önce: tarih türü, sınır ve ≤ 2025-12-31; hüküm ≤ 2023-12-24, bilgi satırı 13 ≤ 2025-05-31; `istek_kur`'da `assert`. Bilgi satırı 13 ayrı rol, G0'a girmez |
| 10 `say` | Tamam | Eksik istek ya da üstveri varsa durur ("aşama 0 tamamlanmadı: …; G0 verilmez"); içerik şartın listesini taşıyor; atomik, `sort_keys`, belirlenimci |
| 11 aşama H | Tamam (Ö1, Ö2, K1 ile) | Tohumlu seçim kuru kipte yazdırılır; bayt, süre, kod, sha256; kademe sabit eşiklerle ve `asama0_sonuc.json`'un V'leriyle; elle girdi yok |
| 12 süre, prova | Tamam | `sure_sn` ≤ 6000; kalan < 2 × en uzun beklenen istek ise yeni istek yok. Prova bütün gösterimleri yapıyor |
| 13 `--ag-onay` | Tamam | Bayraksız ağ kipi istek atmadan çıkar (prova P0) |
| 14 tek koşu | Tamam | `kur` yoklama başladıktan sonra listeyi değiştiremez; `ustveri` liste kurulduktan sonra koşmaz; `yokla` sayımdan sonra koşmaz; `say` farklı sonuçla yeniden yazamaz |

## 2. İstenen noktalar

- **Kapı G0.** `yer_T` = T başına dolu yer kümesinin büyüklüğü; `kapi` ≥ 10 yerli T'ler arasında `y − x ≥ 3` olan bir çift
  arıyor. Ön kayıt §4.3 adım 0 ve §4.4 ile aynı. Ön kayıt sayıları (15, 16, 15, 14, 14, 9, 10, 9 → geçer; sıkı
  doluluk 7, 12, 11, 9, 9, 9, 8, 7 → geçmez) bataryada aynı sonucu veriyor. G0 hükmü sahte boru hattında bağımsız
  yazımla yeniden hesaplandı (B6i–j).
- **Yer birleştirme.** Tek birleşen yer ISK + KAVV'dir ve KAVV aday kümesine hiç girmez. Bu yüzden G0 sayımı ile yer
  sayımı aynıdır. M05 ("yer yerine istasyon say") bu yüzden eşdeğer mutanttır, hata değildir. Temsilci aşama 0'dan
  sonra yeniden seçilmez: ISK bir T'de düşerse KAVV yerine geçmez (§2.4 "Öteki istasyon indirilmez").
- **Olaysızlık ve M5 maskesi listeden.** Betik olaysızlığı yeniden hesaplamaz. `DOLU_ana` ve `aday_yoklanmamis`
  csv'de `uygun_ustveri`'ye, o da `sakin_ana`'ya bağlı (sayım betiği satır 219–221). Denetlendi: iki bayrağın her
  satırında `sakin_ana` doğru. M5 maskesi aşama 0'ın işi değildir (ε'dan gün atar); csv'deki `maske_gun` ve
  `maske_olay` koşu kodunun girdisidir.
- **Kesin kodlar, iki deneme, eksikken G0 yok:** B4, B6b–h ve M08–M11, M20 ile sınandı.
- **2026 kapısı:** B3 ve M12–M13 ile sınandı. Aşama H'de istek bitişi yerel güneş günü d'dir. UTC penceresi
  (d − 1) 22:00 – d 02:00'dır, bu yüzden bitiş ≤ d. Seçilen günlerin en geçi 2023-06-07.
- **Aşama H kademe seçimi.** `kademe_karar` §5.3 madde 1–4'ü uyguluyor: ilk ölçüm A ya da C verirse karar odur. Vermezse
  ölçüm 2 ve 3, her biri bir öncekinin bitişinden ≥ 2 gün sonra koşulur. Üç ölçümün medyanına madde 1–2 yeniden
  uygulanır, seçilmezse "veri yok (aktarım hızı)". A eşiği V_A / v ≤ 7 gün, C eşiği V_D / v ≤ 21 gün; V'ler
  `asama0_sonuc.json`'dan (aşama 0'dan sonra dolu kalanlar). Birim GB = 10⁹ bayt, v KiB/s; §5.3'ün önceden bildirilen
  süreleriyle (ör. V_C 196,7 GB, 23 KiB/s → 97 gün) tutarlı. Kesik koşu ve "veri yok (indirme bütçesi)" bu betikte
  değil, koşu kodundadır (doğru: indirme başlamadan bütçe yoktur). Ek metinler §4.5 kalıplarıyla aynı.
- **Hız hesabı.** v = Σ bayt / Σ süre, sekiz isteğin geçerli satırlarından. Süre `_akit` içinde bağlantı açılmadan
  başlar, son bayta kadar sürer. Bağlantı ve sunucu beklemesi dahildir, istekler arası 2 sn dahil değildir. Hata kodlu
  isteklerin sayılışı:
  - İki denemede de hata veren istek 0 bayt ve kendi süresiyle sayılır. Bu v'yi düşürür ve "bağlantı ve bekleme
    dahil" cümlesine uyar.
  - 204/404 kesindir; 0 bayt ve süresiyle sayılır.
  - Tavanı aşan istek o ana kadarki bayt ve süreyle sayılır (Ö1'den sonra zaman aşımında da).
  - İlk denemesi hata veren, ikincisi başaran isteğin yalnız ikinci denemesi sayılır; ilk denemenin süresi dışarıda
    kalır (K2).
  - POST reddi satırları ölçüme girmez.

  Metne uygun (B7e).

## 3. Yazarın okumaları

| Okuma | Hüküm | Gerekçe |
|---|---|---|
| Aşama H seçimi: 8 **farklı** istasyon (yerine koymadan), ana örneklemin 102 yer-penceresinin (aşama 0 öncesi) gün birleşiminden **5 ardışık gün**, 2014-01-01…2023-12-31 içinde, ilk gün ≤ ayın 16'sı (beş gün de 1–20'de), UTC penceresi yerel ortalama güneş gecesi (tam saate yuvarlanmış boylam), `HH?`, `--` | **KABUL** | §5.2'nin "ana örneklemin yer-pencerelerinden" ifadesinin en dar ve veri görmeyen okunuşu. Aşama 0 öncesi listeden seçmek, seçimi kuru kipte yazdırılabilir kılar (madde 11) ve aşama 0'ın sonucuna bağlamaz. 1–20 şartı metinde yok, ama zararsızdır: istek hem A'nın hem C'nin gün kümesinden olur. Sürüm bağımlılığı Ö2 ile kapatıldı |
| "En çok 5 gün": ilk tamamlanmış ölçümün bitişinden 5 gün geçince, eldeki tamamlanmış ölçümlerin (1 ya da 2) medyanına madde 1–2 uygulanır; seçilmezse madde 4 | **KABUL** | §4.3 adım 0 "en çok 5 gün sürer ve madde 1, 2 ya da 4 ile biter" ile çelişmez ve durumu her koşulda kapatır. Takvim sığar: 2. ölçüm ≥ 2 gün, 3. ölçüm ≥ 4 gün + süre (≤ 2 saat). **Yol ağsız sınandı** (B2h–k, B7a–b): tek ölçüm 60 KiB/s, 5 gün → "veri yok (aktarım hızı)", yeni istek yok; iki ölçüm 60 ve 120 → medyan 90 → C; 5 gün dolmadan iki ölçüm → "ertelendi"; 2 günden önce yeni ölçüm yok; en çok üç ölçüm. Yan etkisi K3'te |
| Sunucu `eida.koeri.boun.edu.tr` (ön kayıt §2.1: `eida-service.koeri.boun.edu.tr`) | **KABUL**; ön kayıt metni Ek 1 ile düzeltildi | TR-5'in doluluk önbelleğini (`ce4fe524…`) üreten `doluluk_yokla.py`, `ustveri_indir.py`, `tr5b_asama0.py` ve TR-7 betikleri hep `eida.koeri.boun.edu.tr`'yi kullanır. AV.md satır 20'deki erişim de bu adla. Ön kayıttaki ad bir yazım farkıdır. Ağsız inceleme olduğu için ad yoklanmadı |
| Üstveri 26 istasyon | **KABUL** | 22 ana istasyon (KAVV dahil) + GAZK, GEML (aday) + BOTS, NMR9 (2025 PK). `tr4_onkayit_sayim.py` satır 361'in tanımı ve §5.1 tablosu. KAVV, BOTS ve NMR9'un üstverisi kullanılmaz; bu 3 hafif istek israftır, zararsızdır ve tablo bağlayıcıdır |

## 4. Bulgular

Düzeltilenler: **Ö1, Ö2, K1** (yukarıda). Düzeltilmeyenler, bilgi ve not:

- **K2.** Aşama H'de ilk denemesi kesin olmayan kodla biten isteğin süresi v'ye girmez. Yalnız hatalar sıksa önemlidir.
  Bunlar `hiz_gunluk.jsonl`'da görünür. Metin yeniden denemeyi tanımlamıyor. Bırakıldı.
- **K3.** 5 gün kuralı zamana bağlıdır. Operatör 3. ölçümü 5 gün sınırının dışına iterek kararı iki ölçümle
  aldırabilir. Bu yalnız hızı görür, dv/v körlüğünü bozmaz. İşletim notu: 2. ve 3. ölçüm, 2 günlük bekleme biter
  bitmez koşulmalıdır.
- **K4.** İki denemede de alınamayan üstverinin pencereleri `uc_bilesen_yok` nedeniyle düşer; ayrıca
  `ustveri_alinamayan`'da listelenir. Neden kodu yanıltıcıdır, hesap doğrudur (İ1-E4 madde 3: en çok iki deneme).
- **K5.** Aşama H'de 429/503'ün Retry-After başlığı okunmuyor; 30 sn beklenir. Zararsız.
- **K6. Ön kayıt boşluğu.** G0 geçip dolu yer-penceresi < 30 olursa (kapı ≥ 20 pencereyle geçebilir) ön kayıt
  hüküm tanımlamıyor. Kod indirme yapmaz, aşama H koşmaz. Bu sayılarla pratikte olanaksız. Olursa hüküm koşu kodunun
  incelemesinde bağlanmalıdır.
- **K7. Koşu koduna not** (`tr4_kosu.py`): üretim isteklerinin soket zaman aşımı, aşama H'nin ölçtüğü rejimle aynı
  olmalıdır (Ö1). Kesik koşunun "kesin kodla tamamlandı" sayımı aynı `KESIN` kümesiyle yapılmalıdır.

## 5. Mutasyon sınaması (ağsız)

Bağımsız denetim bataryası 66 sınamadır (B1 kapı, B2 kademe, B3 körlük, B4 kesin kod ve deneme, B5 aygıt, B6 sahte
boru hattı: eksikken `say`, yeniden deneme, yatay kural, Z oranı ve boşluk, tek koşu, G0'ın bağımsız yeniden hesabı;
B7 aşama H: 5 gün yolu, 2 gün aralığı, en çok üç ölçüm, hız hesabı, dolu < 30; B8 `_akit` zaman aşımı; B9 seçim).
Düzeltilmiş betikte hepsi geçiyor. Özgün betikte B8'in iki sınaması (zaman aşımı ve tavanda kesik sayma) kalıyor (Ö1).

Her mutant için `kuru` (sha256 aynı mı), prova (sha256 aynı mı) ve batarya koşuldu.

| Mutant | kuru | prova | batarya |
|---|---|---|---|
| M00 değişmemiş | geçti | geçti | geçti |
| M01 kapı eşiği 10 → 9 | yakaladı | yakaladı | yakaladı |
| M02 kapı arası 3 → 2 yıl | yakaladı | yakaladı | yakaladı |
| M03 kapı `>=` → `>` | yakaladı | yakaladı | yakaladı |
| M04 temsilci kuralı yok (KAVV aday) | yakaladı (durdu) | yakaladı | yakaladı |
| M05 yer yerine istasyon sayılır | – | – | – (**eşdeğer**; KAVV aday değil) |
| M06 yatay: bilgili dilim şartı yok | – | – | yakaladı |
| M07 yatay: koşulsuz (TR-5b sürüm 2 kuralı) | – | yakaladı | yakaladı |
| M08 kesin kodlardan 404 çıkar | – | – | yakaladı |
| M09 kesin kodlara 500 eklenir | – | yakaladı | yakaladı |
| M10 yoklama deneme sınırı 2 → 3 | – | yakaladı | yakaladı |
| M11 üstveri deneme sınırı 2 → 3 | – | yakaladı | – |
| M12 SON_ISTEK 2026-12-31 | – | yakaladı | yakaladı |
| M13 `kor_denet` SON_ISTEK sınamasını atlar | – | – | yakaladı |
| M14 kademe A eşiği 7 → 8 gün | – | – | yakaladı |
| M15 kademe C eşiği 21 → 22 gün | – | – | yakaladı |
| M16 kademe C'de V_D yerine V_C | – | – | yakaladı |
| M17 ertelendi sınırı 5 → 6 gün | – | – | yakaladı |
| M18 medyan → ortalama | – | – | yakaladı |
| M19 ölçümler arası 2 → 1 gün | – | – | yakaladı |
| M20 eksikken `say`: istek eksiği yok sayılır | – | yakaladı | yakaladı |
| M21 Z dolu oranı 0,80 → 0,75 | – | – | yakaladı |
| M22 sayımdan sonra `yokla` koruması yok | – | yakaladı | yakaladı |
| M23 aşama H 60 sn zaman aşımı (Ek 1 öncesi) | – | – | yakaladı |
| M24 aygıt kuralı kapalı | – | – | yakaladı |
| M25 aday kümesine `ana_T` dışı pencereler | yakaladı (durdu) | yakaladı | yakaladı |
| M26 dolu < 30 koruması yok | – | – | yakaladı |

25 / 25 eşdeğer olmayan mutant yakalandı. Yazarın prova ve `kuru`su tek başına 12'sini yakalıyor. Kademe eşikleri, 5 gün
sınırı, aygıt kuralı ve 404'ün kesinliği yalnız bataryayla yakalanıyor. Bu, provanın bir kusuru değildir: prova
sürdürmeyi gösterir, kuralları sınamaz. Batarya bu inceleme için yazıldı ve depoya konmadı.

## 6. Yeniden üretim ve sha256'lar

| Dosya | Önce | Sonra |
|---|---|---|
| `tr4_asama0.py` | `e5d8c33cdeb824b5103cf27f27436d1c1b7260b16684883e99078dfd3aa8c550` | `183aafd9d9fca43a7f312cb54d987040c63bd57f3de2eeed951faa74dfd80297` |
| `tr4_asama0_kuru.json` | `ecbde36cb4782261e9a0979cf519c444fdcb56fa6655471c2e89d6064e6969e3` | aynı (iki koşuda) |
| `tr4_asama0_prova.py` | `6ce012b7e41a9667fdc91d91e32878e62059ff24328552ea65993791c8b631da` | değişmedi |
| `tr4_asama0_prova.json` | `42adc1af54b85df15161028f9a23efb3fd7125155af7b913e76464f997ee90ae` | aynı (özgün betikle bir, düzeltilmiş betikle iki koşu) |

Prova, sahte `_akit` kullandığı için Ö1 ve K1'i görmez. Ö2'nin denetimi seçimi değiştirmez. Bu yüzden iki çıktı
bit düzeyinde aynıdır. Aşama 0'ı koşturma komutları (ön kayıt Ek bölümü) **değişmedi**.
