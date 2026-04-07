"""
保卫萝卜 - 怪物系统测试
"""
import sys
sys.path.insert(0, '../src')

def test_monster_creation():
    """测试怪物创建"""
    from monsters import MonsterFactory, Monster
    
    m = MonsterFactory.create("小怪物")
    assert m is not None
    assert m.name == "小怪物"
    assert m.health == 50
    assert m.max_health == 50
    assert m.speed > 0
    assert m.alive == True
    print("✓ test_monster_creation passed")

def test_monster_damage():
    """测试怪物受伤"""
    from monsters import Monster
    
    m = Monster("测试怪", 100, 0.01, 10)
    assert m.health == 100
    
    killed = m.take_damage(50)
    assert m.health == 50
    assert killed == False
    
    killed = m.take_damage(60)
    assert m.health == -10
    assert killed == True
    assert m.alive == False
    print("✓ test_monster_damage passed")

def test_monster_health_bar():
    """测试血条计算"""
    from monsters import Monster
    
    m = Monster("测试怪", 100, 0.01, 10)
    
    assert m.get_health_ratio() == 1.0
    
    m.take_damage(25)
    assert m.get_health_ratio() == 0.75
    
    m.take_damage(50)
    assert m.get_health_ratio() == 0.25
    
    m.take_damage(30)
    assert m.get_health_ratio() == 0.0
    print("✓ test_monster_health_bar passed")

def test_monster_factory():
    """测试怪物工厂"""
    from monsters import MonsterFactory
    
    monsters = MonsterFactory.list_monsters()
    assert "小怪物" in monsters
    assert "Boss" in monsters
    
    # 测试所有怪物类型都能创建
    for name in monsters:
        m = MonsterFactory.create(name)
        assert m is not None
        assert m.reward > 0
    print("✓ test_monster_factory passed")

def test_monster_slow():
    """测试减速效果"""
    from monsters import Monster
    
    m = Monster("测试怪", 100, 0.01, 10)
    original_speed = m.speed
    
    m.apply_slow(0.5, 1.0)
    assert m.speed == original_speed * 0.5
    assert m.slow_factor == 0.5
    
    # 测试更强减速被忽略
    m.apply_slow(0.8, 2.0)  # 0.8比0.5弱，不应生效
    assert m.slow_factor == 0.5
    print("✓ test_monster_slow passed")

def run_all_tests():
    """运行所有测试"""
    print("Running monster tests...")
    test_monster_creation()
    test_monster_damage()
    test_monster_health_bar()
    test_monster_factory()
    test_monster_slow()
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    run_all_tests()