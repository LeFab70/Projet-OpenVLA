#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère agenda_quotidien_Fabrice.docx (en-tête rapports hebdomadaires, blocs par semaine)."""

import shutil
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

DIR = Path(__file__).resolve().parent
ROOT = DIR.parent
TEMPLATE = ROOT / "rapports_hebdomadaires" / "Semaine_01_14-15_mai_2026.docx"
LOGO = ROOT / "media" / "ccnb_innov_logo.jpeg"
OUT_DOCX = DIR / "agenda_quotidien_Fabrice.docx"
OUT_MD = DIR / "agenda_quotidien_Fabrice.md"

HEADER_PARA_COUNT = 6
SUPERVISEUR = "Guillaume Batungwanayo"
STAGIAIRE = "Fabrice Kouonang"

SEMAINES = [
    {
        "num": 1,
        "periode": "jeudi 14 au vendredi 15 mai 2026",
        "jours": "01–02",
        "objectif": (
            "Cadrer le stage CCNB-INNOV, le démonstrateur OpenVLA (UR + Zivid 2+ MR130) "
            "et installer l’environnement d’inférence openvla-7b."
        ),
        "jours_list": [
            {
                "num": "01",
                "titre": "Début de stage CCNB-INNOV",
                "date": "14 mai 2026 (jeudi)",
                "objectif": "Cadrage du sujet, objectifs, rapport final (parties I à III).",
                "realisations": [
                    "Question directrice : ingrédients de la « sauce OpenVLA » (VLA vs robotique classique).",
                    "Rapport final : I — architecture (SigLIP/DINOv2 + MLP + Llama 2 7B), II — pipeline Zivid / OpenVLA / UR16e, III — comparaison programmation / perception / contrôle.",
                    "Schéma des flux : image 224×224 + prompt texte → vecteur d’action 7D (ΔXYZ, rotation, gripper).",
                ],
                "prochaine": "Installation openvla-7b et tests GPU sous Windows.",
            },
            {
                "num": "02",
                "titre": "Prise en main OpenVLA",
                "date": "15 mai 2026 (vendredi)",
                "objectif": "Mettre en place env_openvla et valider le chargement du modèle sur GPU NVIDIA.",
                "realisations": [
                    "Conda Python 3.11 : env_openvla, transformers==4.40.1, PyTorch nightly cu128 (RTX 5090 / sm_120).",
                    "Téléchargement Hugging Face openvla/openvla-7b (~15 Go VRAM, inférence FP16/bfloat16).",
                    "test_openvla.py : vérification CUDA, VRAM et predict_action.",
                    "Boucle VLA documentée : encodeur visuel → fusion langage → tête d’action discrète continue.",
                ],
                "prochaine": "Environnements Conda Zivid/UR et premiers URScript.",
            },
        ],
    },
    {
        "num": 2,
        "periode": "mardi 19 au vendredi 22 mai 2026",
        "jours": "03–06",
        "objectif": (
            "Maîtriser URScript, API Zivid MR130, pipeline Zivid→OpenVLA, "
            "puis boucle fermée Zivid→OpenVLA→UR16e (RTDE)."
        ),
        "jours_list": [
            {
                "num": "03",
                "titre": "Robot UR — tracé lettre A",
                "date": "19 mai 2026 (mardi)",
                "objectif": "Programmer le UR en URScript (movej / movel) avec paramètres de sécurité.",
                "realisations": [
                    "5 poses TCP pour la lettre « A » : approche movej (lift 0,02 m), traits movel, retrait.",
                    "Vitesse limitée ~0,1 m/s ; scripts URscriptLetterA.script, traceAOnce.script, returnToCenter.script.",
                    "Validation PolyScope : enseignement point à point des poses avant exécution script.",
                ],
                "prochaine": "Capture 2D/3D Zivid et environnements Conda isolés.",
            },
            {
                "num": "04",
                "titre": "API Zivid + Conda",
                "date": "20 mai 2026 (mercredi)",
                "objectif": "Capturer RGB + nuage de points MR130 et isoler les dépendances Python.",
                "realisations": [
                    "Zivid SDK : connexion MR130, capture_2d_3d → ColorImage.png, Frame.zdf, PointCloud.ply (capture.py).",
                    "Environnements Conda 3.11 : env_zivid (zivid, numpy, opencv), env_ur (ur-rtde), env_integration.",
                    "Contrainte distance MR130 : profondeur valide dans la plage fabricant (éviter Z bruité hors workspace optique).",
                ],
                "prochaine": "Inférence OpenVLA sur images Zivid 224×224.",
            },
            {
                "num": "05",
                "titre": "OpenVLA + intégration Zivid",
                "date": "21 mai 2026 (jeudi)",
                "objectif": "Chaîne capture Zivid → prétraitement → predict_action OpenVLA sur GPU.",
                "realisations": [
                    "Conversion RGBA→RGB, redimensionnement 224×224, prompt libre (ex. « pick up the phone »).",
                    "test_zivid_openvla.py : capture live + inférence ; sortie 7D (translation, rotation euler/quat, gripper).",
                    "Poste Windows 11 Pro dédié (CUDA) — OpenVLA non exécutable sur Mac sans GPU NVIDIA.",
                ],
                "prochaine": "Boucle RTDE UR16e avec SAFE_MODE et SCALE.",
            },
            {
                "num": "06",
                "titre": "Rapport final + démonstrateur",
                "date": "22–23 mai 2026",
                "objectif": "Consolider rapport I–III puis demoTest.py : Zivid→OpenVLA→UR16e.",
                "realisations": [
                    "22 mai : édition rapport final (architecture, pipeline, comparaison traditionnelle).",
                    "23 mai : demoTest.py — ur_rtde moveL, getActualTCPPose(), setToolDigitalOut (pince), lecture action OpenVLA.",
                    "SAFE_MODE (affichage sans exécution), SCALE=0,05 m/step max, accélération/vitesse réduites.",
                    "Arborescence scripts/ : zivid/, ur/*.script, integration/testUR_ZIVID/, openVLA_ZIVID/.",
                ],
                "prochaine": "Détection 2D (YOLO / Grounding DINO) + projection (u,v)→(X,Y,Z).",
            },
        ],
    },
    {
        "num": 3,
        "periode": "lundi 25 au vendredi 29 mai 2026",
        "jours": "07–11",
        "objectif": (
            "Perception 2D/3D, boucle adaptative OpenVLA, refactoring pipeline/, "
            "calibration eye-in-hand T_tcp_cam.npy."
        ),
        "jours_list": [
            {
                "num": "07",
                "titre": "YOLO, Grounding DINO, flux 3D",
                "date": "25 mai 2026 (lundi)",
                "objectif": "Comparer YOLOv8n (COCO) et Grounding DINO (open-vocab) avec projection Zivid.",
                "realisations": [
                    "Pipeline : Zivid RGB + point cloud → bbox (u,v) → (X,Y,Z) caméra → prompt → predict_action → RTDE.",
                    "YOLOv8n (yolov8n.pt) : label COCO + XYZ injectés dans le prompt (« pick up the {label} at X=… »).",
                    "Grounding DINO (IDEA-Research/grounding-dino-base) : requête texte libre, XYZ pour contrôleur robot.",
                    "Scripts : zivid_yolo_openvla.py, test_zivid_groundingDino.py, returnAllPositions.py.",
                ],
                "prochaine": "Boucle continue perception→action→réinférence.",
            },
            {
                "num": "08",
                "titre": "Boucle continue OpenVLA adaptatif",
                "date": "26 mai 2026 (mardi)",
                "objectif": "Itérer capture→inférence→mouvement avec réobservation à chaque cycle.",
                "realisations": [
                    "demo_adaptatif_openvla.py : DINO + boucle UR ; demo_adaptatif_openvla_print_value.py : logs sans robot.",
                    "Prompt enrichi optionnel : coordonnées (X,Y,Z) projetées depuis DINO + nuage Zivid (comme variante YOLO).",
                    "Paramètres SAFE_MODE, SCALE, seuil de convergence sur distance TCP–objet.",
                ],
                "prochaine": "Métriques d_t, convergence, analyse des oscillations.",
            },
            {
                "num": "09",
                "titre": "Tests et interprétation",
                "date": "27 mai 2026 (mercredi)",
                "objectif": "Quantifier la boucle adaptative (simulation puis robot en SAFE_MODE).",
                "realisations": [
                    "Logs par itération : bbox DINO, (X,Y,Z), delta OpenVLA, pose TCP, distance euclidienne d_t, état pince.",
                    "Critères : convergence si d_t < seuil ; oscillation → calibration TCP ; divergence → SCALE ou détection instable.",
                    "Filtrage profondeur Z (moyenne locale sur nuage) pour réduire le bruit MR130.",
                ],
                "prochaine": "Modulariser en pipeline/ (config, calibration, détecteurs, UR, VLA).",
            },
            {
                "num": "10",
                "titre": "Refactoring pipeline/",
                "date": "28 mai 2026 (jeudi)",
                "objectif": "Modules indépendants + workspace + prompt relatif (deltas).",
                "realisations": [
                    "pipeline/ : config.py (SAFE_MODE, SCALE, Z_MIN/Z_MAX), zivid_capture, dino_detector (scale_u/v, clip indices), ur_controller, vla_controller, gripper.",
                    "main_real.py / main_sim.py ; calibrer_robot.py pour T_tcp_cam.npy (hand-eye).",
                    "Réinférence DINO toutes les N itérations ; prompt basé sur vecteur TCP→objet plutôt qu’absolu.",
                ],
                "prochaine": "Calibration mire Zivid et np.save(T_tcp_cam).",
            },
            {
                "num": "11",
                "titre": "Calibration main-œil + rapport hebdo",
                "date": "29 mai 2026 (vendredi)",
                "objectif": "Générer T_tcp_cam (4×4) et documenter conversion caméra→base robot.",
                "realisations": [
                    "calibrer_robot.py : poses variées (inclinaison RX/RY ±15–25°, Z 40–60 cm, rotation RZ), detect_feature_points, calibrate_eye_in_hand.",
                    "calibration.py : load_calibration(), cam_to_robot(), compute_distance_tcp_to_object().",
                    "Matrice homogène T_tcp_cam : point caméra → repère base UR16e pour moveL cohérents.",
                ],
                "prochaine": "Essais réels main_real.py avec calibration chargée.",
            },
        ],
    },
    {
        "num": 4,
        "periode": "lundi 1 juin 2026",
        "jours": "12",
        "objectif": "Valider le démonstrateur complet sur cellule (Zivid + OpenVLA + UR16e + pince).",
        "jours_list": [
            {
                "num": "12",
                "titre": "Test réel du démonstrateur",
                "date": "1 juin 2026 (lundi)",
                "objectif": "Exécution bout en bout avec T_tcp_cam.npy, workspace et SAFE_MODE.",
                "realisations": [
                    "(Prévu) test_zivid_openvla.py : capture MR130 + inférence 224×224 sans RTDE.",
                    "(Prévu) demoTest.py puis pipeline/main_real.py : DINO → OpenVLA → moveL, bornes workspace.",
                    "(Prévu) Vérification SCALE, getActualTCPPose(), pince Robotiq ; journalisation d_t et itérations.",
                ],
                "prochaine": "Prise d’objet en boucle fermée et documentation semaine 4.",
            },
        ],
    },
]


def _set_paragraph_text(paragraph, text):
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def _clear_body_after_header(doc):
    for para in reversed(doc.paragraphs[HEADER_PARA_COUNT:]):
        para._element.getparent().remove(para._element)


def _add_h1(doc, text):
    try:
        return doc.add_paragraph(text, style="Heading1")
    except KeyError:
        return doc.add_paragraph(text, style="Heading 1")


def _add_bullets(doc, items, style="ListBullet"):
    for item in items:
        if item:
            try:
                doc.add_paragraph(item, style=style)
            except KeyError:
                doc.add_paragraph(item, style="List Bullet")


def _add_run_paragraph(doc, text, bold=True, size_half_pt=22):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(size_half_pt / 2)
    return p


def _load_document_from_template():
    if TEMPLATE.is_file():
        tmp = DIR / "_tmp_template.docx"
        shutil.copy(TEMPLATE, tmp)
        doc = Document(str(tmp))
        tmp.unlink(missing_ok=True)
        _clear_body_after_header(doc)
        _set_paragraph_text(doc.paragraphs[1], "Projet OpenVLA — Agenda quotidien")
        _set_paragraph_text(doc.paragraphs[2], f"Par : {STAGIAIRE}")
        _set_paragraph_text(doc.paragraphs[4], f"Superviseur direct : {SUPERVISEUR}")
        _set_paragraph_text(
            doc.paragraphs[5], "Période : 14 mai au 1 juin 2026 | Jours 01–12"
        )
        return doc
    doc = Document()
    if LOGO.is_file():
        p = doc.add_paragraph()
        p.alignment = 1
        p.add_run().add_picture(str(LOGO), width=Inches(2.8))
    _add_run_paragraph(doc, "Projet OpenVLA — Agenda quotidien", bold=True, size_half_pt=28)
    _add_run_paragraph(doc, f"Par : {STAGIAIRE}", bold=False, size_half_pt=22)
    _add_run_paragraph(doc, "—" * 28, bold=False, size_half_pt=20)
    _add_run_paragraph(doc, f"Superviseur direct : {SUPERVISEUR}", bold=False, size_half_pt=22)
    _add_run_paragraph(
        doc, "Période : 14 mai au 1 juin 2026 | Jours 01–12", bold=False, size_half_pt=20
    )
    return doc


def _add_jour(doc, jour):
    _add_run_paragraph(
        doc, f"Jour {jour['num']} — {jour['titre']}", bold=True, size_half_pt=24
    )
    _add_run_paragraph(doc, f"Date : {jour['date']}", bold=False, size_half_pt=20)
    _add_h1(doc, "1. Objectif du jour")
    _add_bullets(doc, [jour["objectif"]])
    _add_h1(doc, "2. Réalisations")
    _add_bullets(doc, jour["realisations"])
    _add_h1(doc, "3. Prochaine étape")
    _add_bullets(doc, [jour["prochaine"]])


def build():
    doc = _load_document_from_template()
    first_block = True

    for semaine in SEMAINES:
        if not first_block:
            doc.add_page_break()
        first_block = False

        _add_run_paragraph(
            doc,
            f"Semaine {semaine['num']} — {semaine['periode']} | Jours {semaine['jours']}",
            bold=True,
            size_half_pt=28,
        )
        _add_h1(doc, "Objectif de la semaine")
        _add_bullets(doc, [semaine["objectif"]])

        for j, jour in enumerate(semaine["jours_list"]):
            if j > 0:
                doc.add_paragraph()
            _add_jour(doc, jour)

    doc.save(OUT_DOCX)
    print(f"Écrit : {OUT_DOCX}")


def build_md():
    lines = [
        "# Agenda quotidien — Stage OpenVLA",
        "",
        f"**Programmeur :** {STAGIAIRE}  ",
        "**Document Word :** `agenda_quotidien_Fabrice.docx`",
        "",
        f"**Superviseur :** {SUPERVISEUR}",
        "",
        "---",
        "",
    ]
    for semaine in SEMAINES:
        lines += [
            f"## Semaine {semaine['num']} — {semaine['periode']} (jours {semaine['jours']})",
            "",
            f"**Objectif de la semaine :** {semaine['objectif']}",
            "",
        ]
        for jour in semaine["jours_list"]:
            lines += [
                f"### Jour {jour['num']} — {jour['titre']}",
                "",
                f"**Date :** {jour['date']}",
                "",
                "#### 1. Objectif du jour",
                "",
                jour["objectif"],
                "",
                "#### 2. Réalisations",
                "",
            ]
            lines += [f"- {r}" for r in jour["realisations"]]
            lines += [
                "",
                "#### 3. Prochaine étape",
                "",
                jour["prochaine"],
                "",
            ]
        lines.append("---\n")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Écrit : {OUT_MD}")


if __name__ == "__main__":
    build()
    build_md()
