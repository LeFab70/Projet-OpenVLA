# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : gripper.py
# Objectif    : Contrôle pince Robotiq (abstraction + implémentation)
# =============================================================================

from __future__ import annotations

import time
from dataclasses import dataclass


class GripperBase:
    def open(self) -> None:  # pragma: no cover
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover
        raise NotImplementedError


@dataclass
class RobotiqConfig:
    # Placeholder : selon câblage / driver réel
    tool_digital_output: int = 0
    settle_s: float = 0.5


class RobotiqGripper(GripperBase):
    """Contrôle pince Robotiq via sorties outil UR (placeholder).

    Remarque : selon installation, Robotiq peut nécessiter URCap / Modbus / RS485.
    Ici on garde une interface stable + implémentation minimale (à adapter).
    """

    def __init__(self, rtde_control_iface, cfg: RobotiqConfig):
        self.rtde_c = rtde_control_iface
        self.cfg = cfg

    def open(self) -> None:
        self.rtde_c.setToolDigitalOut(self.cfg.tool_digital_output, False)
        time.sleep(self.cfg.settle_s)

    def close(self) -> None:
        self.rtde_c.setToolDigitalOut(self.cfg.tool_digital_output, True)
        time.sleep(self.cfg.settle_s)

