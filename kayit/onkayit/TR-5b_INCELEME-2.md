DÜZELTMEYLE KABUL

# TR-5b ön kayıt: bağımsız inceleme 2 (son tur)

İncelenen: `TR-5b_sismik-hiz-oncul_ONKAYIT.md`, TASLAK sürüm 2 (12 Kasım 2026). Karşılaştırılan: `TR-5b_INCELEME-1.md`.
Dayanaklar: `TR-5_TR-4_SAYIM.md` (Ek 1) ve `kayit/turetme/tr5/` (`tr5b_liste_s2.py/.json`, `tr5b_asama0.py`,
`tr5b_guc2.py`, `tr5b_yapay.py`, `tr5b_yapay2.py`, çıktıları).

Bu inceleme ne yaptı, ne yapmadı:
- Hiçbir dalga formu istenmedi, indirilmedi, açılmadı ya da yoklanmadı. `tr5b_asama0.py` yalnız `kuru` kipte koşuldu;
  ağ kipleri çalıştırılmadı. Sürdürme mantığı, `urlopen` yasaklanıp `_getir` sahte bir yanıtlayıcıyla değiştirilerek
  ağsız sınandı.
- Ağa yalnız bir kez çıkıldı: Wells–Coppersmith katsayısı için bir web araması ve bir sayfa okuması (OpenQuake kaynak
  kodu). Kişi ya da proje bilgisi gönderilmedi.
- Liste betiği ve `kuru` kip, depo dosyalarına dokunmamak için karalama dizinindeki bir kopyada
  (`…/scratchpad/inc2/k/`) koşuldu. Girdiler `/mnt/project-files/turetme/tr5b-ham/` ve `tr2-ham` arşivlerinden açıldı.
- Denetim betikleri ve çıktıları `kayit/turetme/tr5/inc2/` altında (aşağıda E bölümü). Hepsi `python3 -I -B`, yalnız
  numpy; `__pycache__` kalmadı. Ön kayıt ve `tr5` dizinindeki dosyalar değiştirilmedi. Git işlemi yapılmadı.

## Hüküm

**DÜZELTMEYLE KABUL.** Sürüm 2, İNCELEME-1'in 3 engelleyici, 9 önemli ve 12 küçük bulgusunun hepsini işlemiş (A
bölümü). Bağlayıcı liste ve bütün sha256'lar bit düzeyinde yeniden üretildi. Güç tabloları ve E3 bağımsız yazımla
Monte Carlo saçılımı içinde tutuyor. Tasarım dondurulabilir.

Dondurmadan önce iki engelleyici düzeltme gerekir. İkisi de kapı G0'ı ilgilendirir. G0 geri alınamaz bir kapıdır:
"güç yok (aşama 0)" ile kapanan bir sınav bu ön kayıt içinde yeniden açılmaz.

- **İ2-E1. Aşama 0 kodu G0'ı eksik ya da geçici hatalı veriyle verebilir; liste sha256'sı hiçbir kipte denetlenmiyor.**
  `say` yoklanmamış ve hata dönen istekleri "yok" sayıyor ve eksiklikte durmuyor. Hata satırları önbellekte "yapıldı"
  sayıldığı için bir daha denenmiyor (ağsız sınamada 40 hata satırının 0'ı yeniden denendi). Yarım yazılmış son
  önbellek satırı `say`'ı düşürüyor. `LISTE_SHA = None`, yani §2.8'in "koşu kodu sha'yı denetler" cümlesi bugün
  doğru değil.
- **İ2-E2. Yatay yoklamanın "altı isteğin hepsi var" kuralı, gerçek üç bileşen eksikliğinden bağımsız olarak dolu
  pencerelerin en az %8'ini düşürür.** Ek 1'in Z yoklamasıyla ölçüldü: `dolu_ana` geçen 60 olay penceresinin 5'inde
  (%8,3) dilim orta aylarından biri Z'de de boş. Ek 1'deki geçici 500 hatası oranı (%0,36) altı istekle pencere başına
  ≈ %2 daha ekler. Bu kayıplar üç bileşenin varlığıyla ilgili değildir. Olayların %77'si tek istasyonludur, bu yüzden
  pencere kaybı doğrudan küme kaybıdır. Düzeltme koşulludur: Z'si "var" olmayan dilimin yatay isteği sayılmaz. İstek
  listesi değişmez.

Önemli bulgular beş tane (İ2-Ö1–Ö5). En önemlisi İ2-Ö1: PK geçmediğinde hüküm adı yöntem hatası iddia ediyor. Oysa
gerçekçi uzaklık karışımında Napa ölçeğinde PK'nin yöntem doğruyken geçmeme olasılığı 0,16–0,54'tür. Kural kalır, ad
ve önceden bildirilen olasılık düzeltilir. İ2-Ö3 dondurma anını aşama 0'ın ilk ağ isteğinin önüne çeker.

Üçüncü tura gerek yoktur. Düzeltmelerin hepsi metin ve `tr5b_asama0.py`'de sınırlı kod değişikliğidir. Liste, örneklem,
§3'ün parametreleri ve hüküm kuralı değişmez. Yeni sayım, yeni liste ve dalga formu erişimi gerekmez.

**Bağımsız olarak doğrulananlar.**
- **Liste.** `tr5b_liste_s2.py` karalama kopyasında arşivlenmiş girdilerle koşuldu (23 sn). `tr5b_liste_s2.json`
  `a3a6a45a…`, `tr5b_olaylar_s2.csv` `8e2f908c…`, `tr5b_kontroller_s2.csv` `00e489e7…`, `tr5b_pilot_s2.csv` `f36cfe74…`
  ve `tr5b_ozet_s2.json` `217d6d74…` **bit düzeyinde aynı** çıktı. K 37 → volkaniksiz **31**, eşleşik plasebo **16**;
  Z önizlemesi 28 / 15; kota önizlemesi "hepsi dolu" 31 / 16.
- **Arşiv ve depo sha256'ları.** `tr5b_ham_sha256.txt`'deki dört arşiv, `tr5b_yapay_ccf.npz` (`44189a31…`, 631 137 078
  bayt), `tr5b_yapay_ccf_ref.json`, `tr5b_gvp_holosen.csv` ve `tr5_doluluk.csv` tutuyor. Değişiklik listesindeki
  betik sha256'ları da (`tr5b_asama0.py`, `tr5b_guc2.py`, `tr5b_yapay2.py`, `tr5b_liste_s2.py`, `tr5b_yapay.py`) tutuyor.
- **Aşama 0 kuru kip.** Bütün sayılar aynı: 1246 pencere (60 / 815 / 26 / 438), 292 istasyon, 27 410 istek
  (292 / 20 424 / 6694), merkez payları, 2,88 / 1,64 saat, 2 iş, K₀ ≤ 28, K_p₀ ≤ 15. Ama dosyanın baytları her koşuda
  değişiyor (İ2-K2): üç koşuda üç ayrı sha256 çıktı, biri ön kayıttakiyle aynıydı.
- **Kota okunuşları** bağımsız yazımla. Dinamik: 31 / 16 (Z önizlemesi 28 / 15). Statik: **29 / 14** (Z ile 26 / 11);
  yazarın "K 29" sayısı doğru. Volkanik 6 olayın kotaya yazılması K'yi değiştirmiyor (iki durumda da 31 / 16 ve
  28 / 15).
- **Güç.** Bağımsız yazım (t niceliği sayısal tümlevle, tohum 515151, B = 12 000):

  | Sayı | Ön kayıt | Bağımsız |
  |---|---|---|
  | H1 / H0 / ana, δ 0 (K 31) | 0,012 / 0,561 / 0,047 | 0,016 / 0,559 / 0,052 |
  | H1 / H0 / ana, δ 0,5 | 0,251 / 0,059 / 0,619 | 0,250 / 0,061 / 0,619 |
  | H1 / ana, δ 0,75 | 0,505 / 0,926 | 0,508 / 0,928 |
  | H0, δ 0 (K 20 / K_p 10) | 0,191 | 0,202 |
  | Ö7, H1 δ 0,75 | 0,277 | 0,270 |
  | 4. adım (K 31), σ %0,1 / 0,15 / 0,2 / 0,3 | 0,99 / 0,86 / 0,63 / 0,34 | 0,994 / 0,860 / 0,626 / 0,338 |
  | σ*(K 31) | %0,234 | %0,234 |
  | P1 geçer, σ %0,15 / 0,2 (K 31) | 0,99 / 0,81 | 0,99 / 0,81 |
- **E3.** Bağımsız ve kısaltmasız yazım: bütün günler ayrı üretildi, tam ızgara. Havuz 300 istasyon, 2000 çekiliş
  (D bölümü). A = %0,08'de 0,72 / 0,59 / 0,97 çıktı; ön kayıtta 0,795 [0,753; 0,829] / 0,601 [0,530; 0,664] / 0,973.
  Küçük havuzun beklenen saçılımı içinde. Gürültüsüz durumda iki uygulamanın δ_ko'su aynı (≈ −0,66 · A_k).
- **Körlük.** Bütün istek tarihleri ≤ 2023-12-31; `assert`'ler yerinde. En geç PK penceresi 2023-03-08, P2'de
  2022-10-18. Liste istasyonlarının hiçbiri TR-1 Marmara kutusunda değil. Aşama 0 olay sonrası dalga formuna dokunmuyor:
  Z ve yatay yoklamalar [a, T − 8] içinde; T + 30'a uzanan yalnız üstveri isteği.
- **Wells–Coppersmith.** L(M) = 10^(−2,44 + 0,59 M) km, alt yüzey kırık boyu, bütün türler. Açık kaynakta aynı
  katsayılar bulundu: OpenQuake `openquake.hazardlib.scalerel.wc1994.WC1994.get_median_rld`, rake yokken
  `10.0 ** (-2.44 + 0.59 * mag)`, "median subsurface rupture length". Bu ikincil bir kaynaktır; asıl makalenin
  tablosu (BSSA 84(4), 974–1002, Tablo 2A) okunmadı.

---

## A. İNCELEME-1 bulgularının sürüm 2'de işlenişi

| Bulgu | İşlendi mi | Not |
|---|---|---|
| E1 aşama 0 | Evet | §5.1 tam metin, G0, betik. Kodun eksiklikleri → İ2-E1. Yatay kuralın sertliği → İ2-E2. Dondurma anı → İ2-Ö3 |
| E1 pilot | Evet | P1 ve P2 tam metin; P2 listesi koddan, 20 olay; hacim yeniden hesaplandı (0,094 + 0,024 TB doğrulandı). P1 birimi → İ2-Ö2; P2 uzaklığı → İ2-Ö4 |
| E1 1b sırası | Evet | 1b-olay önce; "güç yok (1b, olay tarafı)" |
| E2 | Evet | Ölçüt %95 üst sınır < 0,5; S4 bilgi; K 31 / 28 / 20 tabloları doğrulandı |
| E3a–c | Evet | Enerji reddi medyanı, ±%2 ızgarası, aygıt [T − 1095, T + 30]. (T − 8, T + 30] ile İNCELEME-1'in [T − 7, T + 30]'u aynı gün kümesidir |
| E3d | Evet | 5 havuz × 1000; A = 0 ve mevsim %0,10 satırları. A = 0'ın 0,051'i → İ2-Ö5 |
| E3 ek, E3e | Evet | En yakın geçerli istasyon; "ayırt edilemez (PK geçmedi)". "güç yok" dalının adı → İ2-Ö1 |
| Ö1 | Evet | 1b'de ≥ 9 ay yığın şartı, maskesiz payda, 6a (K₆, K_p6) |
| Ö2 | Evet | Adım 1–2 için sınır yok → İ2-K4 |
| Ö3 | Evet | GVP indirildi, sha256'lar tutuyor; (f) simetrik; K 37 → 31 doğrulandı |
| Ö4 | Evet, dinamik okunuşla | B bölümünde hükme bağlandı (KABUL) |
| Ö5 | Evet | Kesişim; usb000r2hc düştü; d_k tanımı |
| Ö6 | Evet | Zorunlu hidroloji cümlesi, r̄_kay notu, §7 gerekçesi |
| Ö7 | Evet | "İstasyon çevresi, ortanca 50 km"; σ_Δ birimi; 1,5 kat satırı |
| Ö8 | Evet | Bilgi satırı 16; düşüş H1'inde zorunlu not |
| Ö9 | Evet | npz ve başvuru sha256'ları doğrulandı; dizi başına tolerans |
| K1–K12 | Evet | K2'nin ±0,10 hesabı (0,025) doğrulandı. K7(4) hacim tablosu tekrarsız. K10 tablosu genişletildi. Wells–Coppersmith satırı → İ2-K1 |
| D | Gerekmiyor | – |

Değişiklik listesindeki "Yazar 1–4" satırları kabul edildi.

## B. Yazarın işaret ettiği yerlere hükümler

### §2.3 ve §9/2: kotanın dinamik okunuşu. Hüküm: KABUL

İNCELEME-1 Ö4'ün cümlesi "Kota, kontrolün koşuda kullanılıp kullanılmadığına göre işler; yedekler de dahildir"
idi. Bu cümlenin tek tutarlı okunuşu dinamik okunuştur: kotaya yalnız atanan aday yazılır, atanan yedek de yazılır.
Statik okunuş "kullanılıp kullanılmadığına göre" ifadesiyle çelişir ve bağımsız yeniden hesapla K'yi 29'a (Z
önizlemesiyle 26'ya) indirir.

Dinamik atama aşama 0'ın doluluk sonucuna bağlıdır. Ama doluluk dv/v bilgisi taşımaz, kural koddadır ve deterministtir.
Volkanik olayların da kotaya yazıldığı metinde açık değil; K'ye etkisi yok, metne bir cümle eklenir (İ2-K3).

1b'deki "baştan yeniden atama" sonlanır: dolu küme yalnız küçülür. Ama başka bir olayın zaten dolu olan bir kontrolü
yer değiştirebilir. Bu israftır, körlüğü bozmaz.

### §9/3: yatay yoklamada altı isteğin hepsinin "var" istenmesi. Hüküm: DÜZELTİLİR (İ2-E2)

"Gerçek kayıp küçük beklenir" yargısı ölçüldü ve tutmadı. Yatay bileşenler Z ile aynı aylarda var olsa bile kayıp
≥ %8,3'tür. Buna geçici hatalardan gelen ≈ %2 eklenir.

### §9/4: P1 istasyon düzeyi, 4. adım kontrol düzeyi. Hüküm: KABUL, nicel metinle (İ2-Ö2)

Yön tutucudur, büyüklüğü sınırlıdır. İlk 5 adayların istasyon sayıları 1 / 2 / 3 için 88 / 39 / 68, ortalama 1/n =
0,668. İstasyonlar bağımsızsa kontrol düzeyi σ = 0,817 × istasyon düzeyi σ olur; tam ilişkide ikisi eşittir.

P1'in kontrol düzeyindeki etkin eşiği bu yüzden σ*'ın 0,82–1 katıdır: K 31'de %0,19–0,23. Bu aralıkta 4. adımın geçme
olasılığı 0,67–0,50'dir. Yani P1, 4. adımın en çok ≈ 0,67 olasılıkla geçeceği durumlarda durdurabilir.

Kontrol düzeyinde P1 (1. adayın bütün istasyonları) bu farkı kaldırırdı. Ama P1 hacmini 0,094'ten 0,195 TB'ye
çıkarır; INGV payı 0,056 TB'dir ve ölçülmemiş hızla bulutta 15–39 saat sürer. Bu yüzden önerilmez.

### §6.1 E3: A = 0'da 0,04–0,06 ve Napa ölçeğinde ≈ %40 geçmeme. Hüküm: kural KALIR, ad ve metin DÜZELTİLİR (İ2-Ö1, İ2-Ö5)

- **Yanlış geçme.** Kesin Wilcoxon'un p ≤ 0,05'te ulaşılabilir boyutu n = 8…15 için 0,039–0,049'dur (n = 15'te
  0,0473). Simetrik gürültüde test %5'i aşmaz. Gözlenen 0,051 (en kötü havuz 0,060) havuz dengesizliğidir. Bağımsız
  300'lük havuzda mevsim %0,10'da 0,100 çıktı; o havuzun A = 0 medyanı −%0,010'du. Eşik değişmez.
- **Geçmeme.** Kural doğrudur. Bilinen kosismik düşüşü örneklem içinde görmeyen bir zincirin H0'ı "etki yok" diye
  yazılamaz.
- **Ad yanlıştır.** P2 (bağımsız olaylar, medyan 29 km) ve 4. adım geçmeden 8. adıma gelinmez. 8. adımda PK geçmezse,
  kanıt "yöntem bilinen düşüşü göstermedi"den çok "bu 15 kümelik, kısmen > 50 km'lik örneklemde görülmedi"dir.
  Gerçekçi uzaklık karışımında (en yakın geçerli istasyonu > 50 km olan 3 küme etkisiz) geçme 0,46 / 0,55 / 0,84'tür.
  Yöntem doğruyken geçmeme olasılığı bu yüzden 0,16–0,54'tür.
- **Haksızlık.** Soru haksız yere öldürülmez, çünkü "güç yok" adayı elemez ve §11 yeniden açmayı tanımlar. Ama
  kaybedilen H0 olasılığı önceden yazılmalıdır: δ = 0'da P(H0 ve PK geçer) ≈ 0,56 × (0,46–0,97) ≈ 0,26–0,54
  (bağımsızlık varsayımıyla kaba).

### §9/13: P2 istasyonlarının uzaklığı. Hüküm: KABUL, liste değişmez (İ2-Ö4)

20 olayın 6'sının istasyonu > 50 km'dedir: IU.HNR 337, PS.PSI 213, NZ.MXZ 102, CN.LGNH 93, GE.MALT 57, C.ROC1 51.
Bunlardan > 90 km'deki 4'ü etkisiz sayılırsa P2 Napa ölçeğinde 0,68 / 0,59 / 0,93 geçer; 6'sı etkisiz sayılırsa
0,55 / 0,52 / 0,82. Eşiği şimdi 50 km'ye kısmak P2 listesini yeniden üretmeyi gerektirir. Kazanç belirsizdir: büyük
olaylarda kırığa uzaklık dış merkez uzaklığından küçüktür. Bu yüzden önerilmez; olasılık metne girer.

### Wells–Coppersmith. Hüküm: DOĞRULANDI (ikincil açık kaynak; İ2-K1)

### LISTE_SHA'nın dondurmada sabitlenmesi. Hüküm: GEREKLİ, ama yetmez (İ2-E1)

Değer `a3a6a45a97d9e6a625f3aa6157093cda75b2190a026740573369d64bd46e8763`'tür. Denetim bugün yalnız `say`'dadır ve
`None` iken hiç çalışmaz. Her kipte yapılmalı ve uyuşmazlıkta durmalıdır. Bu düzeltmeler listeyi değiştirmez;
`tr5b_asama0.py`'nin sha256'sı değişir.

### Hüküm kuralı, kapalı ad listesi, körlük, tek koşu, yeniden açma, İstanbul olasılığı

- **Oynama payı.** Hüküm kuralı otomatik ve sıralı. §4.6 kapalı listesi §4.2 ile tutarlı; tek değişiklik İ2-Ö1'in adı.
  Koşu öncesi düzeltme kuralı adım 3–4'e iki deneme sınırı koyuyor, adım 1–2'ye koymuyor (İ2-K4).
- **Körlük.** 2026 verisi yok. İstekler ≤ 2023-12-31, P2 ≤ 2025-12-31 (fiilen 2022-10-18). Marmara GNSS'e dokunulmuyor.
  Ama dondurma anı aşama 0'dan sonraya kalabiliyor (İ2-Ö3).
- **Tek koşu.** Aşama 0'ın yeniden yoklanması tanımsız (İ2-Ö3).
- **Yeniden açma (§11)** yeterli.
- **İstanbul için mutlak olasılık** yok; §10'da yasak cümlesi yerinde.

## C. Numaralı bulgular ve düzeltme metinleri

Kök oturum aşağıdaki metinleri harfiyen işler. "Değiştir" verilen metnin tamamını yerine koyar; "ekle" verilen yere
ekler.

### İ2-E1 (E). Aşama 0: sha denetimi, eksik ve hatalı istekler, sürdürme

**Kod, `kayit/turetme/tr5/tr5b_asama0.py`** (yalnız bu değişiklikler):

1. `LISTE_SHA = None …` satırını şu satırla değiştir:
   `LISTE_SHA = 'a3a6a45a97d9e6a625f3aa6157093cda75b2190a026740573369d64bd46e8763'   # ön kayıt §2.8 (dondurulmuş)`
2. `ag_onayi` tanımından önce ekle:
   ```python
   KESIN = (200, 204, 404, 401, 403)          # kesin yanıt kodları; ötekiler bir kez yeniden denenir


   def liste_denet(liste):
       sha = hashlib.sha256(open(liste, 'rb').read()).hexdigest()
       if sha != LISTE_SHA: sys.exit(f'liste sha256 uyuşmuyor ({sha}); durdu')
       return sha


   def satirlar(yol):
       """jsonl; yarım ya da bozuk satır atlanır."""
       out = []
       if os.path.exists(yol):
           for l in open(yol, encoding='utf-8'):
               try: out.append(json.loads(l))
               except ValueError: pass
       return out


   def son_durum(kayitlar):
       """anahtar -> geçerli satır (varsa kesin kodlu son satır, yoksa son satır) ve deneme sayısı."""
       d, n = {}, collections.Counter()
       for x in kayitlar:
           n[x['k']] += 1
           if x['k'] not in d or x['kod'] in KESIN or d[x['k']]['kod'] not in KESIN: d[x['k']] = x
       return d, n
   ```
3. `kuru`, `ustveri`, `kur` ve `say`'ın ilk satırı olarak `liste_denet(liste)` çağrılır. `kuru` ve `say`'daki
   `sha = hashlib…` satırları `sha = liste_denet(liste)` olur. `say`'daki `if LISTE_SHA and sha != LISTE_SHA: …`
   satırı silinir.
4. `yokla`'da `yapilan` şöyle kurulur. Bir istek, kesin kodlu bir satırı varsa ya da iki kez denenmişse yapılmış sayılır:
   ```python
   d, n = son_durum(satirlar(oyol))
   yapilan = {k for k, x in d.items() if x['kod'] in KESIN or n[k] >= 2}
   ```
5. `ustveri`'de dosya önce `s + '.txt.tmp'` adıyla yazılır, sonra `os.replace` ile yerine konur. Önbellekte dosyası
   olmayan bir istasyon, `ustveri_gunluk.jsonl`'da iki kez kesin olmayan kodla görünüyorsa yeniden istenmez.
6. `say`'da önbellek `kayit, deneme = son_durum(satirlar(os.path.join(ob, 'onbellek.jsonl')))` ile okunur. Sayımdan
   önce şu denetim yapılır:
   ```python
   eksik = [anahtar(r) for r in IST['istekler'] if anahtar(r) not in kayit or
            (kayit[anahtar(r)]['kod'] not in KESIN and deneme[anahtar(r)] < 2)]
   ug = collections.Counter(x['ist'] for x in satirlar(os.path.join(ob, 'ustveri_gunluk.jsonl')) if x['kod'] not in KESIN)
   ust_eksik = [s for s in IST['ustveri_eksik'] if ug[s] < 2]
   if eksik or ust_eksik: sys.exit(f'aşama 0 tamamlanmadı: {len(eksik)} istek, {len(ust_eksik)} üstveri; G0 verilmez')
   ```
   Çıktıya şunlar eklenir:
   - `istek_durum`: istekler üstünden `var`, `bos`, `kisitli`, `hata` sayıları, rol ve merkez kırılımıyla;
   - `ustveri_alinamayan`;
   - `onbellek_sha256`;
   - `istekler_sha256`.
7. Komutlarda `sure_sn` 6600 yerine **6000**'dir. Gerekçe: tek bir istek 3 × 120 sn zaman aşımı ve beklemelerle
   ≈ 400–600 sn sürebilir; iş 2 saatlik sınırı aşmamalı.

**Metin.**

- §5.1 madde 3'te "Her yanıt `onbellek.jsonl`'a satır olarak eklenir. İş önbellekten sürdürülür: yeniden çağrı yalnız
  kalan istekleri atar." cümleleri şununla değiştirilir:
  > Her yanıt `onbellek.jsonl`'a satır olarak eklenir. İş önbellekten sürdürülür: yeniden çağrı yalnız kalan istekleri
  > atar. Bir istek, kesin kodla (200, 204, 404, 401, 403) yanıtlanmışsa ya da iki kez denenmişse tamamlanmış sayılır.
  > Öteki kodlar ve bağlantı hataları sonraki çağrıda bir kez yeniden denenir (en çok iki deneme; her denemenin içinde
  > §5.1'in 429/503 kuralı ayrıca geçerlidir). Üstveri istekleri de aynı kuralla en çok iki kez denenir ve dosyalar
  > bütün olarak yazılır. Yarım yazılmış önbellek satırı yok sayılır.
- §5.1 madde 4'ün başına eklenir:
  > `say`, istek listesindeki her istek ve her üstveri isteği tamamlanmadıkça hiçbir sayı ve hüküm vermez ve durur.
  > Liste sha256'sı her kipte denetlenir; uyuşmazlıkta iş durur.
- Madde 4'teki "öteki: hata (yok sayılır, ayrıca sayılır)" ifadesinden sonra eklenir:
  > Hata ve kısıtlı sayıları rol ve merkez kırılımıyla `asama0_sonuc.json` → `istek_durum` alanına yazılır.
- §2.8'deki "(`tr5b_asama0.LISTE_SHA` dondurmada bu değere sabitlenir)" ifadesi şununla değiştirilir:
  > (`tr5b_asama0.LISTE_SHA` bu değere sabittir; `kuru`, `ustveri`, `kur` ve `say` kipleri denetler)
- Ek'teki komutlarda `6600` → `6000`.

Kök oturum kod değişikliğinden sonra şunları yapar:
1. `tr5b_liste_s2.py`'yi yeniden koşar ve beş çıktının sha256'sının değişmediğini doğrular (liste betiği `kota_ata` ve
   `K_say`'ı içe aktarır; bunlara dokunulmaz).
2. `inc2/inc2_asama0_denetim.py`'nin bir kopyasını, yeni kodun yeniden denemeyi yaptığını gösterecek biçimde koşar.
   Beklenen: "ucuncu_cagrida_atilan" 40, dördüncü çağrıda 0; yarım satırda `say` düşmez.
3. Değişiklik listesindeki `tr5b_asama0.py` sha256'sını günceller.

### İ2-E2 (E). Yatay yoklama: koşullu kural

**Kod**, `say` içinde `h_ok = all(…)` satırı şununla değiştirilir:
```python
zd = lambda ay: ay_durum(kayit.get(f"{ag}.{st}.{s['loc']}.{s['bant']}Z.{ay}"))
bilgili = [orta_ay(x, y) for x, y in dil if zd(orta_ay(x, y)) == 'var']
h_ok = bool(bilgili) and all(ay_durum(kayit.get(f"{ag}.{st}.{s['loc']}.{s['bant']}{h}.{ay}")) == 'var'
                             for ay in bilgili for h in s['yatay'])
```
Neden kodlarına `'yatay_bilgisiz'` eklenir (`bilgili` boşsa).

**Metin.** §5.1 madde 2'deki "Altı istekten biri 'var' değilse pencere 'üç bileşen yok' sayılır." cümlesi
şununla değiştirilir:
> Bir dilimin yatay istekleri, aynı ayın Z isteği "var" ise bilgilidir; Z'si "var" olmayan dilimin yatay istekleri
> sayılmaz (o ayın boşluğu Z ay doluluğunda zaten sayılır). Bilgili her dilimde iki yatay istek de "var" olmalıdır.
> Hiçbir dilim bilgili değilse ya da bilgili bir dilimde yatay isteklerden biri "var" değilse pencere "üç bileşen
> yok" sayılır.

§5.1 madde 4'teki "ve altı yatay istek 'var'" ifadesi "ve yatay yoklama kuralı (madde 2) geçti" olur.

§9 madde 3 şununla değiştirilir:
> 3. **Yatay yoklama (İNCELEME-2 İ2-E2).** Sert kural ("altısı da var") Ek 1 verisiyle dolu pencerelerin ≥ %8,3'ünü,
> yalnız Z'nin de boş olduğu aylar yüzünden düşürüyordu. Kural koşullu yapıldı; istek listesi değişmedi.

### İ2-Ö1 (Ö). 8. adım: PK geçmediğinde hükmün adı ve önceden bildirilen olasılık

**Metin.**

- §4.2 adım 8'de ve §4.6 tablosunda "güç yok (yöntem bilinen kosismik düşüşü göstermedi)" adı her yerde
  **"güç yok (8. adım: pozitif kontrol geçmedi)"** olur. §4.6'daki satırın "Zorunlu ek metin" hücresi şu olur:
  > "geçerli PK kümesi [..], p = [..]; P2 ve 4. adım geçmişti; önceden hesaplanan geçme olasılığı Napa ölçeğinde
  > 0,46–0,97 (§6.1); bu hüküm yöntemin çalışmadığını göstermez, H0'ın bu örneklemde dayanaksız kaldığını gösterir;
  > 9. adımın H0 şartı: [tuttu / tutmadı]"
- §4.3 "Güç yok" maddesine eklenir:
  > "(8. adım)": ölçü kuruldu ve 4. adım geçti, ama örneklemin kendi kosismik düşüşü gösterilemediği için H0
  > yazılamadı.
- §4.4'ün sonuna eklenir:
  > **PK ile birlikte.** δ = 0'da H0 ancak PK da geçerse yazılır. P(H0 ve PK geçer) ≈ 0,56 × (0,46–0,97) ≈ 0,26–0,54
  > (bağımsızlık varsayımıyla kaba; §6.1).
- §6.1 "Okuma"nın ikinci maddesinin sonuna eklenir:
  > **Uzaklık.** E3 her kümeye aynı ölçekte düşüş verir. PK kümelerinin en yakın geçerli istasyonu üçünde > 50 km'dir
  > (NZ.KNZ 53, HT.LKD2 67, AK.CHN 69 km). Boschelli 2021'e göre bu uzaklıkta düşüş beklenmez. Bu üç küme A = 0
  > sayılırsa Napa ölçeğinde geçme 0,55 / 0,46 / 0,84'e iner (CC₁₀ ≈ 0,5 / 0,5 ve mevsim %0,10 / 0,7;
  > İNCELEME-2 bağımsız benzetimi, 300'lük havuz). Yöntem doğruyken PK'nin geçmeme olasılığı bu yüzden ≈ 0,16–0,54'tür.
- §9 madde 5 şununla değiştirilir:
  > 5. **PK'nin geçme olasılığı (İNCELEME-2 İ2-Ö1).** Napa ölçeğinde 0,46–0,97 (uzaklık senaryosu dahil). Kural
  > kaldı; adı "güç yok (8. adım: pozitif kontrol geçmedi)" oldu ve yöntem hatası iddia etmez.

### İ2-Ö2 (Ö). P1'in birimi: nicel sınır

**Metin.** §5.1 P1'deki "Not: σ̂_P1 istasyon düzeyindedir; …; kural tutucu yöndedir." maddesi şununla değiştirilir:
> Not: σ̂_P1 istasyon düzeyindedir, 4. adımın σ_Δ'sı kontrol düzeyindedir. Bir kontrol 1–3 istasyonun ortalamasıdır
> (ilk 5 adaylarda 88 / 39 / 68; ortalama 1/n = 0,668). İstasyonlar bağımsızsa σ_kontrol ≈ 0,817 · σ_istasyon,
> tam ilişkide σ_kontrol = σ_istasyon. P1'in kontrol düzeyindeki etkin eşiği bu yüzden σ*(K)'nın 0,82–1 katıdır
> (K 31: %0,19–0,23). Bu noktada 4. adımın geçme olasılığı 0,67–0,50'dir. Yani P1 yalnız 4. adımın ≲ 0,67 olasılıkla
> geçeceği durumlarda durdurabilir. Kontrol düzeyinde P1 hacmi 0,094'ten 0,195 TB'ye çıkarırdı (INGV 0,056 TB); bu
> yüzden seçilmedi. Bu tutuculuk kabul edildi (İNCELEME-2 İ2-Ö2).

§6.2'deki P1 tablosuna satır eklenir:

| σ_Δ (kontrol düzeyi) | %0,05 | %0,075 | %0,1 | %0,15 | %0,2 | %0,3 |
|---|---|---|---|---|---|---|
| P1 geçer, K 31, istasyonlar bağımsız (σ_ist = σ_Δ / 0,817) | 1,00 | 1,00 | 1,00 | 0,90 | 0,50 | 0,07 |

Satırın altına "(İNCELEME-2; σ*(K 31) = %0,2337, n = 24, 200 000 çekiliş; `inc2_guc_bagimsiz.py` B = 40 000 ile
%0,15 / 0,2 / 0,25'te 0,90 / 0,50 / 0,20)" yazılır.

§9 madde 4 şununla değiştirilir:
> 4. **P1'in birimi (İNCELEME-2 İ2-Ö2).** Tutuculuk sınırlı: etkin eşik σ*'ın 0,82–1 katı.

### İ2-Ö3 (Ö). Dondurma anı ve aşama 0'da tek koşu

**Metin.** §5.1'deki "Ön kayıt, liste ve koşu kodu aşama P'den önce dondurulur ve push edilir." cümlesi şununla
değiştirilir:
> Ön kayıt, bağlayıcı liste ve `tr5b_asama0.py` aşama 0'ın ilk ağ isteğinden önce dondurulur ve push edilir. dv/v koşu
> kodu, kod incelemesinden sonra ve aşama P'den önce dondurulur ve push edilir.

§5.5'e madde olarak eklenir:
> **Aşama 0'da tek koşu.** Aşama 0 bir kez koşulur. Önbellek silinmez, yeniden yoklama yapılmaz. Tek yeniden deneme,
> §5.1 madde 3'ün kesin olmayan kodlar için tanımladığı denemedir. `say` bir kez, bütün istekler tamamlanınca koşulur.
> `asama0_sonuc.json`, `onbellek.jsonl` ve `istekler.json`'un sha256'ları kayda geçer ve push edilir. G0 kararından
> sonra aşama 0'ın hiçbir kuralı değiştirilemez.

### İ2-Ö4 (Ö). P2 uzaklıkları: olasılık metne

**Metin.** §9 madde 13 şununla değiştirilir:
> 13. **P2'nin istasyonları (İNCELEME-2 İ2-Ö4).** 20 olayın 6'sında istasyon > 50 km'de (IU.HNR 337, PS.PSI 213,
> NZ.MXZ 102, CN.LGNH 93, GE.MALT 57, C.ROC1 51 km). > 90 km'deki 4'ü etkisiz sayılırsa P2 Napa ölçeğinde (A %0,08)
> 0,68 / 0,59 / 0,93 olasılıkla geçer; 6'sı etkisiz sayılırsa 0,55 / 0,52 / 0,82 (CC₁₀ ≈ 0,5 / 0,5 ve mevsim %0,10 /
> 0,7; bağımsız benzetim, 300'lük havuz). Liste değiştirilmedi: büyük olaylarda kırığa uzaklık dış merkez uzaklığından
> küçüktür ve P2 olaylarının çoğu Napa'dan büyüktür.

§5.1 P2 "Geçme şartı" maddesinin sonuna eklenir:
> Önceden hesaplanan geçme olasılığı için §9 madde 13.

### İ2-Ö5 (Ö). E3'te A = 0 yanlış geçmesi

**Metin.** §6.1 "Okuma"nın ilk maddesi ("A = 0'da yanlış geçme ≈ düzey. …") şununla değiştirilir:
> - **A = 0'da yanlış geçme ≈ düzey.** Ortalamalar 0,051 / 0,042 / 0,043; en kötü havuz 0,060. Kesin Wilcoxon'un
>   p ≤ 0,05'teki ulaşılabilir boyutu n = 8…15 için 0,039–0,049'dur (n = 15'te 0,047). Simetrik gürültüde test %5'i
>   aşmaz. Fazlalık havuzların mevsim evresi dengesizliğidir (İNCELEME-2'nin 300'lük bağımsız havuzunda 0,034 / 0,100 /
>   0,035; 0,100'lük havuzun A = 0 medyanı −%0,010). Eşik değiştirilmedi.

§9 madde 5'in eski son cümlesi İ2-Ö1'in metniyle zaten değişmiştir.

### Küçük bulgular

**İ2-K1. Wells–Coppersmith.** §3.7 tablosunun son satırının "Durum" hücresi şu olur:
> Açık ikincil kaynakla doğrulandı: OpenQuake `scalerel.wc1994.WC1994.get_median_rld` (rake yokken
> 10^(−2,44 + 0,59 M), alt yüzey kırık boyu). Asıl makalenin Tablo 2A'sı okunmadı.

§9 madde 11 şununla değiştirilir:
> 11. **Wells–Coppersmith katsayıları** ikincil açık kaynakla doğrulandı (İNCELEME-2 İ2-K1).

**İ2-K2. Kuru çıktısının baytları belirsiz.** `kuru`'da `for m in set(mk) | set(mk_ust):` döngüsü
`for m in sorted(set(mk) | set(mk_ust)):` olur. Bir sonraki satırdaki iki `sorted(… key=lambda x: -x[1])` anahtarı
`key=lambda x: (-x[1], x[0])` olur. Kuru kip yeniden koşulur ve değişiklik listesindeki `tr5b_asama0_kuru.json`
sha256'sı yeni değerle güncellenir. Sayılar değişmez.

**İ2-K3. Kotada volkanik olaylar.** §2.3 "Kota" paragrafındaki "Olaylar (T, kimlik) sırasıyla işlenir." cümlesi
şununla değiştirilir:
> Olaylar, volkanik olanlar dahil (bilgi satırı 1 için kontrolleri gerekir), (T, kimlik) sırasıyla işlenir.
> Volkanik olayların kotaya yazılması K'yi değiştirmez (İNCELEME-2: 31 / 16 ve 28 / 15).

**İ2-K4. Adım 1–2'nin yeniden deneme sınırı.** §5.5'teki "3. ya da 4. adım iki kez başarısız olursa hüküm kesinleşir
(…)" cümlesi şununla değiştirilir:
> 1.–4. adımlardan herhangi biri iki kez başarısız olursa o adımın hükmü kesinleşir ("geçersiz (kod)", "geçersiz (kod
> ya da tasarım)" ya da "güç yok (4. adım: ölçü −%0,1'e kör)").

**İ2-K5. Başlık ve durum.** Dondurmada:
- Başlıktaki durum satırı "Sürüm 3, DONDURULDU (İNCELEME-1 ve İNCELEME-2 düzeltmeleri işlendi)" olur.
- §0 "Öncelik sırası"na `TR-5b_INCELEME-2.md`, `TR-5b_INCELEME-1.md`'den önce eklenir.
- Değişiklik listesine "Sürüm 2 → 3" tablosu eklenir: İ2-E1, İ2-E2, İ2-Ö1–Ö5 ve İ2-K1–K5 için birer satır.
- Değişiklik listesindeki dosya tablosu `tr5b_asama0.py`, `tr5b_asama0_kuru.json` ve bu inceleme dosyasının yeni
  sha256'larıyla güncellenir.

## D. Görevde sorulan kalemlere kısa hükümler

| Kalem | Hüküm |
|---|---|
| İNCELEME-1 E1–E3, Ö1–Ö9, K1–K12 | Hepsi işlenmiş (A). Ayrıntı düzeltmeleri İ2-E1, İ2-E2, İ2-Ö1–Ö5, İ2-K4 |
| K 31 / K_p 16, sha'lar | Bit düzeyinde yeniden üretildi |
| Güç tabloları | Bağımsız yazımla Monte Carlo saçılımı içinde |
| E3 | Bağımsız yazımla tutarlı. Uzaklık senaryosu eklenmeli (İ2-Ö1) |
| §2.3, §9/2 dinamik kota | KABUL |
| §9/3 yatay altı istek | DÜZELTİLİR, koşullu kural (İ2-E2) |
| §9/4 P1 birimi | KABUL, nicel sınırla (İ2-Ö2) |
| §6.1 A = 0 ve PK %40 | Eşik kalır; ad "güç yok (8. adım: pozitif kontrol geçmedi)"; olasılık önceden yazılır (İ2-Ö1, Ö5) |
| §9/13 P2 uzaklığı | KABUL, olasılıkla (İ2-Ö4) |
| Wells–Coppersmith | Doğrulandı, ikincil kaynak (İ2-K1) |
| LISTE_SHA | Sabitlenir ve her kipte denetlenir (İ2-E1) |
| Oynama payı, kapalı liste, körlük, tek koşu, yeniden açma, İstanbul | Sağlam. İki ek: dondurma aşama 0'dan önce, aşama 0'da tek koşu (İ2-Ö3) |
| Sürdürme ve 2 saat sınırı | Sürdürme çalışıyor (ağsız sınama: 30 + 90 = 120, çift kayıt 0). Hata satırları yeniden denenmiyor, eksiklikte G0 veriliyor, yarım satır `say`'ı düşürüyor (İ2-E1). `sure_sn` 6000 |

## E. Yeniden hesaplar ve betikler (`kayit/turetme/tr5/inc2/`)

| Betik | Ne yapar | Çıktı |
|---|---|---|
| `inc2_kota_p1.py` | Dinamik / statik / volkaniksiz kota; P1 istasyon sayıları | `inc2_kota_p1.json` |
| `inc2_p1_hacim.py` | P1 hacmi, istasyon düzeyi ile kontrol düzeyi | `inc2_p1_hacim.json` |
| `inc2_yatay_kayip.py <Ek1 önbellek>` | Sert ve koşullu yatay kuralın kaybı (Ek 1 Z yoklamasıyla; ağ yok) | `inc2_yatay_kayip.json` |
| `inc2_guc_bagimsiz.py` | Güç, 4. adım, σ*, P1 (tohum 515151, B 12 000; ≈ 5 sn) | `inc2_guc_bagimsiz.json` |
| `inc2_e3_bagimsiz.py [N]` | Bağımsız E3, uzaklık senaryoları (N = 300, 4 süreç, 224 sn) | `inc2_e3_bagimsiz.json` |
| `inc2_asama0_denetim.py <geçici kök>` | Ağsız sürdürme sınaması (`urlopen` yasaklı) | `inc2_asama0_denetim.json` |

Bağımsız E3 (300 istasyonluk havuz, 2000 çekiliş, A %0,08):

| Koşul | A = 0, 15 küme | A %0,08, 15 küme | PK: 12 sinyal + 3 sıfır | P2: 16 + 4 | P2: 14 + 6 | δ_ko medyanı (A 0 / 0,08), % |
|---|---|---|---|---|---|---|
| CC₁₀ ≈ 0,5, mevsim %0,05 | 0,034 | 0,722 | 0,551 | 0,678 | 0,548 | +0,001 / −0,041 |
| CC₁₀ ≈ 0,5, mevsim %0,10 | 0,100 | 0,587 | 0,464 | 0,589 | 0,521 | −0,010 / −0,051 |
| CC₁₀ ≈ 0,7, mevsim %0,05 | 0,035 | 0,968 | 0,836 | 0,930 | 0,824 | +0,001 / −0,046 |

Gürültüsüz denetim (mevsim 0, snr 100): iki uygulamada δ_ko ≈ −0,66 · A_k. Mevsimsiz, CC₁₀ ≈ 0,5'te 200'er istasyon:
medyan δ_ko −0,055 (bağımsız) ve −0,051 (`tr5b_yapay2.pk_istasyon`); sd 0,06–0,08 %.

Yatay kural (Ek 1, 60 dolu olay penceresi, taban 3 yıl): dilim orta ayında Z "var" oranı 0,972. Sert kuralın en az
kaybı 0,083, koşullu kuralın kaybı 0,000. Ek 1 kodları: 200 için 8905, 204 için 4837, 500 için 50.

Kaynak (Wells–Coppersmith doğrulaması): [OpenQuake `wc1994` kaynak kodu](https://docs.openquake.org/oq-engine/master/manual/_modules/openquake/hazardlib/scalerel/wc1994.html).
