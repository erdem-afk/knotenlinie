#!/usr/bin/env python3
"""TR-6c İNCELEME-2: sürüm 2 için kaynak düzeyi mutasyon sınaması (yalnız yapay veri).

Her mutant için tr6/ dizininin .py/.json/.txt dosyaları geçici bir ayna dizine kopyalanır (kayit/onkayit bağlantıyla),
mutasyon tam bir kez geçen bir metin değişikliğiyle uygulanır ve yazarın sınamalarından seçilen sınıflar koşulur.
Mutant "yakalandı" ⟺ sınama çıkış kodu ≠ 0. Depodaki dosyalara dokunulmaz.

Kullanım: python3 -I -B kayit/turetme/tr6/inc_c2/inc_c2_mutasyon.py <geçici_dizin> <çıktı.json> [sınıf ...]
(varsayılan sınıflar: TTasarimC)
"""
import json
import os
import shutil
import subprocess
import sys
import time

BURA = os.path.dirname(os.path.abspath(__file__))
TR6 = os.path.dirname(BURA)
DEPO = os.path.abspath(os.path.join(TR6, "..", "..", ".."))

K, Y = "tr6a_kosu.py", "tr6a_yapay.py"
MUTANTLAR = [
    ("N1 havuz kapıdan sonra (K_kapı birimleri; v1'e dönüş)", K,
     'kal_k, _, _ = self.kume_seti([u for u in hazir if self.B[u]["secim"]])',
     'kal_k, _, _ = self.kume_seti(gecen)'),
    ("N2 kenar kümeleri havuzdan çıkmaz", K,
     'kal_k = [c for c in kal_k if c["temsilci"] not in kenar]', 'kal_k = list(kal_k)'),
    ("N3 havuz yalnız sahtesi önceden hesaplanmış (K_kapı) kümelerden", K,
     'gec = [r for c in kal_k for r in sahte[c["temsilci"]] if r["gecerli"]]',
     'gec = [r for c in kal_k if c["temsilci"] in [x["temsilci"] for x in kal] for r in sahte[c["temsilci"]] if r["gecerli"]]'),
    ("N4 manifest çekirdeğinde kalibrasyon listesi yok", K, 'c["kalibrasyon_kumeleri"] = m["kalibrasyon_kumeleri"]', "pass"),
    ("N5 S1/S7 süzgeci ≤ yerine < 0 (hep çıkar)", K, 'return B["kapi"][B["secim"]][lob]["N0"] <= N0_UST_C',
     'return B["kapi"][B["secim"]][lob]["N0"] <= 0'),
    ("N6 S2'de kenar kümesi kalır", K, "continue                     # TR-6c §C4 kural 7", "pass                     # TR-6c §C4 kural 7"),
    ("N7 Y p'si paydası K (KY değil)", K, "p_Y_p0arti=(ust_kuyruk(Y, KY, p0p)", "p_Y_p0arti=(ust_kuyruk(Y, K, p0p)"),
    ("N8 ters yön eşiği c⁺(K) (K_Y değil)", K, 'cp = S.kritik(T["ana"].get("K_Y", K), p0p)', "cp = S.kritik(K, p0p)"),
    ("N9 tamlık elemesinden sonra S7 süzgeci yok", K,
     'm2["K_nt"] = [c["temsilci"] for c in ana if kp(c["temsilci"])["notr"]["N0"] >= ESIK[19.0]\n                      and self._kontrol_kenar_disi(c["temsilci"], "notr")]',
     'm2["K_nt"] = [c["temsilci"] for c in ana if kp(c["temsilci"])["notr"]["N0"] >= ESIK[19.0]]'),
    ("N10 C1 havuzu kapı koşullu (sürüm 1)", Y, 'f = _fark_se(c["SD"], c["J"], c["D"][kv])',
     'f = _fark_se(c["SD"][kv], c["J"][kv], c["D"][kv])'),
    ("N11 C1′b (ii)'ye de uygulanır", Y, 'if ad.startswith("i:"):', "if True:"),
    ("N12 karma aralığı 20–60 → 30–60", Y, "KARMA_C = (20.0, 60.0)", "KARMA_C = (30.0, 60.0)"),
    ("N13 bağlayıcı parça koruması (sha boşken) yok", Y, "if baglayici and KO.TR6C_ONKAYIT_SHA is None:", "if False:"),
    ("N14 kenar A'sı 0 (sürüm 1 davranışı)", K, 'r["A_kenar_oncesi"], r["A"], r["kenar_etkisi"] = r["A"], None, True',
     'r["A_kenar_oncesi"], r["A"], r["kenar_etkisi"] = r["A"], 0, True'),
]


def ayna(kok):
    hedef = os.path.join(kok, "kayit", "turetme", "tr6")
    os.makedirs(hedef)
    for f in os.listdir(TR6):
        if f.endswith((".py", ".json", ".txt")) and os.path.isfile(os.path.join(TR6, f)):
            shutil.copy2(os.path.join(TR6, f), hedef)
    os.symlink(os.path.join(DEPO, "kayit", "onkayit"), os.path.join(kok, "kayit", "onkayit"))
    return hedef


def main():
    gecici, cikti = sys.argv[1], sys.argv[2]
    siniflar = sys.argv[3:] or ["TTasarimC"]
    sonuc = []
    for i, (ad, dosya, eski, yeni) in enumerate([("M0 mutasyonsuz", K, "", "")] + MUTANTLAR):
        kok = os.path.join(gecici, f"m{i:02d}")
        if os.path.exists(kok):
            shutil.rmtree(kok)
        h = ayna(kok)
        if eski:
            y = os.path.join(h, dosya)
            metin = open(y, encoding="utf-8").read()
            assert metin.count(eski) == 1, (ad, metin.count(eski))
            open(y, "w", encoding="utf-8").write(metin.replace(eski, yeni))
        t = time.time()
        p = subprocess.run([sys.executable, "-I", "-B", os.path.join(h, "tr6a_test_yapay.py")] + siniflar,
                           capture_output=True, text=True, timeout=3600)
        son = (p.stderr.strip().splitlines() or [""])[-1]
        hatalar = [s for s in p.stderr.splitlines() if s.startswith(("FAIL:", "ERROR:"))]
        sonuc.append(dict(ad=ad, yakalandi=p.returncode != 0, son_satir=son, hatalar=hatalar,
                          sure_s=round(time.time() - t, 1)))
        print(ad, "YAKALANDI" if p.returncode else "yakalanmadı", son, flush=True)
        shutil.rmtree(kok)
    with open(cikti, "w", encoding="utf-8") as f:
        json.dump(dict(siniflar=siniflar, mutantlar=sonuc), f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
