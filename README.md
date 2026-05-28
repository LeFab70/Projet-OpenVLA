# openVLA

**Programmeur :** Fabrice Kouonang  
**Début du stage :** 14 mai 2026

---

## Intro stage

Développement d’un démonstrateur OpenVLA pour robot collaboratif UR et vision 2D ou 3D ZIVID

## Objectifs

Le projet visera en particulier à répondre à la question suivante : quels sont les ingrédients de la « sauce OpenVLA » et en quoi cette approche diffère-t-elle des méthodes robotiques plus traditionnelles ? Le stage permettra donc de combiner veille technologique, expérimentation pratique, intégration robotique et vulgarisation technique.

## Principales responsabilités

- Étudier l’architecture générale d’OpenVLA et en produire une description technique claire et structurée.
- Identifier les différentes composantes de la pipeline : perception, inférence, génération d’actions et exécution robotique.
- Comparer l’approche OpenVLA aux approches robotiques traditionnelles, notamment en ce qui concerne la programmation de tâches, la perception, la planification et le contrôle.
- Mettre en place un démonstrateur expérimental utilisant un robot collaboratif UR et une caméra Zivid.
- Réaliser l’intégration logicielle et matérielle nécessaire au fonctionnement du démonstrateur.
- Effectuer des essais, analyser les résultats obtenus et documenter les limites, défis et opportunités de l’approche.
- Produire une documentation technique et une synthèse vulgarisée destinée à l’équipe de CCNB-INNOV.
- Présenter les résultats du stage sous forme de démonstration et de présentation technique.

---

## Jour 01 — Début de stage CCNB-INNOV (rapport final)

**Date :** 14 mai 2026

Présentation du stage, objectifs, responsabilités et **rapport final** (parties I à III complétées) :

- **I.** Architecture générale d'OpenVLA
- **II.** Composantes de la pipeline (Zivid, OpenVLA, UR)
- **III.** Comparaison OpenVLA / robotique traditionnelle
- **II.5** Flux de données robot, Zivid et interprétation OpenVLA (jour 07)
- **II.1.1** Détection YOLOv8 + coordonnées 3D (jour 07)
- **II.1.2** Grounding DINO open-vocabulary (jour 07)
- **II.1.3** Comparaison YOLO vs Grounding DINO

- Rapport : `OpenVLA_day01_stage_CCNB.docx` — parties I à III, figures 1–4, sections II.1.1–II.1.3

## Jour 02 — Prise en main OpenVLA

**Date :** 14 mai 2026

Veille et documentation : architecture OpenVLA, flux de données, comparaison aux approches robotiques classiques, installation **openvla-7b** sous **Windows 11 Pro**.

- Rapport : `OpenVLA_day02_prise_en_main.docx`
- Notes d’installation détaillées : `scripts/utils.txt`

## Jour 03 — Robot UR (tracé lettre A)

**Date :** 19 mai 2026

Premier programme URScript sur le bras collaboratif : tracé géométrique de la lettre **A** avec `movej` (approche / retrait) et `movel` (traits linéaires).

**Étapes essentielles :** préparer TCP → définir 5 poses du A → approche (`movej`) → tracer (`movel`) → retour sécurité → répéter si besoin (`trace_A(n)`).

Les mêmes étapes peuvent aussi être exécutées **directement sur le robot** (PolyScope), pose par pose, sans script complet.

| Script UR (`.script`) | Description |
|-----------------------|-------------|
| `scripts/ur/URscriptLetterA.script` | Fonction `trace_A(n)` — 1 à 4 lettres (décalage Y) |
| `scripts/ur/traceAOnce.script` | Un seul A, sans boucle |
| `scripts/ur/returnToCenter.script` | Retour au centre de la table |

- Rapport : `OpenVLA_day03_trace_A.docx`

## Jour 04 — API Zivid + Conda (MR130)

**Date :** 20 mai 2026

- **Zivid** : connexion caméra **Zivid 2+ MR130**, acquisition 2D/3D (`capture_2d_3d`).
- **Sauvegarde** : `scripts/zivid/capture.py` enregistre `ColorImage.png`, `Frame.zdf` et `PointCloud.ply`.
- **Conda** : environnements Python **3.11** — `env_zivid`, `env_ur`, `env_integration`.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day04_zivid_api.docx` | API Zivid, script capture.py, sauvegarde image/frame/nuage |
| `OpenVLA_day04_conda_anaconda.docx` | Guide Conda/Anaconda, arborescence, commandes |

| Fichier Python (`.py`) | Description |
|------------------------|-------------|
| `scripts/zivid/capture.py` | Acquisition 2D/3D + sauvegarde PNG, ZDF, PLY |

## Jour 05 — OpenVLA + intégration Zivid / UR

**Date :** 21 mai 2026

- **Caméra** : test de capture réussi avec la Zivid 2+ MR130 (images 2D/3D, nuage de points).
- **OpenVLA** : environnement d’inférence sur **Windows 11 Pro** — modèle `openvla-7b` chargé et testé sur GPU (CUDA).
- **Pipeline** : capture Zivid → conversion RGB 224×224 → inférence OpenVLA → prédiction d’actions (XYZ, rotation, pince).
- **Intégration** : schéma Python — Zivid (SDK) + OpenVLA (transformers) ; connexion UR (ur-rtde) à venir.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day05_openvla_integration.docx` | Environnement OpenVLA, tests Zivid + inférence, intégration UR ↔ Zivid |

| Fichier Python (`.py`) | Rôle |
|------------------------|------|
| `scripts/integration/test/test_openvla.py` | Chargement modèle OpenVLA + vérification VRAM |
| `scripts/integration/test/test_zivid_openvla.py` | Capture Zivid + inférence OpenVLA (consignes texte) |

| Autre | Rôle |
|-------|------|
| `scripts/utils.txt` | Notes utilitaires (chemins, commandes, rappels) |

## Jour 06 — Rapport final + démonstrateur UR/Zivid/OpenVLA

Note : section déplacée après Jour 09 — révisée le 27 mai 2026.

**Date :** 22–23 mai 2026

### Édition rapport final (22 mai)

- **Rapport final** : édition et consolidation des **3 premières parties** de `OpenVLA_day01_stage_CCNB.docx`.
- **I.** Architecture générale d'OpenVLA — description technique, schémas, contraintes openvla-7b
- **II.** Composantes de la pipeline — Zivid, inférence OpenVLA, exécution UR
- **III.** Comparaison OpenVLA / robotique traditionnelle — tableau et synthèse démonstrateur

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day01_stage_CCNB.docx` | Rapport final — parties I à III éditées (22 mai 2026) |

### Démonstrateur complet (23 mai)

- **Intégration** : boucle fermée **Zivid → OpenVLA → UR16e** via `demoTest.py`.
- **RTDE** : `moveL`, lecture pose TCP, pince UR native (`setToolDigitalOut`).
- **Sécurité** : `SAFE_MODE`, `SCALE` (max 5 cm/step), vitesse/accélération limitées.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day06_demo_ur_zivid.docx` | Démonstrateur UR16e + Zivid + OpenVLA, boucle demoTest.py |

| Fichier Python (`.py`) | Description |
|------------------------|-------------|
| `scripts/integration/testUR_ZIVID/demoTest.py` | Boucle capture → inférence → commande robot (mode safe / réel) |

### Environnements Conda (Python 3.11)

| Environnement | Usage | Installation |
|---------------|-------|--------------|
| `env_zivid` | Caméra seule | `pip install zivid numpy opencv-python` |
| `env_ur` | Robot seul | `pip install ur-rtde` |
| `env_integration` | Zivid + UR | `pip install zivid ur-rtde numpy opencv-python` |
| `env_openvla` | Inférence OpenVLA | Windows 11 Pro — voir `OpenVLA_day02_prise_en_main.docx` et `scripts/utils.txt` |

**Installation openvla-7b (Windows 11 Pro, Python 3.11)**

```bash
conda create -n env_openvla python=3.11 -y && conda activate env_openvla
conda install -c conda-forge cmake -y
pip install numpy opencv-python scipy pillow ur_rtde zivid huggingface_hub accelerate
pip install transformers==4.40.1
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
hf auth login
huggingface-cli download openvla/openvla-7b --local-dir C:\Users\Etudiant\models\openvla-7b
python scripts/integration/test/test_openvla.py
```

```bash
conda create --name env_zivid python=3.11 -y && conda activate env_zivid
conda create --name env_ur python=3.11 -y && conda activate env_ur
conda create --name env_integration python=3.11 -y && conda activate env_integration
conda create --name env_openvla python=3.11 -y && conda activate env_openvla
```

### Arborescence `scripts/`

```
scripts/
├── zivid/capture.py
├── ur/                              (*.script UR)
├── openVLA_ZIVID/                   (package pip : Zivid + YOLO + OpenVLA)
│   ├── functions/returnAllPositions.py
│   └── test/
│       ├── zivid_yolo_openvla.py
│       ├── test_zivid_groundingDino.py
│       ├── test_yolo.py
│       └── havePositions.py
├── integration/
│   ├── zivid_ur_robot_integration.py
│   ├── test/
│   │   ├── test_openvla.py
│   │   ├── test_zivid_openvla.py
│   │   └── test_zivid_inference.py
│   └── testUR_ZIVID/
│       └── demoTest.py
└── utils.txt
```

**Dépendances détection 2D :** `pip install ultralytics` — `yolov8n.pt` (YOLO) ; Grounding DINO via `transformers` (`grounding-dino-base` sur Hugging Face).

Les fichiers `.py` sont en local (voir `.gitignore`) ; les `.script` UR sont versionnés sur Git.

**Fichiers du dépôt**

| Rapport (`.docx`) | Description |
|-------------------|-------------|
| `OpenVLA_day01_stage_CCNB.docx` | Rapport final — I à III, II.1.1–II.1.3 détection, II.5 |
| `OpenVLA_day02_prise_en_main.docx` | Jour 02 — architecture OpenVLA + installation openvla-7b |
| `OpenVLA_day03_trace_A.docx` | Jour 03 — tracé A UR, movej/movel |
| `OpenVLA_day04_zivid_api.docx` | Jour 04 — API Zivid, capture.py, sauvegarde image |
| `OpenVLA_day04_conda_anaconda.docx` | Jour 04 — Conda / Anaconda |
| `OpenVLA_day05_openvla_integration.docx` | Jour 05 — OpenVLA et intégration Zivid/UR |
| `OpenVLA_day06_demo_ur_zivid.docx` | Jour 06 — démonstrateur UR16e + Zivid + OpenVLA |
| `OpenVLA_day07_robot_data.docx` | Jour 07 — flux UR, YOLO vs Grounding DINO, prompts OpenVLA |

| Fichier Python (`.py`) | Description |
|------------------------|-------------|
| `scripts/zivid/capture.py` | Acquisition 2D/3D + sauvegarde ColorImage.png, Frame.zdf, PointCloud.ply |
| `scripts/integration/test/test_openvla.py` | Test chargement OpenVLA (GPU / VRAM) |
| `scripts/integration/test/test_zivid_openvla.py` | Test capture Zivid + inférence OpenVLA |
| `scripts/integration/testUR_ZIVID/demoTest.py` | Boucle Zivid + OpenVLA + UR16e (RTDE, mode safe) |
| `scripts/integration/zivid_ur_robot_integration.py` | Intégration Zivid + UR (en cours) |
| `scripts/openVLA_ZIVID/test/zivid_yolo_openvla.py` | Pipeline Zivid → YOLO → OpenVLA |
| `scripts/openVLA_ZIVID/test/test_zivid_groundingDino.py` | Pipeline Zivid → Grounding DINO → OpenVLA |
| `scripts/openVLA_ZIVID/functions/returnAllPositions.py` | Capture + détection YOLO + coords 3D |
| `yolov8n.pt` | Poids YOLOv8 nano (Ultralytics) |

| Script UR (`.script`) | Description |
|-----------------------|-------------|
| `scripts/ur/URscriptLetterA.script` | Programme UR — tracé du A (boucle) |
| `scripts/ur/traceAOnce.script` | Programme UR — tracé d’un seul A |
| `scripts/ur/returnToCenter.script` | Programme UR — retour au centre |

| Autre | Description |
|-------|-------------|
| `scripts/utils.txt` | Notes utilitaires du projet |

## Jour 07 — Données robot, YOLO, Grounding DINO et OpenVLA

**Date :** 25 mai 2026

Comprendre le **flux de données** Zivid → détection 2D → OpenVLA → UR ; comparer **YOLOv8n** (classes COCO) et **Grounding DINO** (open-vocabulary) ; clarifier ce qui entre dans OpenVLA versus ce que le robot conserve (XYZ).

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day07_robot_data.docx` | Rapport jour 07 complet : flux UR, YOLO, Grounding DINO, tableau comparatif |
| `OpenVLA_day01_stage_CCNB.docx` | Sections II.1.1–II.1.3, figures pipeline |

**Pipeline commun :** Zivid (RGB + nuage) → détection 2D → (u,v) → (X,Y,Z) → OpenVLA (224×224 + prompt) → `predict_action` → UR (RTDE).

| | **YOLOv8n** | **Grounding DINO** |
|---|-------------|-------------------|
| Détection | Classes COCO fixes | Texte libre (ex. `cell phone.`) |
| Modèle | `yolov8n.pt` | `IDEA-Research/grounding-dino-base` |
| Prompt OpenVLA | `pick up the {label} at position X=… Y=… Z=…` | `pick up the {label}` (option : + XYZ projetés) |
| Coords 3D | Injectées dans le prompt VLA | Affichées pour le contrôleur robot |

| Script | Rôle |
|--------|------|
| `scripts/openVLA_ZIVID/test/zivid_yolo_openvla.py` | Zivid → YOLO → OpenVLA (XYZ dans prompt) |
| `scripts/openVLA_ZIVID/test/test_zivid_groundingDino.py` | Zivid → Grounding DINO → OpenVLA |
| `scripts/openVLA_ZIVID/functions/returnAllPositions.py` | Capture + YOLO + coords 3D |
| `scripts/openVLA_ZIVID/test/test_yolo.py` | Test YOLO isolé |
| `scripts/integration/testUR_ZIVID/demoTest.py` | Boucle UR sans détecteur 2D |

**Dépendances :** `pip install ultralytics` (YOLO) ; Grounding DINO via `transformers` (Hugging Face).

## Jour 08 — Boucle continue (OpenVLA adaptatif)

**Date :** 26 mai 2026

Tester une boucle continue **perception → action → réinférence** pour rendre le système plus adaptatif (correction itérative à chaque nouvelle observation), avec Grounding DINO en amont pour localiser l’objet.

- **Note importante** : il est possible d’**injecter dans l’instruction OpenVLA** les coordonnées \((X,Y,Z)\) issues de **Grounding DINO + projection 3D Zivid**, pour guider davantage l’action (comme la variante YOLO) et gagner en efficacité.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day08_boucle_continue.docx` | Rapport jour 08 : boucle continue, scripts adaptatifs, prompt avec/sans XYZ |
| `OpenVLA_day01_stage_CCNB.docx` | Ajout dans II.5 : boucle continue + injection XYZ (Grounding DINO) |

| Script | Rôle |
|--------|------|
| `scripts/integration/test/demo_adaptatif_openvla.py` | DINO + UR16e + boucle OpenVLA (SAFE_MODE possible) |
| `scripts/integration/test/demo_adaptatif_openvla_print_value.py` | DINO + boucle OpenVLA (simulation, logs valeurs) |
| `scripts/build_day08_continuous_loop.py` | Génère le rapport jour 08 + met à jour le rapport final |

Mise à jour rapport final : **II.1.1**, **II.1.2**, **II.1.3**, **II.5** dans `OpenVLA_day01_stage_CCNB.docx`.

## Jour 09 — Tests, interprétation et mise à jour des rapports

**Date :** 27 mai 2026

Objectif : valider et analyser en détail la boucle continue (OpenVLA adaptatif) avec Grounding DINO ; interpréter les résultats en fonction
des coordonnées (X,Y,Z) fournies par DINO et la projection 3D Zivid.

- **Procédure de test :**
	- Exécuter `scripts/integration/test/demo_adaptatif_openvla_print_value.py` (mode simulation) pour consigner par itération : itération, coordonnées DINO (X,Y,Z), prédiction OpenVLA (delta), position TCP projetée, distance au but, état pince.
	- Pour essai réel, lancer `scripts/integration/test/demo_adaptatif_openvla.py` avec `SAFE_MODE` activé.

- **Métriques à collecter :**
	- Distance euclidienne entre l'objectif (X,Y,Z) de DINO et la position atteinte après chaque étape (m).
	- Nombre d'itérations jusqu'à convergence (distance < seuil défini).
	- Évolution de la coordonnée Z (vérifier la profondeur et saisie).
	- Stabilité des détections DINO (changement de bbox / multi-détections).

- **Interprétation rapide :**
	- Convergence rapide et décroissance monotone de la distance → comportement attendu (succès).
	- Oscillation autour d'un offset constant → possible erreur de calibration TCP/transform.
	- Divergence ou augmentation de la distance → détection instable ou SCALE de mouvement trop grand.
	- Variations importantes en Z → bruit de projection 3D (nuage Zivid) ; proposer d'augmenter la moyenne locale ou le filtre de profondeur.

- **Livrables jour 09 :**
	- `OpenVLA_day09_boucle_results.docx` — rapport d'expérimentation (tableaux, graphiques, synthèse).
	- Mise à jour de `OpenVLA_day01_stage_CCNB.docx` : ajout d'un appendice II.5 avec résultats et interprétation.

- **Scripts utiles / remarques :**
	- `scripts/integration/test/demo_adaptatif_openvla_print_value.py` (logs détaillés pour analyse).
	- `scripts/integration/test/demo_adaptatif_openvla.py` (exécution avec robot / SAFE_MODE).
	- `scripts/build_day08_continuous_loop.py` peut être étendu pour générer automatiquement `OpenVLA_day09_boucle_results.docx`.

## Jour 10 — Refactoring pipeline (modules indépendants)

**Date :** 28 mai 2026

Idée : refactoriser le démonstrateur en **modules indépendants** pour sécuriser l’intégration UR16e, corriger les bugs majeurs (calibration/workspace), et rendre la boucle continue plus robuste (réintégration DINO).

- **Points critiques** :
	- Calibration main-œil (caméra → robot) **obligatoire** : sans `T_tcp_cam.npy`, conversion DINO → robot non fiable.
	- **Workspace** : bornes obligatoires pour éviter des mouvements hors cellule.
	- **Réintégrer DINO** dans la boucle (toutes les N étapes) pour corriger la dérive.
	- **Prompt dynamique OpenVLA** : préférer une consigne relative basée sur la distance TCP→objet (deltas), plutôt que des coordonnées absolues.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day10_refactoring_pipeline.docx` | Rapport jour 10 : refactoring + points de sécurité |
| `OpenVLA_day01_stage_CCNB.docx` | Ajout note “Jour 10” dans II.5 |

| Dossier / scripts | Rôle |
|-------------------|------|
| `pipeline/` | Découpage : `config.py`, `calibration.py`, `zivid_capture.py`, `dino_detector.py`, `ur_controller.py`, `gripper.py`, `vla_controller.py` |
| `pipeline/main_real.py` | Exécution robot réel (UR16e) |
| `pipeline/main_sim.py` | Simulation / dry-run |
| `pipeline/calibrer_robot.py` | Calibration main-œil UR16e + Zivid → sauvegarde `T_tcp_cam.npy` |

## Jour 11 — Rapport hebdomadaire + calibration main-œil (T_tcp_cam)

**Date :** 29 mai 2026

Rapport hebdomadaire (semaine 26–29 mai) + mise en place de la **calibration caméra → robot**.  
Le rapport final (`OpenVLA_day01_stage_CCNB.docx`) reprend cette section en **II.6** avec les parties **I à V** ci-dessous.

### I. Fichier `T_tcp_cam.npy` — traducteur mathématique

Sans la matrice **T_tcp_cam** (4×4), la caméra et le bras ne partagent pas le même repère :

- **Caméra** : « Je vois la bouteille à 10 cm à ma gauche et 50 cm devant moi. »
- **Robot** : « Moi, je suis à 40 cm de ma base. Je ne sais pas où est ta gauche. »

Après calibration Zivid réussie, le résultat est enregistré avec **`np.save`** :

```python
np.save(CALIBRATION_FILE, T_tcp_cam)  # → T_tcp_cam.npy (voir pipeline/config.py)
```

### II. `pipeline/calibrer_robot.py` — script **autonome** (création du fichier)

À exécuter **seul**, indépendamment de `main_real.py` / `main_sim.py`, pour générer ou régénérer `T_tcp_cam.npy` :

1. Déplacer le UR16e vers des poses variées (mire damier noir et blanc visible).
2. Pour chaque pose : **`camera.capture()`** (échantillon Zivid), puis détection de la mire via **`zivid.calibration.detect_feature_points`** sur le nuage de points.
3. Accumuler les paires pose TCP + détection valide, puis **`zivid.calibration.calibrate_eye_in_hand`**.
4. Si la calibration est valide : **`np.save`** vers `T_tcp_cam.npy`.

```bash
python -m pipeline.calibrer_robot
```

### III. `pipeline/calibration.py` — utilisé **à chaque** run OpenVLA

Lors des déplacements du pipeline (perception → OpenVLA → RTDE), ce module **recharge** la matrice et convertit les coordonnées :

| Fonction | Rôle |
|----------|------|
| `load_calibration()` | `np.load(T_tcp_cam.npy)` si présent, sinon matrice identité |
| `cam_to_robot()` | Convertit un point DINO (repère caméra) → base robot |
| `compute_distance_tcp_to_object()` | Distance TCP–objet (arrêt / prompt adaptatif) |

**Distinction :** `calibrer_robot.py` **crée** le fichier (mire + hand-eye) ; `calibration.py` **l’utilise** à chaque cycle pour réajuster les mouvements.

### IV. Les 3 règles d’or pour les poses de calibration

- **Varier l’inclinaison** : ne pas rester toujours à la verticale (RX=0, RY=3.14). Incliner le poignet de ±15° à ±25° (~0,3 à 0,4 rad).
- **Varier la hauteur (Z)** : captures à ~40 cm, 50 cm et 60 cm de la mire.
- **Rotation RZ** : faire tourner l’outil sur lui-même.

### V. Livrables

| Rapport / module | Contenu |
|------------------|---------|
| `OpenVLA_day11_rapport_hebdomadaire.docx` | Rapport hebdomadaire (parties I–III calibration) |
| `OpenVLA_day01_stage_CCNB.docx` | Rapport final — section **II.6 Jour 11** |
| `rapports_hebdomadaires/` | Dossier des rapports hebdomadaires (à compléter) |
| `pipeline/calibrer_robot.py` | Calibration eye-in-hand → `T_tcp_cam.npy` |
| `pipeline/calibration.py` | Chargement + conversion à chaque exécution pipeline |

