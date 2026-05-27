# =============================================================================
# Programmeur : Fabrice Kouonang
# Date        : 25 mai 2026
# Fichier     : ur_controller.py
# Objectif    : Contrôle UR16e (RTDE) + workspace safety
# =============================================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Pose6:
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float

    def as_list(self) -> list[float]:
        return [self.x, self.y, self.z, self.rx, self.ry, self.rz]


class URController:
    """Contrôle UR16e via RTDE avec garde-fous workspace.

    - 3) Calibration main-œil absente = bug majeur pour cam→robot, géré dans calibration.py
    - Workspace safety : aucune limite = dangereux. On impose des bornes via config.
    """

    def __init__(
        self,
        robot_ip: str,
        workspace: Optional[dict],
        safe_mode: bool,
        speed: float,
        accel: float,
    ):
        self.robot_ip = robot_ip
        self.workspace = workspace
        self.safe_mode = bool(safe_mode)
        self.speed = float(speed)
        self.accel = float(accel)

        self._rtde_c = None
        self._rtde_r = None

    def connect(self) -> None:
        if self.safe_mode:
            return
        import rtde_control
        import rtde_receive

        self._rtde_c = rtde_control.RTDEControlInterface(self.robot_ip)
        self._rtde_r = rtde_receive.RTDEReceiveInterface(self.robot_ip)

    def disconnect(self) -> None:
        if self._rtde_c is not None:
            try:
                self._rtde_c.stopScript()
            except Exception:
                pass

    def get_tcp_pose(self) -> Pose6:
        if self.safe_mode:
            # Pose simulée neutre (à surcharger dans main_sim via état local)
            return Pose6(0.0, 0.0, 0.0, 0.0, 3.14, 0.0)
        pose = self._rtde_r.getActualTCPPose()
        return Pose6(*[float(v) for v in pose])

    def moveL(self, target: Pose6) -> None:
        if self.workspace is None and not self.safe_mode:
            raise RuntimeError("WORKSPACE absent (danger). Configure `WORKSPACE` dans config.py.")

        if self.workspace is not None and not (
            self.workspace["x_min"] <= target.x <= self.workspace["x_max"]
            and self.workspace["y_min"] <= target.y <= self.workspace["y_max"]
            and self.workspace["z_min"] <= target.z <= self.workspace["z_max"]
        ):
            raise RuntimeError(
                f"Target hors workspace: xyz=({target.x:.3f},{target.y:.3f},{target.z:.3f})"
            )

        if self.safe_mode:
            print(f"[SAFE] moveL -> {target.as_list()}")
            return

        self._rtde_c.moveL(target.as_list(), speed=self.speed, acceleration=self.accel)

