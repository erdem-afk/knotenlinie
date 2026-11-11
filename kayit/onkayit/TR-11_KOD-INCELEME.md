KOŞULABİLİR

# TR-11 koşu kodu: bağımsız kod incelemesi

Tarih: 11 Kasım 2026. İncelenen commit: e67117a (dal `claude/project-thread-hjup0f`). İncelenen dosyalar:
`tr11_kosu.py`, `tr11_indir.py`, `tr11_test_yapay.py`, `beklenti_gurultu.py`, `sayim_ustveri.py` (ilgili kısımlar) ve
`tr11_kume_listesi.json`. Bağlayıcı metinler §0 sırasıyla okundu: INCELEME-1 düzeltme metinleri, ön kayıt (Ek 1 dahil),
SAYIM §2, §4, §5 ve TR-1 menteşe tanımı. tenv3 biçimi için yalnız NGL `README_tenv3.txt` okundu.

Körlük beyanı: hiçbir gerçek tenv3 dosyası indirilmedi ya da okunmadı. `tr11_indir.py` yalnız `--kuru` ile koşuldu.
`tr11_kosu.py` yalnız yapay ağlarla koşuldu. 2026 deprem verisine ve Marmara kutusu verisine dokunulmadı. Kullanılan
üstveri yalnız DataHoldings koordinatları ve steps.txt tarihleridir. Depoda kod ya da ön kayıt değişmedi, commit
atılmadı, `__pycache__` kalmadı. Denetim betikleri depo dışında, karalama dizinindedir (`inc/bagimsiz.py`,
`sigma2.py`, `dv_sd.py`, `yanlilik.py`, `uctan.py`, `zaman.py`, `liste_den.py`).

## Hüküm

Engelleyici bulgu yok. Kod, bağlayıcı tanımları (Ö2 menteşe modeli, S, E2 madde 1–7, E1 (ii-a)/(ii-b), Ö1 etiketi,
E3 çevirisi, Ö3 kuralı) incelediğim her noktada harfiyen uyguluyor. Bağımsız uygulamalarla sayısal uyum var: menteşe
katsayısı 1e-12, σ_h ±%0,5 içinde. Gerçek S'nin denetimlerden önce hesaplanmadığı ve hiçbir yere sızmadığı kod
okumasıyla ve yapay koşuda doğrulandı. Mevcut 26 test geçiyor (289 sn).

Üç önemli bulgu var: Ö1 sırasız dosyada sessiz veri kaybı, Ö2 biçim hatasının tek koşuyu "veri yok" hükmüyle tüketmesi
ve Ö3 b_f* ızgarasının kenarda etiketi değiştirebilmesi. Üçü de nadir durumlardır ve sonucu ancak kenar durumlarda
etkiler. Yamaları kısadır. Gerçek seri indirilmeden, "koşu öncesi düzeltme" başlığıyla uygulanmaları önerilir.
Uygulanmasalar da koşu bağlayıcı metne aykırı olmaz. Bu yüzden hüküm "koşulabilir"dir.

---

## A. Engelleyici bulgular

Yok.

---

## B. Önemli bulgular

### Ö1. Dosya zamana göre sıralı değilse erken durma, pencere içi satırları sessizce atar

- **Bulgu.** `tenv3_ayristir` en son pencerenin sonundan (`son`) büyük MJD'li ilk satırda `break` ile duruyor. README
  satır sırası hakkında hiçbir şey söylemiyor. Pencere içi bir satır, pencere sonrası bir satırdan sonra gelirse
  okunmaz. Bu durumda `geri` sayacı da artmaz, çünkü döngü zaten bitmiştir. Yapay örnek (karalama `bagimsiz.py`):
  günler [w0, w0+1, w1+5, w0+2] sırasıyla yazılınca okunan günler [0, 1] çıktı, `bilgi = {geri: 0, durdu: True}`.
  w0+2 kayboldu ve hiçbir sayaçta görünmedi. Kayıp ya doluluk düşmesine ya da yanlı bir maskeye yol açar. Kod
  denetimi (i) aynı maskeyi kullandığı için bunu yakalayamaz.
- **Neden önemli.** Ö4 yalnız "w1 sonrası satırlar belleğe alınmadan atılır" diyor, okumanın durmasını istemiyor.
  Erken durma Ek 1'de kodlayıcının okuması olarak kayıtlı. `continue` da Ö4'ü aynı ölçüde karşılar: satır dizgesi
  geçicidir, saklanmaz. Üstelik veri kaybını sıfırlar.
- **Yama** (`tr11_kosu.py`, `tenv3_ayristir`):
  ```python
  -    bilgi = dict(bozuk=0, geri=0, tekrar=0, durdu=False, baslik=False)
  +    bilgi = dict(bozuk=0, geri=0, tekrar=0, durdu=False, baslik=False, sonrasi=0)
  ...
  -        if m > son:
  -            bilgi['durdu'] = True
  -            break
  +        if m > son:                      # Ö4: saklanmaz, ayrıştırılmaz; okuma sürer (sırasız dosyaya karşı)
  +            bilgi['durdu'] = True
  +            bilgi['sonrasi'] += 1
  +            continue
  ```
  Değişiklik "Ek 2 / koşu öncesi düzeltme" olarak kayda geçer: "okuma durmaz, w1 sonrası satırlar ayrıştırılmadan
  atlanır". `test_w1_sonrasi_okunmaz` testi buna göre güncellenmelidir: sonraki satırların değerleri saklanmamalı,
  `sonrasi` doğru sayılmalı. Kısıtlı bir seçenek de var: `break` korunur, `kos` içinde `okuma_bilgi['geri'] > 0`
  ise `KosuDur` atılır. Bu seçenek kaybı ancak `break`'ten önceki sırasızlıkta görür, bu yüzden ilki önerilir.

### Ö2. tenv3 biçim hatası koşuyu durdurmuyor; bütün dosyalar düşerse tek koşu "veri yok" hükmüyle tükenir

- **Bulgu.** Başlık uyuşmazlığı (`Tenv3Hata`) istasyonu yalnız `basarisiz` kümesine ekliyor ve nedeni `indirme` olarak
  sayılıyor. %5 indirme kuralı bundan önce, manifestle hesaplandığı için bu düşmeleri görmüyor. NGL başlığında ya da
  sütun düzeninde bir değişiklik olursa (örneğin bir sütun adı ya da sütun sayısı) bütün istasyonlar düşer.
  Veri kapısı da "veri yok" yazar. `yaz` iki çıktı dosyasını "x" kipinde oluşturur, tek koşu koruması devreye girer
  ve Ö4 dosyaları silinir. Ancak bu bir veri sonucu değil, bir kod/biçim hatasıdır. Benzer biçimde, başlıksız dosyada
  `len(p) < 11` satırları yalnız `bozuk` sayılıyor ve bunun için bir eşik yok.
- **Yama** (`kos`, `okuma bitti` logundan hemen önce):
  ```python
  +    if okuma_bilgi['tenv3_hata']:
  +        raise KosuDur(f'tenv3 biçim hatası, {len(okuma_bilgi["tenv3_hata"])} dosya '
  +                      f'(ilk: {okuma_bilgi["tenv3_hata"][:3]}); S hesaplanmadı')
  +    if okuma_bilgi['bozuk'] > 0.01 * max(1, sum(len(r.get('ms', ())) for r in kayit.values())):
  +        raise KosuDur(f'bozuk satır payı %1\'i aşıyor ({okuma_bilgi["bozuk"]}); S hesaplanmadı')
  ```
  Ayrıca `--yalniz-denetim` kipine, her dosyanın **yalnız ilk satırını** okuyan bir başlık denetimi eklenmesi önerilir.
  Bu denetim seri değeri okumaz ve Ö4'e dokunmaz:
  ```python
  +    for s in istasyonlar:
  +        p = os.path.join(a.tenv3, f'{s}.tenv3')
  +        if s in tamam and os.path.exists(p):
  +            with open(p, errors='replace') as f:
  +                tenv3_ayristir([f.readline()], [(0, -1)])   # başlık uyuşmazlığında Tenv3Hata
  ```
  `Tenv3Hata` burada `KosuDur`'a çevrilir.

### Ö3. b_f* bootstrap ızgarası [b/3, 3b] kenarda etiket eşiklerini (2 ve 4) dışarıda bırakabiliyor

- **Bulgu.** `_bf_izgara_coz` hedef ızgaranın dışında kalırsa ızgara ucunu döndürüyor. Durum `izgara_disi` olarak
  sayılıyor, ama etiket kırpılmış değerle konuyor. İki kenar durumu var:
  - b* < 0,67 ise ızgaranın üst ucu 3b* < 2 olur. 2'nin üstündeki bootstrap değerleri bu uca kırpılır, b_f*'nin üst
    sınırı yapay olarak < 2 çıkabilir ve etiket yanlışlıkla "N0-düşük'ten küçük" olur.
  - b* > 12 ise ızgaranın alt ucu b*/3 > 4 olur. Alt sınır bu uca kırpılır ve > 4 çıkar; etiket yanlışlıkla
    "N0-yüksek'ten büyük" olur.
  İki durum da beklenen bölgenin (b* ≈ 2–5) dışındadır, ama etiket kuralı bağlayıcıdır ve sonuç ızgara seçimine
  bağlı olmamalıdır. Ek 1 ızgaranın nokta sayısını (121) kaydediyor, aralığını kaydetmiyor.
- **Yama** (`bf_hazirla`). Izgara iki eşiği her zaman içine alırsa kırpma etiketi değiştiremez: alt uç ≤ 1 < 2,
  üst uç ≥ 6 > 4.
  ```python
  -    izg_b = np.linspace(b / 3, 3 * b, ayar.bf_izgara_n) if b > 0 else np.linspace(0, 3, ayar.bf_izgara_n)
  +    izg_b = np.linspace(min(b / 3, 1.0), max(3 * b, 6.0), ayar.bf_izgara_n)
  ```
  b* ≈ 3 için adım 0,067 olur. Bu ızgarada doğrusal ara değer hatası ihmal edilebilir: q95_N0(b) b ≥ 1'de neredeyse
  doğrusaldır. Ek olarak, etiket satırına `izgara_disi > 0` ise bir uyarı eklenmelidir.

---

## C. Küçük bulgular

- **K1. Veri kapısı gerçek uydurmadaki düşmelerden önce sayılıyor (K2).** `rank_mad` ile gerçek uydurmada düşen
  küme-pencereler (`kume_pencere_gercek_uydurma_dusen`) kapıdan sonra çıkıyor. K2 kapının "rank eksikliğinden sonra"
  sayılmasını istiyor. Pratikte etkisi sıfıra yakındır. Yama: (ii-a) geçtikten sonra, `ana_olcum`'dan önce `go`'dan
  geçerli küme-pencereler yeniden sayılır. Yer < 100 ya da blok < 30 ise "veri yok" yazılır. Bu adımda S
  hesaplanmaz. Ayrıca `go` içindeki istasyon düzeyi `rank_mad` sayıları `dusme.istasyon_T_neden`'e eklenmelidir.
- **K2. `Tenv3Hata` "indirme" diye sayılıyor.** `dusme` içinde `tenv3_bicim` adıyla ayrı bir neden olmalıdır (Ö2
  yamasıyla zaten durur).
- **K3. reflon / e0 / n0 değişimi.** Ö2 toplamın yine kullanılmasını istiyor ve kod buna uyuyor. Yapay sınamada tam
  sayı kısmının 10 m yeniden başlatılması (README not 5) toplamı değiştirmedi (fark 0). reflon değişimi ise farklı
  bir meridyene geçiş demektir ve toplamda büyük bir sıçrama yaratır. Bağlayıcı metin gereği davranış değişmemeli.
  Yalnız bilgi sayacı önerilir: `bilgi['reflon_degisti']`, `bilgi['e0n0_degisti']` (pencere içinde ilk satırdan
  farklıysa +1).
- **K4. Ö4 dosyaları her durumda silinmiyor.** `yaz`, hüküm "geçersiz (kod)" ise ve herhangi bir `KosuDur` ya da
  istisna olursa dosyaları silmiyor. Kod düzeltmesi sonrası yeniden koşu için bu bilinçli olabilir, ama ön kayıt
  "koşudan sonra silinir" diyor. Yama: davranışı Ek'e yazmak ya da `main` içinde bir `finally` bloğunda, son çıktı
  yazıldıysa silmek. Ayrıca Ö4 dosyalarının sha256'sı koşuda denetlenmiyor (`sha_ok = None`). Bayt düzeyinde
  sha256 hesabı satırları ayrıştırmaz, belleğe almaz. Denetlenmesi önerilir; değilse bu fark kayda geçmelidir.
- **K5. Tek koşu koruması `--cikti` değiştirilerek aşılabilir.** Yama: `ana_olcum` çağrılmadan hemen önce tenv3
  dizinine `open(os.path.join(a.tenv3, 'TR11_GERCEK_S_HESAPLANDI'), 'x')` yazılır. `girdi_denetimi` bu dosya varsa
  durur.
- **K6. `tr11_indir.py` yeniden başlatılınca başarısız istasyonları yeniden dener.** `yeniden_deneme_turu` bayrağı
  yalnız otomatik turu sınırlıyor. Betik elle yeniden koşulunca, K6'nın "tek bir yeniden deneme turu" kuralı bu
  yüzden fiilen sınırsız olur. S hesaplanmadığı için körlüğü bozmaz. Yama: manifestte `bitis` varsa ve `--devam`
  verilmemişse dur. Ayrıca `--hedef` depo içindeyse durmalı (SAYIM: "depoya konmaz"):
  `depo = os.path.abspath(os.path.join(BURADA, '..', '..', '..'))`;
  `if os.path.commonpath([os.path.abspath(a.hedef), depo]) == depo: sys.exit('DUR: hedef depo içinde')`.
- **K7. Küçük katmanlarda yüzdelik bootstrap.** Epok 2003 (≈14 KP) ve n_y katmanlarında q95'in yüzdelik bootstrap
  aralığı dar ve kesikli çıkar. Yapay 60 KP'lik ağda gerçek b_f = 3 aralığın dışında kaldı ([2,58, 2,85]). Bu
  satırlar bilgi satırıdır, hüküm vermez. Ama md tablosuna "< 100 KP: aralık güvenilmez" notu eklenmesi önerilir.
  Ana katmanda (≈ 744 KP) sorun beklenmez: 140 KP'lik yapay ağda 12 gerçekleşmede (i) oranının ortalaması
  0,993 ± 0,012 (sd 0,041) çıktı, yanlılık yok.
- **K8. "n_y = 8 katmanı" doluluk sonrası n_y ile kuruluyor.** E3 bunu belirtmiyor. Kod kalan yakın istasyon sayısını
  kullanıyor; bu tutarlı ve dar bir okuma. Ek'e yazılması önerilir.
- **K9. Çeviri etiketi koşulsuz.** `etiket='alt sınır: düşük sismisiteli bölge tabanı (sınıf A güç yok)'`, A sınıfında
  ≥ 30 yer olsa da yazılıyor. Bugünkü listeyle bu olanaksız (2 yer), ama koşullu yazılması doğru olur:
  `if kir['sinif']['A'].get('hukum') == 'güç yok'`.
- **K10. SAYIM §4.3'teki tek satırlık hüküm cümlesi md'de yok.** Ö1 ve E3 bu cümlenin içeriğini değiştirdi, ama tek
  satırlık biçim ("TR-11: [etiket]; sakin pencerelerde S, küme-pencerelerin %5'inde q95 = X [L, U] mm/yıl'ı aşar
  (yer K, blok B, KP N; sınıf D). Sınıf A: güç yok. Marmara çevirisi: …") okuru kolaylaştırır. Önerilir; hükmü
  değiştirmez.
- **K11. SAYIM §8 "Ş1–Ş3 kapalı değişkesi" bilgi satırı uygulanmamış.** §8 bağlayıcı bölümler arasında değil ve
  liste bağlayıcı olduğu için ek küme-pencere kurulamaz. Fark olarak kayda geçmesi yeterlidir.
- **K12. Ölçek denetimi.** Bağlayıcı boyutlarda (M = 2000, B = 2000, 744–803 KP) hiç uçtan uca koşu yapılmadı.
  Testler M = 400, B = 200 ve 100 yerle koşuyor. Ölçtüğüm değerler: MC çekilişlerinin z dizisi 334 MB; bir MC geçişi
  (744 KP) tek süreçte 1,4 sn; b_f* için yaklaşık 22 ikiye bölme ve 121 ızgara geçişi, toplam yaklaşık 3–4 dk; ızgara
  havuzları 121 × 1,49 M × 8 B ≈ 1,45 GB; ağırlıklı nicelik çağrısı 0,01 sn. Bootstrap yaklaşık 15 katman × 2000
  yinelemedir. Toplam RAM gereksinimi yaklaşık 3 GB, süre onlarca dakikadır. Koşu makinesinde ≥ 8 GB RAM olduğu önceden
  denetlenmelidir (bu ortamda 15 GB). Sonradan fark edilen bir bellek hatası, gerçek S hesaplandıktan sonra istisna
  olarak gelir (b_f* gerçek S'den sonra çözülür) ve "koşu sonrası değişiklik" kaydı ister. Tam boyutlu yapay prova
  önerilir (yapay istasyon adlarıyla, gerçek listenin n_y/n_r yapısıyla).

---

## D. Denetim maddeleri (görev listesine göre)

### 1. tenv3 ayrıştırma

- Sütunlar README ile birebir uyumlu: 0 tabanlı 3 = MJD (README 4), 7/8 = doğu tam sayı/kesir (8/9), 9/10 = kuzey
  tam sayı/kesir (10/11). Doğu = e0 + east, kuzey = n0 + north, × 1000 mm. Başlık varsa sütun adları `_` atılarak
  denetleniyor, uyuşmazlıkta `Tenv3Hata`. Başlık yoksa ayrıştırma konuma göre yapılıyor. README başlık satırından
  söz etmiyor; iki durum da destekleniyor.
- Pencere dışı satırlar saklanmıyor. Tekrar eden MJD'de dosyadaki ilk satır alınıyor (Ö2 ile aynı). Yapay sınamada
  10 m tam sayı yeniden başlatması toplamı değiştirmedi.
- Erken durma ve sırasız dosya: bkz. Ö1. Biçim hatası: bkz. Ö2. reflon: bkz. K3.

### 2. Menteşe modeli (Ö2)

- t = (MJD − MJD(w0)) / 365,25; menteşe max(0, t − t_H); sin/cos(2πt), sin/cos(4πt); kod 1 regresörü
  1{MJD ≥ MJD(t_k)}. Aynı gün kayıtları kümeyle tekilleştiriliyor. Ağırlıksız EKK, bileşenler ayrı. MAD bileşen başına
  bir kez uygulanıyor: |r − med| > 5 × 1,4826 × MAD atılıyor, MAD = 0 ise ayıklama yok. Rank ayıklamadan önce ve sonra
  denetleniyor. Doluluk satır günleriyle ve ayıklamadan önce hesaplanıyor; paydalar 1096 ([w0, H)) ve 730
  ([H, w1]). Bu paydalar 2013 epoğu için elle doğrulandı (w0 = 54467, H = 55563, w1 = 56292).
- H'ye ve pencere kenarına 30 gün kuralı ile kod 2 kuralı kodda yeniden uygulanmıyor, listeye güveniliyor. Üstveriyle
  denetledim (`liste_den.py`): 803 KP'de kod 2 ihlali 0, kod 1 30 gün ihlali 0. 3263 (istasyon, KP) çiftinde 1–7 kod 1
  sıçraması var. Savunma amaçlı bir `assert` eklenebilir.
- **Bağımsız uygulama.** Kendi tasarım matrisim, normal denklemler ve MAD ile 50 boşluklu, aykırı günlü, iki
  sıçramalı yapay seride `K.olc` ile en büyük menteşe farkı **1,0e-12** çıktı.

### 3. S tanımı

- `S_hesapla`: referans Δv'lerinin bileşen bazında `np.median`'ı yakın istasyonlardan çıkarılıyor, boyların medyanı
  alınıyor. Elle örnekler (çift n dahil) testte doğru. Doluluk, rank ve indirme düşmesinden sonra yakın ya da
  referans sayısı < 3 olan KP düşüyor. Yerine istasyon alınmıyor, yalnız listenin `y` ve `r` alt kümeleri
  kullanılıyor. Yapay ve gerçek uydurmadaki ek düşmeler ayrı sayılıyor.

### 4. σ_h, q95_N0, ρ, bootstrap, b_f*, kuyruk

- σ_h: a = Q[:, −1] / R[−1, −1], (XᵀX)⁻¹Xᵀ'nin son satırına eşit (R⁻¹ üst üçgen). VF = ΔT^½‖Tᵀa‖². FFT boyu 4096
  > 2 × 1826 − 1 olduğu için dairesel sarma yok. Williams katsayılarını lgamma ile bağımsız hesapladım: göreli fark
  3,6e-12.
- **Bağımsız Monte Carlo** (açık Toeplitz matrisi, FFT yok, n = 20 000, göreli se 0,005):

  | Maske | Kod analitik | Bağımsız analitik | Bağımsız MC | Oran |
  |---|---|---|---|---|
  | boşluksuz | 0,7475 | 0,7475 | 0,7436 | 0,995 |
  | yakın dönem 0,62 doluluk + 1 sıçrama | 0,8405 | 0,8405 | 0,8378 | 0,997 |
  | taban 0,61 bloklu boşluk | 0,7500 | 0,7500 | 0,7500 | 1,000 |
  | %30 rastgele + 130 g delik + 2 sıçrama (n = 4000) | 0,8923 | – | 0,8833 | 0,990 |

  Kodun kendi yapay seri üreticisi ve MAD'li boru hattıyla (n = 3000, iki maske) σ_h oranı 0,990–0,997 çıktı.
- q95_N0: `default_rng(20261111)`, KP'ler liste sırasıyla, (M, n_y + n_r, 2) çekiliş, eşit ağırlıklı birleşimin
  `np.quantile(linear)` ile %95'i. ρ = q95 / q95_N0.
- Bootstrap: `default_rng(20261112)`, (B, blok sayısı) iadeli çekiliş. Pay ve payda aynı blok ağırlıklarıyla
  hesaplanıyor; payda hazır çekilişlerden alınıyor. Aralık %5/%95 yüzdelik. `agirlikli_nicelik`, `np.repeat` +
  `np.quantile` ile birebir aynı (test).
- b_f*: nokta ikiye bölmeyle bulunuyor, aralık ızgarayla. Etiket alt sınır > 4 / üst sınır < 2 kuralıyla konuyor
  (Ö1). Kuyruk: ρ₉₅/ρ₅₀, alt sınır > 1,1. Izgara kenarı için bkz. Ö3.

### 5. Sıra ve sızıntı

- Kod okumasıyla sıra: girdi denetimi → okuma → veri kapısı → MC → (i) ve (ii-b) yapay serilerde → başarısızsa
  `yaz` (S yok) → (ii-a) → başarısızsa `yaz` (S yok) → `ana_olcum`. Gerçek S'yi yalnız `ana_olcum` hesaplıyor (satır
  909). `S_refsiz` ve kod 1 dışarıda satırları da bu fonksiyonun içinde.
- (ii-a) bütün gerekli (istasyon, T) çiftleri için gerçek Δv hesaplıyor (`go`), ama yalnız medyan(d_E),
  medyan(|d_N|) ve çift sayısını loglayıp yazıyor. Δv değeri ve S hiçbir log satırına, istisna iletisine ya da
  geçici dosyaya gitmiyor. `KosuDur` iletilerinde yalnız istasyon adları ve sayılar var.
- Yapay uçtan uca koşuda (`uctan.py`) yeni dosya olarak yalnız `tr11_sonuc.json` ve `tr11_sonuc.md` oluştu. "gerçek
  S hesaplandı" satırından önceki 6 log satırında hiçbir S değeri yoktu. Mevcut test 1, üç başarısızlık yolunda
  `ana_olcum`'un çağrılmadığını doğruluyor.
- Not: E1'in dediği gibi, sinyal ilk uydurmadan önce eklendiği için artıklar değişmiyor; MAD seçimi aynı kalıyor ve
  d_E tam 3 çıkıyor (yapay koşuda 3,0000 / 0,0000). (ii-a) bu yüzden yalnız kod yolunun bütünlüğünü sınar. Tasarım
  gereği beklenen bir durumdur, kusur değildir.

### 6. Marmara çevirisi (E3, Ö3)

- G = |arctan(x/D) − m_r| / π; 3 geometri × 3 D × 5 x = 45 hücre. Elle hesap:

  | Hücre | Elle | Kod |
  |---|---|---|
  | dengeli D5 x5 | 0,25000 | 0,25000 |
  | dengeli D10 x20 | atan2/π = 0,35242 | 0,35242 |
  | aynı yan D15 x5 | atan3/π = 0,39758 | 0,39758 |
  | karşı yan D5 x50 | ½ + atan10/π = 0,96827 | 0,96827 |
  | aynı yan D5 x50 | atan0,1/π = 0,03173 | 0,03173 |

  L₈ = 1,45 ve S50₈ = 0,95 için √(L₈² − S50²) = 1,0954. a = 1,0954 / 0,96827 = 1,1313 (karşı yan D5 x50, kodla aynı).
  c = 1,0954 / 0,35242 = 3,1084 (kodla aynı).
- n_y = 8 katmanı ≥ 300 KP değilse havuza geçiliyor ve bu yazılıyor. S50 aynı katmanın medyanı. L₈ ≤ S50 ise kök 0
  alınıyor (Ek 1). Bilgi satırları √(q95² − S50²)/G ve U₈/G yazılıyor.
- Yorum cümlesi E3'teki sabit biçimle harfiyen aynı. Ö3: a ≥ 10 ise "kapalı", değilse "Bu ölçüm yolu kapatamadı. Bu
  hüküm yolun açık olduğu anlamına gelmez."; c < 5 ise not ekleniyor. Test ve elle denemede doğru.

### 7. Veri kapısı, sınıf, bilgi satırları, girdiler, indirme

- Kapı: yer ≥ 100 ve blok ≥ 30, K2'ye göre doluluk, indirme ve rank sonrası (istisna için bkz. K1). Sınıf satırları
  ≥ 30 yer ister, yoksa "güç yok". Bilgi satırlarının hepsi var: referans farksız S, yer bootstrap'ı, en büyük blok
  dışarıda, bileşen bazında Δv, kod 1 dışarıda, yer ağırlıklı (60/n_epok tam sayı ağırlığı), N1. q99 yalnız
  ≥ 300 KP'de yazılıyor.
- Girdi denetimi: liste sha256 (tam) ile DataHoldings, steps ve TR-2 dosyalarının sha16'sı denetleniyor. Bu ortamdaki
  üstveri dosyaları beklenen değerlerle uyuşuyor. tenv3 sha256'sı manifestle karşılaştırılıyor, uyuşmazlıkta durur
  (Ö4 istisnası için bkz. K4). %5 indirme kuralı uygulanıyor. Tek koşu koruması "x" kipi ve başlangıç denetimiyle
  sağlanıyor (bkz. K5).
- `tr11_indir.py --kuru`: listede 4730 istasyon, kutuda 0. Ö4 listesi AFYN 84,7, AKHR 125,7, CMLD 82,4, KLUU 142,6,
  KRBK 98,3 km; INCELEME-1 Ö4 ile aynı. Betik ağ isteği yapmadı, dizin oluşturmadı. Listede olmayan istasyon
  indirilmiyor (`izinli`); kutuda istasyon varsa hiçbir şey indirmeden duruyor.
- Ö4: w1 sonrası satırlar ayrıştırılmıyor ve saklanmıyor; dosyalar koşudan sonra siliniyor (istisnalar için bkz. K4).
- 2026: steps ve katalogda ≥ 2026-01-01 satırları atılıyor. tenv3 okuması en geç 2022-12-31'de (w1, 2023 epoğu)
  bitiyor.

### 8. Dil

`md_yap` ve `ceviri` metinlerinde mutlak İstanbul olasılığı ya da olasılık çarpanı yok. Etiketler Ö1'deki üçlüyle
sınırlı. "Yol açık" yalnız "TR-11 hiçbir durumda 'yol açık' hükmü vermez" cümlesinde geçiyor ve Ö3 bu cümleyi
istiyor. Aşırı iddia dili bulunmadı.

### 9. Testler ve uçtan uca deneme

- `python3 -I -B tr11_test_yapay.py -v`: **26 test, 288,9 sn, OK.** Uçtan uca test sonuçları: KP 140; (i) 0,964;
  (ii-b) 2,254 / m* 2,214; (ii-a) d_E 3,0000; b_f* 2,90 [2,60, 3,00]; hüküm "taban N0 bandında". (ii-b) için beş
  gerçekleşmenin ortalaması 2,254, m* 2,214.
- Kendi denemem (`uctan.py`; 45 yer, 60 KP, kapı eşikleri yalnız bu deneme için 30/10'a indirildi):

  | Yapay dünya | (i) | (ii-b) / m* | ρ [L, U] | b_f* [L, U] | Hüküm |
  |---|---|---|---|---|---|
  | b_f = 3 (N0) | 0,929 | 2,084 / 2,208 | 0,921 [0,862, 0,950] | 2,76 [2,58, 2,85] | N0 bandında |
  | b_f = 5 | 0,929 | 2,084 / 2,208 | 1,539 [1,443, 1,567] | 4,65 [4,35, 4,73] | N0-yüksek'ten büyük |

  Etiket gürültü düzeyine doğru tepki veriyor. Kod denetimleri (i) ve (ii-b) yalnız gerçek maskeye bağlı olduğu için
  iki dünyada aynı çıkıyor; bu doğru davranıştır. Küçük ağda aralıklar dar (bkz. K7).
- (i) oranının yanlılığı (`yanlilik.py`; 140 KP, 12 bağımsız yapay gerçekleşme): ortalama 0,993, se 0,012, sd 0,041.
  Yanlılık yok. Gerçek boyutta (≈ 744 KP) sd yaklaşık 0,02 olur; [0,9, 1,1] bandı rahat.

---

## E. Önerilen işlem sırası

1. Ö1–Ö3 yamaları (ve isteğe göre K1, K2, K4, K5) "Ek 2: koşu öncesi düzeltme (kod incelemesi)" başlığıyla kayda
   geçer. Hiçbir gerçek seri görülmeden uygulanır. Testler güncellenir ve yeniden koşulur.
2. Bağlayıcı boyutta yapay prova yapılır (K12), süre ve bellek kaydedilir.
3. İndirme → `--yalniz-denetim` (Ö2 başlık denetimiyle) → tek koşu.
