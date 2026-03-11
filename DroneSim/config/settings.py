# ============================================================
#  DroneSim — Settings & Palette
# ============================================================

from ursina import color

# ── World ────────────────────────────────────────────────────
WORLD = {
    "sky_color":          color.rgb(80, 140, 210),    # daytime blue
    "fog_color":          color.rgb(160, 200, 230),
    "fog_density":        0.006,
    "ground_scale":       180,
    "ground_color":       color.rgb(44, 130, 60),
    "ground_tex_scale":   (80, 80),
    "num_obstacles":      28,
    "obstacle_min_h":     4,
    "obstacle_max_h":     15,
}

# ── Drone physics ────────────────────────────────────────────
DRONE_PHYSICS = {
    "gravity":              -9.81,
    "linear_drag":          0.90,
    "angular_drag":         0.86,
    "altitude_hold_damp":   5.5,
    "move_power":           14.0,
    "thrust_power":         21.0,
    "yaw_rate":             75.0,
    "max_bank":             28,
    "max_pitch":            24,
    "collision_radius":     1.05,
    "bounce_restitution":   0.62,
}

# ── Drone look ───────────────────────────────────────────────
DRONE_COLORS = {
    "body":       color.rgb(20,  20,  25),     # near-black carbon
    "arms":       color.rgb(10,  10,  12),
    "top_panel":  color.rgb(40,  40,  50),
    "nose":       color.rgb(255, 60,  60),     # hot-red nose
    "motor":      color.rgb(50,  50,  55),
    "prop":       color.rgba(180, 220, 255, 160),  # translucent blue tint
    "led_front":  color.rgb(0,   220, 255),    # cyan LEDs
    "led_rear":   color.rgb(255, 30,  30),     # red rear LEDs
}

# ── Environment colours ──────────────────────────────────────
ENV_COLORS = {
    # Tree trunks / building walls
    "obstacle_base":   color.rgb(62,  42,  28),
    # Tree canopy variation – sampled randomly
    "canopy":         [
        color.rgb(34,  110,  40),
        color.rgb(26,   95,  35),
        color.rgb(50,  135,  52),
        color.rgb(20,   80,  30),
        color.rgb(60,  145,  55),
        color.rgb(38,  118,  44),
        color.rgb(15,   70,  25),   # dark understory
        color.rgb(70,  155,  60),   # bright highlight
    ],
    "ground":          color.rgb(44,  130,  60),
    "ground_line":     color.rgb(30,  90,   40),   # texture grid tint
}

# ── Camera ───────────────────────────────────────────────────
CAMERA = {
    "modes": ["follow_back", "top_down", "side_follow", "first_person"],
    "follow_dist":    11,
    "follow_height":  4.2,
    "follow_lerp":    5,
    "top_height":     28,
    "side_dist":      10,
    "side_height":    3.6,
    "fp_lerp":        9,
}