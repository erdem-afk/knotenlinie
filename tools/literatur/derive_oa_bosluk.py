"""Japonya/Cascadia/Şili/Hikurangi yöntem aileleri -> Marmara boşluk ölçümü (10 Kasım 2026).
Her aile: tohum atıf yapanları içinde başlık/özet 'Marmara|Istanbul|North Anatolian' geçen işler.
Pozitif kontrol: aynı atıf yapanlar içinde köken bölge (Japan|Cascadia|Chile|Nankai|Hikurangi)."""
import json,os,sys,urllib.request,urllib.parse,time
K=os.environ["OPENALEX_API_KEY"]
def get(p,**q):
    q["api_key"]=K; u="https://api.openalex.org/"+p+"?"+urllib.parse.urlencode(q)
    for i in range(5):
        try: return json.load(urllib.request.urlopen(u,timeout=90))
        except Exception as e:
            if i==4: raise
            time.sleep(2**i)
A=json.load(open(sys.argv[1]))
TR='"Marmara" OR "Istanbul" OR "North Anatolian"'
KOK='Japan OR Cascadia OR Chile OR Nankai OR Hikurangi OR Tohoku OR subduction'
out={}
for ad,ws in A.items():
    f="cites:"+"|".join(ws)
    tot=get("works",filter=f,**{"per-page":1})["meta"]["count"]
    kok=get("works",filter=f+",title_and_abstract.search:"+KOK,**{"per-page":1})["meta"]["count"]
    d=get("works",filter=f+",title_and_abstract.search:"+TR,**{"per-page":50},select="id,doi,title,publication_year")
    tr=d["meta"]["count"]
    out[ad]={"atif_toplam":tot,"koken_bolge":kok,"marmara":tr,"oran_marmara_koken":tr/max(kok,1),
             "marmara_isleri":[[r["publication_year"],r["title"],r["doi"]] for r in d["results"]]}
    print(f"{ad:10} toplam {tot:5d} köken {kok:5d} Marmara {tr:3d} oran {tr/max(kok,1):.4f}")
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
