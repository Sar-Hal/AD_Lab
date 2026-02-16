from ursina import *
import random


app = Ursina()
window.title = 'Drone Simulator'
window.borderless = False
window.color = color.rgb(135, 206, 235)


ground = Entity(
    model='plane',
    scale=180,
    color=color.rgb(30, 170, 70),
    texture='white_cube',
    texture_scale=(80, 80),
    collider='box'
)


obstacles = []
for _ in range(18):
    height = random.uniform(3, 12)
    obstacle = Entity(
        model='cube',
        scale=(2.2, height, 2.2),
        position=(random.uniform(-70, 70), height / 2, random.uniform(-70, 70)),
        color=color.rgb(35, 120, 40),
        collider='box'
    )
    obstacle.hit_radius = max(obstacle.scale_x, obstacle.scale_z) * 0.62
    obstacle.impact_velocity = Vec3(0, 0, 0)
    obstacle.impact_spin = 0.0
    obstacle.base_y = obstacle.y
    obstacles.append(obstacle)


class Drone(Entity):
    def __init__(self):
        super().__init__(model='cube', scale=(1.0, 0.35, 1.0), color=color.azure)
        self.position = Vec3(0, 6, 0)
        self.collider = BoxCollider(self, center=Vec3(0, 0, 0), size=Vec3(1, 0.35, 1))

        self.velocity = Vec3(0, 0, 0)
        self.acceleration = Vec3(0, 0, 0)

        self.gravity = -9.81
        self.linear_drag = 0.9
        self.angular_drag = 0.86
        self.altitude_hold_damping = 5.5

        self.move_power = 14.0
        self.thrust_power = 21.0
        self.yaw_rate = 75.0

        self.roll = 0.0
        self.pitch = 0.0
        self.roll_vel = 0.0
        self.pitch_vel = 0.0

        self.max_bank = 28
        self.max_pitch = 24
        self.collision_radius = 1.05
        self.bounce_restitution = 0.62

        self._build_mesh()

    def _build_mesh(self):
        self.body_core = Entity(parent=self, model='cube', scale=(1.05, 0.22, 1.05), color=color.light_gray)
        self.body_top = Entity(parent=self, model='cube', scale=(0.72, 0.12, 0.72), y=0.14, color=color.white)
        self.nose = Entity(parent=self, model='cube', scale=(0.25, 0.1, 0.18), position=(0, 0.07, 0.55), color=color.red)

        self.arm_x = Entity(parent=self, model='cube', scale=(2.15, 0.07, 0.14), color=color.black)
        self.arm_z = Entity(parent=self, model='cube', scale=(0.14, 0.07, 2.15), color=color.black)

        self.motor_fl = Entity(parent=self, model='sphere', scale=(0.22, 0.08, 0.22), position=(0.96, 0.03, 0.96), color=color.dark_gray)
        self.motor_fr = Entity(parent=self, model='sphere', scale=(0.22, 0.08, 0.22), position=(-0.96, 0.03, 0.96), color=color.dark_gray)
        self.motor_bl = Entity(parent=self, model='sphere', scale=(0.22, 0.08, 0.22), position=(0.96, 0.03, -0.96), color=color.dark_gray)
        self.motor_br = Entity(parent=self, model='sphere', scale=(0.22, 0.08, 0.22), position=(-0.96, 0.03, -0.96), color=color.dark_gray)

        self.prop_fl = Entity(parent=self, model='cube', scale=(0.58, 0.01, 0.08), position=(0.96, 0.1, 0.96), color=color.rgba(30, 30, 30, 180))
        self.prop_fr = Entity(parent=self, model='cube', scale=(0.58, 0.01, 0.08), position=(-0.96, 0.1, 0.96), color=color.rgba(30, 30, 30, 180))
        self.prop_bl = Entity(parent=self, model='cube', scale=(0.58, 0.01, 0.08), position=(0.96, 0.1, -0.96), color=color.rgba(30, 30, 30, 180))
        self.prop_br = Entity(parent=self, model='cube', scale=(0.58, 0.01, 0.08), position=(-0.96, 0.1, -0.96), color=color.rgba(30, 30, 30, 180))

    def spin_props(self, dt):
        spin_speed = max(160, 420 + abs(self.velocity.y) * 35)
        self.prop_fl.rotation_y += spin_speed * dt
        self.prop_fr.rotation_y += spin_speed * dt
        self.prop_bl.rotation_y += spin_speed * dt
        self.prop_br.rotation_y += spin_speed * dt

    def update_physics(self, dt):
        self.velocity += self.acceleration * dt
        self.velocity *= max(0.0, 1 - self.linear_drag * dt)
        self.position += self.velocity * dt

        if self.y < 0.7:
            self.y = 0.7
            if self.velocity.y < 0:
                self.velocity.y = 0

        self.roll += self.roll_vel * dt
        self.pitch += self.pitch_vel * dt
        self.roll_vel *= max(0.0, 1 - self.angular_drag * dt * 4.0)
        self.pitch_vel *= max(0.0, 1 - self.angular_drag * dt * 4.0)

        self.roll = clamp(self.roll, -self.max_bank, self.max_bank)
        self.pitch = clamp(self.pitch, -self.max_pitch, self.max_pitch)

        self.rotation_x = self.pitch
        self.rotation_z = self.roll


drone = Drone()


camera_modes = ['follow_back', 'top_down', 'side_follow', 'first_person']
camera_mode_index = 0


def update_camera():
    mode = camera_modes[camera_mode_index]

    if mode == 'follow_back':
        target = drone.position + drone.forward * 2.5
        camera.position = lerp(camera.position, drone.position - drone.forward * 11 + Vec3(0, 4.2, 0), time.dt * 5)
        camera.look_at(target)
        camera.rotation_z = 0

    elif mode == 'top_down':
        camera.position = lerp(camera.position, drone.position + Vec3(0, 28, 0.01), time.dt * 5)
        camera.look_at(drone.position)
        camera.rotation_z = 0

    elif mode == 'side_follow':
        camera.position = lerp(camera.position, drone.position + drone.right * 10 + Vec3(0, 3.6, 0), time.dt * 5)
        camera.look_at(drone.position + drone.forward * 2)
        camera.rotation_z = 0

    elif mode == 'first_person':
        camera.position = lerp(camera.position, drone.position + Vec3(0, 0.65, 0), time.dt * 9)
        camera.rotation = lerp(camera.rotation, Vec3(drone.rotation_x, drone.rotation_y, 0), time.dt * 8)


def update_obstacles(dt):
    for tower in obstacles:
        tower.position += tower.impact_velocity * dt
        tower.rotation_y += tower.impact_spin * dt

        tower.impact_velocity *= max(0.0, 1 - 3.8 * dt)
        tower.impact_spin *= max(0.0, 1 - 4.2 * dt)

        if tower.y != tower.base_y:
            tower.y = tower.base_y


def resolve_tower_collisions():
    for tower in obstacles:
        offset = Vec3(drone.x - tower.x, 0, drone.z - tower.z)
        distance = offset.length()
        minimum_distance = drone.collision_radius + tower.hit_radius

        if distance >= minimum_distance:
            continue

        normal = offset.normalized() if distance > 0.0001 else Vec3(1, 0, 0)
        penetration = minimum_distance - distance
        drone.position += normal * penetration

        relative_velocity = drone.velocity - tower.impact_velocity
        separating_speed = relative_velocity.dot(normal)

        if separating_speed < 0:
            impulse = -(1 + drone.bounce_restitution) * separating_speed
            drone.velocity += normal * impulse
            tower.impact_velocity -= normal * min(8.5, impulse * 0.45)
            tower.impact_spin += random.uniform(-120, 120) * min(1.0, abs(separating_speed) / 10.0)
            drone.velocity.y = max(drone.velocity.y, 0.8)


def input(key):
    global camera_mode_index

    if key == 'c':
        camera_mode_index = (camera_mode_index + 1) % len(camera_modes)


def update():
    dt = time.dt

    hover_force = -drone.gravity
    drone.acceleration = Vec3(0, drone.gravity + hover_force, 0)

    if held_keys['up arrow']:
        drone.acceleration += drone.forward * drone.move_power
        drone.pitch_vel += 55 * dt
    if held_keys['down arrow']:
        drone.acceleration -= drone.forward * drone.move_power
        drone.pitch_vel -= 55 * dt

    if held_keys['left arrow']:
        drone.acceleration -= drone.right * drone.move_power * 0.8
        drone.roll_vel += 70 * dt
    if held_keys['right arrow']:
        drone.acceleration += drone.right * drone.move_power * 0.8
        drone.roll_vel -= 70 * dt

    if held_keys['space']:
        drone.acceleration.y += drone.thrust_power
    if held_keys['shift']:
        drone.acceleration.y -= drone.thrust_power * 0.72
    if not held_keys['space'] and not held_keys['shift']:
        drone.acceleration.y += -drone.velocity.y * drone.altitude_hold_damping

    if held_keys['z']:
        drone.rotation_y -= drone.yaw_rate * dt
    if held_keys['x']:
        drone.rotation_y += drone.yaw_rate * dt

    if not held_keys['left arrow'] and not held_keys['right arrow']:
        drone.roll *= max(0.0, 1 - dt * 2.3)
    if not held_keys['up arrow'] and not held_keys['down arrow']:
        drone.pitch *= max(0.0, 1 - dt * 2.3)

    drone.spin_props(dt)
    drone.update_physics(dt)
    resolve_tower_collisions()
    update_obstacles(dt)
    update_camera()


info = Text(
    text='Controls: Arrow Keys move/bank | Space up | Shift down | Z/X yaw | C camera mode | Towers are crashable',
    position=(-0.5, 0.46),
    origin=(0, 0),
    scale=0.95,
    background=True
)


app.run()
