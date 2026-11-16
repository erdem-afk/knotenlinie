# TR-13b ön kayıt: bağımsız inceleme 2

İncelenen: `TR-13b_sinirli-kosu_ONKAYIT.md` (TASLAK sürüm 2), `kayit/turetme/tr13b/tr13b_v2_mde.py/.json`; karşılaştırma
için sürüm 1, `TR-13b_INCELEME-1.md` (Z1–Z5), `TR-13_SAYIM.md`, `ESIK-DAYANAGI.md`. Taslak ve yazarın betikleri
değiştirilmedi. Gerçek katalogda hiçbir V(q) ya da z hesaplanmadı, katalog indirilmedi, ham arşiv açılmadı. Tek gerçek
girdi `tr13_tamsayim.json`'daki üstveri satırlarıdır (sürüm 2'nin `liste()` işleviyle aynen).

Bağımsız betik: `kayit/turetme/tr13b/inc2/tr13b_inc2.py` (`python3 -I -B`, numpy, tohum 20261122, ≈ 9 dk) →
`tr13b_inc2.json`. Üreteç, GK74 ve z ölçüsü `tr13_guc.py`'den; sınama düzeni, kalibrasyon ve kural karşılaştırması
bağımsız yazıldı. Listenin gerçek bileşimi (15 üye, 13 küme, keşif dışı 10), sıfır dallanma 0,4/0,6/0,8 (üye başına
≈ 340 bölge), veri: D0 sinyalsiz, D1 durağan sürüler, D4 yalnız önce-pencerede kenar ağ kaybı (üye başına ≈ 210),
sinyal f = 0,2–0,6 (üye başına ≈ 125). Sürüm 2'den iki farkı: (i) μ her üyenin **kendi R'sinde** kalibre edilir
(aşağıda K1); (ii) D4'ün kenarı 0,375 R (R = 80'de INCELEME-1'in 30 km'si).

## Hüküm

**DÜZELTMEYLE KABUL.** Z1–Z4 doğru uygulanmış. Z5 yazıldığı gibi uygulanmış ama işe yaramıyor: plasebo denetimi
sürü ve ağ bozulmalarını **seçmiyor**, bütün "VAR"ları (sinyalsiz, bozulmalı, gerçek sinyalli) aşağı yukarı aynı oranda
kesiyor; p > 0,20 düzeyinde ise kuralın gücüne ≈ 0,75'lik bir **tavan** koyuyor, bu yüzden "MDE > 0,5" bir etki
büyüklüğü değil, tasarımın güç 0,8'e hiç ulaşamamasıdır. §9.4 kararı: **plasebo bilgi satırı olur, hükmü bağlamaz.**
Bu kural (üç dallanma × bütün liste ve keşif dışı) bileşimde yanlış alarmı sinyalsizde 0,020, sürüde 0,053, kenar ağ
kaybında 0,025 tutuyor; MDE **f ≈ 0,40**. Sürüm 2'nin "bilgi satırı olursa yanlış alarm 0,08–0,09" önermesi yanlış
kurala aitti (tek dallanmalı T1, K = 14, türdeş R 80); tam "VAR" kuralının üç dallanma ve iki liste birlikteliği zaten
tutucudur. Ayrıca bir kalibrasyon hatası (K1), tanımsız bir geçersizlik ölçütü (K2) ve donmamış koşu kodu/tohum (K3)
dondurmadan önce düzeltilmeli.

## A. Z1–Z5 uygulandı mı

| Madde | Durum | Not |
|---|---|---|
| Z1 keşif kümeleri | **doğru** | `KESIF = {397, 979, 395}`; K_kd = 10; "VAR" iki listede de ister; cümlenin öznesi keşif dışı satır. Ishigaki'nin ortak Mc ile düşmesi doğru hesaplanmış (58 × 10^−0,2 = 36,6). |
| Z2 gerçek bileşimle MDE | **doğru, bir hatayla** | R 58–426 ve doyma sonrası N kullanılıyor. Ama `_is_A` μ'yü `M.kalibre` ile **R = 80'de** kalibre edip üyeyi kendi R'sinde benzetiyor (K1). Etki MDE'de küçük (0,391 → 0,399), ama aynı işlev koşuda kullanılırsa sıfır havuzu yanlış N'li olur. |
| Z3 çok olaylı küme | **doğru** | `kume_ort` ve `karar` üyeleri kendi havuzlarından ayrı çekip ortalıyor. Eksik: bir üye düşerse kümenin tek üyeyle sürdüğü yazılı değil (D-3). |
| Z4 dallanma | **doğru** | Üç havuz, "üçünde de", uydurma yok. |
| Z5 plasebo denetimi | **yazıldığı gibi uygulandı, ama işlevsiz** | §B. Ayrıca INCELEME-1 plasebo için ayrı, plasebo penceresinin kendi N'siyle kalibre havuz demişti; sürüm 2 olayın havuzundaki z_p'yi kullanıyor. Bilgi satırı olunca bu fark önemsizleşir; yine de raporda plasebo penceresinin N'si yazılmalı. |
| Ö1–Ö4 | doğru | Ö4'te "≥ 2000" serbestlik bırakıyor (K3). |

**Sürüm 2'de doğan yeni serbestlikler / kusurlar:**

- **K1 (kalibrasyon R'si).** `tr13b_mde.kalibre` `bolge(..., B_ref=2)` çağırır, R'yi geçirmez (varsayılan 80).
  Kendi R'sinde ölçtüğüm: R = 80'de kalibre edilen μ büyük R'li üyelerde önce-pencere arka planını hedefin
  ≈ %8–27 üstünde, küçük R'lilerde (Cook Boğazı, Jan Mayen) %10–15 altında veriyor (`tr13b_inc2.json`,
  `kalibrasyon`: oran 0,79–1,18). Koşuda sıfır havuzu gerçek N3bg'den sapmış olur → kalibrasyon uyuşmazlığı, ki
  INCELEME-1 D'de α'yı en çok bozan şeydi.
- **K2 (dal 2 tanımsız).** "f = 0,3'te ortalama z `tr13b_v2_mde.json` beklentisinin ±%25'i" — o dosyada ortalama z
  yok, yalnız red oranları var. Ölçüt şu haliyle sonradan seçilebilir.
- **K3 (koşu kodu ve tohum donmamış).** Gerçek z'yi hesaplayacak betik yok; sıfır havuzlarının tohumu yazılı değil;
  havuz "≥ 2000". Bu üçü birlikte "tohumu değiştirip yeniden koş" serbestliği bırakır.
- **K4 (dal 1, K < 8).** Keşif dışı K 8 ya da 9'a inerse koşu sürer; MDE yeniden hesaplanacağı için kabul edilebilir,
  ama cümlede o K'nin MDE'si kullanılmalı (taslak zaten öyle diyor).
- **K5 (MDE'nin koşudan önce yeniden hesabı).** Doğru fikir, ama hangi betik ve tohumla yapılacağı yazılmalı;
  yeniden hesap hüküm kuralını değiştiremez, yalnız cümledeki sayıyı.

## B. §9.4: plasebo denetimi bağlasın mı

Bileşimde, kendi R'sinde kalibrasyonla (`tr13b_inc2.json`, `kurallar`; Monte Carlo hatası red oranlarında ≈ ±0,01–0,015,
güçte ≈ ±0,03):

| Kural | D0 sinyalsiz | D1 sürü | D4 kenar ağ | f 0,2 | 0,3 | 0,4 | 0,5 | 0,6 | MDE f |
|---|---|---|---|---|---|---|---|---|---|
| T1 tek dallanma 0,6, bütün liste (karşılaştırma) | 0,051 | **0,126** | 0,067 | 0,48 | 0,72 | 0,93 | 0,96 | 0,99 | 0,34 |
| **R0** üç dallanma × (bütün liste ve keşif dışı) | **0,020** | **0,053** | **0,025** | 0,30 | 0,52 | 0,80 | 0,90 | 0,97 | **0,40** |
| R1 R0 + plasebo p > 0,20 (sürüm 2 tam kuralı) | 0,014 | 0,035 | 0,018 | 0,25 | 0,43 | 0,68 | 0,72 | **0,75** | **yok** |
| R1b R0 + plasebo p > 0,05 | 0,018 | 0,047 | 0,022 | 0,29 | 0,50 | 0,78 | 0,85 | 0,90 | 0,43 |
| R3 R0, eşik en kötü bozulmaya göre (a = 0,048) | 0,019 | 0,050 | 0,023 | 0,29 | 0,51 | 0,80 | 0,89 | 0,97 | 0,40 |
| R4 fark z − z_p ile T1 (bilgi) | 0,028 | 0,029 | 0,030 | 0,15 | 0,22 | 0,42 | 0,51 | 0,66 | > 0,6 |

Plasebonun seçiciliği (R0'ın "VAR" dediği çekilişlerde plasebo p ≤ 0,20 olanların payı, `plasebo_seciciligi`):
D0 **0,30**, D1 **0,34**, D4 **0,28**, sinyal f 0,2–0,6 **0,16–0,23**. Ortalama kaymalar (D0'a göre): D1'de z −0,17,
z_p −0,15; D4'te z −0,09, z_p −0,06.

Okuma:
1. **Tavan.** Sinyal plasebo penceresine düşmez; plasebo sinyal altında da sinyalsizdeki gibi davranır. p > 0,20
   kapısı her durumda çekilişlerin ≈ %20–25'ini atar, güç ≈ 0,75'i geçemez. "MDE > 0,5" sayısı bu tavanın ürünüdür;
   f ne kadar büyük olursa olsun güç 0,8'e varmaz. Sürüm 2'nin kendi tablosu da bunu gösteriyor (f 0,5'te 0,91 → 0,70).
2. **Seçicilik yok.** Plasebo, sürü altındaki sahte "VAR"ı (0,34) sinyalsizdekinden (0,30) ancak biraz daha çok
   kesiyor; kenar ağ kaybını hiç seçmiyor (yalnız önce-pencerede olan bir bozulmayı tanımı gereği göremez). Sürüm 2
   §6'daki "%30 azaltıyor" doğru ama yanıltıcı: D0'ı da, gücü de %30 azaltıyor. Bu, α'yı sıkılaştırmanın pahalı bir
   eşdeğeridir. Nedeni: D1 hem olay hem plasebo penceresini aynı ölçüde iter (−0,17 / −0,15), ama K = 13'te küme
   ortalamasının sd'si ≈ 0,4; −0,15'lik kayma ayırt edilemez.
3. **Asıl koruma zaten R0'da.** Üç dallanma ve iki liste birlikte istendiğinde sinyalsizde gerçek α 0,020 (anma 0,05);
   bu pay sürü bozulmasını ≈ 0,05'e kadar karşılıyor. §9.4'teki "0,08–0,09" tek dallanmalı T1'in (K 14, R 80) sayısıydı,
   tam kuralın değil.
4. **Üçüncü yollar.** (a) "Aday" etiketi: "VAR"ın kendisi için R1'in tavanını taşır, "VAR + aday" için R0'dır; seçicilik
   olmadığından etiket bilgi taşımaz. (b) En kötü bozulmaya göre kalibre eşik (R3): a = 0,048 çıktı, yani R0 zaten
   sınırda; ayrıca bozulma yoğunlukları (yılda 0,4 sürü, %30 görünürlük) bizim seçimimiz, gerçek sıklıkları ölçülmedi;
   eşiği onlara bağlamak yeni bir serbestlik olur. (c) p > 0,05 kapısı (R1b): MDE'yi 0,03 büyütüp D1'i 0,006 düşürüyor.
   (d) Fark istatistiği (R4): bozulmaya dayanıklı ama gücü yarıya iniyor. Hiçbiri R0'dan iyi değil.

**Karar: R0 bağlar; plasebo bilgi satırıdır; plasebo zayıfsa "VAR" cümlesine zorunlu bir uyarı eklenir (hüküm
değişmez).** Seçilen kuralın sayıları (bileşim, kendi R'de kalibrasyon): yanlış alarm D0 0,020 / D1 0,053 / D4 0,025;
güç f 0,3'te 0,52, 0,4'te 0,80, 0,5'te 0,90; **MDE f ≈ 0,40 (± 0,03)**; ×0,5 (f 0,2) güç 0,30; ×2 benzetim aralığının
dışında (f 0,6'da 0,97).

Kesin ön kayıt cümleleri (§3.8, §7.3, §7.4, §9.4 yerine):

> **§3.8.** Plasebo T1 (z̄_p, dallanma 0,6 sıfırı, bütün liste) hesaplanır ve p_plasebo raporda yazılır; plasebo
> penceresinin arka plan sayısı da yazılır. p_plasebo hükmü değiştirmez.
>
> **§7.3.** Büyük etki VAR: üç dallanmanın üçünde de bütün listede p ≤ 0,05 **ve** üçünde de keşif dışı listede
> p ≤ 0,05. Cümle: "BZ20'nin keşif olayları dışındaki K = … bölgede, ana şoktan önceki 3 yılda kümesizleştirilmiş arka
> plan, ETAS'ın ürettiğinden belirgin biçimde yerelleşmiş. Tahmin ya da alarm iddiası değildir; ileriye dönük sınav ayrı
> ön kayıt ister." p_plasebo ≤ 0,05 ise cümleye eklenir: "Aynı bölgelerin 3 yıl önceki penceresi de ETAS'a göre
> yerelleşmiş görünüyor (p = …); sonuç ETAS dışı durağan bir bozulmadan ayrılamıyor."
>
> **§7.4.** (Kaldırılır; "ETAS uyumsuzluğu" dalı yoktur.)
>
> **§9.4.** Plasebo denetimi yapay sınamada seçici değil (INCELEME-2 §B) ve p > 0,20 kapısı güce ≈ 0,75 tavan koyuyor;
> bu yüzden bilgi satırıdır. ETAS dışı bozulmalara karşı koruma, üç dallanma × iki liste birlikteliğinin tutuculuğudur:
> yapayda yanlış alarm sinyalsiz 0,020, durağan sürüde 0,053, kenar ağ kaybında 0,025. Bozulma yoğunlukları seçimdir;
> gerçek sıklıkları ölçülmedi. Kalan risk budur.

## C. Değer hükmü

- f ≈ 0,40, önce-penceredeki arka planın **ortalama** %40'ının 2 km'lik kırık bandına toplanması, R 80'lik bölgede bant
  payının ≈ %8'den ≈ %18'e (≈ 2,2 kat) çıkması demek; R 280–430 km'lik bölgelerde bu daha da aşırı bir yoğunlaşmadır.
  BZ20'nin bildirdiği büyüklük okunamadığı için bunun "kuramın kaç katı" olduğu bilinmiyor. Dürüst okuma: sınav yalnız
  çok büyük, örneklemin geneline yayılmış bir yerelleşmeyi görür. Birkaç bölgede güçlü, ötekilerde olmayan bir etki
  (heterojen etki) ortalama z'de kaybolabilir.
- En olası sonuç "ayırt edilemez (MDE f ≈ 0,40)"dır ve bu önceden kabul edilmeli. Bu sonuç TR-13'ün durumunu "güç yok"tan
  "büyük ve yaygın etki de görülmedi"ye taşır; BZ20 hakkında hüküm değildir. Bir "VAR" ise şaşırtıcı ve değerli olur,
  ama yalnız ileriye dönük sınava aday gösterir.
- Koşmaya değer mi: evet, maliyet ≈ 0 ve iki sonucun anlamı önceden yazılı. Ama beklenen bilgi kazancı küçüktür;
  bu açıkça §0'da söylenmeli.
- §8 ("söyler / söylemez") yapı olarak doğru, ama (i) "yarısından fazlası / ≳ 2,5 kat" sayıları R1'in tavanına
  dayanıyor ve yeni kurala göre "≈ %40'ı / ≈ 2,2 kat (R 80'de)" olmalı; (ii) "ortalama etki; birkaç bölgeye sınırlı
  yerelleşme hakkında bilgi yok" eklenmeli; (iii) "bu sonuç BZ20'yi ne doğrular ne çürütür" tek cümle olarak yazılmalı.

## D. Zorunlu düzeltmeler (dondurmadan önce)

1. **D-1 (§9.4 kararı).** §3.8, §7.3, §7.4, §9.4 yukarıdaki kesin cümlelerle değiştirilir. §0, §4, §5 ve §7.5'teki
   "MDE > 0,5" yerine "f ≈ 0,40 (bileşim, kendi R'de kalibrasyon; INCELEME-2)" yazılır; §5 tablosuna bu incelemenin
   R0 satırı eklenir; §6'ya "denetim seçici değil: R0 reddi içinde plasebonun kestiği pay D0 0,30, D1 0,34, D4 0,28,
   sinyal 0,16–0,23" eklenir.
2. **D-2 (K1, kalibrasyon R'si).** "Sıfır havuzunun μ'sü her olayın kendi R'sinde, önce-pencere GK74 arka plan
   sayısı gerçek N3bg'ye eşit olacak biçimde kalibre edilir; kalibrasyon ≥ 40 deneme; havuzun ortalama N'si gerçek
   N3bg'nin ±%5'i dışındaysa kalibrasyon bir kez yinelenir, yine dışındaysa dal 2 (geçersiz)." Koşudan önce yapılan MDE
   yeniden hesabı da kendi R'de kalibre edilir (`tr13b_v2_mde.py`'de `M.kalibre` R'yi geçirmeli).
3. **D-3 (K2, dal 2).** "Geçersiz: koşu betiği yapay girdiyle (her olayın R ve N3bg'si, dallanma 0,6) çalıştırıldığında
   (a) sinyalsiz yapayda R0'ın yanlış alarmı > 0,05 ya da (b) f = 0,4'te R0'ın gücü 0,65'in altında. Gerçek z
   görülmeden koşar." Bir üye düşerse küme kalan üyeyle sürer; küme boşalırsa düşer.
4. **D-4 (K3, kod ve tohum).** Koşu betiği dondurmadan önce yazılır, yapay girdiyle D-3 denetiminden geçirilir ve
   sha256'sı ön kayda yazılır. Sıfır havuzları olay başına ve dallanma başına **tam 2000** bölge, tohum
   `20261201 + 1000 × olay sırası + dallanma sırası` (ya da yazarın seçtiği, ama yazılı tek tohum); T1 çekilişi 200 000,
   tohum yazılı. Koşu bir kez yapılır; Monte Carlo yüzünden "sınırda" çıkan p yeniden koşulmaz.
5. **D-5 (§8).** C'deki üç ek.

Öneriler: Ö-a Küba 2024'ün referans penceresi [2014, 2021) Jamaika 2020 Mw 7,7 artçılarının bir kısmını içerebilir;
GK74'ün M 7,7 penceresi ≈ 86 km / ≈ 970 gün. Kural değişmez, ama raporda referans penceresindeki en büyük olay ve
uzaklığı yazılsın (denetlemedim). Ö-b Bozulma senaryolarının yoğunluğu hem INCELEME-1'de hem burada seçimdir; §9.2'de
"gerçek sıklık ölçülmedi" cümlesi kalsın.

## Yeniden üretim

```
cd kayit/turetme/tr13b/inc2
python3 -I -B tr13b_inc2.py tr13b_inc2.json        # ≈ 9 dk, 4 çekirdek
```
Sınırlar: bütün sayılar yapay ETAS; veri havuzu üye başına ≈ 125–210 bölge, red oranlarında ±0,01–0,015, güçte ±0,03;
veri havuzları sıfır havuzlarından ayrı kalibre edildi (gerçekteki tek kalibrasyon gürültüsünden biraz kötümser); D1 ve
D4'ün yoğunluğu seçimdir; D4'ün kenarı R ile ölçeklendi (0,375 R), bu yüzden bileşimdeki D4 etkisi INCELEME-1'in R 80
sayısından küçüktür.
