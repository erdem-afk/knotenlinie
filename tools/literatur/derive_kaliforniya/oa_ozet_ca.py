import json,sys,urllib.request,urllib.parse,time
K=open(sys.argv[1]).read().strip(); r=json.load(open(sys.argv[2]))
pat=sys.argv[3:]
seen=set()
for k,v in r["kopruler"].items():
  for i in v["kesisim_isleri"]:
    if i[0] in seen or not any(p.lower() in (i[1] or "").lower() for p in pat): continue
    seen.add(i[0])
    u=f"https://api.openalex.org/works/{i[0]}?api_key={K}&select=id,doi,title,publication_year,authorships,primary_location,abstract_inverted_index"
    for t in range(5):
      try: time.sleep(0.3); w=json.load(urllib.request.urlopen(u,timeout=60)); break
      except Exception: time.sleep(2**(t+1))
    ii=w.get("abstract_inverted_index") or {}
    pos=sorted((p,wd) for wd,ps in ii.items() for p in ps); ab=" ".join(wd for _,wd in pos)
    au=", ".join(a["author"]["display_name"] for a in w["authorships"][:3])
    src=((w.get("primary_location") or {}).get("source") or {}).get("display_name")
    print(f"\n## {w['publication_year']} {au} — {w['title']} [{src}] {w['doi']}\n{ab[:1100]}")
