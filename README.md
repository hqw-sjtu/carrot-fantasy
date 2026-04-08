# 🎮 Carrot Fantasy (保卫萝卜)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![pygame](https://img.shields.io/badge/pygame-2.5+-green.svg)](https://www.pygame.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.3.1-orange.svg)]

> A polished tower defense game based on Python & Pygame - Guard your carrot from waves of monsters!

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/hqw-sjtu/carrot-fantasy.git
cd carrot-fantasy

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the game
python src/main.py
```

Or use the launcher:
```bash
bash start.sh
```

## 🕹️ Controls

### 🎮 Gameplay Controls

| Key | Action | Key | Action |
|-----|--------|-----|--------|
| `1-5` | Select tower type | `U` | Upgrade selected tower |
| `Mouse` | Place/Select tower | `D` | Sell tower (50% refund) |
| `Space` | Start wave | `ESC` | Pause |

### ⚡ Quick Actions

| Key | Feature | Key | Feature |
|-----|---------|-----|---------|
| `I` | Tower Dictionary | `J` | Monster Dictionary |
| `K` | Daily Check-in | `M` | Toggle Sound |
| `T` | Statistics | `H` | Toggle HP Display |
| `P` / `F12` | Screenshot | - | - |

### Shortcuts
- **I**: Tower Dictionary
- **J**: Monster Dictionary  
- **K**: Daily Check-in
- **M**: Toggle Sound
- **T**: Statistics
- **H**: Toggle HP Display
- **P**: Screenshot
- **F12**: Screenshot

## 🎯 Features

- 10+ Levels with different themes
- **4 Tower Types**:
  - ⚔️ 箭塔 (Arrow) - Fast attack
  - 💣 炮塔 (Cannon) - High AOE damage
  - ✨ 魔法塔 (Magic) - Life steal
  - ❄️ 冰霜塔 (Frost) - Slow + freeze wave
- **Tower Specialization System** (满级3选1):
  - 箭塔: 穿透射击/狙击大师/急速射击
  - 炮塔: 毁灭轰炸/远程轰炸/速射炮
  - 魔法塔: 奥术爆发/精神控制/能量倾泻
  - 冰霜塔: 冰封千里/绝对零度/寒冰风暴
- Tower Quality System (Common/Rare/Epic)
- **Tower Selling System** (50% refund, particle effects)
- **Tower Upgrade Aura** (golden glow effect on upgrade)
- **Wave Completion Celebration** (particle explosion effects)
- Random Events (Coin Rain/Double Damage/Global Slow)
- Tower Combo Effects (+10% damage for adjacent same-type towers)
- Achievement System
- Daily Tasks & Check-in Rewards
- Particle Effects & Dynamic Lighting
- Sound System
- Critical Hit System (10% chance, 150% damage)
- Hidden Easter Eggs

## 📋 Requirements

- Python 3.8+
- pygame>=2.5.0

## 📁 Project Structure

```
carrot-fantasy/
├── src/              # Source code
│   ├── main.py       # Main game
│   ├── towers.py     # Tower logic
│   ├── monsters.py   # Monster logic
│   ├── projectiles.py
│   ├── waves.py
│   ├── particle_system.py  # Particle effects
│   └── ...
├── config.json       # Game configuration
├── requirements.txt  # Dependencies
├── tests/            # Unit tests
├── .github/          # CI/CD workflows
└── README.md
```

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/ -v

# Or run in-game tests
python -c "import sys; sys.path.insert(0, 'src'); from main import *; print('Import OK')"
```

## 🐛 Troubleshooting

If you encounter errors:
```bash
# Reinstall dependencies
pip uninstall pygame -y
pip install pygame
```

## 📄 License

MIT License

---

**Enjoy the game!** 🎉