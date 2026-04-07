# Changelog | 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.6] - 2026-04-08

### Fixed | 修复问题
- ✅ 所有核心模块语法检查通过
- ✅ 快速检查脚本创建完成

### Added | 新增功能
- ✨ **粒子特效扩展**:
  - 装甲破碎特效 (emit_armor_break): 蓝色碎片+白色火花
  - 冰冻特效 (emit_freeze): 冰晶粒子飞散
- 📊 快速检查脚本 (tests/quick_check.py): 无需pytest的基础功能验证

### Updated | 更新
- 🧪 核心模块导入测试: towers/monsters/particle_system/config_loader

---

## [1.1.5] - 2026-04-08

### Fixed | 修复问题
- ✅ 代码语法检查全部通过

### Added | 新增功能
- 🎯 **主动技能系统** (塔按K键释放):
  - 箭塔「专注射击」: 攻速大幅提升
  - 炮塔「轰炸」: 范围AOE伤害
  - 魔法塔「能量汲取」: 吸血效果
- 🧪 新增技能系统测试用例

### Updated | 更新
- 📖 GitHub Pages文档: 添加主动技能说明

---
## [1.1.4] - 2026-04-07

### Fixed | 修复问题
- ✅ 语法检查通过
- ✅ 测试用例路径修复(test_monsters.py)

### Added | 新增功能
- 🧪 完整单元测试套件: towers/monsters/particle_system
- ⚡ 性能优化: 粒子预渲染表面缓存
- 📊 游戏结束报告: 详细统计展示

### Technical | 技术更新
- Python语法验证通过(6个核心模块)
- pytest测试框架集成
- GitHub Actions CI自动化

---

## [1.1.3] - 2026-04-07

### Fixed | 修复问题
- ✅ 语法检查通过

### Added | 新增功能
- ✨ 怪物血条渲染: 实时显示怪物HP百分比(绿/黄/红色)
- 💀 击杀特效: 怪物死亡时触发粒子爆炸(Boss大型特效)
- 🧪 怪物系统单元测试: 覆盖创建/受伤/血条/减速
- ⚡ 粒子系统优化: 对象池减少GC压力

### CI/CD
- 🏗️ GitHub Actions CI: 添加自动测试工作流

---

## [1.1.2] - 2026-04-07

### Fixed | 修复问题
- ✅ 语法检查通过

### Fixed | 修复问题
- ✅ 语法检查通过

### Added | 新增功能
- ✨ 防御塔升级光晕特效: 升级时金色光环扩散
- 🎉 波次完成庆祝动画: 粒子爆炸+上升粒子
- 🧪 粒子系统测试用例: 验证升级光晕功能

---

## [1.1.1] - 2026-04-07

### Fixed | 修复问题
- 🔧 修复出售功能(D键)未正确实现的问题
- ✅ 语法检查通过

### Added | 新增功能
- 🏷️ 塔出售功能: 按D键出售选中的塔，返还50%升级费用
- ✨ 出售粒子特效: 金色/橙色粒子飞散效果
- 📊 出售统计: 更新成就系统(首次出售)

---

## [1.1.0] - 2026-04-07

### Added | 新增功能
- 🧪 Complete test suite (pytest)
- ✨ New particle system module (particle_system.py)
- 📖 Updated README with testing instructions
- 🔧 GitHub Actions CI workflow for automated testing

### Technical | 技术更新
- Python syntax validation for all source files
- Unit tests for core modules (monsters, towers, projectiles, waves)
- Integration tests for config and placement systems

---

## [1.0.0] - 2026-04-07

### Added | 新增功能
- 🎮 Initial release with core tower defense gameplay
- 🗼 4 tower types: Arrow, Cannon, Magic, Ice
- 👾 Multiple monster types with different behaviors
- 🌊 10+ levels with increasing difficulty
- 💎 Tower quality system (Normal/Rare/Epic)
- 🎲 Random events (Gold Rain, Double Damage, Slow All)
- ⚔️ Tower synergy system (+10% damage for adjacent same-type towers)
- 🏆 Achievement system
- 📅 Daily check-in system
- 📊 Statistics panel
- 🎨 Particle effects and dynamic lighting
- 🔊 Sound effects and background music
- ⌨️ Full keyboard and mouse controls
- 🖼️ Screenshot functionality

### Technical | 技术更新
- Python 3.8+ support
- Pygame 2.5+ integration
- Modular code architecture (towers, monsters, waves, UI)
- JSON-based configuration system
- State machine for game flow

---

## [0.9.0] - 2026-04-02

### Added
- Alpha version with basic gameplay
- Core tower placement mechanics
- Basic monster waves

---

## [0.5.0] - 2026-04-01

### Added
- Project initialization
- Basic game framework

---

## Planned Features | 计划功能

### Future | 后续规划
- 🌐 Multi-language support
- 👥 Multiplayer mode
- 🕹️ More tower types
- 📱 Mobile port
- 🎭 More themes and skins
- 🏅 Leaderboards

---

## Version History | 版本历史

- [1.0.0](./releases/tag/v1.0.0) - Initial Release
- [0.9.0](./releases/tag/v0.9.0) - Alpha
- [0.5.0](./releases/tag/v0.5.0) - Prototype

---

<div align="center">

**Thank you for playing!** 🎮

</div>