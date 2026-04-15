"""
防御塔升级光辉特效 | Tower Upgrade Glow Effect
工艺品级别 - 升级时的绚丽光效
"""
import pygame
import math
import random


class TowerUpgradeGlow:
    """防御塔升级时的光辉特效"""
    
    def __init__(self, x, y, tower_level):
        self.x = x
        self.y = y
        self.level = tower_level
        self.lifetime = 1.5  # 特效持续时间(秒)
        self.elapsed = 0
        self.particles = []
        self.rings = []
        self.max_radius = 80 + tower_level * 15
        
        # 初始化粒子
        self._init_particles()
        # 初始化光环
        self._init_rings()
        
    def _init_particles(self):
        """初始化升级粒子"""
        num_particles = 20 + self.level * 5
        colors = [
            (255, 215, 0),    # 金色
            (255, 255, 200),  # 浅黄
            (255, 180, 50),   # 橙黄
            (255, 255, 255),  # 白色
        ]
        
        for i in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                'x': self.x,
                'y': self.y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed - 50,  # 向上
                'size': random.randint(2, 6),
                'color': random.choice(colors),
                'alpha': 255,
                'life': random.uniform(0.5, 1.2)
            })
    
    def _init_rings(self):
        """初始化扩散光环"""
        self.rings = [
            {'radius': 0, 'alpha': 200, 'width': 4},
            {'radius': 0, 'alpha': 150, 'width': 3},
            {'radius': 0, 'alpha': 100, 'width': 2},
        ]
    
    def update(self, dt):
        """更新特效状态"""
        self.elapsed += dt
        
        # 更新粒子
        for p in self.particles[:]:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 200 * dt  # 重力
            p['life'] -= dt
            p['alpha'] = max(0, int(255 * (p['life'] / 1.0)))
            
            if p['life'] <= 0 or p['alpha'] <= 0:
                self.particles.remove(p)
        
        # 更新光环
        for ring in self.rings:
            ring['radius'] += (self.max_radius / 1.5) * dt
            ring['alpha'] = max(0, ring['alpha'] - 150 * dt)
        
        return self.elapsed < self.lifetime
    
    def draw(self, screen):
        """绘制特效"""
        # 绘制光环
        for ring in self.rings:
            if ring['alpha'] > 0 and ring['radius'] > 0:
                color = (255, 215, 0)
                surface = pygame.Surface((ring['radius'] * 2 + 4, ring['radius'] * 2 + 4), pygame.SRCALPHA)
                center = ring['radius'] + 2
                pygame.draw.circle(surface, (*color, min(255, ring['alpha'])), 
                                 (center, center), 
                                 ring['radius'], ring['width'])
                screen.blit(surface, (self.x - center, self.y - center))
        
        # 绘制粒子
        for p in self.particles:
            if p['alpha'] > 0 and p['life'] > 0:
                size = max(1, int(p['size'] * (p['life'] / 1.0)))
                color = (*p['color'], min(255, p['alpha']))
                surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(surface, color, (size + 1, size + 1), size)
                screen.blit(surface, (int(p['x']) - size - 1, int(p['y']) - size - 1))


class UpgradeGlowManager:
    """升级特效管理器"""
    
    def __init__(self):
        self.effects = []
    
    def spawn(self, x, y, level):
        """生成升级特效"""
        self.effects.append(TowerUpgradeGlow(x, y, level))
    
    def update(self, dt):
        """更新所有特效"""
        for effect in self.effects[:]:
            if not effect.update(dt):
                self.effects.remove(effect)
    
    def draw(self, screen):
        """绘制所有特效"""
        for effect in self.effects:
            effect.draw(screen)
    
    def clear(self):
        """清空特效"""
        self.effects.clear()
