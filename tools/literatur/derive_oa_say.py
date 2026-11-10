import json,os,sys,urllib.request,urllib.parse,time
K=os.environ["OPENALEX_API_KEY"]
for q in sys.argv[1:]:
    u="https://api.openalex.org/works?"+urllib.parse.urlencode({"filter":"title_and_abstract.search:"+q,"per-page":5,"api_key":K,"select":"title,publication_year,doi"})
    for i in range(6):
        try: d=json.load(urllib.request.urlopen(u,timeout=60)); break
        except Exception: time.sleep(3*2**i)
    print(f"[{d['meta']['count']}] {q}")
    for r in d["results"]: print("   ",r["publication_year"],(r["title"] or "")[:110])
