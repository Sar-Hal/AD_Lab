# src/physics.py
# ============================================================
#  Physics helpers — collision resolution, obstacle dynamics
# ============================================================

import random
from ursina import *


def resolve_tower_collisions(drone, obstacles):
    """
    Cylinder-vs-cylinder sweep for each obstacle trunk.
    Pushes the drone out, applies bounce impulse, and knocks
    the tree with a random spin.
    """
    for tower in obstacles:
        offset   = Vec3(drone.x - tower.x, 0, drone.z - tower.z)
        distance = offset.length()
        min_dist = drone.collision_radius + tower.hit_radius

        if distance >= min_dist:
            continue

        normal      = offset.normalized() if distance > 0.0001 else Vec3(1, 0, 0)
        penetration = min_dist - distance
        drone.position += normal * penetration

        rel_vel       = drone.velocity - tower.impact_velocity
        sep_speed     = rel_vel.dot(normal)

        if sep_speed < 0:
            impulse = -(1 + drone.bounce_restitution) * sep_speed
            drone.velocity        += normal * impulse
            tower.impact_velocity -= normal * min(8.5, impulse * 0.45)
            tower.impact_spin     += (
                random.uniform(-120, 120)
                * min(1.0, abs(sep_speed) / 10.0)
            )
            drone.velocity.y = max(drone.velocity.y, 0.8)


def update_obstacles(obstacles, dt):
    """Decay impact_velocity / spin on each obstacle."""
    for tower in obstacles:
        tower.position += tower.impact_velocity * dt
        tower.rotation_y += tower.impact_spin * dt

        tower.impact_velocity *= max(0.0, 1 - 3.8 * dt)
        tower.impact_spin     *= max(0.0, 1 - 4.2 * dt)

        # Re-pin Y so trees don't drift vertically
        if tower.y != tower.base_y:
            tower.y = tower.base_y