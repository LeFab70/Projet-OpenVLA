"""
# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : config.py
# Objectif    : Toutes les constantes du pipeline OpenVLA + UR16e + ZIVID
# =============================================================================

Ce module reste volontairement en constantes "plates" (facile à modifier),
et sert de source unique de vérité pour tous les autres modules du dossier `pipeline/`.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

# ─────────────────────────────────────────
# 🤖 ROBOT (UR16e)
# ─────────────────────────────────────────
ROBOT_IP = "192.168.1.10"
ROBOT_SPEED = 0.05
ROBOT_ACCEL = 0.10
APPROACH_SPEED = 0.30
APPROACH_ACCEL = 0.50
APPROACH_Z = 0.15

# OpenVLA -> robot : attention, ici SCALE est bien un facteur "delta step"
SCALE = 0.02
MAX_STEPS = 20

# Workspace sécurisé UR16e (m, repère base robot)
# IMPORTANT : aucune limite workspace = dangereux
WORKSPACE = {
    "x_min": -0.80,
    "x_max": 0.80,
    "y_min": -0.80,
    "y_max": 0.80,
    "z_min": 0.05,
    "z_max": 0.90,
}

# ─────────────────────────────────────────
# 📷 CAMÉRA ZIVID Two
# ─────────────────────────────────────────
ZIVID_Z_MIN = 0.30  # m
ZIVID_Z_MAX = 1.50  # m

# ─────────────────────────────────────────
# 🔧 CALIBRATION MAIN-ŒIL (eye-in-hand)
# ─────────────────────────────────────────
CALIBRATION_FILE = r"C:\Users\Etudiant\models\calibration\T_tcp_cam.npy"
T_TCP_CAM_DEFAULT = np.eye(4, dtype=np.float64)

# ─────────────────────────────────────────
# 🎯 GROUNDING DINO
# ─────────────────────────────────────────
DINO_MODEL_ID = "IDEA-Research/grounding-dino-base"
BOX_THRESHOLD = 0.25
TEXT_THRESHOLD = 0.20
DINO_EVERY_N_STEPS = 5

# ─────────────────────────────────────────
# 🤖 OPENVLA
# ─────────────────────────────────────────
MODEL_PATH = r"C:\Users\Etudiant\models\openvla-7b"
UNNORM_KEY = "bridge_orig"
GRIPPER_THRESHOLD = 0.40

# ─────────────────────────────────────────
# 🤏 PINCE ROBOTIQ
# ─────────────────────────────────────────
ROBOTIQ_PORT = "/dev/ttyUSB0"  # Windows: "COM3"
ROBOTIQ_SPEED = 128
ROBOTIQ_FORCE = 128
ROBOTIQ_OPEN = 0
ROBOTIQ_CLOSED = 255

# ─────────────────────────────────────────
# 💾 FICHIERS
# ─────────────────────────────────────────
SAVE_DIR = r"C:\Users\Etudiant\StageFab\OpenVLA\outputs"
os.makedirs(SAVE_DIR, exist_ok=True)

RUNS_DIR = Path("outputs") / "pipeline_runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)

