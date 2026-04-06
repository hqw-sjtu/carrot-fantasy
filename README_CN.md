# 🎮 保卫萝卜

> 基于Python & Pygame的塔防游戏

## 🚀 快速开始

```bash
# 1. 克隆或下载项目
git clone https://github.com/hqw-sjtu/carrot-fantasy.git
cd carrot-fantasy

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行游戏
python src/main.py
```

或使用启动器：
```bash
bash start.sh
```

## 🕹️ 操作说明

| 按键 | 功能 |
|------|------|
| 1-4 | 选择塔类型 |
| 鼠标 | 放置/选中塔 |
| U | 升级选中塔 |
| D | 出售选中塔 |
| 空格 | 开始波次 |
| ESC | 暂停 |

### 快捷键
- **I**: 塔图鉴
- **J**: 怪物图鉴
- **K**: 每日签到
- **M**: 开关音效
- **T**: 查看统计
- **H**: 切换血量显示
- **P**: 截图

## 🎯 游戏特色

- 10+关卡，不同主题
- 4种塔类型（箭塔、炮塔、法术、冰霜）
- 塔品质系统（普通/优秀/史诗）
- 随机事件（金币雨/双倍伤害/全屏减速）
- 塔组合效果（相邻同类型+10%伤害）
- 成就系统
- 每日任务和签到奖励
- 粒子特效和动态光影
- 音效系统

## 📋 环境要求

- Python 3.8+
- pygame>=2.5.0

## 📁 项目结构

```
carrot-fantasy/
├── src/              # 源代码
│   ├── main.py       # 主游戏
│   ├── towers.py     # 塔逻辑
│   ├── monsters.py   # 怪物逻辑
│   ├── projectiles.py
│   ├── waves.py
│   └── ...
├── config.json       # 游戏配置
├── requirements.txt  # 依赖
└── README.md
```

## 🐛 常见问题

遇到报错可尝试：
```bash
# 重新安装依赖
pip uninstall pygame -y
pip install pygame
```

## 📄 开源协议

MIT License

---

**祝你游戏愉快！** 🎉