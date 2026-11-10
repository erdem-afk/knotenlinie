# S1 sonucu: fay sıçrama kurallarının yayım sonrası sınavı (10 Kasım 2026)

Kural: `S1-S6-KURAL.md` (sha 167ef5b4…, OTS, 4e71914) ve puanlamadan önce yazılan Ek 1 (518c230; kör değil, gerekçesi orada). Kod: `tools/arastirma/s1_gecit.py`, `s1_puan.py`, `s1_marmara.py`. Envanter `S1-envanter.json`, puan `s1_sonuc.json`, Marmara `s1_marmara.json`. Tek koşu. 0 €.

## Hüküm satırı

| | Değer |
|---|---|
| Olay / puanlanan geçit | 6 olay (Kumamoto 2016, Ridgecrest 2019 ×2, Kahramanmaraş 2023 Mw 7,8, Elbistan 2023 Mw 7,6, Myanmar 2025); 51 geçit: 47 geçti, 4 durdu |
| Ateşleme kapısı | beklenen ΔL 2,15 nat, SE 1,86 → **KAPALI: sonuç önceden "ayırt edilemez"** |
| ΔL = L(BW) − L(R0 = 0,46) | +6,28 nat (geçit başına +0,123), olay bloklu %95 [+1,70, +14,14] |

Kurala göre hüküm **ayırt edilemez**. Kapı kapalı olduğu için ΔL > 0 olması BW lehine kanıt sayılmaz. Önceden yazıldığı gibi (Ek 1 madde 5) ΔL'nin 5,6 nat'ı geçilen küçük bükümlerden geliyor.

## Asıl bulgu (bilgi satırı, güçlü): kırılmalar BW'nin dediğinden çok daha sık geçiyor

| BW olasılık kutusu | n | BW'nin beklediği geçiş | Gözlenen geçiş |
|---|---|---|---|
| 0–0,2 | 3 | 0,27 | **2** |
| 0,2–0,5 | 1 | 0,49 | 1 |
| 0,5–0,8 | 47 | 26,9 | **44** (binom p ≈ 3·10⁻⁸) |

- Sabit oran R1 (örneklem içi geçiş payı 0,92) BW'yi 18,7 nat geçiyor (örneklem içi, bilgi).
- BW'nin "durur" dediği 3 geçidin 2'si geçildi: Kahramanmaraş'ta 32° büküm, Elbistan'da 32° büküm.
- Kırpma 0,01 veya 0,05 alınınca ΔL aynı kalıyor (+6,28).

**Dikkat, karışıklık:** bizim 5 km kiriş ölçütümüz yumuşak eğriliği de "büküm" sayıyor. Özellikle InSAR'la sayısallaştırılmış izlerde bu böyle. BW17'nin bükümleri haritalanmış ayrık yapılar. Fazla geçişin bir kısmı tanım farkından gelebilir. Buna rağmen ≥30° iki bükümün geçilmesi tanım farkıyla açıklanamaz: ikisi de 2023 Türkiye kırılmalarında.

## Marmara (puandan bağımsız, kurala göre)

EDSF13 geometrisi (2013, olay öncesi) aynı algoritmayla ölçüldü:

| Geçit | Ölçü | P_BW | P_R0 |
|---|---|---|---|
| İzmit (1999) → Doğu Marmara, Çınarcık | basamak 8,5 km | 0,02 (BW: geçilmez) | 0,46 |
| PIF → CMF geçişi (≈28,9°D) | iki büküm, 12,8° ve 10,9° (toplam ≈39°) | 0,57 × 0,57 = 0,33 | 0,46² = 0,21 |
| CMF → Ganos (Tekirdağ) | basamak 2,6 km | 0,52 | 0,46 |
| Ganos içi | büküm 11,6° | 0,57 | 0,46 |

- **İstanbul'a bağlantı:** hüküm H0 olduğu için kurala göre R0 kullanılır. Buna göre bir PIF kırılması CMF'ye ulaştığında geçiş olasılığı ≈0,21; BW'ye göre 0,33. 2016 sonrası gözlenen geçiş payıyla (bilgi) ≈0,85.
- Bu, v1.7'nin ortak kırılma payıyla (f ≈ 0,10; 0,05–0,15) doğrudan aynı şey değil. f, olayların hangi payının ortak olduğudur. Geçidin koşullu geçiş olasılığı ise kırılmanın geçide ulaşmasını varsayar. Ama üç tahmin de 0,10'un üstünde. f'nin küçük tarafta olduğu varsayımı bu veriyle desteklenmiyor.
- **Öneri (rakip, v1.3b değişmez):** v1.7b, ortak kırılma payını geçiş olasılığından türetir (R0 0,21; BW 0,33; gözlenen 0,85 üç dal). Dönüşüm için kırılmanın geçide ulaşma olasılığı gerekir; bunu simülatör (S5 thread'i) verebilir.
- BW, 1999 gibi bir İzmit kırılmasının Çınarcık basamağını geçmeyeceğini söylüyor (8,5 km). 1999'da kırılma gerçekten orada durmuştu, tutarlı.

## Sınırlar

- Kaikoura, Palu ve Maduo dışarıda (açık iz yok ya da 3,4 GB). Durma geçidi yalnız 4; kalibrasyonun "durur" yanı neredeyse ölçülmedi.
- Ridgecrest uçları puanlanmadı: GEM bu fayları göstermiyor.
- Kahramanmaraş InSAR çizgilerinin olaylara ataması kuralla yapıldı; batıdaki bir zincir dışarıda.
- Ek 1 envanter görüldükten sonra yazıldı (veri kalitesi gerekçesiyle, kör değil).
- Kazanç ve kalibrasyon farkı geçit tanımına duyarlı. Daha iyi sınav: haritalanmış ayrık bükümler (FDHI/SURE yapısal öznitelikleri) ve tam olay listesi.
