# 🚁 DroneSim

A first/third-person drone flight simulator built with [Ursina Engine](https://www.ursinaengine.org/).

---

## Project Structure

```
dronesim/
├── main.py                  ← Entry point — wires everything together
├── config/
│   └── settings.py          ← ALL tunable values (colours, physics, camera)
├── src/
│   ├── drone.py             ← Drone entity: mesh, physics, propeller spin
│   ├── world.py             ← Ground, trees, rocks, bushes
│   ├── camera_controller.py ← 4 camera modes with smooth lerp
│   ├── physics.py           ← Collision resolution & obstacle dynamics
│   └── hud.py               ← On-screen telemetry & controls hint
└── assets/
    ├── textures/            ← Drop .png/.jpg textures here
    └── models/              ← Drop .obj/.ursinamesh models here
```

---

## Installation

```bash
pip install ursina
python main.py
```

---

## Controls

| Key | Action |
|-----|--------|
| ↑ / ↓ | Pitch forward / backward |
| ← / → | Bank left / right |
| Space | Ascend |
| Shift | Descend |
| Z / X | Yaw left / right |
| C | Cycle camera mode |

---

## Camera Modes

| Mode | Description |
|------|-------------|
| `follow_back` | Classic 3rd-person chase cam |
| `top_down` | Overhead tactical view |
| `side_follow` | Cinematic side-on |
| `first_person` | FPV cockpit view |

---

## Customisation

Everything visual and physical lives in **`config/settings.py`**:

- `WORLD` — sky colour, ground scale, fog, number of trees
- `DRONE_PHYSICS` — gravity, drag, thrust power, bounce
- `DRONE_COLORS` — body, arms, props, LED colours
- `ENV_COLORS` — ground, trunk, canopy colour palette
- `CAMERA` — distances, heights, lerp speeds per mode

### Adding Textures

1. Drop your `.png` / `.jpg` into `assets/textures/`
2. In `world.py`, set `texture='assets/textures/your_file.png'` on the ground or obstacle entity.

### Adding Custom Models

1. Drop your `.obj` into `assets/models/`
2. Reference with `model='assets/models/your_model'` (no extension needed for `.obj`).

---

## Visual Upgrades at a Glance

| Feature | Where |
|---------|-------|
| Carbon-black drone body + coloured nose | `src/drone.py → _build_mesh()` |
| Cyan front LEDs / red rear LEDs | `src/drone.py → _build_mesh()` |
| Landing gear legs | `src/drone.py → _build_mesh()` |
| Semi-transparent tinted propellers | `src/drone.py → _build_mesh()` |
| Stylised trees: trunk + sphere canopy | `src/world.py → Obstacle` |
| Scattered rocks & bushes | `src/world.py → build_small_rocks/build_bushes` |
| Telemetry HUD (alt, speed, vspeed) | `src/hud.py` |
| Camera-mode label | `src/hud.py` |