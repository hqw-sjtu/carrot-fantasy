---
layout: default
title: 保卫萝卜 - Carrot Fantasy
---

# 🦊 保卫萝卜 (Carrot Fantasy)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)](https://www.pygame.org/)
[![CI](https://github.com/hqw-sjtu/carrot-fantasy/actions/workflows/ci.yml/badge.svg)](https://github.com/hqw-sjtu/carrot-fantasy/actions)

## 游戏简介

一款基于 Python + Pygame 开发的塔防游戏，**工艺品级别**品质，可上市高标准。作为学习项目持续迭代升级，已实现完整塔防游戏框架。

## 🎮 核心功能

### 防御塔系统 (4种基础塔 + 专精系统)
| 塔类型 | 特点 | 主动技能 |
|--------|------|----------|
| ⚔️ 箭塔 | 高速攻击 | 专注射击 |
| 💣 炮塔 | 范围高伤 | 轰炸 |
| ✨ 魔法塔 | 吸血效果 | 能量汲取 |
| ❄️ 冰霜塔 | 减速控制 | 冰封大地 |

### 塔专精系统 (满级3选1)
- **箭塔**: 穿透射击 / 狙击大师 / 急速射击
- **炮塔**: 毁灭轰炸 / 远程轰炸 / 速射炮
- **魔法塔**: 奥术爆发 / 精神控制 / 能量倾泻
- **冰霜塔**: 冰封千里 / 绝对零度 / 寒冰风暴

### 品质系统
- 普通 (60%) - 基础属性
- 优秀 (30%) - +25%伤害, +10%范围
- 史诗 (10%) - +50%伤害, +20%范围

### 高级系统
- **Combo Strike** - 多塔集火同一目标额外+5%/塔(最高+50%)
- **Screen Shake** - 屏幕震动反馈
- 暴击系统 (10%暴击率, 150%伤害)
- **暴击闪光特效** - 十字闪光反馈
- **连锁闪电特效** - 魔法塔链式攻击
- 粒子特效系统 (15+种特效)
- 塔基发光与粒子环特效
- 每日挑战与签到系统
- 成就系统
- 随机事件 (金币雨/双倍伤害/全局减速)

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
├── src/                     # 游戏源码
│   ├── main.py              # 主程序 (~2500行)
│   ├── towers.py            # 防御塔系统
│   ├── monsters.py          # 怪物系统
│   ├── projectiles.py       # 子弹系统
│   ├── particle_system.py   # 粒子特效
│   ├── wave.py              # 波次系统
│   └── ...
├── config.json              # 游戏配置
├── tests/                   # 单元测试
├── docs/                    # GitHub Pages
├── .github/workflows/       # CI/CD
└── README.md
```

## 🕹️ 操作说明

### 基础控制
| 按键 | 功能 |
|------|------|
| 鼠标左键 | 放置/选择防御塔 |
| 1-4 | 选择塔类型 |
| U | 升级选中塔 |
| D | 出售塔 (50%返还) |
| Space | 开始波次 |
| F9 | 快速保存 |
| F10 | 快速读取 |
| ESC | 暂停 |

### 快捷键
| 按键 | 功能 |
|------|------|
| I | 防御塔图鉴 |
| J | 怪物图鉴 |
| K | 每日签到 |
| M | 开关音效 |
| T | 统计信息 |
| H | 显示/隐藏血条 |
| P / F12 | 截图 |

## 🧪 测试

```bash
# 运行单元测试
python -m pytest tests/ -v

# 语法检查
find src -name "*.py" -exec python -m py_compile {} +

# 导入测试
python -c "import sys; sys.path.insert(0, 'src'); from main import *; print('OK')"
```

## 💫 高级特效系统

### 护盾保护 (ShieldEffect)
- 能量护盾环绕保护防御塔
- 多层旋转能量环
- 粒子环绕动画

### 波纹扩散 (RippleEffect)
- 攻击命中时的水波扩散
- 多重波纹叠加
- 淡出动画效果

---

## 🎯 GitHub Actions CI

项目配置了完整的CI/CD流程:
- ✅ 多Python版本测试 (3.8, 3.10, 3.12)
- ✅ 语法检查
- ✅ 单元测试 + 覆盖率
- ✅ 代码风格检查
- ✅ 构建验证

## 📋 更新日志

See [CHANGELOG.md](CHANGELOG.md) — Current: **v2.0.0**

### 最新特性: 快速存档/读档系统 (v2.0.0)
- **F9 快速保存**: 保存当前游戏进度(金币/生命/波次/防御塔)
- **F10 快速读取**: 读取存档继续游戏
- 存档后播放粒子特效反馈
- 333测试用例覆盖
- **SkillTreeView**: 按 N 键打开技能树面板
  - 4种塔(箭/炮/魔法/冰霜)的技能树独立显示
  - 可视化技能节点+前置依赖连线
  - 悬停显示技能详情
  - Tab 键切换技能树
- 325测试用例覆盖,全部通过

### 上一特性: 鼠标悬停提示系统 (v1.7.2)
- **TooltipSystem**: 鼠标悬停显示详细信息
  - 防御塔: 伤害/射程/攻速/专精/品质
  - 怪物: 生命值/赏金/异常状态
  - 智能位置/美观半透明背景
- 196测试用例全部通过

### 上一特性: 升级光柱 & 塔选中脉冲 (v1.7.1)
- **UpgradeBeamEffect**: 升级时金色(Lv2)/紫色(Lv3)/橙红色(Lv4+)光柱直冲云霄,20粒子环绕
- **TowerSelectionPulse**: 选中塔时呼吸光环,双圈同心圆设计,1.5秒循环
- **StarburstEffect**: 高连击庆祝烟火,12条光线粒子爆发,中心光环+重力
- **TrailFadeEffect**: 消失式路径效果,点对点渐变淡出
- **BlackHoleEffect**: 黑洞吸引特效,30粒子+36段吸积盘,核心脉动
- **BossHealthBarEffect**: Boss血条暴击效果,闪红+震动+暴击数字
- 156测试用例覆盖,全部通过

## 🤝 贡献指南

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

*Made with ❤️ by QW | 上海交通大学*