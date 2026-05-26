# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Objectif    : Pipeline complet
#               ZIVID → Grounding DINO → OpenVLA
#
# Description :
# - Capture RGB + profondeur avec Zivid
# - Détection open-vocabulary avec Grounding DINO
# - Extraction coordonnées 3D depuis point cloud
# - OpenVLA reçoit seulement la description de l’objet
# - Le contrôleur robot garde les XYZ
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
import os

# ─────────────────────────────────────────
# ⚙️ CONFIG
# ─────────────────────────────────────────
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"

SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"

# Objet recherché par Grounding DINO
#TEXT_PROMPT = "cell phone"
TEXT_PROMPT = input(
    "🔎 Entrez l'objet à détecter : "
).strip()



BOX_THRESHOLD = 0.35
TEXT_THRESHOLD = 0.25

os.makedirs(SAVE_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 📷 ÉTAPE 1 — Capture ZIVID
# ─────────────────────────────────────────
print("=" * 60)
print("📷 ÉTAPE 1 : Capture ZIVID")
print("=" * 60)

app = zivid.Application()
camera = app.connect_camera()

print(f"✅ Caméra : {camera.info.model_name}")

settings = zivid.Settings(
    acquisitions=[zivid.Settings.Acquisition()],
    color=zivid.Settings2D(
        acquisitions=[zivid.Settings2D.Acquisition()]
    ),
)

# Capture RGB + 3D
frame = camera.capture_2d_3d(settings)

# Image RGB
image_rgba = frame.frame_2d().image_rgba_srgb().copy_data()
image_rgb = image_rgba[:, :, :3]

# Point cloud XYZ
point_cloud = frame.point_cloud().copy_data("xyz")

# Dimensions
h_pc, w_pc = point_cloud.shape[:2]
h_img, w_img = image_rgb.shape[:2]

scale_u = w_pc / w_img
scale_v = h_pc / h_img

print(f"✅ Image RGB   : {w_img}x{h_img}")
print(f"✅ Point cloud : {w_pc}x{h_pc}")

# Sauvegarde image
image_path = os.path.join(SAVE_DIR, "capture.png")

Image.fromarray(image_rgb).save(image_path)

print(f"✅ Image sauvegardée : {image_path}")

# ─────────────────────────────────────────
# 🎯 ÉTAPE 2 — Grounding DINO
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🎯 ÉTAPE 2 : Grounding DINO")
print("=" * 60)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

processor_dino = AutoProcessor.from_pretrained(
    "IDEA-Research/grounding-dino-base"
)

model_dino = AutoModelForZeroShotObjectDetection.from_pretrained(
    "IDEA-Research/grounding-dino-base"
).to(DEVICE)

print("✅ Grounding DINO chargé")

# Conversion image PIL
pil_image = Image.fromarray(image_rgb)

# Préparer inputs
inputs_dino = processor_dino(
    images=pil_image,
    text=TEXT_PROMPT,
    return_tensors="pt"
).to(DEVICE)

# Inférence
with torch.no_grad():
    outputs_dino = model_dino(**inputs_dino)

# Post-processing
results = processor_dino.post_process_grounded_object_detection(
    outputs_dino,
    inputs_dino.input_ids,
    box_threshold=BOX_THRESHOLD,
    text_threshold=TEXT_THRESHOLD,
    target_sizes=[pil_image.size[::-1]]
)

# ─────────────────────────────────────────
# 📦 EXTRACTION OBJETS + XYZ
# ─────────────────────────────────────────
detected_objects = []

for result in results:

    boxes = result["boxes"]
    scores = result["scores"]
    labels = result["labels"]

    for box, score, label in zip(boxes, scores, labels):

        x1, y1, x2, y2 = box.tolist()

        # Centre bbox
        u = int((x1 + x2) / 2)
        v = int((y1 + y2) / 2)

        # Conversion vers résolution point cloud
        u_pc = min(int(u * scale_u), w_pc - 1)
        v_pc = min(int(v * scale_v), h_pc - 1)

        # Coordonnées 3D
        X, Y, Z = point_cloud[v_pc, u_pc]

        # Vérification NaN
        if np.isnan(X) or np.isnan(Y) or np.isnan(Z):

            print(f"⚠️  {label} → point 3D invalide")
            continue

        detected_objects.append({
            "label": label,
            "conf": float(score),
            "u": u,
            "v": v,
            "X": float(X) / 1000,
            "Y": float(Y) / 1000,
            "Z": float(Z) / 1000,
        })

        print(
            f"✅ {label} ({float(score)*100:.1f}%) → "
            f"pixel=({u},{v}) | "
            f"3D=({float(X)/1000:.3f}m, "
            f"{float(Y)/1000:.3f}m, "
            f"{float(Z)/1000:.3f}m)"
        )

# Vérification
if not detected_objects:

    print("⚠️ Aucun objet détecté")
    exit()

# Meilleur objet
best = max(detected_objects, key=lambda o: o["conf"])

print(
    f"\n🏆 Meilleur objet : "
    f"{best['label']} "
    f"({best['conf']*100:.1f}%)"
)

# ─────────────────────────────────────────
# 🤖 ÉTAPE 3 — Charger OpenVLA
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🤖 ÉTAPE 3 : Chargement OpenVLA")
print("=" * 60)

processor_vla = AutoProcessor.from_pretrained(
    MODEL_PATH,
    trust_remote_code=True
)

vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")

print(
    f"✅ OpenVLA prêt — "
    f"VRAM : {torch.cuda.memory_allocated()/1e9:.1f} GB"
)

# ─────────────────────────────────────────
# 🔍 ÉTAPE 4 — Inférence OpenVLA
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("🔍 ÉTAPE 4 : Inférence OpenVLA")
print("=" * 60)

# IMPORTANT :
# On donne seulement la description de l’objet
# PAS les coordonnées XYZ

prompt_instruction = f"pick up the {best['label']}"

prompt = (
    f"In: What action should the robot take to "
    f"{prompt_instruction}?\nOut:"
)

print(f"📌 Prompt : {prompt_instruction}")

# Image 224x224 pour OpenVLA
pil_vla = Image.fromarray(image_rgb).resize((224, 224))

inputs_vla = processor_vla(
    prompt,
    pil_vla
).to("cuda:0", dtype=torch.bfloat16)

# Action OpenVLA
action = vla.predict_action(
    **inputs_vla,
    unnorm_key="bridge_orig",
    do_sample=False
)

# ─────────────────────────────────────────
# 📊 ÉTAPE 5 — Résultats
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("📊 ÉTAPE 5 : Résultats")
print("=" * 60)

print(f"Objet ciblé : {best['label']}")

print(
    f"Position 3D réelle : "
    f"X={best['X']:.3f}m  "
    f"Y={best['Y']:.3f}m  "
    f"Z={best['Z']:.3f}m"
)

print(
    f"dx={action[0]:+.4f}  "
    f"dy={action[1]:+.4f}  "
    f"dz={action[2]:+.4f}"
)

print(
    f"rx={action[3]:+.4f}  "
    f"ry={action[4]:+.4f}  "
    f"rz={action[5]:+.4f}"
)

print(
    f"gripper={action[6]:.4f} → "
    f"{'FERMER 🤏' if action[6] < 0.5 else 'OUVRIR ✋'}"
)

print("=" * 60)
print("✅ Pipeline Grounding DINO → OpenVLA terminé !")
