# 🏰 保卫萝卜 (Carrot Fantasy)

> 基于 Python + Pygame 的塔防游戏 | 工艺品级别品质

[![CI](https://github.com/hqw-sjtu/carrot-fantasy/actions/workflows/ci.yml/badge.svg)](https://github.com/hqw-sjtu/carrot-fantasy/actions)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)

## ✨ 特色功能

### 🎯 核心玩法
- **6种防御塔**: 箭塔、炮塔、魔法塔、减速塔等
- **15+波次挑战**: 多种难度级别
- **升级系统**: 最高3级，支持技能树
- **合成系统**: 同类塔合成高阶塔

### 🎨 特效系统
- **粒子系统**: 攻击、爆炸、升级光晕
- **伤害数字**: 暴击、连击显示
- **塔基特效**: 攻击时发光环、粒子环
- **屏幕震动**: 强力攻击时震动

### 📊 任务与成就
- 每日任务系统
- 成就徽章系统
- 统计追踪

## 🕹️ 安装与运行

```bash
# 克隆项目
git clone https://github.com/hqw-sjtu/carrot-fantasy.git
cd carrot-fantasy

# 安装依赖
pip install pygame pytest

# 运行游戏
python src/main.py

# 运行测试
pytest tests/
```

## 🎮 操作说明

| 操作 | 功能 |
|------|------|
| 鼠标点击 | 放置/升级防御塔 |
| 数字键1-4 | 快速选择塔类型 |
| Tab | 查看波次预览 |
| Space | 暂停/继续 |
| Esc | 退出 |

## 📁 项目结构

```
carrot-fantasy/
├── src/           # 源代码
│   ├── main.py           # 主游戏逻辑
│   ├── towers.py         # 防御塔系统
│   ├── monsters.py       # 怪物系统
│   ├── projectiles.py    # 子弹系统
│   ├── particle_system.py # 粒子系统
│   ├── base_effects.py   # 塔基特效系统 ⭐
│   └── ...
├── tests/         # 测试代码
├── config.json    # 游戏配置
└── docs/          # GitHub Pages
```

## 🧪 测试覆盖

```bash
# 运行所有测试
pytest tests/ -v

# 查看覆盖率
pytest tests/ --cov=src --cov-report=term-missing
```

## 🔄 更新日志

### 2026-04-10
- 新增**塔基特效系统** - 攻击时发光环/粒子环
- 优化代码架构，提升性能

### 2026-04-07
- 完成结构化基准测试
- 完善合成系统

---

*Made with ❤️ by QW*