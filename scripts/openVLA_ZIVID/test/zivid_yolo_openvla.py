# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Objectif    : Pipeline complet ZIVID → YOLO → OpenVLA
#               Les coordonnées 3D YOLO sont injectées dans le prompt OpenVLA
# =============================================================================
from transformers import AutoModelForVision2Seq, AutoProcessor
from ultralytics import YOLO
from PIL import Image
import zivid
import numpy as np
import torch
import os

# ─────────────────────────────────────────
# ⚙️ CONFIG
# ─────────────────────────────────────────
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR   = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"
YOLO_CONF  = 0.25
os.makedirs(SAVE_DIR, exist_ok=True)

# ─────────────────────────────────────────
# 📷 ÉTAPE 1 — Capture ZIVID
# ─────────────────────────────────────────
print("=" * 55)
print("📷 ÉTAPE 1 : Capture ZIVID")
print("=" * 55)

app    = zivid.Application()
camera = app.connect_camera()
print(f"✅ Caméra : {camera.info.model_name}")

settings = zivid.Settings(
    acquisitions=[zivid.Settings.Acquisition()],
    color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
)

frame      = camera.capture_2d_3d(settings)
image_rgba = frame.frame_2d().image_rgba_srgb().copy_data()
image_rgb  = image_rgba[:, :, :3]

# Point cloud XYZ
point_cloud    = frame.point_cloud().copy_data("xyz")
h_pc, w_pc     = point_cloud.shape[:2]
h_img, w_img   = image_rgb.shape[:2]
scale_u        = w_pc / w_img
scale_v        = h_pc / h_img

print(f"✅ Image RGB    : {w_img}x{h_img}")
print(f"✅ Point cloud  : {w_pc}x{h_pc}")

# Sauvegarder image
image_path = os.path.join(SAVE_DIR, "capture.png")
Image.fromarray(image_rgb).save(image_path)
print(f"✅ Image sauvegardée : {image_path}")

# ─────────────────────────────────────────
# 🎯 ÉTAPE 2 — Détection YOLO
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("🎯 ÉTAPE 2 : Détection YOLO")
print("=" * 55)

yolo  = YOLO("yolov8n.pt")
results = yolo.predict(image_rgb, conf=YOLO_CONF, verbose=False)

# Extraire objets détectés avec coordonnées 3D
detected_objects = []

for r in results:
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf   = float(box.conf[0])
        label  = yolo.names[cls_id]

        # Centre de la boîte en pixels
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        u = int((x1 + x2) / 2)
        v = int((y1 + y2) / 2)

        # Convertir vers résolution point cloud
        u_pc = min(int(u * scale_u), w_pc - 1)
        v_pc = min(int(v * scale_v), h_pc - 1)

        # Coordonnées 3D
        X, Y, Z = point_cloud[v_pc, u_pc]

        # Ignorer points invalides
        if np.isnan(X) or np.isnan(Y) or np.isnan(Z):
            print(f"  ⚠️  {label} → point 3D invalide (NaN), ignoré")
            continue

        detected_objects.append({
            "label" : label,
            "conf"  : conf,
            "u"     : u,
            "v"     : v,
            "X"     : float(X) / 1000,  # mm → mètres si nécessaire
            "Y"     : float(Y) / 1000,
            "Z"     : float(Z) / 1000,
        })

        print(f"  ✅ {label} ({conf*100:.1f}%) → "
              f"pixel=({u},{v}) | "
              f"3D=({float(X)/1000:.3f}m, {float(Y)/1000:.3f}m, {float(Z)/1000:.3f}m)")

if not detected_objects:
    print("⚠️  Aucun objet détecté — place un objet devant la caméra")
    exit()

# Prendre l'objet avec la meilleure confiance
best = max(detected_objects, key=lambda o: o["conf"])
print(f"\n🏆 Meilleur objet : {best['label']} ({best['conf']*100:.1f}%)")

# ─────────────────────────────────────────
# 🤖 ÉTAPE 3 — Charger OpenVLA
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("🤖 ÉTAPE 3 : Chargement OpenVLA")
print("=" * 55)

processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")
print(f"✅ OpenVLA prêt — VRAM : {torch.cuda.memory_allocated()/1e9:.1f} GB")

# ─────────────────────────────────────────
# 🔍 ÉTAPE 4 — Inférence OpenVLA
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("🔍 ÉTAPE 4 : Inférence OpenVLA")
print("=" * 55)

# Injection des coordonnées 3D dans le prompt
prompt_instruction = (
    f"pick up the {best['label']} "
    f"at position X={best['X']:.3f}m "
    f"Y={best['Y']:.3f}m "
    f"Z={best['Z']:.3f}m"
)
prompt = f"In: What action should the robot take to {prompt_instruction}?\nOut:"

print(f"📌 Prompt : {prompt_instruction}")

# Image PIL 224x224 pour OpenVLA
pil_image = Image.fromarray(image_rgb).resize((224, 224))

inputs = processor(prompt, pil_image).to("cuda:0", dtype=torch.bfloat16)
action = vla.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)

# ─────────────────────────────────────────
# 📊 ÉTAPE 5 — Résultats
# ─────────────────────────────────────────
print("\n" + "=" * 55)
print("📊 ÉTAPE 5 : Résultats")
print("=" * 55)
print(f"  Objet ciblé : {best['label']}")
print(f"  Position 3D : X={best['X']:.3f}m  Y={best['Y']:.3f}m  Z={best['Z']:.3f}m")
print(f"  dx={action[0]:+.4f}  dy={action[1]:+.4f}  dz={action[2]:+.4f}")
print(f"  rx={action[3]:+.4f}  ry={action[4]:+.4f}  rz={action[5]:+.4f}")
print(f"  gripper={action[6]:.4f} → {'FERMER 🤏' if action[6] < 0.5 else 'OUVRIR ✋'}")
print("=" * 55)
print("✅ Pipeline complet ZIVID → YOLO → OpenVLA terminé !")