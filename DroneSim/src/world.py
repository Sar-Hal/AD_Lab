# src/world.py
# ============================================================
#  World — full environment build
#  Includes: sky dome, sun, mountains, ground patches,
#            landing pad, fence perimeter, varied trees,
#            rocks, bushes, tall grass tufts, pond
# ============================================================

import random
import math
from ursina import *
from config.settings import WORLD, ENV_COLORS as EC


# ════════════════════════════════════════════════════════════
#  SKY
# ════════════════════════════════════════════════════════════

def build_sky():
    sky = Entity(
        model='sphere',
        scale=380,
        double_sided=True,
        color=color.rgb(90, 155, 220),
    )
    # Horizon band
    horizon = Entity(
        model='sphere',
        scale=374,
        double_sided=True,
        color=color.rgb(170, 205, 235),
    )
    horizon.scale_y = 0.08
    horizon.y = -8

    # Sun
    sun = Entity(
        model='sphere', scale=6,
        position=Vec3(120, 95, -160),
        color=color.rgb(255, 245, 200),
        unlit=True,
    )
    Entity(
        model='sphere', scale=11,
        position=Vec3(120, 95, -160),
        color=color.rgba(255, 230, 140, 55),
        unlit=True,
    )
    return sky, horizon, sun


# ════════════════════════════════════════════════════════════
#  GROUND
# ════════════════════════════════════════════════════════════

def build_ground():
    return Entity(
        model='plane',
        scale=WORLD["ground_scale"],
        color=EC["ground"],
        texture='white_cube',
        texture_scale=(90, 90),
        collider='box',
    )


def build_ground_patches(count=45):
    for _ in range(count):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        w = random.uniform(4, 20)
        d = random.uniform(4, 20)
        shade = random.randint(-20, 14)
        Entity(
            model='plane',
            scale=(w, 1, d),
            position=(x, 0.01, z),
            color=color.rgb(
                clamp(44 + shade, 10, 255),
                clamp(130 + shade, 10, 255),
                clamp(60 + shade, 10, 255),
            ),
        )


# ════════════════════════════════════════════════════════════
#  MOUNTAINS
# ════════════════════════════════════════════════════════════

def build_mountains():
    configs = [
        (-170,   0,  55, 38, 30, (80,  105, 80)),
        ( 170,   0,  55, 42, 30, (75,  100, 75)),
        (   0,-170,  60, 35, 28, (70,   95, 70)),
        (   0, 170,  50, 40, 28, (85,  110, 85)),
        (-130,-120,  45, 28, 25, (90,  115, 90)),
        ( 130,-120,  50, 32, 25, (78,  103, 78)),
        (-130, 120,  48, 30, 25, (82,  107, 82)),
        ( 130, 120,  52, 36, 25, (72,   97, 72)),
    ]
    for x, z, w, h, d, col in configs:
        r, g, b = col
        Entity(model='cube', scale=(w, h, d),
               position=(x, h*0.45, z), color=color.rgb(r, g, b))
        if h > 33:
            Entity(model='cube', scale=(w*0.35, h*0.22, d*0.35),
                   position=(x, h*0.84, z), color=color.rgb(230, 235, 240))
        Entity(model='cube', scale=(w*1.5, h*0.4, d*1.4),
               position=(x, h*0.18, z),
               color=color.rgb(min(255,r+15), min(255,g+15), min(255,b+15)))


# ════════════════════════════════════════════════════════════
#  LANDING PAD
# ════════════════════════════════════════════════════════════

def build_landing_pad():
    Entity(model='cube', scale=(6, 0.12, 6), position=(0, 0.06, 0),
           color=color.rgb(160, 160, 165))
    # Yellow border
    for dx, dz, sx, sz in [(0,2.7,5.6,0.3),(0,-2.7,5.6,0.3),(2.7,0,0.3,5.6),(-2.7,0,0.3,5.6)]:
        Entity(model='cube', scale=(sx, 0.13, sz), position=(dx, 0.07, dz),
               color=color.rgb(240, 200, 20))
    # H mark
    Entity(model='cube', scale=(3.2, 0.14, 0.5), position=(0, 0.08, 0),
           color=color.rgb(240, 200, 20))
    for dx in (-1.35, 1.35):
        Entity(model='cube', scale=(0.5, 0.14, 2.4), position=(dx, 0.08, 0),
               color=color.rgb(240, 200, 20))
    # Corner lights
    for cx, cz in [(2.5,2.5),(-2.5,2.5),(2.5,-2.5),(-2.5,-2.5)]:
        Entity(model='sphere', scale=0.18, position=(cx, 0.22, cz),
               color=color.rgb(255, 80, 80), unlit=True)


# ════════════════════════════════════════════════════════════
#  FENCE
# ════════════════════════════════════════════════════════════

def build_fence(half=82, post_gap=6):
    positions = []
    for x in range(-half, half+1, post_gap):
        positions += [(x, -half), (x, half)]
    for z in range(-half+post_gap, half, post_gap):
        positions += [(-half, z), (half, z)]

    for x, z in positions:
        Entity(model='cube', scale=(0.2, 1.8, 0.2),
               position=(x, 0.9, z), color=color.rgb(110, 75, 40))
        for ry in (0.5, 1.2):
            on_zedge = abs(z) == half
            Entity(model='cube',
                   scale=(post_gap if on_zedge else 0.15, 0.09,
                          post_gap if not on_zedge else 0.15),
                   position=(x, ry, z), color=color.rgb(130, 90, 50))


# ════════════════════════════════════════════════════════════
#  TREES (OBSTACLES)
# ════════════════════════════════════════════════════════════

TRUNK_COLORS = [
    color.rgb(72, 48, 28), color.rgb(58, 38, 22),
    color.rgb(85, 58, 32), color.rgb(62, 42, 25),
]


class Obstacle(Entity):
    def __init__(self, position):
        height  = random.uniform(WORLD["obstacle_min_h"], WORLD["obstacle_max_h"])
        trunk_w = random.uniform(0.55, 1.1)

        super().__init__(
            model='cube',
            scale=(trunk_w, height, trunk_w),
            position=(position[0], height / 2, position[1]),
            color=random.choice(TRUNK_COLORS),
            collider='box',
        )
        self.hit_radius      = max(self.scale_x, self.scale_z) * 0.75
        self.impact_velocity = Vec3(0, 0, 0)
        self.impact_spin     = 0.0
        self.base_y          = self.y
        self._add_canopy(height, trunk_w)

    def _add_canopy(self, height, trunk_w):
        num_layers = random.randint(2, 4)
        base_r     = trunk_w * random.uniform(2.0, 3.4)
        for i in range(num_layers):
            frac = i / max(num_layers - 1, 1)
            r    = base_r * (1.0 - frac * 0.45)
            y    = 0.46 + frac * 0.28
            j    = random.uniform(-0.08, 0.08)
            Entity(
                parent=self, model='sphere',
                scale=(r/self.scale_x, r*random.uniform(0.75,1.05)/self.scale_y, r/self.scale_z),
                position=(j, y, j),
                color=random.choice(EC["canopy"]),
                collider=None,
            )


# ════════════════════════════════════════════════════════════
#  GROUND DETAIL
# ════════════════════════════════════════════════════════════

def build_rocks(count=40):
    for _ in range(count):
        x = random.uniform(-78, 78)
        z = random.uniform(-78, 78)
        s = random.uniform(0.15, 0.9)
        Entity(
            model='cube',
            scale=(s, s*random.uniform(0.38,0.65), s*random.uniform(0.7,1.3)),
            position=(x, s*0.22, z),
            rotation_y=random.uniform(0, 360),
            color=color.rgb(
                random.randint(95,145), random.randint(90,135), random.randint(85,130)),
        )


def build_bushes(count=45):
    for _ in range(count):
        x = random.uniform(-75, 75)
        z = random.uniform(-75, 75)
        s = random.uniform(0.5, 1.5)
        col = color.rgb(random.randint(18,50), random.randint(88,155), random.randint(18,50))
        Entity(model='sphere', scale=(s, s*0.6, s), position=(x, s*0.3, z), color=col)
        Entity(model='sphere',
               scale=(s*0.7, s*0.55, s*0.7),
               position=(x+random.uniform(-0.4,0.4), s*0.45, z+random.uniform(-0.4,0.4)),
               color=color.rgb(random.randint(22,52), random.randint(95,160), random.randint(22,52)))


def build_grass_tufts(count=90):
    for _ in range(count):
        x = random.uniform(-78, 78)
        z = random.uniform(-78, 78)
        h = random.uniform(0.3, 1.0)
        col = color.rgb(random.randint(30,65), random.randint(110,175), random.randint(25,55))
        for angle in (0, 60, 120):
            Entity(model='cube', scale=(0.06, h, 0.5),
                   position=(x, h*0.5, z), rotation_y=angle, color=col)


def build_water_pond():
    Entity(model='plane', scale=(12,1,8), position=(-28, 0.05, 18),
           color=color.rgb(55, 120, 180), texture='white_cube', texture_scale=(6,4))
    Entity(model='plane', scale=(9,1,5.5), position=(-28, 0.06, 18),
           color=color.rgb(90, 160, 215))
    for _ in range(16):
        rh = random.uniform(0.7, 1.5)
        Entity(model='cube', scale=(0.07, rh, 0.07),
               position=(-28+random.uniform(-6,6), rh*0.5, 18+random.uniform(-4,4)),
               color=color.rgb(60, 100, 40))


def build_path():
    """Dirt path winding from landing pad toward the forest."""
    segments = [
        (0,  8,  2.0, 5),
        (1, 15,  2.0, 5),
        (3, 22,  1.8, 5),
        (6, 28,  1.6, 4),
    ]
    for x, z, w, d in segments:
        Entity(model='plane', scale=(w, 1, d), position=(x, 0.02, z),
               color=color.rgb(148, 118, 80))


# ════════════════════════════════════════════════════════════
#  MASTER BUILDER
# ════════════════════════════════════════════════════════════

def build_world():
    build_sky()
    ground    = build_ground()
    build_ground_patches()
    build_mountains()
    build_landing_pad()
    build_rocks()
    build_bushes()
    build_grass_tufts()
    build_water_pond()
    build_path()
    build_fence()
    obstacles = _scatter_obstacles()
    return ground, obstacles


def _scatter_obstacles():
    obstacles = []
    attempts  = 0
    placed    = []
    min_sep   = 7.0

    while len(obstacles) < WORLD["num_obstacles"] and attempts < 600:
        attempts += 1
        x = random.uniform(-70, 70)
        z = random.uniform(-70, 70)
        if abs(x) < 9 and abs(z) < 9:
            continue
        if -36 < x < -18 and 12 < z < 26:
            continue
        too_close = any(
            math.sqrt((x-px)**2 + (z-pz)**2) < min_sep
            for px, pz in placed
        )
        if too_close:
            continue
        obs = Obstacle((x, z))
        obstacles.append(obs)
        placed.append((x, z))

    return obstacles