# TR-7c koşu kodu: bağımsız kod incelemesi (koşu dondurmasından önce)

Tarih: 17 Kasım 2026. İncelenen: `kayit/turetme/tr7c/tr7c_kosu.py` (gelen sha256 `345dc176…73b3`), `tr7c_test_yapay.py`
(+ json), `tr7c_mf.py`, `tr7c_duman.py`, `tr7c_tr7b112.py`, `tr7c_kd_k5.py` ve json'ları; kodlayıcının belgesi
`TR-7c_KODLAYICI-OKUMALARI.md` (O-1…O-41, KMS-1…KMS-10). Bağlayıcı metin: `TR-7c_tetiklenmis-tremor_ONKAYIT.md` (KARAR
METNİ DONDURULDU, bd3c93a; §0 sırası), INCELEME-0/1/2, `TR-7c_USTVERI.md`. Dayanılan kod: `tr7/tr7_cekirdek.py`,
`tr7/tr7_kosu.py`, `tr7/tr7_indir.py`, `tr7b/tr7b_yapay.py`, `tr7b/tr7b_yapay2.py` (değiştirilmedi). Karar metni,
inceleme dosyaları, TR-7/TR-7b dosyaları değiştirilmedi. Ben kodun yazarı değilim; amaç kusur bulmaktı.

İncelemecinin dosyaları: `kayit/turetme/tr7c/kodinc/`
- `tr7c_kodinc.py` (+ `tr7c_kodinc.json`): birim, kapı, uçtan uca sınamaları ve 31 yeni mutasyon; yapay pencere üreteci
  bu dosyada bağımsız yazıldı (kodlayıcının üreteci kullanılmadı).
- `tr7c_kodinc_kd.py` (+ `tr7c_kodinc_kd.json`, `tr7c_kodinc_kd_say.json`): kodlayıcının `tr7c_kd_k5.py`'sini
  değiştirmeden tam ölçekte koşan sarmalayıcı ve KD'nin koşulmayan satırları için K0/K5 bayrak ayrışma sayımı.

Körlük ve TR-13b §G dersi: bütün sınama süreçleri ilk satırda bir denetim kancası (`sys.addaudithook`) kurar; soket,
`/mnt/project-files` altında açma, gerçek çıktı dizinine (`tr7c/kosu/`) yazma/dizin kurma ve alt süreç reddedilir ve
sayılır. Gerçek kip yolları yalnız bu kanca altında ve kapı KAPALIYKEN çağrıldı; kapının açık hâli yalnız
`kosu_dondurulmus_mu(onkayit=geçici kopya)` ile sınandı, açık kapıyla hiçbir gerçek yol çağrılmadı. **Hiçbir ağ
isteği yapılmadı; `/mnt/project-files` altında hiçbir dosya açılmadı** (Tohoku zarf deposu da açılmadı; duman sonucu
kodlayıcının json'undan okundu). Reddedilen tek girişim: obspy içe aktarılırken kendi sürümünü bulmak için çalıştırdığı
`git rev-parse` alt süreci (site-packages dizininde; depo ya da veriyle ilgisiz). 2026+ veri yok. Maliyet 0 €.

## Hüküm

**DÜZELTMEYLE KABUL.** Kod karar metninin dallarını, sırasını, etiketlerini, D-2 denetimini, kapıyı ve tek koşu kilidini
doğru uyguluyor; üç kusur bulundu ve koda işlendi (K-1…K-3, yeni sha256 §H). K-1 bağlayıcı bir kuralın (D-1) gerçek
koşuda sessizce uygulanmaması idi ve yapay sınamaların hiçbiri onu görmüyordu. Koşu dondurmasından önce kapanması
gerekenler: §D'deki 10 ek cümle ve §I'daki ek cümleler (aynen), §C'deki iki öneri ve §G'nin hacim düzeltmesi. Tasarım
düzeyinde değiştirmediğim, raporladığım üç konu: gerçek I/O katmanı hiç koşmadı (O-34; §B.3), `asama_kos`'ta TR-7'nin
aşama önkoşulu ve durma kaydı yok (§B.4), D8 (ham yoklama günlükleri) bu incelemede açılmadı (§A notu).

### Bulunan kusurlar ve düzeltmeler

- **K-1 (önemli; D-1 ihlali): Vanuatu 2009 biriminin dondurulmuş üstverisi okunmuyordu.** `birimler_kur` birleşik
  birimin USTVERI kaydını `ub.get(evids[0])` (= `'200910072203'`) ile arıyordu; USTVERI bu birimi `'VANUATU2009'` adıyla
  yazar. Sonuç: birimin `maskelenen` listesi `None` oldu ve `dunya_kur` bu birim için **hiçbir E1 satırı üretmedi**.
  Yani D-1'in "N 28 'öteki olay' olarak M ≥ 7,0 kuralıyla (P ve S, 240 sn) maskelenir" cümlesi gerçek koşuda
  uygulanmayacaktı: N 28'in (M 7,8) P'si (22:31:18) ve S'si (22:40:04), usp000h2gr'nin (M 7,4) P ve S'si ve iki M 6,8
  P'si maskesiz kalacaktı. N 28'in P'si birimin Q aralığının içindedir (K5'in Q doğrusunu kirletir), S'si ve M 7,4'ün
  fazları W ve K1b içindedir (sahte küme ve N'de yanlış algılama). Ayrıca K1b açık payı dondurulmuş 0,841 yerine
  "pencereden" (yazılmayan alan, varsayılan 1,0) okunuyordu ve `tetikleyici_id` boştu. Yön: N'de algılamayı artırır,
  yani Fisher'ı zorlaştırır (tutucu), ama bağlayıcı bir kuralın uygulanmamasıdır ve D-9'un genliği eşlenmiş
  sınamasıyla ilgisi olmasa da X_N'yi bozar. Kodlayıcının sınamaları birim sayısını (29) denetliyor, birimin maskesini
  ve payını denetlemiyordu; O-4'teki "K1b'si USTVERI'nin dondurulmuş birleşik aralığı" cümlesi kodda doğru değildi
  (K1b sayıca tesadüfen aynı çıktı: formül USTVERI'yle saniyesi saniyesine tuttu). Düzeltme tek satır:
  `u = ub.get(bid)`. Sınama: U13 (pay 0,841, 6 E1 satırı, N 28 P ve S 240 sn; 39 P/N biriminin hepsinde dondurulmuş
  pay ve E1 satırı kullanılıyor). Mutasyonla eski hâle döndürmek yakalanıyor.
- **K-2 (orta; kapı): kapı gerçek I/O motorunun sha256'sını denetlemiyordu.** Gerçek kip `tr7_kosu.py` ve
  `tr7_indir.py`'yi çağırır (indir–zarfla–sil, `ws_kur`, maske, MDA girdisi, StationXML). Kapı yalnız `tr7c_kosu.py`,
  `tr7c_mde_ek.py`, D-2 dosyaları ve repo girdilerini denetliyordu; TR-7 motoru dondurmadan sonra değişse fark
  edilmezdi. Düzeltme: `TR7_MOTOR` sözlüğü (`tr7_kosu.py` `ce439a47…9005`, `tr7_indir.py` `0763f46d…1f2f`;
  `tr7_sonuc.md`'deki TR-7 kod sha'larıyla aynı) ve `kosu_dondurulmus_mu` içinde `d2_denetle(TR7_MOTOR)`. Sınama: kapı
  grubu "K-2" satırı.
- **K-3 (küçük; E-1 gerçek katmanı): uzun periyot kaydının anahtarında konum kodu yoktu ve sürdürmede "bulundu" bilgisi
  kayboluyordu.** `lp_indir` ve `GercekKaynak.lp_adaylari` kayıtları (pencere, istasyon, kanal) ile anahtarlıyordu; bir
  istasyonda aynı kanal kodu iki konumda varsa (ör. `00.BHZ` ve `10.BHZ`) iki kanal aynı kaydı (son yazılanı) okur ve
  E-1'in seçtiği konumun yerine öteki konumun verisi kullanılabilirdi. Ayrıca kesintiden sonra sürdürmede, önceden
  başarıyla indirilmiş kanal `gecti` saymıyordu; kod bir sonraki (daha uzak) istasyona da istek atardı (seçim
  değişmezdi, yalnız fazla istek). Düzeltme: satıra `konum` eklendi, anahtar (pencere, istasyon, kanal, konum); önceki
  başarılı kayıt `gecti` sayılır. Bu katman kapı kapalıyken çalıştırılamadığı için yalnız okuma ile doğrulandı.

Her değişiklik `# K-n (kod incelemesi)` yorumuyla işaretli.

## A. Karar metni ↔ kod eşlemesi

| # | Bağlayıcı kural | Kodda | Durum | Dayanak |
|---|---|---|---|---|
| A1 | Olay listesi (Z2; §3.1 10 P, §3.2 30 N, bilgi Kunlun/Tonga; Tohoku dışarıda) | `P_OLAY`, `olaylar`, `birimler_kur` | uyuyor | U1: listeler karar metninin tablolarından ayrıştırılıp karşılaştırıldı |
| A2 | N 27 + N 28 tek birim (D-1): W, K1b, R/Q N 27'nin, E1'de N 28 maskelenir, bir kez sayılır | `BIRLESIK_BIRIMLER`, `birimler_kur`, `dunya_kur` | **sapma → K-1 ile uyuyor** | U13; E2 (n_N 29, X_N'de bir kez) |
| A3 | n_P, n_N: ≥ 3 liste istasyonu ve K1b'nin ≥ %50'si açık (dondurulmuş pay) | `taranan_mi` + `ws_kur` (N_IST_MIN 3) | uyuyor (K-1 sonrası Vanuatu dahil) | U13, U14 (0,50 sayılır) |
| A4 | K5 bayt bayt `tr7b_yapay2.K5`; değiştirilmeden içe aktarılır | `k5_ist` → `Y2.K5` | uyuyor | U2 (modül dosyaları), U3; kodlayıcının §11.2 38/38 |
| A5 | D-2: üç dosyanın sha256'sı, K5 içe aktarılmadan önce; çağrı ağacında başka dosya yok | `d2_denetle` (modül başında), `assert Y.c is K` | uyuyor | U2 (sha'lar metinden ayrıştırıldı), U3 (`sys.setprofile` ile K5 çağrı ağacı: depo içinden yalnız `tr7b_yapay2.py`, `tr7b_yapay.py`) |
| A6 | Toplama: istasyonların ≥ yarısı → küme atılır | `ayikla_k5` | uyuyor | U8 (4/2 atılır, 3/1 atılmaz) |
| A7 | Q = [T0 + t_P (iz ortası, iasp91), W başı) ∖ maske | `GercekKaynak.pencere` | uyuyor; "W başı" = Wb başı (KMS-4) | U12: 41 birimde, derinlik 0–700 km, Q başı > 0 ve Q ≥ 189 sn; K5'in `q[Q0:Q1]` dilimi sarmaz |
| A8 | D30M3 (Z3): (i) X_P ≥ max(⌈n_P/2⌉, X_min); (ii) N_PK ≥ 5 ve FAR ≤ 0,30; (iii) Fisher tek yanlı üst kuyruk ≤ 0,05; (iv) ≥ 3 P olayında p ≤ 0,01 | `z3`, `fisher_tek`, `xmin` | uyuyor (X_min K2'siz, KMS-5) | U4 (scipy hypergeom, fisher_exact), U5, U6 |
| A9 | Dallar ve sıra (Z4) + D-7 okuma kuralı; X_min yoksa (i) yok; A90 belirsiz/> 100 µm/s ise (d) yok | `k1c_dal` | uyuyor | U6: 126 060 noktada metinden yazılmış başvuruyla 0 fark (kodlayıcının ızgarasından ayrı, scipy ile) |
| A10 | Marmara yalnız (b) | `marmara_acilir`, `marmara_kos` | uyuyor (bağlantı yazılmadı, O-30) | U6; kapı: `marmara_kos` her durumda durur |
| A11 | D-8 eki (c/d/e), Ö-d "(kalan: …)" | `k1c_cumle`, `mde_degeri` | uyuyor | U16: §7.3 tablosu; n_P 8–10 × n_N 20–29 hepsi dondurulmuş |
| A12 | D-9 genlik etiketi (4 N; K1b ile kesişen sağ küme; p ≤ 0,01; VAR'ı engeller; ölçülemeyen sayısı yazılır) | `k1c_hesap`, `var_verilebilir` | uyuyor (yalnız taranan olaylarda aranır; 4 olayın dondurulmuş payı 0,878–1,0, fark doğmaz) | U1 (GENLIK4 metinden), E2 |
| A13 | D-10 cümlesi ve "Parkfield modülasyonu geçti" (⌈X_P/2⌉) | `k1c_cumle`, `mod_gecti` | uyuyor | E3 |
| A14 | E-1 kanal seçimi: B/H bant, H alet, yanıt oranı ≥ 0,5, W/R örtüsü ≥ %90; en yakın istasyon; HH sonra BH; yatay yoksa yalnız Z | `e1_secim`, `lp_adaylari_manifest`, `lp_indir` | uyuyor (K-3 ile) | U9 (6 durum) |
| A15 | E-2: k_koşu, koşu durmaz, "k: üstveriden 10, koşuda [..]", k < 10 ise güç bilgisi | `k1c_hesap`, `k1c_cumle`, `k_guc` | uyuyor | E3 (k 5, güç 0,61/0,24), U15 (§7.3 k tablosu) |
| A16 | Modülasyon: TR-7 §6.4 aynen; `default_rng(20261112 + 3)` yeni örnek; kümeler T0 sırasıyla, olay içinde I′ başı | `modulasyon_turu`, `modulasyon_kume` | uyuyor; P ve 29 N iç içe tek akış (KMS-2) | U10 (`K.mod_p` ile birebir), E1/E5 (bağımsız başvuruyla p'ler birebir) |
| A17 | Önce N sonra P; Z3/Z4 bütün olaylardan sonra; hüküm bir kez | `algilama_turu`, `k1c_kos` | uyuyor | E1 (jsonl sırası N×29, P×10, B×2; Z3/Z4 tek çağrıda en sonda) |
| A18 | Tek koşu kilidi | `k1c_kos` (dosya varsa hiçbir şey hesaplanmaz; "x" kipi) | uyuyor | E1 (ikinci çağrı hiçbir pencereye dokunmaz) |
| A19 | Rastgele negatifler (TR-7b §6.3): 10 P + Macquarie + Peru 2007, 10'ar, `default_rng(20261116 + 1)`, N_PK ≤ 120; f_PK W'nin herhangi bir yerinde; MDA yalnız algılamasız negatifte, 3 başlangıç | `negatif_sec`, `negatif_turu`, `k1c_hesap` | uyuyor | E1/E2 (f 1/12, MDA 11 pencerede, 36 deneme) |
| A20 | (b′) etiketi, A_PK, ŝ, ŝ_alt, bilgi satırları (Kuril 2007 çıkarılmış Z3, 4 N algılama, X/n, Q doğrusu) | `k1c_hesap` | uyuyor | kodlayıcının sınamaları |
| A21 | Bilgi satırları "liste sınıfına karşı kuyu sınıfı" (Z4) ve "N 27/N 28 ayrı Z3 (iii)" (D-1) | yok | **sapma (bilgi; dal değiştirmez)** | O-28, O-29; ek cümleleri §D (KMS-7, KMS-10) |
| A22 | TR-7 §7.2 uygulama hatası yolu, bir kez, yalnız (d)/(e) | yok | **sapma (izin verilen bir yolun yokluğu)** | §D KMS-8 cümlesi |
| A23 | Durum dosyası `kayit/turetme/tr7c/TR7C_KOSU_DURUM.json` (§10 madde 6) | `kosu/TR7C_KOSU_DURUM.json` | **sapma (yol)** | §I ek cümlesi |
| A24 | Kör koşu kapısı (§10 madde 5) | `gercek_kapi`, `kosu_dondurulmus_mu` | uyuyor (K-2 ile) | §B |
| A25 | Bilgi birimleri (Kunlun 2001, Tonga 2006) | B sınıfı, algılanır, modülasyon akışına girmez | belirsiz: USTVERI'de E1 satırları ve pay yok → bu iki satır E1 maskesiz | §I ek cümlesi |

Ö-i notları (Z8): (1) `_rho` eşit değerlere ortalama sıra vermez (`argsort(argsort)`); sürekli L'de Spearman ile fark
< 1e-9 (U11). L 0,01'e nicemlenmiş yapay örnekte fark görülür (U11 json'unda en büyük ve medyan fark); gerçek L,
float32 zarfın 5 sn ortalamasının log10'udur, eşitlik pratikte yoktur. Okuma: davranış K5'in kendisidir ve D-2 gereği
değiştirilemez; ek cümle §I'da. (2) `_k1_kalinti`'nin Q dizinleri gerçek veride pencere ekseninin saniyeleridir (k0 =
⌊R başı − 600⌋); maske aynı eksende (`saniye_maskesi(…, k0, n)`) kurulur; Q başı her birimde ≥ 4455 (U12), dolayısıyla
negatif dizin sarması yoktur. (`q_dogrusu_var`'daki `max(0, …)` yalnız bilgi satırındadır ve gerçekte devreye girmez.)

D8 (ham yoklama günlükleri `/mnt/project-files/turetme/tr7b-ham/`): görev tanımı gereği bu incelemede açılmadı.
Koşu dondurmasından önce koordinatörün izniyle ve yalnız istek satırları okunarak yapılmalıdır (karar metni §8 D8 bunu
bağımsız kod incelemecisine verir; açık kalır).

## B. Gerçek kip kapısı

1. **Giriş noktaları.** Modül yüklenince yalnız D-2 denetimi ve üç D-2 modülünün içe aktarılması olur (ağ yok, dosya
   açma yalnız depo içi). Ağ isteği ya da gerçek dalga formu/zarf açan bütün yollar kapıdan geçer: komut satırının
   `kos`, `baslat`, `marmara` komutları; `asama_kos`, `asama_manifest`, `asama_indirme`, `lp_adaylari_manifest`,
   `lp_indir`, `marmara_kos`; `GercekOrtam` (kurucu ve `zyol`, `hyol`, `istemci`); `GercekKaynak` (kurucu, `pencere`,
   `lp_adaylari`, `mda`, `b_prime_girdisi`); `k1c_kos` gerçek dizin, gerçek kaynak ya da `gercek=True` ile. Kendi
   sınamamda bu 22 giriş, **kurucuyu `object.__new__` ile atlayan çağrılar dahil**, denetim kancası altında
   `GERÇEK KİP REDDEDİLDİ` verdi; soket, `/mnt`, `kosu/` ya da alt süreç girişimi 0 (kapı grubu, 29/29). `kapi` ve
   `durum` komutları hiçbir şey açmaz. `dunya_kur`, `birimler_kur`, `negatif_sec` saf işlevlerdir (yalnız repo dosyası).
2. **Açılma şartları** (geçici kopyada sınandı): "Durum:" satırında `KOŞU DONDURULDU` + kod sha'ları metinde → açılır;
   yalnız "KARAR METNİ DONDURULDU" + sha'lar → açılmaz (KMS-1); TR-7 motoru değişirse → açılmaz (K-2). Kapı sahte açık
   kılındığında bile yapay düğmeler gerçek kipte reddedilir: yapay kaynak, yapay dizin, `mod_n ≠ 1000`.
3. **Gerçek I/O katmanı hiç koşmadı** (O-34). `asama_manifest`, `asama_indirme`, `lp_indir`, `GercekKaynak.pencere`
   TR-7 motorunu çağıran ince bir yapıştırıcıdır; satır satır okudum. Bulunanlar: K-1 (bu katmana veri sağlayan
   `birimler_kur`'da), K-3. Ayrıca okunup doğru bulunanlar: `GercekOrtam.yol`'un `tr7_*` → `tr7c_*` eşlemesi (TR-7
   motorunun okuduğu dosyaların hepsi `tr7c_` adlı ve `kosu/` altında; `kd_son` `tr7c_kd*` dosyasını `tr7_kd` önekiyle
   bulamaz ve `None` döner, manifestte `kd: None` yazılır, zararsız); lp zarfının ekseni `pencere_ekseni(p)` ile
   pencereninkiyle aynı; başvurunun W'si `eksen_dilim` ile başvuru istasyonunun kendi W'si (TR-7 §6.4 aynen). Yine de
   bu katmanın bir sahte sunucu (yerel FDSN taklidi ve yapay miniSEED) ile uçtan uca koşturulmadan dondurulması,
   kör koşunun ortasında bir çöküş ve "teknik çöküş" düzeltmesi riski taşır. **Öneri (dal değiştirmez):** koşu
   dondurmasından önce kodlayıcı `Istemci`'yi yerel bir taklitle değiştiren, 2 birim + 2 negatiflik bir kuru prova
   eklesin (TR-7'deki `kuru_prova` gibi); bu yapılmazsa §I'daki "teknik çöküş" cümlesi bağlayıcıdır.
4. **Aşama önkoşulu ve durma kaydı yok.** TR-7'nin `onkosul`'u (önceki aşama tamamlanmış mı, aşama ikinci kez mi,
   sürdürmede durma nedeni kayda geçmiş mi) TR-7c'nin `asama_kos`'unda yok; `--surdur` bayrağı okunuyor ama
   kullanılmıyor. Kilit yalnız hüküm dosyasındadır (bu yeterlidir: hüküm ikinci kez yazılamaz ve hesaplanamaz). Eksik
   olan, TR-7 §10.6'nın "durma nedeni kayda geçer" kuralıdır. Kod değiştirmedim (aşama protokolüne dokunur); §I'da
   ek cümle.

## C. Bağımsız sınamalar ve mutasyonlar (`tr7c_kodinc.py`, `tr7c_kodinc.json`)

**Sonuç: 74/74 geçti (K-1…K-3 sonrası kodda).** Gruplar: birim 32/32, kapı 29/29, uçtan uca 13/13.

Birim (seçme): U1 olay listeleri karar metninin tablolarından ayrıştırıldı; U2 D-2 sha'ları metinden ayrıştırıldı ve
içe aktarılan modüllerin dosyaları denetlendi; U3 K5 çağrı ağacı `sys.setprofile` ile; U4 Fisher scipy ile; U5 X_min
scipy beta/binom ile; U6 dal (126 060 nokta, metinden yazılmış başvuru); U7 K1b uçları; U8 "≥ yarı" toplaması; U8b K5'e pencerenin Q'su; U9 E-1
altı durum; U10 `modulasyon_kume` = `K.mod_p`; U11 `_rho`; U12 Q geometrisi (41 birim, gerçek koordinatlar, iasp91);
U13 Vanuatu birimi (K-1) ve 39 birimin dondurulmuş payı; U14 %50 sınırı; U15–U16 §7.3 tabloları; U15b güç satırı yalnız k_koşu < 10; U17 tohum ve eşikler.

Uçtan uca (bağımsız üreteç: log-normal gürültü, dar bantlı 15–30 sn Gauss başvuru hızı, fazına kilitli 2–8 Hz tremor;
41 birim, 12 negatif; mod_n 200):

| Senaryo | Sonuç |
|---|---|
| E1 gerçek tremor: 8/10 P kilitli, 1 N kilitsiz, negatif temiz | (b), X_P 8/10, X_N 1/29, f_PK 0/12, M_olc = M_mod = 8, "ölçü sınandı", VAR verilebilir; p'ler başvuruyla birebir |
| E1 modülasyon p'leri, kendi yazdığım başvuruyla (P+N T0 sırası, tek üreteç, `K.mod_p`) | birebir |
| E1 kilit: ikinci `k1c_kos` | hiçbir pencereye dokunmadı, aynı hüküm |
| E2 D-9 (Nias'ta kilitli tremor) + D-1 (Vanuatu'da tremor) + 1 negatif yanlış alarm | (b) + "genlik karıştırıcısı dışlanmadı", VAR yok; Vanuatu bir kez sayılır (n_N 29, X_N 3); f_PK 1/12, MDA yalnız 11 negatifte |
| E3 E-2: 5 P'de başvuru yok | (b), k_koşu 5, M_mod 3, "Parkfield modülasyonu geçmedi", güç bilgisi 0,61 / 0,24 |
| E4 8 P'de başvuru yok | (e) "modülasyon ölçülemedi" + D-8 eki |
| E5 bir P olayında iki algılama kümesi | (M, p) başvuruyla birebir ve aynı sırada (I′ başı) |

**Mutasyonlar: 31 / 31 yakalandı** (hepsi kodlayıcının 34'ünden farklı; liste json'da). Kapsanan konular: modülasyon üreteç sırası
(önce P sonra N; yalnız P; B de girer; küme sırası; kaydırma aralığı; p'nin +1'i), Fisher (katı kuyruk; n_P/n_N
yer değiştirir), N birimi birleştirme (USTVERI kaydı; birim T0'ı), E-1 (konum önceliği; alet kodu; tek yatay), k_koşu
(yalnız taranan; k = 10'da güç satırı; tablo kayması), kilit (iki katman birden), kapı (Durum'da "DONDURULDU" yeter;
K-2 yok; `zyol` kapısız; `pencere` kapısız), K5 (toplama "> yarı"; Q yerine boş aralık), %50 sınırı, f_PK'nın tanımı,
MDA'nın algılamalı negatifte koşması, A90 sınırı, K1b üst ucu, algılama sırası, GENLIK4 eksik olay, D-9'un P'yi de
taraması.

Dürüst not: ilk koşuda 31'in 27'si yakalandı. Yakalanmayan dördü sınamalarımın açığıydı, kodun kusuru değil: "küme sırası I′ sonu tersten" (E1'de her P olayında tek küme vardı; iki kilitli kümenin p'si 1/(n+1)'de eşit çıktığından p karşılaştırması da yetmedi → E5 iki kümeli olay ve M sırası eklendi), "D-1: birim T0'ı N 28'den" (→ U13 T0 sınaması), "E-2 güç satırı k = 10'da da" (→ U15b), "K5'e Q yerine boş aralık" (kalıntı kolu yapay pencerelerde tetiklenmiyordu → U8b, K5'e giden Q doğrudan denetlenir). Eklemelerden sonra 31/31. Kalan açık: U8b Q'nun K5'e iletildiğini denetler, K5'in kalıntı kolunun bir yapay pencerede gerçekten karar değiştirdiğini göstermez (o kol TR-7b §11.2 sınamalarına dayanır; KMS-9). Engellenen tek erişim, obspy içe aktarılırken kendiliğinden denenen `git rev-parse` alt sürecidir (zararsız; ağ ve /mnt/project-files girişimi 0).

## D. KMS-1…KMS-10: değerlendirme ve koşu dondurması ekine aynen girecek cümleler

Kural: karar metni değişmez; aşağıdaki cümleler yalnız belirsizliği kapatır, hiçbir eşiği gevşetmez. Her cümle
kodun bugünkü (K-1…K-3 sonrası) davranışını yazar; kod bu cümlelerle sınandı.

**KMS-1 (belirteç). Gerçek sorun:** §10 madde 5 "Durum: DONDURULDU …" der, bugünkü satır "KARAR METNİ DONDURULDU"
içerir; yalnız "DONDURULDU" arayan bir kapı yanlış açılırdı. Kodun okuması (ayrı belirteç) savunulabilir ve
serbestlik bırakmaz.
> "Koşu dondurmasının belirteci, metnin 'Durum:' satırında geçen 'KOŞU DONDURULDU' dizesidir; §10 madde 5'teki
> 'Durum: DONDURULDU …' bu dize olarak okunur. Koşu kodu gerçek kipte ancak şunların hepsi sağlanınca çalışır: bu dize
> 'Durum:' satırında; §0–§6 gövdesinin sha256'sı 8761573150be97dca99590283d7e3cecc3ddf0067804945966773f5276f69f18;
> `tr7c_kosu.py` ve `tr7c_mde_ek.py`'nin bu ekte yazılı sha256'ları; D-2'nin üç dosyası; repo girdileri
> (`tr7b_sayim.json`, `ustveri/tr7c_ustveri.json`, `tr7_parkfield_liste.csv`, `inc1/tr7c_inc1.json`,
> `tr7c_mde_ek.json`); TR-7 motoru `tr7_kosu.py` (ce439a4797fd1992ddd68de734ee842b146bd6f13155ba6151769bceb26a9005) ve
> `tr7_indir.py` (0763f46da14b2a12f5268937dc6e479dbfd1bc54c3c3ba93d700914dc4b91f2f)."

**KMS-2 (modülasyon üreteç sırası). Gerçek sorun:** §4.1 ve D-9 akışa hangi olayların, hangi sırayla gireceğini tam
söylemiyor; P kümelerinin p değerleri bu seçime bağlıdır (dağılımı değil). Sonuçtan sonra seçilirse sınırdaki bir p
(ör. 0,009 / 0,011) bu yolla oynatılabilir; bu yüzden ekte kapanmalıdır. Kodun seçimi (P ve 29 N iç içe, T0 sırası)
D-9'un "N olaylarıyla birlikte, T0 sırasıyla" cümlesinin en doğal okunuşudur ve §6.1'in "N olaylarındaki algılama
kümelerinin modülasyon p'leri" bilgi satırını da aynı akıştan verir. Savunulabilir.
> "Parkfield modülasyon ölçüsünün üreteci `default_rng(20261112 + 3)` tek bir örnektir ve 39 birimin (10 P olayı, 29 N
> birimi) algılama satırları yazıldıktan sonra bir kez kurulur. Algılama kümeleri (ayıklamadan sağ çıkan ve K1b
> aralığıyla kesişen kümeler) birimler T0 sırasıyla, P ve N iç içe (Vanuatu 2009 birimi N 27'nin T0'ıyla), birim içinde
> I′ başı ve eşitlikte I′ sonu sırasıyla işlenir. Bilgi birimleri (Kunlun 2001, Tonga 2006) ve rastgele negatif
> pencereler akışa girmez. Başvuru kanalı olmayan ya da M'si hesaplanamayan küme üreteçten sayı çekmez. Her küme 1000
> dairesel kaydırma kullanır; kaydırma `integers(120, |W_başvuru| − 120)`'dir (TR-7 §6.4). Bu sıra sonuç görüldükten
> sonra değiştirilmez."

**KMS-3 (modülasyonun zamanı). Kısmen sorun:** zaman p'yi değiştirmez, yalnız sıra değiştirir; KMS-2 cümlesi kapatır.
> "Modülasyon ölçüsü K1c-algılama aşamasında, 29 N biriminin ve 10 P olayının algılama satırları yazıldıktan sonra ve
> Z3/Z4'ten önce hesaplanır; ara sonuç dosyaya yazılmaz, yalnız hüküm dosyasında yer alır."

**KMS-4 (Q'nun bitişi). Gerçek ama etkisi küçük:** istasyon W başları birkaç saniye ayrışır (en kısa Q 189 sn, U12).
Seçim serbestliği sonucu fark edilir biçimde oynatamaz, yine de kapanmalı.
> "K5'in Q aralığı bir penceredeki bütün istasyonlar için aynıdır: Q = [⌊T0 + t_P⌋, Wb başı); t_P iz köşe
> ortalamasında (35,9125° K, 120,4625° B) iasp91 ile, ComCat tetikleyici kaydının derinliğinde en erken P fazıdır; Wb
> başı kullanılan (12 sınırından sonraki) istasyonların W başlarının en erkenidir. Maskeli ve kayıtsız saniyeler
> `_k1_kalinti`'nin kendi kuralıyla düşer. Rastgele negatif pencerelerde aynı tanım, kaydırılmış T0 ile kullanılır."

**KMS-5 (X_min ve K2). Gerçek sorun, okuma zorunlu:** K2 (f ≤ ⌊0,05 N⌋) uygulansaydı Z3 (ii)'nin 0,30 tavanı anlamsız
kalır ve §7 güç tablolarının hiçbiri geçerli olmazdı. Kodun okuması tek tutarlı okumadır; serbestlik bırakmaz.
> "Z3 (i)'deki X_min(n_P, f_PK), TR-7 §8'in binom tanımıdır: p_üst = f_PK/N_PK'nin Clopper–Pearson tek yanlı %95 üst
> sınırı, X_min = P(Bin(n_P, p_üst) ≥ X) ≤ 0,05 olan en küçük X ∈ [2, n_P]; yoksa (i) sağlanmaz. TR-7'nin Marmara
> tarafındaki K2 kapısı K1c'de uygulanmaz; K1c'nin FAR şartı Z3 (ii)'dir. Bu, INCELEME-1 güç ızgarasının ve §7
> tablolarının tanımıdır."

**KMS-6 (D-9'da "ölçülemeyen"). Küçük sorun:** sayı yalnız bilgidir, etiketi tetiklemez; sonuçtan sonra oynatılacak
bir şey yok.
> "D-9'daki 'modülasyonu ölçülemeyen olay', dört olaydan §5 madde 4'ün ölçülebilirlik tanımını sağlamayanlardır:
> taranmayan, K1b ile kesişen ve ayıklamadan sağ çıkan kümesi olmayan, E-1 başvuru kanalı olmayan ya da M'si
> hesaplanamayan olay. Sayı K1c satırına, her olayın nedeni hüküm dosyasına yazılır. Ne sayı ne neden etiketi ya da dalı
> değiştirir; etiketi yalnız p ≤ 0,01 veren bir küme tetikler."

**KMS-7 (N 27/N 28 ayrı bilgi satırı). Gerçek sorun:** ayrı K1b, W ve E1 tanımı dondurulmadı; sonuçtan sonra
tanımlanırsa bilgi satırı seçilmiş olur. Hesaplamamak tutucudur.
> "D-1'in bilgi satırı ('iki olay ayrı sayılarak hesaplanan Z3 (iii)') bu koşuda hesaplanmaz, çünkü N 27 ve N 28 için
> ayrı K1b, W ve E1 tanımı koşudan önce dondurulmadı; sonuç raporunda 'hesaplanmadı (ayrı pencere tanımı yok)' diye
> anılır ve sonradan hesaplanmaz. Dal değişmez."

**KMS-8 (uygulama hatası yolu). Gerçek sorun:** §6.1 yolu tutar ama yordamı yazılı değil; kod yolu yazmadı, kilit
ikinci hükmü engeller. Yolun sonuçtan sonra serbestçe kurulması en büyük serbestliktir; kapatılmalı.
> "TR-7 §7.2'nin uygulama hatası yolu bu koşu kodunda yazılmadı. K1c (d) ya da (e) dalından sonra bir uygulama hatası
> bulunursa ilk hüküm dosyası silinmez ve üzerine yazılmaz; düzeltme ayrı bir bağımsız kod incelemesinden geçer;
> ikinci hüküm ayrı adla (`tr7c_k1c_hukum_2.json`) bir kez yazılır ve iki hüküm birlikte yayımlanır. Yol bir kez
> kullanılır; (a), (b) ve (c) dallarında yoktur. Tanım, eşik, pencere, liste, sızıntı kuralı, üreteç sırası ve
> E-2'nin örtü eksikliği 'uygulama hatası' sayılmaz."

**KMS-9 (KD'de Q). Gerçek ama zorunlu okuma:** KD pencerelerinde tetikleyici yok. Q = ∅ okuması tek olanaklı okumadır;
yalnız KD'nin K5'in kalıntı kolunu sınamadığı açıkça yazılmalı.
> "§10 adım 2'deki 'TR-7'nin KD'si K5 ile', KD pencerelerinde tetikleyici olmadığı için Q = ∅ ile koşulur; K5'in
> kalıntı kolu orada çalışmaz, yalnız ρ kolu çalışır. K5'in Q doğrulu kalıntı kolu TR-7b §11.2 satırlarıyla (iki tohum,
> 38/38 Tur 2 ile birebir) sınanmış sayılır. KD satırları bu koşu kodunun `ayikla_k5`'iyle tam ölçekte koşuldu
> (`kodinc/tr7c_kodinc_kd.json`)."

**KMS-10 (kuyu sınıfı bilgi satırı). Gerçek sorun:** Z4 bu bilgi satırını sayar ama pencere ve indirme tanımı yok.
> "Z4'ün 'liste sınıfına karşı kuyu sınıfı' bilgi satırı bu koşuda hesaplanmaz: kuyu sınıfı için pencere, indirme ve
> kod koşudan önce dondurulmadı. Sonuç raporunda 'hesaplanmadı' diye anılır. Hesaplanacaksa yalnız K1c hüküm dosyası
> yazıldıktan sonra, ayrı incelenmiş kodla ve yalnız bilgi olarak yapılır; hiçbir dalı ya da etiketi değiştirmez."

## E. KD: kısaltılmış koşu yeterli mi; tam ölçek

**Yetersizdi.** Kodlayıcı 0,25 ölçekle (25 pencere/tohum) yalnız D7, D7b, D7c, D7d, D15'i koştu. TR-6a dersi gereği
yöntem sınaması dondurmadan önce tam ölçekte koşulmalıdır; 25 pencerede "atılma ≤ 0,03" bandı tek atılmayla kalır,
yani bant pratikte "0/25" demektir ve Monte Carlo payı bandın kendisinden büyüktür. Ayrıca D2/D3 (algılama eşiği) ve
D13/D14 (MDA) satırları da ayıklama kuralına bağlıdır (`r['algilama']` ve MDA'nın kendi algılaması); bunlar hiç
koşulmadı.

Tam ölçek süresi (ölçüm): kodlayıcının 5 satırı 0,25'te 3101 sn → tam ölçek ≈ 12 400 çekirdek-sn ≈ 1,7 sa
(2 çekirdekte). D2 ≈ 9 sn/pencere, D3 ≈ 26 sn/pencere (ölçüldü) → D2/D3 tam ölçek ≈ 2,5 sa; D13/D14 TR-7'de KD'nin en
pahalı satırlarıdır. Hepsi birlikte 2 saati aşıyor. Bu yüzden:
1. **Kodlayıcının 5 satırı tam ölçekte (olcek 1,0; 100 pencere/tohum, iki tohum, 24 iş) koşuldu**, 2 çekirdekte iki
   parça, ara sonuç her işten sonra jsonl'e: **12/12 bant geçti, eksik iş 0, engellenen erişim 0** (24 iş, 12 872 çekirdek-sn ≈ 3,6 çekirdek-sa; iki parça 1 sa 48 dk'da bir kez durdurulup ara jsonl'den sürdürüldü). Bütün satırlarda K5'in tam ölçek değerleri TR-7'nin K0 tam ölçek değerleriyle (tr7_kd.json) **birebir aynıdır** (D7 0/0, D7b 0/0 üç genlikte, D7c 0/0 dört durumda, D7d 1,0/1,0, D15 (a)/(b) atılma 1,0). Kodlayıcının 0,25 ölçekli bilgi sütunları (yanlis_on, yanlis_inc1_I) tam ölçekte biraz farklıdır (ör. D7b 3 sn yanlis_on 0,071/0,111; 0,25'te 0,04/0,042); bunlar bant değildir. Sonuç: kısaltılmış koşunun hükmü (K5, K0'ın KD davranışını bozmaz) tam ölçekte doğrulandı; dosya `kodinc/tr7c_kodinc_kd.json`.
2. **D2, D3, D12, D13, D14 için bayrak ayrışma sayımı:** bu satırlarda K5'in K0'dan farklı karar verdiği küme sayısı
   küçük ölçekte sayıldı (`--say`). Ölçek 0,05 (D2 20, D3 10, D12 10, D13 10, D14 15 pencere/tohum; 725 sn): **1268 kümenin 0'ında K5 ile K0 ayrıştı**; iki kural da hiçbir kümede sızıntı bayrağı kaldırmadı (D2 180, D3 103, D12 20, D13 90, D14 875 küme). Ayıklamanın öteki kolları (darbe, taban, 3a) ortak olduğundan, bu satırların K5'li değerleri bu ölçekte K0'lı değerlerle aynıdır; tam ölçekte yeniden koşmak (tahmin ≥ 3 sa) bu yüzden gerekli görülmedi. Sınır: 0,05 ölçek nadir ayrışmaları (≲ 1/1268) dışlamaz; bu satırların bantları K5'e değil algılayıcıya bağlıdır. Dosya `kodinc/tr7c_kodinc_kd_say.json`.

## F. Duman sınaması ve m_t (bilgi satırı; dal değişmez, Z7)

Duman sonucu: Tohoku'da K5'ten sağ çıkan 3 W kümesi ve saf P kümesi; hiçbirinde p ≤ 0,01 yok (W kümelerinde p 0,18,
0,083, 0,18; atılan dördüncü 0,22; saf P 0,28). Bu tek olaylık bir gözlemdir; kümelerin tremor olduğu doğrulanmadı ve
kümeler bağımsız değildir. Yine de m_t'nin üst ucu hakkında bir şey söyler: üç kümeyi bağımsız gerçek tremor kümesi
sayarsak hiçbirinin geçmeme olasılığı m_t 0,8'de 0,2³ = 0,008, m_t 0,5'te 0,125, m_t 0,3'te 0,34'tür. Aynı modelle
(`tr7c_inc1.py` `sabit_model`/`p_d30m3`, n_P 10, n_N 29, q 0,1) gücün m_t'ye bağlılığı:

| m_t | görülebilir en küçük s (güç 0,80) | güç, s 0,7 | güç, s 1,0 |
|---|---|---|---|
| 0,8 | 0,58 | 0,94 | 1,00 |
| 0,5 | 0,77 | 0,73 | 0,95 |
| 0,4 | 0,96 | 0,56 | 0,83 |
| 0,3 | yok (s = 1'de bile < 0,80) | 0,35 | 0,62 |
| 0,2 | yok | 0,16 | 0,32 |

Koşu dondurması ekine bilgi satırı olarak önerilen cümle (aynen):
> "Bilgi (dal değiştirmez; Z7, D-3): Tohoku duman sınamasında K5'ten sağ çıkan 3 W kümesinin hiçbiri modülasyonda
> p ≤ 0,01 vermedi (en küçük p 0,083). Tek olaylık, tremor olduğu doğrulanmamış bu gözlem m_t'yi ölçmez, ama m_t 0,8
> varsayımını desteklemez (üç bağımsız kümede hiç geçmeme olasılığı m_t 0,8'de 0,008, m_t 0,5'te 0,13). Kör koşunun
> gücü bu yüzden m_t 0,5 sütunuyla okunmalıdır: görülebilir en küçük s ≈ 0,77; m_t 0,4'te ≈ 0,96; m_t ≤ 0,3'te s = 1
> bile 0,80 güç vermez. 'Ölçü sınanamadı (… kalan: (iv))' sonucu öncelikle modülasyon ölçüsünün gerçek tremorda düşük
> geçme olasılığının işareti olarak okunur; Parkfield'da tetiklenmiş tremorun yokluğu ya da algılayıcının tremoru
> görmediği diye okunmaz."

## G. İndirme planı ve kör pencere kuralları

İstek tanımları (okuma ve repo-içi hesap, ağ yok):
- Dalga formu istekleri yalnız `istek_tanimi` ile, istasyon başına [R başı − 600 sn, W sonu + 600 sn] aralığında
  kurulur (TR-7 §3.5; 600 sn dolgu Hilbert kenarı içindir). Bu aralık R, Q (T0 + t_P … W başı) ve W'yi kapsar; Q
  K5'in tanımı gereği gereklidir. Vanuatu biriminde aralık N 27'nin R başından N 28'in W sonuna kadardır (D-1).
- Her istek `dataselect_url` → `sinir` ile denetlenir (bitiş < 2026-01-01; katalog ≤ 2025-12-31); `dunya_kur` ayrıca
  her pencerenin W sonu + dolgusunu denetler. Kör olayların hepsi 2001–2010; negatifler ±60 gün → en geç 2010-08.
- Rastgele negatifler TR-7 §7.3 kuralıyla seçilir; kaydırılmış [R başı − 3 sa, W sonu] aralığında M ≥ 6,5 olmaması
  şartı, bütün kör olaylar M ≥ 7,5 olduğu için, bir negatifin başka bir kör olayın W'siyle örtüşmesini dışlar
  (bir kör olayın W sonu T0'dan en çok ≈ 1,6 sa sonradır < 3 sa). Bir negatif bir kör olayın R'si (olay öncesi gürültü)
  ile örtüşebilir; bu aynı tek koşunun içindedir ve körlüğü bozmaz.
- Marmara: hiçbir istek kurulmaz; `marmara_kos` kapıdan, hüküm dosyasından ve dal (b)'den sonra bile durur (O-30).
- Tetikleyici ComCat istekleri ±60 sn; M ≥ 6,5 negatif katalog istekleri [R − 61 g − 3 sa, W + 61 g]; StationXML
  istekleri yalnız üstveri.
- **Hacim düzeltmesi.** O-6 ve §9'daki "pencere başına bütün liste istasyonları, ≈ 7300 istek" kestirimi TR-7 motorunu
  yanlış okur: `indirme_plani` her pencerede iz sırasıyla ilk 12 istasyonu (tetikleyici pencerelerinde ayrıca PGV'ye
  uygun istasyonları) ister ve `pencere_indir` 12 istasyon örtüden geçince o pencerede durur; düşen istasyonun yerine
  sıradaki istenir. Repo-içi sayım (`dunya_kur`): tetikleyici birimlerde liste istasyonu 34–52 (toplam 1882),
  negatiflerde 12 olay × 10 × (38–51) = 5440. Gerçek istek sayısı bu yüzden ≈ 41 × (12…~20) + 120 × (12…~16) ≈
  2000–2800 (+ E-1 için ≈ 40–80), hacim ≈ 2–4 GB, süre (TR-7'nin 2–3 sn/istek ölçüsüyle) indirme ≈ 1,5–2,5 sa + MDA
  ≈ 6–7 sa. 7300 istek / 7–10 GB / 11–14 sa üst sınırdır (tutucu); plan bunu aşmaz.
- Sonuç: istek tanımları kör pencere kurallarına uyuyor (yalnız tanımlı W/R pencereleri ve aradaki Q, ≤ 2025, Marmara
  yalnız dal (b) sonrası ve bu kodda hiç).

## H. Kodlayıcının sınamalarının yeni kodda yeniden koşusu ve son sha256'lar

Kodlayıcının `tr7c_test_yapay.py`'si değiştirilmeden K-1…K-3 sonrası kodda yeniden koşuldu: **sınamalar 100/100** (birim 49, kapı 27, sha/kilit 9, uçtan uca 15), **mutasyonlar 34/34 yakalandı**; mutasyon dizelerinin hepsi yeni kodda uygulanabildi (`kodinc/tr7c_kodlayici_test_yeniden.json`). İncelemecinin takımı: 74/74, 31/31 (`kodinc/tr7c_kodinc.json`). Koşu dondurması eki `tr7c_kosu.py` için aşağıdaki sha256'yı yazmalıdır (kodlayıcının 345dc176… değeri artık geçersizdir).

| Dosya | sha256 |
|---|---|
| `kayit/turetme/tr7c/tr7c_kosu.py (K-1…K-3 sonrası)` | b0f706423894a0d73b4edd26dcedc7dfeb2441b7a3821c70b365aa4594674a1a |
| `kayit/turetme/tr7c/tr7c_kd_k5.py (değişmedi)` | 77aeab9951972d7cc2580bd8e6fab95f8dc96dfa67218c8aea998b2076fc2a64 |
| `kayit/turetme/tr7c/tr7c_test_yapay.py (değişmedi)` | 6267a5b53b0405e0e2c3d4c2f24771a97b9477548e4327b00ac09e26be82fd9f |
| `kayit/turetme/tr7/tr7_kosu.py (K-2 ile denetlenir)` | ce439a4797fd1992ddd68de734ee842b146bd6f13155ba6151769bceb26a9005 |
| `kayit/turetme/tr7/tr7_indir.py (K-2 ile denetlenir)` | 0763f46da14b2a12f5268937dc6e479dbfd1bc54c3c3ba93d700914dc4b91f2f |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc.py` | 03e479639222ba184a0dcd1b51a046ac2990da266fb35235378eb8ba31e31c06 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc_kd.py` | ae3feb2f40314926642c1b81469256a1c02ea6d6026b60dd0160853294537d63 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc.json` | 9c891ec156d10c662f3e00e88bd1101383fb9de8949f04d6102c2d23bd56b498 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc_kd.json` | abd774cbcbe790b128cb2c0c3713e42095851a850db485349b73b83eca05ce99 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodinc_kd_say.json` | 5de5611b247645d73bc7540d49af7d0d6fca4c45351e5fdbb0323c3f8c8a3881 |
| `kayit/turetme/tr7c/kodinc/tr7c_kodlayici_test_yeniden.json` | 6ea61e62501184983e885359170d2d6359bd5a8f92a899dffb097517ce3bec38 |

## I. Koşu dondurması ekine ek cümleler (bu incelemenin bulgularından; aynen)

1. (A23) "Durum dosyası `kayit/turetme/tr7c/kosu/TR7C_KOSU_DURUM.json`'dur; §10 madde 6'daki
   `kayit/turetme/tr7c/TR7C_KOSU_DURUM.json` bu yol olarak okunur. Durum dosyası yalnız 'başladı / tamamlandı / hata',
   zaman ve dosya sha256'larını taşır."
2. (§B.4) "Bir aşama kesilirse sürdürmeden önce durma nedeni (teknik çöküşün ileti metni ve saat) durum dosyasına
   elle ve commit ile yazılır; jsonl satırları ve üreteç durumu kaldığı yerden sürer. K1c-algılama aşamasından sonra
   koşu yalnız teknik çöküşle durur. Teknik çöküşü gidermek için yapılan kod değişikliği yalnız okuma/ayrıştırma
   katmanına dokunabilir, `TR-7c_KOD-INCELEME` biçiminde ayrıca incelenir ve sha256'sı deftere yazılır."
3. (A25) "Kunlun 2001 ve Tonga 2006 bilgi satırları E1 maskesi olmadan hesaplanır (USTVERI'de bu iki olayın E1 satırı
   yoktur); yalnız bilgi olarak yazılır ve hiçbir dalı ya da etiketi değiştirmez."
4. (Ö-i) "`_rho` eşit L değerlerine ortalama sıra yerine konum sırası verir; bu K5'in D-2 ile dondurulmuş davranışıdır
   ve değiştirilmez. Sürekli L'de Spearman ile farkı yoktur."
5. (§G) "İndirme planı TR-7 motorunun 12-istasyon kuralıyladır; istek sayısı ≈ 2000–2800 + E-1 istekleri
   kestirilir; koşu kodu kör olaylarda W, R ve aradaki Q dışında ve 2026 ve sonrasında hiçbir dalga formu istemez."

## J. Olay kaydı

Bu incelemede gerçek veriye istenmeden dokunulmadı. Denetim kancası bütün süreçlerde açıktı; tek reddedilen girişim
obspy'nin içe aktarılırken çalıştırdığı `git rev-parse` (site-packages) idi. Kapının açık hâli yalnız geçici kopya
dosyayla ve `kosu_dondurulmus_mu` düzeyinde sınandı; açıkken hiçbir gerçek yol çağrılmadı.
