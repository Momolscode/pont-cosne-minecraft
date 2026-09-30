import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))   # chemins relatifs au dossier du script
import numpy as np
exec(open("fit.py").read().split("best=None")[0])   # reuse rot/proj defs
P=np.load("fitP.npy")
cx,cy,cz,yaw,pitch,roll,f=P[:7]
fwd,r,u=rot(yaw,pitch,roll)
C=np.array([cx,cy,cz])
def ray(x,y):
    d=fwd+ (x-360)/f*r - (y-640)/f*u
    return d/np.linalg.norm(d)
def hit_plane_z(x,y,h):
    d=ray(x,y); t=(h-C[2])/d[2]; return C+t*d
def hit_plane_t(x,y,tt):
    d=ray(x,y); k=(tt-C[1])/d[1]; return C+k*d
W=10.0
print("--- near cable (t=+W/2):")
for (x,y) in [(237,225),(330,250),(420,267),(550,271),(720,271)]:
    p=hit_plane_t(x,y,W/2); print((x,y),"-> s=%.1f z=%.1f"%(p[0],p[2]))
print("--- far cable (t=-W/2):")
for (x,y) in [(393,268),(405,279),(550,305),(720,338)]:
    p=hit_plane_t(x,y,-W/2); print((x,y),"-> s=%.1f z=%.1f"%(p[0],p[2]))
print("--- near hangers x on near cable:")
for x in [413,480,555,665]:
    # find y on near-cable polyline approx then backproject
    ys=np.interp(x,[237,330,420,550,720],[225,250,267,271,271]); p=hit_plane_t(x,ys,W/2); print(x,"s=%.1f"%p[0])
print("--- far hangers:")
for x in [452,494,545,606,681]:
    ys=np.interp(x,[393,405,720],[268,279,338]); p=hit_plane_t(x,ys,-W/2); print(x,"s=%.1f"%p[0])
print("--- main span cables (left):")
for (x,y) in [(218,280),(130,420),(40,545)]:
    p=hit_plane_t(x,y,W/2); print("near",(x,y),"-> s=%.1f z=%.1f"%(p[0],p[2]))
for (x,y) in [(350,310),(260,420),(170,525)]:
    p=hit_plane_t(x,y,-W/2); print("far",(x,y),"-> s=%.1f z=%.1f"%(p[0],p[2]))
print("--- ground points (z=0.5):")
for (x,y) in [(60,760),(60,805),(300,720),(300,760),(550,700),(550,760),(650,660),(500,655),(100,640)]:
    p=hit_plane_z(x,y,0.5); print((x,y),"-> s=%.1f t=%.1f dist=%.1f"%(p[0],p[1],np.hypot(p[0]-cx,p[1]-cy)))
print("--- horizon y at x=0,360,720:")
for x in [0,360,720]:
    # direction horizontal: find y where ray z-component = 0
    ys=np.linspace(300,900,6001); dz=[ray(x,yy)[2] for yy in ys]; i=np.argmin(np.abs(dz)); print(x,ys[i])
print("--- camera in bridge frame", C, "yaw deg",np.degrees(yaw),"pitch",np.degrees(pitch),"roll",np.degrees(roll))
print("fwd",fwd,"right",r,"up",u)
