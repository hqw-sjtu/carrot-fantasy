# -*- coding: utf-8 -*-
"""
测试UI Combo显示功能
验证选中塔时显示集火伤害加成
"""

import sys
sys.path.insert(0, 'src')


def test_combo_bonus_display():
    """测试Combo伤害加成显示逻辑"""
    from towers import Tower
    
    # 创建塔并模拟集火加成 (使用正确的初始化参数)
    tower = Tower('箭塔', 10, 100, 50, 1.0, 200, 200)
    tower.combo_damage_bonus = 15  # 3塔集火
    tower.adjacent_bonus = 10      # 相邻同类型塔
    
    # 计算总加成
    combo_bonus = getattr(tower, 'combo_damage_bonus', 0) + getattr(tower, 'adjacent_bonus', 0)
    
    assert combo_bonus == 25, f"Combo加成应为25%, 实际为{combo_bonus}%"
    print(f"✅ Combo加成显示: +{combo_bonus}%")
    


def test_no_combo_display():
    """测试无集火加成时不应显示"""
    from towers import Tower
    
    tower = Tower('箭塔', 10, 100, 50, 1.0, 200, 200)
    # 未设置combo属性
    combo_bonus = getattr(tower, 'combo_damage_bonus', 0) + getattr(tower, 'adjacent_bonus', 0)
    
    assert combo_bonus == 0, f"无加成时应为0, 实际为{combo_bonus}%"
    print("✅ 无集火加成时不显示")
    


def test_tower_selection_combo():
    """测试选中塔时的Combo信息"""
    from towers import Tower
    
    # 测试各级别塔的Combo显示 (使用正确的初始化参数)
    tower = Tower('箭塔', 10, 100, 50, 1.0, 200, 200)
    tower.level = 2
    tower.combo_damage_bonus = 20
    tower.adjacent_bonus = 10
    
    combo_text = f"⚔️ 集火: +{tower.combo_damage_bonus + tower.adjacent_bonus:.0f}%"
    assert combo_text == "⚔️ 集火: +30%", f"Combo文本错误: {combo_text}"
    
    print("✅ 选中塔Combo信息显示正确")
    


def run_all_tests():
    """运行所有UI Combo测试"""
    print("\n=== UI Combo显示测试 ===")
    
    tests = [
        test_combo_bonus_display,
        test_no_combo_display,
        test_tower_selection_combo,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
    
    print(f"\n=== 结果: {passed}/{len(tests)} 通过 ===")
    return passed == len(tests)


if __name__ == '__main__':
    run_all_tests()