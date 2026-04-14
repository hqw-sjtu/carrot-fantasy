"""
保卫萝卜 - 护盾破碎特效系统
Carrot Fantasy - Shield Shatter Effect System
"""
import pygame
import math
import random


class ShatterParticle:
    """破碎碎片粒子"""
    
    def __init__(self, x, y, color, size, velocity, rotation_speed):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = rotation_speed
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.05)
        self.gravity = random.uniform(50, 150)
        self.shape = random.choice(['triangle', 'diamond', 'shard'])
    
    def update(self, dt):
        """更新粒子状态"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt  # 重力
        self.rotation += self.rotation_speed * dt
        self.life -= self.decay
        return self.life > 0
    
    def draw(self, screen):
        """绘制碎片"""
        if self.life <= 0:
            return
        
        alpha = int(255 * self.life)
        size = max(2, self.size * self.life)
        
        # 旋转后的顶点
        rad = math.radians(self.rotation)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        
        if self.shape == 'triangle':
            points = [
                (self.x + size * cos_a, self.y + size * sin_a),
                (self.x + size * 0.5 * math.cos(rad + 2.09), 
                 self.y + size * 0.5 * math.sin(rad + 2.09)),
                (self.x + size * 0.5 * math.cos(rad - 2.09), 
                 self.y + size * 0.5 * math.sin(rad - 2.09)),
            ]
        elif self.shape == 'diamond':
            points = [
                (self.x, self.y - size),
                (self.x + size * 0.7, self.y),
                (self.x, self.y + size),
                (self.x - size * 0.7, self.y),
            ]
            # 应用旋转
            points = [(self.x + (px - self.x) * cos_a - (py - self.y) * sin_a,
                       self.y + (px - self.x) * sin_a + (py - self.y) * cos_a)
                      for px, py in points]
        else:  # shard
            points = [
                (self.x + size * cos_a * 0.8, self.y + size * sin_a * 0.8),
                (self.x + size * 0.3 * math.cos(rad + 1.5), 
                 self.y + size * 0.3 * math.sin(rad + 1.5)),
                (self.x - size * 0.2 * cos_a, self.y - size * 0.2 * sin_a),
                (self.x + size * 0.3 * math.cos(rad - 1.5), 
                 self.y + size * 0.3 * math.sin(rad - 1.5)),
            ]
        
        # 绘制填充
        color = tuple(min(255, int(c * self.life + 50 * (1 - self.life))) for c in self.color)
        pygame.draw.polygon(screen, color, points)
        
        # 绘制高光边缘
        if self.life > 0.5:
            edge_color = tuple(min(255, c + 80) for c in color)
            pygame.draw.polygon(screen, edge_color, points, 1)


class ShatterEffect:
    """护盾破碎特效管理器"""
    
    def __init__(self):
        self.particles = []
    
    def create_shatter(self, x, y, color=(100, 200, 255), count=15):
        """创建破碎特效"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            velocity = (
                math.cos(angle) * speed + random.uniform(-50, 50),
                math.sin(angle) * speed - random.uniform(50, 150)  # 向上爆发
            )
            size = random.uniform(4, 12)
            rotation_speed = random.uniform(-180, 180)
            
            particle = ShatterParticle(x, y, color, size, velocity, rotation_speed)
            self.particles.append(particle)
    
    def update(self, dt):
        """更新所有粒子"""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen):
        """绘制所有碎片"""
        for particle in self.particles:
            particle.draw(screen)
    
    def is_active(self):
        """检查是否有活跃粒子"""
        return len(self.particles) > 0
    
    def clear(self):
        """清除所有粒子"""
        self.particles.clear()


# 涟漪特效
class RippleEffect:
    """涟漪扩散特效"""
    
    def __init__(self, x, y, max_radius=50, color=(255, 255, 255)):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = max_radius
        self.color = color
        self.life = 1.0
        self.speed = 80
    
    def update(self, dt):
        self.radius += self.speed * dt
        self.life = 1 - (self.radius / self.max_radius)
        return self.radius < self.max_radius
    
    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(255 * self.life)
        # 使用半透明绘制
        color = tuple(min(255, int(c * self.life)) for c in self.color)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 
                          int(self.radius), 2)


class RippleManager:
    """涟漪特效管理器"""
    
    def __init__(self):
        self.ripples = []
    
    def add_ripple(self, x, y, max_radius=50, color=(255, 255, 255)):
        self.ripples.append(RippleEffect(x, y, max_radius, color))
    
    def update(self, dt):
        self.ripples = [r for r in self.ripples if r.update(dt)]
    
    def draw(self, screen):
        for ripple in self.ripples:
            ripple.draw(screen)
    
    def clear(self):
        self.ripples.clear()