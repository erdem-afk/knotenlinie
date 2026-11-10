import json,os,sys,urllib.request,urllib.parse
K=os.environ["OPENALEX_API_KEY"]; out={}
Q=json.load(open(sys.argv[1]))
for s,qs in Q.items():
  out[s]={}
  for q in qs:
    u="https://api.openalex.org/works?"+urllib.parse.urlencode({"search":q,"per-page":25,"select":"id,doi,title,publication_year,cited_by_count","api_key":K})
    d=json.load(urllib.request.urlopen(u,timeout=60))
    out[s][q]={"n":d["meta"]["count"],"top":[[r["id"].split("/")[-1],r["publication_year"],r["cited_by_count"],r["title"],r["doi"]] for r in d["results"]]}
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
for s in out:
  for q,v in out[s].items():
    print("==",s,"|",q,"| n=",v["n"])
    for r in v["top"][:15]: print("  ",r[1],r[2],(r[3] or "")[:120])
