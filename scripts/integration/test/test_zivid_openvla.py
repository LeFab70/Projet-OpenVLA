from transformers import AutoModelForVision2Seq, AutoProcessor
import torch
from PIL import Image
import os
import zivid
import numpy as np
# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
SAVE_DIR = r"C:\Users\Etudiant\StageFinal\OpenVLA\outputs"
os.makedirs(SAVE_DIR, exist_ok=True)
# ─────────────────────────────────────────
#CAMERA CAPTURE
# ─────────────────────────────────────────
print("📷 Connecting to camera")
app = zivid.Application()
camera = app.connect_camera()
print(f"✅ Connected to camera: {camera.info().name()}")
settings = zivid.Settings(
    acquisitions=[zivid.Settings.Acquisition()],
    color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
)
print("📸 Capturing frame")
frame = camera.capture_2d_3d(settings)
image_rgba = frame.frame_2d().image_rgba_srgb()
image_file = os.path.join(SAVE_DIR, "capture.png")
print(f"💾 Saving 2D color image (sRGB color space) to file: {image_file}")
image_rgba.save(image_file)
print(f"✅ Image saved: {image_file}")
# ─────────────────────────────────────────
#Convert RGBA to RGB for OpenVLA
# ─────────────────────────────────────────
print("🔄 Converting RGBA image to RGB format for OpenVLA")
rgba_array = np.array(image_rgba)
rgb_array = rgba_array[:, :, :3]  # Keep only R, G, B
rgb_image = Image.fromarray(rgb_array).rezize((224, 224))  # Resize to model's expected input size
rgb_image_file = os.path.join(SAVE_DIR, "capture_rgb.png")
print(f"💾 Saving RGB image for OpenVLA to file: {rgb_image_file}")
rgb_image.save(rgb_image_file)
print(f"✅ RGB image saved: {rgb_image_file}")
# ─────────────────────────────────────────
# load openvla
# ─────────────────────────────────────────
print("Loading OpenVLA processor...")
processor = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
vla = AutoModelForVision2Seq.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=True,
    trust_remote_code=True
).to("cuda:0")
print("✅ Modèle prêt")

# ─────────────────────────────────────────
# 3. DESCRIPTIONS À TESTER
# ─────────────────────────────────────────
instructions = [
    "pick up the object on the table",
    "grab the red object",
    "push the object to the left",
    "place the object in the bin",
]

print("\n🔍 Analyse de la scène...\n")
print("─" * 50)
print("\n🔍 Analyse de la scène...\n")
print("─" * 50)

for instruction in instructions:
    prompt = f"In: What action should the robot take to {instruction}?\nOut:"
    inputs = processor(prompt, pil_image).to("cuda:0", dtype=torch.bfloat16)
    action = vla.predict_action(**inputs, unnorm_key="bridge_orig", do_sample=False)

    gripper_str = "FERMER 🤏" if action[6] < 0.5 else "OUVRIR ✋"

    print(f"📌 Instruction : '{instruction}'")
    print(f"   → XYZ  : dx={action[0]:+.3f}  dy={action[1]:+.3f}  dz={action[2]:+.3f}")
    print(f"   → ROT  : rx={action[3]:+.3f}  ry={action[4]:+.3f}  rz={action[5]:+.3f}")
    print(f"   → Pince: {action[6]:.3f} ({gripper_str})")
    print("─" * 50)

print("\n✅ Analyse terminée !")
print(f"📁 Images sauvegardées dans : {SAVE_DIR}")