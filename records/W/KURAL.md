# W/KURAL — kısa süreli tamlık (STAI) seçim ve puanlama kuralı

Bu dosya 2011–2015 puanlamasından **önce** yazıldı; 2011–2015 verisi bu noktada
açılmadı. Aşağıdaki seçim kuralı ve varyant listesi donmuştur.

## Model

R'nin (uzun, Mc(t)'li, CSEP-maskeli ETAS) olabilirliği korunur. Etkin tamlık

```
Mc_e(t) = max(Mc_dönem(t), Mc_sonra(t))
```

olur. Gözlenen her hedef `s(t)=10^(-b(Mc_e(t)-Mc0))` tespit ağırlığıyla girer
(ETAS-D biçimi); kompansatör de aynı ağırlıkla Mc_e üstündeki oranı GR ile
integre eder. Ebeveyn olarak Mc_dönem üstündeki bütün olaylar kalır; eksik
ebeveyn impute edilmez. R'nin maskesi, KDE arka planı, b'si ve Mc_dönem basamağı
(1985–2004 Mc=3,1; 2005+ Mc=2,5) aynen alınır. Not: "Mc_e altındaki olay hedef
sayılmaz" sert kesimi gözlenen katalogda monoton ve tanımsız olurdu (olayı
atmak serbestçe log-olabilirliği artırır); bu yüzden sert kesim yerine R'nin
kendi Mc(t) mantığının sürekli hâli olan tespit ağırlığı kullanıldı.

İki önceden sabit biçim:

- **a (HKJ 2006 sabit):** `Mc_sonra(t)=max_j[M_j-4,5-0,75·log10(Δt_gün)]`,
  `M_j≥5,0`, `0<Δt≤30` gün. Ek parametre yok.
- **b (Hainzl 2016 tipi kör süre):** son `M≥5,0` olaydan bu yana `Δt` ile
  `Mc_sonra(t)=Mc0+dMc·exp(-Δt/tau)`, `Δt≤60` gün. `(dMc,tau)` ≤ayar verisiyle
  MLE'de kestirilir; sınırlar `dMc∈[0,05;1,5]`, `tau∈[0,3;10]` gün.

İki hedef tanımı (ikisi de önceden sabit):

- **i:** gözlenecek oran = gerçek oran × `s(t)` (Mc_e'ye göre tespit olasılığı).
- **ii:** gerçek oran (tespit ağırlığı yok). Ayrım yalnız W'nin yeniden
  kurgulanmış ETAS parametrelerinden gelir; parametreler aynıysa ii = R.

## Adaylar ve seçim

Adaylar: `R`, `W-a-i`, `W-a-ii`, `W-b-i`, `W-b-ii`.

1. **Kurulum (≤2005):** R'nin ≤2005 R kurulumu (`etas_s_le2005.json`) tabandır.
   R kurulumu dallanma oranı sınırında (n≈1) durduğu için ETAS parametreleri
   birlikte kestirilemez; her W biçiminde ETAS parametreleri bu R kurulumunda
   **sabit** tutulur ve yalnız STAI parametreleri (`(dMc,tau)`) profil MLE ile
   kestirilir. Bu yüzden hedef ii tahmini R ile özdeştir; ayrım W'de `s(t)`
   çarpanından (hedef i) gelir.
2. **Seçim (2006–2010):** beş aday J/R günlük çerçevesinde (CSEP İtalya ızgarası,
   [0,30) km, HORUS-Mw, günlük, M≥2,95) puanlanır; en büyük logL kazanır.
   `W-·-i` günlük çarpanı `s(t)` ile türetilir.
3. **Yeniden kurulum (≤2010):** seçilen biçimin STAI parametreleri ≤2010
   verisinde, ETAS parametreleri R'nin ≤2010 kurulumunda sabitken yeniden
   kestirilir. Seçim R ise `etas_ortak.json` kullanılır.
4. **Puanlama (2011–2015):** seçilen W bir kez 2011–2015'te R-ortak-kaskad ve
   ETAS-LM'ye karşı puanlanır; M≥2,95/3,95/4,95.

Seçim 2011–2015 sonucuna göre değiştirilmez. Referanslar: R-ortak-kaskad
(`tools/etas_uzun/`), ETAS-LM (`tools/etas_lm/`).

## Raporlama

IG = ortalama log(λ_aday/λ_taban) − (Λ_aday−Λ_taban)/N; blok SE haftalık
(`tools/karsilastir/kor_ac.py: blok_ozeti`), tek yönlü z. Dizi payı: hedeflerin
önceki 30 gün/50 km içinde M≥5 olay olan alt kümesi. Skor defteri
`$KNOTENLINIE_RUNS/defter/W/` altına her aday ve dönem için yazılır.

## Ek 1 (2026-10-12; 2011–2015 puanlamasından önce, 2011–2015 verisi açılmadı)

Yukarıdaki metin değiştirilmedi; aşağıdakiler ona üstündür. Gerekçe, devralınan ilk
uygulamanın incelenmesinde bulunan iki yapısal kusurdur.

1. **Sert kesim ve tek ölçek.** "Mc_e altı hedef sayılmaz" kuralı θ'ya bağlı (b) biçiminde
   tanımsızdır (olay atmak olabilirliği serbestçe artırır). İlk uygulamadaki tek `s(t)`
   çarpanı ise bütün büyüklük kutularını kısıyordu; oysa M≥3,95 kutuları çoğu zaman
   eksik değildir. Yerine **yumuşak, büyüklüğe bağlı tespit** konur:
   `q(m,t)=Φ((m−Mc_sonra(t))/σ + z95)`, `σ=0,25`, `z95=1,645` (Mc_sonra %95 tamlık
   düzeyi; Ogata–Katsura 1993 biçimi). `σ` ve `z95` sabittir, hiçbir veriyle ayarlanmaz.
   Mc_dönem R'deki gibi sert kesimdir. Olabilirliğe etkin ağırlık
   `s_W(t)=∫_{Mc_dönem}^∞ f(m) q(m,t) dm` girer (GR yoğunluğu, kapalı çözüm); kompansatör
   `s_dönem − s_W` azalmasını analitik Omori integralleriyle düşer. Mc_sonra ve (a)/(b)
   formülleri yukarıdaki gibidir. (b) Hainzl 2016'nın hıza bağlı tespit olasılığı
   değil, onun zamansal bir sadeleşmesidir (son M≥5 olaydan üstel sönüm); bu sınırlama
   raporda yazılır.
2. **ETAS parametreleri sabit değil.** "ETAS parametreleri R kurulumunda sabit" maddesi
   kaldırıldı: bu, hedef ii'yi R ile özdeş kılar ve deney tasarımının sorusunu (kısa süreli
   eksiklik c, K, α'yı saptırıyor mu) sınanamaz bırakır. Her W biçiminde ETAS (8
   parametre) ve STAI parametreleri **birlikte** kestirilir; başlangıç R çözümü, b, KDE,
   maske ve Mc basamağı R'den aynen alınır. R'nin ≤2005 kurulumu dallanma sınırında
   (n=0,999999) durduğundan sınırdaki bir ETAS parametresi kısıt olarak kalır; bu W'ye
   de aynen uygulanır.
3. **Hedef tanımları.** (ii) gerçek oran = W parametreleriyle R'nin kaskad tahmini.
   (i) gözlenecek oran = (ii) × `q̄(gün, kutu)`: gün başı geçmişinden (yalnız gün başından
   önceki M≥5 olaylar) hesaplanan, kutu içi GR ağırlıklı ve gün içi zaman ağırlıklı
   ortalama tespit olasılığı. Gün içi ağırlık, geçmiş M≥4 olaylardan kurulan Omori
   oran vekilidir (μ + Σ K·10^{α(M−2,5)}(t−t_i+c)^{−p}). İki hedef aynı koşudan türer
   (kaskad çıktısı kutu bazında çarpılır).
4. **Seçim** değişmez: {R, W-a-i, W-a-ii, W-b-i, W-b-ii} içinde 2006–2010 M≥2,95
   logL'i en büyük olan. Eşitlikte R. Ayar ≤2005 (R: `etas_s_le2005.json`; W: onun üzerine
   birlikte MLE). Seçilen biçim ≤2010 verisiyle (başlangıç `etas_ortak.json`) aynı
   birlikte MLE ile yeniden kurulur ve 2011–2015'te bir kez puanlanır.
5. **Dizi alt kümesi** (önceki 30 gün/50 km içinde M≥5): integral terimi gruplara
   dağıtılmaz; alt kümede olay log-oranı toplamının N_alt'a bölümü (IG_olay) raporlanır.
