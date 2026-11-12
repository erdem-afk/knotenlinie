DÜZELTMEYLE KABUL

# TR-6a ön kayıt: bağımsız inceleme 2 (son tur)

İncelenen: `TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md` (TASLAK sürüm 2, 12 Kasım 2026). Taslağı ve İNCELEME-1'i ben
yazmadım. Dayanak olarak okundu: `TR-6a_INCELEME-1.md`; `TR-6_SAYIM.md` Ek 1; `kayit/turetme/tr6/` altında
`tr6a_onkayit_sayilar.py/.json`, `tr6a_olay_listesi.json`, `tr6a_onbellek_kor.py`, `tr6a_sifir_buyukluk.py/.json`,
`tr6a_inc1_denetim.py/.json` ve `tr6_a_kapi.py` (`kumele`, `gereken_n0`, `binom_ust`, `maxc`).

**Körlük.** Hiçbir katalog sorgusu yapılmadı. Hiçbir lobda oran, oran değişimi ya da ΔCFF hesaplanmadı. Ek 1 önbelleği
yalnız bir kez ve yalnız `tr6a_onbellek_kor.oku_sorgu` üzerinden okundu: `tr6a_sifir_buyukluk.py` depo dışı bir kopyada
yeniden koşuldu. Çıktısı yalnız katalog toplamlarıdır. Olay sonrası pencere için hiçbir sayı üretilmedi.

**Yeniden üretim.** Bütün betikler `python3 -I -B` ile ve depo dışı bir kopyada koşuldu
(`/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/inc2/kopya/`). Depodaki dosyalara yazılmadı,
`__pycache__` kalmadı. Bağımsız denetim betikleri `…/scratchpad/inc2/bag/b1.py`–`b4.py`'dir. Bunlar binom ve Poisson
değerlerini scipy ile, taslağın kodundan ayrı yazar; yapay ortak-veri benzetimi de yapar. Depoya bu rapor dışında dosya
eklenmedi. Sonuçlar:
- `tr6a_onkayit_sayilar.py` iki dosyayı bayt bayt aynı üretiyor: liste sha256 0cde4fa1…048f, sayılar 18e6a2fc…34d1.
- `tr6a_inc1_denetim.py` çıktısı bayt bayt aynı (4ff6f4d0…050a, 46 sn).
- `tr6a_sifir_buyukluk.py` (maskeli) çıktısı bayt bayt aynı (ff20aebf…c732).
- Girdi sha256'ları (8da8ba3c…, 5a90b0eb…, ff20aebf…) ve ham önbellek arşivi (f350d2e0…) metinle aynı.
- `--md` çıktısındaki 136 tablo satırının hepsi metinde birebir var. Bunlar §6.1 eşik tablosu, hüküm olasılıkları,
  p₀ ızgarası, testere dişi, güç tablosu ve Ek A'dır.
- scipy ile bağımsız denetim (K = 18–80, p₀ 0,50–0,60) uyuşuyor: c(K; p₀), gerçek α, güç, h(K), testere dişi çözümü
  ve ilk/kalıcı K değerleri. Uyuşmayan hücre yok.
- Poisson H0 P(D) değerleri 0,4459 / 0,4585 / 0,4680 / 0,4783 / 0,4869 tutuyor; P(A) 0,4606 tutuyor. §4.3 α satırında
  yalnız dördüncü ondalıkta ±0,0001 yuvarlama farkı var: kod α'yı yuvarlanmış P(D)'den hesaplıyor.

## Hüküm

Sürüm 2 İNCELEME-1'in bütün bulgularını işlemiş. Sapmaların hepsi gerekçeli ve sayıları yeniden üretiliyor. §16'daki
15 sapmanın 14'ü kabul edilebilir. Bir tanesi kabul edilemez: J < 30 kuralı (A1). Testere dişi p₀ ızgarasında tek
anlamlı. Kalibrasyon, sahte ve gerçek oylar aynı veriyi paylaşsa da α'yı korur (yapay hesap, B2).

Dondurmadan önce üç engelleyici açık kapanmalı:
1. **J < 30 kuralı (A1).** Kalibrasyon zayıfken α korumasını kaldırıyor ve p̂₀ = 0,8 gibi açık bir yanlılığı bile yok
   sayıyor.
2. **Hüküm adları (A2).** Hüküm adlarının kapalı bir listesi, bileşim sırası ve §13'e taşıma ölçütü yok. Bu, olay sonrası
   veri görüldükten sonra "hangi H1 Marmara'ya taşınır" kararını açık bırakıyor. "Koşulmadı (yöntem)" çıkışının da
   kalıbı yok.
3. **S7 nötr kontrolünün kapısı yok (A3).** π = 0,1572'de n ≤ 4 olan pencerede düşüş oyu tanım gereği 0'dır. Bu yüzden
   olaysız nötr bölgeler McNemar'ı kendiliğinden gölge lehine "ayrışmış" gösterir. A2'nin (İNCELEME-1) tamlık koruması
   bu noktada dişsiz kalıyor.

Altı önemli bulgu (B1–B6) ve on beş küçük bulgu (K1–K15) aşağıdadır. Her biri metne aynen konabilecek bir düzeltme
metniyle verildi. Düzeltmeler işlenince üçüncü bir inceleme turu gerekmez. Yalnız şu metin dışı işler kalır:
- `tr6a_onkayit_sayilar.py`'ye küçük bir ekleme: B1, A1 ve K4 sayıları için;
- listenin yeniden üretilmesi ve sha256'sının metne yazılması: liste içeriği değişmezse sha256 da değişmez.

Bu ikisi kod incelemesinde (§9 adım 4) denetlenir.

---

## A. Engelleyici bulgular

### A1. J < 30 kuralı α korumasını kaldırıyor ve p̂₀'ı yok sayıyor (§16 sapma 2)

- **Bulgu.** §4.6'ya göre J < 30 ise p₀ = p₀⁺ = 0,50 olur ve yalnız ada bir not düşülür. Bunun iki sonucu var:
  1. Kalibrasyonun bulunma nedeni aşırı saçılımdır (§4.3 tablosu). Bu koşulda α K = 23'te 0,0625'e, K = 23–45
     aralığında en çok 0,072'ye çıkar (N0 31,36, φ = 5, P(D) = 0,5151; bağımsız hesap). J < 30 tam da bu korumanın en
     çok gerektiği zayıf veri durumudur.
  2. J < 30 iken p₀ > 0,60 denetimi de yapılmaz. J = 29 ve p̂₀ = 0,70 gibi açık bir yanlılık bile p₀ = 0,50 ile hükme
     gider.
- **Ne olasılıkla?** Önsayımda J = 64/87. J < 30 için geçerli pay K = 23'te %43'ün altına inmeli. Olasılık düşük ama
  sıfır değil: B2'deki "sahte kapı" eklenince J biraz daha düşer. Kural yine de tek anlamlı ve tutucu olmalı.
- **Önerilen kural.** J < 30'da p̂₀ yalnız yukarı yönde kullanılır ve taban 0,52'dir. p₀ = 0,52'ye karşı en kötü ızgara
  hücresinde (P(D) 0,5151) gerçek α K = 23–45'te en çok **0,044**'tür. p₀ = 0,50'ye karşı bu değer 0,072'dir. P(D) =
  0,53 dünyasında α en çok 0,061'e çıkar; buna karşı ayrıca p₀ > 0,60 kuralı ve etiket durur. Güç bedeli: K = 23 /
  26 / 29 / 33'te 0,654 / 0,685 / 0,834 / 0,819. Testere tablosunun p₀ 0,52 sütunu bunu zaten çözüyor; yeni tablo
  gerekmez.
- **Düzeltme metni (§4.6, "J < 30 ise kalibrasyon yapılmaz…" maddesinin yerine):**

  > - **J < 30 ise kalibrasyon zayıftır.** O zaman p₀ = max(0,52; ⌈100 S / J⌉/100) ve p₀⁺ = max(0,52; ⌈100 S⁺ / J⌉/100)
  >   olur (S⁺ = Σ A'_ij; J = 0 ise ikisi de 0,52). p₀ > 0,60 ve p₀⁺ > 0,60 kuralları aynen uygulanır. Hüküm adına
  >   "kalibrasyon zayıf: J = …, p₀ = …" niteleyicisi eklenir (§6.4). Gerekçe: §4.3 aşırı saçılım ızgarasının en kötü
  >   hücresinde (N0 31,36, φ = 5) P(D | H0) = 0,5151'dir. Bu dünyada p₀ = 0,50'ye karşı gerçek α K = 23–45'te en çok
  >   0,072, p₀ = 0,52'ye karşı en çok 0,044'tür. J < 30'da p̂₀ yalnız p₀'ı yukarı itebilir.

- **Ek düzeltmeler:**
  - §1 hüküm satırının ikinci cümlesinin sonuna: "(J < 30 ise taban 0,52; §4.6)".
  - §5 işlem sırasında "p₀ kalibrasyonu (§4.6)" yerine: "p₀ kalibrasyonu (§4.6, J < 30 kuralı dahil)".
  - §16 madde 2'nin yerine: "**A1, p₀ > 0,60 kuralı ve J < 30 kuralı** düzeltme metninde yoktu. p₀ = 0,60'ta güç 0,80'e
    ancak K ≥ 62'de ulaşır. J < 30'da p₀ tabanı 0,52'dir (İNCELEME-2 A1)."
  - §8 üst bilgisine "J < 30 kuralı uygulandı mı" eklenir.

### A2. Hüküm adlarının kapalı listesi, bileşim sırası ve §13'e taşıma ölçütü yok

- **Bulgu.** Hüküm adı birkaç yerden geliyor ve bunlar birbirine bağlanmamış:
  - §6.3 beş kalıp veriyor;
  - §6.2 altı ayrı ad türetiyor;
  - §5 ve §4.6 iki ek getiriyor ("tasarım gücünün altında", "p₀ kalibre edilemedi");
  - §8 tablosu ise yalnız "H1 / H0 / ayırt edilemez / güç yok" diyor.

  Açık kalan noktalar:
  1. **Sıra belirsiz.** §6.2 "sırayla uygulanır" diyor. Kural 1 H1'i "ayırt edilemez"e çevirirse kural 2 ve 2a'daki
     "H1 verilmişse" koşulunun özgün hükmü mü, yeni adı mı kastettiği yazılmamış. Birden çok düşürücü uyarsa hangi adın
     yazılacağı da belirsiz.
  2. **§13 belirsiz.** "H1 (yorum kurallarından geçmiş hâliyle)" ifadesi şu adların Marmara'ya taşınıp
     taşınmayacağını söylemiyor: "H1 (nötr kontrolden ayrışmadı)", "H1 (megathrust kümelerine dayanıyor)", "H1 (pozitif
     kontrol koşulamadı)". Bu karar olay sonrası veri görüldükten sonra verilecek. Ön kayıtta kalmaması gereken bir
     serbestliktir.
  3. **Kalıbı olmayan çıkışlar.**
     - §3.3: "Bir sınama başarısız olursa olay sonrası veri indirilmez". Hüküm adı yok.
     - §9 adım 2: "yöntem yapay sınamada yetersiz". Kalıbı yok.
     - "Kalibrasyonsuz" ya da "kalibrasyon zayıf" eki için de kalıp yok.
- **Düzeltme metni (yeni §6.4, §6.3'ten sonra):**

  > ### 6.4 Hüküm adlarının kapalı listesi ve bileşimi
  >
  > Sonuç dosyasındaki hüküm adı yalnız bu kurallarla kurulur; başka ad yazılmaz.
  >
  > 1. **Taban hüküm.** Tam olarak biri seçilir; aşağıdakilerden ilk uyan geçerlidir.
  >    - (a) **"koşulmadı (yöntem: Okada sınaması | yapay katalog sınaması | tamlık sınaması)".** §3.3 doğrulaması,
  >      §9 adım 2'nin yapay katalog sınaması ya da tamlık yedek merdiveni §9 adım 2'deki sonuç kuralıyla kesin
  >      biçimde tutmadı. Olay sonrası veri indirilmez, aday elenmez. Yeniden açma ancak ayrı bir ön kayıtla olur.
  >    - (b) **"güç yok"**: K_kapı < 23 (§5).
  >    - (c) **"güç yok (ölçü yanlı)"**: p₀ > 0,60 (§4.6).
  >    - (d) **"H1", "H0" ya da "ayırt edilemez"** (§6.1). c(K) ≤ h(K) olan bir K'de X ≥ c ise taban H1'dir.
  > 2. **Düşürücüler.** Yalnız taban H1'e uygulanır. Hepsi özgün taban H1'e göre denetlenir; birinin uygulanması ötekilerin
  >    koşulunu değiştirmez. Uyanlar §6.2 sırasıyla, noktalı virgülle aynı parantezde yazılır ve taban "ayırt
  >    edilemez" olur. Düşürücüler:
  >    - "pozitif kontrol tutmadı" (§6.2 kural 1);
  >    - "olay öncesi düşüş eğilimi" (kural 2);
  >    - "nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu" (kural 2a).
  >
  >    Örnek: "ayırt edilemez (pozitif kontrol tutmadı; nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu)". Düşürülen
  >    hükme madde 4'teki H0 ve ayırt edilemez ekleri uygulanmaz. X, c ve p yine yazılır.
  > 3. **Niteleyiciler.** Düşürülmemiş H1'e eklenir; bu sırayla, tek parantezde, noktalı virgülle:
  >    - "pozitif kontrol koşulamadı";
  >    - "negatif kontrol koşulamadı";
  >    - "nötr kontrol koşulamadı" ya da "nötr kontrolden ayrışmadı";
  >    - "megathrust kümelerine dayanıyor";
  >    - "tasarım gücünün altında: güç …";
  >    - "kalibrasyon zayıf: J = …, p₀ = …".
  >
  >    Örnek: "H1 (nötr kontrolden ayrışmadı; tasarım gücünün altında: güç 0,654)".
  > 4. **H0 ve ayırt edilemez ekleri.** Bu sırayla, cümle olarak:
  >    - ters yön notu (§6.1);
  >    - "pozitif kontrol de tutmadı: hat ya da model başarısız; ayrılamaz" (§6.2 kural 1);
  >    - "olay öncesi artış eğilimiyle ayırt edilemez" (kural 2);
  >    - etkin N0 cümlesi (§6.2 kural 6);
  >    - "(tasarım gücünün altında: güç …)";
  >    - "(kalibrasyon zayıf: J = …, p₀ = …)".
  > 5. **§13'e taşıma.** §13'ün H1 cümlesi yalnız hüküm adı tam olarak "H1" ya da "H1 (tasarım gücünün altında: güç …)"
  >    ise yazılır. Başka herhangi bir niteleyici varsa §13 cümlesi yazılmaz; yerine "Marmara'ya taşınmadı:
  >    <niteleyici>" yazılır.

- **Ek düzeltmeler:**
  - §6.2 başlığı: "### 6.2 Yorum kuralları (hükmü değiştirmez, adını niteler; §6.4'e göre bileşir)".
  - §6.2 kural 2'deki kalın ad **"H1, olay öncesi eğilimle ayırt edilemez"** yerine: düşürücü "olay öncesi düşüş
    eğilimi" (§6.4).
  - §6.3'e iki kalıp eklenir:
    - **Koşulmadı (yöntem):** "TR-6a koşulmadı: <sınama> önceden yazılan ölçütü tutmadı (<ölçüt, değer>). Olay sonrası
      veri indirilmedi. Aday elenmedi; yeniden açma ayrı ön kayıtla."
    - **Kalibrasyon zayıf eki:** "Olay öncesi sahte zamanlardan yalnız J = … geçerli oy elde edildi (< 30). p₀ tabanı
      0,52 alındı (§4.6)."
  - §8 tablosunun "Hüküm / etiket" hücresi: "§6.4'teki kapalı listeden ad (taban + düşürücüler ya da niteleyiciler +
    ekler)".
  - §13 ilk maddenin başı: "H1 çıkarsa ve §6.4 madde 5'in taşıma ölçütü tutarsa Marmara'ya taşınan tek cümle: …".

### A3. S7 nötr kontrolünün kapısı yok: olaysız nötr bölge McNemar'ı kendiliğinden "ayrışmış" gösterir

- **Bulgu.** Nötr bölgede kapı yok ("Kapı yok; n = 0 ise oy 0"). Oy kuralında π = 0,15720 iken düşüş oyu ancak
  n ≥ 5'te 1 olabilir: (1 − π)⁴ = 0,505 > 0,5, (1 − π)⁵ = 0,425. Bu yüzden n_nt ≤ 4 olan her nötr pencerede D_nt = 0
  kendiliğinden olur. Sonuç:
  - b = #(D_g = 0, D_nt = 1) küçülür; McNemar p = P(Binom(a + b, 0,5) ≥ a) küçülür. Bütün nötr bölgeler seyrekse b = 0
    ve X ≥ 4 için p = 0,5^X ≤ 0,10 olur. Nötr kontrol her zaman "ayrıştı" der.
  - X_nt ≥ c(K; p₀) koşulu da seyrek nötr bölgelerde tutamaz.

  Yani kural 2a, İNCELEME-1 A2'nin hedef aldığı tamlık yapay olgusunu tam da nötr bölgenin seyrek olduğu yerlerde
  görmez. Bu, H1 yönünde bir açıktır. Nötr bölge |ΔCFF| ≤ 2 kPa ve r_k ≤ gölgenin en uzak r_k'si ile sınırlı; açık
  denizde seyrek kalması olasıdır. Ayrıca Mc_kul, gölgede olduğu gibi Mc_son ile yükselir.
- **Düzeltme metni (§7 S7 satırının "Tanım" ve "Kapı / küme seti" hücrelerinin yerine):**

  > | **S7 nötr kontrol** | Ana K temsilcileri. Nötr bölge: bölgede \|ΔCFF\| ≤ 2 kPa olan ve r_k'si gölge lobunun en uzak hücresinin r_k'sini aşmayan hücreler. Kendi Mc_lob_nt'si (§3.5 kuralı), aynı Mc_son, Mc_kul,nt = max(Mc_lob_nt, Mc_son); aynı kümesizleştirme ve oy (X_nt, Y_nt). **Nötr kapı:** olay öncesi N0_nt (Mc_lob_nt ile, ön pencere, kümesizleştirilmiş) ≥ 31,36 olay/yıl (n_on,nt ≥ 155). K_nt bu kümelerin sayısıdır ve manifestte, olay sonrası indirmeden önce yazılır. X_nt, Y_nt ve McNemar yalnız bu K_nt kümede sayılır: a = #(D_gölge = 1, D_nt = 0), b = #(D_gölge = 0, D_nt = 1), p = P(Binom(a + b, 0,5) ≥ a); a + b = 0 ise p = 1. K_nt < 10 ise S7 "koşulamadı". Kapı dışı kümelerin nötr oyları bilgi olarak yazılır. | ana K'nin alt kümesi (K_nt) |

- **Düzeltme metni (§6.2 madde 2a'nın yerine):**

  > 2a. **Nötr kontrol (§7 S7).**
  > - K_nt < 10 ise H1 "nötr kontrol koşulamadı" niteleyicisini alır.
  > - K_nt ≥ 10, H1 verilmiş ve X_nt ≥ c(K_nt; p₀) ise "nötr bölgede de düşüş: tamlık ya da ağ yapay olgusu"
  >   düşürücüsü uygulanır (§6.4) ve §13'e hiçbir şey taşınmaz.
  > - K_nt ≥ 10, H1 verilmiş, X_nt < c(K_nt; p₀) ve McNemar p > 0,10 ise "nötr kontrolden ayrışmadı" niteleyicisi
  >   eklenir.
  >
  > Gerekçe: π = 0,15720'de n ≤ 4 olan pencerede düşüş oyu tanım gereği 0'dır. Kapısız bir nötr bölgede D_nt = 0
  > kendiliğinden olur ve McNemar gölge lehine ayrışma gösterir. Kesin hesap (`tr6a_inc1_denetim.json`
  > `mcnemar_gucu`): gölgede p 0,75, nötrde 0,4585 iken McNemar p ≤ 0,10'un gücü K_nt = 23'te 0,677, 28'de 0,757,
  > 33'te 0,819, 37'de 0,860.

- §9 adım 3 manifest içeriğine eklenir: "nötr kapı N0_nt'leri ve K_nt".
- §10 "Negatif ve nötr kontrol" maddesine eklenir: "Nötr kapı yüzünden K_nt < 10 olasılığı küçük değildir. O durumda
  H1 yalnız 'nötr kontrol koşulamadı' niteleyicisiyle verilebilir ve §13'e taşınmaz (§6.4)."

---

## B. Önemli bulgular

### B1. Pozitif kontrolün kapısı (N0⁺ ≥ 3,0) hattı değil sayı azlığını sınıyor

- **Bulgu.** B1'in (İNCELEME-1) amacı, pozitif kontrolün geometri ya da sayı azlığı yüzünden tutmayıp H1'i sebepsiz
  düşürmesini önlemekti. 3,0 olay/yıl kapısı buna yetmiyor. Pozitif lobda yalnız +10 kPa'lık Dieterich adımı
  (Aσ 19 kPa) ile küme başına artış oyu olasılığı (taslağın `Oy` sınıfıyla kesin hesap):

  | N0⁺ (/yıl) | 3 | 5 | 10 | 20 | 31,36 |
  |---|---|---|---|---|---|
  | P(A), kalıcı adım | 0,727 | 0,823 | 0,928 | 0,986 | 0,997 |
  | P(A), t_a 1,9 yıl | 0,627 | 0,716 | 0,832 | 0,930 | 0,971 |
  | P(A \| H0) | 0,376 | 0,406 | 0,429 | 0,451 | 0,461 |

  Başarı ölçütü X⁺ ≥ c(K⁺; 0,50). Kapının hemen üstündeki loblarda (P(A) 0,727) S1'in tutma olasılığı K⁺ = 10 / 15 /
  20 için 0,196 / 0,381 / 0,524'tür. N0⁺ ≥ 10'da (P(A) 0,928) bu olasılık 0,841 / 0,981 / 0,998 olur. Gerçek pozitif
  loblarda ΔCFF çoğunlukla +10 kPa'dan büyüktür. Ama kontrolün dayanağı bu en küçük adım olmalıdır. §10'daki "yapay
  dünyada 0,97–1,00" cümlesi N0 31,36 için doğrudur, 3,0 kapısı için doğru değildir.
- **Düzeltme metni (§7 S1 satırında "≥ 3,0 olay/yıl olanlar" yerine):** "≥ 10,0 olay/yıl (n_on⁺ ≥ 50) olanlar".
- **Düzeltme metni (§10 "Pozitif kontrol" maddesinin yerine):**

  > - **Pozitif kontrol.** Yalnız +10 kPa'lık kalıcı adımla bile küme başına artış oyu N0⁺ = 10'da 0,928'dir. S1 bu
  >   durumda K⁺ = 10'da 0,84, K⁺ = 15'te 0,98 olasılıkla tutar (`tr6a_onkayit_sayilar.json` `pozitif_kapi`). Gerçek
  >   pozitif loblarda ΔCFF çoğunlukla daha büyüktür. K⁺ < 10 olasılığı, kapı 3,0'dan 10,0'a çıktığı için sürüm 2'deki
  >   ≈ 0,2'den büyüktür; yazarın önseli ≈ 0,3.

- **Kod:** `tr6a_onkayit_sayilar.py`'ye `pozitif_kapi` anahtarı eklenir. Bu anahtar N0⁺ ∈ {3, 5, 10, 20, 31,36} ve
  t_a ∈ {∞; 1,9 yıl} için P(A), ayrıca K⁺ ∈ {10, 15, 20} için S1 tutma olasılığını yazar. Yukarıdaki tablo bu
  anahtardan alınır. Hepsi yapay hesaptır.

### B2. Sahte kalibrasyon: temsil, geçerlilik geometrisi ve ortak veri

Görevin sorduğu üç nokta tek tek:

1. **Kalibrasyon örneklemi hükme giren kümeleri temsil ediyor mu?** Kısmen. Önsayımda 29 kümenin 5'inde geçerli sahte
   zaman yok:
   - usp0006qh3, kaba N0 96,8;
   - 2004 Sumatra, 52,8;
   - Tohoku, 4501;
   - 2012 Hint Okyanusu, 111,2;
   - Mendocino 2024, 52,5.

   Bunlar yalnız en büyük N0'lı kümeler değil; N0 sırasında 7., 8., 21., 24. ve 29. sıradalar. Asıl yoksunluk M 9,1
   olaylarıdır. Bunun α'ya etkisini yapay olarak ölçtüm (`b3.py`). Yıllık oranın sabit varyasyon katsayısıyla (CV)
   saçıldığı model kullanıldı: φ = 1 + CV² N0, yani saçılım N0 ile büyür. K = 23'ün 5–8 kümesi yüksek N0'lı (500–1000)
   ve sahte zamansız alındı; kalan kümeler N0 50 ve üç geçerli sahte zamanla alındı. Sonuç:

   | CV | yüksek N0'lı küme | α, p₀ 0,50 | α, §4.6 kalibrasyonuyla |
   |---|---|---|---|
   | 0,1 | 5 × 1000 | 0,033 | 0,026 |
   | 0,2 | 5 × 1000 | 0,048 | 0,034 |
   | 0,2 | 8 × 1000 | 0,051 | 0,032 |
   | 0,3 | 5 × 500 | 0,064 | 0,041 |
   | 0,3 | 8 × 1000 | 0,070 | 0,041 |

   Bu modelde P(D | H0) en çok ≈ 0,53'e çıkıyor (CV 0,3, N0 500). Orta N0'lı kümeler saçılımın çoğunu yakalıyor.
   Temsil eksikliği α'yı korumasız bırakmıyor. Bilgi satırı ve §11 metni yeter; bağlayıcı yeni kural gerekmez.
2. **p̂₀ hükümden bağımsız mı?** Tam değil. Sahte j = 1'in son penceresi [t0 − 365 g, t0 − 30) gerçek ön pencerenin
   içindedir; sahte ön pencereler de gerçekle örtüşür. Yapay hesapta (`b2.py`; aynı Gamma beyaz gürültü modeli,
   12 bölütlü ortak zaman ekseni) korelasyon küçük:
   - corr(D, D'₁) = −0,019 … −0,024;
   - tam yordamın α'sı, sahte oylar bağımsız alındığındakinden 0,001–0,005 yüksek (Monte Carlo standart hatası
     ≈ 0,0013);
   - bütün hücrelerde (N0 31,36 / 100 / 500; φ 1 / 3 / 5; K 23 / 28) α ≤ 0,037.

   Kabul edilebilir; §11'e yazılmalı.
3. **Gürültü ve yukarı yuvarlama.** Kabul (bkz. §E sapma 1). Gürültü yalnız gücü düşürür; α'yı yükseltmez.

Bunlara ek olarak üç düzeltme gerekiyor:

- **(a) Sahte kapı yok.** Sahte oylar, sahte ön penceredeki sayıya bakılmadan hesaplanıyor. Gerçek oylar ise kapıdan
  geçmiş (n_on ≥ 155) loblardan geliyor. Ağlar zamanla yoğunlaştığı için sahte ön pencereler daha seyrek olabilir.
  Poisson H0'da P(D) N0 ile artar: 17,08'de 0,4459, 31,36'da 0,4585. n ≤ 4'te ise D' tanım gereği 0'dır. Kapı altı
  sahte oylar p̂₀'ı gerçek oyların H0 düzeyinin altına çeker; bu, H1 yönüdür.
- **(b) Geçerlilik ve maske geometrisi farklı yazılmış.** Geçerlilik ölçütü 3 L_A + 3 L_temsilci, §9 maskesi 4 L_A.
  Bu çelişki değil, çünkü manifest sahte oyları kendi indirmesinden maskesiz sayar. Ama metin bunu söylemiyor. 4 L_A +
  3 L_temsilci ile J 64 yerine 61 olurdu; değiştirmeye gerek yok.
- **(c) Asimetri.** Sahte pencerede bir komşu A'nın olay sonrası penceresi son pencereyle örtüşürse sahte zaman
  atılıyor. Gerçek oyda A son pencereye düşerse §3.7 kesmesi var. Ama A, t0'dan önceki bir yılda olduysa (artçıları
  hem ön pencerenin sonunda hem son pencerede) hiçbir önlem yok. Omori sönümü ön oranı şişirir; bu da H1 yönüdür.
  Önsayımda tam 5 küme böyle; bunlar sahte j = 1'i geçersiz olan kümelerle aynı: usp0006qh3, 2004 Sumatra,
  usp000hrw0, Tohoku, 2012 Hint Okyanusu.

- **Düzeltme metni (§4.6, "Sahte zamanın geçerliliği" paragrafının iki maddesinden sonra):**

  > Ayrıca sahte j, sahte ön penceredeki kümesizleştirilmiş gölge lobu sayısı n_on' (sahte Mc_lob ile, §3.6'nın 730 g
  > tamponuyla) 155'ten küçükse geçersizdir (neden: "sahte kapı"; manifestte yazılır). Gerekçe: gerçek oylar kapıdan
  > geçmiş loblardan gelir. Poisson H0'da P(D) N0 ile artar ve n ≤ 4'te düşüş oyu tanım gereği 0'dır. Kapı altı sahte
  > oylar p̂₀'ı aşağı, H1 yönüne çeker.
  >
  > Geçerlilik ölçütü (3 L_A + 3 L_temsilci) "olay yok" dünyasının fiziksel ölçütüdür. §9 adım 3'teki 4 L_A maskesi
  > yalnız ad hoc önbellek okumaları içindir; manifest sahte oyları adayın kendi indirmesinden, maskesiz sayar.

- **Düzeltme metni (§4.6 "Kestirim ve eşik" listesinin sonuna, bilgi):**

  > - Bilgi (hükmü değiştirmez): manifest şunları ayrıca yazar:
  >   - p̂₀'ı, kapı N0'ı K_kapı medyanının altında ve üstünde kalan kümeler için ayrı ayrı;
  >   - hiç geçerli sahte zamanı olmayan küme sayısı K_0 ve bu kümelerin kimlikleri, kapı N0'ları.

- **Düzeltme metni (§7 B3 satırının "Tanım" hücresinin sonuna):**

  > "Öncül komşulu" kümeler: temsilcinin [t0 − 365 g, t0) aralığında, dış merkez uzaklığı < 3 L_A + 3 L_temsilci olan
  > bir havuz olayı A (grup dışı) varsa küme işaretlenir. Önsayımda 5 küme işaretli: usp0006qh3,
  > official20041226005853450_30, usp000hrw0, official20110311054624120_30, official20120411083836720_20. Bu kümeler
  > çıkarılmış hâliyle X, K ve c(K; p₀) de yazılır.

- **Düzeltme metni (§11 madde 12'nin sonuna):**

  > Sahte ve gerçek pencereler veri paylaşır (sahte j = 1'in son penceresi gerçek ön pencerenin içindedir). Yapay hesap
  > (İNCELEME-2; Gamma beyaz gürültü, N0 31,36–500, φ 1–5, K 23 ve 28) şunu verdi: gerçek ve sahte oy arasında
  > korelasyon ≈ −0,02; tam yordamın α'sı, bağımsız sahte oy varsayımındakinden 0,001–0,005 yüksek ve en çok 0,037.

- **Düzeltme metni (§11 madde 17'nin sonuna):**

  > Yapay hesap (İNCELEME-2): yıllık oran CV'si 0,1–0,3 iken (φ = 1 + CV² N0), K = 23'ün 5–8 kümesi N0 500–1000 ve
  > sahte zamansız, kalanı N0 50 olsun. Bu durumda kalibrasyonlu α 0,026–0,041, kalibrasyonsuz (p₀ 0,50) α 0,033–0,070
  > olur. "Sahte kapı" (§4.6) kalan küçük yanlılığı tutucu yöne çeker.

### B3. Yapay sınamalar: Monte Carlo gürültüsü, tohum, başarısızlığın sonucu ve yedek (c)'nin yayılımı

Bu sınamalar gerçek veri görmez; körlük sorunu yoktur. Ama dört eksik, sınavın kendisini rastlantıya bağlıyor:

1. **Monte Carlo gürültüsü yanlış "başarısız" üretiyor.** Tamlık ölçütü "fark ≤ 0,02, en az 4000 deneme" diyor. 4000
   denemede standart hata (SE) ≈ 0,0079. Kusursuz bir kuralda bile tek hücrenin gürültüyle 0,02'yi aşma olasılığı
   0,0057'dir. 96 hücrenin en az birinde bu olasılık ≈ 0,42'dir. Her basamak ≈ %42 olasılıkla gürültüyle düşer;
   dört basamağın hepsi ≈ 0,03 olasılıkla düşer ve TR-6a sebepsiz kapanır. Bağlayıcı basamak da rastlantıyla seçilir.
   20 000 denemede SE ≤ 0,0036 olur, 0,02 = 5,6 SE'dir ve 96 hücrede yanlış başarısızlık olasılığı < 1e−6'dır.
2. **Tohum yazılmamış.** Tohum yazılmazsa sınama tutana dek yeniden koşulabilir.
3. **Genel yapay katalog sınamasının sonucu tanımsız.** "Ölçütler" listelenmiş, tutmazsa ne olacağı yazılmamış. Ayrıca
   lobda GK tipi ikincil diziler varken Δτ = 0 dünyasının beklenen P(D)'si kesin Poisson değeri değildir:
   kümesizleştirme artıkları aşırı saçılımdır. Birinci ölçüt doğru çalışan bir hatta da tutmayabilir.
4. **Yedek (c)'nin yayılımı yazılmamış.** Son pencere 90 g'de başlarsa üç şey değişir: sahte ve S2 pencereleri,
   §3.7'deki T_son < 60 g ölçütü, D2. Örneğin 2004 Sumatra kümesinin T_son'u 61,6 g'den 1,6 g'ye iner.

- **Düzeltme metni (§9 adım 2, "Yapay katalog sınaması" alt maddesinin yerine):**

  > - **Yapay katalog sınaması** iki biçimde koşulur. Tohum 20261114, her ölçüt için en az 20 000 deneme.
  >   - (i) Lobda arka plan saf Poisson'dur; bölgede ikincil diziler vardır. Ölçütler:
  >     - Δτ = 0 dünyasında gölge düşüş oyu oranı N0 ∈ {31,36; 100; 500} için §4.3'teki kesin değerle 3,5 SE içinde;
  >     - kalıcı −10 kPa dünyasında N0 31,36'da 0,987 ile 3,5 SE içinde;
  >     - Δτ_est medyanı §4.5 tablosuyla 3,5 SE içinde.
  >   - (ii) Lobda da GK tipi ikincil diziler vardır. Ölçüt: Δτ = 0 dünyasında p̂₀'ın beklenen değeri, gerçek düşüş oyu
  >     oranıyla 3,5 SE içinde. Bu biçimde P(D)'nin kendisi bilgi olarak yazılır.
  >
  >   Bir ölçüt tutmazsa kod hatası aranır. Bulunan her hata düzeltilir, hata listesi commit edilir ve bütün sınama aynı
  >   tohumla yeniden koşulur. Hata bulunamazsa TR-6a "koşulmadı (yöntem: yapay katalog sınaması)" diye kapanır (§6.4).

- **Düzeltme metni (§9 adım 2, tamlık sınamasında "(en az 4000 deneme)" yerine):** "(hücre başına en az 20 000 deneme,
  standart hata ≤ 0,0036; tohum 20261115; lobda arka plan saf Poisson)".
- **Düzeltme metni (aynı yerde, "Aşarsa yedekler sırayla denenir…" cümlesinin sonuna):** "Her basamak bir kez, aynı
  tohumla koşulur. Bütün basamakların bütün hücre sonuçları, manifestten önce commit edilir."
- **Düzeltme metni (yedek (c) maddesinin sonuna):**

  > (c) seçilirse 90 g başlangıcı her yerde uygulanır:
  > - §3.7'deki T_son < 60 g ölçütü yeni başlangıçla yeniden uygulanır. Önsayımda 2004 Sumatra kümesi T_son 1,6 g ile
  >   çıkar.
  > - Sahte son pencereler [t'_j + (t_s − t0) + 90 g, t'_j + e) olur.
  > - S2'nin "son" penceresi [t0 − 305 g + (t_s − t0), t0 − 30 g) olur; π_nk aynı formülle hesaplanır.
  > - D2 satırı kalkar.
  > - Mc_son alt pencereleri [90, 180) ve [180, 365) olur.

- "Hiçbiri tutmazsa…" cümlesindeki "yöntem yapay sınamada yetersiz" yerine: "koşulmadı (yöntem: tamlık sınaması)"
  (§6.4).

### B4. Okada doğrulaması: beş sınama çözümü belirler, ama yönelim, işaret ve ΔCFF izdüşümünü sınamaz

- **Bulgu.** Beş sınama, verilen geometride yarı uzay çözümünü sağlam biçimde denetler: yüzeyde çekme sıfır, denge,
  süreksizlik, türev, nokta kaynak sınırı. Ancak şu hataları göremez:
  1. **Yönelim ve işaret hataları.** Doğrultu ya da eğim yönü, coğrafi dönüşüm ve rake işaretindeki hatalar
     "kendi içinde tutarlı ama yanlış yönlü" bir çözüm verir. Böyle bir çözüm (1)–(5)'in hepsinden geçer. King vd.
     (1994) denetimi niteldir; ölçütü yok.
  2. **Fay dışında süreklilik.** Sınama (3) yalnız fay yüzeyinde süreksizliği sınıyor. Fay dışında sürekliliği
     sınamıyor; bu yüzden daha büyük bir fayın çözümü de geçer.
  3. **ΔCFF izdüşümü.** Δτ ve Δσ_n işaretleri hükmün ta kendisidir, ama hiç sınanmıyor.
  4. **Tekillik.** DC3D'nin tekil noktaları ve 7,5 km'de kayan bir alt faya çok yakın hücreler ele alınmamış. Kırık izi
     yalnız kayması en büyüğün ≥ %10'u olan alt faylardan kuruluyor. Bu yüzden r_k ≥ 20 km olan bir hücre, kayması
     daha küçük ama sıfır olmayan bir alt fayın hemen yanında olabilir.
- **Düzeltme metni (§3.3 "Doğrulama" listesine 6–9 maddeleri ve ızgara kuralı):**

  > 6. **Süreklilik.** Fay düzleminin uzantısında, dikdörtgenin dışında (kenardan en az 0,05 W uzakta), ±1e−6 W iki yan
  >    arasındaki yer değiştirme farkı birim kaymanın 1e−6'sından küçüktür.
  > 7. **Üst üste binme.** Bir dikdörtgen dört eş parçaya bölünür. Parçaların toplam çözümü tek dikdörtgen çözümüyle
  >    yer değiştirme ve gerilmede 1e−10 göreli içinde uyuşur.
  > 8. **Yönelim ve simetri.** Düşey, sağ yanal, 0–15 km derinlikte, boyu 30 km bir fay alınır; doğrultusu 0°, 90° ve
  >    225° olan üç hâli koşulur. Alıcı kaynakla aynıdır, μ' = 0, derinlik 7,5 km.
  >    - Fay ucunun doğrultu uzantısında, uçtan 15 km ötede Δτ > 0'dır.
  >    - Fay ortasından faya dik 15 km ötede Δτ < 0'dır.
  >    - Fay merkezli yerel eksenlerde (x doğrultu, y dik) |Δτ(x, y) − Δτ(−x, y)| ve |Δτ(x, y) − Δτ(x, −y)| değerleri
  >      max|Δτ|'nin 1e−8'inden küçüktür. |Δσ_n(x, y) + Δσ_n(−x, y)| için de aynı sınır geçerlidir.
  >    - Üç doğrultunun çözümleri koordinat döndürmesiyle 1e−8 göreli içinde uyuşur.
  > 9. **ΔCFF izdüşümü.** Doğu-kuzey-yukarı eksenlerinde, çekme pozitif. Alıcı normali tavan bloğuna doğrudur; kayma
  >    vektörü Aki & Richards kuralıyla cos λ · ŝ − sin λ · d̂'dir (ŝ doğrultu, d̂ eğim aşağı birim vektörü).
  >    - (a) Yalnız σ_EN = s; alıcı doğrultu 0°, eğim 90°, rake 180° → Δτ = −s, Δσ_n = 0.
  >    - (b) Yalnız σ_EE = s; aynı alıcı → Δτ = 0, Δσ_n = +s.
  >    - (c) Yalnız σ_EU = s; alıcı doğrultu 0°, eğim 30°, rake 90° → Δτ = −s · cos 60° = −0,5 s,
  >      Δσ_n = s · sin 60° = 0,866 s.
  >
  >    Üçü de 1e−12 göreli içinde tutar.
  >
  > Tekil noktalar: sınamalar, DC3D'nin tekil kümelerinde (kenar uzantıları, fay düzlemi) en az 50 nokta içerir. Kod
  > orada sonlu bir değer ya da açık bir "tekil" işareti döndürür. Izgaraya NaN ya da sonsuz değer girmez.
  >
  > **Izgara kuralı (§3.4'e de yazılır).** Hücre merkezinin, kayması sıfırdan büyük herhangi bir alt fay
  > dikdörtgenine 3B uzaklığı 5 km'den küçükse hücre "tekil yakın alan" sayılır. Böyle bir hücre hiçbir loba ve nötr
  > bölgeye girmez. Sayısı aday başına manifestte yazılır.

- §3.3'teki "Ek olarak King vd. (1994) dört lob işaret deseni denetlenir" cümlesi kalır. Artık nicel karşılığı 8.
  maddedir.

### B5. Oy Mc'si kapı Mc'sinin çok üstüne çıkabilir; H0 bu durumda tamlıkla da açıklanır

- **Bulgu.** A2 alt pencere kuralı α'yı korur, ama bedeli büyük olaylarda ağırdır. Taslağın kendi 96 hücrelik
  gürültüsüz ızgarasında (`tr6a_inc1_denetim.json` `tamlik`) Mc_kul − Mc_lob 2,6'ya kadar çıkıyor (M 9, Mc_lob 1,0).
  Etkin N0 10^−ΔMc ile düşer. ΔMc 1,0'da kalıcı −10 kPa'da P_D 0,644'tür (`mc_farki`); n ≤ 4'te oy tanım gereği 0'dır.
  Böyle kümeler H1'in gücünü değil, olumsuz hükmün anlamını değiştirir. Bu durumda H0, "gerilme ölçer ya da Coulomb
  başarısız" demek değildir: oy sayılabilir olay kalmamıştır. Bu bir üçüncü açıklamadır ve kalıplarda yok.
- **Düzeltme metni (§6.2'ye yeni madde 6):**

  > 6. **Etkin N0.** Her küme için N0_kul = n_on(Mc_kul) / (1796/365,25) yazılır (ön pencere, kümesizleştirilmiş,
  >    Mc_kul ile). Hükmün K kümesinin yarısından fazlasında N0_kul < 31,36 ise H0 ve ayırt edilemez kalıplarına şu cümle
  >    eklenir: "Oy Mc'si kapı Mc'sinin belirgin üstünde: K kümenin …'inde etkin N0_kul < 31,36. Olumsuz sonuç (iii) ana
  >    şok sonrası tamlık sınırıyla da açıklanabilir; (i), (ii) ve (iii) ayrılamaz." H1'e uygulanmaz.

- §8 küme başına satırına "N0_kul" eklenir.
- §10 "En olası sonuç" maddesine eklenir: "Büyük olaylarda Mc_kul − Mc_lob ≥ 1 olası; yapay ızgarada 2,6'ya kadar."

### B6. Koşu sonrası değişikliğin sonucu hangi satırdır?

- **Bulgu.** §9 adım 6 oy görüldükten sonraki kod değişikliğinin yazılacağını söylüyor. Ama bağlayıcı hükmün
  değişiklikten önceki mi sonraki mi koşudan geleceğini söylemiyor. Bu, veri sonrası bir karar bırakır. TR-10b ön kaydı
  aynı yerde "sonucu ayrı satırdır" der.
- **Düzeltme metni (§9 adım 6'nın son cümlesinin yerine):**

  > Herhangi bir oy ya da X görüldükten sonraki her kod değişikliği "koşu sonrası değişiklik" başlığında yazılır ve
  > sonucu ayrı satırdır. Hüküm adı, değişiklikten önce tamamlanmış koşudan gelir. Değişiklikten sonraki koşu farklı
  > bir taban hüküm verirse hüküm adına "(koşu sonrası değişiklikle: <ad>)" eklenir. İstisnayla duran bir koşunun
  > doğrudan nedeni düzeltilip tamamlanan ilk koşu, bu kuralda "değişiklikten önceki koşu" sayılır.

---

## C. Küçük bulgular

### K1. c(K) ≤ h(K) çakışması (K ≥ 49)

p₀ = 0,50'de K = 49, 51–60 ve daha büyük K'lerde c ≤ h oluyor (ör. K = 49: c = h = 31). Bu bölge p₀ = 0,51–0,52'de de
başlıyor. Bu K'lerde aynı X hem H1 hem H0 olur. Ana K için olasılık yok denecek kadar küçük, ama JSON K = 60'a kadar
tablo veriyor. **Düzeltme metni (§6.1 eşik listesinin sonuna):** "c(K) ≤ h(K) olan K'lerde (p₀ 0,50'de K ≥ 49) X ≥ c
ise hüküm H1'dir; H0 yalnız X ≤ h ve X < c ise verilir."

### K2. Testere tablosu K_kapı > 45 için

Metindeki tablo K_kapı = 23–45'i veriyor. **Düzeltme metni (§5 testere maddesinin üçüncü alt maddesinin sonuna):**
"K_kapı = 46–80 için çözüm `tr6a_onkayit_sayilar.json` `p0_izgarasi.<p₀>.testere` anahtarından okunur ve bağlayıcıdır.
K_kapı > 80 için aynı kural aynı fonksiyonla uygulanır."

### K3. §3.7 kesmesinde bağlayıcı r_k'nin tanımı

r_k hücre merkezi için tanımlı. Kesmede "olayın dış merkezinin r_k'si" deniyor; hücreye atanıp atanmadığı ve 20 km iç
sınırın uygulanıp uygulanmadığı belirsiz. **Düzeltme metni (§3.7 kesme maddesinde parantezin yerine):** "(havuz
olayının dış merkezinin, temsilci grubunun kırık izi nokta kümesine (§3.4) yatay uzaklığı ≤ 2L; L grubun en büyük
üyesinden; olay hücreye atanmaz ve 20 km iç sınır uygulanmaz)".

Ayrıca "Bağlayıcı karar manifestte r_k ile verilir" cümlesinden sonra: "Önsayımda dış merkez ≤ 3L ile K_kaba
değişmedi (29); r_k ≤ 2L, dış merkezi bu sınırın içinde kalan bütün olayları kapsar." Bu inceleme ayrıca şunu denetledi:
81 koşu adayının hiçbirinde [t0, t_s + 30 g) aralığında, 3L içinde grup dışı bir havuz olayı yok. İlk 30 güne düşen
böyle bir olay için kural gerekmiyor.

### K4. "0 büyüklük" işaretli satır: "seçime girmez" ile "yeniden kestirilir" çelişiyor

§3.5'te bu satırlar için hem "seçime girmez" hem "manifestte satır o katalog için yeniden kestirilir" deniyor. Sorgu
maddesi de "geçersiz satırda manifestteki yeniden kestirim" diyor. Yeniden kestirilen satırın seçime girip girmediği
belirsiz. İki olay da ISC ile kapıdan geçtiği için en yalın yol satırı dışarıda bırakmaktır.

**Düzeltme metni:**
- "**'0 büyüklük' işaretli** (yukarıda) Ek 1 satırları seçime girmez; manifestte satır o katalog için yukarıdaki
  kurallarla yeniden kestirilir." cümlesinin yerine: "**'0 büyüklük' işaretli** Ek 1 satırları (2012 Hint Okyanusu ve
  2003 Tokachi-oki, ComCat) bu olaylar için seçime ve hiçbir satıra girmez; yeniden kestirilmez."
- Sorgu maddesinde "(Mc_halka = o kataloğun Ek 1 Mc'si; geçersiz satırda manifestteki yeniden kestirim)" yerine: "(Mc_halka =
  o kataloğun Ek 1 Mc'si)".

### K5. Mekanizma dökümü temsilciye göre değil, kümenin en büyük olayına göre sayılmış

`onsayim_ozet` mekanizmayı kümenin en büyük M'li birimine göre sayıyor: 15 megathrust, 3 normal. S3 ve S4 ise
"temsilci grubunun en büyük üyesi"ne göre tanımlı. Temsilciye göre döküm 14 megathrust, 10 doğrultu atımlı, 4 normal,
1 ters (diğer)'dir. Fark küme 23'ten geliyor: temsilci us1000i2gt normal, üye us6000dg77 megathrust. **Düzeltme metni
(§10 ve §11 madde 4):** "Önsayımın 29 kümesinin 14'ünün temsilcisi megathrust'tır (doğrultu atımlı 10, normal 4, ters
diğer 1; S3/S4 tanımıyla)." §11 madde 4'teki "15'i" de "14'ü" olur.

### K6. Kapı ve oy için kümesizleştirme Mc'si

§3.6 "Yalnız o lobun içindeki olaylar (Mc_kul üstü)" diyor. Ama kapı Mc_lob ile ve olay sonrası veriden önce sayılır;
Mc_kul o anda bilinmez. **Düzeltme metni (§3.6 ilk maddenin sonuna):** "Kapı (§4.2) ve sahte oylar için ön katalog
Mc_lob (sahtede sahte Mc_lob) üstü olaylarla kümesizleştirilir. Oy için ön ve son katalog Mc_kul üstü olaylarla ayrıca
kümesizleştirilir. İki kümesizleştirme aynı kuralladır."

### K7. Küçük paydalar

- **Düzeltme metni (§7 S2 satırının sonuna):** "K_nk < 10 ise S2 'koşulamadı'; §6.2 kural 2 uygulanmaz ve H1
  'negatif kontrol koşulamadı' niteleyicisini alır (§6.4)."
- **Düzeltme metni (§6.2 kural 3'te "X_S4/K_S4 ≤ 0,5 ise" yerine):** "K_S4 < 5 ya da X_S4/K_S4 ≤ 0,5 ise".
- **Düzeltme metni (§6.2 kural 4'ün sonuna):** "K = 0 olan satırlar 'koşulamadı' diye adıyla listelenir."

### K8. Önbellek okuma yolu: kod düzeyinde zorlanmıyor; yol geçici; maske yarıçapı varsayıma dayanıyor

`tr6a_onbellek_kor.py`'yi okudum ve maskeli yolla bir kez koştum. Doğru çalışıyor:
- maske, döndürmeden önce uygulanıyor;
- sahibi bulunamayan sorgu okunmuyor;
- sahip olayın kendi penceresinin atlanması bilgi sızdırmıyor, çünkü sorgu t_sahip − 29 g'de bitiyor;
- maskelenen satırlar hakkında hiçbir sayı dönmüyor.

Ama bu modül "tek okuma yolu" değil. `tr6_a_kapi.getir` aynı dosyaları maskesiz açabilir (satır 140); `_fdsn` ve `_koeri`
doğrudan çağrılabilir. Kural yalnız metinle korunuyor. Ayrıca `ONBELLEK` bu oturumun geçici karalama dizinine sabit
yazılmış. 4 L_A yarıçapı ise "kırık izi dış merkezden ≤ 2 L_A" varsayımına dayanıyor.

**Düzeltme metni (§9 adım 3, "Bu kuralların dışındaki her önbellek okuması…" maddesinin sonuna):**

> Önbellek yalnız arşivden (sha256 f350d2e0…0d60) açılan bir dizinden okunur; yol `oku_sorgu(…, onb=…)` ile verilir.
> Kod incelemesi (§9 adım 4), önbelleği ya da ön ham dizinleri açan her `open(` çağrısını listeler. `oku_sorgu` ve
> manifestin aday başına kendi indirmesini okuyan işlevi dışında bir çağrı varsa bu hata sayılır. Manifest, kırık izleri
> çıkınca her havuz olayı için R_A = 2 L_A + (izin dış merkeze en uzak noktası) değerini yazar. R_A > 4 L_A olan bir
> olay varsa maske o olay için R_A'ya genişletilir ve sonraki ad hoc okumalar genişletilmiş maskeyle yapılır.

### K9. Sonlu fay ürünü: birden çok ürün, grup üyesinin eksikliği, ürün tarihi

**Düzeltme metni (§3.3 "Sonlu fay modeli" maddesinin ilk cümlesinden sonra):**

> Bir üyenin birden çok `finite-fault` ürünü varsa ComCat'in indirme anındaki tercihli ürünü (olay ayrıntı yanıtında
> ilk listelenen) alınır. Ötekilerin kimlikleri ve `updateTime`'ları manifestte yazılır. Ürünün `updateTime`'ı
> 2025-12-31'den sonra olabilir; tarih sınırı katalog olaylarına uygulanır, kaynak modele uygulanmaz. Bir grup üyesi
> "veri yok" olursa bütün birim "veri yok" olur, çünkü grup ΔCFF'si eksik kalır.

### K10. Olay sonrası indirmenin kapsamı

§9 adım 5 olay sonrası indirmeyi "seçilen kataloğundan" yapıyor. Ama D6, ISC'nin seçilemediği olaylar için ISC ister.
**Düzeltme metni (§9 adım 5'in ilk cümlesinin sonuna):** "D6 satırının olayları için ayrıca ISC'den; S6 için SRCMOD
modelleri (katalog değil) aynı adımda bir kez."

### K11. Kapı eşiklerinin tamsayı karşılıkları

`gereken_n0` değerleri 17,0796 / 31,3626 / 111,2142'dir. 1796 günde n_on eşikleri 84 / 155 / 547'dir. **Düzeltme metni
(§4.2 "Duyarlılık eşikleri" cümlesinin sonuna):** "(n_on ≥ 84 ve n_on ≥ 547)".

### K12. §5 kapı 4'ün adı

"4. Kod denetimi (yapay veri, koşudan önce; §9)" maddesi manifest kapılarından sonra yazılmış. Oysa §9 adım 2'deki yapay
sınama manifestten önce yapılır. **Düzeltme metni:** "4. **Kod incelemesi** (§9 adım 4; yapay sınamalar §9 adım 2'de
manifestten önce tamamlanmıştır)."

### K13. GeoNet yedek kuralı

"Değişmeyen sayı kabul edilir" ifadesi tek anlamlı değil. **Düzeltme metni (§5 madde 1'deki GeoNet cümlesinin
yerine):** "Limit parametresini kabul etmeyen servislerde (GeoNet) her yıllık parça ikiye bölünür. İki yarının satır
sayıları toplamı bütünün satır sayısına eşitse bütün kabul edilir. Değilse her yarıya aynı işlem uygulanır. 1 günlük
parçada da eşitlik sağlanmazsa olay 'veri yok' olur."

### K14. Ek B: betik koşmak dondurulan listenin üzerine yazar

`tr6a_onkayit_sayilar.py` her koşuda `tr6a_olay_listesi.json`'ı yeniden yazıyor. Girdiler aynıyken çıktı bayt bayt aynı;
bunu denetledim. Ama dondurmadan sonra bir girdi değişirse liste sessizce değişir. Ayrıca betik ile `tr6a_sifir_buyukluk.py`
birbirinin çıktısını okuyor: maske listenin `olaylar` alanını, liste `sifir` işaretlerini kullanıyor. Bu döngü kararlı,
çünkü maske yalnız işaretten bağımsız alanları okuyor. **Düzeltme metni (Ek B'nin sonuna):**

> Dondurmadan sonra bu betikler depo kopyasında değil, geçici bir kopyada koşulur. Yeniden üretim, çıktıların sha256'sı
> §3.1'deki ve §9 adım 1'deki değerlerle karşılaştırılarak denetlenir. `tr6a_sifir_buyukluk.py` listenin yalnız
> `olaylar` alanının kimlik, zaman, konum ve L değerlerini okur; bunlar "0 büyüklük" işaretinden bağımsızdır.

Betiğin docstring'indeki "≈ 1 dk" süresi "≈ 4 sn" olur.

### K15. §3.6 S2 ve sahte pencerelerde Mc_son başlangıcı

Bu ifade zaten doğru: "aynı alt pencere düzeni o pencerenin kendi başlangıcına göre". Yalnız "gün sayısı t_s'den" ifadesinin
sahte zamandaki karşılığı yazılmalı. **Düzeltme metni (§3.5 madde 2'nin son cümlesinin sonuna):** "(sahte j'de gün
sayısı t'_j + (t_s − t0)'dan, S2'de t0 − 395 g + (t_s − t0)'dan sayılır)".

---

## D. İNCELEME-1 bulgularının işlenişi

| Bulgu | İşlendi mi | Not |
|---|---|---|
| A1 aşırı saçılım | Evet, genişletilerek | §4.3 iki tablo; §4.6 sahte kalibrasyonu; §11.12. Sayılar 400 000 denemeyle yeniden üretildi ve tutuyor. Açık: J < 30 kuralı (A1), sahte kapı ve öncül komşu (B2). |
| A2 tamlık | Evet | Alt pencere Mc_son t_s'ye göre (B2 ile tutarlı); S7; kural 2a; 96 hücre ve yedek merdiveni ((c) grup için uyarlanmış). Gürültüsüz denetim tutuyor: sürüm 1 kuralı 56/96 hücrede düşüyor, en çok +0,469; yeni kural 0/96. Açık: S7 kapısı (A3), Monte Carlo ölçütü (B3), etkin N0 (B5). |
| A3 bilinen kümeler | Evet | Sıra düzeltmesi doğru (sapma 6); B4 satırı; körlük beyanı. |
| A4 ISC | Evet | "Kesilmemiş t0 + 365 g" açıklaması doğru (sapma 7); D6; §11.2. Örnek N0'lar listeden tutuyor (1912,8; 426,3; 53,3; 623,6 → KOERI 147,8). |
| B1 pozitif kontrol | Evet | Kapı değeri yetersiz (B1). |
| B2 olay grupları | Evet | t_s, π, kırık izi ve konum tanımları tam. |
| B3 önbellek | Evet, genişletilerek | Okuma işlevi ve 4 L_A maskesi var. Kod düzeyinde zorlanmıyor (K8). 42/30 ve 52/33 sayıları tutuyor. |
| B4 kesme | Evet | Bağlayıcı r_k tanımı eksik (K3). Dört çıkan küme ve 61,6 g tutuyor. |
| B5 güç | Evet | Doğru lob payı tablosu, p₀ 0,50/0,52/0,55 güçleri ve p0_kestirim tutuyor. |
| B6 Okada yedeği | Evet | Yetersiz: yönelim, izdüşüm, süreklilik ve tekillik eklenmeli (B4). |
| B7 sonlu fay | Evet | Birden çok ürün ve grup eksikliği (K9). |
| B8 ikincil satırlar ve yeniden koşma | Evet | D8 de eklenmiş. |
| B9 tampon | Evet | Ana, sahte ve negatif kontrolde. |
| B10 satır sınırı | Evet | GeoNet yedeği belirsiz (K13). |
| K1 sıra | Evet | ISC'nin katalog seçimine taşınması doğru. |
| K2 alıcı | Evet | Tam. |
| K3 sıfır büyüklük | Evet, daraltılarak | Maskeli yeniden koşu tutuyor. Seçim cümlesi çelişkili (K4). |
| K4 olay atama | Evet | — |
| K5 D8 | Evet | — |
| K6 tanımsız Δτ_est | Evet | — |
| K7 ters yön sütunu | Evet | Kaldırılmış. |
| K8 mekanizma ve iç sınır | Evet | Mekanizma dökümünün tanımı S3/S4 ile uyuşmuyor (K5). |
| F.3 liste | Değişti (sapma 12) | Kabul; sha256 yeniden üretildi. |

## E. §16'daki 15 sapmaya hükümler

| # | Sapma | Hüküm | Gerekçe |
|---|---|---|---|
| 1 | p₀ yukarı yuvarlama | **Kabul** | Yukarı yuvarlama tutucudur ve §5–§6.1 tablolarını tek anlamlı yapar. Güç bedeli dar bir bantta kalır: ör. K = 23'te p̂₀ ∈ (0,500; 0,504] için c 16 yerine 17 olur. p̂₀'ın çözünürlüğü (1/J ≈ 0,016) ızgara adımından kabadır; yuvarlama bilgi kaybettirmez. Alternatif olan en yakına yuvarlama ise α'yı korumaz. |
| 2 | p₀ > 0,60 ve J < 30 | **p₀ > 0,60: kabul. J < 30: ret** | J < 30'da α korunmuyor ve p̂₀ yok sayılıyor (A1). Önerilen kural taban 0,52 ve p̂₀'ın yalnız yukarı kullanılmasıdır, artı "kalibrasyon zayıf" niteleyicisi. |
| 3 | Payda J ve geçerlilik kuralı | **Kabul, eklerle** | "Olay yok" gerekçesi doğru. Gerçek pencerede karşılığı §3.7 kesmesidir. Önsayımdaki 64/87 ve beş sahte zamansız küme yeniden üretildi. Eklenecekler: sahte kapı, geometri cümlesi, öncül komşu bayrağı, temsil bilgisi (B2). |
| 4 | Ön indirme t0 − 3621 g | **Kabul** | 395 + 670 + 1826 + 730 = 3621. En erken başlangıç 1983-08-13; bütün veri 2025-12-31'den önce. |
| 5 | Sayılar taslağın kendi kodundan | **Kabul** | Bayt bayt yeniden üretildi; scipy ile bağımsız denetim uyuşuyor. φ = 3, N0 = 100'de P(D) 0,4993'tür; İNCELEME-1'in 0,505'i 4000 denemelik gürültüydü. |
| 6 | A3 işlem sırası | **Kabul** | İNCELEME-1'in düzeltme metni kendi içinde çelişiyordu; K1 sırası doğru. |
| 7 | A4 "son pencere" kesilmemiş | **Kabul** | Tutucu ve tek anlamlı. |
| 8 | B3 birim düzeyi ve 4 L_A maskesi | **Kabul** | 42/30 ve 52/33 tutuyor. Zorlama, yol ve yarıçap denetimi eklenmeli (K8). |
| 9 | B4 önsayımı dış merkezle | **Kabul** | Bağlayıcı r_k tanımı eklenmeli (K3). 3L duyarlılığı K'yi değiştirmiyor. |
| 10 | §10 K = 29, P(K < 23) ≈ 0,7 | **Kabul** | 81 → 41 → 35 → 29 zinciri ve bütün duyarlılıklar (29 / 19 / 6 / 11 / 7) yeniden üretildi. Önsel yazarındır; kaba sayıyla tutarlı. |
| 11 | K3 kuralının daraltılması | **Kabul** | Maskeli taramada türü dolu binlerce gerçek mikro deprem satırı var; geniş kural bunları da atardı. Seçim cümlesindeki çelişki düzeltilmeli (K4). |
| 12 | Listenin değişmesi | **Kabul** | Liste hiçbir olay sonrası bilgi taşımıyor (alanlar denetlendi); sha256 tutuyor. |
| 13 | S2 ayrı satır | **Kabul** | Ön pencereleri gerçekten farklı. S2'nin j = 1'i geçerli kümelerle sınırlanması tutarlı. Küçük K_nk kuralı eklenmeli (K7). |
| 14 | McNemar gücü kesin | **Kabul** | 0,677 / 0,757 / 0,819 / 0,860 tutuyor. Ama kapısız nötr bölgede McNemar dişsiz (A3). |
| 15 | GeoNet satır sınırı yedeği | **Kabul, netleştirilerek** | Kural metni K13'teki gibi tek anlamlı yazılmalı. |

## F. Görevde özellikle sorulanlara kısa yanıtlar

- **Yukarı yuvarlama ve "güç yok (ölçü yanlı)".** Kabul. p₀ > 0,60 olasılığı sahte p 0,46'da ≤ 0,01, 0,50'de ≤ 0,046.
- **J < 30.** α korumasını kaldırıyor. Taban 0,52 ve "kalibrasyon zayıf" niteleyicisi gerekir (A1). Kullanıcının
  önerdiği "H1 (kalibrasyonsuz)" etiketi tek başına yetmez: etiket α'yı düzeltmez. İkisi birlikte uygulanmalı.
- **Kalibrasyon kümeleri temsil ediyor mu?** Kısmen (5/29 küme sahte zamansız, iki M 9,1 dahil). Yapay hesapta
  α ≤ 0,041 kalıyor. Bilgi satırları ve sahte kapı yeter (B2).
- **p̂₀ gürültüsü ve bağımsızlık.** Gürültü yalnız gücü düşürüyor (K = 23'te 0,804'ten 0,745–0,659'a). Ortak veri
  ilişkisi α'yı en çok 0,005 artırıyor (B2).
- **§3.7.** Bağlayıcı olan r_k'dir. Tanımı K3'teki metinle tek anlamlı olur. Dış merkez önsayımı ile 3L duyarlılığı
  aynı K'yi veriyor.
- **§9 adım 3 ve `tr6a_onbellek_kor.py`.** Doğru çalışıyor ve sızdırmıyor. Ama tek okuma yolu yalnız metinle
  korunuyor; kod incelemesine `open(` denetimi eklenmeli (K8).
- **S7 McNemar'ın hükme etkisi.** H1 için tanımlı, ama nötr kapısı olmadan dişsiz (A3). H0 ve ayırt edilemez için
  etkisi yok; bu doğru, çünkü tamlık kaybı H1 yönündedir.
- **Yedek merdiveni.** Sıra veri görülmeden sabit. Ama 4000 denemede basamak seçimi Monte Carlo gürültüsüne bağlı;
  tohum, sonuç kuralı ve (c)'nin yayılımı yazılmamış (B3).
- **Pozitif kontrol kapısı.** 3,0 yetersiz, 10,0 olmalı (B1).
- **Testere tablosu.** p₀ ızgarasında tek anlamlı. K_kapı > 45 için JSON'a atıf ve K ≥ 49'daki c ≤ h çakışması
  için öncelik kuralı eklenmeli (K1, K2).
- **Okada sınamaları.** Çözümü denetler; yönelim, işaret, izdüşüm, süreklilik ve tekilliği denetlemez (B4).
- **Sonlu fay ürününün dondurulması.** Yeterli; birden çok ürün ve grup kuralı eklenmeli (K9).
- **Hüküm kalıpları.** Eksik; kapalı liste ve bileşim kuralı A2'de.

## G. Denetimde temiz çıkanlar

- **Tarih ve veri sınırı.** Bütün sorgu pencereleri 2025-12-31'den önce: en geç bitiş 2025-12-05, en erken sahte ön
  indirme 1983-08-13. Tarih kuralıyla çıkan 7 birim, 67 katalogsuz birim, 81 koşu adayı (84 olay), dört çok üyeli grup
  ve t_s kaymaları listeden tutuyor.
- **Önsayım.** K_kaba 29 (Aσ 13'te 35, Aσ 39'da 6); sürüm 1 yeniden üretimi 46/37. Çıkan altı küme ve nedenleri,
  D6'nın üç birimi ve Kahramanmaraş'ın KOERI'ye geçişi tutuyor.
- **Binom ve güç.** §6.1 eşik ve hüküm olasılığı tabloları, p₀ ızgarası, testere dişi tablosu ve ilk/kalıcı K'ler
  scipy ile birebir uyuşuyor (K = 18–80). p₀ = 0,50'de K = 28–200 aralığında güç ≥ 0,80.
- **Oy.** Poisson H0 P(D) ve P(A) değerleri ve Monte Carlo 0,4582 tutuyor. Koşullu oy kuralı her n'de P(D | n) ≤ 0,5
  veriyor. D ve A aynı kümede birlikte 1 olamaz.
- **Saçılım ve kalibrasyon.** Aşırı saçılım tablosu, "kalibrasyonla α ≤ 0,035" savı (en çok 0,0348) ve p0_kestirim
  değerleri tutuyor (0,25 / 0,20; 0,745 / 0,659; 0,825 / 0,750; 0,874 / 0,811; ≤ 0,01 / ≤ 0,046).
- **Yapay Dieterich ve tamlık.** Yapay Dieterich tablosu, Mc farkı tablosu (0,934 / 0,868 / 0,644) ve doğru lob payı
  tablosu tutuyor. Tamlık ön denetimi de tutuyor: %1,3–3,1 kayıp, 56/96, +0,469.
- **"0 büyüklük".** Önbellek özeti ve iki olayın yeniden kestirimi tutuyor: 0,2 → 4,7 ve 0,3 → 4,3, maskeli yolla.
- **Eşik.** Kapı eşiği n_on ≥ 155, gereken_n0'ın kesin değeriyle (31,3626) tutarlı.
- **İstanbul ve Marmara.** Metinde İstanbul ya da Marmara için mutlak olasılık yok. §12–§14 tutarlı.

## H. Dondurma öncesi yapılacaklar (sıralı)

1. A1, A2 ve A3 düzeltme metinleri işlenir: §4.6, §6.2, yeni §6.4, §6.3, §7 S7, §8, §13, §16 madde 2.
2. B1–B6 metinleri işlenir: §7 S1, §10, §4.6, §7 B3, §11.12, §11.17, §9 adım 2, §3.3, §3.4, §6.2 madde 6, §9 adım 6.
3. K1–K15 metinleri işlenir.
4. `tr6a_onkayit_sayilar.py`'ye yalnız `pozitif_kapi` anahtarı eklenir (B1; yapay). Betik geçici bir kopyada koşulur.
   Liste içeriği değişmediği için sha256 0cde4fa1…048f kalmalıdır; değişirse yeni değer §3.1'e yazılır.
5. §16'ya bir madde eklenir: "16. İNCELEME-2 düzeltmeleri işlendi (A1–A3, B1–B6, K1–K15); sapma yok."
6. Metin "DONDURULDU" başlığıyla commit edilir. Üçüncü inceleme turu gerekmez. Kod incelemesi (§9 adım 4) özellikle
   şunları denetler:
   - J < 30 ve sahte kapı dalları;
   - nötr kapısı;
   - §6.4 ad kurucusu;
   - B4'teki 6–9 sınamaları;
   - K8'deki `open(` denetimi.
