import sys, os
from collections import deque
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
def key_magenta(im):
    a=np.asarray(im.convert('RGB')).astype(float); r,g,b=a[...,0],a[...,1],a[...,2]
    mag=np.minimum(r,b)-g
    alpha=np.clip(1-(mag-70)/120,0,1)
    # un-mix magenta from semi-transparent edge pixels
    rgb=a.copy()
    for c,m in ((0,255),(1,0),(2,255)):
        rgb[...,c]=np.where((alpha>0.02)&(alpha<0.98),np.clip((a[...,c]-(1-alpha)*m)/np.maximum(alpha,0.02),0,255),a[...,c])
    return Image.fromarray(np.dstack([rgb,alpha*255]).astype(np.uint8),'RGBA')
def components(rgba,grow=13,minpx=30,box=None):
    al=rgba.getchannel('A'); mask=al.point(lambda v:255 if v>128 else 0).filter(ImageFilter.MaxFilter(grow))
    sm=np.asarray(mask.resize((mask.width//4,mask.height//4)))>0
    H,W=sm.shape; seen=np.zeros_like(sm); out=[]
    for y in range(H):
        for x in range(W):
            if sm[y,x] and not seen[y,x]:
                q=deque([(y,x)]); seen[y,x]=1; ys=[];xs=[]
                while q:
                    cy,cx=q.popleft(); ys.append(cy); xs.append(cx)
                    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                        ny,nx=cy+dy,cx+dx
                        if 0<=ny<H and 0<=nx<W and sm[ny,nx] and not seen[ny,nx]: seen[ny,nx]=1; q.append((ny,nx))
                if len(ys)>=minpx:
                    bx=(min(xs)*4,min(ys)*4,(max(xs)+1)*4,(max(ys)+1)*4)
                    sp=rgba.crop(bx); bb=sp.getbbox()
                    if bb: out.append((bx[0]+bb[0],bx[1]+bb[1],sp.crop(bb)))
    return sorted(out,key=lambda t:(t[1]//120,t[0]))
name=sys.argv[1]
im=Image.open(f'out/{name}.png')
if name=='SPECIALS':
    W,H=im.size; im=im.crop((0,0,W,int(H*0.3)))
rg=key_magenta(im); comps=components(rg)
os.makedirs(f'spr/{name}',exist_ok=True)
for i,(x,y,sp) in enumerate(comps): sp.save(f'spr/{name}/{i:02d}.png')
# labelled contact sheet for review / labelling
cell=170; cols=6; rows=(len(comps)+cols-1)//cols
cs=Image.new('RGB',(cols*cell,rows*cell),'#d8d8d8'); d=ImageDraw.Draw(cs)
for i,(x,y,sp) in enumerate(comps):
    t=sp.copy(); t.thumbnail((cell-30,cell-30))
    ox=(i%cols)*cell+(cell-t.width)//2; oy=(i//cols)*cell+22+(cell-30-t.height)//2
    cs.paste(t,(ox,oy),t); d.text(((i%cols)*cell+6,(i//cols)*cell+4),str(i),fill='black',font=ImageFont.load_default(20))
cs.save(f'spr/{name}_contact.png'); print(name,len(comps))
