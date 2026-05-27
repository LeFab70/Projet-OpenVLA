"""
# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : zivid_capture.py
# Objectif    : Capture ZIVID Two + validation distance min/max
# =============================================================================
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple

import numpy as np
import zivid
from PIL import Image

from .config import SAVE_DIR, ZIVID_Z_MAX, ZIVID_Z_MIN


@dataclass(frozen=True)
class ZividFrame:
    image_rgb: np.ndarray  # (H,W,3) uint8
    point_cloud_mm: np.ndarray  # (H,W,3) float32, mm (NaN where invalid)


def init_camera() -> Tuple[zivid.Application, object]:
    app = zivid.Application()
    camera = app.connect_camera()
    print(f"✅ Caméra ZIVID connectée : {camera.info.model_name}")
    return app, camera


def capture(camera) -> Tuple[np.ndarray, np.ndarray]:
    settings = zivid.Settings(
        acquisitions=[zivid.Settings.Acquisition()],
        color=zivid.Settings2D(acquisitions=[zivid.Settings2D.Acquisition()]),
    )
    frame = camera.capture_2d_3d(settings)
    image_rgba = frame.frame_2d().image_rgba_srgb().copy_data()
    image_rgb = image_rgba[:, :, :3]
    point_cloud = frame.point_cloud().copy_data("xyz").astype(np.float32)  # mm
    return image_rgb, point_cloud


def validate_depth(Z_mm: float, label: str = "") -> bool:
    Z_m = float(Z_mm) / 1000.0
    if np.isnan(Z_mm):
        print(f"  ⚠️  {label} → profondeur NaN (point non mesuré)")
        return False
    if Z_m < ZIVID_Z_MIN:
        print(f"  ⚠️  {label} → trop proche : Z={Z_m:.3f}m (min={ZIVID_Z_MIN}m)")
        return False
    if Z_m > ZIVID_Z_MAX:
        print(f"  ⚠️  {label} → trop loin : Z={Z_m:.3f}m (max={ZIVID_Z_MAX}m)")
        return False
    return True


def save_capture(image_rgb: np.ndarray, filename: str = "capture.png") -> str:
    os.makedirs(SAVE_DIR, exist_ok=True)
    path = os.path.join(SAVE_DIR, filename)
    Image.fromarray(image_rgb).save(path)
    print(f"  💾 Image sauvegardée : {path}")
    return path


