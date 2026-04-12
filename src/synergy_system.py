"""
保卫萝卜 - 防御塔协同系统
Carrot Fantasy - Tower Synergy System

当特定类型的防御塔靠近时产生额外加成效果
"""

import math

# 协同效果定义
SYNERGIES = {
    # 同类型塔协同 - 相同塔靠近时获得攻速/伤害加成
    "same_type": {
        "name": "协同作战",
        "min_distance": 120,  # 像素
        "max_bonus_towers": 3,  # 最多计算附近塔数
        "max_tower_bonus": {
            "attack_speed": 0.08,  # 每座塔+8%攻速
            "damage": 0.05,        # 每座塔+5%伤害
        }
    },
    
    # 元素协同 - 不同元素塔组合
    "elemental": {
        "pairs": [
            ("火塔", "冰霜塔", "frozen_fire", "🔥❄️ 冰火交融", 0.15),  # 15%伤害加成
            ("火塔", "魔法塔", "arcane_fire", "🔥✨ 奥术火焰", 0.12),
            ("箭塔", "魔法塔", "magic_arrow", "🏹✨ 魔法箭矢", 0.10),
            ("炮塔", "冰霜塔", "frost_bomb", "💥❄️ 冰霜炸弹", 0.18),  # AOE增强
            ("箭塔", "冰霜塔", "ice_arrow", "🏹❄️ 冰霜箭矢", 0.12),
        ]
    },
    
    # 射程协同 - 远近配合
    "range_synergy": {
        "short_range_towers": ["炮塔", "火塔"],
        "long_range_towers": ["箭塔", "魔法塔", "冰霜塔"],
        "bonus": 0.10,  # 10%伤害加成
        "min_distance": 100,
    },
}

class SynergyManager:
    """防御塔协同管理器"""
    
    def __init__(self):
        self.active_synergies = {}  # {tower_id: [(synergy_type, bonus_info), ...]}
        self.synergy_cache = {}     # 缓存计算结果
        self.last_update = 0
        self.update_interval = 500  # 500ms更新一次
        
    def calculate_synergies(self, towers, current_time):
        """计算所有塔的协同效果
        
        Args:
            towers: 防御塔列表
            current_time: 当前时间(毫秒)
            
        Returns:
            协同效果字典 {tower_id: {bonus_type: bonus_value}}
        """
        # 限制更新频率
        if current_time - self.last_update < self.update_interval:
            return self.synergy_cache
            
        self.last_update = current_time
        self.synergy_cache.clear()
        
        if len(towers) < 2:
            return self.synergy_cache
            
        # 计算所有塔之间的协同
        tower_list = list(towers) if isinstance(towers, (list, tuple)) else list(towers.values())
        
        for i, tower1 in enumerate(tower_list):
            tower_id = id(tower1)
            bonuses = {}
            
            # 1. 同类型协同
            same_type_bonus = self._calc_same_type_synergy(tower1, tower_list)
            if same_type_bonus:
                bonuses.update(same_type_bonus)
                
            # 2. 元素协同
            elemental_bonus = self._calc_elemental_synergy(tower1, tower_list)
            if elemental_bonus:
                bonuses.update(elemental_bonus)
                
            # 3. 射程协同
            range_bonus = self._calc_range_synergy(tower1, tower_list)
            if range_bonus:
                bonuses.update(range_bonus)
                
            if bonuses:
                self.synergy_cache[tower_id] = bonuses
                
        return self.synergy_cache
        
    def _calc_same_type_synergy(self, tower, all_towers):
        """计算同类型协同效果"""
        synergy_config = SYNERGIES["same_type"]
        min_dist = synergy_config["min_distance"]
        max_bonus = synergy_config["max_tower_bonus"]
        
        nearby_count = 0
        for other in all_towers:
            if other is tower:
                continue
            if other.name == tower.name:  # 同类型
                dist = math.hypot(other.x - tower.x, other.y - tower.y)
                if dist <= min_dist:
                    nearby_count += 1
                    if nearby_count >= synergy_config["max_bonus_towers"]:
                        break
                        
        if nearby_count > 0:
            return {
                "synergy_attack_speed": nearby_count * max_bonus["attack_speed"],
                "synergy_damage": nearby_count * max_bonus["damage"],
            }
        return None
        
    def _calc_elemental_synergy(self, tower, all_towers):
        """计算元素协同效果"""
        if "elemental" not in SYNERGIES:
            return None
            
        synergy_config = SYNERGIES["elemental"]
        
        for tower1_name, tower2_name, synergy_id, synergy_name, bonus in synergy_config["pairs"]:
            if tower.name == tower1_name:
                # 查找配对塔
                for other in all_towers:
                    if other is tower:
                        continue
                    if other.name == tower2_name:
                        dist = math.hypot(other.x - tower.x, other.y - tower.y)
                        if dist <= 150:  # 元素协同距离
                            return {
                                f"synergy_{synergy_id}": bonus,
                                "synergy_name": synergy_name,
                            }
        return None
        
    def _calc_range_synergy(self, tower, all_towers):
        """计算射程协同效果"""
        synergy_config = SYNERGIES["range_synergy"]
        
        is_short = tower.name in synergy_config["short_range_towers"]
        is_long = tower.name in synergy_config["long_range_towers"]
        
        if not (is_short or is_long):
            return None
            
        target_type = "long_range" if is_short else "short_range"
        target_names = (synergy_config["long_range_towers"] if is_short 
                       else synergy_config["short_range_towers"])
        
        for other in all_towers:
            if other is tower:
                continue
            if other.name in target_names:
                dist = math.hypot(other.x - tower.x, other.y - tower.y)
                if dist <= synergy_config["min_distance"]:
                    return {
                        "synergy_range_combo": synergy_config["bonus"],
                        "synergy_name": "🎯 远近配合",
                    }
        return None
        
    def get_synergy_bonus(self, tower, bonus_type="damage"):
        """获取指定塔的协同加成
        
        Args:
            tower: 防御塔对象
            bonus_type: 加成类型 ("damage", "attack_speed")
            
        Returns:
            加成值（乘数）
        """
        tower_id = id(tower)
        if tower_id not in self.synergy_cache:
            return 1.0
            
        bonuses = self.synergy_cache[tower_id]
        
        if bonus_type == "damage":
            # 收集所有伤害加成
            damage_bonus = 1.0
            for key, value in bonuses.items():
                if "damage" in key or "synergy_" in key:
                    if isinstance(value, (int, float)) and value < 1.0:  # 百分比加成
                        damage_bonus += value
            return damage_bonus
            
        elif bonus_type == "attack_speed":
            speed_bonus = 1.0
            for key, value in bonuses.items():
                if "speed" in key:
                    if isinstance(value, (int, float)) and value < 1.0:
                        speed_bonus += value
            return speed_bonus
            
        return 1.0
        
    def get_synergy_description(self, tower):
        """获取协同效果描述"""
        tower_id = id(tower)
        if tower_id not in self.synergy_cache:
            return None
            
        bonuses = self.synergy_cache[tower_id]
        
        # 检查是否有命名协同效果
        if "synergy_name" in bonuses:
            return bonuses["synergy_name"]
            
        # 生成本动描述
        parts = []
        for key, value in bonuses.items():
            if isinstance(value, (int, float)) and value > 0:
                if "speed" in key:
                    parts.append(f"攻速+{int(value*100)}%")
                elif "damage" in key and "synergy_" not in key:
                    parts.append(f"伤害+{int(value*100)}%")
                    
        return " | ".join(parts) if parts else None
        
    def has_active_synergy(self, tower):
        """检查塔是否有激活的协同效果"""
        return id(tower) in self.synergy_cache and bool(self.synergy_cache[id(tower)])


# 全局协同管理器实例
_synergy_manager = None

def get_synergy_manager():
    """获取全局协同管理器"""
    global _synergy_manager
    if _synergy_manager is None:
        _synergy_manager = SynergyManager()
    return _synergy_manager


def apply_synergy_bonuses(tower, base_damage, base_speed):
    """应用协同加成到防御塔属性
    
    Args:
        tower: 防御塔对象
        base_damage: 基础伤害
        base_speed: 基础攻速
        
    Returns:
        (实际伤害, 实际攻速)
    """
    manager = get_synergy_manager()
    
    damage_mult = manager.get_synergy_bonus(tower, "damage")
    speed_mult = manager.get_synergy_bonus(tower, "attack_speed")
    
    return int(base_damage * damage_mult), base_speed * speed_mult