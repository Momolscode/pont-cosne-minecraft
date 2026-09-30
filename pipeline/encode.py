# Frames PNG -> MP4 H.264 9:16 pour la story (avec la piste audio de la vidéo d'origine + une version sans audio)
# usage: python encode.py FRAMES SORTIE.mp4 [--fps 15] [--size 1080x1920] [--crf 18] [--audio source/pont-cosne_original.mov]
#                                          [--ffmpeg chemin] [--fade 0] [--preset slow]
#  FRAMES : motif de scene.py (ex. renders/frames/f_####.png), motif printf (f_%04d.png) ou dossier contenant une seule séquence
#  sorties : SORTIE.mp4 (vidéo + audio coupé à la durée de la vidéo) et SORTIE_sans_audio.mp4
#  mise à l'échelle lanczos pour couvrir SIZE puis recadrage centré (sans effet si les frames ont déjà la bonne taille)
#  ffmpeg : --ffmpeg, sinon ffmpeg du PATH, sinon celui du paquet imageio-ffmpeg (pip install imageio-ffmpeg)
import argparse, glob, os, re, shutil, subprocess, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # racine du projet
ap=argparse.ArgumentParser(description="frames PNG -> MP4 H.264 story 9:16")
ap.add_argument("frames"); ap.add_argument("out")
ap.add_argument("--fps",type=int,default=15)
ap.add_argument("--size",default="1080x1920")
ap.add_argument("--crf",type=int,default=18)
ap.add_argument("--preset",default="slow")
ap.add_argument("--audio",default=os.path.join(ROOT,"source","pont-cosne_original.mov"),help="'' = pas de version avec audio")
ap.add_argument("--fade",type=float,default=0.0,help="fondu de sortie de l'audio (s)")
ap.add_argument("--ffmpeg",default="")
a=ap.parse_args()

def find_ffmpeg():
    if a.ffmpeg: return a.ffmpeg
    p=shutil.which("ffmpeg")
    if p: return p
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: sys.exit("ffmpeg introuvable : passer --ffmpeg, l'ajouter au PATH ou pip install imageio-ffmpeg")
FF=find_ffmpeg()

# ---------------- séquence de frames : motif printf + numéros présents
fr=a.frames
if os.path.isdir(fr):
    seqs={}
    for f in os.listdir(fr):
        m=re.fullmatch(r"(.*?)(\d+)\.png",f)
        if m: seqs.setdefault((m.group(1),len(m.group(2))),[]).append(int(m.group(2)))
    if len(seqs)!=1: sys.exit(f"dossier {fr} : {len(seqs)} séquences PNG trouvées, donner le motif (ex. f_####.png)")
    (pre,nd),nums=seqs.popitem(); pat=os.path.join(fr,f"{pre}%0{nd}d.png")
else:
    ms=list(re.finditer(r"#+",fr))
    if ms: m=ms[-1]; pat=fr[:m.start()]+f"%0{m.end()-m.start()}d"+fr[m.end():]
    elif re.search(r"%0?\d*d",fr): pat=fr
    else: sys.exit("FRAMES doit contenir #### (ou %04d) ou être un dossier")
    d,b=os.path.split(pat); m=re.search(r"%0?(\d*)d",b)
    if not os.path.isdir(d or "."): sys.exit(f"dossier introuvable : {d}")
    rx=re.compile(re.escape(b[:m.start()])+(r"(\d{%s})"%m.group(1) if m.group(1) else r"(\d+)")+re.escape(b[m.end():])+"$")
    nums=[int(mm.group(1)) for f in os.listdir(d or ".") for mm in [rx.match(f)] if mm]
nums=sorted(nums)
if not nums: sys.exit(f"aucune frame pour {pat}")
miss=sorted(set(range(nums[0],nums[-1]+1))-set(nums))
if miss: sys.exit(f"frames manquantes ({len(miss)}) : {miss[:20]}{' ...' if len(miss)>20 else ''} -> les rendre (scene.py frame_start/frame_end) avant l'encodage")
N=len(nums); DUR=N/a.fps
W,H=(int(x) for x in a.size.lower().split("x"))
print(f"{N} frames ({nums[0]}..{nums[-1]}) à {a.fps} i/s = {DUR:.3f} s -> {W}x{H}  [{FF}]")

def run(cmd):
    print(" ".join(f'"{c}"' if (" " in c or "," in c) else c for c in cmd),flush=True)
    r=subprocess.run(cmd)
    if r.returncode: sys.exit(f"ffmpeg a échoué (code {r.returncode})")
out=os.path.abspath(a.out); os.makedirs(os.path.dirname(out),exist_ok=True)
mute=os.path.splitext(out)[0]+"_sans_audio.mp4"
# couvrir WxH en lanczos, recadrer au centre, puis RGB -> YUV 4:2:0 en BT.709 (plage TV) explicitement
vf=(f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
    f"scale=out_color_matrix=bt709:out_range=tv:flags=lanczos,format=yuv420p,setsar=1")
COL=["-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709","-color_range","tv"]
run([FF,"-hide_banner","-loglevel","warning","-y","-framerate",str(a.fps),"-start_number",str(nums[0]),"-i",pat,
     "-vf",vf,"-c:v","libx264","-preset",a.preset,"-crf",str(a.crf),"-profile:v","high","-pix_fmt","yuv420p",*COL,
     "-r",str(a.fps),"-frames:v",str(N),"-an","-map_metadata","-1","-movflags","+faststart",mute])
outs=[mute]
if a.audio:
    if not os.path.isfile(a.audio): print(f"ATTENTION audio introuvable ({a.audio}) : seule la version sans audio est produite")
    else:
        af="apad"+(f",afade=t=out:st={max(0.0,DUR-a.fade):.3f}:d={a.fade}" if a.fade>0 else "")
        run([FF,"-hide_banner","-loglevel","warning","-y","-i",mute,"-i",a.audio,"-map","0:v:0","-map","1:a:0",
             "-c:v","copy","-af",af,"-c:a","aac","-b:a","160k","-t",f"{DUR:.3f}",
             "-map_metadata","-1","-map_metadata:s:a","-1","-movflags","+faststart",out])   # pas de métadonnées (GPS) de la vidéo source
        outs.insert(0,out)
# contrôle : flux et durée lus par ffmpeg -i
for o in outs:
    info=subprocess.run([FF,"-hide_banner","-i",o],capture_output=True,text=True).stderr
    print(f"-> {o} ({os.path.getsize(o)/1e6:.1f} Mo)")
    for l in info.splitlines():
        if "Duration" in l or "Stream #" in l: print("   "+l.strip())
