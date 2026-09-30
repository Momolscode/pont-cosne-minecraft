# POV Minecraft dans le monde réel : brief de reprise

À lire en entier avant d'agir. **`HANDOFF.md`, à la racine, concerne un autre projet (le pont de Cosne) : l'ignorer pour cette tâche et ne pas reprendre ses prompts.**

Ce brief sert à une session qui a accès à Higgsfield et aux vidéos de l'utilisateur. Les faits sur Higgsfield viennent de [RECHERCHE_HIGGSFIELD.md](RECHERCHE_HIGGSFIELD.md) (état au 30/09/2026, sources et niveaux de confiance). **Aucun prompt n'a été testé, aucune génération n'a été lancée.** Les commandes ffmpeg marquées « testée » l'ont été sur des vidéos de synthèse avec ffmpeg 7.0.2 ; les autres sont à essayer d'abord sur un court extrait.

## 0. Démarrage rapide (message à coller dans la nouvelle session)

```
Clone Momolscode/pont-cosne-minecraft, branche pov-minecraft, et lis pov-minecraft/BRIEF.md en entier
(ignore HANDOFF.md, qui concerne le pont). Si la branche ou le brief est introuvable, arrête-toi et dis-le-moi.
Récupère mes 2 vidéos (§ 4, étape 0), remplis la fiche d'observation, découpe et prépare les images de référence.
Montre-moi les planches, la fiche, les références, l'outil choisi pour chaque vidéo et le coût affiché.
Ne lance aucune génération payante avant mon « ok ». Ensuite : 1 essai par vidéo sur le segment le plus court,
puis les résultats avant toute autre dépense.
```

## 1. L'idée

Deux stories Snapchat verticales (9:16), filmées en POV au téléphone. Effet recherché : **« Minecraft dans la vraie vie »**. Le monde reste réel ; seuls les objets et les effets deviennent ceux du jeu, et l'interface du jeu s'affiche par-dessus. L'utilisateur veut un rendu **le plus réaliste possible** et **les éléments du jeu** : pioche, barre d'objets, cœurs, faim, expérience, viseur, particules, ramassage d'objet.

D'après l'utilisateur (à vérifier sur les vidéos) :

| Vidéo | Ce qui est filmé | Ce qu'on veut voir |
|---|---|---|
| **1 : la pioche** | L'utilisateur tient une bouteille de Coca et fait le geste de piocher avec. Il ramasse ensuite un caillou. | La bouteille devient **la pioche du jeu** (pioche en diamant par défaut), tenue dans la vraie main et qui suit exactement les coups, avec des particules de blocs à chaque impact. Le caillou ramassé « entre dans l'inventaire ». |
| **2 : les cailloux dans l'eau** | L'utilisateur jette des cailloux dans l'eau (jets simples ou ricochets : à constater). | Les cailloux deviennent des petits blocs de pierre texturés, l'eau reste réelle, avec des gouttes carrées ajoutées aux impacts. La barre d'objets montre la pile de cailloux qui diminue à chaque lancer. |

Les vidéos sont dans le dossier Google Drive **« higgfield »** de l'utilisateur. Le Drive branché à la session du 30/09 était un autre compte et ne les voyait pas.

**Question à poser au premier point d'étape :** la bouteille doit-elle être remplacée dès la première image, ou l'utilisateur veut-il voir la bascule (environ 1 s de vraie bouteille, puis changement de case active dans la barre et pioche en main) ? Dans le second cas, seule la partie après la bascule passe par Higgsfield, et l'étiquette reste visible au début (à flouter s'il préfère).

## 2. Prérequis

### 2.1 À faire par l'utilisateur avant d'ouvrir la session

- Ajouter le **connecteur Higgsfield** sur claude.ai (Settings → Connectors → connecteur personnalisé `https://mcp.higgsfield.ai/mcp`). Il se connecte lui-même par OAuth. Les connecteurs sont chargés au démarrage de la session.
- **Rendre les rushes accessibles** : brancher le connecteur Google Drive sur le compte qui possède le dossier « higgfield », ou partager ce dossier avec le compte déjà branché. Jamais en « tous les utilisateurs disposant du lien ».
- Vérifier son **plan et ses crédits Higgsfield**. Seedance 2.5 n'est pas inclus dans les plans Starter et Basic.

### 2.2 Outils dans la session

- **ffmpeg** : `ffmpeg -version`. À défaut, `pip install imageio-ffmpeg`, puis utiliser le binaire donné par `python -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'`. Ce paquet ne fournit ni ffprobe (lire les infos avec `ffmpeg -hide_banner -i fichier`) ni, en 7.0.2, le filtre drawtext.
- **Pillow** (Python), pour les références et les calques du HUD.
- **Accès Higgsfield**, dans cet ordre de préférence :
  1. **Connecteur MCP** (recommandé) : se fier aux descriptions des outils du connecteur réellement branché. Les noms relevés dans la recherche (`models_explore`, `media_upload` puis `media_confirm`, `generate_video`, `job_status`, `balance`) viennent d'une règle Cursor de mai 2026, retirée depuis, et d'une copie tierce (Composio).
  2. **CLI officielle** `npm i -g @higgsfield/cli@1.1.26` (la version inspectée), seulement si Claude Code tourne sur l'ordinateur de l'utilisateur : `higgsfield auth login` ouvre le navigateur. Pour couper la télémétrie Sentry : `HIGGSFIELD_DISABLE_TELEMETRY=1` (effet non vérifié).
  3. **Session cloud sans connecteur** : voir § 9 (dépannage non testé).
- **Réseau d'une session cloud** : le 30/09 à 08:47 UTC, six hôtes Higgsfield répondaient dans l'environnement de la session précédente (`higgsfield.ai`, `clerk.`, `fnf.`, `api.`, `fnf-api-gw.`, `mcp.`). Le joker `*.higgsfield.ai` n'a pas été vérifié. Les domaines du stockage d'upload et du CDN des résultats sont inconnus (S3 ou CloudFront selon un tiers). En cas d'échec, lire l'hôte refusé dans l'erreur (ou `$HTTPS_PROXY/__agentproxy/status`) et le donner à l'utilisateur pour qu'il l'autorise.

## 3. Règles de conduite

1. **Aucune dépense sans accord explicite.**
   - Au début, lire le solde et le plan (`balance` via le MCP, ou `higgsfield account status`), puis fixer avec l'utilisateur un plafond de crédits pour la session.
   - Avant **chaque** génération payante (vidéo, image de référence, retouche, nouvelle tentative, passe enchaînée, changement d'outil), afficher l'outil, la durée, la résolution, le coût lu et le solde, puis attendre un oui pour ce lancement précis.
   - Coût : `higgsfield generate cost …` en CLI. Via le MCP, aucun outil d'estimation n'est documenté : lire le bouton Generate de l'interface web pour les mêmes réglages. Si le coût n'est pas lisible, le dire et demander. Ne jamais annoncer un coût non lu. Après chaque job, relire le solde et annoncer le coût réel et le total dépensé ; s'arrêter au plafond.
   - Un seul job à la fois, jamais de lot.
   - Premier essai à la plus basse résolution proposée, sauf si l'utilisateur choisit 720p.
   - Repères (blogs Higgsfield, septembre 2026, environ 0,05 $ le crédit selon le plan) : Genjutsu 15 s = 40 crédits en 480p, 104 en 720p, 144 en 1080p. Kling Edit : coût introuvable.
2. **Propriété intellectuelle.**
   - Ne jamais utiliser `reveal_generation`, ni cocher « I own the rights » pour des éléments Minecraft ou Coca-Cola : l'utilisateur n'en détient pas les droits.
   - Si l'étiquette Coca est lisible, la flouter ou demander de refilmer **avant** le premier envoi.
   - Si un job est bloqué pour propriété intellectuelle, s'arrêter et prévenir l'utilisateur. Ne pas reformuler le prompt pour échapper à la détection, et ne pas changer d'outil dans le seul but de passer le filtre.
   - Les prompts décrivent le style au lieu de nommer le jeu, comme le conseille Higgsfield.
3. **Pas de HUD ni de texte générés par l'IA.** Les modèles déforment les interfaces et le texte. Le HUD et les compteurs se font au montage (§ 6).
4. **Un seul changement par génération**, puis enchaîner les passes, chacune soumise à la règle 1.
5. **Le dépôt pont-cosne-minecraft doit rester privé, et il ne reçoit jamais de vidéos.** Ne jamais y ajouter, commiter ni pousser de rushes, de segments, de planches, de sorties Higgsfield ou de montages. Travailler dans le scratchpad de la session ou dans un dossier hors du dépôt. Seuls les scripts et les calques maison (`refs/`, `tools/`) vont dans le dépôt. Ne jamais écraser les rushes d'origine : travailler sur des copies nommées.
6. **Ne rien publier ni partager** : ni `tiktok_publish`, ni lien public Higgsfield, ni envoi sur un réseau. La session remet les fichiers ; l'utilisateur poste lui-même.
7. **Aucun secret** : jamais de mot de passe, de jeton ni de clé API dans un fichier ou dans le chat. Ne jamais demander la sortie de `higgsfield auth token` ni le contenu de `~/.config/higgsfield/`. Seule exception encadrée : le § 9.
8. **Honnêteté** : ne dire qu'une génération a réussi qu'après l'avoir regardée image par image.

## 4. Préparation des rushes

### Étape 0 : récupérer les rushes

1. Drive : `search_files` avec `title contains 'higg'` (tolère la faute de frappe) et le type dossier, puis `parentId = '<id du dossier>'`. Noter le nom, le type MIME et la taille de chaque fichier.
2. `download_file_content` renvoie le fichier en base64 dans la conversation : ne l'essayer que pour un fichier de quelques Mo.
3. Sinon, ne pas insister : demander à l'utilisateur de déposer les vidéos directement dans le chat. Ne rien lancer tant que les deux fichiers ne sont pas lisibles par ffmpeg.

### Étape 1 : infos techniques et planches

```bash
# Durée, résolution, fps, rotation (ffprobe si présent)
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate:stream_side_data=rotation -of json rush1.mp4
# Sans ffprobe : la durée, la résolution, le fps et la ligne « displaymatrix » s'affichent ici
ffmpeg -hide_banner -i rush1.mp4

# Planches : 1 vignette toutes les 0,5 s, 12 s par planche, toutes les planches (testée)
ffmpeg -i rush1.mp4 -vf 'fps=2,scale=240:-2,tile=6x4' planche1_%02d.png
# La vignette k (1 à 24) de la planche n correspond à (n-1)*12 + (k-1)*0,5 s

# Autour d'un impact repéré à T secondes : toutes les images au fps natif
ffmpeg -ss <T-0.5> -i rush1.mp4 -t 1 -vf 'scale=360:-2,tile=6x5' impact_<T>.png
```

### Étape 2 : fiche d'observation

À remplir sur les planches et à **montrer à l'utilisateur avant tout prompt**. Les prompts du § 5 contiennent ces champs entre crochets : les remplacer par ce qui est observé, jamais par des suppositions.

- **[HAND]** main qui tient la bouteille ; **[GRIP]** prise (goulot ou corps) ; **[HEAD_END]** extrémité qui frappe (elle deviendra la tête de la pioche).
- **[BOTTLE]** verre ou plastique, couleur, secondes où l'étiquette est lisible.
- **[SURFACE]** ce qui est frappé (terre, herbe, pierre, rien).
- Impacts : timecodes à l'image près.
- Ramassage : main utilisée, sort de la bouteille pendant ce temps, image où la main se ferme.
- Vidéo 2 : nombre de lancers, jets simples ou ricochets (et nombre de rebonds), cailloux visibles en main avant le lancer, timecodes du lâcher et de chaque contact avec l'eau.
- Technique : durée, résolution, fps, rotation, incrustations Snapchat gravées (date, autocollants, texte, filtre).

### Étape 3 : préparer les segments

- **Incrustations Snapchat gravées** : demander à l'utilisateur l'export sans incrustations, ou recadrer. Noter leur place pour ne pas y mettre le HUD.
- **fps inférieur à 24** (les rushes Snap de l'utilisateur étaient à 15 i/s pour le pont) : des copies tierces de la doc Kling indiquent une entrée de 24 à 60 i/s. Préparer la copie à envoyer par duplication d'images, pas par interpolation (testée sur une source à 15 i/s) :
  ```bash
  ffmpeg -ss <début> -i rush1.mp4 -t <durée> -vf fps=30 -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac seg1a.mp4
  ```
- **Découper selon l'outil** :
  - Genjutsu (4 à 30 s) et Seedance Edit (jusqu'à 30 s) : toute la séquence de gestes en une seule passe si elle tient en 30 s, pour que la pioche garde le même aspect.
  - Kling Edit et Gemini Omni Flash (10 s au plus) : segments de 4 à 10 s qui se chevauchent d'environ 0,5 s, coupés sur une image d'impact (le mouvement cache le raccord), avec les mêmes références et le même prompt.
  - Premier essai payant : le segment le plus court qui contient un coup net.
- **Ramassage** : si la bouteille est posée pendant le ramassage, décider avec l'utilisateur. Soit la pioche reste visible au sol (remplacement sur toute la durée), soit une coupe au montage avec changement de case active dans la barre : dans le jeu, l'objet tenu descend hors champ et le suivant remonte.

## 5. Générations Higgsfield

### 5.0 Contrôles sans crédit, avant toute génération

1. **Voie d'accès** : si les outils du connecteur Higgsfield sont listés, utiliser le MCP ; sinon `higgsfield account status` ; sinon § 9.
2. **Solde et plan** (`balance` ou `account status`). Si Seedance 2.5 n'est pas dans le plan, la vidéo 2 part sur Kling.
3. **Pour chaque outil** (Genjutsu Object Swap, Kling 3.0 Omni Edit, Gemini Omni Flash, Seedance 2.5 Edit), relever avec `models_explore` ou `higgsfield model get <id> --json` : l'identifiant, les rôles des médias, les étiquettes à utiliser dans le prompt, les durées, les résolutions et les formats acceptés (9:16 non confirmé pour Genjutsu). Ne jamais inventer un identifiant. `hf_mult_replace_object` (Object Swap) vient d'un tiers ; aucun identifiant CLI n'a été trouvé pour Kling Omni Edit ni pour Gemini Omni Flash.
4. **Envoi d'un clip de test d'une seconde**, sans génération. Si l'envoi échoue au proxy, donner l'hôte à autoriser à l'utilisateur et ne rien lancer.
5. **Mode web** : si un outil n'est exposé ni par le MCP ni par la CLI, préparer un paquet (segments, références, prompts dans un .txt, réglages, coût attendu) et le remettre à l'utilisateur. Il lance sur higgsfield.ai (par exemple https://higgsfield.ai/ai-video-editor) et renvoie les résultats par le même canal que les rushes. La session reprend au § 5.4.

**Étiquettes dans les prompts** : `@Video1`/`@Image1` (Kling), `Video 1`/`Image 1` (Genjutsu, Seedance) et `<<<video_1>>>` (démo Gemini) viennent de guides et de démos. Les remplacer par celles que montre l'interface ou le schéma de l'outil. Donner les références avant le prompt. Si l'outil n'accepte pas d'étiquettes, décrire les médias (« the source video », « the reference image »).

### 5.1 Références, fabriquées en local et sans crédit

Dans le jeu, l'outil tenu est **un sprite 16×16 extrudé très mince**, pas un modèle voxel épais. La tête de la pioche est **un arc en escalier dont les deux pointes reviennent vers le manche**, pas un T à angle droit. Et « diamond » pousse les modèles vers de vrais cristaux facettés : il faut l'interdire. Cette description, notée `<BLOC PIOCHE>`, est réutilisée partout :

```text
a pixel-art pickaxe shaped like a 16x16 pixel sprite made into a thin solid object, about one pixel thick: a straight handle of square brown wood-coloured pixels in two tones with a dark brown outline, topped by an arched, stair-stepped pick head of opaque light-cyan and turquoise square pixels with a dark teal outline, the two tips of the head curving back toward the handle; every edge is a hard square pixel step, flat matte colours, no bevels, no rounded edges, no gemstone facets, no transparency, no glow
```

Références à fabriquer :
1. **Pioche de face** : script Pillow, pioche 16×16 dessinée par nous. La grille de pixels est écrite à la main et les teintes sont choisies par nous, sans copier le sprite du jeu ni ses textures, qui appartiennent à Mojang. Agrandir ×64 au plus proche voisin, sur un fond gris neutre uni : `refs/pioche_face_1024.png`.
2. **Vue 3/4** du même sprite extrudé d'un pixel d'épaisseur (Pillow ou Blender).
3. **Pioche en main** : coller la pioche à la place de la bouteille sur une image nette du segment (Pillow). Sinon, avec un modèle d'édition d'image Higgsfield, **payant, règle 1** :
   ```text
   Edit Image 1, a frame from a phone video: replace the soda bottle in the [HAND] hand with the pickaxe from Image 2, gripped by its handle exactly where the bottle is gripped, pick head at [HEAD_END], same scale, same daylight, same motion blur, focus and grain as the photo. The hand, fingers and background stay identical. No text, no logos, no interface.
   ```
4. **Cube de caillou** : cube texturé avec des tuiles pierre maison (on peut s'inspirer des tuiles `stone`, `gravel` et `mossy_stone` de `pipeline/mc/atlas.png`, dessinées pour le projet du pont).

Format : au moins 1024 px de côté et moins de 10 Mo. Kling accepte au plus 4 images : face et en main. **Faire valider les références par l'utilisateur avant la première vidéo.** Le même sprite sert d'icône dans la barre d'objets.

### 5.2 Vidéo 1 : bouteille → pioche

Ordre d'essai : **A. Genjutsu Object Swap**, puis **B. Kling 3.0 Omni Edit** (ou Kling O1 Video Edit), puis **C. Gemini Omni Flash**. Higgsfield reconnaît que le remplacement marche mal quand la forme change beaucoup (un cylindre qui devient une forme en T) : l'orientation de la tête est donc précisée dans chaque prompt.

**V1-A : Genjutsu Object Swap** (Video 1 = segment, Image 1 = pioche de face, Image 2 = pioche en main)
```text
Replace the [BOTTLE] held in the [HAND] hand in Video 1 with the pickaxe shown in Image 1 and Image 2. The fingers grip the pickaxe handle exactly where they grip the bottle; the pick head sits at [HEAD_END] and leads every swing. Pickaxe: <BLOC PIOCHE>, about the length of the bottle. It is a real physical object filmed by the same phone: same daylight and light direction, matching shadows on the fingers, same motion blur on fast swings, same focus, grain and compression. Keep the rest of the shot the same: real hand with five fingers, arm, [SURFACE], background, light, camera shake and the timing of every swing. No trace of the bottle, its label or its logo in any frame. No text, no interface, no logos.
```

**V1-B : Kling 3.0 Omni Edit.** Grammaire officielle Kling : `Change [sujet] in [@Video] to [cible] from [@Image]`.
```text
Change the [BOTTLE] held in the [HAND] hand in @Video1 to the pixel-art pickaxe from @Image1, gripped by its handle exactly where the hand grips the bottle, with the pick head at [HEAD_END] leading every swing: <BLOC PIOCHE>. The pickaxe is a real physical object in the shot: same daylight and direction, matching shadows on the fingers, same motion blur, focus and grain as the footage. Keep the real hand with five fingers, the arm, the [SURFACE], the background, the lighting, the camera shake and the timing of every swing unchanged; only the held object changes. No trace of the bottle, its label or its logo in any frame. No text, no interface, no morphing, no rounded pixels, no duplicated tools, no extra fingers.
```

**V1-C : Gemini Omni Flash**
```text
V2V on <<<video_1>>>. Keep the performance, hand motion, timing and camera move exactly as in the source. Change only the [BOTTLE] in the [HAND] hand into <BLOC PIOCHE>, gripped by its handle where the bottle is gripped, pick head leading each swing, lit and motion-blurred like the rest of the footage. No trace of the bottle or its label in any frame. Real photorealistic hand, five fingers. No text, no interface, no HUD.
```

**V1-P : particules**, passe facultative, seulement sur une pioche validée (Kling). Sinon, les particules se font au montage (§ 6).
```text
Add to @Video1, only at the exact moments the pick head hits the [SURFACE], a short burst of about fifteen tiny flat square particles in the colours of the [SURFACE], popping up and falling back within half a second. Keep everything else in @Video1 unchanged, including the pickaxe, the hand and the timing. No text, no interface, no sparks, no glow, no smoke.
```

**V1-D : le caillou devient un bloc**, passe facultative, sur la sortie validée.
```text
Change the small stone that the [main du ramassage] hand picks up in @Video1 to a small solid cube of the same size, covered with grey cobblestone pixel texture (irregular light and dark grey stones with dark grey gaps), hard square edges, lit by the same daylight, lying on the ground and then gripped by the fingers exactly like the stone. Keep everything else in @Video1 unchanged, including the pickaxe and the hand. No text, no interface, no logos.
```

Variante : pour une pioche en pierre, remplacer la tête cyan par « a flat grey stone-coloured pick head with a dark grey outline ». Si la pioche fait jouet ou n'est pas reconnaissable, essayer ensuite « noticeably longer than the bottle », sur accord (règle 1).

### 5.3 Vidéo 2 : cailloux jetés dans l'eau

On ne transforme **que les cailloux** : l'eau, les éclaboussures et les ondes restent réelles, c'est l'élément le plus difficile à garder réaliste. Les cailloux deviennent des cubes **dès la main**, pour éviter un saut visible au lâcher.

Ordre d'essai : **A. Seedance 2.5 Edit** (par prompt ou Draw to Edit), puis **B. Kling 3.0 Omni Edit**, puis **C. Gemini Omni Flash**.

**V2-A : Seedance 2.5 Edit** (Image 1 = cube de référence)
```text
Goal: the thrown stones become small pixel-textured cubes while the real world stays real. @Video 1 is the sole editing master; Image 1 shows the target cube. Modify only the stones: in the hand and in the air, every stone becomes a solid cube of the same size covered with grey cobblestone pixel texture, hard square edges, tumbling naturally, lit by the same daylight with the same motion blur. Keep the real hand, arm, water surface, splashes, ripples, shoreline, sky, lighting, camera motion and timing from @Video 1 unchanged and photorealistic. No text, no interface, no logos, no watermarks, no rounded or melted cubes.
```

**V2-B : Kling 3.0 Omni Edit**
```text
Change every stone held or thrown by the hand in @Video1 to a small solid cube of the same size from @Image1, covered with grey cobblestone pixel texture, hard square edges, same trajectory, same spin and same motion blur. Keep the real hand, arm, water, splashes, ripples, shoreline, sky, lighting, camera motion and timing unchanged and photorealistic. No text, no interface, no logos.
```

**V2-S : gouttes carrées**, passe facultative d'ajout, sans jamais remplacer l'eau (payante, règle 1). Les gouttes peuvent aussi se faire au montage.
```text
Add to @Video1, at each moment a cube touches the water[, including every skip], a small burst of tiny flat square droplets in light blue and white that pop up and fall back within half a second, on top of the real splash. Keep the real splash, the ripples and everything else in @Video1 unchanged and photorealistic. No text, no interface.
```

### 5.4 Contrôle de chaque sortie

Sur une planche d'images (`fps=4,scale=240:-2,tile=6x4`) et côte à côte avec la source, après mise à la même taille (`[0:v][1:v]hstack`) :
- la pioche est reconnaissable sur une image fixe à la taille d'un téléphone ;
- l'objet est stable du début à la fin : pas de retour à la bouteille, pas de logo visible ;
- la main a cinq doigts, sans fusion avec l'objet ;
- le mouvement et le timing sont ceux du rush ;
- les blocs restent carrés ;
- le format 9:16, la résolution et le fps sont ceux attendus (le fps de sortie diffère selon les modèles).

Envoyer la vidéo et la planche à l'utilisateur avec l'outil d'envoi de fichiers de la session. Si un essai échoue, **proposer** la suite avec son coût (nouvelle tentative, autre outil, référence refaite), sans la lancer.

## 6. Montage : éléments du jeu

Tout ce qui est interface, texte et compteur se fait **au montage**, avec des calques **générés par script (Pillow)**, sans fichiers, police, logo ni sons officiels du jeu.

**Proportions du HUD** (en pixels d'interface, agrandis ×5 au plus proche voisin sur un canevas transparent de 1080×1920) :
- barre d'objets de 182×22 : 9 cases au pas de 20, case active encadrée plus clair (la barre fait ainsi 910 px de large) ;
- 10 cœurs et 10 cuisses de faim de 9×9 au pas de 8, au-dessus de la barre ;
- barre d'expérience verte de 182×5 entre les deux ;
- viseur « + » au centre de l'écran.
- Chiffres : police bitmap maison 5×7, en blanc avec une ombre gris foncé décalée d'un pixel d'interface, en bas à droite de la case.
- Placer le tout dans la zone sûre des stories (au-dessus de la zone de réponse Snapchat, hors des incrustations) et **faire valider la position sur une image fixe avant le rendu**.

**Inventaire et ramassage (fidèle au jeu).** Le caillou disparaît dans la main. Son icône apparaît dans une case avec un petit rebond : échelle 1,2 puis 1 sur 3 à 4 images, avec un « pop » libre de droits. Le jeu n'affiche pas de compteur pour un objet unique. Proposer donc à l'utilisateur soit l'icône seule (fidèle), soit une pile déjà présente (par exemple 7 → 8) pour que le compteur bouge. Reprendre ce nombre au début de la vidéo 2, puis décompter à chaque lâcher ; l'icône disparaît au dernier caillou. Variante : l'icône vole jusqu'à la case.

**Particules** (si l'IA n'en a pas fait) : à chaque impact repéré à l'image près, 8 à 16 carrés d'un à deux pixels d'interface, couleurs prélevées sur la surface frappée, projetés vers le haut puis soumis à la gravité, pendant 0,3 à 0,6 s. En séquence de PNG RGBA numérotés, posés par `overlay` avec `enable`.

**Fissures** : retirées par défaut, car sans bloc à fissurer il faudrait suivre le sol réel. **Facultatif** : une barre d'usure verte sous l'icône de la pioche après le premier coup.

**Son** : garder le son d'origine, ou ajouter des bruitages 8-bit génériques libres de droits. Pas les sons officiels du jeu. L'utilisateur peut ajouter une musique dans Snapchat au moment de poster.

**Commandes** (testées ; X, Y et T sont à mesurer sur la vidéo réelle) :
```bash
# 1. Mettre la sortie IA au format final
ffmpeg -i edit1.mp4 -vf 'scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,setsar=1' -c:v libx264 -crf 16 -pix_fmt yuv420p -an edit1_1080.mp4
# 2. Poser le HUD dessiné en 1080x1920, sans le redimensionner
ffmpeg -i edit1_1080.mp4 -i hud_1080x1920.png -filter_complex '[0:v][1:v]overlay=0:0,format=yuv420p' -c:v libx264 -crf 16 hud1.mp4
# 3. Faire apparaître une icône ou un compteur à partir de T secondes
ffmpeg -i hud1.mp4 -i icone.png -filter_complex "[0:v][1:v]overlay=X:Y:enable='gte(t,T)'" -c:v libx264 -crf 16 -pix_fmt yuv420p final1.mp4
```
Toute mise à l'échelle d'un calque en pixel art se fait en `flags=neighbor`, par un facteur entier.

**Mention juridique.** Redessiner limite l'emprunt sans le supprimer : un HUD très fidèle reste un élément distinctif de la marque selon les règles de Mojang (https://www.minecraft.net/en-us/usage-guidelines). Pour une story personnelle non monétisée, le risque pratique est faible. Si « Minecraft » figure dans la légende, l'employer comme simple description, sans le logo. Ceci n'est pas un avis juridique.

## 7. Export

MP4 H.264, 1080×1920, `yuv420p`, `crf 18`, AAC. La durée maximale d'une story est à vérifier dans Snapchat. Les sorties en 720p (Gemini, Seedance) sont agrandies en local à l'étape 1 du § 6 (lanczos, gratuit), ou avec l'agrandissement Higgsfield (payant, règle 1).

**Remettre le son d'origine du même intervalle** que le segment (testée). La valeur de `-ss` est celle utilisée pour couper le segment :
```bash
ffmpeg -i final1.mp4 -ss <début_du_segment> -i rush1.mp4 -map 0:v -map 1:a -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest story1.mp4
```
Pour plusieurs segments mis bout à bout, remettre le son segment par segment avant la concaténation. Vérifier la synchronisation sur un impact.

## 8. Contenu de ce dossier

| Fichier | Rôle |
|---|---|
| `BRIEF.md` | Ce brief |
| `RECHERCHE_HIGGSFIELD.md` | Fiche de capacités Higgsfield, avec sources et niveaux de confiance |
| `refs/`, `tools/` | Pas encore livrés. Les fabriquer comme décrit en § 5.1 et § 6 |

## 9. Connexion Higgsfield depuis une session cloud sans connecteur (dépannage non testé)

À n'utiliser que si le connecteur MCP est impossible, et avec l'accord explicite de l'utilisateur.

1. Lancer `higgsfield auth login` **en arrière-plan**, en capturant sa sortie (la commande attend le retour). Si elle n'affiche qu'un chemin de fichier local (« If browser does not open, open this file… »), y lire l'adresse de connexion. Si aucune adresse n'apparaît, arrêter.
2. L'utilisateur vérifie que l'adresse commence par `https://clerk.higgsfield.ai/` avant de se connecter.
3. Son navigateur aboutit sur une page d'erreur `http://localhost:<port>/callback?code=…&state=…`. Il colle aussitôt cette adresse dans le chat : le code expire vite.
4. La session vérifie qu'elle commence par `http://localhost:` ou `http://127.0.0.1:`, puis la rejoue une seule fois dans le conteneur avec `curl --noproxy '*' -s "<adresse>"`. Elle ne la recopie ni dans ses messages, ni dans un fichier, ni dans un commit. Vérifier ensuite avec `higgsfield account status`.

En principe (OAuth 2.0 avec PKCE), ce code est de courte durée, à usage unique et inutilisable sans le `code_verifier` gardé par la CLI. **Ce n'est pas vérifié chez Higgsfield.** La connexion laisse dans le conteneur un jeton de rafraîchissement durable. Ne jamais lancer `higgsfield auth token`, ne jamais copier `~/.config/higgsfield/`, et lancer `higgsfield auth logout` en fin de travail. Cette commande supprime le jeton local ; la révocation côté serveur n'est pas vérifiée.
