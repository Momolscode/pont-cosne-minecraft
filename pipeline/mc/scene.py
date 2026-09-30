# Construit la scène Blender depuis world.npz et rend une image.
# usage: python scene.py OUT.png WIDTH SAMPLES [key=val ...]      (hauteur = WIDTH*16/9)
#  lumière : sun_az (° depuis l'axe caméra d'origine, + = gauche)  sun_el (°)  sun_str  sky_str  expo
#            sun_col=r,g,b   fog_col=r,g,b   fog_d  fog_max  cloud_op  cloud_em  bump  look="AgX - ..."
#  caméra  : cam_fwd / cam_right / cam_up (blocs = m, relatif à la vue)  cam_yaw / cam_pitch (°)  zoom
#            (le soleil reste fixe dans le monde quand la caméra bouge -> frames début/fin cohérentes)
#  divers  : save_blend=chemin.blend   bounces  diff_b  transp_b  adapt
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
cx,cy,cz,yaw,pitch,roll,fpx=P[:7]
roll=kv("roll_scale",1.0)*roll
fwd0,_,_=rot(yaw,pitch,roll)                      # axe de la photo d'origine (référence soleil)
yaw+=math.radians(kv("cam_yaw",0.0)); pitch+=math.radians(kv("cam_pitch",0.0))
_fh=(math.cos(yaw),math.sin(yaw)); _rh=(math.sin(yaw),-math.cos(yaw))
cx+=kv("cam_fwd",0.0)*_fh[0]+kv("cam_right",0.0)*_rh[0]; cy+=kv("cam_fwd",0.0)*_fh[1]+kv("cam_right",0.0)*_rh[1]; cz+=kv("cam_up",0.0)
fwd,rgt,upv=rot(yaw,pitch,roll)
cam=bpy.data.cameras.new("cam"); co=bpy.data.objects.new("cam",cam); sc.collection.objects.link(co)
M=Matrix(((rgt[0],upv[0],-fwd[0],cx),(rgt[1],upv[1],-fwd[1],cy),(rgt[2],upv[2],-fwd[2],cz),(0,0,0,1)))
co.matrix_world=M
cam.sensor_fit='HORIZONTAL'; cam.sensor_width=36.0; cam.lens=fpx/720.0*36.0*kv("zoom",1.0)
cam.clip_start=0.1; cam.clip_end=6000
sc.camera=co

# ---------------- matériaux
def fog_wrap(nt,shader_out,out_node):
    """mélange brume (émission) pour les rayons caméra selon la distance"""
    lp=nt.nodes.new("ShaderNodeLightPath"); cd=nt.nodes.new("ShaderNodeCameraData")
    m1=nt.nodes.new("ShaderNodeMath"); m1.operation='DIVIDE'; m1.inputs[1].default_value=FOG_D
    nt.links.new(cd.outputs["View Distance"],m1.inputs[0])
    m2=nt.nodes.new("ShaderNodeMath"); m2.operation='MULTIPLY'; m2.inputs[1].default_value=-1.0
    nt.links.new(m1.outputs[0],m2.inputs[0])
    m3=nt.nodes.new("ShaderNodeMath"); m3.operation='EXPONENT'; nt.links.new(m2.outputs[0],m3.inputs[0])
    m4=nt.nodes.new("ShaderNodeMath"); m4.operation='SUBTRACT'; m4.inputs[0].default_value=1.0; nt.links.new(m3.outputs[0],m4.inputs[1])
    m5=nt.nodes.new("ShaderNodeMath"); m5.operation='MULTIPLY'; m5.inputs[1].default_value=FOG_MAX; nt.links.new(m4.outputs[0],m5.inputs[0])
    m6=nt.nodes.new("ShaderNodeMath"); m6.operation='MULTIPLY'; nt.links.new(m5.outputs[0],m6.inputs[0]); nt.links.new(lp.outputs["Is Camera Ray"],m6.inputs[1])
    em=nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value=FOG_COL; em.inputs["Strength"].default_value=FOG_STR
    mx=nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(m6.outputs[0],mx.inputs[0]); nt.links.new(shader_out,mx.inputs[1]); nt.links.new(em.outputs[0],mx.inputs[2])
    nt.links.new(mx.outputs[0],out_node.inputs["Surface"])
FOG_COL=tuple(float(x) for x in kvs("fog_col","0.62,0.66,0.78").split(","))+(1.0,)
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
    return m
MATS={"opaque":mat_blocks("blocks"),"cutout":mat_blocks("cutout",True),"water":mat_water(),"cloud":mat_cloud()}

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
for k in ("opaque","cutout","water","cloud"):
    make_mesh(k,W["V_"+k],W["U_"+k],MATS[k])
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
sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_depth='16'
sc.render.filepath=OUT
_sb=kvs("save_blend","")
if _sb: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(_sb))
_unk=sorted(set(KV)-USED)
if _unk: print("ATTENTION paramètres inconnus ignorés :",_unk)
t0=time.time(); bpy.ops.render.render(write_still=True); print("RENDER_S",round(time.time()-t0,1))
