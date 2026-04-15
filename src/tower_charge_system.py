"""
Tower Charge System - 防御塔充能系统
当防御塔持续攻击时累积充能，满了释放特殊技能
"""

import pygame
import math
from typing import Dict, List, Optional


class ChargeEffect:
    """充能时的视觉特效"""
    
    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        self.decay = 0.03
        self.radius = 0
        self.max_radius = 30
        
    def update(self) -> bool:
        """更新特效，返回是否存活"""
        self.life -= self.decay
        self.radius = self.max_radius * (1 - self.life)
        return self.life > 0
    
    def draw(self, screen: pygame.Surface):
        if self.life <= 0:
            return
        # 充能光环
        alpha = int(100 * self.life)
        surface = pygame.Surface((int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surface, (*self.color, alpha), 
                          (int(self.radius), int(self.radius)), int(self.radius), 2)
        screen.blit(surface, (self.x - self.radius, self.y - self.radius))


class ChargeBurst:
    """充能爆发特效"""
    
    def __init__(self, x: float, y: float, color: tuple):
        self.x = x
        self.y = y
        self.color = color
        self.rings: List[tuple] = []  # (radius, alpha)
        self.max_rings = 3
        self.timer = 0
        self.done = False
        
    def update(self) -> bool:
        """更新爆发特效"""
        self.timer += 1
        if self.timer % 5 == 0 and len(self.rings) < self.max_rings:
            self.rings.append((0, 255))
        
        for i, (r, a) in enumerate(self.rings):
            self.rings[i] = (r + 4, max(0, a - 15))
        
        self.rings = [(r, a) for r, a in self.rings if a > 0]
        return len(self.rings) > 0
    
    def draw(self, screen: pygame.Surface):
        for radius, alpha in self.rings:
            surface = pygame.Surface((int(radius * 2), int(radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, alpha),
                             (int(radius), int(radius)), int(radius), 3)
            screen.blit(surface, (self.x - radius, self.y - radius))


class TowerChargeManager:
    """防御塔充能管理器"""
    
    def __init__(self):
        self.charges: Dict[int, float] = {}  # tower_id -> charge (0-100)
        self.effects: List[ChargeEffect] = []
        self.bursts: List[ChargeBurst] = []
        self.charge_colors = {
            'fire': (255, 100, 50),
            'ice': (100, 200, 255),
            'lightning': (255, 255, 100),
            'poison': (150, 255, 100),
            'default': (255, 215, 0)
        }
        
    def start_charge(self, tower_id: int, tower_type: str = 'default'):
        """开始为防御塔充能"""
        if tower_id not in self.charges:
            self.charges[tower_id] = 0
            
    def add_charge(self, tower_id: float, amount: float):
        """增加充能"""
        if tower_id in self.charges:
            self.charges[tower_id] = min(100, self.charges[tower_id] + amount)
            
    def get_charge(self, tower_id: int) -> float:
        """获取充能值"""
        return self.charges.get(tower_id, 0)
    
    def is_charged(self, tower_id: int) -> bool:
        """检查是否已充满"""
        return self.charges.get(tower_id, 0) >= 100
    
    def trigger_burst(self, tower_id: int, x: float, y: float, tower_type: str = 'default') -> bool:
        """触发充能爆发，返回是否成功触发"""
        if not self.is_charged(tower_id):
            return False
        
        color = self.charge_colors.get(tower_type, self.charge_colors['default'])
        self.bursts.append(ChargeBurst(x, y, color))
        self.charges[tower_id] = 0
        return True
    
    def spawn_charge_effect(self, x: float, y: float, tower_type: str = 'default'):
        """生成充能视觉效果"""
        color = self.charge_colors.get(tower_type, self.charge_colors['default'])
        self.effects.append(ChargeEffect(x, y, color))
        
    def update(self):
        """更新所有特效"""
        self.effects = [e for e in self.effects if e.update()]
        self.bursts = [b for b in self.bursts if b.update()]
        
    def draw(self, screen: pygame.Surface):
        """绘制所有特效"""
        for effect in self.effects:
            effect.draw(screen)
        for burst in self.bursts:
            burst.draw(screen)
            
    def get_charge_color(self, tower_id: int, tower_type: str = 'default') -> tuple:
        """获取充能颜色"""
        charge = self.get_charge(tower_id)
        base_color = self.charge_colors.get(tower_type, self.charge_colors['default'])
        
        # 根据充能值调整亮度
        if charge < 30:
            return base_color
        elif charge < 70:
            # 中等充能，稍微变亮
            return tuple(min(255, c + 50) for c in base_color)
        else:
            # 充满电，发光效果
            return tuple(min(255, c + 100) for c in base_color)
            
    def draw_charge_bar(self, screen: pygame.Surface, x: float, y: float, 
                       tower_id: int, width: int = 40, height: int = 6):
        """绘制充能条"""
        charge = self.get_charge(tower_id)
        if charge <= 0:
            return
            
        # 背景
        bg_rect = pygame.Rect(x - width//2, y - 15, width, height)
        pygame.draw.rect(screen, (50, 50, 50), bg_rect)
        
        # 充能条
        fill_width = int(width * charge / 100)
        if fill_width > 0:
            fill_rect = pygame.Rect(x - width//2, y - 15, fill_width, height)
            color = self.get_charge_color(tower_id)
            pygame.draw.rect(screen, color, fill_rect)
            
        # 边框
        pygame.draw.rect(screen, (100, 100, 100), bg_rect, 1)
        
    def clear(self):
        """清除所有数据"""
        self.charges.clear()
        self.effects.clear()
        self.bursts.clear()


# 全局实例
_charge_manager = None

def get_charge_manager() -> TowerChargeManager:
    """获取全局充能管理器"""
    global _charge_manager
    if _charge_manager is None:
        _charge_manager = TowerChargeManager()
    return _charge_manager