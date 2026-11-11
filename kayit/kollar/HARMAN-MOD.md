# Harman kapısı: mod kararı (11 Kasım 2026)

```yaml
mode: campaign-candidate
lit_paths: [R1, R4, R9]
justification:
  R1: "Dört kolun terimleri (gevşeme, veri asimilasyonu, öncü, geçici) sınanabilir belirlenime indirilmeden aday tablosu kurulamaz."
  R4: "Seçilen her aday için hedef küme, rakip ve kriter koşudan önce dondurulmalı (ön kayıt)."
  R9: "Zaman eksenini daralttığı iddiası yalnız bakir veride tek vuruşla hükme bağlanır."
owner_gate: required      # yeni fizik iş paketlerinde seçim Erdem'in
execution: blocked        # fizik koşuları; literatür ve veri taraması serbest (solo/kompozit iş)
```

- Mekanizma sayısı 4 (viskoelastik yüklenme, fay ağı durumu, tetiklenme/öncü, yeni veri akışları): ayrı ürün, ayrı ölüm testi geçer.
- Transfer sorusu: başka bölgede kurulmuş yöntem Marmara'da kazanç verir mi.
- Nadas: 1 Ocak 2027 sonrası ileri test ve Türkiye dışı 2026 (dokunulmadı). Geçmişte başka bakir Türkiye verisi yok (mühür 7 Kasım'da açıldı); bu, her adayın gücünü sınırlar.
- Şu anki iş (tarama, envanter, defter) kampanya değil; aday seçilince R4 ile dondurma, sonra tek vuruş.
- task-tree notu: Pi tabanlı task-tree harness'i bu bulut oturumunda kurulu değil ve run modeli tek (deepseek-flash). İstenen düzen (kol başında Fable, altında Opus) aynı ağaç yapısıyla ajan aracı üzerinden kuruldu: kök bu oturum, dört kol başı Fable, alt ajanlar Opus, dosya sahipliği kol başına ayrı (`kayit/kollar/<KOL>.*`).
