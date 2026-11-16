#!/usr/bin/env python3
"""TR-6c İNCELEME-1: prova parçalarının yeniden üretimi. Seçilen (hücre, parça) için `hucre_parcasi_c(ad, 7311, p)`
bugünkü kodla yeniden koşulur, `prova_c` ile aynı biçimde (json.dump, varsayılan ayırıcılar) geçici dizine yazılır ve
sha256'sı tr6c_prova_<hücre>.json `parca_sha256` listesindekiyle karşılaştırılır. Yalnız yapay veri.

Kullanım: python3 -I -B kayit/turetme/tr6/inc_c/inc_c_parca_sha.py <geçici_dizin> <hücre:parça> ...
"""
import hashlib
import json
import os
import sys

BURA = os.path.dirname(os.path.abspath(__file__))
TR6 = os.path.dirname(BURA)
sys.path.insert(0, TR6)
import tr6a_yapay as Y               # noqa: E402

gecici = sys.argv[1]
os.makedirs(gecici, exist_ok=True)
for x in sys.argv[2:]:
    ad, p = x.rsplit(":", 1)
    p = int(p)
    oz = json.load(open(os.path.join(TR6, f"tr6c_prova_{ad.replace(':', '_')}.json"), encoding="utf-8"))
    y = os.path.join(gecici, f"{ad.replace(':', '_')}_t7311_p{p:03d}.json")
    with open(y, "w", encoding="utf-8") as f:
        json.dump(Y.hucre_parcasi_c(ad, 7311, p), f)
    h = hashlib.sha256(open(y, "rb").read()).hexdigest()
    print(json.dumps(dict(hucre=ad, parca=p, sha256=h, kayitli=oz["parca_sha256"][p], ayni=h == oz["parca_sha256"][p]),
                     ensure_ascii=False), flush=True)
