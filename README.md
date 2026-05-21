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

## Jour 01 — Prise en main OpenVLA

**Date :** 14 mai 2026

Veille et documentation : architecture OpenVLA, flux de données, comparaison aux approches robotiques classiques.

- Rapport : `OpenVLA_prise_en_main.docx` — inclut l’installation **openvla-7b** sous **Windows 11 Pro** (Conda Python 3.11, PyTorch CUDA, Hugging Face, tests GPU).
- Notes d’installation détaillées : `scripts/utils.txt`

## Jour 02 — Robot UR (tracé lettre A)

**Date :** 19 mai 2026

Premier programme URScript sur le bras collaboratif : tracé géométrique de la lettre **A** avec `movej` (approche / retrait) et `movel` (traits linéaires).

**Étapes essentielles :** préparer TCP → définir 5 poses du A → approche (`movej`) → tracer (`movel`) → retour sécurité → répéter si besoin (`trace_A(n)`).

Les mêmes étapes peuvent aussi être exécutées **directement sur le robot** (PolyScope), pose par pose, sans script complet.

| Script UR (`.script`) | Description |
|-----------------------|-------------|
| `scripts/ur/URscriptLetterA.script` | Fonction `trace_A(n)` — 1 à 4 lettres (décalage Y) |
| `scripts/ur/traceAOnce.script` | Un seul A, sans boucle |
| `scripts/ur/returnToCenter.script` | Retour au centre de la table |

- Rapport : `OpenVLA_day02_trace_A.docx` — étapes, script de référence, exécution directe movej/movel

## Jour 03 — API Zivid + Conda (MR130)

**Date :** 20 mai 2026

- **Zivid** : connexion caméra **Zivid 2+ MR130**, acquisition 2D/3D (`capture_2d_3d`).
- **Sauvegarde** : `scripts/zivid/capture.py` enregistre `ColorImage.png`, `Frame.zdf` et `PointCloud.ply`.
- **Conda** : environnements Python **3.11** — `env_zivid`, `env_ur`, `env_integration`.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day03_zivid_api.docx` | API Zivid, script capture.py, sauvegarde image/frame/nuage |
| `OpenVLA_day03_conda_anaconda.docx` | Guide Conda/Anaconda, arborescence, commandes |

| Fichier Python (`.py`) | Description |
|------------------------|-------------|
| `scripts/zivid/capture.py` | Acquisition 2D/3D + sauvegarde PNG, ZDF, PLY |

## Jour 04 — OpenVLA + intégration Zivid / UR

**Date :** 21 mai 2026

- **Caméra** : test de capture réussi avec la Zivid 2+ MR130 (images 2D/3D, nuage de points).
- **OpenVLA** : environnement d’inférence sur **Windows 11 Pro** — modèle `openvla-7b` chargé et testé sur GPU (CUDA).
- **Pipeline** : capture Zivid → conversion RGB 224×224 → inférence OpenVLA → prédiction d’actions (XYZ, rotation, pince).
- **Intégration** : schéma Python — Zivid (SDK) + OpenVLA (transformers) ; connexion UR (ur-rtde) à venir.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day04_openvla_integration.docx` | Environnement OpenVLA, tests Zivid + inférence, intégration UR ↔ Zivid |

| Fichier Python (`.py`) | Rôle |
|------------------------|------|
| `scripts/integration/test/test_openvla.py` | Chargement modèle OpenVLA + vérification VRAM |
| `scripts/integration/test/test_zivid_openvla.py` | Capture Zivid + inférence OpenVLA (consignes texte) |

| Autre | Rôle |
|-------|------|
| `scripts/utils.txt` | Notes utilitaires (chemins, commandes, rappels) |

### Environnements Conda (Python 3.11)

| Environnement | Usage | Installation |
|---------------|-------|--------------|
| `env_zivid` | Caméra seule | `pip install zivid numpy opencv-python` |
| `env_ur` | Robot seul | `pip install ur-rtde` |
| `env_integration` | Zivid + UR | `pip install zivid ur-rtde numpy opencv-python` |
| `env_openvla` | Inférence OpenVLA | Windows 11 Pro — voir `OpenVLA_prise_en_main.docx` et `scripts/utils.txt` |

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
│   └── test/
│       ├── test_openvla.py
│       └── test_zivid_openvla.py
└── utils.txt
```

Les fichiers `.py` sont en local (voir `.gitignore`) ; les `.script` UR sont versionnés sur Git.

**Fichiers du dépôt**

| Rapport (`.docx`) | Description |
|-------------------|-------------|
| `OpenVLA_prise_en_main.docx` | Prise en main OpenVLA + installation openvla-7b (Windows 11 Pro) |
| `OpenVLA_day02_trace_A.docx` | Journal jour 02 — tracé A, movej/movel, exécution directe |
| `OpenVLA_day03_zivid_api.docx` | Journal jour 03 — API Zivid, capture.py, sauvegarde image |
| `OpenVLA_day03_conda_anaconda.docx` | Journal jour 03 — Conda / Anaconda |
| `OpenVLA_day04_openvla_integration.docx` | Journal jour 04 — OpenVLA et intégration Zivid/UR |

| Fichier Python (`.py`) | Description |
|------------------------|-------------|
| `scripts/zivid/capture.py` | Acquisition 2D/3D + sauvegarde ColorImage.png, Frame.zdf, PointCloud.ply |
| `scripts/integration/test/test_openvla.py` | Test chargement OpenVLA (GPU / VRAM) |
| `scripts/integration/test/test_zivid_openvla.py` | Test capture Zivid + inférence OpenVLA |
| `scripts/integration/zivid_ur_robot_integration.py` | Intégration Zivid + UR (en cours) |

| Script UR (`.script`) | Description |
|-----------------------|-------------|
| `scripts/ur/URscriptLetterA.script` | Programme UR — tracé du A (boucle) |
| `scripts/ur/traceAOnce.script` | Programme UR — tracé d’un seul A |
| `scripts/ur/returnToCenter.script` | Programme UR — retour au centre |

| Autre | Description |
|-------|-------------|
| `scripts/utils.txt` | Notes utilitaires du projet |
