# Génère le monde voxel (pont de Cosne) + géométries fines -> world.npz (quads)
import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))   # chemins relatifs au dossier du script
import numpy as np, json, cv2, math, sys
TILES=json.load(open("tiles.json"))
rng=np.random.default_rng(2026)
# ---------------- grille
S0,S1=-100,430; T0,T1=-280,120; Z0,Z1=-4,56
NS,NT,NZ=S1-S0,T1-T0,Z1-Z0
vox=np.zeros((NS,NT,NZ),np.uint8)
AIR,GRASS,DIRT,COARSE,SAND,GRAVEL,STONE,BRICKS,BRICKS_M,CAP,PINK,PINK_L,STEEL,STEEL_D,ASPHALT,LOG,LV_G,LV_Y,LV_O,LV_B,LV_L,WATER,GRASS_DRY,PATH,RIVERBED,MOSSY,SAND_WET=range(27)
LEAVES={LV_G,LV_Y,LV_O,LV_B,LV_L}
# Nouveaux blocs (identifiants réservés, à déclarer aussi dans mesher.py) : herbe 30-34, grève 35-39, rive 40-44, tablier 45-49
# ext:herbe
GRASS_PATCHY=30
# ext:greve
PEBBLES=35
TUFT=36
TALUS=37
# ext:rive
# ext:tablier
def zi(z): return int(z)-Z0
def si(s): return int(s)-S0
def ti(t): return int(t)-T0
ss=np.arange(S0,S1)+0.5; tt=np.arange(T0,T1)+0.5
SS,TT=np.meshgrid(ss,tt,indexing="ij")
def vnoise(scale,seed,amp=1.0):
    r=np.random.default_rng(seed)
    g=r.random((NS//scale+3,NT//scale+3)).astype(np.float32)
    big=cv2.resize(g,( (NT//scale+3)*scale, (NS//scale+3)*scale),interpolation=cv2.INTER_CUBIC)
    return (big[:NS,:NT]-0.5)*2*amp
n1=vnoise(12,1); n2=vnoise(5,2); n3=vnoise(24,3); n4=vnoise(3,4)
def sm(a,b,x):
    t_=np.clip((x-a)/(b-a),0,1); return t_*t_*(3-2*t_)

# ---------------- hauteur du terrain H (z du dessus du sol) et type de surface
H=np.full((NS,NT),-3.0)        # lit profond par défaut
top=np.full((NS,NT),RIVERBED,np.uint8)
# lit du fleuve : moins profond près des rives / bancs
H=np.where(n3>0.25,-2.0,H); H=np.where(n1>0.45,-1.0,H)

# rive proche (côté caméra) : plateau z=6 puis terrasses jusqu'à la plage z=1
bank_edge=-44.0+1.2*n2+0.8*n4
u=SS-bank_edge
steps=np.clip(np.floor((u+1.0)/4.2),0,3)
Hbank=4-steps
# ligne d'eau (bord du fleuve : pile les pieds dans l'eau, grève en biais à droite ; lagune à gauche)
t_=TT
wl=np.where(t_>9,-4.0-0.12*(t_-9)-0.6*np.clip(t_-30,0,None),np.where(t_>-9,-3.5,np.maximum(-24.0,-3.5+1.25*(t_+9))))+0.7*n1   # langue effilée vers t=36
s_in=np.minimum(-9.5,-15.3+0.6*(t_-9.3))+0.6*n1                 # bord intérieur de la langue de grève
s_nr=np.where(t_>=10,-25.8,-25.8+2.3*(10-t_))+0.6*n1              # bord du talus côté lagune
lagoon=(t_>5)&(SS>s_nr)&(SS<s_in)                                 # eau peu profonde (reflets de la pile)
Hb=np.where(Hbank<=3,4-np.clip(np.floor((SS+44.0-1.2*n3+1.0)/4.2),1,3),Hbank)   # marches du talus lissées (bord du plateau inchangé)
land_near=(SS<wl)&~lagoon
H=np.where(land_near,Hb,H)
top=np.where(land_near,GRASS,top)
# plage basse en bandes : talus vert (z=1), galets calcaire au ras de l'eau, buttes d'herbe (1 bloc) le long du fleuve
beach=land_near&(Hb<=1)
nb5=vnoise(3,35); nb6=vnoise(9,36)
SHRUBS=[(-6,0,2.5,2.3),(-13,-10,2.1,2.0)]                          # arbustes de la photo : (s,t,rayon,demi-hauteur)
near_sh=np.zeros_like(beach)
for (s_,t_s,r_,h_) in SHRUBS: near_sh|=((SS-s_-0.5)**2+(TT-t_s-0.5)**2)<(r_+1.6)**2
butte=beach&(((wl-SS)<np.where(t_>9,4.6,5.5)+2.2*nb5+0.8*nb6)|near_sh)&(n4>-0.5)   # touffes groupées, bord festonné
s_fg=np.clip(-25.3+0.75*t_,-30.5,-21.0)+0.8*n1                    # limite talus vert / galets
bt=np.where(butte,TUFT,np.where(SS<s_fg,GRASS,PEBBLES))
top=np.where(beach,bt,top)
# marches de la pelouse : bords rectilignes dans la zone filmée (t de -12 à 30). Avec le bruit de bank_edge,
# chaque décroché d'un bloc tourné vers la caméra (+t) laissait voir, en vue rasante, un triangle de grass_side
# éclairé par le soleil, planté dans la pelouse (la marche elle-même, herbe sur herbe, reste invisible).
jA,jB=ti(-12),ti(30); lw=land_near[:,jA:jB]&(H[:,jA:jB]>=2)
H[:,jA:jB]=np.where(lw,np.where(lw,H[:,jA:jB],-9).max(1,keepdims=True),H[:,jA:jB])
# plateau : pelouse d'automne. Zones sèches / vertes (bruit lent) mêlées bloc à bloc, herbe clairsemée,
# plaques de terre ; chemin de terre sableux en travers du bas de l'image
plateau=land_near&(H>=4)
rh=np.random.default_rng(3030)                                   # aléa propre (ne décale pas rng des arbres)
ndry=vnoise(10,31)+0.5*vnoise(4,32); nbare=vnoise(5,33)+0.4*vnoise(2,34)
Pc=np.load("../geo/fitP_rollfree.npy"); fh=np.array([math.cos(Pc[3]),math.sin(Pc[3])])   # caméra de la photo
df=(SS-Pc[0])*fh[0]+(TT-Pc[1])*fh[1]; dr=(SS-Pc[0])*fh[1]-(TT-Pc[1])*fh[0]         # devant / à droite (m)
dry=(0.8*ndry+0.4*np.clip((9-df)/5,-1,1)+0.25*(rh.random(H.shape)-0.5)>0.2)^(rh.random(H.shape)<0.15)  # plus sec près du chemin
lawn_t=np.where(dry,GRASS_DRY,GRASS)
lawn_t=np.where((nbare>0.5)|(rh.random(H.shape)<0.03),GRASS_PATCHY,lawn_t)
lawn_t=np.where((nbare>0.72)|(rh.random(H.shape)<0.01),COARSE,lawn_t)
pe=4.8+0.12*dr+0.45*vnoise(3,35)                                  # bord haut du chemin
path=(df<pe)&(df>-10)&(np.abs(dr)<30)
lawn_t=np.where(path,np.where(rh.random(H.shape)<0.04,COARSE,PATH),lawn_t)
rim=(~path)&(df<pe+0.5)&(rh.random(H.shape)<0.3)                # lisière : herbe clairsemée, terre
lawn_t=np.where(rim,np.where(rh.random(H.shape)<0.15,COARSE,GRASS_PATCHY),lawn_t)
top=np.where(plateau,lawn_t,top)
# eau peu profonde le long de la plage
shore=(~land_near)&(SS<wl+6)
H=np.where(shore&(H<-1),-1.0,H)
H=np.where(beach&(bt!=GRASS),np.where(butte,1.0,0.0),H)           # galets au ras de l'eau, buttes un bloc au-dessus
# bord des marches du talus : côté en brins d'herbe plutôt qu'en terre (triangles roses au soleil rasant)
lower=np.zeros_like(beach)
for d in [(1,0),(-1,0),(0,1),(0,-1)]: lower|=np.roll(H,d,(0,1))<H
top=np.where(land_near&(Hbank<=3)&(top==GRASS)&lower,TALUS,top)

# île boisée (droite) : rive proche vers s=20, pointe vers (30,-28)
isl=((SS-85)/68)**2+((TT+120)/92)**2 + 0.10*n1
isl_tip=((SS-40)/22)**2+((TT+44)/18)**2
island=(isl<1.0)|(isl_tip<1.0)
island&=SS>18+2*n2
# V3.1 : île basse et plate comme sur la photo. Large plage de sable au ras de l'eau (H=0, comme les bancs de
# sable ; pourtour et pointe, avancée de quelques mètres vers la caméra) ; intérieur boisé un bloc plus haut,
# bordé de sable (la marche est en sable mouillé, pas en terre) ; seul l'intérieur porte des arbres, bas.
island|=(((SS-32)/20)**2+((TT+50)/26)**2<1)&(SS>13+2*n2)
isl_in=island&(isl<0.86+0.03*n2)
isl_rim=np.zeros_like(isl_in)
for d in [(1,0),(-1,0),(0,1),(0,-1)]: isl_rim|=~np.roll(isl_in,d,(0,1))
H=np.where(island,np.where(isl_in,1.0,0.0),H)
top=np.where(island,np.where(isl_in&~isl_rim,GRASS,SAND),top)
# bancs de sable dans le fleuve (gauche et centre)
bank1=(((SS-95)/45)**2+((TT-24)/12)**2+0.3*n2)<1
bank2=(((SS-175)/30)**2+((TT+14)/9)**2+0.3*n2)<1
for bk in (bank1,bank2):
    H=np.where(bk&(H<0),0.0,H); top=np.where(bk,SAND,top)
# rive lointaine (s>295) avec colline boisée à gauche (V3.1 : basse, 8 m au plus : vallée plate de la photo)
far=SS>296+3*n2
hill=np.clip(1-(((SS-372)/70)**2+((TT+18)/85)**2),0,1)
Hf=3+2*n3+8*hill**1.3
H=np.where(far,np.floor(Hf),H)
top=np.where(far,np.where(SS<300+3*n2,SAND,GRASS),top)
# rive droite lointaine (t<-230) : berge basse boisée
farR=TT<-236+4*n2
H=np.where(farR&(H<2),2.0,H); top=np.where(farR,GRASS,top)
H=np.clip(np.round(H),-3,50).astype(int)

# ---------------- remplissage colonnes
zz=np.arange(Z0,Z1)
for k,z in enumerate(zz):
    solid=z<H                                   # bloc occupe [z,z+1) si z+1<=H
    depth=H-1-z
    col=np.where(depth==0,top,np.where(depth<=2,DIRT,STONE))
    # sous le sable -> sable ; sous gravier -> gravier ; lit -> lit
    col=np.where((depth>0)&(depth<=3)&np.isin(top,[SAND,RIVERBED,GRAVEL,SAND_WET]),top,col)
    col=np.where((depth>0)&(depth<=2)&(top==GRASS_DRY),DIRT,col)
    col=np.where((depth>0)&np.isin(top,[COARSE,PATH]),DIRT,col)
    vox[:,:,k]=np.where(solid,col,AIR)
    water=(~solid)&(z<0)
    vox[:,:,k]=np.where(water,WATER,vox[:,:,k])
# sable mouillé au contact de l'eau (bord de plage)
k1=zi(0)
edge=(H==1)&np.isin(top,[SAND,GRAVEL])
nb=np.zeros_like(edge)
for d in [(1,0),(-1,0),(0,1),(0,-1)]:
    nb|=np.roll(H<=0,d,(0,1))
vox[:,:,k1]=np.where(edge&nb&(top==SAND),SAND_WET,vox[:,:,k1])
# sous les galets et les buttes : galets (pas de terre au ras de l'eau)
for z in (-1,0):
    vox[:,:,zi(z)]=np.where(land_near&np.isin(top,[PEBBLES,TUFT])&(vox[:,:,zi(z)]==DIRT),PEBBLES,vox[:,:,zi(z)])

def setbox(s0,s1,t0,t1,z0,z1,b):
    vox[si(s0):si(s1),ti(t0):ti(t1),zi(z0):zi(z1)]=b

# ---------------- PONT
DECK_S0,DECK_S1=-75,345
def pylon(sc):
    # pile en pierre de taille, becs arrondis
    setbox(sc-2,sc+2,-9,9,-4,9,BRICKS)
    setbox(sc-2,sc+2,9,10,-4,9,BRICKS); setbox(sc-2,sc+2,-10,-9,-4,9,BRICKS)
    setbox(sc-1,sc+1,10,11,-4,9,BRICKS); setbox(sc-1,sc+1,-11,-10,-4,9,BRICKS)
    # pierres moussues à la ligne d'eau
    for z in (-1,0):
        m=vox[si(sc-2):si(sc+2),ti(-11):ti(11),zi(z)]
        r_=rng.random(m.shape)<0.55
        m[(m==BRICKS)&r_]=BRICKS_M
    # chaperon
    setbox(sc-2,sc+2,-9,9,8,9,CAP)
    # jambes 2x2
    for t0_ in (4,-6):
        setbox(sc-1,sc+1,t0_,t0_+2,9,30,PINK)
        for zb in (15,24):
            setbox(sc-1,sc+1,t0_,t0_+2,zb,zb+1,PINK_L)
    # traverse haute + goussets (arc en escalier)
    setbox(sc-1,sc+1,-4,4,27,30,PINK)
    setbox(sc-1,sc+1,-4,-3,26,27,PINK); setbox(sc-1,sc+1,3,4,26,27,PINK)
    setbox(sc-1,sc+1,-4,-3,25,26,PINK); setbox(sc-1,sc+1,3,4,25,26,PINK)
    setbox(sc-1,sc+1,-3,-2,26,27,PINK); setbox(sc-1,sc+1,2,3,26,27,PINK)
    # selles de câble
    setbox(sc-1,sc+1,4,5,30,31,STEEL_D); setbox(sc-1,sc+1,-5,-4,30,31,STEEL_D)
pylon(0); pylon(260)
# culées
setbox(-80,-66,-7,7,-4,10,BRICKS); setbox(-80,-66,-7,7,9,10,CAP)
setbox(330,346,-7,7,-4,10,BRICKS); setbox(330,346,-7,7,9,10,CAP)
# massifs d'ancrage des câbles
setbox(-72,-64,-7,-2,6,9,BRICKS); setbox(-72,-64,2,7,6,9,BRICKS)

# ---------------- arbres
# V3.1 : chênes à houppier arrondi (couches basses de rayon 2-3, couches hautes de rayon 1, coins retirés au hasard),
# peupliers rares, bas, à sommet arrondi ; pas de feuilles orange. Aléa propre (rt) : la pile garde rng.
rt=np.random.default_rng(4031)
def _set(s,t,z_,b):
    k=zi(z_)
    if 0<=k<NZ and vox[si(s),ti(t),k]==AIR: vox[si(s),ti(t),k]=b
def tree(s,t,z,kind,lv,h=None,low=0):
    """arbre au pied (s,t), sol au niveau z ; h = hauteur totale en blocs au-dessus du sol"""
    if not (S0+6<s<S1-6 and T0+6<t<T1-6): return
    if kind=="poplar":                                   # colonne de rayon 1, sommet en croix puis bloc seul
        h=int(h or rt.integers(9,13))
        for z_ in range(z,z+h-3): _set(s,t,z_,LOG)
        for dz in range(2,h):
            for ds in (-1,0,1):
                for dt in (-1,0,1):
                    c=abs(ds)+abs(dt)
                    if dz==h-1: ok=c==0 or (c==1 and rt.random()<0.25)
                    elif dz==h-2 or dz==2: ok=c<=1
                    else: ok=c<=1 or rt.random()<0.5
                    if ok: _set(s+ds,t+dt,z+dz,lv)
    elif kind=="oak":
        h=int(h or rt.integers(7,13))
        R=2 if h<10 else 3
        rad=[1.0,1.5]+([2.3,2.3] if R==2 else [2.3,3.2,3.2,2.3])  # rayon des couches, du haut vers le bas
        if low: rad=[1.0,1.5,2.3,2.3,2.3,1.5][:h-1]; rad[-1]=min(rad[-1],1.5)   # arbre bas de l'île : feuillage jusqu'à 1 bloc du sol
        nl=min(len(rad),h-2+low)
        for z_ in range(z,z+h-nl+1): _set(s,t,z_,LOG)         # tronc (s'arrête dans la couche basse)
        for k in range(nl):
            r=rad[k]; zz_=z+h-1-k; rn=int(r)
            for ds in range(-rn,rn+1):
                for dt in range(-rn,rn+1):
                    d2=ds*ds+dt*dt
                    if k==0: ok=d2<=1 and (d2==0 or rt.random()<0.85)
                    elif d2<=(r-0.5)**2+0.1: ok=True                  # cœur plein
                    else: ok=d2<=r*r and rt.random()<0.6              # bord : coins retirés au hasard
                    if ok: _set(s+ds,t+dt,zz_,lv)
def leaf_kind(p_y=0.15,p_o=0.0):
    r_=rt.random()
    return LV_Y if r_<p_y else (LV_O if r_<p_y+p_o else (LV_L if r_<p_y+p_o+0.2 else LV_G))
NTREE={}
def scatter(mask,spacing,fn,name=""):
    idx=np.argwhere(mask)
    rt.shuffle(idx)
    occ=np.zeros((NS//spacing+2,NT//spacing+2),bool)
    for i,j in idx:
        a,b=i//spacing,j//spacing
        if occ[a,b]: continue
        occ[a,b]=True; fn(ss[i]-0.5,tt[j]-0.5,H[i,j]); NTREE[name]=NTREE.get(name,0)+1
    print("arbres",name,{k:v for k,v in NTREE.items() if k.startswith(name)})
def kind_far(p_pop,name,hmax=13):
    def fn(s,t,z):
        k="poplar" if rt.random()<p_pop else "oak"; NTREE[name+"_"+k]=NTREE.get(name+"_"+k,0)+1
        tree(int(s),int(t),z,k,leaf_kind(),h=int(rt.integers(7,hmax)) if k=="oak" else int(rt.integers(9,min(hmax,13))))
    return fn
road=(np.abs(TT)<9)&(SS<352)                                   # abords de la culée : pas d'arbre sous le tablier
# île : chênes bas (5 à 7 blocs) seulement à l'intérieur, en retrait de la plage ; aucun peuplier
scatter(isl_in,5,lambda s,t,z: tree(int(s),int(t),z,"oak",leaf_kind(),h=int(rt.integers(5,8)),low=1),"ile")
# rives lointaines : bois continu de chênes (7 à 12 blocs), peupliers rares (≤ 15 %, ≤ 12 blocs)
scatter(far&(top==GRASS)&~road,5,kind_far(0.12,"far"),"far")
scatter(farR&(top==GRASS),6,kind_far(0.12,"farR",11),"farR")        # rive droite : plus basse (ciel sous le tablier à f1)
# arbustes de la grève (deux, placés comme sur la photo) : boule de feuillage irrégulière posée sur les buttes
for (s_,t_s,r_,h_) in SHRUBS:
    r2=np.random.default_rng(int(s_*31+t_s)&0xffff); z0=int(H[si(s_),ti(t_s)])-1
    for ds in range(-3,4):
        for dt in range(-3,4):
            rr=r_*(0.8+0.35*r2.random())                              # contour irrégulier
            for dz in range(0,int(2*h_)+3):
                d=(ds/rr)**2+(dt/rr)**2+((dz-h_+0.3)/h_)**2
                if (d<=1.1 or (d<=1.6 and r2.random()<0.15)) and r2.random()>0.2 and vox[si(s_+ds),ti(t_s+dt),zi(z0+dz)]==AIR:
                    vox[si(s_+ds),ti(t_s+dt),zi(z0+dz)]=LV_B
np.save("vox.npy",vox); np.save("H.npy",H)
print("voxels:",{n:int((vox==v).sum()) for n,v in [("water",WATER),("leaves",-1)] if v>=0}, "solid",int(((vox!=AIR)&(vox!=WATER)).sum()))
