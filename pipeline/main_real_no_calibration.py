# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 29 mai 2026
# Fichier     : main_real_no_calib.py
# Objectif    : Test du pipeline SANS calibration — utiliser coords caméra directement
# =============================================================================

from __future__ import annotations

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
    ROBOT_ACCEL,
    ROBOT_IP,
    ROBOT_SPEED,
    RUNS_DIR,
    SCALE,
    TEXT_THRESHOLD,
    UNNORM_KEY,
    WORKSPACE,
    T_TCP_CAM_DEFAULT,
)
from .dino_detector import DinoDetector
from .ur_controller import Pose6, URController
from .vla_controller import VLAController
from .zivid_capture import capture, init_camera, save_capture


def main() -> None:
    safe_mode = False

    if WORKSPACE is None:
        raise RuntimeError("WORKSPACE absent (dangereux).")

    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S_real_no_calib")
    run_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("PIPELINE TEST — SANS calibration")
    print("Utilisation directe des coordonnées caméra DINO")
    print("=" * 60)
    print("⚠️  MODE TEST : Les coordonnées ne sont pas converties")
    print("    robot - c'est juste pour valider le reste du pipeline")
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

    ur = URController(
        ROBOT_IP,
        WORKSPACE,
        safe_mode=safe_mode,
        speed=ROBOT_SPEED,
        accel=ROBOT_ACCEL,
    )
    ur.connect()

    try:
        # ─────────────────────────────────────────
        # DÉTECTION INITIALE
        # ─────────────────────────────────────────
        image_rgb, pc_mm = capture(camera)
        save_capture(image_rgb, filename="dino_initial.png")
        det = dino.detect(image_rgb, pc_mm, text_prompt)

        if det is None:
            raise RuntimeError(f"Aucune détection DINO pour '{text_prompt}'")

        label = det.label

        # ❌ NE PAS convertir cam→robot pour l'instant
        # ✅ Utiliser les coordonnées caméra directement
        # Celles-ci sont en mètres dans le repère caméra
        target_cam = np.array(det.point_cam_m)  # (X, Y, Z) en mètres

        print(f"\n✅ DINO détecté : {label}")
        print(f"   Confiance : {det.conf:.2f}")
        print(f"   Pixel (u,v) : {det.pixel_uv}")
        print(f"   Coordonnées CAMÉRA : X={target_cam[0]:.3f}m "
              f"Y={target_cam[1]:.3f}m Z={target_cam[2]:.3f}m")
        print("\n⚠️  TEST MODE : pas de conversion vers coords robot")
        print("   Les mouvements du robot seront basés sur coords caméra (imprécis)")

        # ─────────────────────────────────────────
        # BOUCLE PRINCIPALE
        # ─────────────────────────────────────────
        for step in range(1, MAX_STEPS + 1):
            # Réintégrer DINO périodiquement pour corriger dérive
            if step == 1 or (
                DINO_EVERY_N_STEPS > 0 and step % DINO_EVERY_N_STEPS == 0
            ):
                image_rgb, pc_mm = capture(camera)
                save_capture(image_rgb, filename=f"dino_step{step:02d}.png")

                det2 = dino.detect(image_rgb, pc_mm, text_prompt)
                if det2 is not None:
                    det = det2
                    target_cam = np.array(det.point_cam_m)
                    print(f"\n  [STEP {step}] DINO réintégré : {det.label}")

            # Position TCP actuelle
            tcp = ur.get_tcp_pose()
            tcp_xyz = np.array([tcp.x, tcp.y, tcp.z], dtype=float)

            # Distance restante (coords caméra, pas robot — c'est imprécis)
            remaining = target_cam - tcp_xyz
            dist = float(np.linalg.norm(remaining))

            # Build prompt avec distance restante
            prompt = vla.build_prompt_dynamic(label, tuple(remaining.tolist()))

            # Inférence OpenVLA
            image_rgb, _ = capture(camera)
            action = vla.predict_action(prompt, image_rgb)

            # Appliquer action au robot
            new_pose = Pose6(
                x=tcp.x + action.dx * SCALE,
                y=tcp.y + action.dy * SCALE,
                z=tcp.z + action.dz * SCALE,
                rx=tcp.rx + action.rx * SCALE,
                ry=tcp.ry + action.ry * SCALE,
                rz=tcp.rz + action.rz * SCALE,
            )

            # Mouvement robot
            ur.moveL(new_pose)

            # Log
            print(
                f"STEP {step:02d} | "
                f"dist={dist:.3f}m | "
                f"action(dx,dy,dz)=({action.dx:+.4f},"
                f"{action.dy:+.4f},{action.dz:+.4f}) | "
                f"gripper={action.gripper:.3f}"
            )

            # Arrêt si proche cible et gripper fermé
            if dist < 0.05 and action.gripper < GRIPPER_THRESHOLD and step > 2:
                print(f"\n🏁 FIN : proche cible + gripper<seuil")
                print(f"   Distance finale : {dist:.3f}m")
                break

    except RuntimeError as e:
        print(f"\n❌ Erreur robot : {e}")
        print("   Vérifier que le robot est en mode AUTO et accessible")

    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()

    finally:
        ur.disconnect()
        print("\n✅ Robot déconnecté")


if __name__ == "__main__":
    main()