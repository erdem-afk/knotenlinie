# Z/KURAL — uzun vadeli ölçüm kuralı (2011–2015 puanlamasından önce donduruldu)

Bu dosya deney Z'nin tasarım adımlarını sabitler. Kural 2011–2015 puanlaması başlamadan önce
yazılmıştır; aday ızgaraları ve eşikler burada donar, sonuç görülünce değiştirilmez.

## Veri ve çerçeve

İtalya: `$KNOTENLINIE_DATA/ortak/italya_katalog_le2015.csv` (HORUS-Mw), CSEP İtalya ızgarası
(8993 hücre), derinlik `[0,30)` km, tamlık `Mc=3.1`. Eğitim başlangıcı İtalya 1985
(ortak zemin ile aynı). 2016+ satır hiçbir aşamada okunmaz (`katalog_oku` reddeder).

## Kümesizleştirme (önceden sabit)

Birincil **Gardner–Knopoff (1974)**: `dr = 10^(0.1238m+0.983)` km,
`dt = 10^(0.032m+2.7389)` gün (`m≥6.5`), yoksa `dt = 10^(0.5409m−0.547)` gün. Duyarlılık:
**Uhrhammer (1986)** `dr = exp(−1.024+0.804m)`, `dt = exp(−2.87+1.235m)`; **Reasenberg (1985)**
`rfact=10, xk=0.5, τ_min=1, τ_max=10 gün, p=0.95`. Pencere yöntemleri büyüklükçe azalan sırada
işler, zaman penceresi simetriktir (öncü + artçı); ana şok kendinden küçük komşuları siler.
Kümesizleştirme yalnız ≤2015 veriye ve ilgili ayar/hedef kesimine uygulanır.

## Modeller (`tools/uzun_vade/`)

Hepsi kümesizleştirilmiş katalogdan, kesik GR ile hedef eşiğine; `b` (Aki–Utsu) ve `M≥Mc`
toplam oranı yalnız ayar verisinden. Şekil hücre kütlesine normalize; `zemin=0.002` düzgün
taban sıfır hücreyi engeller.

- **U0** sabit bantlı Gauss KDE; σ ∈ {10, 20, 40} km.
- **U1** uyarlamalı bant (Helmstetter, Kagan ve Jackson 2007): her olayın σ'sı k'inci en yakın
  komşu uzaklığı; k ∈ {10, 20, 40}.
- **U2** = seçilen U1 + DISS 3.2.0 (`csstop320.geojson`, deney D `tools/fay_butce/`) fay moment
  bütçesi şekli; yalnız İtalya.
- **U3** = seçilen U1 + GEAR1 M≥5.95 uzaysal şekli (`gear1_<bolge>_01.npz`). [Yayın notu: U3 bu
  sürümde kapalıdır, GEAR1 dahil değildir; donmuş İtalya seçiminde U3 ağırlığı 0'dır ve seçilen şekil (U0)
  değişmez.]

Karışım ağırlıkları `w ∈ {0, 0.1, …, 0.9}` (toplam korunur, konveks şekil karışımı).

## Seçim ve puanlama takvimi

1. Adaylar **≤2005** verisiyle kurulur (b, oran, KDE; eğitim başlangıcından 2006-01-01'e).
2. Seçim **2006–2010**, kümesizleştirilmiş geliştirme eşiğinde (İtalya M≥3.95)
   hücre×kutu Poisson logL ile yapılır: U0 σ'sı, U1 k'sı, sonra U2/U3 `w`'si, en son U0–U3
   arasından en iyisi.
3. Seçilen hiperparametreler **≤2010** verisiyle yeniden kurulur.
4. **2011–2015** tek kez puanlanır; sonuç bu dosyayı değiştirmez.

## Ölçüm

Hedefler kümesizleştirilmiş (birincil) ve bütün olaylar (karşılaştırma) olarak M≥4.95'tür;
ayrıca geliştirme eşikleri raporlanır. 5 yıllık tek dönemde hücre×kutu Poisson logL, olay başına
bilgi kazancı

    IG = mean(log λ_aday − log λ_taban) − (Λ_aday − Λ_taban)/N,

olay yeniden örneklemeli bootstrap SE (2000 tekrar, tohum 20261005), N/S/M (`puan.tutarlilik`)
ve güç beyanı `P(z>1.645) = Φ(IG/SE − 1.645)`. Güç, tahmin edilen IG/SE ve kör pencerede aynı
N varsayımıyladır.

## Yerleşik taban sınırı

CSEP İtalya XML'leri yalnız **M≥4.95** yayımlar (`csep_xml`; taban
kutuları 4.95'ten başlar). Donmuş okuyucular değiştirilmez, alt eşiğe ekstrapolasyon yapılmaz.
Bu yüzden hüküm satırları M≥4.95'tir; M≥3.95 geliştirme satırları düzgün alan sıfırına
karşıdır ve `not_` alanında bu açıkça yazılıdır.
