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

- Rapport : `OpenVLA_prise_en_main.docx`

## Jour 02 — Robot UR (tracé lettre A)

**Date :** 19 mai 2026

Premier programme URScript sur le bras collaboratif : tracé géométrique de la lettre **A** avec déplacement linéaire (`movel`), approche sécurisée et paramètres de vitesse/accélération.

- Script : `scripts/ur/URscriptLetterA.script` — fonction `trace_A(n)` pour tracer 1 à 4 lettres (décalage automatique sur Y).
- Script : `scripts/ur/traceAOnce.script` — un seul A, sans boucle.
- Script : `scripts/ur/returnToCenter.script` — retour position centre table.
- Rapport : `OpenVLA_day02_trace_A.docx` — objectifs, code de référence et notes de sécurité.

## Jour 03 — API Zivid + Conda (MR130)

**Date :** 20 mai 2026

- **Zivid** : connexion caméra **Zivid 2+ MR130**, acquisition 2D/3D (`capture_2d_3d`).
- **Conda** : trois environnements Python 3.10 — `env_zivid`, `env_ur`, `env_integration`.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day03_zivid_api.docx` | API Zivid, exemple d’acquisition |
| `OpenVLA_day03_conda_anaconda.docx` | Guide Conda/Anaconda, arborescence, commandes |

## Jour 04 — OpenVLA + intégration Zivid / UR

**Date :** 21 mai 2026

- **Caméra** : test de capture réussi avec la Zivid 2+ MR130 (images 2D/3D, nuage de points).
- **OpenVLA** : environnement d’inférence sur **Windows 11 Pro** — modèle `openvla-7b` chargé et testé sur GPU (CUDA).
- **Pipeline** : capture Zivid → conversion RGB 224×224 → inférence OpenVLA → prédiction d’actions (XYZ, rotation, pince).
- **Intégration** : schéma Python — Zivid (SDK) + OpenVLA (transformers) ; connexion UR (ur-rtde) à venir.

| Rapport | Contenu |
|---------|---------|
| `OpenVLA_day04_openvla_integration.docx` | Environnement OpenVLA, tests Zivid + inférence, intégration UR ↔ Zivid |

| Script | Rôle |
|--------|------|
| `scripts/integration/test/test_openvla.py` | Chargement modèle OpenVLA + vérification VRAM |
| `scripts/integration/test/test_zivid_openvla.py` | Capture Zivid + inférence OpenVLA (consignes texte) |
| `scripts/utils.txt` | Notes utilitaires (chemins, commandes, rappels) |

### Environnements Conda (Python 3.10)

| Environnement | Usage | Installation |
|---------------|-------|--------------|
| `env_zivid` | Caméra seule | `pip install zivid numpy opencv-python` |
| `env_ur` | Robot seul | `pip install ur-rtde` |
| `env_integration` | Zivid + UR | `pip install zivid ur-rtde numpy opencv-python` |
| `env_openvla` | Inférence OpenVLA | Windows 11 Pro — `pip install transformers torch pillow zivid numpy` |

```bash
conda create --name env_zivid python=3.10 -y && conda activate env_zivid
conda create --name env_ur python=3.10 -y && conda activate env_ur
conda create --name env_integration python=3.10 -y && conda activate env_integration
conda create --name env_openvla python=3.10 -y && conda activate env_openvla
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

| Fichier | Description |
|---------|-------------|
| `OpenVLA_prise_en_main.docx` | Prise en main OpenVLA (architecture, flux de données) |
| `OpenVLA_day02_trace_A.docx` | Journal jour 02 — intégration UR |
| `OpenVLA_day03_zivid_api.docx` | Journal jour 03 — API Zivid MR130 |
| `OpenVLA_day03_conda_anaconda.docx` | Journal jour 03 — Conda / Anaconda |
| `OpenVLA_day04_openvla_integration.docx` | Journal jour 04 — OpenVLA et intégration Zivid/UR |
| `scripts/zivid/capture.py` | Acquisition 2D/3D Zivid MR130 |
| `scripts/integration/test/test_openvla.py` | Test chargement OpenVLA (GPU / VRAM) |
| `scripts/integration/test/test_zivid_openvla.py` | Test capture Zivid + inférence OpenVLA |
| `scripts/integration/zivid_ur_robot_integration.py` | Script d’intégration Zivid + UR (en cours) |
| `scripts/utils.txt` | Notes utilitaires du projet |
| `scripts/ur/URscriptLetterA.script` | Programme UR — tracé du A (boucle) |
| `scripts/ur/traceAOnce.script` | Programme UR — tracé d’un seul A |
| `scripts/ur/returnToCenter.script` | Programme UR — retour au centre |
