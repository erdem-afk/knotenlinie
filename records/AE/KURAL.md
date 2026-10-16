# AE — hesap öncesi sabit kural (hiyerarşik büzülme)

Yazıldı 2026-10-12. O sırada hiçbir cezalı İtalya ayarı kurulmamış, 2006–2010 ya da 2011–2015 AE puanlaması yapılmamıştı.
Bölge çekirdek ayarları (SCSN, GeoNet, İtalya 1985–2004) kurulmuştu ve bakılmıştı; hepsi dallanma tavanında çıktı
(n = 0,999999). Sonradan değişmez; gerekirse puanlamadan önce tarihli "Ek".

**Çerçeve.** J/R çerçevesi: CSEP İtalya 8993 hücre, [0,30) km, HORUS-Mw, günlük, 0,1 M kutuları 2,95'ten, son kutu +∞.
Seçim ≤2005 ayar ve çekirdekle; seçilen ≤2010 ayar ve çekirdekle yeniden kurulur, 2011–2015'te bir kez puanlanır.

**Model.** Cezalı olabilirlik: −logL_R(v) + Σ_k∈maske (g_k(v) − çekirdek_k)² / (2τ²). logL_R, R-ortak-kaskad MLE'sinin olabilirliğidir
(`tools/etas_uzun/mle.py::Olabilirlik`; ≤2005: S'nin kurulumu, ≤2010: R'nin; KDE, b, Mc(t) aynen). τ = ∞ cezasızdır ve R'dir
(R'nin kayıtlı x'inde logL özdeşliği koşudan önce doğrulanır). Kaskad, çekirdek ve tahmin R ile aynıdır; yalnız parametreler değişir.

**Karşılaştırılabilir parametreler.** g = (log K_ref, log c, log α, log p, log D_ref, log q, log(γ + 0,05)); K_ref = K·10^{α(M_ref−Mc0)},
D_ref = D·10^{γ(M_ref−Mc0)}, **M_ref = 3,5**, Mc0 = bölgenin referans büyüklüğü (İtalya R için 2,5). Zaman gün, uzay km. μ büzülmez.

**Çekirdek ayarları** (`tools/etas_hiyerarsi/bolge.py`; R-tipi = dönem Mc'li, kesmeli; `tools/yan_tezgah` kopyası): SCSN (1996'dan; 100 km,
365,25 gün kesme), GeoNet (2002'den; 100 km). [Yayın notu: AE'nin
kayıtlı sayıları bu sürümün verisiyle birebir yeniden üretilemez.] Dönem yapısı yalnız ayar
verisinden kurulur: ≤2005 için olaylar < 2006-01-01, ≤2010 için < 2011-01-01. SCSN/GeoNet dosyaları (≤2020 geliştirme verisi) okunur ama ayar sınırından önce süzülür.
SCSN ≤2010 ayarı
yerel makinede ~3,5 dakika sürdü; kaynak kuralı "SCSN'i ≤2010'a sınırla" tetiklenmedi, her iki aşamada tam ayar kullanıldı.
Bölge belirsizliği: gözlenen bilginin (toplam logL Hessian'ı, analitik gradyanın merkezi farkı) tersi; delta yöntemiyle g'nin varyansı.
Zaman-havuzu çekirdeği: İtalya'nın kendi **1985–2004, Mc 3,1** ayarı (`tools/etas_mc25` olabilirliği, CSEP maskesiz dış dikdörtgen
kompansatörü; KDE 1985–2004'ün ilk yarısı kurulum, ikinci yarısı seçim). İki aşamada da aynı, sabit çekirdektir.

**Çekirdek (varyant A).** Bileşen bileşen ters varyans ağırlıklı ortalama (log uzayında) bölge ayarlarının. **Önceden yazılı kapı:**
dallanma ≥ 0,999 çıkan ayar çekirdeğe girmez. **Gözlem (Ek, puanlamadan önce):** tüm bölge ayarları (ve İtalya 1985–2004)
dallanma tavanında (0,999999) çıktı; sıkı kapı çekirdeği boş bırakır ve A, B tanımsız olurdu. Tavanda K yalnız tavan kısıtıyla
belirlenir (K_ref bilgisizdir); öteki altı bileşen tavan koşullu profil kestirimidir. Bu yüzden Ek: **dallanma kapısı yalnız K_ref
bileşenine uygulanır** (K_ref penaltısı yok, K serbest); c, α, p, D_ref, q, γ bileşenleri yakınsayan her bölgeden alınır.
Sıkı sürüm "tanımsız" diye raporlanır; AE'nin tüm adayları bu Ek'in gevşek sürümüdür. Varyant B aynı K_ref kuralını kullanır.

**Adaylar (sabit, 11).** τ ∈ {0,05; 0,1; 0,2; 0,4; 0,8} × varyant {A (bölge çekirdeği), B (İtalya 1985–2004)} = 10 aday, artı τ = ∞ (R).
Sıcak başlangıç: R'nin x'i, sonra τ büyükten küçüğe aynı varyantta zincir; L-BFGS-B, R'nin sınırları ve toleransları, maksiter 300.

**Seçim.** ≤2005 ayar ve çekirdekle kurulan her adayın 2006–2010, M≥2,95 Poisson logL'i (log n! hariç) en büyük olanı. τ = ∞ aday olarak yer alır;
kazanırsa AE = R'dir ve raporda öyle yazılır. Seçilen (varyant, τ) ≤2010 ayar ve ≤2010 çekirdekle (A için ≤2010 bölge ayarları, B sabit)
yeniden kurulur, aynı sıcak zincirle; 2011–2015'te bir kez puanlanır. 2011–2015 sonucuna göre hiçbir şey değişmez.

**Ölçüm.** AE − ETAS-LM ve AE − R-ortak-kaskad, M≥2,95/3,95/4,95, U'nun ölçüm koduyla (`_satir`): N, Λ'lar, IG, IG_olay, integral, haftalık blok SE,
tek yönlü z, N/S/M. Hüküm satırı M≥3,95, ETAS-LM'ye karşı. **E6** = eşit ağırlıklı {AE, ETAS-LM}, − LM hüküm, − R yan satır; U'nun eşit {R, LM}
satırı yan yana. Holm yok (tek satır). Bileşen kabul kuralı: R'ye karşı M≥2,95'te IG>0 ve z>1,645, M≥3,95'te IG>0.
Parametre tablosu: R, AE, çekirdek (İtalya Mc0'ında doğal parametreler), ETAS-LM. Skor defteri `$KNOTENLINIE_RUNS/defter/AE/` (U biçimi, Lam495 dahil).

**Kayıt dışı.** Sonuç görüldükten sonra denenen her şey (başka τ, çekirdek, K_ref cezası vb.) `AE/EK-*.md`'de "kayıt dışı" diye durur ve hükmün yerine geçmez.
Sonuç PROVISIONAL: bağımsız skor-kodu incelemesi yok.
