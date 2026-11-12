DÜZELTMEYLE KABUL

# TR-6a koşu kodu: bağımsız kod incelemesi

Tarih: 12 Kasım 2026.

İncelenen dosyalar (`kayit/turetme/tr6/`): `tr6a_okada.py`, `tr6a_ffm.py`, `tr6a_katalog.py`, `tr6a_kosu.py`,
`tr6a_yapay.py`, `tr6a_test_yapay.py`, `tr6a_onbellek_kor.py`.

Metinler şu öncelikle okundu:
1. ön kayıt sürüm 3 (gövde sha256 `41ca1e95…`);
2. bu incelemeyle yazılan Ek 1;
3. `TR-6a_KODLAYICI-OKUMALARI.md` (41 okuma).

**Körlük beyanı.** Olay sonrası hiçbir katalog sorgusu yapılmadı ve gerçek lob oranı hesaplanmadı. `son-indir` ve `kos`
gerçek veriyle çalıştırılmadı; yalnız yapay veri ve `sinama` yolu kullanıldı. 2026 verisine ve Marmara 2017+ GNSS'e
dokunulmadı.

Ağa yalnız şunlar için çıkıldı:
- yayımlanmış Okada denetim değerleri (bosai.go.jp DC3D kılavuzu ve Okada 1985 PDF'i; çapraz denetim için açık bir
  DC3D gerçeklemesinin test dosyası);
- dört ana şokun sonlu fay ürünü BAŞLIKLARI (yalnız biçim).

İsteklerde genel User-Agent kullanıldı. 401 ya da 403 alınmadı; GitHub API'nin 403'ü aşılmadı, aynı dosya herkese açık
ham adresten okundu. Bağlayıcı tohumlar (20261114, 20261115) kullanılmadı. Commit atılmadı. `__pycache__`
bırakılmadı.

## Hüküm

**DÜZELTMEYLE KABUL.** Kodun çekirdeği ön kayıtla satır satır uyuşuyor:
- pencereler ve π;
- p₀, testere dişi ve en zayıf sırası;
- binom oyu, S7 McNemar ve S4;
- ters yön, etkin N0 ve kesme;
- katalog seçimi ve hüküm adı dilbilgisi;
- körlük kapıları.

Üç hesap/biçim hatası ve bir küçük bulgu düzeltildi (bölüm B). Kodlayıcının "KARAR GEREKİR" maddeleri (3, 9, 10) ve
tamlık riski Ek 1'de karara bağlandı ve koda işlendi.

Testler:
- 54 yapay sınamanın hepsi geçiyor (44'ü eski).
- Kodlayıcının 7 mutasyonuna 19 kaynak düzeyi ya da sabit mutasyonu eklendi; 26 mutasyonun 26'sı yakalanıyor.
- Tam koşu yaklaşık 1 dk 45 s sürüyor.

## A. Engelleyici bulgu

Yok.

En önemli konu kodda değil, yöntemdeydi: §3.5'in "Mc_lob + 0,3" yedeği tamlık sınamasını geçemiyordu. Ek 1 E1.3 (d)
ile çözüldü (bölüm F).

## B. Düzeltilen hatalar

- **H1 (önemli). Yedek (c)'nin Mc_son eki 0,2 yazılmıştı.** Metin (c)'yi "(b) ile birlikte" tanımlar. (b) +0,2
  ekler, ön denetim betiği (`tr6a_inc1_denetim.py`) de (c)'yi +0,4 ile sınamıştı.
  - Düzeltme: `KAT.MC_SON_EK["yedek_c"] = 0.4`; (d) de 0,4 kullanır.
  - Bu düzeltme olmasaydı bağlayıcı tamlık sınamasının (c) basamağı metindeki kuralı değil başka bir kuralı sınardı.
- **H2 (önemli). Birim denetimi gerçek katmanlı ürünleri reddediyordu.** Satır başına [5; 100] GPa sınırı
  us1000hhb1'in 19 alt fayını (2,2 GPa) dışarıda bırakıyordu. Sonuç BicimHata olur ve okuma 31 gereği bütün manifest
  aşaması durur.
  - Düzeltme: her alt fay [0,3; 300] GPa ve medyan [10; 100] GPa (Ek 1 E1.2).
  - Birim kayması (cm↔m ya da dyn·cm↔N·m) yine yakalanır.
- **H3 (orta). GeoNet yarı eşitliği 1 günlük parçaya inmeden VeriYok veriyordu.** 2 günlük parça eşitliği tutmayınca
  1 günlük parçalar yarılanmadan VeriYok çıkıyordu (§5 madde 1'in "1 günlük parçada da" şartı).
  - Düzeltme: satır sınırı olmayan sunucuda 1 günlük parça 12 saatlik yarılarla denetlenir. Yalnız KOERI bölünemez
    (okuma 30).
- **K1 (küçük). B3 bayrağının penceresi.** Bayrak [t0, t0 + 365 g) aralığında konuyordu. §7 B3 "temsilcinin son
  penceresinde" der.
  - Düzeltme: [t_s + 30 g, t0 + 365 g). Bilgi satırıdır, hükmü değiştirmez.

Ek 1 kararlarının kodda uygulanışı:
- E1.1: `ek1_degerlendir`, `yayimlanmis_denetim`, `OKADA_EK1_KARAR`.
- E1.2: `coz` için (i), (i′), (ii) ve `.fsp` Mech RAKE yedeği.
- E1.3: (d) yedeği şu parçalardan oluşur:
  - `ALT_PENCERE["yedek_d"]`;
  - `mc_son_hist(veri_yok=…)`;
  - `Analiz.tamlik_eleme`;
  - `mc_son_gercek`;
  - sahte ve S2'de geçersizlik;
  - hücre ölçütünde SE_ek.
- E1.4: MT istek yükü azaltma; bağlayıcı sınamada ön kayıt git denetimi; ön kayıt gövdesinin ilk 126 740 bayt
  üzerinden sha256 denetimi (`ONKAYIT_GOVDE_BAYT`).

Tamlık yüzünden K_kapı < 23 düşerse ad §6.4 (b)'nin "güç yok"udur. Kapalı liste genişlemez; neden cümlede yazılır.

Bunlara ek olarak `Mc_kul` tek işleve (`KO.mc_kul`) toplandı. Koşu kodu ve yapay sınama aynı işlevi kullanır;
mutasyon sınamasının tek noktadan vurabilmesi için.

## C. Denetlenen ve uygun bulunan noktalar

Pencereler (§4.2–§4.6, sınama `test_pencere_uclari_ve_pi`):
- gerçek: ön [t0 − 1826, t0 − 30), son [t_s + S0, son_bit);
- sahte: t′_j = t0 − 395 − 335(j − 1), son ucu t′_j + (son_bit − t0);
- S2: ön [t0 − 1826, t0 − 365), son [t0 − 395 + k + S0, t0 − 30), π_nk paydası 1461;
- D2: [t_s + 90, son_bit). (c) ve (d)'de D2 yoktur.

π = T_son/(1796 + T_son) kesmeden sonra yeniden hesaplanır.

Oylar ve eşikler:
- Binom oyu D, A (1e−12 toleransı) `tr6a_onkayit_sayilar.Oy` tablolarıyla birebir uyuşur.
- p₀: ⌈100 S/J⌉/100, J ≥ 30'da taban 0,50, J < 30'da 0,52.
- Testere dişi: JSON ile 23–80 aralığında birebir, > 80'de aynı kural.
- En zayıf sırası: N0 küçük önce, eşitlikte kimlik ters sözlük sırası.
- S7 McNemar tek yönlü: p = P(Bin(a + b, ½) ≥ a).
- S4, ters yön (p̂₀⁺) ve etkin N0 (> K/2) uygun.

Kesme (§3.7): bir gün önce, r_k ≤ 2L, grup dışı havuz olayı; T_son < 60 g ise çıkış.

Kataloglar:
- Katalog seçimindeki eşitlik sırası uygun.
- Ana şok satırları kümesizleştirmeden tümüyle çıkarılıyor (okuma 13'ün yazımı yanlış, kod doğru).
- GK + 730 g tampon başvuru gerçeklemesiyle eşdeğer.
- MAXC eşitlikte küçük değeri alıyor.
- Mc_son alt pencere birleştirmesi uygun.

Körlük:
- `tarih_denetle`: 2025-12-31T23:59:59 üstü ve 2026, istekten önce durur.
- `GercekKaynak.katalog`: "on" aşamasında sınır t0 − 30 g.
- `kor_maske` uygun.
- `.tr6a_kor` önbellek engeli uygun.

Git ve sha denetimleri:
- `git_denetle` commit ve upstream'e push edilmiş olmayı denetler.
- Manifest ve `kos` ön kayıt gövde sha'sını denetler. Gövde artık ilk N bayttır; ek eklendiği için tam dosya sha'sı
  değişir.

Önbelleği ya da ham dizinleri açabilecek `open(` çağrıları:
- `tr6a_katalog.py`: `Getirici.__init__`, `Getirici.__call__`, `kendi_indirmesini_oku`.
- `tr6a_ffm.py`: `indir`, `arsivden_oku`.
- `tr6a_kosu.py`:
  - `GercekKaynak.__init__` ve `_kaydet` (yalnız kendi `kaynak_kayit.json`'u);
  - `_ham_listesi_denetle` (`kos` aşamasında ham dosyaların sha256'sı; içerik ayrıştırılmaz);
  - `devam`, `asama_*`, `liste_oku`, `p0_izgarasi`, `sha256_dosya`, `onkayit_govde_sha`, `x_yaz` (manifest,
    işaret, JSON ve ön kayıt).

Yapay ve Okada dosyaları `open(` çağırmaz. Önbelleğin tek okuma yolu `tr6a_onbellek_kor.py`'dir. Olay öncesi
kodun olay sonrası dosyayı açan bir yolu bulunmadı.

## D. Kodlayıcının riskleri 5, 6, 7

**Risk 5: kapı seçim yanlılığı.** Kapı n_on ≥ 155 düşük N0'da yukarı dalgalanmayı seçer. Kesin Poisson hesabında
P(D | kapı) − P(D) şöyledir:

| N0 | P(D \| kapı) − P(D) | P(kapı) |
|---|---|---|
| 20 | +0,54 | ≈ 0 |
| 25 | +0,43 | 0,003 |
| 31,36 | +0,136 | 0,485 |
| 40 | +0,0004 | – |
| ≥ 60 | 0 | – |

Sahte zamanlar aynı kapıyı aynı Mc_lob kuralıyla uygular (n_on′ ≥ 155). Durağan bir dünyada p̂₀ aynı seçimi taşır ve
yanlılığı beklenen değerde soğurur: c(K; p₀) yükselir. Artık risk iki yerde kalır:
- sahte oyu geçersiz olan kümeler;
- durağan olmayan oran: ön pencere oranı sahte ön pencerelerden farklıysa.

Yapay katalog ölçütü (i) koşulsuz P(D) iledir; kapı koşullu değer bilgi satırıdır (okuma 15). Ek 1'de yazıldı.

**Risk 6: kümesizleştirme yanlılığı.** Yapay katalog sınamasında lob saf Poisson'dur. Ana şok artçılarının loba düşüp
büyük artçıların GK pencereleriyle son pencere sayımını azaltma etkisi orada sınanmıyor (okumalar 14 ve 19). Bu yanlılık
sahte zamanlarda yoktur, çünkü sahte zamanda büyük ana şok yoktur. Dolayısıyla p₀ bunu soğurmaz.

Korumalar tasarımdadır:
- S7: nötr lobda da düşüş varsa H1 "ayırt edilemez" olur. GK yanlılığı lob ayırmaz, nötr lobu da vurur.
- S1: pozitif lobda artış istenir. Yanlılık buna karşı çalışır, bu yüzden S1 tutmaz ve H1 düşer.
- D4: kümesizleştirmesiz sayım bilgi satırıdır.

Bu bir yöntem riskidir, kod hatası değildir. Kod metni uyguluyor. Kalan risk: yanlılık nötr ve gölge loba farklı
şiddetle vurursa (artçı yoğunluğu lob geometrisine bağlıysa) S7 bunu tam ayıramaz.

**Risk 7: hafif sınanmış B3/B4.** İkisi de bilgi satırıdır, hükmü değiştirmez. Okuma sonucu:
- B3 bayrak penceresi düzeltildi (K1).
- Kesme ile çıkan kümeler, örtüşen çiftler, tek bağlantı sayısı ve öncül komşu çıkarılmış X/K metne uygun.
- B4 (bilinen sonuçlu kümeler eklenmiş, Tohoku çıkarılmış) metne uygun.

Yeni sınama `test_B3_B4_bilgi_satirlari` bunları yapay dünyada yapısal olarak denetler. Kesme kodu mutasyonla da
sınanıyor (`_kesme` kaynak mutasyonları).

## E. Kodlayıcının 41 okuması

Hükümler: KABUL (yazıldığı gibi), DÜZELT (kod ya da yazım düzeltildi), EK-1'E (Ek 1'de karara bağlandı).

| # | Hüküm | Not |
|---|---|---|
| 1 | KABUL | Dosya adları. |
| 2 | EK-1'E (E1.1) | UC0 katsayısı artık yayımlanmış değerlerle doğrulandı (Okada 1985 Tablo 2, 108 değer; DC3D kılavuzu). Okada 1992 tabloları doğrulanamadı. |
| 3 | EK-1'E (E1.1) | Bağlayıcı ölçüt: Richardson, uzak alan eğimi ve 60 L, integral yakınsaması, yayımlanmış değerler. `OKADA_EK1_KARAR` kuruldu. |
| 4 | KABUL | 0,01 km sınaması ≥ 1 km noktalarda. |
| 5 | EK-1'E (E1.1) | Richardson artık bağlayıcı (≤ 1e−6). |
| 6 | EK-1'E (E1.1) | 90° eğim atımlı istisna gerekçeli (W²/12d² terimi). |
| 7 | KABUL | |
| 8 | KABUL | |
| 9 | EK-1'E (E1.2) | (i) → (i′) `.fsp` başlığı → (ii) geometrik. (ii) pratikte daima "veri yok". |
| 10 | EK-1'E (E1.2) | M0 `.fsp` başlığından. |
| 11 | DÜZELT (H2) + EK-1'E | Birim aralığı; ürün seçimi kabul. |
| 12 | KABUL | |
| 13 | DÜZELT (yazım) | Kod ana şok satırlarını olay sonrası kümesizleştirmeden tümüyle çıkarır (§3.6); okuma metni "ana olay olarak tutulur" diyor ve yanlış. Ek 1 E1.4 (c). |
| 14 | KABUL | Lob saf Poisson (risk 6'ya bakınız). |
| 15 | KABUL | Kapı koşullu değer bilgi satırı (risk 5). |
| 16 | KABUL | |
| 17 | KABUL | |
| 18 | EK-1'E (E1.3, E1.4 b) | `bolge_carpani = 1` bağlayıcı. |
| 19 | KABUL | |
| 20 | KABUL | |
| 21 | KABUL | (d) seçilirse yedek kalkar (E1.3). |
| 22 | KABUL | S6 koşulamadı. |
| 23 | KABUL | Yalnız j = 1; S2 kümeleri `_nk_kumeleri` ile kurulur, (d)'de yeniden kurulur. |
| 24 | KABUL | |
| 25 | KABUL | |
| 26 | KABUL | |
| 27 | KABUL | |
| 28 | KABUL | |
| 29 | KABUL | |
| 30 | DÜZELT (H3) | KOERI kuralı kabul; GeoNet 1 günlük parça düzeltildi. |
| 31 | KABUL | H2'den sonra katmanlı ürünler durdurmaz. |
| 32 | KABUL | |
| 33 | KABUL | İstek yükü azaltma E1.4 (e). |
| 34 | KABUL | Bu dosya commit edilmeden `son-indir` açılmaz. |
| 35 | KABUL | B3 bayrak penceresi düzeltildi (K1). |
| 36 | KABUL | |
| 37 | KABUL | |
| 38 | KABUL | (d)'ye de uygulanır. |
| 39 | KABUL | |
| 40 | KABUL | Tamlık nedeniyle K < 23 → "güç yok" (kapalı liste aynı). |
| 41 | KABUL | |
| – | KABUL | Bağlayıcı tohum reddi, kuru prova, Marmara satırı. |

## F. Ek 1 için yapay veri sayıları

**E1.1 Okada.** Hepsi tuttu.

| Denetim | Sonuç |
|---|---|
| Richardson, sınama 3 | 5,1e−15 |
| Richardson, sınama 6 | 1,2e−14 |
| Uzak alan eğimleri | −1,925 ile −2,074 arası |
| İstisna (90° eğim atımlı) | −1,286; 60 L'de 8,2e−3 (bilgi) |
| Integral oranları | 4,0 |
| m = 20 farkları | ≤ 8,6e−6 |
| Okada 1985 Tablo 2 (108 değer) | en kötü 0,975 yarım birim |
| DC3D kılavuzu | 0,856 yarım birim (−37,89814; 63,17894; 14,96068) |

Doğrulama yaklaşık 5 s sürüyor.

**E1.2 FFM yoklaması** (us7000c7y0, us1000hhb1, us2000cmy3, us6000jllz; yalnız başlıklar):
- `.param` başlığı koordinat anlamı ve M0 konusunda sessiz.
- `.fsp` başlıklarının hepsi "Coordinates are given for center of each subfault" diyor.
- `.fsp` Mo / `.param` moment toplamı ≈ 1,00. Üç üründe `.fsp` alt fay toplamı / Mo: 0,978, 0,945, 1,000.
- Eski ürünlerde `.param` derinliği `.fsp` merkezinden alt fay düşey yarı genişliğinin 2/3'ü kadar sığdır; jllz'de
  ikisi aynıdır.
- (ii) dört üründe de karar veremezdi: fark 0,11–0,43 km, yarı genişlik 1,25–2,65 km. (i′) dördünde de karar verir.

**E1.3 (d), geliştirme koşuları** (bağlayıcı değil, bölge arka planı = lob):

| Koşu | Kural | En büyük fark | > 0,02 hücre | Veri yok payı (ort) |
|---|---|---|---|---|
| n 2000, tohum 4242 | A2 | +0,5415 | 32 | 0 |
| n 2000, tohum 4242 | (c) | +0,5426 | 15 | 0 |
| n 2000, tohum 4242 | (d) | +0,0246 | 1 (M8 Mc3 N0 500 ap0) | 0,232 |
| n 2000, tohum 4243, kod yolu | (d) | +0,0231 | 1 (M7 Mc1 N0 100 ap0) | 0,232 |
| n 2000, tohum 4243, kod yolu | (a), (b) | +0,5415 | 33 / 21 | 0 |
| n 10 000, tohum 777, en yüksek 10 hücre | (d) | −0,0128 ile +0,0071 (SE 0,005) | 0 | – |
| n 20 000, tohum 780, en yüksek 6 hücre | (d) | −0,0049 ile +0,0029 | 0 | – |
| n 10 000, tohum 778 | A2 | +0,0485'e kadar | – | – |

Geliştirmedeki tek hücre aşımları gürültüdür; n = 2000'de SE ≈ 0,011. 12 hücrede bütün denemeler veri yoktur: düşük
Mc_lob ile büyük M_ana ve küçük N0 birleşimi. Küçük n_ok'lu hücrelerde koşullu fark güçlü negatiftir (−0,2 ile −0,46
arası), yani tutucudur. (e) tanımlanmadı.

## G. Mutasyon provası

Her mutasyon kodu geçici olarak bozar. Yakalanması, ilgili sınamanın AssertionError vermesi demektir. Mutasyonsuz
hâlde aynı sınamalar geçer.

Kodlayıcının 7 mutasyonu: ΔCFF işareti, μ = 0,6, lob eşiği 8 kPa, Mc_son sürüm 1, Mc_son eki 0, tampon 0, p₀
yuvarlaması. Hepsi yakalandı. Kesme mutasyonu veri düzeyinde ayrı sınamadır.

Yeni 19 mutasyon:

| # | Mutasyon | Yakalayan sınama |
|---|---|---|
| 1 | Son pencere t_s + S0 yerine t_s'de başlar | pencere |
| 2 | Ön pencere t0'da biter (ON_B = 0) | pencere |
| 3 | Sahte son ucu t_s'ye göre | pencere |
| 4 | π: T_ON = 1826 | pencere |
| 5 | π: kesme sonrası paydada T_son yok | kesme kodu |
| 6 | Mc_kul = Mc_lob | Mc_kul |
| 7 | Binom oyu F(n_son − 1) | oy tablosu |
| 8 | Testere dişi en küçük K | testere |
| 9 | p₀: J < 30 tabanı 0,50 | p₀ |
| 10 | McNemar a ↔ b | McNemar |
| 11 | Kesme aynı gün (kaynak) | kesme kodu |
| 12 | Körlük: 2025-12-31 kapısı devre dışı | körlük |
| 13 | Körlük: "on" aşaması t0 − 30 g sınırı yok | aşama sınırı |
| 14 | H1: yedek_c eki 0,2 | Mc_son |
| 15 | (d): Mc_lob + 0,3 geri gelir | Mc_son |
| 16 | (d): K düşürmeden önce sayılır | tamlık eleme |
| 17 | H2: birim [5, 100] GPa | birim |
| 18 | H3: GeoNet 1 günlük parça yarılanmaz | GeoNet |
| 19 | Okada: α = 0,6 | yayımlanmış değerler |

Sonuç: 26/26 yakalandı.

## H. Sınama sayıları

Komut: `python3 -I -B kayit/turetme/tr6/tr6a_test_yapay.py` (54 sınama, OK).

Yeni ya da yeniden yazılan sınamalar:
- `test_ek1_olcutu`, `test_ek1_degerlendirme_yolu`;
- `test_ek1_fsp_basligi_ve_geometrik`, `test_koordinat_ve_M0_karari_yoksa_durur`;
- `test_tensor_istek_yuku`, `test_pencere_uclari_ve_pi`;
- `test_ek1_tamlik_eleme`, `test_mc_kul_ve_satirlar`, `test_mcnemar`;
- `test_onkayit_govde_sha`, `test_B3_B4_bilgi_satirlari`.

Mc_son, GeoNet, birim, körlük ve aşama sınırı sınamaları genişletildi.

## I. Koşu komutları ve süre

Bağlayıcı sınama, Ek 1, bu dosya ve kod commit + push edildikten sonra koşulur:

    python3 -I -B kayit/turetme/tr6/tr6a_kosu.py sinama --baglayici

Kod ön kayıt ve kod dosyalarının commit + push edildiğini, ön kayıt gövde sha'sını ve `tr6a_sinama_sonuc.json`'un
olmadığını denetler. Tahmini süre yaklaşık 2,5 saattir (tek çekirdek):

| Parça | Ölçüm | Tahmin |
|---|---|---|
| Okada | – | ≈ 5 s |
| Yapay katalog, n = 20 000 | n = 200'de 48 s | ≈ 80 dk |
| Tamlık, basamak başına 96 hücre × 20 000 | hücre başına ≈ 8 s | ≈ 13 dk |

Tamlıkta A2 ile (a)–(c) geliştirmede tutmadığından beş basamağın hepsi koşacak; tamlık toplamı ≈ 65 dk.

Sonra `tr6a_sinama_sonuc.json` commit + push edilir. Ardından `manifest` aşaması gelir.

## J. Kalan riskler

1. **(d) yeni bir seçim kanalı açar.** Küme düşürme olay sonrası bölge histogramına dayanır ve bölge lobları içerir.
   Gerçek bir gölge düşüşü bölge sayısını azaltır ve kümeyi "veri yok"a itebilir. Bu, H1'e karşı çalışır (tutucu),
   ama gücü düşürür. Δτ = 0 dünyasındaki ölçüt bunu görmez.
2. **(d)'de veri yok payı yüksek.** Payı yapay ızgarada ortalama %23, 12 hücrede %100. Gerçek kümelerde K_kapı'nın 23
   altına düşmesi ("güç yok") olasıdır. Bu, gerçek veri görmeden kestirilemez.
3. **Risk 6 (lobda kümesizleştirme yanlılığı) yapay olarak sınanmadı.** Yalnız S7, S1 ve D4 korur.
4. **Risk 5'in artığı:** geçersiz sahte oylu kümeler ve durağan olmayan oran.
5. **E1.2 (ii) pratikte daima "veri yok"tur.** `.fsp` başlığı olmayan ya da sessiz bir ürün birimi düşürür.
   Yoklanan dört ürün (i′) ile çözülüyor.
6. **Okada 1992 tablo değerleri doğrulanamadı.** Yerine Okada 1985 ve DC3D kılavuzu tuttu; bağlayıcı ölçüt bunlara
   dayanır.
7. **Bağlayıcı tamlıkta (d)'nin gürültüyle düşme olasılığı.** n = 20 000'de 0,02 = 5,6 SE'dir; en yüksek gerçek fark
   ≈ +0,007 olduğundan olasılık çok küçüktür. Yine de düşerse metin gereği "koşulmadı (yöntem: tamlık sınaması)" olur.

## K. Değişen dosyalar (commit edilmedi)

- `kayit/onkayit/TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md`: sona Ek 1 eklendi. İlk 126 740 bayt değişmedi, sha256
  `41ca1e95…`.
- `kayit/onkayit/TR-6a_KOD-INCELEME.md`: bu dosya.
- `kayit/turetme/tr6/`:
  - `tr6a_okada.py`: E1.1;
  - `tr6a_ffm.py`: E1.2, H2;
  - `tr6a_katalog.py`: H1, H3, (d);
  - `tr6a_kosu.py`: E1.1–E1.4, K1, gövde sha, `mc_kul`;
  - `tr6a_yapay.py`: (d), SE_ek, `mc_kul`;
  - `tr6a_test_yapay.py`: sınamalar ve mutasyonlar.
