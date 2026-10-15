import cv2,numpy as np,importlib.util,sys
spec=importlib.util.spec_from_file_location('m','methods.py')
src=open('methods.py').read().split('files=sorted')[0]
ns={}; exec(src,ns)
D='/home/claude/cd/color_data/4A8B_'
names=['atcool_wood_core_01','atwarm_wood_core_01','awaywarm_wood_core_01','atmid_wood_shadow_01','atwarm_wood_neg_01','upmid_wood_top&stripe_02']
cols=['raw','A: fixed HSV','B: gray-world + HSV','D: shades-of-gray + HSV']
keys=[None,'A_hsv_fixed','B_grayworld+hsv','D_shadesgray+hsv']
W,H=320,240; rows=[]
hdr=np.full((28,W*4,3),255,np.uint8)
for i,c in enumerate(cols): cv2.putText(hdr,c,(i*W+6,20),0,0.6,(0,0,0),2)
rows.append(hdr)
for n in names:
    im=cv2.imread(D+n+'.png'); tiles=[]
    for k in keys:
        if k is None: t=im.copy()
        else:
            o,b=ns['METHODS'][k](im); o,b=ns['clean'](o),ns['clean'](b)
            t=(im*0.35).astype(np.uint8); t[o]=(0,140,255); t[b]=(255,90,0)
        t=cv2.resize(t,(W,H))
        if k is None: cv2.putText(t,n.replace('_wood','').replace('_01',''),(5,20),0,0.55,(0,0,0),3); cv2.putText(t,n.replace('_wood','').replace('_01',''),(5,20),0,0.55,(255,255,255),1)
        tiles.append(t)
    rows.append(np.hstack(tiles)); rows.append(np.full((4,W*4,3),255,np.uint8))
cv2.imwrite('comparison.png',np.vstack(rows))
