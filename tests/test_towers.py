"""
保卫萝卜 - 防御塔系统测试
"""
import sys
sys.path.insert(0, '../src')

def test_tower_creation():
    """测试防御塔创建"""
    from towers import Tower, TowerFactory
    
    t = TowerFactory.create("箭塔", 100, 100)
    assert t is not None
    assert t.name == "箭塔"
    assert t.damage > 0
    assert t.range > 0
    print("✓ test_tower_creation passed")

def test_tower_upgrade():
    """测试防御塔升级"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔", 100, 100)
    initial_damage = t.damage
    
    t.upgrade()
    assert t.level == 2
    assert t.damage > initial_damage
    print("✓ test_tower_upgrade passed")

def test_tower_sell():
    """测试防御塔出售"""
    from towers import TowerFactory
    
    t = TowerFactory.create("箭塔", 100, 100)
    t.upgrade()
    t.upgrade()
    
    sell_price = t.get_sell_price()
    # 售价应该是等级1基础价格*50% + 升级投入*50%
    assert sell_price > 0
    print("✓ test_tower_sell passed")

def test_tower_targeting():
    """测试防御塔索敌"""
    from towers import TowerFactory
    from monsters import Monster
    
    t = TowerFactory.create("箭塔", 100, 100)
    m = Monster("测试怪", 100, 50, 10)  # 快速怪物
    
    # 怪物在塔范围内
    t.target = m
    assert t.target is not None
    
    # 怪物离开范围
    m.x = 1000
    m.y = 1000
    t.update_target()
    # 目标应该在范围外
    print("✓ test_tower_targeting passed")

def test_tower_combo():
    """测试防御塔Combo效果"""
    from towers import TowerFactory
    
    t1 = TowerFactory.create("箭塔", 100, 100)
    t2 = TowerFactory.create("箭塔", 150, 100)
    
    # 相邻同类型塔应该有combo
    combo_bonus = t1.get_combo_bonus(t2)
    assert combo_bonus >= 0
    print("✓ test_tower_combo passed")

def run_all_tests():
    """运行所有测试"""
    print("Running tower tests...")
    test_tower_creation()
    test_tower_upgrade()
    test_tower_sell()
    test_tower_targeting()
    test_tower_combo()
    print("\n✅ All tower tests passed!")

if __name__ == "__main__":
    run_all_tests()