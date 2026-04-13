"""
保卫萝卜 - 轨道护盾环绕特效
Carrot Fantasy - Orbital Shield Effect
"""
import pygame
import math
import random


class OrbitalShieldEffect:
    """防御塔轨道护盾环绕特效"""
    
    def __init__(self, x, y, radius=40, color=(100, 200, 255)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.angle = 0
        self.particles = []
        self.max_particles = 12
        self.active = True
        self.alpha = 200
        
    def update(self, dt):
        """更新护盾效果"""
        self.angle += 60 * dt  # 旋转速度
        
        # 生成轨道粒子
        if len(self.particles) < self.max_particles:
            if random.random() < 0.3:
                self.particles.append(self._create_particle())
        
        # 更新粒子
        for p in self.particles:
            p['angle'] += p['speed'] * dt
            p['life'] -= dt
            p['size'] = max(2, p['size'] * 0.99)
        
        # 移除死亡粒子
        self.particles = [p for p in self.particles if p['life'] > 0]
        
        # 淡出效果
        if not self.active:
            self.alpha = max(0, self.alpha - 100 * dt)
            
        return self.alpha > 0
    
    def _create_particle(self):
        """创建轨道粒子"""
        angle = random.uniform(0, 360)
        return {
            'angle': angle,
            'speed': random.uniform(40, 80),
            'size': random.uniform(3, 6),
            'life': random.uniform(1, 2),
            'color': random.choice([
                (100, 200, 255),  # 蓝色
                (150, 220, 255),  # 浅蓝
                (200, 240, 255),  # 亮蓝
            ])
        }
    
    def draw(self, screen):
        """绘制护盾效果"""
        if self.alpha <= 0:
            return
            
        # 绘制轨道圆环
        pygame.draw.circle(
            screen, 
            (*self.color, self.alpha // 3),
            (int(self.x), int(self.y)),
            self.radius,
            2
        )
        
        # 绘制轨道粒子
        for p in self.particles:
            rad = math.radians(p['angle'])
            px = self.x + math.cos(rad) * self.radius
            py = self.y + math.sin(rad) * self.radius
            
            # 粒子发光
            size = int(p['size'])
            if size > 3:
                # 外发光
                pygame.draw.circle(
                    screen,
                    (*p[:3], self.alpha // 4),
                    (int(px), int(py)),
                    size + 2
                )
            
            # 核心
            pygame.draw.circle(
                screen,
                (*p['color'], self.alpha),
                (int(px), int(py)),
                size
            )


class OrbitalShieldManager:
    """轨道护盾管理器"""
    
    def __init__(self):
        self.shields = {}
        
    def add_shield(self, tower_id, x, y):
        """为防御塔添加轨道护盾"""
        self.shields[tower_id] = OrbitalShieldEffect(x, y)
        
    def remove_shield(self, tower_id):
        """移除防御塔的轨道护盾"""
        if tower_id in self.shields:
            self.shields[tower_id].active = False
            
    def update(self, dt):
        """更新所有护盾"""
        for shield in list(self.shields.values()):
            shield.update(dt)
        # 清理不活跃的护盾
        self.shields = {k: v for k, v in self.shields.items() if v.alpha > 0}
        
    def draw(self, screen):
        """绘制所有护盾"""
        for shield in self.shields.values():
            shield.draw(screen)


# 全局管理器实例
orbital_shield_manager = OrbitalShieldManager()