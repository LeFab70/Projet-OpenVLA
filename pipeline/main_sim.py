# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : main_sim.py
# Objectif    : Script 2 — simulation : boucle Zivid → DINO → OpenVLA (dry-run)
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np

from . import calibration
from .config import (
    BOX_THRESHOLD,
    DINO_EVERY_N_STEPS,
    DINO_MODEL_ID,
    GRIPPER_THRESHOLD,
    MAX_STEPS,
    MODEL_PATH,
    RUNS_DIR,
    SCALE,
    TEXT_THRESHOLD,
    UNNORM_KEY,
    WORKSPACE,
    ZIVID_Z_MAX,
)
from .dino_detector import DinoDetector
from .ur_controller import Pose6, URController
from .vla_controller import VLAController
from .zivid_capture import init_camera, capture, save_capture


@dataclass
class SimState:
    pose: Pose6


def main() -> None:
    safe_mode = True
    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S_sim")
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PIPELINE SIM — Zivid → DINO → OpenVLA (boucle)")
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

    # Simulation : on garde un état pose local
    ur = URController("SIM", WORKSPACE, safe_mode=True, speed=0.0, accel=0.0)
    state = SimState(pose=Pose6(0.45, 0.0, 0.40, 0.0, 3.14, 0.0))

    T_tcp_cam, is_real = calibration.load_calibration()
    if not is_real:
        print("[WARN] Calibration absente (SIM ok, RÉEL bloquant).")

    # Détection initiale
    image_rgb, pc_mm = capture(camera)
    #stockage image pour debug
    save_capture(image_rgb, filename="dino_initial.png")

    
    det = dino.detect(image_rgb, pc_mm, text_prompt)
    if det is None:
        raise RuntimeError(f"Aucune détection DINO pour '{text_prompt}'")

    label = det.label
    # Simulation: on réutilise cam_to_robot avec pose simulée
    target_base = calibration.cam_to_robot(np.array(det.point_cam_m), state.pose.as_list(), T_tcp_cam)

    print(f"✅ DINO: {label} conf={det.conf:.2f} uv={det.pixel_uv} camXYZ={det.point_cam_m}")

    for step in range(1, MAX_STEPS + 1):
        # 4) Réintégrer DINO périodiquement pour corriger dérive (même en SIM)
        if step == 1 or (DINO_EVERY_N_STEPS > 0 and step % DINO_EVERY_N_STEPS == 0):
            image_rgb, pc_mm = capture(camera)
            # save image pour debug
           
            save_capture(image_rgb, filename=f"dino_step{step:02d}.png")
            det2 = dino.detect(image_rgb, pc_mm, text_prompt)
            if det2 is not None:
                det = det2
                target_base = calibration.cam_to_robot(np.array(det.point_cam_m), state.pose.as_list(), T_tcp_cam)

        tcp_xyz = np.array([state.pose.x, state.pose.y, state.pose.z], dtype=float)
        remaining = target_base - tcp_xyz
        prompt = vla.build_prompt_dynamic(label, tuple(remaining.tolist()))
        image_rgb, _ = capture(camera)
        action = vla.predict_action(prompt, image_rgb)

        new_pose = Pose6(
            x=state.pose.x + action.dx * SCALE,
            y=state.pose.y + action.dy * SCALE,
            z=state.pose.z + action.dz * SCALE,
            rx=state.pose.rx + action.rx * SCALE,
            ry=state.pose.ry + action.ry * SCALE,
            rz=state.pose.rz + action.rz * SCALE,
        )

        # workspace safety (même en SIM)
        ur.moveL(new_pose)
        state.pose = new_pose

        dist = float(np.linalg.norm(remaining))
        print(
            f"STEP {step:02d} dist={dist:.3f}m action(dx,dy,dz)=({action.dx:+.3f},{action.dy:+.3f},{action.dz:+.3f}) gripper={action.gripper:.3f}"
        )

        # arrêt simple : proche + gripper ferme
        # ici on s'arrete si proche cible + gripper fermé (dans la réalité, on brancherait la commande de la pince Robotiq ici)
        if dist < 0.03 and action.gripper < GRIPPER_THRESHOLD and step > 2:
            print("🏁 FIN (SIM): proche cible + gripper<seuil")
            break


if __name__ == "__main__":
    main()

