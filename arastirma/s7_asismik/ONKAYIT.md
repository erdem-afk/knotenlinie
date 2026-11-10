# S7 ön kaydı: asismik kayma geçicileri M≥4 oranını ETAS'ın üstünde artırıyor mu (doğrultu atımlı, Kuzey Kaliforniya)

Durum: TASLAK → inceleme → DONDUR (sha256 + OTS). Yazım 10 Kasım 2026, veri yüklenip yalnız biçimi
görüldükten sonra; kovaryat ile hedef arasındaki ilişkiye bakılmadı.

Kaynak soru: `docs/arastirma-sorulari/2026-11-10_yeni-arastirma-sorulari.md`, soru 7. Öncül:
Uchida vd. 2016 (Science, dalma-batma, Japonya): tekrarlayan depremlerden çıkarılan kayma hızı
dalgalanmaları büyük deprem oranını modüle ediyor. Burada doğrultu atımlı sünen faylarda sınanır.

## Veri

1. Tekrarlayan depremler: Waldhauser ve Schaff 2021 (JGR, doi:10.1029/2021JB022495), Zenodo
   doi:10.5281/zenodo.5576354, `NCA_REPQcat_20210919.txt`, md5 e097a146a9dca904bd8b367729f0d1cc
   (Zenodo ile eşleşti), sha256 ebf6453722351fb5e621817f233954389984c3a88d1df4d15dce4fcc47c88b98.
   1984–2014, 27 675 olay, 7 713 dizi.
2. Hedef ve ETAS kataloğu: USGS ANSS ComCat, 35,5–38,5° K, 123,0–120,5° B, 1984-01-01 – 2014-12-31,
   M ≥ 2,5. İndirme sorgusu bitiş tarihini 2014-12-31 olarak koyar; 2015 sonrası satır indirilmez.
   (Türkiye dışı 2026 kör verisine hiçbir koşulda dokunulmaz.)

## Tanımlar

- Hücre: 0,2° × 0,2° ızgara. "İzlenen hücre": içinde ≥ 3 olaylı ve etkinliği ≥ 10 yıla yayılan en az 5
  tekrarlayan dizi olan hücre. Liste koşunun ilk adımında üretilir ve dondurulur (hedeflere bakmadan).
- Zaman: 3 aylık çeyrekler. Çeyrek q için tahmin yalnız q başından önceki veriyi kullanır.
- Kayma vekili: tekrarlayan olay başına d = 10^(−2,36) · M0^0,17 cm (Nadeau ve Johnson 1998),
  M0 (dyn·cm) = 10^(1,5·M + 16,1), M = katalog NCSN büyüklüğü. Hücrenin pencere kayma hızı = pencere
  içindeki d toplamı / (hücrede o ana kadar etkin dizi sayısı) / pencere yılı.
- İvmelenme kovaryatı: A(hücre, q) = ln[(v_12 + ε) / (v_60 + ε)]; v_12 son 12 ay, v_60 ondan önceki
  60 ay kayma hızı, ε = 0,1 cm/yıl. 6 yıllık geçmiş gerektiği için ilk tahmin çeyreği 1990-Ç1.
- Hedef: izlenen hücrelerde M ≥ 4,0 olaylar (kümesizleştirilmemiş; kümelenmeyi ETAS taşır).

## Modeller

R0 (rakip, ETAS): hücre başına zamansal ETAS, ortak parametreler.
λ_h(t) = μ_h + Σ_{i: t_i < t, i hücre h içinde ya da merkezine ≤ 20 km} K·10^(α(M_i − 2,5))·(t − t_i + c)^(−p),
tetikleyiciler M ≥ 2,5. Parametreler (μ_h, K, α, c, p) seçim döneminde (1984–2003) M ≥ 2,5 olaylarla en
büyük olabilirlik. M ≥ 4 beklenen sayı = ∫λ dt · 10^(−b·1,5), b seçim döneminden Aki tahmini.
Doğrulamada ETAS parametreleri dondurulur; geçmiş olaylar tetiklemeye girer (standart sözde-ileri).

H1: λ1 = λ0 · exp(β·A(hücre, q)); β seçim döneminde (1990–2003 çeyrekleri) M ≥ 4 sayılarının Poisson
olabilirliğiyle, R0 sabitken tek parametre olarak uydurulur.

## Sınav

Doğrulama: 2004-Ç1 – 2014-Ç4, izlenen hücreler. Puan: hücre-çeyrek Poisson log olabilirliği;
IG = (LL_H1 − LL_R0) / N_doğrulama (nat/olay). Belirsizlik: yıl blokları (11) üzerinden jackknife SE.

Ateşleme kapısı: koşunun ilk adımında N_doğrulama sayılır (yalnız sayı). N_doğrulama < 20 ise sonuç
önceden "ayırt edilemez" ilan edilir, IG yalnız bilgi satırı olarak yazılır.

Hüküm: IG − 2·SE > 0 → H1 (ivmelenme ETAS'a bilgi ekliyor); IG + 2·SE < 0 → H0 lehine (kovaryat zarar
veriyor); arada → ayırt edilemez. β işareti ve büyüklüğü ayrıca raporlanır (H1 fiziksel olarak β > 0
bekler; β ≤ 0 ile gelen kazanç "H1 değil, başka etki" diye yazılır).

Ek satırlar (hükme girmez): (a) 2004-09-28 Parkfield M6,0 dizisi (ilk 90 gün, 30 km) hariç IG;
(b) M ≥ 5 hedef sayısı ve IG (güç yok, bilgi); (c) seçim döneminde β profil olabilirliği.

## Marmara'ya bağ

Marmara için tekrarlayan deprem kataloğu kısa (Bohnhoff 2017 vb.); burada sayısal satır yok. Sonuç
ileri test defterine yalnız bilgi satırı olarak girer, İstanbul olasılığına yayılmaz. Anlamı: CMF'de
bir hızlanma görülürse kısa vadede ETAS üstüne çarpan uygulanmalı mı sorusuna Kaliforniya cevabı.

## Sapma kuralı

S4 ile aynı: sapma "SAPMA" başlığıyla yazılır; hata düzeltmesi sonrası tek yeniden koşu, iki koşu da
raporlanır. Maliyet 0 € (bulut). Sonuç: `arastirma/s7_asismik/SONUC.md`.
