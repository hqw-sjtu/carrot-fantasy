"""
保卫萝卜 - 激光瞄准系统
防御塔攻击时的激光瞄准线与目标锁定特效
"""
import pygame
import math
import random


class LaserTargetSystem:
    """激光瞄准系统 - 防御塔攻击时显示激光瞄准线"""
    
    def __init__(self):
        self.lasers = []  # 活跃的激光线
        self.max_life = 0.15  # 激光持续150ms
        
    def add_laser(self, start_pos, end_pos, tower_type="default", damage=0):
        """添加一条激光线"""
        # 根据塔类型设置激光颜色
        colors = {
            "箭塔": (100, 200, 255),    # 蓝色
            "炮塔": (255, 100, 50),     # 橙红色
            "魔法塔": (200, 100, 255),  # 紫色
            "冰冻塔": (150, 230, 255),  # 浅蓝色
            "闪电塔": (255, 255, 100),  # 黄色
            "default": (255, 255, 255)  # 白色
        }
        color = colors.get(tower_type, colors["default"])
        
        laser = {
            'start': start_pos,
            'end': end_pos,
            'color': color,
            'life': 0,
            'damage': damage,
            'active': True,
            'width': 3 if tower_type == "default" else 2
        }
        self.lasers.append(laser)
        
    def update(self, dt):
        """更新所有激光"""
        for laser in self.lasers:
            laser['life'] += dt
            if laser['life'] >= self.max_life:
                laser['active'] = False
        # 清理非活跃激光
        self.lasers = [l for l in self.lasers if l['active']]
        
    def draw(self, screen):
        """绘制所有激光线"""
        for laser in self.lasers:
            if not laser['active']:
                continue
                
            start = laser['start']
            end = laser['end']
            color = laser['color']
            life_ratio = 1 - (laser['life'] / self.max_life)
            
            # 外层发光（半透明）
            glow_color = (*color, int(80 * life_ratio))
            pygame.draw.line(screen, glow_color, start, end, laser['width'] * 4)
            
            # 中层光晕
            mid_color = (*color, int(150 * life_ratio))
            pygame.draw.line(screen, mid_color, start, end, laser['width'] * 2)
            
            # 核心亮线
            core_color = (*color, int(255 * life_ratio))
            pygame.draw.line(screen, core_color, start, end, laser['width'])
            
            # 目标点爆炸效果
            self._draw_target_hit(screen, end, color, life_ratio)
            
    def _draw_target_hit(self, screen, pos, color, intensity):
        """在目标点绘制击中爆炸效果"""
        # 内圈
        radius = int(8 * intensity)
        if radius > 0:
            pygame.draw.circle(screen, color, pos, radius)
        # 外圈扩散
        if intensity > 0.5:
            outer_radius = int(15 * (1 - intensity) * 2)
            outer_color = (*color, int(100 * (1 - intensity)))
            if outer_radius > 0:
                pygame.draw.circle(screen, outer_color, pos, outer_radius, 2)


class TargetLockEffect:
    """目标锁定特效 - 防御塔锁定目标时的追踪圈"""
    
    def __init__(self, target, ring_radius=30):
        self.target = target  # 目标对象
        self.ring_radius = ring_radius
        self.active = True
        self.life = 0
        self.max_life = 0.3  # 300ms
        
    def update(self, dt):
        self.life += dt
        if self.life >= self.max_life or not getattr(self.target, 'alive', True):
            self.active = False
            
    def draw(self, screen):
        if not self.active:
            return
            
        # 获取目标位置
        target_x = getattr(self.target, 'x', 0)
        target_y = getattr(self.target, 'y', 0)
        
        # 脉动半径
        pulse = math.sin(self.life * 20) * 5
        radius = self.ring_radius + pulse
        
        # 绘制锁定圈（虚线效果）
        life_ratio = 1 - (self.life / self.max_life)
        color = (255, 50, 50, int(200 * life_ratio))
        
        # 外圈
        pygame.draw.circle(screen, color[:3], (int(target_x), int(target_y)), int(radius), 2)
        # 内圈
        pygame.draw.circle(screen, color[:3], (int(target_x), int(target_y)), int(radius * 0.6), 1)
        # 十字准星
        cross_size = 8
        pygame.draw.line(screen, color[:3], 
                        (target_x - cross_size, target_y), 
                        (target_x + cross_size, target_y), 1)
        pygame.draw.line(screen, color[:3], 
                        (target_x, target_y - cross_size), 
                        (target_x, target_y + cross_size), 1)


class TowerRangeIndicator:
    """塔攻击范围指示器 - 显示防御塔的攻击范围"""
    
    def __init__(self, tower):
        self.tower = tower
        self.active = True
        self.pulse_life = 0
        
    def update(self, dt):
        self.pulse_life += dt
        
    def draw(self, screen):
        if not self.active:
            return
            
        tower_x = getattr(self.tower, 'x', 0)
        tower_y = getattr(self.tower, 'y', 0)
        tower_range = getattr(self.tower, 'range', 100)
        
        # 计算屏幕像素范围
        grid_size = 40  # 假设网格大小
        pixel_range = tower_range * grid_size
        
        # 脉动效果
        pulse = math.sin(self.pulse_life * 4) * 0.1 + 0.9
        
        # 绘制范围圈（半透明）
        color = (100, 200, 255, 60)
        pygame.draw.circle(screen, color[:3], (int(tower_x), int(tower_y)), 
                          int(pixel_range * pulse), 2)
        
        # 填充半透明区域
        s = pygame.Surface((int(pixel_range * 2), int(pixel_range * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color[:3], 20), 
                          (int(pixel_range), int(pixel_range)), int(pixel_range * pulse))
        screen.blit(s, (int(tower_x - pixel_range), int(tower_y - pixel_range)))