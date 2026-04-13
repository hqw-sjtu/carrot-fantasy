# -*- coding: utf-8 -*-
"""全局光影系统 - Ambient Light System

工艺品级别：全局环境光效，增强游戏沉浸感
- 暗角效果 (Vignette)
- 动态环境光变化
- 屏幕色调调节
- 战斗氛围光照
"""

import pygame
import math
from typing import Tuple, Optional


class AmbientLightSystem:
    """全局光影系统"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 暗角效果
        self.vignette_enabled = True
        self.vignette_strength = 0.4  # 0-1
        self.vignette_radius = 0.7    # 暗角半径比例
        self.vignette_smoothness = 0.5  # 渐变平滑度
        
        # 环境光
        self.base_tint = (255, 255, 255)  # 基础色调
        self.current_tint = (255, 255, 255)
        self.target_tint = (255, 255, 255)
        self.tint_transition_speed = 2.0
        
        # 亮度
        self.brightness = 1.0  # 0-2, 1为正常
        self.target_brightness = 1.0
        
        # 战斗氛围
        self.battle_mode = False
        self.battle_intensity = 0.0  # 0-1
        self.battle_pulse = 0.0
        
        # 颜色配置
        self.presets = {
            "normal": {"tint": (255, 255, 255), "brightness": 1.0, "vignette": 0.3},
            "night": {"tint": (180, 190, 220), "brightness": 0.85, "vignette": 0.5},
            "sunset": {"tint": (255, 200, 150), "brightness": 0.95, "vignette": 0.35},
            "boss": {"tint": (255, 100, 100), "brightness": 1.1, "vignette": 0.6},
            "victory": {"tint": (255, 240, 200), "brightness": 1.2, "vignette": 0.2},
        }
        
        # 预渲染暗角表面
        self._vignette_surface = None
        self._create_vignette_surface()
    
    def _create_vignette_surface(self):
        """创建暗角渐变表面"""
        self._vignette_surface = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA
        )
        
        # 从中心到边缘的渐变
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        max_radius = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(self.screen_height):
            for x in range(self.screen_width):
                # 计算到中心的距离
                dx = x - center_x
                dy = y - center_y
                dist = math.sqrt(dx*dx + dy*dy)
                
                # 归一化距离
                norm_dist = dist / max_radius
                
                # 暗角强度计算
                if norm_dist > self.vignette_radius:
                    # 边缘区域
                    edge_factor = (norm_dist - self.vignette_radius) / (1 - self.vignette_radius)
                    edge_factor = max(0, min(1, edge_factor))
                    # 平滑过渡
                    edge_factor = edge_factor ** (1 / self.vignette_smoothness)
                    alpha = int(self.vignette_strength * edge_factor * 255)
                else:
                    alpha = 0
                
                if alpha > 0:
                    self._vignette_surface.set_at((x, y), (0, 0, 0, alpha))
    
    def set_preset(self, preset_name: str, transition: bool = True):
        """设置环境光预设"""
        if preset_name not in self.presets:
            return
        
        preset = self.presets[preset_name]
        
        if transition:
            self.target_tint = preset["tint"]
            self.target_brightness = preset["brightness"]
            self.vignette_strength = preset.get("vignette", self.vignette_strength)
        else:
            self.current_tint = preset["tint"]
            self.target_tint = preset["tint"]
            self.brightness = preset["brightness"]
            self.target_brightness = preset["brightness"]
            self.vignette_strength = preset.get("vignette", self.vignette_strength)
    
    def start_battle_mode(self):
        """进入战斗模式"""
        self.battle_mode = True
        self.battle_intensity = 0.0
    
    def end_battle_mode(self):
        """退出战斗模式"""
        self.battle_mode = False
        self.target_tint = self.presets["normal"]["tint"]
        self.target_brightness = self.presets["normal"]["brightness"]
    
    def update(self, dt: float):
        """更新光影效果"""
        # 平滑过渡色调
        r = self.current_tint[0] + (self.target_tint[0] - self.current_tint[0]) * self.tint_transition_speed * dt
        g = self.current_tint[1] + (self.target_tint[1] - self.current_tint[1]) * self.tint_transition_speed * dt
        b = self.current_tint[2] + (self.target_tint[2] - self.current_tint[2]) * self.tint_transition_speed * dt
        self.current_tint = (int(r), int(g), int(b))
        
        # 亮度过渡
        self.brightness += (self.target_brightness - self.brightness) * self.tint_transition_speed * dt
        
        # 战斗模式效果
        if self.battle_mode:
            self.battle_intensity = min(1.0, self.battle_intensity + dt * 0.5)
            self.battle_pulse += dt * 5.0
            
            # 战斗时偏红色调
            pulse = (math.sin(self.battle_pulse) + 1) / 2
            battle_tint = (
                int(255 * (1 - pulse * 0.3)),
                int(220 - pulse * 20),
                int(220 - pulse * 70)
            )
            self.target_tint = battle_tint
            self.target_brightness = 1.0 + pulse * 0.1
        else:
            self.battle_intensity = max(0.0, self.battle_intensity - dt * 0.8)
    
    def apply_tint(self, surface: pygame.Surface) -> pygame.Surface:
        """应用色调到表面"""
        if self.current_tint == (255, 255, 255) and self.brightness == 1.0:
            return surface
        
        # 创建色调表面
        tinted = surface.copy()
        tint_surf = pygame.Surface(surface.get_size())
        tint_surf.fill(self.current_tint)
        
        # 混合
        tinted.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        
        # 亮度调整
        if self.brightness != 1.0:
            # 使用亮度调节
            for y in range(tinted.get_height()):
                for x in range(tinted.get_width()):
                    color = tinted.get_at((x, y))
                    if color.a > 0:  # 只处理非透明像素
                        r = min(255, int(color.r * self.brightness))
                        g = min(255, int(color.g * self.brightness))
                        b = min(255, int(color.b * self.brightness))
                        tinted.set_at((x, y), pygame.Color(r, g, b, color.a))
        
        return tinted
    
    def draw(self, screen: pygame.Surface):
        """绘制光影效果"""
        if not self.vignette_enabled:
            return
        
        # 绘制暗角
        screen.blit(self._vignette_surface, (0, 0))
        
        # 战斗模式额外效果
        if self.battle_intensity > 0:
            # 红色光晕
            pulse = (math.sin(self.battle_pulse) + 1) / 2
            overlay = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            alpha = int(self.battle_intensity * pulse * 30)
            overlay.fill((255, 50, 0, alpha))
            screen.blit(overlay, (0, 0))
    
    def get_light_info(self) -> dict:
        """获取当前光照信息"""
        return {
            "tint": self.current_tint,
            "brightness": self.brightness,
            "vignette_strength": self.vignette_strength,
            "battle_mode": self.battle_mode,
            "battle_intensity": self.battle_intensity,
        }


# 全局单例
_ambient_light_instance: Optional[AmbientLightSystem] = None


def get_ambient_light() -> AmbientLightSystem:
    """获取全局光影系统实例"""
    global _ambient_light_instance
    if _ambient_light_instance is None:
        # 需要先初始化
        raise RuntimeError("AmbientLightSystem not initialized. Call init_ambient_light() first.")
    return _ambient_light_instance


def init_ambient_light(screen_width: int = 800, screen_height: int = 600):
    """初始化全局光影系统"""
    global _ambient_light_instance
    _ambient_light_instance = AmbientLightSystem(screen_width, screen_height)
    return _ambient_light_instance


__all__ = ['AmbientLightSystem', 'get_ambient_light', 'init_ambient_light']