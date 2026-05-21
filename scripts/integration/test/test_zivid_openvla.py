# =========================================================
# IMPORT DES LIBRAIRIES
# =========================================================
from transformers import AutoModelForVision2Seq, AutoProcessor
import torch
from PIL import Image
import os
import zivid
import numpy as np


# =========================================================
# CONFIGURATION
# =========================================================
# Chemin vers ton modèle OpenVLA local
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"

# Dossier pour sauvegarder images
SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"
os.makedirs(SAVE_DIR, exist_ok=True)


# =========================================================
# 📷 1. CAPTURE AVEC LA CAMÉRA ZIVID
# =========================================================
print("📷 Connecting to camera...")

# Initialiser Zivid
app = zivid.Application()

# Connexion à la caméra
camera = app.connect_camera()

# Configuration capture (3D + couleur)
settings = zivid.Settings(
    acquisitions=[zivid.Settings.Acquisition()],
    color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
)

print("📸 Capturing frame...")
frame = camera.capture_2d_3d(settings)

# Image RGBA (4 canaux)
image_rgba = frame.frame_2d().image_rgba_srgb()

# Sauvegarde image brute
image_file = os.path.join(SAVE_DIR, "capture.png")
image_rgba.save(image_file)

print(f"✅ Image saved: {image_file}")


# =========================================================
# 🎨 2. CONVERSION RGBA → RGB (important pour OpenVLA)
# =========================================================
print("🔄 Converting RGBA image to RGB format...")

# ✅ Conversion correcte Zivid → NumPy
rgba_array = image_rgba.copy_data()

# Vérification shape
print("Shape image:", rgba_array.shape)  # doit être (H, W, 4)

# Supprimer canal alpha → garder RGB uniquement
rgb_array = rgba_array[:, :, :3]

# Convertir en image PIL + resize (format attendu par modèle)
rgb_image = Image.fromarray(rgb_array).resize((224, 224))

# Sauvegarde
rgb_image_file = os.path.join(SAVE_DIR, "capture_rgb.png")
rgb_image.save(rgb_image_file)

print(f"✅ RGB image saved: {rgb_image_file}")


# =========================================================
# 🧠 3. CHARGEMENT DU MODÈLE OPENVLA
# =========================================================
print("🧠 Loading OpenVLA model...")

# Préprocesseur (texte + image)
processor = AutoProcessor.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True
)

# Modèle OpenVLA (GPU)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")

print("✅ Modèle prêt")


# =========================================================
# 🧠 4. INSTRUCTIONS (ce qui est demandé au robot)
# =========================================================
instructions = [
    "pick up the object on the table",
    "grab the red object",
    "push the object to the left",
    "place the object in the bin",
]

print("\n🔍 Analyse de la scène...\n")
print("─" * 50)


# =========================================================
# 🤖 5. PRÉDICTION OPENVLA
# =========================================================
for instruction in instructions:

    # Format attendu par OpenVLA
    prompt = f"In: What action should the robot take to {instruction}?\nOut:"

    # Préparer inputs (image + texte)
    inputs = processor(prompt, rgb_image).to("cuda:0", dtype=torch.bfloat16)

    # 🔥 Prédiction principale
    action = vla.predict_action(
        **inputs,
        unnorm_key="bridge_orig",
        do_sample=False
    )

    # =====================================================
    # 🤏 ✋ INTERPRÉTATION DE LA PINCE (IMPORTANT)
    # =====================================================
    # action = [dx, dy, dz, rx, ry, rz, gripper]

    # action[6] correspond à l'état de la pince :
    #   - valeur proche de 0 → FERMER (grasp)
    #   - valeur proche de 1 → OUVRIR (release)

    if action[6] < 0.5:
        gripper_str = "FERMER 🤏"
    else:
        gripper_str = "OUVRIR ✋"

    # =====================================================
    # AFFICHAGE DES RÉSULTATS
    # =====================================================
    print(f"📌 Instruction : '{instruction}'")

    # Mouvement du robot (delta position)
    print(f"   → XYZ  : dx={action[0]:+.3f}  dy={action[1]:+.3f}  dz={action[2]:+.3f}")

    # Orientation du robot
    print(f"   → ROT  : rx={action[3]:+.3f}  ry={action[4]:+.3f}  rz={action[5]:+.3f}")

    # État pince
    print(f"   → Pince: {action[6]:.3f} ({gripper_str})")

    print("─" * 50)


# =========================================================
# ✅ FIN
# =========================================================
print("\n✅ Analyse terminée !")
print(f"📁 Images sauvegardées dans : {SAVE_DIR}")
