# S7 ön kaydı: asismik kayma geçicileri M≥4 oranını ETAS'ın üstünde artırıyor mu (doğrultu atımlı, Kuzey Kaliforniya)

Sürüm 2 (bağımsız inceleme KABUL-ŞARTLI; 9 zorunlu değişiklik işlendi, `INCELEME.md`). Yazım
10 Kasım 2026, veri yüklenip yalnız biçimi ve sayıları görüldükten sonra; kovaryat ile hedef
arasındaki ilişkiye bakılmadı, hedef kataloğu indirilmedi.

Kaynak soru: `docs/arastirma-sorulari/2026-11-10_yeni-arastirma-sorulari.md`, soru 7. Öncül:
Uchida vd. 2016 (Science, dalma-batma): tekrarlayan depremlerden çıkan kayma hızı dalgalanmaları
büyük deprem oranını modüle ediyor. Burada doğrultu atımlı sünen faylarda sınanır.

## Veri

1. Tekrarlayan depremler: Waldhauser ve Schaff 2021 (JGR, doi:10.1029/2021JB022495), Zenodo
   doi:10.5281/zenodo.5576354, `NCA_REPQcat_20210919.txt`, md5 e097a146a9dca904bd8b367729f0d1cc
   (Zenodo ile eşleşti), sha256 ebf64537…. 1984–2014.
2. Hedef ve ETAS kataloğu: USGS ANSS ComCat, 35,2–38,8° K, 123,3–120,2° B (izlenen alanın her yönde
   0,3° genişletilmişi), 1984-01-01 – 2014-12-31, M ≥ 2,5, ComCat tercihli büyüklük. Sorgu bitişi
   2014-12-31; 2015 sonrası satır indirilmez. Sorgu URL'si sonuç dosyasına yazılır. Türkiye dışı 2026
   kör verisine dokunulmaz.

## Tanımlar

- Kovaryata giren olaylar: 0 < MAG < 3,5 (MAG = 0 eksik sayılır). Bir olay t anında kovaryata ancak
  dizisinde t'den önce en az bir olay varsa girer (dizinin ilk olayı, ikinci olay gelene kadar sayılmaz;
  gerçek zamanlı tekrarlayan tanımı).
- Hücre: 0,2° × 0,2° ızgara. Dizi konumu = dizinin ≤ 2003 olaylarının medyan konumu. "İzlenen hücre":
  yalnız 2003-12-31'e kadarki olaylarla, ≥ 3 olaylı ve etkinliği ≥ 10 yıla yayılan en az 5 dizisi
  olan hücre. Liste koşunun ilk adımında üretilir, sha256 ile kayda geçer.
- Zaman: 3 aylık çeyrekler; çeyrek q için her şey yalnız q başından önceki veriyle.
- Kayma vekili: olay başına d = 10^(−2,36) · M0^0,17 cm (Nadeau ve Johnson 1998), M0 (dyn·cm) =
  10^(1,5·MAG + 16,1). Pencere kayma hızı = pencere içi d toplamı / P / pencere yılı; P = q başında
  ≥ 1 olayı olmuş dizi sayısı (v_12 ve v_60 için aynı P). P = 0 ise v_12 = v_60 = 0, dolayısıyla A = 0.
  ≤ 2003 olayı olmayan diziler hiçbir hücreye atanmaz, kovaryata girmez.
- Ham ivmelenme: A(h, q) = ln[(v_12 + ε)/(v_60 + ε)], v_12 son 12 ay, v_60 ondan önceki 60 ay,
  ε = 0,1 cm/yıl. Algılama sürüklenmesi düzeltmesi: A*(h, q) = A(h, q) − medyan_{izlenen h'} A(h', q).
  H1 A* kullanır; ham A ile koşu bilgi satırı.
- İlk tahmin çeyreği 1990-Ç1 (6 yıl geçmiş). 1984 ETAS için ısınma yılıdır; ETAS olabilirliği 1985'ten.
- Hedef: izlenen hücrelerde M ≥ 4,0 olaylar (kümesizleştirilmemiş; kümelenmeyi ETAS taşır).

## Modeller

R0 (rakip, ETAS), yalnız izlenen hücrelerde:
λ_h(t) = μ_h + Σ_{i: t_i < t, episantrı hücre h merkezine ≤ 20 km} K·10^(α(M_i − 2,5))·(t − t_i + c)^(−p),
tetikleyiciler genişletilmiş kutudaki M ≥ 2,5 olaylar. Parametreler (μ_h ≥ 10⁻⁶/gün, K, α ≤ 2,3, c,
p > 1), seçim döneminde (1985–2003) izlenen hücrelerdeki M ≥ 2,5 olayların sürekli zamanlı nokta süreci
olabilirliğinin en büyüğüyle bulunur (uydurmada λ sürekli güncellenir; tahminde yalnız çeyrek başı
tetikleyiciler);
5 rastgele başlangıç, en iyi LL. b: Aki–Utsu (ΔM/2 düzeltmesi), M ≥ 2,5, izlenen hücreler, 1984–2003.
Çeyrek q'nun M ≥ 4 beklenen sayısı = ∫_q λ dt · 10^(−b·1,5), λ yalnız q başından önceki tetikleyicilerle
(çeyrek içi güncelleme yok; H1 ile simetrik). Doğrulamada parametreler dondurulur.

H1: λ1 = λ0 · exp(β·A*(h, q)); β, R0 sabitken seçim döneminin (1990–2003) M ≥ 4 hücre-çeyrek
sayılarının Poisson olabilirliğiyle tek parametre olarak uydurulur. Seçimdeki M ≥ 4 sayısı raporlanır.

## Sınav

Doğrulama: 2004-Ç1 – 2014-Ç4, izlenen hücreler. Puan: hücre-çeyrek Poisson log olabilirliği;
IG = (LL_H1 − LL_R0) / N_doğrulama (nat/olay). SE: yıl jackknife'ı, β ve ETAS sabit; IG_(−k) k yılı
çıkarılarak; SE = √((n−1)/n · Σ(IG_(−k) − ort)²), n = 11.

Ateşleme kapısı (yalnız sayılar, kovaryata bakmadan): N_doğrulama < 20 ya da hedeflerin dağıldığı yıl
sayısı < 5 ise sonuç önceden "ayırt edilemez" ilan edilir, IG bilgi satırı olur.

Hüküm: IG − 2·SE > 0 VE β > 0 → H1. IG + 2·SE < 0 → H0 lehine. Diğer her durum (β ≤ 0 ile gelen
kazanç dahil) → ayırt edilemez / başka etki.

Yorum şartı: H1 çıkarsa, genişletilmiş kutudaki ComCat M ≥ 5 olaylarından herhangi birinin sonraki
365 günüyle zamanda kesişen ve merkezi o olaya ≤ 30 km olan hücre-çeyrekler çıkarılır; kalan kümede IG
nokta tahmini > 0 ise "asismik geçici" yorumu yazılır, aksi halde "artçı ya da ETAS model hatası
düzeltmesi".

Ek satırlar (hükme girmez): ham A ile IG; 2004-09-28 Parkfield M6,0 dizisi (ilk 90 gün, 30 km) hariç
IG; M ≥ 5 hedef sayısı ve IG; seçim döneminde β profil olabilirliği.

## Marmara'ya bağ

Marmara için sayısal satır yok (tekrarlayan katalog kısa). Sonuç ileri test defterine yalnız bilgi
satırı olarak girer, İstanbul olasılığına yayılmaz.

## Sapma kuralı

"Hata" = kod ile bu metin arasındaki fark. Hata düzeltmesi sonrası tek yeniden koşu, iki koşu da
raporlanır; bilinçli sapma "SAPMA" başlığıyla yazılır. Maliyet 0 € (bulut). Sonuç:
`arastirma/s7_asismik/SONUC.md`.
