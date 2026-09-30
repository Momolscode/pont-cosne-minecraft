import os as _os; _os.chdir(_os.path.dirname(_os.path.abspath(__file__)))   # chemins relatifs au dossier du script
import numpy as np
src=open("fit.py").read()
pre=src.split("best=None")[0]
exec(pre)
from scipy.optimize import least_squares
for roll_fix in [0.0, 0.02, 0.035, None]:
    lo2=lo.copy(); hi2=hi.copy()
    if roll_fix is not None:
        lo2[5]=roll_fix-1e-6; hi2[5]=roll_fix+1e-6
    lo2[12]=3.99; hi2[12]=4.01          # pier thickness 4
    lo2[13]=180; hi2[13]=300
    best=None
    for seed in range(30):
        rng=np.random.default_rng(seed)
        x=x0+rng.normal(0,1,len(x0))*(hi-lo)*0.06
        x=np.clip(x,lo2+1e-6,hi2-1e-6)
        s=least_squares(resid,x,bounds=(lo2,hi2),max_nfev=3000)
        if best is None or s.cost<best.cost: best=s
    P=best.x; m=model(P)
    errs=[np.hypot(*(proj(m[k],P)[0]-np.array(v))) for k,v in obs.items()]
    print(f"roll={np.degrees(P[5]):5.2f}deg cost={best.cost:8.1f} maxerr={max(errs):5.1f} med={np.median(errs):4.1f} | cam=({P[0]:.1f},{P[1]:.1f},{P[2]:.1f}) yaw={np.degrees(P[3]):.1f} pitch={np.degrees(P[4]):.1f} f={P[6]:.0f} Hd={P[7]:.1f} Hp={P[9]:.1f} Ht={P[10]:.1f} Wp={P[11]:.1f} L={P[13]:.0f} Wd={P[14]:.1f}")
    np.save(f"fitP_roll{'free' if roll_fix is None else int(round(np.degrees(roll_fix)))}.npy",P)
    for k,v in obs.items():
        q=proj(m[k],P)[0]; print(f"   {k:12s} err={np.hypot(*(q-np.array(v))):5.1f}")
