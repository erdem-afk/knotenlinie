import json,sys,urllib.request,urllib.parse
K=open(sys.argv[1]).read().strip()
def g(path,**q):
    q["api_key"]=K; u="https://api.openalex.org/"+path+"?"+urllib.parse.urlencode(q)
    import time
    for i in range(6):
        try:
            time.sleep(1.1); return json.load(urllib.request.urlopen(u,timeout=60))
        except Exception as e:
            time.sleep(2**i)
    raise RuntimeError("openalex")
for line in open(sys.argv[2]):
    t=line.strip()
    if not t or t.startswith("#"): print(t); continue
    d=g("works",search=t,select="id,doi,title,publication_year,cited_by_count,authorships",**{"per-page":3})
    for r in d["results"][:2]:
        a=(r["authorships"][0]["author"]["display_name"] if r["authorships"] else "?")
        print(f"  {r['publication_year']} {a[:18]:18} c={r['cited_by_count']:5} {r['doi']} | {r['title'][:90]}")
