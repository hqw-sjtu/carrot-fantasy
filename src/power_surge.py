"""
Power Surge System - 能量爆发系统
工艺品级别: 当玩家激活时,所有防御塔临时获得伤害加成
"""

import pygame
import math
import random
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SurgeParticle:
    """能量粒子"""
    x: float
    y: float
    angle: float
    distance: float
    speed: float
    alpha: int
    size: float


class PowerSurge:
    """能量爆发管理器"""
    
    def __init__(self):
        self.active = False
        self.duration = 5.0  # 持续时间(秒)
        self.damage_boost = 1.5  # 伤害倍率
        self.elapsed = 0.0
        self.particles: List[SurgeParticle] = []
        self.max_particles = 50
        self.center_x = 0
        self.center_y = 0
        self.radius = 0
        self.activated = False  # 是否已激活过
        
    def activate(self, center_x: float, center_y: float, radius: float):
        """激活能量爆发"""
        self.active = True
        self.elapsed = 0.0
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.activated = True
        # 初始化粒子
        self.particles = []
        for i in range(self.max_particles):
            angle = (i / self.max_particles) * math.pi * 2
            self.particles.append(SurgeParticle(
                x=center_x,
                y=center_y,
                angle=angle,
                distance=0,
                speed=50 + random.random() * 30,
                alpha=255,
                size=3 + random.random() * 3
            ))
    
    def update(self, dt: float):
        """更新状态"""
        if not self.active:
            return
            
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.active = False
            self.particles = []
            return
            
        # 更新粒子
        for p in self.particles:
            p.distance += p.speed * dt
            p.angle += dt * 0.5
            if p.distance > self.radius:
                p.distance = 0
            # 透明度随距离衰减
            progress = p.distance / self.radius
            p.alpha = int(255 * (1 - progress * 0.7))
    
    def get_damage_multiplier(self) -> float:
        """获取当前伤害倍率"""
        if not self.active:
            return 1.0
        
        # 结束时淡出
        if self.elapsed > self.duration * 0.8:
            progress = (self.elapsed - self.duration * 0.8) / (self.duration * 0.2)
            return self.damage_boost * (1 - progress)
        
        return self.damage_boost
    
    def render(self, surface: pygame.Surface) -> Optional[bool]:
        """渲染能量爆发效果"""
        if not self.active:
            return None
            
        # 外圈光环
        progress = self.elapsed / self.duration
        base_radius = self.radius * 0.2
        ring_radius = base_radius + (self.radius - base_radius) * progress
        
        # 绘制多个光环
        colors = [
            (255, 200, 50),
            (255, 150, 0),
            (255, 100, 0)
        ]
        
        for i, color in enumerate(colors):
            alpha = int(200 * (1 - i * 0.3))
            offset = i * 20
            pygame.draw.circle(
                surface, 
                (*color, alpha),
                (int(self.center_x), int(self.center_y)),
                int(ring_radius + offset),
                3
            )
        
        # 绘制粒子
        for p in self.particles:
            x = self.center_x + math.cos(p.angle) * p.distance
            y = self.center_y + math.sin(p.angle) * p.distance
            
            # 能量粒子
            color = (255, 220, 100)
            pygame.draw.circle(surface, color, (int(x), int(y)), int(p.size))
            
            # 粒子光晕
            if p.alpha > 100:
                glow_surf = pygame.Surface((int(p.size * 4), int(p.size * 4)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*color, p.alpha // 4), 
                                 (int(p.size * 2), int(p.size * 2)), int(p.size * 2))
                surface.blit(glow_surf, (int(x - p.size * 2), int(y - p.size * 2)))
        
        return True


# 单例实例
_power_surge_instance = None

def get_power_surge() -> PowerSurge:
    """获取单例实例"""
    global _power_surge_instance
    if _power_surge_instance is None:
        _power_surge_instance = PowerSurge()
    return _power_surge_instance
