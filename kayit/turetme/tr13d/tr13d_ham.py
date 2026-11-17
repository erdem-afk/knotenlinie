#!/usr/bin/env python3
"""TR-13d ham indirmeleri paketler ve ağ dizinine yazar (dizin taranmaz; yol sonunda eğik çizgi).

AUTH dosyası (finalcat.cat) 2026 satırları da içeriyor: pakete yalnız 2026-01-01'den önceki satırlar konur; özgün
dosyanın sha256'sı ayrıca yazılır. JMA .npz ara dosyaları pakete girmez (zip'lerden yeniden kurulur).

Kullanım: python3 -I -B tr13d_ham.py <ham_dizin/> <ag_dizin/> <sha_liste.txt>
"""
import hashlib
import io
import os
import re
import sys
import tarfile
import time

sys.dont_write_bytecode = True


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_dosya(yol):
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(ham, ag, liste):
    assert ham.endswith("/") and ag.endswith("/")
    ad = "tr13d_ham_2026-11-17.tar.gz"
    yerel = os.path.join(os.path.dirname(ham.rstrip("/")), ad)
    satir, auth_not = [], []
    with tarfile.open(yerel, "w:gz") as tf:
        for kok, _, dosyalar in sorted(os.walk(ham)):
            for f in sorted(dosyalar):
                if f.endswith(".npz") or f.endswith(".tmp"):
                    continue
                yol = os.path.join(kok, f)
                b = open(yol, "rb").read()
                rel = "ham/" + os.path.relpath(yol, ham)
                if "onbellek_AUTH" in kok and re.search(rb"\n2026-", b):
                    ozg = sha(b)
                    b = b"".join(s for s in io.BytesIO(b).readlines() if not s.startswith(b"2026-"))
                    auth_not.append(f"{rel}: özgün sha256 {ozg} (2026 satırları dahil, pakete girmedi); "
                                    f"paketteki <2026 kopya sha256 {sha(b)}")
                ti = tarfile.TarInfo(rel)
                ti.size = len(b)
                ti.mtime = int(time.time())
                tf.addfile(ti, io.BytesIO(b))
                satir.append(f"  {sha(b)}  {rel}")
    h1 = sha_dosya(yerel)
    hedef = ag + ad
    os.makedirs(ag, exist_ok=True)
    with open(yerel, "rb") as s_, open(hedef, "wb") as d_:
        for b in iter(lambda: s_.read(1 << 20), b""):
            d_.write(b)
    time.sleep(10)
    h2 = sha_dosya(hedef)
    assert h1 == h2, (h1, h2)
    boy = os.path.getsize(hedef)
    with open(liste, "w") as f:
        f.write("TR-13d ham veri (depoda değil). 17 Kasım 2026. Bütün sorguların bitişi < ana şok ve <= 2025-12-31.\n\n")
        f.write(f"Arşiv: {hedef} ({boy} B)\n  sha256 {h1}\n  (yazıldıktan ≈ 10 sn sonra yeniden okundu: uyuşuyor)\n\n")
        for n in auth_not:
            f.write("AUTH notu: " + n + "\n")
        f.write("\nİçerik (dosya başına sha256):\n" + "\n".join(satir) + "\n")
    print(hedef, boy, h1, len(satir))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
