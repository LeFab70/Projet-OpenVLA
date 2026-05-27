"""
# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : calibration.py
# Objectif    : Chargement matrice T_tcp_cam + transformation coords caméra → robot
#
# IMPORTANT — Calibration main-œil (eye-in-hand) :
#   Sans cette calibration, les coordonnées DINO (repère caméra)
#   ne peuvent PAS être converties en coordonnées robot fiables.
#   Guide ZIVID : https://support.zivid.com/en/latest/how-to/hand-eye-calibration
# =============================================================================
"""

from __future__ import annotations

import os
from typing import Tuple

import numpy as np

from .config import CALIBRATION_FILE, T_TCP_CAM_DEFAULT


def load_calibration() -> Tuple[np.ndarray, bool]:
    """Charge T_tcp_cam depuis fichier.

    Retour:
      - T_tcp_cam (4x4)
      - is_real: True si fichier présent, False si matrice défaut
    """
    if os.path.exists(CALIBRATION_FILE):
        T_tcp_cam = np.load(CALIBRATION_FILE)
        return T_tcp_cam.astype(np.float64), True
    return T_TCP_CAM_DEFAULT.copy(), False


def cam_to_robot(xyz_cam_m: np.ndarray, tcp_pose: list, T_tcp_cam: np.ndarray) -> np.ndarray:
    """Caméra -> base robot via base->tcp puis tcp->cam.

    - xyz_cam_m: (3,) en mètres dans le repère caméra
    - tcp_pose: [x,y,z,rx,ry,rz] (UR axis-angle)
    """
    P_cam = np.array([float(xyz_cam_m[0]), float(xyz_cam_m[1]), float(xyz_cam_m[2]), 1.0], dtype=np.float64)
    T_base_tcp = _pose_to_matrix(tcp_pose)
    P_base = T_base_tcp @ T_tcp_cam @ P_cam
    return P_base[:3]


def compute_distance_tcp_to_object(xyz_robot_obj: np.ndarray, tcp_pose: list) -> float:
    tcp_xyz = np.array(tcp_pose[:3], dtype=np.float64)
    return float(np.linalg.norm(np.asarray(xyz_robot_obj, dtype=np.float64) - tcp_xyz))


def _pose_to_matrix(pose: list) -> np.ndarray:
    """Pose UR axis-angle -> matrice homogène 4x4."""
    x, y, z, rx, ry, rz = [float(v) for v in pose]
    angle = float(np.sqrt(rx**2 + ry**2 + rz**2))
    T = np.eye(4, dtype=np.float64)
    T[0, 3] = x
    T[1, 3] = y
    T[2, 3] = z

    if angle < 1e-10:
        return T

    kx, ky, kz = rx / angle, ry / angle, rz / angle
    c, s = np.cos(angle), np.sin(angle)
    t = 1 - c

    T[0, 0] = t * kx * kx + c
    T[0, 1] = t * kx * ky - s * kz
    T[0, 2] = t * kx * kz + s * ky
    T[1, 0] = t * kx * ky + s * kz
    T[1, 1] = t * ky * ky + c
    T[1, 2] = t * ky * kz - s * kx
    T[2, 0] = t * kx * kz - s * ky
    T[2, 1] = t * ky * kz + s * kx
    T[2, 2] = t * kz * kz + c

    return T

