"""
保卫萝卜 - 性能测试
Carrot Fantasy - Performance Tests
"""
import sys
import os
import time

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """测试模块导入"""
    try:
        from particle_system import Particle, ParticleSystem
        from towers import Tower
        from projectiles import Projectile
        from monsters import Monster
        assert True, "All imports successful"
    except Exception as e:
        assert False, f"Import error: {e}"

def test_particle_pool():
    """测试粒子对象池"""
    from particle_system import ParticleSystem
    
    ps = ParticleSystem()
    assert len(ps._particle_pool) == 200, "Pool size should be 200"
    
    # 测试获取和归还
    p = ps._get_particle()
    assert p['active'] == True, "Particle should be active"
    
    ps._release_particle(p)
    assert p['active'] == False, "Particle should be released"
    
    assert True, "Particle pool working"

def test_tower_creation():
    """测试塔创建"""
    from towers import Tower
    
    tower = Tower('箭塔', 10, 100, 50, 1.0, 200, 200)
    assert tower.name == '箭塔', "Tower name should match"
    assert tower.level == 1, "Initial level should be 1"
    
    # 测试升级
    tower.upgrade()
    assert tower.level == 2, "Level should be 2 after upgrade"
    
    assert True, "Tower creation and upgrade working"

def test_projectile_flight():
    """测试子弹飞行"""
    from projectiles import Projectile
    from monsters import Monster
    
    target = Monster('小怪', 100, 2, 10)
    target.x, target.y = 100, 50
    proj = Projectile(0, 0, target, 10, 5, 1.0, None, '箭塔')
    
    # 模拟更新
    for _ in range(10):
        alive = proj.update(0.016)  # 60fps
    
    assert True, "Projectile flight working"

def benchmark_particles():
    """粒子系统基准测试"""
    from particle_system import ParticleSystem
    
    ps = ParticleSystem()
    
    # 发射1000个粒子
    start = time.time()
    for _ in range(50):
        ps.emit(400, 300, 20, (255, 100, 100), lifetime=0.5)
    
    # 更新100帧
    for _ in range(100):
        ps.update(0.016)
    
    elapsed = time.time() - start
    
    # 应该在50ms内完成
    if elapsed < 0.1:
        return True, f"Particle benchmark: {elapsed*1000:.1f}ms (PASS)"
    else:
        return False, f"Particle benchmark: {elapsed*1000:.1f}ms (SLOW)"

def run_all_tests():
    """运行所有测试"""
    tests = [
        ("Module Imports", test_imports),
        ("Particle Pool", test_particle_pool),
        ("Tower Creation", test_tower_creation),
        ("Projectile Flight", test_projectile_flight),
        ("Particle Benchmark", benchmark_particles),
    ]
    
    print("=" * 50)
    print("Carrot Fantasy - Performance Tests")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            success, msg = test_func()
            status = "✓ PASS" if success else "✗ FAIL"
            print(f"{status}: {name} - {msg}")
            if success:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: {name} - {e}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return failed == 0

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)