# -*- coding: utf-8 -*-
"""成就徽章展示系统 - Achievement Badges Display

在游戏主界面顶部显示已解锁的成就徽章，点击可查看详情。
"""

import math
import pygame
from typing import List, Tuple, Optional


class AchievementBadge:
    """成就徽章"""
    def __init__(self, id: str, name: str, icon: str, color: Tuple[int, int, int]):
        self.id = id
        self.name = name
        self.icon = icon
        self.color = color  # 徽章颜色
        self.x = 0
        self.y = 0
        self.hovered = False
        self.pulse_phase = 0.0  # 脉冲动画相位
    
    def update(self, dt: float):
        """更新徽章动画"""
        self.pulse_phase += dt * 3.0
        if self.pulse_phase > 6.28:
            self.pulse_phase -= 6.28
    
    def draw(self, screen: pygame.Surface, small_font: pygame.font.Font):
        """绘制徽章"""
        # 脉冲发光效果
        pulse = (math.sin(self.pulse_phase) + 1) / 2  # 0-1
        glow_size = 4 + pulse * 3
        
        # 背景圆
        bg_color = (*self.color, 200)
        radius = 18
        
        # 发光边框
        if self.hovered:
            glow_color = (*self.color, 150 + int(pulse * 105))
            pygame.draw.circle(screen, glow_color, (self.x, self.y), radius + glow_size)
        
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)
        
        # 图标
        icon_surf = small_font.render(self.icon, True, (255, 255, 255))
        icon_rect = icon_surf.get_rect(center=(self.x, self.y))
        screen.blit(icon_surf, icon_rect)


class AchievementBadgesDisplay:
    """成就徽章展示器"""
    
    def __init__(self, achievement_manager):
        self.manager = achievement_manager
        self.badges: List[AchievementBadge] = []
        self.show_tooltip = False
        self.tooltip_text = ""
        self.tooltip_pos = (0, 0)
        self._init_badges()
    
    def _init_badges(self):
        """初始化徽章列表"""
        # 颜色配置
        colors = {
            "kill": (220, 60, 60),       # 红色 - 击杀
            "gold": (255, 200, 0),       # 金色 - 金币
            "tower": (60, 150, 220),     # 蓝色 - 防御塔
            "wave": (150, 60, 220),      # 紫色 - 波次
            "special": (60, 220, 120),   # 绿色 - 特殊
        }
        
        # 成就ID到类型映射
        type_map = {
            "first_blood": ("kill", "初战告捷"),
            "slayer_10": ("kill", "小试牛刀"),
            "slayer_50": ("kill", "怪物猎人"),
            "slayer_100": ("kill", "传奇猎手"),
            "slayer_500": ("kill", "毁灭者"),
            "rich_1000": ("gold", "小有积蓄"),
            "rich_10000": ("gold", "腰缠万贯"),
            "rich_50000": ("gold", "富甲一方"),
            "first_tower": ("tower", "初建防御"),
            "tower_master": ("tower", "塔大师"),
            "first_wave": ("wave", "首波告捷"),
            "wave_10": ("wave", "十波之主"),
            "wave_25": ("wave", "波次达人"),
            "perfect_defense": ("special", "完美防御"),
            "speed_kill": ("special", "闪电击杀"),
            "no_damage": ("special", "零伤通关"),
        }
        
        # 只显示已解锁的成就
        unlocked = self.manager.get_unlocked_achievements()
        
        for ach in unlocked:
            ach_id = ach.id
            if ach_id in type_map:
                type_info = type_map[ach_id]
                color = colors.get(type_info[0], (150, 150, 150))
                badge = AchievementBadge(ach_id, type_info[1], ach.icon, color)
                self.badges.append(badge)
    
    def update(self, dt: float, mouse_pos: Tuple[int, int]):
        """更新徽章状态"""
        # 更新位置 (顶部居中)
        screen_width = pygame.display.get_surface().get_width()
        total_width = len(self.badges) * 45
        start_x = (screen_width - total_width) // 2
        
        for i, badge in enumerate(self.badges):
            badge.x = start_x + i * 45 + 22
            badge.y = 35
            badge.update(dt)
            
            # 检测悬停
            dx = mouse_pos[0] - badge.x
            dy = mouse_pos[1] - badge.y
            badge.hovered = (dx * dx + dy * dy) < 400  # 20像素半径
        
        # 显示提示
        self.show_tooltip = any(b.hovered for b in self.badges)
        if self.show_tooltip:
            hovered_badge = next(b for b in self.badges if b.hovered)
            self.tooltip_text = hovered_badge.name
            self.tooltip_pos = (hovered_badge.x, hovered_badge.y - 25)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font, small_font: pygame.font.Font):
        """绘制徽章"""
        if not self.badges:
            return
        
        for badge in self.badges:
            badge.draw(screen, small_font)
        
        # 绘制提示
        if self.show_tooltip and self.tooltip_text:
            tooltip = font.render(self.tooltip_text, True, (255, 255, 255))
            tooltip_bg = pygame.Surface((tooltip.get_width() + 16, tooltip.get_height() + 8), pygame.SRCALPHA)
            tooltip_bg.fill((0, 0, 0, 200))
            screen.blit(tooltip_bg, (self.tooltip_pos[0] - tooltip.get_width() // 2 - 8, self.tooltip_pos[1] - 12))
            screen.blit(tooltip, (self.tooltip_pos[0] - tooltip.get_width() // 2, self.tooltip_pos[1] - 8))
    
    def refresh(self):
        """刷新徽章列表(当成就解锁时调用)"""
        self.badges.clear()
        self._init_badges()