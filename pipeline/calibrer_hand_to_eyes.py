# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 29 mai 2026
# Fichier     : calibrer_manuel.py
# Objectif    : Calibration MANUELLE eye-to-hand (sans mire)
# =============================================================================

import numpy as np
from pathlib import Path
from pipeline.config import CALIBRATION_FILE


def calibrate_manual():
    """Calibration manuelle : mesurer position caméra → base robot."""

    print("=" * 70)
    print("CALIBRATION MANUELLE — Eye-to-Hand (caméra fixe)")
    print("=" * 70)

    print("\n📏 MESURE DE POSITION")
    print("-" * 70)
    print("""
    Tu vas mesurer la position de la caméra ZIVID par rapport à la base du robot.
    
    Repère :
        Base robot = point (0, 0, 0) — généralement sur le socle
        
    À mesurer :
        - X : distance avant/arrière (en mètres)
        - Y : distance gauche/droite (en mètres)
        - Z : hauteur (en mètres)
        
    Utilise un mètre ruban ou règle. Approximation ±5cm OK.
    """)

    print("\n📐 Entrez les coordonnées de la caméra :")
    print("-" * 70)

    try:
        x_input = input(f"  X (avant/arrière) [0.50m] : ").strip()
        x = float(x_input) if x_input else 0.50

        y_input = input(f"  Y (gauche/droite) [0.00m] : ").strip()
        y = float(y_input) if y_input else 0.00

        z_input = input(f"  Z (hauteur) [1.10m] : ").strip()
        z = float(z_input) if z_input else 1.10

    except ValueError:
        print("❌ Erreur : entrées invalides")
        return

    # ─────────────────────────────────────────
    # CONSTRUIRE T_BASE_CAM
    # ─────────────────────────────────────────
    # Matrice de transformation base→caméra
    # Pour une caméra regardant vers le haut (+Z)

    T_base_cam = np.array([
        [1, 0, 0, x],    # Rotation (identité) + position X
        [0, 1, 0, y],    #                       position Y
        [0, 0, 1, z],    #                       position Z
        [0, 0, 0, 1],    # Homogène
    ], dtype=np.float64)

    # ─────────────────────────────────────────
    # AFFICHAGE ET CONFIRMATION
    # ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print("MATRICE T_BASE_CAM")
    print("=" * 70)
    print(f"\n{T_base_cam}\n")

    print("Position caméra résumée :")
    print(f"  X = {x:.3f}m (avant/arrière)")
    print(f"  Y = {y:.3f}m (gauche/droite)")
    print(f"  Z = {z:.3f}m (hauteur)")

    confirm = input("\n✓ Confirmer ? (oui/non) : ").strip().lower()
    if confirm not in ["oui", "o", "yes", "y"]:
        print("❌ Annulé")
        return

    # ─────────────────────────────────────────
    # SAUVEGARDE
    # ─────────────────────────────────────────
    Path(CALIBRATION_FILE).parent.mkdir(parents=True, exist_ok=True)
    np.save(CALIBRATION_FILE, T_base_cam)

    print("\n" + "=" * 70)
    print("🏆 CALIBRATION SAUVEGARDÉE !")
    print("=" * 70)
    print(f"\nFichier : {CALIBRATION_FILE}")
    print("\n✅ Tu peux maintenant lancer :")
    print("   python -m pipeline.main_real")

    # Vérifier que le fichier est chargeable
    T_test = np.load(CALIBRATION_FILE)
    print(f"\n✓ Vérification : fichier chargeable ✅")


if __name__ == "__main__":
    calibrate_manual()