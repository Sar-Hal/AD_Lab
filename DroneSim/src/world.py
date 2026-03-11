# src/world.py
# ============================================================
#  World — ground plane, trees/towers, sky setup
# ============================================================

import math
import random
from ursina import *
from config.settings import WORLD, ENV_COLORS as EC


# ── Procedural tree / tower obstacle ──────────────────────────

class Obstacle(Entity):
    """
    A stylised tree: dark trunk + coloured canopy blob on top.
    Physics properties (impact velocity / spin) live here too.
    """

    def __init__(self, position):
        height = random.uniform(WORLD["obstacle_min_h"], WORLD["obstacle_max_h"])
        trunk_w = random.uniform(1.6, 2.6)

        # Trunk
        super().__init__(
            model='cube',
            scale=(trunk_w, height, trunk_w),
            position=(position[0], height / 2, position[1]),
            color=EC["obstacle_base"],
            collider='box',
        )
        self.hit_radius     = max(self.scale_x, self.scale_z) * 0.62
        self.impact_velocity = Vec3(0, 0, 0)
        self.impact_spin    = 0.0
        self.base_y         = self.y

        # Canopy (random size + colour)
        canopy_r = random.uniform(trunk_w * 0.9, trunk_w * 1.6)
        canopy_color = random.choice(EC["canopy"])
        self.canopy = Entity(
            parent=self,
            model='sphere',
            scale=(canopy_r / self.scale_x,
                   canopy_r * random.uniform(0.7, 1.1) / self.scale_y,
                   canopy_r / self.scale_z),
            y=0.52,          # sit on top of trunk (normalised)
            color=canopy_color,
            collider=None,   # collision handled by trunk
        )

        # Occasional secondary canopy for fuller look
        if random.random() < 0.5:
            offset_x = random.uniform(-0.25, 0.25)
            offset_z = random.uniform(-0.25, 0.25)
            r2 = canopy_r * random.uniform(0.55, 0.80)
            Entity(
                parent=self,
                model='sphere',
                scale=(r2 / self.scale_x, r2 * 0.9 / self.scale_y, r2 / self.scale_z),
                position=(offset_x, 0.45 + r2 * 0.3 / self.scale_y, offset_z),
                color=random.choice(EC["canopy"]),
                collider=None,
            )


# ── Ground ────────────────────────────────────────────────────

def build_ground():
    """Create the grass ground plane with a subtle grid texture."""
    ground = Entity(
        model='plane',
        scale=WORLD["ground_scale"],
        color=EC["ground"],
        texture='white_cube',
        texture_scale=WORLD["ground_tex_scale"],
        collider='box',
    )
    return ground


# ── Scatter decorations ───────────────────────────────────────

def build_small_rocks(count=30):
    """Low-poly rocks scattered on the ground for visual interest."""
    rocks = []
    for _ in range(count):
        x = random.uniform(-75, 75)
        z = random.uniform(-75, 75)
        s = random.uniform(0.2, 0.7)
        r = Entity(
            model='cube',
            scale=(s, s * 0.55, s),
            position=(x, s * 0.27, z),
            rotation_y=random.uniform(0, 360),
            color=color.rgb(
                random.randint(90, 130),
                random.randint(85, 125),
                random.randint(80, 120),
            ),
        )
        rocks.append(r)
    return rocks


def build_bushes(count=25):
    """Small rounded bushes for ground cover."""
    bushes = []
    for _ in range(count):
        x = random.uniform(-70, 70)
        z = random.uniform(-70, 70)
        s = random.uniform(0.4, 1.1)
        b = Entity(
            model='sphere',
            scale=(s, s * 0.65, s),
            position=(x, s * 0.32, z),
            color=color.rgb(
                random.randint(20, 50),
                random.randint(90, 140),
                random.randint(20, 50),
            ),
        )
        bushes.append(b)
    return bushes


# ── Master world builder ──────────────────────────────────────

def build_world():
    """
    Builds and returns:
        ground, obstacles (list), rocks (list), bushes (list)
    """
    ground    = build_ground()
    obstacles = _scatter_obstacles()
    rocks     = build_small_rocks()
    bushes    = build_bushes()
    return ground, obstacles, rocks, bushes


def _scatter_obstacles():
    obstacles = []
    attempts  = 0
    placed    = []
    min_sep   = 8.0   # minimum distance between trunks

    while len(obstacles) < WORLD["num_obstacles"] and attempts < 500:
        attempts += 1
        x = random.uniform(-68, 68)
        z = random.uniform(-68, 68)

        # Keep spawn area clear
        if abs(x) < 7 and abs(z) < 7:
            continue

        # Prevent overlap
        too_close = any(
            math.sqrt((x - px) ** 2 + (z - pz) ** 2) < min_sep
            for px, pz in placed
        )
        if too_close:
            continue

        obs = Obstacle((x, z))
        obstacles.append(obs)
        placed.append((x, z))

    return obstacles