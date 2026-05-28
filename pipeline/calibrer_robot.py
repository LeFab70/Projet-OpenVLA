"""
# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 28 mai 2026
# Fichier     : calibrer_robot.py
# Objectif    : Fonctions de calibration pour le robot UR16e (main-œil)
# =============================================================================
ce fichier contient des fonctions de calibration pour le robot UR16e, notamment la transformation caméra→robot via la matrice T_tcp_cam, ainsi que des fonctions utilitaires pour calculer la distance TCP-objet et la pose cible du robot. Ces fonctions sont utilisées dans le pipeline main_real.py pour assurer une conversion fiable des coordonnées DINO (repère caméra) vers les coordonnées robot, ce qui est crucial pour le succès de la manipulation en mode réel.
"""
import zivid
import zivid.calibration
import numpy as np
import rtde_receive
import rtde_control
from scipy.spatial.transform import Rotation
from pipeline.config import CALIBRATION_FILE, ROBOT_IP

def run_calibration():
    app = zivid.Application()
    camera = app.connect_camera()
    
    # Connexion au UR16e
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)

    # 1. Définir des poses variées (X, Y, Z, rx, ry, rz)
    # TRÈS IMPORTANT : Vérifie que ces poses sont sécurisées pour le setup avant !
   
    """
     # Les 3 règles d'or pour tes poses :
     # Varier l'inclinaison : Ne reste pas toujours à la verticale ($RX=0, RY=3.14$).
     #  Incline le poignet de ±15° à ±25° (environ 0.3 à 0.4 radians).
     # Varier la hauteur (Z) : Prends des photos à 40 cm, 50 cm et 60 cm de la mire.
     # Rotation autour de l'axe Z (RZ) : Fais tourner l'outil sur lui-même.
    """
    calibration_poses = [
    # --- VUE CENTRALE (différentes hauteurs) ---
    [0.45,  0.00, 0.50,  0.0, 3.14, 0.0],
    [0.45,  0.00, 0.40,  0.0, 3.14, 0.0],
    [0.45,  0.00, 0.60,  0.0, 3.14, 0.0],

    # --- INCLINAISONS VERS L'AVANT / ARRIÈRE ---
    [0.50,  0.00, 0.45,  0.0, 2.80, 0.0], # Penché vers l'avant
    [0.40,  0.00, 0.45,  0.0, 3.40, 0.0], # Penché vers l'arrière

    # --- INCLINAISONS LATÉRALES (Gauche / Droite) ---
    [0.45,  0.10, 0.45,  0.3, 3.14, 0.0], # Décalé Y+ et incliné
    [0.45, -0.10, 0.45, -0.3, 3.14, 0.0], # Décalé Y- et incliné

    # --- ROTATIONS DE L'OUTIL (RZ) ---
    [0.45,  0.00, 0.45,  0.0, 3.14,  0.5], # Rotation outil +
    [0.45,  0.00, 0.45,  0.0, 3.14, -0.5], # Rotation outil -

    # --- POSES COMBINÉES (Les plus importantes pour la précision) ---
    [0.50,  0.10, 0.50,  0.2, 2.90,  0.3],
    [0.50, -0.10, 0.50, -0.2, 2.90, -0.3],
    [0.35,  0.10, 0.40,  0.2, 3.30,  0.3],
    [0.35, -0.10, 0.40, -0.2, 3.30, -0.3],
    
    # --- POSES ÉLOIGNÉES ---
    [0.55,  0.00, 0.55,  0.0, 3.14, 0.0],
    [0.45,  0.15, 0.45,  0.4, 3.14, 0.0]
    ]

    detection_results = []

    for i, pose in enumerate(calibration_poses):
        print(f"Déplacement vers pose {i+1}...")
        rtde_c.moveL(pose, 0.1, 0.1) # Vitesse lente par sécurité
        
        # Lire la pose réelle du TCP
        tcp_pose = rtde_r.getActualTCPPose()
        
        # Convertir en matrice 4x4 pour Zivid
        T_base_tcp = np.eye(4)
        T_base_tcp[:3, 3] = tcp_pose[:3]
        T_base_tcp[:3, :3] = Rotation.from_rotvec(tcp_pose[3:]).as_matrix()
        
        # Capturer l'image 3D
        frame = camera.capture()
        detection = zivid.calibration.detect_feature_points(frame.point_cloud())

        if detection.valid():
            hand_eye_input = zivid.calibration.HandEyeInput(
                zivid.calibration.Pose(T_base_tcp), 
                detection
            )
            detection_results.append(hand_eye_input)
            print("✅ Mire détectée !")
        else:
            print("❌ Mire non détectée, ajuste l'éclairage ou la position.")

    # 2. Calculer la calibration (Eye-in-Hand car caméra sur le robot)
    print("Calcul de la matrice de calibration...")
    result = zivid.calibration.calibrate_eye_in_hand(detection_results)

    if result.valid():
        T_tcp_cam = result.transform()
        # 3. SAUVEGARDE DU FICHIER
        np.save(CALIBRATION_FILE, T_tcp_cam)
        print(f"🏆 Calibration réussie ! Fichier sauvé dans : {CALIBRATION_FILE}")
    else:
        print("Fiasco : La calibration a échoué.")

if __name__ == "__main__":
    run_calibration()