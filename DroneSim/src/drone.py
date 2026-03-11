# src/drone.py
# ============================================================
#  Drone — physics + rich visual mesh
# ============================================================

from ursina import *
from config.settings import DRONE_PHYSICS as DP, DRONE_COLORS as DC


class Drone(Entity):
    """
    Quadcopter drone with:
      • Carbon-fibre-style dark body with coloured accents
      • Semi-transparent tinted propellers
      • Front cyan LEDs / rear red LEDs
      • Roll & pitch banking
      • Simple physics (gravity, drag, altitude-hold)
    """

    def __init__(self):
        super().__init__(
            model='cube',
            scale=(1.0, 0.35, 1.0),
            color=DC["body"],
        )
        self.position = Vec3(0, 6, 0)
        self.collider = BoxCollider(self, center=Vec3(0, 0, 0), size=Vec3(1, 0.35, 1))

        # ── Physics state ─────────────────────────────────
        self.velocity      = Vec3(0, 0, 0)
        self.acceleration  = Vec3(0, 0, 0)

        self.gravity              = DP["gravity"]
        self.linear_drag          = DP["linear_drag"]
        self.angular_drag         = DP["angular_drag"]
        self.altitude_hold_damping= DP["altitude_hold_damp"]

        self.move_power       = DP["move_power"]
        self.thrust_power     = DP["thrust_power"]
        self.yaw_rate         = DP["yaw_rate"]

        self.roll      = 0.0
        self.pitch     = 0.0
        self.roll_vel  = 0.0
        self.pitch_vel = 0.0

        self.max_bank           = DP["max_bank"]
        self.max_pitch          = DP["max_pitch"]
        self.collision_radius   = DP["collision_radius"]
        self.bounce_restitution = DP["bounce_restitution"]

        self._build_mesh()

    # ── Mesh construction ──────────────────────────────────

    def _build_mesh(self):
        """All child entities that make up the drone visual."""

        # Central body shell
        self.body_core = Entity(
            parent=self, model='cube',
            scale=(1.05, 0.22, 1.05),
            color=DC["body"],
        )
        self.body_top = Entity(
            parent=self, model='cube',
            scale=(0.68, 0.10, 0.68),
            y=0.15,
            color=DC["top_panel"],
        )
        # Camera/nose bump
        self.nose = Entity(
            parent=self, model='cube',
            scale=(0.22, 0.09, 0.18),
            position=(0, 0.05, 0.56),
            color=DC["nose"],
        )
        # Lens dot on nose
        self.lens = Entity(
            parent=self, model='sphere',
            scale=(0.07, 0.07, 0.04),
            position=(0, 0.05, 0.65),
            color=color.black,
        )

        # Cross arms
        self.arm_x = Entity(
            parent=self, model='cube',
            scale=(2.15, 0.07, 0.13),
            color=DC["arms"],
        )
        self.arm_z = Entity(
            parent=self, model='cube',
            scale=(0.13, 0.07, 2.15),
            color=DC["arms"],
        )

        # Motors (4 corners)
        motor_positions = [
            Vec3( 0.96, 0.04,  0.96),
            Vec3(-0.96, 0.04,  0.96),
            Vec3( 0.96, 0.04, -0.96),
            Vec3(-0.96, 0.04, -0.96),
        ]
        self.motors = []
        for pos in motor_positions:
            # flat sphere approximates a motor can — cylinder isn't built into Ursina
            m = Entity(
                parent=self, model='sphere',
                scale=(0.21, 0.09, 0.21),
                position=pos,
                color=DC["motor"],
            )
            self.motors.append(m)

        # Propellers — two blades per motor, slightly tinted
        prop_offsets = [
            Vec3( 0.96, 0.11,  0.96),
            Vec3(-0.96, 0.11,  0.96),
            Vec3( 0.96, 0.11, -0.96),
            Vec3(-0.96, 0.11, -0.96),
        ]
        self.props = []
        for pos in prop_offsets:
            blade_a = Entity(
                parent=self, model='cube',
                scale=(0.60, 0.012, 0.07),
                position=pos,
                color=DC["prop"],
            )
            blade_b = Entity(
                parent=self, model='cube',
                scale=(0.60, 0.012, 0.07),
                position=pos,
                rotation_y=90,
                color=DC["prop"],
            )
            self.props.extend([blade_a, blade_b])

        # Front LEDs (cyan)
        self.led_fl = Entity(
            parent=self, model='sphere',
            scale=0.065,
            position=( 0.95, -0.05,  0.95),
            color=DC["led_front"],
        )
        self.led_fr = Entity(
            parent=self, model='sphere',
            scale=0.065,
            position=(-0.95, -0.05,  0.95),
            color=DC["led_front"],
        )
        # Rear LEDs (red)
        self.led_rl = Entity(
            parent=self, model='sphere',
            scale=0.065,
            position=( 0.95, -0.05, -0.95),
            color=DC["led_rear"],
        )
        self.led_rr = Entity(
            parent=self, model='sphere',
            scale=0.065,
            position=(-0.95, -0.05, -0.95),
            color=DC["led_rear"],
        )

        # Landing gear — 4 small legs
        leg_positions = [
            ( 0.55, -0.22,  0.55),
            (-0.55, -0.22,  0.55),
            ( 0.55, -0.22, -0.55),
            (-0.55, -0.22, -0.55),
        ]
        for pos in leg_positions:
            Entity(
                parent=self, model='cube',
                scale=(0.06, 0.20, 0.06),
                position=Vec3(*pos),
                color=color.rgb(30, 30, 35),
            )

    # ── Per-frame helpers ──────────────────────────────────

    def spin_props(self, dt):
        """Spin all propeller blades."""
        spin_speed = max(180, 450 + abs(self.velocity.y) * 40)
        for prop in self.props:
            prop.rotation_y += spin_speed * dt

    def update_physics(self, dt):
        """Integrate velocity, clamp ground, decay attitude."""
        self.velocity  += self.acceleration * dt
        self.velocity  *= max(0.0, 1 - self.linear_drag * dt)
        self.position  += self.velocity * dt

        # Ground clamp
        if self.y < 0.7:
            self.y = 0.7
            if self.velocity.y < 0:
                self.velocity.y = 0

        # Attitude integration & decay
        self.roll  += self.roll_vel  * dt
        self.pitch += self.pitch_vel * dt
        self.roll_vel  *= max(0.0, 1 - self.angular_drag * dt * 4.0)
        self.pitch_vel *= max(0.0, 1 - self.angular_drag * dt * 4.0)

        self.roll  = clamp(self.roll,  -self.max_bank,  self.max_bank)
        self.pitch = clamp(self.pitch, -self.max_pitch, self.max_pitch)

        self.rotation_x = self.pitch
        self.rotation_z = self.roll