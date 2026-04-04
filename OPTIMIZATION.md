# 保卫萝卜项目优化计划 (2026-04-04)

## 目标
- 打造出色的塔防游戏成品
- 分层架构：渲染/逻辑/配置分离

## 已完成 (✅)
- [x] 配置外置 (config.json)
- [x] 游戏状态机 (state_machine.py)
- [x] 鼠标放塔交互 (tower_placement.py)
- [x] 可视化UI面板 (ui_panel.py)
- [x] 代码清理（删除冗余文件）
- [x] 波次生成系统 (waves.py)

## 待完成
- [ ] 防御塔升级系统
- [ ] 技能系统（减速/冰冻/溅射）
- [ ] 更多关卡设计
- [ ] 音效系统
- [ ] 动画效果

## 项目结构
```
carrot-fantasy/
├── config.json          # 配置文件
├── requirements.txt     # 依赖
├── README.md           # 说明
└── src/
    ├── main.py         # 主程序
    ├── config_loader.py # 配置加载
    ├── state_machine.py # 状态机
    ├── tower_placement.py # 放塔交互
    ├── ui_panel.py    # UI面板
    ├── towers.py      # 防御塔
    ├── monsters.py    # 怪物
    ├── projectiles.py # 子弹
    └── waves.py       # 波次
```

## 运行
```bash
python3 -m src.main
```