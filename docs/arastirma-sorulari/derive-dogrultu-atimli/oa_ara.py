import json,sys,urllib.request,urllib.parse,os,time
def G(u):
    for i in range(7):
        try: return json.load(urllib.request.urlopen(u,timeout=120))
        except Exception: time.sleep(2**i)
    return {'results':[],'meta':{'count':-1}}
K=open(sys.argv[1]).read().strip(); Q=json.load(open(sys.argv[2])); out={}
for ad,qs in Q.items():
    res={}
    for q in qs:
        u="https://api.openalex.org/works?"+urllib.parse.urlencode({"search":q,"per-page":15,"sort":"relevance_score:desc","select":"id,doi,title,publication_year,cited_by_count","api_key":K})
        d=G(u); time.sleep(1)
        for r in d["results"]: res[r["id"].split("/")[-1]]=[r["publication_year"],r["cited_by_count"],r["title"],r.get("doi")]
        print(f"## {ad} | {q} | n={d['meta']['count']}")
    out[ad]=res
    for k,v in sorted(res.items(),key=lambda x:-(x[1][0] or 0)): print("  ",v[0],v[1],(v[2] or "")[:130])
json.dump(out,open(sys.argv[3],"w"),ensure_ascii=False,indent=1)
