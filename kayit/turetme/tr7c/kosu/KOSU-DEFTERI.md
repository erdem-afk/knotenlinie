# TR-7c koşu defteri (E-3)

Koşu yeri: kiralık Hetzner makinesi `knotenlinie-turetme`, depo kopyası `~/tr7c-repo` (yerel çıplak `origin`).
Sıra (KOSU-DONDURMA-EKI §0, E-3): sunucuda `baslat` → commit → paketle bulut oturumuna → aynı commit kimliğiyle GitHub
dalına push → `git ls-remote` doğrulaması → bu deftere kayıt → ancak sonra `kos`.

Koşu dondurması: commit a278070 (18 Kasım 2026 01:47Z push).

| Aşama | `baslat` commit | GitHub'da doğrulandı (UTC) | `kos` başladı (UTC) | Bitti / not |
|---|---|---|---|---|
| manifest | 4a92cd79e7598a3d4c8d9e5febcc245978537335 | 2026-11-18T01:48:20Z | 2026-11-18T01:48:58Z | 02:29:25Z tamamlandı; çıktı commit cbee35ed (GitHub 02:30:11Z); manifest sha 97e7fefd…; yalnız üstveri ve katalog (4,3 MB), dalga formu yok |
| K1c-indirme | 6c588474fe8ab513591bfbd4a9fcf429b0e7c16c | 2026-11-18T02:30:17Z | 2026-11-18T02:30:3xZ (defter commit abae26f sonrası) | 05:28:07Z tamamlandı; çıktı commit 561e18ee (GitHub 06:30:13Z); 2197 zarf + 148 uzun dönem dosyası, 1,3 GB; kesinti yok |
| K1c-negatif | 9a77f8572a238640ce36efd61249175d786ee11a | 2026-11-18T06:30:19Z | bu defter satırının commit'inden hemen sonra | |
