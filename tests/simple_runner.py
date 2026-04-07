#!/usr/bin/env python3
"""
Simple Test Runner - 不依赖pytest的轻量测试运行器
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_tests():
    """运行所有测试"""
    results = []
    
    # Test 1: towers module
    print("=" * 50)
    print("Testing towers.py...")
    try:
        from towers import Tower, ArrowTower, CannonTower, MagicTower, FrostTower
        # 创建测试塔
        arrow = ArrowTower(100, 100)
        assert arrow.damage > 0, "Arrow tower damage should be positive"
        assert arrow.range > 0, "Arrow tower range should be positive"
        print("✅ ArrowTower: PASS")
        results.append(("towers", True))
    except Exception as e:
        print(f"❌ towers: FAIL - {e}")
        results.append(("towers", False))
    
    # Test 2: monsters module
    print("=" * 50)
    print("Testing monsters.py...")
    try:
        from monsters import Monster
        m = Monster(0, 0, 100, 1)
        assert m.health == 100, "Monster health should be 100"
        assert m.alive == True, "New monster should be alive"
        m.take_damage(50)
        assert m.health == 50, "Monster health after damage should be 50"
        m.take_damage(100)
        assert m.alive == False, "Dead monster should not be alive"
        print("✅ Monster: PASS")
        results.append(("monsters", True))
    except Exception as e:
        print(f"❌ monsters: FAIL - {e}")
        results.append(("monsters", False))
    
    # Test 3: projectiles module
    print("=" * 50)
    print("Testing projectiles.py...")
    try:
        from projectiles import Projectile, Arrow, Cannonball, MagicBolt, IceShard
        p = Projectile(0, 0, 10, 5, 0, 0, 10)
        assert p.damage == 10, "Projectile damage should be 10"
        print("✅ Projectile: PASS")
        results.append(("projectiles", True))
    except Exception as e:
        print(f"❌ projectiles: FAIL - {e}")
        results.append(("projectiles", False))
    
    # Test 4: particle system
    print("=" * 50)
    print("Testing particle_system.py...")
    try:
        from particle_system import Particle, ParticleSystem
        ps = ParticleSystem()
        assert ps is not None, "ParticleSystem should be created"
        ps.add_critical_effect(100, 100)
        print("✅ ParticleSystem: PASS")
        results.append(("particles", True))
    except Exception as e:
        print(f"❌ particles: FAIL - {e}")
        results.append(("particles", False))
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    print(f"\nTotal: {passed}/{total} passed")
    
    return passed == total

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)