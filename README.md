# 🚀 2D Space Shooter (Pygame)

A feature-complete 2D arcade space shooter built with Python and Pygame featuring multiple enemy types, boss encounters, dynamic particle effects, power-ups, smooth player ship tilting, and persistence.

---

## 🎮 Game Features

- **Smooth Ship Movement:** Ship leans dynamically when moving left/right using angle linear interpolation (`lerp`).
- **3 Enemy Types:**
  - **Scout:** Fast, fragile, low point reward.
  - **Standard Fighter:** Medium speed and health.
  - **Heavy Tank:** Slow, high HP with dynamic health bar.
- **Boss Battles:** Periodically spawns every 500 points with triple-shot lasers and a screen-wide health bar.
- **Power-Up System:**
  - **Heal (Cyan):** Restores 1 life.
  - **Double Shot (Magenta):** Grants double laser cannons for 5 seconds.
  - **Screen Bomb (Yellow):** Adds 1 screen-clearing bomb.
- **Secondary Weapon:** Trigger a screen-clearing bomb to erase all regular enemies, clear boss lasers, and deal massive damage to the boss.
- **High Score System:** Automatically saves and loads your local high score to `highscore.txt`.
- **Asset Fallback System:** Uses procedural color shapes if PNG files in `assets/` are missing.

---

## 🕹️ Controls

| Key | Action |
| :--- | :--- |
| **A / D** or **Left / Right** | Move Ship (Left / Right) |
| **SPACE** | Fire Primary Lasers |
| **B** or **LEFT SHIFT** | Trigger Screen Bomb |
| **R** | Restart Game (Game Over Screen) |
| **M** | Return to Main Menu (Game Over Screen) |

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher installed on your system.

### Steps

1. **Extract Project Archive:**
   Extract the `.zip` file into a directory of your choice.

2. **Set Up Virtual Environment (Optional, Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
