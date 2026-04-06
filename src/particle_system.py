"""
保卫萝卜 - 粒子特效系统
Carrot Fantasy - Particle Effects System
"""
import pygame
import random
import math


class Particle:
    """单个粒子"""
    
    def __init__(self, x, y, vx, vy, color, lifetime, size, fade=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.fade = fade
        
    def update(self, dt):
        """更新粒子"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        # 减速
        self.vx *= 0.98
        self.vy *= 0.98
        
        return self.lifetime > 0
    
    def draw(self, screen):
        """绘制粒子"""
        if self.lifetime <= 0:
            return
            
        # 计算透明度
        alpha = int(255 * (self.lifetime / self.max_lifetime)) if self.fade else 255
        
        # 绘制发光圆点
        radius = self.size * (self.lifetime / self.max_lifetime)
        if radius < 0.5:
            radius = 0.5
            
        # 外发光
        if radius > 2:
            glow_surf = pygame.Surface((int(radius * 4), int(radius * 4)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, alpha // 3), 
                             (int(radius * 2), int(radius * 2)), int(radius * 2))
            screen.blit(glow_surf, (self.x - radius * 2, self.y - radius * 2))
        
        # 核心
        pygame.draw.circle(screen, (*self.color, alpha), 
                          (int(self.x), int(self.y)), int(radius))


class ParticleSystem:
    """粒子系统管理器"""
    
    def __init__(self):
        self.particles = []
        
    def emit(self, x, y, count, color, lifetime=1.0, size=5, 
             speed=50, spread=360, fade=True, upward=False):
        """发射粒子"""
        for _ in range(count):
            # 随机角度
            if upward:
                angle = random.uniform(-180, 0)  # 向上
            else:
                angle = random.uniform(0, 360)
                
            angle_rad = math.radians(angle)
            velocity = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle_rad) * velocity
            vy = math.sin(angle_rad) * velocity
            
            self.particles.append(Particle(
                x, y, vx, vy, color, lifetime, size, fade
            ))
    
    def emit_explosion(self, x, y, color, count=20):
        """发射爆炸特效"""
        self.emit(x, y, count, color, lifetime=0.5, size=8, 
                 speed=100, spread=360, fade=True)
    
    def emit_hit(self, x, y, color):
        """命中特效"""
        self.emit(x, y, 10, color, lifetime=0.3, size=6, 
                 speed=30, spread=180, fade=True)
    
    def emit_trail(self, x, y, color):
        """拖尾特效"""
        self.emit(x, y, 2, color, lifetime=0.2, size=3, 
                 speed=10, spread=30, fade=True)
    
    def emit_level_up(self, x, y):
        """升级特效"""
        # 金色粒子
        for _ in range(30):
            self.particles.append(Particle(
                x, y,
                random.uniform(-80, 80),
                random.uniform(-150, -50),  # 向上
                (255, 215, 0),  # 金色
                lifetime=random.uniform(0.8, 1.5),
                size=random.uniform(4, 8),
                fade=True
            ))
        # 白色闪烁
        for _ in range(10):
            self.particles.append(Particle(
                x, y,
                random.uniform(-50, 50),
                random.uniform(-100, -30),
                (255, 255, 255),
                lifetime=0.5,
                size=random.uniform(3, 6),
                fade=True
            ))
    
    def emit_money(self, x, y):
        """金币特效"""
        self.emit(x, y, 8, (255, 215, 0), lifetime=0.8, size=5, 
                 speed=60, spread=90, fade=True, upward=True)
    
    def update(self, dt):
        """更新所有粒子"""
        self.particles = [p for p in self.particles if p.update(dt)]
        
    def draw(self, screen):
        """绘制所有粒子"""
        for p in self.particles:
            p.draw(screen)
    
    def clear(self):
        """清除所有粒子"""
        self.particles = []


# 全局粒子系统实例
_global_particle_system = None

def get_particle_system():
    """获取全局粒子系统"""
    global _global_particle_system
    if _global_particle_system is None:
        _global_particle_system = ParticleSystem()
    return _global_particle_system


def create_hit_particles(x, y, tower_type):
    """根据塔类型创建命中特效"""
    ps = get_particle_system()
    
    # 不同塔类型不同颜色
    colors = {
        '箭塔': (100, 200, 100),    # 绿色
        '炮塔': (255, 100, 50),     # 橙红色
        '魔法塔': (150, 100, 255),  # 紫色
    }
    
    color = colors.get(tower_type, (200, 200, 200))
    ps.emit_hit(x, y, color)


def create_trail_particles(x, y, tower_type):
    """创建拖尾粒子"""
    ps = get_particle_system()
    
    colors = {
        '箭塔': (150, 220, 150),
        '炮塔': (255, 150, 100),
        '魔法塔': (180, 140, 255),
    }
    
    color = colors.get(tower_type, (200, 200, 200))
    ps.emit_trail(x, y, color)