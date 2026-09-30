# Voxels + géométries fines -> quads par matériau (world.npz)
import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))   # chemins relatifs au dossier du script
import numpy as np, json, math
TILES=json.load(open("tiles.json"))
exec(open("world.py").read().split("# ---------------- grille")[0])   # imports
S0,S1=-100,430; T0,T1=-280,120; Z0,Z1=-4,56
vox=np.load("vox.npy"); H=np.load("H.npy")
NS,NT,NZ=vox.shape
AIR,GRASS,DIRT,COARSE,SAND,GRAVEL,STONE,BRICKS,BRICKS_M,CAP,PINK,PINK_L,STEEL,STEEL_D,ASPHALT,LOG,LV_G,LV_Y,LV_O,LV_B,LV_L,WATER,GRASS_DRY,PATH,RIVERBED,MOSSY,SAND_WET=range(27)
LEAVES=[LV_G,LV_Y,LV_O,LV_B,LV_L]
rng=np.random.default_rng(7)
EPS=0.02/16
def tile_uv(tile,uu,vv):
    """uu,vv in [0,1] -> atlas uv"""
    r,c=divmod(tile,16)
    u=(c+np.clip(uu,EPS,1-EPS))/16.0
    v=1.0-(r+1-np.clip(vv,EPS,1-EPS))/16.0
    return u,v
Tn=lambda n: TILES[n]
FT={ # top, side, bottom
 GRASS:("grass_top*","grass_side","dirt"), DIRT:("dirt",)*3, COARSE:("coarse_dirt","dirt","dirt"),
 SAND:("sand",)*3, GRAVEL:("gravel",)*3, STONE:("stone",)*3, BRICKS:("bricks",)*3, BRICKS_M:("bricks_mossy",)*3,
 CAP:("cap",)*3, PINK:("pink",)*3, PINK_L:("pink_light",)*3, STEEL:("steel",)*3, STEEL_D:("steel_dark",)*3,
 ASPHALT:("asphalt",)*3, LOG:("log_top","log","log_top"), LV_G:("leaves_green",)*3, LV_Y:("leaves_yellow",)*3,
 LV_O:("leaves_orange",)*3, LV_B:("leaves_bush",)*3, LV_L:("leaves_light",)*3, GRASS_DRY:("grass_top_dry","grass_side","dirt"),
 PATH:("path","dirt","dirt"), RIVERBED:("riverbed",)*3, MOSSY:("mossy_stone",)*3, SAND_WET:("sand_wet",)*3,
}
NB=32
tile_lut=np.zeros((NB,3,3),np.int32)   # [block, face(0 top,1 side,2 bottom), variant]
for b,(a,s_,c) in FT.items():
    for f,name in enumerate((a,s_,c)):
        if name.endswith("*"):
            for v in range(3): tile_lut[b,f,v]=Tn(name[:-1]+str(v))
        else: tile_lut[b,f,:]=Tn(name)
opaque=np.zeros(NB,bool); opaque[[b for b in FT if b not in LEAVES]]=True
isleaf=np.zeros(NB,bool); isleaf[LEAVES]=True

class Q:
    def __init__(s): s.V=[]; s.U=[]
    def add(s,V,U): s.V.append(np.asarray(V,np.float32).reshape(-1,4,3)); s.U.append(np.asarray(U,np.float32).reshape(-1,4,2))
    def arr(s):
        if not s.V: return np.zeros((0,4,3),np.float32),np.zeros((0,4,2),np.float32)
        return np.concatenate(s.V),np.concatenate(s.U)
QO,QC,QW,QK=Q(),Q(),Q(),Q()     # opaque, cutout, water, cloud

# ---------------- faces voxel (vectorisé)
DIRS=[((1,0,0),1),((-1,0,0),1),((0,1,0),1),((0,-1,0),1),((0,0,1),0),((0,0,-1),2)]
CORN={ (1,0,0):[(1,0,0),(1,1,0),(1,1,1),(1,0,1)], (-1,0,0):[(0,1,0),(0,0,0),(0,0,1),(0,1,1)],
       (0,1,0):[(1,1,0),(0,1,0),(0,1,1),(1,1,1)], (0,-1,0):[(0,0,0),(1,0,0),(1,0,1),(0,0,1)],
       (0,0,1):[(0,0,1),(1,0,1),(1,1,1),(0,1,1)], (0,0,-1):[(0,1,0),(1,1,0),(1,0,0),(0,0,0)] }
BASEUV=np.array([(0,0),(1,0),(1,1),(0,1)],np.float32)
pad=np.zeros((NS+2,NT+2,NZ+2),np.uint8); pad[1:-1,1:-1,1:-1]=vox
for (d,fcat) in DIRS:
    nbr=pad[1+d[0]:1+d[0]+NS,1+d[1]:1+d[1]+NT,1+d[2]:1+d[2]+NZ]
    cur=vox
    # opaques : visibles si voisin non opaque
    m_op=opaque[cur]&~opaque[nbr]
    m_lf=isleaf[cur]&~opaque[nbr]&~isleaf[nbr]
    m_wt=(cur==WATER)&(nbr!=WATER)
    for m,QQ,kind in ((m_op,QO,"b"),(m_lf,QC,"b"),(m_wt,QW,"w")):
        idx=np.argwhere(m)
        if len(idx)==0: continue
        base=np.stack([idx[:,0]+S0,idx[:,1]+T0,idx[:,2]+Z0],1).astype(np.float32)
        corners=np.array(CORN[d],np.float32)
        V=base[:,None,:]+corners[None]
        if kind=="w":
            V[...,2]=np.where(V[...,2]==0,-0.12,V[...,2])     # surface d'eau un peu abaissée
            QQ.add(V,np.zeros((len(V),4,2),np.float32)); continue
        b=cur[m]
        h=(idx[:,0]*73856093 ^ idx[:,1]*19349663 ^ idx[:,2]*83492791)&0xffff
        var=h%3
        tl=tile_lut[b,fcat,var]
        uv=np.broadcast_to(BASEUV,(len(idx),4,2)).copy()
        if fcat==0:   # rotation aléatoire des dessus (casse la répétition)
            rot=(h>>3)%4
            for r_ in range(1,4):
                sel=rot==r_
                uv[sel]=np.roll(uv[sel],r_,axis=1)
        u,v=tile_uv(tl[:,None],uv[...,0],uv[...,1])
        QQ.add(V,np.stack([u,v],-1))

# ---------------- géométries fines
def face_grid(QQ,o,eu,ev,lu,lv,tile,flip=False):
    """face plane rectangulaire découpée en cellules <=1m ; UV 1 tuile = 1 m"""
    o=np.array(o,np.float32); eu=np.array(eu,np.float32); ev=np.array(ev,np.float32)
    nu=max(1,int(math.ceil(lu-1e-6))); nv=max(1,int(math.ceil(lv-1e-6)))
    Vs=[];Us=[]
    for i in range(nu):
        a0=i; a1=min(i+1,lu)
        for j in range(nv):
            b0=j; b1=min(j+1,lv)
            c=[(a0,b0),(a1,b0),(a1,b1),(a0,b1)]
            if flip: c=c[::-1]
            Vs.append([o+eu*a+ev*b for a,b in c])
            uu=np.array([a-a0 for a,b in c]); vv=np.array([b-b0 for a,b in c])
            u,v=tile_uv(tile,uu,vv); Us.append(np.stack([u,v],-1))
    QQ.add(np.array(Vs),np.array(Us))
def box(QQ,x0,x1,y0,y1,z0,z1,tt_,ts,tb):
    lx,ly,lz=x1-x0,y1-y0,z1-z0
    face_grid(QQ,(x0,y0,z1),(1,0,0),(0,1,0),lx,ly,tt_)                 # dessus
    face_grid(QQ,(x0,y0,z0),(0,1,0),(1,0,0),ly,lx,tb)                  # dessous
    face_grid(QQ,(x0,y0,z0),(1,0,0),(0,0,1),lx,lz,ts)                  # -y
    face_grid(QQ,(x1,y1,z0),(-1,0,0),(0,0,1),lx,lz,ts)                 # +y
    face_grid(QQ,(x0,y1,z0),(0,-1,0),(0,0,1),ly,lz,ts)                 # -x
    face_grid(QQ,(x1,y0,z0),(0,1,0),(0,0,1),ly,lz,ts)                  # +x
DECK_S0,DECK_S1=-75.0,345.0
L=DECK_S1-DECK_S0
st=Tn("steel"); sd=Tn("steel_dark"); asp=Tn("asphalt"); lat=Tn("lattice"); cab=Tn("cable")
# tablier : chaussée + membrures + treillis + pièces de pont
for s0 in np.arange(DECK_S0,DECK_S1,20.0):
    s1=min(s0+20,DECK_S1)
    box(QO,s0,s1,-3,3,9.5,10,asp,sd,sd)                     # chaussée
    for tc in (3,-4):                                        # membrures basse/haute (t in [3,4] et [-4,-3])
        box(QO,s0,s1,tc,tc+1,9.5,10.5,st,st,sd)
        box(QO,s0,s1,tc,tc+1,11.5,12.0,st,st,sd)
    for tp in (3.5,-3.5):                                    # treillis (plan alpha)
        face_grid(QC,(s0,tp,10.5),(1,0,0),(0,0,1),s1-s0,1.0,lat)
for s in np.arange(DECK_S0,DECK_S1,2.0):                     # pièces de pont
    box(QO,s,s+0.5,-4,4,9.0,9.5,sd,sd,sd)
    # poteaux verticaux du treillis tous les 4 m
    if int(s)%4==0:
        for tc in (3.25,-3.75):
            box(QO,s,s+0.5,tc,tc+0.5,10.5,11.5,st,st,st)
# câbles porteurs (segments de 0.5 m, hauteur quantifiée au 1/16)
def cable_z(s):
    if s<0:   return 30.35+0.45*s+0.0011*s*s
    if s<=260:
        zm=12.9; return zm+(30.35-zm)*((s-130)/130)**2
    d=s-260; return 30.35-0.45*d+0.0011*d*d
CT=0.36
for tcab in (4.0,-4.0):
    s=-62.0
    while s<322:
        z=round(cable_z(s+0.25)*16)/16
        if z>9.6: box(QO,s,s+0.5,tcab-CT/2,tcab+CT/2,z-CT/2,z+CT/2,cab,cab,cab)
        s+=0.5
    # suspentes tous les 4 m
    for s in np.arange(-56,320,4.0):
        if abs(s)<2 or abs(s-260)<2: continue
        ztop=cable_z(s)
        if ztop>12.4:
            box(QO,s-0.07,s+0.07,tcab-0.07,tcab+0.07,12.0,ztop,cab,cab,cab)
# ---------------- plantes (croix)
tg=Tn("tallgrass"); dg=Tn("drygrass"); fy=Tn("flower_yellow"); fw=Tn("flower_white")
def cross(x,y,z,tile,sz=1.0):
    h=sz/2*0.72
    for (dx,dy) in ((h,h),(h,-h)):
        V=[(x-dx,y-dy,z),(x+dx,y+dy,z),(x+dx,y+dy,z+sz),(x-dx,y-dy,z+sz)]
        u,v=tile_uv(tile,np.array([0,1,1,0.]),np.array([0,0,1,1.]))
        QC.add(np.array([V]),np.stack([u,v],-1)[None])
Hs=H
for i in range(NS):
    s=i+S0
    if s<-60 or s>40: continue
    for j in range(NT):
        t=j+T0
        if t<-60 or t>60: continue
        k=Hs[i,j]-Z0
        if k<0 or k>=NZ or Hs[i,j]<1: continue
        if vox[i,j,k]!=AIR or vox[i,j,k-1] not in (GRASS,GRASS_DRY,GRAVEL,COARSE): continue
        near=(s<-39)
        dcam=((s+47.2)**2+(t-18.6)**2)**0.5
        r_=rng.random()
        base=vox[i,j,k-1]
        if base in (GRASS,GRASS_DRY):
            p_grass=(0.07 if dcam<9 else 0.16) if near else 0.22
            if r_<0.03 and near: cross(s+0.5,t+0.5,Hs[i,j],fy if rng.random()<0.6 else fw)
            elif r_<0.05 and not near: cross(s+0.5,t+0.5,Hs[i,j],fy if rng.random()<0.5 else fw)
            elif r_<p_grass: cross(s+0.5,t+0.5,Hs[i,j],tg if base==GRASS else dg)
        elif base in (GRAVEL,COARSE) and r_<0.12:
            cross(s+0.5,t+0.5,Hs[i,j],dg)
# ---------------- nuages en blocs (cellules 12x12x4 m)
cs=10.0
cg=np.random.default_rng(99)
nx,ny=150,130
g=cg.random((nx//3+2,ny//3+2)).astype(np.float32)
import cv2
g=cv2.resize(g,((ny//3+2)*3,(nx//3+2)*3),interpolation=cv2.INTER_CUBIC)[:nx,:ny]
g2=cg.random((nx,ny)).astype(np.float32)
cm=(0.8*g+0.2*g2)>0.66
ox,oy=-500.0,-900.0
cz0,cz1=150.0,154.0
cpad=np.zeros((nx+2,ny+2),bool); cpad[1:-1,1:-1]=cm
for i,j in np.argwhere(cm):
    x0=ox+i*cs; y0=oy+j*cs
    Vs=[[(x0,y0,cz1),(x0+cs,y0,cz1),(x0+cs,y0+cs,cz1),(x0,y0+cs,cz1)],
        [(x0,y0+cs,cz0),(x0+cs,y0+cs,cz0),(x0+cs,y0,cz0),(x0,y0,cz0)]]
    if not cpad[i+2,j+1]: Vs.append([(x0+cs,y0,cz0),(x0+cs,y0+cs,cz0),(x0+cs,y0+cs,cz1),(x0+cs,y0,cz1)])
    if not cpad[i,j+1]:   Vs.append([(x0,y0+cs,cz0),(x0,y0,cz0),(x0,y0,cz1),(x0,y0+cs,cz1)])
    if not cpad[i+1,j+2]: Vs.append([(x0+cs,y0+cs,cz0),(x0,y0+cs,cz0),(x0,y0+cs,cz1),(x0+cs,y0+cs,cz1)])
    if not cpad[i+1,j]:   Vs.append([(x0,y0,cz0),(x0+cs,y0,cz0),(x0+cs,y0,cz1),(x0,y0,cz1)])
    QK.add(np.array(Vs),np.zeros((len(Vs),4,2)))
out={}
for name,QQ in (("opaque",QO),("cutout",QC),("water",QW),("cloud",QK)):
    V,U=QQ.arr(); out["V_"+name]=V; out["U_"+name]=U; print(name,len(V),"quads")
np.savez_compressed("world.npz",**out)
