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
        self.is_critical = False  # 是否暴击
        # 弹道轨迹系统
        self.trail_positions = []  # 轨迹位置列表
        self.trail_max_length = 8  # 轨迹最大长度
        self.last_x = x  # 上一次位置
        self.last_y = y
        
    def update(self, dt):
        """更新子弹位置"""
        if not self.active or not self.target or not self.target.alive:
            self.active = False
            return
        
        # 记录当前位置到轨迹
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > self.trail_max_length:
            self.trail_positions.pop(0)
        
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
            # 暴击概率检测
            import random
            if random.random() < 0.1:  # 10%暴击率
                self.is_critical = True
                self.damage = int(self.damage * 1.5)  # 暴击伤害提升50%
                
            self.target.take_damage(self.damage)
            # 应用减速效果 (持续3秒)
            if self.slow_factor < 1.0:
                self.target.apply_slow(self.slow_factor, 3.0)
            # 播放击中音效
            if _sound_manager:
                _sound_manager.play('hit')
            
            # 暴击时触发特效
            if self.is_critical and hasattr(self.source_tower, 'particle_system'):
                self.source_tower.particle_system.add_critical_effect(self.target.x, self.target.y)
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
        
        # 绘制弹道轨迹
        if len(self.trail_positions) >= 2:
            for i, (tx, ty) in enumerate(self.trail_positions):
                # 轨迹渐变透明度
                alpha = int(255 * (i / len(self.trail_positions)) * 0.6)
                color = self._get_trail_color(alpha)
                size = max(1, 3 * (i / len(self.trail_positions)))
                pygame.draw.circle(screen, color, (int(tx), int(ty)), int(size))
        
        # 绘制命中特效
        if self.hit_effect > 0:
            effect_size = self.hit_effect * 2  # 特效大小随帧数递减
            pygame.draw.circle(screen, (255, 255, 200, 150), (int(self.hit_x), int(self.hit_y)), effect_size)
            self.hit_effect -= 1
    
    def _get_trail_color(self, alpha):
        """获取轨迹颜色（根据塔类型）"""
        if self.tower_type:
            if "箭" in self.tower_type:
                return (200, 200, 255, alpha)
            elif "炮" in self.tower_type:
                return (255, 150, 50, alpha)
            elif "魔法" in self.tower_type:
                return (180, 80, 255, alpha)
            elif "减速" in self.tower_type:
                return (100, 200, 255, alpha)
        return (255, 255, 150, alpha)