# Agenda quotidien — Stage OpenVLA

**Programmeur :** Fabrice Kouonang  
**Début du stage :** 14 mai 2026  
**Document Word :** `agenda_quotidien_Fabrice.docx` (généré par ce script)

**Superviseur :** Guillaume Batungwanayo

---

## Jour 01 — Début de stage CCNB-INNOV

**Date :** 14 mai 2026 (jeudi)

### 1. Objectif du jour

Démarrer le stage au CCNB-INNOV, cadrer le sujet du démonstrateur OpenVLA (robot UR + caméra Zivid 2+ MR130) et lancer le rapport final.

### 2. Réalisations

- Présentation du stage, des objectifs et des responsabilités (veille, intégration, démonstration).
- Formulation de la question directrice : quels sont les ingrédients de la « sauce OpenVLA » ?
- Structuration du rapport final : parties I (architecture), II (pipeline Zivid / OpenVLA / UR), III (comparaison).
- Première description technique d’OpenVLA et du positionnement par rapport à la robotique traditionnelle.

### 3. Problèmes et solutions

- Aucun blocage majeur documenté.

### 4. Livrables

- OpenVLA_day01_stage_CCNB.docx — parties I à III, figures 1–4.
- README du dépôt — journal de bord (Jour 01).

### 5. Prochaine étape

Étudier l’architecture OpenVLA en détail et installer openvla-7b sur le poste Windows.

---

## Jour 02 — Prise en main OpenVLA

**Date :** 15 mai 2026 (vendredi)

### 1. Objectif du jour

Comprendre la boucle Vision–Langage–Action (VLA) et mettre en place l’environnement d’inférence openvla-7b sous Windows 11 Pro.

### 2. Réalisations

- Veille : encodeur visuel (SigLIP / DINOv2), projecteur MLP, LLM Llama 2 (> 95 % des poids).
- Installation Conda env_openvla (Python 3.11), transformers==4.40.1, PyTorch CUDA, Hugging Face.
- Téléchargement et test de chargement du modèle openvla-7b (~15 Go VRAM en FP16).
- Comparaison conceptuelle OpenVLA vs robotique classique (langage, stratégie, adaptation).
- Documentation des commandes et chemins dans scripts/utils.txt.

### 3. Problèmes et solutions

- GPU RTX 5090 (Blackwell sm_120) non supporté par PyTorch stable → PyTorch nightly CUDA 12.8 (cu128).
- Version transformers stricte pour OpenVLA → figer transformers==4.40.1.
- Modèle volumineux → chargement float16/bfloat16 sur GPU ≥ 16 Go.

### 4. Livrables

- OpenVLA_day02_prise_en_main.docx
- scripts/integration/test/test_openvla.py (vérification GPU / VRAM)
- scripts/utils.txt

### 5. Prochaine étape

Configurer Conda (Zivid, UR), prendre en main le robot UR et l’API Zivid.

---

## Jour 03 — Robot UR — tracé lettre A

**Date :** 19 mai 2026 (mardi)

### 1. Objectif du jour

Premiers mouvements programmés sur le bras collaboratif UR via URScript (approche sécurisée, tracé géométrique).

### 2. Réalisations

- Définition de 5 poses clés pour tracer la lettre « A » (movej approche/retrait, movel traits linéaires).
- Paramètres de sécurité : vitesse ~0,1 m/s, lift 0,02 m entre segments.
- Scripts URscriptLetterA.script (boucle 1–4 lettres), traceAOnce.script, returnToCenter.script.
- Essai complémentaire sur PolyScope (saisie point par point, sans script complet).

### 3. Problèmes et solutions

- Première prise en main du TCP et des repères → validation pose par pose sur le teach pendant.

### 4. Livrables

- OpenVLA_day03_trace_A.docx
- scripts/ur/*.script (versionnés Git)

### 5. Prochaine étape

Connecter la caméra Zivid MR130 et isoler les environnements Python.

---

## Jour 04 — API Zivid + environnements Conda

**Date :** 20 mai 2026 (mercredi)

### 1. Objectif du jour

Maîtriser la capture 2D/3D Zivid et structurer les environnements Conda par brique logicielle.

### 2. Réalisations

- Connexion Zivid 2+ MR130, acquisition capture_2d_3d.
- Script scripts/zivid/capture.py : export ColorImage.png, Frame.zdf, PointCloud.ply.
- Création de 3 environnements Conda (Python 3.11) : env_zivid, env_ur, env_integration.
- Guide Conda/Anaconda : arborescence, activation, dépendances par module.

### 3. Problèmes et solutions

- Plage de distance MR130 : profondeur bruitée hors zone de travail → respect distance fabricant, bornes Z à la capture.

### 4. Livrables

- OpenVLA_day04_zivid_api.docx
- OpenVLA_day04_conda_anaconda.docx
- scripts/zivid/capture.py

### 5. Prochaine étape

Chaîner capture Zivid et inférence OpenVLA sur GPU.

---

## Jour 05 — OpenVLA + intégration Zivid

**Date :** 21 mai 2026 (jeudi)

### 1. Objectif du jour

Valider la pipeline perception (Zivid) → inférence OpenVLA → prédiction d’actions 7D.

### 2. Réalisations

- Capture Zivid réussie ; conversion RGBA → RGB 224×224 pour l’encodeur visuel.
- Chargement openvla-7b sur GPU ; predict_action (XYZ, rotation, pince).
- Scripts test_openvla.py et test_zivid_openvla.py (consignes texte libres).
- Schéma d’intégration Zivid (SDK) + OpenVLA (transformers) ; connexion UR-RTDE planifiée.

### 3. Problèmes et solutions

- OpenVLA impossible sur Mac (pas de CUDA) → déploiement PC Windows 11 Pro dédié.
- Conflits de dépendances Zivid / UR / OpenVLA → environnements Conda séparés.

### 4. Livrables

- OpenVLA_day05_openvla_integration.docx
- scripts/integration/test/test_openvla.py
- scripts/integration/test/test_zivid_openvla.py

### 5. Prochaine étape

Fermer la boucle avec le UR16e (RTDE) et consolider le rapport final.

---

## Jour 06 — Rapport final + démonstrateur UR/Zivid/OpenVLA

**Date :** 22–23 mai 2026 (vendredi–samedi labo)

### 1. Objectif du jour

Consolider le rapport final (I–III) puis réaliser le premier démonstrateur en boucle fermée sur le robot.

### 2. Réalisations

- 22 mai : édition et consolidation des parties I à III de OpenVLA_day01_stage_CCNB.docx.
- 23 mai : boucle Zivid → OpenVLA → UR16e via demoTest.py (RTDE moveL, lecture TCP, pince digitale).
- Modes SAFE_MODE (simulation des poses) et SCALE max 5 cm/step ; vitesses et accélérations limitées.
- Documentation de l’arborescence scripts/ et des 4 environnements Conda (zivid, ur, integration, openvla).

### 3. Problèmes et solutions

- Risque de mouvements non maîtrisés → SAFE_MODE, SCALE=0,05, vitesses réduites avant essais réels.

### 4. Livrables

- OpenVLA_day06_demo_ur_zivid.docx
- scripts/integration/testUR_ZIVID/demoTest.py
- OpenVLA_day01_stage_CCNB.docx (mise à jour 22 mai)

### 5. Prochaine étape

Ajouter détection 2D (YOLO / Grounding DINO) et projection 3D dans la pipeline.

---

## Jour 07 — Données robot, YOLO, Grounding DINO

**Date :** 25 mai 2026 (lundi)

### 1. Objectif du jour

Clarifier le flux Zivid → détection 2D → OpenVLA → UR et comparer YOLOv8n vs Grounding DINO.

### 2. Réalisations

- Pipeline commun : RGB + nuage → (u,v) → (X,Y,Z) → prompt OpenVLA → predict_action → RTDE.
- YOLOv8n : classes COCO, coordonnées XYZ injectées dans le prompt.
- Grounding DINO : open-vocabulary (ex. cell phone.), projection 3D pour le contrôleur.
- Scripts zivid_yolo_openvla.py, test_zivid_groundingDino.py, returnAllPositions.py.
- Mise à jour rapport final : sections II.1.1, II.1.2, II.1.3.

### 3. Problèmes et solutions

- Résolutions 2D ≠ 3D Zivid → attention au scale_u / scale_v pour la projection (préparation jour 10).

### 4. Livrables

- OpenVLA_day07_robot_data.docx
- scripts/openVLA_ZIVID/test/*.py
- yolov8n.pt

### 5. Prochaine étape

Boucle continue adaptative (réinférence à chaque nouvelle image).

---

## Jour 08 — Boucle continue (OpenVLA adaptatif)

**Date :** 26 mai 2026 (mardi)

### 1. Objectif du jour

Tester une boucle perception → action → réinférence pour correction itérative avec Grounding DINO.

### 2. Réalisations

- Scripts demo_adaptatif_openvla.py (DINO + UR + boucle) et demo_adaptatif_openvla_print_value.py (simulation, logs).
- Injection optionnelle des coordonnées (X,Y,Z) DINO + Zivid dans le prompt (comme variante YOLO).
- Mise à jour rapport final II.5 (boucle continue + injection XYZ).

### 3. Problèmes et solutions

- Premiers signes d’oscillation possible → prévoir SCALE réduit et filtrage profondeur (jour 09–10).

### 4. Livrables

- OpenVLA_day08_boucle_continue.docx
- scripts/integration/test/demo_adaptatif_openvla*.py

### 5. Prochaine étape

Collecter métriques, interpréter convergence / divergence, documenter résultats.

---

## Jour 09 — Tests, interprétation et rapports

**Date :** 27 mai 2026 (mercredi)

### 1. Objectif du jour

Valider et analyser la boucle adaptative ; interpréter l’impact des coordonnées DINO et de la projection 3D.

### 2. Réalisations

- Procédure : demo_adaptatif_openvla_print_value.py (itération, XYZ DINO, delta OpenVLA, TCP, distance, pince).
- Essais robot avec SAFE_MODE via demo_adaptatif_openvla.py.
- Métriques : distance euclidienne d_t, itérations jusqu’à convergence, stabilité Z, multi-détections DINO.
- Interprétation : convergence monotone, offset constant (calibration TCP), divergence (SCALE / détection).
- Appendice II.5 du rapport final avec résultats.

### 3. Problèmes et solutions

- Bruit Z sur nuage Zivid → moyenne locale / filtre profondeur envisagés.
- Oscillation autour d’un offset → hypothèse calibration TCP / transform (traité jour 11).

### 4. Livrables

- OpenVLA_day09_boucle_results.docx
- OpenVLA_day01_stage_CCNB.docx (II.5)

### 5. Prochaine étape

Refactoriser en modules pipeline/ et sécuriser workspace + calibration.

---

## Jour 10 — Refactoring pipeline (modules indépendants)

**Date :** 28 mai 2026 (jeudi)

### 1. Objectif du jour

Découper le démonstrateur en modules réutilisables ; corriger bugs majeurs (calibration, workspace, DINO).

### 2. Réalisations

- Dossier pipeline/ : config, calibration, zivid_capture, dino_detector, ur_controller, gripper, vla_controller.
- main_real.py (robot réel), main_sim.py (dry-run), calibrer_robot.py (génération T_tcp_cam.npy).
- Règles : calibration main-œil obligatoire, bornes workspace, réintégration DINO toutes les N étapes.
- Prompt dynamique basé sur distance TCP→objet (deltas) plutôt que coordonnées absolues.

### 3. Problèmes et solutions

- IndexError dino_detector (u,v) hors nuage → scale_u/scale_v + clipping des indices.
- Dérive boucle continue → réinférence périodique DINO + réduction SCALE.

### 4. Livrables

- OpenVLA_day10_refactoring_pipeline.docx
- pipeline/*.py

### 5. Prochaine étape

Calibration eye-in-hand et rapport hebdomadaire semaine 3.

---

## Jour 11 — Rapport hebdomadaire + calibration main-œil

**Date :** 29 mai 2026 (vendredi)

### 1. Objectif du jour

Produire le rapport hebdomadaire (semaine 26–29 mai) et générer T_tcp_cam.npy (hand-eye Zivid).

### 2. Réalisations

- Rapport Semaine_03_25-29_mai_2026.docx dans rapports_hebdomadaires/.
- calibrer_robot.py : poses variées, mire Zivid, detect_feature_points, calibrate_eye_in_hand, np.save.
- calibration.py : load_calibration(), cam_to_robot(), compute_distance_tcp_to_object().
- Règles de pose : inclinaison ±15–25°, hauteur Z 40–60 cm, rotation RZ.
- Rapport final : section II.6 Jour 11.

### 3. Problèmes et solutions

- Sans T_tcp_cam, repère caméra ≠ repère robot → script autonome de calibration avant main_real.

### 4. Livrables

- OpenVLA_day11_rapport_hebdomadaire.docx
- rapports_hebdomadaires/Semaine_03_25-29_mai_2026.docx
- pipeline/calibrer_robot.py, pipeline/calibration.py

### 5. Prochaine étape

Tests réels du démonstrateur avec calibration et validation workspace.

---

## Jour 12 — Test réel du démonstrateur Zivid / OpenVLA

**Date :** 1 juin 2026 (lundi)

### 1. Objectif du jour

Exécuter et valider la chaîne complète sur la cellule UR16e : capture Zivid, inférence OpenVLA, mouvements RTDE avec calibration T_tcp_cam et bornes de sécurité.

### 2. Réalisations

- (Prévu) Lancer test_zivid_openvla.py — validation capture + inférence sans robot.
- (Prévu) Lancer demoTest.py puis pipeline/main_real.py avec T_tcp_cam.npy chargé.
- (Prévu) Vérifier SAFE_MODE, SCALE, workspace ; noter distances, convergence pince Robotiq.
- (Prévu) Consigner résultats pour rapport et agenda / semaine 4.

### 3. Problèmes et solutions

- (À compléter après essais) — calibration, profondeur MR130, stabilité DINO en conditions réelles.

### 4. Livrables

- Scripts : test_zivid_openvla.py, demoTest.py, pipeline/main_real.py
- Fichier calibration : T_tcp_cam.npy (si généré)
- Mise à jour agenda + rapport journalier (à rédiger)

### 5. Prochaine étape

Prise d’objet en boucle fermée (DINO + OpenVLA + pince) et poursuite documentation.

---

## Repères calendaires

- 16–18 mai : pause / hors labo
- 24 mai : dimanche | 30–31 mai : week-end
- Rapports hebdo : `rapports_hebdomadaires/Semaine_01` à `Semaine_03`
