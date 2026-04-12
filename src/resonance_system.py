"""
保卫萝卜 - 防御塔共鸣系统
Carrot Fantasy - Tower Resonance System

当多个同类型塔在共鸣范围内时，触发视觉特效和额外伤害加成
"""

import pygame
import math
import random

class ResonanceEffect:
    """共鸣特效"""
    def __init__(self, x, y, tower_type, intensity=1.0):
        self.x = x
        self.y = y
        self.tower_type = tower_type
        self.intensity = intensity
        self.lifetime = 0
        self.max_lifetime = 60  # 1秒(60帧)
        self.particles = []
        
        # 初始化共鸣粒子
        for _ in range(int(12 * intensity)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3) * intensity
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(20, 40),
                'max_life': 40,
                'size': random.randint(2, 5),
                'color': self._get_particle_color(tower_type)
            })
    
    def _get_particle_color(self, tower_type):
        """获取共鸣粒子颜色"""
        colors = {
            '箭塔': (255, 200, 100),    # 金色
            '炮塔': (255, 100, 50),     # 橙红
            '魔法塔': (147, 112, 219),  # 紫色
            '冰霜塔': (100, 200, 255),  # 浅蓝
            '火塔': (255, 80, 30),      # 火焰色
        }
        return colors.get(tower_type, (200, 200, 200))
    
    def update(self):
        """更新特效"""
        self.lifetime += 1
        
        # 更新粒子
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['vy'] += 0.05  # 轻微重力
        
        # 移除死亡粒子
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        return self.lifetime < self.max_lifetime
    
    def draw(self, surface):
        """绘制特效"""
        # 绘制共鸣环
        progress = self.lifetime / self.max_lifetime
        radius = 30 + progress * 40 * self.intensity
        alpha = int(255 * (1 - progress) * 0.5)
        
        # 绘制多层共鸣环
        for i in range(3):
            ring_radius = radius - i * 10
            if ring_radius > 0:
                color = self._get_particle_color(self.tower_type)
                color_with_alpha = (*color, alpha // (i + 1))
                
                # 创建临时表面实现透明度
                temp_surf = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(temp_surf, color_with_alpha, 
                                 (ring_radius + 5, ring_radius + 5), ring_radius, 2)
                surface.blit(temp_surf, (self.x - ring_radius - 5, self.y - ring_radius - 5))
        
        # 绘制粒子
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            size = int(p['size'] * (p['life'] / p['max_life']))
            color = (*p['color'], alpha)
            
            temp_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, color, (size, size), size)
            surface.blit(temp_surf, (p['x'] - size, p['y'] - size))


class ResonanceManager:
    """共鸣管理器"""
    
    # 共鸣配置
    RESONANCE_CONFIG = {
        'min_towers': 1,      # 最少邻近塔数量触发共鸣(1表示2座塔互相共鸣)
        'resonance_radius': 150,  # 共鸣范围(像素)
        'damage_bonus_per_tower': 0.05,  # 每座塔5%额外伤害
        'max_bonus': 0.25,    # 最多25%额外伤害
        'effect_interval': 120,  # 特效触发间隔(帧)
    }
    
    def __init__(self):
        self.effects = []  # 活跃的共鸣特效
        self.tower_resonance_count = {}  # {tower_id: 共鸣塔数量}
        self.last_effect_time = {}  # {tower_id: 上次特效时间}
        self.resonance_active = set()  # 正在共鸣的塔ID集合
        
    def update(self, towers, current_time):
        """更新共鸣系统
        
        Args:
            towers: 防御塔列表
            current_time: 当前帧数
        """
        # 清除过期特效
        self.effects = [e for e in self.effects if e.update()]
        
        if len(towers) < 2:
            self.tower_resonance_count.clear()
            self.resonance_active.clear()
            return
        
        # 计算每座塔的共鸣
        tower_list = list(towers) if isinstance(towers, (list, tuple)) else list(towers.values())
        
        for tower in tower_list:
            tower_id = id(tower)
            nearby_towers = self._find_resonance_towers(tower, tower_list)
            count = len(nearby_towers)
            
            self.tower_resonance_count[tower_id] = count
            
            # 触发共鸣特效
            min_towers = self.RESONANCE_CONFIG['min_towers']
            if count >= min_towers:
                self.resonance_active.add(tower_id)
                
                # 检查是否触发新特效
                last_time = self.last_effect_time.get(tower_id, 0)
                interval = self.RESONANCE_CONFIG['effect_interval']
                
                if current_time - last_time > interval:
                    intensity = min(count / 5, 1.0)
                    effect = ResonanceEffect(tower.x, tower.y, tower.name, intensity)
                    self.effects.append(effect)
                    self.last_effect_time[tower_id] = current_time
            else:
                self.resonance_active.discard(tower_id)
    
    def _find_resonance_towers(self, tower, tower_list):
        """查找在共鸣范围内的同类型塔"""
        radius = self.RESONANCE_CONFIG['resonance_radius']
        nearby = []
        
        for other in tower_list:
            if other is tower:
                continue
            if other.name != tower.name:  # 必须是同类型
                continue
                
            dist = math.hypot(other.x - tower.x, other.y - tower.y)
            if dist <= radius:
                nearby.append(other)
        
        return nearby
    
    def get_damage_bonus(self, tower):
        """获取塔的伤害加成
        
        Args:
            tower: 防御塔对象
            
        Returns:
            float: 伤害加成比例
        """
        tower_id = id(tower)
        count = self.tower_resonance_count.get(tower_id, 0)
        
        if count < self.RESONANCE_CONFIG['min_towers']:
            return 0.0
        
        bonus_per_tower = self.RESONANCE_CONFIG['damage_bonus_per_tower']
        max_bonus = self.RESONANCE_CONFIG['max_bonus']
        
        return min(count * bonus_per_tower, max_bonus)
    
    def is_resonance_active(self, tower):
        """检查塔是否处于共鸣状态"""
        return id(tower) in self.resonance_active
    
    def draw(self, surface):
        """绘制所有共鸣特效"""
        for effect in self.effects:
            effect.draw(surface)
    
    def get_resonance_count(self, tower):
        """获取塔的共鸣塔数量"""
        return self.tower_resonance_count.get(id(tower), 0)


# 全局共鸣管理器实例
_resonance_manager = None

def get_resonance_manager():
    """获取全局共鸣管理器"""
    global _resonance_manager
    if _resonance_manager is None:
        _resonance_manager = ResonanceManager()
    return _resonance_manager


def set_resonance_manager(manager):
    """设置全局共鸣管理器(用于测试)"""
    global _resonance_manager
    _resonance_manager = manager