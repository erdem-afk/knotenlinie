# AG/KURAL.md — sonlu kaynak çekirdeği (X-b-5,5) SCSN tezgâhında

Bu dosya puanlamadan (SCSN 2011–2020 X, D1, D0 koşuları) **önce** yazıldı. Sonradan değişmez; gerekirse
puanlamadan önce tarihli "Ek" eklenir. Çerçeve: ortak ölçüm ve kabul kuralları, `Y/KURAL.md` (+ Ek, Ek 2),
`X/KURAL.md`.

## Önceden sabit model (seçim yok)

Tek aday: **X-b-5,5**, deney X'in İtalya'da seçtiği biçim, yeniden seçim yok.

- Taban: Y tezgâhının **D1**'i (dönem Mc'li R-tipi ETAS), ayar ≤2010-12-31, `gunluk_y` ile aynı veri, aynı kesme
  (uzay 100 km, zaman 365,25 gün), aynı hedef eşiği (M≥2,8; ikinci eşik 2,9). **D1 parametreleri aynen alınır, yeniden MLE yok.**
- X yalnız **M ≥ 5,5** ebeveynlerin doğrudan uzaysal çekirdeğini değiştirir; üretkenlik (K, α), c, p, D, q, γ, b, μ ve
  zaman çekirdeği D1'inkiyle aynı. Büyüklük kutusu ağırlıkları ve Mc(t) kuralı (yalnız dönem Mc) aynı.
- Doğrultu yolu **b**: ebeveynden sonra, gün başından önceki, `≤3 gün` ve `≤ L(M)` km içindeki artçıların (tabandaki
  tarihçe süzgeci: M ≥ Mc0) temel bileşen ekseni; **en az 10** olay yoksa ebeveyn izotrop kalır. Şerit merkezi
  artçı bulutunun ağırlık merkezi, doğrultu kuzeyden saat yönü. Yön her gün, ebeveynin `t+3 gün` sonrasına dek yeniden
  hesaplanır, sonra donar (X'teki gibi).
- Uzunluk: Wells ve Coppersmith 1994, yüzey altı kırık boyu, `L = 10^(−2,44 + 0,59 M)` km.
- Şerit: K tek sayı düğüm (3–15; aralık ≈ D_i/2, `etas_sonlu.model.serit_noktalari`), eşit ağırlık, toplam kütle ebeveynin
  izotrop çekirdeğiyle aynı (düğüm çekirdeklerinin ortalaması). **Kesme tutarlılığı:** her düğüm çekirdeği, tabanın
  izotrop çekirdeğiyle aynı `R ≤ 100 km` kırpmasından geçer (R düğümden ölçülür); kırpılmış çekirdek yeniden normalize
  edilmez. Zaman kesmesi (yaşı 365,25 günü aşan ebeveyn katkı vermez) tabandaki gibidir. Tahmin, olay terimi ve integral
  aynı `beklenen` çıktısından gelir (ayrı bir kompansatör yok; X yalnız tahmini değiştirir, ayar D1'in).
- Düzeltme yalnız doğrudan ebeveyn satırıdır: `cell += Σ_j w_j (şerit_j − izotrop_j)`, `w_j` D1'in K·10^{α(M_j−Mc0)}·Omori ağırlığı.

Hüküm bakımından bilmeyi gerektiren bir önkoşul (puanlamadan önce, performans görülmeden listelendi): katalogda 2011–2020'de
M ≥ 5,5 olaylar şunlardır: 2012-08-26 (5,50), 2019-07-04 (6,40), 2019-07-06 (7,10 ve 5,50), 2020-06-04 (5,51), 2020-06-24 (5,80);
yedi ebeveyn. Ridgecrest dizisi (2019) baskın olacaktır. Bu sayı modelin seçimini ya da eşiği değiştirmez.

## Ölçüm

- Çerçeve `Y/KURAL.md`'deki gibi: 0,1° ızgara, günlük, 0,1 M kutuları, her UTC gün başında yalnız gün başından önceki olaylar geçmişte.
  Hedefler `[2011-01-01, 2021-01-01)`, `hedef = 2,8` ve `hedef + 0,1 = 2,9`.
- **Hüküm satırı: SCSN 2011–2020, M ≥ 2,8, X − D1.** IG = ortalama log(λ_X/λ_D1) − (Λ_X − Λ_D1)/N; haftalık UTC-Pazartesi blok SE'si
  (`kor_ac.blok_ozeti`), tek yönlü z.
- **Kabul (ortak bileşen kabul kuralı):** M ≥ 2,8'de IG > 0 ve z > 1,645; M ≥ 2,9'da IG > 0. İkisi sağlanırsa X finalist modele girer.
  Sağlanmazsa girmez. Beraberlikte ya da z ≤ 1,645'te girmez.
- **Ek satırlar** (hükme girmez): X − D0 (M ≥ 2,8/2,9), D1 − D0 (Y2'yle özdeşlik denetimi, beklenen +0,280 / +0,259);
  N/S/M operasyonel tanı (`tools/karsilastir/puan.py`).
- **Büyük ebeveyn alt kümesi:** hedefin önceki 30 gün ve 100 km içinde M ≥ 5,5 bir olay (katalogdaki herhangi bir olay)
  bulunması. Raporlanan: N, olay terimi IG_olay ± SE (haftalık blok), z, ve X'teki tanımla IG (olay terimi eksi toplam
  integral farkı / N_alt). Hüküm değil, tanıdır.
- **GeoNet ek satırı** (bilgi için, hükme girmez; Y2'nin GeoNet ayarı sınırda): aynı kurallar, bölge `geonet`, hedef 3,8 / 3,9,
  kesme 100 km (zaman kesmesi yok), X − D1 (ve X − D0). Zaman kesmesi olmadığından GeoNet'te bütün M ≥ 5,5 ebeveynler (2010 Darfield dahil)
  tarihçede kalır.
- Bütün Λ ve N için ortak ölçüm alanları `OLCUM.json`'da: N, Λ_aday, Λ_taban, IG, IG_olay, integral, SE_blok, z, p_tek, N/S/M.
- Tohum 20261011, 10000 N/S/M tekrarı.

## Test ve defter

- Testler (iki Python): kütle korunumu, doğrultulu sentetik dizide PCA hatası <10° ve şerit logL > izotrop, büyük ebeveyn
  ya da doğrultu yoksa X = D1 birebir, defter–koşucu logL farkı 1e−9.
- Skor defteri `$KNOTENLINIE_RUNS/defter/AG/` (D1, X; D0): `<model>__<bolge>__2011-2020__olay/gun.csv.gz`, `Y` defteriyle aynı sütunlar.
  D1'in logL'i ve olay oranları `Y` defteriyle (D1__scsn__2011-2020) karşılaştırılır: ayar bit düzeyinde yeniden üretilmeli (denetim).

## Kaynak

Yerel makine, tek ağır süreç, tepe bellek ≤4 GB izlenir. Süre D0/D1 ayarı + 3 günlük geçiş.

## Sonradan yapılan her şey

Sonuç görüldükten sonra denenen her şey `AG/EK-kayit-disi.md`'de, "kayıt dışı" etiketiyle durur ve hükme girmez.
