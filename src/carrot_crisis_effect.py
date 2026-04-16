# -*- coding: utf-8 -*-
"""萝卜危机特效系统 - Carrot Crisis Effect

当萝卜血量低于一定阈值时，触发危机视觉警告效果。
按L键打开图鉴。
"""

import pygame
import math
import random


class CarrotCrisisEffect:
    """萝卜危机特效"""
    
    def __init__(self):
        self.enabled = False
        self.intensity = 0.0  # 0.0-1.0 危机强度
        self.pulse_phase = 0  # 脉冲相位
        self.warning_color = (255, 50, 50)  # 警告色
        self.crack_lines = []  # 裂纹效果
        self.shake_offset = (0, 0)  # 震动偏移
        self.glow_strength = 0  # 发光强度
        
    def update(self, carrot_hp_ratio: float, dt: float):
        """更新危机特效
        
        Args:
            carrot_hp_ratio: 萝卜血量比例 (0.0-1.0)
            dt: .delta时间(秒)
        """
        # 血量低于30%开始危机效果
        threshold = 0.3
        if carrot_hp_ratio < threshold:
            # 计算危机强度 (血量越低越强)
            self.intensity = (threshold - carrot_hp_ratio) / threshold
            self.intensity = min(1.0, self.intensity * 1.5)  # 放大效果
            self.enabled = True
            
            # 更新脉冲
            self.pulse_phase += dt * (3 + self.intensity * 4)
            
            # 更新震动
            if self.intensity > 0.3:
                magnitude = int(self.intensity * 5)
                self.shake_offset = (
                    random.randint(-magnitude, magnitude),
                    random.randint(-magnitude, magnitude)
                )
            else:
                self.shake_offset = (0, 0)
            
            # 更新发光
            self.glow_strength = (math.sin(self.pulse_phase * 2) + 1) / 2 * self.intensity
            
            # 更新裂纹 (低血量时出现)
            if self.intensity > 0.5 and random.random() < 0.02:
                self._add_crack()
        else:
            self.enabled = False
            self.intensity = 0
            self.shake_offset = (0, 0)
    
    def _add_crack(self):
        """添加裂纹"""
        if len(self.crack_lines) < 8:
            self.crack_lines.append({
                'start': (random.randint(100, 700), random.randint(50, 150)),
                'end': (random.randint(100, 700), random.randint(200, 350)),
                'width': random.randint(1, 3)
            })
    
    def draw(self, screen: pygame.Surface, carrot_pos: tuple, carrot_radius: int):
        """绘制危机特效
        
        Args:
            screen: 屏幕surface
            carrot_pos: 萝卜位置 (x, y)
            carrot_radius: 萝卜半径
        """
        if not self.enabled:
            return
        
        cx, cy = carrot_pos
        
        # 1. 红色发光光环
        if self.glow_strength > 0.1:
            glow_radius = int(carrot_radius * (1.5 + self.glow_strength * 0.8))
            glow_surface = pygame.Surface((glow_radius * 2 + 40, glow_radius * 2 + 40), pygame.SRCALPHA)
            
            # 多层发光
            for i in range(5, 0, -1):
                alpha = int(30 * self.glow_strength * (6 - i) / 5)
                pygame.draw.circle(
                    glow_surface, 
                    (*self.warning_color, alpha),
                    (glow_radius + 20, glow_radius + 20),
                    glow_radius * i // 4
                )
            
            screen.blit(glow_surface, (cx - glow_radius - 20 + self.shake_offset[0], 
                                        cy - glow_radius - 20 + self.shake_offset[1]))
        
        # 2. 脉冲边框
        pulse_size = int(20 + self.intensity * 15 + math.sin(self.pulse_phase) * 5)
        pygame.draw.circle(
            screen,
            (*self.warning_color, 100 + int(100 * self.glow_strength)),
            (cx + self.shake_offset[0], cy + self.shake_offset[1]),
            carrot_radius + pulse_size,
            3
        )
        
        # 3. 裂纹效果 (低血量时)
        if self.intensity > 0.4:
            for crack in self.crack_lines:
                pygame.draw.line(
                    screen,
                    (80, 20, 20),
                    (cx - carrot_radius + crack['start'][0] // 10 + self.shake_offset[0],
                     cy - carrot_radius + crack['start'][1] // 10 + self.shake_offset[1]),
                    (cx - carrot_radius + crack['end'][0] // 10 + self.shake_offset[0],
                     cy - carrot_radius + crack['end'][1] // 10 + self.shake_offset[1]),
                    crack['width']
                )


class CarrotProtectionAura:
    """萝卜保护光环 - 血量高时的正向反馈"""
    
    def __init__(self):
        self.rings = []
        self.max_rings = 3
        
    def update(self, carrot_hp_ratio: float, dt: float):
        """更新保护光环
        
        Args:
            carrot_hp_ratio: 萝卜血量比例 (0.0-1.0)
            dt: delta时间
        """
        # 血量高于70%显示保护光环
        if carrot_hp_ratio > 0.7:
            # 随机添加新光环
            if random.random() < 0.03 * carrot_hp_ratio:
                self.rings.append({
                    'radius': 40,
                    'alpha': 180,
                    'speed': 30
                })
        
        # 更新现有光环
        for ring in self.rings[:]:
            ring['radius'] += ring['speed'] * dt
            ring['alpha'] -= 60 * dt
            
            if ring['alpha'] <= 0:
                self.rings.remove(ring)
        
        # 限制数量
        self.rings = self.rings[:self.max_rings]
    
    def draw(self, screen: pygame.Surface, carrot_pos: tuple):
        """绘制保护光环
        
        Args:
            screen: 屏幕surface
            carrot_pos: 萝卜位置 (x, y)
        """
        cx, cy = carrot_pos
        
        for ring in self.rings:
            # 绿色保护光环
            color = (100, 255, 100, int(ring['alpha']))
            pygame.draw.circle(
                screen,
                color,
                (cx, cy),
                int(ring['radius']),
                2
            )


# 全局实例
_crisis_effect = CarrotCrisisEffect()
_protection_aura = CarrotProtectionAura()


def get_crisis_effect() -> CarrotCrisisEffect:
    """获取危机特效实例"""
    return _crisis_effect


def get_protection_aura() -> CarrotProtectionAura:
    """获取保护光环实例"""
    return _protection_aura


def update_carrot_effects(carrot_hp_ratio: float, dt: float):
    """更新萝卜所有视觉效果
    
    Args:
        carrot_hp_ratio: 萝卜血量比例
        dt: delta时间
    """
    _crisis_effect.update(carrot_hp_ratio, dt)
    _protection_aura.update(carrot_hp_ratio, dt)


def draw_carrot_effects(screen: pygame.Surface, carrot_pos: tuple, carrot_radius: int):
    """绘制萝卜所有视觉效果
    
    Args:
        screen: 屏幕surface
        carrot_pos: 萝卜位置
        carrot_radius: 萝卜半径
    """
    # 先画保护光环(底层)
    _protection_aura.draw(screen, carrot_pos)
    # 再画危机特效(顶层)
    _crisis_effect.draw(screen, carrot_pos, carrot_radius)