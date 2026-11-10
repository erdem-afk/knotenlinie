# Soru 3 · Mikrosismisite M7'yi yanlış yere mi koyuyor? Ön kayıt TASLAĞI (bulut, 10 Kasım 2026)

Durum: TASLAK, dondurulmadı. Sunucu oturumu D3 hedef listesini görmeden önce bu metni sabitleyip DONDUR-mikrosism.json + OTS yapacak. D3 olaylarının puanlarına bu taslakta bakılmadı.

## Hedef ve puan
- Olay kümesi: D3'ün 49 küresel doğrultu atımlı M7+ olayı (1990–2025), D3 kuralındaki kırılma izleri. Türkiye dışı 2026'ya dokunulmaz.
- Her olay için D3'teki fay sistemi izi 15 km binlere bölünür; olaydan önce yayımlanmış iz kullanılır. Tahmin: bin payı p_i (toplam 1).
- Puan (önceden seçildi): kırılan binlerin log payının ortalaması, L = (1/k) Σ_{i∈kırık} log p_i. Bilgi satırı: ilk kırılma (hiposantr) binine kategorik log p.
- Olay öncesi katalog: ISC-GEM + ISC (yoksa ComCat), olaydan önceki 15 yıl, son 30 gün hariç (öncü depremler dışarıda), M ≥ max(3,0, yerel Mc), faydan ≤10 km.

## Modeller
- H0 rakip (ETAS-orantılı): p_i ∝ λ_i + ε, λ_i v1.2 düzleştirme çekirdeğiyle bin yoğunluğu.
- A1 ters sismisite: p_i ∝ 1/(λ_i + ε).
- A2 sünme düzeltmeli: yayımlanmış (olay öncesi) sünme haritasında sünen binde λ_i × 0,1, kilitli olduğu açıkça yazılı binde × 1; haritası olmayan olayda A2 = H0 (nötr; proje kuralı).
- K tekdüze kontrol: p_i = 1/n.
- ε: H0 ve A1 için tek sabit, fay sisteminin bin başına ortalama λ'sının %10'u (önceden, serbest değil).

## Ateşleme kapısı
- Etkin N: aynı fay sistemindeki olaylar (ör. 1999 İzmit + Düzce, 2023 Kahramanmaraş ikilisi, Landers + Hector Mine) tek blok. Blok bootstrap SE (10.000).
- MDE = 2,8 × SE_beklenen (α 0,05 iki yönlü, güç 0,8). Beklenen fark (|A − H0|) MDE'den küçükse sonuç önceden "ayırt edilemez".
- Önsel beklenti: olayların çoğunda sünme haritası yok, A2 büyük olasılıkla ≈H0. Asıl sınanabilir karşılaştırma H0 – A1 – K.

## Karar
- A, H0'ı ≥ +2 SE geçer ve ≥2 bağımsız fay sisteminde (blokta) aynı işaret → H1 desteklenir.
- Aksi halde H0 (Kagan–Jackson yönü).
- Ne çıkarsa çıksın v1.3b NİHAİ değişmez. Kazanan dönüşüm Marmara'da CMF/PIF/Kumburgaz binlerine uygulanır (CMF batısı sünen: v1.8, docs/sonuc/2026-11-10_cmf-kilitlenme.md), sıradaki sürüm adıyla ileri test defterine RAKİP girer. Önceden yazılı çıktı: İstanbul 30 yıl ORANI (vs v1.3b), %10–90 genişlik oranı, aralık payları. Olasılık yazılmaz.

## Sünme haritası envanteri (olay öncesi yayımlanmış adaylar; Crossref ile bulundu, yayım tarihi muhur.py ile ayrıca doğrulanacak)
| Fay | Kaynak | DOI | Yıl |
|---|---|---|---|
| San Andreas orta kesim | Titus vd. (saha rehberi, sünme ölçümleri) | 10.1130/2006.1906sf(16) | 2006 |
| KAF İsmetpaşa | Çakır vd. | 10.1016/j.epsl.2005.06.044 | 2005 |
| Chaman | Fattahi & Amelung | 10.1002/2016gl070121 | 2016 |
| Chaman | Barnhart | 10.1002/2016jb013656 | 2017 |
| Haiyuan | Jolivet vd. | 10.1029/2011jb008732 | 2012 |
| Longitudinal Valley | Champenois vd. | 10.1029/2005gl024624 | 2006 |
| Philippine (Leyte) | Duquesnoy vd. | 10.1029/94gl00640 | 1994 |
| Hayward | Lienkaemper (USGS OFR 97-690) | 10.3133/ofr97690 | 1997 |
| Orta Marmara batısı | v1.8 kaynak tablosu (2016+) | depoda | — |
Yakın öncüller: Schorlemmer & Wiemer 2005 (10.1038/4341086a), Kaneko, Avouac & Lapusta 2010 (10.1038/ngeo843).

Dürüst sınır: D3 olaylarının büyük kısmı (Landers, Hector Mine, Denali, Kunlun, Kaikoura, Ridgecrest, Maduo, Myanmar vb.) olay öncesi sünme haritası olmayan faylarda; A2'nin gücü düşük olacak, asıl bilgi H0–A1–K karşılaştırmasından gelir.
