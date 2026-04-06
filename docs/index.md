---
layout: default
title: 保卫萝卜 - Carrot Fantasy
---

# 🦊 保卫萝卜 (Carrot Fantasy)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)

## 游戏简介

一款基于 Python + Pygame 开发的塔防游戏，作为学习项目持续迭代升级。

## 🎮 核心功能

### 基础塔防
- 多种防御塔类型（瓶子炮、风扇塔、星星塔、便便塔）
- 怪物波次系统
- 金币与升级机制

### 增强功能
- ✨ 暴击火花效果（10%暴击率，150%伤害）
- 🎯 快捷键支持（P暂停、F12截图、Ctrl+Shift+R彩蛋）
- 💰 金币动画优化
- 📅 每日挑战与签到系统

### 视觉效果
- 血条渐变美化
- 粒子特效系统
- UI悬停动画
- 发光效果

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/hqw-sjtu/carrot-fantasy.git
cd carrot-fantasy

# 安装依赖
pip install pygame

# 运行游戏
python src/main.py
# 或使用启动器
python launcher.py
```

## 📁 项目结构

```
carrot-fantasy/
├── src/              # 游戏源码
│   ├── main.py       # 主程序
│   ├── towers.py     # 防御塔
│   ├── monsters.py   # 怪物
│   ├── projectiles.py # 子弹
│   └── ...
├── docs/             # GitHub Pages 文档
├── screenshots/      # 游戏截图
└── README.md
```

## 🕹️ 操作说明

| 按键 | 功能 |
|------|------|
| 鼠标左键 | 放置防御塔/选择 |
| P | 暂停/继续 |
| F12 | 截图 |
| Ctrl+Shift+R | 隐藏彩蛋 |

## 📝 更新日志

See [CHANGELOG.md](CHANGELOG.md)

## 🤝 贡献指南

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Made with ❤️ by QW*