import json,os,sys,urllib.request,urllib.parse
K=os.environ["OPENALEX_API_KEY"]
for t in sys.argv[1:]:
    u="https://api.openalex.org/works?"+urllib.parse.urlencode({"search":t,"per-page":1,"api_key":K,"select":"title,publication_year,doi,authorships,abstract_inverted_index,primary_location"})
    import time
    for i in range(6):
        try: r=json.load(urllib.request.urlopen(u,timeout=60))["results"][0]; break
        except Exception: time.sleep(3*2**i)
    ii=r.get("abstract_inverted_index") or {}
    w=sorted(((p,k) for k,ps in ii.items() for p in ps)); ab=" ".join(k for p,k in w)
    au=", ".join(a["author"]["display_name"] for a in r["authorships"][:3])
    src=((r.get("primary_location") or {}).get("source") or {}).get("display_name")
    print(f"### {r['publication_year']} {au} | {src} | {r['doi']}\n{r['title']}\n{ab[:1300]}\n")
