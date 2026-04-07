"""
保卫萝卜 - 粒子系统测试
验证新增的护盾特效功能
"""
import sys
sys.path.insert(0, 'src')

def test_particle_system_import():
    """测试粒子系统导入"""
    from particle_system import Particle, ParticleSystem, ScreenShake
    print("✓ 粒子系统模块导入成功")
    return True

def test_particle_creation():
    """测试粒子创建"""
    p = Particle(100, 100, 10, 10, (255, 0, 0), 1.0, 5)
    assert p.x == 100
    assert p.y == 100
    assert p.color == (255, 0, 0)
    print("✓ 粒子创建测试通过")
    return True

def test_particle_update():
    """测试粒子更新"""
    p = Particle(100, 100, 10, 10, (255, 0, 0), 1.0, 5)
    alive = p.update(0.1)
    assert alive == True
    assert p.lifetime < 1.0
    print("✓ 粒子更新测试通过")
    return True

def test_particle_system():
    """测试粒子系统"""
    ps = ParticleSystem()
    assert len(ps.particles) == 0
    
    # 测试护盾特效（新增功能）
    ps.emit_shield(200, 200)
    assert len(ps.particles) > 0
    
    # 更新
    ps.update(0.1)
    print(f"✓ 粒子系统测试通过，护盾特效触发{len(ps.particles)}个粒子")
    return True

def test_freeze_effect():
    """测试冰冻特效"""
    ps = ParticleSystem()
    ps.emit_freeze(150, 150)
    initial_count = len(ps.particles)
    assert initial_count > 0
    
    # 更新几次
    for _ in range(5):
        ps.update(0.1)
    
    print(f"✓ 冰冻特效测试通过，粒子数从{initial_count}减少到{len(ps.particles)}")
    return True

def test_screen_shake():
    """测试屏幕震动"""
    ss = ScreenShake()
    ss.trigger(intensity=15, duration=0.5)
    assert ss.intensity == 15
    assert ss.duration == 0.5
    
    ss.update(0.1)
    assert ss.current_time > 0
    
    print("✓ 屏幕震动测试通过")
    return True

def run_all_tests():
    """运行所有测试"""
    print("\n=== 粒子系统测试 ===")
    
    tests = [
        test_particle_system_import,
        test_particle_creation,
        test_particle_update,
        test_particle_system,
        test_freeze_effect,
        test_screen_shake,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 失败: {e}")
    
    print(f"\n=== 测试结果: {passed}/{len(tests)} 通过 ===")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)