"""装备系统测试"""
import sys
sys.path.insert(0, 'src')

from equipment_system import (
    Equipment, EquipmentType, EquipmentRarity,
    generate_random_equipment, TowerEquipment,
    EquipmentDrop, get_equipment_drop
)


def test_equipment_creation():
    """测试装备创建"""
    eq = Equipment(
        name="测试武器",
        equip_type=EquipmentType.WEAPON,
        rarity=EquipmentRarity.RARE,
        damage_boost=10,
        crit_chance=0.1
    )
    assert eq.name == "测试武器"
    assert eq.equip_type == "weapon"
    assert eq.rarity == "rare"
    print(f"✓ 装备创建: {eq}")
    return eq


def test_random_equipment():
    """测试随机装备生成"""
    for _ in range(10):
        eq = generate_random_equipment()
        if eq:
            stats = eq.get_stats()
            print(f"  {eq} -> 伤害+{stats['damage_boost']:.1f}, "
                  f"攻速+{stats['attack_speed_boost']:.1%}, "
                  f"范围+{stats['range_boost']:.1%}, "
                  f"暴击+{stats['crit_chance']:.1%}")
    print("✓ 随机装备生成")


def test_tower_equipment():
    """测试塔装备管理"""
    te = TowerEquipment()
    
    # 装备武器 - 使用字符串
    weapon = generate_random_equipment("weapon")
    result = te.equip(weapon)
    print(f"装备结果: {result}, weapon: {weapon}, type: {weapon.equip_type}")
    assert result == True, f"Failed to equip {weapon.equip_type}"
    print(f"✓ 装备武器: {weapon}")
    
    # 装备饰品
    accessory1 = generate_random_equipment("accessory")
    accessory2 = generate_random_equipment("accessory")
    te.equip(accessory1)
    te.equip(accessory2)
    print(f"✓ 装备饰品 x2")
    
    # 获取总加成
    bonus = te.get_total_bonus()
    print(f"  总属性加成: 伤害+{bonus['damage_boost']:.1f}, "
          f"攻速+{bonus['attack_speed_boost']:.1%}, "
          f"范围+{bonus['range_boost']:.1%}")
    
    # 卸下装备
    unequipped = te.unequip(EquipmentType.WEAPON)
    assert unequipped == weapon
    print("✓ 卸下装备")


def test_equipment_drop():
    """测试装备掉落"""
    drop = get_equipment_drop()
    
    dropped = 0
    for level in [1, 5, 10, 20]:
        for _ in range(100):
            eq = drop.roll_equipment(level)
            if eq:
                dropped += 1
                print(f"  等级{level}掉落: {eq} ({eq.rarity})")
    
    print(f"✓ 装备掉落测试: {dropped}/400 掉落")


def test_rarity_colors():
    """测试稀有度颜色"""
    for rarity in [EquipmentRarity.COMMON, EquipmentRarity.UNCOMMON, 
                   EquipmentRarity.RARE, EquipmentRarity.EPIC,
                   EquipmentRarity.LEGENDARY]:
        eq = Equipment("测试", EquipmentType.WEAPON, rarity, 10)
        color = eq.get_color()
        print(f"  {rarity}: RGB{color}")
    print("✓ 稀有度颜色")


if __name__ == "__main__":
    print("\n=== 装备系统测试 ===\n")
    test_equipment_creation()
    print()
    test_random_equipment()
    print()
    test_tower_equipment()
    print()
    test_equipment_drop()
    print()
    test_rarity_colors()
    print("\n✅ 所有测试通过!")