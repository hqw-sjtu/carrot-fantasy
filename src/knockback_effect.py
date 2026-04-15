"""
击退效果系统 - Knockback Effect System
怪物受击时产生击退效果，增加战斗打击感
"""
import pygame
import math
from typing import List, Tuple, Optional


class KnockbackEffect:
    """单个击退效果"""
    
    def __init__(self, target, direction: Tuple[float, float], distance: float, duration: float = 0.15):
        self.target = target
        self.direction = direction  # 归一化方向向量
        self.distance = distance    # 击退距离
        self.duration = duration    # 持续时间(秒)
        self.elapsed = 0.0
        self.start_x = target.x
        self.start_y = target.y
        
    def update(self, dt: float) -> bool:
        """更新击退效果,返回是否结束"""
        self.elapsed += dt
        progress = min(self.elapsed / self.duration, 1.0)
        # 使用缓动函数使击退更自然
        eased = 1 - (1 - progress) ** 2
        
        offset_x = self.direction[0] * self.distance * eased
        offset_y = self.direction[1] * self.distance * eased
        
        self.target.x = self.start_x + offset_x
        self.target.y = self.start_y + offset_y
        
        return self.elapsed >= self.duration


class KnockbackManager:
    """击退效果管理器"""
    
    def __init__(self):
        self.effects: List[KnockbackEffect] = []
        
    def add_knockback(self, target, direction: Tuple[float, float], distance: float, duration: float = 0.15):
        """添加击退效果"""
        # 归一化方向
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        if length > 0:
            direction = (direction[0]/length, direction[1]/length)
        
        effect = KnockbackEffect(target, direction, distance, duration)
        self.effects.append(effect)
        
    def update(self, dt: float):
        """更新所有击退效果"""
        self.effects = [e for e in self.effects if not e.update(dt)]
        
    def clear(self):
        """清除所有击退效果"""
        self.effects.clear()


# 全局实例
_knockback_manager = None

def get_knockback_manager() -> KnockbackManager:
    """获取全局击退管理器"""
    global _knockback_manager
    if _knockback_manager is None:
        _knockback_manager = KnockbackManager()
    return _knockback_manager


# 便捷函数
def apply_knockback(target, attacker_pos: Tuple[float, float], power: float = 20.0):
    """对目标应用击退效果(从攻击者位置推开)"""
    dx = target.x - attacker_pos[0]
    dy = target.y - attacker_pos[1]
    get_knockback_manager().add_knockback(target, (dx, dy), power)


def update_knockback(dt: float):
    """更新击退系统"""
    get_knockback_manager().update(dt)


def clear_knockback():
    """清除所有击退效果"""
    get_knockback_manager().clear()