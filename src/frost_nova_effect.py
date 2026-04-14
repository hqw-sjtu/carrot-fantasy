"""
保卫萝卜 - 冰霜新星特效
Carrot Fantasy - Frost Nova Effect
"""

import pygame
import math
import random


class FrostNovaEffect:
    """冰霜新星特效 - 冰冻波向外扩散"""
    
    def __init__(self, x, y, radius=200, intensity=1.0):
        self.x = x
        self.y = y
        self.max_radius = radius
        self.current_radius = 0
        self.intensity = intensity
        self.max_life = 0.8  # 800ms持续时间
        self.life = 0
        self.active = True
        self.frozen_enemies = []  # 被冰冻的敌人列表
        
        # 粒子系统
        self.particles = []
        self.particle_count = 30
        
    def update(self, dt, game):
        """更新特效状态"""
        if not self.active:
            return
            
        self.life += dt
        
        # 半径扩散
        progress = min(self.life / 0.3, 1.0)  # 前300ms扩散
        self.current_radius = self.max_radius * progress
        
        # 冰冻范围内敌人
        if progress < 1.0 and hasattr(game, 'monsters'):
            for monster in game.monsters:
                if not monster.alive:
                    continue
                dist = math.hypot(monster.x - self.x, monster.y - self.y)
                if dist <= self.current_radius:
                    if monster not in self.frozen_enemies:
                        # 施加冰冻效果
                        monster.frozen = max(monster.frozen, 30)  # 30帧
                        monster.slow_factor = 0.3 * self.intensity  # 70%减速
                        monster.slow_timer = 2.0  # 2秒
                        self.frozen_enemies.append(monster)
        
        # 生成冰晶粒子
        if self.life < self.max_life * 0.5:
            self._spawn_particles()
            
        # 更新粒子
        for p in self.particles[:]:
            p['life'] -= dt
            p['x'] += p['vx'] * dt * 30
            p['y'] += p['vy'] * dt * 30
            if p['life'] <= 0:
                self.particles.remove(p)
        
        # 结束
        if self.life >= self.max_life:
            self.active = False
            
    def _spawn_particles(self):
        """生成冰晶粒子"""
        for _ in range(3):
            angle = random.uniform(0, math.pi * 2)
            dist = self.current_radius * random.uniform(0.5, 1.0)
            self.particles.append({
                'x': self.x + math.cos(angle) * dist,
                'y': self.y + math.sin(angle) * dist,
                'vx': math.cos(angle) * random.uniform(-1, 1),
                'vy': math.sin(angle) * random.uniform(-1, 1),
                'size': random.randint(3, 8),
                'life': 0.5,
                'color': random.choice([
                    (150, 220, 255),
                    (200, 240, 255),
                    (100, 180, 255)
                ])
            })
        
    def draw(self, screen):
        """绘制冰霜新星"""
        if not self.active:
            return
            
        # 绘制冰环
        if self.current_radius > 10:
            # 外环
            pygame.draw.circle(
                screen, 
                (150, 220, 255), 
                (int(self.x), int(self.y)), 
                int(self.current_radius),
                max(1, int(3 * self.intensity))
            )
            # 内环（半透明）
            s = pygame.Surface((int(self.current_radius * 2), int(self.current_radius * 2)), pygame.SRCALPHA)
            pygame.draw.circle(
                s,
                (150, 220, 255, 40),
                (int(self.current_radius), int(self.current_radius)),
                int(self.current_radius * 0.8)
            )
            screen.blit(s, (int(self.x - self.current_radius), int(self.y - self.current_radius)))
        
        # 绘制冰晶粒子
        for p in self.particles:
            alpha = int(255 * (p['life'] / 0.5))
            color = (*p['color'], alpha)
            pygame.draw.circle(screen, p['color'], (int(p['x']), int(p['y'])), p['size'])


class FrostNovaManager:
    """冰霜新星管理器"""
    
    _instance = None
    _effects = []
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def trigger(cls, x, y, radius=200, intensity=1.0):
        """触发冰霜新星"""
        effect = FrostNovaEffect(x, y, radius, intensity)
        cls._effects.append(effect)
        return effect
    
    @classmethod
    def update(cls, dt, game):
        """更新所有特效"""
        for effect in cls._effects[:]:
            effect.update(dt, game)
            if not effect.active:
                cls._effects.remove(effect)
                
    @classmethod
    def draw(cls, screen):
        """绘制所有特效"""
        for effect in cls._effects:
            effect.draw(screen)
    
    @classmethod
    def clear(cls):
        """清除所有特效"""
        cls._effects.clear()


# 预设配置
class FrostNovaPresets:
    """冰霜新星预设"""
    
    @staticmethod
    def small():
        """小型冰霜新星 - 初级冰塔"""
        return {'radius': 120, 'intensity': 0.6}
    
    @staticmethod
    def medium():
        """中型冰霜新星 - 中级冰塔"""
        return {'radius': 180, 'intensity': 0.8}
    
    @staticmethod
    def large():
        """大型冰霜新星 - 高级冰塔"""
        return {'radius': 250, 'intensity': 1.0}
    
    @staticmethod
    def ultimate():
        """终极冰霜新星 - 满级冰塔"""
        return {'radius': 350, 'intensity': 1.5}