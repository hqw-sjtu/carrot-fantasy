# -*- coding: utf-8 -*-
"""防御塔图鉴UI系统 - Tower Bestiary UI

在游戏中展示玩家已解锁的防御塔和统计信息。
"""

import pygame
import os
from src.tower_bestiary import get_bestiary


class TowerBestiaryUI:
    """防御塔图鉴界面"""
    
    def __init__(self, screen):
        self.screen = screen
        self.bestiary = get_bestiary()
        self.font_title = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        
        # 颜色定义
        self.COLOR_BG = (20, 20, 40)
        self.COLOR_PANEL = (30, 30, 60)
        self.COLOR_BORDER = (60, 60, 100)
        self.COLOR_TEXT = (220, 220, 240)
        self.COLOR_ACCENT = (255, 180, 80)
        self.COLOR_LOCKED = (80, 80, 100)
        
        # 所有塔类型定义
        self.ALL_TOWERS = [
            {"name": "箭塔", "icon": "🏹", "desc": "基础单体攻击"},
            {"name": "炮塔", "icon": "💣", "desc": "范围AOE伤害"},
            {"name": "魔法塔", "icon": "🔮", "desc": "减速控制"},
            {"name": "电塔", "icon": "⚡", "desc": "链式闪电"},
            {"name": "冰塔", "icon": "❄️", "desc": "冰冻减速"},
            {"name": "火塔", "icon": "🔥", "desc": "持续燃烧"},
            {"name": "毒塔", "icon": "☠️", "desc": "中毒debuff"},
            {"name": "眩晕塔", "icon": "⭐", "desc": "眩晕控制"},
        ]
        
        # 滚动偏移
        self.scroll_offset = 0
        self.max_visible = 5
        self.item_height = 80
        
    def handle_event(self, event):
        """处理输入事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.key == pygame.K_DOWN:
                max_scroll = max(0, len(self.ALL_TOWERS) - self.max_visible)
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
            elif event.key == pygame.K_ESCAPE:
                return False
        return True
    
    def draw(self):
        """绘制图鉴界面"""
        # 背景
        self.screen.fill(self.COLOR_BG)
        
        # 标题
        title = self.font_title.render("🏰 防御塔图鉴", True, self.COLOR_ACCENT)
        self.screen.blit(title, (40, 30))
        
        # 统计信息
        unlocked = self.bestiary.get_unlocked_count()
        total = len(self.ALL_TOWERS)
        stats_text = self.font_normal.render(
            f"已解锁: {unlocked}/{total}", True, self.COLOR_TEXT
        )
        self.screen.blit(stats_text, (40, 70))
        
        # 绘制塔列表
        panel_rect = pygame.Rect(30, 110, 740, 400)
        pygame.draw.rect(self.screen, self.COLOR_PANEL, panel_rect)
        pygame.draw.rect(self.screen, self.COLOR_BORDER, panel_rect, 2)
        
        visible_towers = self.ALL_TOWERS[self.scroll_offset:self.scroll_offset + self.max_visible]
        
        for i, tower in enumerate(visible_towers):
            y = 120 + i * (self.item_height + 5)
            is_unlocked = self.bestiary.is_unlocked(tower["name"])
            
            # 塔项背景
            item_rect = pygame.Rect(40, y, 720, self.item_height)
            color = self.COLOR_BORDER if is_unlocked else self.COLOR_LOCKED
            pygame.draw.rect(self.screen, color, item_rect)
            
            # 图标
            icon = self.font_title.render(tower["icon"], True, self.COLOR_TEXT if is_unlocked else self.COLOR_LOCKED)
            self.screen.blit(icon, (55, y + 20))
            
            # 名称
            name_color = self.COLOR_TEXT if is_unlocked else self.COLOR_LOCKED
            name = self.font_normal.render(tower["name"], True, name_color)
            self.screen.blit(name, (110, y + 10))
            
            # 描述
            desc = self.font_small.render(tower["desc"], True, (150, 150, 170))
            self.screen.blit(desc, (110, y + 40))
            
            # 状态和解锁统计
            if is_unlocked:
                stats = self.bestiary.get_tower_stats(tower["name"])
                kills = stats.get('kills', 0)
                damage = stats.get('damage', 0)
                stat_text = self.font_small.render(
                    f"击杀: {kills} | 伤害: {damage}", True, (150, 200, 150)
                )
                self.screen.blit(stat_text, (550, y + 30))
                
                status = self.font_normal.render("✓ 已解锁", True, (100, 200, 100))
                self.screen.blit(status, (620, y + 10))
            else:
                status = self.font_normal.render("🔒 未解锁", True, self.COLOR_LOCKED)
                self.screen.blit(status, (620, y + 25))
        
        # 滚动提示
        if len(self.ALL_TOWERS) > self.max_visible:
            scroll_hint = self.font_small.render(
                "↑/↓ 滚动 · ESC 退出", True, (120, 120, 150)
            )
            self.screen.blit(scroll_hint, (350, 530))
        
        return self.screen