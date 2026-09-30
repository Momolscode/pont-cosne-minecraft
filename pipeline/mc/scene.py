# Construit la scène Blender depuis world.npz et rend une image.
# usage: python scene.py OUT.png WIDTH SAMPLES [key=val ...]      (hauteur = WIDTH*16/9)
#  lumière : sun_az (° depuis l'axe caméra d'origine, + = gauche)  sun_el (°)  sun_str  sky_str  expo
#            sun_col=r,g,b   fog_col=r,g,b   fog_d  fog_max  cloud_op  cloud_em  bump  look="AgX - ..."
#  V3.1 arrière-plan (défauts = V3, effet nul) :
#            fog_d0 (m) : brume V3 (échelle fog_dn=900, couleur fog_coln) en deçà, échelle fog_d et couleur fog_col au-delà
#            fog_warm (0-1) fog_warm_col=r,g,b fog_warm_pow (2) : brume lointaine plus chaude face au soleil
#            cloud_col=r,g,b (émission)  cloud_sun cloud_sun_col=r,g,b (lueur des faces au soleil)
#            cloud_d0 cloud_d1 (m) : nuages estompés entre d0 et d1 (smoothstep ; cloud_d1=0 : pas d'estompage)
#  caméra  : cam_fwd / cam_right / cam_up (blocs = m, relatif à la vue)  cam_yaw / cam_pitch (°)  zoom
#            (le soleil reste fixe dans le monde quand la caméra bouge -> frames début/fin cohérentes)
#  divers  : save_blend=chemin.blend   bounces  diff_b  transp_b  adapt
#            border=x0,x1,y0,y1 (fractions 0-1, y=0 en bas : rend et recadre une zone, pour tester vite)
#            threads=N (0 = auto)   seed=N
#  animation : anim=1 -> OUT devient un motif de fichiers (ex. frames/f_####.png ; les # = n° de frame, 1..frames)
#            frames=150  fps=15  frame_start=1  frame_end=frames  frame_step=1 (sous-ensemble / reprise)
#            overwrite=0 : les frames déjà présentes sont sautées (écriture via .part.png puis renommage)
#            fin du travelling : cam_fwd1 cam_right1 cam_up1 cam_yaw1 cam_pitch1 zoom1 (défaut = valeur de départ)
#            ease=1 (0 = linéaire, 1 = départ/arrivée adoucis)   le soleil reste fixe dans le monde
#            cloud_dx cloud_dy : dérive des nuages sur toute la durée (m ; dx vers la droite de la vue d'origine, dy vers le fond)
#            w_flow : courant de l'eau (m/s, vers la droite de l'image)  w_evol (défaut w_flow/2) : évolution sur place
#            sway : amplitude des herbes au sommet (m, 0 = off)  sway_T (période, s, 2.6)  sway_L (longueur d'onde du vent, m, 7)
#            graine de bruit fixe, render.use_persistent_data (la scène n'est construite qu'une fois)
import bpy, numpy as np, math, sys, time, json
from mathutils import Matrix, Vector
import os
SP=os.environ.get("PONT_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # dossier pipeline/
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
OUT=os.path.abspath(args[0]); WIDTH=int(args[1]); SAMPLES=int(args[2])
KV=dict(a.split("=",1) for a in args[3:])
USED=set()
def kv(k,d): USED.add(k); return type(d)(KV.get(k,d))
def kvs(k,d): USED.add(k); return KV.get(k,d)
SUN_EL=kv("sun_el",13.0); SUN_AZ_REL=kv("sun_az",150.0)   # angle depuis l'avant caméra, vers la gauche
SUN_STR=kv("sun_str",4.0); SKY_STR=kv("sky_str",1.0); EXPO=kv("expo",0.0)
FOG_D=kv("fog_d",900.0); FOG_MAX=kv("fog_max",0.55)
LOOK=kvs("look","AgX - Medium High Contrast")
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
W=np.load(f"{SP}/mc/world.npz")
atlas=bpy.data.images.load(f"{SP}/mc/atlas.png"); atlas.alpha_mode='STRAIGHT'

# ---------------- caméra (ajustement photo)
P=np.load(f"{SP}/geo/fitP_rollfree.npy")
def rot(yaw,pitch,roll):
    cy_,sy_=np.cos(yaw),np.sin(yaw); cp,sp=np.cos(pitch),np.sin(pitch); cr,sr=np.cos(roll),np.sin(roll)
    fwd=np.array([cy_*cp, sy_*cp, sp]); right=np.array([sy_,-cy_,0.0]); up=np.cross(right,fwd)
    return fwd, cr*right+sr*up, -sr*right+cr*up
cx0,cy0,cz0,yaw0,pitch0,roll,fpx=P[:7]
roll=kv("roll_scale",1.0)*roll
fwd0,_,_=rot(yaw0,pitch0,roll)                    # axe de la photo d'origine (référence soleil)
CAMK=("cam_fwd","cam_right","cam_up","cam_yaw","cam_pitch","zoom")
CAM0={k:kv(k,1.0 if k=="zoom" else 0.0) for k in CAMK}
def cam_pose(c):
    """paramètres caméra (dict CAMK) -> matrice monde, focale (mm), (cx,cy,cz,yaw,pitch,fwd,rgt,upv)"""
    yaw=yaw0+math.radians(c["cam_yaw"]); pitch=pitch0+math.radians(c["cam_pitch"])
    _fh=(math.cos(yaw),math.sin(yaw)); _rh=(math.sin(yaw),-math.cos(yaw))
    cx=cx0+(c["cam_fwd"]*_fh[0]+c["cam_right"]*_rh[0]); cy=cy0+(c["cam_fwd"]*_fh[1]+c["cam_right"]*_rh[1]); cz=cz0+c["cam_up"]
    fwd,rgt,upv=rot(yaw,pitch,roll)
    M=Matrix(((rgt[0],upv[0],-fwd[0],cx),(rgt[1],upv[1],-fwd[1],cy),(rgt[2],upv[2],-fwd[2],cz),(0,0,0,1)))
    return M,fpx/720.0*36.0*c["zoom"],(cx,cy,cz,yaw,pitch,fwd,rgt,upv)
ANIM=kv("anim",0)>0                               # mode animation (section en fin de fichier)
cam=bpy.data.cameras.new("cam"); co=bpy.data.objects.new("cam",cam); sc.collection.objects.link(co)
M,_lens,(cx,cy,cz,yaw,pitch,fwd,rgt,upv)=cam_pose(CAM0)
co.matrix_world=M
cam.sensor_fit='HORIZONTAL'; cam.sensor_width=36.0; cam.lens=_lens
cam.clip_start=0.1; cam.clip_end=6000
sc.camera=co

# ---------------- matériaux
def fog_wrap(nt,shader_out,out_node):
    """mélange brume (émission) pour les rayons caméra selon la distance
    V3.1 (fog_d0>0) : deux couches. Jusqu'à fog_d0 (m), brume V3 (échelle fog_dn, couleur fog_coln) : pile et premier
    plan inchangés ; au-delà, brume plus dense (échelle fog_d) de couleur fog_col, tirée vers fog_warm_col face au soleil
    (fog_warm). brume = FOG_MAX*(1-exp(-(min(d,d0)/fog_dn + max(0,d-d0)/fog_d)))"""
    lp=nt.nodes.new("ShaderNodeLightPath"); cd=nt.nodes.new("ShaderNodeCameraData")
    def op(o,a,b=None,clamp=False):
        n=nt.nodes.new("ShaderNodeMath"); n.operation=o; n.use_clamp=clamp
        for k,x in enumerate((a,b)):
            if x is None: continue
            if isinstance(x,(int,float)): n.inputs[k].default_value=x
            else: nt.links.new(x,n.inputs[k])
        return n.outputs[0]
    dist=cd.outputs["View Distance"]
    if FOG_D0>0:
        e_near=op('DIVIDE',op('MINIMUM',dist,FOG_D0),FOG_DN)
        e=op('ADD',e_near,op('DIVIDE',op('MAXIMUM',op('SUBTRACT',dist,FOG_D0),0.0),FOG_D))
    else: e=op('DIVIDE',dist,FOG_D)
    f=op('SUBTRACT',1.0,op('EXPONENT',op('MULTIPLY',e,-1.0)))
    m6=nt.nodes.new("ShaderNodeMath"); m6.operation='MULTIPLY'; nt.links.new(op('MULTIPLY',f,FOG_MAX),m6.inputs[0]); nt.links.new(lp.outputs["Is Camera Ray"],m6.inputs[1])
    em=nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value=FOG_COL; em.inputs["Strength"].default_value=FOG_STR
    def mix(fac,a,b):
        mc=nt.nodes.new("ShaderNodeMix"); mc.data_type='RGBA'; so={x.identifier:x for x in list(mc.inputs)+list(mc.outputs)}
        for k,x in (("A_Color",a),("B_Color",b)):
            if isinstance(x,tuple): so[k].default_value=x
            else: nt.links.new(x,so[k])
        nt.links.new(fac,so["Factor_Float"]); return so["Result_Color"]
    col=FOG_COL
    if FOG_WARM>0:   # direction de vue = -Incoming : max(0, vue.soleil)^p * fog_warm
        geo=nt.nodes.new("ShaderNodeNewGeometry"); dp=nt.nodes.new("ShaderNodeVectorMath"); dp.operation='DOT_PRODUCT'
        dp.inputs[1].default_value=tuple(-float(x) for x in SUN_DIR_M); nt.links.new(geo.outputs["Incoming"],dp.inputs[0])
        col=mix(op('MULTIPLY',op('POWER',op('MAXIMUM',dp.outputs["Value"],0.0),FOG_WARM_POW),FOG_WARM,clamp=True),FOG_COL,FOG_WARM_COL)
    if FOG_D0>0:     # part de la couche lointaine dans la brume totale : 1 - (1-exp(-e_near))/(1-exp(-e))
        w=op('SUBTRACT',1.0,op('DIVIDE',op('SUBTRACT',1.0,op('EXPONENT',op('MULTIPLY',e_near,-1.0))),f),clamp=True)
        col=mix(w,FOG_COLN,col)
    if col is not FOG_COL: nt.links.new(col,em.inputs["Color"])
    mx=nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(m6.outputs[0],mx.inputs[0]); nt.links.new(shader_out,mx.inputs[1]); nt.links.new(em.outputs[0],mx.inputs[2])
    nt.links.new(mx.outputs[0],out_node.inputs["Surface"])
FOG_COL=tuple(float(x) for x in kvs("fog_col","0.62,0.66,0.78").split(","))+(1.0,)
FOG_COLN=tuple(float(x) for x in kvs("fog_coln","0.62,0.66,0.78").split(","))+(1.0,)
FOG_D0=kv("fog_d0",0.0); FOG_DN=kv("fog_dn",900.0); FOG_WARM=kv("fog_warm",0.0); FOG_WARM_POW=kv("fog_warm_pow",2.0)
FOG_WARM_COL=tuple(float(x) for x in kvs("fog_warm_col","1.0,0.72,0.45").split(","))+(1.0,)
_fh=np.array([fwd0[0],fwd0[1]]); _fh/=np.linalg.norm(_fh); _dh=math.cos(math.radians(SUN_AZ_REL))*_fh+math.sin(math.radians(SUN_AZ_REL))*np.array([-_fh[1],_fh[0]])
SUN_DIR_M=np.array([_dh[0]*math.cos(math.radians(SUN_EL)),_dh[1]*math.cos(math.radians(SUN_EL)),math.sin(math.radians(SUN_EL))])   # = sun_dir (ciel + soleil)
FOG_STR=kv("fog_str",1.0)
def mat_blocks(name,cutout=False):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial")
    tex=nt.nodes.new("ShaderNodeTexImage"); tex.image=atlas; tex.interpolation='Closest'; tex.extension='CLIP'
    bs=nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(tex.outputs["Color"],bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value=0.82
    bs.inputs["Specular IOR Level"].default_value=0.35
    # relief pixel léger
    bw=nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(tex.outputs["Color"],bw.inputs[0])
    bump=nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=kv("bump",0.25); bump.inputs["Distance"].default_value=0.02
    nt.links.new(bw.outputs[0],bump.inputs["Height"]); nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    sh=bs.outputs[0]
    if cutout:
        tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); nt.links.new(tex.outputs["Color"],tr.inputs["Color"])
        mx=nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value=0.28
        nt.links.new(bs.outputs[0],mx.inputs[1]); nt.links.new(tr.outputs[0],mx.inputs[2])
        tp=nt.nodes.new("ShaderNodeBsdfTransparent")
        mt=nt.nodes.new("ShaderNodeMixShader")
        gt=nt.nodes.new("ShaderNodeMath"); gt.operation='GREATER_THAN'; gt.inputs[1].default_value=0.5
        nt.links.new(tex.outputs["Alpha"],gt.inputs[0])
        nt.links.new(gt.outputs[0],mt.inputs[0]); nt.links.new(tp.outputs[0],mt.inputs[1]); nt.links.new(mx.outputs[0],mt.inputs[2])
        sh=mt.outputs[0]
    fog_wrap(nt,sh,out)
    return m
def mat_water():
    m=bpy.data.materials.new("water"); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial")
    bs=nt.nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value=(0.20,0.45,0.50,1)
    bs.inputs["Roughness"].default_value=kv("w_rough",0.035)
    bs.inputs["IOR"].default_value=1.333
    bs.inputs["Transmission Weight"].default_value=1.0
    # vaguelettes pixelisées
    tc=nt.nodes.new("ShaderNodeTexCoord")
    mul=nt.nodes.new("ShaderNodeVectorMath"); mul.operation='MULTIPLY'; mul.inputs[1].default_value=(8,8,8)
    fl=nt.nodes.new("ShaderNodeVectorMath"); fl.operation='FLOOR'
    dv=nt.nodes.new("ShaderNodeVectorMath"); dv.operation='DIVIDE'; dv.inputs[1].default_value=(8,8,8)
    nz=nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value=0.9; nz.inputs["Detail"].default_value=3
    nt.links.new(tc.outputs["Object"],mul.inputs[0]); nt.links.new(mul.outputs[0],fl.inputs[0]); nt.links.new(fl.outputs[0],dv.inputs[0]); nt.links.new(dv.outputs[0],nz.inputs["Vector"])
    if ANIM:   # décalage animé du bruit après la pixellisation (clés posées en fin de fichier)
        ofs=nt.nodes.new("ShaderNodeVectorMath"); ofs.operation='ADD'; ofs.name="w_anim"
        nt.links.new(dv.outputs[0],ofs.inputs[0]); nt.links.new(ofs.outputs[0],nz.inputs["Vector"])
    bump=nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value=kv("w_bump",0.12); bump.inputs["Distance"].default_value=0.05
    nt.links.new(nz.outputs["Fac"],bump.inputs["Height"]); nt.links.new(bump.outputs[0],bs.inputs["Normal"])
    fog_wrap(nt,bs.outputs[0],out)
    va=nt.nodes.new("ShaderNodeVolumeAbsorption"); va.inputs["Color"].default_value=(0.30,0.62,0.62,1); va.inputs["Density"].default_value=kv("w_dens",0.45)
    nt.links.new(va.outputs[0],out.inputs["Volume"])
    return m
def mat_cloud():
    m=bpy.data.materials.new("cloud"); m.use_nodes=True; nt=m.node_tree; nt.nodes.clear()
    out=nt.nodes.new("ShaderNodeOutputMaterial")
    df=nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value=(0.95,0.95,0.97,1)
    em=nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value=(1.0,0.93,0.88,1); em.inputs["Strength"].default_value=kv("cloud_em",0.35)
    tr=nt.nodes.new("ShaderNodeBsdfTranslucent"); tr.inputs["Color"].default_value=(1,0.98,0.96,1)
    mx=nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value=0.35
    nt.links.new(df.outputs[0],mx.inputs[1]); nt.links.new(tr.outputs[0],mx.inputs[2])
    tp=nt.nodes.new("ShaderNodeBsdfTransparent"); mt=nt.nodes.new("ShaderNodeMixShader"); mt.inputs[0].default_value=kv("cloud_op",0.85)
    ad=nt.nodes.new("ShaderNodeAddShader"); nt.links.new(mx.outputs[0],ad.inputs[0]); nt.links.new(em.outputs[0],ad.inputs[1])
    nt.links.new(tp.outputs[0],mt.inputs[1]); nt.links.new(ad.outputs[0],mt.inputs[2])
    nt.links.new(mt.outputs[0],out.inputs["Surface"])
    # V3.1 : teinte (cloud_col), lueur côté soleil (cloud_sun), estompage des nuages lointains (cloud_d0/d1).
    # Seuls les rayons qui voient les nuages (caméra, reflets, réfraction) en profitent : les rayons diffus et
    # d'ombre gardent les nuages V3, l'éclairage d'appoint qu'ils donnent aux ombres est donc inchangé.
    CC=kvs("cloud_col",""); CS=kv("cloud_sun",0.0); CD0,CD1=kv("cloud_d0",600.0),kv("cloud_d1",0.0)
    if CC or CS>0 or CD1>CD0:
        lpc=nt.nodes.new("ShaderNodeLightPath"); v1=nt.nodes.new("ShaderNodeMath"); v1.operation='ADD'
        v2=nt.nodes.new("ShaderNodeMath"); v2.operation='ADD'; v2.use_clamp=True
        nt.links.new(lpc.outputs["Is Camera Ray"],v1.inputs[0]); nt.links.new(lpc.outputs["Is Glossy Ray"],v1.inputs[1])
        nt.links.new(v1.outputs[0],v2.inputs[0]); nt.links.new(lpc.outputs["Is Transmission Ray"],v2.inputs[1]); vis=v2.outputs[0]
    if CC:
        mc=nt.nodes.new("ShaderNodeMix"); mc.data_type='RGBA'; so={x.identifier:x for x in list(mc.inputs)+list(mc.outputs)}
        so["A_Color"].default_value=tuple(em.inputs["Color"].default_value); so["B_Color"].default_value=tuple(float(x) for x in CC.split(","))+(1.0,)
        nt.links.new(vis,so["Factor_Float"]); nt.links.new(so["Result_Color"],em.inputs["Color"])
    if CS>0:   # lueur chaude des faces tournées vers le soleil : cloud_sun*max(0, N.soleil)
        geo=nt.nodes.new("ShaderNodeNewGeometry"); dp=nt.nodes.new("ShaderNodeVectorMath"); dp.operation='DOT_PRODUCT'
        dp.inputs[1].default_value=tuple(float(x) for x in SUN_DIR_M); nt.links.new(geo.outputs["Normal"],dp.inputs[0])
        s1=nt.nodes.new("ShaderNodeMath"); s1.operation='MAXIMUM'; s1.inputs[1].default_value=0.0; nt.links.new(dp.outputs["Value"],s1.inputs[0])
        s2=nt.nodes.new("ShaderNodeMath"); s2.operation='MULTIPLY'; s2.inputs[1].default_value=CS; nt.links.new(s1.outputs[0],s2.inputs[0])
        s3=nt.nodes.new("ShaderNodeMath"); s3.operation='MULTIPLY'; nt.links.new(s2.outputs[0],s3.inputs[0]); nt.links.new(vis,s3.inputs[1])
        e2=nt.nodes.new("ShaderNodeEmission"); e2.inputs["Color"].default_value=tuple(float(x) for x in kvs("cloud_sun_col","1.0,0.62,0.38").split(","))+(1.0,)
        nt.links.new(s3.outputs[0],e2.inputs["Strength"])
        a2=nt.nodes.new("ShaderNodeAddShader"); nt.links.new(ad.outputs[0],a2.inputs[0]); nt.links.new(e2.outputs[0],a2.inputs[1]); nt.links.new(a2.outputs[0],mt.inputs[2])
    if CD1>CD0:   # opacité * (1 - smoothstep(d0, d1, distance)) pour les rayons qui voient les nuages
        op=mt.inputs[0].default_value
        cdn=nt.nodes.new("ShaderNodeCameraData"); mr=nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type='SMOOTHSTEP'
        mr.inputs["From Min"].default_value=CD0; mr.inputs["From Max"].default_value=CD1
        mr.inputs["To Min"].default_value=op; mr.inputs["To Max"].default_value=0.0
        nt.links.new(cdn.outputs["View Distance"],mr.inputs["Value"])
        mo=nt.nodes.new("ShaderNodeMapRange"); mo.inputs["To Min"].default_value=op; nt.links.new(vis,mo.inputs["Value"]); nt.links.new(mr.outputs["Result"],mo.inputs["To Max"])
        nt.links.new(mo.outputs["Result"],mt.inputs[0])
    return m
MATS={"opaque":mat_blocks("blocks"),"cutout":mat_blocks("cutout",True),"water":mat_water(),"cloud":mat_cloud()}
MATS["plants"]=MATS["cutout"]
def mat_steel(name,cutout=False):
    """acier du tablier : quasi mat (le reflet du soleil rasant sur les faces côté caméra, qui renvoient
    presque exactement vers l'objectif, les blanchissait) ; treillis sans translucidité"""
    m=mat_blocks(name,cutout)
    for n in m.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            n.inputs["Roughness"].default_value=0.9; n.inputs["Specular IOR Level"].default_value=0.05
        if n.type=='MIX_SHADER' and any(l.from_node.type=='BSDF_TRANSLUCENT' for l in n.inputs[2].links):
            n.inputs[0].default_value=0.0
    return m
MATS["steel"]=mat_steel("steel"); MATS["truss"]=mat_steel("truss",True)

# ---------------- maillages (foreach_set)
def make_mesh(name,V,U,mat):
    n=len(V)
    if n==0: return
    me=bpy.data.meshes.new(name)
    me.vertices.add(n*4); me.vertices.foreach_set("co",V.reshape(-1).astype(np.float32))
    me.loops.add(n*4); me.loops.foreach_set("vertex_index",np.arange(n*4,dtype=np.int32))
    me.polygons.add(n); me.polygons.foreach_set("loop_start",np.arange(0,n*4,4,dtype=np.int32))
    uv=me.uv_layers.new(name="UVMap"); uv.data.foreach_set("uv",U.reshape(-1).astype(np.float32))
    me.update(calc_edges=True); me.validate(verbose=False)
    ob=bpy.data.objects.new(name,me); sc.collection.objects.link(ob); me.materials.append(mat)
    return ob
t0=time.time()
for k in ("opaque","cutout","water","cloud","plants"):
    if "V_"+k in W.files: make_mesh(k,W["V_"+k],W["U_"+k],MATS[k])
for k in ("steel","truss"):     # tablier (mesher.py)
    if "V_"+k in W.files: make_mesh(k,W["V_"+k],W["U_"+k],MATS[k])
print("meshes built",round(time.time()-t0,1),"s")
# plan d'eau lointain (hors monde voxel) et terre lointaine
def big_quad(name,x0,x1,y0,y1,z,mat):
    V=np.array([[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)]],np.float32); U=np.zeros((1,4,2),np.float32)
    return make_mesh(name,V,U,mat)
S0,S1=-100,430; T0,T1=-280,120
ring=[(-6000,S0,-6000,6000),(S1,6000,-6000,6000),(S0,S1,-6000,T0),(S0,S1,T1,6000)]
mw=mat_water()
for i,(a,b,c,d) in enumerate(ring): big_quad(f"farwater{i}",a,b,c,d,-0.12,mw)

# ---------------- ciel + soleil
w=bpy.data.worlds.new("w"); sc.world=w; w.use_nodes=True; nt=w.node_tree
bg=nt.nodes["Background"]; sky=nt.nodes.new("ShaderNodeTexSky"); sky.sky_type='MULTIPLE_SCATTERING'
fh=np.array([fwd0[0],fwd0[1]]); fh/=np.linalg.norm(fh); lh=np.array([-fh[1],fh[0]])
a=math.radians(SUN_AZ_REL); dh=math.cos(a)*fh+math.sin(a)*lh
sun_dir=np.array([dh[0]*math.cos(math.radians(SUN_EL)),dh[1]*math.cos(math.radians(SUN_EL)),math.sin(math.radians(SUN_EL))])
sky.sun_elevation=math.radians(SUN_EL)
sky.sun_rotation=math.atan2(dh[0],dh[1])      # blender: rotation autour de Z depuis +Y (horaire)
sky.sun_disc=False
sky.altitude=kv("alt",50.0)
sky.air_density=kv("air",1.0); sky.aerosol_density=kv("aer",0.5); sky.ozone_density=kv("ozone",1.0)
nt.links.new(sky.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=SKY_STR
ld=bpy.data.lights.new("sun",'SUN'); lo=bpy.data.objects.new("sun",ld); sc.collection.objects.link(lo)
ld.energy=SUN_STR; ld.angle=math.radians(kv("sun_ang",0.9))
ld.color=tuple(float(x) for x in kvs("sun_col","1.0,0.78,0.56").split(","))
lo.rotation_euler=Vector((-sun_dir[0],-sun_dir[1],-sun_dir[2])).to_track_quat('-Z','Y').to_euler()

# ---------------- rendu
sc.render.engine='CYCLES'; sc.cycles.device='CPU'
sc.cycles.samples=SAMPLES; sc.cycles.use_adaptive_sampling=True; sc.cycles.adaptive_threshold=kv("adapt",0.02)
sc.cycles.use_denoising=True; sc.cycles.denoiser='OPENIMAGEDENOISE'
sc.cycles.max_bounces=kv("bounces",6); sc.cycles.diffuse_bounces=kv("diff_b",2); sc.cycles.glossy_bounces=3
sc.cycles.transmission_bounces=6; sc.cycles.transparent_max_bounces=kv("transp_b",12); sc.cycles.volume_bounces=0
sc.cycles.caustics_reflective=False; sc.cycles.caustics_refractive=False
sc.cycles.blur_glossy=1.0
sc.render.resolution_x=WIDTH; sc.render.resolution_y=int(round(WIDTH*16/9)); sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX'
try: sc.view_settings.look=LOOK
except Exception as e: print("look err",e)
sc.view_settings.exposure=EXPO
_b=kvs("border","")
if _b:
    x0_,x1_,y0_,y1_=(float(x) for x in _b.split(","))
    sc.render.use_border=True; sc.render.use_crop_to_border=True
    sc.render.border_min_x,sc.render.border_max_x,sc.render.border_min_y,sc.render.border_max_y=x0_,x1_,y0_,y1_
_th=kv("threads",0)
if _th>0: sc.render.threads_mode='FIXED'; sc.render.threads=_th
sc.cycles.seed=kv("seed",0)
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_depth='16'
sc.render.filepath=OUT

# ---------------- animation (anim=1) : travelling, nuages, eau, herbes -> une clé par frame (save_blend = .blend animé)
if ANIM:
    import re
    NF=kv("frames",150); FPS=kv("fps",15)
    F0=max(1,kv("frame_start",1)); F1=min(NF,kv("frame_end",NF)); FSTEP=max(1,kv("frame_step",1))
    OVERWRITE=kv("overwrite",0)>0
    CAM1={k:kv(k+"1",CAM0[k]) for k in CAMK}      # pose de fin (défaut = départ)
    EASE=kv("ease",1.0)                           # 0 = linéaire, 1 = smoothstep (départ et arrivée en douceur)
    _ms=list(re.finditer(r"#+",OUT))
    if not _ms: OUT=os.path.splitext(OUT)[0]+"_####.png"; _ms=list(re.finditer(r"#+",OUT))
    if not OUT.lower().endswith(".png"): OUT+=".png"
    def fpath(f): m=_ms[-1]; return OUT[:m.start()]+str(f).zfill(m.end()-m.start())+OUT[m.end():]
    os.makedirs(os.path.dirname(OUT),exist_ok=True)
    sc.frame_start=1; sc.frame_end=NF; sc.render.fps=FPS
    sc.render.use_persistent_data=True; sc.cycles.use_animated_seed=False   # scène gardée en mémoire, bruit fixe
    bpy.context.preferences.edit.keyframe_new_interpolation_type='LINEAR'
    if not kv("fog_nee",0):   # brume = émission vue des seuls rayons caméra : inutile comme lumière (sinon arbre de lumières géant reconstruit à chaque frame)
        for m in bpy.data.materials:
            if m.node_tree and any(n.bl_idname=="ShaderNodeLightPath" and n.outputs["Is Camera Ray"].is_linked for n in m.node_tree.nodes):
                m.cycles.emission_sampling='NONE'
    fh0=np.array([math.cos(yaw0),math.sin(yaw0)]); rh0=np.array([fh0[1],-fh0[0]])   # axes horizontaux de la vue d'origine
    CL=kv("cloud_dx",0.0)*rh0+kv("cloud_dy",0.0)*fh0                             # dérive totale des nuages (m)
    WF=kv("w_flow",0.0); WE=kv("w_evol",0.5*WF)   # eau : courant vers -t (droite de l'image), évolution sur place
    SWAY=kv("sway",0.0); SWAY_T=kv("sway_T",2.6); SWAY_L=kv("sway_L",7.0)
    ob_cl=bpy.data.objects.get("cloud"); ob_pl=bpy.data.objects.get("plants")
    w_nodes=[m.node_tree.nodes["w_anim"] for m in bpy.data.materials if m.node_tree and "w_anim" in m.node_tree.nodes]
    # herbes : 2 harmoniques x 2 shape keys (cos/sin de la phase) ; déplacement nul au pied, maximal au sommet de chaque quad
    sk=[]
    if SWAY>0 and ob_pl:
        V=np.empty(len(ob_pl.data.vertices)*3,np.float32); ob_pl.data.vertices.foreach_get("co",V); V=V.reshape(-1,4,3)
        z0q=V[:,:,2].min(1); hq=V[:,:,2].max(1)-z0q; xy=V[:,:,:2].mean(1)      # pied, hauteur et position de chaque quad
        wz=np.where(hq[:,None]>1e-4,(V[:,:,2]-z0q[:,None])/np.maximum(hq,1e-4)[:,None],0.0)   # 0 en bas, 1 en haut
        hs=lambda a,b: np.modf(np.abs(np.sin(xy[:,0]*a+xy[:,1]*b)*43758.5453))[0]   # aléa par plante (même valeur pour les 2 quads d'une croix)
        r1,r2,r3=hs(12.9898,78.233),hs(39.346,11.135),hs(73.156,52.235)
        an=(r1-0.5)*0.8; d=np.stack([rh0[0]*np.cos(an)-rh0[1]*np.sin(an),rh0[0]*np.sin(an)+rh0[1]*np.cos(an)],1)   # vent vers la droite ±23°
        amp=SWAY*(0.7+0.6*r2)*hq
        ob_pl.shape_key_add(name="Basis",from_mix=False)
        for j,(a_,T_,L_) in enumerate(((1.0,SWAY_T,SWAY_L),(0.3,SWAY_T/2.7,SWAY_L/2.8))):
            ph=-2*np.pi*(xy@rh0)/L_+(1.2+j)*np.pi*r3                              # onde de vent qui traverse le champ
            for nm,fn in (("c",np.cos),("s",np.sin)):                            # sin(wt+ph) = sin wt.cos ph + cos wt.sin ph
                kb=ob_pl.shape_key_add(name=f"sway{j}{nm}",from_mix=False); kb.slider_min=-1.0
                D=np.zeros_like(V); D[:,:,:2]=wz[:,:,None]*(a_*amp*fn(ph))[:,None,None]*d[:,None,:]
                kb.data.foreach_set("co",(V+D).reshape(-1)); sk.append((kb,2*np.pi/T_,np.sin if nm=="c" else np.cos))
    co.rotation_mode='QUATERNION'; q_prev=None
    for f in range(1,NF+1):
        u=(f-1)/max(1,NF-1); t=(f-1)/FPS; e=(1-EASE)*u+EASE*u*u*(3-2*u)
        Mf,cam.lens,_=cam_pose({k:CAM0[k]+(CAM1[k]-CAM0[k])*e for k in CAMK})
        loc,q,_s=Mf.decompose()
        if q_prev is not None: q.make_compatible(q_prev)
        q_prev=q; co.location=loc; co.rotation_quaternion=q
        co.keyframe_insert("location",frame=f); co.keyframe_insert("rotation_quaternion",frame=f); cam.keyframe_insert("lens",frame=f)
        if ob_cl and CL.any(): ob_cl.location=(CL[0]*u,CL[1]*u,0.0); ob_cl.keyframe_insert("location",frame=f)
        if WF or WE:
            for n in w_nodes: n.inputs[1].default_value=(0.0,WF*t,WE*t); n.inputs[1].keyframe_insert("default_value",frame=f)
        for kb,om,fn in sk: kb.value=float(fn(om*t)); kb.keyframe_insert("value",frame=f)
    def render_anim():
        todo=[f for f in range(F0,F1+1,FSTEP) if OVERWRITE or not (os.path.isfile(fpath(f)) and os.path.getsize(fpath(f))>0)]
        print(f"ANIM {NF} frames à {FPS} i/s ; frames {F0}-{F1} pas {FSTEP} : {len(todo)} à rendre -> {OUT}",flush=True)
        T0=time.time()
        for i,f in enumerate(todo):
            sc.frame_set(f); p=fpath(f); tmp=p[:-4]+".part.png"; sc.render.filepath=tmp   # écriture atomique (reprise sûre)
            t0=time.time(); bpy.ops.render.render(write_still=True); os.replace(tmp,p)
            el=time.time()-T0
            print(f"FRAME {f} {time.time()-t0:.1f} s  ({i+1}/{len(todo)}, reste ~{el/(i+1)*(len(todo)-i-1)/60:.1f} min)",flush=True)
        print("RENDER_S",round(time.time()-T0,1))
_sb=kvs("save_blend","")
if _sb: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(_sb))
_unk=sorted(set(KV)-USED)
if _unk: print("ATTENTION paramètres inconnus ignorés :",_unk)
if ANIM: render_anim()
else: t0=time.time(); bpy.ops.render.render(write_still=True); print("RENDER_S",round(time.time()-t0,1))
