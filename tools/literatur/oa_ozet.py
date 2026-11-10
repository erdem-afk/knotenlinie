import json,os,sys,urllib.request,urllib.parse
K=os.environ["OPENALEX_API_KEY"]; d=json.load(open(sys.argv[1])); pats=sys.argv[3:]; out=[]
seen=set()
for s in d:
  for q,v in d[s].items():
    for r in v["top"]:
      t=r[3] or ""
      if r[0] in seen or not any(p.lower() in t.lower() for p in pats): continue
      seen.add(r[0])
      w=json.load(urllib.request.urlopen("https://api.openalex.org/works/"+r[0]+"?"+urllib.parse.urlencode({"api_key":K}),timeout=60))
      inv=w.get("abstract_inverted_index") or {}
      pos=sorted((p,wd) for wd,ps in inv.items() for p in ps); ab=" ".join(wd for _,wd in pos)
      au=", ".join(a["author"]["display_name"] for a in w["authorships"][:4])
      so=((w.get("primary_location") or {}).get("source") or {}).get("display_name")
      out.append({"id":r[0],"soru":s,"yil":w["publication_year"],"baslik":w["title"],"yazar":au,"kaynak":so,"doi":w["doi"],"atif":w["cited_by_count"],"ozet":ab})
      print("##",s,w["publication_year"],w["title"],"|",au,"|",so,"|",w["doi"]); print(ab[:1500]); print()
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=1)
