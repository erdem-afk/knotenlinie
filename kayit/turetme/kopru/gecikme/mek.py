import json,os,sys
out={}
for f in os.listdir(sys.argv[1]):
    try: j=json.load(open(os.path.join(sys.argv[1],f)))
    except Exception: continue
    pr=j.get('properties',{}).get('products',{})
    rk=None
    for key in ('moment-tensor','focal-mechanism'):
        for p in pr.get(key,[]):
            v=p.get('properties',{})
            if 'nodal-plane-1-rake' in v:
                rk=(float(v['nodal-plane-1-rake']),float(v.get('nodal-plane-2-rake',v['nodal-plane-1-rake']))); break
        if rk: break
    out[f[:-5]]=rk
json.dump(out,open(sys.argv[2],'w'))
ss=[k for k,v in out.items() if v and min(abs(v[0]),abs(abs(v[0])-180))<=30 and min(abs(v[1]),abs(abs(v[1])-180))<=30]
print('toplam',len(out),'mekanizmalı',sum(1 for v in out.values() if v),'doğrultu atımlı',len(ss))
json.dump(ss,open(sys.argv[3],'w'))
