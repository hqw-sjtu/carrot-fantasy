# Changelog | 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.2.1] - 2026-04-08

### Fixed | 修复问题
- ✅ 语法检查通过 (main.py + 全部模块)

### Added | 新增功能
- 📊 **稳定性压力测试** (test_stability.py):
  - 粒子性能测试: 1000次更新耗时验证
  - 塔创建压力测试: 100个塔并发创建
  - 路径计算稳定性: 50个怪物批量更新
  - 配置加载稳定性: 10次重复加载
  - 状态机转换: 多次状态切换

### Updated | 更新
- 📝 CHANGELOG更新

---

## [1.2.0] - 2026-04-08

### Fixed | 修复问题
- ✅ 语法检查通过 (main.py + 全部模块)

### Added | 新增功能
- ✨ **萝卜血条显示**: 血量低于70%自动显示萝卜生命值血条，低血量时颜色警示
- ✨ **防御塔专精系统** (Tower Specialization):
  - 满级(3级)防御塔可选专精方向
  - 箭塔: 穿透射击(×2伤害)/狙击大师(+50%范围)/急速射击(×2攻速)
  - 炮塔: 毁灭轰炸(×2伤害)/远程轰炸(+50%范围)/速射炮(+80%攻速)
  - 魔法塔: 奥术爆发(×2伤害+吸血)/精神控制(+50%范围)/能量倾泻(×2攻速)
- 📊 专精系统测试用例通过

### Updated | 更新
- 📝 CHANGELOG更新

---

## [1.1.9] - 2026-04-08

### Fixed | 修复问题
- ✅ 语法检查通过 (main.py + 全部模块)
- ✅ 粒子系统测试通过

### Added | 新增功能
- ✨ **暴击粒子特效** (emit_critical):
  - 暴击伤害时触发金色闪电粒子
  - 25个金色粒子 + 15个白色火花 + 10个红色火花
  - 与projectiles.py暴击系统完美集成
- 📊 粒子系统功能测试通过

### Updated | 更新
- 📝 CHANGELOG更新

---

## [1.1.8] - 2026-04-08

### Fixed | 修复问题
- ✅ 语法检查通过 (main.py + 全部模块)
- ✅ UI面板呼吸效果动画

### Added | 新增功能
- ✨ **UI呼吸效果动画**:
  - 波次开始按钮添加呼吸效果(绿色渐变)
  - 新增 get_breathing_color() 函数
- ✨ **护盾特效** (emit_shield):
  - 护盾塔/技能触发时蓝色光环粒子
  - 20个蓝色光环粒子+8个中心亮点
- 📊 测试覆盖: 粒子系统/UI面板

### Updated | 更新
- 📝 CHANGELOG更新

---

## [1.1.7] - 2026-04-08

### Fixed | 修复问题
- ✅ 语法检查通过 (main.py + 16个模块)
- ✅ 防御塔放置系统完善

### Added | 新增功能
- 🚀 **GitHub Pages自动部署workflow**: deploy.yml
- 📖 Jekyll配置优化: docs/_config.yml
- 📊 完整CI测试覆盖: 语法/导入/单元/性能/稳定性

### Updated | 更新
- 📝 任务计划: 第二批交互完善待完成

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
- 🧪 **状态机测试**: 验证 GameStateMachine 状态转换
- ⚡ **性能基准测试**: 500次粒子更新需<500ms
- 🚀 **GitHub CI增强**:
  - 性能基准测试 (1000次粒子更新)
  - 游戏稳定性测试 (状态机/塔/怪物)

### Updated | 更新
- 📖 GitHub Pages文档: 添加主动技能说明
- 🔧 CI/CD流程: 增加性能和稳定性验证

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