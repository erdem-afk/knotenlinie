#!/usr/bin/env python3
"""TR-6c İNCELEME-1: kaynak düzeyi mutasyon sınaması (yalnız yapay veri).

Her mutant için tr6/ dizininin .py/.json/.txt dosyaları geçici bir ayna dizine kopyalanır (kayit/onkayit bağlantıyla),
mutasyon tam bir kez geçen bir metin değişikliğiyle uygulanır ve yazarın sınamalarından seçilen sınıflar koşulur.
Mutant "yakalandı" ⟺ sınama çıkış kodu ≠ 0. Depodaki dosyalara dokunulmaz.

Kullanım: python3 -I -B kayit/turetme/tr6/inc_c/inc_c_mutasyon.py <geçici_dizin> <çıktı.json> [sınıf ...]
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
    ("M1 kenar sınırı 500 → 5000", K, "N0_UST_C = 500.0 ", "N0_UST_C = 5000.0 "),
    ("M2 kenar sınırı > yerine ≥ ve 2 kat", K, "if x > N0_UST_C}", "if x >= 2 * N0_UST_C}"),
    ("M3 A = 0 satır listesi yalnız ana gölge", K, 'GOLGE_LOBLARI = ("golge", "D3a", "D3b", "D5", "D8")',
     'GOLGE_LOBLARI = ("golge",)'),
    ("M4 S2'de kenar A sıfırlanmaz", K, 'o = self._kenar_A(dict(o, temsilci=c["temsilci"]))',
     'o = dict(o, temsilci=c["temsilci"])'),
    ("M5 kenar kuralı D'yi de sıfırlar", K, 'r["A_kenar_oncesi"], r["A"], r["kenar_etkisi"] = r["A"], 0, True',
     'r["A_kenar_oncesi"], r["A"], r["D"], r["kenar_etkisi"] = r["A"], 0, 0, True'),
    ("M6 kenar sahteleri p̂₀ havuzuna girer", K,
     'gec = [r for t, x in sahte.items() if t not in kenar for r in x if r["gecerli"]]',
     'gec = [r for t, x in sahte.items() for r in x if r["gecerli"]]'),
    ("M7 manifest çekirdeğinde kenar listesi yok", K, 'c["kenar_birimleri"] = m["kenar_birimleri"]', "pass"),
    ("M8 C1 eşiği 3,5 → 2,0 SE", Y,
     'z=round(z, 2), gecti=bool(abs(z) <= 3.5), bilgi=bilgi))\n\n    if ad.startswith("adim")',
     'z=round(z, 2), gecti=bool(abs(z) <= 2.0), bilgi=bilgi))\n\n    if ad.startswith("adim")'),
    ("M9 C1′ tek yanlı → iki yanlı", Y, "gecti=bool(z <= 3.5)", "gecti=bool(abs(z) <= 3.5)"),
    ("M10 C1′ eşiği 3,5 → 1e9 (hiç tutmamaz)", Y, "gecti=bool(z <= 3.5)", "gecti=bool(z <= 1e9)"),
    ("M11 kenar hücresi sınırı 500 → 1500 (i:1500 C1 alır)", Y, "kenar = N0 > KO.N0_UST_C", "kenar = N0 > 1500.0"),
    ("M12 bağlayıcı katalog tohumu TR-6a'nınki", Y, "TOHUM_KATALOG_C, TOHUM_TAMLIK_C = 20261116, 20261117",
     "TOHUM_KATALOG_C, TOHUM_TAMLIK_C = 20261114, 20261117"),
    ("M13 parça tohumu hücre kodu içermez", Y, "default_rng([tohum, HUCRE_KODU_C[ad], parca])",
     "default_rng([tohum, parca])"),
    ("M14 hücre kodu sırası değişir (ii önce)", Y,
     'tuple([f"i:{x:g}" for x in N0_IZGARA_C] + [f"ii:{x:g}" for x in N0_IZGARA_C]',
     'tuple([f"ii:{x:g}" for x in N0_IZGARA_C] + [f"i:{x:g}" for x in N0_IZGARA_C]'),
    ("M15 parça boyu 1000 → 500", Y, "PARCA_C = 1000", "PARCA_C = 500"),
    ("M16 yapay Mc farkı 0,2 → 0 (kesin değerler N0 ile)", Y, "MC_FARKI_C = 0.2 ", "MC_FARKI_C = 0.0 "),
    ("M17 SE₀ paydasında ort(J) yok", Y, "/ (J_.mean() * math.sqrt(len(J_))))", "/ math.sqrt(len(J_)))"),
    ("M18 bağlayıcı deneme sayısı 20 000 → 2000", Y, "N_BAGLAYICI = 20000", "N_BAGLAYICI = 2000"),
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
