# S6 sonucu: türbidit eşzamanlılığı ortak kırılmayı ölçemiyor (10 Kasım 2026)

Kural: `S1-S6-KURAL.md` (sha 167ef5b4…, OTS, 4e71914). Kod: `tools/arastirma/s6_sentetik.py` (tohum 20261110, σ başına 4000 simülasyon). 0 €.

| 1σ yaş hatası | f = 0,1 ile 0,5'i ayırma gücü (α 0,05, 1000 yıl) | eşzamanlı pay f = 0,1 | f = 0,5 |
|---|---|---|---|
| 30 yıl | 0,17 | 0,39 | 0,51 |
| 60 yıl | 0,12 | 0,48 | 0,57 |
| 100 yıl | 0,00 | 0,56 | 0,62 |
| 15 yıl (bilgi) | 0,15 | 0,32 | 0,47 |
| 5 yıl (bilgi) | 0,35 | 0,18 | 0,38 |

**Hüküm (kurala göre): S6 ölçülemez, kapandı.** Eşik 0,8; hiçbir σ'da yaklaşılmıyor. Sınırı tarihleme kadar olay sayısı koyuyor: 1000 yılda segment başına ≈4 olay var, ve tetiklenmiş yakın çiftler (0–30 yıl) ile Poisson rastlantıları "eşzamanlı" görünüyor. σ 5 yıla insen bile güç 0,35. Gerçek türbidit verisine geçilmedi.

Sonuç: CMF+PIF ortak kırılma payını yalnız S1 (sıçrama kuralları) ve simülatör (S5) kısıtlayabilir.

Sınır: sentetik model basit (Poisson, sabit tetiklenme payı %20). Daha uzun kayıt (≥ 5000 yıl) ya da tek tek olayın kalınlık/köken izi (havza kaynaklı türbidit imzası) gücü değiştirebilir; bu kuralın dışında.
