import cv2,numpy as np,glob,os,json
D='/home/claude/cd/color_data/'
files=sorted(glob.glob(D+'4A8B_*_wood_core_01.png'))
rows=[]
def st(px):
    hsv=cv2.cvtColor(px,cv2.COLOR_BGR2HSV).reshape(-1,3).astype(float)
    lab=cv2.cvtColor(px,cv2.COLOR_BGR2LAB).reshape(-1,3).astype(float)
    h=hsv[:,0].copy(); h[h>150]-=180
    return dict(H=np.median(h),S=np.median(hsv[:,1]),V=np.median(hsv[:,2]),a=np.median(lab[:,1])-128,b=np.median(lab[:,2])-128,L=np.median(lab[:,0])*100/255)
for f in files:
    name=os.path.basename(f)[5:-18]; im=cv2.imread(f); hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
    x0,x1=(320,360) if name=='upcool' else (360,400)
    band=hsv[150:400,x0:x1]; blue=((band[:,:,0]>95)&(band[:,:,0]<130)&(band[:,:,1]>80)).mean(1)
    r=np.where(blue>0.6)[0]; y0,y1=150+r.min(),150+r.max()
    o=np.vstack([im[y0-28:y0-8,x0:x1].reshape(-1,3),im[y1+8:y1+28,x0:x1].reshape(-1,3)])[None]
    s=im[y0+2:y1-1,x0:x1]; w=im[400:470,20:200]
    mean=im.reshape(-1,3).mean(0)[::-1]
    rows.append(dict(light=name,orange=st(o),stripe=st(s),wood=st(w),meanRGB=mean.round(0).tolist()))
json.dump(rows,open('grid_stats.json','w'),indent=1,default=float)
print(f"{'light':9s} | orange H/S/V   a*  b* | blue-stripe H/S/V  a*  b* | wood H/S/V  a*  b* | image mean RGB")
for r in rows:
    o,s,w=r['orange'],r['stripe'],r['wood']
    print(f"{r['light']:9s} | {o['H']:4.0f}{o['S']:4.0f}{o['V']:4.0f} {o['a']:4.0f}{o['b']:4.0f} | {s['H']:4.0f}{s['S']:4.0f}{s['V']:4.0f} {s['a']:4.0f}{s['b']:4.0f} | {w['H']:4.0f}{w['S']:4.0f}{w['V']:4.0f} {w['a']:4.0f}{w['b']:4.0f} | {r['meanRGB']}")
