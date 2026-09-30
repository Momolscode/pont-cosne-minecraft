# Pont de Cosne × Minecraft — brief de reprise (Claude Code + Higgsfield)

## 0. Démarrage rapide — à coller dans Claude Code

```
Lis HANDOFF.md. Connecte Higgsfield (section 4), puis lance la piste A :
3 vidéos 9:16 de ~10 s depuis renders/final_1080x1920.png (Kling 3, Veo 3.1, Seedance 2.5)
avec le prompt A. Montre-moi les résultats avant d'aller plus loin (ça consomme des crédits).
```

## 1. Objectif

Story Snapchat (9:16) : version « Minecraft » artistique de ma vidéo du pont suspendu de Cosne-sur-Loire,
avec le thème Minecraft en musique. Il faut un rendu « wow » qui garde la composition de la vidéo d'origine.

Historique des retours :
1. « Refais cette photo artistique pour ma story snap, y a le thème Minecraft en musique »
2. V1 (animation pixel-art 2D) → « C'est mauvais, refais »
3. « Utilise Higgsfield si besoin » (pas d'accès Higgsfield dans la session où V2 a été faite)
4. V2 (reconstruction 3D voxel, `renders/final_*`) → « on retravaille tout ça avec Higgsfield »

## 2. Contenu

| Chemin | Quoi |
|---|---|
| `source/pont-cosne_original.mov` | Vidéo Snap d'origine : 720×1280, 10 s, 15 i/s, avec les incrustations Snap (date, sticker). **La piste audio contient la musique de la story.** |
| `source/photo_ref_720x1280.png` | Image fixe nettoyée : médiane des frames, puis date, sticker et oiseau retirés par inpainting. Sert de référence de composition. |
| `renders/final_1080x1920.png` | **V2 finale, format story plein** : meilleure image de départ pour Higgsfield. |
| `renders/final_540x960.png` | Le même rendu en 540×960 (version déjà vue et envoyée). |
| `renders/variantes_eclairage/` | 3 lumières testées (k, l, m) + comparatif côte à côte. |
| `archive/v1_pixel-art-2D_REJETEE.mp4` | V1 rejetée. **Ne pas refaire ce style.** |
| `pipeline/` | Reconstruction 3D rejouable : calibration caméra, monde voxel, rendu Blender (section 6). |

## 3. Ce qu'est la V2

- Pose de la caméra et géométrie du pont calées sur la vidéo par photogrammétrie : points annotés + moindres carrés, erreur médiane ≈ 3 px.
  Le cadrage de la V2 correspond donc à celui de la vidéo.
- Monde voxel 530×400×60 blocs (≈ 1 bloc = 1 m) : lit de la Loire, grèves, pile en pierre, pylônes roses,
  tablier acier, câbles et suspentes, arbres, nuages cubiques.
- Textures 16×16 **faites maison** (générées, ce ne sont pas celles de Mojang). Rendu Cycles, tonemapping AgX, brume, eau réfractive.
- Paramètres exacts du final : `sun_az=62 sun_el=4.5 sun_str=18 sky_str=0.10 sun_col=1.0,0.78,0.56 expo=0.45`, 32 samples + débruitage OIDN.
  La variante « l » utilisait `sun_col=1.0,0.52,0.28` (plus orangé). Le final a gardé la couleur par défaut parce qu'une clé mal nommée
  avait été ignorée sans prévenir. `scene.py` affiche maintenant un avertissement pour toute clé inconnue.

Limites connues, à améliorer avec Higgsfield :
- Lumière de fin de journée sous ciel bleu, alors que la vidéo est filmée sous un ciel d'automne couvert : c'est un choix artistique, à garder ou à inverser.
- Premier plan d'herbe un peu plat et répétitif, avec quelques artefacts : de petits triangles à texture « côté d'herbe » plantés dans la pelouse.
- Grève du milieu en blocs épars assez bruités. Rive d'en face et arbres lointains peu lisibles.
- Tablier trop blanc (le vrai est gris acier) et treillis simplifié. Image fixe : aucune animation pour l'instant.

## 4. Connecter Higgsfield à Claude Code

Il faut un abonnement Higgsfield actif (pas de clé API). **Chaque génération consomme des crédits.**

```
npm i -g @higgsfield/cli
higgsfield auth login            # connexion dans le navigateur
npx skills add higgsfield-ai/skills
```

Autre option, le serveur MCP officiel : `claude mcp add --transport http higgsfield https://mcp.higgsfield.ai/mcp`, puis `/mcp` pour s'authentifier.
Modèles annoncés : vidéo Kling 3, Veo 3.1, Seedance 2.5, Sora 2, WAN 2.6 ; image Nano Banana Pro, Seedream 5.0, GPT Image 2, Flux 2.
Upscale, recadrage/outpainting. Vérifier ce qui est réellement disponible au moment de lancer.

## 5. Plan de reprise

**Piste A — image → vidéo (rapide, recommandée).** Entrée : `renders/final_1080x1920.png`. Format 9:16, durée ~10 s (celle de la musique ;
si le modèle plafonne à 5 ou 8 s, boucler ou enchaîner deux plans). Mouvement lent : un léger travelling avant est le plus stable.
Faire 2 ou 3 variantes selon les modèles et garder celle où les blocs ne « fondent » pas. Couper l'audio généré (Veo en produit) : la musique vient de Snap.

**Piste B — restyle de la vraie image (plus fidèle).** Modèle d'édition multi-références (Nano Banana Pro / Seedream 5.0 / GPT Image 2).
Image 1 = `source/photo_ref_720x1280.png` pour la composition, image 2 = `renders/final_1080x1920.png` pour le style voxel.
Sortie en 1080×1920, puis passer le résultat en piste A.

**Piste C — mouvement maîtrisé.** Rendre une frame de début et une frame de fin avec le pipeline (section 6), puis générer
la vidéo « start/end frame » (Kling / Veo 3.1). Utile si les pistes A et B inventent de la géométrie.

**Finition.** Sortie en 1080×1920, H.264, ≤ 60 s. Remettre la musique dans Snap au moment de poster, ou reprendre l'audio d'origine :

```
ffmpeg -i video_higgsfield.mp4 -i source/pont-cosne_original.mov -map 0:v -map 1:a -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest story_finale.mp4
```

Contraintes : garder uniquement le **style** voxel. Pas de personnages ni de créatures Minecraft (Steve, Creeper…), pas de logo, pas de texte incrusté.

### Prompts (en anglais, meilleurs résultats)

**A — image → vidéo**
```
Minecraft-style voxel world with a cinematic shader look. Slow, smooth dolly-in toward a blocky
suspension bridge: salmon-pink concrete portal tower, steel truss deck, thin steel cables with
vertical hangers, a massive stone-block pier standing in a calm, shallow river. Square voxel clouds
drift slowly across the sky, a light breeze sways the blocky tall grass, soft ripples and glints on
the water. Warm, low golden-hour sunlight with long shadows. Everything stays perfectly blocky with
crisp 16x16 pixel textures and stable geometry. Vertical 9:16.
```
Négatif : `characters, people, animals, mobs, text, logo, watermark, morphing, melting blocks, warping bridge, camera shake, flicker`

**B — restyle (image 1 = photo, image 2 = style)**
```
Rebuild image 1 as a Minecraft-style voxel scene with shaders, keeping its exact framing, camera
angle and composition. Suspension bridge with a salmon-pink concrete portal tower, grey steel truss
deck with X-lattice girders, steel cables with vertical hangers and a large stone-block pier; shallow
river with gravel banks and green grass tufts; autumn trees on the far bank; grassy foreground with a
dirt path at the bottom. Everything made of cubes with crisp 16x16 pixel textures and voxel clouds.
Match the block style and lighting of image 2. No characters, no text. Vertical 9:16, 1080x1920.
```
Variante fidèle à la vidéo : remplacer la lumière par `overcast autumn sky, soft diffuse light`.

## 6. Pipeline 3D (optionnel : re-rendre, nouvelles frames)

Python **3.11** obligatoire (bpy). Sous Windows, depuis la racine du dossier. Les commandes fonctionnent dans PowerShell et dans Git Bash (slashes `/`).

```
py -3.11 -m venv .venv          # ou : uv venv -p 3.11 .venv
.venv/Scripts/python -m pip install -r pipeline/requirements.txt
.venv/Scripts/python pipeline/mc/scene.py renders/test.png 540 32 sun_az=62 sun_el=4.5 sun_str=18 sky_str=0.10 "sun_col=1.0,0.78,0.56" expo=0.45
```

- Usage : `scene.py SORTIE.png LARGEUR SAMPLES [clé=valeur…]`. La hauteur vaut LARGEUR×16/9. La liste des clés est en tête de `scene.py`.
  Mettre entre guillemets les valeurs qui contiennent des virgules.
- Temps de rendu (CPU 2 cœurs) : ~1,5 min en 540×960, ~6 min en 1080×1920. Le script rend sur CPU. Pour passer sur GPU (OptiX/CUDA), il faut modifier `scene.py`.
- Caméra : `cam_fwd`, `cam_right` et `cam_up` en mètres (relatifs à la vue), `cam_yaw` et `cam_pitch` en degrés, plus `zoom`.
  Le soleil reste fixe dans le monde, donc les frames de début et de fin restent cohérentes. Exemple de frame de fin pour la piste C :
  `... scene.py renders/end.png 1080 32 <mêmes params lumière> cam_fwd=12 cam_up=3 cam_pitch=4`
- Régénérer le monde après avoir modifié `world.py` : `textures.py` → `world.py` → `mesher.py` (tous dans `pipeline\mc\`). Ils produisent `world.npz`.
- Calibration : `pipeline\geo\fit.py` et `fit_roll.py` produisent `fitP_rollfree.npy`, que lit `scene.py`.
