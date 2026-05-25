# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Objectif    : Capturer une scène avec la Zivid, extraire les coordonnées 3D d'objets détectés en 2D, et retourner ces coordonnées pour une utilisation ultérieure (ex : inférence OpenVLA, contrôle robotique).
# =============================================================================
import zivid
import numpy as np
from ultralytics import YOLO
from PIL import Image
import os

# Charger YOLO ()
yolo_model = YOLO("yolov8n.pt")


def detect_objects_and_get_3d(save_dir):
    """
    Capture Zivid → Détection YOLO → Coordonnées 3D.
    Retourne : image_rgb, liste_pixels, liste_coordonnees_3D
    """

    # ─────────────────────────────────────────
    # 1. Capture Zivid
    # ─────────────────────────────────────────
    app = zivid.Application()
    camera = app.connect_camera()

    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
    )

    frame = camera.capture_2d_3d(settings)

    # Image RGB (H, W, 4)
    image_rgba = frame.frame_2d().image_rgba_srgb().copy_data()
    image_rgb = image_rgba[:, :, :3]

    # Sauvegarde locale
    os.makedirs(save_dir, exist_ok=True)
    image_path = os.path.join(save_dir, "capture_zivid_yolo.png")
    Image.fromarray(image_rgb).save(image_path)
    print(f"📁 Image sauvegardée dans : {image_path}")

    # Nuage de points (H, W, 3)
    point_cloud = frame.point_cloud().copy_data("xyz") # coordonnées 3D (X, Y, Z) en mètres pour chaque pixel

# Dimensions réelles
    h_pc, w_pc = point_cloud.shape[:2]      # taille point cloud
    h_img, w_img = image_rgb.shape[:2]      # taille image RGB
    # Facteurs de conversion
    scale_u = w_pc / w_img
    scale_v = h_pc / h_img
    # ─────────────────────────────────────────
    # 2. Détection YOLO
    # ─────────────────────────────────────────
    # YOLO attend une image RGB (H, W, 3) en uint8
    # on recupère les pixels centraux des boîtes détectées pour extraire les coordonnées 3D correspondantes dans le nuage de points
    results = yolo_model.predict(image_rgb, conf=0.25, verbose=False)

    pixel_list = []

# Extraire les coordonnées 2D (u, v) des centres des boîtes détectées
# results contient une liste de résultats pour chaque image (ici une seule image), et chaque résultat a une liste de boîtes détectées avec leurs coordonnées
    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            u = int((x1 + x2) / 2)
            v = int((y1 + y2) / 2)
            pixel_list.append((u, v))

    print(f"🎯 Pixels détectés : {pixel_list}")

    # ─────────────────────────────────────────
# 3. Conversion en coordonnées 3D
# ─────────────────────────────────────────
    coords_3d = []
    for (u, v) in pixel_list:
    # Redimensionner pixel vers résolution point cloud
        u_pc = int(u * scale_u)
        v_pc = int(v * scale_v)

    # Clamp pour éviter out of bounds
        u_pc = min(u_pc, w_pc - 1)
        v_pc = min(v_pc, h_pc - 1)

        X, Y, Z = point_cloud[v_pc, u_pc]

    # Ignorer points invalides (NaN)
        if np.isnan(X) or np.isnan(Y) or np.isnan(Z):
            print(f"  ⚠️  Objet ({u},{v}) → point 3D invalide (NaN)")
            continue

        coords_3d.append((float(X), float(Y), float(Z)))

    print("📌 Coordonnées 3D :")
    for i, (X, Y, Z) in enumerate(coords_3d):
        print(f"  Objet {i+1} → X={X:.3f}, Y={Y:.3f}, Z={Z:.3f}")

    return image_rgb, pixel_list, coords_3d
