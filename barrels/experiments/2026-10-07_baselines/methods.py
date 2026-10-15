import cv2,numpy as np,glob,os,json
D='/home/claude/cd/color_data/'
def grayworld(im):
    f=im.astype(np.float32); m=f.reshape(-1,3).mean(0); g=m.mean()/m
    return np.clip(f*g,0,255).astype(np.uint8)
def hsv_masks(im):
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); H,S,V=[hsv[:,:,i].astype(int) for i in range(3)]
    o=((H<=20)|(H>=170))&(S>=120)&(V>=70)
    b=(H>=90)&(H<=130)&(S>=120)&(V>=50)
    return o,b
def lab_masks(im):
    lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(int); L,a,b=lab[:,:,0],lab[:,:,1]-128,lab[:,:,2]-128
    o=(a>=30)&(b>=15)&(L>40)
    bl=(b<=-18)&(a<=25)&(L>25)
    return o,bl
def shades_of_gray(im,p=6):
    f=im.astype(np.float32)+1; m=(f.reshape(-1,3)**p).mean(0)**(1/p); g=m.mean()/m
    return np.clip(f*g,0,255).astype(np.uint8)
def white_patch(im):
    f=im.astype(np.float32); m=np.percentile(f.reshape(-1,3),99,axis=0); g=255/m
    return np.clip(f*g,0,255).astype(np.uint8)
METHODS={
 'A_hsv_fixed':lambda im:hsv_masks(im),
 'B_grayworld+hsv':lambda im:hsv_masks(grayworld(im)),
 'C_grayworld+lab':lambda im:lab_masks(grayworld(im)),
 'D_shadesgray+hsv':lambda im:hsv_masks(shades_of_gray(im)),
 'E_whitepatch+hsv':lambda im:hsv_masks(white_patch(im)),
}
def clean(m):
    k=np.ones((3,3),np.uint8); return cv2.morphologyEx(m.astype(np.uint8),cv2.MORPH_OPEN,k)>0
files=sorted(glob.glob(D+'4A8B_*.png'))
# probes for core images (from grid.py)
res={}
for mname,fn in METHODS.items():
    res[mname]={}
    for f in files:
        name=os.path.basename(f)[5:-4]; im=cv2.imread(f); o,b=fn(im); o,b=clean(o),clean(b)
        res[mname][name]=(o,b)
json.dump({},open('/dev/null','w'))
# metrics
grid=json.load(open('grid_stats.json'))
print("METRICS (label-free): core images = 9 lamp settings, same scene")
print(f"{'method':18s} | orange-body recall | blue-stripe recall | wood flagged orange | neg-image FP% (o/b)")
table={}
for mname in METHODS:
    orr,sr,wf=[],[],[]
    for f in sorted(glob.glob(D+'4A8B_*_wood_core_01.png')):
        name=os.path.basename(f)[5:-4]; light=name.split('_')[0]
        im=cv2.imread(f); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
        x0,x1=(320,360) if light=='upcool' else (360,400)
        band=hsv[150:400,x0:x1]; bl=((band[:,:,0]>95)&(band[:,:,0]<130)&(band[:,:,1]>80)).mean(1)
        r=np.where(bl>0.6)[0]; y0,y1=150+r.min(),150+r.max()
        o,b=res[mname][name]
        orr.append(np.concatenate([o[y0-28:y0-8,x0:x1].ravel(),o[y1+8:y1+28,x0:x1].ravel()]).mean())
        sr.append(b[y0+2:y1-1,x0:x1].mean()); wf.append(o[400:470,20:200].mean())
    o,b=res[mname]['atwarm_wood_neg_01']
    table[mname]=dict(orange=orr,stripe=sr,wood=wf,neg=(o.mean(),b.mean()))
    print(f"{mname:18s} | {np.mean(orr)*100:5.1f}% (min {np.min(orr)*100:4.0f}) | {np.mean(sr)*100:5.1f}% (min {np.min(sr)*100:4.0f}) | {np.mean(wf)*100:5.1f}% (max {np.max(wf)*100:4.0f}) | {o.mean()*100:4.1f} / {b.mean()*100:4.1f}")
lights=[os.path.basename(f)[5:].split('_')[0] for f in sorted(glob.glob(D+'4A8B_*_wood_core_01.png'))]
print("\nper-lighting blue-stripe recall:")
for m in METHODS: print(f"  {m:18s}", ' '.join(f"{l}:{v*100:.0f}" for l,v in zip(lights,table[m]['stripe'])))
print("per-lighting wood flagged as orange:")
for m in METHODS: print(f"  {m:18s}", ' '.join(f"{l}:{v*100:.0f}" for l,v in zip(lights,table[m]['wood'])))
json.dump({m:{k:(np.array(v).tolist() if k!='neg' else v) for k,v in t.items()} for m,t in table.items()}|{'lights':lights},open('metrics.json','w'),default=float)
# overlays
os.makedirs('overlays',exist_ok=True)
for mname in METHODS:
    tiles=[]
    for f in files:
        name=os.path.basename(f)[5:-4]; im=cv2.imread(f); o,b=res[mname][name]
        ov=(im*0.35).astype(np.uint8); ov[o]=(0,140,255); ov[b]=(255,90,0)
        t=cv2.resize(np.hstack([im,ov]),(480,180))
        cv2.putText(t,name,(4,14),0,0.45,(0,0,0),3); cv2.putText(t,name,(4,14),0,0.45,(255,255,255),1)
        tiles.append(t)
    while len(tiles)%3: tiles.append(np.full_like(tiles[0],255))
    rows=[np.hstack(tiles[i:i+3]) for i in range(0,len(tiles),3)]
    cv2.putText(rows[0],mname,(4,175),0,0.6,(0,255,255),2)
    cv2.imwrite(f'overlays/{mname}.png',np.vstack(rows))

print("\nWood directly in front of/below barrels (y380-470, x150-600), fraction flagged orange:")
for mname in METHODS:
    v=[res[mname][os.path.basename(f)[5:-4]][0][380:470,150:600].mean() for f in sorted(glob.glob(D+'4A8B_*_wood_core_01.png'))]
    table[mname]['wood_center']=v
    print(f"  {mname:18s} mean {np.mean(v)*100:4.1f}%  ", ' '.join(f"{l}:{x*100:.0f}" for l,x in zip(lights,v)))
print("\nWhole top third of frame (background: wall/mug/box), fraction flagged blue:")
for mname in METHODS:
    v=[res[mname][os.path.basename(f)[5:-4]][1][0:150,:].mean() for f in sorted(glob.glob(D+'4A8B_*_wood_core_01.png'))]
    table[mname]['bg_blue']=v
    print(f"  {mname:18s} mean {np.mean(v)*100:4.1f}%")
json.dump({m:{k:(np.array(v).tolist() if k!='neg' else v) for k,v in t.items()} for m,t in table.items()}|{'lights':lights},open('metrics.json','w'),default=float)
