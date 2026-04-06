# 🎮 保卫萝卜 (Carrot Fantasy)

> A Tower Defense Game built with Python & Pygame

English | [中文](README_CN.md)

## ⭐ Quick Start

```bash
# 1. Clone or download the project
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

## 🕹️ How to Play

| Key | Action |
|-----|--------|
| 1-4 | Select tower type |
| Mouse | Place / select tower |
| U | Upgrade selected tower |
| D | Sell selected tower |
| Space | Start wave |
| ESC | Pause |

### Shortcuts
- **I**: Tower Encyclopedia
- **J**: Monster Book
- **K**: Daily Check-in
- **M**: Toggle sound
- **T**: Statistics
- **H**: Toggle health bars
- **P**: Screenshot

## 🎯 Features

- 10+ Levels with different themes
- 4 Tower types (Arrow, Cannon, Magic, Ice)
- Tower quality system (Normal/Rare/Epic)
- Random events (Gold Rain, Double Damage, Slow All)
- Tower synergy (adjacent same-type +10% damage)
- Achievement system
- Daily quests & check-in rewards
- Particle effects & dynamic lighting
- Sound effects

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
│   └── ...
├── config.json       # Game config
├── requirements.txt  # Dependencies
└── README.md
```

## 🐛 Issues

If you encounter errors, try:
```bash
# Reinstall dependencies
pip uninstall pygame -y
pip install pygame
```

## 📄 License

MIT License

---

**Enjoy the game!** 🎉