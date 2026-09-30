# Fiche de capacités vérifiées : Higgsfield pour deux vidéos POV « jeu voxel dans le monde réel »

État au 30/09/2026. Cette fiche croise trois recherches. Rien n'a été généré, aucun compte Higgsfield n'a été connecté et aucun prompt n'a été testé.

**Légende des niveaux de confiance**
- **[OFFICIEL]** : page Higgsfield, Google, Kling ou Mojang, ou binaire officiel inspecté.
- **[TIERS]** : site non officiel (revendeur d'API, guide, test indépendant).
- **[INCERTAIN]** : les sources se contredisent, ou l'information n'a pas été trouvée.
- **[ANALYSE]** : recommandation de travail, pas un fait sourcé.

**Accès aux sources.** WebFetch était bloqué vers higgsfield.ai et minecraft.net (EGRESS_BLOCKED). Ces pages ont été lues via le crawler Exa, donc leur contenu peut venir d'un cache. open.higgsfield.ai/explore demande une connexion. Un contrôle curl a été fait depuis le conteneur le 30/09/2026 à 08:47 UTC :

| Hôte | Réponse |
|---|---|
| higgsfield.ai | 200 |
| clerk.higgsfield.ai | 200 |
| fnf.higgsfield.ai | 401 |
| api.higgsfield.ai | 405 |
| fnf-api-gw.higgsfield.ai, mcp.higgsfield.ai, fnf-device-auth.higgsfield.ai | 404 à la racine |

Ces codes viennent des serveurs Higgsfield eux-mêmes, donc le proxy laisse passer. Entre 08:14 et 08:35 UTC, le proxy refusait encore ces hôtes (403).

---

## 0. En bref

1. **Vidéo 1** (bouteille → pioche) : Genjutsu Object Swap en premier choix, puis Kling 3.0 Omni Edit, puis Gemini Omni Flash.
2. **Vidéo 2** (cailloux dans l'eau) : Seedance 2.5 Edit (par prompt ou Draw to Edit), puis Kling 3.0 Omni Edit, puis Gemini Omni Flash.
3. **Post-production** : le HUD, le compteur d'inventaire, le « +1 » et tout le texte se font au montage, pas par l'IA.
4. **Découpage** : couper chaque rush en segments de **4 à 10 s** centrés sur le geste. C'est la seule plage acceptée par tous les outils retenus (Genjutsu demande au moins 4 s ; Kling et Gemini acceptent au plus 10 s).
5. **Propriété intellectuelle** : ne pas écrire « Minecraft » ni « Coca-Cola » dans les prompts. Ne reprendre ni les textures, ni la police, ni le logo, ni les sons officiels.
6. **Lancement** : il faut le compte et les crédits de l'utilisateur. Via la CLI ou le MCP, il n'y a ni accès illimité ni générations gratuites. C'est l'utilisateur qui se connecte ; aucun jeton n'est collé dans un fichier.

---

## 1. Options classées

### Vidéo 1 : bouteille tenue en main → pioche voxel, geste de piochage, ramassage d'un caillou

#### Option 1 : Higgsfield Genjutsu, Object Swap — [OFFICIEL], sauf mention contraire

- **Rôle.** Remplace un objet, un accessoire, une tenue ou un personnage désigné. La caméra, la lumière et le mouvement restent ceux du plan d'origine. L'outil marche sur des vidéos réelles. Le tableau officiel classe les accessoires (« props ») dans Object Swap.
  - https://higgsfield.ai/blog/higgsfield-genjutsu
  - https://higgsfield.ai/blog/edit-ai-video-without-regenerating
- **Entrée.**
  - Une vidéo de 4 à 30 s.
  - Jusqu'à 30 images de référence.
  - Prompt facultatif, ou l'un des 30 presets et plus : https://higgsfield.ai/higgsfield-genjutsu-presets
- **Sortie.**
  - Jusqu'en 1080p.
  - Format 9:16 : Higgsfield ne le confirme pas. layer.ai annonce 16:9 et 9:16 [TIERS].
  - FPS de sortie : non publié.
- **Coût** (tarif « vérifié en septembre 2026 », environ 0,05 $ le crédit) :

  | Durée | 480p | 720p | 1080p |
  |---|---|---|---|
  | 15 s | 40 crédits (~2,00 $) | 104 crédits (~5,20 $) | 144 crédits (~7,20 $) |
  | 10 s (autre billet) | — | — | 99 crédits (~4,95 $) |

- **Chiffres contradictoires chez les tiers** [TIERS] :
  - layer.ai : 8 références, 480p ou 720p, au moins 409 600 px par image (https://layer.ai/models/higgsfield-genjutsu-object-swap).
  - Axiabits : 3 à 30 s et 40 références (https://axiabits.com/how-to-use-higgsfield-genjutsu-for-motion-transfer/).
  - L'API développeur annonce 1 à 30 s [INCERTAIN].
- **Risques.**
  - Un test indépendant a échoué (balle de golf remplacée par un œuf) : l'objet d'origine est resté visible et le nouvel objet était mal placé. https://app.therundown.ai/guides/swap-the-product-and-keep-the-performance-with-higgsfield [TIERS]
  - Higgsfield reconnaît que le remplacement marche mal quand la taille ou la forme changent beaucoup, ce qui est le cas entre une bouteille cylindrique et une pioche en T [OFFICIEL].
- **Identifiants.**
  - API développeur : `higgsfield/genjutsu/object-swap/v1.0` [OFFICIEL, mais c'est un produit distinct].
  - MCP : `hf_mult_replace_object`, d'après la copie de Composio [TIERS].
  - CLI : aucun identifiant confirmé.

#### Option 2 : Kling 3.0 Omni Edit (ou Kling O1 Video Edit) — [OFFICIEL], sauf mention contraire

- **Rôle.** Édition d'une vidéo existante en langage naturel, présentée comme « Exclusive to Higgsfield » sur https://higgsfield.ai/ai-video-editor.
- **Grammaire officielle** pour un remplacement local : `Change [sujet] in [@Video] to [cible] from [@Image]`. https://app.klingai.com/global/quickstart/klingai-video-o1-user-guide
- **Entrée.**
  - Vidéo de 3 à 10 s.
  - Jusqu'à 4 images de référence quand une vidéo est fournie.
  - Guide Kling : 200 Mo au plus, 2K au plus ; images d'au moins 300 px et de 10 Mo au plus.
  - Sources : https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-kling et https://higgsfield.ai/blog/Kling-01-is-Here-A-Complete-Guide-to-Video-Model
- **Sortie.**
  - 1080p au maximum.
  - Selon des tiers : formats 9:16, 16:9 ou 1:1 ; durée égale à l'entrée ; 24 fps ; option pour garder le son d'origine (`keep_audio` ou `keep_original_sound`). Cette option n'a pas été vue dans l'interface Higgsfield. Sources : https://docs.unifically.com/models/video/kling/kling-3.0-omni-video-edit et https://doc.302.ai/424603175e0 [TIERS]
- **Coût en crédits Higgsfield : non trouvé.** Il faut lire le bouton Generate. L'API développeur affiche 0,063 $/s (−50 % sur un tarif de 0,126 $/s), mais ce prix ne se convertit pas en crédits web [INCERTAIN]. https://open.higgsfield.ai/models/kling-video/omni/video-edit/playground
- **Pas de champ `negative_prompt`** dans la référence d'API : https://open.higgsfield.ai/models/kling-video/omni/video-edit/api-reference

#### Option 3 : Gemini Omni Flash — [OFFICIEL], sauf mention contraire

- **Rôle.** Édition d'une vidéo réelle par instruction, avec des tours d'édition successifs. Une démo Higgsfield montre une main réelle ; le prompt y verrouille la performance et la caméra avec la syntaxe `V2V on <<<video_1>>>`.
  - https://higgsfield.ai/blog/Higgsfield-Omni-VFX
  - https://higgsfield.ai/blog/gemini-omni-flash-vfx-video-editing
  - https://higgsfield.ai/gemini-omni-flash
- **Sortie.**
  - 720p, 3 à 10 s, 24 fps.
  - Formats 16:9, 9:16, 1:1 et 4:5.
  - Images de début et de fin possibles.
  - Environ 1,50 $ par clip de 10 s : https://higgsfield.ai/blog/best-ways-to-access-gemini-omni-flash-2026
- **Durée d'entrée : contradictoire** [INCERTAIN].
  - Google : 10 s maximum (https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash).
  - Page Higgsfield : 30 s. FAQ Higgsfield : 60 s.
  - Par prudence, envoyer des segments de 10 s au plus.
- **Restriction.** L'édition de la voix sur des images de personnes réelles est limitée. A priori sans effet sur une vidéo POV.

#### Options de dernier recours ou à écarter pour la vidéo 1

- **Seedance 2.5 Edit** : techniquement possible (Draw to Edit sur la bouteille). Mais Seedance applique son propre filtre IP, que Higgsfield ne peut pas lever. Il est donc le plus exposé au logo Coca visible dans la source. Voir la vidéo 2.
- **MiniMax H3** : Higgsfield met en avant des HUD de jeu et une vue à la première personne cohérents d'une image à l'autre (https://higgsfield.ai/minimax/h3). Mais la durée d'entrée en mode édition n'est pas publiée, et un tiers affirme que l'édition n'existe que dans l'application [INCERTAIN].
- **Grok Imagine Edit** : listé sur https://higgsfield.ai/ai-video-editor. Selon des tiers : entrée tronquée à 8 s environ, sortie en 480p ou 720p. Non confirmé sur Higgsfield [TIERS].
- **Draw to Edit / `draw_to_video`** à partir d'une image retouchée : c'est un repli officiel (voir § 3.2).
- **Ne conviennent pas :**
  - Wan Animate et Recast : ils demandent un visage visible dès la première image.
  - Mixed Media : il restyle toute l'image (3 à 15 s).
  - Sora 2 et Veo 3.1 : l'édition d'une vidéo importée n'est pas confirmée.
  - Runway Aleph et Luma Modify : absents de Higgsfield.
- **Image → vidéo avec images de début et de fin** (Kling 3.0, Seedance 2.0, Veo 3.1…) : le mouvement réel de la main n'est pas conservé, il est réinventé.

#### Ramassage du caillou vers l'inventaire — [ANALYSE]

On garde le geste réel. Deux possibilités :
- (a) une deuxième passe IA avec un seul changement : le caillou devient un petit cube voxel ;
- (b) le caillou reste réel, et tout l'effet d'inventaire est fait en post-production.

Higgsfield reconnaît qu'il est difficile de créer un contact ou une occultation qui n'existent pas dans la source [OFFICIEL, https://higgsfield.ai/blog/edit-ai-video-without-regenerating]. La disparition du caillou dans la main se fait donc mieux au montage, par une coupe ou un masque.

### Vidéo 2 : jet de cailloux dans l'eau → cailloux voxel et éclaboussures façon jeu

#### Option 1 : Seedance 2.5 Edit — [OFFICIEL], sauf mention contraire

- **Rôle.** Modifie un clip existant, audio compris : par prompt, par zone (Region edit) ou par Draw to Edit (zone dessinée sur une image du clip). Marche sur des vidéos réelles.
  - https://higgsfield.ai/creator-hub/help-center/ai-models/how-do-i-use-seedance
  - https://higgsfield.ai/blog/edit-ai-video-without-regenerating
- **Entrée** : jusqu'à 30 s et jusqu'à 50 références.
- **Sortie** : même durée que la source. D'après la console API et un tiers, le format est fixé par la source, ce qui conserve le 9:16.
- **Résolution et coût : contradictoires** [INCERTAIN].
  - Centre d'aide : 480p à 720p.
  - Skill CLI officiel : `seedance_2_5` plafonne à 720p.
  - Blog : 10 s en 1080p = 90 crédits.
  - Selon un tiers, le coût dépend de la durée du clip source : https://aivideosensei.com/guides/seedance-2-5-editing-features
- **Plans** : Seedance 2.5 n'est pas inclus dans les plans Starter et Basic.
- **Filtre IP** propre à Seedance, que Higgsfield ne peut pas lever : https://higgsfield.ai/creator-hub/help-center/troubleshooting/my-generation-blocked-for-copyright-or-ip

#### Option 2 : Kling 3.0 Omni Edit

Mêmes limites qu'en vidéo 1 : 3 à 10 s, 1080p, coût à lire sur le bouton Generate. Formules à combiner : `Change the stones in [@Video] to …` et `Add … to [@Video]`. Kling accepte officiellement plusieurs tâches dans un même prompt.

#### Option 3 : Gemini Omni Flash

Mêmes limites qu'en vidéo 1 : 720p, segments de 10 s, environ 1,50 $ par clip de 10 s.

**Remarque [ANALYSE].** Genjutsu Object Swap pourrait remplacer les cailloux, mais rien de publié n'indique qu'il gère des objets petits, rapides et nombreux.

---

## 2. À faire en post-production plutôt qu'en IA

**Pourquoi.**
- T2VTextBench a évalué 10 modèles texte → vidéo : la plupart ne produisent pas de texte lisible et stable, et le meilleur score moyen n'est que de 0,37 sur 1 (https://arxiv.org/abs/2505.04946).
- Les guides de 2026 recommandent d'ajouter en post tout texte d'interface (https://aitoolsguidebook.com/en/articles/ai-video-text-overlay-garbled/).
- Un générateur « Minecraft » admet lui-même que sa barre d'objets est décorative et change d'une image à l'autre (https://www.kavel.ai/video/minecraft-parkour-video-generator) [TIERS].
- Seule exception revendiquée : MiniMax H3, non testé.

**Éléments à ajouter au montage** (CapCut, Premiere, After Effects, ou ffmpeg en local) :
- Barre d'objets de 9 cases, cœurs et viseur central, en calque PNG fixe. Le HUD est fixé à l'écran, donc aucun suivi de mouvement n'est nécessaire.
- La pioche affichée dans la case active.
- Le ramassage : quand la main se referme, masquer ou couper le caillou, faire voler une icône jusqu'à une case, puis incrémenter le compteur (« 1 », « 2 »…).
- Des particules carrées de cassage, si l'IA n'en produit pas assez.
- Des sons 8-bit génériques. Pas les sons officiels, y compris le « pop » de ramassage.
- Un flou sur tout reste de logo Coca.
- Tout le texte.

Demander donc à l'IA une vidéo propre : `no HUD, no text, no interface`.

**Contraintes de création** [OFFICIEL, https://www.minecraft.net/en-us/usage-guidelines] :
- Le HUD doit être dessiné par vous. Mojang range les noms, logos, polices et textures dans sa marque, et les graphismes, textures, modèles et sons dans ses « assets ».
- Partager publiquement, même gratuitement, compte comme un « commercial use » au sens de ces règles.
- Si le nom est cité, ajouter : « NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT. » « Minecraft » ne peut apparaître que comme titre secondaire.
- Ceci n'est pas un avis juridique.

**Commandes ffmpeg standard** (syntaxe ffmpeg classique, jamais exécutée sur les rushes ; les valeurs 2.0, 8, X, Y et 3.2 sont à mesurer) :

```bash
# Lire la durée, la résolution et le FPS réels du rush (inconnus à ce jour)
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height,r_frame_rate -of json rush1.mp4

# Extraire un segment de 8 s qui commence à 2,0 s
ffmpeg -ss 2.0 -i rush1.mp4 -t 8 -c:v libx264 -crf 18 -c:a aac seg1.mp4

# Incruster le HUD fixe. Le PNG doit avoir la résolution de la SORTIE IA (par ex. 720x1280 en 720p), pas celle du rush
ffmpeg -i edit1.mp4 -i hud.png -filter_complex "[0:v][1:v]overlay=0:0" -c:a copy hud1.mp4

# Faire apparaître l'icône du caillou dans la barre à partir de t = 3,2 s
ffmpeg -i hud1.mp4 -i icone_caillou.png -filter_complex "[0:v][1:v]overlay=X:Y:enable='gte(t,3.2)'" -c:a copy final1.mp4
```

Le FPS de sortie diffère selon l'outil (24 fps pour Gemini et Kling selon les sources, non publié pour Genjutsu et Seedance Edit). Monter sur une timeline à FPS unique.

---

## 3. Lancer concrètement

### 3.0 Prérequis communs à toutes les voies

- **Abonnement payant actif.** Via MCP, CLI, Canvas ou Supercomputer, tout est facturé au tarif standard : ni accès illimité, ni générations gratuites [OFFICIEL]. https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp
- **Aucun secret dans les fichiers ou le chat** : ni mot de passe, ni jeton, ni `credentials.json`, ni clé API (règle de AGENTS.md). C'est l'utilisateur qui se connecte.
- **Traiter les rushes dans le scratchpad de la session, pas dans le dépôt `la-beuze-distributeur`.** AGENTS.md réserve ce dépôt à LA BEUZE [ANALYSE fondée sur AGENTS.md].
- **Lire le coût avant chaque lancement** : bouton Generate, ou `higgsfield generate cost`.
- **Premier essai en basse résolution et sans audio**, comme le conseille Higgsfield : https://higgsfield-enterprise-help.higgsfield.app/docs/ai-models

### 3.1 Interface web (la voie la plus sûre pour lancer tout de suite)

- **Pages** :
  - https://higgsfield.ai/ai-video-editor (Kling 3.0 Omni Edit, Grok Imagine Edit, etc.)
  - https://higgsfield.ai/higgsfield-genjutsu-presets
  - https://higgsfield.ai/gemini-omni-flash
  - https://higgsfield.ai/minimax/h3
- **Chemin de menu vers Genjutsu, Kling Edit et Seedance Edit : non documenté** dans les sources lues. Seul chemin documenté : Edit → Reframe, pour changer le format.
- **Bouton « I own the rights for this image »** : à utiliser seulement si l'utilisateur détient réellement les droits sur ce qu'il importe. Ne pas s'en servir pour faire passer le logo Coca ou des éléments Minecraft.

### 3.2 CLI officielle

La syntaxe ci-dessous a été relevée dans `--help` du binaire v1.1.26, lancé hors réseau. **Elle n'a jamais été exécutée contre Higgsfield.**

**Version** [OFFICIEL]. Paquet `@higgsfield/cli` 1.1.26, publié le 18/09/2026, licence MIT. C'est un lanceur : il télécharge le binaire Go `hf` depuis https://github.com/higgsfield-ai/cli/releases/tag/v1.1.26 et vérifie son SHA-256. Commandes exposées : `higgsfield`, `higgs`, `hf`.

**Installation :**

```bash
npm i -g @higgsfield/cli
# ou :
curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
# L'option --prefix=$HOME/.local (installation sans sudo) est documentée ;
# la façon exacte de la passer au script n'a pas été vérifiée.

# Skills (facultatif), depuis https://github.com/higgsfield-ai/skills (v0.13.0, commit f83af0b) :
claude plugin marketplace add higgsfield-ai/skills
claude plugin install higgsfield@higgsfield
# ou : npx skills add higgsfield-ai/skills
```

**Authentification :**

```bash
higgsfield auth login      # OAuth PKCE dans le navigateur, rappel sur localhost:8765 (option --port)
higgsfield account status
```

- **Dans un conteneur cloud (non testé)**, la redirection vers localhost vise la machine de l'utilisateur, pas le conteneur. La connexion risque donc d'échouer.
- Le binaire ne contient **aucun device-flow**, contrairement à ce qu'affirme le CLAUDE.md du dépôt skills.
- Les identifiants sont stockés dans `~/.config/higgsfield/credentials.json` (selon la doc du dépôt skills). Ne pas copier ce fichier dans le conteneur.

**Découverte, obligatoire avant tout lancement.** La règle du dépôt skills interdit d'inventer un identifiant de modèle.

```bash
higgsfield model list --video --json
higgsfield model get seedance_2_5 --json
higgsfield model get hf_mult_replace_object --json
higgsfield workflow list
higgsfield workflow get draw_to_video
```

**Upload, coût, génération et suivi** (syntaxe vérifiée dans `--help`) :

```bash
higgsfield upload create ./seg1.mp4
higgsfield generate cost <job_type> ...
higgsfield generate create <job_type> --prompt "..." --video ./seg1.mp4 --image ./pioche_ref.png --wait --wait-timeout 20m --wait-interval 5s
higgsfield generate workflow draw_to_video --video ./seg1.mp4 --sketch ./frame_edit.png --timestamp 3.2 --prompt "..." --wait
higgsfield generate cost workflow draw_to_video --duration 8.2 --resolution 720p
higgsfield generate get <job_id> --json
higgsfield generate wait <job_id> --timeout 20m --interval 5s
higgsfield generate list --video --json
```

- Flags de médias présents : `--video` / `--video-references`, `--image` / `--image-references`, `--start-image`. Le flag accepté dépend du schéma du modèle, à lire avec `model get`.
- Un chemin local passé à un flag de média est uploadé automatiquement.
- `--image` est un alias de `--sketch` dans `draw_to_video`.
- Options globales : `--json` et `--no-color`.

**Téléchargement.** La CLI n'a pas de commande de téléchargement ; `--wait` affiche une URL de résultat. Exemple tiré du README :

```bash
higgsfield generate list --json | jq -r '.[] | select(.status=="completed") | .result_url'
curl -L -o edit1.mp4 "<url>"
```

Non vérifiés : le nom du champ d'URL dans `generate get --json` et le domaine du CDN.

**Non vérifié [INCERTAIN].** Le catalogue du skill liste pour `seedance_2_5` les modes `t2v`, `omni_reference`, `video_edit` et `video_extension`. Mais le fichier MODELS.md du dépôt CLI n'a pas de section `seedance_2_5`. La commande suivante est donc à confirmer avec `model get` avant usage :

```bash
higgsfield generate create seedance_2_5 --mode video_edit --video ./seg2.mp4 --prompt "..." --aspect_ratio 9:16 --resolution 720p --wait --wait-timeout 30m
```

Les identifiants CLI de Kling 3.0 Omni Edit et de Gemini Omni Flash n'ont pas été trouvés.

**Divers.** La variable `HIGGSFIELD_DISABLE_TELEMETRY` existe dans le binaire, mais son effet exact n'est pas vérifié. Le binaire envoie de la télémétrie Sentry.

### 3.3 MCP

- **Serveur** [OFFICIEL] : `https://mcp.higgsfield.ai/mcp`, transport HTTP, sans clé API, connexion OAuth. Les métadonnées publiques annoncent deux flux :
  - Clerk (`authorization_code` + PKCE) ;
  - `fnf-device-auth.higgsfield.ai` (`device_code`) ;
  - avec enregistrement dynamique des clients sur `https://mcp.higgsfield.ai/oauth2/register`.
- **Ajout dans claude.ai** : Settings → Connectors → Add custom connector. Aucun connecteur Higgsfield n'est présent dans la session actuelle.
- **Outils principaux** [OFFICIEL, d'après la règle du plugin Cursor] : `generate_video`, `media_upload` puis `media_confirm` (qui renvoie un `media_id`), `models_explore`, `job_status`, `job_display`, `balance`, `show_plans_and_credits`, `list_workspaces`, `select_workspace`.
- **Liste étendue** [TIERS, Composio v20260910_00] : `media_upload_widget` (upload depuis le navigateur, car le serveur ne lit pas les pièces jointes du chat), `media_import_url`, `jobs_wait`, `reframe`, `upscale_video`, `motion_control`, `reveal_generation`… Selon ces descriptions, un job vidéo prend 60 à 180 s.
- **Object Swap via MCP** [TIERS] : `generate_video` avec le modèle `hf_mult_replace_object`, les images en rôle `image` et exactement une vidéo en rôle `video`.
- **`reveal_generation`** débloque un job Seedance en statut `ip_detected` après attestation de droits. **Ne pas l'utiliser ici** : l'utilisateur ne détient les droits ni de Minecraft ni de Coca-Cola.
- **CLI ou MCP ?** Higgsfield recommande la CLI plutôt que le MCP pour Claude Code et Codex : https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-connect-higgsfield-to-ai-agent. Le flux `device_code` côté serveur MCP pourrait mieux convenir à une session cloud que le rappel localhost de la CLI. Non testé.

### 3.4 API développeur (à éviter sauf décision du porteur)

- Adresse `https://api.higgsfield.ai`, authentification par clé API.
- Facturation à la requête, en dollars, sur un solde prépayé. C'est un produit distinct des crédits web.
- C'est la seule voie sans navigateur.
- La clé doit être ajoutée par le porteur du projet comme secret d'environnement, jamais dans un fichier.
- Les prix de Genjutsu y sont contradictoires : 0,159 à 0,816 $/s dans le tableau ; 0,318, 0,681 et 1,632 $/s (480p, 720p, 1080p) dans le playground [INCERTAIN].

### 3.5 Domaines à autoriser pour une session cloud

| Usage | Domaines |
|---|---|
| Installation | `registry.npmjs.org`, `github.com` et son hôte de téléchargement des releases (déjà fonctionnel dans cette session), `raw.githubusercontent.com`, `api.github.com` |
| CLI | `fnf-api-gw.higgsfield.ai` (API), `clerk.higgsfield.ai` (OAuth), `higgsfield.ai`, `fnf.higgsfield.ai` |
| MCP | `mcp.higgsfield.ai`, `clerk.higgsfield.ai`, `fnf-device-auth.higgsfield.ai` |
| API développeur | `api.higgsfield.ai` |
| Télémétrie | `o4509169762697216.ingest.de.sentry.io` (seulement si la télémétrie reste active) |
| Non identifiés | stockage présigné pour l'upload, CDN des résultats (S3 ou CloudFront selon un tiers) |

- Le plus simple : autoriser `higgsfield.ai` et `*.higgsfield.ai`, dans les paramètres réseau de l'environnement cloud (https://code.claude.com/docs/en/claude-code-on-the-web).
- À 08:47 UTC, tous les hôtes Higgsfield testés répondaient depuis ce conteneur.

---

## 4. Règles de prompt et prompts négatifs

### Règles

1. **Écrire en anglais.** La grammaire officielle de Kling est en anglais.
2. **Un seul changement par génération**, puis enchaîner les passes.
3. **Préférer la formule locale au restyle global.** `Change … in [@Video] to …` garde le monde réel. `Change [@Video] to … style` transforme toute l'image [OFFICIEL, guide Kling].
4. **Nommer une seule cible, décrire son nouvel état, puis dire ce qui reste identique** (`keep everything else unchanged`). Pour Seedance, un guide tiers propose cinq blocs : l'objectif ; `@Video 1 is the sole editing master` ; le rôle des références ; `Modify only …` ; `Keep … from @Video 1`. https://omniart.studio/blog/tutorials-how-to-guides/seedance-2-5-video-editing-and-extension [TIERS]
5. **Désigner les fichiers par leurs libellés** : Image 1 / Video 1 ; `@Video` / `@Image` chez Kling ; `<<<video_1>>>` dans la démo Gemini. Fournir les références avant le prompt.
6. **Décrire au lieu de nommer.** C'est le conseil officiel de Higgsfield. Écrire `blocky voxel sandbox game, 16x16 pixel-art textures, pixelated pickaxe` plutôt que « Minecraft », et `plastic soda bottle` plutôt que « Coca-Cola ». Ajouter `remove every label and logo from the bottle`. Les images et vidéos de référence sont elles aussi contrôlées : la pioche de référence doit être un dessin original, pas une texture extraite du jeu.
7. **Décrire une pioche compacte, de la taille de la bouteille**, avec la même prise, la même position et la même trajectoire. Cela limite le problème de forme reconnu par Higgsfield.
8. **Choisir la prise la plus lente et la plus nette.** Travailler sur des segments de 4 à 10 s, ne refaire que l'intervalle raté, et recadrer si deux essais échouent [TIERS : https://picsart.com/blog/replace-object-in-video-with-ai/ et https://arxiv.org/html/2406.07754v2].
9. **Méthode « image d'abord »** [TIERS] : retoucher une image du clip pour y montrer la pioche en main, la valider, puis la fournir comme `@Image1`. La même image sert de `--sketch` pour `draw_to_video`.
10. **Demander une sortie propre** : `no HUD, no text, no interface`.

### Prompts négatifs

- Les références d'API de Kling Omni Video Edit, Kling O3 Video Edit et Kling 3.0 n'ont **aucun champ `negative_prompt`** [OFFICIEL] :
  - https://open.higgsfield.ai/models/kling-video/o3/video-edit/api-reference
  - https://open.higgsfield.ai/models/kling-video/v3.0/pro/image-to-video/api-reference
- Les exemples officiels de Higgsfield placent les exclusions dans le prompt lui-même.
- Un guide tiers indique que Kling 3.0 réagit mieux aux formulations positives.
- Recommandation : des exclusions courtes dans le prompt, doublées de verrous positifs.

Bloc d'exclusions :

```text
No text, no interface, no HUD, no logos, no readable labels, no watermarks, no morphing or sliding, no melted or rounded blocks, no duplicated tools, no extra fingers.
```

Verrous positifs :

```text
Real photorealistic human hand with five fingers, same grip, same arm, same lighting, same camera shake and timing; only the [target] changes.
```

Stabilité du style voxel [TIERS, https://buble.ai/minecraft-video-generator] :

```text
coherent cubic geometry, crisp pixel textures, right-angle silhouettes, stable block scale
```

### Modèles de prompts (non testés)

**V1-A — Genjutsu Object Swap** (Video 1 = segment, Image 1 = pioche originale) :

```text
Replace the plastic soda bottle held in the right hand in Video 1 with the pickaxe in Image 1: a compact blocky voxel pickaxe about the same size as the bottle, square pixel-textured wooden handle, flat grey stone pick head, crisp 16x16-style pixel texture, right-angle silhouette. Same grip, same position in the hand, same swing motion and timing. Keep the rest of the shot the same: real photorealistic hand with five fingers, arm, ground, background, lighting and camera shake unchanged. No labels, no logos, no text, no interface.
```

**V1-B — Kling 3.0 Omni Edit** (@Video1 = segment, @Image1 = pioche) :

```text
Change the plastic soda bottle held in the right hand in @Video1 to the blocky voxel pickaxe from @Image1: square pixel-textured wooden handle, flat grey stone-coloured pick head, crisp 16x16-style pixel texture, right-angle silhouette, compact size close to the bottle, held in the same grip and position, following the same swing motion. Remove every label and logo from the bottle. Keep the real human hand, five fingers, arm, lighting, ground, background, camera shake and timing unchanged and photorealistic; only the held object changes. When the pick hits the ground, a small burst of square pixel dust particles. No text, no interface, no logos, no morphing, no melted or rounded blocks, no extra fingers.
```

**V1-C — Gemini Omni Flash.** La syntaxe `<<<video_1>>>` vient de la démo officielle ; à confirmer dans l'interface.

```text
V2V on <<<video_1>>>. Keep the performance, hand motion, timing and camera move exactly as in the source. Change only the plastic soda bottle in the hand into a compact blocky voxel pickaxe with a pixel-textured wooden handle and a flat grey stone head, same size and same grip. Remove all labels and logos. Real photorealistic hand, five fingers. No text, no interface, no HUD.
```

**V1-D — Deuxième passe facultative : le caillou devient un cube** [ANALYSE] :

```text
Change the small stone picked up by the hand in @Video1 to a small blocky grey voxel cube with pixel texture, same size, following the hand exactly. Keep everything else unchanged and photorealistic. No text, no interface, no logos.
```

**V2-A — Seedance 2.5 Edit** (prompt en cinq blocs). Pour Draw to Edit, on peut en plus marquer la zone d'eau sur l'image de l'impact.

```text
Goal: turn the thrown stones and their water impacts into a blocky voxel game look while the real world stays real. @Video 1 is the sole editing master. Modify only the stones and the splashes: each stone becomes a small grey voxel cube with a pixel texture while in the air; where it lands, a burst of square pixel water droplets and a small flat ripple. Keep the real hand, arm, water surface, shoreline, sky, lighting, camera motion and timing from @Video 1 unchanged and photorealistic. No text, no interface, no logos, no watermarks, no melted or rounded blocks.
```

**V2-B — Kling 3.0 Omni Edit.** Si le résultat dérive, faire les cailloux et les éclaboussures en deux passes séparées.

```text
Change the stones thrown by the hand in @Video1 to small blocky grey voxel cubes with pixel texture, and change the water splashes in @Video1 to bursts of square pixel water droplets with a small flat ripple. Keep the real hand, arm, water surface, shoreline, sky, lighting, camera motion and timing unchanged and photorealistic. No text, no interface, no logos.
```

---

## 5. À vérifier dans l'interface au moment de lancer

- [ ] Le coût affiché sur Generate pour chaque outil. Celui de Kling O1 Video Edit et de Kling 3.0 Omni Edit n'a pas été trouvé.
- [ ] Genjutsu :
  - durée minimale (4 s sur le web, 1 s sur l'API, 3 s selon un tiers) ;
  - nombre de références (30, 8 ou 40 selon les sources) ;
  - résolution maximale (1080p ou 720p) ;
  - acceptation du 9:16 ;
  - taille minimale des images (409 600 px selon layer.ai).
- [ ] Gemini Omni Flash : durée d'entrée maximale (10 s, 30 s ou 60 s selon les sources).
- [ ] Seedance 2.5 Edit : résolution maximale (720p ou 1080p), coût réel, disponibilité selon le plan (absent de Starter et Basic).
- [ ] FPS de sortie de Genjutsu, Kling Edit et Seedance Edit (non publié), et FPS réel des rushes Snapchat (à lire avec `ffprobe`).
- [ ] Existence d'une option « garder le son d'origine » dans Kling Edit sur Higgsfield.
- [ ] Filtre IP : le style voxel décrit sans nom de marque passe-t-il ? Le logo Coca dans la source bloque-t-il ? Si possible, refilmer avec l'étiquette cachée ou tournée.
- [ ] Filtre sur les visages réels chez Seedance : risque probablement faible en POV, non confirmé sur Higgsfield.
- [ ] Identifiants et flags de la CLI :
  - `hf_mult_replace_object` ;
  - `seedance_2_5` avec `--mode video_edit` ;
  - identifiants de Kling Omni Edit et de Gemini Omni Flash (introuvables).
- [ ] `higgsfield auth login` dans un conteneur cloud, avec le rappel sur localhost : non testé.
- [ ] Nom du champ d'URL dans `generate get --json`, et domaines de stockage et de CDN.
- [ ] MiniMax H3 : mode édition disponible sur le web, et durée d'entrée acceptée.
- [ ] Wan 2.7 Edit sur une vidéo importée dans Higgsfield : non confirmé.
- [ ] Preset de style « Minecraft » (vu vers avril 2025) : encore disponible ? utilisable en vidéo → vidéo ? Non vérifié. Le mod HiggsCraft (Minecraft Java 1.21.1) génère à l'intérieur du jeu, pas dans la vie réelle, et ne prouve aucune exemption du filtre IP.
- [ ] Aucun exemple public vérifié ne montre l'effet exact (objet en main transformé en pioche voxel par vidéo → vidéo, avec HUD). Prévoir plusieurs essais.

---

## Ce qui n'a pas été fait

- Aucune génération lancée, aucun crédit dépensé, aucun compte connecté, aucun prompt testé.
- Le binaire CLI n'a été exécuté qu'avec `--help` et `version`, réseau coupé.
- Aucun fichier du dépôt `/home/user/la-beuze-distributeur` n'a été modifié.