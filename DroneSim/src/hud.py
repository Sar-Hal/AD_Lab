# src/hud.py
# ============================================================
#  HUD — on-screen display elements
# ============================================================

from ursina import *


CONTROLS_TEXT = (
    "Arrow Keys — move/bank  |  Space — ascend  |  Shift — descend  "
    "|  Z/X — yaw  |  C — cycle camera"
)


class HUD:
    """
    Heads-up display:
      • Controls hint bar at top
      • Speed / altitude readout (bottom-left)
      • Camera-mode label (bottom-right)
    """

    def __init__(self, drone, cam_ctrl):
        self.drone    = drone
        self.cam_ctrl = cam_ctrl

        # ── Controls bar ─────────────────────────────────
        self.controls = Text(
            text=CONTROLS_TEXT,
            position=(-0.5, 0.46),
            origin=(0, 0),
            scale=0.80,
            background=True,
            color=color.white,
        )

        # ── Telemetry readout ────────────────────────────
        self.telem = Text(
            text='',
            position=(-0.85, -0.43),
            origin=(-0.5, 0),
            scale=0.85,
            background=True,
            color=color.rgb(180, 230, 255),
        )

        # ── Camera mode label ────────────────────────────
        self.cam_label = Text(
            text='',
            position=(0.85, -0.43),
            origin=(0.5, 0),
            scale=0.85,
            background=True,
            color=color.rgb(255, 220, 100),
        )

    def update(self):
        d = self.drone
        speed = round(Vec3(d.velocity.x, 0, d.velocity.z).length(), 1)
        alt   = round(max(0, d.y - 0.7), 1)
        vspeed = round(d.velocity.y, 1)

        self.telem.text = (
            f"ALT  {alt:>6.1f} m\n"
            f"SPD  {speed:>6.1f} m/s\n"
            f"VSPD {vspeed:>+6.1f} m/s"
        )

        mode_nice = self.cam_ctrl.current_mode.replace('_', ' ').upper()
        self.cam_label.text = f"CAM: {mode_nice}"