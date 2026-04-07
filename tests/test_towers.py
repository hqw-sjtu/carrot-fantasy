"""
保卫萝卜 - 防御塔系统测试
"""
import sys
import os
# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_tower_factory():
    """测试防御塔工厂"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔")
    assert t is not None
    assert t.name == "箭塔"
    assert t.damage > 0
    assert t.range > 0
    assert t.cost > 0
    assert t.level == 1
    print("✓ test_tower_factory passed")

def test_tower_upgrade():
    """测试防御塔升级"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔")
    initial_damage = t.damage
    initial_range = t.range
    
    result = t.upgrade()
    assert result == 2  # 返回新等级
    assert t.level == 2
    assert t.damage > initial_damage
    assert t.range > initial_range
    print("✓ test_tower_upgrade passed")

def test_tower_max_level():
    """测试满级不能升级"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔")
    t.upgrade()
    t.upgrade()
    
    assert t.level == 3
    assert not t.can_upgrade()
    result = t.upgrade()
    assert result is None  # 满级无法升级
    print("✓ test_tower_max_level passed")

def test_tower_sell_price():
    """测试防御塔出售价格"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔")
    sell_price = t.get_sell_price()
    assert sell_price > 0
    print("✓ test_tower_sell_price passed")

def test_tower_quality():
    """测试防御塔品质系统"""
    from towers import TowerFactory
    
    # 测试多次创建以覆盖不同品质
    qualities = {"normal": 0, "rare": 0, "epic": 0}
    for _ in range(100):
        t = TowerFactory.create("箭塔")
        qualities[t.quality] += 1
    
    # 至少应该有普通品质
    assert qualities["normal"] > 0
    print(f"✓ test_tower_quality passed (normal:{qualities['normal']}, rare:{qualities['rare']}, epic:{qualities['epic']})")

def test_tower_synergy():
    """测试防御塔协同效果"""
    from towers import TowerFactory
    
    t1 = TowerFactory.create("箭塔")
    t1.x, t1.y = 100, 100
    t2 = TowerFactory.create("箭塔")
    t2.x, t2.y = 150, 100  # 相距50像素，在100像素范围内
    
    all_towers = [t1, t2]
    synergy = t1.check_synergy(all_towers)
    assert synergy > 1.0  # 应该有协同加成
    print("✓ test_tower_synergy passed")

def test_tower_priority():
    """测试攻击优先级"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔")
    assert t.priority == "first"  # 默认优先级
    
    t.priority = "weak"
    assert t.priority == "weak"
    
    t.priority = "strong"
    assert t.priority == "strong"
    print("✓ test_tower_priority passed")

def run_all_tests():
    """运行所有测试"""
    print("Running tower tests...")
    test_tower_factory()
    test_tower_upgrade()
    test_tower_max_level()
    test_tower_sell_price()
    test_tower_quality()
    test_tower_synergy()
    test_tower_priority()
    print("\n✅ All tower tests passed!")

if __name__ == "__main__":
    run_all_tests()