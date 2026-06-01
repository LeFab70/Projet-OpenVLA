# Agenda quotidien — Stage OpenVLA

**Programmeur :** Fabrice Kouonang  
**Document Word :** `agenda_quotidien_Fabrice.docx`

**Superviseur :** Guillaume Batungwanayo

---

## Semaine 1 — jeudi 14 au vendredi 15 mai 2026 (jours 01–02)

**Objectif de la semaine :** Cadrer le stage CCNB-INNOV, le démonstrateur OpenVLA (UR + Zivid 2+ MR130) et installer l’environnement d’inférence openvla-7b.

### Jour 01 — Début de stage CCNB-INNOV

**Date :** 14 mai 2026 (jeudi)

#### 1. Objectif du jour

Cadrage du sujet, objectifs, rapport final (parties I à III).

#### 2. Réalisations

- Question directrice : ingrédients de la « sauce OpenVLA » (VLA vs robotique classique).
- Rapport final : I — architecture (SigLIP/DINOv2 + MLP + Llama 2 7B), II — pipeline Zivid / OpenVLA / UR16e, III — comparaison programmation / perception / contrôle.
- Schéma des flux : image 224×224 + prompt texte → vecteur d’action 7D (ΔXYZ, rotation, gripper).

#### 3. Prochaine étape

Installation openvla-7b et tests GPU sous Windows.

### Jour 02 — Prise en main OpenVLA

**Date :** 15 mai 2026 (vendredi)

#### 1. Objectif du jour

Mettre en place env_openvla et valider le chargement du modèle sur GPU NVIDIA.

#### 2. Réalisations

- Conda Python 3.11 : env_openvla, transformers==4.40.1, PyTorch nightly cu128 (RTX 5090 / sm_120).
- Téléchargement Hugging Face openvla/openvla-7b (~15 Go VRAM, inférence FP16/bfloat16).
- test_openvla.py : vérification CUDA, VRAM et predict_action.
- Boucle VLA documentée : encodeur visuel → fusion langage → tête d’action discrète continue.

#### 3. Prochaine étape

Environnements Conda Zivid/UR et premiers URScript.

---

## Semaine 2 — mardi 19 au vendredi 22 mai 2026 (jours 03–06)

**Objectif de la semaine :** Maîtriser URScript, API Zivid MR130, pipeline Zivid→OpenVLA, puis boucle fermée Zivid→OpenVLA→UR16e (RTDE).

### Jour 03 — Robot UR — tracé lettre A

**Date :** 19 mai 2026 (mardi)

#### 1. Objectif du jour

Programmer le UR en URScript (movej / movel) avec paramètres de sécurité.

#### 2. Réalisations

- 5 poses TCP pour la lettre « A » : approche movej (lift 0,02 m), traits movel, retrait.
- Vitesse limitée ~0,1 m/s ; scripts URscriptLetterA.script, traceAOnce.script, returnToCenter.script.
- Validation PolyScope : enseignement point à point des poses avant exécution script.

#### 3. Prochaine étape

Capture 2D/3D Zivid et environnements Conda isolés.

### Jour 04 — API Zivid + Conda

**Date :** 20 mai 2026 (mercredi)

#### 1. Objectif du jour

Capturer RGB + nuage de points MR130 et isoler les dépendances Python.

#### 2. Réalisations

- Zivid SDK : connexion MR130, capture_2d_3d → ColorImage.png, Frame.zdf, PointCloud.ply (capture.py).
- Environnements Conda 3.11 : env_zivid (zivid, numpy, opencv), env_ur (ur-rtde), env_integration.
- Contrainte distance MR130 : profondeur valide dans la plage fabricant (éviter Z bruité hors workspace optique).

#### 3. Prochaine étape

Inférence OpenVLA sur images Zivid 224×224.

### Jour 05 — OpenVLA + intégration Zivid

**Date :** 21 mai 2026 (jeudi)

#### 1. Objectif du jour

Chaîne capture Zivid → prétraitement → predict_action OpenVLA sur GPU.

#### 2. Réalisations

- Conversion RGBA→RGB, redimensionnement 224×224, prompt libre (ex. « pick up the phone »).
- test_zivid_openvla.py : capture live + inférence ; sortie 7D (translation, rotation euler/quat, gripper).
- Poste Windows 11 Pro dédié (CUDA) — OpenVLA non exécutable sur Mac sans GPU NVIDIA.

#### 3. Prochaine étape

Boucle RTDE UR16e avec SAFE_MODE et SCALE.

### Jour 06 — Rapport final + démonstrateur

**Date :** 22–23 mai 2026

#### 1. Objectif du jour

Consolider rapport I–III puis demoTest.py : Zivid→OpenVLA→UR16e.

#### 2. Réalisations

- 22 mai : édition rapport final (architecture, pipeline, comparaison traditionnelle).
- 23 mai : demoTest.py — ur_rtde moveL, getActualTCPPose(), setToolDigitalOut (pince), lecture action OpenVLA.
- SAFE_MODE (affichage sans exécution), SCALE=0,05 m/step max, accélération/vitesse réduites.
- Arborescence scripts/ : zivid/, ur/*.script, integration/testUR_ZIVID/, openVLA_ZIVID/.

#### 3. Prochaine étape

Détection 2D (YOLO / Grounding DINO) + projection (u,v)→(X,Y,Z).

---

## Semaine 3 — lundi 25 au vendredi 29 mai 2026 (jours 07–11)

**Objectif de la semaine :** Perception 2D/3D, boucle adaptative OpenVLA, refactoring pipeline/, calibration eye-in-hand T_tcp_cam.npy.

### Jour 07 — YOLO, Grounding DINO, flux 3D

**Date :** 25 mai 2026 (lundi)

#### 1. Objectif du jour

Comparer YOLOv8n (COCO) et Grounding DINO (open-vocab) avec projection Zivid.

#### 2. Réalisations

- Pipeline : Zivid RGB + point cloud → bbox (u,v) → (X,Y,Z) caméra → prompt → predict_action → RTDE.
- YOLOv8n (yolov8n.pt) : label COCO + XYZ injectés dans le prompt (« pick up the {label} at X=… »).
- Grounding DINO (IDEA-Research/grounding-dino-base) : requête texte libre, XYZ pour contrôleur robot.
- Scripts : zivid_yolo_openvla.py, test_zivid_groundingDino.py, returnAllPositions.py.

#### 3. Prochaine étape

Boucle continue perception→action→réinférence.

### Jour 08 — Boucle continue OpenVLA adaptatif

**Date :** 26 mai 2026 (mardi)

#### 1. Objectif du jour

Itérer capture→inférence→mouvement avec réobservation à chaque cycle.

#### 2. Réalisations

- demo_adaptatif_openvla.py : DINO + boucle UR ; demo_adaptatif_openvla_print_value.py : logs sans robot.
- Prompt enrichi optionnel : coordonnées (X,Y,Z) projetées depuis DINO + nuage Zivid (comme variante YOLO).
- Paramètres SAFE_MODE, SCALE, seuil de convergence sur distance TCP–objet.

#### 3. Prochaine étape

Métriques d_t, convergence, analyse des oscillations.

### Jour 09 — Tests et interprétation

**Date :** 27 mai 2026 (mercredi)

#### 1. Objectif du jour

Quantifier la boucle adaptative (simulation puis robot en SAFE_MODE).

#### 2. Réalisations

- Logs par itération : bbox DINO, (X,Y,Z), delta OpenVLA, pose TCP, distance euclidienne d_t, état pince.
- Critères : convergence si d_t < seuil ; oscillation → calibration TCP ; divergence → SCALE ou détection instable.
- Filtrage profondeur Z (moyenne locale sur nuage) pour réduire le bruit MR130.

#### 3. Prochaine étape

Modulariser en pipeline/ (config, calibration, détecteurs, UR, VLA).

### Jour 10 — Refactoring pipeline/

**Date :** 28 mai 2026 (jeudi)

#### 1. Objectif du jour

Modules indépendants + workspace + prompt relatif (deltas).

#### 2. Réalisations

- pipeline/ : config.py (SAFE_MODE, SCALE, Z_MIN/Z_MAX), zivid_capture, dino_detector (scale_u/v, clip indices), ur_controller, vla_controller, gripper.
- main_real.py / main_sim.py ; calibrer_robot.py pour T_tcp_cam.npy (hand-eye).
- Réinférence DINO toutes les N itérations ; prompt basé sur vecteur TCP→objet plutôt qu’absolu.

#### 3. Prochaine étape

Calibration mire Zivid et np.save(T_tcp_cam).

### Jour 11 — Calibration main-œil + rapport hebdo

**Date :** 29 mai 2026 (vendredi)

#### 1. Objectif du jour

Générer T_tcp_cam (4×4) et documenter conversion caméra→base robot.

#### 2. Réalisations

- calibrer_robot.py : poses variées (inclinaison RX/RY ±15–25°, Z 40–60 cm, rotation RZ), detect_feature_points, calibrate_eye_in_hand.
- calibration.py : load_calibration(), cam_to_robot(), compute_distance_tcp_to_object().
- Matrice homogène T_tcp_cam : point caméra → repère base UR16e pour moveL cohérents.

#### 3. Prochaine étape

Essais réels main_real.py avec calibration chargée.

---

## Semaine 4 — lundi 1 juin 2026 (jours 12)

**Objectif de la semaine :** Valider le démonstrateur complet sur cellule (Zivid + OpenVLA + UR16e + pince).

### Jour 12 — Test réel du démonstrateur

**Date :** 1 juin 2026 (lundi)

#### 1. Objectif du jour

Exécution bout en bout avec T_tcp_cam.npy, workspace et SAFE_MODE.

#### 2. Réalisations

- (Prévu) test_zivid_openvla.py : capture MR130 + inférence 224×224 sans RTDE.
- (Prévu) demoTest.py puis pipeline/main_real.py : DINO → OpenVLA → moveL, bornes workspace.
- (Prévu) Vérification SCALE, getActualTCPPose(), pince Robotiq ; journalisation d_t et itérations.

#### 3. Prochaine étape

Prise d’objet en boucle fermée et documentation semaine 4.

---
