from ultralytics import YOLO
from PIL import Image
import cv2
import numpy as np

# Charger l'image capturée
image_path = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs\capture_zivid_yolo.png"
image = cv2.imread(image_path)

# YOLO avec seuil très bas pour voir TOUT ce qu'il détecte
model = YOLO("yolov8n.pt")
results = model.predict(image, conf=0.1, verbose=True)  # seuil 10%

# Afficher toutes les détections
for r in results:
    print(f"\n🔍 Détections trouvées : {len(r.boxes)}")
    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf   = float(box.conf[0])
        label  = model.names[cls_id]
        print(f"  → {label} ({conf*100:.1f}%)")

# Sauvegarder image annotée
annotated = results[0].plot()
cv2.imwrite("debug_yolo.png", annotated)
print("\n✅ Image annotée sauvegardée : debug_yolo.png")