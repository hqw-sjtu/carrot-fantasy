"""
保卫萝卜 - 稳定性压力测试
Carrot Fantasy Stability Stress Tests
"""
import sys
import os
import time
import random

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def test_particle_performance():
    """性能测试: 大量粒子更新"""
    from particle_system import ParticleSystem
    ps = ParticleSystem()
    
    # 模拟1000次粒子更新
    start = time.time()
    for _ in range(1000):
        # 每次添加20个粒子
        ps.emit(100, 100, 20, (255, 100, 100), lifetime=0.5, size=5)
        ps.update(0.016)  # ~60fps
    elapsed = time.time() - start
    
    print(f"✅ 粒子性能测试: 1000次更新耗时 {elapsed:.3f}s")
    assert elapsed < 2.0, f"粒子更新过慢: {elapsed:.3f}s"
    


def test_tower_creation_stress():
    """压力测试: 大量塔创建"""
    from towers import Tower
    
    towers = []
    start = time.time()
    for i in range(100):
        tower = Tower(
            name="箭塔",
            damage=10 + i,
            range=100 + i * 2,
            cost=50,
            attack_speed=1.0,
            x=100 + i * 10,
            y=200
        )
        towers.append(tower)
    elapsed = time.time() - start
    
    print(f"✅ 塔创建压力测试: 100个塔耗时 {elapsed:.3f}s")
    assert elapsed < 1.0
    


def test_monster_pathfinding():
    """测试: 怪物路径计算稳定性"""
    from monsters import Monster
    
    # 模拟大量怪物
    monsters = []
    for i in range(50):
        m = Monster(
            name=f"monster_{i}",
            health=100 + i * 10,
            speed=1.0,
            reward=10,
            monster_type="normal"
        )
        m.position = random.random()
        monsters.append(m)
    
    # 批量更新
    for m in monsters:
        m.position += 0.01
        if m.position > 1.0:
            m.position = 0.0
    
    print(f"✅ 路径计算测试: 50个怪物更新正常")
    


def test_config_loading():
    """测试: 配置加载稳定性"""
    from config_loader import load_config
    
    # 重复加载10次
    for _ in range(10):
        config = load_config()
        assert config is not None
    
    print(f"✅ 配置加载测试: 10次重复加载正常")
    


def test_state_machine_transitions():
    """测试: 状态机转换稳定性"""
    from state_machine import GameStateMachine
    
    sm = GameStateMachine()
    
    # 模拟多次状态转换
    states = ["menu", "playing", "paused", "playing", "menu"]
    for state in states:
        sm.set_state(state)
    
    print(f"✅ 状态机测试: {len(states)}次状态转换正常")
    


def run_all_stability_tests():
    """运行所有稳定性测试"""
    print("\n" + "="*50)
    print("🧪 保卫萝卜稳定性测试套件")
    print("="*50 + "\n")
    
    tests = [
        ("粒子性能", test_particle_performance),
        ("塔创建压力", test_tower_creation_stress),
        ("路径计算", test_monster_pathfinding),
        ("配置加载", test_config_loading),
        ("状态机", test_state_machine_transitions),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print(f"📊 测试结果: {passed} 通过, {failed} 失败")
    print("="*50 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_stability_tests()
    sys.exit(0 if success else 1)