# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Objectif    : Pipeline adaptatif ZIVID → DINO → UR16e → OpenVLA (boucle)
#               Phase 1 : DINO positionne le robot au-dessus de l'objet
#               Phase 2 : OpenVLA boucle perception→action→réinférence
#               Arrêt    : quand la pince se ferme (objet saisi)
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
import rtde_control
import rtde_receive
import os
import time

# ─────────────────────────────────────────
# ⚙️ CONFIG
# ─────────────────────────────────────────
ROBOT_IP   = "xxx.xxx.xxx.xxx"  # ← à configurer
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR   = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"

SCALE      = 0.08    # max 2cm par step (sécurité)
SPEED      = 0.05    # m/s
ACCEL      = 0.1     # m/s²
MAX_STEPS  = 20      # sécurité : arrêt après 20 steps
APPROACH_Z = 0.15    # hauteur approche au-dessus objet (15cm)
GRIPPER_THRESHOLD = 0.4  # en dessous = fermer pince

SAFE_MODE  = True    # ← True = affiche sans bouger

BOX_THRESHOLD  = 0.20  # seuil confiance DINO pour les boîtes
TEXT_THRESHOLD = 0.15  # seuil confiance DINO pour le texte


os.makedirs(SAVE_DIR, exist_ok=True)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ─────────────────────────────────────────
# 📷 FONCTION — Capture ZIVID
# ─────────────────────────────────────────
def capture_zivid(camera):
    """Retourne image_rgb (numpy) + point_cloud (numpy H,W,3)"""
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
    """Retourne le meilleur objet détecté avec ses coordonnées 3D"""
    h_pc, w_pc = point_cloud.shape[:2]
    h_img, w_img = image_rgb.shape[:2]
    scale_u = w_pc / w_img
    scale_v = h_pc / h_img

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

    detected = []
    for result in results:
        for box, score, label in zip(
            result["boxes"], result["scores"], result["labels"]
        ):
            x1, y1, x2, y2 = box.tolist()
            u = int((x1 + x2) / 2)
            v = int((y1 + y2) / 2)
            u_pc = min(int(u * scale_u), w_pc - 1)
            v_pc = min(int(v * scale_v), h_pc - 1)
            X, Y, Z = point_cloud[v_pc, u_pc]

            if np.isnan(X) or np.isnan(Y) or np.isnan(Z):
                continue

            detected.append({
                "label": label,
                "conf" : float(score),
                "X"    : float(X) / 1000,
                "Y"    : float(Y) / 1000,
                "Z"    : float(Z) / 1000,
            })

    return max(detected, key=lambda o: o["conf"]) if detected else None

# ─────────────────────────────────────────
# 🤏 FONCTION — Contrôle pince UR native
# ─────────────────────────────────────────
def control_gripper(rtde_c, close: bool):
    rtde_c.setToolDigitalOut(0, close)
    time.sleep(0.5)

# ─────────────────────────────────────────
# 🚀 INITIALISATION
# ─────────────────────────────────────────
print("=" * 60)
print("  DÉMONSTRATEUR ADAPTATIF — DINO + OpenVLA + UR16e")
print("=" * 60)
if SAFE_MODE:
    print("⚠️  MODE SÉCURISÉ — robot ne bougera PAS\n")
else:
    print("🚨  MODE RÉEL — robot va bouger !\n")

# Objet cible
TEXT_PROMPT = input("🔎 Objet à saisir : ").strip()
print()

# ZIVID
print("📷 Connexion ZIVID...")
app    = zivid.Application()
camera = app.connect_camera()
print(f"✅ Caméra : {camera.info.model_name}")

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

# UR16e
print(f"\n🦾 Connexion UR16e ({ROBOT_IP})...")
rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
print("✅ Robot connecté")

# ─────────────────────────────────────────
# 🎯 PHASE 1 — DINO : positionnement initial
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🎯 PHASE 1 : Localisation DINO + approche robot")
print("=" * 60)

image_rgb, point_cloud = capture_zivid(camera)
best = detect_with_dino(
    processor_dino, model_dino,
    image_rgb, point_cloud, TEXT_PROMPT
)

if best is None:
    print(f"❌ Objet '{TEXT_PROMPT}' non détecté — vérifier la scène")
    exit()

print(f"✅ Détecté : {best['label']} ({best['conf']*100:.1f}%)")
print(f"   Position 3D : X={best['X']:.3f}m  Y={best['Y']:.3f}m  Z={best['Z']:.3f}m")

# Pose d'approche — au-dessus de l'objet
approach_pose = [
    best['X'],
    best['Y'],
    best['Z'] + APPROACH_Z,  # 15cm au-dessus
    0.0, 3.14, 0.0           # orientation vers le bas
]

if SAFE_MODE:
    print(f"  [SAFE] Approche vers : {[f'{v:.3f}' for v in approach_pose]}")
else:
    print(f"🦾 Approche vers l'objet...")
    rtde_c.moveL(approach_pose, speed=0.3, acceleration=0.5)
    print("✅ Robot positionné au-dessus de l'objet")

# ─────────────────────────────────────────
# 🔄 PHASE 2 — Boucle OpenVLA adaptative
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🔄 PHASE 2 : Boucle perception → action → réinférence")
print("=" * 60)

""" prompt = (
    f"In: What action should the robot take to "
    f"pick up the {best['label']}?\nOut:"
) """

#utiliser les coordonnées 3D dans le prompt pour guider OpenVLA
prompt = (  
    f"In:the {best['label']} is located at position X={best['X']:.3f}m "
    f"Y={best['Y']:.3f}m "
    f"Z={best['Z']:.3f}m"
    f"\nWhat action should the robot take to pick it up the {best['label']}?\nOut:"
)


gripper_closed = False
step = 0

while not gripper_closed and step < MAX_STEPS:
    step += 1
    print(f"\n─── STEP {step}/{MAX_STEPS} ──────────────────────────────")

    # 1. Perception — nouvelle image à chaque step
    print("📷 Capture ZIVID...")
    image_rgb, _ = capture_zivid(camera)
    pil_vla = Image.fromarray(image_rgb).resize((224, 224))

    # Sauvegarder image du step
    pil_vla.save(os.path.join(SAVE_DIR, f"step_{step:02d}.png"))

    # 2. Inférence OpenVLA
    print("🤖 Inférence OpenVLA...")
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

    # 3. Action — envoyer au robot
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
        print(f"  [SAFE] Nouvelle pose : {[f'{v:.4f}' for v in new_pose]}")
    else:
        rtde_c.moveL(new_pose, speed=SPEED, acceleration=ACCEL)

        # Contrôle pince
        if gripper < GRIPPER_THRESHOLD:
            control_gripper(rtde_c, close=True)
            gripper_closed = True
            print("  🤏 Pince fermée — objet saisi !")
        else:
            control_gripper(rtde_c, close=False)

    # Condition arrêt SAFE_MODE
    if SAFE_MODE and gripper < GRIPPER_THRESHOLD and step > 2:
        print("\n  [SAFE] Pince se fermerait ici — arrêt simulé")
        gripper_closed = True

    time.sleep(0.1)

# ─────────────────────────────────────────
# 🏁 FIN
# ─────────────────────────────────────────
print("\n" + "=" * 60)
if gripper_closed:
    print(f"✅ Objet '{TEXT_PROMPT}' saisi en {step} steps !")
else:
    print(f"⚠️  Arrêt après {MAX_STEPS} steps sans saisie")
print(f"📁 Images steps : {SAVE_DIR}")
print("=" * 60)

if not SAFE_MODE:
    rtde_c.stopScript()