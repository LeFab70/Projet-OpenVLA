from transformers import AutoModelForVision2Seq, AutoProcessor
from PIL import Image
import zivid
import numpy as np
import torch
import os

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"
os.makedirs(SAVE_DIR, exist_ok=True)

# ─────────────────────────────────────────
# ÉTAPE 1 — CAPTURE ZIVID
# ─────────────────────────────────────────
print("=" * 50)
print("📷 ÉTAPE 1 : Capture ZIVID")
print("=" * 50)

app    = zivid.Application()
camera = app.connect_camera()
print(f"✅ Caméra connectée : {camera.info.model_name}")

settings = zivid.Settings(
    acquisitions=[zivid.Settings.Acquisition()],
    color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
)

frame      = camera.capture_2d_3d(settings)
image_rgba = frame.frame_2d().image_rgba_srgb()

# Sauvegarder image originale
image_path = os.path.join(SAVE_DIR, "capture.png")
image_rgba.save(image_path)
print(f"✅ Image sauvegardée : {image_path}")

# Convertir pour OpenVLA
rgba_array = image_rgba.copy_data()
pil_image  = Image.fromarray(rgba_array[:, :, :3]).resize((224, 224))
pil_image.save(os.path.join(SAVE_DIR, "capture_224.png"))
print(f"✅ Image 224x224 prête")

# ─────────────────────────────────────────
# ÉTAPE 2 — CHARGER OPENVLA
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("🤖 ÉTAPE 2 : Chargement OpenVLA")
print("=" * 50)

processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")
print(f"✅ Modèle prêt — VRAM : {torch.cuda.memory_allocated()/1e9:.1f} GB")

# ─────────────────────────────────────────
# ÉTAPE 3 — INFÉRENCE
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("🔍 ÉTAPE 3 : Inférence OpenVLA")
print("=" * 50)

# Change cette instruction selon ce qu'il y a devant la caméra
instruction = "pick up the object on the table"

prompt = f"In: What action should the robot take to {instruction}?\nOut:"
print(f"📌 Instruction : '{instruction}'")
print("⏳ Calcul en cours...")

inputs = processor(prompt, pil_image).to("cuda:0", dtype=torch.bfloat16)
action = vla.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)

# ─────────────────────────────────────────
# ÉTAPE 4 — RÉSULTATS
# ─────────────────────────────────────────
print("\n" + "=" * 50)
print("📊 ÉTAPE 4 : Résultats")
print("=" * 50)
print(f"  dx = {action[0]:+.4f}  (gauche/droite)")
print(f"  dy = {action[1]:+.4f}  (avant/arrière)")
print(f"  dz = {action[2]:+.4f}  (haut/bas)")
print(f"  rx = {action[3]:+.4f}  (rotation X)")
print(f"  ry = {action[4]:+.4f}  (rotation Y)")
print(f"  rz = {action[5]:+.4f}  (rotation Z)")
print(f"  gripper = {action[6]:.4f} → {'FERMER 🤏' if action[6] < 0.5 else 'OUVRIR ✋'}")
print("=" * 50)
print(f"\n✅ Terminé ! Image dans : {SAVE_DIR}")