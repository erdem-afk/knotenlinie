"""A3 kural 2.1 §2 egri sayisallastirma + okunabilirlik kapisi (Illapel, Metois 2012 Sekil 8).
Maske: RGB uzakligi <= 60, referans renk (255,0,0). Cizim alani: kirmizi y ekseni cizgisi ile
x ekseninin sag ucu arasi, y ekseni 0.00 ve 1.00 centikleri arasi. Ikinci kume: bir sutundaki maske
pikselleri bosluk > 3 px ile ayrilan birden fazla dikey parcaya bolunuyorsa."""
import sys, json, numpy as np
from PIL import Image
im=np.array(Image.open(sys.argv[1]).convert('RGB')).astype(int)
ref=np.array([255,0,0]); m=np.sqrt(((im-ref)**2).sum(-1))<=60
# y ekseni: en uzun kirmizi dikey kosu olan sutun (sayfanin ust yarisi)
H=im.shape[0]//3; col=m[:H].sum(0); xa=int(np.argmax(col))
ys=np.nonzero(m[:H,xa])[0]; y_top,y_bot=int(ys.min()),int(ys.max())
# centikler: eksenin hemen solunda kirmizi yatay parcalar
left=m[:H,xa-25:xa-3].sum(1); tick_y=[]
for y in np.nonzero(left>10)[0]:
    if not tick_y or y-tick_y[-1][-1]>3: tick_y.append([y])
    else: tick_y[-1].append(y)
tick_y=[float(np.mean(t)) for t in tick_y]
# x ekseni: siyah yatay cizgi y_bot civari; sag uc
blk=(im.sum(-1)<150)
row=int(y_bot); xs=np.nonzero(blk[row-6:row+7].any(0))[0]; xs=xs[xs>xa]
# sag uca kadar ardisik kosu
run=[xs[0]]
for x in xs[1:]:
    if x-run[-1]<=2: run.append(x)
    else: break
x_right=int(run[-1])
y1,y0=tick_y[0],tick_y[-1]   # 1.00 ve 0.00
alan=m[int(y1)-2:int(y0)+3, xa+6:x_right]
egrili=0; ikinci=0
for j in range(alan.shape[1]):
    r=np.nonzero(alan[:,j])[0]
    if len(r)==0: continue
    egrili+=1
    if (np.diff(r)>3).any(): ikinci+=1
pay=ikinci/max(egrili,1)
# bindirme goruntusu
ov=(im*0.35+165).astype('uint8'); sub=ov[int(y1)-2:int(y0)+3, xa+6:x_right]; sub[alan]=[0,90,255]
Image.fromarray(ov[max(0,int(y1)-200):int(y0)+200, max(0,xa-300):x_right+100]).save(sys.argv[2])
res=dict(y_ekseni_x=xa,centik_y=tick_y,x_sag=x_right,egrili_sutun=egrili,ikinci_kume_sutun=ikinci,pay=pay,
         hukum='okunamaz' if pay>0.05 else 'okunabilir')
print(json.dumps(res,indent=1)); json.dump(res,open(sys.argv[3],'w'),indent=1)
