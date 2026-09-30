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
# Nouveaux blocs, un bloc de lignes par zone (identifiants réservés : herbe 30-34, grève 35-39, rive 40-44, tablier 45-49)
# ext:herbe
GRASS_PATCHY=30
FT[GRASS_DRY]=("grass_top_dry*","grass_side","dirt")          # herbe sèche : 2 tuiles (grass_top_dry0/2 = alias)
FT[GRASS_PATCHY]=("grass_top_patchy","grass_side","dirt")
# ext:greve
PEBBLES=35
TUFT=36
TALUS=37
FT[PEBBLES]=("pebbles*",)*3
FT[TUFT]=("tuft_top","tuft_side","pebbles0")
FT[TALUS]=("grass_top*","tuft_side","dirt")
PEB_GRASS=55                                                   # v3.1 : galets mêlés d'herbe
FT[PEB_GRASS]=("pebbles_grass","pebbles0","pebbles0")
FT[BRICKS]=("bricks*",)*3                                      # v3.1 : pile, 3 variantes de moellons (bricks0 = bricks)
# ext:rive
ri=np.random.default_rng(3033)   # V3.1 : aléa des plantes de l'île (s>=10), la grève garde rng
# ext:tablier
NB=64
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
QO,QC,QW,QK,QP=Q(),Q(),Q(),Q(),Q()     # opaque, cutout, water, cloud, plants (croix, maillage à part pour l'animation)
QWL=Q(); LAGOON=np.load("lagoon.npy")    # eau de la lagune (world.py) : matériau à part (lueur, scene.py)

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
            lg=LAGOON[idx[:,0],idx[:,1]]
            QWL.add(V[lg],np.zeros((int(lg.sum()),4,2),np.float32))
            QQ.add(V[~lg],np.zeros((int((~lg).sum()),4,2),np.float32)); continue
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
QS,QT=Q(),Q()     # acier du tablier, matériau mat dédié (scene.py) : pleins / treillis découpé
def quad_uv(QQ,o,eu,ev,tile,v0=0.0,v1=1.0,flip=False):
    """un quad o+eu*a+ev*b (a,b in [0,1]) -> tuile entière, ou bande [v0,v1] de la tuile ; flip = miroir en u"""
    o=np.array(o,np.float32); eu=np.array(eu,np.float32); ev=np.array(ev,np.float32)
    V=[o,o+eu,o+eu+ev,o+ev]
    uu=np.array([1,0,0,1.]) if flip else np.array([0,1,1,0.])
    vv=np.clip(np.array([v0,v0,v1,v1]),v0+EPS,v1-EPS)
    u,v=tile_uv(tile,uu,vv); QQ.add(np.array([V]),np.stack([u,v],-1)[None])
# tablier : poutres latérales hautes (membrure basse 9,5-10, panneaux en X 10-11,5, membrure haute 11,5-12)
ZB,ZP,ZT=9.5,10.0,11.5
for s0 in np.arange(DECK_S0,DECK_S1,20.0):
    s1=min(s0+20,DECK_S1)
    box(QS,s0,s1,-3.5,3.5,9.5,10,asp,sd,sd)                 # chaussée (dessous acier sombre)
    for ta in (3.5,-4.0):                                    # membrures des deux poutres (t in [3.5,4] et [-4,-3.5])
        box(QS,s0,s1,ta,ta+0.5,ZB,ZP,st,st,sd)
        box(QS,s0,s1,ta,ta+0.5,ZT,ZT+0.5,st,st,sd)
tA,tB,tC=Tn("truss_a"),Tn("truss_b"),Tn("truss_c")
for s in np.arange(DECK_S0,DECK_S1,2.0):
    for tp in (3.75,-3.75):                                  # panneau 2 m x 1,5 m : croisillon + gousset en losange
        # vu depuis +t (caméra) : +s part vers la gauche, d'où le miroir (arête éclairée du gousset côté soleil)
        quad_uv(QT,(s,tp,ZP+0.5),(1,0,0),(0,0,1),tB,flip=True); quad_uv(QT,(s+1,tp,ZP+0.5),(1,0,0),(0,0,1),tA,flip=True)
        quad_uv(QT,(s,tp,ZP),(1,0,0),(0,0,0.5),tC,0.0,0.5,True); quad_uv(QT,(s+1,tp,ZP),(1,0,0),(0,0,0.5),tC,0.5,1.0,True)
        face_grid(QS,(s,tp-0.3*np.sign(tp),ZP),(1,0,0),(0,0,1),2.0,0.75,sd)   # v3.1 : tôle sombre derrière la moitié basse (photo : ciel en haut seulement)
    box(QS,s-0.25,s+0.25,-3.5,3.5,9.25,9.5,sd,sd,sd)         # pièces de pont minces (leurs abouts prennent le soleil rasant)
# passerelle de visite en treillis devant chaque pile, pendue sous le tablier (photo : côté caméra de la pile)
for sc in (0.0,260.0):
    sp=sc-2.4
    for k,t in enumerate(np.arange(-8.0,4.0,1.5)):
        quad_uv(QT,(sp,t,7.5),(0,1.5,0),(0,0,1.5),lat,flip=bool(k%2))
    for t,zt in ((-8.0,9.0),(4.0,9.5)):                      # montants : vers le chaperon de la pile / sous la membrure
        box(QS,sp-0.1,sp+0.1,t-0.1,t+0.1,7.5,zt,st,st,st)
# câbles porteurs : escalier au texel (pas de 1/16 m, z arrondi au 1/16, paliers de même z fusionnés : marche <= 1/16 m)
def cable_z(s):
    if s<0:   return 30.35+0.45*s+0.0011*s*s
    if s<=260:
        zm=12.9; return zm+(30.35-zm)*((s-130)/130)**2
    d=s-260; return 30.35-0.45*d+0.0011*d*d
CT=0.25
for tcab in (4.0,-4.0):
    ds_=1/16; s=-62.0; run0=None; zr=None
    while True:
        z=round(cable_z(s+ds_/2)*16)/16 if s<322-1e-9 else None
        if z!=zr:
            if zr is not None and zr>9.6: box(QO,run0,s,tcab-CT/2,tcab+CT/2,zr-CT/2,zr+CT/2,cab,cab,cab)
            run0=s; zr=z
        if z is None: break
        s=round(s+ds_,6)
    # suspentes tous les 4 m, collier acier sombre à l'attache
    for s in np.arange(-56,320,4.0):
        if abs(s)<2 or abs(s-260)<2: continue
        ztop=cable_z(s)
        if ztop>12.4:
            box(QO,s-0.05,s+0.05,tcab-0.05,tcab+0.05,12.0,ztop,cab,cab,cab)
            box(QO,s-0.09,s+0.09,tcab-CT/2-0.04,tcab+CT/2+0.04,ztop-CT/2-0.12,ztop+CT/2+0.02,sd,sd,sd)
# ---------------- plantes (croix)
tg=Tn("tallgrass"); dg=Tn("drygrass"); fy=Tn("flower_yellow"); fw=Tn("flower_white")
def cross(x,y,z,tile,sz=1.0):
    h=sz/2*0.72
    for (dx,dy) in ((h,h),(h,-h)):
        V=[(x-dx,y-dy,z),(x+dx,y+dy,z),(x+dx,y+dy,z+sz),(x-dx,y-dy,z+sz)]
        u,v=tile_uv(tile,np.array([0,1,1,0.]),np.array([0,0,1,1.]))
        QP.add(np.array([V]),np.stack([u,v],-1)[None])
gs=Tn("grass_short"); gsd=Tn("grass_short_dry"); wd=Tn("weeds")
def cross2(x,y,z,tile,h=1.0,v0=None,fl=False):
    """croix de hauteur h (m), UV rognés pour garder 16 px/m ; v0 = bas de la bande lue dans la tuile
    (défaut 1-h : haut de la tuile, touffe « enfoncée » dans le sol)"""
    v0=1-h if v0 is None else v0; d=0.36
    u,v=tile_uv(tile,np.array([1,0,0,1.]) if fl else np.array([0,1,1,0.]),np.array([v0,v0,v0+h,v0+h]))
    for (dx,dy) in ((d,d),(d,-d)):
        V=[(x-dx,y-dy,z),(x+dx,y+dy,z),(x+dx,y+dy,z+h),(x-dx,y-dy,z+h)]
        QP.add(np.array([V]),np.stack([u,v],-1)[None])
Hs=H
# v3.1 : plantes de la grève et du talus (branche à part, aléa propre)
GRV=(PEBBLES,TUFT,TALUS,PEB_GRASS)
rg_=np.random.default_rng(3132)
gst=Tn("grass_strand"); tpl=Tn("tuft_plant"); gdn=Tn("grass_dense")
SHRUB_C=((-6,0,2.5),(-13,-10,2.1))                                   # arbustes de world.py (s, t, rayon)
def plant3(x,y,z,tile,h,fl=False):
    """croix de hauteur h (m) portant la tuile entière (herbes hautes, 0,5-1,5 m) ; largeur ~ hauteur"""
    d=0.36*max(0.8,min(h,1.3))
    u,v=tile_uv(tile,np.array([1,0,0,1.]) if fl else np.array([0,1,1,0.]),np.array([0,0,1,1.]))
    for (dx,dy) in ((d,d),(d,-d)):
        V=[(x-dx,y-dy,z),(x+dx,y+dy,z),(x+dx,y+dy,z+h),(x-dx,y-dy,z+h)]
        QP.add(np.array([V]),np.stack([u,v],-1)[None])
# pelouse et bande verte (terre ferme proche, H>=2) : aléa propre, plantes basses près de la caméra.
# dtr = distance au trajet de la caméra (photo -> fin des travellings testés : 10-16 m vers le fleuve, 0-5 m à droite)
rp=np.random.default_rng(3031)
_c0=np.array([-47.2,18.6]); _c1=np.array([-38.0,11.0])
def dtr(p):
    w=_c1-_c0; a=np.clip(np.dot(p-_c0,w)/np.dot(w,w),0,1); return float(np.linalg.norm(p-_c0-a*w))
LAWN=(GRASS,GRASS_DRY,GRASS_PATCHY,COARSE,PATH)
for i in range(NS):
    s=i+S0
    if s<-60 or s>40: continue
    for j in range(NT):
        t=j+T0
        if t<-60 or t>60: continue
        k=Hs[i,j]-Z0
        if k<0 or k>=NZ or (Hs[i,j]<1 and not (k>0 and vox[i,j,k-1] in GRV)): continue   # v3.1 : galets au ras de l'eau (H=0) admis
        base=vox[i,j,k-1]
        if vox[i,j,k]!=AIR: continue
        if base in GRV:                    # v3.1 : grève et talus (galets, buttes, TALUS) : aléa propre rg_, rp et rng inchangés
            x,y=s+0.5+rg_.uniform(-0.2,0.2),t+0.5+rg_.uniform(-0.2,0.2); z=Hs[i,j]; fl=rg_.random()<0.5; r_=rg_.random(); r2_=rg_.random()
            dsh=min(math.hypot(s+0.5-a,t+0.5-b)-c for a,b,c in SHRUB_C)          # distance au bord des arbustes
            nlow=[Hs[min(max(i+a,0),NS-1),min(max(j+b,0),NT-1)] for a,b in ((1,0),(-1,0),(0,1),(0,-1))]
            if base==TALUS:                # bande d'herbes vertes denses sur les marches (bord de la lagune : plus basse à f1)
                lag=any(LAGOON[min(max(i+a,0),NS-1),min(max(j+b,0),NT-1)] for a,b in ((1,0),(-1,0),(0,1),(0,-1)))
                if Hs[i,j]<=1: h_=0.55+0.2*r2_ if t<16 else (0.8+0.3*r2_ if t<22 else 1.0+0.5*r2_)
                elif Hs[i,j]==2: h_=0.7+0.3*r2_
                else: h_=0.6
                if Hs[i,j]>=3:             # marches hautes (près de la caméra) : touffes éparses, pas de haie
                    if r_<0.25: cross2(x,y,z,tpl,h_,fl=fl)
                elif r_<(0.85 if (lag or Hs[i,j]<=1) else 0.65): plant3(x,y,z,gdn if r2_<0.7 else tg,h_,fl=fl)
            elif base==TUFT:
                if dsh<1.5 and r_<0.45: plant3(x,y,z,gst,1.0+0.3*r2_,fl=fl)                       # herbes gris-vert au pied des arbustes
                elif min(nlow)<Hs[i,j] and r_<0.8:                                                      # bord de butte : touffe débordant sur le flanc
                    a,b=((1,0),(-1,0),(0,1),(0,-1))[int(np.argmin(nlow))]
                    cross2(x+0.3*a,y+0.3*b,z,tpl,(0.6,0.8,1.0)[int(r2_*3)],fl=fl)
                elif r_<0.15: cross2(x,y,z,tpl,0.6,fl=fl)
            elif base==PEB_GRASS:
                if r_<0.3: cross2(x,y,z,tpl,0.6 if r2_<0.6 else 0.8,fl=fl)
            elif dsh<2.0 and r_<0.3: plant3(x,y,z,gst,0.9+0.3*r2_,fl=fl)
            elif r_<0.04: cross2(x,y,z,tpl,0.6,fl=fl)
            continue
        if Hs[i,j]>=2 and s<-26 and base in LAWN:
            x,y=s+0.5+rp.uniform(-0.15,0.15),t+0.5+rp.uniform(-0.15,0.15); z=Hs[i,j]; fl=rp.random()<0.5
            d=dtr(np.array([x,y])); r_=rp.random()
            edge=Hs[i,j]>=4 and Hs[min(i+1,NS-1),j]<Hs[i,j]          # lisière du plateau (dernier bloc avant la marche)
            if Hs[i,j]<=3 or edge:                                     # bande de végétation verte, plus haute
                if base not in (GRASS,GRASS_DRY): p_=0.25
                else: p_=0.35 if edge else (0.72 if Hs[i,j]==3 else 0.85)
                if r_<0.035: cross2(x,y,z,fy,rp.choice([0.75,1.0]),fl=fl)
                elif r_<p_*0.4: cross2(x,y,z,wd,1.0,fl=fl)
                elif r_<p_*0.92: cross2(x,y,z,tg,rp.choice([0.75,1.0],p=[0.6,0.4]),fl=fl)
                elif r_<p_: cross2(x,y,z,dg,1.0,fl=fl)
                continue
            # plateau : touffes basses partout, moyennes loin du trajet, fleurs rares
            p_={GRASS:0.26,GRASS_DRY:0.24,GRASS_PATCHY:0.16,COARSE:0.07,PATH:0.03}[base]
            if r_<0.006 and d>6: cross2(x,y,z,fy if rp.random()<0.5 else fw,0.75,fl=fl)
            elif r_<p_*0.2 and d>7: cross2(x,y,z,tg if base==GRASS else dg,1.0,fl=fl)
            elif r_<p_: cross2(x,y,z,gs if (base==GRASS)^(rp.random()<0.25) else gsd,0.5,v0=0,fl=fl)
            continue
        # grève, île : règle d'origine
        if base not in (GRASS,GRASS_DRY,GRAVEL,COARSE): continue
        if s>=10:   # V3.1, île (s>=10) : plantes rares, aléa propre (ri), aucune à l'ombre du tablier ; grève (s<10) inchangée
            if abs(t)<8: continue
            r_=ri.random()
            if base in (GRASS,GRASS_DRY):
                if r_<0.01: cross(s+0.5,t+0.5,Hs[i,j],fy if ri.random()<0.5 else fw)
                elif r_<0.06: cross(s+0.5,t+0.5,Hs[i,j],tg if base==GRASS else dg)
            elif r_<0.03: cross(s+0.5,t+0.5,Hs[i,j],dg)
            continue
        near=(s<-39)
        dcam=((s+47.2)**2+(t-18.6)**2)**0.5
        r_=rng.random()
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
ox,oy=-500.0,-900.0
# V3.1 : nuages plus rares et moins déchiquetés au loin (moins de lamelles serrées derrière les suspentes).
# Tirages de cg inchangés : jusqu'à 300 m (horizontaux) du trajet de la caméra, le motif est celui de la V3 ;
# de 300 à 750 m, le seuil de couverture monte de 0,66 à 0,88 et le bruit par cellule (g2) s'efface.
cdist=np.hypot(ox+(np.arange(nx)[:,None]+0.5)*cs+43.0,oy+(np.arange(ny)[None,:]+0.5)*cs-15.0)
k_=np.clip((cdist-300.0)/450.0,0,1)
g2=g2+k_*(0.5-g2)
cm=(0.8*g+0.2*g2)>0.66+0.22*k_
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
for name,QQ in (("opaque",QO),("cutout",QC),("water",QW),("water_lagoon",QWL),("cloud",QK),("plants",QP)):
    V,U=QQ.arr(); out["V_"+name]=V; out["U_"+name]=U; print(name,len(V),"quads")
for name,QQ in (("steel",QS),("truss",QT)):   # tablier : acier mat (matériaux dédiés dans scene.py)
    V,U=QQ.arr(); out["V_"+name]=V; out["U_"+name]=U; print(name,len(V),"quads")
np.savez_compressed("world.npz",**out)
