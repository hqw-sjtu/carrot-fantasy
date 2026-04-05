"""
保卫萝卜 - 子弹系统
"""

import math
import pygame

class Projectile:
    """子弹类"""
    
    def __init__(self, x, y, target, damage, speed=5, slow_factor=1.0, source_tower=None):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.slow_factor = slow_factor  # 减速因子 (1.0=无减速)
        self.active = True
        self.hit_effect = 0  # 命中特效持续时间
        self.hit_x = 0
        self.hit_y = 0
        self.source_tower = source_tower  # 发射该子弹的塔
        
    def update(self, dt):
        """更新子弹位置"""
        if not self.active or not self.target or not self.target.alive:
            self.active = False
            return
            
        # 计算到目标的方向
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # 如果已经到达目标或距离很近，则命中
        if distance < self.speed * dt:
            self.hit_x = self.target.x
            self.hit_y = self.target.y
            self.hit_effect = 10  # 10帧的命中特效
            self.hit_target()
            return
            
        # 移动子弹
        if distance > 0:
            self.x += (dx / distance) * self.speed * dt
            self.y += (dy / distance) * self.speed * dt
            
    def hit_target(self):
        """命中目标"""
        if self.target and self.target.alive:
            self.target.take_damage(self.damage)
            # 应用减速效果 (持续3秒)
            if self.slow_factor < 1.0:
                self.target.apply_slow(self.slow_factor, 3.0)
        self.active = False
        
    def draw(self, screen):
        """绘制子弹"""
        if self.active:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 3)
        
        # 绘制命中特效
        if self.hit_effect > 0:
            effect_size = self.hit_effect * 2  # 特效大小随帧数递减
            pygame.draw.circle(screen, (255, 255, 200, 150), (int(self.hit_x), int(self.hit_y)), effect_size)
            self.hit_effect -= 1