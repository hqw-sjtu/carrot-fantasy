"""
Attack Rhythm System - 塔攻击节奏系统
为防御塔添加攻击时的节奏光效反馈
"""

import pygame
import math
import random


class AttackRhythm:
    """防御塔攻击节奏效果"""
    
    def __init__(self):
        self.active = False
        self.tower = None
        self.rhythm_interval = 0.5  # 节奏间隔(秒)
        self.elapsed = 0.0
        self.pulse_size = 0
        self.max_pulse_size = 80
        self.rings = []  # 波纹环
        self.color = (255, 215, 0)  # 金色
        self.brightness = 255
        
    def activate(self, tower, interval=None):
        """激活节奏效果"""
        self.active = True
        self.tower = tower
        self.elapsed = 0.0
        self.rings = []
        if interval:
            self.rhythm_interval = interval
            
    def deactivate(self):
        """停止节奏效果"""
        self.active = False
        self.tower = None
        self.rings = []
        
    def update(self, dt):
        """更新节奏效果"""
        if not self.active or not self.tower:
            return
            
        self.elapsed += dt
        
        # 节奏脉冲
        if self.elapsed >= self.rhythm_interval:
            self.elapsed = 0.0
            self._trigger_pulse()
            
        # 更新波纹
        for ring in self.rings[:]:
            ring['age'] += dt
            ring['size'] += ring['speed'] * dt * 60
            ring['alpha'] = max(0, 255 - ring['age'] / ring['lifetime'] * 255)
            if ring['alpha'] <= 0:
                self.rings.remove(ring)
                
        # 亮度脉动
        cycle = (self.elapsed / self.rhythm_interval) * math.pi
        self.brightness = int(180 + 75 * math.sin(cycle))
        
    def _trigger_pulse(self):
        """触发脉冲"""
        if self.tower:
            self.rings.append({
                'x': self.tower.x,
                'y': self.tower.y,
                'size': 20,
                'speed': 60,
                'lifetime': 0.6,
                'age': 0,
                'alpha': 255
            })
            
    def draw(self, surface):
        """绘制节奏效果"""
        if not self.active:
            return
            
        # 绘制波纹
        for ring in self.rings:
            if ring['alpha'] > 0:
                color = tuple(min(255, c * ring['alpha'] // 255) for c in self.color)
                width = max(1, int(4 * ring['alpha'] / 255))
                pygame.draw.circle(
                    surface, color,
                    (int(ring['x']), int(ring['y'])),
                    int(ring['size']),
                    width
                )
                
        # 绘制中心光晕
        if self.tower and self.elapsed < self.rhythm_interval * 0.3:
            pulse_alpha = 1.0 - self.elapsed / (self.rhythm_interval * 0.3)
            center_color = tuple(
                min(255, c + int((255 - c) * pulse_alpha * 0.3))
                for c in self.color
            )
            radius = int(self.tower.range * 0.15 * pulse_alpha)
            if radius > 0:
                s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    s, (*center_color, int(100 * pulse_alpha)),
                    (radius, radius), radius
                )
                surface.blit(s, (self.tower.x - radius, self.tower.y - radius))


class RhythmManager:
    """节奏管理器(单例)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.rhythms = {}  # tower_id -> AttackRhythm
        self.enabled = True
        
    def register_tower(self, tower, interval=None):
        """注册塔到节奏系统"""
        rhythm = AttackRhythm()
        rhythm.activate(tower, interval)
        self.rhythms[id(tower)] = rhythm
        
    def unregister_tower(self, tower):
        """注销塔"""
        if id(tower) in self.rhythms:
            self.rhythms[id(tower)].deactivate()
            del self.rhythms[id(tower)]
            
    def update(self, dt):
        """更新所有节奏效果"""
        if not self.enabled:
            return
        for rhythm in self.rhythms.values():
            rhythm.update(dt)
            
    def draw(self, surface):
        """绘制所有节奏效果"""
        if not self.enabled:
            return
        for rhythm in self.rhythms.values():
            rhythm.draw(surface)
            
    def get_rhythm(self, tower):
        """获取塔的节奏效果"""
        return self.rhythms.get(id(tower))
        
    def clear(self):
        """清除所有节奏"""
        for rhythm in self.rhythms.values():
            rhythm.deactivate()
        self.rhythms.clear()


def get_rhythm_manager():
    """获取节奏管理器单例"""
    return RhythmManager()