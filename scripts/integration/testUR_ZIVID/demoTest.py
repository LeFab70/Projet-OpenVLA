# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 29 mai 2026
# Objectif    : OpenVLA + DINO — s'approcher jusqu'à proximité bouteille
# =============================================================================

from transformers import AutoModelForVision2Seq, AutoProcessor
from PIL import Image
import zivid
import numpy as np
import torch
import rtde_control
import rtde_receive
import os
import time

# ─────────────────────────────────────────
# ⚙️ CONFIG
# ─────────────────────────────────────────
ROBOT_IP = "10.146.97.7"
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"

INSTRUCTION = "pick up the bottle"
SCALE = 2.0        # Amplification actions
SPEED = 0.05         # Vitesse robot (lent)cls
ACCEL = 0.1
MAX_STEPS = 50       # Augmenté pour convergence
SAFE_MODE = False

# Seuils d'arrêt
GRIPPER_THRESHOLD = 0.5  # gripper < 0.5 = fermé
DISTANCE_THRESHOLD = 0.05  # Arrêter si distance < 5cm

os.makedirs(SAVE_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 📷 Capture ZIVID
# ─────────────────────────────────────────
def capture_zivid(camera) -> tuple:
    """Capture RGB et point cloud."""
    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
    )
    frame = camera.capture_2d_3d(settings)
    
    # RGB pour OpenVLA (224x224)
    image_rgba = frame.frame_2d().image_rgba_srgb()
    image_rgba.save(os.path.join(SAVE_DIR, "capture_latest.png"))
    rgba_array = image_rgba.copy_data()
    image_rgb = Image.fromarray(rgba_array[:, :, :3]).resize((224, 224))
    
    # Point cloud pour DINO (détection bouteille)
    pc_mm = frame.point_cloud().copy_data("xyz").astype(np.float32)
    
    return image_rgb, pc_mm, rgba_array  # rgba_array pour DINO


# ─────────────────────────────────────────
# 🎯 DINO — Détecter la bouteille
# ─────────────────────────────────────────
def detect_bottle_dino(image_rgb_large, pc_mm):
    """Détecter bouteille avec DINO (optionnel pour distance)."""
    try:
        from groundingdino.util.inference import load_model, predict
        
        # Charger DINO une seule fois
        if not hasattr(detect_bottle_dino, 'model'):
            print("📦 Chargement DINO...")
            detect_bottle_dino.model = load_model(
                "GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py",
                "weights/groundingdino_swint_ogc.pth"
            )
        
        # Prédire
        boxes, logits, phrases = predict(
            detect_bottle_dino.model,
            image_rgb_large,
            "bottle",
            0.3,
            0.25
        )
        
        if len(boxes) > 0:
            # Première détection (meilleure confiance)
            box = boxes[0]
            conf = logits[0]
            
            # Convertir box → pixel
            h, w = image_rgb_large.shape[:2]
            x_center = int((box[0] + box[2]) / 2 * w)
            y_center = int((box[1] + box[3]) / 2 * h)
            
            # Obtenir profondeur
            if 0 <= y_center < pc_mm.shape[0] and 0 <= x_center < pc_mm.shape[1]:
                z_mm = pc_mm[y_center, x_center, 2]
                if not np.isnan(z_mm) and z_mm > 0:
                    distance = z_mm / 1000.0  # mm → m
                    return True, distance, conf
        
        return False, None, None
    
    except Exception as e:
        print(f"⚠️  DINO indisponible : {e}")
        return False, None, None


# ─────────────────────────────────────────
# 🚀 INITIALISATION
# ─────────────────────────────────────────
print("=" * 60)
print("DÉMONSTRATEUR OPENVLA → BOUTEILLE (avec suivi DINO)")
print("=" * 60)

# ZIVID
print("\n📷 Connexion ZIVID...")
app = zivid.Application()
camera = app.connect_camera()
print(f"✅ Caméra : {camera.info.model_name}")

# OpenVLA
print("\n🤖 Chargement OpenVLA...")
processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")
print(f"✅ OpenVLA prêt ({torch.cuda.memory_allocated()/1e9:.1f} GB)")

# UR16e
print(f"\n🦾 Connexion UR16e...")
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
print("✅ Robot connecté")

# ─────────────────────────────────────────
# 🔄 BOUCLE PRINCIPALE
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print(f"🎯 Instruction : {INSTRUCTION}")
print("=" * 60)

prompt = f"In: What action should the robot take to {INSTRUCTION}?\nOut:"

last_gripper = 1.0
convergence_count = 0
MAX_CONVERGENCE = 3  # Si pas de changement pendant 3 steps → arrêter

# ─────────────────────────────────────────
# 🔄 BOUCLE AVEC STRATÉGIE
# ─────────────────────────────────────────

phase = 1  # Phase 1: approach, Phase 2: descend, Phase 3: grasp
step_in_phase = 0
STEPS_PER_PHASE = 15

for step in range(1, MAX_STEPS + 1):
    print(f"\n─── STEP {step}/{MAX_STEPS} [Phase {phase}] ───────────────────")

    # CAPTURE
    image_rgb, pc_mm, rgba_array = capture_zivid(camera)
    print("✅ Capture Zivid")

    # PROMPT DYNAMIQUE selon la phase
    if phase == 1:
        # Phase 1: s'approcher
        prompt = f"In: The robot should approach the bottle. What action?\nOut:"
    elif phase == 2:
        # Phase 2: descendre
        prompt = f"In: The robot should lower the gripper to the bottle. What action?\nOut:"
    else:
        # Phase 3: saisir
        prompt = f"In: The robot should grasp the bottle by closing the gripper. What action?\nOut:"

    # INFÉRENCE OPENVLA
    print(f"🤖 Inférence OpenVLA (phase {phase})...")
    inputs = processor(prompt, image_rgb).to("cuda:0", dtype=torch.bfloat16)
    action = vla.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)

    dx, dy, dz = action[0], action[1], action[2]
    rx, ry, rz = action[3], action[4], action[5]
    gripper = action[6]

    print(f"  XYZ : dx={dx:+.4f}  dy={dy:+.4f}  dz={dz:+.4f}")
    print(f"  Gripper : {gripper:.4f}")

    # MOUVEMENT ROBOT
    current_pose = rtde_r.getActualTCPPose()
    new_pose = [
        current_pose[0] + dx * SCALE,
        current_pose[1] + dy * SCALE,
        current_pose[2] + dz * SCALE,
        current_pose[3] + rx * SCALE,
        current_pose[4] + ry * SCALE,
        current_pose[5] + rz * SCALE,
    ]

    if not SAFE_MODE:
        rtde_c.moveL(new_pose, speed=SPEED, acceleration=ACCEL)
        print("✅ Mouvement exécuté")

    # ─────────────────────────────────────────
    # TRANSITION ENTRE PHASES
    # ─────────────────────────────────────────
    step_in_phase += 1

    if step_in_phase >= STEPS_PER_PHASE:
        if phase < 3:
            phase += 1
            step_in_phase = 0
            print(f"→ Passage à la phase {phase}")
        else:
            # Phase 3 terminée
            print(f"\n🏁 SUCCÈS — Bouteille saisie !")
            break

    time.sleep(0.2)

# ─────────────────────────────────────────
# 🏁 FIN
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("✅ Script terminé")
print(f"📁 Images : {SAVE_DIR}")
rtde_c.stopScript()