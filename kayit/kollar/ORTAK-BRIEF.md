# Kol brief'i (ortak kısım) — 11 Kasım 2026

Sen bir araştırma kolunun başısın (Fable). Alt işleri Agent aracıyla **model "opus"** alt ajanlara ver (en çok 3 alt ajan, her birine dar ve kendi başına anlaşılır brief; bu dosyanın yolunu da ver). Sentezi ve hükmü sen yazarsın. Mümkünse `anthropic-skills:deep-research` skill'ini yükleyip onun düzeniyle çalış.

## Proje ve amaç
Knotenlinie: İstanbul/Marmara için sınanmış olasılıksal deprem tahmini. Bugünkü durum: nihai model v1.3b donduruldu (Marmara M7+ segment olasılıkları; zaman ekseni Poisson 0,95 / BPT 0,05). 30 yıllık aralığın kaynakları İstanbul için: uzamsal eksen ≈%46, dal içi parametreler ≈%37 (kayma açığı, Mchar), tekrar süresi ≈%6, zaman ≈%11.
Erdem'in hedefi: olasılığı **zaman ekseninde** daraltmak, 30 yıl ölçeğinden yıl ölçeğine doğru (M7+ olmuyorsa M6+), ve bunun yapılabildiğini **sınanmış biçimde** göstermek. Var olanı taklit etmiyoruz: literatür boşluklarını bulup İstanbul'a "büküyoruz" (başka bölge/alan için geliştirilmiş, İstanbul'a hiç uygulanmamış ya da hiç ileriye dönük sınanmamış yöntem ve veriler).

## Dürüstlük (bağlayıcı)
- Yıl ölçeğinde deprem tahmini bugün hiçbir yerde ileriye dönük testte kanıtlanmış değil. Hiçbir adayı "çalışır" diye sunma; her aday bir **sınama önerisi**.
- Her iddia: ön kayıt (kural veriden önce dondurulur), sızıntı kapısı (girdi yayım tarihi < hedef olay), görülmemiş veri, rakibe göre log skor (nat). Örneklem küçükse önce güç hesabı; güç yoksa "önceden ayırt edilemez" de.
- Kaynak uydurma. Her kaynak için DOI ver ve DOI'yi gerçekten çözdür (doi.org ya da OpenAlex/Crossref). Okuyamadığın (ödeme duvarı) makaleyi "özetten" diye işaretle.
- Kör veri (Türkiye dışı 2026 katalogları, 2027+) okunmaz. Mutlak İstanbul olasılığı yazılmaz.

## Önce defter
`/home/user/knotenlinie/kayit/README.md` oku. Her fikir için önce `python3 /home/user/knotenlinie/kayit/kayit.py ara <kelime>` çalıştır. Kapanmış adayı (54 satır: S-1…7, Y-1…3, DY-1…5, DK-1…5, DD-1…5, DT-1…5, DV-K1…5, K10, çekirdek) yeniden önerme; ancak `yeniden_acma_sarti` sağlanıyorsa ya da gerçekten farklı bir mekanizmaysa öner ve farkı tek cümleyle yaz.
Bilinen sonuçlar (yeniden keşfetme): Coulomb gerilme aktarımı M7 doğrulamalarında ≈0; BPT/yenilenme sınavda Poisson'dan kötü; küresel CRS ve gelgit ≈0; asismik geçici çarpanı ayırt edilemez; PIF kilitlenmesi karadan ölçülemiyor; ETAS kısa vadede çok güçlü rakip.

## Araçlar
- Literatür: WebSearch/WebFetch; OpenCitations `https://api.opencitations.net/index/v2/citations/doi:<doi>` (anahtarsız, eş-atıf kesişimi için tercih et); OpenAlex anahtarı Doppler'da: `curl -s -H "Authorization: Bearer $DOPPLER_TOKEN" "https://api.doppler.com/v3/configs/config/secret?project=knotenlinie&config=prd&name=OPENALEX_API_KEY"` (değeri ekrana yazdırma, kabuk değişkenine al; arama 10 kredi, istekler arası ≥1 s, 429'da bekle; bütçe diğer kollarla ortak, idareli kullan). Çok kelimeli aramada `search=` kullan.
- Köprü ölçüm betikleri: `/mnt/project-files/literatur-boslugu/v3/bosluk_olc_v3.py` (OpenCitations) ve `../bosluk_olc_v2.py` (OpenAlex). /mnt/project-files ağ bağlantısıdır: tümünü tarama, yolun sonuna / koy.
- OUP/Wiley bot korumasını atlatmaya çalışma.
- Para harcama yok, makine kiralama yok. Sunucuya (knotenlinie-depo) erişimin yok.

## Çıktı (yalnız bu üç dosyaya yaz; git komutu ÇALIŞTIRMA, commit'i ben yaparım)
1. `/home/user/knotenlinie/kayit/kollar/<KOL>.md` — Türkçe, kısa. Bölümler: (a) tarama özeti: ne arandı, köprü ölçüleri (kesişim k, Jaccard, pozitif kontrol); (b) **aday tablosu**, her aday için: kimlik (`<ÖNEK>-1…`), soru, neden yeni (öncül taraması: en yakın 2–3 iş, DOI), zaman eksenine nasıl dokunur (hangi vade: gün/ay/yıl; M6+/M7+), sınama tasarımı (H1/H0, rakip, hedef olay kümesi ve kaba N, güç tahmini, sızıntı riski), veri (açık mı, URL, boyut), maliyet/süre, tür (`fizik` iş paketi mi, yoksa `literatur`/`veri` işi mi), senin hükmün (öner / bekle / eleme) ve gerekçe; (c) elenenler ve neden; (d) dürüst sınır.
2. `/home/user/knotenlinie/kayit/kollar/<KOL>.adaylar.jsonl` — defter biçiminde satırlar (README'deki alanlar; `durum` "aday" ya da "elendi").
3. `/home/user/knotenlinie/kayit/kollar/<KOL>.doi.txt` — kullandığın kaynakların DOI'leri, satır başına bir tane.
En çok 6 aday; azı daha iyi. Zaman sınırı: yaklaşık 40 dakika. Son mesajında yalnız 10 satırlık özet ver (aday kimlikleri, tek cümle hüküm).
