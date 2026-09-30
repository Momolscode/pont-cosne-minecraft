# Textures pixel 16x16 originales -> atlas 256x256 (16x16 tuiles), RGBA
import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))   # chemins relatifs au dossier du script
import numpy as np
from PIL import Image
T=16
ATLAS_N=16
atlas=np.zeros((ATLAS_N*T,ATLAS_N*T,4),np.uint8)
TILES={}
def put(name,idx,img):
    img=np.asarray(img)
    if img.shape[2]==3: img=np.concatenate([img,np.full((T,T,1),255,np.uint8)],2)
    r,c=divmod(idx,ATLAS_N)
    atlas[r*T:(r+1)*T,c*T:(c+1)*T]=img
    TILES[name]=idx
def pal_img(rng,palette,weights,blob=1):
    """image aléatoire depuis une palette, avec petites taches (blob px)"""
    n=T//blob
    idx=rng.choice(len(palette),size=(n,n),p=np.array(weights)/np.sum(weights))
    idx=np.kron(idx,np.ones((blob,blob),int))
    # quelques pixels isolés pour casser les blocs
    m=rng.random((T,T))<0.35
    idx2=rng.choice(len(palette),size=(T,T),p=np.array(weights)/np.sum(weights))
    idx=np.where(m,idx2,idx)
    return np.array(palette,np.uint8)[idx]
def C(*a): return tuple(int(x) for x in a)

# ---------------- herbe (pelouse d'automne : vert olive, brins secs, terre)
def lawn(seed,pal,w,dots,nd,blob=2):
    """dessus d'herbe : palette en taches + brins isolés (1-2 px verticaux) d'autres teintes"""
    rng=np.random.default_rng(seed); img=pal_img(rng,pal,w,blob=blob).copy()
    for _ in range(nd):
        y,x=rng.integers(0,T,2); c=dots[rng.integers(0,len(dots))]
        img[y,x]=c
        if rng.random()<0.5: img[(y+1)%T,x]=c
    return img
G=[C(94,128,50),C(82,114,44),C(106,140,58),C(72,100,38),C(120,138,62),C(140,136,76)]      # vert olive
GS=[C(152,140,84),C(134,120,70),C(60,88,32)]                                                # brins secs / sombres
for i,seed in enumerate([1,2,3]):
    put(f"grass_top{i}",i,lawn(seed,G,[5,4,3,2,1.4,0.6],GS,10))
GD=[C(132,124,76),C(116,110,66),C(146,138,90),C(98,94,56),C(98,112,54),C(160,150,104)]    # herbe sèche (paille, olive)
GDd=[C(92,120,50),C(80,78,48),C(184,170,118)]
put("grass_top_dry",3,lawn(4,GD,[5,4,3,2.5,2.5,1],GDd,16))
D=[C(134,96,66),C(116,82,56),C(152,112,78),C(100,71,48),C(166,126,90)]
def dirt(seed): return pal_img(np.random.default_rng(seed),D,[5,4,3,2,1],blob=1)
put("dirt",4,dirt(5))
# côté herbe
side=dirt(6).copy(); rng=np.random.default_rng(7)
gtop=pal_img(rng,G,[5,4,3,2,1.4,0.6],blob=1)
depth=np.clip(3+rng.integers(-1,2,T)+ (rng.random(T)<0.25)*rng.integers(1,3,T),2,6)
for x in range(T): side[:depth[x],x]=gtop[:depth[x],x]
put("grass_side",5,side)
# terre grossière (plaques de terre nue de la pelouse) : brun gris, cailloux, quelques brins secs
DC=[C(132,110,84),C(118,98,74),C(146,124,96),C(106,88,68),C(156,136,108)]
cd=pal_img(np.random.default_rng(8),DC,[5,4,3,2,1],blob=1).copy(); rng=np.random.default_rng(9)
for _ in range(9):
    y,x=rng.integers(0,T-1,2); col=np.array([C(128,122,112),C(100,96,90),C(150,144,132)][rng.integers(0,3)],np.uint8)
    cd[y:y+2,x:x+rng.integers(1,3)]=col
for _ in range(6):
    y,x=rng.integers(0,T,2); cd[y,x]=[C(150,136,82),C(96,118,50)][rng.integers(0,2)]
put("coarse_dirt",6,cd)
# chemin de terre sableux (dessus)
P_=[C(170,150,114),C(158,138,104),C(182,164,128),C(146,128,96),C(194,178,146)]
pa=pal_img(np.random.default_rng(10),P_,[5,4,3,2,1.5],blob=1).copy(); rng=np.random.default_rng(35)
for _ in range(7):
    y,x=rng.integers(0,T,2); pa[y,x:x+rng.integers(1,3)]=[C(132,120,104),C(118,104,86),C(206,196,172)][rng.integers(0,3)]
put("path",7,pa)
# sable
S=[C(221,208,160),C(208,194,146),C(232,222,178),C(196,180,132),C(240,232,196)]
put("sand",8,pal_img(np.random.default_rng(11),S,[6,4,3,1,1],blob=1))
SW=[C(176,160,118),C(160,144,104),C(188,172,130),C(146,132,96)]            # sable mouillé / lit
put("sand_wet",9,pal_img(np.random.default_rng(12),SW,[5,4,3,2],blob=1))
# gravier
gv=np.zeros((T,T,3),np.uint8); rng=np.random.default_rng(13)
gv[:]=C(112,106,102)
GP=[C(136,130,126),C(96,92,90),C(160,152,146),C(122,108,96),C(80,78,78),C(148,140,128)]
for _ in range(40):
    y,x=rng.integers(0,T,2); h,w=rng.integers(1,3,2)
    gv[y:y+h,x:x+w]=GP[rng.integers(0,len(GP))]
put("gravel",10,gv)
# pierre
ST=[C(128,128,126),C(114,114,112),C(142,142,140),C(104,104,102)]
put("stone",11,pal_img(np.random.default_rng(14),ST,[5,4,3,2],blob=2))
# pierres de taille (pile) : moellons calcaires gris-beige contrastés, 3 assises irrégulières par bloc (5, 6, 5 px),
# joints sombres ; mêmes assises pour toutes les variantes (les joints horizontaux se raccordent d'un bloc à l'autre)
def bricks(seed,mossy=False,tone=1.0):
    rng=np.random.default_rng(seed)
    SB=[C(208,174,164),C(196,166,158),C(218,188,176),C(182,154,148),C(202,176,168),C(160,134,128),C(226,200,188),C(138,116,112)]
    WB=np.array([5,4,3,2,3,1.2,2,0.8]); WB=WB/WB.sum()
    img=np.zeros((T,T,3),int)
    joint=np.array(C(50,46,44))
    y=0
    for hc in (5,6,5):                                   # assises (px) ; joint = dernière ligne de l'assise
        x=int(rng.integers(0,T)); n=0
        while n<T:
            w=int(rng.integers(5,11)); w=min(w,T-n)
            if T-n-w<4: w=T-n                                   # pas de pierre de moins de 4 px en fin de rang
            c=(np.array(SB[rng.choice(len(SB),p=WB)])*tone).astype(int)+rng.integers(-16,17)
            for k in range(w):
                xx=(x+k)%T
                img[y:y+hc-1,xx]=c+rng.integers(-6,7,(hc-1,3))
                if k==0: img[y:y+hc-1,xx]=joint+8               # joint montant
            img[y,(x+1)%T:(x+1)%T+max(0,min(w-2,T-(x+1)%T))]+=10   # arête haute éclairée
            if rng.random()<0.35:                                 # pierre patinée : tache sombre
                yy,xx0=y+int(rng.integers(0,hc-1)),(x+int(rng.integers(1,max(2,w))))%T
                img[yy,xx0]-=28
            x=(x+w)%T; n+=w
        img[y+hc-1,:]=joint+rng.integers(-6,7,(T,1))
        y+=hc
    for x in rng.choice(T,int(rng.integers(1,4)),replace=False):   # coulures sombres (ruissellement, photo)
        y0=int(rng.integers(0,6)); img[y0:y0+int(rng.integers(5,12)),x]-=32
    if mossy:                                                       # pied de pile : pierre mouillée plus sombre, mousse, bande sombre en bas
        img=(img*np.linspace(0.92,0.62,T)[:,None,None]).astype(int)
        M=[C(84,108,58),C(70,94,48),C(98,122,64)]
        for _ in range(12):
            y_,x_=rng.integers(4,T,2); img[y_,x_:x_+rng.integers(1,3)]=M[rng.integers(0,3)]
        img[12:16,:][rng.random((4,T))<0.4]=M[0]
    return np.clip(img,0,255).astype(np.uint8)
put("bricks",12,bricks(15)); put("bricks_mossy",13,bricks(16,True))
put("bricks1",70,bricks(115,tone=0.82)); put("bricks2",71,bricks(215,tone=1.13)); TILES["bricks0"]=TILES["bricks"]   # variantes ("bricks*", mesher.py)
cap=np.full((T,T,3),C(204,196,176),np.uint8); rng=np.random.default_rng(17)
cap=np.clip(cap.astype(int)+rng.integers(-6,7,(T,T,1)),0,255).astype(np.uint8)
cap[0,:]=cap[-1,:]=cap[:,0]=cap[:,-1]=C(170,162,142)
put("cap",14,cap)
# béton rose (pylône)
def pink(seed,light=False):
    rng=np.random.default_rng(seed)
    # béton rose pâle (photo : saumon délavé, peu saturé) ; moucheture réduite
    if light: Pk=[C(220,195,185),C(214,189,179),C(226,201,191),C(210,184,175)]
    else:     Pk=[C(205,165,155),C(199,159,150),C(211,171,160),C(195,156,147),C(216,176,164)]
    img=pal_img(rng,Pk,[5,4,3,2,1][:len(Pk)],blob=2).astype(int)
    # coulures verticales légères
    for x in rng.choice(T,2,replace=False):
        y0=rng.integers(0,8); img[y0:y0+rng.integers(4,10),x]-=7
    return np.clip(img,0,255).astype(np.uint8)
put("pink",15,pink(18)); put("pink_light",16,pink(19,True))
# acier du tablier : gris bleuté volontairement sombre. Les faces verticales côté caméra reçoivent
# le soleil rasant (N.L 0,56 contre 0,08 pour le sol) : un albédo clair y sortait presque blanc.
def steel(seed,dark=False):
    rng=np.random.default_rng(seed)
    if dark: base=[C(38,44,56),C(34,40,51),C(43,50,63)]
    else:    base=[C(57,66,86),C(53,61,80),C(62,72,92),C(49,57,74)]
    img=pal_img(rng,base,[5,4,3,2][:len(base)],blob=2).astype(int)
    for y0 in (0,8):   # deux plats de 0,5 m par tuile (une membrure montre une moitié) : arêtes + rivets
        img[y0,:]+=9; img[y0+7,:]-=9
        if not dark:
            for x in range(1,T,4): img[y0+3,x]+=20; img[y0+4,x]-=8
    img[:,0]+=5; img[:,-1]-=8
    return np.clip(img,0,255).astype(np.uint8)
put("steel",17,steel(20)); put("steel_dark",18,steel(21,True))
AS=[C(64,66,70),C(56,58,62),C(74,76,80),C(50,52,56)]
put("asphalt",19,pal_img(np.random.default_rng(22),AS,[5,4,2,2],blob=1))
# treillis (alpha) de la passerelle de pile : membrures, montants, diagonale (panneau en N) ;
# plus clair que le tablier car sa face côté caméra est toujours à l'ombre
GM=np.array(C(104,118,138)+(255,),np.uint8); GH=np.array(C(124,138,158)+(255,),np.uint8); GK=np.array(C(78,90,108)+(255,),np.uint8)
lat=np.zeros((T,T,4),np.uint8)
lat[0:2,:]=GM; lat[0,:]=GH; lat[14:16,:]=GM; lat[15,:]=GK
lat[:,0]=GH; lat[:,15]=GM          # montant partagé avec le panneau voisin (1 px de chaque côté)
for x in range(1,T-1):
    y=int(round(13-(x-1)*11/13)); lat[y,x]=GH; lat[min(y+1,13),x]=GM
put("lattice",20,lat)
# feuilles (alpha)
def leaves(seed,pal,hole=0.14):
    rng=np.random.default_rng(seed)
    img=pal_img(rng,pal,[5,4,3,2][:len(pal)],blob=1)
    a=np.where(rng.random((T,T))<hole,0,255).astype(np.uint8)
    # grappes plus sombres
    dark=rng.random((T,T))<0.18
    img=np.where(dark[...,None],(img.astype(int)*0.78).astype(np.uint8),img)
    return np.concatenate([img,a[...,None]],2)
put("leaves_green",21,leaves(23,[C(98,124,30),C(84,106,24),C(112,138,40),C(70,92,20)]))            # V3.1 : vert olive d'automne
put("leaves_yellow",22,leaves(24,[C(196,176,64),C(176,156,52),C(214,194,86),C(160,146,50)]))
put("leaves_orange",23,leaves(25,[C(206,126,52),C(186,104,40),C(222,150,72),C(170,92,36)]))
put("leaves_bush",24,leaves(26,[C(120,148,90),C(102,130,76),C(140,164,104),C(88,114,64)],hole=0.24))   # arbustes de grève gris-vert
put("leaves_light",25,leaves(27,[C(148,160,52),C(130,142,44),C(164,176,66),C(112,126,38)]))       # V3.1 : vert-jaune
# bûche
lg=np.zeros((T,T,3),np.uint8); rng=np.random.default_rng(28)
B=[C(104,84,62),C(90,72,52),C(118,96,72),C(78,62,44)]
lg[:]=pal_img(rng,B,[5,4,2,2],blob=1)
for x in rng.choice(T,5,replace=False): lg[:,x]=(lg[:,x].astype(int)*0.75).astype(np.uint8)
put("log",26,lg)
lt=np.zeros((T,T,3),np.uint8)
yy,xx=np.mgrid[0:T,0:T]; rr=np.maximum(np.abs(yy-7.5),np.abs(xx-7.5))
lt[:]=C(160,128,84); lt[(rr.astype(int)%2)==0]=C(140,110,70); lt[rr>6.5]=C(96,76,56)
put("log_top",27,lt)
# herbes hautes / fleurs (alpha)
def plant(seed,cols,n=11,hmin=6,hmax=15,tip=None):
    """touffe de brins de 1 px sur des colonnes distinctes, haut incliné (tip : teinte de la pointe)"""
    rng=np.random.default_rng(seed); img=np.zeros((T,T,4),np.uint8)
    for x in rng.choice(np.arange(1,T-1),min(n,T-2),replace=False):
        h=rng.integers(hmin,hmax); lean=rng.choice([-1,0,0,1]); k0=int(h*rng.uniform(0.5,0.8))
        c=np.array(cols[rng.integers(0,len(cols))]+(255,),np.uint8)
        for k in range(h):
            y=T-1-k; xx_=x+(lean if k>=k0 else 0)
            if 0<=xx_<T: img[y,xx_]=np.array(tip+(255,),np.uint8) if (tip and k==h-1) else c
    return img
put("tallgrass",28,plant(29,[C(84,140,48),C(70,122,40),C(100,154,58),C(62,106,36),C(112,160,64)],n=11,hmin=6,tip=C(132,170,74)))
put("drygrass",29,plant(30,[C(166,150,92),C(146,130,78),C(182,166,108),C(128,114,68),C(116,124,62)],n=7,hmin=7,tip=C(112,92,60)))
def flower(seed,petal,center):
    """deux fleurs sur tiges fines, petites feuilles"""
    rng=np.random.default_rng(seed); img=np.zeros((T,T,4),np.uint8)
    st=np.array(C(70,122,42)+(255,),np.uint8); lf=np.array(C(90,142,54)+(255,),np.uint8)
    for cx in (rng.integers(3,7),rng.integers(9,13)):
        cy=rng.integers(3,8); img[cy+1:T,cx]=st
        for yl in rng.choice(np.arange(cy+4,T-1),2,replace=False):
            d=rng.choice([-1,1]); img[yl,cx+d]=lf; img[yl-1,cx+2*d]=lf
        for dx,dy in [(0,-1),(0,1),(-1,0),(1,0)]: img[cy+dy,cx+dx]=np.array(petal+(255,),np.uint8)
        img[cy,cx]=np.array(center+(255,),np.uint8)
    return img
put("flower_yellow",30,flower(31,C(236,204,48),C(200,140,24)))
put("flower_white",31,flower(32,C(238,238,228),C(230,190,40)))
# câble / chaîne
cb=np.zeros((T,T,3),np.uint8); cb[:]=C(62,68,78)             # câble mince (4 px) : torons à peine marqués
for y in range(0,T,4): cb[y,:]=C(76,83,94)
put("cable",32,cb)
# lit de rivière (sous l'eau)
RB=[C(150,138,104),C(134,122,92),C(164,152,116),C(120,110,84)]
put("riverbed",33,pal_img(np.random.default_rng(33),RB,[5,4,3,2],blob=2))
# pierre moussue (rochers)
MS=[C(118,122,110),C(104,108,98),C(96,120,72),C(132,134,124)]
put("mossy_stone",34,pal_img(np.random.default_rng(34),MS,[5,4,2,2],blob=2))
# Nouvelles tuiles (index réservés : herbe 35-39, grève 40-44, rive 45-49, tablier 50-54)
# ext:herbe
put("grass_top_dry1",35,lawn(36,GD,[4,5,2,3,2,1.2],GDd,18))
TILES["grass_top_dry0"]=TILES["grass_top_dry"]; TILES["grass_top_dry2"]=TILES["grass_top_dry"]   # alias pour "grass_top_dry*"
# herbe clairsemée : terre visible entre les touffes
rg=np.random.default_rng(37)
cov=np.kron(rg.random((8,8)),np.ones((2,2)))*0.75+rg.random((T,T))*0.25>0.36        # trous de terre en paquets de 2 px
gp=np.where(cov[...,None],lawn(38,GD,[5,4,3,2,1.6,1],GDd,6),pal_img(rg,DC,[5,4,3,2,1],blob=1))
put("grass_top_patchy",36,gp)
# touffes basses (contenu sur les 8 px du bas : croix de 0,5 m)
put("grass_short",37,plant(38,[C(96,130,52),C(84,116,46),C(112,142,60),C(150,140,84),C(134,122,72)],n=10,hmin=3,hmax=9))
put("grass_short_dry",38,plant(39,[C(172,156,96),C(152,136,80),C(188,172,112),C(130,118,68),C(110,122,58)],n=9,hmin=3,hmax=9))
# plante feuillue façon fougère (bande verte entre pelouse et grève) : 3 tiges arquées, folioles alternées
def weeds(seed):
    rng=np.random.default_rng(seed); img=np.zeros((T,T,4),np.uint8)
    L=[C(60,108,40),C(76,128,48),C(92,144,56),C(108,158,64)]
    for x0,dx,h in ((7,0,rng.integers(13,16)),(6,-1,rng.integers(9,12)),(9,1,rng.integers(9,12))):
        for k in range(h):
            y=T-1-k; x=x0+int(round(dx*(k/h)**1.4*4)); img[y,x]=L[0]+(255,)
            if k>=3 and (k+dx)%2==0:
                sd=1 if (k//2)%2 else -1
                for q in (1,2):
                    xx=x+sd*q; yy=y-(q-1)
                    if 0<=xx<T and k<h-1: img[yy,xx]=L[rng.integers(1,4)]+(255,)
    return img
put("weeds",39,weeds(40))
# ext:greve
# galets calcaire (grève) : gros cailloux (3-5 px) blancs, contrastés, sur joints brun-gris sombres ; tuile raccordable
def pebbles(seed,n_st=14):
    rng=np.random.default_rng(seed)
    img=pal_img(rng,[C(130,110,84),C(124,104,80),C(136,116,88),C(118,100,76)],[5,4,3,2],blob=2).astype(int)   # joints brun chaud (taches de 2 px : moins de scintillement)
    PB=[C(244,230,202),C(238,220,188),C(246,236,212),C(236,212,176),C(240,222,190),C(230,206,170)]   # crème et ocre clair
    yy,xx=np.mgrid[0:T,0:T]; placed=np.zeros((T,T),bool); n=0
    for _ in range(300):
        if n>=n_st: break
        cy_,cx_=rng.uniform(0,T,2); ry,rx=rng.uniform(1.5,2.4),rng.uniform(1.6,2.6)
        dy=(yy-cy_+T/2)%T-T/2; dx=(xx-cx_+T/2)%T-T/2          # distance torique
        m=(dy/ry)**2+(dx/rx)**2<=1.0
        if (m&placed).sum()>0.35*m.sum(): continue
        n+=1
        ring=np.zeros((T,T),bool)                                 # liseré de joint autour du galet (sépare les galets voisins)
        for sy,sx in ((1,0),(-1,0),(0,1),(0,-1)): ring|=np.roll(m,(sy,sx),(0,1))
        ring&=~m; img[ring&placed]=np.array(C(124,104,80)); placed|=m
        c=np.array(PB[rng.integers(0,len(PB))])
        img[m]=c+rng.integers(-2,3,(m.sum(),1))
        img[m&((dy/ry+dx/rx)<-0.9)]+=6                           # reflet haut-gauche
        img[m&((dy/ry+dx/rx)>1.05)]-=22                          # ombre bas-droite
    for _ in range(8):                                          # gravillons dans les joints
        y,x=rng.integers(0,T,2)
        if not placed[y,x]: img[y,x]=C(176,168,152)
    return np.clip(img,0,255).astype(np.uint8)
for i in range(3): put(f"pebbles{i}",40+i,pebbles(40+i))
# buttes d'herbe drue : dessus en touffes sombres, côté en brins de hauteurs variées (base sombre, pointes claires)
TG=[C(84,138,52),C(72,124,46),C(100,156,62),C(64,110,40),C(118,168,72)]
tt_=pal_img(np.random.default_rng(43),[C(70,118,44),C(60,104,38),C(84,134,52),C(52,92,34)],[5,4,3,2],blob=2).astype(int); rg=np.random.default_rng(44)
for _ in range(16):                                              # touffes : petit éclat clair + creux sombre
    y,x=rg.integers(0,T,2); c=np.array([C(112,166,70),C(128,176,80),C(146,166,86)][rg.integers(0,3)])
    tt_[y,x]=c; tt_[y,(x+1)%T]=c*0.9; tt_[(y+1)%T,x]=(c*0.55).astype(int)
put("tuft_top",43,np.clip(tt_,0,255).astype(np.uint8))
ts_=pal_img(np.random.default_rng(45),[C(52,90,36),C(60,100,40),C(46,80,32)],[3,2,2],blob=1).astype(int); rg=np.random.default_rng(46)
for _ in range(15):                                              # brins : du bas vers le haut, légère courbure
    x=rg.integers(0,T); h=rg.integers(7,17); lean=rg.choice([-1,0,1]); c=np.array(TG[rg.integers(0,len(TG))])
    for k in range(h):
        y=T-1-k; xx_=(x+(lean if k>h*0.55 else 0))%T; f=0.72+0.45*k/h
        ts_[y,xx_]=np.clip(c*f,0,255).astype(int)
    if rg.random()<0.2: ts_[T-h:T-h+2,x]=C(152,150,86)          # pointe sèche
put("tuft_side",44,np.clip(ts_,0,255).astype(np.uint8))
# v3.1 : galets mêlés d'herbe (bloc PEB_GRASS), arbustes plus clairs et contrastés, herbes en croix de la grève
pg=pebbles(72,8).astype(int); rg=np.random.default_rng(73)
for _ in range(7):                                               # touffes vertes dans les joints
    y,x=rg.integers(0,T,2); c=np.array(TG[rg.integers(0,len(TG))])
    for dy,dx in ((0,0),(0,1),(1,0),(-1,0),(0,-1),(1,1)):
        if rg.random()<0.8: pg[(y+dy)%T,(x+dx)%T]=np.clip(c*rg.uniform(0.7,1.1),0,255)
put("pebbles_grass",72,np.clip(pg,0,255).astype(np.uint8))
lb=leaves(26,[C(150,172,108),C(122,148,88),C(176,194,132),C(96,122,70)],hole=0.38).astype(int); rg=np.random.default_rng(74)
hl=(rg.random((T,T))<0.22)&(lb[...,3]>0); lb[hl,:3]=np.clip(lb[hl,:3]*1.5,0,255)    # éclats clairs (feuilles au soleil)
dk=(rg.random((T,T))<0.18)&(lb[...,3]>0)&~hl; lb[dk,:3]=(lb[dk,:3]*0.45).astype(int)  # creux sombres
sv=(rg.random((T,T))<0.1)&(lb[...,3]>0)&~dk; lb[sv,:3]=np.array(C(206,218,176))          # revers argentés des feuilles (photo)
put("leaves_bush",24,np.clip(lb,0,255).astype(np.uint8))   # redéclarée : arbustes de grève gris-vert, plus clairs et contrastés
put("grass_strand",73,plant(75,[C(128,146,98),C(110,128,84),C(146,160,112),C(96,112,72),C(160,164,118)],n=12,hmin=8,tip=C(176,172,124)))
put("tuft_plant",74,plant(76,TG+[C(152,150,86)],n=13,hmin=5,hmax=15,tip=C(140,176,84)))
put("grass_dense",75,plant(77,[C(78,134,46),C(66,118,40),C(92,148,56),C(58,102,34),C(106,156,62)],n=14,hmin=9,hmax=16,tip=C(128,168,72)))
# ext:rive
# ext:tablier
# panneau de poutre latérale 2 m x 1,5 m (32x24 px, alpha) : croisillon en X de 3 px, gousset carré plein au croisement,
# montants aux bords du panneau, goussets d'angle ; acier gris. Découpé en 3 tuiles : haut gauche, haut droite, bas (2 demi-tuiles)
SM=np.array(C(44,48,56)+(255,),np.uint8); SH=np.array(C(58,63,72)+(255,),np.uint8); SK=np.array(C(26,28,34)+(255,),np.uint8)   # acier gris (face au soleil rasant : albédo sombre)
PH,PW=24,32
pan=np.zeros((PH,PW,4),np.uint8)
for x in range(PW):                                  # diagonales en escalier, 3 px (arête haute claire, basse sombre)
    for xx in (x,PW-1-x):
        y=int(x*(PH-1)/(PW-1)+0.5)
        for dy,c in ((-1,SH),(0,SM),(1,SK)):
            if 0<=y+dy<PH: pan[y+dy,xx]=c
pan[:,0:2]=SM; pan[:,0]=SH; pan[:,PW-1]=SK           # montants (partagés avec le panneau voisin : 3 px)
yy,xx=np.mgrid[0:PH,0:PW]
for (cx,cy) in ((0,0),(PW,0),(0,PH),(PW,PH)):       # goussets d'angle (se rejoignent d'un panneau à l'autre)
    tri=np.abs(xx+0.5-cx)+np.abs(yy+0.5-cy)*1.2<5
    pan[tri]=SM
sq=(np.abs(xx-15.5)<=4)&(np.abs(yy-11.5)<=4)          # gousset carré plein (8x8), sans point central
pan[sq]=SM; pan[sq&((xx==12)|(yy==8))]=SH; pan[sq&((xx==19)|(yy==15))]=SK
for (ry,rx) in ((9,13),(9,18),(14,13),(14,18)):
    pan[ry,rx]=SH                                    # rivets d'angle
put("truss_a",50,pan[0:16,0:16]); put("truss_b",51,pan[0:16,16:32])
put("truss_c",52,np.concatenate([pan[16:24,0:16],pan[16:24,16:32]],0))
Image.fromarray(atlas,"RGBA").save("atlas.png")
import json; json.dump(TILES,open("tiles.json","w"),indent=0)
# aperçu agrandi
prev=np.array(Image.fromarray(atlas).resize((ATLAS_N*T*4,ATLAS_N*T*4),Image.NEAREST))
bg=np.zeros_like(prev); bg[...,:3]=(40,40,48); bg[...,3]=255
a=prev[...,3:4]/255.0; comp=(prev[...,:3]*a+bg[...,:3]*(1-a)).astype(np.uint8)
Image.fromarray(comp[:3*T*4]).save("atlas_preview.png")
print(len(TILES),"tiles")
