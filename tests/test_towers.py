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

def test_tower_active_skill():
    """测试主动技能系统"""
    from towers import TowerFactory
    from monsters import Monster
    
    # 测试箭塔技能
    t = TowerFactory.create("箭塔")
    skill_status = t.get_skill_status()
    assert skill_status is not None
    assert skill_status["name"] == "专注射击"
    assert skill_status["ready"] == True  # 初始就绪
    
    # 激活技能
    result = t.activate_skill()
    assert result == True
    assert t.skill_active == True
    
    # 再次激活应该失败（冷却中）
    result = t.activate_skill()
    assert result == False
    
    print("✓ test_tower_active_skill passed")

def test_tower_specialization():
    """测试防御塔专精系统"""
    from towers import TowerFactory, TOWER_SPECIALIZATIONS
    
    t = TowerFactory.create("箭塔")
    # 先升到满级
    t.upgrade()
    t.upgrade()
    
    # 测试满级后可专精
    assert t.can_specialize() == True
    assert t.level == 3
    
    # 获取专精选项
    options = t.get_specialization_options()
    assert "damage" in options
    assert "range" in options
    assert "speed" in options
    
    # 应用专精
    result = t.specialize("damage")
    assert result == True
    assert t.specialized == True
    assert t.specialization == "damage"
    
    # 专精后伤害 >= 基础伤害
    assert t.get_effective_damage() >= t.damage
    
    # 专精后不能再专精
    assert t.can_specialize() == False
    print("✓ test_tower_specialization passed")

def test_tower_skill_apply():
    """测试技能效果应用"""
    from towers import TowerFactory
    from monsters import Monster
    
    t = TowerFactory.create("炮塔")
    monsters = [Monster("小怪", 100, 1.0, 10)]
    monsters[0].x, monsters[0].y = 200, 300
    projectiles = []
    
    t.activate_skill()
    t.update_skill(0.1, monsters, projectiles)
    
    # 技能激活状态
    assert t.skill_active == True
    print("✓ test_tower_skill_apply passed")

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
    test_tower_active_skill()
    test_tower_skill_apply()
    test_tower_specialization()
    print("\n✅ All tower tests passed!")

if __name__ == "__main__":
    run_all_tests()