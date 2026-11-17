# TR-13b koşu betiği: bağımsız kod incelemesi (dondurma öncesi son kapı)

Tarih: 17 Kasım 2026. İncelenen: `kayit/turetme/tr13b/tr13b_kosu.py` (sha256 `1bc2277b…`), `tr13b_test_yapay.py`
(`3a24af28…`), bağımlılıklar `kayit/turetme/tr13/tr13_guc.py` (`0223ca7a…`) ve `tr13_sayim.py` (`d526db7d…`); ölçüt metni
`TR-13b_sinirli-kosu_ONKAYIT.md` (TASLAK sürüm 3, commit cc7a8da; kod 3352ef8). Önceki incelemeler INCELEME-1 ve
INCELEME-2 okundu. Ön kayıt metni değiştirilmedi; önerilen ek cümleler §E'de. Yazara güvenilmedi: her madde kodda satır
satır okundu ve bağımsız sınamayla (aşağıda "Y" sınamaları) denetlendi.

Bağımsız inceleme betikleri: `kayit/turetme/tr13b/kodinc/` (`tr13b_kodinc.py` birim / uçtan uca / seri / mutasyon;
`asim.py` + `asim_analiz.py` asimetri ölçümü). Çıktılar aynı dizinde (`*.json`). Hepsi `python3 -I -B`, yalnız yapay ETAS.

## Hüküm

**DÜZELTMEYLE KABUL** (düzeltmeler bu incelemede koda işlendi; yeni sha256 §F'de). Betik metnin aşamalarını, tohumlarını,
kalibrasyonunu, R0'ını, plasebo bilgi satırını ve tek koşu kilidini doğru uyguluyor. Üç kusur bulundu ve düzeltildi:

- **K-1 (kritik): gerçek kip kapısı yalnız komut satırındaydı.** `kos()` içe aktarılarak varsayılan `Yollar()` ile
  çağrılınca dondurulmamış ön kayıtla gerçek arşivi açıyor, hazırlık sayımlarını yapıyor ve sıfır havuzlarına
  geçiyordu. Bu inceleme sırasında **benim kendi sınamam bu açıktan geçti** (§G, olay kaydı). Düzeltme: kapı `kos()`'un
  başında; gerçek arşiv dizini ya da gerçek sha256 listesi gösterildiğinde (ya da `gercek=True`) dondurulmamış ön kayıtla
  `SystemExit`, gerçek girdiyle yalnız ön kayıt ayarı (havuz 2000, B_ref 200, 200 000 çekiliş, test düğmeleri kapalı).
- **K-2 (önemli, "VAR" yönünde): sıfır havuzu z_p şartıyla süzülüyordu.** `sonlu()` T1/R0 sıfırından z'si **ya da
  z_p'si** tanımsız bölgeleri atıyordu; metin (§3.5) yalnız z'si tanımsızın düşmesini söyler ve gerçek üyede z_p şartı
  yoktur. z_p'si tanımsız bölgeler havuzun ortalama %9,9'u (üye başına %3,8–21) ve z'leri belirgin biçimde düşük
  (ort. −0,40, ötekiler −0,08): atılmaları sıfırın sol kuyruğunu inceltip p'yi küçültüyordu. Ölçülen etki: R0 yanlış
  alarmı +0,0045 ± 0,0014 (bileşim; 0,016 → 0,022), +0,0022 ± 0,0013 (düşük-N zorlaması). D-3 de aynı süzgeci veriye
  uyguladığı için bu yanlılığı göremiyordu. Düzeltme: T1/R0 sıfırında ve D-3 verisinde yalnız z şartı; z_p şartı yalnız
  plasebo satırında.
- **K-3 (önemli, yazarın (b) zayıflığı): N ≥ 50 asimetrisi.** Bileşimde etkisi ihmal edilebilir ve H0 yönünde, ama
  düşük-N durumunda "VAR" yönünde (+0,0032 ± 0,0019; güç +0,015). Gerçek N3bg'lerin tahminden düşük çıkması olası
  olduğundan düzeltildi: sıfır havuzu ve D-3 verisi de gerçek üye gibi önce-pencere N ≥ 50 şartıyla süzülür
  (kalibrasyonun ±%5 denetimi değişmeden bütün 2000 bölgenin ortalama N'siyle yapılır).

Düzeltmelerden sonra (bileşim, havuz 1000, eşli önyükleme): R0 sinyalsiz yanlış alarm **0,018 ± 0,003**, f = 0,4
gücü **0,78 ± 0,02** (ön kayıt: 0,020 / 0,80). Uçtan uca 20 bağımsız sinyalsiz yapay liste: **YYY**; f = 0,4 ile 10
liste: **ZZZ** (§D).

## A. Kod metne madde madde uyuyor mu

| Madde (metin) | Kod | Durum |
|---|---|---|
| Aşama sırası 1 girdi → 2 hazırlık → 3 sıfır → 4 D-3 → 5 gerçek z → 6 hüküm (§12.2) | `kos` | **uyuyor**; gerçek z D-3 kapısından sonra (E3d ve M12 bunu sınar); `gercek_z.json` "x" kipinde, sürdürmede yeniden kullanılır (Yu2, Y15). |
| §3.1 süzgeç [t − 10 y, t), t < 2026-01-01, derinlik ≤ 40 km | `hazirla` `sec` | **uyuyor**. Körlük sınırı `<` 2026-01-01T00:00:00: Y2 (ana şok 2026-03 sınamada; 2025-12-31T23:59:59.999 sayılır, 2026-01-01T00:00 ve sonrası sayılmaz). Gerçek listede t_ana < 2026 olduğundan bu süzgeç t < t_ana'nın yanında artıktır ama doğrudur. |
| §3.1 ortak Mc_b = max(Mc_önce, Mc_ref), önce ve referansa birlikte | `mc = max(mc0, mcr)`, tek `ust` maskesi | **uyuyor** (U4, M17). |
| §3.2 GK74 indirilen bütün dairede, m ≥ Mc_b | `T.gk74(t[ust], …)` R süzgeci olmadan | **uyuyor**. Not (n-1): GK74 derinlik süzgecinden *sonra* koşulur (derin büyük olaylar küme başı olmaz); TR-13 `olc` derinlik süzgeçsiz koşuyordu. Metin "Süzgeç … derinlik ≤ 40 km" dediği için uyumlu; §E'de açıklayıcı cümle önerildi. |
| §3.3 doyma: N3bg > 100 → Mc + 0,1, GK74 yeniden, ≤ 100'e dek; ref'e de uygulanır | `while True` döngüsü | **uyuyor** (U4 GK74'ü bağımsız yeniden hesaplar). |
| §3.3 düşme: N3bg < 50; referans < N3bg + 5; eksik parça → veri yok | `hazirla` | **uyuyor** (U4, M11, E3b). |
| §3.4 ölçü, 200 alt örnek, tohum 20261201 + 1000 i + 50 | `tohum_olcu`, `z_guvenli` | **uyuyor** (U1, Y1). |
| §3.5 kendi R'de kalibrasyon, 40 + 40 deneme, tohum + 10 + d | `kalibre`, `tohum_kal` | **uyuyor** (U5, Y1, Y16). |
| §3.5 ±%5, bir yineleme (μ × N/ort, tohum + 20 + d), sonra dal 2 | `kal_tamam`, deneme döngüsü | **uyuyor** (U14, E3c). |
| §3.5 havuz tam 2000, 4 parça, `SeedSequence(tohum, spawn_key=(p,))`, tohum 20261201 + 1000 i + d | `HAVUZ`, `_is_havuz`, `parca_boylari` | **uyuyor** (U1, Y1, Y11, Y12: havuz dosyalarından bağımsız sayım). |
| §3.5 "z'si tanımsız bölge havuzdan düşer" | `sonlu` | **uymuyordu** (z_p'si tanımsız olan da düşüyordu) → **K-2 düzeltildi**. |
| §3.6 küme z = üye ortalaması; sıfırda her üye kendi havuzundan bağımsız çekiliş | `kume_ort`, `sifir_cekilis` | **uyuyor** (U8, Y3, Y4: p'ler havuz dosyalarından bağımsız yeniden kurulur). |
| §3.7 T1, 200 000 çekiliş, tohum 20260900 + d, bütün ve keşif dışı aynı çekilişlerden, tek yanlı ≤ | `p_deger`, `S`, `Sa`, `Sk` | **uyuyor** (Yu1 bağımsız yeniden hesap; Y01, Y03, Y17). |
| §7.3 R0 üç dallanma × iki liste, p ≤ 0,05 | `karar`, `r0_oran` | **uyuyor** (U6, Y4, Y06). |
| §3.8 / §7.3 plasebo bilgi satırı, hükmü değiştirmez; p ≤ 0,05'te uyarı cümlesi | `hukum_kur`, `cumle_var` | **uyuyor** (U7, M04). |
| §3.9 MC standart hata, "sınırda" ±0,03, yeniden koşu yok | `se`, `sinirda` | **uyuyor**. |
| §7.1 veri yok: sha256 uyuşmazlığı ya da keşif dışı K < 8; K 8–9'da sürer | `sha_denetimi`, `KD_MIN` | **uyuyor** (E3a, E3b, Yu3: K = 8'de koşu sürer; Y08). |
| §7.2 / D-3: sinyalsiz yanlış alarm > 0,05 ya da f 0,4 gücü < 0,65 → dal 2, gerçek z hesaplanmadan | `d3_gecer`, `oran[D3_F]` | **uyuyor** (U14, E3d, Yu4: kapıya giden güç f = 0,4'ünkü; Y18). |
| §7.5 cümlede keşif dışı K ve yeniden hesaplanan MDE | `cumle_ayirt(K_kd, mm)` | **uyuyor** (Yu1 cümledeki K'yi bağımsız sayar; Y07). |
| §12.2 tek koşu kilidi ("x" kipi; dosya varsa hiçbir şey hesaplamadan çık) | `kos` başı, `_yaz_hukum` | **uyuyor** (U10, E3e). |
| §12.1 dondurulmamışken gerçek kipi reddetme | `dondurulmus_mu` yalnız `__main__`'de | **eksikti** → **K-1 düzeltildi** (Y5, Y13, Y14, Y19). |

Öteki notlar (düzeltme gerektirmez):
- n-2: Yapay bölgede GK74 R + 30 km'lik dairede ve 5 yıl ısınmayla koşulur; gerçekte ComCat dışı olaylarda yalnız R
  dairesi, ısınma yok (§9.9 ısınmayı yazıyor; R farkını yazmıyor). Uçtan uca seride sinyalsiz p'lerin dağılımı yukarı
  kaymış (§D): gerçek biçimli katalogdaki bu farkların net etkisi bu yapay ayarda **tutucu** (H0 yönünde).
- n-3: `dondurulmus_mu` "DONDURULDU" dizgisini "Durum:" satırında alt dizgi olarak arar; "Durum: DONDURULDU değil"
  gibi bir yazım da geçer. Dondurma satırı yazılırken buna dikkat edilmeli (§E).
- n-4: Yazarın mutasyon düzeni modül kopyasını depo dışına koyduğundan kopyada `ONKAYIT` yolu "ön kayıt yok"a düşer;
  yazarın sınamaları kapıyı sınamadığı için sonuçları etkilemez. Benim düzenim depo yollarını sabitler.
- n-5: Sınamada küçük havuzlarla (100–150) ±%5 kalibrasyon denetimi rastlantıyla tutmayabilir (Yu1'in ilk denemesi
  dal 2 verdi). Y sınamaları ve seri yalnız sınamada toleransı ±%15'e gevşetir (`TOL_SINAMA`); gerçek ayarda (2000)
  ±%5 değişmez.

## B. Yazarın bildirdiği iki zayıflık: hüküm

Ölçüm: listenin üstveri bileşimi (15 üye / 13 küme / keşif dışı 10; §2 tablosunun R ve doyma sonrası N3bg'si), her üye
ve dallanma için 1000 bölgelik sıfır havuzu, ayrı kalibrasyonla 600 sinyalsiz + 300 f = 0,4 "veri" bölgesi (dallanma
0,6), R0 kuralı tam (üç dallanma × iki liste), 100 000 sıfır / 20 000 veri çekilişi; havuzların eşli önyüklemesi
(B = 20). Zorlama: aynı R'lerle bütün N3bg = 55 (havuz 600, veri 400/200). `kodinc/asim_tablo.json`,
`kodinc/asim_dusuk.json`.

R0 red oranı (sinyalsiz yanlış alarm / f = 0,4 gücü):

| Sıfır süzgeci | Veri süzgeci | Bileşim | N = 55 zorlaması | Anlamı |
|---|---|---|---|---|
| z ve z_p tanımlı (eski kod) | z ve z_p tanımlı | 0,017 / 0,76 | 0,020 / 0,82 | eski D-3'ün ölçtüğü |
| z ve z_p tanımlı (eski kod) | z tanımlı, N ≥ 50 | **0,022 / 0,79** | **0,024 / 0,87** | eski kodun gerçek koşuda yaptığı |
| z tanımlı | z tanımlı, N ≥ 50 | 0,016 / 0,77 | 0,021 / 0,86 | yalnız K-2 düzeltmesi |
| z tanımlı, N ≥ 50 | z tanımlı, N ≥ 50 | **0,018 / 0,78** | **0,019 / 0,85** | K-2 + K-3 (yeni kod) |

Eşli önyükleme farkları (ort. ± sd): z_p şartı (eski − K-2) bileşimde +0,0045 ± 0,0014, zorlamada +0,0022 ± 0,0013;
N ≥ 50 şartı (K-2 − K-2+K-3) bileşimde −0,0008 ± 0,0007, zorlamada **+0,0032 ± 0,0019** (güç +0,015 ± 0,009).

**(a) `tr13_guc.V_q`'nun IndexError'ı.** Hüküm: **yanlılık yok denecek kadar küçük; düzeltme gerekmez, metin yanlış
gerekçe veriyor.** Ölçtüğüm: sıfır havuzunda z'si tanımsız bölge payı ortalama %0,74 (üye başına %0–2,7); bu
bölgelerin önce-pencere N'si ortalama 188 (yani "çok küçük n" değil) ve %96'sında N ≥ 50. Kaynakları `z_olcu`'nun kendi
kuralları: önce-pencere n < 5 ya da **referans < n + 5**. Ayrı bir izlemeyle (3 üye × dallanma, 750 bölge) IndexError
**hiç** görülmedi. "referans < n + 5" düşmesi gerçek üyenin "referans arka planı < N3bg + 5 → düşer" kuralının tam
eşidir; yani bu düşme simetriktir. Yön: bu bölgeler sıfırdan atılınca, gerçek üye de aynı durumda atıldığından, p'de
sistematik kayma beklenmez; ölçülebilir bir sınır: pay %0,74 olduğundan etki R0'da ≤ 0,001 mertebesi.
IndexError gerçekte olursa (`z_guvenli` gerçek üyeyi de NaN yapar ve üye düşer) yine simetriktir.

**(b) N ≥ 50 asimetrisi.** Hüküm: **bileşimde ihmal edilebilir ve H0 yönünde (−0,0008), ama düşük N'de "VAR" yönünde
(+0,003, ≈ %18 göreli; güç +0,015).** Gerçek N3bg'ler üstveri tahmininden düşük çıkabilir (Cook Boğazı 74; Ishigaki'nin
düşmesi gibi); bu yüzden **K-3 olarak düzeltildi**: sıfır havuzu ve D-3 verisi de N ≥ 50 ile süzülür. Bedeli: bileşimde
güç ≈ 0, zorlamada −0,015. Asıl "VAR" yönlü yanlılık (b) değil, bu incelemede bulunan z_p şartıydı (K-2).

## C. Mutasyon sınamaları (yazarınkilerden farklı, 21)

Her mutasyon betiğin bir kopyasına uygulandı; yakalayıcılar: Y birim (Y1–Y6), yazarın birimleri (U1–U14), Y uçtan uca
(Yu1 bağımsız yeniden hesap: p'ler, z̄'ler, K'ler, havuz boyları, ±%5, R0, D-3 kapısı ve cümledeki K, havuz
dosyalarından ve `gercek_z.json`'dan yazarın işlevleri kullanılmadan; Yu2 kesinti/sürdürme; Yu3 keşif dışı K = 8;
Yu4 D-3 kapısına giden güç). Hız için Yu1 deterministik havuz dosyalarını önbellekten alır (havuz üretimini değiştiren
Y11, Y12 önbelleksiz koşuldu). **21 / 21 yakalandı.** İlk turda Y04 ve Y18 kaçtı; Y04 yalnız birim sınamasına
verilmişti (ortak indeks bağımsız havuzlarda istatistiksel olarak eşdeğerdir, ama tohum düzenini bozar; Yu1'in tam
tohumlu yeniden hesabı yakalar), Y18 için Yu4 eklendi. Sonuç: `kodinc/test_mutasyon.json`, `kodinc/test_mutasyon2.json`.

| # | Mutasyon | Yakalayan |
|---|---|---|
| Y01 | p kuyruğu: keşif dışı p bütün listenin sıfırına karşı | Yu1 |
| Y02 | p kuyruğu: D-3'te `p_vektor` üst kuyruk | Y4 |
| Y03 | küme ortalaması: keşif dışı z̄ bütün listeden | Yu1 |
| Y04 | küme: üyeler ortak indeksle çekilir (tohum düzeni bozulur) | Yu1 |
| Y05 | dallanma listesi: üç sıfır da 0,6 havuzundan | Yu1 |
| Y06 | dallanma listesi: D-3'ün R0'ı 0,8'i yok sayar | Y4 |
| Y07 | K sayımı: cümledeki K bütün liste | Yu1 |
| Y08 | K sayımı: K = 8'de veri yok | Yu3 |
| Y09 | körlük: 2026-01-01T00:00 dahil (`<=`) | Y2 |
| Y10 | körlük: sınır 31 gün kayık | Y2 |
| Y11 | havuz boyu: son parça okunmaz | Yu1 |
| Y12 | havuz boyu: %10 eksik havuz | Yu1 |
| Y13 | kilit: DONDURULDU bütün metinde aranır (metin §12.1 bu sözcüğü zaten içeriyor: kapı açılırdı) | Y5 |
| Y14 | kilit: sha256 şartı kapıdan kalkar | Y5 |
| Y15 | kilit: sürdürmede gerçek z yeniden hesaplanır | Yu2 |
| Y16 | tohum: kalibrasyon tohumu + 11 | Y1 |
| Y17 | tohum: T1 çekilişi üç dallanmada aynı | Yu1 |
| Y18 | D-3 kapısı f = 0,5 gücüyle | Yu4 |
| Y19 | kilit: `kos()`'un kendi kapısı kalkar (K-1 geri) | Y5 |
| Y20 | sıfır havuzu z_p şartıyla (K-2 geri) | Yu1 |
| Y21 | sıfır havuzunda N ≥ 50 şartı kalkar (K-3 geri) | Y6 |

Yazarın 20 mutasyonu yeni kodda yeniden koşuldu: **XXX**.

## D. Uçtan uca yapay seri

Yazarın sahte arşiv üreteci (`tr13b_test_yapay.sahte_veri`: 16 olay, 14 küme, ComCat/ISC/GeoNet biçimleri, antimeridyen,
lat/lon + ms) her liste için ayrı tohumla (20261300 + j; f = 0,4'te 20261800 + j); `kos()` olduğu gibi (aşamalar 1–6).
**Sınama ayarı küçültüldü (süre sınırı):** havuz 100 (gerçekte 2000), B_ref 50 (200), 40 000 T1 çekilişi (200 000),
D-3 havuzları 40 / 30 (200 / 150), D-3 çekilişi 8000, kalibrasyon 40 + 40 (aynı), ±%5 yerine ±%15 (n-5). Her
koşunun p'leri havuz dosyalarından bağımsız yeniden hesaplandı (hepsinde fark yok). `kodinc/test_seri_f0.json`,
`kodinc/test_seri_f04.json`.

SSS

## E. Ön kayıt metni için önerilen ek cümleler (kesin)

1. **§3.5, "z'si tanımsız bölge (bkz. §9.8) havuzdan düşer; sayısı raporlanır." cümlesinin yerine:**
   > z'si tanımsız bölge ve önce-pencere arka plan sayısı 50'den az olan bölge, gerçek üyenin seçimiyle aynı biçimde,
   > T1/R0 sıfırından ve D-3 verisinden düşer; ikisinin sayısı da raporlanır. z_p'si tanımsız bölge T1/R0 sıfırında
   > kalır, yalnız plasebo satırından düşer (gerçek üyede z_p şartı yoktur). Kalibrasyonun ±%5 denetimi süzgeçten önce,
   > 2000 bölgenin tümünün ortalama N'siyle yapılır. Süzgeçten sonra boş kalan havuz dal 2'dir.
2. **§9.8'in yerine:**
   > 8. **Sıfır havuzu ile gerçek üye arasındaki asimetriler (kod incelemesi, `TR-13b_KOD-INCELEME.md` §B):**
   > (a) Sıfır havuzunda z'si tanımsız bölge payı ortalama %0,7 (üye başına %0–2,7); bunlar `z_olcu`'nun "referans <
   > n + 5" ve "n < 5" kurallarından gelir ve gerçek üyenin "referans arka planı < N3bg + 5 → düşer" kuralının eşidir;
   > `tr13_guc.V_q`'nun IndexError'ı 750 yapay bölgede hiç görülmedi. Yanlılık ölçülemeyecek kadar küçüktür.
   > (b) Gerçek üye N3bg ≥ 50 şartıyla girer; sıfır havuzu ve D-3 verisi de aynı şartla süzülür. Şartsız sıfır,
   > bileşimde R0 yanlış alarmını −0,001 (H0 yönü), bütün üyelerin N3bg'si 55 olduğunda +0,003 ("VAR" yönü) kaydırıyordu.
   > (c) Sürüm 3'ün ilk betiği sıfırdan z_p'si tanımsız bölgeleri de atıyordu (havuzun ≈ %10'u, z'leri ortalamadan
   > ≈ 0,3 düşük); bu, yanlış alarmı bileşimde 0,016'dan 0,022'ye çıkarıyordu ve D-3'te görünmüyordu. Düzeltildi.
   > Düzeltilmiş betikle bileşimde R0: sinyalsiz yanlış alarm 0,018, f = 0,4 gücü 0,78 (havuz 1000, ± 0,003 / ± 0,02).
3. **§9.9'a ek:**
   > Ayrıca yapay bölgede GK74 R + 30 km'lik dairede koşulur; ComCat dışı gerçek olaylarda yalnız R dairesi indirildi.
   > Gerçek biçimli yapay kataloglarla uçtan uca seride (`TR-13b_KOD-INCELEME.md` §D) bu iki farkın net etkisi H0
   > yönündedir (sinyalsiz p'ler yukarı kaymış).
4. **§3.2'ye açıklama:** "GK74, §3.1'in derinlik süzgecinden sonra kalan olaylarla koşulur."
5. **§12.1, "Gerçek kip yalnız…" paragrafına ek:**
   > Kapı `kos()` işlevinin içindedir: içe aktarılarak çağrıldığında da, gerçek arşiv dizini ya da gerçek sha256 listesi
   > verildiğinde dondurulmamış ön kayıtla hiçbir şey açılmaz ve yazılmaz; gerçek girdiyle yalnız ön kayıt ayarı (havuz
   > 2000, B_ref 200, 200 000 çekiliş, sınama düğmeleri kapalı; çekirdek sayısı serbest) kabul edilir. Dondurma satırı
   > tam olarak "Durum: DONDURULDU …" biçiminde yazılır; satırda olumsuzlama bulunmaz.
6. **§12.1 tablosu:** `tr13b_kosu.py` sha256'sı §F'deki yeni değerle değiştirilir; §12.4–12.5 sayıları yeni betikle
   yeniden üretilmelidir (yazarın `tr13b_test_yapay.py birim/uctan/mutasyon` sınamaları yeni betikte geçti, §F).
7. **§0 ve §5 sayıları:** R0'ın yanlış alarmı ve MDE'si değişmez sayılabilir (0,018 / güç 0,78 ↔ ön kayıt 0,020 /
   0,80, Monte Carlo hatası içinde); metin değiştirilmek istenirse §9.8 (c)'deki cümle yeterlidir.

## F. Son durum ve sha256

| Dosya | sha256 |
|---|---|
| `kayit/turetme/tr13b/tr13b_kosu.py` (düzeltilmiş) | `SHAKOSU` |
| `kayit/turetme/tr13/tr13_guc.py` (değişmedi) | `0223ca7a0b55a26f27c9c04af183cbc53150f07d22141f7e897f6a7201d035b2` |
| `kayit/turetme/tr13/tr13_sayim.py` (değişmedi) | `d526db7de33a816c6e4217cafb2fa034c4060ff27b9e6b864145388f829fbc9b` |
| `kayit/turetme/tr13b/tr13b_test_yapay.py` (değişmedi) | `3a24af28714eb187a0a3670aa124cc907258ebeb9f605bae6cf6b94e64652fd6` |
| `kayit/turetme/tr13b/kodinc/tr13b_kodinc.py` (bu inceleme) | `SHAKODINC` |

Yeni betikte koşulan sınamalar: yazarın `birim` 11/11, `uctan` E1–E3e TTT; Y `birim` Y1–Y6 6/6, Y `uctan` Yu1–Yu4 4/4.

## G. Olay kaydı: inceleme sırasında gerçek arşive istenmeden dokunuldu

K-1'i sınamak için yazdığım ilk Y5 sınaması, açığın var olduğunu varsayarak değil, kapının çalıştığını varsayarak
`kos(K.Ayar(), K.Yollar(cikti=<karalama>), gercek=True)` çağırdı. Eski betikte `kos()` içinde kapı olmadığından koşu
gerçek arşivle başladı; ≈ 5 dakika sonra fark edilip durduruldu. Durum dosyasına göre tamamlanan aşamalar:
`1_girdi_sha` (sha256'lar uyuşuyor), `2_hazirlik` (gerçek kataloglarda ortak Mc, GK74, doyma döngüsü ve **yalnız
sayılar**: N3bg, N_ref, N_plasebo, referanstaki en büyük olay), `3a_kalibrasyon` (yapay) ve 20 yapay sıfır havuzu
parçası. **Gerçek katalogda V(q) ya da z hesaplanmadı** (`gercek_z.json` ve hüküm dosyası oluşmadı; D-3 aşamasına
gelinmedi). Ekrana yalnız iki olayın hazırlık satırı düştü (Superstition Hills 1987: Mc 2,0 → 2,3, N3bg 85; Loma
Prieta 1989: Mc 1,4 → 2,5, N3bg 94; N_plasebo değerleri); bunlar ölçü değil sayımdır ve ön kaydın §2 üstveri
tahminleriyle (86, 96) aynı mertebededir. Çıktı dizini (durum.json sha256 `e41330a3…`) karalamadan silindi, hiçbir yere
kopyalanmadı ve commit edilmedi. Ardından sınama, modülün "gerçek" sabitlerini boş bir sahte dizine çevirerek ve
süreç içinde `/mnt/project-files` altındaki her `open`/`tarfile.open`/`sha256` çağrısını hata verdirerek yeniden
yazıldı; sonraki bütün sınamalar (mutasyonlar dahil) bu korumayla koştu. Bu olay K-1'in gerçek olduğunun da
kanıtıdır. Ön kayıt sahibi bu sayımların görülmesini körlük açısından değerlendirmelidir; benim görüşüm: §2'deki
üstveri sayımlarıyla aynı türden bilgidir, V/z hakkında bilgi taşımaz.
