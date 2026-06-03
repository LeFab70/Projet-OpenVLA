# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 29 mai 2026
# Fichier     : main_real_debug.py
# Objectif    : DEBUG complet — voir pourquoi robot ne bouge pas
# =============================================================================

from __future__ import annotations

from datetime import datetime
import time

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
)
from .dino_detector import DinoDetector
from .ur_controller import Pose6, URController
from .vla_controller import VLAController
from .zivid_capture import capture, init_camera, save_capture


def main() -> None:
    print("\n" + "=" * 70)
    print("PIPELINE DEBUG — Diagnostic robot")
    print("=" * 70)

    # Vérifier config
    print("\n[CONFIG]")
    print(f"  ROBOT_IP : {ROBOT_IP}")
    print(f"  ROBOT_SPEED : {ROBOT_SPEED}")
    print(f"  ROBOT_ACCEL : {ROBOT_ACCEL}")
    print(f"  SCALE : {SCALE}")
    print(f"  WORKSPACE : {WORKSPACE}")

    if WORKSPACE is None:
        raise RuntimeError("WORKSPACE absent")

    run_dir = RUNS_DIR / datetime.now().strftime("%Y%m%d_%H%M%S_debug")
    run_dir.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────
    # TEST CONNEXION ROBOT
    # ─────────────────────────────────────────
    print("\n[ROBOT] Initialisation...")
    ur = URController(
        ROBOT_IP,
        WORKSPACE,
        safe_mode=False,
        speed=ROBOT_SPEED,
        accel=ROBOT_ACCEL,
    )

    print("[ROBOT] Tentative de connexion...")
    try:
        ur.connect()
        print("✅ [ROBOT] Connecté !")
    except Exception as e:
        print(f"❌ [ROBOT] Erreur connexion : {e}")
        return

    # Test pose actuelle
    print("\n[ROBOT] Lecture pose initiale...")
    try:
        pose = ur.get_tcp_pose()
        print(f"✅ Pose initiale : x={pose.x:.3f} y={pose.y:.3f} z={pose.z:.3f}")
        print(f"                  rx={pose.rx:.3f} ry={pose.ry:.3f} rz={pose.rz:.3f}")
    except Exception as e:
        print(f"❌ Erreur lecture pose : {e}")
        ur.disconnect()
        return

    # ─────────────────────────────────────────
    # TEST MOUVEMENT SIMPLE
    # ─────────────────────────────────────────
    print("\n[ROBOT] Test mouvement simple (+5cm en Z)...")
    pose_test = Pose6(
        x=pose.x,
        y=pose.y,
        z=pose.z + 0.05,  # +5cm en Z
        rx=pose.rx,
        ry=pose.ry,
        rz=pose.rz,
    )

    print(f"  Pose cible : x={pose_test.x:.3f} y={pose_test.y:.3f} z={pose_test.z:.3f}")

    try:
        print("  → Envoi moveL()...")
        ur.moveL(pose_test)
        print("✅ moveL() complété sans erreur")
        time.sleep(2)  # Attendre le mouvement
    except Exception as e:
        print(f"❌ Erreur moveL() : {e}")
        ur.disconnect()
        return

    # Vérifier si pose a changé
    print("\n[ROBOT] Vérification pose après mouvement...")
    try:
        pose_after = ur.get_tcp_pose()
        print(f"✅ Pose actuelle : x={pose_after.x:.3f} y={pose_after.y:.3f} z={pose_after.z:.3f}")
        
        delta_z = pose_after.z - pose.z
        print(f"   Δz observé : {delta_z:.3f}m (attendu : ~+0.050m)")
        
        if abs(delta_z - 0.05) < 0.01:
            print("✅ ROBOT BOUGE CORRECTEMENT !")
        else:
            print(f"❌ Robot ne s'est pas déplacé comme prévu (Δz={delta_z:.3f}m)")
    except Exception as e:
        print(f"❌ Erreur lecture pose : {e}")

    ur.disconnect()

    # ─────────────────────────────────────────
    # PIPELINE COMPLET AVEC DEBUG
    # ─────────────────────────────────────────
    if input("\nContinuer avec pipeline complet ? (oui/non) : ").lower() != "oui":
        return

    print("\n[PIPELINE] Démarrage...")

    ur.connect()

    try:
        text_prompt = input("\n🔎 Objet à saisir : ").strip()

        _, camera = init_camera()
        dino = DinoDetector(
            model_id=DINO_MODEL_ID,
            box_threshold=BOX_THRESHOLD,
            text_threshold=TEXT_THRESHOLD,
            device="cuda:0",
            save_dir=run_dir,
        )
        vla = VLAController(MODEL_PATH, "cuda:0", UNNORM_KEY)

        # Détection
        print("\n[DINO] Capture initiale...")
        image_rgb, pc_mm = capture(camera)
        save_capture(image_rgb, filename="dino_initial.png")

        print("[DINO] Détection en cours...")
        det = dino.detect(image_rgb, pc_mm, text_prompt)

        if det is None:
            print(f"❌ Aucune détection pour '{text_prompt}'")
            return

        label = det.label
        target_cam = np.array(det.point_cam_m)

        print(f"✅ Détecté : {label}")
        print(f"   Coordonnées caméra : X={target_cam[0]:.3f}m Y={target_cam[1]:.3f}m Z={target_cam[2]:.3f}m")

        # Boucle principale
        print("\n[PIPELINE] Boucle moteur...\n")

        for step in range(1, MAX_STEPS + 1):
            if step == 1 or (DINO_EVERY_N_STEPS > 0 and step % DINO_EVERY_N_STEPS == 0):
                image_rgb, pc_mm = capture(camera)
                det2 = dino.detect(image_rgb, pc_mm, text_prompt)
                if det2 is not None:
                    target_cam = np.array(det2.point_cam_m)

            # Pose actuelle
            tcp = ur.get_tcp_pose()
            tcp_xyz = np.array([tcp.x, tcp.y, tcp.z], dtype=float)

            remaining = target_cam - tcp_xyz
            dist = float(np.linalg.norm(remaining))

            prompt = vla.build_prompt_dynamic(label, tuple(remaining.tolist()))
            image_rgb, _ = capture(camera)
            action = vla.predict_action(prompt, image_rgb)

            # NOUVEAU POSE
            new_pose = Pose6(
                x=tcp.x + action.dx * SCALE,
                y=tcp.y + action.dy * SCALE,
                z=tcp.z + action.dz * SCALE,
                rx=tcp.rx + action.rx * SCALE,
                ry=tcp.ry + action.ry * SCALE,
                rz=tcp.rz + action.rz * SCALE,
            )

            # DEBUG : Afficher déplacement réel
            delta_x = action.dx * SCALE
            delta_y = action.dy * SCALE
            delta_z = action.dz * SCALE

            print(
                f"STEP {step:02d} | "
                f"dist={dist:.3f}m | "
                f"ΔP=({delta_x:+.4f},{delta_y:+.4f},{delta_z:+.4f}m) | "
                f"gripper={action.gripper:.3f}"
            )

            # Mouvement
            try:
                ur.moveL(new_pose)
                print(f"          → moveL() envoyé ✅")
            except Exception as e:
                print(f"          → ❌ Erreur moveL() : {e}")
                break

            if dist < 0.05 and action.gripper < GRIPPER_THRESHOLD and step > 2:
                print(f"\n🏁 FIN : proche cible")
                break

    finally:
        ur.disconnect()
        print("\n✅ Déconnecté")


if __name__ == "__main__":
    main()