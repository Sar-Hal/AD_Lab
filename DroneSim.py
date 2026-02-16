import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from dataclasses import dataclass

@dataclass
class Vector3:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def normalize(self):
        magnitude = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if magnitude > 0:
            return Vector3(self.x / magnitude, self.y / magnitude, self.z / magnitude)
        return self

class Drone:
    def __init__(self, x=0, y=5, z=0):
        # Position
        self.position = Vector3(x, y, z)
        
        # Velocity and acceleration
        self.velocity = Vector3(0, 0, 0)
        self.acceleration = Vector3(0, 0, 0)
        
        # Rotation (pitch, yaw, roll in radians)
        self.pitch = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        
        # Angular velocity
        self.pitch_vel = 0.0
        self.yaw_vel = 0.0
        self.roll_vel = 0.0
        
        # Physics parameters
        self.mass = 1.0
        self.thrust = 0.0
        self.drag_coefficient = 0.1
        self.gravity = -9.81
        self.max_tilt = 0.3  # Max pitch/roll in radians
        self.max_thrust = 20.0
        
    def draw(self):
        """Draw the drone as a simple + shape"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glRotatef(math.degrees(self.yaw), 0, 1, 0)
        glRotatef(math.degrees(self.pitch), 1, 0, 0)
        glRotatef(math.degrees(self.roll), 0, 0, 1)
        
        # Draw drone body (cube)
        glColor3f(1, 0, 0)
        self.draw_cube(0.2, 0.1, 0.2)
        
        # Draw propellers (arms)
        glColor3f(0, 1, 0)
        # Front arm
        glPushMatrix()
        glTranslatef(0.4, 0, 0)
        self.draw_cube(0.15, 0.05, 0.05)
        glPopMatrix()
        
        # Back arm
        glPushMatrix()
        glTranslatef(-0.4, 0, 0)
        self.draw_cube(0.15, 0.05, 0.05)
        glPopMatrix()
        
        # Right arm
        glPushMatrix()
        glTranslatef(0, 0, 0.4)
        self.draw_cube(0.05, 0.05, 0.15)
        glPopMatrix()
        
        # Left arm
        glPushMatrix()
        glTranslatef(0, 0, -0.4)
        self.draw_cube(0.05, 0.05, 0.15)
        glPopMatrix()
        
        # Draw thrust indicator
        if self.thrust > 0:
            glColor4f(1, 1, 0, 0.5)
            glPushMatrix()
            glTranslatef(0, -0.3, 0)
            self.draw_cube(0.1, self.thrust / 50, 0.1)
            glPopMatrix()
        
        glPopMatrix()
    
    def draw_cube(self, width, height, depth):
        """Draw a cube"""
        w, h, d = width / 2, height / 2, depth / 2
        glBegin(GL_QUADS)
        
        # Front face
        glVertex3f(-w, -h, d)
        glVertex3f(w, -h, d)
        glVertex3f(w, h, d)
        glVertex3f(-w, h, d)
        
        # Back face
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, -h, -d)
        
        # Top face
        glVertex3f(-w, h, -d)
        glVertex3f(-w, h, d)
        glVertex3f(w, h, d)
        glVertex3f(w, h, -d)
        
        # Bottom face
        glVertex3f(-w, -h, -d)
        glVertex3f(w, -h, -d)
        glVertex3f(w, -h, d)
        glVertex3f(-w, -h, d)
        
        # Right face
        glVertex3f(w, -h, -d)
        glVertex3f(w, h, -d)
        glVertex3f(w, h, d)
        glVertex3f(w, -h, d)
        
        # Left face
        glVertex3f(-w, -h, -d)
        glVertex3f(-w, -h, d)
        glVertex3f(-w, h, d)
        glVertex3f(-w, h, -d)
        
        glEnd()
    
    def update(self, dt):
        """Update drone physics"""
        # Apply gravity
        self.acceleration.y = self.gravity + (self.thrust / self.mass)
        
        # Apply drag
        self.acceleration.x = -self.velocity.x * self.drag_coefficient
        self.acceleration.z = -self.velocity.z * self.drag_coefficient
        
        # Update velocity
        self.velocity = self.velocity + self.acceleration * dt
        
        # Limit velocity
        max_vel = 15.0
        vel_mag = math.sqrt(self.velocity.x**2 + self.velocity.y**2 + self.velocity.z**2)
        if vel_mag > max_vel:
            self.velocity = self.velocity.normalize() * max_vel
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Ground collision
        if self.position.y < 0.5:
            self.position.y = 0.5
            self.velocity.y = 0
        
        # Update angular velocity
        self.pitch_vel *= 0.95  # Damping
        self.yaw_vel *= 0.95
        self.roll_vel *= 0.95
        
        self.pitch += self.pitch_vel * dt
        self.yaw += self.yaw_vel * dt
        self.roll += self.roll_vel * dt
        
        # Clamp rotations
        self.pitch = max(-math.pi/3, min(math.pi/3, self.pitch))
        self.roll = max(-math.pi/3, min(math.pi/3, self.roll))
    
    def apply_control(self, forward, strafe, rotate_left, rotate_right, up, down, rot_left, rot_right):
        """Apply control inputs"""
        control_force = 0.08
        angular_force = 0.1
        
        # Forward/backward movement (pitch)
        if forward:
            self.pitch_vel = min(0.3, self.pitch_vel + angular_force)
        if forward == 0 and self.pitch_vel > 0:
            self.pitch_vel -= angular_force
        
        # Strafe movement (roll)
        if strafe > 0:  # Right strafe
            self.roll_vel = max(-0.3, self.roll_vel - angular_force)
        elif strafe < 0:  # Left strafe
            self.roll_vel = min(0.3, self.roll_vel + angular_force)
        
        if strafe == 0 and abs(self.roll_vel) > 0:
            if self.roll_vel > 0:
                self.roll_vel -= angular_force
            else:
                self.roll_vel += angular_force
        
        # Thrust control
        if up:
            self.thrust = min(self.max_thrust, self.thrust + 0.5)
        if down:
            self.thrust = max(0, self.thrust - 0.5)
        
        # Natural thrust decay
        self.thrust *= 0.95
        
        # Rotation
        if rot_left:
            self.yaw_vel = min(1.0, self.yaw_vel + angular_force)
        if rot_right:
            self.yaw_vel = max(-1.0, self.yaw_vel - angular_force)

class Camera:
    def __init__(self):
        self.distance = 8.0
        self.height_offset = 3.0
        self.angle_x = 0.2
        self.angle_y = 0.0
    
    def update(self, drone):
        """Update camera to follow drone"""
        # Position camera behind and above the drone
        camera_x = drone.position.x - math.sin(drone.yaw) * self.distance * math.cos(self.angle_x)
        camera_y = drone.position.y + self.height_offset + math.sin(self.angle_x) * self.distance
        camera_z = drone.position.z - math.cos(drone.yaw) * self.distance * math.cos(self.angle_x)
        
        # Look at drone with slight lead
        look_ahead = 2.0
        look_x = drone.position.x + math.sin(drone.yaw) * look_ahead
        look_y = drone.position.y + 1.0
        look_z = drone.position.z + math.cos(drone.yaw) * look_ahead
        
        gluLookAt(camera_x, camera_y, camera_z,
                  look_x, look_y, look_z,
                  0, 1, 0)

def draw_ground():
    """Draw ground plane"""
    glColor3f(0.2, 0.8, 0.2)
    glBegin(GL_QUADS)
    size = 100
    glVertex3f(-size, 0, -size)
    glVertex3f(size, 0, -size)
    glVertex3f(size, 0, size)
    glVertex3f(-size, 0, size)
    glEnd()
    
    # Draw grid
    glColor3f(0.3, 0.9, 0.3)
    glBegin(GL_LINES)
    for i in range(-10, 11):
        glVertex3f(i * 10, 0.01, -100)
        glVertex3f(i * 10, 0.01, 100)
        glVertex3f(-100, 0.01, i * 10)
        glVertex3f(100, 0.01, i * 10)
    glEnd()

def draw_sky():
    """Draw sky"""
    glColor3f(0.5, 0.7, 1.0)
    # Sky is drawn by the background clear color

def draw_hud(drone):
    """Draw HUD information"""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, 1200, 800, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Disable depth test for HUD
    glDisable(GL_DEPTH_TEST)
    
    # Draw simple HUD elements (would need text rendering)
    # For now, we'll skip text and just show visual indicators
    
    glEnable(GL_DEPTH_TEST)
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def main():
    # Initialize Pygame and OpenGL
    pygame.init()
    display = (1200, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Drone Simulator - Controls: SPACE=Up, SHIFT=Down, ARROWS=Move, Z/X=Rotate")
    
    # Set up OpenGL
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.5, 0.7, 1.0, 1.0)
    
    # Perspective setup
    gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
    
    # Create game objects
    drone = Drone(0, 5, 0)
    camera = Camera()
    
    # Game loop variables
    clock = pygame.time.Clock()
    running = True
    
    print("=== DRONE SIMULATOR ===")
    print("Controls:")
    print("  UP/DOWN ARROW    - Pitch forward/backward")
    print("  LEFT/RIGHT ARROW - Roll left/right (bank)")
    print("  Z/X              - Rotate left/right (yaw)")
    print("  SPACE            - Increase thrust (go up)")
    print("  SHIFT            - Decrease thrust (go down)")
    print("  ESC              - Quit")
    print()
    
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time in seconds
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Get continuous key presses
        keys = pygame.key.get_pressed()
        
        forward = -1 if keys[pygame.K_UP] else (1 if keys[pygame.K_DOWN] else 0)
        strafe = 1 if keys[pygame.K_RIGHT] else (-1 if keys[pygame.K_LEFT] else 0)
        rotate_left = keys[pygame.K_z]
        rotate_right = keys[pygame.K_x]
        up = keys[pygame.K_SPACE]
        down = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Update drone
        drone.apply_control(forward, strafe, False, False, up, down, rotate_left, rotate_right)
        drone.update(dt)
        
        # Update camera
        camera.update(drone)
        
        # Render
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Set up 3D view
        camera.update(drone)
        
        # Draw scene
        draw_sky()
        draw_ground()
        drone.draw()
        
        # Swap buffers
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
