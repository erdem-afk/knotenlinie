# TR-13c sayım kuralı (sayımdan ÖNCE yazıldı): M ≥ 6,0 ile yeni bağımsız küme sayısı ve MDE

Tarih: 17 Kasım 2026. Durum: **sayım kuralı; ön kayıt değil.** Bu dosya, yeni adayların ortak Mc, GK74 ve doyma
sonrası sayıları hesaplanmadan önce commit edilir. Sonuç `TR-13c_SAYIM.md`'de, kod ve json `kayit/turetme/tr13c/`'de.
Sonuçtan sonra bu kural değiştirilmez; değişirse rapor beyan eder.

## 0. Sayımdan önce görülmüş olan

- `tr13_tamsayim.json` satırları (TR-13 Ek 1; yayımlı): olay, küme, R, katalog, Mc_önce, Mc_ref, N3bg (yalnız
  Mc_önce'de, ortak Mc'siz), ref_gecer. `sayim_tam_satirlar.json` (= sayim4) içindeki örnek tahminleri.
- TR-13b koşusunun 15 olayının hazırlık sayıları ve z'leri (`tr13b_sonuc.md`). Bu 15 olay TR-13c'de **geliştirme
  verisidir**, hükme girmez.
- Yeni adayların ortak Mc_b ile GK74 sonrası N3bg'si, doyma adımı ve N_ref'i **görülmedi**. Gerçek katalogda hiçbir
  yerelleşme ölçüsü (V(q), Gini, z) hesaplanmaz; `tr13b_kosu.kos()` çağrılmaz.

## 1. Aday listesi

**Ana liste (TR-13b §2'nin eşiği 6,5 → 6,0 indirilmiş aynısı):** `tr13_tamsayim.json` satırlarından
6,0 ≤ M < 6,5 ve `ref_gecer["0.3"]` doğru olanlar, dosya sırasıyla. M ≥ 6,5 olup TR-13b listesine girmeyen satırlar
aynı §2 kuralıyla (ref_gecer yanlış) yine dışarıdadır. Bu kuralla 11 satır:

| id | olay | küme | TR-13b kümesi mi |
|---|---|---|---|
| ci700917 | North Palm Springs 1986 | 397 | evet (geliştirme) |
| ci134894 | Elmore Ranch 1987 | 397 | evet (geliştirme) |
| ci3019681 | Joshua Tree 1992 | 397 | evet (geliştirme) |
| usb000rtp6 | Yakutat 2014 | 847 | hayır |
| nc72282711 | South Napa 2014 | 854 | hayır |
| us20005hzn | Kumamoto öncü 2016 (M 6,2) | 901 | evet (geliştirme) |
| us10006pdp | Mutatá 2016 | 910 | hayır |
| us20007fta | Kurayoshi 2016 | 911 | hayır |
| us10008npq | Tacikistan 2017 | 1102 | hayır |
| ci38443183 | Ridgecrest öncü 2019 (M 6,4) | 979 | evet (geliştirme) |
| us6000nyzk | Doğanyol 2024 | 1137 | hayır |

- **Küme** = TR-13 kuralı (1175 ana şokta tek bağlantı: uzaklık ≤ R_i + R_j ve süre ≤ 10 y), `kume` alanından aynen.
  Ayrıca kodla doğrudan çakışma denetimi: her geçen yeni olay ile TR-13b'nin 16 olayı arasında uzaklık ≤ R_i + R_j ve
  |Δt| ≤ 10 y.
- **Yeni küme** = TR-13b ön kayıt listesinin 14 kümesinde (397, 160, 303, 395, 1141, 689, 727, 802, 901, 942, 979,
  1139, 1035, 1144) olmayan küme. TR-13b kümesine düşen M 6,0–6,49 olaylar sayılır ve yazılır ama K'ye girmez.
- **Yeni K** = §3.1–3.3'ü geçen en az bir üyesi olan yeni küme sayısı.

## 2. Kurallar (TR-13b ön kaydı §3.1–3.3, dondurulmuş, değiştirilmeden)

1. Ortak Mc_b = max(Mc_önce, Mc_ref) (`tr13_tamsayim.json`); süzgeç [t − 10 y, t), t < 2026-01-01, derinlik ≤ 40 km.
2. GK74 m ≥ Mc_b ile indirilen bütün dairede (ComCat R_ind, ötekiler R); N3bg = [t − 3 y, t) arka planı, R içinde.
3. N3bg > 100 iken Mc_b += 0,1 ve GK74 yeniden; son N3bg < 50 → düşer; referans [t − 10 y, t − 3 y) arka planı
   < N3bg + 5 → düşer; arşivde parça eksik → düşer (veri yok).

Uygulama: `tr13b_kosu.hazirla`, `katalog`, `arsiv_oku`, `uye_adlari` içe aktarılarak, değiştirilmeden çağrılır (bu
işlevler yalnız sayı üretir; okundu). Önce iki ham arşivin sha256'sı `tr13_ham_sha256.txt` ile denetlenir.

## 3. İki okuma

- **(a) bütün bölgeler:** yeni K.
- **(b) yoğun ağ:** geçen olayın ortak Mc_b'si (doyma öncesi) **≤ 2,5**. Bir yeni küme, (b)'yi sağlayan en az bir
  geçen üyesi varsa (b)'de sayılır. Ölçüt katalogdandır; bölge adı (Kaliforniya, Japonya, Yeni Zelanda …) yalnız
  bilgi olarak yazılır. Not: Mc_önce ve Mc_ref bu kural yazılırken görülmüştü (§0); N3bg görülmemişti.

## 4. Bilgi satırları (yeni K'ye girmez)

- (i) 6,0 ≤ M < 6,5 olup ref_gecer[0,3] yanlış olan tamsayım satırları (ak995cti1ypa Minto 1995, usb000m8ch
  Lixouri 2014, us7000g8n3 Hualien 2022) aynı §2 adımlarından geçirilir ve sonucu yazılır.
- (ii) **Ek tarama:** tamsayıma hiç girmemiş, önce-penceresi temiz, 6,0 ≤ M < 6,5 ve yalnız örnekten tahmin edilmiş
  (en iyi katalog ISC_ornek) olaylardan örnek N3bg_mc ≥ 20 olanlar: us7000irp8 (Düzce 2022), usp000jmcv (Japonya
  2012), usp000jqf3 (Palu 2012). ISC FDSN'den [t − 10 y, t), R dairesi, M ≥ örnek Mc − 0,3, yıl yıl; genel
  User-Agent; bitiş < t ve ≤ 2025-12-31; 401/403 aşılmaz ("doğrulanamadı"). Mc_önce = [t − 3 y, t) MAXC + 0,2,
  Mc_ref = [t − 10 y, t − 3 y) MAXC + 0,2 (20–49 olayda + 0,3); TR-13 Ek 1 referans şartı (Mc_ref ≤ Mc_önce + 0,3,
  N_ref,bg(m ≥ Mc_önce) ≥ 100); sonra §2. Geçen olursa "genişletilmiş K" ayrı yazılır; ana K değişmez. İndirilenler
  `/mnt/project-files/turetme/tr13c-ham/`, sha256 listesiyle. Düzce 2022 Marmara kutusundadır; yalnız sayı yazılır,
  Marmara terimi değildir.

## 5. MDE (yalnız yapay ETAS)

- Bileşim: ana listede geçen **yeni** üyelerin gerçek (R, doyma sonrası N3bg) değerleri ve küme yapısı.
- Yöntem: `tr13b_inc2.py` düzeni; bölge üreteci, kalibrasyon ve süzgeç dondurulmuş koşu betiğinin kod incelemesi
  sonrası işlevleri (`tr13b_kosu.yapay_bolge` B_ref 200, `kalibre` 40 + 40 deneme kendi R'de, `sonlu_z`: z tanımlı ve
  önce N ≥ 50). Sıfır havuzu üye ve dallanma (0,4 / 0,6 / 0,8) başına 400; veri dallanma 0,6, ayrı kalibrasyon,
  sinyalsiz 300 ve f = 0,1 / 0,2 / 0,3 / 0,4 / 0,5 / 0,6 için 150. Sıfır 200 000, veri 20 000 küme çekilişi.
  Tohum 20261117.
- **R0 tek liste biçimi:** üç dallanmanın üçünde de yeni listede p ≤ 0,05. Yeni listede BZ20 keşif olayı yok
  (keşif kümeleri 397, 979, 395 TR-13b kümeleridir), bu yüzden ikinci (keşif dışı) liste yoktur.
- Çıktılar: f = 0,1…0,6 güç eğrisi, MDE (güç 0,80, doğrusal ara değer), sinyalsiz yanlış alarm. Duyarlılık: K × 2
  (her küme bağımsız iki kez çekilir) ve K × 0,5 (K/2 kümelik bütün alt kümelerin ortalama gücü; K tekse ⌊K/2⌋).
  Okuma (b) için aynı hesap (b) alt kümesinde.
- Etki büyüklüğünün kaynağı: f ≈ 0,2 **tahmin** (TR-13 benzetimi; literatür sayısı okunamadı, ESIK-DAYANAGI).
- **Bilgi:** TR-13b'nin koşuda kalan 15 olayı (hazırlık sayıları `kosu/durum.json`) + yeni üyeler birleşik listesinde
  aynı R0 tek liste MDE'si. TR-13b z'leri görüldüğü için birleşik liste hükme giremez; yalnız "birleşik bilgi satırı"
  seçeneğinin tartışılması içindir.

## 6. Dal kuralı (okuma (a)'nın MDE'si bağlar; (b) yazılır)

- Yeni K < 4: "veri yok"; MDE yine yazılır (benzetim aralığında güce ulaşılmazsa "f > 0,6").
- **MDE ≤ 0,25:** TR-13c ön kaydı yazılır.
- **0,25 < MDE ≤ 0,39:** TR-13b ile birleştirilmiş bilgi satırı seçeneği tartışılır (ön kayıt yazılmaz).
- **MDE > 0,39** ya da güce ulaşılmaz: TR-13c ön kaydı yazılmaz; M ≥ 6,0'a inmek bu açık veriyle K'yi yetecek kadar
  büyütmüyor.
- Hiçbir aday elenmez. Bu bir H0 ya da yerelleşme hükmü değildir.

## 7. Körlük

2026 ve sonrası yok; ana şok sonrası pencere yok; Marmara GNSS'e dokunulmaz; İstanbul için olasılık yazılmaz.
