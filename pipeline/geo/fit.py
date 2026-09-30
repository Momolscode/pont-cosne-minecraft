import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))   # chemins relatifs au dossier du script
import numpy as np
from scipy.optimize import least_squares
np.set_printoptions(precision=3,suppress=True)
# ---- 2D observations (720x1280 photo)
obs={
 'nleg_top':(236,229),'fleg_top':(380,270),'nleg_pier':(211,560),
 'pier_tl':(160,560),'pier_bl':(153,700),'pier_tr':(400,573),'pier_br':(393,693),
 'farpyl_top':(35,489),'fardeck_top':(35,550),
 'tc1':(380,496),'tc2':(560,467),'tc3':(720,449),
 'bc1':(420,538),'bc2':(720,536),
}
W=10.0   # leg spacing (scale anchor, blocks)
names=['cx','cy','cz','yaw','pitch','roll','f','Hd','ht','Hp','Ht','Wp','dp','L','Wd','s1','s2','s3','s4','s5']
x0=np.array([-45,20,5, -0.38, 0.05, 0.0, 890, 9,3,5,24, 16,6,90,8, -8,-20,-30,-10,-30],float)
lo=np.array([-150,-10,1,-1.5,-0.4,-0.15,600, 5,1.5,2,12, 10,3,40,5, -40,-80,-120,-60,-120],float)
hi=np.array([ 5,  80,15, 1.5, 0.5, 0.15,1400,16,4.5,12,40, 30,10,250,9.8, 0,0,0,0,0],float)
def rot(yaw,pitch,roll):
    # camera looks along +d; world bridge frame: s (x), t (y), z up
    cy_,sy_=np.cos(yaw),np.sin(yaw); cp,sp=np.cos(pitch),np.sin(pitch); cr,sr=np.cos(roll),np.sin(roll)
    fwd=np.array([cy_*cp, sy_*cp, sp])          # yaw measured from +s axis
    right=np.array([sy_,-cy_,0.0])
    up=np.cross(right,fwd)
    r2=cr*right+sr*up; u2=-sr*right+cr*up
    return fwd,r2,u2
def proj(p,P):
    cx,cy,cz,yaw,pitch,roll,f=P[:7]
    fwd,r,u=rot(yaw,pitch,roll)
    d=np.array(p)-np.array([cx,cy,cz])
    zc=d@fwd; return np.array([360+f*(d@r)/zc, 640-f*(d@u)/zc]), zc
def model(P):
    Hd,ht,Hp,Ht,Wp,dp,L,Wd,s1,s2,s3,s4,s5=P[7:]
    return {
     'nleg_top':(0,W/2,Ht),'fleg_top':(0,-W/2,Ht),'nleg_pier':(0,W/2,Hp),
     'pier_tl':(-dp/2,Wp/2,Hp),'pier_bl':(-dp/2,Wp/2,0),'pier_tr':(-dp/2,-Wp/2,Hp),'pier_br':(-dp/2,-Wp/2,0),
     'farpyl_top':(L,-W/2,Ht),'fardeck_top':(L,Wd/2,Hd),
     'tc1':(s1,Wd/2,Hd),'tc2':(s2,Wd/2,Hd),'tc3':(s3,Wd/2,Hd),
     'bc1':(s4,Wd/2,Hd-ht),'bc2':(s5,Wd/2,Hd-ht),
    }
wts={'fardeck_top':0.7,'farpyl_top':0.7}
def resid(P):
    m=model(P); r=[]
    for k,(u,v) in obs.items():
        q,zc=proj(m[k],P); w=wts.get(k,1.0)
        r+= [w*(q[0]-u), w*(q[1]-v), (0.0 if zc>1 else 1e3*(1-zc))]
    Hd,ht,Hp=P[7],P[8],P[9]
    r+=[ 3*(Hd-ht-Hp-2.0) ]            # pier top ~2 blocks below road deck
    r+=[ 2*(ht-3.0) ]                   # truss ~3 blocks
    r+=[ 10*P[5] ]                      # roll small
    return np.array(r)
best=None
for seed in range(40):
    rng=np.random.default_rng(seed)
    x=x0+rng.normal(0,1,len(x0))*(hi-lo)*0.08
    x=np.clip(x,lo+1e-6,hi-1e-6)
    s=least_squares(resid,x,bounds=(lo,hi),max_nfev=4000)
    if best is None or s.cost<best.cost: best=s
P=best.x
print("cost",best.cost)
for n,v in zip(names,P): print(f"{n:6s} {v:8.3f}")
m=model(P)
for k,(u,v) in obs.items():
    q,zc=proj(m[k],P); print(f"{k:12s} obs=({u},{v}) fit=({q[0]:.0f},{q[1]:.0f}) depth={zc:.1f}")
fwd,r,u=rot(*P[3:6])
# horizon & fov
print("vFOV deg",np.degrees(2*np.arctan(640/P[6])),"hFOV",np.degrees(2*np.arctan(360/P[6])))
np.save("fitP.npy",P)
