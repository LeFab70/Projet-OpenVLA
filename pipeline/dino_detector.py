# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : dino_detector.py
# Objectif    : Détection Grounding DINO + sauvegarde pixels (u,v) + bbox + XYZ caméra
# =============================================================================

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import torch
from PIL import Image
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

from .zivid_capture import validate_depth


@dataclass(frozen=True)
class DinoDetection:
    label: str
    conf: float
    bbox_xyxy: Tuple[float, float, float, float]
    pixel_uv: Tuple[int, int]  # (u,v) en pixels image
    point_cam_m: Tuple[float, float, float]  # (X,Y,Z) repère caméra, en m


class DinoDetector:
    def __init__(
        self,
        model_id: str,
        box_threshold: float,
        text_threshold: float,
        device: str,
        save_dir: Path,
    ):
        self.model_id = model_id
        self.box_threshold = float(box_threshold)
        self.text_threshold = float(text_threshold)
        self.device = device
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

        self.processor = AutoProcessor.from_pretrained(model_id)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(
            device
        )

        self._jsonl = self.save_dir / "dino_pixels.jsonl"

    def detect(
        self, image_rgb: np.ndarray, point_cloud_mm: np.ndarray, text_prompt: str
    ) -> Optional[DinoDetection]:
        pil = Image.fromarray(image_rgb)
        inputs = self.processor(
            images=pil, text=(text_prompt.strip() + "."), return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            box_threshold=self.box_threshold,
            text_threshold=self.text_threshold,
            target_sizes=[pil.size[::-1]],
        )

        h, w = image_rgb.shape[:2]
        best: Optional[DinoDetection] = None

        for result in results:
            for box, score, label in zip(
                result["boxes"], result["scores"], result["labels"]
            ):
                x1, y1, x2, y2 = [float(v) for v in box.tolist()]
                u = int(round((x1 + x2) / 2))
                v = int(round((y1 + y2) / 2))
                u = int(np.clip(u, 0, w - 1))
                v = int(np.clip(v, 0, h - 1))

                Xmm, Ymm, Zmm = [float(vv) for vv in point_cloud_mm[v, u]]
                if not np.isfinite(Xmm) or not np.isfinite(Ymm) or not np.isfinite(Zmm):
                    continue
                if not validate_depth(Zmm, label=str(label)):
                    continue

                Xm, Ym, Zm = Xmm / 1000.0, Ymm / 1000.0, Zmm / 1000.0

                det = DinoDetection(
                    label=str(label),
                    conf=float(score),
                    bbox_xyxy=(x1, y1, x2, y2),
                    pixel_uv=(u, v),
                    point_cam_m=(float(Xm), float(Ym), float(Zm)),
                )
                if best is None or det.conf > best.conf:
                    best = det

        if best is not None:
            self._append_pixels(best, text_prompt)
        return best

    # 2) Sauvegarder les pixels DINO (u,v) + bbox
    def _append_pixels(self, det: DinoDetection, text_prompt: str) -> None:
        rec = {
            "text_prompt": text_prompt,
            "label": det.label,
            "conf": det.conf,
            "bbox_xyxy": list(det.bbox_xyxy),
            "pixel_uv": list(det.pixel_uv),
            "point_cam_m": list(det.point_cam_m),
        }
        with self._jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

