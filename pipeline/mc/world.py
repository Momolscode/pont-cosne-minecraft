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
# ligne d'eau (côté gauche : l'eau arrive au pied du talus, devant la pile : plage)
t_=TT
wl=np.where(t_>12,-26.0+1.5*n2,np.where(t_>-10,-2.5,-9.5+1.5*n2))
blend=sm(4,12,t_)                      # transition douce plage -> talus
wl=np.where((t_>4)&(t_<=12),-2.5*(1-blend)+(-26.0)*blend,wl)
wl=np.where((t_<=-10)&(t_>-14),-2.5+( -9.5+2.5)*sm(-10,-14,t_),wl)
land_near=SS<wl
H=np.where(land_near,Hbank,H)
top=np.where(land_near,GRASS,top)
# plage basse (z=1) : gravier / herbe / sable selon bruit
beach=land_near&(Hbank<=1)
bt=np.where(n4>0.15,GRAVEL,np.where(n2>0.25,GRASS,np.where(n4<-0.45,SAND,np.where(n2<-0.3,COARSE,GRAVEL))))
top=np.where(beach,bt,top)
# plateau : herbe + taches de terre grossière / chemin (comme la photo)
plateau=land_near&(Hbank>=4)
top=np.where(plateau&(n4>0.55),COARSE,top)
top=np.where(plateau&(n2<-0.62)&(n4<0),COARSE,top)
# bande de sable au bas à droite (zone claire de la photo)
sandy=(SS>-46.5)&(SS<-44)&(TT<14.5)&(TT>11)
top=np.where(land_near&sandy,np.where(n4>0.0,PATH,COARSE),top)
# eau peu profonde le long de la plage
shore=(~land_near)&(SS<wl+6)
H=np.where(shore&(H<-1),-1.0,H)

# île boisée (droite) : rive proche vers s=20, pointe vers (30,-28)
isl=((SS-85)/68)**2+((TT+120)/92)**2 + 0.10*n1
isl_tip=((SS-40)/22)**2+((TT+44)/18)**2
island=(isl<1.0)|(isl_tip<1.0)
island&=SS>18+2*n2
Hi=np.where(isl<0.72,3.0,2.0); Hi=np.where((isl>0.9)&(isl_tip>0.8),1.0,Hi)
H=np.where(island,Hi,H)
top=np.where(island,np.where(Hi<=1,SAND,GRASS),top)
# bancs de sable dans le fleuve (gauche et centre)
bank1=(((SS-95)/45)**2+((TT-24)/12)**2+0.3*n2)<1
bank2=(((SS-175)/30)**2+((TT+14)/9)**2+0.3*n2)<1
for bk in (bank1,bank2):
    H=np.where(bk&(H<0),0.0,H); top=np.where(bk,SAND,top)
# rive lointaine (s>295) avec colline boisée à gauche
far=SS>296+3*n2
hill=np.clip(1-(((SS-372)/70)**2+((TT+18)/85)**2),0,1)
Hf=3+2*n3+30*hill**1.3
H=np.where(far,np.floor(Hf),H)
top=np.where(far,np.where(SS<300+3*n2,SAND,GRASS),top)
# rive droite lointaine (t<-230) : berge basse boisée
farR=TT<-236+4*n2
H=np.where(farR&(H<3),3.0,H); top=np.where(farR,GRASS,top)
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
def tree(s,t,z,kind,lv):
    if not (S0+6<s<S1-6 and T0+6<t<T1-6): return
    if kind=="poplar":
        h=rng.integers(12,17); r=2
        for z_ in range(z,z+h-2): vox[si(s),ti(t),zi(z_)]=LOG
        for dz in range(3,h+1):
            rr=r if dz<h-3 else 1
            if dz<5: rr=1
            for ds in range(-rr,rr+1):
                for dt in range(-rr,rr+1):
                    if ds*ds+dt*dt<=rr*rr+0.5 and rng.random()>0.12:
                        zz_=z+dz
                        if vox[si(s+ds),ti(t+dt),zi(zz_)]==AIR: vox[si(s+ds),ti(t+dt),zi(zz_)]=lv
    elif kind=="oak":
        h=rng.integers(6,10); r=rng.integers(3,5)
        for z_ in range(z,z+h): vox[si(s),ti(t),zi(z_)]=LOG
        cz_=z+h-1
        for dz in range(-2,3):
            rr=r if abs(dz)<=1 else r-1
            for ds in range(-rr,rr+1):
                for dt in range(-rr,rr+1):
                    d2=ds*ds+dt*dt+ (dz*dz*1.5)
                    if d2<=rr*rr+0.8 and rng.random()>0.08:
                        if vox[si(s+ds),ti(t+dt),zi(cz_+dz)]==AIR: vox[si(s+ds),ti(t+dt),zi(cz_+dz)]=lv
    elif kind=="bush":
        h=rng.integers(1,3)
        for dz in range(h):
            for ds in range(-1,2):
                for dt in range(-1,2):
                    if (abs(ds)+abs(dt)<=1 or rng.random()<0.4) and vox[si(s+ds),ti(t+dt),zi(z+dz)]==AIR:
                        vox[si(s+ds),ti(t+dt),zi(z+dz)]=lv
def leaf_kind(p_y=0.22,p_o=0.08):
    r_=rng.random()
    return LV_Y if r_<p_y else (LV_O if r_<p_y+p_o else (LV_L if r_<p_y+p_o+0.2 else LV_G))
def scatter(mask,spacing,fn):
    idx=np.argwhere(mask)
    rng.shuffle(idx)
    taken=np.zeros_like(mask,dtype=bool)
    occ=np.zeros((NS//spacing+2,NT//spacing+2),bool)
    for i,j in idx:
        a,b=i//spacing,j//spacing
        if occ[a,b]: continue
        occ[a,b]=True; fn(ss[i]-0.5,tt[j]-0.5,H[i,j])
# île : peupliers + chênes
scatter(island&(H>=2)&(isl<0.95),5,lambda s,t,z: tree(int(s),int(t),z,"poplar" if rng.random()<0.55 else "oak",leaf_kind()))
# rive lointaine : forêt dense
scatter(far&(H>=3),5,lambda s,t,z: tree(int(s),int(t),z,"oak" if rng.random()<0.6 else "poplar",leaf_kind(0.25,0.1)))
scatter(farR&(H>=3),6,lambda s,t,z: tree(int(s),int(t),z,"oak" if rng.random()<0.5 else "poplar",leaf_kind()))
# buissons sur la plage basse et en pied de talus
bmask=land_near&(H==1)&(SS>-30)&(SS>wl-3.5)&(n2>-0.1)
scatter(bmask,7,lambda s,t,z: tree(int(s),int(t),z,"bush",LV_B))
bmask2=land_near&(H==2)&(n2>0.2)&(TT<12)
scatter(bmask2,11,lambda s,t,z: tree(int(s),int(t),z,"bush",LV_B))
# rochers sur la plage
rk=land_near&(H==1)&(rng.random(H.shape)<0.035)
for i,j in np.argwhere(rk):
    k=H[i,j]-Z0
    if vox[i,j,k]==AIR: vox[i,j,k]=MOSSY if rng.random()<0.5 else STONE
np.save("vox.npy",vox); np.save("H.npy",H)
print("voxels:",{n:int((vox==v).sum()) for n,v in [("water",WATER),("leaves",-1)] if v>=0}, "solid",int(((vox!=AIR)&(vox!=WATER)).sum()))
