# POV Minecraft dans le monde réel : brief de reprise

À lire en entier avant d'agir. Ce brief sert à une session qui a accès à Higgsfield et aux vidéos de l'utilisateur. Les faits sur Higgsfield viennent de [RECHERCHE_HIGGSFIELD.md](RECHERCHE_HIGGSFIELD.md) (état au 30/09/2026, sources citées). **Aucun prompt de ce brief n'a encore été testé.**

## 0. Démarrage rapide (message à coller dans la nouvelle session)

```
Clone Momolscode/pont-cosne-minecraft, passe sur la branche pov-minecraft et lis pov-minecraft/BRIEF.md.
Récupère mes 2 vidéos dans le dossier Google Drive « higgfield » (compte morgan.olsen969@gmail.com),
puis suis le brief : découpe, 1er essai par vidéo en 720p, montre-moi les résultats avant d'aller plus loin.
```

## 1. L'idée

Deux stories Snapchat verticales (9:16), filmées en POV au téléphone. On veut l'effet **« Minecraft dans la vraie vie »** : le monde reste réel, seuls les objets et les effets deviennent ceux du jeu, et l'interface du jeu est affichée par-dessus. L'utilisateur veut le rendu **le plus réaliste possible** et **les éléments du jeu** : pioche, barre d'objets, cœurs, faim, expérience, viseur, particules, ramassage d'objet.

| Vidéo | Ce qui est filmé | Ce qu'on veut voir |
|---|---|---|
| **1 : la pioche** | L'utilisateur tient une bouteille de Coca et fait le geste de piocher avec. Il ramasse ensuite un caillou. | La bouteille devient **une pioche Minecraft** (pioche en diamant par défaut) tenue dans la vraie main et qui suit exactement les coups. Des fissures et des particules de blocs apparaissent à chaque impact. Le caillou ramassé « entre dans l'inventaire » : il vole vers la barre d'objets et le compteur passe à 1. |
| **2 : les ricochets** | L'utilisateur jette des cailloux dans l'eau. | Les cailloux deviennent des petits blocs de pierre voxel et les impacts donnent des éclaboussures cubiques. La barre d'objets montre la pile de cailloux qui diminue à chaque lancer. |

Les vidéos sont dans le dossier Google Drive **« higgfield »** du compte **morgan.olsen969@gmail.com**. Le Drive branché à la session du 30/09 était un autre compte (lerepaire58@gmail.com) et ne les voyait pas.

## 2. Prérequis de la session

- **Accès Higgsfield**, par l'une de ces voies :
  - **Connecteur MCP** : claude.ai → Settings → Connectors → ajouter `https://mcp.higgsfield.ai/mcp`, puis ouvrir une nouvelle session. L'utilisateur se connecte lui-même par OAuth.
  - **CLI officielle** : `npm i -g @higgsfield/cli` puis `higgsfield auth login`. La connexion se fait dans le navigateur, avec un retour sur `localhost:8765`. C'est simple sur l'ordinateur de l'utilisateur.
  - **Session cloud** : la politique réseau doit autoriser `higgsfield.ai` et `*.higgsfield.ai`. C'est le cas depuis le 30/09 vers 08:45 UTC dans l'environnement actuel. Pour la connexion, voir § 9.
- **Abonnement Higgsfield actif avec des crédits.** Chaque génération est payante, même via le MCP ou la CLI. Seedance 2.5 n'est pas inclus dans les plans Starter et Basic.
- **ffmpeg** pour découper et monter les vidéos.
- **Jamais de secret dans un fichier ni dans le chat** : ni mot de passe, ni jeton, ni clé API. C'est l'utilisateur qui se connecte.

## 3. Règles de conduite

1. **Montrer les résultats avant de dépenser plus.** Faire un essai par vidéo en 720p, afficher le coût lu avant chaque lancement (`higgsfield generate cost …` ou le bouton Generate), puis attendre l'accord de l'utilisateur pour la suite. Ordre de grandeur (blog Higgsfield, septembre 2026) : 10 s de Genjutsu en 1080p coûtent environ 99 crédits, soit environ 5 $.
2. **Ne jamais contourner un filtre de propriété intellectuelle.** Pas de `reveal_generation`, et pas de case « I own the rights » cochée pour des éléments Minecraft ou Coca-Cola : l'utilisateur n'en détient pas les droits.
3. **Pas de HUD ni de texte générés par l'IA.** Les modèles déforment les interfaces et le texte. Le HUD et les compteurs se font au montage (§ 6).
4. **Un seul changement par génération**, puis enchaîner les passes.
5. **Ne pas écraser les rushes d'origine.** Travailler sur des copies nommées (`seg1a.mp4`, `edit1a_genjutsu.mp4`…).
6. **Rester honnête** : ne dire qu'une génération a réussi qu'après l'avoir regardée image par image.

## 4. Préparation des rushes

```bash
# Durée, résolution, fps et rotation réels
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate:stream_tags=rotate -of json rush1.mp4

# Planche d'images pour repérer les gestes (1 image toutes les 0,5 s)
ffmpeg -i rush1.mp4 -vf "fps=2,scale=240:-2,tile=6x4" -frames:v 1 planche1.png
```

- Repérer et noter les timecodes : prise de la bouteille, chaque coup de pioche (moment d'impact), ramassage du caillou (main qui se ferme), chaque lancer et chaque impact dans l'eau.
- Couper en **segments de 4 à 10 s** centrés sur les gestes. Cette plage est acceptée par tous les outils retenus : Genjutsu demande au moins 4 s, Kling Edit et Gemini Omni Flash acceptent au plus 10 s.
  ```bash
  ffmpeg -ss 2.0 -i rush1.mp4 -t 8 -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac seg1a.mp4
  ```
- Si l'étiquette Coca est bien visible et que la génération est bloquée pour propriété intellectuelle, le plus efficace est de **refilmer avec l'étiquette tournée ou retirée**.

## 5. Générations Higgsfield

### 5.1 Image de référence de la pioche

Genjutsu et Kling fonctionnent mieux avec une **image de référence** de l'objet cible. Elle doit être **un dessin original** de pioche voxel, pas une texture extraite du jeu : les filtres contrôlent aussi les références. Deux options :
- utiliser `pov-minecraft/refs/pioche_diamant_ref.png` si le dépôt la contient (rendu Blender maison, voir § 8) ;
- sinon, la générer avec un modèle d'image Higgsfield : « a chunky blocky voxel pickaxe, cyan diamond pick head, brown wooden handle, crisp 16x16 pixel-art texture extruded in 3D, isolated on plain white background, three-quarter view ».

**Méthode « image d'abord »** (recommandée par des guides tiers) : retoucher une image du rush pour y montrer la pioche en main, la valider avec l'utilisateur, puis la donner comme référence.

### 5.2 Vidéo 1 : bouteille → pioche

Ordre d'essai : **A. Genjutsu Object Swap**, puis **B. Kling 3.0 Omni Edit** (ou Kling O1 Video Edit), puis **C. Gemini Omni Flash**. Découvrir d'abord les modèles et leurs paramètres réels :

```bash
higgsfield model list --video --json
higgsfield model get hf_mult_replace_object --json   # Object Swap, identifiant rapporté par un tiers, à confirmer
higgsfield upload create ./seg1a.mp4
higgsfield generate cost <job_type> ...                 # toujours avant de lancer
```

Via le MCP : `models_explore`, puis `media_upload`/`media_confirm`, puis `generate_video` et `job_status`. Ne jamais inventer un identifiant de modèle.

**Prompt V1-A : Genjutsu Object Swap** (Video 1 = segment, Image 1 = pioche de référence)
```text
Replace the plastic soda bottle held in the right hand in Video 1 with the pickaxe in Image 1: a chunky blocky voxel pickaxe, cyan diamond pick head and brown wooden handle, crisp 16x16 pixel-art texture extruded in 3D, right-angle silhouette, about the same length as the bottle. Same grip, same position in the hand, same swing motion and timing. Keep the rest of the shot identical: real photorealistic hand with five fingers, arm, ground, background, lighting and camera shake unchanged. No labels, no logos, no text, no interface.
```

**Prompt V1-B : Kling 3.0 Omni Edit** (@Video1 = segment, @Image1 = pioche). Grammaire officielle Kling : `Change [sujet] in [@Video] to [cible] from [@Image]`.
```text
Change the plastic soda bottle held in the right hand in @Video1 to the blocky voxel pickaxe from @Image1: cyan diamond pick head, brown wooden handle, crisp 16x16 pixel-art texture extruded in 3D, right-angle silhouette, compact size close to the bottle, held in the same grip and following the same swing motion. Remove every label and logo from the bottle. Each time the pick hits the ground, a small burst of square pixel dust particles and blocky cracks. Keep the real human hand, five fingers, arm, lighting, ground, background, camera shake and timing unchanged and photorealistic; only the held object changes. No text, no interface, no logos, no morphing, no melted or rounded blocks, no extra fingers.
```

**Prompt V1-C : Gemini Omni Flash.** La syntaxe `<<<video_1>>>` vient d'une démo Higgsfield, à confirmer dans l'interface.
```text
V2V on <<<video_1>>>. Keep the performance, hand motion, timing and camera move exactly as in the source. Change only the plastic soda bottle in the hand into a chunky blocky voxel pickaxe with a cyan diamond head and a brown wooden handle, crisp pixel-art texture, same size and same grip. At each impact, square pixel dust particles. Remove all labels and logos. Real photorealistic hand, five fingers. No text, no interface, no HUD.
```

**Passe facultative V1-D : le caillou devient un bloc.** Seulement si la pioche est réussie : enchaîner sur la sortie de V1.
```text
Change the small stone picked up by the hand in @Video1 to a small blocky grey cobblestone voxel cube with crisp pixel texture, same size, following the hand exactly. Keep everything else unchanged and photorealistic. No text, no interface, no logos.
```

Variante de style : pour une pioche en pierre, remplacer « cyan diamond pick head » par « flat grey stone pick head ». Si un modèle bloque la génération, retirer d'abord toute mention de marque. Les prompts ci-dessus n'en contiennent volontairement aucune : ils décrivent le style au lieu de le nommer, comme le conseille Higgsfield.

### 5.3 Vidéo 2 : cailloux jetés dans l'eau

Ordre d'essai : **A. Seedance 2.5 Edit** (par prompt ou par Draw to Edit sur la zone d'impact), puis **B. Kling 3.0 Omni Edit**, puis **C. Gemini Omni Flash**.

**Prompt V2-A : Seedance 2.5 Edit**
```text
Goal: turn the thrown stones and their water impacts into a blocky voxel game look while the real world stays real. @Video 1 is the sole editing master. Modify only the stones and the splashes: each stone becomes a small grey cobblestone voxel cube with a crisp pixel texture while in the air; where it lands, a burst of square pixel water droplets and a flat blocky ripple. Keep the real hand, arm, water surface, shoreline, sky, lighting, camera motion and timing from @Video 1 unchanged and photorealistic. No text, no interface, no logos, no watermarks, no melted or rounded blocks.
```

**Prompt V2-B : Kling 3.0 Omni Edit.** Si le résultat dérive, faire les cailloux et les éclaboussures en deux passes séparées.
```text
Change the stones thrown by the hand in @Video1 to small blocky grey cobblestone voxel cubes with crisp pixel texture, and change the water splashes in @Video1 to bursts of square pixel water droplets with a flat blocky ripple. Keep the real hand, arm, water surface, shoreline, sky, lighting, camera motion and timing unchanged and photorealistic. No text, no interface, no logos.
```

### 5.4 Contrôle de chaque sortie

À vérifier avant de montrer à l'utilisateur, sur une planche d'images (`fps=4,tile`) :
- l'objet tenu est-il stable du début à la fin (pas de retour à la bouteille, pas de logo visible) ?
- la main a-t-elle cinq doigts, sans fusion avec l'objet ?
- le mouvement et le timing sont-ils ceux du rush ?
- les blocs restent-ils carrés ?
- le fps et la résolution sont-ils les attendus (le fps de sortie diffère selon les modèles) ?

Si un segment échoue deux fois, essayer l'outil suivant ou refaire l'image de référence.

## 6. Montage : éléments du jeu

Tout ce qui est interface et texte se fait **au montage**, sur la vidéo générée, avec des calques dessinés à la main dans le style du jeu, sans reprendre les fichiers officiels (règles d'usage Mojang : https://www.minecraft.net/en-us/usage-guidelines).

- **HUD fixe** en bas d'écran, dans la zone sûre des stories (au-dessus de la barre de réponse Snapchat) :
  - barre de 9 cases, la pioche dans la case active (vidéo 1) ou la pile de cailloux (vidéo 2) ;
  - 10 cœurs, 10 jambonneaux de faim, barre d'expérience verte ;
  - viseur « + » au centre.
- **Ramassage (vidéo 1)** : quand la main se referme sur le caillou, masquer le caillou ou couper, faire voler une icône de caillou jusqu'à une case sur 6 à 8 images avec un petit rebond, puis afficher le compteur « 1 ».
- **Coups de pioche** : si l'IA n'en a pas mis assez, ajouter des fissures et une gerbe de particules carrées à chaque impact.
- **Ricochets (vidéo 2)** : le compteur de la pile de cailloux diminue à chaque lancer (par exemple 5, 4, 3…).
- **Son** : garder le son d'origine, ou ajouter des bruitages 8-bit génériques libres de droits. Pas les sons officiels du jeu. La musique peut être ajoutée dans Snapchat au moment de poster.

Commandes de base (les coordonnées et les temps sont à mesurer sur la vidéo réelle) :

```bash
ffmpeg -i edit1.mp4 -i hud_1080x1920.png -filter_complex "[1:v]scale=iw*main_w/1080:-1[h];[0:v][h]overlay=0:0" -c:a copy hud1.mp4
ffmpeg -i hud1.mp4 -i compteur_1.png -filter_complex "[0:v][1:v]overlay=X:Y:enable='gte(t,3.2)'" -c:a copy final1.mp4
```

## 7. Export

MP4 H.264, 1080×1920, `-pix_fmt yuv420p`, `-crf 18`, AAC, 60 s maximum par story. Remettre le son d'origine si l'outil l'a remplacé :

```bash
ffmpeg -i final1.mp4 -i rush1.mp4 -map 0:v -map 1:a -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -shortest story1.mp4
```

## 8. Contenu de ce dossier

| Fichier | Rôle |
|---|---|
| `BRIEF.md` | Ce brief |
| `RECHERCHE_HIGGSFIELD.md` | Fiche de capacités Higgsfield vérifiées, avec sources et niveaux de confiance |
| `refs/` | À venir : image de référence de la pioche, calques du HUD et icônes, dessinés maison |
| `tools/` | À venir : script de montage (HUD, ramassage, compteurs) |

Tant que `refs/` et `tools/` ne sont pas présents, suivre les solutions de repli décrites en § 5.1 et § 6.

## 9. Connexion Higgsfield depuis une session cloud

La CLI renvoie le navigateur vers `http://localhost:8765/…`, qui désigne l'ordinateur de l'utilisateur et non le conteneur. Deux solutions :
1. **Recommandée** : ajouter le connecteur MCP Higgsfield sur claude.ai et ouvrir une nouvelle session. L'OAuth est géré par claude.ai.
2. **Dépannage** : lancer `higgsfield auth login` dans le conteneur. L'utilisateur ouvre le lien affiché et se connecte. Son navigateur aboutit sur une page d'erreur `localhost:8765/…?code=…`. Il copie **l'adresse de cette page** dans le chat, et la session la rejoue dans le conteneur avec `curl "<adresse>"`. Ce code est à usage unique et inutilisable sans la clé PKCE gardée par la CLI. Ce n'est ni un mot de passe ni un jeton durable, mais il ne doit jamais être écrit dans un fichier.

Les identifiants de la CLI sont ensuite dans `~/.config/higgsfield/` : ne jamais les copier ni les commiter.
