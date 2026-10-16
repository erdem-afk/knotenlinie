# Deney Y okuma kuralı (puanlamadan önce donar)

Bu dosya, Kaliforniya (SCSN) ve Yeni Zelanda (GeoNet) güç tezgâhının ölçüm kuralını
`OLCUM.json` üretilmeden önce dondurur. Puanlama sırasında hiçbir seçim değiştirilmez.

## Veri ve mühür

- Kaynak: SCEDC FDSN (SCSN, `minmag=1.0`, `maxdepth=30`) ve GeoNet FDSN
  (`minmag=2.0`, `maxdepth=40`); aylık pencereler, `endtime<=2020-12-31T23:59:59.999999`.
- Kutular: `scsn` = (32.5–36.5 N, 121.0–114.5 W); `geonet` = (43.8–37.0 S, 171.5–178.5 E).
- Bütün satırlar `tools/muhur.py` ile taranır; 2021+ satır yok (`atilan_2021_sonrasi=0`).
- Büyüklük türü karışıktır (SCSN `l`/`c`/`h`/`w`/…, GeoNet `M`/`ML`/`MLv`/`Mw`). Ana ölçüm
  kataloğun yayımladığı büyüklüğü tek ölçek sayar; `(l)`/`(M)` baskın tür alt kümesi
  duyarlılık satırıdır ve hükmü değiştirmez. Ayrı bir ML↔Mw dönüşümü icat edilmez.

## Tamlık

- Dönem Mc: 5 yıllık pencerelerde MBS (maksimum eğrilik + b-kararlılığı; `tools/etas/tamlik.py`).
  Pencere `n<200` ya da MBS kararsızsa MAXC+0.2 (Woessner–Wiemer 2005).
- Kısa süreli terim: HKJ 2006, `Mc_after = max_{M_j>=5, 0<Δt<=30g}(M_j-4.5-0.75 log10 Δt)`.
- Olay başına `Mc95_i = max(Mc_period(t_i), Mc_after(t_i))`.
- Hedef eşiği: `hedef = ceil_0.1(max_period_Mc + 0.2)`; ikinci eşik `hedef+0.1`.
  Küçük ölçek denemesi `taban_mc` ile eşiği yükseltir ve raporda açıkça belirtilir.

## Modeller (hepsi ≤2010 ile ayarlı)

- **D0** düz ETAS, tek Mc = `hedef` (referans Mc0 = hedef, s(t)=1).
- **D1** R-tipi: Mc0 = `min_period_Mc`; olay terimi `s_i=10^{-b(Mc_period(t_i)-Mc0)}`,
  kompansatör dönem parçalarıyla `s(t)=10^{-b(Mc_period(t)-Mc0)}` (GR ölçeği).
- **D2** = D1 + HKJ: `s(t)=10^{-b(max(Mc_period(t),Mc_after(t))-Mc0)}`, HKJ pencereleri
  1 günlük parçalara bölünür; `Mc_olay=mc95`.
- **D3** = D0,D1,D2 ağırlıklı doğrusal karışımı. Ağırlıklar **≤2006** bileşenleriyle
  **2006–2010** günlük Poisson logL'i üzerinde 0,2 adımlı ızgara taramasıyla seçilir;
  puanlanan D3, seçilen ağırlıklarla **≤2010** bileşenlerinin karışımıdır.
- Kesişme kabulü: her iki bölgede de tam çiftler; karesel hücre integrali; izotrop çekirdek.

## Puanlama

- Izgara 0,1°, günlük, hedef olaylar `[test_bas, test_son)` içinde; her UTC gün başında
  yalnız gün başından önceki olaylar geçmişe girer.
- Ölçüm: D1−D0, D2−D1, D3−en iyi tek; eşik `hedef` ve `hedef+0.1`.
- IG = ortalama log(λ_aday/λ_taban) − (Λ_aday−Λ_taban)/N; haftalık blok sandwich SE;
  z = IG/SE. N/S/M `tools/karsilastir/puan.py` ile; bunlar operasyonel tanıdır, kör hüküm değil.
- Tohum 20261011; blok = UTC Pazartesi haftaları.

## Skor defteri

- `$KNOTENLINIE_RUNS/defter/Y/<model>__<bolge>__<donem>__olay.csv.gz` (zaman, enlem, boylam, mw,
  hucre, kutu, gun, lam) ve `…__gun.csv.gz` (gun, Lam_hedef, Lam_hedef1).
- Defterden hesaplanan IG, koşucunun IG'siyle 1e−9 göreli içinde eşleşir (test edilir).

## Küçük ölçek

Yerel makinede yalnız `--taban-mc` ile yükseltilmiş bir eşikte, tek yıllık bir pencere puanlanır:
tam ayar ve 2011–2020 puanlaması hesap sunucusunda ayrı bir koşuyla yapılır. Küçük ölçek
sonuçları tam ölçek hükmü değildir.

## Ek (2026-10-12, Y2, puanlamadan önce): çift kesmesi ve tanı satırı

Bu ek, GeoNet tam koşusu (2011–2020) puanlanmadan önce yazıldı; sonuçlara bakıldıktan sonra değişmez.

- **Kesme (önceden yazılı):** çekirdek `g(r)·1[r ≤ 100 km]` (iki bölgede) ve `f(Δt)·1[Δt ≤ Tmax]`;
  `Tmax` SCSN'de 365,25 gün, GeoNet'te yok. Kırpılmış çekirdek **yeniden normalize edilmez**.
  Aynı kırpılmış çekirdek (a) olay terimine, (b) kompansatöre (zaman: `∫ s(t) f` üstten `Tmax`'a kırpılır;
  uzay: sınır integralinde `min(R², rmax²)`), (c) tahmine (`YanModel.beklenen`: yaşı `Tmax`'ı
  aşan ebeveyn katkı vermez, hücre integrali yalnız disk içi) girer. D0, D1, D2 ve D3 bileşenleri aynı kesmeyi kullanır.
- **Değişmeyenler:** model aileleri, Mc kuralları, D3 ağırlık seçimi (≤2006 bileşenleri, 2006–2010, 0,2 ızgara),
  eşikler, blok SE. Kesme dışındaki kod değişiklikleri yalnız hızdır (seyrek ebeveyn önbelleği, kopyasız doğrulama,
  HKJ penceresini son 30 güne kırpma) ve sayıyı değiştirmez (testle, tam kutu integraliyle eşitlik).
- **GeoNet tam koşusu:** ayar ≤2010, puan 2011–2020, `--taban-mc` yok, hedef = tamlıktan gelen eşik ve +0,1 kutusu.
- **HKJ tanı satırı** (`hkj_tani`, seçim için kullanılmaz): D2−D1 satırlarında D2'nin Λ'sının N'ye ve D1'in Λ'sına oranı,
  ve günleri "D2, D1'den ≥%1 düşük bekliyor" (HKJ etkin) / değil diye bölen N ve Λ.
  Λ_D2/N > 1,05 → D2 fazla tahmin ediyor.

### Ek 2 (2026-10-12, Y2): D2 kompansatör düzeltmesi — ilk koşu hatalıydı

İlk tam GeoNet koşusunda (`OLCUM-tam-geonet-hatali-ilk-kosu.json`, saklandı, hükme girmez) D2'nin tespit
parçaları `max(Mc_dönem, Mc_sonra, hedef)` ile kuruldu; olay terimi ise `mc95 = max(Mc_dönem, Mc_sonra)` kullanıyor.
Yani kompansatör eşiği 3,8'de, olaylar 2,6'dan sayılıyordu: μ=110/gün, Λ_D2/N=5,7. Bu, yukarıdaki D2 tanımına (hedef tabanı yok)
aykırı bir kod hatasıdır; küçük ölçekte `--taban-mc` eşiği zaten dönem Mc'lerine işlediği için görünmemişti.
Düzeltme yalnız `_araliklar_hkj`'de hedef tabanını kaldırır; kural değişmedi. Seçim ölçüte değil kurala uyuma bakılarak
yapıldı, ama ilk koşunun sonuçları görülmüştü; bu yüzden ikinci koşu aynı kurallarla tek kez puanlanır ve ilk koşu raporda anılır.
Ek: seyrek önbellekte |integral| ≤ 1e−12 hücreler saklanmaz (bellek; sonuç etkisi ihmal edilebilir).
