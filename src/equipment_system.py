"""
装备系统 | Equipment System
==========================
为防御塔提供装备道具来增强属性

Author: Carrot Fantasy Team
Version: 1.0.0
"""

import pygame
import random
import json
import os
from typing import Dict, Optional, List

# 装备类型
class EquipmentType:
    WEAPON = "weapon"      # 武器 - 伤害加成
    ARMOR = "armor"        # 防具 - 生命/抗性
    ACCESSORY = "accessory" # 饰品 - 攻速/范围
    GEM = "gem"            # 宝石 - 特殊效果

# 装备稀有度
class EquipmentRarity:
    COMMON = "common"          # 普通 - 白色
    UNCOMMON = "uncommon"      # 优秀 - 绿色
    RARE = "rare"              # 稀有 - 蓝色
    EPIC = "epic"              # 史诗 - 紫色
    LEGENDARY = "legendary"    # 传说 - 橙色


class Equipment:
    """装备数据类"""
    
    # 稀有度颜色
    RARITY_COLORS = {
        EquipmentRarity.COMMON: (200, 200, 200),
        EquipmentRarity.UNCOMMON: (100, 200, 100),
        EquipmentRarity.RARE: (100, 150, 255),
        EquipmentRarity.EPIC: (180, 100, 255),
        EquipmentRarity.LEGENDARY: (255, 180, 50),
    }
    
    # 稀有度属性加成倍率
    RARITY_MULTIPLIERS = {
        EquipmentRarity.COMMON: 1.0,
        EquipmentRarity.UNCOMMON: 1.25,
        EquipmentRarity.RARE: 1.5,
        EquipmentRarity.EPIC: 2.0,
        EquipmentRarity.LEGENDARY: 3.0,
    }
    
    def __init__(self, name: str, equip_type: str, rarity: str, 
                 damage_boost: float = 0, attack_speed_boost: float = 0,
                 range_boost: float = 0, crit_chance: float = 0,
                 crit_damage: float = 0, special_effect: str = ""):
        self.name = name
        self.equip_type = equip_type
        self.rarity = rarity
        self.damage_boost = damage_boost
        self.attack_speed_boost = attack_speed_boost
        self.range_boost = range_boost
        self.crit_chance = crit_chance
        self.crit_damage = crit_damage
        self.special_effect = special_effect
    
    def get_color(self):
        return self.RARITY_COLORS.get(self.rarity, (255, 255, 255))
    
    def get_multiplier(self):
        return self.RARITY_MULTIPLIERS.get(self.rarity, 1.0)
    
    def get_stats(self) -> Dict:
        mult = self.get_multiplier()
        return {
            "damage_boost": self.damage_boost * mult,
            "attack_speed_boost": self.attack_speed_boost * mult,
            "range_boost": self.range_boost * mult,
            "crit_chance": self.crit_chance * mult,
            "crit_damage": self.crit_damage * mult,
        }
    
    def __str__(self):
        return f"[{self.rarity}] {self.name}"


# 装备模板
EQUIPMENT_TEMPLATES = {
    EquipmentType.WEAPON: [
        {"name": "锋利剑", "damage": 10, "crit_chance": 0.05},
        {"name": "破甲弓", "damage": 15, "crit_chance": 0.08},
        {"name": "烈焰剑", "damage": 20, "special_effect": "burn"},
        {"name": "冰霜之刃", "damage": 18, "special_effect": "freeze"},
    ],
    EquipmentType.ARMOR: [
        {"name": "铁甲", "damage_boost": -0.1},
        {"name": "锁甲", "range_boost": 0.05},
        {"name": "皮甲", "attack_speed_boost": 0.1},
    ],
    EquipmentType.ACCESSORY: [
        {"name": "敏捷戒指", "attack_speed_boost": 0.15},
        {"name": "力量戒指", "damage_boost": 0.2},
        {"name": "视野戒指", "range_boost": 0.1},
        {"name": "致命戒指", "crit_chance": 0.1, "crit_damage": 0.3},
    ],
    EquipmentType.GEM: [
        {"name": "红宝石", "damage_boost": 0.25},
        {"name": "蓝宝石", "range_boost": 0.15},
        {"name": "黄宝石", "crit_chance": 0.15},
        {"name": "绿宝石", "attack_speed_boost": 0.2},
    ],
}


def generate_random_equipment(equip_type: str = None) -> Equipment:
    """生成随机装备"""
    if equip_type is None:
        equip_type = random.choice(list(EQUIPMENT_TEMPLATES.keys()))
    
    # 确保equip_type是字符串格式
    if hasattr(equip_type, 'value'):
        equip_type = equip_type.value
    
    templates = EQUIPMENT_TEMPLATES.get(equip_type, {})
    if not templates:
        return None
    
    template = random.choice(templates)
    
    # 随机稀有度
    roll = random.random()
    if roll < 0.5:
        rarity = EquipmentRarity.COMMON
    elif roll < 0.8:
        rarity = EquipmentRarity.UNCOMMON
    elif roll < 0.95:
        rarity = EquipmentRarity.RARE
    elif roll < 0.99:
        rarity = EquipmentRarity.EPIC
    else:
        rarity = EquipmentRarity.LEGENDARY
    
    return Equipment(
        name=template["name"],
        equip_type=equip_type,
        rarity=rarity,
        damage_boost=template.get("damage", 0),
        attack_speed_boost=template.get("attack_speed_boost", 0),
        range_boost=template.get("range_boost", 0),
        crit_chance=template.get("crit_chance", 0),
        crit_damage=template.get("crit_damage", 0),
        special_effect=template.get("special_effect", ""),
    )


class TowerEquipment:
    """塔的装备管理器"""
    
    SLOTS = {
        "weapon": 1,      # 武器槽 x1
        "armor": 1,       # 防具槽 x1
        "accessory": 2,   # 饰品槽 x2
        "gem": 3,         # 宝石槽 x3
    }
    
    def __init__(self):
        self.slots: Dict[str, Equipment] = {
            "weapon": None,
            "armor": None,
            "accessory": [None, None],
            "gem": [None, None, None],
        }
    
    def equip(self, equipment: Equipment) -> bool:
        """装备物品，返回是否成功"""
        equip_type = equipment.equip_type
        if equip_type not in self.slots:
            return False
        slots = self.slots[equip_type]  # 直接从字典获取当前值
        
        if isinstance(slots, list):
            # 查找空槽位
            for i, slot in enumerate(slots):
                if slot is None:
                    self.slots[equip_type][i] = equipment
                    return True
            return False
        else:
            # 单槽类型
            if slots is None:
                self.slots[equip_type] = equipment
                return True
            return False
    
    def unequip(self, equip_type: str, slot_index: int = 0) -> Optional[Equipment]:
        """卸下装备"""
        slots = self.slots.get(equip_type)
        if slots is None:
            return None
        
        if isinstance(slots, list):
            if 0 <= slot_index < len(slots):
                equipment = slots[slot_index]
                slots[slot_index] = None
                return equipment
        else:
            equipment = slots
            self.slots[equip_type] = None
            return equipment
        return None
    
    def get_total_bonus(self) -> Dict:
        """获取总属性加成"""
        total = {
            "damage_boost": 0,
            "attack_speed_boost": 0,
            "range_boost": 0,
            "crit_chance": 0,
            "crit_damage": 0,
        }
        
        for slots in self.slots.values():
            if isinstance(slots, list):
                for eq in slots:
                    if eq:
                        stats = eq.get_stats()
                        for k, v in stats.items():
                            total[k] += v
            else:
                if slots:
                    stats = slots.get_stats()
                    for k, v in stats.items():
                        total[k] += v
        
        return total
    
    def has_special_effect(self, effect: str) -> bool:
        """检查是否有特殊效果"""
        for slots in self.slots.values():
            if isinstance(slots, list):
                for eq in slots:
                    if eq and eq.special_effect == effect:
                        return True
            else:
                if slots and slots.special_effect == effect:
                    return True
        return False
    
    def get_equipment_list(self) -> List[Equipment]:
        """获取所有已装备的物品"""
        result = []
        for slots in self.slots.values():
            if isinstance(slots, list):
                result.extend([eq for eq in slots if eq])
            else:
                if slots:
                    result.append(slots)
        return result


class EquipmentDrop:
    """装备掉落管理器"""
    
    def __init__(self):
        self.drop_rates = {
            EquipmentRarity.COMMON: 0.5,
            EquipmentRarity.UNCOMMON: 0.3,
            EquipmentRarity.RARE: 0.15,
            EquipmentRarity.EPIC: 0.04,
            EquipmentRarity.LEGENDARY: 0.01,
        }
    
    def roll_equipment(self, enemy_level: int = 1) -> Optional[Equipment]:
        """根据敌人等级roll装备"""
        # 只有特定波次或Boss才会掉落装备
        if random.random() > 0.1:  # 10%基础掉落率
            return None
        
        # 根据敌人等级提升稀有度概率
        level_bonus = min(enemy_level * 0.02, 0.3)
        
        roll = random.random()
        cumulative = 0
        
        for rarity, base_rate in self.drop_rates.items():
            adjusted_rate = base_rate + level_bonus * base_rate
            cumulative += adjusted_rate
            if roll < cumulative:
                return generate_random_equipment()
        
        return generate_random_equipment()


# 全局装备掉落器
_equipment_drop = None

def get_equipment_drop() -> EquipmentDrop:
    global _equipment_drop
    if _equipment_drop is None:
        _equipment_drop = EquipmentDrop()
    return _equipment_drop