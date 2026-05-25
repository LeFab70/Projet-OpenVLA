# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Objectif    : tester la fonction de capture et d'extraction des coordonnées 3D à partir d'une scène capturée par la Zivid, en utilisant YOLO pour détecter les objets et extraire leurs positions 3D correspondantes.
# =============================================================================

SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"
from openVLA_ZIVID.functions.returnAllPositions import detect_objects_and_get_3d

image_rgb, pixel_list, coords_3d = detect_objects_and_get_3d(SAVE_DIR)
print("\n✅ Résultats :")
print(f"Nombre d'objets détectés : {len(pixel_list)}")
print("Coordonnées 2D (u, v) des centres des boîtes détectées :")
for i, (u, v) in enumerate(pixel_list):
    print(f"  Objet {i+1} : (u={u:.1f}, v={v:.1f})")
print("\nCoordonnées 3D correspondantes (X, Y, Z) :")
for i, (X, Y, Z) in enumerate(coords_3d):
    print(f"  Objet {i+1} : (X={X:.3f} m, Y={Y:.3f} m, Z={Z:.3f} m)")   
