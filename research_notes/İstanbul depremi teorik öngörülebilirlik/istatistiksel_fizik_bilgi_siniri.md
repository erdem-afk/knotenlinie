# Büyük deprem zamanlamasının istatistiksel fizik ve bilgi kuramı: tek bir fayda (ör. Marmara altındaki KAF) M7+ olayın zamanı Poisson'a göre kuramsal olarak ne kadar daraltılabilir? (durum: 2026)

Yöntem notu. Literatür taraması OpenAlex (yerel `kayit/oa.py`) üzerinden yapıldı. Açık erişimli tam metinler (Molchan 2010 arXiv, Sornette & Knopoff 1997 arXiv) okundu; diğer kaynaklarda yalnız özet/künye görüldü. "Hesap" diye işaretlenen sayılar bu not için Python/SciPy ile analitik formüllerden hesaplandı (betik: `/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/calc/renew.py`). Bunlar yayımlanmış sayı değil, standart formüllerin sayısal değerleridir. Hesaplarda zaman birimi ortalama yinelenme süresi μ'dür (t/μ). Hiçbir yerde İstanbul için mutlak olasılık verilmedi. Kaynakta doğrulanamayan sayılar "doğrulanamadı" diye işaretlendi. 2026 katalog verisi kullanılmadı.

---

## 1. Yenilenme (renewal) kuramı: BPT, Weibull, lognormal; çevrim sonunda tehlike fonksiyonu, "gecikmiş" faylar, bilgi kazancı ve α

### Takeaway
Bilinen parametrelerle bir yenilenme modelinin Poisson'a göre beklenen bilgi kazancı yalnız aperiyodiklik α'ya (CV) bağlıdır. Paleosismolojide tipik α≈0.3–0.7 için bu kazanç olay başına ≈0.85–0.24 nat'tır (olasılık kazancı ≈2.3–1.3 kat). Çevrim sonunda tehlike oranı Poisson'un en fazla ≈1.5–3 katıdır. Uyarı penceresini yıl ölçeğine (μ≈250 yıl için ±1 yıl) indirmek için α≈0.004 gerekir; bu, gözlenen değerlerden iki mertebe küçüktür. Yani yenilenme kuramı ilkesel olarak yıl ölçeğinde daraltma vermez, onlarca yıl ölçeğinde "birkaç kat" verir.

### Cited Findings
**Denklemler**
- BPT (ters Gauss) modeli, sabit yüklemeye Brown gürültüsü eklenen bir durum değişkeninin kırılma eşiğine ilk varış zamanıdır: f(t; μ, α) = (μ/(2πα²t³))^{1/2} exp[−(t−μ)²/(2μα²t)]. α = CV olarak tanımlanır. Matthews, Ellsworth & Reasenberg (2002), BSSA 92(6), "A Brownian Model for Recurrent Earthquakes" — [DOI](https://doi.org/10.1785/0120010267). (Formül ve "tehlike, sonlu bir asimptota yaklaşır, sıfıra düşmez" özelliği bu makalenin bilinen içeriğidir; tam metin bu oturumda okunmadı.) Fiziksel temeli için bkz. Ellsworth ve ark. (1999), USGS OFR 99-522 — [DOI](https://doi.org/10.3133/ofr99522).
- BPT'nin tehlike fonksiyonu h(t) = f/S, t→∞ iken 1/(2α²μ) değerine yaklaşır. Hesap, aşağıdaki tabloda bu asimptotu doğruluyor.
- Lognormal ve Weibull aynı ortalama ve CV ile parametrelendirildi. Lognormal'de σ² = ln(1+α²). Weibull'da k, CV = √(Γ(1+2/k)/Γ²(1+1/k) − 1) eşitliğinden çözüldü.

**"Ne kadar uzun süre geçtiyse o kadar uzun mu beklenir?"**
- Davis, Jackson & Kagan (1989), BSSA 79(5) — [DOI](https://doi.org/10.1785/bssa0790051439). Lognormal yinelenme kullanır ve parametre belirsizliğini (μ ile varyansın olabilirlik ortalaması) ve geçen "kuraklık" süresini parametre tahminine katar. Olaysız geçen zaman μ ve varyans tahminlerini büyütür, bu da başlıktaki soruya sonunda "evet" yanıtını getirir: "kuraklık tahmini yinelenme süresini aşınca risk tahmini düşmeye başlar." Parkfield için 1988 sonrası her olaysız yılda 5 yıllık olasılığın azalacağını öngörmüşlerdir.
- Sornette & Knopoff (1997), BSSA 87(4) — [DOI](https://doi.org/10.1785/bssa0870040789), [arXiv](https://arxiv.org/pdf/cond-mat/9705046). Analitik sonuç şudur: periyodik, düzgün, yarı-Gauss, Rayleigh dağılımlarında ve k>1 Weibull'da uzun geçen sürede beklenen kalan süre azalır. Lognormal, kuvvet yasası ve k<1 Weibull'da artar. Ayrımı, kuyruğun üstel düşüşe göre hızı belirler. Poisson'dan sonlu örneklem alınması bile artan kalan-süre tahmini üretir.
- Hesap (beklenen kalan süre E[T−tₑ | T>tₑ], birim μ; tₑ = 0, 0.5, 1, 1.5, 2, 3, 4):
  - BPT α=0.5: 1.00, 0.57, 0.47, 0.44, 0.44, 0.44, 0.45. Değer 2α²μ = 0.5μ platosuna oturur.
  - LN α=0.5: 1.00, 0.57, 0.46, 0.45, 0.47, 0.52, 0.58. Yaklaşık tₑ>1.5μ'den sonra yeniden artar.
  - LN α=1.0: 1.00, 0.85, 0.95, 1.08, 1.20, 1.44, 1.66. Davis ve ark. paradoksunun kendisidir.
  - Sonuç: "gecikmiş" bir fay için BPT tehlikesi sabit bir platoya, lognormal tehlikesi yavaşça sıfıra, Weibull (k>1) tehlikesi sınırsız artışa gider. Çevrim sonu davranışı tamamen dağılım seçimine bağlıdır ve veriyle ayırt edilemez (bkz. Inferences).

**Tehlike oranı h(t)/(1/μ) (hesap)** — tₑ/μ = 0.5, 0.8, 1.0, 1.1, 1.3, 1.5, 2.0, 3.0:

| α | model | 0.5 | 0.8 | 1.0 | 1.1 | 1.3 | 1.5 | 2.0 | 3.0 | asimptot |
|---|---|---|---|---|---|---|---|---|---|---|
| 0.3 | BPT | 0.24 | 1.93 | 3.01 | 3.43 | 4.05 | 4.48 | 5.07 | 5.47 | 5.56 |
| 0.3 | LN | 0.24 | 1.93 | 3.04 | 3.47 | 4.08 | 4.46 | 4.82 | 4.68 | →0 |
| 0.3 | Weibull (k=3.71) | 0.39 | 1.39 | 2.54 | 3.29 | 5.17 | 7.63 | 16.7 | 50 | →∞ |
| 0.5 | BPT | 0.93 | 1.72 | 1.97 | 2.05 | 2.15 | 2.21 | 2.27 | 2.27 | 2.00* |
| 0.5 | LN | 0.89 | 1.73 | 2.02 | 2.11 | 2.22 | 2.26 | 2.24 | 2.03 | →0 |
| 0.5 | Weibull (k=2.10) | 0.76 | 1.27 | 1.63 | 1.81 | 2.17 | 2.54 | 3.49 | 5.46 | →∞ |
| 0.7 | BPT | 1.25 | 1.50 | 1.53 | 1.53 | 1.52 | 1.50 | 1.44 | 1.35 | 1.02 |

*α=0.5'te BPT tehlikesi asimptota üstten, tepe yaparak yaklaşır.

Pratik anlamı: tₑ≈μ civarında α=0.5 ile tehlike Poisson'un yaklaşık 2 katıdır, α=0.3 ile yaklaşık 3 katıdır. Üç model tₑ≲1.1μ'ye kadar neredeyse aynı değeri verir.

**Bilgi kazancı (entropi skoru)**
- Harte & Vere-Jones (2005), PAGEOPH 162, "The Entropy Score and its Uses in Earthquake Forecasting" — [DOI](https://doi.org/10.1007/s00024-004-2667-2). Bu makale, olasılık tahminlerinin log-olabilirlik (entropi) skorunu ve beklenen değerinin sürecin entropisine bağlı bir kazanç olduğunu tanımlar. Özet OpenAlex'te yok, tam metin kapalı; formül ayrıntıları kaynaktan doğrulanamadı. Ayrıca Vere-Jones (1998/2013), "Probabilities and Information Gain for Earthquake Forecasting", Computational Seismology (AGU yeniden basım) — [DOI](https://doi.org/10.1029/cs005p0104).
- Imoto (2014), Earth Planets Space 58, "Probability gains expected for renewal process models" — [DOI](https://doi.org/10.1186/bf03352517). Yenilenme modeli ile durağan Poisson arasındaki log-olabilirlik farkının beklenen değeri, olasılık kazancının logaritmasının beklenen değerine eşittir. Zaman birimi beklenen aralığa çevrilince serbest parametre sayısı 1'e (α'ya) iner. Gözlenen parametre değerlerinde beklenen olasılık kazancı 2 ile 5 arasındadır. Imoto'nun kazanç tanımı olay anındaki tehlike oranına dayanır; aşağıdaki "olay başına ortalama log kazanç" ile aynı nicelik olmayabilir. Tablo değerleri tam metin açılamadığı için doğrulanamadı.
- Hesap: μ=1 alınırsa, bilinen parametreli bir yenilenme sürecinin aynı ortalamalı Poisson'a göre olay başına beklenen log-olabilirlik kazancı G = E[ln f(T)] − E[ln e^{−T}] = 1 − H(f) olur. Burada H, normalize aralık yoğunluğunun diferansiyel entropisidir; üstel dağılım için H=1 olduğundan G=0'dır.

| α | G_BPT (nat/olay) | e^G | G_LN | G_Weibull | olay başına LLR std (BPT) | t-testi ile ayırt etmek için gereken olay sayısı N (iki yönlü %5, güç 0.8) |
|---|---|---|---|---|---|---|
| 0.1 | 1.89 | 6.6 | 1.89 | 1.93 | 0.70 | ≈1 |
| 0.2 | 1.22 | 3.4 | 1.22 | 1.20 | 0.67 | ≈2.4 |
| 0.3 | 0.85 | 2.3 | 0.85 | 0.79 | 0.64 | ≈4.4 |
| 0.5 | 0.44 | 1.56 | 0.44 | 0.32 | 0.52 | ≈11 |
| 0.7 | 0.24 | 1.27 | 0.24 | 0.10 | 0.40 | ≈22 |
| 1.0 | 0.12 | 1.13 | 0.11 | 0 | 0.30 | ≈46 |

  N ≈ ((z₀.₉₅+z₀.₈)·s/G)². Bu, parametreler biliniyor varsayımıyla bir üst sınırdır; parametreler veriden tahmin edilirse gereken N büyür. Dikkat: N olay sayısıdır. Tek bir Marmara segmentinde μ yüzyıl mertebesinde olduğundan, α=0.5 için bile ≈11 olay, binlerce yıllık prospektif kayıt demektir.

**Yıl ölçeğinde daraltma için gereken α (hesap)**
- BPT'de tₑ=μ verildiğinde kalan sürenin %5–%95 aralık genişliği (μ birimi): α=0.05 → 0.099; α=0.1 → 0.21; α=0.2 → 0.44; α=0.3 → 0.71; α=0.5 → 1.33. Küçük α için genişlik ≈2αμ.
- Örnek, yalnız ölçek göstermek için ve Marmara parametresi olarak iddia edilmeden: μ=250 yıl alınırsa, α=0.5'te %90 penceresi ≈330 yıl, α=0.1'de ≈50 yıl, α=0.05'te ≈25 yıldır. Yaklaşık 2 yıllık bir pencere α≈0.004 gerektirir.
- Molchan optimal alarm stratejisi (hesap; BPT'de tehlike monoton arttığı için alarm "t>t₀" demektir). α=0.5, t₀=μ: alarm zaman oranı τ=0.19, ıskalama oranı n=0.59, kazanç (1−n)/τ=2.15. α=0.3, t₀=μ: τ=0.12, n=0.56, kazanç=3.8. Yani olayların yarısını yakalamak için alarm, çevrimin yaklaşık %12–19'u boyunca, yani onlarca yıl açık kalmalıdır.

**Parametre (α) ampirik değerleri**
- Ellsworth ve ark. (1999) ve WGCEP pratiği α≈0.5'i genel değer olarak kullanır — [USGS OFR 99-522](https://doi.org/10.3133/ofr99522). (0.5±0.2 değeri yaygın biçimde bu kaynağa atfedilir; bu oturumda tam metinden doğrulanamadı.) Paleosismik yaş belirsizliğinin α tahminlerine etkisi için bkz. "Age Uncertainty in Recurrence Analysis of Paleoseismic Records" (2021), JGR — [DOI](https://doi.org/10.1029/2021jb021996) (yazarlar ve bulgu ayrıntısı doğrulanamadı).

**Marmara uygulaması (yalnız oran)**
- Murru, Akıncı, Falcone, Pucci, Console & Parsons (2016), JGR 121 — [DOI](https://doi.org/10.1002/2015jb012595). Marmara'da 26 kaynak ve 10 çok-segmentli Mw7–8 kırılma için Poisson, BPT ve BPT+ΔCFF modellerini Monte Carlo ile karşılaştırır (α, Mmax, kayma hızı belirsizlikleri Gauss dağılımlı). İstanbul için toplu M>7.3 olasılığında zamana bağlı + etkileşim modelinin Poisson'a oranı ≈1.3'tür (iki mutlak değerin oranından türetildi; mutlak değerler bu notta bilerek verilmedi). Gerede segmenti için oran ≈1.7'dir.

**Gerilme-boşalım (stress-release) modelleri**
- Vere-Jones (1978), J. Phys. Earth 26, "Earthquake prediction – a statistician's view" — [DOI](https://doi.org/10.4294/jpe1952.26.129). Kısa ve orta vadeli risk tahminini kesin öngörüye alternatif olarak önerir. Gerilme-boşalım fikrinin istatistiksel çıkış noktası olarak anılır.
- Gerilme-boşalım modelinin yoğunluk fonksiyonu λ(t) = exp[a + b(ρt − S(t))]'dir; S(t), t'ye kadar boşalan toplam "gerilme"dir (tipik olarak ∝ 10^{0.75M}). LSRM sürümü: λᵢ(t) = exp[aᵢ + bᵢ(ρᵢt − Σⱼ θᵢⱼ Sⱼ(t))]; θᵢⱼ>0 bir bölgedeki olayın diğerinde gerilmeyi kaldırmasını (inhibisyon), θᵢⱼ<0 ise aktarımı (tetikleme) gösterir. Bebbington & Harte (2003), GJI 154 — [DOI](https://doi.org/10.1046/j.1365-246x.2003.02015.x). Olasılık kuramı için Liu, Vere-Jones ve ark. "On the statistics of the linked stress release model" (2001), J. Appl. Prob. — [DOI](https://doi.org/10.1017/s0021900200112768). (Denklem biçimi literatürde standarttır; bu oturumda tam metinden satır satır doğrulanamadı.)
- Uygulamalar: Japon tarihsel depremleri — [DOI](https://doi.org/10.1186/bf03351562) (2014); iki tektonik tipte tarihsel veri — [DOI](https://doi.org/10.1007/pl00001087) (2000); İtalya Bayesçi SRM — [DOI](https://doi.org/10.1111/j.1365-246x.2006.03314.x) (2007); eşbağlı SRM'lerde Poisson-dışı davranış ve tehlikeye etkisi — [DOI](https://doi.org/10.1111/j.1365-246x.2008.03835.x) (2008); Coulomb aktarımlı çok boyutlu SRM — [DOI](https://doi.org/10.1111/j.1365-246x.2011.05208.x) (2011); gerilme gevşemesi eklenmiş nokta süreci — [DOI](https://doi.org/10.1093/gji/ggad482) (2023). Zheng & Vere-Jones'un (1991/1994) özgün DOI'si OpenAlex'te eşleşmedi; künye doğrulanamadı.

**Prospektif ve yarı-prospektif sınamalar (kuramsal öngörünün değerlendirilmesi)**
- Parkfield: karakteristik/yarı-periyodik modelin 1988±5 öngörüsü tutmadı, olay 2004'te oldu. Bakun ve ark. (2005), Nature 437 — [DOI](https://doi.org/10.1038/nature04067).
- Sismik boşluk hipotezi: Rong, Jackson & Kagan (2003), JGR 108 — [DOI](https://doi.org/10.1029/2002JB002334). Kagan, Jackson & Geller (2012), SRL 83, "Characteristic Earthquake Model, 1884–2011, R.I.P." — [DOI](https://doi.org/10.1785/0220120107). Özetleri bu oturumda alınmadı. Bilinen sonuç, boşluk/karakteristik modelin prospektif dönemde Poisson'u geçemediğidir (ayrıntılı sayılar doğrulanamadı).
- UCERF3 zamana bağlı modeli, elastik geri tepme tipi yenilenmeyi fay sistemine uygular. Field ve ark. (2015), BSSA 105 — [DOI](https://doi.org/10.1785/0120140093).

### Inferences
- Yenilenme kuramının en iyi durumda verdiği şey on yıllar ölçeğinde "1.5–3 kat" bir tehlike oranıdır. Yıl ölçeğinde zamanlama, ancak fiziksel olarak inandırıcı olmayan α≲0.01 ile mümkündür. Bu α'dan bağımsız, ölçekten kaynaklanan bir sonuçtur: pencere ≈2αμ.
- Çevrim sonu davranışı (BPT platosu, LN düşüşü, Weibull artışı) tₑ>1.3μ'den sonra ayrışır. Bunu ayırt etmek için gereken olay sayısı tek bir fay için hiçbir zaman elde edilemez. Ayrımın kaynağı veri değil, model varsayımıdır (BPT'nin fiziksel gerekçesi Brown yüklemesi, LN'nin ise çarpımsal süreçtir).
- Davis ve ark. (1989) bağlamında parametre belirsizliği, tahmin edilen tehlikeyi Poisson'a doğru düzleştirir. Az olay bilinen (n≈3–6) bir Marmara segmentinde, Bayesçi ortalama alınmış α'nın etkin değeri nominal değerden büyüktür. Bu yüzden gerçek kazanç tablodaki değerlerden düşüktür.
- Tek bir fay için yenilenme modelinin prospektif sınaması ilkesel olarak yapılamaz. Yapılabilen tek şey birçok fayın havuzlanmasıdır (Rong 2003 ve Kagan 2012 türü küresel testler), bu da bağımsız α varsayımını gerektirir.

### Gaps
- Imoto (2014) tablosundaki α'ya göre kazanç değerleri ve Harte & Vere-Jones (2005) içindeki formüllerin tam biçimi: tam metinlere erişilemedi (Springer PDF bağlantısı HTML döndürdü; ödeme duvarı aşılmadı).
- Zheng & Vere-Jones LSRM özgün künyesi ve gerilme-boşalım modelinin olasılık kazancını α'ya karşılık veren kapalı formülü bulunamadı.

---

## 2. Öngörülebilirliğin kuramsal üst sınırları: Molchan hata diyagramı, entropi/bilgi skoru, ETAS ve öncü şoklar, magnitüd bağımsızlığı, EEPAS

### Takeaway
Molchan kuramına göre herhangi bir veri kümesi I(t) için en iyi alarm stratejisi koşullu yoğunluk r(t)'nin bir eşiği aşmasıyla tanımlanır. Bu yüzden ulaşılabilir kazanç tamamen r(t)/λ̄'nin zaman içindeki dağılımı tarafından sınırlanır. ETAS (magnitüd bağımsız) kuramında büyük olayların öncü özellikleri küçük olaylarınkinden farksızdır. Bu nedenle M7+ için kısa vadeli kazanç yalnız kümelenmeden gelir ve olayların çoğunda kazanç küçüktür. 2019–2022'de Nandan ve ark. magnitüd korelasyonlu ETAS'ın yarı-prospektif olarak daha iyi olduğunu öne sürmüştür. Bu, büyük olayların sınırlı ölçüde daha öngörülebilir olabileceğini gösterir; bağımsız prospektif doğrulama sınırlıdır.

### Cited Findings
- Molchan (1997), PAGEOPH 149, "Earthquake prediction as a decision-making problem" — [DOI](https://doi.org/10.1007/bf00945169). Molchan (2010), PAGEOPH 167, "Space–Time Earthquake Prediction: The Error Diagrams" — [DOI](https://doi.org/10.1007/s00024-010-0087-z), [arXiv](https://arxiv.org/pdf/0807.2533) (tam metin okundu):
  - Strateji π(t), I(t) verisine dayalı alarm kararıdır; hedef fonksiyon φ(n, τ)'dur. Burada n ıskalama oranı, τ alarm zaman oranıdır. Yerel olarak optimal strateji koşullu yoğunluk r(t) = P{dN(t)>0 | I(t)}/dt ile ifade edilir. Küçük aralıkta karar, iki basit hipotez testine (Neyman–Pearson) indirgenir ve (β(α), α) → (n(τ), τ) olur.
  - n(τ), I(t)'nin sınırlayıcı öngörü kapasitesidir. Konveks seviye kümeli her kayıp fonksiyonunun minimumu bu eğri üzerindedir. n+τ=1 köşegeni rastgele tahminleri gösterir. Öngörü potansiyeli max_τ(1−n(τ)−τ)/√2 ile ölçülür.
  - Uzay–zaman ağırlıklı sürümde optimal alarm koşulu rᵢ(t)/λᵢ ≥ c olarak yazılır ve "sol taraf olasılık kazancı olarak bilinir."
- Kagan (2007), PAGEOPH 164, "On Earthquake Predictability Measurement: Information Score and Error Diagram" — [DOI](https://doi.org/10.1007/s00024-007-0260-1). Bilgi skoru (olay başına nat) ile hata diyagramı arasındaki ilişkiyi kurar (özet yok; ayrıntı doğrulanamadı). Ayrıca Zechar & Jordan (2008), GJI, "Testing alarm-based earthquake predictions" — [DOI](https://doi.org/10.1111/j.1365-246x.2007.03676.x). Kagan (2009), GJI, "Testing long-term earthquake forecasts: likelihood methods and error diagrams" — [DOI](https://doi.org/10.1111/j.1365-246x.2008.04064.x). Molchan & Keilis-Borok (2008), GJI, "Earthquake prediction: probabilistic aspect" — [DOI](https://doi.org/10.1111/j.1365-246x.2008.03785.x).
- Kuramsal üst sınır (Molchan çerçevesinden türetme; Vere-Jones/Harte entropi skoruyla tutarlı): ψ(t) = r(t)/λ̄ normalize koşullu yoğunluk ve F, ψ'nin zaman ağırlıklı dağılımı olsun.
  - Optimal hata eğrisi: τ(c) = P(ψ>c), 1−n(c) = E[ψ·1{ψ>c}].
  - Olay başına beklenen bilgi kazancı: G = E_zaman[ψ ln ψ] = KL(olay-ağırlıklı ‖ zaman-ağırlıklı).
  - Sonuç: herhangi bir öncüden elde edilecek maksimum kazanç, o öncünün r(t)'de yaratabileceği değişkenlikle sınırlıdır. Örnek: ψ zamanın p kesrinde g katına çıkıyor, kalanında düşüyorsa (E[ψ]=1), G = p·g ln g + (1−p)·ψ₀ ln ψ₀, ψ₀=(1−pg)/(1−p). (Türetme bu nota aittir.)
- Vere-Jones (1995), Int. J. Forecasting 11, "Forecasting earthquakes and earthquake risk": DOI (10.1016/0169-2070(95)00591-9) OpenAlex'te bulunamadı, içerik doğrulanamadı. Daley & Vere-Jones'un nokta süreçleri kitabı (entropi skorunun kuramsal temeli) bu oturumda künye olarak doğrulanamadı. Ogata (2013), Statistical Science, "A Prospect of Earthquake Prediction Research" — [DOI](https://doi.org/10.1214/13-sts439). Ogata (2017), Annu. Rev. Earth Planet. Sci. 45 — [DOI](https://doi.org/10.1146/annurev-earth-063016-015918).
- ETAS ve öncü şoklar:
  - Model: λ(t) = μ + Σᵢ K·10^{α(Mᵢ−M₀)}/(t−tᵢ+c)^p, magnitüdler GR'den bağımsız çekilir.
  - Helmstetter & Sornette (2003), JGR 108, "Foreshocks explained by cascades of triggered seismicity" — [DOI](https://doi.org/10.1029/2003jb002409). Öncülerin anormal özellikleri (büyük/küçük oranı, ana şoka doğru kuvvet yasası ivmelenmesi, göç) "her deprem başka depremi tetikler" modelinden doğal olarak çıkar. Öncü özellikleri ana şok büyüklüğünden bağımsızdır. Bu nedenle büyük ya da küçük depremler, sismisite hızı geçmişten ne ölçüde öngörülebilirse o ölçüde öngörülebilirdir.
  - Felzer, Abercrombie & Ekström (2004), BSSA 94, "A Common Origin for Aftershocks, Foreshocks, and Multiplets" — [DOI](https://doi.org/10.1785/0120030069). Ayrıca Helmstetter, Sornette & Grasso (2003), "Mainshocks are aftershocks of conditional foreshocks", JGR — [DOI](https://doi.org/10.1029/2002jb001991).
  - Aksi yönde gözlem: "Rare Occurrences of Non-cascading Foreshock Activity in Southern California" (2021), GRL — [DOI](https://doi.org/10.1029/2020gl091757). Başlığa göre kaskad-dışı öncü etkinlik nadirdir; yazarlar ve sayılar doğrulanamadı.
  - Kısa vadeli ETAS kazancının ölçümü: Helmstetter, Kagan & Jackson (2006), BSSA 96 — [DOI](https://doi.org/10.1785/0120050067). Olay başına kazanç değeri bu oturumda doğrulanamadı.
- Magnitüd bağımsızlığına itiraz:
  - Nandan, Ouillon & Sornette (2019), JGR 124 — [DOI](https://doi.org/10.1029/2018jb017118). EM algoritmasıyla Kaliforniya kataloğunda üç farklı β değeri bulunur: arka plan için β_b, tetikleyiciden küçük tetiklenmişler için β_a−δ, büyükler için β_a+δ ("kinked" dağılım). Bu ETAS sürümü "katalogları açık ara en iyi tanımlıyor".
  - Nandan, Ouillon & Sornette (2022), JGR 127, "Are Large Earthquakes Preferentially Triggered by Other Large Events?" — [DOI](https://doi.org/10.1029/2022jb024380). Titiz yarı-prospektif deneylerde magnitüd korelasyonlu ve magnitüde bağlı Omori çekirdekli ETAS, basit ETAS'ı anlamlı biçimde geçer. "Büyük olaylar tercihen büyük olayları tetikler." Bu, "en küçük olaylar büyükleri tetiklemede baskındır, öngörü bu yüzden doğası gereği zordur" görüşüne (UV ıraksaklığı) karşı çıkar.
  - 2026 ön baskı: "Non-normal amplification in multitype Hawkes-ETAS models of earthquake triggering", arXiv 2607.26036 — [DOI](https://doi.org/10.48550/arxiv.2607.26036). İçerik okunmadı.
- EEPAS (Every Earthquake a Precursor According to Scale):
  - Öncül ölçek artışı (Ψ) olgusu: büyük olaydan (Mm) önce bir A_P alanında, T_P zamanında, M_P büyüklüğünde ani hız ve büyüklük artışı görülür. Ölçekleme ilişkileri Mm ≈ a_M + b_M M_P, log T_P = a_T + b_T M_P, log A_P = a_A + b_A M_P biçimindedir.
  - Christophersen, Rhoades & Hainzl (2024), SRL, "Algorithmic Identification of the Precursory Scale Increase Phenomenon in Earthquake Catalogs" — [DOI](https://doi.org/10.1785/0220240233). Ψ, büyük depremden önceki uzay–zaman kümelenmesinin bir özelliğidir: katalog rastgeleleştirilip artçılar çıkarılınca doğrulanmıştır. A_P–T_P ödünleşimi vardır. Ölçekleme ilişkileri gerçek ve ETAS-benzeri benzetim kataloglarında tutarlıdır. EEPAS, Yeni Zelanda kamu tahminlerinde hibrit modellere ve ulusal tehlike modeline katkı verir. Ufuk Mm'ye bağlı olarak "aylardan on yıllara" uzanır.
  - Özgün katsayılar (Evison & Rhoades 2002 ve sonrası; ör. b_M≈1) doğrulanamadı. Evison & Rhoades (2002), Annals of Geophysics, "Precursory scale increase and long-term seismogenesis in California and Northern Mexico" — [DOI](https://doi.org/10.4401/ag-3523). Japonya testi (Rhoades & Evison 2005), PAGEOPH — [DOI](https://doi.org/10.1007/s00024-004-2669-0). Güney Kaliforniya (2007), SRL — [DOI](https://doi.org/10.1785/gssrl.78.1.110). İtalya (2023), GJI — [DOI](https://doi.org/10.1093/gji/ggad123).

### Inferences
- Christophersen ve ark. (2024), Ψ'nin ETAS benzetimlerinde de ortaya çıktığını bildiriyor. Buna göre EEPAS'ın orta vadeli kazancı, kümelenme kuramından ayrı bir "kritik nokta" fiziği gerektirmez. Bu da Helmstetter & Sornette (2003) ile tutarlıdır.
- Magnitüd bağımsız ETAS'ta M7+ olayların çok küçük bir kesrinde uyarı kazancı büyük olur (öncülü olanlar). Olayların çoğunda r(t)/λ̄≈1 olduğundan Molchan eğrisi köşegene yakın kalır. Nandan ve ark.'ın magnitüd korelasyonu doğruysa ψ dağılımının üst kuyruğu M7+ için kalınlaşır; ama büyüklüğü (nat/olay) M7+ için bağımsız olarak ölçülmüş değildir.
- Tek fay ölçeğinde ETAS, yenilenme modelinin tersi bir hazard şekli verir: olaydan hemen sonra en yüksek, sonra Poisson'a geri döner. İki kuram birleştirildiğinde (UCERF3-ETAS) uzun vadeli yenilenme ile kısa vadeli kümelenme çatışır. UCERF3'te bu çatışma, kendi kendine tetiklemenin elastik geri tepme ile bastırılmasıyla çözülür (Field ve ark. 2017, BSSA — [DOI](https://doi.org/10.1785/0120160173)).

### Gaps
- Literatürde, belirli bir r(t) değişkenliği için maksimum kazancı veren adlandırılmış bir "Molchan–Kagan teoremi" bulunamadı. Yukarıdaki üst sınır Molchan'ın çerçevesinden türetilmiştir.
- ETAS'ın büyük olaylarda öngördüğü "öncülü olan ana şok kesri" (yaygın olarak ~%10–40 aralığında anılır): sayısal değer bu oturumda kaynaktan doğrulanamadı.
- Nandan ve ark. 2021 küresel model makalesi OpenAlex'te bulunamadı.

---

## 3. Kritik nokta kuramı ve hızlanan moment boşalımı (AMR / LPPL)

### Takeaway
Kritik nokta kuramı, kritik bölgede kümülatif Benioff gerinmesinin ε(t) = A + B(t_f − t)^m (m≈0.3) biçiminde hızlanacağını öngörür. Log-periyodik düzeltmeler ve log R ∝ ~0.44M olan bir kritik bölge yarıçapı da öngörü arasındadır. Hardebeck ve ark. (2008), veri uydurma serbestlikleri hesaba katılınca AMR'nin istatistiksel olarak anlamsız olduğunu gösterdi. Mignan (2011) sonrasında kuram "kritik olmayan" yükleme modellerine kaydı. 2026 itibarıyla AMR'nin prospektif başarısı belgelenmemiştir.

### Cited Findings
- Bufe & Varnes (1993), JGR 98, "Predictive modeling of the seismic cycle of the Greater San Francisco Bay Region" — [DOI](https://doi.org/10.1029/93JB00357). Zaman-kırılma analizinde boşalım hızı ∝ (t_f−t)^{−n}'dir ve üs ölçekten bağımsız görünür. Tam çevrimin 269±50 yıl olduğu tahmin edildi. 1989 Loma Prieta'nın geriye dönük olarak "2 yıl zaman ve 0.5 büyüklük belirsizliğiyle öngörülebilir olacağı" iddia edildi; konum öngörülemezdi.
- Sornette & Sammis (1995), J. Phys. I France 5, "Complex Critical Exponents from Renormalization Group Theory of Earthquakes" — [DOI](https://doi.org/10.1051/jp1:1995154). Kesikli ölçek değişmezliği karmaşık kritik üsler, yani log-periyodik düzeltmeler doğurur: ε(t) = A + B(t_f−t)^m[1 + C cos(2π ln(t_f−t)/ln λ + φ)]. Loma Prieta ve Aleut üzerinde ön sınamalar yapıldı. (Formül LPPL'in standart biçimidir; λ'nın sayısal değeri doğrulanamadı.)
- Jaumé & Sykes (1999), PAGEOPH 155, "Evolving Towards a Critical Point: A Review of Accelerating Seismic Moment/Energy Release Prior to Large and Great Earthquakes" — [DOI](https://doi.org/10.1007/s000240050266).
- Bowman, Ouillon, Sammis, Sornette & Sornette (1998), JGR 103, "An observational test of the critical earthquake concept" — [DOI](https://doi.org/10.1029/98jb00792). Kritik bölge yarıçapının ana şok büyüklüğüyle ölçeklenmesi log R ∝ 0.44M olarak raporlanır (katsayı yaygın biçimde atfedilir; bu oturumda tam metinden doğrulanamadı). Bu, M7 için yüzlerce km mertebesinde bir bölge demektir.
- Hardebeck, Felzer & Michael (2008), JGR 113, "Improved tests reveal that the accelerating moment release hypothesis is statistically insignificant" — [DOI](https://doi.org/10.1029/2007JB005410). Zaman, alan ve büyüklük aralığı en güçlü AMR'yi verecek biçimde optimize edildiğinde, sinyal olmasa da AMR bulunur. Aynı verilerde (Kaliforniya–Nevada M≥6.5, 2004 Sumatra) hem AMR hem yavaşlayan boşalım uydurulabilir. Uzay–zaman kümelenmesi içeren sentetik kataloglar, AMR içermedikleri halde gerçek veriyle benzer AMR sinyali verir.
- Mignan (2011), Tectonophysics 505, "Retrospective on the Accelerating Seismic Release (ASR) hypothesis: Controversy and new horizons" — [DOI](https://doi.org/10.1016/j.tecto.2011.03.010). Özet OpenAlex'te yok. Bilinen içerik şudur: ASR'nin kritik nokta yorumu yerine, yükleme altında gerilme birikimine dayanan kritik olmayan açıklamalar önerilir. Bu içerik bu oturumda doğrulanamadı.
- Sonraki çalışmalar: yüksek gerilme bölgelerinde AMR testi (2013), GJI — [DOI](https://doi.org/10.1093/gji/ggt298); ASR fiziğine karmaşıklık bakışı (2018), Entropy — [DOI](https://doi.org/10.3390/e20100754); laboratuvarda kritik kırılma olmadan hızlanan boşalım (2018), PRL — [DOI](https://doi.org/10.1103/physrevlett.120.245501); büyük ölçekli heterojenliğin ASR'yi değiştirmesi (2023), PRE — [DOI](https://doi.org/10.1103/physreve.108.014131); Wellington için sentetik sismisiteyle AMR testleri (2006), JGR — [DOI](https://doi.org/10.1029/2005jb003720).

### Inferences
- Kuramın öngördüğü sinyal büyüklüğü (Benioff eğrisinin doğrusal fitten sapması, C parametresi) bir sınama istatistiği olarak tanımlıdır. Ancak t_f, m, R ve M_min gibi serbestlik dereceleri çok olduğundan etkin çoklu-test düzeltmesi ağırdır. Hardebeck ve ark.'nın ETAS-boş hipotezi, kuramın yerine geçebilecek "kümelenme yeterli" alternatifidir.
- Marmara için AMR'nin kritik bölgesi (M7.5 için yüzlerce km) Ege–Anadolu sismisitesinin geniş bir kısmını kapsar. Burada artçı dizileri (1999 İzmit–Düzce) ve ETAS boş modeli baskındır, dolayısıyla sınama gücü düşük olur.
- AMR, sonucu bilinmeyen bir t_f tahmini üretir. Belgelenmiş prospektif bir t_f isabeti bu taramada bulunamadı.

### Gaps
- AMR ve LPPL için CSEP tipi prospektif sınama raporuna rastlanmadı.
- Mignan (2011) tam metnine erişilmedi.

---

## 4. Natural time analizi, nowcasting (EPS), entropi/düzen parametresi; b-değeri gerilmeölçer olarak

### Takeaway
Natural time (κ₁ = 0.070 kritiklik koşulu) ve Rundle nowcasting (EPS) yaklaşımlarının ikisi de gözlemsel ve geriye dönük olarak savunulmuştur. Hiçbiri CSEP tipi, önceden kayıtlı (pre-registered) bir prospektif testten geçmemiştir. EPS kuramsal olarak "natural time"da bir yenilenme modelidir; bu nedenle bölüm 1'deki α sınırlamalarına aynen tabidir. b-değerinin diferansiyel gerilmeyle doğrusal azaldığı laboratuvar ve kabuk ölçeğinde kalibre edilmiştir. Ama b'deki değişimden ana şok öngören trafik ışığı sistemi, uzman kararlarına duyarlı bulunmuş ve tartışmalı kalmıştır.

### Cited Findings
- Natural time:
  - Tanımlar: χ_k = k/N, p_k = E_k/ΣE. Düzen parametresi κ₁ = Σp_kχ_k² − (Σp_kχ_k)². Kritik durumda κ₁ ≈ 0.070 olur. (Standart Varotsos tanımları; sayısal eşik bu oturumda tam metinden doğrulanmadı.)
  - Sarlis, Skordas, Varotsos, Nagao, Kamogawa & Tanaka (2013), PNAS 110 — [DOI](https://doi.org/10.1073/pnas.1312740110). Japonya kataloğu 1984–2011'de birkaç aylık kayan pencerede κ₁ dalgalanmasında, 27 yılda sığ M≥7.6 olayların hepsinden birkaç ay önce belirgin minimumlar bulundu. En derin minimum Tohoku öncesindeydi. "Öncül ve öncül olmayan iki tür minimum" vardı; yani yanlış alarmlar mevcuttu. Ayrıca bkz. 2011 EPL — [DOI](https://doi.org/10.1209/0295-5075/96/59002); 2022 Geosciences derlemesi — [DOI](https://doi.org/10.3390/geosciences12060225); küresel analiz (2022), Appl. Sci. — [DOI](https://doi.org/10.3390/app12157496).
- Nowcasting:
  - Rundle, Turcotte, Donnellan, Grant Ludwig, Luginbuhl & Gong (2016), Earth Space Sci. 3 — [DOI](https://doi.org/10.1002/2016ea000185). EPS = P(n < n(t)): son büyük olaydan beri sayılan küçük olay sayısının, büyük olaylar arası küçük olay sayılarının kümülatif dağılımındaki yeri. "Deprem çevrimi fikri dışında model içermez." En az ~20 büyük olay çevrimi gerekir.
  - Uygulamalar: megakentler (2017), PAGEOPH — [DOI](https://doi.org/10.1007/s00024-017-1720-x); Oklahoma/Geysers (2017), PAGEOPH — [DOI](https://doi.org/10.1007/s00024-017-1678-8); Bengal Körfezi (2018), PAGEOPH — [DOI](https://doi.org/10.1007/s00024-018-2037-0); Sulawesi (2021), Geosci. Lett. — [DOI](https://doi.org/10.1186/s40562-021-00197-5).
  - Rundle ve ark. (2021), Earth Space Sci., "Imaging the Earthquake Cycle in California With Machine Learning" — [DOI](https://doi.org/10.1029/2021ea001757). PCA tabanlı ağırlıklı korelasyon zaman serisi büyük olaylardan önce genellikle azalır, hemen sonra ani artar.
  - Geriye dönük test: "Earthquake Nowcasting: Retrospective Testing in Greece" (2023), Entropy 25 — [DOI](https://doi.org/10.3390/e25020379); yazarlar ve skorlar doğrulanamadı. ETAS kataloglarının bilgi entropisiyle nowcasting (2023 ön baskı) — [DOI](https://doi.org/10.22541/essoar.169826986.64908737/v1).
- b-değeri:
  - Scholz (2015), GRL 42, "On the stress dependence of the earthquake b value" — [DOI](https://doi.org/10.1002/2014GL062863). b = 1.23 ± 0.06 − (0.0012 ± 0.0003)(σ₁−σ₃) [MPa]. 100 MPa'lık diferansiyel gerilme artışı b'de yalnız ≈0.12 düşüş demektir.
  - Ayrıca Schorlemmer, Wiemer ve ark.'ın derinlikle b bağımlılığı (2012), GRL — [DOI](https://doi.org/10.1002/grl.50093) ve dayanım bağımlılığı (2024), Nat. Commun. — [DOI](https://doi.org/10.1038/s41467-024-49422-7). Wiemer & Wyss (1997), JGR, asperitelerde b haritalama — [DOI](https://doi.org/10.1029/97jb00726).
  - Gulia & Wiemer (2019), Nature 574 — [DOI](https://doi.org/10.1038/s41586-019-1606-4). Öncü/artçı ayrımı için b-değeri trafik ışığı: arka plana göre b düşerse "kırmızı", artarsa "yeşil". Eşik ±%10 olarak bilinir; özgün metinden doğrulanamadı.
  - Dascher-Cousineau, Lay & Brodsky (2020), SRL — [DOI](https://doi.org/10.1785/0220200082). Ridgecrest Mw6.4 dizisinde yüksek risk göstergesi bulundu, ama Mw7.1 artçılarının başlangıcı belirsiz tanımlandı. Sonuç uzman kararına güçlü biçimde bağlıdır; makul karar aralığında Monte Carlo yapıldığında sonuçlar dağılır. Yorum ve yanıt: [DOI](https://doi.org/10.1785/0220200428), [DOI](https://doi.org/10.1785/0220210059).
  - Geçici eksiklikte b tahmin yanlılığına karşı b-positive: van der Elst (2021), JGR — [DOI](https://doi.org/10.1029/2020jb021027); devamı (2024) — [DOI](https://doi.org/10.1029/2023jb027849).

### Inferences
- EPS, n(t)'nin büyük-olaylar-arası dağılımındaki yüzdeliğidir. Dolayısıyla "natural time"da geçen sürenin CDF'idir: geçen süreye göre monoton artar ve bölüm 1'deki yenilenme modellerinin özel bir hâlidir. Bilgi kazancı, n'nin büyük olaylar arası dağılımının CV'siyle sınırlıdır. Rundle ve ark. Weibull uydurmaları genellikle k≈1–1.5 olan, düşük periyodiklikli dağılımlar verir; bu tür dağılımda kazanç olay başına ≈0–0.3 nat'tır (bkz. tablo; uydurulmuş k değerleri bu oturumda doğrulanamadı).
- Scholz kalibrasyonuyla, bir sismik çevrimde gerilme birikimi tipik olarak ≲10 MPa düzeyindedir (gerilme düşümü mertebesi). Bu, Δb ≈ 0.01 demektir ve tipik b kestirim hatasının (n=100–1000 olay için ±0.05–0.1, Aki formülü b/√n) çok altındadır. Dolayısıyla b'nin "çevrim içi saat" olarak kullanılması kuramsal olarak sinyal/gürültü bakımından sınırlıdır. Gulia–Wiemer'in büyük Δb'leri (~%10–20) çevrim içi birikimden değil, yerel gerilme düzenlenmesinden (ana şok sonrası boşalım) kaynaklanıyor olmalıdır. (Bu hesap bu nota aittir.)
- Natural time minimumları için yanlış alarm oranı ve Molchan eğrisi PNAS 2013'te nicel olarak özetlenmemiştir. Japonya için büyük olay sayısı (M≥7.6, ~10) ile ayırt etmek için gereken N, ancak yanlış alarm oranı biliniyorsa hesaplanabilir.

### Gaps
- Natural time veya EPS için CSEP/pyCSEP altında önceden kayıtlı bir prospektif test bulunamadı. Mevcut testler geriye dönük ya da yazarların kendi uygulamalarıdır.
- Gulia & Wiemer'in özgün eşikleri ve başarı oranları tam metinden doğrulanamadı.

---

## 5. Uzun bellek, süper çevrimler ve uzun vadeli kümelenme: tehlike fonksiyonunun biçimine etkisi

### Takeaway
Kagan & Jackson (1991) büyük sığ depremlerin zamanda yarı-periyodik değil kümeli olduğunu (CV>1) öne sürdü; bu, çevrim sonunda azalan bir tehlike demektir. Salditch ve ark.'ın (2020) Uzun Vadeli Fay Belleği (LTFM) modeli ise olasılığı geçen süreye değil birikmiş (boşalmamış) gerinime bağlar. Böylece süper çevrimler ve kümeler aynı çerçevede açıklanır. Sonuçta tek bir fayın tehlike fonksiyonunun biçimi (artan mı, azalan mı) yalnız son olayın tarihinden değil, birkaç çevrimlik kayma geçmişinden belirlenir.

### Cited Findings
- Kagan & Jackson (1991), GJI 104, "Long-Term Earthquake Clustering" — [DOI](https://doi.org/10.1111/j.1365-246x.1991.tb02498.x). Uzun vadeli kümelenme ve boşluk hipotezine karşı argüman (özet alınamadı; bu klasik sonuç bu oturumda tam metinden doğrulanmadı).
- Salditch, Stein, Neely, Spencer, Brooks & Agnon (2020), Tectonophysics 774, 228289, "Earthquake supercycles and Long-Term Fault Memory" — [DOI](https://doi.org/10.1016/j.tecto.2019.228289); düzeltme — [DOI](https://doi.org/10.1016/j.tecto.2020.228700). Özet alınamadı. Bilinen içerik: olasılık, birikmiş gerinimin bir fonksiyonudur ve bir deprem gerinimin yalnız bir kısmını boşaltır. Bu nedenle çevrimler arası bellek, süper çevrim ve kümelenme oluşur. Bu içerik kaynaktan doğrulanamadı.
- Süper çevrim kanıtları (Türkiye'den): 2023 Mw7.8 Kahramanmaraş'ın çok segmentli kırılması bin yıllık süper çevrim bağlamında (2023), Commun. Earth Environ. — [DOI](https://doi.org/10.1038/s43247-023-01030-x); Doğu Anadolu Fayı'nda kayma kanalizasyonu ve süper çevrim (2024), Nat. Commun. — [DOI](https://doi.org/10.1038/s41467-024-53234-0). Kamçatka M9 sınıfında kısa yinelenme ve aşma (overshoot) (2025), Seismica — [DOI](https://doi.org/10.26443/seismica.v4i2.2012).
- Komşu segmentlerin yinelenme örüntüsünü denetlemesi (ölçekli analog modeller, 2025), GRL — [DOI](https://doi.org/10.1029/2024gl114002). Orta Apenin benzetim kataloglarında çevrim değişkenliği (2026), GJI — [DOI](https://doi.org/10.1093/gji/ggag378).

### Inferences
- LTFM'de Marmara gibi bir fayın tehlikesi, son tarihsel kırılmaların ne kadar kayma boşalttığına bağlıdır. Paleosismik kayma miktarları belirsiz olduğundan, LTFM tehlike oranı BPT'ye göre hem daha yüksek hem daha düşük olabilir. Bu belirsizlik, kazancı daha da düşürür.
- Kümelenme (CV>1) ile yarı-periyodiklik (CV<1) ayrımı, tek bir fayda ancak çok sayıda paleosismik olayla yapılabilir. Hurst/uzun bellek kestirimleri tek fay ölçeğinde (n<20) istatistiksel güçten yoksundur.

### Gaps
- Hurst üssü ve büyük olaylarda uzun bellek üzerine tek fay ölçeğinde nicel çalışma bu taramada bulunamadı.
- LTFM'nin olay başına bilgi kazancı (nat) için yayımlanmış bir değer bulunamadı.

---

## 6. Modellerin birleştirilmesi ve zayıf bir öncünün sınanması için güç analizi

### Takeaway
Log-doğrusal (çarpımsal) birleştirmede, bağımsız bilgi taşıyan öncülerin kazançları yaklaşık olarak toplanır; doğrusal birleştirme (Bayesçi model ortalaması) ise kazancı en iyi modelinkinin altında tutar. Olay başına I nat kazançlı ve olay başına log-oran standart sapması s olan bir öncüyü ayırt etmek için N ≈ (2.8·s/I)² hedef olay gerekir. I=0.1 nat ve s≈1 için bu ≈780 olaydır. Marmara ölçeğinde M7+ hedefiyle böyle bir test olanaksızdır; testler daha küçük büyüklük ve geniş bölge gerektirir.

### Cited Findings
- Rhoades, Schorlemmer, Gerstenberger, Christophersen, Zechar & Imoto (2011), Acta Geophysica 59, "Efficient testing of earthquake forecasting models" — [DOI](https://doi.org/10.2478/s11600-011-0013-5). Olay başına bilgi kazancı I_N(A,B) = (1/N)Σ[ln λ_A(i) − ln λ_B(i)] − (N̂_A − N̂_B)/N ve bunun t-testi. Formül literatürde standart biçimdedir; tam metin kapalı olduğundan doğrulanamadı.
- Marzocchi, Zechar & Jordan (2012), BSSA 102, "Bayesian Forecast Evaluation and Ensemble Earthquake Forecasting" — [DOI](https://doi.org/10.1785/0120110327). Bayes faktörleri; sonsal olasılıklar ya da ters log-olabilirliklerle ağırlıklandırılmış ortalamalar; model korelasyonu için Garthwaite–Mubwandarikwa sınırlı özdeğer şeması; RELM 5 yıllık deneyine uygulama.
- Herrmann & Marzocchi (2023), GJI, "Maximizing the forecasting skill of an ensemble model" — [DOI](https://doi.org/10.1093/gji/ggad020). Çok değişkenli lojistik regresyonla topluluk becerisini maksimize eden ağırlıklar. İtalya OEF'de en iyi tek modele göre istatistiksel olarak anlamlı üstünlük sağlanır; yalnız yakın tarihli verinin kullanılması beceriyi artırır.
- Shebalin, Narteau, Zechar & Holschneider (2014), EPS 66, "Combining earthquake forecasts using differential probability gains" — [DOI](https://doi.org/10.1186/1880-5981-66-37). Yeni hız = başlangıç hızı × yerel diferansiyel olasılık kazancı. EEPAS+EAST birleşimi, Temmuz 2009–Aralık 2011 test döneminde (19 hedef olay) her iki modelden de iyidir (Molchan ve olabilirlik açısından).
- Rhoades ve ark. (2014), BSSA 104, "Regional Earthquake Likelihood Models II: Information Gains of Multiplicative Hybrids" — [DOI](https://doi.org/10.1785/0120140035). Kaliforniya'da çarpımsal hibritlerin prospektif değerlendirmesi (2022), GJI — [DOI](https://doi.org/10.1093/gji/ggac018). Canterbury hibrit OEF retrospektif testleri (2015), GJI — [DOI](https://doi.org/10.1093/gji/ggv447). Hibrit kazanç değerleri bu oturumda doğrulanamadı.
- Araç: pyCSEP (2022), SRL — [DOI](https://doi.org/10.1785/0220220033). Aşırı olaylarda tahmin değerlendirmesi tuzakları için "Forecaster's Dilemma" (2017), Statistical Science — [DOI](https://doi.org/10.1214/16-sts588).

### Inferences
- Güç analizi (türetme): tek yönlü %5 düzeyi ve 0.8 güç için N ≈ ((1.645+0.84)·s/I)² ≈ (2.5·s/I)². İki yönlü %5 için ≈ (2.8·s/I)². Bir yenilenme modeli için hesaplanan s≈0.5 (α=0.5) ve I≈0.44 ile N≈11 olur (bölüm 1). Zayıf bir öncü (I=0.05–0.1 nat) için s≈0.5–1 alınırsa N≈150–3000 hedef olay gerekir.
- Log-doğrusal birleştirmede λ = λ₀ Π fᵢ^{wᵢ}. Eklenen öncünün koşullu kazancı yalnız mevcut modelde olmayan bilgiye (koşullu karşılıklı bilgi) eşittir. Örneğin EPS ile BPT aynı "geçen süre" bilgisini taşıdığı için ikisinin çarpımı ek kazanç getirmez.
- Marmara için gerçekçi birleşik model şu bileşenlerden oluşur: (a) yenilenme/LSRM (on yıllar ölçeğinde 1.5–3 kat), (b) ETAS kısa vadeli kümelenme (günler–haftalar ölçeğinde olayların küçük bir kesrinde yüksek kazanç), (c) EEPAS orta vade (yıllar). Kuramsal olarak bunlar toplanabilir, ancak (a)'nın doğrulanması tek bir fayda olanaksızdır; (b) ve (c) daha küçük olaylarda ve geniş bölgede sınanabilir.

### Gaps
- Topluluk modellerinin M7+ için olay başına kazancına ilişkin prospektif bir değer bulunamadı. Prospektif CSEP testlerinde hedef olaylar genellikle M≥4.95 (RELM) ve benzeridir.

---

## Sınanabilir kuramsal öngörüler

Durum etiketleri:
- **[0 € şimdi]**: açık veri ve araçlarla hemen sınanabilir.
- **[yeni veri]**: yeni gözlem, paleosismoloji ya da zaman gerekir.
- **[sınanamaz]**: pratikte sınanamaz.

| # | Nicelik | Öngörülen büyüklük (kuram) | Zaman ölçeği | Gereken veri | Açık veri var mı? | Durum |
|---|---|---|---|---|---|---|
| 1 | Bilinen parametreli BPT'nin Poisson'a göre olay başına bilgi kazancı | 1−H(f): α=0.3→0.85, α=0.5→0.44, α=0.7→0.24 nat (hesap, §1) | Analitik | Yok (sayısal integral); ayrıca küresel paleosismik aralık derlemeleri | Evet (SciPy; derlemeler kısmen açık) | [0 € şimdi] (analitik); havuzlanmış fay testi [0 € şimdi], sınırlı |
| 2 | tₑ≈μ'de tehlike oranı h/(1/μ) | α=0.5→~2, α=0.3→~3; tₑ≲1.1μ'ye kadar BPT, LN ve Weibull farkı <%25 | On yıllar | Segment bazında olay tarihleri | Kısmen (yayımlanmış paleosismik/tarihsel katalog) | [sınanamaz] tek fay için; çok fay havuzunda [yeni veri] |
| 3 | Yıl ölçeğinde (%90 penceresi ≈2 yıl) zamanlamanın gerektirdiği α | α ≈ 2 yıl/(2μ); μ=250 yıl için ≈0.004 (hesap) | Analitik | Yok | — | [0 € şimdi] (analitik sonuç; gözlenen α≈0.3–0.7 ile çelişki zaten açık) |
| 4 | Gecikmiş fayda beklenen kalan süre davranışı | BPT: platoya 2α²μ; LN: tₑ≳1.5μ'den sonra artar; Weibull k>1: azalır (Sornette & Knopoff 1997) | Yüzyıllar | Çok sayıda çevrim | Hayır (tek fay) | [sınanamaz] |
| 5 | Yenilenme modelinin Poisson'u t-testiyle yenmesi için gereken olay sayısı | α=0.5'te N≈11; α=0.7'de N≈22 (bilinen parametreyle alt sınır) | Tek fayda yüzyıllar–binyıllar | Prospektif M7+ olaylar | Hayır | [sınanamaz] tek fay; küresel fay havuzunda [0 € şimdi] (Rong 2003 ve Kagan 2012 tarzı) |
| 6 | Molchan optimal alarm (BPT, t>t₀) | α=0.5, t₀=μ: τ≈0.19, n≈0.59, kazanç≈2.2; α=0.3: kazanç≈3.8 | On yıllar | Çok fayda olay tarihleri | Kısmen | [0 € şimdi] havuzlanmış; tek fay [sınanamaz] |
| 7 | ETAS öncü özelliklerinin ana şok büyüklüğünden bağımsızlığı (Helmstetter & Sornette 2003) | Öncü sayısı, ivmelenme üssü ve göç, Mm'den bağımsız | Günler–aylar | Bölgesel yüksek çözünürlüklü katalog (Türkiye: AFAD/KOERI; küresel: ISC, ComCat) | Evet | [0 € şimdi] |
| 8 | Magnitüd korelasyonlu ETAS'ın (Nandan 2019/2022) basit ETAS'a göre büyük olaylarda kazancı | Yarı-prospektif olarak anlamlı üstünlük (büyüklük değeri doğrulanamadı) | Günler–yıllar | Uzun, homojen katalog; pyCSEP | Evet | [0 € şimdi] (Marmara/Ege için yarı-prospektif tekrar yapılabilir) |
| 9 | EEPAS Ψ ölçekleme ilişkileri (Mm–M_P, T_P, A_P) | Mm≈M_P+~1 (doğrulanamadı); M7 için T_P yıllar–on yıllar | Yıllar | Uzun bölgesel katalog | Evet (Türkiye katalogları, ISC) | [0 € şimdi] (Christophersen 2024 algoritmaları ve ETAS kontrolüyle) |
| 10 | AMR/LPPL kritik bölgede Benioff hızlanması | ε=A+B(t_f−t)^m, m≈0.3; log R∝~0.44M (doğrulanamadı) | Yıllar–on yıllar | Katalog + ETAS boş modeli (Hardebeck 2008) | Evet | [0 € şimdi] (önceden kayıtlı parametre seçimiyle; geçmiş testler anlamsız) |
| 11 | Natural time κ₁ minimumu → M≥7.6 öncesi aylar | Japonya'da tüm olaylardan önce minimum, artı yanlış alarmlar (Sarlis 2013) | Aylar | Bölgesel katalog | Evet | [0 € şimdi] (Molchan eğrisiyle, önceden kayıtlı pencere; Marmara'da M7 olmadığından ancak daha geniş bölge ve küçük hedeflerle) |
| 12 | Nowcasting EPS'nin bilgi kazancı | Natural time'da yenilenme; kazanç ≤ BPT/Weibull sınırı (k≈1–1.5 için ~0–0.3 nat; k doğrulanamadı) | Yıllar–on yıllar | ≥20 büyük olay çevrimi (bölgesel) | Evet (küresel katalog) | [0 € şimdi] (geniş bölge, pyCSEP) |
| 13 | b-değerinin diferansiyel gerilmeyle değişimi | db/dΔσ = −0.0012/MPa (Scholz 2015); çevrim içi ≲10 MPa → Δb≈0.01 | Çevrim (yüzyıllar) | Derinlik/bölge b haritaları | Evet | [0 € şimdi] (kalibrasyon); çevrim içi saat olarak [sınanamaz] (Δb < kestirim hatası) |
| 14 | b trafik ışığı (Gulia & Wiemer 2019) ile öncü/artçı ayrımı | Sonrası dizilerde b düşüşü→kırmızı (eşik ±%10, doğrulanamadı) | Günler | M≥6 dizileri, b-positive | Evet | [0 € şimdi] (önceden kayıtlı kurallarla; Dascher-Cousineau 2020 uzman kararı duyarlılığı gösterdi) |
| 15 | LSRM'de segmentler arası etkileşim katsayıları θᵢⱼ'nin işareti (KAF segmentleri) | θ<0 aktarım / θ>0 inhibisyon; KAF 1939–1999 göçü aktarımla uyumlu olmalı | On yıllar–yüzyıllar | Tarihsel katalog (M≥6.5, ~2000 yıl) | Kısmen (yayımlanmış tarihsel kataloglar) | [0 € şimdi] (geriye dönük uydurma); prospektif [sınanamaz] |
| 16 | LTFM: tehlike birikmiş gerinime bağlı | Çevrimler arası bellek; azalmayan tehlike geçmiş kaymaya bağlı | Yüzyıllar–binyıllar | Olay başına kayma miktarları (paleosismik) | Kısmen | [yeni veri] |
| 17 | Zayıf öncünün (I nat/olay) anlamlılığı için gereken hedef olay sayısı | N≈(2.8·s/I)²; I=0.1, s=1 → ~780 | — | Prospektif kayıtlı tahminler | — | [0 € şimdi] (güç hesabı); M7+ Marmara hedefiyle [sınanamaz] |
| 18 | Log-doğrusal topluluklarda kazançların toplanabilirliği | Koşullu bağımsızlıkta I_toplam ≈ ΣIᵢ; EPS+BPT ek kazanç ≈0 | — | pyCSEP + birden çok model | Evet | [0 € şimdi] |
