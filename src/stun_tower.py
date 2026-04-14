"""
眩晕塔系统 (Stun Tower)
工艺品级别 - 使敌人眩晕的防御塔

功能:
- 周期性眩晕范围内敌人
- 眩晕条可视化显示
- 眩晕抵抗机制（boss有抗性）
- 眩晕连锁效果
"""

import pygame
import random
import math


class StunEffect:
    """眩晕效果"""
    
    def __init__(self, duration, intensity=1.0):
        self.duration = duration  # 眩晕持续时间（秒）
        self.intensity = intensity  # 眩晕强度
        self.remaining = duration
        self.stunned = True
        
    def update(self, dt):
        self.remaining -= dt
        if self.remaining <= 0:
            self.stunned = False
        return self.stunned
    
    def get_progress(self):
        """获取眩晕进度（0-1）"""
        if self.duration <= 0:
            return 1.0
        return 1.0 - (self.remaining / self.duration)


class StunIndicator:
    """眩晕指示器 - 显示在受击敌人头上"""
    
    _instances = []
    
    @classmethod
    def clear_all(cls):
        cls._instances = []
    
    @classmethod
    def create(cls, x, y, duration, intensity=1.0):
        indicator = cls(x, y, duration, intensity)
        cls._instances.append(indicator)
        return indicator
    
    def __init__(self, x, y, duration, intensity):
        self.x = x
        self.y = y
        self.duration = duration
        self.remaining = duration
        self.intensity = intensity
        self.stars = []
        self.rotation = 0
        # 生成星星
        for i in range(5):
            angle = (i / 5) * math.pi * 2
            self.stars.append({
                'angle': angle,
                'distance': 20 + random.random() * 10,
                'speed': random.uniform(2, 4)
            })
    
    def update(self, dt):
        self.remaining -= dt
        self.rotation += 180 * dt
        # 更新星星
        for star in self.stars:
            star['angle'] += star['speed'] * dt
        return self.remaining > 0
    
    def draw(self, surface, camera_offset=(0, 0)):
        if self.remaining <= 0:
            return
        
        # 半透明背景
        progress = 1.0 - (self.remaining / self.duration)
        alpha = int(200 * (1 - progress * 0.5))
        
        center_x = self.x - camera_offset[0]
        center_y = self.y - camera_offset[1] - 30
        
        # 绘制眩晕图标（旋转的星星）
        for star in self.stars:
            sx = center_x + math.cos(star['angle']) * star['distance']
            sy = center_y + math.sin(star['angle']) * star['distance']
            
            # 星星颜色根据强度变化
            color = (255, 255, 0) if self.intensity > 0.7 else (255, 200, 0)
            
            # 绘制小星星
            size = max(2, int(4 * self.intensity))
            
            # 创建临时表面实现透明度
            temp_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*color, alpha), (size, size), size)
            surface.blit(temp_surface, (sx - size, sy - size))
        
        # 中心大星星
        rotation_rad = math.radians(self.rotation)
        self._draw_star(surface, center_x, center_y, 8, 4, (255, 255, 100), alpha)
    
    def _draw_star(self, surface, cx, cy, outer_r, inner_r, color, alpha):
        """绘制五角星"""
        points = []
        for i in range(10):
            angle = math.radians(self.rotation + i * 36 - 90)
            r = outer_r if i % 2 == 0 else inner_r
            points.append((
                cx + math.cos(angle) * r,
                cy + math.sin(angle) * r
            ))
        
        # 使用临时表面实现透明度
        if alpha < 255:
            temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            pygame.draw.polygon(temp_surface, (*color, alpha), points)
            surface.blit(temp_surface, (0, 0))
        else:
            pygame.draw.polygon(surface, color, points)


class StunTower:
    """眩晕塔"""
    
    TOWER_NAME = "眩晕塔"
    TOWER_ICON = "⚡"
    
    def __init__(self, x, y, level=1):
        self.x = x
        self.y = y
        self.level = level
        
        # 基础属性（根据等级）
        base_stats = [
            {'damage': 5, 'range': 100, 'stun_duration': 1.0, 'cooldown': 1.5, 'aoe': 0},
            {'damage': 8, 'range': 120, 'stun_duration': 1.5, 'cooldown': 1.2, 'aoe': 30},
            {'damage': 12, 'range': 150, 'stun_duration': 2.0, 'cooldown': 1.0, 'aoe': 50},
        ]
        
        stats = base_stats[min(level - 1, 2)]
        self.damage = stats['damage']
        self.range = stats['range']
        self.stun_duration = stats['stun_duration']
        self.cooldown = stats['cooldown']
        self.aoe_radius = stats['aoe']
        
        self.cooldown_timer = 0
        self.active = True
        self.animation_phase = 0
        
        # 特效相关
        self.pulse_radius = 0
        self.pulse_alpha = 0
        self.chain_lightning = []  # 链式闪电
        
    def update(self, dt, enemies, projectiles_list):
        self.cooldown_timer -= dt
        self.animation_phase += dt * 3
        
        # 更新脉冲效果
        if self.pulse_radius > 0:
            self.pulse_radius += dt * 200
            self.pulse_alpha -= dt * 255
            if self.pulse_alpha <= 0:
                self.pulse_radius = 0
        
        # 更新链式闪电
        self.chain_lightning = [bolt for bolt in self.chain_lightning if bolt[2] > 0]
        for i in range(len(self.chain_lightning)):
            self.chain_lightning[i] = (self.chain_lightning[i][0], 
                                        self.chain_lightning[i][1], 
                                        self.chain_lightning[i][2] - dt)
        
        # 寻找目标并攻击
        if self.cooldown_timer <= 0:
            targets = self._find_targets(enemies)
            if targets:
                self._attack(targets, projectiles_list)
                self.cooldown_timer = self.cooldown
    
    def _find_targets(self, enemies):
        """寻找范围内敌人"""
        targets = []
        for enemy in enemies:
            if not hasattr(enemy, 'alive') or not enemy.alive:
                continue
            if hasattr(enemy, 'stunned') and enemy.stunned:
                continue  # 已经眩晕的敌人不重复眩晕
            
            dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
            if dist <= self.range:
                targets.append((enemy, dist))
        
        # 按距离排序
        targets.sort(key=lambda x: x[1])
        return [t[0] for t in targets[:5]]  # 最多眩晕5个
    
    def _attack(self, targets, projectiles_list):
        """攻击敌人"""
        self.cooldown_timer = self.cooldown
        
        # 触发脉冲效果
        self.pulse_radius = 10
        self.pulse_alpha = 200
        
        # 对每个目标造成伤害和眩晕
        for target in targets:
            if hasattr(target, 'stunned') and hasattr(target, 'hp'):
                # 造成伤害
                damage = self.damage
                target.hp -= damage
                
                # 施加眩晕
                stun_resistance = getattr(target, 'stun_resistance', 0)
                actual_duration = self.stun_duration * (1 - stun_resistance)
                
                if actual_duration > 0:
                    if not hasattr(target, 'stun_effect'):
                        target.stun_effect = StunEffect(actual_duration, 1.0)
                    else:
                        # 刷新眩晕时间
                        target.stun_effect = StunEffect(actual_duration, 1.0)
                    target.stunned = True
                    
                    # 创建眩晕指示器
                    StunIndicator.create(target.x, target.y, actual_duration, 1.0)
                
                # 记录链式闪电
                self.chain_lightning.append((self.x, target.x, 0.2))
        
        # AOE眩晕效果
        if self.aoe_radius > 0:
            for enemy in targets:
                if enemy in targets:
                    continue
                for target in targets:
                    dist = math.sqrt((enemy.x - target.x)**2 + (enemy.y - target.y)**2)
                    if dist <= self.aoe_radius and hasattr(enemy, 'hp'):
                        # AOE范围内的敌人也受波及
                        aoe_damage = self.damage * 0.3
                        enemy.hp -= aoe_damage
    
    def draw(self, surface, camera_offset=(0, 0)):
        cx = self.x - camera_offset[0]
        cy = self.y - camera_offset[1]
        
        # 绘制范围圈（淡入效果）
        if self.pulse_radius > 0:
            pulse_color = (255, 255, 100, int(self.pulse_alpha))
            pygame.draw.circle(surface, pulse_color, (cx, cy), int(self.pulse_radius), 2)
        
        # 塔基座
        base_color = (100, 100, 120)
        pygame.draw.circle(surface, base_color, (cx, cy), 20)
        
        # 塔身
        tower_color = (255, 200, 0)  # 金色
        pygame.draw.circle(surface, tower_color, (cx, cy), 15)
        
        # 塔顶装饰 - 旋转的闪电
        self._draw_lightning_symbol(surface, cx, cy - 5)
        
        # 绘制攻击范围
        range_color = (255, 255, 0, 30)
        pygame.draw.circle(surface, range_color, (cx, cy), int(self.range), 1)
    
    def _draw_lightning_symbol(self, surface, cx, cy):
        """绘制闪电符号"""
        # 简单的闪电符号
        points = [
            (cx + 3, cy - 8),
            (cx - 2, cy - 2),
            (cx + 2, cy - 2),
            (cx - 3, cy + 8),
            (cx + 2, cy),
            (cx - 2, cy),
        ]
        pygame.draw.polygon(surface, (255, 255, 255), points)
    
    def draw_chain_lightning(self, surface, camera_offset=(0, 0)):
        """绘制链式闪电"""
        for start_x, end_x, _ in self.chain_lightning:
            start_pos = (start_x - camera_offset[0], self.y - camera_offset[1])
            end_pos = (end_x - camera_offset[0], self.y - camera_offset[1])
            
            # 绘制闪电链
            self._draw_bolt(surface, start_pos, end_pos)
    
    def _draw_bolt(self, surface, start, end):
        """绘制闪电 bolt"""
        # 简化的闪电效果
        mid_x = (start[0] + end[0]) / 2 + random.uniform(-10, 10)
        mid_y = (start[1] + end[1]) / 2
        
        points = [start, (mid_x, mid_y), end]
        
        # 绘制主线
        pygame.draw.line(surface, (255, 255, 150), start, end, 2)
        
        # 分叉闪电
        if random.random() > 0.5:
            branch_end = (mid_x + random.uniform(-20, 20), mid_y + random.uniform(10, 30))
            pygame.draw.line(surface, (200, 200, 100), (mid_x, mid_y), branch_end, 1)


# 全局函数
def update_stun_effects(enemies, dt):
    """更新所有敌人的眩晕效果"""
    StunIndicator.clear_all()
    
    for enemy in enemies:
        if hasattr(enemy, 'stun_effect') and enemy.stun_effect:
            if not enemy.stun_effect.update(dt):
                enemy.stunned = False
                enemy.stun_effect = None
            else:
                enemy.stunned = True
                # 创建指示器
                StunIndicator.create(enemy.x, enemy.y, 
                                    enemy.stun_effect.remaining,
                                    enemy.stun_effect.intensity)


def draw_stun_indicators(surface, camera_offset=(0, 0)):
    """绘制所有眩晕指示器"""
    for indicator in StunIndicator._instances:
        indicator.draw(surface, camera_offset)