"""TR-6a ön kaydı sürüm 3: `tr6a_onkayit_sayilar.py --md` çıktısındaki her tablo satırının ön kayıt metninde birebir
(tam satır olarak) bulunduğunu denetler. Ayrılma satırları (|---|) sayılmaz. Gerçek veri okumaz, ağ yok.

Kullanım: python3 -I -B tr6a_md_denetim.py [ön_kayıt.md]
          (varsayılan: kayit/onkayit/TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md)
Çıkış kodu: 0 bütün satırlar var; 1 eksik satır var (eksikler basılır).
"""
import os, subprocess, sys

BURAYA = os.path.dirname(os.path.abspath(__file__))
VARSAYILAN = os.path.join(BURAYA, "..", "..", "onkayit", "TR-6a_gerilme-olcer-kor-dogrulama_ONKAYIT.md")


def main(md_yol):
    cikti = subprocess.run([sys.executable, "-I", "-B", os.path.join(BURAYA, "tr6a_onkayit_sayilar.py"), "--md"],
                           capture_output=True, text=True, check=True, cwd=BURAYA).stdout
    satirlar = [s.rstrip() for s in cikti.splitlines() if s.startswith("|") and not s.startswith("|---")]
    metin = {s.rstrip() for s in open(md_yol, encoding="utf-8").read().splitlines()}
    eksik = [s for s in satirlar if s not in metin]
    print(f"--md tablo satırı: {len(satirlar)}; metinde birebir: {len(satirlar) - len(eksik)}; eksik: {len(eksik)}")
    for s in eksik:
        print("EKSİK:", s)
    return 1 if eksik else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else VARSAYILAN))
