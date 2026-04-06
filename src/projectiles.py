"""
保卫萝卜 - 子弹系统
"""

import math
import pygame

# 尝试导入音效管理器（避免循环导入问题）
try:
    from sound_manager import SoundManager
    _sound_manager = None  # 需要由main.py设置
    def set_sound_manager_for_projectiles(sm):
        global _sound_manager
        _sound_manager = sm
except ImportError:
    _sound_manager = None

class Projectile:
    """子弹类"""
    
    def __init__(self, x, y, target, damage, speed=5, slow_factor=1.0, source_tower=None, tower_type=None):
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
        self.tower_type = tower_type  # 塔类型，用于确定子弹形状
        
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
            # 播放击中音效
            if _sound_manager:
                _sound_manager.play('hit')
        self.active = False
        
    def draw(self, screen):
        """绘制子弹"""
        if not self.active:
            return
        
        # 根据塔类型显示不同形状子弹
        if self.tower_type:
            if "箭" in self.tower_type:
                # 箭塔：三角形（模拟箭矢）
                points = [(self.x, self.y - 6), (self.x - 4, self.y + 4), (self.x + 4, self.y + 4)]
                pygame.draw.polygon(screen, (200, 200, 255), points)
            elif "炮" in self.tower_type:
                # 炮塔：圆形（炮弹）
                pygame.draw.circle(screen, (255, 100, 50), (int(self.x), int(self.y)), 6)
                pygame.draw.circle(screen, (255, 200, 100), (int(self.x), int(self.y)), 3)
            elif "魔法" in self.tower_type:
                # 魔法塔：菱形（魔法弹）
                points = [(self.x, self.y - 7), (self.x + 6, self.y), (self.x, self.y + 7), (self.x - 6, self.y)]
                pygame.draw.polygon(screen, (200, 100, 255), points)
            elif "减速" in self.tower_type:
                # 减速塔：方形（冰晶）
                pygame.draw.rect(screen, (100, 200, 255), (self.x - 5, self.y - 5, 10, 10))
            else:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)
        else:
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 5)
        
        # 绘制命中特效
        if self.hit_effect > 0:
            effect_size = self.hit_effect * 2  # 特效大小随帧数递减
            pygame.draw.circle(screen, (255, 255, 200, 150), (int(self.hit_x), int(self.hit_y)), effect_size)
            self.hit_effect -= 1