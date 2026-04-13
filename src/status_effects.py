"""
状态效果系统 | Status Effects System
===============================
为怪物提供各种负面状态效果: 冰冻、减速、中毒、灼烧、眩晕

Author: Carrot Fantasy Team
Version: 1.0.0
"""

import pygame
import random
from typing import Dict, Optional


class StatusEffectType:
    """状态效果类型常量"""
    FROZEN = "frozen"       # 冰冻(完全停止)
    SLOW = "slow"           # 减速
    POISON = "poison"       # 中毒(持续伤害)
    BURN = "burn"           # 灼烧
    STUN = "stun"           # 眩晕
    WEAKEN = "weaken"       # 虚弱(降低防御)


class StatusEffect:
    """单一状态效果"""
    
    def __init__(self, effect_type: str, duration: float, intensity: float = 1.0, 
                 damage_per_second: float = 0, color=None):
        self.effect_type = effect_type
        self.duration = duration      # 持续时间(秒)
        self.max_duration = duration  # 最大持续时间(用于进度条)
        self.intensity = intensity    # 强度(0-1)
        self.damage_per_second = damage_per_second  # DPS
        self.color = color or self._get_default_color(effect_type)
        self.applied = False          # 是否已应用
        self.last_tick = 0            # 上次伤害 tick
    
    def _get_default_color(self, effect_type: str):
        colors = {
            StatusEffectType.FROZEN: (100, 200, 255),   # 浅蓝
            StatusEffectType.SLOW: (150, 150, 150),     # 灰色
            StatusEffectType.POISON: (128, 0, 128),     # 紫色
            StatusEffectType.BURN: (255, 100, 0),       # 橙色
            StatusEffectType.STUN: (255, 255, 0),       # 黄色
            StatusEffectType.WEAKEN: (200, 200, 200),   # 浅灰
        }
        return colors.get(effect_type, (255, 255, 255))
    
    def update(self, dt: float) -> bool:
        """更新状态效果,返回是否仍然有效"""
        self.duration -= dt
        return self.duration > 0
    
    def get_progress(self) -> float:
        """获取剩余进度(0-1)"""
        if self.max_duration <= 0:
            return 0
        return max(0, self.duration / self.max_duration)


class StatusEffectManager:
    """状态效果管理器 - 负责应用和管理所有状态效果"""
    
    # 效果颜色配置
    EFFECT_COLORS = {
        StatusEffectType.FROZEN: (100, 200, 255),
        StatusEffectType.SLOW: (150, 150, 150),
        StatusEffectType.POISON: (128, 0, 128),
        StatusEffectType.BURN: (255, 100, 0),
        StatusEffectType.STUN: (255, 255, 0),
        StatusEffectType.WEAKEN: (200, 200, 200),
    }
    
    def __init__(self):
        self.active_effects: Dict[int, list] = {}  # monster_id -> [StatusEffect]
        self.particle_colors: Dict[str, list] = {}  # 存储每种效果的粒子颜色
    
    def apply_effect(self, monster, effect_type: str, duration: float, 
                    intensity: float = 1.0, damage_per_second: float = 0) -> bool:
        """
        对怪物应用状态效果
        
        Args:
            monster: 怪物对象
            effect_type: 效果类型
            duration: 持续时间(秒)
            intensity: 效果强度
            damage_per_second: 每秒伤害
        
        Returns:
            bool: 是否成功应用
        """
        if not hasattr(monster, 'id'):
            return False
        
        # 初始化怪物的效果列表
        if monster.id not in self.active_effects:
            self.active_effects[monster.id] = []
        
        # 检查是否已有相同效果,如有则延长持续时间
        existing = self._find_effect(monster.id, effect_type)
        if existing:
            existing.duration = max(existing.duration, duration)
            existing.intensity = max(existing.intensity, intensity)
            return True
        
        # 创建新效果
        color = self.EFFECT_COLORS.get(effect_type)
        effect = StatusEffect(effect_type, duration, intensity, damage_per_second, color)
        effect.applied = True
        self.active_effects[monster.id].append(effect)
        
        # 应用立即效果到怪物属性
        self._apply_to_monster(monster, effect)
        
        return True
    
    def _find_effect(self, monster_id: int, effect_type: str) -> Optional[StatusEffect]:
        """查找指定类型的效果"""
        if monster_id not in self.active_effects:
            return None
        for effect in self.active_effects[monster_id]:
            if effect.effect_type == effect_type:
                return effect
        return None
    
    def _apply_to_monster(self, monster, effect: StatusEffect):
        """将效果应用到怪物属性"""
        if effect.effect_type == StatusEffectType.FROZEN:
            if hasattr(monster, 'frozen'):
                monster.frozen = effect.duration * 60  # 转换为帧
        
        elif effect.effect_type == StatusEffectType.SLOW:
            if hasattr(monster, 'apply_slow'):
                monster.apply_slow(1 - effect.intensity * 0.5, effect.duration)
        
        elif effect.effect_type == StatusEffectType.BURN:
            if hasattr(monster, 'burn_timer'):
                monster.burn_timer = effect.duration
        
        elif effect.effect_type == StatusEffectType.POISON:
            if hasattr(monster, 'poison_timer'):
                monster.poison_timer = effect.duration
    
    def update(self, monster, dt: float) -> Dict[str, float]:
        """
        更新所有状态效果,返回各效果的伤害统计
        
        Returns:
            dict: {effect_type: total_damage}
        """
        damage_stats = {}
        
        if not hasattr(monster, 'id') or monster.id not in self.active_effects:
            return damage_stats
        
        effects = self.active_effects[monster.id]
        to_remove = []
        
        for effect in effects:
            # 更新持续时间
            if not effect.update(dt):
                to_remove.append(effect)
                continue
            
            # 处理周期性伤害
            if effect.damage_per_second > 0:
                effect.last_tick += dt
                if effect.last_tick >= 0.5:  # 每0.5秒造成一次伤害
                    damage = effect.damage_per_second * effect.last_tick
                    damage_stats[effect.effect_type] = \
                        damage_stats.get(effect.effect_type, 0) + damage
                    effect.last_tick = 0
                    
                    # 对怪物造成伤害
                    if hasattr(monster, 'take_damage'):
                        monster.take_damage(damage)
        
        # 移除已过期的效果
        for effect in to_remove:
            effects.remove(effect)
            self._remove_from_monster(monster, effect)
        
        return damage_stats
    
    def _remove_from_monster(self, monster, effect: StatusEffect):
        """从怪物移除效果"""
        if effect.effect_type == StatusEffectType.FROZEN:
            if hasattr(monster, 'frozen'):
                monster.frozen = 0
        
        elif effect.effect_type == StatusEffectType.BURN:
            if hasattr(monster, 'burn_timer'):
                monster.burn_timer = 0
        
        elif effect.effect_type == StatusEffectType.POISON:
            if hasattr(monster, 'poison_timer'):
                monster.poison_timer = 0
    
    def get_active_effects(self, monster_id: int) -> list:
        """获取怪物的所有活跃效果"""
        return self.active_effects.get(monster_id, [])
    
    def has_effect(self, monster_id: int, effect_type: str) -> bool:
        """检查怪物是否有指定效果"""
        return self._find_effect(monster_id, effect_type) is not None
    
    def clear_effects(self, monster_id: int):
        """清除怪物的所有效果"""
        if monster_id in self.active_effects:
            del self.active_effects[monster_id]
    
    def draw_effect_indicators(self, screen, monster) -> None:
        """在怪物头顶绘制状态效果指示器"""
        if not hasattr(monster, 'id') or monster.id not in self.active_effects:
            return
        
        effects = self.active_effects[monster.id]
        if not effects:
            return
        
        # 怪物位置
        x = getattr(monster, 'x', 0)
        y = getattr(monster, 'y', 0)
        
        # 在怪物上方绘制效果图标
        icon_size = 16
        spacing = 2
        start_x = x - (len(effects) * (icon_size + spacing)) // 2
        
        for i, effect in enumerate(effects):
            # 绘制效果图标背景
            icon_x = start_x + i * (icon_size + spacing)
            icon_y = y - 30
            
            # 根据效果类型选择颜色
            color = effect.color
            
            # 绘制圆形背景
            pygame.draw.circle(screen, color, (icon_x + icon_size // 2, icon_y + icon_size // 2), 
                             icon_size // 2)
            
            # 绘制进度条
            progress = effect.get_progress()
            if progress > 0:
                bar_width = icon_size
                bar_height = 3
                bar_y = icon_y + icon_size + 1
                # 背景
                pygame.draw.rect(screen, (50, 50, 50), 
                               (icon_x, bar_y, bar_width, bar_height))
                # 进度
                pygame.draw.rect(screen, color, 
                               (icon_x, bar_y, bar_width * progress, bar_height))


class TowerStatusApplier:
    """防御塔状态效果应用器 - 将防御塔与状态系统连接"""
    
    def __init__(self, status_manager: StatusEffectManager):
        self.status_manager = status_manager
        
        # 防御塔效果配置
        self.tower_effects = {
            'ice_tower': {
                StatusEffectType.FROZEN: {'duration': 2.0, 'intensity': 0.8}
            },
            'slow_tower': {
                StatusEffectType.SLOW: {'duration': 3.0, 'intensity': 0.5}
            },
            'poison_tower': {
                StatusEffectType.POISON: {'duration': 5.0, 'intensity': 0.6, 'dps': 10}
            },
            'fire_tower': {
                StatusEffectType.BURN: {'duration': 4.0, 'intensity': 0.7, 'dps': 15}
            },
            'stun_tower': {
                StatusEffectType.STUN: {'duration': 1.5, 'intensity': 1.0}
            },
        }
    
    def apply_tower_effect(self, tower, monster):
        """根据防御塔类型应用相应的状态效果"""
        tower_type = getattr(tower, 'tower_type', None)
        if not tower_type or tower_type not in self.tower_effects:
            return
        
        effects_config = self.tower_effects[tower_type]
        for effect_type, config in effects_config.items():
            self.status_manager.apply_effect(
                monster,
                effect_type,
                duration=config['duration'],
                intensity=config.get('intensity', 1.0),
                damage_per_second=config.get('dps', 0)
            )


# 全局状态效果管理器实例
_global_status_manager = None

def get_status_manager() -> StatusEffectManager:
    """获取全局状态效果管理器"""
    global _global_status_manager
    if _global_status_manager is None:
        _global_status_manager = StatusEffectManager()
    return _global_status_manager