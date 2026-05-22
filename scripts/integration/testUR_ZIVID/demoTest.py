# ─────────────────────────────────────────────────────────────
# DÉMONSTRATEUR OPENVLA — ZIVID + OpenVLA + UR16e
# Pince UR native | IP xxx.xxx.xxx.xxx | Modèle OpenVLA-7b
# ─────────────────────────────────────────────────────────────
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
# ⚙️ CONFIG — À MODIFIER
# ─────────────────────────────────────────
ROBOT_IP   = "192.168.1.10"        # IP  UR16e
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"

INSTRUCTION = "pick up the object on the table"  # changer selon la scène

SCALE       = 0.05   # max 5cm par step (sécurité)
SPEED       = 0.05   # vitesse robot (m/s) — lent pour sécurité
ACCEL       = 0.1    # accélération (m/s²)
MAX_STEPS   = 10     # nombre max d'itérations
SAFE_MODE   = True   # ← True = affiche sans bouger | False = bouge vraiment

os.makedirs(SAVE_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 📷 FONCTION — Capture ZIVID
# ─────────────────────────────────────────
def capture_zivid(camera) -> Image.Image:
    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
    )
    frame      = camera.capture_2d_3d(settings)
    image_rgba = frame.frame_2d().image_rgba_srgb()

    # Sauvegarder image originale
    image_rgba.save(os.path.join(SAVE_DIR, "capture_latest.png"))

    # Convertir en PIL RGB 224x224 pour OpenVLA
    rgba_array = image_rgba.copy_data()
    pil_image  = Image.fromarray(rgba_array[:, :, :3]).resize((224, 224))
    return pil_image

# ─────────────────────────────────────────
# 🤏 FONCTION — Contrôle pince UR native
# ─────────────────────────────────────────
def control_gripper(rtde_c, close: bool):
    # Pince UR native via signal digital
    # close=True → fermer | close=False → ouvrir
    if close:
        rtde_c.setToolDigitalOut(0, True)   # signal DO0 → fermer
        print("  🤏 Pince : FERMER")
    else:
        rtde_c.setToolDigitalOut(0, False)  # signal DO0 → ouvrir
        print("  ✋ Pince : OUVRIR")
    time.sleep(0.5)  # attendre fin mouvement pince

# ─────────────────────────────────────────
# 🚀 INITIALISATION
# ─────────────────────────────────────────
print("=" * 55)
print("  DÉMONSTRATEUR OPENVLA — UR16e + ZIVID Two")
print("=" * 55)

if SAFE_MODE:
    print("⚠️  MODE SÉCURISÉ — robot ne bougera PAS")
else:
    print("🚨  MODE RÉEL — robot va bouger !")
print()

# 1. ZIVID
print("📷 Connexion ZIVID...")
app    = zivid.Application()
camera = app.connect_camera()
print(f"✅ Caméra : {camera.info.model_name}")

# 2. OpenVLA
print("\n🤖 Chargement OpenVLA (patience ~5s)...")
processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")
print(f"✅ OpenVLA prêt — VRAM : {torch.cuda.memory_allocated()/1e9:.1f} GB")

# 3. UR16e
print(f"\n🦾 Connexion UR16e ({ROBOT_IP})...")
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
print("✅ Robot connecté")

# ─────────────────────────────────────────
# 🔄 BOUCLE PRINCIPALE
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print(f"🎯 Instruction : '{INSTRUCTION}'")
print("=" * 55)

prompt = f"In: What action should the robot take to {INSTRUCTION}?\nOut:"

for step in range(MAX_STEPS):
    print(f"\n─── STEP {step + 1}/{MAX_STEPS} ───────────────────────────")

    # ÉTAPE 1 — Capture image
    print("📷 Capture ZIVID...")
    image = capture_zivid(camera)
    print("✅ Image capturée")

    # ÉTAPE 2 — Inférence OpenVLA
    print("🤖 Inférence OpenVLA...")
    inputs = processor(prompt, image).to("cuda:0", dtype=torch.bfloat16)
    action = vla.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)

    dx, dy, dz = action[0], action[1], action[2]
    rx, ry, rz = action[3], action[4], action[5]
    gripper    = action[6]

    print(f"  → XYZ     : dx={dx:+.4f}  dy={dy:+.4f}  dz={dz:+.4f}")
    print(f"  → ROT     : rx={rx:+.4f}  ry={ry:+.4f}  rz={rz:+.4f}")
    print(f"  → Gripper : {gripper:.4f} ({'FERMER' if gripper < 0.5 else 'OUVRIR'})")

    # ÉTAPE 3 — Mouvement robot
    current_pose = rtde_r.getActualTCPPose()
    new_pose = [
        current_pose[0] + dx * SCALE,
        current_pose[1] + dy * SCALE,
        current_pose[2] + dz * SCALE,
        current_pose[3] + rx * SCALE,
        current_pose[4] + ry * SCALE,
        current_pose[5] + rz * SCALE,
    ]

    if SAFE_MODE:
        print(f"  [SAFE] Pose actuelle : {[f'{v:.4f}' for v in current_pose]}")
        print(f"  [SAFE] Nouvelle pose : {[f'{v:.4f}' for v in new_pose]}")
        print("  [SAFE] Mouvement NON envoyé")
    else:
        print("🦾 Envoi commande robot...")
        rtde_c.moveL(new_pose, speed=SPEED, acceleration=ACCEL)
        control_gripper(rtde_c, close=(gripper < 0.5))
        print("✅ Mouvement exécuté")

    # Condition d'arrêt — pince stable = tâche probablement terminée
    if step > 2 and abs(gripper - 0.5) > 0.4:
        print("\n🏁 Pince stable — tâche probablement terminée !")
        break

    time.sleep(0.2)  # pause entre steps

# ─────────────────────────────────────────
# 🏁 FIN
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("✅ Démo terminée !")
print(f"📁 Images dans : {SAVE_DIR}")
rtde_c.stopScript()