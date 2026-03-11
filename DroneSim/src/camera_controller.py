# src/camera_controller.py
# ============================================================
#  Camera Controller — 4 modes, smooth lerp
# ============================================================

from ursina import *
from config.settings import CAMERA as CAM


class CameraController:
    """
    Manages all camera modes and provides cycle() to switch.

    Modes:
      follow_back  – classic third-person chase
      top_down     – overhead tactical view
      side_follow  – cinematic side-on
      first_person – cockpit / FPV
    """

    def __init__(self, drone):
        self.drone      = drone
        self.modes      = CAM["modes"]
        self.mode_index = 0

    @property
    def current_mode(self):
        return self.modes[self.mode_index]

    def cycle(self):
        self.mode_index = (self.mode_index + 1) % len(self.modes)

    def update(self):
        dt   = time.dt
        d    = self.drone
        mode = self.current_mode

        if mode == 'follow_back':
            target = d.position + d.forward * 2.5
            desired = d.position - d.forward * CAM["follow_dist"] + Vec3(0, CAM["follow_height"], 0)
            camera.position = lerp(camera.position, desired, dt * CAM["follow_lerp"])
            camera.look_at(target)
            camera.rotation_z = 0

        elif mode == 'top_down':
            desired = d.position + Vec3(0, CAM["top_height"], 0.01)
            camera.position = lerp(camera.position, desired, dt * CAM["follow_lerp"])
            camera.look_at(d.position)
            camera.rotation_z = 0

        elif mode == 'side_follow':
            desired = d.position + d.right * CAM["side_dist"] + Vec3(0, CAM["side_height"], 0)
            camera.position = lerp(camera.position, desired, dt * CAM["follow_lerp"])
            camera.look_at(d.position + d.forward * 2)
            camera.rotation_z = 0

        elif mode == 'first_person':
            desired = d.position + Vec3(0, 0.65, 0)
            camera.position = lerp(camera.position, desired, dt * CAM["fp_lerp"])
            target_rot = Vec3(d.rotation_x, d.rotation_y, 0)
            camera.rotation = lerp(camera.rotation, target_rot, dt * 8)