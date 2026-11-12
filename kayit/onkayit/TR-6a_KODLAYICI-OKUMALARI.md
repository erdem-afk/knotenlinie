# TR-6a kodlayıcı okumaları (Ek 1 adayı)

Bu dosya, TR-6a ön kaydı sürüm 3'ün (`TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md`, sha256
41ca1e951d330ab72d106be79bb5f700b415d9574dbddff3da0a12ad73fea94e) koşu kodunu yazarken metnin açık bıraktığı ya da iki
türlü okunabilen yerlerde kodun hangi okumayı uyguladığını yazar. Öncelik: sürüm 3 > İNCELEME-2 > İNCELEME-1 >
TR-6_SAYIM.md. Kural: en dar / en tutucu okuma. Metin değiştirilmedi. Kök oturum bunları "Ek 1" olarak kaydeder;
**"KARAR GEREKİR"** işaretli maddelerde kod karar vermez, ilgili aşamada durur.

Kod: `kayit/turetme/tr6/` altında `tr6a_okada.py`, `tr6a_ffm.py`, `tr6a_katalog.py`, `tr6a_kosu.py`, `tr6a_yapay.py`,
`tr6a_test_yapay.py`. Kod içindeki "okuma N" göndermeleri bu numaralardır.

## A. Dosyalar ve Okada (§3.3)

1. **Dosya adları.** Görev metnindeki dört dosyaya ek olarak yapay dünya `tr6a_yapay.py`'dedir (sınama dosyası ile
   koşu kodunun ortak kullandığı yapay kaynak). Çıktılar: `tr6a_sinama_sonuc.json`, `tr6a_manifest.json`,
   `tr6a_on_ham_sha256.txt`, `tr6a_son_ham_sha256.txt`, `tr6a_sonuc.json/.md`; kod incelemesi
   `kayit/onkayit/TR-6a_KOD-INCELEME.md` (son indirmeden önce commit edilmiş olmalı, okuma 34).
2. **Okada 1992 tablo değerleri.** Tablo 2 değerleri elde yoktu; DC3D/DC3D0 bellekten yazıldı. Bir terim (UC0, açılma,
   UYZ) ∂/∂z tutarlılığını bozuyordu; katsayı UC0[9:12] = ∂u/∂z koşulundan sayısal türevle 1e-10 içinde belirlendi.
   Sınama sonucunda durum "Okada 1992 tablo değerleri doğrulanamadı" diye yazılır.
3. **KARAR GEREKİR — §3.3 sınamaları 3, 5 (uzak alan) ve 6 harfi harfine tutmuyor.** Ölçülen: 3 (kayma süreksizliği)
   6,3e-6 > 1e-6; 5-uzak (20L) 3,6e-3 > 1e-3; 6 (fay dışı süreklilik) 8,6e-6 > 1e-6. Tanılar kodun doğru olduğunu
   gösteriyor (okuma 5, 6). Metne göre Okada sınaması tutmazsa "koşulmadı (yöntem: Okada sınaması)". Kod bu kararı
   vermez: `tr6a_kosu.OKADA_EK1_KARAR = None` iken manifest aşaması açılmaz. Kök oturum ya ölçütün tanı biçimini
   (Richardson / 40L genel normal) Ek 1'de bağlayıcı kılar ya da TR-6a'yı bu adla kapatır.
4. **Sınama 5 (nokta kaynak, 0,01 km):** sınama noktaları kaynaktan ≥ 1 km uzakta seçilir (metin noktayı
   söylemiyor; yakın alanda sonlu/nokta farkı tanım gereği büyüktür). Tuttu.
5. **Sınama 3 ve 6 tanısı:** harfiyen ±ε farkı doğrusal terim 2ε ∂u/∂n taşır; Richardson 2Δ(ε) − Δ(2ε) ile 3: 6e-15,
   6: 1,7e-14. Bilgi olarak yazılır; bağlayıcı değildir (okuma 3).
6. **Sınama 5 uzak alan tanısı:** fark sonlu boyut (dört kutup) terimidir, (L/r)² ile azalır; 20–60L genel normalle
   ve 40L'de ayrıca yazılır; 20×20 nokta kaynak toplamı ile karşılaştırma bilgi satırıdır.
7. **Hücre dizini:** AEQD izdüşümünde dış merkez (0, 0) bir hücrenin merkezidir; hücre (i, j) merkezi (i·10, j·10) km.
8. **Doğrultu izdüşümü:** coğrafi doğrultu, alt fay merkezinden doğrultu yönünde küçük bir adımın izdüşümüyle düzleme
   taşınır (AEQD'de kuzey her yerde "yukarı" değildir).
12. **Sayısal biçim:** R + ξ, R + η (ξ, η < 0) ve R + d (d < 0) iptal kaybını önlemek için (R² − ξ²)/(R − ξ) biçiminde
   hesaplanır. Okada'nın tekil durum kuralları (R + ξ = 0 vb.) aynen uygulanır; tekil hücreler loblardan çıkar.

## B. Sonlu fay ürünü (§3.3, İNCELEME-2 K9)

9. **KARAR GEREKİR — alt fay koordinatının anlamı.** basic_inversion.param / .fsp başlığı koordinatın alt fay merkezi mi
   üst kenar mı olduğunu söylemiyorsa kod tahmin etmez: `tr6a_ffm.KOORDINAT_KARARI = None` iken BicimHata ile durur
   (veri yok sayılmaz). Seçenekler "merkez" | "ust_kenar".
10. **KARAR GEREKİR — "başlıktaki M0".** param başlığında M0 yoksa `M0_KAYNAGI_KARARI` ("fsp_basligi": aynı ürünün .fsp
   başlığındaki Mo) verilmedikçe BicimHata.
11. **Birimler:** param kayma cm, moment dyn·cm; .fsp kayma m, moment N·m. Satır başına ima edilen μ [5, 100] GPa dışına
   çıkarsa BicimHata (birim kayması ΔCFF'yi 100 kat bozardı). Ürün seçimi: ComCat'in tercih ettiği (ilk) ürün; öteki
   ürünler manifestte yazılır. Sonlu fay okunamazsa (VeriYok, BicimHata, OkadaHata) olay grubunda R_A hesaplanmaz
   (None) ve o birim "veri yok" olur; BicimHata manifest aşamasını durdurur (okuma 31).

## C. Olay seçimi ve kataloglar (§3.2, §3.5, §5)

13. **Ana şokun katalogdaki kendi satırları:** t0 ± 16 s, dış merkezden ≤ 100 km ve M ≥ 5,5 olan satırlar ana şokun
   kendi kaydı sayılır (kataloglar arası saat/konum farkı); kümesizleştirmede ana olay olarak tutulur, sayılmaz.
20. **"Bölge"** tekil hücreleri de içerir (Mc_son bölgenin bütün hücrelerinden hesaplanır, §3.5); tekil hücreler
   yalnız loblardan çıkarılır.
30. **KOERI satır sınırı:** KOERI gün çözünürlüklü olduğundan yarılama gün sınırında yapılır; 1 günlük parçada yarı
   eşitliği denetlenemezse VeriYok.
31. **Biçim hataları:** beklenmedik yanıt biçimi (ayrıştırıcı, sayım, birim) koşuyu durdurur; veri yok sayılmaz.
32. **VeriYok:** olay öncesi indirmede VeriYok → o birim "veri yok" (manifestte yazılır, kapıya girmez). Olay sonrası
   indirmede VeriYok → koşu durur (`KosuDur`); §5 madde 1 kök oturumda karara bağlanır (sessiz düşürme yok).
33. **Tercih edilen moment tensörü:** ComCat ayrıntısındaki ilk (tercih edilen) moment-tensor ürünü.
36. **Bölünmüş indirme ve günlük:** her istek `ham/yanit_gunluk.jsonl`'a (url, sha256, dosya) yazılır; aynı ham dizinle
   yeniden çağrıda günlükteki URL'ler yeniden istenmez (sha256 doğrulanır). Bu yalnız indirmeyi parçalara böler;
   seçim, kapı ve manifest tek bir son çağrıda hesaplanır.

## D. Yapay sınamalar (§9 adım 2)

14. **Yapay katalog sınaması kurgusu:** tek birim (M 7,8; bilinen yapay sonlu fay, bilinen alıcı), lobda saf Poisson,
   bölgede GK tipi ikincil diziler; N0 ∈ {31,36; 100; 500}. Kod yolunun tamamı (Okada → loblar → katalog → GK →
   Mc → oy) koşulur; kestirme yok.
15. **(i) ölçütü:** Δτ = 0'da P(D), kesin Poisson H0 değeriyle, binom SE'nin 3,5 katı içinde; kapıdan koşullu değer
   bilgi satırıdır. −10 kPa satırında P(D) ve Δτ_est medyanı (medyanın altındaki pay 0,5'e karşı) ayrıca.
16. **Kalıcı adım:** −10 kPa satırı t_a → ∞ (tablonun ilk satırı) ile koşulur.
17. **(ii) ölçütü:** Δτ = 0 dünyasında p̂₀'ın beklenen değeri (ΣS/ΣJ) − kapıdan geçen denemelerde gerçek P(D);
   SE ikisinin birleşik SE'si (S − p̂₀J'nin oran kestiricisi SE'si ve binom SE).
18. **Tamlık sınamasında bölge büyüklüğü (metin söylemiyor).** Bölge arka planı = lob arka planı (`bolge_carpani = 1`),
   artçılar bölgede, payı ap. Mc_lob ve Mc_son koddaki işlevlerle (MAXC, alt pencere birleştirme, 50 olay kuralı,
   Mc_lob + 0,3 yedeği) hesaplanır. **Not (bkz. Risk 1):** §3.5'in "50'den az → Mc_lob + 0,3" yedeği, gürültüsüz ön
   denetimde (`tr6a_inc1_denetim.py`) modellenmemişti. M 9, Mc_lob 1,0, ap 0 hücrelerinde Mc(t) yıl boyunca 2,6–3,4'tür;
   bölgede bu büyüklüğün üstünde 50 olay toplanmaz, yedek Mc_kul'u 1,3'e bırakır, n_son ≈ 0 olur ve düşüş oyu ≈ 1'dir
   (fark +0,54). Bu, bölge çarpanı 30 iken de sürer. Geliştirme koşularında hiçbir basamak (A2, a, b, c) tutmadı.
19. **Tamlık sınamasında kümesizleştirme yok:** lob saf Poisson arka plandır (metin "lobda arka plan saf Poisson");
   artçılar yalnız bölge histogramına girer ve sayılmaz.
- Bağlayıcı tohumlar (20261114, 20261115) geliştirmede kullanılamaz (kod reddeder); her basamak bir kez koşulur.

## E. Mc, pencereler ve satırlar (§3.5, §3.7, §7)

21. **Mc_son yedeği:** "Mc_lob + 0,3" gölge lobunun Mc_lob'udur (pozitif ve nötr lob aynı Mc_son'u kullanır). S1 ve S7
   ana koşunun Mc_son'unu kullanır.
22. **S6:** SRCMOD erişimi ve kapsamı doğrulanmadı; S6 "koşulamadı" yazılır.
23. **S2 (negatif kontrol):** Mc_lob ve Mc_son S2'nin kendi pencerelerinden (alt pencereler t0 − 395 g + (t_s − t0)'dan);
   S2 için gereken katalog t0 − 395 g'den itibaren ön indirmeyle gelir; yalnız tam geçerli j = 1 penceresi.
24. **D1** kapısı Mc_lob + 0,5 ile yeniden hesaplanır.
25. **D2, D3, D5, D8** ana Mc_son'u kullanır (yeniden kestirilmez).
26. **D5:** öteki (yardımcı) düğüm düzlemi alıcı alınır; lob, kapı ve oy yeniden kurulur.
27. **D6 kümesi:** ana kapıdan geçen birimler + ISC kuralıyla (A4) ana hükümden düşen ve ISC ile kapıdan geçen
   birimler (bunlar ISC ile sayılır); küme kuralı yeniden uygulanır.
28. **Satır kapıları** ana katalog seçimini korur (satır başına yeniden katalog seçilmez).
29. **Medyan bölme:** ≤ medyan / > medyan.
35. **§3.7 kesmesi ve B3 bayrağı** kırık izine yatay uzaklıkla (r_k), öncül komşu ise dış merkez uzaklığıyla.
37. **Spearman:** bağlarda ortalama sıra.
38. **Yedek (c) seçilirse** §3.7 kesme penceresinin kendisi değişmez; yalnız T_son < 60 g ölçütü yeni başlangıçla
   uygulanır.
39. **Etkin N0 ölçütü:** "K'nin yarısından fazlası" kesin büyüktür (> K/2).

## F. Hüküm ve koşu disiplini (§6.4, §9)

34. **Kod incelemesi** (`TR-6a_KOD-INCELEME.md`) commit edilmeden `son-indir` aşaması açılmaz.
40. **Hüküm adı biçimi** (§6.4 kapalı liste): "H1 (q1; q2)", "ayırt edilemez (d1; d2)", "H0 — e1; e2",
   "koşulmadı (yöntem: …)", "güç yok", "güç yok (ölçü yanlı)". Niteleyiciler parantezde "; " ile, ekler "—" sonrası.
   Testler 10 000'den fazla bileşimin kapalı dilbilgisinde kaldığını denetler.
41. **Git denetimi:** "push edilmiş" yerel upstream ref'i (`@{u}`) ile denetlenir (`merge-base --is-ancestor`); kod ağa
   çıkıp fetch etmez; commit/push yapmaz.
- **Kuru prova** (§9): olay sonrası yerine olay öncesi pencereden yeniden örneklenmiş yapay veriyle; ardından anlık
  görüntü ve iki işaret dosyası "x" kipinde yazılır; ikinci gerçek koşu açılmaz (`--devam` yalnız yarıda kalanı sürdürür).
- İstanbul/Marmara için mutlak olasılık yazılmaz; §13 satırı yalnız metindeki kalıpla.
