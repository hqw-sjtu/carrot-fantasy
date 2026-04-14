# -*- coding: utf-8 -*-
"""
Tower Upgrade Preview System - 防御塔升级预览系统
工艺品级别功能：玩家可直观预览升级路径与效果对比
"""

import pygame
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class UpgradePath:
    """升级路径信息"""
    level: int
    name: str
    damage_bonus: float  # 伤害加成百分比
    range_bonus: float   # 范围加成百分比
    speed_bonus: float   # 攻速加成百分比
    cost: int
    special_effect: str  # 特殊效果描述


class TowerUpgradePreview:
    """防御塔升级预览面板"""
    
    # 各塔升级路径配置
    UPGRADE_PATHS = {
        "arrow": [
            UpgradePath(1, "普通", 0, 0, 0, 0, "基础攻击"),
            UpgradePath(2, "强化", 20, 10, 15, 50, "伤害+20%"),
            UpgradePath(3, "精通", 40, 20, 30, 100, "穿透+1"),
            UpgradePath(4, "大师", 60, 30, 45, 200, "暴击+10%"),
            UpgradePath(5, "传奇", 100, 50, 60, 400, "三重箭"),
        ],
        "cannon": [
            UpgradePath(1, "普通", 0, 0, 0, 0, "基础攻击"),
            UpgradePath(2, "强化", 25, 10, 10, 60, "范围+25%"),
            UpgradePath(3, "精通", 50, 20, 25, 150, "暴击伤害+50%"),
            UpgradePath(4, "大师", 80, 30, 40, 300, "眩晕效果"),
            UpgradePath(5, "传奇", 120, 50, 50, 500, "毁灭打击"),
        ],
        "magic": [
            UpgradePath(1, "普通", 0, 0, 0, 0, "基础攻击"),
            UpgradePath(2, "强化", 15, 15, 20, 70, "魔法回复"),
            UpgradePath(3, "精通", 35, 25, 40, 140, "连锁闪电"),
            UpgradePath(4, "大师", 55, 40, 50, 280, "吸取生命"),
            UpgradePath(5, "传奇", 80, 60, 70, 450, "奥术风暴"),
        ],
        "ice": [
            UpgradePath(1, "普通", 0, 0, 0, 0, "基础攻击"),
            UpgradePath(2, "强化", 10, 15, 10, 60, "减速+15%"),
            UpgradePath(3, "精通", 25, 25, 25, 120, "冰霜新星"),
            UpgradePath(4, "大师", 40, 35, 40, 250, "冰封禁锢"),
            UpgradePath(5, "传奇", 60, 50, 55, 420, "绝对零度"),
        ],
        "lightning": [
            UpgradePath(1, "普通", 0, 0, 0, 0, "基础攻击"),
            UpgradePath(2, "强化", 20, 20, 15, 80, "弹跳+1"),
            UpgradePath(3, "精通", 45, 35, 35, 160, "范围闪电"),
            UpgradePath(4, "大师", 70, 50, 50, 320, "连锁闪电"),
            UpgradePath(5, "传奇", 100, 70, 70, 550, "雷神降世"),
        ],
        "poison": [
            UpgradePath(1, "普通", 0, 0, 0, 0, "基础攻击"),
            UpgradePath(2, "强化", 15, 10, 20, 65, "毒伤+25%"),
            UpgradePath(3, "精通", 35, 20, 40, 130, "扩散毒云"),
            UpgradePath(4, "大师", 55, 35, 50, 260, "剧毒领域"),
            UpgradePath(5, "传奇", 80, 50, 65, 440, "致命毒素"),
        ],
    }
    
    def __init__(self):
        self.visible = False
        self.tower_type: Optional[str] = None
        self.current_level: int = 1
        self.tower_x: int = 0
        self.tower_y: int = 0
        self.font: Optional[pygame.font.Font] = None
        self.title_font: Optional[pygame.font.Font] = None
        
        # 面板配置
        self.panel_width = 280
        self.panel_height = 350
        self.panel_x = 0
        self.panel_y = 0
        self.padding = 15
        self.spacing = 8
        
    def initialize(self):
        """初始化字体"""
        try:
            # 尝试使用支持中文的字体
            font_paths = [
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc", 
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
            for font_path in font_paths:
                try:
                    self.font = pygame.font.Font(font_path, 14)
                    self.title_font = pygame.font.Font(font_path, 18)
                    break
                except:
                    continue
            if not self.font:
                self.font = pygame.font.Font(None, 18)
                self.title_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.Font(None, 18)
            self.title_font = pygame.font.Font(None, 24)
            
    def show(self, tower_type: str, x: int, y: int, current_level: int = 1):
        """显示升级预览面板"""
        if tower_type not in self.UPGRADE_PATHS:
            return
            
        self.tower_type = tower_type
        self.current_level = current_level
        self.tower_x = x
        self.tower_y = y
        self.visible = True
        
        # 计算面板位置（避免超出屏幕）
        self.panel_x = min(x + 40, 800 - self.panel_width - 10)
        self.panel_y = max(y - self.panel_height // 2, 10)
        
    def hide(self):
        """隐藏面板"""
        self.visible = False
        
    def toggle(self, tower_type: str, x: int, y: int, current_level: int = 1):
        """切换显示状态"""
        if self.visible and self.tower_type == tower_type:
            self.hide()
        else:
            self.show(tower_type, x, y, current_level)
            
    def draw(self, screen: pygame.Surface) -> bool:
        """绘制预览面板"""
        if not self.visible or not self.tower_type:
            return False
            
        if not self.font or not self.title_font:
            self.initialize()
            
        # 绘制半透明背景
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                 self.panel_width, self.panel_height)
        
        # 使用渐变背景效果
        bg_surface = pygame.Surface((self.panel_width, self.panel_height))
        bg_surface.set_alpha(230)
        bg_surface.fill((20, 25, 40))
        screen.blit(bg_surface, (self.panel_x, self.panel_y))
        
        # 绘制边框
        border_color = (100, 120, 180)
        pygame.draw.rect(screen, border_color, panel_rect, 2, border_radius=8)
        
        # 绘制标题
        tower_names = {
            "arrow": "⚔️ 箭塔",
            "cannon": "💣 炮塔", 
            "magic": "✨ 魔法塔",
            "ice": "❄️ 冰霜塔",
            "lightning": "⚡ 闪电塔",
            "poison": "☠️ 毒气塔",
        }
        title = tower_names.get(self.tower_type, self.tower_type)
        title_surface = self.title_font.render(f"升级路线 - {title}", True, (255, 220, 100))
        screen.blit(title_surface, (self.panel_x + self.padding, 
                                      self.panel_y + self.padding))
        
        # 获取升级路径
        paths = self.UPGRADE_PATHS.get(self.tower_type, [])
        
        # 绘制升级路径
        y_offset = self.panel_y + self.padding + 35
        total_cost = 0
        
        for i, path in enumerate(paths):
            # 计算累计成本
            if path.level > self.current_level:
                total_cost += path.cost
                
            # 绘制等级节点
            node_x = self.panel_x + self.padding + 15
            node_y = y_offset + 10
            
            # 节点颜色：当前等级=金色，已解锁=绿色，未解锁=灰色
            if path.level == self.current_level:
                node_color = (255, 200, 0)  # 金色-当前
                level_color = (255, 220, 100)
            elif path.level < self.current_level:
                node_color = (100, 200, 100)  # 绿色-已升级
                level_color = (150, 255, 150)
            else:
                node_color = (80, 80, 80)   # 灰色-未解锁
                level_color = (120, 120, 120)
            
            # 绘制连接线
            if i > 0:
                line_color = node_color if path.level <= self.current_level else (50, 50, 50)
                pygame.draw.line(screen, line_color, 
                               (node_x, node_y - 15), (node_x, node_y), 2)
            
            # 绘制节点圆圈
            pygame.draw.circle(screen, node_color, (node_x, node_y), 12)
            pygame.draw.circle(screen, (30, 35, 50), (node_x, node_y), 12, 2)
            
            # 绘制等级数字
            level_text = self.font.render(str(path.level), True, (0, 0, 0))
            screen.blit(level_text, (node_x - 4, node_y - 7))
            
            # 绘制升级信息
            info_x = node_x + 25
            
            # 等级名称和效果
            name_text = self.font.render(path.name, True, level_color)
            screen.blit(name_text, (info_x, y_offset))
            
            # 详细属性变化
            stats = []
            if path.damage_bonus > 0:
                stats.append(f"伤害+{path.damage_bonus}%")
            if path.range_bonus > 0:
                stats.append(f"范围+{path.range_bonus}%")
            if path.speed_bonus > 0:
                stats.append(f"攻速+{path.speed_bonus}%")
                
            if stats:
                stats_text = ", ".join(stats)
                stats_surface = self.font.render(stats_text, True, (180, 180, 180))
                screen.blit(stats_surface, (info_x, y_offset + 18))
            
            # 特殊效果
            if path.special_effect:
                effect_surface = self.font.render(path.special_effect, True, (255, 150, 150))
                screen.blit(effect_surface, (info_x, y_offset + 36))
            
            # 升级成本
            if path.level > self.current_level:
                cost_color = (255, 200, 100) if total_cost <= 500 else (255, 100, 100)
                cost_text = self.font.render(f"💰 {path.cost}", True, cost_color)
                screen.blit(cost_text, (info_x + 150, y_offset))
            
            y_offset += 65
            
        # 绘制总计成本提示
        if total_cost > 0:
            total_y = self.panel_y + self.panel_height - 30
            total_text = self.font.render(f"升级至满级还需: {total_cost} 💰", True, (255, 220, 100))
            screen.blit(total_text, (self.panel_x + self.padding, total_y))
            
        return True
        
    def is_point_inside(self, x: int, y: int) -> bool:
        """检查点是否在面板内"""
        return (self.panel_x <= x <= self.panel_x + self.panel_width and
                self.panel_y <= y <= self.panel_y + self.panel_height)
    
    def get_upgrade_cost(self, target_level: int) -> int:
        """获取升级到指定等级的总成本"""
        if not self.tower_type or target_level <= self.current_level:
            return 0
            
        paths = self.UPGRADE_PATHS.get(self.tower_type, [])
        total = 0
        for path in paths:
            if path.level > self.current_level and path.level <= target_level:
                total += path.cost
        return total


# 全局实例
_upgrade_preview_instance: Optional[TowerUpgradePreview] = None


def get_upgrade_preview() -> TowerUpgradePreview:
    """获取全局升级预览实例"""
    global _upgrade_preview_instance
    if _upgrade_preview_instance is None:
        _upgrade_preview_instance = TowerUpgradePreview()
    return _upgrade_preview_instance