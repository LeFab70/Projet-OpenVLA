# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : vla_controller.py
# Objectif    : OpenVLA — inférence + prompt dynamique (distance TCP → objet)
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor


@dataclass(frozen=True)
class VlaAction:
    dx: float
    dy: float
    dz: float
    rx: float
    ry: float
    rz: float
    gripper: float


class VLAController:
    def __init__(self, model_path: str, device: str, unnorm_key: str):
        self.model_path = model_path
        self.device = device
        self.unnorm_key = unnorm_key

        self.processor = AutoProcessor.from_pretrained(
            model_path, trust_remote_code=True
        )
        self.model = AutoModelForVision2Seq.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        ).to(device)

    def build_prompt_dynamic(
        self, label: str, remaining_xyz_base_m: Tuple[float, float, float]
    ) -> str:
        # 6) Prompt dynamique : rester cohérent avec un modèle entraîné sur deltas
        dx, dy, dz = remaining_xyz_base_m
        dist = float(np.linalg.norm(np.array([dx, dy, dz], dtype=float)))
        return (
            "In: The robot end-effector is not yet at the target. "
            f"Remaining displacement to reach the {label} is "
            f"dx={dx:+.3f}m dy={dy:+.3f}m dz={dz:+.3f}m "
            f"(distance={dist:.3f}m). "
            "What action (delta) should the robot take next to pick it up?\nOut:"
        )

    def build_prompt_minimal(self, label: str) -> str:
        return (
            "In: What action should the robot take to "
            f"pick up the {label}?\nOut:"
        )

    def predict_action(self, prompt: str, image_rgb: np.ndarray) -> VlaAction:
        pil = Image.fromarray(image_rgb).resize((224, 224))
        inputs = self.processor(prompt, pil).to(self.device, dtype=torch.bfloat16)
        action = self.model.predict_action(
            **inputs,
            unnorm_key=self.unnorm_key,
            do_sample=False,
        )
        return VlaAction(
            dx=float(action[0]),
            dy=float(action[1]),
            dz=float(action[2]),
            rx=float(action[3]),
            ry=float(action[4]),
            rz=float(action[5]),
            gripper=float(action[6]),
        )

