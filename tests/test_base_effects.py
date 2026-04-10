"""
塔基特效系统测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_base_effects_import():
    """测试塔基特效模块导入"""
    from base_effects import BaseEffect, GlowRing, ParticleRing, BaseEffectManager, get_base_effect_manager
    assert BaseEffect is not None
    assert GlowRing is not None
    assert ParticleRing is not None
    assert BaseEffectManager is not None
    print("✓ 模块导入测试通过")


def test_glow_ring():
    """测试发光圆环特效"""
    from base_effects import GlowRing
    effect = GlowRing(100, 100, (100, 200, 255), 25)
    assert effect.x == 100
    assert effect.y == 100
    assert effect.active == True
    assert effect.max_life == 90
    print("✓ 发光圆环测试通过")


def test_particle_ring():
    """测试粒子环特效"""
    from base_effects import ParticleRing
    effect = ParticleRing(100, 100, (255, 200, 100), 12)
    assert effect.x == 100
    assert effect.y == 100
    assert len(effect.particles) == 12
    assert effect.active == True
    print("✓ 粒子环测试通过")


def test_base_effect_manager():
    """测试特效管理器"""
    from base_effects import BaseEffectManager, get_base_effect_manager
    manager = BaseEffectManager()
    assert len(manager.effects) == 0
    assert len(manager.tower_base_glows) == 0
    
    # 测试添加特效
    manager.add_glow_ring(100, 100, (100, 200, 255))
    assert len(manager.effects) == 1
    
    manager.add_particle_ring(200, 200)
    assert len(manager.effects) == 2
    
    # 测试塔基发光
    manager.set_tower_base_glow(12345, (255, 200, 100))
    assert 12345 in manager.tower_base_glows
    
    manager.remove_tower_base_glow(12345)
    assert 12345 not in manager.tower_base_glows
    
    print("✓ 特效管理器测试通过")


def test_singleton():
    """测试单例模式"""
    from base_effects import get_base_effect_manager
    m1 = get_base_effect_manager()
    m2 = get_base_effect_manager()
    assert m1 is m2
    print("✓ 单例测试通过")


def test_effect_update():
    """测试特效更新"""
    from base_effects import GlowRing
    effect = GlowRing(100, 100, (100, 200, 255), 25)
    
    # 初始状态
    assert effect.active == True
    
    # 更新到过期
    effect.life = 100
    effect.update(1)
    assert effect.active == False
    
    print("✓ 特效更新测试通过")


if __name__ == "__main__":
    test_base_effects_import()
    test_glow_ring()
    test_particle_ring()
    test_base_effect_manager()
    test_singleton()
    test_effect_update()
    print("\n✅ 所有塔基特效测试通过!")