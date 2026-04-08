"""测试Combo Strike集火系统"""
import sys
sys.path.insert(0, 'src')

from towers import Tower
from monsters import Monster


def test_combo_strike_basic():
    """测试集火加成基础功能"""
    # 创建两个塔和一个怪物
    tower1 = Tower("箭塔", damage=100, range=3, cost=50, attack_speed=1.0, x=100, y=200)
    tower2 = Tower("箭塔", damage=100, range=3, cost=50, attack_speed=1.0, x=150, y=200)
    monster = Monster("小怪", health=500, speed=0.01, reward=10)
    
    all_towers = [tower1, tower2]
    
    # 测试：同一目标集火时获得额外加成
    Tower._combo_targets[id(monster)] = 2  # 模拟2塔集火
    
    synergy1 = tower1.check_synergy(all_towers, monster)
    synergy2 = tower2.check_synergy(all_towers, monster)
    
    # 同塔 synergy=1.0 + 0.1(同类型)+ 0.1(集火)=1.2
    assert synergy1 >= 1.15, f"Expected synergy >= 1.15, got {synergy1}"
    print(f"✓ Combo Strike加成正常: {synergy1}")
    
    # 清理
    Tower._combo_targets.clear()
    print("✓ test_combo_strike_basic PASSED")


def test_combo_strike_limit():
    """测试集火加成上限"""
    tower = Tower("箭塔", damage=100, range=3, cost=50, attack_speed=1.0, x=100, y=200)
    monster = Monster("小怪", health=500, speed=0.01, reward=10)
    all_towers = [tower]
    
    # 模拟大量塔集火
    Tower._combo_targets[id(monster)] = 20
    
    synergy = tower.check_synergy(all_towers, monster)
    
    # 最多+50%
    assert synergy <= 1.5, f"Expected synergy <= 1.5, got {synergy}"
    print(f"✓ 集火加成上限正确: {synergy}")
    
    Tower._combo_targets.clear()
    print("✓ test_combo_strike_limit PASSED")


if __name__ == "__main__":
    test_combo_strike_basic()
    test_combo_strike_limit()
    print("\n✅ All Combo Strike tests PASSED!")