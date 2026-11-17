# TR-7c kodlayıcı okumaları: koşu kodu, yapay sınama, m_f ve Tohoku duman sınaması

Tarih: 17 Kasım 2026.

Kapsam: `TR-7c_tetiklenmis-tremor_ONKAYIT.md`'nin iki adımı:
- §10 adım 2: kod yalnız yapay veride; m_f ölçümü (D-4);
- §10 adım 3: Tohoku duman sınaması (§9, Z7).

Değiştirilmeyenler:
- Karar metni (KARAR METNİ DONDURULDU, commit bd3c93a): değiştirilmedi.
- TR-7, TR-7b ve inceleme dosyaları: değiştirilmedi.
- `kayit/turetme/tr13d/`: dokunulmadı.

## Körlük

- Kör Parkfield olaylarının (10 P, 29 N birimi, 2 bilgi olayı) W/R pencerelerinde hiçbir dalga formu istenmedi ya da
  açılmadı. Marmara'da da istenmedi, açılmadı.
- Hiçbir ağ isteği yapılmadı. Üstveri isteği de yapılmadı.
- Okunan tek gerçek veri TR-7'nin Tohoku geliştirme zarflarıdır:
  - konum: `/mnt/project-files/turetme/tr7-zarf/zarf/pk_tohoku/`;
  - 13 dosya: kullanılan 12 istasyon ve BK.PKD;
  - sha256'ları `tr7_zarf_sha256.jsonl` ile denetlendi.
- Yapay sınama süreci bir denetim kancası (`sys.addaudithook`) kurar. Kanca şunları reddeder:
  - her soket çağrısını;
  - `/mnt/project-files` altındaki her açma girişimini;
  - gerçek çıktı dizinine (`kayit/turetme/tr7c/kosu/`) her yazmayı.
- Kapı sınamalarında kanca ayrıca alt süreçleri ve dizin kurmayı da reddeder.
- Sonuç:
  - Özgün kodun sınamalarında reddedilen girişim sayısı 0'dır.
  - Mutasyonlar sırasında 5 girişim reddedildi: 4 `git ls-files` alt süreci ve 1 `kosu/` dizini kurma girişimi. Hepsi
    kapının kaldırıldığı mutantlardan geldi.
  - Soket girişimi yoktur. `/mnt` açma girişimi yoktur. `kosu/` dizini kurulmadı.

Bu belgede iki tür madde var:
- **O-n:** kodlayıcı okuması. Karar metninin boş bıraktığı ya da birden çok okunabilen yerde kodun yaptığı seçimdir.
- **Karar metni sorunu (KMS-n):** metinde bulunan bir sorundur. Metin değiştirilmedi; sorun yalnız buraya yazıldı.

## 1. Dosyalar ve sha256

Hepsi `kayit/turetme/tr7c/` altında:

| Dosya | sha256 | Ne |
|---|---|---|
| `tr7c_kosu.py` | `345dc176ef5d00ae0e38931bbf0c18da99ef53422e67042a9638f5f10d3c73b3` | Koşu kodu (aşamalar, kapı, kilit, K1c hükmü) |
| `tr7c_mde_ek.py` | `4876dcbee8ce455c221efa4782e4af0047e5ade2f7b84eb985f9eb127873e910` | D-8 MDE ve E-2 k-güç tablosu (koşudan önce donduruldu) |
| `tr7c_mde_ek.json` | `e759176ec28f0b4a9f18fed47bddfe1ed7f43a52fa24ed994c5d2a1d062c3b3d` | Tablonun çıktısı; inc1 hücreleri birebir yeniden üretildi |
| `tr7c_test_yapay.py` | `6267a5b53b0405e0e2c3d4c2f24771a97b9477548e4327b00ac09e26be82fd9f` | Birim, kapı, sha/kilit, uçtan uca sınamaları ve mutasyonlar |
| `tr7c_test_yapay.json` | `837396d4a410f7f45bd294b52591cb6eb0315ba60eb391e7db78508ef5979fc4` | Sınama sonucu |
| `tr7c_mf.py` | `334185a28d3738b58a71b316495f63823cb36fe7543f2d67fe254f70dd120dd2` | D-4 m_f ölçümü |
| `tr7c_mf.json` | `5c014eae0308288002d42b9b2245a5b85eed5c0cf0724d6748b0c8659f3c3fd7` | m_f sonucu |
| `tr7c_duman.py` | `d974586836bc5e028a26ef84045cd0592b14e01e5d68e9bf63afc6d6bd5c2515` | §9 Tohoku duman sınaması |
| `tr7c_duman.json` | `11aaa0a04ac4ce562e1f271a4ea20e0cbd334e3330a5f2b7e3d95270e085acb6` | Duman sonucu |
| `tr7c_tr7b112.py` | `8d19f035c329cc90b619058c5e55cb1a927a999128843a64f3a913bbdda35dda` | TR-7b §11.2 satırları, koşu kodunun yolundan |
| `tr7c_tr7b112_20261117.json`, `_9393.json` | §6'da | Sonuç (iki tohum) |
| `tr7c_kd_k5.py` | `77aeab9951972d7cc2580bd8e6fab95f8dc96dfa67218c8aea998b2076fc2a64` | TR-7 KD'si, K5 ile (kısaltılmış) |
| `tr7c_kd_k5.json` | §6'da | KD sonucu |

Doğrulanan girdiler:
- **D-2 dosyaları** (modül yüklenirken denetlenir; üçü de uyuşuyor):

  | Dosya | sha256 başı |
  |---|---|
  | `tr7b_yapay2.py` | ae995ba8… |
  | `tr7b_yapay.py` | e9271531… |
  | `tr7_cekirdek.py` | 4a1b9131… |

- **Repo girdileri** (kapı ve `k1c_kos` denetler):

  | Dosya | sha256 başı |
  |---|---|
  | `tr7b_sayim.json` | 55318360… |
  | `tr7c_ustveri.json` | ed8cf3c6… |
  | `tr7_parkfield_liste.csv` | 9dca3380… |
  | `inc1/tr7c_inc1.json` | 4974dbe6… |
  | `tr7c_mde_ek.json` | e759176e… |

- **Karar metni §0–§6 gövdesi:** "\n## 0. " ile "\n## 7. " arası, sha256 `8761573150be…69f18`. Bu, bd3c93a'daki metinle
  aynıdır.

Koşulan sürümler:
- `tr7c_mf.py`, `tr7c_kosu.py`'nin bir önceki hâliyle koşuldu. Aradaki tek fark, `GercekKaynak.pencere`'ye eklenen
  `ref_W` satırıdır (O-18). Bu satır gerçek veri katmanındadır, m_f hesabına girmez. json'daki `tr7c_kosu.py` sha'sı
  koşu sonunda okunduğu için güncel değeri gösterir.
- Öteki bütün sonuçlar tabloda yazılı `tr7c_kosu.py` sha'sıyla koşuldu.

## 2. Koşu kodunun yapısı

`tr7c_kosu.py`:

- **D-2:** modül yüklenirken, K5 içe aktarılmadan ÖNCE çalışır. Bir sha uyuşmazsa modül yüklenmez. Bu bir alt süreç
  sınamasıyla gösterildi.
- **Gerçek kip kapısı (`gercek_kapi`)** gerçek veriye dokunan her yolun ilk satırındadır:
  - `GercekOrtam` (kurucu, `zyol`, `hyol`, `istemci`);
  - `GercekKaynak` (kurucu ve bütün okuma işlevleri);
  - bütün `asama_*` işlevleri, `lp_adaylari_manifest`, `lp_indir`;
  - `marmara_kos`;
  - `k1c_kos`: gerçek kaynak, gerçek dizin ya da `gercek=True` verilirse;
  - komut satırının `kos`, `baslat` ve `marmara` komutları.

  İşlev içe aktarılarak çağrılsa da kapı işler.

  Kapının açılması için hepsi gerekir:
  1. Ön kaydın "Durum:" satırında "KOŞU DONDURULDU" yazmalı.
  2. `tr7c_kosu.py` ve `tr7c_mde_ek.py`'nin sha256'ları ön kayıt metninde geçmeli.
  3. §0–§6 gövdesi dondurulmuş hâliyle aynı olmalı.
  4. D-2 dosyaları uyuşmalı.
  5. Repo girdileri uyuşmalı.

  **Bugün kapı KAPALIDIR.** Neden: Durum satırında "KOŞU DONDURULDU" yok. Bu bir sınamayla gösterildi; komut satırında
  `kapi` komutu da aynı sonucu verir.
- **Aşamalar:**
  1. `manifest`: ComCat tetikleyici kaydı ve derinlik; negatif kaydırmalar; TR-7 manifest motoru; E-1 adayları.
  2. `K1c-indirme`: TR-7'nin indir–zarfla–sil motoru ve E-1 uzun periyot indirmesi.
  3. `K1c-negatif`.
  4. `K1c-algılama`, `k1c_kos` içinde şu sırayla:
     - negatifler;
     - algılama: önce 29 N, sonra 10 P, sonra 2 bilgi;
     - modülasyon;
     - Z3/Z4;
     - hüküm dosyası `tr7c_k1c_hukum.json` bir kez, "x" kipinde yazılır.

  Durum dosyası yalnız şunları taşır: durum, zaman ve dosya sha256'ları (Ö-b).
- **Marmara** ayrı bir komuttur. Sırası: kapı, sonra hüküm dosyası var mı, sonra dal (b) mi. Bu sürümde (b) olsa da
  durur, çünkü bağlantı yazılmadı (O-30).

## 3. Okumalar ve seçimler (O-n)

Numaralar koddaki atıflarla aynıdır (`tr7c_kosu.py`: O-3, O-8, O-12, O-17, O-30, O-35, O-37; `tr7c_mf.py`: O-40;
`tr7c_kd_k5.py`: O-41). Bu yüzden bölümler içinde sıra atlar.

### Girdi ve birimler

- **O-1 Kapı belirteci.** Kapı "Durum:" satırında "KOŞU DONDURULDU" arar. Bkz. KMS-1.
- **O-2 Gövde sha'sı.** Yalnız §0–§6 sha'lanır. §7 ve sonrası, D-3 ve D-5 gereği koşudan önce sayıca değişebilir.
- **O-3 Repo girdileri.** Yalnız okunur; sha256'ları `GIRDI`'de sabittir ve `girdi_denetimi` ile denetlenir: `tr7b_sayim.json`, `tr7c_ustveri.json`, `tr7_parkfield_liste.csv`, `inc1/tr7c_inc1.json`, `tr7c_mde_ek.json`. Biri uyuşmazsa koşu durur.
- **O-4 Birimler (Z2, D-1).** Kaynak `tr7b_sayim.json`'dur; Tohoku dışarıda kalır. Sınıflar:
  - P: 10 olay.
  - N: Q_CC = 0 olan 30 olay, 29 birim.
  - B (bilgi): Kunlun 2001 ve Tonga 2006.

  Vanuatu birimi:
  - adı `VANUATU2009` (N27 + N28);
  - T0'ı ilk olayınki;
  - PGV_T'si iki olayın en büyüğü;
  - K1b'si USTVERI'nin dondurulmuş birleşik aralığı.
- **O-5 "Taranan" (Z2).** İki şart birlikte aranır:
  - pencere TR-7 `ws_kur` ile "tarandi" çıkmalı (≥ 3 liste istasyonu, TR-7 §4.2 örtüsü);
  - USTVERI'de dondurulmuş K1b açık payı ≥ 0,50 olmalı.

  n_P ve n_N koşuda sayılır.
- **O-6 İndirilecek istasyonlar.** TR-7'nin motoru `p['ist']`'teki bütün istasyonları indirir; 12 sınırı indirmeden sonra
  uygulanır. Bu yüzden TR-7c, pencere başına SAYIM'ın bütün liste istasyonlarını (34–52) indirir. Hacim için bkz. §8.
- **O-7 Tetikleyici eşlemesi (Ö-k).** Tetikleyici, ±60 sn içinde M ≥ 7,0 olan en yakın ComCat kaydıdır. Bulunamazsa
  koşu durur (Tr7cDur); "veri yok" yazılmaz.
- **O-8 2–8 Hz kanalı.** `z_kanal` liste istasyonları için `tr7b_sayim.json`'daki kanallardan seçilir. Şart: W ve R örtüsü
  ≥ 0,90. Öncelik HHZ > BHZ > EHZ > SHZ (TR-7 §3.2'nin okunuşu). Kod incelemesi bunu TR-7'nin kendi seçimiyle
  karşılaştırmalıdır.
- **O-35 K1b.** USTVERI'de dondurulmuş epoch değerleri kullanılır. Uç kapsayıcıdır: I′ = [a, b) ile [c, d], a ≤ d ve
  b > c ise kesişir.

### K5, Q, negatifler ve MDA

- **O-9 Q.** Q = [⌊T0 + t_P⌋, Wb başı).
  - t_P: iz ortası, iasp91, ComCat derinliği.
  - Wb: penceredeki istasyon W'lerinin birleşimi. "W başı" Wb'nin başı okunur.
  - Bkz. KMS-4.
- **O-10 Fisher.** Yazarın seçimi 1 aynen uygulanır (`tr7c_guc.py` `fisher_tek` ile birebir).
- **O-11 Negatifler.**
  - Seçim TR-7 §7.3 kuralıyla yapılır; `tr7_negatif_pencere.sec` ile birebir sınandı.
  - Üreteç `default_rng(20261116 + 1)`; olaylar T0 sırasıyla; tek akış.
  - Olaylar: 10 P + Macquarie 2004 + Peru 2007, olay başına 10 pencere.
  - N_PK = taranan pencereler, en çok 120.
  - f_PK = W'nin herhangi bir yerinde algılama veren negatif sayısı.
- **O-12 X_min.** TR-7 §8 tanımı K2 kapısı OLMADAN kullanılır, INCELEME-1'in ızgarasıyla aynı. Bkz. KMS-5.
- **O-17 MDA.**
  - Yalnız W'de algılama vermeyen negatiflerde, pencere başına 3 başlangıçla.
  - Üreteç `default_rng(20261112 + 2)`; negatifler sırasıyla tek akış; sürdürülebilir.
  - MDA'nın kendi algılaması da K5 ile yapılır: `k5_mda_baglami`, `K.ayikla`'yı geçici olarak `ayikla_k5`'e bağlar.
    Dosya değişmez; bağlam bitince eski hâline döner, bu sınandı.

### Modülasyon

- **O-13 Sıra.** Modülasyon bütün algılamadan sonra hesaplanır.
  - Üreteç `default_rng(20261112 + 3)` ile yeni bir örnekle başlar ve tek akıştır.
  - Birimler P ve N birlikte, T0 sırasıyla; birim içinde I′ başı sırasıyla işlenir.
  - Yalnız algılama kümeleri ölçülür: sağ çıkan ve K1b ile kesişen kümeler.
  - Bilgi birimleri (B) ölçülmez.
  - Bkz. KMS-2.
- **O-14 E-1 aynen uygulanır.**
  - Adaylar: penceredeki liste istasyonları.
  - Kanal şartı: düşey, bant B/H, alet H; olay epokunda |H(0,02)|/|H(1)| ≥ 0,5.
  - Örtü: indirilen veride W ve R ≥ %90. Ölçüt: işleme zincirinde düşme yok.
  - Seçim: en yakın istasyon, önce HH.
  - Yataylar TR-7 `yatay_sec` ile alınır. vR ya da vT yoksa yalnız Z kullanılır.
  - İndirme: adaylar uzaklık sırasıyla denenir, ilk uygun istasyon bulununca durulur.
- **O-15 E-1 kanalı, D-9'un 4 N olayı.** Bu 4 olayda da E-1 aynı kuralla uygulanır. Kod 29 N biriminin hepsi için E-1
  uygular ve hepsinin p'sini bilgi olarak yazar (Ö: m_f'nin kaba göstergesi).
- **O-16 Ölçülebilir olay (§5 madde 4).** Başvurusu olan ve en az bir algılama kümesi için M hesaplanan olaydır.
  M_ölç = bu P olaylarının sayısı. M_mod = en az bir kümesi p ≤ 0,01 olan P olaylarının sayısı.
- **O-18 Başvurunun W'si.** Başvuru istasyonunun KENDİ W'si alınır (TR-7 `eksen_dilim`, TR-7 §6.4 aynen). Yapay
  sınamada Wb kullanılır.
- **O-23 k_koşu (E-2).** k_koşu = başvuru kanalı bulunan P olayı sayısı (10 üzerinden). n_P içindeki k ayrıca bilgi
  olarak yazılır. Güç değeri dondurulmuş tablodan okunur (işlevin varsayılanları: n_P 10, n_N 30).

### Etiketler ve cümleler

- **O-19 D-8.** MDE değerleri `tr7c_inc1.json`'dan okunur; orada olmayan n'ler için `tr7c_mde_ek.json`'dan. Kapsam:
  n_P 8…10, n_N 20…29. Dal (a)'da ek yoktur.
- **O-20 (b′).** TR-7 §7.2 uygulanır. Kümenin I′ başı şu iki aralıktan birine düşerse küme (b′) durumundadır:
  - E1 bireysel sonundan sonraki 0–5 sn;
  - bir çekirdek fazına −10…+120 sn (iasp91, ComCat derinliği).

  Algılama veren P olaylarının hepsinde bütün algılama kümeleri bu durumdaysa "geçti, belirsiz" yazılır.
- **O-21 A_PK.** TR-7 §7.5 kestiricisi kullanılır: ×r_hiposantr/25 ve ×1e9 nm/s (`tr7_kosu` ile aynı). İki bilgi satırı
  ayrıca yazılır (Ö-a):
  - yalnız modülasyonlu kümelerden A_PK;
  - olay başına medyan kümeden A_PK.
- **O-22 ŝ ve ŝ_alt (Ö-e).** ŝ = max(0, (X_P/n_P − q)/(1 − q)). ŝ_alt aynı formülde X_P/n_P yerine Clopper–Pearson tek
  yanlı alt sınırı koyar.
- **O-37 D-9 "ölçülemeyen".** Ölçülebilir olay tanımı sağlanmıyorsa olay ölçülemeyen sayılır; algılama kümesi
  olmayan olay da bu sayıya girer. Neden olay başına ayrıca yazılır: "taranmadı", "algılama kümesi yok", "başvuru kanalı
  yok" ya da "M hesaplanamadı". Bkz. KMS-6.
- **O-24 D-10 cümlesi aynen.** VAR şartı: (b), (b′) yok, modülasyon geçti ve D-9 etiketi yok. Bu, `var_verilebilir`'de
  yalnız bilgi olarak hesaplanır; Marmara aşaması yazılmadı.

### Durum, kilit ve tohumlar

- **O-25 Tohumlar.** Hüküm dosyasına yazılır ve sınanır:
  - modülasyon 20261115;
  - MDA 20261114;
  - negatif seçimi 20261117.
- **O-26 Kilit.** Hüküm dosyası varsa `k1c_kos` hiçbir şey hesaplamaz; ayrıca dosya "x" kipinde yazılır.
- **O-27 Algılama satırı.** Olay başına şunları yazar: algılama, küme sayısı, atılma nedenleri, K5 bayrak sayıları,
  "Q doğrusu kuruldu mu" (Ö-h) ve bilgi için TR-7 K0 bayrak sayısı.

### Yazılmayanlar (açık kalanlar)

- **O-28 Kuyu sınıfı.** "Liste sınıfına karşı kuyu sınıfı" bilgi satırı YAZILMADI. Kuyu sınıfı ayrı pencere ve indirme
  ister. Dal değiştirmez, ama karar metninde adı geçen bir bilgi satırıdır. Koşu dondurmasından önce eklenmeli ya da
  açıkça bırakılmalıdır.
- **O-29 N27/N28 ayrı.** "N 27 ve N 28 ayrı sayılarak Z3 (iii)" bilgi satırının hesap yeri kodda var: "Nayri" sınıfı
  satırlarıyla. Ama ayrı pencereleri kuran kod YOK, çünkü ayrı K1b ve W tanımı metinde yok. Bkz. KMS-7.
- **O-30 Marmara bağlantısı yazılmadı.**
  - TR-7 Marmara aşamalarının K5 ve Z6 ile bağlanması YAZILMADI.
  - `marmara_kos` yalnız önkoşulları denetler: kapı ve dal (b). Sonra durur.
  - Z6/D-6 cümlesi saf işlev olarak (`z6_cumle`) yazıldı ve sınandı.
  - K1c (b) çıkarsa ayrı bir kod ve bir kod incelemesi gerekir.
- **O-31 τ_ölç.** Hesaplanmaz; K1c'ye girmez.
- **O-32 Uygulama hatası yolu** (TR-7 §7.2, bir kez, yalnız (d) ya da (e)). Kodda YOK. Kilit ikinci bir hükmü engeller.
  Bkz. KMS-8.
- **O-33 Tohoku duman satırı.** Duman sonucu K1c hüküm dosyasına bilgi satırı olarak girmez; ayrı dosyadadır
  (`tr7c_duman.json`).
- **O-34 Gerçek I/O katmanı sınanmadı.** Şu işlevler sahte bir sunucuyla sınanmadı: `asama_manifest`,
  `lp_adaylari_manifest`, `asama_indirme`, `lp_indir`, `GercekKaynak`. Bu katman TR-7 motorunu (`tr7_kosu`) çağırır;
  kapı yüzünden bugün çalışamaz. Kod incelemesinde satır satır okunmalı. Gerekirse bir yapay sunucu sınaması eklenmeli.

### Sınama betiklerinin okumaları

- **O-36 Yapay sınamada MDA.** Uçtan uca senaryolarda MDA bir taslak işlevdir (A eşiği rastgele); TR-7 `mda_deneme` 100 Hz parça verisi ister. A90 burada yalnız dal mantığını besler.
- **O-38 TR-7b §11.2 karşılaştırması.** `tr7c_tr7b112.py` Tur 2 satırlarını `tr7b_yapay2.main`'deki aynı üreteç çağrılarıyla ve sırayla kurar; algılayıcı rastgele sayı çekmediği için pencereler Tur 2 ile aynıdır, K5 sütunlarının birebir tutması beklenir.
- **O-39 Duman: saf P kümesinin başvuru W'si.** Saf P kümesi gerçek W'nin dışında olduğundan modülasyonu için başvuru W'si sahte P aralığı alındı (Ö-c).
- **O-40 m_f yöntemi (D-4).** TR-7b Y2 (18 hücre) ve Y3 (3 hücre), hücre başına 20 pencere, 3 istasyon. "Ayıklamadan önce algılanan küme" = TR-7 §6.3 tutarlı küme, I′ W'nin herhangi bir yerinde. Başvuru hızı: üç bağımsız dar bantlı (15–30 sn) Gauss dizisi. Ölçü `modulasyon_kume`, 1000 kaydırma. Üreteçler `default_rng(20261119)` (pencereler) ve `default_rng(20261120)` (hız, kaydırma).
- **O-41 KD'de Q.** KD pencerelerinde tetikleyici yoktur; Q = ∅ alınır (K5'in "doğru kurulamazsa a = b = 0" kolu; yalnız ρ kolu çalışır). `tr7_cekirdek.ayikla` yalnız o süreçte sarmalanır: 'sizinti' bayrağı `ayikla_k5` sonucuyla değiştirilir. Bkz. KMS-9.

## 4. Karar metni sorunları (metin değiştirilmedi)

- **KMS-1: Koşu dondurmasının belirteci.** §10 madde 5 "Durum: DONDURULDU …" der. Bugünkü satır "KARAR METNİ
  DONDURULDU" diye başlar. Yalnız "DONDURULDU"ya bakan bir kapı bugün açık olurdu. Kod "KOŞU DONDURULDU" arar (görev
  tanımı). Koşu dondurması bu belirteci kullanmalı ya da metin belirteci açıkça yazmalı.
- **KMS-2: Modülasyon üreteç sırası.** §4.1 "kümeler olaylar T0 sırasıyla" der. D-9 "bu 4 olayın kümeleri N olaylarıyla
  birlikte, T0 sırasıyla" der. Metin şunları söylemiyor:
  - Akışa yalnız P mi girer, P + 4 N mi, yoksa P + 29 N mi?
  - P ve N iç içe mi işlenir, art arda mı?

  Kod P ile 29 N'nin hepsini T0 sırasıyla tek akışta işler (O-13). P p'lerinin kesin değeri bu seçime bağlıdır;
  dağılımı bağlı değildir.
- **KMS-3: Modülasyonun zamanı.** §10 madde 6 algılama sırasını verir. Modülasyonun algılamadan sonra mı, olay olay mı
  hesaplanacağını söylemez. Kod algılamadan sonra hesaplar (O-13).
- **KMS-4: Q'nun bitişi.** "Q = [T0 + t_P, W başı)" der. W istasyon başınadır, K5 de istasyon başına çalışır; hangi W'nin
  başı olduğu yazılı değil. Kod pencere birleşiminin (Wb) başını alır.
- **KMS-5: X_min ve K2.** Z3 (i) "TR-7 §8 tanımı" der. TR-7'nin `x_min`'i K2 kapısı taşır: f > ⌊0,05 N⌋ ise 'K2' döner.
  Bu, (ii)'nin 0,30 tavanıyla çelişir; FAR 0,05–0,30 arasında (i) hiç sağlanamazdı. INCELEME-1'in ızgarası K2'siz
  hesapladı; kod da öyle yapar (O-12).
- **KMS-6: D-9'da "ölçülemeyen".** Algılama kümesi hiç olmayan olay "modülasyonu ölçülemeyen" sayılır mı, metin
  söylemiyor. Kod sayar ve nedeni ayrıca yazar (O-37). Sonuç: yapay "gerçek tremor" senaryosunda satır "ölçülemeyen: 4"
  der, çünkü 4 olayda algılama yoktur.
- **KMS-7: N27/N28 ayrı bilgi satırı.** Bu satır ayrı K1b'ler, ayrı W'ler ve ayrı E1 maskesi ister. D-1 ve USTVERI
  yalnız birleşik birimi dondurdu. Ayrı tanım metinde yok (O-29).
- **KMS-8: Uygulama hatası yolu ile tek hüküm.** §6.1 TR-7 §7.2'nin yolunu "bir kez, yalnız (d)/(e)" diye tutar. §10
  madde 6 hüküm dosyasının bir kez yazılmasını ister. E-2 "örtü eksikliği uygulama hatası sayılmaz" der. Yolun TR-7c'deki
  yordamı yazılı değil: hangi dosya, ikinci hüküm, kilidin kaldırılması. Kodda yok (O-32).
- **KMS-9: KD'de Q.** §10 adım 2 "TR-7'nin KD'si K5 ile koşulur" der. KD pencerelerinde tetikleyici ve Q yoktur. K5'in
  kalıntı kolu orada tanımsızdır; yalnız ρ kolu işler. Kod Q = ∅ alır (O-41).
- **KMS-10: Kuyu sınıfı bilgi satırı.** Satır, karar metninde ayrı pencere ve indirme gerektirdiği yazılmadan geçer.
  Hacim tahminine girmedi (O-28).

## 5. Yapay sınama sonuçları (`tr7c_test_yapay.json`)

**100 sınamanın 100'ü geçti.** Toplam süre 996 sn; mutasyonlar dışındaki ana bölüm 108 sn.

| Grup | Sınama | Geçen |
|---|---|---|
| Birim | 49 | 49 |
| Kapı | 27 | 27 |
| sha/kilit | 9 | 9 |
| Uçtan uca | 15 | 15 |

### Birim sınamaları

- **Dal ızgarası.** Kodun `k1c_dal`'ı, metinden ayrıca yazılmış bir başvuruyla karşılaştırıldı. Başvurunun hesapları:
  scipy ile X_min, kesin kesirle Fisher.
  - Taranan uzay: n_P 0–10 × n_N 0–29 × bütün X_P, X_N × (M_ölç, M_mod) × 9 (f_PK, N_PK, A90) birleşimi.
  - 2 971 350 noktada 0 uyuşmazlık. Marmara yalnız (b)'de açılıyor.
  - Dal sayıları:

    | Dal | Nokta |
    |---|---|
    | (a) | 1 936 305 |
    | (b) | 79 185 |
    | (c) | 284 190 |
    | (d) | 518 670 |
    | (e) | 153 000 |

  - Ayrıca D-7 örneği ve sınır durumları sınandı.
- **İstatistik:**
  - Fisher üç ayrı yolla aynı: kesin hipergeometrik, `tr7c_guc.py`, yön denetimi.
  - X_min (K2'siz), CP alt sınırı ve ŝ.
- **D-1:** 10 P / 29 N / 2 B birimi; Vanuatu tek birim; D-9 genlik bayrağı 4 birimde.
- **E-1:** 6 durum. En yakın istasyon önce; HH önce; HH'nin örtüsü kalırsa BH; uygunsuz kanallar dışlanır; yatay yoksa
  yalnız Z; uygun kanal yoksa None.
- **E-2:** k_koşu 10'da güç satırı yok; 6'da var. Tablo değerleri inc1 ile aynı.
- **Cümleler:** D-8 eki (c/d/e), Ö-d, D-10, (b′), D-9, VAR şartları; Z6/D-6 (oran > 1, n_açık, belirsiz A90).
- **K5:**
  - K5 istasyon ve küme düzeyinde `tr7b_yapay2.K5` ile birebir.
  - Örnek ayırt edicidir: K0 ile K5'in ayrıldığı istasyonlar ve K5'in bayrakladığı istasyonlar var.
  - MDA bağlamı K5'i kullanıyor.
  - Negatif seçimi TR-7 ile birebir.
  - Modülasyon sayımında p ≤ 0,01 eşiği ve ölçülebilir olay tanımı doğru.

### Kapı, sha ve kilit

- **Kapı bugün kapalı.** 17 gerçek giriş noktası, işlev içe aktarılarak çağrıldığında kendi işlem adıyla reddeder.
- **Kapı geçici bir kopyada açılır.** Ön kaydın bir kopyasında Durum satırı ve sha'lar yazılınca kapı açılıyor. Şu üç
  durumda kapanıyor:
  - gövde bir boşlukla değişirse;
  - sha eksikse;
  - belirteç Durum satırında değil de metnin başka yerindeyse.
- **Marmara önkoşulu:** (a), (c), (d), (e) → "(b) dışında Marmara verisi indirilmez".
- **D-2:**
  - değişmiş dosya durdurur;
  - alt süreç sınamasında modül hiç yüklenmez;
  - repo girdisi uyuşmazsa durur.
- **Kilit:** ikinci koşu hiçbir şey hesaplamıyor. "x" kipi üzerine yazmayı engelliyor. Durum dosyası Ö-b'ye uygun.
- **Komut satırı:** `kos manifest` → "GERÇEK KİP REDDEDİLDİ".

### Uçtan uca senaryolar

Kurulum:
- Bellekte TR-7b üreteçleriyle (değiştirilmeden) kurulan pencereler; 4 istasyon; 12 negatif.
- Modülasyon `mod_n` 100 ile; 100 kaydırmayla en küçük p 1/101'dir.
- Tremor, dar bantlı bir başvuru hızının (15–30 sn) fazına kilitli. Bütün P ve N'de K0'ın attığı ama K5'in atmadığı bir
  telesismik sızıntı var (TR-7b Y1: a_y 5, κ 12,5).

| Senaryo | Sonuç | Beklenen |
|---|---|---|
| Gerçek tremor (8/10 P kilitli, N'de yok) | (b) "ölçü sınandı"; X_P 8/10, X_N 0/29, M_mod 8; Marmara açık; VAR verilebilir | ✓ |
| Ayırt etmeyen algılayıcı (P ve N'de aynı tremor) | (c), kalan (iii); X_P 10/10, X_N 29/29 | ✓ |
| Genliğe bağlı, kilitsiz 2–8 Hz sızıntı (K5'ten geçer; A ∝ PGV_T) | (c), kalan (iii) ve (iv); 40 kümenin 39'u sağ çıktı, M_mod 0 | ✓ (b değil; (iv) kırar) |
| Telesismik koda sızıntısı (TR-7b Y2 sabit, a_y ∝ PGV_T) | (d); 65 kümenin 65'i K5 ile atıldı | ✓ |
| Veri yok | (a) "Parkfield verisi yok" | ✓ |
| D-9 (Peru 2007 N'de kilitli tremor) | (b) + "genlik karıştırıcısı dışlanmadı"; VAR verilemez | ✓ |
| E-2, k_koşu 4 | (e) "modülasyon ölçülemedi"; koşu sürdü, n_P aynı; güç bilgisi 0,41 / 0,13 yazıldı | ✓ |
| E-2, k_koşu 1 | (e) "modülasyon ölçülemedi" | ✓ |
| (b′), hepsi | (b) + "geçti, belirsiz" | ✓ |
| (b′), yalnız 3 P | etiket yok | ✓ |
| Kilitsiz tremor P'de | (c), kalan (iv) | ✓ |

Ek uçtan uca sınamalar:
- algılama sırası N, P, B;
- belirlenimcilik;
- tohumlar hüküm dosyasında;
- negatif turunun yarıda kesilip sürdürülmesi aynı MDA çekilişlerini veriyor.

### Mutasyonlar: 34, hepsi yakalandı

Her mutasyon `tr7c_kosu.py` kaynağında tek bir dize değişikliğidir. Mutant bir modül olarak yüklenir ve bütün sınama
takımı onun üzerinde koşar. Izgara burada küçük tutulur (63 342 nokta).

Listede §10 adım 2'nin bütün örnekleri var:
- Fisher yönü ters;
- (iv) "≥ 1";
- (a) eşiği n_N < 2;
- (b) dışında Marmara;
- Vanuatu iki kez;
- D-7 kaldırılır;
- D-9 VAR'ı engellemez.

Ötekiler:
- K5 yerine K0; K5 hiç bayraklamaz;
- K1b'de bir saniye kayma;
- E-1: önce BH, en uzak istasyon, örtü şartı yok;
- kod sha denetimi, gövde denetimi ve D-2 karşılaştırması atlanır;
- kilit atlanır;
- kapı tümden kaldırılır; GercekOrtam, k1c_kos ve asama_kos'ta tek tek kaldırılır;
- modülasyon eşiği 0,05; modülasyon tohumu farklı;
- X_min yok sayılır; N_PK < 5 kuralı yok;
- ŝ ham alınır;
- D-10, (b′), D-8 eki ve E-2 güç satırı yazılmaz;
- algılama sırası ters;
- ölçülebilir olay için başvuru yeterli sayılır;
- D-9'u ölçülemeyen olay tetikler;
- (b′) için tek olay yeter.

Dürüst not:
- **İlk tam koşuda 34 mutasyonun 29'u yakalandı.** Yakalanmayan 5 mutasyon:
  - E-1 örtü şartı yok;
  - X_min yok sayılır;
  - N_PK < 5 kuralı yok;
  - ölçülebilir olay için başvuru yeterli;
  - (b′) için tek olay yeter.
- Kod değil sınamalar güçlendirildi:
  - E-1 sınamasında örtüsü kalan kanala da hız verildi;
  - küçük ızgaraya iki (f_PK, N_PK) birleşimi eklendi: (30, 120) ve (0, 4);
  - "başvuru var, M yok" durumu eklendi;
  - kısmi (b′) senaryosu eklendi.

  İkinci tam koşuda 34'ün 34'ü yakalandı.
- "Kilit atlanır" mutantını davranış sınaması değil, ikinci güvence yakaladı. Hüküm dosyası "x" kipinde yazıldığı için
  ikinci yazım FileExistsError ile çöktü.

### Yapay sınamanın sınırları

- **MDA bir taslak işlevle üretildi.** TR-7 `mda_deneme` 100 Hz parça verisi ister. Taslak, A eşiğini rastgele çeker.
  MDA'nın K5'e bağlanması ayrıca birim sınamasıyla gösterildi.
- **Gerçek I/O katmanı sınanmadı** (O-34).

## 6. TR-7b §11.2 satırları ve TR-7 KD'si (K5 ile)

- **TR-7b §11.2 satırları** koşu kodunun yolundan geçirildi: `pencere_algila_k5` → `ayikla_k5` → `k5_ist`. Tohumlar
  20261117 ve 9393, n 100. Sonuç: <<T112>>.
- **TR-7 KD'si (§7.1) K5 ile:** <<KD>>.

## 7. m_f (D-4; `tr7c_mf.json`)

**Ölçülen m_f = 8/326 = 0,025.** Clopper–Pearson tek yanlı %95 üst sınırı 0,044. **≤ 0,10**: D-4 eşiği aşılmadı.

Yöntem:
- 21 hücre (TR-7b Y2: 18; Y3: 3), hücre başına 20 pencere.
- Ölçülen kümeler: ayıklamadan önce algılanan bütün tutarlı kümeler. Toplam 326.
- Ölçü TR-7 §6.4, 1000 kaydırma.

| | Küme | p ≤ 0,01 | m_f | CP üst |
|---|---|---|---|---|
| Y2 | 264 | 8 | 0,030 | 0,054 |
| Y3 | 62 | 0 | 0,000 | 0,047 |
| Toplam | 326 | 8 | 0,025 | 0,044 |

Notlar:
- **K5'ten sağ kalan pay:** 326 kümenin hiçbiri ayıklamadan sağ çıkmadı. Bu yüzden sağ kalanlardaki m_f
  tanımsızdır. Bu, Tur 2'nin "K5_sag 0" sonucuyla tutarlıdır.
- **Y2 'egim' hücrelerinde küme azdır:** 9 hücreden yalnız 3'ünde küme var, toplam 17. Kümelerin çoğu 'sabit' hücrelerden
  ve Y3'ten gelir.
- **Kapsam (D-4, aynen):** Bu ölçüm yalnız yüzey dalgasına KİLİTLİ OLMAYAN sızıntıyı kapsar. Y2/Y3 zarflarında yüzey
  dalgası periyodu yoktur. Başvuru hızı sızıntıdan bağımsız, dar bantlı (15–30 sn), üç bileşenlidir. Kilitli sızıntının
  m_f'si 0 € ile ölçülemez; doğrulanamadı. Tanım gereği ≈ 1'dir (`tr7c_inc1.json` `kilitli_sizinti`).
- **Gerçek veride kaba gösterge:** Duman sınamasında saf P kümesinin p'si 0,28 çıktı (§8). Bu tek gözlemdir.

## 8. Tohoku duman sınaması (§9, Z7; `tr7c_duman.json`)

**Sonuç: kod çalıştı.**
- 13 zarf dosyasının sha256'sı TR-7 kaydıyla uyuştu.
- Çağrılan koşu kodu işlevleri: `pencere_sonucu`, `e1_secim`, `modulasyon_kume`.
- Süre 25 sn. Yeni indirme yok.

Girdiler `tr7b_gelistirme.py` ile aynıdır:
- maske: yalnız E1, birim PARKFIELD;
- R: T0 − 3600;
- Q: [05:57:53, 06:13:29);
- Wb: 06:13:29–06:45:15.

| Küme (I′, UTC) | İstasyon | K5 bayraklı ist. | K0 bayraklı ist. (bilgi) | Darbe | K5 | Taban | Sağ | M | p |
|---|---|---|---|---|---|---|---|---|---|
| 06:13:29–06:17:29 | 10 | 0 | 9 | – | – | – | **sağ** | 0,128 | 0,18 |
| 06:20:57–06:23:51 | 10 | 1 | 10 | – | – | – | **sağ** | 0,248 | 0,083 |
| 06:25:35–06:26:37 | 7 | 2 | 7 | – | – | – | **sağ** | 0,617 | 0,18 |
| 06:41:38–06:45:09 | 9 | 3 | 9 | – | – | taban | atıldı | 0,256 | 0,22 |
| Saf P, 05:57:43–06:05:57 (sahte W) | 10 | 4 | 10 | – | – | – | **sağ** | 0,080 | 0,28 |

Okunuş:
- **K5, beş kümenin hiçbirini sızıntı diye atmadı.**
- **W'de sağ kalan küme 3, saf P aralığında 1.** TR-7'de K0 ile bu kümelerin hepsi atılmıştı.
- **I′ eşleşmesi.** Dört W kümesinin I′'ları TR-7 K1'inkilerle eşleşiyor. Tek fark: son kümenin sonu 06:45:09, TR-7'de
  06:45:08. Fark `tr7b_gelistirme.json` ile birebir aynıdır, yani TR-7b'de zaten vardı.
- **Q doğrusu.** W'de 12 istasyonun 11'inde kuruldu. Saf P sahte penceresinde Q boştur (Q = [T0 + t_P, sahte W başı));
  orada yalnız ρ kolu işler.
- **Modülasyon.** Başvuru BK.PKD; 3 bileşen; iz ortasına 8 km; E-1 kuralıyla seçildi. Kanal kodu TR-7 kaydında yok;
  HHZ varsayıldı. Hiçbir kümede p ≤ 0,01 yok.
  - Saf P kümesinde p = 0,28. Ö-c'nin önceden yazılı okunuşuna göre bu, kilitsiz sızıntıda m_f'nin büyük olduğuna dair
    bir işaret değildir.
  - Saf P kümesi için başvuru W'si sahte P aralığıdır, çünkü küme gerçek W'nin dışındadır. Bu bir okumadır.
- **Duman sonrası düzeltme:** yok. Kod çökmedi.

Z7 ve D-3 gereği bu sonuç hiçbir dalı, eşiği ya da yazarın seçimini değiştirmez.

Kod incelemesi için not (dal değil, yalnız bilgi): tremor dışı olduğu bilinen saf telesismik P kümesi K5'ten sağ çıktı.
Bunun nedeni o sahte pencerede Q'nun boş olması (yalnız ρ kolu) ve ρ'nun −0,7'ye inmemesi. Kör koşuda bu aralık W'nin
dışındadır. Ö-c gereği §12'ye yazılması koordinatörün işidir; burada metin değiştirilmedi.

## 9. Kör koşu için indirme hacmi ve süre kestirimi

Bunlar kestirimdir, ölçüm değildir. Dayanaklar:
- TR-7'nin kendi indirme günlükleri (`tr7_indirme_K1-*.jsonl`);
- TR-7'nin MDA zaman damgaları (`tr7_mda.jsonl`);
- TR-7c birim ve istasyon sayıları (`tr7b_sayim.json` ve USTVERI).

**İstasyon-pencere sayısı:**
- Tetikleyici birimler: 41 birim (10 P, 29 N, 2 B) × 34–52 liste istasyonu = **1 882**.
- Rastgele negatifler: 12 olay × 10 kaydırma × olayın istasyonları = **5 440**.
- Toplam ≈ **7 300 dataselect isteği**. Buna E-1 uzun periyot istekleri eklenir: ≈ 40–80 istek.

**Hacim:**
- TR-7 ortalamaları: negatif istasyon-pencere başına 0,90 MB (çoğu tek bileşen EHZ/SHZ), Tohoku tetikleyici penceresinde
  2,0 MB.
- 1 882 × 2,0 + 5 440 × 0,9 ≈ **8,7 GB**.
- Uzun periyot: HH ya da BH, 3 bileşen, ≈ 2,3 sa × 100 Hz; istek başına ≈ 5–8 MB → **0,2–0,6 GB**.
- **Toplam ≈ 7–10 GB aktarım.** Ham veri işlenip silinir. Kalıcı zarf deposu 1 Hz npz'dir, ≈ 1–2 GB.
- StationXML ve ComCat: birkaç on MB.

**Süre:**
- **İndirme ve zarflama:** TR-7'de istek başına 1,9–2,8 sn (126 istek 234 sn'de; 16 istek 45 sn'de). 7 300 istek →
  **≈ 4–6 saat**. Ağa bağlıdır.
- **MDA:** TR-7'de negatif pencere başına ≈ 200 sn (3 başlangıç). En çok 120 pencere → **≈ 6–7 saat**. Yalnız W'de
  algılama vermeyen pencereler sayılır.
- **Algılama:** dakikalar.
- **Modülasyon:** küme başına ≈ 5 sn (1000 kaydırma, 3 bileşen); 100'ü aşmayan küme için **< 10 dk**.
- **Toplam: ≈ 11–14 saat**, tek çekirdek ağırlıklı. Arka plan işleri 2 saatle sınırlı olduğu için aşamalar
  `--surdur` ile parçalara bölünmelidir; jsonl satırları ve üreteç durumu her pencereden sonra yazılır.
- **Bedel:** 0 €. Bütün servisler açıktır: NCEDC, SCEDC, EarthScope, ComCat.

İndirme hacmini azaltmanın yolu: istasyonları iz sırasıyla indirip 12'si geçince durmak. Bu TR-7 motorundan sapmadır ve
yalnız bir kod incelemesiyle karara bağlanabilir. Hacmi kabaca 3 kat azaltır. Bu sürümde YAPILMADI.

## 10. Koşu dondurmasından önce kapanması gerekenler

1. Bağımsız kod incelemesi (Z8). Bakması gerekenler:
   - D-2 çağrı ağacı;
   - Ö-i notları;
   - O-8 kanal önceliği;
   - O-34: gerçek I/O katmanı sınanmadı;
   - O-9 Q;
   - O-13 üreteç sırası.
2. Kuyu sınıfı bilgi satırı (O-28) ve N27/N28 ayrı bilgi satırı (O-29): eklenecek mi, açıkça bırakılacak mı?
3. Uygulama hatası yolu (O-32, KMS-8).
4. Marmara bağlantısı (O-30). Yalnız K1c (b) çıkarsa gerekir; ama kod incelemesi o durumda ikinci kez yapılmalı.
5. KMS-1…KMS-10'un koordinatörce görülmesi. Hiçbiri karar metninin değiştirilmesini zorunlu kılmaz. KMS-1, KMS-2 ve
   KMS-4'ün okunuşları koşu dondurmasına yazılmalıdır.
