DÜZELTMEDEN KOŞULAMAZ (tek engelleyici: Ek 1'in K = 42 cümlesi çıktıda yok; yaması küçük ve taraf bilgisi taşımıyor)

# TR-2 koşu kodu bağımsız incelemesi (isabet hesaplanmadan önce)

Tarih: 11 Kasım 2026. İncelenen commit: 2305994 (dal `claude/project-thread-hjup0f`).
Okunanlar: ön kayıt (Ek 1 dahil), `TR-2_SAYIM.md` §1, `tr2_sayim.py`, `tr2_manifest.py`, `tr2_etas.py`,
`tr2_kosu.py`, `tr2_test_yapay.py`, `tr2_manifest.csv`, `tr2_manifest_agirlik.csv`, `tr2_etas_p.csv`.

Körlük beyanı: `tr2_kosu.py` gerçek veride çalıştırılmadı. Gerçek veride hiçbir sonraki ya da önceki olayın
işaretli s değeri ya da isabeti hesaplanmadı, yazdırılmadı. Gerçek veride yalnız şunlar çalıştı: manifest ve ETAS
yeniden üretimi (bayt karşılaştırması), `sha_dogrula`, |A| = 1/3 sınır sayımı, u/L medyan eşitliği ve çift/öncü
olaylarının zaman ve uzaklığı (mutlak değerler). Bütün işaret sınamaları yapay veriyle yapıldı. Dosya, commit ve
`__pycache__` bırakılmadı; yalnız bu belge yazıldı.

## Sonuç özeti

İsabetin çekirdeği doğru. Sessiz taraf, s işareti, ETAS, eşikler, yorum kuralları, log skorlar ve bootstrap ön
kayıtla uyuşuyor. Manifest ve ETAS dosyaları anlık görüntüden bayt bayt yeniden üretildi. İşaret tersliği yok.
Uçtan uca yapay sınamada (ham dizin → `tr2_manifest.py` → `tr2_etas.py` → `tr2_kosu.py`) 3 tohum × 40 kümede
isabet ve isabet_ters hatasız. Bunlara tarih çizgisini aşan 15 küme ve 78° enlemde 24 küme dahil.

Tek engelleyici bulgu: Ek 1, sonuç yazılırken K = 42 okumasının hükmü değiştirip değiştiremeyeceğinin açıkça
yazılmasını şart koşuyor. `tr2_kosu.py` bunu üretmiyor. Elle eklemek mümkün, ama X görüldükten sonra çıktıyı
değiştiren her müdahale "koşu sonrası değişiklik" sayılır. Yaması 15 satır ve yalnız X'e bağlı. Koşudan önce
eklenmeli. Yama uygulanıp yapay sınama geçince kod KOŞULABİLİR.

## Engelleyici

### E1. Ek 1'deki K = 42 duyarlılık cümlesi çıktıda yok

`md_yaz` ve `hesapla` içinde K = 42 okuması, X ile X + 2 arası değerler ya da 27/23 eşikleri geçmiyor
(`grep 42` yalnız rastlantısal sayılar buluyor). Ek 1: "Sonuç yazılırken, gözlenen X için K = 42 okumasında
hükmün değişip değişemeyeceği (X ile X + 2 arasındaki her değer için) açıkça belirtilir; iki olayın isabeti
hesaplanmaz."

K = 42 eşikleri doğrulandı: P(X ≥ 27 | 42; 0,5) = 0,0442 ve P(X ≥ 26) = 0,0821, yani H1 eşiği 27.
P(X ≤ 23 | 42; 0,70) = 0,0264 ve P(X ≤ 24) = 0,0526, yani H0 eşiği 23. Ek 1'deki eşikler doğru.

"Diğer 40 seçim iki okumada aynıdır" savı da doğrulandı. `manifest_kur(..., sayim_yuvarlama=False)` 42 satır
veriyor. 40 satırın (birincil, sonraki, önceki, sessiz) dörtlüsü yuvarlamalı manifestle aynı, fazladan iki satır
`usp00055dh` ve `us7000i90q`. Bu iki olayın isabeti hesaplanmadı.

Yama (`tr2_kosu.py`):

```python
# sabitlerin altına
H1_ESIK_42, H0_ESIK_42 = 27, 23    # Ek 1: K = 42 okuması

def hukum_k42(X):
    return "H1" if X >= H1_ESIK_42 else "H0" if X <= H0_ESIK_42 else "ayirt_edilemez"

# hesapla() içinde, hk = hukum(X, K) satırından sonra
k42 = {x: hukum_k42(x) for x in range(X, X + 3)}
ek1 = {"K42_hukumleri": k42, "hukum_degisebilir": any(v != hk for v in k42.values()),
       "not": "iki olayın (usp00055dh, us7000i90q) isabeti hesaplanmadı"}
# return sözlüğüne: "ek1_K42": ek1,

# md_yaz() içinde, Hüküm bölümünün son maddesinden sonra
e = r["ek1_K42"]
L.insert(L.index("## Yorum kuralları (§3; hükmü değiştirmez)") - 1,
         "- Ek 1 (K = 42 okuması; eşikler X ≥ 27 H1, X ≤ 23 H0; dışarıda kalan iki kümenin isabeti hesaplanmadı): "
         + ", ".join(f"X = {x} → {v}" for x, v in e["K42_hukumleri"].items())
         + (". Hüküm K = 42 okumasında DEĞİŞEBİLİR." if e["hukum_degisebilir"]
            else ". Hüküm K = 42 okumasında değişmez."))
```

`tr2_test_yapay.py`'ye eklenecek sınama:

```python
@sina
def ek1_k42():
    for X, deg in ((22, True), (23, True), (24, False), (25, True), (26, True), (27, False), (30, False)):
        man, ag, ol, et, _ = yapay(X=X, tohum=300 + X)
        r = KO.hesapla(man, ag, ol, et)
        assert r["ek1_K42"]["hukum_degisebilir"] is deg, (X, r["ek1_K42"])
        assert "Ek 1 (K = 42" in KO.md_yaz(r)
```

Beklenen değerler el hesabıdır. X = 22: {22 H0, 23 H0, 24 ayırt} ve K40'ta H0, değişebilir. X = 24: üçü de ayırt,
değişmez. X = 25: 27'de H1, değişebilir. X = 26: 26'da ayırt, değişebilir. X = 27: üçü de H1, değişmez.

## Önemli

### Ö1. Tek koşu korumasında yazma sırası

`main` önce `tr2_sonuc.json` dosyasını yazıyor, sonra `md_yaz` ile md'yi üretiyor. `md_yaz` bir biçim hatasıyla
düşerse (örneğin beklenmeyen bir `None` değeri), X ve hüküm JSON'da kalır. Yeniden koşmak için de `--uzerine-yaz`
gerekir. Bu durum "istisna sonrası koşu" kuralını X görülmüş hâlde işletir. Yapay sınamalarda düşme görülmedi.

Yama: her şeyi bellekte üret, sonra iki dosyayı yaz.

```python
    r = hesapla(man, ag, olaylar, etas)
    r["girdi"] = {...}
    js = json.dumps(r, ensure_ascii=False, indent=1)
    md = md_yaz(r)                       # yazmadan önce; düşerse hiçbir dosya yoktur
    os.makedirs(a.cikti, exist_ok=True)
    for ad, icerik in (("tr2_sonuc.json", js), ("tr2_sonuc.md", md)):
        with open(os.path.join(a.cikti, ad), "x") as f:   # "x": var olanın üzerine yazmaz
            f.write(icerik)
```

`--uzerine-yaz` için `open(..., "w")` kullanılmalı. Bu bayrak kullanıldığında `r["girdi"]["uzerine_yaz"] = True`
yazılmalı, böylece yineleme izsiz kalmaz.

### Ö2. Girdilerin kimliği sonuçta kayıtlı değil

`girdi` alanında yalnız dosya adları var. Ham dizin sha listesiyle doğrulanıyor, ama manifest, ETAS dosyası ve
koşu kodunun kendisi doğrulanmıyor. Commit'teki dosyalardan farklı yerel bir dosyayla koşulursa sonuçta iz kalmaz.

Yama: `r["girdi"]` alanına şu dosyaların sha256 değerini ekle: `tr2_manifest.csv`, `tr2_manifest_agirlik.csv`,
`tr2_etas_p.csv`, `tr2_ham_sha256.txt`, `tr2_kosu.py`, `tr2_sayim.py`. Bu inceleme anındaki değerler commit
2305994'ten alınabilir. Koşu öncesi `git status --porcelain kayit/turetme/tr2` boş olmalı. Bu denetim ya koda
eklenir ya da koşu komutuna yazılır.

## Küçük

### K1. §4 "arka plan kuralına tabi" bayrağı tek yönlü

`s4_oncelik.etas_okumasi_arka_plan_kuralina_tabi = k3` yalnız alt kuyruk durumunu (ETAS lehine okuma) kapsıyor.
"Boşluk − ETAS" sıfırı pozitif yönde dışlarsa ilgili arka plan durumu üst kuyruk reddidir (kural 2). Hükmü
etkilemez, ama ETAS satırlarının yorumunda eksik kalır.

Yama:

```python
"etas_satiri_yonu": {a: ("pozitif" if log_skor[a]["aralik_95"][0] > 0 else
                         "negatif" if log_skor[a]["aralik_95"][1] < 0 else "sifir")
                     for a in ("etas_eksi_taban", "bosluk_eksi_etas")},
"ters_cevrim_ust_red": ust_red, "ters_cevrim_alt_red": alt_red,
```

Md'de dict repr yerine düz cümle yazılmalı (`{'etas_eksi_taban': True, ...}` şu an ham sözlük olarak basılıyor).

### K2. Bilgi satırı 6 ve 7'nin metni ön kayıttaki ifadeyi taşımıyor

- §5.6: X ≤ 14 ise notun adı "artçısı çok taraf lehine". Md yalnız "düşülür" yazıyor.
  Yama: `'düşülür: "artçısı çok taraf lehine" (§3 arka plan kuralına tabi)'`.
- §5.7: "Sonucu yalnız anılır; hiçbir Marmara cümlesine dayanak olmaz." Md'de yalnız "(yalnız anılır)" var.
  Yama: satırın sonuna " Bu sonuç hiçbir Marmara cümlesine dayanak olmaz." ekle.

### K3. `--sayim-yuvarlama` varsayılanı Ek 1'e ters

`tr2_manifest.py` varsayılan olarak metin okumasını (K 42) kullanıyor ve docstring'deki kullanım bayrağı
anmıyor. Bayraksız yeniden üretim `DUR: K = 42` ile güvenli biçimde durur, yani yanlış manifest yazılmaz. Yine de
docstring'e `--sayim-yuvarlama` eklenmeli ve "Ek 1 uyarınca zorunlu" notu düşülmeli.

Ek 1'deki "uygulamada |A| > 1/3" ifadesi tam değil. Fiilî ölçüt |A| ≥ 0,3335'tir. (1/3, 0,3335) aralığına düşen
bir k/n için n > 2000 gerekir. Gerçek veride n ≥ 10 olup |A| ∈ [1/3, 0,3335) olan 6 olayın hepsi tam 1/3
(sayım: usp00055dh, usp000h7qu, usp000hbbt, us2000cp4y, us7000i90q, us6000mghc). Bunlardan yalnız ikisi nitelikli
kümelerin ilk adayı. Sonucu etkilemez.

### K4. Sayım ile manifest arasında sonraki olay aralığının alt ucu

Sayımda `t0 + 30 g ≤ t` (kapalı), manifestte `t0 + 30 g < t` (açık; ön kayıt §2 bunu söylüyor). Manifest K = 40'ı
ve bayrak toplamlarını (çift/öncü 6, |s|/L ≤ 1 6, M ≥ Mw 10, ss birincil 14) aynen verdiği için fark sonuçsuz.
Yama gerekmez.

### K5. Bilgi satırı 5 ve 9 "40'tan çıkar" okumasıyla kodlanmış

Gölge (11 küme) ve çift/öncü (6 küme), kümeleme yeniden yapılmadan 40 kümeden çıkarılıyor. Sayımdaki gölge
varyantı ise birincilleri baştan atıp yeniden kümeliyordu (K 29). Burada da 40 − 11 = 29 çıkıyor, ama küme
içeriği aynı olmayabilir. Ön kayıt metni ("dışlanınca X ve K") iki okumaya da açık. Kodun okuması daha dar ve
körlüğe daha uygun. Md'ye "40 kümeden çıkarılarak (yeniden kümeleme yok)" ibaresi eklenmeli.

### K6. Yapay uçtan uca sınama ham dizinden geçmiyor

`uctan_uca_dosyalarla` sınaması manifesti elle kuruyor. `tr2_manifest.py`'nin artçılardan sessiz tarafı
çıkarmasını ve `tr2_etas.py`'yi zincire katmıyor. Bu incelemede yazılan sınama (aşağıda §1) zinciri tam kapsıyor
ve depoya eklenmeye değer. Kaynak: `/tmp/claude-0/-home-user/635decb6-3930-5a4d-9c31-b6f30d64fb94/scratchpad/kodinc/uctan_uca.py`
(depoda değil). `tr2_test_yapay.py`'ye `@sina` ile taşınabilir.

## Denetim ayrıntıları

### 1. İsabet fonksiyonu ve işaret zinciri

- `isabet()`, `S.eksen_bilesen({"lat": koken_lat, "lon": koken_lon}, olay, stk)` ile s'yi hesaplıyor. Sessiz
  taraf da `manifest.asimetri()` içinde aynı fonksiyonla, aynı köken ve aynı `stk` ile hesaplanıyor. Ana
  manifestte köken dış merkez (`koken_lat == dis_merkez_lat`, `repr` gidiş-dönüşü kayıpsız). `stk`, `repr` ile
  yazılıyor ve `float` ile okunuyor; değer aynı. ETAS da aynı `stk`'yi ve dış merkezi kullanıyor.
- `asimetri`: `sessiz = 1 if npoz < nneg else -1`. +s yanında daha az artçı varsa sessiz +1; bu "artçısı AZ olan
  taraf" demek, ters değil. Tarafsız bant (|s| < 5 km) sayımla aynı.
- Uçtan uca yapay sınama (bu inceleme, `uctan_uca.py`): 40 birincil, sahte `mekanizma.jsonl` (düğüm düzlemi
  doğrultusu rastgele olarak eksen ya da eksen + 180°; iki düzlemin sırası rastgele), yoğun yana 14–20, sessiz
  yana 3–6 artçı, bir tarafsız artçı ve birincilin kendi satırı. Sonraki ve önceki olay bilinen yana konuldu.
  `MF.main(..., sayim_yuvarlama=True)` → `ET.main` → `KO.main` zinciri çalıştırıldı. Tohum 1/2/3 için
  X = 19/23/20 ve X_ters = 19/16/22, hepsi beklenenle aynı. Hatalı küme: 0.
- Tarih çizgisi: 5 küme dış merkezi −179,7° boylamda, eksen 90°. Sonraki/önceki olaylar ±180°'yi aşıyor;
  isabetler doğru. `mesafe_az` boylam farkını trigonometrik olarak sarıyor, `hedef_nokta` sonucu [−180, 180)
  aralığına getiriyor.
- Kutup yakını: 85–89,99° (iki yarıküre) 3000 rastgele nokta. `eksen_bilesen` en çok 1,3e-9 km hatayla tersine
  dönüyor, isabet hatası 0. Yapay zincirdeki 8 küme 78° enlemde ve doğru. Tam kutupta azimut tanımsız, ama veride
  kutup olayı yok.
- `isabet` s = 0 ve sessiz ∉ {±1} için istisna veriyor. `_olay_hesap`, manifestteki |s|/L ve |d| ile yeniden
  hesaplananı karşılaştırıyor (doğru olay mı denetimi).

### 2. Eşikler, hüküm, yorum kuralları, ters çevrim

- `H1_ESIK, H0_ESIK = 26, 22`. `hukum` K ≠ 40'ta istisna veriyor. Binom değerleri ve §3 tablosu yapay testte
  tutuyor (0,0403; 0,0320).
- Kural 1: ters çevrimin iki kuyruk reddi raporlanıyor (ölçüm §5.8).
- Kural 2: `hk == "H1" and ust_red` olunca metin "H1, sıraya özgü değil, statik geometriyle ayırt edilemez;
  §8'e hiçbir şey taşınmaz". Doğru.
- Kural 3: `(hk == "H0" or X ≤ 14) and alt_red`. Doğru. X ≤ 14 zaten H0 olduğu için ikinci koşul fazlalık, ama
  zararsız.
- Kural 4: (i) u/L medyanının altında ve üstünde oran > 0,5; (ii) ağırlık merkezi X/K ≥ 0,6. İkisi de sağlanmazsa
  "dış merkezin arkası; kırılma yönüyle ayırt edilemez" yazılıyor. Doğru.
- §8 aktarım adayı: H1, komşu koşulları ve üst kuyruk reddi yok. Doğru.
- Ters çevrim: `kutu_adaylari(..., "onceki")` aralığı `[max(t0 − 15 y, 1976-01-01), t0 − 30 g)`. Aynı köken,
  stk ve kutu kullanılıyor. `bi["once"][-1]` havuz zaman sırasında en sonuncuyu alıyor. Ortak olay kuralı ters
  çevrime uygulanmıyor (Ek 1 notu). Yapay testte sınırlar (tam 30. gün dışarıda) doğru. Gerçek veride
  K_ters adayı 28.
- K = 42 cümlesi: yok (E1).

### 3. ETAS (§4) ve p_i medyanının 0,27 olması

- Hücreler: |s| = 0,5 L + 1 + 2k ≤ 5 L, d = −D + 1 + 2m ≤ D, D = max(L, 30). Toplamayla değil indeksle
  üretiliyor, birikimli kayan nokta hatası yok. Kutu süzgeci açık. Kaynak kümesi j: birincil (0, 0, Mw) ve
  `artci_oku`'nun bulutu (M ≥ 4, M < Mw, kimlik ≠ birincil, |s| < 5 km dahil). Zaman ve 3 L süzgeci artçı
  sorgusunun kendisinde (sayımla aynı dosya). Çekirdek `10^(M−4)·(r² + c²)^(−1,5)·4`, c = max(5, 0,5·L(M)).
  Kırpma [0,05; 0,95]. Hepsi §4'le harfiyen aynı.
- Bağımsız numpy uygulamasıyla karşılaştırma (yapay 25 artçı): `p_ham` 0,409242 ve 0,590758, bağımsız sonuç da
  aynı (1e-15).
- Simetrik bulut p = 0,5000; yalnız birincil p = 0,5. Tek M 5 kaynak +3 L'de ve sessiz −1 iken p = 0,401
  (< 0,5), sessiz +1 iken 0,599.
- Medyan 0,27: formülün doğal sonucu, etiket tersliği değil. Artçılar çoğunlukla yoğun yandadır ve yoğun yandaki
  kutuya daha yakındır. Bu yüzden R_yoğun > R_sessiz ve p_i < 0,5 olur. Uçtan uca yapay zincirde de (sessiz
  etiket doğruluğu isabetle doğrulanmışken) p_ETAS medyanı 0,27–0,32 çıktı. Gerçek veride 40 p_i'den biri
  (0,545) > 0,5. Bu, sayım ile ETAS ağırlığının farklı olmasından beklenen bir durum: büyüklük ağırlığı ve kutuya
  yakınlık sayımı tersine çevirebilir. Kırpılan p yok.

### 4. Log skor ve bootstrap

`_bern` doğru. Üç fark satırı küme başına hesaplanıyor. `default_rng(20261111)`, tek bir `idx` matrisi
(10 000 × K) üç satırda ortak (eşleştirilmiş). `np.percentile` varsayılanı doğrusal (numpy 2.5.3). Aralık
toplam fark üzerinden. "sıfırı içerir" kapalı aralıkla tanımlı. Yapay testte X = 26/29 aralığı sıfırı içeriyor,
X = 30 içermiyor (inceleme 1 E2 ile aynı).

### 5. On bilgi satırı

| § | Ön kayıt | Kod | Durum |
|---|---|---|---|
| 5.1 | u/L medyanının altı ve üstü | `statistics.median`; eşitler iki gruba da girmez (Ek 1) | uygun (gerçek veride eşit 0, 20/20) |
| 5.2 | ağırlık merkezi tanımıyla X, K | ayrı manifest; köken, sessiz taraf ve kutu centroidden; K ne çıkarsa (8) | uygun |
| 5.3 | düğüm düzlemi–artçı ekseni > 30° var/yok | `pfark > 30` | uygun |
| 5.4 | aday ≥ 3 var/yok | `len(son) >= 3` | uygun |
| 5.5 | gölge dışlanınca X, K | 40'tan çıkar (11) | uygun, bkz. K5 |
| 5.6 | X ≤ 14 notu | bayrak | uygun, ifade K2 |
| 5.7 | Türkiye yalnız anılır | `tr` bayrağı (1 küme) | uygun, ifade K2 |
| 5.8 | zaman ters çevrimi | yukarıda | uygun |
| 5.9 | çift/öncü dışlanınca (6/40) | `buyuk` = artçı dosyasında M ≥ Mw; 6 | uygun |
| 5.10 | \|s\|/L ≤ 1 (6), M ≥ Mw (10), ss birincil (14) | bayraklar 6/10/14 | uygun |

Çift/öncü olaylarından hiçbiri birincilin yinelenmiş kaydı değil: en kısa zaman farkı 4412 s, ilk 60 s içinde
kayıt yok.

### 6. Yeniden üretilebilirlik

- `python3 -I -B tr2_manifest.py <ham> <tar> --sayim-yuvarlama --cikti <geçici>` komutu tar sha256 assert'ini
  geçti. `tr2_manifest.csv`, `tr2_manifest_agirlik.csv` ve `tr2_ham_sha256.txt` depodakilerle bayt bayt AYNI.
  Özet: K 40, nitelikli 49, ortak olay 0, K_ağırlık 8, deprem dışı sonraki 0.
- `tr2_etas.py <ham> --cikti <geçici>` (depodaki manifestle ve yeniden üretilen manifestle) çıktısı
  `tr2_etas_p.csv` ile bayt bayt AYNI. Özet: medyan 0,2661, en küçük 0,0751, en büyük 0,5451.
- `sha_dogrula(ham, tr2_ham_sha256.txt)` 1344 dosyayı doğruladı.
- Mevcut `tr2_test_yapay.py` 9/9 geçti.

### 7. Tek koşu, sha, istisnalar, dil

- Tek koşu: çıktı varsa duruyor; `--uzerine-yaz` bilinçli bir kaçış. Yazma sırası Ö1'de.
- `dosyalari_oku` şunları denetliyor: K = 40, ETAS ile manifestin küme ve birincil sırası, birincilin konumu,
  büyüklüğü ve t0'ı (ham aday dosyasıyla), havuzda olay eksikliği, 2025 sonrası olay assert'i.
- İstisna mesajları yalnız küme adı ya da dosya yolu taşıyor; isabet ya da s sızdırmıyor.
- Sonuç dosyasında İstanbul ya da Marmara için mutlak olasılık yok, iddia dili yok. Hüküm adları ön kayıttaki
  gibi. Türkiye satırı "yalnız anılır" (K2 eki önerildi).

## Koşu öncesi yapılacaklar

1. E1 yamasını ve testini uygula; `python3 -I -B kayit/turetme/tr2/tr2_test_yapay.py` geçmeli.
2. Ö1 ve Ö2'yi uygula (önerilir; Ö1 tek koşu güvenliği için).
3. K1, K2 ve K5 ifade yamaları (isteğe bağlı, hükmü etkilemez).
4. Commit et. Ardından `git status` temizken tek komutla koş.
