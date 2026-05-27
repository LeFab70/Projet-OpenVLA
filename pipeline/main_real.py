# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : main_real.py
# Objectif    : Script 1 — robot réel (UR16e) : boucle Zivid → DINO → OpenVLA avec sécurité
# =============================================================================

from __future__ import annotations

from datetime import datetime

import numpy as np

from . import calibration
from .config import (
    APPROACH_ACCEL,
    APPROACH_SPEED,
    APPROACH_Z,
    BOX_THRESHOLD,
    DINO_EVERY_N_STEPS,
    DINO_MODEL_ID,
    GRIPPER_THRESHOLD,
    MAX_STEPS,
    MODEL_PATH,
    ROBOT_ACCEL,
    ROBOT_IP,
    ROBOT_SPEED,
    RUNS_DIR,
    SCALE,
    TEXT_THRESHOLD,
    UNNORM_KEY,
    WORKSPACE,
)
from .dino_detector import DinoDetector
from .ur_controller import Pose6, URController
from .vla_controller import VLAController
from .zivid_capture import init_camera, capture


def main() -> None:
    safe_mode = False
    if WORKSPACE is None:
        raise RuntimeError("WORKSPACE absent (dangereux).")

    # 1&2&3: calibration main-œil absente = bug majeur en réel
    T_tcp_cam, is_real = calibration.load_calibration()
    if not is_real:
        raise RuntimeError(
            "CALIBRATION ABSENTE: impossible d'utiliser caméra→robot de façon fiable en mode réel."
        )

    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S_real")
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PIPELINE RÉEL — Zivid → DINO → OpenVLA → UR16e (+ pince)")
    print("=" * 60)

    text_prompt = input("🔎 Objet à saisir : ").strip()

    _, camera = init_camera()
    dino = DinoDetector(
        model_id=DINO_MODEL_ID,
        box_threshold=BOX_THRESHOLD,
        text_threshold=TEXT_THRESHOLD,
        device="cuda:0",
        save_dir=run_dir,
    )
    vla = VLAController(MODEL_PATH, "cuda:0", UNNORM_KEY)

    ur = URController(ROBOT_IP, WORKSPACE, safe_mode=safe_mode, speed=ROBOT_SPEED, accel=ROBOT_ACCEL)
    ur.connect()

    try:
        # Détection initiale
        image_rgb, pc_mm = capture(camera)
        det = dino.detect(image_rgb, pc_mm, text_prompt)
        if det is None:
            raise RuntimeError(f"Aucune détection DINO pour '{text_prompt}'")

        label = det.label

        # cible en base UR (cam -> base via base->tcp + tcp->cam)
        tcp_pose_list = ur.get_tcp_pose().as_list()
        target_base = calibration.cam_to_robot(np.array(det.point_cam_m), tcp_pose_list, T_tcp_cam)

        print(
            f"✅ DINO: {label} conf={det.conf:.2f} uv={det.pixel_uv} camXYZ={det.point_cam_m} baseXYZ=({target_base[0]:.3f},{target_base[1]:.3f},{target_base[2]:.3f})"
        )

        for step in range(1, MAX_STEPS + 1):
            # 4) Réintégrer DINO périodiquement pour corriger dérive
            if step == 1 or (DINO_EVERY_N_STEPS > 0 and step % DINO_EVERY_N_STEPS == 0):
                image_rgb, pc_mm = capture(camera)
                det2 = dino.detect(image_rgb, pc_mm, text_prompt)
                if det2 is not None:
                    det = det2
                    tcp_pose_list = ur.get_tcp_pose().as_list()
                    target_base = calibration.cam_to_robot(np.array(det.point_cam_m), tcp_pose_list, T_tcp_cam)

            tcp = ur.get_tcp_pose()
            tcp_xyz = np.array([tcp.x, tcp.y, tcp.z], dtype=float)
            remaining = target_base - tcp_xyz

            prompt = vla.build_prompt_dynamic(label, tuple(remaining.tolist()))

            image_rgb, _ = capture(camera)
            action = vla.predict_action(prompt, image_rgb)

            new_pose = Pose6(
                x=tcp.x + action.dx * SCALE,
                y=tcp.y + action.dy * SCALE,
                z=tcp.z + action.dz * SCALE,
                rx=tcp.rx + action.rx * SCALE,
                ry=tcp.ry + action.ry * SCALE,
                rz=tcp.rz + action.rz * SCALE,
            )

            ur.moveL(new_pose)

            dist = float(np.linalg.norm(remaining))
            print(
                f"STEP {step:02d} dist={dist:.3f}m action(dx,dy,dz)=({action.dx:+.3f},{action.dy:+.3f},{action.dz:+.3f}) gripper={action.gripper:.3f}"
            )

            # arrêt simple
            if dist < 0.03 and action.gripper < GRIPPER_THRESHOLD and step > 2:
                print("🏁 FIN: proche cible + gripper<seuil (brancher Robotiq ici)")
                break

    finally:
        ur.disconnect()


if __name__ == "__main__":
    main()

