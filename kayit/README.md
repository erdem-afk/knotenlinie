# Ortak kayıt: aday defteri ve kaynakça

Amaç: aynı iş iki kez yapılmasın. Her oturum (insan ya da ajan) yeni bir araştırma
sorusu, fizik iş paketi ya da literatür taramasına başlamadan **önce** buraya bakar,
başlarken satır açar, bitince kapatır.

| Dosya | İçerik |
|---|---|
| `adaylar.jsonl` | Her satır bir aday/hipotez. Açık, koşan, kapanmış hepsi burada. |
| `kaynakca.bib` | Tek kaynakça (BibTeX; Zotero, JabRef, Pandoc okur). Anahtar = DOI'den türetilir. `openalex` alanı varsa OpenAlex kimliği. |
| `kayit.py` | `ara`, `dogrula`, `ekle-kaynak`, `ozet` komutları. Yalnız standart kitaplık. |

## Kurallar

1. **Önce ara.** `python3 kayit/kayit.py ara <kelime>` (ad, soru, etiket, ders alanlarında arar).
   Benzer bir satır `kapandi` ise yeniden açma; `yeniden_acma_sarti` alanı ne diyorsa o.
2. **Başlarken satır aç.** `durum: "aday"` (yalnız fikir) ya da `"kosuyor"`; `sahip` alanına thread/dal adı.
   Kimlik çakışmasın: yeni kimlikler `<kol>-<harf><no>` (ör. `VE-1`, `FA-2`, `TK-3`, `AV-1`).
   Eski kısa adlar (K1, D3…) kollar arasında çakıştığı için `kimlik` alanında kol önekiyle yazıldı, `eski_ad` özgün adı tutar.
3. **Bitince kapat.** `durum`, `hukum`, `sonuc` (sayı + belirsizlik), `ders` (bir sonraki kişiye tek cümle), `kayit` (commit, dosya).
4. **Satır eklemek/ değiştirmek tek satırlık diff olmalı** (JSONL bu yüzden). `git add kayit/adaylar.jsonl` — yalnız dosya adıyla; `git commit -a` yasak.
5. **Kaynak eklerken** `python3 kayit/kayit.py ekle-kaynak <doi> [<doi> …]`. Aynı DOI ikinci kez eklenmez.
   Adayın `kaynaklar` alanına BibTeX anahtarı ya da DOI yazılır.
6. Mutlak İstanbul olasılığı bu dosyalara **yazılmaz** (16 Ekim taahhüdü); yalnız oranlar, genişlik oranları, nat farkları.
7. Yeni fizik iş paketi `durum: "aday"` ile girer; seçim Erdem'in. Literatür ve veri işleri doğrudan başlar.
8. Kör veri (Türkiye dışı 2026, 1 Ocak 2027+ ileri test) hiçbir aday için okunmaz. v1.3b nihai dondurmasına dokunulmaz; yeni sürüm ileri test defterine **rakip** girer.

## Alanlar

`kimlik`, `eski_ad`, `kol`, `ad`, `soru`, `tur` (`fizik` | `istatistik` | `literatur` | `veri` | `altyapi`),
`durum` (`aday` | `kosuyor` | `kapandi` | `rakip` | `kapali-sartli` | `birlesti` | `elendi`),
`hukum` (`H0` | `H1` | `ayirt-edilemez` | `veri-yok` | `guc-yok` | `rakip` | `-`),
`sonuc`, `ders`, `yeniden_acma_sarti`, `istanbul_etkisi`, `maliyet_eur`, `tarih`, `sahip`, `kayit`, `kaynaklar`, `etiket`.

`durum` anlamları: `rakip` = donduruldu, ileri test defterinde v1.3b'nin yanında; `kapali-sartli` = yalnız yazılı şart sağlanırsa açılır;
`birlesti` = başka adayın içine alındı (`kayit` alanı hangisi olduğunu söyler); `elendi` = taramada elendi, koşulmadı.

## Dürüstlük notu

Yıl ölçeğinde (ör. "şu 1–3 yıl içinde") deprem tahmini bugün hiçbir yerde ileriye dönük testte kanıtlanmış değildir.
Bu defterdeki her aday bir **sınama önerisidir**; "daraltır" ifadesi ancak ön kayıt + sızıntı kapısı + görülmemiş veriyle ölçülmüş bilgi kazancından sonra kullanılır.
