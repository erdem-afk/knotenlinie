# Z2/KURAL — uzun katalogdan Weichert toplam oranı (puanlamadan önce donduruldu)

Bu dosya deney Z2'nin tasarım adımlarını sabitler. **Z2 bir kör test değildir:** 2011–2015
penceresi Z'de zaten görülmüştür ve Z2 aynı pencereyi puanlar; burada 2011–2015'e göre
hiçbir seçim yapılmaz. Tek önceden sabit model ve iki duyarlılık vardır; sonuç bunları
değiştirmez.

## Amaç

Z'nin kaybının ana kaynağı toplam orandı (İtalya Λ 12,5 / gözlenen 7). Z toplam oranı ≤2010'un kısa dönem M≥Mc verisinden kesik GR ile M≥4,95'e
taşıyordu. Z2 bunun yerine uzun bir kümesizleştirilmiş katalogdan, dönemsel tamlıkla ve
Weichert (1980) kestiricisiyle M≥4,95 oranını kestirir; uzaysal şekil Z'nin seçtiği
şekildir (`sekil` dizisi birebir). Skor zinciri: uzun katalog oranı × Z'nin şekli →
2011–2015 kümesizleştirilmiş M≥4,95 → MPS04/HAZFX/TripleS karşısında IG.

## Kestirici (yeni modül `tools/uzun_vade/weichert.py`)

Weichert (1980), eşit olmayan tamlık dönemlerinde ayrık büyüklük kutuları üzerinden
profilli Poisson MLE'sidir: `n_i ~ Poisson(A·T_i·q_i(b))`,
`q_i(b)=10^(-b(m_i-m1))-10^(-b(m_{i+1}-m1))`; `T_i` tamlık eşiği `Mc<=m_i` olan dönemlerin
süresidir. Eşikler 0,1 ızgarasında olduğundan kutu/olay uyuşmazlığı yoktur. `A` m1
eşiğindeki yıllık orandır; hedef `M>=4,95` oranı `A·10^(-b(4,95-m1))`. Tamlık tablosu
tabanı `bas` dönemlerin başıdır (İtalya 1000).

## İtalya

`$KNOTENLINIE_DATA/kesik-2015/CPTI15_v4.0_le2015.csv`, `MwDef`, default konum `LatDef/LonDef`,
≤2010; CSEP İtalya maskesi (8993 hücre). **Derinlik bilgisi eksiktir; bütün derinlikler
alınır.** Gardner–Knopoff (1974) kümesizleştirme ([0,1) ızgara, kesirli yıl). Tamlık
dönemleri yayımlanmış CPTI/Stucchi (2011) çizelgesinden (`weichert.CPTI_TAMLIK`):
1000–1348 Mc 6,5; 1348–1450 6,1; 1450–1500 5,7; 1500–1600 5,5; 1600–1750 5,3;
1750–1850 5,0; 1850–1870 4,7; 1870–1900 4,5; 1900–1940 4,3; 1940–1970 4,1;
1970–1980 4,0; 1980+ 3,5. Repodaki `tools/isindirma/girdi/cpti15_tamlik.json`
DETERMINED-PENDING olduğundan tablo CPTI15 v4.0 belgesinden doğrulanamadı; bu çizelge
kullanıldı ve sınırlılık rapordadır. Stepp (1972) yedeği de koşuldu; durağan hız
varsayımı bozulduğu için tek/kararsız dönem verdi (tanı olarak `OLCUM.json`).

## Model

Tek önceden sabit birincil model: toplam = ≤2010'dan kurulmuş Weichert `M>=4,95` oranı
(5 yıl), `b` Weichert'ten, şekil Z'nin seçtiği şekil (İtalya U0 σ=10 km).
UzunVade `rate_ust`, modelin `M>=4,95` kümülatifi Weichert oranına eşit olacak şekilde
seçilir. İki duyarlılık:

1. **b_Z:** b Weichert'ten değil Z'nin model b'sinden (0,806 İtalya);
   oran aynı Weichert oranı.
2. **sık_tablo:** tamlık tablosu bir kademe (0,5) sıkı (`weichert.sikilastir`); b ve
   oran bu tablodan yeniden kestirilir.

Ayrıca 2006–2010 için ≤2005 verisiyle kurulmuş Weichert oranı raporlanır (şekil aynı).

## Ölçüm

Z'nin `tools/karsilastir/uzun_z.py` puanlayıcısı import edilir. Hedefler Z ile aynı:
2011–2015 ve 2006–2010, kümesizleştirilmiş ve bütün olaylar, M≥4,95; tabanlar HAZFX,
TripleS, MPS04 (İtalya). Hücre×kutu Poisson logL, olay başına bilgi kazancı
`IG = mean(log λ_aday − log λ_taban) − (Λ_aday − Λ_taban)/N`, olay yeniden örneklemeli
bootstrap SE (2000 tekrar, tohum 20261005), N/S/M ve güç beyanı
`P(z>1,645)=Φ(IG/SE−1,645)`. Poisson kimliği (`(logL_aday−logL_taban)/N = IG`) her
satırda zorunludur.

## Sınırlar

CPTI15 kendi yayımlanmış tablosundan değil, atıflı CPTI/Stucchi çizelgesinden kuruldu;
bu bir sınırlılıktır.
Derinlik CPTI15'te yoktur. Karşılaştırma yalnız M≥4,95'tir (yerleşikler alt eşiği
yayımlamaz). Bu bir kör/GEAR1 hükmü değildir.
