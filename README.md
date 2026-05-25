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

- Rapport : `OpenVLA_day01_stage_CCNB.docx` — table des matières, synthèse + schémas architecture (parties I à III ; II.5 jour 07)

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

## Jour 07 — Données robot et interprétation OpenVLA

**Date :** 25 mai 2026

Comprendre le **flux de données** entre Zivid, OpenVLA et le robot UR : ce qui entre réellement dans le modèle (image RGB 224×224 + consigne texte), ce que le robot fournit via RTDE (pose TCP pour exécution, pas pour l’inférence), et comment `predict_action` produit et interprète les 7 degrés de liberté.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day07_robot_data.docx` | Entrées/sorties OpenVLA, rôle RTDE, tableau récapitulatif, scripts de référence |

**Points clés :**

- **Entrées OpenVLA** : capture Zivid → RGB 224×224 ; prompt `In: What action should the robot take to {instruction}?\nOut:`
- **Pas d’entrée robot dans le modèle** : joints / pose TCP non envoyés au réseau dans la démo actuelle
- **Robot après inférence** : `getActualTCPPose()` → `new_pose = current + action × SCALE` → `moveL` + pince
- **Scripts** : `test_zivid_openvla.py` (sans UR), `demoTest.py` (boucle complète)

Mise à jour du rapport final : section **II.5** dans `OpenVLA_day01_stage_CCNB.docx`.

## Jour 06 — Rapport final + démonstrateur UR/Zivid/OpenVLA

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
├── ur/                              (*.script UR + test_robot.py)
├── integration/
│   ├── zivid_ur_robot_integration.py
│   ├── test/
│   │   ├── test_openvla.py
│   │   └── test_zivid_openvla.py
│   └── testUR_ZIVID/
│       └── demoTest.py
└── utils.txt
```

Les fichiers `.py` sont en local (voir `.gitignore`) ; les `.script` UR sont versionnés sur Git.

**Fichiers du dépôt**

| Rapport (`.docx`) | Description |
|-------------------|-------------|
| `OpenVLA_day01_stage_CCNB.docx` | Rapport final — parties I à III + II.5 flux données (jour 07) |
| `OpenVLA_day02_prise_en_main.docx` | Jour 02 — architecture OpenVLA + installation openvla-7b |
| `OpenVLA_day03_trace_A.docx` | Jour 03 — tracé A UR, movej/movel |
| `OpenVLA_day04_zivid_api.docx` | Jour 04 — API Zivid, capture.py, sauvegarde image |
| `OpenVLA_day04_conda_anaconda.docx` | Jour 04 — Conda / Anaconda |
| `OpenVLA_day05_openvla_integration.docx` | Jour 05 — OpenVLA et intégration Zivid/UR |
| `OpenVLA_day06_demo_ur_zivid.docx` | Jour 06 — démonstrateur UR16e + Zivid + OpenVLA |
| `OpenVLA_day07_robot_data.docx` | Jour 07 — données robot, entrées OpenVLA, interprétation predict_action |

| Fichier Python (`.py`) | Description |
|------------------------|-------------|
| `scripts/zivid/capture.py` | Acquisition 2D/3D + sauvegarde ColorImage.png, Frame.zdf, PointCloud.ply |
| `scripts/integration/test/test_openvla.py` | Test chargement OpenVLA (GPU / VRAM) |
| `scripts/integration/test/test_zivid_openvla.py` | Test capture Zivid + inférence OpenVLA |
| `scripts/integration/testUR_ZIVID/demoTest.py` | Boucle Zivid + OpenVLA + UR16e (RTDE, mode safe) |
| `scripts/integration/zivid_ur_robot_integration.py` | Intégration Zivid + UR (en cours) |

| Script UR (`.script`) | Description |
|-----------------------|-------------|
| `scripts/ur/URscriptLetterA.script` | Programme UR — tracé du A (boucle) |
| `scripts/ur/traceAOnce.script` | Programme UR — tracé d’un seul A |
| `scripts/ur/returnToCenter.script` | Programme UR — retour au centre |

| Autre | Description |
|-------|-------------|
| `scripts/utils.txt` | Notes utilitaires du projet |
