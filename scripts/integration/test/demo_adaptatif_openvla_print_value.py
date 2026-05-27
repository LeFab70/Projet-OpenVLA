# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Objectif    : Pipeline adaptatif ZIVID → DINO → OpenVLA (boucle)
#               Phase 1 : DINO localise l'objet + coordonnées 3D
#               Phase 2 : OpenVLA boucle perception→action→réinférence
#               Arrêt    : quand la pince se ferme (objet saisi)
#               UR16e    : en commentaire (activation future)
# =============================================================================
from transformers import (
    AutoProcessor,
    AutoModelForVision2Seq,
    AutoModelForZeroShotObjectDetection,
)
from PIL import Image
import zivid
import numpy as np
import torch
# import rtde_control                  # ← UR16e désactivé
# import rtde_receive                  # ← UR16e désactivé
import os
import time

# ─────────────────────────────────────────
# ⚙️ CONFIG
# ─────────────────────────────────────────
# ROBOT_IP   = "192.168.1.10"          # ← UR16e désactivé
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR   = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"

SCALE              = 0.08    # max 2cm par step (sécurité)
APPROACH_Z         = 0.15
MAX_STEPS          = 20
GRIPPER_THRESHOLD  = 0.4
BOX_THRESHOLD      = 0.20
TEXT_THRESHOLD     = 0.15

os.makedirs(SAVE_DIR, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─────────────────────────────────────────
# 📷 FONCTION — Capture ZIVID
# ─────────────────────────────────────────
def capture_zivid(camera):
    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(
            acquisitions=[zivid.Settings2D.Acquisition()]
        ),
    )
    frame       = camera.capture_2d_3d(settings)
    image_rgba  = frame.frame_2d().image_rgba_srgb().copy_data()
    image_rgb   = image_rgba[:, :, :3]
    point_cloud = frame.point_cloud().copy_data("xyz")
    return image_rgb, point_cloud

# ─────────────────────────────────────────
# 🎯 FONCTION — Détection DINO + XYZ
# ─────────────────────────────────────────
def detect_with_dino(processor_dino, model_dino, image_rgb,
                     point_cloud, text_prompt):
    h_pc, w_pc   = point_cloud.shape[:2]
    h_img, w_img = image_rgb.shape[:2]
    scale_u      = w_pc / w_img
    scale_v      = h_pc / h_img

    pil_image   = Image.fromarray(image_rgb)
    inputs_dino = processor_dino(
        images=pil_image,
        text=text_prompt + ".",
        return_tensors="pt"
    ).to(DEVICE)

    with torch.no_grad():
        outputs = model_dino(**inputs_dino)

    results = processor_dino.post_process_grounded_object_detection(
        outputs,
        inputs_dino.input_ids,
        box_threshold=BOX_THRESHOLD,
        text_threshold=TEXT_THRESHOLD,
        target_sizes=[pil_image.size[::-1]]
    )

   # print(f"  🔍 DINO a détecté {len(results[0]['boxes'])} objets")
   
    detected = []
    for result in results:
        for box, score, label in zip(
            result["boxes"], result["scores"], result["labels"]
        ):
            x1, y1, x2, y2 = box.tolist()
            u    = int((x1 + x2) / 2)
            v    = int((y1 + y2) / 2)
            u_pc = min(int(u * scale_u), w_pc - 1)
            v_pc = min(int(v * scale_v), h_pc - 1)
            X, Y, Z = point_cloud[v_pc, u_pc]

            if np.isnan(X) or np.isnan(Y) or np.isnan(Z):
                print(f"  ⚠️  {label} → point 3D invalide (NaN), ignoré")
                continue

            detected.append({
                "label" : label,
                "conf"  : float(score),
                "X"     : float(X) / 1000,
                "Y"     : float(Y) / 1000,
                "Z"     : float(Z) / 1000,
            })
            print(
                f"  ✅ {label} ({float(score)*100:.1f}%) → "
                f"3D=({float(X)/1000:.3f}m, "
                f"{float(Y)/1000:.3f}m, "
                f"{float(Z)/1000:.3f}m)"
            )

    return max(detected, key=lambda o: o["conf"]) if detected else None

# ─────────────────────────────────────────
# 🚀 INITIALISATION
# ─────────────────────────────────────────
print("=" * 60)
print("  DÉMONSTRATEUR ADAPTATIF — DINO + OpenVLA")
print("  [MODE SIMULATION — UR16e désactivé]")
print("=" * 60)

# Saisie objet cible
TEXT_PROMPT = input("🔎 Entrez l'objet à saisir : ").strip()
print()
#TEXT_PROMPT += "."  # ponctuation pour mieux guider DINO
# ZIVID
print("📷 Connexion ZIVID...")
app    = zivid.Application()
camera = app.connect_camera()
print(f"✅ Caméra connectée : {camera.info.model_name}")

# Grounding DINO
print("\n🎯 Chargement Grounding DINO...")
processor_dino = AutoProcessor.from_pretrained(
    "IDEA-Research/grounding-dino-base"
)
model_dino = AutoModelForZeroShotObjectDetection.from_pretrained(
    "IDEA-Research/grounding-dino-base"
).to(DEVICE)
print("✅ DINO prêt")

# OpenVLA
print("\n🤖 Chargement OpenVLA...")
processor_vla = AutoProcessor.from_pretrained(
    MODEL_PATH, trust_remote_code=True
)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")
print(f"✅ OpenVLA prêt — VRAM : {torch.cuda.memory_allocated()/1e9:.1f} GB")

# UR16e — désactivé
# rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
# rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
# print("✅ Robot connecté")
print("\n🦾 UR16e : [DÉSACTIVÉ — simulation uniquement]")

# ─────────────────────────────────────────
# 🎯 PHASE 1 — DINO : localisation initiale
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print(f"🎯 PHASE 1 : Localisation '{TEXT_PROMPT}' avec DINO")
print("=" * 60)

image_rgb, point_cloud = capture_zivid(camera)
best = detect_with_dino(
    processor_dino, model_dino,
    image_rgb, point_cloud, TEXT_PROMPT
)

if best is None:
    print(f"❌ Objet '{TEXT_PROMPT}' non détecté — vérifier la scène")
    exit()

print(f"\n🏆 Meilleur objet : {best['label']} ({best['conf']*100:.1f}%)")
print(f"   Position 3D    : X={best['X']:.3f}m  Y={best['Y']:.3f}m  Z={best['Z']:.3f}m")

# Pose d'approche simulée
approach_pose = [
    best['X'], 
    best['Y'],
    best['Z'] + APPROACH_Z,
    0.0, 3.14, 0.0
]
print(f"\n[SIM] UR16e moveL() → approche au-dessus : {[f'{v:.3f}' for v in approach_pose]}")
# rtde_c.moveL(approach_pose, speed=0.3, acceleration=0.5)  # ← UR16e désactivé

# ─────────────────────────────────────────
# 🔄 PHASE 2 — Boucle OpenVLA adaptative
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🔄 PHASE 2 : Boucle perception → action → réinférence")
print("=" * 60)

""" prompt = (
    f"In: What action should the robot take to "
    f"pick up the {TEXT_PROMPT}?\nOut:"
 ) """


#utiliser les coordonnées 3D dans le prompt pour guider OpenVLA
prompt = (  
    f"In:the {best['label']} is located at position X={best['X']:.3f}m "
    f"Y={best['Y']:.3f}m "
    f"Z={best['Z']:.3f}m"
    f"\nWhat action should the robot take to pick it up the {best['label']}?\nOut:"
)

print(f"📌 Prompt : pick up the {best['label']}\n")

# Pose simulée initiale (au-dessus de l'objet)
simulated_pose = approach_pose.copy()
gripper_closed = False
step           = 0

while not gripper_closed and step < MAX_STEPS:
    step += 1
    print(f"─── STEP {step}/{MAX_STEPS} ──────────────────────────────")

    # 1. Perception
    print("  📷 Capture ZIVID...")
    image_rgb, _ = capture_zivid(camera)
    pil_vla = Image.fromarray(image_rgb).resize((224, 224))
    pil_vla.save(os.path.join(SAVE_DIR, f"step_{step:02d}.png"))
    print(f"  ✅ Image sauvegardée : step_{step:02d}.png")

    # 2. Inférence OpenVLA
    print("  🤖 Inférence OpenVLA...")
    inputs_vla = processor_vla(
        prompt, pil_vla
    ).to("cuda:0", dtype=torch.bfloat16)

    action = vla.predict_action(
        **inputs_vla,
        unnorm_key="bridge_orig",
        do_sample=False
    )

    dx, dy, dz = action[0], action[1], action[2]
    rx, ry, rz = action[3], action[4], action[5]
    gripper    = action[6]

    print(f"  → XYZ     : dx={dx:+.4f}  dy={dy:+.4f}  dz={dz:+.4f}")
    print(f"  → ROT     : rx={rx:+.4f}  ry={ry:+.4f}  rz={rz:+.4f}")
    print(f"  → Gripper : {gripper:.4f} "
          f"({'FERMER 🤏' if gripper < GRIPPER_THRESHOLD else 'OUVRIR ✋'})")

    # 3. Action simulée
    new_pose = [
        simulated_pose[0] + dx * SCALE,
        simulated_pose[1] + dy * SCALE,
        simulated_pose[2] + dz * SCALE,
        simulated_pose[3] + rx * SCALE,
        simulated_pose[4] + ry * SCALE,
        simulated_pose[5] + rz * SCALE,
    ]
    print(f"  [SIM] Pose actuelle  : {[f'{v:.4f}' for v in simulated_pose]}")
    print(f"  [SIM] Nouvelle pose  : {[f'{v:.4f}' for v in new_pose]}")

    # rtde_c.moveL(new_pose, speed=SPEED, acceleration=ACCEL)  # ← UR16e désactivé

    # Mise à jour pose simulée
    simulated_pose = new_pose

    # Contrôle pince simulé
    if gripper < GRIPPER_THRESHOLD:
        print("  [SIM] UR16e → pince FERMER 🤏")
        # control_gripper(rtde_c, close=True)   # ← UR16e désactivé
        if step > 2:
            gripper_closed = True
            print("  🏁 Objet saisi (simulé) !")
    else:
        print("  [SIM] UR16e → pince OUVRIR ✋")
        # control_gripper(rtde_c, close=False)  # ← UR16e désactivé

    print()
    time.sleep(0.1)

# ─────────────────────────────────────────
# 🏁 FIN
# ─────────────────────────────────────────
print("=" * 60)
if gripper_closed:
    print(f"✅ Simulation terminée — '{TEXT_PROMPT}' saisi en {step} steps !")
else:
    print(f"⚠️  Arrêt après {MAX_STEPS} steps sans saisie")
print(f"📁 Images sauvegardées : {SAVE_DIR}")
print("=" * 60)

# rtde_c.stopScript()    # ← UR16e désactivé