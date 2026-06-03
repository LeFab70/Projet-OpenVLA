# =============================================================================
# Test détection mire ZIVID — avant de lancer la calibration
# =============================================================================

import zivid
import numpy as np

def test_mire_detection():
    """Tester si ZIVID peut voir la mire."""
    
    print("=" * 60)
    print("TEST DÉTECTION MIRE ZIVID")
    print("=" * 60)
    print("\n⚠️  Place la mire ZIVID officiellement devant la caméra")
    print("   La mire doit être :")
    print("   - À 30-80cm de la caméra")
    print("   - Face à la caméra (pas trop inclinée)")
    print("   - Bien éclairée (pas de zones sombres)")
    print("   - Plate et non roulée")
    
    input("\n   Appuie sur Entrée quand c'est prêt...")
    
    app = zivid.Application()
    camera = app.connect_camera()
    print(f"\n✅ Caméra connectée : {camera.info.model_name}")
    
    # Paramètres de capture
    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
    )
    
    print("\n[CAPTURE] Acquisition en cours...")
    frame = camera.capture_2d_3d(settings)
    print("✅ Frame capturée")
    
    # ─────────────────────────────────────────
    # TEST 1 — Détection de mire 3D
    # ─────────────────────────────────────────
    print("\n[TEST 1] Détection mire (3D point cloud)...")
    pc = frame.point_cloud()
    detection_3d = zivid.calibration.detect_feature_points(pc)
    
    if detection_3d.valid():
        print("✅ Mire détectée en 3D !")
        print(f"   Corner points : {len(detection_3d.corners())} coins")
    else:
        print("❌ Mire NON détectée en 3D")
        print("   → Problèmes possibles :")
        print("     • Mire trop loin (>1m)")
        print("     • Mire mal orientée")
        print("     • Mauvais éclairage")
        print("     • Mire pas officielle ZIVID")
    
    # ─────────────────────────────────────────
    # TEST 2 — Détection de mire 2D (RGB)
    # ─────────────────────────────────────────
    print("\n[TEST 2] Détection mire (2D image RGB)...")
    image_2d = frame.frame_2d()
    image_rgb = image_2d.image_rgba_srgb().copy_data()
    
    # Sauvegarder pour inspection
    image_rgb_uint8 = (image_rgb[:, :, :3] * 255).astype(np.uint8)
    from PIL import Image
    img = Image.fromarray(image_rgb_uint8)
    img.save("test_mire.png")
    print("   Image sauvegardée : test_mire.png")
    print("   → Ouvre et vérifie que la mire est visible")
    
    # ─────────────────────────────────────────
    # TEST 3 — Vérifier plage Z
    # ─────────────────────────────────────────
    print("\n[TEST 3] Vérifier plage profondeur...")
    xyz = pc.copy_data("xyz")
    
    # Points valides
    valid = ~np.isnan(xyz[:, :, 2])
    z_values = xyz[valid, 2]
    
    if len(z_values) > 0:
        z_min = np.nanmin(z_values)
        z_max = np.nanmax(z_values)
        z_mean = np.nanmean(z_values)
        print(f"✅ Profondeur :")
        print(f"   Min: {z_min*1000:.1f}mm")
        print(f"   Max: {z_max*1000:.1f}mm")
        print(f"   Mean: {z_mean*1000:.1f}mm")
        print(f"   → Mire doit être entre 300-1500mm")
    else:
        print("❌ Aucun point valide (point cloud vide)")
    
    # ─────────────────────────────────────────
    # DIAGNOSTIC
    # ─────────────────────────────────────────
    print("\n" + "=" * 60)
    print("DIAGNOSTIC")
    print("=" * 60)
    
    if detection_3d.valid():
        print("✅ SUCCÈS — Mire détectée !")
        print("\n→ Tu peux lancer la calibration :")
        print("  python -m pipeline.calibrer_robot")
    else:
        print("❌ ÉCHEC — Mire non détectée")
        print("\n→ Checklist avant de relancer ce test :")
        print("  ☐ Mire officielle ZIVID (pas imprimée)")
        print("  ☐ À 40-80cm de la caméra")
        print("  ☐ Face de la caméra (pas angle)")
        print("  ☐ Bien éclairée (pas d'ombres)")
        print("  ☐ Plate (pas roulée/froissée)")
        print("  ☐ Zivid Settings optimisées")
        print("\n→ Ou lis : https://support.zivid.com/en/latest/")
        print("   how-to/calibrate-camera-hand-eye.html")

if __name__ == "__main__":
    test_mire_detection()