#!/usr/bin/env python3
"""
保卫萝卜 - 快速语法检查
不需要pytest，直接运行基本功能验证
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_tests():
    """运行所有测试"""
    print("=" * 50)
    print("保卫萝卜 - 快速检查")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    # 1. 测试塔工厂
    try:
        from towers import TowerFactory
        t = TowerFactory.create("箭塔")
        assert t.name == "箭塔"
        assert t.damage > 0
        print("✓ 塔工厂创建正常")
        passed += 1
    except Exception as e:
        print(f"✗ 塔工厂测试失败: {e}")
        failed += 1
    
    # 2. 测试塔升级
    try:
        from towers import TowerFactory
        t = TowerFactory.create("箭塔")
        old_damage = t.damage
        t.upgrade()
        assert t.damage > old_damage
        assert t.level == 2
        print("✓ 塔升级系统正常")
        passed += 1
    except Exception as e:
        print(f"✗ 塔升级测试失败: {e}")
        failed += 1
    
    # 3. 测试怪物系统
    try:
        from monsters import Monster
        m = Monster("普通怪物", 100, 1.0, 10)
        assert m.health == 100
        m.take_damage(50)
        assert m.health == 50
        print("✓ 怪物系统正常")
        passed += 1
    except Exception as e:
        print(f"✗ 怪物系统测试失败: {e}")
        failed += 1
    
    # 4. 测试减速效果
    try:
        from monsters import Monster
        m = Monster("快速怪物", 100, 2.0, 10)
        original_speed = m.speed
        m.apply_slow(0.5, 5.0)
        assert m.speed < original_speed
        print("✓ 减速系统正常")
        passed += 1
    except Exception as e:
        print(f"✗ 减速系统测试失败: {e}")
        failed += 1
    
    # 5. 测试粒子系统
    try:
        from particle_system import ParticleSystem
        ps = ParticleSystem()
        ps.emit_death(100, 100, False)
        assert len(ps.particles) > 0
        print("✓ 粒子系统正常")
        passed += 1
    except Exception as e:
        print(f"✗ 粒子系统测试失败: {e}")
        failed += 1
    
    # 6. 测试配置加载
    try:
        from config_loader import get_config
        config = get_config()
        assert 'towers' in config
        print("✓ 配置加载正常")
        passed += 1
    except Exception as e:
        print(f"✗ 配置加载测试失败: {e}")
        failed += 1
    
    # 总结
    print("=" * 50)
    print(f"通过: {passed}, 失败: {failed}")
    if failed == 0:
        print("✓ 所有检查通过!")
    else:
        print("✗ 存在失败项")
    print("=" * 50)
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)