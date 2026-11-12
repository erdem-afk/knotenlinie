# TR-6a bağlayıcı yöntem sınaması: tutmayan hücrenin tanısı

12 Kasım 2026. Bağımsız tanı. Kodu ve Ek 1'i bu tanıyı yapan yazmadı. Yalnız yapay veri kullanıldı. Olay sonrası
katalog sorgusu yapılmadı, 2026 verisi kullanılmadı. Bağlayıcı tohum (20261114) yeniden koşulmadı. Ön kayıt ve kod
değişmedi. Tanı betikleri ve çıktıları `kayit/turetme/tr6/tani/` altındadır (tohumlar 601–608).

## 1. Hüküm

**(C) Hata yok.** Sapmanın nedeni yöntemin kendisidir: §3.6'nın tanımladığı kümesizleştirme, saf Poisson lobda bile
kısa son pencerede (335 g) uzun ön pencerede (1796 g) olduğundan daha az olay siler. Bu fark n_son'u göreli olarak
şişirir ve düşüş oyunu azaltır. Etki N0 ile hızla büyür: N0 31,36 ve 100'de ölçülemeyecek kadar küçüktür, N0 500'de
−0,017 ile −0,021 arasıdadır, N0 1500'de −0,09'dur.

- Kümesizleştirme kapatılınca P(D), kesin Poisson değerine döner.
- Koşu kodu §3.6'yı harfiyen uyguluyor.
- Beklenen değer doğru hesaplanmış.
- Sınama kodu, metindeki ölçütü metnin söylediği gibi kuruyor.

Metne göre TR-6a **"koşulmadı (yöntem: yapay katalog sınaması)"** diye kapanır (§9 adım 2, §6.4 1(a)). Olay sonrası
veri indirilmez ve aday elenmez. Yeniden açma ancak ayrı bir ön kayıtla olur.

## 2. Ölçütün metindeki tanımı

§9 adım 2'ye göre yapay katalog sınamasında "bütün hat (lob, Mc, kümesizleştirme, oy, sahte kalibrasyon)
çalıştırılır". (i) biçiminde lob saf Poisson'dur. Ölçüt şudur: "Δτ = 0 dünyasında gölge düşüş oyu oranı N0 ∈ {31,36;
100; 500} için **§4.3'teki kesin değerle** 3,5 SE içinde."

§4.3'teki değer, "P(D | H0, Poisson)" satırının kesin Poisson değeridir. Ek 1 (kapı seçim yanlılığı paragrafı) şunu
ekler: "(i) koşulsuz P(D) ile değerlendirilir".

Buna göre beklenen değer, **kümesizleştirme hariç** kesin Poisson H0 değeridir. Ölçülen değer ise kümesizleştirme
**dahil** hattın çıktısıdır. Metin, ölçüte yön ya da kümesizleştirme payı koymaz: ölçüt iki yanlı, 3,5 SE'dir. Sınama
kodu (`tr6a_yapay.yapay_katalog_sinamasi`) tam olarak bunu uygular:
- beklenen değer `S.Oy.olasilik(N0·1796/365,25, N0·335/365,25)`;
- SE √(p(1−p)/n), p beklenen değer;
- 20 000 deneme.

## 3. Kanıt (bağlayıcı olmayan tohumlar)

Her denemede bütün hat koşulur: `TekBirimSinama.deneme` ile aynı adımlar, sahte oylar yok, (i) dünyası (lobda saf
Poisson, bölgede ikincil diziler). Aynı katalog gerçekleşmesi beş biçimde sayılır (eşli):
- **V0:** hat, §3.6 pencereleri. Ön katalog [t0 − 2556, t0 − 30), son katalog [t0, t0 + 365), sayım
  [t0 + 30, t0 + 365).
- **V1:** kümesizleştirme yok (D4 biçimi).
- **V2:** son kataloğun önüne 730 g tampon eklenir (t0 − 730'dan başlar).
- **V3:** tek kesintisiz katalog [t0 − 3651, t0 + 400) bir kez kümesizleştirilir.
- **V4:** V2'ye ek olarak iki pencerenin sonuna 35 g veri eklenir.

"Artık", ortalama n_son − π·n'dir; H0'da 0 olmalıdır.

**N0 500** (tohum 601, 602, 603; toplam 14 000 deneme; kesin değer 0,48985):

| Biçim | P(D) | z (kesin değere karşı) | eşli fark (biçim − V0) | artık (olay) |
|---|---|---|---|---|
| V0 hat | 0,4731 | −3,95 | — | +0,81 ± 0,17 |
| V1 kümesizleştirme yok | 0,4906 | +0,17 | +0,0174 ± 0,0027 | −0,02 ± 0,17 |
| V2 son kataloğa 730 g ön tampon | 0,4810 | −2,09 | +0,0079 ± 0,0007 | +0,38 ± 0,17 |
| V3 tek kesintisiz katalog | 0,4838 | −1,44 | +0,0106 ± 0,0010 | +0,30 ± 0,17 |
| V4 V2 + iki pencere sonuna 35 g | 0,4845 | −1,27 | +0,0114 ± 0,0009 | +0,21 ± 0,17 |

- Bağlayıcı koşunun 0,4686'sı (fark −0,0212) bu tahminle uyumludur: V0'ın farkı −0,0167 ± 0,0042, iki farkın arası
  0,0045, birleşik SE ≈ 0,0055.
- Kümesizleştirme her iki pencerede yaklaşık %4 siler: ön pencerede 0,0399, son pencerede 0,0382–0,0398.
- Etkin oranın düşmesi (N 500 → 480) kesin değeri yalnız 0,0003 değiştirir. Sapmanın nedeni oran kaybı değil,
  pencereler arasındaki silme farkıdır.

**Öteki N0'lar** (eşli fark V1 − V0):

| N0 | n (tohum) | fark | Not |
|---|---|---|---|
| 31,36 | 4000 (604) | +0,0013 ± 0,0017 | ihmal edilebilir |
| 100 | 4000 (604) | +0,0033 ± 0,0028 | ihmal edilebilir |
| 1500 | 2000 (605) | +0,074 ± 0,011 | V0 0,403 (z −8,2), V1 0,477 (z −1,5), kesin 0,494; V3 ve V4 de z −4,3 ve −3,8'de kalır |

Bu, bağlayıcı koşuda yalnız N0 500 hücresinin tutmamasıyla uyumludur.

**Mekanizma ("gelecek kesmesi" kenarı; `tr6a_tani_kenar.py`).** Olay öncesi dönemin içinde 335 g'lük bir pencere
alındı. Önünde 730 g tampon vardır. Pencerenin sonundan sonra katalog 0, 35, 100 ve 335 g uzatılarak kümesizleştirildi.
Silinen pay şöyle çıktı:

| N0 | 0 g | 35 g | 100 g | 335 g | 1796 g'lük ön pencere (0 g) |
|---|---|---|---|---|---|
| 500 | 0,03982 | 0,04043 | 0,04075 | 0,04116 | 0,04085 |
| 1500 | 0,11057 | 0,11234 | 0,11305 | 0,11420 | 0,11500 |

GK pencereleri iki yanlıdır. M ≥ 4 için zaman penceresi ≥ 41 g, M 5'te 143 g, M 6'da 499 g'dür. Bu yüzden pencerenin
son günlerindeki olaylar, sonrasındaki daha büyük olaylarla silinemez. Bu kenarın mutlak büyüklüğü iki pencerede
aynıdır, ama 335 g'lük pencerede göreli olarak yaklaşık 5,4 kat ağırdır. §3.6'nın son penceresinin önündeki 30 g'lük
tampon da (öndeki 730 g'ye karşı) aynı yönde çalışır (V2).

İki kenarın toplamı, N0 500'deki +0,8 olaylık artığı açıklar:
- son kenar ≈ (0,04085 − 0,03982) · 459 · 0,843 ≈ 0,4 olay;
- ön tampon ≈ 0,43 olay.

Silme olasılığı lob yoğunluğuyla arttığından, z cinsinden sapma kabaca N0^1,5 ile büyür.

## 4. (A) ve (B) neden değil

- **Beklenen değer doğru.** `tr6a_tani_denetim.py`, `Oy` sınıfını kullanmadan, math.lgamma ile bağımsız bir hesap
  yapar. Sonuçlar §4.3 tablosuyla uyuşuyor:

  | N0 | 31,36 | 100 | 300 | 500 | 1000 |
  |---|---|---|---|---|---|
  | P(D) | 0,45852 | 0,47725 | 0,48694 | 0,48985 | 0,49281 |

  V1 (kümesizleştirmesiz hat) bu değere döner (z +0,17). Yerleştirme, Mc ve oy zinciri yansızdır.
- **Kümesizleştirme işlevi doğru.** `KAT.kumesizlestir`, başvuru `tr6_sayim.kumesizlestir` ile N0 500 dünyasında
  30/30 lob kataloğunda birebir aynı sonucu verdi.
- **Pencereler metindeki gibi.** `KAT.pencere_sayisi` §3.6'yı harfiyen uygular:
  - ön katalog [a − 730, b);
  - son katalog [t0, son pencere sonu), t_s + 30 g'ye kadar tampon;
  - yalnız lob içi ve Mc_kul üstü olaylar.

  Sapma, metnin bu tanımından doğar, uygulamadan değil.
- **Sınama kodu metnin ölçütünü kuruyor.** Ölçüt, koşulsuz P(D)'yi kesin Poisson değeriyle iki yanlı 3,5 SE içinde
  karşılaştırır. Metin bu karşılaştırmayı açıkça kümesizleştirme dahil hatla ister. "Beklenen değer kümesizleştirme
  dahil H0 değeri olmalıydı" okuması metinde yoktur. Şimdi bu okumayı benimsemek, bağlayıcı sonucu gördükten sonra
  ölçüt değiştirmek olur.

## 5. Yanlılığın hükme etkisi (bilgi; kapanışı değiştirmez)

- **Yön: H1 aleyhine (tutucu).** Δτ = 0'da düşüş oyu azalır, n_son göreli olarak artar. Yanlış H1 üretmez, gücü biraz
  düşürür. −10 kPa altında oy olasılığı ≈ 0,99 olduğundan güç kaybı küçüktür.
- **(ii) bunu soğuruyor.** Sahte pencereler aynı yapıdadır (30 g tampon, sonu kesik 335 g). Bu yüzden p̂₀ aynı kaymayı
  taşır. Bağlayıcı (ii) N0 500 sonucu: p̂₀ 0,461, kapı koşullu P(D) 0,4626, fark −0,0016.

  Ancak p₀ = max(0,50; ⌈100 p̂₀⌉/100) olduğundan, p̂₀ < 0,50 iken kayma eşiği zaten değiştirmez. Sonuç: α korunur, X
  biraz düşer.
- **Gerçek birimlerde payı (önsayım, `tr6a_onkayit_sayilar.json` `onsayim.19`; lob payı 0,25 varsayımlı kaba N0).**
  - 29 kümenin 2'sinde kaba N0 ≥ 500: 2003 Tokachi-oki (ISC, 583,7) ve 2011 Tohoku (ISC, 4501,4).
  - 3'ünde ≥ 300; üçüncüsü 316,3.
  - Kaba N0'lar yarıya inerse yalnız Tohoku ≥ 500 kalır.
  - Tohoku'nun hiç geçerli sahte zamanı yoktur (K_0). N0 4500'de yanlılık N0 1500'deki −0,09'dan da büyük olur;
    düşüş oyu H1 aleyhine güçlü biçimde baskılanır.
  - Gerçek lob N0'ları manifestten önce bilinmez.
- **Kapsam dışı.** Bu tanı yalnız durağan Poisson kenar etkisini ölçer. Kod incelemesinin Risk 6'sı ayrı bir
  mekanizmadır: lobda artçılar ve büyük artçıların GK pencereleri. Risk 6 yine sınanmadı ve bu tanı onun hakkında
  hiçbir şey söylemez.

## 6. Metne göre yapılması gereken

Kod hatası bulunmadı. §9 adım 2'ye göre TR-6a **"koşulmadı (yöntem: yapay katalog sınaması)"** diye kapanır:
- §6.4 madde 1(a) uygulanır;
- olay sonrası veri indirilmez;
- aday elenmez;
- manifest aşaması açılmaz (`sinama_degerlendir` de bunu verir);
- yeniden açma ancak ayrı bir ön kayıtla olur.

## 7. Kök oturumun karar vermesi gereken açık noktalar

1. **Hükmün kaydı.** Tutmayan hücre tutucu yöndedir: H1 aleyhine, α'yı bozmaz. Metin ise ölçütü iki yanlı koyar ve
   yön istisnası tanımaz. "Yanlılık tutucu, geçmiş sayılsın" okuması bağlayıcı sonuçtan sonra yapılmış bir ölçüt
   değişikliği olur. Bu tanı onu önermez.

   Kök oturum, kapanış kaydına şu notu eklemeye karar verebilir: "neden yöntemin bilinen kenar etkisi (kodlayıcının
   önceden yazdığı ≈ 0,02 riski), yön H1 aleyhine". Bu not hükmü değiştirmez.
2. **Olası bir yeni ön kayıt için** (yalnız yapay bulgu, bağlayıcı değil):
   - Son pencereye ön katalogdan 730 g tampon vermek sapmanın ancak ≈ %45'ini giderir (V2).
   - Pencere sonundaki "gelecek kesmesi" bu tasarımda kaçınılmazdır. Kesintisiz kümesizleştirme (V3, V4) bile N0
     1500'de z ≈ −4 bırakır.
   - Seçenekler şunlardır:
     - ölçütün beklenen değerini sahte pencerelerden almak, yani (ii) biçimi;
     - (i)'yi tek yanlı (H1 yönü) kurmak;
     - kümesizleştirmesiz sayımı (D4) ana satır yapıp artçı sorununu başka yolla ele almak;
     - N0 ızgarasını gerçek lob N0'larına göre genişletmek (Tohoku düzeyi).
   - Bu seçimler yeni ön kaydın işidir.

## Dosyalar

- `kayit/turetme/tr6/tani/tr6a_tani_kumesiz.py`: V0–V4 eşli karşılaştırma (tohum 601–605).
- `kayit/turetme/tr6/tani/tr6a_tani_denetim.py`: bağımsız kesin P(D) ve kümesizleştirme başvuru eşliği (tohum 606).
- `kayit/turetme/tr6/tani/tr6a_tani_kenar.py`: gelecek kesmesi kenarı (tohum 607, 608).
- `kayit/turetme/tr6/tani/tr6a_tani_sonuc.json`: bütün çıktılar.

Yeniden üretmek için deponun kökünde şunlar koşulur (iki süreçle yaklaşık 25 dk):
- `python3 -I -B kayit/turetme/tr6/tani/tr6a_tani_kumesiz.py 601 4000 500`
- 602 4000 500
- 603 6000 500
- 604 4000 100 31.36
- 605 2000 1500
- `tr6a_tani_denetim.py 606 15`
- `tr6a_tani_kenar.py 608 1500 500` ve `607 400 1500`
